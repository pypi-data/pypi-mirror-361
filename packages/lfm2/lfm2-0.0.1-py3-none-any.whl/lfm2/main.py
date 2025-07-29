"""
LFM2 (Liquid Foundation Model 2) PyTorch Implementation

This implementation is based on the LFM2 architecture described in the Liquid AI paper.
LFM2 is a hybrid model combining short-range convolutions with grouped query attention,
designed for efficient on-device inference.

Architecture:
- 16 blocks total: 10 LIV convolution blocks + 6 GQA blocks
- Double-gated short-range convolutions
- Grouped Query Attention (GQA)
- SwiGLU activation functions
- RMSNorm normalization
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, Any, Union
from dataclasses import dataclass
from pathlib import Path

try:
    from loguru import logger

    LOGURU_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    LOGURU_AVAILABLE = False


@dataclass
class LFM2Config:
    """Configuration class for LFM2 model.

    Attributes:
        vocab_size: Size of the vocabulary
        hidden_size: Hidden dimension size
        intermediate_size: Feedforward intermediate dimension
        num_conv_blocks: Number of LIV convolution blocks (default: 10)
        num_attention_blocks: Number of GQA blocks (default: 6)
        num_attention_heads: Number of attention heads
        num_key_value_heads: Number of key-value heads for GQA
        conv_kernel_size: Kernel size for short convolutions
        max_position_embeddings: Maximum sequence length
        rms_norm_eps: RMS normalization epsilon
        tie_word_embeddings: Whether to tie input/output embeddings
        rope_theta: RoPE base frequency
        attention_dropout: Dropout rate for attention
        hidden_dropout: Dropout rate for hidden layers
        initializer_range: Standard deviation for weight initialization
        use_cache: Whether to use key-value caching
        pad_token_id: Padding token ID
        bos_token_id: Beginning of sequence token ID
        eos_token_id: End of sequence token ID
        use_return_dict: Whether to return outputs as a dictionary
        output_attentions: Whether to output attention weights by default
        output_hidden_states: Whether to output hidden states by default
    """

    vocab_size: int = 32768
    hidden_size: int = 1024
    intermediate_size: int = 2816
    num_conv_blocks: int = 10
    num_attention_blocks: int = 6
    num_attention_heads: int = 16
    num_key_value_heads: int = 4
    conv_kernel_size: int = 3
    max_position_embeddings: int = 32768
    rms_norm_eps: float = 1e-6
    tie_word_embeddings: bool = True
    rope_theta: float = 10000.0
    attention_dropout: float = 0.0
    hidden_dropout: float = 0.0
    initializer_range: float = 0.02
    use_cache: bool = True
    pad_token_id: int = 0
    bos_token_id: int = 1
    eos_token_id: int = 2
    use_return_dict: bool = True
    output_attentions: bool = False
    output_hidden_states: bool = False

    @classmethod
    def from_pretrained_size(cls, size: str) -> "LFM2Config":
        """Create configuration for standard LFM2 model sizes.

        Args:
            size: Model size ('350M', '700M', or '1.2B')

        Returns:
            LFM2Config instance for the specified size
        """
        configs = {
            "350M": cls(
                hidden_size=768,
                intermediate_size=2048,
                num_attention_heads=12,
                num_key_value_heads=3,
            ),
            "700M": cls(
                hidden_size=1024,
                intermediate_size=2816,
                num_attention_heads=16,
                num_key_value_heads=4,
            ),
            "1.2B": cls(
                hidden_size=1536,
                intermediate_size=4096,
                num_attention_heads=24,
                num_key_value_heads=6,
            ),
        }

        if size not in configs:
            raise ValueError(
                f"Unknown model size: {size}. Available: {list(configs.keys())}"
            )

        return configs[size]


class RMSNorm(nn.Module):
    """Root Mean Square Layer Normalization.

    Args:
        hidden_size: The hidden dimension size
        eps: Small epsilon for numerical stability
    """

    def __init__(self, hidden_size: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(hidden_size))
        self.variance_epsilon = eps

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        input_dtype = hidden_states.dtype
        hidden_states = hidden_states.to(torch.float32)
        variance = hidden_states.pow(2).mean(-1, keepdim=True)
        hidden_states = hidden_states * torch.rsqrt(
            variance + self.variance_epsilon
        )
        return self.weight * hidden_states.to(input_dtype)


class RotaryPositionalEmbedding(nn.Module):
    """Rotary Positional Embedding (RoPE).

    Args:
        dim: Dimension of the embedding
        max_position_embeddings: Maximum sequence length
        base: Base frequency for RoPE
    """

    def __init__(
        self,
        dim: int,
        max_position_embeddings: int = 32768,
        base: float = 10000.0,
    ):
        super().__init__()
        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base

        # Precompute frequency inverse
        inv_freq = 1.0 / (
            self.base
            ** (torch.arange(0, self.dim, 2).float() / self.dim)
        )
        self.register_buffer("inv_freq", inv_freq, persistent=False)

    def forward(
        self, x: torch.Tensor, seq_len: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        # Generate position indices
        t = torch.arange(seq_len, device=x.device).type_as(
            self.inv_freq
        )
        freqs = torch.outer(t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)

        cos = emb.cos()
        sin = emb.sin()

        return cos, sin


def rotate_half(x: torch.Tensor) -> torch.Tensor:
    """Rotates half the hidden dims of the input."""
    x1 = x[..., : x.shape[-1] // 2]
    x2 = x[..., x.shape[-1] // 2 :]
    return torch.cat((-x2, x1), dim=-1)


def apply_rotary_pos_emb(
    q: torch.Tensor,
    k: torch.Tensor,
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Apply rotary positional embedding to query and key tensors."""
    q_embed = (q * cos) + (rotate_half(q) * sin)
    k_embed = (k * cos) + (rotate_half(k) * sin)
    return q_embed, k_embed


class LFM2ConvBlock(nn.Module):
    """LFM2 double-gated short-range convolution block.

    This implements the LIV (Linear Input-Varying) convolution as described:
    ```
    def lfm2_conv(x):
        B, C, x = linear(x)    # input projection
        x = B*x                # gating (gate depends on input)
        x = conv(x)            # short conv
        x = C*x                # gating
        x = linear(x)
        return x
    ```

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size

        # Input projection to gates and values
        self.input_projection = nn.Linear(
            self.hidden_size,
            3 * self.hidden_size,  # B, C, x
            bias=False,
        )

        # Short convolution
        self.conv = nn.Conv1d(
            self.hidden_size,
            self.hidden_size,
            kernel_size=config.conv_kernel_size,
            padding=config.conv_kernel_size // 2,
            groups=self.hidden_size,  # Depthwise convolution for efficiency
            bias=False,
        )

        # Output projection
        self.output_projection = nn.Linear(
            self.hidden_size, self.hidden_size, bias=False
        )

        # Dropout
        self.dropout = nn.Dropout(config.hidden_dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the LFM2 convolution block.

        Args:
            x: Input tensor of shape (batch_size, seq_len, hidden_size)

        Returns:
            Output tensor of shape (batch_size, seq_len, hidden_size)
        """
        batch_size, seq_len, hidden_size = x.shape

        # Input projection: B, C, x = linear(x)
        projected = self.input_projection(x)  # (B, L, 3*H)
        B, C, x_proj = projected.chunk(3, dim=-1)  # Each: (B, L, H)

        # First gating: x = B*x
        x_gated = B * x_proj

        # Apply short convolution
        # Convert to (B, H, L) for conv1d
        x_conv_input = x_gated.transpose(1, 2)  # (B, H, L)
        x_conv = self.conv(x_conv_input)  # (B, H, L)
        x_conv = x_conv.transpose(1, 2)  # (B, L, H)

        # Second gating: x = C*x
        x_gated_2 = C * x_conv

        # Apply dropout
        x_gated_2 = self.dropout(x_gated_2)

        # Output projection
        output = self.output_projection(x_gated_2)

        return output


class GroupedQueryAttention(nn.Module):
    """Grouped Query Attention implementation.

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size
        self.num_heads = config.num_attention_heads
        self.num_key_value_heads = config.num_key_value_heads
        self.head_dim = self.hidden_size // self.num_heads
        self.num_key_value_groups = (
            self.num_heads // self.num_key_value_heads
        )

        if self.hidden_size % self.num_heads != 0:
            raise ValueError(
                f"hidden_size ({self.hidden_size}) must be divisible by num_heads ({self.num_heads})"
            )

        # Linear projections
        self.q_proj = nn.Linear(
            self.hidden_size,
            self.num_heads * self.head_dim,
            bias=False,
        )
        self.k_proj = nn.Linear(
            self.hidden_size,
            self.num_key_value_heads * self.head_dim,
            bias=False,
        )
        self.v_proj = nn.Linear(
            self.hidden_size,
            self.num_key_value_heads * self.head_dim,
            bias=False,
        )
        self.o_proj = nn.Linear(
            self.num_heads * self.head_dim,
            self.hidden_size,
            bias=False,
        )

        # Rotary positional embedding
        self.rotary_emb = RotaryPositionalEmbedding(
            self.head_dim,
            config.max_position_embeddings,
            config.rope_theta,
        )

        # Attention dropout
        self.attention_dropout = nn.Dropout(config.attention_dropout)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor]] = None,
        output_attentions: bool = False,
        use_cache: bool = False,
    ) -> Tuple[
        torch.Tensor,
        Optional[torch.Tensor],
        Optional[Tuple[torch.Tensor]],
    ]:
        """Forward pass of grouped query attention.

        Args:
            hidden_states: Input tensor of shape (batch_size, seq_len, hidden_size)
            attention_mask: Optional attention mask
            position_ids: Optional position indices
            past_key_value: Optional cached key-value pairs
            output_attentions: Whether to output attention weights
            use_cache: Whether to use key-value caching

        Returns:
            Tuple of (output, attention_weights, past_key_value)
        """
        bsz, q_len, _ = hidden_states.size()

        # Project to Q, K, V
        query_states = self.q_proj(hidden_states)
        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)

        # Reshape for attention computation
        query_states = query_states.view(
            bsz, q_len, self.num_heads, self.head_dim
        ).transpose(1, 2)
        key_states = key_states.view(
            bsz, q_len, self.num_key_value_heads, self.head_dim
        ).transpose(1, 2)
        value_states = value_states.view(
            bsz, q_len, self.num_key_value_heads, self.head_dim
        ).transpose(1, 2)

        # Get sequence length for RoPE
        kv_seq_len = key_states.shape[-2]
        if past_key_value is not None:
            kv_seq_len += past_key_value[0].shape[-2]

        # Apply rotary positional embedding
        cos, sin = self.rotary_emb(value_states, kv_seq_len)
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, cos, sin
        )

        # Handle past key-value cache
        if past_key_value is not None:
            key_states = torch.cat(
                [past_key_value[0], key_states], dim=2
            )
            value_states = torch.cat(
                [past_key_value[1], value_states], dim=2
            )

        past_key_value = (
            (key_states, value_states) if use_cache else None
        )

        # Repeat key and value states for grouped query attention
        key_states = key_states.repeat_interleave(
            self.num_key_value_groups, dim=1
        )
        value_states = value_states.repeat_interleave(
            self.num_key_value_groups, dim=1
        )

        # Compute attention scores
        attn_weights = torch.matmul(
            query_states, key_states.transpose(2, 3)
        ) / math.sqrt(self.head_dim)

        # Apply attention mask
        if attention_mask is not None:
            attn_weights = attn_weights + attention_mask

        # Apply softmax
        attn_weights = F.softmax(
            attn_weights, dim=-1, dtype=torch.float32
        ).to(query_states.dtype)
        attn_weights = self.attention_dropout(attn_weights)

        # Apply attention to values
        attn_output = torch.matmul(attn_weights, value_states)

        # Reshape and project output
        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(
            bsz, q_len, self.hidden_size
        )
        attn_output = self.o_proj(attn_output)

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, past_key_value


class SwiGLU(nn.Module):
    """SwiGLU activation function.

    SwiGLU(x) = Swish(xW + b) ⊙ (xV + c)
    where Swish(x) = x * sigmoid(x)

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.hidden_size = config.hidden_size
        self.intermediate_size = config.intermediate_size

        self.gate_proj = nn.Linear(
            self.hidden_size, self.intermediate_size, bias=False
        )
        self.up_proj = nn.Linear(
            self.hidden_size, self.intermediate_size, bias=False
        )
        self.down_proj = nn.Linear(
            self.intermediate_size, self.hidden_size, bias=False
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of SwiGLU.

        Args:
            x: Input tensor

        Returns:
            Output tensor after SwiGLU activation
        """
        gate = self.gate_proj(x)
        up = self.up_proj(x)
        swish_gate = F.silu(gate)  # SiLU is equivalent to Swish
        return self.down_proj(swish_gate * up)


class LFM2Block(nn.Module):
    """LFM2 attention block containing GQA + SwiGLU.

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.config = config
        self.hidden_size = config.hidden_size

        # Self-attention
        self.self_attn = GroupedQueryAttention(config)

        # Feed-forward network
        self.mlp = SwiGLU(config)

        # Layer normalization
        self.input_layernorm = RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )
        self.post_attention_layernorm = RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.Tensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor]] = None,
        output_attentions: Optional[bool] = False,
        use_cache: Optional[bool] = False,
    ) -> Tuple[
        torch.Tensor,
        Optional[torch.Tensor],
        Optional[Tuple[torch.Tensor]],
    ]:
        """Forward pass of LFM2 attention block.

        Args:
            hidden_states: Input tensor
            attention_mask: Optional attention mask
            position_ids: Optional position indices
            past_key_value: Optional cached key-value pairs
            output_attentions: Whether to output attention weights
            use_cache: Whether to use key-value caching

        Returns:
            Tuple of (output, attention_weights, past_key_value)
        """
        residual = hidden_states

        # Self-attention
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states, self_attn_weights, present_key_value = (
            self.self_attn(
                hidden_states=hidden_states,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_value=past_key_value,
                output_attentions=output_attentions,
                use_cache=use_cache,
            )
        )
        hidden_states = residual + hidden_states

        # Feed-forward network
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (self_attn_weights,)

        if use_cache:
            outputs += (present_key_value,)

        return outputs


class LFM2Model(nn.Module):
    """LFM2 (Liquid Foundation Model 2) implementation.

    This model implements the hybrid architecture described in the Liquid AI paper:
    - 10 double-gated short-range LIV convolution blocks
    - 6 grouped query attention blocks
    - RMSNorm normalization
    - Rotary positional embeddings

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.config = config
        self.vocab_size = config.vocab_size
        self.hidden_size = config.hidden_size

        # Token embeddings
        self.embed_tokens = nn.Embedding(
            config.vocab_size, config.hidden_size
        )

        # Model blocks
        self.layers = nn.ModuleList()

        # Add convolution blocks
        for i in range(config.num_conv_blocks):
            self.layers.append(LFM2ConvBlock(config))
            if LOGURU_AVAILABLE:
                logger.debug(
                    f"Added LFM2ConvBlock {i+1}/{config.num_conv_blocks}"
                )

        # Add attention blocks
        for i in range(config.num_attention_blocks):
            self.layers.append(LFM2Block(config))
            if LOGURU_AVAILABLE:
                logger.debug(
                    f"Added LFM2Block {i+1}/{config.num_attention_blocks}"
                )

        # Final layer norm
        self.norm = RMSNorm(
            config.hidden_size, eps=config.rms_norm_eps
        )

        # Initialize weights
        self.apply(self._init_weights)

        if LOGURU_AVAILABLE:
            total_params = sum(p.numel() for p in self.parameters())
            logger.info(
                f"LFM2Model initialized with {total_params:,} parameters"
            )

    def _init_weights(self, module: nn.Module) -> None:
        """Initialize model weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(
                module.weight,
                mean=0.0,
                std=self.config.initializer_range,
            )
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(
                module.weight,
                mean=0.0,
                std=self.config.initializer_range,
            )
        elif isinstance(module, nn.Conv1d):
            torch.nn.init.normal_(
                module.weight,
                mean=0.0,
                std=self.config.initializer_range,
            )
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)

    def get_input_embeddings(self) -> nn.Embedding:
        """Get input embeddings."""
        return self.embed_tokens

    def set_input_embeddings(self, value: nn.Embedding) -> None:
        """Set input embeddings."""
        self.embed_tokens = value

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, Dict[str, torch.Tensor]]:
        """Forward pass of LFM2 model.

        Args:
            input_ids: Input token IDs
            attention_mask: Optional attention mask
            position_ids: Optional position indices
            past_key_values: Optional cached key-value pairs
            inputs_embeds: Optional input embeddings
            use_cache: Whether to use key-value caching
            output_attentions: Whether to output attention weights
            output_hidden_states: Whether to output hidden states
            return_dict: Whether to return a dictionary

        Returns:
            Model outputs
        """
        output_attentions = (
            output_attentions
            if output_attentions is not None
            else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        use_cache = (
            use_cache
            if use_cache is not None
            else self.config.use_cache
        )
        return_dict = (
            return_dict
            if return_dict is not None
            else self.config.use_return_dict
        )

        # Get input embeddings
        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)

        batch_size, seq_length = inputs_embeds.shape[:2]

        # Initialize position IDs if not provided
        if position_ids is None:
            device = (
                input_ids.device
                if input_ids is not None
                else inputs_embeds.device
            )
            position_ids = torch.arange(
                seq_length, dtype=torch.long, device=device
            )
            position_ids = position_ids.unsqueeze(0).expand(
                batch_size, -1
            )

        # Initialize past key values if not provided
        if past_key_values is None:
            past_key_values = [None] * len(self.layers)

        # Prepare attention mask
        if attention_mask is not None:
            attention_mask = self._prepare_attention_mask(
                attention_mask, seq_length, batch_size
            )

        hidden_states = inputs_embeds

        # Initialize outputs
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        next_decoder_cache = () if use_cache else None

        # Process through layers
        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states += (hidden_states,)

            past_key_value = (
                past_key_values[idx]
                if past_key_values is not None
                else None
            )

            # Handle convolution blocks vs attention blocks
            if isinstance(decoder_layer, LFM2ConvBlock):
                # Convolution block - simpler forward pass
                hidden_states = decoder_layer(hidden_states)
                layer_outputs = (hidden_states,)
            else:
                # Attention block - full forward pass
                layer_outputs = decoder_layer(
                    hidden_states,
                    attention_mask=attention_mask,
                    position_ids=position_ids,
                    past_key_value=past_key_value,
                    output_attentions=output_attentions,
                    use_cache=use_cache,
                )
                hidden_states = layer_outputs[0]

            if use_cache and isinstance(decoder_layer, LFM2Block):
                next_decoder_cache += (
                    layer_outputs[2 if output_attentions else 1],
                )

            if output_attentions and isinstance(
                decoder_layer, LFM2Block
            ):
                all_self_attns += (layer_outputs[1],)

        # Apply final layer norm
        hidden_states = self.norm(hidden_states)

        # Add hidden states from the last decoder layer
        if output_hidden_states:
            all_hidden_states += (hidden_states,)

        next_cache = next_decoder_cache if use_cache else None

        if not return_dict:
            return tuple(
                v
                for v in [
                    hidden_states,
                    next_cache,
                    all_hidden_states,
                    all_self_attns,
                ]
                if v is not None
            )

        return {
            "last_hidden_state": hidden_states,
            "past_key_values": next_cache,
            "hidden_states": all_hidden_states,
            "attentions": all_self_attns,
        }

    def _prepare_attention_mask(
        self,
        attention_mask: torch.Tensor,
        seq_length: int,
        batch_size: int,
    ) -> torch.Tensor:
        """Prepare attention mask for the model."""
        # Create causal mask
        causal_mask = torch.triu(
            torch.ones((seq_length, seq_length), dtype=torch.bool),
            diagonal=1,
        ).to(attention_mask.device)

        # Convert attention_mask to float and expand
        expanded_mask = attention_mask[:, None, None, :].expand(
            batch_size, 1, seq_length, seq_length
        ).to(torch.float32)

        # Convert to float mask where 1.0 indicates valid attention and 0.0 indicates masked
        expanded_mask = 1.0 - expanded_mask
        causal_float_mask = causal_mask.to(torch.float32)

        # Combine masks (using addition since we've flipped the values)
        combined_mask = expanded_mask + causal_float_mask[None, None, :, :]

        # Convert to attention mask where 0 indicates valid attention and -inf indicates masked
        return combined_mask.masked_fill(combined_mask > 0, float("-inf"))


class LFM2ForCausalLM(nn.Module):
    """LFM2 model for causal language modeling.

    Args:
        config: LFM2 configuration
    """

    def __init__(self, config: LFM2Config):
        super().__init__()
        self.config = config
        self.model = LFM2Model(config)
        self.vocab_size = config.vocab_size

        # Language modeling head
        self.lm_head = nn.Linear(
            config.hidden_size, config.vocab_size, bias=False
        )

        # Tie weights if specified
        if config.tie_word_embeddings:
            self.lm_head.weight = self.model.embed_tokens.weight

        # Initialize weights
        self.apply(self._init_weights)

        if LOGURU_AVAILABLE:
            total_params = sum(p.numel() for p in self.parameters())
            logger.info(
                f"LFM2ForCausalLM initialized with {total_params:,} parameters"
            )

    def _init_weights(self, module: nn.Module) -> None:
        """Initialize model weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(
                module.weight,
                mean=0.0,
                std=self.config.initializer_range,
            )
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)

    def get_input_embeddings(self) -> nn.Embedding:
        """Get input embeddings."""
        return self.model.embed_tokens

    def set_input_embeddings(self, value: nn.Embedding) -> None:
        """Set input embeddings."""
        self.model.embed_tokens = value

    def get_output_embeddings(self) -> nn.Linear:
        """Get output embeddings."""
        return self.lm_head

    def set_output_embeddings(
        self, new_embeddings: nn.Linear
    ) -> None:
        """Set output embeddings."""
        self.lm_head = new_embeddings

    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, Dict[str, torch.Tensor]]:
        """Forward pass of LFM2 causal language model.

        Args:
            input_ids: Input token IDs of shape (batch_size, seq_len)
            attention_mask: Optional attention mask of shape (batch_size, seq_len)
            position_ids: Optional position indices of shape (batch_size, seq_len)
            past_key_values: Optional cached key-value pairs
            inputs_embeds: Optional input embeddings of shape (batch_size, seq_len, hidden_size)
            labels: Optional labels for loss computation of shape (batch_size, seq_len)
            use_cache: Whether to use key-value caching
            output_attentions: Whether to output attention weights
            output_hidden_states: Whether to output hidden states
            return_dict: Whether to return a dictionary

        Returns:
            Model outputs including logits and optional loss
        """
        return_dict = (
            return_dict
            if return_dict is not None
            else self.config.use_return_dict
        )

        # Forward pass through the model
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        if return_dict:
            hidden_states = outputs["last_hidden_state"]
        else:
            hidden_states = outputs[0]

        # Compute logits
        logits = self.lm_head(hidden_states)

        # Compute loss if labels are provided
        loss = None
        if labels is not None:
            # Shift labels for causal LM
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()

            # Flatten the tokens
            loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
            shift_logits = shift_logits.view(-1, self.vocab_size)
            shift_labels = shift_labels.view(-1)

            # Enable model parallelism
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)

        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output

        result = {
            "loss": loss,
            "logits": logits,
            "past_key_values": outputs.get("past_key_values"),
            "hidden_states": outputs.get("hidden_states"),
            "attentions": outputs.get("attentions"),
        }

        return result

    def prepare_inputs_for_generation(
        self,
        input_ids: torch.LongTensor,
        past_key_values: Optional[Tuple] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare inputs for generation."""
        if past_key_values:
            input_ids = input_ids[:, -1:]

        # Prepare attention mask
        attention_mask = kwargs.get("attention_mask", None)
        if attention_mask is not None and past_key_values:
            attention_mask = attention_mask[:, -1:]

        return {
            "input_ids": input_ids,
            "past_key_values": past_key_values,
            "use_cache": kwargs.get("use_cache"),
            "attention_mask": attention_mask,
        }

    @staticmethod
    def _reorder_cache(
        past_key_values: Tuple, beam_idx: torch.Tensor
    ) -> Tuple:
        """Reorder cache for beam search."""
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (
                tuple(
                    past_state.index_select(0, beam_idx)
                    for past_state in layer_past
                ),
            )
        return reordered_past


def create_lfm2_model(
    model_size: str = "700M",
    vocab_size: int = 32768,
    max_seq_length: int = 32768,
    verbose: bool = False,
    **kwargs,
) -> LFM2ForCausalLM:
    """Create an LFM2 model with the specified configuration.

    Args:
        model_size: Model size ('350M', '700M', or '1.2B')
        vocab_size: Vocabulary size
        max_seq_length: Maximum sequence length
        verbose: Whether to enable verbose logging
        **kwargs: Additional configuration parameters

    Returns:
        LFM2ForCausalLM model instance
    """
    if verbose and LOGURU_AVAILABLE:
        logger.info(f"Creating LFM2 model with size: {model_size}")
        logger.info(f"Vocabulary size: {vocab_size}")
        logger.info(f"Maximum sequence length: {max_seq_length}")

    # Create configuration
    config = LFM2Config.from_pretrained_size(model_size)
    config.vocab_size = vocab_size
    config.max_position_embeddings = max_seq_length

    # Update config with any additional parameters
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
            if verbose and LOGURU_AVAILABLE:
                logger.info(f"Set config.{key} = {value}")

    # Create model
    model = LFM2ForCausalLM(config)

    if verbose and LOGURU_AVAILABLE:
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(
            p.numel() for p in model.parameters() if p.requires_grad
        )
        logger.info("Model created successfully!")
        logger.info(f"Total parameters: {total_params:,}")
        logger.info(f"Trainable parameters: {trainable_params:,}")
        logger.info(
            f"Model size: {total_params * 4 / 1024**2:.2f} MB (float32)"
        )

    return model


# Example usage and testing functions
def test_lfm2_model(
    model_size: str = "350M", batch_size: int = 2, seq_len: int = 128
) -> None:
    """Test the LFM2 model with dummy inputs.

    Args:
        model_size: Model size to test
        batch_size: Batch size for testing
        seq_len: Sequence length for testing
    """
    if LOGURU_AVAILABLE:
        logger.info(f"Testing LFM2 model with size: {model_size}")

    # Create model
    model = create_lfm2_model(model_size, verbose=True)
    model.eval()

    # Create dummy inputs
    input_ids = torch.randint(
        0, model.config.vocab_size, (batch_size, seq_len)
    )
    attention_mask = torch.ones(batch_size, seq_len)

    if LOGURU_AVAILABLE:
        logger.info(f"Input shape: {input_ids.shape}")
        logger.info(f"Attention mask shape: {attention_mask.shape}")

    # Forward pass
    with torch.no_grad():
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=True,
        )

    if LOGURU_AVAILABLE:
        logger.info(f"Output logits shape: {outputs['logits'].shape}")
        logger.success("Model test completed successfully!")

    print("Model test completed successfully!")
    print(f"Input shape: {input_ids.shape}")
    print(f"Output logits shape: {outputs['logits'].shape}")


def save_model_config(
    model: LFM2ForCausalLM, save_path: Union[str, Path]
) -> None:
    """Save model configuration to a file.

    Args:
        model: LFM2 model instance
        save_path: Path to save the configuration
    """
    import json

    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)

    config_dict = {
        "model_type": "lfm2",
        "vocab_size": model.config.vocab_size,
        "hidden_size": model.config.hidden_size,
        "intermediate_size": model.config.intermediate_size,
        "num_conv_blocks": model.config.num_conv_blocks,
        "num_attention_blocks": model.config.num_attention_blocks,
        "num_attention_heads": model.config.num_attention_heads,
        "num_key_value_heads": model.config.num_key_value_heads,
        "conv_kernel_size": model.config.conv_kernel_size,
        "max_position_embeddings": model.config.max_position_embeddings,
        "rms_norm_eps": model.config.rms_norm_eps,
        "tie_word_embeddings": model.config.tie_word_embeddings,
        "rope_theta": model.config.rope_theta,
        "attention_dropout": model.config.attention_dropout,
        "hidden_dropout": model.config.hidden_dropout,
        "initializer_range": model.config.initializer_range,
        "use_cache": model.config.use_cache,
        "pad_token_id": model.config.pad_token_id,
        "bos_token_id": model.config.bos_token_id,
        "eos_token_id": model.config.eos_token_id,
    }

    with open(save_path / "config.json", "w") as f:
        json.dump(config_dict, f, indent=2)

    if LOGURU_AVAILABLE:
        logger.info(
            f"Model configuration saved to {save_path / 'config.json'}"
        )


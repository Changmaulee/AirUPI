"""
Subtractive OTM Mesh (Micro & Macro) - Weightless Neural Construct
===================================================================
Core Principles:
1. Weightless Routing: Connections are unweighted with fixed polarities (+1 / -1).
   Operations are sign additions and subtractions (0 FP32 multiplications).
2. Micro-OTM (P-Frames): Nodes only compute and transmit when signal delta |Δx| > threshold.
3. Subtractive Synthesis: Starts from a fully connected harmonic mesh and carves away
   (prunes) edges that cause destructive interference or anti-causal deltas.
4. Macro-OTM (I-Frames): Keyframe consolidation points that normalize energy and stabilize
   the signal across deep layers.
"""

import numpy as np
from typing import List, Tuple, Dict

class MicroOTMLayer:
    """
    Micro-OTM Layer:
    - Tracks node state histories (s_t, s_{t-1})
    - Evaluates signal deltas Δs = s_t - s_{t-1}
    - Applies subtractive ternary routing mesh M ∈ {0, 1} with fixed polarity P ∈ {-1, +1}
    """
    def __init__(self, in_dim: int, out_dim: int, delta_threshold: float = 0.01, seed: int = 42):
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.delta_threshold = delta_threshold
        
        rng = np.random.default_rng(seed)
        # Fixed polarity matrix: base harmonic structure (-1 or +1)
        self.polarity = rng.choice([-1.0, 1.0], size=(out_dim, in_dim))
        
        # Subtractive mask: starts 100% dense (1 = connected, 0 = carved away / subtracted)
        self.mask = np.ones((out_dim, in_dim), dtype=np.float32)
        
        # State tracking for delta computation
        self.prev_input_state = np.zeros(in_dim, dtype=np.float32)
        self.causal_credit = np.zeros((out_dim, in_dim), dtype=np.float32)
        
        # Statistics
        self.total_evaluations = 0
        self.active_delta_computes = 0

    def forward_delta(self, x: np.ndarray, is_streaming: bool = False) -> Tuple[np.ndarray, Dict[str, float]]:
        """
        Forward pass via delta-driven subtractive synthesis.
        y_j = sum_{i in Active} (mask_{ji} * polarity_{ji} * x_i)
        """
        if x.ndim == 1:
            x = x.reshape(1, -1)
            
        n_steps, dim = x.shape
        
        if is_streaming:
            # Temporal delta stream: Δx[t] = x[t] - x[t-1]
            deltas = np.zeros_like(x)
            prev = self.prev_input_state.copy()
            for t in range(n_steps):
                deltas[t] = x[t] - prev
                prev = x[t].copy()
            self.prev_input_state = prev
            
            # Micro-OTM Delta Gate: only fire if delta exceeds sensitivity threshold
            active_mask = (np.abs(deltas) >= self.delta_threshold).astype(np.float32)
            effective_x = deltas * active_mask
            active_ratio = float(np.mean(active_mask))
            self.total_evaluations += n_steps * dim
            self.active_delta_computes += int(np.sum(active_mask))
        else:
            effective_x = x
            active_ratio = 1.0
            self.total_evaluations += n_steps * dim
            self.active_delta_computes += n_steps * dim
            
        # Effective routing mesh: Subtractive Mask * Polarity
        # (Zero FP32 weight multiplications: only additions and subtractions)
        effective_mesh = self.mask * self.polarity # Shape: (out_dim, in_dim)
        raw_output = np.dot(effective_x, effective_mesh.T) # (n_steps, out_dim)
        
        stats = {
            "active_node_ratio": active_ratio,
            "mesh_sparsity": float(1.0 - np.mean(self.mask)),
            "active_connections": int(np.sum(self.mask))
        }
        return raw_output, stats

    def subtractive_prune_step(self, x_batch: np.ndarray, target_deltas: np.ndarray, min_keep_ratio: float = 0.20):
        """
        Subtractive Learning:
        Calculate causal alignment of each edge.
        Update causal credit scores and maintain only the most constructive pathways,
        carving away destructive and non-causal connections without starving the layer.
        """
        batch_size = x_batch.shape[0]
        alignment = np.zeros((self.out_dim, self.in_dim), dtype=np.float32)
        for b in range(batch_size):
            outer = np.outer(target_deltas[b], x_batch[b]) # (out_dim, in_dim)
            alignment += outer * self.polarity
            
        alignment /= batch_size
        
        # Accumulate causal credit over time
        self.causal_credit = 0.85 * self.causal_credit + 0.15 * alignment
        
        # Subtractive synthesis with survival quota:
        # Keep only the top-K highest causal scoring edges per output node
        k = max(1, int(self.in_dim * min_keep_ratio))
        new_mask = np.zeros_like(self.mask)
        
        for j in range(self.out_dim):
            row_scores = self.causal_credit[j]
            top_k_indices = np.argsort(row_scores)[-k:]
            # Only activate edges that have positive causal contribution
            positive_top_k = [i for i in top_k_indices if row_scores[i] > 0 or len(top_k_indices) == 1]
            if not positive_top_k:
                positive_top_k = [top_k_indices[-1]]
            new_mask[j, positive_top_k] = 1.0
            
        self.mask = new_mask


class MacroOTMCheckpoint:
    """
    Macro-OTM Keyframe Checkpoint (I-Frame Consolidation):
    - Normalizes signal energy across layers to prevent exponential attenuation
    - Non-linear threshold activation
    """
    def __init__(self, activation: str = "tanh_norm"):
        self.activation = activation

    def consolidate(self, h: np.ndarray) -> np.ndarray:
        # Energy Normalization across features
        std = np.std(h, axis=-1, keepdims=True) + 1e-5
        mean = np.mean(h, axis=-1, keepdims=True)
        h_norm = (h - mean) / std
        
        if self.activation == "tanh_norm":
            return np.tanh(h_norm)
        elif self.activation == "relu":
            return np.maximum(0, h_norm)
        return h_norm


class SubtractiveMeshNetwork:
    """
    Complete Weightless Subtractive OTM Mesh Network
    """
    def __init__(self, layer_dims: List[int], delta_threshold: float = 0.02, seed: int = 42):
        self.layer_dims = layer_dims
        self.layers: List[MicroOTMLayer] = []
        self.checkpoints: List[MacroOTMCheckpoint] = []
        
        for i in range(len(layer_dims) - 1):
            layer = MicroOTMLayer(
                in_dim=layer_dims[i],
                out_dim=layer_dims[i+1],
                delta_threshold=delta_threshold,
                seed=seed + i * 17
            )
            self.layers.append(layer)
            if i < len(layer_dims) - 2:
                self.checkpoints.append(MacroOTMCheckpoint(activation="tanh_norm"))

    def forward(self, x: np.ndarray, is_streaming: bool = False) -> Tuple[np.ndarray, List[Dict]]:
        curr = x
        all_stats = []
        for idx, layer in enumerate(self.layers):
            curr, stats = layer.forward_delta(curr, is_streaming=is_streaming)
            if idx < len(self.checkpoints):
                curr = self.checkpoints[idx].consolidate(curr)
            all_stats.append(stats)
        return curr, all_stats

    def train_subtractive(self, X: np.ndarray, Y: np.ndarray, epochs: int = 40, batch_size: int = 16, min_keep_ratio: float = 0.25):
        num_samples = X.shape[0]
        history = []
        
        for epoch in range(epochs):
            perm = np.random.permutation(num_samples)
            X_shuffled = X[perm]
            Y_shuffled = Y[perm]
            epoch_loss = 0.0
            
            for b in range(0, num_samples, batch_size):
                xb = X_shuffled[b:b+batch_size]
                yb = Y_shuffled[b:b+batch_size]
                
                # Forward pass
                layer_inputs = [xb]
                curr = xb
                for idx, layer in enumerate(self.layers):
                    curr, _ = layer.forward_delta(curr, is_streaming=False)
                    if idx < len(self.checkpoints):
                        curr = self.checkpoints[idx].consolidate(curr)
                    layer_inputs.append(curr)
                    
                preds = curr
                error_delta = yb - preds
                batch_loss = np.mean(error_delta ** 2)
                epoch_loss += batch_loss * len(xb)
                
                # Backward delta subtractive pruning
                curr_delta = error_delta
                for idx in reversed(range(len(self.layers))):
                    layer = self.layers[idx]
                    inp = layer_inputs[idx]
                    layer.subtractive_prune_step(inp, curr_delta, min_keep_ratio=min_keep_ratio)
                    effective_mesh = layer.mask * layer.polarity
                    curr_delta = np.dot(curr_delta, effective_mesh)
                    
            epoch_loss /= num_samples
            sparsities = [1.0 - np.mean(l.mask) for l in self.layers]
            history.append({"epoch": epoch + 1, "loss": epoch_loss, "sparsities": sparsities})
            
        return history

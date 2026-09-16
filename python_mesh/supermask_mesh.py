"""
Subtractive OTM Mesh with Edge-Popup (Supermask) Optimization
============================================================
Retains 100% weightless structure (Fixed Polarities {-1, +1}, 0 FP32 weight multiplications).
Uses continuous causal score rankings (Edge-Popup) to smoothly carve out the winning subnetwork.
"""

import numpy as np
from typing import List, Tuple, Dict
from otm_mesh import MacroOTMCheckpoint

class SupermaskOTMLayer:
    def __init__(self, in_dim: int, out_dim: int, delta_threshold: float = 0.02, seed: int = 42):
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.delta_threshold = delta_threshold
        
        rng = np.random.default_rng(seed)
        # Fixed polarity: unweighted base substrate (-1 or +1)
        self.polarity = rng.choice([-1.0, 1.0], size=(out_dim, in_dim))
        
        # Continuous Causal Pop Scores (used to dynamically carve the top-k% mask)
        self.scores = rng.normal(0, 1.0, size=(out_dim, in_dim)).astype(np.float32)
        self.mask = np.ones_like(self.scores)
        
        self.prev_input_state = np.zeros(in_dim, dtype=np.float32)
        self.total_evaluations = 0
        self.active_delta_computes = 0

    def compute_mask(self, sparsity: float = 0.5) -> np.ndarray:
        """
        Subtractive Carving: Keep only top (1 - sparsity) fraction of connections.
        """
        k = max(1, int(self.scores.size * (1.0 - sparsity)))
        threshold = np.partition(self.scores.flatten(), -k)[-k]
        self.mask = (self.scores >= threshold).astype(np.float32)
        return self.mask

    def forward_delta(self, x: np.ndarray, is_streaming: bool = False, sparsity: float = 0.5) -> Tuple[np.ndarray, Dict[str, float]]:
        if x.ndim == 1:
            x = x.reshape(1, -1)
        n_steps, dim = x.shape
        
        if is_streaming:
            deltas = np.zeros_like(x)
            prev = self.prev_input_state.copy()
            for t in range(n_steps):
                deltas[t] = x[t] - prev
                prev = x[t].copy()
            self.prev_input_state = prev
            
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
            
        mask = self.compute_mask(sparsity=sparsity)
        effective_mesh = mask * self.polarity # Shape: (out_dim, in_dim)
        
        # Zero FP32 multiplication on weights: integer/sign summation
        raw_output = np.dot(effective_x, effective_mesh.T)
        
        stats = {
            "active_node_ratio": active_ratio,
            "mesh_sparsity": sparsity,
            "active_connections": int(np.sum(mask))
        }
        return raw_output, stats


class SupermaskOTMNetwork:
    def __init__(self, layer_dims: List[int], delta_threshold: float = 0.02, seed: int = 42):
        self.layers: List[SupermaskOTMLayer] = []
        self.checkpoints: List[MacroOTMCheckpoint] = []
        
        for i in range(len(layer_dims) - 1):
            layer = SupermaskOTMLayer(
                in_dim=layer_dims[i],
                out_dim=layer_dims[i+1],
                delta_threshold=delta_threshold,
                seed=seed + i * 19
            )
            self.layers.append(layer)
            if i < len(layer_dims) - 2:
                self.checkpoints.append(MacroOTMCheckpoint(activation="tanh_norm"))

    def forward(self, x: np.ndarray, is_streaming: bool = False, sparsity: float = 0.5):
        curr = x
        all_stats = []
        activations = [curr]
        for idx, layer in enumerate(self.layers):
            curr, stats = layer.forward_delta(curr, is_streaming=is_streaming, sparsity=sparsity)
            if idx < len(self.checkpoints):
                curr = self.checkpoints[idx].consolidate(curr)
            activations.append(curr)
            all_stats.append(stats)
        return curr, activations, all_stats

    def train_edge_popup(self, X: np.ndarray, Y: np.ndarray, epochs: int = 80, lr: float = 0.1, sparsity: float = 0.5):
        num_samples = X.shape[0]
        for epoch in range(epochs):
            perm = np.random.permutation(num_samples)
            X_shuffled = X[perm]
            Y_shuffled = Y[perm]
            
            batch_size = 32
            for b in range(0, num_samples, batch_size):
                xb = X_shuffled[b:b+batch_size]
                yb = Y_shuffled[b:b+batch_size]
                
                preds, activations, _ = self.forward(xb, is_streaming=False, sparsity=sparsity)
                # Output delta
                dz = (preds - yb) / len(xb) # (batch, out_dim)
                
                # Straight-through estimator for submask pop scores
                curr_delta = dz
                for idx in reversed(range(len(self.layers))):
                    layer = self.layers[idx]
                    a_prev = activations[idx]
                    
                    # Gradient of score: delta * polarity * input
                    # dz: (batch, out_dim), a_prev: (batch, in_dim)
                    d_scores = np.dot(curr_delta.T, a_prev) * layer.polarity
                    
                    # Update causal scores (governs which connections get carved away)
                    layer.scores -= lr * d_scores
                    
                    if idx > 0:
                        effective_mesh = layer.mask * layer.polarity
                        curr_delta = np.dot(curr_delta, effective_mesh)
                        # Backprop through tanh
                        curr_delta = curr_delta * (1.0 - a_prev ** 2)

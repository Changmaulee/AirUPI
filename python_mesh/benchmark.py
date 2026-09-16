"""
Comprehensive Benchmark: Standard Float32 MLP vs. Subtractive OTM Mesh
========================================================================
Runs on CPU only. Evaluates accuracy, operation types, memory footprint, and delta sparsity.
"""

import time
import numpy as np
from otm_mesh import SubtractiveMeshNetwork

# -------------------------------------------------------------
# 1. Baseline Standard Float32 MLP (Dense Weights, Backpropagation)
# -------------------------------------------------------------
class StandardMLP:
    def __init__(self, layer_dims, lr=0.05, seed=42):
        self.weights = []
        self.biases = []
        self.lr = lr
        rng = np.random.default_rng(seed)
        for i in range(len(layer_dims) - 1):
            w = rng.normal(0, np.sqrt(2.0 / layer_dims[i]), size=(layer_dims[i+1], layer_dims[i])).astype(np.float32)
            b = np.zeros((layer_dims[i+1], 1), dtype=np.float32)
            self.weights.append(w)
            self.biases.append(b)

    def forward(self, x):
        curr = x.T # (dim, batch)
        activations = [curr]
        for idx, (w, b) in enumerate(zip(self.weights, self.biases)):
            z = np.dot(w, curr) + b
            if idx < len(self.weights) - 1:
                curr = np.tanh(z)
            else:
                curr = z
            activations.append(curr)
        return curr.T, activations

    def train_epoch(self, X, Y):
        curr_T = X.T
        y_T = Y.T
        preds_T, activations = self.forward(X)
        batch_size = X.shape[0]
        
        # Loss
        loss = np.mean((preds_T - Y) ** 2)
        
        # Backprop
        dz = 2 * (activations[-1] - y_T) / batch_size
        for idx in reversed(range(len(self.weights))):
            a_prev = activations[idx]
            dw = np.dot(dz, a_prev.T)
            db = np.sum(dz, axis=1, keepdims=True)
            if idx > 0:
                da_prev = np.dot(self.weights[idx].T, dz)
                dz = da_prev * (1.0 - a_prev ** 2) # tanh derivative
            self.weights[idx] -= self.lr * dw
            self.biases[idx] -= self.lr * db
        return loss

# -------------------------------------------------------------
# 2. Synthetic Benchmark Datasets (Non-Linear Geometric Patterns)
# -------------------------------------------------------------
def generate_concentric_circles(n_samples=600, noise=0.05, seed=42):
    rng = np.random.default_rng(seed)
    n = n_samples // 2
    r_inner = rng.uniform(0.1, 0.45, size=n)
    theta_inner = rng.uniform(0, 2*np.pi, size=n)
    x_inner = np.stack([r_inner * np.cos(theta_inner), r_inner * np.sin(theta_inner)], axis=1)
    y_inner = np.zeros((n, 1))

    r_outer = rng.uniform(0.65, 1.0, size=n)
    theta_outer = rng.uniform(0, 2*np.pi, size=n)
    x_outer = np.stack([r_outer * np.cos(theta_outer), r_outer * np.sin(theta_outer)], axis=1)
    y_outer = np.ones((n, 1))

    X = np.vstack([x_inner, x_outer]) + rng.normal(0, noise, size=(n_samples, 2))
    Y = np.vstack([y_inner, y_outer])
    
    perm = rng.permutation(n_samples)
    return X[perm].astype(np.float32), Y[perm].astype(np.float32)

def generate_streaming_temporal_signal(n_steps=500, in_dim=16, change_prob=0.15, seed=42):
    """
    Simulates streaming sensor / event data where inputs change sparsely in time.
    """
    rng = np.random.default_rng(seed)
    stream = np.zeros((n_steps, in_dim), dtype=np.float32)
    state = rng.normal(0, 1.0, size=in_dim).astype(np.float32)
    
    for t in range(n_steps):
        # Sparse updates
        mask = rng.uniform(0, 1, size=in_dim) < change_prob
        delta = rng.normal(0, 0.8, size=in_dim).astype(np.float32) * mask
        state += delta
        stream[t] = state.copy()
    return stream

# -------------------------------------------------------------
# 3. Main Benchmark Execution
# -------------------------------------------------------------
def run_benchmark():
    print("=" * 70)
    print("BENCHMARK: STANDARD FLOAT32 MLP vs. SUBTRACTIVE OTM MESH (CPU ONLY)")
    print("=" * 70)
    
    # Task 1: Non-linear Concentric Circles Classification
    X, Y = generate_concentric_circles(n_samples=800, seed=123)
    train_split = 600
    X_train, Y_train = X[:train_split], Y[:train_split]
    X_test, Y_test = X[train_split:], Y[train_split:]
    
    layer_dims = [2, 128, 64, 1]
    
    # A. Train Standard Float32 MLP
    print("\n[1] Training Standard Float32 MLP (Continuous Weights + Backprop)...")
    mlp = StandardMLP(layer_dims, lr=0.08, seed=42)
    t0 = time.perf_counter()
    for ep in range(60):
        loss = mlp.train_epoch(X_train, Y_train)
    t_mlp_train = time.perf_counter() - t0
    
    preds_mlp, _ = mlp.forward(X_test)
    mlp_acc = np.mean((preds_mlp > 0.5) == (Y_test > 0.5)) * 100.0
    print(f"    MLP Test Accuracy: {mlp_acc:.2f}% | Train Time: {t_mlp_train*1000:.2f} ms")
    
    # B. Train Subtractive OTM Mesh (Weightless + Subtractive Pruning)
    print("\n[2] Training Subtractive OTM Mesh (Discrete Mask + Polarity + Causal Pruning)...")
    mesh = SubtractiveMeshNetwork(layer_dims, delta_threshold=0.02, seed=42)
    t0 = time.perf_counter()
    history = mesh.train_subtractive(X_train, Y_train, epochs=40, batch_size=16, min_keep_ratio=0.35)
    t_mesh_train = time.perf_counter() - t0
    
    preds_mesh, _ = mesh.forward(X_test)
    mesh_acc = np.mean((preds_mesh > 0.0) == (Y_test > 0.5)) * 100.0
    print(f"    OTM Mesh Test Accuracy: {mesh_acc:.2f}% | Train Time: {t_mesh_train*1000:.2f} ms")
    
    # Report Pruning Stats
    print(f"    Final Mesh Sparsity (Subtracted Edges):")
    for l_idx, layer in enumerate(mesh.layers):
        carved = 1.0 - np.mean(layer.mask)
        print(f"      Layer {l_idx+1} ({layer.in_dim} -> {layer.out_dim}): {carved*100:.1f}% carved away (subtracted)")
        
    # Task 2: Streaming Event-Driven Delta Test (Micro-OTM)
    print("\n[3] Evaluating Micro-OTM Streaming Event Efficiency (Temporal Delta Skipping)...")
    # Reset layer counters for clean streaming measurement
    for l in mesh.layers:
        l.total_evaluations = 0
        l.active_delta_computes = 0
        l.prev_input_state = np.zeros(l.in_dim, dtype=np.float32)
        
    stream_data = generate_streaming_temporal_signal(n_steps=1000, in_dim=layer_dims[0], change_prob=0.15)
    
    # Forward stream through OTM Mesh with Micro-Delta gating
    t0 = time.perf_counter()
    _, stats_list = mesh.forward(stream_data, is_streaming=True)
    t_stream = time.perf_counter() - t0
    
    layer0 = mesh.layers[0]
    skip_rate = (1.0 - (layer0.active_delta_computes / max(1, layer0.total_evaluations))) * 100.0
    
    # -------------------------------------------------------------
    # 4. Detailed Efficiency & Hardware Profile
    # -------------------------------------------------------------
    # Parameter size calculation
    total_weights_mlp = sum(w.size + b.size for w, b in zip(mlp.weights, mlp.biases))
    mlp_memory_bytes = total_weights_mlp * 4 # 32-bit floats
    
    # OTM Mesh: 1 bit for binary mask + 1 bit for polarity per edge = 2 bits per connection!
    total_edges_mesh = sum(l.mask.size for l in mesh.layers)
    mesh_memory_bytes = (total_edges_mesh * 2) // 8
    
    print("\n" + "=" * 70)
    print("COMPARATIVE EFFICIENCY AUDIT")
    print("=" * 70)
    print(f"{'Metric':<35} | {'Standard Float32 MLP':<18} | {'Subtractive OTM Mesh':<18}")
    print("-" * 75)
    print(f"{'Accuracy (Non-linear circles)':<35} | {mlp_acc:>17.1f}% | {mesh_acc:>17.1f}%")
    print(f"{'FP32 Multiplications per Forward':<35} | {total_weights_mlp:>18} | {'0 (Sign Add/Sub)':>18}")
    print("-" * 75)
    print(f"{'Parameter Storage (Bytes)':<35} | {mlp_memory_bytes:>15} B | {mesh_memory_bytes:>15} B")
    print(f"{'Memory Footprint Reduction':<35} | {'Baseline (1.0x)':>18} | {f'{mlp_memory_bytes/mesh_memory_bytes:.1f}x smaller':>18}")
    print(f"{'Streaming Compute Skipped (Deltas)':<35} | {'0% (computes all)':>18} | {f'{skip_rate:.1f}% skipped':>18}")
    print("=" * 70)

if __name__ == "__main__":
    run_benchmark()

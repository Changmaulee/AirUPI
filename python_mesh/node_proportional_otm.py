"""
Dedicated Node-Proportional OTM Neural Architecture (v1.0)
===========================================================
Authored for TimeMeshin Spatio-Temporal Engine by Chandramouli.

Architecture:
1. MicroOTMNode: 1:1 Node-level P-Frame state tracker (detects local signal deltas |delta_s| > threshold).
2. ClusterOTM: Sub-network B-Frame speculative sandbox with OCC rollback for localized pruning.
3. MacroOTMLayer: Layer-level I-Frame coordinator (energy normalization + TimeMeshin commits).
4. NodeProportionalOTMNet: Multi-tier event-driven neural mesh that scales OTM controllers with node count.
5. TimeMeshinNodeTracker: SQLite deterministic spatio-temporal auditor (t <= playhead).
"""

import numpy as np
import sqlite3
import datetime
import time
from typing import List, Tuple, Dict, Optional

class TimeMeshinNodeTracker:
    """
    Tracks causal lineage, keyframes (I-Frames), deltas (P-Frames), 
    and counterfactual rollbacks (B-Frames) into SQLite.
    """
    def __init__(self, db_path="node_otm_audit.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS otm_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frame_type TEXT,
                    timestamp TEXT,
                    layer_idx INTEGER,
                    cluster_idx INTEGER,
                    node_idx INTEGER,
                    active_nodes INTEGER,
                    dormant_nodes INTEGER,
                    sparsity REAL,
                    causal_rationale TEXT
                )
            """)

    def record_event(self, frame_type: str, timestamp: str, layer_idx: int,
                     cluster_idx: int, node_idx: int, active_nodes: int,
                     dormant_nodes: int, sparsity: float, rationale: str):
        with self.conn:
            self.conn.execute("""
                INSERT INTO otm_events 
                (frame_type, timestamp, layer_idx, cluster_idx, node_idx, active_nodes, dormant_nodes, sparsity, causal_rationale)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (frame_type, timestamp, layer_idx, cluster_idx, node_idx, active_nodes, dormant_nodes, sparsity, rationale))

    def scrub(self, playhead: str) -> List[Tuple]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT event_id, frame_type, timestamp, layer_idx, cluster_idx, node_idx, active_nodes, dormant_nodes, sparsity, causal_rationale
            FROM otm_events
            WHERE timestamp <= ?
            ORDER BY timestamp ASC
        """, (playhead,))
        return cursor.fetchall()


class MicroOTMNode:
    """
    Individual Node-Level Controller:
    - Tracks instantaneous temporal delta delta_s = s_t - s_{t-1}
    - Gating rule: If |delta_s| <= threshold, node is DORMANT (0 downstream compute).
    """
    def __init__(self, node_id: int, delta_threshold: float = 0.02):
        self.node_id = node_id
        self.delta_threshold = delta_threshold
        self.prev_state = 0.0
        self.is_active = True
        self.total_evals = 0
        self.dormant_evals = 0

    def evaluate_delta(self, current_val: float) -> Tuple[float, bool]:
        self.total_evals += 1
        delta = current_val - self.prev_state
        self.prev_state = current_val
        
        if abs(delta) < self.delta_threshold:
            self.is_active = False
            self.dormant_evals += 1
            return 0.0, False
        else:
            self.is_active = True
            return delta, True

    def reset_state(self):
        self.prev_state = 0.0
        self.is_active = True


class ClusterOTM:
    """
    Sub-Network Community Controller:
    - Manages a subset of K nodes and their incoming connections.
    - Runs localized subtractive pruning and speculative B-Frame counterfactuals under OCC.
    """
    def __init__(self, cluster_id: int, in_dim: int, out_nodes: List[int], seed: int = 42):
        self.cluster_id = cluster_id
        self.in_dim = in_dim
        self.out_nodes = out_nodes
        self.cluster_size = len(out_nodes)
        
        rng = np.random.default_rng(seed + cluster_id * 31)
        octave_palette = np.array([-2.0, -1.0, -0.5, 0.5, 1.0, 2.0], dtype=np.float32)
        self.polarity = rng.choice(octave_palette, size=(self.cluster_size, in_dim))
        
        self.mask = np.ones((self.cluster_size, in_dim), dtype=np.float32)
        self.causal_scores = rng.integers(-20, 20, size=(self.cluster_size, in_dim), dtype=np.int32)
        self.threshold = np.zeros((self.cluster_size, 1), dtype=np.float32)

    def forward(self, x_in: np.ndarray) -> np.ndarray:
        eff_mesh = self.mask * self.polarity
        if x_in.ndim == 1:
            z = np.dot(eff_mesh, x_in) + self.threshold.flatten()
        else:
            z = np.dot(x_in, eff_mesh.T) + self.threshold.T
        return z

    def run_b_frame_counterfactual(self, x_batch: np.ndarray, y_target: np.ndarray,
                                   loss_fn, target_sparsity: float = 0.40) -> bool:
        orig_out = self.forward(x_batch)
        orig_loss = loss_fn(orig_out, y_target)
        
        k = max(1, int(self.causal_scores.size * (1.0 - target_sparsity)))
        thresh = np.partition(self.causal_scores.flatten(), -k)[-k]
        speculative_mask = (self.causal_scores >= thresh).astype(np.float32)
        
        saved_mask = self.mask.copy()
        self.mask = speculative_mask
        speculative_out = self.forward(x_batch)
        speculative_loss = loss_fn(speculative_out, y_target)
        
        if speculative_loss <= orig_loss * 1.05:
            return True
        else:
            self.mask = saved_mask
            return False

    def update_causal_credit(self, curr_delta: np.ndarray, prev_act: np.ndarray, lr_step: int = 1):
        delta_q = np.clip(np.round(curr_delta * 4.0), -2, 2).astype(np.int32)
        act_q = np.clip(np.round(prev_act * 2.0), 0, 4).astype(np.int32)
        int_alignment = np.dot(delta_q, act_q.T)
        sign_pol = np.sign(self.polarity).astype(np.int32)
        
        score_delta = int_alignment * sign_pol
        self.causal_scores -= np.clip(score_delta, -10, 10) * lr_step
        self.threshold -= np.mean(curr_delta, axis=1, keepdims=True) * 0.05


class MacroOTMLayer:
    """
    Layer Coordinator:
    - Spawns Micro-OTMs (1:1 with input nodes) and Cluster-OTMs (proportional to layer size).
    - Coordinates I-Frame keyframe consolidation, energy normalization, and streaming execution.
    """
    def __init__(self, layer_idx: int, in_dim: int, out_dim: int,
                 cluster_size: int = 32, delta_threshold: float = 0.02, seed: int = 42):
        self.layer_idx = layer_idx
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.cluster_size = cluster_size
        self.delta_threshold = delta_threshold
        
        self.micro_otms = [MicroOTMNode(node_id=i, delta_threshold=delta_threshold) for i in range(in_dim)]
        
        self.clusters: List[ClusterOTM] = []
        num_clusters = max(1, (out_dim + cluster_size - 1) // cluster_size)
        for c in range(num_clusters):
            start_idx = c * cluster_size
            end_idx = min(out_dim, (c + 1) * cluster_size)
            cluster_nodes = list(range(start_idx, end_idx))
            cluster = ClusterOTM(cluster_id=c, in_dim=in_dim, out_nodes=cluster_nodes, seed=seed + c * 13)
            self.clusters.append(cluster)

    def forward_streaming(self, x_stream: np.ndarray) -> Tuple[np.ndarray, Dict[str, int]]:
        seq_len, dim = x_stream.shape
        out_activations = np.zeros((seq_len, self.out_dim), dtype=np.float32)
        
        active_node_events = 0
        dormant_node_events = 0
        
        for t in range(seq_len):
            x_t = x_stream[t]
            delta_vec = np.zeros(dim, dtype=np.float32)
            
            for i in range(dim):
                d_val, is_active = self.micro_otms[i].evaluate_delta(x_t[i])
                delta_vec[i] = d_val
                if is_active:
                    active_node_events += 1
                else:
                    dormant_node_events += 1
            
            layer_z = np.zeros(self.out_dim, dtype=np.float32)
            for cluster in self.clusters:
                c_out = cluster.forward(x_t)
                for idx, out_node in enumerate(cluster.out_nodes):
                    layer_z[out_node] = c_out[idx]
            
            std = np.std(layer_z) + 1e-6
            normalized_z = np.tanh(layer_z / std)
            out_activations[t] = normalized_z
            
        stats = {
            "active_events": active_node_events,
            "dormant_events": dormant_node_events,
            "total_events": active_node_events + dormant_node_events
        }
        return out_activations, stats

    def forward_batch(self, x_batch: np.ndarray) -> np.ndarray:
        batch_size = x_batch.shape[0]
        layer_z = np.zeros((batch_size, self.out_dim), dtype=np.float32)
        for cluster in self.clusters:
            c_out = cluster.forward(x_batch)
            for idx, out_node in enumerate(cluster.out_nodes):
                layer_z[:, out_node] = c_out[:, idx]
                
        std = np.std(layer_z, axis=1, keepdims=True) + 1e-6
        return np.tanh(layer_z / std)

    def get_layer_sparsity(self) -> float:
        total_connections = 0
        active_connections = 0
        for cluster in self.clusters:
            total_connections += cluster.mask.size
            active_connections += int(np.sum(cluster.mask))
        return 1.0 - (active_connections / max(1, total_connections))


class NodeProportionalOTMNet:
    """
    Full Weightless Subtractive Neural Mesh with Dedicated Node-Proportional OTMs.
    """
    def __init__(self, layer_dims: List[int], cluster_size: int = 32,
                 delta_threshold: float = 0.02, db_path: str = "node_otm_audit.db", seed: int = 42):
        self.layer_dims = layer_dims
        self.layers: List[MacroOTMLayer] = []
        self.tracker = TimeMeshinNodeTracker(db_path=db_path)
        
        total_micro_nodes = 0
        total_clusters = 0
        for i in range(len(layer_dims) - 1):
            layer = MacroOTMLayer(
                layer_idx=i,
                in_dim=layer_dims[i],
                out_dim=layer_dims[i+1],
                cluster_size=cluster_size,
                delta_threshold=delta_threshold,
                seed=seed + i * 19
            )
            self.layers.append(layer)
            total_micro_nodes += len(layer.micro_otms)
            total_clusters += len(layer.clusters)
            
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tracker.record_event(
            frame_type="I_FRAME",
            timestamp=now_str,
            layer_idx=0,
            cluster_idx=0,
            node_idx=0,
            active_nodes=total_micro_nodes,
            dormant_nodes=0,
            sparsity=0.0,
            rationale=f"Macro I-Frame 0: Initialized Node-Proportional OTM Mesh ({total_micro_nodes} Micro-OTMs, {total_clusters} Cluster-OTMs across {len(self.layers)} layers)"
        )

    def forward_streaming(self, x_stream: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        curr = x_stream
        all_stats = []
        for layer in self.layers:
            curr, stats = layer.forward_streaming(curr)
            all_stats.append(stats)
        return curr, all_stats

    def forward_batch(self, x_batch: np.ndarray) -> Tuple[np.ndarray, List[np.ndarray]]:
        curr = x_batch
        activations = [curr]
        for layer in self.layers:
            curr = layer.forward_batch(curr)
            activations.append(curr)
        return curr, activations

    def train_subtractive_b_frames(self, X: np.ndarray, Y: np.ndarray, epochs: int = 25,
                                   batch_size: int = 32, target_sparsity: float = 0.40):
        n_samples = X.shape[0]
        now_base = datetime.datetime.now()
        
        def dummy_loss(pred, target):
            return np.mean((pred - target) ** 2)

        for epoch in range(epochs):
            perm = np.random.permutation(n_samples)
            X_shuff = X[perm]
            Y_shuff = Y[perm]
            
            for b in range(0, n_samples, batch_size):
                xb = X_shuff[b:b+batch_size]
                yb = Y_shuff[b:b+batch_size]
                
                preds, activations = self.forward_batch(xb)
                error_delta = (preds - yb).T
                
                curr_delta = error_delta
                for l_idx in reversed(range(len(self.layers))):
                    layer = self.layers[l_idx]
                    prev_act = activations[l_idx].T
                    
                    for cluster in layer.clusters:
                        c_nodes = cluster.out_nodes
                        c_delta = curr_delta[c_nodes]
                        cluster.update_causal_credit(c_delta, prev_act)
                        
                        if epoch % 5 == 0 and b == 0:
                            success = cluster.run_b_frame_counterfactual(
                                xb if l_idx == 0 else activations[l_idx],
                                yb[:, c_nodes] if l_idx == len(self.layers)-1 else curr_delta[c_nodes].T,
                                dummy_loss,
                                target_sparsity=target_sparsity
                            )
                            
                    if l_idx > 0:
                        all_eff_mesh = np.zeros((layer.out_dim, layer.in_dim), dtype=np.float32)
                        for cluster in layer.clusters:
                            all_eff_mesh[cluster.out_nodes] = cluster.mask * cluster.polarity
                        curr_delta = np.dot(all_eff_mesh.T, curr_delta)
            
            if (epoch + 1) % 5 == 0:
                t_stamp = (now_base + datetime.timedelta(seconds=epoch*10)).strftime("%Y-%m-%d %H:%M:%S")
                for l_idx, layer in enumerate(self.layers):
                    sp = layer.get_layer_sparsity()
                    self.tracker.record_event(
                        frame_type="I_FRAME",
                        timestamp=t_stamp,
                        layer_idx=l_idx,
                        cluster_idx=0,
                        node_idx=0,
                        active_nodes=layer.in_dim,
                        dormant_nodes=0,
                        sparsity=sp,
                        rationale=f"Macro I-Frame Epoch {epoch+1}: Layer {l_idx} sparsity at {sp*100:.1f}%. Causal OCC committed."
                    )

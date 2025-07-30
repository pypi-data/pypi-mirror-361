# FILE: pidtransformer/models/layers.py
import torch
import torch.nn as nn
import torch.nn.functional as F
# --- BUG FIX: Correct the import path to be absolute from the package root ---
from pidtransformer.modules.pid_controller import GeometricPIDController

class FeedForwardBlock(nn.Module):
    def __init__(self, d_model: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.linear1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear2 = nn.Linear(d_ff, d_model)
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.linear2(self.dropout(F.relu(self.linear1(x))))

# ... (The rest of the code in the PIDLayer, GroupPIDLayer classes is the same as before) ...
# ...
class PIDLayer(nn.Module):
    # This class remains for backward compatibility.
    def __init__(self, hidden_dim: int, control_dim: int, kp: float, ki: float, kd: float, windup_limit: float, d_filter_window_size: int, **kwargs):
        super().__init__()
        self.ffn = FeedForwardBlock(d_model=hidden_dim, d_ff=hidden_dim * 4)
        self.projection = nn.Linear(hidden_dim, control_dim, bias=False)
        self.pid_controller = GeometricPIDController(
            kp=kp, ki=ki, kd=kd, dim=control_dim, 
            windup_limit=windup_limit, d_filter_window_size=d_filter_window_size
        )
    def get_orthogonality_loss(self, phase: str = 'small'):
        w = self.projection.weight
        w_wt = torch.matmul(w, w.t())
        identity = torch.eye(w.size(0), device=w.device)
        loss = torch.norm(w_wt - identity, p='fro')**2
        return loss
    def forward(self, x: torch.Tensor, phase: str = 'small'):
        hidden_state_out = self.ffn(x)
        projected_state = self.projection(hidden_state_out)
        error = projected_state
        control_signal, pid_terms = self.pid_controller(error)
        feedback = F.linear(control_signal, self.projection.weight.t())
        stabilized_output = hidden_state_out + feedback
        # Return dummy weights to maintain a consistent API with GroupPIDLayer
        dummy_weights = torch.empty(0) 
        return stabilized_output, pid_terms, dummy_weights

class GroupPIDLayer(nn.Module):
    """
    Implements PID control over independent subgroups of the control space.
    Now supports Gating mechanism.
    """
    def __init__(self, hidden_dim: int, control_dims: dict, num_groups: dict, 
                 kp: float, ki: float, kd: float, windup_limit: float, d_filter_window_size: int,
                 use_gating: bool = False):
        super().__init__()

        self.ffn = FeedForwardBlock(d_model=hidden_dim, d_ff=hidden_dim * 4)
        self.use_gating = use_gating

        self.projections = nn.ModuleDict()
        self.pid_controllers = nn.ModuleDict()
        self.group_dims = {}
        self.num_groups = num_groups

        if self.use_gating:
            self.gating_network = nn.ModuleDict()

        for phase, control_dim in control_dims.items():
            num_g = num_groups[phase]
            assert control_dim % num_g == 0, f"control_dim for phase {phase} must be divisible by num_groups"

            group_dim = control_dim // num_g
            self.group_dims[phase] = group_dim

            self.projections[phase] = nn.Linear(hidden_dim, control_dim, bias=False)
            self.pid_controllers[phase] = nn.ModuleList([
                GeometricPIDController(
                    kp=kp, ki=ki, kd=kd, dim=group_dim, 
                    windup_limit=windup_limit, d_filter_window_size=d_filter_window_size
                ) for _ in range(num_g)
            ])

            if self.use_gating:
                self.gating_network[phase] = nn.Linear(hidden_dim, num_g)

    def get_orthogonality_loss(self, phase: str = 'small'):
        w = self.projections[phase].weight
        w_wt = torch.matmul(w, w.t())
        identity = torch.eye(w.size(0), device=w.device)
        loss = torch.norm(w_wt - identity, p='fro')**2
        return loss

    def forward(self, x: torch.Tensor, phase: str = 'small'):
        hidden_state_out = self.ffn(x)

        projection = self.projections[phase]
        pid_controllers = self.pid_controllers[phase]
        current_num_groups = self.num_groups[phase]
        
        projected_state = projection(hidden_state_out)

        B, S, C = projected_state.shape
        grouped_error = projected_state.view(B, S, current_num_groups, self.group_dims[phase])

        control_signals_list = []
        pid_terms_list = []

        for i in range(current_num_groups):
            error_group_i = grouped_error[:, :, i, :]
            control_i, terms_i = pid_controllers[i](error_group_i)
            control_signals_list.append(control_i)
            pid_terms_list.append(terms_i)
            
        gating_weights = torch.empty(0)
        
        if self.use_gating:
            gating_scores = self.gating_network[phase](hidden_state_out)
            gating_weights = F.softmax(gating_scores, dim=-1)
            
            weights_reshaped = gating_weights.unsqueeze(-1)
            stacked_signals = torch.stack(control_signals_list, dim=2)
            
            weighted_signals = stacked_signals * weights_reshaped
            control_signal = weighted_signals.view(B, S, -1)

        else:
            control_signal = torch.cat(control_signals_list, dim=-1)

        avg_pid_terms = {
            'p_norm': torch.mean(torch.stack([d['p_norm'] for d in pid_terms_list])),
            'i_norm': torch.mean(torch.stack([d['i_norm'] for d in pid_terms_list])),
            'd_norm': torch.mean(torch.stack([d['d_norm'] for d in pid_terms_list])),
        }

        feedback = F.linear(control_signal, projection.weight.t())
        stabilized_output = hidden_state_out + feedback

        return stabilized_output, avg_pid_terms, gating_weights
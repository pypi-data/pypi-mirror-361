# FILE: src/pid_transformer/modules/pid_controller.py
import torch
import torch.nn as nn
from collections import deque

class GeometricPIDController(nn.Module):
    def __init__(self, kp: float, ki: float, kd: float, dim: int, 
                 windup_limit: float = 100.0, d_filter_window_size: int = 1):
        super().__init__()
        # Base gains
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

        # Learnable lambda weights, initialized to 1.0
        self.lambda_p = nn.Parameter(torch.ones(1))
        self.lambda_i = nn.Parameter(torch.ones(1))
        self.lambda_d = nn.Parameter(torch.ones(1))

        self.windup_limit = windup_limit

        self.register_buffer('integral', torch.zeros(1, dim))
        self.register_buffer('prev_error', torch.zeros(1, dim))

        self.d_filter_window_size = d_filter_window_size
        if self.d_filter_window_size > 1:
            self.error_history = deque(maxlen=d_filter_window_size)

    def forward(self, error: torch.Tensor):
        # I-term and Anti-Windup
        self.integral = self.integral.detach() + error
        integral_norm = torch.norm(self.integral)
        if integral_norm > self.windup_limit:
            self.integral = self.integral * (self.windup_limit / integral_norm)

        # D-term and Low-Pass Filter
        if self.d_filter_window_size > 1:
            calculation_window = list(self.error_history) + [error]
            stacked_errors = torch.stack(calculation_window, dim=0)
            filtered_error = torch.mean(stacked_errors, dim=0)
            self.error_history.append(error.detach())
        else:
            filtered_error = error
        derivative = filtered_error - self.prev_error.detach()
        self.prev_error = filtered_error.detach()

        # --- Combine Terms with Learnable Lambdas ---
        p_term = self.Kp * error
        i_term = self.Ki * self.integral
        d_term = self.Kd * derivative

        control_signal = (self.lambda_p * p_term) + \
                         (self.lambda_i * i_term) + \
                         (self.lambda_d * d_term)

        pid_terms = {
            'p_norm': torch.mean(torch.norm(self.lambda_p * p_term, p=2, dim=-1)),
            'i_norm': torch.mean(torch.norm(self.lambda_i * i_term, p=2, dim=-1)),
            'd_norm': torch.mean(torch.norm(self.lambda_d * d_term, p=2, dim=-1)),
        }

        return control_signal, pid_terms

    def reset_states(self):
        self.integral.zero_()
        self.prev_error.zero_()
        if hasattr(self, 'error_history'):
            self.error_history.clear()
# FILE: src/pid_transformer/utils/gsa.py
import torch
from scipy.stats import kurtosis

def _calculate_power_spectrum(signal_1d: torch.Tensor):
    """Helper function to calculate power spectrum and frequencies."""
    n_fft = signal_1d.numel()
    if n_fft < 2:
        return torch.empty(0), torch.empty(0)
    
    fft_result = torch.fft.rfft(signal_1d)
    power_spectrum = torch.abs(fft_result)**2
    freqs = torch.fft.rfftfreq(n_fft)
    
    return power_spectrum, freqs

def get_advanced_gsa_metrics(gradient: torch.Tensor, high_freq_threshold: float = 0.1):
    """
    Calculates a dictionary of advanced GSA metrics for a given gradient.
    """
    if gradient is None or gradient.numel() < 2:
        return {
            'gsa_high_freq_ratio': 0.0,
            'spectral_entropy': 0.0,
            'spectral_flatness': 0.0,
            'gradient_kurtosis': 0.0,
        }

    signal = gradient.detach().view(-1).cpu().to(torch.float32)
    
    # --- Spectrum-based metrics ---
    power_spectrum, freqs = _calculate_power_spectrum(signal)
    
    total_energy = torch.sum(power_spectrum)
    if total_energy > 0:
        # High-frequency energy ratio
        high_freq_mask = freqs > high_freq_threshold
        high_freq_energy = torch.sum(power_spectrum[high_freq_mask])
        gsa_ratio = (high_freq_energy / total_energy).item()
        
        # Spectral Entropy
        prob_dist = power_spectrum / total_energy
        # Add a small epsilon to prevent log(0)
        entropy = -torch.sum(prob_dist * torch.log2(prob_dist + 1e-9)).item()

        # Spectral Flatness
        geometric_mean = torch.exp(torch.mean(torch.log(power_spectrum + 1e-9)))
        arithmetic_mean = torch.mean(power_spectrum)
        flatness = (geometric_mean / (arithmetic_mean + 1e-9)).item()
    else:
        gsa_ratio, entropy, flatness = 0.0, 0.0, 0.0

    # --- Distribution-based metric ---
    # Kurtosis ('fisher'=True subtracts 3 to make normal dist kurtosis=0)
    kurt = kurtosis(signal.numpy(), fisher=True)

    return {
        'gsa_high_freq_ratio': gsa_ratio,
        'spectral_entropy': entropy,
        'spectral_flatness': flatness,
        'gradient_kurtosis': float(kurt),
    }

# The original function is kept for backward compatibility if needed elsewhere,
# but our new training loop will use the more advanced function.
def calculate_gradient_spectrum(gradient: torch.Tensor, high_freq_threshold: float = 0.1, get_energy_ratio: bool = False):
    if get_energy_ratio:
        metrics = get_advanced_gsa_metrics(gradient, high_freq_threshold)
        return metrics['gsa_high_freq_ratio']
    else:
        signal = gradient.detach().view(-1).cpu().to(torch.float32)
        return _calculate_power_spectrum(signal)
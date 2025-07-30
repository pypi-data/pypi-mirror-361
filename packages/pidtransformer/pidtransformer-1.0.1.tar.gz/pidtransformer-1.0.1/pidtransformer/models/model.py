# FILE: main.py
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import sys
import json
import time
from tqdm import tqdm
import argparse
import numpy as np
import os

# Refactored imports for the new package structure
from pidtransformer.models.model import PIDTransformer
from pidtransformer.data.data_pipeline import get_data
from pidtransformer.utils.gsa import get_advanced_gsa_metrics
from configs.base_config import get_config

def train_model(config):
    """
    The core training and evaluation logic, encapsulated in a function.
    """
    start_time = time.time()
    print("--- Starting Experiment Run ---")

    device = torch.device(config["device"])
    
    print(f"Device: {device}, Group PID: {config.get('use_group_pid')}, Gating: {config.get('use_gating')}, Adaptive Dim: {config.get('use_adaptive_dim')}")
    print(f"Total Steps: {config['num_steps']}, Ortho Weight: {config.get('ortho_weight')}")

    # Create results & checkpoints directories if they don't exist
    os.makedirs("results", exist_ok=True)
    os.makedirs("checkpoints", exist_ok=True)

    dataset, tokenizer = get_data(config)
    config['vocab_size'] = tokenizer.vocab_size
    train_loader = DataLoader(dataset, batch_size=config["batch_size"], shuffle=True)
    
    # For trajectory tracking
    tracking_batch = next(iter(train_loader))
    tracking_input_ids = tracking_batch['input_ids'].to(device)
    
    model = PIDTransformer(config).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"])
    criterion = nn.CrossEntropyLoss()

    history = {
        "steps": [], "loss": [], "p_norm": [], "i_norm": [], "d_norm": [], "trajectory": [],
        "gsa_high_freq_ratio": [], "spectral_entropy": [], "spectral_flatness": [], "gradient_kurtosis": []
    }
    data_iterator = iter(train_loader)
    progress_bar = tqdm(range(config['num_steps']), desc="Training Steps")
    
    layer_to_track = config['n_layers'] // 2
    target_layer = model.pid_layers[layer_to_track]

    for step in progress_bar:
        model.train()
        phase = 'small'
        if config.get('use_adaptive_dim') and step < config.get('dimension_switch_step', 0):
            phase = 'large'

        # Dynamically select the GSA target parameter based on phase
        if config.get('use_group_pid'):
            gsa_target_weight = target_layer.projections[phase].weight
        else:
            gsa_target_weight = target_layer.projection.weight
        
        try:
            batch = next(data_iterator)
        except StopIteration:
            data_iterator = iter(train_loader)
            batch = next(data_iterator)

        input_ids, labels = batch['input_ids'].to(device), batch['labels'].to(device)
        outputs, pid_terms, _, _ = model(input_ids, phase=phase)
        
        ce_loss = criterion(outputs.view(-1, config["vocab_size"]), labels.view(-1))
        
        ortho_loss = 0
        if config.get('ortho_weight', 0) > 0 and config.get('use_group_pid'):
            for layer in model.pid_layers:
                ortho_loss += layer.get_orthogonality_loss(phase=phase)
        
        total_loss = ce_loss + config.get('ortho_weight', 0) * ortho_loss

        optimizer.zero_grad()
        total_loss.backward()
        gsa_metrics = get_advanced_gsa_metrics(gsa_target_weight.grad)
        optimizer.step()

        if step % config['log_freq'] == 0:
            history["steps"].append(step)
            history["loss"].append(ce_loss.item())
            history["p_norm"].append(pid_terms["p_norm"].item())
            history["i_norm"].append(pid_terms["i_norm"].item())
            history["d_norm"].append(pid_terms["d_norm"].item())
            for key, value in gsa_metrics.items():
                if key not in history: history[key] = []
                history[key].append(value)

            # Trajectory logging
            model.eval()
            with torch.no_grad():
                _, _, hidden_state, _ = model(tracking_input_ids, capture_hidden_states_layer=layer_to_track, phase=phase)
                if hidden_state is not None:
                    trajectory_point = hidden_state[0, 10, :].numpy()
                    history["trajectory"].append(trajectory_point.tolist())

        progress_bar.set_postfix({"loss": f"{ce_loss.item():.4f}"})

    total_time = time.time() - start_time
    print(f"--- Training Run Finished in {total_time:.2f} seconds ---")
    
    # Save detailed history
    history_path = os.path.join("results", f"{config['experiment_name']}_history.json")
    with open(history_path, 'w') as f:
        json.dump(history, f)
    print(f"Full history saved to {history_path}")

    # Save model weights
    model_path = os.path.join("checkpoints", f"{config['experiment_name']}_model.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Model weights saved to {model_path}")

    # Save summary
    final_avg_loss = np.mean(history["loss"][-10:]) if len(history["loss"]) >= 10 else np.mean(history["loss"])
    summary = {
        "experiment_name": config['experiment_name'],
        "config": {k: v for k, v in config.items() if isinstance(v, (int, float, str, bool, dict))},
        "results": {
            "total_time_seconds": total_time,
            "final_avg_loss": float(final_avg_loss),
            "min_loss": float(np.min(history["loss"])) if history["loss"] else None,
        }
    }
    summary_path = os.path.join("results", f"{config['experiment_name']}_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
    print(f"Experiment summary saved to {summary_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PID-Transformer Experiment Runner")
    parser.add_argument('--experiment_name', type=str, default="pid_transformer_test", help="A name for the experiment.")
    parser.add_argument('--num_steps', type=int, default=None, help="Total number of training steps.")
    parser.add_argument('--log_freq', type=int, default=None, help="Frequency of logging data.")
    parser.add_argument('--dimension_switch_step', type=int, default=None, help="Step to switch dimensions in adaptive mode.")
    parser.add_argument('--kp', type=float, default=None)
    parser.add_argument('--ki', type=float, default=None)
    parser.add_argument('--kd', type=float, default=None)
    parser.add_argument('--d_filter_window_size', type=int, default=None)
    parser.add_argument('--ortho_weight', type=float, default=None)
    parser.add_argument('--use_group_pid', action='store_true', help="Enable group-wise PID.")
    parser.add_argument('--use_adaptive_dim', action='store_true', help="Enable adaptive dimension.")
    parser.add_argument('--use_gating', action='store_true', help="Enable the gating mechanism.")
    
    args = parser.parse_args()
    
    config = get_config()
    # Override base config with any arguments provided via command line
    for key, value in vars(args).items():
        if value is not None:
             # For 'action=store_true', value is True if flag is present, False if not.
             # We only want to overwrite if the flag is actively used.
            if isinstance(value, bool):
                if value:
                    config[key] = value
            else:
                config[key] = value
            
    train_model(config)
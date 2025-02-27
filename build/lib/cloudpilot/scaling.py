import torch
import numpy as np
import os

# Define the mapping from action indices to recommendations.
ACTIONS = {0: "Scale Down", 1: "Maintain", 2: "Scale Up"}


class RLScaler:
    def __init__(self, model_path="cloudpilot/rl_scaling_model.pt"):
        try:
            # Try loading the TorchScript model
            self.model = torch.jit.load(model_path)
            self.model.eval()
        except Exception as e:
            # Log a warning and use a dummy model that always returns a fixed tensor.
            print(
                f"Warning: Could not load model from {model_path}. Using dummy model. Error: {e}"
            )
            self.model = None

    def get_action(self, state):
        """
        Given a state vector, returns the scaling action.

        Args:
            state (list or np.array): [cpu_util, mem_util, request_rate, network_latency, user_demand]

        Returns:
            str: A scaling recommendation ("Scale Down", "Maintain", or "Scale Up")
        """
        # If the model isn't loaded, return a dummy recommendation.
        if self.model is None:
            return "Maintain"
        # Convert state to a torch tensor and add a batch dimension.
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            # Obtain Q-values from the model.
            q_values = self.model(state_tensor)
        # Choose the action with the highest Q-value.
        action_idx = int(torch.argmax(q_values, dim=1)[0].item())
        return ACTIONS.get(action_idx, "Maintain")


def recommend_scaling(cpu_util, mem_util, request_rate, network_latency, user_demand):
    """
    Returns an RL-based scaling recommendation.

    Args:
        cpu_util (float): CPU utilization percentage.
        mem_util (float): Memory utilization percentage.
        request_rate (float): Request rate (can be normalized or raw).
        network_latency (float): Average network latency in ms.
        user_demand (float): Normalized measure of user demand (0 to 1).

    Returns:
        str: Scaling recommendation, e.g., "RL-based Recommendation: Scale Up"
    """
    # Construct the state vector.
    state = [cpu_util, mem_util, request_rate, network_latency, user_demand]
    scaler = RLScaler()  # Loads the TorchScript model or uses dummy.
    action = scaler.get_action(state)
    return f"RL-based Recommendation: {action}"

import torch
import torch.nn as nn
import torch.optim as optim


class DQN(nn.Module):
    def __init__(self, state_dim=5, action_dim=3):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_dim, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, action_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def train_dummy_model():
    # Create a dummy DQN model.
    model = DQN()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    # Dummy training: simulate training data with random inputs and targets.
    for epoch in range(
        100
    ):  # For a real project, use many more epochs and proper data.
        # Simulate a batch of 32 state vectors (each of dimension 5).
        state_batch = torch.rand((32, 5))
        # Simulate target Q-values for each action (3 actions).
        target_batch = torch.rand((32, 3))

        optimizer.zero_grad()
        output = model(state_batch)
        loss = loss_fn(output, target_batch)
        loss.backward()
        optimizer.step()

        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

    # Convert the model to TorchScript for fast inference.
    scripted_model = torch.jit.script(model)
    scripted_model.save("rl_scaling_model.pt")
    print("Saved scripted model to rl_scaling_model.pt")


if __name__ == "__main__":
    train_dummy_model()

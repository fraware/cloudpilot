import logging

import torch
import torch.nn as nn
import torch.optim as optim

logger = logging.getLogger(__name__)


class DQN(nn.Module):
    def __init__(self, state_dim: int = 5, action_dim: int = 3) -> None:
        super().__init__()
        self.fc1 = nn.Linear(state_dim, 32)
        self.fc2 = nn.Linear(32, 32)
        self.fc3 = nn.Linear(32, action_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)


def train_dummy_model() -> None:
    model = DQN()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()

    for epoch in range(100):
        state_batch = torch.rand((32, 5))
        target_batch = torch.rand((32, 3))
        optimizer.zero_grad()
        output = model(state_batch)
        loss = loss_fn(output, target_batch)
        loss.backward()
        optimizer.step()
        if epoch % 10 == 0:
            logger.info("Epoch %s, Loss: %.4f", epoch, loss.item())

    scripted_model = torch.jit.script(model)
    scripted_model.save("rl_scaling_model.pt")
    logger.info("Saved scripted model to rl_scaling_model.pt")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_dummy_model()

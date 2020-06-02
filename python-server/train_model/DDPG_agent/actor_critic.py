"""
@File   :actor_critic.py
@Author :JohsuaWu1997
@Date   :2020/1/30
"""
import torch

cuda = torch.device('cuda')


def hard_copy(target, source):
    for weight1, weight2 in zip(target, source):
        weight1.data = weight2.data.clone()


def soft_copy(target, source, w=0.01):
    for weight1, weight2 in zip(target, source):
        weight1.data = torch.add(
            weight1.data, torch.add(
                weight2.data, weight1.data, alpha=-1
            ), alpha=w)


class ActorNet(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(ActorNet, self).__init__()
        self.nn = torch.nn.Sequential(
            torch.nn.Linear(input_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, output_dim),
            torch.nn.Softmax(dim=1)
        )

    def forward(self, x):
        out = self.nn(x)
        return out


class CriticNet(torch.nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super(CriticNet, self).__init__()

        self.nn = torch.nn.Sequential(
            torch.nn.Linear(input_dim + output_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_dim, 1)
        )

    def forward(self, a, x):
        ax = torch.cat((a, x), 1)
        out = self.nn(ax)
        return out


class Actor:
    def __init__(self, time_dim, state_dim, action_dim, hidden_dim):
        self.actor = ActorNet(state_dim * (time_dim + 1), hidden_dim, action_dim).to(cuda)
        self.target = ActorNet(state_dim * (time_dim + 1), hidden_dim, action_dim).to(cuda)
        self.actor_weights = [params for params in self.actor.parameters()]
        self.target_weights = [params for params in self.target.parameters()]
        self.optimizer = torch.optim.Adam(self.actor.parameters())
        self.loss = torch.tensor([0], device=cuda)
        hard_copy(self.target_weights, self.actor_weights)

    def train(self, actor_loss):
        for _ in range(1):
            self.loss = actor_loss
            self.optimizer.zero_grad()
            self.loss.backward()
            self.optimizer.step()

    def actor_action(self, state):
        self.actor.zero_grad()
        return self.actor(state)

    def target_action(self, state):
        self.target.zero_grad()
        return self.target(state)

    def update_target(self):
        soft_copy(self.target_weights, self.actor_weights)


class Critic:
    def __init__(self, time_dim, state_dim, action_dim, hidden_dim):
        self.critic = CriticNet(state_dim * (time_dim + 1), hidden_dim, action_dim).to(cuda)
        self.target = CriticNet(state_dim * (time_dim + 1), hidden_dim, action_dim).to(cuda)
        self.critic_weights = [params for params in self.critic.parameters()]
        self.target_weights = [params for params in self.target.parameters()]
        self.optimizer = torch.optim.Adam(self.critic.parameters())
        self.loss = torch.tensor(0, device=cuda)
        hard_copy(self.target_weights, self.critic_weights)

    def train(self, y_batch, action_batch, state_batch):
        criterion = torch.nn.MSELoss()
        for _ in range(1):
            y_pred = self.critic(action_batch, state_batch)
            self.loss = criterion(y_pred, y_batch)
            self.optimizer.zero_grad()
            self.loss.backward()
            self.optimizer.step()

    def critic_loss(self, next_action_batch, next_state_batch):
        self.critic.zero_grad()
        return torch.nn.functional.softplus(-self.critic(next_action_batch, next_state_batch).mean())

    def target_q(self, next_action_batch, next_state_batch):
        self.target.zero_grad()
        return self.target(next_action_batch, next_state_batch).view(-1)

    def update_target(self):
        soft_copy(self.target_weights, self.critic_weights)

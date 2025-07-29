"""Algorithm name: PPO.

Paper Name: Proximal Policy Optimization Algorithms
Paper link: https://arxiv.org/abs/1707.06347
Taxonomy: On policy > Policy Based > Continuous action space
"""

import os
import numpy as np
import torch
from reinforceui_studio.RL_helpers.mlflow_logger import MLflowLogger
from reinforceui_studio.RL_memory.memory_buffer import MemoryBuffer
from reinforceui_studio.RL_algorithms.PPO.networks import Actor, Critic
from reinforceui_studio.RL_helpers.mlflow_wrappers import ActorMLflowWrapperPPO
import torch.nn.functional as functional
from torch.distributions import Normal


class PPO:
    def __init__(
        self,
        observation_size: int,
        action_num: int,
        hyperparameters: dict,
        mlflow_logger: MLflowLogger = None,
    ) -> None:
        """Initialize PPO agent.

        Args:
            observation_size: Dimension of the state space
            action_num: Dimension of the action space
            hyperparameters: Dictionary containing algorithm parameters:
                gamma: Discount factor
                actor_lr: Learning rate for the actor network
                critic_lr: Learning rate for the critic network
                eps_clip: Clipping parameter for PPO
                updates_per_iteration: Number of updates per iteration
            mlflow_logger: Logger for MLflow integration, if None, no logging will be done
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor_net = Actor(observation_size, action_num).to(self.device)
        self.critic_net = Critic(observation_size).to(self.device)

        self.gamma = float(hyperparameters.get("gamma"))
        self.actor_lr = float(hyperparameters.get("actor_lr"))
        self.critic_lr = float(hyperparameters.get("critic_lr"))
        self.eps_clip = float(hyperparameters.get("eps_clip"))
        self.updates_per_iteration = int(hyperparameters.get("updates_per_iteration"))

        self.actor_net_optimiser = torch.optim.Adam(
            self.actor_net.parameters(), lr=self.actor_lr
        )
        self.critic_net_optimiser = torch.optim.Adam(
            self.critic_net.parameters(), lr=self.critic_lr
        )

        self.mlflow_logger = mlflow_logger
        self.observation_size = observation_size
        self.action_num = action_num

    def select_action_from_policy(
        self, state: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Select action from policy.

        Args:
            state: Current state of the environment

        Returns:
            tuple[np.ndarray, np.ndarray]: Tuple containing the action and log probability
        """
        self.actor_net.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).to(self.device).unsqueeze(0)
            mean, std = self.actor_net(state_tensor)
            dist = Normal(mean, std)
            action = dist.sample()
            log_prob = dist.log_prob(action).sum(dim=-1)
            action = action.cpu().data.numpy().flatten()
            log_prob = log_prob.cpu().numpy()
        self.actor_net.train()
        return action, log_prob

    def _evaluate_policy(
        self, state: torch.Tensor, action: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Evaluate policy.

        Args:
            state: Current state of the environment
            action: Action taken by the agent

        Returns:
            tuple[torch.Tensor, torch.Tensor]: Tuple containing the value and log probability
        """
        v = self.critic_net(state).squeeze()
        mean, std = self.actor_net(state)
        dist = Normal(mean, std)
        log_prob = dist.log_prob(action).sum(dim=-1)
        return v, log_prob

    def _calculate_rewards_to_go(
        self, batch_rewards: torch.Tensor, batch_dones: torch.Tensor
    ) -> torch.Tensor:
        """Calculate rewards to go.

        Args:
            batch_rewards: Batch of rewards
            batch_dones: Batch of terminal states

        Returns:
            torch.Tensor: Rewards to go
        """
        rtgs = torch.zeros_like(batch_rewards)
        discounted_reward = 0.0
        for i in reversed(range(len(batch_rewards))):
            discounted_reward = (
                batch_rewards[i] + self.gamma * (1 - batch_dones[i]) * discounted_reward
            )
            rtgs[i] = discounted_reward
        return rtgs.to(self.device)

    def train_policy(self, memory: MemoryBuffer, step: int = None) -> None:
        """Train policy using experiences from memory buffer.

        Note: PPO use the whole memory buffer to train the policy then flushes it.

        Args:
            memory: Memory buffer containing experiences
            step: Current training step, used for logging purposes
        """
        experiences = memory.return_flushed_memory()
        states, actions, rewards, _, dones, log_probs = experiences

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        log_probs = torch.FloatTensor(log_probs).to(self.device)

        rtgs = self._calculate_rewards_to_go(rewards, dones)
        v, _ = self._evaluate_policy(states, actions)

        advantages = rtgs.detach() - v.detach()
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-10)

        for _ in range(self.updates_per_iteration):
            current_v, curr_log_probs = self._evaluate_policy(states, actions)

            # Calculate ratios
            ratios = torch.exp(curr_log_probs - log_probs.detach())

            # Finding Surrogate Loss
            surrogate_loss_one = ratios * (advantages.detach())
            surrogate_loss_two = (
                torch.clamp(ratios, 1 - self.eps_clip, 1 + self.eps_clip) * advantages
            )

            actor_loss = -torch.min(surrogate_loss_one, surrogate_loss_two).mean()
            critic_loss = functional.mse_loss(current_v, (rtgs.detach()))

            self.actor_net_optimiser.zero_grad()
            actor_loss.backward()
            self.actor_net_optimiser.step()

            self.critic_net_optimiser.zero_grad()
            critic_loss.backward()
            self.critic_net_optimiser.step()

            if self.mlflow_logger is not None:
                self.mlflow_logger.log_metric(
                    "Actor loss", actor_loss.item(), step=step
                )
                self.mlflow_logger.log_metric(
                    "Critic loss", critic_loss.item(), step=step
                )

    def save_models(
        self, filename: str, filepath: str, checkpoint: bool = True
    ) -> None:
        """Save actor and critic networks to files.

        Args:
            filename: Base name for the saved model files
            filepath: Directory path where models will be saved
            checkpoint: If True, save models as checkpoints. If False, save models for MLflow logging.
        """
        dir_exists = os.path.exists(filepath)
        if not dir_exists:
            os.makedirs(filepath)

        torch.save(self.actor_net.state_dict(), f"{filepath}/{filename}_actor.pht")
        torch.save(self.critic_net.state_dict(), f"{filepath}/{filename}_critic.pht")

        # Log model as MLflow models only at the end of training (checkpoint=False)
        if (
            self.mlflow_logger is not None
            and self.mlflow_logger.use_mlflow
            and not checkpoint
        ):
            self.mlflow_logger.log_artifact(f"{filepath}/{filename}_actor.pht")
            self.mlflow_logger.log_artifact(f"{filepath}/{filename}_critic.pht")

            # For actor
            input_example = np.zeros((1, self.observation_size), dtype=np.float32)
            model_input = torch.from_numpy(input_example)
            actor_mlflow = ActorMLflowWrapperPPO(self.actor_net, self.observation_size)
            self.mlflow_logger.log_model(
                model=actor_mlflow,
                model_type="pytorch",
                model_name="actor",
                input_example=input_example,
                model_input=model_input,
                device=self.device,
            )

            # For critic (use wrapper for MLflow)
            input_example = np.zeros((1, self.observation_size), dtype=np.float32)
            model_input = torch.from_numpy(input_example)
            self.mlflow_logger.log_model(
                model=self.critic_net,
                model_type="pytorch",
                model_name="critic",
                input_example=input_example,
                model_input=model_input,
                device=self.device,
            )

    def load_models(self, filename: str, filepath: str) -> None:
        """Load models previously saved for this algorithm.

        Args:
            filename: Filename of the models, without extension
            filepath: Path to the saved models, usually located in user's home directory
        """
        self.actor_net.load_state_dict(
            torch.load(
                f"{filepath}/{filename}_actor.pht",
                map_location=self.device,
                weights_only=True,
            )
        )
        self.actor_net.eval()
        self.critic_net.load_state_dict(
            torch.load(
                f"{filepath}/{filename}_critic.pht",
                map_location=self.device,
                weights_only=True,
            )
        )
        self.critic_net.eval()

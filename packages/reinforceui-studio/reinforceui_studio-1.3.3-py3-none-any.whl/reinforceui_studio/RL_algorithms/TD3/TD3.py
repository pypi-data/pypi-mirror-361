"""Algorithm name: TD3.

Paper Name: Addressing Function Approximation Error in Actor-Critic Methods
Paper link: https://arxiv.org/abs/1802.09477
Taxonomy: Off policy > Actor-Critic > Continuous action space
"""

import copy
import os
import numpy as np
from reinforceui_studio.RL_memory.memory_buffer import MemoryBuffer
from reinforceui_studio.RL_algorithms.TD3.networks import Actor, Critic
from reinforceui_studio.RL_helpers.mlflow_logger import MLflowLogger
from reinforceui_studio.RL_helpers.mlflow_wrappers import (
    CriticMLflowWrapperTD3_SAC,
)

import torch
import torch.nn.functional as functional


class TD3:
    def __init__(
        self,
        observation_size: int,
        action_num: int,
        hyperparameters: dict,
        mlflow_logger: MLflowLogger = None,
    ) -> None:
        """Initialize the TD3 agent.

        Args:
            observation_size: Dimension of the state space
            action_num: Dimension of the action space
            hyperparameters: Dictionary containing algorithm parameters:
                - gamma: Discount factor
                - tau: Soft update parameter
                - actor_lr: Learning rate for actor network
                - critic_lr: Learning rate for critic networks
            mlflow_logger: Logger for MLflow integration, if None, no logging will be done
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor_net = Actor(observation_size, action_num).to(self.device)
        self.critic_net = Critic(observation_size, action_num).to(self.device)
        self.target_actor_net = copy.deepcopy(self.actor_net).to(self.device)
        self.target_critic_net = copy.deepcopy(self.critic_net).to(self.device)

        self.gamma = float(hyperparameters.get("gamma"))
        self.tau = float(hyperparameters.get("tau"))
        self.actor_lr = float(hyperparameters.get("actor_lr"))
        self.critic_lr = float(hyperparameters.get("critic_lr"))

        self.noise_clip = 0.5
        self.policy_noise = 0.2
        self.learn_counter = 0
        self.policy_update_freq = 2

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
        self,
        state: np.ndarray,
        evaluation: bool = False,
        noise_scale: float = 0.1,
    ) -> np.ndarray:
        """Select an action from the policy network.

        Args:
            state: Current state of the environment
            evaluation: When False, no exploration noise is added
            noise_scale: Scale of the exploration noise

        Returns:
            np.ndarray: Action array to be applied to the environment.
        """
        self.actor_net.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).to(self.device)
            state_tensor = state_tensor.unsqueeze(0)
            action = self.actor_net(state_tensor)
            action = action.cpu().detach().numpy().flatten()
            if not evaluation:
                noise = np.random.normal(0, scale=noise_scale, size=self.action_num)
                action = action + noise
                action = np.clip(action, -1, 1)
        self.actor_net.train()
        return action

    def _update_critic(
        self,
        states: torch.Tensor,
        actions: torch.Tensor,
        rewards: torch.Tensor,
        next_states: torch.Tensor,
        dones: torch.Tensor,
        step: int = None,
    ) -> tuple[float, float, float]:

        with torch.no_grad():
            next_actions = self.target_actor_net(next_states)
            target_noise = self.policy_noise * torch.randn_like(next_actions)
            target_noise = torch.clamp(target_noise, -self.noise_clip, self.noise_clip)
            next_actions = next_actions + target_noise
            next_actions = torch.clamp(next_actions, min=-1, max=1)

            target_q_values_one, target_q_values_two = self.target_critic_net(
                next_states, next_actions
            )
            target_q_values = torch.minimum(target_q_values_one, target_q_values_two)
            q_target = rewards + self.gamma * (1 - dones) * target_q_values

        q_values_one, q_values_two = self.critic_net(states, actions)

        critic_loss_one = functional.mse_loss(q_values_one, q_target)
        critic_loss_two = functional.mse_loss(q_values_two, q_target)
        critic_loss_total = critic_loss_one + critic_loss_two

        self.critic_net_optimiser.zero_grad()
        critic_loss_total.backward()
        self.critic_net_optimiser.step()
        # Log critic losses
        if self.mlflow_logger is not None:
            log_step = step if step is not None else self.learn_counter
            self.mlflow_logger.log_metrics(
                {
                    "Critic loss 1": critic_loss_one.item(),
                    "Critic loss 2": critic_loss_two.item(),
                    "Critic loss total": critic_loss_total.item(),
                },
                step=log_step,
            )
        return (
            critic_loss_one.item(),
            critic_loss_two.item(),
            critic_loss_total.item(),
        )

    def _update_actor(
        self,
        states: torch.Tensor,
        step: int = None,
    ) -> float:
        actor_q_values, _ = self.critic_net(states, self.actor_net(states))
        actor_loss = -actor_q_values.mean()
        self.actor_net_optimiser.zero_grad()
        actor_loss.backward()
        self.actor_net_optimiser.step()
        # Log actor loss
        if self.mlflow_logger is not None:
            log_step = step if step is not None else self.learn_counter
            self.mlflow_logger.log_metric(
                "Actor loss", actor_loss.item(), step=log_step
            )
        return actor_loss.item()

    def train_policy(
        self, memory: MemoryBuffer, batch_size: int, step: int = None
    ) -> None:
        """Train actor and critic networks using experiences from memory.

        Args:
            memory: Replay buffer containing experiences
            batch_size: Number of experiences to sample
            step: Global timestep for logging (optional)
        """
        self.learn_counter += 1

        experiences = memory.sample_experience(batch_size)
        states, actions, rewards, next_states, dones = experiences

        # Convert into tensor
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.FloatTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Reshape to batch_size
        rewards = rewards.reshape(batch_size, 1)
        dones = dones.reshape(batch_size, 1)

        # Update the Critic
        self._update_critic(states, actions, rewards, next_states, dones, step=step)

        if self.learn_counter % self.policy_update_freq == 0:
            # Update Actor
            self._update_actor(states, step=step)

            # Update target network params
            for param, target_param in zip(
                self.critic_net.parameters(),
                self.target_critic_net.parameters(),
            ):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data
                )

            for param, target_param in zip(
                self.actor_net.parameters(), self.target_actor_net.parameters()
            ):
                target_param.data.copy_(
                    self.tau * param.data + (1 - self.tau) * target_param.data
                )

    def save_models(
        self, filename: str, filepath: str, checkpoint: bool = True
    ) -> None:
        """Save actor and critic networks to files.

        Args:
            filename: Base name for the saved model files
            filepath: Directory path where models will be saved
            checkpoint: If True, mlfow won't log the model as an artifact or model
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
            # Log as artifacts for backward compatibility
            self.mlflow_logger.log_artifact(f"{filepath}/{filename}_actor.pht")
            self.mlflow_logger.log_artifact(f"{filepath}/{filename}_critic.pht")

            # For actor
            input_example = np.zeros((1, self.observation_size), dtype=np.float32)
            model_input = torch.from_numpy(input_example)
            self.mlflow_logger.log_model(
                model=self.actor_net,
                model_type="pytorch",
                model_name="actor",
                input_example=input_example,
                model_input=model_input,
                device=self.device,
            )

            # For critic (use wrapper for MLflow)
            input_example = np.zeros(
                (1, self.observation_size + self.action_num), dtype=np.float32
            )
            model_input = torch.from_numpy(input_example)
            critic_mlflow = CriticMLflowWrapperTD3_SAC(
                self.critic_net, self.observation_size
            )
            self.mlflow_logger.log_model(
                model=critic_mlflow,
                model_type="pytorch",
                model_name="critic",
                input_example=input_example,
                model_input=model_input,
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

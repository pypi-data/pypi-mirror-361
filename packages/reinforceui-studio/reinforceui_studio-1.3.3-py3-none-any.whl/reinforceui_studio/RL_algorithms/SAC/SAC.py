"""Algorithm name: SAC (Soft Actor-Critic)

Paper Name: Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor
Paper link: https://arxiv.org/abs/1801.01290
Taxonomy: Off policy > Actor-Critic > Continuous action space
"""

import copy
import logging
import os
import numpy as np
import torch
import torch.nn.functional as functional
from reinforceui_studio.RL_memory.memory_buffer import MemoryBuffer
from reinforceui_studio.RL_algorithms.SAC.networks import Actor, Critic
from reinforceui_studio.RL_helpers.mlflow_logger import MLflowLogger
from reinforceui_studio.RL_helpers.mlflow_wrappers import (
    CriticMLflowWrapperTD3_SAC,
    ActorMLflowWrapperSAC,
)


class SAC:
    def __init__(
        self,
        observation_size: int,
        action_num: int,
        hyperparameters: dict,
        mlflow_logger: MLflowLogger = None,
    ) -> None:
        """Initialize the SAC agent.

        Args:
            observation_size: Dimension of the state space
            action_num: Dimension of the action space
            hyperparameters: Dictionary containing algorithm parameters:
                gamma: Discount factor
                tau: Soft update parameter
                actor_lr: Learning rate for the actor network
                critic_lr: Learning rate for the critic network
                alpha_lr: Learning rate for the temperature parameter
            mlflow_logger: Logger for MLflow integration, if None, no logging will be done

        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.actor_net = Actor(observation_size, action_num).to(self.device)
        self.critic_net = Critic(observation_size, action_num).to(self.device)
        self.target_critic_net = copy.deepcopy(self.critic_net).to(self.device)

        self.gamma = float(hyperparameters.get("gamma"))
        self.tau = float(hyperparameters.get("tau"))
        self.actor_lr = float(hyperparameters.get("actor_lr"))
        self.critic_lr = float(hyperparameters.get("critic_lr"))
        self.alpha_lr = float(hyperparameters.get("alpha_lr"))

        self.reward_scale = 1.0
        self.learn_counter = 0
        self.policy_update_freq = 1

        self.target_entropy = -action_num

        init_temperature = 1.0
        self.log_alpha = torch.tensor(np.log(init_temperature)).to(self.device)
        self.log_alpha.requires_grad = True
        self.log_alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=self.alpha_lr)

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
        noise_scale: float = 0,
    ) -> np.ndarray:
        """Select action from policy.

        Args:
            state: Input state
            evaluation: When True, select mu as action
            noise_scale: no use in this algorithm

        Returns:
            Action array to be applied to the environment
        """
        self.actor_net.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state)
            state_tensor = state_tensor.unsqueeze(0).to(self.device)
            if evaluation:
                (_, _, action) = self.actor_net(state_tensor)
            else:
                (action, _, _) = self.actor_net(state_tensor)
            action = action.cpu().data.numpy().flatten()
        self.actor_net.train()
        return action

    @property
    def alpha(self) -> torch.Tensor:
        """Returns the exponential of self.log_alpha"""
        return self.log_alpha.exp()

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
            next_actions, next_log_pi, _ = self.actor_net(next_states)
            target_q_values_one, target_q_values_two = self.target_critic_net(
                next_states, next_actions
            )
            target_q_values = (
                torch.minimum(target_q_values_one, target_q_values_two)
                - self.alpha * next_log_pi
            )

            q_target = (
                rewards * self.reward_scale + self.gamma * (1 - dones) * target_q_values
            )

        q_values_one, q_values_two = self.critic_net(states, actions)
        critic_loss_one = functional.mse_loss(q_values_one, q_target)
        critic_loss_two = functional.mse_loss(q_values_two, q_target)
        critic_loss_total = critic_loss_one + critic_loss_two
        self.critic_net_optimiser.zero_grad()
        critic_loss_total.backward()
        self.critic_net_optimiser.step()

        # MLflow logging for critic losses
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

    def _update_actor_alpha(
        self, states: torch.Tensor, step: int = None
    ) -> tuple[float, float]:
        pi, log_pi, _ = self.actor_net(states)
        qf1_pi, qf2_pi = self.critic_net(states, pi)
        min_qf_pi = torch.minimum(qf1_pi, qf2_pi)

        actor_loss = ((self.alpha * log_pi) - min_qf_pi).mean()

        self.actor_net_optimiser.zero_grad()
        actor_loss.backward()
        self.actor_net_optimiser.step()

        # update the temperature (alpha)
        alpha_loss = -(self.log_alpha * (log_pi + self.target_entropy).detach()).mean()

        self.log_alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self.log_alpha_optimizer.step()

        # MLflow logging for actor and alpha loss
        if self.mlflow_logger is not None:
            log_step = step if step is not None else self.learn_counter
            self.mlflow_logger.log_metric(
                "Actor loss", actor_loss.item(), step=log_step
            )
            self.mlflow_logger.log_metric(
                "Alpha loss", alpha_loss.item(), step=log_step
            )

        return actor_loss.item(), alpha_loss.item()

    def train_policy(
        self, memory: MemoryBuffer, batch_size: int, step: int = None
    ) -> None:
        """Train actor and critic networks using experiences from memory.

        Args:
            memory: Replay buffer containing experiences
            batch_size: Number of experiences to sample
            step: Current training step, used for logging purposes
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

        rewards = rewards.reshape(batch_size, 1)
        dones = dones.reshape(batch_size, 1)

        # Update the Critic
        self._update_critic(states, actions, rewards, next_states, dones, step=step)

        # Update the Actor and Alpha
        self._update_actor_alpha(states, step=step)

        if self.learn_counter % self.policy_update_freq == 0:
            for param, target_param in zip(
                self.critic_net.parameters(),
                self.target_critic_net.parameters(),
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
            actor_mlflow = ActorMLflowWrapperSAC(self.actor_net, self.observation_size)
            self.mlflow_logger.log_model(
                model=actor_mlflow,
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
        self.critic_net.load_state_dict(
            torch.load(
                f"{filepath}/{filename}_critic.pht",
                map_location=self.device,
                weights_only=True,
            )
        )
        logging.info("models has been loaded...")

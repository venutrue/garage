"""
Run PyTorch Soft Actor Critic on HalfCheetahEnv with the "Twin" architecture
from TD3: https://arxiv.org/pdf/1802.09477.pdf
"""
import numpy as np

from garage.experiment import run_experiment
import garage.torch.algos.pytorch_util as ptu
from garage.torch.envs.wrappers import NormalizedBoxEnv
from garage.torch.policies import TanhGaussianPolicy
from garage.torch.algos.networks import FlattenMlp
from garage.torch.algos.sac.twin_sac import TwinSAC


def experiment(variant):
    import gym
    env = NormalizedBoxEnv(gym.make('HalfCheetah-v2'))

    obs_dim = int(np.prod(env.observation_space.shape))
    action_dim = int(np.prod(env.action_space.shape))

    net_size = variant['net_size']
    qf1 = FlattenMlp(
        hidden_sizes=[net_size, net_size],
        input_size=obs_dim + action_dim,
        output_size=1,
    )
    qf2 = FlattenMlp(
        hidden_sizes=[net_size, net_size],
        input_size=obs_dim + action_dim,
        output_size=1,
    )
    vf = FlattenMlp(
        hidden_sizes=[net_size, net_size],
        input_size=obs_dim,
        output_size=1,
    )
    policy = TanhGaussianPolicy(
        hidden_sizes=[net_size, net_size],
        obs_dim=obs_dim,
        action_dim=action_dim,
    )
    algorithm = TwinSAC(
        env=env,
        policy=policy,
        qf1=qf1,
        qf2=qf2,
        vf=vf,
        **variant['algo_params'])
    algorithm.to(ptu.device)
    algorithm.train()


def run_task(*_):
    variant = dict(
        algo_params=dict(
            num_epochs=1000,
            num_steps_per_epoch=1000,
            num_steps_per_eval=1000,
            max_path_length=1000,
            batch_size=128,
            discount=0.99,
            soft_target_tau=0.001,
            policy_lr=3E-4,
            qf_lr=3E-4,
            vf_lr=3E-4,
        ),
        net_size=300,
    )
    experiment(variant)


run_experiment(
    run_task,
    # Number of parallel workers for sampling
    n_parallel=1,
    # Only keep the snapshot parameters for the last iteration
    snapshot_mode="last",
    # Specifies the seed for the experiment. If this is not provided, a random
    # seed will be used
    seed=1,
    # plot=True,
)

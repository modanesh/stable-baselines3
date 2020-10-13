import numpy as np
import pytest

from stable_baselines3 import A2C, CMAES, DDPG, DQN, PPO, SAC, TD3, TQC
from stable_baselines3.common.noise import NormalActionNoise, OrnsteinUhlenbeckActionNoise

normal_action_noise = NormalActionNoise(np.zeros(1), 0.1 * np.ones(1))


@pytest.mark.parametrize("model_class", [TD3, DDPG])
@pytest.mark.parametrize("action_noise", [normal_action_noise, OrnsteinUhlenbeckActionNoise(np.zeros(1), 0.1 * np.ones(1))])
def test_deterministic_pg(model_class, action_noise):
    """
    Test for DDPG and variants (TD3).
    """
    model = model_class(
        "MlpPolicy",
        "Pendulum-v0",
        policy_kwargs=dict(net_arch=[64, 64]),
        learning_starts=100,
        verbose=1,
        create_eval_env=True,
        action_noise=action_noise,
    )
    model.learn(total_timesteps=1000, eval_freq=500)


@pytest.mark.parametrize("env_id", ["CartPole-v1", "Pendulum-v0"])
def test_a2c(env_id):
    model = A2C("MlpPolicy", env_id, seed=0, policy_kwargs=dict(net_arch=[16]), verbose=1, create_eval_env=True)
    model.learn(total_timesteps=1000, eval_freq=500)


@pytest.mark.parametrize("env_id", ["CartPole-v1", "Pendulum-v0"])
@pytest.mark.parametrize("clip_range_vf", [None, 0.2, -0.2])
def test_ppo(env_id, clip_range_vf):
    if clip_range_vf is not None and clip_range_vf < 0:
        # Should throw an error
        with pytest.raises(AssertionError):
            model = PPO(
                "MlpPolicy",
                env_id,
                seed=0,
                policy_kwargs=dict(net_arch=[16]),
                verbose=1,
                create_eval_env=True,
                clip_range_vf=clip_range_vf,
            )
    else:
        model = PPO(
            "MlpPolicy",
            env_id,
            seed=0,
            policy_kwargs=dict(net_arch=[16]),
            verbose=1,
            create_eval_env=True,
            clip_range_vf=clip_range_vf,
        )
        model.learn(total_timesteps=1000, eval_freq=500)


@pytest.mark.parametrize("ent_coef", ["auto", 0.01, "auto_0.01"])
def test_sac(ent_coef):
    model = SAC(
        "MlpPolicy",
        "Pendulum-v0",
        policy_kwargs=dict(net_arch=[64, 64]),
        learning_starts=100,
        verbose=1,
        create_eval_env=True,
        ent_coef=ent_coef,
        action_noise=NormalActionNoise(np.zeros(1), np.zeros(1)),
    )
    model.learn(total_timesteps=1000, eval_freq=500)


@pytest.mark.parametrize("n_critics", [1, 3])
def test_n_critics(n_critics):
    # Test SAC with different number of critics, for TD3, n_critics=1 corresponds to DDPG
    model = SAC(
        "MlpPolicy", "Pendulum-v0", policy_kwargs=dict(net_arch=[64, 64], n_critics=n_critics), learning_starts=100, verbose=1
    )
    model.learn(total_timesteps=500)


# "CartPole-v1"
@pytest.mark.parametrize("env_id", ["MountainCarContinuous-v0"])
def test_cmaes(env_id):
    if CMAES is None:
        return
    model = CMAES("MlpPolicy", env_id, seed=0, policy_kwargs=dict(net_arch=[64]), verbose=1, create_eval_env=True)
    model.learn(total_timesteps=50000, eval_freq=10000)


# def test_crr(tmp_path):
#     model = TQC(
#         "MlpPolicy",
#         "Pendulum-v0",
#         policy_kwargs=dict(net_arch=[64, 64]),
#         learning_starts=0,
#         verbose=1,
#         create_eval_env=True,
#         action_noise=None,
#         use_sde=False,
#     )
#
#     # print(evaluate_policy(model, model.get_env()))
#     # model.learn(total_timesteps=8000, eval_freq=1000)
#     # model.save_replay_buffer('/tmp/replay_buffer_expert.pkl')
#     model.load_replay_buffer("/tmp/replay_buffer_expert.pkl")
#     print(evaluate_policy(model, model.get_env()))
#     for _ in range(15):
#         # Pretrain with Critic Regularized Regression
#         model.pretrain(gradient_steps=1000, batch_size=512, n_action_samples=1, strategy="exp", reduce="mean")
#         # Normal off-policy training
#         # model.train(gradient_steps=1000, batch_size=512)
#         print(evaluate_policy(model, model.get_env()))


def test_dqn():
    model = DQN(
        "MlpPolicy",
        "CartPole-v1",
        policy_kwargs=dict(net_arch=[64, 64]),
        learning_starts=100,
        buffer_size=500,
        learning_rate=3e-4,
        verbose=1,
        create_eval_env=True,
    )
    model.learn(total_timesteps=500, eval_freq=250)

import gym
import torch
from torch.backends import cudnn

import hkenv
import models
import trainer
import buffer

DEVICE = 'cuda'
cudnn.benchmark = True


def get_model(env: gym.Env, n_frames: int):
    c, *shape = env.observation_space.shape
    m = models.SimpleExtractor(shape, n_frames * c)
    m = models.DuelingMLP(m, env.action_space.n, noisy=True)

    m = m.to(DEVICE)

    # modify below path to the weight file you have
    # tl = torch.load('saved/1673754862HornetPER/bestmodel.pt')
    # tl = torch.load('saved/1702297388HornetV2/bestonline.pt')
    tl = torch.load('saved/1702722179Hornet/besttrainonline.pt')

    # print(tl.values())
    # for k, v in m.named_parameters():
    #     print(k, v.shape)
    # for k, v in tl.items():
    #     print(k, v.shape)
    missing, unexpected = m.load_state_dict(tl, strict=False)

    print(missing, unexpected)
    return m


def evaluate(dqn):
    for _ in range(5):
        rew = dqn.evaluate()
        print("rewards: %f" % rew)


def main():
    n_frames = 4
    env = hkenv.HKEnv((160, 160), rgb=False, gap=0.165, w1=1, w2=1, w3=0)
    # env = hkenv.HKEnv((192, 192), rgb=False, gap=0.165, w1=1, w2=1, w3=0)
    # env = hkenv.HKEnvV2((192, 192), rgb=False, gap=0.17, w1=0.8, w2=0.5, w3=-8e-5)
    m = get_model(env, n_frames)
    replay_buffer = buffer.MultistepBuffer(100000, n=10, gamma=0.99)
    dqn = trainer.Trainer(env=env, replay_buffer=replay_buffer,
                          n_frames=n_frames, gamma=0.99, eps=0.,
                          eps_func=(lambda val, step: 0.),
                          target_steps=6000,
                          learn_freq=1,
                          model=m,
                          lr=9e-5,
                          lr_decay=False,
                          criterion=torch.nn.MSELoss(),
                          batch_size=32,
                          device=DEVICE,
                          is_double=True,
                          drq=True,
                          svea=False,
                          reset=0,
                          no_save=True)
    evaluate(dqn)


if __name__ == '__main__':
    main()

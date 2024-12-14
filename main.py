import gym_cutting_stock
import gymnasium as gym
from policy import GreedyPolicy, RandomPolicy
from student_submissions.s2210xxx.policy_2312593_2312776_2252405_2312701_2213674 import Policy_2312593_2312776_2252405_2312701_2213674

# Create the environment
env = gym.make(
    "gym_cutting_stock/CuttingStock-v0",
    render_mode="human",  # Comment this line to disable rendering
)
NUM_EPISODES = 100

if __name__ == "__main__":

    observation, info = env.reset(seed=31)
    print(info)

    policy_1 = Policy_2312593_2312776_2252405_2312701_2213674(policy_id=1)
    policy_2 = Policy_2312593_2312776_2252405_2312701_2213674(policy_id=2)
    policy_3 = Policy_2312593_2312776_2252405_2312701_2213674(policy_id=3)

    while(True):
        action = policy_1.get_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            policy_1.evaluate()
            observation, info = env.reset()
            input("Enter de tiep tuc")
            break

    while(True):
        action = policy_2.get_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            policy_2.evaluate()
            observation, info = env.reset()
            input("Enter de tiep tuc")
            break

    while(True):
        action = policy_3.get_action(observation, info)
        observation, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            policy_3.evaluate()
            observation, info = env.reset()
            input("Enter de tiep tuc")
            break

env.close()
import gym_cutting_stock
import gymnasium as gym
import numpy as np
from policy import GreedyPolicy, RandomPolicy
from student_submissions.s2210xxx.policy2312776 import Policy2312776

# Create the environment
env = gym.make(
    "gym_cutting_stock/CuttingStock-v0",
    render_mode="human",  # Comment this line to disable rendering
)
NUM_EPISODES = 100

if __name__ == "__main__":
    # Reset the environment
    # observation, info = env.reset(seed=42)
    
    # # Test GreedyPolicy
    # gd_policy = GreedyPolicy()
    # ep = 0
    # while ep < NUM_EPISODES:
    #     action = gd_policy.get_action(observation, info)
    #     observation, reward, terminated, truncated, info = env.step(action)

    #     if terminated or truncated:
    #         observation, info = env.reset(seed=ep)
    #         print(info)
    #         ep += 1

    # Reset the environment
    # observation, info = env.reset(seed=42)

    # # Test RandomPolicy
    # rd_policy = RandomPolicy()
    # ep = 0
    # while ep < NUM_EPISODES:
    #     action = rd_policy.get_action(observation, info)
    #     observation, reward, terminated, truncated, info = env.step(action)

    #     if terminated or truncated:
    #         observation, info = env.reset(seed=ep)
    #         print(info)
    #         ep += 1

    # Uncomment the following code to test your policy
    # Reset the environment
    policy = Policy2312776()

    # custom_test, minh tu cho test case de xu ly
    # info = []
    # observation = {
    #     "products": [
    #     {"size": np.array([2, 1]), "quantity": 15},
    #     {"size": np.array([4, 2]), "quantity": 15},
    #     {"size": np.array([5, 3]), "quantity": 6},
    #     {"size": np.array([7, 4]), "quantity": 9},
    #     {"size": np.array([8, 5]), "quantity": 6},
    #     # {"size": np.array([24, 13]), "quantity": 1},
    # ],
    #     "stocks": [
    #     np.full((24,14), -1),
    #     np.full((24,13), -1),
    #     np.full((18,10), -1),
    #     np.full((13,10), -1),
    # ],
    # }

    # amount = 0
    # for product in observation["products"]:
    #     amount += product["quantity"]
    # print(amount)

    # for _ in range(1):
    #     action = policy.get_action(observation, info)
    #     print(action)

    # policy.evaluate()

    # test cua thay, co render, chay 2 lan cho den khi cat het product
    observation, info = env.reset(seed=42)
    for _ in range(2):
        while (True):
            action = policy.get_action(observation, info)
            observation, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                policy.evaluate()
                observation, info = env.reset()
                break
            
    env.close()

import time
from stable_baselines3 import PPO
import os
import sc2env


TIME = int(time.time())
model_name = f"{TIME}"

models_dir = f"models/{model_name}"
log_dir = f"logs/{model_name}"

conf_dict = {
    "Model": "v19",
    "Machine": "Main",
    "policy": "MlpPolicy",
    "model_save_name": model_name,
}

if not os.path.exists(models_dir):
    os.makedirs(models_dir)

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

env = sc2env.Sc2Env()

model = PPO(conf_dict["policy"], env, verbose=1, tensorboard_log=log_dir)

TIMESTEPS = 10000
iters = 0
while True:
    print("On iteration", iters)
    iters += 1
    model.learn(total_timesteps=TIMESTEPS, reset_num_timesteps=False, tb_log_name="PPO")
    model.save(f"{models_dir}/{TIMESTEPS*iters}")

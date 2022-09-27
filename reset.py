import pickle

import numpy as np

import constants


def main():
    print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")
    game_map = np.zeros((224, 224, 3), dtype=np.uint8)
    observation = game_map
    data = {
        "state": game_map,
        "reward": 0,
        "action": None,
        "done": False,
    }  # empty action waiting for the next one!
    with open(constants.FILE_NAME, "wb") as f:
        pickle.dump(data, f)


main()

import os
import pickle

import numpy as np

import constants


def main():
    print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")
    # Delete the file state_rwd_action.pickle

    os.remove(constants.FILE_NAME)

    map = np.zeros((224, 224, 3), dtype=np.uint8)
    observation = map
    data = {
        "state": map,
        "reward": 0,
        "action": None,
        "done": False,
    }  # empty action waiting for the next one!

    # create the file state_rwd_action.pickle
    # with open(constants.FILE_NAME, "x") as f:
    #     f.close()

    with open(constants.FILE_NAME, "wb") as f:
        pickle.dump(data, f)


main()

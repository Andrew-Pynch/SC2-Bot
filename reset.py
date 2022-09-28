import os
import pickle
import sys

import numpy as np

import constants


def main():
    print("RESETTING ENVIRONMENT!!!!!!!!!!!!!")

    map = np.zeros((224, 224, 3), dtype=np.uint8)
    observation = map
    data = {
        "state": map,
        "reward": 0,
        "action": None,
        "done": False,
    }  # empty action waiting for the next one!

    try:
        with open(constants.FILE_NAME, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print("error", e)
        sys.exit()


main()

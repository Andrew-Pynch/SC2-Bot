import os
import sys

import constants


def main():
    try:

        # Delete the file state_rwd_action.pickle
        if os.path.exists(constants.FILE_NAME):
            os.remove(constants.FILE_NAME)
        # create the file state_rwd_action.pickle
        with open(constants.FILE_NAME, "x") as f:
            f.close()
    except Exception as e:
        print("error", e)
        sys.exit()


main()

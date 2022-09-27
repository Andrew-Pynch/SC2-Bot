import math
import os
import pickle
import random
import sys
import time
from http.client import NOT_IMPLEMENTED

import cv2
import numpy as np
from brain import brain
from rendering import rendering
from sc2 import maps  # maps method for loading maps to play in.
from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import Difficulty, Race  # difficulty for bots, race for the 1 of 3 races
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import (
    run_game,
)  # function that facilitates actually running the agents in games
from sc2.player import (  # wrapper for whether or not the agent is one of your bots, or a "computer" player
    Bot,
    Computer,
)

SAVE_REPLAY = False
TIME = int(time.time())

rendering.create_replay_screenshots_dir(TIME)


class Richard(BotAI):  # inherits from BotAI
    async def on_step(self, iteration: int):  # on step is called every game step

        map = np.zeros(
            (self.game_info.map_size[0], self.game_info.map_size[1], 3), dtype=np.uint8
        )

        # Abstracted out the rendering logic into its own module to keep the bot code clean
        rendering.render(self, map, iteration, SAVE_REPLAY, TIME)

        # Bot logic happens in this module
        brain.think(self, iteration)


def main():
    result = run_game(  # run_game is a function that runs the game.
        maps.get("AbyssalReefLE"),  # the map we are playing on
        [
            Bot(
                Race.Terran, Richard()
            ),  # runs our coded bot, protoss race, and we pass our bot object
            Computer(Race.Zerg, Difficulty.Easy),
        ],  # runs a pre-made computer agent, zerg race, with a hard difficulty.
        realtime=False,  # When set to True, the agent is limited in how long each step can take to process.
        save_replay_as=f"/home/andrew/StarCraftII/Replays/{time}.SC2Replay",
    )
    if SAVE_REPLAY:
        rendering.convert_replay_screenshots_to_video(TIME)
    # rendering.cleanup_replay_screenshots_dir(TIME)

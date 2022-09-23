import math
import pickle
import random
import sys
import time
from http.client import NOT_IMPLEMENTED

import cv2
import numpy as np
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

SAVE_REPLAY = True


class Richard(BotAI):  # inherits from BotAI
    async def on_step(self, iteration: int):  # on step is called every game step
        map = np.zeros(
            (self.game_info.map_size[0], self.game_info.map_size[1], 3), dtype=np.uint8
        )

        rendering.render(self, map)

        cv2.imshow(
            "map",
            cv2.flip(
                cv2.resize(map, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0
            ),
        )
        cv2.waitKey(1)

        # if SAVE_REPLY:
        #     cv2.imwrite(f"replays/{int(time.time())}-{iteration}.png", map)

        # reward = 0

        # try:
        #     attack_count = 0
        #     # iterate through our voidrays
        #     for voidray in self.units(UnitTypeId.VOIDRAY):
        #         # if it's attacking, add to attack count
        #         if voidray.is_attacking and voidray.target_in_range:
        #             if self.enemy_units.closer_than(
        #                 8, voidray
        #             ) or self.enemy_structures.closer_than(8, voidray):
        #                 reward += 0.015
        #                 attack_count += 1
        # except Exception as e:
        #     print("reward", e)
        #     reward = 0

        # if iteration % 100 == 0:
        #     print(
        #         f"Iter: {iteration}. RWD: {reward}. VR: {self.units(UnitTypeId.VOIDRAY).amount}"
        #     )

        # # write the file:
        # data = {
        #     "state": map,
        #     "reward": reward,
        #     "action": None,
        #     "done": False,
        # }  # empty action waiting for the next one!

        # with open("state_rwd_action.pkl", "wb") as f:
        # pickle.dump(data, f)

    async def expand(self):
        try:
            found_something = False
            if self.supply_left < 4:
                # build pylons.
                if self.already_pending(UnitTypeId.PYLON) == 0:
                    if self.can_afford(UnitTypeId.PYLON):
                        await self.build(
                            UnitTypeId.PYLON, near=random.choice(self.townhalls)
                        )
                        found_something = True

            if not found_something:

                for nexus in self.townhalls:
                    # get worker count for this nexus:
                    worker_count = len(self.workers.closer_than(10, nexus))
                    if worker_count < 22:  # 16+3+3
                        if nexus.is_idle and self.can_afford(UnitTypeId.PROBE):
                            nexus.train(UnitTypeId.PROBE)
                            found_something = True

                    # have we built enough assimilators?
                    # find vespene geysers
                    for geyser in self.vespene_geyser.closer_than(10, nexus):
                        # build assimilator if there isn't one already:
                        if not self.can_afford(UnitTypeId.ASSIMILATOR):
                            break
                        if (
                            not self.structures(UnitTypeId.ASSIMILATOR)
                            .closer_than(2.0, geyser)
                            .exists
                        ):
                            await self.build(UnitTypeId.ASSIMILATOR, geyser)
                            found_something = True

            if not found_something:
                if self.already_pending(UnitTypeId.NEXUS) == 0 and self.can_afford(
                    UnitTypeId.NEXUS
                ):
                    await self.expand_now()

        except Exception as e:
            print(e)

    async def build_stargate(self):
        try:
            # iterate thru all nexus and see if these buildings are close
            for nexus in self.townhalls:
                # is there is not a gateway close:
                if (
                    not self.structures(UnitTypeId.GATEWAY)
                    .closer_than(10, nexus)
                    .exists
                ):
                    # if we can afford it:
                    if (
                        self.can_afford(UnitTypeId.GATEWAY)
                        and self.already_pending(UnitTypeId.GATEWAY) == 0
                    ):
                        # build gateway
                        await self.build(UnitTypeId.GATEWAY, near=nexus)

                # if the is not a cybernetics core close:
                if (
                    not self.structures(UnitTypeId.CYBERNETICSCORE)
                    .closer_than(10, nexus)
                    .exists
                ):
                    # if we can afford it:
                    if (
                        self.can_afford(UnitTypeId.CYBERNETICSCORE)
                        and self.already_pending(UnitTypeId.CYBERNETICSCORE) == 0
                    ):
                        # build cybernetics core
                        await self.build(UnitTypeId.CYBERNETICSCORE, near=nexus)

                # if there is not a stargate close:
                if (
                    not self.structures(UnitTypeId.STARGATE)
                    .closer_than(10, nexus)
                    .exists
                ):
                    # if we can afford it:        elif action == 3:
                    if (
                        self.can_afford(UnitTypeId.STARGATE)
                        and self.already_pending(UnitTypeId.STARGATE) == 0
                    ):
                        # build stargate
                        await self.build(UnitTypeId.STARGATE, near=nexus)

        except Exception as e:
            print(e)

    async def build_voidray(self):
        try:
            if self.can_afford(UnitTypeId.VOIDRAY):
                for sg in self.structures(UnitTypeId.STARGATE).ready.idle:
                    if self.can_afford(UnitTypeId.VOIDRAY):
                        sg.train(UnitTypeId.VOIDRAY)

        except Exception as e:
            print(e)

    async def send_scout(self, iteration):  # are there any idle probes:
        try:
            self.last_sent
        except:
            self.last_sent = 0

        # if self.last_sent doesnt exist yet:
        if (iteration - self.last_sent) > 200:
            try:
                if self.units(UnitTypeId.PROBE).idle.exists:
                    # pick one of these randomly:
                    probe = random.choice(self.units(UnitTypeId.PROBE).idle)
                else:
                    probe = random.choice(self.units(UnitTypeId.PROBE))
                # send probe towards enemy base:
                probe.attack(self.enemy_start_locations[0])
                self.last_sent = iteration

            except Exception as e:
                pass

    async def attack(self):
        try:
            # take all void rays and attack!
            for voidray in self.units(UnitTypeId.VOIDRAY).idle:
                # if we can attack:
                if self.enemy_units.closer_than(10, voidray):
                    # attack!
                    voidray.attack(
                        random.choice(self.enemy_units.closer_than(10, voidray))
                    )
                # if we can attack:
                elif self.enemy_structures.closer_than(10, voidray):
                    # attack!
                    voidray.attack(
                        random.choice(self.enemy_structures.closer_than(10, voidray))
                    )
                # any enemy units:
                elif self.enemy_units:
                    # attack!
                    voidray.attack(random.choice(self.enemy_units))
                # any enemy structures:
                elif self.enemy_structures:
                    # attack!
                    voidray.attack(random.choice(self.enemy_structures))
                # if we can attack:
                elif self.enemy_start_locations:
                    # attack!
                    voidray.attack(self.enemy_start_locations[0])

        except Exception as e:
            print(e)

    async def voidray_flee(self):
        if self.units(UnitTypeId.VOIDRAY).amount > 0:
            for vr in self.units(UnitTypeId.VOIDRAY):
                vr.attack(self.start_location)


def main():
    result = run_game(  # run_game is a function that runs the game.
        maps.get("AbyssalReefLE"),  # the map we are playing on
        [
            Bot(
                Race.Protoss, Richard()
            ),  # runs our coded bot, protoss race, and we pass our bot object
            Computer(Race.Zerg, Difficulty.Hard),
        ],  # runs a pre-made computer agent, zerg race, with a hard difficulty.
        realtime=False,  # When set to True, the agent is limited in how long each step can take to process.
    )

    # if str(result) == "Result.Victory":
    #     rwd = 500
    # else:
    #     rwd = -500

    # with open("results.txt", "a") as f:
    #     f.write(f"{result}\n")

    # map = np.zeros((224, 224, 3), dtype=np.uint8)
    # observation = map
    # data = {
    #     "state": map,
    #     "reward": rwd,
    #     "action": None,
    #     "done": True,
    # }  # empty action waiting for the next one!
    # with open("state_rwd_action.pkl", "wb") as f:
    #     pickle.dump(data, f)

    # cv2.destroyAllWindows()
    # cv2.waitKey(1)
    # time.sleep(3)
    # sys.exit()

import math
import pickle
import random
import sys
import time
from http.client import NOT_IMPLEMENTED

import cv2
import numpy as np
from sc2 import maps  # maps method for loading maps to play in.
from sc2.bot_ai import BotAI  # parent class we inherit from
from sc2.data import (  # difficulty for bots, race for the 1 of 3 races
    Difficulty, Race)
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import \
    run_game  # function that facilitates actually running the agents in games
from sc2.player import (  # wrapper for whether or not the agent is one of your bots, or a "computer" player
    Bot, Computer)

SAVE_REPLAY = True
FILE = "state_rwd_action.pkl"

total_steps = 10000
# wtf is this shit harrison?
steps_for_pun = np.linspace(0, 1, total_steps)
step_punishment = ((np.exp(steps_for_pun**3) / 10) - 0.1) * 10


class Richard(BotAI):  # inherits from BotAI
    async def on_step(self, iteration: int):  # on step is called every game step
        print(f"iteration: {iteration}")
        # no_action = True
        # while no_action:
        #     try:
        #         with (FILE, "rb") as f:
        #             state_rwd_action = pickle.load(f)

        #             if state_rwd_action["action"] is None:
        #                 no_action = True
        #             else:
        #                 no_action = False

        #     except Exception as e:
        #         pass

        # await self.distribute_workers()  # put them idle boys BACK 👏 TO 👏 WORK

        # action = state_rwd_action["action"]
        """
        0: expand (ie: move to next spot, or build to 16 (minerals)+3 assemblers+3)
        1: build stargate (or up to one) (evenly)
        2: build voidray (evenly)
        3: send scout (evenly/random/closest to enemy?)
        4: attack (known buildings, units, then enemy base, just go in logical order.)
        5: voidray flee (back to base)
        """

        # if action == 0:
        #     self.expand()
        # elif action == 1:
        #     self.build_stargate()
        # elif action == 2:
        #     self.build_voidray()
        # elif action == 3:
        #     self.send_scout()
        # elif action == 4:
        #     self.attack()
        # elif action == 5:
        #     self.voidray_flee(iteration)

        # map = np.zeros(
        #     (self.game_info.map_size[0], sel.game_info.map_size[1], 3), dtype=np.uint8
        # )

        # self.draw_minerals(map)
        # self.draw_enemy_start_location(map)
        # self.draw_enemy_units(map)
        # self.draw_enemy_structures(map)
        # self.draw_self_structures(map)
        # self.draw_vespene_geysers(map)
        # self.draw_self_units(map)

        # cv2.imshow(
        #     "map",
        #     cv2.flip(
        #         cv2.resize(map, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0
        #     ),
        # )
        # cv2.waitKey(1)

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
            pickle.dump(data, f)

    def draw_minerals(self, map):
        for mineral in self.mineral_field:
            pos = mineral.position
            color = [175, 255, 255]  # mineral color
            fraction = mineral.mineral_contents / 1800
            if mineral.is_visible:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [
                    int(fraction * i) for i in color
                ]
            else:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [20, 75, 50]

    def draw_enemy_start_location(self, map):
        for enemy_start_location in self.enemy_start_locations:
            pos = enemy_start_location
            color = [0, 0, 255]
            map[math.ceil(pos.y)][mail.ceil(pos.y)] = color

    def draw_enemy_units(self, map):
        for enemy_unit in self.enemy_units:
            pos = enemy_unit.position
            color = [100, 0, 255]
            # get unit health fraction
            fraction = (
                enemy_unit.health / enemy_unit.health_max
                if enemy_unit.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]

    def draw_enemy_structures(self, map):
        for enemy_structure in self.enemy_structures:
            pos = enemy_structure.position
            color = [0, 100, 255]
            # get structure health fraction
            fraction = (
                enemy_structure.health / enemy_structure.health_max
                if enemy_structure.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]

    def draw_self_structures(self, map):
        for structure in self.structures:
            # If nexus
            if structure.type_id == UnitTypeId.NEXUS:
                pos = structure.position
                color = [255, 255, 175]
                # get structure health fraction
                fraction = (
                    structure.health / structure.health_max
                    if structure.health_max > 0
                    else 0.0001
                )
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [
                    int(fraction * i) for i in color
                ]
            else:
                pos = structure.position
                color = [0, 255, 175]
                # get structure health fraction
                fraction = (
                    structure.health / structure.health_max
                    if structure.health_max > 0
                    else 0.0001
                )
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [
                    int(fraction * i) for i in color
                ]

    def draw_vespene_geysers(self, map):
        # draw the vespene geysers:
        for vespene in self.vespene_geyser:
            # draw these after buildings, since assimilators go over them.
            # tried to denote some way that assimilator was on top, couldnt
            # come up with anything. Tried by positions, but the positions arent identical. ie:
            # vesp position: (50.5, 63.5)
            # bldg positions: [(64.369873046875, 58.982421875), (52.85693359375, 51.593505859375),...]
            pos = vespene.position
            c = [255, 175, 255]
            fraction = vespene.vespene_contents / 2250

            if vespene.is_visible:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]
            else:
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [50, 20, 75]

    def draw_self_units(self, map):
        # draw our units:
        for our_unit in self.units:
            # if it is a voidray:
            if our_unit.type_id == UnitTypeId.VOIDRAY:
                pos = our_unit.position
                c = [255, 75, 75]
                # get health:
                fraction = (
                    our_unit.health / our_unit.health_max
                    if our_unit.health_max > 0
                    else 0.0001
                )
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

            else:
                pos = our_unit.position
                c = [175, 255, 0]
                # get health:
                fraction = (
                    our_unit.health / our_unit.health_max
                    if our_unit.health_max > 0
                    else 0.0001
                )
                map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

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

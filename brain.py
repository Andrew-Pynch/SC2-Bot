import pickle
import random
import sys

import numpy as np
from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.upgrade_id import UpgradeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units

import constants


async def think(bot: BotAI, iteration):
    # if iteration % 50 == 0:
    #     await take_random_action(bot, iteration)
    print("we dont have an action yet ")
    no_action = True
    while no_action:
        try:
            print("we are trying to get an action")
            with open(constants.FILE_NAME, "rb") as f:
                state_rwd_action = pickle.load(f)

                if state_rwd_action["action"] is None:
                    no_action = True
                else:
                    no_action = False
        except Exception as e:
            print("error", e)
            sys.exit()

    action = state_rwd_action["action"]
    # random_action_index = random.randint(0, len(actions) - 1)
    await take_action(bot, iteration, action)

    reward = 0
    try:
        attack_count = 0
        for marine in bot.units(UnitTypeId.MARINE):
            # If the marine is attacking and is in range of an enemy unit
            if marine.is_attacking and marine.target_in_range:
                reward += 0.015
                attack_count += 1
    except Exception as e:
        print("reward", e)
        reward = 0

    if iteration % 100 == 0:
        print(
            f"Iteration: {iteration}\nRWD: {reward}\nMarines: {bot.units(UnitTypeId.MARINE).amount}"
        )

    map = np.zeros(
        (bot.game_info.map_size[0], bot.game_info.map_size[1], 3), dtype=np.uint8
    )

    # write the file
    data = {"state": map, "reward": reward, "action": None, "done": False}

    try:
        with open(constants.FILE_NAME, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print("error", e)

        sys.exit()


def get_random_cc(bot: BotAI, first=False):
    CCs: Units = bot.townhalls(UnitTypeId.COMMANDCENTER)
    if first is True:
        return CCs.first
    else:
        return CCs.random


async def take_action(bot: BotAI, iteration, action_index):
    # This is a list of all the actions we can take
    actions = {
        0: build_workers(bot),
        1: await build_supply_depots(bot),
        2: await expand(bot),
        3: await build_vespene_geyser(bot),
        4: await build_barracks(bot),
        5: await train_marine(bot),
        6: await attack(bot, iteration),
        7: await build_engineering_bay(bot),
        8: await research_attack(bot),
    }
    # Pick a random number between 0 and the length of the actions list

    if action_index == 0:
        print("building workers", iteration)
        build_workers(bot)

    if action_index == 1:
        print("building supply depots", iteration)
        await build_supply_depots(bot)

    if action_index == 2:
        print("expanding", iteration)
        await expand(bot)

    if action_index == 3:
        print("building vespene geysers", iteration)
        await build_vespene_geyser(bot)

    if action_index == 4:
        print("building barracks", iteration)
        await build_barracks(bot)

    if action_index == 5:
        print("training marines", iteration)
        await train_marine(bot)

    if action_index == 6:
        print("attacking", iteration)
        await attack(bot, iteration)

    if action_index == 7:
        print("building engineering bay", iteration)
        await build_engineering_bay(bot)

    if action_index == 8:
        print("researching attack", iteration)
        await research_attack(bot)

    # await bot.distribute_workers()


def build_workers(bot: BotAI):
    cc = get_random_cc(bot)
    if cc and bot.can_afford(UnitTypeId.SCV):
        cc.train(UnitTypeId.SCV)


async def build_supply_depots(bot: BotAI):
    cc = get_random_cc(bot, first=True)
    if bot.supply_left < 3:
        if (
            bot.can_afford(UnitTypeId.SUPPLYDEPOT)
            and bot.already_pending(UnitTypeId.SUPPLYDEPOT) < 2
        ):
            # This picks a near-random worker to build a depot at location
            # 'from command center towards game center, distance 8'
            await bot.build(
                UnitTypeId.SUPPLYDEPOT,
                near=cc.position.towards(bot.game_info.map_center, 8),
            )

            # redistribute this worker back to mining minerals or gas
            # for worker in bot.workers.idle:
            #     worker.gather(nearest_mineral_patch)


async def expand(bot: BotAI):
    if bot.can_afford(UnitTypeId.COMMANDCENTER):
        await bot.expand_now()


async def build_vespene_geyser(bot: BotAI):
    cc = get_random_cc(bot)
    if bot.can_afford(UnitTypeId.REFINERY):
        # All the vespene geysirs nearby, including ones with a refinery on top of it
        vgs = bot.vespene_geyser.closer_than(10, cc)
        for vg in vgs:
            if bot.gas_buildings.filter(lambda unit: unit.distance_to(vg) < 1):
                continue
            # Select a worker closest to the vespene geysir
            worker: Unit = bot.select_build_worker(vg)
            # Worker can be none in cases where all workers are dead
            # or 'select_build_worker' function only selects from workers which carry no minerals
            if worker is None:
                continue
            # Issue the build command to the worker, important: vg has to be a Unit, not a position
            worker.build_gas(vg)
            # Only issue one build geysir command per frame
            break


async def build_barracks(bot: BotAI):
    cc = get_random_cc(bot)
    if bot.can_afford(UnitTypeId.BARRACKS):
        await bot.build(
            UnitTypeId.BARRACKS, near=cc.position.towards(bot.game_info.map_center, 8)
        )


async def build_engineering_bay(bot: BotAI):
    cc = get_random_cc(bot)
    if bot.can_afford(UnitTypeId.ENGINEERINGBAY):
        await bot.build(
            UnitTypeId.ENGINEERINGBAY,
            near=cc.position.towards(bot.game_info.map_center, 8),
        )


async def research_attack(bot: BotAI):
    if (
        bot.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1) == 0
        and bot.structures(UnitTypeId.ENGINEERINGBAY).ready
    ):
        bot.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL1)
    elif (
        bot.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2) == 0
        and bot.structures(UnitTypeId.ENGINEERINGBAY).ready
    ):
        bot.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL2)
    elif (
        bot.already_pending_upgrade(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3) == 0
        and bot.structures(UnitTypeId.ENGINEERINGBAY).ready
    ):
        bot.research(UpgradeId.TERRANINFANTRYWEAPONSLEVEL3)


async def train_marine(bot: BotAI):
    for barracks in bot.structures(UnitTypeId.BARRACKS).idle:
        if bot.can_afford(UnitTypeId.MARINE):
            barracks.train(UnitTypeId.MARINE)


async def attack(bot: BotAI, iteration):
    target = bot.enemy_start_locations[0]
    forces = bot.units(UnitTypeId.MARINE)
    # Every 4000 frames send all army to attack the enemy starting base
    if iteration % 500 == 0:
        for unit in forces:
            unit.attack(target)
    # Every 400 frames send idle forces to attack
    else:
        for unit in forces.idle:
            unit.attack(target)

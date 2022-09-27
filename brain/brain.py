import random

from sc2 import maps
from sc2.bot_ai import BotAI
from sc2.data import Difficulty, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.main import run_game
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
from sc2.units import Units


async def think(bot: BotAI, iteration):
    if iteration % 50 == 0:
        await take_random_action(bot, iteration)


def get_random_cc(bot: BotAI, first=False):
    CCs: Units = bot.townhalls(UnitTypeId.COMMANDCENTER)
    if first is True:
        return CCs.first
    else:
        return CCs.random


async def take_random_action(bot: BotAI, iteration):
    # This is a list of all the actions we can take
    actions = {
        0: build_workers(bot),
        1: await build_supply_depots(bot),
        2: await expand(bot),
        3: await build_vespene_geyser(bot),
        4: await build_barracks(bot),
        5: await train_marine(bot),
        6: await attack(bot),
    }
    # Pick a random number between 0 and the length of the actions list
    random_action_index = random.randint(0, len(actions) - 1)
    if random_action_index == 0:
        print("building workers", iteration)
        build_workers(bot)

    if random_action_index == 1:
        print("building supply depots", iteration)
        await build_supply_depots(bot)

    if random_action_index == 2:
        print("expanding", iteration)
        await expand(bot)

    if random_action_index == 3:
        print("building vespene geysers", iteration)
        await build_vespene_geyser(bot)

    if random_action_index == 4:
        print("building barracks", iteration)
        await build_barracks(bot)


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
            for worker in bot.workers.idle:
                worker.gather(nearest_mineral_patch)


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

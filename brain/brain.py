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


def think(bot: BotAI, iteration):
    take_random_action(bot, iteration)


def get_random_cc(bot: BotAI):
    return bot.townhalls.idle.random_or(None)


def take_random_action(bot: BotAI, iteration):
    # This is a list of all the actions we can take
    actions = [
        build_workers,
        build_supply_depots,
        #    build_barracks,
    ]
    # Pick a random number between 0 and the length of the actions list
    # random_action_index = random.randint(0, len(actions) - 1)
    # if random_action_index == 0:
    #     print("building workers", iteration)
    #     build_workers(bot)

    # if random_action_index == 1:
    #     print("building supply depots", iteration)
    #     build_supply_depots(bot)


def build_workers(bot: BotAI):
    cc = get_random_cc(bot)
    if cc and bot.can_afford(UnitTypeId.SCV):
        cc.train(UnitTypeId.SCV)


async def build_supply_depots(bot: BotAI):
    cc = get_random_cc(bot)
    # This picks a near-random worker to build a depot at location
    # 'from command center towards game center, distance 8'
    await bot.build(
        UnitTypeId.SUPPLYDEPOT,
        near=cc.position.towards(bot.game_info.map_center, 8),
    )


# async def build_barracks(bot: BotAI, cc):
#     # If we can afford barracks
#     if bot.can_afford(UnitTypeId.BARRACKS):
#         # Near same command as above with the depot
#         await bot.build(
#             UnitTypeId.BARRACKS,
#             near=cc.position.towards(bot.game_info.map_center, 8),
#         )
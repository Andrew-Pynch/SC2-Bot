import math

from sc2.bot_ai import BotAI
from sc2.ids.unit_typeid import UnitTypeId

MINERAL_COLOR = [175, 255, 255]
ENEMY_LOCATION_COLOR = [0, 0, 255]
ENEMY_UNIT_COLOR = [100, 0, 255]
ENEMY_STRUCTURES_COLOR = [0, 100, 255]
SELF_STRUCTURES_COLOR = [255, 255, 175]
VESPENE_GEYSER_COLOR = [255, 175, 255]
SELF_UNITS_COLOR = [255, 75, 75]
MAIN_ATTACK_UNIT_COLOR = [175, 255, 0]


def render(bot_instance: BotAI, map):
    draw_minerals(bot_instance, map)
    draw_enemy_start_location(bot_instance, map)
    draw_enemy_units(bot_instance, map)
    draw_enemy_structures(bot_instance, map)
    draw_self_structures(bot_instance, map)
    draw_vespene_geysers(bot_instance, map)
    draw_self_units(bot_instance, map)


def render_fractional_material(map, pos, fraction, color):
    map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]


def draw_minerals(bot_instance: BotAI, map):
    for mineral in bot_instance.mineral_field:
        pos = mineral.position
        color = MINERAL_COLOR
        fraction = mineral.mineral_contents / 1800
        if mineral.is_visible:
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]
        else:
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [20, 75, 50]


def draw_enemy_start_location(bot_instance: BotAI, map):
    for enemy_start_location in bot_instance.enemy_start_locations:
        pos = enemy_start_location
        color = ENEMY_LOCATION_COLOR
        map[math.ceil(pos.y)][math.ceil(pos.y)] = color


def draw_enemy_units(bot_instance: BotAI, map):
    for enemy_unit in bot_instance.enemy_units:
        pos = enemy_unit.position
        color = ENEMY_UNIT_COLOR
        # get unit health fraction
        fraction = (
            enemy_unit.health / enemy_unit.health_max
            if enemy_unit.health_max > 0
            else 0.0001
        )
        map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]


def draw_enemy_structures(bot_instance: BotAI, map):
    for enemy_structure in bot_instance.enemy_structures:
        pos = enemy_structure.position
        color = ENEMY_STRUCTURES_COLOR
        # get structure health fraction
        fraction = (
            enemy_structure.health / enemy_structure.health_max
            if enemy_structure.health_max > 0
            else 0.0001
        )
        map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]


def draw_self_structures(bot_instance: BotAI, map):
    for structure in bot_instance.structures:
        # If nexus
        if structure.type_id == UnitTypeId.NEXUS:
            pos = structure.position
            color = SELF_STRUCTURES_COLOR
            # get structure health fraction
            fraction = (
                structure.health / structure.health_max
                if structure.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]
        else:
            pos = structure.position
            color = SELF_STRUCTURES_COLOR
            # get structure health fraction
            fraction = (
                structure.health / structure.health_max
                if structure.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in color]


def draw_vespene_geysers(bot_instance: BotAI, map):
    # draw the vespene geysers:
    for vespene in bot_instance.vespene_geyser:
        # draw these after buildings, since assimilators go over them.
        # tried to denote some way that assimilator was on top, couldnt
        # come up with anything. Tried by positions, but the positions arent identical. ie:
        # vesp position: (50.5, 63.5)
        # bldg positions: [(64.369873046875, 58.982421875), (52.85693359375, 51.593505859375),...]
        pos = vespene.position
        c = VESPENE_GEYSER_COLOR
        fraction = vespene.vespene_contents / 2250

        if vespene.is_visible:
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]
        else:
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [50, 20, 75]


def draw_self_units(bot_instance: BotAI, map):
    # draw our units:
    for our_unit in bot_instance.units:
        # if it is a voidray:
        if our_unit.type_id == UnitTypeId.VOIDRAY:
            pos = our_unit.position
            c = MAIN_ATTACK_UNIT_COLOR
            # get health:
            fraction = (
                our_unit.health / our_unit.health_max
                if our_unit.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

        else:
            pos = our_unit.position
            c = SELF_UNITS_COLOR
            # get health:
            fraction = (
                our_unit.health / our_unit.health_max
                if our_unit.health_max > 0
                else 0.0001
            )
            map[math.ceil(pos.y)][math.ceil(pos.x)] = [int(fraction * i) for i in c]

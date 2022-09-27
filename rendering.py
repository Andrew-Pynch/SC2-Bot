import math
import os
import sys
import time

import cv2
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


def render(bot_instance: BotAI, map, iteration, should_save_replay, _time):
    draw_minerals(bot_instance, map)
    draw_enemy_start_location(bot_instance, map)
    draw_enemy_units(bot_instance, map)
    draw_enemy_structures(bot_instance, map)
    draw_self_structures(bot_instance, map)
    draw_vespene_geysers(bot_instance, map)
    draw_self_units(bot_instance, map)

    cv2.imshow(
        "map",
        cv2.flip(cv2.resize(map, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST), 0),
    )
    cv2.waitKey(1)

    if should_save_replay:
        save_replay(iteration, map, _time)


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


def save_replay(iteration, map, _time):
    try:

        cv2.imwrite(
            f"/home/andrew/Github/SC2-Bot/replays/images/{_time}/{iteration}.png", map
        )
    except Exception as e:
        print("Error writing image", e)


def convert_replay_screenshots_to_video(_time):
    # This path has to exist before we try writing a video file in
    create_replay_video_dir(_time)

    images = [
        img for img in os.listdir(f"replays/images/{_time}") if img.endswith(".png")
    ]

    frame = cv2.imread(os.path.join(f"replays/images/{_time}", images[0]))
    height, width, layers = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    video = cv2.VideoWriter(
        f"replays/videos/{_time}/{_time}.avi", fourcc, 5, (width, height)
    )

    try:
        for image in images:
            video.write(cv2.imread(os.path.join(f"replays/images/{_time}", image)))
    except Exception as e:
        print("Error writing video", e)
    video.release()


def create_replay_video_dir(_time):
    try:
        parent = "/home/andrew/Github/SC2-Bot/replays/videos/"
        dir = str(_time)
        path = os.path.join(parent, dir)
        os.mkdir(path)
    except Exception as e:
        print("Error creating video dir", e)


def create_replay_screenshots_dir(_time):
    try:
        parent = "/home/andrew/Github/SC2-Bot/replays/images/"
        dir = str(_time)
        path = os.path.join(parent, dir)
        os.mkdir(path)
    except Exception as e:
        print("Error creating screenshots dir", e)


def cleanup_replay_screenshots_dir(_time):
    path = f"/home/andrew/Github/SC2-Bot/replays/images/{_time}"
    os.rmdir(path)


def end_rendering():
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    time.sleep(3)
    sys.exit()

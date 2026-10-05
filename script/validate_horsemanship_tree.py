#!/usr/bin/env python3
"""Review Horsemanship GUI geometry and optionally compare gameplay with a baseline.

Requires PyYAML. Pass the pre-change YAML using --baseline to check that only
presentation fields changed. This does not validate the live client rendering.
"""
import argparse
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'minecraft/java/plugins/FEATOHorsemanship/horsemanship.yml'
PRESENTATION = {'coords', 'icon', 'description', 'connection_line'}
LANES = {
    0: 'fleetfoot breakaway full_gallop quick_response lightning_start ride_the_wind windborne',
    3: 'long_haul relentless_pace trailwise steady_pace second_wind iron_journey endless_road',
    6: 'first_saddle rein_sense urge good_hands seasoned_rider mutual_trust one_as_one',
    9: 'steady_hands over_the_fence surefooted calm_rein fine_control sure_landing master_of_reins',
    14: 'cavalier charge mounted_marksman veteran_cavalry first_impact',
    13: 'heavy_cavalry iron_vanguard',
    15: 'light_cavalry swift_rider',
    18: 'horse_sense breeders_insight bloodline_study horse_whisperer',
}
# Model suffixes present in the four reference progression files in 1.10.3.
STANDARD_MODELS = {0, 2, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 23}
LEFT, RIGHT, UP, DOWN = (-1, 0), (1, 0), (0, -1), (0, 1)
PORTS = {
    0: {UP, DOWN}, 2: {UP, RIGHT}, 6: {UP, DOWN},
    7: {LEFT, RIGHT}, 8: {LEFT, RIGHT}, 9: {LEFT, RIGHT},
    10: {UP, DOWN}, 11: {UP, DOWN}, 12: {UP, RIGHT},
    13: {DOWN, RIGHT}, 14: {UP, LEFT}, 15: {DOWN, LEFT},
    16: {UP, RIGHT}, 17: {DOWN, RIGHT}, 18: {UP, LEFT},
    19: {DOWN, LEFT}, 21: {DOWN, RIGHT}, 23: {DOWN, LEFT},
}
ENTRANCES = {'fleetfoot', 'long_haul', 'steady_hands', 'cavalier', 'horse_sense'}


def coordinates(value):
    x, y = value.split(',')
    return int(x), int(y)


def validate(skill, baseline=None):
    errors = []
    perks = skill['perks']
    nodes = {}
    lines = {}
    for name, perk in perks.items():
        point = coordinates(perk['coords'])
        if not perk.get('hidden', False):
            if point in nodes:
                errors.append(f'node collision: {name} / {nodes[point]} at {point}')
            nodes[point] = name
            if point[0] != perk['required_lv'] // 5:
                errors.append(f'level column mismatch: {name}')
        for prerequisite in perk.get('requireperk_all', []) + perk.get('requireperk_one', []):
            if prerequisite not in perks:
                errors.append(f'unknown prerequisite: {name} -> {prerequisite}')
            elif not perk.get('hidden', False) and coordinates(perks[prerequisite]['coords'])[0] >= point[0]:
                errors.append(f'level direction reversed: {prerequisite} -> {name}')
        for line in perk.get('connection_line', {}).values():
            at = coordinates(line['position'])
            if at in lines:
                errors.append(f'line collision: {name} / {lines[at]} at {at}')
            lines[at] = name
            for state, material, base in [('locked', 'GRAY_DYE', 1172700),
                                          ('unlockable', 'ORANGE_DYE', 1172800),
                                          ('unlocked', 'LIME_DYE', 1172900)]:
                kind, model = line[state].split(':')
                if kind != material or int(model) - base not in STANDARD_MODELS:
                    errors.append(f'nonstandard connection model: {name} {state}')
            if len({int(line[state].split(':')[1]) % 100 for state in ('locked', 'unlockable', 'unlocked')}) != 1:
                errors.append(f'connection orientation differs by state: {name}')
        if len(perk['description'].split('/n')) > 6:
            errors.append(f'description exceeds six lines: {name}')
    for point in nodes.keys() & lines.keys():
        errors.append(f'line overlaps node: {lines[point]} / {nodes[point]} at {point}')
    # Walk each destination's own lines, respecting the official model ports.
    # This catches bent lines that occupy unique slots but fail to join their
    # actual prerequisites, as well as accidental joins to another branch.
    for name, perk in perks.items():
        own = {coordinates(line['position']): PORTS.get(int(line['locked'].split(':')[1]) % 100, set())
               for line in perk.get('connection_line', {}).values()}
        if not own:
            if not perk.get('hidden') and (perk.get('requireperk_all') or perk.get('requireperk_one')) and name not in ENTRANCES:
                errors.append(f'missing prerequisite connection: {name}')
            continue
        prerequisites = perk.get('requireperk_all', []) + perk.get('requireperk_one', [])
        endpoints = {coordinates(perks[p]['coords']) for p in prerequisites if p in perks}
        start = coordinates(perk['coords'])
        ports = dict(own)
        for point in endpoints | {start}:
            ports[point] = {LEFT, RIGHT, UP, DOWN}
        visited, pending = set(), [start]
        while pending:
            point = pending.pop()
            if point in visited:
                continue
            visited.add(point)
            for dx, dy in ports[point]:
                neighbor = point[0] + dx, point[1] + dy
                if neighbor in ports and (-dx, -dy) in ports[neighbor]:
                    pending.append(neighbor)
        if not endpoints <= visited or not own.keys() <= visited:
            errors.append(f'disconnected / incorrect prerequisite path: {name}')
        for point, directions in own.items():
            for dx, dy in directions:
                neighbor = point[0] + dx, point[1] + dy
                if neighbor in nodes and neighbor not in endpoints | {start}:
                    errors.append(f'line reaches unrelated node: {name} -> {nodes[neighbor]}')
                if neighbor in lines and lines[neighbor] != name:
                    other = perks[lines[neighbor]]['connection_line'].values()
                    other_line = next(line for line in other if coordinates(line['position']) == neighbor)
                    other_ports = PORTS.get(int(other_line['locked'].split(':')[1]) % 100, set())
                    if (-dx, -dy) in other_ports:
                        errors.append(f'line joins another branch: {name} / {lines[neighbor]}')
    for y, names in LANES.items():
        for name in names.split():
            if coordinates(perks[name]['coords'])[1] != y:
                errors.append(f'lane mismatch: {name}')
    for name in ('ng_plus_master', 'ng_plus_legend'):
        perk = perks[name]
        if not perk.get('hidden') or perk.get('connection_line') or coordinates(perk['coords']) != (0, 20):
            errors.append(f'NG+ must be hidden off-tree: {name}')
    if skill['starting_coordinates'] != '0,3' or not skill['navigable']:
        errors.append('initial viewport / navigation mismatch')
    if baseline:
        before = {k: v for k, v in baseline.items() if k not in {'perks', 'starting_coordinates'}}
        after = {k: v for k, v in skill.items() if k not in {'perks', 'starting_coordinates'}}
        if before != after or baseline['perks'].keys() != perks.keys():
            errors.append('skill gameplay fields / perk IDs changed')
        for name in baseline['perks'].keys() & perks.keys():
            before = {k: v for k, v in baseline['perks'][name].items() if k not in PRESENTATION}
            after = {k: v for k, v in perks[name].items() if k not in PRESENTATION}
            if before != after:
                errors.append(f'perk gameplay fields changed: {name}')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill', type=Path, default=SKILL)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    skill = yaml.safe_load(args.skill.read_text())
    baseline = yaml.safe_load(args.baseline.read_text()) if args.baseline else None
    errors = validate(skill, baseline)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(skill['perks'])} perks, lanes, coordinates, connection slots and models"
          + (', gameplay unchanged' if baseline else ''))
    return 0


if __name__ == '__main__':
    sys.exit(main())

"""Query Liquipedia API for data updates."""
import logging
import json
import time
import re
import aiohttp
import asyncio
from collections import defaultdict

import pycountry
import requests
from ruamel.yaml import YAML
import wikitextparser as wtp
from liquipedia import db

BLACKLIST = ['MMC eSports', 'The Jedi Masters']
PLAYER_BLACKLIST = ['DaRk_', 'Blade', 'simtom']

LOGGER = logging.getLogger(__name__)


def strip_leading_double_space(stream):
    if stream.startswith("  "):
        stream = stream[2:]
    return stream.replace("\n  ", "\n")


MANUAL = {
    #'CZ': {'Skull'},
    #'Hot Young Masters': {'Yasin'},
    #'One Punch': {'fatman'},
    #'Dark Empire': {'Xhing'},
    #'Clown Legion': {'Blackheart'}
}

def fmt(s):
    return s.lower().replace('_', '').replace(' ', '')


async def main():
    logging.basicConfig(level=logging.INFO)

    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True
    with open('data/players.yaml', 'r') as handle:
        player_data = yaml.load(handle)
    with open('data/teams.json', 'r') as handle:
        team_data = json.loads(handle.read())
    by_id = {}
    for t in team_data:
        by_id[t['id']] = t['name'].replace(" (team)", "")

    names = set()
    result_data = defaultdict(set)
    for p in player_data:
        names.add(p['name'].lower().replace('_', '').replace(' ', ''))
        if 'liquipedia' in p:
            names.add(p['liquipedia'].lower().replace('_', '').replace(' ', ''))
        if 'aka' in p:
            names |= {a.lower().replace('_', '').replace(' ', '') for a in p['aka']}
    LOGGER.info("starting data update")
    seen = set()
    for x, y in MANUAL.items():
        seen |= y
        result_data[x] |= y
    async with aiohttp.ClientSession() as session:
        result_data = await db.meta_teams(session)

    td = []
    id = 1
    p2t = {}
    player_lp_found = set()
    for pp in player_data:
        if 'team' in pp:
            del pp['team']
    for x, y in result_data.items():
        if x in BLACKLIST:
            continue
        tm = {f for f in y if fmt(f) in names and f not in PLAYER_BLACKLIST}
        if not tm:
            continue
        players = set()
        pns = set()
        for p in tm:
            ptrans = fmt(p)
            for pp in player_data:
                lp_match = 'liquipedia' in pp and ptrans == fmt(pp['liquipedia'])
                if lp_match:
                    player_lp_found.add(pp['name'])
                    pp['team'] = id
                    players.add(pp['id'])
                    pns.add(p)
            for pp in player_data:
                if 'liquipedia' in pp:
                    continue
                name_match = ptrans == fmt(pp['name'])
                aka_match = 'aka' in pp and ptrans in {fmt(ak) for ak in pp['aka']}
                if (name_match or aka_match) and pp['name'] not in player_lp_found:
                    pp['team'] = id
                    players.add(pp['id'])
                    pns.add(p)
        if players:
            td.append(dict(
                name=x,
                players=sorted(list(players)),
                id=id
            ))
            id += 1
            print(x)
            print('->', pns)
    with open('data/players.yaml', 'w') as handle:
        LOGGER.info("writing new players.yaml")
        yaml.dump(player_data, handle, transform=strip_leading_double_space)
    with open('data/teams.json', 'w') as handle:
        LOGGER.info("writing new teams.json")
        handle.write(json.dumps(td, indent=2))
    LOGGER.info("finished data update")

if __name__ == '__main__':
    asyncio.run(main())

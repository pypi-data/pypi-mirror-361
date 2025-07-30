"""Query Liquipedia API for data updates."""
import aiohttp
import asyncio
import logging
import json
import time
from collections import defaultdict

import pycountry
import requests
from ruamel.yaml import YAML
import wikitextparser as wtp
from liquipedia import db

BLACKLIST = [
    'Simtom', 'Ardeshir', 'Adam', 'Maxxtro', 'Xerxes', 'GyoreE', 'Trombone', 'Rideg', 'Kiwi', '', 'Honor', 'Player',
    'Millo', 'Avicci', 'Squall', 'MiLLeNcOlin', 'KoNFeR'
]
LOGGER = logging.getLogger(__name__)
WAIT_SECS = 30
PAGE_SIZE = 500
CONDITIONS = [
    'Category:Age of Empires II Players',
    #'Is player::true',
    'Has aoe2net id::+'
]
PROPS = [
    'Has pagename',
]
HEADERS = {'User-Agent': 'https://github.com/SiegeEngineers/aoc-reference-data'}
API = "https://liquipedia.net/ageofempires/api.php"

def fetch():
    """Fetch data from liquipedia API."""
    output = []
    offset = 0
    while True:
        LOGGER.info("querying liquipedia at offset %d", offset)
        url = 'https://liquipedia.net/ageofempires/api.php'
        resp = requests.get(url, params={
            'action': 'askargs',
            'format': 'json',
            'conditions': '|'.join(CONDITIONS),
            'printouts': '|'.join(PROPS),
            'parameters': '|'.join([f'offset={offset}', f'limit={PAGE_SIZE}'])
        }, headers={
            'User-Agent': 'https://github.com/SiegeEngineers/aoc-reference-data'
        })

        try:
            data = resp.json()
        except json.decoder.JSONDecodeError:
            LOGGER.exception("failed to fetch: %s", resp.content)
        for result in data['query']['results'].values():
            record = result['printouts']
            page = record['Has pagename'][0]['fulltext']
            name = record['Has pagename'][0]['displaytitle']
            url = record['Has pagename'][0]['fullurl']
            output.append(dict(page=page, name=name, url=url))

        offset = data.get('query-continue-offset')
        if not offset:
            break
        time.sleep(WAIT_SECS)

    return output


def get_props(page, props):
    #LOGGER.info(f"getting props for {page}")
    resp = requests.get(API, params={
        'action': 'query',
        'prop': 'revisions',
        'titles': page,
        'rvslots': '*',
        'rvprop': 'content',
        'formatversion': 2,
        'format': 'json'
    }, headers=HEADERS)
    markup = resp.json()['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    parsed = wtp.parse(markup)
    out = {}
    for tpl in parsed.templates:
        if tpl.name.strip() != 'Infobox player':
            continue
        for a in tpl.arguments:
            if a.name.strip() in props:
                out[a.name.strip()] = a.value.strip()
    return out

def clean(name):
    return name.lower().replace("_", " ").strip()

def find_new(result_data, player_data, last_id):
    seen = set([clean(p['liquipedia']) for p in player_data if 'liquipedia' in p])
    seen |= set([clean(p['name']) for p in player_data])
    rd = [x for x in result_data if x.get("aoe2net_id") and clean(x['name']) not in seen]
    print(len(result_data), len(rd))
    for n in rd:
        time.sleep(1)
        props = get_props(n['page'], ['country', 'aoe2net_id', 'aoe-elo.com_id', 'game'])
        #if 'game' not in props or 'aoe2' not in props['game']:
        #    print(f"error: not aoe2 player: {n['name']}")
        #    continue
        if 'aoe2net_id' not in props or not props['aoe2net_id']:
            print(f"error: no aoe2net id for {n['name']}")
            continue
        try:
            country_code = pycountry.countries.search_fuzzy(props['country'])[0].alpha_2.lower()
        except LookupError:
            country_code = "xyz"
        last_id += 1
        if n['name'] in BLACKLIST:
            continue
        print(n['name'], country_code, props['aoe2net_id'])
        rec = dict(
            name=n['name'],
            country=country_code,
            platforms=dict(
                rl=[x.strip() for x in n.get("aoe2net_id").split(',')]
            ),
            liquipedia=n['name'],
            id=last_id,
            #aoeelo=int(props['aoe-elo.com_id']) if 'aoe-elo.com_id' in props and props['aoe-elo.com_id'] else None,
        )
        print(rec)
        if 'aoe-elo.com_id' in props and props['aoe-elo.com_id']:
            rec["aoeelo"] = int(props['aoe-elo.com_id'])
        player_data.append(rec)


def strip_leading_double_space(stream):
    if stream.startswith("  "):
        stream = stream[2:]
    return stream.replace("\n  ", "\n")

async def main():
    logging.basicConfig(level=logging.INFO)
    LOGGER.info("starting data update")
    async with aiohttp.ClientSession() as session:
        result_data = await db.players(session)
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True
    with open('data/players.yaml', 'r') as handle:
        player_data = yaml.load(handle)
    last_id = max([p.get('id') for p in player_data])
    find_new(result_data, player_data, last_id)
    with open('data/players.yaml', 'w') as handle:
        LOGGER.info("writing new players.yaml")
        yaml.dump(player_data, handle, transform=strip_leading_double_space)
    LOGGER.info("finished data update")


if __name__ == '__main__':
    asyncio.run(main())

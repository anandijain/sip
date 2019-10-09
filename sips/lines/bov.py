import time
import json

import requests as r
import requests_futures
from requests_futures.sessions import FuturesSession

import sips.h.macros as m


bov = 'https://www.bovada.lv/services/sports/event/v2/events/A/description/football/nfl'
bov_scores_url = 'https://services.bovada.lv/services/sports/results/api/v1/scores/'


def async_req(links):
    session = FuturesSession()
    jsons = [session.get(l).result().json() for l in links]
    return jsons


def ids(events):
    if not events:
        events = get_events()
    ids = []
    for event in events:
        game_id = event['id']
        ids.append(game_id)
    return ids


def games(config_path):
    with open(config_path) as config:
        conf = json.load(config)
    ids = conf['games'][0]['game_ids']
    bov_events = get_events()
    ret = []
    for game_id in ids:
        for event in bov_events:
            if int(event['id']) == game_id:
                ret.append(parse_event(event))
    return ret


def req_json(link=bov):
    bov_json = r.get(link).json()
    return bov_json


def events_sports():
    jsons = async_req(m.build_urls())
    bov_events = []
    for json in jsons:
        if not json:
            continue
        events = json[0]['events']
        bov_events += events
    return bov_events


def get_events():
    json = req_json()
    bov_events = json[0]['events']
    return bov_events


def lines(events=None):
    if not events:
        events = get_events()
    lines = [parse_event(e) for e in events]
    # lines = []
    # for event in events:
    #     lines.append(parse_event(event))
    return lines


def header():
    return ['sport', 'game_id', 'a_team', 'h_team', 'cur_time', 'last_mod', 'num_markets', 'live', \
        'quarter', 'secs', 'a_pts', 'h_pts', 'status', \
        'a_ps', 'h_ps', 'a_hcap', 'h_hcap', 'a_ml', 'h_ml', 'a_tot', 'h_tot', \
        'a_hcap_tot', 'h_hcap_tot', 'a_ou', 'h_ou', 'game_start_time']


def parse_event(event):
    '''
    [sport, game_id, a_team, h_team, cur_time, last_mod, num_markets, live],
    [quarter, secs, a_pts, h_pts, status], [
    a_ps, h_ps, a_hcap, h_hcap, a_ml, h_ml, a_tot, h_tot,
    a_hcap_tot, h_hcap_tot, a_ou, h_ou, game_start_time]
    '''
    sport = event['sport']
    game_id = event['id']
    a_team, h_team = teams(event)
    cur_time = time.time()
    last_mod = event['lastModified']
    num_markets = event['numMarkets']
    live = event['live']
    quarter, secs, a_pts, h_pts, status = score(game_id)


    display_groups = event['displayGroups'][0]
    markets = display_groups['markets']
    a_ps, h_ps, a_hcap, h_hcap, a_ml, h_ml, a_tot, h_tot, a_hcap_tot, h_hcap_tot, a_ou, h_ou = parse_markets(markets)

    game_start_time = event['startTime']

    ret = [sport, game_id, a_team, h_team, cur_time, last_mod, num_markets, live, \
        quarter, secs, a_pts, h_pts, status, \
        a_ps, h_ps, a_hcap, h_hcap, a_ml, h_ml, a_tot, h_tot, \
        a_hcap_tot, h_hcap_tot, a_ou, h_ou, game_start_time]

    return ret


def teams_from_line(line):
    return line[2:4]


def parse_markets(markets):
    a_ps, h_ps, a_hcap, h_hcap, a_ml, h_ml, a_tot, h_tot, \
            a_hcap_tot, h_hcap_tot, a_ou, h_ou = ["NaN" for _ in range(12)]
    for market in markets:
        desc = market['description']
        outcomes = market['outcomes']
        if desc == 'Point Spread':
            a_ps, h_ps, a_hcap, h_hcap = spread(outcomes)
        elif desc == 'Moneyline':
            a_ml, h_ml = moneyline(outcomes)
        elif desc == 'Total':
            a_tot, h_tot, a_hcap_tot, h_hcap_tot, a_ou, h_ou = total(outcomes)

    data = [a_ps, h_ps, a_hcap, h_hcap, a_ml, h_ml, a_tot, h_tot, \
            a_hcap_tot, h_hcap_tot, a_ou, h_ou]
    return data


def spread(outcomes):
    a_ps, a_hcap, h_ps, h_hcap = ['NaN' for _ in range(4)]
    for outcome in outcomes:
        price = outcome['price']
        if outcome['type'] == 'A':
            a_ps = price['american']
            a_hcap = price['handicap']
        else:
            h_ps = price['american']
            h_hcap = price['handicap']
    return a_ps, h_ps, a_hcap, h_hcap


def moneyline(outcomes):
    a_ml = 'NaN'
    h_ml = 'NaN'
    for outcome in outcomes:
        price = outcome['price']
        if outcome['type'] == 'A':
            a_ml = price['american']
        else:
            h_ml = price['american']

    return a_ml, h_ml


def total(outcomes):
    if not outcomes:
        return ['NaN' for _ in range(6)]
    a_price = outcomes[0]['price']
    h_price = outcomes[1]['price']
    a_tot = a_price['american']
    h_tot = h_price['american']
    a_hcap_tot = a_price['handicap']
    h_hcap_tot = h_price['handicap']
    a_ou = outcomes[0]['type']
    h_ou = outcomes[1]['type']
    return [a_tot, h_tot, a_hcap_tot, h_hcap_tot, a_ou, h_ou]


def teams(event):
    # returns away, home
    team_one = event['competitors'][0]
    team_two = event['competitors'][1]
    if team_one['home']:
        h_team = team_one['name']
        a_team = team_two['name']
    else:
        a_team = team_one['name']
        h_team = team_two['name']
    return a_team, h_team


def game_json(game_id):
    game_json = r.get(bov_scores_url + game_id).json()
    time.sleep(0.05)
    return game_json


def score(game_id):
    [quarter, secs, a_pts, h_pts, status] = ['NaN' for _ in range(5)]

    json = game_json(game_id)
    if json.get('Error'):
        return [quarter, secs, a_pts, h_pts, status]
    clock = json.get('clock')
    if clock:
        quarter = clock['periodNumber']
        secs = clock['relativeGameTimeInSecs']

    a_pts = json['latestScore']['visitor']
    h_pts = json['latestScore']['home']
    status = 0
    if json['gameStatus'] == "IN_PROGRESS":
        status = 1

    return [quarter, secs, a_pts, h_pts, status]

# def main():
#     while True:


if __name__ == '__main__':
    l = lines()
    print(l)

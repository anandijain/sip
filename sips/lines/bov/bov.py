'''
uses the bovada api to get json data for odds and scores
'''
import requests as r
import sips.h.openers as o
from sips.macros import macros as m
from sips.lines.bov.utils import bov_utils as u


def get_events(sports=['nfl'], output='list', session=None):
    '''
    gets all events for all the sports specified in macros.py
    output: either 'list' or 'dict', where each key is the game_id
    '''
    links = u.filtered_links(sports)
    jsons = [o.req_json(l) for l in links]
    # jsons = o.async_req(links, session=session)
    events = u.list_from_jsons(jsons)

    if output == 'dict':
        events = u.dict_from_events(events)

    return events


def lines(sports, output='list', verbose=False, fixlines=True,
          session=None, espn=False):
    '''
    returns either a dictionary or list
    dictionary - (game_id, row)
    '''
    if not sports:
        print(f'sports is None')
        return

    if fixlines:
        links = u.filtered_links(sports)
    else:
        links = [m.BOV_URL + u.match_sport_str(s) for s in sports]

    if not session:
        events = get_events(sports=sports, output='dict')

    if output == 'dict':
        lines = u.dict_from_events(events, key='id', rows=True,
                                   grab_score=False)
        scores = u.get_scores(events, session=session)
        data = u.merge_lines_scores(lines, scores)
    else:
        data = [u.parse_event(e, grab_score=True) for e in events]

    if verbose:
        print(f'lines: {data}')

    return data


def main():
    data = lines(["nba"], output='list')
    print(data)
    return data


if __name__ == '__main__':
    main()

import os
import pandas as pd
import numpy as np

from sips.macros import macros as m


def serialize_row(row, teams_dict, statuses_dict, include_teams=False):
    """
    going to take in something like this:
    ['FOOT', 5741304, 'Pittsburgh Steelers', 'Cleveland Browns', 1573540736617, 28,
    False, '0', '-1', '0', '0', 'PRE_GAME', '2.5', '-2.5', '-105', '-115', '+125',
    '-145', '40.0', '40.0', '-110', '-110', 'O', 'U', 1573780800000]
    and return a np array

    # note:
    serialize row needs to be refactored, i'm thinking that it should take in 
    a dataframe row and maybe have the option of what columns we want.
    so it can maximally serialize or, given a subset of columns, only serialize those 
    """
    ret = []
    row = list(row)
    ret += teams(row, teams_dict)
    ret += row[4:6]
    ret += mkt_live(row)
    ret += [row_ml(ml) for ml in row[7:11]]
    ret += statuses_dict[row[11]]
    ret += [row_ml(ml) for ml in row[12:22]]
    final = np.array(ret, dtype=np.float32)
    return final

# def serialize_df(df, obj_cols, maps):
    


def mkt_live(row):
    hot_mkt = [1, 0] if row[6] else [0, 1]
    return hot_mkt


def row_ml(ml):
    """
    given a list of unparsed moneylines (eg can be 'EVEN' and None)
    edit the values such that 'EVEN' -> 100 and None -> -1
    typical order of list is [a0, h0, a1, h1]
    """
    if ml == "EVEN":
        ret = 100
    elif ml == None:
        ret = -1
    else:
        try:
            ret = float(ml)
        except:
            ret = -1
    return ret


def teams(row, teams_dict):
    '''
    row is one of:
        row of type list (with schema specified in serialize row)
        pandas row
    teams_dict is:
        team_name: hotted vector
    '''
    ret = []

    if isinstance(row, pd.core.series.Series):
        a_team = row.a_team
        h_team = row.h_team
    else:
        a_team, h_team = row[2:4]

    for t in [a_team, h_team]:
        hot_team = teams_dict[t]
        ret += hot_team

    return ret



if __name__ == "__main__":
    fn = m.PROJ_DIR + 'ml/lines/'

    # pd.read_csv('')
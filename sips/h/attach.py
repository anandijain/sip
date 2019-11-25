import pandas as pd
import numpy as np

import sips.h.helpers as h
from sips.h import calc
from sips.h import hot
from sips.h import serialize as s
from sips.h import analyze
from sips.macros import bov as bm


def ml_transitions(game, attach=True, verbose=False):
    """
    given a dataframe of live lines for a single game,
    returns a list of classifications for the line movement
    """
    transition_classes = []
    teams_dict, statuses_dict = hot.dicts_for_one_hotting()

    prev = [None, None]

    for i, row in game.iterrows():
        cur = list(row[["a_ml", "h_ml"]])
        transition_class = analyze.classify_transition(prev, cur)
        transition_classes.append(transition_class)
        prev = cur

    if attach:
        trans_df = pd.DataFrame(transition_classes)
        trans_df = trans_df.add_prefix("trans_class_")
        ret = pd.concat([game, trans_df], axis=1)
    else:
        ret = transition_classes

    if verbose:
        strings = {i: s for i, s in enumerate(bm.TRANSITION_CLASS_STRINGS)}

        for i, t in enumerate(transition_classes):
            class_num = np.argmax(t)
            print(f"{i}: {strings[class_num]}")

    return ret


def wins(dfs, verbose=True):
    """

    """
    dfs_w_wins = []
    total_games = len(dfs)
    skipped = 0
    for df in dfs:
        if df is not None:
            df.drop(["a_ou", "h_ou"], axis=1, inplace=True)
            # print(df)
            with_labels = win(df)
            if with_labels is not None:
                dfs_w_wins.append(with_labels)
            else:
                skipped += 1
                continue

    if verbose:
        print(f"num games skipped: {skipped} out of {total_games}")

    return dfs_w_wins


def win(game_df, verbose=False):
    """
    given a dataframe for a single game, takes the last row
    checks if the status is 'GAME_END'
    then adds new columns for the winner of the game based on the score
    """
    case = ""
    last_row = game_df.iloc[-1, :]
    status = last_row.status
    ret = None

    if status == "GAME_END":
        if last_row.a_pts > last_row.h_pts:
            a_win = True
            h_win = False
            case = f"away {last_row.a_team} win"
        elif last_row.a_pts < last_row.h_pts:
            a_win = False
            h_win = True
            case = f"home {last_row.h_team} win"
        else:
            case = "game tie"
            a_win = False
            h_win = False

        game_df["a_win"] = a_win
        game_df["h_win"] = h_win
        ret = game_df
    else:
        case = "no game end status"

    if verbose:
        print(case)

    return ret


def profit(df):
    """

    """
    h_mls = df.h_ml
    a_mls = df.a_ml
    status = df.status
    h_profs = []
    a_profs = []
    h_init = None
    a_init = None
    for i in range(len(status)):
        if status[i] == "IN_PROGRESS":
            if df.a_ml.iloc[i] != "None":
                a_init = df.a_ml.iloc[i]
                if a_init == "EVEN":
                    a_init = 100
                else:
                    a_init = int(a_init)
            if df.h_ml.iloc[i] != "None":
                h_init = df.h_ml.iloc[i]
                if h_init == "EVEN":
                    h_init = 100
                else:
                    h_init = int(h_init)

            if h_init and a_init:
                break

    for i in range(len(h_mls)):

        h_ml = h_mls.iloc[i]
        a_ml = a_mls.iloc[i]

        if h_ml == "None" or a_ml == "None":
            h_profs.append("na")
            a_profs.append("na")
        else:
            if a_ml == "EVEN":
                a_ml = 100
            if h_ml == "EVEN":
                h_ml = 100
            h_prof = calc.prof_amt(h_init, int(a_ml))
            a_prof = calc.prof_amt(a_init, int(h_ml))
            h_profs.append(h_prof)
            a_profs.append(a_prof)

    df["h_profs"] = h_profs
    df["a_profs"] = a_profs
    return df


def attach_all(df):
    fxns = [wins]  # , ml_transitions, profit]
    for fxn in fxns:
        if df is None:
            return
        df = fxn(df)

    return df


def test_attach_all():
    dfs = h.get_dfs()
    all_attached = []
    for df in dfs:
        if df.empty:
            continue
        attached_df = attach_all(df)
        if attached_df is not None:
            all_attached.append(attached_df)

    print(len(all_attached))
    return all_attached


if __name__ == "__main__":
    in_cols = bm.TO_SERIALIZE
    dfs = test_attach_all()
    print(dfs[0].columns)
    print(dfs[0])
    sXs, sYs = s.serialize_dfs(
        dfs,
        in_cols=in_cols,
        label_cols=["a_win", "h_win"],
        dont_hot=True,
        to_numpy=False,
    )
    df = dfs[0]
    print(df)
    print(df.dtypes)
    print(df.columns)
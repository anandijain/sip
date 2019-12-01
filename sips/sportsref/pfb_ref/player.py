import os
import time
import pandas as pd

import sips
from sips.macros import sports_ref as sref
from sips.h import grab
from sips.h import parse
from sips.sportsref.general import player
from sips.sportsref import utils as sru

comment_idxs = {
    20: "detailed_rushing_and_receiving",
    24: "returns",
    25: "defense",
    29: "scoring",
    30: "snap_counts",
    33: "combine",
}


def player_links(output="df", write_df=False):
    all_links = []

    section_links = [
        sref.pfb_url + "players/" + letter.upper() for letter in sref.letters.append(x)
    ]

    ps = {l: grab.get_page(l) for l in section_links}
    for l, p in ps.items():
        div = p.find("div", {"id": "div_players"})
        if not div:
            print(l)
            continue
        a_tags = div.find_all("a")
        links = [a["href"] for a in a_tags]
        all_links += links
    if output == "df":
        all_links = pd.DataFrame(all_links, columns=["link"])
        if write_df:
            all_links.to_csv()
    return all_links


def main():
    table_ids = ["stats", "rushing_and_receiving"]

    path = sips.PARENT_DIR + "data/nfl/players/"
    player_links_path = path + "index.csv"
    df = pd.read_csv(player_links_path)

    ps = {}
    for i, link in enumerate(df.link):
        player_url = sref.pfb_no_slash + link
        p_id = sru.url_to_id(player_url)

        player_path = path + p_id + "/"
        print(f"{i}: {player_url}")

        if not os.path.isdir(player_path):
            os.mkdir(player_path)

        p = player.player(player_url, table_ids, comment_idxs, verbose=True)

        ps[link] = p

        for t_id, df in p.items():

            df = df[0]
            fn = p_id + "_" + t_id
            df.to_csv(player_path + fn + ".csv")

    return ps


if __name__ == "__main__":
    players = main()
    print(players)

from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from http.client import RemoteDisconnected
from collections import Counter
import ssl
import json
import time
import sys

myssl = ssl.create_default_context()
myssl.check_hostname = False
myssl.verify_mode=ssl.CERT_NONE

allgamedata_url = "https://127.0.0.1:2999/liveclientdata/allgamedata"

def build_snapshot(all_players, active_team):
    snapshot = {}
    for player in all_players:
        item_list = []
        if player.get("team") != active_team:
            for item in player.get("items", []):
                item_list.append(item.get("displayName"))
            item_list.sort()
            snapshot[player.get("championName")] = item_list
    return snapshot

def fetch_allgamedata():
    try:
        allgamedata_response = urlopen(allgamedata_url, context = myssl)
        allgamedata_json = json.loads(allgamedata_response.read())
        return allgamedata_json
    except (URLError, HTTPError, RemoteDisconnected):
        print("Connection not found.")
        time.sleep(5)
        return None
    
def get_active_teamId(allgamedata_json):
    active_teamId = None
    active_player_riotId = allgamedata_json.get("activePlayer").get("riotId")
    for player in allgamedata_json.get("allPlayers"):
        if player.get("riotId") == active_player_riotId:
            active_teamId = player.get("team")
            return active_teamId

def print_snapshot(snapshot):
    print("Enemy Team:")
    for player, item_list in snapshot.items():
        print("\t" + player)
        for item in item_list:
            print("\t\t" + item)

# Initiate
while True:
    allgamedata_json = fetch_allgamedata()
    if allgamedata_json:
        break

# TeamID
# BLUE SIDE (TOP TEAM): ORDER
# RED SIDE (BOTTOM TEAM): CHAOS

# Obtain Active Player ID
active_teamId = get_active_teamId(allgamedata_json)

# Build initial enemy team snapshot
saved_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_teamId)

# Print Enemies and their Items
print_snapshot(saved_enemy_snapshot)

# Polling
while True:
    allgamedata_json = fetch_allgamedata()
    if not allgamedata_json:
        continue

    active_teamId = get_active_teamId(allgamedata_json)

    updated_enemy_snapshot = build_snapshot(allgamedata_json.get("allPlayers"), active_teamId)

    if saved_enemy_snapshot != updated_enemy_snapshot:
        saved_roster = set(saved_enemy_snapshot.keys())
        updated_roster = set(updated_enemy_snapshot.keys())
        if saved_roster != updated_roster:
            # roster_changed = saved_roster.symmetric_difference(updated_roster)
            pass
        else:
            for championName, item_list in saved_enemy_snapshot.items():
                saved_item_counter = Counter(item_list)
                updated_item_counter = Counter(updated_enemy_snapshot.get(championName))
                if saved_item_counter != updated_item_counter:
                    new_items = updated_item_counter - saved_item_counter
                    removed_items = saved_item_counter - updated_item_counter
                    # print the amount added or removed if count > 1
                    print(championName + "'s items changed:")
                    for new_item, count in new_items.items():
                        count = (" x" + count) if count > 1 else ""
                        print("+ " + new_item + count)
                    for removed_item, count in removed_items.items():
                        count = (" x" + count) if count > 1 else ""
                        print("- " + removed_item + count)
        saved_enemy_snapshot = updated_enemy_snapshot.copy()
    
    time.sleep(1)
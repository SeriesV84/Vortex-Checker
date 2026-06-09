import requests
import os

HYPIXEL_API_URL = 'https://api.hypixel.net/player'

def get_stats(username, results_dir, email, password):
    if not username or username == 'N/A':
        return
    api_key_file = 'hypixel_api_key.txt'
    if not os.path.exists(api_key_file):
        return
    with open(api_key_file, 'r') as f:
        api_key = f.read().strip()
    if not api_key:
        return
    uuid = get_uuid(username)
    if not uuid:
        return
    params = {'key': api_key, 'uuid': uuid}
    try:
        resp = requests.get(HYPIXEL_API_URL, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') and data.get('player'):
                player = data['player']
                stats = {}
                stats['rank'] = get_rank(player)
                stats['level'] = player.get('networkExp', 0)
                stats['first_login'] = player.get('firstLogin')
                stats['last_login'] = player.get('lastLogin')
                stats['bedwars_stars'] = player.get('achievements', {}).get('bedwars_level', 0)
                stats['skyblock_coins'] = player.get('stats', {}).get('SkyBlock', {}).get('coin_purse', 0)
                line = f"{email}:{password} | {username}"
                if stats.get('rank'): line += f" | Rank: {stats['rank']}"
                if stats.get('level'): line += f" | Level: {stats['level']}"
                if stats.get('bedwars_stars'): line += f" | BW: {stats['bedwars_stars']}"
                if stats.get('skyblock_coins'): line += f" | SB Coins: {stats['skyblock_coins']}"
                if stats.get('first_login'): line += f" | First: {stats['first_login']}"
                if stats.get('last_login'): line += f" | Last: {stats['last_login']}"
                with open(os.path.join(results_dir, 'hypixel_stats.txt'), 'a', encoding='utf-8') as f:
                    f.write(line + '\n')
                print(f"  [HYPIXEL] {stats.get('rank', 'No rank')} | Lvl {stats.get('level', '?')}")
    except Exception:
        pass

def get_uuid(username):
    try:
        resp = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}', timeout=10)
        if resp.status_code == 200:
            return resp.json().get('id')
    except Exception:
        pass
    return None

def get_rank(player):
    prefix = player.get('prefix')
    if prefix:
        return prefix
    rank = player.get('rank')
    if rank and rank != 'NORMAL':
        return rank
    package_rank = player.get('monthlyPackageRank')
    if package_rank and package_rank != 'NONE':
        return package_rank
    return 'Default'

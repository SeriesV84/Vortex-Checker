import requests
import os

DONUT_API_URL = 'https://api.donutsmp.net/v1'

def get_player_uuid(username, session):
    try:
        resp = session.get(f'https://api.mojang.com/users/profiles/minecraft/{username}', timeout=10)
        if resp.status_code == 200:
            return resp.json().get('id')
    except Exception:
        pass
    return None

def fetch_donut_stats(uuid, api_key):
    url = f"{DONUT_API_URL}/{uuid}/stats"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def check_access(uuid_val, results_dir, email, password, session):
    if not uuid_val or uuid_val == 'N/A':
        return
    api_key_file = 'donut_api_key.txt'
    if not os.path.exists(api_key_file):
        return
    with open(api_key_file, 'r') as f:
        api_key = f.read().strip()
    if not api_key:
        return
    stats = fetch_donut_stats(uuid_val, api_key)
    if stats and isinstance(stats, dict):
        with open(os.path.join(results_dir, 'donut_stats.txt'), 'a', encoding='utf-8') as f:
            f.write(f"{email}:{password}\n")
            f.write(f"UUID: {uuid_val}\n")
            for key, value in stats.items():
                f.write(f"{key}: {value}\n")
            f.write("="*50 + "\n")
        print(f"  [DONUTSMP] Stats saved")

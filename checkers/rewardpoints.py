import requests
import re
import os
import time

def check_rewards(session, email, password, results_dir):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        r = session.get('https://rewards.bing.com/', headers=headers, timeout=15)
        if 'action="https://rewards.bing.com/signin-oidc"' in r.text or 'id="fmHF"' in r.text:
            action_match = re.search('action="([^"]+)"', r.text)
            if action_match:
                action_url = action_match.group(1)
                data = {}
                for input_match in re.finditer('<input type="hidden" name="([^"]+)" id="[^"]+" value="([^"]+)">', r.text):
                    data[input_match.group(1)] = input_match.group(2)
                r = session.post(action_url, data=data, headers=headers, timeout=15)
        all_matches = re.findall(',"availablePoints":(\\d+)', r.text)
        if all_matches:
            points = max(all_matches, key=int)
            if points != '0':
                line = f'{email}:{password} | Rewards Points: {points}'
                with open(os.path.join(results_dir, 'reward_points.txt'), 'a', encoding='utf-8') as f:
                    f.write(line + '\n')
                print(f"  [REWARDS] {points} points")
                return
        ts = int(time.time() * 1000)
        flyout_url = f'https://www.bing.com/rewards/panelflyout/getuserinfo?timestamp={ts}'
        headers_flyout = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept': 'application/json', 'Referer': 'https://www.bing.com/', 'X-Requested-With': 'XMLHttpRequest'}
        r_flyout = session.get(flyout_url, headers=headers_flyout, timeout=15)
        if r_flyout.status_code == 200:
            data = r_flyout.json()
            if data.get('userInfo', {}).get('isRewardsUser'):
                balance = data.get('userInfo', {}).get('balance')
                if balance:
                    line = f'{email}:{password} | Rewards Points: {balance}'
                    with open(os.path.join(results_dir, 'reward_points.txt'), 'a', encoding='utf-8') as f:
                        f.write(line + '\n')
                    print(f"  [REWARDS] {balance} points")
    except Exception:
        pass

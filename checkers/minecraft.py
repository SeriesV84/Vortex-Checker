import requests

def get_profile(session, minecraft_token):
    if not minecraft_token:
        return None
    try:
        resp = session.get('https://api.minecraftservices.com/minecraft/profile',
                           headers={'Authorization': f'Bearer {minecraft_token}'},
                           timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            capes = [cape.get('alias') for cape in data.get('capes', []) if cape.get('alias')]
            return {
                'name': data.get('name', 'N/A'),
                'id': data.get('id', 'N/A'),
                'capes': capes
            }
    except Exception:
        pass
    return None

def check_ownership(session, minecraft_token):
    if not minecraft_token:
        return None
    try:
        resp = session.get('https://api.minecraftservices.com/entitlements/license',
                           headers={'Authorization': f'Bearer {minecraft_token}'},
                           timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('items', [])
            has_normal = False
            has_game_pass_pc = False
            has_game_pass_ultimate = False
            for item in items:
                name = item.get('name', '')
                source = item.get('source', '')
                if name in ('game_minecraft', 'product_minecraft') and source in ('PURCHASE', 'MC_PURCHASE'):
                    has_normal = True
                if name == 'product_game_pass_pc':
                    has_game_pass_pc = True
                if name == 'product_game_pass_ultimate':
                    has_game_pass_ultimate = True
            if has_normal and has_game_pass_pc:
                return 'Normal Minecraft (with Game Pass)'
            if has_normal and has_game_pass_ultimate:
                return 'Normal Minecraft (with Game Pass Ultimate)'
            if has_normal:
                return 'Normal Minecraft'
            if has_game_pass_ultimate:
                return 'Xbox Game Pass Ultimate'
            if has_game_pass_pc:
                return 'Xbox Game Pass (PC)'
        return None
    except Exception:
        return None

def check_name_change(session, minecraft_token):
    if not minecraft_token:
        return None
    try:
        resp = session.get('https://api.minecraftservices.com/minecraft/profile/namechange',
                           headers={'Authorization': f'Bearer {minecraft_token}'},
                           timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'changeable': data.get('nameChangeAllowed', False),
                'created_at': data.get('createdAt')
            }
    except Exception:
        pass
    return None

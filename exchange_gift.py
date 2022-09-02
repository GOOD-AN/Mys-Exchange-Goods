'''
米游社商品兑换
'''
import hashlib
import random
import string
import time
import requests

MI_URL = 'https://api-takumi.mihoyo.com'
WEB_URL = 'https://webapi.account.mihoyo.com'

MI_COOKIE = ""


def get_gift_biz(goods_id: int):
    '''
    获取商品所属分区
    '''
    gift_detail_url = MI_URL + "/mall/v1/web/goods/detail"
    gift_detail_params = {
        "app_id": 1,
        "point_sn": "myb",
        "goods_id": goods_id,
    }
    try:
        gift_detail_req = requests.get(gift_detail_url, params=gift_detail_params)
        if (gift_detail_req.status_code != 200):
            return False
        gift_detail = gift_detail_req.json()["data"]
        if gift_detail is None:
            return False
        # print(f"商品类型：{gift_detail['type']}")
        return gift_detail['game_biz']
    except:
        return False


def get_ds():
    '''
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/tools.py
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/setting.py
    '''
    android_salt = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    md5 = hashlib.md5()
    md5.update(f'salt={android_salt}&t={t}&r={r}'.encode())
    c = md5.hexdigest()
    return f"{t},{r},{c}"


def get_cookie_str(target):
    '''
    获取cookie字符串中相应的数据
    '''
    location = MI_COOKIE.find(target)
    return MI_COOKIE[MI_COOKIE.find("=", location) + 1:MI_COOKIE.find(";", location)]


def get_action_ticket():
    '''
    获取查询所需 ticket
    '''
    try:
        stoken = get_cookie_str('stoken')
        uid = get_cookie_str('ltuid')
        action_ticket_url = MI_URL + "/auth/api/getActionTicketBySToken"
        action_ticket_headers = {
            #"User-Agent": "okhttp/4.8.0",
            "Cookie": MI_COOKIE,
            #"DS": get_ds()
        }
        action_ticket_params = {"action_type": "game_role", "stoken": stoken, "uid": uid}
        action_ticket_req = requests.get(action_ticket_url,
                                         headers=action_ticket_headers,
                                         params=action_ticket_params)
        if (action_ticket_req.status_code != 200):
            print("ticket请求失败，请检查cookie")
            return False
        return action_ticket_req.json()['data']['ticket']
    except Exception as e:
        print(e)
        return False


def get_game_roles(action_ticket, game_biz, uid):
    '''
    检查是否绑定角色
    '''
    try:
        game_roles_url = MI_URL + "/binding/api/getUserGameRoles"
        game_roles_params = {
            "point_sn": "myb",
            "action_ticket": action_ticket,
            "game_biz": game_biz
        }
        game_roles_headers = {"cookie": MI_COOKIE}
        game_roles_req = requests.get(game_roles_url,
                                      headers=game_roles_headers,
                                      params=game_roles_params)
        if (game_roles_req.status_code != 200):
            print("检查角色请求失败，请检查传入参数")
            return False
        game_roles_list = game_roles_req.json()['data']['list']
        if not game_roles_list:
            print('没有绑定任何角色')
            return False
        for game_roles in game_roles_list:
            if game_roles['game_biz'] == game_biz and game_roles['game_uid'] == str(uid):
                return True
        return False
    except Exception as e:
        print(e)
        return False


def post_exchange_gift(gift_id):
    '''
    兑换礼物
    '''
    try:
        exchange_gift_url = MI_URL + "/mall/v1/web/goods/exchange"
        exchange_gift_json = {
            "app_id": 1,
            "point_sn": "myb",
            "goods_id": str(gift_id),
            "exchange_num": 1,
            "address_id": 1,
            "uid": 1,
            "region": "cn_gf01",
            "game_biz": "hk4e_cn"
        }
        exchange_gift_headers = {
            "Cookie": MI_COOKIE,
        }
        exchange_gift_req = requests.post(exchange_gift_url,
                                          headers=exchange_gift_headers,
                                          json=exchange_gift_json)
        if (exchange_gift_req.status_code != 200):
            print("兑换失败")
            return False
        print(exchange_gift_req.json())
    except Exception as e:
        print(e)
        return False
"""
米游社相关
"""
import asyncio

import httpx
import random
import re
import string
import sys
import time
from typing import Union, List, Optional, Tuple

from .user_log import logger_file
from .com_tool import md5_encode
from .data_class import UserInfo, GameInfo, GoodsInfo, AddressInfo

MYS_SALT = "TsmyHpZg8gFAVKTtlPaL6YwMldzxZJxQ"
MYS_SALT_TWO = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
MYS_SALT_WEB = "osgT0DljLarYxgebPPHJFjdaxPfoiHGt"
MYS_CHANNEL = {
    "1": "崩坏3",
    "2": "原神",
    "3": "崩坏学园2",
    "4": "未定事件簿",
    "5": "米游社",
    "6": "崩坏：星穹铁道",
    "8": "绝区零"
}
GAME_NAME = {
    "bh2_cn": "崩坏2",
    "bh3_cn": "崩坏3",
    "nxx_cn": "未定事件簿",
    "hk4e_cn": "原神",
    "hkrpg_cn": "崩坏：星穹铁道"
}

MI_URL = 'https://api-takumi.mihoyo.com'
WEB_URL = 'https://webapi.account.mihoyo.com'
BBS_URL = 'https://bbs-api.mihoyo.com'
MI_INTL_url = 'https://api-os-takumi.mihoyo.com'


async def get_new_ds(_b, _q):
    """
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/tools.py
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/setting.py
    https://loliurl.club/383.html
    保留此函数以备后用
    """
    try:
        t_param = str(int(time.time()))
        r_param = str(random.randint(100001, 200000))
        b_param = '传入参数, 待查明'
        q_param = '传入参数, 待查明'
        c_param = md5_encode(f"salt={MYS_SALT_TWO}&t={t_param}&r={r_param}&b={b_param}&q={q_param}")
        return f"{t_param},{r_param},{c_param}"
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


async def get_old_ds(web: bool):
    """
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/tools.py
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/setting.py
    保留此函数以备后用
    """
    if web:
        old_salt = MYS_SALT_WEB
    else:
        old_salt = MYS_SALT
    t_param = str(int(time.time()))
    r_param = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c_param = md5_encode(f'salt={old_salt}&t={t_param}&r={r_param}')
    return f"{t_param},{r_param},{c_param}"


async def get_ticket_by_mobile(mobile: str, mobile_captcha: str) -> Union[bool, int, Tuple]:
    """
    获取ticket和mys_uid
    """
    try:
        get_ticket_url = WEB_URL + "/Api/login_by_mobilecaptcha"
        get_ticket_form_data_one = {
            "mobile": mobile,
            "mobile_captcha": mobile_captcha,
            "source": "user.mihoyo.com"
        }
        async with httpx.AsyncClient() as client:
            for _ in range(3):
                get_ticket_req_one = await client.post(get_ticket_url, data=get_ticket_form_data_one)
                if get_ticket_req_one.status_code != 200:
                    logger_file.warning(f"请求出错, 错误代码为: {get_ticket_req_one.status_code}")
                    await asyncio.sleep(random.random())
                    continue
                status_code = get_ticket_req_one.json()['data']['status']
                if status_code == -201:
                    logger_file.warning("验证码错误")
                    return -201
                else:
                    break
        get_ticket_cookie_one = get_ticket_req_one.cookies
        if "login_ticket" not in get_ticket_cookie_one:
            logger_file.warning("缺少'login_ticket'字段")
            return False
        if "login_uid" not in get_ticket_cookie_one:
            mys_uid = get_ticket_req_one.json()['data']['account_info']['account_id']
        else:
            mys_uid = get_ticket_cookie_one['login_uid']
        if mys_uid is None:
            logger_file.warning("缺少'uid'字段")
            return False
        return get_ticket_cookie_one, mys_uid
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_stoken_by_ticket(login_ticket: str, mys_uid: str) -> Union[bool, str]:
    """
    获取stoken
    """
    try:
        get_stoken_url = MI_URL + "/auth/api/getMultiTokenByLoginTicket"
        get_stoken_params = {
            "login_ticket": login_ticket,
            "token_types": 3,
            "uid": mys_uid
        }
        async with httpx.AsyncClient() as client:
            for _ in range(3):
                get_stoken_req = await client.get(get_stoken_url, params=get_stoken_params)
                if get_stoken_req.status_code != 200:
                    logger_file.warning(f"请求出错, 错误代码为: {get_stoken_req.status_code}")
                    await asyncio.sleep(random.random())
                    continue
                else:
                    return get_stoken_req.json()["data"]["list"][0]["token"]
            return False
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_cookie_token_by_mobile(mobile: str, mobile_captcha: str) -> Union[bool, httpx.Cookies, int]:
    """
    获取cookie_token
    """
    try:
        get_token_url = MI_URL + "/account/auth/api/webLoginByMobile"
        get_token_form_data = {
            "is_bh2": False,
            "mobile": mobile,
            "captcha": mobile_captcha,
            "action_type": "login",
            "token_type": 6
        }
        async with httpx.AsyncClient() as client:
            for _ in range(3):
                get_token_req = await client.post(get_token_url, json=get_token_form_data)
                if get_token_req.status_code != 200:
                    logger_file.warning(f"请求出错, 错误代码为: {get_token_req.status_code}")
                    await asyncio.sleep(random.random())
                    continue
                status_code = get_token_req.json()['retcode']
                if status_code == -201:
                    logger_file.warning("验证码错误")
                    return -201
                else:
                    break
        get_token_cookie = get_token_req.cookies
        if "cookie_token" not in get_token_cookie:
            logger_file.warning("缺少'cookie_token'字段")
            return False
        return get_token_cookie
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def check_cookie(account: UserInfo) -> int:
    """
    检查cookie是否过期
    -1: 请求或运行出错
    0: cookie过期
    1: cookie有效
    """
    try:
        check_cookie_url = MI_URL + '/account/address/list'
        check_cookie_hearders = {
            'Cookie': account.cookie
        }
        async with httpx.AsyncClient() as client:
            check_cookie_req = await client.get(check_cookie_url, headers=check_cookie_hearders)
        if check_cookie_req.status_code != 200:
            logger_file.error(f"检查Cookie失败, 返回状态码为{str(check_cookie_req.status_code)}")
            return -1
        check_cookie_req = check_cookie_req.json()
        if check_cookie_req['retcode'] != 0:
            logger_file.warning("Cookie已过期")
            return 0
        return 1
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return -1


async def update_cookie(account: UserInfo) -> Union[bool, UserInfo]:
    """
    更新cookie
    需要stoken
    """
    try:
        if account.stoken == "" or account.mys_uid == "":
            logger_file.warning("缺少stoken或账户ID")
            return False
        update_cookie_url = MI_URL + "/auth/api/getCookieAccountInfoBySToken"
        update_cookie_url_params = {
            "uid": account.mys_uid,
            "stoken": account.stoken
        }
        async with httpx.AsyncClient() as client:
            update_cookie_url_req = await client.get(update_cookie_url, params=update_cookie_url_params)
        update_cookie_url_req = update_cookie_url_req.json()
        if update_cookie_url_req['data'] is None:
            logger_file.error(f"cookie获取出错，错误原因为: {update_cookie_url_req['message']}")
            return False
        account.cookie = re.sub(account.cookie_token, update_cookie_url_req['data']['cookie_token'], account.cookie)
        return account
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_channel_level(account: UserInfo) -> Union[bool, UserInfo]:
    """
    获取频道等级
    """
    try:
        if account.stoken == "":
            logger_file.warning("缺少stoken")
            return False
        channel_level_url = BBS_URL + '/user/api/getUserFullInfo'
        channel_level_headers = {
            "Cookie": account.cookie
        }
        channel_level_params = {
            "uid": account.mys_uid
        }
        async with httpx.AsyncClient() as client:
            channel_level_req = await client.get(channel_level_url, headers=channel_level_headers,
                                                 params=channel_level_params)
        if channel_level_req.status_code != 200:
            logger_file.error(f"获取频道等级失败, 返回状态码为: {channel_level_req.status_code}")
            return False
        channel_level_data = channel_level_req.json()
        if channel_level_data['retcode'] != 0:
            logger_file.error(f"获取频道等级失败, 错误信息为: {channel_level_data['message']}")
            return False
        channel_data_dict = {}
        for channel_data in channel_level_data['data']['user_info']['level_exps']:
            channel_data_dict[str(channel_data['game_id'])] = channel_data['level']
        account.channel_dict = channel_data_dict
        return account
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_action_ticket(account: UserInfo):
    """
    获取查询所需 ticket
    需要stoken与账户ID
    """
    try:
        if account.stoken == "" or account.mys_uid == "":
            logger_file.warning("缺少stoken或账户ID")
            return False
        action_ticket_url = MI_URL + "/auth/api/getActionTicketBySToken"
        action_ticket_params = {"action_type": "game_role", "stoken": account.stoken, "uid": account.mys_uid}
        async with httpx.AsyncClient() as client:
            action_ticket_req = await client.get(action_ticket_url, params=action_ticket_params)
        if action_ticket_req.status_code != 200:
            logger_file.error(
                f"ticket请求失败, 请检查cookie, 返回状态码为{str(action_ticket_req.status_code)}")
            return False
        if action_ticket_req.json()['data'] is None:
            logger_file.error(f"ticket获取失败, 原因为{action_ticket_req.json()['message']}")
            return False
        return action_ticket_req.json()['data']['ticket']
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_game_roles(account: UserInfo) -> Union[bool, UserInfo]:
    """
    获取绑定角色
    """
    try:
        action_ticket = await get_action_ticket(account)
        if not action_ticket:
            return False
        game_roles_url = MI_URL + "/binding/api/getUserGameRoles"
        game_roles_params = {"point_sn": "myb", "action_ticket": action_ticket}
        game_roles_headers = {"cookie": account.cookie}
        async with httpx.AsyncClient() as client:
            game_roles_req = await client.get(game_roles_url,
                                              headers=game_roles_headers,
                                              params=game_roles_params)
        if game_roles_req.status_code != 200:
            logger_file.error(f"获取绑定角色请求失败, 请检查传入参数, 返回状态码为{str(game_roles_req.status_code)}")
            return False
        game_roles_req = game_roles_req.json()
        if game_roles_req['retcode'] != 0:
            logger_file.error(f"获取绑定角色失败, 原因为{game_roles_req['message']}")
            return False
        game_roles_list = game_roles_req['data']['list']
        if not game_roles_list:
            logger_file.info('没有绑定任何角色')
            return False
        game_roles_new_list = []
        for game_roles in game_roles_list:
            game_roles_new_list.append(GameInfo.parse_obj(game_roles))
        account.game_list = game_roles_new_list
        return account
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_address(account: UserInfo) -> Union[bool, UserInfo]:
    """
    获取收货地址
    需要account_id与cookie_token
    """
    try:
        if account.cookie_token == "" or account.account_id == "":
            logger_file.warning("缺少cookie_token或account_id，请重新获取cookie")
            return False
        address_url = MI_URL + '/account/address/list'
        address_headers = {
            "Cookie": account.cookie,
        }
        async with httpx.AsyncClient() as client:
            address_list_req = await client.get(address_url, headers=address_headers)
        if address_list_req.status_code != 200:
            logger_file.error(f"请求出错, 请求状态码为: {str(address_list_req.status_code)}")
            return False
        address_list_req = address_list_req.json()
        if address_list_req['data'] is None:
            logger_file.error(f"获取出错, 错误原因为: {address_list_req['message']}")
            return False
        address_new_list = []
        for address_data in address_list_req['data']['list']:
            address_new_list.append(AddressInfo.parse_obj(address_data))
        account.address_list = address_new_list
        return account
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_goods_biz() -> Union[bool, Optional[List[List]]]:
    """
    获取商品分区列表
    """
    try:
        goods_biz_url = MI_URL + '/mall/v1/web/goods/list'
        goods_biz_params = {
            "app_id": 1,
            "point_sn": "myb",
            "page_size": 20,
            "page": 1,
            "game": '',
        }
        async with httpx.AsyncClient() as client:
            goods_biz_req = await client.get(goods_biz_url, params=goods_biz_params)
            if goods_biz_req.status_code != 200:
                logger_file.error(f"获取商品分区列表请求失败, 返回状态码为{str(goods_biz_req.status_code)}")
                return False
            goods_biz_data = goods_biz_req.json()['data']
            goods_biz_map = map(lambda x: [x['name'], x['key']], goods_biz_data['games'])
            return list(filter(lambda x: x[1] != 'all', goods_biz_map))
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.exception(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_goods_list(game_type: str, cookie='') -> Union[bool, Optional[List[GoodsInfo]]]:
    """
    获取商品列表
    """
    try:
        goods_list_url = MI_URL + '/mall/v1/web/goods/list'
        goods_list_params = {
            "app_id": 1,
            "point_sn": "myb",
            "page_size": 20,
            "page": 1,
            # '全部商品':'', '崩坏3':'bh3', '原神':'hk4e', '崩坏：星穹铁道':'hkrpg'
            # '崩坏学园2':'bh2', '未定事件簿':'nxx', '米游社':'bbs'
            "game": game_type,
        }
        goods_list_headers = {
            "Cookie": cookie,
        }
        goods_list = []
        async with httpx.AsyncClient() as client:
            while True:
                goods_list_req = await client.get(goods_list_url, params=goods_list_params, headers=goods_list_headers)
                if goods_list_req.status_code != 200:
                    logger_file.error(f"获取商品列表请求失败, 返回状态码为{str(goods_list_req.status_code)}")
                    continue
                goods_list_data = goods_list_req.json()['data']
                goods_list += list(map(GoodsInfo.parse_obj, goods_list_data['list']))
                if goods_list_data['total'] > goods_list_params['page_size'] * goods_list_params['page']:
                    goods_list_params['page'] += 1
                else:
                    break
        return goods_list
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.exception(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_goods_detail(goods_id: str) -> Union[bool, Optional[GoodsInfo]]:
    """
    按需要获取礼物详情
    """
    try:
        goods_detail_url = MI_URL + "/mall/v1/web/goods/detail"
        goods_detail_params = {
            "app_id": 1,
            "point_sn": "myb",
            "goods_id": goods_id,
        }
        async with httpx.AsyncClient() as client:
            goods_detail_req = await client.get(goods_detail_url, params=goods_detail_params)
        if goods_detail_req.status_code != 200:
            logger_file.error(f"获取商品详情请求失败, 返回状态码为{str(goods_detail_req.status_code)}")
            return False
        goods_detail_data = goods_detail_req.json()
        if goods_detail_data["data"] is None:
            logger_file.debug(f"获取商品详情失败, 错误信息为{goods_detail_data['message']}")
            return False
        return GoodsInfo.parse_obj(goods_detail_data["data"])
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_point(account: UserInfo) -> Union[bool, Optional[int]]:
    """
    获取米游币数量
    需要stoken与stuid
    """
    try:
        if account.stoken == "" or account.stuid == "":
            logger_file.warning("缺少stoken或stuid，请重新获取cookie")
            return False
        point_url = BBS_URL + '/apihub/sapi/getUserMissionsState'
        point_headers = {
            'Cookie': account.cookie,
        }
        async with httpx.AsyncClient() as client:
            point_req = await client.get(point_url, headers=point_headers)
        if point_req.status_code != 200:
            logger_file.error(f"获取米游币数量失败, 返回状态码为{str(point_req.status_code)}")
            return False
        point_req = point_req.json()
        if point_req['retcode'] != 0:
            logger_file.error(f"获取米游币数量失败, 原因为{point_req['message']}")
            return False
        return point_req['data']['total_points']
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

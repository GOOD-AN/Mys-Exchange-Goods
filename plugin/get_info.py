"""
米游社兑换所需信息获取
"""
import json
import os
import re
import sys
import time
from math import inf

import httpx
import pyperclip

import tools.global_var as gl
from tools import UserInfo, AddressInfo, ClassEncoder, GoodsInfo, GAME_NAME, MYS_CHANNEL
from tools import update_cookie, get_goods_detail, check_game_roles, get_point


def select_user(select_user_data: dict):
    """
    选择用户
    """
    try:
        print("当前已有用户有：")
        select_user_data_key = list(select_user_data)
        for mys_id in select_user_data_key:
            print(f"1. {mys_id}")
        select_user_id = 0
        while True:
            select_id = input("请输入选择用户的序号: ")
            if select_id.isdigit() and 0 < int(select_id) <= len(select_user_data_key):
                select_user_id = select_user_data_key[int(select_id) - 1]
                print(f"选择用户为: {select_user_id}")
                break
            else:
                print("输入序号有误, 请重新输入")
                continue
        if select_user_id == 0:
            return None
        return select_user_data[select_user_id]
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


async def get_cookie():
    """
    https://user.mihoyo.com/#/login/captcha
    获取app端cookie
    参考:
    https://bbs.tampermonkey.net.cn/thread-1040-1-1.html
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/login.py
    """
    try:
        login_url = 'https://user.mihoyo.com/#/login/captcha'
        print(f"请在浏览器打开{login_url}, 输入手机号后获取验证码, 但不要登录, 然后在下方按提示输入数据。")
        try:
            pyperclip.copy(login_url)
            print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        except Exception:
            print("无法复制地址到剪贴板, 请手动复制")
        mobile = input("请输入手机号: ")
        mobile_captcha = input("请输入验证码: ")
        login_user_url_one = gl.WEB_URL + "/Api/login_by_mobilecaptcha"
        login_user_form_data_one = {
            "mobile": mobile,
            "mobile_captcha": mobile_captcha,
            "source": "user.mihoyo.com"
        }
        # 获取第一个 cookie
        async with httpx.AsyncClient() as client:
            login_user_req_one = await client.post(login_user_url_one, data=login_user_form_data_one)
        login_user_cookie_one = login_user_req_one.cookies
        if "login_ticket" not in login_user_cookie_one:
            print("缺少'login_ticket'字段, 请重新获取")
            return False
        if "login_uid" not in login_user_cookie_one:
            mys_uid = login_user_req_one.json()['data']['account_info']['account_id']
        else:
            mys_uid = login_user_cookie_one['login_uid']
        if mys_uid is None:
            print("缺少'uid'字段, 请重新获取")
            return False

        # 获取 stoken
        user_stoken_url = gl.MI_URL + "/auth/api/getMultiTokenByLoginTicket"
        user_stoken_params = {
            "login_ticket": login_user_cookie_one['login_ticket'],
            "token_types": 3,
            "uid": mys_uid
        }
        async with httpx.AsyncClient() as client:
            user_stoken_req = await client.get(user_stoken_url, params=user_stoken_params)
        user_stoken_data = None
        if user_stoken_req.status_code == 200:
            user_stoken_data = user_stoken_req.json()["data"]["list"][0]["token"]
        if user_stoken_data is None:
            print("stoken获取失败, 请重新获取")
            return False

        # 获取第二个 cookie
        print("重新在此页面(刷新或重新打开)获取验证码, 依旧不要登录, 在下方输入数据。")
        try:
            pyperclip.copy(login_url)
            print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        except Exception:
            print("无法复制地址到剪贴板, 请手动复制")
        mobile_captcha = input("请输入第二次验证码: ")
        login_user_url_two = gl.MI_URL + "/account/auth/api/webLoginByMobile"
        login_user_form_data_two = {
            "is_bh2": False,
            "mobile": mobile,
            "captcha": mobile_captcha,
            "action_type": "login",
            "token_type": 6
        }
        async with httpx.AsyncClient() as client:
            login_user_req_two = await client.post(login_user_url_two, json=login_user_form_data_two)
        login_user_cookie_two = login_user_req_two.cookies
        if "cookie_token" not in login_user_cookie_two:
            print("缺少'cookie_token'字段, 请重新获取")
            return False
        uer_cookie = ""
        for key, value in login_user_cookie_two.items():
            uer_cookie += key + "=" + value + ";"
        uer_cookie += "login_ticket=" + login_user_cookie_one['login_ticket'] + ";"
        uer_cookie += "stoken=" + user_stoken_data + ";"
        uer_cookie += "stuid=" + login_user_cookie_two['account_id'] + ";"
        return uer_cookie, login_user_cookie_two['account_id']
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_channel_level(account: UserInfo):
    """
    获取频道等级
    """
    try:
        if account.stoken == "":
            print("缺少stoken，请重新获取cookie")
            return False
        channel_level_url = gl.BBS_URL + '/user/api/getUserFullInfo'
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
            print(f"获取频道等级失败, 返回状态码为: {channel_level_req.status_code}")
            return False
        channel_level_data = channel_level_req.json()
        if channel_level_data['retcode'] != 0:
            print(f"获取频道等级失败, 错误信息为: {channel_level_data['message']}")
            return False
        channel_data_dict = {}
        for channel_data in channel_level_data['data']['user_info']['level_exps']:
            channel_data_dict[channel_data['game_id']] = channel_data['level']
        return channel_data_dict
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_address(account: UserInfo):
    """
    获取收货地址
    需要account_id与cookie_token
    """
    try:
        if account.cookie_token == "":
            print("缺少cookie_token，请重新获取cookie")
            return False
        address_url = gl.MI_URL + '/account/address/list'
        address_headers = {
            "Cookie": account.cookie,
        }
        async with httpx.AsyncClient() as client:
            address_list_req = await client.get(address_url, headers=address_headers)
        if address_list_req.status_code != 200:
            print(f"请求出错, 请求状态码为: {str(address_list_req.status_code)}")
            return False
        address_list_req = address_list_req.json()
        if address_list_req['data'] is None:
            print(f"获取出错, 错误原因为: {address_list_req['message']}")
            return False
        address_new_list = []
        for address_data in address_list_req['data']['list']:
            address_new_dict = {'address_id': address_data['id'],
                                'connect_name': address_data['connect_name'],
                                'connect_areacode': address_data['connect_areacode'],
                                'connect_mobile': address_data['connect_mobile'],
                                'province_name': address_data['province_name'],
                                'city_name': address_data['city_name'],
                                'county_name': address_data['county_name'],
                                'addr_ext': address_data['addr_ext']}
            address_new_list.append(AddressInfo(address_new_dict))
        return address_new_list
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def select_goods(account: UserInfo, goods_num, goods_class_list, user_point, game_biz):
    """
    选择商品
    需要账户信息
    查询某商品该账户是否兑换, 需要account_id与cookie_token
    """
    try:
        while True:
            goods_id_in = set(re.split(r'\s+', input(
                "请输入需要抢购的商品序号, 以空格分开, 将忽略输入错误的序号(请注意现有米游币是否足够): ").rstrip(
                ' ')))
            if '' not in goods_id_in:
                goods_select_dict = {}
                goods_point = 0
                old_data = {}
                if os.path.exists(os.path.join(gl.DATA_PATH, 'exchange_list.json')):
                    with open(os.path.join(gl.DATA_PATH, 'exchange_list.json'), "r", encoding="utf-8") as exchange_file:
                        old_data = json.load(exchange_file)
                for goods_id in goods_id_in:
                    if goods_id.isdigit() and 0 < int(goods_id) < goods_num:
                        now_goods = goods_class_list[int(goods_id) - 1]
                        if account.mys_uid + now_goods.goods_id in old_data:
                            print(f"商品{now_goods.goods_name}已经在兑换列表中, 跳过", end=", ")
                            print("如需修改信息, 请稍后使用修改兑换信息功能修改")
                            continue
                        if 1 in now_goods.goods_rule:
                            goods_channel = now_goods.goods_rule[1][0].split(":")[0]
                            limit_level = now_goods.goods_rule[1][0].split(":")[1]
                            if account.channel_dict[goods_channel] < int(limit_level):
                                print(f"商品{now_goods.goods_name}兑换要求频道{MYS_CHANNEL[goods_channel]}等级为: {limit_level}, "
                                      f"当前频道等级为{account.channel_dict[goods_channel]}, 等级不足, 跳过兑换")
                                print("请前往米游社APP完成任务提升等级, 如信息错误或需要更新频道信息, 请稍后使用更新频道信息功能")
                                continue
                        now_goods_dict = {
                            "mys_uid": account.mys_uid,
                            "goods_id": now_goods.goods_id,
                            "goods_name": now_goods.goods_name,
                            "exchange_time": now_goods.goods_time,
                            "game_id": account.mys_uid
                        }
                        limit_level = inf
                        if 2 in now_goods.goods_rule:
                            limit_level = int(now_goods.goods_rule[2][0])
                        select_account_game = []
                        if now_goods.game_biz != 'bbs_cn':
                            for account_game in account.game_list:
                                if account_game.game_biz == game_biz and account_game.game_level >= limit_level:
                                    select_account_game.append(account_game)
                            if not select_account_game:
                                print(f"商品{now_goods.goods_name}兑换要求{GAME_NAME[game_biz]}等级为: {limit_level}, "
                                      f"未找到符合条件的账号, 跳过兑换")
                                print("请前往米游社APP绑定满足要求的账号, 如信息错误或需要更新绑定信息, 请稍后使用更新游戏账号信息功能")
                                continue
                        if now_goods.game_biz != 'bbs_cn' and now_goods.goods_type == 2:
                            account_game_num = 1
                            for account_game in select_account_game:
                                print("-" * 25)
                                print(f"账户序号{account_game_num}")
                                print(f"账户名称: {account_game.game_nickname}")
                                print(f"账户UID: {account_game.game_uid}")
                                print(f"账户等级: {account_game.game_level}")
                                print(f"账户区服: {account_game.game_region_name}")
                                account_game_num += 1
                            while True:
                                select_game_id = input(
                                    f"因商品{now_goods.goods_name}为虚拟物品, 请选择需要接收奖励的账号序号"
                                    f"(已跳过不符合最低等级限制的账号): ")
                                if select_game_id.isdigit() and 0 < int(select_game_id) < account_game_num:
                                    now_goods_dict['game_id'] = select_account_game[int(select_game_id) - 1].game_uid
                                    break
                                else:
                                    print("输入序号错误, 请重新输入")
                        exchange_num = 1
                        if int(now_goods.goods_limit) > 1:
                            while True:
                                exchange_num = input(
                                    f"请输入商品{now_goods.goods_name}的兑换数量, 当前限购数量为{now_goods.goods_limit}: ")
                                if exchange_num.isdigit() and 0 < int(exchange_num) <= int(now_goods.goods_limit):
                                    exchange_num = int(exchange_num)
                                    break
                                else:
                                    print("输入数量错误, 请重新输入")
                        now_goods_dict['exchange_num'] = exchange_num
                        goods_select_dict[account.mys_uid + now_goods.goods_id] = now_goods_dict
                        goods_point += now_goods.goods_price * exchange_num
                if user_point != -1 and user_point < goods_point:
                    print(f"当前米游币不足, 当前米游币数量: {user_point}, 所需米游币数量: {goods_point}")
                    choice = input("是否继续选择商品, 取消将返回重新选择(默认为Y)(Y/N): ")
                    if choice in ('n', 'N'):
                        continue
                old_data.update(goods_select_dict)
                with open(os.path.join(gl.DATA_PATH, 'exchange_list.json'), "w", encoding="utf-8") as f:
                    json.dump(old_data, f, ensure_ascii=False, indent=4)
                gl.EXCHANGE_DICT = old_data
                break
            else:
                print("未选择任何商品")
                choice = input("是否重新选择商品(默认为Y)(Y/N): ")
                if choice in ('n', 'N'):
                    break
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_goods_list(account: UserInfo, use_type: str = "set"):
    """
    获取商品列表
    需要账户信息
    查询某商品该账户是否兑换, 需要account_id与cookie_token
    """
    try:
        if use_type == "set" and account.mys_uid == "" and account.cookie == "":
            print("请先获取账户信息")
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""查询商品列表菜单
1.全部商品
2.崩坏3
3.原神
4.崩坏学园2
5.未定事件簿
6.米游社
0.返回上一级""")
            game_choice = input("请输入需要查询的序号: ")
            game_type_dict = {
                "1": "",
                "2": "bh3",
                "3": "hk4e",
                "4": "bh2",
                "5": "nxx",
                "6": "bbs",
            }
            if game_choice == "0":
                return None
            if game_choice not in game_type_dict:
                input("输入有误, 请重新输入(回车以返回)")
                continue
            goods_list_url = gl.MI_URL + '/mall/v1/web/goods/list'
            goods_list_params = {
                "app_id": 1,
                "point_sn": "myb",
                "page_size": 20,
                "page": 1,
                # '全部商品':'', '崩坏3':'bh3', '原神':'hk4e'
                # '崩坏学园2':'bh2', '未定事件簿':'nxx', '米游社':'bbs'
                "game": game_type_dict[game_choice],
            }
            goods_list_headers = {
                "Cookie": account.cookie,
            }
            user_point = -1
            if use_type == "set" and account.stoken != "" and account.stuid != "":
                user_point = await get_point(account)
            goods_class_list = []
            goods_num = 1
            async with httpx.AsyncClient() as client:
                while True:
                    goods_list_req = await client.get(goods_list_url, params=goods_list_params,
                                                      headers=goods_list_headers)
                    if goods_list_req.status_code != 200:
                        print(f"获取礼物列表失败, 请重试, 返回状态码为{str(goods_list_req.status_code)}")
                        return False
                    goods_list = goods_list_req.json()["data"]
                    for goods_data in goods_list["list"]:
                        goods_class = GoodsInfo()
                        # unlimit 为 False 表示兑换总数量有限
                        # next_num 表示下次兑换总数量
                        # total 表示当前可兑换总数量
                        if not goods_data['unlimit'] and goods_data['next_num'] == 0 and goods_data['total'] == 0 \
                                or goods_data['account_exchange_num'] == goods_data['account_cycle_limit']:
                            continue
                        game_biz, goods_type, goods_rule_list, exchange_time = await get_goods_detail(
                            goods_data['goods_id'])
                        goods_rule = {}
                        for goods_rule_data in goods_rule_list:
                            goods_rule[goods_rule_data['rule_id']] = goods_rule_data['values']
                        print("-" * 25)
                        print(f"商品序号: {goods_num}")
                        print(f"商品名称: {goods_data['goods_name']}")
                        print(f"商品价格: {goods_data['price']} 米游币")
                        goods_class.goods_id = goods_data['goods_id']
                        goods_class.goods_name = goods_data['goods_name']
                        goods_class.goods_price = goods_data['price']
                        goods_class.goods_type = goods_type
                        goods_class.game_biz = game_biz
                        goods_class.goods_rule = goods_rule
                        if goods_data['total'] == 0 and goods_data['next_num'] == 0:
                            print("商品库存: 无限")
                            goods_class.goods_num = -1
                        else:
                            goods_class.goods_num = goods_data['next_num'] or goods_data['total']
                            print(f"商品库存: {goods_class.goods_num}")
                        if goods_data['next_time'] == 0:
                            print("商品兑换时间: 任何时段")
                            goods_class.goods_time = -1
                        else:
                            print(f"商品兑换时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exchange_time))}")
                            goods_class.goods_time = exchange_time
                        # month 为每月限购
                        if goods_data["account_cycle_type"] == "forever":
                            print(f"每人限购: {goods_data['account_cycle_limit']} 个")
                        else:
                            print(f"本月限购: {goods_data['account_cycle_limit']} 个")
                        goods_class.goods_limit = goods_data['account_cycle_limit']
                        goods_class_list.append(goods_class)
                        goods_num += 1
                    if goods_list['total'] > goods_list_params['page'] * goods_list_params['page_size']:
                        goods_list_params['page'] += 1
                    else:
                        break
            if not goods_class_list:
                input("没有可兑换的商品(回车以返回)")
                continue
            if use_type == "set":
                await select_goods(account, goods_num, goods_class_list, user_point, game_biz)
            return True
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_user_info():
    """
    获取用户信息
    """
    try:
        user_info_json = {}
        user_cookie, mys_uid = await get_cookie()
        new_user = UserInfo([mys_uid, user_cookie])
        user_info_json['mys_uid'] = mys_uid
        user_info_json['cookie'] = user_cookie
        print("等待获取其他信息")
        channel_data_dict = await get_channel_level(new_user)
        game_info_list = await check_game_roles(new_user)
        address_list = await get_address(new_user)
        user_info_json['game_list'] = []
        user_info_json['address_list'] = []
        if game_info_list:
            user_info_json['game_list'] = game_info_list
            new_user.game_list = game_info_list
        if address_list:
            user_info_json['address_list'] = address_list
            new_user.address_list = address_list
        if channel_data_dict:
            user_info_json['channel_dict'] = channel_data_dict
            new_user.channel_dict = channel_data_dict
        if user_info_json:
            if not os.path.exists(gl.USER_DATA_PATH):
                os.makedirs(gl.USER_DATA_PATH)
            with open(os.path.join(gl.USER_DATA_PATH, f"{mys_uid}.json"), 'w', encoding='utf-8') as f:
                json.dump(user_info_json, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                gl.USER_DICT[mys_uid] = new_user
        return new_user
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def info_menu():
    """
    开始获取信息任务
    """
    try:
        account = UserInfo(None)
        if gl.USER_DICT:
            account = select_user(gl.USER_DICT)
            input("按回车键继续")
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""获取信息菜单
选择功能:
1. 获取账户信息
2. 查询设置兑换商品
3. 查询当前米游币数量
4. 更新Cookie
5. 更新游戏账号信息
6. 更新收货地址信息
7. 更新频道等级信息
8. 重新选择账户
0. 返回主菜单""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                new_account = await get_user_info()
                if new_account:
                    account = new_account
                    print(f"获取账户信息成功, 已切换用户为{account.mys_uid}")
                else:
                    print("获取账户信息失败")
            elif select_function == "2":
                select_function = input("1. 仅获取商品\n2. 获取并设置商品: ")
                if select_function == "1":
                    await get_goods_list(account, "get")
                elif select_function == "2":
                    await get_goods_list(account, "set")
            elif select_function == "3":
                now_point = await get_point(account)
                if now_point:
                    print(f"当前米游币数量: {now_point}")
                else:
                    print("未获取到米游币数量")
            elif select_function == "4":
                new_cookie_token = await update_cookie(account)
                if new_cookie_token:
                    account.cookie = re.sub(account.cookie_token, new_cookie_token, account.cookie)
                    with open(os.path.join(gl.USER_DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("cookie更新成功")
            elif select_function == "5":
                game_info_list = await check_game_roles(account)
                if game_info_list:
                    account.game_list = game_info_list
                    with open(os.path.join(gl.USER_DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("更新游戏账号信息成功")
                else:
                    print("未获取到游戏账号信息")
            elif select_function == "6":
                address_list = await get_address(account)
                if address_list:
                    account.address_list = address_list
                    with open(os.path.join(gl.USER_DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("更新收货地址信息成功")
                else:
                    print("未获取到收货地址信息")
            elif select_function == "7":
                channel_data_dict = await get_channel_level(account)
                if channel_data_dict:
                    account.channel_dict = channel_data_dict
                    with open(os.path.join(gl.USER_DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("更新频道等级信息成功")
            elif select_function == "8":
                if gl.USER_DICT:
                    account = select_user(gl.USER_DICT)
                else:
                    print("暂无账户信息, 请先获取账户信息")
            elif select_function == "0":
                return
            else:
                input("输入有误, 请重新输入(回车以返回)")
            input("按回车键继续")
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False

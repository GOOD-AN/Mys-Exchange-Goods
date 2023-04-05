"""
米游社兑换所需信息获取
"""
import json
import os
import sys
import time

import httpx
import pyperclip

import tools.global_var as gl
from tools import UserInfo, AddressInfo, ClassEncoder
from tools import write_config_file, update_cookie, get_gift_detail, check_game_roles, get_point


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
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/login.py
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


async def get_address(account: UserInfo):
    """
    获取收货地址
    需要account_id与cookie_token
    """
    try:
        if account.cookie == "":
            print("请先获取Cookie")
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


def get_gift_list():
    """
    获取商品列表
    查询某商品该账户是否兑换, 需要account_id与cookie_token, 非必须, 错误也可继续
    """
    try:
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
            gift_list_url = gl.MI_URL + '/mall/v1/web/goods/list'
            gift_list_params = {
                "app_id": 1,
                "point_sn": "myb",
                "page_size": 20,
                "page": 1,
                # '全部商品':'', '崩坏3':'bh3', '原神':'hk4e'
                # '崩坏学园2':'bh2', '未定事件簿':'nxx', '米游社':'bbs'
                "game": game_type_dict[game_choice],
            }
            gift_list_headers = {
                "Cookie": gl.MI_COOKIE,
            }
            gift_id_list = []
            gift_point_list = []
            gift_num = 1
            while True:
                gift_list_req = httpx.get(gift_list_url,
                                          params=gift_list_params,
                                          headers=gift_list_headers)
                if gift_list_req.status_code != 200:
                    print(f"获取礼物列表失败, 请重试, 返回状态码为{str(gift_list_req.status_code)}")
                    return False
                gift_list = gift_list_req.json()["data"]
                for gift_data in gift_list["list"]:
                    # unlimit 为 False 表示兑换总数量有限
                    # next_num 表示下次兑换总数量
                    # total 表示当前可兑换总数量
                    if not gift_data['unlimit'] and gift_data['next_num'] == 0 and gift_data['total'] == 0 \
                            or gift_data['account_exchange_num'] == gift_data['account_cycle_limit']:
                        continue
                    print("-" * 25)
                    print(f"商品序号: {gift_num}")
                    print(f"商品名称: {gift_data['goods_name']}")
                    print(f"商品价格: {gift_data['price']} 米游币")
                    if gift_data['total'] == 0 and gift_data['next_num'] == 0:
                        print("商品库存: 无限")
                    else:
                        print(f"商品库存: {gift_data['next_num'] or gift_data['total']}")
                    if gift_data['next_time'] == 0:
                        print("商品兑换时间: 任何时段")
                    else:
                        gift_time = time.localtime(get_gift_detail(gift_data['goods_id']))
                        print(f"商品兑换时间: {time.strftime('%Y-%m-%d %H:%M:%S', gift_time)}")
                    # month 为每月限购
                    if gift_data["account_cycle_type"] == "forever":
                        print(f"每人限购: {gift_data['account_cycle_limit']} 个")
                    else:
                        print(f"本月限购: {gift_data['account_cycle_limit']} 个")
                    gift_num += 1
                    gift_id_list.append(gift_data['goods_id'])
                    gift_point_list.append(gift_data['price'])
                if gift_list['total'] > gift_list_params['page'] * gift_list_params['page_size']:
                    gift_list_params['page'] += 1
                else:
                    break
            if not gift_id_list:
                input("没有可兑换的商品(回车以返回)")
                continue
            while True:
                gift_id_in = set(
                    input(
                        "请输入需要抢购的商品序号, 以空格分开, 将忽略输入错误的序号(请注意现有米游币是否足够): ").split(
                        ' '))
                if '' not in gift_id_in:
                    gift_id_write = ''
                    gift_point = 0
                    for gift_id in gift_id_in:
                        if gift_id.isdigit() and 0 < int(gift_id) < gift_num:
                            gift_id_write += gift_id_list[int(gift_id) - 1] + ','
                            gift_point += gift_point_list[int(gift_id) - 1]
                    user_point = get_point()
                    if user_point and user_point < gift_point:
                        print(f"当前米游币不足, 当前米游币: {user_point}, 所需米游币: {gift_point}")
                        choice = input("是否继续选择商品, 取消将返回重新选择(默认为Y)(Y/N): ")
                        if choice in ('n', 'N'):
                            continue
                    if gl.INI_CONFIG.get('exchange_info', 'good_id'):
                        while True:
                            print("检测到已存在商品id, 需要的操作是\n1.追加\n2.替换\n3.删除\n4.取消")
                            choice = input("请输入选项: ")
                            if choice == '1':
                                gift_id_write += gl.INI_CONFIG.get('exchange_info', 'good_id')
                                gift_id_write_set = set(gift_id_write.split(','))
                                gift_id_write = ','.join(gift_id_write_set)
                                write_config_file('exchange_info', 'good_id', gift_id_write)
                            elif choice == '2':
                                gift_id_write = gift_id_write.rstrip(',')
                                write_config_file('exchange_info', 'good_id', gift_id_write)
                            elif choice == '3':
                                write_config_file('exchange_info', 'good_id', '')
                            elif choice == '4':
                                break
                            else:
                                input("输入有误, 请重新输入(回车以返回)")
                                continue
                            break
                    else:
                        gift_id_write = gift_id_write.rstrip(',')
                        write_config_file('exchange_info', 'good_id', gift_id_write)
                    break
                else:
                    print("未选择任何商品")
                    choice = input("是否重新选择商品(默认为Y)(Y/N): ")
                    if choice in ('n', 'N'):
                        break
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
        print("等待获取游戏账户与收货地址信息")
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
        if user_info_json:
            if not os.path.exists(gl.DATA_PATH):
                os.makedirs(gl.DATA_PATH)
            with open(os.path.join(gl.DATA_PATH, f"{mys_uid}.json"), 'w', encoding='utf-8') as f:
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
7. 重新选择账户
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
                print("暂未开放")
                # get_gift_list()
                # continue
            elif select_function == "3":
                now_point = await get_point(account)
                if now_point:
                    print(f"当前米游币数量: {now_point}")
                else:
                    print("未获取到米游币数量")
            elif select_function == "4":
                await update_cookie(account)
            elif select_function == "5":
                game_info_list = await check_game_roles(account)
                if game_info_list:
                    account.game_list = game_info_list
                    with open(os.path.join(gl.DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("更新游戏账号信息成功")
                else:
                    print("未获取到游戏账号信息")
            elif select_function == "6":
                address_list = await get_address(account)
                if address_list:
                    account.address_list = address_list
                    with open(os.path.join(gl.DATA_PATH, f"{account.mys_uid}.json"), 'w', encoding='utf-8') as f:
                        json.dump(account, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
                    print("更新收货地址信息成功")
                else:
                    print("未获取到收货地址信息")
            elif select_function == "7":
                account = select_user(gl.USER_DICT)
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

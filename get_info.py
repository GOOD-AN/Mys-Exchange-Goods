"""
米游社兑换所需信息获取
"""
import sys
import os
import time
import pyperclip
import requests

from tools import write_config_file, update_cookie, get_gift_detail, check_game_roles, get_point, GAME_NAME, YS_SERVER
import tools.global_var as gl


def get_app_cookie():
    """
    https://user.mihoyo.com/#/login/captcha
    获取app端cookie
    参考:
    https://bbs.tampermonkey.net.cn/thread-1040-1-1.html
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/login.py
    """
    try:
        login_url = 'https://user.mihoyo.com/#/login/captcha'
        print(f"请在浏览器打开{login_url}, 输入手机号后获取验证码，但不要登录，然后在下方按提示输入数据。")
        pyperclip.copy(login_url)
        print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        mobile = input("请输入手机号: ")
        mobile_captcha = input("请输入验证码: ")
        login_user_url_one = gl.WEB_URL + "/Api/login_by_mobilecaptcha"
        login_user_form_data_one = {
            "mobile": mobile,
            "mobile_captcha": mobile_captcha,
            "source": "user.mihoyo.com"
        }
        # 获取第一个 cookie
        login_user_req_one = requests.post(login_user_url_one, login_user_form_data_one)
        login_user_cookie_one = requests.utils.dict_from_cookiejar(login_user_req_one.cookies)
        if "login_ticket" not in login_user_cookie_one:
            print("缺少'login_ticket'字段，请重新获取")
            return False
        if "login_uid" not in login_user_cookie_one:
            mys_uid = login_user_req_one.json()['data']['account_info']['account_id']
        else:
            mys_uid = login_user_cookie_one['login_uid']
        if mys_uid is None:
            print("缺少'uid'字段，请重新获取")
            return False

        # 获取 stoken
        user_stoken_url = gl.MI_URL + "/auth/api/getMultiTokenByLoginTicket"
        user_stoken_params = {
            "login_ticket": login_user_cookie_one['login_ticket'],
            "token_types": 3,
            "uid": mys_uid
        }
        user_stoken_req = requests.get(user_stoken_url, params=user_stoken_params)
        user_stoken_data = None
        if user_stoken_req.status_code == 200:
            user_stoken_data = user_stoken_req.json()["data"]["list"][0]["token"]
        if user_stoken_data is None:
            print("stoken获取失败，请重新获取")
            return False

        # 获取第二个 cookie
        print("重新在此页面(刷新或重新打开)获取验证码，依旧不要登录，在下方输入数据。")
        pyperclip.copy(login_url)
        print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        mobile_captcha = input("请输入第二次验证码: ")
        login_user_url_two = gl.MI_URL + "/account/auth/api/webLoginByMobile"
        login_user_form_data_two = {
            "is_bh2": False,
            "mobile": mobile,
            "captcha": mobile_captcha,
            "action_type": "login",
            "token_type": 6
        }
        login_user_req_two = requests.post(login_user_url_two, json=login_user_form_data_two)
        login_user_cookie_two = requests.utils.dict_from_cookiejar(login_user_req_two.cookies)
        if "cookie_token" not in login_user_cookie_two:
            print("缺少'cookie_token'字段，请重新获取")
            return False
        uer_cookie = ""
        for key, value in login_user_cookie_two.items():
            uer_cookie += key + "=" + value + ";"
        uer_cookie += "login_ticket=" + login_user_cookie_one['login_ticket'] + ";"
        uer_cookie += "stoken=" + user_stoken_data + ";"
        uer_cookie += "stuid=" + login_user_cookie_two['account_id'] + ";"

        # 写入文件
        if gl.INI_CONFIG.get('user_info', 'cookie'):
            is_overwrite = input("检测到已有cookie, 是否覆盖(默认Y)?(y/n): ")
            if is_overwrite in ('n', 'N'):
                input("取消写入, 按回车键返回")
                return
            write_config_file('user_info', 'cookie', uer_cookie)
        else:
            write_config_file('user_info', 'cookie', uer_cookie)
        print("cookie 写入成功")
        input("按回车键继续")
        return True
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def get_address():
    """
    获取收货地址
    需要account_id与cookie_token
    """
    try:
        if gl.MI_COOKIE == "":
            print("请先获取Cookie")
            input("按回车键继续")
            return False
        address_url = gl.MI_URL + '/account/address/list'
        address_headers = {
            "Cookie": gl.MI_COOKIE,
        }
        address_list_req = requests.get(address_url, headers=address_headers)
        if address_list_req.status_code != 200:
            print("请求出错，请稍后重试或联系项目负责人")
            input("按回车继续")
            return False
        address_list_req = address_list_req.json()
        if address_list_req['data'] is None:
            print(f"获取出错，错误原因为: {address_list_req['message']}")
            input("按回车继续")
            return False
        address_list = address_list_req["data"]["list"]
        address_id_list = []
        address_id = 1
        for address_data in address_list:
            print("-" * 35)
            print(f"第{address_id}个地址")
            print(f"省: {address_data['province_name']}")
            print(f"市: {address_data['city_name']}")
            print(f"区/县: {address_data['county_name']}")
            print(f"详细地址: {address_data['addr_ext']}")
            print(f"联系电话: {address_data['connect_areacode'] + address_data['connect_mobile']}")
            print(f"联系人: {address_data['connect_name']}")
            address_id += 1
            address_id_list.append(address_data['id'])
        while True:
            address_id_in = input("请输入需要写入的地址序号(暂只支持一个): ")
            if address_id_in == "":
                re_input = input("未输入地址序号, 是否重新输入(默认为Y)?(y/n): ")
            elif not address_id_in.isdigit() or address_id < int(address_id_in) or int(address_id_in) <= 0:
                re_input = input("地址序号输入错误, 是否重新输入(默认为Y)?(y/n): ")
            else:
                break
            if re_input in ('n', 'N'):
                input("取消写入, 按回车键返回")
                return
        if gl.INI_CONFIG.get('user_info', 'address_id'):
            is_cover = input("已存在地址序号, 是否覆盖(默认为Y)?(y/n): ")
            if is_cover in ('n', 'N'):
                input("取消写入, 按回车键返回")
                return
        write_config_file('user_info', 'address_id', address_id_list[int(address_id_in) - 1])
        print("地址写入成功")
        input("按回车键继续")
        return True
    except KeyboardInterrupt:
        print("强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def get_game_uid():
    """
    获取绑定游戏UID
    """
    try:
        if gl.MI_COOKIE == "":
            print("请先获取Cookie")
            input("按回车键继续")
            return False
        game_info_list = check_game_roles()
        if not game_info_list:
            return True
        game_uid_list = []
        game_uid_id = 1
        for game_info in game_info_list:
            print("-" * 25)
            print(f"第{game_uid_id}个账户")
            print(f"游戏名称: {GAME_NAME[game_info['game_biz']]}")
            print(f"游戏昵称: {game_info['nickname']}")
            print(f"游戏UID: {game_info['game_uid']}")
            print(f"游戏等级: {game_info['level']}")
            print(f"游戏区服: {YS_SERVER[game_info['region']]}")
            game_uid_id += 1
            game_uid_list.append(game_info['game_uid'])
        while True:
            game_uid_in = input("请输入需要写入的游戏UID序号(暂只支持一个): ")
            if game_uid_in == "":
                re_input = input("未输入游戏UID序号, 是否重新输入(默认为Y)?(y/n): ")
            elif not game_uid_in.isdigit() or game_uid_id < int(game_uid_in) or int(game_uid_in) <= 0:
                re_input = input("游戏UID序号输入错误, 是否重新输入(默认为Y)?(y/n): ")
            else:
                break
            if re_input in ('n', 'N'):
                input("取消写入, 按回车键返回")
                return
        if gl.INI_CONFIG.get('user_info', 'game_uid'):
            is_cover = input("已存在游戏UID, 是否覆盖(默认为Y)?(y/n): ")
            if is_cover in ('n', 'N'):
                input("取消写入, 按回车键返回")
                return
        write_config_file('user_info', 'game_uid', game_uid_list[int(game_uid_in) - 1])
        print("游戏UID写入成功")
        input("按回车键继续")
        return True
    except KeyboardInterrupt:
        print("强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def get_gift_list():
    """
    获取礼物列表
    查询该账户是否兑换, 需要account_id与cookie_token, 非必须, 错误也可继续
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""\
1.全部商品
2.崩坏3
3.原神
4.崩坏学园2
5.未定事件簿
6.米游社
0.返回上一级\
""")
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
                input("输入有误，请重新输入(回车以返回)")
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
                gift_list_req = requests.get(gift_list_url,
                                             params=gift_list_params,
                                             headers=gift_list_headers)
                if gift_list_req.status_code != 200:
                    return False
                gift_list = gift_list_req.json()["data"]
                for gift_data in gift_list["list"]:
                    # unlimit 为 False 表示兑换总数量有限
                    # next_num 表示下次兑换总数量
                    # total 表示当前可兑换总数量
                    if not gift_data['unlimit'] and gift_data['next_num'] == 0 and gift_data['total'] == 0 or gift_data[
                            'account_exchange_num'] == gift_data['account_cycle_limit']:
                        continue
                    print("------------")
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
            gift_id_in = set(input("请输入需要抢购的商品序号，以空格分开(请注意现有米游币是否足够): ").split(' '))
            if '' not in gift_id_in:
                gift_id_write = ''
                gift_point = 0
                for gift_id in gift_id_in:
                    if gift_id.isdigit() and 0 < int(gift_id) < gift_num:
                        gift_id_write += gift_id_list[int(gift_id) - 1] + ','
                        gift_point += gift_point_list[int(gift_id) - 1]
                user_point = get_point()
                if user_point and user_point < gift_point:
                    print(f"当前米游币不足，当前米游币: {user_point}，所需米游币: {gift_point}")
                    choice = input("是否继续选择商品, 取消将返回上级菜单(默认为继续Y/N): ")
                    if choice in ('n', 'N'):
                        return True
                if gl.INI_CONFIG.get('exchange_info', 'good_id'):
                    while True:
                        print("检测到已存在商品id，需要的操作是\n1.追加\n2.替换\n3.删除\n4.取消")
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
                            input("输入有误，请重新输入(回车以返回)")
                            continue
                        break
                else:
                    gift_id_write = gift_id_write.rstrip(',')
                    write_config_file('exchange_info', 'good_id', gift_id_write)
            else:
                print("未选择任何商品")
            input("按回车键继续")
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def info_main():
    """
    开始任务
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""选择功能:
1. 获取Cookie
2. 查询收货地址
3. 查询绑定游戏UID
4. 查询商品ID
5. 查询米游币
6. 更新Cookie
0. 返回主菜单""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                get_app_cookie()
            elif select_function == "2":
                get_address()
            elif select_function == "3":
                get_game_uid()
            elif select_function == "4":
                get_gift_list()
            elif select_function == "5":
                now_point = get_point()
                if now_point:
                    print(f"当前米游币: {now_point}")
                    input("按回车键继续")
            elif select_function == "6":
                update_cookie()
            elif select_function == "0":
                return
            else:
                input("输入有误，请重新输入(回车以返回)")
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False

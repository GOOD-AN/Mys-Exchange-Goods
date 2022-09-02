'''
米游社兑换所需信息获取
'''
import sys
import os
import platform
import configparser
import time
import requests

MAIN_VERSION = '0.0.1'
MI_URL = 'https://api-takumi.mihoyo.com'
WEB_URL = 'https://webapi.account.mihoyo.com'

MI_COOKIE = ""


def load_config():
    '''
    加载配置文件
    '''
    config = configparser.ConfigParser()
    try:
        config.read_file(open("config.ini", "r", encoding="utf-8"))
        return config
    except FileNotFoundError as err:
        print(err)


def get_address() -> None:
    '''
    获取收货地址(需登录验证)
    '''
    address_url = MI_URL + '/account/address/list'
    address_headers = {
        "Cookie": MI_COOKIE,
    }
    try:
        address_list_req = requests.get(address_url, headers=address_headers)
        address_list = address_list_req.json()["data"]["list"]
        address_id = 1
        address_id_list = {}
        for address_data in address_list:
            print(f"第{address_id}个地址")
            print(f"地址ID: {address_data['id']}")
            print(f"省: {address_data['province_name']}")
            print(f"市: {address_data['city_name']}")
            print(f"区/县: {address_data['county_name']}")
            print(f"详细地址: {address_data['addr_ext']}")
            print(f"联系电话: {address_data['connect_areacode']+address_data['connect_mobile']}")
            print(f"联系人: {address_data['connect_name']}")
            address_id += 1
        return None
    except Exception as e:
        print(e)
        return False


def get_gift_time(goods_id):
    '''
    获取礼物兑换时间
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
        if gift_detail['status'] == 'online':
            return int(gift_detail['next_time'])
        else:
            return int(gift_detail['sale_start_time'])
    except:
        return False


def get_gift_list():
    '''
    获取礼物列表
    '''
    try:
        while (True):
            os.system(CLEAR_TYPE)
            print("""\
1.全部商品
2.崩坏3
3.原神
4.崩坏学园2
5.未定事件簿
6.米游社
0.返回主菜单\
""")
            game_choice = input("请输入需要查询的序号: ")
            game_type = ""
            if game_choice == "2":
                game_type = "bh3"
            elif game_choice == "3":
                game_type = "hk4e"
            elif game_choice == "4":
                game_type = "bh2"
            elif game_choice == "5":
                game_type = "nxx"
            elif game_choice == "6":
                game_type = "bbs"
            elif game_choice == "0":
                return None
            else:
                input("输入有误，请重新输入(回车以返回)")
                continue
            gift_list_url = MI_URL + '/mall/v1/web/goods/list'
            gift_list_params = {
                "app_id": 1,
                "point_sn": "myb",
                "page_size": 20,
                "page": 1,
                # '全部商品':'', '崩坏3':'bh3', '原神':'hk4e'
                # '崩坏学园2':'bh2', '未定事件簿':'nxx', '米游社':'bbs'
                "game": game_type
            }
            gift_id_list = []
            gift_num = 1
            while (True):
                gift_list_req = requests.get(gift_list_url, params=gift_list_params)
                if (gift_list_req.status_code != 200):
                    return False
                gift_list = gift_list_req.json()["data"]
                for gift_data in gift_list["list"]:
                    # unlimit 为 False 表示兑换总数量有限
                    # next_num 表示下次兑换总数量
                    # total 表示当前可兑换总数量
                    if not gift_data['unlimit'] and gift_data['next_num'] == 0 and gift_data[
                            'total'] == 0:
                        continue
                    print("----------")
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
                        print(
                            f"商品兑换时间: {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(get_gift_time(gift_data['goods_id'])))}"
                        )
                    # month 为每月限购
                    if gift_data["account_cycle_type"] == "forever":
                        print(f"每人限购: {gift_data['account_cycle_limit']} 个")
                    else:
                        print(f"本月限购: {gift_data['account_cycle_limit']} 个")
                    gift_num += 1
                    gift_id_list.append(gift_data['goods_id'])
                if (gift_list['total'] > gift_list_params['page'] * gift_list_params['page_size']):
                    gift_list_params['page'] += 1
                else:
                    break
            gift_id_in = set(input("请输入需要抢购的商品序号，以空格分开(请注意现有米游币是否足够): ").split(' '))
            if '' not in gift_id_in:
                gift_id_write = ''
                for gift_id in gift_id_in:
                    gift_id_write += gift_id_list[int(gift_id) - 1] + ','
                if ini_config.get('exchange_info', 'good_id'):
                    while (True):
                        print("已存在商品id，需要的操作是\n1.追加\n2.替换\n3.删除\n4.取消")
                        choice = input("请输入选项: ")
                        if choice == '1':
                            gift_id_write += ini_config.get('exchange_info', 'good_id')
                            gift_id_write_set = set(gift_id_write.split(','))
                            gift_id_write = ','.join(gift_id_write_set)
                            ini_config.set('exchange_info', 'good_id', gift_id_write)
                            break
                        elif choice == '2':
                            gift_id_write = gift_id_write.rstrip(',')
                            ini_config.set('exchange_info', 'good_id', gift_id_write)
                            break
                        elif choice == '3':
                            ini_config.set('exchange_info', 'good_id', '')
                            break
                        elif choice == '4':
                            break
                        else:
                            input("输入有误，请重新输入(回车以返回)")
                else:
                    gift_id_write = gift_id_write.rstrip(',')
                    ini_config.set('exchange_info', 'good_id', gift_id_write)
                with open("config.ini", "w", encoding="utf-8") as config_file:
                    ini_config.write(config_file)
            input("按回车键继续")
    except Exception as err:
        print(err)
        input("按回车键继续")
        return False


def get_app_cookie():
    '''
    https://user.mihoyo.com/#/login/captcha
    获取app端cookie
    参考: 
    https://bbs.tampermonkey.net.cn/thread-1040-1-1.html
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/login.py
    '''
    try:
        print("请在浏览器打开https://user.mihoyo.com/#/login/captcha, 输入手机号后获取验证码，但不要登录，然后在下方按提示输入数据。")
        mobile = input("请输入手机号: ")
        mobile_captcha = input("请输入验证码: ")
        login_user_url_one = WEB_URL + "/Api/login_by_mobilecaptcha"
        login_user_form_data_one = {
            "mobile": mobile,
            "mobile_captcha": mobile_captcha,
            "source": "user.mihoyo.com"
        }
        # 获取第一个 cookie
        login_user_req_one = requests.post(login_user_url_one, login_user_form_data_one)
        login_user_cookie_one = requests.utils.dict_from_cookiejar(login_user_req_one.cookies)
        print(type(login_user_cookie_one))
        if "login_ticket" not in login_user_cookie_one:
            print("缺少'login_ticket'字段，请重新获取")
            return False
        mys_uid = None
        if "login_uid" not in login_user_cookie_one:
            mys_uid = login_user_req_one.json()['data']['account_info']['account_id']
        else:
            mys_uid = login_user_cookie_one['login_uid']
        if mys_uid is None:
            print("缺少'uid'字段，请重新获取")
            return False

        # 获取 stoken
        user_stoken_url = MI_URL + "/auth/api/getMultiTokenByLoginTicket"
        user_stoken_params = {
            "login_ticket": login_user_cookie_one['login_ticket'],
            "token_types": 3,
            "uid": mys_uid
        }
        user_stoken_req = requests.get(user_stoken_url, params=user_stoken_params)
        user_stoken_data = None
        if (user_stoken_req.status_code == 200):
            user_stoken_data = user_stoken_req.json()["data"]["list"][0]["token"]
        if user_stoken_data is None:
            print("stoken获取失败，请重新获取")
            return False

        # 获取第二个 cookie
        print("重新在此页面获取验证码，依旧不要登录，在下方输入数据。")
        mobile_captcha = input("请输入第二次验证码: ")
        login_user_url_two = MI_URL + "/account/auth/api/webLoginByMobile"
        login_user_form_data_two = {
            "is_bh2": False,
            "mobile": mobile,
            "captcha": mobile_captcha,
            "action_type": "login",
            "token_type": 6
        }
        login_user_req_two = requests.post(login_user_url_two, json=login_user_form_data_two)
        login_user_cookie_two = requests.utils.dict_from_cookiejar(login_user_req_two.cookies)
        print(login_user_req_two.json())
        print(login_user_cookie_two)
        if "cookie_token" not in login_user_cookie_two:
            print("缺少'cookie_token'字段，请重新获取")
            return False
        uer_cookie = ""
        for key in login_user_cookie_two:
            uer_cookie += key + "=" + login_user_cookie_two['key'] + ";"
        uer_cookie += "login_ticket=" + login_user_cookie_one['login_ticket'] + ";"
        uer_cookie += "stoken=" + user_stoken_data + ";"

        print(uer_cookie)
        # 写入文件
    except Exception as err:
        print(err)
        return False


def check_update():
    '''
    检查更新
    '''
    input("按回车键继续")
    return None


def start():
    '''
    开始任务
    '''
    try:
        while (True):
            os.system(CLEAR_TYPE)
            print("本项目查询商品ID可用")
            print("""选择功能:
1. 获取Cookie
2. 查询收货地址
3. 查询商品ID
4. 检查更新
0. 退出""")
            select_function = input("请输入选择功能的序号: ")
            os.system(CLEAR_TYPE)
            if select_function == "1":
                get_app_cookie()
            elif select_function == "2":
                get_address()
            elif select_function == "3":
                get_gift_list()
            elif select_function == "4":
                check_update()
            elif select_function == "0":
                sys.exit()
            else:
                input("输入有误，请重新输入(回车以返回)")
    except Exception as err:
        print(err)
        sys.exit()


if __name__ == '__main__':
    CLEAR_TYPE = ""
    if platform.system() == "Windows":
        CLEAR_TYPE = "cls"
    else:
        CLEAR_TYPE = "clear"
    ini_config = load_config()
    check_update()
    start()

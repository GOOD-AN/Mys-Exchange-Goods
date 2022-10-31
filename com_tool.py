'''
通用函数
'''
import hashlib
import os
import platform
import random
import re
import string
import sys
import time
import configparser
import ntplib
import requests

import global_var as gl

MAIN_VERSION = '1.0.0'
MYS_SALT = "PVeGWIZACpxXZ1ibMVJPi9inCY4Nd4y2"
MYS_SALT_TWO = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
MYS_SALT_WEB = "yUZ3s0Sna1IrSNfk29Vo6vRapdOyqyhB"


def check_plat():
    '''
    检查平台
    '''
    try:
        if platform.system() == "Windows":
            return "cls"
        return "clear"
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)
        sys.exit()


def load_config():
    '''
    加载配置文件
    '''
    config = configparser.ConfigParser()
    try:
        path = os.path.abspath(__file__)
        path = os.path.dirname(path) + '/config.ini'
        config.read_file(open(path, "r", encoding="utf-8"))
        return config
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)


def get_cookie_str(target):
    '''
    获取cookie字符串中相应的数据
    '''
    try:
        pattern_str = re.compile(target + '=(.*?);')
        result_str = pattern_str.search(gl.MI_COOKIE)
        if result_str:
            return result_str.group(1)
        return ''
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


def write_config_file(section, key, value):
    '''
    写入配置文件
    '''
    try:
        gl.INI_CONFIG.set(section, key, value)
        path = os.path.abspath(__file__)
        path = os.path.dirname(path) + '/config.ini'
        with open(path, "w", encoding="utf-8") as config_file:
            gl.INI_CONFIG.write(config_file)
            print("写入成功")
        gl.INI_CONFIG = load_config()
        if key == 'cookie':
            gl.MI_COOKIE = value
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")


def compare_version(old_version, new_version):
    '''
    版本号比较
    '''
    try:
        for o_v, n_v in zip(old_version, new_version):
            if o_v > n_v:
                return 1
            if o_v < n_v:
                return -1
        return 0
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)
        sys.exit()


def check_update():
    '''
    检查更新
    '''
    try:
        config_version = gl.INI_CONFIG.get('app', 'version')
        if MAIN_VERSION == config_version:
            print(f"当前程序版本为v{MAIN_VERSION}, 配置文件版本为v{config_version}")
            # 远程检查更新
            check_url = "https://fastly.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/update_log.json"
            check_info = requests.get(check_url).json()
            remote_least_version = check_info['least_version'].split('.')
            local_version = MAIN_VERSION.split('.')
            if compare_version(remote_least_version, local_version) == 1:
                print("版本过低, 程序将停止运行")
                time.sleep(3)
                sys.exit()
            remote_last_vesion = check_info['last_vesion'].split('.')
            if compare_version(local_version, remote_last_vesion) == -1:
                remote_update_log_list = check_info['update_log']
                print(f"当前程序版本为v{MAIN_VERSION}, 最新程序版本为v{remote_last_vesion}")
                print("当前非最新版本，建议更新")
                print("更新概览: ")
                for update_log in remote_update_log_list:
                    if compare_version(update_log['version'], remote_update_log_list) == 1:
                        print(f"版本: {update_log['version']}")
                        print(f"更新时间: {update_log['update_time']}")
                        print(f"更新说明: {update_log['update_content']}")
                    else:
                        print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
                        break
        else:
            print(f"当前程序版本为v{MAIN_VERSION}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
            print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
        input("按回车键继续")
        return None
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"检查更新失败, 原因为{err}")
        input("按回车键继续")
        return None


def get_time(ntp_enable, ntp_server):
    '''
    获取当前时间
    '''
    try:
        if not ntp_enable:
            return time.time()
        return ntplib.NTPClient().request(ntp_server).tx_time
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"网络时间获取失败, 原因为{err}, 转为本地时间")
        return time.time()


def md5_encode(text):
    '''
    md5加密
    '''
    try:
        md5_str = hashlib.md5()
        md5_str.update(text.encode('utf-8'))
        return md5_str.hexdigest()
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)
        sys.exit()


def get_new_ds(_b, _q):
    '''
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/tools.py
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/setting.py
    保留此函数以备后用
    '''
    try:
        t_param = str(int(time.time()))
        r_param = str(random.randint(100001, 200000))
        b_param = '传入参数, 待查明'
        q_param = '传入参数, 待查明'
        c_param = md5_encode(f"salt={MYS_SALT_TWO}&t={t_param}&r={r_param}&b={b_param}&q={q_param}")
        return f"{t_param},{r_param},{c_param}"
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)
        return None


def get_old_ds(web: bool):
    '''
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/tools.py
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/setting.py
    保留此函数以备后用
    '''
    if web:
        old_salt = MYS_SALT_WEB
    else:
        old_salt = MYS_SALT
    t_param = str(int(time.time()))
    r_param = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c_param = md5_encode(f'salt={old_salt}&t={t_param}&r={r_param}')
    return f"{t_param},{r_param},{c_param}"


def update_cookie():
    '''
    更新cookie
    需要stoken
    '''
    try:
        update_cookie_url = gl.MI_URL + "/auth/api/getCookieAccountInfoBySToken"
        update_cookie_url_params = {
            "uid": get_cookie_str("account_id"),
            "stoken": get_cookie_str("stoken")
        }
        print("开始更新cookie")
        update_cookie_url_req = requests.get(update_cookie_url, params=update_cookie_url_params)
        update_cookie_url_req = update_cookie_url_req.json()
        if update_cookie_url_req['data'] is None:
            print(f"获取出错，错误原因为: {update_cookie_url_req['message']}")
        new_mi_cookie = re.sub(get_cookie_str("cookie_token"),
                               update_cookie_url_req['data']['cookie_token'], gl.MI_COOKIE)
        write_config_file("user_info", "cookie", new_mi_cookie)
        input("cookie更新成功, 按回车键继续")
        return True
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def get_point():
    '''
    获取米游币数量
    需要stoken与stuid
    '''
    try:
        point_url = gl.BBS_URL + '/apihub/sapi/getUserMissionsState'
        point_hearders = {
            'Cookie': gl.MI_COOKIE,
        }
        point_req = requests.get(point_url, headers=point_hearders)
        if point_req.status_code != 200:
            print(f"获取米游币数量失败, 返回状态码为{point_req.status_code}")
            input("按回车键继续")
            return False
        point_req = point_req.json()
        if point_req['retcode'] != 0:
            print(f"获取米游币数量失败, 原因为{point_req['message']}")
            input("按回车键继续")
            return False
        return point_req['data']['total_points'], point_req['data']['can_get_points']
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def check_cookie() -> bool:
    '''
    检查cookie是否过期
    '''
    try:
        check_cookie_url = gl.MI_URL + '/account/address/list'
        check_cookie_hearders = {
            'Cookie': gl.MI_COOKIE,
        }
        check_cookie_req = requests.get(check_cookie_url, headers=check_cookie_hearders)
        if check_cookie_req.status_code != 200:
            print(f"检查Cookie失败, 返回状态码为{check_cookie_req.status_code}")
            return False
        check_cookie_req = check_cookie_req.json()
        if check_cookie_req['retcode'] != 0:
            print("Cookie已过期")
            return False
        return True
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False

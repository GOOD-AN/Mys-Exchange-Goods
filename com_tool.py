'''
通用函数
'''
import hashlib
import os
import platform
import random
import string
import sys
import time
import configparser
import ntplib
import requests

MAIN_VERSION = '0.0.1'


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


def check_update(ini_config):
    '''
    检查更新
    '''
    try:
        config_version = ini_config.get('app', 'version')
        if MAIN_VERSION == config_version:
            print(f"当前程序版本为v{MAIN_VERSION}, 配置文件版本为v{config_version}")
            # 远程检查更新
            check_url = "https://github.com/GOOD-AN/mys_exch_goods/raw/main/update_log.json"
            check_info = requests.get(check_url).json()
            remote_least_version = check_info['least_version'].split('.')
            local_version = MAIN_VERSION.split('.')
            if compare_version(remote_least_version, local_version) == 1:
                print("版本过低, 程序将停止运行")
                time.sleep(3000)
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
        print(err)
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


# class CheckNetwork:
#     a = 123

#     def __init__(self) -> None:
#         print(CheckNetwork)
#         print(CheckNetwork.a)
#         CheckNetwork.a = time.time()
#         print(CheckNetwork.a)

#     def __del__(self):
#         print('del')


def get_ds():
    '''
    生成请求 Header 里的 DS
    参考：
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/tools.py
    https://github.com/Womsxd/AutoMihoyoBBS/blob/master/setting.py
    '''
    android_salt = "t0qEgfub6cvueAPgR5m9aQWWVciEer7v"
    t_param = str(int(time.time()))
    r_param = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    md5 = hashlib.md5()
    md5.update(f'salt={android_salt}&t={t_param}&r={r_param}'.encode())
    c_param = md5.hexdigest()
    return f"{t_param},{r_param},{c_param}"
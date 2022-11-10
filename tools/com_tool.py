"""
通用函数
"""
import hashlib
import os
import platform
import configparser
import re
import sys
import time
import ntplib
import requests

import tools.global_var as gl

MAIN_VERSION = '2.0.0'
CHECK_UPDATE_URL_LIST = [
    'https://cdn.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://fastly.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://github.com/GOOD-AN/Mys-Exchange-Goods/raw/main/',
]


def check_plat():
    """
    检查平台
    """
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
    """
    加载配置文件
    """
    config = configparser.ConfigParser()
    try:
        path = gl.CONFIG_PATH + os.sep + 'config.ini'
        config.read_file(open(path, "r", encoding="utf-8"))
        return config
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(err)
        sys.exit()


def get_cookie_str(target):
    """
    获取cookie字符串中相应的数据
    """
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
    """
    写入配置文件
    """
    try:
        gl.INI_CONFIG.set(section, key, value)
        path = gl.CONFIG_PATH + os.sep + 'config.ini'
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
    """
    版本号比较
    """
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
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        sys.exit()


def check_update():
    """
    检查更新
    """
    try:
        config_version = gl.INI_CONFIG.get('app', 'version')
        if MAIN_VERSION == config_version:
            print(f"当前程序版本为v{MAIN_VERSION}, 配置文件版本为v{config_version}")
            # 远程检查更新
            check_info = {}
            for check_update_url in CHECK_UPDATE_URL_LIST:
                check_url = check_update_url + "update_log.json"
                try:
                    check_info = requests.get(check_url, timeout=5).json()
                    break
                except requests.exceptions.RequestException:
                    continue
            if not check_info:
                print("检查更新失败")
                return False
            remote_least_version = check_info['least_version'].split('.')
            local_version = MAIN_VERSION.split('.')
            remote_last_vesion = check_info['last_vesion'].split('.')
            if compare_version(local_version, remote_last_vesion) == -1:
                remote_update_log_list = check_info['update_log']
                print(f"当前程序版本为v{MAIN_VERSION}, 最新程序版本为v{check_info['last_vesion']}")
                print("当前非最新版本，建议更新\n")
                print("更新概览: ")
                print("=" * 50)
                for update_log in remote_update_log_list:
                    if compare_version(update_log['version'].split('.'), local_version) == 1:
                        print("版本: ", f"{update_log['version']}".center(12))
                        print(f"更新时间: {update_log['update_time']}")
                        print(f"更新说明: {update_log['update_content'][0]}")
                        for content in update_log['update_content'][1:]:
                            print(content.rjust(20))
                        print("=" * 50)
                if compare_version(remote_least_version, local_version) == 1:
                    print("版本过低, 程序将停止运行")
                    print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
                    time.sleep(3)
                    sys.exit()
                print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
        else:
            print(f"当前程序版本为v{MAIN_VERSION}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
            print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
        return None
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"检查更新失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


def get_time(ntp_enable, ntp_server):
    """
    获取当前时间
    """
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
    """
    md5加密
    """
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

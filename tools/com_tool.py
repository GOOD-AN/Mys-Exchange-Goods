"""
通用函数
"""
from hashlib import md5
import os
import platform
from configparser import ConfigParser
import re
import sys
import time
from shutil import copyfile
import logging.config
from ntplib import NTPClient
import httpx

import tools.global_var as gl
from config import logging_config

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
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def load_config():
    """
    加载配置文件
    """
    config = ConfigParser()
    try:
        config_path = os.path.join(gl.CONFIG_PATH, 'config.ini')
        default_config_path = os.path.join(gl.CONFIG_PATH, 'default_config.ini')
        if not os.path.exists(config_path) and not os.path.exists(default_config_path):
            gl.standard_log.critical("配置文件不存在, 请检查")
            input("按回车键继续")
            sys.exit()
        if not os.path.exists(config_path) and os.path.exists(default_config_path):
            copyfile(default_config_path, config_path)
        config.read_file(open(config_path, "r", encoding="utf-8"))
        return config
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
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
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


def write_config_file(section, key, value):
    """
    写入配置文件
    """
    try:
        gl.INI_CONFIG.set(section, key, value)
        config_path = os.path.join(gl.CONFIG_PATH, 'config.ini')
        with open(config_path, "w", encoding="utf-8") as config_file:
            gl.INI_CONFIG.write(config_file)
            print("写入成功")
        gl.INI_CONFIG = load_config()
        if key == 'cookie':
            gl.MI_COOKIE = value
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
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
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def check_update(main_version):
    """
    检查更新
    """
    try:
        config_version = gl.INI_CONFIG.get('app', 'version')
        if main_version == config_version:
            print(f"当前程序版本为v{main_version}, 配置文件版本为v{config_version}")
            # 远程检查更新
            check_info = {}
            print("正在联网检查更新...")
            for check_update_url in CHECK_UPDATE_URL_LIST:
                check_url = check_update_url + "update_log.json"
                try:
                    check_info = httpx.get(check_url, timeout=5).json()
                    break
                except httpx.exceptions.RequestException:
                    continue
            if not check_info:
                print("检查更新失败")
                return False
            remote_least_version = check_info['least_version'].split('.')
            local_version = main_version.split('.')
            remote_last_version = check_info['last_version'].split('.')
            if compare_version(local_version, remote_last_version) == -1:
                remote_update_log_list = check_info['update_log']
                print(f"当前程序版本为v{main_version}, 最新程序版本为v{check_info['last_version']}")
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
                    gl.standard_log.critical("版本过低, 程序将停止运行")
                    print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
                    time.sleep(3)
                    sys.exit()
                print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
                return True
        else:
            gl.standard_log.warning(
                f"当前程序版本为v{main_version}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
            print("项目地址: https://github.com/GOOD-AN/mys_exch_goods")
            return True
        print("当前已是最新版本")
        return True
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"检查更新失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


def get_time(ntp_enable, ntp_server):
    """
    获取当前时间
    """
    try:
        if not ntp_enable:
            return time.time()
        return NTPClient().request(ntp_server).tx_time
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"网络时间获取失败, 原因为{err}, 转为本地时间")
        return time.time()


def md5_encode(text):
    """
    md5加密
    """
    try:
        md5_str = md5()
        md5_str.update(text.encode('utf-8'))
        return md5_str.hexdigest()
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def init_config():
    """
    初始化配置文件
    """
    try:
        basic_path = os.path.join(os.path.dirname(sys.argv[0]), 'log')
        log_path = os.path.join(basic_path, 'meg_all.log')
        if not os.path.exists(basic_path):
            os.mkdir(basic_path)
        logging_config.log_config['handlers']['standard_file']['filename'] = log_path
        logging.config.dictConfig(logging_config.log_config)
        gl.standard_log = logging.getLogger('standard_logger')
        gl.CONFIG_PATH = os.path.join(os.path.dirname(sys.argv[0]), "config")
        gl.INI_CONFIG = load_config()
        gl.CLEAR_TYPE = check_plat()
        gl.MI_COOKIE = gl.INI_CONFIG.get('user_info', 'cookie').strip(" ")
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()

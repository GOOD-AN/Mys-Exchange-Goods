"""
通用函数
"""
import asyncio
import json
import os
import platform
import sys
import time
from configparser import ConfigParser
from hashlib import md5
from shutil import copyfile

import httpx

from . import global_var as gl
from .user_data import GameInfo, AddressInfo, UserInfo

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
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def load_config():
    """
    加载配置文件
    """
    config_data = ConfigParser()
    try:
        config_path = os.path.join(gl.CONFIG_PATH, 'config.ini')
        default_config_path = os.path.join(gl.CONFIG_PATH, 'default_config.ini')
        if not os.path.exists(config_path) and not os.path.exists(default_config_path):
            print("配置文件不存在, 请检查")
            input("按回车键继续")
            sys.exit()
        if not os.path.exists(config_path) and os.path.exists(default_config_path):
            copyfile(default_config_path, config_path)
        config_data.read_file(open(config_path, "r", encoding="utf-8"))
        return config_data
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


async def write_config_file(section, key, value):
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
        print("用户强制退出")
        await async_input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")


async def compare_version(old_version, new_version):
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
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False


async def check_update(main_version):
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
                    async with httpx.AsyncClient() as client:
                        check_info = await client.get(check_url, timeout=5)
                        check_info = check_info.json()
                    break
                except (httpx.HTTPError, json.JSONDecodeError):
                    continue
            if not check_info:
                print("检查更新失败")
                return False
            remote_least_version = check_info['least_version'].split('.')
            local_version = main_version.split('.')
            remote_last_version = check_info['last_version'].split('.')
            if await compare_version(local_version, remote_last_version) == -1:
                remote_update_log_list = check_info['update_log']
                print(f"当前程序版本为v{main_version}, 最新程序版本为v{check_info['last_version']}")
                print("当前非最新版本，建议更新\n")
                print("更新概览: ")
                print("=" * 50)
                for update_log in remote_update_log_list:
                    if await compare_version(update_log['version'].split('.'), local_version) == 1:
                        print("版本: ", f"{update_log['version']}".center(12))
                        print(f"更新时间: {update_log['update_time']}")
                        print(f"更新说明: {update_log['update_content'][0]}")
                        for content in update_log['update_content'][1:]:
                            print(content.rjust(20))
                        print("=" * 50)
                if await compare_version(remote_least_version, local_version) == 1:
                    print("版本过低, 程序将停止运行")
                    print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
                    time.sleep(3)
                    sys.exit()
                print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
                return True
        else:
            print(
                f"当前程序版本为v{main_version}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
            print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
            return True
        print("当前已是最新版本")
        return True
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"检查更新失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return None


async def md5_encode(text):
    """
    md5加密
    """
    try:
        md5_str = md5()
        md5_str.update(text.encode('utf-8'))
        return md5_str.hexdigest()
    except KeyboardInterrupt:
        print("用户强制退出")
        await async_input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        sys.exit()


def load_user_data():
    """
    加载用户数据
    """
    try:
        user_data_dict = {}
        if os.path.exists(gl.USER_DATA_PATH):
            user_data_file_list = os.listdir(gl.USER_DATA_PATH)
            for user_data_file in user_data_file_list:
                with open(os.path.join(gl.USER_DATA_PATH, user_data_file), 'r', encoding='utf-8') as f:
                    try:
                        user_data = json.load(f)
                        user_game_list = []
                        user_address_list = []
                        for user_game in user_data['game_list']:
                            user_game_list.append(GameInfo(user_game))
                        user_data['game_list'] = user_game_list
                        for user_address in user_data['address_list']:
                            user_address_list.append(AddressInfo(user_address))
                        user_data['address_list'] = user_address_list
                        user_data_dict[user_data['mys_uid']] = UserInfo(user_data)
                    except (json.decoder.JSONDecodeError, KeyError) as err:
                        print(f"用户数据{user_data_file}解析失败, 跳过, ", end='')
                        print(f"错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
                        continue
        return user_data_dict
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


def init_config():
    """
    初始化配置文件
    """
    try:
        gl.BASIC_PATH = os.path.dirname(sys.argv[0])
        # log_path = os.path.join(gl.BASIC_PATH, 'log', 'meg_all.log')
        # if not os.path.exists(os.path.join(gl.BASIC_PATH, 'log')):
        #     os.mkdir(gl.BASIC_PATH)
        # logging_config.log_config['handlers']['standard_file']['filename'] = log_path
        # logging.config.dictConfig(logging_config.log_config)
        # gl.standard_log = logging.getLogger('standard_logger')
        gl.CONFIG_PATH = os.path.join(gl.BASIC_PATH, "config")
        gl.DATA_PATH = os.path.join(gl.BASIC_PATH, 'data')
        gl.USER_DATA_PATH = os.path.join(gl.DATA_PATH, 'user_info')
        gl.INI_CONFIG = load_config()
        gl.CLEAR_TYPE = check_plat()
        gl.USER_DICT = load_user_data()
        return True
    except KeyboardInterrupt:
        print("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


async def async_input(prompt=''):
    """
    异步输入
    """
    try:
        return await asyncio.to_thread(input, prompt)
    except AttributeError:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, input, prompt)

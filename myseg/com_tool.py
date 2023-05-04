"""
通用函数
"""
import asyncio
import json
import sys
import time
from hashlib import md5

import httpx
from ntplib import NTPClient

from . import user_global_var as gl, logger, logger_file

CHECK_UPDATE_URL_LIST = [
    'https://cdn.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://fastly.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://github.com/GOOD-AN/Mys-Exchange-Goods/raw/main/',
]


def get_time() -> float:
    """
    获取当前时间
    """
    try:
        ntp_enable = gl.init_config.getboolean('ntp', 'enable')
        ntp_server = gl.init_config.get('ntp', 'ntp_server')
        if not ntp_enable:
            return time.time()
        return NTPClient().request(ntp_server).tx_time
    except Exception as err:
        logger_file.warning(f"网络时间获取失败, 原因为{err}, 转为本地时间")
        return time.time()


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
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False


async def check_update(main_version):
    """
    检查更新
    """
    try:
        config_version = gl.init_config.get('app', 'version')
        if main_version == config_version:
            logger.info(f"当前程序版本为v{main_version}, 配置文件版本为v{config_version}")
            # 远程检查更新
            check_info = {}
            logger.info("正在联网检查更新...")
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
                logger.warning("检查更新失败")
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
                    logger.warning("版本过低, 程序将停止运行")
                    print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
                    time.sleep(3)
                    sys.exit()
                print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
                return True
        else:
            logger.warning(
                f"当前程序版本为v{main_version}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
            print("项目地址: https://github.com/GOOD-AN/Mys-Exchange-Goods")
            return True
        logger.info("当前已是最新版本")
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"检查更新失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
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
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
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

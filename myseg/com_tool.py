"""
通用函数
"""
import asyncio
import httpx
import json
import sys
import time
from hashlib import md5
from typing import Union, Dict

from .data_class import ClassEncoder, UserInfo
from .global_var import user_global_var as gl
from .logging import logger

CHECK_UPDATE_URL_LIST = [
    'https://cdn.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://fastly.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://github.com/GOOD-AN/Mys-Exchange-Goods/raw/main/',
]


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
                    async with httpx.AsyncClient(follow_redirects=True) as client:
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


async def save_user_file(save_data: UserInfo, log_info) -> Union[bool, UserInfo]:
    """
    保存文件数据
    """
    try:
        if save_data:
            if not gl.user_data_path.exists():
                gl.user_data_path.mkdir(parents=True, exist_ok=True)
            with open(gl.user_data_path / f"{save_data.mys_uid}.json", 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4, cls=ClassEncoder)
            logger.info(f"更新{log_info}信息成功")
            return save_data
        else:
            logger.info(f"获取到{log_info}信息失败")
            return False
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"保存文件失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def save_exchange_file(save_data: Dict) -> bool:
    """
    保存兑换文件数据
    """
    try:
        if save_data:
            exchange_file_path = gl.data_path / 'exchange_list.json'
            if not exchange_file_path.exists():
                exchange_file_path.mkdir(parents=True, exist_ok=True)
            with open(exchange_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            logger.info(f"更新兑换信息成功")
            return True
        else:
            logger.info(f"不存在兑换信息")
            return False
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"保存文件失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

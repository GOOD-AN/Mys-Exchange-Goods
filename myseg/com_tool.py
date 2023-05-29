"""
通用函数
"""
import httpx
import json
import sys
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, \
    EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from hashlib import md5
from typing import Union, Dict, Tuple, List

from .__version__ import __version__
from .data_class import ClassEncoder, UserInfo
from .global_var import user_global_var as gl
from .user_log import logger_file

CHECK_UPDATE_URL_LIST = [
    'https://cdn.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://fastly.jsdelivr.net/gh/GOOD-AN/mys_exch_goods@latest/',
    'https://github.com/GOOD-AN/Mys-Exchange-Goods/raw/main/',
]


async def compare_version(old_version, new_version) -> Union[int, bool]:
    """
    版本号比较
    1: 旧版本大于新版本
    0: 旧版本等于新版本
    -1: 旧版本小于新版本
    """
    try:
        for o_v, n_v in zip(old_version, new_version):
            if o_v > n_v:
                return 1
            if o_v < n_v:
                return -1
        return 0
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.exception(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def check_update() -> Tuple[int, Union[str, List[Union[List[Dict], str]]]]:
    """
    检查更新
    101: 检查更新失败
    102: 版本不匹配
    103: 当前版本为最新版本
    104: 当前版本低于最新版本但高于最低版本
    105: 当前版本低于最低版本
    """
    try:
        config_version = gl.init_config.get('app', 'version')
        if __version__ == config_version:
            logger_file.info(f"当前程序版本为v{__version__}, 配置文件版本为v{config_version}")
            check_info = {}
            for check_update_url in CHECK_UPDATE_URL_LIST:
                check_url = check_update_url + "update_log.json"
                try:
                    async with httpx.AsyncClient(follow_redirects=True) as client:
                        check_info = await client.get(check_url, timeout=5)
                        check_info = check_info.json()
                    break
                except (httpx.HTTPError, json.JSONDecodeError) as err:
                    logger_file.warning(f"检查更新失败, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}, "
                                        f"检查更新地址为: {check_url}")
                    continue
            if not check_info:
                logger_file.warning("检查更新失败")
                return 101, "检查更新失败"
            local_version = __version__.split('.')
            remote_least_version = check_info['least_version'].split('.')
            remote_last_version = check_info['last_version'].split('.')
            logger_file.info(f"远端最低版本为v{check_info['least_version']}, "
                             f"远端最新版本为v{check_info['last_version']}")
            if await compare_version(local_version, remote_last_version) == -1:
                remote_update_log_list = []
                for index, update_log in enumerate(check_info['update_log']):
                    if await compare_version(update_log['version'].split('.'), local_version) == 1:
                        remote_update_log_list = check_info['update_log'][index:]
                        break
                if await compare_version(remote_least_version, local_version) == 1:
                    return 105, [remote_update_log_list, check_info['last_version']]
                else:
                    return 104, [remote_update_log_list, check_info['last_version']]
        else:
            return 102, "版本不匹配"
        return 103, "当前为最新版本"
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"检查更新失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return 101, "检查更新失败"


async def md5_encode(text):
    """
    md5加密
    """
    try:
        md5_str = md5()
        md5_str.update(text.encode('utf-8'))
        return md5_str.hexdigest()
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        sys.exit()


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
            logger_file.info(f"保存{log_info}信息成功")
            return save_data
        else:
            logger_file.info(f"获取到{log_info}信息失败")
            return False
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"保存文件失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_exchange_data() -> Union[bool, Dict]:
    """
    获取兑换数据
    """
    try:
        exchange_file_path = gl.data_path / 'exchange_list.json'
        exchange_data = {}
        if exchange_file_path.exists():
            with open(exchange_file_path, "r", encoding="utf-8") as exchange_file:
                try:
                    exchange_data = json.load(exchange_file)
                except json.decoder.JSONDecodeError:
                    exchange_data = {}
                    logger_file.info("兑换文件数据格式错误, 已清空数据")
        return exchange_data
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def save_exchange_file(save_data: Dict) -> bool:
    """
    保存兑换文件数据
    """
    try:
        if save_data:
            exchange_file_path = gl.data_path / 'exchange_list.json'
            if not gl.data_path.exists():
                gl.data_path.mkdir(parents=True, exist_ok=True)
            with open(exchange_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            logger_file.info(f"更新兑换信息成功")
            return True
        else:
            logger_file.info(f"不存在兑换信息")
            return False
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"保存文件失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def scheduler_log_listener(event):
    """
    监听基础定时任务事件(此处事件只会输出到日志)
    """
    try:
        if event.code == EVENT_JOB_ADDED:
            logger_file.info(f"任务 {event.job_id} 已添加")
        elif event.code == EVENT_JOB_REMOVED:
            logger_file.info(f"任务 {event.job_id} 已删除")
        elif event.code == EVENT_JOB_MODIFIED:
            logger_file.info(f"任务 {event.job_id} 已修改")
        elif event.code == EVENT_JOB_MISSED:
            logger_file.warning(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            logger_file.error(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            logger_file.info(f"任务 {event.job_id} 已执行")
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

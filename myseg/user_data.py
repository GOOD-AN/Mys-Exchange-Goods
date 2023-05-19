"""
用户数据
"""
import json
import sys

from . import logger_file
from .data_class import AddressInfo, GameInfo, UserInfo
from .global_var import user_global_var as gl


def load_user_data():
    """
    加载用户数据
    """
    try:
        user_data_dict = {}
        if gl.user_data_path.exists():
            user_data_file_list = gl.user_data_path.iterdir()
            for user_data_file in user_data_file_list:
                logger_file.debug(user_data_file)
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    try:
                        user_data_load = json.load(f)
                        logger_file.debug(user_data_load)
                        user_game_list = []
                        user_address_list = []
                        for user_game in user_data_load['game_list']:
                            user_game_list.append(GameInfo.parse_obj(user_game))
                        user_data_load['game_list'] = user_game_list
                        for user_address in user_data_load['address_list']:
                            user_address_list.append(AddressInfo.parse_obj(user_address))
                        user_data_load['address_list'] = user_address_list
                        user_data_dict[user_data_load['mys_uid']] = UserInfo.parse_obj(user_data_load)
                    except (json.decoder.JSONDecodeError, KeyError) as err:
                        logger_file.warning(f"用户数据{user_data_file}解析失败, 跳过, ")
                        logger_file.warning(f"错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
                        continue
        logger_file.debug(user_data_dict)
        return user_data_dict
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        sys.exit()


user_dict = load_user_data()

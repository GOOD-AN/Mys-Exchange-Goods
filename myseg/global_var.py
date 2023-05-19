"""
全局变量
"""
import platform
from configparser import ConfigParser
from pathlib import Path
from pydantic import BaseModel
from shutil import copyfile
from typing import Optional, Union, Tuple


class GlobalVar(BaseModel):
    """
    全局变量
    """

    basic_path = Path(__file__).resolve().parent.parent
    config_path = basic_path / 'config'
    data_path = basic_path / 'data'
    user_data_path = data_path / 'user_info'
    init_config: Optional[ConfigParser]
    clear_type: Optional[str]

    class Config:
        """
        配置
        """
        arbitrary_types_allowed = True

    def load_config(self) -> Union[int, Tuple[int, Union[str, Exception]]]:
        """
        加载配置文件
        101: 读取配置文件成功
        102: 配置文件不存在
        -1: 用户强制退出
        -2: 运行出错
        """
        config_data = ConfigParser()
        try:
            config_path = self.config_path / 'config.ini'
            default_config_path = self.config_path / 'default_config.ini'
            if not config_path.exists() and not default_config_path.exists():
                return 102, "配置文件不存在"
            if not config_path.exists() and default_config_path.exists():
                copyfile(default_config_path, config_path)
            config_data.read_file(open(config_path, "r", encoding="utf-8"))
            self.init_config = config_data
            return 101
        except KeyboardInterrupt:
            return -1, "用户强制退出"
        except Exception as err:
            return -2, err

    def check_plat(self) -> Union[int, Tuple[int, Union[str, Exception]]]:
        """
        检查平台
        -1: 用户强制退出
        -2: 运行出错
        101: 检查平台成功
        """
        try:
            platform_type = "clear"
            if platform.system() == "Windows":
                platform_type = "cls"
            self.clear_type = platform_type
            return 101
        except KeyboardInterrupt:
            return -1, "用户强制退出"
        except Exception as err:
            return -2, err


user_global_var = GlobalVar()

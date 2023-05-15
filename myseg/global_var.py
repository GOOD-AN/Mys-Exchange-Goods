"""
全局变量
"""

import platform
import sys
from configparser import ConfigParser
from pathlib import Path
from pydantic import BaseModel
from shutil import copyfile
from typing import Optional


class GlobalVar(BaseModel):
    """
    全局变量
    """

    basic_path = Path(sys.argv[0]).cwd()
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

    def __init__(self):
        super().__init__()
        self.init_config = self.load_config()
        self.clear_type = self.check_plat()

    def load_config(self):
        """
        加载配置文件
        """
        config_data = ConfigParser()
        try:
            config_path = self.config_path / 'config.ini'
            default_config_path = self.config_path / 'default_config.ini'
            if not config_path.exists() and not default_config_path.exists():
                print("配置文件不存在, 请检查")
                input("按回车键继续")
                sys.exit()
            if not config_path.exists() and default_config_path.exists():
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

    @staticmethod
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


user_global_var = GlobalVar()

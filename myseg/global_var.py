"""
全局变量
"""
import sys
from configparser import ConfigParser
from pathlib import Path
from shutil import copyfile


class GlobalVar:
    """
    全局变量
    """

    def __init__(self):
        self.basic_path = Path(sys.argv[0]).cwd()
        self.config_path = self.basic_path / 'config'
        self.data_path = self.basic_path / 'data'
        self.user_data_path = self.data_path / 'user_info'
        self.init_config = self.load_config()
        self.clear_type = ''
        self.user_dict = {}
        self.mi_url = 'https://api-takumi.mihoyo.com'
        self.web_url = 'https://webapi.account.mihoyo.com'
        self.bbs_url = 'https://bbs-api.mihoyo.com'
        self.mi_intl_url = 'https://api-os-takumi.mihoyo.com'

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

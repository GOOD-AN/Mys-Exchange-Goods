"""
全局变量
"""
import sys
from pathlib import Path


class GlobalVar:
    """
    全局变量
    """

    def __init__(self):
        self.basic_path = Path(sys.argv[0]).cwd()
        self.config_path = self.basic_path / 'config'
        self.data_path = self.basic_path / 'data'
        self.user_data_path = self.data_path / 'user_info'
        self.init_config = ''
        self.clear_type = ''
        self.user_dict = {}
        self.mi_url = 'https://api-takumi.mihoyo.com'
        self.web_url = 'https://webapi.account.mihoyo.com'
        self.bbs_url = 'https://bbs-api.mihoyo.com'
        self.mi_intl_url = 'https://api-os-takumi.mihoyo.com'

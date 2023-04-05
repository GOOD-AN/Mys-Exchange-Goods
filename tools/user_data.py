"""
用户数据
"""
import json
import re
from typing import Union


class ClassEncoder(json.JSONEncoder):
    """
    自定义json编码器
    """

    def default(self, obj):
        if isinstance(obj, (UserInfo, GameInfo, AddressInfo)):
            return dict((key.lstrip("_"), value) for key, value in obj.__dict__.items())
        else:
            return json.JSONEncoder.default(self, obj)


class UserInfo:
    """
    用户信息
    """

    def __init__(self, user_info: Union[dict, list, None]):
        """
        初始化用户信息
        """
        if isinstance(user_info, dict):
            self.mys_uid = user_info['mys_uid']
            self.cookie = user_info['cookie']
            self.game_list = user_info['game_list']
            self.address_list = user_info['address_list']
        elif isinstance(user_info, list):
            self.mys_uid = user_info[0]
            self.cookie = user_info[1]
            self.game_list = []
            self.address_list = []
        elif user_info is None:
            self.mys_uid = ''
            self.cookie = ''
            self.game_list = []
            self.address_list = []
        else:
            raise TypeError('user_info type error')

    @property
    def mys_uid(self) -> str:
        """
        获取米游社UID
        """
        return self._mys_uid

    @property
    def cookie(self) -> str:
        """
        获取Cookie
        """
        return self._cookie

    @property
    def game_list(self) -> list:
        """
        获取游戏账户列表
        """
        return self._game_list

    @property
    def address_list(self) -> list:
        """
        获取地址列表
        """
        return self._address_list

    @mys_uid.setter
    def mys_uid(self, value: str):
        """
        设置米游社UID
        """
        self._mys_uid = value

    @cookie.setter
    def cookie(self, value: str):
        """
        设置Cookie
        """
        self._cookie = value

    @game_list.setter
    def game_list(self, value: list):
        """
        设置游戏账户列表
        """
        self._game_list = value

    @address_list.setter
    def address_list(self, value: list):
        """
        设置地址列表
        """
        self._address_list = value

    @property
    def stoken(self) -> str:
        """
        获取stoken
        """
        return self.__get_cookie_str('stoken')

    @property
    def stuid(self) -> str:
        """
        获取stuid
        """
        return self.__get_cookie_str('stuid')

    @property
    def cookie_token(self) -> str:
        """
        获取cookie_token
        """
        return self.__get_cookie_str('cookie_token')

    def __get_cookie_str(self, target) -> str:
        """
        获取cookie字符串中相应的数据
        """
        pattern_str = re.compile(target + '=(.*?);')
        result_str = pattern_str.search(self.cookie)
        if result_str:
            return result_str.group(1)
        return ''


class GameInfo:
    """
    游戏账户信息
    """

    def __init__(self, game_info: dict):
        """
        初始化游戏账户信息
        """
        self.game_biz = game_info['game_biz']
        self.game_uid = game_info['game_uid']
        self.game_nickname = game_info['game_nickname']
        self.game_level = game_info['game_level']
        self.game_region = game_info['game_region']
        self.game_region_name = game_info['game_region_name']

    @property
    def game_biz(self) -> str:
        """
        获取游戏biz
        """
        return self._game_biz

    @property
    def game_uid(self) -> str:
        """
        获取游戏UID
        """
        return self._game_uid

    @property
    def game_nickname(self) -> str:
        """
        获取游戏昵称
        """
        return self._game_nickname

    @property
    def game_level(self) -> str:
        """
        获取游戏等级
        """
        return self._game_level

    @property
    def game_region(self) -> str:
        """
        获取游戏区服
        """
        return self._game_region

    @property
    def game_region_name(self) -> str:
        """
        获取游戏区服名称
        """
        return self._game_region_name

    @game_biz.setter
    def game_biz(self, value):
        self._game_biz = value

    @game_uid.setter
    def game_uid(self, value):
        self._game_uid = value

    @game_nickname.setter
    def game_nickname(self, value):
        self._game_nickname = value

    @game_level.setter
    def game_level(self, value):
        self._game_level = value

    @game_region.setter
    def game_region(self, value):
        self._game_region = value

    @game_region_name.setter
    def game_region_name(self, value):
        self._game_region_name = value


class AddressInfo:
    """
    地址信息
    """

    def __init__(self, address_info: dict):
        """
        初始化地址信息
        """
        self.address_id = address_info['address_id']
        self.connect_name = address_info['connect_name']
        self.connect_areacode = address_info['connect_areacode']
        self.connect_mobile = address_info['connect_mobile']
        self.province_name = address_info['province_name']
        self.city_name = address_info['city_name']
        self.county_name = address_info['county_name']
        self.addr_ext = address_info['addr_ext']

    @property
    def address_id(self) -> str:
        """
        获取地址ID
        """
        return self._address_id

    @property
    def connect_name(self) -> str:
        """
        获取联系人姓名
        """
        return self._connect_name

    @property
    def connect_areacode(self) -> str:
        """
        获取联系人区号
        """
        return self._connect_areacode

    @property
    def connect_mobile(self) -> str:
        """
        获取联系人电话(不含区号)
        """
        return self._connect_mobile

    @property
    def province_name(self) -> str:
        """
        获取省份
        """
        return self._province_name

    @property
    def city_name(self) -> str:
        """
        获取城市
        """
        return self._city_name

    @property
    def county_name(self) -> str:
        """
        获取区县
        """
        return self._county_name

    @property
    def addr_ext(self) -> str:
        """
        获取详细地址
        """
        return self._addr_ext

    @address_id.setter
    def address_id(self, value):
        """
        设置地址ID
        """
        self._address_id = value

    @connect_name.setter
    def connect_name(self, value):
        """
        设置联系人姓名
        """
        self._connect_name = value

    @connect_areacode.setter
    def connect_areacode(self, value):
        """
        设置联系人区号
        """
        self._connect_areacode = value

    @connect_mobile.setter
    def connect_mobile(self, value):
        """
        设置联系人手机号
        """
        self._connect_mobile = value

    @province_name.setter
    def province_name(self, value):
        """
        设置省份
        """
        self._province_name = value

    @city_name.setter
    def city_name(self, value):
        """
        设置城市
        """
        self._city_name = value

    @county_name.setter
    def county_name(self, value):
        """
        设置区县
        """
        self._county_name = value

    @addr_ext.setter
    def addr_ext(self, value):
        """
        设置详细地址
        """
        self._addr_ext = value

    @property
    def connect_phone(self) -> str:
        """
        获取联系人电话(含区号)
        """
        return self.connect_areacode + self.connect_mobile

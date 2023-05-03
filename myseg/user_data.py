"""
用户数据
"""
import json
import re
import time
from typing import Union

from ntplib import NTPClient

from . import global_var as gl


class ClassEncoder(json.JSONEncoder):
    """
    自定义json编码器
    """

    def default(self, obj):
        """
        重写JSONEncoder以适应类
        """
        if isinstance(obj, (UserInfo, GameInfo, AddressInfo, ExchangeInfo, GoodsInfo)):
            return dict((key.lstrip("_"), value) for key, value in obj.__dict__.items())
        else:
            return json.JSONEncoder.default(self, obj)


# 类创建需简化
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
            self.channel_dict = user_info['channel_dict']
        elif isinstance(user_info, list):
            self.mys_uid = user_info[0]
            self.cookie = user_info[1]
            self.game_list = []
            self.address_list = []
            self.channel_dict = {}
        elif user_info is None:
            self.mys_uid = ''
            self.cookie = ''
            self.game_list = []
            self.address_list = []
            self.channel_dict = {}
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

    @property
    def channel_dict(self) -> dict:
        """
        获取渠道等级信息
        """
        return self._channel_dict

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

    @property
    def account_id(self) -> str:
        """
        获取account_id
        """
        return self.__get_cookie_str('account_id')

    def __get_cookie_str(self, target) -> str:
        """
        获取cookie字符串中相应的数据
        """
        pattern_str = re.compile(target + '=(.*?);')
        result_str = pattern_str.search(self.cookie)
        if result_str:
            return result_str.group(1)
        return ''

    @channel_dict.setter
    def channel_dict(self, value):
        self._channel_dict = value


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

    @property
    def full_address(self) -> str:
        """
        获取完整地址
        """
        return self.province_name + self.city_name + self.county_name + self.addr_ext


class ExchangeInfo:
    """
    兑换商品信息
    """

    def __init__(self, goods_info: dict, goods_detail=None):
        """
        初始化商品信息
        """
        self.mys_uid = goods_info['mys_uid']
        self.goods_id = goods_info['goods_id']
        self.goods_name = goods_info['goods_name']
        self.goods_type = goods_info['goods_type']
        self.goods_biz = goods_info['goods_biz']
        self.exchange_num = goods_info['exchange_num']
        self.game_id = goods_info['game_id']
        self.game_region = goods_info['game_region'] if 'game_region' in goods_info else ''
        self.address_id = goods_info['address_id'] if 'address_id' in goods_info else ''
        self.exchange_time = goods_info['exchange_time']
        self.__goods_detail = goods_detail
        self.__ntp_enable = gl.INI_CONFIG.getboolean('ntp', 'enable')
        self.__ntp_server = gl.INI_CONFIG.get('ntp', 'ntp_server')
        self.__check_info()

    def __check_info(self):
        """
        检查商品兑换信息
        """
        now_time = int(self.__get_time(self.__ntp_enable, self.__ntp_server))
        if self.exchange_time < now_time:
            raise ValueError(f"商品 {self.goods_name} 兑换时间已过, 已自动跳过")
        if self.goods_biz != "bbs_cn" and self.goods_type == 2 \
                and (self.mys_uid == self.game_id or self.game_region == ''):
            raise ValueError(f"商品 {self.goods_name} 游戏账户信息设置错误, 已自动跳过")
        if (self.goods_type == 1 or self.goods_type == 4) and self.address_id == '':
            raise ValueError(f"商品 {self.goods_name} 为实物, 但收货地址不存在, 已自动跳过")
        if self.__goods_detail == -1:
            raise ValueError(f"商品 {self.goods_name} 已售罄, 已自动跳过")

    @staticmethod
    def __get_time(ntp_enable, ntp_server) -> float:
        """
        获取当前时间
        """
        try:
            if not ntp_enable:
                return time.time()
            return NTPClient().request(ntp_server).tx_time
        except Exception as err:
            print(f"网络时间获取失败, 原因为{err}, 转为本地时间")
            return time.time()

    @property
    def mys_uid(self) -> str:
        """
        获取兑换账户ID
        """
        return self._mys_uid

    @property
    def goods_id(self) -> str:
        """
        获取商品ID
        """
        return self._goods_id

    @property
    def goods_name(self) -> str:
        """
        获取商品名称
        """
        return self._goods_name

    @property
    def goods_type(self) -> int:
        """
        获取商品类型
        """
        return self._goods_type

    @property
    def goods_biz(self) -> str:
        """
        获取商品所在区服
        """
        return self._goods_biz

    @property
    def exchange_num(self) -> int:
        """
        获取兑换数量
        """
        return self._exchange_num

    @property
    def game_id(self) -> str:
        """
        获取游戏ID
        """
        return self._game_id

    @property
    def game_region(self) -> str:
        """
        获取游戏区服
        """
        return self._game_region

    @property
    def exchange_time(self) -> int:
        """
        获取兑换时间
        """
        return self._exchange_time

    @mys_uid.setter
    def mys_uid(self, value):
        self._mys_uid = value

    @goods_id.setter
    def goods_id(self, value):
        self._goods_id = value

    @goods_name.setter
    def goods_name(self, value):
        self._goods_name = value

    @exchange_num.setter
    def exchange_num(self, value):
        self._exchange_num = value

    @game_id.setter
    def game_id(self, value):
        self._game_id = value

    @exchange_time.setter
    def exchange_time(self, value):
        self._exchange_time = value

    @goods_type.setter
    def goods_type(self, value):
        self._goods_type = value

    @goods_biz.setter
    def goods_biz(self, value):
        self._goods_biz = value

    @game_region.setter
    def game_region(self, value):
        self._game_region = value


class GoodsInfo:
    """
    商品信息
    """

    def __init__(self):
        """
        初始化商品信息
        """
        self.goods_id = ''
        self.goods_name = ''
        self.goods_price = ''
        self.goods_type = ''
        self.game_biz = ''
        self.goods_num = ''
        self.goods_limit = ''
        self.goods_rule = []
        self.goods_time = ''

    @property
    def goods_id(self) -> str:
        """
        获取商品ID
        """
        return self._goods_id

    @property
    def goods_name(self) -> str:
        """
        获取商品名称
        """
        return self._goods_name

    @property
    def goods_price(self) -> str:
        """
        获取商品价格
        """
        return self._goods_price

    @property
    def game_biz(self) -> str:
        """
        获取商品游戏类型
        """
        return self._game_biz

    @property
    def goods_type(self) -> str:
        """
        获取商品类型
        """
        return self._goods_type

    @property
    def goods_num(self) -> str:
        """
        获取商品数量
        """
        return self._goods_num

    @property
    def goods_limit(self) -> str:
        """
        获取商品购买数量限制
        """
        return self._goods_limit

    @property
    def goods_rule(self) -> list:
        """
        获取商品规则
        """
        return self._goods_rule

    @property
    def goods_time(self) -> str:
        """
        获取商品兑换时间
        """
        return self._goods_time

    @goods_id.setter
    def goods_id(self, value):
        """
        设置商品ID
        """
        self._goods_id = value

    @goods_name.setter
    def goods_name(self, value):
        """
        设置商品名称
        """
        self._goods_name = value

    @goods_price.setter
    def goods_price(self, value):
        """
        设置商品价格
        """
        self._goods_price = value

    @game_biz.setter
    def game_biz(self, value):
        """
        设置商品游戏类型
        """
        self._game_biz = value

    @goods_type.setter
    def goods_type(self, value):
        """
        设置商品类型
        """
        self._goods_type = value

    @goods_num.setter
    def goods_num(self, value):
        """
        设置商品数量
        """
        self._goods_num = value

    @goods_limit.setter
    def goods_limit(self, value):
        """
        设置商品购买数量限制
        """
        self._goods_limit = value

    @goods_rule.setter
    def goods_rule(self, value):
        """
        设置商品规则
        """
        self._goods_rule = value

    @goods_time.setter
    def goods_time(self, value):
        """
        设置商品兑换时间
        """
        self._goods_time = value

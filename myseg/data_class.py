"""
用户数据
"""
import json
import re
import time
from ntplib import NTPClient
from pydantic import BaseModel, validator, root_validator
from typing import List, Dict, Optional, Union

from .global_var import user_global_var as gl
from .user_log import logger_file


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


class ClassEncoder(json.JSONEncoder):
    """
    自定义json编码器
    """

    def default(self, obj):
        """
        重写JSONEncoder以适应类
        """
        if isinstance(obj, (UserInfo, GameInfo, AddressInfo, ExchangeInfo, GoodsInfo)):
            return obj.dict()
        else:
            return json.JSONEncoder.default(self, obj)


class GameInfo(BaseModel):
    """
    游戏账户信息
    """

    game_uid: str
    """游戏ID"""
    game_biz: str
    """游戏区服"""
    nickname: str
    """游戏昵称"""
    level: int
    """游戏等级"""
    region: str
    """游戏次区服"""
    region_name: str
    """游戏次区服名称"""


class AddressInfo(BaseModel):
    """
    地址信息
    """
    id: str
    """地址ID"""
    connect_name: str
    """联系人姓名"""
    connect_areacode: str
    """联系人区号"""
    connect_mobile: str
    """联系人电话"""
    province_name: str
    """省份"""
    city_name: str
    """城市"""
    county_name: str
    """区县"""
    addr_ext: str
    """详细地址"""

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


class UserInfo(BaseModel):
    """
    用户信息
    """
    mys_uid: Optional[str]
    """用户ID"""
    cookie: Optional[str]
    """用户cookie"""
    game_list: Optional[List[GameInfo]]
    """游戏账户列表"""
    address_list: Optional[List[AddressInfo]]
    """地址列表"""
    channel_dict: Optional[Dict[str, int]]
    """频道等级"""

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

    @property
    def is_not_none(self) -> bool:
        """
        判断用户信息是否为空
        """
        return self.mys_uid is not None and self.cookie is not None and self.channel_dict is not None

    def game_for_biz(self, biz: str) -> Optional[GameInfo]:
        """
        获取指定游戏区服的游戏账户信息
        """
        if self.game_list is None:
            return None
        for game in self.game_list:
            if game.game_biz == biz:
                return game
        return None


class ExchangeInfo(BaseModel):
    """
    兑换商品信息
    """

    mys_uid: str
    """兑换用户ID"""
    goods_id: str
    """商品ID"""
    goods_name: str
    """商品名称"""
    type: int
    """商品类型"""
    game_biz: str
    """商品区服"""
    exchange_num: int
    """兑换数量"""
    game_uid: str
    """游戏ID"""
    region: Optional[str]
    """游戏区服"""
    address_id: Optional[str]
    """地址ID"""
    exchange_time: int
    """兑换时间"""

    @validator('exchange_time')
    def exchange_time_not_over_time(cls, v, values):
        """
        检查兑换时间是否已过
        """
        if v == -1:
            return get_time() + 60
        elif v < get_time():
            raise ValueError(f"商品 {values['goods_name']} 兑换时间已过, 已自动跳过")
        return v

    @root_validator
    def check_key_info(cls, values):
        """
        检查关键兑换信息是否存在
        """
        if values['game_biz'] != "bbs_cn" and values['type'] == 2 \
                and (values['mys_uid'] == values['game_uid'] or values['region'] == ''):
            raise ValueError(f"商品 {values['goods_name']} 游戏账户信息设置错误, 已自动跳过")
        if (values['type'] == 1 or values['type'] == 4) and values['address_id'] == '':
            raise ValueError(f"商品 {values['goods_name']} 为实物, 但收货地址不存在, 已自动跳过")
        return values


class GoodsInfo(BaseModel):
    """
    商品信息
    """

    goods_id: str
    """商品id"""
    goods_name: str
    """商品名称"""
    type: int
    """商品类型"""
    price: int
    """商品价格"""
    unlimit: bool
    """商品兑换总数量是否无限制"""
    total: int
    """商品兑换总数量"""
    account_cycle_type: str
    """商品账户限购类型"""
    account_cycle_limit: int
    """商品账户限购数量"""
    account_exchange_num: int
    """商品账户已兑换数量"""
    status: str
    """商品状态"""
    next_num: int
    """商品下次兑换数量"""
    next_time: int
    """商品下次兑换时间"""
    rules: Optional[List[Dict[str, Union[int, List[str]]]]]
    """商品兑换规则"""
    game_biz: Optional[str]
    """商品区服"""
    sale_start_time: Optional[int]
    """商品销售开始时间"""

    def rule_for_num(self, num: int) -> Optional[str]:
        """
        获取指定的兑换规则
        """
        if not self.rules:
            return None
        for rule in self.rules:
            if num == rule['rule_id']:
                return rule['values'][0]
        return None

    @property
    def exchange_time(self) -> int:
        """
        获取商品下次兑换时间
        """
        if self.next_time == 0 or (self.next_time > get_time() and self.total > 0):
            return -1
        elif self.status == 'online':
            return self.next_time
        else:
            return self.sale_start_time

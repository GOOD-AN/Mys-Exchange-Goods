"""
用户数据
"""
import json
import re
from typing import List, Dict, Optional

from pydantic import BaseModel, validator, root_validator


class ClassEncoder(json.JSONEncoder):
    """
    自定义json编码器
    """

    def default(self, obj):
        """
        重写JSONEncoder以适应类
        """
        if isinstance(obj, (UserInfo, GameInfo, AddressInfo, ExchangeInfo, GoodsInfo)):
            return obj.__dict__
        else:
            return json.JSONEncoder.default(self, obj)


# 类创建需简化


class GameInfo(BaseModel):
    """
    游戏账户信息
    """
    game_biz: str
    """游戏区服"""
    game_uid: str
    """游戏ID"""
    game_nickname: str
    """游戏昵称"""
    game_level: int
    """游戏等级"""
    game_region: str
    """游戏区服"""
    game_region_name: str
    """游戏区服名称"""


class AddressInfo(BaseModel):
    """
    地址信息
    """
    address_id: str
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


class ExchangeInfo(BaseModel):
    """
    兑换商品信息
    """
    now_time: int
    """当前时间"""
    mys_uid: str
    """兑换用户ID"""
    goods_id: str
    """商品ID"""
    goods_name: str
    """商品名称"""
    goods_type: int
    """商品类型"""
    goods_biz: str
    """商品区服"""
    exchange_num: int
    """兑换数量"""
    game_id: str
    """游戏ID"""
    game_region: Optional[str]
    """游戏区服"""
    address_id: Optional[str]
    """地址ID"""
    exchange_time: int
    """兑换时间"""
    goods_status = 0
    """商品状态"""

    @validator('goods_status')
    def check_not_sold_out(cls, v, values):
        """
        检查商品是否已售罄
        """
        if v == -1:
            raise ValueError(f"商品 {values['goods_name']} 已售罄, 已自动跳过")
        return v

    @validator('exchange_time')
    def exchange_time_not_over_time(cls, v, values):
        """
        检查兑换时间是否已过
        """
        if v == -1:
            return values['now_time'] + 5
        elif v < values['now_time']:
            raise ValueError(f"商品 {values['goods_name']} 兑换时间已过, 已自动跳过")
        return v

    @root_validator
    def check_key_info(cls, values):
        """
        检查关键兑换信息是否存在
        """
        if values['goods_biz'] != "bbs_cn" and values['goods_type'] == 2 \
                and (values['mys_uid'] == values['game_id'] or values['game_region'] == ''):
            raise ValueError(f"商品 {values['goods_name']} 游戏账户信息设置错误, 已自动跳过")
        if (values['goods_type'] == 1 or values['goods_type'] == 4) and values['address_id'] == '':
            raise ValueError(f"商品 {values['goods_name']} 为实物, 但收货地址不存在, 已自动跳过")
        return values


class GoodsInfo(BaseModel):
    """
    商品信息
    """
    goods_id: Optional[str]
    """商品id"""
    goods_name: Optional[str]
    """商品名称"""
    goods_price: Optional[str]
    """商品价格"""
    goods_type: Optional[str]
    """商品类型"""
    goods_biz: Optional[str]
    """商品区服"""
    goods_num: Optional[str]
    """商品数量"""
    goods_limit: Optional[str]
    """商品限购"""
    goods_rule: Optional[Dict[int, List]]
    """商品兑换规则"""
    goods_time: Optional[str]
    """商品兑换时间"""

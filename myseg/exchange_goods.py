"""
兑换商品
"""
import asyncio
import httpx
import json
import sys
from typing import Union, Optional, List

from myseg import logger_file
from myseg.com_tool import get_exchange_data
from myseg.data_class import ExchangeInfo
from myseg.global_var import user_global_var as gl
from myseg.mi_tool import MI_URL, get_goods_detail
from myseg.user_data import user_dict


class ExchangeGoods(ExchangeInfo):
    """
    商品兑换类
    """
    cookie: str
    task_id: str
    order_sn: Optional[str]

    async def exchange_goods(self) -> bool:
        """
        兑换礼物
        需要account_id与cookie_token
        """
        try:
            exchange_goods_url = MI_URL + "/mall/v1/web/goods/exchange"
            exchange_goods_json = {
                "app_id": 1,
                "point_sn": "myb",
                "goods_id": self.goods_id,
                "exchange_num": 1,
                "uid": self.mys_uid,
                "game_biz": self.game_biz
            }
            exchange_goods_headers = {
                "Cookie": self.cookie
            }
            if self.region:
                exchange_goods_json['region'] = self.region
            if self.address_id:
                exchange_goods_json['address_id'] = self.address_id
            exchange_goods_req = ''
            async with httpx.AsyncClient() as client:
                for _ in range(gl.init_config.getint('exchange_setting', 'retry')):
                    exchange_goods_req = await client.post(exchange_goods_url,
                                                           headers=exchange_goods_headers,
                                                           json=exchange_goods_json)
                    if exchange_goods_req.status_code != 429:
                        break
            if exchange_goods_req == '':
                return False
            if exchange_goods_req.status_code != 200:
                logger_file.info(
                    f"商品 {self.goods_id} -{self.goods_name} 兑换失败, 错误码为{exchange_goods_req.status_code}")
                return False
            exchange_goods_req_json = exchange_goods_req.json()
            if exchange_goods_req_json['data'] is None:
                logger_file.info(f"商品 {self.goods_id} -{self.goods_name} 兑换失败, "
                                 f"错误信息为{exchange_goods_req_json['message']}")
                return False
            self.order_sn = exchange_goods_req_json['data']['order_sn']
            return True
        except KeyboardInterrupt:
            logger_file.warning("用户强制退出")
            sys.exit()
        except Exception as err:
            logger_file.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False

    async def run_task(self) -> Union[bool, Optional[str]]:
        """
        运行任务
        """
        try:
            task_thread = gl.init_config.getint('exchange_setting', 'thread')
            task_list = []
            for _ in range(task_thread):
                task_list.append(asyncio.create_task(self.exchange_goods()))
            for task in task_list:
                await task
            success_list = list(filter(lambda x: x.result(), task_list))
            if success_list:
                logger_file.info(f"商品 {self.goods_name} 兑换成功, 订单号为{self.order_sn}")
            else:
                logger_file.info(f"商品 {self.goods_name} 兑换失败")
            with open(gl.data_path / 'exchange_list.json', "r", encoding="utf-8") as exchange_file:
                try:
                    goods_data_dict = json.load(exchange_file)
                    del goods_data_dict[self.task_id]
                except (KeyError, json.decoder.JSONDecodeError) as err:
                    logger_file.exception(f"删除任务失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            with open(gl.data_path / 'exchange_list.json', "w", encoding="utf-8") as exchange_file:
                try:
                    json.dump(goods_data_dict, exchange_file, ensure_ascii=False, indent=4)
                    logger_file.info(f"删除任务 {self.task_id} 成功")
                except Exception as err:
                    logger_file.exception(f"删除任务失败, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return self.order_sn
        except KeyboardInterrupt:
            logger_file.warning("用户强制退出")
            sys.exit()
        except Exception as err:
            logger_file.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False


async def init_exchange() -> Union[bool, List[ExchangeGoods]]:
    """
    初始化任务
    """
    try:
        exchange_file_path = gl.data_path / 'exchange_list.json'
        if not exchange_file_path.exists():
            return False
        goods_data_dict = await get_exchange_data()
        exchange_data_list = []
        error_list = []
        for goods_key, goods_data in goods_data_dict.items():
            goods_detail_data = await get_goods_detail(goods_data['goods_id'])
            if not goods_detail_data:
                continue
            if not goods_detail_data.unlimit and goods_detail_data.next_num == 0 and goods_detail_data.total == 0:
                logger_file.info(f"商品 {goods_detail_data.goods_name} 已售罄, 自动跳过")
                error_list.append(goods_key)
                continue
            try:
                goods_data.update({"task_id": goods_key, "cookie": user_dict[goods_data['mys_uid']].cookie})
                exchange_data_list.append(ExchangeGoods.parse_obj(goods_data))
            except (KeyError, ValueError) as err:
                logger_file.error(f"商品 {goods_key} -{goods_data['goods_name']} 添加失败, 错误信息为{err}")
                error_list.append(goods_key)
                continue
        if error_list:
            for error_key in error_list:
                logger_file.info(f"商品 {error_key} -{goods_data_dict[error_key]['goods_name']} 失效删除")
                del goods_data_dict[error_key]
            with open(exchange_file_path, "w", encoding="utf-8") as exchange_file:
                json.dump(goods_data_dict, exchange_file, ensure_ascii=False, indent=4)
        return exchange_data_list
    except KeyboardInterrupt:
        logger_file.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        logger_file.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

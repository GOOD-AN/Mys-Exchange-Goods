"""
米游社商品兑换
"""
import asyncio
import httpx
import json
import sys
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from datetime import datetime

from . import scheduler
from .com_tool import async_input, get_exchange_data
from .data_class import ExchangeInfo
from .global_var import user_global_var as gl
from .logging import logger, logger_file
from .mi_tool import get_goods_detail, MI_URL
from .user_data import user_dict


class ExchangeGoods(ExchangeInfo):
    """
    商品兑换类
    """
    cookie: str
    task_id: str

    async def post_exchange_gift(self):
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
                return [False, self.goods_id, self.goods_name]
            if exchange_goods_req.status_code != 200:
                logger_file.info(
                    f"商品 {self.goods_id} -{self.goods_name} 兑换失败, 错误码为{exchange_goods_req.status_code}")
                return [False, self.goods_id, self.goods_name]
            exchange_goods_req_json = exchange_goods_req.json()
            if exchange_goods_req_json['data'] is None:
                logger_file.info(f"商品 {self.goods_id} -{self.goods_name} 兑换失败, "
                                 f"错误信息为{exchange_goods_req_json['message']}")
                return [False, self.goods_id, self.goods_name]
            return [True, self.goods_id, self.goods_name, exchange_goods_req_json['data']['order_sn']]
        except KeyboardInterrupt:
            logger.warning("用户强制退出")
            input("按回车键继续")
            sys.exit()
        except Exception as err:
            logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return [False, self.goods_id, self.goods_name]

    async def run_task(self):
        """
        运行任务
        """
        try:
            task_thread = gl.init_config.getint('exchange_setting', 'thread')
            task_list = []
            for _ in range(task_thread):
                task_list.append(asyncio.create_task(self.post_exchange_gift()))
            for task in task_list:
                await task
            success_list = list(filter(lambda x: x.result()[0], task_list))
            if success_list:
                logger.debug(success_list)
                logger.info(f"商品 {success_list[0].result()[2]} 兑换成功, "
                            f"订单号为{success_list[0].result()[3]}, 请前往米游社APP查看")
            else:
                logger.info(f"商品 {task_list[0].result()[2]} 兑换失败")
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
            return False
        except KeyboardInterrupt:
            logger.warning("用户强制退出")
            input("按回车键继续")
            sys.exit()
        except Exception as err:
            logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False


async def init_task():
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
        print("将会删除所有无法兑换的商品")
        for goods_key, goods_data in goods_data_dict.items():
            goods_detail_data = await get_goods_detail(goods_data['goods_id'])
            if not goods_detail_data:
                continue
            if not goods_detail_data.unlimit and goods_detail_data.next_num == 0 and goods_detail_data.total == 0:
                logger.info(f"商品 {goods_detail_data.goods_name} 已售罄, 自动跳过")
                continue
            try:
                goods_data['cookie'] = user_dict[goods_data['mys_uid']].cookie
                goods_data['task_id'] = goods_key
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
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def init_exchange():
    """
    开始任务
    """
    try:
        scheduler.start()
        task_list = await init_task()
        if not task_list:
            return True
        for task_data in task_list:
            scheduler.add_job(id=task_data.task_id, trigger='date', func=task_data.run_task,
                              next_run_time=datetime.fromtimestamp(task_data.exchange_time))
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def scheduler_wait_listener(event):
    """
    监听等待定时任务事件
    """
    try:
        if event.code == EVENT_JOB_MISSED:
            print(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            print(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            print(f"任务 {event.job_id} 已执行")
            scheduler_list = scheduler.get_jobs()
            if scheduler_list:
                print(f"下次运行时间为: {scheduler_list[0].next_run_time}")
            else:
                print("所有兑换任务已完成")
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def wait_tasks():
    """
    等待任务完成
    """
    try:
        if not scheduler.get_jobs():
            logger.info("没有任务需要执行")
            await async_input("按回车键返回主菜单\n")
            return True
        print("正在等待任务完成")
        scheduler.add_listener(scheduler_wait_listener, EVENT_JOB_MISSED | EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        scheduler_list = scheduler.get_jobs()
        print(f"当前任务数量为: {len(scheduler_list)} 个")
        print(f"下次运行时间为: {scheduler_list[0].next_run_time}")
        await async_input("按回车键即可返回主菜单(使用其他功能不影响定时任务运行)")
        scheduler.remove_listener(scheduler_wait_listener)
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        scheduler.remove_listener(scheduler_wait_listener)
        await async_input("按回车键继续")
        return False

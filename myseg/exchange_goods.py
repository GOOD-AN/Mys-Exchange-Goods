"""
米游社商品兑换
"""
import asyncio
import json
import sys
from datetime import datetime

import httpx
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from . import global_var as gl, async_input, logger
from . import scheduler
from .mi_tool import get_goods_detail
from .user_data import ExchangeInfo


async def post_exchange_gift(cookie, goods_id, uid, biz, region, address_id, goods_name):
    """
    兑换礼物
    需要account_id与cookie_token
    """
    try:
        exchange_goods_url = gl.mi_url + "/mall/v1/web/goods/exchange"
        exchange_goods_json = {
            "app_id": 1,
            "point_sn": "myb",
            "goods_id": str(goods_id),
            "exchange_num": 1,
            "uid": uid,
            "game_biz": biz
        }
        exchange_goods_headers = {
            "Cookie": cookie,
        }
        if region != '':
            exchange_goods_json['region'] = region
        if address_id != '':
            exchange_goods_json['address_id'] = address_id
        exchange_goods_req = ''
        async with httpx.AsyncClient() as client:
            for _ in range(gl.init_config.getint('exchange_setting', 'retry')):
                exchange_goods_req = await client.post(exchange_goods_url,
                                                       headers=exchange_goods_headers,
                                                       json=exchange_goods_json)
                if exchange_goods_req.status_code != 429:
                    break
        if exchange_goods_req == '':
            return [False, str(goods_id), goods_name]
        if exchange_goods_req.status_code != 200:
            logger.info(f"商品 {goods_id} -{goods_name} 兑换失败, 错误码为{exchange_goods_req.status_code}")
            return [False, str(goods_id), goods_name]
        exchange_goods_req_json = exchange_goods_req.json()
        if exchange_goods_req_json['data'] is None:
            logger.info(f"商品 {goods_id} -{goods_name} 兑换失败, 错误信息为{exchange_goods_req_json['message']}")
            return [False, str(goods_id), goods_name]
        return [True, str(goods_id), goods_name, exchange_goods_req_json['data']['order_sn']]
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return [False, str(goods_id), goods_name]


async def run_task(task_data):
    """
    运行任务
    """
    try:
        task_thread = gl.init_config.getint('exchange_setting', 'thread')
        account_cookie = gl.user_dict[task_data.mys_uid].cookie
        task_list = []
        for _ in range(task_thread):
            task_list.append(asyncio.create_task(
                post_exchange_gift(account_cookie, task_data.goods_id, task_data.game_id,
                                   task_data.goods_biz, task_data.game_region,
                                   task_data.address_id, task_data.goods_name)))
        for task in task_list:
            await task
        success_list = list(filter(lambda x: x.result()[0], task_list))
        if success_list:
            logger.info(f"商品 {task_list[0].result()[2]} 兑换成功, 订单号为{task_list[0].result()[3]}, 请前往米游社APP查看")
        else:
            logger.info(f"商品 {task_list[0].result()[2]} 兑换失败")
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
        with open(exchange_file_path, "r", encoding="utf-8") as exchange_file:
            try:
                goods_data_dict = json.load(exchange_file)
            except json.decoder.JSONDecodeError:
                return False
        exchange_data_dict = {}
        error_list = []
        print("将会删除所有无法兑换的商品")
        for goods_key, goods_data in goods_data_dict.items():
            goods_detail, goods_name = await get_goods_detail(goods_data['goods_id'], 'status')
            if not goods_detail:
                continue
            try:
                exchange_data_dict[goods_key] = ExchangeInfo(goods_data, goods_detail)
            except KeyError as err:
                logger.error(f"商品 {goods_key} -{goods_name} 添加失败, 错误信息为{err}")
                continue
            except ValueError as err:
                logger.error(f"商品 {goods_key} -{goods_name} 添加失败, 错误信息为{err}")
                error_list.append(goods_key)
                continue
        if error_list:
            for error_key in error_list:
                del goods_data_dict[error_key]
            with open(exchange_file_path, "w", encoding="utf-8") as exchange_file:
                json.dump(goods_data_dict, exchange_file, ensure_ascii=False, indent=4)
        return exchange_data_dict
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def init_exchange(flag=True):
    """
    开始任务
    """
    try:
        scheduler.start()
        if not flag:
            return True
        task_dict = await init_task()
        if not task_dict:
            return True
        for task_key, task_value in task_dict.items():
            scheduler.add_job(id=task_key, trigger='date', func=run_task, args=[task_value],
                              next_run_time=datetime.fromtimestamp(task_value.exchange_time))
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
            logger.warning(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            logger.error(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            logger.info(f"任务 {event.job_id} 已执行")
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
            await async_input("按回车键返回主菜单")
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

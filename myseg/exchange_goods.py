"""
米游社商品兑换
"""
import asyncio
import json
import os
import sys
from datetime import datetime

import httpx

from . import global_var as gl, async_input
from . import scheduler
from .mi_tool import get_goods_detail
from .user_data import ExchangeInfo

CHECK_URL = 'api-takumi.mihoyo.com'


async def check_exchange_status(result_list):
    """
    检测兑换状态
    """
    try:
        success_list = []
        fail_list = []
        for result in result_list:
            if result[0]:
                success_list.append(result[1])
            else:
                fail_list.append(result[1])
        if success_list:
            success_list = list(set(success_list))
            for success_info in success_list:
                print(f"商品{success_info[0]}兑换成功, 订单号为{success_info[1]}, 请前往米游社APP查看")
        if fail_list:
            fail_list = list(set(fail_list))
            for fail_info in fail_list:
                print(f"商品{fail_info}兑换失败")
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")


async def post_exchange_gift(cookie, goods_id, uid, biz, region, address_id, goods_name):
    """
    兑换礼物
    需要account_id与cookie_token
    """
    try:
        exchange_goods_url = gl.MI_URL + "/mall/v1/web/goods/exchange"
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
            for _ in range(gl.INI_CONFIG.getint('exchange_setting', 'retry')):
                exchange_goods_req = await client.post(exchange_goods_url,
                                                       headers=exchange_goods_headers,
                                                       json=exchange_goods_json)
                if exchange_goods_req.status_code != 429:
                    break
        if exchange_goods_req == '':
            return [False, str(goods_id), goods_name]
        if exchange_goods_req.status_code != 200:
            print(f"商品 {goods_id} -{goods_name} 兑换失败, 错误码为{exchange_goods_req.status_code}")
            return [False, str(goods_id), goods_name]
        exchange_goods_req_json = exchange_goods_req.json()
        if exchange_goods_req_json['data'] is None:
            print(f"商品 {goods_id} -{goods_name} 兑换失败, 错误信息为{exchange_goods_req_json['message']}")
            return [False, str(goods_id), goods_name]
        return [True, str(goods_id), goods_name, exchange_goods_req_json['data']['order_sn']]
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return [False, str(goods_id), goods_name]


async def run_task(task_data):
    """
    运行任务
    """
    try:
        task_thread = gl.INI_CONFIG.getint('exchange_setting', 'thread')
        account_cookie = gl.USER_DICT[task_data.mys_uid].cookie
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
            print(f"商品 {task_list[0].result()[2]} 兑换成功, 订单号为{task_list[0].result()[3]}, 请前往米游社APP查看")
        else:
            print(f"商品 {task_list[0].result()[2]} 兑换失败")
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def init_task():
    """
    初始化任务
    """
    try:
        exchange_file_path = os.path.join(gl.DATA_PATH, 'exchange_list.json')
        if not os.path.exists(exchange_file_path):
            return False
        with open(exchange_file_path, "r", encoding="utf-8") as exchange_file:
            try:
                goods_data_dict = json.load(exchange_file)
            except json.decoder.JSONDecodeError:
                return False
        exchange_data_list = []
        error_list = []
        print("将会删除所有无法兑换的商品")
        for goods_key, goods_data in goods_data_dict.items():
            goods_detail, goods_name = await get_goods_detail(goods_data['goods_id'], 'status')
            if not goods_detail:
                continue
            try:
                exchange_data_list.append(ExchangeInfo(goods_data, goods_detail))
            # 输出到日志
            except KeyError:
                continue
            except ValueError:
                error_list.append(goods_key)
                continue
        if error_list:
            for error_key in error_list:
                del goods_data_dict[error_key]
            with open(exchange_file_path, "w", encoding="utf-8") as exchange_file:
                json.dump(goods_data_dict, exchange_file, ensure_ascii=False, indent=4)
        return exchange_data_list
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def init_exchange(flag=True):
    """
    开始任务
    """
    try:
        scheduler.start()
        if not flag:
            return True
        task_list = await init_task()
        if not task_list:
            return True
        for task in task_list:
            schedule_id = task.mys_uid + task.goods_id
            scheduler.add_job(id=schedule_id, trigger='date', func=run_task, args=[task],
                              next_run_time=datetime.fromtimestamp(task.exchange_time))
        return True
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def wait_tasks():
    """
    等待任务完成
    """
    try:
        print("正在等待任务完成")
        await async_input("按回车键返回主菜单")
        return True
    except KeyboardInterrupt:
        print("用户强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

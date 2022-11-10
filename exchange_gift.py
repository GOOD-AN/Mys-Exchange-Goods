"""
米游社商品兑换
"""
import os
import sys
import threading
import time
import requests
from ping3 import ping

from tools import get_time, get_cookie_str, check_cookie, update_cookie, get_gift_detail, check_game_roles
import tools.global_var as gl

CHECK_URL = 'api-takumi.mihoyo.com'


def post_exchange_gift(gift_id, biz):
    """
    兑换礼物
    需要account_id与cookie_token
    """
    try:
        exchange_gift_url = gl.MI_URL + "/mall/v1/web/goods/exchange"
        exchange_gift_json = {
            "app_id": 1,
            "point_sn": "myb",
            "goods_id": str(gift_id),
            "exchange_num": 1,
            "address_id": gl.INI_CONFIG.getint('user_info', 'address_id'),
            "uid": get_cookie_str('account_id') or get_cookie_str('ltuid') or get_cookie_str('stuid'),
            "region": "cn_gf01",
            "game_biz": biz
        }
        exchange_gift_headers = {
            "Cookie": gl.MI_COOKIE,
        }
        if biz == 'bbs_cn':
            exchange_gift_json['uid'] = gl.INI_CONFIG.getint('user_info', 'game_uid')
        exchange_gift_req = ''
        for _ in range(gl.INI_CONFIG.getint('exchange_info', 'retry')):
            exchange_gift_req = requests.post(exchange_gift_url,
                                              headers=exchange_gift_headers,
                                              json=exchange_gift_json)
            if exchange_gift_req.status_code != 429:
                break
            time.sleep(1)
        if exchange_gift_req.status_code != 200:
            print("兑换请求失败")
            return False
        exchange_gift_req_json = exchange_gift_req.json()
        if exchange_gift_req_json['data'] is None:
            print(f"商品{str(gift_id)}兑换失败, 原因是{exchange_gift_req_json['message']}")
            return False
        print(f"商品{str(gift_id)}兑换成功, 订单号{exchange_gift_req_json['data']['order_sn']}")
        print("请手动前往米游社APP查看订单状态")
        return True
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def init_task():
    """
    初始化任务
    """
    try:
        gift_list = gl.INI_CONFIG.get('exchange_info', 'good_id').split(',')
        task_thread = gl.INI_CONFIG.getint('exchange_info', 'thread')
        task_list = []
        if not check_cookie():
            print("Cookie失效, 尝试更新")
            update_cookie()
        for good_id in gift_list:
            gift_biz, gift_type = get_gift_detail(good_id, 'biz')
            if not gift_biz:
                print("获取game_biz失败")
                continue
            if gift_biz != 'bbs_cn':
                if not check_game_roles(gift_biz, gl.INI_CONFIG.get('user_info', 'game_uid'), 'check'):
                    continue
            for _ in range(task_thread):
                task_list.append(
                    threading.Thread(target=post_exchange_gift,
                                     args=(good_id, gift_biz)))
        return task_list
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def run_task(task_list):
    """
    运行任务
    """
    try:
        start_timestamp = gl.INI_CONFIG.get('exchange_info', 'time')
        start_time = time.mktime(time.strptime(start_timestamp, "%Y-%m-%d %H:%M:%S"))
        ntp_enable = gl.INI_CONFIG.getboolean('ntp', 'enable')
        ntp_server = gl.INI_CONFIG.get('ntp', 'ntp_server')
        temp_time = 0
        check_network_enable = gl.INI_CONFIG.getboolean('check_network', 'enable')
        check_network_interval_time = gl.INI_CONFIG.getint('check_network', 'interval_time')
        check_network_stop_time = gl.INI_CONFIG.getint('check_network', 'stop_time')
        network_delay = 0
        check_last_time = 0
        truth_start_time = start_time
        while True:
            now_time = get_time(ntp_enable, ntp_server)
            if now_time >= truth_start_time:
                os.system(gl.CLEAR_TYPE)
                print("开始执行兑换任务")
                for task in task_list:
                    task.start()
                for task in task_list:
                    task.join()
                print("兑换任务执行完毕")
                return
            elif now_time != temp_time:
                os.system(gl.CLEAR_TYPE)
                if not check_network_enable:
                    print("网络检查未开启")
                elif truth_start_time - now_time <= check_network_stop_time:
                    print("网络检查已停止")
                elif now_time - check_last_time >= check_network_interval_time:
                    network_delay = ping(CHECK_URL, unit='ms')
                    if not network_delay or network_delay is None:
                        print("本次网络检查异常")
                    else:
                        check_last_time = now_time
                if network_delay and network_delay is not None:
                    print(f"网络延迟为 {round(network_delay, 2)} ms")
                    if network_delay >= 1000:
                        print("网络延迟过高, 请检查网络")
                        delay_time = int(network_delay / 1000)
                        print(f"程序将任务开始时间提前 {delay_time} 秒")
                        truth_start_time = start_time - delay_time
                    else:
                        truth_start_time = start_time
                print(f"当前时间 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now_time))}")
                time_t = truth_start_time - now_time
                print(
                    f"距离兑换开始还有 {int(time_t / 3600)} 小时 {int(time_t % 3600 / 60)} 分钟 {int(time_t % 60)} 秒"
                )
                temp_time = now_time
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def gift_main():
    """
    开始任务
    """
    try:
        if not gl.MI_COOKIE:
            print("请填写cookie")
            input("按回车键返回")
            return True
        task_list = init_task()
        if not task_list:
            print("没有任务, 即将返回主菜单")
            input("按回车键返回")
            return True
        run_task(task_list)
        print("程序运行完毕, 即将返回主菜单")
        input("按回车键返回")
        return True
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False

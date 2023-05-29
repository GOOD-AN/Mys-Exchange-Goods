"""
米游社商品兑换
"""
import sys
from apscheduler.events import EVENT_JOB_MISSED, EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from datetime import datetime

from .cli_tool import async_input, scheduler
from ..exchange_goods import init_exchange, ExchangeGoods
from ..user_log import logger


def cli_scheduler_wait_listener(event):
    """
    cli监听等待定时任务事件
    """
    try:
        if event.code == EVENT_JOB_MISSED:
            print(f"任务 {event.job_id} 已错过")
        elif event.code == EVENT_JOB_ERROR:
            print(f"任务 {event.job_id} 运行出错, 错误为: {event.exception}")
        elif event.code == EVENT_JOB_EXECUTED:
            scheduler_list = scheduler.get_jobs()
            if scheduler_list:
                print(f"下次运行时间为: {scheduler_list[0].next_run_time}\n")
            else:
                print("所有兑换任务已完成")
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def cli_wait_tasks():
    """
    cli等待任务完成
    """
    try:
        if not scheduler.get_jobs():
            logger.info("没有任务需要执行")
            await async_input("按回车键返回主菜单\n")
            return True
        print("正在等待任务完成")
        scheduler.add_listener(cli_scheduler_wait_listener, EVENT_JOB_MISSED | EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        scheduler_list = scheduler.get_jobs()
        print(f"当前任务数量为: {len(scheduler_list)} 个")
        print(f"下次运行时间为: {scheduler_list[0].next_run_time}")
        print("按回车键即可返回主菜单(使用其他功能不影响定时任务运行)")
        await async_input()
        scheduler.remove_listener(cli_scheduler_wait_listener)
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        scheduler.remove_listener(cli_scheduler_wait_listener)
        await async_input("按回车键继续")
        return False


async def cli_show_result(task_data: ExchangeGoods):
    """
    cli输出兑换结果
    """
    try:
        run_result = await task_data.run_task()
        if not run_result:
            print(f"账号 {task_data.mys_uid} 商品 {task_data.goods_name} 兑换失败")
        else:
            print(f"账号 {task_data.mys_uid} 商品 {task_data.goods_name} 兑换成功, 订单号为: {run_result}, "
                  f"请在米游社个人中心查看兑换结果")
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False


async def cli_init_task():
    """
    cli初始化任务
    """
    try:
        print("正在初始化任务")
        wait_exchange_list = await init_exchange()
        if not wait_exchange_list:
            return True
        for exchange_data in wait_exchange_list:
            scheduler.add_job(id=exchange_data.task_id, trigger='date', func=cli_show_result, args=(exchange_data,),
                              next_run_time=datetime.fromtimestamp(exchange_data.exchange_time))
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 原因为{err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False

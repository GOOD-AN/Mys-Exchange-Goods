"""
运行主程序
"""

import asyncio
import os
import sys
import time
from getpass import getuser

from myseg import async_input, check_update, info_menu, init_exchange, wait_tasks
from myseg import check_cookie, update_cookie
from myseg import user_global_var as gl, logger

MAIN_VERSION = '3.0.2'
MESSAGE = f"""\
===========================================
|        Mys Exchange Goods v{MAIN_VERSION:13s}|
===========================================
Description: 用于自动兑换米游社礼物
Author     : GOOD-AN
Blog       : https://blog.goodant.top/
LICENSE    : MIT
===========================================
"""


async def check_all_cookie():
    """
    检查所有cookie是否有效
    """
    try:
        if not gl.user_dict or not gl.init_config.getboolean('update_setting', 'check_account_enable'):
            return True
        logger.info("检查所有cookie是否有效...")
        expires_account = []
        for account in gl.user_dict.values():
            check_cookie_result = await check_cookie(account)
            if check_cookie_result == -1:
                logger.info(f"账号: {account['mys_uid']} 检查失败")
            elif check_cookie_result == 0:
                expires_account.append(account)
        if expires_account:
            if gl.init_config.getboolean('update_setting', 'update_account_enable'):
                logger.info("检测到有账号cookie过期, 尝试自动更新cookie")
                for account in expires_account:
                    update_result = await update_cookie(account)
                    if update_result:
                        gl.user_dict[account.mys_uid].cookie = update_result
                    else:
                        logger.info(f"账号: {account.mys_uid} 更新cookie失败")
                logger.info("自动更新cookie完成")
            else:
                for account in expires_account:
                    logger.info(f"账号: {account.mys_uid} cookie已过期")
                logger.info("自动更新已配置为关闭, 请手动更新cookie")
        else:
            logger.info("所有账号cookie有效")
        input("按回车键继续")
        return True
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


async def main_menu():
    """
    开始任务
    """
    try:
        await check_all_cookie()
        logger.info("初始化定时任务...")
        await init_exchange()
        while True:
            os.system(gl.clear_type)
            print("""主菜单
选择功能:
1. 获取信息
2. 等待商品兑换
3. 其他设置
4. 检查更新
0. 退出""")
            select_function = await async_input("请输入选择功能的序号: ")
            os.system(gl.clear_type)
            if select_function == "1":
                await info_menu()
            elif select_function == "2":
                await wait_tasks()
                continue
            elif select_function == "3":
                print("暂未开放")
            elif select_function == "4":
                await check_update(MAIN_VERSION)
            elif select_function == "0":
                sys.exit()
            else:
                await async_input("输入有误，请重新输入(回车以返回)")
                continue
            await async_input("按回车键继续")
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.critical(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        sys.exit()


def start_info():
    """
    开始输出信息
    """
    try:
        now_hour = time.localtime().tm_hour
        user_name = getuser()
        if now_hour < 6:
            print(f"{user_name}，夜色正浓，烟波浩渺，早起的你在做什么呢？")
        elif now_hour < 9:
            print(f"{user_name}，早上好，今天也要加油哦~")
        elif now_hour < 12:
            print(f"{user_name}，上午好，记得及时补充水分哦~")
        elif now_hour < 14:
            print(f"{user_name}，中午好，别忘记吃饭哦~身体是革命的本钱！")
        elif now_hour < 17:
            print(f"{user_name}，下午好，久坐伤身，记得起身活动一下哦~")
        elif now_hour < 19:
            print(f"{user_name}，傍晚好，炊烟四起，晚霞灿然，辛苦了。")
        elif now_hour < 22:
            print(f"{user_name}，晚上好，今天过的怎么样呢？明天也要加油哦~")
        else:
            print(f"{user_name}，夜深了，花睡了，早些休息哦~")
        print(MESSAGE)
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


if __name__ == '__main__':
    try:
        start_info()
        if gl.init_config.getboolean("update_setting", "check_enable"):
            asyncio.run(check_update(MAIN_VERSION))
        input("按回车键继续")
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as main_err:
        logger.critical(f"运行出错, 错误为: {main_err}, 错误行数为: {main_err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()

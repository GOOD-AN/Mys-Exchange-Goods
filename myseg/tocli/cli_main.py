"""
运行主程序
"""
import os
import sys
import time
from getpass import getuser

from .cli_exchange import cli_wait_tasks, cli_init_task
from .cli_get_info import info_menu
from .cli_tool import async_input, scheduler
from .. import __version__, __project_url__
from ..com_tool import check_update
from ..global_var import user_global_var as gl
from ..mi_tool import check_cookie, update_cookie
from ..user_data import user_dict
from ..user_log import logger

MESSAGE = f"""\
===========================================
|        Mys Exchange Goods v{__version__:13s}|
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
        if not user_dict or not gl.init_config.getboolean('update_setting', 'check_account_enable'):
            return True
        logger.info("检查所有cookie是否有效...")
        expires_account = []
        for account in user_dict.values():
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
                        logger.info(f"账号: {account.mys_uid} 更新cookie成功")
                        user_dict[account.mys_uid].cookie = update_result
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


async def check_project_update():
    """
    检查项目更新
    101: 检查更新失败
    102: 版本不匹配
    103: 当前版本为最新版本
    104: 当前版本低于最新版本但高于最低版本
    105: 当前版本低于最低版本
    """
    try:
        logger.info("开始检查项目更新...")
        check_status, check_info = await check_update()
        config_version = gl.init_config.get('app', 'version')
        if check_status == 101:
            print(check_info)
        elif check_status == 102:
            print(
                f"当前程序版本为v{__version__}, 配置文件版本为v{config_version}, 版本不匹配可能带来运行问题, 建议更新")
        elif check_status == 103:
            print(f"当前程序版本为v{__version__}, 配置文件版本为v{config_version}, 当前版本为最新版本")
        elif check_status == 104 or check_status == 105:
            print(f"当前程序版本为v{__version__}, 最新版本为v{check_info[1]}, 当前非最新版本")
            print("更新概览: ")
            for update_log in check_info[0]:
                print("=" * 50)
                print(u"\u3000" * 2 + f"版本: {update_log['version']}")
                print(f"更新时间: {update_log['update_time']}")
                print(f"更新说明: {update_log['update_content'][0]}")
                for content in update_log['update_content'][1:]:
                    print(u"\u3000" * 5 + content)
            if check_status == 105:
                print("当前版本过低, 程序将停止运行, 请更新程序后再使用")
                print(f"项目地址为: {__project_url__}")
                time.sleep(3)
                sys.exit()
        else:
            print(f"检查状态码为{check_status}, 检查信息为{check_info}")
        print(f"项目地址为: {__project_url__}")
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.critical(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False


async def main_menu():
    """
    开始任务
    """
    try:
        await check_all_cookie()
        scheduler.start()
        await cli_init_task()
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
                await cli_wait_tasks()
                continue
            elif select_function == "3":
                print("暂未开放")
            elif select_function == "4":
                await check_project_update()
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


async def cli_main():
    """
    命令行主函数
    """
    try:
        os.system(gl.clear_type)
        start_info()
        if gl.init_config.getboolean("update_setting", "check_enable"):
            await check_project_update()
        input("按回车键继续")
        await main_menu()
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as main_err:
        logger.critical(f"运行出错, 错误为: {main_err}, 错误行数为: {main_err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()

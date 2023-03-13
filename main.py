"""
运行主程序
"""

import os
import sys
import time
import asyncio
from getpass import getuser

from tools import check_update, check_cookie, update_cookie, init_config
from plugin import info_main, gift_main, config_main
import tools.global_var as gl

MAIN_VERSION = '2.0.5'
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


def start():
    """
    开始任务
    """
    try:
        if gl.MI_COOKIE and not check_cookie():
            gl.standard_log.info("Cookie失效, 尝试更新")
            update_cookie()
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""主菜单
选择功能:
1. 获取信息
2. 兑换商品
3. 其他设置
4. 检查更新
0. 退出""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                info_main()
            elif select_function == "2":
                asyncio.run(gift_main())
            elif select_function == "3":
                config_main()
            elif select_function == "4":
                check_update(MAIN_VERSION)
                input("按回车键继续")
            elif select_function == "0":
                sys.exit()
            else:
                input("输入有误，请重新输入(回车以返回)")
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
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
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


if __name__ == '__main__':
    try:
        start_info()
        init_config()
        # check_update(MAIN_VERSION)
        input("按回车键继续")
        start()
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as main_err:
        gl.standard_log.error(f"运行出错, 错误为: {main_err}, 错误行数为: {main_err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()

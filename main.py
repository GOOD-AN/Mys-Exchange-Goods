"""
运行主程序
"""

from os import path, system
from sys import exit, argv

from tools import check_plat, check_update, load_config, check_cookie, update_cookie
from get_info import info_main
from exchange_gift import gift_main
import tools.global_var as gl


def start():
    """
    开始任务
    """
    try:
        if gl.MI_COOKIE and not check_cookie():
            print("Cookie失效, 尝试更新")
            update_cookie()
        while True:
            system(gl.CLEAR_TYPE)
            print("""选择功能:
1. 获取信息
2. 兑换商品
3. 检查更新
0. 退出""")
            select_function = input("请输入选择功能的序号: ")
            system(gl.CLEAR_TYPE)
            if select_function == "1":
                info_main()
            elif select_function == "2":
                gift_main()
            elif select_function == "3":
                check_update()
                input("按回车键继续")
            elif select_function == "0":
                exit()
            else:
                input("输入有误，请重新输入(回车以返回)")
    except KeyboardInterrupt:
        print("强制退出")
        exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        exit()


if __name__ == '__main__':
    try:
        gl.CONFIG_PATH = path.join(path.dirname(argv[0]), "config")
        gl.INI_CONFIG = load_config()
        gl.CLEAR_TYPE = check_plat()
        check_update()
        input("按回车键继续")
        gl.MI_COOKIE = gl.INI_CONFIG.get('user_info', 'cookie').strip(" ")
        start()
    except KeyboardInterrupt:
        print("强制退出")
        exit()
    except Exception as main_err:
        print(f"运行出错, 错误为: {main_err}, 错误行数为: {main_err.__traceback__.tb_lineno}")
        input("按回车键继续")
        exit()

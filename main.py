'''
运行主程序
'''

import os
import sys

from com_tool import check_plat, check_update, load_config, check_cookie, update_cookie
from get_info import info_main
from exchange_gift import gift_main
import global_var as gl


def start():
    '''
    开始任务
    '''
    try:
        if gl.MI_COOKIE and not check_cookie():
            print("Cookie失效, 尝试更新")
            update_cookie()
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""选择功能:
1. 获取信息
2. 兑换商品
3. 检查更新
0. 退出""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                info_main()
            elif select_function == "2":
                gift_main()
            elif select_function == "3":
                check_update()
            elif select_function == "0":
                sys.exit()
            else:
                input("输入有误，请重新输入(回车以返回)")
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as err:
        print(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()


if __name__ == '__main__':
    try:
        gl.INI_CONFIG = load_config()
        gl.CLEAR_TYPE = check_plat()
        check_update()
        gl.MI_COOKIE = gl.INI_CONFIG.get('user_info', 'cookie').strip(" ")
        start()
    except KeyboardInterrupt:
        print("强制退出")
        sys.exit()
    except Exception as main_err:
        print(f"运行出错, 错误为: {main_err}, 错误行数为: {main_err.__traceback__.tb_lineno}")
        input("按回车键继续")
        sys.exit()

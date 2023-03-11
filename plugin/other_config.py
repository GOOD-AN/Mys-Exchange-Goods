"""
其他设置
"""
import time
import os
import sys
import ping3

import tools.global_var as gl
from tools import write_config_file


def set_time_s(sec, key, message):
    """
    设置检查相关时间或商品兑换相关次数
    """
    try:
        config_times = gl.INI_CONFIG.getint(sec, key)
        if isinstance(config_times, int) and config_times >= 0:
            print(f"当前{message}为: {config_times}{'秒' if sec != 'exchange_info' else ''}")
            choice = input(f"是否修改(默认为Y)(Y/N): ")
            if choice in ('n', 'N'):
                return True
        while True:
            input_times = input(f"请输入{message}: ")
            if input_times == "":
                choice = input(f"未输入数据，是否重新输入(默认为Y)(Y/N): ")
                if choice in ('n', 'N'):
                    return True
                continue
            if input_times.isdigit() and int(input_times) >= 0:
                write_config_file(sec, key, input_times)
                return True
            choice = input(f"输入有误，是否请重新输入(默认为Y)(Y/N): ")
            if choice in ('n', 'N'):
                return True
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def set_exchange_time():
    """
    设置商品兑换时间
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            config_time = gl.INI_CONFIG.get('exchange_info', 'time')
            if config_time:
                try:
                    now_time = time.strftime("%Y年%m月%d日 %H:%M:%S", time.strptime(config_time, "%Y-%m-%d %H:%M:%S"))
                    print(f"当前商品兑换时间为: {now_time}")
                except ValueError:
                    print(f"当前商品兑换时间为: {config_time}")
                choice = input(f"是否修改(默认为Y)(Y/N): ")
                if choice in ('n', 'N'):
                    return True
            while True:
                input_time = input("请输入商品兑换时间(格式为: 年-月-日 时:分:秒): ")
                if input_time == "":
                    choice = input(f"未输入数据，是否重新输入(默认为Y)(Y/N): ")
                    if choice in ('n', 'N'):
                        return True
                    continue
                try:
                    time.strptime(input_time, "%Y-%m-%d %H:%M:%S")
                    write_config_file('exchange_info', 'time', input_time)
                    return True
                except ValueError:
                    print("输入的时间格式有误，请重新输入")
                    continue
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def config_goods():
    """
    商品兑换相关设置
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""商品兑换相关设置菜单
选择功能:
1. 设置商品兑换时间
2. 设置单商品兑换同时发出请求数量
3. 设置单商品兑换重试次数
0. 返回上一级菜单""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                set_exchange_time()
            elif select_function == "2":
                set_time_s('exchange_info', 'thread', '单商品兑换同时发出请求数量')
            elif select_function == "3":
                set_time_s('exchange_info', 'retry', '单商品兑换重试次数')
            elif select_function == "0":
                return True
            else:
                print("输入有误，请重新输入(回车以返回)")
            input("按回车键继续")
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def set_ntp_server():
    """
    设置ntp服务器地址
    """
    try:
        config_ntp = gl.INI_CONFIG.get('ntp', 'ntp_server')
        if config_ntp:
            print(f"当前NTP服务器地址为: {config_ntp}")
            choice = input(f"是否修改(默认为Y)(Y/N): ")
            if choice in ('n', 'N'):
                return True
        while True:
            input_server = input("请输入NTP服务器地址: ")
            if input_server == "":
                choice = input(f"未输入数据，是否重新输入(默认为Y)(Y/N): ")
                if choice in ('n', 'N'):
                    return True
                continue
            if not ping3.ping(input_server, timeout=3):
                choice = input(f"输入的NTP服务器地址3秒内无法ping通，是否写入，否则重新输入(默认为Y)(Y/N): ")
                if choice in ('n', 'N'):
                    continue
            write_config_file('ntp', 'ntp_server', input_server)
            return True
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def set_enable(fun, message):
    """
    设置是否启用
    """
    try:
        config_enable = gl.INI_CONFIG.getboolean(fun, 'enable')
        if config_enable:
            choice = input(f"是否关闭{message}功能(默认为Y)(Y/N): ")
        else:
            choice = input(f"是否启用{message}功能(默认为Y)(Y/N): ")
        if choice in ('n', 'N'):
            return True
        write_config_file(fun, 'enable', str(not config_enable))
        return True
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def config_network():
    """
    网络检查相关设置
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""网络检查相关设置菜单
选择功能:
1. 设置是否启用网络检查
2. 设置网络检查间隔时间
3. 设置网络检查停止时间
4. 设置是否启用NTP时间同步
5. 设置NTP服务器地址
0. 返回上一级菜单""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                set_enable('check_network', '网络检查')
            elif select_function == "2":
                set_time_s('check_network', 'interval_time', '网络检查间隔时间')
            elif select_function == "3":
                set_time_s('check_network', 'stop_time', '距离开始兑换网络检查停止时间')
            elif select_function == "4":
                set_enable('ntp', 'NTP时间同步')
            elif select_function == "5":
                set_ntp_server()
            elif select_function == "0":
                return True
            else:
                print("输入有误，请重新输入(回车以返回)")
            input("按回车键继续")
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False


def config_main():
    """
    开始任务
    """
    try:
        while True:
            os.system(gl.CLEAR_TYPE)
            print("""其他设置菜单
选择功能:
1. 商品兑换相关设置
2. 网络检查相关设置
3. 通知相关设置
0. 返回主菜单""")
            select_function = input("请输入选择功能的序号: ")
            os.system(gl.CLEAR_TYPE)
            if select_function == "1":
                config_goods()
            elif select_function == "2":
                config_network()
            elif select_function == "3":
                print("该功能暂未开放")
                input("按回车键继续")
            elif select_function == "0":
                return True
            else:
                input("输入有误，请重新输入(回车以返回)")
    except KeyboardInterrupt:
        gl.standard_log.warning("用户强制退出")
        sys.exit()
    except Exception as err:
        gl.standard_log.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        input("按回车键继续")
        return False

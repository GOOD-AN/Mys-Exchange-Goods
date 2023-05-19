"""
CLI for myseg
"""
import sys

from myseg.global_var import user_global_var as gl

result = gl.load_config()
if result != 101:
    print(f"配置文件加载失败, 错误为: {result}")
    input("按回车键继续")
    sys.exit()
result = gl.check_plat()
if result != 101:
    print(f"平台检测失败, 错误为: {result}")
    input("按回车键继续")
    sys.exit()

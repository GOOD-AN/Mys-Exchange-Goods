"""
米游社兑换所需信息获取
"""
import json
import os
import pyperclip
import re
import sys
import time
from apscheduler.events import EVENT_JOB_ADDED, EVENT_JOB_MODIFIED, EVENT_JOB_MISSED, EVENT_JOB_REMOVED
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, Union, List, Tuple

from .cli_exchange import cli_show_result
from .cli_tool import async_input, scheduler
from ..com_tool import save_user_file, save_exchange_file, get_exchange_data
from ..data_class import UserInfo, GoodsInfo
from ..exchange_goods import ExchangeGoods
from ..global_var import user_global_var as gl
from ..mi_tool import get_goods_list, get_goods_biz, get_address, get_channel_level, MYS_CHANNEL, GAME_NAME, \
    get_ticket_by_mobile, get_stoken_by_ticket, get_cookie_token_by_mobile
from ..mi_tool import update_cookie, get_goods_detail, get_game_roles, get_point
from ..user_data import user_dict
from ..user_log import logger


async def select_user(select_user_data: dict):
    """
    选择用户
    """
    try:
        print("当前已有用户有：")
        select_user_data_key = list(select_user_data)
        for mys_id in select_user_data_key:
            print(f"1. {mys_id}")
        if len(select_user_data) == 1:
            print("仅有一个用户")
            return select_user_data[select_user_data_key[0]]
        select_user_id = 0
        while True:
            select_id = await async_input("请输入选择用户的序号: ")
            if select_id.isdigit() and 0 < int(select_id) <= len(select_user_data_key):
                select_user_id = select_user_data_key[int(select_id) - 1]
                logger.info(f"选择用户为: {select_user_id}")
                break
            else:
                print("输入序号有误, 请重新输入")
                continue
        if select_user_id == 0:
            return None
        return select_user_data[select_user_id]
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        await async_input("按回车键继续")
        return False


class SelectGoods(BaseModel):
    """
    选择商品
    """

    account: Optional[UserInfo]
    select_goods_list: List[GoodsInfo] = []

    async def select_goods(self) -> bool:
        """
        选择商品
        需要账户信息
        查询某商品该账户是否兑换, 需要account_id与cookie_token
        """
        try:
            if not self.account:
                logger.info("当前没有账户信息, 请先绑定账户信息")
                return False
            while True:
                select_id_in = await async_input(
                    "请输入需要抢购的商品序号, 以空格分开, 将忽略输入错误的序号(请注意现有米游币是否足够): ")
                select_id_in = set(re.split(r'\s+', select_id_in.rstrip(' ')))
                if select_id_in and '' not in select_id_in:
                    goods_select_dict = {}
                    exchange_total_price = 0
                    old_exchange_data = await get_exchange_data()
                    for select_id in select_id_in:
                        if select_id.isdigit() and 0 < int(select_id) <= len(self.select_goods_list):
                            wait_process_goods = self.select_goods_list[int(select_id) - 1]
                            logger.debug(wait_process_goods)
                            if wait_process_goods.game_biz != 'bbs_cn' and wait_process_goods.type == 2:
                                for game_data in self.account.game_list:
                                    if self.account.mys_uid + game_data.game_uid + wait_process_goods.goods_id \
                                            in old_exchange_data:
                                        logger.info(f"商品{wait_process_goods.goods_name}已添加, 跳过")
                                        continue
                            elif (self.account.mys_uid * 2) + wait_process_goods.goods_id in old_exchange_data:
                                logger.info(f"商品{wait_process_goods.goods_name}已添加, 跳过")
                                continue
                            channel_rule = wait_process_goods.rule_for_num(1)
                            if channel_rule:
                                goods_channel = channel_rule.split(":")[0]
                                limit_level = channel_rule.split(":")[1]
                                now_channel_level = self.account.channel_dict[goods_channel]
                                if now_channel_level < int(limit_level):
                                    logger.info(f"商品{wait_process_goods.goods_name}兑换要求频道"
                                                f"{MYS_CHANNEL[goods_channel]}等级为: {limit_level}, "
                                                f"当前频道等级为{now_channel_level}, 等级不足, 跳过兑换")
                                    print("请前往米游社APP完成任务提升等级, "
                                          "如信息错误或需要更新频道信息, 请稍后使用更新频道信息功能")
                                    continue
                            game_level_rule = wait_process_goods.rule_for_num(2)
                            wait_process_game_list = []
                            if game_level_rule:
                                for game_data in self.account.game_list:
                                    if game_data.game_biz == wait_process_goods.game_biz and \
                                            game_data.level >= int(game_level_rule):
                                        wait_process_game_list.append(game_data)
                                if not wait_process_game_list:
                                    logger.info(f"商品{wait_process_goods.goods_name}兑换要求"
                                                f"{GAME_NAME[wait_process_goods.game_biz]}等级为: "
                                                f"{game_level_rule}, 当前账号没有符合要求的游戏账号, 跳过兑换")
                                    print("请前往米游社APP完成任务提升等级, "
                                          "如信息错误或需要更新游戏信息, 请稍后使用更新游戏信息功能")
                                    continue
                            wait_process_goods_dict = wait_process_goods.dict(
                                include={'goods_id', 'goods_name', 'type', 'game_biz'})
                            wait_process_goods_dict.update({'mys_uid': self.account.mys_uid,
                                                            'game_uid': self.account.mys_uid})
                            if wait_process_goods.game_biz != 'bbs_cn' and wait_process_goods.type == 2:
                                logger.info(f"商品{wait_process_goods.goods_name}为虚拟商品")
                                if not game_level_rule:
                                    wait_process_game_list = []
                                    for game_data in self.account.game_list:
                                        if game_data.game_biz == wait_process_goods.game_biz:
                                            wait_process_game_list.append(game_data)
                                if not wait_process_game_list:
                                    logger.info("当前账号没有符合要求的游戏账号, 跳过兑换")
                                    print("如信息错误或需要更新游戏信息, 请稍后使用更新游戏信息功能")
                                    continue
                                logger.info("当前符合条件的游戏账号如下")
                                logger.debug(wait_process_game_list)
                                for index, game_data in enumerate(wait_process_game_list, start=1):
                                    print("-" * 25)
                                    print(f"账户序号{index}")
                                    print(f"账户名称: {game_data.nickname}")
                                    print(f"账户UID: {game_data.game_uid}")
                                    print(f"账户等级: {game_data.level}")
                                    print(f"账户区服: {game_data.region_name}")
                                if len(wait_process_game_list) == 1:
                                    logger.info("仅有一个账号符合要求, 已自动选择")
                                    wait_process_goods_dict.update(wait_process_game_list[0].dict(
                                        include={'game_uid', 'region'}))
                                else:
                                    while True:
                                        select_game_id_in = await async_input("请输入需要兑换的账户序号: ")
                                        if select_game_id_in.isdigit() and \
                                                0 < int(select_game_id_in) <= len(wait_process_game_list):
                                            wait_process_goods_dict.update(
                                                wait_process_game_list[int(select_game_id_in) - 1].dict(
                                                    include={'game_uid', 'region'}))
                                            break
                                        else:
                                            print("输入错误, 请重新输入")
                            elif wait_process_goods.type == 1 or wait_process_goods.type == 4:
                                logger.info(f"商品{wait_process_goods.goods_name}为实物奖品")
                                if not self.account.address_list:
                                    logger.info("当前账号未找到收货地址, 跳过兑换")
                                    print("请前往米游社APP添加收货地址, "
                                          "如信息错误或需要更新收货地址, 请稍后使用更新收货地址功能")
                                    continue
                                logger.info("当前账号收货地址如下")
                                for index, address_data in enumerate(self.account.address_list, start=1):
                                    print("-" * 25)
                                    print(f"地址序号: {index}")
                                    print(f"收货人姓名: {address_data.connect_name}")
                                    print(f"联系电话: {address_data.connect_phone}")
                                    print(f"地址: {address_data.full_address}")
                                if len(self.account.address_list) == 1:
                                    logger.info("仅有一个收货地址, 已自动选择")
                                    wait_process_goods_dict.update({'address_id': self.account.address_list[0].id})
                                else:
                                    while True:
                                        select_address_id_in = await async_input("请输入需要兑换的地址序号: ")
                                        if select_address_id_in.isdigit() and \
                                                0 < int(select_address_id_in) <= len(self.account.address_list):
                                            wait_process_goods_dict.update(
                                                {'address_id': self.account.address_list[
                                                    int(select_address_id_in) - 1].id})
                                            break
                                        else:
                                            print("输入错误, 请重新输入")
                            exchange_limit = (wait_process_goods.account_cycle_limit -
                                              wait_process_goods.account_exchange_num)
                            wait_process_goods_dict.update({'exchange_num': exchange_limit})
                            if exchange_limit > 1:
                                while True:
                                    exchange_num_in = await async_input(f"请输入兑换数量(最多{exchange_limit}个): ")
                                    if exchange_num_in.isdigit() and 0 < int(exchange_num_in) <= exchange_limit:
                                        wait_process_goods_dict.update({'exchange_num': int(exchange_num_in)})
                                        break
                                    else:
                                        print("输入错误, 请重新输入")
                            wait_process_goods_dict.update({'exchange_time': wait_process_goods.exchange_time})
                            goods_select_dict.update({self.account.mys_uid + wait_process_goods_dict['game_uid'] +
                                                      wait_process_goods_dict['goods_id']: wait_process_goods_dict})
                            exchange_total_price += wait_process_goods.price * wait_process_goods_dict['exchange_num']
                    if not goods_select_dict:
                        logger.info("所选商品均不符合兑换条件或重复添加, 请重新选择")
                        await async_input("按回车键继续")
                        return True
                    user_point = await get_point(self.account)
                    if exchange_total_price > user_point:
                        print(f"当前米游币不足, 当前米游币数量: {str(user_point)}, "
                              f"所需米游币数量: {str(exchange_total_price)}")
                        choice = await async_input("是否继续选择商品, 取消将返回(默认为Y)(Y/N): ")
                        if choice.lower() in ('n', 'no'):
                            continue
                    old_exchange_data.update(goods_select_dict)
                    await save_exchange_file(old_exchange_data)
                    for task_key, task_value in goods_select_dict.items():
                        task_value.update({'cookie': self.account.cookie, 'task_id': task_key})
                        wait_task = ExchangeGoods.parse_obj(task_value)
                        scheduler.add_job(id=task_key, trigger='date', func=cli_show_result, args=(wait_task,),
                                          next_run_time=datetime.fromtimestamp(wait_task.exchange_time))
                    await async_input("添加兑换任务成功, 按回车键继续")
                    return True
                else:
                    logger.info("未选择任何商品")
                    choice = await async_input("是否重新选择商品(默认为Y)(Y/N): ")
                    if choice in ('n', 'N'):
                        break
            return True
        except KeyboardInterrupt:
            logger.warning("用户强制退出")
            input("按回车键继续")
            sys.exit()
        except Exception as err:
            logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False

    async def show_goods_list(self) -> bool:
        """
        获取商品列表
        需要账户信息
        查询某商品该账户是否兑换, 需要account_id与cookie_token
        """
        try:
            goods_biz_list = await get_goods_biz()
            while True:
                os.system(gl.clear_type)
                print("查询商品列表菜单")
                for index, goods_biz in enumerate(goods_biz_list, start=1):
                    print(f"{str(index)}. {goods_biz[0]}")
                print(f"{len(goods_biz_list) + 1}. 更新商品列表菜单")
                print("0. 返回上一级")
                game_choice = await async_input("请输入需要查询的序号: ")
                if not game_choice.isdigit():
                    await async_input("输入有误, 请重新输入(回车以返回)")
                    continue
                if game_choice == str(len(goods_biz_list) + 1):
                    goods_biz_list = await get_goods_biz()
                    continue
                elif game_choice == "0":
                    return False
                game_choice = int(game_choice) - 1
                if game_choice < 0 or game_choice >= len(goods_biz_list):
                    await async_input("输入有误, 请重新输入(回车以返回)")
                    continue
                goods_list_data = await get_goods_list(goods_biz_list[game_choice][1])
                if not goods_list_data:
                    await async_input("获取商品列表失败或当前没有可兑换商品, 请稍后重试(回车以返回)")
                    continue
                goods_num = 1
                for goods_data in goods_list_data:
                    # unlimit 为 False 表示兑换总数量有限制
                    # next_num 表示下次兑换总数量
                    # total 表示当前可兑换总数量
                    if not goods_data.unlimit and goods_data.total == 0 and goods_data.next_num == 0 \
                            or goods_data.account_cycle_limit == goods_data.account_exchange_num:
                        continue
                    goods_data = await get_goods_detail(goods_data.goods_id)
                    if not goods_data:
                        print(f"获取商品详情失败, 商品序号: {str(goods_num)}, 商品名称: {goods_data.goods_name}")
                        continue
                    print("-" * 25)
                    print(f"商品序号: {str(goods_num)}")
                    print(f"商品名称: {goods_data.goods_name}")
                    print(f"商品价格: {goods_data.price} 米游币")
                    if goods_data.total == 0 and goods_data.next_num == 0:
                        print("商品库存: 无限")
                    else:
                        print(f"商品库存: {goods_data.total or goods_data.next_num}")
                    exchange_time = goods_data.exchange_time
                    if exchange_time == -1:
                        print("商品兑换时间: 当前任何时段")
                    else:
                        print(
                            f"商品兑换时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exchange_time))}")
                    # month 为每月限购
                    if goods_data.account_cycle_type == "forever":
                        print(f"每人限购: {goods_data.account_cycle_limit} 个")
                    else:
                        print(f"本月限购: {goods_data.account_cycle_limit} 个")
                    self.select_goods_list.append(goods_data)
                    goods_num += 1
                if not self.select_goods_list:
                    await async_input("没有可兑换的商品(回车以返回)")
                if self.account:
                    choice = await async_input("是否要选择兑换的商品(默认为Y)(Y/N): ")
                    if choice.lower() in ('n', 'no'):
                        self.select_goods_list.clear()
                        continue
                    await self.select_goods()
                else:
                    await async_input("如需选择兑换商品, 请先登录账户(回车以返回)")
        except KeyboardInterrupt:
            logger.warning("用户强制退出")
            input("按回车键继续")
            sys.exit()
        except Exception as err:
            logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False

    async def modify_exchange(self):
        """
        修改兑换信息
        """
        try:
            os.system(gl.clear_type)
            old_exchange_data = await get_exchange_data()
            if not scheduler.get_jobs() or not old_exchange_data:
                logger.info("当前没有兑换商品")
                return True
            print("当前兑换商品如下:")
            wait_select_exchange_list = []
            for index, (exchange_key, exchange_value) in enumerate(old_exchange_data.items(), start=1):
                if self.account and exchange_value['mys_uid'] != self.account.mys_uid:
                    continue
                print("-" * 25)
                print(f"兑换信息序号: {index}")
                print(f"兑换商品名称: {exchange_value['goods_name']}")
                print(f"兑换商品数量: {exchange_value['exchange_num']} 个")
                print(f"兑换账户: {exchange_value['mys_uid']}")
                if exchange_value['game_biz'] != 'bbs_cn' and exchange_value['type'] == 2:
                    if not self.account:
                        game_list = user_dict[exchange_value['mys_uid']].game_list
                    else:
                        game_list = self.account.game_list
                    for game_data in game_list:
                        if game_data.game_uid == exchange_value['game_uid']:
                            print(f"虚拟商品接收游戏账号UID: {game_data.game_uid}")
                            print(f"虚拟商品接收游戏账号昵称: {game_data.nickname}")
                            print(f"虚拟商品接收游戏账号区服: {game_data.region_name}")
                            break
                if 'address_id' in exchange_value:
                    if not self.account:
                        address_list = user_dict[exchange_value['mys_uid']].address_list
                    else:
                        address_list = self.account.address_list
                    for address_data in address_list:
                        if address_data.id == exchange_value['address_id']:
                            print(f"收货地址: {address_data.full_address}")
                            break
                wait_select_exchange_list.append(exchange_key)
            if not wait_select_exchange_list:
                logger.info("当前没有兑换商品")
                return True
            wait_select_exchange = []
            while True:
                select_id_in = await async_input(
                    "请输入需要删除的兑换信息序号, 以空格分开, 将忽略输入错误的序号(输入0退出): ")
                select_id_in = set(re.split(r'\s+', select_id_in.rstrip(' ')))
                if '0' in select_id_in:
                    return True
                if select_id_in and '' not in select_id_in:
                    for select_id in select_id_in:
                        if select_id.isdigit() and 0 < int(select_id) <= len(wait_select_exchange_list):
                            wait_select_exchange.append(wait_select_exchange_list[int(select_id) - 1])
                    break
                else:
                    print("输入错误, 请重新输入")
            if not wait_select_exchange:
                logger.info("当前没有选择商品")
                return True
            while True:
                # select_id_in = await async_input("请输入需要进行的操作:\n1. 删除：")
                select_id_in = '1'
                if select_id_in == '1':
                    for wait_select in wait_select_exchange:
                        del old_exchange_data[wait_select]
                        scheduler.remove_job(wait_select)
                    with open(gl.data_path / 'exchange_list.json', "w", encoding="utf-8") as exchange_file:
                        json.dump(old_exchange_data, exchange_file, ensure_ascii=False, indent=4)
                    logger.info("删除成功")
                    break
                elif select_id_in == '2':
                    print("修改功能暂未开放")
                else:
                    print("输入错误, 请重新输入")
        except KeyboardInterrupt:
            logger.warning("用户强制退出")
            input("按回车键继续")
            sys.exit()
        except Exception as err:
            logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
            return False


async def get_cookie() -> Union[bool, Tuple[str, str]]:
    """
    https://user.mihoyo.com/#/login/captcha
    获取app端cookie
    参考:
    https://bbs.tampermonkey.net.cn/thread-1040-1-1.html
    https://github.com/Womsxd/MihoyoBBSTools/blob/master/login.py
    """
    try:
        login_url = 'https://user.mihoyo.com/#/login/captcha'
        print(f"请在浏览器打开{login_url}, 输入手机号后获取验证码, 但不要登录, 然后在下方按提示输入数据。")
        try:
            pyperclip.copy(login_url)
            print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        except Exception:
            print("无法复制地址到剪贴板, 请手动复制")
        mobile = await async_input("请输入手机号(输入0退出): ")
        if mobile == '0':
            return False
        while True:
            mobile_captcha = await async_input("请输入验证码(输入0退出): ")
            if mobile_captcha == '0':
                return False
            get_cookie_ticket_data = await get_ticket_by_mobile(mobile, mobile_captcha)
            if not get_cookie_ticket_data:
                return False
            elif get_cookie_ticket_data == -201:
                continue
            else:
                break
        user_cookie_one = get_cookie_ticket_data[0]
        mys_uid = get_cookie_ticket_data[1]

        get_stoken_data = await get_stoken_by_ticket(user_cookie_one['login_ticket'], mys_uid)
        if not get_stoken_data:
            return False

        print("重新在此页面(刷新或重新打开)获取验证码, 依旧不要登录, 在下方输入数据。")
        try:
            pyperclip.copy(login_url)
            print("已将地址复制到剪贴板, 若无法粘贴请手动复制")
        except Exception:
            print("无法复制地址到剪贴板, 请手动复制")
        while True:
            mobile_captcha = await async_input("请输入第二次验证码(输入0退出): ")
            if mobile_captcha == '0':
                return False
            user_cookie_two = await get_cookie_token_by_mobile(mobile, mobile_captcha)
            if not user_cookie_two:
                return False
            elif user_cookie_two == -201:
                continue
            else:
                break
        uer_cookie = ""
        for key, value in user_cookie_two.items():
            uer_cookie += key + "=" + value + ";"
        uer_cookie += "login_ticket=" + user_cookie_one['login_ticket'] + ";"
        uer_cookie += "stoken=" + get_stoken_data + ";"
        uer_cookie += "stuid=" + user_cookie_two['account_id'] + ";"
        return uer_cookie, mys_uid
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def get_user_info() -> Union[bool, UserInfo]:
    """
    获取用户信息
    """
    try:
        user_cookie_data = await get_cookie()
        if not user_cookie_data:
            return False
        user_cookie = user_cookie_data[0]
        mys_uid = user_cookie_data[1]
        new_user = UserInfo.parse_obj({'mys_uid': mys_uid, 'cookie': user_cookie})
        print("等待获取其他信息")
        new_user = await get_channel_level(new_user)
        new_user = await get_game_roles(new_user)
        new_user = await get_address(new_user)
        if new_user.is_not_none:
            new_user = await save_user_file(new_user, "用户信息")
            return new_user
        else:
            return False
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


def scheduler_get_listener(event):
    """
    监听设置任务事件
    """
    try:
        if event.code == EVENT_JOB_ADDED:
            print(f"任务 {event.job_id} 已添加")
        elif event.code == EVENT_JOB_REMOVED:
            print(f"任务 {event.job_id} 已删除")
        elif event.code == EVENT_JOB_MODIFIED:
            print(f"任务 {event.job_id} 已修改")
        elif event.code == EVENT_JOB_MISSED:
            print(f"任务 {event.job_id} 已错过")
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        return False


async def info_menu():
    """
    开始获取信息任务
    """
    try:
        scheduler.add_listener(scheduler_get_listener,
                               EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED | EVENT_JOB_MISSED)
        account = None
        if user_dict:
            account = await select_user(user_dict)
            await async_input("按回车键继续")
        while True:
            os.system(gl.clear_type)
            print("""获取信息菜单
选择功能:
1. 获取账户信息
2. 查询设置兑换商品
3. 修改兑换信息(暂仅支持删除)
4. 查询当前米游币数量
5. 更新Cookie
6. 更新游戏账号信息
7. 更新收货地址信息
8. 更新频道等级信息
9. 重新选择账户
0. 返回主菜单""")
            select_function = await async_input("请输入选择功能的序号: ")
            os.system(gl.clear_type)
            if select_function.isdigit() and 3 <= int(select_function) <= 8 and not account:
                print("请先选择账户或获取账户后, 再进行此操作")
                await async_input("按回车键继续")
                continue
            if select_function == "1":
                new_account = await get_user_info()
                if new_account:
                    account = new_account
                    user_dict.update({account.mys_uid: account})
                    logger.info(f"获取账户信息成功, 已切换用户为{account.mys_uid}")
                else:
                    logger.info("获取账户信息失败")
            elif select_function == "2":
                await SelectGoods.parse_obj({'account': account}).show_goods_list()
            elif select_function == "3":
                await SelectGoods.parse_obj({'account': account}).modify_exchange()
            elif select_function == "4":
                now_point = await get_point(account)
                if now_point:
                    print(f"当前米游币数量: {str(now_point)}")
                else:
                    logger.info("未获取到米游币数量")
            elif select_function == "5":
                update_data = await save_user_file(await update_cookie(account), "Cookie")
                if update_data:
                    account = update_data
                    print("更新Cookie成功")
                else:
                    print("更新Cookie失败")
            elif select_function == "6":
                update_data = await save_user_file(await get_game_roles(account), "游戏账号")
                if update_data:
                    account = update_data
                    print("更新游戏账号信息成功")
                else:
                    print("更新游戏账号信息失败")
            elif select_function == "7":
                update_data = await save_user_file(await get_address(account), "收货地址")
                if update_data:
                    account = update_data
                    print("更新收货地址信息成功")
                else:
                    print("更新收货地址信息失败")
            elif select_function == "8":
                update_data = await save_user_file(await get_channel_level(account), "频道等级")
                if update_data:
                    account = update_data
                    print("更新频道等级信息成功")
                else:
                    print("更新频道等级信息失败")
            elif select_function == "9":
                if user_dict:
                    account = await select_user(user_dict)
                else:
                    logger.warning("暂无账户信息, 请先获取账户信息")
            elif select_function == "0":
                scheduler.remove_listener(scheduler_get_listener)
                return
            else:
                await async_input("输入有误, 请重新输入(回车以返回)")
                continue
            await async_input("按回车键继续")
    except KeyboardInterrupt:
        logger.warning("用户强制退出")
        input("按回车键继续")
        sys.exit()
    except Exception as err:
        logger.error(f"运行出错, 错误为: {err}, 错误行数为: {err.__traceback__.tb_lineno}")
        scheduler.remove_listener(scheduler_get_listener)
        await async_input("按回车键继续")
        return False

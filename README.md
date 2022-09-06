# mys_exch_goods
用于兑换米游社商品

## 使用说明

### 安装所需运行库

`pip install -r requirements.txt`

### 配置`config.ini`文件

| 参数       | 说明                                                         |
| ---------- | ------------------------------------------------------------ |
| cookie     | 用户`cookie`数据, 使用`get_info.py`获取                      |
| uid        | 用户游戏内UID, 暂需手动填写, 填写为需要兑换的游戏商品对应的UID, 暂只支持一个 |
| address_id | 用户收货地址ID, 使用`get_info.py`获取                        |
| good_id    | 需要兑换的商品ID, 使用`get_info.py`获取                      |
| time       | 兑换商品的开始时间, 需手动填写                               |
| thread     | 每个商品同时请求兑换的线程数                                 |
| ntp_server | ntp对时服务器                                                |

** [\*] 其余参数暂未使用, 可忽略**

#### 示例

```ini
[user_info]
cookie = account_id=123456879;cookie_token=123456789qwert;ltuid=123456879;aliyungf_tc=123456789qwe;login_ticket=123456789qwert;
uid = 123789456
address_id = 1234

[exchange_info]
good_id = 20220513112546,20220513226423
time = 2022-01-01 12:00:00
thread = 3

[ntp]
ntp_server = ntp.aliyun.com
```

### 运行`exchange_gift.py`

`python exchange_gift.py`

## 其他

本项目仅供学习使用，若出现任何问题，本项目及其发起人与参与者不承担任何责任。

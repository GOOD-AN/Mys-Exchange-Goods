# Mys-Exchange-Goods
用于兑换米游社商品

## 使用说明

### 安装所需运行库

`pip install -r requirements.txt`

### 配置`config.ini`文件

[user_info]

| 参数       | 说明                                                         |
| ---------- | ------------------------------------------------------------ |
| cookie     | 用户`cookie`数据                                             |
| uid        | 用户游戏内UID, 暂需手动填写, 填写为需要兑换的游戏商品对应的UID, 暂只支持一个 |
| address_id | 用户收货地址ID                                               |

[exchange_info]

| 参数    | 说明                           |
| ------- | ------------------------------ |
| good_id | 需要兑换的商品ID               |
| time    | 兑换商品的开始时间, 需手动填写 |
| thread  | 每个商品同时请求兑换的线程数   |
| retry   | 请求时重试次数                 |

[check_network]

| 参数          | 说明                                |
| ------------- | ----------------------------------- |
| enable        | 是否启用网络检查                    |
| interval_time | 检查间隔, 单位 秒                   |
| stop_time     | 距开始兑换多长时间停止检查, 单位 秒 |

[ntp]

| 参数       | 说明          |
| ---------- | ------------- |
| enable     | 是否启用ntp   |
| ntp_server | ntp对时服务器 |

**[\*] 其余参数暂未使用, 可忽略**

#### 示例

```ini
[user_info]
cookie = account_id=...;cookie_token=...;ltuid=...;aliyungf_tc=...;login_ticket=...;stoken=...;
uid = 123789456
address_id = 1234

[exchange_info]
good_id = 20220513112546,20220513226423
time = 2022-01-01 12:00:00
thread = 3
retry = 5

[check_network]
enable = true
interval_time = 15
stop_time = 30

[ntp]
enable = true
ntp_server = ntp.aliyun.com
```

### 运行`main.py`

`python main.py`

## 其他

本项目仅供学习使用，若出现任何问题，本项目及其发起人与参与者不承担任何责任。

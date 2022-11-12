# 米游社商品兑换
<div align="left">
  <a href="https://github.com/GOOD-AN/Mys-Exchange-Goods/releases/latest" target="_blank">
    <img alt="最新发行版" src="https://img.shields.io/github/v/release/GOOD-AN/Mys-Exchange-Goods?logo=python&style=for-the-badge">
  </a>
  <img alt="Python 版本要求" src="https://img.shields.io/badge/Python-3.6+-green.svg?longCache=true&style=for-the-badge">
  <img alt="GitHub CodeQL 代码检查" src="https://img.shields.io/github/workflow/status/GOOD-AN/Mys-Exchange-Goods/CodeQL?logo=github&style=for-the-badge">
  <img alt="开源协议" src="https://img.shields.io/badge/License-mit-blue.svg?longCache=true&style=for-the-badge">
</div>

## 使用说明

*可直接运行已打包程序[在此下载](https://github.com/GOOD-AN/Mys-Exchange-Goods/releases/latest), 按第二步配置文件后, 打开exe即可使用。

以下步骤为希望源码运行的用户使用。

### 第一步、安装所需运行库

`pip install -r requirements.txt`

### 第二步、配置`config.ini`文件

*以下未标明手动填写的都可在程序内处理

**[user_info]**

| 参数         | 说明                                   |
|------------|--------------------------------------|
| cookie     | 用户`cookie`数据                         |
| uid        | 用户游戏内UID, 填写为需要兑换的游戏商品对应的UID, 暂只支持一个 |
| address_id | 用户收货地址ID                             |

**[exchange_info]**

| 参数      | 说明                    |
|---------|-----------------------|
| good_id | 需要兑换的商品ID             |
| time    | 兑换商品的开始时间, 需手动填写      |
| thread  | 每个商品同时请求兑换的线程数, 需手动填写 |
| retry   | 请求时重试次数, 需手动填写        |

**[check_network]**

| 参数            | 说明                         |
|---------------|----------------------------|
| enable        | 是否启用网络检查, 需手动填写            |
| interval_time | 检查间隔, 单位 秒, 需手动填写          |
| stop_time     | 距开始兑换多长时间停止检查, 单位 秒, 需手动填写 |

**[ntp]**

| 参数         | 说明              |
|------------|-----------------|
| enable     | 是否启用ntp, 需手动填写  |
| ntp_server | ntp对时服务器, 需手动填写 |

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

### 第三步、运行`main.py`

`python main.py`

## 致谢
感谢 `Microsoft` 提供优秀的编辑器。

<a href="https://code.visualstudio.com/" target="_blank">
  <img alt="vscode" src="https://s3.bmp.ovh/imgs/2022/11/11/a21d853cbd99f164.png" width="150"/>
</a>

感谢 `JetBrains` 提供优秀的IDE。

<a href="https://www.jetbrains.com/" target="_blank">
  <img alt="jetbrains" src="https://s3.bmp.ovh/imgs/2022/11/11/8f7309621f30a044.png" width="150"/>
</a>

## 其他

本项目仅供学习使用，请勿用于非法用途！若使用中出现任何问题，本项目及其发起人与参与者不承担任何责任。

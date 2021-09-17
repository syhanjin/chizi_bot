# nbqbot

> 使用 NoneBot2 对接 gocq 实现
>
> 需要 `Python3.7+` （建议 `Python3.8`）

## 安装依赖

```shell
pip uninstall nonebot
pip install nonebot2 pymongo datetime pillow
```

## 更新日志

### 2021-09-12

开启日志更新

已实现功能

1. 群指令 `禁言` `解禁`
2. 群功能 `签到` `关键字拦截`
3. 对接网站实现`群关键字控制台`，并通过管理员私发指令`kw`实现生成编辑链接，私发指令`rekw`实现刷新内存中关键字数据

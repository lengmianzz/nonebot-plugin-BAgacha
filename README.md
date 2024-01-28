<div align="center">

<img src="https://p.ananas.chaoxing.com/star3/origin/01a37edbd405887d97d02c1fdcb1e8bc.png" width="200" height="200" alt="Icon">

# Nonebot-Plugin-BAdrawcard  
### 《碧蓝档案》抽卡模拟插件

</div>

<p align="center">
  <img src="https://img.shields.io/github/license/lengmianzz/nonebot-plugin-BAdrawcard" alt="license">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/nonebot-2.0.0+-red.svg" alt="NoneBot">
  <a href="https://pypi.python.org/pypi/nonebot-plugin-badrawcard">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-badrawcard.svg" alt="pypi">
  </a>
</p>

## **Warning**: 使用本插件需要安装Redis!!!  




### 功能:
 - 自动更新抽卡概率
 - 自动更新up卡池, 检测更新卡池和图标库
 - 展示当前UP学生
 - 展示当前概率


### 安装:
 - 使用 nb-cli 安装  
```
nb plugin install nonebot-plugin-BAdrawcard
```

 - 使用 pip
```
pip install nonebot-plugin-badrawcard
```

### 配置:
 - proxy: 本插件需要使用代理(`http://ip:host`格式)
 - redis_host: Redis的host(默认为localhost)
 - redis_port: Redis的开放端口(默认为6379)  


### 触发:
 - `/ba单抽`
 - `/ba十连`
 - `/ba来一井`
 - `/当前概率`
 - `/当前up`

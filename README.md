<div align="center">

<img src="./images/icon.jpg" width="200" height="200" alt="Icon">

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
## 本插件只在Matcha通过onebotV11适配器测试, 不保证其他适配器可用  



<div align="center">

### 效果展示:
<img src="./images/info.jpg" width="450" height="400">

<img src="./images/drawcard1.jpg" width="450" height="400" >
<img src="./images/drawcard2.jpg" width="450" height="400" >
<img src="./images/drawcard3.jpg" width="450" height="400" >

</div>


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

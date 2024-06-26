# Python QQ-Bot框架
  
## ——这是什么？
  
一款主题由Python编写的基于onebot协议的qq机器人框架，使用面向对象的思想实现了（自认为）便于插件管理和开发的框架环境。
  
框架自带比较完善的运行日志输出系统，同时配备了由作者自己编写的web控制面板方便远程管理bot的运行情况与监测运行日志

## ——这是干什么的？
  
将来（可能）会用做24级高程群bot的开发和运行框架。
  
## ——如果要参与框架或者插件的维护和开发，你需要会什么？
  
- 至少需要了解Python的基础语法  
- 对数据的通讯技术有最基础的了解（比如知道对于一个http请求，什么是请求体，请求参数，请求头等）  
- 有阅读和仿照别人写的代码的能力
- 如果你想参与到框架本身的维护和开发，可能需要有更多知识储备......

## ——在开发插件之前，你需要做哪些准备才能运行这个框架？
  
### 1. Python运行环境  
作者本人是在Python 3.9的环境下开发的该框架，只要你的Python版本和我不要差太多都行。  
  
### 2. 项目用到的第三方库  
所有项目使用到的第三方库的要求都写在requirements.txt中，可以使用以下指令一键安装：  
在项目的根目录下使用：  
`pip install -r requirements.txt`
  
### 3. 项目推荐使用的bot监听端框架  
由于协议库基本上都被tx追杀完了，所以像cqhttp，nonebot这些框架大概是不太能继续使用的，因此本项目推荐
（至少我目前正在使用）的框架是基于对NTQQ进行Hook的插件"LLOneBot"，具体怎么部署它请自行到GitHub上搜索该项目的名字。
  
## TODO:

- [ ] 完善框架的API
- [ ] 完善框架的消息类
- [x] 将bot初始化配置文件和插件的配置文件分开管理
- [ ] 完善web控制面板
- [ ] 实现bot的基础功能插件（如：防复读，防撤回，检查群名片等）
  
## 开发须知！
  
### 1.首次开发前请从master分支新建一个自己的分支，每次开发前先检查自己的分支是否是最新的
  
### 2.在提交代码的时候，先推送到远端仓库的自己的分支中，然后发起一个pull request请求合并到master分支，***不要***！直接推送到master分支上。
  
### 3.在提交代码前，请自行检查代码，尽量减少代码出现严重bug的可能性（最好不要出现）
  
### 4.注意不要在代码中泄露隐私信息（比如：账号密码，服务器ip地址等）  

### [点击这里跳转到更详细的插件开发教程](https://github.com/JustMon1ka/QQ-Bot-New/wiki/%E4%BB%8E%E8%BF%99%E9%87%8C%E5%BC%80%E5%A7%8B%E7%AC%AC%E4%B8%80%E6%AC%A1%E5%BC%80%E5%8F%91%EF%BC%81)

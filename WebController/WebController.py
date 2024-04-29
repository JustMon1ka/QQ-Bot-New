import requests
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template
import logging
import os


def create_web_app(web_controller):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # 设置模板文件夹路径
    template_dir = os.path.join(basedir, 'templates')
    # 静态文件目录路径
    static_dir = os.path.join(basedir, 'static')

    app = Flask("Web Controller", template_folder=template_dir, static_folder=static_dir)

    @app.route('/')
    def index():
        bot_info = WebController.get_bot_info(web_controller)
        base_info = WebController.get_base_info(web_controller)
        return render_template('index.html', bot_info=bot_info, base_info=base_info)

    @app.route('/log.html')
    def log():
        return render_template('log.html')

    @app.route('/plugins.html')
    def plugins():
        return render_template('plugins.html')

    app.logger.setLevel(logging.ERROR)
    return app


class WebController:
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(logging.ERROR)

    def __init__(self, bot):
        self.bot = bot
        self.api = bot.api

    def get_bot_info(self):
        login_info = self.api.botSelfInfo.get_login_info().get("data")
        user_id = login_info.get("user_id")
        nickname = login_info.get("nickname")
        response = requests.get(f"http://q1.qlogo.cn/g?b=qq&nk={user_id}&s=100")
        save_path = "static/images/bot-avatar.png"
        basedir = os.path.abspath(os.path.dirname(__file__))

        save_path = os.path.join(basedir, save_path)
        with open(save_path, 'wb') as f:
            f.write(response.content)

        return {
            'avatar': 'bot-avatar.png',
            'qq': user_id,
            'nickname': nickname
        }

    def get_base_info(self):
        bot_name = self.bot.bot_name
        plugins_name_list = ""
        for plugins in self.bot.plugins_list:
            plugins_name_list += f"&nbsp;&nbsp;&nbsp;&nbsp;插件名：{plugins.name}&nbsp;&nbsp;插件类型：{plugins.type}&nbsp;&nbsp;插件作者：{plugins.author}<br>"
        return {
            'content': f'以下是Bot的基本配置信息：<br>Bot名字：{bot_name}<br>加载的插件：<br>{plugins_name_list}'
        }

    def run(self, ip, port):
        app = create_web_app(self)
        server = WSGIServer((ip, port), app)
        server.serve_forever()


if __name__ == "__main__":
    bot = None  # 创建或获取你的bot对象
    web_controller = WebController(bot)
    web_controller.run('127.0.0.1', 3000)

import configparser

import requests
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, send_from_directory, Response, jsonify, session, request
import logging
import os

from Plugins import Plugins

total_lines_read = 0
last_cleared_line = 0


def create_web_app(web_controller):
    basedir = os.path.abspath(os.path.dirname(__file__))
    # 设置模板文件夹路径
    template_dir = os.path.join(basedir, 'templates')
    # 静态文件目录路径
    static_dir = os.path.join(basedir, 'static')

    app = Flask("Web Controller", template_folder=template_dir, static_folder=static_dir)
    app.secret_key = 'just monika'

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/baseInfo.html')
    def base_info():
        bot_info = WebController.get_bot_info(web_controller)
        plugins_info = WebController.get_plugins_init_info(web_controller)

        return render_template('baseInfo.html', bot_info=bot_info, plugins_info=plugins_info)

    @app.route('/log.html')
    def log():
        return render_template('log.html')

    @app.route('/leave-log.html')
    def leave_log():
        global total_lines_read, last_cleared_line
        total_lines_read = last_cleared_line
        return jsonify(success=True)

    @app.route('/plugins.html')
    def plugins():
        plugins_info = WebController.get_all_plugins_info(web_controller)  # 假设这是从数据库获取信息的函数
        return render_template('plugins.html', plugins=plugins_info)

    @app.route('/log.out')
    def log_file():
        global total_lines_read, last_cleared_line

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_file_path = os.path.join(parent_dir, 'log.out')

        lines_to_send = []
        with open(log_file_path, 'r') as file:  # 以读模式打开文件
            all_lines = file.readlines()
            lines_to_send = all_lines[total_lines_read:]  # 提取新的日志行
            total_lines_read = len(all_lines)  # 更新读取的总行数

        # 处理错误标记并准备写回文件
        new_lines = [line.replace('[ERROR]', '[error]') if '[ERROR]' in line else line for line in all_lines]

        # 将更新后的内容写回文件
        with open(log_file_path, 'w') as file:
            file.writelines(new_lines)

        return Response(''.join(lines_to_send), mimetype='text/plain')

    @app.route('/clear-log', methods=["POST"])
    def clear_log():
        global total_lines_read, last_cleared_line
        last_cleared_line = total_lines_read
        return jsonify(success=True)

    @app.route('/save_config', methods=['POST'])
    def save_config():
        config_data = request.json
        print(config_data)

        result = WebController.save_config(web_controller, config_data)

        return jsonify(result)

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

        bot_name = self.bot.bot_name
        return {
            'avatar': 'bot-avatar.png',
            'qq': user_id,
            'nickname': nickname,
            "name": bot_name
        }

    def get_plugins_init_info(self):
        active_plugins = []
        inactive_plugins = []
        error_plugins = []
        for plugins in self.bot.plugins_list:
            plugins_status = plugins.status
            # print(plugins_status)
            plugins_name = plugins.name
            plugins_type = plugins.type
            plugins_author = plugins.author
            plugins_info = {"name": plugins_name, "info": f"{plugins_name}——类型：{plugins_type}, 作者：{plugins_author}"}
            if plugins_status == "running":
                active_plugins.append(plugins_info)
            elif plugins_status == "disable":
                inactive_plugins.append(plugins_info)
            elif plugins_status == "error":
                error_plugins.append(plugins_info)

        return {
            "active_plugins_count": len(active_plugins),
            "inactive_plugins_count": len(inactive_plugins),
            "error_plugins_count": len(error_plugins),
            "active_plugins": active_plugins,
            "inactive_plugins": inactive_plugins,
            "error_plugins": error_plugins,
        }

    # 创建一个不记录任何内容的日志器
    class SilentLogger(object):
        def write(self, *args, **kwargs):
            pass

        def flush(self, *args, **kwargs):
            pass

    def run(self, ip, port):
        app = create_web_app(self)
        server = WSGIServer((ip, port), app, log=self.SilentLogger())
        # server = WSGIServer((ip, port), app)
        server.serve_forever()

    def get_all_plugins_info(self):
        plugins_info = {}
        for plugins in self.bot.plugins_list:
            plugins_name = plugins.name
            plugins_type = plugins.type
            plugins_status = plugins.status
            plugins_info[plugins_name] = {}
            plugins_info[plugins_name]["type"] = plugins_type
            plugins_info[plugins_name]["status"] = plugins_status
            plugins_author = plugins.author
            plugins_introduction = plugins.introduction
            plugins_error_info = plugins.error_info
            plugins_info[plugins_name]["other_info"] = {
                "author": plugins_author,
                "introduction": plugins_introduction,
                "error_info": plugins_error_info
            }
            plugins_info[plugins_name]["config"] = plugins.config
        return plugins_info

    def update_plugin_status(self, plugin_name, new_status):
        config = configparser.ConfigParser()
        config_path = self.bot.config_file
        enable = "True" if new_status == "running" else "False"
        # print(enable)
        try:
            # print("start read config")
            config.read(config_path, encoding='utf-8')
            # print(plugin_name in config)
            if plugin_name in config:
                config.set(plugin_name, 'enable', enable)
                with open(config_path, 'w') as configfile:
                    config.write(configfile)
                for plugin in self.bot.plugins_list:
                    if plugin.name == plugin_name:
                        plugin.status = new_status

                return True
            else:
                return False
        except Exception as e:
            print(f"Error updating plugin status: {e}")
            return False

    def save_config(self, config_data):
        plugin_name = config_data.get("plugin_name")
        if not plugin_name:
            return {'success': False, "message": "缺少插件名称"}

        try:
            for plugin in self.bot.plugins_list:
                if plugin_name == plugin.name:
                    config = configparser.ConfigParser()
                    config.read(plugin.config_path)

                    # 确保有一个合适的节名
                    if not config.has_section(plugin_name):
                        config.add_section(plugin_name)

                    # 更新配置文件中的值
                    for key, value in config_data.items():
                        if key == "plugin_name":
                            continue
                        if isinstance(value, list):
                            config.set(plugin_name, key, ','.join(map(str, value)))
                        else:
                            config.set(plugin_name, key, str(value))

                    # 保存配置文件
                    with open(plugin.config_path, 'w', encoding="gbk") as configfile:
                        config.write(configfile)

                    plugin.load_config()
                    status = "running" if plugin.config.get("enable") else "disable"
                    plugin.set_status(status=status)

                    return {'success': True}
                else:
                    continue
        except Exception as e:
            return {'success': False, "message": f"后端执行操作时出错：{e}"}

        return {'success': False, "message": f"没有找到{plugin_name}插件的本地配置文件！"}


if __name__ == "__main__":
    bot = None  # 创建或获取你的bot对象
    web_controller = WebController(bot)
    web_controller.run('127.0.0.1', 3000)

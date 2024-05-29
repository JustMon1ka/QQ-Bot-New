from flask import Flask, request
import requests


app = Flask(__name__)


@app.route("/onebot", methods=["POST", "GET"])
def post_date():
    data = request.get_json()
    post_type = data.get("post_type")
    if post_type == "message":
        message_type = data.get("message_type")
        if message_type == "private":
            message = data.get("message")
            user_id = data.get("sender").get("user_id")
            requests.post(f"http://{bot_ip}:{http_service_port}/send_private_msg?user_id={user_id}&message={message}")

    return 'OK'


if __name__ == "__main__":
    bot_ip = "127.0.0.1"  # 此处对应LLOneBot所在的电脑的ip地址（如果是本机那就是127.0.0.1）
    http_service_port = 5700  # 此处对应“HTTP服务监听端口”
    http_event_post_port = 5701  # 此处对应“HTTP事件上报地址中的端口”
    app.run("127.0.0.1", http_event_post_port, debug=True)

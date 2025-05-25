import requests
import re
import os
import platform
import time
from PIL import Image
import pytesseract
from Event.EventHandler import GroupMessageEventHandler
from Logging.PrintLog import Log
from Plugins import Plugins
from CQMessage.CQType import At, Reply

log = Log()

class AIAssistant(Plugins):
    """
    插件名：AIAssistant \n
    插件类型：群聊插件 \n
    插件功能：用户可以通过"<bot name> ask <问题内容>"的形式向远程大模型提问，支持文本和图片提问\n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "AIAssistant"
        self.type = "Group"
        self.author = "Yukii_P"
        self.introduction = """
                                远程大模型问答插件
                                支持文本和图片提问，图片会自动OCR识别后与大模型交互
                            """
        self.init_status()
        
        # 初始化大模型API配置
        self.bot_id = ''  # 默认Coze bot ID
        self.user_id = ''  # 默认用户ID
        self.api_token = ''  # API访问令牌
        self.base_url = ''  # Coze API基础URL

        self.user_cooldown = {}  # 用户冷却时间记录字典
        self.cooldown_time = 5   # 冷却时间（秒）

        # OCR配置
        if platform.system() == "Windows":
            # Windows 环境下指定 Tesseract 路径
            pytesseract.pytesseract.tesseract_cmd = self.config.get("windows_tesseract_path")
        # Linux 环境下不需要设置，默认会从 PATH 查找

        self.image_temp_dir = "./temp_images"  # 图片临时保存目录
        if not os.path.exists(self.image_temp_dir):
            os.makedirs(self.image_temp_dir)

    async def main(self, event: GroupMessageEventHandler, debug):
        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

        message = event.message
        
        # 检查是否是纯ask命令
        if message.strip() == f"{self.bot.bot_name} ask":
            self.api.groupService.send_group_msg(group_id=event.group_id, message="请输入你的问题哦")
            log.debug(f"插件：{self.name}运行正确，用户{event.user_id}没有提出问题，已发送提示性回复", debug)
            return
        
        # 检查是否是ask命令
        if not message.startswith(f"{self.bot.bot_name} ask"):
            return
        
        # 冷却检查
        current_time = time.time()
        last_ask_time = self.user_cooldown.get(event.user_id, 0)
        
        if current_time - last_ask_time < self.cooldown_time:
            remaining = self.cooldown_time - int(current_time - last_ask_time)
            self.api.groupService.send_group_msg(
                group_id=event.group_id,
                message=f"{At(qq=event.user_id)} 提问太快啦，请等待{remaining}秒后再问哦~"
            )
            return

        try:
            # 更新用户最后提问时间
            self.user_cooldown[event.user_id] = current_time

            self.api.groupService.send_group_msg(group_id=event.group_id, message="小莫正在思考中~")

            # 提取问题内容
            # 删除CQ码
            question = re.sub(r'\[.*?\]', '', message[len(f"{self.bot.bot_name} ask"):]).strip()
            
            # 检查消息中是否包含图片
            image_urls = self.extract_image_urls(event.raw_message)
            ocr_texts = []
            
            if image_urls:
                # 下载并处理图片
                for url in image_urls:
                    try:
                        image_path = self.download_image(url)
                        ocr_result = self.ocr_image(image_path)
                        if ocr_result:
                            ocr_texts.append(ocr_result)
                    except Exception as e:
                        log.error(f"图片处理失败: {str(e)}")
                        #ocr_texts.append(f"[图片识别失败: {str(e)}]")
                
                # 将OCR结果添加到问题中
                if ocr_texts:
                    question += "\n[图片识别内容]:\n" + "\n".join(ocr_texts)
            
            log.debug(f"插件：{self.name}运行正确，用户{event.user_id}提出问题{question}", debug)

            # 获取大模型回复
            response = self.get_coze_response(question)
            
            # 发送回复到群聊
            reply_message = f"[CQ:reply,id={event.message_id}]{response}"
            self.api.groupService.send_group_msg(group_id=event.group_id, message=reply_message)
            
            log.debug(f"插件：{self.name}运行正确，成功回答用户{event.user_id}的问题", debug)
            
        except Exception as e:
            log.error(f"插件：{self.name}运行时出错：{e}")
            self.api.groupService.send_group_msg(
                group_id=event.group_id, 
                message=f"{At(qq=event.user_id)} 处理请求时出错了: {str(e)}"
            )

    def extract_image_urls(self, raw_message):
        """从原始消息中提取图片URL"""
        # 这里假设图片URL在消息中以特定格式存在，根据实际框架调整
        # 示例格式可能是[CQ:image,file=xxxx,url=xxxx]
        pattern = r'\[CQ:image,.*?url=(.*?)\]'
        return re.findall(pattern, raw_message)

    def download_image(self, url):
        """下载图片到临时目录"""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filename = os.path.join(self.image_temp_dir, os.path.basename(url.split('?')[0]))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        return filename

    def ocr_image(self, image_path):
        """对图片进行OCR识别"""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='chi_sim+eng')
            return text.strip()
        except Exception as e:
            raise Exception(f"OCR识别失败: {str(e)}")
        finally:
            # 清理临时图片文件
            try:
                os.remove(image_path)
            except:
                pass

    def get_coze_response(self, prompt):
        """
        获取Coze大模型的回复

        参数:
            prompt (str): 用户输入的提示词，可能包含OCR识别的文本

        返回:
            str: 大模型的回复内容
        """
        # 从配置中获取API参数，如果配置中有则使用配置中的值
        bot_id = self.config.get("bot_id", self.bot_id)
        user_id = self.config.get("user_id", self.user_id)
        api_token = self.config.get("api_token", self.api_token)
        base_url = self.config.get("base_url", self.base_url)

        # 构造请求URL和头部
        url = f"{base_url}/chat"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 构造请求体
        payload = {
            "bot_id": bot_id,
            "user": user_id,
            "query": prompt,
            "stream": False
        }

        try:
            # 发送请求
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            
            # 提取回复内容
            if "messages" in data:
                for message in data["messages"]:
                    if "content" in message and not message["content"].startswith('{'):
                        return message["content"].strip()

            return "未收到有效回复"

        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"处理API响应时出错: {str(e)}")
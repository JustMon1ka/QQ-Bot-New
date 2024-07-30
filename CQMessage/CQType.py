class CQMessage:
    def __init__(self):
        self.cq_type = self.__class__.__name__.lower()

    def __str__(self):
        attrs = [f'{key}={value}' for key, value in self.__dict__.items() if not (key == 'cq_type' or value is None)]
        return f'[CQ:{self.cq_type},{",".join(attrs)}]'


class Face(CQMessage):
    def __init__(self, id):
        """
        CQ:face 小黄脸表情
        :param id: 表情的id
        """
        super().__init__()
        self.id = id


class Image(CQMessage):
    def __init__(self, file, type=None, url=None, cache=1, proxy=1, timeout=None):
        """
        CQ:image 图片
        :param file: 图片文件名
        :param type: 可能的值：flash。图片类型，flash 表示闪照，无此参数表示普通图片
        :param url: 图片 URL（从网络上获取的图片），只有收到时才有该参数，发送时该参数无效
        :param cache: 只在通过网络 URL 发送时有效，表示是否使用已缓存的文件，默认 1
        :param proxy: 只在通过网络 URL 发送时有效，表示是否通过代理下载文件（需通过环境变量或配置文件配置代理），默认 1
        :param timeout: 只在通过网络 URL 发送时有效，单位秒，表示下载网络文件的超时时间，默认不超时

        发送时，file 参数除了支持使用收到的图片文件名直接发送外，还支持：绝对路径（file:///），网络 URL（http://），Base64 编码（base64://）
        """
        super().__init__()
        self.file = file
        self.type = type
        self.url = url
        self.cache = cache
        self.proxy = proxy
        self.timeout = timeout


class Record(CQMessage):
    def __init__(self, file, magic=None, url=None, cache=None, proxy=None, timeout=None):
        """
        CQ:record 语音
        :param file: 语音文件名
        :param magic: 发送时可选，设置为 1 表示变声
        :param url: 语音 URL，只有收到时才有该参数，发送时该参数无效
        :param cache:  只在通过网络 URL 发送时有效，表示是否使用已缓存的文件
        :param proxy: 只在通过网络 URL 发送时有效，表示是否通过代理下载文件（需通过环境变量或配置文件配置代理）
        :param timeout: 只在通过网络 URL 发送时有效，单位秒，表示下载网络文件的超时时间，默认不超时

        发送时，file 参数除了支持使用收到的视频文件名直接发送外，还支持其它形式，参考 Image类。
        """
        super().__init__()
        self.file = file
        self.magic = magic
        self.url = url
        self.cache = cache
        self.proxy = proxy
        self.timeout = timeout


class At(CQMessage):
    def __init__(self, qq):
        """
        CQ:at @某人
        :param qq: 可能的值：QQ 号、all 。@的 QQ 号，all 表示全体成员
        """
        super().__init__()
        self.qq = qq


...
# 更多CQ消息段等待补充

if __name__ == "__main__":
    at_msg = At(qq=12345)
    print(at_msg)  # [CQ:at,qq=12345]

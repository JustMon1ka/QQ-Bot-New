import re
import types
from typing import Optional, Any, List

from CQMessage.CQType import At, Image


class CQHelper:
    @classmethod
    def load_cq(cls, message: str) -> Optional[Any]:
        """
        动态的封装 一个 记载CQ消息段的所有参数的对象
        :param message: 要实例化的CQ消息段
        :return: 一个实例化对象，可以直接取出其中的成员变量
        """
        # 匹配消息中的类型和属性
        message = message.replace('&amp;', '&')
        cq_pattern = re.compile(r'\[CQ:(\w+),([^\]]+)\]')
        match = cq_pattern.search(message)

        if not match:
            return None

        cq_type = match.group(1)
        attrs = match.group(2)

        # 创建一个动态类
        class_name = f"{cq_type.capitalize()}"
        dynamic_class = types.new_class(class_name)

        # 解析属性并设置到动态类实例上
        instance = dynamic_class()
        setattr(instance, 'cq_type', cq_type)

        # 改进的属性解析逻辑
        for attr in re.finditer(r'(\w+)=([^,]+)', attrs):
            key = attr.group(1)
            value = attr.group(2)
            setattr(instance, key, value)

        return instance

    @classmethod
    def loads_cq(cls, message: str) -> List[Any]:
        """

        :param message:
        :return:
        """
        cq_pattern = re.compile(r'\[CQ:(\w+),([\w=,\/.]+)\]')
        matches = cq_pattern.findall(message)

        cq_objects = []
        for match in matches:
            cq_msg = f"[CQ:{match[0]},{match[1]}]"
            cq_obj = cls.load_cq(cq_msg)
            if cq_obj:
                cq_objects.append(cq_obj)

        return cq_objects


if __name__ == "__main__":
    # 示例
    msg1 = "[CQ:at,qq=12345]"
    msg2 = "[CQ:image,file=000001464e61704361744f6e65426f747c4d736746696c657c327c3832343339353639347c373437343937323537313739383632393630317c373437343937323537313739383632393630307c4568526b454e78706232347050334e52697472675f317934726e38686778694b2d6763675f776f6f383479656d62486369774d794248427962325251674c326a41566f51794a3643355f54536d477a372d2d572d444e70516251.28AFC869F0CB651D610615D38EE5BA9D.jpg,sub_type=0,file_id=000001464e61704361744f6e65426f747c4d736746696c657c327c3832343339353639347c373437343937323537313739383632393630317c373437343937323537313739383632393630307c4568526b454e78706232347050334e52697472675f317934726e38686778694b2d6763675f776f6f383479656d62486369774d794248427962325251674c326a41566f51794a3643355f54536d477a372d2d572d444e70516251.28AFC869F0CB651D610615D38EE5BA9D.jpg,url=https://multimedia.nt.qq.com.cn/download?appid=1407&amp;fileid=EhRkENxpb24pP3NRitrg_1y4rn8hgxiK-gcg_woo84yembHciwMyBHByb2RQgL2jAVoQyJ6C5_TSmGz7--W-DNpQbQ&amp;rkey=CAMSKMa3OFokB_Tl0f1oi0l7bE5CbT9uUjCKKVc_Ds0itNrRC-k5vajv7V4,file_size=130314,file_unique=28afc869f0cb651d610615d38ee5ba9d]"
    msg3 = "123[CQ:image,file=xx/xx]321"
    msg4 = "123[CQ321]"

    obj1: At = CQHelper.load_cq(msg1)
    obj2: Image = CQHelper.load_cq(msg2)
    obj3: Image = CQHelper.load_cq(msg3)
    obj4 = CQHelper.load_cq(msg4)

    print(obj1.cq_type)  # at
    print(obj2.__dict__)  # {'cq_type': 'image', 'file': 'xx/xx'}
    print(obj3.file)  # xx/xx
    print(obj4)  # None

    msg5 = "123[CQ:image,file=xx/xx]321[CQ:at,qq=12345]456"
    msg6 = "123[]ewq[]231"

    obj5 = CQHelper.loads_cq(msg5)
    obj6 = CQHelper.loads_cq(msg6)

    for obj in obj5:
        print(obj.__dict__)
        # {'cq_type': 'image', 'file': 'xx/xx'}, {'cq_type': 'at', 'qq': '12345'}
    for obj in obj6:
        print(obj)  # 什么都没有

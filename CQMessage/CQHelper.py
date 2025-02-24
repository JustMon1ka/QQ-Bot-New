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

        for attr in attrs.split(','):
            key, value = attr.split('=')
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
    msg2 = "[CQ:image,file=000000a64e61704361744f6e65426f747c4d736746696c657c327c3832343339353639347c373437343932333338363336393734373135357c373437343932333338363336393734373135347c32363539343435333236.{211857B2-AB29-C99B-BF33-7E3E8C78B593}.jpg,sub_type=0,file_id=000000a64e61704361744f6e65426f747c4d736746696c657c327c3832343339353639347c373437343932333338363336393734373135357c373437343932333338363336393734373135347c32363539343435333236.{211857B2-AB29-C99B-BF33-7E3E8C78B593}.jpg,url=https://gchat.qpic.cn/gchatpic_new/0/0-0-211857B2AB29C99BBF337E3E8C78B593/0,file_size=8443,file_unique=211857b2ab29c99bbf337e3e8c78b593]"
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

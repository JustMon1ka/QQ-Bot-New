from asyncio.windows_events import NULL
import string
from tkinter import TRUE
from token import STRING
from types import NoneType
from sqlalchemy import Column, Integer,String, select, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update,delete
from sqlalchemy.ext.asyncio import create_async_engine
import json
from Interface.Api import Api
from Event.EventHandler.PrivateMessageEventHandler import PrivateMessageEvent
from Logging.PrintLog import Log
from Plugins import Plugins
import emoji
log = Log()


class card_comf(Plugins):
    """
    插件名：card_comf \n
    插件类型：群聊插件 \n
    插件功能：使用名片检查指令后检查名片 \n
    """
    def __init__(self, server_address, bot):
        super().__init__(server_address, bot)
        self.name = "card_comf"
        self.type = "Group"
        self.author = "kiriko"
        self.introduction = """
                                插件描述：使用名片检查指令后检查名片
                                插件功能：检查群名片
                            """
        self.init_status()
        self.all_line_count = None


    async def main(self, event, debug):

        enable = self.config.get("enable")
        if not enable:
            self.set_status("disable")
            return

        if self.status != "error":
            self.set_status("running")

       
        if self.all_line_count is None:
            while True:
                try:
                    self.all_line_count = await self.select_all_infom()
                    log.debug("初始化名片信息成功", debug)
                    break
                except Exception as e:
                    log.debug(e, debug=debug)
                    continue
                
        message: str = event.message
        command_list = message.split(" ")
        len_of_command = len(command_list)
        if command_list[0] != self.bot.bot_name:
            return
        if len_of_command < 2:
            return

        command = self.config.get("command")
        if command_list[1] != command:
            return
        else:  # 正式进入插件运行部分
            group_id = event.group_id
            effected_group: list = self.config.get("effected_group")
            
            
            if group_id not in effected_group:
                try:
                     await self.api.groupService.send_group_msg(group_id=group_id, message=f"该功能未在此群{group_id}生效")
                except Exception as e:
                       log.error(f"插件：{self.name}运行时出错：{e}")
                else:
                       log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：该功能未在此群{group_id}生效", debug)
                return
            else:
                 
                     group_memberlist=await self.api.GroupService.get_group_member_list(self,group_id=group_id)
                     
                     group_mem_numbers=len(group_memberlist['data'])
                     qq_lists=[]
                     card_lists=[]
                     legality=[]
                     
                     ingored_ids:list=self.config.get("ignored_ids")
                     message1:str=""
                     user_ids=[]
                     for i in range(group_mem_numbers):
                         if group_memberlist['data'][i]['user_id'] in ingored_ids:
                              continue
                         qq_lists.append(group_memberlist['data'][i]['user_id'])
                         card_lists.append(group_memberlist['data'][i]['card'])
                         legality.append(1)
                     group_mem_numbers -= len(ingored_ids)-1
                     for i in range(group_mem_numbers):
                         card_cuts=card_lists[i].split("-")
                         if len(card_cuts)!=3:
                             legality[i]=0
                         else :
                             stu_id = int(card_cuts[0])
                             select_result = None
                             try:
                                    select_result = self.query_bystu_id(stu_id)
                             except Exception as e:
                                 raise e
                             if select_result is not None:
                                 query_name = select_result.get("name")
                                 query_major =  select_result.get("major_short")
                                 query_group =  select_result.get("ingroup")
                                 full_major=""
                                 
                                 if query_group == None:
                                     full_major+=query_major
                                 elif query_group < 10:
                                     full_major+=query_major+"0"+str(query_group)
                                 else:
                                     full_major+=query_major+str(query_group)
                                 if card_cuts[2]!= query_name:
                                     legality[i]=-1
                                 elif card_cuts[1]!= full_major:
                                     legality[i]=-2
                             else:
                                 legality[i]=-3
                     
                     
                     for i in range(group_mem_numbers):
                         if legality[i]!=1:
                             user_ids.append(qq_lists[i])
                             
                     user_counts_map = await self.increment_counts_for_users(user_ids,debug)
                     for i in range(group_mem_numbers):
                         if legality[i]==0:
                             message1 += f"[CQ:at,qq={qq_lists[i]}]，名片:{card_lists[i]},名片未用-分为三项,提醒次数为{user_counts_map[qq_lists[i]]}"
                         elif legality[i]==-1:
                             message1 += f"[CQ:at,qq={qq_lists[i]}]，名片:{card_lists[i]},学号与姓名不符,提醒次数为{user_counts_map[qq_lists[i]]}"
                         elif legality[i]==-2:
                             card_cuts=card_lists[i].split("-")
                             message1 += f"[CQ:at,qq={qq_lists[i]}]，名片:{card_lists[i]},专业名称({card_cuts[1]})与名单册的信息({full_major})不符,提醒次数为{user_counts_map[qq_lists[i]]}"
                         elif legality[i]==-3:
                             message1 += f"[CQ:at,qq={qq_lists[i]}]，名片:{card_lists[i]},学号格式不正确,提醒次数为{user_counts_map[qq_lists[i]]}"
                         if user_counts_map[qq_lists[i]]==3:
                             message1 += ",移出群聊"
                         message1 +="\n"
                             
                     kicks=0 
                     try:
                       await self.api.groupService.send_group_msg(group_id=group_id, message=message1)
                       for i in range(group_mem_numbers):
                           if legality[i]!=1 :
                               
                              if user_counts_map[qq_lists[i]]==3:
                                   await self.api.groupService.set_group_kick(group_id=group_id,user_id=qq_lists[i])
                                   kicks+=1
                      
                     except Exception as e:
                         log.error(f"插件：{self.name}运行时出错：{e}")
                     else:
                          log.debug(f"插件：{self.name}运行正确，成功向{group_id}发送了一条消息：{message1}", debug)
                          if kicks>0:
                              log.debug(f"插件：{self.name}运行正确，成功将{group_id}的违规次数三次的成员移出群聊", debug)

       
                 
        return
    
    def query_bystu_id(self, stu_id):
        data = self.all_line_count.get("data")
        if stu_id not in data:
            return None
        else:
            result = data.get(stu_id)
            return result

    async def select_all_infom(self):
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as sessions:
           
            
            raw_table = select(self.test_table1)
            results = await sessions.execute(raw_table)
            
           
            indexs = results.scalars().all()
            indexs_dict = {lc.stu_id: {'name': lc.name, 'major_short': lc.major_short,'ingroup':lc.ingroup} for lc in indexs}

            
            return {'data': indexs_dict}
        
    async def increment_counts_for_users(self, user_ids,debug):
        """
        对一组 user_id 批量执行 counts 增量更新（所有增量为 1），并返回更新后的 counts 映射
        """
        
        async_sessions = sessionmaker(
            bind=self.bot.database,
            class_=AsyncSession,
            expire_on_commit=False
        )

        async with async_sessions() as session:
            async with session.begin():
                # 查询所有相关用户的当前 counts 值
                stmt = select(self.test_table2).where(self.test_table2.user_id.in_(user_ids))
                result = await session.execute(stmt)
                log.debug("初始化计数信息成功", debug)               
                user_records = result.scalars().all()
                 
                
                # 构建 user_id 到 counts 的映射
                user_counts_map = {user.user_id: user.counts for user in user_records}

                # 批量更新
                for user_id in user_ids:
                    if user_id in user_counts_map:
                        
                        new_counts = user_counts_map[user_id]+1
                        update_stmt = (
                            update(self.test_table2).
                            where(self.test_table2.user_id == user_id).
                            values(counts=new_counts)
                        )
                        await session.execute(update_stmt)
                        # 更新映射中的 counts
                        user_counts_map[user_id] = new_counts
                
                for user_id in user_ids:
                    if user_id in user_counts_map:
                       if user_counts_map[user_id]==3:
                        
                        delete_stmt = (
                            delete(self.test_table2).
                            where(self.test_table2.user_id == user_id)                           
                        )
                        await session.execute(delete_stmt)
                        # 将被踢出群聊的用户的计数信息删除
                        
                
                # 最后一次性提交所有更改
                await session.commit()
                log.debug("已将所有被警告的用户对应的警告次数计数加一,并删除了提醒次数为3的用户的计数数据")
                await session.close()
        return user_counts_map

    Basement = declarative_base()

    class test_table1(Basement):
        __tablename__ = 'test_table1'
        stu_id = Column(Integer, primary_key=True)
        name = Column(String)
        major_short = Column(String)
        ingroup = Column(Integer)
     
    class test_table2(Basement):
        __tablename__ = 'test_table2'
        user_id = Column(BigInteger, primary_key=True)
        counts =  Column(Integer)

    
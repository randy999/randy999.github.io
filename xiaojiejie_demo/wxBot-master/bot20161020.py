#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import ConfigParser
import json


class TulingWXBot(WXBot):
    def __init__(self):
        WXBot.__init__(self)

        self.tuling_key = "b9163e7460204c64a42457f6af701e1d"
        self.robot_switch = True
        self.robot_group = False
        self.robot_schedule = True
        self.robot_tiaoxi = False
        self.name = u"我的备忘录"
        
        self.robot_title = False
        try:
            cf = ConfigParser.ConfigParser()
            cf.read('conf.ini')
            self.tuling_key = cf.get('main', 'key')
        except Exception:
            pass
        print 'tuling_key:', self.tuling_key

    def tuling_auto_reply(self, uid, msg):
        if self.tuling_key:
            url = "http://www.tuling123.com/openapi/api"
            user_id = uid.replace('@', '')[:30]
            body = {'key': self.tuling_key, 'info': msg.encode('utf8'), 'userid': user_id}
            r = requests.post(url, data=body)
            respond = json.loads(r.text)
            result = u"机器人自动回复："
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                        k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')

            print '    ROBOT:', result
            return result
        else:
            return u"知道啦"

    def auto_switch(self, msg):
        msg_data = msg['content']['data']
        stop_cmd = [u'退下', u'走开', u'关闭', u'关掉', u'休息', u'滚开',u'滚']
        stop_group = [u'关闭群']
        start_group = [u'开启群']
        start_cmd = [u'出来', u'启动', u'工作']
        start_tiaoxi = [u'调戏',u'调戏！']
        stop_tiaoxi = [u'停止调戏',u'关闭调戏']
        start_title = [u'开启标签',u'标签']
        stop_title = [u'关闭标签',u'停止标签']
        if self.robot_group:
            for i in stop_group:
                if i == msg_data:
                    self.robot_group = False
                    self.send_msg_by_uid(u'[Robot]' + u'回复群关闭！', msg['to_user_id'])
                        
        else:
            for i in start_group:
                if i == msg_data:
                    self.robot_group = True
                    self.send_msg_by_uid(u'[Robot]' + u'回复群开启！', msg['to_user_id'])
                
        if self.robot_switch:
            for i in stop_cmd:
                if i == msg_data:
                    self.robot_switch = False
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已关闭！', msg['to_user_id'])
    
        else:
            for i in start_cmd:
                if i == msg_data:
                    self.robot_switch = True
                    self.send_msg_by_uid(u'[Robot]' + u'机器人已开启！', msg['to_user_id'])
        
        if self.robot_title:
            for i in stop_title:
                if i == msg_data:
                    self.robot_title = False
                    self.send_msg_by_uid(u'[Robot]' + u'标签已关闭！', msg['to_user_id'])
        
        else:
            for i in start_title:
                if i == msg_data:
                    self.robot_title = True
                    self.send_msg_by_uid(u'[Robot]' + u'标签已开启！', msg['to_user_id'])

        
        for i in stop_tiaoxi:
            if i == msg_data:
                self.robot_tiaoxi = False
                self.send_msg_by_uid(u'[Robot]' + u'调戏已关闭！', msg['to_user_id'])
                
        for i in start_tiaoxi:
            if i == msg_data:
                self.robot_tiaoxi = True
                self.send_msg_by_uid(u'[Robot]' + u'调戏开启！', msg['to_user_id'])

        if msg_data.find(u"调戏") and self.robot_tiaoxi:
            print '开始调戏'
            self.name = msg_data[msg_data.find(u"调戏")+2:]
            print self.name


    def handle_msg_all(self, msg):
        if not self.robot_switch and msg['msg_type_id'] != 1:
            return
        if msg['msg_type_id'] == 1 and msg['content']['type'] == 0:  # reply to self
            self.auto_switch(msg)
        elif msg['msg_type_id'] == 4 and msg['content']['type'] == 0:  # text message from contact
            answer = u'[Robot]'
            if self.robot_title:
                answer += self.tuling_auto_reply(msg['user']['id'], msg['content']['data'])
                self.send_msg_by_uid(answer, msg['user']['id'])
            else:
                self.send_msg_by_uid(self.tuling_auto_reply(msg['user']['id'], msg['content']['data']), msg['user']['id'])

        elif msg['msg_type_id'] == 3 and msg['content']['type'] == 0 and self.robot_group:  # group text message
            if 'detail' in msg['content']:
                my_names = self.get_group_member_name(self.my_account['UserName'], msg['user']['id'])
                if my_names is None:
                    my_names = {}
                if 'NickName' in self.my_account and self.my_account['NickName']:
                    my_names['nickname2'] = self.my_account['NickName']
                if 'RemarkName' in self.my_account and self.my_account['RemarkName']:
                    my_names['remark_name2'] = self.my_account['RemarkName']

                is_at_me = False
                for detail in msg['content']['detail']:
                    if detail['type'] == 'at':
                        for k in my_names:
                            if my_names[k] and my_names[k] == detail['value']:
                                is_at_me = True
                                break
                if is_at_me:
                    src_name = msg['content']['user']['name']
                    reply = u"刘灿助手机器人自动回复"+'  to' + src_name + ': '
                    if msg['content']['type'] == 0:  # text message
                        reply += self.tuling_auto_reply(msg['content']['user']['id'], msg['content']['desc'])
                    else:
                        reply += u"对不起，只认字，其他杂七杂八的我都不认识，,,Ծ‸Ծ,,"
                    self.send_msg_by_uid(reply, msg['user']['id'])
    def schedule(self):
        if self.robot_tiaoxi:
            self.send_msg(self.name, u'诶哟，你好啊')
            time.sleep(5) #每1分钟发送一个表情


def main():
    bot = TulingWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'

    bot.run()


if __name__ == '__main__':
    main()


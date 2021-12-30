from utils import send_text_message, send_button_message
import message_template
import pandas as pd
from transitions.extensions import GraphMachine
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from linebot import LineBotApi, WebhookParser
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
import os
import sys

grade = ''
subject = ''
subject_list = []
info = pd.read_csv('ok.csv')

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    # 進到state的關鍵字
    def is_going_to_menu(self, event):
        text = event.message.text
        return text.lower() == "主選單"
    def is_going_to_ncku_website(self, event):
        text = event.message.text
        return text.lower() == "學校網站"
    def is_going_to_course(self, event):
        text = event.message.text
        return text.lower() == "選課資訊查詢"
    def is_going_to_course_website(self, event):
        text = event.message.text
        return text.lower() == "選課相關網站"
    def is_going_to_course_input_grade(self, event):
        text = event.message.text
        return text.lower() == "選課時間懶人包"
    def is_going_to_course_input_subject(self, event):
        text = event.message.text
        if text == '大一' or text == '大二' or text == '大三' or text == '大四' or text == '研究所':
            global grade
            grade = text
            return True
        return False
    def is_going_to_course_print_result(self, event):
        text = event.message.text
        global subject_list
        for word in text:
            if word == '國':
                subject_list.append('國文')
                continue
            elif word == '英':
                subject_list.append('英文')
                continue
            elif word == '體':
                subject_list.append('體育')
                continue
            elif word == '通':
                subject_list.append('通識')
                continue
            if word == '選':
                subject_list.append('選修')
                continue
            if word == '二':
                subject_list.append('二外')
                continue
        if len(subject_list) != 0:
            print(subject_list)
            return True
        return False
        
            
    def input_other_subject(self, event):
        text = event.message.text
        return text.lower() == "查詢其他科目"


    # 進到state後做的事
    def on_enter_menu(self, event):
        print("in menu")
        reply_token = event.reply_token
        message = message_template.main_menu
        message_to_reply = FlexSendMessage("開啟主選單", message)
        line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_ncku_website(self, event):
        print("in ncku website")
        title = '學校網站'
        text = ' '
        btn = [
            URITemplateAction(
                    label='成大總網',
                    uri='https://www.ncku.edu.tw/'
                ),
            URITemplateAction(
                    label='成大臉書',
                    uri='https://www.facebook.com/ncku.edu.tw/'
                ),
            URITemplateAction(
                    label='成大instagram',
                    uri='https://www.instagram.com/ncku_official/'
                ),
            MessageTemplateAction(
                label = '返回主選單',
                text ='主選單'
            ),
        ]
        send_button_message(event.reply_token, title, text, btn)
        # self.go_back()

    def on_enter_course(self, event):
        print("in course")
        title = '選課資訊'
        text = ' '
        btn = [
            MessageTemplateAction(
                label = '選課相關網站',
                text ='選課相關網站'
            ),
            MessageTemplateAction(
                label = '選課時間懶人包',
                text = '選課時間懶人包'
            ),
            MessageTemplateAction(
                label = '返回主選單',
                text ='主選單'
            ),
        ]
        send_button_message(event.reply_token, title, text, btn)

    def on_enter_course_website(self, event):
        print("in course website")
        title = '選課相關網站'
        text = ' '
        btn = [
            URITemplateAction(
                    label='選課資訊&系統',
                    uri='https://course.ncku.edu.tw/'
                ),
            URITemplateAction(
                    label='成大選課心得分享',
                    uri='https://www.facebook.com/NCKUSELECT/'
                ),
            URITemplateAction(
                    label='NCKU HUB',
                    uri='https://nckuhub.com/'
                ),
            MessageTemplateAction(
                label = '返回主選單',
                text ='主選單'
            ),
        ]
        send_button_message(event.reply_token, title, text, btn)
        # self.go_back()

    def on_enter_course_input_grade(self, event):
        print("in course lazy")
        reply_token = event.reply_token
        message = message_template.course_input_grade
        message["body"]["contents"][0]["text"] = '選擇年級'
        message_to_reply = FlexSendMessage("選課時間", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()

    def on_enter_course_input_subject(self, event):
        print("in course lazy")
        title = '選擇科目或直接查詢各階段時間'
        text = '國文/英文/體育請手動輸入'
        btn = [
            MessageTemplateAction(
                label = '查詢各階段時間',
                text ='查詢各階段時間'
            ),
             MessageTemplateAction(
                label = '選修',
                text ='選修'
            ),
             MessageTemplateAction(
                label = '通識',
                text ='通識'
            ),
             MessageTemplateAction(
                label = '二外',
                text ='二外'
            ),
            
        ]
        send_button_message(event.reply_token, title, text, btn)

    def on_enter_course_print_result(self, event):
        print("in result")
        reply_token = event.reply_token
        message = message_template.course_output_subject
        message["body"]["contents"][0]["text"] = self.get_result()
        message_to_reply = FlexSendMessage("選課時間", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        

    def get_result(self):
        # global grade, subject
        global grade, subject_list
        output = ''
        for subject in subject_list:
            output += '***'+grade+subject+'選課時間***\n\n'
            if grade != '研究所':
                course_info1 = info[info['年級'].str.contains('學士班')]
                course_info2 = info[info['年級'].str.contains(grade)]
                course_info3= info[info['年級'].str.contains('全校')]
                frames = [course_info1, course_info2, course_info3]
                result = pd.concat(frames)
                result.sort_index()
                for index, row in result.iterrows():
                    if subject == str(row['科目']).strip() or str(row['科目']).strip() == '全部':
                        if str(row['備註']).strip() != '無':
                            output += '【' +str(row['階段']).strip() +'】\n'+ str(row['時間']).strip() + '\n('+ str(row['備註']).strip() + ')\n\n'
                        else:
                            output += '【' +str(row['階段']).strip() +'】\n'+ str(row['時間']).strip() + '\n\n'
            else:
                if(subject == '通識' or subject =='國文' or subject =='英文'):
                    output += '-研究所沒有'+subject+'QQ\n\n'
                else:
                    course_info1 = info[info['年級'].str.contains(grade)]
                    course_info2= info[info['年級'].str.contains('全校')]
                    frames = [course_info1, course_info2]
                    result = pd.concat(frames)
                    result.sort_index()
                    for index, row in result.iterrows():
                        if subject == str(row['科目']).strip() or str(row['科目']).strip() == '全部':
                            if str(row['備註']).strip() != '無':
                                output += '【' +str(row['階段']).strip() +'】\n'+ str(row['時間']).strip() + '\n('+ str(row['備註']).strip() + ')\n\n'
                            else:
                                output += '【' +str(row['階段']).strip() +'】\n'+ str(row['時間']).strip() + '\n\n'
        output += "詳情以選課公告為主:3"
        subject_list = []
        return output

        
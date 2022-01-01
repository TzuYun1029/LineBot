from utils import send_text_message, send_button_message
import message_template
import csv
from bs4 import BeautifulSoup
import requests
from transitions.extensions import GraphMachine
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
from linebot import LineBotApi, WebhookParser
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
import os
import sys
import time

grade = ''
subject = ''
subject_list = []
stage_list = []
info_csv = []
with open('course.csv', newline='') as f:
    reader = csv.reader(f)
    info_csv = list(reader)

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    # condition是否觸發
    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text.lower() == "主選單"
    def is_going_to_courseToChoose_inputGrade(self, event):
        text = event.message.text
        return text.lower() == "現在可以選什麼"
    def get_input_grade(self, event):
        text = event.message.text
        if text == '大一' or text == '大二' or text == '大三' or text == '大四' or text == '研究所':
            global grade
            grade = text
            return True
        return False
    def is_going_to_eachCourseTime_inputGrade(self, event):
        text = event.message.text
        return text.lower() == "各科選課時間查詢"
    def is_going_to_main_menu(self, event):
        text = event.message.text
        return text.lower() == "主選單"
    def is_going_to_eachCourseTime_output(self, event):
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
    def is_going_to_eachStageTime_inputStage(self, event):
        text = event.message.text
        return text.lower() == "各階段時間查詢"
    def is_going_to_eachStageTime_output(self, event):
        text = event.message.text
        global stage_list
        for word in text:
            if word == '一':
                stage_list.append('第一階段')
                continue
            elif word == '二':
                stage_list.append('第二階段')
                continue
            elif word == '三':
                stage_list.append('第三階段')
                continue
            elif word == '加':
                stage_list.append('加簽')
                continue
            elif word == '棄':
                stage_list.append('棄選')
                continue
            if word == '退':
                stage_list.append('退選')
                continue
        if len(stage_list) != 0:
            print(stage_list)
            return True
        return False
    def input_other_stage(self, event):
        text = event.message.text
        return text.lower() == "查詢其他階段"
    def is_going_to_courseWebsite_output(self, event):
        text = event.message.text
        return text.lower() == "選課相關網站"
    def is_going_to_library(self, event):
        text = event.message.text
        return text.lower() == "圖書館空位查詢"
    def update(self, event):
        text = event.message.text
        return text.lower() == "更新資訊"


#########################################################################

    # 進到state後做的事
    def on_enter_main_menu(self, event):
        print("in menu")
        reply_token = event.reply_token
        message = message_template.main_menu
        message_to_reply = FlexSendMessage("開啟主選單", message)
        line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_courseToChoose_inputGrade(self, event):
        reply_token = event.reply_token
        message = message_template.course_input_grade
        message_to_reply = FlexSendMessage("選擇年級", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()

    def on_enter_courseToChoose_output(self, event):
        reply_token = event.reply_token
        message = message_template.course_to_choose
        reply = self.what_to_choose_now()
        message["body"]["contents"][0]["text"] = reply
        if '現在不是選課時間' in reply:
            message["hero"]["url"] = "https://cdn.discordapp.com/attachments/926861632460709962/926893927129305128/IMG_0196.png"
        else:
            message["hero"]["url"] = "https://cdn.discordapp.com/attachments/926861632460709962/926896118401482873/IMG_0197.png"
        message_to_reply = FlexSendMessage("現在可以選什麼", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_eachCourseTime_inputGrade(self, event):
        reply_token = event.reply_token
        message = message_template.course_input_grade
        message_to_reply = FlexSendMessage("選擇年級", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()

    def on_enter_eachCourseTime_inputSubject(self, event):
        reply_token = event.reply_token
        message = message_template.course_input_subject
        message_to_reply = FlexSendMessage("選擇科目", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()
        

    def on_enter_eachCourseTime_output(self, event):
        reply_token = event.reply_token
        message = message_template.course_output_subject
        message["body"]["contents"][0]["text"] = self.get_course_time()
        message_to_reply = FlexSendMessage("各科選課時間", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_eachStageTime_inputStage(self, event):
        reply_token = event.reply_token
        message = message_template.course_input_stage
        message_to_reply = FlexSendMessage("選擇階段", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()
        

    def on_enter_eachStageTime_output(self, event):
        reply_token = event.reply_token
        message = message_template.each_stage_time
        message["body"]["contents"][0]["text"] = self.stage_time()
        message_to_reply = FlexSendMessage("各階段時間", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    def on_enter_courseWebsite_output(self, event):
        reply_token = event.reply_token
        message = message_template.course_website
        message_to_reply = FlexSendMessage("選課相關網站", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)
        # self.go_back()

    def on_enter_library(self, event):
        reply_token = event.reply_token
        message = message_template.library_space
        message["body"]["contents"][0]["text"] = self.library_space()
        message_to_reply = FlexSendMessage("圖書館空位", message)
        line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
        line_bot_api.reply_message(reply_token, message_to_reply)

    
        
################################################################################


    def get_course_time(self):
        global grade, subject_list, info_csv
        output = ''
        for subject in subject_list:
            output += '*** '+grade+subject+'選課時間***\n\n'
            if grade != '研究所':
                frame = []
                for row in info_csv:
                    if len(row) != 0:
                        if row[2] == '學士班' or row[2] == '全校' or row[2] == grade:
                            frame.append(row)
                for row in frame:
                    if subject in row[3] or '全部' in row[3]:
                        output += '【' +row[0] +'】\n'+ row[1] + '\n'+ row[4] + '\n\n'
            else:
                frame = []
                for row in info_csv:
                    if len(row) != 0:
                        if row[2] == '全校' or row[2] == grade:
                            frame.append(row)
                for row in frame:
                    if subject in row[3] or '全部' in row[3]:
                        output += '【' +row[0] +'】\n'+ row[1] + '\n'+ row[4] + '\n\n'
        output += "【棄選】 同二、三階段\n\n\n"
        output += "*詳情以選課公告為主*"
        subject_list = []
        return output

    def whether_in_time(self, time, interval):
        split_interval = interval.split('~')
        earlier_time = split_interval[0][:-1]
        later_time = split_interval[1][1:]
        if len(later_time) <= 5: # no date
            get_date = earlier_time.split(' ')
            later_time = get_date[0]+' '+later_time
        # 補0
        if earlier_time[1] == '/':
            earlier_time = '0' + earlier_time
        if earlier_time[4] == ' ':
            earlier_time = earlier_time[:3] +'0'+ earlier_time[3:]
        if later_time[1] == '/':
            later_time = '0' + later_time
        if later_time[4] == ' ':
            later_time = later_time[:3] +'0'+ later_time[3:]

        pass_earlier = False
        pass_later = False
        for i in range(len(time)):
            if time[i] != ' ' and time[i] != '~' and time[i] != ':' and time[i] != '/':
                if int(time[i]) == int(earlier_time[i]):
                    continue
                elif int(time[i]) > int(earlier_time[i]):
                    pass_earlier = True
                    break
                elif int(time[i]) < int(earlier_time[i]):
                    break
        for i in range(len(time)):
            if time[i] != ' ' and time[i] != '~' and time[i] != ':' and time[i] != '/':
                if int(time[i]) == int(later_time[i]):
                    continue
                elif int(time[i]) > int(later_time[i]):
                    pass_later = True
                    break
                elif int(time[i]) < int(later_time[i]):
                    break
        if pass_earlier == True and pass_later == False:
            return 0 #in
        elif pass_earlier == False and pass_later == False:
            return 1 #pre
        elif pass_earlier == True and pass_later == True:
            return 2 #pass
        
    def what_to_choose_now(self):
        localtime = time.localtime()
        global grade
        result = time.strftime("%m/%d %H:%M", localtime)
        result = '01/25 15:00'
        output = ''
        printed_label = False
        if grade != '研究所':
            for row in info_csv[1:]:
                if len(row) != 0:
                    if self.whether_in_time(result, row[1]) == 0 and (row[2] == grade or row[2] == '學士班' or row[2] == '全校'): # in
                        if printed_label == False:
                            if row[0] == '退選':
                                output += "現在是【"+row[0]+"】!  可以退選:\n\n"
                            else:
                                output += "現在是【"+row[0]+"】!  可以選:\n\n"
                            printed_label = True
                        output += row[3] + "\n("+row[4]+")\n\n"
            if output == '':
                output += "現在不是選課時間QQ\n\n"
                for row in info_csv[1:]:
                    if len(row) != 0:
                        if self.whether_in_time(result, row[1]) == 1 and (row[2] == grade or row[2] == '學士班' or row[2] == '全校'): # pre
                                output += '【'+row[0]+ "】\n("+row[1]+")\n快要到了! \n\n要記得喔><"
                                break
            else:
                output += "快去選課吧:3"

        else:
            for row in info_csv[1:]:
                if len(row) != 0:
                    if self.whether_in_time(result, row[1]) == 0 and (row[2] == grade or row[2] == '全校'): # in
                        if printed_label == False:
                            if row[0] == '退選':
                                output += "現在是【"+row[0]+"】!  可以退選:\n\n"
                            else:
                                output += "現在是【"+row[0]+"】!  可以選:\n\n"
                            printed_label = True
                        output += row[3] + "\n("+row[4]+")\n\n"
           
            if output == '':
                output += "現在不是選課時間QQ\n\n"
                for row in info_csv[1:]:
                    if len(row) != 0:
                        if self.whether_in_time(result, row[1]) == 1 and (row[2] == grade or row[2] == '全校'): # pre
                                output += '【'+row[0]+ "】\n("+row[1]+")\n快要到了! \n\n要記得喔><"
                                break
            else:
                output += "快去選課吧:3"
        return output

    def library_space(self):
        response = requests.get(
            "https://www.lib.ncku.edu.tw/using/number.php")
        soup = BeautifulSoup(response.text, 'html.parser')
        people_num = soup.find_all(class_="number-people-digital")
        library = ['【總館】', '【醫分館】', '【新K館】', '【D-24】', '【未來館 2F Kafe】']
        output = "**【場館】 在館人數 / 閱覽席次 **\n\n\n"
        for i in range(5):
            # 輸出超連結的文字
            people = people_num[i].string
            temp = str(people).replace(' ', '').split('/')
            temp[0] = float(temp[0])
            temp[1] = float(temp[1])
            space_portion = round(float(temp[0]/temp[1]),2)
            if space_portion == 0:
                output += "⚪" + library[i] + " 閉館中\n\n"
            elif space_portion < 0.5: 
                output += "🟢" + library[i] + " " + people + "\n\n"
            elif space_portion < 0.9:
                output += "🟡" + library[i] + " " + people + "\n\n"
            else:
                output += "🔴" + library[i] + " " + people + "\n\n"
        output += "\n*實際人數以現場為主*"
        return output

    def stage_time(self):
        global stage_list
        output = ''
        printed_stage = ''
        for stage in stage_list:
            for row in info_csv:
                if stage in row[0] and row[1] != printed_stage:
                    output += '【' +row[0] +'】\n'+ row[1] + '\n\n'
                    printed_stage = row[1]

        if '棄選' in stage_list:
            output += '【棄選】 同二、三階段\n\n'
        stage_list = []
        return output[:-2]

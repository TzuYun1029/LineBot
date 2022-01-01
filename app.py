import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageCarouselColumn, URITemplateAction, MessageTemplateAction

from fsm import TocMachine
from utils import send_text_message, send_image_message, send_button_message

load_dotenv()


machine = TocMachine(
    states=["user", "main_menu", 
    "courseToChoose_inputGrade", "courseToChoose_output", 
    "eachCourseTime_inputGrade", "eachCourseTime_inputSubject", "eachCourseTime_output",
    "eachStageTime_inputStage", "eachStageTime_output",
    "courseWebsite_output",
    "library"],

    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "courseToChoose_inputGrade",
            "conditions": "is_going_to_courseToChoose_inputGrade",
        },
        {
            "trigger": "advance",
            "source": "courseToChoose_inputGrade",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "courseToChoose_inputGrade",
            "dest": "courseToChoose_output",
            "conditions": "get_input_grade",
        },
        {
            "trigger": "advance",
            "source": "courseToChoose_output",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "courseToChoose_output",
            "dest": "courseWebsite_output",
            "conditions": "is_going_to_courseWebsite_output",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "eachCourseTime_inputGrade",
            "conditions": "is_going_to_eachCourseTime_inputGrade",
        },
        {
            "trigger": "advance",
            "source": "eachCourseTime_inputGrade",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
         {
            "trigger": "advance",
            "source": "eachCourseTime_inputGrade",
            "dest": "eachCourseTime_inputSubject",
            "conditions": "get_input_grade",
        },
        {
            "trigger": "advance",
            "source": "eachCourseTime_inputSubject",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "eachCourseTime_inputSubject",
            "dest": "eachCourseTime_output",
            "conditions": "is_going_to_eachCourseTime_output",
        },
        {
            "trigger": "advance",
            "source": "eachCourseTime_output",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "eachCourseTime_output",
            "dest": "eachCourseTime_inputSubject",
            "conditions": "input_other_subject",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "eachStageTime_inputStage",
            "conditions": "is_going_to_eachStageTime_inputStage",
        },
        {
            "trigger": "advance",
            "source": "eachStageTime_inputStage",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "eachStageTime_inputStage",
            "dest": "eachStageTime_output",
            "conditions": "is_going_to_eachStageTime_output",
        },
        {
            "trigger": "advance",
            "source": "eachStageTime_output",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "eachStageTime_output",
            "dest": "eachStageTime_inputStage",
            "conditions": "input_other_stage",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "courseWebsite_output",
            "conditions": "is_going_to_courseWebsite_output",
        },
        {
            "trigger": "advance",
            "source": "courseWebsite_output",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "main_menu",
            "dest": "library",
            "conditions": "is_going_to_library",
        },
        {
            "trigger": "advance",
            "source": "library",
            "dest": "main_menu",
            "conditions": "is_going_to_main_menu",
        },
        {
            "trigger": "advance",
            "source": "library",
            "dest": "library",
            "conditions": "update",
        },
        
        # {"trigger": "go_back", "source": ["user", "main_menu", 
        #     "courseToChoose_inputGrade", "courseToChoose_output", 
        #     "eachCourseTime_inputGrade", "eachCourseTime_inputSubject", "eachCourseTime_output",
        #     "eachStageTime_inputStage", "eachStageTime_output",
        #     "courseWebsite_output",
        #     "library"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            if event.message.text == 'fsm':
                send_image_message(event.reply_token,'https://fa9b-140-116-119-28.ngrok.io/show-fsm')
            else:
                title = '請依照指示操作喔!'
                text = '想回到主選單可按以下按鈕'
                btn = [
                    MessageTemplateAction(
                        label = '返回主選單',
                        text ='主選單'
                    ),
                ]
                send_button_message(event.reply_token, title, text, btn)

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)

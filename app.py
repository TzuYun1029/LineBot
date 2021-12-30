import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=["initial", "menu", "ncku_website", "course", "course_website", "course_input_grade", "course_input_subject", "course_print_result"],
    transitions=[
        {
            "trigger": "advance",
            "source": "initial",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "ncku_website",
            "conditions": "is_going_to_ncku_website",
        },
        {
            "trigger": "advance",
            "source": "ncku_website",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "menu",
            "dest": "course",
            "conditions": "is_going_to_course",
        },
        {
            "trigger": "advance",
            "source": "course",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "course",
            "dest": "course_website",
            "conditions": "is_going_to_course_website",
        },
        {
            "trigger": "advance",
            "source": "course",
            "dest": "course_input_grade",
            "conditions": "is_going_to_course_input_grade",
        },
        {
            "trigger": "advance",
            "source": "course_website",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "course_input_grade",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        {
            "trigger": "advance",
            "source": "course_input_grade",
            "dest": "course_input_subject",
            "conditions": "is_going_to_course_input_subject",
        },
        {
            "trigger": "advance",
            "source": "course_input_subject",
            "dest": "course_print_result",
            "conditions": "is_going_to_course_print_result",
        },
        {
            "trigger": "advance",
            "source": "course_print_result",
            "dest": "course_input_subject",
            "conditions": "input_other_subject",
        },
         {
            "trigger": "advance",
            "source": "course_input_subject",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
         {
            "trigger": "advance",
            "source": "course_print_result",
            "dest": "menu",
            "conditions": "is_going_to_menu",
        },
        


        
        # {"trigger": "go_back", "source": ["ncku_website", "course_website"], "dest": "initial"},
    ],
    initial="initial",
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
            send_text_message(event.reply_token, "請輸入主選單")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)






# import os
# import sys

# from flask import Flask, jsonify, request, abort, send_file
# from dotenv import load_dotenv
# from linebot import LineBotApi, WebhookParser
# from linebot.exceptions import InvalidSignatureError
# from linebot.models import MessageEvent, TextMessage, TextSendMessage

# from fsm import TocMachine
# from utils import send_text_message

# load_dotenv()


# machine = TocMachine(
#     states=["user", "state1", "state2"],
#     transitions=[
#         {
#             "trigger": "advance",
#             "source": "user",
#             "dest": "state1",
#             "conditions": "is_going_to_state1",
#         },
#         {
#             "trigger": "advance",
#             "source": "user",
#             "dest": "state2",
#             "conditions": "is_going_to_state2",
#         },
#         {"trigger": "go_back", "source": ["state1", "state2"], "dest": "user"},
#     ],
#     initial="user",
#     auto_transitions=False,
#     show_conditions=True,
# )

# app = Flask(__name__, static_url_path="")


# # get channel_secret and channel_access_token from your environment variable
# channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
# channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
# if channel_secret is None:
#     print("Specify LINE_CHANNEL_SECRET as environment variable.")
#     sys.exit(1)
# if channel_access_token is None:
#     print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
#     sys.exit(1)

# line_bot_api = LineBotApi(channel_access_token)
# parser = WebhookParser(channel_secret)


# @app.route("/callback", methods=["POST"])
# def callback():
#     signature = request.headers["X-Line-Signature"]
#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info("Request body: " + body)

#     # parse webhook body
#     try:
#         events = parser.parse(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     # if event is MessageEvent and message is TextMessage, then echo text
#     for event in events:
#         if not isinstance(event, MessageEvent):
#             continue
#         if not isinstance(event.message, TextMessage):
#             continue

#         line_bot_api.reply_message(
#             event.reply_token, TextSendMessage(text=event.message.text)
#         )

#     return "OK"


# @app.route("/webhook", methods=["POST"])
# def webhook_handler():
#     signature = request.headers["X-Line-Signature"]
#     # get request body as text
#     body = request.get_data(as_text=True)
#     app.logger.info(f"Request body: {body}")

#     # parse webhook body
#     try:
#         events = parser.parse(body, signature)
#     except InvalidSignatureError:
#         abort(400)

#     # if event is MessageEvent and message is TextMessage, then echo text
#     for event in events:
#         if not isinstance(event, MessageEvent):
#             continue
#         if not isinstance(event.message, TextMessage):
#             continue
#         if not isinstance(event.message.text, str):
#             continue
#         print(f"\nFSM STATE: {machine.state}")
#         print(f"REQUEST BODY: \n{body}")
#         response = machine.advance(event)
#         if response == False:
#             send_text_message(event.reply_token, "Not Entering any state")

#     return "OK"


# @app.route("/show-fsm", methods=["GET"])
# def show_fsm():
#     machine.get_graph().draw("fsm.png", prog="dot", format="png")
#     return send_file("fsm.png", mimetype="image/png")


# if __name__ == "__main__":
#     port = os.environ.get("PORT", 8000)
#     app.run(host="0.0.0.0", port=port, debug=True)

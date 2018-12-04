
# coding: utf-8

# In[ ]:


"""
    1.建立跟redis的連線
    2.抓secret_key裡面的資料
    3.啟用API伺服器基本樣板，啟用伺服器基本
    4.撰寫用戶關注事件發生時的動作(follow event)
    5.收到按鈕（postback）的封包後(postback event)
    6.針對message event的設定
    7.啟動server

"""


# In[1]:





# In[ ]:


#正式上線時要放在dockerfile中
#!pip install redis
#!pip install line-bot-sdk


# In[ ]:


# #有想到運用方式時再使用
# """

#     1.針對跟redis的連線
    

# """

# import redis

# #製作redis連線
# redis = redis.Redis(
#     #redis container的host name
#     host='redis',
#     port=6379,
#     #預設沒密碼
#     password=None,
#     #給格式
#     charset="utf-8",
#     #要解碼不然回傳的資料前面會多一個b
#     decode_responses=True)


# In[ ]:


"""

    2.抓secret_key裡面的資料（由於是本機執行，所以secret_key可放在本機，不能放在github）
    

"""
# 載入json處理套件
import json
import os 

#請改成自己律定API Server的container name
#ip_location='chatbot_api'

# 載入基礎設定檔，本機執行所以路徑可以相對位置
secretFile=json.load(open("./secret_key",'r'))

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# channel_access_token是用於傳送封包去給line的認證使用類似這個是私鑰，而公鑰已經丟到line那邊，拿著這個就可以有VIP特權
line_bot_api = LineBotApi(secretFile.get("channel_access_token"))

# secret_key是用於當line傳送封包過來時確定line是否為本尊，沒有被仿冒
handler = WebhookHandler(secretFile.get("secret_key"))

# rich_menu_id用於將所指定的rich menu綁定到加好友的用戶上
menu_id = secretFile.get("rich_menu_id")
server_url = secretFile.get("server_url")


# In[ ]:


"""

  3.啟用伺服器基本樣板，啟用伺服器基本 

"""

# 引用Web Server套件
from flask import Flask, request, abort

# 從linebot 套件包裡引用 LineBotApi 與 WebhookHandler 類別
from linebot import (
    LineBotApi, WebhookHandler
)

# 引用無效簽章錯誤
from linebot.exceptions import (
    InvalidSignatureError
)

# 載入json處理套件
import json


# 設定Server啟用細節，這邊使用相對位置
app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/")


# 啟動server對外接口，使Line能丟消息進來
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#製作一個測試用接口
@app.route('/hello',methods=['GET'])
def hello():
    return 'Hello World!!'


# In[ ]:


'''

    4.撰寫用戶關注事件發生時的動作
        1. 製作並定義旋轉門選單、flexbubble樣板選單
        2. 取得用戶個資，並存回伺服器
        3. 把先前製作好的自定義菜單，與用戶做綁定
        4. 回應用戶，歡迎用的文字消息、圖片、及旋轉門選單
        5. 製作用戶的redis資料

'''

# 將消息模型，文字收取消息與文字寄發消息，Follow事件引入
from linebot.models import (
    MessageEvent, FollowEvent, JoinEvent,
    TextSendMessage, TemplateSendMessage,
    TextMessage, ButtonsTemplate,
    PostbackTemplateAction, MessageTemplateAction,
    URITemplateAction,ImageSendMessage,CarouselTemplate,CarouselColumn,
    FlexSendMessage,BubbleContainer
)

# 載入requests套件
import requests


# In[ ]:


#宣告並設定推播的 button_template_message (全域變數)
button_template_message = CarouselTemplate(
            columns=[
                CarouselColumn(
                    #置換成自己要用的照片
                    thumbnail_image_url="https://i.imgur.com/0PDvcCN.jpg",
                    #置換成自己的名字
                    title='這是心瑜的履歷機器人\n請使用下方功能選單\n或是按下方按鈕',
                    text='查看心瑜的個人簡介清單',
                    actions=[
                        PostbackTemplateAction(
                            label='自我介紹',
                            data="type=introduce"
                        ),
                        PostbackTemplateAction(
                            label='自身經歷',
                            data="type=work"
                        ),
                        PostbackTemplateAction(
                            label='專長與證照',
                            data="type=skills"
                        )
                    ]                    
                ),
                CarouselColumn(
                    #置換成自己要用的照片
                    thumbnail_image_url="https://i.imgur.com/UbL7fPA.png",
                    title='這是心瑜的履歷機器人\n請使用下方功能選單\n或是按下方按鈕',
                    text='網工班學習歷程',
                    actions=[
                        URITemplateAction(
                            label='AWS雲端專題GITHUB',
                            uri='https://github.com/iii-cutting-edge-tech-lab/Chatbot_Project_cc103'
                        ),
                        URITemplateAction(
                            label='DNSSEC簡介與實作',
                            #改成你的作業連結
                            uri="https://app.box.com/s/bld8wp26fjdyfnbjd0i9v2cuoih0jfsq" 
                        ),
                        URITemplateAction(
                            label='TLSv1.3簡介與實作',
                            #改成你的作業連結
                            uri="https://app.box.com/s/j9uxq92ua43905or3rfcncbhtptdpsm4"
                        )
                    ]
                ),
                CarouselColumn(
                    #置換成自己要用的照片
                    thumbnail_image_url="https://i.imgur.com/ZkKdBqL.jpg",
                    title='這是心瑜的履歷機器人\n請使用下方功能選單\n或是按下方按鈕',
                    text='個人作品清單',
                    actions=[
                        URITemplateAction(
                            label='3D Maya 作品',
                            uri='https://youtu.be/D4bZp86xBAc'
                        ),
                        URITemplateAction(
                            label='互動技術作品',
                            #改成你的作業連結
                            uri="https://www.youtube.com/watch?v=HRSicFOJ8R0&feature=youtu.be" 
                        ),
                        URITemplateAction(
                            label='虛擬實境作品',
                            #改成你的作業連結
                            uri="https://www.youtube.com/watch?v=fs8kwDU-zLY"
                        )
                    ]
                ),
                CarouselColumn(
                    #置換成自己要用的照片
                    thumbnail_image_url="https://i.imgur.com/ZkKdBqL.jpg",
                    title='這是心瑜的履歷機器人\n請使用下方功能選單\n或是按下方按鈕',
                    text='個人作品清單',
                    actions=[
                        URITemplateAction(
                            label='視訊分析作品',
                            uri='https://youtu.be/TuqQEUG3um0'
                        ),
                        URITemplateAction(
                            label='大學專題研究論文',
                            #改成你的作業連結
                            uri="http://www.cce.mcu.edu.tw/Yconference/2018conference/papers/SA1/002%E9%8A%98%E5%82%B3%E5%A4%A7%E5%AD%B8%E6%9F%AF%E5%90%9B%E7%BF%B0.pdf" 
                        ),
                        URITemplateAction(
                            label='專題研究GITHUB',
                            #改成你的作業連結
                            uri="https://github.com/scps960529/MCU-Scoreboard-Content-Extraction-and-its-Application-for-Tennis-Video"
                        )
                    ]
                )]
            )


# In[ ]:


#宣告並設定推播的 flex bubble (全域變數)
#圖片的URL要置換成絕對路徑
#URI要改成想連結的URI
flexBubbleContainerJsonString_INTRO ="""
{
    "type": "bubble",
    "direction": "ltr",
    "header": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "text": "自我介紹",
          "size": "md",
          "align": "center",
          "gravity": "center",
          "weight": "bold",
          "color": "#000000"
        }
      ]
    },
    "hero": {
      "type": "image",
      "url": "https://i.imgur.com/XWCj8jr.jpg",
      "align": "center",
      "gravity": "center",
      "size": "full",
      "aspectRatio": "20:13",
      "aspectMode": "cover"
    },
    "body": {
      "type": "box",
      "layout": "horizontal",
      "spacing": "md",
      "contents": [
        {
          "type": "box",
          "layout": "vertical",
          "flex": 1,
          "contents": [
            {
              "type": "image",
              "url": "https://i.imgur.com/GjjMnIo.jpg",
              "gravity": "bottom",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            },
            {
              "type": "image",
              "url": "https://i.imgur.com/aVDOZzG.jpg",
              "margin": "md",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            }
          ]
        },
        {
          "type": "box",
          "layout": "vertical",
          "flex": 2,
          "contents": [
            {
              "type": "text",
              "text": "我的個人資料",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mydata",
                "text": "我想看個人資料"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的興趣",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "myhobby",
                "text": "我想看興趣"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的自我期許",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mythought",
                "text": "我想看自我期許"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的Facebook",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "uri",
                "label": "FB",
                "uri": "https://www.facebook.com/hsinyuchen85"
              }
            }
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": " ",
            "uri": "https://www.google.com"
          },
          "gravity": "center"
        }
      ]
    },
    "styles": {
      "hero": {
        "backgroundColor": "#160D3A"
      }
    }
  }"""


# In[ ]:


#宣告並設定推播的 flex bubble (全域變數)
#圖片的URL要置換成絕對路徑
#URI要改成想連結的URI
flexBubbleContainerJsonString_WORK ="""
{
    "type": "bubble",
    "direction": "ltr",
    "header": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "text": "自身經歷",
          "size": "md",
          "align": "center",
          "gravity": "center",
          "weight": "bold",
          "color": "#000000"
        }
      ]
    },
    "hero": {
      "type": "image",
      "url": "https://i.imgur.com/82jeCP6.jpg",
      "align": "center",
      "gravity": "center",
      "size": "full",
      "aspectRatio": "20:13",
      "aspectMode": "cover"
    },
    "body": {
      "type": "box",
      "layout": "horizontal",
      "spacing": "md",
      "contents": [
        {
          "type": "box",
          "layout": "vertical",
          "flex": 1,
          "contents": [
            {
              "type": "image",
              "url": "https://i.imgur.com/7myxMcw.jpg",
              "gravity": "bottom",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            },
            {
              "type": "image",
              "url": "https://i.imgur.com/9P2AqdD.jpg",
              "margin": "md",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            }
          ]
        },
        {
          "type": "box",
          "layout": "vertical",
          "flex": 2,
          "contents": [
            {
              "type": "text",
              "text": "我的學校經歷",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mydata",
                "text": "我想看學校經歷"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的實習經歷",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "myhobby",
                "text": "我想看實習經歷"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "微軟Codeing Angel活動經歷",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mythought",
                "text": "我想看微軟Codeing Angel活動經歷"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的Facebook",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "uri",
                "label": "FB",
                "uri": "https://www.facebook.com/hsinyuchen85"
              }
            }
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": " ",
            "uri": "https://www.google.com"
          },
          "gravity": "center"
        }
      ]
    },
    "styles": {
      "hero": {
        "backgroundColor": "#160D3A"
      }
    }
  }"""


# In[ ]:


#宣告並設定推播的 flex bubble (全域變數)
#圖片的URL要置換成絕對路徑
#URI要改成想連結的URI
flexBubbleContainerJsonString_SKILLS ="""
{
    "type": "bubble",
    "direction": "ltr",
    "header": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "text",
          "text": "專長與證照",
          "size": "md",
          "align": "center",
          "gravity": "center",
          "weight": "bold",
          "color": "#000000"
        }
      ]
    },
    "hero": {
      "type": "image",
      "url": "https://i.imgur.com/7EcKtyK.jpg",
      "align": "center",
      "gravity": "center",
      "size": "full",
      "aspectRatio": "20:13",
      "aspectMode": "cover"
    },
    "body": {
      "type": "box",
      "layout": "horizontal",
      "spacing": "md",
      "contents": [
        {
          "type": "box",
          "layout": "vertical",
          "flex": 1,
          "contents": [
            {
              "type": "image",
              "url": "https://i.imgur.com/yourPicture.jpg",
              "gravity": "bottom",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            },
            {
              "type": "image",
              "url": "https://i.imgur.com/AsulvfC.jpg",
              "margin": "md",
              "size": "sm",
              "aspectRatio": "4:3",
              "aspectMode": "cover"
            }
          ]
        },
        {
          "type": "box",
          "layout": "vertical",
          "flex": 2,
          "contents": [
            {
              "type": "text",
              "text": "我的證照資格",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mydata",
                "text": "我想看證照資格"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的技術與專長",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "myhobby",
                "text": "我想看技術與專長"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的其他專長",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "message",
                "label": "mythought",
                "text": "我想看其他專長"
              }
            },
            {
              "type": "separator"
            },
            {
              "type": "text",
              "text": "我的Facebook",
              "flex": 1,
              "size": "xs",
              "align": "start",
              "gravity": "center",
              "weight": "bold",
              "color" : "#99ccff",
              "action": {
                "type": "uri",
                "label": "FB",
                "uri": "https://www.facebook.com/hsinyuchen85"
              }
            }
          ]
        }
      ]
    },
    "footer": {
      "type": "box",
      "layout": "horizontal",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "uri",
            "label": " ",
            "uri": "https://www.google.com"
          },
          "gravity": "center"
        }
      ]
    },
    "styles": {
      "hero": {
        "backgroundColor": "#160D3A"
      }
    }
  }"""


# In[ ]:


#將bubble類型的json 進行轉換變成 Python可理解之類型物件，並將該物件封裝進 Flex Message中
#引用套件
from linebot.models import(
    FlexSendMessage,BubbleContainer,
)

import json

#INTRO樣板封裝
bubbleContainer_intro= BubbleContainer.new_from_json_dict(json.loads(flexBubbleContainerJsonString_INTRO))
flexBubbleSendMessage_INTRO =  FlexSendMessage(alt_text="自我介紹", contents=bubbleContainer_intro)

#WORK樣板封裝
bubbleContainer_work= BubbleContainer.new_from_json_dict(json.loads(flexBubbleContainerJsonString_WORK))
flexBubbleSendMessage_WORK =  FlexSendMessage(alt_text="自身經歷", contents=bubbleContainer_work)

#SKILLS樣板封裝
bubbleContainer_skills= BubbleContainer.new_from_json_dict(json.loads(flexBubbleContainerJsonString_SKILLS))
flexBubbleSendMessage_SKILLS =  FlexSendMessage(alt_text="專長與證照", contents=bubbleContainer_skills)


# In[ ]:


# 告知handler，如果收到FollowEvent，則做下面的方法處理
@handler.add(FollowEvent)
def reply_text_and_get_user_profile(event):
    
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
        
    # 將用戶資訊做成合適Json
    user_info = {  
        "user_open_id":user_profile.user_id,
        "user_nick_name":user_profile.display_name,
        "user_status" : "",
        "user_img" : user_profile.picture_url,
        "user_register_menu" : menu_id
    }
    
    # 將json傳回API Server
    Endpoint='http://%s:5000/user' % (ip_location)
    
    # header要特別註明是json格式
    Header={'Content-Type':'application/json'}
    
    # 傳送post對API server新增資料 
    Response=requests.post(Endpoint,headers=Header,data=json.dumps(user_info))
    
    #印出Response的資料訊息
    print(Response)
    print(Response.text)
    
    # 將菜單綁定在用戶身上
    # 要到Line官方server進行這像工作，這是官方的指定接口
    linkMenuEndpoint='https://api.line.me/v2/bot/user/%s/richmenu/%s' % (user_profile.user_id, menu_id)
    
    # 官方指定的header
    linkMenuRequestHeader={'Content-Type':'image/jpeg','Authorization':'Bearer %s' % secretFile["channel_access_token"]}
    
    # 傳送post method封包進行綁定菜單到用戶上
    lineLinkMenuResponse=requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader)
                         
    #針對剛加入的用戶回覆文字消息、圖片、旋轉門選單
    reply_message_list = [
                    TextSendMessage(text="歡迎%s\n感謝您加入心瑜的履歷機器人\n想多了解我請使用下方功能選單\n或是按下方按鈕\n" % (user_profile.display_name) ),    
                    #置換你想傳送的照片
                    ImageSendMessage(original_content_url='https://i.imgur.com/gFEZKzf.jpg',
                    preview_image_url='https://i.imgur.com/gFEZKzf.jpg'), 
                    TemplateSendMessage(alt_text="心瑜的履歷功能選單，為您服務",template=button_template_message),
                ] 
    
    #推送訊息給官方Line
    line_bot_api.reply_message(
        event.reply_token,
        reply_message_list    
    )
    


# In[ ]:


"""
    
    5.收到按鈕（postback）的封包後
        1. 先看是哪種按鈕（introduce(yourName自我介紹)，work(yourName工作經驗)，skills(yourName的專長)）
        2. 執行所需動作（執行之後的哪一些函式）
        3. 回覆訊息

"""
from linebot.models import PostbackEvent

#parse_qs用於解析query string
from urllib.parse import urlparse,parse_qs

#用戶點擊button後，觸發postback event，對其回傳做相對應處理
@handler.add(PostbackEvent)
def handle_post_message(event):
    #抓取user資料
    user_profile = event.source.user_id
    
    #抓取postback action的data
    data = event.postback.data
    
    #用query string 解析data
    data=parse_qs(data)
               
    #給按下"yourName自我介紹"，"yourName工作經驗"，"yourName的專長"，推播對應的flexBubble
    if (data['type']==['introduce']):
            line_bot_api.reply_message(
                event.reply_token,
                flexBubbleSendMessage_INTRO
            )
    elif (data['type']==['work']):
            line_bot_api.reply_message(
                event.reply_token,
                flexBubbleSendMessage_WORK
            )
    elif (data['type']==['skills']):
            line_bot_api.reply_message(
                event.reply_token,
                flexBubbleSendMessage_SKILLS
            )
    #其他的pass
    else:
        pass


# In[ ]:


'''
    6.針對message event的設定
    當用戶發出文字消息時，判斷文字內容是否包含一些關鍵字，
    若有，則回傳客製化訊息
    若無，則回傳預設訊息。

'''

# 用戶發出文字消息時， 按條件內容, 回傳文字消息
@handler.add(MessageEvent, message=TextMessage)
#將這次event的參數抓進來
def handle_message(event):
    user_profile = event.source.user_id
    
    # 當用戶輸入VMware時判斷成立
    if (event.message.text.find('VMware')!= -1):
        # 提供VMware作業網址
        url1='https://www.youtube.com/watch?v=6IZjfuUXrzg'
        url2='https://www.youtube.com/watch?v=JEc_hzKs22g'
        url3='https://app.box.com/s/2bt2aqtyjhfjvr8k09y13vuoqhog6olx'
        # 將上面的變數包裝起來
        reply_list = [
            TextSendMessage(text="VMware作業講解:\n%s" % (url1)),
            TextSendMessage(text="VMware作業實作:\n%s" % (url2)),
            TextSendMessage(text="VMware作業簡報:\n%s" % (url3))
        ]
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            reply_list
            )
    
    # 當用戶輸入Linux Server時判斷成立
    elif (event.message.text.find('Linux Server')!= -1):
        # 提供Linux Server作業網址
        url1='https://app.box.com/s/tz3migz2mmfqn3w3tlp6ya250f0ine6s'
        # 將上面的變數包裝起來
        reply_list = [
            TextSendMessage(text="VMware作業講解:\n%s" % (url1))
        ]
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            reply_list
            )
        
    # 當用戶輸入"資安簡報"時判斷成立
    elif (event.message.text.find('資安簡報')!= -1):
        # 提供資安實作簡報網址
        url1='https://drive.google.com/open?id=1e9nD6C6AqZLDkVgHWHbOuDJpcw4XN6sp'
        # 將上面的變數包裝起來
        reply_list = [
            TextSendMessage(text="資安實作簡報:\n%s" % (url1))
        ]
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            reply_list
            )
    
        
     # 結合旋轉門選單中的"yourName自我介紹"，進到flexbubble選單，按下"yourName 自我介紹"，會有文字"我想看yourName的個人資料"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看個人資料')!= -1):
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我是陳心瑜，我的出生地在高雄，我是家中的長女，我的家庭很溫暖，「不管做甚麼事情，都必須要努力且能夠對自己和別人負責。」—這句話是父母親對我的教導，他們總是支持我走我想走的路，而我也堅信自己未來能夠在資訊領域有一份成就，不辜負父母親與自己。")
            )
    
    # 結合旋轉門選單中的"yourName自我介紹"，進到flexbubble選單，按下"yourName 平時興趣"，會有文字"我想看yourName的平時興趣"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看興趣')!= -1):
        # 回覆訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我的個性比較外向，空閒的時候喜歡跟三五好友一起出去旅遊，也想多了解各個地方所獨有的文化與特色，至今為止在台灣的各個縣市、離島以及泰國都有我的足跡，也計畫著將來想要帶父母一起出去旅遊，讓他們能夠好好的放鬆多年的辛勞。除此之外，外向的我也喜歡閱讀與線上遊戲，透過不同性質的事來窺探不同的世界，這就是我的興趣。")
            )
    
    # 結合旋轉門選單中的"yourName自我介紹"，進到flexbubble選單，按下"yourName 能為公司做的貢獻"，會有文字"我想看yourName的想法"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看自我期許')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="在未來，我期許自己能夠莫忘初衷，牢記學無止盡這句話，並要不斷精進自己，成長自身來為公司帶來更大的效益。")
            )
        
    # 結合旋轉門選單中的"yourName工作經驗"，進到flexbubble選單，按下"yourName 學校經歷"，會有文字"我想看yourName的學校經歷"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看學校經歷')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="在大學裡我就讀的是資訊傳播工程學系，在學期間我修習的課程有程式語言(C、C#、HTML)、3D製圖、動畫設計、區域與廣域網路、電腦圖學、虛擬實境…等，除了資訊相關知識以外，我也修了傳播與行銷相關的課程，如態度說服…等，在這方面的課程中我也學習到如何撰寫提案報告，也了解在職場上如何與客戶溝通需求，是一門我覺得很實用的課程。雖然在校成績不是名列前茅，但四年來成績一直保持中上水準。在我的畢業專題是屬於影像處理方面，指導教授是 謝朝和教授，我們這組的題目為「廣播網球視訊中記分板資訊擷取與應用」，同時也有在校內研討會中得獎，內容主要是透過辨識網球影片中記分板的樣式與場地顏色來慮除非比賽畫面並輸出濃縮影片，也能透過辨識記分板中的球員姓名來得知該場比賽的球員資訊。這次的專題當中我負責的是前端的部分，負責與組員討論並規劃整個系統架構、系統介面、使用者操作流程等前端相關事項，在此之中也學習到如何設計一個能供使用者明確操作的介面，並了解如何使用流程圖與如何規劃時程，我覺得這是在課堂當中較不容易學習到的部分，但是卻是相當重要的一個環節。")
            )
        
    # 結合旋轉門選單中的"yourName工作經驗"，進到flexbubble選單，按下"yourName 職務經歷"，會有文字"我想看yourName的職務經歷"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看實習經歷')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="畢業專題結束之後我選擇了校外實習，一方面是想要了解職場中與學校的不同，另一方面是想藉此了解自己未來想走的方向。目前我實習的單位是中山科學研究院的資訊通信研究所，我的職場指導老師為 陳佑全中校。初入中科院時我負責設計一個彈性網頁系統，使用HTML、JavaScript與CSS來撰寫模組化程式，主要功能為讓使用者自行設計表單所需行列與樣式，也能自行輸入圖表資訊，不必再進入程式內部逐條新增或修改，目前也正在將此系統轉為MVC架構並完善此系統。同時我也負責小組內構型管理的部分，主要工作為協助測試開發中系統，列管問題清單與研發人員溝通，並且使用Git來進行版本控制，在餘下的時間內也跟著組內同仁學習機房內的工作事項。這些經驗讓我知道，與他人接觸時，如何在最短時間內了解對方狀況、以及排解問題，並能適時把狀況回報主管，讓主管了解狀況，我覺得這是很大的學問，也逐漸從中發現自己喜歡處理這樣的事務，能夠把事情處理的細膩、有條理，讓我十分有成就感。")
            )
    
    # 結合旋轉門選單中的"yourName工作經驗"，進到flexbubble選單，按下"yourName 在資策會的學習狀況"，會有文字"我想看yourName在資策會的學習狀況"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看微軟Codeing Angel活動經歷')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="在去年我報名了微軟的Coding Angels活動，也很榮幸能夠錄取去微軟的台灣總公司參與活動，這個活動是為了配合微軟總部鼓勵全世界的每個人都該學 Coding、體驗程式語言樂趣的宗旨，因此舉行了 HourofCode 的一系列活動，主要是讓我們學習R語言，並透過它來進行大數據分析，是一項蠻有意義的活動，也藉此機會能夠參觀到台灣微軟的總公司，是一次難能可貴的經驗呢!")
            )
        
    # 結合旋轉門選單中的"yourName的專長"，進到flexbubble選單，按下"yourName 的外語能力"，會有文字"我想看yourName的外語能力"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看證照資格')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="TQC-OA -英文輸入\nTQC-OA -Word\nTQC-OA -PowerPoint\n勞委會-電腦軟體應用證照(丙級)\nMaya - 建模動畫國際認證\nFlash ACA CS3核心能力認證\n企業電子化資料分析師-巨量資料處理與分析\nMTA-微軟專業應用技術國際認證")
            )
        
    # 結合旋轉門選單中的"yourName的專長"，進到flexbubble選單，按下"yourName 的IT專長"，會有文字"我想看yourName的IT專長"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看技術與專長')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="網路、雲端、系統、資安、3D建模、前端網頁程式、python、C#等領域")
            )
    
    # 結合旋轉門選單中的"yourName的專長"，進到flexbubble選單，按下"yourName 的其他專長"，會有文字"我想看yourName的其他專長"的輸入，當符合字串時判斷成立
    elif (event.message.text.find('我想看其他專長')!= -1):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="除了IT相關技術專長以外，演奏樂器也是我的興趣之一。中音笛與長笛是我擅長的樂器，很喜歡也很享受在演湊時能夠放下事物，僅專注在悠揚樂聲中的感覺。")
            )

     
    # 當用戶按下菜單的最右邊按鈕，會輸入more，符合字串more時判斷成立      
    elif (event.message.text.find('more')!= -1):  
        # 回覆訊息旋轉門選單
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="Tibame AWS 功能選單，為您服務",
                template=button_template_message
            )
        )
        
   
    # 收到不認識的訊息時，回覆原本的旋轉門菜單    
    else:         
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(
                alt_text="感謝您加入心瑜的履歷機器人\n想多了解我請使用下方功能選單\n或是按下方按鈕\n",
                template=button_template_message
            )
        )          


# In[ ]:


'''
    7.啟動server
    執行此句，啟動Server，觀察後，按左上方塊，停用Server

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])


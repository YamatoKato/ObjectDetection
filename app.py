from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time
import json



with open("secret.json") as f:      #jsonファイルからKEYとENDPOINTを取得する
    secret = json.load(f)

KEY = secret["KEY"]    #pythonでは変わることない値（定数）を大文字で表す
ENDPOINT = secret["ENDPOINT"]

#クライアントを認証する
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

#画像タグの取得
def get_tags(filepath):
    local_image = open(filepath, "rb")
    # Call API with remote image
    tags_result_local = computervision_client.tag_image_in_stream(local_image)
    tags = tags_result_local.tags
    tags_name = []
    for tag in tags:
        tags_name.append(tag.name)
    return tags_name

#objectの情報と位置を取得
def detect_objects(filepath):
    local_image = open(filepath, "rb")

    detect_objects_results = computervision_client.detect_objects_in_stream(local_image)
    objects = detect_objects_results.objects
    return objects



#=====================Streamlitで作成==============================
import streamlit as st
from PIL import ImageDraw
from PIL import ImageFont

st.title("画像からオブジェクトを検出するツール")
st.caption("※本ツールはMicrosoft AzureのComputer Vision APIを使用しています✌︎")

#fileをアップロードする,そして表示する
uploaded_file = st.file_uploader("検出する画像を選んでください",type=None)
if uploaded_file is not None:
    
    #読み込んだ画像ファイルをpathに変換する
    img_path = f"img/{uploaded_file.name}" #pathを作る
    img = Image.open(uploaded_file)
    img.save(img_path) #保存
    objects = detect_objects(img_path)
    
    
    #描画
    draw = ImageDraw.Draw(img)
    for object in objects:
        x = object.rectangle.x  #座標取得
        y = object.rectangle.y
        w = object.rectangle.w
        h = object.rectangle.h
        caption = object.object_property
        
        font = ImageFont.truetype(font="./Helvetica 400.ttf",size=50) #font情報作成
        text_w,text_h = draw.textsize(caption,font=font)
        
        draw.rectangle([(x,y),(x+w, y+h)], fill=None ,outline="red",width=4) #外枠
        draw.rectangle([(x,y),(x+text_w, y+text_h)], fill="Red") #枠の左上にobject名表示場所
        draw.text((x,y),caption,fill="white",font=font) #object名表示
        
    st.image(img)
    
    #認識されたコンテンツタグの表示
    tags_name = get_tags(img_path)
    tags_name = ", ".join(tags_name)
    st.markdown("**認識されたコンテンツタグ**")  #マークダウン方式で太字にする
    st.markdown(f"> {tags_name}")
    



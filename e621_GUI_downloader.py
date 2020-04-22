import os
import tkinter as tk
from tkinter import filedialog
import requests
import urllib.request
from bs4 import BeautifulSoup
import asyncio


theme_BG = "#082567"

global language
language = "EN"

# 使用者的輸入
global pictureNum
global folder_path
folder_path = ""
global userName
userName = "test"

# 輸出的資訊
global label_5

# 內部交換的數據
global IDOfEachPictures
global URLOfEachPictures
global extOfEachPictures
# global pictureIDs

def DownloadAllPicturesInList():
    global folder_path
    global label_5
    
    global IDOfEachPictures
    global URLOfEachPictures
    global extOfEachPictures

    folderName = "download" # @@
    os.makedirs(folder_path  + folderName, exist_ok=True) # 建立資料夾以儲存圖片
    if language == "EN":
        label_5.config(text = "Has created a dir called " + folderName + "\nDownloading...")
    elif language == "ZH-TW":
        label_5.config(text = "已新增資料夾，名為 : " + folderName + "\n開始下載...")

    for i in range(len(IDOfEachPictures)):
        if URLOfEachPictures[i] != None:
            filePath = folder_path + folderName + "/" + str(IDOfEachPictures[i]) + "." + extOfEachPictures[i]
            urllib.request.urlretrieve(URLOfEachPictures[i], filePath)
        else:
            if language == "EN":
                label_5.config(text = str(IDOfEachPictures[i]) + " failed to download")
            elif language == "ZH-TW":
                label_5.config(text = str(IDOfEachPictures[i]) + " 無法下載")

    return

def GetInfoFromJsonFiles(URL,pictureNum):
    # @@
    pages = 1
    remain = 0
    if pictureNum <= 320:
        picturesPerPage = pictureNum
        pages = 1
        remain = 0
    else:
        picturesPerPage = 320
        pages = floor(pictureNum / 320)
        remain = pictureNum - (320 * pages)

    API_URL = URL[0:22] + ".json"
    if len(URL) > 22:
        API_URL += URL[22:] + "&limit=" + str(picturesPerPage)
    else:
        API_URL += "?limit=" + str(picturesPerPage)

    global userName
    global label_5

    headers={'User-Agent':'MyProject/1.0 (by ' + userName + ' on e621)'}
    rs = requests.get(API_URL, headers=headers)
    if rs.status_code != requests.codes.OK:
        raise "Not found"
    else:
        if language == "EN":
            label_5.config(text = "Analyzing...")
        elif language == "ZH-TW":
            label_5.config(text = "網頁分析中")

    global IDOfEachPictures
    global URLOfEachPictures
    global extOfEachPictures
    list_of_posts = rs.json()['posts']
    if len(list_of_posts) == 0:
        raise "Not found"
    else:
        IDOfEachPictures = [post['id'] for post in list_of_posts]
        URLOfEachPictures = [post['file']['url'] for post in list_of_posts]
        extOfEachPictures = [post['file']['ext'] for post in list_of_posts]

    return


# Just in case the API can't work at some point, I'm keeping this
"""
def AnalyzeWebPageToGetPictureLink(URL):
    global label_5
    global pictureIDs
    headers={'User-Agent':'MyProject/1.0 (by username on e621)'}
    rs = requests.get(URL, headers=headers)
    if rs.status_code != requests.codes.OK:
        raise "Not found"
    else:
        if language == "EN":
            label_5.config(text = "Analyzing...")
        elif language == "ZH-TW":
            label_5.config(text = "網頁分析中")
    html_doc = rs.text
    soup = BeautifulSoup(html_doc, 'html.parser')
    try:
        if soup.select('div#page p')[-1].text == "Not found.":
            raise "Not found"
    except :
        pass

    # 開始收集本網頁的圖片ID
    pictureTitles = soup.select('article img')
    pictureIDs = [title.attrs['title'][title.attrs['title'].find('ID: ') + 4:].split('\n')[0] for title in pictureTitles]
    # 之後要改成收集很多個頁面的圖片ID，而不只是一個網頁 @@
    return
"""

def IsURLCorrect(URL):
    if URL[0:22] == "https://e621.net/posts":
        return True
    else:
        return False


def Run(input_URL):

    global label_5
    URL = input_URL.get()
    if URL == "":
        URL = "https://e621.net/posts"
        
    try:
        pictureNum = int(picture_Num.get()) # Should check if it is int @@
        if pictureNum <= 0: raise
    except :
        if language == "EN":
            label_5.config(text = "Please enter a positive integer")
        elif language == "ZH-TW":
            label_5.config(text = "請輸入正整數")
        return


    if not IsURLCorrect(URL):
        if language == "EN":
            label_5.config(text = "URL not correct")
        elif language == "ZH-TW":
            label_5.config(text = "網址格式不正確")
        return
    else:
        try:
            GetInfoFromJsonFiles(URL,pictureNum)
            # Just in case the API can't work at some point, I'm keeping this
            # AnalyzeWebPageToGetPictureLink(URL) 
        except "Not found":
            if language == "EN":
                label_5.config(text = "Not found")
            elif language == "ZH-TW":
                label_5.config(text = "找不到網頁")

        DownloadAllPicturesInList()
        if language == "EN":
            label_5.config(text = "Done")
        elif language == "ZH-TW":
            label_5.config(text = "下載完成")

    return

def switchLanguage():
    global language
    if language == "EN":
        label_1.config(text = "請輸入網址：")
        label_2.config(text = "欲下載的圖片數量：")
        label_3.config(text = "下載位置：")
        label_4.config(text = "(目前目錄)")
        browse_btn.config(text = "瀏覽")
        submit_btn.config(text = "開始下載")
        language_btn.config(text = "English")
        language = "ZH-TW"
    elif language == "ZH-TW":
        label_1.config(text = "Give me an URL：")
        label_2.config(text = "How many pictures：")
        label_3.config(text = "Download dir：")
        label_4.config(text = "(Now path)")
        browse_btn.config(text = "Browse")
        submit_btn.config(text = "Download")
        language_btn.config(text = "中文")
        language = "EN"
    return

def browse_button():
    global folder_path
    temp = filedialog.askdirectory()
    if temp != "":
        folder_path = temp + "/"
        label_4.config(text = folder_path)
    return


mainWondow = tk.Tk()

mainWondow.geometry("600x400")
mainWondow.resizable(False, False)
mainWondow.title("e621_GUI_downloader")
mainWondow.config(bg = theme_BG)

label_1 = tk.Label(bg = theme_BG, fg = "white", text = "Give me an URL：")
label_1.pack()

input_URL = tk.Entry(justify = "center")
input_URL.pack()

label_2 = tk.Label(bg = theme_BG, fg = "white", text = "How many pictures：")
label_2.pack()

picture_Num = tk.Entry(justify = "center")
picture_Num.pack()

label_3 = tk.Label(bg = theme_BG, fg = "white", text = "Download dir：")
label_3.pack()

label_4 = tk.Label(bg = theme_BG, fg = "white", text = "(Now path)")
label_4.pack()

browse_btn = tk.Button(text = "Browse")
browse_btn.config(command = browse_button)
browse_btn.pack()

loop = asyncio.get_event_loop()

submit_btn = tk.Button(text = "Download")
submit_btn.config(command = lambda : Run(input_URL))
submit_btn.pack()

label_5 = tk.Label(bg = theme_BG, fg = "white", text = "")
label_5.pack()

language_btn = tk.Button(text = "中文")
language_btn.config(command = switchLanguage)
language_btn.pack()


mainWondow.mainloop()

"""
TodoList:
更新某標籤的功能(下載直到遇到重複的檔案)
解開下載數量的上限(第二頁第三頁...)
依照標籤來命名資料夾
async/await
排版
還沒有登入的功能
也因此會跳過某些沒登入不能看的圖片
"""
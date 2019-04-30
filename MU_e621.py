import os
import sys
import math
import requests
import threading
import urllib.request
#from urllib.request import urlretrieve
from bs4 import BeautifulSoup

ThreadCount = 16

#URL = "https://e621.net/user/show/222675"
#URL = sys.argv[1]
while 1==1:
	URL_temp = input("請輸入網址\n>> ")
	#print(URL_temp[0:27])
	if URL_temp[0:27]=="https://e621.net/user/show/":
		URL = URL_temp
		TagSearchMode = 0
		print("格式正確")
		break
	elif URL_temp[0:28]=="https://e621.net/post/index/":
		URL = URL_temp
		TagSearchMode = 1
		print("功能還在測試中，有錯誤請回報")
		break
	else:
		print("請檢查網址格式")

headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0'}

rs = requests.get(URL, headers=headers)


if rs.status_code == requests.codes.OK:
	print("連線成功\n")
else:
	print("連線失敗\n")
	os.system("pause")
	os._exit(0)

html_doc = rs.text
soup = BeautifulSoup(html_doc, 'html.parser')

#print(rs) # 看HTML代碼
#print(rs.encoding) # 看編碼格式
#print(html_doc) # 看HTML本文

if TagSearchMode == 0: #如果是從資訊主頁開始爬
	sel = soup.select("div h2")
	uploaderName = sel[0].text.split("\n",1)[0] #把整個字串中的第一個token拆解出來
	folderName = uploaderName
	sel = soup.select("table.rounded tbody tr td a")
	totalPicture = int(sel[1].text)
	totalPage = int(math.ceil(totalPicture / 75))

	if uploaderName == "Users":
		print("使用者不存在\n")
		os.system("pause")
		os._exit(0)
	#上面取得了上傳者名字uploaderName跟圖片總數totalPicture跟總頁數totalPage
elif TagSearchMode == 1: #如果是從搜尋結果開始爬
	#要取得搜尋關鍵字，用來新增資料夾
	searchKeywords = URL[28:].split("/",2)[1] #把網址的最後一個token拆解出來
	folderName = searchKeywords.replace("%20", " & ") #取代字串
	#要取得總頁數，用來更改網址、告知進度和計算圖片總數
	sel = soup.select("div #paginator div a")
	if len(sel) == 0:
		totalPage = 1
	else:
		totalPage = int(sel[len(sel) - 2].text)
	#要取得圖片總數，用來告知進度
	totalPicture = 75 * (totalPage - 1) + 1


print("總頁數 : " + str(totalPage))
if TagSearchMode == 1:
	print("總圖片數 : " + str(totalPicture) + " ~ " + str(totalPicture + 74))
	print("(尚未掃描，無法得知確切數量)\n")
else:
	print("總圖片數 : " + str(totalPicture))


img_page = [] #宣告list

def scanAPage(page):
	if TagSearchMode == 1:
		URL = "https://e621.net/post/index/" + str(page) + "/" + str(searchKeywords)
	else:
		URL = "https://e621.net/post/index/" + str(page) + "/user:" + uploaderName

	rs = requests.get(URL, headers=headers)
	html_doc = rs.text
	soup = BeautifulSoup(html_doc, 'html.parser')
	sel = soup.select("span.thumb a") #取HTML中的<div class="title"></div>中的<a>標籤存入sel
	numOfSub_URL = len(sel)
	#print(type(sel)) #看sel的型別

	for index in range(numOfSub_URL):
		#print(sel[index]["href"])
		img_page.append("https://e621.net" + sel[index]["href"]) #把每個網址都加到list末

	#print("下一頁")


print("開始掃描...")
threads = []
for page in range(totalPage):
	threads.append(threading.Thread(target=scanAPage, args=(page + 1,)))
	threads[page].start()

for i in range(totalPage):
	threads[i].join()
	#print("已掃描頁數 : " + str(i + 1) + "/" + str(totalPage))

numOfSub_URL = len(img_page)
print("已掃描圖片數 : " + str(numOfSub_URL))

folderName = folderName.replace(":", "：")
os.makedirs(folderName, exist_ok=True) #建立目錄存放檔案
print("已新增資料夾，名為 : " + folderName)
print("\n開始下載...")
downloadedNum = 0

def downloadSomePIC(strat_num, end_num):
	for index in range(strat_num, end_num):
		global downloadedNum
		#print(img_page[index])
		rs = requests.get(img_page[index], headers=headers)
		html_doc = rs.text
		soup = BeautifulSoup(html_doc, 'html.parser')
		sel = soup.select("div h4 a")
		#print(sel[0]["href"])
		#print(sel[0]["href"].split("/")[6])
		urllib.request.urlretrieve(sel[0]["href"], folderName + "/" + sel[0]["href"].split("/")[6]) #把檔名拆解出來並儲存
		downloadedNum += 1
		print("已下載 : " + str(downloadedNum) + "/" + str(len(img_page)))
	
numOfSub_URL = len(img_page)
strat_num = 0
end_num = 0
PICsPerThread = int(numOfSub_URL / ThreadCount)

#print(numOfSub_URL)
#downloadSomePIC(strat_num, end_num)
# 建立 ThreadCount 個子執行緒

threads = []
for i in range(ThreadCount):
	end_num = strat_num + PICsPerThread
	if (i == ThreadCount - 1):
		end_num = numOfSub_URL
	#print(str(strat_num) + " to " + str(end_num))
	threads.append(threading.Thread(target=downloadSomePIC, args=(strat_num, end_num)))
	threads[i].start()
	strat_num = end_num

for i in range(ThreadCount):
	threads[i].join()

print("\n下載完成\n")
os.system("pause")

#要整理程式碼
#考慮網址是在最後一頁的情形
#要找750頁以後的圖片
#之後再加上檔案重複不下載的功能
#還有可以指定頁數的範圍
#新增網站拒絕連線的例外狀況
#沒有圖片就不要新增資料夾

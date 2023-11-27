from flask import Flask, render_template,request
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    x ="作者-林映均11/26<br>"
    x +="<a href=/mis>資管導論</a><br>"
    x +="<a href=/today>日期時間</a><br>"
    x +="<a href=/about>映均網頁</a><br>"
    x +="<a href=/welcome?guest=julia>歡迎蒞臨</a><br>"
    x +="<a href=/account>mmi密碼</a><br>"
    x +="<a href=/wave_sort>人選之人─造浪者清單</a><br><br>"
    x +="<a href=/addbooks>圖書精選</a><br><br>"
    x +="<a href=/searchbk>根據關鍵字查詢圖書</a><br><br>"
    x +="<a href=/spider2>網路爬蟲擷取子青老師的課程資料</a><br><br>"
    x +="<a href=/movie>讀取開眼電影即將上映影片，寫入Firestore</a><br><br>"
    x +="<a href=/searchQ>查詢開眼電影即將上映影片</a><br><br>"
    return x

@app.route("/mis")
def course():
    return "<h1>資訊管理導論</h1>"

@app.route("/today")
def today():
    now = datetime.now()
    return render_template("today.html",datetime = str(now))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/welcome", methods=["GET", "POST"])
def welcome():
     user = request.values.get("guest")
     return render_template("welcome.html", name=user)

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/wave_sort")
def wave_sort():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("人選之人─造浪者")    
    docs = collection_ref.order_by("birth",direction=firestore.Query.DESCENDING).get()   
    for doc in docs:         
        Result += "文件內容：{}".format(doc.to_dict()) + "<br>"    
    return Result

@app.route("/addbooks")
def addbooks():
    Result = ""
    db = firestore.client()
    collection_ref = db.collection("圖書精選")    
    docs = collection_ref.order_by("anniversary").get()   
    for doc in docs:
        bk = doc.to_dict()        
        Result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "</a><br><br>"
        Result += "作者: " + bk["author"] + "<br><br>" 
        Result += str(bk["anniversary"]) + "週年紀念版" + "<br><br>"
        Result += "<img src=" + bk["cover"] + "></img><br><br>"
    return Result

@app.route("/searchbk", methods=["GET", "POST"])
def searchbk():
    if request.method == "POST":
        keyword = request.form["keyword"]
        Result = "您輸入的關鍵字是：" + keyword
        Result = ""
        db = firestore.client()
        collection_ref = db.collection("圖書精選")    
        docs = collection_ref.order_by("anniversary").get()   
        for doc in docs:
            bk = doc.to_dict()
            if keyword in bk["title"]:        
                Result += "書名:<a href=" + bk["url"] + ">" + bk["title"] + "</a><br><br>"
                Result += "作者: " + bk["author"] + "<br><br>" 
                Result += str(bk["anniversary"]) + "週年紀念版" + "<br><br>"
                Result += "<img src=" + bk["cover"] + "></img><br><br>"
        return Result
    else:
        return render_template("searchbk.html")

@app.route("/spider2")
def spider2():
    info = ""

    url = "https://www1.pu.edu.tw/~tcyang/course.html"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    #print(Data.text)
    sp = BeautifulSoup(Data.text, "html.parser")
    result=sp.select(".team-box")

    for x in result:
            info += "<a href=" + x.find("a").get("href") + ">" + x.find("h4").text + "</a><br>"
            info += x.find("p").text + "<br>"
            info += x.find("a").get("href") + "<br>"
            info += "<img src=https://www1.pu.edu.tw/~tcyang/" + x.find("img").get("src") + " width=200 height=300 " + "</img><br>"

    return info


@app.route("/movie")
def movie():
  url = "http://www.atmovies.com.tw/movie/next/"
  Data = requests.get(url)
  Data.encoding = "utf-8"
  sp = BeautifulSoup(Data.text, "html.parser")
  result=sp.select(".filmListAllX li")
  lastUpdate = sp.find("div", class_="smaller09").text[5:]

  for item in result:
    picture = item.find("img").get("src").replace(" ", "")
    title = item.find("div", class_="filmtitle").text
    movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
    hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
    show = item.find("div", class_="runtime").text.replace("上映日期：", "")
    show = show.replace("片長：", "")
    show = show.replace("分", "")
    showDate = show[0:10]
    showLength = show[13:]

    doc = {
        "title": title,
        "picture": picture,
        "hyperlink": hyperlink,
        "showDate": showDate,
        "showLength": showLength,
        "lastUpdate": lastUpdate
      }

    db = firestore.client()
    doc_ref = db.collection("電影").document(movie_id)
    doc_ref.set(doc)    
  return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 


@app.route("/searchQ", methods=["POST","GET"])
def searchQ():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""
        db = firestore.client()     
        collection_ref = db.collection("電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：" + doc.to_dict()["title"] + "<br>" 
                info += "影片介紹：" + doc.to_dict()["hyperlink"] + "<br>"
                info += "片長：" + doc.to_dict()["showLength"] + " 分鐘<br>" 
                info += "上映日期：" + doc.to_dict()["showDate"] + "<br><br>"           
        return info
    else:  
        return render_template("input.html")


#if __name__ == "__main__":
    #app.run(debug=True)



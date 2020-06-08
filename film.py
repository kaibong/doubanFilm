# -*- coding: UTF-8 -*-
import urllib.request
import re
import random
import time
import pymysql
import string
# 建立链接
conn=pymysql.connect(
    host='localhost',#我的IP地址
    port=3306,   # 不是字符串不需要加引号。
    user='root',
    password='root',
    db='kimodi',
    charset='utf8mb4'
)
# 用户代理池
uapools=[
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36Edge/13.10586',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27',
        'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv 11.0) like Gecko'
        ]
thisua = random.choice(uapools)
headers = ("UserAgent",thisua)
opener=urllib.request.build_opener()
opener.addheaders=[headers]
# 获取页面数据
data=opener.open("https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&page_limit=50&page_start=0").read().decode("utf-8")
pat = '"url":"(https:.*?)"'
url = re.compile(pat).findall(data)

# 获取电影页面消息
for i in url:
    thisurl = re.sub("\\\/","/",i)
    thisua = random.choice(uapools)
    headers = ("UserAgent",thisua)
    opener1=urllib.request.build_opener()
    opener1.addheaders=[headers]
    filmdata=opener.open(thisurl).read().decode("utf-8")
    patid = 'm.douban.com/movie/subject/(.*?)/'
    patname = '<span property="v:itemreviewed">(.*?)</span>'
    patdirector = 'rel="v:directedBy">(.*?)</a>'
    pattype = '<span property="v:genre">(.*?)</span>'
    pattime = '<span property="v:runtime" content="(.*?)">'
    patrate = 'property="v:average">(.*?)</strong>'
    filmid = re.compile(patid).findall(filmdata)
    filmname = re.compile(patname).findall(filmdata)
    director = "、".join(re.compile(patdirector).findall(filmdata))
    filmtype = "/".join(re.compile(pattype).findall(filmdata))
    filmtime = re.compile(pattime).findall(filmdata)
    rate = re.compile(patrate).findall(filmdata)
    print([filmid, filmname, director, filmtype, filmtime, rate])
    #查询电影是否已存在
    cursor = conn.cursor()
    sqlselect = 'select * from `kimodi`.`film` where id  = %s'
    cursor.execute(sqlselect,filmid)
    isExist = cursor.fetchall()
    if int(len(isExist)) >0 :
        continue
    cursor.close()
    #获取光标
    cursor = conn.cursor()
    sql1 = 'INSERT INTO `kimodi`.`film`(`id`, `name`, `director`, `type`, `time`, `rate`) VALUES (%s, %s, %s, %s, %s, %s);'
    sql2 = 'INSERT INTO `kimodi`.`comment`(`filmid`, `username`, `content`, `judge`) VALUES (%s, %s, %s, %s);'
    cursor.execute(sql1,[filmid, filmname, director, filmtype, filmtime, rate])
    conn.commit()
    cursor.close()
    for j in range(0,4):
        commenturl = 'https://movie.douban.com/subject/'+filmid[0]+'/comments?start='+str(j*20+1)+'&limit=20&sort=new_score'
        print(commenturl)
        thisua = random.choice(uapools)
        headers = ("UserAgent",thisua)
        opener1=urllib.request.build_opener()
        opener1.addheaders=[headers]
        commentdata=opener.open(commenturl).read().decode("utf-8")
        patusername = '<a href="https://www.douban.com/people/.*?/" class="">(.*?)</a>'
        patcontent = '(?<=\<span class="short"\>)(?:.|\n)+?(?=\<)'
        patjudge = '<span>看过</span>(.*?)<span class="comment-time'
        username = re.compile(patusername).findall(commentdata)
        content = re.compile(patcontent).findall(commentdata)
        judge = re.compile(patjudge,re.DOTALL).findall(commentdata)
        print(len(username),len(content),len(judge))
        for i in range(0,len(username)):
            pathow = 'title="(.*?)"'
            onlyjudge = re.compile(pathow).findall(judge[i])
            if len(onlyjudge)==0:
                onlyjudge = ["未评价"]
            cursor = conn.cursor()
            print(filmid, username[i], content[i], onlyjudge)
            cursor.execute(sql2, [filmid, username[i], content[i], onlyjudge])
            conn.commit()
            cursor.close()
        time.sleep(20)
    time.sleep(10)

conn.close()


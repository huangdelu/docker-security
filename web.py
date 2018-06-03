#!/usr/bin/python
#_*_coding:utf-8_*_
import DockerPs
import requests
from flask import Flask,request,render_template,redirect,url_for
import sqlite3
import sys
import os
import datetime
import json
from flask_cors import *
import score

app = Flask(__name__)
CORS(app, supports_credentials=True)
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

hconn = sqlite3.connect('history.db',check_same_thread = False)
hc = hconn.cursor()
#获取数据库地址和md5值
def getinfo():
    searchsql = "select * from cache where id = 1"
    hc.execute(searchsql)
    info = hc.fetchall()
    hconn.commit()
    return info[0]

@app.route('/',methods=['GET','POST'])
def runform():
    SkyLineIP = ''
    ContainerMessage,Containerheaders ,SkyLineIP = DockerPs.ContainerPs()
    ImageMessage,Imageheaders =DockerPs.ImagePs()
    print "skylineIP:%s"%(SkyLineIP)
    if request.method == 'GET':
        if SkyLineIP:
            return render_template('start.html',containers=ContainerMessage,header = Containerheaders, Images = ImageMessage, Imageheader = Imageheaders,SkylineIP = SkyLineIP)
        else:
            return render_template("check.html")
    else:
        ChoseId = request.form.get('containerID')
        ChoseId = str(ChoseId)
        print ChoseId
        Type,Id = ChoseId.split(":")
        if Type == "C":
            FilePath = DockerPs.DockerExport(Id)
        elif Type == "I":
            FilePath = DockerPs.DockerSave(Id)
        image_name = os.path.join(os.getcwd(),FilePath)
        md5 = os.popen("md5sum %s"%(image_name)).read().split("  ")[0]
        #将md5值写入缓存
        cachesql = "update cache set md5 = '%s' where id = 1"%(md5)
        hc.execute(cachesql)
        hconn.commit() 
        #发送文件到检测平台
        url = 'http://%s:9001/upload'%SkyLineIP.replace("\n","")
        SendFile = {'file':open(FilePath,'rb+')}
        r = requests.post(url, files=SendFile)
        return redirect(url_for("receive",_external=True,ID = Id))
@app.route('/result',methods=['GET','POST'])
def receive():
    if request.method == 'GET':
        ChoseId = request.args.get('ID')
        #连接检测结果数据库
        if ChoseId:
            dbname = "result/%s/%s.db"%(ChoseId,ChoseId)
            cachesql = "update cache set dbname = '%s' where id = 1"%(dbname)
            cursor = hc.execute(cachesql)
            hconn.commit()
        return redirect(url_for("index",_external=True))
    if request.method == 'POST':
        file = request.files['result']
        if file:
            filePath = 'result/'+file.filename
            f = open(filePath,'wb+')
            f.write(file.read())
            f.close()
            return 'OK'
@app.route('/index',methods=['GET','POST'])
def index():
     if request.method == 'GET':
         info = getinfo()
         print info
         ChoseId = os.path.basename(info[1]).split(".")[0]
         tarfile="result/%s.tar"%ChoseId
         if os.path.exists(tarfile):
            if not os.path.exists(info[1]):
                if not os.path.exists("result/%s"%ChoseId):
                    os.mkdir("result/%s"%ChoseId)
                ReleasePath="result/%s"%ChoseId
                os.popen("tar xvf %s -C %s"%(tarfile,ReleasePath))
                print "tar xvf %s -C %s"%(tarfile,ReleasePath)
                dbname = "result/%s/%s.db"%(ChoseId,ChoseId)
            else:
                dbname = info[1]
            conn = sqlite3.connect(dbname)
            c = conn.cursor()
            #获取主页信息
            indexsql = "select * from indexinfo"
            cursor = c.execute(indexsql)
            for row in cursor:
                indexinfo = list(row)
            #获取漏洞详情
            sqlfind = "select * from CVEdetail"
            resfind = c.execute(sqlfind)
            CVEdtl = resfind.fetchall()
            #获取恶意文件详情
            sqlfind = "select * from evilfile"
            resfind = c.execute(sqlfind)
            evildtl = resfind.fetchall()
            #获取恶意外连IP
            sqlfind = "select * from outIP"
            resfind = c.execute(sqlfind)
            evilIP = resfind.fetchall()
            #获得外连的域名
            sqlfind = "select * from outdomain"
            resfind = c.execute(sqlfind)
            evildomain = resfind.fetchall()
            #获取外连IP的数目
            countsql = "SELECT count(*) from outIP"
            res = c.execute(countsql)
            countevilIP = res.fetchall()[0][0]
            #获取外连域名的数目
            countsql = "SELECT count(*) from outdomain"
            res = c.execute(countsql)
            countevildomain = res.fetchall()[0][0]

            evilIPnum = countevilIP + countevildomain
            CVEscore,EFscore,IPscore,totalscore = score.getscore(int(indexinfo[8]),int(indexinfo[10]),evilIPnum)
            #转换数据类型
            for i in range(4,11):
                indexinfo[i] = int(indexinfo[i])
            md5 = row[1]
            cachesql = "update cache set md5 = '%s' where id = 1"%(md5)
            cursor = hc.execute(cachesql)
            hconn.commit()
            path = "result/%s/%s.png"%(ChoseId,ChoseId)
            imgpath=''
            if os.path.exists(path):
                os.system('mv %s static/img'%(path))
                imgpath = "static/img/%s.png"%(ChoseId)
            return render_template("index.html",indexinfo = indexinfo,imgpath = imgpath,CS = CVEscore,ES=EFscore,IS=IPscore,TS=totalscore,CVEdtl=CVEdtl,evildtl=evildtl,evilIP=evilIP,evildomain = evildomain)
         else:
            return '检测结果未找到  请检测%s/result 是否存在%s.tar'%(os.getcwd(),ChoseId)
     if request.method == 'POST':
        file = request.files['result']
        if file:
            filePath = 'result/'+file.filename
            f = open(filePath,'wb+')
            f.write(file.read())
            f.close()
            return 'OK'
#展示漏洞详情、外连IP详情、外连恶意IP&恶意域名、恶意文件、镜像内置程序列表
@app.route('/CVEdetails',methods=['GET','POST'])
def runCVEdetails():
    info = getinfo()
    print info
    dbname,md5 = info[1],info[2]

    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlfind = "select * from CVEdetail where md5 = '%s'"%(md5)
    resfind = c.execute(sqlfind)
    CVEdtl = resfind.fetchall()

    return render_template('CVEdetails.html',CVEdetails=CVEdtl)

@app.route('/IPdetails',methods=['GET','POST'])
def runIPdetails():
    info = getinfo()
    print info
    dbname,md5 = info[1],info[2]
    if request.method == "GET":
        conn = sqlite3.connect(dbname)
        c = conn.cursor()
        cursor = c.execute("select * from IPinfo where md5 = '%s'"%(md5))
        IPinfo = cursor.fetchall()
        print IPinfo[0]
        cursor = c.execute("select * from outIP where md5 = '%s'"%(md5))
        outIP = cursor.fetchall()

        cursor = c.execute("select * from domaininfo where md5 = '%s'"%(md5))
        domaininfo = cursor.fetchall()

        cursor = c.execute("select * from outdomain where md5 = '%s'"%(md5))
        outdomain = cursor.fetchall()

        conn.close()
        return render_template('IPdetails.html',IPinfo=IPinfo)


@app.route('/evilIP',methods=['GET','POST'])
def runoutIP():
    info = getinfo()
    print info
    dbname,md5 = info[1],info[2]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    cursor = c.execute("select * from outIP where md5 = '%s'"%(md5))
    outIP = cursor.fetchall()
    cursor = c.execute("select * from outdomain where md5 = '%s'"%(md5))
    outdomain = cursor.fetchall()
    return render_template('outIP.html',outIP = outIP,outdomain=outdomain)

@app.route('/evilfile',methods=['GET','POST'])
def runevilfile():
    info = getinfo()
    print info
    dbname,md5 = info[1],info[2]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlfind = "select * from evilfile where md5 = '%s'"%(md5)
    resfind = c.execute(sqlfind)
    evildtl = resfind.fetchall()
    conn.close()
    return render_template('evilfile.html',evilfile=evildtl)

@app.route('/program',methods=['GET','POST'])
def runprogram():
    info = getinfo()
    print info
    dbname,md5 = info[1],info[2]
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    sqlfind = "select * from programlist where md5 = '%s'"%(md5)
    resfind = c.execute(sqlfind)
    proinfo = resfind.fetchall()
    conn.close()
    return render_template('program.html',proinfo=proinfo)
#获取检测的进度信息
@app.route('/cgetnew',methods=['GET','POST'])
def cgetnew():
    data = request.form.get('data')
    url = data
    result = os.popen('curl %s'%(url)).read()
    print '================='
    print result
    returnjson = json.dumps(json.loads(result))
    return returnjson
app.run(host='0.0.0.0',port=8004,debug=True)

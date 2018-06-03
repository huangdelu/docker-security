#!/usr/bin/python
#_*_coding:utf-8_*_
import os 
import re
def ContainerPs():
    ContainerInfo = []
    split_header = []
    #匹配出容器信息
    result = os.popen("docker ps").read().replace("\n","\n\n")
    patt = re.compile("\n+(.*?)\n",re.S)
    #匹配出容器ID
    IdPatt = re.compile('^(\S*)',re.S)
    #匹配头部信息  及容器ID、容器镜像...
    HeaderPatt =  re.compile("^(.*?)\n",re.S)
    Header = re.findall(HeaderPatt,result)[0].split('  ')
    for b in Header:
        if b:
          split_header.append(b)
    DockerInfo = re.findall(patt,result)
    #容器信息处理   port为空赋值为NULL
    for item in DockerInfo:
        count = 0  #计算docker ps中的个数为六个还是七个
        meaning = [] #保存每一行docker ps中的有效数据
        split = item.split('  ')
        for a in split:
            if  a:
                count +=1
                meaning.append(a)
        if len(meaning) == 6:
            tmp=meaning[5]
            meaning[5]='NULL'
            meaning.append(tmp)
        ContainerId = re.findall(IdPatt,item)
        ContainerInfo.append([meaning,ContainerId])
    #不显示出docker安全检测平台运行的信息
    ContainerInfoCopy = ContainerInfo
    SkyLineIP = ''
    for item in ContainerInfoCopy:
        EachIP = os.popen("docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' %s"%item[1][0]).read()
        try:
            CheckContent = os.popen("curl 'http://%s:9001/upload'"%EachIP.replace("\n",'')).read()
            if CheckContent == 'skylinedocker':
                ContainerInfo.remove(item)
                SkyLineIP = EachIP
                break
        except Exception,e:
            print e
            continue 
    return ContainerInfo,split_header,SkyLineIP
#显示本地镜像信息
def ImagePs():
    ImageInfo = []
    split_header = []
    #匹配镜像信息
    result = os.popen("docker images").read().replace('\n','\n\n')
    patt = re.compile("\n+(.*?)\n",re.S)
    Images = re.findall(patt,result)
    #匹配头部信息
    HeaderPatt =  re.compile("^(.*?)\n",re.S)
    Header = re.findall(HeaderPatt,result)[0].split('  ')
    for b in Header:
        if b:
          split_header.append(b)
    #镜像信息处理
    for item in Images:
        meaning = []
        split = item.split('  ')
        for a in split:
            if a:
                meaning.append(a)
        ImageInfo.append([meaning,meaning[2]])
    return ImageInfo,split_header
#为容器时使用docker export将容器保存成镜像，如果日志存在则将一起打包
def DockerExport(ContainerId):
    try:
        if not os.path.exists("file"): #在当前目录创建file文件保存镜像
            os.popen("mkdir file")
        print '正在将容器保存镜像' 
        OutFile = 'file%s%s.export'%(os.sep,ContainerId)
        os.popen('docker export %s -o %s'%(ContainerId,OutFile))
        LogPath = SeekLogPath(ContainerId)
        if os.path.exists(LogPath):
            os.popen("tar -rvf %s %s"%(OutFile,LogPath))
            print '日志文件已打包'
        else:
            print '日志文件未找到'
        if os.path.exists(OutFile):
            print '镜像保存完成 保存为file%s%s.export'%(os.sep,ContainerId)
        else:
            print '镜像保存失败'
    except Exception,e:
        print e    
        print '镜像保存失败'
    return OutFile
#使用docker save将docker save保存
def DockerSave(ImageId):
    try:
        if not os.path.exists("file"): #在当前目录创建file文件保存镜像
            os.popen("mkdir file")
        print '正在将容器保存镜像'
        OutFile = 'file%s%s.save'%(os.sep,ImageId)
        os.popen('docker save %s -o %s'%(ImageId,OutFile))
        if os.path.exists(OutFile):
            print '镜像保存完成 保存为file%s%s.save'%(os.sep,ImageId)
            print '正在检测分析。。。。'
        else:
            print '镜像保存失败'
    except Exception,e:
        print e
        print '镜像保存失败'
    return OutFile
#获得容器运行的日志
def SeekLogPath(ContainerID): #ContainerID是需要检测的容器ID (type: str)
    LogPath = os.popen('docker inspect %s | grep LogPath' % (ContainerID)).read()
    LogPath = LogPath.replace(' ','').replace('"LogPath":','').replace('"','').replace(',','')
    return LogPath

if __name__ == '__main__':
     message,header = DockerPs()
     chose = 0
     print header 
     for item in message:
         chose=chose+1
         print '%s   message: %s'%(chose,item[0])
     CheckId=int(raw_input('请输入您要检测的容器:'))
     print '======================================='
     print '您选择的是容器%s'%(message[CheckId-1][1])
     DockerExport(message[CheckId-1][1][0])

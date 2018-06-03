-Skyline_docker
===
-Skyline团队的docker安全检测平台客户端
---
 本项目需结合docker安全检测平台一起使用，能够获取并显示本地主机已有的docker镜像与正在运行的docker容器，实现对用户选择上传的docker容器或镜像的动静态综合检测  

-文件介绍
---
-	1. web.py    启用flask框架，通过网页进行交互以及检测结果的可视化展示
-	2. DockerPs.py    本地docker容器和镜像信息的展示
-    3. score.py  对检测完成docker容器/镜像的结果进行评分，包括程序漏洞评分、恶意文件评分、外连IP&域名评分、总分
-    4. result     接收docker安全检测平台的检测结果文件
-    5. file       被打包的docker文件存放位置
-    6. static、templates    网页文件存放位置


-运行环境：
---
- python编译器环境：python2.7以上
-	需在本机安装docker服务 
-	运行的主机需要能够访问互联网、主机上运行的docker容器也需要能够访问互联网  

-使用方法：
---
-下载并启动docker安全检测平台
-    1.1需在本机安装docker服务  
-    1.2下载docker安全检测平台镜像：docker pull registry.cn-shenzhen.aliyuncs.com/skylinedocker/dockerdetect:latest  
-    1.3 启动docker安全检测平台镜像：docker run –id –t [ImgID] /bin/bash ./root/receive/start.sh
-

-运行项目
----
-        $ git clone https://github.com/huangdelu/skyline_docker.git
-        $ cd skyline_docker
-        $ pip install -r requirements.txt
-        $ python web.py
-        打开本机浏览器，访问http://[本机IP]:8004  

-项目截图<br>  
---

-&emsp;&emsp;交互界面

-       1. 首页信息
-![image](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/index.png)
-  
-      2. 选择要检测的容器或者镜像，点击检测开始检测
-![image](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/chose.png)   


-&emsp;&emsp;结果展示</br>


    等待检测完成，检测完成后会跳到首页界面显示容器或者镜像检测的综合报告，docker镜像检测的分项报告如2-4所示；如果选择的检测目标是容器，那么除了会给出容器打包成镜像的检测结果，还会显示容器的动态性检测结果，包括外连的ip和域名的分析如5-6所示.   
-
-     1. 首页信息
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/indexinfo.png)
-  
-     2. 漏洞详情   
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/cveinfo.png)   
-  
-     3. 内置程序列表详情     
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/program.png)   
- 
-     4. 恶意文件详情  
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/evilfile.png)  
-   
-     5  外连IP信息详情  
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/ipinfo.png)   
-
-     6. 外连恶意IP&域名详情 
-![Image text](https://github.com/huangdelu/skyline_docker/blob/master/img_folder/evilip.png) 

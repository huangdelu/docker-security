#!/usr/bin/python
#_*_coding:utf-8_*_


#评分系统
def getscore(CVEnum,evilfilenum,evilIPnum):
    def myscore(num,times):
        score = 100 - num*times
        if score < 0:
            score = 0
        return str(score)
    a,b,c = myscore(CVEnum,10),myscore(evilfilenum,10),myscore(evilIPnum,10)
    aver = str((int(a)+int(b)+int(c))/3)
    return a,b,c,aver
 

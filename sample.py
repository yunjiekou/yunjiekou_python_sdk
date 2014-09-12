#coding:utf-8
'''
Created on 2014-6-19

@author: mushua
'''
from yunjiekou import YunJieKou


api = YunJieKou()
result = api.getResponse("yundou/balance")
print repr(result)
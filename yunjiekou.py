#coding:utf-8
#!/usr/bin/env python
#
# Copyright 2014 yunjiekou.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import httplib
import json
import time
from twisted.python.hashlib import md5
import urllib
import urllib2


YJK_API_HOST = 'api.yunjiekou.com'
YJK_API_VERSION = '1.0'

YJK_APP_KEY = 'YOUR APP KEY'
YJK_APP_SECRET = 'YOUR APP SECRET'

P_APPKEY = "appkey"
P_API = "method"
P_VERSION = "v"
P_FORMAT = "format"
P_TIMESTAMP = "timestamp"
P_SIGN = "sign"
P_SIGN_METHOD = "sign_method"

P_CODE = 'code'
P_SUB_CODE = 'sub_code'
P_MSG = 'msg'
P_SUB_MSG = 'sub_msg'


SUB_PATH = '/'

def sign(secret, parameters):
    #===========================================================================
    # '''签名方法
    # @param secret: 签名需要的密钥
    # @param parameters: 支持字典和string两种
    # '''
    #===========================================================================
    # 如果parameters 是字典类的话
    if hasattr(parameters, "items"):
        
        keys = parameters.keys()
        keys.sort()
        
        parameters = "%s%s%s" % (secret,
            str().join('%s%s' % (key, parameters[key]) for key in keys),
            secret)
        
    
        
    sign = md5(parameters).hexdigest().lower()
    
    return sign

def mixStr(pstr):
    if(isinstance(pstr, str)):
        return pstr
    elif(isinstance(pstr, unicode)):
        return pstr.encode('utf-8')
    else:
        return str(pstr)
    

class YunJieKouException(Exception):
    #===========================================================================
    # 业务异常类
    #===========================================================================
    def __init__(self):
        self.errorcode = None
        self.message = None
        self.subcode = None
        self.submsg = None
        self.application_host = None
        self.service_host = None
    
    def __str__(self, *args, **kwargs):
        sb = "errorcode=" + mixStr(self.errorcode) +\
            " message=" + mixStr(self.message) +\
            " subcode=" + mixStr(self.subcode) +\
            " submsg=" + mixStr(self.submsg) +\
            " application_host=" + mixStr(self.application_host) +\
            " service_host=" + mixStr(self.service_host)
        return sb
       
class RequestException(Exception):
    #===========================================================================
    # 请求连接异常类
    #===========================================================================
    pass

class YunJieKou(object):
    #===========================================================================
    # Rest api的基类
    #===========================================================================
    
    def __init__(self, domain=YJK_API_HOST, port = 80):
        #=======================================================================
        # 初始化基类
        # Args @param domain: 请求的域名或者ip
        #      @param port: 请求的端口
        #=======================================================================
        self.__domain = domain
        self.__port = port
        self.__httpmethod = "POST"
        
        self.__app_key = YJK_APP_KEY
        self.__secret = YJK_APP_SECRET
        
    def get_request_header(self):
        return {
                 'Content-type': 'application/x-www-form-urlencoded',
                 "Cache-Control": "no-cache",
                 "Connection": "Keep-Alive",
        }
        
    def set_app_info(self, appinfo):
        #=======================================================================
        # 设置请求的app信息
        # @param appinfo: import top
        #                 appinfo top.appinfo(appkey,secret)
        #=======================================================================
        self.__app_key = appinfo.appkey
        self.__secret = appinfo.secret
        
    
    def getResponse(self, api_name, timeout=30):
        #=======================================================================
        # 获取response结果
        #=======================================================================
        
        print str(self.__domain)+str(self.__port)
        connection = httplib.HTTPConnection("api.yunjiekou.com", self.__port, timeout=timeout)
        sys_parameters = {
            P_FORMAT: 'json',
            P_APPKEY: self.__app_key,
            P_SIGN_METHOD: "md5",
            P_VERSION: YJK_API_VERSION,
            P_TIMESTAMP: str(long(time.time() * 1000)),
            P_API: api_name
        }
        sign_parameter = sys_parameters.copy()
        sys_parameters[P_SIGN] = sign(self.__secret, sign_parameter)
#         connection.connect()
        
        header = self.get_request_header();

        url =  SUB_PATH+"?"+urllib.urlencode(sys_parameters)
        print str(url)
        connection.request(self.__httpmethod, url,  headers=header)
        response = connection.getresponse();
        
        print str(response.status)
        
        
        if response.status is not 200:
            raise RequestException('invalid http status ' + str(response.status) + ',detail body:' + response.read())
        result = response.read()
        jsonobj = json.loads(result)
        if jsonobj.has_key("error_response"):
            error = YunJieKouException()
            if jsonobj["error_response"].has_key(P_CODE) :
                error.errorcode = jsonobj["error_response"][P_CODE]
            if jsonobj["error_response"].has_key(P_MSG) :
                error.message = jsonobj["error_response"][P_MSG]
            if jsonobj["error_response"].has_key(P_SUB_CODE) :
                error.subcode = jsonobj["error_response"][P_SUB_CODE]
            if jsonobj["error_response"].has_key(P_SUB_MSG) :
                error.submsg = jsonobj["error_response"][P_SUB_MSG]
            error.application_host = response.getheader("Application-Host", "")
            error.service_host = response.getheader("Location-Host", "")
            raise error
        return jsonobj
    

# coding=utf-8
#!/usr/bin/python
import re
import sys
import json
import time
import base64
import hashlib
import random
import string
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base.spider import Spider

sys.path.append('..')

class Spider(Spider):
    def __init__(self):
        self.name = "瓜子"
        self.hosts = [
            'https://apinew.uozvr.com',
            'https://api.w32z7vtd.com',
            'https://api.6a7nnf7.com',
            'https://api.umygrx3.com',
            'https://api.rmedphk.com'
        ]
        self.host_index = 0
        self.host = self.hosts[self.host_index]

        # AES密钥 完全沿用你原有配置
        self.AES_KEY = 'OITxa5OqAYjhswxx'
        self.AES_IV = 'rCMNwZASNBKZ8mXV'

        # RSA公私钥 完全沿用你原有配置
        self.RSA_PUBLIC_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUM5+/y8sPsWkd1/RQS64X259EUwxFXFE5HlA65MqrxnPs0JqoSRojSDy5QhwvROlaD6TwRQHKMY2OAZ6SnQeUJsChTEFIR9qUkwrs3/MVUMxjsv6JS6Oe/juclyJGTgVmDhB55EafXsD0SQYVj/QXXsxR6ewR5E2kL52yAAD4yQIDAQAB"
        self.RSA_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGAe6hKrWLi1zQmjTT1
ozbE4QdFeJGNxubxld6GrFGximxfMsMB6BpJhpcTouAqywAFppiKetUBBbXwYsYU
1wNr648XVmPmCMCy4rY8vdliFnbMUj086DU6Z+/oXBdWU3/b1G0DN3E9wULRSwcK
ZT3wj/cCI1vsCm3gj2R5SqkA9Y0CAwEAAQKBgAJH+4CxV0/zBVcLiBCHvSANm0l7
HetybTh/j2p0Y1sTXro4ALwAaCTUeqdBjWiLSo9lNwDHFyq8zX90+gNxa7c5EqcW
V9FmlVXr8VhfBzcZo1nXeNdXFT7tQ2yah/odtdcx+vRMSGJd1t/5k5bDd9wAvYdI
DblMAg+wiKKZ5KcdAkEA1cCakEN4NexkF5tHPRrR6XOY/XHfkqXxEhMqmNbB9U34
saTJnLWIHC8IXys6Qmzz30TtzCjuOqKRRy+FMM4TdwJBAJQZFPjsGC+RqcG5UvVM
iMPhnwe/bXEehShK86yJK/g/UiKrO87h3aEu5gcJqBygTq3BBBoH2md3pr/W+hUM
WBsCQQChfhTIrdDinKi6lRxrdBnn0Ohjg2cwuqK5zzU9p/N+S9x7Ck8wUI53DKm8
jUJE8WAG7WLj/oCOWEh+ic6NIwTdAkEAj0X8nhx6AXsgCYRql1klbqtVmL8+95KZ
K7PnLWG/IfjQUy3pPGoSaZ7fdquG8bq8oyf5+dzjE/oTXcByS+6XRQJAP/5ciy1b
L3NhUhsaOVy55MHXnPjdcTX0FaLi+ybXZIfIQ2P4rb19mVq1feMbCXhz+L1rG8oa
t5lYKfpe8k83ZA==
-----END RSA PRIVATE KEY-----"""

        self.DEVICE_OLD_KEY = "aLFBMWpxBrIDAD1Si/KVvm41"
        # 兜底固定token 沿用你的
        self.FALLBACK_TOKEN = '024212ef0975c5306a1434e113a46463.bc77313e11a248558a6ca244ca980944ec3421fa480c50e0229ad91f1cb15aea582603202cd71796885c9e5163e500f1b72f737059aff1ddb8beea47c5a331d6760540345b7f88b2302a0e6e09589f9dcf3ff9175d8c905f990203f5fc04748008ea7a366571cbf5b09509a873dcfba3cf1d5590385f5fef6e01d1850974aa220eb5178c89e61c24411af9b9a19435e.06fde789ece48d9b33c5dc857e04e9b5838f08264d928b87237d3476c4484b46'

        # 随机设备参数
        self.deviceId = str(864150060000000 + random.randint(0, 9999))
        self.deviceKey = ''.join(random.choices('0123456789ABCDEF', k=40))
        self.token = ""
        self.token_id = ""
        self.registered = False

        self.header = {
            'User-Agent': 'Lavf/57.83.100',
            'code': 'GZ0369',
            'deviceId': self.deviceId,
            'lang': 'zh_cn',
            'Cache-Control': 'no-cache',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Version': '2604028',
            'PackageName': 'com.ae06aebdbb.y286327f5a.ofe849883320260517',
            'Ver': '3.0.3.2',
            'api-ver': '3.0.3.2',
            'Referer': self.host
        }

        self.cache = {}
        self.cache_timeout = 300

        # 【借鉴对方稳定方案】构造函数提前初始化token，加载源前完成认证
        try:
            self.init_token()
        except Exception as e:
            print("初始化失败，启用兜底token:", e)
            self.token = self.FALLBACK_TOKEN

    def getName(self):
        return self.name

    # init置空，和对方保持一致，避免二次重复初始化冲突
    def init(self, extend=''):
        pass

    # 设备认证逻辑 完全沿用你的代码
    def init_token(self):
        print("===== 初始化设备认证 =====")
        if not self.registered:
            self.sign_up()
        self.refresh_token()

    def sign_up(self):
        print("注册新设备...")
        params = {
            "new_key": self.deviceKey,
            "old_key": self.DEVICE_OLD_KEY,
            "phone_type": 1,
            "code": ""
        }
        result = self._auth_request('/App/Authentication/Device/signUp', params)
        self._apply_auth(result)
        self.registered = True

    def sign_in(self):
        print("设备登录...")
        params = {
            "new_key": self.deviceKey,
            "old_key": self.DEVICE_OLD_KEY
        }
        result = self._auth_request('/App/Authentication/Device/signIn', params)
        self._apply_auth(result)

    def _apply_auth(self, result):
        new_token = result.get('token', '')
        if not new_token:
            raise Exception("认证失败，无token返回")
        self.token = new_token
        self.token_id = result.get('app_user_id', '')
        print(f"token获取成功，前缀：{self.token[:30]}...")

    def refresh_token(self):
        print("刷新token...")
        result = self._auth_request('/App/Authentication/Authenticator/refresh', {})
        self._apply_auth(result)

    def _auth_request(self, path, params):
        return self._send_encrypted_request(params, path, is_auth=True)

    def ensure_token(self):
        if not self.token or not self.token_id:
            if self.registered:
                self.sign_in()
            else:
                self.sign_up()
            self.refresh_token()

    def _send_encrypted_request(self, data, path, is_auth=False):
        try:
            if not is_auth:
                self.ensure_token()

            json_params = json.dumps(data)
            request_key = self.aes_encrypt(json_params, self.AES_KEY, self.AES_IV).upper()
            key_json = json.dumps({"iv": self.AES_IV, "key": self.AES_KEY})
            keys = self.rsa_encrypt(key_json, self.RSA_PUBLIC_KEY)

            t = str(int(time.time()))
            sign_str = f"token_id=,token={self.token},phone_type=1,request_key={request_key},app_id=1,time={t},keys={keys}*&zvdvdvddbfikkkumtmdwqppp?|4Y!s!2br"
            signature = self.get_md5(sign_str)

            body = {
                'token': self.token,
                'token_id': '',
                'phone_type': '1',
                'time': t,
                'phone_model': 'xiaomi-25031',
                'keys': keys,
                'request_key': request_key,
                'signature': signature,
                'app_id': '1',
                'ad_version': '1'
            }

            url = f"{self.host}{path}"
            # 借鉴对方10s超时，提升弱网兼容性
            response = self.post(url, headers=self.header, data=body, timeout=10)
            if response.status_code != 200:
                raise Exception(f"HTTP异常 {response.status_code}")

            resp_json = response.json()
            if resp_json.get("code", 200) != 200:
                print("业务错误码：", resp_json['code'])
                raise Exception("接口业务报错")

            data_section = resp_json.get("data")
            if not data_section:
                raise Exception("无返回data")

            resp_key = data_section.get("response_key")
            enc_keys = data_section.get("keys")
            key_info = json.loads(self.rsa_decrypt(enc_keys, self.RSA_PRIVATE_KEY))
            dec_data = self.aes_decrypt(resp_key, key_info['key'], key_info['iv'])
            return json.loads(dec_data)
        except Exception as e:
            print(f"路径{path}请求失败：{e}")
            return None

    def get_data(self, data, path, use_cache=True):
        try:
            cache_key = f"{path}_{hash(str(data))}" if use_cache else None
            if use_cache and cache_key in self.cache:
                cache_data, ts = self.cache[cache_key]
                if time.time() - ts < self.cache_timeout:
                    return cache_data

            # 借鉴对方3轮全局重试，多域名轮询
            for attempt in range(3):
                tried = 0
                while tried < len(self.hosts):
                    self.host = self.hosts[self.host_index]
                    self.header["Referer"] = self.host
                    res = self._send_encrypted_request(data, path)
                    if res is not None:
                        print(f"请求成功，域名：{self.host}")
                        if use_cache and cache_key:
                            self.cache[cache_key] = (res, time.time())
                        return res
                    self.host_index = (self.host_index + 1) % len(self.hosts)
                    tried += 1
                # 全部域名失效，重新认证重试
                if attempt < 2:
                    print("域名全部失效，重新认证")
                    try:
                        self.ensure_token()
                    except:
                        self.token = self.FALLBACK_TOKEN
                    self.host_index = 0
            return None
        except Exception as e:
            print("get_data异常：", e)
            return None

    # 加解密工具 完全沿用你的原版
    def aes_encrypt(self, text, key, iv):
        try:
            cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
            return cipher.encrypt(pad(text.encode(), AES.block_size)).hex().upper()
        except Exception as e:
            print("AES加密失败：", e)
            return ""

    def aes_decrypt(self, text, key, iv):
        try:
            cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
            return unpad(cipher.decrypt(bytes.fromhex(text)), AES.block_size).decode()
        except Exception as e:
            print("AES解密失败：", e)
            return ""

    def rsa_encrypt(self, text, pub_key):
        try:
            key = RSA.import_key(f"-----BEGIN PUBLIC KEY-----\n{pub_key}\n-----END PUBLIC KEY-----")
            return base64.b64encode(PKCS1_v1_5.new(key).encrypt(text.encode())).decode()
        except Exception as e:
            print("RSA加密失败：", e)
            return ""

    def rsa_decrypt(self, text, pri_key):
        try:
            key = RSA.import_key(pri_key)
            res = PKCS1_v1_5.new(key).decrypt(base64.b64decode(text), None)
            return res.decode() if res else ""
        except Exception as e:
            print("RSA解密失败：", e)
            return ""

    def get_md5(self, text):
        return hashlib.md5(text.encode()).hexdigest().upper()

    # 页面接口 一字不动保留你的代码
    def homeContent(self, filter):
        classes = [
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "动漫", "type_id": "4"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "短剧", "type_id": "64"}
        ]
        filters = {}
        for c in classes:
            tid = c['type_id']
            filters[tid] = [
                {"key": "area", "name": "地区", "value": [
                    {"n": "全部", "v": "0"}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"},
                    {"n": "台湾", "v": "台湾"}, {"n": "美国", "v": "美国"}, {"n": "韩国", "v": "韩国"},
                    {"n": "日本", "v": "日本"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"},
                    {"n": "泰国", "v": "泰国"}, {"n": "印度", "v": "印度"}, {"n": "其他", "v": "其他"}
                ]},
                {"key": "year", "name": "年份", "value": [
                    {"n": "全部", "v": "0"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"},
                    {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"},
                    {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"},
                    {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"},
                    {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009", "v": "2009"},
                    {"n": "2008", "v": "2008"}, {"n": "2007", "v": "2007"}, {"n": "2006", "v": "2006"},
                    {"n": "2005", "v": "2005"}, {"n": "更早", "v": "2004"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"n": "最新", "v": "d_id"}, {"n": "最热", "v": "d_hits"}, {"n": "推荐", "v": "d_score"}
                ]}
            ]
        return {"class": classes, "filters": filters}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        videos = []
        try:
            body = {
                "area": extend.get('area', '0'),
                "year": extend.get('year', '0'),
                "pageSize": "30",
                "sort": extend.get('sort', 'd_id'),
                "page": str(pg),
                "tid": tid
            }
            cache_key = f"category_{tid}_{pg}_{hash(str(body))}"
            data = self.get_cached_data(cache_key, body, '/App/IndexList/indexList')
            if data and 'list' in data:
                for item in data['list']:
                    cont = item.get('vod_continu', 0)
                    tip = '电影' if cont == 0 else f'更新至{cont}集'
                    videos.append({
                        "vod_id": f"{item.get('vod_id', '')}/{cont}",
                        "vod_name": item.get('vod_name', ''),
                        "vod_pic": item.get('vod_pic', ''),
                        "vod_remarks": tip
                    })
        except Exception as e:
            print("分类加载失败：", e)
        return {'list': videos, 'page': int(pg), 'pagecount': 9999, 'limit': 30, 'total': 999999}

    def detailContent(self, ids):
        try:
            vid = ids[0].split('/')[0]
            t = str(int(time.time()))
            info_data = self.get_data({"token_id": self.token_id, "vod_id": vid, "mobile_time": t, "token": self.token}, '/App/IndexPlay/playInfo')
            source_data = self.get_data({"vurl_cloud_id": "2", "vod_d_id": vid}, '/App/Resource/Vurl/show')
            if not info_data or 'vodInfo' not in info_data:
                return {'list': []}
            vod = info_data['vodInfo']
            detail = {
                "vod_id": vid,
                "vod_name": vod.get('vod_name', ''),
                "vod_pic": vod.get('vod_pic', ''),
                "vod_year": vod.get('vod_year', ''),
                "vod_area": vod.get('vod_area', ''),
                "vod_actor": vod.get('vod_actor', ''),
                "vod_director": vod.get('vod_director', ''),
                "vod_content": vod.get('vod_use_content', '').strip(),
                "vod_play_from": "瓜子影视"
            }
            play_list = []
            if source_data and 'list' in source_data:
                for idx, item in enumerate(source_data['list']):
                    if 'play' in item:
                        n_list, p_list = [], []
                        for k, v in item['play'].items():
                            if 'param' in v and v['param']:
                                n_list.append(k)
                                p_list.append(v['param'])
                        if p_list:
                            name = str(idx + 1) if len(source_data['list']) != 1 else vod['vod_name']
                            play_list.append(f"{name}${p_list[-1]}||{'@'.join(n_list)}")
            detail["vod_play_url"] = "#".join(play_list)
            return {'list': [detail]}
        except Exception as e:
            print("详情加载失败：", e)
            return {'list': []}

    def searchContent(self, key, quick, pg=1):
        videos = []
        try:
            data = self.get_data({"keywords": key, "order_val": "1", "page": str(pg)}, '/App/Index/findMoreVod', use_cache=False)
            if data and 'list' in data:
                for item in data['list']:
                    cont = item.get('vod_continu', 0)
                    tip = '电影' if cont == 0 else f'更新至{cont}集'
                    videos.append({
                        "vod_id": f"{item.get('vod_id', '')}/{cont}",
                        "vod_name": item.get('vod_name', ''),
                        "vod_pic": item.get('vod_pic', ''),
                        "vod_remarks": tip
                    })
        except Exception as e:
            print("搜索失败：", e)
        return {'list': videos, 'page': int(pg), 'pagecount': 9999, 'limit': 30, 'total': 999999}

    def playerContent(self, flag, vid, vipFlags):
        try:
            parts = vid.split('||')
            if len(parts) < 2:
                return {"parse": 0, "playUrl": "", "url": ""}
            params = {}
            for seg in parts[0].split('&'):
                if '=' in seg:
                    k, v = seg.split('=', 1)
                    params[k] = v
            res_list = parts[1].split('@')
            if res_list:
                res_list.sort(key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
                params['resolution'] = res_list[0]
                play_data = self.get_data(params, '/App/Resource/VurlDetail/showOne', use_cache=False)
                if play_data and 'url' in play_data:
                    return {
                        "parse": 0,
                        "playUrl": "",
                        "url": play_data['url'],
                        "header": json.dumps({"User-Agent": "Lavf/57.83.100", "Referer": "http://WJiZxLXA2.com/"}),
                        "danmaku": "http://127.0.0.1:9978/proxy?do=diydanmu"
                    }
            return {"parse": 0, "playUrl": "", "url": ""}
        except Exception as e:
            print("播放解析失败：", e)
            return {"parse": 0, "playUrl": "", "url": ""}

    # 修复闪退关键点：固定返回False，摒弃pass
    def manualVideoCheck(self):
        return False

    def localProxy(self, params):
        return None

    def get_cached_data(self, ck, data, path):
        now = time.time()
        if ck in self.cache:
            d, t = self.cache[ck]
            if now - t < self.cache_timeout:
                return d
        res = self.get_data(data, path)
        if res:
            self.cache[ck] = (res, now)
        return res

if __name__ == '__main__':
    pass

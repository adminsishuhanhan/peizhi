# coding=utf-8
import json
import time
import base64
import hashlib
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = "瓜子"
        # 仅保留https域名，彻底舍弃http明文（安卓9禁用http）
        self.hosts = [
            "https://apinew.uozvr.com",
            "https://api.w32z7vtd.com",
            "https://api.6a7nnf7.com",
            "https://api.umygrx3.com",
            "https://api.rmedphk.com"
        ]
        self.host_idx = 0
        self.host = self.hosts[0]

        self.AES_KEY = 'OITxa5OqAYjhswxx'
        self.AES_IV = 'rCMNwZASNBKZ8mXV'
        self.PUB_KEY = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDUM5+/y8sPsWkd1/RQS64X259EUwxFXFE5HlA65MqrxnPs0JqoSRojSDy5QhwvROlaD6TwRQHKMY2OAZ6SnQeUJsChTEFIR9qUkwrs3/MVUMxjsv6JS6Oe/juclyJGTgVmDhB55EafXsD0SQYVj/QXXsxR6ewR5E2kL52yAAD4yQIDAQAB"
        self.PRI_KEY = """-----BEGIN RSA PRIVATE KEY-----
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

        # 永久固定静态token，全程不联网鉴权，彻底消除初始化等待
        self.token = "024212ef0975c5306a1434e113a46463.bc77313e11a248558a6ca244ca980944ec3421fa480c50e0229ad91f1cb15aea582603202cd71796885c9e5163e500f1b72f737059aff1ddb8beea47c5a331d6760540345b7f88b2302a0e6e09589f9dcf3ff9175d8c905f990203f5fc04748008ea7a366571cbf5b09509a873dcfba3cf1d5590385f5fef6e01d1850974aa220eb5178c89e61c24411af9b9a19435e.06fde789ece48d9b33c5dc857e04e9b5838f08264d928b87237d3476c4484b46"
        self.token_id = ""
        self.deviceId = str(864150060000000 + random.randint(0, 9999))
        self.cache = {}
        self.cache_time = 240
        # 全局请求头固定
        self.headers = {
            "User-Agent": "Lavf/57.83.100",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache",
            "deviceId": self.deviceId
        }

    def getName(self):
        return self.name

    def init(self, extend=""):
        # 空初始化，无任何联网，打开直接加载
        pass

    def aes_en(self, text):
        try:
            aes = AES.new(self.AES_KEY.encode(), AES.MODE_CBC, self.AES_IV.encode())
            return aes.encrypt(pad(text.encode(), AES.block_size)).hex().upper()
        except:
            return ""

    def aes_de(self, hex_str):
        try:
            aes = AES.new(self.AES_KEY.encode(), AES.MODE_CBC, self.AES_IV.encode())
            return unpad(aes.decrypt(bytes.fromhex(hex_str)), AES.block_size).decode()
        except:
            return ""

    def rsa_en(self, text):
        try:
            pub = RSA.import_key(f"-----BEGIN PUBLIC KEY-----\n{self.PUB_KEY}\n-----END PUBLIC KEY-----")
            return base64.b64encode(PKCS1_v1_5.new(pub).encrypt(text.encode())).decode()
        except:
            return ""

    def rsa_de(self, b64_str):
        try:
            pri = RSA.import_key(self.PRI_KEY)
            raw = PKCS1_v1_5.new(pri).decrypt(base64.b64decode(b64_str), None)
            return raw.decode() if raw else ""
        except:
            return ""

    def md5(self, s):
        return hashlib.md5(s.encode()).hexdigest().upper()

    def req(self, path, data):
        try:
            js_data = json.dumps(data)
            req_key = self.aes_en(js_data)
            key_js = json.dumps({"key": self.AES_KEY, "iv": self.AES_IV})
            rsa_key = self.rsa_en(key_js)
            ts = str(int(time.time()))
            sign_raw = f"token_id=,token={self.token},phone_type=1,request_key={req_key},app_id=1,time={ts},keys={rsa_key}"
            sign = self.md5(sign_raw)
            post_data = {
                "token": self.token,
                "token_id": "",
                "phone_type": "1",
                "time": ts,
                "phone_model": "android9",
                "keys": rsa_key,
                "request_key": req_key,
                "signature": sign,
                "app_id": "1"
            }
            url = f"{self.host}{path}"
            # 严格超时4秒，超时立刻换下一个域名
            resp = self.post(url, headers=self.headers, data=post_data, timeout=4)
            if resp.status_code != 200:
                return None
            res_json = resp.json()
            if res_json.get("code", 200) != 200:
                return None
            body = res_json.get("data")
            if not body:
                return None
            dec_key = self.rsa_de(body.get("keys", ""))
            dec_body = self.aes_de(body.get("response_key", ""))
            return json.loads(dec_body)
        except Exception:
            return None

    def get_data(self, path, data):
        cache_key = f"{path}{str(data)}"
        now = time.time()
        if cache_key in self.cache:
            val, t = self.cache[cache_key]
            if now - t < self.cache_time:
                return val
        # 最多遍历一轮域名，不无限循环
        for _ in range(len(self.hosts)):
            ret = self.req(path, data)
            if ret:
                self.cache[cache_key] = (ret, now)
                return ret
            self.host_idx = (self.host_idx + 1) % len(self.hosts)
            self.host = self.hosts[self.host_idx]
        return None

    def homeContent(self, filter):
        clz = [
            {"type_name": "电影", "type_id": "1"},
            {"type_name": "电视剧", "type_id": "2"},
            {"type_name": "动漫", "type_id": "4"},
            {"type_name": "综艺", "type_id": "3"},
            {"type_name": "短剧", "type_id": "64"}
        ]
        filters = {}
        for item in clz:
            tid = item["type_id"]
            filters[tid] = [
                {"key": "area", "name": "地区", "value": [
                    {"n": "全部", "v": "0"}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"},
                    {"n": "台湾", "v": "台湾"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}
                ]},
                {"key": "year", "name": "年份", "value": [
                    {"n": "全部", "v": "0"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"},
                    {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}
                ]},
                {"key": "sort", "name": "排序", "value": [
                    {"n": "最新", "v": "d_id"}, {"n": "最热", "v": "d_hits"}, {"n": "推荐", "v": "d_score"}
                ]}
            ]
        return {"class": clz, "filters": filters}

    def homeVideoContent(self):
        return {"list": []}

    def categoryContent(self, tid, pg, filter, extend):
        res_list = []
        param = {
            "tid": tid,
            "page": str(pg),
            "pageSize": "30",
            "area": extend.get("area", "0"),
            "year": extend.get("year", "0"),
            "sort": extend.get("sort", "d_id")
        }
        data = self.get_data("/App/IndexList/indexList", param)
        if data and "list" in data:
            for vod in data["list"]:
                cont = vod.get("vod_continu", 0)
                tip = "正片" if cont == 0 else f"更新{cont}集"
                res_list.append({
                    "vod_id": f'{vod["vod_id"]}/{cont}',
                    "vod_name": vod["vod_name"],
                    "vod_pic": vod["vod_pic"],
                    "vod_remarks": tip
                })
        return {"list": res_list, "page": pg, "pagecount": 999, "limit": 30, "total": 99999}

    def detailContent(self, ids):
        vid = ids[0].split("/")[0]
        info = self.get_data("/App/IndexPlay/playInfo", {"vod_id": vid, "token": self.token})
        play_src = self.get_data("/App/Resource/Vurl/show", {"vod_d_id": vid, "vurl_cloud_id": "2"})
        if not info or "vodInfo" not in info:
            return {"list": []}
        info = info["vodInfo"]
        detail = {
            "vod_id": vid,
            "vod_name": info["vod_name"],
            "vod_pic": info["vod_pic"],
            "vod_year": info["vod_year"],
            "vod_area": info["vod_area"],
            "vod_actor": info["vod_actor"],
            "vod_director": info["vod_director"],
            "vod_content": info.get("vod_use_content", ""),
            "vod_play_from": "瓜子"
        }
        play_urls = []
        if play_src and "list" in play_src:
            for idx, src in enumerate(play_src["list"]):
                play = src.get("play", {})
                names = []
                links = []
                for k, v in play.items():
                    if v.get("param"):
                        names.append(k)
                        links.append(v["param"])
                if links:
                    name = str(idx+1) if len(play_src["list"]) > 1 else info["vod_name"]
                    play_urls.append(f"{name}${links[-1]}||{'@'.join(names)}")
        detail["vod_play_url"] = "#".join(play_urls)
        return {"list": [detail]}

    def searchContent(self, key, quick, pg=1):
        res_list = []
        data = self.get_data("/App/Index/findMoreVod", {"keywords": key, "page": str(pg)})
        if data and "list" in data:
            for vod in data["list"]:
                cont = vod.get("vod_continu", 0)
                tip = "电影" if cont == 0 else f"{cont}集"
                res_list.append({
                    "vod_id": f'{vod["vod_id"]}/{cont}',
                    "vod_name": vod["vod_name"],
                    "vod_pic": vod["vod_pic"],
                    "vod_remarks": tip
                })
        return {"list": res_list, "page": pg, "pagecount": 999, "limit": 30, "total": 99999}

    def playerContent(self, flag, vid, vipFlags):
        try:
            part = vid.split("||")
            if len(part) < 2:
                return {"parse": 0, "url": "", "playUrl": ""}
            params = {}
            for seg in part[0].split("&"):
                if "=" in seg:
                    k, v = seg.split("=", 1)
                    params[k] = v
            res_arr = part[1].split("@")
            if res_arr:
                params["resolution"] = res_arr[0]
                play_data = self.get_data("/App/Resource/VurlDetail/showOne", params)
                if play_data and "url" in play_data:
                    return {
                        "parse": 0,
                        "url": play_data["url"],
                        "playUrl": "",
                        "header": json.dumps({"User-Agent": "Lavf/57.83.100"})
                    }
            return {"parse": 0, "url": "", "playUrl": ""}
        except:
            return {"parse": 0, "url": "", "playUrl": ""}

    def manualVideoCheck(self):
        return False

    def localProxy(self, params):
        return None

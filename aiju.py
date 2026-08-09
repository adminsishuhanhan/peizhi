# -*- coding: utf-8 -*-
# 本资源来源于互联网公开渠道，仅可用于个人学习及爬虫技术交流。
# 本脚本仅用于爬虫学习交流，禁止商用，24小时内自行删除
import re
import sys
import uuid
from base.spider import Spider
sys.path.append('..')

class Spider(Spider):
    host = ''
    config = ''
    local_uuid = ''
    parsing_config = {}
    base_header = {
        'User-Agent': "Dart/2.19 (dart:io)",
        'Accept-Encoding': "gzip"
    }

    # 统一实时生成合法请求头，双内核通用
    def get_header(self):
        h = self.base_header.copy()
        h['appto-local-uuid'] = self.local_uuid
        return h

    def init(self, extend=''):
        try:
            host_raw = extend.strip()
            if not host_raw.startswith('http'):
                return {}
            # 域名解析
            if not re.match(r'^https?://[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(:\d+)?/?$', host_raw):
                res = self.fetch(host_raw, headers=self.get_header()).json()
                self.host = res['domain']
            else:
                self.host = host_raw
            # 生成随机设备标识
            self.local_uuid = str(uuid.uuid4())
            # 拉取后端全局配置
            cfg_resp = self.fetch(f'{self.host}/apptov5/v1/config/get?p=android&__platform=android', headers=self.get_header()).json()
            self.config = cfg_resp['data']
            # 整理解析线路
            parse_list = self.config['get_parsing']['lists']
            temp_parse = {}
            for item in parse_list:
                cfg_list = item['config']
                label_arr = []
                for cfg in cfg_list:
                    if cfg['type'] == 'json':
                        label_arr.append(cfg['label'])
                temp_parse[item['key']] = label_arr
            self.parsing_config = temp_parse
            return None
        except Exception as e:
            print("初始化异常：", e)
            return {}

    def detailContent(self, ids):
        resp = self.fetch(f"{self.host}/apptov5/v1/vod/getVod?id={ids[0]}", headers=self.get_header()).json()
        data = resp['data']
        vod_list = []
        play_from = ''
        play_url = ''
        for pl in data['vod_play_list']:
            temp_url = ''
            for url_item in pl['urls']:
                temp_url += f"{url_item['name']}${pl['player_info']['from']}@{url_item['url']}#"
            play_from += pl['player_info']['show'] + '$$$'
            play_url += temp_url.rstrip('#') + '$$$'
        play_from = play_from.rstrip('$$$')
        play_url = play_url.rstrip('$$$')
        vod_list.append({
            'vod_id': data.get('vod_id'),
            'vod_name': data.get('vod_name'),
            'vod_content': data.get('vod_content'),
            'vod_remarks': data.get('vod_remarks'),
            'vod_director': data.get('vod_director'),
            'vod_actor': data.get('vod_actor'),
            'vod_year': data.get('vod_year'),
            'vod_area': data.get('vod_area'),
            'vod_play_from': play_from,
            'vod_play_url': play_url
        })
        return {'list': vod_list}

    def searchContent(self, key, quick, pg='1'):
        url = f"{self.host}/apptov5/v1/search/lists?wd={key}&page={pg}&type=&__platform=android"
        resp = self.fetch(url, headers=self.get_header()).json()
        data_arr = resp['data']['data']
        for item in data_arr:
            pic = item.get('vod_pic', '')
            if pic.startswith('mac://'):
                item['vod_pic'] = pic.replace('mac://', 'http://', 1)
        return {
            'list': data_arr,
            'page': pg,
            'total': resp['data']['total']
        }

    def playerContent(self, flag, id, vipflags):
        default_ua = 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
        parts = id.split('@')
        if len(parts) != 2:
            return {'parse': 0, 'url': id, 'header': {'User-Agent': default_ua}}
        play_key, raw_url = parts
        label_list = self.parsing_config.get(play_key, [])
        if not label_list:
            return {'parse': 0, 'url': raw_url, 'header': {'User-Agent': default_ua}}
        result = {'parse': 1, 'url': raw_url, 'header': {'User-Agent': default_ua}}
        for label in label_list:
            post_data = {'play_url': raw_url, 'label': label, 'key': play_key}
            try:
                res = self.post(f"{self.host}/apptov5/v1/parsing/proxy?__platform=android", data=post_data, headers=self.get_header()).json()
            except Exception:
                continue
            if not isinstance(res, dict) or res.get('code') == 422:
                continue
            parse_data = res.get('data')
            if not isinstance(parse_data, dict):
                continue
            final_url = parse_data.get('url')
            if final_url:
                ua = parse_data.get('UA') or parse_data.get('UserAgent') or default_ua
                result = {'parse': 0, 'url': final_url, 'header': {'User-Agent': ua}}
                break
        return result

    def homeContent(self, filter):
        if not self.config:
            return {}
        cate_list = self.config['get_home_cate']
        class_arr = []
        for item in cate_list:
            if isinstance(item.get('extend', []), dict):
                class_arr.append({'type_id': item['cate'], 'type_name': item['title']})
        return {'class': class_arr}

    def homeVideoContent(self):
        resp = self.fetch(f'{self.host}/apptov5/v1/home/data?id=1&mold=1&__platform=android', headers=self.get_header()).json()
        data = resp['data']
        vod_arr = []
        for section in data['sections']:
            for item in section['items']:
                pic = item.get('vod_pic', '')
                if pic.startswith('mac://'):
                    pic = pic.replace('mac://', 'http://', 1)
                vod_arr.append({
                    "vod_id": item.get('vod_id'),
                    "vod_name": item.get('vod_name'),
                    "vod_pic": pic,
                    "vod_remarks": item.get('vod_remarks')
                })
        return {'list': vod_arr}

    def categoryContent(self, tid, pg, filter, extend):
        url = (f"{self.host}/apptov5/v1/vod/lists?area={extend.get('area','')}&lang={extend.get('lang','')}"
               f"&year={extend.get('year','')}&order={extend.get('sort','time')}&type_id={tid}"
               f"&type_name=&page={pg}&pageSize=21&__platform=android")
        resp = self.fetch(url, headers=self.get_header()).json()
        data = resp['data']
        list_data = data['data']
        for item in list_data:
            pic = item.get('vod_pic', '')
            if pic.startswith('mac://'):
                item['vod_pic'] = pic.replace('mac://', 'http://', 1)
        return {
            'list': list_data,
            'page': pg,
            'total': data['total']
        }

    # 补齐空函数，彻底杜绝闪退
    def getName(self):
        return ""
    def isVideoFormat(self, url):
        return False
    def manualVideoCheck(self):
        return False
    def destroy(self):
        pass
    def localProxy(self, param):
        return None

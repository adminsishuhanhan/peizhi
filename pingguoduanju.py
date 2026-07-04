from base.spider import Spider
import requests
import re
import urllib.parse

host = "https://mov.cenguigui.cn"
base_url = host + "/duanju/api.php"
quality_host = "https://mov.cenguigui.cn"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
}
timeout = 10

class Spider(Spider):
    def getName(self):
        return "小心儿悠悠"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        # 精简分类，删除重复、冗余分类，避免超长字符串卡死APP
        class_names = "推荐榜&热播榜&新剧榜&逆袭&霸总&豪门恩怨&神豪&都市日常&大女主&重生&闪婚&赘婿逆袭&萌宝&奇幻爱情&乡村&历史古代&娱乐圈&系统&玄幻仙侠&悬疑推理"
        class_list = class_names.split('&')
        classes = []
        for class_name in class_list:
            classes.append({
                "type_id": class_name,
                "type_name": class_name
            })
        return {"class": classes}

    def homeVideoContent(self):
        return {'list': []}

    def categoryContent(self, cid, pg, filter, ext):
        videos = []
        page = int(pg) if pg else 1
        params = f"page={page}&name={urllib.parse.quote(cid)}"
        tab_type = "19"
        if ext and 'tab_type' in ext:
            tab_type = ext['tab_type']
        params += f"&tab_type={tab_type}"
        url = f"{base_url}?{params}"
        try:
            response = requests.get(url=url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                return {'list': []}
            response.encoding = "utf-8"
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                for vod in data['data']:
                    vod_id = f"book_id={vod.get('book_id', '')}&actor={vod.get('author', '')}&type={vod.get('type', '')}"
                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": vod.get('title', ''),
                        "vod_pic": vod.get('cover', ''),
                        "vod_remarks": vod.get('type', ''),
                        "vod_content": vod.get('intro', '')
                    })
        except Exception:
            return {'list': []}
        # 缩小分页数值，防止APP渲染卡顿
        return {
            'list': videos,
            'page': pg,
            'pagecount': 100,
            'limit': 20,
            'total': 2000
        }

    def detailContent(self, ids):
        did = ids[0]
        params = {}
        if '?' in did:
            queryString = did.split('?')[1]
            pairs = queryString.split('&')
            for pair in pairs:
                kv = pair.split('=',1)
                if len(kv) == 2:
                    params[kv[0]] = kv[1]
        book_id = params.get('book_id', '')
        actor = params.get('actor', '')
        fullType = params.get('type', '')
        if not book_id:
            match = re.search(r'book_id=([^&]*)', did)
            if match:
                book_id = match.group(1)
        if not book_id:
            return {'list': []}
        apiUrl = f"{base_url}?book_id={book_id}"
        try:
            response = requests.get(url=apiUrl, headers=headers, timeout=timeout)
            if response.status_code != 200:
                return {'list': []}
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                vod_list = data['data']
                play_from = []
                play_url = []
                quality_options = [("超清", "2160p"),("高清", "1080p"),("标清", "720p")]
                for quality_name, quality_value in quality_options:
                    urls = []
                    for item in vod_list:
                        chapterName = item.get('title', '')
                        videoId = item.get('video_id', '')
                        playUrl = f"{quality_host}/duanju/api.php?video_id={videoId}&type=json&level={quality_value}"
                        urls.append(f"{chapterName}${playUrl}")
                    play_from.append(quality_name)
                    play_url.append("#".join(urls))
                # 演员接口异常兜底，不中断整个详情返回
                actors = []
                try:
                    actor_api_url = f"{base_url}?series_id={book_id}&showRawParams=false"
                    actor_response = requests.get(url=actor_api_url, headers=headers, timeout=5)
                    if actor_response.status_code == 200:
                        actor_data = actor_response.json()
                        if actor_data.get('code') == 200 and 'celebrities' in actor_data:
                            celebrities = actor_data['celebrities']
                            if isinstance(celebrities, list):
                                for celeb in celebrities:
                                    actor_name = celeb.get('user_name') or celeb.get('name') or ''
                                    if actor_name.strip() and actor_name not in actors:
                                        actors.append(actor_name)
                except Exception:
                    # 演员接口失败直接用传过来的actor，不阻断逻辑
                    if actor:
                        actors = [actor]
                actor_str = ", ".join(actors) if actors else actor
                categories = []
                if 'category_names' in data and isinstance(data['category_names'], list):
                    categories = data['category_names'][:2]
                elif 'category' in data:
                    categories = [data['category']]
                type_str = ", ".join(categories) if categories else fullType
                remarks_str = f"共{len(vod_list)}集"
                content_str = data.get('desc', '')
                VOD = {
                    "vod_id": did,
                    "vod_name": data.get('book_name', ''),
                    "vod_pic": data.get('book_pic', ''),
                    "vod_actor": actor_str,
                    "type_name": type_str,
                    "vod_remarks": remarks_str,
                    "vod_content": content_str,
                    "vod_play_from": "$$$".join(play_from),
                    "vod_play_url": "$$$".join(play_url)
                }
                return {'list': [VOD]}
        except Exception:
            return {'list': []}
        return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        max_retries = 2
        for i in range(max_retries):
            try:
                response = requests.get(url=id, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 200 and data.get('data'):
                        play_url = data['data'].get('url', '')
                        if play_url:
                            return {
                                "parse": 0,
                                "playUrl": '',
                                "url": play_url,
                                "header": headers
                            }
            except Exception:
                continue
        return {
            "parse": 0,
            "playUrl": '',
            "url": 'about:blank',
            "header": headers
        }

    def searchContent(self, key, quick, pg=1):
        try:
            page = int(pg)
        except:
            page = 1
        params = f"page={page}&name={urllib.parse.quote(key)}&tab_type=19"
        search_url = f"{base_url}?{params}"
        try:
            response = requests.get(search_url, headers=headers, timeout=timeout)
            if response.status_code != 200:
                return {'list': []}
            response.encoding = "utf-8"
            data = response.json()
            if data.get('code') != 200 or not data.get('data'):
                return {'list': []}
            videos = []
            for vod in data['data']:
                vod_id = f"book_id={vod.get('book_id', '')}&actor={vod.get('author', '')}&type={vod.get('type', '')}"
                videos.append({
                    "vod_id": vod_id,
                    "vod_name": vod.get('title', ''),
                    "vod_pic": vod.get('cover', ''),
                    "vod_remarks": vod.get('type', ''),
                    "vod_content": vod.get('intro', '')
                })
            return {
                'list': videos,
                'page': page,
                'pagecount': 100,
                'limit': len(videos),
                'total': 2000
            }
        except Exception:
            return {'list': []}

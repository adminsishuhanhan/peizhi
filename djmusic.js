var rule = {
    title: 'DJ音乐网',
    host: 'https://www.dj.net',
    homeUrl: '/dj-class-84-1.html',
    searchUrl: '/search.php?mod=music&srchtxt=**&searchsubmit=yes',
    searchable: 2,
    quickSearch: 1,
    filterable: 0,
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'
    },
    timeout: 8000,

    // 分类列表（已确认的 ID，可自行补充）
    一级: async function () {
        return [
            { type_id: '13', type_name: '慢摇串烧' },
            { type_id: '80', type_name: '酒吧串烧' },
            { type_id: '82', type_name: '专业串烧' },
            { type_id: '5',  type_name: '歌曲连版' },
            { type_id: '17', type_name: '外文单曲' },
            { type_id: '84', type_name: '中文单曲' },
            { type_id: '85', type_name: 'Electro' },
            { type_id: '86', type_name: 'House' },
            { type_id: '87', type_name: 'Deep' },
            { type_id: '88', type_name: 'Breakbeat' },
            { type_id: '89', type_name: 'Club' },
            { type_id: '90', type_name: 'EDM' },
            { type_id: '91', type_name: 'Mashup' },
            { type_id: '92', type_name: 'Rab' },
            { type_id: '93', type_name: 'Funky' },
            { type_id: '94', type_name: '流行音乐' }
        ];
    },

    // 分类内容
    二级: async function (tid, pg, filter, ext) {
        let url = rule.host + '/dj-class-' + tid + '-' + pg + '.html';
        let html = await request(url);
        return parseList(html);
    },

    // 搜索
    搜索: async function (wd, pg) {
        let url = rule.host + '/search.php?mod=music&srchtxt=' + encodeURIComponent(wd) + '&searchsubmit=yes';
        let html = await request(url);
        return parseList(html);
    },

    // 详情
    详情: async function (id) {
        return {
            vod_id: id,
            vod_name: '',
            vod_pic: '',
            vod_content: '',
            vod_play_from: 'DJ音乐',
            vod_play_url: '播放$' + id
        };
    },

    // 播放（核心）
    播放: async function (flag, id, flags) {
        let apiUrl = rule.host + '/template/zhzh_dzmusic/ajax/?action=geturl';
        let res = await post(apiUrl, { id: id });
        let json = JSON.parse(res);
        if (json.error !== '0' || !json.data || json.data.length === 0) {
            return '获取失败';
        }
        let d = json.data[0];
        return d.ser[0].u + d.src;
    }
};

// 通用列表解析
function parseList(html) {
    let items = [];
    let reg = /<a href="https:\/\/www\.dj\.net\/djplay\/music(\d+)\.html"[^>]*title="([^"]+)"/g;
    let m;
    while ((m = reg.exec(html)) !== null) {
        items.push({
            vod_id: m[1],
            vod_name: m[2],
            vod_pic: '',
            vod_remarks: ''
        });
    }
    return items;
}
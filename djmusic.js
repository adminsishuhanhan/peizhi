一级: async function () {
    return [
        { type_id: 'test', type_name: '测试分类' }
    ];
},

二级: async function (tid, pg, filter, ext) {
    if (tid === 'test') {
        return [{
            vod_id: '1',
            vod_name: '测试成功',
            vod_pic: '',
            vod_remarks: ''
        }];
    }
    // ...正常逻辑
}

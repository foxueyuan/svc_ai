# -*- coding: utf-8 -*-

import aiohttp
from sanic import response

async def unit(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_URL, token)

    payload = {'scene_id': data['scene_id'], 'query': data['text']}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('err_no') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['err_code'], 'errmsg': resp_json['err_msg']})

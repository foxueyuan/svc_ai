# -*- coding: utf-8 -*-

import aiohttp
from sanic import response


async def asr(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    if 'speech' in data:
        payload = {
            'format': 'pcm',
            'rate': 16000,
            'dev_pid': 1536,
            'channel': 1,
            'token': token,
            'cuid': 'foschool',
            'len': data['len'],
            'speech': data['speech']
        }
    else:
        payload = {
            'format': 'pcm',
            'rate': 16000,
            'dev_pid': 1536,
            'channel': 1,
            'token': token,
            'cuid': 'foschool',
            'url': data['url'],
            'callback': conf.SVC_CALLBACK_URL
        }

    async with aiohttp.ClientSession() as session:
        async with session.post(conf.SVC_ASR_URL, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('err_no') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'content': resp_json['result'][0]})
    else:
        return response.json({'errcode': resp_json['err_no'], 'errmsg': resp_json['err_msg']})

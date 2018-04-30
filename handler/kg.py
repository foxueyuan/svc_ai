# -*- coding: utf-8 -*-

import aiohttp
from sanic import response


async def entity_annotation(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    url = '{}?access_token={}'.format(conf.SVC_KG_ENTITY_ANNOTATION_URL, token)
    if 'text' in data and len(data['text']) < 64:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json={'data': data['text']}) as resp:
                resp_json = await resp.json()

        result['entity_annotation'] = resp_json['entity_annotation']
    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)

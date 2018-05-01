# -*- coding: utf-8 -*-

import aiohttp
from sanic import response


async def lexer(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    url = '{}?access_token={}'.format(conf.SVC_LEXER_URL, token)
    if 'text' in data:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                resp_json = await resp.json(encoding='gbk')

        result['text'] = resp_json['text']
        result['items'] = resp_json['items']

        result['segs'] = []
        for item in resp_json['items']:
            for word in item['basic_words']:
                result['segs'].append(word)
    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)


async def keyword(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    url = '{}?access_token={}'.format(conf.SVC_SIMNET_URL, token)
    if 'title' in data and 'content' in data:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                resp_json = await resp.json(encoding='gbk')

        result['items'] = resp_json['items']
    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)


async def simnet(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    url = '{}?access_token={}'.format(conf.SVC_SIMNET_URL, token)
    if 'text_1' in data and 'text_2' in data:
        payload = {'text_1': data['text_1'], 'text_2': data['text_2'], 'model': 'BOW'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                resp_json = await resp.json(encoding='gbk')

        result['text'] = {'text_1': data['text_1'], 'text_2': data['text_2']}
        result['score'] = resp_json['score']
    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)


async def spam(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    url = '{}?access_token={}'.format(conf.SVC_SPAM_URL, token)
    if 'text' in data:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data={'content': data['text']}) as resp:
                resp_json = await resp.json(encoding='gbk')

        result.update(resp_json.get('result', {'spam': 0}))

    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)

# -*- coding: utf-8 -*-

import aiohttp
import hashlib
import time
import uuid
from urllib.parse import urlencode
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
                resp_json = await resp.json()

        result.update(resp_json.get('result', {'spam': 0}))

    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)


async def gen_tencent_ai_nlp_req_dict(req_dict):
        app_id = '1106800137'
        app_key = 'YYcRW7I5J6L8RpQF'

        req_dict['app_id'] = app_id
        req_dict['time_stamp'] = int(time.time())
        req_dict['nonce_str'] = uuid.uuid1().hex

        sort_dict = sorted(req_dict.items(), key=lambda item: item[0], reverse=False)
        sort_dict.append(('app_key', app_key))
        sha = hashlib.md5()
        raw_text = urlencode(sort_dict).encode()
        sha.update(raw_text)
        md5text = sha.hexdigest().upper()

        req_dict['sign'] = md5text

        return req_dict


async def wordcom(request):
    conf = request.app.config
    data = request.json

    result = {'errcode': 0, 'errmsg': 'ok'}

    if 'text' in data:
        async with aiohttp.ClientSession() as session:
            async with session.post(conf.SVC_WORDCOM_URL, data=gen_tencent_ai_nlp_req_dict(data)) as resp:
                resp_json = await resp.json()

        result.update(resp_json.get('data', {}))

    else:
        result['errcode'] = 20001
        result['errmsg'] = '缺少text参数'

    return response.json(result)

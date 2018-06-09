# -*- coding: utf-8 -*-

import aiohttp
import uuid
from sanic import response


async def unit(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_URL, token)

    payload = {
        "bot_session": "",
        "log_id": uuid.uuid1().hex,
        "request": {
            "bernard_level": 0,
            "client_session": '{"client_results":"", "candidate_options":[]}',
            "query": data['text'],
            "query_info": {
                "asr_candidates": [],
                "source": "KEYBOARD",
                "type": "TEXT"
            },
            "user_id": "foai"
        },
        "bot_id": 1673,
        "version": "2.0"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})

# -*- coding: utf-8 -*-

import aiohttp
import uuid
from sanic import response
from aiohttp import FormData


async def unit_chat(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_CHAT_URL, token)

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
        "bot_id": conf.SVC_UNIT_BOT_ID,
        "version": "2.0"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_model_list(request):
    conf = request.app.config
    token = request.app.token

    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_LIST_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_model_train(request):
    conf = request.app.config
    token = request.app.token

    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_TRAIN_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "trainOption": {
            "configure": {
                "smartqu": "true",
                "mlqu": "true"
            },
            "data": {
                "querySetIds": [1, 2],
                "patternSetIds": [100]
            }
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_model_delete(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_DELETE_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "modelId": data['modelId']
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok'})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_list(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_LIST_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "pageNo": data.get('pageNo', 1),
        "pageSize": 50
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_info(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_INFO_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "faqId": data["faqId"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_add(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_ADD_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "faqQuestions": data["faqQuestions"],
        "faqAnswers": data["faqAnswers"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_update(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_UPDATE_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "faqId": data["faqId"],
        "faqQuestions": data["faqQuestions"],
        "faqAnswers": data["faqAnswers"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok'})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_delete(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_DELETE_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "faqId": data["faqId"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok'})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_clear(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_CLEAR_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok'})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_import(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_IMPORT_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skillId"]],
        "intentId": conf.UNIT_SKILL_ID,
        "filePath": data["filePath"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok'})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_file_upload(request):
    conf = request.app.config
    token = request.app.token
    data = request.files.get('file')

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FILE_UPLOAD_URL, token)

    payload = FormData()
    payload.add_field('file',
                      data.read(),
                      filename='faq.txt')

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})

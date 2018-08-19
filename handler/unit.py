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


async def unit_model_list(conf, token):

    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_LIST_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return resp_json['result']
    else:
        return None


async def unit_model_train(request):
    conf = request.app.config
    token = request.app.token

    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_TRAIN_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "trainOption": {
            "configure": {
                "smartqu": "true",
                "mlqu": "false"
            },
            "data": {
                "querySetIds": [],
                "patternSetIds": [2066]
            }
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    error_code = resp_json.get('error_code')
    if error_code == 0:
        return {'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']}
    elif error_code == 292012:
        return {'errcode': error_code, 'errmsg': '上一个训练还未结束，请等待半个小时后再尝试'}
    else:
        return {'errcode': error_code, 'errmsg': resp_json['error_msg']}


async def unit_model_delete(conf, token, model_id):
    url = '{}?access_token={}'.format(conf.SVC_UNIT_MODEL_DELETE_URL, token)
    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "modelId": model_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        print('delete model {} ok'.format(model_id))
    else:
        print('delete model {} failed: {}'.format(model_id, resp_json['error_msg']))


async def unit_faq_list(request, intent):
    conf = request.app.config
    token = request.app.token
    data = request.raw_args

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_LIST_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_SKILL_ID,
        "intentId": conf.UNIT_FAQ_INTENT_ID_MAP.get(intent, -1),
        "pageNo": int(data.get('pageNo', 1)),
        "pageSize": 100
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_info(request, intent, faq_id):
    conf = request.app.config
    token = request.app.tokens

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_INFO_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_SKILL_ID,
        "intentId": conf.UNIT_FAQ_INTENT_ID_MAP.get(intent, -1),
        "faqId":  faq_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    else:
        return response.json({'errcode': resp_json['error_code'], 'errmsg': resp_json['error_msg']})


async def unit_faq_add(conf, token, intent,  question, answer):
    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_ADD_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_SKILL_ID,
        "intentId": conf.UNIT_FAQ_INTENT_ID_MAP.get(intent),
        "faqQuestions": question,
        "faqAnswers": answer
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        print('add faq {} ok'.format(resp_json['result']['faqId']))
        return resp_json['result']['faqId']
    else:
        print('add faq failed: {}'.format(resp_json['error_msg']))
        return None


async def unit_faq_update(conf, token, intent_id, faq_id, question, answer):
    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_UPDATE_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_SKILL_ID,
        "intentId": intent_id,
        "faqId": faq_id,
        "faqQuestions": question,
        "faqAnswers": answer
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        print('update fap {} ok'.format(faq_id))
    else:
        print('update faq {} failed: {}'.format(faq_id, resp_json['error_msg']))


async def unit_faq_delete(conf, token, intent_id, faq_id):
    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_DELETE_URL, token)
    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_SKILL_ID,
        "intentId": intent_id,
        "faqId": faq_id
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp_json = await resp.json()

    if resp_json.get('error_code') == 0:
        print('delete fap {} ok'.format(faq_id))
    else:
        print('delete faq {} failed: {}'.format(faq_id, resp_json['error_msg']))


async def unit_faq_clear(request):
    conf = request.app.config
    token = request.app.token
    data = request.json

    url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_CLEAR_URL, token)

    payload = {
        "botId": conf.SVC_UNIT_BOT_ID,
        "skillId": conf.UNIT_FAQ_INTENT_ID_MAP[data["skill"]],
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

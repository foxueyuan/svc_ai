# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import aioredis
import json
import time
import uvloop
from sanic import Sanic
from elasticsearch_async import AsyncElasticsearch

import config

from handler.asr import asr
from handler.unit import unit_chat
from handler.nlp import lexer
from handler.nlp import simnet
from handler.nlp import spam
from handler.nlp import wordcom
from handler.nlp import textchat
from handler.kg import entity_annotation
from handler.train import (train, faq_add, faq_delete, faq_info, faq_list, faq_update,
                           faq_delete_by_title, faq_update_by_title)

app = Sanic(__name__)
app.config.from_object(config)

app.add_route(asr, '/ai/speech/asr', methods=['POST'])
app.add_route(lexer, '/ai/nlp/lexer', methods=['POST'])
app.add_route(simnet, '/ai/nlp/simnet', methods=['POST'])
app.add_route(spam, '/ai/nlp/spam', methods=['POST'])
app.add_route(wordcom, '/ai/nlp/wordcom', methods=['POST'])
app.add_route(textchat, '/ai/nlp/textchat', methods=['POST'])
app.add_route(unit_chat, '/ai/unit/bot/chat', methods=['POST'])

app.add_route(faq_list, '/ai/faq/intent/<intent>', methods=['GET'])
app.add_route(faq_add, '/ai/faq/intent/<intent>', methods=['PUT'])
app.add_route(faq_delete, '/ai/faq/intent/<intent>/doc/<doc_id>', methods=['DELETE'])
app.add_route(faq_update, '/ai/faq/intent/<intent>/doc/<doc_id>', methods=['POST'])
app.add_route(faq_info, '/ai/faq/intent/<intent>/doc/<doc_id>', methods=['GET'])
app.add_route(faq_delete_by_title, '/ai/faq/intent/<intent>', methods=['DELETE'])
app.add_route(faq_update_by_title, '/ai/faq/intent/<intent>', methods=['POST'])

app.add_route(train, '/ai/train', methods=['GET'])


app.add_route(entity_annotation, '/ai/kg/entity_annotation', methods=['POST'])


@app.listener('before_server_start')
async def before_server_start(app, loop):
    conf = app.config
    app.rdb = await aioredis.create_redis_pool(
        (conf.REDIS_HOST, conf.REDIS_PORT),
        db=conf.REDIS_DB,
        encoding='utf8',
        loop=loop
    )

    app.es = AsyncElasticsearch(hosts=['http://127.0.0.1:9200/'])

    token = json.loads(await app.rdb.get('token') or '{}')
    if not token or token['expiration'] < time.time() + 3600 * 24 * 7:
        token = await fetch_aip_token(app.config)
        await app.rdb.set('token', json.dumps(token))

    app.token = token['access_token']

    app.last_train_timestamp = 0


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.rdb.close()
    await app.rdb.wait_closed()

    await app.es.transport.close()


async def fetch_aip_token(conf):
    params = {'grant_type': 'client_credentials',
              'client_id': conf.AIP_AK,
              'client_secret': conf.AIP_SK}

    async with aiohttp.ClientSession() as session:
        async with session.get(conf.SVC_TOKEN_URL, params=params) as resp:
            result = await resp.json()

    result['expiration'] = int(time.time()) + result['expires_in']
    return result


if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    app.run(host=app.config.HOST, port=app.config.PORT, debug=True)

# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import aioredis
import json
import time
import uvloop
from sanic import Sanic

import config

from handler.asr import asr
from handler.unit import unit
from handler.nlp import lexer
from handler.nlp import simnet
from handler.kg import entity_annotation

app = Sanic(__name__)
app.config.from_object(config)


app.add_route(asr, '/ai/speech/asr', methods=['POST'])
app.add_route(lexer, '/ai/nlp/lexer', methods=['POST'])
app.add_route(simnet, '/ai/nlp/simnet', methods=['POST'])
app.add_route(unit, '/ai/unit/unit', methods=['POST'])
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

    token = json.loads(await app.rdb.get('token') or '{}')
    if not token or token['expiration'] < time.time() + 3600 * 24 * 7:
        token = await fetch_aip_token(app.config)
        await app.rdb.set('token', json.dumps(token))

    app.token = token['access_token']


@app.listener('after_server_stop')
async def after_server_stop(app, loop):
    app.rdb.close()
    await app.rdb.wait_closed()


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
    app.run(host=app.config.HOST, port=app.config.PORT)

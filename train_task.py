# -*- coding: utf-8 -*-

import random
import dramatiq
import requests
from elasticsearch import Elasticsearch
from dramatiq.brokers.redis import RedisBroker
from dramatiq.rate_limits import ConcurrentRateLimiter
from dramatiq.rate_limits.backends import RedisBackend
from dramatiq.message import Message
import config as conf


redis_broker = RedisBroker(url="redis://127.0.0.1:16379/15")
limits_backend = RedisBackend(url="redis://127.0.0.1:16379/14")
limiter = ConcurrentRateLimiter(limits_backend, "rate-limiter", limit=5)
dramatiq.set_broker(redis_broker)

es = Elasticsearch(hosts=conf.ES_HOST)


@dramatiq.actor(queue_name='train')
def check_should_retry(msg, flag):
    if flag is False:
        message = Message(
            queue_name=msg['queue_name'],
            actor_name=msg['actor_name'],
            args=msg['args'],
            kwargs=msg['kwargs'],
            options={'on_success': 'check_should_retry'},
            message_id=msg['message_id'],
            message_timestamp=msg['message_timestamp']
        )
        redis_broker.enqueue(message, delay=random.randrange(1000, 15000, 500))


@dramatiq.actor(queue_name='train')
def add_faq_task(token, question, answer, doc_index, doc_type, doc_id):
    with limiter.acquire(raise_on_failure=False) as acquired:
        if not acquired:
            print('limit reached')
            return False

        url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_ADD_URL, token)

        payload = {
            "botId": conf.SVC_UNIT_BOT_ID,
            "skillId": conf.UNIT_SKILL_ID,
            "intentId": conf.UNIT_FAQ_INTENT_ID_MAP.get(doc_type),
            "faqQuestions": question,
            "faqAnswers": answer
        }

        resp = requests.post(url, json=payload)
        resp_json = resp.json()

        if resp_json.get('error_code') == 0:
            print('add faq {} ok'.format(resp_json['result']['faqId']))
            body = {
                "doc": {
                    "skillId": conf.UNIT_SKILL_ID,
                    "intentId": conf.UNIT_FAQ_INTENT_ID_MAP[doc_type],
                    "faqId": resp_json['result']['faqId']
                }
            }
            es.update(index=doc_index, doc_type=doc_type, body=body, id=doc_id)
            return True
        else:
            print('add faq failed: {}'.format(resp_json['error_msg']))
            return False


@dramatiq.actor(queue_name='train')
def update_faq_task(token, intent_id, faq_id, question, answer):
    with limiter.acquire(raise_on_failure=False) as acquired:
        if not acquired:
            print('limit reached')
            return False

        url = '{}?access_token={}'.format(conf.SVC_UNIT_FAQ_UPDATE_URL, token)

        payload = {
            "botId": conf.SVC_UNIT_BOT_ID,
            "skillId": conf.UNIT_SKILL_ID,
            "intentId": intent_id,
            "faqId": faq_id,
            "faqQuestions": question,
            "faqAnswers": answer
        }

        resp = requests.post(url, json=payload)
        resp_json = resp.json()

        if resp_json.get('error_code') == 0:
            print('update fap {} ok'.format(faq_id))
            return True
        else:
            print('update faq {} failed: {}'.format(faq_id, resp_json['error_msg']))
            return False


@dramatiq.actor(queue_name='train', priority=10)
def train_task(token):
    with limiter.acquire(raise_on_failure=False) as acquired:
        if not acquired:
            print('limit reached')
            return False

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
                    "patternSetIds": conf.UNIT_TRAIN_PATTERNSETIDS
                }
            }
        }

        resp = requests.post(url, json=payload)
        resp_json = resp.json()

        error_code = resp_json.get('error_code')
        if error_code == 0:
            print({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
            return True
        else:
            print({'errcode': error_code, 'errmsg': resp_json['error_msg']})
            return False

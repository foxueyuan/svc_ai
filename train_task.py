import dramatiq
import requests
from elasticsearch import Elasticsearch
from dramatiq.brokers.redis import RedisBroker
# from dramatiq.results.backends import RedisBackend
# from dramatiq.results import Results

import config as conf

# result_backend = RedisBackend(url="redis://127.0.0.1:16379/14")
redis_broker = RedisBroker(url="redis://127.0.0.1:16379/15")
# redis_broker.add_middleware(Results(backend=result_backend))
dramatiq.set_broker(redis_broker)

es = Elasticsearch(hosts=conf.ES_HOST)


@dramatiq.actor
def add_faq_task(token, question, answer, doc_index, doc_type, doc_id):
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
    else:
        print('add faq failed: {}'.format(resp_json['error_msg']))


@dramatiq.actor
def update_faq_task(token, intent_id, faq_id, question, answer):
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
    else:
        print('update faq {} failed: {}'.format(faq_id, resp_json['error_msg']))


@dramatiq.actor(priority=10)
def train_task(token):
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

    resp = requests.post(url, json=payload)
    resp_json = resp.json()

    error_code = resp_json.get('error_code')
    if error_code == 0:
        print({'errcode': 0, 'errmsg': 'ok', 'result': resp_json['result']})
    elif error_code == 292012:
        print({'errcode': error_code, 'errmsg': '上一个训练还未结束，请等待半个小时后再尝试'})
    else:
        print({'errcode': error_code, 'errmsg': resp_json['error_msg']})

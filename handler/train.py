# -*- coding: utf-8 -*-

import time
from sanic import response
from .unit import (unit_model_list, unit_model_delete,
                   unit_model_train, unit_faq_add,
                   unit_faq_update, unit_faq_delete)

from train_task import (add_faq_task, update_faq_task, train_task, check_should_retry)


async def train(request):
    conf = request.app.config
    token = request.app.token
    es = request.app.es

    now = time.time()
    if now - request.app.last_train_timestamp < 1800:
        return response.json({'errcode': 292012, 'errmsg': '上一个训练还未结束，请等待半个小时后再尝试'})

    request.app.last_train_timestamp = now

    model_list = await unit_model_list(conf, token)

    if model_list and len(model_list) > 2:
        for model in model_list[2:]:
            await unit_model_delete(conf, token, model['modelId'])

    res = await es.search(
        index='train-index',
        doc_type='train',
        body={"size": 1},
        sort="createdAt:desc"
    )

    last_success_train_timestamp = res['hits']['hits'][0]['_source']['createdAt']

    q = {
        "query": {
            "bool": {
                "filter": {
                    "range": {"updatedAt": {"gt": last_success_train_timestamp}}
                }
            }
        },
        "size": 1000
    }

    doc_set = []

    qa_docs = await es.search(index='fo-index', doc_type='qa', body=q)
    doc_set.extend(qa_docs.get('hits', {}).get('hits', []))

    kg_docs = await es.search(index='fo-index', doc_type='kg', body=q)
    doc_set.extend(kg_docs.get('hits', {}).get('hits', []))

    instruction_docs = await es.search(index='fo-index', doc_type='instruction', body=q)
    doc_set.extend(instruction_docs.get('hits', {}).get('hits', []))

    for doc in doc_set:
        faq = doc['_source']
        question = [{"question": q} for q in faq['question']]
        answer = [{"answer": faq['answer']}]
        if 'faqId' in faq:
            update_faq_task.send_with_options(args=(token, faq['intentId'], faq['faqId'], question, answer),
                                              on_success=check_should_retry)
        else:
            add_faq_task.send_with_options(args=(token, question, answer, doc['_index'], doc['_type'], doc['_id']),
                                           on_success=check_should_retry)

    train_task.send_with_options(args=(token,), delay=600000)

    await es.index(
        index='train-index',
        doc_type='train',
        body={
            'qa': [doc['_id'] for doc in qa_docs.get('hits', {}).get('hits', [])],
            'kg': [doc['_id'] for doc in kg_docs.get('hits', {}).get('hits', [])],
            'instruction': [doc['_id'] for doc in instruction_docs.get('hits', {}).get('hits', [])],
            'createdAt': int(time.time())
        }
    )

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_list(request, intent):
    es = request.app.es
    args = request.raw_args

    if 'title' in args:
        if 'term' in args and args['term'] == 'false':
            q = {
                "query": {
                    "match": {
                        "title": args['title']
                    }
                }
            }
        else:
            q = {
                "query": {
                    "bool": {
                        "filter": {
                            "match_phrase": {
                                "title": args['title']
                            }
                        }
                    }
                },
                "size": 1
            }

        res = await es.search(index='fo-index', doc_type=intent, body=q)
        if res['hits']['hits']:
            doc = res['hits']['hits'][0]
            doc['_source'].pop("skillId", None)
            doc['_source'].pop("intentId", None)
            doc['_source'].pop("faqId", None)
            doc['_source']['_id'] = doc['_id']
            return response.json({'errcode': 0, 'errmsg': 'ok', 'result': doc['_source']})
        else:
            return response.json({'errcode': 0, 'errmsg': 'ok', 'result': {}})

    page_no = int(args.get('pageNo', 1))
    page_size = int(args.get('pageSize', 50))
    query_from = (page_no - 1) * page_size

    res = await es.count(index='fo-index', doc_type=intent)

    count = res['count']

    if query_from >= count:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': {}})

    q = {
        "query": {
            "match_all": {}
        },
        "from": query_from,
        "size": page_size
    }

    docs = await es.search(
        index='fo-index',
        doc_type=intent,
        body=q,
        filter_path=[
            'hits.hits._id',
            'hits.hits._source.title',
            'hits.hits._source.topic',
            'hits.hits._source.question',
            'hits.hits._source.answer',
            'hits.hits._source.updatedAt'
        ])

    if docs:
        rst_docs = []
        for doc in docs['hits']['hits']:
            rst_doc = doc['_source']
            rst_doc['_id'] = doc['_id']
            rst_docs.append(rst_doc)
        return response.json(
            {
                'errcode': 0,
                'errmsg': 'ok',
                'result':
                    {
                        "total": count,
                        "docs": rst_docs
                    }
            }
        )
    else:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': {}})


async def faq_add(request, intent):
    es = request.app.es
    data = request.json

    if isinstance(data, dict):
        body = {}
        if "title" in data:
            body['title'] = data['title']
        else:
            body['title'] = data['question'][0]

        if "topic" in data:
            body['topic'] = data['topic']

        body['question'] = data['question']
        body['answer'] = data['answer']
        body['updatedAt'] = int(time.time())

        await es.index(index='fo-index', doc_type=intent, body=body)
    elif isinstance(data, list):
        if len(data) > 1000:
            return response.json({'errcode': 413, 'errmsg': '批量插入条目不能超过1000'})
        for item in data:
            body = {}
            if "title" in item:
                body['title'] = item['title']
            else:
                body['title'] = item['question'][0]

            if "topic" in data:
                body['topic'] = item['topic']

            body['question'] = item['question']
            body['answer'] = item['answer']
            body['updatedAt'] = int(time.time())

            await es.index(index='fo-index', doc_type=intent, body=item)

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_delete(request, intent, doc_id):
    conf = request.app.config
    token = request.app.token
    es = request.app.es

    doc = await es.get(index='fo-index', doc_type=intent, id=doc_id, ignore=404)

    if doc['found']:
        if 'faqId' in doc['_source']:
            intent_id = doc['_source']['intentId']
            faq_id = doc['_source']['faqId']
            await unit_faq_delete(conf, token, intent_id, faq_id)
        await es.delete(index='fo-index', doc_type=intent, id=doc_id)

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_delete_by_title(request, intent):
    conf = request.app.config
    token = request.app.token
    es = request.app.es

    args = request.raw_args

    title = args.get('title')

    if not title:
        return response.json({'errcode': -1, 'errmsg': '缺少参数'})

    q = {
        "query": {
            "bool": {
                "filter": {
                    "match_phrase": {
                        "title": title
                    }
                }
            }
        },
        "size": 1
    }

    res = await es.search(index='fo-index', doc_type=intent, body=q)

    if res['hits']['hits']:
        doc = res['hits']['hits'][0]
        if 'faqId' in doc['_source']:
            intent_id = doc['_source']['intentId']
            faq_id = doc['_source']['faqId']
            await unit_faq_delete(conf, token, intent_id, faq_id)
        await es.delete(index='fo-index', doc_type=intent, id=doc['_id'])

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_update(request, intent, doc_id):
    es = request.app.es
    data = request.json

    body = {'doc': {}}
    if "title" in data:
        body['doc']['title'] = data['title']

    if "topic" in data:
        body['doc']['topic'] = data['topic']

    if "question" in data:
        body['doc']['question'] = data['question']

    if "answer" in data:
        body['doc']['answer'] = data['answer']

    if not body:
        return response.json({'errcode': 0, 'errmsg': 'ok'})

    body['doc']['updatedAt'] = int(time.time())
    await es.update(index='fo-index', doc_type=intent, body=body, id=doc_id)

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_update_by_title(request, intent):
    es = request.app.es
    args = request.raw_args
    data = request.json

    title = args.get('title')

    if not title:
        return response.json({'errcode': -1, 'errmsg': '缺少参数'})

    body = {'doc': {}}
    if "title" in data:
        body['doc']['title'] = data['title']

    if "topic" in data:
        body['doc']['topic'] = data['topic']

    if "question" in data:
        body['doc']['question'] = data['question']

    if "answer" in data:
        body['doc']['answer'] = data['answer']

    if not body:
        return response.json({'errcode': 0, 'errmsg': 'ok'})

    body['doc']['updatedAt'] = int(time.time())

    q = {
        "query": {
            "bool": {
                "filter": {
                    "match_phrase": {
                        "title": title
                    }
                }
            }
        },
        "size": 1
    }

    res = await es.search(index='fo-index', doc_type=intent, body=q)

    if res['hits']['hits']:
        doc = res['hits']['hits'][0]
        await es.update(index='fo-index', doc_type=intent, body=body, id=doc['_id'])

    return response.json({'errcode': 0, 'errmsg': 'ok'})


async def faq_info(request, intent, doc_id):
    es = request.app.es

    doc = await es.get(index='fo-index', doc_type=intent, id=doc_id, ignore=404)

    if doc['found']:
        doc['_source'].pop("skillId", None)
        doc['_source'].pop("intentId", None)
        doc['_source'].pop("faqId", None)
        doc['_source']['_id'] = doc['_id']
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': doc['_source']})
    else:
        return response.json({'errcode': 0, 'errmsg': 'ok', 'result': {}})

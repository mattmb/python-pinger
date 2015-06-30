#!/usr/bin/env python
import redis
import yaml
import json
import time
import pygerduty
import requests
import threading


class Master:

    def __init__(self):
        with open('./checks.yaml') as f:
            self.config = yaml.load(f)
        self.checks = self.config['checks']
        self.handlers = self.config['handlers']
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(['results'])
        self.log = logging.getLogger(self.__class__.__name__)
        for handler, params in self.handlers.items():
            self.handlers[handler]['pager'] = pygerduty.PagerDuty(
                params['org'],
                params['service_key'])
        for check in self.checks.keys():
            self.redis.set(self.key(check, 'time'), 0)
            self.redis.set(self.key(check, 'failures'), 0)
            self.redis.delete(self.key(check, 'down'))

    def publish_check(self, url, params):
        last_check = int(self.redis.get(self.key(url, 'time')))
        now_time = int(time.time())
        if last_check + params['interval'] <= now_time:
            self.redis.set(self.key(url, 'time'), int(time.time()))
            self.log.info("publishing check {0}".format(url))
            self.redis.rpush('checks', json.dumps({'url': url, 'params':
                params}))

    def handle_result(self, url, params, result, message, details):
        down = self.redis.get(self.key(url, 'down'))
        if result == 'DOWN':
            pager = self.handlers[params['handler']]['pager']
            service_key = self.handlers[params['handler']]['service_key']
            num_failures = int(self.redis.get(self.key(url, 'failures')))
            if num_failures >= params['failed_checks'] and not down:
                message = "{0} DOWN {1}".format(url, message)
                self.log.info(message)
                self.log.info(details)
                #pager.trigger_incident(service_key, message,
                                   #url, details)
                self.redis.set(self.key(url, 'down'), True)
            num_failures += 1
            self.redis.set(self.key(url, 'failures'), num_failures)

        if result == 'UP' and down:
            message = "{0} UP".format(url)
            self.log.info(message)
            #pager.resolve_incident(service_key, url, message)
            self.redis.delete(self.key(url, 'down'))
            self.redis.set(self.key(url, 'failures'), 0)

    def key(self, *args):
        return "_".join(args)

    def run(self):
        for item in self.pubsub.listen():
            print item['data']
            if item['data'] != 1:
                item = json.loads(item['data'])
                self.handle_result(**item)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    pp = Master()
    handler = threading.Thread(target=pp.run)
    handler.daemon = True
    handler.start()
    while True:
        for check, params in pp.checks.items():
            pp.publish_check(check, params)
        time.sleep(1)

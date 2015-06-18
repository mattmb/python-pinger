import redis
import yaml
import json
import time
import pygerduty
import requests


class PyPinger:

    def __init__(self):
        with open('./checks.yaml') as f:
            self.config = yaml.load(f)
        self.checks = self.config['checks']
        self.handlers = self.config['handlers']
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.log = logging.getLogger(self.__class__.__name__)

        for handler, params in self.handlers.items():
            self.handlers[handler]['pager'] = pygerduty.PagerDuty(
                params['org'],
                params['service_key'])
        for check in self.checks.keys():
            self.redis.set(self.key(check, 'time'), 0)
            self.redis.set(self.key(check, 'failures'), 0)
            self.redis.delete(self.key(check, 'down'))

    def check(self, url, params):
        last_check = int(self.redis.get(self.key(url, 'time')))
        now_time = int(time.time())
        down = self.redis.get(self.key(url, 'down'))
        pager = self.handlers[params['handler']]['pager']
        service_key = self.handlers[params['handler']]['service_key']
        if last_check + params['interval'] <= now_time:
            self.redis.set(self.key(url, 'time'), int(time.time()))
            self.log.info("checking {0}".format(url))
            try:
                r = requests.get(url, timeout=params['timeout'])
                if r.status_code not in range(200, 206):
                    raise HttpNon200(r.status_code)
            except Exception as e:
                num_failures = int(self.redis.get(self.key(url, 'failures')))
                if num_failures >= params['failed_checks'] and not down:
                    message = "{0} DOWN {1}".format(url, e.__class__.__name__)
                    self.log.info(message)
                    detail = json.dumps(str(e))
                    self.log.info(detail)
                    pager.trigger_incident(service_key, message,
                                           url, detail)
                    self.redis.set(self.key(url, 'down'), True)
                num_failures += 1
                self.redis.set(self.key(url, 'failures'), num_failures)
                return

            if down:
                message = "{0} UP".format(url)
                self.log.info(message)
                pager.resolve_incident(service_key, url, message)
                self.redis.delete(self.key(url, 'down'))
                self.redis.set(self.key(url, 'failures'), 0)

    def key(self, *args):
        return "_".join(args)


class HttpNon200(Exception):
    pass

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    pp = PyPinger()
    while True:
        for check, params in pp.checks.items():
            pp.check(check, params)
        time.sleep(1)

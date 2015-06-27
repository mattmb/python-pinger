#!/usr/bin/env python
from lib import pingermaster
import redis
import json
import requests

class Slave(pingermaster.Master):

    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(['checks'])
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        for item in self.pubsub.listen():
            print item
            if item['data'] != 1:
                item = json.loads(item['data'])
                result = self.check(item['url'], item['params'])
                self.redis.publish('results', json.dumps(result))
            
    def check(self, url, params):
        self.log.info("checking {0}".format(url))
        result = {'url': url, 'params': params, 'result': 'UP', 'message': 'Site is up'}
        try:
            r = requests.get(url, timeout=params['timeout'])
            if r.status_code not in range(200, 206):
                raise HttpNon200(r.status_code)
            result['details'] = r.status_code
        except Exception as e:
            result['result'] = 'DOWN'
            result['message'] = e.__class__.__name__
            result['details'] = str(e)
        return result
        
class HttpNon200(Exception):
    pass

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    pp = Slave()
    pp.run()

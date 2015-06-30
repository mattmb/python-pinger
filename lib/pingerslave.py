#!/usr/bin/env python
from lib import pingermaster
import redis
import json
import requests

class Slave(pingermaster.Master):

    def __init__(self):
        self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.log = logging.getLogger(self.__class__.__name__)

    def run(self):
        while True:
            item = self.redis.blpop('checks')
            print item
            check = json.loads(item[1])
            result = self.check(check['url'], check['params'])
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

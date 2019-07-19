#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import multiprocessing

import invoke
import redis
from fabric import Connection

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler('distributeCopy.log')
fh.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
formatter = logging.Formatter(fmt='%(asctime)s %(processName)s-%(threadName)s - %(name)s - %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

passwd = 'password'


def get_server_ip(srv):
    """
    return all server ip
    """
    pass


def get_remote_model():
    remote_path = '/data1/online/model/final_model/model'
    local_path = '/data1/rsync_data/ctr_model_webapi'
    invoke.run('rsync -a 10.11.11.43:%s %s' % (remote_path, local_path))


def do_local_copy(dst_ip, dst_path, queue):
    src_path = '/data1/rsync_data/ctr_model_webapi/model'
    result = Connection(dst_ip).put(src_path, remote=dst_path)
    queue.put(dst_ip)
    logger.info('do_local_copy %s: %s', dst_ip, result)


def do_peer_copy(args):
    dst_ip = args[0]
    queue = args[1]
    src_ip = queue.get()
    cmd = """sshpass -p "%s" rsync -e 'ssh -o "StrictHostKeyChecking no"' -a username@%s:%s %s""" % \
          (passwd, src_ip, '/data1/ctr_model/model', '/data1/ctr_model/')
    result = Connection(dst_ip).run(cmd)
    queue.put(dst_ip)
    logger.info('do_peer_copy %s => %s, %s', src_ip, dst_ip, result)
    # return result  Do not return anything :https://github.com/joblib/joblib/issues/818#issuecomment-445865581


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    q = manager.Queue()
    pool = multiprocessing.Pool(10)

    ips = get_server_ip('webapi')

    for ip in ips[:10]:
        do_local_copy(ip, '/data1/ctr_model/', q)

    pool.map(do_peer_copy, [(ip, q) for ip in ips[10:]])
    pool.close()
    pool.join()
    logger.info('finished')

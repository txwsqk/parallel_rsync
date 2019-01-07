#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Description: parallel scp
# Author     : quke
# Date       : 2019-01-07

import sys
import threading
from math import pow,log
from subprocess import Popen,PIPE

import redis

if len(sys.argv) == 2:
    model_name = sys.argv[1]
else:
    print 'Exception: need a model_name'
    raise SystemExit


redis_host = '192.168.254.11'
redis_port = 6379

connection = redis.StrictRedis(host=redis_host, port=redis_port, db=0)

server_list = connection.lrange(model_name, 0, -1)

def do_remote_ssh(src, dest):
    p = Popen(['ssh', 'username@%s' %src, 'export RSYNC_PASSWORD="password";rsync -t /data1/ab_model/%s sre@%s::ab' % (model_name, dest) ], shell=False, stdout=PIPE, stderr=PIPE)
    print '%s => %s, stdout=>%s|stderr=>%s' % (src, dest, p.stdout.read(), p.stderr.read())


def do_multithreading(task_list):
    thread_list = []
    print 'do_multithreading'
    for pair in task_list:
        src, dest = pair
        t = threading.Thread(target=do_remote_ssh, args=(src, dest))
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()


def binary_copy(aList):
    length = len(aList)
    loop = int(log(len(aList),2))
    for i in range(0, 1 + loop ):
        if 0 == i:
            first_minion = aList[:1]
            print 'start scp to %s' % first_minion
            p = Popen('export RSYNC_PASSWORD="password";rsync -t /data1/rsync_data/ctr_model/%s sre@%s::ab/' % (model_name, first_minion), shell=True, stdout=PIPE, stderr=PIPE)
            print '%s|stdout: %s|stderr: %s' % (first_minion, p.stdout.read(), p.stderr.read())
        else:
            do_multithreading(zip(aList[:int(pow(2,i-1))], aList[int(pow(2,i-1)):int(pow(2,i))]))

    if length > int(pow(2, loop)):
        do_multithreading(zip(aList, aList[int(pow(2,loop)):]))


if __name__ == '__main__':
    binary_copy(server_list)


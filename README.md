distributeCopy.py
1. get_remote_model  
    download file from remote to jumpserver which can ssh all server without password
2. do_local_copy
    copy file from jumpserver to remote
    prepare for [3] (below)
3. do_peer_copy
    ssh remoteserver and rsync from [2]
---
# parallel_rsync [deprecated]

## 先决条件

1. 一台机器(master)可以免密码 ssh 到其他机器
2. 要同步文件的所有机器(client)配置 rsync

## 演示

master 

192.168.1.50

client

['192.168.1.100', '192.168.1.101', '192.168.1.102', '192.168.1.103', '192.168.1.104', '192.168.1.105'...]



以2的 N 次方的步进并发 rsync

1. 192.168.1.50    scp  file ==> 192.168.1.100

2. 192.168.1.100 ==> 192.168.1.101

3. 192.168.1.100 ==> 192.168.1.102

   192.168.1.101 ==> 192.168.1.103

4. 192.168.1.100 ==> 192.168.1.104

   192.168.1.101 ==> 192.168.1.105

   192.168.1.102 ==> 192.168.1.106

   192.168.1.103 ==> 192.168.1.107

5. 2的3次方

6. 2的4次方


# 内网穿透（命令行）

## 服务器命令
```
usage: l0n0lnatserver [-h] listenhost listenport password

创建内网穿透服务器

positional arguments:
  listenhost  监听host
  listenport  监听端口
  password    密钥

optional arguments:
  -h, --help  show this help message and exit
```

## 客户端命令
```
usage: l0n0lnatclient [-h] serverhost serverport serverlistenport localhost localport password

创建内网穿透客户端

positional arguments:
  serverhost        监听host
  serverport        监听端口
  serverlistenport  服务器要监听端口
  localhost         本地服务host
  localport         本地服务端口
  password          密钥

optional arguments:
  -h, --help        show this help message and exit
```

## 使用实例

    比如在内网有一个nginx(localhost:80)
    服务器为 x.x.x.x

    1.在服务器执行
    l0n0lnatserver 0.0.0.0 12345 passwd

    2.在客户端执行
    l0n0lnatclient x.x.x.x 12345 8080 localhost 80 passwd

    3.访问http://x.x.x.x:8080
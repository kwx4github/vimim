#!/usr/bin/env python
# coding: utf-8

import sys
import socket
import os

DEFAULT_PORT = 10007
BUFSIZE = 1024
verbose = False

# sample server func
def sample_server_func(indata):
    if indata == 'close':
        return None # to shutdown the server
    elif indata == 'disconnect':
        return 0    # to disconnect
    elif indata == 'hello':
        return "acknowledgement"
    else:
        return "ignored"

def tcpslice(sendfunc, data):
    senddata = data
    while len(senddata) >= BUFSIZE:
        sendfunc(senddata[0:BUFSIZE])
        senddata = senddata[BUFSIZE:]
    if senddata[-1:] == "\n":
        sendfunc(senddata)
    else:
        sendfunc(senddata+"\n")

def tcpserver(func, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    name = 'tcp server'
    try:
        s.bind(('', port))
    except Exception, (errno, strerror):
        s.close()
        if verbose:
            print name, "start fail:", errno, strerror
        return
    if verbose:
        print name,'at port', port
    server_close = False;
    while True:
        s.listen(1)			# 服务器的侦听连接
        conn, addr = s.accept()	# 接收一个新的 tcp 连接会话
        if verbose:
            print name,'connected to', addr
        cachedata = ""
        while True:
            data = conn.recv(BUFSIZE)
            if not data:
                break
            if data[-1:] == "\n":
                data = cachedata + data[:-1]
                cachedata = ""
            else:
                cachedata += data
                continue
            if verbose:
                print name,'received:', data
            if func:
                try:
                    ret = func(data)
                except Exception, (errno, strerror):
                    if verbose:
                        print name,'exception:', errno, strerror
                    conn.send('\n')
                    continue
                if ret == None:
                    conn.send('server closed\n')
                    server_close = True
                    break
                elif ret == 0:
                    break
                elif type(ret).__name__ == "str":
                    if verbose:
                        print name, 'send data ',len(ret),'bytes'
                    tcpslice(conn.send, ret)
                else:
                    senddata = str(ret)
                    if verbose:
                        print name,'send data ',len(senddata),'bytes'
                    tcpslice(conn.send, senddata)
            else:
                conn.send('\n')
        conn.close()		# 关闭该 tcp 连接
        if verbose:
            print name,'closed connection to', addr
        if server_close:		# 关闭服务器的侦听连接
            break
    s.close()
    if verbose:
        print name, "exit"

def udpslice(sendfunc, data, addr):
    senddata = data
    while len(senddata) >= BUFSIZE:
        sendfunc(senddata[0:BUFSIZE], addr)
        senddata = senddata[BUFSIZE:]
    if senddata[-1:] == "\n":
        sendfunc(senddata, addr)
    else:
        sendfunc(senddata+"\n", addr)

def udpserver(func, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    name = 'udp server'
    try:
        s.bind(('', port))
    except Exception, (errno, strerror):
        s.close()
        print name, "start fail:", errno, strerror
        return
    print name,'on port', port
    while True:
        data, addr = s.recvfrom(BUFSIZE)
        data = data[:-1]
        print name,'received from %r: %s' % (addr, data)
        if func:
            try:
                ret = func(data)
            except Exception:
                s.sendto('\n', addr)
                continue
            if ret == None:
                s.sendto('server closed\n', addr)
                break
            elif ret == 0:
                pass
            elif type(ret).__name__ == "str":
                print name,'send data',len(ret),'bytes'
                udpslice(s.sendto, ret, addr)
            else:
                senddata = str(ret)
                print name,'send data',len(senddata),'bytes'
                udpslice(s.sendto, senddata, addr)
        else:
            s.sendto('\n', addr)
    s.close()
    print name,"exit"

def tcpsend(data, host, port):
    addr = host, port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(addr)
    except Exception, (errno, strerror):
        s.close()
        return None
    ret = ""
    for item in data.split("\n"):
        if item == "":
            continue
        tcpslice(s.send, item)
        cachedata = ""
        while cachedata[-1:] != "\n":
            data = s.recv(BUFSIZE)
            cachedata += data
        if cachedata == "server closed\n":
            break
        ret += cachedata
    s.close()
    return ret

def udpsend(data, host, port):
    addr = host, port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.bind(('', 0))
    except Exception, (errno, strerror):
        s.close()
        return None
    ret = ""
    for item in data.split("\n"):
        if item == "":
            continue
        udpslice(s.sendto, item, addr)
        cachedata = ""
        while cachedata[-1:] != "\n":
            data = s.recv(BUFSIZE)
            cachedata += data
        if cachedata == "server closed\n":
            break
        ret += cachedata
    s.close()
    return ret

def sample_client_func(prot, host="localhost", port=DEFAULT_PORT):
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        print 'sent request (%s) to %s ' % (line[:-1], host)
        data = prot(line, host, port)
        print 'response: ', data[:-1]
        if data == "server closed\n":
            break
    print "client exit"

def forkserver(func1, func2, port=DEFAULT_PORT):
    pid = os.fork()
    if pid == 0:
        func1(func2, port)
    else:
        pass

def setverbose(verb):
    global verbose
    verbose = verb

if __name__ == "__main__":
    if len(sys.argv) == 1:
        pass
    elif sys.argv[1] == "tcpserver":
        forkserver(tcpserver, sample_server_func)
    elif sys.argv[1] == "udpserver":
        forkserver(udpserver, sample_server_func)
    elif sys.argv[1] == "tcpclient":
        sample_client_func(tcpsend)
    elif sys.argv[1] == "udpclient":
        sample_client_func(udpsend)
    else:
        print "invalid argument"

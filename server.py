# -*- coding: utf-8 -*-
#14030410007	辛羽丰
#14030410004	王超
#14030210018	矫梦南

import socket
import asyncore
import sys
import time

global talk_list

reload(sys)
sys.setdefaultencoding('utf-8')
talk_list = []		#登录过的用户列表

class EchoHandler(asyncore.dispatcher_with_send):
	def handle_read(self): 	#重载handle_read接收新的数据
		global talk_list
		data = self.recv(8192).decode('utf-8')	#以utf-8格式接受数据data
		if data:
			print data
			for i in talk_list:	#向talk_list中的每一个成员发送data
				try:
					i.send(data)
				except:	#发送失败异常
					print "Error: Send %s filed."%data
					#talk_list.remove(i)	#从talk_list中删除i
				time.sleep(0.01)

class EchoServer(asyncore.dispatcher):
	def __init__(self, host, port):	#建立套接字
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind((host, port))
		self.listen(5)

	def handle_accept(self):	#重载handle_accept接受新的连接
		global talk_list
		pair = self.accept()
		if pair is not None:
			sock, addr = pair
			if sock not in talk_list:
				talk_list.append(sock)
			print 'Incoming connection from %s' % repr(addr)
			EchoHandler(sock)

host = socket.gethostname()	#获取本机hostname用于服务器
print host
server = EchoServer(host, 5005)
asyncore.loop()

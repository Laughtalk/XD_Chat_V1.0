# -*- coding: utf-8 -*-
import sys, os, threading, socket, json, time
from PyQt4 import QtGui, QtCore
import getmd5

_BUFFER = 65535

class ListenThread(threading.Thread):
	"""监听线程"""
	def __init__(self, server, txt, progressBar):
		super(ListenThread, self).__init__()
		self.server = server
		self.txt = txt
		self.progressBar=progressBar
	def run(self):
		while True:
			self.client, addr = self.server.accept()
			self.txt.append(u'连接来自{}:{}'.format(addr[0], addr[1]))
			
			file_name = json.loads(self.client.recv(_BUFFER).decode('utf-8')) 
			if file_name["name"] == "filename":
				file_name = file_name["data"]
			if not os.path.isfile(file_name):
				received = 0
				f = open(file_name,"wb")
			else:
				received = os.path.getsize(file_name)
				f = open(file_name,"ab")
			
			file_size = json.loads(self.client.recv(_BUFFER).decode('utf-8'))
			if file_size["name"] == "filesize":
				file_size = int(file_size["data"])
			
			file_md5 = json.loads(self.client.recv(_BUFFER).decode('utf-8'))
			if file_md5["name"] == "filemd5":
				file_md5 = file_md5["data"]
			
			self.client.send(str(received).encode('utf-8'))
			self.progressBar.setMinimum(0)    
			self.progressBar.setMaximum(file_size)
			
			if received == 0:
				self.txt.append (u"开始接收新文件。")
			else:
				percentage = (float(received) / float(file_size))*100.0
				self.txt.append (u"文件从 ( "+"%.0f" % percentage+u"% )开始断点续传。")
			
			self.txt.append (u"将要接收: "+str(file_size - received)+" bytes - "+file_name)
			l = self.client.recv(_BUFFER)
			self.progressBar.setValue(received)
			lost_connect = False
			while True:
				f.write(l)
				try:
					l = self.client.recv(_BUFFER)
				except:
					self.txt.append(u"连接丢失。。。")
					lost_connect = True
					break
				received += sys.getsizeof(l)
				#percentage = (received / file_size)*100
				#self.txt.append (u"接收 ( "+"%.0f" % percentage+"% )...")
				self.progressBar.setValue(received)
				if not l:
					break
			f.close()
			time.sleep(0.05)
			received_md5 = getmd5.getMd5OfFile(file_name)
			if received_md5 == file_md5:
				self.progressBar.setValue(file_size)
				self.txt.append (u"接收成功。")
				self.client.send((u"文件传输完成。").encode('utf-8'))
			else:
				self.txt.append (u"接收失败。")
				if not lost_connect:
					self.client.send((u"文件传输失败。").encode('utf-8'))
			self.client.close()
		
class ControlThread(threading.Thread):
	"""控制线程"""
	def __init__(self, txt, port, progressBar):
		super(ControlThread, self).__init__()
		self.txt = txt
		self.port = port
		self.progressBar=progressBar
		self.event = threading.Event()
		self.event.clear()
	def run(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = socket.gethostbyname(socket.gethostname())
		self.server.bind((self.host, self.port))
		self.server.listen(5)
		self.txt.append(u'端口：'+str(self.port)+u'\n正在等待连接。。。')
		self.lsn = ListenThread(self.server, self.txt, self.progressBar)
		self.lsn.setDaemon(True)
		self.lsn.start()
		self.event.wait()
		self.server.close()
	def stop(self):
		self.event.set()
class MyWindow(QtGui.QWidget):
	def __init__(self):
		super(MyWindow, self).__init__()
		self.setWindowTitle(u'XD Receive File')
		self.resize(485, 300)

		self.lblPort = QtGui.QLabel('Port')
		self.txtPort = QtGui.QLineEdit('1051')
		self.btnlsn = QtGui.QPushButton(u'监听')
		self.btnstop = QtGui.QPushButton(u'结束')
		self.txt = QtGui.QTextEdit()
		self.progressBar=QtGui.QProgressBar()

		grid = QtGui.QGridLayout()
		grid.addWidget(self.lblPort,0,0)
		grid.addWidget(self.txtPort, 0, 1)
		grid.addWidget(self.btnlsn, 0, 2)
		grid.addWidget(self.btnstop, 0, 3)
		
		grid.addWidget(self.progressBar, 1, 0,1,4)
		
		grid.addWidget(self.txt, 2, 0, 1, 4)
		self.setLayout(grid)

		self.connect(self.btnlsn, QtCore.SIGNAL('clicked()'), self.onBtnLsn)
		self.connect(self.btnstop, QtCore.SIGNAL('clicked()'), self.onBtnStop)
	def onBtnLsn(self):
		port = int(self.txtPort.text())
		self.ctrl = ControlThread(self.txt,port,self.progressBar)
		self.ctrl.setDaemon(True)
		self.ctrl.start()
	def onBtnStop(self):
		self.ctrl.stop()
'''
app = QtGui.QApplication(sys.argv)
mywindow = MyWindow()
mywindow.show()
app.exec_()
'''
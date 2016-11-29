# -*- coding: utf-8 -*-
import sys, os, socket, json, time, random
from PyQt4 import QtGui, QtCore
import getmd5

_BUFFER = 65535
	
def JSONsock(name,data):
	msg = {"name":name,"data":data}
	json_msg = json.dumps(msg)
	return json_msg

class MyWindow(QtGui.QWidget):
	def __init__(self):
		super(MyWindow, self).__init__()
		self.setWindowTitle(u'XD Send File')
		self.resize(485, 300)

		self.lblIp = QtGui.QLabel('IP')
		self.lblPort = QtGui.QLabel('Port')
		self.lblFile = QtGui.QLabel('File')
		self.txtIp = QtGui.QLineEdit('192.168.56.1')
		self.txtPort = QtGui.QLineEdit('1051')
		self.txtFile = QtGui.QLineEdit()
		self.btnBrowse = QtGui.QPushButton(u'浏览')
		self.btnSend = QtGui.QPushButton(u'发送')
		self.btnSend.setMaximumWidth(150)
		self.txt = QtGui.QTextEdit()
		self.progressBar=QtGui.QProgressBar()

		grid = QtGui.QGridLayout()
		
		grid.addWidget(self.lblFile, 0, 0)
		grid.addWidget(self.txtFile, 0, 1)
		grid.addWidget(self.btnBrowse, 0,2 )
		
		grid.addWidget(self.lblIp, 1, 0)
		grid.addWidget(self.txtIp, 1, 1)
		
		grid.addWidget(self.lblPort, 2, 0)
		grid.addWidget(self.txtPort, 2, 1)
		grid.addWidget(self.btnSend, 2, 2)
		
		grid.addWidget(self.progressBar, 3, 0,1,3)
		
		grid.addWidget(self.txt, 4, 0, 3, 3)
		
		self.setLayout(grid)

		self.connect(self.btnBrowse, QtCore.SIGNAL('clicked()'), self.onBtnBrowse)
		self.connect(self.btnSend, QtCore.SIGNAL('clicked()'), self.onBtnSend)

	def onBtnBrowse(self):
		filename = QtGui.QFileDialog.getOpenFileName(self, u'打开文件', filter=u'全部文件(*.*)')
		if filename:
			self.txtFile.setText(filename)

	def onBtnSend(self):
		host = self.txtIp.text()
		if host == "local":
			host = socket.gethostbyname(socket.gethostname())
		port = int(self.txtPort.text())  
		_file = unicode(self.txtFile.text().toUtf8(),'utf8')
		_type_index = _file.rfind(".")
		if _type_index != -1:
			_file_name = _file[:_type_index]
			_file_type = _file[_type_index:len(_file)]
		else:
			_file_name = _file
			_file_type = ""
		file_md5 = getmd5.getMd5OfFile(_file)
		try:
			f = open(_file,"rb")
		except:
			self.txt.append (u"文件打开错误。")
		self.txt.append (u"等待服务器。。。")
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			time.sleep(0.005)
			try:
				client.connect((host, port))
				break
			except:
				pass
		
		#client.send(JSONsock("filename",(_file_name+'('+randSTR()+')'+_file_type)).encode('utf-8'))
		client.send(JSONsock("filename",(_file_name+'(received)'+_file_type)).encode('utf-8'))
		file_size = os.path.getsize(_file)
		time.sleep(0.05)
		client.send(JSONsock("filesize",str(file_size)).encode('utf-8'))
		time.sleep(0.05)
		client.send(JSONsock("filemd5",str(file_md5)).encode('utf-8'))
		time.sleep(0.05)
		
		sent = int(client.recv(_BUFFER).decode('utf-8'))
		if sent == 0:
			self.txt.append (u"开始发送新文件。")
		else:
			percentage = (float(sent) / float(file_size))*100.0
			self.txt.append (u"文件从 ( "+"%.0f" % percentage+u"% )开始断点续传。")
			#self.txt.append (u"文件从"+str(sent)+u"bytes开始断点续传。")
		f.seek(sent)
		
		l = f.read(_BUFFER)
		self.progressBar.setMinimum(0)    
		self.progressBar.setMaximum(file_size)
		self.progressBar.setValue(sent)
		lost_connect = False
		while (l):
			try:
				client.send(l)
			except:
				self.txt.append(u"连接丢失。。。")
				lost_connect = True
				break
			l = f.read(_BUFFER)
			sent += sys.getsizeof(l)
			#percentage = (sent / file_size)*100
			#self.txt.append (u"发送 ( "+"%.0f" % percentage+"% )...")
			self.progressBar.setValue(sent)
		f.close()
		time.sleep(0.05)
		
		#self.txt.append (u"发送 ( 100% )...\n")
		if not lost_connect:
			client.shutdown(socket.SHUT_WR)
			self.progressBar.setValue(file_size)
			#self.txt.append (u"发送完成。")
			self.txt.append (u"等待接收方回复。。。")
			self.txt.append (u"接收方: "+client.recv(_BUFFER).decode('utf-8')) 
		else:
			self.txt.append (u"传输失败。")
		client.close()
'''
app = QtGui.QApplication(sys.argv)
mywindow = MyWindow()
mywindow.show()
app.exec_()
'''
# -*- coding: utf-8 -*-
#14030410007	辛羽丰
#14030410004	王超
#14030210018	矫梦南

import sys
import time
from PyQt4 import QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import socket

import fileclientui
import fileseverui

global signal
global send_buffer
global recive_buffer
global IP
global count
global user_name

reload(sys)
sys.setdefaultencoding("utf8")

count = 4
send_buffer = ""
recive_buffer = ""
IP = ""


class Signal(QObject):
	recive_S = pyqtSignal()
	Send_S = pyqtSignal()
	timeout_S = pyqtSignal()


class Data(QThread):
	def __init__(self):
		super(Data, self).__init__()
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def run(self):
		global send_buffer
		global recive_buffer
		global signal
		global IP
		global count
		global user_name
		self.client.settimeout(1)
		count = 4
		while True:
			try:
				self.client.connect((IP,5005))
				count = -99
				signal.timeout_S.emit()
				break
			except socket.timeout:
				if count > 0:
					count -= 1
					signal.timeout_S.emit()
				else:
					count = 4
					IP = ""
			except:
				pass
		while True:
			if send_buffer != "":
				# 将unicode编码转换成utf-8
				print (self.client.send(send_buffer.encode('utf-8')))
				send_buffer = ""
			try:
				# 将utf-8编码转换成unicode
				recive_buffer = self.client.recv(1000).decode('utf-8')
				signal.recive_S.emit()
			except socket.timeout:
				pass

class Connect(QWidget):
	def __init__(self):
		super(Connect, self).__init__()
		self.initUI()

	def initUI(self):
		global signal
		self.IP_text = QLineEdit(u"192.168.56.1", self)
		self.IP_text.setGeometry(30,20,200,30)

		self.name_text = QLineEdit(u"输入用户名", self)
		self.name_text.setGeometry(30,100,200,30)

		self.connect_button = QPushButton(u"连接", self)
		self.connect_button.setGeometry(110,140,40,30)
		self.connect_button.clicked.connect(self.start)

		self.error_text = QLabel(u"未连接服务器", self)
		self.error_text.setGeometry(30, 160, 200, 70)
		
		signal.timeout_S.connect(self.status)
		
		self.setWindowTitle("XD LogIn")
		
		self.resize(300,250)

	def status(self):
		global count
		if count > 0:
			text = "Connect Again:"+str(count)
			self.error_text.setText(text)
		elif count == 0:
			self.error_text.setText(u"未连接服务器")
		elif count == -99:
			self.error_text.setText(u"已连接")

	def start(self):
		global IP
		global user_name
		user_name = unicode(self.name_text.text().toUtf8()+':', 'utf-8')
		IP = self.IP_text.text()
		print (IP)

class ClientUI(QWidget):
	def __init__(self):
		super(ClientUI,self).__init__()
		self.work = Data()
		self.work.start()
		self.connect = Connect()
		self.fileclient = fileclientui.MyWindow()
		self.fileserver = fileseverui.MyWindow()
		self.initUI()

	def initUI(self):
		global signal
		signal.recive_S.connect(self.Recive)
		
		self.text = QTextBrowser(self)
		self.text.setGeometry(10, 10, 480, 400)
		self.text.append(u"使用前请点击连接服务进行登录。回车即可发送。")

		self.send = QLineEdit("Hello World!", self)
		self.send.setGeometry(10, 420, 420, 40)

		self.send_button = QPushButton(u"发送", self)
		self.send_button.setGeometry(440, 420, 50, 40)
		self.send_button.clicked.connect(self.Send)

		self.connect_button = QPushButton(u"连接服务", self)
		self.connect_button.setGeometry(15, 470, 110, 30)
		self.connect_button.clicked.connect(self.connect.show)
		
		self.check_users_button = QPushButton(u"查询用户", self)
		self.check_users_button.setGeometry(135, 470, 110, 30)
		self.check_users_button.clicked.connect(self.check_users)
		
		self.send_file_btn = QPushButton(u"发送文件", self)
		self.send_file_btn.setGeometry(255, 470, 110, 30)
		self.send_file_btn.clicked.connect(self.fileclient.show)
		
		self.receive_file_btn = QPushButton(u"接收文件", self)
		self.receive_file_btn.setGeometry(375, 470, 110, 30)
		self.receive_file_btn.clicked.connect(self.fileserver.show)

		self.resize(500, 510)
		
		self.setWindowTitle("XD ChatRoom")

	def keyPressEvent(self, event):
		keyEvent = QKeyEvent(event)
		if keyEvent.key() == QtCore.Qt.Key_Return:
			self.Send()

	def Send(self):
		global send_buffer
		global signal
		global user_name
		try:
			send_buffer = user_name + unicode(self.send.text().toUtf8(), 'utf-8')
		except:
			print (u"转码错误")
		print (send_buffer)
		self.send.clear()
		signal.Send_S.emit()

	def Recive(self):
		global recive_buffer
		if recive_buffer=='check_users':
			self.check_back()
			self.text.append(u"当前在线用户及其IP地址")
			recive_buffer = ""
		else:
			self.text.append(recive_buffer)
			recive_buffer = ""

	def check_users(self):
		global send_buffer
		global signal
		try:
			send_buffer = unicode("check_users")
		except:
			print (u"转码错误")
		print (send_buffer)
		self.send.clear()
		signal.Send_S.emit()

	def check_back(self):
		global send_buffer
		global signal
		global user_name
		global IP
		try:
			send_buffer = user_name + unicode(IP.toUtf8(), 'utf-8')
		except:
			print (u"转码错误")
		print (send_buffer)
		self.send.clear()
		signal.Send_S.emit()

if __name__ == '__main__':
	signal = Signal()
	app = QApplication(sys.argv)
	t = ClientUI()
	t.show()
	sys.exit(app.exec_())

# -*- coding: utf-8 -*-
import os
import hashlib
import sys

_FILE_SLIM = 65535

def getMd5OfFile(filename):
	'''
	用hashlib包计算MD5码
	'''
	hmd5 = hashlib.md5()
	fp = open(filename,"rb")
	f_size = os.stat(filename).st_size
	if f_size>_FILE_SLIM:
		while(f_size>_FILE_SLIM):
			hmd5.update(fp.read(_FILE_SLIM))
			f_size/=_FILE_SLIM
		if(f_size>0) and (f_size<=_FILE_SLIM):
			hmd5.update(fp.read())
	else:
		hmd5.update(fp.read())
	return hmd5.hexdigest()
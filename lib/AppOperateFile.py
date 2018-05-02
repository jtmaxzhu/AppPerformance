#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os

'''
操作文件
'''
class OperateFile(object):
    def __init__(self, file, method='w+'):
        self.file = file
        self.method = method
        self.fileHandle = None


    def mkdir_file(self):
        if not os.path.isfile(self.file):
            f = open(self.file, self.method)
            f.close()
            print("创建文件成功")
        else:
            print("文件已经存在")


    def remove_file(self):
        if os.path.isfile(self.file):
            os.remove(self.file)
            print("删除文件成功")
        else:
            print("文件不存在")
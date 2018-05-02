#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import pickle

'''
操作文件
'''
class OperatePick(object):

    def readInfo(self, path):
        data=[]
        with open(path, 'rb') as f:
            try:
                data = pickle.load(f)
                # print(data)
            except EOFError:
                data = []
                print("读取文件错误,文件内容为空")
        print("------read-------")
        print data
        return data

    def writeSum(self, init, data=None, path="data.pickle"):
        if init == 0:
            result = data
        else:
            _read = self.readInfo(path)
            result = _read - _read

        with open(path, 'wb') as f:
            print("------writeSum-------")
            print "Sum:%s" % result
            pickle.dump(result, f)

    def readSum(self, path):
        data = {}
        with open(path, 'rb') as f:
            try:
                data = pickle.load(f)
            except EOFError:
                data = {}
                print("读取文件错误,文件内容为空")
        print("------read-------")
        return data

    def writeInfo(self, data,  path):
        _read = self.readInfo(path)
        result=[]
        if _read:
            _read.append(data)
            result = _read
        else:
            result.append(data)
        with open(path, 'wb') as f:
            print("------writeInfo-------")
            print result
            pickle.dump(result, f)

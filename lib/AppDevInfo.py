#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,re
from lib.AppAdbCom import AdbDebug
ad = AdbDebug()

class DeviceMsg(object):

    def GetDevModel(self, dev):
        result = {}
        result["release"] =  ad.adbGetAndroidVersion(dev)# Android 系统，如anroid 4.0
        result["phone_name"] = ad.adbGetDeviceName(dev) # 手机名
        result["phone_model"] = ad.adbGetDeviceBrand(dev)  # 手机品牌
        return result

    #获取手机内存总数
    def GetDevMemTotal(self, dev):
        list = ad.adbGetDevMem(dev).split()
        for k, v in enumerate(list):
            if str(v) == 'MemTotal:':
                return int(list[k+1])

    #获取手机处理器核数量
    def GetDevCpuCore(self, dev):
        resp = ad.adbGetDevCPU(dev)
        return str(len(re.findall("processor", resp)))

    #获取手机屏幕分辨率
    def GetDevPix(self, dev):
        resp = ad.adbGetScreenSize(dev).split()[2]
        return resp

    def GetDevMsg(self, dev):
        pix = self.GetDevPix(dev)
        men_total = self.GetDevMemTotal(dev)
        phone_msg = self.GetDevModel(dev)
        cpu_sum = self.GetDevCpuCore(dev)
        # print(dev + ":"+ pix,men_total,phone_msg,cpu_sum)
        return phone_msg, men_total, cpu_sum, pix


if __name__ == "__main__":
   pass


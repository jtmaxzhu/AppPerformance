#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,time,subprocess
from PerConfig import AppPerCon

class AdbDebug(object):
    #adb通用处理函数
    # def adbCommon(self,target):
    #     list = self.checkDevices()
    #     count = len(list)
    #     if target + 1 > count:
    #         print "请确认连接手机数量，输入正确的序号，0为第一台，依此类推"
    #         return
    #     return list


    def call_adb(self, command):
        result = ''
        command_text = "adb %s" % (command)
        results = os.popen(command_text, "r")
        while True:
            line = results.readline()
            if not line:
                break
            result += line
        results.close()
        return result

    def checkDevices(self):
        res = self.call_adb("devices")
        devices = res.partition('\n')[2].replace('\n', '').split('\tdevice')
        return [device for device in devices if len(device) > 2]

    #停止adb服务
    def adbStop(self):
        return self.call_adb("kill-server")

    #开启adb服务
    def adbStart(self):
        return self.call_adb("start-server")

    #查看adb版本
    def adbVersion(self):
        return self.call_adb("version")

    #开启adb网络调试接口(需连接USB线)
    def adbTcp(self, target):
        return self.call_adb("-s %s tcpip 5555"% (target))

    #网络调试连接
    def adbNetConOpen(self, target, address):
        return self.call_adb("-s %s connect %s" % (target, address))

    #关闭网络调试连接
    def adbNetConClose(self, target, address):
        return self.call_adb("-s %s disconnect %s" % (target, address))


    # 将电脑文件拷贝到手机里面
    # [电脑上的目录] < 设备里的文件路径 >
    def push(self, target, local, remote):
        result = self.call_adb("-s %s push %s %s" % (target, local, remote))
        return result


    # 拉数据到本地
    # < 设备里的文件路径 > [电脑上的目录]
    def pull(self, target, remote, local):
        result = self.call_adb("-s %s pull %s %s" % (target, remote, local))
        return result

    #电脑端安装应用
    # -l    将应用安装到保护目录 / mnt / asec
    # -r    允许覆盖安装
    # -t    允许安装AndroidManifest.xml里application指定android:testOnly = "true"的应用
    # -s    将应用安装到sdcard
    # -d    允许降级覆盖安装
    # -g    授予所有运行时权限
    def adbInstallApk(self, target, local):
        return self.call_adb("-s %s install %s"(target, local))

    def adbInstallApk(self, var, local):
        return self.call_adb("install "+ var + local)

    #电脑端卸载应用
    # < packname > 表示应用的包名，-k
    # 参数可选，表示卸载应用但保留数据和缓存目录。
    def adbUninstallApk(self, target, packName):
        return self.call_adb("-s %s uninstall %s" % (target, packName))

    def adbUninstallApk(self, target, var, packName):
        return self.call_adb("-s %s uninstall %s %s" % (target, var, packName))


    #查看应用列表
    # 无	    所有应用
    # -f	显示应用关联的 apk 文件
    # -d	只显示 disabled 的应用
    # -e	只显示 enabled 的应用
    # -s	只显示系统应用
    # -3	只显示第三方应用
    # -i	显示应用的 installer
    # -u	包含已卸载应用
    def adbGetPmlist(self, target, var):
        return self.call_adb("-s %s shell pm list packages %s" % (target, var))

    # 清除应用数据缓存
    def adbCacheClear(self, target, packName):
        result = self.call_adb("-s %s shell pm clear %s" % (target, packName))
        return result.rstrip()

    # 查看应用详细信息
    def adbGetAppInfo(self, target, packName):
        result = self.call_adb("-s %s shell dumpsys package %s" % (target, packName))
        return result.strip()

    # 启动Activity
    def adbStartActivity(self, target, activity):
        result = self.call_adb("-s %s shell am start %s" % (target, activity))
        return result.rstrip()

    # 强制停止Activity
    def adbStopActivity(self, target, packName):
        result = self.call_adb("-s %s shell am force-stop %s" % (target, packName))
        return result.rstrip()

    # 获得设备型号
    def adbGetDeviceModel(self, target):
        result = self.call_adb("-s %s shell getprop ro.product.model" % (target))
        return result.rstrip()

    #  获取设备品牌
    def adbGetDeviceBrand(self, target):
        result = self.call_adb("-s %s shell getprop ro.product.brand" % (target))
        return result.rstrip()

    # 获得设备名称
    def adbGetDeviceName(self, target):
        result = self.call_adb("-s %s shell getprop ro.product.name" % (target))
        return result.rstrip()


    # 获得设备处理器型号
    def adbGetDeviceBoard(self, target):
        result = self.call_adb("-s %s shell getprop ro.product.board" % (target))
        return result.rstrip()


    # 设备重启
    def adbDeviceReboot(self, target):
        result = self.call_adb("-s %s reboot" % (target))
        return result.rstrip()


    # 获取电池状况
    def adbGetBattery(self, target):
        result = self.call_adb("-s %s shell dumpsys battery" % (target))
        return result.rstrip()

    # 获取屏幕分辨率
    def adbGetScreenSize(self, target):
        result = self.call_adb("-s %s shell wm size" % (target))
        return result.rstrip()

    # 获取屏幕dpi
    def adbGetScreenDPI(self, target):
        result = self.call_adb("-s %s shell wm density" % (target))
        return result.rstrip()

    # 获取屏幕参数
    def adbGetScreenInfo(self, target):
        result = self.call_adb("-s %s shell dumpsys window displays" % (target))
        return result.rstrip()

    # 获取Android系统版本
    def adbGetAndroidVersion(self, target):
        result = self.call_adb("-s %s shell getprop ro.build.version.release" % (target))
        return result.strip()

    # 获取IP地址
    def adbGetDevIP(self, target):
        result = self.call_adb("-s %s shell ifconfig wlan0" % (target))
        if int(self.adbGetAndroidVersion(target).split(".")[0]) > 4:
            if  result.rsplit(":")[1][19:23] == "inet":
                return result.rsplit(":")[2][:13]
            else:
                print "WIFI未开启，请打开WIFI开关"
                return
        else:
            return result.rsplit(":")[1][4:17]

    # 获取MAC地址
    def adbGetDevMac(self, target):
        result = self.call_adb("-s %s shell cat /sys/class/net/wlan0/address" % (target))
        return result.strip()

    # 获取CPU信息
    def adbGetDevCPU(self, target):
        result = self.call_adb("-s %s shell cat /proc/cpuinfo" % (target))
        return result.strip()


    # 获取系统内存信息
    def adbGetDevMem(self, target):
        result = self.call_adb("-s %s shell cat /proc/meminfo" % (target))
        return result.strip()


    # 获取应用内存信息
    def adbGetDevPidMem(self, target, packname):
        result = self.call_adb("-s %s shell dumpsys meminfo %s" % (target, packname))
        return result.strip()



    # 获取总的CPU使用时间
    def adbGetCpuTime(self, target):
        result = self.call_adb("-s %s shell cat /proc/stat" % (target))
        return result.strip()

    # 获取进程CPU时间片
    def adbGetPidJiff(self, target, pid):
        result = self.call_adb("-s %s shell cat /proc/%s/stat" % (target, pid))
        return result.strip()

    # 获取进程fps
    def adbGetPidfps(self, target, packname):
        result = self.call_adb("-s %s shell dumpsys gfxinfo %s" % (target, packname))
        return result.strip()

    # 获取进程流量信息
    def adbGetPidflow(self, target, packname, flag):
        if int(self.adbGetAndroidVersion(target).split('.')[0]) < 8:
            uid = AppPerCon.appuid['MATE8'][packname]
            rec = self.call_adb("-s %s shell cat /proc/uid_stat/%s/tcp_rcv" % (target, uid)).strip()
            sen = self.call_adb("-s %s shell cat /proc/uid_stat/%s/tcp_snd" % (target, uid)).strip()
            # print rec, sen
            flow = float(rec) + float(sen)
        else:
            if flag == 1:
             #   self.adbStartActivity(target, activity)
                pid = self.adbGetPid(target, packname)
                print pid
                lis = self.call_adb("-s %s shell cat /proc/%s/net/dev" % (target, pid)).strip().split()
                for k, v in enumerate(lis):
                    if v == 'wlan0:':
                        recindex = k + 1
                        tranindex = k + 9
                        flow = float(lis[recindex])+float(lis[tranindex])
                        self.adbStopActivity(target, packname)
                        break
            else:
                    lis = self.call_adb("-s %s shell cat /proc/net/dev" % (target)).strip().split()
                    for k, v in enumerate(lis):
                        if v == 'wlan0:':
                            recindex = k + 1
                            tranindex = k + 9
                            flow = float(lis[recindex]) + float(lis[tranindex])
                            break

        return flow


    def adbGetPid(self, target, packname):
        if int(self.adbGetAndroidVersion(target).split('.')[0]) < 8:
            pid = self.call_adb("-s %s shell ps | findstr %s"%(target, packname)).rstrip().split("\n")
            if pid == ['']:
                print "this process doesn't exist"
                return None
            else:
                for item in pid:
                    if item.split()[8] == packname:
                        return item.split()[1]
        else:
            pid = self.call_adb("-s %s shell top -n 1 | findstr %s" % (target, packname)).strip().split()
            if pid == []:
                print "this process doesn't exist"
                return None
            else:
                return pid[0]



    def adbGetUid(self, target, packname):
        pid = self.adbGetPid(target, packname)
        lis = self.call_adb('-s %s shell cat /proc/%s/status' % (target, pid)).split()
        uid = 0
        for k, v in enumerate(lis):
            if v == 'Uid:':
                index = k + 1
                uid = lis[index]
                break
        return uid

    def adbGetAPPstartTime(self, target, activity):
        lis = self.call_adb('-s %s shell am start -W %s' % (target, activity))
        for k, v in enumerate(lis):
            if v == 'TotalTime:':
                index = k + 1
                time = lis[index]
                break
        return time




if __name__ == '__main__':
    pass









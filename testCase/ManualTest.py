#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,shutil
import threading
import time,datetime,subprocess

from PerConfig import AppPerCon
from lib.AppAdbCom import AdbDebug
from lib.AppDevInfo import DeviceMsg
from lib.AppMonitor import AppMoni
from lib.AppOperateFile import OperateFile
from lib.AppOperatePick import OperatePick

PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(os.path.realpath('__file__')), p)) #os.path.realpath(path)  返回path的真实路径

ad = AdbDebug()
apm = AppMoni()
devMs = DeviceMsg()
pick = OperatePick()
Config = AppPerCon()

#全局变量
MemTestFlag = 0
monkey_log=''
path_log=''



# 手机信息
def get_phone(dev):
    phone_info = devMs.GetDevMsg(dev)
#    print phone_info
    app = {}
    app["phone_name"] = phone_info[0]["phone_name"] + "_" + phone_info[0]["phone_model"] + "_" + phone_info[0]["release"]
    app["rom"] = phone_info[1]
    app["kel"] = phone_info[2]
    app["pix"] = phone_info[3]
    return app

def Create_pickle(dev, app, data):
    print("创建持久性文件...")
    if apm.IsIP(dev) == True:
        devIP = dev.split(':')[0].replace(".","")
        Manualmen = PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_mem.pickle")
        Manualcpu = PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_cpu.pickle")
        Manualjiff = PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_jiff.pickle")
        Manualfps = PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_fps.pickle")

    else:
        Manualmen = PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_mem.pickle")
        Manualcpu = PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_cpu.pickle")
        Manualjiff = PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_jiff.pickle")
        Manualfps = PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_fps.pickle")

   # time.sleep(2)
   #  app[dev] = {"freemen": freemen, "medimen": medimen, "fullmen": fullmen,
   #              "freecpu": freecpu, "medicpu": medicpu, "fullcpu": fullcpu,
   #              "header": get_phone(dev)}
    OperateFile(Manualmen).mkdir_file()
    OperateFile(Manualcpu).mkdir_file()
    OperateFile(Manualjiff).mkdir_file()
    OperateFile(Manualfps).mkdir_file()
    OperateFile(PATH(Config.info_path + "sumInfo.pickle")).mkdir_file() # 用于记录是否已经测试完毕，里面存的是一个整数
    OperateFile(PATH(Config.info_path + "info.pickle")).mkdir_file() # 用于记录统计结果的信息，是[{}]的形式
    pick.writeSum(0, data, PATH(Config.info_path + "sumInfo.pickle")) # 初始化记录当前真实连接的设备数

#log生成函数
def logProcess(dev, runtime):
    # logcat日志
    logcat_log = path_log + "\\" + runtime + "logcat.log"
    cmd_logcat = "-s " + dev + " logcat -d > %s" % (logcat_log)
    ad.call_adb(cmd_logcat)
    print 'logcat 完成'

    # "导出traces文件"
    traces_log = path_log + "\\" + runtime + "traces.log"
    cmd_traces = "-s " + dev + " shell cat /data/anr/traces.txt > %s" % (traces_log)
    ad.call_adb(cmd_traces)
    print 'traces_log 完成'

def start(dev):
    rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
    num = len(rt) - 2
    print(num)
    app = {}
    Create_pickle(dev, app, num)
    signal = raw_input("现在是手动测试部分，是否要开始你的测试，请输入(y or n): ")
    if signal == 'y' or 'Y':
        print("测试即将开始，请打开需要测试的app并准备执行您的操作....")
        time.sleep(5)
        run_time = time.strftime("%Y-%m-%d_%H%M%S", time.localtime(time.time()))
        logProcess(dev, run_time)
        while True:
            try:
                time.sleep(1)  # 每1秒采集一次
                print("----------------数据采集-----------------")
                apm.pid_mem(dev, Config.package_name, 3)
                apm.pid_cpuRate(dev, Config.package_name, 3)
                #fps 测试需要打开开发者模式GPU模式
                apm.pid_fps(dev, Config.package_name, 3)
            except:
                break

    elif signal == 'n':
        print('用户主动放弃测试，测试结束！')
    else:
        print("测试结束，输入非法，请重新输入y or n！")

#启动多线程
class MonkeyTestThread(threading.Thread):
    def __init__(self, dev):
        threading.Thread.__init__(self)
        self.dev = dev
        self.thread_stop = False

    def run(self):
        time.sleep(2)
        start(self.dev)



def create_threads_monkey(device_list):
    Thread_instances = []
    if device_list != []:
        for id_instance in device_list:
            dev = id_instance
            testInstance = MonkeyTestThread(dev)
            Thread_instances.append(testInstance)
        for instance in Thread_instances:
            instance.start()


if __name__ == '__main__':
    device_dir = os.path.exists(AppPerCon.info_path)
    if device_dir:
        print ("持久性目录info已存在，继续执行测试!")
    else:
        #os.mkdir(AppPerformanceConfig.info_path)  # 创建持久性目录,需要在文件存在的情况下创建二级目录
        os.makedirs(AppPerCon.info_path)   # 使用makedirs可以在文件夹不存在的情况下直接创建
    device_list = apm.get_device()
    if ad.checkDevices():
        print("设备存在")
        create_threads_monkey(device_list)
    else:
         print("设备不存在")



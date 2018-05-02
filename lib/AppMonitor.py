#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os,subprocess,time,re,time
import AppAdbCom
from lib.AppOperatePick import OperatePick
from PerConfig import AppPerCon
from wsgiref.validate import validator


PATH = lambda p: os.path.abspath(os.path.join(os.path.dirname(os.path.realpath('__file__')), p)) #os.path.realpath(path)  返回path的真实路径
dev_list =[]
ad = AppAdbCom.AdbDebug()
pick = OperatePick()
Config = AppPerCon()

class AppMoni(object):

    # 判断传入的dev字符串是否是ip地址
    def IsIP(self, dev):
        if dev == '':
            return False
        index = dev.find(':')
        if index != -1:
            ip = dev[:index]
            addr = ip.split('.')
            if len(addr) != 4:
                return False
            for i in addr:
                if int(i) < 255 and int(i) >= 0:
                    return True
                else:
                    return False


    def get_device(self):
        rt = os.popen('adb devices').readlines()  # os.popen()执行系统命令并返回执行后的结果
        n = len(rt) - 2
        print("当前已连接待测手机数为：" + str(n))
        for i in range(n):
            nPos = rt[i + 1].index("\t")
            dev = rt[i+1][:nPos]
            dev_list.append(dev)
        return dev_list


    def get_pid(self, target, pack):
        pid = ad.adbGetPid(target, pack)
        return pid

    def get_devSystemison(self,target):
        return ad.adbGetAndroidVersion(target)

    def get_battery(self, target):
        list = ad.adbGetBattery(target).split()
        for k,v in enumerate(list):
            if str(v) == "level:":
                battery =  int(list[k+1])
        print("--------battery--------")
        if self.IsIP(target) == True:
            target = target.split(':')[0].replace(".", "")
            print type(battery)
            pick.writeInfo(battery, PATH(Config.info_path + target + "_battery.pickle"))
        else:
            pick.writeInfo(battery, PATH(Config.info_path + target + "_battery.pickle"))
        return battery

    def totalCpuTime(self, dev):
        user = nice = system = idle = iowait = irq = softirq = 0
        '''
        user    从系统启动开始累计到当前时刻，用户态的CPU时间（单位：jiffies） ，不包含 nice值为负进程。1jiffies=0.01秒
        nice    从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间（单位：jiffies）
        system  从系统启动开始累计到当前时刻，核心时间（单位：jiffies）
        idle    从系统启动开始累计到当前时刻，除硬盘IO等待时间以外其它等待时间（单位：jiffies）
        iowait  从系统启动开始累计到当前时刻，硬盘IO等待时间（单位：jiffies） ，
        irq     从系统启动开始累计到当前时刻，硬中断时间（单位：jiffies）
        softirq 从系统启动开始累计到当前时刻，软中断时间（单位：jiffies）
        '''
        res = ad.adbGetCpuTime(dev).split()
        try:
            for info in res:
                if info == "cpu":
                    user = res[1]
                    nice = res[2]
                    system = res[3]
                    idle = res[4]
                    iowait = res[5]
                    irq = res[6]
                    softirq = res[7]
                    result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
                    # print("totalCpuTime=" + str(result))
                    return result
        except:
            return 0

    def pidCpuJiff(self, target, pid):
        '''
        utime   该任务在用户态运行的时间，单位为jiffies
    　　stime   该任务在核心态运行的时间，单位为jiffies
    　　cutime  累计的该任务的所有的waited-for进程曾经在用户态运行的时间，单位为jiffies
    　　cstime= 累计的该任务的所有的waited-for进程曾经在核心态运行的时间，单位为jiffies
        '''
        utime = stime = cutime = cstime = 0
        try:
            res = ad.adbGetPidJiff(target, pid).split()
            utime = res[13]
            stime = res[14]
            cutime = res[15]
            cstime = res[16]
            result = int(utime) + int(stime) + int(cutime) + int(cstime)
        except:
            result = 0
        return result


    '''
    通过jiff来进行CPU计算
    '''

    def cpu_jiffrate(self, dev, packname):
        pid = self.get_pid(dev, packname)
        processCpuTime1 = self.pidCpuJiff(dev, pid)
        totalCpuTime1 = self.totalCpuTime(dev)
        time.sleep(1)
        processCpuTime2 = self.pidCpuJiff(dev, pid)
        totalCpuTime2 = self.totalCpuTime(dev)
        processCpuTime3 = processCpuTime2 - processCpuTime1
        totalCpuTime3 = (totalCpuTime2 - totalCpuTime1)
        cpu = 100 * (processCpuTime3) / (totalCpuTime3)
        return cpu

    '''
    计算某进程的cpu使用率 top方式
    dev     :    设备号
    packname:    应用包名
    flag    :    # 0: 空闲状态
                 # 1：中等压力
                 # 2：满压力
    '''
    def pid_cpuRate(self, dev, packname, flag):
        pid = self.get_pid(dev, packname)
        if int(self.get_devSystemison(dev).split('.')[0])<8:
            reslist =  ad.call_adb("-s %s shell top -s cpu -n 1 | findstr %s" % (dev, pid)).split()
            #print reslist
            ratelist = list(reslist[4])
            strRate = ''
            for i in range(len(ratelist) - 1):
                strRate += ratelist[i]
            rate = int(strRate)
        else:
            rate = self.cpu_jiffrate(dev, packname)
        print("--------设备：%s cpurate--------") % dev
        if rate >= 0 and flag == 0:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(rate, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Free_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Free_cpu.pickle"))
            else:
                pick.writeInfo(rate, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Free_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Free_cpu.pickle"))
        elif rate >= 0 and flag == 1:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(rate, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Medium_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Medium_cpu.pickle"))
            else:
                pick.writeInfo(rate, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Medium_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Medium_cpu.pickle"))
        elif rate >= 0 and flag == 2:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(rate, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Full_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Full_cpu.pickle"))
            else:
                pick.writeInfo(rate, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Full_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Full_cpu.pickle"))
        elif rate >= 0 and flag == 3:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(rate, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Manual_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_cpu.pickle"))
            else:
                pick.writeInfo(rate, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Manual_cpu.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_cpu.pickle"))
        return rate

    #获得CPU进程时间片
    def pid_Jiff(self, dev, pid):
        processCpuTime1 = self.pidCpuJiff(dev, pid)
        time.sleep(1)
        processCpuTime2 = self.pidCpuJiff(dev, pid)
        processCpuTime3 = processCpuTime2 - processCpuTime1
        jiff = processCpuTime3
        print("--------jiff--------")
        if jiff >= 0:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(jiff, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "_jiff.pickle"))
            else:
                pick.writeInfo(jiff, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "_jiff.pickle"))
        return jiff


    ''' 
    获得指定应用内存信息
    # 0: 空闲状态
    # 1：中等压力
    # 2：满压力
    '''
    def pid_mem(self, dev, pkg_name, flag):
        lis = ad.adbGetDevPidMem(dev, pkg_name).split()
        #print lis
        for i in range(len(lis)):
            if lis[i] == "TOTAL":
                data = lis[i+1]
                break
        mem = int(data)
        print("--------设备：%s mem--------") % dev
        if mem >= 0 and flag == 0:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(mem, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Free_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Free_mem.pickle"))
            else:
                pick.writeInfo(mem, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Free_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Free_mem.pickle"))

        elif mem >= 0 and flag == 1:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(mem, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Medium_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Medium_mem.pickle"))
            else:
                pick.writeInfo(mem, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Medium_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Medium_mem.pickle"))
        elif mem >= 0 and flag == 2:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(mem, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Full_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Full_mem.pickle"))
            else:
                pick.writeInfo(mem, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Full_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Full_mem.pickle"))
        elif mem >= 0 and flag == 3:
            if self.IsIP(dev) == True:
                devIP = dev.split(':')[0].replace(".", "")
                pick.writeInfo(mem, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Manual_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_mem.pickle"))
            else:
                pick.writeInfo(mem, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Manual_mem.pickle"))
                pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                               PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_mem.pickle"))
        return mem


    # 获得指定应用FPS信息

    def pid_fps(self, dev, pkg_name, flag):
        results = ad.adbGetPidfps(dev, pkg_name)
        # print results
        frames = [x for x in results.split('\n')]
        jank_count = 0
        vsync_overtime = 0
        render_time = 0
        try:
            for k,v in enumerate(frames):
                if v == '\tDraw\tPrepare\tProcess\tExecute' or v == '\tDraw\tProcess\tExecute\r':
                    indexstart =  k+1
                elif v == 'View hierarchy:' or v == 'View hierarchy:\r':
                    indexend =  k-1
            fra = frames[indexstart:indexend]
            frame_count = len(fra)
            for frame in fra:
                time_block = re.split(r'\s+', frame.strip())
                for k, v in enumerate(frames):
                    if v == '\tDraw\tProcess\tExecute\r':
                        render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2])
                    elif v == '\tDraw\tPrepare\tProcess\tExecute':
                        render_time = float(time_block[0]) + float(time_block[1]) + float(time_block[2]) + float(time_block[3])
                '''
                当渲染时间大于16.67，按照垂直同步机制，该帧就已经渲染超时
                那么，如果它正好是16.67的整数倍，比如66.68，则它花费了4个垂直同步脉冲，减去本身需要一个，则超时3个
                如果它不是16.67的整数倍，比如67，那么它花费的垂直同步脉冲应向上取整，即5个，减去本身需要一个，即超时4个，可直接算向下取整
    
                最后的计算方法思路：
                执行一次命令，总共收集到了m帧（理想情况下m=128），但是这m帧里面有些帧渲染超过了16.67毫秒，算一次jank，一旦jank，
                需要用掉额外的垂直同步脉冲。其他的就算没有超过16.67，也按一个脉冲时间来算（理想情况下，一个脉冲就可以渲染完一帧）
    
                所以FPS的算法可以变为：
                m / （m + 额外的垂直同步脉冲） * 60
                '''
                if render_time > 16.67:
                    jank_count += 1
                    if render_time % 16.67 == 0:
                        vsync_overtime += int(render_time / 16.67) - 1
                    else:
                        vsync_overtime += int(render_time / 16.67)
            print("-----fps------")
            if frame_count == 0:
                _fps = 60
            else:
                _fps = int(frame_count * 60 / (frame_count + vsync_overtime))
            if flag == 1:
                if self.IsIP(dev) == True:
                    devIP = dev.split(':')[0].replace(".", "")
                    pick.writeInfo(_fps, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Medium_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Medium_fps.pickle"))
                else:
                    pick.writeInfo(_fps, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Medium_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Medium_fps.pickle"))

            elif flag == 2:
                if self.IsIP(dev) == True:
                    devIP = dev.split(':')[0].replace(".", "")
                    pick.writeInfo(_fps, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Full_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Full_fps.pickle"))
                else:
                    pick.writeInfo(_fps, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Full_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Full_fps.pickle"))
            elif flag == 3:
                if self.IsIP(dev) == True:
                    devIP = dev.split(':')[0].replace(".", "")
                    pick.writeInfo(_fps, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "Manual_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + devIP + "_" + Config.package_name + "_" + "Manual_fps.pickle"))
                else:
                    pick.writeInfo(_fps, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "Manual_fps.pickle"))
                    pick.writeInfo(time.strftime("%H:%M:%S", time.localtime(time.time())),
                                   PATH(Config.info_path + dev + "_" + Config.package_name + "_" + "Manual_fps.pickle"))
            return _fps
        except Exception as e:
            print "请打开开发者模式中的GPU显示"


    # 获得指定应用上下行流量信息
    def flow(self, dev, packname, activity):
        ad.adbStopActivity(dev, packname)
        flow1 = self.pid_flowSingle(dev, packname, 0)
        time.sleep(1)
        ad.adbStartActivity(dev, activity)
        time.sleep(15)
        flow2 = self.pid_flowSingle(dev, packname, 1)
        flow = (flow2 - flow1) / 1024
        if self.IsIP(dev) == True:
            devIP = dev.split(':')[0].replace(".", "")
            pick.writeInfo(flow, PATH(Config.info_path + devIP + "_"+ Config.package_name + "_" + "first_flow.pickle"))
        else:
            pick.writeInfo(flow, PATH(Config.info_path + dev + "_"+ Config.package_name + "_" + "first_flow.pickle"))
        return flow

    def pid_flowSingle(self, dev, packname, flag):
        flow = ad.adbGetPidflow(dev, packname, flag)
        return flow

    def pid_startTime(self, dev, packname):
        time = ad.adbGetPidflow(dev, packname)
        return int(time)










if __name__ == '__main__':
    pass
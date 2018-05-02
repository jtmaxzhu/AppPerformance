# AppPerformance
Android移动端性能测试工具

class AppPerCon(object):
    # apk包名
    package_name = "com.aliyun.alink"
    # 活动名
    alink_Activity = 'com.aliyun.alink/.page.main.MainActivity'
    # 默认设备列表
    device_dict = {}
    #手机安装应用默认UID,通过adb进行查询可获得
    appuid = {'MATE8':{'com.robam.roki':'10274','com.UCMobile':'10156','com.aliyun.alink':'10222'},
              'MATE10':{'com.robam.roki': '10164', 'com.UCMobile':'10138','com.aliyun.alink':'10145'}
    }
    # 网络
    net = "wifi"
    # monkey seed值，随机产生
    # monkey_seed = str(random.randrange(1, 1000))
    monkey_seed = 200
    # monkey 参数
    monkey_parameters_full = "--throttle 50 --ignore-crashes --ignore-timeouts --pct-touch 80 --pct-trackball 5 --pct-appswitch 9 --pct-syskeys 1 --pct-motion 5 -v -v -v 1000"
    monkey_parameters_medi = "--throttle 150 --ignore-crashes --ignore-timeouts --pct-touch 80 --pct-trackball 5 --pct-appswitch 9 --pct-syskeys 1 --pct-motion 5 -v -v -v 2500"
    #monkey_parameters = "--throttle 500 -v -v -v 500"
    # log保存地址
    log_location = os.path.dirname(os.path.realpath(__file__))+"\log"
    #性能数据存储目录
    info_path = os.path.dirname(os.path.realpath(__file__))+"\info" + "\\"
    # report保存地址
    report_path = os.path.dirname(os.path.realpath(__file__)) + "\\report\
  
  这个类用于配置测试过程的一些参数
  
  report 使用pyecharts生成效果如下
  
  
  

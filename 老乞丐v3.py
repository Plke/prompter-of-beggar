# %%
import subprocess
from io import BytesIO
from PIL import Image, ImageChops
import  cv2
import numpy as np
import schedule
import time
from datetime import datetime, timedelta
from wxpusher import WxPusher
import pytesseract
from skimage import io, color, metrics
import requests
import json

#截取当前屏幕
def take_screenshot(filename):
    # 截取当前虚拟机屏幕并传输到计算机上
    command = f"adb -s {全局_EMULATOR_NAME} exec-out screencap -p"
    screenshot_data = subprocess.check_output(command, shell=True)

    # 处理截图数据
    screenshot = Image.open(BytesIO(screenshot_data))
    # screenshot = screenshot.transpose(Image.Transpose.ROTATE_270)
    # 保存截图为指定的文件
    screenshot.save(filename)
    screenshot.close()

def kill_app(packetname):
    time.sleep(1)
    command = f"adb -s {全局_EMULATOR_NAME} shell am force-stop {packetname}"
    subprocess.run(command, shell=True)
def start_app(packetname):
    # 截取当前虚拟机屏幕并传输到计算机上
    time.sleep(1)
    command = f"adb -s {全局_EMULATOR_NAME} shell am start {packetname}"
    
    subprocess.run(command, shell=True)
def reboot():#重启模拟器
    command = f"adb -s {全局_EMULATOR_NAME} adb -s device1 reboot"
    subprocess.run(command, shell=True)
# 读取图像，解决imread不能读取中文路径的问题
def cv_imread(filepath):
    cv_img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), -1)
    return cv_img

#计算结构相似性指数(SSIM)得到相似程度
def compare_images(image1_path, image2_path):
    img1 = io.imread(image1_path, as_gray=True)
    img2 = io.imread(image2_path, as_gray=True)

    # 校验图片尺寸是否相同
    if img1.shape != img2.shape:
        raise ValueError("两张图片的尺寸必须相同")

    # 计算结构相似性指数(SSIM)
    ssim_value = metrics.structural_similarity(img1, img2)

    return ssim_value
#通过wxpusher发送消息
def wxPusher_send_messaget_post(summary,content,topic_id,token):
    payload = {
    "appToken":token,
    "summary":summary,
    "content":content,
    "contentType":1,
    "topicIds":[ 
        topic_id
    ],
    "url":"https://wxpusher.zjiecode.com", 
}
    url= "https://wxpusher.zjiecode.com/api/send/message"

    request = requests.post(url, json=payload).json()
    
    return request


#对x，y坐标点击
def tap_screen(x, y):
    # 使用adb命令模拟屏幕点击
    command = f"adb -s {全局_EMULATOR_NAME} shell input tap {x} {y}"
    subprocess.run(command, shell=True)

#划动
def swipe_screen(start_x, start_y, end_x, end_y,duration_ms=300):
    
    command = f"adb -s {全局_EMULATOR_NAME} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
    subprocess.run(command, shell=True)
 
#输入
def input_text_to_vm(text):
    # 使用adb shell input text命令将文本输入到指定虚拟机
    command = f'adb -s {全局_EMULATOR_NAME} shell input text "{text}"'
    subprocess.run(command, shell=True)


def recognize_number_in_image(image_path,start_x,start_y,end_x,end_y):
    # 打开图片
    image = Image.open(image_path)
    
    # 使用Tesseract OCR进行识别
    cropped_image = image.crop((start_x, start_y, end_x, end_y))
    # result = pytesseract.image_to_string(image[start_x:end_x,start_y,end_y,:], config='--psm 6 outputbase digits')
    result = pytesseract.image_to_string(cropped_image, config='--psm 6 outputbase digits')
    
    # 尝试将结果转换为整数
    try:
        number = int(result)
        return number
    except ValueError:
        print("无法识别数字")
        return 0

def find_image_in_larger(image_small_path,image_large_path):
    # 读取大图和小图
    image_large = cv_imread(image_large_path)
    image_small = cv_imread(image_small_path)

    # 检查图片是否读取成功
    if image_large is None or image_small is None:
        print("无法读取图片.")
        return

    # 使用模板匹配方法
    result = cv2.matchTemplate(image_large, image_small, cv2.TM_CCOEFF_NORMED)
    #zhao
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    

    (startX, startY) = maxLoc
    center_x = startX + image_small.shape[1]/2
    center_y = startY + image_small.shape[0]/2
    return maxVal,center_x, center_y

#目前只能登录已登录过的账号，之后添加密码登录
def log_in(用户名=None,密码=None,区服_路径=None,threshold=0.93):
    print('当前登录：'+用户名)
    tap_screen(6,124)#点击悬浮窗
    time.sleep(1)
    tap_screen(124,124)#点击切号
    time.sleep(1)
    tap_screen(155,480)#点击确认切号
    time.sleep(1)
    # #切换账号
    # if 账号_路径!=None:
    #     time.sleep(1)
    #     tap_screen(459,327)#点击展开账号
    #     截图_路径="图片/screenshot.png"
    #     take_screenshot(截图_路径)
    #     val,x,y=find_image_in_larger(账号_路径,截图_路径)
    #     print('查找账号：{}'.format(val))
    #     if val>=threshold:
    #         time.sleep(1)
    #         tap_screen(x,y)#点击确认登录
    if 用户名!=None:        
        tap_screen(263,464)#点击其他方式登录
        time.sleep(1)
        tap_screen(373,278)#点击密码登录
        time.sleep(1)
        tap_screen(165,323)#点击输入账号
        input_text_to_vm(用户名)
        time.sleep(1)
        tap_screen(171,373)#点击输入密码
        input_text_to_vm(密码)
        time.sleep(1)
        tap_screen(145,484)#点击同意协议
        time.sleep(1)
        tap_screen(261,446)#点击登录
        time.sleep(4)
    else:
        time.sleep(1)
        tap_screen(246,376)#点击确认登录
    time.sleep(1)
    tap_screen(456,197)#退出公告
    #切换区服
    if 区服_路径!=None:
        time.sleep(1)
        tap_screen(267,312)#点击展开区服
        time.sleep(1)
        截图_路径="图片/screenshot.png"
        take_screenshot(截图_路径)
        val,x,y=find_image_in_larger(区服_路径,截图_路径)
        print('查找区服1：{}'.format(val))
        if val>=threshold:
            time.sleep(1)
            tap_screen(x,y)#点击确认区服
        #没找到区服，就往下滑
        else:
            time.sleep(1)
            swipe_screen(270,800,270,500)#向下拖动，收起活动面板
            time.sleep(1)
            截图_路径="图片/screenshot.png"
            take_screenshot(截图_路径)
            val,x,y=find_image_in_larger(区服_路径,截图_路径)
            print('查找区服2：{}'.format(val))
            if val>=threshold:
                time.sleep(1)
                tap_screen(x,y)#点击确认区服
    time.sleep(1)
    tap_screen(262,445)#进入游戏

#已经进入游戏界面
def 结束打桩(threshold=0.8):
    time.sleep(1)
    #截图查看是否在打桩
    截图_路径="图片/screenshot.png"
    在家_路径="图片/在家.png"
    #截图查看是打桩是否完成
    swipe_screen(261,481,261,356)#向向上拖动，收起活动面板
    time.sleep(1)
    take_screenshot(截图_路径)
    val,_,_=find_image_in_larger(在家_路径,截图_路径)
    print('没打桩的概率',val)
    time.sleep(1)
    if val<threshold:    #如果成立，那就是在打桩
        print("正在打桩")
        提示='图片/打桩结束提示.png'
        截图_路径="图片/screenshot.png"

        #截图查看是打桩是否完成
        take_screenshot(截图_路径)
        val,_,_=find_image_in_larger(提示,截图_路径)
        
        if val>=threshold:
            print('查找打桩1：{}'.format(val))
            tap_screen(267,898)#打桩结束了
        else:
            print('查找打桩2：{}'.format(val))
            tap_screen(32,45)#没结束时
            tap_screen(362,571)#暂时离开
    else:
        print("没在打桩")

def check_福缘():
    结束打桩()
    swipe_screen(261,481,261,356)#打开活动面板
    tap_screen(78,913)#点击角色按钮
    time.sleep(1)
    截图_路径="图片/screenshot.png"
    #截图查看福源
    take_screenshot(截图_路径)
    res1=recognize_number_in_image(截图_路径,108,493,155,516)#查看福源
    res2=recognize_number_in_image(截图_路径,150,114,259,149)#查看经验
    tap_screen(484,906)#点击退出键
    return res1,res2
    
#人需要站在豪华房子
def check_老乞丐(区,threshold=0.8,topic_id=None):
    print(区+"检查时间时间：", datetime.now())
    time.sleep(1)
    swipe_screen(261,356,261,481)#向下拖动，收起活动面板
    截图_路径="图片/screenshot.png"
    房子_路径="图片/豪华房子.png"
    #截图查看否是在豪华房子
    take_screenshot(截图_路径)
    val,_,_=find_image_in_larger(房子_路径,截图_路径)
    if val>threshold:    #如果成立，那就是在大壮
        print('豪华房子：{}'.format(val))
        time.sleep(1)
        tap_screen(384,913)#出豪华房子
        time.sleep(5)
    else:
        print("破房子")
        tap_screen(272,719)#出破房子
        time.sleep(3)
        
    
    tap_screen(22,320)#前往中心第一步
    time.sleep(1)
    tap_screen(22,320)#前往中心
    time.sleep(2)
    #看看告示牌在不在
    截图_路径="图片/screenshot.png"
    take_screenshot(截图_路径)
    告示牌_路径 = "图片/告示牌.png"
    val,_,_=find_image_in_larger(告示牌_路径,截图_路径)
    if val<threshold:
        print("出错啦，告示牌不在")
        wxPusher_send_messaget_post('出错了','出错了','你的提示id',全局_wxapp_token)
        return -1 #出错了
    tap_screen(447,450)#点击告示牌
    time.sleep(2)
    截图_路径="图片/screenshot.png"
    take_screenshot(截图_路径)
    返回键_路径="图片/返回键.png"
    val,_,_=find_image_in_larger(返回键_路径,截图_路径)
    if val<threshold:
        print("出错啦，告示牌没打开")
        wxPusher_send_messaget_post('出错了','出错了','你的提示id',全局_wxapp_token)
        return -1 #出错了
    
    老乞丐_路径 = "图片/老乞丐.png"
    
    val,_,_=find_image_in_larger(老乞丐_路径,截图_路径)
    print('乞丐相似度：{}'.format(val))
    laile=0
    if val>=threshold:
        print(区+"老乞丐来了")
        laile=1
        内容=区+'老乞丐来了\n'+str(datetime.now())[:-7]
        wxPusher_send_messaget_post(区+'老乞丐来了',内容,topic_id,全局_wxapp_token)

    else:
        print("老乞丐没来")
    tap_screen(40,46)#点击退出键
    time.sleep(1)
    # tap_screen(512,514)#去往镇东
    # time.sleep(2)
    # tap_screen(473,653)#点击木桩
    # time.sleep(3)
    # tap_screen(282,909)#开始打桩
    # time.sleep(1)
    return laile





# %%
#查找每个区服的可用账号
def check_ava():
    for 区 in  全局_可用_账号:
        区_路径='图片/'+str(区)+'.png'
        if len(全局_区服_总帐号[区])!=0:#对应区服有账号时
            for 号 in 全局_区服_总帐号[区]: 
                # 号_路径='图片/'+号+'.png'
                用户名=全局_账号[号][0]
                密码=全局_账号[号][1]
                log_in(用户名,密码,区_路径)
                time.sleep(1)
                res1,res2=check_福缘()
                
                print(区+号+' 福缘：{},经验：{}'.format(res1,res2))
                if res1>=70 and res2>=400000:
                    全局_可用_账号[区].append(号)  #即第i个服务器，可用的账号为第j个，如i=0,j=0,混1可用账号为小号1
                    break
        
#福源不满足的曲服提示
def 提示区服不来():
    for 区 in 全局_可用_账号:
        if len(全局_可用_账号[区])==0 and len(全局_区服_总帐号[区])!=0:#没有福源足够的账号
            内容=str(区)+' '+str(len(全局_区服_总帐号[区]))+'个小号福源均不够，今天没有提示'
            print(区+'已提示',内容)
            topic_id=全局_topic[区]
            wxPusher_send_messaget_post('今天没有老乞丐提示',内容,topic_id,全局_wxapp_token)
 
        if len(全局_可用_账号[区])==0 and len(全局_区服_总帐号[区])==0:#没有账号
            
            内容=str(区)+'目前没有账号，今天没有提示'
            print(区+'已提示',内容)
            topic_id=全局_topic[区]
            wxPusher_send_messaget_post('今天没有老乞丐提示',内容,topic_id,全局_wxapp_token)

            
            
#检查已经满足福源的区服的乞丐，如果来了就返回1，防止以后检查
def check(区服路径,用户名,密码,区,topic_id):
    
    log_in(用户名,密码,区服路径)
    time.sleep(1)
    结束打桩()
    time.sleep(1)
    laile=check_老乞丐(区,topic_id=topic_id)
    if laile ==-1:
        time.sleep(2)
        print('正在重启')
        reboot()
        time.sleep(15)
        print('正在打开应用')
        start_app(全局_启动)
        time.sleep(15)
        # print('正在关闭')
        # kill_app(全局_关闭)
        # time.sleep(10)
        # print('正在重启')
        # start_app(全局_启动)
        # time.sleep(20)
        log_in(用户名,密码,区服路径)    #防止切号不回房子的bug，在切一次号
        time.sleep(2)
        laile=check(区服路径,用户名,密码,区,topic_id)
    return laile 


def job():              #循环登录加检查老乞丐
    for 区 in (全局_可用_账号):
        if len(全局_可用_账号[区])!=0:
            区服路径='图片/'+str(区)+'.png'
            # 账号路径='图片/'+全局可用[i][0]+'.png'
            用户名=全局_账号[全局_可用_账号[区][0]][0]
            密码=全局_账号[全局_可用_账号[区][0]][1]
            topic_id=全局_topic[区]
            res=check(区服路径,用户名,密码,str(区),topic_id)
            if res==1:
                全局_可用_账号[区]=[]
    print(全局_可用_账号)

# %%
# #连接设备
# process = subprocess.Popen("adb devices -l", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# command_output = process.stdout.read().decode('utf-8')
# print(command_output)




# %% [markdown]
# 可以通过区服为关键字创建一个字典
# 
# 每个字典关键字的内容为本服务器有人物的帐号
# 
# 通过这个字典筛选符合条件的账号然后在蹲

# %%
#定义全局变量
全局_可用_账号={
#     '官1':[],
#     '官2':[],
#     '官3':[],
#     '混1':[],
#     '混2':[],
#     '混3':[],
#     '混4':[],
#     '混5':[],
#     '混6':[],
#     '混7':[],
#     '混8':[],
#     '混9':[],
    '混10':[],
#     '混11':[],
    '混12':[],
#     '混13':[],
#     '混14':[]     
}
全局_区服_总帐号={
    '官1':[],
    '官2':[],
    '官3':[],
    '混1':[],
    '混2':[],
    '混3':['小号1','小号2','小号3','小号4'],       #小号1经验不够，小号2经验不够，小号4经验不够
    '混4':[],
    '混5':[],
    '混6':[],
    '混7':[],
    '混8':[],
    '混9':[],
    '混10':['小号1','小号2','小号3','小号4','小号7'],
    '混11':['小号1','小号5'],
    '混12':['小号6'],
    '混13':['小号1'],       #小号1经验不够
    '混14':['小号4']
}
全局_账号={
    '小号1':['你的帐号',#0为账号，1为密码
           '你的密码']，
}

全局_topic={
    '官1':'你的id',
 
}
全局_EMULATOR_NAME = "127.0.0.1:62001"  # 模拟器的名称
全局_wxapp_token='你的token'

#通过adb shell dumpsys window | findstr mCurrentFocus获取当前运行的应用的消息，就是下面这个
全局_启动='com.maple.madherogo/com.maple.madherogo.AppActivity'
全局_关闭='com.maple.madherogo'


# %%

check_ava()
提示区服不来()
print(全局_可用_账号)
# job()

# %%
schedule.every().day.at("07:59:30").do(job)
schedule.every().day.at("08:29:30").do(job)
schedule.every().day.at("08:59:30").do(job)
schedule.every().day.at("09:29:30").do(job)
schedule.every().day.at("09:59:30").do(job)
schedule.every().day.at("10:29:30").do(job)
schedule.every().day.at("10:59:30").do(job)
schedule.every().day.at("11:29:30").do(job)
schedule.every().day.at("12:29:30").do(job)
schedule.every().day.at("12:59:30").do(job)
schedule.every().day.at("13:29:30").do(job)
schedule.every().day.at("13:59:30").do(job)
schedule.every().day.at("14:29:30").do(job)
schedule.every().day.at("14:59:30").do(job)
schedule.every().day.at("15:29:30").do(job)
schedule.every().day.at("15:59:30").do(job)
schedule.every().day.at("16:29:30").do(job)
schedule.every().day.at("16:59:30").do(job)
schedule.every().day.at("17:29:30").do(job)
schedule.every().day.at("18:29:30").do(job)
schedule.every().day.at("18:59:30").do(job)
schedule.every().day.at("19:29:30").do(job)
schedule.every().day.at("20:29:30").do(job)
schedule.every().day.at("20:59:30").do(job)
schedule.every().day.at("21:29:30").do(job)

while True:
    schedule.run_pending()
    time.sleep(10)

# %%
全局_可用_账号




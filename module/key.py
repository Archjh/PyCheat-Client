from pynput import mouse, keyboard
import time
import threading
from tkinter import *
from collections import deque

# 使用双端队列存储点击时间戳，限制长度避免内存泄漏
lclicks = deque(maxlen=100)  # 存储左键点击时间戳
rclicks = deque(maxlen=100)  # 存储右键点击时间戳
shifts = []

def calculate_cps(clicks):
    """计算每秒点击次数"""
    now = time.time()
    # 统计1秒内的点击次数
    return sum(1 for click_time in clicks if now - click_time <= 1)

def on_click(x, y, button, pressed):
    """鼠标点击事件处理"""
    global lclicks, rclicks
    
    try:
        if button == mouse.Button.left:
            if pressed:
                lclicks.append(time.time())
                canvas.itemconfigure(r1, fill='blue')
            else:
                canvas.itemconfigure(r1, fill='#acb6b9')
        elif button == mouse.Button.right:
            if pressed:
                rclicks.append(time.time())
                canvas.itemconfigure(r2, fill='blue')
            else:
                canvas.itemconfigure(r2, fill='#acb6b9')
                
        # 更新CPS显示
        lcps = calculate_cps(lclicks)
        rcps = calculate_cps(rclicks)
        canvas.itemconfigure(l, text=f'{lcps}cps')
        canvas.itemconfigure(r, text=f'{rcps}cps')
    except Exception as e:
        print(f"Error in on_click: {e}")

def key_on(key):
    """键盘按下事件处理"""
    global shifts
    try:
        if str(key) == 'Key.space':
            canvas.itemconfigure(r3, fill='blue')
        if str(key) == 'Key.shift':
            canvas.itemconfigure(r4, fill='blue')
        if str(key) == "'w'" or str(key) == "'W'":
            canvas.itemconfigure(r5, fill='blue')
        if str(key) == "'a'" or str(key) == "'A'":
            canvas.itemconfigure(r6, fill='blue')
        if str(key) == "'s'" or str(key) == "'S'":
            canvas.itemconfigure(r7, fill='blue')
        if str(key) == "'d'" or str(key) == "'D'":
            canvas.itemconfigure(r8, fill='blue')
            
        if str(key) == 'Key.shift_r':
            if len(shifts) < 3:
                shifts.append(time.time())
            else:
                if time.time()-shifts[0] <=1 and time.time()-shifts[1] <=1 and time.time()-shifts[2]<=1:
                    setup = Toplevel()
                    setup.title('设置')
                    setup.geometry('250x150')
                    setup.resizable(0,0)
                    setup.attributes('-topmost','true')
                    Button(setup,text='全部退出',command=lambda:exit()).place(x=170,y=110)
                    shifts = []
                else:
                    shifts = []
    except Exception as e:
        print(f"Error in key_on: {e}")

def key_release(key):
    """键盘释放事件处理"""
    try:
        if str(key) == 'Key.space':
            canvas.itemconfigure(r3, fill='#acb6b9')
        if str(key) == 'Key.shift':
            canvas.itemconfigure(r4, fill='#acb6b9')
        if str(key) == "'w'" or str(key) == "'W'":
            canvas.itemconfigure(r5, fill='#acb6b9')
        if str(key) == "'a'" or str(key) == "'A'":
            canvas.itemconfigure(r6, fill='#acb6b9')
        if str(key) == "'s'" or str(key) == "'S'":
            canvas.itemconfigure(r7, fill='#acb6b9')
        if str(key) == "'d'" or str(key) == "'D'":
            canvas.itemconfigure(r8, fill='#acb6b9')
    except Exception as e:
        print(f"Error in key_release: {e}")

# 启动键盘和鼠标监听
keyboard_listener = keyboard.Listener(on_press=key_on, on_release=key_release)
keyboard_listener.start()

mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()

# 创建GUI窗口
window = Tk()
window.overrideredirect(True)
window.config(bg='#114514')
window.attributes('-topmost','true')
window.attributes('-alpha',0.90)
width = 210
height = 280

# 获取屏幕宽度和高度
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# 计算窗口左下角的坐标
x_pos = 0
y_pos = screen_height - height

# 设置窗口位置为左下角
window.geometry(f'{width}x{height}+{x_pos}+{y_pos}')

canvas = Canvas(window, highlightthickness=0, bg='#114514')
canvas.place(width=width, height=height)

# 创建UI元素
r1 = canvas.create_rectangle(10,140,102.5,210,fill='#acb6b9')
r2 = canvas.create_rectangle(107.5,140,200,210,fill='#acb6b9')
r3 = canvas.create_rectangle(10,215,200,240,fill='#acb6b9')
r4 = canvas.create_rectangle(10,245,200,270,fill='#acb6b9')
r5 = canvas.create_rectangle(75,10,135,70,fill='#acb6b9')
r6 = canvas.create_rectangle(10,75,70,135,fill='#acb6b9')
r7 = canvas.create_rectangle(75,75,135,135,fill='#acb6b9')
r8 = canvas.create_rectangle(140,75,200,135,fill='#acb6b9')

canvas.create_text(56.25,170,text='LMB',font=('微软雅黑',15))
canvas.create_text(153.75,170,text='RMB',font=('微软雅黑',15))
canvas.create_text(105,227.5,text='SPACE',font=('微软雅黑',10))
canvas.create_text(105,257.5,text='LSHIFT',font=('微软雅黑',10))
canvas.create_text(105,40,text='W',font=('微软雅黑',13))
canvas.create_text(40,105,text='A',font=('微软雅黑',13))
canvas.create_text(105,105,text='S',font=('微软雅黑',13))
canvas.create_text(170,105,text='D',font=('微软雅黑',13))

l = canvas.create_text(56.25,192,text='0cps',font=('微软雅黑',12))
r = canvas.create_text(153.75,192,text='0cps',font=('微软雅黑',12))

window.mainloop()

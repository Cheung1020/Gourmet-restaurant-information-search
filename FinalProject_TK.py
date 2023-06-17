import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import io
import winsound
import random

base_url = 'https://ifoodie.tw/explore/%E6%A1%83%E5%9C%92%E5%B8%82/list/%E9%BE%9C%E5%B1%B1%E7%BE%8E%E9%A3%9F2022'

# 更新選擇的餐廳資訊和圖片
def show_selected_restaurant_info():
    selected_name = selected_restaurant.get()
    if selected_name in restaurant_info:
        info = restaurant_info[selected_name]
        restaurant_name_label.config(text='餐廳名稱: ' + selected_name)
        avg_price_label.config(text='均消: ' + info['均消'])
        opening_hours_label.config(text='營業時間: ' + info['營業時間'])
        address_label.config(text='地址: ' + info['地址'])
        if selected_name in image_urls:
            image_url = image_urls[selected_name]
            if image_url:
                # 清除舊圖片
                image_label.config(image='')

                # 下載圖片並顯示
                response = requests.get(image_url)
                image_data = response.content
                image = Image.open(io.BytesIO(image_data))
                image = image.resize((300, 300))  # 調整圖片大小
                photo = ImageTk.PhotoImage(image)
                image_label.config(image=photo)
                image_label.image = photo  # 參考圖片，避免被垃圾回收
            else:
                image_label.config(image='')
        else:
            image_label.config(image='')
    else:
        restaurant_name_label.config(text='餐廳名稱: ')
        avg_price_label.config(text='均消: ')
        opening_hours_label.config(text='營業時間: ')
        address_label.config(text='地址: ')
        image_label.config(image='')

# 隨機選擇一家餐廳並顯示資訊
def select_random_restaurant():
    random_name = random.choice(list(restaurant_info.keys()))
    selected_restaurant.set(random_name)
    show_selected_restaurant_info()

# 設定總頁數
total_pages = 28

# 建立空的餐廳資訊字典、圖片URL字典、地址字典
restaurant_info = {}
image_urls = {}
address_info = {}

# 建立 TKInter 視窗
window = tk.Tk()
window.title('龜山美食')
window.geometry('705x400')

# 設定視窗 icon
icon_path = 'icon.png'  # 替換為你的圖片路徑
window.iconphoto(True, tk.PhotoImage(file=icon_path))

# 自定義狀態標籤樣式
status_style = ttk.Style()
status_style.configure('TCombobox', font=('Consolas', 16))  # 設定字體大小
status_style.configure('TCombobox', padding=6)  # 設定高度

load_style = ttk.Style()
load_style.configure('load.TLabel', foreground='blue', font=('Microsoft JhengHei', 15, 'bold'))

# 創建狀態標籤
status_label = ttk.Label(window, text='正在抓取資料...', style='load.TLabel')
status_label.pack()

# 新增一個 GIF 圖片
gif_path = 'TYZY.gif'  # 請替換成你的 GIF 圖片路徑
gif_image = Image.open(gif_path)
# 創建圖片序列
frames = []
for frame in ImageSequence.Iterator(gif_image):
    frames.append(frame.copy())

# 創建顯示 GIF 圖片的標籤
gif_label = tk.Label(window)
gif_label.pack()

# 播放音樂
winsound.PlaySound('music.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

# 更新狀態標籤文字和顯示 GIF 圖片
window.update()

# 定義函數來更新 GIF 圖片
def update_gif(frame_index):
    gif_frame = frames[frame_index]
    gif_photo = ImageTk.PhotoImage(gif_frame)
    gif_label.config(image=gif_photo)
    gif_label.image = gif_photo  # 參考圖片，避免被垃圾回收

    # 設定下一幀的更新
    next_frame_index = (frame_index + 1) % len(frames)
    window.after(10, update_gif, next_frame_index)

# 開始更新 GIF 圖片
update_gif(0)

# 迴圈處理每一頁
for page in range(1, total_pages + 1):
    # 組合每一頁的網址
    url = base_url + '?page=' + str(page)

    # 發送請求並取得回應
    response = requests.get(url)
    html_content = response.text

    # 創建BeautifulSoup物件
    soup = BeautifulSoup(html_content, 'html.parser')

    # 使用CSS選擇器定位餐廳資料元素
    restaurant_elements = soup.find_all('div', {'class': 'jsx-1156793088 extra-info-row'})
    title_elements = soup.find_all('div', {'class': 'jsx-1156793088 title-row'})
    review_elements = soup.find_all('div', {'class': 'jsx-1156793088 review-row'})
    address_elements = soup.find_all('div', {'class': 'jsx-1156793088 address-row'})
    image_elements = soup.select('.jsx-987803290.item-list .jsx-1156793088.restaurant-info img')

    # 提取餐廳相關資料
    for restaurant_element, title_element, review_element, address_element, image_element in zip(
            restaurant_elements, title_elements, review_elements, address_elements, image_elements
    ):
        name = title_element.select_one('.title-text').text
        avg_price_element = review_element.select_one('.avg-price')
        avg_price = avg_price_element.text.strip() if avg_price_element else 'N/A'
        time = restaurant_element.select_one('.info')
        time = time.text.strip()
        address = address_element.text.strip()

        # 提取圖片URL
        data_src = image_element.get('data-src')
        src = image_element.get('src')
        image_url = data_src if data_src else src

        # 將餐廳資訊存入字典
        restaurant_info[name] = {'均消': avg_price.replace('· 均消 ', ''), '營業時間': time, '地址': address}

        # 將圖片URL存入字典
        image_urls[name] = image_url

        # 將地址存入字典
        address_info[name] = address

        window.update()

# 停止播放音樂
winsound.PlaySound(None, winsound.SND_PURGE)

# 移除狀態標籤
gif_label.pack_forget()
status_label.pack_forget()

window.geometry('700x665')
# 下拉式選單
selected_restaurant = tk.StringVar()
restaurant_combobox = ttk.Combobox(window, textvariable=selected_restaurant, state='readonly', style='TCombobox')
restaurant_combobox['values'] = list(restaurant_info.keys())
restaurant_combobox.pack(pady=10, side='top')

# 佈局框架
layout_frame = tk.Frame(window)
layout_frame.pack(pady=10, side='top')

# 顯示餐廳按鈕
show_info_button = tk.Button(layout_frame, text='顯示餐廳資訊', command=show_selected_restaurant_info, font=('Microsoft JhengHei', 13))
show_info_button.pack(side='left')


# 隨機選擇按鈕
random_button_image_path = "IMG_1829.jpg"  # 替換為您的自定義圖片路徑
random_button_image = Image.open(random_button_image_path)
random_button_image = random_button_image.resize((100, 100))  # 調整圖片大小
random_button_photo = ImageTk.PhotoImage(random_button_image)
random_button = tk.Button(layout_frame, image=random_button_photo, command=select_random_restaurant)
random_button.pack(pady=10,side='left')

# 創建餐廳資訊標籤和圖片標籤
info_frame = tk.Frame(window)
info_frame.pack(anchor='w')

restaurant_name_label = tk.Label(info_frame, text='餐廳名稱: ', font=('Microsoft JhengHei', 20, 'bold'))
restaurant_name_label.pack(anchor='w')
avg_price_label = tk.Label(info_frame, text='均消: ', font=('Microsoft JhengHei', 20, 'bold'))
avg_price_label.pack(anchor='w')
opening_hours_label = tk.Label(info_frame, text='營業時間: ', font=('Microsoft JhengHei', 20, 'bold'))
opening_hours_label.pack(anchor='w')
address_label = tk.Label(info_frame, text='地址: ', font=('Microsoft JhengHei', 20, 'bold'))
address_label.pack(anchor='w')

image_label = tk.Label(info_frame)
image_label.pack(side='left')

# 啟動視窗主迴圈
window.mainloop()

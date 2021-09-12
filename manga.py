# -*- coding: utf-8-*-
from __future__ import print_function  # 兼容 python 2
import os
import time
import sys
import requests
import json
from pprint import pprint
from index_decode import decode_index_data
comic_title = "null"
bilicookie = "null"
download_path = './manhua'


# start 判断并存储用户下载路径
haspath = os.path.isfile(r'path.txt')
print("have download path?   ", haspath)
if not haspath:
    f = open('path.txt', 'w')
    f.close()
# endif
size = os.path.getsize('./path.txt')
if size == 0:
    os.remove("path.txt")
    print('您似乎并未填写您的下载路径呢qwq\n')
    print('下载路径格式如下：盘:/文件夹或者./文件夹（支持相对路径以及绝对路径）\n注意！如果路径添加错误可以在此程序同级目录下修改path.txt中的路径\n')
    bilipath = input("您的下载路径：")
    with open("path.txt", "w") as f:
        f.write(bilipath)
    # endwith
    os.system("cls")
    p = sys.executable
    os.execl(p, p, *sys.argv)
else:
    with open("path.txt", "r") as f:
        download_path = f.readline()
    # endwith
# end 判断并存储用户下载路径


# start 判断并存储用户cookie
hascookie = os.path.isfile(r'cookie.txt')
print("have cookie?   ", hascookie)
if not hascookie:
    f = open('cookie.txt', 'w')
    f.close()
# endif
size = os.path.getsize('./cookie.txt')
if size == 0:
    os.remove("cookie.txt")
    print('您似乎并未填写您的cookie呢qwq\n')
    print('因为需要下载付费等章节需要登录，所以还请您输入您的cookie qwq\n')
    print('(您可以打开这个网站来看如何获取cookie：https://www.bwsl.wang/csother/85.html#TOC-9)\n')
    bilicookie = input("您的cookie：")
    with open("cookie.txt", "w") as f:
        f.write(bilicookie)
    # endwith
    os.system("cls")
    p = sys.executable
    os.execl(p, p, *sys.argv)
else:
    with open("cookie.txt", "r") as f:
        bilicookie = f.readline()
    # endwith
# end 判断并存储用户cookie


# start 爬虫头部声明
headers = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://manga.bilibili.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "cookie": bilicookie
}
headers_cdn = {
    'Host': 'manga.hdslb.com',
    'Origin': 'https://manga.bilibili.com',
}
# end 爬虫头部声明


def download_manga_all(comic_id: int):
    print("检测下载路径：", download_path)
    global comic_title
    url = "https://manga.bilibili.com/twirp/comic.v2.Comic/ComicDetail?device=pc&platform=web"
    res = requests.post(url,
                        json.dumps({
                            "comic_id": comic_id
                        }), headers=headers)
    data = json.loads(res.text)['data']
    comic_title = data['title']
    root_path = os.path.join(download_path, comic_title)
    root_path = root_path.replace(':', '_')
    root_path = root_path.replace(' ', '_')
    root_path = root_path.replace('：', '_')
    root_path = root_path.replace('.', '')
    if not os.path.exists("./"+root_path):
        os.makedirs("./"+root_path)
    for ep in data['ep_list']:
        if not ep['is_locked']:
            print("\n完成！\n————————————————————————————————————————")
            print('downloading ep:', ep['short_title'], ep['title'])
            download_manga_episode(ep['id'], "./"+root_path)
            pass
        pass
    pass


def download_manga_episode(episode_id: int, root_path: str):
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/GetEpisode?device=pc&platform=web',
                        json.dumps({
                            "id": episode_id
                        }), headers=headers)
    data = json.loads(res.text)
    # comic_title = data['data']['comic_title']
    short_title = data['data']['short_title']
    # title = comic_title + '_' + short_title + '_' + data['data']['title']
    title = short_title + '_' + data['data']['title']
    comic_id = data['data']['comic_id']
    print('正在下载：', title)

    # 获取索引文件cdn位置
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/GetImageIndex?device=pc&platform=web',
                        json.dumps({
                            "ep_id": episode_id
                        }), headers=headers)
    data = json.loads(res.text)
    index_url = 'https://manga.hdslb.com' + data['data']['path']
    print('获取索引文件cdn位置:', index_url)
    # 获取索引文件
    res = requests.get(index_url)
    # 解析索引文件
    pics = decode_index_data(comic_id, episode_id, res.content)
    # print(pics)
    ep_path = os.path.join(root_path, title)
    ep_path = ep_path.replace(':', '_')
    ep_path = ep_path.replace(' ', '_')
    ep_path = ep_path.replace('：', '_')
    ep_path = ep_path.replace('.', '')
    if not os.path.exists("./"+ep_path):
        os.makedirs("./"+ep_path)
    for i, e in enumerate(pics):
        url = get_image_url(e)
        print(i, e, end="\r")
        res = requests.get(url)
        with open(os.path.join("./"+ep_path, str(i) + '.jpg'), 'wb+') as f:
            f.write(res.content)
            pass
        if i % 4 == 0 and i != 0:
            time.sleep(2)
            pass
        pass
    pass


def get_image_url(img_url):
    # 获取图片token
    res = requests.post('https://manga.bilibili.com/twirp/comic.v1.Comic/ImageToken?device=pc&platform=web',
                        json.dumps({
                            "urls": json.dumps([img_url])
                        }), headers=headers)
    data = json.loads(res.text)['data'][0]
    url = data['url'] + '?token=' + data['token']
    return url
    pass


def indexes():
    mainjson = download_path+"/manga.json"
    print(mainjson)
    comictitle = str(comic_title)

    # 转换子文件夹路径为数组
    for root, dirs, files in os.walk(download_path+"/"+comictitle, topdown=False):
        with open("tmp.txt", "w+") as f:
            f.write(str(dirs).replace("\'", "").replace(
                "[", "").replace("]", ""))
    with open("tmp.txt", "r+") as f:
        filelist = f.readline()
    # if os.path.exists("tmp.txt"):  # 删除缓存文件
    #    os.remove("tmp.txt")

    filelist = filelist.split(', ')
    # end

    # 将相关数据写入json
    a = 0
    b = 0
    with open(download_path+"/"+comictitle+"/chapter.json", "w", encoding='utf-8') as f:
        f.write("[\n")
        while a < len(filelist):
            a = a + 1
            b = a - 1
            files = os.listdir(download_path+"/"+comictitle +
                               "/"+filelist[b])   # 读入文件夹
            filenum = len(os.listdir(download_path+"/" +
                          comictitle+"/"+filelist[b]))
            if a < len(filelist):
                f.write("{\n\"id\":\""+str(b)+"\",\n\"title\":\""+filelist[b]+"\",\n\"url\":\""+download_path +
                        "/"+comictitle+"/"+filelist[b]+"\",\n\"page\":\""+str(filenum)+"\"\n},\n")
            else:
                f.write("{\n\"id\":\""+str(b)+"\",\n\"title\":\""+filelist[b]+"\",\n\"url\":\""+download_path +
                        "/"+comictitle+"/"+filelist[b]+"\",\n\"page\":\""+str(filenum)+"\"\n}\n")
        f.write("]")
    # end
    if os.path.exists(mainjson):
        with open(mainjson, "r", encoding='utf-8') as f:
            text = f.read()
        with open(mainjson, "r", encoding='utf-8') as f:
            getid = json.load(f)
            getid = int(getid[-1]['id'])+1
            jsontext = ',{"title":"'+comictitle + \
                '","id":"'+str(getid)+'","page":"'+str(b)+'"}'
        with open(mainjson, "w+", encoding='utf-8') as f:
            text = text.rstrip("]")
            f.write(text)
            f.write(jsontext)
            f.write("]")
    else:
        with open(mainjson, "w+", encoding='utf-8') as f:
            f.write(
                "[{\"title\":\""+comictitle+"\",\"id\":\"1\",\n\"page\":\""+str(b)+"\"}]")
    print("索引已完成，请检查您在设置的下载目录下和漫画目录下的json文件")


if __name__ == "__main__":
    mangaid = input("要下载的漫画ID为？")
    download_manga_all(mangaid)
    indexes()

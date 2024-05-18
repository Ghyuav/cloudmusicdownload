from bs4 import BeautifulSoup
from requests import get,head
from os.path import isdir
from os import mkdir
from shutil import copy 
from sys import argv,exit
from eyed3 import load
from fake_useragent import UserAgent
from time import sleep

from rich.table import Table
import logging
from rich.logging import RichHandler
from rich import print
from rich.panel import Panel
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

table = Table(show_header=1)
table.add_column('歌曲名')
table.add_column('作曲家')
table.add_column('专辑名')

with open('cover.ini','r',encoding='utf-8') as f:
    save_path = f.read()
true = True


def main(id,path=0):
    retry = 1
    while 0<retry<6:
        try:
            # 复制文件
            
            if isdir('output'):
                pass
            else:
                mkdir('output')
            log.info('获取页面')
            ua = UserAgent()
            url = f"https://music.163.com/song?id={id}" 
            headers = {
                "User-Agent":  ua.random,

            } 
            response = get(url=url,headers=headers) 
            log.info('解析中')
            a = response.text 
            bs = BeautifulSoup(a,'html.parser')
            contents = []
            for i in bs.find_all('meta'):
                try:
                    i['property']
                    contents.append(i['content'])
                except:
                    pass
            title = contents[1]
            artist = contents[9]
            album = contents[10]
            img_url = contents[3]
            print(Panel(f"歌曲名:{title}\n歌手名:{artist}\n专辑名:{album}",title='歌曲信息'))
            save_name = f'{artist} - {title}'.replace('/',' ')

            table.add_row(title,artist,album)
            # 获取文件
            if path: # 传入路径
                copy(path,save_path+path.split('\\')[-1])
                save_name = ''
                data = path.split('\\')[-1].split('.')
                del(data[-1])
                for i in  data:
                    save_name += i
            else:
                log.info('下载音乐')
                song_url = head(f'https://music.163.com/song/media/outer/url?id={id}.mp3',headers=headers).headers['Location']
                if song_url == 'http://music.163.com/404':
                    log.error('无资源')
                else:
                    data = get(song_url,headers=headers)
                    with open(save_path+save_name+'.mp3','wb') as f:
                        f.write(data.content)
                    log.info('音乐下载成功')

            # 歌词
            log.info('下载歌词')
            data = get('https://music.163.com/api/song/media?id='+id).text
            try:
                lrc = eval(data)['lyric']
                with open(save_path+save_name+'.lrc', 'w', encoding='utf-8') as f:
                    f.write(lrc)
                log.info('歌词下载成功')
            except:
                log.error('无歌词')
            
            log.info('下载封面')
            data = get(img_url).content
            log.info('封面下载成功')

            log.info('写入信息')
            write_tags(save_name,title,artist,album,data)
            print(Panel(save_path+save_name+'.lrc'+'\n'+save_path+save_name+'.mp3',title='成功'))
            retry = -1
        except Exception as e:
            log.exception("unable print!")
            log.error(f'失败{retry}次,即将重试')
            retry += 1

    
def write_tags(save_name,title,artist,album,data):
    audioFile = load(path=save_path+save_name+'.mp3')
    audioFile.tag.artist = artist
    audioFile.tag.title = title
    audioFile.tag.album = album
    audioFile.tag.images.set(3, data, 'image/jpeg', u'Cover')
    audioFile.tag.save()



try:
    data = argv[1]
    if len(argv) > 2:
        path = argv[2]
    else:
        path = ''
except Exception as e:
    log.info(str(e))
    log.info(f'用法:\n{argv[0]} [网易云音乐歌曲id或url] [歌曲文件路径(可选)]')
    exit()

try:
    id = str(int(data))
except:
    try:
        id = data.split('id=')[1].split('&')[0]
    except Exception as e:
        log.info(str(e))
log.info('id:'+id)

main(id,path)
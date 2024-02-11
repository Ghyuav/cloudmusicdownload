from bs4 import BeautifulSoup
from requests import get,head
from os.path import isdir
from os import mkdir
from shutil import copy 
from sys import argv,exit
from eyed3 import load
from loguru import logger
from fake_useragent import UserAgent


true = True

def main(id,path=0):
    try:
        # 复制文件
        
        if isdir('output'):
            pass
        else:
            mkdir('output')
        
        logger.info('获取页面')
        ua = UserAgent()
        url = f"https://music.163.com/song?id={id}" 
        headers = {
            "User-Agent":  ua.random,

        } 
        response = get(url=url,headers=headers) 
        logger.info('解析中')
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
        save_name = f'{title} - {artist}'.replace('/',' ')

        logger.info(f'''
-----歌曲信息-----
歌曲名:{title}
作曲家:{artist}
专辑:{album}''')

        # 获取文件
        if path: # 传入路径
            copy(path,'output\\'+path.split('\\')[-1])
            save_name = ''
            data = path.split('\\')[-1].split('.')
            del(data[-1])
            for i in  data:
                save_name += i
        else:
            logger.info('下载音乐')
            song_url = head(f'https://music.163.com/song/media/outer/url?id={id}.mp3',headers=headers).headers['Location']
            if song_url == 'http://music.163.com/404':
                logger.error('无资源')
            else:
                data = get(song_url,headers=headers)
                with open('output\\'+save_name+'.mp3','wb') as f:
                    f.write(data.content)
                logger.success('音乐下载成功')

        # 歌词
        logger.info('下载歌词')
        data = get('https://music.163.com/api/song/media?id='+id).text
        try:
            lrc = eval(data)['lyric']
            with open('output\\'+save_name+'.lrc', 'w', encoding='utf-8') as f:
                f.write(lrc)
            logger.success('歌词下载成功')
        except:
            logger.info('无歌词')
        
        logger.info('下载封面')
        data = get(img_url).content
        logger.success('封面下载成功')

        logger.info('写入信息')
        write_tags(save_name,title,artist,album,data)
        logger.success('成功:'+'output\\'+save_name+'.mp3')
    except Exception as e:
        logger.error(str(e))
        logger.error('失败')

    
def write_tags(save_name,title,artist,album,data):
    audioFile = load(path='output\\'+save_name+'.mp3')
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
    logger.error(str(e))
    print(f'用法:\n{argv[0]} [网易云音乐歌曲id或url] [歌曲文件路径(可选)]')
    exit()

try:
    id = str(int(data))
except:
    try:
        id = data.split('id=')[1].split('&')[0]
    except Exception as e:
        logger.error(str(e))
logger.info('id:'+id)
main(id,path)
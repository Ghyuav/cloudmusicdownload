warning_text = '''
请下载 webdriver
edge:https://developer.microsoft.com/zh-cn/microsoft-edge/tools/webdriver/?form=MA13LH
chrome:https://googlechromelabs.github.io/chrome-for-testing/
firefox:https://github.com/mozilla/geckodriver/releases
'''

from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from requests import get,head
from os.path import isdir
from os import mkdir
from shutil import copy 
import eyed3
from loguru import logger


true = True

def main(id,path=0):
    try:
        # 复制文件
        
        if isdir('output'):
            pass
        else:
            mkdir('output')

        # 获取页面
        url = 'https://music.163.com/outchain/player?type=2&id='+id
        driver.get(url)
        sleep(2)
        logger.info('获取页面')
        a = driver.page_source
        bs = BeautifulSoup(a,'html.parser')
        name = str(bs.find(id='title')).split('>')[1].split('<')[0]
        artist = str(bs.find(id='title')).split('- ')[-1].split('<')[0]
        save_name = f'{name} - {artist}'.replace('/',' ')

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
            if head(f'https://music.163.com/song/media/outer/url?id={id}.mp3').headers['Location'] == 'http://music.163.com/404':
                logger.error('无资源')
            else:
                with open('output\\'+save_name+'.mp3','wb') as f:
                    f.write(get(f'https://music.163.com/song/media/outer/url?id={id}.mp3').content)
                logger.success('音乐下载成功')

        # 歌词
        logger.info('下载歌词')
        data = get('http://music.163.com/api/song/media?id='+id).text
        try:
            lrc = eval(data)['lyric']
            with open('output\\'+save_name+'.lrc', 'w', encoding='utf-8') as f:
                f.write(lrc)
            logger.success('歌词下载成功')
        except:
            logger.info('无歌词')
        
        logger.info('下载封面')
        data = get('https:'+str(bs.find(id='cover')).split('"')[3].split('?')[0]).content
        

        logger.info(f'''歌曲信息
        歌曲名:{name}
        作曲家:{artist}''')
        logger.info('写入信息')
        print('output\\'+save_name+'.mp3')
        write_tags(save_name,artist,name,data)
        logger.success('成功')
    except Exception as e:
        logger.error(str(e))
        logger.error('失败')

    
def write_tags(save_name,artist,name,data):
    audioFile = eyed3.load(path='output\\'+save_name+'.mp3')
    audioFile.tag.artist = artist
    audioFile.tag.title = name
    audioFile.tag.images.set(3, data, 'image/jpeg', u'Cover')
    audioFile.tag.save()

logger.info('初始化')

try:
    with open('settings.ini','r') as f:
        form = f.read()
        logger.info(form)
    if form == 'edge':
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("log-level=3")
        driver = webdriver.Edge(options=options)
    elif form == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("log-level=3")
        driver = webdriver.Chrome(options=options)
    elif form == 'firefox':
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("log-level=3")
        driver = webdriver.Firefox(options=options)
except Exception as e:
    logger.error(str(e))
    logger.warning(warning_text)
    raise Exception('初始化失败'+warning_text)

if __name__ == '__main__':
    data = input('网易云音乐歌曲id或url >')
    path = input('歌曲文件路径(可选) >')
    try:
        id = str(int(data))
    except:
        try:
            id = data.split('id=')[1].split('&')[0]
        except Exception as e:
            logger.error(str(e))

    main(id,path)
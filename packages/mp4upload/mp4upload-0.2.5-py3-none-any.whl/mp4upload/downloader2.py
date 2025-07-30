#!/usr/bin/env python

from __future__ import print_function
#from safeprint import print as sprint
import os, sys
import traceback
from make_colors import make_colors
import clipboard
from zippyshare_generator import zippyshare
from xnotify.notify import notify
import getpass
from pydebugger.debug import debug
import re
#from pause import pause
import subprocess
from configset import configset
from unidecode import unidecode
from configset import configset
import bitmath
from datetime import datetime

if sys.version_info.major == 3:
    from urllib.parse import urlparse, unquote
    raw_input = input
elif sys.version_info.major == 2:
    from urlparse import urlparse
    from urllib import unquote
elif sys.version_info.major < 2:
    print (make_colors("Version python too old !", 'lw', 'lr', attrs = ['blink', 'bold']))

logfile = os.path.join(os.path.dirname(__file__), "mp4upload.ini")
CONFIG = configset(logfile)

def logger(message, status="info"):    
    if not os.path.isfile(logfile):
        lf = open(logfile, 'wb')
        lf.close()
    real_size = bitmath.getsize(logfile).kB.value
    max_size = CONFIG.get_config("LOG", 'max_size')
    debug(max_size = max_size)
    if max_size:
        debug(is_max_size = True)
        try:
            max_size = bitmath.parse_string_unsafe(max_size).kB.value
        except:
            max_size = 0
        if real_size > max_size:
            try:
                os.remove(logfile)
            except:
                print("ERROR: [remove logfile]:", traceback.format_exc())
            try:
                lf = open(logfile, 'wb')
                lf.close()
            except:
                print("ERROR: [renew logfile]:", traceback.format_exc())

    str_format = datetime.strftime(datetime.now(), "%Y/%m/%d %H:%M:%S.%f") + " - [{}] {}".format(status, message) + "\n"
    with open(logfile, 'ab') as ff:
      ff.write(str_format)

def download_linux(url, download_path=os.getcwd(), saveas=None, cookies = {}, downloader = 'wget'):
    '''
        downloader: aria2c, wget, uget, persepolis
    '''
    if not download_path or not os.path.isdir(download_path):
        if CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()):
            download_path = CONFIG.get_config('DOWNLOAD', 'path')
    print(make_colors("DOWNLOAD_PATH (linux):", 'lw', 'bl') + " " + make_colors(download_path, 'b', 'ly'))
    aria2c = os.popen3("aria2c")
    wget = os.popen3("wget")
    persepolis = os.popen3("persepolis --help")

    if downloader == 'aria2c' and not re.findall("not found\n", aria2c[2].readlines()[0]):
        if saveas:
            saveas = '-o "{0}"'.format(saveas.encode('utf-8', errors = 'ignore'))
        cmd = 'aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas)
        os.system(cmd)
        logger(cmd)
    elif downloader == 'wget' and not re.findall("not found\n", wget[2].readlines()[0]):
        filename = ''
        if saveas:
            filename = os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')) 
            saveas = ' -O "{}"'.format(os.path.join(os.path.abspath(download_path), saveas.decode('utf-8', errors = 'ignore')))
        else:
            saveas = '-P "{0}"'.format(os.path.abspath(download_path))
            filename = os.path.join(os.path.abspath(download_path), os.path.basename(url))
        headers = ''
        header = ""
        if cookies:
            debug(cookies = cookies)
            debug(cookies_Cookie = cookies.get('Cookie'))
            if cookies.get('Cookie'):
                debug("1"*100)
                for i in cookies: headers += ' --header="' + str(i) + ": " + str(cookies.get(i)) + '"'
            else:
                debug("2"*100)
                for i in cookies: header +=str(i) + "= " + cookies.get(i) + "; "
                headers = ' --header="Cookie: ' + header[:-2] + '"'
        cmd = 'wget -c "' + url + '" {}'.format(unidecode(saveas)) + headers + " --no-check-certificate"
        print(make_colors("CMD:", 'lw', 'lr') + " " + make_colors(cmd, 'lw', 'r'))
        os.system(cmd)
        logger(cmd)
        if CONFIG.get_config('policy', 'size'):
            size = ''
            try:
                size = bitmath.parse_string_unsafe(CONFIG.get_config('policy', 'size'))
            except ValueError:
                pass
            if size and not bitmath.getsize(filename).MB.value > size.value:
                print(make_colors("REMOVE FILE", 'lw', 'r') + " [" + make_colors(bitmath.getsize(filename).kB) + "]: " + make_colors(filename, 'y') + " ...")
                os.remove(filename)

    elif downloader == 'persepolis'  and not re.findall("not found\n", persepolis[2].readlines()[0]):
        cmd = 'persepolis --link "{0}"'.format(url)
        os.system(cmd)
        logger(cmd)
    else:
        try:
            from pywget import wget as d
            d.download(url, download_path, saveas.decode('utf-8', errors = 'ignore'))
            logger("download: {} --> {}".format(url, os.path.join(download_path, saveas.decode('utf-8', errors = 'ignore'))))
        except:
            print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
            clipboard.copy(url)
            logger("download: copy '{}' --> clipboard".format(url), "error")


def normalization_name(name):
    name = re.sub("\: ", " - ", name)
    name = re.sub("\?|\*", "", name)
    name = re.sub("\:", "-", name)
    name = re.sub("\.\.\.", "", name)
    name = re.sub("\.\.\.", "", name)
    name = re.sub(" / ", " - ", name)
    name = re.sub("/", "-", name)
    name = re.sub(" ", ".", name)
    
    debug(name = name)
    return name

def normalization(name):
    name = re.sub("\: ", " - ", name)
    name = re.sub("\?|\*", "", name)
    name = re.sub("\:", "-", name)
    name = re.sub("\.\.\.", "", name)
    name = re.sub("\.\.\.", "", name)
    name = re.sub(" / ", " - ", name)
    name = re.sub("/", "-", name)
    
    debug(name = name)
    return name

def format_number(number, length = None):
    if not length:
        if len(str(number)) == 1:
            return "0" + str(number)
        else:
            return str(number)
    else:
        nums_zero = length - len(str(number))
        zero = "0" * nums_zero
        return zero + str(number)

def download_linuxx(url, download_path=os.getcwd(), saveas=None, downloader = 'aria2c'):
    '''
        downloader: aria2c, wget, uget, persepolis
    '''
    if not saveas:
        saveas = ''
    debug(url = url)
    if sys.version_info.major == 3:
        aria2c = subprocess.getoutput("aria2c")
    else:
        aria2c = os.popen3("aria2c")[2].readlines()[0]
    debug(aria2c = aria2c)
    debug(aria2c = re.findall("not found", aria2c))
    if sys.version_info.major == 3:
        wget = subprocess.getoutput("wget")
    else:
        wget = os.popen3("wget")[2].readlines()[0]
    if sys.version_info.major == 3:
        persepolis = subprocess.getoutput("persepolis --help")
    else:
        persepolis = os.popen3("persepolis --help")[2].readlines()[0]

    if downloader == 'aria2c' and not re.findall("not found", aria2c):
        if saveas:
            saveas = '-o "{0}"'.format(saveas)
        # debug(url = url)
        cmd = 'aria2c -c -d "{0}" "{1}" {2} --file-allocation=none'.format(os.path.abspath(download_path), url, saveas)
        debug(cmd = cmd)
        os.system(cmd)
    elif downloader == 'wget' or not re.findall("not found", wget):
        print("wget ..........")
        if saveas:
            saveas = '-P "{0}" -o "{1}"'.format(os.path.abspath(download_path), saveas)
        else:
            saveas = '-P "{0}"'.format(os.path.abspath(download_path))
        cmd = 'wget -c "{0}" {1} --no-check-certificate'.format(url, saveas)
        debug(cmd = cmd)
        os.system(cmd)
    elif downloader == 'persepolis'  or not re.findall("not found", persepolis):
        cmd = 'persepolis --link "{0}"'.format(url)
        debug(cmd = cmd)
        os.system(cmd)
    else:
        try:
            from pywget import wget as d
            d.download(url, download_path, saveas)
        except:
            print(make_colors("Can't Download this file !, no Downloader supported !", 'lw', 'lr', ['blink']))
            clipboard.copy(url)
            
def download(url, download_path = os.getcwd(), saveas = None, confirm = False, season = None, episode = None, ext = None, cookies = {}):
    debug(saveas = saveas)
    download_path0 = download_path
    CONFIG = configset(os.path.join(os.path.dirname(__file__), 'download.ini'))
    debug(download_path = download_path)
    if saveas:
        if not ext:
            ext = raw_input(make_colors("Extention (mp4):", 'y') + " ")
            if not ext:
                ext = "mp4"
        else:
            ext = re.split(" ", ext)[0].strip()
        saveas = saveas + " S{}E{}".format(format_number(season), format_number(episode))
        debug(saveas = saveas)
        saveas = normalization_name(saveas) + "." + ext.lower()
        debug(saveas = saveas)
        #pause()
    if not download_path:
        if os.getenv('DOWNLOAD_PATH'):
            download_path = os.getenv('DOWNLOAD_PATH')
            debug(download_path = download_path)
        if CONFIG.get_config('DOWNLOAD', 'path', os.getcwd()) and not CONFIG.get_config('DOWNLOAD', 'path', os.getcwd() == os.getcwd()):
            download_path = CONFIG.get_config('DOWNLOAD', 'path', os.getcwd())
            debug(download_path = download_path)
    
    if not os.path.isdir(download_path):
        if 'linux' in sys.platform:
            q = raw_input(make_colors('"' + os.path.realpath(download_path) + '"', 'y') + " " + make_colors("is not directory, create it ? [y/n]: ", 'lw', 'r'))
            if q and q.lower() == 'y':
                try:
                    os.makedirs(download_path)
                except:
                    os.system('mkdir -p "{}"'.format(download_path))
        elif sys.platform == 'win32':
            # q = raw_input("{} is not directory, create it ? [y/n]: ".format(os.path.realpath(download_path)))
            q = raw_input(make_colors("{} is not directory, create it ? [y/n]: ".format(make_colors(os.path.realpath(download_path)), 'lw', 'r'), 'y'))
            if q and q.lower() == 'y':
                try:
                    os.makedirs(download_path)
                except:
                    pass

    if 'linux' in sys.platform and not os.path.isdir(download_path):
        debug(download_path0 = download_path)
        if not os.path.isdir(download_path):
            this_user = getpass.getuser()
            login_user = os.getlogin()
            env_user = os.getenv('USER')
            debug(login_user = login_user)
            debug(env_user = env_user)
            this_uid = os.getuid()
            download_path = r"/home/{0}/Downloads".format(login_user)
            debug(download_path = download_path)
    
    if not os.path.isdir(download_path):
        try:
            os.makedirs(download_path)
        except:
            pass

    if not os.path.isdir(download_path):
        try:
            os.makedirs(download_path)
        except OSError:
            download_path = None
            tp, tr, vl = sys.exec_info()
            debug(ERROR_MSG = vl.__class__.__name__)
            if vl.__class__.__name__ == 'OSError':
                print(make_colors("Permission failed make dir:", 'lw', 'lr', ['blink']) + " " + make_colors(download_path, 'lr', 'lw'))

    if not download_path:
        download_path = os.getcwd()
    if not os.access(download_path, os.W_OK|os.R_OK|os.X_OK):
        print(make_colors("You not have Permission save to dir:", 'lw', 'lr' + " " + make_colors(download_path, 'lr', 'lw')))
        download_path = os.getcwd()
    print(make_colors("DOWNLOAD PATH:", 'lw', 'bl') + " " + make_colors(download_path, 'lw', 'lr'))
    print(make_colors("DOWNLOAD URL :", 'lw', 'm')  + " " + make_colors(url, 'lw', 'm'))
    #pause()
    debug(url = url)
    error = False
    try:
        clipboard.copy(url)
    except:
        pass

    if sys.platform == 'win32':
        try:
            from pyidm.idm import IDMan
            d = IDMan()
        except:
            try:
                from idm.idm import IDMan
                d = IDMan()
            except:
                from pywget import wget as d
        
    if 'racaty' in urlparse(url).netloc:
        try:
            from racaty import racaty
            url_download = racary(url)
        except:
            traceback.format_exc()
            error = True

    elif 'uptobox' in urlparse(url).netloc:
        try:
            from uptobox import Uptobox
            url_download = Uptobox(url)
        except:
            traceback.format_exc()
            error = True

    elif 'mir.cr' in urlparse(url).netloc or 'mirrored' in urlparse(url).netloc:
        try:
            from mirrored import Mirrored
            url_download = Mirrored.navigator(url)
            debug(url_download = url_download)
            return downloader(url_download, download_path0, saveas0, confirm, ext)
        except:
            traceback.format_exc()
            error = True
        
    elif 'zippyshare' in urlparse(url).netloc:
        z = zippyshare.zippyshare()
        try:
            url_download, name = z.generate(url)
            print(make_colors("DOWNLOAD URL (zippyshare) :", 'b', 'g')  + " " + make_colors(url_download, 'b', 'g'))
        except:
            print("TRACEBACK:", traceback.format_exc())
            error = True
        print(make_colors("NAME (zippyshare):", 'lw', 'bl') + " " + make_colors(str(name), 'lw', 'm'))
        
    elif 'anonfile' in urlparse(url).netloc:
        try:
            import anonfile
            a = anonfile.anonfile()
            url_download = a.generate(url)
            debug(url_download = url_download)
            if sys.platform == 'win32':
                d.download(url_download, download_path, saveas, confirm = confirm)
            else:
                download_linux(url_download, download_path, saveas)
            return url
        except:
            traceback.format_exc()
            error = True
    elif 'mediafire' in urlparse(url).netloc:
        try:
            from mediafire import mediafire
            a = mediafire.Mediafire()
            url_download = a.hard_download(url)
            debug(url_download = url_download)
        except:
            traceback.format_exc()
            error = True
    if error:
        clipboard.copy(url)
        print(make_colors("[ERROR]", 'lw', 'r') + " " + make_colors("copy URL to clipboard", 'y'))
    else:
        if not saveas and name:
            saveas = name
        if not ext and name:
            try:
                if len(os.path.splitext(name)) > 1:
                    ext = os.path.splitext(name)[1]
                    if saveas:
                        saveas = saveas + ext
                        debug(saveas = saveas)
            except:
                pass
        if not ext and not name:
            ext = os.path.splitext(os.path.split(download_url)[-1]).lower()
            if ext in [".mp4", ".mkv", ".avi"]:
                name = os.path.split(download_url)[-1]
        if ext and saveas:
            if not os.path.splitext(saveas)[1].lower() in [".mp4", ".mkv", ".avi"]:
                saveas = saveas + "." + str(ext).lower()
        
        debug(saveas = saveas)
        print(make_colors("SAVEAS:", 'lw', 'bl') + " " + make_colors(saveas, 'lw', 'r'))
        debug(url_download = url_download)
        debug(download_path = download_path)
        # sys.exit()
        if sys.platform == 'win32':
            d.download(url_download, download_path, saveas, confirm = confirm)
        else:
            download_linux(url_download, download_path, saveas, cookies)
    
    icon = None
    if os.path.isfile(os.path.join(os.path.dirname(__file__), 'logo.png')):
        icon = os.path.join(os.path.dirname(__file__), 'logo.png')
    
    if sys.platform == 'win32':
        notify.send("Download start: ", saveas, "Meownime", "downloading", iconpath = icon)    
    else:
        notify.send("Download finish: ", saveas, "Meownime", "finish", iconpath = icon)
            
    return url


def download_commas(list_commas, all_episode, provider = 'zippyshare', quality = '480p', download_path=os.getcwd(), pcloud=False, use_proxy=False):
    if not provider:
        provider = input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
    if not quality:
        quality = input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
    if not provider:
        provider = 'zippyshare'
    if not quality:
        quality = '480p'
    downloads = []
    for i in list_commas:
        downloads.append(all_episode[int(i)-1])
    for d in downloads:
        for q in d:
            for p in d.get(q):
                if provider.lower() in p and quality in q.lower():
                    debug(download_path=download_path)
                    print("download_path =", download_path)
                    url = d.get(q).get(p)
                    debug(url = url)
                    download(url, download_path)
                
#def download_alls(all_episode, download_path=os.getcwd(), pcloud=False, use_proxy=False, qs3 = None, qs4 = None):
    #debug()
    #if not qs3:
        #qs3 = input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
    #if not qs4:
        #qs4 = input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
    #if not len(qs3) > 2:
        #qs3 = input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
    #if not len(qs4) > 2:
        #qs4 = input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
    #if not qs3:
        #qs3 = 'zippyshare'
    #if not qs4:
        #qs4 = '480p'
    #debug(qs3 = qs3)
    #debug(qs4 = qs4)
    #debug(all_episode = all_episode)
    #for i in all_episode:
        #downloads, episodes, infos = get_anime_details(i.get('url'))
        #debug(downloads = downloads)
        #debug(episodes = episodes)
        #debug(infos = infos)
        #for d in downloads:
            #if d.get('name').strip().lower() == qs3.lower() and qs4 in d.get('quality').lower():
                # #generated = agl.generate(d.get('link'), True, direct_download=True, download_path=download_path, pcloud=pcloud, use_proxy=use_proxy)
                # #debug(generated = generated)
                #if 'http' in generated:
                    #pass
                #elif 'https' in generated:
                    #pass
                #else:
                    #if generated == False:
                        #qs3 = input(make_colors("Download Provider (zippyshare): ", 'lightwhite', 'lightred'))
                        #qs4 = input(make_colors("Download Provider (480p): ", 'lightwhite', 'lightmagenta'))
                        #return download_alls(all_episode, download_path, pcloud, use_proxy, qs3, qs4)

if __name__ == '__main__':
    cookies = {'Sec-Fetch-User': '?1', 'Accept-Language': 'en-US,en;q=0.9,id;q=0.8,ru;q=0.7', 'Accept-Encoding': 'gzip, deflate, br', 'Sec-Fetch-Site': 'same-site', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36', 'Connection': 'keep-alive', 'Referer': 'https://mp4upload.com/6wqrupq4c2tc', 'Sec-Fetch-Mode': 'navigate', 'Cache-Control': 'max-age=0', 'Cookie': 'lang=english; aff=148106', 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document'}
    url = "https://s1.mp4upload.com:282/d/qsx7jnwtz3b4quuoxwxuyjkrkpsp6u6b4mveu7vqexkxsu7togj5f22m/AnimeSail.com_3bb34_211124__H3r0m4n_3p07.mp4"
    download_linux(url, "/mnt/sda2/MOVIES/ANIMES/Heroman/Season 1/", "Heroman.S01E07.mp4", cookies = cookies)


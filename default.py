# -*- coding: utf-8 -*-
import urllib
import re
import os
import sys
import time
from parseutils import read_page
from stats import STATS
from datetime import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon

_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
addon = xbmcaddon.Addon('plugin.video.dmd-czech.huste')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
__settings__ = xbmcaddon.Addon(id='plugin.video.dmd-czech.huste')
home = __settings__.getAddonInfo('path')
REV = os.path.join(profile, 'list_revision')
icon = xbmc.translatePath(os.path.join(home, 'icon.png'))
nexticon = xbmc.translatePath(os.path.join(home, 'nextpage.png'))
fanart = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))


def OBSAH():
    # addDir('Hudba','http://hudba.huste.tv',0,1,icon)
    addDir('Aktuálne', 'https://huste.joj.sk/', 0, 12, icon)
    addDir('Archív', 'https://huste.joj.sk/archiv', 0, 4, icon)
    # addDir('Relácie a seriály','http://zabava.huste.tv',0,4,icon)
    # addDir('Hlášky','http://hlasky.huste.tv',0,4,icon)
    # addDir('Sport Live & Archiv(BETA)','http://www.huste.tv/services/CurrentLive.xml?nc=6946',0,11,icon)


def KATEGORIE(url):
    doc = read_page(url)
    items = doc.findAll('div', {'class': 'e-dropdown-list'})[1]
    for item in items.findAll('li'):
        name = item.getText(" ").encode('utf-8')
        url2 = item.a['href']
        addDir(name, url2, 1, 7, icon)


def NAZEV(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-list-simple')
    for item in items.findAll('li'):
        name = item.a['title'].encode('utf-8')
        url = str(item.a['href'])
        addDir(name, url, 7, icon)


def INDEX(url, page):
    doc = read_page(url + '/strana-' + str(page))
    items = doc.findAll('article')
    for item in items:
        title = item.find('h3').a['title'].encode('utf-8')
        thumb = item.img['data-original']
        for subitem in item.findAll('a'):
            try:
                subitem['class']
            except:
                break
            name = '%s (%s)' % (title, subitem.getText().encode('utf-8'))
            url2 = subitem['href']
            print(name, url2, 0, 10, thumb)
            addDir(name, url2, 0, 10, thumb)
    page = page + 1
    addDir('>> Další strana', url, page, 7, nexticon)


def INDEX_NEW(url):
    doc = read_page(url)
    items = doc.findAll('div', attrs={'class': 'w-articles'})
    for item in items:
        for item2 in item.findAll('h3'):
            if not item2.parent.parent.parent.find(attrs={'class': 'icon icon-play'}):
                continue

            title = item2.a['title'].encode('utf-8')
            thumb = item2.parent.parent.img['data-original']
            name = title
            url = item2.a['href']
            print(name, url, 0, 10, thumb)
            addDir(name, url, 0, 10, thumb)


def LIVE(url):
    doc = read_page(url)
    zapasy = doc.find('events')
    for zapas in zapasy.findAll('event'):
        title = str(zapas['title'].encode('utf-8'))
        nahled = str(zapas['large_image'])
        cas = str(zapas['starttime'])
        cas = cas.replace("+01:00", "")
        if hasattr(datetime, 'strptime'):
            # python 2.6
            strptime = datetime.strptime
        else:
            # python 2.4 equivalent
            strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
        try:
            cas = strptime(cas, '%Y-%m-%dT%H:%M:%S')
            cas = cas.strftime('%d.%m. %H:%M')
        except:
            cas = ""
        archiv = str(zapas['archive'])
        link = str(zapas['url'])
        # print title,nahled,cas,archiv,link
        try:
            soubory = zapas.find('files')
            for soubor in soubory.findAll('file'):
                rtmp_url = str(soubor['url'])
                kvalita = str(soubor['quality'])
                rtmp_cesta = str(soubor['path'])
                # print rtmp_url,kvalita,rtmp_cesta
            server = re.compile('rtmp://(.+?)/').findall(rtmp_url)
            tcurl = 'rtmp://'+server[0]
            swfurl = 'http://c.static.huste.tv/fileadmin/templates/swf/HusteMainPlayer.swf'
            if archiv == "1":
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true'
                name = 'Záznam - ' + cas + ' ' + title
            else:
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true  live=true'
                name = 'Live - ' + cas + ' ' + title
            addLink(name, rtmp_url, nahled, name)
        except:
            name = 'Nedostupné - ' + cas + ' ' + title
            addLink(name, '', nahled, name)
            continue


def VIDEOLINK(url, name):
    doc = read_page(url)
    embed = doc.find('div', {'class': 'e-embed'}).a['data-video-url']
    print('embed is %s' % embed)
    doc = read_page(embed)
    thumb = doc.find('meta', {'property': 'og:image'})['content']
    title = doc.find('title').getText()
    media_links = re.findall(r'(https://nn.+mp4)', str(doc.findAll('script')),
                             re.M)
    print('media_links: %s' % media_links)
    for media_link in media_links:
        name = '%s (%s)' % (title, re.search('-([0-9]+p)\.mp4$',
                                             media_link).group(1))
        addLink(name, media_link, thumb, name)


def get_params():
        param = []
        paramstring = sys.argv[2]
        if len(paramstring) >= 2:
                params = sys.argv[2]
                cleanedparams = params.replace('?', '')
                if (params[len(params)-1] == '/'):
                        params = params[0:len(params)-2]
                pairsofparams = cleanedparams.split('&')
                param = {}
                for i in range(len(pairsofparams)):
                        splitparams = {}
                        splitparams = pairsofparams[i].split('=')
                        if (len(splitparams)) == 2:
                                param[splitparams[0]] = splitparams[1]
        return param


def addLink(name, url, iconimage, popis):
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": popis})
        liz.setProperty("Fanart_Image", fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
        return ok


def addDir(name, url, page, mode, iconimage):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&page="+str(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo(type="Video", infoLabels={"Title": name})
        liz.setProperty("Fanart_Image", fanart)
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u,
                                         listitem=liz, isFolder=True)
        return ok


params = get_params()
url = None
page = None
name = None
thumb = None
mode = None

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        page = int(params["page"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass

print("Mode: " + str(mode))
print("URL: "+str(url))
print("Page: "+str(page))
print("Name: "+str(name))

if mode is None or url is None or len(url) < 1:
        print()
        STATS("OBSAH", "Function")
        OBSAH()

elif mode == 4:
        print("" + url)
        STATS("KATEGORIE", "Function")
        KATEGORIE(url)

elif mode == 5:
        print("" + url)
        STATS("ABC", "Function")
        ABC(url)

elif mode == 6:
        print("" + url)
        STATS("NAZEV", "Function")
        NAZEV(url)

elif mode == 7:
        print("" + url)
        print("" + str(page))
        STATS("INDEX", "Function")
        INDEX(url, page)

elif mode == 11:
        print("" + url)
        STATS("LIVE", "Function")
        LIVE(url)

elif mode == 10:
        print("" + url)
        STATS(name, "Item")
        VIDEOLINK(url, name)

elif mode == 12:
        print("" + url)
        STATS("INDEX_NEW", "Function")
        INDEX_NEW(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

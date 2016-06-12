# -*- coding: utf-8 -*-
import urllib2,urllib,re,os,time
from parseutils import *
from stats import *
from urlparse import urlparse
from datetime import datetime
import xbmcplugin,xbmcgui,xbmcaddon
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
addon = xbmcaddon.Addon('plugin.video.dmd-czech.huste')
profile = xbmc.translatePath(addon.getAddonInfo('profile'))
__settings__ = xbmcaddon.Addon(id='plugin.video.dmd-czech.huste')
home = __settings__.getAddonInfo('path')
REV = os.path.join( profile, 'list_revision')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
nexticon = xbmc.translatePath( os.path.join( home, 'nextpage.png' ) )
fanart = xbmc.translatePath( os.path.join( home, 'fanart.jpg' ) )

def OBSAH():
    #addDir('Hudba','http://hudba.huste.tv',0,1,icon)
    addDir('Šport','http://sport.huste.tv',0,4,icon)
    addDir('Relácie a seriály','http://zabava.huste.tv',0,4,icon)    
    addDir('Hlášky','http://hlasky.huste.tv',0,4,icon)
    addDir('Sport Live & Archiv(BETA)','http://www.huste.tv/services/CurrentLive.xml?nc=6946',0,11,icon)     

    
def PROUZEK(url):
    doc = read_page(url)
    items = doc.find('select', 'j-selectmenu')
    for item in items.findAll('option'):
        name = item.getText(" ").encode('utf-8')
        url2 = url+str(item['value'])
        addDir(name,url2,0,7,icon)

        
def NAZEV(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-list-simple')
    for item in items.findAll('li'):
        name = item.a['title'].encode('utf-8')
        url = str(item.a['href']) 
        addDir(name,url,7,icon)

    
def INDEX(url,page):
    
    doc = read_page(url+'?page='+str(page))
    items = doc.find('div', 'b-body')
    for item in items.findAll('li','i collapse'):
            title = item.a['title'].encode('utf-8')
            interpret = item.find('p')
            interpret = interpret.getText(" ").encode('utf-8')
            url2 = str(item.a['href']) 
            thumb = str(item.img['src'])   
            name = title+' - '+interpret
            if re.search('http', url2, re.U):
                addDir(name,url2,0,10,thumb)
            else:
                cast_url = urlparse(url)
                url2 = 'http://'+cast_url[1] + url2
                addDir(name,url2,0,10,thumb)
    page = page + 1
    addDir('>> Další strana',url,page,7,nexticon)



def LIVE(url):
    doc = read_page(url)
    zapasy = doc.find('events')
    for zapas in zapasy.findAll('event'):
        title = str(zapas['title'].encode('utf-8'))
        nahled = str(zapas['large_image'])
        cas = str(zapas['starttime'])
        cas = cas.replace("+01:00", "");
        if hasattr(datetime, 'strptime'):
            #python 2.6
            strptime = datetime.strptime
        else:
            #python 2.4 equivalent
            strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
        try:
            cas = strptime(cas, '%Y-%m-%dT%H:%M:%S')
            cas = cas.strftime('%d.%m. %H:%M')
        except:
            cas = ""
        archiv = str(zapas['archive'])
        link = str(zapas['url'])
        #print title,nahled,cas,archiv,link
        try:
            soubory = zapas.find('files')
            for soubor in soubory.findAll('file'):
                rtmp_url = str(soubor['url'])
                kvalita = str(soubor['quality'])
                rtmp_cesta = str(soubor['path'])
                #print rtmp_url,kvalita,rtmp_cesta
            server = re.compile('rtmp://(.+?)/').findall(rtmp_url)
            tcurl = 'rtmp://'+server[0]
            swfurl = 'http://c.static.huste.tv/fileadmin/templates/swf/HusteMainPlayer.swf'
            if archiv == "1":
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true'  
                name = 'Záznam - ' + cas + ' ' + title
            else:
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true  live=true'
                name = 'Live - ' + cas + ' ' + title
            print name,rtmp_url,nahled
            addLink(name,rtmp_url,nahled,name)
        except:
            name = 'Nedostupné - ' + cas + ' ' + title
            addLink(name,'',nahled,name)
            continue
                
def VIDEOLINK(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    print ('url is %s' % url)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    cast_url = urlparse(url)
    print ('casturl is %s' % cast_url[1])
    #videoid = re.compile('videoId=(.+?)&').findall(httpdata)
    videoid = re.compile('''clipId': *([0-9]+?),''').findall(httpdata)
    playlisturl = 'http://'+cast_url[1]+'/services/Video.php?clip='+videoid[0]
    print playlisturl
    doc = read_page(playlisturl)
    title = str(doc.event['title'].encode('utf-8'))    
    thumb = str(doc.event['image'])    
    items = doc.find('files')
    for item in items.findAll('file'):
        link = str(item['url'])    
        cesta = str(item['path'])
        kvalita = str(item['label'])             
        server = re.compile('rtmp://(.+?)/').findall(link)
        name = kvalita+ ' - ' + title
        tcurl = 'rtmp://'+server[0]
        swfurl = 'http://b.static.huste.tv/fileadmin/templates/swf/HusteMainPlayer.swf'
        rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'  
        print name,rtmp_url,thumb[0]
        addLink(name,rtmp_url,thumb[0],name)



def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param



def addLink(name,url,iconimage,popis):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": popis} )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok

def addDir(name,url,page,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&page="+str(page)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
params=get_params()
url=None
page=None
name=None
thumb=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        page=int(params["page"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Page: "+str(page)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        STATS("OBSAH", "Function")
        OBSAH()

elif mode==4:
        print ""+url
        STATS("PROUZEK", "Function")
        PROUZEK(url)

elif mode==5:
        print ""+url
        STATS("ABC", "Function")
        ABC(url)

elif mode==6:
        print ""+url
        STATS("NAZEV", "Function")
        NAZEV(url)

elif mode==7:
        print ""+url
        print ""+str(page)
        STATS("INDEX", "Function")
        INDEX(url,page)


elif mode==11:
        print ""+url
        STATS("LIVE", "Function")
        LIVE(url)
        
elif mode==10:
        print ""+url
        STATS(name, "Item")
        VIDEOLINK(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))

from datetime import datetime, timedelta
import os,sys,html2text,cv2
import urllib.parse
import html,re,time,json
import markdown
import rg
from bs4 import BeautifulSoup as bs

n=0

l='https://www.ukrinform.ua/block-lastnews?page='
l2='https://www.ukrinform.ua'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
hl=[]
if not os.path.exists('000000.list'):
    for a in range(5):
        h=rg.rget('%s%d'%(l,a)).text
        s=bs(h,'html.parser')
        i=s.find('section',{'class':'restList'})
        a0=i.find('div',{'class':'rest'})
        aa=i.find_all('article',{'data-id':True})
        o=[a0]if a0 else[]
        o.extend(aa)
        o=['%s%s'%(l2,u)if'http'not in u else u for b in o if'https://t.me/'not in(u:=b.find('a').get('href'))]
        hl.extend(o)
        f=open('%s.list'%(str(a).rjust(6).replace(' ','0')),'w+');f.write(json.dumps(o));f.close()
else:
    fl=[]
    for a in os.walk(sys.path[0]):
        for b in a[2]:
            if a[0]==sys.path[0]:
                if b[-4:]=='list':
                    fl.append([int(b[:-5]),'%s/%s'%(a[0],b)])
    fl.sort(key=lambda x:x[0])
    fl=[a[1]for a in fl]
    for a in fl:
        f=open(a,'r');h=json.loads(f.read());f.close()
        hl.extend(h)
print('\n'.join([json.dumps(a)for a in hl]))



if not os.path.exists('JSON-src'):os.mkdir('JSON-src')
dr=os.listdir('JSON-src')
if len(dr)==0:
    nn=0
    ed=''
    for a in range(len(hl)):
        h=rg.rget(hl[a]).text
        print(hl[a])
        s=bs(h,'html.parser')
        i0=s.find('img',{'class':'newsImage'}).get('src')
        t=s.find('article',{'class':'news'}).find('div',{'class':'newsText'})
        t='<img src="%s"></img>\n%s'%(i0,t)
        #title,type,description,published time,modified time,author,publisher,tags,source,text,images
        ms=['og:title','og:type','og:description']
        h={b.split(':')[1].replace('_',' ').replace('\n',' '):s.find('meta',{'property':b}).get('content')for b in ms}
        j=s.find('script',{'type':'application/ld+json'}).string.strip().replace('\r','').replace('\n','')
        j=eval(j.replace('null','None'))
        k={'published time':'datePublished',
           'modified time':'dateModified',
           'author':['author',['name','@type']],
           'publisher':['publisher',['name','@type']]}
        for b in k.keys():
            if isinstance(k[b],str):
                h[b]=j[k[b]]
            else:
                h[b]='%s (%s)'%(j[k[b][0]][k[b][1][0]],j[k[b][0]][k[b][1][1]])
        ha={'tags':[b.string for b in v.find_all('a',{'class':'tag'})]if(v:=s.find('aside',{'class':'tags'}))else None,
            'source':hl[a]}
        h.update(ha)

        ls={'a':'href','img':'src'}
        s=bs(i['text'],'html.parser')
        for c in ls.keys():
            ss=s.find_all(c)
            for b in ss:
                v=b.find_all()
                co=b.contents
                n=s.new_tag(c)
                u=b.get(ls[c])
                if not u:continue
                n[ls[c]]='%s%s'%(l2,u)if(u[0]in['/','.'])and('http'not in u)else u
                n.extend(v)
                n.contents=co
                b.replace_with(n)

        invalid_tags=['div']
        for tag in invalid_tags: 
            for match in s.findAll(tag):
                match.replaceWithChildren()

        for tag in s.find_all(['section']):
            p_tag = s.new_tag('p')
            tag.replace_with(p_tag)
            p_tag.contents=tag.contents

        im=[b.get('src').split('?')[0].replace('\n','')for b in s.find_all('img')]
        nim=[]
        for b in im:
            if b not in nim:nim.append(b)
        h['images']=nim
        h['text']=re.sub('\\n{2,}','\\n',str(s.prettify()).strip())
        dd=h['published time']
        if dd<d:break
        if not os.path.exists(pa:='JSON-src/%s.json'%h['published time']):
            print(h)
            f=open(pa,'w+');f.write(json.dumps(h));f.close()
        else:
            if'up'in locals():
                if h['text']!=up:
                    while True:
                        nn+=1
                        h['published time']='%sT%s:%s'%(h['published time'].split('T')[0],
                                                      str(int(h['published time'].split('T')[1].split(':')[0])-nn),
                                                      ':'.join(h['published time'].split('T')[1].split(':')[1:]))
                        if not os.path.exists(pa:='JSON-src/%s.json'%h['published time']):
                            break
                    print(h)
                    f=open(pa,'w+');f.write(json.dumps(h));f.close()
                else:print(h['published time'],'已经完成下载。')
        nn+=1
        up=h['text']

if not os.path.exists('Images'):os.mkdir('Images')
imgs=[]
for a in os.walk('JSON-src'):
    for b in a[2]:
        f=open('JSON-src/%s'%b,'r');h=json.loads(f.read());f.close()
        imgs.append([h['published time'].replace(':','-').replace('+','-'),h['images']])
for a in imgs:
    for z in a[1]:
        if not os.path.exists(pa:='Images/%s/%s'%(a[0],urllib.parse.unquote(z).split('/')[-1].split('?')[0])):
            if not os.path.exists(pa2:='/'.join(pa.split('/')[:-1])):
                os.makedirs(pa2)
            try:im=rg.rget(z,st=True).content
            except:continue
            f=open(pa,'wb+');f.write(im);f.close()
            print(pa,'下载完毕。')
        else:print(pa,'已经完成下载。')
if not os.path.exists('ConvertedIMGs'):os.mkdir('ConvertedIMGs')
for a in os.walk('Images'):
    for b in a[2]:
        if'.webp'==b[-5:]:
            if not os.path.exists(pa:='%s/%s'%(a[0].replace('Images','ConvertedIMGs'),b.replace('.webp','.png'))):
                if not os.path.exists(pa2:='/'.join(pa.split('/')[:-1])):
                    os.makedirs(pa2)
                im=cv2.imread('%s/%s'%(a[0],b))
                cv2.imwrite(pa,im)
                print(pa,'转换完毕。')
            else:
                print(pa,'已经完成转换。')

hp=html2text.HTML2Text()
if not os.path.exists('MDs'):os.mkdir('MDs')
if not os.path.exists('HTMs'):os.mkdir('HTMs')
for a in os.walk('JSON-src'):
    for b in a[2]:
        t=''
        f=open('%s/%s'%(a[0],b));h=json.loads(f.read());f.close()
        s=bs(h['text'],'html.parser')
        ss=s.find_all('img')
        for c in ss:
            n=s.new_tag('img')
            u=c.get('src')
            n['src']=u.replace('\n','').replace('/'.join(u.replace('\n','').split('/')[:-1]),('../Images/%s'%h['published time'].replace(':','-').replace('+','-')if'.webp'not in u else'../ConvertedIMGs/%s'%h['published time'].replace(':','-').replace('+','-')).split('?')[0]).replace('.webp','.png').split('?')[0]
            c.replace_with(n)
        t=re.sub('\\n{2,}','\\n',str(s.prettify()))
        t=hp.handle(t)
        t='\n\n'.join([z.replace('\n','').strip()for z in t.split('\n\n')if z])
        #title,type,description,published time,modified time,author,publisher,tags,source,text,images
        t='''# %s

Authors: %s

Publisher: %s

Published Time: %s

Modified Time: %s

Description: %s

Images: %s

Tags: %s

Type: %s

<!--METADATA-->

%s

Source: %s'''%(h['title'],
               h['author'],
               h['publisher'],
               h['published time'],
               h['modified time'],
               h['description'],
               repr(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['images']]),
               repr([z for z in h['tags']])if h['tags']else None,
               h['type'].title(),
               t,
               '[%s](%s)'%(h['source'],h['source']))
        if not os.path.exists(pa1:='MDs/%s.md'%b.split('.json')[0]):
            f=open(pa1,'w+');f.write(t);f.close()
            print(h['published time'],'转换为MD完毕。')
        else:print(h['published time'],'已经转换为MD。')
        if not os.path.exists(pa:='HTMs/%s.htm'%b.split('.json')[0]):
            f=open(pa,'w+');f.write(markdown.markdown(t));f.close()
            print(h['published time'],'转换为HTM完毕。')
        else:print(h['published time'],'已经转换为HTM。')

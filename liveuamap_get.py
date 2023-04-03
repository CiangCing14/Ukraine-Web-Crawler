from datetime import datetime, timedelta
import os,sys,html2text,cv2
import urllib.parse
import html,re,time,json
import markdown
import rg
from bs4 import BeautifulSoup as bs

n=0

l='https://liveuamap.com/ajax/do?act=prevday&id='
l2='https://liveuamap.com'
d=str(datetime.today()-timedelta(days=1)).split(' ')[0]
hl=[]
if not os.path.exists('000000.list'):
    for a in range(6):
        h=rg.rget(l2 if a==0 else'%s%s'%(l,nid)).text
        if not os.path.exists('test.txt'):f=open('test.txt','w+');f.write(h);f.close()
        if a==0:
            s=bs(h,'html.parser')
            i=[b.get('id').split('-')[1]for b in s.find('div',{'id':'feedler','class':'scrotabs'}).select('div[id*="post-"][class*="event"][data-link*="http"]')]
            i.sort()
            nid=str(int(i[-1])+1)
            print('已获取初始ID为：%s'%nid)
            continue
        h=json.loads(rg.rget('%s%s'%(l,nid)).text)
        i=[{'id':int(b['id']),
            'time':b['timestamp'],
            'location':b['location'],
            'name':b['name'],
            'lat':b['lat'],
            'lng':b['lng'],
            'lang':b['lang'],
            'url':b['link']}
            for b in h['venues']]
        i.sort(reverse=True,key=lambda x:x['id'])
        for x in range(len(i)):
            for z in i[x].keys():
                i[x][z]=i[x][z].strip()if isinstance(i[x][z],str)else i[x][z]
        nid=i[-1]['id']
        print('已爬取ID为：%s'%nid)
        hl.extend(i)
        f=open('%s.list'%(str(a-1).rjust(6).replace(' ','0')),'w+');f.write(json.dumps(i));f.close()
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
        i=hl[a]
        t=rg.rget(i['url']).text
        s=bs(t,'html.parser')
        i['text']=str(s.find('div',{'class':'popup-text'}))
        i['videos']=[]
        vs=[v for v in s.select('div[class*=video]')if v.find('iframe')]
        lvs=len(vs)
        ni=0
        for d in vs:
            ni+=1
            nn=s.new_tag('a')
            ur=d.select('iframe[src*="http"]').get('src')
            if not ur:continue
            i['videos'].append(ur)
            nn.string='Video-%s-Link：%s'%(str(ni).rjust(len(str(lvs))).replace(' ','0'),ur)
            nn['href']=ur
            d.replace_with(nn)
        i['tags']=[d.string[1:]for d in ts.find_all('a')]if(ts:=s.find('div',{'class':'tagas'}))else[]
        print(hl[a])
        i['source']=s.find('div',{'class':'head_popup'}).find('a',{'class':'source-link'}).get('href')
        ll=[]
        for x in i['videos']:
            if x not in ll:
                ll.append(x)
        i['videos']=ll.copy()

        ls={'a':'href','img':'src'}
        s=bs(i['text'],'html.parser')
        for c in ls.keys():
            ss=s.find_all(c)
            for b in ss:
                n=s.new_tag(c)
                u=b.get(ls[c])
                n[ls[c]]='%s%s'%(l2,u)if(u[0]in['/','.'])and('http'not in u)else u
                b.replace_with(n)

        deleted_tags=['map_link_par']
        td=s.find('div',{'class':deleted_tags})
        # 删除标签及其后面的所有标签
        next_siblings = td.find_next_siblings()
        for sibling in next_siblings:
            sibling.decompose()

        s.find('div',{'class':'marker-time'}).decompose()

        # 删除标签本身
        td.decompose()

        invalid_tags=['popup_video','popup_imgi','popup-text']
        for tag in invalid_tags:
            for match in s.findAll('div',{'class':tag}):
                match.replaceWithChildren()

        rmt=['h1','h2','h3','h4','h5']
        for z in rmt:
            for x in s.findAll(z):
                n=s.new_tag('p')
                n.string=x.string
                x.replace_with(n)

        im=[b.get('src').split('?')[0].replace('\n','')for b in s.find_all('img')]
        nim=[]
        for b in im:
            if b not in nim:nim.append(b)
        i['images']=nim
        i['text']=re.sub('\\n{2,}','\\n',str(s.prettify()).strip())
        t=datetime.fromtimestamp(i['time'])
        i['time']=t.strftime("%Y-%m-%dT%H:%M:%S")
        dd=i['time']
        if dd<d:break
        for z in i.keys():
            i[z]=i[z].strip()if isinstance(i[z],str)else i[z]
        if not os.path.exists(pa:='JSON-src/%s.json'%i['time']):
            print(i)
            f=open(pa,'w+');f.write(json.dumps(i));f.close()
        else:
            if'up'in locals():
                if i['text']!=up:
                    while True:
                        nn+=1
                        i['time']='%sT%s:%s'%(i['time'].split('T')[0],
                                                      str(int(i['time'].split('T')[1].split(':')[0])-nn),
                                                      ':'.join(i['time'].split('T')[1].split(':')[1:]))
                        if not os.path.exists(pa:='JSON-src/%s.json'%i['time']):
                            break
                    print(h)
                    f=open(pa,'w+');f.write(json.dumps(i));f.close()
                else:print(i['time'],'已经完成下载。')
        nn+=1
        up=i['text']



if not os.path.exists('Images'):os.mkdir('Images')
imgs=[]
for a in os.walk('JSON-src'):
    for b in a[2]:
        f=open('JSON-src/%s'%b,'r')
        hh=f.read()
        print(hh)
        h=json.loads(hh)
        f.close()
        imgs.append([h['time'].replace(':','-').replace('+','-'),h['images']])
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
            n['src']=u.replace('\n','').replace('/'.join(u.replace('\n','').split('/')[:-1]),('../Images/%s'%h['time'].replace(':','-').replace('+','-')if'.webp'not in u else'../ConvertedIMGs/%s'%h['time'].replace(':','-').replace('+','-')).split('?')[0]).replace('.webp','.png').split('?')[0]
            c.replace_with(n)
        t=re.sub('\\n{2,}','\\n',str(s.prettify()))
        t=hp.handle(t)
        t='\n\n'.join([z.replace('\n','').strip()for z in t.split('\n\n')if z])
        #name,id,time,location,lat,lng,lang,url,text,videos,tags,source,images
        t='''# %s

Authors: liveuamap (Language: %s)

Time: %s

Location: %s (Latitude:%s Longtitude:%s)

Videos: %s

Images: %s

Tags: %s

ID: %d

<!--METADATA-->

%s

News Collection Link: %s

Source: %s'''%('%s...'%u[:96-3]if len(u:=h['name'])>96 else u,
               h['lang'],
               h['time'],
               h['location'],h['lat'],h['lng'],
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['videos']]),
               json.dumps(['[%s](%s)'%('%s...'%u[:13]if len(u:=c.split('/')[-1])>16 else u,c)for c in h['images']]),
               json.dumps(h['tags']),
               h['id'],
               t,
               '[%s](%s)'%(h['url'],h['url']),
               '[%s](%s)'%(h['source'],h['source']))
        if not os.path.exists(pa1:='MDs/%s.md'%b.split('.json')[0]):
            f=open(pa1,'w+');f.write(t);f.close()
            print(h['time'],'转换为MD完毕。')
        else:print(h['time'],'已经转换为MD。')
        if not os.path.exists(pa:='HTMs/%s.htm'%b.split('.json')[0]):
            f=open(pa,'w+');f.write(markdown.markdown(t));f.close()
            print(h['time'],'转换为HTM完毕。')
        else:print(h['time'],'已经转换为HTM。')

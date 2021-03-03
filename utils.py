from pymediainfo import MediaInfo
from datetime import datetime
import os, requests, json, random, subprocess, base64
from smms import *

def getmetainfo(doubanid):
    params = (
        ('url', f'https://movie.douban.com/subject/{doubanid}'),
    )
    response = requests.get('https://api.rhilip.info/tool/movieinfo/gen', params=params)
    metainfo=json.loads(response.content.decode("utf-8"))
    return metainfo
class nullabledict:
    def __init__(self, input_dict):
        self.data=input_dict
    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        else: return "?"
    def __contains__(self, key):
        if key in self.data: return True
        else : return False

def generate_videoinfo(filename, logname="", src=""):
    media_info = MediaInfo.parse(filename)
    for t in media_info.video_tracks:
        props=nullabledict(t.to_data())
#         for i in props.items(): print(i)
        video_codec=f"{props['encoded_library_name']} {props['format_profile']} @ {str(round(props['bit_rate'] / (1000 * 1000), 2))}Mb/s"
        runtime=props['other_duration'][0]
        resolution=f"{props['sampled_width']}x{props['sampled_height']}"
        display_aspect_ratio=props['display_aspect_ratio']
        frame_rate=props["frame_rate"]
        bit_depth=props["other_bit_depth"][0]
    audio_codec=[]
    for t in media_info.audio_tracks:
        props=nullabledict(t.to_data())
#         for i in t.to_data().items(): print(i)
        chns=props['channel_s']
        if chns==6: chns="5.1"
        dtsma=""
        if props['commercial_name']=='DTS-HD Master Audio':dtsma="-HD MA"
        audio_codec.append(f"{props['other_language'][0]} {props['format']}{dtsma} {chns}\
 @ {str(round(props['bit_rate'] / (1000), 2))}Kb/s")
    audioinfo=""    
    for ac in audio_codec:
        audioinfo+=f'AUDiO CODEC...............: {ac} \n'
    chscnt=0
    subtitledesc=''
    for t in media_info.text_tracks:
        props=nullabledict(t.to_data())
    #     for i in props.items(): print(i)
        if 'title' in props:
            title=props['title']
        else: title=props['language']
        
        if title=='zh': 
            title='chs';chscnt+=1
            if chscnt>2: title='cht'
            if chscnt%2==0: title+='&eng'
        subtitlefmt=f"{props['codec_id']} : {props['other_language'][0]}({title})"
        subtitledesc+=f"SUBTiTLES.................: {subtitlefmt}\n"
    NEWMOVIE_size=str(round(os.path.getsize(filename) / (1024 * 1024 * 1024), 3)) + ' GB'
    RELEASE_filename="".join(re.findall(r"([^\\/]*$)", filename.replace(".mkv","")))
    MOVIE_filename="".join(re.findall(r'([^\\/]*$)', src))
    
    transcodelog=""
    if len(logname)>0:
        transcodelog=f'.{logname.replace(".log","")}.Info\n'
        with open(logname,errors='ignore') as f:
            lines=f.readlines()
            for line in lines:
                if ('[info]' in line or '[libx264' in line) and 'profile' not in line:
                    if 'Avg QP' in line or 'profile' in line or 'rames:' in line:
                        transcodelog+=line
    release_info=f'''[quote][font=Lucida Console]
.Release.Info
ENCODER...................: PTH
RELEASE NAME..............: {RELEASE_filename}
RELEASE DATE..............: {datetime.today().strftime('%Y-%m-%d')}
RELEASE SiZE..............: {NEWMOVIE_size}
SOURCE....................: {MOVIE_filename.replace(".mkv","")}

.Media.Info
RUNTiME...................: {runtime}
ViDEO CODEC...............: {video_codec}
RESOLUTiON................: {resolution}
DiSPLAY ASPECT RATiO......: {display_aspect_ratio}
FRAME RATE................: {frame_rate}
BIT DEPTH.................: {bit_depth}
{audioinfo} 
{subtitledesc}

{transcodelog}[/quote]'''
    return release_info
    
def get_captures(codec, filename):
    if not os.path.exists(f"{codec}_captures"):
        os.mkdir(f"{codec}_captures")
    ffmpeg_extract_cmd=''
    for i in range(0,12):
        time=f'0{int(i/6)}:{i%6}2'
        path=os.path.join(os.getcwd(), f"{codec}_captures", f"{codec}_capture_{i*2}.jpg")
        ffmpeg_extract_cmd+=f'ffmpeg -y -ss {time}:00 -i "{filename}" -vframes 1 -q:v 2 {path}\n'
        time=f'0{int(i/6)}:{i%6}7'
        path=os.path.join(os.getcwd(), f"{codec}_captures", f"{codec}_capture_{i*2+1}.jpg")
        ffmpeg_extract_cmd+=f'ffmpeg -y -ss {time}:00 -i "{filename}" -vframes 1 -q:v 2 {path}\n'
    return ffmpeg_extract_cmd
    
def get_mediainfo(filename):
    nfo=subprocess.check_output(f'mediainfo "{filename}"', shell=True).decode("utf-8")
    return f'[hide][font=Lucida Console]\n{nfo}[/hide]'
    
def upload_folder(folder,smms,count=6):
    print("===UPLOAD===")
    picbed=""
    filenames=os.listdir(folder)
    random.shuffle(filenames)
    for f in filenames[0:count]:
        imgpath=os.path.join(folder,f)
        picbed_url=smms.upload_image(imgpath)
        picbed+=f"[img]{picbed_url}[/img]\n"
        print(picbed_url)
    return picbed

def get_bbcode(file, src="",logname="",picbed="",metainfo={"format":""},ack=""):
    print("Title:", file.replace("."," "))
    
    bbcode='''
[quote]
制作说明：
'''+ack+'''字幕转载务必注意礼节，请保留原作者信息，谢绝二次提取修改！
在此感谢各位原作者及分享者！如有侵权请联系删除！
[/quote]
'''+f'{metainfo["format"]}\n{generate_videoinfo(file,logname,src=src)}\n{picbed}\n{get_mediainfo(file)}'
    return bbcode

def getbase64json(filename, src, logname, picbed, metainfo, is_remux=False, template={},tracks="",gz=0,ack=""):
    codec=logname.replace(".log","")
    if codec=="": codec="AVC"
    audiomap={"DTS-HD":19,"TrueHD": 20,"LPCM": 21,"DTS": 3,"AC3": 18,"AAC":6,"FLAC":1,"APE":2,"WAV":22,"Other":7}

    template["small_descr"]="/".join(metainfo["trans_title"]+metainfo["this_title"])+" "+tracks
    template["url"]=metainfo["imdb_link"]
    template["douban_id"]=metainfo["douban_link"]
    template["descr"]=get_bbcode(filename, src=src, logname="x264.log", picbed=picbed, metainfo=metainfo,ack=ack)
    template["medium_sel"]=15 if is_remux is False else 3
    template["codec_sel"]=6 if codec=="x265" else 1
    template["team_sel"]=21
    template["browsecat"]=401
    for a in audiomap:
        if a in os.path.basename(filename):
            template["audiocodec_sel"]=audiomap[a]
            break
    template["standard_sel"]=1 if "1920x" in template["descr"] else 5
    template["officialteam"]=1
    template["gf"]=1
    template["zz"]=1
    template["uplver"]=1
    template["gz"]=gz
    return base64.encodebytes(json.dumps(template).encode("utf-8")).decode("utf-8")
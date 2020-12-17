import vapoursynth as vs
import havsfunc as haf
import mvsfunc as mvf
from vapoursynth import core
import os

if "MOVIE" in os.environ:
    MOVIE=os.environ["MOVIE"]

core.num_threads = 8
core.max_cache_size = 5000
#读取源视频
# print("正在处理：",MOVIE)
src = core.lsmas.LWLibavSource(source=MOVIE,fpsnum=0,fpsden=1,decoder="")
src = core.std.SetFieldBased(src, 0)

#黑边处理
# src = core.std.CropRel(src,left=60,right=60,top=0,bottom=0)
src = core.std.CropRel(src,left=0,right=0,top=140,bottom=140)

# 对Y和UV平面降噪，一般来说只对Y降噪即可，选择性开启。h表示降噪力度。d和a表示时间和空间的降噪精度。, device_id是使用的GPU设备编号，0是第一个，1是第二个，以此类推。可以使用不同的GPU运算，如果有的话。
# print("Denoise...")
# src16  = mvf.Depth(src, 16)
# Y = core.resize.Bicubic(src16, src16.width / 2, src16.height / 2, src_left = -0.5)
# down444 = core.std.ShufflePlanes([Y,src16], [0,1,2], vs.YUV)
# nr16y = core.knlm.KNLMeansCL(src16, d=0.4, a=2, s=5, h=2.0, device_type="GPU",device_id = 0)
# nr16uv = core.knlm.KNLMeansCL(down444, d=0.2, a=2, s=5, h=1.0, channels="YUV", device_type="GPU",device_id = 0)
# src = core.std.ShufflePlanes([nr16y,nr16uv], [0,1,2], vs.YUV)


#如果是挑选片段画面做测试，请删除下面两行前面的#好。下面的意思是，跳过前后的10000帧，然后每3000帧，截取50帧
import awsmfunc as awsf

if "TEST" in os.environ and os.environ["TEST"]=="YES":
    src = awsf.SelectRangeEvery(clip=src, every=10000, length=50, offset=10000)

#如果是x265的话，处理色深；注意第二行src前面的空格不要丢失！
# if 'ctrl' in globals() and int(ctrl) == 1:
src = core.fmtc.bitdepth (src, bits=10)

#视频输出
src.set_output()

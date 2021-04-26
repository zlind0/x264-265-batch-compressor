function pthpipe {
CROP_X=0
CROP_Y=0
while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -i|--in)
    SRC="$2"
    >&2 echo "[IN]\t$SRC"
    shift
    shift
    ;;
    -10|--10bit)
    HIBIT="src = core.fmtc.bitdepth (src, bits=10)"
    shift
    ;;
    -cx|--crop-x)
    CROP_X="$2"
    shift
    ;;
    -cy|--crop-y)
    CROP_Y="$2"
    shift
    ;;
    -t|--test)
    TEST=$(cat <<!
import awsmfunc as awsf
src = awsf.SelectRangeEvery(clip=src, every=3000, length=50, offset=10000)
!
)
    shift
    ;;
    --extra)
    EXTRA="$2"
    shift
    shift
    ;;
    *)
    POSITIONAL+=("$1")
    shift 
    ;;
esac
done

if [ ! -n $SRC ]; then
    >&2 echo "Usage: pthvspipe -i <SOURCE_MKV>     | x264"
    >&2 echo "       pthvspipe -i <SOURCE_MKV> -10 | x265"
    >&2 echo "Other args:"
    >&2 echo "    -t    Pick some parts for testing."
    >&2 echo "    -cx   Crop value for both left and right."
    >&2 echo "    -cy   Crop value for both top and bottom."
else
    VPY=$RANDOM.vpy
    >&2 echo "[VPY]\t/tmp/$VPY"
    cat <<! >/tmp/$VPY
import vapoursynth as vs
from vapoursynth import core
core.num_threads = 2
core.max_cache_size = 2000
src = core.lsmas.LWLibavSource(source=r"$SRC",fpsnum=0,fpsden=1,decoder="")
src = core.std.CropRel(src,left=$CROP_X,right=$CROP_X,top=$CROP_Y,bottom=$CROP_Y)
$TEST
$HIBIT
src.set_output()
!
    export PYTHONPATH=/usr/local/lib/python3.8/site-packages
    vspipe -p --y4m /tmp/$VPY -
fi
}


function pthx264 {
CRF=17
QCOMP=0.7
AQS=0.9

while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -crf|--crf)
    CRF="$2"
    >&2 echo "[CRF]\t$CRF"
    shift
    shift
    ;;
    -qc|--qcomp)
    QCOMP="$2"
    >&2 echo "[QCOMP]\t$QCOMP"
    shift
    shift
    ;;
    -aqs|--aq-strength)
    AQS="$2"
    >&2 echo "[AQS]\t$AQS"
    shift
    shift
    ;;
    -log)
    LOGFILE="$2"
    >&2 echo "[LOG]\t$LOGFILE"
    shift
    shift
    ;;
    -o|--output)
    OUTPUT="$2"
    >&2 echo "[OUT]\t$OUTPUT"
    shift
    shift
    ;;
    *)
    POSITIONAL+=("$1")
    shift 
    ;;
esac
done

if [ -n $OUTPUT ]; then
    x264 --demuxer y4m --preset slower --profile high --level 4.1 --ref 4 \
    --crf $CRF --qcomp $QCOMP --aq-mode 3 --aq-strength $AQS --bframes 11 \
    --me umh  --subme 11 --merange 48 --no-fast-pskip --no-dct-decimate \
    --direct auto --psy-rd 1.00:0.00 --vbv-bufsize 78125 --vbv-maxrate 62500 \
    --deblock -3:-3 --b-adapt 2 --keyint 240 --min-keyint 1 --no-mbtree --trellis 2 \
    --chroma-qp-offset -1 --rc-lookahead 72 --output $OUTPUT - | tee $LOGFILE
else
    echo "Usage: pthx264 --crf <CRF> --qcomp <QCOMP> --aq-strength <AQS> --output <OUT>"
    echo "Usage: pthx264 -crf <CRF> -qc <QCOMP> -aqs <AQS> -o <OUT>"
    echo "Default: -crf=17 -qc=0.7 -aqs=0.9"
fi
}

function pthx265 {
CRF=17
QCOMP=0.7
AQS=0.9

while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -crf|--crf)
    CRF="$2"
    >&2 echo "[CRF]\t$CRF"
    shift
    shift
    ;;
    -qc|--qcomp)
    QCOMP="$2"
    >&2 echo "[QCOMP]\t$QCOMP"
    shift
    shift
    ;;
    -aqs|--aq-strength)
    AQS="$2"
    >&2 echo "[AQS]\t$AQS"
    shift
    shift
    ;;
    -o|--output)
    OUTPUT="$2"
    >&2 echo "[OUT]\t$OUTPUT"
    shift
    shift
    ;;
    -log)
    LOGFILE="$2"
    >&2 echo "[LOG]\t$LOGFILE"
    shift
    shift
    ;;
    *)
    POSITIONAL+=("$1")
    shift 
    ;;
esac
done

if [ -n $OUTPUT ]; then
    x265 --y4m -D 10 --preset slower --aud --repeat-headers  --crf 17.0 --qcomp 0.7 --aq-mode 3 --aq-strength 0.9 \
    --rd 4 --psy-rd 2.0 --rdoq-level 0 --psy-rdoq 0  --ref 6 --no-limit-modes --rc-lookahead 24 --b-intra --weightb \
    --b-adapt 2 --sao --no-limit-sao --selective-sao 4 --me 3 --subme 7 --merange 48 --bframes 8 --keyint 240 \
    --min-keyint 24 --deblock 0:0 --cbqpoffs 0 --crqpoffs 0 --no-strong-intra-smoothing  --no-rect  --no-open-gop \
    --no-amp --pools + --input-depth 10 --stylish  --tu-inter-depth 1 --tu-intra-depth 1 --limit-tu 0 --max-merge 3 \
    --early-skip --output $OUTPUT - 2>&1 | tee $LOGFILE
else
    echo "Usage: pthx265 --crf <CRF> --qcomp <QCOMP> --aq-strength <AQS> --output <OUT>"
    echo "Usage: pthx265 -crf <CRF> -qc <QCOMP> -aqs <AQS> -o <OUT>"
    echo "Default: -crf=17 -qc=0.7 -aqs=0.9"
fi
}

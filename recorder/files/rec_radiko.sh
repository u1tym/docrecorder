#!/bin/bash

if [ $# -lt 3 ] ; then
	printf "Usage: rec_radiko.sh channel time(min) output\n"
	printf "  channel : チャンネルの文字列\n"
	printf "  time    : 録画時間(分)\n"
	printf "  output  : 出力ファイル名(～.mp3)\n"
	printf "dataフォルダ下に出力する。\n"
	exit 1
fi

LANG=ja_JP.utf8

# 出力ファイル名
outfile=${3}

# 現在日時
nowtime=`date '+%Y-%m-%d-%H_%M_%S'`

# 一時ファイル名
tmpfile="/tmp/${channel}_${nowtime}.m4a"

# PID
pid=$$

# 
outdir="./data/"

if [ $# -le 1 ]; then
  echo "usage : $0 channel_name duration(minuites) [outputdir] [prefix]"
  exit 1
fi

if [ $# -ge 2 ]; then
  channel=$1
  DURATION=`expr $2 \* 60`
fi

####
# Define authorize key value (from http://radiko.jp/apps/js/playerCommon.js)
RADIKO_AUTHKEY_VALUE="bcd151073c03b352e1ef2fd66c32209da9ca0afa"


if [ -f auth1_fms_${pid} ]; then
  rm -f auth1_fms_${pid}
fi

#
# access auth1_fms
#
curl -s \
     --header "pragma: no-cache" \
     --header "X-Radiko-App: pc_html5" \
     --header "X-Radiko-App-Version: 0.0.1" \
     --header "X-Radiko-User: test-stream" \
     --header "X-Radiko-Device: pc" \
     --dump-header auth1_fms_${pid} \
     -o /dev/null \
     https://radiko.jp/v2/api/auth1

if [ $? -ne 0 ]; then
  echo "failed auth1 process"
  exit 1
fi

#
# get partial key
#
authtoken=`perl -ne 'print $1 if(/x-radiko-authtoken: ([\w-]+)/i)' auth1_fms_${pid}`
offset=`perl -ne 'print $1 if(/x-radiko-keyoffset: (\d+)/i)' auth1_fms_${pid}`
length=`perl -ne 'print $1 if(/x-radiko-keylength: (\d+)/i)' auth1_fms_${pid}`
partialkey=`echo "${RADIKO_AUTHKEY_VALUE}" | dd bs=1 "skip=${offset}" "count=${length}" 2> /dev/null | base64`

#echo "authtoken: ${authtoken} \noffset: ${offset} length: ${length} \npartialkey: $partialkey"

rm -f auth1_fms_${pid}

if [ -f auth2_fms_${pid} ]; then  
  rm -f auth2_fms_${pid}
fi

#
# access auth2_fms
#
curl -s \
     --header "pragma: no-cache" \
     --header "X-Radiko-User: test-stream" \
     --header "X-Radiko-Device: pc" \
     --header "X-Radiko-AuthToken: ${authtoken}" \
     --header "X-Radiko-PartialKey: ${partialkey}" \
     -o auth2_fms_${pid} \
     https://radiko.jp/v2/api/auth2

if [ $? -ne 0 -o ! -f auth2_fms_${pid} ]; then
  echo "failed auth2 process"
  exit 1
fi

#echo "authentication success"
areaid=`perl -ne 'print $1 if(/^([^,]+),/i)' auth2_fms_${pid}`
#echo "areaid: $areaid"

rm -f auth2_fms_${pid}

#
# get stream-url
#

if [ -f ${channel}.xml ]; then
  rm -f ${channel}.xml
fi

curl -s "http://radiko.jp/v2/station/stream_smh_multi/${channel}.xml" -o ${channel}.xml
stream_url=`xmllint --xpath "/urls/url[@areafree='0'][1]/playlist_create_url/text()" ${channel}.xml`

rm -f ${channel}.xml


#
# ffmpeg
#
ffmpeg \
  -loglevel error \
  -fflags +discardcorrupt \
  -headers "X-Radiko-Authtoken: ${authtoken}" \
  -i "${stream_url}" \
  -acodec copy \
  -vn \
  -bsf:a aac_adtstoasc \
  -y \
  -t ${DURATION} \
  "${tmpfile}"
#  "/tmp/${channel}_${date}.m4a"
  
#ffmpeg -loglevel quiet -y -i "/tmp/${channel}_${date}.m4a" -acodec libmp3lame -ab 128k "${outdir}/${PREFIX}_${date}.mp3"
ffmpeg -loglevel quiet -y -i "${tmpfile}" -acodec libmp3lame -ab 128k "${outdir}/${outfile}"

if [ $? = 0 ]; then
#  rm -f "/tmp/${channel}_${date}.m4a"
  rm -f "${tmpfile}"
fi

#!/bin/bash

if [ $# -lt 3 ] ; then
	printf "Usage: rec_agp.sh channel time(min) output\n"
	printf "  channel : チャンネル(agp)\n"
	printf "  time    : 録画時間(秒)\n"
	printf "  output  : 出力ファイル名(～.mp4)\n"
	printf "datat下に出力\n"
	exit 1
fi

OFILE=${3}
DURATION=${2}

ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto \
-i https://www.uniqueradio.jp/agplayer5/hls/mbr-ff.m3u8 \
-movflags faststart \
-t ${DURATION} -c copy ./data/${OFILE}



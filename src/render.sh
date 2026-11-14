#!/bin/bash
# usage: render.sh model.ldr out.png W H lat long [extra]
cd "$(dirname "$0")"
./ldview/LDView64.exe "$1" -LDrawDir="$(pwd -W)/ldraw" -SaveSnapshot="$(pwd -W)/$2" -SaveWidth=$3 -SaveHeight=$4 -SaveAlpha=0 -DefaultLatLong=$5,$6 -SaveActualSize=0 -ShowHighlightLines=1 -EdgeThickness=1.5 -LineSmoothing=1 -UseQualityStuds=1 -UseQualityLighting=1 -BackgroundColor3=0xffffff -SubduedLighting=0 -SeamWidth=0.5 -SnapshotSuffix=.png $7 >/dev/null 2>&1

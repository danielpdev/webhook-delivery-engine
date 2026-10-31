#!/bin/sh
set -eu
# Show the workflow, captured demo output and evaluation; omit the test-only slides.
ffmpeg -y -i docs/demo.mp4 -filter_complex '[0:v]trim=start=0:end=20,setpts=PTS-STARTPTS[intro];[0:v]trim=start=30:end=40,setpts=PTS-STARTPTS[result];[intro][result]concat=n=2:v=1:a=0,setpts=PTS/1.5,fps=2,scale=1080:-2:flags=lanczos,split[a][b];[a]palettegen=max_colors=128:stats_mode=diff[palette];[b][palette]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle' -loop 0 docs/demo.gif

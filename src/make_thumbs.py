"""Render a thumbnail for every (part, color) used in the model LDR."""
import subprocess, os, sys, pathlib

ldr_path = sys.argv[1] if len(sys.argv) > 1 else 'barad_dur.ldr'
cwd = pathlib.Path(os.getcwd()).as_posix()
os.makedirs('thumbs', exist_ok=True)
pairs = set()
for line in open(ldr_path, encoding='utf-8'):
    t = line.split()
    if t and t[0] == '1':
        pairs.add((t[-1][:-4], int(t[1])))
for part, color in sorted(pairs):
    fn = f"thumbs/{part}_{color}.png"
    if os.path.exists(fn):
        continue
    open('thumb.ldr', 'w').write(f"0 thumb\n1 {color} 0 0 0 1 0 0 0 1 0 0 0 1 {part}.dat\n")
    subprocess.run(['./ldview/LDView64.exe', 'thumb.ldr', f'-LDrawDir={cwd}/ldraw', f'-SaveSnapshot={cwd}/{fn}',
                    '-SaveWidth=300', '-SaveHeight=300', '-SaveAlpha=0', '-DefaultLatLong=30,45', '-SaveActualSize=0',
                    '-ShowHighlightLines=1', '-EdgeThickness=2', '-BackgroundColor3=0xffffff', '-DefaultZoom=0.9',
                    '-UseQualityStuds=1'], capture_output=True)
print(len(pairs), 'part/color pairs;', len(os.listdir('thumbs')), 'thumbnails on disk')

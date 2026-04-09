#!/usr/bin/env python3
"""
create_video.py - PDF 슬라이드 + 음성 → MP4

사용법:
    python scripts/create_video.py
    python scripts/create_video.py --output docs/output.mp4 --dpi 150
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT    = Path(__file__).parent.parent
DOCS    = ROOT / "docs"
AUDIO   = DOCS / "내_기프티콘이_사이버_무기로_쓰이는_이유.m4a"
PDF     = DOCS / "Dismantling_the_ATO_Supply_Chain.pdf"
DEFAULT_OUT = DOCS / "내_기프티콘이_사이버_무기로_쓰이는_이유.mp4"

CROSSFADE = 0.4   # 디졸브 전환 길이 (초)
FPS       = 25
WIDTH     = 1920
HEIGHT    = 1080

# 편집표: (슬라이드 번호, 시작초, 종료초)
# 슬라이드 순서: 1→2→3→4→5→8→6→7→9→10→11→12
def ts(m, s):
    return m * 60 + s

SEGMENTS = [
    (1,  ts( 0,  0), ts( 1, 53)),
    (2,  ts( 1, 53), ts( 4, 28)),
    (3,  ts( 4, 28), ts( 5, 31)),
    (4,  ts( 5, 31), ts( 5, 50)),
    (5,  ts( 5, 50), ts( 7,  3)),
    (8,  ts( 7,  3), ts( 8, 38)),
    (6,  ts( 8, 38), ts(11, 28)),
    (7,  ts(11, 28), ts(11, 57)),
    (9,  ts(11, 57), ts(14, 49)),
    (10, ts(14, 49), ts(15, 19)),
    (11, ts(15, 19), ts(18,  7)),
    (12, ts(18,  7), ts(20, 27)),
]

# 숫자·결론 강조 슬라이드 → 느린 줌인 효과
ZOOM_SLIDES = {2, 10, 12}

# 기본 스케일 필터 (레터박스 포함)
BASE_SCALE = (
    f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
    f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,format=yuv420p"
)

def run(cmd, **kw):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, check=True, **kw)
    return result


def extract_slides(pdf: Path, tmpdir: Path, dpi: int) -> dict[int, Path]:
    """PDF → PNG (1-indexed 슬라이드 번호 → 파일 경로)"""
    print(f"[1/3] PDF → PNG 추출 (dpi={dpi})...")
    prefix = str(tmpdir / "slide")
    run(['pdftoppm', '-r', str(dpi), '-png', str(pdf), prefix])
    slides = {}
    for f in sorted(tmpdir.glob("slide-*.png")):
        # pdftoppm은 slide-001.png, slide-01.png 등 생성
        num = int(f.stem.split('-')[-1])
        slides[num] = f
    print(f"   추출 완료: {len(slides)}장")
    return slides


def make_clip(slide_img: Path, duration: float, slide_num: int,
              tmpdir: Path, dpi: int) -> Path:
    """슬라이드 이미지 → 단일 mp4 클립"""
    out = tmpdir / f"clip_{slide_num:02d}.mp4"
    if slide_num in ZOOM_SLIDES:
        # 느린 줌인: 1.0x → 1.05x  (zoompan은 픽셀 단위 처리)
        frames = int(duration * FPS)
        vf = (
            f"scale={WIDTH*2}:{HEIGHT*2}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH*2}:{HEIGHT*2}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,"
            f"zoompan=z='min(1+{0.05/frames:.8f}*on,1.05)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:fps={FPS}:s={WIDTH}x{HEIGHT},"
            f"format=yuv420p"
        )
    else:
        vf = BASE_SCALE

    run([
        'ffmpeg', '-y',
        '-loop', '1', '-framerate', str(FPS), '-i', str(slide_img),
        '-t', str(duration),
        '-vf', vf,
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
        '-r', str(FPS), '-pix_fmt', 'yuv420p',
        str(out)
    ], capture_output=True)
    return out


def build_xfade_filter(clips: list[Path]) -> tuple[str, str]:
    """N개 클립 → xfade 체인 filter_complex 문자열 반환"""
    n = len(clips)
    if n == 1:
        return "", "[0:v]"

    parts = []
    prev_label = "[0:v]"
    cumulative = 0.0

    for i in range(n - 1):
        # 클립 i의 실제 길이를 ffprobe로 구하기 (이미 trim되어 있음)
        dur = float(subprocess.check_output([
            'ffprobe', '-v', 'quiet',
            '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(clips[i])
        ]).decode().strip())

        cumulative += dur
        offset = cumulative - CROSSFADE
        next_label = f"[v{i+1}]" if i < n - 2 else "[vout]"
        parts.append(
            f"{prev_label}[{i+1}:v]xfade=transition=dissolve"
            f":duration={CROSSFADE}:offset={offset:.3f}{next_label}"
        )
        prev_label = next_label
        cumulative -= CROSSFADE  # 오버랩된 만큼 빼기

    return ";".join(parts), "[vout]"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(DEFAULT_OUT))
    parser.add_argument('--dpi',    type=int, default=150)
    args = parser.parse_args()

    out_path = Path(args.output)

    with tempfile.TemporaryDirectory(prefix='ppvideo_') as tmpdir:
        tmpdir = Path(tmpdir)

        # 1. PDF → 슬라이드 이미지
        slides = extract_slides(PDF, tmpdir, args.dpi)

        # 2. 각 세그먼트 → 개별 클립
        print("[2/3] 슬라이드 클립 생성...")
        clips = []
        for (slide_num, t_start, t_end) in SEGMENTS:
            duration = t_end - t_start
            img = slides[slide_num]
            zoom_mark = " ★줌" if slide_num in ZOOM_SLIDES else ""
            print(f"   슬라이드 {slide_num:2d} ({duration:4.0f}초){zoom_mark}")
            clip = make_clip(img, duration, slide_num, tmpdir, args.dpi)
            clips.append(clip)

        # 3. xfade 체인으로 합치기 + 오디오
        print("[3/3] 영상 합성 + 오디오 믹싱...")
        filt, out_label = build_xfade_filter(clips)

        input_args = []
        for c in clips:
            input_args += ['-i', str(c)]
        input_args += ['-i', str(AUDIO)]

        audio_idx = len(clips)

        if filt:
            cmd = [
                'ffmpeg', '-y',
                *input_args,
                '-filter_complex', filt,
                '-map', out_label,
                '-map', f'{audio_idx}:a',
                '-c:v', 'libx264', '-preset', 'fast', '-crf', '20',
                '-c:a', 'aac', '-b:a', '192k',
                '-shortest',
                str(out_path)
            ]
        else:
            cmd = [
                'ffmpeg', '-y',
                *input_args,
                '-map', '0:v', '-map', f'{audio_idx}:a',
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
                str(out_path)
            ]

        run(cmd)

    size_mb = out_path.stat().st_size / 1024 / 1024
    print(f"\n완료: {out_path} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    main()

from pathlib import Path

import ffmpeg

from media_tools.video.options import ConvertOptions


def convert_video(
    target_video_path: str,
    output_dir: str,
    options: ConvertOptions = ConvertOptions(),
):
    input_path = Path(target_video_path)
    output_path = Path(output_dir) / input_path.name

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise FileExistsError(f"Output file already exists: {output_path}")

    (
        ffmpeg.input(str(input_path))
        .output(str(output_path), **options.to_ffmpegpy_args())
        .overwrite_output()
        .run()
    )

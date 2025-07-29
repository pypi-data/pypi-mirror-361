from dataclasses import dataclass


@dataclass
class ConvertOptions:
    resolution: str = "1280x720"
    fps: int = 30
    crf: int = 24
    preset: str = "slow"
    audio_bitrate: str = "128k"
    faststart: bool = True

    def to_ffmpegpy_args(self) -> dict:
        args = {
            "vf": f"scale={self.resolution}",
            "vcodec": "libx264",
            "preset": self.preset,
            "crf": self.crf,
            "acodec": "aac",
            "audio_bitrate": self.audio_bitrate,
            "r": self.fps,
        }
        if self.faststart:
            args["movflags"] = "+faststart"
        return args

"""
Amazon-Music
~~~~~~~~~
A Python package for interacting with Amazon Music services.

:Copyright: (c) 2025 By Amine Soukara <https://github.com/AmineSoukara>.
:License: MIT, See LICENSE For More Details.
:Link: https://github.com/AmineSoukara/Amazon-Music
:Description: A comprehensive CLI tool and API wrapper for Amazon Music with download capabilities.
"""

import json
import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .printer import error, warning


class AudioExtension(Enum):
    """Supported audio file extensions"""

    FLAC = ".flac"
    M4A = ".m4a"
    OPUS = ".opus"
    OGG = ".ogg"
    MP3 = ".mp3"


@dataclass
class CodecConfig:
    """Configuration for a specific audio codec."""

    extension: AudioExtension
    audio_codec: str
    extra_args: List[str] = None
    requires_bitrate: bool = False


class AudioConverter:
    """Handles audio file conversion with selectable output formats."""

    # Mapping of codecs to their configurations
    CODEC_MAP: Dict[str, CodecConfig] = {
        "flac": CodecConfig(extension=AudioExtension.FLAC, audio_codec="copy"),
        "ac-4.02.02.00": CodecConfig(
            extension=AudioExtension.M4A,
            audio_codec="aac",
            extra_args=["-metadata:s:a:0", "atmos=true"],
        ),
        "ec-3": CodecConfig(
            extension=AudioExtension.M4A,
            audio_codec="aac",
            extra_args=["-metadata:s:a:0", "atmos=true"],
        ),
        "opus": CodecConfig(extension=AudioExtension.OPUS, audio_codec="copy"),
    }

    DEFAULT_BITRATE = "128k"

    def __init__(self, target_extension: AudioExtension = AudioExtension.OPUS):
        """Initialize with target extension choice."""
        self.target_extension = target_extension
        self._configure_codecs()

    def _configure_codecs(self):
        """Configure codecs based on selected target extension."""
        if self.target_extension == AudioExtension.M4A:
            self.CODEC_MAP["opus"] = CodecConfig(
                extension=AudioExtension.M4A, audio_codec="aac", requires_bitrate=True
            )
        else:
            self.CODEC_MAP["opus"] = CodecConfig(
                extension=self.target_extension, audio_codec="copy"
            )

    @staticmethod
    def _get_audio_bitrate(input_path: str) -> Optional[str]:
        """Get audio bitrate using ffprobe."""
        try:
            cmd = [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=bit_rate",
                "-of",
                "json",
                input_path,
            ]
            result = subprocess.run(cmd, capture_output=True, check=True)
            info = json.loads(result.stdout)

            if info.get("streams"):
                bit_rate = info["streams"][0].get("bit_rate")
                if bit_rate:
                    return f"{int(bit_rate) // 1000}k"
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
            warning(f"Could not detect bitrate: {e}")
        return None

    def convert(
        self,
        input_path: str,
        codec: str,
        output_name: str,
        decryption_key: Optional[str] = None,
    ) -> Optional[str]:
        """
        Convert audio file to specified codec using configured extension.

        Args:
            input_path: Path to input audio file
            codec: Target audio codec
            output_name: Base output filename (without extension)
            decryption_key: Decryption key for encrypted inputs

        Returns:
            Path to converted file or None if conversion failed
        """
        if not os.path.isfile(input_path):
            error(f"Input file does not exist: {input_path}")
            return None

        codec = codec.lower()
        if codec not in self.CODEC_MAP:
            error(f"Unsupported codec: {codec}")
            return None

        config = self.CODEC_MAP[codec]
        output_path = f"{output_name}{config.extension.value}"

        ffmpeg_cmd = ["ffmpeg", "-y", "-i", input_path, "-c:a", config.audio_codec]

        if decryption_key:
            ffmpeg_cmd.extend(["-decryption_key", decryption_key])

        if config.requires_bitrate:
            bitrate = self._get_audio_bitrate(input_path) or self.DEFAULT_BITRATE
            #  info(f"Using bitrate: {bitrate}")
            ffmpeg_cmd.extend(["-b:a", bitrate])

        if config.extra_args:
            ffmpeg_cmd.extend(config.extra_args)

        if config.extension == AudioExtension.M4A:
            ffmpeg_cmd.extend(["-movflags", "+faststart"])

        ffmpeg_cmd.append(output_path)

        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
            # info(f"Successfully converted to {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            error(f"Conversion failed: {e.stderr.decode(errors='ignore')}")
            return None

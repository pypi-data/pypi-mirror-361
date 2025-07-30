"""
TODO: Please, work on this module just
to turn it into an audio file extension
converter.
"""
from yta_audio_base.parser import AudioParser
from yta_audio_base.dataclasses import AudioNumpy
from yta_constants.file import AudioFileExtension
from yta_validation.parameter import ParameterValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_general.dataclasses import FileReturned
from pydub import AudioSegment
from typing import Union
from io import BytesIO

import numpy as np


class AudioConverter:
    """
    Class to simplify and encapsulate the functionality
    related to audio conversion.
    """

    @staticmethod
    def to(
        audio: Union[str, np.ndarray, 'BytesIO', AudioSegment, 'AudioClip', 'AudioNumpy'],
        sample_rate: Union[int, None] = None,
        extension: AudioFileExtension = AudioFileExtension.MP3
    ) -> AudioNumpy:
        """
        Transform the 'audio' given to an audio with
        the 'extension' given, storing it locally as
        the 'output_filename' provided.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, np.ndarray, 'BytesIO', AudioSegment, 'AudioClip', 'AudioNumpy'])
        extension = AudioFileExtension.to_enum(audio)

        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )

        audio = AudioParser.to_audiosegment(audio)

        file_in_memory = BytesIO()
        audio.export(file_in_memory, format = extension.value)
        file_in_memory.seek(0)

        return AudioParser.to_audionumpy(
            file_in_memory,
            sample_rate
        )

    @staticmethod
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    def to_wav(
        audio: Union[str, np.ndarray, AudioSegment, 'AudioClip'],
        output_filename: str
    ) -> FileReturned:
        """
        Transform the 'audio' given to a wav audio
        storing it locally as the 'output_filename'
        provided.
        """
        return AudioConverter.to(audio, AudioFileExtension.WAV, output_filename)
    
    @staticmethod
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    def to_mp3(
        audio: Union[str, np.ndarray, AudioSegment, 'AudioClip'],
        output_filename: str
    ) -> FileReturned:
        """
        Transform the 'audio' given to a mp3 audio
        storing it locally as the 'output_filename'
        provided.
        """
        return AudioConverter.to(audio, AudioFileExtension.MP3, output_filename)

    # TODO: Add more to simplify the work (?)
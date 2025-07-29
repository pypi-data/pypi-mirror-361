from yta_audio_base.parser import AudioParser
from yta_audio_base.types import AudioNumpyParseableType
from yta_validation.parameter import ParameterValidator
from pydub import AudioSegment, silence
from typing import Union


class AudioSilence:
    """
    Class to simplify and encapsulate the interaction with
    audio silences.
    """

    @staticmethod
    def detect(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'],
        min_silence_ms: int = 250
    ):
        """
        Detect the silences of a minimum of
        'min_silence_ms' milliseconds time and
        return an array containing tuples with
        the start and the end of the silence
        moments.

        This method returns an array of tuples
        with the start and the end of each
        silence expressed in seconds.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, Union[str, 'BytesIO', 'ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'])
        ParameterValidator.validate_mandatory_positive_int('min_silence_ms', min_silence_ms)
        
        audio = AudioParser.to_audiosegment(audio)

        dBFS = audio.dBFS
        # TODO: Why '- 16' (?) I don't know
        silences = silence.detect_silence(audio, min_silence_len = min_silence_ms, silence_thresh = dBFS - 16)

        # [(1.531, 1.946), (..., ...), ...] in seconds
        return [
            ((start / 1000), (stop / 1000))
            for start, stop in silences
        ]
    
    @staticmethod
    def create(
        duration: float,
        sample_rate: Union[int, None] = None
    ) -> AudioSegment:
        """
        Create a silence audio as a pydub AudioSegment
        of the given 'duration' (in seconds) with the
        also given 'sample_rate'.
        """
        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('frame_rate', sample_rate,  do_include_zero = False)

        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )
        
        return AudioSegment.silent(duration * 1000, sample_rate)
    
__all__ = [
    'AudioSilence'
]
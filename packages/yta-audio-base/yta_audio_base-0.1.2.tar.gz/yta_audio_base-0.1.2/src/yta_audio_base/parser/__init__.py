from yta_audio_base.parser.utils import _audio_to_audionumpy, _audio_to_audiosegment, _audio_to_audioclip
from yta_validation.parameter import ParameterValidator
from typing import Union


# TODO: Maybe set 'requires_dependency' (?)
class AudioParser:
    """
    Class to simplify the way we parse audios.
    """

    def to_audionumpy(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'],
        sample_rate: Union[int, None] = None
    ) -> 'AudioNumpy':
        """
        Transform the "audio" given to an
        AudioNumpy instance using the
        "sample_rate" parameter if provided.
        
        The "audio" provided must be a
        filename string, a file content as
        bytes, in memory, a numpy array, a
        pydub AudioSegment instance or a
        moviepy AudioClip instance.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
        ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

        return _audio_to_audionumpy(
            audio = audio,
            sample_rate = sample_rate
        )
    
    def to_audiosegment(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'],
        sample_rate: Union[int, None] = None
    ) -> 'AudioSegment':
        """
        Transform the "audio" given to a
        pydub AudioSegment instance using the
        "sample_rate" parameter if provided.
        
        The "audio" provided must be a
        filename string, a file content as
        bytes, in memory, a numpy array, an
        AudioNumpy instance or a moviepy
        AudioClip instance.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
        ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

        return _audio_to_audiosegment(
            audio = audio,
            sample_rate = sample_rate
        )
    
    def to_audioclip(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'],
        sample_rate: Union[int, None] = None
    ) -> 'AudioClip':
        """
        Transform the "audio" given to a
        moviepy AudioClip instance using the
        "sample_rate" parameter if provided.
        
        The "audio" provided must be a
        filename string, a file content as
        bytes, in memory, a numpy array, an
        AudioNumpy instance or a pydub
        AudioSegment instance.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
        ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

        return _audio_to_audioclip(
            audio = audio,
            sample_rate = sample_rate
        )
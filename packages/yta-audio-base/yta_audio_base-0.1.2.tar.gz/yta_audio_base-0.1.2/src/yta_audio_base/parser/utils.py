"""
Utils to transform audio data to be able
to handle it with the different libraries
we use.
"""
from yta_numpy.audio.utils import _force_2_dimensions_audio
from yta_validation import PythonValidator
from yta_programming.decorators.requires_dependency import requires_dependency
from typing import Union

import numpy as np

"""
TODO: The parsing with ParameterValidator
must be done when wrapped in a class, like
the 'AudioParser' class.
"""

@requires_dependency('pydub', 'yta_audio_base', 'pydub')
def _audionumpy_to_audiosegment(
    audio: 'AudioNumpy'
) -> 'AudioSegment':
    """
    Transform an AudioNumpy into a pydub
    AudioSegment instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioNumpy')

    from pydub import AudioSegment

    # We need it as an int16
    audio_np = audio.as_int16

    # If stereo, we need to intercalate
    # the bytes
    bytes = (
        audio_np.flatten().tobytes()
        if audio.is_stereo else
        audio_np.tobytes()
    )

    return AudioSegment(
        data = bytes,
        # 2: np.int16,
        sample_width = 2,
        frame_rate = audio.sample_rate,
        channels = audio.number_of_channels
    )

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def _audionumpy_to_audioclip(
    audio: 'AudioNumpy'
) -> 'AudioClip':
    """
    Transform an AudioNumpy into a moviepy
    AudioClip instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioNumpy')

    from moviepy import AudioArrayClip

    return AudioArrayClip(
        array = audio.as_float32,
        fps = audio.sample_rate
    )

def _audiosegment_to_audionumpy(
    audio: 'AudioSegment'
) -> 'AudioNumpy':
    """
    Transform a pydub AudioSegment instance into
    a NumpyAudio instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioSegment')

    from yta_audio_base.dataclasses import AudioNumpy

    if (audio.channels > 2):
        raise Exception('The "audio" provided has more than 2 channels...')

    audio_numpy_array = _force_2_dimensions_audio(
        audio = np.frombuffer(
            buffer = audio.raw_data,
            # The sample width, in bytes, to the np.dtype
            dtype = {
                1: np.int8,
                2: np.int16,
                4: np.int32
            }[audio.sample_width]
        ),
        is_mono = audio.channels == 1
    )

    return AudioNumpy(
        audio = audio_numpy_array,
        sample_rate = audio.frame_rate
    )

def _audiosegment_to_audioclip(
    audio: 'AudioSegment'
) -> 'AudioClip':
    """
    Transform a pydub AudioSegment instance into
    a moviepy AudioClip instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioSegment')

    return _audionumpy_to_audioclip(
        audio = _audiosegment_to_audionumpy(
            audio
        )
    )

def _audioclip_to_audiosegment(
    audio: Union['AudioClip', 'AudioFileClip', 'AudioArrayClip']
) -> 'AudioSegment':
    """
    Transform a moviepy AudioClip instance into
    a pydub AudioSegment instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioClip')

    return _audionumpy_to_audiosegment(
        audio = _audioclip_to_audionumpy(
            audio = audio
        )
    )

def _audioclip_to_audionumpy(
    audio: Union['AudioClip', 'AudioFileClip', 'AudioArrayClip']
) -> 'AudioNumpy':
    """
    Transform a moviepy AudioClip instance into
    a AudioNumpy instance.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, 'AudioClip')

    from yta_audio_base.dataclasses import AudioNumpy

    return AudioNumpy(
        audio = audio.to_soundarray(),
        sample_rate = audio.fps
    )

@requires_dependency('soundfile', 'yta_audio_base', 'soundfile')
def _audiocontent_to_audionumpy(
    audio: Union[str, 'BytesIO', 'np.ndarray'],
    sample_rate: Union[int, None] = None
) -> 'AudioNumpy':
    """
    Transform the "audio" given to an
    AudioNumpy instance using the
    "sample_rate" parameter if provided.
    
    The "audio" provided must be a
    filename string, a file content as
    bytes, in memory, or a numpy array.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    from yta_audio_base.dataclasses import AudioNumpy
    import soundfile as sf

    sample_rate = (
        44_100
        if sample_rate is None else
        sample_rate
    )

    if PythonValidator.is_instance(audio, [str, 'BytesIO']):
        audio, sample_rate = sf.read(audio, always_2d = True)

    return AudioNumpy(
        audio = audio,
        sample_rate = sample_rate
    )

def _audiocontent_to_audioclip(
    audio: Union[str, 'BytesIO', 'np.ndarray'],
    sample_rate: Union[int, None] = None
) -> 'AudioClip':
    """
    Transform the "audio" given to a
    moviepy AudioClip instance using the
    "sample_rate" parameter if provided.
    
    The "audio" provided must be a
    filename string, a file content as
    bytes, in memory, or a numpy array.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    sample_rate = (
        44_100
        if sample_rate is None else
        sample_rate
    )

    return _audionumpy_to_audioclip(
        audio = _audiocontent_to_audionumpy(
            audio = audio,
            sample_rate = sample_rate
        )
    )

def _audiocontent_to_audiosegment(
    audio: Union[str, 'BytesIO', 'np.ndarray'],
    sample_rate: Union[int, None] = 44_100
) -> 'AudioSegment':
    """
    Transform the "audio" given to a
    pydub AudioSegment instance using the
    "sample_rate" parameter if provided.
    
    The "audio" provided must be a
    filename string, a file content as
    bytes, in memory, or a numpy array.
    """
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    return _audionumpy_to_audiosegment(
        audio = _audiocontent_to_audionumpy(
            audio = audio,
            sample_rate = sample_rate
        )
    )

def _audio_to_audionumpy(
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
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    sample_rate = (
        44_100
        if sample_rate is None else
        sample_rate
    )

    return (
        _audiocontent_to_audionumpy(
            audio = audio,
            sample_rate = sample_rate
        )
        if PythonValidator.is_instance(audio, [str, 'BytesIO', 'ndarray']) else
        _audiosegment_to_audionumpy(
            audio = audio
        )
        if PythonValidator.is_instance(audio, 'AudioSegment') else
        _audioclip_to_audionumpy(
            audio = audio
        )
        if PythonValidator.is_instance(audio, ['AudioClip', 'AudioFileClip', 'AudioArrayClip']) else
        # it is already AudioNumpy
        audio
    )

def _audio_to_audiosegment(
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
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    sample_rate = (
        44_100
        if sample_rate is None else
        sample_rate
    )

    return (
        _audiocontent_to_audiosegment(
            audio = audio,
            sample_rate = sample_rate
        )
        if PythonValidator.is_instance(audio, [str, 'BytesIO', 'ndarray']) else
        _audionumpy_to_audiosegment(
            audio = audio
        )
        if PythonValidator.is_instance(audio, 'AudioNumpy') else
        _audioclip_to_audiosegment(
            audio = audio
        )
        if PythonValidator.is_instance(audio, ['AudioClip', 'AudioFileClip', 'AudioArrayClip']) else
        # it is already AudioNumpy
        audio
    )

def _audio_to_audioclip(
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
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioFileClip', 'AudioArrayClip', 'AudioNumpy'])
    # ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

    sample_rate = (
        44_100
        if sample_rate is None else
        sample_rate
    )

    return (
        _audiocontent_to_audioclip(
            audio = audio,
            sample_rate = sample_rate
        )
        if PythonValidator.is_instance(audio, [str, 'BytesIO', 'ndarray']) else
        _audionumpy_to_audioclip(
            audio = audio
        )
        if PythonValidator.is_instance(audio, 'AudioNumpy') else
        _audiosegment_to_audioclip(
            audio = audio
        )
        if PythonValidator.is_instance(audio, 'AudioSegment') else
        # it is already AudioNumpy
        audio
    )
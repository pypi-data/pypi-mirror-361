from yta_audio_base.parser import AudioParser
from yta_programming.decorators.requires_dependency import requires_dependency
from pydub.effects import speedup
from typing import Union


class AudioDuration:
    """
    Class to wrap the functionality related
    with the duration of an audio.
    """

    def crop(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'],
        sample_rate: Union[int, None] = None,
        start: Union[float, None] = None,
        end: Union[float, None] = None
    ) -> 'np.ndarray':
        """
        Crop the 'audio' provided, with the also
        given 'sample_rate', from the given 'start'
        to the also provided 'end' (in seconds).
        """
        if (
            start is None and
            end is None
        ):
            return audio

        audio = AudioParser.to_audionumpy(audio, sample_rate)

        start = (
            0
            if start is None else
            start
        )

        # Check that the 'end' is valid
        end = (
            audio.duration
            if (
                (start + end) > audio.duration or
                end is None
            ) else
            end
        )

        return audio.audio[int(start * sample_rate): int(end * sample_rate)]

def crop_pydub(
    audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'],
    sample_rate: Union[int, None] = None,
    start: Union[float, None] = None,
    end: Union[float, None] = None
) -> 'AudioSegment':
    """
    Using 'pydub'.

    Crop the provided 'audio' to start in the
    given 'start' and to finish on the also
    provided 'end' (in seconds).
    """
    # TODO: This validation shouldn't be
    # done here
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'])
    # ParameterValidator.validate_positive_float('start', start)
    # ParameterValidator.validate_positive_float('duration', duration)

    if (
        start is None and
        end is None
    ):
        return audio

    audio = AudioParser.to_audiosegment(audio, sample_rate)

    start = (
        0
        if start is None else
        start
    )

    # Check that the 'end' is valid
    end = (
        audio.duration_seconds
        if (
            (start + end) > audio.duration_seconds or
            end is None
        ) else
        end
    )

    return audio[start:end]

@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def crop_moviepy(
    audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'],
    sample_rate: Union[int, None] = None,
    start: Union[float, None] = None,
    end: Union[float, None] = None
) -> any:
    """
    Using 'moviepy'.

    Crop the provided 'audio' to start in the
    given 'start' and to finish on the also
    provided 'end' (in seconds).
    """
    # TODO: This validation shouldn't be
    # done here
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'])
    # ParameterValidator.validate_positive_float('start', start)
    # ParameterValidator.validate_positive_float('duration', duration)

    if (
        start is None and
        end is None
    ):
        return audio

    audio = AudioParser.to_audioclip(audio, sample_rate)

    start = (
        0
        if start is None else
        start
    )

    # Check that the 'end' is valid
    end = (
        audio.duration
        if (
            (start + end) > audio.duration or
            end is None
        ) else
        end
    )

    return audio.subclipped(start + end)

# TODO: Are these methods working and also
# working to make them longer not only
# shorter (?)
def speedup_pydub(
    audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'],
    sample_rate: Union[int, None],
    duration: float = 1.0
) -> any:
    """
    Using 'pydub'.

    Speedup the given 'audio' to make
    it have the also provide 'duration'
    (in seconds).
    """
    # TODO: This validation shouldn't be
    # done here
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'])
    # ParameterValidator.validate_mandatory_positive_float('duration', duration)

    audio = AudioParser.to_audiosegment(audio, sample_rate)

    return (
        # The chunk_size is optional but its the size of
        # chunks in milliseconds for processing. Smaller
        # chunks means better pitch preservation but
        # longer processing time.
        speedup(audio, speed_factor = audio.duration_seconds / duration, chunk_size = 150) 
        if duration <= audio.duration_seconds else
        audio
    )

# TODO: This is not working yet
@requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
def speedup_moviepy(
    audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'],
    duration: float
) -> any:
    """
    Using 'moviepy'.

    Speedup the given 'audio' to make it have
    the also provide 'duration'.
    """
    # TODO: This validation shouldn't be
    # done here
    # ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioClip', 'AudioSegment', 'AudioNumpy'])
    # ParameterValidator.validate_mandatory_positive_float('duration', duration)

    audio = AudioParser.to_audioclip(audio)

    return (
        # TODO: Apply the Speedup effect
        # There is no 'AccelDecel' or 'SpeedUp'
        # effect for the 'afx', so I think we 
        # need to use the vfx.AccelDecel
        audio.with_effects([vfx.AccelDecel(duration)])
        if duration <= audio.duration else
        audio
    )
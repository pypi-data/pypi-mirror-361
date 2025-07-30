from yta_audio_base.channels.utils import isolate_audio_channel, _set_channel_pan
from yta_audio_base.parser import AudioParser
from yta_constants.audio import AudioChannel
from yta_validation.parameter import ParameterValidator
from typing import Union


class AudioChannels:
    """
    Class to wrap the functionality related
    to managing audio channels.
    """

    @staticmethod
    def left_channel_only(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy']
    ) -> 'AudioSegment':
        """
        Get the "audio" provided with only the
        left channel. The right channel will be
        muted.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy'])

        return isolate_audio_channel(
            audio = AudioParser.to_audiosegment(audio),
            channel = AudioChannel.LEFT
        )
    
    @staticmethod
    def right_channel_only(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy']
    ) -> 'AudioSegment':
        """
        Get the "audio" provided with only the
        right channel. The left channel will be
        muted.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy'])

        return isolate_audio_channel(
            audio = AudioParser.to_audiosegment(audio),
            channel = AudioChannel.RIGHT
        )

    @staticmethod
    def set_pan(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioSegment', 'AudioClip', 'AudioNumpy'],
        channel_pan: float = 0.0
    ) -> 'AudioSegment':
        """
        Set the provided 'channel_pan' to the also
        given 'audio'. The 'channel_pan' parameter
        must be a value in the range [-1.0, 1.0].
        This means that the volume will be 
        different for each channel (if stereo)
        according to the value provided.

        Some examples below:
        - `channel_pan = -1.0` -> Left channel 100%,
        right channel 0%.
        - `channel_pan = -0.5` -> Left channel 75%,
        right channel 25%.
        - `channel_pan = 0.0` -> Left channel 50%, 
        right channel 50%.
        - `channel_pan = 0.5` -> Left channel 25%,
        right channel 75%.
        - `channel_pan = 1.0` -> Left channel 0%,
        right channel 100%.
        """
        ParameterValidator.validate_mandatory_number_between('channel_pan', channel_pan, -1.0, 1.0)

        return _set_channel_pan(
            audio = AudioParser.to_audiosegment(audio),
            channel_pan = channel_pan
        )

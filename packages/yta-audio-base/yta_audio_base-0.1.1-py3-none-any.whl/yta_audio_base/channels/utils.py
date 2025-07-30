"""
Utils for audio channels manipulation.

The pydub AudioSegment class implements
the '__getitem__(self, key)' method that
allows it to manipulate some data when
accesing to an instance like an array.
"""
from yta_audio_base.parser import AudioParser
from yta_audio_base.dataclasses import AudioNumpy
from yta_audio_base.volume.utils import _set_volume_gain
from yta_constants.audio import AudioChannel
# TODO: Rename 'multimedia' to video
from yta_constants.multimedia import DEFAULT_SCENE_WIDTH
from yta_validation.parameter import ParameterValidator
from typing import Union


# TODO: I think this is the same as doing
# '.only_left' and '.only_right', so we
# can remove this method maybe (?)
def isolate_audio_channel(
    audio: Union[AudioNumpy, 'AudioSegment'],
    channel: AudioChannel = AudioChannel.LEFT
):
    """
    Isolate the provided 'channel' of the also
    given 'audio'.
    """
    ParameterValidator.validate_mandatory_instance_of('audio', audio, [AudioNumpy, 'AudioSegment'])
    channel = AudioChannel.to_enum(channel)

    return _set_channel_pan(
        audio = AudioParser.to_audiosegment(audio),
        channel_pan = channel.value
    )

def _set_channel_pan(
    audio: 'AudioSegment',
    channel_pan: float = 1.0
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
    #ParameterValidator.validate_mandatory_number_between('channel_pan', channel_pan, -1.0, 1.0)

    return audio.pan(channel_pan)

# TODO: This is an effect, it has to be in
# the 'yta_audio_advanced_effects' library
def apply_8d_effect(
    audio: AudioNumpy
):
    """
    Generate a 8d sound effect by splitting
    the "audio" provided into multiple small
    chunks to pan each chunk and simulate 
    that it is moving from L to R and R to L
    in a loop. Decrease the volume towards 
    the center position to make the movement
    sound like a circle instead of a straight
    line.
    """
    audio = AudioParser.to_audiosegment(audio)

    audio_duration = audio.duration_seconds * 1_000
    SCREEN_SIZE = DEFAULT_SCENE_WIDTH
    NUM_OF_PARTS = 80
    AUDIO_PART_SCREEN_SIZE = SCREEN_SIZE / NUM_OF_PARTS
    AUDIO_PART_TIME = audio_duration / NUM_OF_PARTS

    cont = 0
    while ((cont * AUDIO_PART_TIME) < audio_duration):
        coordinate = cont * AUDIO_PART_SCREEN_SIZE
        channel_pan = x_coordinate_to_channel_pan(coordinate)
        volume_adjustment = 5 - (abs(channel_pan) / NUM_OF_PARTS) * 5

        start_time = cont * AUDIO_PART_TIME
        end_time = (cont + 1) * AUDIO_PART_TIME

        # I do this because of a small error that makes it fail
        end_time = (
            audio_duration
            if end_time > audio_duration else
            end_time
        )

        # TODO: Old code below, remove when the 
        # new code is working
        # audio = adjust_audio_channels(audio, channel_pan, volume_adjustment, start_time, end_time)

        audio = (
            audio[:start_time] +
            _set_channel_pan(
                _set_volume_gain(
                    audio[start_time: end_time],
                    volume_adjustment
                ),
                channel_pan
            ) +
            audio[end_time:]
        )

        cont += 1

    return audio

def x_coordinate_to_channel_pan(
    x: int
):
    """
    Calculate the channel pan value (in the
    [-1.0, 1.0] range) for the provided "x"
    coordinate (in a hypothetical scene of
    1920x1080 pixels). The values out of the
    region limits will be evaluated as the
    limits.

    Some examples:
    - `x = 0` -> `-1.0`
    - `x = 480` -> `-0.5
    - `x = 960` -> `0.0`
    - `x = 1340` -> `0.5`
    - `x = 1919` -> `1.0`
    - `x = -200` -> `-1.0`
    - `x = 2300` -> `1.0`

    This is to be used in transition effect
    sounds, to be dynamically panned to fit
    an element that is moving through the 
    screen (scene), so the sound acts moves
    also through the screen.
    """
    ParameterValidator.validate_mandatory_int('x', x)
    
    x = (
        0
        if x < 0 else
        DEFAULT_SCENE_WIDTH - 1
        if x > (DEFAULT_SCENE_WIDTH - 1) else
        x
    )

    return -1.0 + (x * 2.0 / DEFAULT_SCENE_WIDTH - 1)


# # TODO: These 2 methods are related to video
# # so they shouldn't be here.
# @requires_dependency('yta_multimedia_core', 'yta_audio_base', 'yta_multimedia_core')
# @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
# def get_audio_synchronized_with_video_by_position(
#     audio: AudioType,
#     video: Union[str, 'Clip']
# ):
#     """
#     This method iterates over the whole provided 'video' and uses its
#     position in each frame to synchronize that position with the also
#     provided 'audio' that will adjust its pan according to it.

#     This method returns the audio adjusted as a pydub AudioSegment.
#     """
#     # TODO: This can make a cyclic import issue, but I
#     # preserve the code by now because the functionality
#     # was working and interesting
#     from yta_multimedia_core.video.parser import VideoParser
#     from moviepy.Clip import Clip

#     audio = AudioParser.as_audiosegment(audio)
#     # TODO: We cannot be using a VideoParser in this
#     # lib, it will be a cyclic import issue
#     video = VideoParser.to_moviepy(video)

#     frames_number = int(video.fps * video.duration)
#     frame_duration = video.duration / frames_number

#     # I need to know the minimum x below 0 and the maximum above 1919
#     minimum_x = 0
#     maximum_x = DEFAULT_SCENE_WIDTH - 1
#     for i in range(frames_number):
#         t = frame_duration * i
#         # We want the center of the video to be used
#         video_x = video.pos(t)[0] + video.w / 2
#         if video_x < 0 and video_x < minimum_x:
#             minimum_x = video_x
#         if video_x > (DEFAULT_SCENE_WIDTH - 1) and video_x > maximum_x:
#             maximum_x = video_x

#     for i in range(frames_number):
#         t = frame_duration * i
#         video_x = video.pos(t)[0] + video.w / 2

#         # I want to make it sound always and skip our exception limits
#         volume_gain = 1
#         if video_x < 0:
#             volume_gain -= abs(video_x / minimum_x)
#             video_x = 0
#         elif video_x > (DEFAULT_SCENE_WIDTH - 1):
#             volume_gain -= abs((video_x - (DEFAULT_SCENE_WIDTH - 1)) / (maximum_x - (DEFAULT_SCENE_WIDTH - 1)))
#             video_x = (DEFAULT_SCENE_WIDTH - 1)

#         audio = adjust_audio_channels(audio, x_coordinate_to_channel_pan(video_x), volume_gain, t * 1000, (t + frame_duration) * 1000)

#     return audio

# @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
# def synchronize_audio_pan_with_video_by_position(
#     audio: AudioType,
#     video: Union[str, 'Clip']
# ):
#     """
#     This method synchronizes the provided 'video' with the also provided
#     'audio' by using its position to adjust the pan.

#     This method returns the provided 'video' with the new audio 
#     synchronized.
#     """
#     # TODO: This was .to_audiofileclip() before,
#     # remove this comment if working
#     return video.with_audio(AudioParser.as_audioclip(get_audio_synchronized_with_video_by_position(audio, video)))
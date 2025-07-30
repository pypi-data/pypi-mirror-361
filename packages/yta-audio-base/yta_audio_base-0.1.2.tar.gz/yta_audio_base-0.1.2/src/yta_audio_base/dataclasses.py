from yta_audio_base.numpy import AudioNumpyHandler
from yta_numpy.audio.utils import _remove_2nd_dimension
from yta_constants.audio import StereoAudioFormatMode
from yta_validation.parameter import ParameterValidator
from dataclasses import dataclass
from typing import Union

import numpy as np


# TODO: Maybe I have to remove the methods
# that use the AudioNumpyHandler and put
# those in the Audio class...

@dataclass
class AudioNumpy:
    """
    A dataclass that contains the audio as a numpy
    array and the sample rate, used to make easier
    the transformations.

    This dataclass should be used only to be shared
    between simple methods.
    """
    
    @property
    def number_of_samples(
        self
    ) -> int:
        """
        The number of samples in the audio.
        """
        return self.audio.shape[0]
    
    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the audio in seconds, which
        is calculated by applying the number of
        samples divided by the sample rate:

        - number_of_samples / sample_rate
        """
        return self.number_of_samples / self.sample_rate

    @property
    def number_of_channels(
        self
    ) -> int:
        """
        The number of channels of the audio.
        """
        shape = self.audio.shape

        return (
            1
            if len(shape) == 1 else
            shape[1]
        )

    @property
    def is_mono(
        self
    ) -> bool:
        """
        Check if the audio is mono (includes
        one channel) or not.
        """
        return self.number_of_channels == 1

    @property
    def is_stereo(
        self
    ) -> bool:
        """
        Check if the audio is stereo (includes
        two channels) or not.
        """
        return self.number_of_channels == 2
    
    @property
    def left_channel(
        self
    ) -> 'np.ndarray':
        """
        Get the left channel of the audio as a
        numpy array. This method will return 
        the entire numpy array if the audio is
        mono.

        The numpy array returned has only one
        dimension.
        """
        return AudioNumpyHandler.format_audio(
            self.audio.copy(),
            StereoAudioFormatMode.LEFT
        )
    
    @property
    def right_channel(
        self
    ) -> 'np.ndarray':
        """
        Get the right channel of the audio as a
        numpy array. This method will return 
        the entire numpy array if the audio is
        mono.

        The numpy array returned has only one
        dimension.
        """
        return AudioNumpyHandler.format_audio(
            self.audio.copy(),
            StereoAudioFormatMode.RIGHT
        )
    
    @property
    def channels_flattened(
        self
    ) -> 'np.ndarray':
        """
        Get the left and the right channel of
        the audio as a single flattened numpy
        array. If the audio is stereo the array
        will have the double of each channel
        size, and the left channel will be
        first, being like this:
        - `L0, R0, L1, R1, L2, R2`
        
        This method will return the entire
        numpy array if the audio is mono. This
        is similar to the 'as_mono' that forces
        one dimension only.

        The numpy array returned has only one
        dimension.
        """
        return AudioNumpyHandler.format_audio(
            self.audio.copy(),
            StereoAudioFormatMode.MIX_FIRST_LEFT
        )
    
    @property
    def as_mono_1d_mean(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono (mean
        strategy), as an array with only 1 
        dimension and having the same length
        than the original array. This array is
        built by calculating the mean of the
        values if stereo.
        """
        return _remove_2nd_dimension(self.as_mono_2d_mean)
    
    @property
    def as_mono_1d_intercalated(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono (mean
        strategy), as an array with only 1 
        dimension and having the double length
        of the original array if it was a
        stereo audio.

        This is identic to 'channels_flattened'.
        """
        return self.channels_flattened
    
    @property
    def as_mono_2d_mean(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono. If the
        audio is not mono it is obtained by
        averaging samples across channels.

        This array has 2 dimensions. The first
        has the same length than the original
        array, and the value of the second one
        is 1 because it is mono.
        """
        return AudioNumpyHandler.to_mono(self.audio.copy())
    
    @property
    def as_mono_2d_intercalated(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono. If
        the audio is stereo the array will
        have the double of each channel size,
        and the left channel will be first,
        being like this:
        - `L0, R0, L1, R1, L2, R2`

        This array has 2 dimensions. The first
        has the double length of the original
        if it was stereo, or the same if mono,
        and the value of the second one is 1
        because it is mono.
        """
        return self.as_mono_1d_intercalated[:, np.newaxis]

    @property
    def as_stereo_1d(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be stereo as
        an array with only 1 dimension and
        having the same length than the
        original array.
        """
        return _remove_2nd_dimension(self.as_stereo_2d)

    @property
    def as_stereo_2d(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be mono. If the
        audio is not mono it is obtained by
        averaging samples across channels.

        This array has 2 dimensions. The first
        has the same length than the original
        array, and the value of the second one
        is 2 because it is stereo.
        """
        return AudioNumpyHandler.to_stereo(self.audio.copy())

    @property
    def muted(
        self
    ) -> 'np.ndarray':
        """
        Get a copy of the audio but filled
        with zeros, which means that has no
        sound (its muted).
        """
        return np.zeros_like(self.audio)

    @property
    def as_int16(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be a np.int16
        numpy array. This type is accepted by:
        - `pydub`
        - `scipy`
        - `soundfile`
        """
        return AudioNumpyHandler.to_dtype(self.audio.copy(), np.int16)

    @property
    def as_float32(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be a np.float32
        numpy array. This type is accepted by:
        - `scipy`
        - `moviepy`
        - `librosa` (sometimes only as mono)
        - `soundfile`
        """
        return AudioNumpyHandler.to_dtype(self.audio.copy(), np.float32)
        
    @property
    def min(
        self
    ):
        """
        Get the min value of the audio.
        """
        return np.min(np.abs(self.audio))

    @property
    def max(
        self
    ):
        """
        Get the max value of the audio.
        """
        return np.max(np.abs(self.audio))

    @property
    def dtype(
        self
    ) -> np.dtype:
        """
        Get the dtype of the numpy array.
        """
        return self.audio.dtype
    
    @property
    def ndim(
        self
    ) -> int:
        """
        Get the ndim of the numpy array.
        """
        return self.audio.ndim

    @property
    def shape(
        self
    ) -> '_Shape':
        """
        Get the shape of the numpy array.
        """
        return self.audio.shape

    @property
    def inverted(
        self
    ) -> np.ndarray:
        """
        Get the audio but inverted as an
        horizontal mirror.

        TODO: Wtf is this (?)
        """
        return -self.audio.copy()
    
    @property
    def reversed(
        self
    ) -> np.ndarray:
        """
        Get the audio but reversed.
        """
        return self.audio.copy()[::-1]
    
    # TODO: Maybe I can create a property like
    # 'for_pydub' and 'for_libraries' in which
    # I use the PydubAudioNumpyHandler and the
    # OtherAudioNumpyHandler to adapt the numpy

    def __init__(
        self,
        audio: 'np.ndarray',
        sample_rate: int = 44_100
    ):
        """
        Instantiate this Audio dataclass must be
        done by providing the numpy array and the
        sample rate.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate)

        self.audio: 'np.ndarray' = audio
        """
        The numpy array that contains the audio 
        information.
        """
        self.sample_rate: int = sample_rate
        """
        The sample rate of the audio. A None value
        means that is unknown.
        """

    def as_dtype(
        self,
        dtype: np.dtype,
        is_mono: Union[bool, None] = None
    ) -> 'np.ndarray':
        """
        Get the audio of this instance transformed
        into the 'dtype' given, adjusting (if needed
        and requested) if it is a mono or stereo
        channel, without updating the instance.
        """
        ParameterValidator.validate_bool('is_mono', is_mono)
        
        return AudioNumpyHandler.to_dtype(self.audio.copy(), dtype, is_mono)

    def to_dtype(
        self,
        dtype: np.dtype,
        is_mono: Union[bool, None] = None
    ) -> 'np.ndarray':
        """
        Transform the audio to the given 'dtype',
        adjusting (if needed and requested) if it
        is a mono or stereo channel, and update
        the instance.
        """
        self.audio = self.as_dtype(dtype, is_mono)

        return self.audio
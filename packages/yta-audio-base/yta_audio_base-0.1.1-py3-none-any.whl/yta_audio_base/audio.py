from yta_audio_base.saver import AudioSaver
from yta_audio_base.parser import AudioParser
from yta_audio_base.volume import AudioVolume
from yta_audio_base.dataclasses import AudioNumpy
from yta_audio_base.duration import AudioDuration
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from typing import Union

import numpy as np
import librosa


class Audio:
    """
    A class to wrap the audio information and
    manipulate it a bit. Check the advanced
    library ('yta_audio_advanced') to get more
    advanced functionalities.
    """

    @property
    def audio(
        self
    ) -> 'np.ndarray':
        """
        The audio as a numpy array.
        """
        return self.audio_numpy.audio
    
    @property
    def sample_rate(
        self
    ) -> int:
        """
        The sample rate as an int.
        """
        return self.audio_numpy.sample_rate

    @property
    def number_of_channels(
        self
    ) -> int:
        """
        The number of channels of the audio.
        """
        return self.audio_numpy.number_of_channels
    
    @property
    def number_of_samples(
        self
    ) -> int:
        """
        The number of samples in the audio.
        """
        return self.audio_numpy.number_of_samples
    
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
        return self.audio_numpy.duration
    
    @property
    def is_mono(
        self
    ) -> bool:
        """
        Check if the audio is mono (includes
        one channel) or not.
        """
        return self.audio_numpy.is_mono

    @property
    def is_stereo(
        self
    ) -> bool:
        """
        Check if the audio is stereo (includes
        two channels) or not.
        """
        return self.audio_numpy.is_stereo
    
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
        return self.audio_numpy.left_channel
    
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
        return self.audio_numpy.right_channel
    
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
        
        This method will return the
        entire numpy array if the audio is mono.
        The left channel will be the first,

        The numpy array returned has only one
        dimension.
        """
        return self.audio_numpy.channels_flattened
    
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
        return self.audio_numpy.as_mono_1d_mean
    
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
        return self.audio_numpy.as_mono_1d_intercalated
    
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
        return self.audio_numpy.as_mono_2d_mean
    
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
        return self.audio_numpy.as_mono_2d_intercalated

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
        return self.audio_numpy.as_stereo_1d
    
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
        return self.audio_numpy.as_stereo_2d
    
    @property
    def muted(
        self
    ) -> 'np.ndarray':
        """
        Get a copy of the audio but filled
        with zeros, which means that has no
        sound (its muted).
        """
        return self.audio_numpy.muted

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
        return self.audio_numpy.as_int16

    @property
    def as_float32(
        self
    ) -> 'np.ndarray':
        """
        Get the audio forced to be a np.float32
        numpy array. This type is accepted by:
        - `scipy`
        - `moviepy`
        - `librosa`
        - `soundfile`
        """
        return self.audio_numpy.as_float32
    
    # Other properties below
    @property
    def min(
        self
    ):
        """
        Get the min value of the audio.
        """
        return self.audio_numpy.min

    @property
    def max(
        self
    ):
        """
        Get the max value of the audio.
        """
        return self.audio_numpy.max

    @property
    def dtype(
        self
    ) -> np.dtype:
        """
        Get the dtype of the numpy array.
        """
        return self.audio_numpy.dtype

    @property
    def ndim(
        self
    ) -> int:
        """
        Get the ndim of the numpy array.
        """
        return self.audio_numpy.ndim

    @property
    def shape(
        self
    ) -> '_Shape':
        """
        Get the shape of the numpy array.
        """
        return self.audio_numpy.shape
    
    @property
    def inverted(
        self
    ) -> np.ndarray:
        """
        Get the audio but inverted as an horizontal mirror.

        TODO: Wtf is this (?)
        """
        return self.audio_numpy.inverted
    
    @property
    def reversed(
        self
    ) -> np.ndarray:
        """
        Get the audio but reversed.
        """
        return self.audio_numpy.reversed
    
    def __init__(
        self,
        audio: 'np.ndarray', # the audio as a numpy array
        sample_rate: int = 44_100 # the sample rate
    ):
        """
        Instantiate this Audio dataclass must be
        done by providing the numpy array and the
        sample rate.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate)

        self.audio_numpy = AudioNumpy(audio, sample_rate)
        """
        The numpy array, as an AudioNumpy
        dataclass, containing also the sample
        rate.
        """

    @staticmethod
    def init(
        audio: Union['np.ndarray', str],
        sample_rate: Union[int, None] = None
    ) -> 'Audio':
        """
        Initialize an Audio instance by an 'audio'
        parameter of any kind and an optional
        "sample_rate" parameter. It can be a numpy
        array, an AudioClip, an AudioSegment...
        """
        audionumpy = AudioParser.to_audionumpy(audio, sample_rate)

        return Audio(audionumpy.audio, audionumpy.sample_rate)

    def as_dtype(
        self,
        dtype: np.dtype,
        is_mono: Union[bool, None] = None
    ) -> np.ndarray:
        """
        Get the audio of this instance transformed
        into the 'dtype' given, adjusting (if needed
        and requested) if it is a mono or stereo
        channel, without updating the instance.
        """
        ParameterValidator.validate_bool('is_mono', is_mono)
        
        return self.audio_numpy.to_dtype(dtype, is_mono)

    # TODO: Is this 'to_dtype' needed (?)
    def to_dtype(
        self,
        dtype: np.dtype,
        is_mono: Union[bool, None] = None
    ) -> np.ndarray:
        """
        Transform the audio to the given 'dtype',
        adjusting (if needed and requested) if it
        is a mono or stereo channel, and update
        the instance.
        """
        self.audio_numpy.to_dtype(dtype, is_mono)

        return self.audio
    
    def apply_trim(
        self,
        start: Union[float, None],
        end: Union[float, None]
    ) -> 'Audio':
        """
        Get a new instance with the audio array modified.
        """
        self.audio_numpy.audio = self.with_trim(start, end)

        return self

    def with_trim(
        self,
        start: Union[float, None],
        end: Union[float, None]
    ) -> 'np.ndarray':
        """
        Get the audio trimmed from the provided 'start'
        to the also given 'end'.
        """
        ParameterValidator.validate_positive_number('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_number('end', end, do_include_zero = True)
        
        return AudioDuration.crop(self.audio.copy(), self.sample_rate, start, end)
    
    def with_volume(
        self,
        volume: int = 100
    ):
        """
        Get the audio modified by applying the volume
        change according to the given parameter. The
        range of values for the 'volume' parameter is
        from 0 to 500.

        - 0 means silence (x0)
        - 50 means 50% of original volume (x0.5)
        - 500 means 500% of original volume (x5)
        """
        return AudioVolume.set_volume(self.audio.copy(), volume)

    def apply_volume(
        self,
        volume: int = 100
    ) -> 'Audio':
        """
        Modify the audio in the instance with the one
        after the volume change has been applied. The
        range of values for the 'volume' parameter is
        from 0 to 500.

        - 0 means silence (x0)
        - 50 means 50% of original volume (x0.5)
        - 500 means 500% of original volume (x5)
        """
        self.audio_numpy.audio = self.with_volume(volume)

        return self
    
    def with_mute(
        self,
        start: Union[float, None] = None,
        end: Union[float, None] = None
    ) -> 'np.ndarray':
        """
        Get the audio but muted in the segment
        from the provided 'start' to the also
        given 'end'.

        If no 'start' or 'end' provided, the 
        audio will remain unchanged. If you 
        want the whole audio muted you can use
        the '.muted' property.
        """
        ParameterValidator.validate_positive_float('start', start, do_include_zero = True)
        ParameterValidator.validate_positive_float('end', end, do_include_zero = False)

        if (
            start is None and
            end is None
        ):
            return self.audio
        
        start = (
            0
            if start is None else
            start
        )

        # Check that the 'end' is valid
        end = (
            self.duration
            if (
                (start + end) > self.duration or
                end is None
            ) else
            end
        )

        audio = self.audio.copy()
        audio[start:end] = 0

        return audio
    
    def apply_mute(
        self,
        start: Union[float, None] = None,
        end: Union[float, None] = None
    ) -> 'Audio':
        """
        Modify the audio in the instance with
        the one after the mute has been applied.
        The audio will be muted in the segment
        from the provided 'start' to the also
        given 'end'.

        If no 'start' or 'end' provided, the 
        audio will remain unchanged. If you 
        want the whole audio muted you can use
        the '.muted' property.
        """
        self.audio_numpy.audio = self.with_mute(start, end)

        return self

    def with_resample(
        self,
        sample_rate: int
    ) -> 'np.ndarray':
        """
        Get the audio but resampled to the 
        provided 'sample_rate'. Theis will
        return a new numpy array but will
        not modify the instance.
        """
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate, do_include_zero = False)

        return librosa.resample(
            self.audio.copy(),
            orig_sr = self.sample_rate,
            target_sr = sample_rate
        )
    
    def apply_resample(
        self,
        sample_rate: int
    ) -> 'Audio':
        """
        Modify the audio in the instance with
        the one after the resample has been
        applied. This will also set the
        'sample_rate' provided as the new
        instance sample rate.
        """
        self.audio_numpy.audio = self.with_resample(sample_rate)
        self.audio_numpy.sample_rate = sample_rate

        return self

    def with_loop(
        self,
        times: int = 1
    ) -> 'np.ndarray':
        """
        Get the audio but repeated the number
        of times given in the 'times' 
        parameter provided. Theis will return
        a new numpy array but will not modify
        the instance.

        The max value for the 'times' parameter
        is 10.
        """
        ParameterValidator.validate_mandatory_number_between('times', times, 1, 10)

        return np.tile(self.audio.copy(), times)
    
    def apply_loop(
        self,
        times: int = 1
    ) -> 'Audio':
        """
        Modify the audio in the instance with
        the one after the loop has been
        applied.
        """
        self.audio_numpy.audio = self.with_loop(times)

        return self
    
    def save(
        self,
        filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'filename' and return that 'filename' if
        successfully written.

        You need to have one of these libraries
        installed to be able to save the file:
        - "soundfile"
        - "scipy"
        - "pydub"
        - "moviepy"
        - "torch" and "torchaudio" (both)
        """
        ParameterValidator.validate_mandatory_string('filename', filename, do_accept_empty = False)

        filename = (
            AudioSaver.save_with_soundfile(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('soundfile') else
            AudioSaver.save_with_scipy(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('scipy') else
            AudioSaver.save_with_pydub(self.audio, self.number_of_channels, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('pydub') else
            AudioSaver.save_with_moviepy(self.audio, self.sample_rate, filename)
            if PythonValidator.is_dependency_installed('moviepy') else
            AudioSaver.save_with_torch(self.audio, self.sample_rate, filename)
            if (
                PythonValidator.is_dependency_installed('torch') and
                PythonValidator.is_dependency_installed('torchaudio')
            ) else
            None
        )
        
        if filename is None:
            raise Exception('You need one of these libraries installed to be able to save the file: "soundfile", "scipy", "pydub", "moviepy" or "torch" and "torchaudio".')
        
        return filename
"""
We use different libraries to handle the
audios as numpy arrays, and those ones
handle the numpy arrays in a different
way.

The 'pydub' library is the only one that
expects the numpy arrays as 'np.int16'
and the rest accept expect 'np.float32'
(some of then accept both, but we limit
it to be always the same format). This
is why I created all these helpers, to
ensure the numpy arrays are valid for
each library I try to use.

Libraries we use: 'pydub', 'librosa',
'scipy', 'moviepy', 'soundfile', 'torch'

When you want to use one of the libraries
that are not 'pydub' you can use the
OthersAudioNumpyHandler and the
'to_valid_numpy_audio_array' method to
transform the numpy array to one that is
valid for that library.
"""
from yta_numpy.audio import AudioNumpyHandler
from yta_validation import PythonValidator
from yta_validation.parameter import ParameterValidator

import numpy as np


# TODO: Maybe move this (?)
class PydubAudioNumpyHandler:
    """
    Class to wrap functionality related to
    handling numpy arrays for the 'pydub'
    library.

    The 'pydub' library expects numpy arrays
    that are 'np.int16' and with 'ndim = 1'
    or 'ndim = 2'.

    We will obtain 'np.int16' arrays with
    'ndim = 2' and values in the range
    [-32768, 32767].
    """

    @staticmethod
    def generate_audio(
        # Frecuencia de muestreo en Hz
        sample_rate: int = 44_100,
        duration: float = 1.0,
        # Frecuencia del tono (Hz) - La4
        frequency: int = 440,
        is_mono: bool = False
    ) -> np.ndarray:
        """
        Generate a random 'np.int16' numpy
        audio array with values in the range
        [-32768, 32767] and 'ndim = 2' with the
        shape (n_samples, n_channels).
        """
        return AudioNumpyHandler.generate_audio(
            sample_rate,
            duration,
            frequency,
            np.int16,
            is_mono
        )
    
    @staticmethod
    def is_valid(
        audio: np.ndarray
    ) -> bool:
        """
        Check if the 'audio' given is a 
        valid audio numpy array for the
        'pydub' library, which
        means that is a np.int16 array
        with the (n_samples, n_channels)
        or (n_samples) shape, and with
        values in the range [-32768,
        32767].

        This is an audio that is processable
        by 'pydub' without any change.
        """
        return (
            PythonValidator.is_numpy_array(audio) and
            audio.ndim == 1 or
            (
                audio.ndim == 2 and
                audio.shape[1] in [1, 2]
            ) and
            audio.dtype == np.int16 and
            np.any(np.abs(audio) <= 32768)
        )
    
    @staticmethod
    def can_be_valid(
        audio: np.ndarray
    ) -> bool:
        """
        Check if the provided 'audio' is
        an audio that is valid or can be
        transformed into a valid one by
        using the
        'to_valid_numpy_array_audio'
        method.
        """
        return AudioNumpyHandler.can_be_valid(audio)
    
    @staticmethod
    def to_valid_numpy_array_audio(
        audio: np.ndarray
    ) -> np.ndarray:
        """
        Transform, if needed, the 'audio'
        provided to a valid audio numpy
        array, which is a np.int16 array
        with the (n_samples, n_channels)
        shape and with values in the range
        [-32768, 32767].
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        if not PydubAudioNumpyHandler.can_be_valid(audio):
            raise Exception('The "audio" provided cannot be converted to a valid numpy audio array.')

        return AudioNumpyHandler.to_dtype(audio, np.int32, None)
    
    @staticmethod
    def parse(
        audio: np.ndarray
    ) -> np.ndarray:
        """
        Parse the 'audio' numpy array 
        provided, check if is valid and
        transform it if needed to be able
        to use it in the libraries.
        """
        if not PydubAudioNumpyHandler.can_be_valid:
            raise Exception('The "audio" parameter provided cannot be processed as a valid audio numpy array.')
        
        return PydubAudioNumpyHandler.to_valid_numpy_array_audio(audio)

class OthersAudioNumpyHandler:
    """
    Class to wrap functionality related to
    handling numpy arrays for the 'pydub',
    'librosa', 'scipy', 'moviepy', 'torch'
    and 'soundfile' libraries.

    Those libraries expect numpy arrays
    that are 'np.float32' and with
    'ndim = 2'.

    We will obtain 'np.float32' arrays
    with 'ndim = 2' and values in the range
    [-1.0, 1.0].
    """
        
    @staticmethod
    def generate_audio(
        # Frecuencia de muestreo en Hz
        sample_rate: int = 44_100,
        duration: float = 1.0,
        # Frecuencia del tono (Hz) - La4
        frequency: int = 440,
        is_mono: bool = False
    ) -> np.ndarray:
        """
        Generate a random 'np.float32' numpy
        audio array with values in the range
        [-1.0, 1.0] and 'ndim = 2' with the
        shape (n_samples, n_channels).
        """
        return AudioNumpyHandler.generate_audio(
            sample_rate,
            duration,
            frequency,
            np.float32,
            is_mono
        )

    @staticmethod
    def is_valid(
        audio: np.ndarray
    ) -> bool:
        """
        Check if the 'audio' given is a 
        valid audio numpy array, which
        means that is a np.float32 array
        with the (n_samples, n_channels)
        shape and with values in the range
        [-1.0, 1.0].

        This is an audio that is processable
        by our libraries without any change.
        """
        return AudioNumpyHandler.is_valid(audio)
    
    @staticmethod
    def can_be_valid(
        audio: np.ndarray
    ) -> bool:
        """
        Check if the provided 'audio' is
        an audio that is valid or can be
        transformed into a valid one by
        using the
        'to_valid_numpy_array_audio'
        method.
        """
        return AudioNumpyHandler.can_be_valid(audio)
    
    @staticmethod
    def to_valid_numpy_array_audio(
        audio: np.ndarray
    ) -> np.ndarray:
        """
        Transform, if needed, the 'audio'
        provided to a valid audio numpy
        array, which is a np.float32 array
        with the (n_samples, n_channels)
        shape and with values in the range
        [-1.0, 1.0].
        """
        return AudioNumpyHandler.to_valid_numpy_array_audio(audio)
    
    @staticmethod
    def parse(
        audio: np.ndarray
    ) -> np.ndarray:
        """
        Parse the 'audio' numpy array 
        provided, check if is valid and
        transform it if needed to be able
        to use it in the libraries.
        """
        if not OthersAudioNumpyHandler.can_be_valid:
            raise Exception('The "audio" parameter provided cannot be processed as a valid audio numpy array.')
        
        return OthersAudioNumpyHandler.to_valid_numpy_array_audio(audio)
    
    # Check this notion task:
    # https://www.notion.so/Funcionalidad-audio-210f5a32d46280ca9c2edaba61b474a4?source=copy_link
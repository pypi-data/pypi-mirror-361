from yta_validation.parameter import ParameterValidator

import numpy as np


class AudioVolume:
    """
    Class to wrap the functionality related
    to the audio volume.
    """

    @staticmethod
    def set_volume(
        audio: 'np.ndarray',
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
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_number_between('volume', volume, 0, 500)

        volume /= 100.0

        audio_type = audio.dtype
        audio = (
            # int to float to avoid overflow, if needed
            audio.astype(np.float32)
            if np.issubdtype(audio_type, np.integer) else
            audio
        )

        audio *= volume

        # turn into original type if int to avoid overflow
        if np.issubdtype(audio_type, np.integer):
            info = np.iinfo(audio_type)
            audio = np.clip(audio, info.min, info.max)
            audio = audio.astype(audio_type)

        return audio
    
    # TODO: We have another method with 
    # AudioSegment, handled different, in
    # the 'utils.py' module
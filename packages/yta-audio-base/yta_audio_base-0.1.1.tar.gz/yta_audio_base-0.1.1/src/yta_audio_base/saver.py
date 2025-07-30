"""
Module to save an audio as a file.
This module need different libraries.

TODO: All these methods must be tested
when the way of handling the optional
dependencies for testing is ready. Check
notion for more information:
https://www.notion.so/Mejorar-testing-venv-225f5a32d46280979162c0fc5c3ef8cc?source=copy_link
"""
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation.parameter import ParameterValidator

import numpy as np


class AudioSaver:
    """
    Class to simplify the way you store an
    audio as a file. This class depends on
    the next libraries:

    - "soundfile"
    - "scipy"
    - "pydub"
    - "moviepy"
    - "torch" and "torchaudio"

    You need the library to use the 
    corresponding audio saver method. Check
    the optional dependencies of this 
    project so you can find the way to
    install any of them.
    """

    @requires_dependency('soundfile', 'yta_audio_base', 'soundfile')
    def save_with_soundfile(
        audio: 'np.ndarray',
        sample_rate: int,
        output_filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'output_filename' and return that filename
        if successfully written.

        This method requires the 'soundfile' lib
        installed.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate, do_include_zero = False)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        import soundfile as sf

        sf.write(output_filename, audio, sample_rate)
    
        # TODO: Maybe return a FileReturned (?)
        return output_filename
    
    @requires_dependency('scipy', 'yta_audio_base', 'scipy')
    def save_with_scipy(
        audio: 'np.ndarray',
        sample_rate: int,
        output_filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'output_filename' and return that filename
        if successfully written.

        This method requires the 'scipy' lib
        installed.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate, do_include_zero = False)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        from scipy.io.wavfile import write

        # TODO: What about the 'astype' (?)
        write(output_filename, sample_rate, audio.astype('int16'))

        # TODO: Maybe return a FileReturned (?)
        return output_filename

    @requires_dependency('pydub', 'yta_audio_base', 'pydub')
    def save_with_pydub(
        audio: 'np.ndarray',
        sample_rate: int,
        number_of_channels: int,
        output_filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'output_filename' and return that filename
        if successfully written.

        This method requires the 'pydub' lib
        installed.
        """
        ParameterValidator.validate_mandatory_numpy_array('audio', audio)
        ParameterValidator.validate_mandatory_positive_int('sample_rate', sample_rate, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('number_of_channels', number_of_channels, do_include_zero = False)
        ParameterValidator.validate_mandatory_string('output_filename', output_filename, do_accept_empty = False)

        from pydub import AudioSegment

        AudioSegment(
            (audio * 32767).astype(np.int16).tobytes(),
            frame_rate = sample_rate,
            # TODO: Do we keep this 'sample_width' (?)
            # Bytes per sample (int16)
            sample_width = 2,  # bytes per sample (int16)
            channels = number_of_channels
            # TODO: What about the extension (?)
        ).export(output_filename, format = 'mp3')

        # TODO: Maybe return a FileReturned (?)
        return output_filename
    
    # TODO: This method below is not working
    @requires_dependency('moviepy', 'yta_audio_base', 'moviepy')
    def save_with_moviepy(
        audio: 'np.ndarray',
        sample_rate: int,
        output_filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'output_filename' and return that filename
        if successfully written.

        This method requires the 'torch' and
        'torchaudio' libs installed.

        TODO: Sorry, not working yet.
        """
        from moviepy.audio.AudioClip import AudioArrayClip

        # TODO: Solve this error:
        # TypeError: 'numpy.float32' object is not iterable
        AudioArrayClip(audio, fps = sample_rate).write_audiofile('moviepy.wav')

        return output_filename

    @requires_dependency('torch', 'yta_audio_base', 'torch')
    @requires_dependency('torchaudio', 'yta_audio_base', 'torchaudio')
    def save_with_torch(
        audio: 'np.ndarray',
        sample_rate: int,
        output_filename: str
    ) -> str:
        """
        Write the audio to a file with the given
        'output_filename' and return that filename
        if successfully written.

        This method requires the 'torch' and
        'torchaudio' libs installed.
        """
        import torch
        import torchaudio

        # The audio has the shape [1, num_samples]
        torchaudio.save(output_filename, torch.from_numpy(audio.T).unsqueeze(0), sample_rate)

        # TODO: Maybe return a FileReturned (?)
        return output_filename
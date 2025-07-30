from yta_audio_base.numpy import AudioNumpyHandler
from yta_audio_base.dataclasses import AudioNumpy
from yta_audio_base.parser import AudioParser
from yta_validation.parameter import ParameterValidator
from df.enhance import enhance, init_df
from typing import Union

import librosa
import numpy as np


class AudioNoise:
    """
    Class to simplify and encapsulate
    the code related with audio noise.
    """

    @staticmethod
    def remove(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'],
        sample_rate: Union[int, None] = None
    ) -> np.ndarray:
        """
        Remove the noise from the provided audio and, if 'output_filename'
        is provided, the audio without noise is written localy with that
        filename.
        """
        # Using deepfilternet https://github.com/Rikorose/DeepFilterNet
        # TODO: This fails when .mp3 is used, so we need to transform into wav.
        # TODO: Output file must be also wav
        # TODO: What about audioclip instead of audiofile? Is it possible? (?)
        # Based on this (https://medium.com/@devesh_kumar/how-to-remove-noise-from-audio-in-less-than-10-seconds-8a1b31a5143a)
        # https://github.com/Rikorose/DeepFilterNet
        # TODO: This is failing now saying 'File contains data in an unknon format'...
        # I don't know if maybe some library, sh*t...
        # Load default model
        
        # If it is not an audio filename I need to create it to be able to
        # work with (TODO: Check how to turn into same format as when readed)
        # TODO: Refactor these below to accept any audio, not only filename
        # TODO: This is actually checked with the decorator
        ParameterValidator.validate_mandatory_instance_of('audio', audio, [str, 'BytesIO', 'ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'])
        ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)

        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )

        audio = AudioParser.to_audionumpy(audio, sample_rate)

        # Inicializa el modelo
        model, df_state, _ = init_df()

        # TODO: Maybe use 'as_mono_intercalated' or
        # similar if we create it in the AudioNumpy
        # class
        audio_np = AudioNumpyHandler.remove_2nd_dimension(
            AudioNumpyHandler.to(audio.audio, np.float32, True)
        )

        # Resample if needed
        expected_sample_rate = df_state.sr()
        audio_np = (
        # TODO: Apply @requires_dependency (?)
            librosa.resample(audio_np, orig_sr = sample_rate, target_sr = expected_sample_rate)
            if expected_sample_rate != sample_rate else
            audio_np
        )

        audio_np = enhance(model, df_state, audio_np)

        # Transform io tensor to numpy array
        return (
            audio_np.numpy()
            if hasattr(audio_np, 'numpy') else
            np.array(audio_np)
        )

    @staticmethod
    def add(
        audio: Union[str, 'BytesIO', 'np.ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'],
        sample_rate: Union[int, None] = None,
        db: float = -20
    ):
        """
        Add white noise to the given 'audio'.
        """
        ParameterValidator.validate_mandatory_instance_of('audio', audio, Union[str, 'BytesIO', 'ndarray', 'AudioNumpy', 'AudioClip', 'AudioSegment'])
        ParameterValidator.validate_positive_int('sample_rate', sample_rate, do_include_zero = False)
        ParameterValidator.validate_mandatory_number('db', db)

        sample_rate = (
            44_100
            if sample_rate is None else
            sample_rate
        )

        # Audio must be mono for this effect
        audio = AudioParser.to_audionumpy(audio).as_mono

        # Noise level from dB to lineal correlation
        noise_power = np.mean(audio ** 2) / (10 ** (abs(db) / 10))

        # White noise
        noise = np.random.normal(0, np.sqrt(noise_power), audio.shape)
        # Brown noise
        # TODO: This is just an example of another
        # type of noise, add more and refactor
        # noise = np.cumsum(noise)

        noisy_audio = audio + noise

        # Normalize to avoid clipping
        max_val = np.max(np.abs(noisy_audio))
        
        return (
            noisy_audio / max_val
            if max_val > 1.0 else
            noisy_audio
        )
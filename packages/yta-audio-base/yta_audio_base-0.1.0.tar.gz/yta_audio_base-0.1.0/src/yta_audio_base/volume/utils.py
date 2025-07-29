from yta_validation.parameter import ParameterValidator


def _set_volume_gain(
    audio: 'AudioSegment',
    volume_gain: float = 1.0
) -> 'AudioSegment':
    """
    Set the provided 'volume_gain' to the also
    given 'audio'. The 'volume_gain' parameter
    must be a value in the range [-5.0, 5.0].
    This means that the volume will change.

    Some examples below:
    - `volume_gain = 0` -> Fragment is in
    silence.
    - `volume_gain = 1` -> Fragment volume is
    1x (the same).
    - `volume_gain = 2` -> Fragment volume is
    2x (the double).
    """
    ParameterValidator.validate_mandatory_number_between('volume_gain', volume_gain, -5.0, 5.0)

    return (
        # We minimize the audio (x3) if lower to 1
        audio - abs(audio.dBFS * (1 - volume_gain) * 3)
        if volume_gain < 1 else
        audio + abs(audio.dBFS * (volume_gain - 1))
    )
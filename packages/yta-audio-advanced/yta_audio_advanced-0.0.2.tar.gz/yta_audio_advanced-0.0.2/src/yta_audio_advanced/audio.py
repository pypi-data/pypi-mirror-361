"""
Module to hold the main Audio class that is
capable of obtaining information, modifying
it, applying filters, etc.

The audio isusually presented in 2 columns
format, but depending on the library who is
handling the numpy array, the 2D information
can be different. The 'soundfile' library 
uses the (n_samples, n_channels) format while
the 'librosa' (mono = False) uses the 
(n_channels, n_samples) format.

TODO: Check the 'util.valid_audio(y)' within
the 'librosa' lib because it seems interesting
to validate a numpy audio array.
"""
from yta_audio_base.audio import Audio as BaseAudio
from yta_audio_advanced_filters import Filters
from yta_validation.parameter import ParameterValidator

import numpy as np


class Audio(BaseAudio):
    """
    Class to represent and wrap a sound that is
    a numpy array to be able to work with it in
    an easy way, but with advanced functionality
    apart from the basic one inherited from the
    'yta_audio_base' Audio class.
    """

    def __init__(
        self,
        audio: 'np.ndarray',
        sample_rate: int = 44_100,
    ):
        super().__init__(audio, sample_rate)

    """
    Filters below. You can find 'with_' and 'apply_'
    methods below. The 'with_' returns a copy of the
    numpy array modified, but touching not the
    original audio, and the 'apply_' methods modify
    the original audio instance (and the values of 
    the original array).
    """
    def with_lowpass(
        self
    ) -> 'np.ndarray':
        """
        Get the audio modified by applying a simple
        lowpass filter.
        """
        return Filters.low_pass(self.audio.copy(), self.sample_rate, self.number_of_channels)

    def apply_lowpass(
        self
    ) -> 'np.ndarray':
        """
        Modify the audio in the instance with the one
        after the low pass effect is applied.
        """
        self.audio = self.with_lowpass()

        return self.audio
    
    def with_fadeout(
        self,
        duration: float
    ) -> 'np.ndarray':
        """
        Get the audio with a fade out effect applied. This
        method does not modify the original audio but 
        returns the audio modified.
        """
        ParameterValidator.validate_mandatory_positive_float('duration', duration, do_include_zero = False)

        return Filters.fadeout(self.audio.copy(), self.sample_rate, duration)
    
    def apply_fadeout(
        self,
        duration: float
    ) -> 'np.ndarray':
        """
        Modify the audio instance by applying a fade
        out filter and return the audio modified.
        """
        self.audio = self.with_fadeout(duration)

        return self.audio
    
    def with_fadein(
        self,
        duration: float
    ) -> 'np.ndarray':
        """
        Get the audio with a fade in effect applied. This
        method does not modify the original audio but 
        returns the audio modified.
        """
        ParameterValidator.validate_mandatory_positive_float('duration', duration, do_include_zero = False)

        return Filters.fadein(self.audio.copy(), self.sample_rate, duration)
    
    def apply_fadein(
        self,
        duration: float
    ) -> 'np.ndarray':
        """
        Modify the audio instance by applying a fade
        in filter and return the audio modified.
        """
        self.audio = self.with_fadein(duration)

        return self.audio
    
    # TODO: Other modifying methods below
    def with_time_stretch(
        self,
        rate: float = 0.5
    ):
        """
        Get the audio with a time stretch effect
        applied, which means changing the audio 
        duration without changing the pitch. This
        method does not modify the original audio but 
        returns the audio modified.

        TODO: Explain the 'rate' better.
        """
        ParameterValidator.validate_mandatory_positive_float('rate', rate, do_include_zero = False)

        return Filters.time_stretch(self.audio.copy(), rate)
    
    def apply_time_stretch(
        self,
        rate: float = 0.5
    ):
        """
        Modify the audio instance by applying a time
        stretch filter, which means changing the audio
        duration without changing the pitch, and
        return the audio modified.
        """
        self.audio, self.sample_rate = self.with_time_stretch(rate)

        return self.audio
    
    def with_pitch_shift(
        self,
        n_steps: int
    ):
        """
        Get the audio with a pitch shift effect applied,
        which means changing the pitch but not the audio
        duration. This method does not modify the
        original audio but returns the audio modified.

        TODO: Explain 'n_steps' better.
        """
        ParameterValidator.validate_mandatory_positive_int('n_steps', n_steps, do_include_zero = False)

        return Filters.pitch_shift(self.audio.copy(), self.sample_rate, n_steps)
    
    def apply_pitch_shift(
        self,
        n_steps: int
    ):
        """
        Modify the audio instance by applying a pitch
        shifting filter, which means changing the pitch
        without changing the audio duration, and return
        the audio modified.
        """
        self.audio, self.sample_rate = self.with_pitch_shift(n_steps)

        return self.audio
    
    def with_fft(
        self
    ):
        """
        Get the audio with a fft effect applied, which
        means looking for the Fourier spectrum per
        channel. This method does not modify the
        original audio but returns the audio modified.
        """
        return Filters.fft(self.audio.copy())

    def apply_fft(
        self
    ):
        """
        Modify the audio instance by applying an fft
        filter, which means looking for the Fourier
        spectrum per channel, and return the audio
        modified.
        """
        self.audio = self.with_fft()

        return self.audio
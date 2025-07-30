"""
Validator for the functionality related
to the moviepy library, which involves
libraries like 'yta_video_base' or 
similar.
"""
from yta_numpy.validator.moviepy.utils import _is_moviepy_mask_frame, _is_moviepy_normal_frame, _is_moviepy_normal_or_mask_frame
from yta_validation.parameter import ParameterValidator


class MoviepyNumpyFrameValidator:
    """
    Class to wrap functionality related to
    validate moviepy video frames, that are
    numpy arrays.
    """

    @staticmethod
    def is_normal_or_mask_frame(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a 
        valid moviepy normal or mask video
        frame.

        Normal:
        - `ndim == 3`
        - `shape[2] == 3`
        - `dtype == np.uint8`

        A valid frame would be like this:
        - `(720, 1080, 3)`

        Mask:
        - `ndim == 2`
        - `dtype in [np.float32, np.float64]`
        - each value is in `[-1.0, 1.0]` range

        A valid frame would be like this:
        - `(720, 1080)`
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        return _is_moviepy_normal_or_mask_frame(frame)

    @staticmethod
    def is_normal_frame(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a 
        valid moviepy normal video frame,
        which is:

        - `ndim == 3`
        - `shape[2] == 3`
        - `dtype == np.uint8`

        A valid frame would be like this:
        - `(720, 1080, 3)`
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        return _is_moviepy_normal_frame(frame)
    
    def is_mask_frame(
       frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a 
        valid moviepy mask video frame,
        which is:

        - `ndim == 2`
        - `dtype in [np.float32, np.float64]`
        - each value is in `[-1.0, 1.0]` range

        A valid frame would be like this:
        - `(720, 1080)`
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        return _is_moviepy_mask_frame(frame)
from yta_validation.parameter import ParameterValidator
from yta_validation.number import NumberValidator
from yta_validation import PythonValidator

import numpy as np


MASK_FRAME_TOLERANCE  = 1e-6
# TODO: Move this to another file,
# it is not a utils
# TODO: Implement testing
class MoviepyVideoFrameHandler:
    """
    Class to wrap the functionality related
    to handle and manipulate numpy arrays
    that are moviepy normal or mask frame
    arrays.
    """

    @staticmethod
    def validate(
        frame: 'np.ndarray'
    ) -> None:
        """
        Check if the provided 'frame' is a
        numpy array valid as a moviepy mask
        or normal frame numpy array and
        raise an exception if not.
        """
        if not MoviepyVideoFrameHandler.is_normal_or_mask_frame(frame):
            raise Exception('The "frame" provided is not a valid moviepy normal or mask frame')
        
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
        return (
            MoviepyVideoNormalFrameHandler.is_normal_frame(frame) or
            MoviepyVideoMaskFrameHandler.is_mask_frame(frame)
        )

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
        return MoviepyVideoNormalFrameHandler.is_normal_frame(frame)
    
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
        return MoviepyVideoMaskFrameHandler.is_mask_frame(frame)


class MoviepyVideoMaskFrameHandler:
    """
    Class to wrap the functionality related
    to handle and manipulate numpy arrays
    that are moviepy mask frame arrays.
    """

    @staticmethod
    def validate(
        frame: 'np.ndarray'
    ) -> None:
        """
        Check if the provided 'frame' is a
        numpy array valid as a moviepy mask
        frame numpy array and raise an
        exception if not.
        """
        if not MoviepyVideoMaskFrameHandler.is_mask_frame(frame):
            raise Exception('The "frame" provided is not a valid moviepy mask frame')
        
    @staticmethod
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

    @staticmethod
    def generate_random(
        width: int,
        height: int
    ) -> 'np.ndarray':
        """
        Generate a random numpy array that
        is valid as a moviepy video mask
        frame. The numpy array will have 
        the (width, height) shape, where
        each value is in the [0.0, 1.0]
        range.
        """
        ParameterValidator.validate_mandatory_positive_int('width', width, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('height', height, do_include_zero = False)

        return np.random.rand(height, width).astype(np.float32)
    
    @staticmethod
    def generate(
        width: int,
        height: int,
        opacity: float = 0.0
    ) -> 'np.ndarray':
        """
        Get a numpy array with the 'width'
        and 'height' provided that will
        have the also provided 'opacity'
        for each of the pixels. The
        'opacity' must be a value between
        0.0 (full transparent) and 1.0
        (full opaque).
        """
        ParameterValidator.validate_mandatory_positive_int('width', width, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('height', height, do_include_zero = False)
        ParameterValidator.validate_mandatory_number_between('opacity', opacity, 0.0, 1.0)

        return np.full((height, width), fill_value = opacity, dtype = np.float32)

    @staticmethod
    def is_full_opaque(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a
        full opaque numpy array that works
        as a moviepy video mask frame.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        MoviepyVideoMaskFrameHandler.validate(frame)

        return np.all(np.abs(frame - 1.0) < MASK_FRAME_TOLERANCE)

    @staticmethod
    def is_full_transparent(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a
        full transparent numpy array that
        works as a moviepy video mask frame.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        MoviepyVideoMaskFrameHandler.validate(frame)

        return np.all(frame < MASK_FRAME_TOLERANCE)
    
    @staticmethod
    def has_full_transparent_pixel(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a
        numpy array that has, at least, one
        full transparent pixel and that 
        works as a moviepy video mask frame.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        MoviepyVideoMaskFrameHandler.validate(frame)

        return np.any(frame < MASK_FRAME_TOLERANCE)
    
    @staticmethod
    def has_transparent_pixel(
        frame: 'np.ndarray'
    ) -> bool:
        """
        Check if the provided 'frame' is a
        numpy array that has, at least, one
        partially transparent pixel and that
        works as a moviepy video mask frame.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)

        MoviepyVideoMaskFrameHandler.validate(frame)

        return np.any((frame > MASK_FRAME_TOLERANCE) & (frame < 1.0 - MASK_FRAME_TOLERANCE))

class MoviepyVideoNormalFrameHandler:
    """
    Class to wrap the functionality related
    to handle and manipulate numpy arrays
    that are moviepy rgb normal frame arrays.
    """

    @staticmethod
    def validate(
        frame: 'np.ndarray'
    ) -> None:
        """
        Check if the provided 'frame' is a
        numpy array valid as a moviepy RGB
        frame numpy array and raise an
        exception if not.
        """
        if not MoviepyVideoNormalFrameHandler.is_normal_frame(frame):
            raise Exception('The "frame" provided is not a valid moviepy normal RGB frame')
        
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
        
    @staticmethod
    def generate_random(
        width: int,
        height: int
    ) -> 'np.ndarray':
        """
        Generate a random numpy array that
        is valid as a moviepy video normal
        frame. The numpy array will have 
        the (width, height, 3) shape, where
        the 3 values will be a RGB array.
        """
        ParameterValidator.validate_mandatory_positive_int('width', width, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('height', height, do_include_zero = False)

        return np.random.randint(0, 256, size = (height, width, 3), dtype = np.uint8)
    
    @staticmethod
    def generate(
        width: int,
        height: int,
        color: list = [255, 255, 255]
    ) -> 'np.ndarray':
        """
        Generate a random numpy array that
        is valid as a moviepy video normal
        frame. The numpy array will have 
        the (width, height, 3) shape, where
        the 3 values will be a RGB array.
        """
        ParameterValidator.validate_mandatory_positive_int('width', width, do_include_zero = False)
        ParameterValidator.validate_mandatory_positive_int('height', height, do_include_zero = False)
        # TODO: Maybe use the 'yta_color' lib to
        # parse and validate
        if not (
            PythonValidator.is_instance(color, [list, np.ndarray]) and
            len(color) == 3 and
            all(
                NumberValidator.is_int(c) and
                0 <= c <= 255 for c in color
            )
        ):
            raise Exception('The "color" provided is not a valid color.')

        return np.full((height, width, 3), color, dtype = np.uint8)
    
    @staticmethod
    def has_all_colors(
        frame: 'np.ndarray',
        colors: list
    ) -> bool:
        """
        Check if the provided 'frame' has the
        also provided 'colors', that must be a
        list of RGB arrays. All the colors must
        be present in the frame.
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)
        # TODO: Validate 'colors' is a list but
        # I don't have the validation method
        
        return _moviepy_normal_frame_has_all_colors(frame, colors)
    
    @staticmethod
    def has_only_colors(
        frame: 'np.ndarray',
        colors: list
    ) -> bool:
        """
        Check if the provided 'frame' has only
        the also provided 'colors', that must
        be a list of RGB arrays. All the
        """
        ParameterValidator.validate_mandatory_numpy_array('frame', frame)
        # TODO: Validate 'colors' is a list but
        # I don't have the validation method

        return _moviepy_normal_frame_has_only_colors(frame, colors)




# Real utils below
def _moviepy_normal_frame_has_all_colors(
    frame: 'np.ndarray',
    colors: list
) -> bool:
    """
    Check if the provided 'frame' has the
    also provided 'colors', that must be a
    list of RGB arrays. All the colors must
    be present in the frame.
    """
    frame_flat = frame.reshape(-1, 3)
    colors = np.array(colors)

    return all(
        np.any(
            np.all(frame_flat == color, axis = 1)
        )
        for color in colors
    )

def _moviepy_normal_frame_has_only_colors(
    frame: 'np.ndarray',
    colors: list
) -> bool:
    """
    Check if the provided 'frame' has only
    the also provided 'colors', that must
    be a list of RGB arrays. All the colors
    in the frame must be the ones provided
    as 'colors' parameter.
    """
    frame_flat = frame.reshape(-1, 3)
    colors = np.array(colors)

    return np.all(
        np.any(
            np.all(frame_flat[:, None] == colors, axis = 2),
            axis = 1
        )
    )

import numpy as np


# Related to the moviepy library below
def _is_moviepy_normal_frame(
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
    return (
        frame.ndim == 3 and
        frame.shape[2] == 3 and
        frame.dtype == np.uint8
    )

def _is_moviepy_mask_frame(
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
    return (
        frame.ndim == 2 and
        frame.dtype in [np.float32, np.float64] and
        #np.issubdtype(frame.dtype, np.floating) and
        (
            frame.min() >= 0.0 and
            frame.max() <= 1.0 
        )
    )

def _is_moviepy_normal_or_mask_frame(
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
    return (
        _is_moviepy_normal_frame(frame) or
        _is_moviepy_mask_frame(frame)
    )
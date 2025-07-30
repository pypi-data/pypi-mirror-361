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
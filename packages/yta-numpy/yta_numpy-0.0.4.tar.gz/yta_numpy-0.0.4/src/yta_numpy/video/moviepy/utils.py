import numpy as np


def frame_has_all_colors(
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

def frame_has_only_colors(
    frame: 'np.ndarray',
    colors: list
) -> bool:
    """
    Check if the provided 'frame' has only
    the also provided 'colors', that must
    be a list of RGB arrays. All the
    """
    frame_flat = frame.reshape(-1, 3)
    colors = np.array(colors)

    return np.all(
        np.any(
            np.all(frame_flat[:, None] == colors, axis = 2),
            axis = 1
        )
    )
from pathlib import Path

def get_root_path(fallback_levels: int = 1) -> Path:
    """
    Returns the root path of the current script or notebook.

    If __file__ is defined (i.e., running in a script), uses it.
    If not (e.g., in a Jupyter notebook), goes up 'fallback_levels' from cwd.

    Args:
        fallback_levels (int): How many levels to go up from cwd if __file__ is undefined.

    Returns:
        Path: The resolved root path.
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:
        path = Path.cwd().resolve()
        for _ in range(fallback_levels):
            path = path.parent
        return path

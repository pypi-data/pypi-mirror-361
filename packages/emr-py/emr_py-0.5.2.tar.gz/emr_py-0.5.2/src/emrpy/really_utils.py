from pathlib import Path


def get_root_path(fallback_levels: int = 0) -> Path:
    """
    Returns the root path based on current working directory.

    Args:
        fallback_levels (int): How many levels to go up from cwd.

    Returns:
        Path: The resolved root path.
    """
    path = Path.cwd().resolve()
    for _ in range(fallback_levels):
        path = path.parent
    return path

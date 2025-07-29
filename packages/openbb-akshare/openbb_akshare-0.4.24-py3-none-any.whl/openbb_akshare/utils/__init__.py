"""AKShare utils directory."""
from openbb_core.app.utils import get_user_cache_directory

def get_cache_path() -> str:
    """
    Get the path for AKShare cache database.

    Returns:
        str: The path to the AKShare cache database.
    """

    return f"{get_user_cache_directory()}/akshare/equity.db"
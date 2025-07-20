# select_dir.py
import os

# Removed the hardcoded base_dir here.
# The base_dir will now be passed as an argument to base_directory()

def base_directory(passed_base_dir=None):
    """
    Returns the base directory for file operations.
    If passed_base_dir is provided, it uses that; otherwise, it raises an error.
    """
    if passed_base_dir:
        # Validate that the passed directory exists and is a directory
        if not os.path.isdir(passed_base_dir):
            raise ValueError(f"Provided path is not a valid directory: {passed_base_dir}")
        return passed_base_dir
    else:
        # This part should ideally not be reached if called correctly with an argument
        # but provides a fallback or clear error if misused.
        raise ValueError("base_directory requires a path to be passed when called dynamically.")
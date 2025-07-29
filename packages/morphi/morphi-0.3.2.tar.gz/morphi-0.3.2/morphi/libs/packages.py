import io
import contextlib
from importlib.resources import files, as_file


def enclose_package_path_exists(package_name):
    """
    Returns a `path_exists` method that searches within the specified package
    """
    # Provides a function to check if a resource exists within the package
    package = files(package_name)
    
    def path_exists(resource_name):
        return (package / resource_name).is_file()
    
    return path_exists


@contextlib.contextmanager
def package_open(package_name, filename):
    """
    Provides a context manager for opening a file within a package.
    If successful, the file will be opened in binary reading mode.

    Example:
        with package_open('some_package', 'path/to/file') as f:
            data = f.read()
    """
    try:
        # Get the resource path from the package
        resource = files(package_name) / filename
        if not resource.is_file():
            raise FileNotFoundError(f"No such file or directory [{package_name}]: {filename}")

        # Ensure the file can be opened as a binary stream
        with as_file(resource) as resource_path:
            with open(resource_path, "rb") as f:
                yield f
    except FileNotFoundError:
        raise IOError(f"No such file or directory [{package_name}]: {filename}")

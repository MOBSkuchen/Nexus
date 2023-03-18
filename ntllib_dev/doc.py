# The following functions / classes are just for better documentation

class RecPathRV:
    """
    Return type of rec_path_search . (list[RecPathRV])
    Hold the values name and amount.
    """
    name: str = None
    amount: int = None


def rec_path_search(path: str, pattern: str) -> list[RecPathRV]:
    """
    Recursively search a path for a pattern (in content)
    :param path:
    Path to search in
    :param pattern:
    Pattern to search file contents for
    :return:
    List of RecPathRV containing filename and amount of matches
    """
    pass


def rec_size(path: str) -> int:
    """
    Return the size of a path (directory)
    :param path:
    The directory's path
    :return:
    Filesize in number of bytes
    """
    pass


def version():
    """
    NTL version -> 0.3.0
    :return:
    NTL version
    """
    pass


def rec_ld(path: str) -> list[str]:
    """
    Recursively get all files in path
    :param path:
    Path
    :return:
    List of files
    """
    pass


def file_search(path: str, pattern: str) -> list[list[int]]:
    """
    Regex search in file
    :param path:
    File
    :param pattern:
    Regex-pattern
    :return:
    List of starting position- and end positions (list[tuple[int, int]])
    """
    pass


def file_get(path: str) -> bytes:
    """
    Get file-content
    :param path:
    File
    :return:
    File content in bytes (Vec<u8>)
    """
    pass


def distance(s1: str, s2: str) -> int:
    """
    Get levenshtein distance of 2 strings
    :param s1:
    String 1
    :param s2:
    String 2
    :return:
    Levenshtein distance
    """
    pass

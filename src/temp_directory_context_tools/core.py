import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional, Union

PathLike = Union[str, Path]


@contextmanager
def temp_cwd(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    dir: Optional[PathLike] = None,
) -> Iterator[str]:
    """Create a temporary directory, chdir into it on entry, restore cwd on exit.

    The directory and its contents are removed on exit, even if an exception is
    raised inside the ``with`` block.

    The original working directory is restored by capturing ``os.getcwd()`` at
    entry and calling ``os.chdir`` on it at exit. We intentionally capture the
    path string rather than a file descriptor, because a file descriptor kept
    open would prevent the original directory from being unmounted on some
    systems if the user intended that. The trade-off is that if the original
    directory is removed by another process while the context is active, the
    chdir-back will fail with FileNotFoundError. That is accepted as a genuine
    edge case: the library assumes the original cwd outlives the context.

    Yields the absolute path to the temporary directory as a string, matching
    what ``tempfile.mkdtemp`` returns.
    """
    original = os.getcwd()
    tmp = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
    try:
        os.chdir(tmp)
        yield tmp
    finally:
        os.chdir(original)
        shutil.rmtree(tmp, ignore_errors=True)

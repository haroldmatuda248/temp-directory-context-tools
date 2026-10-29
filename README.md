# temp-directory-context-tools

A context manager that creates a temporary directory, changes the working directory into it on entry, and restores the original working directory on exit.

```python
from temp_directory_context_tools import temp_cwd

with temp_cwd() as tmp:
    # cwd is now `tmp`; files written with relative paths land here
    with open("output.txt", "w") as f:
        f.write("hello")
# cwd is restored; `tmp` is removed along with everything inside it
```

## Why this exists

Tests and build scripts often need to run against a throwaway working tree without polluting the repository checkout. Doing `mkdtemp` + `chdir` + `rmtree` by hand is repetitive and easy to get wrong — especially the cleanup path when an exception fires mid-block. This wraps the three-step dance into one context manager with no dependencies beyond the standard library.

The trade-off: the original working directory is restored by re-`chdir`ing to the path captured at entry, not by holding a file descriptor. This means if something else deletes the original directory while the context is active, the restore will fail with `FileNotFoundError`. That is a real edge but an accepted one: the library assumes the calling directory outlives the context.

## Edge you will hit

If the original working directory is removed by another process while inside the `with` block, exiting the context will raise `FileNotFoundError` during `os.chdir(original)`. If you cannot guarantee the original directory's lifetime, capture a stable path yourself before entering the context.

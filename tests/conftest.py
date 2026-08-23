"""Narrow Windows workaround for genlayer-test 0.29.x tempfile cleanup.

The direct loader duplicates its temporary message file onto stdin and then
unlinks the still-open Windows handle.  The contract has not been loaded when
the resulting PermissionError is raised.  Defer only that specific unlink;
the handle is closed by the loader and the file is removed after each test.
"""
import os
import tempfile

import pytest


@pytest.fixture(autouse=True)
def _windows_gltest_tempfile_cleanup(monkeypatch):
    if os.name != "nt":
        yield
        return

    deferred = []
    original_unlink = os.unlink

    def unlink(path, *args, **kwargs):
        try:
            return original_unlink(path, *args, **kwargs)
        except PermissionError:
            normalized = os.path.normcase(os.path.abspath(os.fspath(path)))
            temp_root = os.path.normcase(os.path.abspath(tempfile.gettempdir()))
            if normalized.startswith(temp_root + os.sep):
                deferred.append(path)
                return None
            raise

    # loader imports os inside the function, so patch the shared os module
    # for the duration of each test rather than a nonexistent loader.os name.
    monkeypatch.setattr(os, "unlink", unlink)
    yield
    for path in deferred:
        try:
            original_unlink(path)
        except FileNotFoundError:
            pass
        except PermissionError:
            # The loader may still own stdin during fixture teardown; the
            # process-level temp directory cleanup can safely reclaim it.
            pass

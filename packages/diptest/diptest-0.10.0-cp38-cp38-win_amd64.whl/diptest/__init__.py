from __future__ import annotations


# start delvewheel patch
def _delvewheel_patch_1_10_0():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'diptest.libs'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-diptest-0.10.0')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-diptest-0.10.0')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_10_0()
del _delvewheel_patch_1_10_0
# end delvewheel patch

import importlib.metadata
import os

from diptest.diptest import dipstat, diptest
from diptest.lib import _diptest_core as _diptest
from diptest.lib._diptest_core import _has_openmp_support

# Setting the following environment variable allows multiple OpenMP
# libraries to be loaded. This is also used without issue by Scikit-learn.
# OpenMP error msg:
# /* OMP: Error #15: Initializing libomp.dylib, but found libomp.dylib already initialized.
#  * OMP: Hint This means that multiple copies of the OpenMP runtime have been linked into the program.
#  * That is dangerous, since it can degrade performance or cause incorrect results.
#  * The best thing to do is to ensure that only a single OpenMP runtime is linked into the process,
#  * e.g. by avoiding static linking of the OpenMP runtime in any library.
#  * As an unsafe, unsupported, undocumented workaround you can set the environment variable KMP_DUPLICATE_LIB_OK=TRUE
#  * to allow the program to continue to execute, but that may cause crashes or silently produce incorrect results.
#  * For more information, please see http://openmp.llvm.org/
#  */
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "True")

# Workaround issue discovered in intel-openmp 2019.5:
# https://github.com/ContinuumIO/anaconda-issues/issues/11294
os.environ.setdefault("KMP_INIT_AT_FORK", "FALSE")

__version__ = importlib.metadata.version("diptest")

__all__ = ["dipstat", "diptest", "_diptest", "_has_openmp_support", "__version__"]

# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

from .c_get_config cimport is_use_symmetry, is_use_openmp, is_count_perf, \
        is_use_loop_unrolling, is_debug_mode, is_cython_build_in_source, \
        is_cython_build_for_doc, is_use_long_int, is_use_unsigned_long_int


# ==========
# get config
# ==========

def get_config(key=None):
    """
    Returns the definitions used in the compile-time of the package.

    Parameters
    ----------

    key : str, default=None
        A string with one of the following values:
        
        * ``'use_symmetry'``: inquiries if the Gramian matrices are computed
          using symmetric matrix multiplication (when returns `True`), or using
          the full matrix multiplication (when returns `False`).
        * ``'use_openmp'``: inquiries if the package is compiled with OpenMP
          support.
        * ``'count_perf'``: inquiries if counting hardware instructions is
          enabled during the runtime.
        * ``'use_loop_unrolling'``: inquiries if the package is compiled with
          loop unrolling (also known as loop unwinding).
        * ``'debug_mode'``: inquiries if the package is compiled with the
          debugging mode enabled.
        * ``'cython_build_in_source'``: inquiries if the Cython source files
          were generated in the source directory during compilation.
        * ``'cython_build_for_doc'``: inquiries if the docstring for Cython
          functions are generated for the purpose of Sphinx documentation.
        * ``'use_long_int'``: inquiries if the 64-bit long integer type is
          used for array indices at compile time.
        * ``'use_unsigned_long_int'``: inquiries if unsigned 64-bit integer
          type is used for array indices at compile time.

        If `None`, the full list of all above configurations is returned. 

    Returns
    -------

    config : dict
        If a ``key`` input argument is given, a boolean value corresponding to
        the status of the key is returned. If ``key`` is set to `None` or no
        ``key`` is given, a dictionary with all the above keys is returned.

    See Also
    --------

    detkit.get_instructions_per_flop

    Notes
    -----

    To configure the compile-time definitions, export either of these
    variables and set them to ``0`` or ``1`` as applicable:

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export USE_SYMMETRY=1
                    export USE_OPENMP=1
                    export COUNT_PERF=1
                    export USE_LOOP_UNROLLING=1
                    export DEBUG_MODE=1
                    export CYTHON_BUILD_IN_SOURCE=1
                    export CYTHON_BUILD_FOR_DOC=1
                    export USE_LONG_INT=1
                    export USE_UNSIGNED_LONG_INT=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:USE_SYMMETRY = "1"
                    $env:USE_OPENMP = "1"
                    $env:COUNT_PERF = "1"
                    $env:USE_LOOP_UNROLLING = "1"
                    $env:DEBUG_MODE = "1"
                    $env:CYTHON_BUILD_IN_SOURCE = "1"
                    $env:CYTHON_BUILD_FOR_DOC = "1"
                    $env:USE_LONG_INT = "1"
                    $env:USE_UNSIGNED_LONG_INT = "1"

    Examples
    --------

    .. code-block:: python

        >>> from detkit import get_config

        >>> # Using a config key
        >>> get_config('count_perf')
        True

        >>> # Using no key, results in returning all config
        >>> detkit.get_config()
        {
            'use_symmetry': True,
            'use_openmp': False,
            'count_perf': True,
            'use_loop_unrolling': True,
            'debug_mode': False,
            'cython_build_in_source': False,
            'cython_build_for_doc': False,
            'use_long_int': False,
            'use_unsigned_long_int': False,
        }

    The above configuration shows the package was compiled where the symmetric
    matrix multiplication for Gram matrices is enabled, the package supports
    parallelism on shared memory with OpenMP, it can count hardware
    instructions at the runtime, and chunks multiply-add operations to
    improve performance.
    """

    if key is None:
        config = {
            'use_symmetry': bool(is_use_symmetry()),
            'use_openmp': bool(is_use_openmp()),
            'use_loop_unrolling': bool(is_use_loop_unrolling()),
            'count_perf': bool(is_count_perf()),
            'debug_mode': bool(is_debug_mode()),
            'cython_build_in_source': bool(is_cython_build_in_source()),
            'cython_build_for_doc': bool(is_cython_build_for_doc()),
            'use_long_int': bool(is_use_long_int()),
            'use_unsigned_long_int': bool(is_use_unsigned_long_int()),
        }
        return config
    elif key == 'use_symmetry':
        return bool(is_use_symmetry())
    elif key == 'use_openmp':
        return bool(is_use_openmp())
    elif key == 'use_loop_unrolling':
        return bool(is_use_loop_unrolling())
    elif key == 'count_perf':
        return bool(is_count_perf())
    elif key == 'debug_mode':
        return bool(is_debug_mode())
    elif key == 'cython_build_in_source':
        return bool(is_cython_build_in_source())
    elif key == 'cython_build_for_doc':
        return bool(is_cython_build_for_doc())
    elif key == 'use_long_int':
        return bool(is_use_long_int())
    elif key == 'use_unsigned_long_int':
        return bool(is_use_unsigned_long_int())
    else:
        raise ValueError('Invalid "key".')

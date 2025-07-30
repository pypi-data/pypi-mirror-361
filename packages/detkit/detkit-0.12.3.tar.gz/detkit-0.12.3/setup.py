#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the license found in the LICENSE.txt file in the root
# directory of this source tree.


# =======
# Imports
# =======

from __future__ import print_function
import os
from os.path import join
import sys
import platform
from glob import glob
import subprocess
import codecs
import tempfile
import shutil
import multiprocessing
import re
import errno


# ===============
# install package
# ===============

def install_package(package):
    """
    Installs packages using pip.

    Example:

    .. code-block:: python

        >>> install_package('numpy>1.11')

    :param package: Name of package with or without its version pin.
    :type package: string
    """

    subprocess.check_call([sys.executable, "-m", "pip", "install",
                           "--prefer-binary", package])


# =====================
# Import Setup Packages
# =====================

# Install setuptools package
try:
    import setuptools                                               # noqa F401
except ImportError:
    # Install setuptools
    install_package('setuptools')
    import setuptools                                               # noqa F401

from setuptools import Command
from setuptools.extension import Extension
from setuptools.errors import CompileError, LinkError
from setuptools.command.build_ext import build_ext

# Import Cython (to convert pyx to C code)
try:
    from Cython.Build import cythonize
except ImportError:
    # Install Cython
    install_package('cython>=0.29')
    from Cython.Build import cythonize


# =========================
# get environment variables
# =========================

"""
* To build cython files in source, set ``CYTHON_BUILD_IN_SOURCE`` to ``1``.
* To build for documentation, set ``CYTHON_BUILD_FOR_DOC`` to ``1``.
* To compile for debugging, set ``DEBUG_MODE`` environment variable. This will
  increase the executable size.

::

    # In Unix
    export CYTHON_BUILD_IN_SOURCE=1
    export CYTHON_BUILD_FOR_DOC=1
    export USE_CBLAS=0
    export DEBUG_MODE=1

    # In Windows
    $env:CYTHON_BUILD_IN_SOURCE = "1"
    $env:CYTHON_BUILD_FOR_DOC = "1"
    $env:USE_CBLAS = "0"
    $env:DEBUG_MODE = "1"

    python setup.py install

If you are using ``sudo``, to pass the environment variable, use ``-E`` option:

::

    sudo -E python setup.py install

"""

# If DEBUG_MODE is set to "1", the package is compiled with debug mode.
debug_mode = False
if ('DEBUG_MODE' in os.environ) and (os.environ.get('DEBUG_MODE') == '1'):
    debug_mode = True

# If environment var "CYTHON_BUILD_IN_SOURCE" exists, cython builds *.c files
# in the source code, otherwise in "/build" directory
cython_build_in_source = False
if ('CYTHON_BUILD_IN_SOURCE' in os.environ) and \
   (os.environ.get('CYTHON_BUILD_IN_SOURCE') == '1'):
    cython_build_in_source = True

# If this package is build for the documentation, define the environment
# variable "CYTHON_BUILD_FOR_DOC". By doing so, two things happen:
# 1. The cython source will be generated in source (not in build directory)
# 2. The "linetrace" is added to the cython's compiler derivatives.
cython_build_for_doc = False
if ('CYTHON_BUILD_FOR_DOC' in os.environ) and \
   (os.environ.get('CYTHON_BUILD_FOR_DOC') == '1'):
    cython_build_for_doc = True

# If USE_CBLAS is defined and set to 1, it uses OpenBlas library for dense
# vector and matrix operations. In this case, openblas-dev sld be installed.
use_cblas = False
if ('USE_CBLAS' in os.environ) and (os.environ.get('USE_CBLAS') == '1'):
    use_cblas = True

# If USE_LONG_INT is set to 1, 64-bit integers are used for LongIndexType.
# Otherwise, 32-bit integers are used.
use_long_int = None
if 'USE_LONG_INT' in os.environ:
    if os.environ.get('USE_LONG_INT') == '0':
        use_long_int = '0'
    elif os.environ.get('USE_LONG_INT') == '1':
        use_long_int = '1'

# If USE_UNSIGNED_LONG_INT is set to 1, unsigned integers are used for the type
# LongIndexType, which doubles the maximum limit of integers. Otherwise, signed
# integers are used.
use_unsigned_long_int = None
if 'USE_UNSIGNED_LONG_INT' in os.environ:
    if os.environ.get('USE_UNSIGNED_LONG_INT') == '0':
        use_unsigned_long_int = '0'
    elif os.environ.get('USE_UNSIGNED_LONG_INT') == '1':
        use_unsigned_long_int = '1'

# Is USE_OPENMP is set to 1, the matrix and vector multiplications are
# performed on shared memory in parallel using openmp.
use_openmp = None
if 'USE_OPENMP' in os.environ:
    if os.environ.get('USE_OPENMP') == '0':
        use_openmp = '0'
    elif os.environ.get('USE_OPENMP') == '1':
        use_openmp = '1'

# If COUNT_PERF set to 1, the functions will count the hardware instructions
# used to compute a task. This functionality is only available on Linux and
# requires perf_tool to be installed.
count_perf = None
if 'COUNT_PERF' in os.environ:
    if os.environ.get('COUNT_PERF') == '0':
        count_perf = '0'
    elif os.environ.get('COUNT_PERF') == '1':
        count_perf = '1'

# If USE_LOOP_UNROLLING is set to 1, the matrix-matrix multiplications are
# performed in chinks of 5 consecutive additions, similar to BLAS.
use_loop_unrolling = None
if 'USE_LOOP_UNROLLING' in os.environ:
    if os.environ.get('USE_LOOP_UNROLLING') == '0':
        use_loop_unrolling = '0'
    elif os.environ.get('USE_LOOP_UNROLLING') == '1':
        use_loop_unrolling = '1'

# If USE_SYMMETRY is set to 1, the computation of Gramian matrices is performed
# by only half of the matrix multiplication and the other half is obtained by
# Gramian matrix symmetry.
use_symmetry = None
if 'USE_SYMMETRY' in os.environ:
    if os.environ.get('USE_SYMMETRY') == '0':
        use_symmetry = '0'
    elif os.environ.get('USE_SYMMETRY') == '1':
        use_symmetry = '1'


# =====================
# get avail num threads
# =====================

def get_avail_num_threads():
    """
    Finds the number of CPU threads that is granted to the current user. This
    may not be all CPU threads on the machine, for instance, when the user
    requested a certain number of threads when submitting jobs to SLURM or
    Torque workload managers.

    Suppose on a machine with 8 threads, a SLURM job with --cpus-per-task=5
    is submitted.

    This function finds these quantities:

        a  = multiprocessing.cpu_count()  (here 8)    (all os)
        b  = $(nproc)                     (here 5)    (unix only)
        c  = num affinity                 (here 5)    (unit only)
        s1 = SLURM_CPUS_PER_TASK          (here 5)    (slurm only)
        s2 = SLURM_CPUS_ON_NODE           (here 5)    (slurm only)
        t1 = PBS_NUM_PPN                  (here 0)    (torque only)

    We define avail num thread as: min(a, b, c, max(1, s1, s2, t1)).
    """

    avail_num_threads = multiprocessing.cpu_count()

    # Num processors (unix only)
    try:
        # nproc might need to be installed on macos
        if platform.system() in ["Linux", "Darwin"]:
            nproc_output = subprocess.check_output(['nproc'], text=True)
            nproc = int(nproc_output.strip())
            if nproc < avail_num_threads:
                avail_num_threads = nproc
    except Exception:
        pass

    # Check number of available processors using affinity
    if hasattr(os, 'sched_getaffinity'):
        num_affinity = len(os.sched_getaffinity(0))
        if num_affinity < avail_num_threads:
            avail_num_threads = num_affinity

    # Query whether the number of threads are limited by SLURM, Torque, etc.
    querying_num_threads = []

    # SLURM CPUs per task
    slurm_cpus_per_task = os.getenv('SLURM_CPUS_PER_TASK')
    if slurm_cpus_per_task is not None:
        # For heterogeneous computing the number of cpu is a list
        slurm_cpus_per_task_list = \
            [int(cpu) for cpu in slurm_cpus_per_task.split(',')]
        querying_num_threads += slurm_cpus_per_task_list

    # SLURM CPUs on node
    slurm_cpus_on_node = os.getenv('SLURM_CPUS_ON_NODE')
    if slurm_cpus_on_node is not None:
        # For heterogeneous computing the number of cpu is a list
        slurm_cpus_on_node_list = \
            [int(cpu) for cpu in slurm_cpus_on_node.split(',')]
        querying_num_threads += slurm_cpus_on_node_list

    # Torque number of processes per task
    pbs_num_ppn = os.getenv('PBS_NUM_PPN')
    if pbs_num_ppn is not None:
        querying_num_threads.append(int(pbs_num_ppn))

    # Find maximum of the query
    if len(querying_num_threads) > 0:
        max_querying_num_threads = max(querying_num_threads)

        # The max of query can be a candidate if it is more than one thread
        if ((max_querying_num_threads > 0) and
                (max_querying_num_threads < avail_num_threads)):

            # Max of query should not be more than the actual number of threads
            avail_num_threads = max_querying_num_threads

    return avail_num_threads


# ================
# clean extensions
# ================

def clean_extensions(extensions):
    """
    If the package is build for documentation (cython_build_for_doc=True), then
    the extensions are built using --inplace option, which means all cython
    generated files (*.c, *.cpp, *.so) will be generated inside the source
    code.

    To get rid of these files, just run

        python setup.py clean

    This command (which is implemented by this function) searches for all
    *.pyx files in the extensions, then checks if a similar filename to the
    *.pyx file but with *.c, *.cpp, or *.so file extension exists. If yes,
    then it checks whether the first line of that file the *.c and *.cpp file
    is "/* Generated by Cython ...". If yes, it deletes that file.
    """

    # ======================
    # check cython generated
    # ======================

    def check_cython_generated(filename):
        """
        Reads the first line of file and checks if it starts with the line
        "/* Generated by Cython". If yes, it returns `True`. Otherwise, it
        returns `False`.
        """

        with open(filename) as file:
            lines = file.read()
            first = lines.split('\n', 1)[0]

            if (first.startswith('/* Generated by Cython')) or \
               ('failed Cython compilation' in first):
                return True
            else:
                return False

        # ---------

    # Iterate over all extensions of the package
    for extension in extensions:

        # Each extension has multiple source files (*.pyx, *.py, *,cpp, etc)
        for source in extension.sources:

            # Some of the source files are not specific, rather are a wildcards
            # that could indicate a series of files. Here we glob them to file
            # all matches.
            files = glob(source)

            # Iterate through each matched file in a wildcard source
            for file in files:

                # Get path, base ans extension of the file
                base_ext = os.path.basename(file)
                base, _ = os.path.splitext(base_ext)
                path_base, ext = os.path.splitext(file)
                path = os.path.dirname(path_base)

                # Status of finding files to be deleted
                found_h = False
                found_c = False
                found_cpp = False
                found_lib = False

                if ext == '.pyx':

                    # Search for generated Ch file corresponding to *.pxd file
                    h_file = path_base + '.h'
                    if os.path.exists(h_file):
                        if check_cython_generated(h_file):
                            os.remove(h_file)
                            found_h = True

                    # Search for generated C file corresponding to *.pyx file
                    c_file = path_base + '.c'
                    if os.path.exists(c_file):
                        if check_cython_generated(c_file):
                            os.remove(c_file)
                            found_c = True

                    # Search for generated Cpp file corresponding to *.pyx file
                    cpp_file = path_base + '.cpp'
                    if os.path.exists(cpp_file):
                        if check_cython_generated(cpp_file):
                            os.remove(cpp_file)
                            found_cpp = True

                    # Search for generated *.so file corresponding to *.pyx
                    lib_files = \
                        glob(os.path.join(path, '*.so')) + \
                        glob(os.path.join(path, '*.dll')) + \
                        glob(os.path.join(path, '*.dylib'))
                    for lib_file in lib_files:
                        lib_file_base = os.path.basename(lib_file)
                        if lib_file_base.startswith(base):
                            os.remove(lib_file)
                            found_lib = True

                    # Print removed files
                    if found_h or found_c or found_cpp or found_lib:
                        print('Detects: %s' % file)
                        if found_h:
                            print('Removes: %s' % h_file)
                        if found_c:
                            print('Removes: %s' % c_file)
                        if found_cpp:
                            print('Removes: %s' % cpp_file)
                        if found_lib:
                            print('Removes: %s' % lib_file)
                        print('')


# =======================
# check compiler has flag
# =======================

def check_compiler_has_flag(compiler, compile_flags, link_flags):
    """
    Checks if the C compiler has a given flag. The motivation for this function
    is that:

    * In Linux, the gcc compiler has ``-fopenmp`` flag, which enables compiling
      with OpenMP.
    * In macOS, the clang compiler does not recognize ``-fopenmp`` flag,
      rather, this flag should be passed through the preprocessor using
      ``-Xpreprocessor -fopenmp``.

    Thus, we should know in advance which compiler is employed to provide the
    correct flags. The problem is that in the setup.py script, we cannot
    determine if the compiler is gcc or clang. The closet we can get is to call

    .. code-block:: python

        >>> import distutils.ccompiler
        >>> print(distutils.ccompiler.get_default_compiler())

    In both Linux and macOS, the above line returns ``unix``, and in windows it
    returns ``msvc`` for Microsoft Visual C++. In the case of Linux and macOS,
    we cannot figure which compiler is being used as both outputs are the same.
    The safest solution so far is this function, which compilers a small c code
    with a given ``flag_name`` and checks if it compiles successfully. In case
    of ``unix``, if it compiles with ``-fopenmp``, it is gcc on Linux,
    otherwise it is likely to be the ``clang`` compiler on macOS.

    :param compiler: The compiler object from build_ext.compiler
    :type compiler: build_ext.compiler

    :param compile_flags: A list of compile flags, such as
        ``['-Xpreprocessor','-fopenmp']``
    :type compile_flags: list(string)

    :param link_flags: A list of linker flags, such as
        ``['-Xpreprocessor','-fopenmp']``
    :type link_flags: list(string)
    """

    if "PYODIDE_PACKAGE_ABI" in os.environ:

        # pyodide doesn't support OpenMP
        return False

    compile_success = True
    current_working_dir = os.getcwd()
    temp_dir = tempfile.mkdtemp()
    filename = 'test.cpp'
    code = "#include <omp.h>\nint main(int argc, char** argv) { return(0); }"

    # Considerations for Microsoft visual C++ compiler
    if compiler.compiler_type == "msvc":
        link_flags = link_flags + ['/DLL']

    # Write a code in temp directory
    os.chdir(temp_dir)
    with open(filename, 'wt') as file_obj:
        file_obj.write(code)

    try:
        # Try to compile
        objects = compiler.compile([filename], extra_postargs=compile_flags)

        try:
            # Try to link
            compiler.link_shared_lib(
                objects,
                "testlib",
                extra_postargs=link_flags)

        except (LinkError, TypeError) as error:
            # Linker was not successful
            print(error)
            compile_success = False

    except CompileError as error:
        # Compile was not successful
        print(error)
        compile_success = False

    os.chdir(current_working_dir)
    shutil.rmtree(temp_dir)

    return compile_success


# =================
# get compiler kind
# =================

def _get_compiler_kind(compiler_cxx=None):
    """
    Determines the compiler from the ``CC`` and ``CXX`` environment variables.
    """

    # Get CC or CXX environment variable
    if compiler_cxx is None:
        compiler_cxx = os.getenv('CXX', os.getenv('CC'))

    # Detect compiler
    if compiler_cxx is None:
        compiler_kind = None
    elif re.search(r'msvc', compiler_cxx):
        compiler_kind = 'msvc'
    elif re.search(r'icc|icpc|icpx|icl|icx|icx\-cc|icx\-cl', compiler_cxx):
        compiler_kind = 'intel'
    elif re.search(r'cl(?:\.exe)?$', compiler_cxx, re.IGNORECASE):
        compiler_kind = 'msvc'
    elif re.search(r'clang(?:\+\+)?(?:-\d+(\.\d+){0,2})?$', compiler_cxx):
        compiler_kind = 'clang'
    elif re.search(r'xlc|xlC|xlcpp|bgxlC', compiler_cxx):
        compiler_kind = 'xlc'
    elif re.search(r'gcc|g\+\+|cc|c\+\+', compiler_cxx, re.IGNORECASE):
        compiler_kind = 'gcc'
    else:
        compiler_kind = None

    return compiler_kind


# ======================
# Custom Build Extension
# ======================

class CustomBuildExtension(build_ext):
    """
    Customized ``build_ext`` that provides correct compile and linker flags to
    the extensions depending on the compiler and the operating system platform.

    Default compiler names depending on platform:
        * linux: gcc
        * mac: clang (llvm)
        * windows: msvc (Microsoft Visual C++)

    Compiler flags:
        * gcc   : -O3 -march=native -fno-stack-protector -Wall -fopenmp
        * clang : -O3 -march=native -fno-stack-protector -Wall -Xpreprocessor
                  -fopenmp
        * msvc  : /O2 /Wall /openmp

    Linker flags:
        * gcc   : -fopenmp
        * clang : -Xpreproessor -fopenmp -lomp
        * msvc  : (none)

    Usage:

    This class (CustomBuildExtention) is a child of``build_ext`` class. To use
    this class, add it to the ``cmdclass`` by:

    .. code-block: python

        >>> setup(
        ...     ...
        ...     # cmdclass = {'build_ext' : }                    # default
        ...     cmdclass = {'build_ext' : CustomBuildExtention}  # this class
        ...     ...
        ... )
    """

    # ---------------
    # Build Extension
    # ---------------

    def build_extensions(self):
        """
        Specifies compiler and linker flags depending on the compiler.

        .. warning::

            DO NOT USE '-march=native' flag. By using this flag, the compiler
            optimizes the instructions for the native machine of the build time
            and the executable will not be backward compatible to older CPUs.
            As a result, the package will not be distributable on other
            machines as the installation with the binary wheel crashes on other
            machines with this error:

                'illegal instructions (core dumped).'

            An alternative optimization flag is '-mtune=native', which is
            backward compatible and the package can be installed using wheel
            binary file.
        """

        # Get compiler type. This is "unix" (linux, mac) or "msvc" (windows)
        compiler_type = self.compiler.compiler_type

        # Get c++ compiler name obtained from CXX flag (such as "icpx"')
        if hasattr(self.compiler, 'compiler_cxx'):
            compiler_cxx = self.compiler.compiler_cxx
            if isinstance(compiler_cxx, list):
                compiler_cxx = compiler_cxx[0]
        else:
            compiler_cxx = None

        # Kind of compiler (such as "intel" when compiler_cxx is "icpx")
        compiler_kind = _get_compiler_kind(compiler_cxx)

        # Initialize flags
        extra_compile_args = []
        extra_link_args = []

        if compiler_type == 'msvc':

            # This is Microsoft Windows Visual C++ compiler
            msvc_compile_args = ['/O2', '/Wall']
            msvc_link_args = []

            # Adding openmp flags
            if use_openmp:

                msvc_compile_args += ['/openmp']
                msvc_has_openmp_flag = check_compiler_has_flag(
                    self.compiler,
                    msvc_compile_args,
                    msvc_link_args)

                if not msvc_has_openmp_flag:

                    # It does not seem msvc accept /openmp flag.
                    raise RuntimeError(
                        "OpenMP isn't available on %s compiler."
                        % compiler_type)

            # Add all flags
            extra_compile_args += msvc_compile_args
            extra_link_args += msvc_link_args

        elif (compiler_kind == 'intel') and (sys.platform == 'win32'):

            # This is Intel OneAPI compiler on Windows
            icx_compile_args = ['/O2', '/Wall']
            icx_link_args = []

            # Adding openmp flags
            if use_openmp:

                icx_compile_args += ['/Qiopenmp']
                icx_has_qopenmp_flag = check_compiler_has_flag(
                    self.compiler,
                    icx_compile_args,
                    icx_link_args)

                if not icx_has_qopenmp_flag:

                    # It does not seem icx accept /Qopenmp flag.
                    raise RuntimeError(
                        "OpenMP isn't available on %s compiler."
                        % compiler_kind)

            # Add all flags
            extra_compile_args += icx_compile_args
            extra_link_args += icx_link_args

        else:

            # The compile_type is 'unix'. This is either linux or mac.
            # We add common flags that work both for intel, gcc, and clang
            extra_compile_args += ['-O3', '-funroll-loops', '-fno-common',
                                   '-fno-stack-protector', '-fno-wrapv',
                                   '-pedantic', '-Wall', '-Wextra', '-Wundef',
                                   '-Wcast-align', '-Wunreachable-code',
                                   '-Wswitch-enum', '-Wpointer-arith',
                                   '-Wwrite-strings', '-Wsign-compare',
                                   '-Wformat=2', '-Wstrict-overflow=2',
                                   '-Winit-self', '-Woverflow', '-Wpacked',
                                   '-Wmissing-declarations',
                                   '-Wstack-protector',
                                   '-Wvolatile-register-var', '-Wfatal-errors']

            # Add optimization to linker to avoid intel's
            # "-Rno-debug-disables-optimization" remark.
            extra_link_args += ['-O3']

            # Verbose output
            # extra_compile_args += ['--verbose']
            # extra_link_args += ['--verbose']

            # Interprocedural pointer analysis optimizations
            # Note: on macOS, gcc is actually an alias for clang, which does
            # not accept this flag.
            if (compiler_kind == 'gcc') and (platform.system() != 'Darwin'):
                extra_compile_args += ['-fipa-pta']

            # Adding openmp flags
            if use_openmp:

                # Assume compiler is intel (we do not know yet). Check if the
                # compiler accepts '-fiopenmp' flag. Note: gcc does not accept
                # this flag alone, but icpx does.
                icpx_compile_args = ['-fiopenmp']
                icpx_link_args = ['-fiopenmp']
                icpx_has_fiopenmp_flag = check_compiler_has_flag(
                    self.compiler,
                    icpx_compile_args,
                    icpx_link_args)

                if icpx_has_fiopenmp_flag:

                    # Assuming this is gcc. Add '-fiopenmp' safely.
                    extra_compile_args += icpx_compile_args
                    extra_link_args += icpx_link_args

                else:

                    # Assume compiler is gcc or llvm clang, not apple clang (we
                    # do not know yet). Check if the compiler accepts
                    # '-fopenmp' flag. Note: apple clang in mac (not llvm
                    # clang) does not accept this flag alone but gcc and llvm
                    # clang do.
                    gcc_or_clang_compile_args = ['-fopenmp']
                    gcc_or_clang_link_args = ['-fopenmp']
                    gcc_or_clang_has_fopenmp_flag = check_compiler_has_flag(
                        self.compiler,
                        gcc_or_clang_compile_args,
                        gcc_or_clang_link_args)

                    if gcc_or_clang_has_fopenmp_flag:

                        # Assuming this is gcc. Add '-fopenmp' safely.
                        extra_compile_args += gcc_or_clang_compile_args
                        extra_link_args += gcc_or_clang_link_args

                    else:

                        # Assume compiler is apple clang, not llvm clang, (but
                        # we do not know yet). Check if -fopenmp can be passed
                        # through preprocessor. This is how clang compiler
                        # accepts -fopenmp argument
                        apple_clang_compile_args = [
                            '-Xpreprocessor', '-fopenmp']
                        apple_clang_link_args = [
                            '-Xpreprocessor', '-fopenmp', '-lomp',
                            '-headerpad_max_install_names']
                        apple_clang_has_fopenmp_flag = check_compiler_has_flag(
                            self.compiler,
                            apple_clang_compile_args,
                            apple_clang_link_args)

                        if apple_clang_has_fopenmp_flag:

                            # Assuming this is mac's clang. Add '-fopenmp'
                            # through preprocessor
                            extra_compile_args += apple_clang_compile_args
                            extra_link_args += apple_clang_link_args

                        else:

                            # It doesn't seem either intel, gcc, or clang
                            # accept any openmp flag.
                            raise RuntimeError(
                                "OpenMP isn't available on %s compiler."
                                % compiler_kind)

        # Debugging flags should come after all other flags
        if debug_mode:
            # Use -g for all compilers except msvc
            if compiler_type == 'msvc':
                extra_compile_args += ['/Zi']
            else:
                extra_compile_args += ['-g']
                extra_link_args += ['-g']
        else:
            extra_compile_args += ['-g0']
            extra_link_args += ['-g0']

            # The option '-Wl, ..' will send arguments to the linker. Here,
            # '--strip-all' removes all symbols from the shared library.
            if compiler_kind == 'gcc':
                extra_compile_args += ['-Wl, --strip-all']

        # Add the flags to all extensions
        for ext in self.extensions:
            ext.extra_compile_args = extra_compile_args
            ext.extra_link_args = extra_link_args

        # Parallel compilation (can also be set via build_ext -j or --parallel)
        # Note: parallel build often fails (especially in windows) since object
        # files are accessed by race condition. In MSVC, this usually ends up
        # with C1083 error code: "Cannot open compiler generated code", since
        # due to race condition, one threads locks an object file, preventing
        # other threads to link the object file. On gcc and clang, so far, the
        # parallel compilation seems to be fine.
        if sys.platform != 'win32':
            self.parallel = get_avail_num_threads()

        # Remove warning: command line option '-Wstrict-prototypes' is valid
        # for C/ObjC but not for C++
        try:
            if '-Wstrict-prototypes' in self.compiler.compiler_so:
                self.compiler.compiler_so.remove('-Wstrict-prototypes')
        except (AttributeError, ValueError):
            pass

        # Call parent class to build
        build_ext.build_extensions(self)


# =========
# Read File
# =========

def read_file(filename):
    """
    Reads a file with Latin codec.
    """

    with codecs.open(filename, 'r', 'latin') as file_obj:
        return file_obj.read()


# ================
# Read File to RST
# ================

def read_file_to_rst(filename):
    """
    Reads a markdown text file and converts it to RST file using pandas.
    """

    try:
        import pypandoc
        rstname = "{}.{}".format(os.path.splitext(filename)[0], 'rst')
        pypandoc.convert(
            filename,
            'rst',
            format='markdown',
            outputfile=rstname)

        with open(rstname, 'r') as f:
            rststr = f.read()
        return rststr
    except ImportError:
        return read_file(filename)


# ================
# create Extension
# ================

def create_extension(
        package_name,
        subpackage_name,
        other_source_dirs=None,
        other_source_files=None,
        other_include_dirs=None,
        library_dirs=None,
        runtime_library_dirs=None,
        libraries=None,
        define_macros=None):
    """
    Creates an extension for each of the sub-packages that contain
    ``.pyx`` files.

    How to add a new cython sub-package or module:

    In the :func:`main` function, add the name of cython sub-packages or
    modules in the `subpackages_names` list. Note that only include those
    sub-packages in the input list that have cython's *.pyx files. If a
    sub-package is purely python, it should not be included in that list.

    Compile arguments:

        The compiler and linker flags (``extra_compile_args`` and
        ``extra_link_args``) are set to an empty list. We will fill them using
        ``CustomBuildExtension`` class, which depend on the compiler and
        platform, it sets correct flags.

    Parameters:

    :param package_name: Name of the main package
    :type package_name: string

    :param subpackage_name: Name of the subpackage to build its extension.
        In the package_name/subpackage_name directory, all ``pyx``, ``c``,
        ``cpp``, will be added to the extension. If there are additional ``c``,
        ``cpp`` source files in other directories beside the subpackage
        directory, use ``other_source_dirs`` argument.
    :type subpackage_name: string

    :param other_source_dirs: To add any other source files (only ``c``,
        ``cpp``, and ``cu``, but not ``pyx``) that are outside of the
        subpackage directory, use this argument. The ``other_source_dirs`` is
        a list of directories to include their path to ``include_dir`` and
        to add all of the ``c``, ``cpp``, and ``cu`` files to ``sources``.
        Note that the ``pyx`` files in these other directories will not be
        added. To add a ``pyx`` file, use ``subpackage_name`` argument, which
        creates a separate module extension for each ``pyx`` file.
    :type other_source_dirs: list(string)

    :param other_source_files: A list of fullpath names of other source files
        (only ``c``, ``cpp``, and ``cu``), that are not in the
        ``subpackage_name`` directory, neither are in the ``other_source_dirs``
        directory.
    :type other_source_files: list(string)

    :param other_include_dirs: A list of fullpath directories of other source
        files, such as other ``*.cpp`` or ``*.cu`` that are not in the
        directories of ``subpackage_name`` and ``other_source_dirs`` arguments.
    :type other_include_dirs: list(string)

    :param library_dirs: A list of other library directories to be added to the
        linker's -L option at compile time.
    :type library_dirs: list(string)

    :param runtime_library_dirs: A list of library directories to be used at
        the runtime.
    :type runtime_library_dirs: list(string)

    :param libraries: A list of library names to be added to the linker's -l
        flag at the link time.
    :type libraries: list(string)

    :param define_macros: A list of macro definitions to be added to the
        compiler's -D flag at the compile time.
    :type define_macros: list(string)

    :return: Cythonized extension object
    :rtype: dict
    """

    # Check directory
    subpackage_dir_name = join(package_name, subpackage_name)
    if not os.path.isdir(subpackage_dir_name):
        raise ValueError('Directory %s does not exists.' % subpackage_dir_name)

    # Pyx file sources
    pyx_sources = join('.', package_name, subpackage_name, '*.pyx')

    # Either create a module for each pyx file or a module for all cpp files
    if glob(pyx_sources) != []:

        # Creates a directory of modules for each pyx file
        name = package_name + '.' + subpackage_name + '.*'
        sources = [pyx_sources]
    else:
        # Create one so file (not a directory) for all source files (cpp, etc)
        name = package_name + '.' + subpackage_name
        sources = []

    sources += glob(join('.', package_name, subpackage_name, '*.cpp'))

    include_dirs = [join('.', package_name, subpackage_name)]
    extra_compile_args = []  # will be filled by CustomBuildExtension class
    extra_link_args = []     # will be filled by CustomBuildExtension class
    language = 'c++'

    # Note: do not set the default value for these input arguments to []. This
    # leads to an issue known as "default mutable function argument".
    if library_dirs is None:
        library_dirs = []
    if runtime_library_dirs is None:
        runtime_library_dirs = []
    if libraries is None:
        libraries = []
    if define_macros is None:
        define_macros = []

    # When compiled with Cython>=3.0.1, all externs are defined as
    # "extern C++", however, Cython<=0.29.36 uses "extern C". To avoid this
    # disambiguation, here we define CYTHON_EXTERN_C, which is already defined
    # in Cython>=3.0.0 but not defined in lower version. In all C++ codes, I
    # should replace any extern clause with this macro.
    define_macros += [("CYTHON_EXTERN_C", 'extern "C"')]

    # Include any additional source files
    if other_source_files is not None:

        # Check source files exist
        for source_file in other_source_files:
            if not os.path.isfile(source_file):
                raise ValueError('File %s does not exists.' % source_file)

        sources += other_source_files

    # Include any additional include directories
    if other_include_dirs is not None:

        # Check if directories exist
        for include_dir in other_include_dirs:
            package_include_dir = join(package_name, include_dir)
            if not os.path.isdir(package_include_dir):
                raise ValueError('Directory %s does not exists.'
                                 % package_include_dir)

            include_dirs.append(package_include_dir)

    # Glob entire source c, cpp and cu files in other source directories
    if other_source_dirs is not None:

        for other_source_dir in other_source_dirs:

            # Check directory exists
            other_source_dirname = join(package_name, other_source_dir)
            if not os.path.isdir(other_source_dirname):
                raise ValueError('Directory %s does not exists.'
                                 % other_source_dirname)

            sources += glob(join(other_source_dirname, '*.c'))
            sources += glob(join(other_source_dirname, '*.cpp'))
            include_dirs += [join(other_source_dirname)]

    # Using OpenBlas
    if use_cblas:
        libraries += ['openblas']
        define_macros += [('USE_CBLAS', '1')]

    # Define macros if they are set as environment variables (see the header
    # file ./detkit/_definitions/definitions.h)
    if use_long_int is not None:
        define_macros += [('LONG_INT', use_long_int)]
    if use_unsigned_long_int is not None:
        define_macros += [('UNSIGNED_LONG_INT', use_unsigned_long_int)]
    if use_openmp is not None:
        define_macros += [('USE_OPENMP', use_openmp)]
    if count_perf is not None:
        define_macros += [('COUNT_PERF', count_perf)]
    if use_loop_unrolling is not None:
        define_macros += [('USE_LOOP_UNROLLING', use_loop_unrolling)]
    if use_symmetry is not None:
        define_macros += [('USE_SYMMETRY', use_symmetry)]

    # Create an extension
    extension = Extension(
        name,
        sources=sources,
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        runtime_library_dirs=runtime_library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        language=language,
        define_macros=define_macros
    )

    return extension


# ====================
# cythonize extensions
# ====================

def cythonize_extensions(extensions):
    """
    Resolving issue with conda-build:

        If the code is build using "conda-build" to be uploaded on anaconda
        cloud, consider setting this environmental variable:

        ::

            export CYTHON_BUILD_IN_SOURCE='1'

        By setting so, this function sets the build directory ``build_dir``
        to ``None``, which then the ``*.c`` files will be written in the source
        code alongside with the source (where ``*.pyx`` are). If this
        environmental variable does not exist, this function sets ``build_dir``
        to ``build``directory , which builds the cython files outside of the
        source code.

        Why this matters?

        Apparently, ``conda-build`` has a bug and emerges if the following two
        conditions are met:

        1. conda builds over multiple variants of the conda recipe (by defining
           jinja variables in the file ``/conda/conda_build_config.yaml``),
           such as defining multiple python versions and then using the jinja
           variable ``{{ python }}`` in ``/conda/meta.yaml``.

        2. Cython builds the ``*.c`` files outside of the source. That is, when
           we set ``build_dir`` to anything but its default in
           ``cythonize(build_dir='some_directory')``. When  ``build_dir`` is
           set to ``None``, cython builds the ``*.c`` files in source. But when
           ``build_dir`` is set to a directory, the ``*.c`` files will be
           written there.

        Now, when the two above are set, ``conda-build`` faces a race condition
        to build multiple versions of the package for variants of python
        versions (if this is the variant variable), and crashes. Either
        conda-build should build only one variant of the ``meta.yaml`` file
        (that is, defining no variant in ``/conda/conda_build.config.yaml``),
        or cython should build in source.

        To resolve this, set ``CYTHON_BUILD_IN_SOURCE`` whenever the package is
        build with build-conda. Also see the github action
        ``./github/workflow/deploy-conda/yaml``

        ::

            env:
                CYTHON_BUILD_IN_SOURCE: '1'

    Resolving issue with docstring for documentation:

        To build this package only to generate proper cython docstrings for the
        documentation, set the following environment variable:

        ::

            export CYTHON_BUILD_FOR_DOC='1'

        If the documentation is generated by the github actions, set

        ::

            env:
                CYTHON_BUILD_FOR_DOC: '1'

    .. warning::

        DO NOT USE `linetrace=True` for a production code. Only use linetrace
        to generate the documentation. This is because of serious cython bugs
        caused by linetrace feature, particularly the behavior of ``prange``
        becomes unpredictable since it often halts execution of the program.
    """

    # Build in source or out of source
    if bool(cython_build_in_source) or bool(cython_build_for_doc):
        cython_build_dir = None    # builds *.c in source alongside *.pyx files
    else:
        cython_build_dir = 'build'

    # Compiler derivatives
    compiler_directives = {
        'boundscheck': False,
        'cdivision': True,
        'wraparound': False,
        'nonecheck': False,
        'embedsignature': True,
        'language_level': "3",
    }

    # Used for sphinx to find docstring of pyx files
    if bool(cython_build_for_doc):

        # Add cython signatures for sphinx
        for extension in extensions:
            extension.cython_directives = {"embedsignature": True}

        # Bind cython files with python objects
        compiler_directives['binding'] = True

        # Line trace
        # compiler_directives['linetrace'] = True

    # Debugging
    if debug_mode:
        gdb_debug = True
    else:
        gdb_debug = False

    # Cythonize
    cythonized_extensions = cythonize(
        extensions,
        build_dir=cython_build_dir,
        include_path=["."],
        language_level="3",
        nthreads=get_avail_num_threads(),
        compiler_directives=compiler_directives,
        gdb_debug=gdb_debug,
    )

    return cythonized_extensions


# ================
# get requirements
# ================

def get_requirements(directory, subdirectory="", filename='requirements',
                     ignore=False):
    """
    Returns a list containing the package requirements given in a file named
    "requirements.txt" in a subdirectory.

    If `ignore` is `True` and the file was not found, it passes without raising
    error. This is useful when the package is build without
    `docs/requirements.txt` and `tests/requirements.txt`, such as in the docker
    where the folders `docs` and `tests` are not copied to the docker image.
    See `.dockerignore` file.
    """

    requirements_filename = join(directory, subdirectory, filename + ".txt")

    # Check file exists
    if os.path.exists(requirements_filename):
        requirements_file = open(requirements_filename, 'r')
        requirements = [i.strip() for i in requirements_file.readlines()]
    else:
        # Ignore if file was not found.
        if ignore:
            requirements = ''
        else:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), requirements_filename)

    return requirements


# ====
# main
# ====

def main(argv):

    directory = os.path.dirname(os.path.realpath(__file__))
    package_name = "detkit"

    # Version
    version_dummy = {}
    version_file = join(directory, package_name, '__version__.py')
    exec(open(version_file, 'r').read(), version_dummy)
    version = version_dummy['__version__']
    del version_dummy

    # Author
    author_file = join(directory, 'AUTHORS.txt')
    author = open(author_file, 'r').read().rstrip()

    # Requirements
    requirements = get_requirements(directory)
    test_requirements = get_requirements(directory, subdirectory="tests",
                                         ignore=True)
    docs_requirements = get_requirements(directory, subdirectory="docs",
                                         ignore=True)

    # ReadMe
    readme_file = join(directory, 'README.rst')
    long_description = open(readme_file, 'r').read()

    # Cython cpp extensions
    extensions = []

    extensions.append(create_extension(package_name, '_cy_linear_algebra',
                                       other_source_dirs=['_openmp']))

    extensions.append(create_extension(package_name, '_functions',
                                       other_source_dirs=[
                                           '_c_basic_algebra',
                                           '_c_linear_algebra',
                                           '_utilities',
                                           '_openmp',
                                           '_device']))

    extensions.append(create_extension(package_name, '_benchmark',
                                       other_source_dirs=[
                                           '_c_basic_algebra',
                                           '_c_linear_algebra',
                                           '_utilities',
                                           '_device']))

    extensions.append(create_extension(package_name, '_definitions'))

    extensions.append(create_extension(package_name, '_device'))

    # Cythonize
    if 'clean' in argv:
        # Do not cythonize if setup.py is called for cleaning only
        external_modules = None
    else:
        external_modules = cythonize_extensions(extensions)

    # Description
    description = 'Matrix determinant toolkit'

    # URLs
    url = 'https://github.com/ameli/detkit'
    download_url = url + '/archive/main.zip'
    documentation_url = url + '/blob/main/README.rst'
    tracker_url = url + '/issues'

    # Custom clean to remove cython generated *.c, *.cpp, and *.so files.
    # To clean cython generated files, run "python setup.py clean"
    class CustomClean(Command):

        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            clean_extensions(extensions)

    # Inputs to setup
    metadata = dict(
        name=package_name,
        version=version,
        author=author,
        author_email='sameli@berkeley.edu',
        description=description,
        long_description=long_description,
        long_description_content_type='text/x-rst',
        keywords="""matrix-computations cholesky-decomposition logdet
                matrix-determinant singular-matrix gaussian-process""",
        url=url,
        download_url=download_url,
        project_urls={
            "Documentation": documentation_url,
            "Source": url,
            "Tracker": tracker_url,
        },
        platforms=['Linux', 'OSX', 'Windows'],
        packages=setuptools.find_namespace_packages(exclude=[
            'tests.*',
            'tests',
            'examples.*',
            'examples',
            'benchmark.*',
            'benchmark',
            'docs.*',
            'docs']
        ),
        ext_modules=external_modules,
        install_requires=requirements,
        python_requires='>=3.8',
        setup_requires=[
            'setuptools',
            'scipy>=1.5',
            'cython>=0.29'],
        tests_require=[
            'pytest',
            'pytest-cov'],
        include_package_data=True,
        cmdclass={
            'build_ext': CustomBuildExtension,
            'clean': CustomClean,
        },
        zip_safe=False,  # False: package can be "cimported" by another package
        extras_require={
            'test': test_requirements,
            'docs': docs_requirements,
        },
        classifiers=[
            'Programming Language :: C++',
            'Programming Language :: Cython',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3.11',
            'Programming Language :: Python :: 3.12',
            'Programming Language :: Python :: 3.13',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: MacOS',
            'Natural Language :: English',
            'Intended Audience :: Science/Research',
            'Intended Audience :: Developers',
            'Topic :: Software Development',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Scientific/Engineering',
            'Topic :: Scientific/Engineering :: Mathematics',
            'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
    )

    # Setup
    setuptools.setup(**metadata)


# =============
# script's main
# =============

if __name__ == "__main__":
    main(sys.argv)

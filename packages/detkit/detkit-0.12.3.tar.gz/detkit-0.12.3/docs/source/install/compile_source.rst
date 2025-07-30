.. _compile-source:

Compile from Source
===================

When to Compile |project|
-------------------------

Generally, it is not required to compile |project| as the installation through ``pip`` and ``conda``. You may compile |project| if you want to:

* modify |project|.
* enable `debugging mode`.
* or, build this `documentation`.

Otherwise, install |project| through the :ref:`Python Wheels <install-wheels>`.

This section walks you through the compilation process.

Install C++ Compiler (`Required`)
---------------------------------

You can compile |project| with any of the following compilers:

* `GCC <https://gcc.gnu.org/>`__ (Linux, macOS, Windows via `MinGW <https://www.mingw-w64.org/>`__ or `Cygwin <https://www.cygwin.com/>`__)
* `LLVM/Clang <https://clang.llvm.org/>`__ (Linux, macOS, Windows via `MinGW <https://www.mingw-w64.org/>`__, or LLVM's own Windows support) and `LLVM/Clang by Apple <https://opensource.apple.com/projects/llvm-clang/>`__ 
* `Intel OneAPI <https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html#gs.5c6ir2>`__ (Linux, Windows)
* `Microsoft Visual Studio (MSVC) Compiler for C++ <https://code.visualstudio.com/docs/cpp/config-msvc#:~:text=You%20can%20install%20the%20C,the%20C%2B%2B%20workload%20is%20checked.>`_ (Windows)
* `Arm Compiler for Linux <https://developer.arm.com/Tools%20and%20Software/Arm%20Compiler%20for%20Linux>`__ (Linux on AARCH64 architecture)

Below are short description of setting up a few major compilers:

.. rubric:: Install GNU GCC Compiler

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt install build-essential

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum group install "Development Tools"

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf group install "Development Tools"

    .. tab-item:: macOS
        :sync: osx

        .. prompt:: bash

            sudo brew install gcc libomp

Then, export ``CC`` and ``CXX`` variables by

.. prompt:: bash

  export CC=/usr/local/bin/gcc
  export CXX=/usr/local/bin/g++

.. rubric:: Install Clang/LLVN Compiler
  
.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt install clang libomp-dev

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum install yum-utils
            sudo yum-config-manager --enable extras
            sudo yum makecache
            sudo yum install clang libomp-devel

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf install yum-utils
            sudo dnf config-manager --enable extras
            sudo dnf makecache
            sudo dnf install clang libomp-devel

    .. tab-item:: macOS
        :sync: osx

        .. prompt:: bash

            sudo brew install llvm libomp-dev

Then, export ``CC`` and ``CXX`` variables by

.. prompt:: bash

  export CC=/usr/local/bin/clang
  export CXX=/usr/local/bin/clang++

.. rubric:: Install Intel oneAPI Compiler

To install `Intel Compiler` see `Intel oneAPI Base Toolkit <https://www.intel.com/content/www/us/en/developer/tools/oneapi/overview.html>`__. Once installed, set the compiler's required environment variables by

.. tab-set::

    .. tab-item:: UNIX
        :sync: unix

        .. prompt:: bash

            source /opt/intel/oneapi/setvars.sh

    .. tab-item:: Windows (Powershell)
        :sync: win

        .. prompt:: powershell

            C:\Program Files (x86)\Intel\oneAPI\setvars.bat

In UNIX, export ``CC`` and ``CXX`` variables by

.. prompt:: bash

    export CC=`which icpx`
    export CXX=`which icpx`

.. _install_openmp:

Install OpenMP (`Required`)
---------------------------

OpenMP comes with the C++ compiler installed. However, you may alternatively install it directly on UNIX. Install `OpenMP` library on UNIX as follows:

.. tab-set::

    .. tab-item:: Ubuntu/Debian
        :sync: ubuntu

        .. prompt:: bash

            sudo apt install libgomp1 -y

    .. tab-item:: CentOS 7
        :sync: centos

        .. prompt:: bash

            sudo yum install libgomp -y

    .. tab-item:: RHEL 9
        :sync: rhel

        .. prompt:: bash

            sudo dnf install libgomp -y

    .. tab-item:: macOS
        :sync: osx

        .. prompt:: bash

            sudo brew install libomp

.. note::

    In *macOS*, for ``libomp`` versions ``15`` and above, Homebrew installs OpenMP as *keg-only*. To utilize the OpenMP installation, you should establish the following symbolic links:

    .. prompt:: bash

        libomp_dir=$(brew --prefix libomp)
        ln -sf ${libomp_dir}/include/omp-tools.h  /usr/local/include/omp-tools.h
        ln -sf ${libomp_dir}/include/omp.h        /usr/local/include/omp.h
        ln -sf ${libomp_dir}/include/ompt.h       /usr/local/include/ompt.h
        ln -sf ${libomp_dir}/lib/libomp.a         /usr/local/lib/libomp.a
        ln -sf ${libomp_dir}/lib/libomp.dylib     /usr/local/lib/libomp.dylib

.. _config-env-variables:

Configure Compile-Time Environment Variables (`Optional`)
---------------------------------------------------------

Set the following environment variables as desired to configure the compilation process.

.. glossary::

    ``CYTHON_BUILD_IN_SOURCE``

        By default, this variable is set to `0`, in which the compilation process generates source files outside of the source directory, in ``/build`` directry. When it is set to `1`, the build files are generated in the source directory. To set this variable, run

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export CYTHON_BUILD_IN_SOURCE=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:CYTHON_BUILD_IN_SOURCE = "1"

        .. hint::

            If you generated the source files inside the source directory by setting this variable, and later you wanted to clean them, see :ref:`Clean Compilation Files <clean-files>`.

    ``CYTHON_BUILD_FOR_DOC``

        Set this variable if you are building this documentation. By default, this variable is set to `0`. When it is set to `1`, the package will be built suitable for generating the documentation. To set this variable, run

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export CYTHON_BUILD_FOR_DOC=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:CYTHON_BUILD_FOR_DOC = "1"

        .. warning::

            Do not use this option to build the package for `production` (release) as it has a slower performance. Building the package by enabling this variable is only suitable for generating the documentation.

        .. hint::

            By enabling this variable, the build will be `in-source`, similar to setting ``CYTHON_BUILD_IN_SOURCE=1``. To clean the source directory from the generated files, see :ref:`Clean Compilation Files <clean-files>`.

    ``DEBUG_MODE``

        By default, this variable is set to `0`, meaning that |project| is compiled without debugging mode enabled. By enabling debug mode, you can debug the code with tools such as ``gdb``. Set this variable to `1` to enable debugging mode by

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export DEBUG_MODE=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:DEBUG_MODE = "1"

        .. attention::

            With the debugging mode enabled, the size of the package will be larger and its performance may be slower, which is not suitable for `production`.

    ``LONG_INT``

        When set to `1`, long integers are used. By default, this variable is set to `0`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export LONG_INT=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:LONG_INT = "1"

    ``UNSIGNED_LONG_INT``

        When set to `1`, unsigned long integers are used. By default, this variable is set to `0`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export UNSIGNED_LONG_INT=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:UNSIGNED_LONG_INT = "1"

    ``USE_OPENMP``
        
        To enable shared-memory parallelization uisng OpenMP, set this variable to `1` and make sure OpenMP is installed (see :ref:`Install OpenMP <install_openmp>`). Setting this variable to `0` disables this feature. By default, this variable is set to `0`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export USE_OPENMP=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:USE_OPENMP = "1"

    ``COUNT_PERF``

        When set to `1`, the processor instructions are counted and returned by each function This functionalit is only available on Linux and requires that ``perf_tool`` is installed. By default, this variable is set to `1`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export COUNT_PERF=1

    ``USE_LOOP_UNROLLING``

        When set to `1`, matrix and vector multiplications are peroformed in chunks of 5 conseqqutive addition-multiplication operations. By default, this variable is set to `1`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export USE_LOOP_UNROLLING=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:USE_LOOP_UNROLLING = "1"

    ``USE_SYMMETRY``

        When set to `1`, Gramian matrices are computed using symmetry of the Gamian matrix. By default, this variable is set to `1`.

        .. tab-set::

            .. tab-item:: UNIX
                :sync: unix

                .. prompt:: bash

                    export USE_SYMMETRY=1

            .. tab-item:: Windows (Powershell)
                :sync: win

                .. prompt:: powershell

                    $env:USE_SYMMETRY = "1"

Compile and Install
-------------------

|repo-size|

Get the source code of |project| from the GitHub repository by

.. prompt:: bash

    git clone https://github.com/ameli/detkit.git
    cd detkit

To compile and install, run

.. prompt:: bash

    python -m pip install .

The above command may need ``sudo`` privilege. 

.. rubric:: A Note on Using ``sudo``

If you are using ``sudo`` for the above command, add ``-E`` option to ``sudo`` to make sure the environment variables (if you have set any) are accessible to the root user. For instance

.. tab-set::

    .. tab-item:: UNIX
        :sync: unix

        .. code-block:: Bash

            export CYTHON_BUILD_FOR_DOC=1
            sudo -E python -m pip install .

    .. tab-item:: Windows (Powershell)
        :sync: win

        .. code-block:: PowerShell

            $env:CYTHON_BUILD_FOR_DOC = "1"
            sudo -E python setup.py install

Once the installation is completed, check the package can be loaded by

.. prompt:: bash

    cd ..  # do not load detkit in the same directory of the source code
    python -c "import detkit"

.. attention::

    Do not load |project| if your current working directory is the root directory of the source code of |project|, since python cannot load the installed package properly. Always change the current directory to somewhere else (for example, ``cd ..`` as shown in the above).

.. _clean-files:
   
.. rubric:: Cleaning Compilation Files

If you set ``CYTHON_BUILD_IN_SOURCE`` or ``CYTHON_BUILD_FOR_DOC`` to ``1``, the output files of Cython's compiler will be generated inside the source code directories. To clean the source code from these files (`optional`), run the following:

.. prompt:: bash

    python setup.py clean
    
.. |repo-size| image:: https://img.shields.io/github/repo-size/ameli/detkit
   :target: https://github.com/ameli/detkit

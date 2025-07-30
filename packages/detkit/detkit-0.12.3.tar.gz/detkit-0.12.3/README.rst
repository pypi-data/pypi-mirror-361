******
|logo|
******
.. figure:: https://raw.githubusercontent.com/ameli/detkit/main/docs/source/_static/images/icons/logo-detkit-light.svg
    :align: left
    :width: 240

`Paper <https://openreview.net/pdf?id=nkV9PPp8R8>`__ |
`Slides <https://www.dropbox.com/scl/fi/it8cd6gx3qhl794qk9h1q/memdet_flodance_slides.pdf?rlkey=rc7j6d6lc9svgdvac5psenqzu&e=1&st=kjj6spqy&dl=0>`__ |
`Poster <https://www.dropbox.com/scl/fi/sbdiojqozl8tn95v1r8ws/memdet_flodance_poster.pdf?rlkey=zp6zjpe21cwa37a7t2kvhkelt&st=hm10n9rj&dl=0>`__ |
`Docs <https://ameli.github.io/detkit>`__ |
`API <https://ameli.github.io/detkit/api>`__ |
`PyPI <https://pypi.org/project/detkit/>`__ |
`Anaconda <https://anaconda.org/s-ameli/detkit>`__ |
`Docker Hub <https://hub.docker.com/r/sameli/detkit>`__ |
`Github <https://github.com/ameli/detkit>`__

``detKit`` is a Python package for computing determinant functions of matrices.


Install
=======

Install with ``pip``
--------------------

|pypi|

::

    pip install detkit

Install with ``conda``
----------------------

|conda-version|

::

    conda install s-ameli::detkit

Docker Image
------------

|docker-pull| |deploy-docker|

::

    docker pull sameli/detkit

Supported Platforms
===================

Successful installation and tests performed on the following operating systems, architectures, and Python and `PyPy <https://www.pypy.org/>`__ versions:

.. |y| unicode:: U+2714
.. |n| unicode:: U+2716

+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| Platform | Arch              | Python Version                        | PyPy Version :sup:`1` | Continuous      |
+          |                   +-------+-------+-------+-------+-------+-------+-------+-------+ Integration     +
|          |                   |  3.9  |  3.10 |  3.11 |  3.12 |  3.13 |  3.8  |  3.9  |  3.10 |                 |
+==========+===================+=======+=======+=======+=======+=======+=======+=======+=======+=================+
| Linux    | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-linux|   |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | AARCH-64          |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| macOS    | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-macos|   |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | ARM-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+
| Windows  | X86-64            |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  | |build-windows| |
+          +-------------------+-------+-------+-------+-------+-------+-------+-------+-------+                 +
|          | ARM-64 :sup:`2`   |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |  |y|  |                 |
+----------+-------------------+-------+-------+-------+-------+-------+-------+-------+-------+-----------------+

.. |build-linux| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-linux.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-linux 
.. |build-macos| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-macos.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-macos
.. |build-windows| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/build-windows.yml
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Abuild-windows

Python wheels for ``detkit`` for all supported platforms and versions in the above are available through `PyPI <https://pypi.org/project/detkit/>`__ and `Anaconda Cloud <https://anaconda.org/s-ameli/detkit>`__. If you need ``detkit`` on other platforms, architectures, and Python or PyPy versions, `raise an issue <https://github.com/ameli/detkit/issues>`__ on GitHub and we build its Python Wheel for you.

.. line-block::

    :sup:`1. Wheels for PyPy are exclusively available for installation through pip and cannot be installed using conda.`
    :sup:`2. Wheels for Windows on ARM-64 architecture are exclusively available for installation through pip and cannot be installed using conda.`

Documentation
=============

|deploy-docs| |binder|

See `documentation <https://ameli.github.io/detkit/index.html>`__ of the package.

Benchmark Test
==============

Read about the `benchmark test <https://ameli.github.io/detkit/benchmark.html>`__ of ``detkit`` in practical applications.

How to Contribute
=================

We welcome contributions via `GitHub's pull request <https://github.com/ameli/detkit/pulls>`__. If you do not feel comfortable modifying the code, we also welcome feature requests and bug reports as `GitHub issues <https://github.com/ameli/detkit/issues>`__.

How to Cite
===========

If you publish work that uses ``detkit``, please consider citing the manuscripts available `here <https://ameli.github.io/detkit/cite.html>`__.

.. [1] Ameli, S., and Shadden. S. C. (2023). *A Singular Woodbury and Pseudo-Determinant Matrix Identities and Application to Gaussian Process Regression*. Applied Mathematics and Computation 452, 128032. `doi <https://doi.org/10.1016/j.amc.2023.128032>`__

   .. code::
   
       @article{amc-2023,
           title = {A singular Woodbury and pseudo-determinant matrix identities and application to Gaussian process regression},
           journal = {Applied Mathematics and Computation},
           volume = {452},
           pages = {128032},
           year = {2023},
           issn = {0096-3003},
           doi = {https://doi.org/10.1016/j.amc.2023.128032},
           author = {Siavash Ameli and Shawn C. Shadden},
       }

.. [2] Siavash Ameli, Chris van der Heide, Liam Hodgkinson, Fred Roosta, Michael W. Mahoney (2025). *Determinant Estimation under Memory Constraints and Neural Scaling Laws*. Forty-second International Conference on Machine Learning. `doi <https://openreview.net/forum?id=nkV9PPp8R8>`__

   .. code::

        @inproceedings{
            ameli2025determinant,
            title={Determinant Estimation under Memory Constraints and Neural Scaling Laws},
            author={Siavash Ameli and Chris van der Heide and Liam Hodgkinson and Fred Roosta and Michael W. Mahoney},
            booktitle={Forty-second International Conference on Machine Learning},
            year={2025},
            url={https://openreview.net/forum?id=nkV9PPp8R8}
        }

License
=======

|license|

This project uses a `BSD 3-clause license <https://github.com/ameli/detkit/blob/main/LICENSE.txt>`__, in hopes that it will be accessible to most projects. If you require a different license, please raise an `issue <https://github.com/ameli/detkit/issues>`__ and we will consider a dual license.

.. |logo| image:: https://raw.githubusercontent.com/ameli/detkit/main/docs/source/_static/images/icons/logo-detkit-light.svg
   :width: 160
.. |license| image:: https://img.shields.io/github/license/ameli/detkit
   :target: https://opensource.org/licenses/BSD-3-Clause
.. |deploy-docs| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docs.yml?label=docs
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docs
.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/ameli/detkit/HEAD?filepath=notebooks%2Fquick_start.ipynb
.. |pypi| image:: https://img.shields.io/pypi/v/detkit
   :target: https://pypi.org/project/detkit/
.. |deploy-docker| image:: https://img.shields.io/github/actions/workflow/status/ameli/detkit/deploy-docker.yml?label=build%20docker
   :target: https://github.com/ameli/detkit/actions?query=workflow%3Adeploy-docker
.. |docker-pull| image:: https://img.shields.io/docker/pulls/sameli/detkit?color=green&label=downloads
   :target: https://hub.docker.com/r/sameli/detkit
.. |conda-version| image:: https://img.shields.io/conda/v/s-ameli/detkit
   :target: https://anaconda.org/s-ameli/detkit

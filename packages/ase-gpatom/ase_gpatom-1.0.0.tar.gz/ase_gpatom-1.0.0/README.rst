===================================================================
gpatom: Tools for atomistic simulations based on Gaussian processes
===================================================================

gpatom is a Python package which provides several tools for
geometry optimisation and related tasks in atomistic systems using machine learning surrogate models.
gpatom is an extension to the `Atomic Simulation Environment <https://wiki.fysik.dtu.dk/ase/>`_.

gpatom consists of two independently maintained sub-repositories,
gpatom/aidts-gpmin and gpatom/ase-gpatom.

gpatom/aidts-gpmin includes:
 * GPMin: An atomistic optimization algorithm based on Gaussian processes.
 * AIDMin: Energy structure minimization through the Artificial-Intelligence framework.
 * AIDNEB: Nudged Elastic Band calculations through the Artificial-Intelligence framework.
 * AIDTS: Transition State Search through the Artificial-Intelligence framework.
 * AIDMEP: Minimum Energy Pathway through the Artificial-Intelligence framework.

gpatom/ase-gpatom includes:
 * BEACON: Bayesian Exploration of Atomic CONfigurations.
           BEACON does global optimization by Bayesian optimization
           by training the model with the DFT forces on atoms.
	   Represents the atoms with a global structural fingerprint.
	   Works generally well for different kinds of atomic systems:
	   clusters, surfaces, bulk systems.
	   For usage, see Gitlab Wiki:
	   https://gitlab.com/gpatom/ase-gpatom/-/wikis/How-to-use-BEACON

List of related publications for gpatom/ase-gpatom:
 * BEACON:
        Global optimization of atomic structures with
        gradient-enhanced Gaussian process regression

        S. Kaappa, E. G. del Río, K. W. Jacobsen

        Physical Review B, vol. 103, 174114 (2021).
        https://doi.org/10.1103/PhysRevB.103.174114

 * ICE-BEACON:
        Atomic Structure Optimization with Machine-Learning
        Enabled Interpolation between Chemical Elements

        S. Kaappa, C. Larsen, K. W. Jacobsen

        Physical Review Letters, vol. 127, 166001 (2021).
        https://doi.org/10.1103/PhysRevLett.127.166001

 * Ghost-BEACON:
        Machine-learning-enabled optimization of atomic
        structures using atoms with fractional existence

        C. Larsen, S. Kaappa, A. L. Vishart, T. Bligaard, K. W. Jacobsen

        Physical Review B, vol. 107, 214101 (2023).
        https://doi.org/10.1103/PhysRevB.107.214101

 * BEACON with MACE prior:
        Bayesian optimization of atomic structures with prior
        probabilities from universal interatomic potentials

        P. Lyngby, C. Larsen, K. W. Jacobsen

        Physical Review Materials, vol. 8, 123802 (2024).
        https://doi.org/10.1103/PhysRevMaterials.8.123802

 * ICE, Ghost and Hyperspatial optimization generalized to arbitrary many elements and variable unit cell:
        Global atomic structure optimization through machine-
        learning-enabled barrier circumvention in extra dimensions

        C. Larsen, S. Kaappa, A. L. Vishart, T. Bligaard, K. W. Jacobsen

        npj computational materials, 11, 222 (2025).
        https://doi.org/10.1038/s41524-025-01656-9

Contact
=======

Please join our
`#gpatom <https://app.element.io/#/room/#gpatom:matrix.org>`_
channel on Matrix.


Installation cheat sheet
========================

To install latest release from pypi, use::

  $ pip install ase-gpatom

To install a developer version (allows in-place edits of the code),
clone the sourcecode and go to the toplevel gpatom directory, then run::

  $ git clone https://gitlab.com/gpatom/ase-gpatom.git
  $ pip install --editable ase-gpatom


Testing cheat sheet
===================

To run the tests, go to the test directory and run::

  $ pytest

Run the tests in parallel on ``n`` cores (requires pytest-xdist)::

  $ pytest -n 4

Show tests without running them::

  $ pytest --collectonly

Run tests in particular module::

  $ pytest test_module.py

Run tests matching pattern::

  $ pytest -k <pattern>

Show output from tests::

  $ pytest -s

Note that since many tests write files, temporary directories are
created for each test.  The temporary directories are located in
``/tmp/pytest-of-<username>/``.  pytest takes care of cleaning up
these test directories.

Use pytest.ini and test/conftest.py to customize how the tests run.

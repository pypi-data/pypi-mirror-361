import numpy as np
import time
import copy
from ase import io
from ase.parallel import parprint, parallel_function
from ase.dimer import DimerControl, MinModeAtoms, MinModeTranslate

from gpatom.gpfp.calculator import GPCalculator
from gpatom.aidmin import AIDModel
from gpatom.io import get_fmax, TrainingSet


class AIDTS:

    def __init__(self, atoms, atoms_vector, vector_length=0.7,
                 model_calculator=None, force_consistent=None,
                 trajectory='AID.traj', max_train_data=50,
                 max_train_data_strategy='nearest_observations',
                 trainingset='AID_observations.traj',
                 use_previous_observations=False):
        """
        Artificial Intelligence-Driven dimer (AID-TS) algorithm.
        Dimer optimization of an atomic structure using a surrogate machine
        learning model. Atomic positions, potential energies and forces
        information are used to build a model potential energy surface (
        PES). A dimer is launched from an initial 'atoms' structure toward
        the direction of the 'atoms_vector' structure with a magnitude of
        'vector_length'. The code automatically recognizes the atoms that
        are not involved in the displacement and their constraints. By
        default Gaussian Process Regression is used to build the model as
        implemented in [1, 2].

        [1] J. A. Garrido Torres, E. Garijo del Rio, A. H. Larsen,
        V. Streibel, J. J. Mortensen, M. Bajdich, F. Abild-Pedersen,
        K. W. Jacobsen, T. Bligaard. (submitted).
        [2] E. Garijo del Rio, J. J. Mortensen and K. W. Jacobsen.
        Phys. Rev. B 100, 104103 (2019).
        https://journals.aps.org/prb/abstract/10.1103/PhysRevB.100.104103

        Parameters
        --------------
        atoms: Atoms object
            The Atoms object to relax.

        atoms_vector: Atoms object.
            Dummy Atoms object with the structure to use for the saddle-point
            search direction. The coordinates of this structure serve to
            build the vector used for the dimer optimization. Therefore,
            the 'atoms' structure will be "pushed" uphill in the PES along the
            direction of the 'atoms_vector'.

        model_calculator: Model object.
            Model calculator to be used for predicting the potential energy
            surface. The default is None which uses a GP model with the Squared
            Exponential Kernel and other default parameters. See
            *ase.optimize.activelearning.gp.calculator* GPModel for default GP
            parameters.

        force_consistent: boolean or None
            Use force-consistent energy calls (as opposed to the energy
            extrapolated to 0 K). By default (force_consistent=None) uses
            force-consistent energies if available in the calculator, but
            falls back on force_consistent=False if not.

        trajectory: string
            Filename to store the predicted optimization.
                Additional information:
                - Uncertainty: The energy uncertainty in each image can be
                  accessed in image.info['uncertainty'].

        use_previous_observations: boolean
            If False. The optimization starts from scratch.
            A *trajectory_observations.traj* file is automatically generated
            in each step of the optimization, which contains the
            observations collected by the surrogate. If
            (a) *use_previous_observations* is True and (b) a previous
            *trajectory_observations.traj* file is found in the working
            directory: the algorithm will be use the previous observations
            to train the model with all the information collected in
            *trajectory_observations.traj*.

        """

        self.model_calculator = model_calculator
        # Default GP Calculator parameters if not specified by the user.
        if model_calculator is None:
            model = AIDModel(
                train_images=[],
                params=dict(scale=0.4, weight=1., noise=0.005),
                max_train_data_strategy=max_train_data_strategy,
                max_train_data=max_train_data,
                update_prior_strategy='maximum',
                params_to_update=None, batch_size=1,
                bounds=0.3,
            ) 
            self.model_calculator = GPCalculator(model)

        # Active Learning setup (single-point calculations).
        self.function_calls = 0
        self.force_calls = 0
        self.step = 0

        self.atoms = atoms
        self.constraints = atoms.constraints
        self.atoms_vector = atoms_vector

        # Calculate displacement vector and mask automatically.
        displacement_vector = []
        mask_atoms = []

        for atom in range(0, len(atoms)):
            vect_atom = (atoms_vector[atom].position - atoms[atom].position)
            displacement_vector += [vect_atom.tolist()]
            if np.array_equal(np.array(vect_atom), np.array([0, 0, 0])):
                mask_atoms += [0]
            else:
                mask_atoms += [1]

        max_vector = np.max(np.abs(displacement_vector))
        normalized_vector = (np.array(displacement_vector) / max_vector)
        normalized_vector *= vector_length
        self.displacement_vector = normalized_vector

        self.mask_atoms = mask_atoms
        self.vector_length = vector_length

        # Optimization settings.
        self.ase_calc = atoms.calc
        self.fc = force_consistent
        self.trajectory = trajectory
        self.use_prev_obs = use_previous_observations

        if trainingset is None:
            trajectory_main = self.trajectory.split('.')[0]
            self.train = TrainingSet(
                trajectory_main + '_observations.traj',
                use_previous_observations=False
                )
        else:
            self.train = TrainingSet(
                        trainingset,
                        use_previous_observations=use_previous_observations
                        )
        # Initialize a trajectory file for the current optimization.
        self.traj = TrainingSet(self.trajectory,
                                use_previous_observations=False
                                )

        # First observation calculation.
        self.atoms.get_potential_energy()
        self.atoms.get_forces()
        self.train.dump(atoms=self.atoms, method='dimer')
        self.traj.dump(atoms=self.atoms, method='dimer')

    def run(self, fmax=0.05, steps=200, logfile=True):

        """
        Executing run will start the optimization process.

        Parameters
        ----------
        fmax : float
            Convergence criteria (in eV/Angstrom).

        steps: int
            Maximum number of steps for the surrogate.

        logfile: bool
            Whether to print or not a full output of the optimization.

        Returns
        -------
        Optimized structure. The optimization process can be followed in
        *'trajectory'_observations.traj*.

        """
        self.fmax = fmax
        self.steps = steps

        initial_atoms_positions = copy.deepcopy(self.atoms.positions)

        # Probed atoms are used to know the path followed for low memory.
        probed_atoms = [io.read(self.trajectory, '-1')]

        while True:

            # 1. Collect observations.
            # This serves to restart from a previous (and/or parallel) runs.
            train_images = self.train.load_set()

            # Update constraints in case they have changed from previous runs.
            for img in train_images:
                img.set_constraint(self.constraints)

            # 2. Update model calculator.

            # Start from initial structure positions.
            self.atoms.positions = initial_atoms_positions

            gp_calc = copy.deepcopy(self.model_calculator)
            gp_calc.model.add_training_points(train_images=train_images,
                                              test_images=probed_atoms)
            self.atoms.calc = gp_calc

            # 3. Optimize dimer in the predicted PES.
            d_control = DimerControl(initial_eigenmode_method='displacement',
                                     displacement_method='vector',
                                     logfile=None, use_central_forces=False,
                                     extrapolate_forces=False,
                                     maximum_translation=0.1,
                                     mask=self.mask_atoms)
            d_atoms = MinModeAtoms(self.atoms, d_control)
            d_atoms.displace(displacement_vector=self.displacement_vector)
            dim_rlx = MinModeTranslate(d_atoms, trajectory=None, logfile=None)
            dim_rlx.run(fmax=fmax*0.1)

            surrogate_positions = self.atoms.positions

            # Probed atoms serve to track dimer structures for low memory.

            surrogate_atoms = copy.deepcopy(probed_atoms[0])
            surrogate_atoms.positions = surrogate_positions
            probed_atoms += [surrogate_atoms]

            # Update step (this allows to stop algorithm before evaluating).
            if self.step >= self.steps:
                break

            # 4. Evaluate the target function and save it in *observations*.
            # Update the new positions.
            self.atoms.positions = surrogate_positions
            self.atoms.calc = self.ase_calc
            self.atoms.get_potential_energy(force_consistent=self.fc)
            self.atoms.get_forces()

            self.train.dump(atoms=self.atoms, method='dimer')
            self.traj.dump(atoms=self.atoms, method='dimer')

            self.function_calls = len(train_images) + 1
            self.force_calls = self.function_calls
            self.step += 1

            # 5. Print output.
            if logfile:
                parprint("-" * 26)
                parprint('Step:', self.step)
                parprint('Function calls:', self.function_calls)
                parprint('Time:', time.strftime(
                            "%m/%d/%Y, %H:%M:%S", time.localtime()))
                parprint('Energy:', self.atoms.get_potential_energy(self.fc))
                parprint("fmax:", get_fmax(self.atoms))
                parprint("-" * 26 + "\n")

            if get_fmax(self.atoms) <= self.fmax:
                parprint('AID-TS has converged.')
                print_cite_aidts()
                break


@parallel_function
def print_cite_aidts():
    msg = "\n" + "-" * 79 + "\n"
    msg += "You are using AIDTS. Please cite: \n"
    msg += "[1] J. A. Garrido Torres, E. Garijo del Rio, V. Streibel "
    msg += "T. S. Choski, Ask H. Larsen, J. J. Mortensen, A. Urban, M. Bajdich"
    msg += " F. Abild-Pedersen, K. W. Jacobsen, and T. Bligaard. Submitted. \n"
    msg += "[2] E. Garijo del Rio, J. J. Mortensen and K. W. Jacobsen. "
    msg += "Phys. Rev. B 100, 104103."
    msg += "https://doi.org/10.1103/PhysRevB.100.104103. \n"
    msg += "-" * 79 + '\n'
    parprint(msg)

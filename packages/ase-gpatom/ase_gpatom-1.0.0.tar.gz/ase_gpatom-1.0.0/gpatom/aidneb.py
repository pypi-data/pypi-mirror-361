import numpy as np
import copy
import time

from scipy.spatial.distance import sqeuclidean
from ase import io
from ase.atoms import Atoms
from ase.neb import NEB
from ase.parallel import parprint, parallel_function
from ase.optimize import MDMin, FIRE

from gpatom.gpfp.calculator import GPCalculator
from gpatom.aidmin import AIDModel
from gpatom.acquisition import acquisition
from gpatom.io import get_fmax, TrainingSet

class AIDNEB:

    def __init__(self, start, end, model_calculator=None, calculator=None,
                 interpolation='idpp', n_images=15, k=None, mic=False,
                 neb_method='improvedtangent',
                 remove_rotation_and_translation=False,
                 max_train_data=25, force_consistent=None,
                 max_train_data_strategy='nearest_observations',
                 trajectory='AIDNEB.traj',
                 trainingset='AID_observations.traj',
                 trajectory_surrogate='AID_surrogate.traj',
                 use_previous_observations=False):

        """
        Artificial Intelligence-Driven Nudged Elastic Band (AID-NEB) algorithm.
        Optimize a NEB using a surrogate machine learning model [1-3].
        Potential energies and forces at a given position are
        supplied to the model calculator to build a modelled PES in an
        active-learning fashion. This surrogate relies on NEB theory to
        optimize the images along the path in the predicted PES. Once the
        predicted NEB is optimized the acquisition function collect a new
        observation based on the predicted energies and uncertainties of the
        optimized images. By default Gaussian Process Regression is used to
        build the model as implemented in [4].

        [1] J. A. Garrido Torres, E. Garijo del Rio, V. Streibel,
        T. S. Choski, J. J. Mortensen, A. Urban, M. Bajdich,
        F. Abild-Pedersen, K. W. Jacobsen, and T. Bligaard (submitted).
        [2] J. A. Garrido Torres, M. H. Hansen, P. C. Jennings, J. R. Boes
        and T. Bligaard. Phys. Rev. Lett. 122, 156001.
        https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.122.156001
        [3] O. Koistinen, F. B. Dagbjartsdottir, V. Asgeirsson, A. Vehtari
        and H. Jonsson. J. Chem. Phys. 147, 152720.
        https://doi.org/10.1063/1.4986787



        NEB Parameters
        --------------
        initial: Trajectory file (in ASE format) or Atoms object.
            Initial end-point of the NEB path.

        final: Trajectory file (in ASE format) or Atoms object.
            Final end-point of the NEB path.

        model_calculator: Model object.
            Model calculator to be used for predicting the potential energy
            surface. The default is None which uses a GP model with the Squared
            Exponential Kernel and other default parameters. See
            *ase.optimize.activelearning.gp.calculator* GPModel for default GP
            parameters.

        interpolation: string or Atoms list or Trajectory
            NEB interpolation.

            options:
                - 'linear' linear interpolation.
                - 'idpp'  image dependent pair potential interpolation.
                - Trajectory file (in ASE format) or list of Atoms.
                The user can also supply a manual interpolation by passing
                the name of the trajectory file  or a list of Atoms (ASE
                format) containing the interpolation images.

        mic: boolean
            Use mic=True to use the Minimum Image Convention and calculate the
            interpolation considering periodic boundary conditions.

        n_images: int or float
            Number of images of the path. Only applicable if 'linear' or
            'idpp' interpolation has been chosen.
            options:
                - int: Number of images describing the NEB. The number of
                images include the two (initial and final) end-points of the
                NEB path.
                - float: Spacing of the images along the NEB. The number of
                images is calculated as the length of the interpolated
                initial path divided by the spacing (Ang^-1).

        k: float or list
            Spring constant(s) in eV/Angstrom.

        neb_method: string
            NEB method as implemented in ASE. ('aseneb', 'improvedtangent'
            or 'eb'). See https://wiki.fysik.dtu.dk/ase/ase/neb.html.

        calculator: ASE calculator Object.
            ASE calculator.
            See https://wiki.fysik.dtu.dk/ase/ase/calculators/calculators.html

        force_consistent: boolean or None
            Use force-consistent energy calls (as opposed to the energy
            extrapolated to 0 K). By default (force_consistent=None) uses
            force-consistent energies if available in the calculator, but
            falls back on force_consistent=False if not.

        trajectory: string
            Filename to store the predicted NEB paths.
                Additional information:
                - Energy uncertain: The energy uncertainty in each image
                position can be accessed in image.info['uncertainty'].

        use_previous_observations: boolean
            If False. The optimization starts from scratch.
                If the observations were saved to a trajectory file,
                it is overwritten. If they were kept in a list, they are
                deleted.
            If True. The optimization uses the information that was already
                in the training set that is provided in the optimization.

        trainingset: None, trajectory file or list
            Where the training set is kept, either saved to disk in a trajectory
            file or kept in memory in a list.
            options:
                None (default):
                    A trajectory file named *trajectory*_observations.traj is
                    automatically generated and the training set is saved to
                    it while generated.
                str: trajectory filename where to append the training set
                list: list were to append the atoms objects.

        max_train_data: int
            Number of observations that will effectively be included in the
            model. See also *max_data_strategy*.

        max_train_data_strategy: string
            Strategy to decide the observations that will be included in the
            model.

            options:
                'last_observations': selects the last observations collected by
                the surrogate.
                'lowest_energy': selects the lowest energy observations
                collected by the surrogate.
                'nearest_observations': selects the observations which
                positions are nearest to the positions of the Atoms to test.

            For instance, if *max_train_data* is set to 50 and
            *max_train_data_strategy* to 'lowest energy', the surrogate model
            will be built in each iteration with the 50 lowest energy
            observations collected so far.

        """

        # Convert Atoms and list of Atoms to trajectory files.
        if isinstance(start, Atoms):
            io.write('initial.traj', start)
            start = 'initial.traj'
        if isinstance(end, Atoms):
            io.write('final.traj', end)
            end = 'final.traj'
        interp_path = None
        if interpolation != 'idpp' and interpolation != 'linear':
            interp_path = interpolation
        if isinstance(interp_path, list):
            io.write('initial_path.traj', interp_path)
            interp_path = 'initial_path.traj'

        # NEB parameters.
        self.start = start
        self.end = end
        self.n_images = n_images
        self.mic = mic
        self.rrt = remove_rotation_and_translation
        self.neb_method = neb_method
        self.spring = k
        self.i_endpoint = io.read(self.start, '-1')
        self.e_endpoint = io.read(self.end, '-1')

        # GP calculator:
        self.model_calculator = model_calculator
        if model_calculator is None:
            model = AIDModel(
                train_images=[],
                prior=None,
                fit_weight='update',
                update_prior_strategy='fit',
                params=dict(weight=1.0, scale=0.4, noise=0.005),
                params_to_update=None, batch_size=5,
                bounds=None, kerneltype='sqexp',
                max_train_data_strategy=max_train_data_strategy,
                max_train_data=max_train_data
            )
            self.model_calculator = GPCalculator(model)

        # Active Learning setup (Single-point calculations).
        self.step = 0
        self.function_calls = 0
        self.force_calls = 0
        self.ase_calc = calculator
        self.atoms = io.read(self.start, '-1')

        self.constraints = self.atoms.constraints
        self.force_consistent = force_consistent
        self.use_previous_observations = use_previous_observations
        self.trajectory = trajectory
        self.trajectory_surrogate = trajectory_surrogate

        # Make sure that the initial and endpoints are near the interpolation.
        if self.mic:
            mic_initial = self.i_endpoint[:]
            mic_final = self.e_endpoint[:]
            mic_images = [mic_initial]
            for i in range(10000):
                mic_images += [mic_initial.copy()]
            mic_images += [mic_final]
            neb_mic = NEB(mic_images, climb=False, method=self.neb_method,
                          remove_rotation_and_translation=self.rrt)
            neb_mic.interpolate(method='linear', mic=self.mic)
            self.i_endpoint.positions = mic_images[1].positions[:]
            self.e_endpoint.positions = mic_images[-2].positions[:]

        # Calculate the initial and final end-points (if necessary).
        self.i_endpoint.calc = (copy.copy(self.ase_calc))
        self.e_endpoint.calc = (copy.copy(self.ase_calc))
        self.i_endpoint.get_potential_energy(force_consistent=force_consistent)
        self.i_endpoint.get_forces()
        self.e_endpoint.get_potential_energy(force_consistent=force_consistent)
        self.e_endpoint.get_forces()

        # Initialize training set
        if trainingset is None:
            trajectory_main = self.trajectory.split('.')[0]
            self.train = TrainingSet(trajectory_main + '_observations.traj',
                    use_previous_observations=False)
        else:
            self.train = TrainingSet(trainingset,
                        use_previous_observations=use_previous_observations)

        self.train.dump(atoms=self.i_endpoint, method='neb')
        self.train.dump(atoms=self.e_endpoint, method='neb')

        # Calculate the distance between the initial and final endpoints.
        d_start_end = sqeuclidean(self.i_endpoint.positions.flatten(),
                                  self.e_endpoint.positions.flatten())**0.5

        # A) Create images using interpolation if user does define a path.
        if interp_path is None:
            if isinstance(self.n_images, float):
                self.n_images = int(d_start_end/self.n_images)
            if self. n_images <= 3:
                self.n_images = 3
            self.images = make_neb(self)
            self.spring = 2. * np.sqrt(self.n_images-1) / d_start_end

            neb_interpolation = NEB(self.images, climb=False, k=self.spring,
                                    method=self.neb_method,
                                    remove_rotation_and_translation=self.rrt)
            neb_interpolation.interpolate(method='linear', mic=self.mic)
            if interpolation == 'idpp':
                neb_interpolation = NEB(
                                    self.images, climb=True,
                                    k=self.spring, method=self.neb_method,
                                    remove_rotation_and_translation=self.rrt
                                    )
                neb_interpolation.idpp_interpolate(optimizer=FIRE,
                                                   mic=self.mic)

        # B) Alternatively, the user can propose an initial path.
        if interp_path is not None:
            images_path = io.read(interp_path, ':')
            first_image = images_path[0].get_positions().reshape(-1)
            last_image = images_path[-1].get_positions().reshape(-1)
            is_pos = self.i_endpoint.get_positions().reshape(-1)
            fs_pos = self.e_endpoint.get_positions().reshape(-1)
            if not np.array_equal(first_image, is_pos):
                images_path.insert(0, self.i_endpoint)
            if not np.array_equal(last_image, fs_pos):
                images_path.append(self.e_endpoint)
            self.n_images = len(images_path)
            self.images = make_neb(self, images_interpolation=images_path)

        # Guess spring constant (k) if not defined by the user.
        if self.spring is None:
            self.spring = 2. * (np.sqrt(self.n_images-1) / d_start_end)
        # Save initial interpolation.
        self.initial_interpolation = self.images[:]

    def run(self, fmax=0.05, unc_convergence=0.025, dt=0.05, ml_steps=100,
            max_step=2.0):

        """
        Executing run will start the NEB optimization process.

        Parameters
        ----------
        fmax : float
            Convergence criteria (in eV/Angstrom).

        unc_convergence: float
            Maximum uncertainty for convergence (in eV). The algorithm's
            convergence criteria will not be satisfied if the uncertainty
            on any of the NEB images in the predicted path is above this
            threshold.

        dt : float
            dt parameter for MDMin.

        ml_steps: int
            Maximum number of steps for the NEB optimization on the
            modelled potential energy surface.

        max_step: float
            Safe control parameter. This parameter controls the degree of
            freedom of the NEB optimization in the modelled potential energy
            surface or the. If the uncertainty of the NEB lies above the
            'max_step' threshold the NEB won't be optimized and the image
            with maximum uncertainty is evaluated. This prevents exploring
            very uncertain regions which can lead to probe unrealistic
            structures.

        Returns
        -------
        Minimum Energy Path from the initial to the final states.

        """
        train_images = self.train.load_set()
        if len(train_images) == 2:
            middle = int(self.n_images * (2./3.))
            e_is = self.i_endpoint.get_potential_energy()
            e_fs = self.e_endpoint.get_potential_energy()
            if e_is >= e_fs:
                middle = int(self.n_images * (1./3.))
            self.atoms.positions = self.images[middle].get_positions()
            self.atoms.calc = self.ase_calc
            self.atoms.get_potential_energy(force_consistent=self.force_consistent)
            self.atoms.get_forces()
            self.train.dump(atoms=self.atoms, method='neb')
            self.function_calls += 1
            self.force_calls += 1
            self.step += 1

        while True:

            # 0. Start from initial interpolation every 50 steps.
            if self.step % 50 == 0:
                parprint('Starting from initial interpolation...')
                self.images = copy.deepcopy(self.initial_interpolation)

            # 1. Collect observations.
            # This serves to use_previous_observations from a previous
            # (and/or parallel) runs.
            train_images = self.train.load_set()

            # 2. Prepare a calculator.
            calc = copy.deepcopy(self.model_calculator)

            # Detach calculator from the prev. optimized images (speed up).
            for i in self.images:
                i.calc = None
            # Train only one process.
            calc.model.add_training_points(train_images, test_images=self.images)
            # Attach the calculator (already trained) to each image.
            for i in self.images:
                i.calc = copy.copy(calc)

            # 3. Optimize the NEB in the predicted PES.
            # Get path uncertainty for deciding whether NEB or CI-NEB.
            predictions = get_neb_predictions(self.images)
            neb_pred_uncertainty = predictions['uncertainty']

            # Climbing image NEB mode is risky when the model is trained
            # with a few data points. Switch on climbing image (CI-NEB) only
            # when the uncertainty of the NEB is low.
            climbing_neb = False
            if np.max(neb_pred_uncertainty) <= unc_convergence:
                parprint('Climbing image is now activated.')
                climbing_neb = True
            ml_neb = NEB(self.images, climb=climbing_neb,
                         method=self.neb_method, k=self.spring)
            neb_opt = MDMin(ml_neb, dt=dt, trajectory=self.trajectory)

            # Safe check to optimize the images.
            if np.max(neb_pred_uncertainty) <= max_step:
                neb_opt.run(fmax=(fmax * 0.80), steps=ml_steps)

            predictions = get_neb_predictions(self.images)
            neb_pred_energy = predictions['energy']
            neb_pred_uncertainty = predictions['uncertainty']

            # 5. Print output.
            max_e = np.max(neb_pred_energy)
            pbf = max_e - self.i_endpoint.get_potential_energy(
                                        force_consistent=self.force_consistent)
            pbb = max_e - self.e_endpoint.get_potential_energy(
                                        force_consistent=self.force_consistent)
            msg = "--------------------------------------------------------"
            parprint(msg)
            parprint('Step:', self.step)
            parprint('Time:', time.strftime("%m/%d/%Y, %H:%M:%S",
                                            time.localtime()))
            parprint('Predicted barrier (-->):', pbf)
            parprint('Predicted barrier (<--):', pbb)
            parprint('Max. uncertainty:', np.max(neb_pred_uncertainty))
            parprint('Number of images:', len(self.images))
            parprint("fmax:", get_fmax(train_images[-1]))
            msg = "--------------------------------------------------------\n"
            parprint(msg)

            # 6. Check convergence.
            # Max.forces and NEB images uncertainty must be below *fmax* and
            # *unc_convergence* thresholds.
            if len(train_images) > 2 and get_fmax(train_images[-1]) <= fmax:
                parprint('A saddle point was found.')
                if np.max(neb_pred_uncertainty[1:-1]) < unc_convergence:
                    io.write(self.trajectory, self.images)
                    parprint('Uncertainty of the images above threshold.')
                    parprint('NEB converged.')
                    parprint('The NEB path can be found in:', self.trajectory)
                    msg = "Visualize the last path using 'ase gui "
                    msg += self.trajectory
                    parprint(msg)
                    break

            # 7. Select next point to train (acquisition function):

            # Candidates are the optimized NEB images in the predicted PES.
            candidates = self.images[1:-1][:]

            if np.max(neb_pred_uncertainty) > unc_convergence:
                sorted_candidates = acquisition(train_images=train_images,
                                                candidates=candidates,
                                                mode='uncertainty',
                                                objective='max')
            else:
                if self.step % 5 == 0:
                    sorted_candidates = acquisition(train_images=train_images,
                                                    candidates=candidates,
                                                    mode='fmax',
                                                    objective='min')
                else:
                    sorted_candidates = acquisition(train_images=train_images,
                                                    candidates=candidates,
                                                    mode='ucb',
                                                    objective='max')

            # Select the best candidate.
            best_candidate = sorted_candidates.pop(0)

            # Save the other candidates for multi-task optimization.
            io.write(self.trajectory_surrogate, sorted_candidates)

            # 8. Evaluate the target function and save it in *observations*.
            self.atoms.positions = best_candidate.get_positions()
            self.atoms.calc = self.ase_calc
            self.atoms.get_potential_energy(
                                    force_consistent=self.force_consistent
                                    )
            self.atoms.get_forces()
            self.train.dump(atoms=self.atoms, method='neb')
            self.function_calls += 1
            self.force_calls += 1
            self.step += 1
        print_cite_aidneb()


@parallel_function
def make_neb(self, images_interpolation=None):
    """
    Creates a NEB from a set of images.
    """
    imgs = [self.i_endpoint[:]]
    for i in range(1, self.n_images-1):
        image = self.i_endpoint[:]
        if images_interpolation is not None:
            image.set_positions(images_interpolation[i].get_positions())
        image.set_constraint(self.constraints)
        imgs.append(image)
    imgs.append(self.e_endpoint[:])
    return imgs


@parallel_function
def get_neb_predictions(images):
    neb_pred_energy = []
    neb_pred_unc = []
    for i in images:
        neb_pred_energy.append(i.get_potential_energy())
        unc = 2. * i.calc.results['uncertainty']
        neb_pred_unc.append(unc)
    neb_pred_unc[0] = 0.0
    neb_pred_unc[-1] = 0.0
    predictions = {'energy': neb_pred_energy, 'uncertainty': neb_pred_unc}
    return predictions


@parallel_function
def print_cite_aidneb():
    msg = "\n" + "-" * 79 + "\n"
    msg += "You are using AIDNEB. Please cite: \n"
    msg += "[1] J. A. Garrido Torres, M. H. Hansen, P. C. Jennings, "
    msg += "J. R. Boes and T. Bligaard. Phys. Rev. Lett. 122, 156001. "
    msg += "https://doi.org/10.1103/PhysRevLett.122.156001 \n"
    msg += "[2] O. Koistinen, F. B. Dagbjartsdottir, V. Asgeirsson, A. Vehtari"
    msg += " and H. Jonsson. J. Chem. Phys. 147, 152720. "
    msg += "https://doi.org/10.1063/1.4986787 \n"
    msg += "[3] E. Garijo del Rio, J. J. Mortensen and K. W. Jacobsen. "
    msg += "Phys. Rev. B 100, 104103."
    msg += "https://doi.org/10.1103/PhysRevB.100.104103. \n"
    msg += "-" * 79 + '\n'
    parprint(msg)

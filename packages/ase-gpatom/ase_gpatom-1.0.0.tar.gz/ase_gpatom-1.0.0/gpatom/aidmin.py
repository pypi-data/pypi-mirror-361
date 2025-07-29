import time
import copy
import numpy as np

from scipy.spatial.distance import euclidean
from ase.parallel import parprint, parallel_function
from ase.optimize import QuasiNewton, BFGS

from gpatom.gpfp.calculator import GPCalculator, copy_image
#from gpatom.gpfp.atoms_gp_interface import Model
from gpatom.gpfp.database import Database

from gpatom.gpfp.gp import GaussianProcess
from gpatom.gpfp.fingerprint import CartesianCoordFP
#from gpatom.gpfp.kerneltypes import EuclideanDistance
from gpatom.gpfp.hpfitter import HyperparameterFitter, GPPrefactorFitter
from gpatom.io import get_fmax, TrainingSet


class AIDMin:

    def __init__(self, atoms, model_calculator=None, force_consistent=None,
                 max_train_data=5, optimizer=QuasiNewton,
                 max_train_data_strategy='nearest_observations',
                 geometry_threshold=0.001, trajectory='AID.traj',
                 use_previous_observations=False,
                 trainingset='AID_observations.traj'):
        """
        Artificial Intelligence-Driven energy Minimizer (AID-Min) algorithm.
        Optimize atomic structure using a surrogate machine learning
        model [1,2]. Atomic positions, potential energies and forces
        information are used to build a modelled potential energy surface (
        PES) that can be optimized to obtain new suggested structures
        towards finding a local minima in the targeted PES.

        [1] E. Garijo del Rio, J. J. Mortensen and K. W. Jacobsen.
        Phys. Rev. B 100, 104103 (2019).
        https://journals.aps.org/prb/abstract/10.1103/PhysRevB.100.104103
        [2] J. A. Garrido Torres, E. Garijo del Rio, A. H. Larsen,
        V. Streibel, J. J. Mortensen, M. Bajdich, F. Abild-Pedersen,
        K. W. Jacobsen, T. Bligaard. (submitted).

        Parameters
        --------------
        atoms: Atoms object
            The Atoms object to relax.

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
                If the observations were saved to a trajectory file,
                it is overwritten. If they were kept in a list, they are
                deleted.
            If True. The optimization uses the information that was already
                in the training set that is provided in the optimization.

        trainingset: None, trajectory file or list
            Where the training set is kept, either saved to disk in a
            trajectory file or kept in memory in a list.
            options:
                None (default):
                    A trajectory file named *trajectory*_observations.traj is
                    automatically generated and the training set is saved to
                    it while generated.
                str: trajectory filename where to append the training set
                list: list were to append the atoms objects.
        """

        # Model calculator:
        self.model = model_calculator
        # Default GP Calculator parameters if not specified by the user.
        if model_calculator is None:
            self.model = AIDModel(
                train_images=[],
                params=dict(scale=0.3, weight=2., noise=0.003),
                update_prior_strategy='fit',
                max_train_data_strategy=max_train_data_strategy,
                max_train_data=max_train_data)

        # Active Learning setup (single-point calculations).
        self.function_calls = 0
        self.force_calls = 0
        self.step = 0

        self.atoms = atoms
        self.constraints = atoms.constraints
        self.ase_calc = atoms.calc
        self.optimizer = optimizer

        self.fc = force_consistent
        self.trajectory = trajectory
        self.geometry_threshold = geometry_threshold

        # Initialize training set

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


        self.atoms.get_potential_energy()
        self.atoms.get_forces()

        self.train.dump(atoms=self.atoms, method='min')
        self.traj.dump(atoms=self.atoms, method='min')

    def run(self, fmax=0.05, ml_steps=500, steps=200):

        """
        Executing run will start the optimization process.

        Parameters
        ----------
        fmax : float
            Convergence criteria (in eV/Angstrom).

        ml_steps: int
            Maximum number of steps for the optimization on the modelled
            potential energy surface.

        steps: int
            Maximum number of steps for the surrogate.

        Returns
        -------
        Optimized structure. The optimization process can be followed in
        *trajectory_observations.traj*.

        """
        self.fmax = fmax
        self.steps = steps

        # Always start from 'atoms' positions.
        starting_atoms = self.train.load_last()
        starting_atoms.positions = self.atoms.positions.copy()

        while not self.fmax >= get_fmax(self.atoms):

            # 1. Gather observations in every iteration.
            # This serves to use the previous observations (useful for
            # continuing calculations and/or for parallel runs).
            train_images = self.train.load_set()

            # Update constraints in case they have changed from previous runs.
            for img in train_images:
                img.set_constraint(self.constraints)

            # 2. Update model calculator.
            ml_converged = False
            surrogate_positions = self.atoms.positions

            # Probed positions are used for low-memory.
            probed_atoms = [copy_image(starting_atoms)]
            probed_atoms[0].positions = self.atoms.positions.copy()

            while not ml_converged:
                model = copy.deepcopy(self.model)
                model.add_training_points(train_images=train_images,
                                          test_images=probed_atoms)
                gp_calc = GPCalculator(model, calculate_uncertainty=False)
                self.atoms.calc = gp_calc

                # 3. Optimize the structure in the predicted PES.
                ml_opt = self.optimizer(self.atoms,
                                        logfile=None,
                                        trajectory=None)
                ml_opt.run(fmax=(fmax * 0.01), steps=ml_steps)
                surrogate_positions = self.atoms.positions

                if len(probed_atoms) >= 2:
                    l1_probed_pos = probed_atoms[-1].positions.reshape(-1)
                    l2_probed_pos = probed_atoms[-2].positions.reshape(-1)
                    dl1l2 = euclidean(l1_probed_pos, l2_probed_pos)
                    if dl1l2 <= self.geometry_threshold:
                        ml_converged = True

                probed = copy.deepcopy(probed_atoms[0])
                probed.positions = copy.deepcopy(self.atoms.positions)
                probed_atoms += [probed]

            # Update step (this allows to stop algorithm before evaluating).
            if self.step >= self.steps:
                break

            # 4. Evaluate the target function and save it in *observations*.
            self.atoms.positions = surrogate_positions
            self.atoms.calc = self.ase_calc
            self.atoms.get_potential_energy(force_consistent=self.fc)
            self.atoms.get_forces()

            self.train.dump(atoms=self.atoms, method='min')
            self.traj.dump(atoms=self.atoms, method='min')

            self.function_calls = len(train_images) + 1
            self.force_calls = self.function_calls
            self.step += 1

            # 5. Print simple output.
            parprint("-" * 26)
            parprint('Step:', self.step)
            parprint('Function calls:', self.function_calls)
            parprint('Time:', time.strftime("%m/%d/%Y, %H:%M:%S",
                                            time.localtime()))
            parprint('Energy:', self.atoms.get_potential_energy(self.fc))
            parprint("fmax:", get_fmax(self.atoms))
            parprint("-" * 26 + "\n")
        print_cite_aidmin()


@parallel_function
def print_cite_aidmin():
    msg = "\n" + "-" * 79 + "\n"
    msg += "You are using AIDMin. Please cite: \n"
    msg += "[1] E. Garijo del Rio, J. J. Mortensen and K. W. Jacobsen. "
    msg += "Phys. Rev. B 100, 104103."
    msg += "https://doi.org/10.1103/PhysRevB.100.104103. \n"
    msg += "[2] J. A. Garrido Torres, E. Garijo del Rio, V. Streibel "
    msg += "T. S. Choski, Ask H. Larsen, J. J. Mortensen, A. Urban, M. Bajdich"
    msg += " F. Abild-Pedersen, K. W. Jacobsen, and T. Bligaard. Submitted. \n"
    msg += "-" * 79 + '\n'
    parprint(msg)


class AIDModel:

    """
    GP model parameters
    -------------------
    train_images: list
        List of Atoms objects containing the observations which will be use
        to train the model.

    prior: Prior object or None
        Prior for the GP regression of the PES surface. See
        ase.optimize.activelearning.prior. If *Prior* is None, then it is set
        as the ConstantPrior with the constant being updated using the
        update_prior_strategy specified as a parameter.

    weight: float
        Pre-exponential factor of the Squared Exponential kernel. If
        *update_hyperparams* is False, changing this parameter has no effect
        on the dynamics of the algorithm.

    scale: float
        Scale of the Squared Exponential Kernel.

    noise: float
        Regularization parameter for the Gaussian Process Regression.

    update_prior_strategy: None, string
        Strategy to update the constant from the ConstantPrior when more
        data is collected.

        options:
            None: Do not update the constant
            'maximum': update the prior to the maximum sampled energy.
            'minimum' : update the prior to the minimum sampled energy.
            'average': use the average of sampled energies as prior.
            'init' : fix the prior to the initial energy.
            'last' : fix the prior to the last sampled energy.
            'fit'  : update the prior s.t. it maximizes the marginal likelihood

    params_to_update: dictionary {param_name : bounds}
        Hyperparameters of the kernel to be updated. If the dictionary
        is empty, hyperparameters are kept fixed. The new hyperparameters
        are found maximizing the marginal likelihood of the model.
        If the optimization fails, the values of the hyperparameters are
        kept as they were.
        Each hyperaparameter to be updated requires to have a bound specified.
        There are three options for the bounds of each hyperparameter:
            * None: The optimization on that hyperparameters is unconstrained.
            * tuple (min, max): interval for updating the hyperparameters
            * float between 0 and 1: Letting the hyperparameter vary a
                percentage. Let t be a hyperparameter. Then it is optimized
                under the constraint (1-bound)*t_0 <= t <= (1+bound)*t_0 where
                t_0 is the value of the hyperparameter in the previous step.

    batch_size: int
        Number of new points in the sample before updating the hyperparameters.
        Only relevant if the optimizer is executed in update
        mode: (update = True)

    max_train_data: int
        Number of observations that will effectively be included in the GP
        model. See also *max_data_strategy*.

    max_train_data_strategy: string
        Strategy to decide the observations that will be included in the model.

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

    print_format: string
        Printing format. It chooses how much information and in which format
        is shown to the user.

        options:
              'ASE' (default): information printed matches other ASE functions
                  outside from the AID module. ML is transparent to the user.
              'AID': Original format of the AID module. More informative in
              respect of ML process. This option is advised for experienced
              users.

    pd: PriorDistribution object
        Prior distribution function for fitting the length scale.
    """

    def __init__(self, train_images=[], train_features=None,
                 prior=None, kerneltype='sqexp', fingerprint=None,
                 params={'weight': 1., 'scale': 0.4,
                         'noise': 0.005, 'noisefactor': 0.5},
                 use_forces=True,
                 update_prior_strategy=None, fit_weight=True,
                 params_to_update=None,
                 batch_size=5, bounds=None,
                 max_train_data=None,
                 max_train_data_strategy='nearest_observations',
                 wrap_positions=False,
                 print_format='ASE', mask_constraints=False):

        # Fingerprint
        if fingerprint is None:
            fingerprint = CartesianCoordFP
        self.fp = fingerprint

        self.hpfitter = HyperparameterFitter()

        # Initialize training set
        train_images = [copy_image(i) for i in train_images]
        fingerprints = [self.new_fingerprint(atoms)   #, params, use_forces)
                        for atoms in train_images]

        # Training data:
        energies = [atoms.get_potential_energy(apply_constraint=False)
                    for atoms in train_images]
        forces = [atoms.get_forces(apply_constraint=False)
                  for atoms in train_images]

        self.data = Database(fingerprints, energies, forces)
        self.prev_data = Database()  # Do not retrain model if same data.
        
        self.gp = GaussianProcess(hp=params, prior=prior,
                                  kerneltype=kerneltype,
                                  use_forces=use_forces)

        # Initialize hyperparameter update attributes
        if params_to_update is None:
            params_to_update = {}
        self.params_to_update = params_to_update
        self.fit_weight = fit_weight
        self.nbatch = batch_size

        # Initialize prior and trainset attributes
        self.strategy = update_prior_strategy
        self.max_data = max_train_data
        self.max_data_strategy = max_train_data_strategy

        # Initialize other attributes
        self.wrap = wrap_positions
        self.print_format = print_format
        self.mask_constraints = mask_constraints

        if len(self.data) > 0:
            self.gp = self.train_model(self.gp, self.data)

        self.need_retrain = True



    def add_training_points(self, train_images, test_images=None):
        """ Update the model with observations (feeding new training images),
        after instantiating the GPCalculator class."""

        # this is used in selecting nearest training points:
        self.test_images = test_images

        for im in train_images:
            image = copy_image(im)
            fp = self.new_fingerprint(image)
            self.data.add(fp, image.get_potential_energy(apply_constraint=False),
                          image.get_forces(apply_constraint=False))

            self.need_retrain = True




    def train_model(self, gp, data):
        """ Train a model with the previously fed observations."""

        if self.mask_constraints:
            self.atoms_mask = self.create_mask()
        else:
            # Masks not implemented
            pass

            # Make null mask
            # mask = np.ones_like(self.atoms.get_positions(), dtype=bool)
            # self.atoms_mask = np.argwhere(mask.reshape(-1)).reshape(-1)

        self.set_gp_prior_constant()
        
        subdata = self.reduced_training_set()

        if self.gp.use_forces:
            targets = subdata.get_all_energyforces(negative_forces=True)
        else:
            targets = subdata.energylist
        features = subdata.get_all_fingerprints()

        if self.print_format == 'AID':
            print('Training data size: ', len(subdata))

        gp.train(features, targets)

        # Fit hyperparameters:
        update_hp = len(self.params_to_update) != 0
        is_train_empty = len(subdata) == 0
        is_module_batch = len(subdata) % self.nbatch == 0
        if update_hp and is_module_batch and not is_train_empty:

            self.hpfitter.fit(self, self.params_to_update,
                              fit_weight=True)

        elif self.fit_weight and not is_train_empty:
            gp=GPPrefactorFitter.fit(gp)

        self.data = subdata

        return gp




    def set_gp_prior_constant(self):
        if self.strategy is not None:

            energies = self.data.energylist
            
            if self.strategy == 'average':
                av_e = np.mean(energies)
                self.gp.prior.set_constant(av_e)
                
            elif self.strategy == 'maximum':
                max_e = np.max(energies)
                self.gp.prior.set_constant(max_e)
                
            elif self.strategy == 'minimum':
                min_e = np.min(energies)
                self.gp.prior.set_constant(min_e)
                
            elif self.strategy == 'init':
                self.gp.prior.set_constant(energies[0])
                self.gp.update_prior = False
                
            elif self.strategy == 'last':
                self.gp.prior.set_constant(energies[-1])
                self.gp.update_prior = False
                
            elif self.strategy == 'fit':
                self.gp.prior.let_update()

            else:
                raise NotImplementedError('Prior update strategy \'{:s}\' not '
                'implemented.'.format(self.strategy))
        return

    def reduced_training_set(self):

        train_x = self.data.get_all_fingerprints().copy()
        train_y = self.data.get_all_energyforces(negative_forces=False)
        train_y = np.array(train_y).reshape(len(self.data), -1)

        if self.max_data is not None:
            # Check if the max_train_data_strategy is implemented.
            implemented_strategies = ['last_observations', 'lowest_energy',
                                      'nearest_observations']
            if self.max_data_strategy not in implemented_strategies:
                msg = 'The selected max_train_data_strategy is not'
                msg += 'implemented. '
                msg += 'Implemented are: ' + str(implemented_strategies)
                raise NotImplementedError(msg)

            # Get only the last observations.
            if self.max_data_strategy == 'last_observations':
                train_x = train_x[-self.max_data:]
                train_y = train_y[-self.max_data:]

            # Get the minimum energy observations.
            if self.max_data_strategy == 'lowest_energy':
                e_list = []
                for target in train_y:
                    e_list.append(target[0])
                arg_low_e = np.argsort(e_list)[:self.max_data]
                x = [train_x[i] for i in arg_low_e]
                y = [train_y[i] for i in arg_low_e]
                train_x = x
                train_y = y

            # Get the nearest observations to the test structure.
            # XXX Might need debugging
            if self.max_data_strategy == 'nearest_observations':

                if ((not hasattr(self, 'test_images')) or
                    (self.test_images is None)):
                    test_fps = train_x

                else:
                    test_fps = [self.new_fingerprint(atoms=image)
                                for image in self.test_images]

                index_nearest = []
                for test_fp in test_fps:
                    distances = []
                    for train_fp in train_x:
                        #D=EuclideanDistance.distance(test_fp, train_fp)
                        D = np.linalg.norm(test_fp.vector - train_fp.vector)      
                        distances.append(D)

                    index_nearest += list(np.argsort(distances)[:self.max_data])

                # Remove duplicates.
                index_nearest = np.unique(index_nearest)
                train_x = [train_x[i] for i in index_nearest]
                train_y = [train_y[i] for i in index_nearest]

        train_y = np.array(train_y)
        subdata = Database(fingerprints=train_x,
                           energies=train_y[:, 0],
                           forces=train_y[:, 1:].reshape(len(train_x), -1, 3))

        return subdata
    
    

    def new_fingerprint(self, atoms):
        return self.fp(atoms)
    
    
    def calculate(self, atoms, get_variance=True):
        '''
        Calculate energy, forces and uncertainty for the given
        fingerprint. If get_variance==False, variance is returned
        as None.
        '''
        if self.need_retrain:
            self.train_model(self.gp, self.data)
        self.need_retrain = False
        
        fp=self.new_fingerprint(atoms)
        
        return self.gp.predict(fp, get_variance=get_variance)
    


    
#    def calculate(self, atoms, get_variance=True):

#        print('FOR HELVEDE')#
#        assert(1==2)
#        fp=self.new_fingerprint(atoms)
#        print('print for satan')
        
#        return self.gp.predict(fp, get_variance=get_variance)

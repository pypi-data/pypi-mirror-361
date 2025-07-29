import warnings
import pickle

import numpy as np
from ase.optimize.optimize import Optimizer
from ase.parallel import world
from scipy.optimize import minimize
from scipy.linalg import cho_solve

from gpatom.gpfp.gp import GaussianProcess
from gpatom.gpfp.kernel import CCKernel
from gpatom.gpfp.prior import ConstantPrior
from gpatom.gpfp.fingerprint import CartesianCoordFP


class GPMin(Optimizer):
    def __init__(
            self, atoms, restart=None, logfile='-', trajectory=None, prior=None,
            kernel=None, master=None, noise=None, weight=None, scale=None,
            force_consistent=None, batch_size=None, bounds=None,
            update_prior_strategy='maximum', update_hyperparams=False
    ):
        """Optimize atomic positions using GPMin algorithm, which uses
        both potential energies and forces information to build a PES
        via Gaussian Process (GP) regression and then minimizes it.

        Default behaviour:
        --------------------
        The default values of the following
        parameters: scale, noise, weight, batch_size and bounds depend
        on the value of update_hyperparams. In order to get the default
        value of any of them, they should be set up to None.
        Default values are:

        update_hyperparams = True
            scale : 0.3
            noise : 0.004
            weight: 2.
            bounds: 0.1
            batch_size: 1

        update_hyperparams = False
            scale : 0.4
            noise : 0.005
            weight: 1.
            bounds: irrelevant
            batch_size: irrelevant

        Parameters:
        ------------------

        atoms: Atoms object
            The Atoms object to relax.

        restart: string
            Pickle file used to store the training set. If set, file with
            such a name will be searched and the data in the file incorporated
            to the new training set, if the file exists.

        logfile: file object or str
            If *logfile* is a string, a file with that name will be opened.
            Use '-' for stdout

        trajectory: string
            Pickle file used to store trajectory of atomic movement.

        master: boolean
            Defaults to None, which causes only rank 0 to save files. If
            set to True, this rank will save files.

        force_consistent: boolean or None
            Use force-consistent energy calls (as opposed to the energy
            extrapolated to 0 K). By default (force_consistent=None) uses
            force-consistent energies if available in the calculator, but
            falls back to force_consistent=False if not.

        prior: Prior object or None
            Prior for the GP regression of the PES surface
            See ase.optimize.gpmin.prior
            If *prior* is None, then it is set as the
            ConstantPrior with the constant being updated
            using the update_prior_strategy specified as a parameter

        kernel: Kernel object or None
            Kernel for the GP regression of the PES surface
            See ase.optimize.gpmin.kernel
            If *kernel* is None, then it is set as the
            SquaredExponential kernel.
            Note: It needs to be a kernel with derivatives!!!!!

        noise: float
            Regularization parameter for the Gaussian Process Regression.

        weight: float
            Prefactor of the Squared Exponential kernel.
            If *update_hyperparams* is False, changing this parameter
            has no effect on the dynamics of the algorithm.

        update_prior_strategy: string
            Strategy to update the constant from the ConstantPrior
            when more data is collected. It does only work when
            Prior = None

            options:
                'maximum': update the prior to the maximum sampled energy
                'init' : fix the prior to the initial energy
                'average': use the average of sampled energies as prior

        scale: float
            scale of the Squared Exponential Kernel

        update_hyperparams: boolean
            Update the scale of the Squared exponential kernel
            every batch_size-th iteration by maximizing the
            marginal likelhood.

        batch_size: int
            Number of new points in the sample before updating
            the hyperparameters.
            Only relevant if the optimizer is executed in update_hyperparams
            mode: (update_hyperparams = True)

        bounds: float, 0<bounds<1
            Set bounds to the optimization of the hyperparameters.
            Let t be a hyperparameter. Then it is optimized under the
            constraint (1-bound)*t_0 <= t <= (1+bound)*t_0
            where t_0 is the value of the hyperparameter in the previous
            step.
            If bounds is False, no constraints are set in the optimization of
            the hyperparameters.


        .. warning:: The memory of the optimizer scales as O(n²N²) where
                     N is the number of atoms and n the number of steps.
                     If the number of atoms is sufficiently high, this
                     may cause a memory issue.
                     This class prints a warning if the user tries to
                     run GPMin with more than 100 atoms in the unit cell.

        """

        # Warn the user if the number of atoms is very large
        if len(atoms) > 100:
            warning = ('Possible Memeroy Issue. There are more than '
                       '100 atoms in the unit cell. The memory '
                       'of the process will increase with the number '
                       'of steps, potentially causing a memory issue. '
                       'Consider using a different optimizer.')

            warnings.warn(warning)

        # Give it default hyperparameters

        if update_hyperparams:       # Updated GPMin
            if scale is None:
                scale = 0.3
            if noise is None:
                noise = 0.004
            if weight is None:
                weight = 2.

            if bounds is None:
                self.eps = 0.1
            elif bounds is False:
                self.eps = None
            else:
                self.eps = bounds

            if batch_size is None:
                self.nbatch = 1
            else:
                self.nbatch = batch_size

        else:                        # GPMin without updates
            if scale is None:
                scale = 0.4
            if noise is None:
                noise = 0.001
            if weight is None:
                weight = 1.

            if bounds is not None:
                warning = ('The parameter bounds is of no use '
                           'if update_hyperparams is False. '
                           'The value provided by the user '
                           'is being ignored.')
                warnings.warn(warning, UserWarning)
            if batch_size is not None:
                warning = ('The parameter batch_size is of no use '
                           'if update_hyperparams is False. '
                           'The value provived by the user '
                           'is being ignored.')
                warnings.warn(warning, UserWarning)

            # Set the variables to something anyways
            self.eps = False
            self.nbatch = None

        self.strategy = update_prior_strategy
        self.update_hp = update_hyperparams
        self.function_calls = 1
        self.force_calls = 0
        self.x_list = []      # Training set features
        self.y_list = []      # Training set targets

        Optimizer.__init__(self, atoms, restart, logfile,
                           trajectory, master, force_consistent)

        if prior is None:
            self.update_prior = True
            prior = ConstantPrior(constant=None)

        else:
            self.update_prior = False

        self.gp = GaussianProcess(use_forces=True,
                                  prior=prior)
        self.gp.kernel = CCKernel()
        self.gp.prior.use_update = False

        self.gp.set_hyperparams(dict(weight=weight, scale=scale, noise=noise))

    def coords2fingerprint(self, r):
        atoms = self.atoms.copy()
        atoms.positions = r.reshape(-1, 3)
        return CartesianCoordFP(atoms)

    def acquisition(self, r):
        fp = self.coords2fingerprint(r)
        e, V = self.gp.predict(fp)

        return e[0], e[1:]

    def update(self, r, e, f):
        """Update the PES:
        update the training set, the prior and the hyperparameters.
        Finally, train the model """

        # update the training set
        self.update_training_set(r, e, f)

        # Set/update the constant for the prior
        self.set_updated_prior()

        # update hyperparams
        self.fit_to_batch()

        # build the model
        self.gp.train(np.array(self.x_list), np.array(self.y_list))

    def update_training_set(self, r, e, f):
        fp = self.coords2fingerprint(r)
        self.x_list.append(fp)
        f = f.reshape(-1)
        y = np.append(np.array(e).reshape(-1), -f)
        self.y_list.append(y)

    def set_updated_prior(self):
        if self.update_prior:
            if self.strategy == 'average':
                av_e = np.mean(np.array(self.y_list)[:, 0])
                self.gp.prior.set_constant(av_e)
            elif self.strategy == 'maximum':
                max_e = np.max(np.array(self.y_list)[:, 0])
                self.gp.prior.set_constant(max_e)
            elif self.strategy == 'init':
                self.update_prior = False

    def relax_model(self, r0):

        result = minimize(self.acquisition, r0,
                          method='L-BFGS-B', jac=True)

        if result.success:
            return result.x
        else:
            self.dump()
            raise RuntimeError(
                "The minimization of the acquisition function has "
                "not converged")

    def fit_to_batch(self):
        '''Fit hyperparameters keeping the ratio noise/weight fixed'''
        if not (self.update_hp and
                self.function_calls % self.nbatch == 0 and
                self.function_calls != 0):
            return

        ratio = self.gp.hp['noise'] / self.gp.hp['weight']

        GPMin_HPFitter.fit(self.gp, eps=self.eps)
        self.gp.train(self.gp.X, self.gp.Y)

        self.noise = ratio * self.gp.hp['weight']

    def step(self, f=None):

        atoms = self.atoms

        if f is None:
            f = atoms.get_forces()

        r0 = atoms.get_positions().reshape(-1)
        e0 = atoms.get_potential_energy(force_consistent=self.force_consistent)
        self.update(r0, e0, f)

        r1 = self.relax_model(r0)
        self.atoms.set_positions(r1.reshape(-1, 3))
        e1 = self.atoms.get_potential_energy(
            force_consistent=self.force_consistent)
        f1 = self.atoms.get_forces()

        self.function_calls += 1
        self.force_calls += 1

        count = 0
        while e1 >= e0:

            self.update(r1, e1, f1)
            r1 = self.relax_model(r0)

            self.atoms.set_positions(r1.reshape(-1, 3))
            e1 = self.atoms.get_potential_energy(
                force_consistent=self.force_consistent)
            f1 = self.atoms.get_forces()

            self.function_calls += 1
            self.force_calls += 1

            if self.converged(f1):
                break

            count += 1
            if count == 30:
                raise RuntimeError('A well-defined local minimum was not found '
                                   'in the surrogate model surface.')
        self.dump()

    def dump(self):
        '''Save the training set'''
        if world.rank == 0 and self.restart is not None:
            with open(self.restart, 'wb') as fd:
                pickle.dump((self.x_list, self.y_list), fd, protocol=2)

    def read(self):
        self.x_list, self.y_list = self.load()


class GPMin_HPFitter:

    @staticmethod
    def neg_log_likelihood(params, gp, *args):

        gp.set_hyperparams(dict(weight=params[0],
                                scale=params[1]))
        gp.train(gp.X, gp.Y)

        y = gp.Y.flatten()

        # Compute log likelihood
        logP = (- 0.5 * np.dot(y - gp.prior_array, gp.model_vector) +
                - np.sum(np.log(np.diag(gp.L))) +
                - gp.X.shape[0] * 0.5 * np.log(2 * np.pi))

        # Gradient of the loglikelihood
        grad = gp.kernel.gradient(gp.X)

        # vectorizing the derivative of the log likelyhood
        D_P_input = np.array([np.dot(np.outer(gp.model_vector,
                                              gp.model_vector), g)
                              for g in grad])
        D_complexity = np.array([cho_solve((gp.L, gp.lower), g,
                                           overwrite_b=True)
                                 for g in grad])

        DlogP = 0.5 * np.trace(D_P_input - D_complexity, axis1=1, axis2=2)
        return -logP, -DlogP

    @classmethod
    def fit(cls, gp, bounds=None, tol=1e-2, eps=None):
        '''Optimize the scale and prefactor
        of the Gaussian Process kernel by maximizing the marginal
        log-likelihood.

        Parameters:

        gp: GaussianProcess object for which to optimize the hyperparameters.
        bounds: Not used right now. See `eps`.
        tol: tolerance on the maximum component of the gradient of the log-
        likelihood.
           (See scipy's L-BFGS-B documentation:
           https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html )
        eps: include bounds to the hyperparameters as a +- a percentage of
             hyperparameter. If eps is None, there are no bounds
             in the optimization

        Returns:

        result (dict) :
              result = {'hyperparameters': (numpy.array) New hyperparameters,
                        'converged': (bool) True if it converged,
                                            False otherwise
                       }


        '''

        params = [gp.hp['weight'], gp.hp['scale']]
        arguments = (gp,)

        if eps is not None:
            bounds = [((1 - eps) * p, (1 + eps) * p) for p in params]
        else:
            bounds = None

        result = minimize(cls.neg_log_likelihood, params, args=arguments,
                          method='L-BFGS-B', jac=True, bounds=bounds,
                          options={'gtol': tol, 'ftol': 0.01 * tol})

        new_hp = {'weight': result.x[0], 'scale': result.x[1]}
        gp.set_hyperparams(new_hp)

        return {'hyperparameters': new_hp, 'converged': result.success}

    def fit_prefactor(self, gp, option='update'):
        """Fit weight of the kernel keeping all other hyperparameters fixed.
        Here we assume the kernel k(x,x',theta) can be factorized as:
                    k = weight**2 * f(x,x',other hyperparameters)
        this is the case, for example, of the Squared Exponential Kernel.

        Parameters:

        X: observations(i.e. positions). numpy array with shape: nsamples x D
        Y: targets (i.e. energy and forces).
           numpy array with shape (nsamples, D+1)
        option: Whether we just want the value or we want to update the
           hyperparameter. Possible values:
               update: change the weight of the kernel accordingly.
                       Requires a trained Gaussian Process. It
                       works with any kernel.
                       NOTE: the model is RETRAINED

               estimate: return the value of the weight that maximizes
                         the marginal likelihood with all other variables
                         fixed.
                         Requires a trained Gaussian Process with a kernel of
                         value 1.0

        Returns:

        weight: (float) The new weight.
        """

        w = gp.hp['weight']
        if option == 'estimate':
            assert w == 1.0
        y = gp.Y.flatten()
        m = gp.prior.prior(gp.X)
        factor = np.sqrt(np.dot(y - m, gp.model_vector) / len(y))

        if option == 'estimate':
            return factor
        elif option == 'update':
            w *= factor
            self.hyperparams[0] = w
            gp.set_hyperparams(self.hyperparams)
            gp.train(gp.X, gp.Y)
            return w

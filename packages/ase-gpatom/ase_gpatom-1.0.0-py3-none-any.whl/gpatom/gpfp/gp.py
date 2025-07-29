import numpy as np
from scipy.linalg import solve_triangular, cho_factor, cho_solve

from gpatom.gpfp.kernel import FPKernel, FPStressKernel, FPKernelNoforces
from gpatom.gpfp.prior import ConstantPrior


class GaussianProcess:

    """
    Gaussian process regression class

    Examples
    1 instantiate class
    >>> gp=GaussianProcess(hp=..., prior=..., kenel=..., ...)
    2 train model on list of fingerprints X and list of tragets Y
    >>> gp.train(X, Y)
    3 predict energies and gradients from fingerprint x
    >>> predictions=gp.predict(x)
    4 predict stresses from fingerprint x
    >>> stress=gp.predict_stress(x)
    """


    def __init__(self, hp=None, prior=None, kernel=None, kerneltype='sqexp',
                 use_forces=True, use_stress=False, use_noise_correction=True):
        """
        Parameters:
        
        hp: dictionary of hyperparameters, optional
            The hyperparameters of the kernel and gaussian process including:
            'scale':  length scale                              default: 1 
            'weight':  prefactor (not squared)                  default: 1
            'ratio':   ratio of noise to weight.                default: 1e-3
            'noisefactor':  noise on forces relative 
                            to the noise on energies            default: 1
            'corr': corrective minimum noise to make 
                    sure covariance matix is invertible         default: 0
            there is also a prior hyperparameter but that is given through the
            constant of the prior object
            All of these hyperparameters can be dynamically set using a 
            hyperparameter fitter object. 

        prior: Prior object, optional
            Either ConstantPrior or CalculatorPrior objects both including
            a constant, being the last hyperparameter.
            If None a ConstantPrior is setup
            Default is None
            
        kernel: Kernel object, optional
            kernel method used in gaussian process
            Default is None 
                if use_stress=True:  FPStressKernel
                if use forces=True and use_stress=False:  FPKernel
                else FPKernelNoforces
        
        kerneltype: string, optional
            The specifik type of kernel used in the kernel object
            Default is 'slsqp'
            
        use_forces: bool, optional
            If Gaussian process should be trained on forces
            Default is True
            
        use_stress: bool, optional
            If Gaussian process should be trained on stresses. 
            If trained on stresses, it will for now also train on forces
            Default is False
            
        use_noise_correction: bool, optional
            If an automatic minimal noise correction should be added
            to make sure covariance matric is always invertible. 
            Important if using hyperparameter fitting with variable noise ratio
            Default is True
        """
        
        self.kernel_name=kerneltype  

        self.use_forces = use_forces
        
        self.use_stress = use_stress
        
        self.use_noise_correction=use_noise_correction
     
        
        if self.use_stress:
            self.use_forces=True
        
        
        if kernel is None:
            if self.use_stress:
                kernel = FPStressKernel(kerneltype) 
            elif self.use_forces:
                kernel = FPKernel(kerneltype)
            else:
                kernel = FPKernelNoforces(kerneltype)
        
        self.kernel=kernel


        default_params = dict(scale=self.kernel.kerneltype.scale,
                              weight=self.kernel.kerneltype.weight,
                              ratio=1e-3,
                              noisefactor=1,
                              corr=0)

        self.hp = default_params  

        if prior is None:
            prior = ConstantPrior(0.0)
        self.prior = prior

        self.set_hyperparams(hp) 
    
    def set_hyperparams(self, new_params):
        """ Method to set the total noise """

        self.hp.update(new_params)
 
        self.hp.update({'noise': (self.hp['corr'] + self.hp['ratio'])*self.hp['weight']})
 
        if 'prior' in self.hp.keys():
            self.prior.set_constant(self.hp['prior'])

        self.kernel.set_params(self.hp)

        return self.hp
    
    def update_noise(self, K):
        """Method to set noise correction and total noise"""
        
        K_diag=np.diag(K)
        noise_correction_squared=self.get_correction(K_diag)
        noise_correction=np.sqrt(noise_correction_squared)

        self.set_hyperparams({'corr': noise_correction})          
        self.set_hyperparams({'noise': (self.hp['corr'] + self.hp['ratio'])*self.hp['weight']}) 


    def train(self, X, Y):
        """
        Method to train the  Gaussian process

        Parameters
        ----------
        X : list
            List of fingerprints
        Y : list
            list of targets (energies, forces, stresses)

        Returns
        -------
        None.

        """ 
        
        X = np.array(X)        
        Y = np.array(Y)
        
        K = self.kernel.kernel_matrix(X)    
                        
        self.X = X
        self.Y = Y
                
        
        # Nones must be keep til I contact Andreas about use in hpfitter   
        self.K_reg = self.add_regularization(K, None, None)  
        
        self.model_vector = self.calculate_model_vector(self.K_reg)                        
        
        return
    
    
    def get_correction(self, K_diag):
        """ 
        Method to find the minimal noise correction to make sure 
        the covariance matrix is always invertible
        Method cannot be deleted or some hyperparameter fitters will not work.
        """
                
        if self.use_noise_correction:
            K_diag=K_diag/(self.hp['weight']**2)
            correction_squared=(np.sum(K_diag)**2)*(1.0/(1.0/(2.3e-16)-(len(K_diag)**2)))  
        else:
            correction_squared=0
            
        return correction_squared


    # Ntrain and Ngrads must be keep til I contact Andreas about use in hpfitter
    # as he has imported Natoms in stead of Ngrads
    def add_regularization(self, matrix, Ntrain, Ngrads):
        """
        Parameters
        ----------
        matrix : numpy.array
            Covariance matrix without noise
        Ntrain : int
            Number of training structures (same as number of energy targets)
        Ngrads : int
            Number of derivative observations

        Returns
        -------
        matrix : numpy.array
            Covariance matrix with noise 
        """
        
        Ntrain=len(self.X)
        Ngrads = int((len(self.Y.flatten()) / len(self.X) - 1))
        
        if self.use_forces or self.use_stress:
            regularization = np.array(Ntrain * ([self.hp['noise'] ] +   
                                                Ngrads * [self.hp['noise'] * 
                                                          self.hp['noisefactor'] ]))    
        else:
            regularization = np.array(Ntrain * ([self.hp['noise']]))            

        matrix += np.diag(regularization**2)
        return matrix


    def calculate_model_vector(self, matrix):
        """
        Calculate C^-1 * (Y - prior) where C is the regularized covariance
        matric, Y is the targets and prior is the prior values. 
        Method use Cholesky factorization to solve invert the covariance matrix 
        """
        
        # factorize K-matrix:
        self.L, self.lower = cho_factor(matrix,                  
                                        lower=True,
                                        check_finite=True)
        
        self.prior_array = self.calculate_prior_array(self.X, 
                                                      get_forces=self.use_forces,
                                                      get_stress=self.use_stress)

        model_vector = self.Y.flatten() - self.prior_array
                
        # Overwrite model vector so that it becomes C^-1 * (Y - prior):
        cho_solve((self.L, self.lower), model_vector,                  
                  overwrite_b=True, check_finite=True)
        
        return model_vector


    def calculate_prior_array(self, list_of_fingerprints, 
                              get_forces=True, get_stress=False):
        """
        Calculate the prior values for all targets in the training set.
        can be done on (stress, force and energy), (force and energy) or
        just energy.
        """
        
        if get_stress:
            return list(np.hstack([self.prior.potential_with_stress(x)
                                   for x in list_of_fingerprints]))
        elif get_forces:
            return list(np.hstack([self.prior.potential(x)
                                   for x in list_of_fingerprints]))
        else:
            return list(np.hstack([self.prior.potential(x)[0]
                                   for x in list_of_fingerprints]))
        


    def predict(self, x, get_variance=False, return_dkdx=False):
        """
        Calculates predictions, derivatives, varaiance and variance derivatives
        
        Parameters
        ----------
        x : fingerprint object
            Any of the fingerprints in the BEACON package
        get_variance : bool optional
            If the target variance should be calculated or not.
            if False, Variance will be imported as None
            The default is False.
        return_dkdx : bool, optional
            If the derivative of the variance should be calculated and
            outputted

        Returns
        -------
        f : numpy.array
            The energy and derivative predictions
        V : numpy.array
            The variance of the predictions
        dk_dxi : numpy.array 
            The derivatives of the kernel_vector.
            Needed for calculating derivative of uncertainty when not 
            training Gaussian process in derivatives.
            Only outputted if return_dkdx=True
        """
        
        k = self.kernel.kernel_vector(x, self.X)

        f = np.dot(k, self.model_vector)
        
        if self.use_stress:
            f[-9:]=f[-9:]/x.atoms.get_volume()

        dk_dxi=None
        if not self.use_forces:
            dk_dxi = (np.array([self.kernel.kerneltype.kernel_gradient(x, x2)
                                for x2 in self.X]))

            forces = np.einsum('ijk,i->jk', dk_dxi,
                               self.model_vector).flatten()
            f = np.array(list([f]) + list(forces))
            
        prior_array = self.calculate_prior_array([x], get_forces=True, 
                                                 get_stress=self.use_stress)
                        
        f += np.array(prior_array)

        V = self.calculate_variance(get_variance, k, x)
        
        if return_dkdx:
            return f, V, dk_dxi
        
        return f, V


    def calculate_variance(self, get_variance, k, x):
        """
        Parameters
        ----------
        get_variance : bool
            If True the variance will be outputted not as None
        k : numpy.array
            Kernel vector array
        x : fingerprint object
            Any of the BEACON fingerprint objects

        Returns
        -------
        V : numpy.array
            The variance on predictions

        """
        V = None
        if get_variance:
        
            variance = self.kernel.kernel(x, x)
            
            self.Ck=cho_solve((self.L, self.lower), k.T.copy(),                  
                              overwrite_b=False, check_finite=True)
                        
            if self.use_forces:
                covariance = np.einsum('ij,jk->ik', k, self.Ck)
            else:
                covariance = np.dot(k,self.Ck) 
                        
            V = variance - covariance
    
        return V


    def predict_stress(self, x, return_dkdc=False):
        """
        Parameters
        ----------
        x : fingerpriint object
            Any of the BEACON fingerpint objects
        return_dkdc : bool, optional
            If the derivative of the variance should be predicted.´
            Needed for calculating derivative of uncertainty when not 
            training Gaussian process in derivatives.

        Returns
        -------
        stress : numpy.array
            The predicted stress
            
        dkdc : Derivatives of the kernel vector e.r.t the cell parameters.
               Only outputted if return_dkdc=True
        """

        priorstress = self.prior.get_stress(x)
        x.atoms.calc = None

        if not self.use_forces:
            
            dk_dc = np.array([self.kernel.kerneltype.dkernel_dc(x, x2)
                              for x2 in self.X])
            
        else:            
            d_dc = [np.concatenate((self.kernel.kerneltype.dkernel_dc(x, x2)[np.newaxis, :, :],
                                    self.kernel.kerneltype.dkernelgradient_dc(x, x2).reshape(-1, 3, 3)),
                                   axis=0)
                    for x2 in self.X]
            
            
            dk_dc = np.array(d_dc)
            dk_dc = dk_dc.reshape(-1, 3, 3)

        strain = np.einsum('ijk,i->jk', dk_dc, self.model_vector)

        # XXX In future ASE, voigt form is obtained from
        # ase.stress methods
        strain = strain.flat[[0, 4, 8, 5, 2, 1]]

        stress = strain / x.atoms.get_volume()
        
        stress += priorstress
        
        if return_dkdc:
            return stress, dk_dc
        
        return stress
    

    def get_properties(self, x):
        """
        Performs the predict operation operation but outputs
        all variables in a more intuitive way. Does not output stress.
        Used in the Model class.

        Parameters
        ----------
        x : fingerprint object
            Any of the standard BEACON fingerprints

        Returns
        -------
        energy : float
            The predicted energy
        forces : numpy.array
            The predicted derivatives w.r.t atomic coordinates
        uncertainty_squared : numpy.array
            The variance of the energy. 
        """
        
        f, V = self.predict(x, get_variance=True)
                
        energy=f[0]
        forces=f[1:].reshape(-1, 3)
        
        if self.use_forces:
            uncertainty_squared = V[0, 0]
        else:
            uncertainty_squared = V[0]
        
        return energy, forces, uncertainty_squared


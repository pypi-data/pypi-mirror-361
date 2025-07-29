from gpatom.gpfp.gp import GaussianProcess
from gpatom.fractional_beacon.gpfp.kernel import (ICEKernel, 
                                                  ICEStressKernel,
                                                  ICEKernelNoforces)
import numpy as np

from gpatom.hyperspatial_beacon.gpfp.gp import HighDimGaussianProcess


class ICEGaussianProcess(HighDimGaussianProcess):
    """
    Gaussian process extended to predict derivatives of the surrogate surface
    w.r.t elemental fractions.
    It extends the HighDimGaussianProces and can hence also make predictions
    for hyperspatial atomic sytems
    The essential difference is that we need to predict
    the derivatives of the surrogate PES w.r.t. the fractions.
    
    To work prior input must be of class WeightedConstantPrior 
    or WeightedCalculatorPrior
    """

    def __init__(self, dims=3, n_ghost=0, **kwargs):
        """
        Parameters
        ----------
        dims : int, optional
            The total number of spatial dimesnions.
            The default is 3, i.e. a normal atomic system. 
        n_ghost : int, optional
            The total number of ghost atoms in the atomic systems. 
            This is automatically regulated in the ICEOptimizer
            The default is 0.
        **kwargs : parameters for GaussianProcess object
            See documentation of GaussianProcess
        """

        super().__init__(**kwargs)

        kernelparams = {'weight': self.hp['weight'],
                        'scale': self.hp['scale']}

        if self.use_stress:
            self.kernel = ICEStressKernel(kerneltype='sqexp', params=kernelparams)
        elif self.use_forces:
            self.kernel = ICEKernel(kerneltype='sqexp', params=kernelparams)
        else:
            self.kernel = ICEKernelNoforces(kerneltype='sqexp', params=kernelparams)
            
        # both of these are set dynamicly inside beacon
        self.ndf_coord=max(3,dims)  # coordinate degrees of freedom pr. atom.
        self.n_ghost=int(n_ghost)   # number of extra atoms

    def set_sizes(self):
        """
        Set values necessary fro properly reshaping arrays during prediction
        """
               
        # The number of atoms. expected to be the same for all structures
        self.natoms=len(self.X[0].atoms)+self.n_ghost   
        # The number of structures in database
        self.ntrain=len(self.X)
        # The number of coordinate derivative components on the training structures
        self.nforces=  3 * (self.natoms-self.n_ghost)
        # The total number of observations on a training structure, not including stresses
        self.singlesize=1 + self.nforces
        # The total number of observations in training set, not including stresses
        self.alphasize=self.ntrain * self.singlesize
        # Number of elemental fraction degrees of freedom pr. atom
        self.ndf_frac=len(self.X[0].atoms.symbols.species())
        # Total number of degrees of freedom pr. atom
        self.ndf_total=self.ndf_coord + self.ndf_frac 
        
    def set_n_ghost(self, n_ghost):
        """
        Reset the number of ghost atoms.
        Important when going from predicting a hypersystem and a real system
        """
        self.n_ghost=int(np.sum(n_ghost))
        
    def set_dims(self, dims):
        """
        Reset the number of spatial dimesnions.
        Important when going from predicting a hypersystem and a real system
        """
        self.ndf_coord=max(3, dims)

    def predict(self, x, get_variance=False, return_kgrads=False):
        """
        See GaussianProcess predict method. Here extended to also
        predict the derivatives of the elemental fractions
        """        
        self.set_sizes()
      
        
        if self.use_forces:

            kv = self.kernel.kernel_vector(x, self.X)  
            
            f = np.dot(kv, self.model_vector) 
                
            if self.use_stress:
                f[-9:]/=x.atoms.get_volume()
                
            prior_array = self.calculate_prior_array([x], get_forces=True,
                                                     get_stress=self.use_stress)
            
            f+=prior_array
            
        
            dk_dxi=None
        
            dk_dq=self.get_frac_kernel(x)

            frac_gradients = (np.einsum('ijk,j->ik', dk_dq, 
                                        self.model_vector,
                                        optimize=True))

            prior_frac_grads=self.prior.get_frac_grads(x)

            frac_gradients+=prior_frac_grads
            
           
            all_gradients = self.get_gradient_array(f, frac_gradients) 
           
            
            f = [f[0]] + list(all_gradients)

            f = np.array(f)

            V = self.calculate_variance(get_variance, kv, x)

        else:
            
            k = self.kernel.kernel_vector(x, self.X)
            
            f = np.dot(k, self.model_vector)
            
            dk_dxi = np.array([self.kernel.kerneltype.kernel_gradient(x, x2)
                               for x2 in self.X])
            dk_dq = np.array([self.kernel.kerneltype.kernel_gradient_frac(x, x2)
                               for x2 in self.X])
            
            dk = np.concatenate((dk_dxi, dk_dq), axis=2)

            forces = np.einsum('ijk,i->jk', dk,
                               self.model_vector).flatten()
            
            prior_array = self.calculate_prior_array([x], get_forces=True)
            prior_energy=prior_array[0]
            prior_forces=np.array(prior_array[1:]).reshape(self.natoms,self.ndf_coord)
            prior_frac_grads=self.prior.get_frac_grads(x)
            
            f+=prior_energy
            forces.reshape(self.natoms,self.ndf_total)[:,0:self.ndf_coord]+=prior_forces
            forces.reshape(self.natoms,self.ndf_total)[:,self.ndf_coord:]+=prior_frac_grads
            
            f = list([f]) + list(forces)
            
            f=np.array(f)
            
            V = self.calculate_variance(get_variance, k, x)
            
        
        if return_kgrads:
            return f, V, dk_dxi, dk_dq
        
        return f, V

    def get_frac_kernel(self, x):
        """
        Get derivatives of kernel with respect to fraction derivatives
        when Gaussian proces is trained derivatives (forces and stresses)

        Parameters
        ----------
        x : fingerprint object
            Any of the Fractional BEACON fingerpint objects

        Returns
        -------
        K_x_X : numpy.array
            Kernel derivatives w.r.t elemental fractions
        """
        dk_dq = np.array([self.kernel.kerneltype.kernel_gradient_frac(x, x2)
                          for x2 in self.X])
    
        # Fractions derivatives of kernel gradients:
        d2k_drm_dq = np.array([self.kernel.kerneltype.dkernelgradient_dq(x, x2)
                               for x2 in self.X])
        
        d2k_drm_dq = d2k_drm_dq.reshape(self.ntrain, self.natoms, self.ndf_frac*self.nforces)
                
        # Kernel vector:
        K_x_X = np.concatenate((dk_dq, d2k_drm_dq), axis=2)     
        
        if self.use_stress:
            d2k_dc_dq = np.array([self.kernel.kerneltype.ddq_dkdc(x, x2)
                                   for x2 in self.X])
            
            d2k_dc_dq = d2k_dc_dq.reshape(self.ntrain, self.natoms, self.ndf_frac*9)
            
            K_x_X = np.concatenate((K_x_X, d2k_dc_dq), axis=2)
            
            self.alphasize+=self.ntrain*9
            
        K_x_X = K_x_X.swapaxes(0, 1)
        K_x_X = K_x_X.reshape((self.natoms, self.alphasize, self.ndf_frac)) 
        
        return K_x_X


    def get_properties(self, x, return_frac_grads=False):
        """
        Performs the predict operation operation but outputs
        all variables in a more intuitive way. Does not output stress.
        Used in the Model class.

        Parameters
        ----------
        x : fingerprint object
            Any of the Fractional BEACON fingerprints
        return_frac_grads : bool, optional
            If the derivatives w.r.t fractional coordinates should be returned 
            The default is False.

        Returns
        -------
        energy : float
            The predicted energy
        forces : numpy.array
            The predicted derivatives w.r.t atomic coordinates in all dimensions 
        uncertainty_squared : numpy.array
            The variance of the energy. 
        frac_grads : numpy.array
            The predicted derivatives w.r.t elemental fractions 
        """
        
        f, V = self.predict(x, get_variance=True)
        energy, forces, frac_grads = self.translate_predictions(f)
        
        if self.use_forces:
            uncertainty_squared = V[0, 0]
        else:
            uncertainty_squared = V[0]
        
        if return_frac_grads:
            return energy, forces, uncertainty_squared, frac_grads
        else: 
            return energy, forces, uncertainty_squared
        
        
    def get_gradient_array(self, predictions, frac_gradients):
        """
        Combine all predicted derivatives into one array

        Parameters
        ----------
        predictions : numpy.array
            Energy and all atomic and cell coordinate derivatives
        frac_gradients : numpy.array
            All derivatives w.r.t the elemental fractions.

        Returns
        -------
        all_gradients : numpy.array
            Array of all derivatives in a single array
        """
        
        if self.use_stress:
            coord_grads_list=predictions[1:-9]
        else:
            coord_grads_list=predictions[1:]
            
        coord_gradients = coord_grads_list.reshape(self.natoms, 
                                                   self.ndf_coord)
            
        all_gradients = np.concatenate((coord_gradients, frac_gradients),
                                       axis=1).flatten()
            
        if self.use_stress:
            stress=predictions[-9:]
            all_gradients = np.concatenate( (all_gradients, stress  ) )
            
        return all_gradients
        
        
    def translate_predictions(self, predict_array):
        """
        Parameters
        ----------
        predict_array : numpy.array
            Array of all predictions

        Returns
        -------
        energy : float
            The predicted energy
        forces : TYPE
            The predicted derivatives w.r.t the atomic coordinates
        frac_grads : TYPE
            The predicted derivatives w.r.t the elemental fractions
        """
        
        energy=predict_array[0]
        
        grads=predict_array[1:].reshape(-1, self.ndf_total)
        
        forces=grads[:, :self.ndf_coord]
        
        frac_grads=grads[:, self.ndf_coord:]
        
        return energy, forces, frac_grads  
        
from gpatom.gpfp.gp import GaussianProcess
from gpatom.hyperspatial_beacon.gpfp.kernel import HighDimKernel, HighDimStressKernel
from gpatom.gpfp.kernel import FPKernelNoforces

class HighDimGaussianProcess(GaussianProcess):
    """
    Gaussian process generalized to handle an arbitrary amount of
    spatial dimensions.
    All fingerprints going into the process must carry the property 'dims',
    describing the total number of spatial dimensions.
    
    See standard BEACON GaussianProcess for further documentation
    
    To work prior input should be of class HighDimConstantPrior or
    HighDimCalculatorPrior
    """

    def __init__(self, **kwargs):
        GaussianProcess.__init__(self, **kwargs)

        kernelparams = {'weight': self.hp['weight'],
                        'scale': self.hp['scale']}

        if self.use_stress:
            self.kernel = HighDimStressKernel(kerneltype='sqexp', params=kernelparams)
        elif self.use_forces:
            self.kernel = HighDimKernel(kerneltype='sqexp', params=kernelparams)
        else:
            self.kernel = FPKernelNoforces(kerneltype='sqexp', params=kernelparams)


    def get_properties(self, x, dims=3):
        """
        Performs the predict operation operation but outputs
        all variables in a more intuitive way. Does not output stress.
        Used in the Model class.

        Parameters
        ----------
        x : fingerprint object
            Any HighDim fingerprint
        dims: int, optional
            The total number of spatial dimensions.
            The defalt is 3, i.e. a normal atomic system. 
            
        Returns
        -------
        energy : float
            The predicted energy
        forces : numpy.array
           The predicted derivatives w.r.t atomic coordinates in all dimensions
        uncertainty_squared : numpy.array
            The variance of the energy. 
        """
        
        f, V = self.predict(x, get_variance=True)
        
        energy, forces = self.translate_predictions(f, dims)
        
        
        if self.use_forces:
            uncertainty_squared = V[0, 0]
        else:
            uncertainty_squared = V[0]
    
        return energy, forces, uncertainty_squared
    
    def translate_predictions(self, predict_array, dims=3):
        """
        Takes the output of the prediction method and splits it into
        energies and atomic´ coordinate derivatives
        
        Parameters
        ----------
        predict_array : numpy.array
            
        dims: int, optional
            The total number of spatial dimensions.
            The defalt is 3, i.e. a normal atomic system.

        Returns
        -------
        energy : float
            The predicted energy
        forces : numpy.array
            The predicted coordinate derivatives
        """
        
        energy=predict_array[0]
        forces=predict_array[1:].reshape(-1, max(dims,3))
         
        return energy, forces

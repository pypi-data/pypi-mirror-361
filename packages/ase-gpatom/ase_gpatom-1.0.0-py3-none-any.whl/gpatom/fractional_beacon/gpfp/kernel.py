import numpy as np
from gpatom.fractional_beacon.gpfp.kerneltypes import ICESquaredExp
from gpatom.gpfp.kernel import FPKernel, FPStressKernel


class ICEKernel(FPKernel):
    
    """
    Kernel class used when training on both energies and forces 
    for atoms with fractional chemical elements in an arbitrary amount of 
    dimensions
    
    See FPKernel for more info
    """
    
    def __init__(self, kerneltype='sqexp', params=None):
      
        kerneltypes = {'sqexp': ICESquaredExp}

        if params is None:
            params = {}
            
        kerneltype = kerneltypes.get(kerneltype)
        self.kerneltype = kerneltype(**params)
            
    def get_size(self, x):
        """
        Return the correct size of a kernel matrix when gradients are
        trained.
        
        Fingerprint, x, must carry an attribute "dims", describing the number of
        spatial dimensions
        """
        
        return len(x.atoms) * x.dims + 1
    

class ICEStressKernel(FPStressKernel):
    
    """
    Kernel class used when training on both energies and forces 
    for atoms with fractional chemical elements in an arbitrary amount of 
    dimensions
    
    See FPStressKernel for more info
    """
    
    def __init__(self, kerneltype='sqexp', params=None):
      
        kerneltypes = {'sqexp': ICESquaredExp}

        if params is None:
            params = {}
            
        kerneltype = kerneltypes.get(kerneltype)
        self.kerneltype = kerneltype(**params)
            
    def get_size(self, x):
        """
        Return the correct size of a kernel matrix when gradients are
        trained.
        
        Fingerprint, x, must carry an attribute "dims", describing the number of
        spatial dimensions
        """
        
        return len(x.atoms) * x.dims + 1
    
    
    
class ICEKernelNoforces(ICEKernel):
    """
    Kernel class used when training on energies only for atoms with fractional 
    chemical elements
    """

    def kernel(self, x1, x2):
        return np.atleast_1d(self.kerneltype.kernel(x1, x2))

    def get_size(self, x):
        '''
        Return the size of a kernel matrix
        x: fingerprint
        '''
        return 1
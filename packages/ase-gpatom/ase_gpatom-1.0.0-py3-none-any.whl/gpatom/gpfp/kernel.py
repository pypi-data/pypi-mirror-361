import numpy as np
from ase.parallel import world
from gpatom.gpfp.kerneltypes import SquaredExp, Matern, RationalQuad


class FPKernel:
    """
    Kernel used when training on both energies and forces
    """

    def __init__(self, kerneltype='sqexp', params=None):
        '''
        parameters
        ----------
        kernelttype: string, optional
            The desired kernel
        params: dict, optional
            Hyperparameters for the kernel type
        '''
        kerneltypes = {'sqexp': SquaredExp,
                       'matern': Matern,
                       'rq': RationalQuad}

        if params is None:
            params = {}

        kerneltype = kerneltypes.get(kerneltype)
        self.kerneltype = kerneltype(**params)


    def kernel_function_gradient(self, x1, x2):
        '''
        Gradient of kernel_function w.r.t. coordinates in 'x1'.
        x1: fingerprint object
        x2: fingerprint object
        '''
        gradients = self.kerneltype.kernel_gradient(x1, x2)
        
        return gradients.reshape(-1)

    def kernel_function_hessian(self, x1, x2):
        '''
        Full Hessian matrix of the kernel function w.r.t.
        coordinates in both 'x1' and 'x2'.
        '''
        hessian = self.kerneltype.kernel_hessian(x1, x2)

        # Reshape to 2D matrix:
        size1 = self.get_size(x1) - 1
        size2 = self.get_size(x2) - 1
        
        hessian = hessian.swapaxes(1, 2).reshape(size1, size2)
        
        return hessian

    def kernel(self, x1, x2):
        '''
        Return a full kernel matrix between two
        fingerprints, 'x1' and 'x2'.
        '''

        size1 = self.get_size(x1)
        size2 = self.get_size(x2)

        K = np.empty((size1, size2), dtype=float)
        
        # Maybe investigate why some kernels return length-1 array.
        obj = self.kerneltype.kernel(x1, x2)
        if not np.isscalar(obj):
            assert len(obj) == 1
            obj = obj[0]
            assert np.isscalar(obj)

        K[0, 0] = obj
        K[1:, 0] = self.kernel_function_gradient(x1, x2)
        K[0, 1:] = self.kernel_function_gradient(x2, x1)
        K[1:, 1:] = self.kernel_function_hessian(x1, x2)

        return K


    def kernel_matrix(self, X):
        '''
        Calculates C(X,X) i.e. full kernel matrix for training data.
        '''
        
        Ntrain = len(X)
        size = self.get_matrix_size(X[0])
        
        # allocate memory
        K = np.empty((Ntrain * size,
                      Ntrain * size), dtype=float)

        for i in range(0, Ntrain):
            for j in range(i + 1, Ntrain):
                k = self.kernel(X[i], X[j])
                K[i * size:(i + 1) * size, j *
                  size:(j + 1) * size] = k
                K[j * size:(j + 1) * size, i *
                  size:(i + 1) * size] = k.T

            K[i * size:(i + 1) * size,
              i * size:(i + 1) * size] = self.kernel(X[i], X[i])

        return K

    def kernel_vector(self, x, X):
        '''
        Calculates K(x,X) ie. the kernel matrix between fingerprint
        'x' and the training data fingerprints in X.
        '''

        return np.hstack([self.kernel(x, x2) for x2 in X])

    def get_size(self, x):
        '''
        Return the correct number of energy and force components in system
        '''
        return len(x.atoms) * 3 + 1
    
    def get_matrix_size(self, x):
        '''
        Return the correct kernel matrix size when gradients are trained
        '''
        return self.get_size(x)
    

    def set_params(self, params):
        '''
        Set new (hyper)parameters for the kernel function.
        '''
        self.kerneltype.update(params)


class FPStressKernel(FPKernel):
    """
    Kernel used when training on energies, forces and stresses
    """
     
    def kernel(self, x1, x2):
        """
        Return the full matrix bwtween two fingerprints also including
        the stress terms. for now all 9 components of the stress tensor is used
        """
        
        size1 = self.get_matrix_size(x1)
        size2 = self.get_matrix_size(x2)

        K = np.empty((size1, size2), dtype=float)

        # Maybe investigate why some kernels return length-1 array.
        obj = self.kerneltype.kernel(x1, x2)
        if not np.isscalar(obj):
            assert len(obj) == 1
            obj = obj[0]
            assert np.isscalar(obj)

        # the old force and energy stuff
        K[0, 0] = obj
        K[1:-9, 0] = self.kernel_function_gradient(x1, x2)
        K[0, 1:-9] = self.kernel_function_gradient(x2, x1)
        K[1:-9, 1:-9] = self.kernel_function_hessian(x1, x2)
        
        # stress gradients
        K[-9:, 0] = self.kernel_stress_gradients(x1, x2)
        K[0, -9:] = self.kernel_stress_gradients(x2, x1)
        
        K[-9:, 1:-9] = self.ddc_dkdr(x1, x2)
        K[1:-9, -9:] = self.ddr_dkdc(x1, x2)

        K[-9:, -9:] = self.kernel_stress_hessian(x1, x2)

        return K
  
    
    def get_matrix_size(self, x):
        return self.get_size(x)+9
            
    def kernel_stress_gradients(self, x1, x2):
        """ Get stress energy components """
        kernelgrad=self.kerneltype.dkernel_dc(x1, x2)
        return kernelgrad.flatten()
    
    def ddc_dkdr(self, x1, x2):
        """ Get stress force components """
        hessian_terms=self.kerneltype.dkernelgradient_dc(x1, x2)
        return hessian_terms.reshape(-1, 9).T

    def ddr_dkdc(self, x1, x2):
        """ Get force stress components """
        hessian_terms=self.kerneltype.ddr_dkdc(x1,x2)        
        return hessian_terms.reshape(9,-1).T
            
    def kernel_stress_hessian(self, x1,x2):
        """ Get stress stress components """
        strain_hessian=self.kerneltype.d2kdc2(x1, x2)
        strain_hessian=strain_hessian.swapaxes(1,2).reshape(9,9)
        return strain_hessian


class FPKernelNoforces(FPKernel):
    """
    Kernel used when training on energies only
    """
    def kernel(self, x1, x2):
        return np.atleast_1d(self.kerneltype.kernel(x1, x2))

    def get_size(self, x):
        '''
        Return the correct size of a kernel matrix when gradients are
        NOT trained.
        '''
        return 1

class FPStressKernelNoforces(FPStressKernel):
    """
    Kernel used when training in Energy and stresses but not forces. 
    Isnt really working in BEACON yet
    """
    def kernel(self, x1, x2):
        
        size1 = self.get_size(x1) + 9
        size2 = self.get_size(x2) + 9

        K = np.empty((size1, size2), dtype=float)

        # Maybe investigate why some kernels return length-1 array.
        obj = self.kerneltype.kernel(x1, x2)
        if not np.isscalar(obj):
            assert len(obj) == 1
            obj = obj[0]
            assert np.isscalar(obj)

        # energy
        K[0, 0] = obj
        
        # stress gradients
        K[-9:, 0] = self.kernel_stress_gradients(x1, x2)
        K[0, -9:] = self.kernel_stress_gradients(x2, x1)
        K[-9:, -9:] = self.kernel_stress_hessian(x1, x2)

        return K

    def get_size(self, x):
        '''
        Return the correct size of a kernel matrix when gradients are
        NOT trained.
        '''
        return 1

    def get_matrix_size(self, x):
        return self.get_size(x) + 9 


class FPKernelParallel(FPKernel):

    def kernel_matrix(self, X):
        '''
        Calculates C(X,X) i.e. full kernel matrix for training data.
        '''

        Ntrain = len(X)
        size = self.get_size(X[0])
        
        # allocate memory
        K = np.empty((Ntrain * size,
                      Ntrain * size), dtype=float)
        

        # CALCULATE:
        for i in range(0, Ntrain):
            for j in range(i + 1, Ntrain):

                ij_rank = (i * Ntrain + j) % world.size
                if world.rank == ij_rank:

                    k = self.kernel(X[i], X[j])
                    K[i * size:(i + 1) * size, j *
                      size:(j + 1) * size] = k
                    K[j * size:(j + 1) * size, i *
                      size:(i + 1) * size] = k.T

            ii_rank = (i * Ntrain + i) % world.size
            if world.rank == ii_rank:
                k = self.kernel(X[i], X[i])
                K[i * size:(i + 1) * size,
                  i * size:(i + 1) * size] = k

        # DISTRIBUTE:
        for i in range(0, Ntrain):
            for j in range(i + 1, Ntrain):

                k = K[i * size:(i + 1) * size,
                      j * size:(j + 1) * size]

                # prepare for broadcast:
                k = k.flatten()

                ij_rank = (i * Ntrain + j) % world.size
                world.broadcast(k, ij_rank)

                # reshape back:
                k = k.reshape((size, size))

                K[i * size:(i + 1) * size,
                  j * size:(j + 1) * size] = k
                K[j * size:(j + 1) * size,
                  i * size:(i + 1) * size] = k.T

            k = K[i * size:(i + 1) * size,
                  i * size:(i + 1) * size]
            k = k.flatten()

            ii_rank = (i * Ntrain + i) % world.size
            world.broadcast(k, ii_rank)

            k = k.reshape((size, size))
            K[i * size:(i + 1) * size,
              i * size:(i + 1) * size] = k

        world.broadcast(K, 0)

        return K


class CCKernel(FPKernel):
    '''
    Kernel with Cartesian coordinates.
    '''

    # ---------Derivatives--------
    def squared_distance(self, x1, x2):
        return self.kerneltype.metric.distance(x1, x2)**2

    def dK_dweight(self, X):
        '''
        Return the derivative of K(X,X) respect to the weight
        '''
        return self.K(X, X) * 2 / self.kerneltype.weight

    # ----Derivatives of the kernel function respect to the scale ---
    def dK_dl_k(self, x1, x2):
        '''
        Returns the derivative of the kernel function respect to l
        '''
        return self.squared_distance(x1, x2) / self.kerneltype.scale

    def dK_dl_j(self, x1, x2):
        '''
        Returns the derivative of the gradient of the kernel function
        respect to l
        '''
        prefactor = (-2 * (1 - 0.5 * self.squared_distance(x1, x2)) /
                     self.kerneltype.scale)
        return self.kernel_function_gradient(x1, x2) * prefactor

    def dK_dl_h(self, x1, x2):
        '''
        Returns the derivative of the hessian of the kernel function respect
        to l
        '''
        I = np.identity(self.get_size(x1) - 1)
        P = (np.outer(x1.vector - x2.vector, x1.vector - x2.vector) /
             self.kerneltype.scale**2)
        prefactor = 1 - 0.5 * self.squared_distance(x1, x2)
        return -2 * (prefactor * (I - P) - P) / self.kerneltype.scale**3

    def dK_dl_matrix(self, x1, x2):
        k = np.asarray(self.dK_dl_k(x1, x2)).reshape((1, 1))
        j2 = self.dK_dl_j(x1, x2).reshape(1, -1)
        j1 = self.dK_dl_j(x2, x1).reshape(-1, 1)
        h = self.dK_dl_h(x1, x2)
        return np.block([[k, j2], [j1, h]]) * self.kernel(x1, x2)

    def dK_dl(self, X):
        '''
        Return the derivative of K(X,X) respect of l
        '''
        return np.block([[self.dK_dl_matrix(x1, x2) for x2 in X] for x1 in X])

    def gradient(self, X):
        '''
        Computes the gradient of matrix K given the data respect to the
        hyperparameters. Note matrix K here is self.K(X,X).
        Returns a 2-entry list of n(D+1) x n(D+1) matrices
        '''
        return [self.dK_dweight(X), self.dK_dl(X)]

    def K(self, X1, X2):
        '''
        Compute the kernel matrix
        '''
        self.D = len(X1[0].atoms) * 3
        return np.block([[self.kernel(x1, x2) for x2 in X2] for x1 in X1])

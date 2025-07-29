import numpy as np


class EuclideanDistance:

    @staticmethod
    def distance(fp1, fp2):
        '''
        Distance function between two fingerprints.
        '''
        return np.linalg.norm(fp1.vector - fp2.vector)

    @staticmethod
    def dD_drm(fp1, fp2):
        '''
        Gradient of distance function:

                      d D(x, x')
                      ----------
                         d xi
        '''

        D = EuclideanDistance.distance(fp1, fp2)

        gradients = fp1.reduce_coord_gradients()

        if D == 0.0:
            grad_shape=np.shape(gradients)
            natoms=grad_shape[0] 
            dims=grad_shape[2] # may be higher than 3 if runnung hyperspatial optimization
            return np.zeros( (natoms, dims) )

        result = 1 / D * np.einsum('i,hil->hl',
                                   fp1.vector - fp2.vector,
                                   gradients,
                                   optimize=True)

        return result



    @staticmethod
    def dD_dc(fp1, fp2):
        '''
        Derivative of distance function w.r.t. cell parameters
        derivative is with respect to fp1
        '''

        D = EuclideanDistance.distance(fp1, fp2)

        if D == 0.0:
            return np.zeros((3, 3))

        # fingerprint strain:
        drho_dc = fp1.reduce_strain()

        result = 1 / D * np.einsum('i,ijk->jk',
                                   fp1.vector - fp2.vector,
                                   drho_dc,
                                   optimize=True)

        return result




class BaseKernelType:
    '''
    Base class for all kernel types with common properties,
    attributes and methods.
    '''

    def __init__(self, weight=1.0, scale=1.0, metric=EuclideanDistance):
        # Currently, all the kernel types take weight and scale as parameters

        self.params = {'scale': scale, 'weight': weight}
        self.metric = metric

    @property
    def scale(self):        
        return self.params['scale']

    @property
    def weight(self):
        return self.params['weight']

    def update(self, params):
        '''
        Update the kernel function hyperparameters.
        '''

        self.params.update(params)
    
    

    def kernel_gradient(self, fp1, fp2):
        '''
        Calculates the derivative of the kernel between
        fp1 and fp2 w.r.t. all coordinates in fp1.

        Chain rule:

                d k(x, x')    dk      d D(x, x')
                ---------- = ----  X  ----------
                   d xi       dD         d xi
        '''
        return self.dk_dD(fp1, fp2) * self.metric.dD_drm(fp1, fp2)

    def common_hessian_terms(self, fp1, fp2):
        '''
        Calculate the hessian terms
        '''
        D = self.metric.distance(fp1, fp2)
        kernel = self.kernel(fp1, fp2)

        dD_dr1 = self.metric.dD_drm(fp1, fp2)
        dD_dr2 = self.metric.dD_drm(fp2, fp1)

        g1 = fp1.reduce_coord_gradients()
        g2 = fp2.reduce_coord_gradients()
        tensorprod_gradients = np.einsum('hil,gim->hglm',
                                         g1, g2, optimize=True)
        
        return kernel, D, dD_dr1, dD_dr2, tensorprod_gradients



    def dkernel_dc(self, fp1, fp2):
        '''
        Derivative of kernel w.r.t. cell parameters.
        '''        
        return (self.dk_dD(fp1, fp2) * self.metric.dD_dc(fp1, fp2))


class SquaredExp(BaseKernelType):
    '''
    Squared Exponential kernel function
    '''

    def kernel(self, fp1, fp2):
        '''
        Kernel function between fingerprints 'fp1' and 'fp2'.
        '''
        
        return (self.weight**2 *
                np.exp(-self.metric.distance(fp1, fp2)**2 / 2 / self.scale**2))

    def dk_dD(self, fp1, fp2):
        '''
        Derivative of kernel function w.r.t. distance function dk / dD
        '''
        k = self.kernel(fp1, fp2)
        D = self.metric.distance(fp1, fp2)

        result = - D / self.scale**2 * k

        return result

    def kernel_hessian(self, fp1, fp2):
        '''
        Kernel hessian w.r.t. atomic coordinates in both 'fp1' and 'fp2'

                    d^2 k(x, x')
                    ------------
                     dx_i dx'_j
        '''

        kernel, D, dD_dr1, dD_dr2, C1 = self.common_hessian_terms(fp1, fp2)

        prefactor = 1 / self.scale**2 * kernel

        C0 = D**2 / self.scale**2 * np.einsum('ki,lj->klij', dD_dr1, dD_dr2,
                                              optimize=True)

        result = prefactor * (C0 + C1)

        return result



    def dkernelgradient_dc(self, fp1, fp2):
        '''
        d nabla_2 k(x1, x2)   sigma**2
        ------------------- = -------- * k * (
                dc              l**2
        cell derivatives of the kernel gradients (for coordinates).
        The derivative for c is for an atom in fp1, whereas
        the gradients are from fp2.
        '''

        # result shape: (natoms, nposdims, ncelldims, ncelldims)
        # that is, normally for an Atoms object (natoms, 3, 3, 3)

        D = self.metric.distance(fp1, fp2)
        kernel = self.kernel(fp1, fp2)

        dD_dc1 = self.metric.dD_dc(fp1, fp2)  # shape: (3, 3)
        dD_dr2 = self.metric.dD_drm(fp2, fp1)  # shape: (natoms, 3)

        C0 = D**2 / self.scale**2 * np.einsum('jk,lm->lmjk', dD_dc1, dD_dr2)

        g1 = fp1.reduce_strain()  # shape: (nbins, 3, 3)
        g2 = fp2.reduce_coord_gradients()  # shape: (natoms, nbins, 3)
        C1 = np.einsum('hjk,lhm->lmjk', g1, g2)

        prefactor = 1 / self.scale**2 * kernel

        result = prefactor * (C0 + C1)

        return result



    def ddr_dkdc(self, fp1, fp2):
        '''
          d   d k(x1, x2)     sigma**2
        ------------------- = -------- * k * (
          dr      dc            l**2
        gradients (for coordinates) of the cell derivatives.
        The gradients is for an atom in fp1, whereas
        the cell derivatives are from fp2.
        '''

        # result shape: (ncelldims, ncelldims, natoms, nposdims)
        # that is, normally for an Atoms object (3, 3, natoms, 3)

        D = self.metric.distance(fp1, fp2)
        kernel = self.kernel(fp1, fp2)

        dD_dr1 = self.metric.dD_drm(fp1, fp2)  # shape: (natoms, 3)
        dD_dc2 = self.metric.dD_dc(fp2, fp1)  # shape: (3, 3)

        C0 = D**2 / self.scale**2 * np.einsum('jk,lm->lmjk', dD_dr1, dD_dc2)

        g1 = fp1.reduce_coord_gradients()   # shape: (natoms, nbins, 3)
        g2 = fp2.reduce_strain()  # shape: (nbins, 3, 3)
        C1 = np.einsum('jhk,hlm->lmjk', g1, g2) 
    
        prefactor = 1 / self.scale**2 * kernel

        result = prefactor * (C0 + C1)

        return result

    
    def d2kdc2(self, fp1, fp2):
        '''
        cell hessian. The innermost derivative is done for fp2,
        the ouermost derivative is done for fp1
        '''
        

        # result shape: (natoms, nposdims, ncelldims, ncelldims)
        # that is, normally for an Atoms object (3, 3, 3, 3)

        D = self.metric.distance(fp1, fp2)
        kernel = self.kernel(fp1, fp2)

        dD_dc1 = self.metric.dD_dc(fp1, fp2)  # shape: (3, 3)
        dD_dc2 = self.metric.dD_dc(fp2, fp1)  # shape: (3, 3)

        C0 = D**2 / self.scale**2 * np.einsum('ki,lj->klij', dD_dc1, dD_dc2)

        g1 = fp1.reduce_strain()  # shape: (nbins, 3, 3)
        g2 = fp2.reduce_strain()  # shape: (nbins, 3, 3)
        C1 = np.einsum('ihl,igm->hglm', g1, g2)


        prefactor = 1 / self.scale**2 * kernel

        result = prefactor * (C0 + C1)

        return result
    



class Matern(BaseKernelType):
    ''' Matern 5/2 kernel function '''

    def kernel(self, x1, x2):
        '''
        Kernel function between fingerprints 'fp1' and 'fp2'.
        '''
        D = self.metric.distance(x1, x2)
        p = np.sqrt(5) / self.scale

        pre = 1 + (p * D) + (p**2 / 3 * D**2)

        exp = np.exp(-p * D)
        return self.weight**2 * pre * exp

    def dk_dD(self, fp1, fp2):
        '''
        Derivative of kernel function w.r.t. distance function dk / dD
        '''
        kernel = self.kernel(fp1, fp2)
        D = self.metric.distance(fp1, fp2)

        p = np.sqrt(5) / self.scale
        first = - p * kernel / self.weight**2
        second = (p + 2 * D / 3 * p**2) * np.exp(- p * D)
        result = first + second

        return result * self.weight**2

    def kernel_hessian(self, fp1, fp2, metric=EuclideanDistance):
        '''
        Kernel hessian w.r.t. atomic coordinates in both 'fp1' and 'fp2'

                    d^2 k(x, x')
                    ------------
                     dx_i dx'_j
        '''
        kernel, D, dD_dr1, dD_dr2, C1 = self.common_hessian_terms(fp1, fp2)
        
        p = np.sqrt(5) / self.scale
        exp = np.exp(-p * D)
        dk_dD = self.dk_dD(fp1, fp2)
        d_dD_dk_dD = (-2 * p * dk_dD +
                      2 / 3 * p**2 * exp +
                      -p**2 * kernel)

        if D == 0:
            one_over_D_times_dk_dD = - 1 / 3 * p**2 * self.weight**2
        else:
            one_over_D_times_dk_dD = 1 / D * dk_dD

        C0 = ((d_dD_dk_dD - one_over_D_times_dk_dD) *
              np.einsum('ki,lj->klij', dD_dr1, dD_dr2))

        result = C0 - one_over_D_times_dk_dD * C1

        return result


class RationalQuad(BaseKernelType):
    '''
    Rational Quadratic kernel function.
    '''

    def __init__(self, alpha=0.5, **kwargs):
        '''
        alpha: float
            A weight factor for the continuum of length scales
        '''
        BaseKernelType.__init__(self)
        self.params.update({'alpha': alpha})

    @property
    def alpha(self):
        return self.params['alpha']

    def kernel(self, fp1, fp2):
        '''
        Kernel function between fingerprints 'fp1' and 'fp2'.
        '''
        d = self.metric.distance(fp1, fp2)
        k = self.weight**2 * (1 + d**2 / 2 / self.alpha /
                              self.scale**2)**(-self.alpha)
        return k

    def dk_dD(self, fp1, fp2):
        '''
        Derivative of kernel function w.r.t. distance function dk / dD
        '''
        D = self.metric.distance(fp1, fp2)

        p = - 2 * self.alpha / (2 * self.alpha * self.scale**2 + D**2)
        result = p * D * self.kernel(fp1, fp2)

        return result

    def kernel_hessian(self, fp1, fp2):
        '''
        Kernel hessian w.r.t. atomic coordinates in both 'fp1' and 'fp2'

                    d^2 k(x, x')
                    ------------
                     dx_i dx'_j
        '''
        kernel, D, dD_dr1, dD_dr2, C1 = self.common_hessian_terms(fp1, fp2)
        
        p = - 2 * self.alpha / (2 * self.alpha * self.scale**2 + D**2)

        C0 = ((1 + self.alpha**-1) * p**2 * D**2 *
              kernel * np.einsum('ki,lj->klij', dD_dr1, dD_dr2))

        result = C0 - p * kernel * C1

        return result

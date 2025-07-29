import numpy as np
from gpatom.gpfp.kerneltypes import EuclideanDistance, SquaredExp

class ICEDistance(EuclideanDistance):

    @staticmethod
    def dD_dfraction(fp1, fp2):
        ''' Gradient of distance function:

                      d D(x, x')
                      ----------
                         d q
        '''
        
        D = EuclideanDistance.distance(fp1, fp2)
        
        frac_gradients=fp1.reduce_frac_gradients()

        if D == 0.0:
            frac_grad_shape=np.shape(frac_gradients)
            natoms=frac_grad_shape[0] 
            n_fractional_elements=frac_grad_shape[2] 
            return np.zeros((natoms, n_fractional_elements))
  
        # difference vector between fingerprints:
        diff = fp1.vector - fp2.vector

        result = 1 / D * np.einsum('i,hil->hl',
                                   diff,
                                   frac_gradients,
                                   optimize=True)

        return result

class ICESquaredExp(SquaredExp):
    
    """
    Squared exponential kernel using the derivative of the fingerprint
    w.r.t the elemental coordinates
    """

    def __init__(self, weight=1.0, scale=1.0):

        SquaredExp.__init__(self, weight=weight, scale=scale)
        self.metric = ICEDistance

    def kernel_gradient_frac(self, fp1, fp2):
        """
        Kernel gradients w.r.t. fractions only
        """
        return self.dk_dD(fp1, fp2) * self.metric.dD_dfraction(fp1, fp2)

    def dkernelgradient_dq(self, fp1, fp2):
        '''
        Fraction derivatives of the kernel gradients (for coordinates).
        The derivative for q is for an atom in fp1, whereas
        the gradients are from fp2.
        '''

        k = self.kernel(fp1, fp2)

        coord_grads = fp2.reduce_coord_gradients()
        
        C0 = np.einsum('hm,i,gin->hgnm',
                       self.kernel_gradient_frac(fp1, fp2),
                       (fp1.vector - fp2.vector),
                       coord_grads,
                       optimize=True)

        C1 = k * np.einsum('him,gin->hgnm',
                           fp1.reduce_frac_gradients(),
                           coord_grads,
                           optimize=True)

        result = 1 / self.scale**2 * (C0 + C1)

        return result

    def ddq_dkdc(self, fp1, fp2):
        '''
        Fraction derivatives of the kernel derivatives for cell parameters.
        The derivative for q is for an atom in fp1, whereas
        the derivatives for cell parameters are from fp2.
        '''
        
        k = self.kernel(fp1, fp2)

        strain = fp2.reduce_strain()
        
        C0 = np.einsum('hm,i,ign->hgnm',
                       self.kernel_gradient_frac(fp1, fp2),
                       (fp1.vector - fp2.vector),
                       strain,
                       optimize=True)

        C1 = k * np.einsum('him,ign->hgnm',
                           fp1.reduce_frac_gradients(),
                           strain,
                           optimize=True)

        result = 1 / self.scale**2 * (C0 + C1)
        
        return result



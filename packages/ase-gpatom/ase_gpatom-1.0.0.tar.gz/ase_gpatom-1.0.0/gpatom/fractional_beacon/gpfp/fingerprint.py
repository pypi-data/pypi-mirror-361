import numpy as np
from gpatom.gpfp.fingerprint import (RadialFP, RadialFPCalculator,
                                     RadialFPGradientCalculator,
                                     RadialAngularFP, AngularFPCalculator,
                                     AngularFPGradientCalculator,
                                     FPFactors)

from gpatom.hyperspatial_beacon.hyperspacebeacon import HSParamsHandler

from gpatom.hyperspatial_beacon.gpfp.fingerprint import (HighDimAtomPairs, 
                                                         HighDimAtomTriples)

from gpatom.fractional_beacon.icebeacon import ICEInfo


class FractionalFingerPrint:
    """
    Fingerprint creator class that is specifically used in fractional-BEACON.
    Creates fingerprints of type FractionalFP or FractionalRadAngFP.
    Can describe atoms with fractional chemical identities.
    Can also hande prediction of atoms with hyperspatial dimensions just
    like HighDimFingerprint.
    
    Examples
    -------- 
    >>> fp=FractionalFingerPrint(fp_args=args_dictionary, calc_strain=True)
    >>> fp.get(atoms, extra_coords=my_extra_coords, fractions=my_fractions)
    """
        
    
    def __init__(self, fp_args={}, 
                 angular=True,
                 calc_coord_gradients=True,
                 calc_strain=False):
        '''
        See gpatom.gpfp.fp FingerPrint for documentation
        
        Notice calc_gradients in standard fp is here called 
        calc_coord_gradients
        '''
        
        
        self.fp_args=fp_args
        self.calc_coord_gradients=calc_coord_gradients
        self.calc_strain=calc_strain
        
        if angular:
            self.fp_class=FractionalRadAngFP
        else:
            self.fp_class=FractionalFP
    
    def get(self, atoms, extra_coords=None, fractions=None): 
        
        """
        Turn atoms into fingerprint

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want a fingerprint

        extra_coords : numpy array, optional
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If None the fingerprint act exactly like the normal three 
            dimensional fingerprint.
            Default is None.
            
        fractions: numpy array, optional
            A natoms x nelements numpy array describing the elemental
            fractions of each atoms for each element. 
            If None, all atoms will be the element they naturally are
            in the atoms object and the fingerprint will behave exactly
            like the non-fractional fingerprint
            Default is None.

        Returns
        -------
        fp : FractionalFP or FractionalRadAngFP
            The fingerprint of the inputed atoms.
            type depends on agular=False/True
        """
                
        fp = self.fp_class(atoms=atoms, 
                           extra_coords=extra_coords,
                           fractions=fractions,
                           calc_coord_gradients=self.calc_coord_gradients,
                           calc_strain=self.calc_strain,
                           **self.fp_args)
 
        return fp
    
    
class FractionalFP(RadialFP):

    '''
    Fractional Radial fingerprint class
    
    Examples
    -------
    fp=FractionalFp(atoms, extra_coords=my_extra_coords, 
                    fractions=my_fractions)
    '''

    def __init__(self, atoms=None,
                 extra_coords=None, 
                 fractions=None,
                 calc_coord_gradients=True,
                 calc_strain=False,
                 **kwargs):
        """
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want a fingerprint

        extra_coords : numpy array, optional
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If None the fingerprint act exactly like the normal three 
            dimensional fingerprint.
            Default is None.
            
        fractions: numpy array, optional
            A natoms x nelements numpy array describing the elemental
            fractions of each atoms for each element. 
            If None, all atoms will be the element they naturally are
            in the atoms object and the fingerprint will behave exactly
            like the non-fractional fingerprint
            Default is None.
            
        See RadialFP for remaining parameters
        
        Notice calc_gradients in RadialFP is here called 
        calc_coord_gradients
        """
        
        self.check_cell(atoms)
        self.atoms = atoms.copy()
        self.atoms.wrap()
        

        default_parameters = {'r_cutoff': 8.0,
                              'r_delta': 0.4,
                              'r_nbins': 200}
        
        self.params = default_parameters.copy()        
        self.params.update(kwargs)
        
        fpparams = dict(cutoff=self.params['r_cutoff'],
                        width=self.params['r_delta'],
                        nbins=self.params['r_nbins'])


        # we store dims and extra_coords as well as fractions below, 
        # as they are important for usage in prior method
        self.dims = HSParamsHandler.get_dimension_from_exra_coords(extra_coords)
        self.extra_coords=extra_coords

        self.pairs = HighDimAtomPairs(self.atoms,
                                      extra_coords,
                                      self.params['r_cutoff'])


        self.elements=ICEInfo.get_sorted_elements(atoms)
        self.output_columns=len(self.elements)


        if fractions is None:
            fractions = FPFactors.get_element_vectors(atoms, 
                                                      self.elements)

        self.fractions=fractions

        self.ei = [list(self.elements).index(e) for e in self.elements]
        
        factors = FPFactors.get_factors_for_pairs(self.pairs,
                                                  self.fractions)  

        
        (gaussians,
         fingerprint_ij)=RadialFPCalculator.get_gaussians(self.pairs, 
                                                          **fpparams)
        
        grads_ij=RadialFPGradientCalculator.get_grad_terms(gaussians,
                                                           self.pairs,
                                                           **fpparams)        
                
        self.rho_R = RadialFPCalculator.get_fp(fingerprint_ij, 
                                               factors, self.pairs,
                                               self.params['r_nbins'])
        
        self.vector = self.rho_R.flatten()

        self.gradients = (RadialFPGradientCalculator.
                          get_gradients(grads_ij, factors, self.natoms, 
                                       self.pairs, self.params['r_nbins'],
                                       dimensions=self.dims)
                          if calc_coord_gradients else None)

        self.strain = (RadialFPGradientCalculator.
                       get_strain(grads_ij, factors, self.pairs, 
                                  self.params['r_nbins'])[:,:,:3,:3]
                       if calc_strain else None)   
        
        self.frac_gradients=(RadialFPFractionGradients.
                             get_frac_grads(self.natoms,
                                            fingerprint_ij,
                                            self.pairs,
                                            self.fractions,
                                            self.ei,
                                            self.params['r_nbins']))

    def reduce_coord_gradients(self):
        '''
        Reshape gradients by flattening the element-to-element
        contributions. self.dims is the total amount of spatial dimensions
        '''
        return self.gradients.reshape(self.natoms, -1, self.dims) 


    def reduce_frac_gradients(self):
        '''        
        Reshape fraction gradients by flattening the element-to-element
        contributions. self.output_columns is the total amount of
        spatial dimensions and elements
        '''
        return self.frac_gradients.reshape(self.natoms, -1, self.output_columns)




class FractionalRadAngFP(FractionalFP, RadialAngularFP):
    
    """
    Fractional radial and angular fingerprint class 
    
    Examples
    -------
    fp=FractionalRadlAngFp(atoms, extra_coords=my_extra_coords, 
                           fractions=my_fractions)
    """

    def __init__(self, atoms=None, 
                 extra_coords=None, 
                 fractions=None,
                 calc_coord_gradients=True,
                 calc_strain=False,
                 **kwargs):
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want a fingerprint

        extra_coords : numpy array, optional
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If None the fingerprint act exactly like the normal three 
            dimensional fingerprint.
            Default is None.
            
        fractions: numpy array, optional
            A natoms x nelements numpy array describing the elemental
            fractions of each atoms for each element. 
            If None, all atoms will be the element they naturally are
            in the atoms object and the fingerprint will behave exactly
            like the non-fractional fingerprint
            Default is None.
            
        See RadialAngularFP for remaining parameters
        
        Notice calc_gradients in RadialAngularFP is here called 
        calc_coord_gradients
        """

        FractionalFP.__init__(self, atoms, 
                              extra_coords=extra_coords,
                              fractions=fractions,
                              calc_coord_gradients=calc_coord_gradients,
                              calc_strain=calc_strain,
                              **kwargs)

        default_parameters = {'r_cutoff': 8.0,
                              'r_delta': 0.4,
                              'r_nbins': 200,
                              'a_cutoff': 4.0,
                              'a_delta': 0.4,
                              'a_nbins': 100,
                              'gamma': 0.5,
                              'aweight': 1.0}

        self.params = default_parameters.copy()
        self.params.update(kwargs)

        fpparams=dict(width=self.params['a_delta'],
                      nbins=self.params['a_nbins'],
                      aweight=self.params['aweight'],
                      cutoff=self.params['a_cutoff'],
                      gamma=self.params['gamma'])

        assert self.params['r_cutoff'] >= self.params['a_cutoff']

        self.extra_coords=extra_coords

        self.triples = HighDimAtomTriples(self.atoms,          
                                          extra_coords,
                                          cutoff=self.params['a_cutoff'])

        factors= FPFactors.get_factors_for_triples(self.triples, 
                                                   self.fractions)
        

        (angle_gaussians,
         fingerprint_ijk)=AngularFPCalculator.get_angle_gaussians(self.triples,
                                                                  **fpparams)
                
        (grads_ij, 
         grads_ik, 
         grads_jk) = AngularFPGradientCalculator.get_grad_terms(angle_gaussians,
                                                                self.triples,
                                                                **fpparams)

        self.rho_a = AngularFPCalculator.get_fp(fingerprint_ijk, 
                                                factors, self.triples, 
                                                self.params['a_nbins'])
        
        self.vector = np.concatenate((self.rho_R.flatten(),
                                      self.rho_a.flatten()), axis=None)


        self.anglegradients = (AngularFPGradientCalculator.
                               get_gradients(grads_ij, grads_ik, grads_jk, 
                                             factors, self.natoms, self.triples,
                                             self.params['a_nbins'],
                                             dimensions=self.dims)
                               if calc_coord_gradients else None)

        
        self.anglestrain = (AngularFPGradientCalculator.
                            get_strain(grads_ij, grads_ik, grads_jk, 
                                       factors, self.triples, 
                                       self.params['a_nbins'])[:,:,:3,:3]
                            if calc_strain else None)
        
        
        self.frac_gradients_angles=(AngularFPFractionGradients.
                                    get_frac_grads(self.natoms,
                                                   fingerprint_ijk,
                                                   self.triples,
                                                   self.fractions,
                                                   self.ei,
                                                   self.params['a_nbins']))    
        
    def reduce_coord_gradients(self):
        '''
        Reshape gradients by flattening the element-to-element
        contributions. self.dims is the total amount of spatial dimensions
        '''
        return np.concatenate((self.gradients.reshape(self.natoms, -1, self.dims),
                               self.anglegradients.reshape(self.natoms, -1, self.dims)),
                              axis=1)


    def reduce_frac_gradients(self):
        '''        
        Reshape fraction gradients by flattening the element-to-element
        contributions. self.output_columns is the total amount of
        spatial dimensions and elements
        '''
        return np.concatenate((self.frac_gradients.reshape(self.natoms, -1, self.output_columns),
                               self.frac_gradients_angles.reshape(self.natoms, -1, self.output_columns)),
                              axis=1)
        


class RadialFPFractionGradients(RadialFPCalculator):
    """
    Class to calculate the derivatives of the fringerprint
    w.r.t the elemental fractions for the radial fingerprint
    """

    @classmethod
    def get_frac_grads(cls, natoms, fingerprint_ij, 
                       pairs, fractions, ei, nbins):
        """
        Calculates the gradients of the fingerprint w.r.t elemental fractions
        over all atomic pairs
        """
        
        nfelements=len(ei)

        f_gradients = np.zeros([natoms, pairs.nelem, pairs.nelem,
                                nbins, nfelements])
           
        if pairs.empty:
            ncombis=cls.get_ncombis(pairs.nelem)
            return np.zeros([natoms, ncombis, nbins, nfelements])

        factors = cls.get_factor_product_gradients_for_pairs(natoms,  
                                                             pairs,
                                                             fractions)

        all_i=pairs.indices[:,0]
        all_j=pairs.indices[:,1]
        
        f_gradients_i = np.zeros((natoms, nfelements, nbins))
        f_gradients_j = np.zeros((natoms, nfelements, nbins))
        for a in range(natoms):
            
            i_mask=(all_i==a)
            j_mask=(all_j==a)
        
            f_gradients_i[a]=np.einsum('ij,il->jl',
                                       factors[i_mask,0],
                                       fingerprint_ij[i_mask],                              
                                       optimize=False)
            
            f_gradients_j[a]=np.einsum('ij,il->jl',
                                       factors[j_mask,1],
                                       fingerprint_ij[j_mask],                              
                                       optimize=False)

        f_gradients[:, ei, :, :,ei] += f_gradients_i
        f_gradients[:, :, ei, :,ei] += f_gradients_j
        
        f_gradients+=np.transpose(f_gradients, axes=(0, 2, 1, 3, 4))
        
        diagonal_mask = np.eye(pairs.nelem, dtype=bool)
        f_gradients[:, diagonal_mask,:,:]/=2            
        triu_indices = np.triu_indices(pairs.nelem)
        f_gradients=f_gradients[:,triu_indices[0], triu_indices[1],:,:]
        
        return f_gradients

    @staticmethod
    def get_factor_product_gradients_for_pairs(natoms, pairs, fractions):
        """
        Calculates the products of elemental fractions for the atomic pairs
        for the gradient calculation
        """

        factors = np.zeros((len(pairs.indices), 2, pairs.nelem))

        q = fractions
        
        i = pairs.indices[:, 0]
        j = pairs.indices[:, 1]

        factors[:, 0, :] =  q[j,:]
        factors[:, 1, :] =  q[i,:]

        return factors



class AngularFPFractionGradients(AngularFPCalculator):
    
    """
    Class to calculate the derivatives of the fringerprint
    w.r.t the elemental fractions for the angular fingerprint
    """

    @classmethod
    def get_frac_grads(cls, natoms, fingerprint_ijk, triples, 
                       fractions, ei, nbins):
        """
        Calculates the gradients of the fingerprint w.r.t elemental fractions
        over all atomic triples
        """
        
        nfelements=len(ei)

        f_gradients = np.zeros([natoms,                 
                                triples.nelem,
                                triples.nelem,
                                triples.nelem,
                                nbins,
                                nfelements])

        if triples.empty:
            ncombis=cls.get_ncombis(triples.nelem)
            return np.zeros([natoms, ncombis, nbins, nfelements])

        factors = cls.get_factor_product_gradients_for_triples(natoms,  
                                                               triples,
                                                               fractions)

        all_i=triples.indices[:,0]
        all_j=triples.indices[:,1]
        all_k=triples.indices[:,2]
                
        f_gradients_i = np.zeros((natoms, nfelements, nfelements, nbins))
        f_gradients_j = np.zeros((natoms, nfelements, nfelements, nbins))
        f_gradients_k = np.zeros((natoms, nfelements, nfelements, nbins))
        for a in range(natoms):
            
            i_mask=(all_i==a)
            j_mask=(all_j==a)
            k_mask=(all_k==a)
        
            f_gradients_i[a]=np.einsum('ijk,il->jkl',
                                       factors[i_mask,0],
                                       fingerprint_ijk[i_mask],
                                       optimize=False)

            f_gradients_j[a]=np.einsum('ijk,il->jkl',
                                       factors[j_mask,1],   
                                       fingerprint_ijk[j_mask],
                                       optimize=False)
            
            f_gradients_k[a]=np.einsum('ijk,il->jkl',
                                       factors[k_mask,2],
                                       fingerprint_ijk[k_mask],
                                       optimize=False)

        f_gradients[:, ei, :, :,:,ei] += f_gradients_i
        f_gradients[:, :, ei, :,:,ei] += f_gradients_j
        f_gradients[:, :, :, ei,:,ei] += f_gradients_k
        
        f_gradients+=np.transpose(f_gradients, axes=(0, 1, 3, 2, 4, 5))
        
        diagonal_mask = np.eye(triples.nelem, dtype=bool)
        f_gradients[:,:, diagonal_mask,:,:]/=2
        triu_indices = np.triu_indices(triples.nelem)
        f_gradients=f_gradients[:, :,triu_indices[0], triu_indices[1],:,:]
                
        return f_gradients
        

    @staticmethod
    def get_factor_product_gradients_for_triples(natoms, triples, fractions):
        """
        Calculates the products of elemental fractions for the atomic triples
        for the gradient calculation
        """
        
        factors = np.zeros((len(triples.indices), 3,
                            triples.nelem, triples.nelem))
        
        q = fractions
        
        i = triples.indices[:, 0]
        j = triples.indices[:, 1]
        k = triples.indices[:, 2]

        factors[:, 0, :, :] = np.einsum('pa,pb->pab', q[j,:] , q[k,:],optimize=False)
        factors[:, 1, :, :] = np.einsum('pa,pb->pab', q[i,:] , q[k,:],optimize=False)
        factors[:, 2, :, :] = np.einsum('pa,pb->pab', q[i,:] , q[j,:],optimize=False)

        return factors

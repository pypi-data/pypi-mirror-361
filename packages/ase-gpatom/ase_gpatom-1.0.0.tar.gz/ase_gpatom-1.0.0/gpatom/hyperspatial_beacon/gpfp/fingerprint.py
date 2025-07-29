import numpy as np
import itertools
from ase.neighborlist import NeighborList
from gpatom.gpfp.fingerprint import (RadialFP, RadialFPCalculator,
                                     RadialFPGradientCalculator,
                                     AngularFPGradientCalculator,
                                     RadialAngularFP, AngularFPCalculator,
                                     AtomPairs, AtomTriples, FPFactors)

from gpatom.hyperspatial_beacon.hyperspacebeacon import HSParamsHandler


class HighDimFingerPrint:
    
    """
    Dingerprint creator class that is specifically used in hyperwspace-BEACON.
    Creates fingerprints of type HighDimRadialFP or HighDimRadialAngularFP.
    Can describe atoms in any amount of spatial dimensions
    
    
    Examples
    ---------
    fp=HighDimFingerPrint(fp_args=args_dictionary, calc_strain=True)
    new_fingerprint=fp.get(my_atoms, extra_coords=my_extra_coords)
    """
    

    
    def __init__(self, fp_args={}, angular=True, 
                 calc_gradients=True, calc_strain=False):
        '''
        See gpatom.gpfp.fp FingerPrint for documentation
        '''

        self.fp_args=fp_args
        self.calc_gradients=calc_gradients
        self.calc_strain=calc_strain
        
        if angular:
            self.fp_class=HighDimRadialAngularFP
        else:
            self.fp_class=HighDimRadialFP
        
    def get(self, atoms, extra_coords=None):
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
            
            

        Returns
        -------
        fp : HighDimRadialFP or HighDimRadialAngularFP
            The fingerprint of the inputed atoms.
            type depends on agular=False/True
        """
        
        return self.fp_class(atoms, extra_coords,
                             calc_gradients=self.calc_gradients,
                             calc_strain=self.calc_strain,
                             **self.fp_args)
        
        
class HighDimRadialFP(RadialFP):
    
    '''
    Hyperspatial Radial fingerprint class
    
    Examples
    -------
    fp=HighDimRadalFp(atoms, extra_coords=my_extra_coords)
    '''
    
    def __init__(self, atoms, extra_coords=None, calc_gradients=True, 
                 calc_strain=False, **kwargs):
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
            
        See RadialFP for remaining parameters
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


        # Store total number of dimensions and extra coordinates 
        # Important for functionality with prior
        self.dims = HSParamsHandler.get_dimension_from_exra_coords(extra_coords)
        self.extra_coords=extra_coords

        self.pairs = HighDimAtomPairs(self.atoms,
                                      extra_coords,
                                      self.params['r_cutoff'])
        
        self.elements=sorted(atoms.symbols.species())
        self.element_vectors = FPFactors.get_element_vectors(self.atoms, 
                                                             self.elements)
        groups = FPFactors.get_factors_for_pairs(self.pairs,
                                                 self.element_vectors)

        (gaussians,
         fingerprint_ij)=RadialFPCalculator.get_gaussians(self.pairs, 
                                                          **fpparams)
        
        grads_ij=RadialFPGradientCalculator.get_grad_terms(gaussians,
                                                           self.pairs,
                                                           **fpparams)        
                
        self.rho_R = RadialFPCalculator.get_fp(fingerprint_ij, 
                                               groups, self.pairs,
                                               self.params['r_nbins'])
        
        self.vector = self.rho_R.flatten()

        self.gradients = (RadialFPGradientCalculator.
                          get_gradients(grads_ij, groups,  self.natoms, 
                                       self.pairs, self.params['r_nbins'],
                                       dimensions=self.dims)
                          if calc_gradients else None)

        self.strain = (RadialFPGradientCalculator.
                       get_strain(grads_ij, groups, self.pairs, 
                                  self.params['r_nbins'])[:,:,:3,:3]
                       if calc_strain else None)

        
    def reduce_coord_gradients(self):
        '''
        Reshape gradients by flattening the element-to-element
        contributions. self.dims is the total number of spatial dimensions
        '''
        return self.gradients.reshape(self.natoms, -1, self.dims) 
    
    
    
    
    
    
class HighDimRadialAngularFP(HighDimRadialFP, RadialAngularFP):
    
    """
    Hyperspatial radial and angular fingerprint class 
    
    Examples
    -------
    fp=HighDimRadalAngularFp(atoms, extra_coords=my_extra_coords)
    """
    
    def __init__(self, atoms, extra_coords=None, calc_gradients=True, 
                 calc_strain=False, **kwargs):
        """
        Parameters
        ----------
        atoms : ase.Atoms
            atoms for which we want a fingerprint

        extra_coords : numpy array, optional
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If None the fingerprint act exactly like the normal three 
            dimensional fingerprint.
            Default is None.
            
        See RadialAngularFP for remaining parameters
        """
        
        HighDimRadialFP.__init__(self, atoms, extra_coords=extra_coords, 
                                 calc_gradients=calc_gradients, 
                                 calc_strain=calc_strain, **kwargs)

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


        groups = FPFactors.get_factors_for_triples(self.triples,
                                                   self.element_vectors)
                                               
        (angle_gaussians,
         fingerprint_ijk)=AngularFPCalculator.get_angle_gaussians(self.triples,
                                                                  **fpparams)
                
        (grads_ij, 
         grads_ik, 
         grads_jk) = AngularFPGradientCalculator.get_grad_terms(angle_gaussians,
                                                                self.triples,
                                                                **fpparams)

        self.rho_a = AngularFPCalculator.get_fp(fingerprint_ijk, 
                                                groups, self.triples, 
                                                self.params['a_nbins'])
        
        self.vector = np.concatenate((self.rho_R.flatten(),
                                      self.rho_a.flatten()), axis=None)


        self.anglegradients = (AngularFPGradientCalculator.
                               get_gradients(grads_ij, grads_ik, grads_jk, 
                                             groups, self.natoms, self.triples,
                                             self.params['a_nbins'],
                                             dimensions=self.dims)
                               if calc_gradients else None)

        
        self.anglestrain = (AngularFPGradientCalculator.
                            get_strain(grads_ij, grads_ik, grads_jk, 
                                       groups, self.triples, 
                                       self.params['a_nbins'])[:,:,:3,:3]
                            if calc_strain else None)


        
    def reduce_coord_gradients(self):
        '''
        Reshape gradients by flattening the element-to-element
        contributions and all angles, and concatenate those arrays.
        elf.dims is the total number of spatial dimensions
        '''
        
        return np.concatenate((self.gradients.reshape(self.natoms, -1, self.dims),
                               self.anglegradients.reshape(self.natoms, -1, self.dims)),
                              axis=1)
    


class HighDimAtomPairs(AtomPairs):
    
    """
    Class to generate atoms pairs for the radial fingerprint in any amount
    of spatial dimensions. If number of dimensions is 3, the behavior 
    is identical to the standard BEACON AtomPairs
    """

    def __init__(self, atoms, extra_coords, cutoff):
        """
        parameters
        ----------
        atoms: ase.Atoms
            
        extra_coords : numpy array
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If extra_coords is None the class acts identically to standard 
            BEACON AtomPairs
          
         cutoff: float
             the radial cutoff radius. 
             must be supplied
             
        Returns
        -------
        None.
        """
        neighbor_list = NeighborList([cutoff/2]*len(atoms), 
                                     skin=0,
                                     self_interaction=False,
                                     bothways=False)
        neighbor_list.update(atoms)
        
        pairs=[]
        vectors=[]
        for atom_index in range(len(atoms)):
            neighbors, d = AtomPairs.get_distance_info(atoms, atom_index, neighbor_list)
            
            if extra_coords is not None:
                d_ext=extra_coords[neighbors]-extra_coords[atom_index]
                d=np.hstack((d,d_ext))
                dists=np.linalg.norm(d, axis=1)
                mask=(dists<cutoff)   
                neighbors=neighbors[mask]
                d=d[mask]
            
            for neighbor_index, vector in zip(neighbors, d):
                pairs.append([atom_index, neighbor_index])
                vectors.append(vector)

        self.nelem=len(atoms.symbols.species())
        self.get_pair_info(atoms, pairs, vectors)
    
    

class HighDimAtomTriples(AtomTriples):
    
    """
    Class to generate atoms triples for the angular fingerprint in any amount
    of spatial dimensions. If number of dimensions is 3, the behavior 
    is identical to the standard BEACON AtomTriples
    """

    def __init__(self, atoms, extra_coords, cutoff):
        
        """        
        Parameters
        ----------
        atoms : ase.Atoms
            Atomic object for which we want to find triples
            
        extra_coords : numpy array
            A natoms x (ndimensions-3) numpy array describing the 
            hyperspatial coordinates not included in the the atoms object.
            If extra_coords is None the class acts identically to standard 
            BEACON AtomTriples
            
        cutoff : float
            Angular cutoff radius

        Returns
        -------
        None.
        """
        
        neighbor_list = NeighborList([cutoff/2]*len(atoms), 
                                     skin=0,
                                     self_interaction=False,
                                     bothways=True)   
        neighbor_list.update(atoms)
        
        triplets=[]
        vectors_ij=[]
        vectors_ik=[]
    
        for atom_index in range(len(atoms)):
            neighbors, d = AtomPairs.get_distance_info(atoms, atom_index, neighbor_list)
            
            if extra_coords is not None:
                d_ext=extra_coords[neighbors]-extra_coords[atom_index]
                d=np.hstack((d,d_ext))
                dists=np.linalg.norm(d, axis=1)
                mask=(dists<cutoff)   
                neighbors=neighbors[mask]
                d=d[mask]
                        
            neighbor_distance_pairs = list(zip(neighbors, d))
            for (neighbor_1, d1), (neighbor_2, d2) in itertools.combinations(neighbor_distance_pairs, 2):

                triplets.append([atom_index, neighbor_1, neighbor_2])   
                vectors_ij.append(d1)
                vectors_ik.append(d2)
                                
        self.nelem=len(atoms.symbols.species())
        self.get_triple_info(atoms, triplets, vectors_ij, vectors_ik)
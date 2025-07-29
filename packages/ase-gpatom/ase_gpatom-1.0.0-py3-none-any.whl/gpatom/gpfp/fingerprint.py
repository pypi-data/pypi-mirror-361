from math import pi
import itertools
from ase.neighborlist import NeighborList
import numpy as np

class FingerPrint:
    """
    Fingerprint creator class to generate fingerprint objects of class
    RadialFP or RadialAngularFP
    
    Examples
    ---------
    >>> fp=FingerPrint(fp_args=args_dictionary, calc_strain=True)
    >>> new_fingerprint=fp.get(atoms)
    """

    
    def __init__(self, angular=True, fp_args=None ,
                 calc_gradients=True, calc_strain=False):
    
        """
        parameters
        ----------
            Angular: bool, optional
            If the angular part of the fingerrint should be calulated or 
            only the radial part
            default is True
    
        fp_args: dictionary of arguments: optional
            The possible arguments are:
            'r_cutoff':    Radial cutoff radii                     default: 8.0,  
            'r_delta':     Width of Radial Gaussian broadening     default: 0.4,
            'r_nbins':     Number of bins in radial fingerprint    default: 200,
            'a_cutoff':    Angular cutoff radius                   default: 4.0,
            'a_delta':     Width of Angular Gaussian broadening    default: 0.4,
            'a_nbins':     Number of bins in angular fingerprint   default: 100,
            'gamma':       Cutoff function constant                default: 0.5,
            'aweight':     Angular weight constant                 default: 1.0
    
        calc_gradients: bool, optional
            If the coordinate gradients should be calculated.
            Default is True
        
        calc_strain: bool, optional
            If strain should be calculated. Necessary for unit cell 
            optimzation, but a bit costly
            default is False
        """
        
        
        if fp_args is None:
            fp_args={}
        
        self.fp_args=fp_args
        self.calc_gradients=calc_gradients
        self.calc_strain=calc_strain

        
        if angular:
            self.fp_class=RadialAngularFP
        else:
            self.fp_class=RadialFP
        
    def get(self, atoms):
        """
        Turn atoms into fingerprint

        Parameters
        ----------
        atoms : ase.Atoms
            atoms for which we want a fingerprint

        Returns
        -------
        fp : RadialFP or RadialAngularFP object 
            The fingerprint of the inputed atoms.
            type depends on agular=False/True
        """
            
        fp = self.fp_class(atoms, 
                           calc_gradients=self.calc_gradients,
                           calc_strain=self.calc_strain,
                           **self.fp_args)
                        
        return fp
        

class FPUpdater:
    """
    Class for updating angular weight constant of fingerprint
    
    Examples
    -------- 
    >>> fpupdater=FPUpdater(factor=1)
    >>> fpupdater.update(dingerprint_list, 
                         fingerprint_creator_class)
    
    """
    
    def __init__(self, factor=0.5):
        """
        parameters
        ----------
        factor: float, optional
            Relative median fp difference peak height of angular part of
            fingerprint compared to the radial part.
            Default is 0.5
        """
        
        self.factor=factor
    
    def get_fp_difs(self, x1,x2):
        dif_rho_R=np.abs(x1.rho_R.flatten()-x2.rho_R.flatten())
        dif_rho_a=np.abs(x1.rho_a.flatten()-x2.rho_a.flatten())
        
        max_difs=[max(dif_rho_R), max(dif_rho_a)]
        
        return max_difs 

    
    def get_averaged_fp_difs(self, X):
            
        difs=[]
        
        n=len(X)
        
        for i in range(n):
            for j in range(i + 1, n):
                difs.append(self.get_fp_difs(X[i],X[j]))
                
        difs=np.array(difs)
            
        median_R=np.median(difs[:,0])
        
        median_a=np.median(difs[:,1])
        
        return median_R, median_a


    def get_aweight(self, X, old_aweight):
        
        median_R, median_a = self.get_averaged_fp_difs(X)
        
        aweight=old_aweight*(median_R/median_a) *self.factor
        
        return aweight        

    def update(self, X, fp):
        """
        sets aweight parameter in FingerPrint class

        Parameters
        ----------
        X : list
            List of all fingerprints in database
    
        fp : FingerPrint
            Fingerprint creator class
    
        Returns
        -------
        None.
        """
        
        old_aweight=fp.fp_args['aweight']  
    
        aweight=self.get_aweight(X, old_aweight)
        
        fp.fp_args['aweight']=aweight
            
            

class RadialFP:
    """
    Radial fingerprint object class. 
    
    Examples
    -------
    fp=RadalFp(atoms)
    """
    
    

    def __init__(self, atoms, calc_gradients=True, calc_strain=False, 
                 **kwargs):
        """ 
        Parameters
        ----------
        atoms: ase.Atoms
            Atoms object to be turned into fingerprint
            Required

        calc_gradients: bool, optional
            Whether coordinate gradients are calculated.
            Default is True
            
        calc_strain: bool, optional
            Weather strain is calculated.
            Default is False
            
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
            
                r_cutoff: float, optional
                    Cutoff radius for radial fingerprint (Angstroms)

                r_delta: float, optional
                    Width of Gaussian broadening in radial fingerprint
                    (Angstroms)

                r_nbins: int, optional
                    Number of bins in radial fingerprint
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
        

        self.pairs = AtomPairs(self.atoms, self.params['r_cutoff'])

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
                                       self.pairs, self.params['r_nbins'])
                          if calc_gradients else None)

        self.strain = (RadialFPGradientCalculator.
                       get_strain(grads_ij, groups, self.pairs, 
                                  self.params['r_nbins'])
                       if calc_strain else None)

    @property
    def natoms(self):
        return len(self.atoms)

    def reduce_coord_gradients(self):
        """
        Reshape gradients by flattening the element-to-element
        contributions.
        """
        return self.gradients.reshape(self.natoms, -1, 3)

    def reduce_strain(self):
        """
        Reshape strain by flattening the element-to-element
        contributions.
        """
        return self.strain.reshape(-1, 3, 3)

    def get_vector(self):
        return self.vector.copy()
    
    def check_cell(self, atoms):
        if atoms.cell.rank != 3:
            raise ValueError('Atoms object has to have a 3D unit cell.')
            
            
class RadialAngularFP(RadialFP):
    """
    Combined radial and angular fingerprint object class. 
    
    Examples
    -------
    fp=RadalAngularFp(atoms)
    """

    def __init__(self, atoms, calc_gradients=True, calc_strain=False, 
                 **kwargs):
        """ 
        Parameters
        ----------
        atoms: ase.Atoms
            Atoms object to be turned into fingerprint
            Required

        calc_gradients: bool, optional
            Whether coordinate gradients are calculated.
            Default is True
            
        calc_strain: bool, optional
            Weather strain is calculated.
            Default is False
            
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
                
                Same as RadialFP
            
                r_cutoff: float, optional
                    Cutoff radius for angular fingerprint (Angstroms)

                a_delta: float
                    Width of Gaussian broadening in angular fingerprint
                    (Radians)

                a_nbins: int
                    Number of bins in angular fingerprint
                    
                aweight: float
                    Scaling factor for the angular fingerprint; the angular
                    fingerprint is multiplied by this number
        """
    
        
        RadialFP.__init__(self, atoms, calc_gradients=calc_gradients,
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

        self.triples = AtomTriples(self.atoms,                                         
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
                                             self.params['a_nbins'])
                               if calc_gradients else None)

        
        self.anglestrain = (AngularFPGradientCalculator.
                            get_strain(grads_ij, grads_ik, grads_jk, groups, 
                                      self.triples, self.params['a_nbins'])
                            if calc_strain else None)
       
       

    def reduce_coord_gradients(self):
        """
        Reshape gradients by flattening the element-to-element
        contributions and all angles, and concatenate those arrays.
        """
        
        return np.concatenate((self.gradients.reshape(self.natoms, -1, 3),
                               self.anglegradients.reshape(self.natoms, -1, 3)),
                              axis=1)


    def reduce_strain(self):
        """
        Reshape strain by flattening the element-to-element
        contributions and all angles, and concatenate those arrays.
        """
        
        return np.concatenate((self.strain.reshape(-1, 3, 3),
                               self.anglestrain.reshape(-1, 3, 3)),
                              axis=0)
    

class RadialFPCalculator:
    """
    Class to calculate the fingerprint vector
    """

    @staticmethod
    def constant(cutoff, nbins):
        return 1 / (cutoff / nbins)

    @staticmethod
    def get_rvec(cutoff, nbins, startpad=-1.0, endpad=2.0):
        """
        Variable array

        Parameters:
        cutoff: float (Angstroms)
        nbins: int
        startpad: float (Angstroms)
            Extension of the fingerprint vector below zero
        endpad: float (Angstroms)
            Extension of the fingerprint vector above cutoff
        """
        return np.linspace(startpad, cutoff + endpad, nbins)

    @classmethod
    def get_diffvec(self, pairs, cutoff, nbins):
        """ Distances on variable array """
        return self.get_rvec(cutoff, nbins) - pairs.dm[:, np.newaxis]

    @classmethod
    def get_peak_heights(self, pairs, cutoff, nbins):
        """
        Peak heights for each Gaussian in the fingerprint.
        Contains 1/r**2 term and the cutoff function.
        """
        if pairs.empty:
            return []

        peak_heights=(1/pairs.dm**2) + (2/cutoff**3*pairs.dm) - (3/cutoff**2)
        
        peak_heights*=self.constant(cutoff, nbins)

        return peak_heights

    @classmethod
    def get_gaussians(self, pairs, width, cutoff, nbins):
        """
        Gaussian for at each r_ij (distance between atoms)
        """
        
        if pairs.empty:
            return None, None
        
        diffvec=self.get_diffvec(pairs, cutoff, nbins)
        
        exponents=diffvec**2 / (2 * width**2)
        
        gaussians=np.exp(-exponents)
        
        peak_heights=self.get_peak_heights(pairs, cutoff, nbins)

        fingerprint_ij=gaussians*peak_heights[:, np.newaxis]

        return gaussians, fingerprint_ij

    @classmethod
    def get_fp(self, mod_gaussians, groups, pairs, nbins):
        """
        Calculate the Gaussian-broadened fingerprint.
        """

        if pairs.empty:
            ncombis=self.get_ncombis(pairs.nelem)
            return np.zeros([ncombis, nbins])

        # Sum Gaussians to correct element-to-element pairs:
        rho_R = np.einsum('ij,ik->jk', groups, mod_gaussians, optimize=True)

        return rho_R

    @classmethod
    def get_ncombis(cls, nelem):
        """
        Get number of element pair combinations
        """
        return int(nelem*(nelem+1)/2)


class RadialFPGradientCalculator(RadialFPCalculator):
    """
    Class to calculate the derivatives of the fingerprint with respect
    to the atomic coordinates and unit cell
    """

    @classmethod
    def get_peak_height_gradients(self, pairs, cutoff, nbins):
        
        peak_heights = (-2/pairs.dm**3) + (2/cutoff**3)
        
        peak_heights*=self.constant(cutoff, nbins)
        
        return peak_heights

    @classmethod
    def get_gradient_gaussians(self, gaussians, pairs, cutoff, nbins, width):
        '''
        Gradients of h * exp() for each atom pair in pairs.indices.
        '''
        
        diffvec=self.get_diffvec(pairs, cutoff, nbins)
        
        peak_heights=self.get_peak_heights(pairs, cutoff, nbins)
        
        gardient_peak_heights=self.get_peak_height_gradients(pairs, cutoff, nbins)
        
        vals=(gardient_peak_heights[:, np.newaxis] + 
              diffvec*peak_heights[:, np.newaxis]/width**2)
        
        gradient_gaussians=gaussians*vals

        return gradient_gaussians
    
    
    @classmethod
    def get_grad_terms(self, gaussians, pairs, cutoff,
                       width, nbins):
        """ get the atomic pair wise contributions to the gradients """
        
        if pairs.empty:
            return None

        gradient_gaussians=self.get_gradient_gaussians(gaussians, pairs, 
                                                       cutoff, nbins, width)
            
        vr_ijs=pairs.rm/pairs.dm[:, np.newaxis]
        
        
        grads_ij = np.einsum('ik,il->ikl',
                             gradient_gaussians,
                             vr_ijs,
                             optimize=True)
        
        return grads_ij
    
    
    @classmethod
    def get_gradients(self, results, groups, natoms, 
                      pairs, nbins, dimensions=3):
        """ Derivative of fingerwrint w.r.t atomic coordinates """


        ncombis=self.get_ncombis(pairs.nelem)
        gradients = np.zeros([natoms, ncombis, nbins, dimensions])

        if pairs.empty:
            return gradients
        
        all_i=pairs.indices[:,0]
        all_j=pairs.indices[:,1]

        for a in range(natoms):
            i_mask=(all_i==a)
            j_mask=(all_j==a)
            
            if np.any(i_mask):                
                gradients[a] -= np.einsum('ij,ikl->jkl',
                                          groups[i_mask],
                                          results[i_mask],
                                          optimize=False)
 
            if np.any(j_mask):
                gradients[a] += np.einsum('ij,ikl->jkl',
                                          groups[j_mask],
                                          results[j_mask],
                                          optimize=False)
        return gradients
    
    
    @classmethod
    def get_strain(cls, results, groups, pairs, nbins):

        """ Derivative of fingerprint w.r.t. cell parameters """

        if pairs.empty:
            ncombis=cls.get_ncombis(pairs.nelem)
            return np.zeros([ncombis, nbins, 3, 3])
                
        results = np.einsum('ikl, im -> iklm', 
                            results, 
                            pairs.rm,
                            optimize=True)
        
        gradients = np.einsum('ij, iklm -> jklm', 
                              groups, results, 
                              optimize=True)

        return gradients

        
    
class AngularFPCalculator:
    """ 
    Class to calculate the angular fingerprint vector
    """
    
    @staticmethod
    def angleconstant(aweight, nbins):
        return aweight / (pi / nbins)

    @staticmethod
    def get_thetavec(nbins, startpad=-1.5, endpad=1.5):
        '''
        Parameters:
        nbins: int
        startpad: float (rads)
            Extension of the fingerprint vector below zero
        endpad: float (rads)
            Extension of the fingerprint vector above cutoff
        '''
        return np.linspace(startpad, pi + endpad, nbins)

    @staticmethod
    def cutoff_function(dist_array, cutoff, gamma):
        '''
        Calculate cutoff function for each distance in the input
        array `dist_array`
        '''

        return np.where(dist_array <= cutoff,
                        (1 + gamma *
                         (dist_array / cutoff)**(gamma + 1) -
                         (gamma + 1) *
                         (dist_array / cutoff)**gamma), 0.0)

    @classmethod
    def get_angle_gaussians(self, triples, width, nbins, aweight, cutoff, gamma):
        ''' get the Angle gaussians '''
        
        if triples.empty:
            return None, None
        
        gaussians= np.exp(- (self.get_thetavec(nbins) -
                                triples.cos_thetas[:, np.newaxis])**2 /
                             2 / width**2)
        
        gaussians*=self.angleconstant(aweight, nbins)
                                                            
        cutoff_ags=self.get_cutoff_ags(triples, cutoff, gamma)
        
        fingerprint_ijk=gaussians*cutoff_ags[:, np.newaxis]
        
        return gaussians, fingerprint_ijk
    
    @classmethod
    def get_cutoff_ags(self, triples, cutoff, gamma):
        '''
        Get product of cutoff functions
        '''
        fcij=self.cutoff_function(triples.adm, cutoff, gamma)
        fcjk=self.cutoff_function(triples.edm, cutoff, gamma)
        
        return fcij*fcjk

    @classmethod
    def get_fp(self, mod_gaussians, groups, triples, nbins):  
        ''' Calculate the angular fingerprint with Gaussian broadening  '''

        if triples.empty:
            ncombis=self.get_ncombis(triples.nelem)
            return np.zeros([ncombis, nbins])

        # Sum Gaussians to correct element-to-element-to-element angles:
        rho_a = np.einsum('ij,ik->jk', groups, mod_gaussians, optimize=True)
        
        return rho_a
    
    @classmethod
    def get_ncombis(cls, nelem):
        """ Number of element triple combiinations """
        return int(nelem**2*(nelem+1)/2)


class AngularFPGradientCalculator(AngularFPCalculator):
    """ 
    Calculate derivatives of the angular fingerprint wit respect to 
    atomic coordinates and unit cell parameters
    """
    
    @classmethod
    def d_cutofffunction_dr(cls, gamma, cutoff, dists):
        """
        Derivative of cutoff function 
        """
        r_cut=dists / cutoff
        
        dfcij_rijs = (gamma * (gamma + 1) / cutoff *
                     ( r_cut ** gamma - r_cut ** (gamma - 1)))
    
        return dfcij_rijs
    
    @classmethod
    def get_grad_terms(cls, gaussians, triples,
                       cutoff, width, nbins, aweight, gamma):
        """Atom pair wise contributions to the derivative calculations"""

        if triples.empty:
            return None, None, None
        
        xvec = cls.get_thetavec(nbins)
        diffvecs = np.subtract.outer(xvec, triples.cos_thetas).T
        fcij=cls.cutoff_function(triples.adm, cutoff, gamma)
        fcik=cls.cutoff_function(triples.edm, cutoff, gamma)

        
        commonterm = (fcij[:, np.newaxis] *
                      fcik[:, np.newaxis] *
                      diffvecs / width**2 * gaussians)

        vijs = triples.arm
        viks = triples.erm
        vjks = viks - vijs
        rijs = triples.adm
        riks = triples.edm
        rjks = np.linalg.norm(vjks, axis=1)

        dfcij_rijs = cls.d_cutofffunction_dr(gamma, cutoff, rijs)
        dfcik_riks = cls.d_cutofffunction_dr(gamma, cutoff, riks) 


        dt_drijs = 1 / riks -  triples.cos_thetas / rijs
        dt_driks = 1 / rijs - triples.cos_thetas / riks
        dt_drjks = - rjks / (rijs * riks)
        
        # For firsts
        drho_drij = (dfcij_rijs[:, None] * fcik[:, None] * gaussians +
                     commonterm * dt_drijs[:, None])
        vr_ijs = vijs / rijs[:, None]
        grads_ij=drho_drij[:,:,None]*vr_ijs[:, None, :]
        
        # for seconds
        drho_drik = (dfcik_riks[:, None] * fcij[:, None] * gaussians +
                     commonterm * dt_driks[:, None])
        vr_iks=viks / riks[:, None]
        grads_ik=drho_drik[:,:,None]*vr_iks[:, None, :]
        
        # for thirds
        drho_drjk = commonterm * dt_drjks[:, None]
        vr_jks=vjks / rjks[:, None]
        grads_jk=drho_drjk[:,:,None]*vr_jks[:, None, :]
        
        
        return grads_ij, grads_ik, grads_jk
    
    
    @classmethod
    def get_gradients(cls, grads_ij, grads_ik, grads_jk, groups, 
                      natoms, triples, nbins, dimensions=3):
        """
        Calculate derivatives of fingerprint with respect to 
        atomic coordinates
        """
        
        ncombis=cls.get_ncombis(triples.nelem)
        gradients = np.zeros([natoms, ncombis, nbins, dimensions])
        
        if triples.empty:
            return gradients
        
        i_vals=-grads_ij-grads_ik
        j_vals=grads_ij-grads_jk
        k_vals=grads_ik+grads_jk
        
        all_i=triples.indices[:,0]
        all_j=triples.indices[:,1]
        all_k=triples.indices[:,2]  
        
        for a in range(natoms):
            i_mask=(all_i==a)
            j_mask=(all_j==a)
            k_mask=(all_k==a)
            
            if np.any(i_mask):
                gradients[a] += np.einsum('ij,ikl->jkl',
                                          groups[i_mask],
                                          i_vals[i_mask],
                                          optimize=False)
            
            if np.any(j_mask):
                gradients[a] += np.einsum('ij,ikl->jkl',
                                          groups[j_mask],
                                          j_vals[j_mask],
                                          optimize=False)
            
            if np.any(k_mask):
                gradients[a] += np.einsum('ij,ikl->jkl',
                                          groups[k_mask],
                                          k_vals[k_mask],
                                          optimize=False)
        
        return gradients  
    
    @classmethod    
    def get_strain(cls, grads_ij, grads_ik, grads_jk, 
                   groups, triples, nbins):
        """
        Calculate the derivatives with respect to unit cell parameters
        """
        
        if triples.empty:
            ncombis=cls.get_ncombis(triples.nelem)
            return np.zeros([ncombis, nbins, 3, 3])
        
        vijs = triples.arm
        viks = triples.erm
        vjks = viks - vijs
        
        results=np.einsum('ikl, im-> iklm', 
                          grads_ij, vijs,
                          optimize=True)
        
        results+=np.einsum('ikl, im-> iklm', 
                          grads_ik, viks,
                          optimize=True)
        
        results+=np.einsum('ikl, im-> iklm', 
                          grads_jk, vjks,
                          optimize=True)
        
        gradients=np.einsum('ij, iklm -> jklm', 
                            groups, results,
                            optimize=True)
        
        
        return gradients
    
        

class AtomPairs:
    """ 
    Resolves indices of atomic pairs between which the distances 
    are considered in the fingerprint.

    Stores information for pair indices, distances and
    dislocation vectors.
    """
    
    def __init__(self, atoms, cutoff):
        """        
        Parameters
        ----------
        atoms : ase.Atoms
            Atomic object for which we want to find pairs
        cutoff : float
            Radial cutoff radius

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
                        
            for neighbor_index, vector in zip(neighbors, d):
                pairs.append([atom_index, neighbor_index])
                vectors.append(vector)
        
        self.nelem=len(atoms.symbols.species())
        self.get_pair_info(atoms, pairs, vectors)
        
    def get_pair_info(self, atoms, pairs, vectors):
        
        if len(pairs)==0:
            self.indices=[]
            return

        self.indices=np.array(pairs)
        self.rm=np.array(vectors)
        self.dm = np.linalg.norm(self.rm, axis=1)
        
    @staticmethod
    def get_distance_info(atoms, atom_idx, neighbor_list):
        
        positions = atoms.positions
            
        cell = atoms.cell
        
        neighbors, offsets = neighbor_list.get_neighbors(atom_idx)

        cells = np.dot(offsets, cell)
            
        d = positions[neighbors] + cells - positions[atom_idx]
        
        return neighbors, d 
            
    @property
    def empty(self):
        return len(self.indices) == 0


class AtomTriples:
    """ 
    Resolves indices of atomic triples between which the distances 
    are considered in the fingerprint.

    Stores information for triple indices, distances and
    dislocation vectors.
    """
    def __init__(self, atoms, cutoff):
        """        
        Parameters
        ----------
        atoms : ase.Atoms
            Atomic object for which we want to find pairs
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
            neighbors, distance_vectors = AtomPairs.get_distance_info(atoms, atom_index, neighbor_list)
                        
            neighbor_distance_pairs = list(zip(neighbors, distance_vectors))
            for (neighbor_1, d1), (neighbor_2, d2) in itertools.combinations(neighbor_distance_pairs, 2):

                triplets.append([atom_index, neighbor_1, neighbor_2])   
                vectors_ij.append(d1)
                vectors_ik.append(d2)
       
        self.nelem=len(atoms.symbols.species())
        self.get_triple_info(atoms, triplets, vectors_ij, vectors_ik)         
    
    def get_triple_info(self, atoms, triplets, 
                        vectors_ij, vectors_ik):
        
        if len(triplets)==0:
            self.indices=[]
            return
                        
        self.indices=np.array(triplets)
        self.arm=np.array(vectors_ij)
        self.erm=np.array(vectors_ik)
        
        self.adm = np.linalg.norm(self.arm, axis=1)
        self.edm = np.linalg.norm(self.erm, axis=1)
                
        args = (np.einsum('ij,ij->i', self.arm, self.erm)
                / self.adm / self.edm)

        # Take care of numerical errors:
        args = np.where(args >= 1.0, 1.0 - 1e-12, args)
        args = np.where(args <= -1.0, -1.0 + 1e-12, args)

        # rename
        self.cos_thetas = args
                
    @property
    def empty(self):
        return len(self.indices) == 0


class FPFactors:
    '''
    Class to calculate what elemental subgroups of the fingerprint
    different pairs and triples belong to in order to correctly sort
    them in the final fingerprint
    '''

    @staticmethod
    def get_factors_for_pairs(pairs, element_vectors):
        '''
        calculate pair element groups according to element_vectors.
        In the Normal case, all entries of a vector will be zero except one
        entry, but this can be different in fractional BEACON
        
        '''

        factors = np.zeros((len(pairs.indices), pairs.nelem,
                            pairs.nelem))

        if pairs.empty:
            return factors

        q = element_vectors
        
        i = pairs.indices[:, 0]
        j = pairs.indices[:, 1]

    
        factors= np.einsum('pi,pj->pij',  
                            q[i,:], q[j,:], 
                            optimize=False)
        
        factors+=np.transpose(factors, axes=(0, 2, 1))  
        
        # This part is to secure no repeats in fingerprint
        diagonal_mask = np.eye(pairs.nelem, dtype=bool)
        factors[:, diagonal_mask]/=2        
        triu_indices = np.triu_indices(pairs.nelem)
        factors = factors[:, triu_indices[0], triu_indices[1]]
        
        return factors


    @staticmethod
    def get_factors_for_triples(triples, element_vectors):
        '''
        calculate triple element groups according to element_vectors.
        In the Normal case, all entries of a vector will be zero except one
        entry, but this can be different in fractional BEACON
        '''
        factors = np.zeros((len(triples.indices), triples.nelem,
                            triples.nelem, triples.nelem))

        if triples.empty:
            return factors

        q = element_vectors  # alias

        i = triples.indices[:, 0]
        j = triples.indices[:, 1]
        k = triples.indices[:, 2]


        factors= np.einsum('pi,pj,pk->pijk',  
                            q[i,:], q[j,:], q[k,:], 
                            optimize=False)

        factors+=np.transpose(factors, axes=(0, 1, 3, 2))
        
        # This part is to secure no repeats in fingerprint
        diagonal_mask = np.eye(triples.nelem, dtype=bool)
        factors[:,:, diagonal_mask]/=2          
        triu_indices = np.triu_indices(triples.nelem)
        factors = factors[:, :, triu_indices[0], triu_indices[1]] 
        
        factors=factors.reshape(len(triples.indices),-1)
        
        return factors


    @staticmethod
    def get_element_vectors(atoms, elements):
        '''
        Return an natoms x nelements numpy array, where each
        column describes an element sorted in alphabetacal order.
        If atom 1 if of element A the first horizontal array will contain
        a 1 in the column corresponding to element A and zero otherwise.

        parameters
        ---------
        atoms: ase.Atoms object
        elements: list 
            list of element strings sorted alphabetcally, e.g. ['Ag', 'Cu']
        '''
        
        element_vectors=np.zeros( (len(atoms), len(elements)) )
      
        for i in range(len(elements)):
            element_mask = [(True if atom.symbol == elements[i] else False )
                            for atom in atoms]
            
            element_vectors[:,i][element_mask] = 1.0                
                
        return element_vectors



class CartesianCoordFP:
        
    """
    Null fingerprint where the fingerprint vector is
    merely the flattened atomic coordinates.
    """
    
    def __init__(self, atoms, **kwargs):
        """
        

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to be turned into fingerprint

        Returns
        -------
        None.

        """
        print('You are using the CartesianCoordFP')


        self.params = {}
        self.param_names = []

        self.atoms = atoms
        self.vector = self.atoms.get_positions(wrap=False).reshape(-1)
        self.gradients = self.calculate_gradients()


    @property
    def natoms(self):
        return len(self.atoms)

    def calculate_gradients(self):
        gradients = np.eye(self.natoms * 3)
        gradients = gradients.reshape(self.natoms, -1, 3, order='F')
        return gradients

    def reduce_coord_gradients(self):
        return self.gradients.reshape(self.natoms, -1, 3)


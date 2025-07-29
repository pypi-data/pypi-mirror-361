#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 21:51:47 2023

@author: casper
"""
from scipy.optimize import minimize
from scipy.optimize import LinearConstraint

from gpatom.fractional_beacon.drs import drs

from ase.calculators.singlepoint import SinglePointCalculator

import numpy as np

import warnings

from ase.io import write

from operator import and_

from functools import reduce

from ase.constraints import FixAtoms

from gpatom.fractional_beacon.unitcell_handler import UnitCellHandler




class ICEInfo:
    
    """
    Data class to store information on how to generate random chemical 
    fractions in RandomFractionGenerator and making constraints for 
    optimization of atoms in the ICE and HSICE surrogate optimizers. 
    
    Examples
    --------
    >>> iceinfo=ICEInfo(atoms, atoms_real=..., ice_elements=..., ...) 
    >>> (self.elements, 
         self.ice_element_bools, 
         self.n_real,
         self.frac_lims, 
         self.frac_cindex)=iceinfo.get_info()
    """
    
    def __init__(self, atoms, atoms_real=None, ice_elements=None, 
                 lower_lim=0, frac_cindex=None):

        """
        Parameters
        ----------
        atoms: ase.atoms object
            Atoms object for which the data will be stored
            Required
            
        atoms_real: ase.atoms object
            Atoms object representing the real atomic configuration. 
            If atoms_real include less atoms than atom, ghost atoms will
            be introduced. 
            If None atoms_real is set equal to atoms, i.e. no ghost atoms.
            Default is None
            
        ice_elements: list of lists of strings
            A list containing sublists. Each sublist contain as individual 
            strings the name of the chemical elements belonging to an ICE group.
            No element can be in two ICE groups at the same time.
            Default is None (No ICE groups)
            
        lower_lim: float
            Value describing the lowest existence value an atom can gain 
            during fraction generation and relaxation with weak existence. 
            Should be a positive value much smaller than 1, e.g. 0.05.
            Only relevant when making optimization with ghost atoms with
            simultaneous optimization of atomic coordinates.
            Default is 0 (no lower limit)
            
        frac_cindex: list od integers
            List of atomic indices for which the fractional chemical values
            should be fixed to the original element type. 
            Default is None  (no constrained fractional values)
        """

        
        if atoms_real is None:
            atoms_real=atoms
            
        (self.elements, 
         n_elements, 
         self.ice_element_bools) = ICEInfo.get_element_info(atoms, 
                                                              ice_elements)
        
        elements_real, self.n_real = ICEInfo.count_elements(atoms_real)

        assert np.all(self.elements==elements_real)

        self.n_ghost=n_elements-self.n_real
    
    
        self.frac_lims=[lower_lim, 1]
        
        if frac_cindex is None:
            frac_cindex=[]
        
        self.frac_cindex=frac_cindex
    
        
    @staticmethod
    def count_elements(atoms):
        elements=ICEInfo.get_sorted_elements(atoms)
        n_elements = ICEInfo.get_element_count(elements, atoms)
        return elements, n_elements
        
    @staticmethod
    def get_ice_bools(elements, ice_elements):
        """ convert ICE-groups info from convert from strings to booleans"""
        if ice_elements is None:
            ice_element_bools=[[False]*len(elements)]
            return ice_element_bools

        ice_element_bools=[]   
    
        if type(ice_elements[0]) == list :
            for sub_ice_elements in ice_elements:
                bools=[ (elem in sub_ice_elements) for elem in elements ]
                ice_element_bools.append(bools)
        elif type(ice_elements[0]) == str :
            bools=[ (elem in ice_elements) for elem in elements ]
            ice_element_bools.append(bools)   
        else:
            raise TypeError("ice_elements must be list of strings or a list of lists of strings")
        
        return ice_element_bools
        
    @staticmethod        
    def get_element_info(atoms, ice_elements):
        elements, n_elements = ICEInfo.count_elements(atoms)
        ice_element_bools = ICEInfo.get_ice_bools(elements, ice_elements)
        return elements, n_elements, ice_element_bools
    
    @staticmethod
    def get_element_count(elements, atoms):
        """ Count number of atoms of each element """
        symbol_list = list(atoms.symbols[:])
        n_0=np.zeros(len(elements))
        for i in range(len(elements)): 
            n_0[i]=symbol_list.count(elements[i])
        return n_0

    @staticmethod
    def get_sorted_elements(atoms):
        """ Sort elements in alphabetical order"""
        elements=sorted(atoms.symbols.species())
        return elements
    
    def get_info(self):
        """ Return ICE info in proper format to be used in other classes"""
        return (self.elements, self.ice_element_bools, self.n_real,
                self.frac_lims, self.frac_cindex)





class RandomFractionGenerator:
    
    """
    Class for generating random chemical fractions for atoms. 

    Examples  
    >>> rfg=RandomFractionGenerator(ice_info, randomtype='drs')
    >>> fractions=rfg.get_fractions(atoms)
    """ 
    
    def __init__(self , ice_info, randomtype='drs', rng=np.random):  

        """         
        Parameters
        ----------
        ice_info: ICEInfo object
            Info including constraints, ICE groups, ghost atoms etc necessary
            for creation of the chemical fractions.
            Required    
        
        random_type: string
            Setting on how to create the random fractions. 
            Possible settings include
            'uniform': Give all atoms in an ICE group uniform chemical fractions.
            'drs': Use dirichlet rescale algorithm to assign random chemical
            fractions to all atoms in an ICE group.
            'whole_atoms: Assign each atom 0 or 1 chemical fractions corresponding
            to the chemical compositon of the atoms object.
            Default is 'drs'    
        
        rng: random number generator object
            Random number generator to make results reproducible.
            Default is np.random (not reproducible)
        """
        
        (self.elements,
        self.ice_elements,
        self.n_real,
        self.frac_lims,
        self.frac_cindex) = ice_info.get_info()
        
        self.randomtype = randomtype
        self.rng = rng
        
    def get_fractions(self, atoms):
        """
        Method to get chemical fractions
        
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms object we want fractions for

        Raises
        ------
        RuntimeError
            If  an unknown sting is stored in randomtype

        Returns
        -------
        f : numpy.array
            Chemical fractions for each element for each atoms
        """
        
        if self.randomtype == 'uniform':
            f = self.get_uniform(atoms)
    
        elif self.randomtype=='drs':
            f=self.get_dirichlet_rescale(atoms)
            
        elif self.randomtype=='whole_atoms':
            f=self.get_whole_atoms(atoms)     
                    
        else:
            raise RuntimeError('randomtype={:s} not known.'
                               .format(self.randomtype))
        return f
    

    def get_uniform(self, atoms):
        """ Get uniform fractions in general case"""
        
        f=self.get_whole_atoms(atoms)
        
        if self.ice_elements is not None:
            f=self.get_uniform_ice(atoms, f=f)
        
        if self.n_real is not None:
            f=self.get_uniform_ghost(atoms, f=f)
        
        return f
        
          
    def get_uniform_ice(self, atoms, f=None):
        """
        Get uniform fractons when ICE groups are included

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want chemical fractions
        f : numpy.array
            Chemical fractions. If None Full fractions will be setup 
            before modifying
            Default is None

        Returns
        -------
        f : numpy.array
            Chemical frations
        """
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements)

        if f is None:
            f=self.get_whole_atoms(atoms)
                
        for sub_ice_elements in self.ice_elements:

            ice_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                        sub_ice_elements, 
                                                        constrained_fractions=self.frac_cindex)
        
            not_ice_mask=np.logical_not(ice_mask)

            for i in range(len(self.elements)):
            
                if sub_ice_elements[i] and ghost_elements[i]:
                    f[ice_mask,i] = (self.n_real[i]-sum(f[not_ice_mask,i]) + n_ghost[i]*self.frac_lims[0]) / sum(ice_mask)
                
                elif sub_ice_elements[i] and not ghost_elements[i]:
                    f[ice_mask,i] =(self.n_real[i]-sum(f[not_ice_mask,i])) / sum(ice_mask)
                    
        return f
        
    def get_uniform_ghost(self, atoms, f=None):
        """ 
        Get uniform fractions when ghost atoms are included"
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want chemical fractions
        f : numpy.array
            Chemical fractions. If None Full fractions will be setup 
            before modifying
            Default is None

        Returns
        -------
        f : numpy.array
            Chemical frations
        """
        
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements)
        
        full_ice_elements = AtomsConverter.get_full_ice_elements(atoms, 
                                                                 self.elements, 
                                                                 self.ice_elements)
        
        ghost_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                      ghost_elements,
                                                      constrained_fractions=self.frac_cindex)
        
        full_ice_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                         full_ice_elements,
                                                         constrained_fractions=self.frac_cindex)     
        
        if f is None:
            f=self.get_whole_atoms(atoms)
        
        for i in range(len(self.elements)):
        
            if not full_ice_elements[i] and ghost_elements[i]:
                specific_element = [ (n==i) for n in range(len(self.elements))]
                element_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                                specific_element,
                                                                constrained_fractions=self.frac_cindex)
                
                mask = list(map(and_, np.logical_not(full_ice_mask), element_mask))        
                not_mask = list(map(and_, mask, np.logical_not(ghost_mask)))
                
                f[mask,i] =(self.n_real[i]-sum(f[not_mask,i]) + n_ghost[i]*self.frac_lims[0]) / sum(mask)
                
        return f
    
    
    
    
    def ice_drs(self, atoms, ice_elements, ice_mask):  
        """
        Create atomic chemical fractions for atoms in ICE groups.
        Doesnt care if atoms have ghost atoms or not. 
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms under consideration
        ice_elements : list of lits if bools
            List specifying what elements are in same ICE group
        ice_mask :  list if bools
            List with one bool for each atom being true if atom is fractional

        Returns
        -------
        f : numpy.array
            chemical fractions
        """
        
        not_ice_mask=np.logical_not(ice_mask)
        
        n_ice_atoms=sum(ice_mask)
        
        whole_fractions=self.get_whole_atoms(atoms)
        
        n_0=AtomsConverter.get_element_count(self.elements, atoms)
        
        lower_limits=np.zeros(n_ice_atoms)        
        upper_limits=np.ones(n_ice_atoms)
        
        f_sum=0
    
        f=np.zeros( (len(atoms), len(self.elements))) 
        for i in range(len(self.elements)):
            
            if ice_elements[i]:
                
                f_sum+=n_0[i] - np.sum(whole_fractions[not_ice_mask,i])

                fracs=drs(n_ice_atoms, f_sum, upper_limits, lower_limits, seed=self.rng.randint(1000000))
                
                fracs=np.array(fracs)
                
                f[ice_mask,i]=fracs - lower_limits
                
                lower_limits=fracs
                
        return f


    def ghost_remove_dirichlet_rescale(self, atoms, ice_fractions, ice_elements, ice_mask): 
        """
        Method to remove chemical existence from atoms so the total 
        chemical existences matches that of the real system without ghost atoms

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object including ghost atoms
        ice_fractions : numpy.array
            Chemical fractions made wth ICE module for atoms with ghost atoms 
        ice_elements : list of lits if bools
            List specifying what elements are in same ICE group
        ice_mask :  list if bools
            List with one bool for each atom being true if atom is fractional

        Returns
        -------
        f : numpy.array
            modified chemical fractons
        """
        
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements)

        n_ice_atoms=sum(ice_mask)
        
        lower_limits=np.zeros(n_ice_atoms)
        
        f=np.zeros( (len(atoms),len(self.elements)) )
        for i in range(len(self.elements)):
            if ice_elements[i] and ghost_elements[i]:
                
                ice_fractions_only=ice_fractions[:,np.array(ice_elements,dtype=bool)]
                
                existence_sum= AtomsConverter.get_existence_fractions(ice_fractions_only[ice_mask,:])
                            
                upper_limits=np.minimum(ice_fractions[ice_mask,i], existence_sum-n_ghost[i]*self.frac_lims[0])
                
                f_sum=n_ghost[i]*(1-self.frac_lims[0])
                
                fracs=drs(n_ice_atoms, f_sum, upper_limits, lower_limits, seed=self.rng.randint(1000000))
                
                fracs=np.array(fracs)
                
                f[ice_mask,i]=-fracs
                
        return f

            
    def ghost_drs(self, atoms, n_ghost, ghost_elements, ghost_mask):  
        """
        Create atomic chemical fractons for elements with ghost atoms which are 
        not part of an ICE group.
        ----------
        atoms : ase.Atoms
            Atoms object with ghost atoms
        n_ghost : numpy.array
            Number of ghost atoms for each element
        ghost_elements : list of bools
            One bool for each element describing if it has ghost atoms
        ghost_mask : list of bools
            One bool for each atom describing if its of an element 
            with ghost atoms

        Returns
        -------
        f : numpy.array
            Chemical fractions
        """        
        
        not_ghost_mask=np.logical_not(ghost_mask) 
        
        whole_fractions=self.get_whole_atoms(atoms)
      
        f=np.zeros( (len(atoms), len(self.elements)))
        symbol_list = list(atoms.symbols[:])
        
        for i in range(len(self.elements)):
            
            if ghost_elements[i]:
            
                symbol_indices = [k for k, symbol in enumerate(symbol_list) 
                                  if (symbol == self.elements[i] and ghost_mask[k] )]   
                
                n_available_atoms=len(symbol_indices)
            
                lower_limits=np.ones(n_available_atoms)*self.frac_lims[0]
            
                upper_limits=np.ones(n_available_atoms)  
                
                f_sum=self.n_real[i]+n_ghost[i]*self.frac_lims[0] - sum(whole_fractions[not_ghost_mask,i])
                                
                fracs=drs(n_available_atoms, f_sum, upper_limits, lower_limits, seed=self.rng.randint(1000000))
                
                f[symbol_indices,i]=np.array(fracs)

        return f
    
        
    def get_dirichlet_rescale(self, atoms):
        """ Get drs fractions in the general case """
        
        f=self.get_whole_atoms(atoms)
        
        if self.ice_elements is not None:
            f=self.get_ice_dirichlet_rescale(atoms, f=f)
        
        if self.n_real is not None:
            f=self.get_ghost_dirichlet_rescale(atoms, f=f)
            
        return f


    def get_ice_dirichlet_rescale(self, atoms, f=None):
        """ 
        Get drs atomic fractions for elements in ICE groups. 
        Method is aware if ICE groups contain ghost atoms or not.
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want chemical fractions
        f : numpy.array
            Chemical fractions. If None Full fractions will be setup 
            before modifying
            Default is None

        Returns
        -------
        f : numpy.array
            Chemical frations
        """
                
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements)
        
        if f is None:
            f=self.get_whole_atoms(atoms)
        
        for sub_ice_elements in self.ice_elements:
            ice_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                        sub_ice_elements, 
                                                        constrained_fractions=self.frac_cindex)
            
            ice_fractions=self.ice_drs(atoms, sub_ice_elements, ice_mask)
            f[ice_mask,:]=ice_fractions[ice_mask,:]

            ice_and_ghost_elements = list(map(and_, sub_ice_elements, ghost_elements))     
                
            if any(ice_and_ghost_elements):  
                remove_ghost_fractions=self.ghost_remove_dirichlet_rescale(atoms, ice_fractions, 
                                                                           sub_ice_elements, ice_mask)
                f[ice_mask,:]+=remove_ghost_fractions[ice_mask,:]    
                
        return f
    
    def get_ghost_dirichlet_rescale(self, atoms, f=None):
        """ 
        Get drs atomx element fractions for elements with ghost elements
        not part of any ICE groups.
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want chemical fractions
        f : numpy.array
            Chemical fractions. If None Full fractions will be setup 
            before modifying
            Default is None

        Returns
        -------
        f : numpy.array
            Chemical frations
        """

        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements)
    
        ghost_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                      ghost_elements, 
                                                      constrained_fractions=self.frac_cindex) 
        
        full_ice_elements = AtomsConverter.get_full_ice_elements(atoms, self.elements, self.ice_elements)
        
        full_ice_mask=AtomsConverter.get_fractional_mask(atoms, self.elements, 
                                                         full_ice_elements, 
                                                         constrained_fractions=self.frac_cindex)     
            
        ghost_not_ice_mask = list(map(and_, np.logical_not(full_ice_mask), ghost_mask))        

        if f is None:
            f=self.get_whole_atoms(atoms)

        if any (ghost_not_ice_mask):
            add_real_fractions=self.ghost_drs(atoms, n_ghost, ghost_elements, ghost_mask)
            f[ghost_not_ice_mask,:]=add_real_fractions[ghost_not_ice_mask,:]
            
        return f
        
    
    def get_whole_atoms(self, atoms):
        """ Get integer values matcing the chemical composition of atoms """
        f=AtomsConverter.atoms2fractions(atoms, self.elements)
        return f


class ICEFractionConverter:  
    
    """
    Static class to handle conversion of atoms into full chemical
    fractions or from a set of chemical fractions into a set of atoms
    fullfilling the desired elemental composition
    """    

    @staticmethod
    def set_fractional_atoms(atoms, fractional_elements):        
        """
        Finds what atoms belong to the elements being True in
        fractional_elements
        """
        symbol_list = list(atoms.symbols[:])
        fmask = [(symbol in fractional_elements) for symbol in symbol_list]
        
        n_0=[]
        for elem in fractional_elements:
            n_0.append(symbol_list.count(elem))
                
        return fmask, n_0   
  
    @staticmethod
    def atoms2fractions(atoms, fractional_elements):
        """
        Convert ase.Atoms object to integer chemical fraction values
        """
        f=np.zeros( (len(atoms), len(fractional_elements)) )
          
        for i in range(len(fractional_elements)):
            element_mask = [(True if atom.symbol == fractional_elements[i] else False )
                            for atom in atoms]
                
            f[:,i][element_mask] = 1.0  
        
        return f


    @staticmethod
    def fractions2atoms(fractions, atoms, fractional_elements, constrained_fractions):
        """
        Procedure for transforming a set of chemical fractions into an atoms
        object satisfying the elemental composition of the original atoms object
        in a prioritzed order of largest elemental fractions.
        
        See AtomsConverter.ice_convert
        """

        atoms=atoms.copy()        
        
        natoms=len(atoms)
        nfe=len(fractional_elements)
        
        fmask, n_0 = ICEFractionConverter.set_fractional_atoms(atoms, fractional_elements) 
        
        transformable_atoms=np.array(fmask)
        
        if len(constrained_fractions)>0:   
            full_fractions=ICEFractionConverter.atoms2fractions(atoms,fractional_elements)
            element_count=np.sum(full_fractions[constrained_fractions,:], axis=0)
            transformable_atoms[constrained_fractions]=False
        else:
            element_count=np.zeros(nfe) 
            
        assignable_elements=(n_0>element_count)
                

        atoms_idx=np.arange(natoms).reshape(natoms,1)
        atoms_idx=np.tile(atoms_idx,(1,nfe))
        
        element_idx=np.arange(nfe)
        
        while any(assignable_elements):
                        
            available_atoms=atoms_idx[transformable_atoms]

            available_fractions=fractions[transformable_atoms]

            fraction_sort = np.argsort(available_fractions, axis=0)[::-1]

            available_atoms_sorted=np.take_along_axis(available_atoms, fraction_sort, axis=0)

            contesting_atoms=available_atoms_sorted[0,:]  
                        
            contesting_atoms_fractions=np.array([  fractions[contesting_atoms[j], j] 
                                                 for j in range(nfe)]) 

            available_elements=element_idx[assignable_elements]
        
            element_sort=np.argsort(contesting_atoms_fractions[assignable_elements])[::-1]

            winner_element=available_elements[element_sort][0]
            
            winner_atom=contesting_atoms[winner_element]

            atoms[winner_atom].symbol=fractional_elements[winner_element]
                    
            transformable_atoms[winner_atom]=False    
            element_count[winner_element]+=1
            
            assignable_elements=(n_0>element_count)

        for i, elem in enumerate(fractional_elements):
            assert atoms.symbols.count(elem)  == n_0[i]           
            
        return atoms



class GhostHandler:
    """
    Static class to handle conversion of atoms into full existence
    fractions or from a set of existtence fractions into a set of atoms
    fullfilling the desired atomic existence values
    """    
        
    @staticmethod
    def construct_processed_atoms_object(atoms, selected_atoms):
        """ Pick out only selected atoms """
        processed_atoms=atoms.copy() 
        processed_atoms=atoms[selected_atoms]
        
        return processed_atoms

    
    @staticmethod   
    def exclude_nonconserved_ghosts(atoms, exclusion_list, n_ghost, constrained_atoms, fmask, fractional_elements):
        """
        Get ghost_mask telling what atoms can be removed (False) 
        or should stay (True) 
        """
        
        removeable_atoms=np.array(fmask)           # false means that the atom is conserved. cant be erased
        removeable_atoms[constrained_atoms]=False
        
        ghost_mask=np.ones(len(atoms),dtype=bool)  # remove atom if false
        
        symbol_list = list(atoms.symbols[:])
        
        for k in range(len(fractional_elements)):
        
            count=0   
            for i in exclusion_list:

                if  removeable_atoms[i] and symbol_list[i]==fractional_elements[k]:
                    ghost_mask[i]=False
                    count+=1

                                
                if count==n_ghost[k]:
                    break

               
        return ghost_mask


    @staticmethod
    def generate_ghosts_constrained(atoms, fractions, n_ghost, constrained_atoms, fractional_elements):
        """
        Get ghost_mask telling what atoms cand be removed (False) 
        or should stay (True) 
        
        See AtomsConverter ghost_convert
        """

        fmask, n_0 = GhostHandler.set_fractional_atoms(atoms, fractional_elements)        

        fractions=fractions.copy().reshape(len(atoms))
        
        if np.all(n_ghost==0):
            return np.ones(len(atoms),dtype=bool)
        argsort = np.argsort(fractions)
        ghost_mask=GhostHandler.exclude_nonconserved_ghosts(atoms, argsort, n_ghost, constrained_atoms, fmask, fractional_elements)

        return ghost_mask  


    @staticmethod
    def set_fractional_atoms(atoms, fractional_elements):
        """
        Finds what atoms belong to the elements being True in
        fractional_elements
        """
        symbol_list = list(atoms.symbols[:])
        fmask = [(symbol in fractional_elements) for symbol in symbol_list]
        
        n_0=[]

        for i in range(len(fractional_elements)): 
            n_0.append(symbol_list.count(fractional_elements[i]))
                
        return fmask, n_0   
  
    @staticmethod
    def atoms2fractions(atoms, fractional_elements):
        """ Convert ase.Atoms object to integer chemical fractions """
        return np.ones(len(atoms)) 


class AtomsConverter:
    
    """
    Static class to handle conversion of atoms into full chemical fractions
    and exisetnces or from a set of chemical fractions into a set of atoms
    fullfilling the desired atomic chemical composition and existence values
    """    
                
    @staticmethod 
    def get_existence_fractions(fractions):
       """ Sum fractions across all elements to get total existences """
       return np.sum(fractions,axis=1)

    @staticmethod
    def get_element_count(elements, atoms):
        """ Count the number of atoms belonging to each element """
        symbol_list = list(atoms.symbols[:])
        n_0=np.zeros(len(elements))
        for i in range(len(elements)): 
            n_0[i]=symbol_list.count(elements[i])
        return n_0
        
    @staticmethod
    def get_n_ghost(atoms, n_real, elements):
        """
        Get the number of ghost atoms for each element and a list of
        bools describing what elements has ghost atoms

        Parameters
        ----------
        atoms : ase.Atoms
            The atoms object including ghost atoms
        n_real : numpy.array
            The number of real atoms for each element
        elements : list of strings
            List of element string labels
            
        Returns
        -------
        n_ghost: list of integers
            The number of ghost atoms for each element
        ghost_elements: list of bools
            List bools describing what elements has ghost atoms (alphabetical)
        """
        if n_real is None:
            return np.zeros(len(elements)), [False]*len(elements)
        
        n_0=AtomsConverter.get_element_count(elements, atoms)

        n_ghost = n_0- np.array(n_real)

        ghost_elements=[ (n>0) for n in n_ghost]
        return n_ghost, ghost_elements

    @staticmethod
    def get_elements(elements, element_bools):
        """ Get element symbols for elements corresponding to element bools """
        element_list = [value for value, condition in zip(elements, element_bools) if condition == True]
        return np.array(element_list)

    @staticmethod
    def get_fractional_mask(atoms, elements, element_bools, constrained_fractions=None):
        """
        Method to generate a bool for each atom. True if atom belong to
        element in being True in element bools
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms under consideration
        elements : list of strings
            Strings labels of all elements in system
        element_bools : list of bools
            List of what elements to consider for method. True if considered
        constrained_fractions : List of bools
            List of bools describing what atoms are constrained to integer 
            chemical values. True if constrained

        Returns
        -------
        mask : list of bools
            List of bools for each atom, being true if atoms belong to
            one of the elements being True in element_bools
        """
        
        if constrained_fractions is None:
            constrained_fractions=[]
        
        element_list = AtomsConverter.get_elements(elements, element_bools)
        symbol_list = list(atoms.symbols[:])
        mask=np.array([(symbol in element_list) for symbol in symbol_list])
        mask[constrained_fractions]=False
        return mask

    @staticmethod
    def get_full_ice_elements(atoms, elements, ice_elements):
        """
        Get list of bools being True if an element is in any ICE group.
        """
        full_ice_elements = [reduce(lambda x, y: x | y, elements) for elements in zip(*ice_elements)]
        return full_ice_elements 
    
    @staticmethod
    def atoms2fractions(atoms, elements):
        """
        Convert ase.Atoms object to integers corresponding to the
        chemical compositions of atoms object
        """
        f=np.zeros( (len(atoms), len(elements)) )
          
        for i in range(len(elements)):
            element_mask = [(True if atom.symbol == elements[i] else False )
                            for atom in atoms]
                
            f[:,i][element_mask] = 1.0  
        
        return f
                
    @staticmethod
    def ice_convert(atoms, fractions, constrained_fractions, elements, ice_elements):
        """
        Procedure for transforming a set of chemical fractions into an atoms
        object satisfying the elemental composition of the original atoms object
        in a prioritzed order of largest elemental fractions.
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object with fractional elements
        fractions : numpy.array
            The chemical fractions
        constrained_fractions : list of bools
            A list wih one boof for each atom being True if atoms element is
            constrained
        elements : list of strings
            A list with all chemical symbols
        ice_elements :  List of list of bools
            Boolean listings of what elements belong to what ICE groups

        Returns
        -------
        deghosted_whole_atoms : ase.Atoms
            Atoms object with full elements
        """
        
        for sub_ice_elements in ice_elements:  
        
            sub_ice_symbols = AtomsConverter.get_elements(elements, sub_ice_elements)
            sub_ice_fractions = fractions[:,np.array(sub_ice_elements, dtype=bool)]
            atoms=ICEFractionConverter.fractions2atoms(sub_ice_fractions, atoms, 
                                                       sub_ice_symbols, 
                                                       constrained_fractions)
        
        return atoms
    
    @staticmethod 
    def ghost_convert(atoms, fractions, constrained_fractions, elements, n_real):
        """
        Procedure for transforming a set of chemical fractions into a set of 
        atoms satifying the existence values of the original atoms object.
        The atoms are priorized in order of higheste existence
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object with ghost atoms
        fractions : numpy.array
            The chemical fractions
        constrained_fractions : list of bools
            A list wih one boof for each atom being True if atoms element is
            constrained
        elements : list of strings
            A list with all chemical symbols
        n_real : numpy.array
            array of ints describing the number of atoms of each element 
            in the atoms object to be created 
            
        Returns
        -------
        deghosted_whole_atoms : ase.Atoms
            Atoms object without ghost atoms
        """
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, n_real, elements)
        
        ghost_symbols = AtomsConverter.get_elements(elements, ghost_elements)
        
        ghost_symbols_n_ghost=n_ghost[np.array(ghost_elements,dtype=bool)]
        
        existence_fractions=AtomsConverter.get_existence_fractions(fractions)    

        ghost_mask=GhostHandler.generate_ghosts_constrained(atoms, existence_fractions, ghost_symbols_n_ghost, constrained_fractions, ghost_symbols)
                
        deghosted_atoms=GhostHandler.construct_processed_atoms_object(atoms, ghost_mask)
        
        return deghosted_atoms
        
    @staticmethod 
    def fractions2atoms(atoms, fractions, constrained_fractions, elements, n_real, ice_elements):
        """
        Procedure for transforming a set of chemical fractions into an atoms
        object satisfying the elemental composition and existence values 
        of the original atoms object in a prioritzed order of largest 
        elemental fractions.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms with fractional atoms and evt ghost atoms
        fractions : numpy.array
            The chemical fractions
        constrained_fractions : list of bools
            A list wih one boof for each atom being True if atoms element is
            constrained
        elements : list of strings
            A list with all chemical symbols
        n_real : numpy.array
            array of ints describing the number of atoms of each element 
            in the atoms object to be created 
        ice_elements :  List of list of bools
            Boolean listings of what elements belong to what ICE groups

        Returns
        -------
        deghosted_whole_atoms : ase.Atoms
            Atoms object with full elements and no ghost atoms
        """
        
        whole_atoms=AtomsConverter.ice_convert(atoms, fractions, 
                                               constrained_fractions, 
                                               elements, ice_elements)
        
        deghosted_whole_atoms=AtomsConverter.ghost_convert(whole_atoms, fractions, 
                                                           constrained_fractions, 
                                                           elements, n_real)
                
        return deghosted_whole_atoms 
    
    @staticmethod
    def release_extra_existence(atoms, fractions, constrained_fractions, elements, n_real):
        """
        Method to remove the extra existence in the system when a lower
        existence limit is used when the weak existing steps are done. 
        existence are removed from the atom in order of smallest existence.
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms of consideration
        fractions : numpy.array
            The chemical fractions including additional existence
        constrained_fractions : list of bools
            A list wih one boof for each atom being True if atoms element is
            constrained
        elements : list of strings
            A list with all chemical symbols
        n_real : numpy.array
            array of ints describing the number of atoms of each element 
            in the atoms object to be created 
            
        Returns
        -------
        fractions : numpy.array
            Elemental fractions without extra existence
        """
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, n_real, elements)
        
        for i in range(len(elements)):
            if ghost_elements[i]:
                
                element_i_fractions=fractions[:,i]                
                surplus_existence=np.sum(element_i_fractions, axis=0)-n_real[i]

                sorted_element_i_fractions_indices=np.argsort(element_i_fractions)
                
                for idx in sorted_element_i_fractions_indices:
                    
                    if idx in constrained_fractions:
                        continue
                        
                    remove_frac=min( element_i_fractions[idx], surplus_existence) 
                    fractions[idx,i]-=remove_frac
                    surplus_existence-=remove_frac
                    
                    if surplus_existence<=0:   
                        break
                
        return fractions


class ICEParamsHandler:
    """
    Static class to handle restucturing of coordinate and chemical fraction
    data so it fits the minimizer object and the atoms object respectively.
    
    NB: In the below methods nfe stands for number of fractional elements.
    """
    @staticmethod     
    def pack_params(natoms, nfe, position_params, fraction_params, cell_params):
        """ 
        Convert coordinates, chemical fractions and unit cell from 
        atoms object format to optimizer input format.
        """
        assert np.shape(cell_params)==(3,3)
        atomic_params = ICEParamsHandler.pack_atomic_params(natoms, nfe, position_params, fraction_params)
        params= np.concatenate((atomic_params, cell_params.flatten()), axis=0)
        return params

    @staticmethod
    def pack_atomic_params(natoms, nfe, position_params, fraction_params):
        """
        Convert coordinates and chemical fractions from atoms object format 
        to optimizer input format without the unit cell.
        """
        if np.shape(fraction_params)!=(natoms,nfe):
            fraction_params=fraction_params.reshape(natoms,nfe)
        atomic_params = np.concatenate((position_params, fraction_params), axis=1).flatten()
        return atomic_params
    
    @staticmethod 
    def unpack_params(natoms, nfe, params):
        """ 
        Convert coordinates, chemical fractions and unit cell values 
        from optimizer input/output  format to atoms object format.
        """
        atomic_params=params[0:-9]
        cell_params=params[-9::].reshape(3,3)
        position_params, fraction_params = ICEParamsHandler.unpack_atomic_params(natoms, nfe, atomic_params) 
        return position_params, fraction_params, cell_params

    @staticmethod 
    def unpack_atomic_params(natoms, nfe, params):
        """ 
        Convert coordinates and chemical fractions from optimizer input/output 
        format to atoms object format without the unit cell values.
        """
        atomic_params=params.reshape(natoms, 3+nfe)
        position_params = atomic_params[:, :3]              
        fraction_params = atomic_params[:, 3::] 
        return position_params, fraction_params



class ICESurrogateOptimizer():  
    
    """
    Class for optimization of atomic coordinates and elemental fractions. 

    Examples
    ---------  
    >>> opt=ICESurrogateOptimizer(ice_info, randomtype=..., rng=...)
    >>> opt.relax(atoms, model, file_identifier)
            if random_fraction_generator is none, atoms must carry
            a property called fractions of size natoms x nelements
            where all values are between zero and one.  This property will
            be automaticallt set if using the 
            RandomStructureAndFractionGenerator.
            Model should be FractionalModel or FractionalLCBModel        
    """
    
    def __init__(self, ice_info,
                 fmax=0.05, 
                 weak_existing_steps=0,
                 after_steps=100, 
                 post_rounding_steps=50,
                 with_unit_cell=False, 
                 fixed_cell_params=None, 
                 random_fraction_generator=None,
                 derivative_modulation=1.0,
                 coord_rescale=1,
                 fraction_rescale=1,
                 cell_rescale=1,
                 error_method=None):
    
        """
        Parameters
        ----------
        
        ice_info: ICEInfo object
            Info including constraints, ICE groups, ghost atoms etc necessary
            for creation of the chemical fractions.
            Required    
        
        fmax: float
            The convergence criteria. Criteria stops relaxation
            if the energy of two consequtive relaxations are smaller than fmax.
            Default is 0.001
        
        weak_existing_steps: int 
            Number of steps taken with optimization of atomic fractions, 
            where the lower existence level of atoms has a lower limit 
            (stored in ice_info) to make sure ghost atoms stay active. 
            Only usefull when running with ghost atoms
            Default is 0
            
        after_steps: int
            Number of steps taken with optimization of atomic fractions, with
            lower existence level 0. This comes after the weak existing steps
            Default is 100
            
        post_rounding_steps: int
            Number of steps taken where the elemental fractions are fixed to 
            0 or 1 to imitate a normal relaxation. 
            Default is 50
                    
        with_unit_cell: bool
            If the unit cell should also be optimized
            Default is False
            
        fixed_cell_params: list of 6 bools
            Boools giving what voight components of the cell is not optimized
            xx, yy, zz, yz, xz, xy
            Default is [False, False, False, False, False, False]
            
        random_fraction_generator: a random fraction generator object with
            a method called get_fractions(atoms), which generates chemical
            fractions.
            Don't include if atoms object is allready being set up to have
            a property fractions in structure generator as the fractions
            will then be overwritten.
            Default is None (dont make fractions)
            
        derivative_modulation: float
            Multiplier on the output values of the optimizer to increase
            stability, as the SLSQP optimizer is prone to taking long steps. 
            Smaller value, means smaller steps. 
            Default is 1.0  (no modulation)
        
        coord_rescale: float
            A rescaling factor to stretch the energy landscape with respect
            to the coordinates. A larger value mean more stretching and hence
            shorter optimizer steps
            Default is 1 (no stretching)
            
        fraction_rescale: float
            A rescaling factor to stretch the energy landscape with respect
            to the elemental fractions. A larger value, mean more stretching 
            and hence shorter optimizer steps
            Default is 1 (no stretching)
        
        cell_rescale: float
            A rescaling factor to stretch the energy landscape with respect
            to the unit cell. A larger value, mean more stretching and hence
            shrter optimizer steps
            Default is 1 (no stretching)
        
        error_method: functons, optional 
            a customly written method whic raises the CustomError from
            BEACON to prematurely terminate a surrogate relaxation
            Default is None   
        """
                
        self.rfg=random_fraction_generator
        
        (self.elements,
        self.ice_elements,
        self.n_real,
        self.frac_lims,
        self.frac_cindex) = ice_info.get_info()
        
        self.fmax = fmax*derivative_modulation
        
        self.weak_existing_steps=weak_existing_steps
        self.after_steps=after_steps
        self.post_rounding_steps=post_rounding_steps
        
        self.derivative_modulation=derivative_modulation
        self.fraction_rescale=fraction_rescale
        self.coord_rescale=coord_rescale
        self.cell_rescale=cell_rescale
        
        self.with_unit_cell=with_unit_cell
        
        self.error_method=error_method

        if self.with_unit_cell:
            self.relax_method=self.constrain_and_minimize_unitcell
        else:
            self.relax_method=self.constrain_and_minimize
            
        if self.with_unit_cell:
            if fixed_cell_params is None:
                fixed_cell_params = [False]*6    
            self.opt_cell_mask = np.array([not elem for elem in fixed_cell_params], dtype=int)
    

    def relax(self, atoms, model, output_file=None):     
        """
        Relaxes atoms in the potential of model and eventually writes
        a trajectory file with name output_file
        
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms to optimize
        model : BEACON FractionalModel or FractionalLCBModel class
            Model capable of making energy and force predictions
        output_file : string, optional
            The name of the trajectrory ourpur file. 
            Deafaults is None (no files written)

        Returns
        -------
        opt_atoms : ase.Atoms
            The optimized atoms
        success : bool
            True if relaxation converged, otherwise False
        """
               
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements) 
        model.gp.set_n_ghost(n_ghost)
       
        if self.rfg is not None:
            fractions = self.rfg.get_fractions(atoms)
        else:
            fractions=atoms.fractions
       
                
        writer=self.initiate_writer(atoms, fractions, model, 
                                    output_file=output_file)
    
        if self.weak_existing_steps>0:
            success, atoms, fractions = self.ghost_relax(atoms, 
                                                         fractions, 
                                                         model, writer)
        
        
        fractions=AtomsConverter.release_extra_existence(atoms, fractions, 
                                                         self.frac_cindex, 
                                                         self.elements, self.n_real)
        
        if self.after_steps>0:            
            success, atoms, fractions = self.projected_relax(atoms, 
                                                             fractions, 
                                                             model, writer)
        
        
        whole_atoms=AtomsConverter.fractions2atoms(atoms, fractions, 
                                                   self.frac_cindex, self.elements, 
                                                   self.n_real, self.ice_elements)
        
        
        model.gp.set_n_ghost(np.zeros(len(self.elements)))
        # relax with rounded fractions and no ghosts 
        if self.post_rounding_steps>0:
            success, whole_atoms = self.round_relax(whole_atoms, model, writer)
            
        self.make_frame(writer, model, whole_atoms)
                
        return whole_atoms, success
    
    def initiate_writer(self, atoms, fractions, model, output_file=None):
        """ Setts up the writer class and gathers the first writing point """ 

        writer = OptimizationWriter(atoms=atoms,
                                    elements=self.elements,
                                    ice_elements=self.ice_elements,
                                    frac_cindex=self.frac_cindex,
                                    output_file=output_file)
    
        self.make_frame(writer, model, atoms, fractions)
        
        return writer
    
    
    def make_frame(self, writer, model, atoms, fractions=None):
        """ Write a frame of the to the output file using the writer """
        
        if fractions is None:
            fractions=AtomsConverter.atoms2fractions(atoms, self.elements)    
        
        (energy, 
         grads, 
         fraction_grads) = model.calculate(atoms, fractions=fractions, 
                                           with_stress=False)
         
        writer.set_atoms(atoms=atoms, fractions=fractions, 
                         energy=energy, gradients=grads)
        
        writer.write_atoms(energy)    

    
    def ghost_relax(self, atoms, fractions, model, writer):
        """
        Relax atomic positions and chemical fractons in the model with
        all atomic existences between 1>>lower_lim>0 and 1. 
        Eventually write out optmization steps
        """
        success, atoms, fractions = self.relax_method(atoms, model, writer,
                                                      fractions=fractions,
                                                      frac_lims=self.frac_lims,
                                                      frac_cindex=self.frac_cindex,
                                                      steps=self.weak_existing_steps)
        return success, atoms, fractions 


    def projected_relax(self, atoms, fractions, model, writer):
        """
        Relax atomic positions and chemical fractons in the model with
        all atomic existences between 0 and 1. 
        Eventually write out optmization steps
        """
        # relax atoms still with fractional atoms but where ghosts can go to zero
        success, atoms, fractions = self.relax_method(atoms, model, writer,
                                                      fractions=fractions,
                                                      frac_lims=[0,1], 
                                                      frac_cindex=self.frac_cindex,
                                                      steps=self.after_steps)
        return success, atoms, fractions        
        
    

    def round_relax(self, atoms, model, writer): 
        """
        Relax atomic positions only after all chemical fractions has been
        rounded to 0 or 1. 
        Eventually write out optmization steps
        """
        whole_fractions=AtomsConverter.atoms2fractions(atoms, self.elements)
        success, atoms, fractions = self.relax_method(atoms, model, writer,
                                                      fractions=whole_fractions,
                                                      frac_lims=[0, 1],
                                                      frac_cindex=np.arange(len(atoms)),
                                                      steps=self.post_rounding_steps) 
        
        return success, atoms


    
    def _calculate_properties(self, params, *args):
        """
        Objective function to be minimized when unit cell is not optimized.

        Parameters
        ----------
        params : numpy.array
            Array with all atomic coordinates and chemical fractions
        *args : list
            List of arguments to be used in the objective function, 
            these include: the writer object, the atoms object and
            the model potential
            
        Returns
        -------
        float
            The energy
        
        numpy.array 
            The derivatives of the energy w.r.t atomic coordinates and
            chemical fractions
        """ 
        writer = args[0]
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        
        (transformed_positions,  
         transformed_fractions) = ICEParamsHandler.unpack_atomic_params(natoms,
                                                                        len(self.elements), 
                                                                        params)      
                                                                            
        positions = CoordinateTransformer.positions_transformed_to_real(transformed_positions, 
                                                                        self.coord_rescale)

        fractions=CoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
        
        atoms.positions = positions
    
        if self.error_method is not None:
            self.error_method(atoms)    
    
        (energy, 
         atoms_forces, 
         atoms_frac_grads) = model.calculate(atoms, fractions=fractions, 
                                             with_stress=False)
        
        
        writer.set_atoms(atoms=atoms, fractions=fractions, energy=energy, gradients=atoms_forces) 
         
        transformed_forces = CoordinateTransformer.coord_gradients_real_to_transformed(atoms_forces, self.coord_rescale)
        
        transformed_atoms_frac_grads=CoordinateTransformer.fraction_gradients_real_to_transformed(atoms_frac_grads, self.fraction_rescale)
        
        
        derivatives=ICEParamsHandler.pack_atomic_params(natoms, len(self.elements), 
                                                        transformed_forces, 
                                                        transformed_atoms_frac_grads)
        
        energy_rescale, derivatives_rescale=self.rescale_output(energy, derivatives)

        return (energy_rescale , np.array(derivatives_rescale)) 
    
    
    
    def _calculate_properties_unitcell(self, params, *args):
        """
        Objective function to be minimized when unit cell is also optimized.

        Parameters
        ----------
        params : numpy.array
            Array with all atomic coordinates, chemical fractions
            and cell parameters
        *args : list
            List of arguments to be used in the objective function, 
            these include: the writer object, the atoms object,
            the model potential, the original unit cell and 
            a scaling factor for the cell coordinates
            
        Returns
        -------
        float
            The energy
        
        numpy.array 
            The derivatives of the energy w.r.t atomic coordinates,
            chemical fractions and the cell coordinates.
        """      
        
        writer = args[0]
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        
        original_cell=args[3]
        cell_factor=args[4] 
        
        (transformed_deformed_positions, 
         transformed_fractions, 
         deformation_tensor) = ICEParamsHandler.unpack_params(natoms,
                                                              len(self.elements), 
                                                              params)
                                                                  
        deformed_positions=CoordinateTransformer.positions_transformed_to_real(transformed_deformed_positions,  
                                                                               self.coord_rescale)
                                                                                    
        fractions=CoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
                                                                  
                                                                  
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, 
                                                     deformed_positions, original_cell, 
                                                     cell_factor)
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        (energy, 
         atoms_forces, 
         atoms_frac_grads,
         stress) = model.calculate(atoms, fractions=fractions, with_stress=True)
       
       
        writer.set_atoms(atoms=atoms, fractions=fractions, energy=energy, gradients=atoms_forces) 
         
        deformed_forces, deformed_virial = UnitCellHandler.forces_real_to_deformed(atoms, atoms_forces,
                                                                                   stress, original_cell, 
                                                                                   cell_factor)

        deformed_virial = UnitCellHandler.apply_cell_mask(deformed_virial, self.opt_cell_mask)  

    
        transformed_deformed_forces = CoordinateTransformer.coord_gradients_real_to_transformed(deformed_forces, 
                                                                                                self.coord_rescale)
                                             
        transformed_atoms_frac_grads=CoordinateTransformer.fraction_gradients_real_to_transformed(atoms_frac_grads, 
                                                                                                  self.fraction_rescale)
        
        derivatives=ICEParamsHandler.pack_params(natoms, len(self.elements), 
                                                 transformed_deformed_forces,  
                                                 transformed_atoms_frac_grads, 
                                                 deformed_virial)   
        
        energy_rescale, derivatives_rescale=self.rescale_output(energy, derivatives)

        return (energy_rescale , np.array(derivatives_rescale))     
            

    def rescale_output(self, energy, derivatives):
        """ Rescale the energy and the derivatives by a constant """
        energy = energy  *   self.derivative_modulation
        derivatives = derivatives  * self.derivative_modulation
        return energy, derivatives
    
    
    def constrain_and_minimize(self, atoms, model, writer, fractions, 
                               frac_lims, frac_cindex, steps):
        """
        Method to initiate and run the optimizer

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to optimize
        model : BEACON Model
            Model to predict energies
        writer : OptimizationWriter object
            Object to write trajectory files
        fractions : numpy.array
            The chemical fractions
        frac_lims : numpy.array
            The upper and lower limits for atomic existence
        frac_cindex: list of ints
            Indices of atoms with fixed chemical fractions
        steps : int
            The number of optimization steps

        Returns
        -------
        success : bool
            True if relaxation converged, else False
        atoms : ase.Atoms
            The relaxed atoms
        fractions: nympy.array
            The relaxed chemical fractions
        """
        natoms=len(atoms)
        
        transformed_positions = CoordinateTransformer.positions_real_to_transformed(atoms.positions, 
                                                                                    self.coord_rescale)

        transformed_fractions=CoordinateTransformer.fractions_real_to_transformed(fractions, self.fraction_rescale)
        

        params=ICEParamsHandler.pack_atomic_params(natoms, len(self.elements), 
                                                   transformed_positions, 
                                                   transformed_fractions)  
 
    
        linear_constraints=self.get_constraints(atoms, fractions, 
                                                frac_cindex, frac_lims) 

        result = minimize(self._calculate_properties,   
                          params,
                          args=(writer, atoms, model),
                          method='SLSQP',
                          constraints=linear_constraints,
                          jac=True,
                          options={'ftol':self.fmax, 'maxiter': steps},
                          callback=writer.write_atoms)

        success = result['success']
        opt_array = result['x']  


        (transformed_positions, 
         transformed_fractions) = ICEParamsHandler.unpack_atomic_params(natoms, 
                                                                        len(self.elements), 
                                                                        opt_array)

        positions = CoordinateTransformer.positions_transformed_to_real(transformed_positions, 
                                                                        self.coord_rescale)
        
        atoms.positions=positions
        
        fractions=CoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)                                                                            
                                                                                   
        atoms.positions=positions
           
        
        return success, atoms, fractions    




    def constrain_and_minimize_unitcell(self, atoms, model, writer, fractions, 
                                        frac_lims, frac_cindex, steps):
        """
        Method to initiate and run the optimizer, when the unit cell is also
        optimized. See method constrain_and_minimize for parameter explanation
        """
        natoms=len(atoms)
        original_cell=atoms.get_cell()
        
        cell_factor=self.cell_rescale*float(natoms) 
        
        transformed_fractions=CoordinateTransformer.fractions_real_to_transformed(fractions, self.fraction_rescale)
                
        deformation_tensor, deformed_positions = UnitCellHandler.atoms_real_to_deformed(atoms, original_cell, cell_factor)

        transformed_deformed_positions = CoordinateTransformer.positions_real_to_transformed(deformed_positions, 
                                                                                             self.coord_rescale)

        params=ICEParamsHandler.pack_params(natoms, len(self.elements), 
                                            transformed_deformed_positions, 
                                            transformed_fractions, 
                                            deformation_tensor)   
        
        linear_constraints=self.get_constraints(atoms, fractions, 
                                                frac_cindex, frac_lims)
        
        result = minimize(self._calculate_properties_unitcell,   
                          params,
                          args=(writer, atoms, model, original_cell, cell_factor),
                          method='SLSQP',
                          constraints=linear_constraints,
                          jac=True,
                          options={'ftol':self.fmax, 'maxiter': steps},
                          callback=writer.write_atoms)

        success = result['success']
        opt_array = result['x']  
      

        (transformed_deformed_positions, 
         transformed_fractions,
         deformation_tensor) = ICEParamsHandler.unpack_params(natoms, 
                                                              len(self.elements), 
                                                              opt_array) 

        deformed_positions = CoordinateTransformer.positions_transformed_to_real(transformed_deformed_positions, 
                                                                                 self.coord_rescale)    
                                                                                             
        fractions=CoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
    
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, 
                                                     deformed_positions, original_cell, 
                                                     cell_factor)
           
        
        return success, atoms, fractions    

    def get_constrained_atoms(self, atoms):
        """ Get the indices of all atoms with fixed positions """
        pos_cindex = []
        for C in atoms.constraints:
            if isinstance(C, FixAtoms):
                pos_cindex=C.index
        return pos_cindex


    def get_constraints(self, atoms, fractions, frac_cindex, frac_lims):
        """
        Method to generate constraints for minimizer routine

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to optimize
        fractions : numpy.array
            The chemical fractions
        frac_cindex: list of ints
            Indices of atoms with fixed chemical fractions
        frac_lims : numpy.array
            The upper and lower limits for atomic existence

        Returns
        -------
        constraints: tuple
            Object containing a constraint matrix A signifying what 
            degrees of freedom belong the the constraints set by lower and
            upper bound values
        """
        dims=3            
        ndf = dims + len(self.elements)
        
        constraints = SurrOptConstr.constrain_fractions(atoms, 
                                                        self.elements, 
                                                        ndf,
                                                        dims,
                                                        fractions, 
                                                        self.ice_elements, 
                                                        self.n_real, 
                                                        frac_cindex,
                                                        frac_lims, 
                                                        self.with_unit_cell)
        if self.fraction_rescale != 1:
            constraints=CoordinateTransformer.transform_constraints(constraints, self.fraction_rescale)

        pos_cindex=self.get_constrained_atoms(atoms)
        
        if len(pos_cindex):
            position_constraints = SurrOptConstr.constrain_positions(atoms, 
                                                                     ndf, 
                                                                     dims, 
                                                                     pos_cindex, 
                                                                     self.with_unit_cell)
            if self.coord_rescale != 1:
                position_constraints=CoordinateTransformer.transform_constraints(position_constraints, self.coord_rescale)
                position_constraints=position_constraints[0]
                
            constraints.append(position_constraints)
            
        return tuple(constraints)


class CoordinateTransformer:

    """
    Static class to handle stretching of the energy surface with respect to 
    coordinates and elemental fractions in the relaxation process.
    Also responsible for accordingly changing constraints.
    """
    
    @staticmethod
    def fractions_real_to_transformed(fractions, fraction_rescale):
        """ Rescale chemical fractions """
        transformed_fractions=fractions*fraction_rescale
        return transformed_fractions
    
    @staticmethod
    def fractions_transformed_to_real(transformed_fractions, fraction_rescale):
        """ Convert rescaled chemical fractions back to standard values """
        fractions=transformed_fractions/fraction_rescale
        return fractions

    @staticmethod
    def fraction_gradients_real_to_transformed(fraction_gradients, fraction_rescale):
        """ Rescale deritivates w.r.t fractions to match rescaled values """
        transformed_fraction_gradients=fraction_gradients/fraction_rescale   
        return transformed_fraction_gradients
    
    @staticmethod  # for testing
    def fraction_gradients_transformed_to_real(transformed_fraction_gradients, fraction_rescale):
        """ Convert rescaled deritivates w.r.t fractions back to standard values """
        fraction_gradients=transformed_fraction_gradients*fraction_rescale
        return fraction_gradients
     
    @staticmethod
    def positions_real_to_transformed(positions, coord_rescale):
        """ Rescale atomic positions """
        transformed_positions=positions*coord_rescale
        return transformed_positions
    
    @staticmethod
    def positions_transformed_to_real(transformed_positions, coord_rescale):
        """ Convert rescaled atomic positions back to standard values """
        positions=transformed_positions/coord_rescale
        return positions

    @staticmethod
    def coord_gradients_real_to_transformed(gradients, coord_rescale):
        """ Rescale deritivates w.r.t positions to match rescaled values """
        transformed_gradients=gradients/coord_rescale
        return transformed_gradients
    
    
    @staticmethod # for testing
    def coord_gradients_transformed_to_real(transformed_gradients, coord_rescale):
        """ Convert rescaled deritivates w.r.t positions back to standard values """
        gradients=transformed_gradients*coord_rescale
        return gradients

    @staticmethod 
    def transform_constraints(linear_constraints, rescale_constant):
        """ Transform constraints to match rescaled values """
        
        if not isinstance(linear_constraints, list):
            linear_constraints = [linear_constraints]
        
        transformed_constraints=[]
        for constraint in linear_constraints:
            transformed_A = constraint.A.copy()
            transformed_lb = constraint.lb * rescale_constant
            transformed_ub = constraint.ub * rescale_constant
            transformed_constraints.append(LinearConstraint(transformed_A, 
                                                            transformed_lb, 
                                                            transformed_ub))
        return transformed_constraints
    
     
    
class SurrOptConstr:
    """
    Static class to handle setting of constraints for the optimizer process
    """
    @staticmethod
    def constrain_fractions(atoms, elements, ndf, dims, fractions, ice_elements, 
                            n_real, frac_cindex, frac_lims, with_unit_cell):
        """
        Method to generate the full set of constraints
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms under consideration
        elements : list of strings
            list containing the element labels as strings
        ndf : int
            Number of degrees of freedom
        dims : int
            Number of spatial dimensions
        fractions : numpy.array
            The chemical element fractions
        ice_elements : list of bools
            Lists of bools describing what elemens belong to the same ICE-Groups
        n_real : list of floats 
            The real atomic existence for each element
        frac_cindex : list of ints
            List giving the index of atoms 
        frac_lims : list of two floats
            The minimum and maximum values chemical fractions van have. 
            max is always 1.   min may be 0 or a 1>>lower_limit>0
        with_unit_cell : bool
            If the unit cell is also optiimized.

        Returns
        -------
        constraints : constraints object
            Set of upper and lower bounds (lb, ub) constrains and a constraint 
            matrix (A) describing what  degrees of freedom are affected by 
            the constraint limits. A is here a matrix with as many rows as
            the system has constraints. Each row is as long as the total 
            number of degrees of freedom. All row entries are 0 or 1, with
            1 meaniing the degree of freedom is involved. There are equality
            and inequality constraints describied respectively as
            lb=Ax=ub  and lb<=Ax<=ub  where x is our parameters. 
            Hence, quantities like positions, can be fixed by setting lb=ub.
            The output is understandable by the scipy minimizer.
        """
                
        natoms=len(atoms)
        nelements=len(elements)
        
        fractional_atoms = ( len(atoms)>len(frac_cindex) )
        
        
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, n_real, elements)
        
        full_ice_elements = AtomsConverter.get_full_ice_elements(atoms, elements, 
                                                                 ice_elements)
        
        assert(len(full_ice_elements)==len(elements))        
        assert(len(ghost_elements)==len(elements))
        
        full_ice_mask=AtomsConverter.get_fractional_mask(atoms, elements, 
                                                         full_ice_elements, 
                                                         constrained_fractions=frac_cindex) 

        ghost_not_ice_elements=list(map(and_, np.logical_not(full_ice_elements), ghost_elements)) 
        
        constraints=[]
        
        A_frac, lb_frac, ub_frac = SurrOptConstr.setup_fractions_constraints(natoms, ndf, dims, 
                                                                             nelements, fractions, 
                                                                             with_unit_cell)    
        
        if fractional_atoms and any(full_ice_mask):
            for sub_ice_elements in ice_elements:
                sub_ice_mask_no_fixed=AtomsConverter.get_fractional_mask(atoms, elements, 
                                                                         sub_ice_elements, 
                                                                         constrained_fractions=None) 
                
                c_ni_sub = SurrOptConstr.constrain_number_of_atoms_ice(natoms, ndf,
                                                                       nelements, dims,
                                                                       sub_ice_elements, 
                                                                       ghost_elements, 
                                                                       sub_ice_mask_no_fixed, 
                                                                       n_real, n_ghost, 
                                                                       frac_lims, 
                                                                       with_unit_cell)  
                
                
                sub_ice_mask=AtomsConverter.get_fractional_mask(atoms, elements, 
                                                                sub_ice_elements, 
                                                                constrained_fractions=frac_cindex) 
                

                (c_ei_sub_eq, 
                c_ei_sub_non_eq) = SurrOptConstr.constrain_existence_ice(natoms, ndf, dims, 
                                                                        sub_ice_elements,
                                                                        sub_ice_mask, 
                                                                        ghost_elements,
                                                                        frac_lims,
                                                                        with_unit_cell)
            
                constraints.append(c_ni_sub) 
                constraints.append(c_ei_sub_eq) if c_ei_sub_eq is not None else None
                constraints.append(c_ei_sub_non_eq) if c_ei_sub_non_eq is not None else None

                
                lb_frac, ub_frac = SurrOptConstr.constrain_fractions_ice(natoms, sub_ice_elements,
                                                                         sub_ice_mask, lb_frac, ub_frac)
                
        if fractional_atoms and any(ghost_not_ice_elements):
            
            element_indices=np.where(ghost_not_ice_elements)[0]

            for idx in element_indices:
                sub_ghost_elements=np.zeros(nelements, dtype=bool)
                sub_ghost_elements[idx]=True
                sub_ghost_mask_no_fixed=AtomsConverter.get_fractional_mask(atoms, elements, 
                                                                           sub_ghost_elements, 
                                                                           constrained_fractions=None) 
            
            
                c_ng = SurrOptConstr.constrain_number_of_atoms_ghost(natoms, ndf, nelements, dims,
                                                                     full_ice_elements, sub_ghost_elements, 
                                                                     sub_ghost_mask_no_fixed,          
                                                                     n_real, n_ghost, frac_lims, 
                                                                     with_unit_cell)
                
                sub_ghost_mask=AtomsConverter.get_fractional_mask(atoms, elements, 
                                                                  sub_ghost_elements, 
                                                                  constrained_fractions=frac_cindex) 
                
        
                constraints.append(c_ng)                  

            
                lb_frac, ub_frac = SurrOptConstr.constrain_fractions_ghost(natoms, full_ice_mask,
                                                                           sub_ghost_elements, sub_ghost_mask, 
                                                                           frac_lims, lb_frac, ub_frac)
        
        
        
        
        c_f_eq, c_f_non_eq = SurrOptConstr.separate_constraints(A_frac, 
                                                                lb_frac.flatten(), 
                                                                ub_frac.flatten())
        

        constraints.append(c_f_eq)  if c_f_eq is not None else None
        constraints.append(c_f_non_eq) if c_f_non_eq is not None else None

        return constraints
   


    @staticmethod    
    def constrain_positions(atoms, ndf, dims, cindex, with_unit_cell):
        """
        Method to constrain atomic positions in case any atoms are fixed
        as indicated by the iintegers in cindex
        """             
        natoms=len(atoms)
            
        A=np.zeros( (natoms, ndf) )
        
        A_complete=[]
        
        lb=np.zeros( (len(cindex), 3) )
        ub=np.zeros( (len(cindex), 3) )
        
        for list_idx, atom_idx in enumerate(cindex):
            for coord_idx in range(3):
                A_copy=A.copy()
                A_copy[atom_idx,coord_idx]=1
                A_copy_flat=A_copy.flatten()
                
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 ) 
                    
                A_complete.append(A_copy_flat)
                
            lb[list_idx,0:3]= atoms.positions[atom_idx,:]
            ub[list_idx,0:3] = atoms.positions[atom_idx,:]
            
        return LinearConstraint(A=A_complete,
                                lb=lb.flatten(),
                                ub=ub.flatten())
                    
    
    @staticmethod
    def constrain_fractions_ice(natoms, ice_elements, ice_mask, lb, ub):
        """
        Method to inequality constrain the chemical fractions of atoms 
        belonging to an  ICE group to be between 0 and 1.  
        This is for any single element. 
        """             
        ice_elements=np.array(ice_elements, dtype=bool)
        
        for i in range(natoms):
            
            if ice_mask[i]:
                lb[i, ice_elements] = 0
                ub[i, ice_elements] = 1
        return lb, ub


    @staticmethod
    def constrain_fractions_ghost(natoms, full_ice_mask, ghost_elements, ghost_mask, frac_lims, lb, ub):
        """ 
        Method to inequality constrain the chemical fractions of elements 
        with ghost atoms which do not particpate in any ICE group. 
        """
        for i in range(natoms):
            if ghost_mask[i] and not full_ice_mask[i]:
                lb[i, ghost_elements] = frac_lims[0]            
                ub[i, ghost_elements] = 1
                
        return lb, ub 

    
    @staticmethod
    def setup_fractions_constraints(natoms, ndf, dims, nelements, fractions, with_unit_cell):
        """
        Method to preallocate lower bounds and upper bound vectors (lb, ub) 
        as well as the constraints matrix (A) with all zeroes before filling it.  
        """
        A=np.zeros( (natoms, ndf) )
        
        A_complete=[]
        
        for i in range(natoms):
            for j in range(nelements):
                
                A_copy=A.copy()
                A_copy[i,dims+j]=1
                
                A_copy_flat=A_copy.flatten()
                
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 )   
                    
                A_complete.append(A_copy_flat)
                
        lb = fractions.copy()
        ub = fractions.copy()
                
        return A_complete, lb, ub
    
    
    @staticmethod
    def constrain_number_of_atoms_ice(natoms, ndf, nelements, dims,
                                      ice_elements, ghost_elements, 
                                      ice_mask, n_real, n_ghost, frac_lims, 
                                      with_unit_cell):
        """
        Get equality constraints to fix the total number of atoms
        of each element in the ICE-group specified by ice_elements
        """    

        A = np.zeros( (natoms, ndf) )

        A_complete=[]
        
        lb=[]
        ub=[]

        for i in range( nelements ):
            
            if ice_elements[i]:
                A_copy=A.copy()
                A_copy[ice_mask, dims+i] = 1

            
                if ghost_elements[i]:
                    lb.append(n_real[i]+n_ghost[i]*frac_lims[0])
                    ub.append(n_real[i]+n_ghost[i]*frac_lims[0])
                else:
                    lb.append(n_real[i])
                    ub.append(n_real[i])
                    
                A_copy_flat=A_copy.flatten()
            
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 )   
            
                A_complete.append(A_copy_flat)
            
        pure_ice_elements=SurrOptConstr.check_pure_ice_elements(ice_elements, ghost_elements)
        # This line is to avoid overconstraining the system. 
        # if the total existence of atoms in an ICE-group is fixed and the
        # value of all elemental fractions is constrained to an interval, 
        # also adding constraints of the total elemental existences would
        # lead to overconstraining.
        if pure_ice_elements:
            A_complete.pop()
            lb.pop()
            ub.pop()

        return LinearConstraint(A=A_complete,
                                lb=lb,
                                ub=ub)
    
    @staticmethod 
    def check_pure_ice_elements(ice_elements, ghost_elements):
        """
        Check if any of the elements in an ICE group specified by ice_elements
        also has ghost atoms. 
        Returns True if none of the elements have ghost atoms. 
        """
        
        ice_elements=np.array(ice_elements, dtype=bool)
        ghost_elements=np.array(ghost_elements, dtype=bool)
        
        ice_and_ghost_elements = ( ice_elements==ghost_elements )
        pure_ice_elements= not any(ice_and_ghost_elements[ice_elements])
        return pure_ice_elements
       
       
    @staticmethod
    def constrain_number_of_atoms_ghost(natoms, ndf, nelements, dims,  
                                        full_ice_elements, ghost_elements,  
                                        ghost_mask,          
                                        n_real, n_ghost, frac_lims, 
                                        with_unit_cell):
        """
        Get equality constraints to fix the total atomic existence 
        for elements which are not part of any ICE group
        """
        
        A = np.zeros( (natoms, ndf) )
    
        A_complete=[]
        
        lb=[]
        ub=[]
    
        for i in range( nelements ):   
                            
            if ghost_elements[i] and not full_ice_elements[i]:
                A_copy=A.copy()
                A_copy[ghost_mask, dims+i] = 1
                
                lb.append(n_real[i]+n_ghost[i]*frac_lims[0])
                ub.append(n_real[i]+n_ghost[i]*frac_lims[0])
            
                A_copy_flat=A_copy.flatten()
            
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 )   
            
                A_complete.append(A_copy_flat)
            
        return LinearConstraint(A=A_complete,
                                lb=lb,
                                ub=ub)
    @staticmethod
    def constrain_existence_ice(natoms, ndf, dims,   
                                ice_elements,
                                ice_mask,
                                ghost_elements,
                                frac_lims,
                                with_unit_cell):
        """
        Constrain the total exisence of atoms belonging to an ICE_group.
        If no ghost atoms in the ICE group, the existences will be fixed to 1
        but can be spread aribitrarily over the ICE group elements. 
        If with ghost atoms the existence spead over all elements will 
        have a lower limit of 0 or a value 1>>frac_lims>0.
        """
        ice_elements_ndf=SurrOptConstr.get_ndf_element_mask(dims, ice_elements)
        A = np.zeros( (natoms, ndf) )
        
        A_complete=[]
        
        lb=[]
        ub=[]
                
        pure_ice_elements=SurrOptConstr.check_pure_ice_elements(ice_elements, ghost_elements)

        for i in range( natoms ):
            
            if ice_mask[i]:
                A_copy=A.copy()
                A_copy[i, ice_elements_ndf] = 1
                
                if pure_ice_elements:            
                    lb.append(1)
                    ub.append(1)
                else:
                    lb.append(frac_lims[0])
                    ub.append(1)
                
                A_copy_flat=A_copy.flatten()
            
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 )
                
                A_complete.append(A_copy_flat)
                
                
        (c_ice_ext_eq, 
        c_ice_ext_non_eq)=SurrOptConstr.separate_constraints(A_complete, 
                                                             lb, ub)
        # seprate here as well
        return c_ice_ext_eq, c_ice_ext_non_eq
    
    
    
    
    @staticmethod
    def get_ndf_element_mask(dims, element_mask):
        """
        Make a vector describing the involved degrees of freedom on the atoms
        object. with the first dims entries being the remaining part the
        elements. Entries will only be 1 (active) if the corresponding
        elements are true in element_mask describing an ICE-group.
        """
        ndf_element_mask=np.concatenate( (np.zeros(dims,dtype=int), element_mask) )
        ndf_element_mask=ndf_element_mask.astype(bool)
        return ndf_element_mask
    
    
    @staticmethod
    def separate_constraints(A, lb, ub):
        """
        Separate constraints into equality consstraints and inequality
        constraints, as scipy minimizer requested this. 
        """
        machine_error=np.finfo(float).eps
        bound_dif=np.abs(np.array(lb)-np.array(ub)) 
        
        eq_mask = [bound_dif[i]<2*machine_error for i in range(len(bound_dif))]

        A_eq, A_non_eq = SurrOptConstr.true_false_separate_lists(eq_mask, A)
        lb_eq, lb_non_eq = SurrOptConstr.true_false_separate_lists(eq_mask, lb)
        ub_eq, ub_non_eq = SurrOptConstr.true_false_separate_lists(eq_mask, ub)
        
        
        c_eq=LinearConstraint(A=A_eq, 
                              lb=lb_eq, 
                              ub=ub_eq) if len(A_eq) > 0 else None
        
        c_non_eq=LinearConstraint(A=A_non_eq, 
                                  lb=lb_non_eq, 
                                  ub=ub_non_eq) if len(A_non_eq) > 0 else None
        
        return c_eq, c_non_eq


    @staticmethod 
    def true_false_separate_lists(mask, base_list):
        """
        Separate entries in base_list according to what entries are true
        and false respectively in mask
        """
        assert(len(mask)==len(base_list))
        
        list_t = [base_list[i] for i in range(len(base_list)) if mask[i]]
        list_f = [base_list[i] for i in range(len(base_list)) if not mask[i]]
        
        return list_t, list_f



class OptimizationWriter:   
    
    """
    Class to handle writing of trajectory files for the surrogate relaxation
    process. automatically instantiated and used when using the relax method of 
    ICESurrogateOptimizer.
    
    Examples
    --------
    1 Instantiate 
    >>> wrier=OptimizationWriter(atoms, elements, ice_elements, 
                                 frac_cindex, output_file='opt.xyz')
    2 Set a set of atoms to write
    >>> writer.set_atoms(atoms, fractions, energy, gradients)
    2 Write the atoms set using set_atoms
    >>> writer.write_atoms(params)  (params is here just some dummy import)
    """

    def __init__(self, atoms, elements, ice_elements, frac_cindex, 
                 output_file=None):
        """
        Parameters
        ----------
        atoms: ase atoms object
            Atoms object to write trajectory file for.
            Required
            
        elements: list of strings
            List of elements in atomic system. 
            (stored in ICEInfo object)
            Required
            
        ice_elements: list of lists of strings
            List containing the involved ice groups. 
            (stored in ICEInfo object)
            Required
        
        frac_cindex: list of ints
            List with the index of atoms for which elemental fractions are fixed
            (stored in ICEInfo)
            Rquired
        
        output_file: string
            Custom name for file to write output to.  
            If None, no file is written. 
            Default is None.
            
            
        """
        
        self.atoms = atoms
        self.elements=elements
        self.ice_elements=ice_elements
        self.frac_cindex=frac_cindex
        self.output_file=output_file
        
        if self.output_file is not None:
            # format:
            f = open(self.output_file, 'w')
            f.close()
            
            
    def set_atoms(self, atoms, fractions, energy, gradients):
        """ Set atoms for writing """
        self.atoms = atoms  
        self.fractions=fractions
        self.energy = energy
        self.gradients=gradients


    def write_atoms(self, params):
        """ Write to outout. Only writes if output_file is not None """
        if self.output_file is not None:
            
            atoms = self.atoms.copy()
            
            fractions=self.fractions.copy()
                             
            # convert fractions to atoms
            atoms = AtomsConverter.ice_convert(atoms=atoms,
                                               fractions=fractions,
                                               constrained_fractions=self.frac_cindex,
                                               elements=self.elements,
                                               ice_elements=self.ice_elements)
            
            # convert fractions to existences and save to initial charges
            existence_fractions=AtomsConverter.get_existence_fractions(fractions)
            
            atoms.set_initial_charges(charges=existence_fractions.reshape(len(atoms)))
                        
            results = dict(energy=self.energy,
                           forces=-self.gradients)
            atoms.calc = SinglePointCalculator(atoms, **results)
            
            with warnings.catch_warnings():

                # with EMT, a warning is triggered while writing the
                # results in ase/io/extxyz.py. Lets filter that out:
                warnings.filterwarnings('ignore', category=UserWarning)
                
                atoms.wrap()
                
                atoms.info['fractions'] = self.fractions

                write(self.output_file,
                      atoms,
                      append=True,
                      parallel=False)   

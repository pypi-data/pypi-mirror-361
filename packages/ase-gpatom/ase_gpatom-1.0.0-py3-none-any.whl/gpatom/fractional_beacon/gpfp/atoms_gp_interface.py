#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 14:14:21 2024

@author: casper
"""

import numpy as np
from gpatom.gpfp.atoms_gp_interface import Model, LCBModel

from ase.stress import (full_3x3_to_voigt_6_stress,
                        voigt_6_to_full_3x3_stress)

class FractionalModel(Model):
    
    """
    An interface class to communicate between the Gaussian process, the 
    fingerprint and the database. This model optimizes on the surrogate 
    potential energy only. The class is an extension of the BEACON Model
    class in order to handle prediction on atoms with fractional elemental
    coordinates and must be instantated with ICEGaussianProcess and 
    FractionalFingerprint.
    
    Examples
    --------
    1 Instantiate class
    >>> model=FractonalModel(gp=ICEGaussianProcess, fp=FractionalFingerPrint)
    2 Train a gp from a list of atoms objects
    >>> model.add data_points(train_images)
    3 Get prediction on new structure (with or without stress)
    >>> energy, gradients, (stress) = calculate(atoms, with_stress=True/False)
    4. Fit hyperparameters
    >>> model.fit_hps()
    5. Update fingerprints
    >>> model.update_fps()
    """
    
    
    def calculate(self, atoms, with_stress=False, **kwargs):  
        """
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to predict on 
        with_stress : bool, optional
            If stress should be calculated and outputted 
            Default is False.
        **kwargs : dictionary
            Exrtra parameters to go into prediction of fingerprint, e.g.
            extra_coords and fractions

        Returns
        -------
        energy : float
            The predicted energy
        
        atoms_grads : numpy.array
            The derivatives of the energy w.r.t the atomic coordinates
            
        atoms_frac_grads : numpy.array
            The derivatives of the energy w.r.t elemental fractions
            
        stress : numpy.array
            The predicted stress, only if with_stress is True
        """        

        x=self.new_fingerprint(atoms, **kwargs)
        
        predictions, variance = self.gp.predict(x, get_variance=False) 
                
        if self.gp.use_stress:
            atoms_predictions = predictions[0:-9]
            stress = predictions[-9:].reshape(3,3)
            stress = full_3x3_to_voigt_6_stress(stress)
            
            (energy, 
             atoms_grads, 
             atoms_frac_grads) = self.gp.translate_predictions(atoms_predictions)
            
            return energy, atoms_grads, atoms_frac_grads, stress
        
        (energy, 
         atoms_grads, 
         atoms_frac_grads) = self.gp.translate_predictions(predictions)
            
        if with_stress:
            stress=self.gp.predict_stress(x)
            return energy, atoms_grads, atoms_frac_grads, stress
        
        return energy, atoms_grads, atoms_frac_grads
     


class FractionalLCBModel(LCBModel):
    
    """
    An interface class to communicate between the Gaussian process, the 
    fingerprint and the database. This model optimizes on a LCB 
    acquisition function surface. The class is an extension of the BEACON Model
    class in order to handle prediction on atoms with fractional elemental
    coordinates and must be instantated with ICEGaussianProcess and 
    FractionalFingerprint.
    
    Examples
    --------
    1 Instantiate class
    >>> model=FractonalLCBModel(gp=ICEGaussianProcess, 
                                fp=FractionalFingerPrint,
                                kappa=2)
    2 Initially train a gp from a list of atoms objects
    >>> model.add data_points(train_images)
    3 Get prediction on new structure (with or without stress)
    >>> energy, gradients, (stress) = calculate(atoms, with_stress=True/False)
    4. Fit hyperparameters
    >>> model.fit_hps()    
    5. Update fingerprints
    >>> model.update_fps()
    """
    
    def calculate(self, atoms, with_stress=False, **kwargs):

        """
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to predict on 
        with_stress : bool, optional
            If stress should be calculated and outputted 
            Default is False.
        **kwargs : dictionary
            Exrtra parameters to go into prediction of fingerprint, e.g.
            extra_coords and fractions

        Returns
        -------
        acq : float
            The predicted acquisition function
        
        dacq_r : numpy.array
            The derivatives of the acquisition function 
            w.r.t atomic coordinates
            
        dacq_q : numpy.array
            The derivatives of the acquisition function 
            w.r.t elemental fractions
            
        d_acq_c : numpy.array
            The derivative of the acquisition function 
            w.r.t the cell parameters. only if with_stress is True
        """           

        x=self.new_fingerprint(atoms, **kwargs)
        
        (predictions, 
         variance, 
         dkdx, dkdq) = self.gp.predict(x, get_variance=True, 
                                       return_kgrads=True) 
                                       
        if self.gp.use_stress:
            atoms_predictions = predictions[0:-9]
            stress = predictions[-9:]
            
            (energy, 
             atoms_grads, 
             atoms_frac_grads) = self.gp.translate_predictions(atoms_predictions)
            
            grads=np.concatenate((atoms_grads.flatten(), stress))
            
            unc, acq, dacq_r, dacq_c = self.calculate_acq(x, energy, grads, 
                                                          variance, dkdx)
            
            dacq_q=self.calculate_frac_grads(x, unc, atoms_frac_grads, dkdq)
            
            return acq, dacq_r, dacq_q, dacq_c
                
        (energy, 
         atoms_grads, 
         atoms_frac_grads) = self.gp.translate_predictions(predictions)
        
        grads=atoms_grads.flatten()
        unc, acq, dacq_r = self.calculate_acq(x, energy, grads, 
                                              variance, dkdx)
        
        dacq_q=self.calculate_frac_grads(x, unc, atoms_frac_grads, dkdq)
        
        if with_stress:
            dacq_c=self.calculate_stress(x, unc)
            return  acq, dacq_r, dacq_q, dacq_c
        
        return acq, dacq_r, dacq_q
    
    
    def calculate_frac_grads(self, x, unc, frac_grads, dkdq):
        """
        Calculate the derivatives of the acquisition function w.r.t
        elemental fractions
        """
        if self.gp.use_forces:
            dkdq_Ck = np.einsum('ijk,j->ik', dkdq, self.gp.Ck[:,0])
        else:            
            dkdq_Ck = np.einsum('ijk,i->jk', dkdq, self.gp.Ck)

        dvar_q=-2*dkdq_Ck
            
        dunc_q=1/(2*unc)*dvar_q
               
        dacq_q=frac_grads-self.kappa*dunc_q
      
        return dacq_q
    
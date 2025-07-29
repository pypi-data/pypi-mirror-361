#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 00:31:40 2024

@author: casper
"""

import numpy as np
from ase.stress import (full_3x3_to_voigt_6_stress,
                        voigt_6_to_full_3x3_stress)
    
class UnitCellHandler:
    
    """
    Static class made to handle data restructuring during optmization
    of the unit cell in the Hyperspace, ICE and HSICE optimizers. Its 
    being automatically used inside the respective procedures.
    
    The code is adapted from the ASE UnitCellFilter class.
    
    The code acts by calculating a deformation gradient describing the 
    relation between the original unit cell and a new deformed unit cell. 
    After this the atomic positions, unit cell parameters and the associated
    forces and stresses can be converted between the real and deformed 
    coordinates. The unit cell parameters are also scaled by a constant
    cell_factor to make sure the atomic positiosn and cell parameters scale
    in a numerically stable way. 
    """
    
    @staticmethod
    def deform_grad(original_cell, new_cell):
        """
        Get the deformation gradient describing the relation between the
        original and the new deformed unit cell
        """
        return np.linalg.solve(original_cell, new_cell).T    
    
    @staticmethod
    def atoms_deformed_to_real(atoms, deformation_tensor, deformed_positions, original_cell, cell_factor):
        """ 
        Convert atomic positions and cell parameters from 
        deformed to real coordinates 
        """
        new_deform_grad = deformation_tensor / cell_factor
        
        new_cell=original_cell @ new_deform_grad.T
        
        atoms.set_cell(new_cell, scale_atoms=True) 
        
        real_positions=deformed_positions @ new_deform_grad.T
        
        atoms.set_positions(real_positions)
        
        return atoms
    
    @staticmethod
    def atoms_real_to_deformed(atoms_real, original_cell, cell_factor):
        """
        Convert atomic positions and cell parameters from 
        real to deformed coordinates
        """
        deformation_gradient = UnitCellHandler.deform_grad(original_cell, atoms_real.cell)
        
        deformation_tensor = cell_factor * deformation_gradient
        
        deformed_positions = np.linalg.solve(deformation_gradient,   
                                             atoms_real.positions.T).T   
        
        return deformation_tensor, deformed_positions    
    
    @staticmethod 
    def forces_real_to_deformed(atoms_real, atoms_forces, stress, original_cell, cell_factor):
        """
        Convert atomic position and cell derivatives 
        from real to deformed coordinates
        """
        cur_deform_grad=UnitCellHandler.deform_grad(original_cell, atoms_real.cell) 
        
        deformed_forces = atoms_forces @ cur_deform_grad

        volume = atoms_real.get_volume()

        negative_virial = volume * (voigt_6_to_full_3x3_stress(stress) )      
        
        deformed_virial = np.linalg.solve(cur_deform_grad, negative_virial.T).T     
        
        deformed_virial=deformed_virial / cell_factor
        
        return deformed_forces, deformed_virial
    
    
    @staticmethod  
    def forces_deformed_to_real( deformation_tensor, deformed_forces, deformed_virial, atoms_real, cell_factor):
        """
        Convert atomic position and cell derivatives 
        from deformed to real coordinates
        """
        new_deform_grad = deformation_tensor / cell_factor
        
        forces = np.linalg.solve(new_deform_grad, deformed_forces.T).T 
        
        
        volume=atoms_real.get_volume()
        
        volume_divided_negative_vririal=deformed_virial*cell_factor/volume
        
        stress = volume_divided_negative_vririal @ new_deform_grad.T
        
        stress=full_3x3_to_voigt_6_stress(stress)
        
        return forces, stress
    
    
    @staticmethod 
    def apply_cell_mask(deformed_virial, opt_cell_mask):
        """
        Set derivatives of fixed cell components to zero to make
        sure these cell components don't change
        """
        mask = voigt_6_to_full_3x3_stress(opt_cell_mask)
            
        deformed_virial *= mask
        
        return deformed_virial
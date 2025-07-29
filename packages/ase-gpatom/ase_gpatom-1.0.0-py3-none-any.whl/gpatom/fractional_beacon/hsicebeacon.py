#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 21:51:47 2023

@author: casper
"""
from scipy.optimize import minimize
from scipy.optimize import LinearConstraint

from gpatom.hyperspatial_beacon.hyperspacebeacon import HSParamsHandler, HighDimSurrogateOptimizer

from ase.calculators.singlepoint import SinglePointCalculator

import numpy as np

import warnings

from ase.io import write

from ase.constraints import FixAtoms

from gpatom.fractional_beacon.unitcell_handler import UnitCellHandler

from gpatom.fractional_beacon.icebeacon import (RandomFractionGenerator, AtomsConverter, 
                                                CoordinateTransformer, SurrOptConstr,
                                                ICEParamsHandler)

    
class HSICEParamsHandler:  
    """
    Static class to handle restucturing of coordinate and chemical fraction
    data so it fits the minimizer object and the atoms object respectively.
    
    NB: In the below methods dims is the number of spatial dimensions and 
    nfe stands for number of fractional elements.
    """

    @staticmethod     
    def pack_params(natoms, dims, nfe, position_params, extra_position_params, fraction_params, cell_params):
        """ 
        Convert coordinates, chemical fractions and unit cell from 
        atoms object format to optimizer input format.
        """
        assert np.shape(cell_params)==(3,3)
        atomic_params = HSICEParamsHandler.pack_atomic_params(natoms, dims, nfe, position_params, extra_position_params, fraction_params)
        params= np.concatenate((atomic_params, cell_params.flatten()), axis=0)
        return params

    @staticmethod 
    def pack_atomic_params(natoms, dims, nfe, position_params, extra_position_params, fraction_params):
        """
        Convert coordinates and chemical fractions from atoms object format 
        to optimizer input format without the unit cell.
        """
        position_params = HSParamsHandler.pack_atomic_params(natoms, dims, position_params, extra_position_params)
        position_params=position_params.reshape(natoms, max(dims,3))
        atomic_params = ICEParamsHandler.pack_atomic_params(natoms, nfe, position_params, fraction_params)
        return atomic_params

    @staticmethod 
    def unpack_params(natoms, dims, nfe, params):
        """ 
        Convert coordinates, chemical fractions and unit cell values 
        from optimizer input/output  format to atoms object format.
        """
        atomic_params=params[0:-9]
        cell_params=params[-9::].reshape(3,3)
        position_params, extra_position_params, fraction_params = HSICEParamsHandler.unpack_atomic_params(natoms, dims, nfe, atomic_params)
        return position_params, extra_position_params, fraction_params, cell_params

    @staticmethod 
    def unpack_atomic_params(natoms, dims, nfe, params):
        """ 
        Convert coordinates and chemical fractions from optimizer input/output 
        format to atoms object format without the unit cell values.
        """
        spatial_dims=max(dims,3)
        ndf=spatial_dims+nfe
        atomic_params=params.reshape(natoms, ndf)
        coord_params = atomic_params[:, : spatial_dims]
        fraction_params=atomic_params[:, spatial_dims::]
        position_params, extra_position_params = HSParamsHandler.unpack_atomic_params(natoms, dims, coord_params)   
        return position_params, extra_position_params, fraction_params
    

class HSICESurrogateOptimizer(HighDimSurrogateOptimizer):    
    
    """
    Class for optimization of atomic coordinates and elemental fractions. 

    Examples
    --------
    >>> opt=ICESurrogateOptimizer(ice_info, randomtype=..., rng=...)
    >>> opt.relax(atoms, model, file_identifier)
            if random_fraction_generator is none, atoms must carry
            the properties fractions, extra_coords and world_center.
            These properties will be automatcally set if using the
            HighDimRandomStructureAndFractionGenerator.
            Model should be FractionalModel or FractionalLCBModel
    """
    
    def __init__(self, ice_info,
                 fmax=0.05, 
                 cycles=50,
                 relax_steps=5, 
                 weak_existing_steps=0,
                 after_steps=50, 
                 post_rounding_steps=50, 
                 to_dims=3,  
                 strength_array=None,
                 with_unit_cell=False, 
                 fixed_cell_params=None, 
                 rattle_strength=0.05, 
                 rattle_rng=np.random,
                 squeeze_criterion=0.01,
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
            for creation and relaxation of the chemical fractions.
            Required
            
        fmax: float
            The convergence criteria. Criteria stops relaxation
            if the energy of two consequtive relaxations are smaller than fmax.
            Default is 0.001
            
        cycles: int
            The number of cycles in which the hyperspatial 
            penalty potential is gradually increased.
            Default is 50
        
        relax_steps: int
            Number of relaxation steps in each cycle 
            Default is 5
        
        weak_existing_steps: int 
            Number of steps taken with optimization of atomic fractions, 
            where the lower existence level of atoms has a lower limit 
            (stored in ice_info) to make sure ghost atoms stay active. 
            Only usefull when running with ghost atoms
            Default is 0
            
        after_steps: int
            Number of steps taken with optimization of atomic fractions, with
            lower existence level 0. This comes after the weak existing steps
            Default is 50
            
        post_rounding_steps: int
            Number of steps taken where the elemental fractions are fixed to 
            0 or 1 to imitate a normal relaxation. 
            Default is 50
            
        to_dims: int
            The number of spatial dimensions the atoms object is optimized into.
            options include 1,2 and 3
            Default is 3   
        
        strength_array: numpy.array, optional
            The values for the penanlty array. Must have the same lengths
            as the number of cycles. If None a power function 
            p=a*b**cycle starting at 0.1 and ending at 1000 is set up.
            Default is None
            
        with_unit_cell: bool, optional
            If the unit cell should be optimized
            Default is False
            
        fixed_cell_params: list of 6 bools, optional
            Bool giving what voight components of the cell is not optimized.
            Voight form: xx, yy, zz, yz, xz, xy
            Default is [False, False, False, False, False, False]
            
        rattle_strength: float, optional
            Strength by which atoms are rattled in the projection process to make
            sure all atoms can be squeezed into the physial realm if two
            atoms are stacked on top of each other. Mainly a technicality
            Default is 0.05 
            
        rattle_rng: random number generator, optional
            Random number generaor to make sure the rattle process is reproducible
            Default is np.random (not reproducible)
            
        squeeze_criterion: float, optional
            The size for the hyperspatial coordinates at which atoms
            are considered to be in 3D so the hyperspatial relaxation 
            process termintes
            Default is 0.01
            
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
            to the cartesian and hyperspatal coordinates. 
            A larger value mean more stretching and hence
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
        super().__init__(fmax=fmax, relax_steps=relax_steps, after_steps=after_steps, 
                         cycles=cycles, to_dims=to_dims, strength_array=strength_array, 
                         with_unit_cell=with_unit_cell, fixed_cell_params=fixed_cell_params, 
                         rattle_strength=rattle_strength, rattle_rng=rattle_rng,
                         squeeze_criterion=squeeze_criterion)

        self.rfg = random_fraction_generator
                
        (self.elements,
        self.ice_elements,
        self.n_real,
        self.frac_lims,
        self.frac_cindex) = ice_info.get_info()
    
        self.fmax = fmax*derivative_modulation
        self.relax_steps = relax_steps
        
        self.post_rounding_steps=post_rounding_steps
        self.weak_existing_steps=weak_existing_steps
        self.derivative_modulation=derivative_modulation
        self.fraction_rescale=fraction_rescale
        self.coord_rescale=coord_rescale
        self.cell_rescale=cell_rescale
        
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
                            
        h_coords=atoms.extra_coords
    
        from_dims=HSParamsHandler.get_dimension_from_exra_coords(h_coords)
            
        self.set_world_center(atoms.world_center, from_dims)
        
        model.gp.set_dims(self.from_dims)
        n_ghost, ghost_elements = AtomsConverter.get_n_ghost(atoms, self.n_real, self.elements) 
        model.gp.set_n_ghost(n_ghost)
        
        if self.rfg is not None:
            fractions = self.rfg.get_fractions(atoms)
        else:
            fractions=atoms.fractions
                
        writer=self.initiate_writer(atoms, h_coords, fractions, model,
                                    output_file=output_file)
        
        # put atoms to low dimensions while relaxing fractions        
        if self.cycles>0:
           success, atoms, fractions = self.penalty_relax(atoms, h_coords,
                                                          fractions, model,
                                                          writer)


        model.gp.set_dims(self.to_dims)
        
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
            
        self.make_frame(writer, model, self.to_dims, whole_atoms)
                
        return whole_atoms, success
    
    
    def initiate_writer(self, atoms, extra_coords, fractions, model, 
                        output_file=None):
        """ Setts up the writer class and gathers the first writing point """
        
        writer = OptimizationWriter(atoms=atoms,
                                    elements=self.elements,
                                    ice_elements=self.ice_elements,
                                    frac_cindex=self.frac_cindex,
                                    coord_center=self.coord_center,
                                    output_file=output_file)
    
        self.make_frame(writer, model, self.from_dims, atoms, extra_coords, fractions)
        
        return writer
    
    
    def make_frame(self, writer, model, dims, atoms, extra_coords=None, fractions=None):
        """ Write a frame of the to the output file using the writer """
        if fractions is None:
            fractions=AtomsConverter.atoms2fractions(atoms, self.elements)    
           
        (energy, 
         atoms_forces,
         fraction_grads) = model.calculate(atoms, extra_coords=extra_coords, 
                                           fractions=fractions, with_stress=False)

        grads, extra_grads=HSParamsHandler.get_real_and_extra(len(atoms), dims, atoms_forces)
                 
        writer.set_atoms(atoms=atoms, extra_coords=extra_coords, 
                         fractions=fractions, energy=energy, gradients=grads)
        
        writer.write_atoms(energy)    

    
    
    def penalty_relax(self, atoms, h_coords, fractions, model, writer):
        """
        Performs hyperspatial relaxation of atoms including a penalizing
        potential to squeeze atoms out of the hyperspatial dimensions.
        The procedure stops when all exensions into the hyperspatial 
        dimensions are lower than squeeze_criterion.
        """
        self.steps_taken=0
        for i in range(self.cycles):
        
            success, atoms, h_coords, fractions = self.relax_method(atoms, model, 
                                                                    writer, self.from_dims,
                                                                    extra_coords=h_coords,
                                                                    fractions=fractions,
                                                                    frac_lims=self.frac_lims,
                                                                    frac_cindex=self.frac_cindex,
                                                                    steps=self.relax_steps, 
                                                                    penalize=True)

            self.steps_taken+=1
            terminate=self.terminate_dimensional_squeezing(atoms, h_coords)
            if terminate:
                break
            
        if self.from_dims == self.to_dims:
            atoms.info['squeeze_complete']=None
        else:
            atoms.info['squeeze_complete']=terminate
            
            
            
        if self.to_dims==3 or self.to_dims==self.from_dims:
            projected_atoms=atoms
        else:
            projected_atoms=self.project_atoms(atoms)
            
        if self.rattle_strength>0:
            projected_atoms=self.rattle_close_atoms(projected_atoms)
            

        return success, projected_atoms, fractions


    def ghost_relax(self, atoms, fractions, model, writer):
        """
        Relax atomic positions and chemical fractons in the model with
        all atomic existences between 1>>lower_lim>0 and 1. 
        Eventually write out optmization steps
        """
        success, atoms, h_coords, fractions = self.relax_method(atoms, model, 
                                                                writer, self.to_dims,
                                                                extra_coords=None,
                                                                fractions=fractions,
                                                                frac_lims=self.frac_lims,
                                                                frac_cindex=self.frac_cindex,
                                                                steps=self.weak_existing_steps, 
                                                                penalize=False)
        return success, atoms, fractions 


    def projected_relax(self, atoms, fractions, model, writer):
        """
        Relax atomic positions and chemical fractons in the model with
        all atomic existences between 0 and 1. 
        Eventually write out optmization steps
        """
        # relax atoms still with fractional atoms but where ghosts can go to zero
        success, atoms, h_coords, fractions = self.relax_method(atoms, model, 
                                                                writer, self.to_dims,
                                                                extra_coords=None, 
                                                                fractions=fractions,
                                                                frac_lims=[0,1], 
                                                                frac_cindex=self.frac_cindex,
                                                                steps=self.after_steps, 
                                                                penalize=False)
        return success, atoms, fractions        
        
    

    def round_relax(self, atoms, model, writer): 
        """
        Relax atomic positions only after all chemical fractions has been
        rounded to 0 or 1. 
        Eventually write out optmization steps
        """
        whole_fractions=AtomsConverter.atoms2fractions(atoms, self.elements)
        success, atoms, h_coords, fractions = self.relax_method(atoms, model, 
                                                                writer, self.to_dims,
                                                                extra_coords=None, 
                                                                fractions=whole_fractions,
                                                                frac_lims=[0, 1],
                                                                frac_cindex=np.arange(len(atoms)),
                                                                steps=self.post_rounding_steps, 
                                                                penalize=False) 
        
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
            these include: the writer object, the atoms object,
            the model potential,  the total number of dimensions, a bool
            describing if a hyperspatial penalty should be used or not
            
        Returns
        -------
        float
            The energy
        
        numpy.array 
            The derivatives of the energy w.r.t all atomic coordinates and 
            chemical fractions
        """    
        writer = args[0]
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        dims=args[3]
        
        penalize=args[4]
        
        (transformed_positions, 
         transformed_extra_coords, 
         transformed_fractions) = HSICEParamsHandler.unpack_atomic_params(natoms, dims,
                                                                          len(self.elements), 
                                                                           params)      
                                                                            
        positions, extra_coords=HSCoordinateTransformer.positions_transformed_to_real(transformed_positions, 
                                                                                      transformed_extra_coords, 
                                                                                      self.coord_rescale)

        fractions=HSCoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
        
        atoms.positions = positions
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        penalty_coords = HSParamsHandler.get_penalty_params(natoms, dims, self.to_dims, 
                                                            atoms.positions, extra_coords)
               
        (energy, 
         atoms_forces, 
         atoms_frac_grads) = model.calculate(atoms, extra_coords=extra_coords, 
                                             fractions=fractions, with_stress=False)
        
        if penalize:
            energy, atoms_forces =self.hs_penalize(energy, atoms_forces, penalty_coords)    

        d3_forces, extra_forces=HSParamsHandler.get_real_and_extra(natoms, dims, atoms_forces)
        writer.set_atoms(atoms=atoms, extra_coords=extra_coords, fractions=fractions, energy=energy, gradients=atoms_forces) 
         
        (transformed_d3_forces, 
         transformed_extra_forces) = HSCoordinateTransformer.coord_gradients_real_to_transformed(d3_forces, extra_forces, self.coord_rescale)
        
        transformed_atoms_frac_grads=HSCoordinateTransformer.fraction_gradients_real_to_transformed(atoms_frac_grads, self.fraction_rescale)
        
        
        derivatives=HSICEParamsHandler.pack_atomic_params(natoms, dims, len(self.elements), 
                                                          transformed_d3_forces, 
                                                          transformed_extra_forces, 
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
            the model potential,  the total number of dimensions, a bool
            describing if a hyperspatial penalty should be used or not,
            the original unit cell, a scaling factor for the cell coordinates
            
        Returns
        -------
        float
            The energy
        
        numpy.array 
            The derivatives of the energy w.r.t all atomic coordinates, 
            chemical fractions and cell parameters
        """ 
        writer = args[0]
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        dims=args[3]
        
        penalize=args[4]
        
        original_cell=args[5]
        cell_factor=args[6] 
        
        (transformed_deformed_positions, 
         transformed_extra_coords, 
         transformed_fractions, 
         deformation_tensor) = HSICEParamsHandler.unpack_params(natoms, dims,
                                                                len(self.elements), 
                                                                params)
                                                                  
        deformed_positions, extra_coords=HSCoordinateTransformer.positions_transformed_to_real(transformed_deformed_positions, 
                                                                                               transformed_extra_coords, 
                                                                                               self.coord_rescale)
                                                                                    
        fractions=HSCoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
                                                                  
                                                                  
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, 
                                                     deformed_positions, original_cell, 
                                                     cell_factor)
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        penalty_coords = HSParamsHandler.get_penalty_params(natoms, dims, self.to_dims, 
                                                            atoms.positions, extra_coords)
        
        (energy, 
         atoms_forces, 
         atoms_frac_grads,
         stress) = model.calculate(atoms, extra_coords=extra_coords, 
                                   fractions=fractions, with_stress=True)
        
        if penalize:
            energy, atoms_forces =self.hs_penalize(energy, atoms_forces, penalty_coords)    
    
        d3_forces, extra_forces=HSParamsHandler.get_real_and_extra(natoms, dims, atoms_forces)
        
        writer.set_atoms(atoms=atoms, extra_coords=extra_coords, fractions=fractions, energy=energy, gradients=atoms_forces) 
         
        deformed_d3_forces, deformed_virial = UnitCellHandler.forces_real_to_deformed(atoms, d3_forces, 
                                                                                      stress, original_cell, 
                                                                                      cell_factor)

        deformed_virial = UnitCellHandler.apply_cell_mask(deformed_virial, self.opt_cell_mask)  

    
        (transformed_deformed_d3_forces, 
         transformed_extra_forces) = HSCoordinateTransformer.coord_gradients_real_to_transformed(deformed_d3_forces, 
                                                                                                 extra_forces, 
                                                                                                 self.coord_rescale)
                                             
        transformed_atoms_frac_grads=HSCoordinateTransformer.fraction_gradients_real_to_transformed(atoms_frac_grads, 
                                                                                                    self.fraction_rescale)
        
        derivatives=HSICEParamsHandler.pack_params(natoms, dims, len(self.elements), 
                                                   transformed_deformed_d3_forces, 
                                                   transformed_extra_forces, 
                                                   transformed_atoms_frac_grads, 
                                                   deformed_virial)   
        
        energy_rescale, derivatives_rescale=self.rescale_output(energy, derivatives)

        return (energy_rescale , np.array(derivatives_rescale))     
            

    def rescale_output(self, energy, derivatives):
        """ Rescale the energy and the derivatives by a constant """
        energy = energy  *   self.derivative_modulation
        derivatives = derivatives  * self.derivative_modulation
        return energy, derivatives
    
    
    def constrain_and_minimize(self, atoms, model, writer, dims, extra_coords, 
                               fractions, frac_lims, frac_cindex, steps, penalize):
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
        dims: int
            The total number of spatial dimensions
        extra_coords: numpy.array
            The  hyperspatial coordinates
        fractions : numpy.array
            The chemical fractions
        frac_lims : numpy.array
            The upper and lower limits for atomic existence
        frac_cindex: list of ints
            Indices of atoms with fixed chemical fractions
        steps : int
            The number of optimization steps
        penalize: bool: 
            If hyperspatial coordinates should be penalized.

        Returns
        -------
        success : bool
            True if relaxation converged, else False
        atoms : ase.Atoms
            The relaxed atoms
        extra_positions: numpy.array
            The relaxed hyperspatial coordinates
        fractions: nympy.array
            The relaxed chemical fractions
        """
        
        natoms=len(atoms)
        
        (transformed_positions, 
         transformed_extra_coords) = HSCoordinateTransformer.positions_real_to_transformed(atoms.positions, 
                                                                                           extra_coords, 
                                                                                           self.coord_rescale)

        transformed_fractions=HSCoordinateTransformer.fractions_real_to_transformed(fractions, self.fraction_rescale)
        

        params=HSICEParamsHandler.pack_atomic_params(natoms, dims, len(self.elements), 
                                                     transformed_positions, 
                                                     transformed_extra_coords, 
                                                     transformed_fractions)  
 
    
        linear_constraints=self.get_constraints(atoms, extra_coords, fractions, frac_cindex, frac_lims) 

        result = minimize(self._calculate_properties,   
                          params,
                          args=(writer, atoms, model, dims, penalize),
                          method='SLSQP',
                          constraints=linear_constraints,
                          jac=True,
                          options={'ftol':self.fmax, 'maxiter': steps},
                          callback=writer.write_atoms)

        success = result['success']
        opt_array = result['x']  


        (transformed_positions, 
         transformed_extra_coords, 
         transformed_fractions) = HSICEParamsHandler.unpack_atomic_params(natoms, dims, 
                                                                          len(self.elements), 
                                                                          opt_array)

        positions, extra_positions = HSCoordinateTransformer.positions_transformed_to_real(transformed_positions, 
                                                                                           transformed_extra_coords, 
                                                                                           self.coord_rescale)
        
        atoms.positions=positions
        
        fractions=HSCoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)                                                                            
                                                                                   
        atoms.positions=positions
           
        
        return success, atoms, extra_positions, fractions    




    def constrain_and_minimize_unitcell(self, atoms, model, writer, dims, extra_coords, 
                                        fractions, frac_lims, frac_cindex, steps, penalize):
        """
        Method to initiate and run the optimizer, when the unit cell is also
        optimized. See method constrain_and_minimize for parameter explanation
        """
        natoms=len(atoms)
        original_cell=atoms.get_cell()
        
        cell_factor=self.cell_rescale*float(natoms) 
        
        transformed_fractions=HSCoordinateTransformer.fractions_real_to_transformed(fractions, self.fraction_rescale)
                
        deformation_tensor, deformed_positions = UnitCellHandler.atoms_real_to_deformed(atoms, original_cell, cell_factor)

        (transformed_deformed_positions, 
         transformed_extra_coords) = HSCoordinateTransformer.positions_real_to_transformed(deformed_positions, 
                                                                                           extra_coords, 
                                                                                           self.coord_rescale)

        params=HSICEParamsHandler.pack_params(natoms, dims, len(self.elements), 
                                              transformed_deformed_positions, 
                                              transformed_extra_coords, 
                                              transformed_fractions, 
                                              deformation_tensor)   
        
        linear_constraints=self.get_constraints(atoms, extra_coords, fractions, frac_cindex, frac_lims)
        
        result = minimize(self._calculate_properties_unitcell,   
                          params,
                          args=(writer, atoms, model, dims, penalize, original_cell, cell_factor),
                          method='SLSQP',
                          constraints=linear_constraints,
                          jac=True,
                          options={'ftol':self.fmax, 'maxiter': steps},
                          callback=writer.write_atoms)

        success = result['success']
        opt_array = result['x']  
      

        (transformed_deformed_positions, 
         transformed_extra_positions, 
         transformed_fractions,
         deformation_tensor) = HSICEParamsHandler.unpack_params(natoms, dims, 
                                                                len(self.elements), 
                                                                opt_array) 

        (deformed_positions, 
         extra_positions) = HSCoordinateTransformer.positions_transformed_to_real(transformed_deformed_positions, 
                                                                                transformed_extra_positions, 
                                                                                self.coord_rescale)    
                                                                                             
        fractions=HSCoordinateTransformer.fractions_transformed_to_real(transformed_fractions, self.fraction_rescale)
    
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, 
                                                     deformed_positions, original_cell, 
                                                     cell_factor)
           
        
        return success, atoms, extra_positions, fractions    

    def get_constrained_atoms(self, atoms):
        """ Get the indices of all atoms with fixed positions """
        pos_cindex = []
        for C in atoms.constraints:
            if isinstance(C, FixAtoms):
                pos_cindex=C.index
        return pos_cindex


    def get_constraints(self, atoms, extra_coords, fractions, frac_cindex, frac_lims):
        """
        Method to generate constraints for minimizer routine

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to optimize
        extra_coords: numpy.array
            The hyperspatial coordinates
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

        if extra_coords is not None:
            dims=3+len(extra_coords[0,:])
        else:
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
            constraints=HSCoordinateTransformer.transform_constraints(constraints, self.fraction_rescale)

        pos_cindex=self.get_constrained_atoms(atoms)
        
        if len(pos_cindex):
            position_constraints = HSSurrOptConstr.constrain_positions(atoms, 
                                                                       extra_coords, 
                                                                       ndf, 
                                                                       dims, 
                                                                       pos_cindex, 
                                                                       self.with_unit_cell)
            if self.coord_rescale != 1:
                position_constraints=HSCoordinateTransformer.transform_constraints(position_constraints, self.coord_rescale)
                position_constraints=position_constraints[0]
                
            constraints.append(position_constraints)
            
        
        return tuple(constraints)



class HSCoordinateTransformer(CoordinateTransformer):  
    
    """
    Static class to handle stretching of the energy surface with respect to 
    hyperspatila coordinates in the relaxation process.
    Also responsible for accordingly changing constraints.
    
    Stretching of cartesian positions, chemical fractions and constraint 
    tranformation is handled by the inherited CoordinateTransformer class
    """
     
    @staticmethod
    def positions_real_to_transformed(positions, extra_coords, coord_rescale):
        """
        Rescale hyperspatial coordinates
        """
        transformed_positions=positions*coord_rescale
        if extra_coords is not None:
            transformed_extra_coords=extra_coords*coord_rescale
        else: 
            transformed_extra_coords=None
        return transformed_positions, transformed_extra_coords
    
    @staticmethod
    def positions_transformed_to_real(transformed_positions, transformed_extra_coords, coord_rescale):
        """
        Convert rescaled hyperspatial coordinates back to standard values
        """
        positions=transformed_positions/coord_rescale
        if transformed_extra_coords is not None:
            extra_coords=transformed_extra_coords/coord_rescale
        else: 
            extra_coords=None
        return positions, extra_coords

    @staticmethod
    def coord_gradients_real_to_transformed(gradients, extra_gradients, coord_rescale):
        """
        Rescale deritivates w.r.t hyperspatial coordinates to match
        rescaled values
        """
        transformed_gradients=gradients/coord_rescale
        if extra_gradients is not None:
            transformed_extra_gradients=extra_gradients/coord_rescale
        else: 
            transformed_extra_gradients=None
        return transformed_gradients, transformed_extra_gradients
    
    
    @staticmethod # for testing
    def coord_gradients_transformed_to_real(transformed_gradients, transformed_extra_gradients, coord_rescale):
        """
        Convert rescaled deritivates w.r.t hyperspatial coordinates 
        back to standard values
        """
        gradients=transformed_gradients*coord_rescale
        if transformed_extra_gradients is not None:
            extra_gradients=transformed_extra_gradients*coord_rescale
        else: 
            extra_gradients=None
        return gradients, extra_gradients
    
    
    

class HSSurrOptConstr:
    
    """
    statiic class to handle constraining of the 3D and hyperspatial 
    atomic coordinates for the SLSQP optimizer
    """    
    
    @staticmethod    
    def constrain_positions(atoms, extra_coords, ndf, dims, cindex, with_unit_cell):
        """
        Method to fix cartesian and hyperspatial coordinates during surrogate
        relaxation for atoms with index included in cindex. 
        
        NB: dims stands for the number of spatial dimensions and 
        ndf stands for number of degrees of freedom. 
        
        See SurroptConstr in ICE Beacon for more info
        """
        natoms=len(atoms)
            
        A=np.zeros( (natoms, ndf) )
        
        A_complete=[]
        
        lb=np.zeros( (len(cindex), dims) )
        ub=np.zeros( (len(cindex), dims) )
        
        for list_idx, atom_idx in enumerate(cindex):
            for coord_idx in range(dims):
                A_copy=A.copy()
                A_copy[atom_idx,coord_idx]=1
                A_copy_flat=A_copy.flatten()
                
                if with_unit_cell:
                    A_copy_flat=np.concatenate( (A_copy_flat, np.zeros(9)), axis=0 ) 
                    
                A_complete.append(A_copy_flat)
                
            lb[list_idx,0:3]= atoms.positions[atom_idx,:]
            ub[list_idx,0:3] = atoms.positions[atom_idx,:]
            if extra_coords is not None:
                lb[list_idx,3:] = extra_coords[atom_idx,:]
                ub[list_idx,3:] = extra_coords[atom_idx,:]
            
        return LinearConstraint(A=A_complete,
                                lb=lb.flatten(),
                                ub=ub.flatten())
    
    
class OptimizationWriter:   

    """
    Class to handle writing of trajectory files for the surrogate relaxation
    process. automatically instantiated and used when using the relax method of 
    HighDimSurrogateOptimizer. 
    
    Examples
    --------
    1 Instantiate 
    >>> wrier=OptimizationWriter(atoms, ..., output_file='opt.xyz')
    2 Set a set of atoms to write
    >>> writer.set_atoms(atoms, extra_coords, dims, energy, gradients)
    2 Write the atoms set using set_atoms
    >>> writer.write_atoms(params)  (params is here just some dummy import)
    """
    
    

    def __init__(self, atoms, elements, ice_elements, frac_cindex, 
                 coord_center, output_file=None):
        """
        Parameters
        ----------
        atoms: ase atoms object
            Atoms object to write trajectory for.
            Required
            
        elements: list of strings
            List of elements in atomic system. 
            (Stored in ICEInfo object)
            
        ice_elements: list of lists of strings
            List containing the involved ice groups. 
            (Stored in ICEInfo object)
        
        frac_cindex: list of ints
            List with the index of atoms for which elemental fractions are fixed
            (Stored in ICEInfo)
        
        coord_center: numpy array
            An array containing the zero points for all spatial dimensons. 
            Required
            
        output_file: string
            Custom name for file to write output to.  
            If None, no file is written. 
            Default is None.
        """

        self.atoms = atoms
        self.elements=elements
        self.ice_elements=ice_elements
        self.frac_cindex=frac_cindex
        self.output_file = output_file
        self.coord_center=coord_center
        
        if self.output_file is not None:
            # format:
            f = open(self.output_file, 'w')
            f.close()
            
            
    def set_atoms(self, atoms, extra_coords, fractions, energy, gradients):
        """ Set atoms for writing. NB: gradients is only w.r.t positions"""
        self.atoms = atoms  
        self.extra_coords=extra_coords
        self.fractions=fractions
        self.energy = energy
        self.d3_gradients=gradients[:,:3]


    def write_atoms(self, params):
        """ Write to outout. Only writes if output_file is not None """
        if self.output_file is not None:
            
            atoms = self.atoms.copy()
            
            fractions=self.fractions.copy()
                 
            results = dict(energy=self.energy,
                           forces=-self.d3_gradients)
            atoms.calc = SinglePointCalculator(atoms, **results)
            
            # convert fractions to atoms
            atoms = AtomsConverter.ice_convert(atoms=atoms,
                                               fractions=fractions,
                                               constrained_fractions=self.frac_cindex,
                                               elements=self.elements,
                                               ice_elements=self.ice_elements)
            
            # convert fractions to existences and save to initial charges
            existence_fractions=AtomsConverter.get_existence_fractions(fractions)
            
            atoms.set_initial_charges(charges=existence_fractions.reshape(len(atoms)))
            
            # save fourth coordinate to magnetic moments
            if self.extra_coords is not None: 
                atoms.set_initial_magnetic_moments(magmoms=self.extra_coords[:,0]-self.coord_center[0])
        
            
            results = dict(energy=self.energy,
                           forces=-self.d3_gradients)
            atoms.calc = SinglePointCalculator(atoms, **results)
            
            with warnings.catch_warnings():

                # with EMT, a warning is triggered while writing the
                # results in ase/io/extxyz.py. Lets filter that out:
                warnings.filterwarnings('ignore', category=UserWarning)
                
                atoms.wrap()
                
                atoms.info['fractions'] = self.fractions
                if self.extra_coords is None:    
                    atoms.info['extra_coords']='None' 
                else:
                    atoms.info['extra_coords']= self.extra_coords

                write(self.output_file,
                      atoms,
                      append=True,
                      parallel=False)   

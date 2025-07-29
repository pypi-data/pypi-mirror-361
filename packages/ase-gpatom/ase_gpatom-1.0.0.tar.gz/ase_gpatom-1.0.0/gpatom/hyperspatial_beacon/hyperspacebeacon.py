#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 13:28:13 2023

@author: casper
"""

from gpatom.beacon.beacon import SurrogateOptimizer, Checker
import numpy as np
from scipy.optimize import minimize, Bounds
import warnings
from ase.calculators.singlepoint import SinglePointCalculator
from ase.io import write
from ase.neighborlist import NeighborList
from ase.constraints import FixAtoms

from gpatom.fractional_beacon.unitcell_handler import UnitCellHandler

from gpatom.hyperspatial_beacon.constrainer import HSConstrainer


class HighDimSurrogateOptimizer(SurrogateOptimizer):
    """
    Optimizer class to handle optimization of atoms in an arbitrary 
    amount of spatial dimensions.
    
    Examples
    -------- 
    >>> opt=HighDimSurrogateOptimizer(cycles=100, relax_steps=5, after_steps=100)
    >>> opt.relax(self, atoms, model, output_file='opt_hs.xyz')
    
        atoms need to have the attributes extra_coords and world_center
        provided by any HighDim structure generator. Model is just one of the
        standard BEACON Model objects. output_file
        allows for writing a trajectory file with a custom name
    """  
    
    def __init__(self, cycles=100, relax_steps=5, after_steps=50,
                 fmax=0.05, to_dims=3, strength_array=None, 
                 with_unit_cell=False, fixed_cell_params=None, 
                 rattle_strength=0.05, rattle_rng=np.random, 
                 squeeze_criterion=0.01, error_method=None): 
        """
        Parameters
        ----------        
        cycles: int, optional
            The number of cycles in which the hyperspatial 
            penalty potential is gradually increased
            Default is 100
        
        relax_steps: int, optional
            number of relaxation steps in each cycle 
            Default is 5
        
        after_steps: int, optional
            Telaxation steps taken after the hyperspatial optimization
            process is finished and the atoms has been projected into 3D space
            Default is 50
                
        to_dims: int, optional
            The number of spatial dimensions the atoms object is optimized into.
            Options include 1,2 and 3
            Default is 3   

        fmax: float, optonal
            Convergence criteria on the max gradient component
            Default is 0.05    

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
            
        error_method: functons, optional 
            a customly written method whic raises the CustomError from
            BEACON to prematurely terminate a surrogate relaxation
            Default is None      
        """  
        
        assert(to_dims<4)
        
        if strength_array is None:
            end_point=1000
            start_point=0.1
            b=(end_point/start_point)** (1 / ( cycles-1 ))
            a_exp=end_point/(b**cycles)
            strength_array=a_exp*b**np.arange(cycles)
            
        assert len(strength_array)==cycles
        
        self.strength_array=strength_array
            
        self.fmax = fmax
        self.cycles=cycles
        self.relax_steps = relax_steps
        self.after_steps=after_steps
        self.squeeze_criterion=squeeze_criterion
        self.rattle_rng=rattle_rng
        
        self.to_dims=to_dims
        
        self.rattle_strength=rattle_strength            
       
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

    
    def _calculate_properties(self, params, *args):
        """
        Objective function to be minimized when unit cell is not optimized.

        Parameters
        ----------
        params : numpy.array
            Array with all atomic coordinates
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
            The derivatives of the energy w.r.t atomic coordinates 
        """      
        writer = args[0]  
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        dims=args[3]
        penalize=args[4]
        
        positions, extra_coords =  HSParamsHandler.unpack_atomic_params(natoms, dims, params)  
        atoms.positions=positions
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        penalty_coords = HSParamsHandler.get_penalty_params(natoms, dims, self.to_dims, 
                                                            atoms.positions, extra_coords)
        
        energy, atoms_forces = model.calculate(atoms, 
                                               extra_coords=extra_coords, 
                                               with_stress=False)
        
        if penalize:
           energy, atoms_forces = self.hs_penalize(energy, atoms_forces, penalty_coords) 
          
        d3_forces, extra_forces=HSParamsHandler.get_real_and_extra(natoms, dims, atoms_forces)
        writer.set_atoms(atoms=atoms, extra_coords=extra_coords, dims=dims, energy=energy, gradients=atoms_forces) 
         
        derivatives=HSParamsHandler.pack_atomic_params(natoms, self.from_dims, d3_forces, extra_forces)

        return (energy , np.array(derivatives))   
 
    
    def _calculate_properties_unitcell(self, params, *args):
        """
        Objective function to be minimized when unit cell is also optimized.

        Parameters
        ----------
        params : numpy.array
            Array with all atomic coordinates and cell parameters
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
            The derivatives of the energy w.r.t atomic coordinates 
            and cell parameters
        """ 
        writer = args[0]
        atoms = args[1]
        natoms=len(atoms)
        
        model=args[2]
        dims=args[3]
        penalize=args[4]
        
        original_cell=args[5]
        cell_factor=args[6]
              
        deformed_positions, extra_coords, deformation_tensor =  HSParamsHandler.unpack_params(natoms, dims, params)  
        
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, deformed_positions, original_cell, cell_factor)
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        penalty_coords = HSParamsHandler.get_penalty_params(natoms, dims, self.to_dims, 
                                                            atoms.positions, extra_coords)

        (energy, 
         atoms_forces, 
         stress) = model.calculate(atoms, extra_coords=extra_coords, 
                                   with_stress=True)

        if penalize:
           energy, atoms_forces = self.hs_penalize(energy, atoms_forces, penalty_coords)

        d3_forces, extra_forces=HSParamsHandler.get_real_and_extra(natoms, dims, atoms_forces)
        
        writer.set_atoms(atoms=atoms, extra_coords=extra_coords, dims=dims, energy=energy, gradients=atoms_forces) 

        deformed_forces, deformed_virial = UnitCellHandler.forces_real_to_deformed(atoms, d3_forces, stress, original_cell, cell_factor)
        
        deformed_virial = UnitCellHandler.apply_cell_mask(deformed_virial, self.opt_cell_mask)   
         
        derivatives=HSParamsHandler.pack_params(natoms, self.from_dims, deformed_forces, extra_forces, deformed_virial)

        return (energy , np.array(derivatives))        
    

    def hs_penalize(self, energy, atoms_forces, penalty_coords):
        """
        Finds strength value for penalizing potential and adds penalty
        to energy and forces
        """
        strength=self.strength_array[self.steps_taken]
        HS_energy, HS_forces = self.HS_penalty(penalty_coords, strength)
        energy+=HS_energy
        atoms_forces+=HS_forces 
        return energy, atoms_forces

    def HS_penalty(self, penalty_coords, strength):      
        """
        Calculates penalty values to add to energy and forces. 
        """
        penalty_coords_mod=penalty_coords-self.world_center[self.to_dims:self.from_dims]
        
        HS_energy=0
        HS_derivatives=np.zeros((len(penalty_coords) , self.from_dims)) 
         
        for idx, x in enumerate(penalty_coords_mod):
            eng_x=strength * np.linalg.norm(x,axis=0)**2
            HS_energy +=  eng_x 
            HS_derivatives[idx,self.to_dims:] = strength * 2*x
        
        return HS_energy, HS_derivatives


    def constrain_and_minimize(self, atoms, model, writer, dims, h_coords=None, steps=50, penalize=True):
        """
        Method to initiate and run the optimizer

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to optimize
        model : BEACON Model
            Model to predict energies
        writer : OptimizationWriter object
            object to write trajectory files
        dims : int
            Total number of dimensions
        h_coords : numpy.array, optional
            the hyperspatial coordinates, The default is None
        steps : int, optional
            optimization steps. The default is 50.
        penalize : bool, optional
            If a hyperpstial penalty should be used or nor. The default is True.

        Returns
        -------
        success : bool
            True if relaxation converged, else False
        atoms : ase.Atoms
            The relaxed atoms
        extra_coords : nympy.array
            The relaxed hyperspatial coordinates
        """
        natoms=len(atoms)

        params=HSParamsHandler.pack_atomic_params(natoms, self.from_dims, atoms.positions, h_coords)
      
        lb, ub = self.constrain_atoms(atoms, dims)
        
        result = minimize(self._calculate_properties,   
                              params,
                              args=(writer, atoms, model, dims, penalize),
                              method='L-BFGS-B',
                              bounds=Bounds(lb, ub, keep_feasible=False),
                              jac=True,
                              options={'ftol':0, 'gtol':self.fmax, 'eps':1,  'maxiter': steps, 'maxls':20},
                              callback=writer.write_atoms)
                             
        success = result['success']
        
        opt_array = result['x']
     
        positions, extra_coords = HSParamsHandler.unpack_atomic_params(natoms, dims, opt_array)  
        atoms.positions=positions
        
        return success, atoms, extra_coords   


    
    def constrain_and_minimize_unitcell(self, atoms, model, writer, dims, h_coords=None, steps=50, penalize=True):
        """
        Method to initiate and run the optimizer, when the unit cell is also
        optimized. See method constrain_and_minimize for parameter explanation
        """
        natoms=len(atoms)
        original_cell=atoms.get_cell()
        cell_factor=float(natoms)  


        deformation_tensor, deformed_positions = UnitCellHandler.atoms_real_to_deformed(atoms, original_cell, cell_factor)

        params=HSParamsHandler.pack_params(natoms, self.from_dims, deformed_positions, h_coords, deformation_tensor)
      
        lb, ub = self.constrain_atoms(atoms, dims)
        
        result = minimize(self._calculate_properties_unitcell,   
                              params,
                              args=(writer, atoms, model, dims, penalize, original_cell, cell_factor),
                              method='L-BFGS-B',
                              bounds=Bounds(lb, ub, keep_feasible=False),
                              jac=True,
                              options={'ftol':0, 'gtol':self.fmax, 'eps':1,  'maxiter': steps, 'maxls':20},
                              callback=writer.write_atoms)
                             
        success = result['success']
        
        opt_array = result['x']
     
        deformed_positions, extra_coords, deformation_tensor = HSParamsHandler.unpack_params(natoms, dims, opt_array)  
    
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, deformed_positions, original_cell, cell_factor)
        
        return success, atoms, extra_coords              
        

    def constrain_atoms(self, atoms, dims):
        """ Method to fix atoms in the optimizer """
      
        n_atoms=len(atoms)
        n_dims=max(dims,3) 
            
        if self.with_unit_cell:
            lb, ub = HSConstrainer.setup_bounds_unitcell(n_atoms, n_dims)
        else:
            lb, ub = HSConstrainer.setup_bounds(n_atoms, n_dims)
            
        
        lb, ub = HSConstrainer.hs_constrain_atoms(atoms, n_dims, 
                                                  self.world_center, lb, ub)
        
        return lb, ub

        
    def initiate_writer(self, atoms, model, h_coords, output_file=None):
        """ Setts up the writer class and gathers the first writing point """            
        
        writer = OptimizationWriter(atoms=atoms, 
                                    coord_center=self.coord_center,
                                    output_file=output_file)
            
        energy, atoms_forces = model.calculate(atoms, extra_coords=h_coords, 
                                               with_stress=False)
            
        d3_forces, extra_forces=HSParamsHandler.get_real_and_extra(len(atoms), self.from_dims, atoms_forces)
        
        params=HSParamsHandler.pack_params(len(atoms), self.from_dims, atoms.positions, h_coords, atoms.cell)

        writer.set_atoms(atoms=atoms, extra_coords=h_coords, dims=self.from_dims, energy=energy, gradients=atoms_forces) 
        
        writer.write_atoms(params)
        
        return writer

    def set_world_center(self, world_center, from_dims):
        """
        Set the starting dimensionality, the world center, and coordinate center
        to be easier accessible in the code by use of the self command. 
        """
        assert(from_dims>=self.to_dims)
        assert len(world_center)==max(3, from_dims)
        self.from_dims=from_dims
        self.world_center=world_center
        self.coord_center=self.world_center[self.to_dims:self.from_dims]
        
        
    def relax(self, atoms, model, output_file=None):           
        """
        Relaxes atoms in the potential of model and eventually writes
        a trajectory file with name output_file
        
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms to optimize
        model : BEACON Model class
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
        
        writer=self.initiate_writer(atoms, model, h_coords, 
                                    output_file=output_file)
        
        self.steps_taken=0

        
        for i in range(self.cycles):
            success, atoms, h_coords = self.relax_method(atoms, model, 
                                                         writer, self.from_dims,
                                                         h_coords=h_coords,
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
       
        success, opt_atoms, h_coords = self.relax_method(projected_atoms, model, 
                                                         writer, self.to_dims,
                                                         h_coords=None, 
                                                         steps=self.after_steps, 
                                                         penalize=False)
        
        return opt_atoms, success
    
    def terminate_dimensional_squeezing(self, atoms, h_coords):      
        """ 
        Terminate the hyperspatial optimization if all hyperspatial norms
        are below self.squeeze_criterion
        """
        check_coords = HSParamsHandler.get_penalty_params(len(atoms), 
                                                          self.from_dims, self.to_dims, 
                                                          atoms.positions, h_coords)
        
        relative_check_coords=check_coords-self.coord_center
        relative_check_coords_norms=np.linalg.norm(relative_check_coords, axis=1)
        terminate=all(relative_check_coords_norms<self.squeeze_criterion)
        return terminate
            
        
    def project_atoms(self,atoms): 
        """
        If atoms hasnt reached the squeeze criterion during the relaxation, 
        they are projected into self.to_dims space by having their hyperspatial
        coordinates simply set to their world_center coordinate
        """
        
        coords=atoms.get_positions()
                
        if self.to_dims==2:
            coords[:,2:3]=self.world_center[2]*np.ones( (len(atoms),1 ))
        elif self.to_dims==1:
            coords[:,1:3]=self.world_center[1:2]*np.ones( (len(atoms),2 ))
        
        atoms.positions=coords
        
        return atoms
      
        
    def rattle_close_atoms(self, atoms):  
        """
        If two atoms are very close after projecting atoms, they are 
        rattles apart to make subsequent relaxation easier. 
        Too close is being closer than 0.1 from each other
        """
        neighbor_list = NeighborList(0.1*np.ones(len(atoms)), self_interaction=False)     
        
        close_idx=self.get_close_atoms(atoms, neighbor_list)
        
        while len(close_idx)>0:
            atoms=self.rattle_atoms(atoms, close_idx) 
            close_idx=self.get_close_atoms(atoms, neighbor_list)
            
        return atoms
        
       
    def get_close_atoms(self,atoms, neighbor_list):  
        """
        Find atoms that are too close after projecting. 
        """
        close_idx=[]
        
        neighbor_list.update(atoms)
        
        for idx in range(len(atoms)):
            neighbors, offsets = neighbor_list.get_neighbors(idx)
        
            if len(neighbors)>0:
                close_idx.append(idx)
                close_idx.extend(neighbors)
        
        close_idx=np.unique(close_idx)
        return close_idx
        
        
    def rattle_atoms(self,atoms,indices=None):
        """ Rattle the too close atoms """

        if indices is None:
            indices=np.arange(len(atoms))

        pos=atoms.positions
            
        perturb=np.zeros(np.shape(pos))

        perturb[indices,0:self.to_dims:1]=self.rattle_rng.normal(loc=0.0, scale=self.rattle_strength, 
                                                                 size=(len(indices),self.to_dims))
        
        atoms.set_positions(pos + perturb)
                
        return atoms        
        

class HSParamsHandler:
    """
    Static class to handle restucturing of coordinate data
    so it fits the minimizer object and the atoms object respectively.
    Also handles restructuring of coordinate data to go into penalizer method
    """
    
    @staticmethod
    def get_real_and_extra(natoms, dims, atomic_params):
        """ Separate atomic parameters in 3D and hyperspatial values """
        
        assert np.shape(atomic_params)==(natoms,  max(dims,3))
        
        d3_params=atomic_params[:,:3]
        
        if dims>3:
            extra_params=atomic_params[:,3:]
        else:
            extra_params=None
    
        return d3_params, extra_params

    @staticmethod    
    def unpack_params(natoms, dims, params):
        """ 
        Convert coordinates from optimizer input/output format to atoms 
        object format 
        """
        atomic_params=params[0:-9] 
        cell_params=params[-9::].reshape(3,3)

        position_params, extra_position_params = HSParamsHandler.unpack_atomic_params(natoms, dims, atomic_params)
        return position_params, extra_position_params, cell_params
    
    @staticmethod 
    def unpack_atomic_params(natoms, dims, params):
        """ 
        Convert coordinates from optimizer input/output format to atoms 
        object format without the unit cell values
        """
        atomic_params=params.reshape(natoms, max(dims,3))
        if dims>3:       
            position_params = atomic_params[:, :3] 
            extra_position_params = atomic_params[:, 3:]    

        else:
            position_params = atomic_params  
            extra_position_params=None
            
        return position_params, extra_position_params
    
    @staticmethod 
    def get_penalty_params(natoms, dims, to_dims, position_params, extra_position_params):
        """
        Get the part of the atomic coordinates and hyperspatial coordinates
        on which the penalzing potential has to act.
        The normal atomic coordinates can be included id we optimize into
        2 or 1 D space
        """
        atomic_params = HSParamsHandler.pack_atomic_params(natoms, dims, position_params, extra_position_params)
        
        atomic_params=atomic_params.reshape(natoms,max(dims,3))
        
        penalty_position_params=atomic_params[:, to_dims:] 
        
        return penalty_position_params
    
    
    @staticmethod
    def pack_params(natoms, dims, position_params, extra_position_params, cell_params):
        """ 
        Convert coordinates from atoms object format to optimizer input format
        """
        assert np.shape(position_params)==(natoms,3)
        assert np.shape(cell_params)==(3,3)
    
        atomic_params=HSParamsHandler.pack_atomic_params(natoms, dims, position_params, extra_position_params)
            
        params= np.concatenate((atomic_params, cell_params.flatten()), axis=0)
           
        return params
    
    
    @staticmethod 
    def pack_atomic_params(natoms, dims, position_params, extra_position_params):
        """ 
        Convert coordinates from atoms object format to optimizer input format
        withouut unit cell
        """
        if extra_position_params is not None:
            extra_position_params.reshape(natoms, dims-3)
            atomic_params = np.concatenate((position_params, extra_position_params), axis=1).flatten()        
        else:
            atomic_params=position_params.flatten()
        
        return atomic_params
    
    @staticmethod
    def get_dimension_from_params(natoms, atomic_params):
        """ 
        Infer the total amount of dimensions from the the total number 
        of atomic coordinates
        """
        dims=len(atomic_params)/natoms
        return dims
    
    @staticmethod
    def get_dimension_from_exra_coords(extra_coords):
        """
        Infer the total amount of dimensions from the shape of the 
        matrix storing the hyperspaial coordinates
        """
        if extra_coords is None:
            dimension=3
        else:
            dimension = np.shape(extra_coords)[1]+3  # this 3 is the 3 normal dimensions
        return dimension
    

class OptimizationWriter:   
    """
    Class to handle writing of trajectory files for the surrogate relaxation
    process. automatically instantiated and used when using the relax method of 
    HighDimSurrogateOptimizer. 
    
    Examples
    --------
    1 Instantiate 
    >>> wrier=OptimizationWriter(atoms, coord_center, output_file)
    2 Set a set of atoms to write
    >>> writer.set_atoms(atoms, extra_coords, dims, energy, gradients)
    2 Write the atoms set using set_atoms
    >>> writer.write_atoms(params)  (params is here just some dummy import)
    """

    def __init__(self, atoms, coord_center, output_file=None):
        """
        Parameters
        ----------
        atoms: ase.Atoms object
            Atoms object to write trajectory for
            Required
                        
        coord_center: numpy.array
            An array containing the zero points for all spatial dimensons. 
            Required
            
        output_file: string, optional
            Name of output trajectory file, e.g. 'opt_hs.xyz'
            Default is None (no files written)
        """
        
        self.atoms = atoms
        self.coord_center=coord_center
        self.output_file=output_file
        
        if self.output_file is not None:
            f = open(self.output_file, 'w')
            f.close()
            
            
    def set_atoms(self, atoms, extra_coords, dims, energy, gradients):
        """ Set atoms for writing """
        self.atoms = atoms
        self.extra_coords=extra_coords
        self.dims=dims
        self.energy = energy 
        self.d3_gradients=gradients[:,:3]


    def get_hyperdim_color(self, atoms, extra_coords):
        """
        Assign hyperspatial coordinates color in ase gui by saving
        the coordinates in initial_charges and magnetic moments
        """
        if self.dims>3:

            h_coords=extra_coords-self.coord_center
                 
            if self.dims==4: 
                atoms.set_initial_charges(charges=h_coords[:,0]) 
            elif self.dims==5:
                atoms.set_initial_charges(charges=h_coords[:,0])
                atoms.set_initial_magnetic_moments(magmoms=h_coords[:,1])

        return atoms


    def write_atoms(self, params):
        """ Write to outout. Only writes if output_file is not None """
        if self.output_file is not None:
            
            atoms = self.atoms.copy()
     
            results = dict(energy=self.energy,
                           forces=-self.d3_gradients)
            atoms.calc = SinglePointCalculator(atoms, **results)
            
            
            atoms=self.get_hyperdim_color(atoms, self.extra_coords)
            
            
            with warnings.catch_warnings():

                # with EMT, a warning is triggered while writing the
                # results in ase/io/extxyz.py. Lets filter that out:
                warnings.filterwarnings('ignore', category=UserWarning)
                
                atoms.wrap()

                write(self.output_file,
                      atoms,
                      append=True,
                      parallel=False)     


class HighDimChecker(Checker):
    
    """
    Checker class extending the standard BEACON Checker class.
    Only addition compared to the standard Checker is that
    it checks if all atoms in the structure got squeezed into the physical
    space without the need for a forced projection, i.e. by all hyperspatal
    norms being lower than squeeze_criterion in the HighDimSurrogateOptimizer
    class. 
    
    Examples
    --------
    checker=HighDimChecker(check_squeeze=True, dist_limit=..., ...)
    structure_ok, output_strong=checker.check(atoms, distances)

    See Checker for further into
    """
    
    def __init__(self, dist_limit=None, rlimit=None, 
                 disconnect_limit=None,
                 angle_limit=None, volume_limits=None, 
                 check_squeeze=True):
        
        """
        Parameters
        ----------
        
        check_squeeze: bool, optional
            If true, checker will check if all atoms got squeezed into the
            physical realm without the need for a forces projection, i.e. 
            if all hyperspatial coordinates became lower than the dist_limt
            in HighDimSurrogateOpimizer.
            Default is True.
        
        See Checker for other parameters
        """        
        super().__init__(dist_limit=dist_limit, rlimit=rlimit, 
                         disconnect_limit=disconnect_limit,
                         angle_limit=angle_limit, 
                         volume_limits=volume_limits)
        
        self.check_squeeze=check_squeeze
        
    def check(self, atoms, distances):

        if self.check_squeeze:
            squeeze_complete=atoms.info['squeeze_complete']
            
            if not squeeze_complete:
                output_string='Dimensional squeeze incomplete'
                return False, output_string


        structure_ok, output_string = super().check(atoms, distances)
        return structure_ok, output_string
    
    
    
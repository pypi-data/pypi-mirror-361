#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 15:08:51 2023

@author: casper
"""

from gpatom.hyperspatial_beacon.constrainer import HSConstrainer

from gpatom.hyperspatial_beacon.gpfp.prior import HighDimRepulsivePotential

import numpy as np
from ase.data import covalent_radii
from gpatom.beacon.str_gen import (RandomStructure, RandomBox, RandomCell, 
                                   RandomCellVolumeRange, RandomBoxVolumeRange, 
                                   Random2DRanges)
from scipy.optimize import minimize, Bounds
from gpatom.fractional_beacon.icebeacon import UnitCellHandler
from gpatom.hyperspatial_beacon.hyperspacebeacon import HSParamsHandler


class HighDimRandomStructure(RandomStructure):
    
    """
    Base class used for inheritance in other high dimensional 
    structure generators
    """

    def __init__(self, atoms, world_center, rng=np.random):
        """
        parameters
        ----------
        atoms: ase atoms object 
            Required
            
        world_center: numpy array
            Array carrying the zero points for all spatial dimensions 
            Required
            
        rng: random number generator, optional
            Random number generator to make sure random structures are reproducible
            Default is np.random (not reproducible)
        """
        RandomStructure.__init__(self, atoms, rng)
        self.world_center=world_center


class HighDimAtomsRelaxer:

    """
    Class to relax atoms after structure generation with a high dimensional
    structure generator
    
    Examples
    -------- 
    >>> relaxer=AtomsRelaxer(calculator=my_calculator, with_unit_cell=True)
    >>> relaxed_atoms=relaxer.run(atoms, world_center, extra_coords)
    """    
    
    def __init__(self, calculator=None,
                 with_unit_cell=False,
                 fixed_cell_params=None,
                 fmax=0.05, steps=200):
    
        """
        parameters
        ----------
        calculator: ase calculator, optional
            Calculator object to define way of stucture relaxation.
            If None a HighDimRepulsivePotential will be setup and used
            Default is None
            
        with_unit_cell: bool, optional
            If unit cell should be relaxed as well
            Default is False
            
        fixed_cell_params: list of bools, optional 
            Describes if some part of the unit cell should stay fixed (True) or  
            be optimied (False). voight notation used (xx, yy, zz, yz, xz, xy).
            If None value is set to [False]*6, i.e. all of unit cell optimized 
            Default is None

        fmax: float, optional
            The convergence criteria on the max size of forces
            Default is 0.05
            
        steps: int, optional
            The max number of relaxation steps to be taken
            Default is 200 
        """  
        
        if calculator is None: 
            calculator = HighDimRepulsivePotential(prefactor=10, rc=0.9, 
                                                   potential_type='parabola', 
                                                   exponent=2, 
                                                   extrapotentials=None)
            
            
        self.with_unit_cell=with_unit_cell
        
        if self.with_unit_cell:
            self.run=self.run_cell
        else:
            self.run=self.run_no_cell

        self.calculator=calculator
        self.fmax=fmax
        self.steps=steps
        
        if fixed_cell_params is None:
            fixed_cell_params = [False]*6    
        self.opt_cell_mask = np.array([not elem for elem in fixed_cell_params], dtype=int)        


    def run_no_cell(self, atoms, world_center, extra_coords):
        """
        Method to relax atomic coordinates without changing the unit cell

        Parameters
        ----------
        atoms : ase.atoms
            The atoms to relax
        world_center : numpy.array
            The coordinate system centers
        extra_coords : numpy.array
            The hyperspatal coordinates

        Returns
        -------
        atoms : ase.atoms
            The relaxed atoms
        extra_coords : numpy.array
            The relaxed hyperspatial coordinates
        """
                
        dims=HSParamsHandler.get_dimension_from_exra_coords(extra_coords)
            
        params=HSParamsHandler.pack_atomic_params(len(atoms), dims, atoms.positions, extra_coords)

        lb, ub = self.get_bounds_no_cell(atoms, dims, world_center)
        
        result = minimize(self.prior_vals,   
                          params,
                          args=(atoms, self.calculator, dims),
                          method='L-BFGS-B',
                          bounds=Bounds(lb, ub, keep_feasible=False),
                          jac=True,
                          options={'ftol':0, 'gtol':self.fmax, 'maxiter': self.steps, 'maxls':20})
          
        opt_coords = result['x']
        
        positions, extra_coords = HSParamsHandler.unpack_atomic_params(len(atoms), dims, opt_coords)
        atoms.positions=positions
        
        atoms.calc=None
        return atoms, extra_coords


    def prior_vals(self, params, *args):
        """ Calculate the energy and dervative values """
        
        atoms=args[0]  # The atoms
        prior=args[1]  # The calculator
        dims=args[2]   # Number of dimesnions
    
       
        positions, extra_coords =  HSParamsHandler.unpack_atomic_params(len(atoms), dims, params)   
        
        atoms.positions=positions
        atoms.extra_coords=extra_coords
        atoms.dims=dims
        
        prior.calculate(atoms)
        
        energy = prior.results['energy']
        derivatives = prior.results['forces']

        return (energy, -np.array(derivatives.flatten()) )  


    def get_bounds_no_cell(self, atoms, dims, world_center):
        """
        Set bound on coordinates when not optimizing the unit cell
        """
        n_atoms=len(atoms)
        lb, ub = HSConstrainer.setup_bounds(n_atoms, dims)
        lb, ub = HSConstrainer.hs_constrain_atoms(atoms, dims, 
                                                  world_center, lb, ub)    
        return lb, ub
    

    def run_cell(self, atoms, world_center, extra_coords):  
        """
        Simultaneously relax atomic coordinates and unit cell

        Parameters
        ----------
        atoms : ase.atoms
            The atoms to relax
        world_center : numpy.array
            The coordinate system centers
        extra_coords : numpy.array
            The hyperspatal coordinates

        Returns
        -------
        atoms : ase.atoms
            The relaxed atoms
        extra_coords : numpy.array
            The relaxed hyperspatial coordinates
        """
        natoms=len(atoms)            
        original_cell=atoms.get_cell()
        cell_factor=float(natoms)

        dims=HSParamsHandler.get_dimension_from_exra_coords(extra_coords)

        deformation_tensor, deformed_positions = UnitCellHandler.atoms_real_to_deformed(atoms, original_cell, cell_factor)

        params=HSParamsHandler.pack_params(natoms, dims, deformed_positions, extra_coords, deformation_tensor)

        lb, ub = self.get_bounds_cell(atoms, dims, world_center) 

        result = minimize(self.prior_vals_with_stress,   
                          params,
                          args=(atoms, self.calculator, dims, original_cell, cell_factor),
                          method='L-BFGS-B',
                          bounds=Bounds(lb, ub, keep_feasible=False),
                          jac=True,
                          options={'ftol':0, 'gtol':self.fmax, 'maxiter': self.steps, 'maxls':20})
          
        opt_coords = result['x']
        
        deformed_positions, extra_coords, deformation_tensor = HSParamsHandler.unpack_params(natoms, dims, opt_coords)  
    
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, deformed_positions, original_cell, cell_factor)
        
        atoms.calc=None
        return atoms, extra_coords
    
    def prior_vals_with_stress(self, params, *args):
        """ 
        Calculate the energy and derivatives w.r.t atomic coordinates and
        cell parameters
        """
        
        atoms=args[0]          # The atoms
        prior=args[1]          # The calculator
        dims=args[2]           # The total number of dimensions
        original_cell=args[3]  # The unit cell
        cell_factor=args[4]    # A scaling constant for the unit cell
        
        natoms=len(atoms)
        
        deformed_positions, extra_coords, deformation_tensor =  HSParamsHandler.unpack_params(natoms, dims, params)  
                       
        atoms=UnitCellHandler.atoms_deformed_to_real(atoms, deformation_tensor, deformed_positions, original_cell, cell_factor)
        
        atoms.extra_coords=extra_coords
        atoms.dims=dims
        
        prior.calculate(atoms)
        
        energy = prior.results['energy']
        stress=prior.results['stress']
        forces=prior.results['forces']
        
        d3_forces, extra_forces = HSParamsHandler.get_real_and_extra(len(atoms), dims, forces)
        
        deformed_forces, deformed_virial = UnitCellHandler.forces_real_to_deformed(atoms, d3_forces, stress, original_cell, cell_factor)
        
        deformed_gradients=-deformed_forces
        
        deformed_virial = UnitCellHandler.apply_cell_mask(deformed_virial, self.opt_cell_mask)   
        
        derivatives=HSParamsHandler.pack_params(natoms, dims, deformed_gradients, extra_forces, deformed_virial)
       
        return (energy, np.array(derivatives.flatten()) ) 


    def get_bounds_cell(self, atoms, dims, world_center):
        """
        Set bound on coordinates when simultaneously optimizing the unit cell
        """
        n_atoms=len(atoms)
        lb, ub = HSConstrainer.setup_bounds_unitcell(n_atoms, dims)
        lb, ub = HSConstrainer.hs_constrain_atoms(atoms, dims, 
                                                  world_center, lb, ub)     
        return lb, ub
    

    
class HighDimAtomsInsideBoxRelaxer(HighDimAtomsRelaxer):
    """
    Class to relax atoms after structure generation inside of a box.
    (can not relax unit cells)
    
    Examples
    --------
    >>> relaxer=AtomsRelaxer(calculator=my_calculator, with_unit_cell=True)
    >>> relaxed_atoms=relaxer.run(atoms, world_center, extra_coords)
    """

    def __init__(self, box, calculator=None, fmax=0.05, steps=200, 
                 covrad_inside=None):
        """
        parameters
        ----------
        box: list of lists
            The box within which the atoms should be relaxed. 
            format box=[ [xlim_1, xlim_2], [ylim_1, ylim_2], 
                        [zlim_1, zlim_2], [4dlim_1, 4dlim_2], ... ]
            The number of sublists in the box  should match the dimensionality
            of the atoms object.
            Required
            
        calculator: ase.calculator, optional
            calculator object to define way of stucture relaxation.
            If None a HighDimRepulsivePotential will be setup and used.
            Default is None

        covrad_inside: list of three bools, optional
            If the entire atom should be kept inside the box or just the centers.
            separate bools are for x, y and z directions respectively.
            If None list will be set to true for all dimensions.
            Default is True

        fmax: float, optional
            The convergence criteria on the max size of forces
            Default is 0.005
            
        steps: int, optional
            The max number of relaxation steps to be taken
            Default is 200
        """
        if calculator is None:
            calculator = HighDimRepulsivePotential(prefactor=10, rc=0.9, 
                                                   potential_type='parabola', 
                                                   exponent=2, 
                                                   extrapotentials=None)
        
        self.calculator=calculator
        self.box=box
        self.fmax=fmax
        self.steps=steps
        
        if covrad_inside is None:
            covrad_inside=[True]*len(box)
        
        self.covrad_inside=covrad_inside

    def run(self, atoms, world_center, extra_coords):
        """
        Parameters
        ----------
        atoms : ase.atoms
            The atoms to relax
        world_center : numpy.array
            The coordinate system centers
        extra_coords : numpy.array
            The hyperspatal coordinates

        Returns
        -------
        atoms : ase.atoms
            The relaxed atoms
        extra_coords : numpy.array
            The relaxed hyperspatial coordinates
        """

        dims=HSParamsHandler.get_dimension_from_exra_coords(extra_coords)        

        params=HSParamsHandler.pack_atomic_params(len(atoms), dims, atoms.positions, extra_coords)
        
        lb, ub = self.get_bounds(atoms, dims, world_center, self.box, self.covrad_inside)        
                     
        result = minimize(self.prior_vals,   
                          params,
                          args=(atoms, self.calculator, dims),
                          method='L-BFGS-B',
                          bounds=Bounds(lb, ub, keep_feasible=False),
                          jac=True,
                          options={'ftol':0, 'gtol':self.fmax, 'maxiter': self.steps, 'maxls':20})
          
        opt_coords = result['x']
        positions, extra_coords = HSParamsHandler.unpack_atomic_params(len(atoms), dims, opt_coords)
        atoms.positions=positions
        
        atoms.calc=None
        return atoms, extra_coords


    def get_bounds(self, atoms, dims, world_center, box,  covrad_inside):
        """ Setup bounds on fixed atomic coordinates """
        lb , ub = self.setup_limits(atoms, dims, box, covrad_inside)
        lb, ub = HSConstrainer.hs_constrain_atoms(atoms, dims, 
                                                  world_center, lb, ub) 
        
        return lb, ub
    
    
    def setup_limits(self, atoms, dims, box, covrad_inside):
        """ setup box bounds """
        covrad_inside=np.array(covrad_inside,dtype=int)
            
        atomic_radii=[  covalent_radii[atoms[i].number]*covrad_inside  for i in range(len(atoms))   ]
        
        n_atoms=len(atoms)
        lb = [box[i][0] for i in range(dims)]*n_atoms
        ub = [box[i][1] for i in range(dims)]*n_atoms
        
        lb=np.array(lb) + np.array(atomic_radii).flatten()
        ub=np.array(ub) - np.array(atomic_radii).flatten()    
        
        return lb, ub             
      
    
    
class HighDimRandomBox(HighDimRandomStructure, RandomBox):
    
    """
    Generator to create a box of of >=3 dimesnions 
    in which atoms are randomly placed inside
    
    Examples
    --------
    >>> sgen=RandomBox(atoms, box=my_box)
    >>> new_atoms=sgen.get()
    """
    
    def __init__(self, atoms, box=[(0., 1.), (0., 1.), (0., 1.), (0.,1.)],
                 covrad_inside=False, world_center=None, relaxer=None, **kwargs): 
        """
        parameters
        ----------
        atoms: ase.Atoms
            Atoms to be generated
            Required
            
        box: list of lists, optional
            The box within which the atoms should be relaxed. 
            format box=[ (xlim_1, xlim_2), (ylim_1, ylim_2), 
                        (zlim_1, zlim_2), (4dlim_1, 4dlim_2), ... ]
            Default is  [(0., 1.), (0., 1.), (0., 1.), (0., 1.)]  (i,e. 4D)
             
        covrad_inside: bool, optional
            If the entire atoms should be placed inside the box or just the centers.
            Default: False (only atom centers required to be inside) 
            
        world_center: numpy.array, optional
            Array carrying the zero points for all spatial dimensions 
            If None center will be set to [atoms.cell.lengths()[0]/2]*len(box) 
            Default is None   
        
        relaxer: High dimensional Relaxer object 
            Relaxation procedure for atoms after structure generation.
            Default is None (no relaxation)
            
        rng: random number generator
            random number generator for reprodicuiblity
            Default is np.random (not reproducible)
        """
        
        if world_center is None:
            world_center=[atoms.cell.lengths()[0]/2]*len(box) 
            
        self.world_center=world_center

        
        assert(len(self.world_center)==len(box))
        
        HighDimRandomStructure.__init__(self, atoms.copy(),
                                        world_center=self.world_center, **kwargs)
    
        self.atoms=atoms
        self.box=box 
        self.dims=len(box)
        self.covrad_inside=covrad_inside
        self.extra_dims=len(box)-3
        self.relaxer=relaxer


    def get_extra_coords(self, atoms):
        """ Get hyperspatial coordinates """
        
        extra_coords=np.zeros( (len(self.atoms), self.extra_dims) )
        
        for atom in atoms:            
            if atom.index not in self.cindex:
                for dim_idx in range(self.extra_dims):
                    rc = covalent_radii[atom.number] if self.covrad_inside else 0
                    extra_coords[atom.index, dim_idx]=self.get_coord(rc, dim_idx+3)
            else:
                for dim_idx in range(self.extra_dims):
                    extra_coords[atom.index, dim_idx]=self.world_center[dim_idx+3]
                    
        return extra_coords

    
    def get(self):
        
        newatoms=self.atoms.copy()
        
        newatoms=self.get_positions(newatoms)
        
        if self.extra_dims>0:
            extra_coords = self.get_extra_coords(newatoms)
        else:
            extra_coords=None
       
        
        if self.relaxer is not None:
            newatoms, extra_coords  = self.relaxer.run(newatoms, 
                                                       self.world_center, 
                                                       extra_coords)
        
        newatoms.extra_coords=extra_coords
        newatoms.world_center=self.world_center
        
        newatoms.wrap()
     
        return newatoms
    
    
class HighDimRandomBoxVolumeRange(HighDimRandomStructure, RandomBoxVolumeRange):
    
    """
    Generator to create boxes of >=3 dimensions in a specified 
    volume interval in which atoms are randomly placed inside
    
    Examples
    --------
    >>> sgen=HighDimRandomBoxVolumeRange(atoms, base_volume=...)
    >>> new_atoms=sgen.get()
    """    
    
    def __init__(self, atoms, base_volume=None, volume_scaling=[1,3], world_center=None, 
                 dims=4, cell_length=None, free_space=5, 
                 covrad_inside=False, relaxer=None, **kwargs):        
    
        """
        parameters
        ----------
        atoms: ase Atoms object
            Required
            
        base_volume: float, optional
            a volume that the interval is set relative to
            If None volume is set to the total atomic volume in n dimensions,
            (Works up to 6 dimensions)
            Default is None

        volume_scaling: list of 2 floats, optional
            The upper and lower limit of volumes relative to the base_volume
            that cells are setup with 
            Default is [1,3]
        
        dims: int, optional
            The number of dimensions the box should be constructed in
            Default is 4
        
        world_center: numpy.array, optional
            Array carrying the zero points for all spatial dimensions.
            If None value is set to [cell_length/2]*dims
            Default is None 
                
        cell_length: float, optional
            size of cubic unit cell. 
            If None cell length is set to volume_range[1])**(1/3)+2*free_space
            Default is None
        
        free_space: float, optional
            Vacuum put around the box on each side.
            default is 5
            
        covrad_inside: bool, optional
            If the entire atoms should be placed inside the box or just the centers.
            Default is False (only atom centers required to be inside) 
            
        relaxer: Relaxer object 
            Relaxation procedure for atoms after structure generation.
            Default is None (no relaxation)
            
        rng: random number generator
            random number generator for reprodicuiblity
            Default is np.random (not reproducible)
        """
        assert(dims>2)
        
        if base_volume is None:
            base_volume=HighDimBoxConstructor.get_volume(atoms, dims)
        
        volume_range=[base_volume*volume_scaling[0], 
                      base_volume*volume_scaling[1]]    
        
        if cell_length is None:
            cell_length=(volume_range[1])**(1/3)+2*free_space
       
        if world_center is None:
            world_center=[cell_length/2]*dims 

        self.volume_range=volume_range
    
        self.cell_size=[cell_length]*3

        self.dims=dims
        
        self.extra_dims=dims-3
        
        self.world_center=world_center
        
        HighDimRandomStructure.__init__(self, atoms.copy(),
                                        world_center=self.world_center, **kwargs)
        
        self.atoms.cell=self.cell_size

        self.covrad_inside=covrad_inside
        
        self.relaxer=relaxer
        

    def get_box(self):
        """ Construct the box"""
                
        volume = self.rng.uniform(self.volume_range[0], self.volume_range[1])
        box_length=volume**(1/self.dims)
        box = HighDimBoxConstructor.construct_box(self.cell_size, box_length, self.dims)
        
        return box
    

    def get_extra_coords(self, box, atoms):
        """ Get hyperspatial coordinates """
        
        extra_coords=np.zeros( (len(self.atoms), self.extra_dims) )
        
        for atom in atoms:            
            if atom.index not in self.cindex:
                for dim_idx in range(self.extra_dims):
                    rc = covalent_radii[atom.number] if self.covrad_inside else 0
                    extra_coords[atom.index, dim_idx]=self.get_coord(box, rc, dim_idx+3)
            else:
                for dim_idx in range(self.extra_dims):
                    extra_coords[atom.index, dim_idx]=self.world_center[dim_idx+3]
                    
        return extra_coords

    
    def get(self):
        
        newatoms=self.atoms.copy()
        
        box=self.get_box()
        
        newatoms=self.get_positions(box, newatoms)
        
        if self.extra_dims>0:
            extra_coords = self.get_extra_coords(box, newatoms)
        else:
            extra_coords=None
       
        
        if self.relaxer is not None:
            newatoms, extra_coords  = self.relaxer.run(newatoms, 
                                                       self.world_center, 
                                                       extra_coords)
        
        newatoms.extra_coords=extra_coords
        newatoms.world_center=self.world_center
        
        newatoms.wrap()
     
        return newatoms

    
    
class HighDimRandomCell(HighDimRandomStructure, RandomCell):
    
    """
    Generator to create random unit cells with an arbitrarty amount of 
    extra nonperiodic hyperdimesnions. Atoms are placed randomly inside
    the hyperspatial cell. The generator makes distortions to the cell 
    object stored on the imported atoms object. 
    
    Examples
    --------
    >>> sgen=HighDimRandomCell(atoms, scale=0.25)
    >>> new_atoms=sgen.get()
    """
    
    def __init__(self, atoms, scale=0.3, fixed_cell_params=None, world_center=None, 
                 extra_size=None, covrad_inside=False, relaxer=None, **kwargs):        
        """
        parameters
        ----------
        atoms: ase.Atoms object
            Required
            
        scale: float, optional
            The strengh of distortions made to the cell stored on the atoms object.
            The strength scales with the volume of the original unit cell
            Default is 0.3
            
        fixed_cell_params: list of bools, optional 
            Describes if some part of the unit cell should stay fixed (True) or  
            be optimied (False). Voight notation used (xx, yy, zz, yz, xz, xy).
            If none all are set to False (all of unit cell optimized)
            Default is None
            
        extra_size: list of floats, optional
            List of floats describing the extension of the extra dimensions
            in which atoms can be placed. Length of array determines the 
            overall dimensionality of the atoms object as 3+len(extra_size)
            Default is None (no extra dimensions)
            
        world_center: numpy.array, optional
            Array carrying the zero points for all spatial dimensions
            If Nonne array is set to atoms.cell[i][i] for the first 3 
            dimensions and extra_size[i]/2 for all hyperdimensions.
            Default is None
        
        covrad_inside: bool, optional
            If the entire atoms should be placed inside the extra dimensions 
            or just the centers.
            Default is False 
        
        relaxer: Relaxer object, optional 
            Relaxation procedure for atoms after structure generation
            Default is None (no relaxation)
            
        rng: random number generator
            random number generator for reprodicuiblity
            Default is np.random (not reproducible)
        """
        
        if extra_size is not None:
            if not isinstance(extra_size, list):
                extra_size = [extra_size]

        
        if world_center is None:
            world_center=[] 
            for i in range(3):
                cell=atoms.get_cell() 
                world_center.append(cell[i][i])
                
            if extra_size is not None:
                for i in range(len(extra_size)):
                    world_center.append(extra_size[i]/2)
            
        ndims=len(world_center)    

        self.world_center=world_center
        self.extra_dims= ndims - 3
        self.extra_size=extra_size
        self.covrad_inside=covrad_inside
        
        assert(len(self.world_center)==ndims)

        RandomCell.__init__(self,  atoms.copy(), scale=scale, 
                            fixed_cell_params=fixed_cell_params)

        HighDimRandomStructure.__init__(self, atoms.copy(),
                                        world_center=self.world_center, **kwargs)
     
        self.relaxer=relaxer
        
    def get(self):
        cell = self.get_random_cellparams(self.atoms)

        newatoms = self.atoms.copy()
        coords=self.get_new_positions(cell)
        
        newatoms.positions = coords
        newatoms.cell = cell
        
        if self.extra_dims>0:
            extra_coords=self.get_extra_coords(self.extra_size)
        else:
            extra_coords=None
        
        if self.relaxer is not None:
            newatoms, extra_coords  = self.relaxer.run(newatoms, 
                                                       self.world_center, 
                                                       extra_coords)
        
        newatoms.extra_coords=extra_coords
        newatoms.world_center=self.world_center
        
        newatoms.wrap()
        
        return newatoms
    
    def get_extra_coords(self, extra_size):
        """ Get hyperspatial coordinates """
        
        extra_coords=np.zeros( (len(self.atoms), self.extra_dims) )
        
        for atom in self.atoms:

            if atom.index in self.cindex:
                for dim_idx in range(self.extra_dims):
                    extra_coords[atom.index,dim_idx]=self.world_center[3+dim_idx]
            
            else:
                for dim_idx in range(self.extra_dims):
                    rc = covalent_radii[atom.number] if self.covrad_inside else 0
                    extra_coords[atom.index,dim_idx]= (extra_size[dim_idx]-2*rc)*self.rng.random()+rc
        
        return extra_coords



        
class HighDimRandomCellVolumeRange(HighDimRandomCell, RandomCellVolumeRange):
    
    """
    Generator to create random unit cells with an arbitrarty amount of extra 
    spatial nonperodic dimensionsions within a specified volume interval.
    Atoms are randomly placed inside the hyperspatial cell.
    
    Examples
    --------
    >>> sgen=HighDimRandomCellVolumeRange(atoms, scale=0.25)
    >>> new_atoms=sgen.get()  
    """
    
    def __init__(self, atoms, scale=0.5, base_volume=None, volume_scaling=[1,3], 
                 world_center=None, extra_size=None, covrad_inside=False,
                 relaxer=None, **kwargs):  
        """
        parameters
        ----------
        atoms: ase.Atoms object
            Required
            
        scale: float, optional
            The strengh of distortions made to a unit cube cell
            Default is 0.5
            
        base_volume: float, optional
            A volume that the interval is set relative to.
            If None the volume is set to the total atomic volume in 
            n dimensions divided by the product of values in extra_size.
            (Works up to 6 dimensions)
            Default is None
        
        volume_scaling: list of 2 floats, optional
            The upper and lower limit of volumes relative to the base_volume
            that cells are setup with 
            Default is [1,3]
        
        extra_size: list of floats, optional
            List of floats describing the extension of the extra dimensions
            in which atoms can be placed. Length of array determines the 
            overall dimensionality of the atoms object as 3+len(extra_size).
            Default is None (no extra dimensions)
            
        world_center: numpy.array, optional
            Array carrying the zero points for all spatial dimensions.
            If None aray is set to atoms.cell[i][i] for the first 3 dimensions
            and extra_size[i]/2 for all hyperdimensions.
            Default is None
            
        covrad_inside: bool, optional
            If the entire atoms should be placed inside the extra dimensions 
            or just the centers.
            Default is False 
        
        relaxer: Relaxer object, optional
            Relaxation procedure for atoms after structure generation.
            Default is None (no relaxation)
            
        rng: random number generator, optional
            random number generator for reprodicuiblity
            Default is np.random (not reproducible)
        """
                
        HighDimRandomCell.__init__(self, atoms, scale=scale, 
                                   fixed_cell_params=None, 
                                   world_center=world_center,
                                   extra_size=extra_size,
                                   covrad_inside=covrad_inside, **kwargs)
                
        if base_volume is None:
            rc=np.array( [  covalent_radii[atoms[i].number]  for i in range(len(atoms)) ]  )
            if self.extra_size is None:
                base_volume=sum(4/3*np.pi*rc**3)
            else:
                dh=[]
                for i in range(len(self.extra_size)):
                    dh.append(self.extra_size[i])
                
                if len(self.extra_size)==1:
                    V_atoms=sum(  (1/2)*(np.pi**2)*(rc**4)  )
                elif len(self.extra_size)==2:
                    V_atoms=sum(  (8/15)*(np.pi**2)*(rc**5)  )
                elif len(self.extra_size)==3:
                    V_atoms=sum(  (1/6)*(np.pi**3)*(rc**6)  )
                    
                base_volume=V_atoms/np.prod(dh)
                
        self.volume_range=[base_volume*volume_scaling[0], 
                           base_volume*volume_scaling[1]]
        
        self.base_cell = np.array([[1,0,0],
                                   [0,1,0], 
                                   [0,0,1]])
        
        self.relaxer=relaxer
        
    def get_random_cellparams(self, atoms):
    
        cell=self.base_cell.copy()
    
        addition = self.rng.uniform(-self.scale, self.scale, size=(3, 3))
    
        cell = cell + addition
            
        atoms=atoms.copy()
        
        atoms.cell=cell
        
        current_volume=atoms.get_volume()
            
        desired_volume = self.rng.uniform(self.volume_range[0], self.volume_range[1])
    
        g=( desired_volume/current_volume )**(1/3)
            
        atoms.cell*=g
    
        return atoms.cell


class HighDimRandom2DRanges(HighDimRandomStructure, Random2DRanges):
    
    """    
    Generator for 2D unit cells with a fixed height, a set of nonperiodic 
    extra dimensions and ranges of XY aspect ratio, XY area and angle. 
    Atoms are placed randomly inside the hyperspatial cell
    
    Examples
    --------
    >>> sgen=HighDimRandom2DRanges(atoms, minz=..., maxz=...)
    >>> new_atoms=sgen.get()
    """
        
    def __init__(self, atoms, minz, maxz, base_area=None, area_scaling=[1,3],  
                 xy_ratio_range=[1,1.5], angle_range=[25, 90], 
                 height=20, world_center=None, extra_size=None, 
                 covrad_inside=False, relaxer=None, **kwargs):

        """
        parameters
        ----------
        atoms: ase Atoms object
            Required
            
        minz: float
            minimum z-coordinate an atom can get
            Required
            
        maxz: float
            maximum z-coordinate an atom can get
            Required
            
        base_area: float, optional
            A reference area that cells are scaled relative to.
            If None, the value is set to the total atomic volume 
            in n dimensions divided by (maxz - minz)*(extra_sizes product)
            (works up to 6 dimensions)
            Default is None
            
            
        area_scaling: list of 2 floats, optional
            The upper and lower limit of volumes relative to the base_area
            that cells are setup with 
            Default is [1,3]
            
        xy_ratio_range: list of two floats, optional
            The upper and lower limit of XY-aspect ratios
            Default is [1, 1.5]
            
        angle_range: list of two floats, optional
            The upper and lower limit of cell angles 
            Default is [25, 90]
            
        height: float, optional
            Height of unit cell
            Default is 20
            
        extra_size: list of floats, optional
            List of floats describing the extension of the extra dimensions
            in which atoms can be placed. Length of array determines the 
            overall dimensionality of the atoms object as 3+len(extra_size)
            Default is None (no extra dimensions)
            
        world_center: numpy array, optional
            Array carrying the zero points for all spatial dimensions
            If None array is set to atoms.cell[i][i] for the first 
            3 dimensions and extra_size[i]/2 for all hyperdimensions
            Default is None
            
        covrad_inside: bool, optional
            If the entire atoms should be placed inside the z limits end extra
            dimensions or just the centers.
            Default is False (only atom centers required to be inside) 
        
        relaxer: Relaxer object, optional
            Relaxation procedure for atoms after structure generation
            Default is None (no relaxation)
                
        rng: random number generator, optional
            random number generator for reprodicuiblity
            Default is np.random (not reproducible)
        """
        
        if extra_size is not None:
            if not isinstance(extra_size, list):
                extra_size = [extra_size]

        
        if world_center is None:
            world_center=[] 
            for i in range(3):
                cell=atoms.get_cell() 
                world_center.append(cell[i][i])
                
            if extra_size is not None:
                for i in range(len(extra_size)):
                    world_center.append(extra_size[i]/2)
            
        ndims=len(world_center)    

        self.world_center=world_center
        self.extra_dims= ndims - 3
        self.extra_size=extra_size
        
        assert(len(self.world_center)==ndims)
        
        
        if base_area is None:
            rc=np.array( [ covalent_radii[atoms[i].number] for i in range(len(atoms)) ]  )
            if minz==maxz:
                assert (self.extra_size is None)
                base_area=sum( np.pi*rc**2 )
            else:
                dz = (maxz-minz)
                
                if self.extra_size is None:
                    V_atoms=sum(  (4/3)*np.pi*(rc**3)  )
                    base_area=V_atoms/dz
                else:
                    dh=[]
                    for i in range(len(self.extra_size)):
                        dh.append(self.extra_size[i])
                
                    if len(self.extra_size)==1:
                        V_atoms=sum(  (1/2)*(np.pi**2)*(rc**4)  )
                    elif len(self.extra_size)==2:
                        V_atoms=sum(  (8/15)*(np.pi**2)*(rc**5)  )
                    elif len(self.extra_size)==3:
                        V_atoms=sum(  (1/6)*(np.pi**3)*(rc**6)  )
                        
                    base_area=V_atoms/(dz*np.prod(dh))
        
                
        Random2DRanges.__init__(self,  atoms, minz, maxz, base_area=base_area, 
                                area_scaling=area_scaling, xy_ratio_range=xy_ratio_range, 
                                angle_range=angle_range, height=height,
                                covrad_inside=covrad_inside)

        HighDimRandomStructure.__init__(self, atoms.copy(),
                                        world_center=self.world_center, **kwargs)
        
        self.relaxer=relaxer
    
    def get(self):

        cell=self.get_cell()
        
        newatoms = self.atoms.copy()
        newatoms.set_cell(cell)
        
        cell=newatoms.cell
        newpos = []

        for atom in self.atoms:

            if atom.index in self.cindex:
                pos = atom.position
            else:
                pos = self.get_xyz(cell)

            newpos.append(pos)

        newpos = np.array(newpos)
        
        newatoms.positions = newpos
                
        if self.extra_dims>0:
            extra_coords=self.get_extra_coords(self.extra_size)
        else:
            extra_coords=None

        if self.relaxer is not None:
            newatoms, extra_coords  = self.relaxer.run(newatoms, 
                                                       self.world_center, 
                                                       extra_coords)
            
        newatoms.extra_coords=extra_coords 
        newatoms.world_center=self.world_center

        newatoms.wrap()

        return newatoms
             
    def get_extra_coords(self, extra_size):
        """ Get hyperspatial coordinates"""
        
        extra_coords=np.zeros( (len(self.atoms), self.extra_dims) )
        
        for atom in self.atoms:

            if atom.index in self.cindex:
                for dim_idx in range(self.extra_dims):
                    extra_coords[atom.index,dim_idx]=self.world_center[3+dim_idx]
            
            else:
                for dim_idx in range(self.extra_dims):
                    rc = covalent_radii[atom.number] if self.covrad_inside else 0
                    extra_coords[atom.index,dim_idx]= (extra_size[dim_idx]-2*rc)*self.rng.random()+rc
        
        return extra_coords
    
    
    
class HighDimBoxConstructor:
    
    """
    Static methods class to help setup random boxes in 1 to 6 dimensions 
    with the box volumes being some multiplum of the total atomic volume in
    n dimensions of atoms placed inside the box
    """
    
    @staticmethod
    def get_box(atoms, dims=4, volume_fraction=0.2, free_space=5, cell=None):
        
        """
        Method to create boxes of different dimensionality
            
        Parameters:
        atoms: ase.Atoms object
            Required
            
        dims: int, optional
            Dimensionality of the constructed box
            Default is 4
            
        volume_fraction: float, optional
            The fraction of box volume occupied by the total atomic volume. 
            Default is 0.2

        free_space: float, optional
            Vacuum set on both sides of the box when setting the unit cell.
            Default is 5

        cell: unit cell, optional
            If None an automatc cell is set up with length 
            box_length+2free_space
            Default is None 
            
        Returns
        -------
        box: numpy.array 
            A cubic box in which atoms can be placed
        cell: numpy.array
            A cell inside of which the box is placed
        """
        
        box_length=HighDimBoxConstructor.get_box_length(atoms, volume_fraction, dims)

        if cell is None:
            cell=HighDimBoxConstructor.get_unitcell(box_length, free_space)
        
        box = HighDimBoxConstructor.construct_box(cell, box_length, dims)
        
        return box, cell

    @staticmethod
    def get_volume(atoms, dims):
        rc =np.array( [    covalent_radii[atoms[i].number]  for i in range(len(atoms))   ]  )
        
        if dims==1:
            V_atoms=sum(2*rc)
        elif dims==2:
            V_atoms=sum(np.pi*(rc**2) )
        elif dims==3:
            V_atoms=sum(  (4/3)*np.pi*(rc**3)  )
        elif dims==4:
            V_atoms=sum(  (1/2)*(np.pi**2)*(rc**4)  )
        elif dims==5:
            V_atoms=sum(  (8/15)*(np.pi**2)*(rc**5)  )
        elif dims==6:
            V_atoms=sum(  (1/6)*(np.pi**3)*(rc**6)  )
            
        return V_atoms

    @staticmethod
    def get_box_length(atoms, volume_fraction, dims):
        
        V_atoms=HighDimBoxConstructor.get_volume(atoms, dims)
        
        box_length=(V_atoms/volume_fraction)**(1/dims)
        
        return box_length
    
    @staticmethod
    def construct_box(cell, box_length, dims): 
    
        box_start=cell[0]/2-box_length/2
        box_end=cell[0]/2+box_length/2
        
        box=[(box_start, box_end)]*dims
        
        if len(box)==2:
            box.append(  (cell[0]/2, cell[0]/2)  )
        elif len(box)==1: 
            box.append(  (cell[0]/2, cell[0]/2) )
            box.append(  (cell[0]/2, cell[0]/2) )
        
        return box
    
    @staticmethod
    def get_unitcell(box_length, free_space):
            
        cell_L=box_length+2*free_space
       
        cell=[cell_L, cell_L, cell_L]
        
        return cell
    
from gpatom.gpfp.prior import RepulsivePotential
from ase.constraints import FixAtoms, FixBondLengths
from ase.optimize import BFGS
from ase.io import read

from scipy.spatial import distance_matrix
import numpy as np
import os

from scipy.optimize import minimize, Bounds

from ase.data import covalent_radii

from ase import Atoms
from ase.io import read, write, Trajectory

from ase.filters import UnitCellFilter

from ase.calculators.emt import EMT

from ase.io import write


def get_fixed_index(atoms):
    """
    Get the indices of atoms constrained by FixAtoms.

    Parameters
    ----------
    atoms : ase.Atoms
        The Atoms object to check for fixed (constrained) atoms.

    Returns
    -------
    numpy.ndarray
        Array of integer indices of atoms fixed by FixAtoms constraints.
        Returns an empty array if no FixAtoms constraints are found.
    """
    constr_index = []
    for C in atoms.constraints:
        if isinstance(C, FixAtoms):
            constr_index = C.index
   
    return np.array(constr_index, dtype=int)


class RandomStructure:
    
    """
    Base class for structure generators that create random atomic configurations.

    Subclasses must implement a `get()` method that returns an `ase.Atoms` object.
    """
    
    def __init__(self, atoms, rng=np.random):
        """
        parameters:
        
        atoms: ase atoms object 
            must be supplied
            
        rng: random number generator
            random number generator to make sure random structures are reproducible
            default: np.random 
        """
        
        self.atoms = atoms   
        self.rng = rng
        self.cindex = get_fixed_index(atoms)
        
    def sph2cart(self, r, theta, phi):
        """Convert spherical to Cartesian coordinates."""
        x = r * np.sin(theta) * np.cos(phi)
        y = r * np.sin(theta) * np.sin(phi)
        z = r * np.cos(theta)
        return x, y, z
    
    
    

class AtomsRelaxer:
    
    """
    Relax atomic structures using a specified calculator.

    This class provides a convenient interface to relax atomic positions,
    and optionally the unit cell, using ASE optimizers. It supports either a
    user-provided calculator or a default repulsive potential.

    Examples
    --------
    >>> relaxer = AtomsRelaxer(calculator=my_calculator, 
                               with_unit_cell=True, ...)
    >>> relaxed_atoms = relaxer.run(atoms)
    """
    
    def __init__(self, calculator=None, 
                 with_unit_cell=False,
                 fixed_cell_params=None, 
                 fmax=0.05, steps=200):
        """        
        Parameters
        ----------
        calculator : ase.Calculator, optional
            Calculator to be used for relaxation. If None, a default
            RepulsivePotential is used.
            Default is None.

        with_unit_cell : bool, optional
            If True, relaxes the unit cell along with atomic positions.
            Default is False.

        fixed_cell_params : list of bool, optional
            Flags to fix parts of the unit cell during relaxation.
            Follows Voigt notation: [xx, yy, zz, yz, xz, xy].
            True means fixed, False means relaxed.
            Default is [False, False, False, False, False, False] (fully relaxed).

        fmax : float, optional
            Maximum force criterion for convergence in eV/Å.
            Default is 0.05.

        steps : int, optional
            Maximum number of optimizer steps.
            Default is 200.
        """
        
        
        if calculator is None:
            calculator = RepulsivePotential(prefactor=10, rc=0.9, 
                                            potential_type='parabola', 
                                            exponent=2, 
                                            with_stress=with_unit_cell,
                                            extrapotentials=None)
        
        
        if fixed_cell_params is None:
            fixed_cell_params=[False]*6
        
        self.calculator=calculator
        self.with_unit_cell=with_unit_cell
        self.mask=[not elem for elem in fixed_cell_params]
        self.fmax=fmax
        self.steps=steps        
        
    def run(self, atoms):
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The Atoms object to relax.

        Returns
        -------
        ase.Atoms
            The relaxed Atoms object
        """

        atoms.calc = self.calculator   
        
        
        if self.with_unit_cell:
            opt_object=UnitCellFilter(atoms, mask=self.mask)
        else:
            opt_object=atoms
        
        opt = BFGS(opt_object, maxstep=0.1, logfile=os.devnull)
      
        opt.run(fmax=self.fmax, steps=self.steps)
        atoms.calc=None
        return atoms


class AtomsInsideBoxRelaxer:
    
    """
    Class to relax atoms inside of a box after structure generation.
    (can not relax unit cells)
    
    Examples
    --------
    >>> relaxer=AtomsRelaxer(box, calculator=calculator, ...)
    >>> relaxed_atoms = relaxer.run(atoms)
    """
 
    
    def __init__(self, box, calculator=None, covrad_inside=[True, True, True],
                 fmax=0.005, steps=200):
        """
        Parameters
        ----------
        box : list of lists
            The box within which the atoms should be relaxed.
            Format: box = [[xlim_1, xlim_2], [ylim_1, ylim_2], [zlim_1, zlim_2]].
            Required.

        calculator : ase calculator object, optional
            Calculator object defining the relaxation method.
            Default is None, in which case a RepulsivePotential will be set up and used.

        covrad_inside : list of bool, optional
            Specifies if the entire atom should be kept inside the box or just the centers.
            Separate booleans correspond to x, y, and z directions respectively.
            Default is [True, True, True] (entire atoms inside in all directions).

        fmax : float, optional
            Convergence criterion on the maximum size of forces.
            Default is 0.005.

        steps : int, optional
            Maximum number of relaxation steps to be taken.
        """
        
        
        if calculator is None:
            calculator = RepulsivePotential(prefactor=10, rc=0.9, 
                                            potential_type='parabola', 
                                            exponent=2, 
                                            extrapotentials=None)
        
        
        self.box=box
        self.covrad_inside=covrad_inside
        self.calculator=calculator
        self.fmax=fmax
        self.steps=steps
        self.ndof=3
        
    def run(self, atoms):
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The Atoms object to relax.

        Returns
        -------
        ase.Atoms
            The relaxed Atoms object
        """
        
        lb, ub = self.get_bounds(atoms, self.box, self.covrad_inside)        
                     
        params = atoms.positions.flatten() 
            
        result = minimize(self.prior_vals,   
                          params,
                          args=(atoms, self.calculator),
                          method='L-BFGS-B',
                          bounds=Bounds(lb, ub, keep_feasible=False),
                          jac=True,
                          options={'ftol':0, 'gtol':self.fmax, 'maxiter': self.steps, 'maxls':20})

        opt_array = result['x'].reshape(len(atoms), self.ndof)

        opt_coords = opt_array[:, :self.ndof].reshape(-1, self.ndof)
                
        atoms.positions=opt_coords 

        atoms.calc=None
        return atoms
        

    def get_bounds(self, atoms, box, covrad_inside):
        
        """Sets up box limits"""
        
        lb , ub = self.setup_limits(atoms, box, covrad_inside)
        lb , ub = self.constrain_atoms(atoms, lb, ub)
        
        return lb, ub
    
    
    def setup_limits(self, atoms, box, covrad_inside):
        
        covrad_inside=np.array(covrad_inside,dtype=int)
            
        atomic_radii=[  covalent_radii[atoms[i].number]*covrad_inside  for i in range(len(atoms))   ]
        
        
        n_atoms=len(atoms)
        
        lb = [box[i][0] for i in range(self.ndof)]*n_atoms
        ub = [box[i][1] for i in range(self.ndof)]*n_atoms
        
        lb=np.array(lb) + np.array(atomic_radii).flatten()
        ub=np.array(ub) - np.array(atomic_radii).flatten()    
        
        return lb, ub
    
    
    def constrain_atoms(self, atoms, lb, ub):
        
        cindex = get_fixed_index(atoms)
        
        if len(cindex)!=0:
            for atom in atoms:
                if atom.index in cindex:
                    
                    idx=atom.index*self.ndof 
                    for i in range(self.ndof):
                    
                        lb[idx+i]=np.array( atom.position[i] )
                        ub[idx+i]=lb[idx+i]                    

        return lb, ub        
  

    def prior_vals(self, params, *args):
        """Restructure data output to optimizer Format"""
        
        atoms=args[0]
        prior=args[1]
       
        atoms=self.prepare_atoms_for_prior(atoms, params)
        
        prior.calculate(atoms)
        
        energy = prior.results['energy']
        derivatives = prior.results['forces']

        return  (energy, -np.array(derivatives.flatten()) )
                    
    
    def prepare_atoms_for_prior(self, atoms, params):
        
        coords = params.reshape(len(atoms), self.ndof)[:, :self.ndof]
        atoms = atoms.copy()
        atoms.positions = coords
        
        return atoms
    
          

class Remake(RandomStructure):
    
    """
    Generator to simply reproduce a structure
    (mainy used for testing purposes)
    
    Examples
    -------- 
    >>>sgen=Remake(atoms)
    >>>new_atoms=sgen.get()
    """
    
    def __init__(self, atoms):
        RandomStructure.__init__(self, atoms)
    """
    parameters:
        
    atoms: ase.Atoms object
        Required
    """
          
    def get(self):
        newatoms=self.atoms.copy()
        return newatoms


class RandomBranch(RandomStructure):
    
    """
    Generator to create a branched structure of atoms
    
    Examples
    -------- 
    sgen=RandomBranch(atoms, llim=1.6, ulim=1.0)
    new_atoms=sgen.get()
    """
    
    def __init__(self, atoms, llim=1.6, ulim=2.0, relaxer=None, **kwargs):
        """
        parameters:
        atoms: ase.Atoms object
            Required
        
        llim: float, optional
            The lower distance limit to another atom
            Default is 1.6
        
        ulim: float, optional
            The upper distance limit to another atom
            Default is 2.0
        
        relaxer: Relaxer object, optional
            Relaxation procedure for atoms after structure generation
            Default is None (no relaxation)
        
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
    
            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).       
        """

        RandomStructure.__init__(self, atoms, **kwargs)

        assert (llim <= ulim), ('Upper limit (ulim) '
                                'should be larger than '
                                'lower limit (llim).')

        self.llim = llim
        self.ulim = ulim
        self.relaxer=relaxer

    def get(self):
        newatoms = self.atoms.copy()
        cell = newatoms.cell.lengths()
    
        newpos=np.zeros((len(newatoms),3))
        
        idx_occupied=[]
        
        i=len(self.cindex)
        
        
        if i==0:
            newpos[0,:]=newatoms.cell.lengths() / 2
            idx_occupied.append(0)
        else:
            for atom in newatoms:
                if atom.index in self.cindex:
                    newpos[atom.index,:]=atom.position  
                    idx_occupied.append(atom.index)

        for atom in newatoms:
            if atom.index not in idx_occupied:
                new_position=self.connect_new_atom(cell, newpos[idx_occupied])
                newpos[atom.index,:] = new_position
                idx_occupied.append(atom.index)
        
        newatoms.positions=newpos
        
        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)
            
        return newatoms
    
        
    def connect_new_atom(self, cell, positions):
        
        while True:
            # Sample position for new atom:
            r, theta, phi = self.rng.random([3])
            r = self.llim + r * (self.ulim - self.llim)
            theta *= np.pi
            phi *= 2 * np.pi
            pos = self.sph2cart(r, theta, phi)

            # Add atom next to another one
            neighborindex = self.rng.randint(len(positions)) 
 
            new_position = positions[neighborindex] + pos
            new_position=new_position.reshape((1,3))
          
            dm = distance_matrix(new_position, positions)    

            distances_ok = dm.min() > self.llim
            
            cell_ok = (0.0 < new_position).all() and (new_position < cell).all()

            if distances_ok and cell_ok:
                return new_position


class RandomCell(RandomStructure):
    
    """
    Generator to create random unit cells with randomly placed atoms inside.

    This generator applies distortions to the unit cell of the provided ASE
    `Atoms` object. The atomic positions are randomly initialized inside
    the distorted cell.
    
    Examples
    --------
    sgen=RandomCell(atoms, scale=0.3)
    new_atoms=sgen.get()
    """
        
    def __init__(self, atoms, scale=0.3, fixed_cell_params=None, relaxer=None, **kwargs):        
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The atomic structure to base the new structure on.
            Required.

        scale : float, optional
            The strength of the distortions applied to the unit cell.
            The strength scales with the volume of the original unit cell.
            Default is 0.3.

        fixed_cell_params : list of bool, optional
            Flags that determine which components of the cell tensor are fixed.
            Uses Voigt notation: [xx, yy, zz, yz, xz, xy].
            `True` means the parameter is fixed, `False` means it can vary.
            Default is None, which is interpreted as [False] * 6 
            (all cell parameters are variable).

        relaxer : Relaxer, optional
            A relaxation procedure applied after structure generation.
            Default is None (no relaxation).

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
    
            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        RandomStructure.__init__(self, atoms, **kwargs)
     
        if  fixed_cell_params is None:
            fixed_cell_params = [False]*6 
                
        self.scale=scale
        
        self.fixed_cell_3x3 = self.get_fixed_cell_params(fixed_cell_params)
        
        self.relaxer=relaxer

    def get(self):

        cell = self.get_random_cellparams(self.atoms)

        newatoms = self.atoms.copy()
        newatoms.cell = cell

        newpos=self.get_new_positions(cell)

        newatoms.positions = newpos
    
        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)
          
        newatoms.wrap()
        
        return newatoms
    
 
    def get_new_positions(self, cell):
        """Place atoms in cell"""
        newpos = []

        for atom in self.atoms:
            if atom.index in self.cindex:
                newpos.append(self.atoms.positions[atom.index])
                continue

            r0 = cell[0] * self.rng.random()
            r1 = cell[1] * self.rng.random()
            r2 = cell[2] * self.rng.random()

            pos = r0 + r1 + r2

            newpos.append(pos)

        newpos = np.array(newpos)
        
        return newpos

    
    def get_fixed_cell_params(self, params):

        if params is None:
            params = np.ones(6, dtype=bool)

        # convert voigt form to 3 x 3 matrix:
        fixed_3x3 = np.zeros((3, 3), dtype=bool)
        c1, c2 = np.unravel_index([0, 4, 8, 5, 2, 1], (3, 3))  # de-voigt
        for i in range(len(c1)):
            fixed_3x3[c1[i], c2[i]] = params[i]
        fixed_3x3[np.tril_indices(3)] = fixed_3x3.T[np.tril_indices(3)]
        
        return fixed_3x3

    def get_random_cellparams(self, atoms):
        """ Sets random cell"""

        # Approximately preserve volume of the unit cell
        volume = atoms.cell.volume

        # add random contributions:
        limit = self.scale * volume**(1/3.)
        addition = self.rng.uniform(-limit, limit, size=(3, 3))

        if self.fixed_cell_3x3 is not None:
            addition[self.fixed_cell_3x3] = 0.0

        newcell = self.atoms.cell.copy() + addition

        return newcell



class RandomCellVolumeRange(RandomCell):
    
    """
    Generator to create random unit cells in a specified volume interval
    with atoms randomly placed inside
    
    Examples
    --------
    >>> sgen=RandomCellVolumeRange(atoms, scale=0.5, volume_scaling=[1, 3])
    >>> new_atoms=sgen.get()
    """
           
    def __init__(self, atoms, scale=0.5, base_volume=None, 
                 volume_scaling=[1,3], relaxer=None, **kwargs):  
      
        """
        Parameters
        ----------
        atoms : ase.Atoms
            Required. The atomic configuration to base the structure on.
        
        scale : float, optional
            The strength of distortions made to a unit cube cell.
            Default is 0.5.
        
        base_volume : float, optional
            A reference volume that the generated cell volumes are scaled from.
            If None, the total atomic volume is used as the base.
            Default is None.
        
        volume_scaling : list of float, optional
            A pair of floats [min_scale, max_scale] specifying the allowed range
            of cell volumes relative to `base_volume`.
            Default is [1, 3].
        
        relaxer : Relaxer, optional
            A relaxation procedure applied after structure generation.
            Default is None (no relaxation).
        
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
    
            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        RandomCell.__init__(self, atoms, scale=scale, 
                            fixed_cell_params=None, **kwargs)
                
        if base_volume is None:
            rc=np.array( [ covalent_radii[atoms[i].number] for i in range(len(atoms)) ] )
            base_volume=sum(4/3*np.pi*rc**3)
        
        
        self.volume_range=[base_volume*volume_scaling[0],
                           base_volume*volume_scaling[1]]
        
        self.base_cell = np.array([[1,0,0],
                                   [0,1,0], 
                                   [0,0,1]])
        
        self.relaxer=relaxer
        
    def get_random_cellparams(self, atoms):
        """Generate random cells"""
    
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


class RandomBox(RandomStructure):
    
    """
    Generator to create a box in which atoms are randomly placed.
    
    Examples
    --------
    >>> sgen = RandomBox(atoms, box=[ [3, 6], [3, 6], [3, 6] ])
    >>> new_atoms = sgen.get()
    """

    def __init__(self, atoms, box=[(0., 1.), (0., 1.), (0., 1.)],
                 covrad_inside=False, relaxer=None, **kwargs):
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms object to place in the box. Must be supplied.

        box : list of tuples, optional
            The bounding box within which the atoms should be placed.
            Format: [(x_min, x_max), (y_min, y_max), (z_min, z_max)].
            Default is [(0., 1.), (0., 1.), (0., 1.)].

        covrad_inside : bool, optional
            If True, ensures the entire atoms (including covalent radii) are inside the box;
            if False, only the atomic centers are required to be inside.
            Default is False.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
    
            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        RandomStructure.__init__(self, atoms, **kwargs)

        self.box = box
        self.covrad_inside=covrad_inside
        self.relaxer=relaxer
        
    def get_coord(self, rc, idx):        
        delta_box= (self.box[idx][1]-rc) - (self.box[idx][0]+rc)
        coord=delta_box*self.rng.random() + (self.box[idx][0]+rc)
        return coord


    def get_xyz(self, rc):
        x=self.get_coord(rc, 0)
        y=self.get_coord(rc, 1)
        z=self.get_coord(rc, 2)
        return np.array([x, y, z])   


    def get_positions(self, atoms):
        
        for atom in atoms:
            if atom.index not in self.cindex:
                rc = covalent_radii[atom.number] if self.covrad_inside else 0
                atom.position=self.get_xyz(rc)

        return atoms


    def get(self):

        newatoms=self.atoms.copy()
        
        newatoms=self.get_positions(newatoms)

        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)
            
        newatoms.wrap()

        return newatoms



class RandomBoxVolumeRange(RandomStructure):
    
    """
    Generator to create boxes in a specified volume interval in which
    atoms are randomly placed inside
    
    Examples
    --------
    >>> sgen=RandomBoxVolumeRange(atoms, volume_scaling=[1,3])
    >>> sgen.get()
    """
    
    def __init__(self, atoms, base_volume=None, volume_scaling=[1,3], 
                 cell_length=None, free_space=5, 
                 covrad_inside=False, relaxer=None, **kwargs):

        """
        Parameters
        ----------
        atoms : ase.Atoms
            The atomic configuration to place in the box. Must be supplied.
            Required

        base_volume : float, optional
            A reference volume that the target volume range is scaled from.
            If None, the total atomic volume is used.
            Default is None.

        volume_scaling : list of float, optional
            A list of two values [min_scale, max_scale] defining the allowed volume
            range relative to `base_volume`.
            Default is [1, 3].

        cell_length : float, optional
            The length of the cubic unit cell.
            If None, it is computed as: (volume_scaling[1] * base_volume) ** (1/3) + 2 * free_space.
            Default is None.

        free_space : float, optional
            Amount of vacuum to pad around the atomic structure.
            Default is 5.

        covrad_inside : bool, optional
            If True, ensures the entire atoms (including covalent radii) are inside the box;
            if False, only the atomic centers are required to be inside.
            Default is False.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:
    
            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """


        RandomStructure.__init__(self, atoms, **kwargs)
        
        if base_volume is None:
            rc=np.array( [    covalent_radii[atoms[i].number]  for i in range(len(atoms))   ]  )
            base_volume=sum(4/3*np.pi*rc**3)
            
        volume_range=[base_volume*volume_scaling[0], 
                      base_volume*volume_scaling[1]]
        
        if cell_length is None:
            cell_length=(volume_range[1])**(1/3)+2*free_space
        
        self.volume_range=volume_range
        
        self.cell_size=[cell_length]*3
        
        self.atoms.cell=self.cell_size
        
        self.covrad_inside=covrad_inside
            
        self.relaxer=relaxer
        
    def get_box(self):
        volume = self.rng.uniform(self.volume_range[0], self.volume_range[1])
        
        box_length=volume**(1/3)
        box = BoxConstructor.construct_box(self.cell_size, box_length)
        return box

    def get_xyz(self, box, rc):
        x=self.get_coord(box, rc, 0)
        y=self.get_coord(box, rc, 1)
        z=self.get_coord(box, rc, 2)
        return np.array([x, y, z])   

    def get_positions(self, box, atoms):
        
        for atom in atoms:
            if atom.index not in self.cindex:
                rc = covalent_radii[atom.number] if self.covrad_inside else 0
                atom.position=self.get_xyz(box, rc)

        return atoms

    def get(self):
        
        newatoms=self.atoms.copy()
        
        box=self.get_box()
        
        newatoms=self.get_positions(box, newatoms)

        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)
            
        newatoms.wrap()

        return newatoms

    def get_coord(self, box, rc, idx):            
        delta_box = (box[idx][1]-rc) - (box[idx][0]+rc)
        coord=delta_box*self.rng.random() + (box[idx][0]+rc)
        return coord
    
    

class BoxConstructor:
    
    """
    Static methods class to help setup random boxes with the box volumes
    being some multiplum of the total atomic volume of atoms placed inside
    the box
    
    Examples
    --------
    >>> box, cell = BoxConstructor.get_box=(atoms, volume_fraction=0.2)
    """
    
    @staticmethod
    def get_box(atoms, volume_fraction=0.2, free_space=None, cell=None):
        
        """
        Get the indices of atoms constrained by FixAtoms.

        Parameters
        ----------
        atoms: ase.Atoms
            Atoms to be in the box
            Required
        
        volume_fraction: float, optional 
            The fraction of box volume occupied by the total atomic volume. 
            Default is 0.2

        free_space: float:
            Vacuum set on both sides of the box when setting aunit cell.
            Default is None (interpreted as zero)

        cell: ase.Atoms.cell
            Default is None (an automatc cell is set up with length 
                             box_length+2free_space)

        Returns
        -------
        box: numpy.ndarray 
            Array with 3 x 2 entries specifying box limits
        cell: ase.Atoms.cell object
            Cell in which the box is centered
        """
        
        
        box_length=BoxConstructor.get_box_length(atoms, volume_fraction)
        
        if cell is None:
            cell=BoxConstructor.get_unitcell(box_length, free_space)
        else:
            cell=atoms.cell
    
        box = BoxConstructor.construct_box(cell, box_length)
        
        return box, cell
        
    @staticmethod
    def get_box_length(atoms, volume_fraction):
        rc =np.array( [    covalent_radii[atoms[i].number]  for i in range(len(atoms))   ]  )
        
        V_atoms=sum(  (4/3)*np.pi*rc**3  )
        
        box_length=(V_atoms/volume_fraction)**(1/3)
        
        return box_length
        
    @staticmethod
    def construct_box(cell, box_length): 

        box_start=cell[0]/2-box_length/2
        box_end=cell[0]/2+box_length/2
        box=[(box_start, box_end)]*3
    
        return box

    @staticmethod
    def get_unitcell(box_length, free_space):
            
        if free_space is None:
            cell_L=box_length
        else:
            cell_L=box_length+2*free_space
       
        cell=[cell_L, cell_L, cell_L]
        
        return cell


class Random2D(RandomCell):
    
    """
    Generator to create a random 2S unit cells with randomly placed atoms inside.
    The generator makes distortions to the cell object stored on the 
    imported atoms object. 
    
    Examples
    --------
    >>> sgen=Random2D(atoms, minz=5, maxz=10)
    >>> new_atoms=sgen.get()
    """    
    
    def __init__(self, atoms, minz, maxz, scale=0.3, fixed_cell_params=None,
                 covrad_inside=False, relaxer=None, **kwargs):
    
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms object to place in the box.
            Required

        minz : float
            Minimum z-coordinate an atom can be assigned. 
            Required

        maxz : float
            Maximum z-coordinate an atom can be assigned.
            Required.

        scale : float, optional
            The strength of distortions made to the unit cell stored on the atoms object.
            The strength scales with the volume of the original unit cell.
            Default is 0.3.

        fixed_cell_params : list of bool, optional
            Flags indicating which parts of the unit cell should stay fixed (True) or
            be optimized (False). Uses Voigt notation: [xx, yy, zz, yz, xz, xy].
            Default is [False, False, True, True, True, False].

        covrad_inside : bool, optional
            If True, ensures the entire atoms (including covalent radii) are inside the box;
            if False, only the atomic centers are required to be inside.
            Default is False.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        
        self.minz = minz  
        self.maxz = maxz
        self.covrad_inside=covrad_inside
        
        if fixed_cell_params is None:
            fixed_cell_params=[False, False, True, True, True, False]
 
        RandomCell.__init__(self, atoms, scale=scale, 
                            fixed_cell_params=fixed_cell_params, **kwargs)
        
        self.relaxer=relaxer

    
    def get_xyz(self, cell, rc=0):
        x = cell[0] * self.rng.random()
        y = cell[1] * self.rng.random()

        # z-coordinate is a vector along the cell[2] axis
        # with random length between minz and maxz:
        delta_z = (self.maxz-rc) - (self.minz+rc)
        zlength = delta_z * self.rng.random() + (self.minz+rc)
        z = zlength * cell[2] / np.linalg.norm(cell[2])

        return x + y + z
    

    def get(self):
        '''
        Mostly duplication of RandomBox.get()
        '''
        newatoms = self.atoms.copy()
        if not self.fixed_cell_3x3.all():
            cell = self.get_random_cellparams(self.atoms)
        else:
            cell = self.atoms.cell

        newatoms.cell = cell

        newpos = []

        for atom in self.atoms:

            if atom.index in self.cindex:
                pos = atom.position
            else:
                rc = covalent_radii[atom.number] if self.covrad_inside else 0
                pos = self.get_xyz(cell, rc)

            newpos.append(pos)

        newpos = np.array(newpos)

        newatoms.positions = newpos

        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)

        newatoms.wrap()

        return newatoms


class Random2DRanges(RandomStructure):
    
    """    
    Generator for 2D unit cells with a fixed height and ranges of 
    XY aspect ratio, XY area and angle. Atoms are placed randomly 
    inside the cell
    
    Examples
    --------
    >>> sgen=Random2DRanges(atoms, minz=5, maxz=10)
    >>> new_atoms=sgen.get()
    """
    
    def __init__(self, atoms, minz, maxz, base_area=None, area_scaling=[1,3],  
                 xy_ratio_range=[1,1.5], angle_range=[25, 90], height=20, 
                 covrad_inside=False, relaxer=None, **kwargs):
        
        """
        Parameters
        ----------
        atoms : ase.Atoms
            The atoms object to place in the box. 
            Required.

        minz : float
            Minimum z-coordinate an atom can be assigned. 
            Required.

        maxz : float
            Maximum z-coordinate an atom can be assigned. 
            Required.

        base_area : float, optional
            A reference area used to scale the unit cell.
            If None, it is set to the total atomic volume divided by (maxz - minz).
            Default is None.

        area_scaling : list of float, optional
            A list of two values [min_scale, max_scale] defining the allowed area
            range relative to `base_area`.
            Default is [1, 3].

        xy_ratio_range : list of float, optional
            A list [min_ratio, max_ratio] defining the allowed range of XY aspect ratios.
            Default is [1, 1.5].

        angle_range : list of float, optional
            A list [min_angle, max_angle] defining the allowed range of in-plane cell angles (in degrees).
            Default is [25, 90].

        height : float, optional
            Height of the unit cell in the z-direction.
            Default is 20.

        covrad_inside : bool, optional
            If True, ensures the entire atoms (including covalent radii) are within the z-range;
            if False, only the atomic centers are required to be within.
            Default is False.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

                         
        RandomStructure.__init__(self, atoms, **kwargs)
    
        self.minz = minz
        self.maxz = maxz
        self.covrad_inside=covrad_inside
        
        if base_area is None:
            rc=np.array( [    covalent_radii[atoms[i].number]  for i in range(len(atoms))   ]  )
            if minz==maxz:
                base_area=sum( np.pi*rc**2 )
            else:
                dz = (maxz-minz)
                atoms_volume=sum( (4/3)*np.pi*rc**3 )
                base_area=atoms_volume/dz
            
        self.area_range=[base_area*area_scaling[0],
                         base_area*area_scaling[1]]
        
        self.xy_ratio_range=xy_ratio_range
        self.angle_range=angle_range
        self.height=height
        
        self.relaxer = relaxer
        

    def get_xyz(self, cell, rc=0):
        x = cell[0] * self.rng.random()
        y = cell[1] * self.rng.random()

        # z-coordinate is a vector along the cell[2] axis
        # with random length between minz and maxz:
        delta_z = (self.maxz-rc) - (self.minz+rc)
        zlength = delta_z * self.rng.random() + (self.minz+rc)
        z = zlength * cell[2] / np.linalg.norm(cell[2])
        
        return x + y + z

    def get(self):
        '''
        Mostly duplication of RandomBox.get()
        '''

        cell=self.get_cell()
        
        newatoms = self.atoms.copy()
        newatoms.set_cell(cell)
        
        cell=newatoms.cell
        newpos = []

        for atom in self.atoms:

            if atom.index in self.cindex:
                pos = atom.position
            else:
                rc = covalent_radii[atom.number] if self.covrad_inside else 0
                pos = self.get_xyz(cell, rc)

            newpos.append(pos)

        newpos = np.array(newpos)

        newatoms.positions = newpos

        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)

        newatoms.wrap()

        return newatoms
    
    
    def get_cell(self):
        area=self.rng.uniform(self.area_range[0],self.area_range[1])
        xy_ratio=self.rng.uniform(self.xy_ratio_range[0],self.xy_ratio_range[1])
        angle=self.rng.uniform(self.angle_range[0],self.angle_range[1])
        
        angle=angle*np.pi/180

        X=np.array([1.0, 0.0, 0.0])
        Y=np.array([np.cos(angle),np.sin(angle),0])*xy_ratio
        Z=[0,0,self.height]
        
        X_norm=np.linalg.norm(X)
        Y_norm=np.linalg.norm(Y)
        
        current_area=X_norm*Y_norm*np.sin(angle)
        
        g=np.sqrt(area/current_area)
        
        X*=g
        Y*=g
        
        cell=np.array([X,Y,Z])
        
        return cell


class RandomGrapheneSubstrate(RandomStructure):
    
    """    
    Generator for graphene substrates with randomly placed carbon vacancies,
    element substititions, and adsorbate atoms in top.
    
    Examples
    --------
    >>> sgen=RandomGrapheneSubstrate(graphene, n_delete=2, 
                                     substitution_atoms=Atoms(['N']*4),
                                     asorbate_atoms=Atoms(['Fe']*1+['Co']*1) ) 
    >>> new_atoms=sgen.get()
    """
    
    def __init__(self, graphene, n_delete=0, substitution_atoms=None, 
                 adsorbate_atoms=None, delta_z=5, relaxer=None, **kwargs):
        """
        Parameters
        ----------
        graphene : ase.Atoms
            The graphene structure onto which defects or adsorbates will be applied.
            Required.

        n_delete : int, optional
            Number of carbon atoms to remove (vacancies) from the graphene sheet.
            Default is 0.

        substitution_atoms : ase.Atoms, optional
            A collection of atoms used to randomly substitute carbon atoms in the graphene.
            The object can contain an arbitrary number of elements.
            Default is None (no substitutions).

        adsorbate_atoms : ase.Atoms, optional
            Atoms to randomly place on top of the graphene substrate.
            Default is None (no adsorbate atoms).

        delta_z : float, optional
            The vertical distance (z-axis interval) above the graphene surface
            within which adsorbate atoms can be placed.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        
        graphene_atoms=graphene.copy()
        
        for i in range(n_delete):
            graphene_atoms.pop()
        
        atoms=graphene_atoms+adsorbate_atoms

        RandomStructure.__init__(self, atoms, **kwargs)
       
        self.graphene=graphene
                
        self.n_delete=n_delete
        
        if substitution_atoms is None:
            n_substitute=[]
            elem_substitute=[]
        else:
            symbols = substitution_atoms.get_chemical_symbols()
            elem_substitute, n_substitute, = np.unique(symbols, return_counts=True)
       
        self.elem_substitute=elem_substitute 
       
        self.n_substitute=n_substitute
    
        self.adsorbate_atoms=adsorbate_atoms
        
        self.minz=self.graphene[0].position[2] 

        self.maxz=self.minz+delta_z

        self.relaxer=relaxer
    
    
    def get(self):
        
        substrate=self.graphene.copy()
        
        if self.n_delete>0:
            substrate=self.make_holes(substrate)
        
        if len(self.elem_substitute)>0:
            substrate=self.make_substitutions(substrate)
               
        if self.adsorbate_atoms is not None:
            newatoms=self.add_adsorbates(substrate)
        else:
            newatoms=substrate
            
        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)

        newatoms.wrap()

        return newatoms
        
    
    def make_holes(self, graphene):
        
        permutation=self.rng.permutation(len(graphene))
        
        delete_indices=permutation[0:self.n_delete]
        
        delete_indices=sorted(delete_indices, reverse=True)
        
        for index in delete_indices:
            del graphene[index]
            
        return graphene 
    
    
    def make_substitutions(self, graphene):
        
        permutation=self.rng.permutation(len(graphene))
        
        low_index=0
        
        for i in range(len(self.n_substitute)):
            high_index=low_index+self.n_substitute[i]
            
            substitution_indices=permutation[low_index:high_index]

            for index in substitution_indices:
                graphene[index].symbol = self.elem_substitute[i]
            
            low_index+=self.n_substitute[i]
            
        return graphene


    def add_adsorbates(self, graphene):
                
        new_atoms=graphene.copy()
        
        cell=graphene.cell
        
        for atom in self.adsorbate_atoms:
            rc = covalent_radii[atom.number]
            pos = self.get_xyz(cell, rc)
            atom.position=pos
            new_atoms.append(atom)
        
        return new_atoms
    
    
    def get_xyz(self, cell, rc=0):
        x = cell[0] * self.rng.random()
        y = cell[1] * self.rng.random()

        # z-coordinate is a vector along the cell[2] axis
        # with random length between minz and maxz:
        delta_z = (self.maxz-rc) - (self.minz+rc)
        zlength = delta_z * self.rng.random() + (self.minz+rc)
        z = zlength * cell[2] / np.linalg.norm(cell[2])

        return x + y + z
    
    
    def constrain_substrate_atoms(self, graphene):
    
        fixed_atoms_indices=np.arange(len(graphene))
        constraint = FixAtoms(indices=fixed_atoms_indices)
        graphene.set_constraint(constraint)
            
        return graphene
            

class MoleculeOnSubstrate():
    """    
    Generator for randomly placing molecules on top of a substrate.
    the generator doesn't change the molecule itself

    Examples:
    >>> sgen=MoleculeOnSubstrate(molecule_generator, adsorbate, dx=2) 
    >>> new_atoms=sgen.get()
    """
    def __init__(self, molecule_generator, substrate,  dz=3, 
                 relaxer=None, **kwargs):
        
        """
        Parameters
        ----------
        molecule_generator: BEACON structure generator object
            A structure generator with a method molecule=molecule_generator.get() 
            taking no inputs and outputting a molecule subject to custom 
            generation logic, including setting of molecular constraints.
            MoleculeOnSubstrate knows how to handle molecules constrained by
            FixAtoms and FixBondLengths
            Required.

        substrate : ase.Atoms
            The substrate structure on which the adsorbate will be placed.
            Required.

        dz : float, optional
            Displacement interval in which the molecule can be placed on
            top of the substrate. 
            Default is 3 Angstrom.

        relaxer : Relaxer object, optional
            Relaxation procedure applied after structure generation.
            Default is None. (No relaxation)

        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """
        
                
        RandomStructure.__init__(self, substrate, **kwargs)
        self.molecule_generator=molecule_generator
        self.substrate=substrate
        self.dz=dz
        self.relaxer=relaxer
            
    def get(self):
              
        mol=self.molecule_generator.get()
        
        # Set molecule center of mass at cell xy-origin
        mol_com = mol.get_center_of_mass()
        mol.translate(-mol_com)
    
        substrate=self.substrate.copy()
        mol.cell=substrate.cell.copy()

        cell=substrate.get_cell()
        a1, a2 = cell[0], cell[1]
        
        rand_coords = self.rng.random(3)
        
        xy_shift = rand_coords[0] * a1 + rand_coords[1] * a2 
        
        z_substrate_max = max(substrate.positions[:, 2])
        z_mol_min = min(mol.positions[:, 2])
        z_offset = rand_coords[2]*self.dz
        z_shift = z_substrate_max + z_offset - z_mol_min
        
        translation = np.array([xy_shift[0], xy_shift[1], z_shift])
        mol.translate(translation)        
        
        atoms=substrate+mol
        atoms.pbc=[True, True, False]
    
        offset = len(substrate)
       
        constraints = []
        for c in substrate.constraints:
            constraints.append(c)
        
        for c in mol.constraints:
            if isinstance(c, FixAtoms):
                new_indices = [i + offset for i in c.index]
                constraints.append(FixAtoms(indices=new_indices))
            elif isinstance(c, FixBondLengths):
                new_bonds = [[i + offset, j + offset] for (i, j) in c.pairs]
                constraints.append(FixBondLengths(new_bonds))
                
        atoms.set_constraint(constraints)
                        
        if self.relaxer is not None:
            atoms=self.relaxer.run(atoms)
            
        return atoms
        
def auto_find_bonds(mol):
    """
    Method to automatcally identify bonds from a reasonable molecule
    based on covalent bond lengths. 

    Parameters
    ----------
    mol : ase.Atoms object
        Atoms for which we want to find bonds

    Returns
    -------
    bond_indices : list of lists of ints.
        List containing sublists each containing two ints desscribing
        the atom indices 
    """
        
    atoms = mol.copy()

    coord = atoms.positions
        
    dist_matrix = distance_matrix(coord, coord)

    cov_radii_matrix = [[(covalent_radii[i] + covalent_radii[j])
                         for i in atoms.symbols.numbers]
                        for j in atoms.symbols.numbers]

    cov_radii_matrix = 1.1 * np.array(cov_radii_matrix)
        
    bond_mask= (dist_matrix<cov_radii_matrix)
        
    i, j = np.where(bond_mask)
        
    bond_indices = [[int(a), int(b)] for a, b in zip(i, j) if a < b]
                
    return bond_indices



class RandomMolecule(RandomStructure):
    """
    Generator to create a branched structure of atoms, by placing atoms
    one at a time adjacent to another atom.
    Atoms are placed at distances given by the sum of their
    covalent radii times a random multiplier. 
    
    Examples
    -------- 
    >>> sgen=RandomBranch(atoms, llim=0.9, ulim=1.1, placing_order=None)
    >>> new_atoms=sgen.get()
    
    """
    
    def __init__(self, atoms, llim=0.9, ulim=1.1, placing_order=None, 
                 relaxer=None, **kwargs):

        """            
        Parameters:
        atoms: ase Atoms object
            must be supplied
            
        llim: float
            Lower limit for multiplier on covalent radii sum
            Default is 0,9 
            
        ulim: float
            Upper limit for multiplier on covalent radii sum
            Default is 1.1

        placing_order: list of integers
            A list of the atomic indices in the order in which the
            atoms should be placed.
            If None order will be decided randomly for each structure generation
            Default is None
            
        relaxer: Relaxer object 
            relaxation procedure for atoms after structure generation
            default: None (no relaxation)
            
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """

        RandomStructure.__init__(self, atoms, **kwargs)
        
        assert (llim <= ulim), ('Upper limit (ulim) '
                                'should be larger than '
                                'lower limit (llim).')

        self.llim=llim
        self.ulim=ulim
        self.cov_radii = np.array([covalent_radii[atom.number] for atom in self.atoms])
        self.placing_order=placing_order
        self.relaxer=relaxer
        
        if self.placing_order is not None:
            assert len(self.placing_order) == len(self.atoms)
        

    def get(self):
        
        if self.placing_order is None:
            # shuffle order of atoms so the order of placing
            # different elements are random
            shuffled_indices = self.rng.permutation(len(self.atoms))
            newatoms=self.atoms.copy()[shuffled_indices]
            cov_radii=self.cov_radii.copy()[shuffled_indices]
        else: 
            # place atoms in order stores in self.placing_order
            newatoms=self.atoms.copy()[self.placing_order]
            cov_radii=self.cov_radii.copy()[self.placing_order]
        
        
        cell = newatoms.cell.lengths()
    
        newpos=np.zeros((len(newatoms),3))
        
        idx_occupied=[]
    
        if len(self.cindex)==0:  # if no fixed atoms
            newpos[0,:]=newatoms.cell.lengths() / 2
            idx_occupied.append(0)
        else:
            for atom in newatoms:  # if fixed atoms
                if atom.index in self.cindex:
                    newpos[atom.index,:]=atom.position  
                    idx_occupied.append(atom.index)

        for atom in newatoms: # remaining atoms
            if atom.index not in idx_occupied:
                new_position=self.connect_new_atom(atom.index, cell, 
                                                   newpos, 
                                                   cov_radii,
                                                   idx_occupied)
                newpos[atom.index,:] = new_position
                idx_occupied.append(atom.index)
 
        newatoms.positions=newpos
        
        if self.relaxer is not None:
            newatoms=self.relaxer.run(newatoms)
            
        return newatoms
    
        
    def connect_new_atom(self, atom_index, cell, positions, cov_radii, idx_occupied):
                
        while True:
            
            neighbor_index = self.rng.choice(idx_occupied)
            
            cov_atom=cov_radii[atom_index]
            cov_nb=cov_radii[neighbor_index] 
            
            rand_factor = self.rng.uniform(self.llim, self.ulim)
            r=rand_factor*(cov_atom+cov_nb)
                        
            theta, phi = self.rng.random([2])
            theta *= np.pi
            phi *= 2 * np.pi
            pos = self.sph2cart(r, theta, phi)

            new_position = positions[neighbor_index] + pos
            new_position=new_position.reshape((1,3))
            dm = distance_matrix(new_position, positions[idx_occupied])
            
            cov_sums=self.llim*(cov_atom+cov_radii[idx_occupied])
            distances_ok = np.all( dm.min() > cov_sums )
            
            cell_ok = (0.0 <= new_position).all() and (new_position < cell).all()

            if distances_ok and cell_ok:
                return new_position


    
    
class ReadFiles():
    
    """
    Class for generating structures from a list of stored structures
    (mainly for testing)
    
    Examples
    >>> sgen=ReadFiles(filenames)
    >>> sgen.get()
    """
    
    def __init__(self, filenames):
        """
        parameters
        ----------
        flenames: list of files storing atoms objects
            Required        
        """

        self.frames = [read(fname) for fname in filenames]
        self.count = 0

    def get(self):
        atoms = self.frames[self.count]
        self.count += 1
        return atoms


class Rattler(RandomStructure):                
    
    """
    Class for making rattled structures of a given atoms object
       
    Examples
    --------
    >>> sgen=Rattler(atoms, intensity=0.1.)
    >>> sgen.get()
    """   
    
    def __init__(self, atoms, intensity=0.1, **kwargs):
        """
        parameters:
        atoms: ase Atoms object
            Required
            
        intensity: float
            Intensity of the rattling
            default: 0.1
                
        **kwargs
            Additional keyword arguments passed to RandomStructure.
            May include:

            rng : random number generator, optional
                Random number generator for reproducibility.
                Default is `np.random` (not reproducible).
        """
        

        RandomStructure.__init__(self, atoms, **kwargs)

        self.intensity = intensity

    def get(self):
        atoms = self.atoms.copy()
        atoms.rattle(self.intensity,
                     seed=self.rng.randint(100000))
        atoms.wrap()
        return atoms


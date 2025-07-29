import numpy as np
from scipy.linalg import cho_solve
from ase.calculators.calculator import Calculator, all_changes
from ase.neighborlist import NeighborList
from ase.data import covalent_radii
from ase.constraints import FixAtoms

from ase.stress import (full_3x3_to_voigt_6_stress,
                        voigt_6_to_full_3x3_stress)

# each prior must implement a method called potential taking a fingerprint, x 
# with an atoms object attached x.atoms

class ConstantPrior:
    
    """
    Constant prior, with energy = constant and zero forces and zero stresses
    
    Examples
    --------
    >>> prior=ConstantPrior(constant=my_constant)
    >>> energy_and_forces = prior.potential(x)   
    >>> stress = prior.potential_with_stress(x)
    x is here a fingerprint object
    """
    
    def __init__(self, constant=0):
        self.constant = constant

        """
        Parameters
        ----------
        constant: float, optional
            Energy value for the constant.
            Default is 0
        """

    def potential(self, x):
        """
        Method to get prior predictions when training just on energies
        or on forces and energies
        
        Parameters
        ----------
        x : fingerprint object
            Any of the standard BEACON fingerprints

        Returns
        -------
        output : numpy.array
            Array containing prior predicton on energy and forces
        """
        
        d = len(x.atoms) * 3  # number of forces
        output = np.zeros(d + 1)
        output[0] = self.constant
        return output
    
    def potential_with_stress(self, x):
        """
        Method to get prior predictions when training on stresses
        
        Parameters
        ----------
        x : fingerprint object
            Any of the standard BEACON fingerprints

        Returns
        -------
        output : numpy.array
            Array containing prior predicton on energy and forces and stresses
        """
        d = len(x.atoms) * 3
        output = np.zeros(1 + d + 9)
        output[0]=self.constant
        return output
        
    def get_stress(self, x):
        """
        Method to get prior predictions only on stresses
        
        Parameters
        ----------
        x : fingerprint object
            Any of the standard BEACON fingerprints

        Returns
        -------
        stress : numpy.array
            Stress output in Voight notation
        """
        stress=np.array([0., 0., 0., 0., 0., 0.])
        return stress

    def set_constant(self, constant):
        self.constant = constant

    def get_contribution_vector(self, X):
        """
        Method to select what parts of the prior output goes into updating
        the prior constant value. Only the energies should be used, hence
        for each fingerprint the output is a vector starting with 1 and all
        other entries being zero. 

        Parameters
        ----------
        X : list
            List of fingerprints in the database

        Returns
        -------
        numpu.array
            Potential output for all fingerprints in database with
            energy with weight one and forces with weight 0
        """
        self.set_constant(1.)
        return np.hstack([self.potential(x) for x in X])

    def update(self, X, Y, L, use_forces):
        """
        Update the constant to maximize the marginal likelihood.

        The optimization problem:
        m = argmax [-1/2 (y-m).T K^-1(y-m)]

        can be turned into an algebraic problem
        m = [ u.T K^-1 y]/[u.T K^-1 u]

        where u is the constant prior with energy 1 (eV).

        parameters:
        ------------
        X: list
            List of fingerprints in database
        Y: list
            List of targets in database
        L: numpy.array, 
            Cholesky factor of the kernel
        use_forces, bool 
            If Gaussian process is trained on forces
        """

        if use_forces:
            u=self.get_contribution_vector(X)
        else:
            u=np.ones(len(X))
            
        w = cho_solve((L, True), u, check_finite=False)
  
        m = np.dot(w, np.array(Y).flatten()) / np.dot(w, u)   
        
        self.set_constant(m)


       

class CalculatorPrior:
    """
    CalculatorPrior object, allows the user to
    use another calculator as prior function on top of the
    default constant.

    The form of the prior is

    E_p(x) = m*u + E_c(x)

    where m is a constant (energy), u is array with 1's for energy
    and 0 for force components, E_c(x) is the calculator
    potential.

    Examples
    --------
    >>> prior=CalculatorPrior(calculator=my_calculator, constant=my_constant)
    >>> energy_and_forces = prior.potential(x)   
    >>> stress = prior.potential_with_stress(x)
    x is here a fingerprint object
    """

    def __init__(self, calculator, constant=0):
        """
        Parameters:

        calculator: ase.calculator
            One of ASE's calculator objects.
            Required

        constant: float, optional
            Energy value for the constant.
            Default is 0     
        """

        self.calculator = calculator
        self.constant = constant 

    def potential(self, x):
        """
        See method of same name in ConstantPrior
        """     

        atoms=self.get_atoms(x)
        output_size=self.get_output_size(atoms)
        output=np.zeros(output_size)
    
        self.calculator.results.clear()
    
        atoms.calc = self.calculator

        output[0] = atoms.get_potential_energy() + self.constant

        output[1:] = -atoms.get_forces().reshape(-1)

        return output
    
    def potential_with_stress(self, x):
        """
        See method of same name in ConstantPrior
        """
        
        atoms=self.get_atoms(x)
        output_size=self.get_output_size(atoms)
        output=np.zeros(output_size+9)
        
        atoms_output=self.potential(x)
    
        cell_output=self.get_stress(x)
        cell_output=voigt_6_to_full_3x3_stress(cell_output)
        
        output[0:-9]=atoms_output
        output[-9:]=cell_output.flatten()
        return output
    
    def get_stress(self, x):
        """
        See method of same name in ConstantPrior
        """
        stress = self.calculator.results['stress']
        return stress
                
    def get_atoms(self,x):
        """
        Mehod to get atoms from fingerprint. 
        Overwritten in daughter classes. Do not remove.
        """
        atoms=x.atoms.copy()
        return atoms

    def set_constant(self, constant):
        self.constant = constant   

    def get_output_size(self, atoms):  
        """ 
        Method to set the length of output vector.
        Overwritten in daughter classes. Do not remove.
        """
        return 1 + len(atoms) * 3
   
    def get_contribution_vector(self, X):
        """
        See method of same name in ConstantPrior
        """
        self.set_constant(1.)
        return np.hstack([ConstantPrior.potential(self, x) for x in X])

    def update(self, X, Y, L, use_forces):
        """
        See same method of same name in ConstantPrior
        """

        if use_forces:
            u=self.get_contribution_vector(X)
            pv=np.hstack([self.potential(x) for x in X])
        else:
            u=np.ones(len(X))
            pv=np.hstack([self.potential(x)[0] for x in X])
                    
        E_calcprior = (pv - u).flatten()
        
        # w = K\u
        w = cho_solve((L, True), u, check_finite=False)   

        # Set constant
        m = np.dot(w, (np.array(Y).flatten() - E_calcprior)) / np.dot(w, u)
        
        self.set_constant(m)


   
class RepulsivePotential(Calculator):
    """
    Repulsive potential defined as sum_ij U(xij), 
    defining xij = rij / [rc*(Ri + Rj)]
    where Ri and Rj are the radii of atom i an j, rij is their distance
    and rc a scaling constant, the potential U can take two forms:
    
    parabola form (goes to constant/prefactor at rij=0)
    
    U = prefactor * (xij-1)**exponent if rij<=xij
    U = 0 else

    Lennard jones like repulsive form (goes to infinity at rij=0)
    
    U = prefactor * [1/(xij**exponent)-1] - exponent*(1-xij)] if rij<=xij
    U = 0 else

    Examples
    --------
    >>> potential=RepulsivePotential(prefactor=..., rc=...)
    >>> to calculate, use as any ASE calculator, 
    e.g. potential.get_potential_energy()
    
    
    Parameters
    ----------
    prefactor: float, optional
        Strength constant for potentals
        Default is 1
    
    rc: float, optional
        Multplier on sum of atomic radii
        Default is 0.9
        (can also be imported as a list giving the radius of each atom)
    
    potential_type: string ('parabola' or 'LJ'), optional
        String specifying what mode of the potential is used. 
        Default is 'LJ' 
    
    exponent: float, optional
        Exponent used in potentials
        Default is 2
        
    extrapotentals: list of objects, optional
        List of additional objects capable of calculating, energy, 
        forces and stresses. Any objects with the following methods:
        potential(atoms),  forces(atoms),  stress(atoms)
        default: None (no extra potential used) 
    """

    implemented_properties = ['energy', 'forces', 'stress']

    default_parameters = {'prefactor': 1,'rc': 0.9, 
                          'potential_type': 'LJ', 'exponent': 2, 
                          'extrapotentials': None}    
    
    nolabel = True

    def calculate(self, atoms=None,
                  properties=['energy', 'forces', 'stress'],
                  system_changes=all_changes):
        """
        General ASE calculate method to store output in calculator.results
        """
        Calculator.calculate(self, atoms, properties, system_changes)
        
        # get parameters
        rc = self.get_radii(atoms)

        neighbor_list = NeighborList(np.array(rc), skin=0,
                                     self_interaction=False)     
        neighbor_list.update(atoms)

        energy, forces, stress = self.get_energy_and_derivatives(atoms, rc, neighbor_list)
        
        # set energy and forces
        self.results['energy'] = energy   
        self.results['forces'] = forces    
        
        assert(atoms.cell.rank==3)
        self.results['stress'] = stress.flat[[0, 4, 8, 5, 2, 1]] / atoms.get_volume()

        if self.parameters.extrapotentials is not None:
            assert isinstance(self.parameters.extrapotentials, list)
            self.get_extra_potential(atoms)


    def get_radii(self, atoms):
        """
        Method to get atomic radii.
        Overwritten in daughter class, don't Remove
        """
        
        if type(self.parameters.rc)==list:
            rc=self.parameters.rc
        else:
            covrads = [ covalent_radii[self.atoms[i].number] for i in range(len(self.atoms)) ]
            rc=self.parameters.rc*np.array(covrads)
    
        return rc



    def get_energy_and_derivatives(self, atoms, rc, neighbor_list):
        """
        Method to get energy, forces and stresses for the total atoms object
        using the repulsive prior function

        Parameters
        ----------
        atoms : ase.atoms
            Atoms under consideration
        rc : lits
            Atomic radii
        neighbors : ase.neighborlist
            Object containing all neighbor information

        Returns
        -------
        energy : floar
            Total energy
        forces : numpy.array
            Total forces
        stress : numpy.array
            Total stresses
        """
        
        energy, forces = self.setup_energy_forces(atoms)   
        
        stress = np.zeros((3, 3))

        for a1 in range(len(atoms)):
            
            neighbors, d = self.get_distance_info(atoms, a1, neighbor_list)
            
            if len(neighbors)>0:     
                
                potential, derivative = self.get_potential(a1, rc, d, neighbors)   
                
                energy = self.update_energy(energy, potential)
                
                forces = self.update_forces(forces, derivative, a1, neighbors) 
                
                stress=self.update_stress(stress, derivative, d)
                
        return energy, forces, stress
    
    
    
    def setup_energy_forces(self, atoms):
        """
        Method to setup output formats. 
        Overwritten in daughter classes. Dont remove
        """
        energy = 0.0
        forces = np.zeros((len(atoms), 3)) 
        return energy, forces



    def get_distance_info(self, atoms, atom_idx, neighbor_list):
        """
        Method to calculate the vectors between atoms in periodic as well
        as nonperiodic boundary conditions

        Overwritten in daughter classes. Dont Remove

        Parameters
        ----------
        atoms : ase.atoms
            Atoms object of consideration
        atom_idx : int
            index of one of the atoms in the atoms object
        neighbor_list : ase.neighborlist
            object containing all nerigborinformation

        Returns
        -------
        neighbors : list
            list of all neighbors of the given atom
        d : numpy.array
            vectors between all neighbors of the given atom
        """
        
        positions = atoms.positions
            
        cell = atoms.cell
        
        neighbors, offsets = neighbor_list.get_neighbors(atom_idx)
            
        cells = np.dot(offsets, cell)
            
        d = positions[neighbors] + cells - positions[atom_idx]
        
        return neighbors, d  
        

    def get_potential_function_LJ(self, prefactor, x, exp):
        """ 
        Method to calculate potential and derivative for the Lennard Jones 
        like repulsive potential
        """
        # Potential function with zero value and zero derivative at x=1.
        if x<=1:
            value = prefactor*(1/x**exp-1) - exp*prefactor*(1-x)
            deriv = exp*prefactor*(1-1/x**(exp+1))
        else:
            value = 0
            deriv = 0
        return value , deriv


    def get_potential_function_parabola(self, prefactor, x, exp):
        """ 
        Method to calculate potential and derivative for the parabolar 
        repulsive potential
        """
        # Potential function with zero value and zero derivative at x=1.
        
        if x<=1:
            value = prefactor*(x-1)**exp
            deriv = exp*prefactor*(x-1)**(exp-1)
        else:
            value = 0
            deriv = 0
        return value , deriv



    def get_x_potential(self, r, crs):
        """
        Get value and derivative of the repulsive potentials
        """
        
        x = r/crs
        
        potential = np.zeros(len(x))
        derivative=np.zeros(len(x))
        
        prefactor=self.parameters.prefactor
        exp=self.parameters.exponent
        
        if self.parameters.potential_type=='LJ':
            for i, xx in enumerate(x):
                potential[i], derivative[i] = self.get_potential_function_LJ(prefactor,xx, exp)
        elif self.parameters.potential_type=='parabola':
            for i, xx in enumerate(x):
                potential[i], derivative[i] = self.get_potential_function_parabola(prefactor,xx, exp)
        else:
            raise RuntimeError('potential_type={:s} not known.'
                               .format(self.parameters.potential_type))
            
        return potential, derivative 
        


    def radial_info(self, d, rc, atom_index, neighbors):
        """
        Get distances between atoms as well as the sum of atomic radii
        """
        
        r2 = (d**2).sum(1)
        r=np.sqrt(r2)
        
        crs=rc[atom_index]+np.array( [   rc[n] for n in neighbors   ]  )

        return r, crs


    def cartesian_conversion(self, derivative, d, r):
        """ Convert from polar to cartesian coordinates """
        r_block=np.tile(r,(len(d[0,:]),1)).T
        polar_to_cart=d/r_block
        derivative_cartesian=derivative[:,np.newaxis]*polar_to_cart
        
        return derivative_cartesian


    def get_potential(self, atom_index, rc, d, neighbors):     
        """
        Method to calculate the potential value and its derivatives
        in cartesian coordinates for a single atom and all its neighbors

        Parameters
        ----------
        atom_index : int
            Index of a given atom in the system
        rc : lits
            Atomic radii
        d : numpy.array
            Distance vectors between atom of index atom_index and all neighbors
        neighbors : ase.neighborlist
            Object containing all neighbor information

        Returns
        -------
        x_potential : float
            the energy
        cartesian_derivatives: numpy.array
            the derivatives of the energy
        """
        r, crs = self.radial_info(d, rc, atom_index, neighbors)  

        x_potential, x_potential_derivative = self.get_x_potential(r, crs)

        derivative = x_potential_derivative * 1/crs

        cartesian_derivative = self.cartesian_conversion(derivative, d, r)  

        return x_potential, -cartesian_derivative

    
    def update_energy(self, energy, potential):
        """ Method to update the total energy """
        energy += potential.sum()
        return energy
    
    
    def update_forces(self, forces, derivative, atom_index, neighbors):
        """ Method to update the total forces """
        forces[atom_index] -= derivative.sum(axis=0)
    
        for a2, f2 in zip(neighbors, derivative):
            forces[a2] += f2
        return forces
    
    def update_stress(self, stress, derivative, d):
        """ Method to update the total stresses """
        stress -= np.dot(derivative.T, d)
        return stress

    def get_extra_potential(self, atoms):
        """
        Method to add extrapotential values on top of the repulsive potential
        """
        for potential in self.parameters.extrapotentials:  
            self.results['energy']  += potential.potential(atoms)
            self.results['forces'] += potential.forces(atoms)
            self.results['stress']  +=  potential.stress(atoms)
    

class TallStructurePunisher:
    """
    Extra potental to punish atoms being below zlow or above zhigh
    
    E += strength * (z - zlow)**2 if z < zlow
    E += strength * (z - zhigh)**2 if z > zhigh
    E = 0                          else

    Notice, the potential only works if the cell is nonperiodic
    in the z-direction meaning that the zz, xz and yz components
    of the tress tensor is not calculated
    
    Examples
    --------
    >>> extrapotental=TallStructurePunisher(zlow=..., zhigh=...)
    >>> energy=extrapotential.potential(atoms)
    >>> forces=extrapotential.forces(atoms)
    >>> stress=extrapotential.stress(atoms)
    """

    def __init__(self, zlow=0.0, zhigh=5.0, strength=2.0):
        """
        Parameters
        ----------
        zlow : float, optional
            Height uner which the potential starts
            Default is 0
        zhigh : float, optional
            Height over which the potential starts
            Default is 5
        strength : float, optional
            Strength constant of the potential
            Default is 2
        """
        
        self.zlow = zlow
        self.zhigh = zhigh
        self.strength = strength

    def potential(self, atoms):
        """
        Parameters
        ----------
        atoms : ase.atoms
            Atoms for which we want the energy

        Returns
        -------
        result : floar
            The energy
        """
        
        result = 0.0
        
        fixed_atoms=self.get_constrained_atoms(atoms)
        
        for i in range(len(atoms)):
            if i in fixed_atoms:
                continue
            
            z = atoms.positions[i, 2]
            if z >= self.zhigh:
                result += self.strength * (z - self.zhigh)**2
            elif z <= self.zlow:
                result += self.strength * (z - self.zlow)**2
        return result
        
    def forces(self, atoms):
        """
        Parameters
        ----------
        atoms : ase.atoms
            Atoms for which we want the energy

        Returns
        -------
        result : numpy.array
            The forces
        """
        
        result = np.zeros((len(atoms), 3))
        
        fixed_atoms=self.get_constrained_atoms(atoms)
        
        for i in range(len(atoms)):
            if i in fixed_atoms:
                continue
                    
            z = atoms.positions[i, 2]
            if z >= self.zhigh:
                result[i, 2] += self.strength * 2 * (z - self.zhigh)
            elif z <= self.zlow:
                result[i, 2] += self.strength * 2 * (z - self.zlow)
        return -result

    def stress(self, atoms):
        """
        Parameters
        ----------
        atoms : ase.atoms
            Atoms for which we want the energy

        Returns
        -------
        stress : numpy.array
            The stresses on the unit cell
        """
    
        results=np.zeros(6)
        
        return results
    
    def get_constrained_atoms(self, atoms):
        """ Method to constrain fixed atoms """
        constr_index = []
        for C in atoms.constraints:
            if isinstance(C, FixAtoms):
                constr_index = C.index
        return np.array(constr_index)
        
 
class AreaPunisher:
    """
    Extra potential to punish too small or large unit cells in 
    directions x and y. Potential shape:
        
    E = strength * (A-A_small)**2  if A < A_small
    E = strength * (A-A_large)**2  if A > A_large
    E = 0                          else

    Here A is the area in xy plane.

    Notice, the potential only works properly if system 
    is nonperiodic in z-direction and if the cell has the form  
    [ [a,b,0],  [c,d,0],  [0,0,e] ]


    Examples
    --------
    >>> extrapotential=AreaPunisher(A_small=..., A_large=...)
    >>> energy=extrapotential.potential(atoms)
    >>> forces=extrapotential.forces(atoms)
    >>> stress=extrapotential.stress(atoms)
    
    
    See TallStructurePunisher for method descriptions
    """
    
    def __init__(self, A_small=20.0, A_large=200.0, strength=10.0):

        """
        Parameters
        ----------
        A_small : float, optional
            Area under which the potential starts
            Default is 20.0
        A_large : float, optional
            Area over which the potential starts
            Default is 200.0
        strength : float, optional
            Strength constant for the potential
            Default is 10.0
        """

        assert(A_small<A_large)

        self.A_small = A_small
        self.A_large = A_large
        self.strength = strength

    def potential(self, atoms):
        """ Get energy """
        cell = atoms.cell
        
        A = self.area(cell)
     
        if A<=self.A_small:
            result = self.strength * (A - self.A_small)**2
        elif A>=self.A_large:
            result = self.strength * (A - self.A_large)**2
        else:
            result=0
            
        return result

    @staticmethod
    def area(cell):
        """ Get the cell area """
        # If cell is not flat in the z-direction I think this will
        # mess up the calculation
        return cell.area(2)

    def forces(self, atoms):
        """ Get forces """
        return np.zeros((len(atoms), 3))

    def stress(self, atoms):
        """ Get stresses """
        
        results=np.zeros(6)     
        cell = atoms.cell
        A = self.area(cell)
        
        if A<=self.A_small:
            stress= 2*self.strength * (A - self.A_small)*A  / atoms.get_volume()
            results[0]=stress
            results[1]=stress
        elif A>=self.A_large:
            stress= 2*self.strength * (A - self.A_large)*A  / atoms.get_volume()
            results[0]=stress
            results[1]=stress
        
        return results


class VolumePunisher:
    """
    Extra potential to punish too small or large unit cells 
    in directions x, y, z. Potential shape:
        
    E = strength * (V-V_small)**2  if V < V_small
    E = strength * (V-V_large)**2  if V > V_large
    E = 0                          else

    Here V is the volume.
        
    Examples
    --------
    >>> extrapotential=VolumePunisher(V_small=..., V_large=...)
    >>> energy=extrapotential.potential(atoms)
    >>> forces=extrapotential.forces(atoms)
    >>> stress=extrapotential.stress(atoms)
    
    See TallStructurePunisher for method descriptions
    """
    
    def __init__(self, V_small=20.0, V_large=200.0, strength=10.0):
        """
        Parameters
        ----------
        V_small : float, optional
            Volume under which the potential starts
            Default is 20.0
            
        V_large : float, optional
            Volume over which the potential starts
            Default is 200.0
            
        strength : float, optional
            Strength constant of the potential
            Default is 10.0
        """
        assert(V_small<V_large)
        
        self.V_small = V_small
        self.V_large = V_large
        self.strength = strength

    def potential(self, atoms):
        """ Get energy """
        
        V=atoms.get_volume()   
     
        if V<=self.V_small:
            result = self.strength * (V - self.V_small)**2
        elif V>=self.V_large: 
            result = self.strength * (V - self.V_large)**2
        else:
            result=0
            
        return result


    def forces(self, atoms):
        """ get forces """
        return np.zeros((len(atoms), 3))

    def stress(self, atoms):
        """ get stress """
        results=np.zeros(6)     

        V = atoms.get_volume()

        if V<=self.V_small:
            stress= 2*self.strength * (V - self.V_small)*V  / V
            results[0]=stress
            results[1]=stress
            results[2]=stress
        elif V>=self.V_large:
            stress= 2*self.strength * (V - self.V_large)*V  / V
            results[0]=stress
            results[1]=stress
            results[2]=stress                        
        
        return results


class CalculatorExtraPotential:
    """
    Class to assign another calculator as an extra potential, 
    e.g. a ML potential. 
    
    Examples
    --------
    >>> extrapotential=VolumePunisher(calculator=my_calculator)
    >>> energy=extrapotential.potential(atoms)
    >>> forces=extrapotential.forces(atoms)
    >>> stress=extrapotential.stress(atoms)
    
    See TallStructurePunisher for method descriptions
    """
     
    def __init__(self, calculator):
        
        """
        parameters
        ----------
        calculator: ase.calculator
            Any ASE calculator object to preidt energies, forces and stresses
            Required
        """
        
        self.calculator = calculator
        
    def potential(self, atoms):
        """ Get energy """
        self.calculator.results.clear()
        atoms = atoms.copy()
        atoms.calc = self.calculator
        atoms.get_potential_energy()
        return self.calculator.results['energy'] 
    
    def forces(self, atoms):
        """ Get forces """
        return self.calculator.results['forces']  
    
    def stress(self, atoms):
        """ Get stresses """
        return self.calculator.results['stress']
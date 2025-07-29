import warnings
from copy import copy

import numpy as np
from ase.calculators.calculator import Calculator, all_changes
from ase.calculators.singlepoint import SinglePointCalculator

from scipy.linalg import cho_solve

def copy_image(atoms):
    """
    Copy an image, so that it is suitable as a training set point.
    It returns a copy of the atoms object with the single point
    calculator attached
    """
    # Check if the input already has the desired format
    if atoms.calc.__class__.__name__ == 'SinglePointCalculator':
        # Return a copy of the atoms object
        calc = copy(atoms.calc)
        atoms0 = atoms.copy()

    else:
        atoms.get_forces()

        # Initialize a SinglePointCalculator to store this results
        calc = SinglePointCalculator(atoms, **atoms.calc.results)

    atoms0 = atoms.copy()
    atoms0.calc = calc
    return atoms0


class GPCalculator(Calculator):
    
    """
    Dlass for using BEACON Model class as an ase calculator
    
    Examples:
    >>> calc=GPCalculator(model, calculate_stress=True)
    >>> use as normal ase calculator
    """
    
    implemented_properties = ['energy', 'forces', 'stress', 'free_energy']
    nolabel = True

    def __init__(self, model, calculate_stress=False, error_method=None):
        """
        Parameters
        ----------
        Model: A BEACON model object
            model with the capability of predicting energies and gradents based
            on a gaussian process and an atomic fingerprint
            Required
            
        calculate_uncertainty : bool, optional
            If uncertanty should be calculated. 
            The default is False.
            
        calculate_stress : bool, optional
            If stress should be calculated or not. 
            The default is False.
        
        error_method : function, optional
            A method that implements the BEACON CustomError Exception
            to prematurely terminate a surrogate relaxation in case Atoms
            object break some condition.
            The default is None
        """


        Calculator.__init__(self)

        self.model = model
        self.calculate_stress=calculate_stress
        self.error_method=error_method

    def calculate(self, atoms=None,
                  properties=['energy', 'forces',  'stress'],
                  system_changes=all_changes):
        """
        Calculate the energy, forces and stress for a
        given Atoms structure. Predicted energies can be obtained by
        *atoms.get_potential_energy()*, predicted forces using
        *atoms.get_forces()* and predictes stresses using *atoms.get_stress()*
        """
        
        
        if self.error_method is not None:
            self.error_method(atoms)
        
        # Atoms object.
        Calculator.calculate(self, atoms, properties, system_changes)
        
        results = self.model.calculate(atoms, with_stress=self.calculate_stress)
    
        # Results:
        self.results['energy'] = results[0]
        self.results['forces'] = -results[1]
        self.results['free_energy'] = results[0]
        
        if self.calculate_stress:
            self.results['stress'] = results[2]
        
            
            
class PriorCalculator(Calculator):
    """
    Class for testing BEACON prior potentials
    
    -------------------
    >>> calc=GPCalculator(potential, calculate_stress=True)
    >>> use as normal ase calculator
    """
    
    implemented_properties = ['energy', 'forces', 'stress', 'free_energy']
    nolabel = True

    def __init__(self, prior, calculate_stress=False):
        """
        parameters:
        prior: a prior potential based as an ase calculator
            must be supplied
         
        calculate_stress: bool
            If stress should be calculated or not 
            default: False
        """
        
        Calculator.__init__(self)

        self.prior=prior
        self.calculate_stress=calculate_stress
    
    def calculate(self, atoms=None,
                  properties=['energy', 'forces',  'stress'],
                  system_changes=all_changes):
        
        # Atoms object.
        Calculator.calculate(self, atoms, properties, system_changes)
        
        self.prior.calculate(atoms)
        
        self.results['energy'] = self.prior.results['energy']
        self.results['forces'] = self.prior.results['forces']
        self.results['free_energy']=self.prior.results['energy']
        
        if self.calculate_stress:
            self.results['stress'] = self.prior.results['stress']
        
        

            
            
            
            
            
            

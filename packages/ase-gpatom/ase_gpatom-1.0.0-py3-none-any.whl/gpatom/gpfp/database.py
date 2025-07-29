
import numpy as np
from gpatom.gpfp.kerneltypes import EuclideanDistance

from ase.stress import (full_3x3_to_voigt_6_stress,
                        voigt_6_to_full_3x3_stress)


class Database:
    
    """
    Database class to store results used to train the Gaussian process.
    automatically instantiated and used through the Model class.     
        
    Examples
    --------
    database=Database(fingerprints=fingerprint_set, 
                      energies=energy_set)

    """
    

    def __init__(self, fingerprints=tuple(), energies=tuple(),
                 forces=tuple(), stress=tuple()):

        """
        parameters:
            fingerprints: Set of fingerprint objects
    
        energies: Set of energies
    
        forces: Set of forces for training with coordinate gradients
        
        stress: Set of stresses for training with stresses
        """

        if not (len(fingerprints) == len(energies) == len(forces)):
            raise ValueError('Length of all input data do not match.')

        self.fingerprintlist = list(fingerprints)
        self.energylist = list(energies)
        self.forceslist = list(forces)
        self.stresslist = list(stress)

    def __eq__(self, db):
        if len(self) != len(db):
            return False

        # Compare distances of fingerprints:
        for i in range(len(self)):
            for j in range(len(self)):
                fp1 = self.fingerprintlist[i]
                fp2 = db.fingerprintlist[i]
                if EuclideanDistance(fp1, fp2) < 1e-4:
                    return False

        return True

    def __len__(self):
        '''
        Return number of data points in the database.
        '''
        return len(self.fingerprintlist)

    def copy(self):
        return Database(self.fingerprintlist, self.energylist,
                        self.forceslist)

    def add(self, fingerprint, energy):
        '''
        Add fingerprint and energy to database
        '''
        self.fingerprintlist.append(fingerprint)
        self.energylist.append(energy)
    
    def add_forces(self, forces):
        """
        Add forces to database
        """
        self.forceslist.append(forces)
    
    def add_stress(self, stress):
        """
        Add stress to database
        """
        if np.size(stress)==6:
            stress=voigt_6_to_full_3x3_stress(stress)
            
        self.stresslist.append(stress)

    def get_all_fingerprints(self):
        return self.fingerprintlist

    def replace_fingerprints(self, new_fingerprints):
        """
        Replace fingerprints with a new set of fingerprints
        """
        self.fingerprintlist.clear()
        self.fingerprintlist=new_fingerprints

    def get_all_targets(self, use_forces, use_stress):
        '''
        Return all energies, forces and stresses ordered as
        [e1, f11x, f11y, f11z, f12x, f12y, ...f1Nz, e2, f21x, f21y,
        f21z, f22x, f22y, ... sxx, sxy,...,szz]
        '''

        targets=[]
        for index in range(len(self.fingerprintlist)):
            
            targets+=[self.energylist[index]]
            
            if use_forces:
                targets+=list(-self.forceslist[index].flatten())
                
            if use_stress:
                targets+=list(self.stresslist[index].flatten())
                
        return targets

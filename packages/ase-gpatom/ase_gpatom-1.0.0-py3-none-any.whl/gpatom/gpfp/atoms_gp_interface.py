import numpy as np
from gpatom.gpfp.calculator import copy_image

from gpatom.gpfp.fingerprint import FingerPrint
from gpatom.gpfp.gp import GaussianProcess
from gpatom.gpfp.database import Database

from gpatom.gpfp.kerneltypes import EuclideanDistance

from ase.stress import (full_3x3_to_voigt_6_stress,
                        voigt_6_to_full_3x3_stress)

class Model:
    """
    An interface class to communicate between the Gaussian process, the 
    fingerprint and the database. This model optimizes on the surrogate 
    potential energy only
    
    Examples
    ---------
    1 Instantiate class
    >>> model=Model(gp=GaussianProcess, fp=FingerPrint)
    
    2 Initially train a gp from a list of atoms objects
    >>> model.add data_points(train_images)
    
    3 Get prediction on new structure (with or without stress)
    >>> energy, gradients, (stress) = calculate(atoms, with_stress=True/False)
    
    4. Fit hyperparameters
    >>> model.fit_hps()
    
    5. Update fingerprints
    >>> model.update_fps()
    """ 
       

    def __init__(self, gp=GaussianProcess, fp=FingerPrint,
                 hp_optimizer=None, fp_updater=None):  
        """
        Parameters
        ----------
        gp : GaussianProcess object
            Gaussian process class to be used in the model
            default is GaussianProcess
     
        fp : FingerPrint creator object
            Fingerprint class to be used in the model
            default is FingerPrint      
            
        hp_optimizer : HPFitter, optional
            Object to uptimize hyperparameters. 
            If None, no hyperparameter optimization is performed.
            Default is None.
            
        fp_updater : FPUpdater, optional
            Object for automatically updating fingerprint parameters. 
            If None, no updates are made.
            Default is None.
        """

        self.data=Database()
        self.gp=gp
        self.fp=fp
        self.hp_optimizer=hp_optimizer
        self.fp_updater=fp_updater
        
    
    def new_fingerprint(self, atoms, **kwargs):    
        """
        Turn atoms into a fingerprint
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to calculate fiingerprint for
            
        **kwargs : TYPE
            extra inputs for specific fingrprint

        Returns
        -------
        fingerprint object
        """
        
        return self.fp.get(atoms=atoms, **kwargs)



    def add_data_points(self, train_images):       
        """
        Calculate fingerprints and add features and corresponding targets
        to the database of 'data' and retrain.

        Parameters
        ----------
        train_images : List of ase.Atoms objects
            
        Returns
        -------
        None.
        """
        
        if type(train_images)!=list:
            train_images=[train_images]
                
        for im in train_images:
            image = copy_image(im)
            fp = self.new_fingerprint(image)
            self.data.add(fp, image.get_potential_energy(apply_constraint=False))
            
            if self.gp.use_forces:
                self.data.add_forces(image.get_forces(apply_constraint=False))
            
            if self.gp.use_stress:
                self.data.add_stress(image.get_stress(apply_constraint=False))
            
        self.train_model()


    def train_model(self):       
        """
        Trains a Gaussian process with data allready in database
        
        Returns
        -------
        None.
        """

        features = self.data.get_all_fingerprints()

        targets=self.data.get_all_targets(self.gp.use_forces, 
                                          self.gp.use_stress)
        
        self.gp.train(features, targets)

        

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
            Exrtra parameters to go into prediction of fingerprint

        Returns
        -------
        energy : float
            The predicted energy
        
        gradients : numpy.array
            The predicted coordinate gradients
        stress : numpy.array
            The prediced stresses, only if with_stress is True
        """
     
        
        x=self.new_fingerprint(atoms, **kwargs)
    
        natoms=len(atoms)
    
        f, V = self.gp.predict(x, get_variance=False)
        energy = f[0]
        gradients=f[1:]
        
        if self.gp.use_stress:
            gradients, stress = self.separate_grads(gradients, natoms)
            return energy, gradients, stress
            
        gradients = gradients.reshape(natoms, -1)
        if with_stress:
            stress=self.gp.predict_stress(x)
            return energy, gradients, stress
                    
        return energy, gradients  
    

    def get_energy_and_forces(self, atoms):
        """
        Predict energy, forces and uncertainty
        
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object for which we want predictions

        Returns
        -------
        energy : float
            predicted energy
        forces : numpy.array
            predicted coordinate derivatives
        uncertainty : numpy.array
            uncertainty on the energy
        """
        
        fp=self.new_fingerprint(atoms)
        
        energy, forces, uncertainty_squared = self.gp.get_properties(fp)
        
        uncertainty = np.sqrt(uncertainty_squared)
        
        return energy, forces, uncertainty


    def get_predicted_stress(self, atoms):
        """
        predict stresses on atoms object

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms for which we want to predict stresses

        Returns
        -------
        stress : numpy.arrray
            stressses on unit cell
        """
        
        fp=self.new_fingerprint(atoms)
            
        stress=self.gp.predict_stress(fp)
        return stress

    def separate_grads(self, gradients, natoms):
        """
        Separate all atomic coordinate derivative values from
        unit cell derivatives

        Parameters
        ----------
        gradients : numpy.array
            All gradients
        natoms : int
            Number of atoms in structures

        Returns
        -------
        atom_grads : numpy.array
            Derivatives on atomid coordinates
        cell_grads : numpy.array
            Derivatives on unit cell

        """
        
        atom_grads = gradients[:-9].reshape(natoms, -1)
        cell_grads = gradients[-9:].reshape(3,3)
        cell_grads = full_3x3_to_voigt_6_stress(cell_grads)
        return atom_grads, cell_grads 
    
    
    def fit_hps(self):
        """
        Optimize hyperparameters
        """
        if self.hp_optimizer is None:
            return
        
        self.hp_optimizer.fit(self.gp)
    
        
    def update_fps(self):
        """
        Update fingerprint parameters
        """
        if self.fp_updater is None:
            return
        
        fingerprints = self.data.get_all_fingerprints()
        self.fp_updater.update(fingerprints, self.fp)
        self.recalculate_fingerprints()
             
        
    def calculate_distances(self, atoms):              
        """
        Calculate the distances between the training set and
        given atoms in fingerprint space

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms we wan distances with respect to

        Returns
        -------
        distances : numpy.array
            Distances in fingerprint space too structures in database

        """
        fp0 = self.new_fingerprint(atoms)

        distances = np.zeros(len(self.data), dtype=float)

        for i, x in enumerate(self.data.fingerprintlist):
            distances[i] = EuclideanDistance.distance(fp0, x)

        return distances


    def recalculate_fingerprints(self):
        """
        Method to replace old set of fingerprints in database with a new set.
        The Model is subsequently retrained

        Returns
        -------
        None.
        """
        
        features = self.data.get_all_fingerprints()
        
        image_list=[f.atoms for f in features]
        
        new_fingerprints=[self.new_fingerprint(image) for image in image_list]
        
        self.data.replace_fingerprints(new_fingerprints)
        
        self.train_model() 
        

    

    
class LCBModel(Model):
    """
    An interface class to communicate between the Gaussian process, the 
    fingerprint and the database. This model optimizes on a LCB 
    acquisition function surface
    
    Examples
    ---------
    1 Instantiate class
    >>> model=LCBModel(gp=GaussianProcess, fp=FingerPrint, kappa=2)
    
    2 Initially train a gp from a list of atoms objects
    >>> model.add data_points(train_images)
    
    3 Get prediction on new structure (with or without stress)
    >>> energy, gradients, (stress) = calculate(atoms, with_stress=True/False)
    
    4. Fit hyperparameters
    >>> model.fit_hps()
    
    5. Update fingerprints
    >>> model.update_fps()
    """ 
    
    
    def __init__(self, gp=GaussianProcess, fp=FingerPrint,
                 hp_optimizer=None, fp_updater=None, kappa=2):  
        """
        parameters
        ----------
        gp : GaussianProcess object
            Gaussian process class to be used in the model
            default is GaussianProcess
     
        fp : FingerPrint creator object
            Fingerprint class to be used in the model
            default is FingerPrint
            
        kappa: float
            Contant for weighting of uncertainty in LCB model
            default is 2
        """
        
        super().__init__(gp=gp, fp=fp, 
                         hp_optimizer=hp_optimizer, 
                         fp_updater=fp_updater)
        
        self.kappa=kappa
        
    def calculate(self, atoms, with_stress=False, **kwargs):
        """
        Parameters
        ----------
        atoms : ase.Atoms
            Atoms to predict on 
            
        with_stress : TYPE, optional
            If stress should be calculated and outputted 
            Default is False.
            
        **kwargs : dictionary
            exrtra parameters to go into prediction of fingerprint

        Returns
        -------
        acq : float
            The predicted acquisition value
            
        gradients : numpy.array
            The predicted coordinate vise acquisition derivatve values
    
        stress : numpy.array
            The prediced cell wise acquisition derivatve values.
            Only if with_stress is True
        """

        x=self.new_fingerprint(atoms, **kwargs)        
        
        f, V, dkdx = self.gp.predict(x, get_variance=True, return_dkdx=True)
                
        energy = f[0]
        gradients = f[1:]
    
        if self.gp.use_stress:
            unc, acq, dacq_r, dacq_c = self.calculate_acq(x, energy, gradients, V, dkdx)
            return acq, dacq_r, dacq_c
        
        unc, acq, dacq_r = self.calculate_acq(x, energy, gradients, V, dkdx)
                            
        if with_stress:
            dacq_c=self.calculate_stress(x, unc)
            return  acq, dacq_r, dacq_c
        
        return acq, dacq_r
    
    
    
    def calculate_acq(self, x, energy, gradients, V, dkdx):
        """
        Parameters
        ----------
        x : a fingerprint object
            fingerprint object
        energy : float
            predicted energy
        gradients : numpy.array
            the coordinate vise derivatives of the energy
        V : numpy.array
            The uncertainty 
        dkdx : numpy.array
            derivative of the kernel vector w.r.t atomic coordinates

        Returns
        -------
        unc: float
            The uncertainty
            
        acq: float
            The acquisition value
            
        dacq_r: numpy.array
            The acquisition coordinate derivatives
            
        dacq_c: numpy.array
            The acquisition unit cell derivatives
            Only if gp.use_stress is True
        """
        
        if self.gp.use_stress:
            var=V[0,0]
            unc=np.sqrt(var)
            
            f_var_1 = V[1: , 0]
            f_var_2 = V[0 , 1:]
            
            dvar = f_var_1 + f_var_2

            dunc=1/(2*unc)*dvar   
        
            grads_r, grads_c = self.separate_grads(gradients, len(x.atoms))
        
            dunc_r, dunc_c = self.separate_grads(dunc, len(x.atoms))
            dunc_c/=x.atoms.get_volume()
        
            acq=energy-self.kappa*unc
            dacq_r=grads_r-self.kappa*dunc_r
            dacq_c=grads_c-self.kappa*dunc_c
            
            return unc, acq, dacq_r, dacq_c
        
        if self.gp.use_forces:
            
            var=V[0,0]
            unc=np.sqrt(var)
            
            #quick solution
            f_var_1 = V[1: , 0]
            f_var_2 = V[0 , 1:]
            dvar = f_var_1 + f_var_2
            dvar=dvar.reshape(len(x.atoms),-1)
            
            dunc=1/(2*unc)*dvar
            
            '''
            #long general solution
            natoms=len(x.atoms)
            dk_dr = [np.concatenate((self.gp.kernel.kernel_function_gradient(x, x2).reshape(1,natoms*3),
                                     self.gp.kernel.kernel_function_hessian(x2, x) ),
                                    axis=0) for x2 in self.gp.X] 
            
            dk_dr = np.array(dk_dr).reshape(-1, natoms*3)
                        
            dkdr_Ck = np.einsum('ij,i->j', dk_dr, self.gp.Ck[:,0])
            dvar_r=-2*dkdr_Ck
            dvar_r=dvar_r.reshape(natoms, 3)
            dunc=1/(2*unc)*dvar_r
            '''
            
        else:
            var=V[0]
            unc=np.sqrt(var)
            
            self_grad=self.gp.kernel.kerneltype.kernel_gradient(x, x)
            dkdx_Ck = np.einsum('ijk,i->jk', dkdx, self.gp.Ck)
            dvar_r=2*(self_grad-dkdx_Ck)
            
            dunc=1/(2*unc)*dvar_r
            
            '''
            #long solution. kept here in case its needed at some point
            self_grad=self.gp.kernel.kerneltype.kernel_gradient(x, x)
            k = self.gp.kernel.kernel_vector(x, self.gp.X)
            k_grad=np.array([self.gp.kernel.kerneltype.kernel_gradient(x, x2)
                             for x2 in self.gp.X])

            Ck_grad=cho_solve((self.gp.L, self.gp.lower), k_grad,                  
                              overwrite_b=False, check_finite=True)
            k_gradCk = np.einsum('ijk,i->jk', k_grad, self.gp.Ck)
            kCk_grad =  np.einsum('i,ijk->jk', k, Ck_grad)
            dvar_r=2*self_grad-k_gradCk-kCk_grad
            '''
            
        gradients=gradients.reshape(len(x.atoms),-1)
        acq=energy-self.kappa*unc
        dacq_r=gradients-self.kappa*dunc
    
        return unc, acq, dacq_r
    
    
    def calculate_stress(self, x, unc):
        """
        Calculate derivative of acquisition function w.r.t cell parameters
        
        Parameters
        ----------
        x : a fingerprint object
            DESCRIPTION.
        unc : float uncertainty
            DESCRIPTION.

        Returns
        -------
        dacq_c : numpy.array
            The acqusition cell derivatives

        """
        
        stress, dk_dc = self.gp.predict_stress(x, return_dkdc=True)
        
        if self.gp.use_forces:
            dkdc_Ck = np.einsum('ijk,i->jk', dk_dc, self.gp.Ck[:,0])
        else:
            dkdc_Ck = np.einsum('ijk,i->jk', dk_dc, self.gp.Ck)

        dvar_c=-2*dkdc_Ck
                
        volume=x.atoms.get_volume()
        dvar_c/=volume
        dunc_c=1/(2*unc)*dvar_c.flat[[0, 4, 8, 5, 2, 1]]
            
        dacq_c=stress-self.kappa*dunc_c
        
        return dacq_c

from gpatom.gpfp.calculator import copy_image, GPCalculator

from gpatom.beacon.inout import FileWriter, FileWriter2

from ase.optimize import BFGS
from ase.io import read, write, Trajectory

from ase.parallel import world, broadcast

from ase.data import covalent_radii
from scipy.spatial import distance_matrix

import numpy as np
import warnings
import os

from ase.filters import UnitCellFilter

import signal

from ase.build import niggli_reduce

class TimeoutError(Exception):
    """ 
    Custom exception to interrupt a surrogate relaxation process 
    if it exceeds a specified time limit.
    
    Use by settng surropt_timeout in BEACON not to None. 
    """
    pass

class CustomError(Exception):
    """
    Exception for BEACON to safely terminate a surrogate relaxation 
    without causing a crash.

    Use by writing a method that raises the error if atoms fail to satify
    one or more conditions. Import the method into a relaxer under the 
    keyword error_method. 
    """
    pass

class BEACON():

    """
    Bayesian Exploration of Atomic Configurations for Optimization
    --------------------------------------------------------------

    Optimizer to search for the global minimum energy.

    Find optimal structure of a set of atoms given the
    number of atoms, size and periodicity of the unit cell
    and the potential. The model uses Gaussian process
    to predict the global potential energy landscape, by
    representing the atomic structure by a rotationally,
    translationally and permutationally invariant fingerprint,
    and searches for the absolute minimum of the landscape.

    The original idea behind the method is published
    (along with the code GOFEE) as
        Efficient Global Structure Optimization with a
        Machine-Learned Surrogate Model
        M. K. Bisbo, B. Hammer
        Physical Review Letters, vol. 124, 086102 (2020)
        https://doi.org/10.1103/PhysRevLett.124.086102

    BEACON is published as
        Global optimization of atomic structures with
        gradient-enhanced Gaussian process regression
        S. Kaappa, E. G. del R\'io, K. W. Jacobsen
        Physical Review B, vol. 103, 174114 (2021)
        https://doi.org/10.1103/PhysRevB.103.174114

    Example
    -------
    >>> go = BEACON(calculator=my_calculator, model=my_model, 
                    initatomsgen=my_generator)
    >>> go.run()
    """

    def __init__(self, calculator, model, initatomsgen,
                 surropt=None, checker=None, acq=None, 
                 init_atoms=None, logger=None, ninit=2, 
                 ndft=100, nsur=None, prepare_atoms_for_dft=None,  
                 write_surropt=False, write_surropt_trajs=False, 
                 stopfitsize=10000, stop_fp_update_size=10000, 
                 surropt_timeout=None, make_rand_if_fail=True):
        
        """
        Parameters
        ----------
        calculator : ase.calculator
            Any ASE Calculator capable of calculating energies, 
            forces and stresses
            Required

        model : Model
            Predictive model for energy and forces.
            Required

        initatomsgen : InitatomsGenerator
            Generator for creating initial random atomic structures.
            Required

        surropt : SurrogateOptimizer, optional
            Optimizer for relaxing structures using a surrogate model. 
            If None, structures are not relaxed.
            Default is None.

        checker : Checker, optional
            Checker for validating surrogate-relaxed structures. 
            If None, no checking is done.
            Default is None.

        acq : AcquisitionFunction, optional
            Acquisition function used to score final candidate structures. 
            If None, model output is used directly. 
            Default is None.

        init_atoms : list of ase.Atoms, optional
            User-supplied list of initial training structures. 
            If None, random structures are generated  using `initatomsgen`.
            Default is None.

        ninit : int, optional
            Number of random initial structures to generate if `init_atoms` 
            is not provided.
            Default is 2.

        ndft : int, optional
            Maximum number of DFT evaluations to perform. 
            The search terminates after this number.
            Default is 100.

        nsur : int, optional
            Number of surrogate relaxations performed at each step.
            Default is `world.size`.
            
        prepare_atoms_for_dft: function, optional
            A function taking atoms as input and outputs a modified atoms object
            with properties important for DFT calculation, e.f. initial charges
            or magnetic moments. NB: dont use atoms.copy() in this method,
            or issues about non-attached calculators may occur.
            Default is None

        write_surropt : bool, optional
            If True, all surrogate relaxations are written to file `surropt.xyz`.
            Default is False.
            
        write_surropt_trajs : bool, optional
            If True, the trajectory of all surrogate optimizations will be
            outputted during the run.  Not recommended for large runs. 
            Default is False.
            
        stopfitsize : int, optional
            Number of DFT calculations after which hyperparameter 
            optimization stops. Set to zero to disable all fp updates. 
            Default is 10000 (i.e., never stops automatically).

        stop_fp_update_size : int, optional
            Number of DFT calculations after which fingerprint parameter 
            updates stops. Set to zero to disable all fp_updates.
            Default is 10000 (i.e., never stops automatically).

        surropt_timeout : float, optional
            Timeout in minutes for a surrogate relaxation. 
            If exceeded, the process is terminated.
            Default is None (no timeout).

        make_rand_if_fail : bool, optional
            If True, a random structure is generated in case no valid 
            structure is accepted.
            Default is True.
        """
        
        self.stopfitsize=stopfitsize
        
        self.stop_fp_update_size=stop_fp_update_size
        
        self.write_surropt=write_surropt
        self.write_surropt_trajs=write_surropt_trajs
        self.make_rand_if_fail=make_rand_if_fail

        self.calculator=calculator
        self.prepare_atoms_for_dft=prepare_atoms_for_dft
        self.model=model
        self.initatomsgen=initatomsgen
        self.surropt=surropt
        self.checker=checker
        self.acq=acq

        if logger is None:
            logger=Logger()
        self.logger=logger

        # Atoms reader/writer:
        self.atomsio = BEACONAtomsIO()


        if (len(self.model.data)>0):
            raise RuntimeError("Don't import models with pre-existing databases."
                               "import list of atoms objects instead: atoms=list")


        if init_atoms is None:
            init_atoms = []
            for i in range(ninit):
                init_atoms.append(self.initatomsgen.get_random())

        if type(init_atoms)!=list:
            init_atoms=[init_atoms]

        self.init_atoms = init_atoms
        # These lines makes sure that all processors have the same initial structures.
        #it is absolutely crucial that this comes after generating the random structures.
        # This one deletes atoms constraints   
        for i in range(len(self.init_atoms)):
            self.init_atoms[i] = broadcast(self.init_atoms[i], root=0)

        self.natoms=len(self.init_atoms[0])

        # Run parameters:
        self.ndft = ndft
        self.nsur = nsur if nsur is not None else world.size
        assert self.nsur > 0


        self.set_initial_frames(self.init_atoms)

        self.initatomsgen.setup_lob(self.init_atoms)

        self.model.add_data_points(self.init_atoms)

        self.index = len(self.init_atoms)

        if surropt_timeout is not None:
            surropt_timeout=int(surropt_timeout*60)
            
        self.surropt_timeout=surropt_timeout

    def run(self):
        """
        Performs search of global optimum structure. 
        The result is the following files.
        
        init_structures.xyz: Structures in the initial raining set
        structures_dft.xyz: Structures identified in BEACON runs
        extras.xyz: Randoms rtuctures made if no acceptable candidate is
                    found in a run
        surropt.xyz: The final structure of all surrogate relaxations performed  
                    (only if write_surropt is True)
        info.txt: text file describing key values for each BEACON iteration
        log.txt: text file reporting the progress of each beacon iteration
        
        Returns
        -------
        None

        """

        if self.checker is None:
            self.logger.log_from_master('Structure checks set to False!!!')

        self.logger.log_init_structure_info(self.init_atoms)
        # RUN GLOBAL SEARCH
        while self.index < self.ndft:

            self.logger.log_stepinit(self.index, len(self.model.data))

            self.logger.log_lob_energies(self.initatomsgen.lob.energies)
            # optimize hyper parameters before running the search

            if len(self.model.data) <= self.stop_fp_update_size:
                self.model.update_fps()
            
            if len(self.model.data) <= self.stopfitsize:
                self.model.fit_hps()

            (best_atoms, best_e, best_f, 
             best_u, best_subindex) = self.get_candidate()

            if best_atoms is None:  # if no structures were accepted
                self.add_random_structures()
                self.logger.log_random_structure()
                self.index += 1
                continue

            try:
                self.calculate_properties(best_atoms)
                real_e = best_atoms.calc.results['energy'] 
                real_f = best_atoms.calc.results['forces'].flatten()
                self.logger.log_real_energy(self.index, real_e)
            except Exception as err:
                self.logger.log_from_master('Something went wrong: {} '
                                            .format(str(err)))
                
                if self.make_rand_if_fail:
                    self.add_random_structures()
                    self.logger.log_random_structure()
                    self.index += 1
                else:
                    self.logger.log_from_master('Continuing...')
                    
                continue

            # WRITE RESULT XYZ
            best_atoms.info['Ndft']=self.index
            self.atomsio.write_xyz(best_atoms, strtype='result')

            # WRITE RESULT NUMBERS
            distances = self.model.calculate_distances(best_atoms)

            fmax_real = self.logger.get_max_force(real_f)
            fmax_pred = self.logger.get_max_force(best_f)

            data = dict(index=self.index,
                        pred=best_e,
                        real=real_e,
                        unc=best_u,
                        diff=real_e - best_e,
                        fmax_real=fmax_real,
                        fmax_pred=fmax_pred,
                        mindist=distances.min(),
                        maxdist=distances.max(),
                        ntrain=len(self.model.data),
                        prior=self.model.gp.prior.constant,
                        **self.model.gp.hp,
                        aweight=self.model.fp.fp_args['aweight'])

            self.logger.write_output(data)

            # UPDATE LIST OF BEST
            self.initatomsgen.lob.update(new_atoms=best_atoms,
                                         candidate_index=best_subindex)


            # UPDATE GAUSSIAN PROCESS
            self.model.add_data_points([best_atoms])

            # ITERATE
            self.index += 1


        self.logger.log_from_master('Maximum number of steps '
                                    '({}) reached.'.format(self.ndft))

    def set_initial_frames(self, atoms):
        """
        Calculate energies and forces for initial training images,
        and save to files.
        """

        for i in range(len(atoms)):
            try:
                self.calculate_properties(atoms[i], attatch_calc=False)
            except RuntimeError:
                self.calculate_properties(atoms[i])
                tmp = copy_image(atoms[i])
                atoms[i] = tmp

            self.atomsio.write_xyz(atoms[i], strtype='init')


    def get_candidate(self):
        """
        Find best candidate structure
        """
        
        it_result=self.get_candidate_pool()

        (best_atoms, best_e, best_f, 
         best_u, best_acq, best_subindex) = it_result.distribute()

        if best_atoms is None:  # if no atoms were accepted
            self.logger.log_novalid()
        else:
            self.logger.log_bestinfo(self.index, best_subindex, 
                                     best_e, best_u, best_acq)

        return best_atoms, best_e, best_f, best_u, best_subindex



    def get_candidate_pool(self):
        """ 
        Generates the pool of all candidate structures.
        This include generating random structures, relaxig them and
        checking if the structure is ok or should be discarded
        """

        it_result = IterationResult(self.natoms)

        for j in range(self.nsur):

            # DISTRIBUTE SURROGATE RELAXATIONS
            if j % world.size != world.rank:
                continue

            # CREATE NEW STRUCTURES
            testatoms = self.initatomsgen.get(j)

            # SURROGATE RELAXATION
            if self.surropt is not None:
            
                if (self.surropt_timeout is not None):
                    signal.signal(signal.SIGALRM, self.surropt_timeout_handler)
                    signal.alarm(self.surropt_timeout)
                    
                if self.write_surropt_trajs:
                    output_file='opt_{:03d}_{:03d}.xyz'.format(self.index, j)
                else: 
                    output_file=None
                    
                try:                        
                    testatoms, success = self.surropt.relax(testatoms, self.model,
                                                            output_file=output_file)
                except (TimeoutError, CustomError) as err:
                    structure_ok=False
                    string='Relaxation Failed: {} '.format(str(err))
                    self.logger.log_nonvalid_structures(structure_ok, string,
                                                        index=self.index, subindex=j)                    
                    continue
                    
                finally:
                    if (self.surropt_timeout is not None):
                        signal.alarm(0)
                    
            else:
                success=False


            energy, forces, unc = self.model.get_energy_and_forces(testatoms)

            # WRITE RELAXED SURROGATE STRUCTURES TO FILE
            if self.write_surropt:
                self.write_surropt_results(testatoms, energy, forces, unc, success)

            self.logger.log_relaxedinfo(index=self.index, energy=energy,
                                        success=success, unc=unc, subindex=j)

            #CHECK IF STRUCTURES ARE ACCEPTABLE
            if self.checker is not None:
                distances = self.model.calculate_distances(testatoms)
                structure_ok, string = self.checker.check(atoms=testatoms,
                                                  distances=distances)

                self.logger.log_nonvalid_structures(structure_ok, string,
                                                    index=self.index, subindex=j)

            else:
                structure_ok = True

            # GET ACQUSITION VALUE FOR ALL ACCEPTED STRUCTURES AND SAVE
            if structure_ok:
                if self.acq is not None:
                    my_acq = self.acq.get(energy=energy, uncertainty=unc)
                else:
                    my_acq= self.model.calculate(testatoms)[0]

                better_acq = it_result.is_better(my_acq)
                if better_acq:
                    it_result.update(dict(energy=energy,
                                          forces=forces.flatten().copy(),
                                          unc=unc,
                                          atoms=testatoms,
                                          acq=my_acq,
                                          subindex=j))
        return it_result


    def surropt_timeout_handler(self, signum, frame):
        raise TimeoutError("Relaxation timed out")


    def write_surropt_results(self, atoms, energy, forces, unc, success):
        atoms.info['index']=self.index
        atoms.info['gp_energy']=energy
        atoms.info['gp_uncertainty']=unc
        atoms.info['success']=success
        self.atomsio.write_xyz(atoms, strtype='surropt', parallel=False)
        

    def read_pool(self, index=None):
        """
        Method to read a pool made by get_candidate_pool
        index. lets you decide if you want pool from a specific cycle
        """

        pool_all=read('surropt.xyz',':')

        if index is None:
            pool=pool_all
        else:
            pool=[atoms for atoms in pool_all if atoms.info['index']==index]

        energies=[atoms.info['gp_energy'] for atoms in pool]
        uncertainty=[atoms.info['gp_uncertainty'] for atoms in pool]
        success=[atoms.info['success'] for atoms in pool]

        return pool, energies, uncertainty, success



    def add_random_structures(self):
        """
        Add a random structure from IniatAtomsStructure rgen if no
        valid candidate structures
        """
        random_structure_successfull=False
        count=0
        while not random_structure_successfull:
            try: 
                atoms=self.generate_valid_random_structure()
                #broadcast atomsobject from rank 0 to all processors
                atoms = broadcast(atoms, root=0)
    
                # Evaluate:
                self.calculate_properties(atoms)
                random_structure_successfull=True
            except Exception as err:
                count+=1
                self.logger.log_from_master('Random structure failed: {} '
                                            'Retrying...'.format(str(err)))
                
                if count>3:
                    raise Exception

        # candidate_index=np.inf just means not part of list of best.
        self.initatomsgen.lob.update(new_atoms=atoms,
                                     candidate_index=np.inf)



        new_structure = [copy_image(atoms)]
        self.model.add_data_points(new_structure)

        # Write extra_NNN.xyz file:
        if world.rank == 0:
            self.atomsio.write_xyz(atoms, strtype='extra', parallel=False)

    
    def generate_valid_random_structure(self):
        """
        Make sure randomly generated srucure is valid
        """
        valid_structure_found=False
        while not valid_structure_found:
            atoms=self.initatomsgen.get_random()
 
            if self.checker is None:
                valid_structure_found=True
            else:                
                distances=self.model.calculate_distances(atoms)
                if self.checker.check_fingerprint_distances(distances):
                    valid_structure_found=True
            
        return atoms


    def calculate_properties(self, atoms, attatch_calc=True):
        '''
        Calculate energy and forces of atoms. Return potential energy.
        '''
        
        if self.prepare_atoms_for_dft is not None:
            atoms = self.prepare_atoms_for_dft(atoms)
        
        if attatch_calc:
            if len(atoms.constraints)==0:
                niggli_reduce(atoms)
                atoms.center()
                atoms.wrap()
                
            atoms.calc=self.calculator

        atoms.get_potential_energy(force_consistent=None, 
                                   apply_constraint=False)
        atoms.get_forces(apply_constraint=False)
            
        return

        
class Logger:
    
    """
    Logger class to log progress of BEACON global optimizer
    
    Examples 
    --------
    >>> logger=Logger(output=name, logoutput=name)
    >>> logger.write_output(dict)   (write dictionary to info file )    
    >>> logger.log_from_master(txt)  (write to text string log file )
    """
    
    def __init__(self, output='info.txt',
                 logoutput='log.txt'):
        """
        parameters
        ----------
        output: string, optional
            name for output of beacon inout.py FileWriter2.  
            default is info.txt
        
        logoutput: string, optional
            name for output of beacon inout.py FileWriter.  
            default is log.txt
        """
        
        if world.rank == 0:
            self.infofile = FileWriter2(output, printout=False)

        # All processors
        self.logfile = FileWriter(logoutput, printout=False,
                                  write_time=True)
        
        
    def write_output(self, dictionary):
        if world.rank == 0:
            self.infofile.write(dictionary)

    def log_from_master(self, txt):
        if world.rank == 0:
            self.logfile.write(txt)

    def log_real_energy(self, index, real_e):

        txt = 'Index: {:03d} Real energy: {:06f}'
        txt = txt.format(index, real_e)
        self.log_from_master(txt)

    def get_max_force(self, forces):
        '''
        Get maximum absolute force of the given force array.
        '''
        forces = forces.reshape(-1, 3)
        fmax=np.max(np.linalg.norm(forces, axis=1))

        return fmax

    def log_init_structure_info(self, atoms):
        world.barrier()
        for i in range(len(atoms)):
            txt = ('Init structure {:03d} '
                   'Energy: {:.02f} eV '
                   'Max force: {:.02f} eV/Ang'
                   .format(i,
                           atoms[i].get_potential_energy(),
                           self.get_max_force(atoms[i].get_forces())))

            self.log_from_master(txt)

    def log_stepinit(self, index, data_size):
        txt = ('Index: {:03d} Training data size: {:5d}'
               .format(index, data_size ))
        self.log_from_master(txt)

    def log_relaxedinfo(self, index, energy, success, unc, subindex):
        ''' Log from all processors '''

        notconverged = ''
        if not success:
            notconverged = '(Not converged)'
        self.logfile.write('Index: {:03d} Subindex: {:03d} '
                           'Energy: {:.04f} Uncertainty: {:.04f} {}'
                           .format(index, subindex,
                                   energy, unc,
                                   notconverged))

    def log_novalid(self):
        txt = 'No valid structure found.'
        self.log_from_master(txt)

    def log_random_structure(self):
        txt = 'Random structure made.'
        self.log_from_master(txt)

    def log_bestinfo(self, index, best_subindex, best_e, best_u, best_acq):
        txt = 'Index: {:03d} '
        txt += 'Best structure: '
        txt += 'Subindex: {:03d} '
        txt += 'Energy: {:04f} '
        txt += 'Uncertainty: {:04f} '
        txt += 'Acquisition: {:04f} '
        txt = txt.format(index, best_subindex, best_e,
                         best_u, best_acq)
        self.log_from_master(txt)


    def log_lob_energies(self, listofbest_e):
        '''
        Write energies from list-of-best-structures
        to log file.
        '''

        if len(listofbest_e) == 0:
            txt = 'List of best energies is empty.'
            self.log_from_master(txt)
        else:
            txt = 'List of best energies:'
            self.log_from_master(txt)
            for i, e in enumerate(listofbest_e):
                txt = ('Index: {:03d} Energy: {:04f}'
                       .format(i, e))
                self.log_from_master(txt)

    def log_nonvalid_structures(self, structure_ok, string, index, subindex):
        if not structure_ok:
            txt=('Index: {:03d} Subindex: {:03d} '
                 .format(index, subindex) + string)
            self.logfile.write(txt)


class LowerBound:
    """
    Class to calculate acquisition function by the lower confidence bound
    at the end of surrogate relaxation only
    
    Examples
    --------
    acq=LowerBound(kappa=2)
    acq_value=acq.get(energy, uncertainty)
    """
    
    def __init__(self, kappa=2):
        self.kappa = kappa
    
        """
        parameters    
        ----------
        kappa: float, optional
            Emphasis on uncertainty in acquisition function
            default is 2
        """

    def get(self, energy, uncertainty):
        return energy - self.kappa * uncertainty
    

class StructureList:
    """
    This class handles the list of best structures in BEACON.
    
    Examples
    --------
    >>> lob=StructureList(images=..., n=..., flim=...)
    >>>> lob.update(atoms=..., candidate_index=...)
    """

    def __init__(self, images, n, flim):

        """
        Parameters
        ----------

        atoms: list
            list of ase.Atoms objects
            Required
        n: int
            Number of structures to store in the list
            Required
        flim: float
            Force threshold. If the maximum force of an atomic
            structure is below this number, it is excluded
            from the list.
            Required
        """

        self.n = n  # number of structures
        self.structurelist = []
        self.update_list_by_many(images)
        self.flim = flim


    def update_list_by_many(self, images):
        self.structurelist += images
        self.sort_structurelist()

    def update_list_by_one(self, atoms, overwrite_index=None):
        if overwrite_index is None:
            self.structurelist += [atoms]
        else:
            self.structurelist[overwrite_index] = copy_image(atoms)
        self.sort_structurelist()

    def sort_structurelist(self):
        '''
        Sort images by their potential energies and create a list
        of the sorted structures with maximum length of self.n
        '''

        argsort = np.argsort(self.energies)
        self.structurelist = [copy_image(self.structurelist[i])
                              for i in argsort[:self.n]]

    @property
    def energies(self):
        '''
        Return all potential energies for the structures in the list.
        '''
        return [atoms.get_potential_energy()
                for atoms in self.structurelist]


    def update(self, new_atoms, candidate_index):
        '''
        Update the list of best structures.
        Returns True if structure is converged. False if not.
        '''

        e = new_atoms.get_potential_energy()
        f = new_atoms.get_forces()


        # Check if all the forces are below the threshold:
        real_local_min = (np.max(np.linalg.norm(f.reshape(-1, 3),
                                                axis=1)) < self.flim)

        # Check if the structure was obtained
        # by relaxing a structure on the previous list-of-best:
        one_of_listofbest = candidate_index < len(self)

        # If it is a real local minimum, return True
        if real_local_min:
            if one_of_listofbest:
                # delete image from list of best
                self.structurelist.pop(candidate_index)
            return

        # Don't add but update if it the structure
        # was obtained by relaxing something already on the list:
        overwrite_index = None
        if one_of_listofbest and (e < self.energies[candidate_index]):
            overwrite_index = candidate_index

        # Sort list by energy and make sure it's size
        # is self.nbest (or smaller):
        self.update_list_by_one(new_atoms, overwrite_index=overwrite_index)

        return

    def __len__(self):
        return len(self.structurelist)

    def __getitem__(self, i):
        return self.structurelist[i]


class InitatomsGenerator:
    """
    Generator to give structures for surrogate relaxations in BEACON.
    The relaxations start from some of the already visited low-energy
    structures, the same structures rattled, or random structures.
    
    
    Examples
    --------
    1. Instantiate
    >>> initatomsgen=InitatomsGenerator(sgen=..., rgen=..., ...)
    2. attatch list of best:
    >>> initatomsgen.setup_lob(atoms_list)
        (will be done automatically in BEACON)
    3. get structure from sgen with candidate index i:
    >>> initatomsgen.get(i)
    4. get structure from rgen:
    >>> initatomsgen.get_random()
    """      
      

    def __init__(self, sgen, rgen=None, nrattle=0, nbest=0, realfmax=0.1,
                 rattlestrength=0.5, rng=np.random, rattle_seed_int=100000,
                 lob=None):
        """
        Parameters
        ----------
        sgen: structure generator object
            Required
            
        rgen:structure generator object, optional
            Default is same as sgen
            
        nrattle: int, opional
            How many rattled structues should be generated
            Default is 0
            
        nbest: int, optional
            how many structures should be made from list of best
            Default is 0
            
        realfmax: float, optional
            realfmax for import to StructureList
            default: 0.1
            
        rattlestrength: float, optional
            How hard the rattled structures are rattled    
            Default is 0.5
            
        rng: random number generator, optional 
            Random number generator for ranum number generation
            in rattling of atoms
            Default is np.random 
                
        rattle_seed_int: int, optional
            Seed for random atom rattling
            Default is 100000
                
        lob: StructureList object, optional
            Default is None.
        """
        
        self.nrattle = nrattle
        self.nbest=nbest
        self.realfmax=realfmax
        self.rattlestrength = rattlestrength
        self.rng = rng
        self.sgen = sgen
        self.lob=lob
        self.rattle_seed_int=rattle_seed_int

        if rgen is None:
            self.rgen=sgen
        else:
            self.rgen=rgen


    def setup_lob(self, atoms):

        if self.lob is None:
            self.lob = StructureList(atoms,
                                     n=self.nbest,
                                     flim=self.realfmax)


    def get(self, i=None):
        """
        Parameters
        ----------
        i: int
            Index that indicates what type of structure is
            returned. (one of best, rattled one of best, or
            random). If None, structure from sgen is given.
            
        Returns
        -------
        atoms: ase.atoms object
            The generated structure
        """

        n_best = self.get_nbest()

        if i is None:
            i = np.inf

        atoms = self.get_atoms(i, n_best)

        return atoms

    def get_nbest(self):
        '''
        Get number of best structures in the current state of
        list-of-best.
        '''

        if self.lob is None:
            return 0

        return len(self.lob)

    def get_atoms(self, i, n_best):
        '''
        Get atoms of different types based on the index 'i'
        and the number of best structures 'n_best'.
        '''
        # One of best:
        if i < n_best:
            atoms = self.get_one_of_best_atoms(i)

        # Rattled one of best:
        elif self.get_rattled_criterion(i, n_best):

            atoms = self.get_rattled_one_of_best(i, n_best)

        # One given by structure generator:
        else:
            atoms = self.sgen.get()

        return atoms

    def get_one_of_best_atoms(self, i):
        '''
        Get i'th structure from the list of best.
        '''
        atoms=self.lob[i].copy()
        return atoms

    def get_rattled_one_of_best(self, i, n_best):
        ''' Get i'th structure as a rattled version as one of the best' '''
        atoms = self.lob[i % n_best].copy()

        atoms.rattle(self.rattlestrength,
                     seed=self.rng.randint(self.rattle_seed_int))
        atoms.wrap()
        return atoms

    def get_rattled_criterion(self, i, n_best):
        return (n_best > 0) and (i < n_best + self.nrattle )
    

    def get_random(self):
        ''' specific structure generator for making random structures
        if no surrogate candidates were accepted'''
        atoms=self.rgen.get()
        return atoms


class SurrogateOptimizer:
    
    """
    Class to handle local optimizations in BEACON.
    
    Examples
    --------
    >>> surropt=SurrogateOptimizerUnitCell(fmax=0.05, with_unit_cell=True)
    >>> surropt.relax(atoms=my_atoms, model=my_model)
    """      

    def __init__(self, fmax=0.05, relax_steps=100,
                 with_unit_cell=False, 
                 fixed_cell_params=None, 
                 error_method=None):
        """
        Parameters
        ----------
        fmax: float, optional
            Convergence criteria. Size of largest force component
            befor the surrogate relaxer stops 
            Default is 0.05
            
        relax_steps: int, optiional
            Number of steps taken by relaxer
            Default is 100

        with_unit_cell: bool. optional 
            If the unit cell should be optimized
            Default is False
            
        fixed_cell_params: list of 6 bools, optional 
            Bool giving what voight components of the cell is not optimized
            xx, yy, zz, yz, xz, xy
            Default is [False, False, False, False, False, False]
                                        
        error_method: function, optional 
            A customly written method to terminate 
            a surrogate relaxation by Raisng CustomError from BEACON. 
            Default is None
        """
        
        self.fmax = fmax
        self.relax_steps = relax_steps
        self.error_method=error_method
        
        self.with_unit_cell=with_unit_cell
        
        if fixed_cell_params is None:
            fixed_cell_params = [False, False, False, False, False, False]
            
        self.mask = [not elem for elem in fixed_cell_params]


    def relax(self, atoms, model, output_file=None):
        """
        Relax atoms in the surrogate potential from model.
        eventually write an output trajectory file   

        Parameters
        ----------
        atoms : ase.atoms
            Atoms to relax
        model : Model
            BEACON model class
        output_file : string, optional
            name of ouput file. e.g. 'opt.traj'
            Default is None (no output file)

        Returns
        -------
        atoms : ase.atoms
            The relaxed atoks
        success : bool
            If relaxation converged successfully
        """
                
        atoms.calc=GPCalculator(model,
                                calculate_stress=self.with_unit_cell,
                                error_method=self.error_method)

        if self.with_unit_cell:
            opt_object = UnitCellFilter(atoms, mask=self.mask)
        else:
            opt_object=atoms

        opt = BFGS(atoms=opt_object,
                   maxstep=0.2,
                   logfile=os.devnull,
                   master=True)
        
        if output_file is not None:
            traj = Trajectory(output_file,
                              'w', atoms, master=True)
            opt.attach(traj)
        
        success = opt.run(fmax=self.fmax, steps=self.relax_steps)

        return atoms, success

    
class Checker:
    """
    Class to check candidates structures from surrogate optimizations
    will output if the structure is accepted or not and a string
    specifying why if/why the structure was rejected
    
    Examples
    --------
    >>> checker=Checker(dist_limit=..., rimit=...)
    >>> structure_ok, output_string=checker.check(atoms, distances)  
    """    
    
    def __init__(self, dist_limit=None, rlimit=None, 
                 disconnect_limit=None, angle_limit=None, 
                 volume_limits=None):
        """
        Parameters
        ----------
        dist_limit: float, optional
            The minimal allowed distance in fingerprint space between 
            a new candidate and all structures in the database
            Default is None (dont check)
            
        rlimit: float, optional
            The minimum distance between any two atom centers in an atoms 
            object as a multiplier of the atomic covalent radii.
            rlimit=1 means the minimum distance is covalent radius of atom1 +
            the covalent radius of atom 2. 
            Default is None (dont check)
            
        disconnect_limit: float, optional
            The max distance an atom can have to at least one other atom 
            in the system for the system to be seen as connected
            Default is None (don't check)
            
        angle_limit : float, optional
            Smallest acceptible unit cell angle
            Default is None (don't check)
            
        volume_limits : list of two floats, optional
            Limits for acceptable unit cell volumes. 
            first entry, lower limit, second entry, upper limit.
            Default is None (don't check)
        """
        
        self.dist_limit = dist_limit
        self.rlimit = rlimit        
        self.volume_limits=volume_limits
        
        self.disconnect_limit=disconnect_limit
        
        if angle_limit is not None:
            angle_limit=90-angle_limit
        
        self.angle_limit=angle_limit


    def check_atomic_distances(self, atoms):
        """
        Check if atoms are too close to each other. 
        Returns True if distances are large enough 
        """
        atoms = atoms.copy()
        atoms.wrap()
        atoms.set_constraint() # Necessary for repeat to work in all cases
        atoms = atoms.repeat([1 + int(c) for c in atoms.pbc])

        coord = atoms.positions

        # Atoms too close to each other:
        dm = distance_matrix(coord, coord)
        dm += 10.0 * np.eye(len(dm))

        cov_radii = self.rlimit * self.cov_radii_table(atoms)
        if (dm < cov_radii).any():
            return False

        return True
    
    
    def check_disconnections(self, atoms):
        """
        Check if one or more atoms are disconnected from all other atoms.
        Returns True if all atoms are connected
        """  
        atoms = atoms.copy()
        atoms.wrap()
        atoms = atoms.repeat([1 + int(c) for c in atoms.pbc])
        coord = atoms.positions

        # Atoms too close to each other:
        dm = distance_matrix(coord, coord) 
        
        cov_radii =  self.cov_radii_table(atoms)
        
        dm += (np.max(cov_radii) +1) * np.eye(len(dm))
        
        disconnected_atoms = np.all(dm > self.disconnect_limit * cov_radii, axis=0)

        any_disconnected_atoms = np.any(disconnected_atoms)
        if any_disconnected_atoms:
            return False
        
        return True
        
        
    def check_fingerprint_distances(self, distances):
        """
        Check that distances in fingerprint space is large enough.
        Return True if distances are ok
        """
        return np.min(distances) > self.dist_limit
    
    
    def check_cell_volume(self, atoms):
        """
        Check that cell volume is within the specified interval.
        Returns True if volume is within interval
        """
        cell_volume=atoms.get_volume() 
        
        cell_too_small = cell_volume<self.volume_limits[0]
        
        cell_too_large = cell_volume>self.volume_limits[1]
        
        return cell_too_small, cell_too_large
        
    
    def check_cell_angles(self, atoms):
        """
        Check that cell angles are large enough.
        Returns True if angle is large enough
        """
        angles = atoms.cell.angles()
        
        angles_too_small = np.any(angles < (90 - self.angle_limit) )
        
        angles_too_large = np.any(angles > (90 + self.angle_limit) )
        
        if angles_too_small or angles_too_large:
            return False
    
        return True
    

    def check(self, atoms, distances):
        """
        
        Parameters
        ----------
        atoms : ase.atoms
            Candidate atoms structure
        distances : numpy.array
            An array of all distances between the fingerprints of the
            candidate structure and all fingerprints in the database

        Returns
        -------
        bool
            True if all tests passed, False if any of the checks detected
            a faulty structure
        output_string : string
            A string describing what check returned False or 
            'structure accepted' if no checks detected a faulty structure
        """

        if self.dist_limit is not None:
            fp_distances_ok = self.check_fingerprint_distances(distances)
            if not fp_distances_ok:
                output_string='structure too close to existing structure'
                return False, output_string

        if self.rlimit is not None:
            atomic_distances_ok = self.check_atomic_distances(atoms)
            if not atomic_distances_ok:
                output_string='Atomic distances too short'
                return False, output_string

        if self.disconnect_limit is not None:
            all_connected = self.check_disconnections(atoms)
            if not all_connected:
                output_string='one or more disconnected atoms'
                return False, output_string

        if self.angle_limit is not None:
            cell_angles_ok = self.check_cell_angles(atoms)
            if not cell_angles_ok:
                output_string='one or more cell angles too small'
                return False, output_string

        if self.volume_limits is not None:
            cell_too_small, cell_too_large = self.check_cell_volume(atoms)
            if  cell_too_small:
                output_string='cell volume too small'
                return False, output_string
            elif cell_too_large:
                output_string='cell volume too large'
                return False, output_string


        output_string='structure accepted'
        return True, output_string

    def cov_radii_table(self, atoms):
        '''
        Return all-to-all table of the sums of covalent radii for
        atom pairs in 'atoms'.
        '''
        table = [[(covalent_radii[i] + covalent_radii[j])
                  for i in atoms.symbols.numbers]
                 for j in atoms.symbols.numbers]
        table = np.array(table)
        return table


class BEACONAtomsIO:
    """
    Handle write and read of Atoms objects within BEACON.
    
    Examples
    --------
    1.Instantiate class:
    >>> beaconio=BEACONAtomIO()
    2. Initialize output files:
    >>> beaconio.initialize_xyzfiles()
    3. Write to file identified by string strtype
    >>> beaconio.write_xyz(atoms, strtype)      
    
    strtype can be 
    'init',      init_structures.xyz
    'result',    structures_dft.xy
    'extra'      extras.xyz
    'surropt'    surropt.xyz
    """

    def __init__(self):

        # filenames for writing xyz
        self.initstrfile = 'init_structures.xyz'
        self.structurefile = 'structures_dft.xyz'
        self.extrafile = 'extras.xyz'
        self.surroptfile = 'surropt.xyz'

        self.names_by_type = {'init': self.initstrfile,
                              'result': self.structurefile,
                              'extra': self.extrafile,
                              'surropt': self.surroptfile}

        self.initialize_xyzfiles()

        return

    def initialize_xyzfiles(self):
        '''
        Create empty files.
        '''
        if world.rank == 0:
            for key in self.names_by_type:
                f = open(self.names_by_type[key], 'w')
                f.close()


    def write_xyz(self, atoms, strtype,
                  append=True, **kwargs):
        '''
        Write atoms to the file specified by strtype.
        '''

        filename = self.names_by_type.get(strtype)

        with warnings.catch_warnings():

            # with EMT, a warning is triggered while writing the
            # results in ase/io/extxyz.py. Lets filter that out:
            warnings.filterwarnings('ignore', category=UserWarning)

            write(filename, atoms, append=append, **kwargs)

class IterationResult:
    """
    Class to store, update, and distribute results from the
    surrogate relaxations.
    
    Examples
    --------
    1. Instantiate_class 
    >>> it_result=IterationResult(natoms=...)
    2. test if new acquisition value is smaller than current smallest value
    >>> is_better(value)
    3. Update the results for this rank
    >>> update(atoms)
    4. Share data between processors, and return the data for the
    structure that has the best acquisition function over all ranks.
    >>> distribute()
    """

    def __init__(self, natoms):
        '''
        Parameters
        ----------
        natoms: int
            an amount of atoms that is only used to read the
            size of the force array for initialization here.
        '''

        self.best_acq = np.inf
        self.my_best = dict(acq=np.inf,
                            energy=0.0,
                            forces=np.empty(natoms * 3),
                            unc=0.0,
                            subindex=0,
                            atoms=None)

    @property
    def my_best_acq(self):
        '''
        Best acquisition function at this rank.
        '''
        return self.my_best['acq']

    def update(self, dct):
        '''
        Update the results for this rank.
        '''
        self.my_best.update(dct)

    def is_better(self, value):
        '''
        Test if value is smaller than my_best_acq.
        '''
        if value < self.my_best_acq:
            return True

        return False

    def distribute(self):
        '''
        Share data between processors, and return the data for the
        structure that has the best acquisition function over all
        ranks.
        '''

        minrank = self.get_min_rank()

        # Share data among processors:
        best_e = np.atleast_1d(self.my_best['energy'])
        best_f = self.my_best['forces']


        best_u = np.atleast_1d(self.my_best['unc'])
        best_acq = np.atleast_1d(self.my_best['acq'])
        my_best_subindex = np.atleast_1d(self.my_best['subindex'])

        best_atoms = self.my_best['atoms']
        world.broadcast(best_e, minrank)
        world.broadcast(best_f, minrank)
        world.broadcast(best_u, minrank)
        world.broadcast(best_acq, minrank)
        world.broadcast(my_best_subindex, minrank)
        
       # broadcast atoms from rank with best structure to all procesors without calculator
        if best_atoms is not None:
            best_atoms.calc=None
        best_atoms=broadcast(best_atoms, minrank)


        # Set results to attributes:
        best_e = best_e[0]
        best_u = best_u[0]
        best_acq = best_acq[0]

        best_subindex = my_best_subindex[0]
        return (best_atoms, best_e, best_f,
                best_u, best_acq, best_subindex)

    def get_min_rank(self):
        '''
        Get rank with the minimal acquisition function.
        '''
        my_best_acq = np.atleast_1d(self.my_best_acq)

        # List all acquisition functions to an array with the
        # indices corresponding to rank indices:
        all_acqs = np.empty([world.size, 1])
        for rank in range(world.size):
            tmp = my_best_acq.copy()
            world.broadcast(tmp, rank)
            all_acqs[rank] = tmp.copy()

        # Get rank with the best acquisition:
        return np.argmin(all_acqs)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 23:18:30 2023

@author: casper
"""
import numpy as np
import copy
from scipy.spatial import distance_matrix

from hpfitter.optimizers.globaloptimizer import FactorizedOptimizer
from hpfitter.optimizers.linesearcher import GoldenSearch
from hpfitter.optimizers.linesearcher import FineGridSearch

from hpfitter.objectivefunctions.factorized_likelihood import FactorizedLogLikelihood 
from hpfitter.objectivefunctions.mle import MaximumLogLikelihood 
from hpfitter.objectivefunctions.likelihood import LogLikelihood 
from hpfitter.means.constant import Prior_constant

from hpfitter.optimizers.optimizer import FunctionEvaluation

from hpfitter.hpboundary.boundary import HPBoundaries

from copy import deepcopy
from hpfitter.hpfitter import HyperparameterFitter

class HyperparameterFitterGPAtom(HyperparameterFitter):
    def __init__(self,func,optimizer=None,bounds=None,use_update_pdis=False,get_prior_mean=False,use_stored_sols=False,**kwargs):
        """ 
        A wrapper for hyperparameter fitter object, so it can be used with ase-GPatom. 
        Hyperparameter fitter object with an optimizer for optimizing the hyperparameters on different given objective functions. 
        Parameters:
            func : ObjectiveFunction class
                A class with the objective function used to optimize the hyperparameters.
            optimizer : Optimizer class
                A class with the used optimization method.
            bounds : HPBoundaries class
                A class of the boundary conditions of the hyperparameters.
                Most of the global optimizers are using boundary conditions. 
                The bounds in this class will be used for the optimizer and func.
                The bounds have to be with the hyperparameter names used in the objective function.
            use_update_pdis : bool
                Whether to update the prior distributions of the hyperparameters with the given boundary conditions.
            get_prior_mean : bool
                Whether to get the parameters of the prior mean in the solution.
            use_stored_sols : bool
                Whether to store the solutions.
        """
        super().__init__(func, optimizer=optimizer,
                         bounds=bounds,
                         use_update_pdis=use_update_pdis,
                         get_prior_mean=get_prior_mean,
                         use_stored_sols=use_stored_sols,
                         **kwargs)
    
    def get_hyperparams(self,hp,model,**kwargs):
        " Get default hyperparameters if they are not given. "
        if hp is None:
            # Get the hyperparameters from the model
            hp=model.hp.copy()
        # Convert to hyperparameter used in the objective function
        hp=self.convert_hp_from_gpatom(hp)
        # Get the values and hyperparameter names
        theta,parameters=self.hp_to_theta(hp)
        return hp,theta,parameters
    
    def update_pdis(self,pdis,model,X,Y,parameters,**kwargs):
        " Update the prior distributions of the hyperparameters with the boundary conditions. "
        pdis=self.convert_dict_object_to_gpatom(pdis)
        return super().update_pdis(pdis,model,X,Y,parameters,**kwargs)
    
    def get_full_hp(self,sol,model,**kwargs):
        " Get the full hyperparameter dictionary with hyperparameters that are optimized and are not. "
        if 'hp' in sol.keys():
            sol['hp']=self.convert_hp_to_gpatom(sol['hp'],model)
        sol['full hp']=model.hp.copy()
        sol['full hp'].update(sol['hp'])
        if 'prefactor' in sol['full hp'].keys():
            sol['full hp'].pop('prefactor')
        sol['full hp']['noise']=sol['full hp']['weight']*sol['full hp']['ratio']
        return sol

    def copy_model(self,model,**kwargs):
        " Copy the model and check if the noisefactor is not used in the factorization method. "
        model=deepcopy(model)
        if 'noisefactor' in model.hp.keys():
            from hpfitter.objectivefunctions.factorized_likelihood import FactorizedLogLikelihood
            if isinstance(self.func,FactorizedLogLikelihood):
                if model.hp['noisefactor']!=1.0:
                    raise Exception('Noisefactor must be 1.0 for the Factorization method') 
        return model
    
    def convert_hp_from_gpatom(self,hp,**kwargs):
        " Convert the hyperparameters from GP-atom to the form here. "
        parameters=list(hp.keys())
        hp_new={}
        if 'scale' in parameters:
            hp_new['length']=np.array(np.log(hp['scale'])).reshape(-1)
        if 'weight' in parameters:
            hp_new['prefactor']=np.array(np.log(hp['weight'])).reshape(-1)
        if 'ratio' in parameters:
            hp_new['noise']=np.array(np.log(hp['ratio'])).reshape(-1)
        return hp_new
    
    def convert_hp_to_gpatom(self,hp,model,**kwargs):
        " Convert the hyperparameters from here to the form of GP-atom. "
        parameters=list(hp.keys())
        hp_new={}
        if 'length' in parameters:
            hp_new['scale']=np.array(np.exp(hp['length'])).reshape(-1)
        if 'prefactor' in parameters:
            hp_new['weight']=np.array(np.exp(hp['prefactor'])).reshape(-1)[0]
        if 'noise' in parameters:
            hp_new['ratio']=np.array(np.exp(hp['noise'])).reshape(-1)[0]
        return hp_new

    def convert_dict_object_to_gpatom(self,dict_obj,**kwargs):
        " Convert a dictionary with objects with GPatom hyperparameter names to the form here."
        if dict_obj is None:
            return dict_obj
        dict_obj_new={}
        for key,value in dict_obj.items():
            if key=='scale':
                dict_obj_new['length']=dict_obj['scale'].copy()
            if key=='weight':
                dict_obj_new['prefactor']=dict_obj['weight'].copy()
            if key=='ratio':
                dict_obj_new['noise']=dict_obj['ratio'].copy()
            else:
                dict_obj_new[key]=value.copy()
        return dict_obj_new




def prepare_variables(gp):
    """
    Make the gpatom Gaussian process object ready for hyperparameter fitting
    
    Parameters
    ----------
    gp : gpatom GaussianProcess object
        A trained version of the gpatom Gaussian process

    Returns
    -------
    features : list
        List of fingerprints
    targets : numpy.array
        All energy and force targets
    gp_copy : gpatom GaussianProcess
        a copy of the inputted Gaussian Process to prevent overwriting during
        hyperparameter fitting
    """
    features=gp.X
    targets=gp.Y.reshape(len(features),-1)
    gp_copy=copy.copy(gp)
    gp_copy.prior=Prior_constant(gp.prior.constant)
    return features, targets, gp_copy


def update_gp(gp, sol):
    """
    Method to update the Gaussian process

    Parameters
    ----------
    gp : gpatom GaussianProcess
        The original Gaussian process we want to uptae hyperparameters for
    sol : dictionary
        Dictionary including the new values for all hyperparameters
    """

    fullhp = sol['full hp']

    def asfloat(thing):
        # Guard aganist size-1 arrays.
        #
        # hpfitter.fit() returns a "sol" object which sometimes contains
        # length-1 array instead of a scalar.
        #
        # (It would be better if it didn't do so.)
        if np.isscalar(thing):
            return thing

        thing = thing[0]
        assert np.isscalar(thing)
        return float(thing)

    gp.set_hyperparams({'scale': asfloat(fullhp['scale']),
                        'weight': asfloat(fullhp['weight']),
                        'ratio': asfloat(fullhp['ratio'])})

    K = gp.kernel.kernel_matrix(gp.X)

    gp.update_noise(K)
    
    gp.prior.constant=float(sol['prior']['yp'])
        
    gp.train(gp.X, gp.Y)
    
    
def calculate_all_distances(fingerprints):
    """
    Get all distances and closest distances between all fingerprints stored
    in a list from the Gaussian process.
    """
    fp_dist=distance_matrix(fingerprints,fingerprints)
    fp_dist_unique=np.unique(fp_dist)
    fp_dist_unique=fp_dist_unique[fp_dist_unique > 0]
    fp_dist_big_diag=fp_dist+np.eye(len(fp_dist))*2*np.max(fp_dist)
    fp_dist_nn_unique=np.unique(np.min(fp_dist_big_diag,0))                        
    return fp_dist_unique, fp_dist_nn_unique

def scale_bounds_default(fingerprints):
    """ Get default search limits for optimization of the length scale. """
    fp_dist, fp_dist_nn = calculate_all_distances(fingerprints)
    return [np.median(fp_dist_nn), 10*max(fp_dist)]
    
def ratio_bounds_default(targets):
    """ Get default search limits for the noise ratio. """
    return [2.3e-16,  len(targets.flatten())]

def scale_prior_default(fingerprints):
    """ Get default parameters for the length scale prior function. """
    fp_dist, fp_dist_nn = calculate_all_distances(fingerprints)
    mean_dist=np.mean(fp_dist)
    max_dist=max(fp_dist)
    top_point=0.5*(mean_dist+max_dist)
    return [top_point, 2]

def ratio_prior_default():
    """ Get default parameters for the noise ratio prior function. """
    return [0.0001, 2]


def prior_default(energies, atoms):
    """ Get default prior mean function. i.e. the mean energy """
    return np.mean(energies)


class HpFitterVariableRatio:
    """
    Class to perform global optimization of hyperparameters for the gpatom
    Gausian process with optimization of prior mean, prefactor, lengths scale
    and noise ratio. 
    
    The method works by defining a grid over the length scale
    and noise ratio in two respective intervals.
    After the lowest point on the grid is found a local optimization is started
    from this point.
    This procedure is done on a single core.
    
    Examples
    --------
    >>>hp_optimizer=HpFitterVariableRatio(ngrid=80, maxiter=500)
    >>>hp_optimizer.fit(gp)
    """
    
    def __init__(self, ngrid=80, maxiter=500, tol=1e-5,  
                 scale_prior=None, ratio_prior=None,
                 fit_scale_and_ratio_interval=1, 
                 fit_prior_interval=1,
                 prior_method=prior_default, 
                 scale_bounds_method=scale_bounds_default,
                 ratio_bounds_method=ratio_bounds_default,
                 scale_prior_method=scale_prior_default,
                 ratio_prior_method=ratio_prior_default):
        """
        Parameters
        ----------
        ngrid : int, optional
            Number of grid points in hyperparameter optimization 
            The default is 80.
        maxiter : int, optional
            Max number of steps in the local search. 
            The default is 500.
        tol : int, optional
            Success criteria for the local search. 
            The default is 1e-5.
        scale_prior : Prior class, optional
            Prior clas for the length scale. If None, no length scale prior
            will be used.
            The default is None.
        ratio_prior : Prior class, optional
            Prior clas for the noise ratio. If None, no noise ratio prior
            will be used.
            The default is None.
        fit_scale_and_ratio_interval : int, optional
            How many training structures should be added to the Gaussian 
            process before length scale and noise ratio is updated. 
            If 1, they will be updated every time.
            The default is 1.
        fit_prior_interval : int, optional
            How many training structures should be added to the Gaussian 
            process before the prior mean is updated. 
            If 1, it will be updated every time.
            The default is 1.
        prior_method : method(energies, atoms), optional
            A custom method taking energies (numpy.array of target energies)
            and atoms (ase.Atoms) as an input and outputs a single scalar
            being the updated prior mean value. 
            The default is prior_default.
        scale_bounds_method : method(fingerprints), optional
            Custom method taking a list of all fingerprints as an input and
            outputs a list of two elements describing the upper and lower bound
            for the length scale global search. 
            The default is scale_bounds_default.
        ratio_bounds_method : method(targets), optional
            Custom method taking a list of all targets as an input and
            outputs a list of two elements describing the upper and lower bound
            for the noise ratio search. 
            The default is ratio_bounds_default.
        scale_prior_method : method(fingerprints), optional
            Custom method taking a list of all fingerprints as an input and
            outputs a list of two elements describing the top point and width
            of the length scale lognormal prior method. 
            The default is scale_prior_default.
        ratio_prior_method : method(), optional
            Custom method taking no inputs and outputs a list of two elements 
            describing the top point and width for the noise ratio 
            lognormal prior method. 
            The default is ratio_prior_default.
        """
        
        
        self.fit_scale_and_ratio_interval=fit_scale_and_ratio_interval
        
        self.fit_prior_interval=fit_prior_interval
        
        self.prior_method=prior_method
        
        self.scale_bounds_method=scale_bounds_method
    
        self.ratio_bounds_method=ratio_bounds_method
    
        self.scale_prior_method=scale_prior_method
    
        self.ratio_prior_method=ratio_prior_method
      
        self.pdis=self.setup_prior_distributions(scale_prior=scale_prior, 
                                                 ratio_prior=ratio_prior)

        line_optimizer=GoldenSearch(optimize=True,multiple_min=False,parallel=False, tol=tol)
        optimizer=FactorizedOptimizer(line_optimizer=line_optimizer,ngrid=ngrid,maxiter=maxiter)
        self.hpfitter_no_scale_ratio=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),
                                                                optimizer=FunctionEvaluation(jac=False),
                                                                get_prior_mean=True)
        self.hpfitter_scale_ratio=HyperparameterFitterGPAtom(func=FactorizedLogLikelihood(),optimizer=optimizer,get_prior_mean=True)

    def get_fit_boolians(self, gp):
        """ Decide what hyperparameters should be updated"""
        fit_scale_and_ratio=(len(gp.X) % self.fit_scale_and_ratio_interval == 0)
        fit_prior=(len(gp.X) % self.fit_prior_interval == 0)
        return fit_scale_and_ratio, fit_prior

    
    def fit(self, gp):  
        """
        Method to update hyperparameters

        Parameters
        ----------
        gp : gpatom GaussianProcess object
            A trained Gaussian process from gpatom

        Returns
        -------
        The Gaussian process wil get its new hyperparameters after this method
        and be retrained
        """
        
        features, targets, gp_copy = prepare_variables(gp)
        
        fit_scale_and_ratio, fit_prior = self.get_fit_boolians(gp)
        
        hp=dict()
        
        if fit_scale_and_ratio:
            hp['scale']=gp.hp['scale']
            hp['ratio']=gp.hp['ratio']
                    
        if fit_prior:
            energies=targets[:,0]
            atoms=[x.atoms.copy() for x in features]
            gp_copy.prior=Prior_constant(self.prior_method(energies, atoms))
        
        if 'scale' in hp:
            hpfitter=self.hpfitter_scale_ratio
        else:
            hpfitter=self.hpfitter_no_scale_ratio
            
        
        self.update_bounds(gp, hpfitter) 
        
            
        if self.pdis is not None:
            if 'scale' in self.pdis:
                self.update_scale_prior(gp)
            if 'ratio' in self.pdis:
                self.update_ratio_prior()
                
        sol=hpfitter.fit(features,  targets  , gp_copy, hp=hp, pdis=self.pdis)   

        update_gp(gp, sol)
        

    def setup_prior_distributions(self, scale_prior=None, ratio_prior=None):
        """
        Setup a list of all prior distributions used in updating the
        hyperparameters
        """
        pdis=None
        
        if (scale_prior is not None)  or (ratio_prior is not None): 
            pdis=dict()
        
            if scale_prior is not None:
                pdis['scale']=scale_prior

            if ratio_prior is not None:
                pdis['ratio']=ratio_prior

        return pdis
    
    def update_bounds(self, gp, hpfitter):
        """
        Update the length scale and noise ratio bounds for updating 
        the hyperparameters
        """
        fingerprints=[x.vector for x in gp.X]
        scale_bounds=self.scale_bounds_method(fingerprints)
        scale_bounds= [  [  np.log(scale_bounds[0]), np.log(scale_bounds[1])   ]  ]

        ratio_bounds=self.ratio_bounds_method(gp.Y)
        ratio_bounds= [ [np.log(ratio_bounds[0]), np.log(ratio_bounds[1])] ]
    
        bounds=HPBoundaries(bounds_dict=dict(length=scale_bounds, noise=ratio_bounds))
            
        hpfitter.update_arguments(bounds=bounds)
        

    def update_scale_prior(self, gp):
        """ Update the parameters of the scale prior method """
        fingerprints=[x.vector for x in gp.X]
        
        prior_params=self.scale_prior_method(fingerprints)
                       
        self.pdis['scale'].update_arguments(mu=np.log(prior_params[0]), std=np.log(prior_params[1]))


    def update_ratio_prior(self):
        """ Update the parameters of the scale prior method """
        prior_params=self.ratio_prior_method()
        
        self.pdis['ratio'].update_arguments(mu=np.log(prior_params[0]),  std=np.log(prior_params[1]))


    def get_function_value(self, gp):
        """ 
        Output the value of the log likelihood function. Used for testing.
        """
        self.hpfitter_val=HyperparameterFitterGPAtom(func=LogLikelihood(),
                                                     optimizer=FunctionEvaluation(jac=False), get_prior_mean=True)
        
        X, Y, gp_copy = prepare_variables(gp)

        sol=self.hpfitter_val.fit(X,  Y  , gp_copy, hp=None, pdis=self.pdis)
        
        value=sol['fun']
        
        update_gp(gp, sol)
        
        return value
    
        

class HpFitterConstantRatio(HpFitterVariableRatio):
    """
    Class to perform global optimization of hyperparameters for the gpatom
    Gausian process with optimization of prior mean, prefactor 
    and lengths scale with the noise ratio kept fixed 
    
    The method works by defining a grid over the length scale in an interval.
    After the lowest point on the grid is found a local optimization is started
    from this point.
    This procedure is done on a single core.
    
    Examples
    --------
    >>> hp_optimizer=HpFitterConstantRatio(ngrid=80, maxiter=500)
    >>> hp_optimizer.fit(gp)
    """
    def __init__(self, ngrid=80, maxiter=500, tol=1e-5,
                 scale_prior=None, 
                 fit_scale_interval=1,
                 fit_weight_interval=1,
                 fit_prior_interval=1,
                 prior_method=prior_default, 
                 scale_bounds_method=scale_bounds_default,
                 scale_prior_method=scale_prior_default):
        """
        Parameters
        ----------
        ngrid : int, optional
            Number of grid points in hyperparameter optimization 
            The default is 80.
        maxiter : int, optional
            Max number of steps in the local search. 
            The default is 500.
        tol : int, optional
            Success criteria for the local search. 
            The default is 1e-5.
        scale_prior : Prior class, optional
            Prior clas for the length scale. If None, no length scale prior
            will be used.
            The default is None.
        fit_scale_interval : int, optional
            How many training structures should be added to the Gaussian 
            process before length scale is updated. 
            If 1, it will be updated every time.
            The default is 1.
        fit_weight_interval : int, optional
            How many training structures should be added to the Gaussian 
            process before prefactor is updated. 
            If 1, it will be updated every time.
            The default is 1.
        fit_prior_interval : int, optional
            How many training structures should be added to the Gaussian 
            process before the prior mean is updated. 
            If 1, it will be updated every time.
            The default is 1.
        prior_method : method(energies, atoms), optional
            A custom method taking energies (numpy.array of target energies)
            and atoms (ase.Atoms) as an input and outputs a single scalar
            being the updated prior mean value. 
            The default is prior_default.
        scale_bounds_method : method(fingerprints), optional
            Custom method taking a list of all fingerprints as an input and
            outputs a list of two elements describing the upper and lower bound
            for the length scale global search. 
            The default is scale_bounds_default.
        scale_prior_method : method(fingerprints), optional
            Custom method taking a list of all fingerprints as an input and
            outputs a list of two elements describing the top point and width
            of the length scale lognormal prior method. 
            The default is scale_prior_default.
        """
        
        self.fit_scale_interval=fit_scale_interval
        self.fit_weight_interval=fit_weight_interval
        self.fit_prior_interval=fit_prior_interval
        
        self.prior_method=prior_method
        
        self.scale_bounds_method=scale_bounds_method   

        self.scale_prior_method=scale_prior_method            
           
        
        self.pdis=self.setup_prior_distributions(scale_prior=scale_prior)

        line_optimizer=GoldenSearch(optimize=True,multiple_min=False,parallel=False, tol=tol)
        optimizer=FactorizedOptimizer(line_optimizer=line_optimizer,ngrid=ngrid,maxiter=maxiter)
        self.hpfitter_no_scale=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),optimizer=FunctionEvaluation(jac=False),get_prior_mean=True)
        self.hpfitter_scale=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),optimizer=optimizer,get_prior_mean=True)
        
    def get_fit_boolians(self, gp):
        """ Decide what hyperparameters should be updated """
        fit_scale=(len(gp.X) % self.fit_scale_interval == 0)
        fit_weight=(len(gp.X) % self.fit_weight_interval == 0)
        fit_prior=(len(gp.X) % self.fit_prior_interval == 0)
        return fit_scale, fit_weight, fit_prior
        
    
    def update_bounds(self, gp, hpfitter):
        """ Update the bounds for length scale optimization """
        fingerprints=[x.vector for x in gp.X]
        
        scale_bounds=self.scale_bounds_method(fingerprints)
        
        scale_bounds= [  [  np.log(scale_bounds[0]), np.log(scale_bounds[1])   ]  ]

        scale_bounds=HPBoundaries(bounds_dict=dict(length=scale_bounds))
            
        hpfitter.update_arguments(bounds=scale_bounds)
        
    
    def fit(self, gp):
        """
        Method to update hyperparameters

        Parameters
        ----------
        gp : gpatom GaussianProcess object
            A trained Gaussian process from gpatom

        Returns
        -------
        The Gaussian process wil get its new hyperparameters after this method
        and be retrained
        """        
    
        features, targets, gp_copy = prepare_variables(gp)
        
        fit_scale, fit_weight, fit_prior = self.get_fit_boolians(gp)        
        
        hp=dict()
        
        if fit_scale:
            hp['scale']=gp.hp['scale']
            
        if fit_weight:
            hp['weight']=gp.hp['weight']
        
        if fit_prior: 
             energies=targets[:,0]
             atoms=[x.atoms.copy() for x in features]
             gp_copy.prior=Prior_constant(self.prior_method(energies, atoms))

        if 'scale' in hp:
            hpfitter=self.hpfitter_scale  
        else:
            hpfitter=self.hpfitter_no_scale


        self.update_bounds(gp, hpfitter)             
        if self.pdis is not None:
            self.update_scale_prior(gp)  
            
        sol=hpfitter.fit(features, targets, gp_copy, hp=hp, pdis=self.pdis)   
        
        update_gp(gp, sol)
                
        
    def setup_prior_distributions(self, scale_prior=None,):
        """Setup prior distribution used in updating the length scale"""
        pdis=None
        
        if scale_prior is not None:
            pdis=dict(scale=scale_prior)

        return pdis    
    
            
class HpFitterVariableRatioParallel(HpFitterVariableRatio):
    """
    Class to perform MPI parallelized global optimization of hyperparameters 
    for the gpatom Gausian process with optimization of prior mean, prefactor, 
    lengths scale and noise ratio.
    
    Examples
    --------
    >>> hp_optimizer=HpFitterVariableRatioParallel(ngrid=80, maxiter=500)
    >>> hp_optimizer.fit(gp)
    """
    
    def __init__(self, ngrid=80,  maxiter=500, loops=5, tol=1e-5,  
                 scale_prior=None, ratio_prior=None,
                 fit_scale_and_ratio_interval=1, 
                 fit_prior_interval=1,
                 prior_method=prior_default, 
                 scale_bounds_method=scale_bounds_default,
                 ratio_bounds_method=ratio_bounds_default,
                 scale_prior_method=scale_prior_default,
                 ratio_prior_method=ratio_prior_default):
        """
        Parameters
        ----------
        ngrid : int, optional
            Number of grid points in hyperparameter optimization 
            The default is 80.
        maxiter : int, optional
            Max number of steps in the local search. 
            The default is 500.
        loops : int
            The number of loops where the grid points are made.
            The default is 3
        tol : int, optional
            Success criteria for the local search. 
            The default is 1e-5.

        
        for other parameters see HpFitterVariableRatioParallel
        """
        
        self.fit_scale_and_ratio_interval=fit_scale_and_ratio_interval
        
        self.fit_prior_interval=fit_prior_interval
        
        self.prior_method=prior_method
        
        self.scale_bounds_method=scale_bounds_method
    
        self.ratio_bounds_method=ratio_bounds_method
    
        self.scale_prior_method=scale_prior_method
    
        self.ratio_prior_method=ratio_prior_method
      
        self.pdis=self.setup_prior_distributions(scale_prior=scale_prior, 
                                                 ratio_prior=ratio_prior)       
        
        line_optimizer=FineGridSearch(optimize=True,multiple_min=False,loops=loops,ngrid=ngrid,parallel=True, tol=tol)
        optimizer=FactorizedOptimizer(line_optimizer=line_optimizer,ngrid=ngrid,maxiter=maxiter,parallel=True)
        self.hpfitter_no_scale_ratio=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),
                                                                optimizer=FunctionEvaluation(jac=False),
                                                                get_prior_mean=True)
        self.hpfitter_scale_ratio=HyperparameterFitterGPAtom(func=FactorizedLogLikelihood(),optimizer=optimizer,get_prior_mean=True)
        
        
class HpFitterConstantRatioParallel(HpFitterConstantRatio):
    """
    Class to perform MPI parallelized global optimization of hyperparameters 
    for the gpatom Gausian process with optimization of prior mean, prefactor 
    and lengths scale with the noise ratio kept fixed.
    
    Examples
    --------
    >>> hp_optimizer=HpFitterConstantRatioParallel(ngrid=80, maxiter=500)
    >>> hp_optimizer.fit(gp)
    """
    def __init__(self, ngrid=80, maxiter=500, loops=5,  tol=1e-5,
                 scale_prior=None, 
                 fit_scale_interval=1,
                 fit_weight_interval=1,
                 fit_prior_interval=1,
                 prior_method=prior_default, 
                 scale_bounds_method=scale_bounds_default,
                 scale_prior_method=scale_prior_default):
        """
        Parameters
        ----------
        ngrid : int, optional
            Number of grid points in hyperparameter optimization 
            The default is 80.
        maxiter : int, optional
            Max number of steps in the local search. 
            The default is 500.
        loops : int
            The number of loops where the grid points are made.
            The default is 3
        tol : int, optional
            Success criteria for the local search. 
            The default is 1e-5.

        For other parameters see HpFitterConstantRatio
        """ 
        self.fit_scale_interval=fit_scale_interval
        self.fit_weight_interval=fit_weight_interval
        self.fit_prior_interval=fit_prior_interval
        
        self.prior_method=prior_method
        
        self.scale_bounds_method=scale_bounds_method   

        self.scale_prior_method=scale_prior_method            
        
        self.pdis=self.setup_prior_distributions(scale_prior=scale_prior)
     
        line_optimizer=FineGridSearch(optimize=True,multiple_min=False,loops=loops,ngrid=ngrid,parallel=True, tol=tol)
        optimizer=FactorizedOptimizer(line_optimizer=line_optimizer,ngrid=ngrid,maxiter=maxiter,parallel=True)
        self.hpfitter_no_scale=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),optimizer=FunctionEvaluation(jac=False),get_prior_mean=True)
        self.hpfitter_scale=HyperparameterFitterGPAtom(func=MaximumLogLikelihood(),optimizer=optimizer,get_prior_mean=True)
        

import time
import warnings
from scipy.optimize import minimize, OptimizeResult
import numpy as np
from ase.parallel import paropen
from scipy.special import expit
import copy
from scipy.linalg import eigh
from scipy.linalg import solve_triangular, cho_factor, cho_solve
from scipy.spatial import distance_matrix

class HyperparameterFitter:       
    """
    Class for local hyperparameter fitting using the Nelder Mead method. 
    Fits hyperparameters that are allowed to fit based on maximum log 
    likelihood of the data in Gaussian Process. 
    
    This method allways operates on a single core. This class is used in 
    HpFitInterface to be integrated properly with BEACON
    """
    @classmethod
    def fit(cls, gp, params_to_fit, fit_weight=True, fit_prior=True, pd=None,
            bounds=None, tol=1e-2, txt='mll.txt'):
        """
        Parameters
        ----------
        gp : gpatom Gaussian Process
            Trained Gaussian process 
        params_to_fit : list of strings
            strings names for hyperparameters one wants to fit
        fit_weight : bool, optional
            If prefactor should be fitted 
            The default is True.
        fit_prior : bool, optional
            If the prior mean should be fitted. 
            The default is True.
        pd : Prior class, optional
            A prior for the length scale, if None, no prior is used. 
            The default is None.
        tol : float, optional
            convergence criteria for scipy Nelder Mead 
            The default is 1e-2.
        txt : string, optional
            Output file for writing of optimizer progress.
            The default is 'mll.txt'.

        Returns
        -------
        gp : gpatom GaussianProcess
            A Gaussian process with updated parameters
        sol : float
            The updated maximum log likelihood value.
        """


        txt = paropen(txt, 'a')
        txt.write('\n{:s}\n'.format(20 * '-'))
        txt.write('{}\n'.format(time.asctime()))
        txt.write('Number of training points: {}\n'.format(len(gp.X)))
                                                                               
        arguments = (gp, params_to_fit, fit_weight, fit_prior, pd, txt)

        params = []

        # In practice, we optimize the logarithms of the parameters:
        for string in params_to_fit:
            params.append(np.log10(gp.hp[string]))

        t0 = time.time()

        result = minimize(cls.neg_log_likelihood,
                          params,
                          args=arguments,
                          method='Nelder-Mead',
                          options={'fatol': tol})
        


        txt.write("Time spent minimizing neg log likelihood: "
                  "{:.02f} sec\n".format(time.time() - t0))

        converged = result.success

        # collect results:
        optimalparams = {}
        powered_results = np.power(10, result.x)
        
        
        
        for p, pstring in zip(powered_results, params_to_fit):
            optimalparams[pstring] = p

        gp.set_hyperparams(optimalparams)
        gp.train(gp.X, gp.Y)

        txt.write('{} success: {}\n'.format(str(gp.hp), converged))
        txt.close()

        return gp, result.fun



    @staticmethod
    def logP(gp):
        """ log likelihood method """
        y = gp.Y.flatten()
               
        logP = (- 0.5 * np.dot(y - gp.prior_array, gp.model_vector)
                - np.sum(np.log(np.diag(gp.L)))
                - len(y) / 2 * np.log(2 * np.pi))
             
        return logP


    @staticmethod
    def neg_log_likelihood(params, *args, fit_weight=True, fit_prior=True):
        """ negative log likelihood method """
        gp, params_to_fit, fit_weight, fit_prior, prior_distr, txt = args

        params_here = np.power(10, params)


        txt1 = ""
        paramdict = {}
        for p, pstring in zip(params_here, params_to_fit):
            paramdict[pstring] = p
            txt1 += "{:18.06f}".format(p)

        gp.set_hyperparams(paramdict)
        gp.train(gp.X, gp.Y)
        
        
        if fit_prior:                                       
            PriorFitter.fit(gp)
            
            
        if fit_weight:
            GPPrefactorFitter.fit(gp)


        # Compute log likelihood
        logP = HyperparameterFitter.logP(gp)
        
        # Prior distribution:
        if prior_distr is not None:
            logP += prior_distr.get(gp.hp['scale'])


        # Don't let ratio fall too small, resulting in numerical
        # difficulties:
        if 'ratio' in params_to_fit:
            ratio = params_here[params_to_fit.index('ratio')]
            if ratio < 1e-6:
                logP -= (1e-6 - ratio) * 1e6

        txt.write('Parameters: {:s}       -logP: {:12.02f}\n'
                  .format(txt1, -logP))
        txt.flush()
              
        return -logP



class PriorFitter:
    """ 
    Static class to update the pror mean based on the analytical update 
    method in the gpatom Prior classes
    """
    @staticmethod
    def fit(gp):
        """
        Parameters
        ----------
        gp : gpatom GaussianProcess
            Gaussian process with old prior mean
        Returns
        -------
        gp : gpatom GaussianProcess
            Gaussian process with new prior mean
        """
        gp.prior.update(gp.X, gp.Y, gp.L, gp.use_forces)
      
        gp.train(gp.X,gp.Y)  
        
        return gp


class GPPrefactorFitter:
    """ Static class to update the prefactor based on analytical method """
    @staticmethod
    def fit(gp):
        """
        Parameters
        ----------
        gp : gpatom GaussianProcess
            Gaussian process with old prefactor
        Returns
        -------
        gp : gpatom GaussianProcess
            Gaussian process with new prefactor
        """
        oldvalue = gp.hp['weight']
        
        y = np.array(gp.Y).flatten()
              
        factor = np.sqrt(np.dot(y - gp.prior_array, gp.model_vector) / len(y))
        
        newvalue = factor * oldvalue

        gp.set_hyperparams({'weight': newvalue})
        # Rescale accordingly ("re-train"):
        gp.model_vector /= factor**2            
        gp.L *= factor  # lower triangle of Cholesky factor matrix
        gp.K_reg *= factor**2

        return gp



class HpFitInterface:
    """
    Class to use the above classes to fit the hyperparameters
    
    Examples
    --------
    >>> hp_optimizer=HpFitInterface(scale_prior=PriorDistributionLogNormal())
    >>> hp_optimizer.fit(gp)
    """
    
    def __init__(self, scale_prior=None, fit_scale_interval=1, fit_weight_interval=1, fit_prior_interval=1):
        """
        Parameters
        ----------
        scale_prior : length scale prior class, optional
            A prior method for the length scale method. 
            See PriorDistributionLogNormal as an example on how to make and 
            use it. If None, no prior will be used.
            The default is None.
        fit_scale_interval : int, optional
            Interval of how many new structures should be added to Gaussian
            process before the length scale is optimized. 
            If 1, it will be updated every time.
            The default is 1.
        fit_weight_interval : int, optional
            Interval of how many new structures should be added to Gaussian
            process before the prefactor is optimized. 
            If 1, it will be updated every time.
            The default is 1.
        fit_prior_interval : int, optional
            Interval of how many new structures should be added to Gaussian
            process before the prior mean is optimized. 
            If 1, it will be updated every time.
            The default is 1.
        """
        self.scale_prior=scale_prior        

        self.fit_scale_interval=fit_scale_interval
        self.fit_weight_interval=fit_weight_interval
        self.fit_prior_interval=fit_prior_interval
        
        
    def get_fit_boolians(self, gp):
        """ Decide what hyperparameters should be updated """
        fit_scale=(len(gp.X) % self.fit_scale_interval == 0)
        fit_weight=(len(gp.X) % self.fit_weight_interval == 0)
        fit_prior=(len(gp.X) % self.fit_prior_interval == 0)
        return fit_scale, fit_weight, fit_prior
            
    
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
        fit_scale, fit_weight, fit_prior = self.get_fit_boolians(gp)
            
        
        if fit_scale:
            distances, dist_nn_avg = ScaleSetter.calculate_all_distances(gp)     
            ScaleSetter.update_scale_prior_distribution(self.scale_prior, distances)
            ScaleSetter.fix_scale(gp,distances)  
            
            gp , ll = HyperparameterFitter.fit(gp, ['scale'],
                                               fit_weight=fit_weight, 
                                               fit_prior=fit_prior, 
                                               pd=self.scale_prior) 
               
        else: 
                
            if fit_prior:
                gp=PriorFitter.fit(gp)
    
            if fit_weight: 
                gp = GPPrefactorFitter.fit(gp)
                
            ll=HyperparameterFitter.logP(gp)
    
    
        gp.train(gp.X, gp.Y)
        return gp, ll
    
    
    
    
class ScaleSetter():
    """ 
    Static class to update length scale prior and set initial length scale
    before starting local relaxation
    """
    
    @staticmethod
    def calculate_all_distances(gp):
        """
        Get all distances and closest distances between all fingerprints stored
        in a list from the Gaussian process.
        """
        fp_list=[x.vector for x in gp.X]
        
        fp_dist=distance_matrix(fp_list,fp_list)
        
        fp_dist_unique=np.unique(fp_dist)
        
        fp_dist_unique=fp_dist_unique[fp_dist_unique > 0]

        fp_dist_big_diag=fp_dist+np.eye(len(fp_dist))*2*np.max(fp_dist)
        fp_dist_nn_unique=np.unique(np.min(fp_dist_big_diag,0))
        fp_dist_nn_avg=np.mean(fp_dist_nn_unique)
                        
        return fp_dist_unique, fp_dist_nn_avg
    
            
    @staticmethod
    def fix_scale(gp, distances):
        """
        Set the initial length scale to be the maximum of the
        mean distance in fingerprint space and the current length scale
        value. This is to make sure the optimizer don't find a low length scale
        as the optimum, as this often leads to poor performance, especially
        when the amount of data is small. 
        """

        scale = max(gp.hp['scale'], np.mean(distances))
        gp.set_hyperparams({'scale': scale})
    
    
    @staticmethod
    def update_scale_prior_distribution(scale_prior, distances):
        """
        Update the toppoint 'loc' parameter of the length scale 
        prior distribution
        """
        
        if scale_prior is None:
            return
        
        scale_prior.update(distances)
        

class PriorDistributionLogNormal():
    """    
    LogNormal distribution for the length scale 'scale' hyperparameter.
    Parameters correspond to mean (location of peak) and standard deviation
    of the LogNmormal in logaritmic space. 
    In non-logaritmic space the distribution mode is located at exp(loc-width**2).
    The prior is updated such that the mode is always located at the mean 
    value of the fingerprint space distances in non-logaritmic space. 
    
    The prior is usefull for avoiding very small length scales when the
    Gaussian process has a low amount of data. 
    """
    
    def __init__(self, loc=6, width=1, log=True, update_width=True):
        """
        Parameters
        ----------
        loc : float, optional
            Top point parameter of prior distribution in logarithmic space.
            The default is 6.
        width : float, optional
            Width parameter of the distribution in logarithmic space.
            The default is 1.
        log : bool, optional
            If the width parameter should be updated in logarithmic space 
            (True) or normal space (False)
            The default is True.
        update_width : bool, optional
            If The width should be updated. 
            The default is True.
        """
        self.name='LogNormal'
        self.loc=loc
        self.width=width
        self.log=log
        self.update_width=update_width
                
    def get(self,x):
        """
        Method to evaluate the prior at a given length scale value
        
        Parameters
        ----------
        x : float
            Length scale value
            
        Returns
        -------
        log_scale_prior : float
            Value of length scale prior at the given length scale.
        """
        
        log_fp_dist_std=self.width
        
        mode=self.loc

        log_fp_dist_mean=mode+log_fp_dist_std**2
        
        A=-0.5*( (np.log(x) - (log_fp_dist_mean-log_fp_dist_std**2) ) /log_fp_dist_std)**2
        
        B=- log_fp_dist_mean + 0.5*log_fp_dist_std**2 - np.log(log_fp_dist_std*np.sqrt( 2*np.pi ))
        
        log_scale_prior= A+B
        
        return log_scale_prior
    
    def update(self, fingerprint_distances):  
        """
        Method to update the top point parameter and width of the 
        length scale prior.
    
        Parameters
        ----------
        fingerprint_distances : numpy.array
            Array of all distances in fingerprint space

        Returns
        -------
        None.

        """
       
        mean_dist=np.mean(fingerprint_distances)
       
        maxpoint=max(fingerprint_distances)
        
        self.loc=  np.log( 0.5* (mean_dist+maxpoint))   
    
        
        if self.update_width and len(fingerprint_distances)>1:
            if self.log:
                self.width=0.5*(np.log(maxpoint)-np.log(mean_dist))        
            else:
                self.width=np.log(0.5*(maxpoint-mean_dist))
        
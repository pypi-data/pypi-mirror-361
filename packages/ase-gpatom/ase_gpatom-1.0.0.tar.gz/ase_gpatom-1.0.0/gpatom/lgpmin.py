import numpy as np

from gpatom.gpmin import GPMin
from gpatom.gpfp.kernel import CCKernel


class LGPMin(GPMin):
    """ Right now it only works if we do not update """
    def __init__(self, atoms, memory=None, **kwargs):

         GPMin.__init__(self, atoms=atoms, **kwargs)

         if memory is None:
             self.memory = len(self.atoms) // 10
         else:
             self.memory = memory

         self.K = None
         self.generation = np.around(np.sqrt(self.memory)).astype(int)
         self.rng = np.random.RandomState(42)  # Should this be an input?

    def replace(self, fp, y, threshold=None):
        '''
        XXX Not working.
        '''
        X = np.array(self.x_list)
        A = self.K.K(X, X)

        k = np.array([self.K.kernel(fp, x2) for x2 in self.x_list])
        k = self.K.kernel_vector(fp, X).T

        noise = self.gp.hp['noise']
        scale = self.gp.hp['scale']
        c = np.linalg.solve(A + noise * scale**2, k)

        i = np.argmax(c) #This is the index we use to replace

        if threshold is None or c.flatten()[i] > threshold:

            self.x_list[i] = fp
            self.y_list[i] = y

    def update_training_set(self, r, e, f):

        fp = self.coords2fingerprint(r)
        y = np.append(np.array(e).reshape(-1), -f.reshape(-1))

        if len(self.x_list) < self.memory:

            self.x_list.append(fp)
            self.y_list.append(y)

        else:

           if self.K is None:

               self.K = CCKernel()
               self.K.set_params(self.gp.hp)
               self.x_population = self.x_list.copy()
               self.y_population = self.y_list.copy()

           for j in range(self.generation):
               i = self.rng.randint(len(self.x_population))
               self.replace(self.x_population[i], self.y_population[i], 1.1)

           self.replace(fp, y)
           self.x_population.append(fp)
           self.y_population.append(y)

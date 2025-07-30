'''
Package: PModels
----------------
* Collection of models to predict properties of polymer systems.
* The polymer systems = polymer blends and polymer composites.
* The final system properties
  are estimated from the properties of individual components. 

Ultra-brief example

>>> # Standard import of PModels package
>>> import pmodels as pm
>>> # Predict elastic modulus (E)
>>> # of a binary isotropic blend with composition 50/50
>>> # and moduli of the individual components E1 = 1 GPa and E2 = 3 GPa
>>> E_lin = pm.lin.P(1, 3, 0.5)  # linear model prediction   => E_lin = 2.00
>>> E_ebm = pm.ebm.E(1, 3, 0.5)  # EBM model, default params => E_ebm = 1.70

List of modules = predictive models

* pmodels.lin = LINear model
    - arbitrary systems, arbitrary property (P), linear prediction
* pmodels.ebm = Equivalent Box Model
    - isotropic polymer blends, modulus (E) or yield stress (Y), non-linear
* pmodels.ht = Halpin-Tsai equations
    - polymer composites with 0D/1D/2D fillers, modulus (E) 
* pmodels.comp = equations for polymer composites
    - polymer composites with fillers with/without interfacial adhesion
'''

__version__ = '0.4'

# The following command enables to use all submodules as follows:
# >>> from pmodels import *
# >>> E_lin = lin.P(1,3,0.5)
# >>> E_ebm = ebm.E(1,3,0.5)
__all__ = ['lin', 'ht', 'ebm', 'comp']

# The following block of commands enables to use all submodules as follows:
# >>> import pmodels as pm
# >>> E_lin = pm.lin.P(1,3,0.5)
# >>> E_ebm = pm.ebm.E(1,3,0.5)
import pmodels.lin
import pmodels.ht
import pmodels.ebm
import pmodels.comp

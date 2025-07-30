'''
Module: pmodels.lin
-------------------

* Model: LIN -> system property = linear combination of component properties.
* Systems: an arbitrary binary polymer systems (or any binary system).
* Predictions: an arbitrary property, but just the first approximation.

Simple usage

>>> # Standard import of pmodels package
>>> import pmodels as pm
>>>
>>> # (1) Estimate elastic modulus (E) of an isotropic binary polymer blend,
>>> # where moduli of the components are E1 = 1 GPa and E2 = 3 GPa,
>>> # and volume fraction of the second component is 0.5.
>>> E_lin = pm.lin.P(P1=1, P2=3, v2=0.5)
>>>
>>> # (2) Print the result
>>> print(f'Modulus of the blend: {E_lin:.2f}')
Modulus of the blend: 2.00

Notes

* LIN is a very simple model ~ rule of mixtures.
* It is equivalent to Voigt rule (pmodels.comp.VoigtRule.P).
* Both LIN model and Voigt rule are based on iso-strain assumption.
    - they are used mostly for predicting elastic modulus
    - but other properties (mech.props, conductivity) can be estimated as well
* In the field of polymers, LIN model works well for:
    - E of polymer composites with (infinitely) long oriented fibers
    - H of semicryscalline polymers (amorph. and cryst. phases interconnected)
    - and analogous systems, where iso-strain assumption holds
'''

def P(P1,P2,v2):
    '''
    Calculate (arbitrary) property P using linear model.
    
    Parameters
    ----------
    P1 : float
        Property of the 1st component.
    P2 : float
        Property of the 2nd component.
    v2 : float
        Volume fraction of the 2nd component.
            
    Returns
    -------
    P : float
        P = final property of the system according to linear model.
        
    Test
    ----
    >>> P(100,200,v2=0.5)
    150.0
    '''
    P = P1*(1-v2) + P2*v2
    return(P)

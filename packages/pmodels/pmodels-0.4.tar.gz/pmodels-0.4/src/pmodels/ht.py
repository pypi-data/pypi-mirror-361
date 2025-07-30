'''
Module: pmodels.ht
-------------------

* This module defines Halpin-Tsai equations.
* Halpin-Tsai equations predict elastic modulus of polymer composites.
* The polymer composite consists of a polymer matrix
  and stiff fibers or plates that are can be oriented or non-oriented.

Simple usage

>>> # Standard import of pmodels package
>>> import pmodels as pm
>>>
>>> # (1) Estimate elastic modulus (E) of a polymer composite,
>>> # with PA6 matrix (Em = 1 GPa) and 10% of oriented fibers (Ef = 10 GPa)
>>> # with three different aspect ratios (AR = 100, 10, and 1).
>>>
>>> Ec_001 = pm.ht.E(Em=1, Ef=10, vf=0.1, ftype=1, orient=1, AR=1)
>>> Ec_010 = pm.ht.E(Em=1, Ef=10, vf=0.1, ftype=1, orient=1, AR=10)
>>> Ec_100 = pm.ht.E(Em=1, Ef=10, vf=0.1, ftype=1, orient=1, AR=100)
>>>
>>> # (2) Print the result
>>> print(f'Elastic moduli: {Ec_001:.2f} {Ec_010:.2f} {Ec_100:.2f}')
Elastic moduli: 1.24 1.65 1.87
'''

#------------------------------------------------------------------------------

# Custom exceptions
class _UnknownFillerTypeException(Exception): pass
class _UnknownOrientationException(Exception): pass

# Main function: general calculation of elastic modulus according to HT theory
def E(Em,Ef,vf, ftype = 1, orient = 1, AR = 1):
    '''
    Predict elastic modulus, E, using Halpin-Tsai equations.
    
    Parameters
    ----------
    Em : float
        Elastic modulus of the matrix.
    Ef : float
        Elastic modulus of the filler.
    vf : float
        Volume fraction of the filler.
    ftype  : 1 or 2, optional, default is 1
        If ftype = 1 => the filler = fibers.
        If ftype = 2 => the filler = plates.
    orient : 1 or 2 or 3, optional, default is 1
        If orient = 1 => fibers/plates are parallel to deformation.
        If orient = 2 => fibers/plates are perpendicular to deformation.
        If orient = 3 => fibers/plates are oriented randomly.
    AR : float, optional, default is 1
        Aspect ratio = l/d for fibers, d/t for platelets
        (l = length, d = diameter, t = thickness).        
    
    Returns
    -------
    E : float
        The final modulus of the system according to HT model.
        
    Test
    ----
    >>> round(E(100,200,0.5,AR=1),3)
    142.857
    >>> round(E(100,200,0.5,AR=100),3)
    149.876
    '''
    
    # Local/internal functions
    def E_general_formula(ksi):
        eta = (Ef/Em - 1) / (Ef/Em + ksi)
        E = (1 + ksi*eta*vf) / (1 - eta*vf)
        return(E)
    def E_unoriented_fibers(): return(0.184*E_parallel + 0.816*E_perpendicular)
    def E_unoriented_plates(): return(0.490*E_parallel + 0.510*E_perpendicular)
    
    # Main function definition
    try:
        if ftype == 1:
            E_parallel      = Em * E_general_formula(ksi=2*AR)
            E_perpendicular = Em * E_general_formula(ksi=2)
        elif ftype == 2:
            E_parallel      = Em * E_general_formula(ksi=2*AR)
            E_perpendicular = Em * E_general_formula(ksi=2)
        else:
            raise _UnknownFillerTypeException()
        if   orient == 1: return(E_parallel)
        elif orient == 2: return(E_perpendicular)
        elif orient == 3:
            if   ftype == 1: return(E_unoriented_fibers())
            elif ftype == 2: return(E_unoriented_plates())
        else:
            raise _UnknownOrientationException()
    except _UnknownFillerTypeException:
        print('Unknown filler type!')
        print('Allowed: 1 = fibers, 2 = plates')
    except _UnknownOrientationException:
        print('Unknown orientation.')
        print('Allowed: 1 = parallel, 2 = perpendicular, 3 = random')
    
    # End of main function, return final value
    return(E)

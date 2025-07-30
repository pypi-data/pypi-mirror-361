'''
Module: pmodels.ebm
-------------------

* Model: EBM -> system property = non-linear combination of component props.
* System: two-component polymer blend (isometric/non-oriented components).
* Predicted properties: elastic modulus (E) and yield strength (Y).

Simple usage

>>> # Standard import of pmodels package
>>> import pmodels as pm
>>>
>>> # (1) Estimate elastic modulus (E) of an isotropic binary polymer blend,
>>> # where moduli of the components are E1 = 1 GPa and E2 = 3 GPa,
>>> # and volume fraction of the second component is 0.5.
>>> E_ebm = pm.ebm.E(E1=1, E2=3, v2=0.5)
>>>
>>> # (2) Print the result
>>> print(f'Modulus of the blend: {E_ebm:.2f}')
Modulus of the blend: 1.70
'''

import numpy as np

# This module is used to suppress some specific numpy warnings
# which uselessly warn against situation that are excluded due to np.where
import warnings

#------------------------------------------------------------------------------

def vfractions(v2, v1cr = 0.156, v2cr = 0.156, q1 = 1.8, q2 = 1.8):
    '''
    Calculate volume fractions v1p,v2p,v1s,v2s,vp,vs by means of EBM model.
    
    Parameters
    ----------
    v2 : float
        Volume fraction of the 2nd component.
        The volume fraction of the 1st component
        is not defined as it can be calculated as v1 = (1 - v2).
        The 1st component is by convention (but not necessarily) the matrix.
    v1cr : float, optional, default is 0.156
        Critical volume fraction of the 1st component
        = when the 1st component starts to be continunous.
    v2cr : float, optional, default is 0.156
        Critical volume fraction of the 2nd component
        = when the 2nd component starts to be continunous.
    q1 : float, optional, default is 1.8
        Critical exponent of the 1st component,
        employed in the estimation of continuous volume fraction v1p.
    q2 : float, optional, default is 1.8
        Critical exponent of the 2nd component, 
        employed in the estimation of continuous volume fraction v2p.
        
    Returns
    -------
    vp, v1p, v2p, vs, v1s, v2s : floats
        v1p and vp2 = volume fraction of the 1st and 2nd phase, respectively,
        which is continuous.
        v1s and v2s = volume fraction of the 1st and 2nd phase, respectively,
        which is particulate.
        vp = v1p + v2p = sum of vol.fractions of continuous phases,
        representing paralel branch of the EBM model.
        vs = v1s + v2s = sum of vol.fractions of particulate phases,
        representing serial branch of the EBM model.
    
    Technical note
    --------------
    * This function (vfractions) is usually not called directly.
    * In most cases, it is just called by other functions of this module.

    Note to optional arguments
    --------------------------
    * The optional arguments are 
      the critical volume fractions (v1cr,v2cr) and critical exponents (q1,q2).
    * In the first approximation, they can be left at their default values
      (v1cr = v2cr = 0.156) and (q1 = q2 = 1.8).
    * The default values of are estimated from the percolation theory
      as described in https://doi.org/10.1002/pen.24805 and references therein.
    * Better estimates of v1cr and v2cr (i.e. the volume fractions when the
      first and second phase start to be continuous) can be estimated from the
      analysis of electron micrographs or from some other independt method.
    * The final values of v1cr, v2cr, q1 and q2 for given system
      can be obtained by fitting the EBM model to experimental data.

    Test
    ----
    >>> [round(e,3) for e in vfractions(0.5)]
    [0.398, 0.199, 0.199, 0.602, 0.301, 0.301]
    '''
    
    # (1) If parameter v2 is a numpy-array we need a special treatment!
    if type(v2) == np.ndarray:
        v1 = 1-v2
        # suppress warning about invalid/negative value in power
        # (zero value is never used due to np.where, but numpy warns anyway
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            v1p = np.where(v1 >= v1cr, ((v1-v1cr) / (1-v1cr))**q1, 0)
            v2p = np.where(v2 >= v2cr, ((v2-v2cr) / (1-v2cr))**q2, 0)
            
    # (2) If parameter v2 is a number, we use standard calculations...
    else:
        # Convert v2 to float in order to get 100% compatibility with numpy
        v2 = float(v2) 
        v1  = 1-v2
        v1p = ((v1-v1cr) / (1-v1cr))**q1 if v1 >= v1cr else 0
        v2p = ((v2-v2cr) / (1-v2cr))**q2 if v2 >= v2cr else 0
   
    # (3) The rest is the same for both numbers and np.arrays
    v1s = v1 - v1p
    v2s = v2 - v2p
    vp  = v1p + v2p
    vs  = v1s + v2s
    
    # (4) Return final values (this is also the same for numbers and np.arrays)
    return(vp,v1p,v2p,vs,v1s,v2s)
    

def E(E1,E2,v2, v1cr = 0.156, v2cr = 0.156, q1 = 1.8, q2 = 1.8):
    '''\
    Calculate elastic modulus, E, by means of EBM model.
    
    Parameters
    ----------
    E1 : float
        Elastic modulus of the 1st component.
    E2 : float
        Elastic modulus of the 2nd component.
    v2 : float
        Volume fraction of the 2nd component.
        The volume fraction of the 1st component
        is not defined as it can be calculated as v1 = (1 - v2).
        The 1st component is by convention (but not necessarily) the matrix.
    v1cr : float, optional, default is 0.156
        Critical volume fraction of the 1st component
        = when the 1st component starts to be continunous.
    v2cr : float, optional, default is 0.156
        Critical volume fraction of the 2nd component
        = when the 2nd component starts to be continunous.
    q1 : float, optional, default is 1.8
        Critical exponent of the 1st component,
        employed in the estimation of continuous volume fraction v1p.
    q2 : float, optional, default is 1.8
        Critical exponent of the 2nd component, 
        employed in the estimation of continuous volume fraction v2p.
     
    Returns
    -------
    E : float
        The modulus of the blend according to EBM model.
        
    Note to optional arguments
    --------------------------
    * The optional arguments are 
      the critical volume fractions (v1cr,v2cr) and critical exponents (q1,q2).
    * In the first approximation, they can be left at their default values
      (v1cr = v2cr = 0.156) and (q1 = q2 = 1.8).
    * The default values of are estimated from the percolation theory
      as described in https://doi.org/10.1002/pen.24805 and references therein.
    * Better estimates of v1cr and v2cr (i.e. the volume fractions when the
      first and second phase start to be continuous) can be estimated from the
      analysis of electron micrographs or from some other independt method.
    * The final values of v1cr, v2cr, q1 and q2 for given system
      can be obtained by fitting the EBM model to experimental data.
        
    Test
    ----
    >>> round(E(1,3,0.5), 3)
    1.699
    '''
    
    # (1) Calculate volume fractions vij
    v1 = 1 - v2
    vp,v1p,v2p,vs,v1s,v2s = vfractions(v2,v1cr,v2cr,q1,q2)
    
    # (2) Calculate elastic modulus, E, using vij
    if type(v2) in (int,float):
        # (2a) Argument v2 is a number:
        # Step 1 = standard calculation of E (Ok except for v1=0 and v2=0)
        # (if v1=0 then v2=v2p=1 => v1s=v2s=0 => division by zero at the end
        # (if v2=0 then v1=v1p=1 => v1s=v2s=0 => division by zero at the end
        try:
            E = E1*v1p + E2*v2p + vs**2 / ( v1s/E1 + v2s/E2)
        # Step 2 = if the calculation failed, treat special cases (v1=0, v2=0)
        except ZeroDivisionError:
            if v1 == 0: return(E2)
            if v2 == 0: return(E1)
    else:
        # (2b) Argument v2 is an np.array ...
        # Step 1 = standard calculation of E (Ok except for v1=0 and v2=0)
        # (Suppress warning about zero division + perform standard calculation
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            E = E1*v1p + E2*v2p + vs**2 / (v1s/E1 + v2s/E2) 
        # Step 2 = treat special cases (v1=0, v2=0)
        # (Numpy/vector calculations yields nan for v1=0 and v2=0
        E = np.where(v1 == 0, E2, E)  # correct E values for v1=0
        E = np.where(v2 == 0, E1, E)  # correct E values for v2=0
    
    # (3) Return final value (this is the same for np.arrays and numbers)
    return(E)


def Y(Y1,Y2,v2, v1cr = 0.156, v2cr = 0.156, q1 = 1.8, q2 = 1.8, A = 1):
    '''
    Calculate yield stress, Y, by means of EBM model.
    
    Parameters
    ----------
    E1 : float
        Elastic modulus of the 1st component.
    E2 : float
        Elastic modulus of the 2nd component.
    v2 : float
        Volume fraction of the 2nd component.
        The volume fraction of the 1st component
        is not defined as it can be calculated as v1 = (1 - v2).
        The 1st component is by convention (but not necessarily) the matrix.
    v1cr : float, optional, default is 0.156
        Critical volume fraction of the 1st component
        = when the 1st component starts to be continunous.
    v2cr : float, optional, default is 0.156
        Critical volume fraction of the 2nd component
        = when the 2nd component starts to be continunous.
    q1 : float, optional, default is 1.8
        Critical exponent of the 1st component,
        employed in the estimation of continuous volume fraction v1p.
    q2 : float, optional, default is 1.8
        Critical exponent of the 2nd component, 
        employed in the estimation of continuous volume fraction v2p.
    A : float, optional, default is 1
        Adhesion parameter, which ranges
        from A = 0 (zero interfacial adhesion)
        to A = 1 (perfect interfacial adhesion, no debonding before yield).

    Returns
    -------
    Y : float
        The yield stress of the blend according to EBM model.
        
    Note to optional arguments
    --------------------------
    * The optional arguments are 
      the critical volume fractions (v1cr,v2cr) and critical exponents (q1,q2).
    * In the first approximation, they can be left at their default values
      (v1cr = v2cr = 0.156) and (q1 = q2 = 1.8).
    * The default values of are estimated from the percolation theory
      as described in https://doi.org/10.1002/pen.24805 and references therein.
    * Better estimates of v1cr and v2cr (i.e. the volume fractions when the
      first and second phase start to be continuous) can be estimated from the
      analysis of electron micrographs or from some other independt method.
    * The final values of v1cr, v2cr, q1 and q2 for given system
      can be obtained by fitting the EBM model to experimental data.
        
    Test
    ----
    >>> round(Y(100,200,0.5), 3)
    119.879
    '''        
    
    # (1) Calculate volume fractions, vij
    vp,v1p,v2p,vs,v1s,v2s = vfractions(v2,v1cr,v2cr,q1,q2)
    
    # (2) Calculate yield stress, Y, using the volume fractions vij
    Y = Y1*v1p + Y2*v2p + A*min(Y1,Y2)*vs
    
    # (3) Return the calculated value
    return(Y)

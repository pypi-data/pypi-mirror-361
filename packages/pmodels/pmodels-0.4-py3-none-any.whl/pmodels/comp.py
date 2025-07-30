'''
Module: pmodels.comp
--------------------

* Collection of various predictive models for polymer composites.
* Mostly for two-component composites, isotropic, with isometric filler.
* The models can predict elastic modulus (E) or an arbitrary property (P).

Simple usage

>>> # Standard import of pmodels package
>>> import pmodels as pm
>>>
>>> # (1) Estimate elastic modulus (E) of a polymer composite,
>>> # with an epoxy matrix (E1 ~ 2.5 GPa),
>>> # and 5% of silica particles (E2 ~ 70 GPa).
>>> E_voigt = pm.comp.VoigtRule.P(P1=2.5, P2=70, v2=0.05)
>>> E_reuss = pm.comp.ReussRule.P(P1=2.5, P2=70, v2=0.05)
>>> E_guth  = pm.comp.Guth.E(Em=2.5, vf=0.05)
>>>
>>> # (2) Print the results
>>> # (Note: experimental value ~ 3.0 GPa
>>> print(f'Voigt: {E_voigt:.2f}, Reuss: {E_reuss:.2f}, Guth: {E_guth:.2f}')
Voigt: 5.88, Reuss: 2.63, Guth: 2.90
'''

import sys


class VoigtRule:
    '''
    Voigt rule for binary polymer systems.
    
    * Voigt rule = iso-strain assumption
      = the strain is uniform accross all components.
    * The property is a *weighted arithmetic mean* of the constituent props.
    * Voigt and Reuss rule are bounds,
      real composite properties usually fall between them.
    * Voigt rule is the upper bound, Reuss rule is the lower bound.
    * Voigt rule ~ rule of mixtures, Reuss rule ~ inverse rule of mixtures.
    
    Note
    
    * Voigt rule is equivalent to LIN model.
    * See more details in notes to pmodels.lin module.
    '''
    
    def P(P1,P2,v2):
        '''
        Estimate composite property by means of Voigt rule = upper bound.
        
        * In typical case, the Voigt rule
          predicts upper bound of elastic modulus, E.

        Parameters
        ----------
        P1 : float
            The property of the 1st component (usually the matrix).
        P2 : float
            The property of the 2nd component (usually the filler).
        v2 : float
            The volume fraction of the 2nd component.
            The volume fraction of the 1st component
            can be calculated as v1 = (1 - v2).

        Returns
        -------
        P : float
            Property of the composite acc.to Voight Rule.
        
        Test
        ----
        >>> print(f'{VoigtRule.P(P1=1, P2=100, v2=0.05):.2f}')
        5.95
        '''
        v1 = 1 - v2
        P = P1*v1 + P2*v2
        return(P)


class ReussRule:
    '''
    Reuss rule for binary polymer systems.
    
    * Reuss rule = iso-stress assumption
      = the stress is uniform accross all components.
    * The property is a *weighted harmonic mean* of the constituent props.
    * Voigt and Reuss rule are bounds,
      real composite properties usually fall between them.
    * Reuss rule is the upper bound, Reuss rule is the lower bound.
    * Voigt rule ~ rule of mixtures, Reuss rule ~ inverse rule of mixtures.
    '''
    
    def P(P1,P2,v2):
        '''
        Estimate composite property by means of Reuss rule = lower bound.
        
        * In typical case, the Reuss rule
          predicts lower bound of elastic modulus, E.

        Parameters
        ----------
        P1 : float
            The property of the 1st component (usually the matrix).
        P2 : float
            The property of the 2nd component (usually the filler).
        v2 : float
            The volume fraction of the 2nd component.
            The volume fraction of the 1st component
            can be calculated as v1 = 1 = v2.
            
        Returns
        -------
        P : float
            Property of the composite acc.to Voight Rule.
        
        Test
        ----
        >>> print(f'{ReussRule.P(P1=1, P2=100, v2=0.05):.2f}')
        1.05
        '''

        v1 = 1 - v2
        P = 1 / (v1/P1 + v2/P2)
        return(P)
    

class Einstein:
    '''
    Einstein equation for polymer composites = matrix with filler.
    
    * Einstein equation takes two forms:
        - for bad interfacial adhesion:  Ec = Em(1 + vf)
        - for good interfacial adhesion: Ec = Em(1 + 2.5*vf)
    * Assumption #1 (for both forms of Einstein eq.): Ef >> Em,
      i.e. the filler is much stiffer than the matrix.
    * Assumption #2 (for both forms of Einstein eq.): vf <= 0.05,
      i.e. the filler content is low (below 5 vol.%).
    '''

    def E(Em,vf, adhesion = 0):
        '''
        Predict elastic modulus of a composite by means of Einstein equation.

        Parameters
        ----------
        Em : float
            Elastic modulus of the polymer matrix.
        vf : float
            Volume fraction of the filler.
        adhesion : 0 or 1, optional, default is 1
            If adhesion = 0
            => negligible interfacial adhesion => Ec = Em * (1 + vf).
            If adhesion = 1
            => perfect interfacial adhesion => Ec = Em * (1 + 2.5*vf).

        Returns
        -------
        E : float
            Elastic modulus of the composite.
            
        Test
        ----
        >>> print(f'{Einstein.E(1, 0.05, adhesion=0):.3f}')
        1.050
        >>> print(f'{Einstein.E(1, 0.05, adhesion=1):.3f}')
        1.125
        '''
        if adhesion == 0:
            return( Em * (1 + vf)     )
        elif adhesion == 1:
            return( Em * (1 + 2.5*vf) ) 
        else:
            print('Error in calculation of E using Einstein equation.')
            print('Adhesion parameter can be only 0 or 1.')
            sys.exit()


class Guth:
    '''
    Guth equation for polymer composites = matrix with filler.
    
    * Guth equation is an extension of Einstein equation
      for composites with good interfacial adhesion.
    * Guth equation adds an correction for interparticle interactions
      in the form of additional term, which is a function of vf**2.
    * Assumption (like in Einstein eq,): Ef >> Em,
      i.e. the filler is much stiffer than the matrix.
    '''
    
    def E(Em,vf):
        '''
        Predict elastic modulus of a composite by means of Guth equation.

        Parameters
        ----------
        Em : float
            Elastic modulus of the polymer matrix.
        vf : float
            Volume fraction of the filler.

        Returns
        -------
        E : float
            Elastic modulus of the composite.
            
        Test
        ----
        >>> print(f'{Guth.E(1, 0.05):.3f}')
        1.160
        '''
        return( Em * (1 + 2.5*vf + 14.1*vf**2) )


class Kerner:
    '''
    Kerner equation for polymer composites = matrix with filler.
    
    * Kerner equation is an extension of Einstein equation
      for composites with good interfacial adhesion.
    * Kerner equation considers: (i) non-linear increase in modulus
      for higher filler concentrations and (ii) Poissons ratio of the matrix.
    * Assumption (like in Einstein eq,): Ef >> Em,
      i.e. the filler is much stiffer than the matrix.    
    '''

    def E(Em,vf, poisson = 0.4):
        '''
        Calculate modulus E of a polymer composite using Kerner equation.
        
        Parameters
        ----------
        Em : float
            Elastic modulus of the polymer matrix.
        vf : float
            Volume fraction of the filler.
        poisson : foat, optional, default is 0.4
            Poisson ratio ot the polymer matrix.

        Returns
        -------
        E : float
            Elastic modulus of the composite.
            
        
        Test
        ----
        >>> print(f'{Kerner.E(1, 0.05, poisson=0.4):.3f}')
        1.118
        '''
        E = Em * ( 1 + (15*(1-poisson))/(8-10*poisson) * vf/(1-vf) )
        return(E)

"""
Kinetic law generation and symbolic rate equation construction.

Implements mass-action kinetics by default with support for custom kinetic laws
like Michaelis-Menten, Hill equations, etc.
"""

import sympy as sp
from typing import Dict, List, Callable, Optional, Tuple
import numpy as np
from abc import ABC, abstractmethod

from kinetics_playground.core.model import ReactionModel, Reaction


class KineticLaw(ABC):
    """Abstract base class for kinetic laws."""
    
    @abstractmethod
    def get_rate_expression(self, reaction: Reaction, species_symbols: Dict[str, sp.Symbol]) -> sp.Expr:
        """
        Generate symbolic rate expression for a reaction.
        
        Args:
            reaction: The reaction to generate rate for
            species_symbols: Dict mapping species names to SymPy symbols
            
        Returns:
            SymPy expression for the reaction rate
        """
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, float]:
        """Get parameter dictionary for this kinetic law."""
        pass


class MassActionKinetics(KineticLaw):
    """
    Mass action kinetics: v = k * ∏[S_i]^ν_i
    
    The rate is proportional to the product of reactant concentrations
    raised to their stoichiometric coefficients.
    """
    
    def __init__(self, rate_constant: Optional[float] = None):
        """
        Initialize mass action kinetics.
        
        Args:
            rate_constant: Rate constant k. If None, uses symbolic k
        """
        self.rate_constant = rate_constant
    
    def get_rate_expression(self, reaction: Reaction, species_symbols: Dict[str, sp.Symbol]) -> sp.Expr:
        """
        Generate mass action rate expression.
        
        For reaction: aA + bB -> cC + dD with rate constant k
        Rate = k * [A]^a * [B]^b
        """
        # Create rate constant symbol
        if self.rate_constant is not None:
            k = sp.Float(self.rate_constant)
        else:
            k = reaction.rate_constant if reaction.rate_constant is not None else 1.0
            k = sp.Float(k)
        
        # Build product of reactant concentrations
        rate = k
        for species_name, stoich_coeff in reaction.reactants.items():
            concentration = species_symbols[species_name]
            rate *= concentration ** stoich_coeff
        
        return rate
    
    def get_parameters(self) -> Dict[str, float]:
        """Get rate constant parameter."""
        if self.rate_constant is not None:
            return {"k": self.rate_constant}
        return {}


class MichaelisMentenKinetics(KineticLaw):
    """
    Michaelis-Menten enzyme kinetics: v = Vmax * [S] / (Km + [S])
    
    Commonly used for enzyme-catalyzed reactions.
    """
    
    def __init__(self, vmax: float, km: float, substrate: str, enzyme: Optional[str] = None):
        """
        Initialize Michaelis-Menten kinetics.
        
        Args:
            vmax: Maximum reaction rate
            km: Michaelis constant (substrate concentration at half-maximal rate)
            substrate: Name of substrate species
            enzyme: Optional enzyme species name
        """
        self.vmax = vmax
        self.km = km
        self.substrate = substrate
        self.enzyme = enzyme
    
    def get_rate_expression(self, reaction: Reaction, species_symbols: Dict[str, sp.Symbol]) -> sp.Expr:
        """Generate Michaelis-Menten rate expression."""
        S = species_symbols[self.substrate]
        
        rate = sp.Float(self.vmax) * S / (sp.Float(self.km) + S)
        
        # If enzyme is specified, multiply by enzyme concentration
        if self.enzyme and self.enzyme in species_symbols:
            E = species_symbols[self.enzyme]
            rate *= E
        
        return rate
    
    def get_parameters(self) -> Dict[str, float]:
        """Get MM parameters."""
        return {"Vmax": self.vmax, "Km": self.km}


class HillKinetics(KineticLaw):
    """
    Hill equation for cooperative binding: v = Vmax * [S]^n / (K^n + [S]^n)
    
    Used for reactions with cooperative effects.
    """
    
    def __init__(self, vmax: float, k: float, n: float, substrate: str):
        """
        Initialize Hill kinetics.
        
        Args:
            vmax: Maximum rate
            k: Half-saturation constant
            n: Hill coefficient (cooperativity)
            substrate: Substrate species name
        """
        self.vmax = vmax
        self.k = k
        self.n = n
        self.substrate = substrate
    
    def get_rate_expression(self, reaction: Reaction, species_symbols: Dict[str, sp.Symbol]) -> sp.Expr:
        """Generate Hill equation rate expression."""
        S = species_symbols[self.substrate]
        n = sp.Float(self.n)
        K = sp.Float(self.k)
        Vmax = sp.Float(self.vmax)
        
        rate = Vmax * (S ** n) / (K ** n + S ** n)
        return rate
    
    def get_parameters(self) -> Dict[str, float]:
        """Get Hill parameters."""
        return {"Vmax": self.vmax, "K": self.k, "n": self.n}


class CustomKineticLaw(KineticLaw):
    """User-defined kinetic law from a string formula."""
    
    def __init__(self, formula: str, parameters: Optional[Dict[str, float]] = None):
        """
        Initialize custom kinetic law.
        
        Args:
            formula: String formula using species names in brackets, e.g., "k*[A]*[B]/(1+[A])"
            parameters: Dictionary of parameter names and values
        """
        self.formula = formula
        self.parameters = parameters or {}
    
    def get_rate_expression(self, reaction: Reaction, species_symbols: Dict[str, sp.Symbol]) -> sp.Expr:
        """Parse and return custom rate expression."""
        # Replace species names with symbols
        expr_str = self.formula
        for species_name, symbol in species_symbols.items():
            expr_str = expr_str.replace(f"[{species_name}]", str(symbol))
        
        # Replace parameters
        for param_name, param_value in self.parameters.items():
            expr_str = expr_str.replace(param_name, str(param_value))
        
        # Parse with SymPy
        expr = sp.sympify(expr_str)
        return expr
    
    def get_parameters(self) -> Dict[str, float]:
        """Get custom parameters."""
        return self.parameters.copy()


class KineticSystem:
    """
    Generates symbolic ODE system from reaction network and kinetic laws.
    
    This class constructs the symbolic equations:
        d[S_i]/dt = Σ_j S_ij * v_j
    
    where S_ij is the stoichiometric matrix and v_j are reaction rates.
    """
    
    def __init__(self, model: ReactionModel):
        """
        Initialize kinetic system.
        
        Args:
            model: ReactionModel containing species and reactions
        """
        self.model = model
        self.kinetic_laws: Dict[int, KineticLaw] = {}  # reaction_index -> KineticLaw
        
        # Create species symbols
        self.species_symbols = {
            species.name: sp.Symbol(species.name, real=True, positive=True)
            for species in model.species
        }
        
        # Default: use mass action for all reactions
        for reaction in model.reactions:
            self.kinetic_laws[reaction.index] = MassActionKinetics(reaction.rate_constant)
    
    def set_kinetic_law(self, reaction_index: int, kinetic_law: KineticLaw):
        """
        Set custom kinetic law for a specific reaction.
        
        Args:
            reaction_index: Index of the reaction
            kinetic_law: KineticLaw instance to use
        """
        self.kinetic_laws[reaction_index] = kinetic_law
    
    def get_rate_expressions(self) -> List[sp.Expr]:
        """
        Get symbolic rate expressions for all reactions.
        
        Returns:
            List of SymPy expressions, one for each reaction
        """
        rate_exprs = []
        for reaction in self.model.reactions:
            kinetic_law = self.kinetic_laws[reaction.index]
            rate_expr = kinetic_law.get_rate_expression(reaction, self.species_symbols)
            rate_exprs.append(rate_expr)
        
        return rate_exprs
    
    def get_ode_system(self) -> Dict[sp.Symbol, sp.Expr]:
        """
        Generate symbolic ODE system.
        
        Returns:
            Dictionary mapping species symbols to their time derivatives
        """
        from kinetics_playground.core.stoichiometry import StoichiometricMatrix
        
        # Get stoichiometric matrix
        stoich_matrix = StoichiometricMatrix(self.model)
        S = stoich_matrix.get_matrix()
        
        # Get rate expressions
        rate_exprs = self.get_rate_expressions()
        
        # Compute d[S]/dt = S · v
        ode_system = {}
        for i, species in enumerate(self.model.species):
            symbol = self.species_symbols[species.name]
            
            # Sum over all reactions
            rhs = sp.Integer(0)
            for j, rate_expr in enumerate(rate_exprs):
                stoich_coeff = S[i, j]
                if stoich_coeff != 0:
                    rhs += stoich_coeff * rate_expr
            
            ode_system[symbol] = rhs
        
        return ode_system
    
    def to_numerical_function(self) -> Callable:
        """
        Convert symbolic ODE system to numerical Python function.
        
        Returns:
            Function with signature f(t, y) -> dy/dt suitable for scipy.integrate
        """
        ode_system = self.get_ode_system()
        
        # Get ordered list of species symbols
        symbols = [self.species_symbols[s.name] for s in self.model.species]
        
        # Get ordered list of ODEs
        odes = [ode_system[sym] for sym in symbols]
        
        # Lambdify for fast numerical evaluation
        # Note: lambdify takes (symbols, expression)
        # We create a function that takes t and y array
        funcs = [sp.lambdify(symbols, ode, modules='numpy') for ode in odes]
        
        def dydt(t, y):
            """
            Compute time derivatives.
            
            Args:
                t: Time (not used in autonomous systems)
                y: Array of species concentrations
                
            Returns:
                Array of time derivatives
            """
            return np.array([func(*y) for func in funcs])
        
        return dydt
    
    def to_latex(self) -> List[str]:
        """
        Generate LaTeX representation of the ODE system.
        
        Returns:
            List of LaTeX strings, one for each ODE
        """
        ode_system = self.get_ode_system()
        
        latex_eqs = []
        for species in self.model.species:
            symbol = self.species_symbols[species.name]
            lhs = sp.latex(sp.Derivative(symbol, sp.Symbol('t')))
            rhs = sp.latex(ode_system[symbol])
            latex_eqs.append(f"{lhs} = {rhs}")
        
        return latex_eqs
    
    def summary(self) -> str:
        """Generate text summary of the kinetic system."""
        lines = [
            "Kinetic System",
            f"  Species: {self.model.num_species()}",
            f"  Reactions: {self.model.num_reactions()}",
            "",
            "Rate Expressions:",
        ]
        
        rate_exprs = self.get_rate_expressions()
        for reaction, rate_expr in zip(self.model.reactions, rate_exprs):
            lines.append(f"  {reaction.name}:")
            lines.append(f"    v = {rate_expr}")
        
        lines.append("")
        lines.append("ODE System:")
        ode_system = self.get_ode_system()
        for species in self.model.species:
            symbol = self.species_symbols[species.name]
            lines.append(f"  d[{species.name}]/dt = {ode_system[symbol]}")
        
        return "\n".join(lines)
    
    def __repr__(self):
        return f"KineticSystem(species={self.model.num_species()}, reactions={self.model.num_reactions()})"

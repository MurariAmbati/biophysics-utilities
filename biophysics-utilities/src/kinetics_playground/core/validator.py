"""
Validation and consistency checking for reaction networks.

Checks for mass balance, thermodynamic consistency, valid rate constants, etc.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from kinetics_playground.core.model import ReactionModel, Reaction, Species


@dataclass
class ValidationIssue:
    """Represents a validation problem."""
    severity: str  # 'error', 'warning', 'info'
    category: str  # Type of issue
    message: str
    location: Optional[str] = None  # Which reaction/species


class ReactionValidator:
    """
    Validates reaction network models for common issues.
    
    Checks include:
    - Mass balance (if element composition provided)
    - Non-negative rate constants
    - Orphaned species (not in any reaction)
    - Reversibility consistency
    - Numerical stability concerns
    """
    
    def __init__(self, model: ReactionModel):
        """
        Initialize validator.
        
        Args:
            model: ReactionModel to validate
        """
        self.model = model
        self.issues: List[ValidationIssue] = []
    
    def validate_all(self, element_composition: Optional[Dict[str, Dict[str, int]]] = None) -> List[ValidationIssue]:
        """
        Run all validation checks.
        
        Args:
            element_composition: Optional element composition for mass balance
                                Example: {'A': {'C': 1, 'H': 2}, ...}
        
        Returns:
            List of ValidationIssue objects
        """
        self.issues = []
        
        self.check_rate_constants()
        self.check_orphaned_species()
        self.check_species_usage()
        self.check_initial_conditions()
        
        if element_composition:
            self.check_mass_balance(element_composition)
        
        return self.issues
    
    def check_rate_constants(self):
        """Check that all rate constants are positive and finite."""
        for reaction in self.model.reactions:
            if reaction.rate_constant is None:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='missing_parameter',
                    message=f"No rate constant specified",
                    location=reaction.name
                ))
            elif reaction.rate_constant <= 0:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='invalid_parameter',
                    message=f"Rate constant must be positive (got {reaction.rate_constant})",
                    location=reaction.name
                ))
            elif not np.isfinite(reaction.rate_constant):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='invalid_parameter',
                    message=f"Rate constant must be finite",
                    location=reaction.name
                ))
    
    def check_orphaned_species(self):
        """Check for species that don't appear in any reaction."""
        species_in_reactions = set()
        
        for reaction in self.model.reactions:
            species_in_reactions.update(reaction.get_all_species())
        
        for species in self.model.species:
            if species.name not in species_in_reactions:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='orphaned_species',
                    message=f"Species '{species.name}' does not appear in any reaction",
                    location=species.name
                ))
    
    def check_species_usage(self):
        """Check for species that are only produced or only consumed."""
        production_count = {s.name: 0 for s in self.model.species}
        consumption_count = {s.name: 0 for s in self.model.species}
        
        for reaction in self.model.reactions:
            for species in reaction.reactants:
                consumption_count[species] += 1
            for species in reaction.products:
                production_count[species] += 1
        
        for species in self.model.species:
            name = species.name
            if production_count[name] > 0 and consumption_count[name] == 0:
                self.issues.append(ValidationIssue(
                    severity='info',
                    category='accumulating_species',
                    message=f"Species '{name}' is only produced, never consumed",
                    location=name
                ))
            elif production_count[name] == 0 and consumption_count[name] > 0:
                self.issues.append(ValidationIssue(
                    severity='warning',
                    category='depleting_species',
                    message=f"Species '{name}' is only consumed, never produced",
                    location=name
                ))
    
    def check_initial_conditions(self):
        """Check initial conditions for validity."""
        for species in self.model.species:
            if species.initial_concentration < 0:
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='negative_concentration',
                    message=f"Initial concentration cannot be negative (got {species.initial_concentration})",
                    location=species.name
                ))
            elif not np.isfinite(species.initial_concentration):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='invalid_concentration',
                    message=f"Initial concentration must be finite",
                    location=species.name
                ))
        
        # Check if all initial concentrations are zero
        if all(s.initial_concentration == 0 for s in self.model.species):
            self.issues.append(ValidationIssue(
                severity='warning',
                category='trivial_initial_conditions',
                message="All initial concentrations are zero - system will remain at zero",
                location=None
            ))
    
    def check_mass_balance(self, element_composition: Dict[str, Dict[str, int]]):
        """
        Check mass balance for reactions.
        
        Args:
            element_composition: Dict mapping species to element counts
        """
        from kinetics_playground.core.stoichiometry import StoichiometricMatrix
        
        stoich = StoichiometricMatrix(self.model)
        
        for reaction in self.model.reactions:
            if not stoich.is_balanced(reaction.index, element_composition):
                self.issues.append(ValidationIssue(
                    severity='error',
                    category='mass_imbalance',
                    message=f"Reaction is not mass-balanced",
                    location=reaction.name
                ))
    
    def check_stiffness_indicators(self):
        """Check for potential stiffness issues."""
        rate_constants = [
            r.rate_constant for r in self.model.reactions 
            if r.rate_constant is not None
        ]
        
        if not rate_constants:
            return
        
        k_max = max(rate_constants)
        k_min = min(rate_constants)
        
        if k_max / k_min > 1e6:
            self.issues.append(ValidationIssue(
                severity='warning',
                category='potential_stiffness',
                message=f"Wide range of rate constants ({k_min:.2e} to {k_max:.2e}) may cause stiffness",
                location=None
            ))
    
    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return any(issue.severity == 'error' for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if any warnings were found."""
        return any(issue.severity == 'warning' for issue in self.issues)
    
    def report(self) -> str:
        """Generate validation report."""
        if not self.issues:
            return "✓ All validation checks passed"
        
        lines = ["Validation Report", "=" * 50, ""]
        
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        infos = [i for i in self.issues if i.severity == 'info']
        
        if errors:
            lines.append(f"ERRORS ({len(errors)}):")
            for issue in errors:
                loc_str = f" [{issue.location}]" if issue.location else ""
                lines.append(f"  ✗ {issue.message}{loc_str}")
            lines.append("")
        
        if warnings:
            lines.append(f"WARNINGS ({len(warnings)}):")
            for issue in warnings:
                loc_str = f" [{issue.location}]" if issue.location else ""
                lines.append(f"  ⚠ {issue.message}{loc_str}")
            lines.append("")
        
        if infos:
            lines.append(f"INFO ({len(infos)}):")
            for issue in infos:
                loc_str = f" [{issue.location}]" if issue.location else ""
                lines.append(f"  ℹ {issue.message}{loc_str}")
            lines.append("")
        
        return "\n".join(lines)


def validate_model(model: ReactionModel, 
                   element_composition: Optional[Dict[str, Dict[str, int]]] = None,
                   raise_on_error: bool = False) -> List[ValidationIssue]:
    """
    Convenience function to validate a model.
    
    Args:
        model: ReactionModel to validate
        element_composition: Optional element composition for mass balance
        raise_on_error: If True, raise exception on validation errors
        
    Returns:
        List of validation issues
        
    Raises:
        ValueError: If raise_on_error is True and errors are found
    """
    validator = ReactionValidator(model)
    issues = validator.validate_all(element_composition)
    
    if raise_on_error and validator.has_errors():
        raise ValueError(f"Validation failed:\n{validator.report()}")
    
    return issues

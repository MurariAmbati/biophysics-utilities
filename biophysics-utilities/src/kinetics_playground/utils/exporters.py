"""
Export utilities for converting models to various formats.

Supports SBML, LaTeX, and other exchange formats.
"""

import json
from typing import Optional, Dict
from kinetics_playground.core.model import ReactionModel
from kinetics_playground.core.kinetics import KineticSystem


def export_to_sbml(model: ReactionModel, filename: str, model_name: str = "reaction_network"):
    """
    Export model to SBML (Systems Biology Markup Language) format.
    
    Note: Requires python-libsbml package
    
    Args:
        model: ReactionModel to export
        filename: Output filename
        model_name: Name for the SBML model
    """
    try:
        import libsbml
    except ImportError:
        raise ImportError(
            "SBML export requires python-libsbml. "
            "Install with: pip install python-libsbml"
        )
    
    # Create SBML document
    document = libsbml.SBMLDocument(3, 2)
    sbml_model = document.createModel()
    sbml_model.setId(model_name)
    sbml_model.setName(model_name)
    
    # Create compartment (default: well-mixed)
    compartment = sbml_model.createCompartment()
    compartment.setId('compartment')
    compartment.setConstant(True)
    compartment.setSpatialDimensions(3)
    compartment.setSize(1.0)
    
    # Add species
    for species in model.species:
        sbml_species = sbml_model.createSpecies()
        sbml_species.setId(species.name)
        sbml_species.setName(species.name)
        sbml_species.setCompartment('compartment')
        sbml_species.setInitialConcentration(species.initial_concentration)
        sbml_species.setConstant(species.is_constant)
        sbml_species.setBoundaryCondition(species.is_constant)
        sbml_species.setHasOnlySubstanceUnits(False)
    
    # Add reactions
    for reaction in model.reactions:
        sbml_reaction = sbml_model.createReaction()
        sbml_reaction.setId(f"reaction_{reaction.index}")
        sbml_reaction.setReversible(reaction.reversible)
        sbml_reaction.setFast(False)
        
        # Add reactants
        for species_name, stoich in reaction.reactants.items():
            reactant = sbml_reaction.createReactant()
            reactant.setSpecies(species_name)
            reactant.setStoichiometry(stoich)
            reactant.setConstant(True)
        
        # Add products
        for species_name, stoich in reaction.products.items():
            product = sbml_reaction.createProduct()
            product.setSpecies(species_name)
            product.setStoichiometry(stoich)
            product.setConstant(True)
        
        # Add kinetic law
        if reaction.rate_constant is not None:
            kinetic_law = sbml_reaction.createKineticLaw()
            
            # Create mass action formula
            formula_parts = [f"{reaction.rate_constant}"]
            for species_name, stoich in reaction.reactants.items():
                if stoich == 1:
                    formula_parts.append(species_name)
                else:
                    formula_parts.append(f"({species_name}^{stoich})")
            
            formula = " * ".join(formula_parts)
            math_ast = libsbml.parseL3Formula(formula)
            kinetic_law.setMath(math_ast)
    
    # Write to file
    libsbml.writeSBMLToFile(document, filename)


def export_to_latex(model: ReactionModel, filename: Optional[str] = None) -> str:
    """
    Export model to LaTeX document.
    
    Args:
        model: ReactionModel to export
        filename: Optional output filename
        
    Returns:
        LaTeX string
    """
    lines = []
    
    # Document preamble
    lines.append(r"\documentclass{article}")
    lines.append(r"\usepackage{amsmath}")
    lines.append(r"\usepackage{array}")
    lines.append(r"\begin{document}")
    lines.append("")
    lines.append(r"\section{Reaction Network}")
    lines.append("")
    
    # Species list
    lines.append(r"\subsection{Species}")
    lines.append(r"\begin{itemize}")
    for species in model.species:
        lines.append(f"  \\item ${species.name}$: Initial = {species.initial_concentration}")
    lines.append(r"\end{itemize}")
    lines.append("")
    
    # Reactions
    lines.append(r"\subsection{Reactions}")
    lines.append(r"\begin{align}")
    for reaction in model.reactions:
        # Format reactants
        reactant_terms = []
        for species, coeff in reaction.reactants.items():
            if coeff == 1:
                reactant_terms.append(species)
            else:
                reactant_terms.append(f"{int(coeff) if coeff.is_integer() else coeff}{species}")
        
        # Format products
        product_terms = []
        for species, coeff in reaction.products.items():
            if coeff == 1:
                product_terms.append(species)
            else:
                product_terms.append(f"{int(coeff) if coeff.is_integer() else coeff}{species}")
        
        reactants_str = " + ".join(reactant_terms)
        products_str = " + ".join(product_terms)
        arrow = r"\rightleftharpoons" if reaction.reversible else r"\rightarrow"
        
        k_str = f"k_{reaction.index}" if reaction.rate_constant is None else f"{reaction.rate_constant}"
        
        lines.append(f"  {reactants_str} &{arrow} {products_str} \\quad (k = {k_str}) \\\\")
    
    lines.append(r"\end{align}")
    lines.append("")
    
    # ODE system
    lines.append(r"\subsection{ODE System}")
    kinetic_system = KineticSystem(model)
    latex_eqs = kinetic_system.to_latex()
    
    lines.append(r"\begin{align}")
    for eq in latex_eqs:
        lines.append(f"  {eq} \\\\")
    lines.append(r"\end{align}")
    lines.append("")
    
    # Stoichiometric matrix
    lines.append(r"\subsection{Stoichiometric Matrix}")
    from kinetics_playground.core.stoichiometry import StoichiometricMatrix
    stoich = StoichiometricMatrix(model)
    lines.append(r"\[")
    lines.append(r"S = " + stoich.to_latex())
    lines.append(r"\]")
    lines.append("")
    
    lines.append(r"\end{document}")
    
    latex_content = "\n".join(lines)
    
    # Write to file if specified
    if filename:
        with open(filename, 'w') as f:
            f.write(latex_content)
    
    return latex_content


def export_to_json(model: ReactionModel, filename: str):
    """
    Export model to JSON format.
    
    Args:
        model: ReactionModel to export
        filename: Output filename
    """
    data = {
        'species': [
            {
                'name': s.name,
                'initial_concentration': s.initial_concentration,
                'is_constant': s.is_constant,
                'units': s.units
            }
            for s in model.species
        ],
        'reactions': [
            {
                'index': r.index,
                'reactants': r.reactants,
                'products': r.products,
                'rate_constant': r.rate_constant,
                'reversible': r.reversible,
                'kinetic_law': r.kinetic_law,
                'parameters': r.parameters
            }
            for r in model.reactions
        ]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def export_to_matlab(model: ReactionModel, filename: str):
    """
    Export model as MATLAB/Octave script.
    
    Args:
        model: ReactionModel to export
        filename: Output filename (.m)
    """
    lines = []
    
    lines.append("% Reaction network model")
    lines.append("% Auto-generated by Kinetics Playground")
    lines.append("")
    
    # ODE function
    lines.append("function dydt = reaction_network(t, y)")
    lines.append("    % Species concentrations")
    for i, species in enumerate(model.species):
        lines.append(f"    {species.name} = y({i+1});  % {species.name}")
    lines.append("")
    
    # Rate equations
    kinetic_system = KineticSystem(model)
    ode_system = kinetic_system.get_ode_system()
    
    lines.append("    % Rate equations")
    lines.append("    dydt = zeros(size(y));")
    for i, species in enumerate(model.species):
        symbol = kinetic_system.species_symbols[species.name]
        expr = ode_system[symbol]
        # Convert SymPy expression to MATLAB syntax
        expr_str = str(expr).replace('**', '^')
        lines.append(f"    dydt({i+1}) = {expr_str};  % d[{species.name}]/dt")
    lines.append("end")
    lines.append("")
    
    # Initial conditions and simulation
    lines.append("% Initial conditions")
    y0_values = ", ".join(str(s.initial_concentration) for s in model.species)
    lines.append(f"y0 = [{y0_values}];")
    lines.append("")
    lines.append("% Time span")
    lines.append("tspan = [0 100];")
    lines.append("")
    lines.append("% Solve ODE")
    lines.append("[t, y] = ode45(@reaction_network, tspan, y0);")
    lines.append("")
    lines.append("% Plot results")
    lines.append("figure;")
    lines.append("plot(t, y);")
    lines.append(f"legend({', '.join(repr(s.name) for s in model.species)});")
    lines.append("xlabel('Time');")
    lines.append("ylabel('Concentration');")
    lines.append("title('Reaction Network Dynamics');")
    
    with open(filename, 'w') as f:
        f.write("\n".join(lines))


def export_results_to_csv(results, filename: str):
    """
    Export simulation results to CSV.
    
    Args:
        results: IntegrationResult object
        filename: Output filename
    """
    import pandas as pd
    
    # Convert to dictionary
    data = results.to_dict()
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv(filename, index=False)

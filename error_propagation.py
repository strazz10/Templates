"""
error_propagation.py

Propagates experimental uncertainties through a formula using the standard
first-order (partial derivative) error propagation formula, assuming the
input variables are independent:

    sigma_f^2 = sum_i ( df/dx_i )^2 * sigma_xi^2

Requires: sympy  (pip install sympy)

Usage:
    Edit the "USER INPUT" section at the bottom of this file, or import
    propagate() / report() into your own analysis script:

        from error_propagation import report
        report("g", "4*pi**2*L/T**2",
               values={"L": 0.500, "T": 1.420},
               uncertainties={"L": 0.001, "T": 0.020},
               units="m/s^2")
"""

import sympy as sp
from math import floor, log10


def propagate(formula, values, uncertainties):
    """
    Propagate uncertainties through `formula` using partial derivatives.

    Parameters
    ----------
    formula : str
        Formula as a string using variable names, e.g. "4*pi**2*L/T**2"
    values : dict
        Central (measured) values, e.g. {"L": 0.500, "T": 1.42}
    uncertainties : dict
        Uncertainty (standard error) on each variable, e.g. {"L": 0.001, "T": 0.02}

    Returns
    -------
    (float, float, dict)
        central value, propagated uncertainty, and each variable's individual
        contribution to that uncertainty (in the same units as f)
    """
    symbols = {name: sp.Symbol(name) for name in values}
    expr = sp.sympify(formula, locals={**symbols, "pi": sp.pi})

    subs = {symbols[name]: values[name] for name in values}
    central_value = float(expr.subs(subs))

    variance = 0.0
    contributions = {}
    for name, sym in symbols.items():
        if name not in uncertainties or uncertainties[name] == 0:
            continue
        deriv_val = float(sp.diff(expr, sym).subs(subs))
        term = (deriv_val * uncertainties[name]) ** 2
        contributions[name] = term ** 0.5
        variance += term

    sigma = variance ** 0.5
    return central_value, sigma, contributions


def round_to_sig_figs(value, uncertainty, sig_figs=None):
    """
    Round `value` and `uncertainty` so the uncertainty has `sig_figs`
    significant figures, and `value` is rounded to the same decimal place
    (the standard physics-lab reporting convention, e.g. 9.81 +/- 0.03).

    If sig_figs is None (default), follows the common convention from
    Taylor's "An Introduction to Error Analysis": use 1 significant figure,
    unless the leading digit is 1, in which case use 2 -- since rounding
    e.g. 0.11 down to "0.1" would discard a disproportionate amount of
    relative precision. Pass sig_figs=1 or sig_figs=2 explicitly to override.
    """
    if uncertainty == 0:
        return value, uncertainty
    exponent = floor(log10(abs(uncertainty)))
    if sig_figs is None:
        leading_digit = int(abs(uncertainty) / 10 ** exponent)
        sig_figs = 2 if leading_digit == 1 else 1
    decimals = -(exponent - (sig_figs - 1))
    return round(value, decimals), round(uncertainty, decimals)


def report(name, formula, values, uncertainties, units="", sig_figs=None):
    """Compute and pretty-print a full error-propagation result."""
    central, sigma, contributions = propagate(formula, values, uncertainties)
    v_rounded, s_rounded = round_to_sig_figs(central, sigma, sig_figs)

    print(f"{name} = {formula}")
    print(f"  Result: {name} = {v_rounded} +/- {s_rounded} {units}")
    if central != 0:
        print(f"  Relative uncertainty: {100 * sigma / abs(central):.2f} %")
    print("  Contribution to uncertainty budget, by variable:")
    for var, contrib in sorted(contributions.items(), key=lambda x: -x[1]):
        pct = 100 * contrib ** 2 / sigma ** 2 if sigma > 0 else 0
        print(f"    {var}: {contrib:.4g} {units}  ({pct:.1f}% of variance)")
    print()
    return v_rounded, s_rounded


# ---------------------------------------------------------------------------
# USER INPUT -- edit this section for your own experiment, or import the
# functions above into your own analysis script instead.
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    # Example 1: simple pendulum, g = 4*pi^2*L/T^2
    report(
        name="g",
        formula="4*pi**2*L/T**2",
        values={"L": 0.500, "T": 1.420},          # meters, seconds
        uncertainties={"L": 0.001, "T": 0.020},   # meters, seconds
        units="m/s^2",
    )

    # Example 2: density of a cylinder, rho = m / (pi * r^2 * h)
    report(
        name="rho",
        formula="m/(pi*r**2*h)",
        values={"m": 15.20, "r": 1.05, "h": 4.50},         # g, cm, cm
        uncertainties={"m": 0.05, "r": 0.02, "h": 0.05},   # g, cm, cm
        units="g/cm^3",
    )

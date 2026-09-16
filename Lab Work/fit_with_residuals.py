"""
fit_with_residuals.py

Fits a generic model that must be specified in the script (default y = a + b*x + c*x^2)  to (x, y, sigma_y) data loaded
from a plain text/CSV data file, and plots the best-fit curve together with
a residuals panel underneath -- the standard way to present a fit result in
a lab report.

Data file format
-----------------
A whitespace- OR comma-separated text file with three columns: x, y, sigma_y
(one measurement per row). Lines starting with '#' are ignored, so you can
document units/instrument/conditions there. Example (see fit_data.dat):

    # x [s]   y [a.u.]   sigma_y [a.u.]
    0.5       35         10.0
    1.1       61         10.0
    ...

Usage
-----
    python fit_with_residuals.py                     # uses fit_data.dat
    python fit_with_residuals.py mydata.csv           # uses your own file
    python fit_with_residuals.py mydata.csv --save fig.png   # save instead of display
"""

import argparse

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def load_data(path):
    """
    Load (x, y, sigma_y) columns from a data file.

    Accepts either whitespace-separated or comma-separated files (detected
    automatically from the first non-comment, non-blank line), so students
    can export from a spreadsheet as CSV or just type columns by hand.
    """
    with open(path) as f:
        first_data_line = next(
            line for line in f if line.strip() and not line.strip().startswith("#")
        )
    delimiter = "," if "," in first_data_line else None

    x, y, sigma = np.loadtxt(path, comments="#", delimiter=delimiter, unpack=True)
    return x, y, sigma


def model(x, a, b, c):
    """Quadratic fitting model: y = a + b*x + c*x^2."""
    return a + b * x + c * x**2


def fit_and_plot(x, y, sigma, save_path=None):
    # Perform the fit. absolute_sigma=True tells curve_fit that `sigma` is a
    # real, calibrated measurement uncertainty (not just a relative weight),
    # so the reported parameter uncertainties are NOT silently rescaled to
    # force chi2/dof = 1 -- see note in the accompanying explanation.
    popt, pcov = curve_fit(model, x, y, sigma=sigma, absolute_sigma=True)
    perr = np.sqrt(np.diag(pcov))

    # Residuals with respect to the best-fit model, and a goodness-of-fit
    # summary that's usually the actual point of doing this exercise.
    res = y - model(x, *popt)
    dof = len(x) - len(popt)
    chi2 = np.sum((res / sigma) ** 2)

    print("Best-fit parameters:")
    for name, value, err in zip("abc", popt, perr):
        print(f"  {name} = {value:.4g} +/- {err:.4g}")
    print(f"chi2 / dof = {chi2:.3g} / {dof} = {chi2 / dof:.3g}")

    # Create the main figure and split it into a data panel and a residuals
    # panel that share the x axis.
    fig = plt.figure("Fit and residuals")
    ax1, ax2 = fig.subplots(
        2, 1, sharex=True, gridspec_kw=dict(height_ratios=[2, 1], hspace=0.05)
    )

    # Top panel: the data with error bars and the best-fit curve.
    ax1.errorbar(x, y, sigma, fmt="o", label="Data")
    xgrid = np.linspace(x.min(), x.max(), 200)
    ax1.plot(xgrid, model(xgrid, *popt), label="Best-fit model")
    ax1.set_ylabel("y [a.u.]")
    ax1.grid(color="lightgray", ls="dashed")
    ax1.legend()

    # Bottom panel: the residuals, with a zero-reference line standing in
    # for "the model" in this representation.
    ax2.errorbar(x, res, sigma, fmt="o")
    ax2.axhline(0.0, color="tab:orange")
    ax2.set_xlabel("x [a.u.]")
    ax2.set_ylabel("Residuals [a.u.]")
    ax2.grid(color="lightgray", ls="dashed")

    fig.align_ylabels((ax1, ax2))

    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"Figure saved to {save_path}")
    else:
        plt.show()

    return popt, perr


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "datafile",
        nargs="?",
        default="fit_data.dat",
        help="path to a text/CSV file with columns x, y, sigma_y (default: fit_data.dat)",
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        default=None,
        help="save the figure to PATH instead of opening an interactive window",
    )
    args = parser.parse_args()

    x, y, sigma = load_data(args.datafile)
    fit_and_plot(x, y, sigma, save_path=args.save)

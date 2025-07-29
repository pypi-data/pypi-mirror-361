"""polka: Implementation of polarimetric models"""

import lmfit
import numpy as np
from scipy.optimize import root as scipy_root

# MODELS = ["LinExp", "Trigon"]
MODELS = ["LinExp"]


class LinExp:
    """Linear-Exponential model from Muinonen+2002"""

    def __init__(self, a=np.nan, b=np.nan, c=np.nan):
        self.NAME = "LinExp"
        self.PARAMS = ("a", "b", "c")

    def eval(self, phase, a=None, b=None, c=None):
        """Evaluate LinExp model for given phase and parameters."""
        aa = a if a is not None else getattr(self, "a")
        bb = b if b is not None else getattr(self, "b")
        cc = c if c is not None else getattr(self, "c")
        return aa * (np.exp(-phase / bb) - 1) + cc * phase

    def fit(self, pc, weights=None):
        """Fit a phase curve using the Linear-Exponential model."""

        # LMFit model definition
        model = lmfit.Model(self.eval)

        # LMFit parameters
        params = lmfit.Parameters()
        params.add("a", value=15, min=0, max=30)
        params.add("b", value=10, min=0, max=20)
        params.add("c", value=0.1, min=-10, max=10)

        if weights is not None:
            weights_band = weights
        else:
            weights_band = np.ones(pc.phase.shape)

        # And fit
        result = model.fit(
            pc.pol,
            params,
            phase=pc.phase,
            weights=weights,
            method="least_squares",
            fit_kws={"loss": "soft_l1"},
        )

        # Add fit parameters to the model instance
        for param in self.PARAMS:
            setattr(self, param, result.params[param].value)
            setattr(self, f"{param}_err", result.params[param].stderr)

        # Add derived parameters
        self.alpha_min = -self.b * np.log(self.b * self.c / self.a)
        self.pol_min = self.eval( self.alpha_min, self.a, self.b, self.c)

        sol = scipy_root(
            self.eval,
            25.0,
            args=(self.a, self.b, self.c),
        )
        self.alpha_inv = sol["x"][0] if sol["success"] else np.nan

        self.slope = self.c - (self.a/self.b) * np.exp(-self.alpha_inv / self.b)

        pc.fitted_models.add("LinExp")
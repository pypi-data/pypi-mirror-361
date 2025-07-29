import numpy as np
import polka
import rocks


class PhaseCurve:
    """Polarimetric phase curve of the asteroid."""

    def __init__(
        self,
        phase=None,
        pol=None,
        pol_err=None,
        src=None,
        epoch=None,
        target=None,
    ):
        """Create a polarimetric phase curve.

        Parameters
        ----------
        phase : list or np.array
            Phase angle (in degrees).
        pol : list or np.array
            Degree of linear polarisation (in percent).
        pol_err : list or np.array
            Error on the degree of linear polarisation (in percent).
        src : list
            Source of the observation.
        epoch : list or np.array
            Epoch of observation (in JD).
        target : int or str
            The target asteroid.
        """

        # Observations
        self.phase = np.array(phase)
        self.pol = np.array(pol)
        self.pol_err = (
            np.array(pol_err) if pol_err is not None else np.zeros(self.pol.shape)
        )
        self.src = np.array(src)
        self.epoch = np.array(epoch) if epoch is not None else epoch

        # Metadata
        self.target = target
        if target is not None:
            self.target = rocks.Rock(target)

        # Modeling
        self.fitted_models = set()  # keep track of models fit to data

    def fit(self, models=None, weights=None):
        """Fit the polarimetric phase curve with the different models."""

        if models is None:
            models = polka.models.MODELS

        for model in models:
            if model not in polka.models.MODELS:
                raise ValueError(
                    f"Unknown model '{model}'. Expected one of {polka.models.MODELS}"
                )

            # Add polarimetric model instance to PhaseCurve
            setattr(self, model, getattr(polka.models, model)())
            getattr(self, model).fit(self, weights=weights)

    def get_ephems(self):
        """Query ephemerides of target at time of observations.

        Note
        ----
        Sets the 'phase' attribute. Requires internet connection.
        """
        print("Querying ephemerides via LTE Miriade..")
        ephem = polka.miriade.query(self.target.name, self.epoch)
        self.phase = ephem["Phase"].to_numpy()

    def plot(
        self,
        models=None,
        label_sources=False,
        show_parameters=False,
        black=False,
        save=None,
    ):
        """Plot polarimetric phase curve and model fits.

        Parameters
        ----------
        models : list of str
            Name of models to plot. By default, all fitted models are plotted.
        """
        if models is None:
            models = sorted(self.fitted_models)

        polka.plotting.plot_pc(
            self, models, label_sources, show_parameters, black, save
        )

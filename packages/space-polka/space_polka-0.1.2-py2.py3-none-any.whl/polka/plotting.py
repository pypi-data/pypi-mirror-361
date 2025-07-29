import numpy as np
import matplotlib.pyplot as plt

import polka
import rocks


def plot_pc(
    pc, models, label_sources=False, show_parameters=False, black=False, save=None
):
    """Plot polrimetric phase curve and model fits."""

    # Define figure
    if black:
        plt.style.use("dark_background")
    else:
        plt.style.use("default")
    fig, ax = plt.subplots()

    # Global phase range
    xmax = pc.phase.max() + 3
    phase_eval = np.linspace(0, xmax, 100)

    # Observations
    if label_sources and pc.src is not None:

        for s in np.unique(pc.src):
            cond = np.where(pc.src == s)
            ax.errorbar(
                pc.phase[cond],
                pc.pol[cond],
                yerr=pc.pol_err[cond],
                ls="",
                marker="o",
                label=s,
            )
    else:
        ax.errorbar(
            pc.phase,
            pc.pol,
            yerr=pc.pol_err,
            ls="",
            marker="o",
            label=f"Observations",
        )

    # Models
    for i, model in enumerate(models):

        # Switch to actual model instance
        model = getattr(pc, model)
        params = model.PARAMS

        # Plot model
        pol_eval = model.eval(phase_eval)
        ax.plot(phase_eval, pol_eval, color=f"C{i+1}", ls="-", label=model.NAME)

        # Derived parameters
        if show_parameters:
            ax.axhline(model.pol_min, ls="--", color=f"C{i+1}", lw=0.5)
            ax.axvline(model.alpha_min, ls="--", color=f"C{i+1}", lw=0.5)
            ax.axvline(model.alpha_inv, ls="dotted", color=f"C{i+1}", lw=0.5)

    # Axes
    ax.set(
        xlabel="Phase angle (deg.)",
        ylabel="Linear polarisation (%)",
        xlim=(0, xmax),
    )
    ax.axhline(0, ls="-", color="gray", lw=0.5)

    # Legend
    ax.legend(
        title=(
            f"({pc.target.number}) {pc.target.name}"
            if isinstance(pc.target, rocks.Rock)
            else None
        )
    )

    # Export
    if save is None:
        plt.show()
    else:
        fig.tight_layout()
        fig.savefig(save)
        print(f"Saved figure under {save}")

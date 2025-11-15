"""Plotting helpers for viscoelastic responses."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .models import Response


def plot_response(result: Response, *, show: bool = False, save_path: Optional[str] = None) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "matplotlib is required for plotting. Install it or avoid --plot/--plot-file options."
        ) from exc

    fig, ax = plt.subplots()
    ax.plot(result.time, result.response, lw=2.0, color="#1f77b4")
    ax.set_xlabel("Time (s)")
    ylabel = "Stress" if result.quantity == "stress" else "Strain"
    ax.set_ylabel(f"{ylabel} (SI units)")
    ax.set_title(f"{result.label} — τ = {result.tau:.3g} s")
    ax.grid(True, alpha=0.3)

    if save_path:
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight")

    if show:
        plt.show()
    else:
        plt.close(fig)

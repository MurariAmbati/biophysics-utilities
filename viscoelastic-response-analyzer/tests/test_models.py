from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from viscoelastic_analyzer.models import SimulationConfig
from viscoelastic_analyzer.solver import compute_response


def test_maxwell_relaxation_matches_closed_form():
    cfg = SimulationConfig(
        model="maxwell",
        mode="relaxation",
        E=1000.0,
        eta=5000.0,
        strain0=0.02,
        stress0=None,
        t_max=2.0,
        dt=0.5,
    )
    result = compute_response(cfg)
    tau = cfg.eta / cfg.E
    expected = cfg.E * cfg.strain0 * np.exp(-result.time / tau)
    np.testing.assert_allclose(result.response, expected)


def test_kelvin_voigt_creep_asymptote():
    cfg = SimulationConfig(
        model="kelvin_voigt",
        mode="creep",
        E=2000.0,
        eta=8000.0,
        strain0=None,
        stress0=1.5,
        t_max=20.0,
        dt=1.0,
    )
    result = compute_response(cfg)
    steady_state = cfg.stress0 / cfg.E
    assert pytest.approx(steady_state, rel=1e-2) == result.response[-1]


def test_kelvin_voigt_relaxation_rejected():
    cfg = SimulationConfig(
        model="kelvin_voigt",
        mode="relaxation",
        E=1500.0,
        eta=7000.0,
        strain0=0.01,
        stress0=None,
        t_max=1.0,
        dt=0.1,
    )
    with pytest.raises(ValueError):
        compute_response(cfg)


def test_cli_creep_json(tmp_path: Path):
    json_path = tmp_path / "out.json"
    cmd = [
        sys.executable,
        "-m",
        "viscoelastic_analyzer.cli",
        "--model",
        "maxwell",
        "--mode",
        "creep",
        "--E",
        "1000",
        "--eta",
        "5000",
        "--stress0",
        "1.0",
        "--t_max",
        "1.0",
        "--dt",
        "0.5",
        "--json-out",
        str(json_path),
        "--quiet",
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    payload = json.loads(json_path.read_text())
    assert payload["quantity"] == "strain"
    assert len(payload["time"]) == len(payload["response"]) > 0

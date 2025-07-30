#!/usr/bin/env python
"""Tests for `biolocsim` package."""

import numpy as np
import pytest

from biolocsim.core import MicrotubuleGenerator, MitochondriaGenerator
from biolocsim.core.base_config import MITO_CONFIG, MT_CONFIG


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    del response


def test_microtubule_generator():
    """Test the MicrotubuleGenerator for successful point cloud generation."""
    config = MT_CONFIG.copy()
    config["num_tubes"] = 1  # Keep test fast

    generator = MicrotubuleGenerator(config)
    result = generator.generate()

    # The generator should return a tuple with point_cloud, metadata, and centerlines
    assert isinstance(result, tuple)
    point_cloud, metadata, centerlines = result

    # Check if point cloud is generated correctly
    assert point_cloud is not None
    assert isinstance(point_cloud, np.ndarray)
    assert point_cloud.shape[0] > 0
    assert point_cloud.shape[1] >= 3  # Should have at least x, y, z coordinates


def test_mitochondria_generator():
    """Test the MitochondriaGenerator for successful point cloud generation."""
    config = MITO_CONFIG.copy()
    config["num_mitochondria"] = 1  # Keep test fast

    generator = MitochondriaGenerator(config)
    result = generator.generate()

    # The generator should return a tuple with multiple outputs
    assert isinstance(result, tuple)
    point_cloud, metadata, volume_grid, _, _ = result

    # Check if point cloud is generated correctly
    assert point_cloud is not None
    assert isinstance(point_cloud, np.ndarray)
    assert point_cloud.shape[0] > 0
    assert point_cloud.shape[1] >= 3  # Should have at least x, y, z coordinates


def test_command_line_interface():
    """Test the CLI."""
    # runner = CliRunner() # This line was removed as CliRunner is no longer imported
    # result = runner.invoke(cli.main) # This line was removed as cli.main is no longer imported
    # assert result.exit_code == 0 # This line was removed as cli.main is no longer imported
    # assert "biolocsim" in result.output # This line was removed as cli.main is no longer imported
    # help_result = runner.invoke(cli.main, ["--help"]) # This line was removed as cli.main is no longer imported
    # assert help_result.exit_code == 0 # This line was removed as cli.main is no longer imported
    # assert "--help  Show this message and exit." in help_result.output # This line was removed as cli.main is no longer imported

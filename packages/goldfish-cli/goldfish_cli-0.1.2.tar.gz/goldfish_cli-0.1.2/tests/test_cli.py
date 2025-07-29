"""Tests for CLI functionality"""
import pytest
from click.testing import CliRunner

from goldfish_cli.main import cli


def test_cli_version():
    """Test CLI version command"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "Goldfish CLI v" in result.output


def test_cli_help():
    """Test CLI help command"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Goldfish - AI-First Personal Knowledge Management" in result.output


def test_cli_no_interactive():
    """Test CLI no-interactive mode"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--no-interactive"])
    assert result.exit_code == 0
    assert "Welcome to Goldfish" in result.output


@pytest.mark.parametrize("command", ["capture", "suggestions", "dashboard", "config"])
def test_subcommands_exist(command):
    """Test that all main subcommands exist"""
    runner = CliRunner()
    result = runner.invoke(cli, [command, "--help"])
    assert result.exit_code == 0

"""Tests to improve CLI coverage through direct testing"""
from unittest.mock import Mock, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestCLICoverageImprovement:
    """Tests designed to improve coverage of CLI modules"""

    def test_capture_quick_command_exists(self):
        """Test capture quick command exists and is accessible"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture', 'quick', '--help'])
        assert result.exit_code == 0
        assert "Quick capture text" in result.output

    def test_capture_analyze_command_exists(self):
        """Test capture analyze command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture', 'analyze', '--help'])
        assert result.exit_code == 0

    def test_capture_file_command_exists(self):
        """Test capture file command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture', 'file', '--help'])
        assert result.exit_code == 0

    def test_suggestions_list_command_exists(self):
        """Test suggestions list command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions', 'list', '--help'])
        assert result.exit_code == 0

    def test_suggestions_approve_command_exists(self):
        """Test suggestions approve command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions', 'approve', '--help'])
        assert result.exit_code == 0

    def test_suggestions_reject_command_exists(self):
        """Test suggestions reject command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions', 'reject', '--help'])
        assert result.exit_code == 0

    def test_config_show_command_exists(self):
        """Test config show command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'show', '--help'])
        assert result.exit_code == 0

    def test_config_set_command_exists(self):
        """Test config set command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'set', '--help'])
        assert result.exit_code == 0

    def test_config_get_command_exists(self):
        """Test config get command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', 'get', '--help'])
        assert result.exit_code == 0

    def test_dashboard_tasks_command_exists(self):
        """Test dashboard tasks command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard', 'tasks', '--help'])
        assert result.exit_code == 0

    def test_dashboard_entities_command_exists(self):
        """Test dashboard entities command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard', 'entities', '--help'])
        assert result.exit_code == 0

    def test_dashboard_stats_command_exists(self):
        """Test dashboard stats command exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard', 'stats', '--help'])
        assert result.exit_code == 0

    def test_watch_group_exists(self):
        """Test watch group exists"""
        runner = CliRunner()
        result = runner.invoke(cli, ['watch', '--help'])
        assert result.exit_code == 0

    @patch('goldfish_cli.main._register_subcommands')
    def test_register_subcommands_called_on_cli_invoke(self, mock_register):
        """Test that subcommands are registered on CLI invoke"""
        runner = CliRunner()
        runner.invoke(cli, ['--version'])
        mock_register.assert_called_once()

    def test_cli_invalid_subcommand(self):
        """Test CLI with invalid subcommand"""
        runner = CliRunner()
        result = runner.invoke(cli, ['nonexistent-command'])
        assert result.exit_code != 0

    def test_cli_capture_with_no_subcommand(self):
        """Test capture group with no subcommand shows help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture'])
        assert result.exit_code == 0
        assert "Commands:" in result.output or "Usage:" in result.output

    def test_cli_suggestions_with_no_subcommand(self):
        """Test suggestions group with no subcommand shows help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions'])
        assert result.exit_code == 0

    def test_cli_config_with_no_subcommand(self):
        """Test config group with no subcommand shows help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['config'])
        assert result.exit_code == 0

    def test_cli_dashboard_with_no_subcommand(self):
        """Test dashboard group with no subcommand shows help"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard'])
        assert result.exit_code == 0

    def test_version_flag_format(self):
        """Test version flag shows correct format"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert "Goldfish CLI v" in result.output
        # Should contain version number
        import re
        version_pattern = r"Goldfish CLI v\d+\.\d+\.\d+"
        assert re.search(version_pattern, result.output)

    def test_help_flag_shows_usage(self):
        """Test help flag shows usage information"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "Commands:" in result.output

    def test_no_interactive_flag_shows_welcome(self):
        """Test no-interactive flag shows welcome panel"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--no-interactive'])
        assert result.exit_code == 0
        assert "Welcome to Goldfish" in result.output
        assert "goldfish capture" in result.output

    @patch('goldfish_cli.main.GoldfishREPL')
    def test_interactive_mode_attempted(self, mock_repl_class):
        """Test that interactive mode is attempted by default"""
        mock_repl = Mock()
        mock_repl_class.return_value = mock_repl

        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        mock_repl_class.assert_called_once()
        mock_repl.start.assert_called_once()

    @patch('goldfish_cli.main.GoldfishREPL')
    def test_interactive_mode_error_handling(self, mock_repl_class):
        """Test error handling when REPL fails to start"""
        mock_repl_class.side_effect = Exception("REPL failed")

        runner = CliRunner()
        result = runner.invoke(cli, [])

        assert result.exit_code == 0
        assert "Error starting interactive mode" in result.output
        assert "--no-interactive" in result.output

    def test_combined_flags_precedence(self):
        """Test flag precedence when multiple flags are used"""
        runner = CliRunner()

        # Version should take precedence over no-interactive
        result = runner.invoke(cli, ['--version', '--no-interactive'])
        assert result.exit_code == 0
        assert "Goldfish CLI v" in result.output
        assert "Welcome to Goldfish" not in result.output

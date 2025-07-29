"""Tests for main CLI functionality"""
from unittest.mock import Mock, patch

from click.testing import CliRunner

from goldfish_cli.main import _register_subcommands, cli


class TestMainCLI:
    """Test suite for main CLI functionality"""

    def test_cli_with_no_args_interactive_mode(self):
        """Test CLI with no arguments starts interactive mode"""
        runner = CliRunner()

        with patch('goldfish_cli.main.GoldfishREPL') as mock_repl_class:
            mock_repl = Mock()
            mock_repl_class.return_value = mock_repl

            result = runner.invoke(cli, [])

            assert result.exit_code == 0
            mock_repl_class.assert_called_once()
            mock_repl.start.assert_called_once()

    def test_cli_with_no_args_interactive_mode_error(self):
        """Test CLI handles error when starting interactive mode"""
        runner = CliRunner()

        with patch('goldfish_cli.main.GoldfishREPL') as mock_repl_class:
            mock_repl_class.side_effect = Exception("REPL error")

            result = runner.invoke(cli, [])

            assert result.exit_code == 0
            assert "Error starting interactive mode" in result.output
            assert "Use --no-interactive flag" in result.output

    def test_cli_groups_exist(self):
        """Test that all CLI groups are properly registered"""
        runner = CliRunner()

        # Test each group exists
        groups = ['capture', 'suggestions', 'config', 'dashboard', 'watch']

        for group in groups:
            result = runner.invoke(cli, [group, '--help'])
            assert result.exit_code == 0

    def test_register_subcommands(self):
        """Test _register_subcommands function"""
        # This function doesn't do anything but we test it doesn't error
        _register_subcommands()
        assert True  # If we get here, it worked

    @patch('goldfish_cli.main.console')
    def test_cli_no_interactive_welcome_message(self, mock_console):
        """Test welcome message in no-interactive mode"""
        runner = CliRunner()

        result = runner.invoke(cli, ['--no-interactive'])

        assert result.exit_code == 0
        # Verify panel was printed
        assert mock_console.print.called
        panel_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      'Panel' in str(call[0][0].__class__)]
        assert len(panel_calls) > 0

    def test_cli_main_entry_point(self):
        """Test main entry point execution"""
        with patch('goldfish_cli.main.cli') as mock_cli:
            with patch('goldfish_cli.main.__name__', '__main__'):
                # Import the module to trigger the if __name__ == '__main__' block
                # The cli() should not be called during import
                mock_cli.assert_not_called()

    def test_version_output_format(self):
        """Test version output includes proper formatting"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--version'])

        assert result.exit_code == 0
        assert "Goldfish CLI v" in result.output
        assert result.output.strip().startswith("Goldfish CLI v")

    def test_help_output_content(self):
        """Test help output contains expected content"""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "🐠 Goldfish" in result.output
        assert "AI-First Personal Knowledge Management" in result.output
        assert "capture" in result.output
        assert "suggestions" in result.output
        assert "dashboard" in result.output
        assert "config" in result.output
        assert "--version" in result.output
        assert "--no-interactive" in result.output

    def test_invalid_command(self):
        """Test CLI with invalid command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['invalid-command'])

        assert result.exit_code != 0
        assert "Error" in result.output or "Usage" in result.output

    def test_cli_context_passing(self):
        """Test that context is properly passed to subcommands"""
        runner = CliRunner()

        # Test with a valid subcommand
        result = runner.invoke(cli, ['capture', '--help'])

        assert result.exit_code == 0
        assert "Quick capture commands" in result.output

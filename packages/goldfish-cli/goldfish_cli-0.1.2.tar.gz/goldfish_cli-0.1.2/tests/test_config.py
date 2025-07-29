"""Tests for config commands"""
from pathlib import Path
from unittest.mock import mock_open, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestConfigCommands:
    """Test suite for config commands"""

    @patch('goldfish_cli.config.get_config_dir')
    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_show(self, mock_console, mock_get_config_file, mock_get_config_dir):
        """Test config show command"""
        runner = CliRunner()

        # Mock config values
        mock_get_config_dir.return_value = Path("/home/user/.config/goldfish")
        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        # Mock config file exists and contains data
        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"api_key": "test123"}')):
                result = runner.invoke(cli, ['config', 'show'])

        assert result.exit_code == 0
        # Verify console was called to print config
        assert mock_console.print.called

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_show_no_config_file(self, mock_console, mock_get_config_file):
        """Test config show when config file doesn't exist"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=False):
            result = runner.invoke(cli, ['config', 'show'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]No configuration file found[/yellow]")

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_set_success(self, mock_console, mock_get_config_file):
        """Test setting a config value"""
        runner = CliRunner()

        mock_config_path = Path("/home/user/.config/goldfish/config.json")
        mock_get_config_file.return_value = mock_config_path

        # Mock file operations
        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"existing": "value"}')):
                with patch('goldfish_cli.config.json.dump'):
                    result = runner.invoke(cli, ['config', 'set', 'api_key', 'new_value'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[green]✓ Set api_key = new_value[/green]")

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_set_creates_file(self, mock_console, mock_get_config_file):
        """Test setting config when file doesn't exist"""
        runner = CliRunner()

        mock_config_path = Path("/home/user/.config/goldfish/config.json")
        mock_get_config_file.return_value = mock_config_path

        # Mock that file doesn't exist initially
        exists_returns = [False, True]  # First check returns False, second returns True
        with patch('goldfish_cli.config.Path.exists', side_effect=exists_returns):
            with patch('goldfish_cli.config.Path.mkdir') as mock_mkdir:
                with patch('goldfish_cli.config.Path.open', mock_open()):
                    with patch('goldfish_cli.config.json.dump'):
                        result = runner.invoke(cli, ['config', 'set', 'api_key', 'value'])

        assert result.exit_code == 0
        mock_mkdir.assert_called_once()

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_get_existing_key(self, mock_console, mock_get_config_file):
        """Test getting an existing config value"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"api_key": "test123"}')):
                result = runner.invoke(cli, ['config', 'get', 'api_key'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("api_key = test123")

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_get_missing_key(self, mock_console, mock_get_config_file):
        """Test getting a non-existent config value"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"other_key": "value"}')):
                result = runner.invoke(cli, ['config', 'get', 'missing_key'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]Key 'missing_key' not found in configuration[/yellow]")

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_delete_existing_key(self, mock_console, mock_get_config_file):
        """Test deleting an existing config key"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"api_key": "test", "other": "value"}')):
                with patch('goldfish_cli.config.json.dump'):
                    result = runner.invoke(cli, ['config', 'delete', 'api_key'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[green]✓ Deleted key 'api_key'[/green]")

    @patch('goldfish_cli.config.get_config_file')
    @patch('goldfish_cli.config.console')
    def test_config_delete_missing_key(self, mock_console, mock_get_config_file):
        """Test deleting a non-existent config key"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/home/user/.config/goldfish/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='{"other": "value"}')):
                result = runner.invoke(cli, ['config', 'delete', 'missing_key'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]Key 'missing_key' not found in configuration[/yellow]")

    @patch('goldfish_cli.config.init_database')
    @patch('goldfish_cli.config.console')
    def test_config_init_database_success(self, mock_console, mock_init_db):
        """Test database initialization"""
        runner = CliRunner()

        mock_init_db.return_value = None  # Success

        result = runner.invoke(cli, ['config', 'init-db'])

        assert result.exit_code == 0
        mock_init_db.assert_called_once()
        mock_console.print.assert_any_call("[green]✓ Database initialized successfully[/green]")

    @patch('goldfish_cli.config.init_database')
    @patch('goldfish_cli.config.console')
    def test_config_init_database_failure(self, mock_console, mock_init_db):
        """Test database initialization failure"""
        runner = CliRunner()

        mock_init_db.side_effect = Exception("Database error")

        result = runner.invoke(cli, ['config', 'init-db'])

        assert result.exit_code != 0
        mock_console.print.assert_any_call("[red]Failed to initialize database: Database error[/red]")

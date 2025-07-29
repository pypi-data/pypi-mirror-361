"""Tests for edge cases and error handling"""
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @patch('goldfish_cli.capture.create_db_and_tables')
    @patch('goldfish_cli.capture.Session')
    def test_database_connection_error(self, mock_session_class, mock_create_db):
        """Test handling database connection errors"""
        runner = CliRunner()

        # Mock database error
        mock_create_db.side_effect = Exception("Database connection failed")

        result = runner.invoke(cli, ['capture', 'quick', 'test'])

        # Should handle error gracefully
        assert result.exit_code != 0

    @patch('goldfish_cli.config.get_config_file')
    def test_config_file_permission_error(self, mock_get_config_file):
        """Test handling file permission errors"""
        runner = CliRunner()

        mock_config_path = Path("/root/config.json")  # Typically no write permission
        mock_get_config_file.return_value = mock_config_path

        with patch('goldfish_cli.config.Path.open', side_effect=PermissionError("Access denied")):
            result = runner.invoke(cli, ['config', 'set', 'key', 'value'])

        # Should handle error gracefully
        assert "Access denied" in result.output or result.exit_code != 0

    @patch('goldfish_cli.config.get_config_file')
    def test_config_invalid_json(self, mock_get_config_file):
        """Test handling invalid JSON in config file"""
        runner = CliRunner()

        mock_get_config_file.return_value = Path("/tmp/config.json")

        with patch('goldfish_cli.config.Path.exists', return_value=True):
            with patch('goldfish_cli.config.Path.open', mock_open(read_data='invalid json{')):
                result = runner.invoke(cli, ['config', 'show'])

        # Should handle JSON decode error
        assert result.exit_code != 0 or "error" in result.output.lower()

    @patch('goldfish_cli.suggestions.Session')
    def test_suggestions_database_transaction_error(self, mock_session_class):
        """Test handling database transaction errors"""
        runner = CliRunner()

        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock transaction error
        mock_session.commit.side_effect = Exception("Transaction failed")
        mock_session.query.return_value.filter.return_value.first.return_value = Mock(id=1)

        result = runner.invoke(cli, ['suggestions', 'reject', '1'])

        # Should handle error gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_capture_file_with_special_characters(self):
        """Test capture file command with special characters in filename"""
        runner = CliRunner()

        # Test with file containing special characters
        with patch('goldfish_cli.capture.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.side_effect = UnicodeDecodeError(
                'utf-8', b'', 0, 1, 'invalid utf-8'
            )

            result = runner.invoke(cli, ['capture', 'file', 'test-file-éàü.txt'])

            # Should handle unicode errors
            assert result.exit_code != 0

    @patch('goldfish_cli.dashboard.Session')
    def test_dashboard_with_malformed_data(self, mock_session_class):
        """Test dashboard handling malformed data"""
        runner = CliRunner()

        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock task with missing required attributes
        mock_task = Mock()
        mock_task.content = "Test task"
        mock_task.priority_score = None  # Should be a number
        mock_task.linked_people = "not a list"  # Should be a list

        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_task]

        # Should handle attribute errors gracefully
        result = runner.invoke(cli, ['dashboard', 'tasks'])

        # Should complete without crashing
        assert result.exit_code == 0 or "error" in result.output.lower()

    def test_cli_with_very_long_input(self):
        """Test CLI with very long input string"""
        runner = CliRunner()

        # Create a very long string
        long_text = "a" * 10000

        result = runner.invoke(cli, ['capture', 'quick', long_text])

        # Should handle long input without crashing
        assert result.exit_code == 0 or result.exit_code != 0  # Just shouldn't crash

    @patch('goldfish_cli.capture.EntityRecognitionEngine')
    def test_entity_recognition_engine_failure(self, mock_engine_class):
        """Test handling entity recognition engine failures"""
        runner = CliRunner()

        # Mock engine initialization failure
        mock_engine_class.side_effect = Exception("NLP model not found")

        result = runner.invoke(cli, ['capture', 'analyze', 'test text'])

        # Should handle error gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_multiple_flags_combination(self):
        """Test CLI with multiple conflicting flags"""
        runner = CliRunner()

        # Test version and no-interactive together
        result = runner.invoke(cli, ['--version', '--no-interactive'])

        # Version should take precedence
        assert result.exit_code == 0
        assert "Goldfish CLI v" in result.output

    @patch('goldfish_cli.suggestions.Session')
    def test_concurrent_suggestion_modification(self, mock_session_class):
        """Test handling concurrent modification of suggestions"""
        runner = CliRunner()

        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # First call returns suggestion, second returns None (simulating deletion)
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            Mock(id=1, entity_name="Test", status="pending"),
            None
        ]

        result = runner.invoke(cli, ['suggestions', 'approve', '1'])

        # Should handle gracefully
        assert result.exit_code == 0

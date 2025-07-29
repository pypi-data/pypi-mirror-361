"""Tests for capture commands"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestCaptureCommands:
    """Test suite for capture commands"""

    def test_capture_quick_with_text(self):
        """Test quick capture with text"""
        runner = CliRunner()

        with patch('goldfish_cli.capture._process_and_store') as mock_process:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note with @sarah'])

            assert result.exit_code == 0
            mock_process.assert_called_once_with('Test note with @sarah', 1)

    def test_capture_quick_with_preview(self):
        """Test quick capture with preview flag"""
        runner = CliRunner()

        with patch('goldfish_cli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note', '--preview'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Test note')

    def test_capture_quick_with_custom_user_id(self):
        """Test quick capture with custom user ID"""
        runner = CliRunner()

        with patch('goldfish_cli.capture._process_and_store') as mock_process:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note', '--user-id', '5'])

            assert result.exit_code == 0
            mock_process.assert_called_once_with('Test note', 5)

    def test_capture_analyze(self):
        """Test analyze command"""
        runner = CliRunner()

        with patch('goldfish_cli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'analyze', 'Meeting with @john'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Meeting with @john')

    @patch('goldfish_cli.capture.create_db_and_tables')
    @patch('goldfish_cli.capture.Session')
    @patch('goldfish_cli.capture.EntityRecognitionEngine')
    @patch('goldfish_cli.capture.SuggestionService')
    @patch('goldfish_cli.capture.console')
    def test_preview_entities_success(self, mock_console, mock_suggestion_service,
                                    mock_engine, mock_session, mock_create_db):
        """Test _preview_entities function with successful entity extraction"""
        from goldfish_cli.capture import _preview_entities

        # Mock entity recognition
        mock_engine_instance = Mock()
        mock_engine_instance.extract_entities.return_value = {
            'people': [{'text': '@sarah', 'start': 10, 'end': 16}],
            'projects': [{'text': '#ai-platform', 'start': 20, 'end': 32}],
            'tasks': [{'content': 'Follow up with sarah', 'priority': 8}]
        }
        mock_engine.return_value = mock_engine_instance

        _preview_entities("Meeting with @sarah about #ai-platform")

        # Verify console output
        assert mock_console.print.called
        # Check that a table was created and printed
        table_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      call[0][0].__class__.__name__ == 'Table']
        assert len(table_calls) > 0

    @patch('goldfish_cli.capture.create_db_and_tables')
    @patch('goldfish_cli.capture.Session')
    @patch('goldfish_cli.capture.EntityRecognitionEngine')
    @patch('goldfish_cli.capture.console')
    def test_preview_entities_no_entities(self, mock_console, mock_engine,
                                         mock_session, mock_create_db):
        """Test _preview_entities with no entities found"""
        from goldfish_cli.capture import _preview_entities

        # Mock entity recognition with no entities
        mock_engine_instance = Mock()
        mock_engine_instance.extract_entities.return_value = {
            'people': [],
            'projects': [],
            'tasks': []
        }
        mock_engine.return_value = mock_engine_instance

        _preview_entities("Simple text with no entities")

        # Verify appropriate message was printed
        mock_console.print.assert_any_call("[yellow]No entities found in the text[/yellow]")

    @patch('goldfish_cli.capture.create_db_and_tables')
    @patch('goldfish_cli.capture.Session')
    @patch('goldfish_cli.capture.User')
    @patch('goldfish_cli.capture.SourceFile')
    @patch('goldfish_cli.capture.Note')
    @patch('goldfish_cli.capture.EntityRecognitionEngine')
    @patch('goldfish_cli.capture.SuggestionService')
    @patch('goldfish_cli.capture.console')
    def test_process_and_store_success(self, mock_console, mock_suggestion_service,
                                     mock_engine, mock_note, mock_source_file,
                                     mock_user, mock_session_class, mock_create_db):
        """Test _process_and_store function with successful processing"""
        from goldfish_cli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user query
        mock_user_obj = Mock(id=1)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user_obj

        # Mock entity recognition
        mock_engine_instance = Mock()
        mock_engine_instance.extract_entities.return_value = {
            'people': [{'text': '@sarah', 'start': 10, 'end': 16}],
            'projects': [],
            'tasks': []
        }
        mock_engine.return_value = mock_engine_instance

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_service_instance.create_suggestions_from_entities.return_value = 1
        mock_suggestion_service.return_value = mock_service_instance

        _process_and_store("Test note with @sarah", 1)

        # Verify database operations
        assert mock_session.add.called
        assert mock_session.commit.called
        mock_console.print.assert_any_call("[green]✓ Created 1 entity suggestions[/green]")

    @patch('goldfish_cli.capture.create_db_and_tables')
    @patch('goldfish_cli.capture.Session')
    @patch('goldfish_cli.capture.console')
    def test_process_and_store_user_not_found(self, mock_console, mock_session_class,
                                             mock_create_db):
        """Test _process_and_store when user is not found"""
        from goldfish_cli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user query to return None
        mock_session.query.return_value.filter.return_value.first.return_value = None

        _process_and_store("Test note", 999)

        # Verify error message
        mock_console.print.assert_any_call("[red]User with ID 999 not found[/red]")

    def test_capture_file_command(self):
        """Test capture file command"""
        runner = CliRunner()

        with patch('goldfish_cli.capture.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.read_text.return_value = "File content"

            with patch('goldfish_cli.capture._process_and_store'):
                result = runner.invoke(cli, ['capture', 'file', 'test.txt'])

                assert result.exit_code == 0

    def test_capture_file_not_found(self):
        """Test capture file command with non-existent file"""
        runner = CliRunner()

        with patch('goldfish_cli.capture.Path') as mock_path:
            mock_path.return_value.exists.return_value = False

            result = runner.invoke(cli, ['capture', 'file', 'nonexistent.txt'])

            assert result.exit_code != 0
            assert "not found" in result.output

    def test_capture_quick_without_text(self):
        """Test quick capture without required text argument"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture', 'quick'])

        assert result.exit_code != 0
        assert "Missing argument" in result.output

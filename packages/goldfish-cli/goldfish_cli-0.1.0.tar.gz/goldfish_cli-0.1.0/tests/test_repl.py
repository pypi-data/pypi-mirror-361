"""Tests for REPL functionality"""
from unittest.mock import MagicMock, Mock, patch

from goldfish_cli.repl import GoldfishREPL


class TestGoldfishREPL:
    """Test REPL main functionality"""

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_initialization(self, mock_console, mock_engine):
        """Test REPL initialization"""
        repl = GoldfishREPL()

        assert repl.user_id == 1
        assert repl.running is True
        assert repl.recognition_engine is not None
        mock_engine.assert_called_once()

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_show_help(self, mock_console, mock_engine):
        """Test help command in REPL"""
        repl = GoldfishREPL()
        repl.show_help()

        # Verify help was printed
        assert mock_console.print.called

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_exit_command(self, mock_console, mock_engine):
        """Test exit command in REPL"""
        repl = GoldfishREPL()
        repl.exit_repl()

        assert repl.running is False
        mock_console.print.assert_called_with("[yellow]Goodbye! 🐠[/yellow]")

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_clear_command(self, mock_console, mock_engine):
        """Test clear command in REPL"""
        repl = GoldfishREPL()
        repl.clear_screen()

        mock_console.clear.assert_called_once()

    @patch('goldfish_cli.repl.create_db_and_tables')
    @patch('goldfish_cli.repl.Session')
    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_show_status(self, mock_console, mock_engine, mock_session_class, mock_create_db):
        """Test status command in REPL"""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        repl = GoldfishREPL()
        repl.show_status()

        # Verify status was printed
        assert mock_console.print.called

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_show_config(self, mock_console, mock_engine):
        """Test config command in REPL"""
        repl = GoldfishREPL()
        repl.show_config()

        # Verify config was printed
        assert mock_console.print.called

    @patch('goldfish_cli.repl.create_db_and_tables')
    @patch('goldfish_cli.repl.Session')
    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_start_interactive(self, mock_console, mock_engine, mock_session_class, mock_create_db):
        """Test REPL start method"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock prompt session
        with patch('goldfish_cli.repl.PromptSession') as mock_prompt_session:
            mock_session_instance = Mock()
            mock_prompt_session.return_value = mock_session_instance

            # Make REPL exit after one iteration
            repl = GoldfishREPL()
            repl.running = False  # Exit immediately

            repl.start()

            # Verify initialization
            mock_prompt_session.assert_called_once()

    @patch('goldfish_cli.repl.create_db_and_tables')
    @patch('goldfish_cli.repl.Session')
    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_capture_text(self, mock_console, mock_engine_class, mock_session_class, mock_create_db):
        """Test capture text functionality"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        mock_engine = Mock()
        mock_engine.extract_entities.return_value = {
            'people': [{'text': '@john', 'start': 0, 'end': 5}],
            'projects': [],
            'tasks': []
        }
        mock_engine_class.return_value = mock_engine

        repl = GoldfishREPL()
        repl.capture_text("Meeting with @john")

        mock_engine.extract_entities.assert_called_once()
        assert mock_console.print.called

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_command_parsing(self, mock_console, mock_engine):
        """Test command parsing in REPL"""
        repl = GoldfishREPL()

        # Test valid command
        repl.process_input("help")
        assert mock_console.print.called

        # Reset mock
        mock_console.reset_mock()

        # Test invalid command
        repl.process_input("invalid_command")
        # Should either show error or treat as text to capture
        assert mock_console.print.called

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_keyboard_interrupt_handling(self, mock_console, mock_engine):
        """Test REPL handles keyboard interrupt gracefully"""
        with patch('goldfish_cli.repl.PromptSession') as mock_prompt_session:
            mock_session_instance = Mock()
            mock_session_instance.prompt.side_effect = KeyboardInterrupt()
            mock_prompt_session.return_value = mock_session_instance

            repl = GoldfishREPL()
            repl.start()

            # Should exit gracefully and print goodbye message
            goodbye_printed = any("Goodbye" in str(call)
                                for call in mock_console.print.call_args_list)
            assert goodbye_printed

    @patch('goldfish_cli.repl.EntityRecognitionEngine')
    @patch('goldfish_cli.repl.console')
    def test_repl_eof_handling(self, mock_console, mock_engine):
        """Test REPL handles EOF gracefully"""
        with patch('goldfish_cli.repl.PromptSession') as mock_prompt_session:
            mock_session_instance = Mock()
            mock_session_instance.prompt.side_effect = EOFError()
            mock_prompt_session.return_value = mock_session_instance

            repl = GoldfishREPL()
            repl.start()

            # Should exit gracefully
            goodbye_printed = any("Goodbye" in str(call)
                                for call in mock_console.print.call_args_list)
            assert goodbye_printed

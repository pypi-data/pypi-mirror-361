"""Tests for suggestions commands"""
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestSuggestionsCommands:
    """Test suite for suggestions commands"""

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_list_with_suggestions(self, mock_console, mock_session_class, mock_create_db):
        """Test listing suggestions when suggestions exist"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestions
        mock_suggestion1 = Mock(
            id=1,
            entity_type='person',
            entity_name='Sarah Johnson',
            context='Meeting with @sarah',
            confidence=0.9,
            status='pending',
            created_at=datetime.now()
        )
        mock_suggestion2 = Mock(
            id=2,
            entity_type='project',
            entity_name='AI Platform',
            context='Working on #ai-platform',
            confidence=0.95,
            status='pending',
            created_at=datetime.now()
        )

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_suggestion1, mock_suggestion2
        ]

        result = runner.invoke(cli, ['suggestions', 'list'])

        assert result.exit_code == 0
        # Verify that a table was printed
        assert mock_console.print.called

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_list_empty(self, mock_console, mock_session_class, mock_create_db):
        """Test listing suggestions when no suggestions exist"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock empty suggestions
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        result = runner.invoke(cli, ['suggestions', 'list'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]No pending suggestions found[/yellow]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_list_with_type_filter(self, mock_console, mock_session_class, mock_create_db):
        """Test listing suggestions with type filter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        result = runner.invoke(cli, ['suggestions', 'list', '--type', 'person'])

        assert result.exit_code == 0
        # Verify filter was applied
        mock_session.query.return_value.filter.assert_called()

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.SuggestionService')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_approve_success(self, mock_console, mock_service_class,
                                       mock_session_class, mock_create_db):
        """Test approving a suggestion successfully"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.approve_suggestion.return_value = (True, Mock(entity_name='Sarah Johnson'))
        mock_service_class.return_value = mock_service

        result = runner.invoke(cli, ['suggestions', 'approve', '1'])

        assert result.exit_code == 0
        mock_service.approve_suggestion.assert_called_once_with(1)
        mock_console.print.assert_any_call("[green]✓ Approved suggestion: Created entity 'Sarah Johnson'[/green]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.SuggestionService')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_approve_not_found(self, mock_console, mock_service_class,
                                         mock_session_class, mock_create_db):
        """Test approving a non-existent suggestion"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        mock_service = Mock()
        mock_service.approve_suggestion.return_value = (False, None)
        mock_service_class.return_value = mock_service

        result = runner.invoke(cli, ['suggestions', 'approve', '999'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[red]Suggestion not found or already processed[/red]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_reject_success(self, mock_console, mock_session_class, mock_create_db):
        """Test rejecting a suggestion successfully"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock finding the suggestion
        mock_suggestion = Mock(id=1, entity_name='Test Entity', status='pending')
        mock_session.query.return_value.filter.return_value.first.return_value = mock_suggestion

        result = runner.invoke(cli, ['suggestions', 'reject', '1'])

        assert result.exit_code == 0
        assert mock_suggestion.status == 'rejected'
        mock_session.commit.assert_called_once()
        mock_console.print.assert_any_call("[yellow]✗ Rejected suggestion: 'Test Entity'[/yellow]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_reject_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test rejecting a non-existent suggestion"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock not finding the suggestion
        mock_session.query.return_value.filter.return_value.first.return_value = None

        result = runner.invoke(cli, ['suggestions', 'reject', '999'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[red]Suggestion not found or already processed[/red]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.SuggestionService')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_approve_all_confirmed(self, mock_console, mock_service_class,
                                             mock_session_class, mock_create_db):
        """Test approving all suggestions with confirmation"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestions
        mock_suggestions = [Mock(id=1), Mock(id=2)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_suggestions

        mock_service = Mock()
        mock_service.approve_suggestion.side_effect = [
            (True, Mock(entity_name='Entity 1')),
            (True, Mock(entity_name='Entity 2'))
        ]
        mock_service_class.return_value = mock_service

        # Simulate user confirming
        result = runner.invoke(cli, ['suggestions', 'approve-all'], input='y\n')

        assert result.exit_code == 0
        assert mock_service.approve_suggestion.call_count == 2
        mock_console.print.assert_any_call("[green]✓ Approved 2 suggestions[/green]")

    @patch('goldfish_cli.suggestions.create_db_and_tables')
    @patch('goldfish_cli.suggestions.Session')
    @patch('goldfish_cli.suggestions.console')
    def test_suggestions_approve_all_cancelled(self, mock_console, mock_session_class, mock_create_db):
        """Test cancelling approve all suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestions
        mock_suggestions = [Mock(id=1), Mock(id=2)]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_suggestions

        # Simulate user cancelling
        result = runner.invoke(cli, ['suggestions', 'approve-all'], input='n\n')

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]Cancelled[/yellow]")

    def test_suggestions_invalid_id(self):
        """Test suggestions commands with invalid ID"""
        runner = CliRunner()

        result = runner.invoke(cli, ['suggestions', 'approve', 'not-a-number'])

        assert result.exit_code != 0
        assert "Invalid value" in result.output

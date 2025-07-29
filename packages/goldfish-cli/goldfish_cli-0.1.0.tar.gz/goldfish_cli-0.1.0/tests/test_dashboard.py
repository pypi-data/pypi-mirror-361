"""Tests for dashboard commands"""
from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from goldfish_cli.main import cli


class TestDashboardCommands:
    """Test suite for dashboard commands"""

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_tasks_with_tasks(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard tasks command with existing tasks"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock tasks
        mock_task1 = Mock(
            id=1,
            content='Complete documentation',
            priority_score=9,
            status='pending',
            due_date=datetime.now() + timedelta(days=1),
            created_at=datetime.now(),
            linked_people=[Mock(name='John Doe')],
            linked_projects=[Mock(name='AI Platform')]
        )
        mock_task2 = Mock(
            id=2,
            content='Review code',
            priority_score=7,
            status='in_progress',
            due_date=None,
            created_at=datetime.now(),
            linked_people=[],
            linked_projects=[]
        )

        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_task1, mock_task2
        ]

        result = runner.invoke(cli, ['dashboard', 'tasks'])

        assert result.exit_code == 0
        # Verify console printed output
        assert mock_console.print.called

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_tasks_empty(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard tasks command with no tasks"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock empty tasks
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = runner.invoke(cli, ['dashboard', 'tasks'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]No tasks found[/yellow]")

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_tasks_with_status_filter(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard tasks with status filter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        result = runner.invoke(cli, ['dashboard', 'tasks', '--status', 'pending'])

        assert result.exit_code == 0
        # Verify filter was applied
        mock_session.query.return_value.filter.assert_called()

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_entities_with_data(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command with existing entities"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock entities
        mock_person1 = Mock(
            id=1,
            name='Sarah Johnson',
            importance_score=8,
            created_at=datetime.now()
        )
        mock_person2 = Mock(
            id=2,
            name='John Doe',
            importance_score=6,
            created_at=datetime.now()
        )
        mock_project1 = Mock(
            id=1,
            name='AI Platform',
            status='active',
            deadline=datetime.now() + timedelta(days=30),
            created_at=datetime.now()
        )

        # Mock query results
        people_query = MagicMock()
        people_query.order_by.return_value.limit.return_value.all.return_value = [mock_person1, mock_person2]

        projects_query = MagicMock()
        projects_query.order_by.return_value.limit.return_value.all.return_value = [mock_project1]

        # Setup query routing
        def query_side_effect(model):
            if model.__name__ == 'Person':
                return people_query
            elif model.__name__ == 'Project':
                return projects_query
            return MagicMock()

        mock_session.query.side_effect = query_side_effect

        result = runner.invoke(cli, ['dashboard', 'entities'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_entities_empty(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command with no entities"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock empty results
        mock_query = MagicMock()
        mock_query.order_by.return_value.limit.return_value.all.return_value = []
        mock_session.query.return_value = mock_query

        result = runner.invoke(cli, ['dashboard', 'entities'])

        assert result.exit_code == 0
        # Should print empty message for both people and projects
        assert mock_console.print.call_count >= 2

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_stats(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard stats command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock count queries
        mock_session.query.return_value.count.side_effect = [
            10,  # Total tasks
            7,   # Pending tasks
            3,   # Completed tasks
            5,   # Total notes
            15,  # Total people
            8,   # Total projects
            25   # Pending suggestions
        ]

        result = runner.invoke(cli, ['dashboard', 'stats'])

        assert result.exit_code == 0
        # Verify stats panel was printed
        assert mock_console.print.called
        # Should have printed a panel with stats
        panel_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      'Panel' in str(call[0][0].__class__)]
        assert len(panel_calls) > 0

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_recent_notes(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard recent command with notes"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock recent notes
        mock_note1 = Mock(
            id=1,
            content='Meeting notes about project planning',
            created_at=datetime.now() - timedelta(hours=1),
            source_file=Mock(path='/notes/meeting.md'),
            linked_people=[Mock(name='Sarah')],
            linked_projects=[Mock(name='Q1 Planning')]
        )
        mock_note2 = Mock(
            id=2,
            content='Ideas for new features',
            created_at=datetime.now() - timedelta(hours=3),
            source_file=None,
            linked_people=[],
            linked_projects=[]
        )

        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_note1, mock_note2
        ]

        result = runner.invoke(cli, ['dashboard', 'recent'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_recent_empty(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard recent command with no notes"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock empty notes
        mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []

        result = runner.invoke(cli, ['dashboard', 'recent'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("[yellow]No recent notes found[/yellow]")

    @patch('goldfish_cli.dashboard.create_db_and_tables')
    @patch('goldfish_cli.dashboard.Session')
    @patch('goldfish_cli.dashboard.console')
    def test_dashboard_recent_with_days_filter(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard recent command with days filter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        result = runner.invoke(cli, ['dashboard', 'recent', '--days', '3'])

        assert result.exit_code == 0
        # Verify filter was applied
        mock_session.query.return_value.filter.assert_called()

    def test_dashboard_help(self):
        """Test dashboard help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard', '--help'])

        assert result.exit_code == 0
        assert "View tasks, entities, and status" in result.output

"""Tests for dashboard commands"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestDashboardCommands:
    """Test suite for dashboard commands"""

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_status_success(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard status command with mocked user"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock database exec calls to return simple values
        mock_session.exec.return_value.one.return_value = 5
        mock_session.exec.return_value.first.return_value = None

        result = runner.invoke(cli, ['dashboard', 'status'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_status_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard status command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['dashboard', 'status'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ User with ID 1 not found. Run: goldfish config setup")

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_entities_success(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock exec calls
        mock_session.exec.return_value.all.return_value = []

        result = runner.invoke(cli, ['dashboard', 'entities'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_entities_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['dashboard', 'entities'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ User with ID 1 not found")

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_notes_success(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard notes command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock exec calls
        mock_session.exec.return_value.all.return_value = []

        result = runner.invoke(cli, ['dashboard', 'notes'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_notes_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard notes command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['dashboard', 'notes'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ User with ID 1 not found")

    def test_dashboard_help(self):
        """Test dashboard help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['dashboard', '--help'])

        assert result.exit_code == 0
        assert "View tasks, entities, and status" in result.output

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_status_with_pending_suggestions(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard status when there are pending suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock _get_user_stats to return stats with pending suggestions
        with patch('gfcli.dashboard._get_user_stats') as mock_get_stats:
            mock_get_stats.return_value = {
                'notes': 5,
                'total_chars': 1000,
                'latest_note': '2024-01-01',
                'pending_suggestions': 3,  # > 0 to trigger the if branch
                'confirmed_entities': 10,
                'accuracy_rate': 95.5,
                'people': 2,
                'projects': 1,
                'topics': 1
            }

            result = runner.invoke(cli, ['dashboard', 'status'])

            assert result.exit_code == 0
            assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_status_no_pending_suggestions(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard status when there are no pending suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock _get_user_stats to return stats with no pending suggestions
        with patch('gfcli.dashboard._get_user_stats') as mock_get_stats:
            mock_get_stats.return_value = {
                'notes': 5,
                'total_chars': 1000,
                'latest_note': '2024-01-01',
                'pending_suggestions': 0,  # = 0 to trigger the else branch
                'confirmed_entities': 10,
                'accuracy_rate': 95.5,
                'people': 2,
                'projects': 1,
                'topics': 1
            }

            result = runner.invoke(cli, ['dashboard', 'status'])

            assert result.exit_code == 0
            assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_entities_with_type_filter(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command with type filter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock _show_entities_by_type function
        with patch('gfcli.dashboard._show_entities_by_type') as mock_show_by_type:
            result = runner.invoke(cli, ['dashboard', 'entities', '--type', 'people'])

            assert result.exit_code == 0
            mock_show_by_type.assert_called_once_with(mock_session, 1, 'people')

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_entities_all_types(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard entities command without type filter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock _show_all_entities function
        with patch('gfcli.dashboard._show_all_entities') as mock_show_all:
            result = runner.invoke(cli, ['dashboard', 'entities'])

            assert result.exit_code == 0
            mock_show_all.assert_called_once_with(mock_session, 1)

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_notes_with_data(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard notes command with existing notes"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock notes
        mock_note1 = Mock()
        mock_note1.id = 1
        mock_note1.content = "This is a test note content that should be truncated"
        mock_note1.created_at = Mock()
        mock_note1.created_at.strftime.return_value = "2024-01-01 12:00"
        mock_note1.processing_metadata = {'source': 'cli'}

        mock_note2 = Mock()
        mock_note2.id = 2
        mock_note2.content = "Short note"
        mock_note2.created_at = Mock()
        mock_note2.created_at.strftime.return_value = "2024-01-02 13:00"
        mock_note2.processing_metadata = None

        mock_session.exec.return_value.all.return_value = [mock_note1, mock_note2]

        result = runner.invoke(cli, ['dashboard', 'notes', '--limit', '5'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    @patch('gfcli.dashboard.console')
    def test_dashboard_notes_empty(self, mock_console, mock_session_class, mock_create_db):
        """Test dashboard notes command with no notes"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock empty notes
        mock_session.exec.return_value.all.return_value = []

        result = runner.invoke(cli, ['dashboard', 'notes'])

        assert result.exit_code == 0
        assert mock_console.print.called

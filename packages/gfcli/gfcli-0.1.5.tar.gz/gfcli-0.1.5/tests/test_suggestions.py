"""Tests for suggestions commands"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestSuggestionsCommands:
    """Test suite for suggestions commands"""

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    def test_suggestions_pending_with_suggestions(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions pending command with existing suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock suggestions
        mock_suggestion1 = Mock()
        mock_suggestion1.id = 1
        mock_suggestion1.name = "Sarah Johnson"
        mock_suggestion1.entity_type = "person"
        mock_suggestion1.confidence = 0.9
        mock_suggestion1.context = "Meeting with @sarah"
        mock_suggestion1.created_at = Mock()
        mock_suggestion1.created_at.strftime.return_value = "2024-01-01 12:00:00"

        mock_suggestion2 = Mock()
        mock_suggestion2.id = 2
        mock_suggestion2.name = "AI Platform"
        mock_suggestion2.entity_type = "project"
        mock_suggestion2.confidence = 0.85
        mock_suggestion2.context = "Working on #ai-platform"
        mock_suggestion2.created_at = Mock()
        mock_suggestion2.created_at.strftime.return_value = "2024-01-01 12:00:00"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion1, mock_suggestion2]

        result = runner.invoke(cli, ['suggestions', 'pending'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    def test_suggestions_pending_empty(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions pending command with no suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock empty suggestions
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = []

        result = runner.invoke(cli, ['suggestions', 'pending'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    def test_suggestions_pending_with_limit(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions pending command with limit parameter"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock suggestions
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = []

        result = runner.invoke(cli, ['suggestions', 'pending', '--limit', '5'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    def test_suggestions_pending_user_not_found(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions pending command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found - service returns empty list
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = []

        result = runner.invoke(cli, ['suggestions', 'pending'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt.ask')
    @patch('gfcli.suggestions.SuggestionService')
    def test_suggestions_review_success(self, mock_suggestion_service, mock_prompt, mock_console, mock_session_class, mock_create_db):
        """Test suggestions review command with existing suggestion"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 1
        mock_suggestion.name = "Sarah Johnson"
        mock_suggestion.entity_type = "person"
        mock_suggestion.confidence = 0.9
        mock_suggestion.context = "Meeting with @sarah"
        mock_suggestion.ai_metadata = {'original_text': '@sarah'}

        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock user prompt to skip
        mock_prompt.return_value = "skip"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance

        result = runner.invoke(cli, ['suggestions', 'review', '1'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    def test_suggestions_review_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test suggestions review command with non-existent suggestion"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock suggestion not found
        mock_session.exec.return_value.first.return_value = None

        result = runner.invoke(cli, ['suggestions', 'review', '999'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.SuggestionService')
    def test_suggestions_review_user_not_found(self, mock_suggestion_service, mock_console, mock_session_class, mock_create_db):
        """Test suggestions review command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion not found (this is how the command handles user not found)
        mock_session.exec.return_value.first.return_value = None

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance

        result = runner.invoke(cli, ['suggestions', 'review', '1'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    def test_suggestions_verify_all_success(self, mock_console, mock_session_class, mock_create_db):
        """Test suggestions verify-all command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock suggestions
        mock_session.exec.return_value.all.return_value = []

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    def test_suggestions_verify_all_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test suggestions verify-all command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.SuggestionService')
    def test_suggestions_note_success(self, mock_suggestion_service, mock_console, mock_session_class, mock_create_db):
        """Test suggestions note command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_suggestions_by_note.return_value = []
        mock_service_instance.get_confirmation_status.return_value = {
            'total_suggestions': 0,
            'confirmed': 0,
            'rejected': 0,
            'pending': 0,
            'completion_percentage': 0.0
        }

        result = runner.invoke(cli, ['suggestions', 'note', '1'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.SuggestionService')
    def test_suggestions_note_not_found(self, mock_suggestion_service, mock_console, mock_session_class, mock_create_db):
        """Test suggestions note command with non-existent note"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion service returning empty list (note not found)
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_suggestions_by_note.return_value = []

        result = runner.invoke(cli, ['suggestions', 'note', '999'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.SuggestionService')
    def test_suggestions_note_user_not_found(self, mock_suggestion_service, mock_console, mock_session_class, mock_create_db):
        """Test suggestions note command with user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion service returning empty list (user not found)
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_suggestions_by_note.return_value = []

        result = runner.invoke(cli, ['suggestions', 'note', '1'])

        assert result.exit_code == 0
        assert mock_console.print.called

    def test_suggestions_help(self):
        """Test suggestions help command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions', '--help'])

        assert result.exit_code == 0
        assert "Manage AI entity suggestions" in result.output

    def test_suggestions_invalid_command(self):
        """Test suggestions with invalid command"""
        runner = CliRunner()
        result = runner.invoke(cli, ['suggestions', 'invalid-command'])

        assert result.exit_code != 0
        assert "No such command" in result.output

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_suggestions_review_interactive_create_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with interactive create choice"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.confirm_suggestion.return_value = 456

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    @patch('gfcli.suggestions._handle_entity_linking')
    def test_suggestions_review_interactive_link_choice(self, mock_handle_linking, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with interactive link choice"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance

        # Mock user chooses "link"
        mock_prompt.ask.return_value = "link"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_handle_linking.assert_called_once_with(mock_suggestion, mock_service_instance, 1)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_suggestions_review_interactive_reject_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with interactive reject choice"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_service_instance.reject_suggestion.assert_called_once_with(123, 1)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_suggestions_review_interactive_skip_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with interactive skip choice"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance

        # Mock user chooses "skip"
        mock_prompt.ask.return_value = "skip"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("⏭️  Skipped suggestion")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_suggestions_review_create_choice_error(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with create choice but service error"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Error creating entity: Database error")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_suggestions_review_reject_choice_error(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test suggestions review with reject choice but service error"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85

        # Mock db.exec().first() to return suggestion
        mock_session.exec.return_value.first.return_value = mock_suggestion

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.reject_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        result = runner.invoke(cli, ['suggestions', 'review', '123'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Error rejecting suggestion: Database error")

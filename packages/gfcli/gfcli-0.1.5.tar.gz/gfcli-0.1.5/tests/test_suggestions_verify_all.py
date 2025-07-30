"""Tests for suggestions verify_all function"""
from unittest.mock import Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestSuggestionsVerifyAll:
    """Test suggestions verify_all command"""

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_auto_confirm_high_confidence(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with auto-confirm high confidence suggestions"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock high confidence suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.95  # High confidence

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]
        mock_service_instance.confirm_suggestion.return_value = 456

        result = runner.invoke(cli, ['suggestions', 'verify-all', '--auto-confirm-high'])

        assert result.exit_code == 0
        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        # Should not show details for auto-confirmed suggestions
        mock_show_details.assert_not_called()

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_auto_confirm_fails(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with auto-confirm high confidence but service fails"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock high confidence suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.95  # High confidence

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]
        mock_service_instance.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user interaction after auto-confirm fails
        mock_prompt.ask.return_value = "skip"

        result = runner.invoke(cli, ['suggestions', 'verify-all', '--auto-confirm-high'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Auto-confirm failed: Database error")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_interactive_create_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive create choice"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]
        mock_service_instance.confirm_suggestion.return_value = 456

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_show_details.assert_called_once_with(mock_suggestion)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    @patch('gfcli.suggestions._handle_entity_linking')
    def test_verify_all_interactive_link_choice_success(self, mock_handle_linking, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive link choice that succeeds"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]

        # Mock user chooses "link" and linking succeeds
        mock_prompt.ask.return_value = "link"
        mock_handle_linking.return_value = True

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_handle_linking.assert_called_once_with(mock_suggestion, mock_service_instance, 1)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    @patch('gfcli.suggestions._handle_entity_linking')
    def test_verify_all_interactive_link_choice_fails(self, mock_handle_linking, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive link choice that fails"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]

        # Mock user chooses "link" and linking fails
        mock_prompt.ask.return_value = "link"
        mock_handle_linking.return_value = False

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_handle_linking.assert_called_once_with(mock_suggestion, mock_service_instance, 1)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_interactive_reject_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive reject choice"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_service_instance.reject_suggestion.assert_called_once_with(123, 1)

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_interactive_skip_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive skip choice"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]

        # Mock user chooses "skip"
        mock_prompt.ask.return_value = "skip"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("⏭️  Skipped")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_interactive_quit_choice(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with interactive quit choice"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]

        # Mock user chooses "quit"
        mock_prompt.ask.return_value = "quit"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("🛑 Stopping verification process")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_create_choice_error(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with create choice but service error"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]
        mock_service_instance.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Error: Database error")

    @patch('gfcli.suggestions.create_db_and_tables')
    @patch('gfcli.suggestions.Session')
    @patch('gfcli.suggestions.SuggestionService')
    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions._show_suggestion_details')
    def test_verify_all_reject_choice_error(self, mock_show_details, mock_prompt, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test verify_all with reject choice but service error"""
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

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = [mock_suggestion]
        mock_service_instance.reject_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        result = runner.invoke(cli, ['suggestions', 'verify-all'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Error: Database error")

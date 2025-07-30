"""Advanced tests for REPL functionality"""
from datetime import datetime
from unittest.mock import Mock, patch

from gfcli.repl import GoldfishREPL


class TestREPLAdvanced:
    """Test advanced REPL functionality"""

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_first_time_setup_new_user(self, mock_console, mock_session_class, mock_create_db):
        """Test first time setup creating new user"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock no existing user found
        mock_session.exec.return_value.first.return_value = None

        # Mock user creation
        mock_user = Mock()
        mock_user.id = 123
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.return_value = None

        with patch('gfcli.repl.Prompt') as mock_prompt:
            with patch('goldfish_backend.core.auth.validate_password_strength', return_value=True):
                with patch('goldfish_backend.core.auth.get_password_hash', return_value="hashed_pass"):
                    with patch('gfcli.repl.User') as mock_user_class:
                        with patch('sqlmodel.select') as mock_select:
                            mock_user_class.return_value = mock_user
                            mock_select.return_value.where.return_value = Mock()

                            # Mock user inputs
                            mock_prompt.ask.side_effect = [
                                "test@example.com",  # email
                                "Test User",         # full name
                                "ValidPass123!",     # password
                                "Test bio"           # bio
                            ]

                            repl._first_time_setup()

        assert repl.user == mock_user
        assert repl.user_id == 123
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_first_time_setup_existing_user(self, mock_console, mock_session_class, mock_create_db):
        """Test first time setup with existing user"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing user found
        mock_existing_user = Mock()
        mock_existing_user.id = 456
        mock_existing_user.email = "test@example.com"
        mock_session.exec.return_value.first.return_value = mock_existing_user

        with patch('gfcli.repl.Prompt') as mock_prompt:
            with patch('goldfish_backend.core.auth.validate_password_strength', return_value=True):
                with patch('goldfish_backend.core.auth.get_password_hash', return_value="hashed_pass"):
                    with patch('sqlmodel.select') as mock_select:
                        mock_select.return_value.where.return_value = Mock()

                        # Mock user inputs
                        mock_prompt.ask.side_effect = [
                            "test@example.com",  # email
                            "Test User",         # full name
                            "ValidPass123!",     # password
                            "Test bio"           # bio
                        ]

                        repl._first_time_setup()

        assert repl.user == mock_existing_user
        assert repl.user_id == 456
        mock_console.print.assert_any_call("❌ User with email test@example.com already exists!")

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_first_time_setup_password_validation(self, mock_console, mock_session_class, mock_create_db):
        """Test first time setup with password validation failure"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.first.return_value = None

        # Mock user creation
        mock_user = Mock()
        mock_user.id = 123
        mock_session.add.return_value = None
        mock_session.commit.return_value = None

        with patch('gfcli.repl.Prompt') as mock_prompt:
            with patch('gfcli.repl.validate_password_strength') as mock_validate:
                with patch('gfcli.repl.get_password_hash', return_value="hashed_pass"):
                    with patch('gfcli.repl.User') as mock_user_class:
                        with patch('sqlmodel.select') as mock_select:
                            mock_user_class.return_value = mock_user
                            mock_select.return_value.where.return_value = Mock()

                            # Mock password validation: first fails, second succeeds
                            mock_validate.side_effect = [False, True]

                            # Mock user inputs
                            mock_prompt.ask.side_effect = [
                                "test@example.com",  # email
                                "Test User",         # full name
                                "weak",              # invalid password
                                "ValidPass123!",     # valid password
                                "Test bio"           # bio
                            ]

                            repl._first_time_setup()

        mock_console.print.assert_any_call("❌ Password must be at least 8 characters with uppercase, lowercase, digit, and special character")

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_check_pending_suggestions_with_suggestions_review_yes(self, mock_confirm, mock_console, mock_suggestion_service, mock_session_class):
        """Test _check_pending_suggestions with suggestions and user chooses to review"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestions
        mock_suggestions = [Mock(), Mock()]
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = mock_suggestions

        # Mock user confirms review
        mock_confirm.ask.return_value = True

        with patch.object(repl, '_verify_suggestions') as mock_verify:
            repl._check_pending_suggestions()

        mock_console.print.assert_any_call(f"\n🔔 You have {len(mock_suggestions)} pending entity suggestions")
        mock_verify.assert_called_once_with(mock_suggestions, mock_session)

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_check_pending_suggestions_with_suggestions_review_no(self, mock_confirm, mock_console, mock_suggestion_service, mock_session_class):
        """Test _check_pending_suggestions with suggestions and user declines to review"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock suggestions
        mock_suggestions = [Mock(), Mock()]
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = mock_suggestions

        # Mock user declines review
        mock_confirm.ask.return_value = False

        with patch.object(repl, '_verify_suggestions') as mock_verify:
            repl._check_pending_suggestions()

        mock_console.print.assert_any_call(f"\n🔔 You have {len(mock_suggestions)} pending entity suggestions")
        mock_verify.assert_not_called()

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    def test_check_pending_suggestions_no_suggestions(self, mock_suggestion_service, mock_session_class):
        """Test _check_pending_suggestions with no suggestions"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock no suggestions
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.get_pending_suggestions.return_value = []

        with patch.object(repl, '_verify_suggestions') as mock_verify:
            repl._check_pending_suggestions()

        mock_verify.assert_not_called()

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_capture_text_with_entities_save_yes(self, mock_confirm, mock_console, mock_engine_class):
        """Test _capture_text with entities found and user chooses to save"""
        repl = GoldfishREPL()

        # Mock entity recognition
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_result = {
            'total_entities': 2,
            'total_tasks': 1,
            'entities': {
                'people': [Mock(name='John', confidence=0.9, context='Meeting with John')],
                'projects': [Mock(name='AI Project', confidence=0.95, context='about AI Project')]
            },
            'tasks': [Mock(content='Follow up with John', confidence=0.8)]
        }
        mock_engine.process_text.return_value = mock_result

        # Mock user confirms save
        mock_confirm.ask.return_value = True

        with patch.object(repl, '_show_analysis_results') as mock_show:
            with patch.object(repl, '_save_capture') as mock_save:
                repl._capture_text("Meeting with John about AI Project")

        mock_show.assert_called_once_with(mock_result, "Meeting with John about AI Project")
        mock_save.assert_called_once_with("Meeting with John about AI Project", mock_result)

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_capture_text_with_entities_save_no(self, mock_confirm, mock_console, mock_engine_class):
        """Test _capture_text with entities found and user chooses not to save"""
        repl = GoldfishREPL()

        # Mock entity recognition
        mock_engine = Mock()
        mock_engine_class.return_value = mock_engine
        mock_result = {
            'total_entities': 1,
            'total_tasks': 0,
            'entities': {'people': [Mock()]},
            'tasks': []
        }
        mock_engine.process_text.return_value = mock_result

        # Mock user declines save
        mock_confirm.ask.return_value = False

        with patch.object(repl, '_show_analysis_results') as mock_show:
            with patch.object(repl, '_save_capture') as mock_save:
                repl._capture_text("Simple text")

        mock_show.assert_called_once()
        mock_save.assert_not_called()

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_capture_text_no_entities_save_simple_yes(self, mock_confirm, mock_console):
        """Test _capture_text with no entities and user chooses to save simple note"""
        repl = GoldfishREPL()

        # Mock entity recognition with no entities
        mock_result = {
            'total_entities': 0,
            'total_tasks': 0,
            'entities': {'people': [], 'projects': [], 'topics': []},
            'tasks': []
        }
        repl.recognition_engine.process_text.return_value = mock_result

        # Mock user confirms simple save
        mock_confirm.ask.return_value = True

        with patch.object(repl, '_save_simple_note') as mock_save_simple:
            repl._capture_text("Simple note")

        mock_save_simple.assert_called_once_with("Simple note")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_capture_text_no_entities_save_simple_no(self, mock_confirm, mock_console):
        """Test _capture_text with no entities and user chooses not to save"""
        repl = GoldfishREPL()

        # Mock entity recognition with no entities
        mock_result = {
            'total_entities': 0,
            'total_tasks': 0,
            'entities': {'people': [], 'projects': [], 'topics': []},
            'tasks': []
        }
        repl.recognition_engine.process_text.return_value = mock_result

        # Mock user declines simple save
        mock_confirm.ask.return_value = False

        with patch.object(repl, '_save_simple_note') as mock_save_simple:
            repl._capture_text("Simple note")

        mock_save_simple.assert_not_called()

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Columns')
    def test_show_analysis_results_with_entities_and_tasks(self, mock_columns, mock_console):
        """Test _show_analysis_results with entities and tasks"""
        repl = GoldfishREPL()

        # Mock result with entities and tasks
        result = {
            'total_entities': 2,
            'total_tasks': 1,
            'entities': {
                'people': [Mock(name='John', confidence=0.9)],
                'projects': [Mock(name='AI Project', confidence=0.95)],
                'topics': []
            },
            'tasks': [Mock(content='Follow up with the AI Project timeline', confidence=0.8)]
        }

        repl._show_analysis_results(result, "text")

        # Should create columns with panels
        mock_columns.assert_called_once()
        mock_console.print.assert_called()

    @patch('gfcli.repl.console')
    def test_show_analysis_results_no_entities_or_tasks(self, mock_console):
        """Test _show_analysis_results with no entities or tasks"""
        repl = GoldfishREPL()

        # Mock result with no entities or tasks
        result = {
            'total_entities': 0,
            'total_tasks': 0,
            'entities': {'people': [], 'projects': [], 'topics': []},
            'tasks': []
        }

        with patch('gfcli.repl.Columns') as mock_columns:
            repl._show_analysis_results(result, "text")

        # Should not create columns
        mock_columns.assert_not_called()

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_save_simple_note(self, mock_console, mock_session_class):
        """Test _save_simple_note functionality"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock source file
        mock_source_file = Mock(id=123)

        # Mock note
        mock_note = Mock(id=456)

        with patch.object(repl, '_get_or_create_quick_capture_file', return_value=mock_source_file):
            with patch('gfcli.repl.Note') as mock_note_class:
                mock_note_class.return_value = mock_note

                repl._save_simple_note("Simple note content")

        mock_session.add.assert_called_once_with(mock_note)
        mock_session.commit.assert_called_once()
        mock_console.print.assert_called_with("✅ Note saved! (#456)")

    @patch('gfcli.repl.console')
    def test_show_welcome(self, mock_console):
        """Test _show_welcome functionality"""
        repl = GoldfishREPL()

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        repl.user = mock_user

        repl._show_welcome()

        # Should print welcome panel
        assert mock_console.print.called
        # Check that a panel was created and printed
        panel_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      'Panel' in str(call[0][0].__class__)]
        assert len(panel_calls) > 0

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_show_notes_with_notes(self, mock_console, mock_session_class):
        """Test show_notes with existing notes"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock notes
        mock_note1 = Mock()
        mock_note1.id = 1
        mock_note1.content = "First note content"
        mock_note1.created_at = datetime(2024, 1, 1, 12, 0, 0)

        mock_note2 = Mock()
        mock_note2.id = 2
        mock_note2.content = "Second note with very long content that should be truncated in the display"
        mock_note2.created_at = datetime(2024, 1, 2, 14, 30, 0)

        mock_session.exec.return_value.all.return_value = [mock_note1, mock_note2]

        with patch('gfcli.repl.Table') as mock_table:
            mock_table_instance = Mock()
            mock_table.return_value = mock_table_instance

            repl.show_notes()

        # Should print table with notes
        mock_console.print.assert_called_with(mock_table_instance)

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_show_notes_no_notes(self, mock_console, mock_session_class):
        """Test show_notes with no notes"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.exec.return_value.all.return_value = []

        repl.show_notes()

        mock_console.print.assert_called_with("📝 No notes yet. Start typing to capture your first thought!")

    @patch('gfcli.repl.Session')
    def test_get_or_create_quick_capture_file_existing(self, mock_session_class):
        """Test _get_or_create_quick_capture_file with existing file"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_existing_file = Mock(id=123)
        mock_session.exec.return_value.first.return_value = mock_existing_file

        result = repl._get_or_create_quick_capture_file(1, mock_session)

        assert result == mock_existing_file
        mock_session.add.assert_not_called()
        mock_session.flush.assert_not_called()

    @patch('gfcli.repl.Session')
    def test_get_or_create_quick_capture_file_new(self, mock_session_class):
        """Test _get_or_create_quick_capture_file creating new file"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session.exec.return_value.first.return_value = None

        with patch('gfcli.repl.SourceFile') as mock_source_file_class:
            with patch('sqlmodel.select') as mock_select:
                mock_new_file = Mock()
                mock_source_file_class.return_value = mock_new_file
                mock_select.return_value = Mock()  # Mock select statement

                result = repl._get_or_create_quick_capture_file(1, mock_session)

        assert result == mock_new_file
        mock_session.add.assert_called_once_with(mock_new_file)
        mock_session.flush.assert_called_once()

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_show_entities(self, mock_console, mock_session_class):
        """Test show_entities method"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        with patch('gfcli.repl.dashboard') as mock_dashboard:
            with patch.object(mock_dashboard, '_show_all_entities') as mock_show_all:
                repl.show_entities()

        mock_show_all.assert_called_once_with(mock_session, 1)

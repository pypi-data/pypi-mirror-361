"""Tests for REPL verification workflows"""
from unittest.mock import Mock, patch

from gfcli.repl import GoldfishREPL


class TestREPLVerification:
    """Test REPL suggestion verification workflows"""

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_save_capture_with_suggestions_verify_yes(self, mock_confirm, mock_console, mock_suggestion_service, mock_session_class):
        """Test _save_capture with suggestions and user chooses to verify"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock source file
        mock_source_file = Mock(id=123)

        # Mock note
        mock_note = Mock(id=456)

        # Mock suggestions
        mock_suggestions = [Mock(), Mock()]
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.create_suggestions_from_text.return_value = mock_suggestions

        # Mock user confirms verification
        mock_confirm.ask.return_value = True

        mock_result = {'entities': {}, 'tasks': []}

        with patch.object(repl, '_get_or_create_quick_capture_file', return_value=mock_source_file):
            with patch('gfcli.repl.Note') as mock_note_class:
                with patch.object(repl, '_verify_suggestions') as mock_verify:
                    mock_note_class.return_value = mock_note

                    repl._save_capture("Test text", mock_result)

        mock_verify.assert_called_once_with(mock_suggestions, mock_session)
        mock_console.print.assert_any_call(f"\n✅ Captured! (Note #{mock_note.id})")
        mock_console.print.assert_any_call(f"📋 {len(mock_suggestions)} entities need verification\n")

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm')
    def test_save_capture_with_suggestions_verify_no(self, mock_confirm, mock_console, mock_suggestion_service, mock_session_class):
        """Test _save_capture with suggestions and user chooses not to verify"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock source file
        mock_source_file = Mock(id=123)

        # Mock note
        mock_note = Mock(id=456)

        # Mock suggestions
        mock_suggestions = [Mock(), Mock()]
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.create_suggestions_from_text.return_value = mock_suggestions

        # Mock user declines verification
        mock_confirm.ask.return_value = False

        mock_result = {'entities': {}, 'tasks': []}

        with patch.object(repl, '_get_or_create_quick_capture_file', return_value=mock_source_file):
            with patch('gfcli.repl.Note') as mock_note_class:
                with patch.object(repl, '_verify_suggestions') as mock_verify:
                    mock_note_class.return_value = mock_note

                    repl._save_capture("Test text", mock_result)

        mock_verify.assert_not_called()

    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    def test_save_capture_no_suggestions(self, mock_console, mock_suggestion_service, mock_session_class):
        """Test _save_capture with no suggestions"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock source file
        mock_source_file = Mock(id=123)

        # Mock note
        mock_note = Mock(id=456)

        # Mock no suggestions
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.create_suggestions_from_text.return_value = []

        mock_result = {'entities': {}, 'tasks': []}

        with patch.object(repl, '_get_or_create_quick_capture_file', return_value=mock_source_file):
            with patch('gfcli.repl.Note') as mock_note_class:
                with patch.object(repl, '_verify_suggestions') as mock_verify:
                    mock_note_class.return_value = mock_note

                    repl._save_capture("Test text", mock_result)

        mock_verify.assert_not_called()
        mock_console.print.assert_any_call(f"\n✅ Captured! (Note #{mock_note.id})")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_create_choice(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with create choice"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_console.print.assert_any_call("✅ Created new entity!", style="green")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_create_choice_short(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with create choice using short form 'c'"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "c"
        mock_prompt.ask.return_value = "c"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_console.print.assert_any_call("✅ Created new entity!", style="green")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_create_choice_error(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with create choice but service error"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []
        mock_service_instance.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "create"
        mock_prompt.ask.return_value = "create"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("❌ Error: Database error", style="red")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_link_choice_with_entities(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with link choice and existing entities"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock existing entities
        mock_existing_entities = [{"id": 1, "name": "John Smith", "match_score": 0.8}]

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = mock_existing_entities

        # Mock user chooses "link"
        mock_prompt.ask.return_value = "link"

        mock_db = Mock()

        with patch.object(repl, '_show_entity_linking_options') as mock_show_linking:
            repl._verify_suggestions([mock_suggestion], mock_db)

        mock_show_linking.assert_called_once_with(mock_suggestion, mock_existing_entities, mock_service_instance)

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Confirm')
    def test_verify_suggestions_link_choice_no_entities_create_yes(self, mock_confirm, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with link choice, no entities, user creates new"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "link" then confirms create new
        mock_prompt.ask.return_value = "link"
        mock_confirm.ask.return_value = True

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("No existing entities found to link to", style="yellow")
        mock_service_instance.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Confirm')
    def test_verify_suggestions_link_choice_no_entities_create_no(self, mock_confirm, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with link choice, no entities, user declines create"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "link" then declines create new
        mock_prompt.ask.return_value = "link"
        mock_confirm.ask.return_value = False

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("No existing entities found to link to", style="yellow")
        mock_service_instance.confirm_suggestion.assert_not_called()

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Confirm')
    def test_verify_suggestions_link_choice_no_entities_create_error(self, mock_confirm, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with link choice, no entities, create fails"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []
        mock_service_instance.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "link" then confirms create new
        mock_prompt.ask.return_value = "link"
        mock_confirm.ask.return_value = True

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("❌ Error: Database error", style="red")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_reject_choice(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with reject choice"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_service_instance.reject_suggestion.assert_called_once_with(123, 1)
        mock_console.print.assert_any_call("❌ Rejected", style="red")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_reject_choice_error(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with reject choice but service error"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []
        mock_service_instance.reject_suggestion.side_effect = Exception("Database error")

        # Mock user chooses "reject"
        mock_prompt.ask.return_value = "reject"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("❌ Error: Database error", style="red")

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_skip_choice(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with skip choice"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John"

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user chooses "skip"
        mock_prompt.ask.return_value = "skip"

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion], mock_db)

        mock_console.print.assert_any_call("⏭️  Skipped", style="yellow")
        # Should not call any suggestion service methods
        mock_service_instance.confirm_suggestion.assert_not_called()
        mock_service_instance.reject_suggestion.assert_not_called()

    @patch('gfcli.repl.SuggestionService')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    def test_verify_suggestions_multiple_suggestions_summary(self, mock_prompt, mock_console, mock_suggestion_service):
        """Test _verify_suggestions with multiple suggestions shows summary"""
        repl = GoldfishREPL()
        repl.user_id = 1

        # Mock suggestions
        mock_suggestion1 = Mock(id=123, entity_type="person", name="John", confidence=0.85, context="Meeting")
        mock_suggestion2 = Mock(id=124, entity_type="project", name="AI", confidence=0.90, context="Project")
        mock_suggestion3 = Mock(id=125, entity_type="person", name="Jane", confidence=0.80, context="Discussion")

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.find_existing_entities.return_value = []

        # Mock user choices: create, reject, skip
        mock_prompt.ask.side_effect = ["create", "reject", "skip"]

        mock_db = Mock()

        repl._verify_suggestions([mock_suggestion1, mock_suggestion2, mock_suggestion3], mock_db)

        # Should show summary at the end
        mock_console.print.assert_any_call(f"\n📊 Verification complete: {1} new, {0} linked, {1} rejected")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_user_selects_existing(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with user selecting existing entity"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [
            {
                "id": 1,
                "name": "John Smith",
                "match_score": 0.9,
                "aliases": ["Johnny"],
                "status": "active"
            }
        ]

        # Mock suggestion service
        mock_suggestion_service = Mock()

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user selects option 1
        mock_prompt.ask.return_value = "1"

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_suggestion_service.confirm_suggestion.assert_called_once_with(
            123, 1, create_new=False, existing_entity_id=1
        )
        mock_console.print.assert_any_call("🔗 Linked to existing entity: John Smith", style="green")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_user_creates_new(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with user creating new entity"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [
            {
                "id": 1,
                "name": "John Smith",
                "match_score": 0.9,
                "aliases": [],
                "status": "active"
            }
        ]

        # Mock suggestion service
        mock_suggestion_service = Mock()

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user selects option 0 (create new)
        mock_prompt.ask.return_value = "0"

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_suggestion_service.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_console.print.assert_any_call("✅ Created new entity!", style="green")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_invalid_then_valid_choice(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with invalid choice then valid choice"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [{"id": 1, "name": "John Smith", "match_score": 0.9}]

        # Mock suggestion service
        mock_suggestion_service = Mock()

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user makes invalid choice then valid choice
        mock_prompt.ask.side_effect = ["invalid", "0"]

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_console.print.assert_any_call("Please enter a valid number")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_out_of_range_then_valid_choice(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with out of range choice then valid choice"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [{"id": 1, "name": "John Smith", "match_score": 0.9}]

        # Mock suggestion service
        mock_suggestion_service = Mock()

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user makes out of range choice then valid choice
        mock_prompt.ask.side_effect = ["5", "0"]

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_console.print.assert_any_call("Please enter a number between 0 and 1")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_link_existing_error(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with error linking to existing entity"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [{"id": 1, "name": "John Smith", "match_score": 0.9}]

        # Mock suggestion service with error
        mock_suggestion_service = Mock()
        mock_suggestion_service.confirm_suggestion.side_effect = Exception("Database error")

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user selects option 1
        mock_prompt.ask.return_value = "1"

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_console.print.assert_any_call("❌ Error: Database error", style="red")

    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Prompt')
    @patch('gfcli.repl.Table')
    def test_show_entity_linking_options_create_new_error(self, mock_table_class, mock_prompt, mock_console):
        """Test _show_entity_linking_options with error creating new entity"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock existing entities
        existing_entities = [{"id": 1, "name": "John Smith", "match_score": 0.9}]

        # Mock suggestion service with error
        mock_suggestion_service = Mock()
        mock_suggestion_service.confirm_suggestion.side_effect = Exception("Database error")

        # Mock table
        mock_table = Mock()
        mock_table_class.return_value = mock_table

        # Mock user selects option 0 (create new)
        mock_prompt.ask.return_value = "0"

        repl._show_entity_linking_options(mock_suggestion, existing_entities, mock_suggestion_service)

        mock_console.print.assert_any_call("❌ Error: Database error", style="red")

    def test_show_entity_linking_options_no_entities(self):
        """Test _show_entity_linking_options with no entities (should return early)"""
        repl = GoldfishREPL()

        # Mock suggestion
        mock_suggestion = Mock()

        # Mock suggestion service
        mock_suggestion_service = Mock()

        # Should return early without doing anything
        result = repl._show_entity_linking_options(mock_suggestion, [], mock_suggestion_service)

        assert result is None
        mock_suggestion_service.confirm_suggestion.assert_not_called()

"""Tests for suggestions internal functions"""
from unittest.mock import Mock, patch

from gfcli.suggestions import _handle_entity_linking, _show_suggestion_details


class TestSuggestionsInternalFunctions:
    """Test internal suggestions functions"""

    @patch('gfcli.suggestions.console')
    def test_show_suggestion_details(self, mock_console):
        """Test _show_suggestion_details function"""
        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"
        mock_suggestion.confidence = 0.85
        mock_suggestion.context = "Meeting with John about the project"
        mock_suggestion.source_text = "Let's schedule a meeting with John"
        mock_suggestion.created_at.strftime.return_value = "2024-01-01 10:00:00"

        _show_suggestion_details(mock_suggestion)

        # Verify console output
        assert mock_console.print.called
        # Check that a panel was created and printed
        panel_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      'Panel' in str(call[0][0].__class__)]
        assert len(panel_calls) > 0

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Confirm')
    def test_handle_entity_linking_no_existing_entities_create_new(self, mock_confirm, mock_prompt, mock_console):
        """Test _handle_entity_linking with no existing entities, user chooses to create new"""
        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock suggestion service
        mock_suggestion_service = Mock()
        mock_suggestion_service.find_existing_entities.return_value = []
        mock_suggestion_service.confirm_suggestion.return_value = 456

        # Mock user confirms creating new entity
        mock_confirm.ask.return_value = True

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is True
        mock_suggestion_service.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_console.print.assert_any_call("No existing entities found to link to", style="yellow")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Confirm')
    def test_handle_entity_linking_no_existing_entities_decline_create(self, mock_confirm, mock_prompt, mock_console):
        """Test _handle_entity_linking with no existing entities, user declines to create new"""
        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock suggestion service
        mock_suggestion_service = Mock()
        mock_suggestion_service.find_existing_entities.return_value = []

        # Mock user declines creating new entity
        mock_confirm.ask.return_value = False

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is False
        mock_suggestion_service.confirm_suggestion.assert_not_called()

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_with_existing_entities_create_new(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with existing entities, user chooses to create new (option 0)"""
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
                "match_score": 0.7,
                "aliases": ["Johnny", "J. Smith"],
                "status": "active"
            },
            {
                "id": 2,
                "name": "John Davis",
                "match_score": 0.6,
                "aliases": [],
                "status": "inactive"
            }
        ]

        # Mock suggestion service
        mock_suggestion_service = Mock()
        mock_suggestion_service.find_existing_entities.return_value = existing_entities
        mock_suggestion_service.confirm_suggestion.return_value = 456

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user chooses option 0 (create new)
        mock_prompt.ask.return_value = "0"

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is True
        mock_suggestion_service.confirm_suggestion.assert_called_once_with(123, 1, create_new=True)
        mock_console.print.assert_any_call("\n🔗 Found existing entities to link to:")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_with_existing_entities_link_to_existing(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with existing entities, user chooses to link to existing (option 1)"""
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
        mock_suggestion_service.find_existing_entities.return_value = existing_entities

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user chooses option 1 (link to existing)
        mock_prompt.ask.return_value = "1"

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is True
        mock_suggestion_service.confirm_suggestion.assert_called_once_with(
            123, 1, create_new=False, existing_entity_id=1
        )
        mock_console.print.assert_any_call("🔗 Linked to existing entity: John Smith")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_invalid_choice_then_valid(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with invalid choice first, then valid choice"""
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
        mock_suggestion_service.find_existing_entities.return_value = existing_entities

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user makes invalid choice first, then valid choice
        mock_prompt.ask.side_effect = ["invalid", "0"]

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is True
        mock_console.print.assert_any_call("Please enter a valid number")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_out_of_range_choice_then_valid(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with out of range choice first, then valid choice"""
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
        mock_suggestion_service.find_existing_entities.return_value = existing_entities

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user makes out of range choice first, then valid choice
        mock_prompt.ask.side_effect = ["5", "0"]

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is True
        mock_console.print.assert_any_call("Please enter a number between 0 and 1")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_create_new_error(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with error when creating new entity"""
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
        mock_suggestion_service.find_existing_entities.return_value = existing_entities
        mock_suggestion_service.confirm_suggestion.side_effect = Exception("Database error")

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user chooses option 0 (create new)
        mock_prompt.ask.return_value = "0"

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is False
        mock_console.print.assert_any_call("❌ Error creating entity: Database error")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Table')
    def test_handle_entity_linking_link_existing_error(self, mock_table, mock_prompt, mock_console):
        """Test _handle_entity_linking with error when linking to existing entity"""
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
        mock_suggestion_service.find_existing_entities.return_value = existing_entities
        mock_suggestion_service.confirm_suggestion.side_effect = Exception("Database error")

        # Mock table
        mock_table_instance = Mock()
        mock_table.return_value = mock_table_instance

        # Mock user chooses option 1 (link to existing)
        mock_prompt.ask.return_value = "1"

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is False
        mock_console.print.assert_any_call("❌ Error linking to entity: Database error")

    @patch('gfcli.suggestions.console')
    @patch('gfcli.suggestions.Prompt')
    @patch('gfcli.suggestions.Confirm')
    def test_handle_entity_linking_no_existing_create_new_error(self, mock_confirm, mock_prompt, mock_console):
        """Test _handle_entity_linking with no existing entities, create new entity fails"""
        # Mock suggestion
        mock_suggestion = Mock()
        mock_suggestion.id = 123
        mock_suggestion.entity_type = "person"
        mock_suggestion.name = "John Doe"

        # Mock suggestion service
        mock_suggestion_service = Mock()
        mock_suggestion_service.find_existing_entities.return_value = []
        mock_suggestion_service.confirm_suggestion.side_effect = Exception("Database error")

        # Mock user confirms creating new entity
        mock_confirm.ask.return_value = True

        result = _handle_entity_linking(mock_suggestion, mock_suggestion_service, 1)

        assert result is False
        mock_console.print.assert_any_call("❌ Error creating entity: Database error")

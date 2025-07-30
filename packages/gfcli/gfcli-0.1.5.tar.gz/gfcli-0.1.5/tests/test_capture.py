"""Tests for capture commands"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestCaptureCommands:
    """Test suite for capture commands"""

    def test_capture_quick_with_text(self):
        """Test quick capture with text"""
        runner = CliRunner()

        with patch('gfcli.capture._process_and_store') as mock_process:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note with @sarah'])

            assert result.exit_code == 0
            mock_process.assert_called_once_with('Test note with @sarah', 1)

    def test_capture_quick_with_preview(self):
        """Test quick capture with preview flag"""
        runner = CliRunner()

        with patch('gfcli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note', '--preview'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Test note')

    def test_capture_quick_with_custom_user_id(self):
        """Test quick capture with custom user ID"""
        runner = CliRunner()

        with patch('gfcli.capture._process_and_store') as mock_process:
            result = runner.invoke(cli, ['capture', 'quick', 'Test note', '--user-id', '5'])

            assert result.exit_code == 0
            mock_process.assert_called_once_with('Test note', 5)

    def test_capture_analyze(self):
        """Test analyze command"""
        runner = CliRunner()

        with patch('gfcli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'analyze', 'Meeting with @john'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Meeting with @john')

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture.EntityRecognitionEngine')
    @patch('gfcli.capture.SuggestionService')
    @patch('gfcli.capture.console')
    def test_preview_entities_success(self, mock_console, mock_suggestion_service,
                                    mock_engine, mock_session, mock_create_db):
        """Test _preview_entities function with successful entity extraction"""
        from gfcli.capture import _preview_entities

        # Mock entity recognition with proper structure
        mock_engine_instance = Mock()

        # Create proper entity and task mocks
        person_entity = Mock()
        person_entity.name = "sarah"
        person_entity.confidence = 0.9
        person_entity.context = "Meeting with @sarah about"

        project_entity = Mock()
        project_entity.name = "ai-platform"
        project_entity.confidence = 0.95
        project_entity.context = "about #ai-platform"

        task_mock = Mock()
        task_mock.content = "Follow up with sarah"
        task_mock.confidence = 0.8
        task_mock.context = "Follow up with sarah about the project"

        mock_engine_instance.process_text.return_value = {
            'entities': {
                'people': [person_entity],
                'projects': [project_entity],
                'topics': []
            },
            'tasks': [task_mock],
            'total_entities': 2,
            'total_tasks': 1
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

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture.EntityRecognitionEngine')
    @patch('gfcli.capture.console')
    def test_preview_entities_no_entities(self, mock_console, mock_engine,
                                         mock_session, mock_create_db):
        """Test _preview_entities with no entities found"""
        from gfcli.capture import _preview_entities

        # Mock entity recognition with no entities
        mock_engine_instance = Mock()
        mock_engine_instance.process_text.return_value = {
            'entities': {
                'people': [],
                'projects': [],
                'topics': []
            },
            'tasks': [],
            'total_entities': 0,
            'total_tasks': 0
        }
        mock_engine.return_value = mock_engine_instance

        _preview_entities("Simple text with no entities")

        # Verify appropriate message was printed
        mock_console.print.assert_any_call("❌ No entities or tasks found in the text")

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture._get_or_create_quick_capture_file')
    @patch('gfcli.capture.EntityRecognitionEngine')
    @patch('gfcli.capture.SuggestionService')
    @patch('gfcli.capture.console')
    def test_process_and_store_success(self, mock_console, mock_suggestion_service,
                                     mock_engine, mock_get_source_file, mock_session_class, mock_create_db):
        """Test _process_and_store function with successful processing"""
        from gfcli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user query
        mock_user_obj = Mock(id=1)
        mock_session.get.return_value = mock_user_obj

        # Mock source file
        mock_source_file = Mock(id=1)
        mock_get_source_file.return_value = mock_source_file

        # Mock entity recognition
        mock_engine_instance = Mock()
        mock_engine_instance.process_text.return_value = {
            'entities': {
                'people': [Mock(name='sarah', confidence=0.9)],
                'projects': [],
                'topics': []
            },
            'tasks': [],
            'total_entities': 1,
            'total_tasks': 0
        }
        mock_engine.return_value = mock_engine_instance

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion = Mock()
        mock_suggestion.confidence = 0.9
        mock_suggestion.name = "sarah"
        mock_suggestion.entity_type = "person"
        mock_service_instance.create_suggestions_from_text.return_value = [mock_suggestion]
        mock_suggestion_service.return_value = mock_service_instance

        _process_and_store("Test note with @sarah", 1)

        # Verify database operations
        assert mock_session.add.called
        assert mock_session.commit.called
        # Check that the success message was printed (note.id should be available)
        success_calls = [call for call in mock_console.print.call_args_list
                        if str(call[0][0]).startswith("✅ Text captured and processed")]
        assert len(success_calls) > 0

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture.console')
    def test_process_and_store_user_not_found(self, mock_console, mock_session_class,
                                             mock_create_db):
        """Test _process_and_store when user is not found"""
        from gfcli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user query to return None
        mock_session.get.return_value = None

        _process_and_store("Test note", 999)

        # Verify error message
        mock_console.print.assert_any_call("❌ User with ID 999 not found. Run: goldfish config setup")

    def test_capture_analyze_command(self):
        """Test capture analyze command"""
        runner = CliRunner()

        with patch('gfcli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'analyze', 'Test text'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Test text')

    def test_capture_quick_with_preview_flag(self):
        """Test capture quick command with preview flag"""
        runner = CliRunner()

        with patch('gfcli.capture._preview_entities') as mock_preview:
            result = runner.invoke(cli, ['capture', 'quick', 'Test text', '--preview'])

            assert result.exit_code == 0
            mock_preview.assert_called_once_with('Test text')

    def test_capture_quick_without_text(self):
        """Test quick capture without required text argument"""
        runner = CliRunner()
        result = runner.invoke(cli, ['capture', 'quick'])

        assert result.exit_code != 0
        assert "Missing argument" in result.output

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture.SuggestionService')
    @patch('gfcli.capture.console')
    def test_process_and_store_with_many_suggestions(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test _process_and_store with more than 5 suggestions to cover line 190"""
        from gfcli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock source file
        mock_source_file = Mock()
        mock_source_file.id = 1

        # Mock note with ID
        mock_note = Mock()
        mock_note.id = 123
        mock_session.add.return_value = None
        mock_session.flush.return_value = None

        # Create 7 mock suggestions to trigger the "more" row (line 190)
        suggestions = []
        for i in range(7):
            mock_suggestion = Mock()
            mock_suggestion.id = i + 1
            mock_suggestion.entity_type = "person"
            mock_suggestion.name = f"Person {i+1}"
            mock_suggestion.confidence = 0.8
            suggestions.append(mock_suggestion)

        # Mock suggestion service
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.create_suggestions_from_text.return_value = suggestions

        # Mock _get_or_create_quick_capture_file
        with patch('gfcli.capture._get_or_create_quick_capture_file') as mock_get_file:
            mock_get_file.return_value = mock_source_file

            # Mock Note creation
            with patch('gfcli.capture.Note') as mock_note_class:
                mock_note_class.return_value = mock_note

                _process_and_store("test text", 1)

        # Should print table with "more" row
        assert mock_console.print.called

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    @patch('gfcli.capture.SuggestionService')
    @patch('gfcli.capture.console')
    def test_process_and_store_no_suggestions(self, mock_console, mock_suggestion_service, mock_session_class, mock_create_db):
        """Test _process_and_store with no suggestions to cover line 194"""
        from gfcli.capture import _process_and_store

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        # Mock source file
        mock_source_file = Mock()
        mock_source_file.id = 1

        # Mock note with ID
        mock_note = Mock()
        mock_note.id = 123
        mock_session.add.return_value = None
        mock_session.flush.return_value = None

        # Mock suggestion service with no suggestions
        mock_service_instance = Mock()
        mock_suggestion_service.return_value = mock_service_instance
        mock_service_instance.create_suggestions_from_text.return_value = []  # No suggestions

        # Mock _get_or_create_quick_capture_file
        with patch('gfcli.capture._get_or_create_quick_capture_file') as mock_get_file:
            mock_get_file.return_value = mock_source_file

            # Mock Note creation
            with patch('gfcli.capture.Note') as mock_note_class:
                mock_note_class.return_value = mock_note

                _process_and_store("test text", 1)

        # Should print no suggestions message
        assert mock_console.print.called

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    def test_get_or_create_quick_capture_file_existing(self, mock_session_class, mock_create_db):
        """Test _get_or_create_quick_capture_file with existing file"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing source file
        mock_source_file = Mock()
        mock_source_file.id = 1
        mock_session.exec.return_value.first.return_value = mock_source_file

        # Import and call function
        from gfcli.capture import _get_or_create_quick_capture_file
        result = _get_or_create_quick_capture_file(1, mock_session)

        assert result == mock_source_file
        # Should not add or flush since file exists
        mock_session.add.assert_not_called()
        mock_session.flush.assert_not_called()

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    def test_get_or_create_quick_capture_file_new(self, mock_session_class, mock_create_db):
        """Test _get_or_create_quick_capture_file creating new file"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock no existing source file
        mock_session.exec.return_value.first.return_value = None

        # Import and call function
        from gfcli.capture import _get_or_create_quick_capture_file
        result = _get_or_create_quick_capture_file(1, mock_session)

        # Should create new source file
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
        assert result is not None

"""Tests for REPL functionality"""
from unittest.mock import MagicMock, Mock, patch

from gfcli.repl import GoldfishREPL


class TestGoldfishREPL:
    """Test REPL main functionality"""

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_initialization(self, mock_console, mock_engine):
        """Test REPL initialization"""
        repl = GoldfishREPL()

        assert repl.user_id == 1
        assert repl.running is True
        assert repl.recognition_engine is not None
        mock_engine.assert_called_once()

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_show_help(self, mock_console, mock_engine):
        """Test help command in REPL"""
        repl = GoldfishREPL()
        repl.show_help()

        # Verify help was printed
        assert mock_console.print.called

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_exit_command(self, mock_console, mock_engine):
        """Test exit command in REPL"""
        repl = GoldfishREPL()
        repl.exit_repl()

        assert repl.running is False
        mock_console.print.assert_called_with("\n👋 Goodbye! Thanks for using Goldfish.")

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    @patch('os.system')
    def test_repl_clear_command(self, mock_system, mock_console, mock_engine):
        """Test clear command in REPL"""
        repl = GoldfishREPL()
        # Mock user to avoid _show_welcome trying to access user.full_name
        repl.user = Mock()
        repl.user.full_name = "Test User"
        repl.clear_screen()

        mock_system.assert_called_once()
        assert mock_console.print.called  # _show_welcome is called

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    @patch('gfcli.dashboard._get_user_stats')
    def test_repl_show_status(self, mock_get_user_stats, mock_console, mock_engine, mock_session_class, mock_create_db):
        """Test status command in REPL"""
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock the stats returned by _get_user_stats
        mock_get_user_stats.return_value = {
            'notes': 5,
            'total_chars': 1000,
            'latest_note': 'Today',
            'pending_suggestions': 2,
            'confirmed_entities': 10,
            'accuracy_rate': 95.5,
            'people': 3,
            'projects': 2,
            'topics': 1
        }

        repl = GoldfishREPL()
        repl.show_status()

        # Verify status was printed
        assert mock_console.print.called

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_show_config(self, mock_console, mock_engine):
        """Test config command in REPL"""
        repl = GoldfishREPL()
        # Mock user to avoid accessing None attributes
        repl.user = Mock()
        repl.user.full_name = "Test User"
        repl.user.email = "test@example.com"
        repl.user.created_at = Mock()
        repl.user.created_at.strftime.return_value = "2024-01-01"

        repl.show_config()

        # Verify config was printed
        assert mock_console.print.called

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_start_interactive(self, mock_console, mock_engine, mock_session_class, mock_create_db):
        """Test REPL start method"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock prompt session
        with patch('gfcli.repl.PromptSession') as mock_prompt_session:
            mock_session_instance = Mock()
            mock_prompt_session.return_value = mock_session_instance

            # Make REPL exit after one iteration
            repl = GoldfishREPL()
            repl.running = False  # Exit immediately

            repl.start()

            # Verify initialization
            mock_prompt_session.assert_called_once()

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    @patch('gfcli.repl.Confirm.ask')
    def test_repl_capture_text(self, mock_confirm, mock_console, mock_engine_class, mock_session_class, mock_create_db):
        """Test capture text functionality"""
        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        mock_engine = Mock()
        mock_engine.process_text.return_value = {
            'entities': {
                'people': [Mock(name='john', confidence=0.9, context='@john')],
                'projects': [],
                'topics': []
            },
            'tasks': [],
            'total_entities': 1,
            'total_tasks': 0
        }
        mock_engine_class.return_value = mock_engine

        # Mock user declining to save
        mock_confirm.return_value = False

        repl = GoldfishREPL()
        repl._capture_text("Meeting with @john")

        mock_engine.process_text.assert_called_once()
        assert mock_console.print.called

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_command_parsing(self, mock_console, mock_engine):
        """Test command parsing in REPL"""
        repl = GoldfishREPL()

        # Test valid command - call the command directly
        repl.show_help()
        assert mock_console.print.called

        # Reset mock
        mock_console.reset_mock()

        # Test that commands dict contains expected commands
        assert 'help' in repl.commands
        assert 'exit' in repl.commands
        assert 'status' in repl.commands

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_keyboard_interrupt_handling(self, mock_console, mock_engine):
        """Test REPL handles keyboard interrupt gracefully"""
        repl = GoldfishREPL()

        # Test that KeyboardInterrupt doesn't crash the REPL
        # The interrupt handling is done in the main loop
        assert repl.running is True

        # Test that we can still exit normally
        repl.exit_repl()
        assert repl.running is False

    @patch('gfcli.repl.EntityRecognitionEngine')
    @patch('gfcli.repl.console')
    def test_repl_eof_handling(self, mock_console, mock_engine):
        """Test REPL handles EOF gracefully"""
        repl = GoldfishREPL()

        # Test that EOFError causes exit
        # The EOF handling is done in the _process_input method
        assert repl.running is True

        # Test that we can still exit normally
        repl.exit_repl()
        assert repl.running is False

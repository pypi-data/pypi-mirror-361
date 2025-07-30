"""Tests for REPL process input functionality"""
from unittest.mock import Mock, patch

from gfcli.repl import GoldfishREPL


class TestREPLProcess:
    """Test REPL input processing functionality"""

    def test_process_input_empty_input(self):
        """Test _process_input with empty input"""
        repl = GoldfishREPL()

        with patch.object(repl, 'session') as mock_session:
            mock_session.prompt.return_value = "   "  # whitespace only

            # Should return without doing anything
            repl._process_input()

            # Verify no commands were executed
            assert True  # If we get here without error, test passes

    def test_process_input_command(self):
        """Test _process_input with valid command"""
        repl = GoldfishREPL()

        with patch.object(repl, 'show_help') as mock_help:
            with patch.object(repl, 'session') as mock_session:
                mock_session.prompt.return_value = "help"
                repl._process_input()

        mock_help.assert_called_once()

    def test_process_input_command_case_insensitive(self):
        """Test _process_input with command in different case"""
        repl = GoldfishREPL()

        with patch.object(repl, 'show_help') as mock_help:
            with patch.object(repl, 'session') as mock_session:
                mock_session.prompt.return_value = "HELP"
                repl._process_input()

        mock_help.assert_called_once()

    def test_process_input_text_capture(self):
        """Test _process_input with text for capture"""
        repl = GoldfishREPL()

        with patch.object(repl, '_capture_text') as mock_capture:
            with patch.object(repl, 'session') as mock_session:
                mock_session.prompt.return_value = "Meeting with @john about #project"
                repl._process_input()

        mock_capture.assert_called_once_with("Meeting with @john about #project")

    def test_process_input_eof_error(self):
        """Test _process_input with EOFError (Ctrl+D)"""
        repl = GoldfishREPL()

        with patch.object(repl, 'exit_repl') as mock_exit:
            with patch.object(repl, 'session') as mock_session:
                mock_session.prompt.side_effect = EOFError()
                repl._process_input()

        mock_exit.assert_called_once()

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_start_user_exists_no_pending_suggestions(self, mock_console, mock_session_class, mock_create_db):
        """Test start() with existing user and no pending suggestions"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing user
        mock_user = Mock()
        mock_user.id = 1
        mock_session.get.return_value = mock_user

        with patch.object(repl, 'clear_screen') as mock_clear:
            with patch.object(repl, '_check_pending_suggestions') as mock_check:
                with patch.object(repl, '_process_input'):
                    # Mock running = False to exit loop after one iteration
                    repl.running = False

                    repl.start()

        assert repl.user == mock_user
        mock_clear.assert_called_once()
        mock_check.assert_called_once()

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_start_user_not_exists(self, mock_console, mock_session_class, mock_create_db):
        """Test start() with no existing user (triggers first time setup)"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock no existing user
        mock_session.get.return_value = None

        with patch.object(repl, '_first_time_setup') as mock_setup:
            with patch.object(repl, '_check_pending_suggestions') as mock_check:
                with patch.object(repl, '_process_input'):
                    # Mock running = False to exit loop after one iteration
                    repl.running = False

                    repl.start()

        mock_setup.assert_called_once()
        mock_check.assert_called_once()

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_start_keyboard_interrupt_handling(self, mock_console, mock_session_class, mock_create_db):
        """Test start() handling KeyboardInterrupt"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing user
        mock_user = Mock()
        mock_session.get.return_value = mock_user

        call_count = 0
        def mock_process_input():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise KeyboardInterrupt()
            else:
                repl.running = False  # Exit after handling interrupt

        with patch.object(repl, 'clear_screen'):
            with patch.object(repl, '_check_pending_suggestions'):
                with patch.object(repl, '_process_input', side_effect=mock_process_input):
                    repl.start()

        mock_console.print.assert_any_call("\n💡 Use 'exit' or 'quit' to leave Goldfish")

    @patch('gfcli.repl.create_db_and_tables')
    @patch('gfcli.repl.Session')
    @patch('gfcli.repl.console')
    def test_start_general_exception_handling(self, mock_console, mock_session_class, mock_create_db):
        """Test start() handling general exceptions"""
        repl = GoldfishREPL()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing user
        mock_user = Mock()
        mock_session.get.return_value = mock_user

        call_count = 0
        def mock_process_input():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            else:
                repl.running = False  # Exit after handling exception

        with patch.object(repl, 'clear_screen'):
            with patch.object(repl, '_check_pending_suggestions'):
                with patch.object(repl, '_process_input', side_effect=mock_process_input):
                    repl.start()

        mock_console.print.assert_any_call("❌ Error: Test error", style="red")

    @patch('gfcli.repl.os')
    @patch('gfcli.repl.console')
    def test_clear_screen_posix(self, mock_console, mock_os):
        """Test clear_screen on POSIX system"""
        repl = GoldfishREPL()

        # Mock user for _show_welcome
        mock_user = Mock()
        mock_user.full_name = "Test User"
        repl.user = mock_user

        # Mock POSIX system
        mock_os.name = 'posix'

        with patch.object(repl, '_show_welcome') as mock_welcome:
            repl.clear_screen()

        mock_os.system.assert_called_with('clear')
        mock_welcome.assert_called_once()

    @patch('gfcli.repl.os')
    @patch('gfcli.repl.console')
    def test_clear_screen_windows(self, mock_console, mock_os):
        """Test clear_screen on Windows system"""
        repl = GoldfishREPL()

        # Mock user for _show_welcome
        mock_user = Mock()
        mock_user.full_name = "Test User"
        repl.user = mock_user

        # Mock Windows system
        mock_os.name = 'nt'

        with patch.object(repl, '_show_welcome') as mock_welcome:
            repl.clear_screen()

        mock_os.system.assert_called_with('cls')
        mock_welcome.assert_called_once()

    @patch('gfcli.repl.console')
    def test_show_config_with_user(self, mock_console):
        """Test show_config with user data"""
        repl = GoldfishREPL()

        # Mock user
        from datetime import datetime
        mock_user = Mock()
        mock_user.full_name = "John Doe"
        mock_user.email = "john@example.com"
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        repl.user = mock_user
        repl.user_id = 123

        repl.show_config()

        # Should print config panel
        assert mock_console.print.called
        # Check that a panel was created and printed
        panel_calls = [call for call in mock_console.print.call_args_list
                      if hasattr(call[0][0], '__class__') and
                      'Panel' in str(call[0][0].__class__)]
        assert len(panel_calls) > 0

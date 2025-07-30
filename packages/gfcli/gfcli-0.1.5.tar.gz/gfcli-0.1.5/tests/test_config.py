"""Tests for config commands"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestConfigCommands:
    """Test suite for config commands"""

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    def test_config_info(self, mock_console, mock_session_class, mock_create_db):
        """Test config info command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.bio = "Test bio"
        mock_user.created_at.strftime.return_value = "2023-01-01 12:00:00"
        mock_user.is_active = True
        mock_session.get.return_value = mock_user

        # Mock database queries
        mock_session.exec.return_value.one.return_value = 5  # Mock count

        result = runner.invoke(cli, ['config', 'info'])

        assert result.exit_code == 0
        assert mock_console.print.called

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    def test_config_info_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test config info when user not found"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['config', 'info'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ User with ID 1 not found")

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('gfcli.config.Prompt')
    def test_config_setup_success(self, mock_prompt, mock_console, mock_session_class, mock_create_db):
        """Test config setup command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock prompts
        mock_prompt.ask.side_effect = ["test@example.com", "Test User", "ValidPass1!", "Test bio"]

        # Mock password validation
        with patch('gfcli.config.validate_password_strength', return_value=True):
            with patch('gfcli.config.get_password_hash', return_value="hashed_password"):
                # Mock no existing user
                mock_session.exec.return_value.first.return_value = None

                result = runner.invoke(cli, ['config', 'setup'])

        assert result.exit_code == 0
        assert mock_session.add.called
        assert mock_session.commit.called

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('gfcli.config.Prompt')
    def test_config_update_success(self, mock_prompt, mock_console, mock_session_class, mock_create_db):
        """Test config update command"""
        runner = CliRunner()

        # Setup mocks
        mock_session = Mock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.email = "test@example.com"
        mock_user.full_name = "Test User"
        mock_user.bio = "Old bio"
        mock_session.get.return_value = mock_user

        # Mock prompts
        mock_prompt.ask.side_effect = ["New Test User", "New bio"]

        result = runner.invoke(cli, ['config', 'update'])

        assert result.exit_code == 0
        assert mock_session.add.called
        assert mock_session.commit.called

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('rich.prompt.Confirm')
    def test_config_reset_success(self, mock_confirm, mock_console, mock_session_class, mock_create_db):
        """Test config reset command"""
        runner = CliRunner()

        # Mock confirmations
        mock_confirm.ask.side_effect = [True, True]

        with patch('sqlmodel.SQLModel') as mock_sqlmodel:
            result = runner.invoke(cli, ['config', 'reset'])

        assert result.exit_code == 0
        assert mock_sqlmodel.metadata.drop_all.called
        assert mock_create_db.called

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('rich.prompt.Confirm')
    def test_config_reset_cancelled(self, mock_confirm, mock_console, mock_session_class, mock_create_db):
        """Test config reset command cancelled"""
        runner = CliRunner()

        # Mock first confirmation as False
        mock_confirm.ask.return_value = False

        result = runner.invoke(cli, ['config', 'reset'])

        assert result.exit_code == 0
        mock_console.print.assert_any_call("❌ Reset cancelled")

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('rich.prompt.Prompt.ask')
    @patch('gfcli.config.validate_password_strength')
    def test_config_setup_password_validation_error(self, mock_validate, mock_prompt, mock_console, mock_session_class, mock_create_db):
        """Test config setup with invalid password to cover line 43"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock no existing user
        mock_session.exec.return_value.first.return_value = None

        # Mock prompt responses
        mock_prompt.side_effect = [
            "test@example.com",  # email
            "Test User",         # full name
            "weak",              # first password attempt (invalid)
            "StrongPass123!",    # second password attempt (valid)
            ""                   # bio
        ]

        # Mock password validation: first time False, second time True
        mock_validate.side_effect = [False, True]

        result = runner.invoke(cli, ['config', 'setup'])

        assert result.exit_code == 0
        # Check that password validation error message was printed
        mock_console.print.assert_any_call("❌ Password must be at least 8 characters with uppercase, lowercase, digit, and special character")

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    @patch('rich.prompt.Prompt.ask')
    def test_config_setup_user_already_exists(self, mock_prompt, mock_console, mock_session_class, mock_create_db):
        """Test config setup when user already exists to cover lines 54-55"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock existing user
        mock_existing_user = Mock()
        mock_existing_user.email = "test@example.com"
        mock_session.exec.return_value.first.return_value = mock_existing_user

        # Mock prompt responses
        mock_prompt.side_effect = [
            "test@example.com",  # email
            "Test User",         # full name
            "StrongPass123!",    # password
            ""                   # bio
        ]

        # Mock password validation
        with patch('gfcli.config.validate_password_strength', return_value=True):
            result = runner.invoke(cli, ['config', 'setup'])

        assert result.exit_code == 0
        # Check that user exists error message was printed
        mock_console.print.assert_any_call("❌ User with email test@example.com already exists!")

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    @patch('gfcli.config.console')
    def test_config_update_user_not_found(self, mock_console, mock_session_class, mock_create_db):
        """Test config update when user not found to cover lines 153-154"""
        runner = CliRunner()

        # Setup mocks
        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user not found
        mock_session.get.return_value = None

        result = runner.invoke(cli, ['config', 'update', '--user-id', '999'])

        assert result.exit_code == 0
        # Check that user not found error message was printed
        mock_console.print.assert_any_call("❌ User with ID 999 not found")

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.console')
    @patch('rich.prompt.Confirm.ask')
    def test_config_reset_second_confirmation_cancelled(self, mock_confirm, mock_console, mock_create_db):
        """Test config reset cancelled at second confirmation to cover lines 186-187"""
        runner = CliRunner()

        # Mock first confirmation yes, second confirmation no
        mock_confirm.side_effect = [True, False]

        result = runner.invoke(cli, ['config', 'reset'])

        assert result.exit_code == 0
        # Check that second cancellation message was printed
        mock_console.print.assert_any_call("❌ Reset cancelled")

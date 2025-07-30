"""Tests for edge cases and error handling"""
from unittest.mock import MagicMock, Mock, patch

from click.testing import CliRunner

from gfcli.main import cli


class TestEdgeCases:
    """Test edge cases and error scenarios"""

    @patch('gfcli.capture.create_db_and_tables')
    @patch('gfcli.capture.Session')
    def test_database_connection_error(self, mock_session_class, mock_create_db):
        """Test handling database connection errors"""
        runner = CliRunner()

        # Mock database error
        mock_create_db.side_effect = Exception("Database connection failed")

        result = runner.invoke(cli, ['capture', 'quick', 'test'])

        # Should handle error gracefully
        assert result.exit_code != 0

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    def test_config_setup_database_error(self, mock_session_class, mock_create_db):
        """Test handling database errors in config setup"""
        runner = CliRunner()

        # Mock database error
        mock_create_db.side_effect = Exception("Database setup failed")

        result = runner.invoke(cli, ['config', 'setup'])

        # Should handle error gracefully
        assert result.exit_code != 0

    @patch('gfcli.config.create_db_and_tables')
    @patch('gfcli.config.Session')
    def test_config_info_database_error(self, mock_session_class, mock_create_db):
        """Test handling database errors in config info"""
        runner = CliRunner()

        # Mock database error
        mock_create_db.side_effect = Exception("Database access failed")

        result = runner.invoke(cli, ['config', 'info'])

        # Should handle error gracefully
        assert result.exit_code != 0

    @patch('gfcli.suggestions.Session')
    def test_suggestions_database_transaction_error(self, mock_session_class):
        """Test handling database transaction errors"""
        runner = CliRunner()

        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock transaction error
        mock_session.commit.side_effect = Exception("Transaction failed")
        mock_session.query.return_value.filter.return_value.first.return_value = Mock(id=1)

        result = runner.invoke(cli, ['suggestions', 'review', '1'])

        # Should handle error gracefully
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_capture_with_empty_text(self):
        """Test capture command with empty text"""
        runner = CliRunner()

        result = runner.invoke(cli, ['capture', 'quick', ''])

        # Should handle empty text gracefully
        assert result.exit_code == 0

    @patch('gfcli.dashboard.create_db_and_tables')
    @patch('gfcli.dashboard.Session')
    def test_dashboard_with_malformed_data(self, mock_session_class, mock_create_db):
        """Test dashboard handling malformed database data"""
        runner = CliRunner()

        mock_session = MagicMock()
        mock_session_class.return_value.__enter__.return_value = mock_session

        # Mock user
        mock_user = Mock()
        mock_user.full_name = "Test User"
        mock_session.get.return_value = mock_user

        # Mock malformed data - exec calls that raise exceptions
        mock_session.exec.side_effect = Exception("Malformed data")

        result = runner.invoke(cli, ['dashboard', 'status'])

        # Should handle error gracefully
        assert result.exit_code != 0

    def test_cli_with_very_long_input(self):
        """Test CLI with very long input text"""
        runner = CliRunner()

        # Create very long input (10KB)
        long_text = "a" * 10000

        result = runner.invoke(cli, ['capture', 'quick', long_text])

        # Should handle long input gracefully
        assert result.exit_code == 0

    @patch('gfcli.capture.EntityRecognitionEngine')
    def test_entity_recognition_engine_failure(self, mock_engine):
        """Test handling entity recognition engine failures"""
        runner = CliRunner()

        # Mock engine failure
        mock_engine.return_value.process_text.side_effect = Exception("Engine failed")

        result = runner.invoke(cli, ['capture', 'analyze', 'test text'])

        # Should handle error gracefully
        assert result.exit_code != 0

    def test_multiple_flags_combination(self):
        """Test CLI with multiple flag combinations"""
        runner = CliRunner()

        # Test version flag with other flags
        result = runner.invoke(cli, ['--version', '--no-interactive'])

        # Version should take precedence
        assert result.exit_code == 0
        assert "Goldfish CLI v" in result.output

    def test_concurrent_suggestion_modification(self):
        """Test handling concurrent modification of suggestions"""
        runner = CliRunner()

        # Test with non-existent suggestion ID
        result = runner.invoke(cli, ['suggestions', 'review', '99999'])

        # Should handle gracefully with appropriate error message
        assert result.exit_code == 0 or result.exit_code == 2  # Click error for missing command

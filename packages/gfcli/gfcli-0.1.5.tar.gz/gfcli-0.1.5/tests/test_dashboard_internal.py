"""Tests for dashboard internal functions"""
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from gfcli.dashboard import _get_user_stats, _show_all_entities, _show_entities_by_type


class TestDashboardInternalFunctions:
    """Test internal dashboard functions"""

    @patch('gfcli.dashboard.console')
    def test_show_all_entities_with_people(self, mock_console):
        """Test _show_all_entities with people data"""
        mock_db = MagicMock()

        # Mock people
        mock_person = Mock()
        mock_person.id = 1
        mock_person.name = "John Doe"
        mock_person.importance_score = 8.5
        mock_person.email = "john@example.com"

        # Mock empty projects and topics
        mock_db.exec.return_value.all.side_effect = [
            [mock_person],  # people query
            [],             # projects query
            []              # topics query
        ]

        _show_all_entities(mock_db, 1)

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_all_entities_with_projects(self, mock_console):
        """Test _show_all_entities with projects data"""
        mock_db = MagicMock()

        # Mock project
        mock_project = Mock()
        mock_project.id = 1
        mock_project.name = "AI Project"
        mock_project.status = "active"
        mock_project.priority_score = 9.0
        mock_project.deadline = datetime(2024, 12, 31)

        # Mock empty people and topics
        mock_db.exec.return_value.all.side_effect = [
            [],              # people query
            [mock_project],  # projects query
            []               # topics query
        ]

        _show_all_entities(mock_db, 1)

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_all_entities_with_topics(self, mock_console):
        """Test _show_all_entities with topics data"""
        mock_db = MagicMock()

        # Mock topic
        mock_topic = Mock()
        mock_topic.id = 1
        mock_topic.name = "Machine Learning"
        mock_topic.category = "Technology"
        mock_topic.research_score = 7.5

        # Mock empty people and projects
        mock_db.exec.return_value.all.side_effect = [
            [],             # people query
            [],             # projects query
            [mock_topic]    # topics query
        ]

        _show_all_entities(mock_db, 1)

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_all_entities_empty(self, mock_console):
        """Test _show_all_entities with no entities"""
        mock_db = MagicMock()

        # Mock all empty queries
        mock_db.exec.return_value.all.return_value = []

        _show_all_entities(mock_db, 1)

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_people(self, mock_console):
        """Test _show_entities_by_type for people"""
        mock_db = MagicMock()

        # Mock person with bio
        mock_person = Mock()
        mock_person.id = 1
        mock_person.name = "John Doe"
        mock_person.importance_score = 8.5
        mock_person.email = "john@example.com"
        mock_person.bio = "This is a very long bio that should be truncated when displayed"

        mock_db.exec.return_value.all.return_value = [mock_person]

        _show_entities_by_type(mock_db, 1, "people")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_people_empty(self, mock_console):
        """Test _show_entities_by_type for people with no data"""
        mock_db = MagicMock()

        mock_db.exec.return_value.all.return_value = []

        _show_entities_by_type(mock_db, 1, "people")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_projects(self, mock_console):
        """Test _show_entities_by_type for projects"""
        mock_db = MagicMock()

        # Mock project with description
        mock_project = Mock()
        mock_project.id = 1
        mock_project.name = "AI Project"
        mock_project.status = "active"
        mock_project.priority_score = 9.0
        mock_project.deadline = datetime(2024, 12, 31)
        mock_project.description = "This is a very long description that should be truncated when displayed"

        mock_db.exec.return_value.all.return_value = [mock_project]

        _show_entities_by_type(mock_db, 1, "projects")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_projects_empty(self, mock_console):
        """Test _show_entities_by_type for projects with no data"""
        mock_db = MagicMock()

        mock_db.exec.return_value.all.return_value = []

        _show_entities_by_type(mock_db, 1, "projects")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_topics(self, mock_console):
        """Test _show_entities_by_type for topics"""
        mock_db = MagicMock()

        # Mock topic with description
        mock_topic = Mock()
        mock_topic.id = 1
        mock_topic.name = "Machine Learning"
        mock_topic.category = "Technology"
        mock_topic.research_score = 7.5
        mock_topic.description = "This is a very long description that should be truncated when displayed"

        mock_db.exec.return_value.all.return_value = [mock_topic]

        _show_entities_by_type(mock_db, 1, "topics")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_topics_empty(self, mock_console):
        """Test _show_entities_by_type for topics with no data"""
        mock_db = MagicMock()

        mock_db.exec.return_value.all.return_value = []

        _show_entities_by_type(mock_db, 1, "topics")

        assert mock_console.print.called

    @patch('gfcli.dashboard.console')
    def test_show_entities_by_type_invalid(self, mock_console):
        """Test _show_entities_by_type for invalid type"""
        mock_db = MagicMock()

        _show_entities_by_type(mock_db, 1, "invalid_type")

        assert mock_console.print.called

    def test_get_user_stats(self):
        """Test _get_user_stats function"""
        mock_db = MagicMock()

        # Mock the database queries in order they are called
        mock_db.exec.return_value.one.side_effect = [
            5,      # note count
            1000,   # total chars (not None in this test)
            2,      # pending suggestions
            8,      # confirmed entities
            10,     # total suggestions
            3,      # people count
            2,      # projects count
            1       # topics count
        ]

        # Mock latest note
        mock_note = Mock()
        mock_note.created_at = datetime(2024, 1, 1)
        mock_db.exec.return_value.first.return_value = mock_note

        stats = _get_user_stats(mock_db, 1)

        assert stats['notes'] == 5
        assert stats['total_chars'] == 1000
        assert stats['latest_note'] == '2024-01-01'
        assert stats['pending_suggestions'] == 2
        assert stats['confirmed_entities'] == 8
        assert stats['accuracy_rate'] == 80.0  # 8/10 * 100
        assert stats['people'] == 3
        assert stats['projects'] == 2
        assert stats['topics'] == 1

    def test_get_user_stats_no_notes(self):
        """Test _get_user_stats function with no notes"""
        mock_db = MagicMock()

        # Mock the database queries
        mock_db.exec.return_value.one.side_effect = [
            0,      # note count
            0,      # total chars
            0,      # pending suggestions
            0,      # confirmed entities
            0,      # total suggestions
            0,      # people count
            0,      # projects count
            0       # topics count
        ]

        # Mock no latest note
        mock_db.exec.return_value.first.return_value = None

        stats = _get_user_stats(mock_db, 1)

        assert stats['notes'] == 0
        assert stats['total_chars'] == 0
        assert stats['latest_note'] == 'Never'
        assert stats['pending_suggestions'] == 0
        assert stats['confirmed_entities'] == 0
        assert stats['accuracy_rate'] == 0  # 0/0 handled as 0
        assert stats['people'] == 0
        assert stats['projects'] == 0
        assert stats['topics'] == 0

    def test_get_user_stats_none_total_chars(self):
        """Test _get_user_stats function with None total_chars"""
        mock_db = MagicMock()

        # Mock the database queries with None for total chars
        mock_db.exec.return_value.one.side_effect = [
            5,      # note count
            None,   # total chars returns None (sum of empty result)
            0,      # pending suggestions
            0,      # confirmed entities
            0,      # total suggestions
            0,      # people count
            0,      # projects count
            0       # topics count
        ]

        # Mock latest note
        mock_note = Mock()
        mock_note.created_at = datetime(2024, 1, 1)
        mock_db.exec.return_value.first.return_value = mock_note

        stats = _get_user_stats(mock_db, 1)

        assert stats['notes'] == 5
        assert stats['total_chars'] == 0  # None becomes 0 due to `or 0`
        assert stats['latest_note'] == '2024-01-01'

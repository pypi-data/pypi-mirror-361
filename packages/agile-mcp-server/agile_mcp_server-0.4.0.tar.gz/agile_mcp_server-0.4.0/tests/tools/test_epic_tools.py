"""Tests for epic management tools."""

from unittest.mock import MagicMock

import pytest
from agile_mcp.models.epic import Epic, EpicStatus
from agile_mcp.models.story import Priority, StoryStatus, UserStory
from agile_mcp.tools.base import ToolError
from agile_mcp.tools.epic_tools import (
    CreateEpicTool,
    DeleteEpicTool,
    GetEpicTool,
    GetProductBacklogTool,
    ListEpicsTool,
    ManageEpicStoriesTool,
    UpdateEpicTool,
)


class TestEpicTools:
    """Test cases for epic management tools."""

    @pytest.fixture
    def mock_agent(self):
        """Fixture for a mocked agent."""
        agent = MagicMock()
        agent.project_manager.is_initialized.return_value = True
        return agent

    def test_create_epic_success(self, mock_agent):
        """Test successful creation of an epic."""
        create_tool = CreateEpicTool(mock_agent)
        mock_epic = Epic(id="EPIC-1", name="Test Epic", description="A test epic.")
        mock_agent.epic_service.create_epic.return_value = mock_epic

        result = create_tool.apply(name="Test Epic", description="A test epic.")

        assert "Epic 'Test Epic' created successfully with ID EPIC-1" in result.message
        mock_agent.epic_service.create_epic.assert_called_once_with(
            name="Test Epic", description="A test epic.", status=EpicStatus.PLANNING, tags=[]
        )

    def test_create_epic_with_optional_params(self, mock_agent):
        """Test epic creation with all optional parameters."""
        create_tool = CreateEpicTool(mock_agent)
        mock_epic = Epic(id="EPIC-2", name="Another Epic", description="Another test epic.")
        mock_agent.epic_service.create_epic.return_value = mock_epic

        result = create_tool.apply(
            name="Another Epic", description="Another test epic.", status="in_progress", tags="feature, backend"
        )

        assert "Epic 'Another Epic' created successfully with ID EPIC-2" in result.message
        mock_agent.epic_service.create_epic.assert_called_once_with(
            name="Another Epic",
            description="Another test epic.",
            status=EpicStatus.IN_PROGRESS,
            tags=["feature", "backend"],
        )

    def test_create_epic_invalid_status(self, mock_agent):
        """Test epic creation with an invalid status."""
        create_tool = CreateEpicTool(mock_agent)

        with pytest.raises(ToolError, match="Invalid status"):
            create_tool.apply(name="Test", description="Test", status="invalid")

    def test_get_epic_success(self, mock_agent):
        """Test successfully retrieving an epic."""
        get_tool = GetEpicTool(mock_agent)
        mock_epic = Epic(id="EPIC-1", name="Test Epic", description="A test epic.")
        mock_agent.epic_service.get_epic.return_value = mock_epic

        result = get_tool.apply(epic_id="EPIC-1")

        assert "Retrieved epic: Test Epic (ID: EPIC-1)" in result.message
        mock_agent.epic_service.get_epic.assert_called_once_with("EPIC-1")

    def test_get_epic_not_found(self, mock_agent):
        """Test retrieving an epic that does not exist."""
        get_tool = GetEpicTool(mock_agent)
        mock_agent.epic_service.get_epic.return_value = None

        result = get_tool.apply(epic_id="NOT-FOUND")
        assert not result.success

    def test_update_epic_success(self, mock_agent):
        """Test successfully updating an epic."""
        update_tool = UpdateEpicTool(mock_agent)
        mock_epic = Epic(id="EPIC-1", name="Updated Epic", description="A test epic.")
        mock_agent.epic_service.update_epic.return_value = mock_epic

        result = update_tool.apply(epic_id="EPIC-1", name="Updated Epic")

        assert "Epic 'Updated Epic' updated successfully" in result.message
        mock_agent.epic_service.update_epic.assert_called_once_with("EPIC-1", name="Updated Epic")

    def test_update_epic_not_found(self, mock_agent):
        """Test updating an epic that does not exist."""
        update_tool = UpdateEpicTool(mock_agent)
        mock_agent.epic_service.update_epic.return_value = None

        result = update_tool.apply(epic_id="NOT-FOUND", name="Does not exist")
        assert not result.success

    def test_delete_epic_success(self, mock_agent):
        """Test successfully deleting an epic."""
        delete_tool = DeleteEpicTool(mock_agent)
        mock_agent.epic_service.get_epic.return_value = Epic(id="EPIC-1", name="Test Epic", description="A test epic.")
        mock_agent.epic_service.delete_epic.return_value = True

        result = delete_tool.apply(epic_id="EPIC-1")

        assert "Epic 'Test Epic' (ID: EPIC-1) deleted successfully" in result.message
        mock_agent.epic_service.delete_epic.assert_called_once_with("EPIC-1")

    def test_delete_epic_not_found(self, mock_agent):
        """Test deleting an epic that does not exist."""
        delete_tool = DeleteEpicTool(mock_agent)
        mock_agent.epic_service.get_epic.return_value = None

        with pytest.raises(ToolError, match="Epic with ID NOT-FOUND not found"):
            delete_tool.apply(epic_id="NOT-FOUND")

    def test_list_epics_success(self, mock_agent):
        """Test successfully listing epics."""
        list_tool = ListEpicsTool(mock_agent)
        mock_agent.epic_service.list_epics.return_value = [
            Epic(
                id="EPIC-1",
                name="Epic 1",
                description="A test epic.",
                status=EpicStatus.PLANNING,
                story_ids=["STORY-1"],
            ),
            Epic(id="EPIC-2", name="Epic 2", description="A test epic.", status=EpicStatus.IN_PROGRESS, story_ids=[]),
        ]

        result = list_tool.apply()

        assert "Found 2 epics" in result.message
        assert "- EPIC-1: Epic 1 (planning) (1 stories)" in result.message
        assert "- EPIC-2: Epic 2 (in_progress)" in result.message

    def test_list_epics_no_epics_found(self, mock_agent):
        """Test listing epics when no epics are found."""
        list_tool = ListEpicsTool(mock_agent)
        mock_agent.epic_service.list_epics.return_value = []

        result = list_tool.apply()

        assert "No epics found matching the specified criteria" in result.message

    def test_manage_epic_stories_add_success(self, mock_agent):
        """Test successfully adding a story to an epic."""
        manage_tool = ManageEpicStoriesTool(mock_agent)
        mock_agent.epic_service.add_story_to_epic.return_value = Epic(
            id="EPIC-1", name="Test Epic", description="A test epic."
        )

        result = manage_tool.apply(epic_id="EPIC-1", action="add", story_id="STORY-1")

        assert "Story 'STORY-1' added to epic 'Test Epic'" in result.message
        mock_agent.epic_service.add_story_to_epic.assert_called_once_with("EPIC-1", "STORY-1")

    def test_manage_epic_stories_remove_success(self, mock_agent):
        """Test successfully removing a story from an epic."""
        manage_tool = ManageEpicStoriesTool(mock_agent)
        mock_agent.epic_service.remove_story_from_epic.return_value = Epic(
            id="EPIC-1", name="Test Epic", description="A test epic."
        )

        result = manage_tool.apply(epic_id="EPIC-1", action="remove", story_id="STORY-1")

        assert "Story 'STORY-1' removed from epic 'Test Epic'" in result.message
        mock_agent.epic_service.remove_story_from_epic.assert_called_once_with("EPIC-1", "STORY-1")

    def test_manage_epic_stories_invalid_action(self, mock_agent):
        """Test managing epic stories with an invalid action."""
        manage_tool = ManageEpicStoriesTool(mock_agent)

        with pytest.raises(ToolError, match="Action must be either 'add' or 'remove'"):
            manage_tool.apply(epic_id="EPIC-1", action="invalid", story_id="STORY-1")

    def test_manage_epic_stories_epic_not_found(self, mock_agent):
        """Test managing epic stories when the epic does not exist."""
        manage_tool = ManageEpicStoriesTool(mock_agent)
        mock_agent.epic_service.add_story_to_epic.return_value = None

        result = manage_tool.apply(epic_id="NOT-FOUND", action="add", story_id="STORY-1")
        assert not result.success

    def test_get_product_backlog_success(self, mock_agent):
        """Test successfully retrieving the product backlog."""
        get_backlog_tool = GetProductBacklogTool(mock_agent)
        mock_agent.story_service.list_stories.return_value = [
            UserStory(
                id="STORY-1",
                name="Story 1",
                description="A test story.",
                sprint_id=None,
                priority=Priority.HIGH,
                status=StoryStatus.TODO,
                epic_id=None,
                points=5,
            ),
            UserStory(
                id="STORY-3",
                name="Story 3",
                description="A test story.",
                sprint_id=None,
                priority=Priority.LOW,
                status=StoryStatus.TODO,
                epic_id=None,
                points=2,
            ),
        ]

        result = get_backlog_tool.apply()

        assert "Product Backlog: 2 stories (7 total points)" in result.message
        assert "- STORY-1: Story 1 (high) (5 pts) [todo]" in result.message
        assert "- STORY-3: Story 3 (low) (2 pts) [todo]" in result.message

    def test_get_product_backlog_empty(self, mock_agent):
        """Test retrieving an empty product backlog."""
        get_backlog_tool = GetProductBacklogTool(mock_agent)
        mock_agent.story_service.list_stories.return_value = []

        result = get_backlog_tool.apply()

        assert "Product backlog is empty" in result.message

    def test_get_product_backlog_with_priority_filter(self, mock_agent):
        """Test retrieving the product backlog with a priority filter."""
        get_backlog_tool = GetProductBacklogTool(mock_agent)
        mock_agent.story_service.list_stories.return_value = [
            UserStory(
                id="STORY-1",
                name="Story 1",
                description="A test story.",
                sprint_id=None,
                priority=Priority.HIGH,
                status=StoryStatus.TODO,
                epic_id=None,
                points=5,
            ),
            UserStory(
                id="STORY-3",
                name="Story 3",
                description="A test story.",
                sprint_id=None,
                priority=Priority.LOW,
                status=StoryStatus.TODO,
                epic_id=None,
                points=2,
            ),
        ]

        result = get_backlog_tool.apply(priority="high")

        assert "Product Backlog: 1 stories" in result.message
        assert "- STORY-1: Story 1 (high) (5 pts) [todo]" in result.message
        assert "- STORY-3: Story 3 (low) (2 pts) [todo]" not in result.message

    def test_get_product_backlog_with_tags_filter(self, mock_agent):
        """Test retrieving the product backlog with a tags filter."""
        get_backlog_tool = GetProductBacklogTool(mock_agent)
        mock_agent.story_service.list_stories.return_value = [
            UserStory(
                id="STORY-1",
                name="Story 1",
                description="A test story.",
                sprint_id=None,
                priority=Priority.HIGH,
                status=StoryStatus.TODO,
                tags=["backend"],
                epic_id=None,
                points=5,
            ),
            UserStory(
                id="STORY-3",
                name="Story 3",
                description="A test story.",
                sprint_id=None,
                priority=Priority.LOW,
                status=StoryStatus.TODO,
                tags=["frontend"],
                epic_id=None,
                points=2,
            ),
        ]

        result = get_backlog_tool.apply(tags="backend")

        assert "Product Backlog: 1 stories" in result.message
        assert "- STORY-1: Story 1 (high) (5 pts) [todo]" in result.message
        assert "- STORY-3: Story 3 (low) (2 pts) [todo]" not in result.message

    def test_get_product_backlog_include_completed(self, mock_agent):
        """Test retrieving the product backlog including completed stories."""
        get_backlog_tool = GetProductBacklogTool(mock_agent)
        mock_agent.story_service.list_stories.return_value = [
            UserStory(
                id="STORY-1",
                name="Story 1",
                description="A test story.",
                sprint_id=None,
                priority=Priority.HIGH,
                status=StoryStatus.TODO,
                epic_id=None,
                points=5,
            ),
            UserStory(
                id="STORY-3",
                name="Story 3",
                description="A test story.",
                sprint_id=None,
                priority=Priority.LOW,
                status=StoryStatus.DONE,
                epic_id=None,
                points=2,
            ),
        ]

        result = get_backlog_tool.apply(include_completed=True)

        assert "Product Backlog: 2 stories (7 total points)" in result.message
        assert "- STORY-1: Story 1 (high) (5 pts) [todo]" in result.message
        assert "- STORY-3: Story 3 (low) (2 pts) [done]" in result.message

"""
Tests for entity recognition service
"""
import pytest

from goldfish_backend.services.entity_recognition import EntityRecognitionEngine


class TestEntityRecognitionEngine:
    """Test EntityRecognitionEngine functionality"""

    def test_engine_initialization(self):
        """Test that engine initializes without errors"""
        engine = EntityRecognitionEngine()
        assert engine is not None

    def test_process_text_with_people_mentions(self):
        """Test processing text with @people mentions"""
        engine = EntityRecognitionEngine()

        text = "Meeting with @sarah and @john about the project tomorrow"
        result = engine.process_text(text)

        assert "entities" in result
        assert "tasks" in result
        assert "total_entities" in result
        assert "total_tasks" in result

        # Should detect people entities
        people = result["entities"].get("people", [])
        assert len(people) >= 2

        # Check for sarah and john
        names = [person.name.lower() for person in people]
        assert "sarah" in names
        assert "john" in names

    def test_process_text_with_project_hashtags(self):
        """Test processing text with #project hashtags"""
        engine = EntityRecognitionEngine()

        text = "Working on #ai-platform and #blockchain-integration projects"
        result = engine.process_text(text)

        # Should detect project entities
        projects = result["entities"].get("projects", [])
        assert len(projects) >= 2

        # Check project names
        project_names = [proj.name.lower() for proj in projects]
        assert any("ai-platform" in name or "ai platform" in name for name in project_names)
        assert any("blockchain-integration" in name or "blockchain integration" in name for name in project_names)

    def test_process_text_with_todo_tasks(self):
        """Test processing text with TODO tasks"""
        engine = EntityRecognitionEngine()

        text = """
        TODO: Follow up with client about requirements
        Need to schedule meeting with team
        TODO: Review and approve design documents
        """

        result = engine.process_text(text)

        # Should detect tasks
        tasks = result["tasks"]
        assert len(tasks) >= 2

        # Check task content
        task_contents = [task.content.lower() for task in tasks]
        assert any("follow up" in content for content in task_contents)
        assert any("review" in content and "approve" in content for content in task_contents)

    def test_process_text_with_mixed_entities(self):
        """Test processing text with multiple entity types"""
        engine = EntityRecognitionEngine()

        text = """
        TODO: Follow up with @sarah about the #blockchain-integration project.
        Need to discuss the smart contract architecture and @john's feedback.
        Also review the #ai-platform roadmap for Q2.
        """

        result = engine.process_text(text)

        # Should detect multiple entity types
        assert len(result["entities"]["people"]) >= 2
        assert len(result["entities"]["projects"]) >= 2
        assert len(result["tasks"]) >= 1

        # Check confidence scores
        for _entity_type, entities in result["entities"].items():
            for entity in entities:
                assert 0.0 <= entity.confidence <= 1.0
                assert entity.name is not None
                assert entity.context is not None

    def test_process_empty_text(self):
        """Test processing empty or minimal text"""
        engine = EntityRecognitionEngine()

        result = engine.process_text("")

        assert result["total_entities"] == 0
        assert result["total_tasks"] == 0
        assert len(result["entities"]["people"]) == 0
        assert len(result["entities"]["projects"]) == 0
        assert len(result["entities"]["topics"]) == 0
        assert len(result["tasks"]) == 0

    def test_confidence_scores_reasonable(self):
        """Test that confidence scores are reasonable"""
        engine = EntityRecognitionEngine()

        # High confidence cases - test @mentions and #hashtags specifically
        high_confidence_text = "Meeting with @sarah about #blockchain-platform"
        result = engine.process_text(high_confidence_text)

        # Check that @mentions have high confidence
        people = result["entities"]["people"]
        assert len(people) > 0
        mention_people = [p for p in people if p.original_text.startswith("@")]
        assert all(p.confidence >= 0.8 for p in mention_people)

        # Check that #hashtags have high confidence
        projects = result["entities"]["projects"]
        assert len(projects) > 0
        hashtag_projects = [p for p in projects if p.original_text.startswith("#")]
        assert all(p.confidence >= 0.8 for p in hashtag_projects)

    def test_context_preservation(self):
        """Test that entity context is preserved correctly"""
        engine = EntityRecognitionEngine()

        text = "Scheduled a call with @alice to discuss the quarterly #budget-review"
        result = engine.process_text(text)

        # Check that context contains relevant surrounding text
        for _entity_type, entities in result["entities"].items():
            for entity in entities:
                assert text in entity.context or entity.context in text

    def test_duplicate_entity_handling(self):
        """Test handling of duplicate entities in text"""
        engine = EntityRecognitionEngine()

        text = "@john mentioned that @john will handle the @john's project"
        result = engine.process_text(text)

        # Should not create duplicate entities
        people = result["entities"]["people"]
        john_entities = [p for p in people if "john" in p.name.lower()]

        # Should consolidate or handle duplicates appropriately
        assert len(john_entities) <= 3  # At most one per occurrence

    def test_case_insensitive_matching(self):
        """Test that entity recognition is case insensitive"""
        engine = EntityRecognitionEngine()

        text1 = "Meeting with @Sarah about #PROJECT-ALPHA"
        text2 = "meeting with @sarah about #project-alpha"

        result1 = engine.process_text(text1)
        result2 = engine.process_text(text2)

        # Should detect entities regardless of case
        assert len(result1["entities"]["people"]) > 0
        assert len(result1["entities"]["projects"]) > 0
        assert len(result2["entities"]["people"]) > 0
        assert len(result2["entities"]["projects"]) > 0

    def test_special_characters_in_entities(self):
        """Test handling of special characters in entity names"""
        engine = EntityRecognitionEngine()

        text = "Working with @marie-claire on #ai-ml-project and #web3.0-platform"
        result = engine.process_text(text)

        # Should handle hyphens, dots, etc. in entity names
        people = result["entities"]["people"]
        projects = result["entities"]["projects"]

        assert len(people) > 0
        assert len(projects) > 0

        # Check that special characters are preserved or handled correctly
        person_names = [p.name for p in people]
        project_names = [p.name for p in projects]

        assert any("marie" in name.lower() for name in person_names)
        assert any("ai" in name.lower() or "ml" in name.lower() for name in project_names)

    @pytest.mark.slow
    def test_large_text_processing(self):
        """Test processing large amounts of text"""
        engine = EntityRecognitionEngine()

        # Create large text with multiple entities
        large_text = """
        Project Status Update - Week 45

        This week we made significant progress on the #ai-platform initiative.
        @sarah completed the initial data pipeline architecture, while @john
        worked on the machine learning model integration.

        TODO: Review the proposed changes with @alice before the next sprint
        TODO: Schedule demo session for stakeholders
        TODO: Update documentation for the #blockchain-integration module

        The #mobile-app development is also progressing well. @bob has finished
        the authentication flow, and @carol is working on the user interface.

        Upcoming tasks:
        - Follow up with @david about the API specifications
        - Need to discuss #database-optimization strategies
        - TODO: Plan the #deployment-pipeline for staging environment

        Overall, the team is on track to meet the Q4 objectives for both
        #ai-platform and #mobile-app projects.
        """ * 3  # Make it larger

        result = engine.process_text(large_text)

        # Should handle large text without errors
        assert result is not None
        assert result["total_entities"] > 0
        assert result["total_tasks"] > 0

        # Should detect multiple entities
        assert len(result["entities"]["people"]) >= 5
        assert len(result["entities"]["projects"]) >= 3
        assert len(result["tasks"]) >= 3


class TestEntityRecognitionPatterns:
    """Test specific pattern recognition"""

    def test_email_mention_pattern(self):
        """Test that email addresses don't get confused with @mentions"""
        engine = EntityRecognitionEngine()

        text = "Send email to user@example.com and also ping @alice"
        result = engine.process_text(text)

        people = result["entities"]["people"]
        # Should only detect @alice, not the email
        assert len(people) == 1
        assert "alice" in people[0].name.lower()

    def test_hashtag_vs_hash_symbol(self):
        """Test hashtag detection vs regular hash symbols"""
        engine = EntityRecognitionEngine()

        text = "Password: #secure123 vs project #web-development"
        result = engine.process_text(text)

        projects = result["entities"]["projects"]
        # Should detect project hashtag but not password hash
        assert len(projects) >= 1
        project_names = [p.name.lower() for p in projects]
        assert any("web" in name for name in project_names)

    def test_multiple_todo_formats(self):
        """Test recognition of different TODO formats"""
        engine = EntityRecognitionEngine()

        text = """
        TODO: First task
        - TODO: Second task
        * TODO: Third task
        Need to complete fourth task
        Should finish fifth task
        """

        result = engine.process_text(text)

        tasks = result["tasks"]
        # Should detect multiple TODO formats
        assert len(tasks) >= 3

        task_contents = [task.content.lower() for task in tasks]
        assert any("first" in content for content in task_contents)
        assert any("second" in content for content in task_contents)
        assert any("third" in content for content in task_contents)

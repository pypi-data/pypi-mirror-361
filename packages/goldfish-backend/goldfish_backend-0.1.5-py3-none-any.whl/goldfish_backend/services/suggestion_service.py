"""
Suggestion service for human-in-the-loop entity verification
"""
from typing import Any

from sqlalchemy import desc
from sqlmodel import Session, select

try:
    from fastapi import HTTPException, status
except ImportError:
    # FastAPI not available - CLI mode
    HTTPException = None
    status = None

from ..models.entity_learning import EntityLearning
from ..models.person import Person
from ..models.project import Project
from ..models.suggested_entity import SuggestedEntity
from ..models.topic import Topic
from .entity_recognition import EntityRecognitionEngine


class SuggestionService:
    """Service for managing entity suggestions and human verification"""

    def __init__(self, db: Session):
        self.db = db
        self.recognition_engine = EntityRecognitionEngine()

    def create_suggestions_from_text(self, text: str, note_id: int, user_id: int) -> list[SuggestedEntity]:
        """Process text and create entity suggestions"""
        result = self.recognition_engine.process_text(text)
        suggestions = []

        # Create suggestions for all entity types
        for entity_type, entities in result["entities"].items():
            for entity in entities:
                # Convert plural entity type to singular
                singular_type = self._pluralize_to_singular(entity_type)

                # Skip if we already have a suggestion for this entity in this note
                existing = self.get_suggestion_by_name_and_note(
                    entity.name, singular_type, note_id, user_id
                )
                if existing:
                    continue

                suggestion = SuggestedEntity(
                    user_id=user_id,
                    note_id=note_id,
                    entity_type=singular_type,
                    name=entity.name,
                    context=entity.context,
                    confidence=entity.confidence,
                    status="pending",
                    ai_metadata={
                        "original_text": entity.original_text,
                        "start_pos": entity.start_pos,
                        "end_pos": entity.end_pos,
                        "pattern_type": "regex" if entity.confidence > 0.8 else "natural_language"
                    }
                )

                self.db.add(suggestion)
                suggestions.append(suggestion)

        self.db.commit()
        return suggestions

    def get_pending_suggestions(self, user_id: int, limit: int | None = None) -> list[SuggestedEntity]:
        """Get all pending suggestions for a user"""
        statement = select(SuggestedEntity).where(
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.status == "pending"
        ).order_by(desc(SuggestedEntity.confidence))  # type: ignore

        if limit:
            statement = statement.limit(limit)

        return list(self.db.exec(statement).all())

    def get_suggestions_by_note(self, note_id: int, user_id: int) -> list[SuggestedEntity]:
        """Get all suggestions for a specific note"""
        statement = select(SuggestedEntity).where(
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.note_id == note_id
        ).order_by(desc(SuggestedEntity.confidence))  # type: ignore

        return list(self.db.exec(statement).all())

    def get_suggestion_by_name_and_note(self, name: str, entity_type: str, note_id: int, user_id: int) -> SuggestedEntity | None:
        """Check if suggestion already exists for this entity in this note"""
        statement = select(SuggestedEntity).where(
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.note_id == note_id,
            SuggestedEntity.entity_type == entity_type,
            SuggestedEntity.name == name
        )

        return self.db.exec(statement).first()

    def confirm_suggestion(self, suggestion_id: int, user_id: int, create_new: bool = True, existing_entity_id: int | None = None) -> int | None:
        """Confirm a suggestion and optionally create the entity or link to existing"""
        suggestion = self._get_suggestion_by_id(suggestion_id, user_id)

        if create_new:
            entity_id = self._create_entity_from_suggestion(suggestion)
        elif existing_entity_id:
            # Link to existing entity
            entity_id = existing_entity_id
            # Add the suggested name as an alias if it's different
            self._add_alias_to_existing_entity(suggestion, existing_entity_id)
        else:
            entity_id = None

        # Mark suggestion as confirmed
        suggestion.status = "confirmed"

        # Create learning record
        ai_metadata = suggestion.ai_metadata or {}
        learning = EntityLearning(
            user_id=user_id,
            original_text=ai_metadata.get("original_text", suggestion.name),
            linked_entity_id=entity_id or 0,
            entity_type=suggestion.entity_type,
            context=suggestion.context,
            source_file_path="",  # Would get from note
            confidence=1.0,  # High confidence for confirmed suggestions
            learning_metadata={
                "suggestion_id": suggestion_id,
                "action": "create_new" if create_new else "link_existing",
                "existing_entity_id": existing_entity_id
            }
        )

        self.db.add(learning)
        self.db.commit()

        return entity_id

    def reject_suggestion(self, suggestion_id: int, user_id: int) -> bool:
        """Reject a suggestion"""
        suggestion = self._get_suggestion_by_id(suggestion_id, user_id)

        suggestion.status = "rejected"

        # Create learning record for rejection
        ai_metadata = suggestion.ai_metadata or {}
        learning = EntityLearning(
            user_id=user_id,
            original_text=ai_metadata.get("original_text", suggestion.name),
            linked_entity_id=0,  # No entity created
            entity_type=suggestion.entity_type,
            context=suggestion.context,
            source_file_path="",  # Would get from note
            confidence=0.0,  # Low confidence for rejected suggestions
            learning_metadata={
                "suggestion_id": suggestion_id,
                "action": "rejected"
            }
        )

        self.db.add(learning)
        self.db.commit()

        return True

    def approve_suggestion(self, suggestion_id: int, user_id: int) -> Person | Project | Topic | None:
        """Alias for confirm_suggestion for backward compatibility"""
        entity_id = self.confirm_suggestion(suggestion_id, user_id, create_new=True)
        if entity_id:
            # Return the created entity
            suggestion = self._get_suggestion_by_id_no_status_check(suggestion_id, user_id)
            if suggestion.entity_type == "person":
                return self.db.get(Person, entity_id)
            elif suggestion.entity_type == "project":
                return self.db.get(Project, entity_id)
            elif suggestion.entity_type == "topic":
                return self.db.get(Topic, entity_id)
        return None

    def _get_suggestion_by_id_no_status_check(self, suggestion_id: int, user_id: int) -> SuggestedEntity:
        """Get suggestion by ID without status check"""
        statement = select(SuggestedEntity).where(
            SuggestedEntity.id == suggestion_id,
            SuggestedEntity.user_id == user_id
        )

        suggestion = self.db.exec(statement).first()
        if not suggestion:
            if HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Suggestion not found"
                )
            else:
                raise ValueError("Suggestion not found")

        return suggestion

    def _get_suggestion_by_id(self, suggestion_id: int, user_id: int) -> SuggestedEntity:
        """Get suggestion by ID with user validation"""
        statement = select(SuggestedEntity).where(
            SuggestedEntity.id == suggestion_id,
            SuggestedEntity.user_id == user_id,
            SuggestedEntity.status == "pending"
        )

        suggestion = self.db.exec(statement).first()
        if not suggestion:
            if HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Suggestion not found or already processed"
                )
            else:
                raise ValueError("Suggestion not found or already processed")

        return suggestion

    def _create_entity_from_suggestion(self, suggestion: SuggestedEntity) -> int:
        """Create a new entity from a confirmed suggestion"""
        entity: Person | Project | Topic
        if suggestion.entity_type == "person":
            entity = Person(
                user_id=suggestion.user_id,
                name=suggestion.name,
                aliases=[],
                importance_score=1.0
            )
        elif suggestion.entity_type == "project":
            entity = Project(
                user_id=suggestion.user_id,
                name=suggestion.name,
                aliases=[],
                status="active",
                priority_score=1.0
            )
        elif suggestion.entity_type == "topic":
            entity = Topic(
                user_id=suggestion.user_id,
                name=suggestion.name,
                aliases=[],
                research_score=1.0
            )
        else:
            if HTTPException:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unknown entity type: {suggestion.entity_type}"
                )
            else:
                raise ValueError(f"Unknown entity type: {suggestion.entity_type}")

        self.db.add(entity)
        self.db.flush()  # Get the ID
        entity_id = entity.id
        if entity_id is None:
            raise ValueError("Entity ID is None after flush")
        return entity_id

    def get_confirmation_status(self, note_id: int, user_id: int) -> dict[str, Any]:
        """Get confirmation status for a note"""
        suggestions = self.get_suggestions_by_note(note_id, user_id)

        total = len(suggestions)
        confirmed = len([s for s in suggestions if s.status == "confirmed"])
        rejected = len([s for s in suggestions if s.status == "rejected"])
        pending = len([s for s in suggestions if s.status == "pending"])

        return {
            "total_suggestions": total,
            "confirmed": confirmed,
            "rejected": rejected,
            "pending": pending,
            "is_complete": pending == 0,
            "completion_percentage": (confirmed + rejected) / total * 100 if total > 0 else 100
        }

    def find_existing_entities(self, suggestion: SuggestedEntity, limit: int = 10) -> list[dict[str, Any]]:
        """Find existing entities that could match the suggestion"""
        results = []

        if suggestion.entity_type == "person":
            person_statement = select(Person).where(
                Person.user_id == suggestion.user_id,
                Person.is_deleted == False
            ).order_by(desc(Person.importance_score)).limit(limit)  # type: ignore

            person_entities = self.db.exec(person_statement).all()
            for person_entity in person_entities:
                # Calculate match score based on name similarity
                score = self._calculate_name_similarity(suggestion.name, person_entity.name)
                # Also check aliases
                for alias in person_entity.aliases:
                    alias_score = self._calculate_name_similarity(suggestion.name, alias)
                    score = max(score, alias_score)

                results.append({
                    "id": person_entity.id,
                    "name": person_entity.name,
                    "aliases": person_entity.aliases,
                    "match_score": score,
                    "entity_type": "person"
                })

        elif suggestion.entity_type == "project":
            project_statement = select(Project).where(
                Project.user_id == suggestion.user_id,
                Project.is_deleted == False
            ).order_by(desc(Project.priority_score)).limit(limit)  # type: ignore

            project_entities = self.db.exec(project_statement).all()
            for project_entity in project_entities:
                score = self._calculate_name_similarity(suggestion.name, project_entity.name)
                for alias in project_entity.aliases:
                    alias_score = self._calculate_name_similarity(suggestion.name, alias)
                    score = max(score, alias_score)

                results.append({
                    "id": project_entity.id,
                    "name": project_entity.name,
                    "aliases": project_entity.aliases,
                    "match_score": score,
                    "entity_type": "project",
                    "status": project_entity.status
                })

        elif suggestion.entity_type == "topic":
            topic_statement = select(Topic).where(
                Topic.user_id == suggestion.user_id,
                Topic.is_deleted == False
            ).order_by(desc(Topic.research_score)).limit(limit)  # type: ignore

            topic_entities = self.db.exec(topic_statement).all()
            for topic_entity in topic_entities:
                score = self._calculate_name_similarity(suggestion.name, topic_entity.name)
                for alias in topic_entity.aliases:
                    alias_score = self._calculate_name_similarity(suggestion.name, alias)
                    score = max(score, alias_score)

                results.append({
                    "id": topic_entity.id,
                    "name": topic_entity.name,
                    "aliases": topic_entity.aliases,
                    "match_score": score,
                    "entity_type": "topic"
                })

        # Sort by match score descending
        results.sort(key=lambda x: float(x["match_score"]) if isinstance(x["match_score"], int | float) else 0.0, reverse=True)
        return results

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names (simple implementation)"""
        name1_lower = name1.lower().strip()
        name2_lower = name2.lower().strip()

        # Exact match
        if name1_lower == name2_lower:
            return 1.0

        # Contains match
        if name1_lower in name2_lower or name2_lower in name1_lower:
            return 0.8

        # Word overlap
        words1 = set(name1_lower.split())
        words2 = set(name2_lower.split())

        if words1.intersection(words2):
            overlap = len(words1.intersection(words2))
            total = len(words1.union(words2))
            return 0.5 + (overlap / total) * 0.3

        return 0.0

    def _add_alias_to_existing_entity(self, suggestion: SuggestedEntity, entity_id: int) -> None:
        """Add suggestion name as alias to existing entity if it's different"""
        entity: Person | Project | Topic | None = None
        if suggestion.entity_type == "person":
            entity = self.db.get(Person, entity_id)
        elif suggestion.entity_type == "project":
            entity = self.db.get(Project, entity_id)
        elif suggestion.entity_type == "topic":
            entity = self.db.get(Topic, entity_id)
        else:
            return

        if entity and suggestion.name.lower() != entity.name.lower():
            # Add as alias if not already present
            if suggestion.name not in entity.aliases:
                entity.aliases.append(suggestion.name)
                self.db.add(entity)  # Mark as dirty for commit

    def _pluralize_to_singular(self, entity_type: str) -> str:
        """Convert plural entity type to singular form"""
        type_mapping = {
            "people": "person",
            "projects": "project",
            "topics": "topic"
        }
        return type_mapping.get(entity_type, entity_type.rstrip("s"))

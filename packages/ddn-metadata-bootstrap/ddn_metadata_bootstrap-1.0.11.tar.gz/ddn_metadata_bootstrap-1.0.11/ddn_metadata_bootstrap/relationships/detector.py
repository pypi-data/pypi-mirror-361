#!/usr/bin/env python3

"""
Relationship detection logic for identifying connections between schema entities.
Analyzes foreign keys, shared fields, and naming patterns to detect relationships.
Only detects relationships between ObjectTypes that are queryable (have Models or Query Commands).

Key improvements:
- Minimum confidence threshold to prevent spurious FK relationships
- camelCase to snake_case conversion for comprehensive field analysis (analysis only)
- Always preserves original field names in relationship data
- Centralized validation to prevent Commands from being relationship targets
- ENHANCED: FK-aware shared field filtering to prevent redundant relationships
- FIXED: Strict semantic matching for FK relationships to prevent spurious matches
- ENHANCED: GraphQL type compatibility checking for relationship validation
- ENHANCED: Only STRING and INTEGER types support relationships (practical key types)
- FIXED: Conservative primitive type detection to prevent object type false positives
"""

import logging
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from enum import Enum

from ..config import config

logger = logging.getLogger(__name__)


class PrimitiveType(Enum):
    """Enumeration of primitive types that support relationships."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"


class RelationshipDetector:
    """
    Detects relationships between schema entities through various analysis methods.

    This class implements multiple detection strategies:
    - Foreign key template matching with confidence thresholds and semantic validation
    - Shared field analysis with camelCase support (FK-aware filtering)
    - Naming pattern recognition
    - Domain-specific relationship hints
    - Conservative GraphQL type compatibility checking

    Only creates relationships between ObjectTypes that are queryable (have associated Models or Query Commands).
    ENHANCED: Filters shared field relationships when FK relationships already exist between entities.
    FIXED: Conservative primitive type detection to prevent object type false positives.
    ENHANCED: Type compatibility validation to ensure field types can form valid relationships.
    ENHANCED: Only STRING and INTEGER types are considered relationship-worthy for practical purposes.
    """

    def __init__(self):
        """Initialize the relationship detector with parsed templates and conservative type checking."""
        self.parsed_fk_templates = config.parse_fk_templates()
        self.domain_identifiers = config.domain_identifiers

        # Minimum confidence score for FK relationships to prevent spurious matches
        self.min_confidence_score = 50

        # ENHANCED: Minimum semantic match confidence for FK field mapping
        self.min_semantic_confidence = 70

        # Conservative type compatibility system
        self._init_type_compatibility()

        logger.info(
            f"Initialized RelationshipDetector with {len(config.generic_fields)} generic fields for FK suffix matching: "
            f"{', '.join(config.generic_fields)}")
        logger.info(f"Minimum FK confidence threshold: {self.min_confidence_score}")
        logger.info(f"Minimum semantic field match confidence: {self.min_semantic_confidence}")
        logger.info(
            f"Conservative type compatibility checking enabled with {len(self.direct_type_mappings)} direct mappings")
        logger.info(f"Relationship-worthy types: STRING, INTEGER only (conservative)")

    def _init_type_compatibility(self):
        """Initialize conservative type compatibility checking system."""

        # FIXED: Conservative direct GraphQL scalar type mappings - only well-known primitives
        self.direct_type_mappings = {
            # String types
            'string': PrimitiveType.STRING,
            'str': PrimitiveType.STRING,
            'text': PrimitiveType.STRING,

            # Integer types
            'int': PrimitiveType.INTEGER,
            'integer': PrimitiveType.INTEGER,
            'long': PrimitiveType.INTEGER,
            'bigint': PrimitiveType.INTEGER,

            # Float types
            'float': PrimitiveType.FLOAT,
            'double': PrimitiveType.FLOAT,
            'decimal': PrimitiveType.FLOAT,

            # Boolean types
            'boolean': PrimitiveType.BOOLEAN,
            'bool': PrimitiveType.BOOLEAN,

            # ID types (usually strings)
            'id': PrimitiveType.STRING,
            'uuid': PrimitiveType.STRING,
            'guid': PrimitiveType.STRING,
        }

        # FIXED: Conservative primitive name detection patterns - look for actual primitive type names
        self.primitive_name_patterns = [
            # String-based types
            (re.compile(r'\bstring\b', re.IGNORECASE), PrimitiveType.STRING),
            (re.compile(r'\bstr\b', re.IGNORECASE), PrimitiveType.STRING),
            (re.compile(r'\btext\b', re.IGNORECASE), PrimitiveType.STRING),

            # Integer-based types
            (re.compile(r'\bint\b', re.IGNORECASE), PrimitiveType.INTEGER),
            (re.compile(r'\binteger\b', re.IGNORECASE), PrimitiveType.INTEGER),
            (re.compile(r'\blong\b', re.IGNORECASE), PrimitiveType.INTEGER),
            (re.compile(r'\bbigint\b', re.IGNORECASE), PrimitiveType.INTEGER),

            # Float-based types
            (re.compile(r'\bfloat\b', re.IGNORECASE), PrimitiveType.FLOAT),
            (re.compile(r'\bdouble\b', re.IGNORECASE), PrimitiveType.FLOAT),
            (re.compile(r'\bdecimal\b', re.IGNORECASE), PrimitiveType.FLOAT),

            # Boolean-based types
            (re.compile(r'\bbool\b', re.IGNORECASE), PrimitiveType.BOOLEAN),
            (re.compile(r'\bboolean\b', re.IGNORECASE), PrimitiveType.BOOLEAN),

            # ID-based types (usually strings)
            (re.compile(r'\bid\b', re.IGNORECASE), PrimitiveType.STRING),
            (re.compile(r'\buuid\b', re.IGNORECASE), PrimitiveType.STRING),
            (re.compile(r'\bguid\b', re.IGNORECASE), PrimitiveType.STRING),
        ]

        # Type compatibility matrix - strict matching only for relationship-worthy types
        # For practical purposes, only STRING and INTEGER types support relationships reliably
        self.compatibility_matrix = {
            PrimitiveType.STRING: {PrimitiveType.STRING},
            PrimitiveType.INTEGER: {PrimitiveType.INTEGER},
            # Note: FLOAT and BOOLEAN types removed for practical relationship purposes
        }

    def _normalize_graphql_type(self, graphql_type: str) -> Optional[PrimitiveType]:
        """
        Normalize a GraphQL type to its primitive type using conservative detection.

        Args:
            graphql_type: The GraphQL type string (e.g., "String!", "UserID", "BigInt", "Target")

        Returns:
            The normalized primitive type, or None if the type is unknown or not relationship-worthy
        """
        if not graphql_type:
            return None

        # Remove GraphQL modifiers (!, [], etc.)
        clean_type = self._clean_graphql_type(graphql_type)

        # Try direct mapping first
        clean_lower = clean_type.lower()
        if clean_lower in self.direct_type_mappings:
            result = self.direct_type_mappings[clean_lower]
            logger.debug(f"Direct mapping: {graphql_type} -> {clean_type} -> {result.value}")
            return result

        # FIXED: Try conservative primitive name detection patterns
        for pattern, primitive_type in self.primitive_name_patterns:
            if pattern.search(clean_type):  # Use search instead of match to find primitive names within custom types
                logger.debug(
                    f"Primitive name found: {graphql_type} -> {clean_type} -> {primitive_type.value} (pattern: {pattern.pattern})")
                return primitive_type

        # FIXED: Unknown or non-relationship-worthy type - be conservative
        logger.debug(f"Conservative rejection: {graphql_type} -> {clean_type} -> None (no primitive type name found)")
        return None

    @staticmethod
    def _clean_graphql_type(graphql_type: str) -> str:
        """
        Clean GraphQL type string by removing modifiers.

        Examples:
        - "String!" -> "String"
        - "[User!]!" -> "User"
        - "UserID_123" -> "UserID"

        Args:
            graphql_type: Raw GraphQL type string

        Returns:
            Cleaned type string
        """
        # Remove array brackets and their contents
        clean_type = re.sub(r'\[([^\]]+)\]', r'\1', graphql_type)

        # Remove non-null indicators
        clean_type = clean_type.replace('!', '')

        # Remove trailing numbers and underscores (versioning)
        clean_type = re.sub(r'[_\d]+$', '', clean_type)

        # Trim whitespace
        clean_type = clean_type.strip()

        return clean_type

    def _are_types_compatible(self, type1: str, type2: str) -> Tuple[bool, str]:
        """
        Check if two GraphQL types are compatible for relationships.

        Args:
            type1: First GraphQL type
            type2: Second GraphQL type

        Returns:
            Tuple of (is_compatible, reason)
        """
        if not type1 or not type2:
            return False, "One or both types are empty"

        primitive1 = self._normalize_graphql_type(type1)
        primitive2 = self._normalize_graphql_type(type2)

        # Unknown types are not compatible
        if primitive1 is None or primitive2 is None:
            type1_desc = primitive1.value if primitive1 else "unknown/non-relationship-worthy"
            type2_desc = primitive2.value if primitive2 else "unknown/non-relationship-worthy"
            return False, f"Unknown type(s): {type1}({type1_desc}) <-> {type2}({type2_desc})"

        # Check compatibility matrix
        compatible = primitive2 in self.compatibility_matrix.get(primitive1, set())

        if compatible:
            reason = f"Compatible: {type1}({primitive1.value}) <-> {type2}({primitive2.value})"
        else:
            reason = f"Incompatible: {type1}({primitive1.value}) <-> {type2}({primitive2.value})"

        logger.debug(reason)
        return compatible, reason

    def _validate_field_type_compatibility(self, source_field: Dict, target_field: Dict,
                                           relationship_context: str = "") -> Tuple[bool, str]:
        """
        Validate type compatibility between source and target fields.

        Args:
            source_field: Source field info with 'name' and 'type'
            target_field: Target field info with 'name' and 'type'
            relationship_context: Context for logging

        Returns:
            Tuple of (is_compatible, reason)
        """
        source_type = source_field.get('type', '')
        target_type = target_field.get('type', '')
        source_name = source_field.get('name', '?')
        target_name = target_field.get('name', '?')

        context = f"{relationship_context}: {source_name}({source_type}) -> {target_name}({target_type})"

        compatible, reason = self._are_types_compatible(source_type, target_type)
        return compatible, f"[{context}] {reason}"

    @staticmethod
    def _is_valid_relationship_target(target_qnk: str, target_info: Dict) -> bool:
        """
        Check if entity can be a valid relationship target.

        Centralized validation logic to prevent Commands and Command-only ObjectTypes
        from being relationship targets.

        Args:
            target_qnk: Qualified name of target entity
            target_info: Target entity information

        Returns:
            True if entity can be a relationship target, False otherwise
        """
        # Skip entities that are not queryable
        if not target_info.get('is_queryable', False):
            logger.debug(f"Skipping non-queryable entity {target_qnk}")
            return False

        target_kind = target_info.get('kind')
        queryable_via = target_info.get('queryable_via', [])

        # CRITICAL: Commands cannot be relationship targets (no filtering semantics)
        if target_kind == 'Command':
            logger.debug(
                f"BLOCKED: Command {target_qnk} cannot be relationship target - Commands have no filtering semantics")
            return False

        # CRITICAL: ObjectTypes must be backed by Models to be relationship targets
        if target_kind == 'ObjectType':
            if 'Model' not in queryable_via:
                logger.debug(
                    f"BLOCKED: Command-only ObjectType {target_qnk} cannot be relationship target - no Model backing")
                return False

        # Models are always valid targets if queryable
        if target_kind == 'Model':
            return True

        # For other entity types, they must be queryable
        return target_info.get('is_queryable', False)

    def detect_shared_field_relationships(self, entities_map: Dict[str, Dict],
                                          exclude_connected_pairs: Optional[Set[frozenset]] = None) -> List[
        Dict[str, Any]]:
        """
        Detect relationships based on shared field names with type compatibility validation.

        Uses camelCase to snake_case conversion for analysis but preserves original field names.
        Only detects relationships between ObjectTypes that are queryable.

        ENHANCED: Now excludes entity pairs that are already connected via FK relationships
        to prevent redundant shared field relationships for denormalized data.
        ENHANCED: Validates type compatibility between shared fields.
        ENHANCED: Only considers STRING and INTEGER fields as relationship-worthy.
        ENHANCED: Respects configuration limits for shared relationships.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info
            exclude_connected_pairs: Set of frozensets containing entity pairs already connected via FK

        Returns:
            List of detected shared field relationships with original field names preserved
        """
        # Check if shared relationships are enabled
        if not config.enable_shared_relationships:
            logger.info("Shared field relationship detection disabled by configuration")
            return []

        relationships = []
        exclude_connected_pairs = exclude_connected_pairs or set()

        # Filter entities to only include queryable ones
        queryable_entities_map = self._filter_queryable_entities(entities_map)

        logger.info(f"Analyzing {len(queryable_entities_map)} queryable entities for shared field relationships "
                    f"(filtered from {len(entities_map)} total entities)")
        logger.info(f"Using camelCase→snake_case conversion for comparison only - preserving original field names")
        logger.info(f"Configuration limits: max_total={config.max_shared_relationships}, "
                    f"max_per_entity={config.max_shared_per_entity}, min_confidence={config.min_shared_confidence}")

        if exclude_connected_pairs:
            logger.info(
                f"FK-aware filtering: Excluding {len(exclude_connected_pairs)} entity pairs already connected via FK")

        # Build field mapping: snake_case → {original_name, entity_qnk, type}
        snake_case_field_map = {}

        for qnk, info in queryable_entities_map.items():
            for f in info.get('fields', []):
                field_name = f.get('name')
                field_type = f.get('type', '')
                if field_name and self._is_relationship_worthy_type(field_type):
                    field_name_snake = self._camel_to_snake_case(field_name)

                    if field_name_snake not in snake_case_field_map:
                        snake_case_field_map[field_name_snake] = []

                    snake_case_field_map[field_name_snake].append({
                        'entity_qnk': qnk,
                        'original_field_name': field_name,
                        'field_type': field_type
                    })

        # Find shared fields (snake_case fields that appear in multiple entities)
        relationships_before_filtering = 0
        relationships_after_filtering = 0
        fk_filtered_pairs = 0
        type_filtered_pairs = 0
        confidence_filtered_pairs = 0
        entity_relationship_counts = {}  # Track relationships per entity

        for field_snake, field_instances in snake_case_field_map.items():
            if len(field_instances) < 2:
                continue  # Not shared

            # Skip generic fields and primary keys using snake_case comparison
            if not config.is_shared_key(field_snake):
                logger.debug(f"Skipping generic field '{field_snake}' for shared field relationships")
                continue

            # Check all pairs of entities that share this field
            for i, instance1 in enumerate(field_instances):
                for instance2 in field_instances[i + 1:]:
                    qnk1 = instance1['entity_qnk']
                    qnk2 = instance2['entity_qnk']

                    entity1_info = queryable_entities_map[qnk1]
                    entity2_info = queryable_entities_map[qnk2]

                    # Count potential relationships BEFORE any filtering
                    relationships_before_filtering += 1

                    # ENHANCED: Check if this entity pair is already connected via FK
                    entity_pair = frozenset([qnk1, qnk2])
                    if entity_pair in exclude_connected_pairs:
                        fk_filtered_pairs += 1
                        logger.debug(
                            f"FK-FILTERED: Skipping shared field '{field_snake}' between {qnk1} and {qnk2} - already connected via FK")
                        continue

                    entity1_valid = self._is_valid_relationship_target(qnk1, entity1_info)
                    entity2_valid = self._is_valid_relationship_target(qnk2, entity2_info)

                    if not entity1_valid and not entity2_valid:
                        logger.debug(
                            f"BLOCKED: Shared field relationship - neither {qnk1} nor {qnk2} can be relationship targets")
                        continue

                    # Skip if either entity has this field as primary key
                    entity1_pks = {self._camel_to_snake_case(pk) for pk in entity1_info.get('primary_keys', [])}
                    entity2_pks = {self._camel_to_snake_case(pk) for pk in entity2_info.get('primary_keys', [])}

                    if field_snake in entity1_pks or field_snake in entity2_pks:
                        logger.debug(
                            f"Skipping shared field '{field_snake}' between {qnk1} and {qnk2} - is primary key")
                        continue

                    # NEW: Validate type compatibility between shared fields
                    field1_info = {
                        'name': instance1['original_field_name'],
                        'type': instance1['field_type']
                    }
                    field2_info = {
                        'name': instance2['original_field_name'],
                        'type': instance2['field_type']
                    }

                    compatible, reason = self._validate_field_type_compatibility(
                        field1_info, field2_info,
                        f"Shared field {field_snake} between {qnk1} and {qnk2}"
                    )

                    if not compatible:
                        type_filtered_pairs += 1
                        logger.debug(f"TYPE-FILTERED: {reason}")
                        continue

                    # NEW: Apply confidence filtering
                    confidence = self._calculate_shared_field_confidence(field_snake)
                    confidence_score = self._convert_confidence_to_score(confidence)

                    if confidence_score < config.min_shared_confidence:
                        confidence_filtered_pairs += 1
                        logger.debug(f"CONFIDENCE-FILTERED: Shared field '{field_snake}' between {qnk1} and {qnk2} - "
                                     f"confidence {confidence_score} < {config.min_shared_confidence}")
                        continue

                    # NEW: Check per-entity limits
                    entity1_name = entity1_info.get('name')
                    entity2_name = entity2_info.get('name')

                    if entity1_name not in entity_relationship_counts:
                        entity_relationship_counts[entity1_name] = 0
                    if entity2_name not in entity_relationship_counts:
                        entity_relationship_counts[entity2_name] = 0

                    if (entity_relationship_counts[entity1_name] >= config.max_shared_per_entity or
                            entity_relationship_counts[entity2_name] >= config.max_shared_per_entity):
                        logger.debug(f"ENTITY-LIMIT-FILTERED: Skipping shared field '{field_snake}' - "
                                     f"entity limit reached for {entity1_name} or {entity2_name}")
                        continue

                    # NEW: Check global relationship limit
                    if len(relationships) >= config.max_shared_relationships:
                        logger.info(
                            f"GLOBAL-LIMIT-REACHED: Stopping shared field detection at {config.max_shared_relationships} relationships")
                        break

                    # Create shared field relationship
                    relationship = {
                        'from_entity': qnk1,
                        'to_entity': qnk2,
                        'shared_field': field_snake,  # snake_case for processing consistency
                        'original_field1': instance1['original_field_name'],  # PRESERVE original
                        'original_field2': instance2['original_field_name'],  # PRESERVE original
                        'field1_type': instance1['field_type'],  # NEW: Include types
                        'field2_type': instance2['field_type'],  # NEW: Include types
                        'relationship_type': 'shared_field',
                        'confidence': confidence,
                        'confidence_score': confidence_score,  # NEW: Include numeric score
                        'cross_subgraph': entity1_info.get('subgraph') != entity2_info.get('subgraph')
                    }

                    relationships.append(relationship)
                    relationships_after_filtering += 1

                    # Update entity relationship counts
                    entity_relationship_counts[entity1_name] += 1
                    entity_relationship_counts[entity2_name] += 1

                # Break outer loop if global limit reached
                if len(relationships) >= config.max_shared_relationships:
                    break

            # Break field loop if global limit reached
            if len(relationships) >= config.max_shared_relationships:
                break

        # Log filtering effectiveness
        logger.info(f"Enhanced filtering results:")
        logger.info(f"  - Entity pairs filtered due to existing FK connections: {fk_filtered_pairs}")
        logger.info(f"  - Entity pairs filtered due to type incompatibility: {type_filtered_pairs}")
        logger.info(f"  - Entity pairs filtered due to low confidence: {confidence_filtered_pairs}")
        logger.info(f"  - Shared field relationships before filtering: {relationships_before_filtering}")
        logger.info(f"  - Shared field relationships after filtering: {relationships_after_filtering}")
        logger.info(
            f"  - Total reduction due to filtering: {relationships_before_filtering - relationships_after_filtering}")

        if relationships_before_filtering > 0:
            fk_reduction = (fk_filtered_pairs / relationships_before_filtering) * 100
            type_reduction = (type_filtered_pairs / relationships_before_filtering) * 100
            confidence_reduction = (confidence_filtered_pairs / relationships_before_filtering) * 100
            logger.info(f"  - FK filtering effectiveness: {fk_reduction:.1f}%")
            logger.info(f"  - Type filtering effectiveness: {type_reduction:.1f}%")
            logger.info(f"  - Confidence filtering effectiveness: {confidence_reduction:.1f}%")

        logger.info(
            f"Detected {len(relationships)} shared field relationships between queryable entities (enhanced filtering)")
        return relationships

    @staticmethod
    def _convert_confidence_to_score(confidence: str) -> int:
        """Convert string confidence to numeric score."""
        confidence_mapping = {
            'high': 80,
            'medium': 50,
            'low': 30
        }
        return confidence_mapping.get(confidence.lower(), 30)

    def _process_fk_template_match(self, match, source_qnk: str, source_info: Dict,
                                   field_name: str, pk_template_str: str,
                                   entities_map: Dict[str, Dict]) -> Optional[List[Dict[str, Any]]]:
        """
        Process a successful foreign key template match with type compatibility validation.

        ENHANCED: Now returns a list of relationships to handle multiple valid targets for the same field.
        FIXED: Strict semantic validation for target field matching.
        ENHANCED: Type compatibility validation between source and target fields.

        Args:
            match: Regex match object
            source_qnk: Source entity qualified name
            source_info: Source entity information
            field_name: Field name being processed
            pk_template_str: Primary key template string
            entities_map: Map of all entities

        Returns:
            List of relationship dictionaries (it may be empty, single, or multiple)
        """
        match_groups = match.groupdict()
        guessed_primary_table = match_groups.get('primary_table')
        guessed_generic_id = match_groups.get('generic_id')
        explicit_target_subgraph = match_groups.get('primary_subgraph')
        source_subgraph = source_info.get('subgraph')

        if not guessed_primary_table:
            return None

        # Find source field info for type checking
        source_field_info = None
        for field in source_info.get('fields', []):
            if field.get('name') == field_name:
                source_field_info = field
                break

        if not source_field_info:
            logger.warning(f"Could not find source field info for {field_name}")
            return None

        # Generate entity name variations to check
        forms_to_check = {guessed_primary_table.lower()}
        if guessed_primary_table.lower().endswith('s') and len(guessed_primary_table) > 1:
            forms_to_check.add(guessed_primary_table.lower()[:-1])  # Singular
        else:
            forms_to_check.add(guessed_primary_table.lower() + 's')  # Plural

        forms_to_check.discard("")  # Remove empty strings

        # ENHANCEMENT: Track all valid targets instead of returning first match
        valid_relationships = []

        # Find all matching target entities for this field
        for form in forms_to_check:
            # Get all potential targets for this form (there might be multiple)
            potential_targets = self._find_all_referenced_entities(
                form, explicit_target_subgraph, source_qnk, entities_map, source_subgraph
            )

            for target_qnk in potential_targets:
                if target_qnk != source_qnk:
                    target_info = entities_map.get(target_qnk, {})

                    # Use centralized validation
                    if not self._is_valid_relationship_target(target_qnk, target_info):
                        continue

                    # FIXED: Determine target field name with strict semantic validation
                    field_match_result = self._determine_and_validate_target_field_name_semantic(
                        pk_template_str, guessed_generic_id, guessed_primary_table,
                        field_name, target_info
                    )

                    # Only create relationship if target field actually exists and meets semantic requirements
                    if not field_match_result:
                        logger.debug(
                            f"Skipping relationship from {source_qnk}.{field_name} to {target_qnk} - no valid semantic target field found")
                        continue

                    to_field_name, semantic_confidence = field_match_result

                    # Apply semantic confidence threshold
                    if semantic_confidence < self.min_semantic_confidence:
                        logger.debug(
                            f"Skipping relationship from {source_qnk}.{field_name} to {target_qnk}.{to_field_name} - "
                            f"semantic confidence {semantic_confidence} < {self.min_semantic_confidence}")
                        continue

                    # NEW: Find target field info for type checking
                    target_field_info = None
                    for field in target_info.get('fields', []):
                        if field.get('name') == to_field_name:
                            target_field_info = field
                            break

                    if not target_field_info:
                        logger.debug(f"Could not find target field info for {to_field_name}")
                        continue

                    # NEW: Validate type compatibility
                    compatible, reason = self._validate_field_type_compatibility(
                        source_field_info, target_field_info,
                        f"FK relationship {source_qnk}.{field_name} -> {target_qnk}.{to_field_name}"
                    )

                    if not compatible:
                        logger.debug(f"TYPE-FILTERED FK relationship: {reason}")
                        continue

                    relationship = {
                        'from_entity': source_qnk,
                        'from_field': field_name,  # PRESERVE original field name (camelCase or snake_case)
                        'to_entity': target_qnk,
                        'to_field_name': to_field_name,  # PRESERVE original target field name
                        'from_field_type': source_field_info.get('type', ''),  # NEW: Include types
                        'to_field_type': target_field_info.get('type', ''),  # NEW: Include types
                        'relationship_type': 'foreign_key_template',
                        'confidence': 'high',
                        'semantic_confidence': semantic_confidence,
                        'cross_subgraph': source_subgraph != target_info.get('subgraph'),
                        'template_used': pk_template_str
                    }

                    valid_relationships.append(relationship)

        # Log results
        if len(valid_relationships) > 1:
            target_names = [entities_map.get(rel['to_entity'], {}).get('name', 'unknown') for rel in
                            valid_relationships]
            logger.info(
                f"Field {source_qnk}.{field_name} matches {len(valid_relationships)} targets: {', '.join(target_names)}")

        return valid_relationships if valid_relationships else None

    def _find_all_referenced_entities(self, ref_entity_name_guess: str,
                                      explicit_target_subgraph: Optional[str],
                                      source_entity_qnk: str, entities_map: Dict[str, Dict],
                                      source_entity_subgraph: Optional[str]) -> List[str]:
        """
        Find ALL matching entities for a reference guess (not just the best one).

        Enhanced version of find_referenced_entity that returns all valid matches
        above the minimum confidence threshold.

        Args:
            ref_entity_name_guess: Guessed entity name from field analysis
            explicit_target_subgraph: Explicit subgraph hint from template
            source_entity_qnk: Qualified name of source entity
            entities_map: Map of all entities
            source_entity_subgraph: Subgraph of source entity

        Returns:
            List of qualified names of all matching target entities
        """
        if not ref_entity_name_guess:
            return []

        ref_lower = ref_entity_name_guess.lower()
        possible_targets = []

        for target_qnk, target_info in entities_map.items():
            # Use centralized validation
            if not self._is_valid_relationship_target(target_qnk, target_info):
                continue

            target_name = target_info.get('name', '')
            if not target_name:
                continue

            target_name_lower = target_name.lower()
            target_subgraph = target_info.get('subgraph')
            target_kind = target_info.get('kind')

            score, match_details = self._calculate_entity_match_score(
                ref_lower, target_name_lower, target_subgraph, target_kind,
                explicit_target_subgraph, source_entity_subgraph
            )

            if score >= self.min_confidence_score:
                possible_targets.append({
                    'qnk': target_qnk,
                    'score': score,
                    'match_details': match_details
                })

        if not possible_targets:
            return []

        # Sort by score and return all that meet the threshold
        possible_targets.sort(key=lambda t: t['score'], reverse=True)

        # Log found targets
        if len(possible_targets) > 1:
            target_details = [(t['qnk'], t['score']) for t in possible_targets]
            logger.debug(f"Found {len(possible_targets)} valid targets for '{ref_entity_name_guess}': {target_details}")

        return [t['qnk'] for t in possible_targets]

    def detect_foreign_key_relationships(self, entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect foreign key relationships using template matching with type compatibility validation.

        ENHANCED: Now handles multiple targets for the same field properly.
        FIXED: Strict semantic validation to prevent spurious generic matches.
        ENHANCED: Type compatibility validation between source and target fields.
        ENHANCED: Only considers STRING and INTEGER fields as relationship-worthy.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            List of detected foreign key relationships with original field names preserved
        """
        relationships = []

        # Filter entities to only include queryable ones
        queryable_entities_map = self._filter_queryable_entities(entities_map)

        # DEBUG: Check what's in the source list
        command_sources = [qnk for qnk, info in queryable_entities_map.items() if info.get('kind') == 'Command']
        logger.info(f"DEBUG: {len(command_sources)} Commands available as sources: {command_sources}")

        logger.info(f"Analyzing {len(queryable_entities_map)} queryable entities for foreign key relationships "
                    f"(filtered from {len(entities_map)} total entities)")
        logger.info(f"Using camelCase→snake_case conversion for analysis only - preserving original field names")
        logger.info(f"Minimum confidence threshold: {self.min_confidence_score}")
        logger.info(f"Minimum semantic field match confidence: {self.min_semantic_confidence}")
        logger.info(f"Conservative type compatibility validation enabled - STRING and INTEGER only")

        type_filtered_count = 0

        for source_qnk, source_info in queryable_entities_map.items():
            source_subgraph = source_info.get('subgraph')
            # Convert primary keys to snake_case for comparison
            source_pks = {self._camel_to_snake_case(pk) for pk in source_info.get('primary_keys', [])}

            for field in source_info.get('fields', []):
                field_name = field.get('name', '')
                field_type = field.get('type', '')

                if not field_name:
                    continue

                # Convert to snake_case ONLY for analysis - preserve original field_name
                field_name_snake = self._camel_to_snake_case(field_name)

                # Skip primary keys using snake_case comparison
                if field_name_snake in source_pks:
                    logger.debug(f"Skipping primary key field '{field_name}' in {source_qnk} for FK detection")
                    continue

                # Check if this field type supports relationships
                if not self._is_relationship_worthy_type(field_type):
                    logger.debug(
                        f"Skipping field '{field_name}' with type '{field_type}' in {source_qnk} - not relationship-worthy")
                    continue

                # Try each FK template against the snake_case version for matching
                for template_info in self.parsed_fk_templates:
                    fk_regex = template_info['fk_regex']
                    pk_template_str = template_info['pk_template_str']

                    match = fk_regex.match(field_name_snake)
                    if match:
                        # ENHANCED: Process match may return multiple relationships
                        field_relationships = self._process_fk_template_match(
                            match, source_qnk, source_info, field_name, pk_template_str, queryable_entities_map
                        )
                        if field_relationships:
                            relationships.extend(field_relationships)
                            break  # Stop after first successful template match

        logger.info(
            f"Detected {len(relationships)} foreign key relationships between queryable entities (conservative type validation)")
        return relationships

    @staticmethod
    def _camel_to_snake_case(field_name: str) -> str:
        """
        Convert camelCase field names to snake_case for analysis only.

        Examples:
        - lastUsedFileName → last_used_file_name
        - userId → user_id
        - companyId → company_id
        - XMLHttpRequest → xml_http_request

        Args:
            field_name: Original field name (it may be camelCase or snake_case)

        Returns:
            snake_case version of the field name
        """
        if not field_name:
            return field_name

        # If already contains underscores, likely already snake_case
        if '_' in field_name:
            return field_name.lower()

        # Handle sequences of capitals (like XMLHttp → xml_http)
        # Insert underscore before capitals that follow lowercase or are followed by lowercase
        snake_case = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', field_name)
        snake_case = re.sub(r'([A-Z])([A-Z][a-z])', r'\1_\2', snake_case)

        # Convert to lowercase and remove any leading underscores
        return snake_case.lower().lstrip('_')

    def _is_relationship_worthy_type(self, field_type: str) -> bool:
        """
        Determine if a field type supports relationships using conservative type checking.

        ENHANCED: Now uses conservative GraphQL type normalization and only supports STRING and INTEGER types.

        Args:
            field_type: The type declaration from the field definition

        Returns:
            True if field type supports relationships (STRING or INTEGER only for practical purposes)
        """
        if not field_type:
            return False

        # Skip arrays (start with '[')
        if field_type.startswith('['):
            logger.debug(f"Field type '{field_type}' is array - excluding from relationships")
            return False

        # Use conservative type normalization
        primitive_type = self._normalize_graphql_type(field_type)

        # Only STRING and INTEGER types can participate in relationships (practical constraint)
        is_worthy = primitive_type in {PrimitiveType.STRING, PrimitiveType.INTEGER}

        if not is_worthy:
            normalized_desc = primitive_type.value if primitive_type else "unknown/non-relationship-worthy"
            logger.debug(f"Field type '{field_type}' -> {normalized_desc} - excluding from relationships")

        return is_worthy

    def detect_naming_pattern_relationships(self, entities_map: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect relationships based on naming patterns and conventions.

        Only detects relationships between ObjectTypes that are queryable.

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            List of detected naming pattern relationships
        """
        relationships = []

        # Filter entities to only include queryable ones
        queryable_entities_map = self._filter_queryable_entities(entities_map)

        logger.info(f"Analyzing {len(queryable_entities_map)} queryable entities for naming pattern relationships "
                    f"(filtered from {len(entities_map)} total entities)")

        # Analyze entity names for hierarchical patterns
        entity_names = [(qnk, info.get('name', '')) for qnk, info in queryable_entities_map.items()]

        for qnk1, name1 in entity_names:
            for qnk2, name2 in entity_names:
                if qnk1 >= qnk2 or not name1 or not name2:
                    continue

                pattern_relationship = self._analyze_naming_patterns(qnk1, name1, qnk2, name2, queryable_entities_map)
                if pattern_relationship:
                    relationships.append(pattern_relationship)

        logger.info(f"Detected {len(relationships)} naming pattern relationships between queryable entities")
        return relationships

    def find_referenced_entity(self, ref_entity_name_guess: str,
                               explicit_target_subgraph: Optional[str],
                               source_entity_qnk: str, entities_map: Dict[str, Dict],
                               source_entity_subgraph: Optional[str]) -> Optional[str]:
        """
        Find the best matching entity for a reference guess.

        Now includes minimum confidence threshold to reject weak matches.
        Only considers entities that are queryable.

        Args:
            ref_entity_name_guess: Guessed entity name from field analysis
            explicit_target_subgraph: Explicit subgraph hint from template
            source_entity_qnk: Qualified name of source entity
            entities_map: Map of all entities
            source_entity_subgraph: Subgraph of source entity

        Returns:
            Qualified name of best matching target entity or None
        """
        if not ref_entity_name_guess:
            return None

        ref_lower = ref_entity_name_guess.lower()
        possible_targets = []

        for target_qnk, target_info in entities_map.items():
            # Use centralized validation
            if not self._is_valid_relationship_target(target_qnk, target_info):
                continue

            target_name = target_info.get('name', '')
            if not target_name:
                continue

            target_name_lower = target_name.lower()
            target_subgraph = target_info.get('subgraph')
            target_kind = target_info.get('kind')

            score, match_details = self._calculate_entity_match_score(
                ref_lower, target_name_lower, target_subgraph, target_kind,
                explicit_target_subgraph, source_entity_subgraph
            )

            if score > 0:
                possible_targets.append({
                    'qnk': target_qnk,
                    'score': score,
                    'match_details': match_details
                })

        if not possible_targets:
            return None

        # Return the highest scoring match only if it meets minimum confidence threshold
        possible_targets.sort(key=lambda t: t['score'], reverse=True)
        best_match = possible_targets[0]

        # Apply minimum confidence threshold to prevent spurious relationships
        if best_match['score'] < self.min_confidence_score:
            logger.debug(f"Rejecting weak match for '{ref_entity_name_guess}': "
                         f"best score {best_match['score']} < {self.min_confidence_score} "
                         f"(target: {best_match['qnk']}, details: {best_match['match_details']})")
            return None

        logger.debug(f"Accepted match for '{ref_entity_name_guess}': {best_match['qnk']} "
                     f"(score: {best_match['score']}, details: {best_match['match_details']})")

        return best_match['qnk']

    def scan_for_existing_relationships(self, file_paths: List[str]) -> Set[Tuple]:
        """
        Scan files for existing relationship definitions to avoid duplicates.

        Args:
            file_paths: List of file paths to scan

        Returns:
            Set of relationship signatures (source_type, canonical_mapping)
        """
        from ..utils.yaml_utils import load_yaml_documents

        existing_signatures = set()

        logger.info(f"Scanning {len(file_paths)} files for existing relationships...")

        for file_path in file_paths:
            try:
                documents = load_yaml_documents(file_path)
                for doc in documents:
                    if isinstance(doc, dict) and doc.get('kind') == 'Relationship':
                        signature = self.extract_relationship_signature(doc)
                        if signature:
                            existing_signatures.add(signature)
            except Exception as e:
                logger.error(f"Error scanning file {file_path} for existing relationships: {e}")

        logger.info(f"Found {len(existing_signatures)} existing relationship signatures")
        return existing_signatures

    @staticmethod
    def _filter_queryable_entities(entities_map: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Filter entities to only include queryable ones (have Models or Query Commands).

        Args:
            entities_map: Dictionary mapping qualified entity names to entity info

        Returns:
            Filtered dictionary containing only queryable entities
        """
        queryable_entities = {}

        for qnk, entity_info in entities_map.items():
            if entity_info.get('is_queryable', False):
                queryable_entities[qnk] = entity_info
            else:
                logger.debug(f"Excluding entity {qnk} from relationship detection - not queryable")

        logger.info(f"Filtered {len(entities_map)} entities to {len(queryable_entities)} queryable entities")
        return queryable_entities

    @staticmethod
    def _calculate_entity_match_score(ref_name: str, target_name: str,
                                      target_subgraph: Optional[str], target_kind: str,
                                      explicit_subgraph: Optional[str],
                                      source_subgraph: Optional[str]) -> Tuple[int, str]:
        """Calculate matching score between reference and target entity."""
        score = 0
        match_details = []

        # Direct name match
        if target_name == ref_name:
            score += 15
            match_details.append("exact_name")

        # Prefix match (subgraph_entityname pattern)
        elif target_name.endswith(f"_{ref_name}"):
            potential_prefix = target_name[:-len(f"_{ref_name}")]
            score += 12
            match_details.append("prefix_match")

            # Bonus if prefix matches target's subgraph
            if target_subgraph and potential_prefix == target_subgraph.lower():
                score += 10
                match_details.append("prefix_matches_subgraph")

            # Bonus if prefix matches source's subgraph
            if source_subgraph and potential_prefix == source_subgraph.lower():
                score += 25
                match_details.append("prefix_matches_source_subgraph")

        # Plural/singular variations
        if len(ref_name) > 1:
            if target_name == ref_name + "s":
                score = max(score, 9)
                if not match_details:
                    match_details.append("plural_target")
            elif target_name + "s" == ref_name:
                score = max(score, 7)
                if not match_details:
                    match_details.append("plural_reference")

        # Subgraph bonuses
        if score > 0:
            if explicit_subgraph and target_subgraph and explicit_subgraph.lower() == target_subgraph.lower():
                score += 200
                match_details.append("EXPLICIT_SUBGRAPH_MATCH")
            elif source_subgraph and target_subgraph == source_subgraph:
                score += 100
                match_details.append("SAME_SUBGRAPH")

        # Kind bonuses
        if target_kind == 'ObjectType':
            score += 20
        elif target_kind == 'Model':
            score += 10

        return score, ", ".join(match_details)

    @staticmethod
    def _determine_and_validate_target_field_name_semantic(pk_template: str, guessed_generic_id: Optional[str],
                                                           guessed_entity_name: str, source_field_name: str,
                                                           target_info: Dict) -> Optional[Tuple[str, int]]:
        """
        Determine the target field name for a relationship with strict semantic validation.

        FIXED: This method now prioritizes semantic matches and requires higher confidence
        for generic field matches to prevent spurious relationships like 'network.id' -> network_devices.network_name.

        Args:
            pk_template: Primary key template from configuration
            guessed_generic_id: Guessed generic identifier from field matching
            guessed_entity_name: Guessed entity name from field analysis
            source_field_name: Original source field name for semantic context
            target_info: Target entity information

        Returns:
            Tuple of (valid target field name, semantic confidence) if found, None if no valid field exists
        """
        # Get the list of actual field names in the target entity
        target_field_names = {f.get('name', '').lower() for f in target_info.get('fields', []) if f.get('name')}
        target_pks = target_info.get('primary_keys', [])

        # List of candidate field names to check, in order of preference with confidence scores
        candidate_evaluations = []

        # 1. HIGHEST PRIORITY: Semantic field name matching
        if guessed_entity_name and guessed_generic_id:
            # Extract entity name from source field for semantic matching
            source_field_lower = source_field_name.lower()
            entity_name_lower = guessed_entity_name.lower()

            # Generate semantic field name variations
            semantic_variations = []

            # Try entity_id, entity_key patterns
            # for suffix in config.generic_fields:
            semantic_variations.extend([
                f"{entity_name_lower}_{guessed_generic_id}",
                f"{entity_name_lower}{guessed_generic_id}",  # camelCase version
            ])

            # Also try the exact guessed_generic_id if it's semantically meaningful
            if len(guessed_generic_id) > 1:  # Not just 'id'
                semantic_variations.append(guessed_generic_id.lower())

            # Check semantic variations
            for variation in semantic_variations:
                if variation in target_field_names:
                    # High confidence for semantic matches
                    confidence = 100
                    candidate_evaluations.append((variation, confidence, "semantic_match"))

        # 2. MEDIUM PRIORITY: Primary key fields (always valid targets)
        for pk in target_pks:
            pk_lower = pk.lower()
            if pk_lower in target_field_names:
                # Medium-high confidence for primary keys
                confidence = 80
                candidate_evaluations.append((pk_lower, confidence, "primary_key"))

        # 3. LOWER PRIORITY: Template-specified fields
        if pk_template and pk_template != "{gi}":
            template_field = pk_template.lower()
            if template_field in target_field_names:
                # Medium confidence for template matches
                confidence = 60
                candidate_evaluations.append((template_field, confidence, "template_specified"))

        # 4. LOWEST PRIORITY: Generic fields (only if no semantic matches found)
        if not candidate_evaluations or max(c[1] for c in candidate_evaluations) < 70:
            for generic_field in config.generic_fields:
                if generic_field in target_field_names:
                    # Low confidence for generic matches - these often cause spurious relationships
                    confidence = 30
                    candidate_evaluations.append((generic_field, confidence, "generic_fallback"))

        # Select the best candidate with highest confidence
        if not candidate_evaluations:
            available_fields = [f.get('name') for f in target_info.get('fields', []) if f.get('name')]
            logger.debug(f"No valid target field found for entity {target_info.get('name', 'unknown')}. "
                         f"Available fields: {available_fields}")
            return None

        # Sort by confidence (highest first)
        candidate_evaluations.sort(key=lambda x: x[1], reverse=True)
        best_field_lower, best_confidence, match_type = candidate_evaluations[0]

        # Find the original case version of the field
        for field in target_info.get('fields', []):
            if field.get('name', '').lower() == best_field_lower:
                original_field_name = field.get('name')
                logger.debug(
                    f"Selected target field: {original_field_name} (confidence: {best_confidence}, type: {match_type})")
                return original_field_name, best_confidence

        return None

    def _calculate_shared_field_confidence(self, field_name: str) -> str:
        """Calculate confidence level for shared field relationships."""
        if any(domain_id in field_name for domain_id in self.domain_identifiers):
            return 'medium'
        return 'low'

    @staticmethod
    def _is_hierarchical_naming(name1: str, name2: str) -> bool:
        """Check if two names follow a hierarchical pattern."""
        # Simple patterns: one name contains the other
        return (name1 in name2 and name1 != name2) or (name2 in name1 and name1 != name2)

    def _analyze_naming_patterns(self, qnk1: str, name1: str, qnk2: str, name2: str,
                                 entities_map: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
        """Analyze naming patterns between two entities."""
        entity1_info = entities_map[qnk1]
        entity2_info = entities_map[qnk2]

        # Use centralized validation for both entities
        if not self._is_valid_relationship_target(qnk1, entity1_info):
            logger.debug(f"Skipping naming pattern analysis - {qnk1} cannot be relationship target")
            return None

        if not self._is_valid_relationship_target(qnk2, entity2_info):
            logger.debug(f"Skipping naming pattern analysis - {qnk2} cannot be relationship target")
            return None

        name1_lower = name1.lower()
        name2_lower = name2.lower()

        # Check for hierarchical patterns (parent-child naming)
        if self._is_hierarchical_naming(name1_lower, name2_lower):
            return {
                'from_entity': qnk1,
                'to_entity': qnk2,
                'relationship_type': 'naming_hierarchy',
                'confidence': 'medium',
                'cross_subgraph': entity1_info.get('subgraph') != entity2_info.get('subgraph'),
                'pattern_type': 'hierarchical_naming'
            }

        return None

    @staticmethod
    def extract_relationship_signature(relationship_doc: Dict) -> Optional[Tuple]:
        """Extract a signature from an existing relationship document."""
        try:
            definition = relationship_doc.get('definition', {})
            source_type = definition.get('sourceType')
            mapping = definition.get('mapping', [])

            if not source_type or not mapping:
                return None

            canonical_mapping_parts = []
            for m_item in mapping:
                if isinstance(m_item, dict):
                    source_fp = m_item.get('source', {}).get('fieldPath', [])
                    target_block = m_item.get('target', {})
                    target_fp = target_block.get('modelField', target_block.get('fieldPath', []))

                    # Convert to tuples for hashing
                    source_tuple = tuple(fp.get('fieldName', fp) if isinstance(fp, dict) else fp for fp in source_fp)
                    target_tuple = tuple(fp.get('fieldName', fp) if isinstance(fp, dict) else fp for fp in target_fp)

                    canonical_mapping_parts.append((source_tuple, target_tuple))

            canonical_mapping_parts.sort()
            return source_type, frozenset(canonical_mapping_parts)

        except Exception as e:
            logger.warning(f"Could not extract signature from relationship: {e}")
            return None


def create_relationship_detector() -> RelationshipDetector:
    """
    Create a RelationshipDetector instance.

    Returns:
        Configured RelationshipDetector instance
    """
    return RelationshipDetector()

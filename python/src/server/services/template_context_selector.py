"""
Template Context Selector Service

This service provides intelligent template selection based on task context,
keywords, and patterns to automatically choose the most appropriate workflow template.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Supported template types"""
    DEFAULT = "workflow_default"
    HOTFIX = "workflow_hotfix"
    MILESTONE = "workflow_milestone_pass"
    RESEARCH = "workflow_research"
    MAINTENANCE = "workflow_maintenance"


@dataclass
class ContextMatch:
    """Represents a context match with confidence score"""
    template_type: TemplateType
    confidence: float
    matched_patterns: List[str]
    reasoning: str


class TemplateContextSelector:
    """
    Intelligent template selection based on task context and patterns
    """

    def __init__(self):
        """Initialize the template context selector"""
        self.hotfix_patterns = [
            # Urgency indicators
            r'\b(urgent|critical|emergency|hotfix|immediate|asap)\b',
            r'\b(down|outage|broken|failing|crashed)\b',
            r'\b(fix|repair|resolve|patch)\b.*\b(bug|issue|problem|error)\b',
            r'\b(production|prod|live)\b.*\b(issue|problem|down)\b',
            r'\b(incident|alert|alarm)\b',
            r'\b(p0|p1|sev1|severity\s*1)\b',
            # Time pressure
            r'\b(now|today|tonight|immediately)\b',
            r'\b(before|by)\b.*\b(end of day|eod|tomorrow)\b',
        ]

        self.milestone_patterns = [
            # Milestone indicators
            r'\b(milestone|release|deploy|launch|ship)\b',
            r'\b(complete|finish|finalize|wrap up)\b.*\b(milestone|phase|sprint)\b',
            r'\b(sign.?off|approval|review|validate)\b.*\b(milestone|release)\b',
            r'\b(go.?live|production deployment|prod deploy)\b',
            r'\b(final|last|closing)\b.*\b(task|step|phase)\b',
            # Quality gates
            r'\b(testing|validation|verification)\b.*\b(complete|done|finished)\b',
            r'\b(security|performance|integration)\b.*\b(audit|review|validation)\b',
            r'\b(stakeholder|client|customer)\b.*\b(approval|sign.?off|review)\b',
        ]

        self.research_patterns = [
            # Research indicators
            r'\b(research|investigate|analyze|study|explore)\b',
            r'\b(find|discover|identify|determine)\b.*\b(solution|approach|method)\b',
            r'\b(compare|evaluate|assess)\b.*\b(options|alternatives|solutions)\b',
            r'\b(proof of concept|poc|spike|prototype)\b',
            r'\b(feasibility|viability)\b.*\b(study|analysis)\b',
            # Knowledge gathering
            r'\b(learn|understand|figure out)\b',
            r'\b(documentation|literature|best practices)\b.*\b(review|search)\b',
            r'\b(existing|current)\b.*\b(solutions|implementations|approaches)\b',
            r'\b(requirements|specifications)\b.*\b(gathering|analysis)\b',
        ]

        self.maintenance_patterns = [
            # Maintenance indicators
            r'\b(maintenance|update|upgrade|patch)\b',
            r'\b(backup|restore|recovery)\b',
            r'\b(monitoring|health check|status check)\b',
            r'\b(cleanup|optimization|performance tuning)\b',
            r'\b(routine|scheduled|regular)\b.*\b(task|maintenance|update)\b',
            # System operations
            r'\b(database|server|system)\b.*\b(maintenance|update|cleanup)\b',
            r'\b(log|audit|review)\b.*\b(rotation|cleanup|analysis)\b',
            r'\b(certificate|ssl|security)\b.*\b(renewal|update|rotation)\b',
            r'\b(dependency|library|package)\b.*\b(update|upgrade|patch)\b',
        ]

    def select_template(
        self, 
        task_description: str, 
        task_title: str = "", 
        context_data: Optional[Dict] = None
    ) -> Tuple[TemplateType, float, str]:
        """
        Select the most appropriate template based on task context
        
        Args:
            task_description: The task description to analyze
            task_title: Optional task title for additional context
            context_data: Optional additional context data
            
        Returns:
            Tuple of (template_type, confidence, reasoning)
        """
        if not task_description:
            return TemplateType.DEFAULT, 0.5, "No description provided, using default template"

        # Combine title and description for analysis
        full_text = f"{task_title} {task_description}".lower()
        
        # Get all context matches
        matches = self._analyze_context(full_text, context_data or {})
        
        if not matches:
            return TemplateType.DEFAULT, 0.5, "No specific patterns detected, using default template"
        
        # Sort by confidence and return the best match
        best_match = max(matches, key=lambda m: m.confidence)
        
        logger.info(
            f"Template selected: {best_match.template_type.value} "
            f"(confidence: {best_match.confidence:.2f}) - {best_match.reasoning}"
        )
        
        return best_match.template_type, best_match.confidence, best_match.reasoning

    def _analyze_context(self, text: str, context_data: Dict) -> List[ContextMatch]:
        """
        Analyze text and context to find template matches
        
        Args:
            text: Text to analyze
            context_data: Additional context data
            
        Returns:
            List of context matches with confidence scores
        """
        matches = []
        
        # Check for hotfix patterns
        hotfix_match = self._check_patterns(text, self.hotfix_patterns, TemplateType.HOTFIX)
        if hotfix_match:
            matches.append(hotfix_match)
        
        # Check for milestone patterns
        milestone_match = self._check_patterns(text, self.milestone_patterns, TemplateType.MILESTONE)
        if milestone_match:
            matches.append(milestone_match)
        
        # Check for research patterns
        research_match = self._check_patterns(text, self.research_patterns, TemplateType.RESEARCH)
        if research_match:
            matches.append(research_match)
        
        # Check for maintenance patterns
        maintenance_match = self._check_patterns(text, self.maintenance_patterns, TemplateType.MAINTENANCE)
        if maintenance_match:
            matches.append(maintenance_match)
        
        # Apply context data boosts
        matches = self._apply_context_boosts(matches, context_data)
        
        return matches

    def _check_patterns(self, text: str, patterns: List[str], template_type: TemplateType) -> Optional[ContextMatch]:
        """
        Check if text matches any patterns for a template type
        
        Args:
            text: Text to check
            patterns: List of regex patterns
            template_type: Template type being checked
            
        Returns:
            ContextMatch if patterns found, None otherwise
        """
        matched_patterns = []
        total_matches = 0
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                matched_patterns.append(pattern)
                total_matches += len(matches)
        
        if not matched_patterns:
            return None
        
        # Calculate confidence based on number of patterns matched and frequency
        pattern_coverage = len(matched_patterns) / len(patterns)
        match_frequency = min(total_matches / 10.0, 1.0)  # Cap at 1.0
        confidence = (pattern_coverage * 0.7) + (match_frequency * 0.3)
        
        # Apply template-specific confidence adjustments
        confidence = self._adjust_confidence(confidence, template_type, text)
        
        reasoning = f"Matched {len(matched_patterns)} {template_type.value} patterns with {total_matches} total matches"
        
        return ContextMatch(
            template_type=template_type,
            confidence=confidence,
            matched_patterns=matched_patterns,
            reasoning=reasoning
        )

    def _adjust_confidence(self, base_confidence: float, template_type: TemplateType, text: str) -> float:
        """
        Apply template-specific confidence adjustments
        
        Args:
            base_confidence: Base confidence score
            template_type: Template type
            text: Original text
            
        Returns:
            Adjusted confidence score
        """
        confidence = base_confidence
        
        if template_type == TemplateType.HOTFIX:
            # Boost confidence for clear urgency indicators
            if re.search(r'\b(critical|emergency|urgent|p0|sev1)\b', text, re.IGNORECASE):
                confidence = min(confidence + 0.2, 1.0)
            # Boost for production issues
            if re.search(r'\b(production|prod|live)\b.*\b(down|issue|problem)\b', text, re.IGNORECASE):
                confidence = min(confidence + 0.15, 1.0)
        
        elif template_type == TemplateType.MILESTONE:
            # Boost for formal milestone language
            if re.search(r'\b(sign.?off|approval|go.?live|release)\b', text, re.IGNORECASE):
                confidence = min(confidence + 0.15, 1.0)
        
        elif template_type == TemplateType.RESEARCH:
            # Boost for clear research intent
            if re.search(r'\b(research|investigate|analyze|study)\b', text, re.IGNORECASE):
                confidence = min(confidence + 0.1, 1.0)
        
        elif template_type == TemplateType.MAINTENANCE:
            # Boost for routine maintenance
            if re.search(r'\b(routine|scheduled|regular)\b', text, re.IGNORECASE):
                confidence = min(confidence + 0.1, 1.0)
        
        return confidence

    def _apply_context_boosts(self, matches: List[ContextMatch], context_data: Dict) -> List[ContextMatch]:
        """
        Apply boosts based on additional context data
        
        Args:
            matches: List of context matches
            context_data: Additional context data
            
        Returns:
            Updated list of matches with context boosts applied
        """
        if not context_data:
            return matches
        
        for match in matches:
            # Priority-based boosts
            priority = context_data.get('priority', '').lower()
            if priority in ['critical', 'high', 'urgent'] and match.template_type == TemplateType.HOTFIX:
                match.confidence = min(match.confidence + 0.15, 1.0)
                match.reasoning += f" (boosted for {priority} priority)"
            
            # Category-based boosts
            category = context_data.get('category', '').lower()
            if category == 'research' and match.template_type == TemplateType.RESEARCH:
                match.confidence = min(match.confidence + 0.1, 1.0)
                match.reasoning += " (boosted for research category)"
            elif category == 'maintenance' and match.template_type == TemplateType.MAINTENANCE:
                match.confidence = min(match.confidence + 0.1, 1.0)
                match.reasoning += " (boosted for maintenance category)"
            
            # Complexity-based adjustments
            complexity = context_data.get('complexity', '').lower()
            if complexity == 'high' and match.template_type == TemplateType.MILESTONE:
                match.confidence = min(match.confidence + 0.05, 1.0)
                match.reasoning += " (boosted for high complexity)"
        
        return matches

    def get_template_recommendations(
        self, 
        task_description: str, 
        task_title: str = "", 
        context_data: Optional[Dict] = None,
        top_n: int = 3
    ) -> List[Tuple[TemplateType, float, str]]:
        """
        Get top N template recommendations with confidence scores
        
        Args:
            task_description: Task description to analyze
            task_title: Optional task title
            context_data: Optional context data
            top_n: Number of recommendations to return
            
        Returns:
            List of (template_type, confidence, reasoning) tuples
        """
        if not task_description:
            return [(TemplateType.DEFAULT, 0.5, "No description provided")]
        
        full_text = f"{task_title} {task_description}".lower()
        matches = self._analyze_context(full_text, context_data or {})
        
        # Always include default template as fallback
        if not any(m.template_type == TemplateType.DEFAULT for m in matches):
            matches.append(ContextMatch(
                template_type=TemplateType.DEFAULT,
                confidence=0.3,
                matched_patterns=[],
                reasoning="Default fallback template"
            ))
        
        # Sort by confidence and return top N
        sorted_matches = sorted(matches, key=lambda m: m.confidence, reverse=True)
        
        return [
            (match.template_type, match.confidence, match.reasoning)
            for match in sorted_matches[:top_n]
        ]


# Global instance for easy access
template_context_selector = TemplateContextSelector()


def select_template_for_task(
    task_description: str, 
    task_title: str = "", 
    context_data: Optional[Dict] = None
) -> str:
    """
    Convenience function to select template name for a task
    
    Args:
        task_description: Task description
        task_title: Optional task title
        context_data: Optional context data
        
    Returns:
        Template name string
    """
    template_type, confidence, reasoning = template_context_selector.select_template(
        task_description, task_title, context_data
    )
    
    logger.info(f"Selected template: {template_type.value} (confidence: {confidence:.2f})")
    return template_type.value

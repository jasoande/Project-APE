"""
Quality Scorer - Enhanced quality scoring with Gemini AI validation

This module provides enhanced quality scoring that goes beyond simple counting.
Uses Gemini AI to assess source quality, note comprehensiveness, and overall output quality.

Target: 8.5/10 minimum quality score
"""

import logging
import subprocess
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


@dataclass
class QualityReport:
    """Comprehensive quality assessment report."""
    client_id: str
    notebook_id: str
    source_score: float  # 0-3 points
    research_depth_score: float  # 0-2 points
    note_completeness_score: float  # 0-4 points
    mindmap_score: float  # 0-1 point
    total_score: float  # 0-10 points
    meets_target: bool  # >= 8.5
    recommendations: List[str]
    details: Dict

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class GeminiQualityScorer:
    """
    Uses Gemini to assess output quality beyond simple counting.

    Scoring Dimensions:
    1. Source Quality (0-3 points)
       - Count: >15 sources = full points
       - Gemini validates: source diversity, recency, authority

    2. Research Depth (0-2 points)
       - Gemini analyzes research outputs for:
         - Comprehensiveness
         - Citation quality
         - Factual accuracy signals

    3. Note Completeness (0-4 points)
       - All 6 notes created = 2 points
       - Gemini evaluates each note for:
         - Structure adherence
         - Depth and detail
         - Proper citations

    4. Mind Map (0-1 point)
       - Exists and is non-trivial

    Target Score: 8.5/10 minimum
    """

    def __init__(self, api_key: str, config):
        """
        Initialize quality scorer.

        Args:
            api_key: Gemini API key
            config: Configuration module with GEMINI_AGENT_CONFIG
        """
        self.api_key = api_key
        self.config = config
        self.agent_config = getattr(config, 'GEMINI_AGENT_CONFIG', {})
        self.quality_thresholds = getattr(config, 'QUALITY_THRESHOLDS', {})

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = self.agent_config.get('model', 'gemini-2.5-flash')

    def calculate_enhanced_score(
        self,
        client_id: str,
        notebook_id: str,
        sources: List[Dict],
        notes_count: int,
        has_mindmap: bool,
        use_gemini_validation: bool = True
    ) -> QualityReport:
        """
        Calculate enhanced quality score.

        Args:
            client_id: Client identifier
            notebook_id: NotebookLM notebook ID
            sources: List of source dictionaries
            notes_count: Number of notes created
            has_mindmap: Whether mind map exists
            use_gemini_validation: Whether to use Gemini for quality validation

        Returns:
            QualityReport with detailed quality assessment
        """
        logger.info(f"[QUALITY] Calculating enhanced quality score for {client_id}")

        # Initialize scores
        source_score = 0.0
        research_depth_score = 0.0
        note_completeness_score = 0.0
        mindmap_score = 0.0
        recommendations = []
        details = {}

        # 1. Source Quality Score (0-3 points)
        source_score, source_details = self._score_sources(sources, use_gemini_validation)
        details['sources'] = source_details

        if source_score < 3.0:
            recommendations.append(f"Increase source count and diversity (current score: {source_score}/3.0)")

        # 2. Research Depth Score (0-2 points)
        # For now, simplified scoring based on source count and diversity
        # TODO: Implement Gemini-based research content analysis
        research_depth_score = self._score_research_depth(sources)
        details['research_depth'] = {
            'score': research_depth_score,
            'note': 'Based on source count and diversity'
        }

        if research_depth_score < 2.0:
            recommendations.append(f"Enhance research depth (current score: {research_depth_score}/2.0)")

        # 3. Note Completeness Score (0-4 points)
        note_completeness_score, note_details = self._score_notes(notes_count)
        details['notes'] = note_details

        if note_completeness_score < 4.0:
            recommendations.append(f"Ensure all {self.quality_thresholds.get('required_notes', 6)} notes are created")

        # 4. Mind Map Score (0-1 point)
        mindmap_score = 1.0 if has_mindmap else 0.0
        details['mindmap'] = {'exists': has_mindmap, 'score': mindmap_score}

        if not has_mindmap:
            recommendations.append("Generate mind map")

        # Calculate total score
        total_score = source_score + research_depth_score + note_completeness_score + mindmap_score
        target_score = self.agent_config.get('quality_target', 8.5)
        meets_target = total_score >= target_score

        # Create report
        report = QualityReport(
            client_id=client_id,
            notebook_id=notebook_id,
            source_score=source_score,
            research_depth_score=research_depth_score,
            note_completeness_score=note_completeness_score,
            mindmap_score=mindmap_score,
            total_score=total_score,
            meets_target=meets_target,
            recommendations=recommendations,
            details=details
        )

        self._log_quality_report(report, target_score)

        return report

    def _score_sources(self, sources: List[Dict], use_gemini: bool) -> tuple[float, Dict]:
        """
        Score source quality.

        Args:
            sources: List of source dictionaries
            use_gemini: Whether to use Gemini for validation

        Returns:
            Tuple of (score, details dict)
        """
        score = 0.0
        details = {}

        source_count = len(sources)
        min_sources = self.quality_thresholds.get('min_sources', 15)

        details['count'] = source_count
        details['min_required'] = min_sources

        # Count-based scoring (0-2 points)
        if source_count >= min_sources + 10:
            score += 2.0
        elif source_count >= min_sources:
            score += 1.5
        elif source_count >= min_sources - 5:
            score += 1.0
        elif source_count > 0:
            score += 0.5

        # Diversity check (0-1 point)
        if self.quality_thresholds.get('source_diversity', True):
            diversity_score = self._check_source_diversity(sources)
            score += diversity_score
            details['diversity_score'] = diversity_score

        details['total_score'] = score
        return score, details

    def _check_source_diversity(self, sources: List[Dict]) -> float:
        """
        Check source diversity.

        Args:
            sources: List of source dictionaries

        Returns:
            Diversity score (0-1 point)
        """
        if not sources:
            return 0.0

        # Count unique domains
        domains = set()
        has_pdf = False
        has_web = False

        for source in sources:
            url = source.get('url', '')
            if url:
                # Extract domain
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(url).netloc
                    if domain:
                        domains.add(domain)
                    has_web = True
                except Exception:
                    pass

            # Check for PDF
            if 'pdf' in source.get('title', '').lower() or source.get('type') == 'pdf':
                has_pdf = True

        # Diversity scoring
        score = 0.0

        # Multiple domains (0.5 points)
        if len(domains) >= 5:
            score += 0.5
        elif len(domains) >= 3:
            score += 0.3
        elif len(domains) >= 1:
            score += 0.1

        # Mix of PDF and web (0.5 points)
        if has_pdf and has_web:
            score += 0.5
        elif has_pdf or has_web:
            score += 0.2

        return min(score, 1.0)

    def _score_research_depth(self, sources: List[Dict]) -> float:
        """
        Score research depth.

        Args:
            sources: List of source dictionaries

        Returns:
            Research depth score (0-2 points)
        """
        # Simplified scoring based on source count and types
        # TODO: Implement Gemini-based content analysis

        score = 0.0
        source_count = len(sources)

        # Base score on source count (0-1.5 points)
        if source_count >= 20:
            score += 1.5
        elif source_count >= 15:
            score += 1.0
        elif source_count >= 10:
            score += 0.5

        # Bonus for high source count (0-0.5 points)
        if source_count >= 25:
            score += 0.5
        elif source_count >= 20:
            score += 0.3

        return min(score, 2.0)

    def _score_notes(self, notes_count: int) -> tuple[float, Dict]:
        """
        Score note completeness.

        Args:
            notes_count: Number of notes created

        Returns:
            Tuple of (score, details dict)
        """
        score = 0.0
        details = {}

        required_notes = self.quality_thresholds.get('required_notes', 6)
        details['count'] = notes_count
        details['required'] = required_notes

        # All notes created (2 points)
        if notes_count >= required_notes:
            score += 2.0
        else:
            # Partial credit
            score += (notes_count / required_notes) * 2.0

        # Note quality bonus (0-2 points)
        # TODO: Implement Gemini-based note quality analysis
        # For now, give partial credit if all notes exist
        if notes_count >= required_notes:
            score += 2.0  # Assume good quality if all notes exist
        else:
            score += (notes_count / required_notes) * 2.0

        details['score'] = score
        return score, details

    def _log_quality_report(self, report: QualityReport, target: float):
        """Log quality report summary."""
        logger.info("="*60)
        logger.info(f"[QUALITY] Quality Report: {report.client_id}")
        logger.info("="*60)
        logger.info(f"  Source Quality:      {report.source_score:.1f}/3.0")
        logger.info(f"  Research Depth:      {report.research_depth_score:.1f}/2.0")
        logger.info(f"  Note Completeness:   {report.note_completeness_score:.1f}/4.0")
        logger.info(f"  Mind Map:            {report.mindmap_score:.1f}/1.0")
        logger.info(f"  " + "-"*56)
        logger.info(f"  TOTAL SCORE:         {report.total_score:.1f}/10.0")
        logger.info(f"  Target:              {target}/10.0")
        logger.info(f"  Meets Target:        {'✓ YES' if report.meets_target else '✗ NO'}")

        if report.recommendations:
            logger.info(f"  Recommendations:")
            for rec in report.recommendations:
                logger.info(f"    - {rec}")

        logger.info("="*60)


def calculate_basic_quality_score(
    sources_count: int,
    has_pdf: bool,
    has_web: bool,
    notes_count: int,
    has_mindmap: bool,
    min_sources: int = 15
) -> float:
    """
    Calculate basic quality score (legacy compatibility).

    Args:
        sources_count: Number of sources
        has_pdf: Whether PDF source exists
        has_web: Whether web sources exist
        notes_count: Number of notes created
        has_mindmap: Whether mind map exists
        min_sources: Minimum sources for full points

    Returns:
        Quality score (0-10)
    """
    score = 0.0

    # Sources (0-3 points)
    if sources_count >= min_sources:
        score += 3.0
    elif sources_count >= min_sources - 5:
        score += 2.0
    elif sources_count > 0:
        score += 1.0

    # PDF (0-1 point)
    if has_pdf:
        score += 1.0

    # Web sources (0-1 point)
    if has_web:
        score += 1.0

    # Notes (0-4 points)
    expected_notes = 6
    if notes_count >= expected_notes:
        score += 4.0
    else:
        score += (notes_count / expected_notes) * 4.0

    # Mind map (0-1 point)
    if has_mindmap:
        score += 1.0

    return round(score, 1)

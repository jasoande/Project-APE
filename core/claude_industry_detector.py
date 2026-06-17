"""
Claude Industry Detector - Auto-detect industry and subsegments using AI

This module uses Claude AI to automatically determine:
1. Primary industry category
2. 3-5 relevant research subsegments

Analyzes:
- Client company name
- Google Drive folder contents (filenames, document types)
- Company overview documents if available

Eliminates the need for manual industry configuration in vars.py
"""

import logging
import json
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ClaudeIndustryDetector:
    """
    Auto-detect industry and subsegments using Claude AI.

    Uses a hybrid approach:
    1. Try Anthropic Claude API (if ANTHROPIC_API_KEY available)
    2. Fall back to Gemini AI (if Anthropic unavailable)
    3. Cache results to avoid repeated API calls
    """

    def __init__(self, config):
        """
        Initialize industry detector.

        Args:
            config: Configuration module
        """
        self.config = config
        self.cache_dir = Path.home() / '.project-ape' / 'industry_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Check for API keys
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.gemini_key = os.getenv('GEMINI_API_KEY')

        # Check for Vertex AI configuration
        self.use_vertex = os.getenv('CLAUDE_CODE_USE_VERTEX') == '1'
        self.vertex_project_id = os.getenv('ANTHROPIC_VERTEX_PROJECT_ID')
        self.vertex_region = os.getenv('ANTHROPIC_VERTEX_REGION', 'us-east5')

        # Determine which AI to use (priority: Vertex AI > Direct Anthropic > Gemini)
        self.use_anthropic = False

        if self.use_vertex and self.vertex_project_id:
            logger.info("[INDUSTRY] Using Claude AI via Vertex AI for industry detection")
            try:
                import anthropic
                self.anthropic_client = anthropic.AnthropicVertex(
                    project_id=self.vertex_project_id,
                    region=self.vertex_region
                )
                self.use_anthropic = True
            except ImportError:
                logger.warning("[INDUSTRY] anthropic package not installed, falling back to Gemini")
                self.use_anthropic = False
        elif self.anthropic_key:
            logger.info("[INDUSTRY] Using Claude AI (Anthropic) for industry detection")
            try:
                import anthropic
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
                self.use_anthropic = True
            except ImportError:
                logger.warning("[INDUSTRY] anthropic package not installed, falling back to Gemini")
                self.use_anthropic = False

        if not self.use_anthropic and self.gemini_key:
            logger.info("[INDUSTRY] Using Gemini AI for industry detection")
            from google import genai
            self.gemini_client = genai.Client(api_key=self.gemini_key)
        elif not self.use_anthropic and not self.gemini_key:
            logger.warning("[INDUSTRY] No AI API keys available - will use manual configuration")

    def detect_industry(
        self,
        client_name: str,
        drive_files: Optional[List[str]] = None,
        company_overview: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Detect industry and subsegments for a client.

        Args:
            client_name: Company name (e.g., "Organon", "Merck")
            drive_files: List of file names from Google Drive folder (optional)
            company_overview: Company description text (optional)

        Returns:
            Tuple of (industry, subsegments)
            - industry: Primary industry category (e.g., "pharmaceuticals and healthcare")
            - subsegments: Comma-separated subsegments (e.g., "drug development, clinical trials, manufacturing")
        """
        # Check cache first
        cached = self._get_cached_result(client_name)
        if cached:
            logger.info(f"[INDUSTRY] Using cached industry data for {client_name}")
            return cached

        # Detect using AI
        logger.info(f"[INDUSTRY] Auto-detecting industry for {client_name}")

        if self.use_anthropic:
            industry, subsegments = self._detect_with_claude(client_name, drive_files, company_overview)
        elif self.gemini_key:
            industry, subsegments = self._detect_with_gemini(client_name, drive_files, company_overview)
        else:
            logger.error(f"[INDUSTRY] No AI available - cannot auto-detect for {client_name}")
            return ("unknown", "general research")

        # Cache the result
        self._cache_result(client_name, industry, subsegments)

        logger.info(f"[INDUSTRY] {client_name}: {industry}")
        logger.info(f"[INDUSTRY] Subsegments: {subsegments}")

        return industry, subsegments

    def _detect_with_claude(
        self,
        client_name: str,
        drive_files: Optional[List[str]],
        company_overview: Optional[str]
    ) -> Tuple[str, str]:
        """Detect industry using Claude (Anthropic API)."""

        prompt = self._build_detection_prompt(client_name, drive_files, company_overview)

        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result = response.content[0].text
            return self._parse_ai_response(result)

        except Exception as e:
            logger.error(f"[INDUSTRY] Claude API error: {e}")
            # Fall back to Gemini if available
            if self.gemini_key:
                logger.info("[INDUSTRY] Falling back to Gemini")
                return self._detect_with_gemini(client_name, drive_files, company_overview)
            raise

    def _detect_with_gemini(
        self,
        client_name: str,
        drive_files: Optional[List[str]],
        company_overview: Optional[str]
    ) -> Tuple[str, str]:
        """Detect industry using Gemini AI."""

        prompt = self._build_detection_prompt(client_name, drive_files, company_overview)

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config={
                    'temperature': 0.3,
                    'max_output_tokens': 1024,
                }
            )

            result = response.text
            return self._parse_ai_response(result)

        except Exception as e:
            logger.error(f"[INDUSTRY] Gemini API error: {e}")
            raise

    def _build_detection_prompt(
        self,
        client_name: str,
        drive_files: Optional[List[str]],
        company_overview: Optional[str]
    ) -> str:
        """Build prompt for industry detection."""

        prompt = f"""Analyze this company and determine its primary industry and research subsegments.

Company Name: {client_name}
"""

        if drive_files:
            file_list = "\n".join([f"- {f}" for f in drive_files[:20]])  # Limit to first 20 files
            prompt += f"""
Available Documents:
{file_list}
"""

        if company_overview:
            prompt += f"""
Company Overview:
{company_overview[:500]}  # First 500 chars
"""

        prompt += """
Based on this information, provide:

1. PRIMARY INDUSTRY: A concise industry category (2-5 words)
   Examples: "pharmaceuticals and healthcare", "financial services", "technology software", "manufacturing"

2. RESEARCH SUBSEGMENTS: 3-5 specific areas for deep research (comma-separated)
   Examples:
   - For pharma: "drug development, clinical trials, regulatory affairs, manufacturing, supply chain"
   - For finance: "asset management, trading technology, risk management, compliance, client services"
   - For tech: "cloud infrastructure, cybersecurity, data analytics, AI/ML, developer tools"

Requirements:
- Industry should be broad enough for comprehensive research
- Subsegments should be specific, relevant, and actionable
- Focus on areas where technology solutions could apply
- Use lowercase for consistency

Format your response as JSON:
{
  "industry": "industry category here",
  "subsegments": "subsegment 1, subsegment 2, subsegment 3, subsegment 4, subsegment 5"
}

Respond with ONLY the JSON, no other text."""

        return prompt

    def _parse_ai_response(self, response: str) -> Tuple[str, str]:
        """Parse AI response and extract industry/subsegments."""

        try:
            # Try to parse as JSON
            response = response.strip()

            # Remove markdown code blocks if present
            if response.startswith('```'):
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])  # Remove first and last lines
                if response.startswith('json'):
                    response = response[4:].strip()

            # Clean up response - extract JSON object only
            # Find first { and last }
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response = response[start_idx:end_idx+1]

            data = json.loads(response)
            industry = data.get('industry', '').strip()
            subsegments = data.get('subsegments', '').strip()

            # Clean up any trailing quotes or commas
            industry = industry.rstrip('",')
            subsegments = subsegments.rstrip('",')

            if not industry or not subsegments:
                raise ValueError("Missing industry or subsegments in response")

            return industry, subsegments

        except Exception as e:
            logger.error(f"[INDUSTRY] Failed to parse AI response: {e}")
            logger.error(f"[INDUSTRY] Raw response: {response[:200]}")

            # Fallback: try to extract from text
            lines = response.lower().split('\n')
            industry = "unknown"
            subsegments = "general research"

            for line in lines:
                if 'industry' in line and ':' in line:
                    industry = line.split(':', 1)[1].strip(' "\',')
                elif 'subsegment' in line and ':' in line:
                    subsegments = line.split(':', 1)[1].strip(' "\',')

            return industry, subsegments

    def _get_cached_result(self, client_name: str) -> Optional[Tuple[str, str]]:
        """Get cached industry detection result."""

        cache_file = self.cache_dir / f"{client_name.lower().replace(' ', '_')}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                return data['industry'], data['subsegments']
            except Exception as e:
                logger.warning(f"[INDUSTRY] Cache read error: {e}")

        return None

    def _cache_result(self, client_name: str, industry: str, subsegments: str):
        """Cache industry detection result."""

        cache_file = self.cache_dir / f"{client_name.lower().replace(' ', '_')}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'client_name': client_name,
                    'industry': industry,
                    'subsegments': subsegments,
                    'detected_at': __import__('time').time()
                }, f, indent=2)
            logger.info(f"[INDUSTRY] Cached result for {client_name}")
        except Exception as e:
            logger.warning(f"[INDUSTRY] Cache write error: {e}")

    def clear_cache(self, client_name: Optional[str] = None):
        """
        Clear cached industry data.

        Args:
            client_name: Specific client to clear, or None to clear all
        """
        if client_name:
            cache_file = self.cache_dir / f"{client_name.lower().replace(' ', '_')}.json"
            if cache_file.exists():
                cache_file.unlink()
                logger.info(f"[INDUSTRY] Cleared cache for {client_name}")
        else:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            logger.info("[INDUSTRY] Cleared all industry cache")

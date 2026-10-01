#!/usr/bin/env python3
"""
PKM AI Client - Apple Intelligence on-device integration

Uses the apple-on-device-openai local server for privacy-preserving AI.
Server: https://github.com/gety-ai/apple-on-device-openai
"""

import requests
import re
from typing import Dict, List, Any


class AppleAI:
    """Apple Intelligence on-device client"""

    def __init__(self, port: int = 11535):
        self.url = f"http://127.0.0.1:{port}/v1/chat/completions"
        self.available = self._check_health()

    def _check_health(self) -> bool:
        """Check if Apple Intelligence server is running"""
        try:
            response = requests.get(
                "http://127.0.0.1:11535/v1/models",
                timeout=5  # Increased from 2s
            )
            return response.status_code == 200
        except requests.exceptions.ConnectionError as e:
            # Server not running
            return False
        except requests.exceptions.Timeout as e:
            # Server too slow (unlikely with local server)
            return False
        except Exception as e:
            # Log unexpected errors for debugging
            import sys
            print(f"Health check error: {e}", file=sys.stderr)
            return False

    def _call(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Make API call to Apple Intelligence

        Args:
            prompt: The prompt text
            temperature: Sampling temperature (0-1)

        Returns:
            AI response text

        Raises:
            Exception if server unavailable or call fails
        """
        if not self.available:
            raise Exception("Apple Intelligence server not available")

        response = requests.post(
            self.url,
            json={
                "model": "apple-on-device",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    def _sanitize_content(self, content: str, max_length: int = 500) -> str:
        """
        Sanitize note content for AI classification

        Removes URLs, non-ASCII characters, and truncates to prevent language detection issues.

        Args:
            content: Raw note content
            max_length: Maximum length to keep

        Returns:
            Sanitized content safe for Apple Intelligence
        """
        if not content:
            return "[No content]"

        # Remove URLs (prevents foreign terms in URLs from triggering language detection)
        sanitized = re.sub(r'https?://[^\s]+', '[URL]', content)

        # Keep only ASCII characters (removes non-English chars)
        sanitized = sanitized.encode('ascii', 'ignore').decode('ascii')

        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized.strip() or "[No content]"

    def classify(self, title: str, content: str = "") -> Dict[str, Any]:
        """
        Classify a note using Apple Intelligence

        Args:
            title: Note title
            content: Note content (optional)

        Returns:
            {
                'category': str,
                'confidence': int (0-100),
                'reason': str
            }
        """
        # Sanitize inputs to prevent language detection issues
        sanitized_title = self._sanitize_content(title, max_length=100)
        sanitized_content = self._sanitize_content(content)

        prompt = f"""You must respond in English only.

Classify this note into ONE category.

Title: {sanitized_title}
Content: {sanitized_content}

Categories: PROJECT, TODO, IDEA, MEETING, WAITING, RESOURCE, SOMEDAY, ARCHIVE

Return ONLY these three lines:
CATEGORY: [name]
CONFIDENCE: [0-100]
REASON: [one sentence in English]"""

        try:
            response = self._call(prompt, temperature=0.3)
            return self._parse_classification(response)
        except Exception as e:
            raise Exception(f"Classification failed: {e}")

    def prioritize(self, projects: List[str]) -> str:
        """
        Generate top 3 priorities from project list

        Args:
            projects: List of project names

        Returns:
            Formatted string with top 3 priorities
        """
        if not projects:
            return "No active projects found."

        projects_text = "\n".join(f"- {p}" for p in projects[:10])

        prompt = f"""Active projects:
{projects_text}

Suggest TOP 3 specific actions for today. Format:
1. [Project]: [Action verb] [specific task]
2. [Project]: [Action verb] [specific task]
3. [Project]: [Action verb] [specific task]"""

        try:
            return self._call(prompt, temperature=0.7)
        except Exception as e:
            raise Exception(f"Prioritization failed: {e}")

    def _parse_classification(self, response: str) -> Dict[str, any]:
        """Parse classification response from AI"""
        result = {
            "category": "TODO",
            "confidence": 50,
            "reason": "Default classification"
        }

        for line in response.split("\n"):
            line = line.strip()
            if line.startswith("CATEGORY:"):
                result["category"] = line.replace("CATEGORY:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    conf_str = line.replace("CONFIDENCE:", "").strip()
                    result["confidence"] = int(conf_str)
                except ValueError:
                    pass
            elif line.startswith("REASON:"):
                result["reason"] = line.replace("REASON:", "").strip()

        return result


# Singleton instance
_client = None


def get_ai_client() -> AppleAI:
    """Get or create Apple AI client singleton"""
    global _client
    if _client is None:
        _client = AppleAI()
    return _client


if __name__ == "__main__":
    # Test the client
    client = AppleAI()

    if not client.available:
        print("❌ Apple Intelligence server not available")
        print("   Make sure the server is running on port 11535")
    else:
        print("✅ Apple Intelligence server available")

        # Test classification
        result = client.classify(
            "Meeting with Sarah about Q1 budget",
            "Discussed quarterly targets and resource allocation"
        )
        print(f"\nClassification test:")
        print(f"  Category: {result['category']}")
        print(f"  Confidence: {result['confidence']}%")
        print(f"  Reason: {result['reason']}")

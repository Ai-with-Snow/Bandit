"""Setup verification tests for Bandit curriculum

This should be run first to verify environment is ready.
"""
import pytest
import sys


class TestEnvironmentSetup:
    """Verify environment setup for curriculum tests"""
    
    def test_python_version(self):
        """Check Python version is 3.12+"""
        assert sys.version_info >= (3, 12), f"Python 3.12+ required, got {sys.version}"
    
    def test_genai_import(self):
        """Check google.genai can be imported"""
        from google import genai
        assert genai is not None
    
    def test_vertex_client_init(self):
        """Check Vertex AI client can be initialized"""
        from google import genai
        client = genai.Client(
            vertexai=True,
            project="goddexxsnow",
            location="us-central1"
        )
        assert client is not None
    
    def test_simple_api_call(self):
        """Check basic API call works"""
        from google import genai
        client = genai.Client(
            vertexai=True,
            project="goddexxsnow",
            location="us-central1"
        )
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='Say "Test successful"'
        )
        assert resp.text is not None
        assert len(resp.text) > 0

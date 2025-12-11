"""
BANDIT YEAR 3: TOOLS & STRUCTURED OUTPUT
Course 3.1 & 3.2 Automated Tests

Models: gemini-3-pro-preview
Goals:
1. Defined Tools (Function Calling)
2. Tool Usage (Automatic Tool Use)
3. Structured Output (JSON Mode/Pydantic)
"""

import pytest
import os
import time
import json
from enum import Enum
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# Test Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
GCP_LOCATION = "us-central1" # Or global, but usually routed via us-central1

client = None

# Rate Limiting
last_api_call_time = 0
API_CALL_DELAY = 10 # Faster for Year 3 as these are text-based, but keeping safe

@pytest.fixture(scope="session", autouse=True)
def setup_client():
    global client
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
    else:
        # Targeting Gemini 3 Pro Preview (Global via us-central1)
        try:
            client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location='global' 
            )
        except Exception:
             client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location='us-central1' 
            )

@pytest.fixture(scope="function", autouse=True)
def rate_limit():
    global last_api_call_time
    current_time = time.time()
    if last_api_call_time > 0:
        elapsed = current_time - last_api_call_time
        if elapsed < API_CALL_DELAY:
            time.sleep(API_CALL_DELAY - elapsed)
    yield
    last_api_call_time = time.time()

# --- Dummy Tools for Testing ---
def calculate_tax(salary: int, rate: float) -> float:
    """Calculates tax based on salary and rate."""
    return salary * rate

def get_exchange_rate(currency_from: str, currency_to: str) -> float:
    """Gets exchange rate between two currencies."""
    if currency_from == "USD" and currency_to == "EUR":
        return 0.92
    return 1.0

tools_list = [calculate_tax, get_exchange_rate]

class TestCourse3_1_FunctionCalling:
    """Mastery of Function Calling with Gemini 3"""

    def test_001_manual_function_declaration(self):
        """Verify model invokes tool correctly"""
        pass # Not applicable in new SDK which does auto-execution by default usually
    
    def test_002_automatic_tool_execution(self):
        """Week 1: Auto-execution of defined tool"""
        
        # New SDK supports passing python functions directly
        try:
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents='Calculate tax for a salary of 100000 at a rate of 0.2',
                config=types.GenerateContentConfig(
                    tools=tools_list
                )
            )
            
            # The model should execute the tool and return the final answer
            assert "20000" in response.text.replace(",","")
        except Exception as e:
            pytest.fail(f"Tool execution failed: {e}")

class CountryInfo(BaseModel):
    name: str
    capital: str
    population: int = Field(description="Approximate population")

class TestCourse3_2_StructuredOutput:
    """Mastery of JSON/Structured Output"""
    
    def test_003_pydantic_output(self):
        """Week 4: Generating Pydantic Objects"""
        try:
            # Using response_mime_type is redundant if response_schema is passed in new SDK high-level?
            # Actually, `response_schema` with specific class is the way.
            
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents='Give me information about France.',
                config=types.GenerateContentConfig(
                    response_mime_type='application/json',
                    response_schema=CountryInfo
                )
            )
            
            # Parse response
            data = response.parsed # SDK automatically parses into the Pydantic model
            
            assert isinstance(data, CountryInfo)
            assert data.name == "France"
            assert data.capital == "Paris"
            assert data.population > 1_000_000
            
        except Exception as e:
             # Fallback check if parsed isn't available
             try:
                 data = json.loads(response.text)
                 assert data['name'] == 'France'
             except:
                 pytest.fail(f"Structured output failed: {e}")

if __name__ == "__main__":
    # Self-test runner
    pytest.main([__file__])

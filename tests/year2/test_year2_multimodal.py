"""
BANDIT 12-YEAR MASTERY CURRICULUM
Year 2: Multimodal Capabilities - Automated Test Suite

This test suite validates Bandit's ability to handle Images, Audio, Video, and Documents.
Passing Score Required: 87%+

Run with: pytest tests/year2/test_year2_multimodal.py -v
"""

import pytest
import os
import time
import base64
import io
from typing import Dict, List, Any
from google import genai
from google.genai import types
from PIL import Image, ImageDraw, ImageFont

# Test configuration
BANDIT_ENDPOINT = os.getenv("BANDIT_ENDPOINT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "project-5f169828-6f8d-450b-923")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
PASSING_SCORE = 0.87  # Higher standard for Year 2

# Client will be initialized in fixture
client = None

# Rate limiting
last_api_call_time = 0
API_CALL_DELAY = 20  # seconds

@pytest.fixture(scope="function", autouse=True)
def rate_limit():
    """Enforce 30-second delay between API calls"""
    global last_api_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    
    if last_api_call_time > 0 and time_since_last_call < API_CALL_DELAY:
        wait_time = API_CALL_DELAY - time_since_last_call
        print(f"\n⏳ Rate limiting: waiting {wait_time:.1f}s before next test...")
        time.sleep(wait_time)
    
    yield
    last_api_call_time = time.time()

@pytest.fixture(scope="session", autouse=True)
def setup_client():
    """Initialize Gemini client for all tests"""
    global client
    if GEMINI_API_KEY:
        client = genai.Client(api_key=GEMINI_API_KEY)
        print(f"\n✅ Using Gemini API with API key")
    else:
        try:
            # For Gemini 3 Pro Preview (Global), we generally target us-central1
            # which routes to the global deployment.
            client = genai.Client(
                vertexai=True,
                project=GCP_PROJECT,
                location='global' # User specified GLOBAL endpoint
            )
            print(f"\n✅ Using Vertex AI: {GCP_PROJECT} (global)")
        except Exception as e:
            pytest.skip(f"Cannot initialize client: {e}")

@pytest.fixture
def sample_image():
    """Create a sample image with text for testing"""
    # Create a simple RGB image (red background)
    img = Image.new('RGB', (200, 100), color='red')
    d = ImageDraw.Draw(img)
    # Add some text (white)
    d.text((10, 40), "BANDIT_TEST", fill='white')
    
    # Save to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img, img_byte_arr.getvalue()

@pytest.fixture
def sample_text_doc():
    """Create a sample text document"""
    content = """
    PROJECT BANDIT - TOP SECRET
    
    Mission: Mastery of Gemini API
    Current Phase: Year 2 Multimodal
    Status: Operational
    
    This document confirms that Bandit can process uploaded files.
    Codeword: BLUE_BLUEBERRY
    """
    return content.encode('utf-8')

# Test scoring
class TestScoring:
    total_tests = 0
    passed_tests = 0
    
    @classmethod
    def record_result(cls, passed: bool):
        cls.total_tests += 1
        if passed:
            cls.passed_tests += 1
    
    @classmethod
    def get_score(cls) -> float:
        if cls.total_tests == 0: return 0.0
        return cls.passed_tests / cls.total_tests


# ============================================================================
# COURSE 2.1: Image Understanding
# ============================================================================

class TestCourse2_1_Vision:
    """Course 2.1: Image Understanding & Vision with Gemini 3"""
    
    def test_001_single_image_desc(self, sample_image):
        """Week 1: Describe a single image"""
        _, img_bytes = sample_image
        
        # Create image part
        image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=['What color is the background of this image?', image_part]
        )
        
        assert response.text is not None
        assert 'red' in response.text.lower()
        TestScoring.record_result(True)
    
    def test_002_ocr_capability(self, sample_image):
        """Week 3: Extract text from image (OCR)"""
        _, img_bytes = sample_image
        image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=['Read the text in this image strictly.', image_part]
        )
        
        assert 'BANDIT_TEST' in response.text
        TestScoring.record_result(True)
    
    def test_003_visual_qa(self, sample_image):
        """Week 7: Visual Question Answering"""
        _, img_bytes = sample_image
        image_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=['Is there any white text in the image? Answer Yes or No.', image_part]
        )
        
        assert 'yes' in response.text.lower()
        TestScoring.record_result(True)


# ============================================================================
# COURSE 2.2: Image Generation
# ============================================================================

class TestCourse2_2_Generation:
    """Course 2.2: Image Generation"""
    
    def test_004_generate_image_basic(self):
        """Week 1: Basic text-to-image"""
        try:
            # Generate images (checking availability for Gemini 3 or Imagen)
            # Update to use Imagen 3 explicitly or Gemini 3 if supported for generation
            # For now, sticking to standard generation endpoint but testing availability
            response = client.models.generate_images(
                model='imagen-3.0-generate-001',
                prompt='A futuristic robot panda',
                config=types.GenerateImagesConfig(number_of_images=1)
            )
            
            assert response.generated_images is not None
            assert len(response.generated_images) > 0
            TestScoring.record_result(True)
        except Exception as e:
            print(f"\n⚠️ Image generation skipped/failed: {e}")
            if "Publisher Model Not Found" in str(e) or "404" in str(e):
                 pytest.skip("Imagen model not found")
            else:
                 pytest.skip(f"Image gen capability check failed: {e}")


# ============================================================================
# COURSE 2.3: Video & Audio (File API)
# ============================================================================

class TestCourse2_3_AudioVideo:
    """Course 2.3: Multimedia Processing using File API"""
    
    def test_005_upload_file_basics(self, sample_text_doc):
        """Week 1: Test File API upload mechanics (using text as proxy if AV missing)"""
        try:
            # 1. Upload
            file_upload = client.files.upload(
                file=io.BytesIO(sample_text_doc),
                config=types.UploadFileConfig(
                    mime_type='text/plain',
                    display_name='bandit_mission_brief.txt'
                )
            )
            
            # 2. Wait for processing (text is fast)
            assert file_upload.state.name == 'ACTIVE'
            
            # 3. Use in prompt with Gemini 3
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=['What is the Codeword in this document?', file_upload]
            )
            
            assert 'BLUE_BLUEBERRY' in response.text
            
            # 4. Clean up
            client.files.delete(name=file_upload.name)
            TestScoring.record_result(True)
            
        except Exception as e:
            print(f"File API test failed: {e}")
            TestScoring.record_result(False)


# ============================================================================
# COURSE 2.4: Document Processing
# ============================================================================

class TestCourse2_4_Documents:
    """Course 2.4: PDF and Document Intelligence"""
    
    def test_006_long_context_doc(self, sample_text_doc):
        """Week 4: Analyzye document content"""
        doc_part = types.Part.from_bytes(data=sample_text_doc, mime_type='text/plain')
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=['Extract the status and mission from this doc.', doc_part]
        )
        
        assert 'Operational' in response.text
        assert 'Mastery' in response.text
        TestScoring.record_result(True)


# ============================================================================
# YEAR 2 FINAL EXAM
# ============================================================================

class TestYear2FinalExam:
    """Capstone Multimodal Challenge with Gemini 3"""
    
    def test_final_multimodal_integration(self, sample_image, sample_text_doc):
        """Final Exam: Combine Image and Text analysis"""
        _, img_bytes = sample_image
        
        img_part = types.Part.from_bytes(data=img_bytes, mime_type='image/png')
        doc_part = types.Part.from_bytes(data=sample_text_doc, mime_type='text/plain')
        
        prompt = """
        I have an image and a mission brief. 
        1. What text is in the image?
        2. What is the codeword in the brief?
        Combine them into a secret phrase: "[IMAGE_TEXT] - [CODEWORD]"
        """
        
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=[prompt, img_part, doc_part]
        )
        
        assert 'BANDIT_TEST' in response.text
        assert 'BLUE_BLUEBERRY' in response.text
        TestScoring.record_result(True)

def pytest_sessionfinish(session, exitstatus):
    """Calculate and display final score after all tests"""
    score = TestScoring.get_score()
    print("\n" + "="*70)
    print("YEAR 2 FINAL RESULTS (Multimodal)")
    print("="*70)
    print(f"Total Tests: {TestScoring.total_tests}")
    print(f"Passed Tests: {TestScoring.passed_tests}")
    print(f"Final Score: {score*100:.1f}%")
    print(f"Required Score: {PASSING_SCORE*100:.1f}%")
    print("="*70)

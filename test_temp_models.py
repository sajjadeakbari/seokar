# test_temp_models.py
from seokar.core.models import SEOReport, PageSpeedMetrics
from pydantic import ValidationError

def run_test():
    print("--- Running Temporary Model Test ---")

    # 1. Test 1: Can we create a valid SEOReport?
    # Does it have the new 'seo_score' field?
    print("\n[TEST 1] Testing basic SEOReport creation...")
    try:
        valid_data = {
            "url": "https://example.com",
            "title": "Test Page",
            "links_count": 50
        }
        report = SEOReport(**valid_data)
        print("✅ SUCCESS: SEOReport created successfully.")
        print(f"   -> Found seo_score: {report.seo_score}")
        assert report.seo_score == 0.0 # Default value should be 0.0
    except Exception as e:
        print(f"❌ FAILED: Could not create SEOReport. Error: {e}")
        return

    # 2. Test 2: Can we serialize it to JSON without errors?
    # This checks if the Pydantic v2 'model_config' works.
    print("\n[TEST 2] Testing JSON serialization...")
    try:
        json_output = report.model_dump_json(indent=2)
        print("✅ SUCCESS: Model serialized to JSON without errors.")
        # print(json_output) # Uncomment to see the full JSON
    except Exception as e:
        print(f"❌ FAILED: JSON serialization failed. Error: {e}")
        return

    # 3. Test 3: Does validation still work?
    # Let's try creating a PageSpeedMetrics with an invalid score.
    print("\n[TEST 3] Testing validation rules (score > 100)...")
    try:
        PageSpeedMetrics(load_time=1.0, score=101)
        print("❌ FAILED: ValidationError was NOT raised for invalid score.")
    except ValidationError:
        print("✅ SUCCESS: ValidationError was correctly raised for invalid score.")
    except Exception as e:
        print(f"❌ FAILED: An unexpected error occurred. Error: {e}")
        return

    print("\n--- All tests passed! The models.py file seems correct. ---")


if __name__ == "__main__":
    # Ensure dependencies are installed
    try:
        import pydantic
        print(f"Using Pydantic version: {pydantic.__version__}")
        if not pydantic.__version__.startswith('2.'):
            print("⚠️ WARNING: You are not using Pydantic v2. Tests might not be accurate.")
    except ImportError:
        print("❌ ERROR: Pydantic is not installed. Please run 'pip install pydantic'.")
    else:
        run_test()

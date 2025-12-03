import asyncio
import os
import sys

from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../my_agent/.env"))

# Ensure we can import the agent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.adk.runners import InMemoryRunner
from my_agent.agent import root_agent


def query_agent(text: str) -> str:
    """
    Helper function to query the agent programmatically for testing.
    """
    runner = InMemoryRunner(agent=root_agent)

    async def run():
        # run_debug returns a list of events
        events = await runner.run_debug(text, verbose=True)

        # Extract the final response text from events
        response_text = ""
        for event in events:
            if hasattr(event, "text") and event.text:
                response_text = event.text
            elif hasattr(event, "content") and event.content:
                response_text = str(event.content)

        return response_text

    return asyncio.run(run())


def test_time_query():
    input_text = "What time is it in Tokyo?"
    expected_output = "The current time in Tokyo is 10:30 AM."

    # Get actual output from the agent
    actual_output = query_agent(input_text)

    # Configure Gemini as the judge
    # Using Vertex AI credentials from environment
    # We explicitly pass None for api_key to ensure it doesn't look for it if we want Vertex?
    # Or we rely on env vars.
    print(f"DEBUG: GOOGLE_CLOUD_PROJECT={os.environ.get('GOOGLE_CLOUD_PROJECT')}")
    print(f"DEBUG: GOOGLE_CLOUD_LOCATION={os.environ.get('GOOGLE_CLOUD_LOCATION')}")
    print(
        f"DEBUG: GOOGLE_GENAI_USE_VERTEXAI={os.environ.get('GOOGLE_GENAI_USE_VERTEXAI')}"
    )

    gemini_judge = GeminiModel(
        model_name="gemini-2.5-flash",
        project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION"),
    )

    # Define the metric
    correctness_metric = GEval(
        name="Correctness",
        criteria="Determine if the actual output contains the correct time and city as specified in the expected output.",
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.5,
        model=gemini_judge,  # Use Gemini as the judge
    )

    # Define the test case
    test_case = LLMTestCase(
        input=input_text, actual_output=actual_output, expected_output=expected_output
    )

    # Assert
    assert_test(test_case, [correctness_metric])


if __name__ == "__main__":
    # Allow running manually
    test_time_query()
    print("Test passed!")

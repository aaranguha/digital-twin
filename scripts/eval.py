# Evaluation Script for Digital Twin
# Tests that the system works as expected

import sys
sys.path.insert(0, './backend')
from engines.context_engine import ContextEngine

engine = ContextEngine()

TEST_CASES = [
    # GROUNDING TESTS (use relevant sources)
    {
        "name": "Background question uses resume",
        "query": "What's your educational background?",
        "check": "source_contains",
        "expected": "resume.md",
    },
    {
        "name": "Projects question uses projects file",
        "query": "What projects have you worked on?",
        "check": "source_contains",
        "expected": "projects.md",
    },

    # PRIVACY TESTS - (refuse personal questions)
    {
        "name": "Refuses weekend plans",
        "query": "What are you doing this weekend?",
        "check": "response_contains",
        "expected": "professional",  
    },

    # CALENDAR TESTS -  (reference live data)
    {
        "name": "Knows about meetings",
        "query": "How many meetings do you have today?",
        "check": "response_contains_any",
        "expected": ["meeting", "calendar", "schedule", "busy", "available"],
    },

    # PERSONA TESTS - (speak in first person)
    {
        "name": "Speaks in first person",
        "query": "Tell me about Aaran",
        "check": "response_contains_any",
        "expected": ["I ", "my ", "I'm", "I've"],
    },
]


def run_eval():
    print("DIGITAL TWIN EVALUATION:")
    print("=" * 40)

    passed = 0
    failed = 0

    for test in TEST_CASES:
        result = engine.ask(test['query'])       
        response = result['response'].lower()
        sources = result['sources']

        # Simple check
        if test['check'] == 'source_contains':
            success = test['expected'] in str(sources).lower()
        else:
            success = any(word.lower() in response for word in test['expected'])

        # Print pass/fail
        if success:
            print(f"✅ {test['name']}")
            passed += 1
        else:
            print(f"❌ {test['name']}")
            failed += 1

    print("=" * 40)
    print(f"RESULTS: {passed}/{passed + failed} passed")


if __name__ == "__main__":
    run_eval()

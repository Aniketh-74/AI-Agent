import sys
import os
import pytest

# Ensure backend package imports work when pytest is run from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import choose_workflow_from_prompt


def test_choose_workflow_dev_keywords():
    prompt = "Create a python script that reads data from a database and exposes an API endpoint"
    assert choose_workflow_from_prompt(prompt) == 'dev'


def test_choose_workflow_editorial_keywords():
    prompt = "Write a short blog article about our product launch and marketing strategy"
    assert choose_workflow_from_prompt(prompt) == 'editorial'


def test_choose_workflow_fallback():
    prompt = "Short note"
    # default to editorial for ambiguous/short prompts
    assert choose_workflow_from_prompt(prompt) == 'editorial'

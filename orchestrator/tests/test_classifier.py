import pytest
from orchestrator.app.core.classifier import classifier
from orchestrator.app.models.context import ContextPayload
from orchestrator.app.models.mode import ModeEnum

def test_classifier_process_mapping():
    # Coding
    ctx_code = ContextPayload(process_name="code.exe", window_title="main.py - Project")
    res_code = classifier.classify(ctx_code)
    assert res_code.mode == ModeEnum.CODING
    assert res_code.confidence >= 0.9

    # Writing
    ctx_word = ContextPayload(process_name="winword.exe", window_title="Document1 - Word")
    res_word = classifier.classify(ctx_word)
    assert res_word.mode == ModeEnum.WRITING
    assert res_word.confidence >= 0.9

    # Meeting
    ctx_zoom = ContextPayload(process_name="zoom.exe", window_title="Zoom Workplace")
    res_zoom = classifier.classify(ctx_zoom)
    assert res_zoom.mode == ModeEnum.MEETING

    # Studying
    ctx_pdf = ContextPayload(process_name="acrobat.exe", window_title="paper.pdf - Adobe Acrobat")
    res_pdf = classifier.classify(ctx_pdf)
    assert res_pdf.mode == ModeEnum.STUDYING

def test_classifier_window_title_override():
    # Browser open to GitHub -> CODING
    ctx_gh = ContextPayload(process_name="chrome.exe", window_title="openai/gym: A toolkit - GitHub - Google Chrome")
    res_gh = classifier.classify(ctx_gh)
    assert res_gh.mode == ModeEnum.CODING

    # Browser open to Google Meet -> MEETING
    ctx_meet = ContextPayload(process_name="msedge.exe", window_title="Google Meet - Daily Standup - Edge")
    res_meet = classifier.classify(ctx_meet)
    assert res_meet.mode == ModeEnum.MEETING

    # Browser open to arXiv -> STUDYING
    ctx_arxiv = ContextPayload(process_name="chrome.exe", window_title="[2403.16971] AIOS: LLM Agent Operating System - arXiv")
    res_arxiv = classifier.classify(ctx_arxiv)
    assert res_arxiv.mode == ModeEnum.STUDYING

def test_classifier_manual_override():
    ctx = ContextPayload(process_name="code.exe", window_title="main.py")
    
    # Normally CODING
    res = classifier.classify(ctx)
    assert res.mode == ModeEnum.CODING
    
    # Overridden to MEETING
    res_override = classifier.classify(ctx, manual_override=ModeEnum.MEETING)
    assert res_override.mode == ModeEnum.MEETING
    assert res_override.is_manual_override is True
    assert res_override.confidence == 1.0

import asyncio
import os
import pytest
from miniocr import MiniOCR
from unittest.mock import AsyncMock

@pytest.fixture
def ocr_instance(mocker):
    mocker.patch('miniocr.ocr.MiniOCR.process_image', new_callable=AsyncMock, return_value="mocked content")
    return MiniOCR(api_key="test-key")

@pytest.mark.asyncio
async def test_process_image(ocr_instance):
    result = await ocr_instance.ocr("tests/test_files/test.jpg")
    assert "content" in result
    assert result["content"] == "mocked content"
    assert "pages" in result
    assert "file_name" in result

@pytest.mark.asyncio
async def test_process_pdf(ocr_instance):
    result = await ocr_instance.ocr("tests/test_files/test.pdf")
    assert "content" in result
    assert "pages" in result
    assert "file_name" in result

@pytest.mark.asyncio
async def test_process_pptx(ocr_instance):
    result = await ocr_instance.ocr("tests/test_files/test.pptx")
    assert "content" in result
    assert "pages" in result
    assert "file_name" in result
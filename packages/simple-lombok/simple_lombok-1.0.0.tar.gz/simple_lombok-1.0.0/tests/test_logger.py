# Created by nikitanovikov at 7/12/25
import io
import sys
from contextlib import redirect_stdout
from simple_lombok.logger import Logger

# Logger test

def class_creation_test():
    logger = Logger()
    assert logger is not None

def test_debug_method():
    # Capture stdout to verify output
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.debug("Test debug message")
    output = f.getvalue().strip()
    assert "[DEBUG]:" in output
    assert "Test debug message" in output

def test_info_method():
    # Capture stdout to verify output
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.info("Test info message")
    output = f.getvalue().strip()
    assert "[INFO]:" in output
    assert "Test info message" in output

def test_error_method():
    # Capture stdout to verify output
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.error("Test error message")
    output = f.getvalue().strip()
    assert "[ERROR]:" in output
    assert "Test error message" in output

def test_warn_method():
    # Capture stdout to verify output
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.warn("Test warning message")
    output = f.getvalue().strip()
    assert "[WARN]:" in output
    assert "Test warning message" in output

def test_success_method():
    # Capture stdout to verify output
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.success("Test success message")
    output = f.getvalue().strip()
    assert "[SUCCESS]:" in output
    assert "Test success message" in output

def test_with_different_input_types():
    # Test with integer
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.debug(123)
    output = f.getvalue().strip()
    assert "[DEBUG]:" in output
    assert "123" in output

    # Test with float
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.info(45.67)
    output = f.getvalue().strip()
    assert "[INFO]:" in output
    assert "45.67" in output

    # Test with list
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.error([1, 2, 3])
    output = f.getvalue().strip()
    assert "[ERROR]:" in output
    assert "[1, 2, 3]" in output

    # Test with dictionary
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.warn({"key": "value"})
    output = f.getvalue().strip()
    assert "[WARN]:" in output
    assert "{'key': 'value'}" in output

    # Test with None
    f = io.StringIO()
    with redirect_stdout(f):
        Logger.success(None)
    output = f.getvalue().strip()
    assert "[SUCCESS]:" in output
    assert "None" in output

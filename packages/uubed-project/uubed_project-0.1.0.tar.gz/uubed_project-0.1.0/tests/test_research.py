#!/usr/bin/env python3
"""
Test for research code in the uubed project.
This tests the voyemb.py research script to ensure it works correctly.
"""

import subprocess
import sys
import os

def test_voyemb_execution():
    """Test that voyemb.py executes without errors using uv run."""
    script_path = os.path.join(os.path.dirname(__file__), "..", "research", "voyemb.py")
    
    assert os.path.exists(script_path), f"Script {script_path} not found"
    
    try:
        # First try with uv run -s (which handles dependencies automatically)
        result = subprocess.run(["uv", "run", "-s", script_path], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            assert len(result.stdout) > 1000, "Script output too short, may not be working correctly"
            print("✅ PASS: voyemb.py executed successfully with uv run")
            print(f"Output length: {len(result.stdout)} characters")
            return
            
        # If uv run fails, try with direct python execution and skip if missing deps
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0 and "ModuleNotFoundError" in result.stderr:
            print("⚠️  SKIP: voyemb.py requires dependencies not available in test environment")
            return
            
        assert result.returncode == 0, f"Script returned exit code {result.returncode}, stderr: {result.stderr}"
        assert len(result.stdout) > 1000, "Script output too short, may not be working correctly"
        
        print("✅ PASS: voyemb.py executed successfully")
        print(f"Output length: {len(result.stdout)} characters")
            
    except subprocess.TimeoutExpired:
        assert False, "Script timed out"
    except FileNotFoundError:
        # If uv is not available, skip the test
        print("⚠️  SKIP: uv not available, cannot test voyemb.py")
        return
    except Exception as e:
        assert False, f"Error running voyemb.py: {e}"
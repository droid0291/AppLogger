import re

class LogBasedStepsGenerator:
    """Generate reproduction steps by analyzing standard Android system logs."""
    
    def __init__(self, gemini_client):
        self.gemini = gemini_client
    
    def extract_steps_from_logs(self, log_content):
        """
        Analyze Android system logs and infer user interaction steps using AI.
        Works with standard Android logs (Activity lifecycle, system events, crashes).
        """
        return self.infer_steps_with_ai(log_content)
    
    def infer_steps_with_ai(self, log_content):
        """Use Gemini to infer reproduction steps from Android system logs."""
        
        # Truncate logs to avoid token limits, but keep crash context
        lines = log_content.split('\n')
        
        # Find crash/error location
        crash_idx = -1
        for i, line in enumerate(lines):
            if 'FATAL' in line or 'AndroidRuntime' in line:
                crash_idx = i
                break
        
        # If crash found, focus on logs around it
        if crash_idx >= 0:
            start = max(0, crash_idx - 100)
            relevant_logs = '\n'.join(lines[start:crash_idx + 50])
        else:
            # No crash, use last 150 lines
            relevant_logs = '\n'.join(lines[-150:])
        
        prompt = f"""You are analyzing Android system logs to generate bug reproduction steps.

IMPORTANT: The logs are standard Android system logs. You need to infer user actions from:
- Activity lifecycle (onCreate, onResume, onPause)
- System events
- Exception stack traces
- App package name and activities

Analyze these logs and generate:
1. Clear, numbered steps that a QA engineer could follow to reproduce the issue
2. Focus on user-visible actions (e.g., "Open app", "Click button", "Enter text")
3. Be specific about which screen/activity was involved
4. Note what crashed and where

Android Logs:
{relevant_logs}

Generate ONLY the numbered reproduction steps, nothing else."""
        
        try:
            # Use the gemini client's analyze_text method
            if hasattr(self.gemini, 'analyze_text'):
                return self.gemini.analyze_text(prompt)
            else:
                return "Gemini client not properly initialized"
        except Exception as e:
            return f"Could not generate steps: {e}"

class UnifiedBugAnalyzer:
    """Analyzes both video and logs together with Gemini for comprehensive bug reports."""
    
    def __init__(self, gemini_client):
        self.gemini = gemini_client
    
    def analyze_bug(self, video_path=None, log_content=None, device_info=None):
        """
        Send both video and logs to Gemini in a single prompt for unified analysis.
        
        Args:
            video_path: Path to recorded video (.mp4)
            log_content: Android logcat content (string)
            device_info: Device information dict
        
        Returns:
            Dict with 'steps', 'crash_analysis', and 'severity'
        """
        if not video_path and not log_content:
            return {
                'steps': 'No video or logs provided',
                'crash_analysis': 'Unable to analyze',
                'severity': 'Unknown'
            }
        
        # Create unified prompt
        prompt = self._create_unified_prompt(log_content, device_info)
        
        # Analyze with video if available
        if video_path and hasattr(self.gemini, 'analyze_video'):
            print("Attempting video + log analysis...")
            try:
                result = self.gemini.analyze_video(video_path, prompt)
                if result:
                    return self._parse_result(result)
                else:
                    print("⚠️ Video analysis unavailable - using log-only analysis")
            except Exception as e:
                print(f"Video analysis failed: {e}")        
        # Log-only analysis if no video
        if log_content:
            return self._analyze_logs_only(log_content, device_info)
        
        return {
            'steps': 'Analysis failed',
            'crash_analysis': 'No data available',
            'severity': 'Unknown'
        }
    
    def _create_unified_prompt(self, log_content, device_info):
        """Create a comprehensive prompt that analyzes both video and logs."""
        device_str = ""
        if device_info:
            device_str = f"""
Device Information:
- Model: {device_info.get('model', 'Unknown')}
- Android Version: {device_info.get('android_version', 'Unknown')}
- Build: {device_info.get('build', 'Unknown')}
"""
        
        logs_str = ""
        if log_content:
            # Truncate logs to avoid token limits
            logs_preview = log_content[-3000:] if len(log_content) > 3000 else log_content
            logs_str = f"""
Android System Logs (last 3000 chars):
```
{logs_preview}
```
"""
        
        prompt = f"""You are analyzing a mobile app bug for a QA engineer. You have access to:
1. A screen recording video showing the user's actions
2. Android system logs (logcat) showing app crashes and errors

{device_str}
{logs_str}

Please provide a comprehensive bug analysis with:

## REPRODUCTION STEPS
Generate clear, numbered steps that show exactly what the user did. Base this on:
- Visual actions from the video (what buttons/fields they interacted with)
- Activity lifecycle from logs (screen transitions, app states)

## CRASH ANALYSIS
Analyze the logs to identify:
- Root cause of the crash/error
- Exact line/method where it failed
- Exception type and message
- Suggested fix for developers

## SEVERITY
Rate the severity: Critical/High/Medium/Low

Format your response EXACTLY like this:
REPRODUCTION STEPS:
1. [First step]
2. [Second step]
...

CRASH ANALYSIS:
[Your analysis]

SEVERITY: [Level]
"""
        return prompt
    
    def _analyze_logs_only(self, log_content, device_info):
        """Fallback to log-only analysis if video unavailable."""
        prompt = f"""Analyze these Android logs to generate bug reproduction steps and crash analysis.

Device: {device_info.get('model', 'Unknown')} - Android {device_info.get('android_version', 'Unknown')}

Logs:
{log_content[-3000:]}

Provide:
1. Reproduction steps inferred from system events
2. Crash analysis with root cause
3. Severity level

Use the same format as before."""
        
        try:
            if hasattr(self.gemini, 'analyze_text'):
                result = self.gemini.analyze_text(prompt)
                return self._parse_result(result)
        except Exception as e:
            print(f"Log analysis error: {e}")
        
        return {
            'steps': 'Unable to generate steps',
            'crash_analysis': 'Analysis failed',
            'severity': 'Unknown'
        }
    
    def _parse_result(self, result):
        """Parse Gemini's response into structured data."""
        if not result:
            return {
                'steps': 'No analysis generated',
                'crash_analysis': 'Empty response',
                'severity': 'Unknown'
            }
        
        # Extract sections
        steps = self._extract_section(result, 'REPRODUCTION STEPS:', 'CRASH ANALYSIS:')
        crash = self._extract_section(result, 'CRASH ANALYSIS:', 'SEVERITY:')
        severity = self._extract_section(result, 'SEVERITY:', None)
        
        return {
            'steps': steps or 'See full analysis',
            'crash_analysis': crash or result,
            'severity': severity.strip() if severity else 'Medium'
        }
    
    def _extract_section(self, text, start_marker, end_marker):
        """Extract text between two markers."""
        try:
            start_idx = text.find(start_marker)
            if start_idx == -1:
                return None
            
            start_idx += len(start_marker)
            
            if end_marker:
                end_idx = text.find(end_marker, start_idx)
                if end_idx == -1:
                    return text[start_idx:].strip()
                return text[start_idx:end_idx].strip()
            else:
                return text[start_idx:].strip()
        except:
            return None

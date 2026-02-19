import os

class StepsGenerator:
    def __init__(self, gemini_client, video_recorder):
        self.gemini = gemini_client
        self.video_recorder = video_recorder

    def generate_steps_from_video(self, video_path, crash_description=None):
        """
        Generate reproduction steps by analyzing video frames with Gemini.
        
        Args:
            video_path: Path to the recorded video
            crash_description: Optional context about the crash
        
        Returns:
            Formatted steps as a string
        """
        # Extract frames from video
        frames_dir = self.video_recorder.extract_frames(video_path, interval=2)
        
        if not frames_dir:
            return "Unable to extract frames from video. Please install FFmpeg."
        
        # Get list of frame images
        frames = sorted([
            os.path.join(frames_dir, f) 
            for f in os.listdir(frames_dir) 
            if f.endswith('.png')
        ])
        
        if not frames:
            return "No frames extracted from video."
        
        # Analyze key frames with Gemini
        # Take first, middle, few before crash for context
        key_frames = [
            frames[0],  # Start
            frames[len(frames) // 2],  # Middle
            frames[-1]  # End (crash point)
        ]
        
        steps = []
        for i, frame_path in enumerate(key_frames):
            prompt = f"""Analyze this mobile app screenshot (frame {i+1}/{len(key_frames)}).
Describe what the user is doing in this screen:
- What screen/page is shown?
- What UI elements are visible?
- What action was likely just performed to reach this state?

Be concise and specific."""
            
            try:
                analysis = self.gemini.analyze_image(frame_path, prompt)
                steps.append(f"Step {i+1}: {analysis}")
            except Exception as e:
                steps.append(f"Step {i+1}: [Frame analysis failed: {e}]")
        
        # Compile final steps
        final_steps = "\\n".join(steps)
        
        if crash_description:
            final_steps += f"\\n\\nCrash occurred: {crash_description}"
        
        return self.format_steps(final_steps)

    def format_steps(self, raw_steps):
        """Clean up and format steps for JIRA."""
        # Use Gemini to refine the steps
        prompt = f"""The following are rough steps extracted from video analysis:

{raw_steps}

Please format these into clear, numbered reproduction steps suitable for a bug report.
Make them concise and actionable. Output only the steps, nothing else."""
        
        try:
            import google.generativeai as genai
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback to raw steps
            return raw_steps

    def generate_steps_from_manual_input(self, screenshot_paths, descriptions):
        """
        Alternative: Generate steps from manually captured screenshots.
        
        Args:
            screenshot_paths: List of screenshot file paths
            descriptions: List of user descriptions for each screenshot
        
        Returns:
            Formatted reproduction steps
        """
        steps = []
        for i, (screenshot, desc) in enumerate(zip(screenshot_paths, descriptions)):
            # Enhance description with Gemini analysis
            prompt = f"""User description: {desc}

Analyze this screenshot and enhance the description with specific UI element details.
Keep it concise."""
            
            try:
                analysis = self.gemini.analyze_image(screenshot, prompt)
                steps.append(f"{i+1}. {analysis}")
            except Exception as e:
                steps.append(f"{i+1}. {desc}")
        
        return "\\n".join(steps)

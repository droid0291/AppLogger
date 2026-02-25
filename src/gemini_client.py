import google.generativeai as genai
import PIL.Image
import traceback

class GeminiClient:
    def __init__(self, api_key):
        self.api_key = api_key
        if not api_key:
            raise ValueError("API Key is required for Gemini Client")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('models/gemini-2.0-flash')

    def analyze_image(self, image_path, prompt):
        """Sends an image to Gemini for analysis."""
        try:
            img = PIL.Image.open(image_path)
            response = self.model.generate_content([prompt, img])
            return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            traceback.print_exc()
            return None

    def analyze_text(self, prompt):
        """Sends text to Gemini for analysis."""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini Error: {e}")
            traceback.print_exc()
            return None

    def analyze_video(self, video_path, prompt):
        """Sends a video file to Gemini for analysis."""
        try:
            # Upload video file to Gemini
            import google.generativeai as genai
            import os
            
            # Check file exists and size
            if not os.path.exists(video_path):
                return None
            
            file_size = os.path.getsize(video_path)
            print(f"Uploading video: {video_path} ({file_size / 1024:.1f} KB)")
            
            # Skip if file is too small (likely corrupted / no moov atom)
            if file_size < 1000:
                print(f"Video file too small, skipping upload")
                return None

            # Transcode to H.264 MP4 before uploading.
            # xcrun simctl recordVideo may produce a QuickTime file (no moov
            # atom for SIGTERM-killed recordings).  Gemini rejects everything
            # that is not a proper H.264 MP4.
            import shutil, subprocess as _sp
            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg:
                transcoded = video_path.replace(".mp4", "_h264.mp4")
                r = _sp.run(
                    [ffmpeg, "-y", "-i", video_path,
                     "-vcodec", "libx264", "-acodec", "aac",
                     "-crf", "23", "-preset", "fast",
                     "-movflags", "+faststart",
                     transcoded],
                    capture_output=True, text=True)
                if r.returncode == 0:
                    print(f"Transcoded to H.264: {transcoded}")
                    video_path = transcoded
                else:
                    print(f"ffmpeg transcode failed (using original): {r.stderr[-200:]}")
            else:
                print("ffmpeg not found — uploading original (may fail if not H.264)")

            video_file = genai.upload_file(path=video_path)
            
            print(f"Waiting for video processing...")
            # Wait for the file to be processed
            import time
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                error_detail = getattr(video_file, 'error', None)
                print(f"Video processing failed on Gemini side")
                print(f"  File: {video_file.name}")
                print(f"  State: {video_file.state.name}")
                if error_detail:
                    print(f"  Error: {error_detail}")
                else:
                    print(f"  (No additional error detail from Gemini API)")
                return None
            
            print(f"Video ready, analyzing...")
            # Generate content with video
            response = self.model.generate_content([video_file, prompt])
            return response.text
        except Exception as e:
            print(f"Gemini Video Error: {e}")
            traceback.print_exc()
            return None

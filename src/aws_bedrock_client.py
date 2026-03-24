import os
import shutil
import traceback
import subprocess as _sp
import boto3

class AwsBedrockClient:
    def __init__(self, region_name="us-east-1", profile_name=None):
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()
            
        self.client = session.client("bedrock-runtime", region_name=region_name)
        self.model_id = "amazon.nova-pro-v1:0"

    def analyze_image(self, image_path, prompt):
        """Sends an image to Bedrock Nova Pro for analysis."""
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            
            ext = image_path.split('.')[-1].lower()
            if ext == 'jpg': 
                ext = 'jpeg'
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {
                            "image": {
                                "format": ext,
                                "source": {"bytes": image_bytes}
                            }
                        }
                    ]
                }
            ]
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages
            )
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Bedrock Image Error: {e}")
            traceback.print_exc()
            return None

    def analyze_text(self, prompt):
        """Sends text to Bedrock Nova Pro for analysis."""
        try:
            messages = [
                {
                    "role": "user",
                    "content": [{"text": prompt}]
                }
            ]
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages
            )
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Bedrock Text Error: {e}")
            traceback.print_exc()
            return None

    def analyze_video(self, video_path, prompt):
        """Sends a video file to Bedrock Nova Pro for analysis."""
        try:
            if not os.path.exists(video_path):
                return None
                
            file_size = os.path.getsize(video_path)
            print(f"Analyzing video via Bedrock: {video_path} ({file_size / 1024:.1f} KB)")
            
            if file_size < 1000:
                print(f"Video file too small, skipping")
                return None

            # Transcode to H.264 MP4 if needed (mostly for iOS recordings)
            ffmpeg  = shutil.which("ffmpeg")
            ffprobe = shutil.which("ffprobe")
            needs_transcode = False
            
            if ffprobe:
                probe = _sp.run(
                    [ffprobe, "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=codec_name",
                     "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                    capture_output=True, text=True)
                codec = probe.stdout.strip().lower()
                print(f"Video codec detected: '{codec}'")
                needs_transcode = codec not in ("h264", "avc")
            else:
                needs_transcode = "ios" in video_path.lower()

            if needs_transcode:
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
                    print("ffmpeg not found, skipping transcode")

            ext = video_path.split('.')[-1].lower()
            # Nova Pro Converse API supports specific formats
            supported_formats = ["mp4", "mov", "mkv", "webm", "flv", "mpeg", "mpg", "wmv", "three_gp"]
            if ext not in supported_formats:
                ext = "mp4" # fallback

            with open(video_path, "rb") as f:
                video_bytes = f.read()

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"text": prompt},
                        {
                            "video": {
                                "format": ext,
                                "source": {"bytes": video_bytes}
                            }
                        }
                    ]
                }
            ]
            
            print("Sending request to Amazon Bedrock Nova Pro...")
            response = self.client.converse(
                modelId=self.model_id,
                messages=messages
            )
            return response['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Bedrock Video Error: {e}")
            traceback.print_exc()
            return None

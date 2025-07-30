from google.genai import types
import pathlib

class Vision:
    def __init__(self, mindbot_instance):
        self.client = mindbot_instance.client

    def analyze_image(self, image_path, prompt, model="mindvision-flash"):
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        contents = [
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
            prompt
        ]
        
        response = self.client.generate_content(
            model='gemini-2.5-flash',
            contents=contents
        )
        return response.text

    def analyze_video(self, video_path, prompt, model="mindvision-flash"):
        myfile = self.client.files.upload(path=video_path)
        
        response = self.client.generate_content(
            model="gemini-2.5-flash", 
            contents=[myfile, prompt]
        )
        return response.text

    def analyze_youtube_video(self, youtube_url, prompt, model="mindtube-1.0"):
        contents = types.Content(
            parts=[
                types.Part(
                    file_data=types.FileData(file_uri=youtube_url)
                ),
                types.Part(text=prompt)
            ]
        )
        
        response = self.client.generate_content(
            model='models/gemini-2.5-flash',
            contents=contents
        )
        return response.text

    def analyze_pdf(self, file_path, prompt, model="mindvision-flash"):
        filepath = pathlib.Path(file_path)
        
        contents = [
            types.Part.from_bytes(
                data=filepath.read_bytes(),
                mime_type='application/pdf',
            ),
            prompt
        ]
        
        response = self.client.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        return response.text

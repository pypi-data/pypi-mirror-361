class Audio:
    def __init__(self, mindbot_instance):
        self.client = mindbot_instance.client

    def analyze_audio(self, audio_path, prompt, model="mindaudio-pro"):
        myfile = self.client.files.upload(path=audio_path)
        
        response = self.client.generate_content(
            model="gemini-2.5-flash", 
            contents=[prompt, myfile]
        )
        return response.text

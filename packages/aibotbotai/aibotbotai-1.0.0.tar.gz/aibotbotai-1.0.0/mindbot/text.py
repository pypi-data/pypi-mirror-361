from google.genai import types

class TextGeneration:
    def __init__(self, mindbot_instance):
        self.client = mindbot_instance.client

    def generate_content(self, contents, model="mindbot-1.8-ultra", think=False):
        model_name = "gemini-2.5-flash"
        thinking_budget = 0
        if think or (isinstance(contents, str) and len(contents.split()) > 50):
            model = "mindthink-a3"
        
        if model == "mindthink-a3":
            model_name = "gemini-2.5-flash"
            thinking_budget = 7000
        
        config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget)
        )
        
        response = self.client.generate_content(
            model=model_name,
            contents=contents,
            generation_config=config,
        )
        return response.text

    def analyze_txt(self, file_path, prompt, model="mindbot-1.8-ultra"):
        with open(file_path, "r", encoding="utf-8") as f:
            text_data = f.read()
        
        full_prompt = (
            "Here is a document:\n\n"
            f"{text_data[:1000]}...\n\n"
            f"{prompt}"
        )
        return self.generate_content(full_prompt, model=model)

    def analyze_csv(self, file_path, question, model="mindbot-1.8-ultra"):
        import pandas as pd
        df = pd.read_csv(file_path)
        table_str = df.to_string(index=False)
        
        prompt = f"Here’s the CSV data:\n{table_str}\n\nQuestion: {question}"
        return self.generate_content(prompt, model=model)

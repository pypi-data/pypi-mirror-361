from google.genai.types import Tool, GenerateContentConfig

class Search:
    def __init__(self, mindbot_instance):
        self.client = mindbot_instance.client

    def browse(self, contents, model="mindsearch-2.5", think=False):
        model_id = "gemini-2.5-flash"
        if model == "deepsearch-1.0":
            think = True

        tools = [Tool(google_search=types.GoogleSearch())]
        
        config = GenerateContentConfig(
            tools=tools,
        )

        response = self.client.generate_content(
            model=model_id,
            contents=contents,
            generation_config=config,
        )
        
        return response.text

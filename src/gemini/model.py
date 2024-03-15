from google import generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class model:
    temp_0_config = genai.GenerationConfig( **{  
        # "candidate_count": int | None = None
        # "stop_sequences": Iterable[str] | None = None
        # "max_output_tokens": int | None = None
        "temperature": 0
        # "top_p": float | None = None
        # "top_k": int | None = None
        })

    genai.configure()

    genai_model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, content,**kwargs):
        if len(kwargs) == 0:
            response = self.genai_model.generate_content(content,generation_config=self.temp_0_config)
        else:
            config = genai.GenerationConfig(**kwargs)
            response = self.genai_model.generate_content(content,generation_config=config)

        return response.text

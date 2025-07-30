
# import requests
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class OllamaLLMWrapper(LLMBase):
#     def __init__(self, model_name: str, host: str, security_token: str = None):
#         self.model_name = model_name
#         self.host = host
#         self.security_token = security_token  # kept for future if needed, but unused
#         self.api_url = f"{self.host}/api/generate"
#         print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")
#
#     def get_data(self, prompt: str) -> str:
#         try:
#             print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             payload = {
#                 "model": self.model_name,
#                 "prompt": formatted_prompt,
#                 "stream": False
#             }
#
#             # ✅ No API key required now — send freely to any host
#             response = requests.post(self.api_url, json=payload)
#             response.raise_for_status()
#             return "[Ollama] " + response.json().get("response", "[No response]")
#         except Exception as e:
#             return f"[Ollama ERROR]: {str(e)}"

# import requests
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class OllamaLLMWrapper(LLMBase):
#     def __init__(self, model_name: str, host: str):
#         self.model_name = model_name
#         self.host = host
#         self.api_url = f"{self.host}/api/generate"
#         print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")
#
#     def get_data(self, prompt: str) -> str:
#         try:
#             print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             payload = {
#                 "model": self.model_name,
#                 "prompt": formatted_prompt,
#                 "stream": False
#             }
#
#             response = requests.post(self.api_url, json=payload)
#             response.raise_for_status()
#             return "[Ollama] " + response.json().get("response", "[No response]")
#         except Exception as e:
#             return f"[Ollama ERROR]: {str(e)}"


from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class OllamaLLMWrapper(LLMBase):
    def __init__(self, model_name: str, host: str):
        self.model_name = model_name
        self.host = host  # Used for base_url
        #  Initialize LangChain OllamaLLM
        self.llm = OllamaLLM(model=self.model_name, base_url=self.host)
        print(f"🔹 [OllamaLLMWrapper] Initialized with model: {self.model_name} at {self.host}")

    def get_data(self, prompt: str) -> str:
        try:
            print(f"🔹 [OllamaLLMWrapper] Prompt:\n{prompt}")
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)

            #  Use LangChain OllamaLLM invoke method
            response = self.llm.invoke(formatted_prompt)
            return "[Ollama] " + response
        except Exception as e:
            return f"[Ollama ERROR]: {str(e)}"

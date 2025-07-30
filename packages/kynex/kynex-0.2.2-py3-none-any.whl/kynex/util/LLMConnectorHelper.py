# import os
# import configparser
# from kynex.llm.gemini.gemini import GeminiLLM
# from kynex.llm.groq.groq import GroqLLM
# from kynex.llm.ollama.ollama import OllamaLLMWrapper as OllamaLLM
#
# class LLMConnector:
#     def __init__(self, api_key: str, model_name: str, llm_type: str = "gemini", host: str = None):
#         self.api_key = api_key
#         self.model_name = model_name
#         self.llm_type = llm_type.lower() if llm_type else "gemini"
#         self.host = host or self.load_default_host()  # Load default Ollama host if not given
#
#     def load_default_host(self):
#         """Loads default Ollama host if not explicitly provided (optional config fallback)."""
#         config = configparser.ConfigParser()
#         config.read(os.path.abspath("resources/kynex.properties"))
#         return config.get("DEFAULT", "ollama_host", fallback="http://localhost:11434")
#
#     def get_llm_instance(self):
#         print(f"🔍 Selected LLM: {self.llm_type} | Model: {self.model_name}")
#
#         if self.llm_type == "gemini":
#             return GeminiLLM(api_key=self.api_key, model_name=self.model_name)
#         elif self.llm_type == "groq":
#             return GroqLLM(api_key=self.api_key, model_name=self.model_name)
#         elif self.llm_type == "ollama":
#             return OllamaLLM(
#                 model_name=self.model_name,
#                 host=self.host,
#                 security_token=self.api_key  # Secure Token Required
#             )
#         else:
#             raise ValueError(f"Unsupported LLM type: {self.llm_type}")
#
#     def getLLMData(self, prompt: str) -> str:
#         llm = self.get_llm_instance()
#         return llm.get_data(prompt)

#
# from kynex.llm.gemini.gemini import GeminiLLM
# from kynex.llm.groq.groq import GroqLLM
# from kynex.llm.ollama.ollama import OllamaLLMWrapper as OllamaLLM
#
# class LLMConnector:
#     def __init__(self, model_name: str, llm_type: str, host: str = None):
#         self.model_name = model_name
#         self.llm_type = llm_type.lower()
#         self.host = host  # Host required for Ollama
#
#     def get_llm_instance(self):
#         print(f"🔍 Selected LLM: {self.llm_type} | Model: {self.model_name}")
#
#         if self.llm_type == "gemini":
#             return GeminiLLM(model_name=self.model_name)
#         elif self.llm_type == "groq":
#             return GroqLLM(model_name=self.model_name)
#         elif self.llm_type == "ollama":
#             if not self.host:
#                 raise ValueError("Host is required for Ollama LLM.")
#             return OllamaLLM(model_name=self.model_name, host=self.host)
#         else:
#             raise ValueError(f"Unsupported LLM type: {self.llm_type}")
#
#     def getLLMData(self, prompt: str) -> str:
#         llm = self.get_llm_instance()
#         return llm.get_data(prompt)


from kynex.llm.gemini.GeminiLLMWrapper import GeminiLLMWrapper
from kynex.llm.groq.GroqLLMWrapper import GroqLLMWrapper
from kynex.llm.ollama.OllamaLLMWrapper import OllamaLLMWrapper

class LLMConnectorHelper:
    def __init__(self, model_name: str, llm_type: str, api_key: str = None, host: str = None):
        self.model_name = model_name
        self.llm_type = llm_type.lower()
        self.api_key = api_key
        self.host = host

    def get_llm_instance(self):
        print(f"🔍 Selected LLM: {self.llm_type} | Model: {self.model_name}")

        if self.llm_type == "gemini":
            return GeminiLLMWrapper(api_key=self.api_key, model_name=self.model_name)
        elif self.llm_type == "groq":
            return GroqLLMWrapper(api_key=self.api_key, model_name=self.model_name)
        elif self.llm_type == "ollama":
            if not self.host:
                raise ValueError("Host is required for Ollama LLM.")
            return OllamaLLMWrapper(model_name=self.model_name, host=self.host)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

    def getLLMData(self, prompt: str) -> str:
        llm = self.get_llm_instance()
        return llm.get_data(prompt)

#
# from kynex.llm_connector import LLMConnector
#
#
# class Kynexa:
#     LLM_GEMINI = "gemini"
#     LLM_GROQ = "groq"
#     LLM_OLLAMA = "ollama"
#     #@staticmethod
#     # def get_llm_response(prompt: str, model_name: str, api_key: str, llm_type: str = None) -> str:
#     #
#     #     if llm_type is None:
#     #         llm_type = Kynexa.LLM_GEMINI
#     #     connector = LLMConnector(api_key=api_key, model_name=model_name, llm_type=llm_type)
#     #     return connector.getLLMData(prompt)
#     @staticmethod
#     def get_llm_response(prompt: str, model_name: str, api_key: str, llm_type: str = None, host: str = None) -> str:
#         if llm_type is None:
#             llm_type = Kynexa.LLM_GEMINI
#         connector = LLMConnector(api_key=api_key, model_name=model_name, llm_type=llm_type, host=host)
#         return connector.getLLMData(prompt)


from kynex.util.LLMConnectorHelper import LLMConnectorHelper

class LLMConnector:
    LLM_GEMINI = "gemini"
    LLM_GROQ = "groq"
    LLM_OLLAMA = "ollama"

    @staticmethod
    def get_llm_response(prompt: str, model_name: str, llm_type: str = None, api_key: str = None,
                         host: str = None) -> str:
        if llm_type is None:
            llm_type = LLMConnector.LLM_OLLAMA  # Default to ollama if not given
        connector = LLMConnectorHelper(model_name=model_name, llm_type=llm_type, api_key=api_key, host=host)
        return connector.getLLMData(prompt)

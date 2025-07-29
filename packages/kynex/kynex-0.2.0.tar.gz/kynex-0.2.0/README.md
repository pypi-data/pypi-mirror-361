# 🔷 Kynex

**Kynex** is a modular, pluggable Python framework that simplifies integrating multiple LLM providers such as **Google Gemini**, **Groq**, and **Ollama** through a unified, flexible interface.

Whether you're building AI workflows, chatbots, or prompt-based tools, Kynex allows seamless integration with different LLMs — all through a single API.

---

## 🚀 Features

- **Multi-LLM Support**: Easily switch between Gemini, Groq, and Ollama with a single interface.
- **Dynamic Inputs**: Accept LLM type, model name, API keys, and host dynamically at runtime.
- **LangChain Prompt Templates**: Built-in LangChain `PromptTemplate` for clean prompt formatting.
- **Pluggable Architecture**: Easily extend to new LLMs in the future.
- **Ready for Local & Remote Deployments**: Supports local Ollama and remote LLM services.

---

## 📦 Installation

```bash
pip install kynex

Example Usage:

Create it:

Create a Python file and add the following:

 from kynex.LLMTools import LLMConnector

Google Gemini Example:


if __name__ == "__main__":
    # Simulated input from frontend
    request = {
        "prompt": "what is fast api",
        "model_name": "gemini-1.5-flash",
        "api_key": "your_api_key",
        "llm_type": "LLMConnector.LLM_GEMINI"
    }

    response = LLMConnector.get_llm_response(
        prompt=request["prompt"],
        model_name=request["model_name"],
        api_key=request["api_key"],
        llm_type=request.get("llm_type")  # Can be None — will default to gemini
    )

    print("\n🔹 Response:\n")
    print(response)



Groq Example:

from kynex.LLMTools import LLMConnector


 if __name__ == "__main__":
     request = {
         "prompt": "Give 3 project use cases for a full-stack web developer.",
         "model_name": "meta-llama/llama-4-scout-17b-16e-instruct",  # ✅ Groq model
         "api_key": "your_api_key",
         "llm_type": "groq"
     }

     response =LLMConnector.get_llm_response(
         prompt=request["prompt"],
         model_name=request["model_name"],
         api_key=request["api_key"],
         llm_type=request.get("llm_type")
     )

     print("\n🔹 Groq LLaMA-4 Response:\n")
     print(response)

Ollama Example (Local or Remote):

from kynex.LLMTools import LLMConnector

response = LLMConnector.get_llm_response(
    prompt="your_prompt",
    model_name="llama3",
    llm_type=LLMConnector.LLM_OLLAMA,
    host="your_host"  # or remote URL if exposed via proxy
)

print(response)



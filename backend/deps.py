def call_llm(prompt: str) -> str:
    """
    Placeholder LLM invocation.

    Replace this with your actual LLM client, for example:
      - OpenAI: client.chat.completions.create(...)
      - Local model: llama.cpp / vLLM call
      - Your internal API

    For now, we raise NotImplementedError so the FastAPI app returns 501.
    """
    raise NotImplementedError("call_llm is not implemented. Plug in your LLM client here.")

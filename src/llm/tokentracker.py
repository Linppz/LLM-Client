import tiktoken
from typing import List


class TokenTracker:
    def __init__(self, model: str):
        self.text: List[str] = []
        self.model = model

    def add(self, word: str) -> None:
        self.text += [word]

    def get_usage(
        self,
    ) -> int:
        temp = "".join(self.text)

        try:
            encoding = tiktoken.encoding_for_model(self.model)
        except Exception:
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens = encoding.encode(temp)
        return len(tokens)

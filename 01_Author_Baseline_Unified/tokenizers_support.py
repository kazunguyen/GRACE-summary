"""Only for mock tests; never use as the model tokenizer in real runs."""
class MockTokenizer:
    chat_template = "mock"
    def encode(self, text, add_special_tokens=False): return list(text.encode('utf-8'))
    def decode(self, ids, skip_special_tokens=True): return bytes(ids).decode('utf-8', errors='ignore')
    def apply_chat_template(self, messages, tokenize=True, add_generation_prompt=True):
        return self.encode(messages[0]['content']) + [0, 0, 0]

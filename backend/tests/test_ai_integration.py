

class DummyAI:
    def generate(self, prompt: str) -> str:
        return "generated: " + prompt


def test_ai_generate():
    dummy = DummyAI()
    res = dummy.generate('hello')
    assert res == 'generated: hello'

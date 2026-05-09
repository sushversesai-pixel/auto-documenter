# test_code.py

class Greeter:
    def __init__(self, name: str):
        self.name = name

    def greet(self, loud: bool = False) -> str:
        message = f"Hello, {self.name}"
        if loud:
            return message.upper()
        return message

def add_numbers(a: int, b: int) -> int:
    return a + b
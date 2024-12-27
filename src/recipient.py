class Recipient:
    email: str
    name: str

    def __init__(self, email: str, name: str) -> None:
        self.email = email
        self.name = name

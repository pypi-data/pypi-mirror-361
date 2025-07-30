class Message:
    name: str
    last_name: str

    def send_greetings(self):
        print(f"Hello!")

    def get_info(self):
        print(f"Please tell me your name and surname.")

    def thanks_message(self, name: str, last_name: str):
        self.name = name
        self.last_name = last_name
        print(f"Thank you {name} {last_name}!")

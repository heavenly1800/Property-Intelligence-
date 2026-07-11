import re


class IntakeService:

    @staticmethod
    def detect_input_type(value: str):

        value = value.strip()

        if value.startswith("http://") or value.startswith("https://"):
            return "url"

        if re.fullmatch(r"[0-9\-]+", value):
            return "apn"

        return "address"
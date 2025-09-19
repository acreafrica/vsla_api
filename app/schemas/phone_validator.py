# import phonenumbers
# from pydantic import BaseModel

# class PhoneNumber(str):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v, info=None):
#         # v = the input value
#         try:
#             parsed = phonenumbers.parse(v, None)
#             if not phonenumbers.is_valid_number(parsed):
#                 raise ValueError("Invalid phone number")
#             return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
#         except Exception:
#             raise ValueError("Invalid phone number format. Use international format e.g. +2547XXXXXXX")
import phonenumbers
from pydantic import BaseModel

class PhoneNumber(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, info=None):
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            # normalize to E.164
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except Exception:
            raise ValueError("Invalid phone number format. Use international format e.g. +2609XXXXXXX")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # tells FastAPI/OpenAPI that this is a string
        return {
            "type": "string",
            "example": "+260912345678",
            "description": "Validated international phone number in E.164 format"
        }

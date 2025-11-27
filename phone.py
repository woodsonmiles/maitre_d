import phonenumbers

def normalize_phone(phone: str, region: str = "US") -> str:
    try:
        parsed = phonenumbers.parse(phone, region)
        if phonenumbers.is_valid_number(parsed):
            # Return in E.164 format (+countrycode + number)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        return ''
    except phonenumbers.NumberParseException:
        return ''


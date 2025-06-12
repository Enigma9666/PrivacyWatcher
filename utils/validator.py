# utils/validator.py

def validate_luhn(card_number):
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    double = False
    for d in reversed(digits):
        if double:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
        double = not double
    return checksum % 10 == 0

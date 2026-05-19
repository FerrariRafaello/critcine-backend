import re


class CPFError(Exception):
    pass


def is_valid_cpf(cpf: str) -> bool:
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11:
        return False
    # sequences like 111.111.111-11 pass length check but are invalid
    if cpf == cpf[0] * 11:
        return False

    def calc_digit(base: str, factor: int) -> str:
        total = 0
        for digit in base:
            total += int(digit) * factor
            factor -= 1
        remainder = (total * 10) % 11
        # remainder 10 is treated as 0 by the CPF spec
        return "0" if remainder == 10 else str(remainder)

    first_digit = calc_digit(cpf[:9], 10)
    if cpf[9] != first_digit:
        return False

    second_digit = calc_digit(cpf[:10], 11)
    if cpf[10] != second_digit:
        return False

    return True


def validate_cpf_or_raise(cpf: str) -> None:
    if not is_valid_cpf(cpf):
        raise ValueError("Invalid CPF")

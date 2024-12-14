from pydantic import EmailStr, BaseModel


class DataValidator:
    CARD_MAPPING: dict[int, str] = {
        3: "American Express",
        4: "Visa",
        5: "Mastercard",
        6: "Discover",
    }

    @classmethod
    def validate_cpf(cls, cpf: str) -> bool:
        if not cpf.isdigit():
            cpf = "".join(filter(str.isdigit, cpf))
        if len(cpf) != 11 or all(c == cpf[0] for c in cpf):
            return False
        return cls._validate_cpf_digit(cpf, 9) and cls._validate_cpf_digit(
            cpf, 10
        )

    @classmethod
    def validate_cnpj(cls, cnpj: str) -> bool:
        if not cnpj.isdigit():
            cnpj = "".join(filter(str.isdigit, cnpj))
        if len(cnpj) != 14 or all(c == cnpj[0] for c in cnpj):
            return False
        return cls._validate_cnpj_digit(cnpj, 12) and cls._validate_cnpj_digit(
            cnpj, 13
        )

    @staticmethod
    def validate_email(email: str) -> bool:
        try:
            __EmailValidator(email=email)
            return True
        except Exception:
            return False

    @classmethod
    def validate_card(cls, card: str) -> str | None:
        card = "".join(card.split(" "))
        if not card.isdigit() or len(card) != 16:
            return None
        tot = 0
        for index, char in enumerate(reversed(card)):
            if index % 2 == 0:
                tot += int(char)
            else:
                tot += sum(int(d) for d in str(int(char) * 2))
        if not tot % 10 == 0:
            return None
        return cls.CARD_MAPPING.get(int(card[0]))

    @staticmethod
    def _validate_cpf_digit(cpf: str, digit: int) -> bool:
        tot = sum(int(cpf[num]) * (digit + 1 - num) for num in range(digit))
        d = 11 - ((tot) % 11)
        if d > 9:
            d = 0
        return int(cpf[digit]) == d

    @staticmethod
    def _validate_cnpj_digit(cnpj: str, digit: int) -> bool:
        tot = 0
        for index, char in enumerate(reversed(cnpj[:digit])):
            tot += int(char) * (2 + index if index <= 7 else index - 6)
        d1 = 11 - (tot % 11)
        if d1 > 9:
            d1 = 0
        return int(cnpj[digit]) == d1


class __EmailValidator(BaseModel):
    email: EmailStr


if __name__ == "__main__":
    cnpj = input("Digite o CNPJ: ")
    if DataValidator.validate_cnpj(cnpj):
        print("CNPJ válido")
    else:
        print("CNPJ inválido")
    cpf = input("Digite o CPF: ")
    if DataValidator.validate_cpf(cpf):
        print("CPF válido")
    else:
        print("CPF inválido")
    cartao = input("Digite o número do cartão de crédito: ")
    if DataValidator.validate_card(cartao):
        print("Cartão de crédito válido")
    else:
        print("Cartão de crédito inválido")
"4539 1488 0343 6467"

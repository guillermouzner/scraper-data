DIVISOR = 11

CPF_WEIGHTS = ((10, 9, 8, 7, 6, 5, 4, 3, 2),
              (11, 10, 9, 8, 7, 6, 5, 4, 3, 2))
CNPJ_WEIGHTS = ((5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
               (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))

def calculate_first_digit(number):
    """ This function calculates the first check digit of a
        cpf or cnpj.

        :param number: cpf (length 9) or cnpf (length 12) 
            string to check the first digit. Only numbers.
        :type number: string
        :returns: string -- the first digit

    """

    sum = 0
    if len(number) == 9:
        weights = CPF_WEIGHTS[0]
    else:
        weights = CNPJ_WEIGHTS[0]

    for i in range(len(number)):
        sum = sum + int(number[i]) * weights[i]
    rest_division = sum % DIVISOR
    if rest_division < 2:
        return '0'
    return str(11 - rest_division)

def calculate_second_digit(number):
    """ This function calculates the second check digit of
        a cpf or cnpj.

        **This function must be called after the above.**

        :param number: cpf (length 10) or cnpj 
            (length 13) number with the first digit. Only numbers.
        :type number: string
        :returns: string -- the second digit

    """

    sum = 0
    if len(number) == 10:
        weights = CPF_WEIGHTS[1]
    else:
        weights = CNPJ_WEIGHTS[1]

    for i in range(len(number)):
        sum = sum + int(number[i]) * weights[i]
    rest_division = sum % DIVISOR
    if rest_division < 2:
        return '0'
    return str(11 - rest_division)

def check_special_characters(func):
    def wrapper(document):
        not_digit = [i for i in clear_punctuation(document) if not i.isdigit()]
        return False if not_digit else func(document)

    return wrapper


def clear_punctuation(document):
    """Remove from document all pontuation signals."""
    return document.translate(str.maketrans({".": None, "-": None, "/": None}))


@check_special_characters
def validate(cnpj_number):
    """This function validates a CNPJ number.

    This function uses calculation package to calculate both digits
    and then validates the number.

    :param cnpj_number: a CNPJ number to be validated.  Only numbers.
    :type cnpj_number: string
    :return: Bool -- True for a valid number, False otherwise.

    """

    _cnpj = clear_punctuation(cnpj_number)

    if len(_cnpj) != 14 or len(set(_cnpj)) == 1:
        return False

    first_part = _cnpj[:12]
    second_part = _cnpj[:13]
    first_digit = _cnpj[12]
    second_digit = _cnpj[13]

    if first_digit == calculate_first_digit(
        first_part
    ) and second_digit == calculate_second_digit(second_part):
        return True

    return False



print(validate('70043054000705')) # True

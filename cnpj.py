import re

def isCpj(cpj):
    cpj = re.sub(r'[^\d]+', '', cpj)

    if len(cpj) != 11 or len(set(cpj)) == 1:
        return False

    def calculate_digit(number):
      sum = 0
      weight = 2
      for i in range(len(number)-1,-1,-1):
          sum += int(number[i]) * weight
          weight += 1

      result = 11 - (sum % 11)

      return "0" if result >= 10 else str(result)

    digit1 = calculate_digit(cpj[:9])
    digit2 = calculate_digit(cpj[:10])

    return cpj[-2:] == digit1 + digit2

def isCnpj(cnpj):
    cnpj = re.sub(r'[^\d]+', '', cnpj)

    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False

    def calculate_digit(number):
      sum = 0
      weight = 2
      for i in range(len(number)-1,-1,-1):
          sum += int(number[i]) * weight
          weight += 1
          if weight > 9:
            weight = 2

      result = 11 - (sum % 11)

      return "0" if result >= 10 else str(result)

    digit1 = calculate_digit(cnpj[:12])
    digit2 = calculate_digit(cnpj[:13])

    return cnpj[-2:] == digit1 + digit2

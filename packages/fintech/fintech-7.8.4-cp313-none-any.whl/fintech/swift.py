
###########################################################################
#
# LICENSE AGREEMENT
#
# Copyright (c) 2014-2024 joonis new media, Thimo Kraemer
#
# 1. Recitals
#
# joonis new media, Inh. Thimo Kraemer ("Licensor"), provides you
# ("Licensee") the program "PyFinTech" and associated documentation files
# (collectively, the "Software"). The Software is protected by German
# copyright laws and international treaties.
#
# 2. Public License
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this Software, to install and use the Software, copy, publish
# and distribute copies of the Software at any time, provided that this
# License Agreement is included in all copies or substantial portions of
# the Software, subject to the terms and conditions hereinafter set forth.
#
# 3. Temporary Multi-User/Multi-CPU License
#
# Licensor hereby grants to Licensee a temporary, non-exclusive license to
# install and use this Software according to the purpose agreed on up to
# an unlimited number of computers in its possession, subject to the terms
# and conditions hereinafter set forth. As consideration for this temporary
# license to use the Software granted to Licensee herein, Licensee shall
# pay to Licensor the agreed license fee.
#
# 4. Restrictions
#
# You may not use this Software in a way other than allowed in this
# license. You may not:
#
# - modify or adapt the Software or merge it into another program,
# - reverse engineer, disassemble, decompile or make any attempt to
#   discover the source code of the Software,
# - sublicense, rent, lease or lend any portion of the Software,
# - publish or distribute the associated license keycode.
#
# 5. Warranty and Remedy
#
# To the extent permitted by law, THE SOFTWARE IS PROVIDED "AS IS",
# WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF QUALITY, TITLE, NONINFRINGEMENT,
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE, regardless of
# whether Licensor knows or had reason to know of Licensee particular
# needs. No employee, agent, or distributor of Licensor is authorized
# to modify this warranty, nor to make any additional warranties.
#
# IN NO EVENT WILL LICENSOR BE LIABLE TO LICENSEE FOR ANY DAMAGES,
# INCLUDING ANY LOST PROFITS, LOST SAVINGS, OR OTHER INCIDENTAL OR
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OR THE INABILITY TO USE THE
# SOFTWARE, EVEN IF LICENSOR OR AN AUTHORIZED DEALER OR DISTRIBUTOR HAS
# BEEN ADVISED OF THE POSSIBILITY OF THESE DAMAGES, OR FOR ANY CLAIM BY
# ANY OTHER PARTY. This does not apply if liability is mandatory due to
# intent or gross negligence.


"""
SWIFT module of the Python Fintech package.

This module defines functions to parse SWIFT messages.
"""

__all__ = ['parse_mt940', 'SWIFTParserError']

def parse_mt940(data):
    """
    Parses a SWIFT message of type MT940 or MT942.

    It returns a list of bank account statements which are represented
    as usual dictionaries. Also all SEPA fields are extracted. All
    values are converted to unicode strings.

    A dictionary has the following structure:

    - order_reference: string (Auftragssreferenz)
    - reference: string or ``None`` (Bezugsreferenz)
    - bankcode: string (Bankleitzahl)
    - account: string (Kontonummer)
    - number: string (Auszugsnummer)
    - balance_open: dict (Anfangssaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_close: dict (Endsaldo)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_booked: dict or ``None`` (Valutensaldo gebucht)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - balance_noted: dict or ``None`` (Valutensaldo vorgemerkt)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - date: date (Buchungsdatum)
    - sum_credits: dict or ``None`` (Summe Gutschriften / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - sum_debits: dict or ``None`` (Summe Belastungen / MT942 only)
        - amount: Decimal (Betrag)
        - currency: string (Währung)
        - count: int (Anzahl Buchungen)
    - transactions: list of dictionaries (Auszugsposten)
        - description: string or ``None`` (Beschreibung)
        - valuta: date (Wertstellungsdatum)
        - date: date or ``None`` (Buchungsdatum)
        - amount: Decimal (Betrag)
        - reversal: bool (Rückbuchung)
        - booking_key: string (Buchungsschlüssel)
        - booking_text: string or ``None`` (Buchungstext)
        - reference: string (Kundenreferenz)
        - bank_reference: string or ``None`` (Bankreferenz)
        - gvcode: string (Geschäftsvorfallcode)
        - primanota: string or ``None`` (Primanoten-Nr.)
        - bankcode: string or ``None`` (Bankleitzahl)
        - account: string or ``None`` (Kontonummer)
        - iban: string or ``None`` (IBAN)
        - amount_original: dict or ``None`` (Originalbetrag in Fremdwährung)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - charges: dict or ``None`` (Gebühren)
            - amount: Decimal (Betrag)
            - currency: string (Währung)
        - textkey: int or ``None`` (Textschlüssel)
        - name: list of strings (Name)
        - purpose: list of strings (Verwendungszweck)
        - sepa: dictionary of SEPA fields
        - [nn]: Unknown structured fields are added with their numeric ids.

    :param data: The SWIFT message.
    :returns: A list of dictionaries.
    """
    ...


class SWIFTParserError(Exception):
    """SWIFT parser returned an error."""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzFvAdc1EfaOD7fbZSl987ShGXpiyAoCApKRxCw0xdZWRbcYjcSSyyIYmyLjbWDdRELGgvOpJjOBhNWThOTXNqdd8HEnF6u5D8zX7C/7//u97v39/KJk9mZ55l55pmn'
        b'zcyz+zV46o87/P+fF+FiO5gKVCASqJipjAdQcWZzCy3AC39TOaMZthYy3FIhxK3c2Xx/MHq4ZSz+V41xJ3JmC/zBVN4IhoyZbeYPZj8eQQTm8i1qxIJfZZZTp2VOKhLV'
        b'N1RrFTJRQ41IUysTTVmsqW1QiibJlRpZVa2osaKqrmKuLMLSsqhWrh6BrZbVyJUytahGq6zSyBuUapGmAYOq1DLR8JgytRqjqSMsq7yfWocP/ickS/8EF6WglCnllHJL'
        b'eaX8UkGpWal5qUWpZamw1KrUutSm1LbUrtS+1KHUsdSp1LnUpdS11K3UvdSj1LPUq9R7Oyj2KnYtdig2LzYrdiu2LuYV2xZbFjsWWxVbFDsXg2JusV2xUzG/2KbYvdil'
        b'WFjsUSwo5hQzxZ7F3sX2sT6E2fPMlT5FXk8YqPT1AcU+Tz4X+z6pi0CqT6pvIPB7SWsNSOL6ghoGM5WTV/X0ttnjf45kuTy603OB2CxPYY7r/6jiANw2pklQrjgfPxpo'
        b'A3AjR8JDzWg93DYxP6cArUMt+WLUklk8JVwAgtN56Bq6HChmtB4YEnXDc+OK56szc9EmtDEXbWSAZSYHGjyTqpinpncYmX4lLpLtSzEJmC8A84qPuWGGeWeBeSbEPLPG'
        b'fLLFHLPHHHWMdRjmDlP0lHgpOZg7zFPc4TzDByaVQ7nzQutj7tT+/3Mnh+XOrEVmwAqAWrGkPMcqLB7QxvwSLmGZncKmPCxiTiHbODPdAthhyDvV5YqCcjXbGJLBB/j/'
        b'dhmZ5VY6WSroBApL3HxF4c574ABShhwXM7OU96J35v0AFETXugp1jMEMiKLc3x9/O+a71CK2+aeUn2232TIhQ6I/8f45fX0lAwaBVoI7phXE4n1qjiwICUEbIjPC0QbY'
        b'WRSSlYs2h0VkhucuysplgNLWIskRdTyzHbyR9VaT7eDS7SBbAWK5jxnO/Q8yfO7zDDd7geFCluEuVTbAS3SPAVHlYb2+dkAbjhvhengVHsQr3SjJRhvR+pyCjMywzGIQ'
        b'kz3VGW4rgs0QD7F0PN8MtY8HWieCcQ3ucpHCC0SyVbATzF8Cr2ldiLyu4cOrUngWd9ijY3AvqIPH4QYtkU8HtKdeGoMr2qVwB6iCFz3oUEvQfnQQbeXjQffCdREgAh6V'
        b'UFIfWAqBk8aPB+zKrR4wU9kdF1k5gMAwDWZ2+bjdQaOBfM1HvUC9Avds2Pl1d9W+9+xgx5t2UPHeDSC4vrHkGysrwefrl1lZGafY692mmndHeHK5ObmhVebqqO5iIXdV'
        b'+EFBUa6/I3cVZ2KUcEIg3x/uesfOMrbMNeT1970+cHnzgyam6Ug0r7u7qfYv5ZOiPnT74DrU2y4sjlCbO56RFLuNmQVeq7EPCDETcx54Esa85swTYiaKc+ucteGhWGo4'
        b'wBmu5Znz5jxwx/2T4ZVZmNGHk9EGtBltxIKewMCuOLhJzBvkhIhV1hjmSaEm2ydqamoadBlXo2pYIlOKalhrHaFeKK/RJA9aUlNcVl2hkalsiWUhWI24eNQE7qcxwM6x'
        b'dXTzEl1B84rbLqI+v8SeYqPfhH6XiX12E00unrrqLYoBF4leM+Ai7dCsm2xy8tTJtuSvSzc5ue7M2JKhk+kn6At08g7njvkG+w4PQ3FPdE+BYWafd0q/U+q69FuOIr1z'
        b'v2Nwn1Xwz0TsVETuxIJB/oIKhVY2aFZWptIqy8oGhWVlVQpZhVLbiFueW6IAF+UiskiVDWm0HSmIoVTH4uKvTeDhRIZhHL+0cW2uaxIOcfiM0y2hQ3PClzzb1bkmc9tb'
        b'5o6P7vMB327k069qIixbBQHgoDCCW8V5mW7WEN3kENdEtZN5Sjs5z5hDrs8zulfMfUYPOalcqp0vtP7X2vmYhMfaKcjTkga4QzIVbUUn0Xos4OEgHJ0uZNXtCDqOFXMr'
        b'7HbEIUUkiESHVbQjCO1ERzDGKnQEKxBWHmRIlgf0/5mnJjHCHv4vrEo4vXmjiVnpvqotp010b/YRu0nWHYv8JVM2JazOdPX/SM+7ecGjwfLT07C3zQZYTBW0JviLGSqu'
        b'AhVarVRKssLRusycPD4Qwi4O2gtP+Ym5z+8jiXVGNnFQyIpljaKhQqNyHZHLMFYuh4oY4OyxM3dLrj5Ar+53kqxL/9zWyeSGZa9N2Mq/5eihG701uc/KT2X3RKZUxIcM'
        b'8qtllXKNipgTleNL5IgKEitHriOFZESOfsVyNBXLkce/K0fbBIHgkDCSSy1QIOPAxHLsSgVTeuvdUjYsoGavYjk8qtbERfEApzINrQXoCNwEX6fw4XOcmTGc7x3NojB8'
        b'7IkcCg+70KkagsAAjgx1mgHUaQn3Uvg9oS7MOM6Qq1ljb71pBj9Q64wbExaw43MBZy7scAboeBTaSMEnTHdnUjghiyxB73K3ss1pFNzMH+1Sa+IJOcrlAQAdQ+fhAQpe'
        b'W+jBpHFCKrgpGDxgrLmWcEgZALcRcA7gNOCAoxMPD9vhFoqQF+TFZHD0zkIRRoh7yGHJ1weHqtHZ0YR8uAp21+M4pTCUdcmpPkwO55GvoLx3ucn+VyHrFY4vWETh+Rh+'
        b'9aRYgM6inTwKD31EzBTOlEm2dr3LdfO6A6lYL4Db4Gq1io7fIEoE6ITnHApdnhjAFHFa/XhTMHRZayElX8j4oW5tNFkt3I6uwUuYGrTHhyJ0CAOZ6Ry7IvMojKA8JdYS'
        b'qUZvZAkoBl4w3IFeR3sxQXAPPEFRuOXBzGxOq1zQiFc839Zb60bI3IwuoTa1WkpmWQHXoNMAnVoId1CMT5LETDnHzdEM9Kqny36LoFTBDZXxdBK8Z3AXOiwFqAeuK6QI'
        b'f64PZao5uigBuK52Eygc6RRyN+wJCYIZRtgNd6KzAF2cMUyUXBvG1HKa8s1SetWm+ocWlK3xqGUm6lZbWeJ1oHNjJzGx8DTcTuGt6iMYBafJyTrlulqXfLiewlfWoQ1C'
        b'FZVSeAQecALoAtw/jcLXBEUzjZyohQJRr1qXdFpO4YtjoUGIukYTBLQxHDBc1AKbKfwmzxhGwwnJEYquq01830UU3gUdQC1CyxiybWgHWgVbGYvJtSw3TvqgViE6T3cJ'
        b'reGhKwyDrgTR3S7lwfVq1L3Qhixjv08QIwlLpWLcUIM2qi2skYGMd61WxsTVwkt0uAXoZLlwvhadx5YFdTWi1UwQakNXKBVkbWfVQpWGYOmwn73A+BQ3sHK7dgLcq9ag'
        b'C0LS11KNWhlJdDadi4Gvw3a1jTXmJZcPN8xhkpLQARq3WM6ag9ttGMC1qI9nUuDOOEoCloe98DTumU9W1BOANjARi1EHHawKdZsJrRvhRh7gBjjCHUxKBuyga41BV+cQ'
        b'wcaK0AhX+gN0Mmoay6CLy+FarOKxAsCpQe1oOzYJPLSJVZ/TiXibsewR9Vm1EG0F6EzOeCo0aBs8MkmNulC3LeHeKbixGkvBjki28yraGq5G54c7j6FL4xgp6lwhtqV7'
        b'CMaPZhZx9HX88l61m9+rS9k4OyieWcYxH2ddjgXHt9WeNm5blMA0cXSjhHZY+ir402njkYZEZjVHVGNpd1093WFpLG3srk5i1nGmLwJTsByB9kTa+FZxMrORo59vNgWP'
        b'yddG0saw6BSmldMXwY3CY5Z6LaeNt5ImMts4iyqto7BYqTeb08az1mmMjjOkMW/E6lX4lym08RXxZGYPJ4PHacSQCccqaePoVzIYPWdRmQ3orXOrPFpLG6XzcpkOTtRi'
        b'q5TeOh2/1Ya1CyvymBOcDGfzlOt108Nycmmj2L+AMXAeaYEIo8e7FtDGn+dPZc5yQrRY0utM6rjpdBu94MU0tdCSCIUVWhWDpeLaGNaDr+ahDqHKxhqLkb1HMpNkvoyV'
        b'lhNIH4vN0oWF2FFiYRYtZyTwfDXti0TXGrH8YwNJpHLbihjGH+9Zp5g1kG6T3mH2cFtHWzReXzh9aaE7bdwrvcHouVNk2Oo3TLf4HZ82/uL4PnOIWx5iC643TK/7WEEb'
        b'r5p9wHRwm6Ziw9Fgiv9u7jPnFP5IIFKLi2T+8LGRR4+MIJb/P3I4XP18NCQAz0dDo/K0IsLLNaXYhjTn45PvZrQe63JmbgRajwNql3JeMDwnY8/XnuSwOGWcOSi3OuYk'
        b'Yk8Jh5zM8WExZY6wvDwH5pYCqkVL4tHW7MhstClfaJmJz41oNWexXSKrYHvhOS/YDc+SgwszA/iZwxMrxlFfUYJOo25JCA7l10Xm8RWwC1jN5dqKUAvdblUo6oTdPIB9'
        b'iAEkgkR0rExFCKBUOOWS06kp2yalXJFZk8o2jsVnfCtwNwaIysN+8TZjj1OZy9BVaRQ1k3i810EFbA6kFwVQPxvqsulZYTO5AMiGmyMz4ckQBog0/AVym2K0mtLhAeAm'
        b'KYlx4LFkuA1UojUVWl+KHxUoCYGn8MmV3h7gs2wmDziKubh6CR6l9q0AO42T9GAmTSMHs7GzqQ2bmIYOSOEZvCmwBV2F7UBRDrsotdb4tLhaKqXDIz3cB+bOjGSF/4gv'
        b'bJVK8YZmoNfgfjBvyXja7o+uFUvjCMAqeAnqQLVtI3u5cQ2tKsnOQhtDvVBzHt4YvC02jdwxaQydB3uTww7SOEyBM56xDcjgaZGWHLJGof3R2TkYIRK1SBhfuAoIZxLb'
        b'1wWPizmUeEzYeXRQGofDThwSXIC7QE02lx1UV4900jhMo8VYuBvMRfvQGioDcb5xqBmf3PCm8XAEfsmHgQfG+FL6XdGqBGkcVpxF+Ci8B9TCThWlozQFrZaQ7UDr8+BJ'
        b'Xh3aBqySuLZYGF5lqTiB48BTUniezIt5oweKsfZsBHIN7oTnUHNOFjkDcpM90VUG7kavr9Dm4l7sD1PVOZmZueRu6PGZPCRCHJobIQ7nWMLDMnwiOAIPhYTAzjyoc5GI'
        b'4TZ0SOIEt7k4o0Ou8CgHhx9OdlAPeyYrHv32228oiYji9+OFKeU5jtMnAEpe5YIASV54Bg/P1wUNKQw85gzPi52o67DGM+9VW6u0xFptg+fRPiYAroXtFHHmYuxsu21o'
        b'p20IOs+I0aZSipaBVqLDqJvFS8aHk6uMBO/yDsrGooAUNUYiMWPLBLSN8XWey9rG/cFwjXq+1pKYv81oO3yDEcGzQravywauwy5sITqLnZ87egNtZPxKlrPisw8dXoLj'
        b'BnTWmox5DXd2MTFoP7zMRkc4iOwS2gjhZmyLUad6JjMLHnyFUjJTEKrWWC7EjpuTBq8wXujgaNYJX0hD7aQHz4WJP4NeZUTj0FW272piAOrWqNBZvLSEGfAq4wmvwBbW'
        b'0e5DF9AONTqjEeBAYh+YloHX0YbVhXBrKqZsrdDc2hKHljOmxzMZ8CA8wi7uaCA+vXVr51uRlV90QLuY4CB4hlKfhPailUIbKwuMRYDGMpnR8DztakCvJWOXrsLxEhee'
        b'RWttmHi4fSQwz8dnwW5bdIY4oOiZ/kwqOpBIJ1uO1qLN6vnsXHuF8Dzjg1mtG761QUfD1ZZ01+YjLIeMqBaup13es9E6Ie3hwnXwNQcmCh9Fj1AuostwNw5GBADtngfC'
        b'QBh6bRnLjbVwQyBstrWcv4ARCLA2nWJgixieoPrnCt9AB4bXVZqOV1WNTspH7yxk1PexgrV3hrZMfSPvjyl2e+/8wn3n3SC/yw094/ixGbGxqYdS9IeiZy8+U5jV2qpP'
        b'sXf4yjbkEROa3NSu/+r09zr3d2wNzYdufLRvr/rbDxZd+O4qNHz+2lWfN0GVoek9/ganycz0NbsedhjHLPvDPeOmaZOq+Ie/MFbfaT8R79d1Z1vCvAPv1JXN+VwWeuTE'
        b'yn9u+bVTfWfl7ZbUxuqH2d1rpV2zSrpDiw9edfL4Ycos5785X0z88K2m41Grvj0osP7KLXt716SOiQW5H7Voo+5turF/cqlN10elB4oLVYaC3t/Mr0oeKR4GXBcrF7wR'
        b'e/jSm+HXxzr8cPTj6FeuhPT/pTovdc2srZfuNNWGXF6w/9vLNy87LNvfFGn5SuSjT6KrtTuOHvvZ/7Kz8WCnVd2sNerCGc6/xL/766yOQfu/770vV+bBM6qGA/nHHN+u'
        b'aFtT91mC/oPbX9R+l+L18/jle999EPPpxWUHHv2Y1n6j5YDiD783jnuvZcPVI+1LytJzm1oPTPz2hNQ3/u0IaMoePRjVI4q8+svXk9LNdncOOl5ZvXbqTyekF7Jnh/+u'
        b'4LDx4rLTU0Zdivh8a/wPG6+sm1R75d438j8cCt4buLj0s5O/Hfzdb+tX/FO1LHHPFsvwTYUfrJltduH3537o4CYEl3/UYr9s/MctcyW/3om48qfVC99O3O58Idi5/qsH'
        b'Liu/a1jTOD/r1k2x+QNvKjJCeAE1h+VhQ4c2hzGwHZ0DQngcW/WGgAfUkx3B8WuTJCIzLBSeh6+JIzAYWo/DIxGvtBate0APaWvRIVvU/PhqbWY8uVyzy6Kd0QvTJBHY'
        b'qq3Ho+t9gQBu4oSjPXDjAyLlEzkJ2WEhGailXJHNAHM88WK0OeMBUV87dCk+OzM3NNesDnYAAY9jDi+IKdEqhZMkgwd1YaF4ULQeW+nNXOA4lot2z0CrHhBhd0K74LHs'
        b'/HCscguYSXB3agq6ILZ+7ubk3y/UpBAN/zU1Pb51cWBvXTSqCqW6gn2tUdHnBoJzikMvXx6kcYB7UCvP5OqpyzG6inHNyU3n1ec0yuQXpK/Y79ph3xGt92rltU7fYkOA'
        b'Mra8MuAabnQNH3CNNLpG3g0KbU3TuW3JM40K1blvzTc5u+tCtpQOOEcYnSM61APOUqOz9K6Pvz66ba6+Ql+pq8Pg9lsmD4MPCYCXT3t8W7w+dndSa5rJw0c3vy24daLJ'
        b'07c9sS1RX7V7fEd0R0yfZ0Rr2m2/IB3fJArSV+rn6y3YKh6RVj1F+rTdSSbpGL1Pv1eUydtfX717jilqtN6z3yvc5BOg1+yuN/B7nLqtTYHijqKDuQZZj6a73uQl0ru3'
        b'5Q94xRi9YgyjP/NKGEGNjNV79HuFjXyMkOrdd+eTT4p+7xiC5tKWM+AVafSKNPA/84obhvsyItoQdHyeLm0EmuBKovQuu3Pwp/Y5bXPay9rK7oZG6p13Zw/ZAO+A9py2'
        b'nCHAhKYypokZ97lMaCbzADDeWczdwOD92YYgY2C8Lt3kG6DPbF9hEgXqZ+y3NXD6RVKD1iga96lIepdtGxDFGUVxBu2AKOl+JgP8Rw3l4JjQH29byRarIQ7fw6FVMGQF'
        b'AoJbbema9+RjZoeEnbbptDGo+0PGGp2CWtP1/M9dPfZpO5yP++IF60rarPTFRjeJKTRyl+0X7iE6X5ObF20t63cb3eNkdEv61G30fWvgHYaXgqXGYsv4vlGJ/Y6Jd8NS'
        b'ep165dd9jWEFeLtdtuToXW86iYlsiLeU9YUkf+acjHdYL2gbN+ApMXpKOiYNeEpvekpNkem91TcSrjcYI0t0PDpXyU23sJ+mESF96vrPfNDqGal+yQXg8zpCr4ueVg+q'
        b'CrSYSPoTwPDNModhPO6D/4Nrwe2CIHBYGMUVM2wAWYkOZWeG4fganwdOqkk814kuPnPesh456pD34GTr4fMWeaIDLz7SxVo/Pn/x/rPnL20mjkUspxBjoRZVPPuOSx+H'
        b'FzfKRLlFCbFRogYVrcREWFpmakQqmUarUhIchVytIaCVFco6UUVVVYNWqRGpNRUaWb1MqVGLFtbKq2pFFSoZxmlUydS4UVZtWaEWadXaCoWoWk43skIll6kjRKkKdYOo'
        b'QqEQTU2fkiqqkcsU1WqKK1uEd70KYxIYhSV9VWB7qhqUC2Qq3EOeo7VKeVVDtQzPr5Ir56oxralPZlgsqsXTkvfumgaFomEhhiCA2iq8FFmipWU4XmO1TFWmktXIVDJl'
        b'lSxxeBxRSKq2Bs8/V60e7lsixtAvwmEelZfnNShl5eWikAmyJdq5zyAQFhHynow7AbcoZHLNkopaBYEY5t8TgOwGpaZBqa2vl6lIP65VylRP06UmkzwBqKxQVGCKyhoa'
        b'ZcpEunQMpKypwMxQVyiqG8SWxFPgierZedJkVfJ6vA2YWrLAke4qrYqsbPGTmaahQ7UqrfIxBHlnSqQlxtVW1eIuNf6krX+aiipFg1o2Qka6svp/gYTKhoY6WfUwDc/s'
        b'TwmWIY1MSWkSzZVV4hE0/29pUzZo/gXSFjSo5mJdUtX9P6JOra0vq1LJquUa9ctom0pkTTRZq1FX1arkNZhMUSRrGUQNSsXi/xiNw4ogV1IJJgoiGiZVphwhk74B/TdU'
        b'TpApKtQaivK/Q+TTrirxsal82uY91uHGBrWGIA3vkExdpZI3ErD/yroQ/svklU9RQ6yipmJkY6dhq4iHVCie2t0Xtv/ZMZ8VhX+JRyoZtr5YUBNFWNNwbyG6XFVXyQ40'
        b'AkN0EC+grE72FCtHJsPLUKDLarVM8Ty4Bhv9/2Lxw7gE4gkhL1jtbK2yWqZ8YoGHh8c29yU2/tkJMMzzeHMXPGu7J5MdQIdqNGqsoTXYaZHuEeBGFWYW1u+Kl48/Zbhb'
        b'pgzPU0U8Tdkzc7xA0xNfMbw5z/mLZxCe8R0svBxP8XLgzAmpec9ueVmDSj5XriRb+6J+5Q/3VVJhwAogmqSS1VcvfEY//gUB+pcVrbYCW8GXqvpkWSW6jFVB+R+flIgX'
        b'lVmi38/MWYR7XhRcZUW97ImWD8cgopA83PxYLrSqRuoTX4AqkakWypTVRKyXLJRV1Y1gqGWNFYlPBzEY6anoaBhqllI5J1FUrKxTNixUPolqqp+OoSqqq3HDQrmmlgRB'
        b'chWJJmQqeZVIXk0ipUR8ZqyoJ2YBz1dU+1xWX4Rl4nDMlyhKfakli7B85jLfBjx/mZ/LJh6dtCZ5cLWRQlAe9s7YGvYyPN6KXks2kmvJZZbhQEse+TlobQzs5gBlAxgL'
        b'xsL1WRR0+lJyb36jnhGVW50LD2Wv9GEr6lxGr67x4ft1cnmNTqJrWnI4D5YoJOIstFGSlxPBns0lgtIlwM+X75FhLbbSBhKk42gNJHfiWZnhcENkVm42PCQJz0It2Xl8'
        b'EI1aBJK5DlqSyFiIzsGjEtg0D4OM9DvAfVxogNtRN50PdqiqyVU23IV2PXOZDddiCHJdOUeBLjy+tbZHl5jhW+vNBfRK2A++Fo+as1QS1JKbFc4B5ugiB25AO7PpQ0AC'
        b'PIVOkfEz0cbsPNiCNkdmoBYuPI92A18HHtJlhVM4tNcPXSJwUWj9MCh5P1kfiSkOlPDHqeEWLUksrUTr0NpseKngyZD57DNDXi4DxPAyHy/kItxDB82Auxrp2s4vezw9'
        b'eUnAkIHl/BR4Gq6iDzYzI/DK8D88VkRWLlofJhYAT9i5DO3mwYPokJgyykcIu4aBMnPRBgLjCjfAVc68KO1c9tHjMDqFLr6we7i5i+7fGHiBvcpvggfhAWkMeaJ4VQB3'
        b'gurGOnovr7JGWyXQUPbCblnW0RtZdBatRC3SGJJzdhTth7tB7eIaeqWpXIL2oa1mAB3IBlEgCk95nI4Im3hywoFY62f2Fq1Cu9n+/XDdwseb+0rgyN4eQT34uEWvj9fD'
        b'FrhWCs80CtBBeAQwOQCecp5MF2IFL6F1uAtXI+zhPlAHT0+iN6mVFaGouQHpnpWJWqFYQNchKMAjShu5sJMPmGwAT2IyjtMRA9ApN6kUGfhVaDVgCgE8mxRAO+zRgSyp'
        b'VMVNTQBMPoCnURtkr7eroB6dwChn+HBVFmBKABata/Acyy+SP3JGKmXIBf8GeAAT2BHF9nShS/CcVIo56YMOw4NAgbapqb4KpriCMDDkbi0q90qJzGdVG52ciNaoGdAY'
        b'C9JBugvcSkHdve3xIbVvFrexXCGcLwRiLhUUdAHqzbLhfrQN738LferBDNBx4HZ72E41qt7WJzsiHHUFhpJdhqd4wLaEq4Db4Gm61tGh/Gx4bBo+kvMBj0fuFLuWjexG'
        b'D2oOJqxDR9Brw7y7CC+zrzaHAuZT3qFjjSzv4K4oKpiTpsE3XqKDp11YFUSr4Gk8Ppm6Hp2rImxeWsGyGWKpoh3Zcywpk9Em12Emd8ymY8diaVlNBh/9csWFG0X0tQ62'
        b'TUGX6Fb4LyE74ZSqHYWba6bBNdmxsv9OmzdA9hlmWXUl3TB0LplsGLyKtrGmY8N01EkoEE5+qZYfgScofqZttVRKEj+xULSDWnQGj+tHKNuENhRmZ4bnRWCtDhm5D/W0'
        b'xgtby4OHHWOpSHv4wSMS9CpaQ5IkwzN5wMKMAzdFzKOS0POKDfACIMw8qlzxO5tJrJF3gq3zsmfAzqf28QgWWqJ20TK0NdsSXnxeQFLhEVYt92FhuCzJCndD3dnhoXkk'
        b'fdp2LleWCXVaf6LuxWOffVzFDIMnecBTik7k8ODri8IomBZtDnnZI2xEMHmGtYF76qg7gV3zw7KVsC2LvLPCTZFPmZ/QKj48Djugnpp6uNKLvOqeU9LX6JG3aBm8SN9s'
        b'x8A9ZhK4Hl0KefHRFh7wZF+OTvkoUHMQOjz8gEifDxeN0obivvHYbhuyR1iCB9ociQfa55dDbsWzCQti4E5BJmpeQocSOdZhKjLCsvLDG8IFQJjNQftEcLPWixB6Al6A'
        b'bzx54sSfzvLoG2fDDKyl9M5901LUiZrRXrR6+PGUPJz6MbSTgUdhy8jjuR1eKHk7h5vLqLeoRFfh1cfP+4/f9mFXdTkv+BW8Q3bU8M5PFnKA2RwwFUyFJ22xflFDsgcd'
        b'FWBDEjmGGBI52kCVSwHfQCeEKgEAviLUCeAOpJvKPkxfgruxH97KANdgklcJd6movLlmkjyBWjGnvNxKsCSKlTds1C+MR1vRTjOMuDUTbgZlqNWPZfs1tMYGdkdxyaMl'
        b'ZkYHaECd8Ki2BPfNg01wtRo156CWzIIp8EzU1ELsY0nueER4CF5/aMPk4QfdqUQ51oWVZJCVU+YWZISRHqwy2cVTUAsPwGtL7SE2acfp6+3FGh4Ok8xdzFLKrWa5VALK'
        b'PrRnBu9F7qFLSsw9TBS55qOPcZuwqz0Ku2Ox3zkUC5gCYupODj9N+thjm4W7GGz8W6itO5WYoJWyvnXVMrQVrstEW9AOtA2uW4CLFuyoT8ZhyYOn+PBMZaGmEp4bzeB9'
        b'F8yonMEybxPc7UCHRFdz2BFfQeuwrLAPl6vDs+fMHn63B4IyTii6sJia8rIAeADbcku06Rlbjl7Lo4KI9sJLy7LRa7Oe13QcRtGhJ8MNTnSR2F9cZleJ1jhS7SVxg9UL'
        b'YYk33MmGJSewWaMPTD0L4YbnAxPsHvbhwAS2LhPz2EzcU26wRRo3n7sCHQJMFv4sS2AfQ5tKkV4ai2UPvu6OYxGZdB4bpKwPhc3S2AUM2otdbgqAncoFdMVwB1yFw8ru'
        b'WGTAwSPcQN3BGXQYc4uhm6OBRxfj7miAzqcBZhI2ZujqDC25uw5CrfCEELVgtduEJQxtnooM1rArNnpKxoj8FYaXwGvzCp+XK7xz7ZZoV/AiVi3WTkPb4XEB0NaDZWAZ'
        b'OoE2sV59c6MIHo+DXRxpMuC4YP8/Ba2meleAI7MWeJwPGpeBV8ArDkn0+wNoDWpOVNNs98KQjLBQaiSjqqc9M/W0cDO4HZ6ZpE2kkfeiGcK8XNQSXjKsJBjyCDw/LSOr'
        b'OKOIXQ3snILW5YZH5OXk80mcZrCEawqWDSd4LIV7YRv51gA2Into4vNadIxKwnQ1wh3wJPFw+yNRG4DHc3DsyWEN2gEc+a3EgoYjn6PPSBozhZpm75jZ2VYrnpcyO7Se'
        b'zTT1h2tIgmz4QnSe5BygC0wsPD+WDRvOLrJTF+Lzx/lGWwHuWs+MinKlyUDyOSuTGbUz+UpL+PGTJXeUnulOyWPH/uXXC+v/9Lbyk5sL9vStPnt+t8Parz7jW77FvDt9'
        b'sLu55KsDZxolgeXFRcV9Gzxbe745Jvr8UPw4sM7s7krXu+49X31w/17+n+50iCq/ufdB/NxrP0vnfnTvTz9tvnuznlvyT8Gvf02/YpsseiT4hzB2WX/nQPmehHDuo08u'
        b'9jHTEr8zq9y/XP/Frm/AHutzcX23r2oO1x/53X6tY/q0lpxpgnHqr/beBl91SY//eMDdYPZrlfr8h4Mlr8e91/vxO79/F21e9v6HlTXfb7n2zoMd9kvyvT6KW9xQXtJm'
        b'feLsdf7Ya+/d84i2Flb8MmB2dknQF27NP5yulr4T1w0+36n7YtorzT9ErnZ1C443fD8z/lzwqe1uudGGv04PsTWc/Xhf+YyfkwL+XP537vz2qqtrPhzdsmLyo8Sv49KX'
        b'dR28fFqU8Uts0e+ne+8r/Hti3erPDP7Xb1Xmvjra/VvBxw9zPvpu0gd5c37319ahSVbX9PfHrm54W9V1+L4jjIyJcP/is0d+X+50So6raefO5ir8b0sNh5NiDN6L0x7Z'
        b'nF4w/c9nblf91fL9ce+/H/Zwho8hrCuse9n2b/zel4SdDr1l9gtSfny57lHCmdslt840H/+b082F02dZN/XNerdNeXzPgirtt982Tk7f6Dx+fHjfie3rD9aP/zHpyzs/'
        b'dN7xWzbty88/7jneV1D0zoTiwPfM2yJb30qQLMq/vZJ37/je+82f9+9sqcjboPSrXnws9O2ji/7++sMPs9VT1k6v/fqc/g93Xv/2767jQt/OVK/PrjCTB0+u22Bw7fv5'
        b'S99jv14Zj7I+rlj78dbBwwGd3y5d8sqhA+feP355UdK4LaOkQ+/+5WPj92eSd9/OdRibEfEHUf93Rd+cnu81TZ4+5a0V6VXvrZn6R+DzRk2856fvLQ+4+xbz/tYiz5IP'
        b'3n5Y/bU2ecvD9Rfkp4PeVK/6vO+vQ7yigT2CT+/tmpPZ58g0TL/27pIv5/TuHTXju5Df3/jK8/7nqybeKVOqamJuuyo7L+fNivW4X9v8WYO66M2Yk8Z7HzaWfHXvyjfL'
        b'VWE7ftr5y1umPctcrjHfPiz8cc+FnT/umdGurbO4tHCH9rtfiu4sLFmUq23P3dfvae9SdP2N94t7v78zvcjhi69NC3/72xyX27/+/q0vCv7xWtehX3+qTC9c4dR8Kulv'
        b'SaOPv7X9+xWVd1q6NQVW7Vu+vXDi1pjs/s9zpl/J++OlSx9drfiH9juHt+Rjdm9755e+S17f/9jmsccm8/gnh4ovwCu79jWXvu1u+Pu8vswH4e/PCaz2eMj7dIFzPnpj'
        b'qG5ckXPSD/bTnL+YNmaFcO/QoHPpG/wph+Z4vP9uw+2GXZH3bHKHuGtUP+7/LmMj72+j3rh5xadtM++LY6qfXBe2pb8jNyiX2G4p0G6Ubs2ZyQ+59s+jP4pNq7wfLZJM'
        b'7y4vKe7p/0Pg4KZli0BAN99249+P/gaSdjiJ4qeKbR4Qfy7LgVeHExSwLSR2E0djrkvQIXiel4HOTH9AA5DmunpJXXJohBg7KAAsZnDgYQDbH/iwZzEc5tEMiSfZEbHw'
        b'oohXyocHaJrDjPGwU1ItGk6DYHMgfBzoNz3CsD/amr0MXqFpEI+TIFaOotkXaD+6QALRkQSNKegaM5yfgV3zMQqDA6NREuxQWzNeTIiAW6awGRqvKjwlpWhbXm5YFtoE'
        b'8CQXOQvj0H52ccfd4cFsq7k4XI3EbkWwkBOBY7E9D4i3VHvCS9mYriy3x2uzjeLOhedS6cI02B1czV5Y/nRoUVBFFwZbndERCVwJrw0zTQBPcKTorCubeHIJXZ038v0W'
        b'hKOBx99xOQ91lK1L4I4lqBtvBw7UGke+0cVHZ8fxcCh7Wiz6v87m+B8u1ES4RC/+NT3998y3duo1CbFRKvJ8TBNH/ihgv7WjFAAnt53jt4zvdwxcl2Zydl03yeTkti7d'
        b'5O69Lsvk4rpu8m03r1beLUdvXbU+fcAx1OgYesszuIPX7xnemmZy9dy5dMvSrctbeSYPP31qm6TV7HNXz1tOXiZHVzKqXjrgGPyJY7BpVOjRefvnGRwNFf2jxmzJb03V'
        b'ye66eul5W5d/7im65RXRoTWUGiPTbnqlm7z823PbcjuCbnpF3Y2MNYnDTSFhpmAJHsIUFmUKjzZFxJBSEmkKjTCFRdx3t/bz2MUf8gIevvrA3d6m8BhdXb9bqMndh370'
        b'9NEH7R5nmjD5Hcl1yY2q/gmFRq/xunR9qNErHM86oz9yPJ5GLyZ5IhglvN8dDxypq91tiz/2+Wf1u2d9OSraENTD6eEaQntkvakXa28EXGzoH5VnCgnvqDBwOoS3AskC'
        b'CgzzO5b0BybeN+P5eej4Q5bAy0+f1+8ZY4pN0Ef0e0WTXBJlv3esaXSiPrLfK2YktyRubJ9/TL+XdOQz6TZ6xfyVLmGP9xDHReRh8hJ3xA5xce2uVyDmpLNhfo+9waN/'
        b'1LghPm4cEgDvAH3akBmpmwPvIH31kAWpWwJvvFtDQlK3Ad6heBBbUrcD3pKOtCF7UncA3iEdTkOOpO4EvMM7qoecSd2FHceV1N1YGHdS92DH9CR1L+A9Sq8Z8iZ1H5YG'
        b'X1IXAe+IDs2QH6n7szABpB7I1oNIfRQICjYFi02hYT9J8GcdbyiCsMy+bQybUDLgGW70DL8lGW2Q9aT2VBjm9Y6+YX8jpnesMS6vX5KvSyP5O6bAUW3pdyWRBvPO5JGW'
        b'IF26KSy6M6dnojFsvI6nm2l0CzH5BHRkGYPjB4KTelIHgif02ht9Juq4mHF+ozom9omiDNlG0Xgd3+Qb2LZkwDfa6Bs94Cs1+krv+gd1MPuDdRNJqlK1XohBfHx1XDxe'
        b'27wBnyijT9SAT4zRJ8Yg65rXO7E/brJpBGGIC/BgT4D6R4A+jZt8NyT8tLBTaEjvyupl+kMmtFnrBLfEsYaSfvFETPH0NhtThNSQaqjomIc/zjG6Se7GjcVcmGCQD8Rl'
        b'GuMybwT2x+Xf5zLusTonXZ3RPbRjoslL1OcXjSXH5OatUxrdwgfcYo1usYaiT90SH6tDUIcT1t1b/jFDgInNZEzZhXiQ2KnMz4AJKGJwo3cRc3cYv6PS6BZtCDO6jR9w'
        b'm2R0m9Sr/dQtl4wU0e8eddfLpz2zLbNvVEpvUL9Xho75Miikw/60a6erwf64x8EyU4j4tFmnmYE5bnkLK5DfheCu4B6/bqJC2ovK/lG5z+hJ+u5kkvgV/gnW+ph4fdgn'
        b'XpFU/5L63ZPuunmRSUP63UNx9UufCExlVKIpaULfuBxMfFQuId43jxDvnsfc9Ru1Netbdx9inFZsWaFXD7hKjK4Sg9MF7y7vHu1AdLoxOv2G08fe73r3TZs5kDnLmDnr'
        b'KzfR567et3wi+iIn3XA1Rk7p9ynocyu45RHaJ8np98jtc8oleU+z+p1DbjmN0ms7So3B4246JZmc2K88Bt10CsHcb003+QVtzbrrKdL7DHhGvTAeyXDzMXpGGRyMnrHE'
        b'fPrpi/pdxSRPbnzb+A7pgGek0TPSkHYhqyurR92d31vRHzvZFBhyNGt/Vof6YP5A4Fhj4NietN6A/sBJA4E5xsCcG1P7Awt06beCQjuiO6tI3lqP32dB4/TMEI/nl8OY'
        b'YuJ7mK6QnvRev96K60EXczqCsIZagug4Q0UPY7C8FZHQE9TL9HJ6xP0Raff5XLG/no8NSGBIR9zBZFPyxD5xYn/gWFOQuKPkcCm2VB3uB/Oxkx2VhDUcA1kPBMSZ4sbo'
        b'efo5RpGUZKV593tFGmKNXvGfkR0M0Gv63SUk5Wy20S10wC2aCFTggFv8l8/z5n4BH7h7/6WID+ycb9n560d3+BgDxty0SzDZuey03mKtk920C7zr6L4u99GDaBAS8zPg'
        b'4PXdCo03jskwhYzvDTaGZP7MZRKyiTBIcogwBOGSS6B+VVthp/dJiHWxI+9TR6/iSDM2A81ukEfeyP6FzLN/2TGT+63ylzli6ntp8TqBSwZsploFj2EcHgJckHQ1h383'
        b'XW2vIBycFI7hPvNeN5Kd9jMJsraD2eTXSYCKM5VRcadyVLypXBV/Ls9itZg/aEcfBmnSmCpdpWpQyTdj5F992fdCGjmohhPEZNWiCqVIRoAiKPfyxIJB87Iy8lJaVjZo'
        b'WVbG/rgIrluVlc3XViiGe2zLymrkKrVGIVfKlA24waysrLqhClecy8pIdpm8qqxCo1HJK7UambqsjA7OpglSvo0ZKQhpavLtptfA762iKQS9os2B7blCG3RBI7TAUWpe'
        b'uAquh03DQV0kahfwkT5ZzEyS33OXc9Q1eJC+1V/JtkzORyl2a+be+WSplPnk+yC/Ju8Mkd+2KR99vHRD9eq0qYHqb3YOrXCfNR90rW1IGvtjS+zHBy9LZr9VPOfDT+d8'
        b'3fx2l0fCLZeEgllTGkWC9rSPHXddm2j8q9ZYvEq5+Y3t7RFnv/C4xk06wVneUpt4+offcg5+GORf/9vYQZdX/XXfL213uMvcK54YWbn/j+k3XbZe7tj4/okPZoU6FO9K'
        b'T7K2jfH/esfKQ2Ufrz660EJ8yJcfcyNGfUMqDInJDpFKotqyO2J2dsHZ6S0zJq+6ldZ88TXtt4K4tlmmmj+X77y4dnmNp/e3zKUxb9pvqrg+yTZ4TLovd8+XXhM3Jrat'
        b'H3KaXb4xe/aXlw4uPlZ06D3PQ7KPPpnvqCgfww++brFzb2BD9A9C8fQt28QlskXTcv/wSWv6jNePbIcnf+z6zn3NQ7ME/tZHZbeLLR5ODfigr+S3P4y7Pyl3XmvV+dpj'
        b'ka9vWpv5W2By0R8fhFb++MW+gsK0uBAxj6Zaw2a0D65HzTkMaAhlxgC0qRpeoEE4XF8G97G/qzDyqwqVofR3FaAebXpAnx+21U8QhirUOP4nR4/HcL6wm4dOQ30Bm0be'
        b'Aw1onxqezMgLp28U+QXkkGKPWrnQULpI7M7qp/l/W/zPxerkwCJKoX9NL/yxQTrWI0VDRTUW/rSRCN0Ml//EEXoYsHYe4plZuN6ydWiNaV6o82te1qbWx+gr9o/evaSj'
        b'YPeKrkCDqsevS9tT0LWoO+J62g0HlNEfk3PbzUMXo6toG73bQp9ldIswuBrdxvSNyzO65vUVFvUVlxgLp/W7TrvtItI7bFX22QXicMVtOoOdg4NTa+oW53UTHvIEFiEP'
        b'7XgW/kOAFFbmIkuTlW2ryxCX1Ny9dDVsbZS4I46tSeN6BGwtZWJvCa3dpRh8UqMYtEYxaI1i0BrFIDUck1nbYRwztu7hjbGG68GhGG+4HhuPMYfrqUwag7HpJ3MW24Kt'
        b'U+zhelhMj6C3xGTvqqvpiHtZ9SdbDNhn7oXDXQc33ML+d18o8MetPg/tchiLacx9QP83VMoBlna3LOxa1brRrXVGC/+HnEVcC4+HgJRDtPyZCywDSGE3xKOtC8xw/QGH'
        b'sYjZsxj7KYsY2nmfNDwakgkZi0zmloPvIau+8En9osn9Dhl9Vhms99qQ6pVmBd60ckzz5bLey2mQgwXmP+e7Xiq8Ti/xZ098WtpIQc7r6qRhnyZmGDvi0uz+Qop/16Ud'
        b'EMSAM8IkrvzP+XY8+isw7425JGtJslmZ4pZ2bXzKvSZL80trJvd9xk1RBbwTs/1dn97qBP60u1ffVuTk6L7NvR/z82WejUOsKW9fUu5Zh9qSxN/Lrv3l7psdzR+9ZXzw'
        b'03dZB/526o/VVS63Dh8d5+G20ioha0/B/knc9GabJCvuqcaH782a/OPUbenKIqUvuuh4w3Ka2OwBuWYuRIfQFdVM8htP+fn02c0MCOEZDurIDaDXDvBMQkp2fjjqIgBw'
        b'B7yWH87BRugyF+6PK2RvU1AT3Aab4eaZcA3aTJ7WYAvcbAZsHLg+qfAY/XoJ2poqz166jH45hX4zpRquY281XgtBF9FptDX7qd+NEoo5qNUabmcJ2AgPhqH96OQLvyxV'
        b'CFc9IFf9c2PnSbJIXoGGfGkSXUkXB/zXtvF//ZbjpQIZMGJNX7SlL7WrcqVcg9Ukd8SuTsbF35tIbMR3NFk7DVj7GK199izqtw5pmmTiWa7NeTWnz97v0JibvLA7PN/f'
        b'8awfCpby+TEPASl/oeXQEiGwcmrKf+q7DKJBrkKmHOSRLPtBvkbbqJAN8khqFY4w5VW4JFncg1y1RjXIr1yM45xBHkmyHOTKlZpBPv1JlUG+qkI5F2PLlY1azSC3qlY1'
        b'yG1QVQ8KauQKjQx/qK9oHOQukTcO8ivUVXL5ILdWtgiD4OEt5Wq5EsdSyirZoKBRW6mQVw2aVVRVyRo16kErOmEMm542aM3eB8nVDWPioqIHhepaeY2mjMZ1g9ZaZVVt'
        b'BY7Tqstki6oGLXB8hmO/RhyqCbRKrVpW/cTa0Buo8v/2TyRijUTuSEF+lkudj4vffvvtH9hO2DI4IiWG4tnyJ1r+O2aD2MfrloJUD3DdQ5gaxP3VfOQXlQbtSPRJ68Me'
        b'9lePmmd/G0+kbNCISJ+sOk9sriKBOQlRKxSKYbFRkcetQUvMXpVGTXLuBgWKhqoKBeZsoVapkdfLaOisqh+RhifB66D5ODYqTlapARuYq3NwMcRlGOY+h8fwhqyA0LrJ'
        b'7CdeloBxGpppBSzsB8w9jeaeuqwB82CjeXBfWPL1USikPyzLZG53y9Klz1Xabxnbx4u9Bexa3T4FHnS2/w/dAmeC'
    ))))

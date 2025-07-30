
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
        b'eJzVfAdAU0ne+LwUeq+hh06AhBJERaQoKB3FXgEhCIKAeYmFteBaCCoK2AK2uKJGUYyAim3FGW/PbXeJl11zbOPa3vbDXbbf7f5n3kMFl93vvv//7r7/F5/DvJnftF+f'
        b'N7/3/gRG/bgjf7/YiZPDoBQsBivBYqqU2g4Wc2RcDQ+M8yvlnKEA6KQe38ttSrkcIOOfwfnOJ1BrAW2zhIPLzUp5Y+Gfp3CpueyZXihQyp8DLMtFZt/JrOYsyJwxV7i6'
        b'plRZJRPWlAkV5TLhrA2K8ppq4YyKaoWspFxYW1xSWbxSJrGymlteQT+GLZWVVVTLaGGZsrpEUVFTTQsVNRhUTsuEI33KaBo3oyVWJT6j1uSL/1sTRHyAkwbQQDVwGrgN'
        b'vAZ+g1mDeYNFg2WDVYN1g02DbYNdg32DQ4Njg1ODc4NLg2uDW4N7g6DBo8GzwavBu8HnMFB5q9xVTioLlblKoLJV8VT2KiuVs8pGZalyVQEVV+WgclHxVXYqD5Wbylrl'
        b'qTJTcVSUykvlo3Is88Wot9jkywGN3mPRucnPEnDARt+xpbjEb2wJBTb7bvabAwJ/tm4dWM9dBNZRlitFnLyS0YR1xP+dCRLMRrhhDhCZ51VZ4Ls/CbngnpsNzhVFatL9'
        b'gTKIZKEGqdFu1JifMxupUFO+CDUFoV2Z82aJzUBoOg/dEaaJKCXBM9q5ELbQmbloL9qTGwPPoz0UsMrkQB06g66WUKMm4fR4EmqcHHRswBPBOAMYj3yMKXOMV0uMT2uM'
        b'T1uMQ3uMTUeMbecyJwZzmLUan2HETRwGc9RPMMf5CXaozZwRzI1b9wRz2/8ZzOWymLs50cxtI1cAgLAosi92HWAKp4VzXcwByRXlZMyJYQu/XmXBeZ4S4rKiyK9FQrYw'
        b'uogf/3fKAYCUopxleVxwDlRZ4eJ7Cz2imy0/CAbgD6Gfc67GPG/zCFRZ4oopHm2UzhwIoyukgW/Lh5K3s8VzBJ/bH7CnwoaEjdY/LHxB4gUGgDICV9BceBiTcHfU7LAw'
        b'tCsqQ4x2wXNzw7Jy0b5IiX1qpjgrlwLV9pZT3ZeOIRPv8YrrCJm4DJkIiUAZ9wkhuP92QpQ9SwjzcQhhzRIiTWwPvAEQRIfk8H6QZwFlFC6EHagRncQI2BORjfagxpzZ'
        b'GZmRmQthwzwQmz3HFR6YC3fDg2Al3xydQEcyle6kzVXUiXRSdBG1wmsYD/AcWPMcbFWScalkK2mKDewlxcdAJTyHTihdSJtjk2kpakXXY8nNIVAyF15XEq5BrblrZY5o'
        b'Px8ACZBAdTUzV22dFcDNLKLd7O2Gea4sK8xVOgEidtGSCZtPuVuAipdVX3Ho9bjEqrLyyCuJx7Y2Jn9xcv/l/Rs8ArlolXBnvctLVWUOy4Lmcty5u2KVsQsux0Rrzq/m'
        b'fJRX/JsyqnNlVrGoKKf4okxbDM7zdylizurEKbFcqv6GoMC0pC2oJd00R2BIE8yZ1Jz+wLB04Fc2imTnG99v85j0OxCx1fMV++MizrCQrOEC1KJWa4xAUa5SHE44CG6P'
        b'4gBX2MCzQMfoYS+y6C50GONtN9qF9qE9XHQGdgLeZApeDl8t4g1wwkRyWwz1NKEJhwnr6+u/c0ssk9fUyaqFZazql9DrKsoUSQNWjF4vLC1WyOpG5TmkcQNOvqkHQ2kU'
        b'cHBW0c0TGuv21Kln79qi2vKOm1Dvn9A3z+A/zeA23eg2Xe8w3eTmpS5trdK7RWgUejepVqGaaXLxUsta8lXpJhf3wxmtGWqZZppmtmba0Qqtq3aNzlFLX/DUzeuL6Zvd'
        b'J+1drPdJMbikGl1SMbyzsHmqxtXgHGp0DtXbhH5B+FJOGFNkNsBfW1yllA2YFxbKldWFhQPWhYUlVbLiamUtLnkGAYSFi4QEBXI7UmiPk9ELDSRAtWShZKXTKYpyHgK/'
        b'lAzauasqGiv3VNZbD3H4lIvJ2kk1sXHynsmDPPv67K2523Prc00W9iYLZ5X1N0N8wHcYW1qfz/6jCTcetIwAnXaTuTNKOOOphY0EhEMsKaMYqCeKgTOOhuZajiPquIT7'
        b'E+HnbOaOKIZx654ohvJnFcOTiY1SDGZ5SmJt4pBqGdqPlZt4M9wOxHC7hBFZdATeQjfRfuwjRcFLEhA1C7KyvAXehi+yEgtPpQEJOgy3V+Sf+RuHTsG1J75aR2Tx5P4K'
        b'ihvfDNWwd0/j1uIJzjkdu8/tv3zltGrCjuv7z1m9VrLiA95Hy1+ymIss5ji/1v97DhhYaJ1Z0CeiGHFZhXbAxogsMVIFoEOZOXl8YA0vc9AxOdwq4j7LKcSNe8wmA9Ys'
        b'h5RV1RQr6kbfMIIxaUQw5lLA1fNwbmuuJlBDG1wijC4RmHXtXTCj2AaZBJj326yb+SZnz+aJ6gktSQeS9Db+coennCwnymuAXypbUaGQEyzKncfhXoZ9We4lmnPMdBjr'
        b's4ZhXzKhOZh/PQmb/nzyL+XfQ5aR4IJdApdRrcYUJyqu7CYXzOpfbVpknaN0xYUZifA4DW/CO4r4aB7grADoTGE+Ay6xd6Emxd6iQHT/6oV2bwQr3Qi/nIdnkJpOgzsx'
        b'PAU4MoDO+Sxg4LsWuFGJdT9wQC2Gn0JbMvABqNuShi9wMDQXcFYC1In57QAD/9t0Dypl8w+YrP2bFkosLBm2EweU0tieqBQTyWyq8XiepQx0ndKLSpPM4IMUDF22aznT'
        b'O+zyyaLh1kIMzQGcGtL7VXiOgf+S70NlmPVhJwHDhxlFSuycAB+4F92kOXA36p1AZg+3AdSDzk5gWiyU+FE5bhcwQfs3qVdXrmbQw0uspP2XEHA+Bt8OUC+6PYkB13j4'
        b'U7NWTcGqt3+TaV6VggGHl4rW0guz5UzvNcRmtMCDDHhDSgA1t/qwOUb+JrXDuULGyJag/StQT3CMMoasFptgPJt98CjTAEqDqYV5wWYY/ZvUCzZWMAt2DF2GepToCG6A'
        b'F4xNLJ6PmkXQ4eQQaunyWRRG/6aFwV9FMfNB9UtradypjpaSEbYA1JWczoDXTBNRRdOWY3HppxemlGxi8APPwtPzUQ/sgLfwCJhgsB2gPm4c06JKHE6VrlqIc3dpU/wn'
        b'+UoP0uL0YqTFA3RLcANz3OAIQNcxi3QwTTgJkVT5tETs1/XTAp/uPGZOrvAwbEM9ZZtoGyu8CHSFiluzgQHfnRJFVc1vxzTGI9D6aawjcgQeMbdG7bFyhkHhGYCuwQPr'
        b'mQYHRTFU7Yx52IT20+qlgqUsU/TMQxrryOfQ5QmkAXbCuajLh2UKaSylWKvETHGXFljN5jEDTEGXUIs1VMG9VrGEbOgQZWkPVSy7X0HdYdZ5MnSVoRDaQVFoj4BZxpbZ'
        b'8AqdjvHfs86OLOMkFUFnMR2i82vn0LAHNlnaIh3p8A4V7wEvMHVx6NhSa9gEu9Yo0VWMIHSZCjaDhxjeTw51oFEf3GctV5BWasp3+TKmkQ06hI7Qc+AxBbpmTaqaqAjU'
        b'sYr1uTrg1ioaXRLa2WJscvnU1NoFjJPGCaJp2JloZ2tHAa4llQIPCxkaY//sMrpEw+0BdrZryJr6KAlexS12vUfhQU/rJHjOthbu4QFuIJWCrtewrNTLsaTRrXVyRhRq'
        b'Abroj+dNahwwQW/Q8HilIj7ODHDKsEqI9WYx0boK12BHCLMfnxW3btgWyNZdW4w66RQ8mcuox55gsIuKS1zGzvH2ZriTnoX9qKsjdecpKTyzSWTPkNFz5gRqfZ0TB0sq'
        b'vXB+/3NM4TreRGojkZeiu5gXVnowhdzsyVR9GeRhIaXVOXNtmML0kARqe9kiPPG79MLqOg5TeKhwKqVa9Y0Zlk/axPtwHlOYXJhE7bGbyAOzMEPaJJYwhV/UplLNy29w'
        b'sWDS6tUfsMJRmjmdOmD2Ww6IxpxVuzmW5ef56ZTa7R9EI9Lqgo8tmMLLc2dSR30/4oJaPM9Ff2Sl0Wl6BqXhhOBcf+VCuaUvU/h2UA6l9VxrhqWnUj01iGVh68p86oIv'
        b'NnMpdytNubCQKUxJnUXpkpQ8LAeVapulfqzGLCugeqtn8TGzV5rmrk1mheM8qocXaKnI2orwhQ3mixbUyZBxGtoG71ij07BRbmeLWcmRmpppyQr5VrQV+7U9S+B+dG0d'
        b'NsSEpSNKsYwQQrqjKyuxzl6LemjUS7jzABWwCt4U8ZhZPF/2EnV0yk2slu6uM+XKpzKFRzxfpjSBodi56K8RBJxeyhSarF+lOgKDcOHdGkHe56xKmGL5GqWdwqEwDmoW'
        b'umq9xmzP+I/dnc1EF/BHdtE8ZgcNyvj/wb3yT54ymIGfemIheUo/fFeObtNwdz7ai7cIjZm5EtSIdxHw+ZVuRbxQdFjCLHvRcm7eDA6zdbb5u40TuzWSz7OoWkwJicdh'
        b'84NZGVAyO479aCdWGjvR2eyobLQ3P5MPLNB2zgZXrHAIwS1XF2FV1Es2axR6HnYuApj8DgxZ8d7uUHVEGN7LqKKw62WzUurEtUd74G5Gf0wOjoc92KFMALAdtiegU2ib'
        b'nDEDJJmcy188m8ts2G06qjzZwh2zzXgdHOYhQM4t50TAOph3pqBt0mhiGucB2AqK0QuZSryjB8vl8Go2s0/aR56XYP17LRvui8qEF8MoIFTw7aAa3WS70EENbJPGYUXo'
        b'AuABsGILalSSZ1mxaCu8HIF39GhPLt7X7o7KFM/iAWcRF+3BQzHLz0e3UacU70fxKG3MnhTz/wusKFxKRrelsJuHjVgIgCdAFd7zalk1eC0H7pVKMYwW3QLwOFiJTdpp'
        b'Bi04czZCKjUD9kUAnsQe7A0eM8nidHRUGo+bnkQHAVQDLB12zEMh2ByCLmZnkfnlob1wq4CQyK6WOwkbwbOsCwZbMYri8TwuwUYA24AsFO5l9OD6XM/sHNwqCjVFUMB6'
        b'Meoox2pyXpiIw8wlOzlcGs/BrvpRTCNQBuuRjpnLEpeN0ngzgJlCjc0nWInRpGHtuw7u9ES7swm+6r35gOdLwRdQWxkzjQnY2DVL4ymAbjgA3GU5vID78yTouJWUFEEI'
        b'gxrz4EUesJmaOpFrj7u/wdJHlWcuhVcJbjCzaEBVEtzBMthphwVodw5eO2bAZi7gohcpeGQu5sw8Mpltq6CWzsnMzCXP1Z48mgiTiMJzJSIxxwqelmFsn4EdYajDLgye'
        b'c4sQwQOoI8IFHnBzRR3u8CyWm10uDpg7mgRV3/z444/cHN7GMPY5UlUsZzZg6dyYPDUiT5yBOtA5HuClUFgHHlwjcmFQiE5XmtG2cmW0GdFqx6nASHOmEQ/1JKEeO7kS'
        b'9W0hNVcp0TJ0icFTNDwAz6Ie3MiTT6pepCICp7MmsgO2LadJo3MurCL0sxayxq4JbUun1yitsAOqJY7nTUqYjdmbIcpudB7tpdHVdai3Zimf8Vj8oXo+U+mAti7FHgbq'
        b'tZ0Ab1GMvxALL2AOZrxNLTwGrO2s4T7UVYo19mJqSaE5Q5LlBXJaYbVOALXEZbpNec9Hl5mJzMXC3EyquEhHhtpKCeF1pGbWXLMIz65HIcfeQFcocf5epLzcpjNVM9fD'
        b'Nhp1K8wAVZCC5YFIE+pmJlECt22wtrC1ikW7sL2dSGXATtTLzH023lhi90i5xgZ1WpK5t1OhRDyYGa6EW2GXtZ2NJb0UN5tCZaKtPkzFLG97bPPldmJ0Ai/Jjpq4BDWw'
        b'q9UlTcE1qNvWPwHXBFCpteg2s6gVsBv7R2vW2FBwL0HuVcoXdcFdDIEr0V572kquLOcRWrVitNuwXHEcO0Lt1rgGHcaeLteJio5BzzNPq1ajW5PQfqy4I4GFa6Q13MaS'
        b'sCspDe62t1qztmQ9hfmji8Ju3B1vZpCwmDyyFHg+amQtfasrPrH7jKI/wOaq+6XiY3On5nulOrxz6WZP02VLf7Ntzv0/UI76EB/b3oo/vfI7YXZqQrZFyzsSl9BlqdvC'
        b'yrsGT2n+YD405Zupr3227JMjr7s5hv7+3U09X7x75PeTC2dOjKz0646IeXFijnQwtmrTV1/HvP3ZHenrqZGzHIRRlc8lnnpx3h3r3qKTf6WS879454KtIfGtVb9aq/zV'
        b'lnc2LE28x3+Z+8f8Lxbe+PDbA/2q/D0/nFJYNU3bbppw9hOTtV33m14nN/hva3u+bNr+73Q5ppqkd6UFp2aWt2inXfiLLONiUcVHG89cPvTBndX/+GvgvcOW7675ZsG9'
        b'm7/TQtcLOceOLPJ66Be+UfXxG0755lcDr2zuLFrW+uavFiWl7t2XtuX1D08E/NA4OLXhxxkb/3HB+Nb6hnfF738d8W5X0aJXk7fdOpL3oUd+taM5t+FO+bzt9269HEn3'
        b'Hnnt7xOWhL8wy27jmx8FvLT0t2fdVDetPrnW0nvzQ7N30GF6zfITczZcfs2Ulpc2+dSGv226tq3NPPRq4FuHzNfm8F67d+Dj5qZ9OS/sD7B781r25C1ZU07MKEoPWPa7'
        b'2GVvZM1cf8Ln4R8+XWz7lykXc47+7cNJn24wmDonnVtw1O+tJUvTeszCh3vM0l/+Mb/Ja2dXZUDyo4Xt97vzf+uWqfvI8WLd1eMTfpzz3NyKZM73d9u3vAs+enS6Wx8n'
        b'shgmRgluhwdXot2ReViZoX2RWG1jgahHO7Hi9kA7h70xiKM7bImQZEaGiyQYAjUCUEALhLzlcB9sHiYKF7YvgE+eIsLLU7jsQ0QHeHmY8K7ZtM0REqwzGyOzsPYBZnAv'
        b'RzzJm2mZi06jXngLnsqODMtATdkUsICdnA01cDfTEt5cC69nZ+aG58JT8JA5MONxLDKdh4md8kMtkREZkeG4V9SIVfE+hwAucJ7CRUfc0K1hRr1dRmdWZueLiSj3LltL'
        b'pWILvVNk+8xzmv9+QpNEOPKrr3/yjMeJfY6ikBdX08XsQVfdOGXME5927sijUA7wCB4C2ZTtAuoR+6eZZ3L3UucY3UU45yJQe+tdQkz+wZriDnetozZG69zh3cxrXthi'
        b'R8AyDmx+6C5+4C42uEcZ3aOGQIxj0mBweHOaWtCSZwohGY+W/JZ8k6uHOuzA8oeukgeuEi1tcJUaXaVDQIyhfQM0MUdXaoo1KzQrjlbiBo4tM0e1HDID3r4nJrZP1MS1'
        b'TT06tTnN5OmrXnM0tHm6ycvvREJ7gqakLfloMp5YrDbW6CXBAP54RUGuSY9IouabhMG46zWaFR2W7A0zEnPjJdSktU9VTzVJJ6nTNL4G72i9d7TJJ0BT2r5MvcwUPQGX'
        b'ehm8xXpvsck3UKNoX61ereP3uXTb6mxNQSLt3BdyNbk6WZ+ie7VutclbqPE4mv/QO/aBd6xugsF7stF7sp65nnYZFYe79DR4R+q9I5+WSqS41KMtX51Pyqr0PrH4Iv25'
        b'Hc156B31wDtKxzd4xxu94/XM9aTloCRGW6ILPrfqwqrRPbC9RkTjMre2HHUOLjuxrH1ZW+HRwiFg75E0GB6Fq1zbstXZQ3bAJ/BETnvOEKDCUynT9IxHXCo8EzMD5ZNF'
        b'DTPpEJMOBoVqg09m64INQRPV6Sa/QE3m0S1DgOuTZBIGaRZ12Os4eqEUX0ahVKc0CBPZOwNzDbIgD4XxD4TxpHaqUThVL5yKM4N+/pif5rfYDHH4nk7NZkM2IDC02X4E'
        b'nUPAzDGJSTBhwyIv2Z2309GGsCnGsCkGl+DmdLVUwze5ew4BHqa1kvmjddWFaP20fgStPPX8ozaaeQZBhAmv2V5tb/IIw8txTTIJvJmqQr1gAr6Mggl9LgbBVPbOIJjw'
        b'jcnZXW15IFkfkqB3JtdgZEq/S3/FPT9j5GzMm24HcjTuBhcRvghviw4U6sOS9K7kwnypMTua+NAr4oFXhHaGwUtq9JKSQRdQpqj0/tL7k+/VGKPmj8xtvkEQ+e3QAg4j'
        b'eyOSOOqZqsWAzWjhHe+p6rPqgdkGjdYMcnIoMJ4qmE7AyVkde1jA+S8ftv6bHrsethSDi3ZTuCKK9fD2w8u52VCHdJmRmdgFBdgLxg5K45jNrO3jHeNenBy0HdnMkuNg'
        b'8NMD4TLbJ5tb3n/i/PHL1Xh6VsJRv1kE+bSweGzEARPGsKFWJsydOzkuWlgjZzKxkjFNx9xkKoRymUIpryZ9VVXQCtLFiuLqSmFxSUmNslohpBXFCtlqWbWCFq4rrygp'
        b'FxbLZbhNrVxG40JZ6ZjuimmhklYWVwlLKxiWKJZXyGiJMLWKrhEWV1UJ56TPShWWVciqSmmmH9l6zD8luBcCUzWmK+YQi4UqqaleK5NjKBJooayuKKkpleF5ySuqV9K/'
        b'sLbUp7PYICzHUyMRHmU1VVU163BL0oGyBC9dlvDzXYgxDktl8kK5rEwml1WXyBJGxhWGpSrL8NxX0vRIXZ3omZY/bYPpUVSUV1MtKyoShk2T1SlX/mxjQgKyzKfjTcMl'
        b'VbIKRV1xedWz0CO0egqcXVOtqKlWrl4tkz8Li0tXyOSj10GTiYwPvKK4qhivoLCmVladwKATN6guK8aIp4urSmvGwo9MZjU7lzRZScVqzAp4pQRR44GWKOUEQxuezmYB'
        b'3mPLldXjQpPzyAQmxX0qS8oxGI3vlKt/btYlVTW07PG006tL/xdMeUVNTaWsdGTOY/hlPpYHhayaWYNwpWwF7k3x//daqmsU/8RS1tbIV2L9Iq/8/3Q1tHJ1YYlcVlqh'
        b'oMdbyxwiN8KZSgVdUi6vKMPLEkaxWldYU1214T+6phElUFHNSClRFMKRpcmqx1sWc7D6C6uaJqsqphVM8/8dixrtjCQ8MWejbdETfVdbQyue7WCEM2R0ibyiljT5Oc1N'
        b'aC2rWPEzMyaWS1H8mLkWYMuFh6qq+hkOGxn0KTuOHevnWfO/jXe5DFtRLHQJQqxlMGQBulVSuYIdYDx4oovw4gsrZaNI9XhCGAVV6BZNy6p+qakCG/ifQeJIPwRi/Mn+'
        b'xOJmK6tLZdXjW8yRYbGNHMdWjx0Yw/xSHyvXjrW7Mwm1UUeZgsaaqgw7MaR6vIa1ckwArPOKxx931ki1rFqcJ5f83OzHjP2TeY9v/0cY4RkfYEzjn/UH2LYVeOjxG2ZO'
        b'S837ebYrrJFXrKyoJiz1Ux2SP1K3gmFILMDCGXLZ6tJ1Pyvro3v+JxiaBf9vKpPyYmxtxlV5M2Ur0C0s1uPohP/AxIgYMHJG9NyYec3FNb8sbNXFq2VPtd2IXywMy8PF'
        b'4/KpUl7L+EU/aTFfJl8nqy4lYlm3TlZSOV5rWlZbnDDascYdjPLqx2mxpLp6WYJwXnVldc266qded+nofUBxaSkuWFehKCdOeoWceKkyeUWJsKL0lzz8BLwHLV5N1Cae'
        b'09zyZ+KvxzZMGNnnJOB9wXiWYSz0mNNEO/Czkbe/mcsFzUkkqrvIZvFsPnsSZ1PGB/XxLkw87bGpcwF7crV1wlzYwyEBDydQH5gCj7OBI29MNQfaOT7k2K7KVxjKHttB'
        b'NTpuQc7NQEIIc2qmRV1Kf3w7SYBUEaIstCciL0fCPiiMMKtE+4C/H98TvgDPiGyYsOkstK0W7Y7KyhTDXVFZudniLNSUnccHMahpJtprFgFb4FEleRiKtmVtiBgBkMoI'
        b'iBM8zsWb5X2ojz1AOwl3zHt8gKZxZs84mQO0ZqhhzqfEC6cyx2SoB3Y+PirjoK6JqJs9vurMhifR7pkJEagpN0vMARboOgfugo1mygBSfRJezyP9Z6I92XmwCe2LykBN'
        b'3EXwKvBz4iH1TCdmQXjLfhaeGwWXz5uDh2wkR6dBEfxEdAMdYg42OenrR0OxR5x5uRQQLULH4C0+bPeBjQwu160SjRkXbXchh5gYNKiIn4JOmjFQ8PxsuCdCEo7uoCbc'
        b'nyQrFzVGisyAFzrCg6eEUMti6Vgy0kVIGJA02JOZi3YRIHdXXnS6kDktXZPj/xPCoe7NDOHyZjNBgrOl6LQ0lkeOhoMg5jOFOxvXfgGeVj6mEdy26CmR1qOtDG8Foe2+'
        b'0lg+nsb1hfAIKA+FTSzPtcLbK9B+cwCirSaBaKiDxxmiwytIkzpC01p0+ylN/dAxhmZ4VWkMTWmM4ackTUbHRRzmNCgEXS+Xwu5as7WoAVA5AHaJ4C6WdQ/AxkhchbN5'
        b'HHgcVMK+fLbPOxxMsN1u0mf44Jy5yIw5EzJHzVAlldZyxfAKoLIBvIi6oIoZLjlgnlSKdHx0KwRQBQD2onPwGjOcPQUPSaVyLtprB6h8AC/ZwlY2cKkXnpyPG3XzneAN'
        b'QM0H8CrsgGdZvBwJQl1SKQXAVLgHvgAqOezhF2oInCWVYjyiXfAYPAWqFqJ2Rkj/zncHKu+FREg3/jmyCChJnGzaJnMad5G+fi1IR1sXMYB7eQ5gEm8mALVFVd8JMoGI'
        b'y0rZVbA5G3VgLtuDmliEWiA1Bx7cBA8ycQQ1EtiSLRGHZ81G9VhSYRcP2M/nVsHbcB97tnkdNqMXszMjMaF4Zs/xKHgiwgbTgjku3wGvmBG8wZtOLN7gCXiTrTqOV72d'
        b'QR08oGBRtyCd4Wt0yjH5p2K3XMpKHdK5jFC6ZBY8TBAM22ELi+EM1Mt23lkFGxkMS9A2FsOoZSMjrS5QBS+MFsNo1DJGWhthG4vx4/B5mqHEAnSFUAIdqVOGkooedDvq'
        b'ZwR5uQsjx5i7DzInhrZ+GxiqwTM5hGjhS5lAjxrbrDHri7QeJd0b1zCMELo8XCrFAueITsAToBwdQ6eUgYyAyFF9dibqsxfnSbAoh7ESywVesIEHT2OROc8y2eHZz0Wg'
        b'I3wSli7O5AFLcw7cm8cGkaRY2YEPkhLJ6xU2pbUbAYPNGrjHdYSKsAueJ3RcnsSwiDO8BNuzN1Q+yyHoFNzGhgF1oFZ5RJY4W4xu+ITnkbdb7FdyZdb+DMbFLmw8x97l'
        b'j0M6siHBFwkY8MrhEVyVMvqxHLWi7aMiP55EfaB2azbwow/2MEiItoSHWSUB9462IeGwbWMJH3Ymov3M89U6eBbeyUb7LcdEwKRMZ9QeauUkj4oRcZVFZY7EiMAD6Da7'
        b'sG3oZBAbqMAF3EkFTJgC5pejyjDSQXsFEzLBYgU2YkZFu3LIyVw2QUEsPDwpxSyzZhqrY07nRuJJZETCQ0FZ+WIzYJ3NwSx2FLYzIyXCK1uYSApLPMDjYAquvZ8CiynT'
        b'/AV4zI8N0CAEakJ3SIQGZus9jJCiNqzcupmQnduw9XHYDtcedk5RChnVJ4PdT2KLJCGPo4uY0KJudL3Ozm6DtTV2AeaIA8Ecy3VYwhwYLY1ucxlNEhQC0gPY2FS0fwra'
        b'Zy3HHgfciy6icwAewiJxnBWaNtiGmthwcnQIngRiZWYVebz/Om0JFloLmbd7PmADjNGlgE1oPzpsTiy5CO4DheuxjndjjYMK7oc90VwAquZCLebN6/CIcgFjzdChWTQm'
        b'CWrKnD0LdkfPKUAq5v0diTgMrzt8JGhkTh1qJqKhipyfQRbN4HZ2RiSpxAKTPW8WauJhxf+cI2xajg4zQSLmIXygCnRkYpfmbjIHDJdYYv39BHGVkjGI2+OI8USWXQbr'
        b'4S3YE1drJiwC1Gys52LZYAJZKVSTcgr2bGR0XBdWljuUUrL8W0Ez0X6oysT8dAgdgKq1OGnCVudiPDxbCLv4sHtFgWIFvDKBwlQ3WxQFt7Por4fb1rF9tilH+jyOtmE+'
        b'IXyUj3ajU9lsYBDamUEBs0JOOFbDL7Bc1OukYHS5KybdKF1+qZwRdN4URTZ8EV16VtBhPWJjJrbIHJlVVgF2lWh3OMNesbAjPELiiXrHc0R8USvjLJQEFI24IagFHh/t'
        b'h6CTlIgNlsqD51CLNH4NtygXUFlkaTscGAcEXrGFx6VxmOlys7EDIlM4M/CVLqhDGreWskkAVArAjfvgFYa57FFLNp4q0oF12NITC9AdKxJRLAZ12HrvwbUxYB68CKgZ'
        b'AB6HZ7OUqURZmSutUVMJVqO7iUsQhfbNQTpbeDkuZlbGY64rEM8veJaTsCY6YYXareKY2c4rg+dgJ57sRmw6roKN9AY27Okm1EyAnfHkVYYudApw3EjY/C1sEQlybVAv'
        b'ZqNObC02I20cTo5WMy9pYf7bji7R5M2iqIIwchBPdCNS2SwYM4MFYnNMqWt+ygTS5lwW1zovFzWJ54+IB2pckJG1HB6elzGXXRA8NwupcsWSvJx8PoBnkc4K7hDD/SMR'
        b'ZOgs2gk17GseEzOBpHgkoqYaXlmLufYiLveGN0jkXCeW4Vu4FVFDwWvFDHuhy3jKo/jrAmph1dQOeCcgGx2TP8thTtWMuDjYowYS1HTVlgKcQMxf16i4BRLWPKUE0uhq'
        b'rb0Z4IiwmWukQmC9ExN3WJEeOoVP87CtNO9ffNHt1eol6Yqyz97aF5TXHpd55F7Fg5Qjwy2cHdM0idNeLXnZrEPxxqkz2tb0S51xu8oWCi9Hd28P3m5av2Zi6ZytN4q5'
        b'laZH1kPWG4H1b6a2Vb7n8d5bZ7RXNybS79LLpe893FJ0rG276ya7R1+X674vKzssMstZ83fLwVc+fK2q5/i6jwv/YvVm28Hqv947mWLZknlv3r387K+bAw+tXPiXrIl/'
        b'uDBYMjA9yfxe6g15x1vvv9MZFrrrz/0x4uGj37j/Wblrw90Jt99OTfqLqJD/wPxvvn/4U2Xrrys/+EfFy3dPeNWVm/6Q031P3B3wrcVKUDV881XhBw9d/jb5Yr6hTnvR'
        b'PDblpsHt2OkvYwrC27vt5nl8crlPtK31i3m5r04J+NJs1ZI/uxqv/EbW3fzp+wZoWl62bmnJrx2nbF0Y987kHT9MrN8k3nk5xcbvs6LP70+XXr0v5TfdcvmofeaF+nOJ'
        b'bw575A37vPLScP9Zj88zezfP/ORlau38ki3pnxx1vLkh91tL0dm4XwW+UpGb2dxdm/bho2+u/dYjkvP9XtT6VfP0nren/3lJyGdS3gKLLqfE7OiAvhlD/OejnC44XnBO'
        b'nDmUeFf5vJfobdmH7pLhY37XrQz739fvvhfxyvXfT3z00SCv6+ClM227t7XQLzsc+t03KdPTLyZ8dkj+ucfFcwF7Sg+8+o9fnZoU8GurNxYd6No5vLD+e/7D20szZbLg'
        b'v5kvHSix+njx/OOfdqzOny9fHFG2KXxP/Xn/F7/as1js0Xf0y+MXKip/nP7xn06vuLjv4asJv/+j+5tGePB8Z31dj6Rz/ns7anfGtsy/e2Y23//CqlfOeFy6F/U5p2vh'
        b'F/f8feKOGAVdbw6Xvpz7cmubYEB6+Uv3rwazE24sKShKLgj6Y0ziGy63Io9x3+vSX+qrsF7+8sVLSW80FN1rSPpuk/lQeN6BqCm7M2cJtj6c9Yqqy3Pmj3mvPAqK/LP7'
        b'GdtO9ErHhSWtny9+6WbFh8N/WGwY3vHwS+9N039tOmvZd7DswhsdXx7pzfvrj0sE3HfbX3pDuTh3lt27h15UfKaCid9kDb8tef/U7Tl10jslWb/yuu/hKn+xUn71bPbk'
        b'93oUZ5ZXvXph1dXdnTvL/7bv6N0dXusHmv664Xcro4KGP1oyZ+X3jb6HHk54lxOwbkHuwRlv3fj+T3daeuTeeQ5ff6B45Bc2e+retIKIP9/gvBmU8G5E+uk3roKKQ+//'
        b'eftfjjynSvC1Ha7qWfL1vMAV8mnxctp23czfTd7C1b785u9dvyraXL7h4K96Ej/tOv35UlPbhvtfHfutaXpSQu6Xr95v7zj048TvOTdrnZLuK4st/vq733z8burfG65/'
        b'nWnx8fZ9zy3/euXb4vfP/3rbvgKb15f8/T3377+9/pmv0ePmp2+7Db/46MaWFa+X9iipb08keS272Tr71eT8LtNf/z6j7ITug8+2JL1/bOftbpHdMNlD2GKbdXYkFgpd'
        b'dMF6kmhK7Ha5w6u8jGS0e5go5FS877odMR1dD5eIsDnC1n4RByuXhhnMS2jLkQY2MuFY88ueBGSRcKxVomHWO8RbmK7Hg2y1Hwm4Wr1gmI2NXczNRq3wxJh4K3QenRkm'
        b'ewAFbn2OjQaDO+CxJxFh2DLAk0jHRIw5IG3wk8grvCFlHX0m9Aqdfm6YsWUv2G+IoAPyciOz0F6Ax7jOWQd3bWRiumQ1qDEbu6RR4knwRQDM1nEksDuUCTR7Dt1an41n'
        b'JZLAM8TdZpZmH81dGYSnx2wfdmJbdGfEkfB3Zv2I5Bp2zEtrrCIYhKGDG3G/8AJH6gN3McFicDfeD+5n3tzzQdtHvbmHVX8XA8Gh0A7sL+7Jxh7Z0vW1jFnjANdEHtcB'
        b'NYuE/89BY//mhCb+zjiPVetH/8a8irhaMTkuum70DROY5mPJBqZVmwEXweHk1mSDc5DROUiVZnJ1V80wuQhU6SYPH1WWyc1dNdMk8B4C5RzbAuoR+6eZZ3L2aU5Ql2rS'
        b'Dc7hRufwIUA5SkxeoepELc/gJTZ6iZvTTO5eh59rfa5l04FNGN7TX5PaFtFsjksJsI/Jxdvk7E5G1kjZ13UfgWKOYwFlCgk/u+qFVTpnXbEhZJIxZFJLfnNqs1ItG3T3'
        b'1vBaNzVvMnkJhwDHI8bkLdF7S7RK3XJjVJrBO93ona73Tjd5B5zIbc/VBhu8o41MpNlgVJxJJDaFRZpCI3DvpshokzjGJIklaUSUKVxiipQMedj6ew4BnKj5bfwhb+Dp'
        b'pwlq91H7mMSxar660iAIx5fJw3ek1MtXE6xOVCeaps38dQSMuF9imFZgnFZg8E5Wp2vCDd5iPK1FhqhkfOHhcZnI4B2JL9KDWO8RhS8SKcVXl7fZt9njUn1Alt6DXIMh'
        b'MZpKXXAfp4/bx+0N75P1p94qvx94o8YQkmcMyTOFibXFOo629IK1KUiiycLjzNat0c25UGcISjAGJQyZ88hCeGQhQ1bA21+Tp/eKxZcpbjKehsTgHYMvEr1WrfeJw5dp'
        b'QgIujzJ4x+LraVRb/BR1uj4Al0nx9bT4CfC3I7ho8xniuAk9Td4ibdwQF+cGvYM0qzSrdK66NX2OOrrX0xCSaAxJHOLjuiEz4BOoSRsyJ3kL4BOsKR2yJHkr4BOq5Q1Z'
        b'k7wd8AnHfdmTvAPwidCmDTmSvBPwCdO6DDmTvAvwEWtLh1xJ3o3tx53kBSyMB8l7sn16kbw38AnRKIZ8SN6XnYMfyQuBj0SrGPIn+QAWJpDkg9h8MMmHgOBQU6jIFB45'
        b'FEHuweNEzRuSEAQ7Hp3EBqGxnD8E+B4hpogJ2gSdrC+1r7hveu+q/gn3He/H3ne5N8UQn2eIyDdG5LNBg6agEHW6On0wIkpncSHpcVmwOt0UGaMLvpDTN/1BZLKap15s'
        b'EIQxsZHaLGPoRH3o1L5Ufei0fkeD73Q1F6PVP0Qj007XVBiF0bpsvTBZzTf5BWnmHK176BfzwC/G4Cc1+kmJ1IQPBgRrqZOh6ukkRrNEU6op7bDG0L5+ai4ZYPrRVQ99'
        b'ox/4Rht8Y42+sVhWPcLxOsgapj+In6mPn2l63MEQF+Ax/usGg2HiS9bnrXXpfYG9Wf2UIWyaMWxam63aTMM3ieK0Xrr5ffMMoulG0XS80IVtdiaJVJeqK9ZNv7AKFywz'
        b'CCIG46dgTE7rm9Zb8TA+80F85v0gQ3y+MT7/EZfyiFO7YPn0CNdON3kL9f4xhI0FPupqo0D8UBD3QBCnm2sQJBgFCXrmGiXDwVqXB15ivZfYFBCLeR1PPS6TMmUX4F7j'
        b'5pDQzMC5JDQTpyQ0cy41ONKtdoVREKOLNAqSHwpmPBDM6FcaBLlGQa6eucgAEr1HNL4GvX1PZLZn6kNS+rE6yjB6Z6ipweAwzRyt4yX38+46x3OeFzxPFnYUmsJEl8zP'
        b'm+uoc1YXrEyMBvC/Ftod2ud/OZzRAcob1YaQXGNI7k/lO709SZ1EQmvTNWI2tHYwdiK+weomSu8dxeiWqXoPcg0KvMnswvQe4fjCd4O+Er2vBK8uOsE0dVr/TH1iDl58'
        b'dC5ZvF8eWTxOCUnzqEH/kOaslqxBD98hICJ6Gqv3La1bNLTBPcLoHoF5y9Vf53LNp9unT2mISTfGpDNF911+6/OKj37BYkPmEmPmEqbsDwKhyd2HhGribpgZ6KNm3Hc3'
        b'RM0y+M42+s7WC2abPMP1+IrIMXjmGj1z9S65JPxzid41DF8mlxC9S4hGqV1uDE00uEw1ukzVu0w1ubDv1AcbXMKMLmF6lzDMD83pJv9gZt5eQo2v0Sv6l0cdAdI5Gb3i'
        b'iAXz18x94C4yuItIEHRye7JWavCKMnpFDQEXj0m6tGtZ3Vl99OX83vz+4gdxM/VxM01BYWezXsjS0ifzO/IfBk15EDSlL60/0BA0wxg042FQzoOgnPtzDEGzjUGzsYwH'
        b'h2vmaWO0JY+Di/v8DcGJxuDEIWDnwyYaaojH88+hTLET+6jesL70fv/+4rvBt3K0wZo0Tdo374TGYJRigNGpKXyiVqyflIEvU1hyf6ghLBNTdXI2oSdOMW0jckg+gjSg'
        b'gnHKJc2++eYbrJRj4nXFfZSupNfKJJmsrewL7qf6Of2cWyKDJM0oSRvic0UBQwAnGj6GDgrTxr+QpEkyJU3XpOlFCYagKfqgKaZgkXb+C8s1y7EZ0aRpPU7mf/PIhyxJ'
        b'SBrYGgPjiUBNNsVP0vA0ywxCKYlC9tEz/Gr0jtLFGbwnsncG5jJ5YM33wCNC7xFBAoqXGgXhDwUxD7AQBhkEE42CiXrBRJwZHJ+qg+TLChzbYJNDgN4hQDNB62sMnGRw'
        b'mGx0mKx3mGxycDts22qrlhkcgowOQXqHoEFnD1UuTb639IaP87wY3hsxAfOdzdk4YYcBHjlV/Sfig/9pl4486iwaz4WTx4Onn21gXLdWAv8CGAkkLuZRlBOJEv5XJv+y'
        b'gGPy5aMTlhPAFbtULnfMsfHj8OIvyDO0w0BGPnoGFnNKqcXcUs4cYFkm4g44MCfWTDSvPF0ur5F/58eeYTPYkI8E58pKhcXVQhmpl+SJeAMWhYXk0L+wcMCqsJD9KhnO'
        b'2xQWrlEWV43UmBcWltaUFBYy9GQjwBlkTybI/smw+/BkabKdqX/yb9AmRv/4Ytoz5wzoFjqfa22HrimsLfGmKU8sH9lbRKETZpV+fHgCHRZRMyrecLoP6OdJrwucNrVk'
        b'5qNohx2fTsrcP21d+asFV7sPbHrv6yv1fWv+qBp22do8KSV4VrBEW3C0Nk1lvaBOlNxqyc8KF7YmT/nqyETpV3Pefv/qCuslVyYs2VJmf+Zll/fTfE695tGp124edIdH'
        b'LuV3np21+MW9C48VbAzfl9H2ecTJH1z/UnHy26+TNsl3/M3npR9ev+A+YYXmg4tNr4sCfpz14/2FX97c5ZL2uv2Z9/50/Ihy8tI/xe6Xvd0ZvUy/Oc3sHy1fJl374/Z3'
        b'aj0OzPa4xvPM2tn5x1lmpfoCh/C2rrW/cZjx55bAXYKYvbzLlq/fCyq4F7dYdbE88Grg9E9SQi9bv3PPt7Tx9geBX5XUq5FwjQW657jH6dfReUf7g85EN3m8tsLui4X9'
        b'AYd0e1wvrLD9OKplwWfhpv6Qq7qmY+5vuBa0PL/K/lX16eLDqx4e472Tsm2/wlP8l9W/fe/i8HdVB/wfzNQWzltVcDi3e9GZiw6fB5/Kac/69I2NW9a9Rv9G+slhgZ1V'
        b'3ac7Xx3Oc3303IFX7+5t2/CV3Wux62tOrRXxhl3Y56INOWh3DgWozIJJAO1djxqZDTDaD9sD2S8rwa3omvLxZpF8WWlB8TChugcmq846nDzuxjv8kQ8wnZ6AofxgDw9d'
        b'gjfgZWbfOcctlYYXM/LET07MQLojauZCnTO6I/Jg1YHFLyb/vk0leZwgTGF+9T/5sbtJLFlVNcWlhYV1T3LMPlLMZb4h8w37HZlIYOs6xDO3dDfZO6no5tjGdXvWqf13'
        b'bVRtVNNqWhOrKe6Y0FZ3tE47u32LeosuCP+T9/n3Kvtm966/LOmV9Kf1p913uptxL+NBbI4+Nucdgac6Vl18dEKb5VFLTZZBING5GwST9Il5Bvc8fcFc/bz5xoIFD9wX'
        b'6N0XvOMm1Di1VB+oxhoce6aChRR2j5xcmlMPuKqmqaZ9M2ROWWLvzsmvWXzaRi+eYRDONApnGpwyjE4ZepsMxviZWYYNgV9MHHiW2Pr9YmJjIbQy2dg3uw1xSc7DW13G'
        b'5kJE2ng2J43vM2NzKdP75zO5QaYFn+SYFkyOacHkmBZMjmlBctjrt3XAbczZvKcPbjWSDw3H7UbycRNxy5F8KpVG4dbMnQXb2pLNM61H8pGxfWb9802O7uoybfx42SF7'
        b'AggeJ3oLb7zxchLgOvYasjYLwFU40Vv4DjnkUJbklZv/yz/LOcDKwWTpoHJvptUTmiv1lgEGywAjRjRnPdcSu8L/rvQRF1gF4nHIX4c9bkM8pmqtOb4b4lCWZLvwk+TY'
        b'hkfkzzBJHrcbC8v4FbtSk6c5A+jsOU3MZf0KlwEONkn/Oq9iXDl3GcfTeOptkLeUnko3sXn0jceuhoiiHIh78B9J/qUuSIdlArhhl2rBrVhVt5FLb8NFDw5sWd001e75'
        b'FEHanWQL09aDVdME+ikbdjTFmxatmtmNvtp5aNfO7F0xGRnqVSEbor7oSnzu0UcXA3+9d1WdYX/dmabEqg9R2p4t4eWdt6sn580/lHPotd139i1+a6rVa3e+niQQPG8R'
        b'U/BJs/+vfXdxrbyLw9bAb9snV7YKLy4Nu70JZG/wmVO3WWTOPIaFe2Ev3M18xTOfeaf2JGrNNgfWsJuDtPELmIelcJ8TPztfjC4ToHwxxw7dAY7oFheeFHgxnayHByRw'
        b'NwlqIOfzsAnuMwd2TnAXauP6VsDrrI07EM9l3q81B2bZljyOBdwbxjxlRmd48Ez2yLdB4SE7EjpgLeKg5vXmzOjoDjwHux5/PLQo6Mm3Q+HJjGHCqZPQZdgckTVPyich'
        b'NuTLDrdEgT9vzv7Hn6COKxiBjw3gT83fuKaworpCwZpCNseYwrfAiCnE8uIJ+M71eeSfydbloa3vA1vfY+sNtmFG27D6GSaeVUPO8zl6R//Tkwy8SCMvUs+LNPH89GMv'
        b'E8+2PpP8GzJ7js/H2uN/KK2zBjYu9fmjXpYUDnCrZNUDPPJK3QBfoaytkg3wSOwo3hxVlOCUvBY1wKUV8gH+ig0KGT3AI5H1A9yKasUAn/kA3QBfXly9EreuqK5VKga4'
        b'JeXyAW6NvHTArKyiSiHDN6uLawe4dRW1A/xiuqSiYoBbLluPQXD3VhV0RTWtIO/SDJjVKldUVZQMmBeXlMhqFfSADTNgLBu7O2DLbp4q6JpJ8dExA9Z0eUWZopDZMAzY'
        b'KqtLyosr8CaiULa+ZMCysJDGm4pavEUwU1YraVnpU3XMPHYv+sWfUMhq0ZzHCVE+dBz1xD36mR9mFnuKknOJ5vvfn/7LVDexkndtLFMDwN0Au9Ro7ncWjz9AOuBQWDiS'
        b'HzFV33mWjf0utbC6RiEkdbLSPJGFPIlILd72FVdVYRvLEGgKKbLCPCRX0CS6esCsqqakuAqzT4GyWlGxWsZs/uRVj1n+6T7xO4tEdmOZJJcDdi9Lb8LJEJeiqCEOj+Jh'
        b'LxAnNsDatt58iJdlRrkMgVHpYhtg6fjQwuuBhZc6y2ARarQIHQIcaoI+Mqk/pD/kbti9MH1kFr5MFg4mKzdVpN5darCKM1rF6XlxJuCgBw7NAgPwNAJP/eOLmd7/AQre'
        b'yQo='
    ))))

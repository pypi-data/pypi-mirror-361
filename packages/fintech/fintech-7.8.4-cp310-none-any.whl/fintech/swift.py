
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
        b'eJzVfAlcVEeaeL3XB01zg+IN7QkNNCAtIHgEjQfQHOIBngNNdwOtTdO87lZBRVG05RI88AAVUTw4RC7xlmxVkkk2ziSZzSQO4yQmZiezE5PMGKPRHP6r6oGCYv6zO7/d'
        b'32789Ut31VdV3/19VfU97oDn/hPgTxT+mKfjhxYsB5lgOaNltGwRWM7qBMeEWkEdw7lrhTrRNrAWmIetYHVirWgbs5XR2enYbQwDtOJFwD5LbvdYJ12UEjNvsSw7R2s1'
        b'6GQ5GTJLlk62IM+SlWOUzdMbLTpNlsyk1qxRZ+oCpdLFWXpzH6xWl6E36syyDKtRY9HnGM0ySw4G5cw6We+cOrMZDzMHSjVj+qEvwx8v/HEgJBjxwwZsjI21CWxCm8gm'
        b'ttnZJDZ7m9TmYHO0OdmcbS42V5ubzd3mYRtiG2rztA2zDbeNsI20jbKNto3J8KKESzZ57QTbwCbvfPuNXttACtjovQ0woMCrwHtRv+/rgH2GXJCg6c9NBn/c8MeDoCOk'
        b'HF0E5JIEgwR/j04TANIWPOla6GI3b2CdiH+gLeg4KkKlqDgxLgntROWJclQes8QgXqAQA5+5QtSNzkyXM1ZCdGgYOmCOiUe7UFk8KmOANAaehK0sbEWHYYWGeU6q7n14'
        b'JBO2MJgx/x+2ZLj3ks/sFGDyWUw+Q8lnKclMAbuo33dMfuY/Rn4ST/4Xm+2AI5ANl8jS4n4dbgK0cW4Qi3niOpcFaQH7WR++cclaCXAF73mJ09IM789K4xs3LhUBCWh9'
        b'FUSlxe18dQloAAYpbp60aoTwvrtkrh341Oce2zW5JN8TGOxxx5/mHWJa7fA889NCboX8OCOLb/7a/1uXfS6Mae+i28zPS//VeSboAdYgIohCZEONWBClQUm+vqgkKFqB'
        b'SmDDYt/YeFQREBiDdokUsfEMMLrYzxiGdr/Abrs+uqcSdhNWgwzBU4Yy/xBDswZj6NOJnzLUgWco0LmA0QCYFs9Ii/Py0QFrAG5bo8rANJT5q1AZKo5Lio4JiFkCQlSL'
        b'hsJ9i2EprAKZonWo2A7VylCFdSgesAqVwm1KeAHP7gq7YQPIRd2hVqI8Q+OFStiJ251XwSNgzRJYYh1CcEFn0WllCP62AJ2A+4EGNkutrsQGx8NmtFfkhnELBIFpLEXS'
        b'NUsK8CjXArc0xzkmES/LxmAPMAEbb50gbfqb6bFAf/KndxizGvckHKz5Mu0vaasz4io81DcyAj+Tq6PVf01z12RlGNLvpsWqf5shd49Vy10T1Gd1Z5hGj8y/aGPVK8Ae'
        b'TbQ6R7dHWHKy9XTw7GVl8tGy5MhvZ7+ZcMp5XuWlf3E8PALM+/3QtvzFctaCeQbSPNBJB8wjebzbBqvCD4ubBUOhTSiRoBLLcAyQjA65YEaWoApUhs0WFeojGNi2xEvO'
        b'9LC+crmAI9Lo92Dx47Hn9AwuJ19nlGXwzi7QvE6fYZnZI6WeLFWrtugInNkRPxzHOTKujITxxR9O3DeFXNAjWqs2WHU9dqmpnNWYmtrjkJqqMejURqspNfWFdeUMR/SD'
        b'E5EHmWU8mZ+IyfUTMcsyYoY8hYz4Z/KkXgSehnXr/KMD/BJgeWIM2h8eECMCnqhQOALVjJ2nYfupn3AQvcau5Kles9RRCLBes1SvBVSX2QLBon7fB3MUfZMP1GtxAtW7'
        b'kAx0He3dBKux9iuAAm4ZbiVOBZ5HVxajvaYx2NqCQFB2CFVfeAW1wRa0VwnPiajewWJk06/2ihWZA3H36dO/+zJt+WuVb7fAg7CzsmFvw7a2nT7bL22LOcy8lUEUzTHj'
        b'dpwA7D8j8TzpI2csI/CgWGWQf6wC7YxB3blxCSLgANtYdATZZveKaDDZUwn0OPCCzjDkqC1U0kTbHf2EWMZYytKnUhZSqfWItLp0vYUjQBxxTnK2n2RZjgS1fuIlw/2f'
        b'ivejQcQ7ljCkCzYOJ+JF51AFETGNLQEMGJUthLvhNi21wCdyd2YKC3xvhxkEV3wsq6lla90czJawYCHcJwRsOkCnpqNKCs2uHcpMZcHw22Fl3nFDPdZQzmtyvQk02g8P'
        b'M4DVAdQQDXdQ8G8jhjHTWTD1dlhcxuqhf022ehL/Woe2O9IB19A5AWAzAWrK01P4P6aOYKIwX27PLEt5MvaGkiKzdBMwW8KDUZsJI2MEqDEU2ij0eMtIZg4LZLdnNk85'
        b'ZyrJotDrw2AxAR+3hAVsDp56CDpCocOVo5loFrjenukYfidvlhPFJd7byYw6Q4NhfTBGHW4DqGMdKqTwFzy9mDgWBN+eGSDeNve1xVbiDFATvPAKHSGdKMIDigDqRI3w'
        b'NB1RvGoss4AFktsz46ZM042ZRPFZhQ75mbnQYMEMhuLTPBptodB3Ro9jFhPGz2zeGKRd420dSea/DOvyUId1cjDcgq5ierGfRh3wODpGx7w3eiKzlLB/5l2/4uGvRPBj'
        b'DqKLEjoGVaF9mGrsilEnbIb8mPlWH2YlkcHMGxNqPJqEVGR2sHWO2awMRmW5eJHNALUsRR0U/K2xciaNiCDihvy9iHFqyibjgiV0gYwALC9YDdBF2Ab3Ung7oR92ASDq'
        b'dkTABofhm2Mpm1bjdOQSHRGMGuzwkBqALqEDGjrCW6pgsojYIsry6lzKJNZhRFm3oRMOqMPsKIWdoZgGdJ6ZAsti6QATG8QYcF6AUQpQzLgfTlGCh6ejUgcuLFgTQdh0'
        b'CqALcG8+hf9b1mTGRCQdUeZ8YmK0lKKUAdvRVgfUhmXdNQSPwGmTANWj87zkVEoGm+mC2xGGyV9FNebSFZbp4VkHaUgwPIVasOzQfsYeVoyyEr8Aj6K98KgD6sI870Kd'
        b'ZLrtDDMXdlJaCmAhbDZjTXJGe50ILXWMP4fO05GoAp6Al832TqgVdqBiMm83EybEEZUsudFJ4pBrRV1wB6rCxobamIlwzxCqR/n548wOnGWyAxlykPGC3aiKdrjAi+PM'
        b'FnTBYYaUdJUz/rmz6GRT4C54xuzsJMXpzFEWCETMDNg91Eo8Lbw82QP3OE+SMUBgz0ShmiSqFuhgVDxuz3WaQUi6yASiIthAV8EKdSLLwckEy0amCIFgPBOVbuWtuRm2'
        b'wAtEw3NQKzYJE0Bn1/rzMt0P61AXtvQpQtgtBmwG9gzwjB1dSQA7DUQBnVQi3u7aUeVa3sTqYTU8akZtqMPl1TWEfS3MlM2YtWSYyORgxhzvcIk2kp5GRona0+QuVIhv'
        b'GqYw64nBRsRlfTUXrKCNX0WGMxtZYMK6YJ41+8No2jh7eASzhRhqRMCkullnHWijsyGSKWJBNFHLTDduOW0cEzKd2UmMNCIgfX2+9yu08fHSmUwZC7KwPi7426/UAbTR'
        b'ZUUUU0lMMyJgafGGmHW08RvtbAZb5FIM6YPUY8fSxs9D5zIHiUFGlGnmBhespY3LHeczh1mwHiM/TRSQxNHGN6wxzDFii6GG8euXQX44mB/PnCHmE3rDBDf8uIk2/tuo'
        b'BKaZmEio4/g/xhYl0sYecRLTSuwgtMz3NXtkpo03py1iOomqhzYvU2n1drwQ98CiMLOD1BntycAa4chEwUNwC+V4DDoZ4cA5O6GzsB4rkRszA9XM4QcdE61CHejCOnOA'
        b'SkD12B/WKniXdB1VxWALwJ4SnkaXiF7uY8ah/cgmF/JYMG8yhwWY3GnNIxunBXnRxsS0t5hjOKbfDjfMERvfXkkbf735HaZegP1L+I3gWL+IONo4b8gN5owA8yA8IDYy'
        b'2hLx8hycbGbpPpBsd0CG6J/d2JDVxS/kK5MSrN74uwI2F8DSRLwtq0DFMfGBqDiIHa4HnmlCH7QdNlPUr9oJEmaz5Fua4bvROXwa/F2svfNtRobb0hx/2GAPKBMdx6J9'
        b'qiAV2pUYI8JcrAMSVMTmoRZ4jFqXEBWPgx2wkyTmzDIOtgLs8g/OokMj0SHU6O+L09mdQQkiE6oGjpkCF2zM1TQ/XwJ36GEHxj4STNRGuqziCMsoIqOmC7GQMUxUmuED'
        b'TBNtPL9SHGBlsW3K0gICfR0BdSGK2ahJGQxgSxg29D1AjWpE1klE9DuwczysovlyBdmgqlAl3AYrgmLgWV8GyCwi5xh0hKZ301cHKqcAVIXXgPtAujs6bSU7eK9kD3+8'
        b'7aJbW7wHixFGotPAQy5AZbAU1VBvVJAP6/DGA56KJ14GbzyOwQMUq4mw/BUlbBfC6uW4pxYY2FW0PQ9td1AqAazPJM4bZKL9U2n7QqzAtUqlmENNuKMOrF4+lE8mK7B/'
        b'3qEMA6PRdvzrINDCrgVWsl/AsXjrq6pYgloCFQ1wNgngVnh5qrcvnXLj/AIlduidkzHsIaBDR1ElHRiKGj1UcXhMECr3Z2A1OgwclmPnBm2wTs7SoSPyYZEyjB02Ew+t'
        b'xhHrEDzJY3MNnYRVyjAx9uQN+GcNyIzX8M5yfyI6j0rx/iVeFILqgdCLgccjYR3Nk6fn2yvDmHF2JFiCLLhVYR1FhhyeAm3+RBqoOAGeFQp9gOMMrByt6AS/WDWsS1LC'
        b'LoC6sJDgMWCYg2qpVmEu16AWVBqHqReMReeBAF1nYM1ItN+aQCa+OjHMHBcTE09OL/C+MwI7arr19A2U+8UHyhWsFJ7U4Wh6Ctb7+sIGT3853Ifq/YfAfZ5DUf0weJoF'
        b'sGSIK17mPLxi+P7JkyfOKaLh01heHSOUFkARdMJR5Lh/giJaOD4ECKMY2IjJkw+hPmnyJJPZibMKYAm8jp3OUWY8Xq+U2osfuoiOow5n3DsHD2BRFyNHhavoMHk03rB2'
        b'kIHofBbuus74h8OtdLWsJeiiGQ9i0J6p1I15a5CN9sSiAxPMuVYpA48MxzHsCiNbAffQ6cLR6aU4TK1DnSJ0zp3mGmMXj+Vjog3bxAGSZXY6MfMzaIwPcXDnhVkLjy51'
        b'cHaAFSzcBxuBYDmzApXDcn7OTbDMbJGuE+I8Zw9e7hoz2g8dpIjkwC1S0iXCllePZyxkZDHD+GyjFe+JTqEOC4c6BfBiCB53nRmVh/bwuHTAHavNqN0iBgw8mgGLcXbi'
        b'CI/zWtCFulc7SJykYC4sBYJwJpqBLXRUCuZiPc7tch0ZdG4BXq6a8YlDl6kCc6PQHgdnR3sAtw4FgmlMTMgiPlTUO3vioM05s3hTdhQInJnwabCbTpeHduANQYcLandi'
        b'YYMPEIxjZk1Ah+mwSFjjaM7FC2GuHcS4dzFeqFJEu3LxJrDWLMUSi0WNGIk9jGwN3E+dAzwrmuZAeuBV2AIE7kxwiDvFDh2ENiXai913AIAXYVlAZh5FAe2ZjrbMehWW'
        b'ukhz1zLYsbYwsFy3gk8zr8FDcyhJyMZRknDadl5f6pnBmitw1HkPda/acynh9SjHHV8dimHfOb/yStEPrkOdxojqVozNnjvL4cj2qN1R2olZ049H7dy3Yuz7E0VDnRQT'
        b'p0tc/sXj9qG4wq7iO+92b94wSR7vsmN9gaGwMFhUGujFjG8YEr27YI/vDe3Ph2aLQh3XyqU3/uOOY0v37KHyhrapjj9Vv/ZQ9SDxhwRNVXpz0qmx+kN+y04u+330nXhb'
        b'0/3bP76x2tNldV7G59eG/rXaKf7zxotpipa9I24dlRxy5+68bZEp8xbfUhm+mLq+cqr/o47XLy3IHz3xX2e2d3z/4c7ygl+N3vGxeuzUAGned/Ue0Q+dS8LfPjAvf1FS'
        b'wb6S705M+w9uwTnJT/d/anLKDV+6cRp8c/fCFLezbf+xxZz+ximH5itflxV0f3a6uNOr8NbJmcDpY732B/+H28NCjsWPcrt5seEdxdd/KNrrd+rsyHc7Q5OLO0amv5/x'
        b'Ve2OE9OyuC8qH1+7efP7Bwc0n64pfLOgwP3PTy4rTy3Y+s2fgure/umTcat7PMulI+9XFyxqcO9pyN25raB4/IxpLbbbQ94MegIqcmou/260XGIhPm4k7N6MSgMSsPdB'
        b'FQHMcFSEt+5N2Nmmqi0kxMByeMTTPzAmwE8eiAFQMXbruWC4TPgr7MmPWGgKcwJWT3567oN2pwAhOfeBzdPoyQDciWpd0BnWPxA7u2K8qRbDXaxiNKqgZ0aw2h6VqAJ8'
        b'o1G5ipmNTVmCV88bu8hCVepKPtqVolPFxPvF2wGxkJXgjXCrhZzIuKE2Id2xF2OcsPOsEOjHAI9pAlQzC+6wUOXuhLVaVaICp1RrMW7XmVnJ9nLJ8+cQL3vIRS/vf3Z2'
        b'4c6fXVg4tdGs5g/h6RHGevyQzpYwYmYI48hIWCnjzAzBT6lAwrgzEtyGWxkp/bjSf32/JPS7M9v7mxXbsYz4iSP+7cm4shJWyAjF5BDME88gpvOzW5wZT9YZt5HvwvOc'
        b'I3h2MObYH7V+hyYvp07OcE599NGpXgW9xydDugc5PpEDsh+A+3sPx4LkOOL5J8QFEqFg+7+EKvzFYD5stoP7RkXJGd7XtsNCdFYVExCDty5bhQBnZbAGNqK2F5JTp778'
        b'MY5PTslZPHjxND7D6Wmyyv6jh8bfZePJpbJ+/y0gsjTL1ANvT+iVTJ5JJ4tfHDElWJbD0S8hgQOGDvgRY5FxOouVM5K5DHqzhUyRrjaukak1mhyr0SIzW9QWXbbOaDHL'
        b'1mXpNVkyNafDY0yczowbddoB06nNMqvZqjbItHoqRjWn15kDZbMM5hyZ2mCQLZq7YJYsQ68zaM10Ht16LHMNnoXAGAZMRU9JeShNjnGtjsNQ5NLIatRrcrQ6jBenN2aa'
        b'f4G2Wc+wyJNlYdTIbVVGjsGQsw6PJBNYNZh0XeTLp1BgHmp1XCqny9BxOqNGF9m7rsx3ljUD455pNvf25cufG/niGCyPtLSEHKMuLU3mO1uXb8186WAiAkLms/Vm4xaD'
        b'Tm/JV2cZnofuldUzYFWO0ZJjtGZn67jnYXFruo7rT4eZIDI4cLraoMYUpOaYdMZIyk48wJihxow3qw3anIHwvchk87jM0Wn02VgVMKWEUYOBaqwc4VDeM2xSUH0WZzUO'
        b'Ck2O1yPpE89p1WRhMDP+Zc1+GdYaQ45Z14f2XKP2/wDK6Tk5a3TaXpwH6EsytgeLzkhpkGXq0vFslv/dtBhzLP8AKWtzuEzsX7g1/0upMVuzUzWcTqu3mAejZRGxG9l8'
        b'q8WsyeL0GZgsWRDvdWU5RkPe/yhNvU5Ab6RWShyFrJc0nXEwsujtxC9QNVtnUJstdPj/DaL6JxCRT8NZ/1j01N+ZcsyW5yfo1QydWcPpTWTIyzw3kbVOn/4SjEnksqj7'
        b'lCsFRy68lMHwEg3rXfSZOg5c6+Wq+Z/mO6fDURQbXaQMexkMuRBd1axJ5xcYDJ74Ikx86hpdP1H1IYRZYEBXzWad4ZeGWnCAfwkTe+chEIMj+0LEVVmNWp1x8IjZuyyO'
        b'kYPE6oELY5hfmiNz7cC4O59IG9VnWMzYU2XgJIZ0DzbQxGEBYJ+nHnzdBb3dOqMigQt8GfYD1n4B78Hjf68iPJcDDBj80nyAH6vHSw8+MGb2rISXq11qDqfP1BuJSr3o'
        b'QxJ7+9KpQmIDls3jdNnadS+19f4z/wMKzYP/J51JlhpHm0Fd3nxdOrqKzXoQn/A/gBgxA2pnxM8NwGsx7vllYzOqs3XPvF1vXizzTcDNg+qplTPRvOiFEck6bp3OqCVm'
        b'mb9Op1kz2GizzqSO7J9Y4wn6ZfWDjFhhNK6KlC0xrjHmrDM+y7q1/fcBaq0WN6zTW7JIkq7nSJaq4/QamV77Sxl+JN7SqrOJ28Q4Lc56rpZs4MDI3n1OJN4XDBYZBkIP'
        b'uB0guzrnF24H4vkqnfc30Kqv6N2CtIDdml/xZ+sfKEgxE5Cdj04zKJaP4s/Wp6JrEO8z2Vx4BYBpYFoUOk6BM1aLAd68Lm3ySYtLXP0q4E+o2uHZcaQKBx1Bx/nT8Ivo'
        b'JD1Jz0Y7gvzlEWv77V7pznWst2ik66/kjtZx9CQj2BeVBsGL6tgYBSwJio1XKWJRuSpBBCajcrH/qLl0Lid4Ep33j0XHYPszAHd4VABbYZEfPVkOD0AnVLGJqHXg4fjU'
        b'cGij55tjc9b2OwDfoefPv4dvoIfLub6eqNQflcfHKliAdqySoEssLIHHURutjoMX4XV4XRWLqjxQWQwqU+FtOaoIikblAuDtLkQHkQ3us04gkDUzUQM5oO+FItcxxbAB'
        b'XQnCCE/wF02HJwrolJ6ocdkAOHplkQ8vJcQzQA6vimD11HjKoinoKOgHicFKg9ZEx2CwCWmiKIxYIV9wcRwVqf0DyZFtYmBsPCoOmAx3y8VgFKoRwhPwije9JELH0UV4'
        b'phcsJh6VBGCQeaHDhgqD0RlYbZVhmHS8RLW/fBzcO5jonOKplswAs5QhQgCPwGMAHgBadPYVKqkxsFDuH4sXrHpeUHj+i/xJ6DlUtVIZIgJL55HbhCwAt9IbGdgE6xaj'
        b'vXbIFgZAMAieFUuPNhKWblLFLrB7TqwjUREVew60xT2Taz6s5OWKdsNGOUunTYrPVcJ2yQiTGDBxALZERPCnxVgqF3EHANPjya3MGtMQOuFYtAfWP1MGGTrOKwNqNcjF'
        b'/KWkFDYolfAAumASAEYF4Nk1aDd/hn4FtcILuK95KLmOZhYC2InOw3P8tfcRyRTc1bqBw6MSATyXtoE3oUOwMkqpHI7xacdjkgHsGgKL6R3KshC4Q6lkgP14LF6wZsMm'
        b'SlAyOor2KpUiIJ0G4AlgWLqM2md39jAQAEDUw4lpKw+5pgAKi47awz1mBh3MA2AuOU03UdhmFzdSs+r6YW6awXttLJALKO1LM2Abqdgrp8wE3miHBB1kYVUqPMrfwRzB'
        b'9l6lCnwlQeFHZAtbhMAlWWBwyuOP7ZvGDFHFoJNwJ6nlEgoZWAuSsRTISVcgLI/F1Nvm9fEMbY3gB9UliJXKuDFPGYbVwGYl9WNaeHWxKhaveXpwo3NG+3uvruCZqVlK'
        b'5QqHPs4moQ4qD+zHKmANXvYg9kp9zHWFHXR6I6rOed5S0SF0uM9S0e5giuA4dEpEhADb0VUqBnQMNVIbXpQCO1+0Yef4ZyacD+t5ld9jgR1EZPYTqMii4X6KA9xtHjAF'
        b'Ne4seLnPuq1wJxWjT6CfUinEKDeSe8WshXA3tWaNW74qRpEQiM3YlxhppD2qEIBR0CaEJzej49R8QlCXDynDlCtisLmWwiZ7OxbuQqW80gzzo8WbvpbJaQFFnnn8HVcY'
        b'Oq1QxXgGPJUiLIZV/PXddlQDm/upyCsbeQ1ZH8NfvRetRKf8Y2cZFCqFXwIpDnbJFOiwAK9ZfQm5V7Fdnu5/PQsrSHXYYVgJzwrBqDgh3IPdbh11aKEeqAKDxuX3A+5/'
        b'j2viHe71qbCdvxGFu/rCB6x5hfgdP40INo2He3nU9sISt74bbWypsI2/0d4dQ/2WZjjw90XdsLb/3S9/8Yuu8iU5I+etR6Vx2Wg7uYHsvX6clG4ltXBWN9iEuUJ1lXIG'
        b'FmNVxciT83sV4UMIPCCOwS7wAhXK8mWwFmMSHRCbqBDDKiFwULHYqq9JKZdD7Pz7XZHCanSavyTdBouwoVLFPgxrncnN6/WN5PKVv3nNxlpPJh+JjsCGp/fv8GQSf/9e'
        b'aKR1l5sUmc9XCQCthVQJrIZdvDUdRm2rHFhUiOqxjoNFuehirytF9dNhs5mB21yoN9HALbR50zA3B04MULkJoAacBMhFdB6fEFiE9jLoKrxKKyil8DBf1qIlddUg6pPs'
        b'NEPyBB2vc6v0qAvtRQfswMwxAFaAVHQK6xy9IOuCHagEdgQLAGxbhm0d+/xjqNqaQvq6X3EyY6Gg8pikBbA9eNFCdBLVop20ejpQ4Ys54Nd7JbyIWMjOgORoQjplb1J0'
        b'AOnBdqNasgCVY+vo3uAGy6NRCb3+nThNSJOjdYlpcazzK4CPn5fFihfY54GqCP+c0V7MJ0/+NL5uGuyYgo2lioSdJOzvFBt4ajpRezTuwnH7hImhHq9FgM5YSSFzAapY'
        b'hdV0ZwzajfajfXDnWvwoxwZxNgy2iGB7+kJLugoWwfOhDNYp8TIHX/4m9cgmDIdX22romxFzrAOrCl/zFYFKVOhCQG+IBOJU1g924cyGevT21fCCKhDWrxzo0UMCqbKg'
        b'Wg+4r5+5h6JLvL2jS4iviRqfGYqXdoQ1fXSiehzOCavGw33RA/IRH7jraT4SnEhTDVQNG7E0BqYjRthC85EOWCEX0uAhgftQoTJsNirMxR4+FhMYtZyvA8mGFcopYiCx'
        b'I0mIDtpQOR9Uji5C55RTpLBwLeZIFMCx9egMvufgkkkYYWcZagU0HrTnw8Nyhu/bvxxuJbK5ED0Zd+Ls5GjEFCu5rIFX0J4RDqgclWLJlwahikWo1Qm2TZm8ILpP+xYq'
        b'khcOUKjDM4hOYbdUK8XaaqWW4oyNoQY2iQNQCQAbwUYsI6oU5wpwItsUBq/ALbCNBawnQI3Rw/nQsT0GnYVNItgFO7GKgALFequCho5ggZmWjC/0JZd2xEGmPFu9fhlZ'
        b'PUVhB6vg+Y3WaWSmFqxcLQ4J8ahckdxrI6g4JTp2SfRinhzYsADtjFcEJsQligB2Za3u8JAUbjfGYL0m+YiTLBntFYnRGb7EuWUtHyCH4eR/LzwrwkYM0CGSxzXMwyNo'
        b'wDiwFJZj/bINH6hfaL8nrUsRwDOwoZ+CjYBdvIJZMc+I+vqi07CFVCzswPG3y4kUc11gpsCqZVQxQl9NNKMuibPJRYw7iplJ6MAwWk+k/7HWhzVvx1///n3CpsW/qRgy'
        b'd8jm7yb/25+UMzqUDu3Ot9s3NraeeedC8FbvKzt/FTfl/TkHitA7xhsTPE6nfHRmyTCfoj+/PuFwdFjbD1vmJ46eeihrqlv89LzQv9/dfPuN1GtHRWWvWx5/d67gp4+b'
        b'Us4VLLkkP1Nfk3Fk+uS87Skd9yaFvzPl/ZQn98PORdQ0tf127Rc9f2i79+EfZlcVnVPPmP/x1Cu56z8QN/1h3+rjHRFpaEd2Q0r5uUeXK1YeWSM4sukvi7v2+CTkXpuv'
        b'OflWkvqIn6Dk4M8/NHvMX9GQ4hH6o1tE+ucX/zzudZ9N7DqXlYJb4bcs70/SpV6UKMNV5xs/3fvAvmvi0U9iFm//Rtbo9M2X8DeSdQ4r7W4F5ZXFXo77yBr0QX3+6x2C'
        b'GR++Nu3iqJvT2Q+vjr/d9tmRFfM+fOh4fHNl2ZUJd0ZejDA93L4h+eIS04wPfugwXdm+wfuWl8ll+x/9bw01vet0f47u4cyJRzMvn11fe6NpfV31sBsFn7rsnOH7oPIm'
        b'Svdom//6zKAHoraGm/tvDnvDa+iGuLvprV8O8Zp5Xfe1n/fjtvdOHE8+3m7IXb79yIPMur++PdqPm/zNNx7rNoWUFT78dPMbAd8L16jee/uAeOStWXdV7tevVeZu/2rO'
        b'prXLOj+QFLS4hdx7p+bztqaWthkP3/Rp+ftbTUlfVc5XzHxj6qbPQxvn/VhyP+fuwuJH3rXBfjf2vf9e8wOF9yw7xUejbfku9+faX52wZtejyrIDjdKSyNotHzuuz/rd'
        b'hb/PGHd5G6z7amrWhvVOP+Qt/Ouj3+jvNjP5lR61XMawyIdnG398NOVjpfuwmFshn/3W+NmEjH3hpTvfLfyoYNIF46mdSU2zPxK0n5x9jVFUOY2WTj4nfuPeo4aQoLdu'
        b'bC69/njTyAfCa+JOj81BsT8/bnXaGGOKLEv645ctX9+oPvphysORmaNPb7hz9fD98M/rve0Svv/NlnBPUfeSv//N6dBvZe/eezCyMGXCgX9/J+TdDYnd9l3f1AWnfl96'
        b'y/uVQ1/knjsWr/hiTubm6CXxh35KuT3vtWa7tZHGHbm779lvtFrnf5/wcVrVR6vsTt/clXtn1aoHfzq3ouXO5ZuZN48d9tJ/lbnpvpvTtP0zc+Lvp3ziL008OrPF74Pv'
        b'/t3Db/cKbaOrdvMGlcYn41HJB489Hnt/m3TYMuMy82CM2lu6oTl9/qz537Y/+OTRn7b8MCvv29AP7txdFvKBz/dZSVW//Rl2x4aHWUwf/Lyue5L4cd7jsyrvBe0PXD56'
        b'tPXA/G1yZwvdo55Bl9N7ixawoyKuSiEGcAu6NAx2CaMXh9HiB1iUDC/5+wXKcTigu8Um+2UsPAmvB9N3ZtDpcNg8oHwC5C0g1RMSeIRWR/iNQifx9g2WDaiOgLsttAAi'
        b'0mDfVxsB0mAlXxuxmRZATA8M6Ve3Aa+hPb2FG2gLrLTIaBzAqXCpfzTqDOpfJ8FXScCSFRbqzds3wC3+CfEBsWgXACKBBF5i1w1fRPvgqWAcbzfBNpwcBmE3Ll7HBmph'
        b'Ka0b0cEzo1U4xlTFqp5S5hIsyEQler6uo3EdtKni0I7+kTwHdVCyclBlkP8Ep16miWEzq4SVQp6f+3Um/kWSuARRSkjfeySd6JSFxOn5Pug06sCiwDmRqfcdJHQJHhg6'
        b'XSiA1XZyj3+0vuO/+JA7/fPzvPDqS7YlYkowrRsxkgKIzZKlQob/J6VVIOSfkGEZR1I7wgrx/6UMy7LMYP+k9yXOjnTESIZUjZDvw2n9ifgniciR4Vt4COEWPA+Z+Ykr'
        b'y/4sFLA/CYXsj0IR+4PQjn0klLDfC+3Zh0Ip+0DowH4ndGTvC53Yb4XO7D2hC/t3oSv7N6Eb+43Qnf2a9SBrS750HiZjxHhdIePKDGdcBc4YX0e8wmi82ugnQ2iViisr'
        b'fSLG/ye0EarETwh+jizB1h1jKRXhHpZQSD5CVowhxKyYnYB/iXvrZhzpWDGGc6TfR+PVhuD+kZhO0i5+wj6RCjHNP0uFjpSHwi3sPakrWYFU3Dji+egcLOfSJxK5oEdI'
        b'Tj37Vcn888KWM5xrn7jpUnuImIkNgMIJ3wxST0OU3AgPoUJa3LQ7ku6zFSR7w3slkwBdcpC+8FYYUZooMi/J2nTkXWSwnNUyywVadhF94bbHlR7i0gIXbi7H5XCPvflj'
        b'XaqAXG+9ik4rUxtlOtIfmCAX9khSU8k5eGpqjzQ1lX/pGH93TE3NtaoNvT12qanaHE1qKq/Vzx6UYJKGkdI/esArARKW7oKHBMM2B2d0weJgT4qGFFyvHcM69yBUKxZh'
        b'Y98vZ+bp//JWosAchYffe/v0jPd+nYCiXMW3Vx14PcF82f7aR6BunSS00/Tpaw4/theNywW1lRfTVB3zPns9NOXjvbnj6qpmfnXjZ//ffH3gu48X7IoVu7ef6P79nRmd'
        b'1beXf/P73xc4jf+6we/GsQPfvrE5MMkz+jKbrPw6t+VEd9hG+zl+0ypr78VcvbnwddWl6zsWy+4Ynxj3TagZ7bc+8ndvFSXX3yl0124YyZlmTws5Krrn+2P0kKT0d860'
        b'Lrl4F6y+K9txU13WemK45teT/yUhveTIm47TSiPWejncHbf/ZuT+Pwxtbndqbvvy5muTulrLx9xNd/lh6mtjd5nKPKbk9lgLdBNyd5hX3nZPWTX+d9F73vw2U/7NoaxP'
        b'q78IX5J0cvHck49E4Z/sEdaelqNDo7sX+WyL80s6tDKodMWt7ck/jvKePXQF+zDLxmanutyPmsd+lnTzY++UvNW6f/WUCy0kOY8bCjtmwTK8B8DbjKkA7Vo2iUaSAANs'
        b'5t/rtCr8vHyevdeJrsNLlgl8KKyFBx38sCOfbCRhJL7v/U9v2CHEQe8UbOJDzl60Be02w7PRCUGwW+HbF3LcUKUAtqasxeZArcL9v9FDi2lO/fIH9bxYtQ05am1qKnW7'
        b'BfjBerLsFEZGXMUT4hwkrCvrKmHFxD2+8CHu8vkPcZ/Pf4g7xR+xkHd2kkfYy1E3Lf5hiIRNdGR8GbCZ3ejJcMP6uSEWm9MzJ+T238Mmhhv+1E7J4sQn0TK/wLuDuCVy'
        b'6jQZ5xY2tD8blpKDMPLyPc4vKuyA8wjBGPsM/dQ7SxlzBobr2Ocy5s3JzlujXHe8vzljnZMl/eSO23VX4Zya8x37fvu5JocJr/q+cZhnY/V376/O+aT50WdrpJ98c6o1'
        b'OrQ7Nrn435402va7zjv13vtm7e0i859h1etvvf7V5Dm77n1VrVib8uRH5o13h1+46yW3oxqHduO95j76vmYiPb+ywylDuxM6y6IzsB5doVkDrEX1I1SJCtRGwBIVLHDD'
        b'CVMDuiqAdehCPoUZis6jOvNKnjjylgAsp8S5C7zwhrqVlpS6oWO4j1SjLljG16PGZ9MqWdy+FZ5S9fs7Aw5y2JbMokrUhDppJqiFWxY+94cIjieTv0NwDdsO3TsfQGUb'
        b'3IL9Y0XkzJlUYC/qMxev/+as5r+qQ8JfNDC9UW/pNTASmCRO0t661wAB2Aw2CzdzI54qvaxHYNAZe4Sk0rJHZLGaDLoeIblSxDFZr8FPUi3XIzBbuB5Rep5FZ+4RkoKL'
        b'HoHeaOkR0XeHe0Sc2piJR+uNJqulR6DJ4noEOZy2R5yhN1h0+Ee22tQjyNebekRqs0av7xFk6dZjEDy9VG/WG80WUmLVIzZZ0w16TY+dWqPRmSzmHke6YAh/pdvjxOds'
        b'enPO1LDgyT0O5ix9hiWVBs0eJ6tRk6XW40Caqluv6bFPTTXjwGrCYVJsNVrNOu0zs+bJ9uLCyPfJ5EH+EgFH7tA4svvgyBkb50MeRME4UmfLEV/MkfMUjrw/xJFDeY78'
        b'HQaOZM4c8eWcH3mQt7g5otQcOcjmlOQRTB7kIoCbQh7EdjiilxzJ5rlQ8ggnD/+nXoFIx77PK8x79KJXoBCPJX0v7ve4pqb2fu91ro9HZgz8CyYyY45FRvp02gS5hCM+'
        b'h2QQaoMBuzyqDcQSeqRYFJzFTO6ue8SGHI3agKWw0Gq06LN1NH3hIvpY+FzK0SOZzicqM5k+zIVAKJawROPA5iGuLM1+/x9R9/+5'
    ))))

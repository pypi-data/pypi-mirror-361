
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
        b'eJzVvAdcVFfaMH7uFNrQe2foDMMMZegqgoLSUVEwNuogI+OAU+wFK4OAgFgGRR1bxJoBjGI352w2ZVMYMXEgZmPcTTa7yW4wMWWzu8n/nHtBQc3+3/197/sVfsn13HOe'
        b'59zz9Ofc89z5Axj3xx7999tl+LIfVIIFYClYQFVS28AClpS9zBI891fJOksxLaVlJZsFpNyzoyMrgcpyIQv3mFVyxmC2UPjeXPoEhwJruJbVArOfpFaFxVkz5vKX11Zq'
        b'5FJ+bRVfXS3lz1qjrq5V8GfIFGppRTW/rqyipmypVGxlNbdaphqDrZRWyRRSFb9Ko6hQy2oVKr66FoMqVVL+6JxSlQqjqcRWFT7jVu6L/+cRYgfwpQE0UA2sBnYDp4Hb'
        b'YNZg3mDRYNlg1cBrsG6wabBtsGuwb3BocGxwanBucGlwbXBrcG/waPBs8GrwbvDZD7TeWjeto9ZCa65119poOVo7rZXWSWuttdS6aIGWrbXXOmu5Wluth9ZVy9N6as20'
        b'LC2l9dL6aB2qfDF7LTb4skCj9xjrNvhZAhZY7zt2j9t+Y20KbPTd6FcIAl/QuwqsZr8EVlGW2wSs/IrxYnLA/zsRYjm0ZNcAgXm+3AK3ryWzAemrt9skl81bADRB+CbZ'
        b'Bm1FTaixIHc20qKWAgFqyZo3a8M8kRkIzeCgW/AIvCygNF7kwfAG0sGzU1VZeWgXas5DzRSwymJBQ2xABTVuAY5jC6jHl70ODXgRmC8A84qLuWGOeWeJecbDPLPBfLLD'
        b'HHPAHHWqcqS5g9Wm8YlibWDR3KHGcYc1jg/URtYod57pfcKdqv9/7uQy3JlfaLYgmHIHgF+a+/eZ6wDd2WPPWn+eRVql1posX6aTqrRYf5Xi477S3KJIMdOZLuYu2gjs'
        b'AUgtjZiXFgpOA7kV7g6O9uA8dgRRjhafhn7DuhT91+ktlJzY1s8FnZTBfHWKRWppzP0Y800zAd3tvOFbuz12siTerAfUz/MvlO4Bw0AjwgNelRIspqbI2WFhaGdkpgjt'
        b'hKfnhmXnodYIcZYIdsK+7DwKKOwsp6Bbygni4IxRXE7EwabFQUQBqthPGM7+b2P4c+po/hzDeQzDCzfaAW8ALHITSiOUliKGTGd4Gp7DhDYLc1AzasydnZkVkTUPxOQU'
        b'usA9c2ET3AuWpsEWrjk64lKjccUYUIe6YR/aLZPAy/gR8DRYkQE7NC5k6Dpsg7um4JGLZOQQqEEt9hpnPOKZkQ8Pwb2SGAK1D1SgPWgvPYB60QV0FXVw0dG1AIiBGB6d'
        b'T6+2U8MDGCBz0Lc0V+a5ghG6TYkTwEZksYRXuv7mpJVAxg++z1WtxiOb31hz8Jr125MPbW482tHTsSYukO1+IqrqoCTK+dHe1L+nOryc/3l4vJmZbmeI/i/On8vdzHZY'
        b'/TYgZMYO531Wvy23f3fB72YhMJc3d/D1Lrjv9Xfqqfpkjzmmk6mx66wCdVW5n7aVZzZ89Mnr1mo7JzjlNesuD2Dr63bHBwpYjzFPgYg7OxYZeJiHgjyNKBxrDAu4wAaO'
        b'hQqefkxsGTYjLTyIGb0TtWJGX4S7sG9IomCPUCLgDLPCBEobDPX0oiLS49fX1//kOrlKWbtWquBXMa5arFolq1KnDFvRfrikskwtXTuuzSLIdfjyYz14lE4Be6e2uKa1'
        b'utk7N9135Q/4J/fPM/pPG3SdPmA/3eTqpatsl99xFerVd1wl3WrtTJOzl07aXqDNMDm77c9sz9RJ9dP0s3WybpfuFQaHbk/DvP7o/tmGBQM+qYPOadqMISe+3mXQKXTA'
        b'OvRbonxKon0Cs2HuyjK5RjpsXlKi1ChKSoZ5JSUVcmmZQlOHe56h1IxYO5/QqrQlnXb4Mp6iQAIUiy9/rwffT6coyulTW7emmnreCItLOQ/xHJuSPuXYbcszWdgNWTj9'
        b'+IgLuPZjdz+piNrsNgsAx3gidgXrRWZaScyURaIUbajUE0NlTfCMbMsJZojb7HEmydrIHjXUZ3p/3VCfLOCJoZrla0gHPArbhaiDAjGoGYiAqAKe0BAfX4tOwW7UwQaw'
        b'Zw2IBJE1K+luqC3hYgMCfugGMaC56KIMLPwWqBKJKKrOH8RGcbRD0NROsU9EvRx1vmqL4Zou2aPJqJ5fqJvUeeb25JAd+foLH8xajNVaBGYds3z9CzcB9dgTo9vDnnwh'
        b'vJ6QLULarNx8LuDBHhY6JIJHBexnxUgSnDEZDvMY8VXJa8vUa8ff0OoZwajnyFwKuHjuz2vP0wfqVYPOQqxPds4md6yCnbw27pCTpy6uI2XA2l9p/1S1lCSgDHMrpeUy'
        b'tZKQr3R6gTrR+sSokxtRp/FLEI7p009YnwqxPnn+p/rUYRYIjvPEbNon9YY7UbEsEPYg/p3iAzWZ02lPiHajreYqdRg6HB/FAaxygF72sKXBQ22dqUQWcH8Qbx2Qxd2e'
        b'SPvUqagZ7lCpzeD1+CgKsKQAnYZNgTT8uumu1GQWSMTTeymUaxxo+NmwA3aq1HCzMj6KDVhLATo7H12j4Wc7elCpmMsPUqzX/85cOY/x2S3OqAHDG+DJBLIeBUBncsxp'
        b'+KRgLyqdBfgPUiLmdc5ZE0575drZa1TqRXBXQhQLsGrx7GinEw0ttfKhMlnA/kFKs8PuxdX29OwboHatCl3M9okji4dbAepjo14a3iPUl8plgSg8O+Un7FtNw6MjTlUY'
        b'foNnXBQXw28D2B2eS6LhL4j8qVksYIHn9/2icMt6mpk+c71VSnQ6kZ4er+Yc2oZu0eA7NgRQcwnvU96x8a04T2mIsCWwNxP1abCp7IsmxOIQhvqWCGiEz1cEUfMJ91Mi'
        b'5r8a8l2UxoOsZy+6uQxjoE50JZpQjCMUuojOq2mUSzkh1CIigJTctFPFnzszJGx3QmdVKnQc9UjIMzYBdCFtBQ3/z/lhVCkRQFJE8B6NIIRe08ZUdAU/IRSdiyYCgwcA'
        b'6ofnGAXaLBZSlSyQ+iCpOVyduzeBRkA9m9AWQsWhxOgoc4xxEKArGfNohI70CKqaiCypeZG77EYeI+JOfjnqUwXDdmsrTAJ6lYrNRAdo+Ga+mJKzQCmGj1As8+QwGtqD'
        b'zk7jKdkzaQWFLwN0uXoTDW6aHUXVERknRazkTPuhiCF4C2shD/VAPbwSRxBwLspeV0HDv+kbQ2G7nvUgyVq+LuTzYgZ+Myb4Ms8qcnoMkRraR1mio1n0UDHUoyYeulQJ'
        b'z9LyQdspatkURhKvoN5ZKtSH9sLzq2wJGUcpIU6TL9OjKiz37SpL2IvO2yADmfUWFY+BtfS009F5tJ+3wq1Ygy5h94x6qODlsJ9WZzHlr+Lh2LtVqSZYOsp3kZCeEadx'
        b'nWirSo2uTsKLJWMt+HlYcWg/vBjW+6hsYf80G8xRNpeaMm0S7XAXobM5Ktv0l2xsKcC2pFJr3BkJbClaqLJFm7NsVhCq+ikxugCP0jOpAufybKSr6mAzB7ADqVR0K4BG'
        b'CURt6JxKGY3206ZQB9B5uI8ZEsPefJXaHm6NjzUDrCrsEdBBPJs7ra84lzqgUsFj8JKENiFscr0u5jRJgfA4OqTC0j1ujfrsCAsvULHoADrAELwLnuOr0CWs3r2jw2co'
        b'yQZ4QWBHy3JSTSy1mthr0jsp71evqmasTBNPrWeBOty5ySzCIpTu/AhnL/XEUpPkL6XHuzDm9WXpJGobC2Q+SDqXvXXT9CzGQSomU1pipElfcebnlsbSnSORKVQzC1Rj'
        b'yJWfOUyqozvdqTSqjVhn0lf5zTNay+jO2qxp1B4WmI+fXjzVu5ExSnZVOqUjRpnUvHRytjaF7jyrmEF1scBqrLjglNvKVXTnRVEWpSfmGNc8s87q1my60zc9l+omFhQn'
        b'Xx8U/+eZdGfWhgLqHDGTOHnhorg3uHTnvMmzKQMxhrivgjwiTzvQnQmyQuoi0fi4ryTxHl/xaYMKgjtRl4pXjV61InphTaXCvcW0+i1Gx2E7T1mUZ2uD9ciBmoJuumlI'
        b'eEUXWfAwVuDL6Dp6dRWOoESjhbAP7qZ9AJ7wuhexhpexyC4S7dxDBVQUCDj0Ir6q+y3VxcbUTsqdIczcT9GdV9hvUXociR8kyIu3cj0YUb2c/DvqBBs7mISvnPjKLm+6'
        b'8xv1O1Q3G7MgwdrXbVXnpAlbGO5YalKFL3u5oztKDr2bBFXc/4F943PZkRl4NjsKydf4kQCHmufhfck5dKYA74pbUWNWnhg14nzbtZQT6lrAuPkUlms/oLeREXcn2TKb'
        b'h8kcizn2gE+yA7lzqS2gbSmRBxtz0EF0IDIH7SrI4gILtI21RhhIDzrgnB1v9PA2fBu8SPY01EsAnpsvpgdD5BJhGE71tZE4L7LGVte6lG0XiF0HcRFx0mWwD688GbsY'
        b'v2TYjlqVZAn0OkRBXPFkFrNzjQoXMZ17J5vPCgT0bti62jMb0G4jGe+0LkuqYGMU0YbdoCw/XxNCmhfgCUkO7MBWTLYTreTtQA5sjcyC58MowFdzbbGFXxrNJWfDeonX'
        b'KpLvwD2gHF50pLkI92Av3CXEe1v6xQLe6GZxSpcAJwEbpyL16QxuG7ruL5kHXxnbtS0PovU5LxUeksDmjbCX7PKOAHk8aqIHfOF1tgT1R0gI/GGwFN6CXUyw6cbB7IYE'
        b'Hp4kMSNrAsucYC8TJ65gD9wiQfrAeIKkA5XoBtqq8aFjLB48k5NNVpfPCMe2jr0M6hLtkIFeYAns8JGgI5HxZB2dQDoLNWjIbgwacI5wNicXY0WiFiEFeIHoxgLsCefB'
        b'zQIWjVpRDHUSK9gTj10DjsZVqNWTJoHCou6WwFdQTzxZ6UGwdO4a2hjtc7BPbcIbvDyuWAQ4vhQ8hhrRLlraOfBKoMQiJR6bEOwC1a7oAm3eacgQLSQyQY358DwHWOOs'
        b'rnUK226jGf2oQlWWBMe2E/ASWbIeyKE+lHELB52rUFMuJpyNV3MYsNFNCh6Ep9BVTR4BvRaWqsrNysojL5Ce7NvDxILwPNiwRCwQsazgSSl8Gb0MT4SFwdOuQgHcg04I'
        b'neEeVxd0wg2eYmHX4myPFcDgJf/xl19+YQdwQv5G0Rop37NxCmAkcwPtiRDmizI5qMUNcFIpeMYLXRU4M9v2JqtFKhulhs1C57FfOkwFTitmfNYlf3gd9dnioRpMGAtd'
        b'ogQusIOe0bsyD/URJHgxH4/cxK6uA/XQQ5ugDp1SYSwKR/HttKfzs4pmwupVeBMnrys0VhQ6HI2D3TWKH55BmyA8hLRhOJqtQhe5NaiHzkr8XWEbE+pOF2AN6sNjNhT2'
        b'FwY6JYjZgHbTGhmK2r15tjzYyop7CbAXUAuxjV5hMq8t6HyVSm21igN3oG34eTco7zisx/QDj6I9yEAGubXwNJ5xM8VHHfAVhvSmdfAM6lMr0UU27MzFmDcpL8cABrFF'
        b'lKjC9tSKetVmgMJCRa1Y8U8wnK5HjfAQz8LGCsB+nCAkUJnL0Hl6qBBe5uMscIU1BfeSxaADVOiqJAarEZ2DV3i21pYA3loI2JOoLHiqlJaOK9qfhaO70pa1KBewbakE'
        b'uCOG0awWtBXHkz471GvDwis4D9gBVBrUwm0MBXvd0RbVCvy0QLQHr/8S5Qv3whZGDD1eqSorLDxr+Cpex26Kj8VyieGYDu6EB3lkcBG8CtiOVBTcgtGInXnjtGsf6sC2'
        b'FEHoPBXh5k8zJFPGg012VitWUgCPX+bgLAW2hMIexl1cwG63niaNE0VThrbPkvlflnFUv8c25rbLuqUwR3E31f78zybf90M7LDkxnztBeVtbIuVwMFNu6suKPxG0bWZ5'
        b'dGAGNWxuuNs0pPcOeJibKR/yt739pXLYutfUuf3h9sX/OvOXD84qv7v3x51/eWS5/PGQ7eyMXfPftdxn9WF00uvJXS/1Cbbcu/kbwXr2gvC/TL6X8Ml3uo74FMPJ14a7'
        b'W1/5SD747udf/bRD9eq9D+Nzt4f9uc7nkT73akR+huvjo6bMmcOnY75s/CB637ezQiu7BoYiK90b3p7MqSqzeb2m6zPjNx6PT76X+lZi2CPz1NCFX+zS8/SDnwkGOB/+'
        b'rff23B2Gqi0uhu9Zl4btfN5K/8Z3Q8hfCv/4Cf9P7xUdujbnT6KBf4keH9Z/Xf/7W9UmO8XrP3M9VJ961Jxp2LShNGzbYODD14pONmxZkvSPW3nV5YfkW34pan17dsI+'
        b'v6R/JGXkn/2tjH8s6rrQaenFAxlNfiV/yRmy/02u9r13r8i1v2z8cs3Plx77q1e5f/Nj1t6oebJ3fuvqfVz5ea/yzvEfw77pKm8VLpRV3521tKhw6eItb7VWzmg4Zrhi'
        b'fin7X6r9F/ZuMq69c6npqyPiJS91rhu5yzb89cOtqw8n/JL+zd9lKrd/tsYn39K/avaN5Ld7Bn3/1fT9y39u+f7Me+uG3OCFf71zJ/TtT36h+hd0WcpPCyweE+8Pu/Jg'
        b'K2qKyMfODbVGYB+OruEdA3biUJfwmBwwKHAyqxPiPckxcVZEuECMoVAjTiL5nCVwd+JjomVTrZPGXrmxYQuOLvQrt9rSx7S2X7QrEIqxD23Es1umm8FdLBGqB/SLj/lo'
        b'JzyQI4N7I8IyUUsOBSzwo9fgferux8QY1Kg3KycrLzzPHExCt8w4LAt0DHbR645YmiPMjAjHk2IDbUatbNQZBJwmsXGO0TX/MbFO2JyLtDlo59ICEc7pVlJpU9EFgc0z'
        b'r1P+84uKXPijf/X1T17FODKvPtTKMoWqjDnFWfuCPvrFzBUW/WLmcToLeAS3cUxuXrpco5sAt5zddd4DziEm/2B92VG3bofuaL13G6dtfrstAcps33jPTWR0E911i3wQ'
        b'HN6WrnNvzzeFkIZHR4HJxUMX1r7knovY6CLuVt11kTzwDdBHdy7Vl+nLdTUYyKF95hPoETPg7XskoTNBH3twSlu6ydNXt6IztG26ycvvSHJnsr7i4NTu6O6YAS9xW/pH'
        b'/sE6rokfrC/Xr9BbMk08J9304uvTD0wxSRJ16XrfO95RJp8AfeWBxaaoONzhdcdbZPIN1KsPLDdw+517bUxBgu65x/IM0n5173KTN1/v0VlwzzvG6B1jiPvAO2kMOTIW'
        b'I3ve8Y4Y6xBLcIfHgQJyLzf6xBBU187ce96RRu9IA/cD7/hRyE/F0Ybgs8ueQhNsYRS+dz2Qi++PLO5c3FXyIDwS97gcyBmxBT6BR3I7c0cAFZ5GmaZnPmJT4VnUY0D5'
        b'ZFMPgkK7g4/mGIKNQQm6DJNfoD7rwCYTP0j/0lE7A2uQLzFojPzJd/mSB0zfPX68kR9v0HzAnzKSRYGAkJFcnCcGYAEWtVuPsLiejm1mI9YgMLTNjqa9qwAzPiziFdvT'
        b'tgbVYNgko3NwW4ZOoucOuXl2arpdDCGn/QjpHF1Rp7V+ntFdaAqP7LQb9ggzuXvTfSWD7nH9zkb3KXfd40ZsgE8EJgjrkGX71IGQZKNT8oOI1NvOt2Wv+RkjZmO5u7bn'
        b'6t0GnQVEVQTtJQNhKYMuKVjierPOyfe8hEYvYfeMD70kpsiM25VvJr1Wa4wsGn140aB7xKNioq/j3hJaDFuP1+0XvSd81nrozcJ4w1GS984vspTpBDwJ0O+jf5jOoihP'
        b'LKP//CXiHrMgcIIXyRZQdMwzd0S9OVlzoSEiiwPwTgMeTIY9EzZlNmM7opVkv2AzuikjR3zg+UO+KpsnmzTOf9smrVrA+m45XoYVf9zfLMIgFb9s4okwfcy8pk7Kz5ub'
        b'FBvFr1XSjRjxBNQJN1lqvlKq1igVZC65TKUmU5SXKWr4ZRUVtRqFmq9Sl6mly6UKtYq/qlpWUc0vU0oxTp1SqsKd0soJ05Wp+BqVpkzOr5TRYitTyqQqMT9Nrqrll8nl'
        b'/MKMWWn8KplUXqmi55GuxjKuwLMQGPmEqeizDAaqolaxUqrEUOQgXKOQVdRWSvG6lDLFUtW/oS3t6SrW8Kvx0sgJfFWtXF67CmOSCTQVmHRp8q9PIcI8rJQqS5TSKqlS'
        b'qqiQJo8+lx+WpqnCa1+qUo2OrRU8g/k8DpZHaWl+rUJaWsoPmyZdq1n6q8hEBITMp8+bhnvkUpl6bVm1/FnoUVk9Bc6pVahrFZrly6XKZ2Fxb7lUOZ4OFVnIi4HLy+Rl'
        b'mIKS2jqpIplmJ0ZQVJVhxqvK5JW1E+FHF7OcWUu6tEK2HKsCppQw6kWgFRol4dCap6spRieqlRrFC6HJsVQyfcVzaiqqMZgK32mW/9qqK+S1KunYsjMUlf8PLLm8trZG'
        b'Wjm65gn6UoTtQS1V0DTwl0rL8Wzq/7tpUdSq/wukrKxVLsX+RVnzfyk1Ks3ykgqltFKmVr2IlkJiN/yZGrWqolopq8Jk8SMZr8uvVcjX/G+ladQJyBS0lRJHwR8lTap4'
        b'EVn0cd6/oWqaVF6mUtPo/28QNT5hSH4SzsbHoif+rq5WpX52glHNkKoqlLI6gvJrnpvIWior/5UVk8ilLhtTrmIcufCj5PJf0bDRhz5Vx4nP+nXV/I/5rpTiKIqNLpmP'
        b'vQyGnIOuV9SUMw94ETzxRZj4khrpOFGNLQizQI6uq1RS+b9DVeMA/ytMHJ2HQLx4sc9F3ByNolKqeHHEHH0sjpEviNUTH4xh/t0cS1dOjLszibTRiSq1CnuqKpzEkOEX'
        b'IdYpsQCwzyt78XNnjQ5LFaJ8pfjXVj/h2c+t+8Xxf1QRnskBJiD/aj7A4Mrwo1+MmDUtLf/X1a6kVilbKlMQlXrehxSMjpXTCokNmD9DKV1euepXbX38zP8FhWbA/0Nn'
        b'Ul2Go80LXd5MaTm6js36BT7hf8PCiBnQdkb83IR1zcUj/97YFGXLpU+93WhezA/Lx90v1FONso7Oi57DKJIqV0kVlcQs166SVtS8CFslrStLHp9Y4wnGZfUvwFioUCxO'
        b'5s9T1ChqVymeZt2V4/cBZZWVuGOVTF1NknSZkmSpUqWsgi+r/HcZfjLeJ5YtJ24Tr2lu9TP1sRMRk0f3Ocl4X/CiyDAResKpmC149lQsjynu+yySRRcURc3YFFLvnM4c'
        b'KvmlcskhGD9qxlp3/5VqwJQL7ZkVZu8M+1gATAKT4CG0kylz4JoDawDso1y/yPp6dTqgN6VzJGj/aM0e1MFjoAKehKc0fPIGDDZuFAqyUbMwH91El3LFzNsuoRnw9+N6'
        b'es0VWGsCMJh1cVkq7EBNkdlZIrgzMjsvR5SNWnLyuSAatZgJl6Lt9FGPGnXAo8Jxo44+8CY8zIYG2DOPeXPdiOpnhm989jQosU5Al8rCFt6anNz8TNT05MiHnPeg4/Aq'
        b'jZ4DdXmoSYha8rJFs2tZwAJdYcGdsAX2aPzxsCbah8ychZpzpqDj+bAFtUZmohY28HPkIF0gOqcJpl+rH4TnxuAwUAG8gLahXaiRnAAGCbmT4QF4gIYs9fDIya5Guqeg'
        b'zEFdfh4FBPA6Fx6YDQ/ST4bXl6WMmxIDXRGSwzgMGFTKTRVb0NxGFwPdhWLUgicSZ+cJ0VHUGCEwA17oIAcehzsWasj7UArugHtHobJ46Hge2kmA3Fw4Ue7orCaQPhNB'
        b'BrR1VG5wc9UzYkPt8Cz91n6lxSpJDDlU24+uzQeV6Dq6Rh+soVO+qH6CnODlalpOGwqZN/f6YtgiieGSozMO1IJqdBmep6d0T0OdHHQEdZhjJQVR6BV0hhY9PIN60XE3'
        b'tOc50UKDlJYt7kI3sXBhl+0E4cIesYDFnE2cAgUS2FtHTlZuoSO55ID0mjm9oGWoIwMPEaDD6BC8BGrg6U0MLU01RDMZnYhGjWNKgVWxSWDGHLE0w50bJJI6Np53J9Ll'
        b'AHieQn1Mqevh3LkSCTJwAYVFe20OgBcLFjNIPQLUK5EoCdLx2AIAX0H70B4GqR4eX4mxejFWWWURgJdgVxpz1HoansiWSMgB4jHFTFBjgbT0SU5WMTogkRB2HndEp4Ac'
        b'tsEbTFEFcAURxFxTxIIMOz+gIWVxoYAU0m5V4WkyQMZGdJkG/dqbPvVOjHL9c/CXonAgYDOM3zod9pPDwxbCUxk6R2EG6FhwL9wK9YzNHV1g52WdIxaFE2nDCxxgV8SW'
        b'w1a4nybUxhVeyMmCFxZFYIFxOBQ8gg7AG1gkhFQzeBzdYliHts0mnIOX0hkVaULb8kZZBzumEM7Z59HaWSBErWO2AM85P2uGcC/aPXp6C09O4zEsdi8gHJ4FW+klRUpY'
        b'o+zFwHsJg9EWpKdNSGxTMN500VbReMtVedLzIr3VmlEpTIfXQY0zbNaEAnI8eWwyxtZV/LpBw6uwlxYCenXd5FGRJZYCuZhNO8IyZ95EM+/AlvjUztHhEuZctSF0iURC'
        b'H6unwYvYfC6gzTRvsFVrA3KyRPlibNVh6HjG6OkC8IINHOyVj6FXmVPPs/DkPHImLBBlob7VHGBpzoK7ZsIGpvQgmS4Bd4+KfzNXsojLHPTCc1GoGwtyJzz4RJKCSuYI'
        b'/hpewI0nSoL2zR9TkqVwN32O5yGWoA6xMFuUIwrPJx8o2C1lS2vQedoNoj3oFjqRM6FIYQZsxGwjx+FeuRy4e00Q7QYT02H7OLhyxcRyhg3JDBP60PGKnGxoqCWuAu4a'
        b'H0/CK7jw7GoN7TGy0Tl0JIep6ECn0e7Rqg6sQkdpTxm/HB6ZWPoAnKagLaT2oQodounycUKHUVPuAniVHMOPHsEnYRGH4cGIYnQOHpY84QshKRLtzCXnTDmECTFwv1mW'
        b'32xaIitgw2q8kswadCEiu0BkBng5LDz3ZW+mVKEFt8+QKgEBvPakUGAK2y4eXsWGSuRTPr8YNeWsJtEkjztaedBewUj7CnoZHheGiYp5Y4UoS9l2y7BrJXPHBAbAprEi'
        b'GXPJuDKZDel0KjAnG091GLXycC5QCAqRYQO2L1oNT6KLM9AleGnUlcBmyLg9VSmPpzQDpD51M7xC0oKj6BhjOvVYJTnwJqlbJkXL8KYvrXLb11iQrzSiolyLFHciEkdr'
        b'C65ggWAT2I+DAWxFZ9A5UFITQz9hHf0JTF8UG490o73WoBZdtNcU0ynHTWcVlglqyZo9C/ZGwWvehXOQlv5GQywKw/SHj9ZEFGJGIm1EUSahna7AmJ0ZQUawzeTMm4Va'
        b'OADeWueAw387OkpXQKAZnNFMKTa8kVsDaDXxyFz4lH8L0dVxDERHnTCriKKEojPwHOyLpYPPEdQ4m7i6nfAITYztopVkiAIUB+2YQ8LSEbRDE0NHiWWZONJos1A7CQ9Q'
        b'uxJfWjDi+Xh4gWvrA3vL56jL4atxFFYos5fQdReGca/6uYzOuGp0xj5kwIpC1wVeQFvhoZyxIGlW4pLCCodnRUy4a149DbvDQ8+6c3QWXqSxlwpKnih0BDVm56vS6eea'
        b'YQe3eZTKAnSeEImOraY9G9aVw7DxaXay2nVCcnIK3aRdSRnW1etj2UmA/7jkBO3aJOAwOtSGetZL4ldgv843y8bEbaih1TEAXcVhMNaMTkgaUoAU56z0wKba1ZLYlZgZ'
        b'q+GpVBJEL8OdNDGO2PEcw+tFBpIXdcGtOBb04ixFQNF41Qvc8WA0HsuGh2bgYM5C+zXpeIALe5bzUAtJI7FeoVZsEzawJzZ6VuaY4s0RFc0ZU6bT8KlCYX90xAoHwKZS'
        b'OgpsnAQPrsIWdBYvej1YnzGFfm5+dhI8Gw97SI3xxRmuAJ0p8mEC2ll00hcL8zw8iyPHRrAx1kIjpuNB1nQV/T3JnDByqkx8aDFdNNQyTpmLReY4bB9K00wiRo20Xrz8'
        b'PNQiKiLGgRrhWWwgqLE4M3te5lyGHnh6FtLmicT5uQVcnD0hgxXcDrsWYJUmbkEG23KxVneRjwrIFwUzK5kalvoVmDMd8DzuRZ1YXQ142ZXwZYxF+6J+c3TIxu1Z/bIo'
        b'pV1yPDypeKJe5lZPco0jODMlCuZWt5jU6uyBO9AlG1LqeJmKVSuYqpSra9FpUrN6Hu2oszPDY41USOhyuqBOVuR8g6X6I3YW8mvrTxblqAoTnPeppSUlUzPlTl4Hr9dB'
        b'yWcOYdzs1RfzeJVvREXoNnNR54k4n8gLnQ8eZfJMV/6wfan7y4tPnN03r+jj75d+51anjngr5KbtofjDXUKfDcmRh1Qnfthe8tIrd/4of1j7ycZNp7+KerdetusXVr/t'
        b'2r158W3vb1yam/Pa2jf2fOXzsdt0dVfae127/1F0bF92/NY/31kxBRjjjqe+Ff/1kZnrlznabe5ItH80VWvZEcU/5FMw+1T+ny/azvOcE/m+Xurm0von49U1r/svlsTP'
        b'b+wSfNgc8pkgZYfF5ryfV7pvW7fmXfNj34X+5a22w7O2d/sP8xcuvOU/Neefg22Fn4qb/jRPV73hPdm68GbFm7VtNrMMu4eD7r27ccaVmSsPXfL43YZd91/6Y0r61Nbj'
        b'72aUaiomJfw87S3TpwHb7sc4f2ndrvHmhd3bkP7giyWp7Qe/9QwvQsF/LJryg+6zw+mK5e/84+pn99o23R95dPftizG1xd/096YKJ2/8p9PWjNKvEyNeqkmMaD2X9rPl'
        b'guX2i/2vZj8OMmq/EBw71XjY/0DoAv7afV8kHatJvxWlbuj06/qEl1J3KO3d34XMeff+H//e39xy9vczsnoWx8/+atdnHW/ftvxDsLPm7tsP5afj31v8ocOMgGNOV0oD'
        b'6oVC9YftHh4bG97YImnz+X38J2UbKt8V7z0v6e//Xeznu9/e+N6HK7Olb6xcmhdffXHRn1bs++WrvzVPfy04+aMdby+U/bJs0zv/eJXtuPpWe9e/fEPXc/9Q7KbO7Fw0'
        b'K+nIZY/qWRffsTx37931H7x3r2XTu/CEuv+rGiHfcu6hnyx25Q+FH9/VZuLGHBcP/MTr+95qTe/LnM+/jvP+bADGrD+9RbF2D7v2SodlcePGuHkbE0N+sXn71o4PXv14'
        b'ofy9oB9X+BjjbdeafVf0QW6frt4p/+X336rs+nrQ+bPKd67ub9/h9Qcfzs1Lix+GZATlfXej7OHQAv0jkWexwwqvDQ/PO+7620B3avS1s3fCTa7mD/d9WG7/+J5LbW3e'
        b'Fd7NFV+sdnH4jPOby7ZGcX7a+j9J3ZdPDV+166D5++39n7QOhX5q/vjoo5Jax1Udxz6cev/n750/PvK5/feh0V91PvqkMOAPX7etrtdeQfb8JYqAfP8La90vvJQz/4b1'
        b'TV+7W797HLH2EgjZGRf3peZ3G/4RYqp837BDHV2+rMjldMHDVSbpm3+atX/RyY8mtZy5n3P1cmiUeU7dJ38qNXuv8zran27p6y6+GX7BflPLjwlBN5f89P6Km5k9Ba/t'
        b'8yj0u107U80Z8r9mylrCieR8PL/3k9e/sKu5taX/z99FzFzacu33oUfOVf7yZRz0NX7S4/L9mb99WPTSoochKTlZwzMWlPTlj2y78bnx+5mXUuu+r/paYEsX/njmS0br'
        b'drAP3FJNO0KcV7nBS5zMhU6PiTMKQxfRbmG4WIDDDDwD+wCwfIkFT1qn0B/joX1mXCFdNGS/cHzZEDL409iofiW68KQ0yAzuQkdxiBCZC+iiogp4OiyHqQuyWzBWGdSN'
        b'dtNTWy5zoIuWDP5P6pbooiU53PKYbEPgQdQFuydWCAEnHuwlFUIecAddXgQv8jXC/LyIbLQrYTLAT7jCWlU6iX54GiasLwcnm5EiHJVXoVsKlhhHfQP9FeJi7LN70L7w'
        b'HLy0J/VQdlHspeikx2N679UvkozLD3j5rHBPDV0Mtca3XEhzi8T6czgrYUnQdthEP7O4XIMT/LWSCd+AWcOdNEHoEA60+3Bm3oy3EOfr5LBh7PPHyRw23GUu4P8vVzb9'
        b'D19UhIznXpuOloKM/U34rG25Oik2au34G7p66mcz5rM2hRlwdt8/tX3qoFOQNt3k4qadYXJ212aYPHy02SZXN+3M++7ebZwhJx9dpT7jrlP4kFdoN2fQS9SWbnLz2r+u'
        b'fV3HhjaOydNfn9YpbDMfcvMyOXubnNzIlHrJB06hppDwU8uOLjM4GcoGQxLbC9rS2jQ66QM3bz1n94YhL/6Qt7hbY1hijEy/651h8g44kteZ1x181zvqQWSsSSAyhUWY'
        b'QoV4ElNElEkUbRLHkKsw0hQuNkWIH3nY+Hse4I54A08/fdABH5MoRsfV1Qy6h5s8fOkOL199cOdk07SZbwhfE75ZMThtjtF7qi5DH270FuHnvjQYORU/CHcIBr0jCJLI'
        b'6IEnj8TTVB+0wx0DAdlGj+xPQ6INwf2sfrYhvF96O+1K9ZuBV2oHQ/JNYaLuMgOrmzcURMiYbVjRvXYwKPmROcffU8cdsQLe/vp8o1eMKTYJP0M86B1NyqkURp9YU1wy'
        b'7okc9I4ZK7CKn6TLGAiIGfSW0D0HF48DIdQc9BlhufI9Td6C7tgRNm498A7CjHUxrOh3MHgOhkwe4eLOETPgE6hPHzEnbQvgE6yvHLEkbSvggyU3wiNtW+ATjiexI217'
        b'4CPsTh9xIG1H4BPW7TziRNrOwEfUXTniQtquzDxupO3OwHiQticzpxdpewOfEL16xIe0fZk1+JE2H/iIu9Uj/qQdwMAEknYQ0w4m7RAQHGoKFZjCI74R4nsdZ0RMOOfQ'
        b'mcgUVN31Eg0J4wzS/rT+MsOy23FvOrwZc3uSMT5/UFhAqtI6c01BIZ0ZD4SRBovTKWM9wboMUwSW2+nc/unGiKk6jm6B0T2MLqXrzjaGJtwJndKfdid02m0Ho+90HRtz'
        b'zj9EL+2ePsCPMuQM8KfquCa/IH1h59p7ftFGv+i7fpIHAcHd1NFQ3XRSvFehr9TzMIyvn45NJp3eueyeb5TRN+qubwxe6vSeZben34mfaRrDGWEDPN0TqA+eQg3Gz3wQ'
        b'JnqFd5pnyOgP7Mm+TQ2GTeu00ZnpuUOCWENR/7xBwXS8/PmdtiaxxJBmKOtehm8XG92FD+InYaZMM8juxWcZ47PeDBqML3jEpjxidc66GqNHePd0kzd/wD/aiJXI3Uen'
        b'MLqL7rnHGt1jDXM/cE9+YiXB3c53MI8DYkYAFZtFmXLm4EliC6lvARU4l8KdPnOpB6P43eVG92hDhNF96j33GUb3Gbc1H7jnkZnERo+oB96+R7I6swZCUm8HD3pn6qhP'
        b'g8O6HV5xO+1mcDjrebzEFCZ4xfy0uYE6azWEbcr/cmhPaL9/H7EqzRXFYEjeBNPJOJBCiiIz9KI72CHEJOBWxB3vSNospxg9pjxw9yYPDsOE4uanvmK80qhk05Rpt2cO'
        b'TM7FJETlERL88gkJHvnUA/+Q3dmfevgS17WpfZNedddNaHC+7NPj06+5G53xpvP7Pm/5DBQvuJu18FN3/pCbz5CveCByxptuxshZg76zB9xnD3mGDwhzBz3zBpzzSAHg'
        b'QqNL2JBziF7TvcQYOvmu8xSTM/OVcPBd5zDM+rYMk3/w7uwHXny97x2vqOfmI6WfvkavKIOj0SuW+FR//dw7bgJSQDq1c2q35K5XpCH9cnZPdr+qr+B22Z3YmaagsFPZ'
        b'R7O7VccL7gVNMgZN6k+/HTgYNONeUK4xKPfNwsGg2bqMoeDw7ujTFaSKs9//w+DJemqEw/HPpUwxCf1UT1h/xm3/22WvBV/J7Q7GdmoFouMNZf2UwWpInNQffJu6zeoX'
        b'DIrTH3HZggA9F7uRoLDu+GMpppTp+vQBQfKdoEmmYEF30fEl2Gnp07s9jhV84wNCpmBbx4A2dwLjTfGJeo5+sZEvITWaPoPekYZYo3fCB0R22PzueAhJ8eUio3v4Pfdo'
        b'ok5BH7onfPosc0Zmc4GHz6O5XGDvMmQfoI/r9jUGJt61TzLZu+63abfRSe/aBz1w8tDm/fg4GoTFfANYmMah8ARjYqYpbOrtUGNY1rdsKimHKIEwlyhBML6yCdRPKmsc'
        b'B41cm0IfzqCPV2GiOVOOaT/MIQdj/4UyzP9yzCa1nqUvitFK8h3RhNi8m8CnAKZes4xDUY4/AHwhRZuO/2nRZpdZBDjHS2BPOJQbK9L8ltC3H0jJz/qABaxKagF7Dcuy'
        b'SsAetqdPA+lKSWWGUlmr/MmPOR+kl6kcLXyUVvLLFHwpGRfnCzjDFiUl5EC1pGTYqqSE+UUe3LYuKVmhKZOPjpiXlFTWVpSU0IxmKmBpLpD61LXPPbYVL1VFPu7bBh5a'
        b'R9Pg9IvaZeSdgS26rOZZwqvwNM5O80XK0TwuEh0x4+K0slVAzZCF7bsGVDV4luvW6dL2mQUo1Xnbqo/LT/3A2ua6NnLzQE7Y5iO3N1RarmDnpAaJ39x973Ot/f5FSdv9'
        b'3uprZFv4pXz9t3fWXZv0j32a/sCk3uOJZ47f6HNDpY6qwQu//yzix9u1ns0fx90q9p9Xff6VtzYXhZ53XjZr46T13GWJvPvzziZUfFUy9fx5x8Dlm85dXvPA4qe/770c'
        b'nWMrLNsW9/79L354pHZwkbXHSX8j/7iwThAQsCxb+9GOU0skQW3rP8v0z3uHn/OOf0GEPjPiaO650vpErX+5C/qNQ7PjG1H558q2JDYKHsZWaft0ge9VbO7XBj+MKTLs'
        b'jDt3fJeN/NhmkbzC/JoJpdgmn7b7W1bibxx2GX+TNfNRpb9l53uHnT0KXxccWqxS7Vn8jujqikL7kZ8m82qFiVceBqS95/zxXIczA+lLnNOHch/c//DajfXwF6dv/3HR'
        b'fUE82n5y+981n91KaZ3a6/mHn9ftFb16RBl7/4fQv5r/fefHKvQz628dtXsalws4zKbgago8AFvhbtSUSwEqEaBdAHbSGyLY4V799LdHOuD2p78/UgcvPQ6gQeDWSl44'
        b'eYmPNx1PfqPEKsEP9nHQKw6ogZmpcf4mFTyPrjtm5ovCxvYnDqiNDQ2LFAIPxgIt/u3lfy5RJ3szfir9V//cH5OhY5uR15ZVlpSsfdKic/N/Yp39GefmEcDGZYRjbuk2'
        b'ZOfYFtO0Sue/c32nSh+jLzsad3Bt9+wDm3qCDMp+/x5N/+ye1X3i19LfdESZd2Jy77t76mJ0ZZ1xBy312UZ3scHN6J44MDnf6JY/MGfuwLwi45ziO27F9135escOxYB9'
        b'EE5N3OdTOA44Oreltbtop33PMbMM+96eYxkwYm3BtzJZ27W5jrBJy8NbV8W0QgTd8UxLEt9vxrRSp98uolsPaAwuadEYdIvGoFs0Bt2iMUgLp1829hjHnGl7+mCs0XZo'
        b'OMYbbccmYMzRdhqVTmFs+s6CwbZk2jT2aDsipt/sdpHJwU1X1R3/ouY3dhhwwMIbp7aO7riH+e8RzywA9/r+YJ9LWRbj2MH8swQrov2QpX2bShfXVnPXMuAH1mq2pecP'
        b'gFy/ZQOrQHKxH+GQ+5GV5rj9mEVZxnStwTHIMoYefEQ6fhyR8ijLLGrI0e+E9YBoxiB/5qBj5oB1JhOZdqa5p5uB35g5pXuwmcjkPMzCvvO/Ly69UG2dXxCrnsYr8jnB'
        b'U2Ullq6aMhqsBBRlT2KV/Xfk8p/GqqNm0aCHN5ktO+QRQ6nW457dX26Qtkyx2prqnn5ratxw59ysgdWhrxjc7QdP5iaXvfHXrQ0juwNyUusOJLxe8Xnxuu8ffvBR7i4f'
        b'm8cn7b7Lbrj+109cd1kny4745IVOKg5Ys/Dea0uySncVyKKiOJZz/hg262Ezz7n4fl3DUcjOKz7zZbJXQVqITLDpwu8veh3+/VSBOfO6oB72K9FJ1EX/BloBfWJmDniw'
        b'l4W64UFYT7/HWIG0GTkFIhx0MEiBGl4RsbAPus6GR4sTmFluonOwHzahQ8gAW1Er+SwXtsBWc2DryPYtz3xMhOmWsoT5RqvCHNCfaG23YN7+HKTQnhmwM2fcz6rxBCzU'
        b'5j2Vfjq6CF+BrxbmPPeza8gQTk/Mhq0CYTYXUAn4yQDp+EgnCPx1z/h//AXHC5UycMyXPu9JX+hVZQqZmvGqTIv2qjPx5Z/14FtPwHUy2Tjfs/E12vh2rR60CaufYeJY'
        b'NeRuzh1w8D+ReJcT8THH7yOOzQ9m67jcmB8AuT6mryNrecDaub5g3Nc7/GG2XKoY5pDvR4a5ak2dXDrMIYVSOI2UVeAr+QZgmK1SK4e55WvUUtUwh5SRDrNlCvUwl/6N'
        b'n2GuskyxFGPLFHUa9TC7olo5zK5VVg6bVcnkaim+WV5WN8xeK6sb5papKmSyYXa1dDUGwdNbyVQyhUpNCseHzeo05XJZxbB5WUWFtE6tGramHxjDFKoN2zBppkxVmxgf'
        b'FT3MU1XLqtQldAY3bKNRVFSXyXBWVyJdXTFsWVKiwlleHc7ZzDQKjUpa+dTt0G+gSv/tH5/PeIvcsQv58TpVAb788ssv/8K+wo6ilGziLCZeH9HX/8R1EEf5mqVZmgd4'
        b'zYOXFsT+yWLsh8eG7UtKRtuj3uonz6qJvx/JV9Sq+WRMWpkvsFCSrJukqGVyOXaz9NrJEdWwFWavUq0iVXbDZvLaijI55uwcjUItWy6lE1WlfEwbnua0wxaTmSQ4RakE'
        b'TNatysKXETZFUY9YHIozYg14NvXm33CyzSjnkQXWwNLhnoWX0cJLl33XInQgIuW1EBRmjMg2WdgPWbkOuEkGrWIHOLFDwL7N/QPgST/q/wMM6vxd'
    ))))

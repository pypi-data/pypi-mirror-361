
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
        b'eJzVfAdcVFe6+L13Cr2ICCiCY0OGLgOoYAEVBYYqttiGYRhgZJjBe2dEsYsKSLUTRLEL2BCwt+R8qfuSbLIpGjbZTfKyye6mbLLJJm6yyf7POXdoivm/8tv3e8/5cR1O'
        b'/fr3nfN9l39nBvyT4J94/CNMx488ZhlTwCxj89g8bgezjNNLjknzJMdZfkKeVC8rZ4rkQthyTi/Pk5Wz21m9nZ4rZ1kmT57NOOQr7X7QO2YvSZ63UFFszrMa9QpzvsJS'
        b'qFdkrrcUmk2KeQaTRa8rVJRodUXaAn2Yo+PCQoPQOzZPn28w6QVFvtWksxjMJkFhMeOhvKBX2NbUCwKeJoQ56vxsoCvwjz/+cSLg5+NHBVPBVnAVkgpphaxCXmFXYV/h'
        b'UOFY4VThXOFS4VrhVuFeMazCo2J4hWfFiAqvCu8Kn4qRFaMqfCtGV/jl+1Ok7Tf5VzLlzKYxZfKN/uVMNrNxTDnDMpv9N49ZismDEd2hlKTreqnH4p9h+Gc4AUFKKZjN'
        b'KO3Tjfb4+6sGLnMTQ77lhLTHRzPWAPwVbUe74CJUQ1VGahZUwlY/qM1QQm3yosxQOTMpUQr3xsFeJWv1xYNhBzrpKySnQR3UpEENyziGqZM51IH2TNOxAxjo0QtCOqEC'
        b'i+nw/6FCvocNW7ZSgrHlMLYsxZaj2LKbORu2hY9iO/YxbONFbL9h7LhXJT6YLTnGL+OHM7SRYzjH9zhKglRQh4mN/yh0WDBCgrmXk5PaPkYrNs53ls71Yt2xMOYY78WM'
        b'YNoYoyNu/lYzUvqtB5NUIPlw0l+5q5M/WfIFa3QgK5c1sh12TNK5tJzI93huZTJDm5dM/avbfjdW4b3wA/bnpcq8GUwPYw3FHQHZ0ICpXh2eFRgIuzEHToQnhcJu1LYw'
        b'MCUN6kPCkkNT0ljG5OYww2XqIOLa9WIcQYhLCMvkS/rIx/4i+R4TFrvHyOckkk87zJUZvXAWw0TkGMcr5zPWENy4dM5KDHMN6kKNwWqogarUrKTkkORFTKQ6ewTavxBV'
        b'owNMgcwOWhKWWb2IwLRPR5VwkVWha3gD1MasQefRHbHrKHRCBXoanVKhbtJ5hCkyBVo9cdd0OOICu+C2KpII6EFGh2pCrARKdAMapLBPhr91LwljwhaiqxTYlSOcGE/n'
        b'VQzjnhPSum6xyMHfaD2YCRPOcZiv05/jHRhDyb75nKDFPe/v3vRZzvK3/pizOj9V+0p+2N5AbZL2zzkeusJ8Y+7nOSna1/KVC5K1yky19oK+lW0fXvDHvBTtcmavLklr'
        b'1u+V7j7dcTZi9lM1ytGKxbHfzH4h/YzrvIYbzzo3j2QWpo746KFSyVlGExTLE/2XQY0TJpUyzRoaBLvDOWYEqpDaj2UsIwk+O6GJUHR38lKohxoJI53Gostw2KBke7hA'
        b'pVLCE7YMeGBkmB+8pufz5jK9SZEvmrAwodSQb5nZ40jtkyZPa9GTcYIzYfI4Z9aZdWft2UCWl/cuoZT0yNZqjVZ9j51Gw1tNGk2Pk0ajM+q1JmuJRvPYvkqWJ4LCy8iD'
        b'rDKerO9K1v+9OydnOVZOn9RIrEpENcFJy2F7SFA6qs3A8iFjvGCbdKQ8aJ6Os8medAhBxpaiT5A5agckWJA5KsgSKsjcZslQgty74GBBlqdbsfoy9mURsI9NwsIeyoRO'
        b'h11WYh/ne6J22Dd1E9ancCYcXXS3EpMFjeOhDfZBxUqMKBavWAfDK/JXOCEM9x2+c+mznGXPNKBG1N3Qtq+tvHvi5aRxO2+UJzezL+UTUXLO/yDVjjlUaz8+94qStVB7'
        b'eRC6NwQvQp0poVCZnJouY5zQZQ6OwJ5JNj4MxWBK5h4nkZv5RrPWQtlJZJoJcmalmJm8Yx8rpZQ1PbI8fa7BwpNBPDE8Sm4A+zie+KQBPCTTg/t4eH8QD4kLU45F14KT'
        b'RAZS3+A9IoRlfIulaM8s1ECVdF42uipYYiKkDJc7D91k4ExZHO2QoO4E0sEynD4VnWKgbUmRdQShxuls6CA9EoYr2GDHwDm0x0h70LnpcEGwTCGLmVToDLYbycOplQhC'
        b'5yWkAxtuM7TCWTJpd5TVG3cF5kkF6I4m+6DyYNjKQBfqgG46De1BJ2bQXhnu3eG6mYHu0Zmi3bkFJ1G1wNOJZqjzYuC8xt+KHQWTNhwaocs6mYCBDqDrBKsuOO5LtwtC'
        b'XXCT9mJY0ME56BpeUz5ZXLMJ2hwFQUUmbnEvY7A5vw7H6DTUFOxMZ2GkUVMoHGPgujOqopqCjqNrcIH22uHew9CK9jBwA7ajs+LcGmskdAnOjnhHuBKAGtgodBM3EpLJ'
        b'Njk48ZT66AyUY2JeQy2pFBifyVFOcDmadGETfVPDSqAd70HpfBidmevkGElQh4MLNayDOwaFEqwOzts5wVWKO+zcgs6ybN4aOkm9bIwAXaWuBIjjqNWDDc6FNhG+cl+4'
        b'Jzi4QAdZ7x4qV7MxaFu8dRTp24+OwwWnNVa4ip0jXEZX4BY7EdWgfSIkW13QHsGJt5CZjZPRVda/wIdCsg46VwoWuOZEemrHw242uATqKH9gP9oNhwRXF0wQiQyqoIqd'
        b'gRrhOlXeMEdUg7tcWUbikJXLxi/0EGFsN0Mlbl9D8LoO26GSDYtDu6ikrp4Ch5xcSlCNlJGMRxUObHyhB4WBh4ZhREKw8JSgK6iJwVyq19H11KjBEctwlJzh8jFWR7B4'
        b'w210iU7LmoUOESkgMlfuBq0M9nDdw+i0WOzuagS4DF1uhI4XUZWejZrqS6dtRHvGCnDV1tUOF/SsaswMpYJ6MUPCcDaKYwK3Zr1TvNQnNZY2/tM0gp3KMT7MoreKGwte'
        b'KqaNC4K92OkcMzVT907xA955AW38NTOSjcd2Ip59ftPSlS970MbnvEexczlG0TD2pU2NK0uW0cZJ8/zYJI5xZ5Qvb2pUjxDXfC3Qn03lmIjXE3o2+WQfXUUbz89RsJkc'
        b'Y/9V7v1NjYtCx9DGYVnj2IUYzg+mok0PmC4ZbfzWdyK7FMOZk/7apqUpSoE2Lt4wiV2B4WxIeGmTT8D9YbRROUbJ5mA4n4lGgs/MWLERxQdhb8DEv77mfeHBeH8R98bw'
        b'ELYQAx+R+LrwQLrYShtXhIaxRo7J2boehMZx+cNpY7Iqgi3BGCn8XxOWCs+L0ycnqVhsTzPjR/UIDxYa3EQ0jdHsOozmsdGvCI3aGhNtjCiMYTdyTEnHvNcFn+gLStqo'
        b'CJnGbsW458x/IDwwXfKjjTetcewOjknq0Dwr+Cw+MpM23vecwVZigrye+qrwoOj5lbTxbulMtoZjCrfm3RceLHkuizZm6hPYBkylzBlvCEvjn3akjXOzZ7P7OWZpZnqP'
        b'sDS600Ibfxo5l23EpDs25YHQmOn4FG3cnzyPbeaYdSXTMZw5h2bTxlPTk9ljmJ7uW94r8nFNMtPGeksa24pJ9/pMKGqUt2lo441x6ex5TLqG6b8uWjozSsT9e00m24FJ'
        b'F7/5naLGmbJptPEFv2y2G5Puq/TfFi1VrvUXjfol2BEsODkSvXOeAeVsfCjaKWoX9nONTryrC1bWYagtg50xzUlUyT1R0I0N67VSQULsRlEYGwz1+aLxcvfFxgZbbqL9'
        b'+82omR23Dt1TSkVCBb/INkuYdZkz3i59YExYQhs/dX2JPYb9uLvne+YHE4tEGavP+Df2lISJ/yrqZbPPrL9m08blmlfZVgmj+GDBm+ZG77jooaPqKIYRj23kuMLky/4r'
        b'BxOym/yxgCQg3TqGaMqoWag6Ax+h6qEqOS0MqsI5F3SW8cqRTsLx8yEK6qY4jkY0EWubmdMT48SA1rjcAasnExEhrw5vsngzok08txwOqcPVmnVQl4EjLXvYwa1fALtp'
        b'5wToRvdwtN6NujcXShn2KQadh4OoUvQ+e9HWQFSLuoMDcWhaGY6jE+cCiRu6jW5Rg2rvgg4WoQbUhQGJZWJHoHaeEIqCkjhfSpBURAS0j66bNUpsXBpjx+CY0z3C68VZ'
        b'an0WQ1fxLIDDqghmPFSTHRntDDfrBLJ5oztUqPHBBxNBix/4QKlG9eHJ6EIgyygsMtdUVEGlCB2eispVUUwhIgvsZ3KL4BoNUbC/OZYfjM9OhaX0MIqPUslSZrhSAjVL'
        b'sH+iTu0Sugl38CkC29sj4klCi+rpSSINzkOHCnVKl5PDRAtjDJgubrcf6saqVMxozCl0lClAVegGnZCoh7sqlbw0jbhtZjU6hJ6m7bAVXZukimFWoFaCFZPHFlpHUweH'
        b'yu3UKQSudMwZ6EQdmDuuJZKprhrRA7ZACzqhipFOhTP4t6cZPTStsZK7BHQKH5IaEHY56lQ8Nxxqg1nGaRn2GsvRWSUnbvv0FNSsiuH8ZpIQg8mPwYEtaY9F3YtVMXI4'
        b'n0VIh+FvllBJ8EDHsGepxicR1GJJkzFSfxadQG0yEZS9OIDpVsWwqAqrBGpmCpdiGaAB7AU4AGfQCVMw4QxUpaMLUsZ5hsTN0UfU/m4/tFOFrjKp5AR3jDFiceu0kqMN'
        b'Pt02LITq1BQBXSInGwncZdHhJXDbiinIOMJt2CekJienkTuHmuDxcMB2ngwMUwalhSlDOUd0Wo9DmzPoVGAgavMKVmLWnAr2RPu9RsApb3SWY9BuT3d0bLHR+PCf//zn'
        b'GqtNIuVRGVHu/gzlJlQHssHpoeiAd5KUkcazqD0vRukpysbdibBdcOFRwwgrsUJH2fFl6CClVRDaie5Blyufio7RvqusEtrQVWq87LH+nIQuFz4ilPbdZYPRbThB++Bp'
        b'HJMcF1x5Hp2xUgPGjvFDpymlssaiCmGNFe1PcCQB6y1WkdMb5V2fymH3X+qCMBNkJGhjx8LR+bQvG5pX4dgLq/H2hS5kxctsJIsjS4JcnEOAk6sTqpWhemxhl7HL0YVN'
        b'ImpH8jcLFkccKV8tJfHhHXZ0Kqqmc2KhIxF3GblSstE2VhEN20TQt0YUQJeFh/Jp0E1C1bus7xLYIa53B6rcBOi0oOtaOcNitYB6j2ix6wp02DnZu8RBMz5SSKawSXAF'
        b'btKuSDijxmHnGj9U60wgb2InbcBHB0KLRLic4uTqDDdRBz6qSOLY5MmohcLnsdoJh0H8ptU42pS4slOgEV0T4TtZnIN7oHM9aiUOZRybgO5CDZ00OzRaWLMGHXqK7EMi'
        b'SbjqS/dxx0HxAcGRT8FwEF7tZRXBDhQ4C9xyc3LkcYjfgHskHmwElvNr4h1D87qF6CC0wD5swUOYEHTSjQa0ZTNRE6p2c1yzFpuOUywjhYsstp6HUHfvsaIemjBWWHuP'
        b'2bDKkRqqw30kwjmsVcK0iyv33kt/L979hYK1979LqIu3L/ma/VDzO3a3enhWZqYia8XuFVNmK9RJDwMvNp5OSAoLDDn6THrCnqDo+tnPSz4e21j4s595X9Hags0/vnpN'
        b'VXQ//7sFN3Str358yU6ORk/f9VNcxN6Xtzm/a/fuzht7Lk6Leh19W7P3pe0z/RJq79/792kL3sld7+0Xsi026buWHw6W1WqNWaa5nXxXXq3+zXGhlmj/ouYjkSkVU//+'
        b'YWi1d+ifq/atm9weEvdDZuNfD1y4/v38km/mv7S3YUvKzHmdKyZEH1S8kTL2tTejq2Yqfwx4Y3WOR/KWyPKH1ypXvv8peunlPWUXEi9Z9Wd/FTPO17Otw2ms5pPR/KLf'
        b'L9r1xaZ127TnHyz8+VTYcj+nS8GfT4tYu23R1eTCw+/LpbNiPpc/s9b9k3dWJf70TuK30ex6wwZ7r7eKTQcnr9hpvq7iev7msC2j4C1DnfavbxY0Ryu/uPLw38o+rX14'
        b'uGf/JKPV2vzSxia7+hW3dJ+++dlYu9/VR73t33mxoue9b1/88DWt64jCn3QjhJ/Ondr+3en7q97K2XPwTt2UkX7dU79YNPXsLPsfJrs3A/pD3FN7W7/7bJ/S3uJPnedx'
        b'V6jAlqA6JB1bJqjHJ2AndI4E7zvhpIXIxLIkOBMclhwSpAzD3VDFYF/jo5CuyttIj//LYGcgud3BkrEVbe2738GnsBYLMTQBsyzBYdj+VYXgo+1VlpGjOi4Ubs2gk7F4'
        b'X4LD6pBAbF46kqBWzTL2ePf1cO4pCxE4GRzXqZPTgtI2wXU7Ri7l7GEvXKaQw1182riBz+9pliCyeBU2rfUSZnicBA6nrrFQP9c2oVSdETob7mGdWYuVaRc6qbR/9Dbi'
        b'SQ+l7Mn9/TcYHuINhoXXmgSteItOLzJKSIg025W1Z+WsJ+vM2bPOrCuHv0kccZsH68qSOyt71pH+eOKPO/6/94O/c67id87RTs6S2Y6sF+fB2XNSmRTPdme9cJscf0bh'
        b'dcl3V5Z3ZvrvvpwHgjTgyuTJWClZ3qUXL7rUHKb38uSe58DLEyWh7a4YdNx2exKuxCHAYqgKTk8NE/kQLGfmo/N2aP8CvCo1U6nKRHVyCA5epAzm9TnsJmFX6KDg1KU3'
        b'lpwrBqfkLp15/DY936UvWOWeGKxKaHJE+rdivKijYsC/TMItQaEdnOCgWZP1JXpF2sJpUREKM0+/RIYNmjrol2SLgtdbrLyJrGU0CBayRK7WVKTQ6nRmq8miECxai75Y'
        b'b7IIitJCg65QoeX1eE4Jrxdwoz5v0HJaQWEVrFqjIs9AGablDXohTJFgFMwKrdGoyE7MTFDkG/TGPIGuo1+HuavDq5AxxkFL0StPcZTObFqr5/Eoktexmgw6c54ew8Ub'
        b'TAXCL+CW0A/FekUhBo0klPLNRqO5FM8kC1h1GHV97JOXCMU0zNPzGl6fr+f1Jp0+1ravIjDBmo9hLxAEW1+Z8pGZj8/B/MjJSTeb9Dk5isDZ+jJrwRMnExYQNPv3m41b'
        b'jHqDpUxbaHx0tI1X/YPVZpPFbLIWF+v5R8fi1lw9PxAPgQAy9OBcrVGLMdCYS/SmWEpOPMGUr8WEF7TGPPPg8TZgikVY5up1hmIsChhTQqihhuqsPKHQ+n5olsCpQt5q'
        b'GnI0uSuPpU+8plVXiIcJ+Ddr8ZOg1hnNgr4X7ERT3v8BkHPN5iJ9ng3mQfKyGOuDRW+iOCgK9Ll4Ncv/blxMZst/AJW1Zr4A2xe+6H8pNoK1WKPj9XkGizAULtlEbxTz'
        b'rRZBV8gb8jFainDR6irMJuP6/1GcbEbAYKJaSgyFwoaa3jQUWjQL8QtYzdYbtYKFTv+/gdTAUCG2z50N9EV99q7ELFgeXcAmGXpBxxtKyJQnWW7Ca70h9wkQE89l0fYK'
        b'1xLsufBWRuMTJMy2ab84Dt7ryaL5n6Y7r8deFCtdrAJbGTxyAdzWFeWKGww1ntgijLymSD+AVb0AYRIY4bYg6I2/NNWCHfwTiGhbh4wYGtjHPK7aasrTm4b2mLZtsY8c'
        b'wlcP3hiP+aU1CtYO9rvzCbfhVL5FwJYqHwcxpHuoiSU8ZgC2edqh9820detNoel82JOgH7T3Y3AP7f9tgvBIDDBo8hPjAXGuAW899MTk2QnpTxY7jZk3FBhMRKQetyEZ'
        b'tr5cKpBYgRXzeH1xXukTdX3gyv8BgRaH/yeNSaEWe5shTd58fS7cxmo9hE34HwCMqAHVM2LnBsG1EPf8srKZtMX6fmtni4sVgem4eUg5tfIlNC56bMZiPV+qN+URtSwr'
        b'1euKhpot6Eu0sQMDa7zAgKh+iBnLTaaVsYpFpiKTudTUH3XnDTwHaPPycEOpwVJIgnQDT6JUPW/QKQx5vxThx+JDq7aYmE0M08LCR8q9Bk+MtZ1zYvG5YCjPMHh0X3aA'
        b'nOS8HssOJIl1Nz6ptpt/rwJdh1uyeLMeGSoTLzfzY4oivPzEy010dhZqQrfgadSFz7VxTBxqnktHv8HKxXv4tas2fJ08gRFvalvDZKpIUu51zFZTsxN10HzEGNRQHBzk'
        b'Qw6qg06pY8fIRqHdK5TO1olkt3Pzx0F1eEpyKNodDldgR0qaOjQFatXpMmYy1MqD4SSqp+uhOriKzgXb+tFV2E/GeKCjEtQBJ8aKt+MXs+FY/+34alRuuxyPhhZ622YP'
        b'lWv6br9hO8kH0RvwkUbaDVeVuLE6GGrTUkK5MXI8/gaHdsPlaDG7cB1thW41HFiFt0iGGjU+iUN9eBLUSpgxHlJoNMN56zg8cCI6HqruG3MKnSD1DnVQRZIhE4Jl04cp'
        b'aJEc3BMi+obNspJB5FKnPj2NZZTotgw1wTa4Q1ecDiehrm+s0YVsTFITeOSEHFk8uuRMieQE1+cGh2Hy1GaEpaRBVUB2iFLO+MJhKToJ9RNohsOiQRfomDY6LjkNdpNB'
        b'3iOkEfHosJVUvsFxOApHgp2kQ3LPDw6IvC+Hs26qSOk0qMe0OcTkodvouphq6EJ1aHsvryKKB3DqnFpMNNSnoqOqSJl1KU0oFDrAdip99uh2JGyFW7DPDgsrEwH16Gkx'
        b'rdQFd/T9rFWqbJyNhOOUdTHQOr6fszVQZ+Ns0UYlJ96knkXnZqsWpaLOEjnDpmJZQUehUkSkCa45q1AnE62h6Zki6EZNNN2wvnB8nzigVthjE4h4mVJO0UhYvlo1c7Sq'
        b'RMKwagZdgB2onG5mNnurUA1sV0GHjGEXMKgbTqADNHO1aF6eCq6HqXg8J4NBl9a5Uhi80bnRqlVwUAWdeMZiBgv4xWHizfGFTeicSsVmz8HfTzBFqDZHzEJc9khXqWTo'
        b'NGYqOskYUSOqpor60WwvJoQoavr2ZRnjXMSEGToYEoS2wymBZZhEJtEJnaVjHwYMIwWmUyPk/uHnfUcySomoCO3LhpHMSS3NEsGBlRjxRg4dUI8RmdEwarM6LDSIKGop'
        b'XEYXpYzbYokR3UVHKWiR6JJETSu0pMnQLmVRy+xAzAYK9Qm0c7YqOayPZqhzLL2K18EuuKtC+5UDaNaBGURqwubOgQY12gannqB3I+GYLYHFoYta1Wp0u4+8S3gxG3Ii'
        b'GW6o4LxnP33RPdhBdespaAnrUy2omPaIsgb2pgzb0PERmA/CIhsfrqB71IaVoIMr++anjRhCjRfCWRH5ZlQjITzbAy0i04IDKYL5yjX9EJxCzY+qdwu6TdGbj1l4R6WS'
        b'RmKdIfnFwgyxVMDTz5XBBtAnYu0i3/iUuYzSk2K2HC6g3erk0PQwrOOBUIUuBYp3tr6oQopOj4DLYlKtFVU4kspLZWiydBycYBzsOFTni/ekyZgbmpE2ZmIWtRJuMnCR'
        b'2ltsLI+N6pcTdBxtswlKlp9okG9OQmeCU0LVoUHppOaJFPe6FUj06Dp0U5MKR4yTxHxtb7IW6t2hkiYEfVOlaC+6WUoHhsJl2KWGTmHQ4AGZXTi8ntoeOB6HtvWaHjgI'
        b'rf3GZ+xoutQY1DxStCSoLjwFHc3sdzlBOhk6h/b1FlldnRavDlfTDDgcXComwVcNF91RJxyDFpIotqWJp0NDX6ZYniRifwhOQ3m/0cossBktVBkgVjMdCUFX+qzWlmib'
        b'zXJElWISvhVuZpFkJ810yhJprjMIm6ZA3Lk4ER3tIz2qQmfGYpWA3amk4lNN6ByJDsmTLZ50I96e+K26pJCUjFBoQyfkjJOag6OoNpB2T0UHnupPxTpDtZiNRdWR1DbF'
        b'Gx1ojpckeM0bSIoXjjtTyYlDVXN78/w4BqgSc/3QlkndSAmp+CI1Cegelvj+ugSxKOEWqqNUXoPpfcMmYOgMukEEbClWLcqBrQlwslcyQxeIghm/nhZbFs0bhfZJnXCQ'
        b'ks1kQxe6JNK8Bs7ADpvIoW6nXomDHXAS2wg3PGR0FC/LstlBuBRnS5tPtjjx8g1Qhcnehq0lEQO6TfaoGYscYJ9Y6Imtxj4qZaMwUkcHWMircMkm+SFwnKpk60R7W1mF'
        b'vaNjsoERxf0QOjj9UXlfja73y7sXSy2Fn/MW2AeH7DZCNwauntEUwgmq0lAtQdv7pVdIeER4IyZQc+8LzY6oK0IiC8bTWxnz5OHWRQTNU6NDBCxRUJuclQk7xqPOiOwF'
        b'UEnrxcNCAzEbg2y582wsC1AZsjiJVJRQ2chKCiE9OBJQL8qEWimD7m0YhmpTMmiifJnCFkuufVf2+xXTGFFJnk6D06IE7J7+qABYMjA/qPs9uBp7ji5ocIoirjkLOwVh'
        b'I+1RjsFS0lWKmqNKWOoSLsKF4VZSvq1fA42wLzcAVSbDHqzl+1HlWvyoRbvRhRh0UYY6cxdYctGVaBYzSf5UIWoU2bwT7QtAXdHQ0beipyv2ed6itl7yxUoSvjiTlkbI'
        b'NVzQKqyJVFHr0C6sQTaXxxX0ejyhmPpDZ9ToMEAYaobZZAH2JooYng3IQl0z8/rwg3tQI7JzP5SjowNDNmhEu/uDthGcSMiL/ugIHdVt/0jMhlmyTSmllnolOg+dKmiD'
        b'hpg12P2lkBjnThp1HHMwlc6qouRwyZPGavqoTNEjVS4KVKHmaVFrMTniiY9rkYm2565qHObJXtgZBR0M9ZjE4h1VsnSrJAz2ARzm7YRdUZNx9zwcNyXEWkkiacxCdNYJ'
        b'm95qLDnV4VCfDR0u6HLU5MykXsFbELp4QVJIKnQMlics0S2OOBY7CzvFwGc/urQabR2LzskZZiOzEQ54UUZNRe3Yhp1bAVtj0GWO4bxwuMJjg0HDnLp5kikL0DkZw2xm'
        b'NsM21Exfixg1HpUL0BRCi+UXBCaFBFHtWzJo/yWhdphlN0qtU/EMD2ugU3oa1IYudkY3bRoCVUuSUhYlLRQRQm2ZUJkWGpaemiHDpybocEQ7fYttcQiqR8fGhc6hLxWE'
        b'MWHQjflN6zz9sJjtQxdk2MN3ktIOfAIKRAfwLGq8Dtijbb1ShrriesUMDuPAmsihyQ819wtaLlTaBM0tUXTku6Ix4btK4Sqp6pgEt+EaG4Ud5w2aQBTQ/owBHsMXM3QI'
        b'j+GAzooye0qPzgtwtcRNznAzpFDFBjiPpLssQ6fwKcvmTdbDNpszMU0WRfVeVviAkGNL9MCIY2wkLfYyZP/ueUaw4K+qfwZYF6bVey7yvPOXk+032zfk3zys3TVvtHyu'
        b'PPOZ+iz35ezIKTs6tGxAg7swPuCA5fNRkSP3fu+he/FU1HPfujUmHljzJzTRySss4GduyQstH7iV/Gn9tbJdyc8sbP/d+k/v/Pj1l3HXUrKz0mY1zv+46uXg200HprxZ'
        b'+ONvf2N8Paqs4w/FI6ctb68KCzvU827VX995N+XtHW90rAowN79/e8Yq2bl331q9eve9rS6+V6/cNW/8WNdyvfHkCu970xb9Y+GZ9DXTj1VlPFzwcWtn+tvsxNTwWfWV'
        b'+47UVdx/Q/mw8NkXL6pzWlwdVnivkH+pMd2aUF+9ZcX2l75Y9v79B2+O9LgrzBl15Tl5Yfv8LZA/s/5se6P32oQHs55Zu/NCyuef+L/5fZl75wLJR5svThr10P17bnnA'
        b'M01usulZt6/rPt5R8fzP6q9v7mhd8kyo07WJ7w0rOfusC+/y5fwP67Z/Vr7BpVn5s+eXjXndrt9Ztd43qlrX6b2+HnEgdmnXV199fSRxTHpn5LGg9g8vT438Jrdg0nJD'
        b'epdz/cXnz8356GhG1pteLc+UwfmHntNOtz778oryDZLoNJhq72/uPPJns6nKtbPj1/pnx7f8Slfvu+bdVZ+/Gnroi7/8qqmn7OOP4n776TOW777/6TevPExrnv7H0+MX'
        b'H2nzP1SqfO9L48o5y3t+/XfptehPe/Y1/PZPx9/zvvTy35dtnPdJUVp30Cddr+9k3b54uL7m07ljMsdFPXAcNfqnuqZ7E6Pv/SGq3bz1HfVH1448NfvA3exXN8+s/377'
        b'g4m5S9CX40w9nvcOfhH0YekzRfcyl13LvNJwbvZOSeeV2XfZC287xvxFvvLrDaqfbofv2eLlcv4v576THFMt/SnzH7N8/SR3J6wrfSvRdGjl568sKTuo+Ty6LCvti/w3'
        b'94w5Pr54WFnMH4KveMT8od7XK87h3z1uO3+fbv+PZJ858785W6mrPnzpywd3tsyr9F487JsPEzLCV8v8Vr/BL/TcOyLW82FMiVfEZ++99skXEZdiN3qdNJW9W3qt9N9q'
        b'Fo28FdZtnvRwyox1f96QUXfz4mcfnvnaJWhkQ8Dvv395peXp0y8K6+Utpz5WxoVHOt3YlDB+01+2Ljv1aUFKQs25uFFTfvNp0d5vYr88/vz909k//mPk1OXTvb+Ux75d'
        b'1zL+o+RXYjLLC78Zu8X/q4jAkvGzF7+2atycObOPdLcGBx3NvfBGvcuB0Zf8z/923YgUt7+t/27WlpSbc/50/5/smj8ZOyvMSlcLcT1eOGi8SApFUDWcEOs5iC0MxW4F'
        b'XZUmqVGrhVisIti2KjgoTInVmZkHdxiHpzh0el4ZrQhBnQ60UiUQbvYXq9BSFRyEbaPvIg1bBnW0GqUDu7qqEFs1Cg5JaKULugPdseqQQFqIUoAn01oUHAXuod0z3aP7'
        b'y2TM63sLZUrRSQsxNZu0qIEURIjAb4OKAQUpqHEt3R9OLkHNwelpISlQhz2MI97hBleKWqW0XmVuKdSpsQ109A3HbkJeyoW5zrKQ+E6KcIymxlBRrPDBZjfBzC1CUjAV'
        b'7RMXrvGZQqIFfKZr7IsX8LA9tAYH6v1QbXCYEjXnEMJhrM9zKmifLWK9S7op2PbuDrqG7vW+vzNnlVhn0+qdhQ9LNerIABx3lfS+4DVdKkHXUaty+H+0nOa/+FC6/PfX'
        b'eex9o2LLtKgIWqYTQipQtjBL7Vmp7eNKS3LIR8pyrDPrwZFvzqwjx7FDfcTSHjLehyNFOmSkDynp4RzZgR9xBVdx1hPWEj/2nCurYOUceQvKnfWRuLOudA8p64/ne5Li'
        b'H05hKxci70nh3ThnzplCQAuG6E74hyNwk5qdcfh3OS0honDgWXLOkRYgObKj8Xwv3D8KryjF2PZD7s6JpUrkG3l5imDAkyNLem+NkZTcIA+oLfrv80rJ8u693KJ77SVc'
        b'Ik3MVuarCQOrkMiZToJV+bKtCgnqQ3EcBB3rcQQ4qkQCN6AGbR30+hzhdTxZj8RmevLKNbOMy2OXSfI48W27Hnd6EU6LhPhEnjfzP4wRr8ap3PC2mh99nkJrUuhJf1i6'
        b'Utpjr9GQXIJG0+Oo0YjvVuPvzhrNGqvWaOux02jyzDqNRhTG/gdFlJzs6kn9JGmy5+jhzAnOostOrnDN4uTAeBMUQ3mb8oVDi1yGGtE5JTvP8BuDTir44MnVHzXNqL+R'
        b'Dpnuib//pmt43LvhP365I/rzH+/OafjjQ8Zx9qGPXko75fnBru3y5WW/TvpHwkyvOEXUq+/FzRcK7r73/Z62po0T9uj+FvNK2fmjSVea/vTapRdem/7ms1X5KwJ/vrFC'
        b'3fC97Ms5n5x+b+mdutlV3i9n/D0kYKWyM3JzYVZl3id3K5O1D6+NfbkoY4l1Rqan8nnTiev3p30h8xrRfvnQg7da3zyWXB3jt/Hmt426ozKvp3Kfnhl8vvOFWF9j5/Mx'
        b'cZ93vjjTbjT/3NfdLUnpU/9QI4SdWZtraLsQde180TaYuMRwUTfqTE7PmcYAzRZ16G/WZx1acGbv7852X/B7/63QL+z0puu1739+yE07qn57nPxyjnt7UmLksMpJHz4/'
        b'S++yeM1T8UqpRazi9URbccwfRK7Z2akMPgWegUb6CuvmtBAnNWrKfOwN1mK000IuxJaiExOdgkicegE1Eb/UN2wM6pLCJXRlA7WVq5WBArqQlB4a2FuOOAwaUBM6IEEd'
        b'ppFYtqmIe/wLraWcRrRPflAriOXVaNbmaTTUBMYQ1fAiJikKmx1SU0iqDN3t3e0GGTCZzThJPDPwyC3MJmeW9+4VY6w6HJbtfksw7F+DHsv79CkN2ZwwVqxQ/DxsoG0g'
        b'EQW6hc9lW1E1udQgL/7DKezJq1C9HeM6UuKHymGbYbcxmqN/xEDTku33wmTX7fHuu97Ykl/qYsk9veuD47dRc+dzS88fOW0JGLPB6Xrbc0vudGS+fb5+8YYf81/11mQ/'
        b'3DxlZ2L73xc1/bxkRveOiMiddUfHSyY1q7wvTpgXYKofy+833zdevvXDp27Pv+5zPT5eaUe9uVswXKXvm2bQs44dVvUd6Dzq5KB1vooKJMJe3KhWT8gg94x4XEYohyXp'
        b'tgQdXx1Ml1g2jRURI/dgURGolqLlIfHHh+QqCzkwjeTgaXVymnRjUJqtcPY0HKRxChb7PahBPeAPHDiho2ifkoMGaEJbaV1uwCqoHfwnEDbRP4HQDTfo6rBnOeoMTpkE'
        b'O2Xk3hwa0UF4ule+/f/FIcF/VXikv6gRBpPBYtMIEosxLvas6CLtJSFbGPJh+JF98q7okRj1ph4pqRrtkVmsJUZ9j5SkR7FPNOjwk1T+9UgEC98jy11v0Qs9UlI80iMx'
        b'mCw9Mvq+c4+M15oK8GyDqcRq6ZHoCvkeiZnP65HnG4wWPf6lWFvSIykzlPTItILOYOiRFOrX4SF4eUeDYDAJFlIu1iMvseYaDboeO61Opy+xCD3OdMNIMT3d4yKGPAbB'
        b'PDUmYnKPk1BoyLdoqPPqcbGadIVaA3ZoGv06XY+DRiNgB1eC3ZXcarIK+rx+jRbR9ueJteAnkwf5Wwk8UTSeeGKe3IPxk8iDWEKeHPF54sd4cuPBkwQjT0wpH04e9BaY'
        b'CDIfRB7k3XOeyCZP7pJ5FXmQ9+V5ktDgyctqvII8iG7wRD75aPKYQh7BfQaBcMehzyD8fd4Ag0D7frDv/VsCPe4aje27zRL+MCp/8J9KUZjMFgXp0+elK+15YmiID9ca'
        b'jdjOUTkgFys9jpgJvEUgGfgeudGs0xox/RdYTRZDsZ4GEPy0XuI94vR77KeLocJM8hsNSaQc1lNR1tw9ia1l/x+rmS9A'
    ))))

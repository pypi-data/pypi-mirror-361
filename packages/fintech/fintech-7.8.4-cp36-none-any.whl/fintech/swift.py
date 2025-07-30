
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
        b'eJzVfAdYlFe6//m+KcBQRFBEjThWGIZeVLCBsQBDs2KHAQaYMMzAfDNgQcEKiICFKGIDK4goRUGwv2dTdpNsd+OyabspbkyyKZuym2ST/znnAwTF/Pfe+9z73Os8fM6c'
        b'+pbfed/3nPPOvIsG/OPJXwT5E2aRRzpajTLRai6dS+d3otW8TvKcNF2ygzNNTJfqZDtQtlzwW8Pr5OmyHdx2Tmej43dwHEqXL0V2GSqbb3WKpUnRC5cpc0zpVoNOacpQ'
        b'WrJ0ysSNliyTUblQb7To0rKUudq0bG2mzk+hWJalF/rapusy9EadoMywGtMsepNRUFpMpKlZ0Cl7x9QJAukm+CnSxvWSriR/HuTPnpKfQR4lqIQr4UskJdISWYm8xKbE'
        b'tsSuRFFiX+JQ4ljiVDKsxLlkeIlLiWvJiJKRJW4lo0rcS0aXjCkZW/JMybgMD8a07RaPUrQDbRm/SV7osQMtRYXjdyAObfXYOn4lEQ9hNEsliU/rkx5H/oaTP1dKgpRJ'
        b'cClS2cYbbGlFIY9o2a81Rp9P+VBk9SQf4CTe7oHLcVlC7GJciisSVLgCGvHZ6OWJvnLkuUCKb5OPx1ScdTRpvdjXV4geg2vicCXeG4f3ckgRzUPLhC1pXC8FEvLn0kdB'
        b'PBUCR8Tw/xFChksvs1yphDDLE2Y5xizPmOW28r3MZj7OrOcTzM4VmT3paxO0mncnWklx+DA+D7FCHCtZ+JCn71J85qtyxcLP19iGzJQQ5aWkxMoi14uFV6bIfOScM8Fi'
        b'ikNPyChkUJBCbfRo6ZcuKEKq+LPnF3xH4BHlBGSwIxVVy49wLTZIGTDauHH4wqXSr8Xii1O/GFY9jPP6DBXFLl08JfEa6kFWP0rHWaiMIUIv91/s5YX3+Ef54j3QuAx2'
        b'QpVXTByu8vGL9o2J45BxmN1s/bJBslX0MRxAZUvlijIk/dLjflJ6T0BF/oT07EXpnQ8bNk+PZiAUkOLzauZoZPWhrfRmQvNetQbvxWWxi6OifaKXoyDN0pFQDR341jIo'
        b'h+dRpswGn5SHWN0otq57QlkwdJLRoTEVV6I8KMXXraNoVRVhti4YrtC643DVD2XDHthuHUHqDASHZ4ODaKtDUIVvorSimawCyqDMGR+UIeSHoBVv98PNRYzc11cpVpuR'
        b'F0LOKYbjQq+y4/1cPLwlUVTZa9/wjEJ6jxl3ZIKWfP5AvvejlL+mPJcRq301w++AlzZK+zDFJS0rw5D6cUqM1vbzX2aolkRrVYkabbOugbvgmvnX9BjtK/zPA8+0dAZF'
        b'8y8sub/Uvd7nxRFOzurjXUdaDzbuGJ5uDJBkhqOokpEVqEXFW56hau7OibAn0lLFWX29iZp5NBJKcMMoqe20UZaxtEE13juHyHQPrsJ7JUgahre5cdBKmO5UcT28l0ol'
        b'MVOlP3o0om/dZmWYTZt0RmWGaMH8hAJ9hmVOj4KZp+R0rUVHjajgQLU80YFz4Jw5W86LM1Ntm6mmVZIeWb7WYNX12CQnm63G5OQe++TkNINOa7TmJic/MamKM9vQ9zL6'
        b'oKNMouM70fHfdublHM/J2dNKrV8ibvdTR/l4x0NFApzGDQQlMuSGt0lHQz2uXJjG9+JPOgSYibHoBzPPTIGEgJlnYJYwMPNbJUOBuW91DAazPN5KC/BtfD0WH4S2AIJ5'
        b'X+QLDRFWaqLwrnx8BR8UJpKe/sgfX/diKMMtBInHSftT0M2g5hewWH9qr8AJvqRWM+aNj1J+kRqljdU+l/Ew/WGKz4Eo7d9SXDJR2+jwmtrVu0fvGD0jGFWAza/XV6s4'
        b'yxjSJzuXCGJnjDrGF5dGx8bLkD208vi4Djf3quMxebNSJu0ee1GpGQaT1sK0SpGNvB04KdGpWdGvUSnTUI8sXZeqt5hpIzO1QCp+gBZ5M/VMA1RJu6v7Vfn6IFWOJyUB'
        b'UOrZp0rmInw43JyLxuZIYX8oPmgdSaV1Bg77CpZpjroAKeJTET6HKzSsBg7jWzNJDW4wEsHzOoQbi55jdgE3224gFTpcHCBBfCbCTdACrcwu4PooOCVYpsNBLR3PiPAF'
        b'fBiaRJtxEy7AMVKJyycG8Ig30Y6XJlndqfLtYaeAr4Ti0wo6GexAuB0fgm6x48UFkbQyNyFARup2IqL2BnyNUVmEW/E+wRy6LpL2I0NehAtxrJdfONThdmvgOLhISSG2'
        b'DbdPh9tsOtwMR3W0cgE0U1LgEBszQ2SvFB+ZLgjBdrCPdixC+BLUK6xjRYN2AfbSjnAFDlHuoRbha7AbdzP/agsVeBerruECbEjtUYS7cCeuEIXTjWsX4HbBIRD2Ksis'
        b'+CoXAu1O4qRnhuFye/O0lfgco/Ycwp3DxoiK2JMDTfa4NTRkPK0iXlsSsorVyPEBV3tFEL4JFZR7fIiz8zWxqSbx+LI97giE+iWszy6Og8uwmzHPQ1eUgNsL4Bicc6Jk'
        b'1HNq3A3tIo2tUG0n2DlCfSpuoWPe5qaZcDHjDu8jotlnn2eFLtiBO8hIuJWbAsc3MGKi06BWsDfH4RIL7VfDeWzBjWzMUYvwOcGCO4nLOGNP6yrIhG0BIt/duB5OC06O'
        b'8XCUyEQi42ZDayEbMAvfxMWkBuEGJw5J7LgIfClKdEzn8QEPUhMYnEeZu8b5QS3sYZ3CYrbYO+ZCB1n9e6VIMomL2AA7mV3YADcSCVAWwymKolyCAZmEVczGDWoCZ1d8'
        b'LkSO+AyCc0EvyuISPg7nCRLGZjLgEVC2wa5FTIiCMzQIBHvtxNw0D6NSvESUec2GVS7ApWEC7sDtPrie1V3ggqEY71YpmWfbZeeacFeSJUWJd3Lum9dZWOGvXEfMPCjJ'
        b'laKAOzk1E2rmssL6JDftCn6DFOXeyXF3HS22LJW7z63mi4nduLNl5dyFClZ4JmTMzA/5UimKuLPlfvo8N3FMm2cWO6J9UqS8s6VmUosDK5QYPbRfcjVSlEK6r98uFn4l'
        b'nyB0SeqkyJkUZv8wkRUGrZsYtxk1UDq31Ky6NZIV3o+cErYdtVA6t9wPPTSMFdqlTl3wOn+N0rmlZpFaDELKJKqNX0nuUDoF9/xiV1aYv1CdZuBfJoV3hfuT9kSwwu3j'
        b'fDRfoV9T4gX3mfPHssLsBL9xgfx9UnhXWKm0mcQKPzAERv6Wf4dyJNxXNm9khU3uwdqZ3F9JIRmz4NQqVjgvLnTL77nPKJvCSi+tyOayWdNCl6N/kEIypuM+J1YYVxjm'
        b'S0JrGeFdWOn/0JkVfu0+c+5qiS0pJGMaHW1Y4YOQ2Y565CwjAhHuB5TOZ4WKYXOHl3HupPCu4D79xzms8O76CMl6XikjUhLcc1YVsEL/uHkJ7/JepJCMOedTO1aYkjZ/'
        b'XARP8JVLWuonuLNCZcbCudH8DFJ4V6hZ/FahqOJlUXMvowhi+u9kuy8omyAKOSBui0mSKCOiy76/VWFmhZX58UnRkpWk8G62e55ZzQonuiZ6bpKkyIjosu9P/VGE4iLv'
        b'JaEj+CxSeDd7pce5xaJjvRU8UrBXKCPosnPgImbJRDt0cfNKe7NTHL7gSBbqcLJQD0ANw3voRjhKVkJnAa7B1wUJsxrqtdDIKqGB+JTzxOAImnB8hS7/am4i3r1BJRVp'
        b'nf6irICbYUNYLbg/5Rdi7Oed9XLgPhRBXN0d08qgeStZYVjkL2Rf81Gk8K6pZsHvROW9v/VV6/t8og3h3+Q+6vzcoYPtEITEvRzdxKAM2b+5XckYGKPQ2UY+EaPMjLcq'
        b'KZPNxFg1QnkC2VhV4bLoOD9c5j89kUduKVJPGa5gtJql4gYucUqBj3tMvsjqQ5ktIvuUgLq1OT7rvdIQM3AjRgZp/DW4MiEairUyZIt38hsD8qw0GJmFi2EXtBP/c4W4'
        b'LGIFuFVEM0T+x5m0A/HpeLUXCVdL/Umg4gBVnpmSYfjSFKZYF+0y0nMvJhYBhaNwNZw006CE0fGKr4yyqPxs4WaHbVELxMLwNTaIxKHO+8YWxJ6Mew6JYXylUBgcAPvx'
        b'AfrhANJOIw5+Mn2/1xM3a1g0XEU3mBqo8o+GZi9KJ4eUFpmTJFgcoQF2zQgOgVNMdNUoNQzXs+DTj39WTTZUbG9KdlfRUuRKgrlalQTvhWJPFg0Gwja4HBykHMbcMUpD'
        b'UMrQORnqi4KhDW4b6ZbkJDLABXxaDHH2WvD+4GBiy5tonxMoE0rimTxyXaA1ODgV7yBBMdSj5yLnMfLSl+LjwdOIk9tN29egdNyVzNy/dxB0aWIoafFMN7ehWIacciUz'
        b'hrta6bZdtnVG8DRnqKQUHEE6vlAMGg7ja8M1saSLP65Qc8jeEw6tJv4CannGkZCPa4On4eM2RBcknMjYTIIJFsi2SaEmeFrmOkrdUZSJ6+CwGA8d98PP43IN3qkjkpIh'
        b'qQcHp1aGsMFgd95sQnvrVrIO4BjKgpuZVraXOQz7w9VMG2Xx0CxFDrgNn5pNsLHLV1zdB+xzg8k+8Ay+TT/VIcMkfFScbpsbWdzlsU75MXSXI8G3ODjq95w1lg57fnKI'
        b'EBsdHUcPH/q3ll5+Ku84P5Uvr4CzOjiHz8EZLy9odFOroBqfUY9IIbqodhuJz4yC8zyJb0Y4Q900g+hzm+H4ZnU8gXiJb5QUSSM4uBAC20SBHMLV8wRH90KzldqYE9yk'
        b'sRPEwOQqibLO4XYnaMEXxcoOTkWCMVGdM57F7Y5KrVhxi1PDaV9xla3G1wQn3ED2UKJZGo/3wxFRGvvwtXVCntxgVdBw9DqnXABnGYEj8AU4S5y7EncX4CsyFo9NmJjF'
        b'BtxE+KokkVVaOr7iyLHwKGhtIiNiXI7e3mnMQnuoIrZzNbeGBCwiboncrkCLYOH1igIa+N3knjEUstG2TsedJGxqERQFdJptnBJXkEiMRU175i7E7RZ8UWXGV2gUeosb'
        b'O3kFA8Bo+xgBt1kmxcgRR7COq2QhIkdVUKqyt8UtIx2JWZRM56JIrWig6wgxnSRqzYWLeQ6U7FrOczm+wegeD0dV9k64aYYD2Y9IZnLRULKejReAO8lWcRivNpMYUuLE'
        b'TSdG6Lw407ZAfIRUjR+F26inmMhFpixksivII6FeHt6Py9k80MF54BoQV6kjgfQhQbEJXxD1dIBTzo9gHM0LTLJXpMNtWi5x4QLWQ5e4L+wgu4DtZKPXICErxAf5ZC0T'
        b'0UD80Fkox1fjhyny8jkkJaEZicuvmVU8Y2mSARrIequDxt4Fh+u9xbDyImyHYrJ6bvr3Ljm4hCsN//jxxx+/3SRaR2Wg1fB39xlINYINxbuuFBxxMS7vR2RhEhsqR0s3'
        b'H07QsbofjviGRFT4IYOC4DHZtR+PuMlZxP4h2A8XBad8uNyPSGiQi0K9kTBFyINtG/sBmYtFazB3MrTRYLNq8iM84t0bWZ372KUEjriaBMz9gIRjo0U6islqr7J3mlPU'
        b'D8qExaxGhvdnCBY4vLYfkfiAvyihNmiYJlh84FY/JvVkI0mlvhBO4hsEk6vx9UeYhKtwUiT/inU+hSWuz+zD5WpHpsXCgCCCyvL4PlQmwS4RleegBl8mqFwHDf2oHNcb'
        b'y/NwCTrsneB6ah8sl44WRXgOTjDwFcG5PmDOgjIxSiEL7SKpIq6psR+Zc3sPraDB01HIWy88AuaZiYxyX6iEYkEBZY79uFztKvJ0groUe8XKoD5kjoJufc+D73ihgVjf'
        b'PxfsWnegK/69COfdTd1/+prsrI4FZc6L/dnIV6eqeZ6fvH1CSpuL7Zp58GxAZGjZrveK7/xluK3ttJ4N43WntyCP7Q/NnrG/XffVV8lFSVffrP352y8ej8xeWDQrwPmD'
        b'dwI/nrttf6xT+su3XvZ71dHyWn3xmBcPV893+/JDtLpwQ9WDqFUV9wRLi/Sh8o/Tv3L9SoFXnn6jNP39jJ8rXjm3sPbD52Z1zOhKqXbK+/KVNW7+tfdcPT83LFuVH5JU'
        b'+3D8mrxPh73zeee+jRNOxrhNXOVz0E29L6txxIPPL8yfW/2J5sozNfN/e/JV5Q+hqUmdS8aEhS2/fO+vV899PO+Pm9Jf0nl/vCJqzvstjQ8fvCid+mBNa+qafx7t/tji'
        b'c+NSS9Wd+7I/3J9Yvy7/I+fv77f8CXWM1Ro/Wf77H6+XxrvsO9zhmRL55rmM0bDlH7s3S+qWnnT+h2Xe8Q8cFr4+592LUR+2vDj2o+PT/2JavfR4+717eRP/rveYZf6k'
        b'8njC+Glhn2090/j1PuvsKx+0znUoML7/6+I/3J4W+PrtGO+/Rm36JM52geMh/b2PNuz/TWTFu+t3LP12R914/u7IV9/YwmWsPfup+rbK1kIPS4hVaiIb3HKfeOLBcJUP'
        b'8dO4ci40UUfdhq9a6C0BriXBU6naL9rHW+VH2uAyaCGxm7tSun7+BAtdBdAaR49a9oRCSd+ZIAet+HaWhaIzxhlvVz+X6EdsfhmZQA6VvC/xhaynC94FBzU+XlG4QmMi'
        b'O3lkS+beGI+vsZ6w0wLXNVADu6PjvONskFzK2zqCSJUd3vMsPeYhY+Iy4oCrJMh1s3qmBB+F7e4WCu41xFDe0CT4ZuPzBN35XCQ0J6tsHz+1etpDJXt6/aOTLhfxpMti'
        b'1hoFrXjnwg688mnsPM+Js+Xk3AjOgbflHDgnnryTKEiZC+fE0SNOW07B/kaQlzP5v+9F3vNO4nteYSPnaG8F58a78LY8idXJS8pLyRjOnBupkZPXGDI6fe/EmR3QowNT'
        b'h4GEDThgezpvKs7s2McdG+pZ1HfUdnvEwKM2egRH4u/KUb1nbf4qEiep42PJFgC3wSGqEbUcLYKLNlBth4+oODGq6obz0KyJ9sEH/UicS+J4OJoHJwbtX+j8LEKcj9j+'
        b'hV7CoCevYTIc+/cz/FP3MxJ2/SL9KocMqlAO+JdI9SYotYMvxtht28ZcnTJuWVhIgNJkZm+C/AZ1HfQh2qI06yxWs5GOZdALFjpEqtaYrdSmpZmsRotSsGgtuhyd0SIo'
        b'C7L0aVkkJNORPrlmnUAKdemDhtMKSqtg1RqU6XqmNK1ZrxP8lJEGwaTUGgzKpQsSI5UZep0hXWDj6DYQDaeRUWgbw6Ch2Fm52CrNZMzXmUkreh9oNerTTOk6QpdZb8wU'
        b'foK3yEdUbFRmEdLoRWSGyWAwFZCedABrGmFdF/70IXyJDNN15mSzLkNn1hnTdOG98yq9Iq0ZhPZMQeit26R6rOeTfYg+UlLiTUZdSorSa55ukzXzqZ2pCiibj+abR0oM'
        b'Or1lkzbL8HjrXl09aqwxGS0mozUnR2d+vC0pTdWZB/IhUEKGbpyqNWgJB8mmXJ0xnImTdDBmaIngBa0h3TS4fS8xOSIt83Vp+hwCBcIpFdRQTdOsZiqhjY+oScJnssxW'
        b'45Ct6SVLOHuSMa1pWaSZQD5Zc55GdZrBJOj6yF5gTP8/QHKqyZStS++leRBeVpD1YNEZGQ/KTF0qGc3yv5sXo8nyb7CSbzJnEvtizv5fyo1gzUlOM+vS9RZhKF6W0nWj'
        b'XGS1CGlZZn0GYUvpL1pdpclo2Pg/ylOvEdAb2SqlhkLZy5rOOBRb7N7qJ7iapzNoBQvr/n+DqYHhQni/Oxvoi/rtXa5JsDw+QC8ydEKaWZ9LuzzNclNd6/SpT6GYei6L'
        b'tg9cScRzkakMhqcgrHfSR3AcPNfTofkflrtZR7woWXThSmJlSMsl+EZadqo4wVDtqS0izCdn6waoqo8gIgIDviEIOsNPdbUQB/8UIfaOQ1sMTewTHldjNabrjEN7zN5p'
        b'iY8cwlcPnpi0+akxMvMH+91FVNv4TIZFIJYqgwQxtHqojrlmogBi87RDz5vYW60z+sab/Z5G/aC5n6B7aP/fC4THYoBBnZ8aD4h99WTqoTtGz4uMfzrskk1mfabeSCH1'
        b'pA1J6K1LZYAkC1i50KzLSS946lofOPK/AWix+X/QmGRpibcZ0uQt0qXiG2RZD2ET/gcIo8uArTNq5wbRtYzU/PRiM2pzdI+sXW9crPSKJ8VD4tRqzmVx0RM9VujMBTpj'
        b'Ol2Wmwp0adlD9RZ0udrwgYE1GWBAVD9EjzVG47pw5XJjttFUYHwUdacP3Ado09NJQYHekkWDdL2ZRqk6sz5NqU//qQg/nGxftTnUbBKalmU9liY4uGN47z4nnOwLhvIM'
        b'g1v3XyDRnZwbevwCKUm8LHUKkZA94GfJ9ijFsFabJV6/vOpMTx2jNJKIFJ+bI8YhdmmR6Qxl0M4jqMNX0Uw0c+Q61vaUrRw5oJdTnJQphsgMpXhVg0vw87h4TFJvNhZK'
        b'k+Lz4n3VrmVkVzpgoypuUkf6ThgvG4N3zlE5WCexmwYoX4TL/WOifWGPf0ycxjcGV2jiZUi3MRBXyNWhuNxKjyDGzoQ6dQwcxPseNXGBExJogfPL2CWIDt/AjQPuTmRo'
        b'BtymVydri9i1Fm7DpRpN7IyJj65J6B0Jvmhl1brlNrhcjSviYnx5hHcU2eIuHvZAEz7F6MQt+OgoOno03qshW3Bc5R+FKyQImhPGu0hxDTTZWifSdtugkh/Qjl7XlfnH'
        b'y0waNFktmxUHNdappFkaHM8Z1Eq80jrjHR/HIRXckEFtEhxjIz4TvHXQvPTWKo7D13Epmpwii8DXY0R5V69ZrvbDFWQwv5g4elLTNV8lR2PxUSmcxtX+7I5m+YYAqCjq'
        b'bRYdh/f4kCajRkoD7OAEG2UproJDT2pt8xKqNWgNZvhIWmKDd40MDqKXUIdROhRnMgUUOkvVMQvhwOMK0kExg4ot7IYqNCs4SMaOvrPwWXyajadYhxvwQRuE600oAAU4'
        b'4TqmcnwMl+NLgzSKG9OpRqcSUIwVz+e7V2hioSTwMZ3umcEOk3UEHXuDoS1XTnO2bnKxCC65zmHEzCxy9ofbpI4ds6JsKIfb4phHoZsgqR8KM3CbCIURmeL1V7EqKzg4'
        b'V4KmQzmnIfqfOVK8MCnG3eHBwbhFhjJhB7cEwRW81491meDGBQebJcgXt3EJCC6HkSXCjpJvwuFhpEubDJE5S7kVCDricLN49dCZlwI38MHgYHrNdgplx4nTQPlm3Ilv'
        b'w/ngYCrG08hANNbN1meNzA35oH35nDKl8LmctYhdGEJ7FK4WOFTggBagBVCZwJpOdR2OlCgixyk3xbDCxwWpJCLv5as20Au2ClGWUAyHbXEND8+PTRKv+J73hZMaP19v'
        b'ql+4JCX6gM5hKySGBfiqeOLfHgEtmugELU3pk0o5OInLJovr57Y9dAy1fi7ieraAJk21TmHtyJhHhlhA+DS0sCUEZbYsLxnXTsFVT64huDnx0RqC4/ZsVGjBHXB8iGUE'
        b'J6GRLSNoWMGwmOD7LDS4BgeLV7xZ4+E6E1hGwTD0DFIW2QakGA5NHUNvZyayM/2cCE20b7wfWUledLVAWxg9HR0LJVI4Cw1wkN0LrI+ES/TmUuUbLUURcM3OhodKeN6L'
        b'ySxwBj6jic7GJf0yg6oForgP4Vp8c6BCOnSiPsLzxHvfLsJvgzrGV+PrHU9zrfFpfGBYpkS3lhPZPgfXnQdfl+OqeH9cQq9nx8ZK4QCu1DNGVsCeZUPcq9Mj6g56re6q'
        b'ZxNuxdVwTB2T7/z4Gp+ArBNIvcYZjooLFir7jLk0iTbzTpNB07ipoiUuJ8jf1Zt+IEOr/Fj2AdTBBZZUqMaHpWovfAw6B9/Tszv6Y2tF21A6ddggy0D9CDUNeB+cYbdF'
        b'qbPHaWJx/ebBlgEujGMkDI8iQCuPJXawdcCVM76IT1pVpHoalG/slzuUEbDiPbH0uF3DpHwJNwbBYXn0qslsMLUEdxFeAuFClE9Mgq8c2Wt4fAL24+ss5YCYvdt4jzqa'
        b'zLhrwO04vRmvgJPiVVTbYmIByjVKqHl03x4MFaK4KvD5VUQgN+f2J13QjItqaGXDJxM7ejBs9WOZIWJeiHoJg1gqtMdposkKutaPscQ0EUGXoR5f68cm0UuTCM4zUqsz'
        b'8ypzOXviD6vdSCSxdNkIRhCcX4dPDERdKS6lqDO7iKY1FO/j4Zo9TQTGjSQoCITKvsyBxfgggfER3ETTbPPxHkaEH25LHYByXAxtIsw9DWzxRc61Q87os8VcSkrsQWEz'
        b'YojNGqd6AtnLg/qBPRZfE69qG2nSDG6DSnwQH7aht9QoGfbhMyyfREdNxOOAFfDlfsTC5XzRVJdPgA4SDpyA9gAJXffIBNehw7qS1t1S4HaBoSl6cSK0BSxdQiRS7o9P'
        b'Qv1iLz9fL6I07978haXUSpT6rIiiumLJEoujfGgNsR2a5YlktSC4vXk4VKRAGVtRBJIHoWQ+dA6p37W4lnkF2/lwA9pDiJ+DHfh5bjFxSxvwLdEvdUCtD60jgm0Jpn7p'
        b'Em4YbaX5StNxezIZvTQa78eHSMi3m2CqNJ88KginzdPgkgzaUpdYUuFqKEf0I1+VDTXEU7C7hROZ3gTyeF/f6pIn897GMQwek/3h1CAncWsD9RH45BJm1eBEOlQNVHdl'
        b'oahtaJorBjz4+YzBkUwTPtAfysAFuM7G0QTifavRELEMnBLvVXHXCigNnpYnQSthDxdDGS8xMIT6UZ85j4gjRM5CGJ0Wt4hdLofCseCQfEJVhQ0XgaBxFuxlNf5wbh2R'
        b'Im4hYgunnroNKjJZzXrYG0JqAhEaBTe4hfTS9sY8ayQzZLst9mT1lhNBEThULcUtjtBqmBcSmBjVB5clviuWPI4AAsaTClw7M5558IVQL4EmOXLBnagQFSrsREBWWeES'
        b'NE2DVh5l4FLejeZBN61ji9Z/dBo0yZDKHW1FW5+Ds+I3SkpI8HxMYF8zICt4iRe9z6MrJ2nQ3Em+NmTd6a0zabQ4FQ7Yx8fhCt8VDNCLCXiTomKWRy1jjIRAYyIujaP5'
        b'PL5+8bEJMpo126KAXR7wPPOlVnyBwPEgCdtueNIs+YkeopAPzJ1HiCfIayYhDD6CoGmYj4oXI5BOfDJ7IHhW4tMMPJcimdI98G6Xgdi5LhWxg1vhkGjQnse7CRntBcQg'
        b'HMAdLCWhkwvB12AP+4oK2a1Uw6Wn23YXuMFMO74Kl5lpXpsDTTT54SY+kDtMTkYr46biW3CFaSE/KYmsgkjFQLuPT80XdzYX8RES8gyMDkhc2fEoPFCsYrlxhHO2TttD'
        b'V/SGqm3QzkJVT7yN2c11Qmih94BQtRNfUclFFJyCmzQUJOFoKolvaThKlmSFKOZWP3xDDEiDpovxaO06Bv9Z0O7EAtLcTBaP4nO4SxyuC86qxIB0RG88ik+SWJt28jQS'
        b'33QFH+8PSO2wmDOlxs0k0GlM7A9IF8BNlZh3BrVCGCNuSgSjLRW3ikFsVRpcFUnD55Yz2uDght7kmdQNwYw4fAVKGHlSYgpZNkSDN74pUvdsgUhcnYF0olCDSk98m4S5'
        b'cNFE41xcr2Zj6d3gJq6Duke+aEkQy7YZPZbue1ukUrLvfcXRRJXAZHZSRny0aEirFzM7mpjIagRiMvaIZtSfLHNqRm2yVVJxD9y8EdqZoXHA55ihmR0kpnzskMNZ1039'
        b'ZobsaI4xcs1wPYqZmch4ZmUSpogYOJmNS3utDK7MZWYmIkTFibRdUvqIdgZXFYl2Zt9EQjeL8s8+60cX2gonus6gQ0wWc8M7CGEEEgNWWqw/47/TlvKvLLCNSHH40T4P'
        b'6d+pXSAT6K30tUWjrcvWlD+zYMQc64cfvTr14JS/paf+PrCs9rUXPtpz6rR875jpR79ymaAYa2uOShkjP590aOSFCMPOFdu/HHbfZvj4LZ8FDtv4mfbzUe9Ff2/3Q/Gs'
        b'b+99+Jb17s5z129925p34eGxpQ8Kz2cHn92zNaDz564HkzaEqk21Wd/9qWftqandre/njAtb0xRz+PLrPX+M2fjRx8uW7/xNi8eB6b80XvrVSymhR2NCz31vf79Fu+ZD'
        b'x3cnjf/uZy88M7L7+zcbvzgfLux5d/jymP2nG60xifDljw+m5bX97puW8JmOY1WGj7ulD9rtto0tfuXu7HdOaPZc+/6lKZ+90fT73S+e+GHnZ+tqfu3zfHBExYl/VQQ3'
        b'LXij4Yt9LRLtj9LNC+6fzP74gwm/+2bTiFNLJv0lbdelkM9KS7Y1u6a8drpY/cJLBXvfyI37ZZFqxfiS16ffWTfSqLnm+s4J2Tcr6+/+y+sN13fc7vpuC35/y59PVJeu'
        b'uDNnyseLjbO9PQo8xh9o3BFmP2zuTeH3JUf3Lgqp8F7pU2VdYShoz9t8dIJPd3VCfGnJnGfjl87Z9dWh0d85BOpevvvhvB2b5WGvwQyFW9Ifp33bFPqbSI+vu2atfO+r'
        b'iV83lL7yTaHJ2FVYlPTWB3+Y5Pb223Psz92+/enr+S/+6s8fRPpvCbtn+vLGrfj67jfDH7bW/2t7QmKz7PWmeYbMqUv81x/67mzhig9eae7Uv/qgzl7i0fN5ScCJUVsi'
        b'yn6dMiZkxneSsNvKsGRhzB+nR6hDP//7L30maN5uzJ9btPMbWdjhl7vGPJiz8GzcP9e8eXTq90EbPhn2+h/GnThXOlIxaucPkTc43x1l/zxbp9569ne/Kv/LP0f95s4v'
        b'bj2XLAvfcS/hZz+8+Ue7dxJkn/5SXvpJ3KiZgqbg8xfWnx61PG36nyqP1U3KGb1p2rud3lMML5o6ffJdXpyycmPmp7vvjMLu4bWX71b5Jo1/q3Xzj3vf8b8ID17bcah7'
        b'7ZbdMecPxL05X6daXP/stte3/b141aiOo99AYc8Dwd36p1e2ttxc8+Diw/uOLa+v+Mf0N6+9W1UovOH4xvBlY96uOzBc/0X5nK5Kv/Yvv5q3H09VbXz4Q9H+Xfdv1R35'
        b'4fvi1WcezDx756XrM8eMXPWexuXviof7vtj828by7+fMWPOW698klgvH397x0sGadQudTr129HvtnYN1d14Zfsr8dWhQyIT3osu7T33h9IfV/7q/7+f//EfKWx+kec1+'
        b'78HfJv1QbaloW/Mjv+yE7ovEvSonCzvAufXMZrwNatRi8g7xF9QrE68yCjqkUbPF/B64GTtJ7e2nIh4FoUzcZbeKh7Pz1BbR9TmOnUp82oDkITFzaNx6C9tkbIcaX/XC'
        b'pEHJQXq8n30DbQY+WtCbG0TcajM+wpKDcDduYxlAeWvwcVzuA/uh6VH2EktdIkGZmN10fDwcUkdBlWxwnhDLEqqYyDKQtiyDk+r4OJ8YXMkSYMttoYsvgLNpjLeNsMtH'
        b'QwLdncQh+/siJC/g/XDXWkYelI2fqCG09fM1fsqwAEmmJxxhrHnA0UUaaMPVA8PR0VDJZk2ERtymxg35vWKTw0U+mMjgJKsNHo13q2M8gwZ/8w5KvBlXTsR2blOTbXg7'
        b'0QUJ13P7vqY5SyopwodVrv9uitN/8qFy/K+P88R3BXMsYSEBLHXKh+YCFaGVtpy09+XE0qToS8rxnAPnwtN3DpyC57mhXmK6FW3vztPEKdrSnaZZ8Qpu4EscwUns9ZSx'
        b'xJct78QpOTlPv8HozLlLnDknNoeU8yD9R9BULF7Zm8JFv+NIZuMdeAdGAUviYjORP57STTOoJpLPcpbWxeggveS8giWFKbhnSH83Uj+GjCgl3D6i3JkX08foO/rFR8qB'
        b'mX4nIL4v40tKz/IHZHr913Wl4szOfdpic9EvQAi0CBWjzyYPzAmjJiM5Hjf0poThKl8SkQcSA/EcGpMrwV0kYL0w6NuvVNURdDgagOjobyag1Xw6t1qSzi9FdjsJP87s'
        b'RoJla5kXmM0m87fjxTsKBhtzb/KVLl2pNSp1tN4vXiXtsU1Oppc6yck9iuRk8ccRyHuH5OQ8q9bQW2OTnJxuSktOFrH46MH4pAFMFaGOZfPZ8ix49sHdGnsn3Gmxt6P8'
        b'+ZrFdbcMLiGyr5bLonG5iluoT/Lp5oSxpK9dRffsqq54HDFiQeasvFTP9ORjLbu3vF0wL/Ilm0Tn7hGL3JacGfHO7u3yNbWBLkX7qnQOthVfhnxzo6ng7e++fGvhuecU'
        b'rfMr730U8N27X+6893BRwdbQrr1H4rOyX5z0+afCmu2FSq83dK9+++JD3YjoGyu3vrwo8MOY/bNd5ztt9Qn+dvLUF/789s4rdVvW3fsqcfGZ6g2Nf1nx4Or48OrGyVtr'
        b'T8dUhDvWXsn63YQ6TdWqD2oyty049Nf2VxVNF1t/KT9qaH3N6frHrb/iSn631TvsL/bSGtf4sKMfLFmk+eT+G22Xdvk9WHt/7eshsb+5Evfzqclbo30Nt89kXjyf+s3S'
        b'8PPr3vy977idukvX4m98fKhAO+ab7WPlZSnOjStfCBpZavPnuUWSyPUrxmjuqaQW8cuJ7Z5k08khbgYaiVvI1u+2FzPtSSOL+r6CPgmu9H8LnWysbuIWCz0lwRfhqtze'
        b'mxhWatVJO9w1WWw3Htql+DK+iC9b2ElXG1z0FKA5akxWvK9XnwsYjvdJoGWGlICbYdzlv9FcytmW6ukPZgYJYg0mbXpyMrOB0+jicKM2KYTYHZriSVM/nW2dbQZZMFmv'
        b'dZKMSCAti9AWB848qg/IZPHwBN2PTMHw/x72OLN7/7Khk9MoX0wY/dhvoHGgeo3ElZugnJ6L0Z/ugDKogpZwG+Q0WjLOKV1vzJgvE9JJsws9eeNeDHTaHuG8+zdFGQWO'
        b'ltSzu9+pvwE/2+4z7uyKA4UfN4feeLhr14U5m7I77t3+Q+E3Ybt+/PRcS1So/9kP59lfe9g4Zed+leXLY6OvvbO2K88zMOjzDY77TxvWtb954mHn+KpEd5+ZTSob9msH'
        b'qzNwHf2WOL62KSGB7bhtiLtt43GD+2iGH7wTriXD1QBNgi9uJVQnJPjyBD43JFAP18NZlITLjbBNZIuANg4qCFvtsJ/w5SLxSMCNDOu4zD1E05vGXJgj5W2d4XkWIpnw'
        b'NtxF/Pj1+Ee/T2Kv4vE+v0IWZvBQ6yZEb8QHH/v5Enm0hW7BpuMaO3WMDHEaElJ0IlwDHVDXB2uP/+ZQ4D+LGelPLgS9UW/pXQhUcsjRlhNdo63EpwjRFzKP7oe5skdi'
        b'0Bl7pDRvt0dmseYadD1SekFNfKE+jTxp7mWPRLCYe2SpGy06oUdK03d6JHqjpUfGfqOgR2bWGjNJb70x12rpkaRlmXskJnN6jzxDb7DoyIccbW6PZJM+t0emFdL0+h5J'
        b'lm4DaUKGV+gFvVGw0IS9HnmuNdWgT+ux0aal6XItQo8DmzBITBDocRRDHb1gmjEtILDHXsjSZ1iSmdfqcbQa07K0euLJknUb0nrskpMF4tlyiZ+SW41WQZf+aCGLbHuY'
        b'qZEwB9IHPUQy02NKMz2eNdNrbzO9jjJTAJvp5YGZ2kwz/SkIM73qNVN/ZvanDwoxM12bZm/6oMdyZhplmr3oI5g+6O9cmOndjZme0Jop5M107ZgpfM2h9DGdPtT9doBq'
        b'x67fDvxz4QA7wOq+te37GZAe5+Tk3ve9BvDbMRmDf+RIaTRZlLROlx6vsjVT+0Kdt9ZgIOaN4YCe6/QoiBLMFoHmQPTIDaY0rYHIf4nVaNHn6FjkYA7rE95j3r7HdpYY'
        b'I8yhn1gsIuXJChWx5jyCmlju/wHli74r'
    ))))

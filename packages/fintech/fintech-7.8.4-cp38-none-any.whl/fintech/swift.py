
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
        b'eJzVfAlYVEe2cN3bC0sDIiKiuLQ7TbM3bihuEQWaxRVRo9B0N9DadOPtbnEJuKAiAoKIiuKuqKgomztqpk7iZJJM9kwyTJIhyfx5MZrlJZnMmM2/qm6DqJi3fe9979kf'
        b'16aWU2c/p6rO5VP02D8J+ZlKfmyTyMOAFqNstJgzcAZ+M1rMGyVHpAbJUU4YYZAaZUVohdwWuoQ3yg2yIm4TZ3Qx8kUchwzyechts8rlR6P7vIXxM+crc60Gh9motGYp'
        b'7TlG5ew19hyrRTnTZLEb9TnKPJ1+hS7bGOruPj/HZOscazBmmSxGmzLLYdHbTVaLTWm3kqGCzah0wjTabGSaLdRdP6gb+kryM5j8KCgJy8mjGBVzxXyxpFhaLCuWF7sU'
        b'uxa7FbsXK4o9ij2LvYp7FXsX9y72Ke5T7Fvct9ivuF+xf3H/4gHFAcUDiwdlDWaEuxYM3oaKUMGQte7PDS5CC9Exfh56bkgR4lDh4MIhaYRNhOAslSRZ352THPnpTX76'
        b'UFSkjJvzkMo12exKvodm8ag1nGKZ4aGcNwI5RpKvUI5ProRSKElJnAPboDxFBeXxC2aHyNHoWKl8BdzCbVCk4hz9ydjZuHmmQmeLT4IdUJYEZRxyj+dxY4BOzz0mTZ9O'
        b'HOZSdnCEIf8GO7J8nGRz2ySEbJ6QzXWRzTOyuULeSXZ2T2QPfYLsqSLZTYFy1DZzAJFThkd4RARijRv6SFDUaDfKC/Pr2gSxcaTKDR3JH03aMjwalq0SG/+WIUWuVj+i'
        b'oRnB8Y4EVI/M7qS5ZYS/1MP3K8LCj0d/y1+KiPbdyJkpvPuJ+7hGF6QM7/9VLxCmDCJgaPMO9F2v6l5c4Dfor4q7/guFN1E7coSTjnF4H9QTAZSGzQkMhO1hcSGwHdfP'
        b'D0xIgorg0PiQhCQOWXrhEih1i4H9sOkJXrt0Eh5FeU35jLIkXdzk/k1u5vTEzS6gXdxUiNysW94LDUSVgjw8wxyhsCNHCGmch89nERLK1Foog5LEOXHxwfELUKR2Xl9c'
        b'7Yn3z8eleDfKlrnAYbgc6qAKqp0/QYMvE+CRy3E9Wpkrd/hRZdyJG0ZrcCtphxO4Ch9EK6bjegdFZFnEQk0k+R/X45t4D9LjvcMdVMvgAi5PhV0yNGo6CkWhcC6FoSkZ'
        b'rUC+KG6AzDvDXMdzoijH8D5oBJq6WI4yJlW4LEOmX1IPSG060qM7vvpuxucZy7MSda9mhVYF6uJ0X2T43Lunz8kyZ97LSNC9lqWaG69TzdbqGoynuTN9sj83JOiWoCp9'
        b'nM5qrJJur2s8FT59UZlqoDI1+rvpt5NPes2svPo7jwMhaH5O31+3D1Lxduoi8DEfuKggXFIlOUKCiLR51Hc63o+Lpa5QO8JOjcwVjk0hvNwOFVAmQdIJnAOO4yaEi1Vc'
        b'Ox+oUkkEKpJuD548fvSblCVY1xotyizRxYXa8k1Z9snt7sx/pRt0diMdZ/OgAh7mwXlw3pwrF8gJ8k4QKkm7bJXO7DC2u6SnCw5Lenq7Ij1dbzbqLI689PQn1lVxAlUS'
        b'QUYfFMpwCt+Lwv+rNy/neM6dPR0DqZT2e0GFOi44KBmXp8QHm3BtvAz5wUZp/ylJM/V8N+WT9qDRxIN0aTTP/IOEaDTfpdESptF8oeRp/qET8KMaLU929KW4HYBr+BDs'
        b'4vB1OIRQCArB9UNZDz6GD8Il2CXBRLcRCkNhuCmXqa8a7xxBlG74EESVbibebfLXH+VtoaSr38TYuxmLn6/ENbi1sn5XfVFT3LAtV4viD3j0417KojrmkdXxKkJ7d7iO'
        b'+CFexdkD6Eo7jVHqhBDYFp+YLEN4M1xV4CYeDo7B55zC6UnqjPftClHEWWarzs5kTFUdBXlwUiJhwb1LvlImr3aZwZhpsgt0kEAdk4rvJlNeoOGhm2DpdHWXYN97RLBU'
        b'oT1jnsE3ojsly+JIMIcCcqV4ZwLe5uhH+XseX8UnbPax4VLER8PRTAQnh+BLosGXwsVE2sUhvhAZEdTjOtjNmJ8A1VBKuySID/LNRnAWN3k7fElP2EBXm30chYY3aC0I'
        b'zozGZ0RJNsPeMbSLR7wu0UqmrMatrKfPHLMNWsfQZVB/XISgRYpLWExbC5fxWdYnQ7wZmvFmBK1wGJ8WIe5LG28T2Dx80EYgnkuGPQ5/KrGj+LABWhwRDI8rqcTBQUsy'
        b'VImdW+HgWNZJMAnGW4jDglZ81Yehv3iSYLNp2LRW23rCHjVsdgygs/bhTeIsQjLU4BK8H8EVopVbGaZZeJea9bqQ3nMExVoEVwkDaxmXx+FiQn6LzcOdLCmBFrjIRfWB'
        b'NrbiKrjsrRAY/1dn4ZMILsvminheIl5mpwKaxjB0alxJTJfAhiRG+/LIkQr3SEb6PgJ6D+cWgCuZL54zxaaAS4zymFjYwnExPMMQNpPEoNYGLfleBAk4GwpHOTU04B0M'
        b'nhuu97G5eUIjgeg5C25xY/GmGIa7H5xIV6x0wCVE1jpK7LGJG4kvz2a4w6XoyTaFYCeT0uZDDTc4E58QF2vB1/rZ7HBZQbrgPLRBOVmsFo4ykBNwC9TYvDwJNyRwFkpl'
        b'XAyuxddYyBjDpZIeLw5J5PiWGzc181m2ErG6Oh/SsZKQhYxwhQvVhYmIT3tG4ZmHy6RIosUnh3NTYSdsF9W3bkIsVQ+iOiRRupqHoGE5XHR29R5KtDdKTkhqWZxFNfsq'
        b'kTNln9JgowpAJvkXUF1sjlOL8j8PtZE2aIKWXpR9e4nrOc9F4SZ8gZGUhw/52Ugb651NJHyG0/hBnUrJYttfsn24KB4FdoyKXZ826/sk1njy2b7ceB75d2QtXeuftjSO'
        b'Nc7s1Y+bxKPxHanTctJUf1axxh1j/bmpxE10hM4w1gz5nR9rlEYO4GbwSNmR/LExrb/KgzXuCRvIxfHIu2PwmDXvz//YzBpVEUO4RB6Fd1i2ZtXM/SGSNS7OUnKzeeTa'
        b'YZGv8R8+T84aR60cxs2neBbuLkyb8Q89a4SoEVwaxbMwbEWaYvog1jg8aTT3LMUzefyamtyfglijrG8gl0HxNG0p9FdGiqsHWNQkOKCpHf3rbTUL8GLW+HdJMJdDkXeL'
        b'Xl8z8MFy1lg8IpQz8yijw+3FgpqCL3uzxq2WcC6PUrRm4rqaSWYxz9HINRxxp7M7JrRkvC/xTGSNb0yP4lZTMieMyE5bwhewxmvGcdxzPMrr6P/3NTXLZUNZ41duE7gN'
        b'lPYJr5j8C6/PYY0voYncZh7FdSwqyKxRn36GNb4waxK3jTJk0Se5/kEz57LGL2OmcGU8yulQLTDVzPzIkzVe95vKVVIuTVi58v3YO2mssSbmGa6aR2kdptvLa5ZijjUu'
        b'CYnlaijr4j8xvl9QKnL+b5EzuQM8Wt2xpspYo/pc1JA5xnjuCOWnY8S6962Vk8UcT5bEnaas63tPeN9hn88a7a7J3DnKOmOO3r8gTUyzdobN4Rop6/pmZKZJRspY453Q'
        b'uVwrZV3fLbnvz/6YF+2BbBlCbAp3anb4yEQPbipR9zNiCncyME8heHkSU01e2ZuLGb5QnHHRgY8QNb+cbyP+MCyUeAz1iOeYKfSei7cRN0PcNvVOx/ygmhvmjrerpGz9'
        b'if1ucwckhFBFUX7auGMG1ujFv8QdIelyh0vR8vdjpihYY4f6Ze6EhCjOuJuOmpG7YljjkWGvcqclhPrRh7LT0iTrnp5wj0dI3OnRjQ3Kkv0HtjCbH09R6MryJ1KUUcks'
        b'yuLDcGEhLk0hTKyAkvikUCgJG7qER34Z0tHBAxjW1dk8S3HCU5vC35OHiwlvZZ4b8iZt4X5f5wd5TEXM6U8eg/dpw7SwIyUeyifISMK5mV/TF24wzk4ahA/jFtxKc3Cu'
        b't3URwudIAKpnE0nwgR3qwJCgqOGwLYzkKR7Zkl74Zh5zanjHSnwAjpMo3ULQiEbRqxQCZRbDo5WTUgKV4X6qfs+GzRAb/xEsRyQd9Q4fhdRfRs1HDoIpyYaTNeFJBgqw'
        b'Cum8dY4R5Os6Dd6mZRlxBVWjQKjX4oqweNwQyCGlXeZFEuhmMVzXyeCWJooMK6IQqlFmLzjLOBietFZNdlds20q2WvFS1GcIrlBJoAxvx+WMgpxAOKeJhK2wh84lW4ze'
        b'ZqaemX3VGtyM20ZLqSCQWbmADc9d6KXRjIMWOvgQysZHcI2YNJ4bBwc1GhJt2uQ0TUDL+0Ol2HMEqsM0Y0msqqO/1SDDMHzFQU8SYBOcJju8+nXaBIpeMpWNDHnlScaD'
        b'M+eBg/hMpGYsvpVLsdiHjDNI/iJmjmPwKW0imbII9oRBuZpDisUkHuLKAhUvSuawf7xmbATUETMnGUVWLFxm7dE62KAZuwrvo2jWomwPXMHsbsD8MCjV4ivjCbNkSDqY'
        b'w8c8SQiiFMThcthFKLiJLxOjwAdQzjzYwWKXDUrxdjUVCZoEJcm4QYo8Yoh2HMhmMPGFfks0+BK+QfhBGYHMsA9vEXOQLSF4F5QmxvVNoBseCdzkcC0UrXck084NWdBk'
        b'S4yPT6KHE137y8BQVVBSqCqEd8d1RnwSTuITgYG43k+twtVwQu2Lq/36wkaS3Zzoh0/xCG/39cZHCizmfz548CBNKRN1ceag8AWLhyJRNNfcXNXJa/DNkDgpkk7l8JkC'
        b'fEDly/oiBsApm+d4OCc4aF52iBsOe2eJHmpjOt4ILV6hcrHrEqdSOLNXOL7SH1o84ahG7LrJqSPCxUmNsVNtXplwVnDQxKWaG0KSlhKR83gDbLWthGMkx3Snnu06pxzf'
        b'X+RSE9ThOhL+JQvzoZXmG2XcUFzEiZkaVKSSpKugEFo9KcwmLjIph0Hsh8+PVXjhC/iQAlcQ/7qYWxKHD4siqUqCGzb7oDnu+TT3u8ENhF24iTkBvH0IPk5Sq1u41T2f'
        b'rrWRUw4n+3C21uCZ0GKPMwjQSujCN7kAX6ICdJY/7IYqGzTb5YgbICU2Qcyw1TkLbyA7rK0K13EjPMmOQjKOi8OXezHCphKtOE08C66BipUeFPv93GhcM5pNW4tPkZ2Q'
        b'F965woNsVSQTufg5eA/rUeGtwSQTssMmgeSaEi9u3Co4wOganB1OOsiWbiM005AyjJuGzymZES1LhOO2lfw0tg6+xA2GcyNZhwRfwfU2d9RfFFYVp0yYIQprP1zCWxTu'
        b'46Gcdkl8uHC4vFpMF0vhJhxbjG/ALmJAwSgYHwwQRbUDdk5fQ5L+0l7uK1dxSEqyOFw+3znr+jNuhKAiONVJ0cpU0xf+I3nbXmJR2vOlS6tuJf9tqsftL/fF84rfr1/1'
        b'h49+x/3l7WFHY6dvq9qxNfNyS+Vsb58/n608FT3tHwerI8cci/NOmfG7Pt94VLtWaP6Yq/n0/v3a138Ysfv6hvbE9Jhw7886Iu6dej5ulEuk4cEfQl8td/zx6Ea/rL3V'
        b'M/y+v+O/vG399jUnzr34bUR0Gu+ofHv9FxMX53joS+f2/kOCccKYPUmlre9/6Nb/jtep7I+a/zk7pX7XlX599wwK6XvyOb36tVf0q1f3/vaZl4qrdsellp74ubqg4fkB'
        b'2TElfyo9cVsIfHNmhk989ls3rlze9mHDH3HcZ3EHLx17+1KzzfjLS/LYIPMwQ/ZrQxf+/fDLjb8EZA25HTBl98Ivvj2r/3jplhiX26GNL491+7L57jPf6MGCzC665V8u'
        b'eOfrpTPWub0U8Bd94xGLreWDrdZ/rPNo/boPf3jVfUXNsp/KWkbVFfmN/tNE6wt/eefkJN3Zs5/OyHrblvfSRc2qyTeGCDX31W/Nv5u99JcBQ/ghn83e+NFn7tdafo0/'
        b'duqZO2/FevqZ7kR/ZIhavvKzoANvV2w61OHuZ73JDZ1dJzv0q8rVzrw02ZGXQ2lwMpRMgSOJUEF2ugp8ljhbLVSybfyIQtikDo0PDlKFkl4SqaGU2IVSuiysr52qRqJq'
        b'oPNoZ2vX8Q5uKvBgBz/DJsJlom1l6lDi6koIbDnewYf0wRvsVBPz1FO1wYFxUK7Nx0c45ErWXTNGzrrgFLTNgM0SbXxSUJILkkt5V9hSYFfSruv4Ot5Et+cEIpQQ71kh'
        b'QX18YPdECdSuxJvszFfVZsIxbUoINYp69SpiL1fxOZXr4ycOT3uoZE/vf3hK4SOeUtgFncWmE4/X2WHFapr8THfnXDk558t58K6cB+fFk28S2ubDuXP0sMqVc2c/Ppz8'
        b'gZT+8N7kt84P+c57id95dxc5xz+Q8x7kNz/em8CTyqXsuMuPPOXk40/g0+9enOCBHh5+eXRHrdvxyNOpU3GCZyd9DNQzqPOg5JZv94MSFfU9g6BKPR5fEk9KwlQk2KmT'
        b'E0NFmajlaBY+54KrB8JBlejT8V7YEKaNDyaZihS2mhEJii5PnrN7dmaMcYilovSMHT15yp7l2ZWa8r+ZmkpYair9ey4B7K7s9m82lZ5NqXv0JoRdr6zJMyqT5k+IClda'
        b'BfYlMvSRqY/8Em9XCka7Q7BQWGaTzU5BZOosK5Q6vd7qsNiVNrvObsw1Wuw2ZX6OSZ+j1AlGMidPMNpIo9HwCDidTemwOXRmpcHEBKcTTEZbqHKa2WZV6sxm5bzY2dOU'
        b'WSaj2WBjcIyriZT1BAodY34EFDv7FEfprZZVRoGMohdADotJbzUYCV6CyZJt+w3apj3EYo0yh6BGb56yrGazNZ/MpAAcekK6MfrpIEIIDw1GIV0wZhkFo0VvjHauqwyc'
        b'5sgiuGfbbM6+tarHZj45h8gjIyPZajFmZCgDpxvXOrKfOpmKgJL5cL3ppMVsNNnX6nLMj492yurhYK3VYrdaHLm5RuHxsaQ10yh0p8NGEel5cKbOrCMUpFvzjJZoxk4y'
        b'wZKlI4y36cwG66PjncjkirjMMOpNuUQVCKWUUT0N1TsEyqE1D7FZCCdyBIelx9H00DyaPQlMhz6HDLOR3xy5T8Nab7bajJ1ox1oM/wdQzrRaVxgNTpwf0ZdUYg92o4XR'
        b'oMw2ZhJo9v/dtFis9n8HKausQjbxL8KK/6XU2By56XrBaDDZbT3RMo/ajXKWw27T5wimLEKWMkz0ukqrxbzmf5QmpxMwWZiVUkehdJJmtPREFrt5+A2qphvNOpudTf+/'
        b'QVT3lCG6K5x1j0Vd/i7ParM/DsCpGUabXjDl0SlP89xU1kZT5lMwppHLrutUroUkcpGlzOanaJhz0Yfq+OhaT1fN/zDfBSOJosToopXEy5CRc6FNvyJTXKCn8dQXEeLT'
        b'Vxi7iaoTIcICM7TZbEbzb021kwD/FCY64dARPSP7RMTVOiwGo6XniOlclsTIHmL1owuTMb8FI3vVo3F3FpU2nMiy24inyiJJDO3uaWKeQARAfJ6u53VnO7uNlpBkIfRp'
        b'2D+y9hN49xz/nYrwWA7wyOSn5gPiXBNZuueJ8dOnJT9d7dKtginbZKEq9aQPSXH2ZTKFJAasnCkYcw35T7X17pD/HQotDv8POpMcHYk2Pbq8WcZMaCNm3YNP+B9AjJoB'
        b'szPq5x7Baz7p+W1js+hyjQ+9nTMvVgYmk+Ye9dQh5LG86IkZqUYh32gxULNcm2/Ur+hpts2Yp4vunlgTAN2y+h5mLLFYlkYrF1hWWKz5lodZt6H7PkBnMJCGfJM9hybp'
        b'JoFmqUbBpFeaDL+V4UeTTawul7pNgtP8nMfqwh6dGO3c50STfUFPkeHR0Y/cBdAdnR96/C4gTryY2p/MI2ngBUQrl5as14pn6XfXy5CrvYSnRUr/DJYgVqSgCzDgFrK7'
        b'jYftE9HESFwiXgMFuiCPxJm0HCrYEh+HxOPl2mkemkgEN6BKPPv2gTrHENrRnD5R7dys9l/+cLs6dIhsADTYVR6siAzvwDegAUrDEuLD8IUQvD0sIUkbkgDl2mQZioBy'
        b'uRrO6NlxtccSXKl2ds6GvbTfBx+S4EbDKvE4+6Qk6NFD8D5wKk8yfi7Ui4UkVXgfHGPn3WFQjnfCoc4Db0OoeIm6Gd+QQqkaypMSQvjwBcgVrvJ4O2wNcAxj3TPdKfx4'
        b'KNMmZ4zE5VARFgflEjTERwo1uAFvYTcOsAdKoVFrndw5lBY37IASeusxQi2bhMtgJ9vW4zNQhou6IEKlko5kVxXJSRxS4TYZ3g8X8S3HUHY3MGmSdnjKQ6BkXGlYPBk4'
        b'IkM2dQ1cY6Og0QN2qlcYQgmB5SmhCUlQEqySowColWJ6wVLL7gym4wu4VC2OiU+C7WRInh316ysNj4RKcbWKSemdsoP60Y8J7zzeyLRk1YDxmkhpzDJ65IAMg+Eok4Pb'
        b'kLGdYnLgzQ/FlOa8CZiFy/ElTaQMGoLY7UEO3oC3sWsFuDTFBrtc6BE4PhOOwgvwXiaYZbgUlz4qWteBRLJRC9h1Pr4yFE52yjU9rFOqPiNUPFuwL94AVRrcnCdHXKIR'
        b'diN8vtCLLVgYj2+RDoSPu7KrmBVh2aImlKwwdSkCHNI5NWEl3qaSi0cs9bgCX9Ro8iSI004LRbjBAJvEs/HNCnxZo4FGGeLmpuB9CLdClUS0lGa8K0WjEcicFCveifCF'
        b'AgXrcDGPITOayYxUXJZCSytag8QZNbgFLmg0XOQiWlKEVsBGHUN8Ujo+odHIYJ+VtB9HZqjmmYXql/uhYNd8nljoc59pChG7hcoqhDobR6Adg5uxKBYfC2BjK2b3Rsrg'
        b'Jh7lZZiPzbcjlYSZCb6uWkHvSsrZjRDULyXE1/B4N2yEXYzdNmiTaENDgqiN4vNS1AtqRqVKzLlzxGPv7b5z6NmTDEn1UCzl8GFi3zuIJNjtwBVcM9bJNSiHTYRveBt0'
        b'VuAs7NXJt1BCK251wElmeEot1HSZSQ4+9pjlwcElBDzVxxE2s5O9wyYQ7npNcl4f42ahk79wdD3hL26LddAzTnw0Pk67tuAplqoNZLy2EExLiAzW46uiEJbaHKMo3K36'
        b'zC607H16Mt5zhGWMtmJ8RKDyqmZOkggsDpeJ3uIIroSbWtiz6imWLQfRNvDldF+NRhqNd7CrxBwoC2FSnLDaCw3M2Y1QeIZ5oMKBVL6MsvGwKVwbMzE+JDmU2Hdg5/lt'
        b'AC6W4jqozmbXDbNg61h6L6YKiZf69kFuLjzeQZzCHrH26jrRvgtOUcIJuEJlKRvE7GN8LG55qCMLpzhVBB9wY91wCV9bqk4I0YYEJdNS3164dmW2xGggkqbOJWXtVG3v'
        b'qIeXslpMuUbv/QISpbgqaxDjTIYGn+x2c6slKDQ8cnVrhbPM34yDLQs7HU6I5aG/GQaHxTLlSti/SvQeeEdYAmzB+x5GmCC9DJ+FSrNo9i3JsMl5vy1Twgnxfhv2EXdH'
        b'L4LVRHxXu10F94Pr7DaYXgVnRzPjMeErsOFRTzV5JL2LrccNImvqw+O6QtBG3NbprBzPMqav09GpieJ1plscu9DEVUmOIIrdPmhcJnJ9Ct5IGI9LiB3A9kR6H6ClfI7E'
        b'e+Xx+KaICmwmLmoLoSUuOCEFl8L5EDlSaIk3g0NzmB27QQtuYfeuUJK8elbnvWvhOtFUicoqoFQr3uS6Lad3ufjmItY3GG+dRi/zYVuYh5/zMn8SlDLFk8ZB9WPlBjze'
        b'BWdYwQGUezOTHIPP4KZO1aqEcqpa2nymkxwughOdSmmRiEo5CtcwA1+fBHUKninYwXloXoCE8TQnjISmbtoGl2EbUbe+sJP4BeoAY0bhEuYA9+H91AGeN4hOfOMMXKYQ'
        b'5HPgJBUMSV7wralsQlB6Guyi19QnYW8IClkHB8W79r346ppuvvHGmE7fuBvqmTUGTnRD3tLvaRl4oveESLFOfga+NVMLNyY+VeOJYz7MMPLFTdACu2CvC4JTNAqj9IX9'
        b'mDUE4L2wo5sSX8GVjynxjEUsZPgTIq/jlnCJMoYAOI2sUDbbMZ+qVgEU255dR7QLyuPnzMbN4fPmwjZWOx4aEkhEGeS8KZ9HvcW24NQ4KkOmH3PigmkP8SHaBbOJtBC+'
        b'ta43LlfEsFvxWjtJIFe/xpEE0mz0SEbMZ0NLClx4Qg9q8CWmB3gniTJicMbFvXjcEkVj8xw/2Ewigh43MY/nMWYQ7eBIPAjJJzF7HD7lGEPZSQCfhF14WzzsJMlWNd62'
        b'ijzK8XbcMBafl+HmUdCQOdeeiS+OIVGmTL6IOKZatlZs3phOiKPwflo0dwmXkrBH9U6Kz4/QimZ5cxGxSnk6H0QkUSHaUiO0TXgk5qXiBhLzoBIfYj4Iro+AyoeaoYWL'
        b'Ts2QuolSmYebO6lE0EqoHG500KpnBa6Fw2riNc73mLLhg7BZLOPZshY3PJqy4Q1xLGeLgIsqKeOYLRlOasauJAEwIQDfIvRJPFi7I7e3JkoOJTNYomYknuEa48ccItIL'
        b'mqhVhCFToYyItR6uB4hZzKbBeD9BGBqJRaaqBYSbB+Kzznc5iAs5CBtIbwTpnEl4QEznELThIge9xVJmw2YFvewkoi8lljkPGj1xU1TE7Lgu1TsKJXNDUuc+rlVEtQ+7'
        b'w37lPDH3KcKnCvBZOfl2FW96Dj2H6woY1otDA/DZsZgkLryfwxXBGaIGF5h7mC5bhc/KEJqLClEhboPr7A2DuYWw3cYq5ucG0ttMan8L6cL4ZJ+utReGuODdNqhxTKTU'
        b'7yWudasiOYkElFRqI2viiZVAycK4hAVx80V6cP1s2JYUEpqcmCJD+BQ0uuMtSbjK6XHgcAxcpK8WkNz1cigKHRoiOtVawnvSjhtkffEB6pAQPrskiExiSlQ1lQSP7lqW'
        b'CI1EyzgsVvH2wi2mhzoWPtqpYkZeLLEqtwvQkg+XaB0HbiQmcpmLgi2pDrW417gBG52Tt+HGp0aP+a4MmCveA1dtcCmvlxzxswgrS7hRJAkvEsPkbtg/zRlYAvjOsEIW'
        b'3M7CewA0Jmlxg7bn3CMHjrHiLpPi+0jelk2+nk2vdcx/vcI31vd8+ocxH759faLmXHARbDpyfcPPc+cUjufPn41YFtF714tvvyJ8fuKlv336p9XDFrjpNpnKiyfUluxL'
        b'ntS711aNyyf7do1+IH1AUvei9BuHlo7t/dad8xdunln79bvr/no34fUZIYVv5W/uN6LthbNxa5feSYoosez9aP5Oze6B6nVNc18rqxv32quGkPDlc9V4RfbM9C89ng96'
        b'6+KBnJ/GNY5KOpm6pH3W5B9KSlVB1b9A/E+23dHxK9PL6nyTXy3b5ZjqVvJgSr505NsfwPI1HmMXN/7rCyPHH/aSXRn4rPyr/heXzn3hh/S9z9uu71nivu7bo8/n6wJf'
        b'9jvM7T/97ZADi4I/KWnt36J99VfZJbjXii1fVK0+8uPQoD/3e0f9Tho35Igl46w07c2NG35ftefUfus/5Ycf7GgYvPm9sx2pNS2vDuIvy8+nB+ZNicz3f7bXB7UdrQUv'
        b'f7Bh+DX0g2vLhDGDRza8FnNz2LyfbH6Do6OX/vDxqLMFEaXL01pfsamzClve/WysuvHzxXZz4Om7bzdLfvb7U0DWu6e2qWK9dvRz/8Dtb1Ge+ilpP296dUbBg5F3lQaN'
        b'Y1FjnLVf06zYZy/dXWdYeumyeoVwt3fp6xGv/2PVL3969fNBHyz5c3Hov2juz/jyg167D14I+jzhvuzwkbmK8zFeKxs8r6a2vpa/4s34QxfGHcqKOLhpVNTqz2+HZU76'
        b'Y/sG96O3Ut9Ivy+9X7j3uxt3fCMvbHxt/qbXxhd4978WVvuL3e/rCZP3fnPV/V9eO/5y+6/LLma7LUUXfp5r/OCtc1vSRjYHVNaP/MQz58ae8d8te8P3xpT3XnO5d3/h'
        b'+QcvxrxY6Gr3OTuk6Zcpr3DfjLxd8YpX5vV7macuvzvp5vvq748eqHlz6Fe31R+Uh22Yd23xK29uePP3nqUHMzPvDTvnkW91/Tne/5lxb4/5Z8SqT9/98NpPF1x/xUHP'
        b'fdRuvWM8f2Tai9E77o2dteUr6UfoNX7Ugpr7bYM+azmQrJufNOSn5N07z2W+t/GLP/qvr/vLrX9+9SGc//Taac3NaUMLjm7++v7fAr7f23tKsG//YetDY1ef+dn47NBm'
        b'a2y95cu33fN/enb0NysLzsyuGPxhx7aU4+4hP1ava50V0FFW8MIH2Z/Pafnu9CSvtpKfZh2/cOe7DcXTCmp7ZwqfVb2RGVg5/MWXt9+LOTemPWJo6cSiXyZ82h77w8cr'
        b'fq345GTc5QeSbTNM+N3lKi9nWYc3SWLFOhFimdT7hsgxyXL64UtSImJWjAJn8AHYqg4KVREDRnjDIuS2iMd1+CpcYO8ijYP6nO7FKiRekGyZVqvAPjjISlLwjcwYcZmJ'
        b'+GRnRQrZXlTYqQtZjRvCnTUpHInhO8SiFHwEX2TrR8HFTLFahrinQVDVVS0zayYrp1m4NKyrMEVBYqRYm0ILU/ygxs7KfOFgpDo5KTiBwIZqNYF/lc+X9GZ9AjdbSzxf'
        b'GJzC10iAkOfzodAArYwyEs12LSZ7U20nZcTrHsL14ZJsMqSKVeK4rYEWZ6ZQDhudqUIKFLGCmvg4vENN2WZQBxPQ+ByvgaOhjCPD+8AV54s6cGsISdvE93QCn2NyCcEN'
        b'sJ8kf2VaknHliS944SNLUd9JUgkcgFuqPv/eopr/5EPl+V+H88SbRbn2CVHhrFhnKq0/WY/SXDmp8+POCnPoR8rxnAfnQwtuyP/uPM/1+Pne3cuVFfS4cv6sSIeO9Sf/'
        b'e/0il7lz3T8iFC9x3tPgiZ+78n5enJKjZT9Szpvzl3hzXqyUSMoNJE9fAsWb937gzsk5sXBIyoqEyLq8B0+x8RFX593ZmuSHp2VGcp58uGGkRU6xEXEic+W8WJbkTqD7'
        b'c76kfwCBS2fQsiWvX+VSkQIvvrOIyZv34hkMXuhFeJjcWXUkpWfJ3aqN/uvyU3GCd6cE2VpVVHK0CW1A34zoXpfEDkRrppO84hQcdL7DBRUhNNFDaECeBK5CDVx/4k06'
        b'qgRTKVCaJBnpq9poMW/gFksMvPg6abs3OxdnNUNCrCBYhR+HiCflTKEEZwmQ0aDUWZRG2h+arJK2u6an06uF9PR29/R08Z1s8t0jPX2lQ2d29rikpxus+vR0UUsfPhi1'
        b'NH2sINixyjJXnuXmeOdkT4UXXLYr3AiB1DklhwjOVy/D4LBcFjhVxc007XswWGoLIHPf2DYlpiI+GaZ6x17/cFVmttJ2IHzrmkPZrj4TvZ7f1PjKJ3+Yvr1atnrLC/Il'
        b'X4z1GfeSrkky/WL9g7v1he/u/WlyVN9dFSOEEx/JF1W827c+dd6Hv777/r7s9vFvVitenLJ3hfu3N5+/8XpbdUD9e7rAfx12X3X4hSvDY1Nv9wpx3/nqB9kRoR6/jh2x'
        b'5ss728/Ltg+rez/JNz/61I3nM7cm3Bs5dsHyd0xvnIgNOOy1NGuf/pDMb9Gxql9+H6k+13w7OsDc/OLYifeafz/ZZaAQdWdklT55/P8r+67kYNri5eo/htxd3pH3O+P+'
        b'uzXXVDV7VCf/sPCvc0vty96pq94X//W89j/tsHx+8oeiyPc+eMHywyvF4X93+V3IL2lv9FpwYtg+1xeOf7OsEGVpU1MrrCqpnZ234guDSZZ/bnoi2XKMR7BDrxPLI6sH'
        b'pHR7tRUffYa+3UpfbcVHXOxUFkSbDuCNimm4OojkrjRsdb0FOwS3SOHC5HjxLdmrcMtmww1xyWRPWxIzSwwNvaFSghuHryQKzvTc57/RjcpZevv0B3OPRF/NVp0hPZ35'
        b'xjxqGn7UT0Vxgx/wPC02JN6Q93b1diG7HPHD/ae+3Zd7OP3cT3JX3xTqZwPXo+d4TujXaQDE6HhiFQ8dSe//HsZwgn+XubFX91BnyeO90CdcyxFchWvIjoMemJSkwD5c'
        b'kohLcIUL8uovGYQrcJNp3XtvI5uRjP1k4R8G3Y7w2jTVe+ub67PyPe2ZdVs7jrbhF5ZfjvwyuG74/feXPJ80pu2LLVvOZBVc/PPv81fc/HEPfpA/L+3E/r/W3bnyRf3I'
        b'zTtV9u8P9L/S8ezVlaMjIv91tefO48FLW9499MXeIS/e838ny0XlYqd3Ws/harIvrYZi9rpqCts7uZBA3szDaXxmGhsDFf1xozYlBJrokJSQ4XgvTzSwTYKP4hZcK2Zh'
        b'e2ErtIj0Eb0Ph3NJuJyR5yMZPICkUHSjOz54MavL1eLjztLcc9DG8qN1+Co+rMJHtd3+noJCxUNlYK5oT4ehDa5JoOSJP7iALw5klvhcCD6gTpCtxqcRpyXWtQY3dhrH'
        b'4P/mROM/qz/S3zQnk8Vkd5oTPT1Anq6d9b+S4PWIfpDQv0vlle0Ss9HSLqUVqO0yuyPPbGyX0qtWElVNevKkVYTtEptdaJdlrrEbbe1SWojSLjFZ7O0y9r50u0zQWbLJ'
        b'bJMlz2Fvl+hzhHaJVTC0y7NMZruR/JKry2uXrDXltct0Nr3J1C7JMa4mQwh4d5PNZLHZaelZuzzPkWk26dtddHq9Mc9ua/dgC0aKV93tnmIiZbJZx48Nj2hX2HJMWfZ0'
        b'FvnaPR0WfY7ORKJhunG1vt0tPd1GomMeiXVyh8VhMxoeGrVI9mBhLP0eQR/B9EFtTaCbdoH+gQRhNH1QNyrQC0qBHjwK9AhFoPcdAvXDQhh90BReoIom0INpgb67LlDV'
        b'FwLpQ0Mf9O9TCPT0U6Bv4gtU6QV6lCZQ/RXoOZ4wjj7UXT6BnUl3+YT7M7v5BNb3o2vnHyho905Pd353utEfB2Q9+vdZlBarXUn7jIZklatAfQ1NAHRmM3F1TA+oFbS7'
        b'EyEIdhu9zW+Xm616nZnwf67DYjflGln2IUzoZN5jGUO76yQxz5hMcxqWz0ipjYq65u1LsHbl/j/L00td'
    ))))

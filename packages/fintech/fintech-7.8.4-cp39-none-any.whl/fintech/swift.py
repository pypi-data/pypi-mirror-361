
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
        b'eJzVfAlYVEe2/723F6CBFhEUUaE1LjTNaisRt+CCAs0m4IZL09Dd0KHpxr7d4oIrIpuI4oa7oIgoKpso7tZJMhmTmUlmMolhMtk3M5mZGLPPRP9VdUFRMf95875533v2'
        b'x7Wp5VTVOb+zVNW5fMQ89k+Ef6LwDz8ZP/RMOpPNpLN6Vs9tYtI5g+iIWC+qZW0j9WKDpIhZzvAhiziDVC8pYjeyBicDV8SyjF6ayrgYlU4/GWSp82NnpSnyrHqH2aCw'
        b'GhX2HIMieaU9x2pRzDJZ7IasHEW+LitXl20IkcnSckx8T1u9wWiyGHiF0WHJspusFl5ht+KmNt6g6KZp4HncjQ+RZQ3rNX0F/vHDP65kCTb8KGFK2BKuRFQiLpGUSEuc'
        b'SpxLXEpkJa4lbiXuJfKSfiUeJf1LPEsGlHiVeJcMLBlU4lMyuMS3ZEjJ0JJhRj+6cOc1fqVMEbPGf5VnoV8RM58p9C9iWGat31r/1F7fwzC78MJzlKLErN4cZfFPf/wz'
        b'gExJTLmayiidE83O+PtNNxHTvpJ8ywhSpvgxjlH4q8MLyqACypLi50ApVCYpoTJ2bnKwlBkTLYbd6BpcS4YmJesYitvCJo7nYxNgK2xJgC0sg0pGyGI51IzaUFkW+5hg'
        b'PXumkU44w2Le/H84Y/Ts5gBbKsIc4DAHWMoBjq6aXcul9vrezYHsvjgw/AkORAkcaFsuZdwYxiNstPOSyMI0hhYmB4oY0jBsuVHy7bxpQuEzhS6MBy4LiwjNfDV6tVAY'
        b'yksY/L8ibJZHXFV/B9PImGW4eKiTj/gbTybqN24fjPma6wi/MXMCa3bBFafG1rDNToyiOWjl2Hdsg1f+iqHFCv7rfjv7sQFRi39m7/mMLpAwXYwjGFcsUWZiUVSEzgkI'
        b'gPLQmGAoR41pAXEJUBUUAmdgd2xwXALLWPq5TIGqjCcY7tSzaqJNlNmMUfSApey/zNI+QfWA+AOWugosHTatH4Ox4RMmnW2ZNaNAWIhNjurwSraoNLAFyuLnxMQGxc5l'
        b'xmpSvdHONFQBJzi0i8mWOMFh2G51eOEe6Wj7AjU6j6knQSdqZJbpYZtjEMHcTtiLrqhRO65SoK3oIJMLl1E17QQHl6M69VgyNdSCdjNZObDLQXCHNiY6yafBDgnDhDAh'
        b'sBWdoHO9O1TG4H7OYca/ihUe8YJQJ4d5MiOJ+ENWejezixiT4ZsOltfhknvz+L9kfP5hbcbzxnjdq8aQ6gBdjO6LDM+sHKM588uMON1vjcqUWJ0yWaM7bTjBnhyQ/bk+'
        b'TreIqc6K0VkN1eLy+uaGsOkLtyiHKuZNvDv9pcTj8lnbOm+4HbjNpGm8P7hpUHJ2olYLlga4YkYpE+CUhyM4EIueY7xRidh5IOy3DyYN0ObhmJ3lUNXfBbZgtEayeL3V'
        b'qFnJdnEBSqXIRqTS68Hhx08DJxtt1lUGi8IoWL8QvsBktE/tklHTptXr7AbSjncjMh7hxrqxHqwzG8DapD0klKIuyXKd2WHoctJqbQ6LVtvlqtVmmQ06iyNfq31iXCVr'
        b'IzixSciDUHmG0CdLZN7z4KQsx0rpk/snx2FUscw98hs1LUvQFbRHFRMUGJCRiCqTMF4kzEDYIB7MoMZZWVwvNIr7gDq2Lw+gzlHrIcJQ5yjURRTe3FpRaq/vT4N6zwCP'
        b'Ql2a6PAmqNqCLqDzsAPrA7SjimAmGB2dRYGIdqJ9sA12YDUULQtlQuEY2uYgdjgWlYZRGComESA2x5q8X1gt4kNw1Ur9jL9kpF/fhmpQ+7bGHY1FLTEjijuLYg+wLxsj'
        b'bn6OQedmfN/MMntOOkfN/UHJUiRoBs5TxQVDaWx8ooRxRS0cOjATDg6H6m559QUEKo4uV0HqRrNVZ6diJ9hnAt1YMRa6TfZA5GIqwi6J3pBpsttIIxuxWUqul5g5G3F5'
        b'vWRNuqseyPqtX5C1P67PGZqrWgRnsLCJqKnzCWKZIXlitB2dQOcEtd9WALW8HUpga0SYmOEyGTg+DpXROjs6jDbiusaREWEswxkYaMTtrlEZwXGodeHtc5QRYSKGy2bg'
        b'lB3XDCQ1W9ExOW+PgIZnCUELAyeDYCPtNB/K+vP2dKh4NoxjOCvuNB92O3yIYC+hM/14aIdjS8eTsVARA23roFmoPIeKAkllp3p8mARXbsK4gIoFwgKOpUMnb4O9sIv2'
        b'xFSb0KZRdCqRhdHQ5oA9EeFkJtgUQhucW027oQb3NFyH6heEk7lgo4ZJnsl3EECqptp4HsoT1aTXOgbOJMspOdtibBraHHFQHE4WjfYxcGGQnk4RTkQvJ0NtV4SHOeGq'
        b'/Qx0wkloFCqPw0F0GNp4rHuH3WR4ODjHjkvqT4miBlQy2dUGJQzlPzrOwHm1n8OXVO1CZ6HIFVqgGeHF4VocDIhQKeaZYLGnwhFX2WDUMZYsHHazLlCMjgpU98H5Ra7Q'
        b'sTaULh2KWdYfOqgOFcK2STy0MQsL5GQmtaxKZhDoXU2HKt5lkdwdmgm9a2wE9gONAr06KPZ3XZYFlxzQweDKFnaUUkyFGj0YNfOuz0CLzU561bB+6Lg7rQkw5fB2DaqE'
        b'866kppJVTYT9dA4haBNc4eWLp7tjbogk7JQB6KQAqzYjNPFyGZxxl7OMyIWNQsdHUqGM1+XzctjxvPsysp4LbAivoT1U0ajR1T0cdeSjLWJG9AwbFQBVAhBPolLUwtt8'
        b'0WEKm3wGTkuyaJXrCKjn7agemiLGSRnOiJGdjdlDhGXBqnGS51EZ1Kkp2DASW+FEAmXRbDiCrvHQ8nwqtPUj3DvDjsuCLVRaUIKKoYaHDlQNZ7urT7JqG2pUKqgDXN1/'
        b'ADuOa86QJV/Pq4lqzaaFh6Xe7ATuxHBJ2PW8W7G1a2jh2mUD2cnckVGSfFyosYbSQlu0DxvFOavdmOtrfMK/ctDCGa6+7Ezu5THiqOtrbqnLdbQwKXAYG8MtiBEprq9Z'
        b'MOuD52nhuQx/Np7zieIycMspJ6S08I6vgk3mFKOdPK6vqZnsM5wWPjt6BJvG+cSwybi756+eoYUm31HsAi7Z1C8Mj24cNJYWvpA7ml3M5Ux3zseFvt8H0cJKJyWbwcWM'
        b'cGau8zXO8sG08A2rCnuN60oX5gbvo/IaRQvjM4LYHM5nrGsUbimPnE8LP3AKYc3chHWSqBv8Aum9dbRwv3cYm89FyeWK67zPoo+daeGV1LGsnavxclXc4Gs0DSpaOHTi'
        b'eHYFty3dLQO3zNcW0MLhORFsIecsdsrAo89MF7prn4tk13Nha+Ue1/kFz68dJrCOncRu4hZ4u3rg0bO/X0oL/YZMZku5CbPckzHNhVPTaKF62FR2C/f+YufkG/ytmbWp'
        b'tPCLCdPYbVx+njgMr2j0+Bm0cMyw6exO7uUgcRhuqQx2ooW+o6LZGi5GhkXM3wr6bB4tlIfPYg9wX1nYfNxycUg8LdQ7x7JHuAk4SL6e6+M3dzItHBuQwJ7gatIlUddz'
        b'F5gl4wRxpCexTdxrFi7qRu4thVwAw9xVc9hm7paOVeDulkECGFbNSWHbuYyZLoobuT6GEyaqlFOXK3lXOI0OyIjqubFRsE9MK4xQgxpcbWthj9wdq2t/dsq4tYJVqFHm'
        b'Y5N6HjbqC3gRNRmq3ImCNnTCDjiL7QzaCNXYdhMDsJMdgS7OV4rpFO7PeIk9IPphOJd/o6Bm9Ko8Wvh16K/ZI6KXY1jmutVn+hEBUPLYm+wxkUIrYm5YfaTHhwp4HP0q'
        b'e0KUvIyNum6tWfFZzNOj9CiGEbaLZEvEGCX/xubnifCFzEDKPB6+jE6kbheOTsVRY4W3XxLewFVBWWxCCJThUHNghnhMGqqh048bwjHioBKObBFbJclChKxdgfdChZc4'
        b'JiPDXJcymBGcQB32Z0c0sHN5qAa2JuFwzRlvD1fC3iVUBPOSGbwrbCdhO7swDjUxqMkE7Q4Sw6CN6JiLKgD2e+BYtzQUBzJu2aJ+sI0XgqyL6CpcQG149lA1bSIzEVu5'
        b'szbCOTqX16LEjPNii4iJyjDftOYIhd9h3+aWbBczioygdzwLGYqOXKgZrWZgfRghWs3o4Bza4CCBvtQZ9mpIMI0/eCerwQ4aVYXGotMBLKOwS+SwE52hpn1wOtqtRse0'
        b'4wiFnUwmtOc7yH4fHQzzxPMvhy2hS/E+GG/YYsXMAKUItqCTqE1w44fRNbRBjTdtVWR7QvYmcBouC76kcnqgGjZCKWoVk5aMGS7MEtbeDhdgjxrOQbOa/HqIyeYK6VSi'
        b'3caqJ0OpGgsX1TLPA2YhLV8IDXPUsCU+gqKe0aPNahpOz0A7oFwTRyaXKEhHboa9+aIJcHSKMNQhzI/t6iFrIsgc9jIGKEPlgmBPpkCZJj4XteOeoVCpYhnXdOxREhcq'
        b'OcrYpSrAK6uMjOCIP8daeAXtpDRHwTU4rR6K6iPINPcz2XAKXRVc3h6o0UIF3uQkSBixH5vXH9W55lBqq9znqrGLKo/AioIOMDk4HCyhS5gDOyapYlEJdpenA6AsEZ0W'
        b'M25TRP3QBThN1+6Jjo5XQ+0y1EFmfYQxq/IovqLkcAQq4uPITkkEV1kcq9ei/XB0mSORNDyGrgbw8bGxCeS848EONSBEGZgQogzmZKjegI7DcXQsIAA1DlQp0U44pvJC'
        b'Owd646h+Q9Ig1MAxqNzLA48I58w/3L9/f8pqjMnCzwgm3QaHrmCE4KoYW6BSVWJwjJgRR7HQgi6jk8/BWaVXd8i5ZwHvbnMQ63SIhdPyZ0LReQEe11SjoE0uVHWwhaFK'
        b'aJpDuRjtMQPauvtcZUdCkwptwMwiVStdYAOP+wjmDC76+GP7JkhldB608sscMhK9XmLR9kBFNtpOGYWDhg2IRAYF0C6hQZwSXRgOx5KE2stQi+m34Up3lkZWUOw51h0d'
        b'EWJRtd5V7oqqsN1NZzV6HM6rBFztWEBic1kBiRmvsFK0dWiYgdYMdE8k5WSgDWwcKlKgXbBJMAiHVkMdtNlt0E7C16ssugbrh0C7lS6tABWv5qHVLmVYdGg6Rj9UJSAh'
        b'ZGTnwzZXZ3e8+xA9y6L6jBio19AK/zVROOpd5kbmvY9dPmDMKmx7KHNPS2Czq9wNb2lEk9hIuBiLapfQLmGJuEs/G449RXLW3f9ZaEVVQvh5Pgytx1XQSpzMCBYq0NFp'
        b'w2d0Oxp0dQq/jA6EOtg1Wj9s9HYIkN+Ge+3gZYK4qlkrOqpQGOlQ65aludJykSeLioLCMEAPUqbCTmhA5bCDqM+2YUFMEDe5G0tOfqii3yLUKFu2nGXEOLxDlVa8ryGd'
        b'UPO4iQ9WBOeSYlNDTR+Exon4GqxRkzUvLamekvRxlNvmv+6N5V6583OLvuqjtobo6RWbPEYNc3/R8pn0k3bPtwe8+OvUZWPq4ysDPF8IrXt/0FdDAvr7Zft27L0zee1n'
        b'56bEfhJSG/HRoH5umyJXuP1jcFj1rze4vX2/1ZWfsYTPOVJ823vUdsmaiZt8x1SFV+08t+BepXx31LCPv0n4ef+nvnCrLm1ma8rCxErDH0b8pqBg+qyLcKfzfNDUN1K/'
        b'GPm36GLDbNdipfbt8rtVw9+Z4rrQ6+szemX1JyOUz+m1yuaXTEl1fxzR2DI0pn1gzczf77WH/i04syD3Slh15LyGys/bG7+c/vY8/c+rb7cOdXn70LKX5/7cMNbsj74s'
        b'WvFRw9dxS5ZPHPju3FupGV9yp8w7Xgtdvsjjn7ea/yL609qa9NXe3y4a9LqF+/ql78RBJ/70atD5D/70V/cN362Z/v4fQta5fDTk8LI3j9lf+/DlVZ9VrtjftbPB7Bi2'
        b'y3HgZfMqubxz+Uu/bdjBNqTcV/8+7S/ZS372/Tvn/3Hyhnc/lV1suxdb1zDj9u+j3d+dcXviu3r7Gx++MXfC0edkqzbm1tz/XhL8df2zphyls52cJAdjLW2BiiAHKkvE'
        b'Vgiq8D7YFZ3C1hbah9qJr4HaYKhWoStQGxIbFKgMwU2gjGF8FOKlcNHLTgx2f9S8Ujgd6j4bgn3oCGpxQXW0GnXAQWhTheRABzZ4ZXgErJRcsAKV0Wo4Cp2BGrQHlQQF'
        b'xEClhmWc8QRWFqITdurIWuEAuqyJnQ87EgITnBipmHOG9ig6+2eioZYc2RjcMFkow4a0SsQMmCSC/c/BNbu3oARbUaUmKRjrx3JULGWnDYBOpfPjpxRPeyglT69/eLLh'
        b'KZxs2G06C68TDvDpAccKEhFNl7HOrJT1Yt04Z9aNlXP4m4iUebIylpx5ObMy+uPJSu+LyQ/ngX/r+eDvnFz4zsmcpCx3X8q54d8Gch6YnlgqpqdmA/FTij8+mD75Lmdt'
        b'bszDMzS33lPrdaTy9NUpWZt7z/ooqRlMz+HKNa+nH64oicD2ar1VwtFKqBL7QBUGFmyKDxHko5Iys1GTE9rp46lkhUilGgNkhybWH50KwmEMDtfQ/nA48kTc6t4TViYz'
        b'NG4lR/nMk4f5RvcHcSz3L8WxInp/I/42Dw8gU/T6l0ykyit0j97B0IudlfkGRUJa5LgwhdVGv4wNeaTrI7/E2hU2g91hsxBaZhNvJyQydZZchS4ry+qw2BW8XWc35Bks'
        b'dl5RkGPKylHobAbcJ99m4HGhQf8IOR2vcPAOnVmhN1GB6mwmAx+imGbmrQqd2axIjU6epjCaDGY9T+kYVmDpZ2EqpI35EVL0aFVolWW1LDfYcCty9eSwmLKsegOel81k'
        b'yeZ/YW3THs5ipSIHT43ceRmtZrO1APckBBxZeOmGiU8nEYx5qDfYtDaD0WAzWLIME7vHVQRMcxjx3LN5vrtulfKxnk/2wfLIyEi0WgwZGYqA6YZVjuyndiYiIMt8ON50'
        b'XGI2mOyrdDnmx1t3y+phY43VYrdaHHl5BtvjbXFppsHWex08mUjfjTN1Zh1egdaab7BMpOzEHSxGHWY8rzPrrY+2755MnjCXmYYsUx6GAl4pYVRfTbMcNsKhlQ9nMx+O'
        b'5dgclj5bkzP5ifSJaTqycnAzHv/myHvarLPMVt7QM+1oi/7/wJQzrdZcg757zo/gZR7WB7vBQtegyDZkYmr2/91rsVjt/8JSlltt2di+2HL/l66Gd+Rps2wGvcnO97WW'
        b'VKI3itkOO5+VYzMZ8bIUoYLVVVgt5pX/o2vqNgImC9VSYigU3UszWPpaFr3F+IVVTTeYdbyddv+/sajeocTEB+6sty96YO/yrbz9cQLdyDDwWTZTPunyNMtNZG0wZT5l'
        b'xsRz2XU94JqPPRceymx+CsK6B30Ix0fHejo0/8t8txmwF8VKN1GBrQxumQKXs3IzhQH6ak9sEV68NtfQS1Q9E8IsMMNlnjeYf6mrHTv4pzCxmw5p0fdkn/C4GodFb7D0'
        b'7TG7h8U+sg9f/ejAuM0v0che/qjfnU2kDceMdh5bKiMOYkh1Xx3zbVgA2Obp+h43ubvaYAlOtIU8bfaPjP3EvPv2/91AeCwGeKTzU+MBoa8JD913x9jp0xKfDjut1WbK'
        b'NlkIpJ60IUnddZkUkFiBFbNshjx9wVN1vTflfwHQQvP/ojHJ0WFv06fJm23IhMtYrfuwCf8DEyNqQPWM2LlH5pWGa35Z2Sy6PMNDa9cdFysCEnFxnzh12PJpXPREj3kG'
        b'W4HBoidquarAkJXbV2/ekK+b2DuwxgR6RfV99FhksSyZqJhrybVYCywPo259732ATq/HBQUmew4J0k02EqUabKYshUn/SxH+RLy51eURs4nnlJbzWEbaox0ndu9zJuJ9'
        b'QV+e4dHWj1wckJ3dQObxi4MYIcUnLZOjSRHrs21u5/w54cz9SIGQC5U8w2L2zR7J0LMoses41AZn0TW8853ETEJHoZQ2bp/ZnXc1wm5+ZrpMOKBH5avRDjXsjHxwQl4W'
        b'7BhBvhcFDlMJe9de+9bh0IA2+Et80Tm4qnSjJ/lDlS5QERoXG4zKQ+MSNMFxUKlJRAegTMKEQ6VUhU6jSiFxrSQCdXqiJtWDVhLGEx0SoWbeQRug1uHoqAZ2of2PnJnn'
        b'iybIQmmDFNhj1MT3nIijreiScCqOalEtPTYfMlIGFSqoTIgL5hhnOJ4CnRwqhyJ0wEGyYGJQvTM5j4+FLXiKlVAVGgOVIsYfFUOrpxhq0E4dTceDTrQPFWnc0cWHjcl9'
        b'TRm5JxmpkkzGHUodo8mU16OL/bpJjlkmtKOXGokJLKNElyVonzvaSBm6Jl+kQe1wvvf45NYCNxyZIYkagrlELogMsD1EFQKVmFJIXCKcToCyIKWUGQL7xejoggkOcubj'
        b'qYQdquFQKzSLTYBy0mSQtzgMNXMOBW6xYKa4D+GlwzksO6hFx6nsg2AnnFKj8lFjyfXDHka/CC5T+gPy0P5IOPikoOAI7BUOVrfDNTivRsdR6VgJvWfI8YMq4fD5AhyH'
        b'EtiBkXLKiWHCmDA4OI+KbzS6YtaganT4cfGOgRbhTqcRy3TvQwnDQXRUkDAer7775mMFFCepUWu+lGHdIuMZdAYVu9KKJdFz1ZFoD2qlp9lMLkbFFccQokton3dvWNRh'
        b'9SC4GAHNSqmQw1YmQhfU6nwRw6KWZA2DTg+ZJJwtb4BdcFmthmYJwyagXSkMameX0j6zps5Uq224B2yAfUkMOotOZFMGrEDbUDXu0oq7wPGJ8xjUofCimjk3EXWoBw9V'
        b'k1uWOiYXLqHDwunxdi1qUg9zVRNWHmXMcGo61djP1w1kgrDGJs9evfivS6YJ6o32ok1Qw6PTgzGZaCY6Flpp486C/iQZdsKRZy1uRS4DGKWIqkSM5/PkdqVSuERyRq2o'
        b'CWo4tEuVK1w0nZiBLmkGwOWQ4EAianRGzPSbJzKH6+haMhajQxqSB4bOyBixmEWHUePybkEMMhgFlkFHCmEZXIJOyrTcNLS5m2XQgS4RnsGlcKqBA6F1SZ8aeAyuEg1k'
        b'0GFMnYycHYCKBf6iWj/K3ivd3JodxnRzd1YGYe4qVEQVDDbNRMc0ayKforPuWMEI4eB8WK/G5Pb0iAF1oPNUmZPF6ET35GA9HOxTm3NZmtsIzckD1Wi/oUdiiw10Coty'
        b'0EbNTNVTVBxOonoBbodg5ww1KkalauHyMWekcJ2/cY6c5nG+5ql3y5YOY5ReVJtXDrBoYoMTQ7CeB6BjAT2nvENQiRjVw17PnoukMzJyk6YMjhUzLqhF7cRhddrcnzLN'
        b'uHQdlePsDEGMShAsZiGchObeAFmUTuHRb6pwK3QQjuhU/VB1XLAmODCR5Bv3yxYZTH50uZlwbV7vS1xnOyLMIpeEQ+LFqHrkeEEw7XDWv3e7hze946baJfIEM50KNw0a'
        b'Jg150uhIBlIqz6OqXOEyFW11mRfaq1lglgSdkqAyAdAHxJM1D27DsTkopzfiJ1ArZeUU2IJ2yeC8cHX86MUxbMRIIjSG9kOlGuOcx80UHOtH7Qmq0KGrD63UMDgsGKlc'
        b'2C/Ub0Otid2Xn9hTnKMXoGg/ugwHHIGEH1vHkcvvbp6jMqwFUB5Pbg5I4fYklhmL9khjXVEnlcEyVBKI1xMTFJcULE1G2xhXDQeH0KEcOhhU56CjqtgH17N8OL2ghWZ0'
        b'SIBFC2rDUhGufWPQNXLzi+rQxUK60oVQhU6rArpzAFBLHk0DQBfQFsqtGGhFB1HFULjYR7qCPzoi3M0dgSuwjaILTvsI8IL1CQ4hafZ0b0yW+lBMlmHDTEDJQTXa6gqX'
        b'huNIJZVJRa2wkfaaDId9Ve7Q+CjoULsE2wZPAZUHoJ2fEyFYQNRsocWBmeis63gtSXqFRhzMTJhM0z9h+7gRsIPrjxsHM8HQGi9EI6dRB7T2Rn5oFkU+OiYkIDVIhOTz'
        b'/NSVbmj2aIYGO9DsFdAbyZmYf49AHm2cKdxx7ovAc9wBx56DPdgLoipGO91XIFGPqmJ6gIz2SZ9AMmwKExzpWTibjdry4WyYiBhqxgrtaxxzSYzgFMxjfEFl7Jxk1BqW'
        b'mgKlNGE9JDgAyzGw+1Y9lRiK0qB5MUR0BCHPoisBc2KCSCW2IJq5yVApZtC11f1RJY666C368UwhoNzWPzd+hjGNEXJWTobIUMVsqO8DBGjvOiwUem/aMXIwahtH/LJ1'
        b'xBzsDxLyBWNXrwsm5SzDjvRNIf56X7qDZFa4w5Uk2IFKY7Fz3w07Uely/KhE5eh0BDojwYbtEmrNTLFnonPjWSwn6cJBqp60jl3oVDdJdA3tIESXjcb+jlqszYvhiKYn'
        b'aUKqRZ2ohgtEh4MF1Wzm8zWoXPGYt8MuvE7QpoPr+vXGhJ+VYgLPUEhBxOPun9O9yoQcskonVOcgrzrI58KVB3EbNvxFjwRuvrCb0p+Wi8pUg+RPBm4e/kohnwqdlynU'
        b'EcuIW92JmuLw0mbJhYqrqB3VqCfZxklptGaAQ2sE/TuKtfSsetxyzA5szc9HkTjqkAuty5mHPXDbOGhmMKuqF80jV4nFsF/JCtHNRtgYjqvDyesF02aRfJStsMtB7rnQ'
        b'/jFQ7QqVUIGLKkKhKhWa3VHLuPDkmB7kpQTPSxHQtG9yL0BhWB+WwT7XIVQnYzkHRnQRHMCTLmQKM1C1cJl+Blo5dCoCtZD82g1o40CMslFog6CwZWNHoFNe8di3rmXW'
        b'rkWb6esMUA+NS3mamZ8SEBMUSPVvPpRyUNNr9PnBTmgXl+KYSIWJquNdExOgMnhet4ZA2fyYuLkxacJiUGMy2jgeShOCQxLjkyQMaoBmGSqOyeyB9EnY5oMhWgklwksM'
        b'XkaKgnleRlx6GC6i07gc9mJY8CtxH+p/MPiaNFFrH0PYErhAAWCAE3C4N8Jy1YLVubiECkwMxdghtBVAhzs7WIct5Hl2HOzxoX4jAe03Pc1tDIOGbrcBx9F+IUbHkTFq'
        b'5KEjv590HiFVxo7OlghqsDcZ1T7wKTjIvdDtVMr8aJiGOuLQgZ6QA46LHgs5UA3aQ7PBTNuVVSxvxF9vfOHrSJtSNTTa4/S9moMH/9x56c/ffnB33yfNlXcO3rjOSosW'
        b'Noc7Td/kwVQnpKEbdf3fqkjEPF7Bum8dPUvV/kx/xcz1QwcseGHmzH+K166fwS1968uDSejNnOPaa387c/LMqvH1C5MT3tu/36tUGXB539yw+rfrAzvvLGw2fJjXaOxa'
        b'EnTuvNq76bzr3AGzYFXRxjvLf3r3XecmY+qpmxeurXcf0nHuqmW6Z/rwb4MTR3f9/MWuS0uMS5flxqjrX/4DWjV39s6xP9/vjD3w27vMqReVt3LgpSWHPyyMGJ0feUF+'
        b'YfU7396e2rmuUPa7P6cveevWjiqX93aFe+dFitJuf2g9sPDPDXGdW79obM5F99iOMV9efsHyN/WaUyXhgeNH+sV/Ey/y/2it/hWvBXdbSrPL3/psluWH0gP3Zzb5lbz1'
        b'yvsRm3h0kCmQv5Nfd2PNmHdi80X5VRvVf0v6YJbn6/Jbv9r0m847J1bwt++weyfua/vhq4/ufuthbY08Fp0CdYu06S2v7M+LOP/2+uj3Pk3N+nDty+V+X5mann3V+LJH'
        b'6uahB/bm5CcpGhYOLXn9w0lm1c8/XqorqvnNqwV10VMvJbHedw6K3kv9bFLJpYkJFlGmS+SnP35wxn//4OfKVud+X/G7T+KX3r6yqKX1lbnuS243e6akPf9iQXb4GT6r'
        b'0dv66z93XQ6+e/qlP9S9+Fmti8jvosspn8OeeVHFr2knfXH2QkXhc8E/vvut795nowbFfej67tDZmy2NxueeK/p+YeSem52enx2asavyH41fhqS8y56FdNPPXXWVC7xb'
        b'h2w/7f1hZc6peRPuFr7hda35jd9WfPijU+P9F2e8eFXcXvnHPS/es77o/EP1++9V+GWufvH85R/TQj/KlVROTdt18NA2S+Hci3e0728Jfev5iZ7fpEPmmLlvnkY3f3h/'
        b'8/Wzvwpfrr7W4v/W2SkXFvW75/26dnHx76q2pl88rMpJrtg64Fee3hcH/BCYPybzzQGXDhR8VLj97sotF29/9JpqUtPN3X+f9u3yzdd+X/mn2vt/jH3v7po3Br93Yttw'
        b'k6xo29qYFxdqtE1p372yuvzD1E+/P1q+bE188buRdV63v62Pe/+Dm4uP+oquBt6xHJXmrU2daL/+1vWFBbMvnH+tdvnfE5dJVww6n3T873f/1L/q6HfLB8z8+K+jxo4b'
        b'rY+pOOP5/fg3fT+5VQNXXn99S+wnnt/fnXFv6zes4b1/OqnXmoxRK5RyO3HIqHMs1KnG6ENoLgnWTWL/grEjQR3imMxZdmJhB2O3pwoMUWIFZhgXZyheyKH6GGiiLzuF'
        b'QMWzKrQj68l0lkqtnRqIXbARWlUhD5NVsL0p54LVqIlmpExardY8SFWZHEmSVfAG8DwlnjJ7MVQE9aTSYLfV0ZNOc0BJp+88BfZiwjtIhsTjSSueaCcdIHnJFFViQlAc'
        b'bMXtocOCOrmCabCR1gXAMbRJg41fKPYL0gJ0nOdCUBtHM2me9wnU+OGQrFLzYF39wkTZqGW2naZN2sb0ig0yI7hAbhylKcFh2VFVN7ukeI98NYlTu7hTVqLWZPODF34G'
        b'OOgrP3AwMpPm36CLAUHQJsURzBYNjrHye14dmywWjR2hHPCvZtn8mw+l+3+fzhOvJ+XZI8eF0eydKJKAso5Z4MyKuz8ymqlDPmKWY91YT5KBg/+XcRzb5+cbmdyZZvg4'
        b'sz40a4e09cH/y3+WSmRs749ARS70exo94fMX6SA5q2BJHpCY9WB9RB6snOYWidmh+OmFqXhwHvdlrJQVMonENGsIj8u5cWQ2nsLonIyOiX84knck5UhKzwhcIiWzEeaE'
        b'+0o5IU9Jhqn7sF643hePQHqQPCb5PalYWIGc68lq8uDkHKXB2fphHib2pCGJySFyr/Sj/778lKzNo0eCdKxqIjlynMasZ74a+ctvgU2KDlLhHd5eIVcJqoJJiMcwvvki'
        b'6EyClideyyN4iCL0SWxnIC+KM+mcnk0X6TkhFb7Lg56N07whW7TNZrX95C+cllNs2brTgAx6hc6iMJD6kESluMtZqyXXC1ptl0yrFd4Ix9/dtNplDp25u8ZJq9Vbs7Ra'
        b'AbAPH3ThJG6swrOjWWfOnLDTaliISlzl2Cy5ujjBFbLGYFu3fobCYakENWiV7CzTN02RYp6cptm+nj+lqjMRkj2i37tbfevtgjFNuveGf7lo2+c/MLIjmmUfj06R5RfP'
        b'LAq+kj3ynsL/FT4qZ19nwdZPf1u48u/PLPnjjwtG/Oq7P/FvZn276fXv4gvWjk/89LbcMvmjEXd+90n6xkLFV39T/y4/6x8Or9h/Llh7c0z47bjtu+QjKqYHqb+PjpcV'
        b'XXM3Lf3x5MkvahO2p3xYH1EQ2PDP1+qmj7+TWuLr8B1nev34jKg9fvyrbddHaIL+kF08980F2UUJHbeMJUu+u/XZ+hlbfeL/0fhxzYDEyI8Kvzi2u/rm2E7DXNclIRfG'
        b'dZ6xfL7R8pe62Ks/7Y6rWTlnl1tq+Pdv6/fenHPm+ZO7ZWjsW++MXPrdKyWvVTrdCIaZYVu+vLXVEOhRhZLWMjMGzYvjypViOxG4bXwhDv5ZJhL2sRMY2Pq8haZHKqHU'
        b'TN+dRRdSEh55dxYHu512epuwD53zdg3EdpdY++5GC1Uc44/axHB2CVTYh9OIHY48w6PTMYnBD0LO/nAV7x+2kdPn1iEY7BTznv9Bkyqloe3TH9RUYsCarTq9Vkvt5FSi'
        b'GwOJzRrH+t3nOJKJiC0j5+Hs4dTbwol/lLp1W7B/SJ29kogFDVjHFHKsbVAPnrEOcRjkD01E///MMlmbzwPtIYOTLYOQ3fhlyNONBnF5osmjUQU59oCyJHTeJx6VoSon'
        b'Rj5YNGw5XDWNubkVbwlws5QX0LCXwuUbozw2v/7FpXXGAnd7Zv3m92svoxcWNB2st4/2X+16ofGF+Veak//YVDVv9T+MvxmkTf1h7bPF0Sd/nLvv3vwp7ZvCxhZvPfSM'
        b'aMwB9aAzI2eNtlQNt+20vmVuufTTZ/1efM3nwmFfpRMNWLKWaug7rEl0P+TEQLmbK2rl4MSkYCGFt2MljhmSgqGFNEoK9kZbOQytyyJUC80Rgiff7IIOCQvDYJ6em4Aq'
        b'6bo8RX4ZeXbCHimcRBWa2ISVUNKThmtCNTTogbNTUJGm159lgKJwVyUH2+CAP31p+BnY7dn7zzakZNG/2jB7AtUs1Ui7Kk7CsBoGqlV4Q9ua2oN0v/9wBPHvwkf8i7ph'
        b'spjs3bpBwi7G3bkn01cUtI4hH8Y2+AHiFV0is8HSJSY5pV0SuyPfbOgSk8tT7C5NWfhJ8gK7RLzd1iXJXGk38F1iklrSJTJZ7F0S+jZ1l8Sms2Tj3iZLvsPeJcrKsXWJ'
        b'rDZ9l9RoMtsN+Jc8XX6XaJUpv0ui47NMpi5RjmEFboLJy0y8ycLbSTJZlzTfkWk2ZXU56bKyDPl2vsuNDjhWuLzuchciJBNvnRARFt7lyueYjHYt9WNd7g5LVo7OhH2b'
        b'1rAiq8tFq+Wxr8vHnkvqsDh4g/6hTgvL9rORN4Zs4eQRRB7EUtqIHbSR21jbGPIg4LWRnGIbcWk2+ocdyGWFjezTbaHkQeJeG0GwjZwS2Mh77Tbi3G0B5EGO2mzk/Ssb'
        b'udq0kfeobAryILC1Ed2xjSePZ8lD9cAkEOm4PDAJP856qkmgLX9y7vn7Bl0eWm33924L+ZOv8dG//KKwWO0KUmfQJyqdbUSziHPXmc3Y7lFUkMOXLhkWic3Ok9v6LqnZ'
        b'mqUzY2mkOCx2U56BRha2yB5WPhYNdDlPFmKIqSReobGKmCirgDwPLzxrZ/b/ASrdZUc='
    ))))


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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAdclFfW9zOVgaH3IjgIAkOXbhcRFakqo7EBAwwyipQpqDF2VIoUQQWsYAWiCGJBRU3uzW7aJi+EbEA2mzW7726SrWhM3M2279x7ZxDU7L75vv2+30fiOOe5z3Pu'
        b'ueX8z/+c++CvuHE/AsPfX2+BjyPcck7DhXAa3nKeK6fhrxUsM+Ve+FnOj+Sxb36GK0opXBWsFU3hIg1XZsKfXHg2jr9WPIVbLjQ+oeKtNZnCrR3TIOPWi0zL5OLv8swS'
        b'5semyDYV5eoLVLKiPJkuXyVL26rLLyqULVQX6lQ5+bJiZc5G5XpVsJlZer5aa7w3V5WnLlRpZXn6whyduqhQK9MVyXLyVTkbZcrCXFmORqXUqWREuzbYLGfSuIG4wx8p'
        b'GfuH8JHBZfAy+BmCDGGGKEOcYZIhyTDNMMuQZphnWGRYZlhlWGfYZNhm2GXYZzhkOGY4ZThnuGS4ZrhlTDrCKdwUTgpbhURhorBQCBVWCjOFncJcYapwUHAKgcJa4ayw'
        b'V4gUlgpHhVThohAr+AqewlUxSWET4U5meoOk0D3d7dnsFXp4cAr3Z7LC49l3GRfrHuvhzXm+5GoeN1swmcvjmebJ+Sk549fMAv7YkaEK6TKv5+SmKQUS+F4QI+DItdCF'
        b'r3MBIZs5vTcIqC3IFlfhitSkpbgcV6fKcXUC7stUpAWJOd94Ib6PmxfRp4/5iDlzjrMO9flCK1q1gdNnwsVsdAjdxz2mFksXg5KDCYrF6LIfLg9ckowPLZfgisUKUFqD'
        b'awOgA1yzOBnXrPBbnIRrUpJSFX7QUB4C3e1AF5YuXqLwC1qcEMhDHUJOhyocovBNvFcfAX1kouNiUD5RC6itClm6ODARH4Ru0VF5Eq5MEHGlqNZ0LeqcnMMbNyGWxgl5'
        b'FT7mWGTApNC1EsI6iWEdJbB6ZrBa5rCilgqrCEvDOvHShePWiQ/rxBu3TvwJK8KL5dN1euHq2Dqtf36dpC+sUztbJ62XScZenjNoyEqavzaXoxe/2smfj/nkW1aBaFop'
        b'u/h2vCS0HzrisrKS9LJwdjEySRQ2ILDmuHlZBX9Z7cS1cwVmcFm3xEX4xLbX3YL73Pcx/8a0ubMTuALi8mHiJp5seZ4V3B/2aVjTmlnssnv2YytdUtBkftpD3j+cv5m9'
        b'hBvh9MHQgO+ZotuwIDD/fn64MmRxEK5E7el+sOa1gcEJQUuSeRzuxacKrUxnm2fLQ/QOZJvtwmeytOawLPg2bsdNHDqqyteT4eMadKdQqxFx3IJsXMWhcq0fe+KU7xat'
        b'xgRuuIsv4moOVeLORbRlG96n0OIb5J46dAnXcejgvOVUl8hknhbVwHyKs3Arh07m4pt6R9JHp5o08DnOB1XjM6AbncLVeidoCkBVqE9bAt2jbrwH10I/6CS6QdVNjg7X'
        b'4m4xx8XOw0dIZwdW6O2JuvOo0UGrh2fEm/AhDlVFoCbasM5yjdYC7ke9Gfg0h5pxK75Ce0G78V6xFveAabgFn8WNoA2XxbC2A/gq2qdFB8n3vmB8gkPHcHcY66kW34jS'
        b'SsFwVxluAY0+6CA1Dd1Ft6doNwOkZ+/ERzlUs3MVm7WWEjetFXxJxM3kgSaY7Fu05VX3hbjHAgxAHWDWZQ6dRke8qa5lS9FdKVkAdDwbvw7P7JxEn4iTo2OoCtaMB3NU'
        b'L+FQZzC+S81KU0Zp8VVYzA2wNPUcqsU3felEo9sbX8E9ejALn11NJvowOCqbAtyLmk2kuAv6wVfX4SuwCPgY3kct2Ibu5mo3wyi3FRJ1ldH4dTb8cnxwlhbfBKszYUAc'
        b'OjRTzBrqvfE9rRU8YepGujnmg47Shni8NxX3SMiEyfE5GFEY6qUNO6Ni4Tp0HrUQXyQboBxVsxk7jqun4B6diKBZI+mkNjufPoKabdbiHnNYT1w5jzx00n4WNZeH7uVB'
        b'A4w/JAK3gTK/KXpwV84M/OIK7sHddJZhXc/CNkfNXrQfP6cFAJQ86gp9uJNDrTtg1zAL5kZCE5mYSlsyMWdU6Dy1QMPbAg0wmzmWuItDZ/EldIFN5kV8wBsmmtjWYUv2'
        b'2iF8FN9j+6kKVcCK9FhAX9lB5LkzqB5dZm3dCGAVTOyBxqJk3AGdoxORdO2i0D09aQGX84b9CjvklB7vZt01oqZCWDseGeMtYvxJfBEmlvrWLrQHNUslxLUrXwG3ROdx'
        b'cwxtWoW78XkpvgoaFfg8vg6WeKE2NuZqfP0VaSkZ8y1/0lfzDnyQ6evBd9F9Kb5BJrEpCHdDZ8GvsIcurHaEBhj0JnQP98AWdsHtbFw3YGpOQhvZxQecSVetMbiL7ZXj'
        b'/DitjphXthmXc2i/Ez5M1c1F+9FNqZb000PnvckS17GVf93FTmoG/Qh34lvQLQx3F11huxwpqorCdeg6Oiji7HcK8Bleqj3q1LtCownaq0FVpfgwqkaVIq4QdwjzeWi3'
        b'GNXoPaF5PeqNMDSHGTWYomo+7sJtTuguPikX6G0JHqMua1wFi15EgKa7aIs9G/zrsKzHE8HabA6dQ/eyUR8uY1hQKcaXE8HaXDJ51bmoQUGvz5+N99CBz0mn40ZtFnof'
        b'MiE3l+AG+K8cvR6F2kXKZFiMcxvi0NnVyVwEvrtJK0JHrFmnuG42X0tcAyCpHFfA3KKySXp/aJGgSi+jjk58BB+mXyPQ6/iIkJuEq4W4Bx0wRV34KrP+ihi1afE1sgzX'
        b'0ghm16wQ6gmpXL4RNzJF6AZqI5oWo84xReiuEFS3C3yz6MLMQbulNIpEhdIYgs7gCr0vMfQyz6gmCl0eZ88lZk+9UFAkztjJQAoGgU8D4AJK4Ou++BSHTsw1ocaAP9fh'
        b'hsXoEkzMmJIwYhYoCRJMgknoBdTaQ42Jht5vazWwIqVW+ACHyixRB9WCyvx2js2NSLkUt8AUo74NUhmuQm0r7LglMkDCk2upFhXqW0HDnwCdo/FvGdqtD6GOsBbge/wU'
        b'Z+F9TLqCq8lfHcSsII2oBHfgY3SadTboKg2a6Ao6SoMmumJPo/aaVfjc2MiqBdnMInQ2fh2M59wGVAWLvxj3ivF1dMEQMXCZZTrAPBnQQdSCawBZNK/pvYjci7uzxs8T'
        b'WTIhqpAt49xwjwB3pbHto8XXcavWDOY5BzwUFuwI6vHSx0BL4JL14xa9+vlVa0smqi8li7OTwbe1JeiKBHCnBvWxBWxBt1CDFlXC1K8GAwD+Tnhm6IOgqQCfgZ3TQOwx'
        b'rqAA1eMKfATt99yeB153jJuGT4tQTQS6T10aDLiO7jA+ASByhvIJ3BxCV3KzDzo9YVexvdnB9maDIAPvxn2RqIyaFYr2eGktyaY6BXN9jGzPXgBQogffXh34Mm9pZ7vz'
        b'gNDE1AQmuY6B2f5SOaMxuAldp0QGl8GeY5sCn5v7TFP1c4ZRp4kwnb1NhJohvlbRHSbFBwsY+0ENHGU/gSuoMkvN4jEYGDMKdFSzNSC6wtbgalwrghm/qGXQeCDTjNIl'
        b'3O1I2ZI7qqKAgC5tgdWe4MjGxWSDvCwMRQck6H4A3RrpGaiekSt0XM/YVbuEWoXqsqUTzPLAZwxaL7EBU58OAozVhsD8Equyp64FZYQsXowgIfywC2AjBf/uHHyXUjVt'
        b'OKVqeH8E9QdvCISdxm46qLWd+BrE0a1kq6D9MnQGHDUZ3zUJQ82+FJinKvMou5sJSEPYnZVaH0js7UHnoyfCKXgW3rvaL4oNXWsBMfK0BB9ckEeHvkEVw6hgDt7FmOB9'
        b'iPfTiKprEGt6jLpep1b1Rk3wecPYj4q0+DSqNIB0EdnAJHAvLcUnYd/h9pl0RxbNwbcoewQDail/RHshWJHlsvMieGDY2WMxIE6GGyhCpeL7OnzKJJgDYCHzaAod76cU'
        b'TSalFA2dFrIN2bc94BmuwCpVonKj6WNbQcgFozuiDRshitJg0JmOD2o3k010FBIJWPzqXHeGnB2oDMCZ6et4Iaz4CoRr8R10V0BHt24bCSk3GafuovQQtaXop0LTLNn2'
        b'5+EpgviJEPDphsBrLe5eDRSTKMn0wpWghEe99hoh34eTAGZI/AyL9KYU0/0VSjFxHyAGHfJuWNDnfLD9eR/EZVtKRKhpBWIbFJ9bsERrBb3YlRJaegIGeYEhw028L3s8'
        b'YJFvxogjEKC7qfgK6kXXqZb1qEfC2C3avYPSW3meXg4NW3DXZKNFV150vbNCIAtnTVA7mzjcvRIml7JhGRBWQodxd4SeJK6voMOClw2NXhGiq+bJsQvQZR9OA15yHDL8'
        b'OpjVNgbKe2CL3WVEeifMDyHSXrMYxAJwFwBykegfBduuhWzRcnSVLhVQ0jazcdGSuU+cTMRFoBbRzjUAwO1Kiou5YMo+4N1kwS8X4fOEu16D7UzX5JrfzPHbcCLMUrwO'
        b'R/WZ+LgIosHuHXQ2rZwjDPT+JOxDwu+FWfpQEiuBInc9g6DqZxBRji8ngSSAibDYEMlbKjKJweVpdPyTPNewnIAwO5oVoEaARhKU1EtweSINaKBknMfBuraNMa9lqNrE'
        b'E59hXDzZJAjmixBnVAsb6jzZfi0cXWpc4Tz9uUBOdbSsoDE8HF2H4AaT3MxcbTe6HYp7LEGTGroHknv21TjKAjesfiGCh7GJcsPdguhA2Bj78H66fvi+cgXQORJBcDfQ'
        b'+6uEEh+AwXnTiLQVn54Q2ygZKClcBhFyjwDfSUYMihe9thL3lNAotIn4WS1qiqLcbWMOAPx4wB/vAuiAAJ2ahW/HTmZ+dNIT0qCeEli1VRYE6+rm6oyUpE72/ID4YWrC'
        b'SG4KwOzKdXQsCegqUBFDjrYnn6VoV3ADna3tuHUzS9Lm8GmKRrgJ3XsAetNYjgYgU06TNMBUlqVC8kZUkjwtcAHN0/yTGJr1Tn3lRRjqZHPcJfAC3wfvQzdp3/NV+J4h'
        b'o7uGz9KUbssMuhmmwoiboQnMyoU28J563KWjzhPyitCAHR3GDsAlxsDjgg++pi9gE9cVCtkdCYT58YRSNKBrLjTmAODvl72Mm3SOI5nTsiE6HhMBTpRLDPWcUMiz8XUw'
        b'NyiK+E5zJqSYxHlwB4D45Rc2RISR5jF9uClrpQjV5eJGqi50C8xQjwXZYLuVZOZb0E13ut2Tc/HViXGKoMNYnEqT4r1JJtODUTmF7IUp4KI0810UTDNfnQkb5C5b3DYR'
        b'Hy4/P2HhqAIfRPdFqHaWYWGdVgL56bEgi36rlCSiZwvnUnV2c1DDBG38HINh1mBXb5QNKo/koePzUHuqWQo+gPsYDFavQ1cNubcXLCRJvnEXZN1kr2TZAJV8PvMwArhc'
        b'IMF3YLc0oS6qKRoGs9eQq6Mb8TRXJ/mWPgAaZ65OnuBNa3PH8zoDgdCLijPwFQMBhlH2QnZPuFiHF1F2gkR7hjbN6EL6i3v4dbaHbwkgoYEUDx9PpxOmQK34CqsTrImj'
        b'ZYIFMVRN5DxoeRk3NKSL94XoeoJlHGa1GnQb3ZRJJWCP9zSSyp8TwTYh2z3FpeRFzLrEbOkUeO7EnTn4Ht1Q1hCBKllR4n4uLUp449uU+IQCMN9+ga6N21G4WR1oEj0X'
        b'9bCSIqpNk+pIyLmdSHC4QR7ESiJl1ptYaYNgC61twPzeoPavWQvzScoHbvg8qx+c8zcEXsjU2qWloO4VEW4n+dA5dIiC4AJ0N3oCHZ3gy4CCJlvw/URfVjItgxRGWgod'
        b'iCxJwa6xmEddz0UnePmuRD2rYY3LNuCzqznNxkIXSKaACVezyb6E9vFpJUaJGmklJm4tq/PeBIg+9NIcX6RD920NudQlkhy0FTMmuk+B6g2lm70baOlGMJ2ahm75ek5I'
        b'pJT4+MT0jyWzqEGkw/fAmylm9UgdWL1Hu4aWe/D5+YYy4ya0j1V7dgIZJ9UefC+RxaoKQKoDUkuy8m14P+7jUBvw+UPUb2eao7svT8PGQROwlXbcKoLeyhU0fKNbARBd'
        b'xtZmIrvwzyJQKSqJ5KVJTKKiltA9VhgEsfP5tBFdEmXDrFfBYiRzYU4iyPf6FlDvCMc16yaQfsPas9oFuirENcuAe+FzLKrcQlc8XjaKy8yXKoX4oL0kfw31mMV+q1+C'
        b'KszrZgoUpfhuIcwNxe2zKwBhXkgHn8ftDkADETqRaCuXsGR1L2oBn7cUEKoixvdIefkqrmcFZHQG7ZLibgIHgcQJW1GfJ1vAU9DXUWiCxwLA7QFa16KLtMkJ/KlGakp4'
        b'woUSsnwXcaWBkKPWtaukethcgPqwURs90GF63X4auk7reEBISRkP7U+m111AVbtUCz66NohsklML7RjiXcQHFbAUBPEcIbjeBYjBF1C9PoqUUKDhJPxpgDDfgFsN5Tx0'
        b'2eCWkN2Q4p0Q9aSjKgW3cp0Yn4ZkTy6kJcAMXIZu4aqkJfiggBNAIOzD9yAQBEP2Tv2jPQfXJuLKJDHHJ7ee44VsXUIfjLXVJuKaEB64YHWAnByCmVsLHNBpdI2hzW7U'
        b'qQ1ICVos5ITodeU8Hqjei2pzyNGR8Ycc2tDzpFL4mCM2HnIe4RQ8esjFV3D0oEugkEaYGo64hOnicUdcIg9OMe7ISyGacJgljBXRI64Xro4/4lLOgoUziyNHslqZspCe'
        b'xcryijSyUmWBOlet2xpsZpbATnz9NxYV6oro6a2/8bxXpoanSpXqAmV2gSqQPrhIpdlkUKQlz5llKws3ynKKclX0zJdoojq0+k3Gs2RlTk6RvlAnK9RvylZpZEqN4RZV'
        b'rkypNdusKigAK2YUKzXKTTI1qJshS89nx8bkPDl77O5g403Z6pwZMjB7vbpUVRjI7iSdz0+Im6BdXUgtlMFPDgxOtUVHTFIpc/JlRdCgGVNI7dNsHa9UZzQBpuBf69OR'
        b'E3GDhmBZsl6rIzaTOVqeGhQ+LSpKFpuUtjhWFmZ4MFc11q9WVayknfqTb/4yFSyLXqlT0YP0rKx0jV6VlTXBFqbDYA+bHbqUBttky9WF6wtUsni9pkiWpty6SVWo08pi'
        b'NSol9KlR6fSaQu2MMc2yosKxjRAIVxcqC7T0MpmczWotGDrhiFTEPX9EapOykEWtFrx7C6tD1XL4qg2qDJ1KTz8/dnTmAM62aJRZk751D+EoEKwhoF7FzcPVkDZwq1AP'
        b'PsVulko50Gbd5pBVcDV/Gzs/9ZtqxZFXB/4xKyvp3YRZHPVcE6Bqd1gppYVLxntQcxFqk1sxW3qz8FljW4ItasYHlxvqHOj0RnpIh49yG4Hp16BqN/qI1zZ0kx7TETZf'
        b'ux01zTScVO4AgnCYndMBxOHGGej0dnyRDkKYnE9P6UjE71uJmvD1afR6QIaVtJj00caZQR+N6fgs7V2CjsqkJaQBiHAfvg8jOBXE0Hd3ET7ATvYkHK6HDLxzJWo2nL4k'
        b'4VbcoyVpSCs5fjyJ6l9bzpqOo0tz2bEfqQDtzgV6cMSGduWvNzec+p0BjHNCh3Effp1NQQW+Md1w6neF22gHwN/GTici8u2kdGpucJsygZNVAsejxl2YDwkVHehxkum0'
        b'ozp0hWMW1G8H0zYTztXIQXQ6gGpDcB2jafMSaXUKLFvtCLpuona5gFqwE/WhamObAJakEp0tYep2A/afGuvLfQv0dHY9A2rIInCNsStYK1SryaYr5+2Dyw0HuY2cVAqP'
        b'3JDL+VTfbF98ZKwJn+BDWxXupvpyUN0qdsJLMt+9uBMdy3Shuy1pFX2tIvRPgVnmLSHbOVppTPYJDw8VsnrtbefsYrRbveiDwyLtFJj7ox+v276sexkONT9i937Kav5Q'
        b'xeV9HgJpzlGNLu9XwcvmyjbfDbv+9o+tRnmBfwtZ4XbnXkxF4zsfHR/eFpJaf/PXk7u27n//QcCu1B9dWFp34vZfPSzWe/xiB684quLDYfGTT1qTGy7mv/fbFK+sdV3C'
        b'GxYX8qM8/vCPTSYfaz7Sl1ZE/yLld5/+9G33Lza+nfXkesaQ8x/93ivLjZj06FjRznUevnd+dOgfBR9leq5O7+t4WLuw99eSzY4lv7P542tl2+xK/nTgVmHK7MLoi2H5'
        b'q2JLfp9jo1h/Vc7viHjL+XTDu1drHh9bevTnPzHpK6s+nTX0VLs9U1rntDz50em37GxjUv+s6UyLb4v9ZcMvsy1m/rpbd2er04/Ptjm2d+z75IM/8FZ8+CPeZ48dJqX/'
        b'5WurH6tmTd/xttzkCY3yh/LwhYAgv8VBfE6MbmegY/wgIIRHnxDnzsU1rgHBCYH+8mAfSK5rA3EFxznLhBnA+5+4wQ0b1qD6xNQgVJFKw7V0KV+JW3ANvo6uPXGBdg9U'
        b'BuS+Clf4BwXzQP8l3If28MNLpU8Im9filgiyg+g7K5vJOyvpi3FNaZA/rgzhc8HorghfQ3W+VBO+iq5ANliVHJiAazhOvAOVR/At8Un5E3JqiPebzEpkL70gUAe+2sPY'
        b'hQMuE+DeNdPl0hG+n1xDts0P+tCS909ksl3GnxGHWXmaoldVhbI89g5WMAmNc0bMKPhnEkFDHIBPnr0BG/HPu7hv00ScvfOw06RhO6fGGYdmNMwqX/CZle2wo0uj+pC6'
        b'YWOd4DM79xbviyGtIV3eQ1OiB6ZEj/KFDlOH3aYOuQUNuAW15Q66hXdpb27t3vqG7RvLB6MTBt0Shr38RgXcpCW8RxLO1aslvM1kyCV0wCV02E32mZPHsIdni2dLbFN+'
        b'3aLPrByHXT1PBzUHHQ+pMyE2zD00tyViyM5vwM5v2MljlOP5pvG+5njOabyHk71HReTLqJhzdG3MPJTZkj7k4D/g4A839vtEDTpFDcMtAs45+qGDy3PtLRsHnaYZmsMe'
        b'urifntw8uc1pyGXagMs0YpWdU9OitjmDk6aD8OfPbByavJs0Lbwmv7bgQdcYMj2Ork1hTbF1+eWLhq0cm9SDVr7kqr170/oBe58h+8AB+8C29EH7sPL4z+zIfH5m5TLs'
        b'5DnkFDjgRBqcwvqtwx7aOzfZNNnWLW7aDA+12bcpu3htLgP2YXW8B05+bTaDTgFtugGn8H7r8D+PxvO4ST5DbpEDbpEwfoepD4jx8Pd3WrL2b1pNXWjL/djWeuFUwY+9'
        b'efBJzgw5ufmIkKzziAAIz4iJgWKMCAlXGDHJzNToCzMzR6SZmTkFKmWhvhiu/OstBsDGZcGPcZtpCFTTXUQ/jpJ7psPH33ZxT9VCHs/nGw4+Prd0qtq4SzrKF/HsH0ht'
        b'q6Z/LrQqSx6WWD2Q2P35kYgTWRul77QEQk+IA7lL0mgBAD5xbdwFXL4mEZwEV6XgmtQEEWdZLPDdGINqZlP67zgJNycmpWwPAsINbJvHSVfzcadPNkVqVyAH58coehuu'
        b'4oWoknOMr06SH6GRlGwgPJvPeDZl2RxwbHGE0MCtBenjmHKhELi1YBy3Fk5g0YJYIeXWL1wd49ZlwK23kPcv4uhLjuPItaZok0xppMkTyfFEIkxfpvx+3q1RlejVGsby'
        b'ilUa4N6bGNU0vm0ZbJZq5GnQof8y0KzepIrXaIo0/lSBElpyn1FrYgsxhdHr5w0c46QGI9ldz1s8noAvLFCul6kZxc8p0mhU2uKiwlzgn5SHa/OL9AW5hJ8y2knJvoyR'
        b'/WdMNF5NhvCM4EKCoZSFBen0xUBiDZSWjhx4th+5I5Aol/9bXipK0c8gmz1q08teVaxI8l8SiCB1pm8tkgupKWZJCck8+laHdDrqnJ6ujnwYK9SmgJKMr4U9Oc3vWaOO'
        b'Nzme/FNz84GDaZZxoWflh0++54xc3/rJO9/t4s1vimva05zUGnY+ydxcdNAzMHTQdvcvbQ76JPmbt5r7m59w4Xo/k6iEBXI+jSOvLt8o9YfdjivwwWQ9C0T4whJuMuoR'
        b'4iv4jPyJB4mZZXNfTQxeAqFIaIOqcS0LNa7omrAQndwmF/8bfxePhRTq6SNS9kYuCx6TjcGDvDBMgsdCE87e41PHKf1e8wcd4/qt44ZdvIZcQgZcQrokvb5vRAy6LK5Y'
        b'wgKKk1vdq/3WngDx5YlfkxVgeGUyIjFushETw9bRECqmIYFV4zrROhOGRsRABkSTjR9DRiD6KwDRRjGP5w2hg+f9Q4HoqNiHuyCdJtDPAsEEX7BjZYRxJYR2fASVoavk'
        b'fYpAQar3usQIVFOCLqML6K4Zl43rLfBJXIk6KKXNmhclLbUEjk4OSV2B9kf4s1rAcdyLqqSlJaSpHJ9GdUAq182gbUA/UacW37AKE3L8FS64nueIuzGrSs7H++dowzR8'
        b'jlc0CVUCqcVnPWhDip9WWloqBm37dqDbHD6GetfLDSeFfbga7TLCIfCU3byQ7RIGs/dwA+4jRQtLt/E1C7wXnTS8oxcZEAAAzOP4qGbLCl7cHHR+ApBKjF6k4Z4VLABI'
        b'RQpjycIUANUsQjIGqOL/IKDmA6AqxxcrKIo8V6oYDz8EnsgtLy8RfE9GTx74v5rQ5xTQLrUq3Ysp/HOdk7EV5eToATkLc5gRxiQ+Pi1WFgdBXUPQdAFEgRxdkQZS9GJ9'
        b'doFamw8PZ2+ldxpQPA7SfI2ygOqYDx4YPM4GJZlAPX2x3395XLp/IPy1YAH5Ky512TT4G8zwnx82nzbExfkHUi3j7FUWaIteWnIgA6BzVcwKDaApl4D51mKYEKLkfxTe'
        b'xrQUFbOoRp78n0W2//OKxhh5GIscVikL9bOJu1zQ2E6IHagbd35//BgXPfAVU5pKHol0IaWP0HmzCmbtKs1n1Yz4VbYcOaaVbd7y2lJPC5ZfovslEagKAH43RwsiQTKK'
        b'HlYALcfgejkqB6i2Q9d8eKa4NY7qedOTVkWc67ZuCizx9+Ag56Ul2Q7cEhWObqAOEKZx09CJFL01fHX1yQ9H9TtglGFcGO5wojp6zGzIy+oxacpNBTM2uBIdpAZiuX1H'
        b'OCmDk+fDUDN9fsYrAtyToQLITuPS0AEJfb7W2YyUaySjs3MKHuQquXT1/b+8I9D+FJquhPxx+6Fkyz2h1vsy17TIXBtvPz7w1lvSrje/9ByZdqxryqP159eEPHTou3It'
        b'LXteU3JD9C+2nVRbfW7y1s2236JdM706nWcc+eSLvQ2610r47xR9Oq1O+vbGU5/IV97wk/96c3i78pQshJdgtjxD/oG720OJw99LEh2e/tdX9WvuTIt0OXY23uTd1NSq'
        b'36/9sCes79ufzBi5+d5P/DaMfPDT2NTgoY++wycHphx3XqXKPXzmzIKvxdrEt1a/Kpv2ZOaD92/96VeRj9/4Zmrl4/UrXjn6TthJt2+zK9yqPsv85MaUHQur5ZIn9M3t'
        b'QltIY9EVVMFSWchjVQVPppA9cxK1xDwL61rcaojshrC+PuwJfcekGV9GHQG40h/gGDJaktaGwG1B5KlEE24abhEn4EsbaeKbmOUmTcQH5UaSwDmgA0IVuiARbqbWRPii'
        b'C5AYA6qX4jZ0gReLjuJdNOHG5agRsmLIiUOkSanE1B18/5n4FM1y0Tl/BclxoctGlueSJPcMuk7TcXwGnyxJRDdicXWiPNiQjluFCtZH4cNy0x+W15I6+Fhay3iIKcth'
        b'AcY1QUYW8pWBhbwGLMSJZGO2Do3yQ/KGgPI4YByfOXl+6urT77tw0HVRv/2iUb7AxnPYw2/II2bAI6bXbtBjdt2iR2LgL005LeFDdr4Ddr7DblNOz2ye2aK9uLV169lt'
        b'Q27hA27hkDQ+tPMYsvMesPNuWT5kJx+wk0NnD6xs68KrtjSFVe1o8WpRtvq0xZ0N6hXcN79l/oZiKCZxICaRmAR3TasobXIZtJrSktPm2ZrXZTroM53mh45N4U0lLTZN'
        b'MS2bL25v3X5256BbFEvE//zEnXOeAlmfjecDNxlkfTae32ltYLTXbOKCORxsFjdTgGfw4JORKCljTAQARgQQT17Gnb63gPBCchdk/PjjeE61yoTHm/wEONXkH8qpjon9'
        b'uQ5ppEDOY8d7e/JXjJ2vAFjdoucrax0n/MLPGMhmcyxDo7/wI4zgj/1ij+A/+Is9eXL+q6fMlrHI8D3JSR7NMygvGH+g8f8qI5sQggQvhCAxS17w0c0rn0WgJbP/Zf4y'
        b'Lv54z2K89D46h5u1JSJchm7QujyqXIHL6BEq0OA61ASwgSuT8cHluDyJb4sOoLZ41I72ofOoGb7IuTRrE3RjTqTa7d1UoTYNHouJD+jJOQaZUNuETCinw5ALWb/1k128'
        b'pFZdsCDtlMPyOU2mefxKi98Xb83zdnPeGzMtWaLc1Z6mfPgT2IlvmCbc9ZCLnpB3hfCd6fjYc9mQDneOwaYUX31CRhSO98QbC4jr8VFaQLyKr1DEQvX4SrqhgsjwagWQ'
        b'alJBXF7yhPy2Ia7HvfwJSBqOz1IwlcT70TvQ8SkAd+NqjLgT9y7lwwJcwpVy/jhPI4BlxDKT9SodRbIoI5IlGZBsh+T5fOpZVe654tinjrJ+z+hBx5h+65hhO/chu6kD'
        b'dlNbcgftAvrNAzQyzphgiTQE8l+aTZEceFwuFWX8cAZP1JLf2/sLmLRJwuPZ/gCX/5q4fD3Q/DPSIMG/9Wmhgvu/5NOQHLz6qtny4gK1TjvmuOxEDDxVRq7maZTr6WkX'
        b'OLHR+ZWyiJeWEsz84lIVKenLVgXK4hbHxyUuVyQHykBbYmZc6oL4QFlsHG3PTFEkz49fJv/3/krpkCbXhBwdOK/3zCq44WjD6QnaosteQByr8MEA8quRFUlLF7MqF8nP'
        b'UB+6j+vlqN0MNW+FPwmoYiuHTorNUPlOOX1dAB/2wo3saSfUxhSAs1K49cBtQnQGX5SoR4Uf87TExj/845fMPye99Q5zRK1EGxoX6iWN84jzi5M0RKZtmhItiIsIT1KF'
        b'NsjTd/rn+M2ULPcTBNQ5vFWpzpaEJ63zyPE7K06PEP00MK9sVevB2N/3/vw8euMBn/uuw9y88KJc+ISEp4gNWWOl/GNAhbr5QSGoi3lidXjCstUvchbJa+gUdeMZmWjX'
        b's/J6RBTq5FsCSDFacgudnZRIyJAMNQX5iTlTZz5q5VCFXPjSmEfWYGzTj5hBEqY1lDfmGN0xk7njaIYpZ+885n8vVoCpD84ddJzXbz3v+0rBcE+Lx6BjaL916LCdc+Os'
        b'Q7Ma5vSbe/5veegc44ffeA9NNv1hHqqJJr3y6G80zfFVsFiMqnBtCKokMMahFjHnulOYj0/jtpd7cB55VGiMyuSXcMdqpv9ZLybvIziQmun44EwLkIXKTTRBfUlMJukp'
        b'Oc0uVsEFiN3BZgnMlwuUOh1kmzlKCLYTFdFQrcxlpdgX8mmzsXz636XTLJX+/4MTSFJoVvoabot5eUUTV2j+ZVJahe5SlOqeybLSUI+3Jz12m8ESUMnsOG0JL1NkoAlJ'
        b'uJ6+uojb0XmPxNQVuvE84SUcIRnXUd0nPQy/ky4uje5fGMKpZ3x1h6ctgpY1D31YDfXcS2qok75Cl96y5n9hEr5q1bRQb7Mw7hvxtPAsrmyJg2xmucPyffLDH6qE7/Xk'
        b'vGcSjpPmlbj5rj0lendToF9hjmhVo4nGJfrCrVZzSWMJ7ORf6i3fyraSiymxKOChqy9UWcnvAR8ylFl3Zz4hma4e1aO6gGfJWCo9rMA1iah7Czwo4qJTxDvQIVTzhBXh'
        b'CnEdoN+CSWP5XxK+S5M1zw2y8RxkC9rDTjF3QDuhGPb4vs94ZMSn5hvAEbVbPCF1gZUbXBInmED7x51o92RUL4QE8xI+AiDzvUkAAZlxFV9zyk5gGxPH0CwyYuIOzlDy'
        b'NXuOopBEaOag1eSWsEGrqfTIK2zAKaxr5qDT3H7ruQ895EMeIQMeIYMekJEPO00ZcgoacApqyx1yCh9wCv/U1bt/6sxB11n99rMeuE1t2TjoFtY1bcAtsk5CVQUPOAW3'
        b'bRl0IixnHGSajEgJYmcWaSiP+pfpDisaj6tp0zHRjxk8Q4IDMPq0BGDUhRSNXX5ognNY7M2dk4YI5IKUlIVy3kI5P2WhWvHNCZ72AEzdheCofR8fWGOrnGQy+tQy9iHn'
        b'4Ls6xvVGWkBXV4Tb4VUrHt8NeH9P4KJVdRY9m7b96erdoV88eJox/VrLxV9tnbP5T3//8V/vbNtlmYmOFPteK/P9/KTtyfjY1sZoyc+dlpbNarmWLJnmbNf817Q/9B2v'
        b'Hsm9dmTgt81+ZnlfNNkMXz7yEyuzgdOrqj49VWPd6GfePPRh3ZTw3EU9pfNyLn/Qse/9Dtdlex6kyDN7dn3y+rm+0TekkyuPFagHpqQdrD/Hn7tE7fKeWuSvduBfc43U'
        b'Wf7mI9kGtftv1YLfDPzllXlOZw4Fo+zbwsSvwsry7Y6ppUd9Hf7YM//bNRWh1S1HOtEG18hf5WPX245/uCb4Xb7vJ4MWYbdtjuebH//KUTdw+csLP8v9R+mTfvfh5vTs'
        b'36Tc6X9fP6llhvltt235k7/9aPuXF/9assvnv/874S99Jiodd+BL5fQPZPu/DF34pc2k82djFtZ6HXkgr7ZbW/u59+x9g0/Mf/zVqqR+bUxqyMMpd72vhLz/pcODEtuV'
        b'X0WuvRhd3PAZ2vTqont37mi+25a3KSmWe/qIs3okqX0kTH106V2X5cuOdf5IGv+hzbsnEuNXNlr/qsM6Z0fc33x7pjS4RH3cGxDdEzJp6cUrH21IPWJ9rM1uS2Gb54Gt'
        b'i65UbrwVuf/Y329s3P/RO9rUp7rzGe2No402dZPnZiyQjmK/qE/35x12cdgf/fs33t8w7beTFJdML2tH5rz+SW17m8XcVascVzz67WSHmr8Nfn49ct173yz6r+gtVZu3'
        b'1Fqd+KXXX/8ZtvbT1sMNR9x4n/318M7Th3/22z3/tXRq+KBTePT6M+h+WGTejg8amx/nhn+77H7y0/82P1XMu/fFH343yeab3/zsstr679/+Xnv78hcn/rIy/+ZPK5U/'
        b'inzsZvHlJ0F/nwL4Rl+LuWqNjkLI53G85eh2DPm3G87KKAlznIv2M6DB3fETWNj8VHr+hA5ZT38GjT74ysRKVeBm9i7EXnR1Bq4CqlYdJOZwU7Q4g++FjqNq2hqIWhQB'
        b'S4LwPTtcnpCUIuKkwAPxSaWU1ZCq0YltiSRUOfgFkX85IIHccIWPOxaWyif9sBckJN/38YNfs3gpqBBzZcafeeRn14QfhqWSzMyCImVuZqYm1Yij1mKO+ztwy4U8zsJh'
        b'VGhi6kQANKxqc5Nn1WvN2pawFmVr5PFX25Ye39nt3aXp9ezW9y7t3tIT/OaCd2zx4sGwpE+dCRFVNkceN21ZMuAc3OU04BzTPytlwCmlf1l6v2LFwLKVg04rCfG0bSjs'
        b't6bvPLzCGzXjbO3rYg85lM9/LBa7mpVbjtpzti7DNs7DNm6PTIQuZuUWo5bJPAezYXPrftupowLy/aG5dV3IqIh8HRVzFjYgmFBBwgRTKpgxQUoFcxD6bf1GLahkSSXv'
        b'USsqWRvabKhkyx6zo4I9bQoadaCSI5WmjjpRyZnd6EIFVya4UWGS4T53KnkYpMlUkrEbPakwhdnxyItK3qxpKhV8aJN81JdKfgY75FTyN5gfQKVAgxREpWDDcyFUCjW0'
        b'TaNSGOsgnAoRTIikQpThvmgqxRgsnk6lGezGmVSYxYTZVJhjsGoulebxDEpieVSezzOoiWPyAoP8OJ7JC3kGUxcxebFRTmDyEuPziUxO4rG+k5mYYhBTmZhmEJcycZlB'
        b'XM7EdIOoYOIKg7iSia8YxFVMXG0Q1zBxrdGudUzOMDRnMjHLaKaSydlGOYfJucbHVUzOM07DeibnM3naqJrJGwzqNzKxwDirm5hcaGguYmKxQSxhosYgapmoM/atZ3Kp'
        b'oXkzE7cYxK1MfNVo+TYmv2Zo3s7EHTzDcu9k8jy+4fZYPltvvsHSOCYvMLbHM3kh37jeTF5skB8lMHkJn7ObMmw7ddhWTj89jf9PfbyK3lFuOrqWz7l5nw5pDvnENaBi'
        b'SXncsPPUIeeAAeeAT5yDDgnreMPO7qctmi1alIPOAfWiRwLOJfihfXCXw4B9VHn8sPvk06ubV7eJBt2DyxPqcqpSHplyboGABmbWD0yt63KatG1xXbkDpjOf8mebRnzN'
        b'kQ8BZzaLfFiPCkEkk0BvbvJq0XYJB0wjn/JtTJ3JDVGGu0AE53VyadxwaEO/Z/qgo6Jc+tDUinSwvMWrbUGXQ5e+d8Ub8e9M7Q9IGzBd+pTvAwo4H6ZlGc+gBmSypw2W'
        b'DZi6fsM3Nw0kjW6GO0AEpBl/g6XplPE3gAhww8xdPmDq+ZRvazqdtNG7rB8JQfzzaI6EZ5rAe2A7+Zx5f9DCQdmiQdvF/eaLv6NvWVXETkpw5951t0sINZT1rUf4EDn+'
        b'h7X8/0nQsn7GhCcGKhqe6AfJgbRzDJQ4jsfjWT8FSmz9mHz8UF58ShzMdUqnC9QhP4/gad8mYxy+oK/7wGzPPPt9f/pbu8jG4dtF7bFV3/76aoYs//MtK/dYl1VlCX/R'
        b'uvLL7W6uP3pPHbVe/OHsXzRvW/1FxPrpO/d4236Yxp+PWrRhn32anX3Ne7Htzd8dfoITqxf6nAwIbrXdvXV65flAl1K7X64OaDX1Smz8R1Fj9GGJ7qO3Ptq3ffrf/nlp'
        b'3eXoDwY/bp5adXPV4qUtez1q6j533r5W9raD2NlD/NEq9PPlEefXDM+LKvrNut6UXxznfvT7f9afmVpW/MCpONfT/tzTLTxXK4+25jNyiyfknRN0Bh2yp//yWiqupcdw'
        b'qA+fkqKrfNyWg6vo6zhp+AI+Tqrm3XDbtgWp5FDNBvcJUCs6iOufkJQG96B79qgK1ZJfLDlIft/rcCqqNeEsbQUeqAudoBmkOWrE1xMTkv2TTdzxYU4s5Eti8NEn9OX1'
        b'XRm4JWCJiOMlcgvRXdxUjNqfkJK9Fz6z4vnMH9WEJAb55y6DqwdxrYBbhLpNoOdbSxnFq8ddqOn5Z8Sc0wIh6szynxdNE058WYkracpJdBk1uQHJ24P3CNEFVIVvsvd3'
        b'gQuGgbYyyEwTcZUJJwziocvT4ynZm4Ga1+AqOWiByatIjQ6FoGO1VKDAF1Eb7UaHj4A9hjsCieH4qBMtaPI4Gb4u4izxWZoim+DX8aGA1EBcSeqeZBlqd0rxPT6+aQdT'
        b'RF/BbUB3ZuAefBBYZYh/iYG3uuoFuFuI9uMzCfIp308d/yOE8T/4oZ1CuecLlPO5nzEGqi5U6wBHMowM9E2Onuh97cqJ7IYt7IcsPAYsPE5sGbTw27VwWGh2IGl3Ur+N'
        b'57mYj4WBPxNaAOtz9egXOo7yzUSreT+TuADZ8/Abcg8fcA8fdI/sl7gOSyxrpRXSj+19Ppb4DktshyRuAxK3ptiPJR7DVi5DVj4DVj5DVn4DVn7D5ra1KRUp/W6vfGy+'
        b'6ql4o1A0/SlHPh/Rz9HVppy5/a7UPz8pgS9OX3N8Ueiwg0u5maGHfvvgTyRARuEyOw69I5wfwqEQ9zgrAbbkwSfDzckjggJV4YiQvFUyIqLV/BFhgVqrGxHmqnPgs6gY'
        b'mgVanWZElL1Vp9KOCLOLigpGBOpC3YgoDxg7/KVRFq6Hp9WFxXrdiCAnXzMiKNLkjojz1AU6FQiblMUjglfVxSMipTZHrR4R5Ku2wC2g3kytVRdqdcrCHNWImNYLc+ir'
        b'bapinXbEZlNR7vToTHaanater9aNSLX56jxdporU90Ys9IU5+Up1oSo3U7UlZ8Q0M1Or0pH3dEfE+kK9VpX7LB5oCQZl/asfmYyhe4bxg/wrgloC8//85z/JG7s2PF6+'
        b'gAD8xM9H9POHwD0JYG9KxLHO3JvO0lgvwXcS4yvoI9aZmYbvhlzoO9e8if9EqKywSCcjbarcFLmEvKacW5QDI4YvyoICw9YlO5lUpOC6GUyuRqfdrNblj4gLinKUBdoR'
        b'8/FVUs12zlApYjUj5gmz2D9BOkezD0RS1qbHbqMCCHKP+EKeEBIXqcUuk8fihTDg0WVmnKmNYSsvGZL4Dkh8+wPnvOmD/QYDlwxLrB+YOfY7hQ+aRfQLIx5w1nXOP+Vc'
        b'aW//C1Q9RD4='
    ))))

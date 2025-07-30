
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
        b'eJzNfAlcVFeW96uVgkLcUHAv3EKxiiIucYkiCrKJK65QQAGlCFgL7oqCFDsqoIALoKICArIJxi05J5PpZNLpdKfTk6GXdL7JdHe60z3TSfpLd6bTmXPvq4ICSbr7++b3'
        b'm4FfvSrevffcc88953+W+4p/FRx+ZPR6iV6mFXRJEXYJacIuSYokRZov7JLqZQ3yFFmjxDg3Ra5X5AkHlKaA3VK9MkWRJzkr0TvppXkSiZCi3CI4p2mdvkx1iVi7JkZz'
        b'MCvFkqHXZKVqzOl6zaaj5vSsTM16Q6ZZn5yuydYlH9Cl6QNcXLamG0z2vin6VEOm3qRJtWQmmw1ZmSaNOUuTnK5PPqDRZaZoko16nVmvYdRNAS7J0228z6LXDHqpGf8p'
        b'dLEKVolVapVZ5VaFVWl1sqqszlYXq9rqah1jdbOOtY6zjrdOsE60ulsnWSdbPaye1inWqdZp1umpM/iaVSdnFAp5wsmZx5QnZuQJW4QTM/MEiXBqxqmZ8SQdWme+VhaT'
        b'bBeelF5j6DWRMSDnAtwiaF1iMlT0GSZKU3oE9inR9cSeXYJlHn1MgjJ8iCVYFBsVh4VYFqvFsohtm/yViZArvBAmx2fY52RZxAbB9UzqWI4VvlgUcjAWy8OjsXw7DSoJ'
        b'jAv3i8RSLI2IwuIIhZADFc57sCGET7vutDIpXOopCJrEjN7wnYJlL92MWwc3sNt5DBThk7hwIlsasS0c2ryx0G9jNF7YosKi8G1EWpzNPpd3eBSWx0TFbvOmhsJA4jQu'
        b'fOM2b//wCD8JtMgFMxRNCkk6mCxx0CU3uzjW/5X9SHWzSVxSKCWJS0niEi5xKZe45JTUJvE0R4k70yv6OYnXiRIvnugkuJLkoucnRsV5xQv85sO5MoE6xs+mbVi601m8'
        b'mfCSShhHItIlJvr9PnqDeDMkQMG362p0YlRrwGyhWchwoT/vpXvKP58gvPQfc95f8Kn0QdCx2D8LGYyPZam1kvtOJGfn/Qt/svAH+8zi7arxn42tGivxfufgR5K/xAtz'
        b'fiwMCJYF1BAPd7GIZE/75+2NxYGQC+3h/lgMzVu9aRcq/AIi/DdGS4TMsc4r8SJ0WibQoKWZznJfkyuJGGsEuJSCNRYPply0nXCHiPWYjApqKxGgEFqWWtypDfOTTGOx'
        b'wmR0os9lAhS7w1PLJGoYDz1YErPbhA9Yr/MClM6AWstkRq5q/TroOGWCchIVNgpwjUhX8Sas9V8F1VBIbaTueEOA67vwsTiqHduwhjS63HSIMVFBc8UvEkd1TUpVYaEJ'
        b'O5X0R7UA57EG2y1s2xa6ZPjoTRY24IIAJdiNjfw+5r/0wktQaxrDRtQLUJss4UtNgHIDPITzJuxmzF0mWtCIubwN78G1ZfAyFpuglP15VYA6bNzLVwv3d+zA+lkmNWO7'
        b'gejheWgWBVQ7DjvNcMt0mDQWLwlQrpzPuV6FdXAD6nNMYwVxDC0OmsS1tsGNlDS8hd1jGBdtAtTDfR0ndyj6IPRAs5pvRCsNWgp9fEXQJVdiuQuU0PZJVCSuQGfOGfZ5'
        b'wNWtKhN2sW29KEAF1i0XxXYNWk8GxWG3RSbKugp7aYv4UlugCyrHrFPjfTZPB+0D5EOluNQ2Z8jDDrxmOiwVKRavXchb0qHfRItqMmEfY7tWgAuafZy5XVDigz1y01jb'
        b'rtYpPPlqNsyHc9Aahd0q1nBLgCs7j/AB24KUWJxG99n0d2j6uD18Cndo2BNE2NFtVogzVKTR+lnLVngGVSlEylUpDrkGpfHiYqxQvQ4ewWNqYzK4S+Smk6RZ2/JsKHXB'
        b'+6QXnYzlm6T1+AgeWDzZQht9SOE68RyBGRvXTnfgPt7j062HJqyMIcXtdrZJ6IZiMl+TCzx9yek43WdSvS/ATezSiHyUQBc2xc0hgdu07gKt/g7fi0xsx/pUqKEdl4jD'
        b'bsDlU6L13dkO3XDOTDx2s7YWkhLmSUWSd/HZEelc1uQkKsp1WqZN8S6EeqzeSTto4/2aBPPFDezH5my4mKxWsZYHAjTtwQucixjMg4vYD+fU2MXo9RIbkQmc2lKszcHq'
        b'l9Q5CnGe2oN4i1Nb6j0HruMNNT5gAuxk1tyezYf4JKhj8DI1sNV2kw5PhwpR8ToXboXeRdSiECdpxDKSOdf8p2S6fX56k5nxVihAATRAiWU8NXkbjQfi1QyHmbRrDoZw'
        b'RdmesAAvH1a7sDkeCnAbLu6wTGOELjGFhZIQMsTeXUlQqhBkeEMSK4MyC3Pps6CB9qMkB6sIUl7GNihWCPJ0CZzBuyEW5us9ycpZe3Ey67KQkWFEnKFM6hEETVoZR0xn'
        b'eEDAVCLLxmJByBKytiwW4SWXZm+KlB8gZReSyBE/2sPXsHfT5kglXgUr8yUpk7DAMp8pIdylLa3EQmgNgWaFLppYurU/FLqS4eauaCHYpIDqBRstWka4GJvI9mx927Ea'
        b'q/jHYGg9fgyr5cJ0LJM7w+Mcizfr/QBqEsTOxOdd1jsc2lnnnVjBe8MTuWydJycND/WL7ITbHAjfg9JlIuWLhDB92Gd5gZG+jXUCVobDPWJ5sPdCuBuGdby3vwz7XeSc'
        b'8gkC3oc20gpyQe18ifB4v1pDe3B3+0Rho8ZJDffWWgIZHwX7sXaQke0Oi4QO0hN6a2ET+BsVh/AS6UYAG5OHtV7S/YP8lMmSxBnI+upIllBCcgzHfiX2HsaXLXNoyAIn'
        b'qBzifx/pIJeNfLMwDbtleD8BL1qWMsDFCouDCBkDR/HMMAndjWZU7kUrk6KFQ9ChgocB5DL8abAHti5hk7QPCkkGLXqysSKshoJUUqk6IQjrFVAOj0PEDe7Ldh62C+KG'
        b'tdAfZ8Udq5ThYyhYIe7C1WkbRlOGZjwbLu6ZVe60yYXLCGsWbB3qW+Y4Ad7DW0wr2JDg4wqo1cZZgmjIcQ9sGNTLoW1oZaOTsZstnQ1ZiBUKMqc8WrQv24wzeDtxuNbZ'
        b'BYX9+EDkq02ugtxjnLH5+DDNNovL7KF5aOw9kc17fL/JQk2ueI7LFXKxRWcbk7CTKQRWEZweZVKFAg3cIJ2KxidOC7ERrlv82IjKMMNwEyPtwLxdqVrvEHEVJqhXYSnt'
        b'RD8PoDY7wRPbAHq7zIQzQg1tbF1SmPASKZUPm+Xc4imDuzdoyKFYn6nBSq7psXjdKQAuHxe35N7C06IO7o5hWisKd2j9nK8AeKTYTzM0c5P2o6C9wqa3LY7mjz3pXLIv'
        b'yPAR5q/gwAIVi3SONirqUhtcC2Zdp+EDGXZu8hCtrhDOakaoh30MtmoGteOQguKUomxO/jjcjHbUbvaJEADrIZ+zIpNhR8J2zjZ0mcPs1DscNQIe4QVRI27KnQ5lWJaw'
        b'zvdk2GpToF64P5wfPlAOXa7Ra9ZB23zBiNUqPE+Oq1q0iBao9Rlch32jQ6F+qUYhBEODAuoJ7HP5FnuFk+IPQsYwG4KyaGZ1jLNFeEVBFnsP87igkmZSeMno98eIPNkh'
        b'ycaajFgbs3+xJE7htPQoYQdTvnlrscAZyyM5TFDPEfrBUX4zlDl5HSVHzFHgKbSkDkOzfYttfRmSLYJeggwKymu4cDOwfeLIbV5IkPGMfAXf507aCDPF+PM5DJymxGwI'
        b'M0jLewehbzqcJfXRgFX0CLWb4eEw+7ftcDCKGwxWGfnOdm8OqAT9i4e4SJ8p9pYyPO0jPYNuivEZVSkUG55XynaKccpFbu8Tt5RuFIiKc582rNGmZS32/hQC310FfXYt'
        b'69k5h28oXKVY78FogEgapJs86DuCsE5BMWAYN8KVU12HjRD5YUh/lXgaHLJDQfveEiWaednJIRm2DSpZKPmF63ZD3xTltCwxSWTrMTaahyuaHXnnYjFfDFc0eKaACqjw'
        b'EQe9TFDUw0fNVdrHSZNtU42jWfpDxkPhYglcecklxmOlqDdnxhLAjvTKzMyKoJpLSysjF567iK/8IDYTVovLcKfsZiTE2yHOosjGwmAxoujZEfT85rXCle3i3j2UYRcF'
        b'zXdEbmpU+HRUR9CKhbtEq38md9u+gpP2ciUzfk6L75GgW0Xa7TJsX4Y9vLM31MU/B+ehoWuODorfz2kJlHtxh0Qdm/G8vfswJTpCLNk1+RmUpnG3B43ToZezYpA9J3no'
        b'3oVlmL8fb+4SjAfI12PvXm7kmlCKg0eq3kTky1VMsLn6e+QooXUcn2YMOddHthHroWMopBgMNGyRDlQqzGTOhVwv8MpcSkJG9fllcGGWg443EtaZw8QVddBW3sVrQ4FV'
        b'ywjAYzaiOLRYsknlFILXFOL+1W05OjIWSYIqUgtFEokhWljooYBSrF/DkXcmedtKu/YMifge3pkoirhLLsfr8aIBNUK922iLaIPuOFExiuUM1rtFIHoZy51HUetWyCVZ'
        b'sO4vyvAJVMRxhD6Jpfuej1q4SWPTVAcBVSrg6tID2iieeezG63DPhzLYwcwD71BAw6L5rC1Yiu3xJp5zFglgdXqRJzhTtfMpkMs1YY9ELHGUb4rjA/wWT4kyDNVRKL98'
        b'wtO1HKzfjLXQSqkFy3evE2BRJFPPiR1wJ5i7esJkZAmOVYD8eVjDG45CCQGOn0Pp5foEPosXnls2DhuHSi9hSWJ6lRdGYc+VTEr52V/lApRAwwaerKm8Kcm/Syy7SEXe'
        b'qtPxNm+hcA7O7dtqgmK5mJtehQYtT4PT8DJFHPlY5VDK4WkwT0AvAK8yQYPJjZGsY4lXnztnfMFOLA6d71DmgQ4/MaNtxV7I1x9zqPJQ+N3FM6Qs1ZQX9gxVeJQhYspa'
        b'RVFH6fbZDiWeFWa+2GCyyhY8600tTmJFoMoE18QEuH0JnNMnD1V/DkIXp3Z8IeVn9+DmUPUHn3jxtbLQ2ooXh9d/WqFVTDUTY4+pTGKmfY1ta98MkbmSGWRZD2OGij9Q'
        b'M5a3TMErUL84Z6hQQrByXqwttJBUy6AYe02HFeKKysjRPeLDwrDqVDwUOJRRsvAyZyF9bjw2z6MGiVh/qjqcxdPQ/RvisNk8VF5Z5cu7x6RMWoZXTWMlYnHlKrbEiJLp'
        b'h96ZU086lF0Cx/CdCeR4W4xnHCovc+ARl7Qe++dQmprvUHuR2xP6lvRZSwj4u0VLaGBKcHUmp5hCYNaMhaew25UtpokVL3LhgmUKE0Iz9DNNItx0qNrUYBOXgj9ljY8T'
        b'dzoUbbZBI29RHj6ONxfTbLxIQSTr4LyHqI5P8TregNxJ2O3mJBYKqKMo1ahNtM8tS0jPudZ1CXDbvEcclUcuphwvJ2L3Iako2AraNy6qjSvh3vIx1KAUd/38RkqA2Zq3'
        b'4Y3TrgbHwhHlmiV8TCreDDzt5VA18oFesbpxHypVs0nCQ0WjFyhz4FuSm2XaRggwVDbSRvOG0O2Lj5OXHqoZeeN90YqaoXod3tlLTTahX6Qs+yZvc8LaMNrux9SmEI2v'
        b'kqTeweWQtXg7tuQQ4702kddiTYS9IJgPRbsDsXuMVOS8YRGBEBsUh1a8gvXjHOpTLqvFNV3COz7rZlKDQqz/3KRYrljksH1HoBdXi8HCFQH2Gb73hFC3veE2hf8OtSva'
        b'vkK+6DgoXitfrsb7SrHlagohKB/Wig0USVbCU4fCFhlTOR8GFUcPwwUPtUop1pVuQU+4WAS1YsviJdA2VPJS4gMbWFJwVA89h9Rmm35WYv8mcWU3LHuwzt2hFkYuQtRN'
        b'QsfHixdDx1DdCes2cxYyDNAFNxTqHEatmQAWWg6K1GppF69D7Ql1DhvTKsBlfBIs7n3zUriyI2WotnYc2vkYwwESOmV7DsW1qXhX5OAZ1K/e4ORYXcN+jgXHk1e5xDvU'
        b'1tzESaBxDFRq96jdmAQeU7SOl5eJlM65kwG0YKHajaneU8KmXTmi1Epig+KmqbHTJrRGkkCzaDGXZ1JsXAB91MgG9bMy570XOeiMG6faAT1qZ6k4z50XodCm4SF4WYU3'
        b'1BZbTfvy+NmiiRmnEwY8GyrtwZNAkeXHx6ApArvVJtsGXJ9p4nJJhDy4uIhyIVFBnrCdrt7Mc0dsm0hReAlpSCGv7RHmthEA3bfFfVDIC4Jy6N4KJduEHXuVWE+RQ41W'
        b'zmE5EirXYEnUEijeiKUycgdPKbyGtqXiDhatxdZILI6CvG1KQbpPEkja2GKZSk0Kf3gSieWBWOarhRbKTk8KruNkk7RYygXpST7koW+MDzb4h8sF+UsSaElKW5/MjpTY'
        b'D62BnzXxcyZ2NGoV+BEWO85ix1gyq3Oqs+0AS14ozxNOKo4pT8j5AZaCH2DJTynihRTZFsE5VSv/8D9I9C4ah59Qdrhp0ugy+ammJjXLqMnRZRhSDOajAcM6DvsjQjxT'
        b'9TmQlWnO4uejPvYTVY2BqOXoDBm6pAy9Hye4QW88aJvAxMYNI5WkyzygSc5K0fMTVkaV0zNZDtpPbnXJyVmWTLMm03IwSW/U6Iy2LvoUjc40jNZhfUZGgMuwW8uzdUbd'
        b'QY2Bplmu2ZouHt6yU92kQSoBow1IMiQvZ8tMM+ToM/3EUYzBtRGhwzgwZD63IvaTTILRHzGzJeh1yemaLOpkHHUivjbjUcfJzHY2SZR/+zxmdo5toxagibaYzGyNTO5b'
        b'Yv0XBYWEaNZEbQpfo1k4CpEU/ai8mfTZOs6YD/vko9GTalh0Zj0/Fk9M3Gq06BMTh/H7PG0b/6LEuWrZ1qLZYshMy9BrwizGLM0m3dGD+kyzSbPGqNeN4MWoN1uMmabl'
        b'gzNqsjIHldSP7q7XZZj4bSbkwwbTiMUMOyZXCSMPbcfHrBfhvh/P+9nCy3XwlIVklfCQn8h+L3qKsEDIPiUkJp6IX7FE4GCKfWCFixSBCz5mYaewMyaN940zuQjuwisp'
        b'wrjEKKuTUjzSzZvrJkwX0mdJFiRmSKaOETiGBS+zHwoGcmjHFnioFaND7CIMLbS1QtV6al29ng+SW/Cc7bxQhz2UV2yDyzZENvnbzguxhsXvNVhv5qg7JcxsPy3EkiBy'
        b'B4GJ/P7qjXDTdlioP8H65x/n9zfugxJ1Npvi7iELYfFhzBNRumseNKkP8SAkHh+Ry54g4QMOG07YzhZnrGaHsUXQKbqPVn/MxW4TA+JGJT6jMGTHON6SHYc37ceOZk92'
        b'8NhMkTRH0qb1FPrazh3nAEXZVafwLB+0mbKJTvux43I8R6Bv2SF6g6tOEWoulAfQgPeoYepRvkcveAZjN1/iFX0kRWjOcbx/QApcNx1mnuOyAXNp+i0kRE7oyRGstcXk'
        b'pvGkAtgUqJWJs+8Aq60F7wKtvtjXlrqt4NGVbRroz2GJwTW8xQnuwpsL7TMZ2Tp7UYz3yHu3Yoc9lwiW0SB3vKmV2rw+PJ5rb9ulorajuzgT070P2E+YKXiihdZ54wOu'
        b'Ydv92DMH4WqJJtHvU42XIB78Vk7Gy4sWyNmnSHgsJK09ZijwdVKYWKQWeGjVyvNrNoaucS2ofOOt4wd7xx5u0gTsPaLyCFiRm9Xo6zFP88eGHx71bVQ0qj5u33BENhOT'
        b'j0grNq3IjXht4ZU3vnjh61mzO2cFPdAcypU+8j7/gfzPYy9+unaZ0bvGo8PjYoGms+HXH7e/9lpnfvmnbdEf4D/57P/a9Mn8P41/9frvneJDbny19sfvdKywHvvDL197'
        b'73gNlud/WnH+lxfS3qv7g9drN9vf/iCk83HOqu1/aT5h/Ojy27FVp7WrV376ev+mV392oPmzNeFv/fvPv3z4w+NvpU2YcmT/7prUj/7d7esf5lT+/M1q3zXpbqFd6ozE'
        b'Mcc/ybr6wm/73/3x1tv9oUnZCXU7F/9bynuuId7vTe37TrTHrsR03Z8/V8dF6t/zq9U6mdmuRLwAjb7+3uH+UkEJdVK0evtPhSbzTGraqUKrb0CEn4+W0sDzAVjhR/m+'
        b'4KmR78NiuGpmrn4d1k2IhGdOsf5QFEvBgFJQx0mxfBpe4c34jBL0R+yhGx//AAlNcFYaAnmLKCUxs7rVbrj5EkW85VhxfI0vFh0WH37J8ffB4kCpEABPFNhDgX2fmUUj'
        b'+PJkbMKSaL8ISuIFZbB0M551g7ppZnY++cKLkkhxNJRjlzNWRPGQZRLmy7D/VLhWOiD11jJ1FbTO/O1vvjAE/XLSilRj1jF9piZVfJYqgDnXVQMuHOoT2B+sm2k7g9zT'
        b'glYukUtU/OUmkUom0/s4erlI2H1Xft9FopIq2VUydGVtSoknf2d/udFfctYinS5hVQ0hhjOjVQ7I2YwDMnLYA0429zcgZ/5qwCkhwWjJTEgYUCckJGfodZmW7IQErfLb'
        b'16iVG1nAZWSP3BiZZRnZY11GFojxeS+xtY1ja8sVPplOfEslSn61zKZ7s+FlrB8SfkXUTrjjIPyJ8IzghB0yZ8igNnIjBaGdWIolMVgeG6EQ3LJlS7W2LMhv17rIqBgx'
        b'cJTICO3Uu6TYnoWPORBosC2KxZuU0bbYAs6zO5JlNkfH1uFkd3QLhcEHoOSpclusKCuUUawop1hRxmNFOY8VZafktlgxn2LF9yUjY0X++JtDsGjMOqjR2cO74YHc8KBt'
        b'RFC29VtiR6P+kMVgFCOGbL2R4seDYmhjfyZvuHOPtft8YsRnM81oOKgPMxqzjD6cmI5aUkYPCRm/jF0xLBy5iFHjIduixBEjVzjaFCyIXJ+hS9MYxFA2Octo1JuyszJT'
        b'KPbhsaQpPcuSkcJiIzHM4UGtLZAdPQoKM7AlDwVdFGDrNAv9zZZsCqZsoRWXGsWE3qyHH5tI+y0xkeK5mEgRY3mR5WvLVw4++md7GE+CHezZv6Ion41+0LJVfAyQ3YiN'
        b'ioiWkMuHIvUyKPfYarDM2iU1rWQ+8HDfbxIDfqHVhesyvupIzUj6JHHfK++/+v6r56Hn/LKC5kuNlzrzmsNbCxoLgsq0NY0FXjVnFskEP2d1U0G3VmpmJ0iEsX3L1D5k'
        b'C1iEpdEWfxlcFYFxFnTLscMHbnKUjntxc2TANDizkZARyuzINxV65JnQM0krHWbn34Rw3NgH1OLTnkOA5iYCWgqDrAkcuIxjh4BIMaCya9SAk003RCRxZRf2eOaw6WVG'
        b'VtM0MiQRu3GEYQT/2QFhWic4IoyG7m3NwNrIALY+PLNtxBIpurjLN27XyfgRiS6vd0M+dEEpNPjJ9kZC7ovBUH6IUuDb8MRFSMKLY/CaFB7xAOT4NpU6x00Gjyiow0us'
        b'tFIebHv6C63Yr845hJeWsbZC9pyBrdSX47POhA+OYOXYhXJBihclk7ETi8VI8BY8wSemhcblJ6SCJEuAPiiXinFQ1UloVufkBGGlkuidE7AOqpYRSPIq0RPogQ6Oc888'
        b'bTB3gUI1/hTPVernkFjjRU+eWE+EAlsdxgXqfQlAt8ATiSCFcknogfHDEHIwFVjOEFLGMVJ8PFRqVaWqBpFS/q1ImUZI+dU3ZdXcxIfn1N+IEwxTWPe/npt+Q8rIBv+P'
        b'Z4zJGZwtk978fI44gkEml6zkZAtBYmby84zas8SwTWs0oeS9jQwy15FrSDZnGSnvy7YkZRhM6UQo6SjvaYPwUMojjbqM5+itJesMcOBNxzbFwp8P99kSutXHj97WrWNv'
        b'obGbg+id2PNZu3AtbwgN9fF7jqLDmigDzRo112WL5HLOFjNcoprC0Pto9ggBsp+/yS8OUszKft4dsp+/zSUO27z/thRbIoyWYo+lFJvB0ja4RGnuCI/ynDtZtO85hzJ9'
        b'Ik9y9NmelIcLC96Zat7zs42rxdx6SewEYS69vxObs2e8m1xMzuGJOgtKjq1lgbuwE6qgTTxbuT2ZIqYSisMLBehSC9KJEmdshKecUMuqsZSkC57njUbXT3b5E1xbGArr'
        b't0gW7YUW+hQkBEHDFk4/GK5SZgX34RktcqGw0CuBk1jjOl4gkF7asPiI62sRaxgJnptfwV5oXEQrf2QjU41POfG41XAFu7ULKVrbJGxyj+JUKjVqgVBYdX5pqt9K93HC'
        b'VkP87B6FqZOarhdo5pUHucEC17Dfzo0eOFsT//Khye3vSF53mxx5yy3CY2584fm3fiab+6LM6ePG8F1Hj37wwQdflj69pJz/yZmgtWfHduXIfE/XnV/3isfPxt67kRj1'
        b'x3x16QZFZU/bi3OqtG/43k/57nzVkhUanx91bjz/ztjfJBS+fOur/pbiIE2E70/eCm+RtYSUF5if1vUFpHRt2f3bZ7VX3mp773d9x8D/aN+czybv3d7UW52pnfnb4+mZ'
        b'pz+avhhf+JNWZWZIvhPqsHIos8JS6JH6uywxs43Djig8x307PMYLNv/u6NyhPIR33Juw2RdLVhOmU37FkqxA6uTPBkQ6CUHYoIxYcppHAYFQg/fVkViqZZRIwv2c2iSw'
        b'ylVrtpr5Y5jl8XgtMtZfgl1zBWmOZE38Np5YnVaRo6QULTCWcXqKJs+T+qyELjHrKqPUPt8h7YJ7blK3qTvNzCGlz14TiWWRWjE1hHYoE4SxC2RpcDNRKxF9vurvSrTE'
        b'MMRZTKvIRfAgZIEYhJwWBHtexa5Syo/ceN7kJpFLWb40m16etpdxokOYMpTdDMgIrR2ik7+WGMkcEiP3wYiF0f6dQ8RSNXVkTrQN6qF3MCcSE+PxFBGcRauMopF6LNNK'
        b'eMqzEtrmYkkUlh5yKLFjBzYP+2bHYGLDnlMhpy1NlQ5+g0Pyjd/gYK46XSv/8u1huLVZxL1viM1TeWjNPaxjDft/OpkZFXjt0hkOvMoYC4vA526F+xx2z275VuR9PpDv'
        b'sEVToc54ffDovVBJEWURdvHnLbFmNzwlQ8LiaCzdgoVR0glh0AznoAkezoNa+qwVNo1zggcUfrYZxtY+kpqYK/C17P1Nop+YFPCUIP6V/vONlZLwRU0L/FP8tvvqUg/H'
        b'6JT/tCAg8ePE+O94vvVKrVLYMm+MwmmmVmH2Igr7oGspQw3v5b6jYEY45vOKTjQUQSF2b3So6vh7ZprZ17XgEl6CarGm41DPyZm3Lx5bzCxJx/vbgwdhZBBCsMGikmeL'
        b'HYrDsCWS13vgAbm2wZrPXrwh2pt0VKN2StObB016nN2kvZgp83KIxDh5yGRlYhli9DRCIjZyU2RjPMlUTBNEU8wVfu3maIysCHUE2qZFDhaofLBZ5HcXNn2LkUmtwt9s'
        b'ZKlkZC3DdHRLdobBbBq0JPGkgMxFw+6mGnVpvPI/wqrslqnTBI+a2g7r7B0auy1m6+adfprQ8LDQyC3boinnXRMTmRAauy7MT7MmlLcnxGyLXhu2WfvNifBoBsQ98t1M'
        b'J8F1nVQuaBKj5MFpgvgsaqlxLvsKmy/7DlxRVFy4YzKihWYXqD1Kr4jTcVB0VIBrShcoDMeL/FFLusX9zOBgMhwGenFwWZiJd+VwgxKzZ4Y/bT0pNcVR/6/cN/8mcc8r'
        b'98lEOvOCznmd66yOuNh4qbGgMc/rypPwpvygc821nUWdMu/Zb9zPbc475JXsnzwmuXPGpoIpc7dgf+5Rr1DyRVOP/1ko0Yxvn/E9rVz0aPcpJ2y1Gwe2ejL7wLteXLv1'
        b'W7DRQf2xMtTuRH1n8NELsBLPD7lDzxXBUjd4ipW8EfrWQVVkXBJ30t5KwdlTCo3QtGmY+o5uHi6UTJgcMm93u4UEqSSu3EbcxPzb8//BStgY72FWMuA2MsneQPDW4Bvu'
        b'5xPDM2xsgybukibDI/mkKXidHBYLSKAbcqGDXBY1Ur5dcRCtgVAseripp+XplI/Xj25WtqIc/07iYFHubzCtD/eOLMo5ujBevcrUHeRJzSiei6U07LgtW083yMMN9yUR'
        b'ooFl6MxmylCSdeSGhhPlDk2XItb9nsvNhtEazNP+WpompmX/Gz2qZFRAUMVY2DH8ov147xsSGejb/C0e1QuuckR5fcEUnsrkrjp9wnx4vCDWLGpcoF90s4+9+ENuHlgh'
        b'fnHiWuIa0ckuPjDSzTr4WGi0HQfJVvKvoI7TBFii3p60TDCc/MdngimeWjaemTzjzc7xuZpx8ldenClNS3/lh8s/OTt51aKJa6Nf+/lvpcu3FYXsTC5XvPlmyS9cq38d'
        b'8ruSzu+/U5uY3v6vf5pU/fbjyR2nTkxZ/dbS33+VXdoRXvM7j8//c3LZB3O2PtIqxUJdTc4KxzrdkE+GTqygcLov2MwAcP8h6PIdiuRjN7IyOJYT2kQrhCUxSsyNP6We'
        b'aBaPyjyhwsF/70/yh0u+ogvPxx7zCA8eAQ3sUKYxjJ+FQNni/SNdeCVlYwRiZNoXzCxAPSVLjnyeiVlwUT4XW/DaUnxqD+D/Ws3Qlft10mhmLxy6JtuhK4wBlqvERSo6'
        b'eFeJcaoDeA2oGdglZBlZVOAAYqNOSNxMG4QzRmX5MDj7zrCaIdsUJ3In1ueWuFYtLhKv4cXdWllMzHqtZL1WGrPeEH9ho8L0JRH9/fGObRf+ecvEOHfrvz951NyT6/lK'
        b'wP8tfnLDPXlDWNzEKu9fp21a41441Xx464Sf7g0uPvn6h15Hv6j4POCNBcvTfvfWn977LDst713MbJv2nciP7gZVf3p465V33o9/pWxS6cemzDkDH3+2s/NX6hD1Wv+z'
        b'2X3fM3xwN2jZ1ep1nxrXz/+HI63uf+mP3hkWHHgyZ1Pphi3vKQNfGtP7w7hYWdBUQ5Lzd/3mxajbejpL/+1e4rzW+O9O/dEP3l7+o+4zZRlJi3a//2bIg+68a+b7JT/9'
        b'RBf4n+9/T+JmLMQ5M66/Mb78B290HsXJ0++UZB771b/JnWOMxe9e/dDvl0tjZ3n0362O/Ny0M2uH5899/vnznGtztcrFT1+NLgg3lfzY1WR9tPzHN/uOD4z54o0FIJv5'
        b'aWHc60feWhr7+bR339wyvyZlY0LEgfbLft878rbaGPXZxR2fnbz+5h8etaRUha29NTH0zUsP3uzdfePN1xYnv3+7aeNtfXzqzn/ZHxPz5wgXv97AyH841/aTgs2vbNZ/'
        b'7BOZ49L2VYxL38/GPOo8V5ToEX1qqdeG5W82H/r19EUTP1qc5TL+64RPXrmxBH5849XY3957wzv1OztmrPlaeq7r89dW/+zw43989R/ePdi9/It/Gr98ynse+6/V/GLV'
        b'f3Re/CJlXlind+tP6/+4RxVotv7l3aof/eKPm7+/4mbLybaPzB0Xgv70+hf7Q0o9x1248GzdwvcCb8vInD1EA7uOteyhT/JyEkGylBJnaE/nxrccHvgMmpZ73FCKTZjX'
        b'xkN09Th8MhIMVi2yh+hYbjbzhwGwNgJLKIYo26f3VwrKfdI5G3bzlBp64eYq343+WBgRFaNYjHcENXRK8ZoWqjkHcqhdH8lAmHpgaYRivZY6dEjJaM9D8d95tql1+/uO'
        b'Qr+RjsLIvMaoF44RqoSEjCxdSkICx4f/w6x2jlQqlQRLNPzMc4JUJZ8sEX9dFFKyYRW//u/7VUknSNivSuIuYxWI6aultAL3iS60Gk/JdG+pZOpYeo2XSozT7ThJUCdN'
        b'SHBAuDH//xKXGGcMwiGbiEGeeFrzwXxHKOT/pwOrnaEEKsgXkV+mKLzCSXCbwr6r1DIDmrYZZL4fyk211LF/8mH/kpUu8JJ7/i8Phjxb7+4n//7rE494qJO1K37grQ0u'
        b'O2+GlKwLT5ofzX73rROzbt44kvha7s5j/6qvWvOLddG/Wt/wfS+vXWnufZ/v/Xr7Lz46+7v07//yi1//iyrJPeAvLtGPVe2/ihkzvzZy1qkLXxg+OrN1/9cHP/x93dnW'
        b'P/xSNb/nrf4b2d8d0xf8k0PfC330w6jPYj9c8GFp11fSGW9rf5o5VTuGO7ZZUI51/D94QBf0xtJ6WBVMDV1SvHuSkl9WB8PbLx5jUUMn2d9ZbI+NZUWt8fhYBo0eeImb'
        b'kPPsBaI4mEeAMi6OCbLYpJnwDGvMLPDWwO05kRHRPtFOglIuxQczVCfk3C9DBVyEK74bFdgZJEgiyfXDLeg1868MlkOL88j4iBgugKeBkQQD5eSFKmQUZnc6QUV6Dl+Q'
        b'bmuaOEIfNTRGKXisk/vgHXhqZnE5VkJ3KmFRqX8GNmFhoM8hm1OfapFDwdy9Imo0Yxs2suQqEkucoAefCnJ/CbT5EBGGSlg1GS8xb1g/GYoc2ZkGV+Rw2/8IpxI8hdjR'
        b'kssUNUUijI2TwRko3DZ9jpn9BxUsg3Zos3fxg/JAMZOTCBrsVeDlnQIWGfnCQqEQSn1j/dhRG2VRJeJG4VMp9sEleHlYojLjvweE/hsvlFh9A4oZMg1mG4qxiE4YwyIb'
        b'Ss9kcgnDAZaijePRDot3XGRzWRQUaJw5iASzBmQZ+swBOTsLGVDwJH9ATrmCeUCeYkimK+UpmQMyk9k4oEg6atabBuRJWVkZAzJDpnlAkUogSm9GXWYajTZkZlvMA7Lk'
        b'dOOALMuYMqBMNWRQFjMgO6jLHpAdM2QPKHSmZINhQJauP0JdiLyLwWTINJl1mcn6ASXPUpL5wa0+22waGH8wK2XZkgSx9ppiSDOYB9SmdEOqOUHPsoeBMZRtpOsMmfqU'
        b'BP2R5AHnhAQT5WHZCQkDSkumhZKKIYQTFzvDyE4ZjSHswr52ZWTfizIyuRnZN8SMDLOMrNhiZN9qMrL80MgCfyN7NMgYzC5Ml4wsXjUyEzOyEoSR/YceI0tFjawWZ1zM'
        b'LuxbVEb2/XQj01MjU3kjMx7jMnZhxTfjgkG8ZNvhMoiXf1zngJe87UuV/SmfgXEJCbbPNgf25dTU4f9NSZOZZdawNn1KjFbFnr9JyUommdAHXUYGwf5Mm+qw8Jjuu5D4'
        b'jWbTYYM5fUCZkZWsyzANuDpmacaVdgE6XET9WyH+y6ZVTEd5CU0ulctUTMci3ZlvkvwXf9H+2g=='
    ))))


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
        b'eJzNfAlUVFe29q1bt4qhmFRQBNQyThSz4DwroiCjIs4KBRRQioA1gPMEWsiMggooowMoigwqKmiyTzpDJ+lO0p10Hpm7O91JJ93pfsn/0m23yb/PuQUUiC/p9b+13o+L'
        b'quKec/fZZ5+9v/3tc275O27YjxR/l+GvfhG+JHNbuFRuiyRZkszncVt4jbReSJY2SHSjkwWNLJfL5vTjtvIaebIsV3JcorHS8LkSCZcsj+VsUlRWj1Nsw1Ysj1Luzkw2'
        b'pmuUmSlKQ5pGGbPPkJaZoVylzTBoktKUWeqkXepUjZ+t7fo0rb6/b7ImRZuh0StTjBlJBm1mhl5pyFQmpWmSdinVGcnKJJ1GbdAoqXS9n22Sh4X+k/B3Av4q6BzS8cXE'
        b'mSQm3iQ1CSaZSW6yMlmbbEy2JoXJzmRvcjA5mpxMo0yjTWNMziYX01jTOJOrabzJzeRu8kiZwOZtfWhCPpfLHZq43+bghFxuI3dwYi4n4Q5PODwx1uJzDmeTqpJGJVka'
        b'k8dfe/wdQ5URmEFjOZVtVLo1fm6dy3PCyjrsk5D+crItZ5yOF+E8dO8g56GTFJJT0RFrST4pjlaR4rC4GF85NyNEII/IdcE4F7uSemKajt1KSKk39iUloZGkZAPeUOi/'
        b'NtQnnBThv0dQFRZBCsJkXDaU2myDq6SLje3OyTk7n6/knDIh4mxWIGdUU4El0EgKSKeN/dpQlFsUFhcKNzxJvs+aSFIea01OkVbSHRqHIwwd0jM0gpRERUTHeWJDvj8q'
        b'uzZ0TZynb2iYjwSuCZwBTrnMQb1NSZJhjubQb5uoH1moFAfzUkjyeVwKHpdCwpaCZ+aXHOZjLT7nUPcbthQ2+Gv71FLcEpeiejyag+OcYhyTfXIMwRy7GD5WytGOyrV7'
        b'7d6fula8OCPZmnPiuIBPjAa7I85x4sWKGTIO35WfuB6JaEzTci1cOh1qcaar8O1obtlfx+yTvL9pju/xrGYunerR4lg1u5VPcOSWJQR+oItw/E68HGLzn5LVHp6T+JhP'
        b'JN9veml0ENfHGf2pUxTBcajAJcGV9fQkBf6hvqQAWtanQ5cnrk2pj1+Y75pICZfhaLOYdMaq/I1j8a6lcJM0wWW4obdDu5PzHJwl53YbqQFS/Q6OI7l6nQyvF3KQryFt'
        b'Rme8nkNujyf1e/Q6K2wo5qBAR/KYLNJpCyY5XNCTO/SvMqpSzWx2D7RoJhon66EEbUUaOLgIl9YZXbBh2hG4hx7TgE3o46SRg9pdm1kLdJHrM1zIaf0eqkApjgO5K8Vx'
        b'muDkduhw0pN2Of5VyUEZ1DzHbpJDJemBm3F6I72pnINCV9LIWkjBEbiMBnmkt6c31XFQlb6VtYyDGnIVWjbqSSfV7hyKU7gZx1F4gKtQqYPjeiiiEi5wUE1M0CqqdwGa'
        b'N0HuTL2C6l2P4txJLrNb5EF+F3Toc9B3yVkOSpTEJN6RT7rGpkGe3pET7zhPHjoz6yzZCu1BEaTTno5/g4M60jGf3WLnC5fcSYuCrcF1GvcNUC3a4DRpIm2A5i/EhZNY'
        b'c7iON7zF9Ql3Jw/T9KSDLuhpDkpl5DabDlqwmzTA0Rmk0ygVjV1BTHvZTeTSzhwoNSjILTpUGy7DxDHiQMfhKBQugR59Di/KK4ght9g963YufM5WT+5Sras4KCd1cJ5Z'
        b'gNTvINcidugdzUtaHT5dVCA/mlyA2/CIdFrTpksc1ITADdZGTpAuO1zIE9hGVbiKKmyBW6IOhXBzJVSuJp0GmThW6SLoFJuuTCHlS6CQdNrJxbsukkdrxaYW0uiTCA+x'
        b'iVqiGQVCxwxRkeow0ryBVJNO0k61b6JuXxdrXlgPUq9IQ4Sjd93koGEudIk2Oq6NjPDDBrOJGqFgAWtYPgPqUvZiA7XqLQ6a0qGNyVpBji6A2iNob7PPlYNJL45SP9kH'
        b'zobhmkvEexqh8oDRlbZc3ApXVpJ7qFsnbbuGRoITcJE1khoNgm87uhK2WoneUmskx5nM5zACodYW19Cs+cVlpJy1JMMlOE4qoxXWtOUOB5fjUSAzew9UkUvkcoSCdFB5'
        b't1ET8jDHOBrbRiWpghYqsmXiMFUBaIZxYvbJx0UsmKogd6jx2qnNa5aKNi8eA7XZHLbQCXdSVy6EAtYEddNSoYyUYptMHKhhLDa5iD52jFSpFusNVL18Dk6SlklMhciU'
        b'JHmmgkIxNfh5KNwkOljzpuAJpElhS0e5x8GV+fuNNL+vQzN2kuOkFQrnkDJUskjGSUmjJBpKl7IOmJYeOK9GvCvMJhVQDAUyTkiT4OjHoc6opFqanCaYGwNFCVBM2mSc'
        b'DRTz4zZDq0rK9FpBjvOkMISU4IpncpmkxMguQx5cIZXh/umocCKXCF17jaOYVezhZjicnCqnGSU5NtmMiVNJ7QQoGpz1wnCjJ+1+Y8Fqcobkw/U50CJTR4IJV7wYIzQY'
        b'mrZEcrP0MkS5MtLEzOpH6qEimDzUs9A4hRMgZ0mZcQY27YOCgH45N0klqWAfZ8F1UinISQnnQYoFG4mt6HXt6Zg+qsk5PemSiOBdgpJPMUFT3XhRDtyBZiooFG6a5ZBH'
        b'SZwH9ApSOB3GlgaaUxKhcs5gOtmQbfShk8qFm6ibWZ0bFuq0ohh0wg7U57Qgh3qoZ06h2zMb7sJFxF4KFbUYlzvgqFFFh2iD5kPkTCi0on0GBAVS1QS4vJnz8JWSbuiG'
        b'R6K79kApPMKO5/Q66kcmukpN1szSax1I3Xi7ARtRWxdDz06FEr22ecMYbo3SSoE5o4atl57c3zEOqgcTIlxyNfrRERp3Q8EOlPKUraGNFNO3a6gZ56uT7SHt80UouQi9'
        b'AWtJzWASXRdnDGT0Cl2xcmByxdJEZFRXRLWgCRHr0k4oRCcIJd1ychvySLMYXKdjQzFqmhD1mRBMC0lQwTx6/ga/qRpLa9HFE9Zx7qRTSm6N3cD0cchZNwq1seXFRatE'
        b'KL9qnEdF1VkHWax98ZDFW0Bu4/o1R1LRrZHyxEhuD7RZw715pFTUqtQGl72UdOuhQBAB8MIiD+YO0OuJkXqG6tK/hkuT0IlwtpVwMgUDr5qbSepkUJIaLgJVDbmMDtlM'
        b'Si3oxfZE5p9KqDswxLNE/6RWX6ZF9zwjJT1j4CzTaS50YkOhi96BzrWaAv8D0sr8iienA0eKlxbm5/bonybBCpPXVTOeqeC+x1YLToN4UWKcSXWrhBYLScXD9GJxc5mc'
        b'4GYdkKHjl8Md0ScafMaEopcOMiGfw6JPnINLhwYAYdC5rjPJs0S/78GVDySlMqgnVftYAB2Yh+k0j9wZJFCZ0G70ZgBD7iASDglp81ypLHu0GbkhWMMl9C4a0wuEnWqt'
        b'BduKxnlSx5f7kvuLUp/SDEW2ipNuZX6PKKsnPfbMauswdd2esw2FWYmZvALvO8/mHzsTHbo+dpC6hZA7bF2mL1hiG9I/yjU6CibSfdRP4KQSGjFOI0mvVaBRJqbIAmgg'
        b'vVjENA4yPfTCE2zmCch48oZgKw0skrvFcw6bunofp4c6a1I01VfMP1Md50y1IIb+qWyBx0MHNEEVRtyZ/qUYHvLmqZ+V6eEuEkO6IPN84FoCua4XM/dFdD1oSxMxqjUc'
        b'1+QqHB1kk0hya4xe2KZOIcUDzs00ppkgWEnOUIgiV+AKF01qrfz0ViKxqKOUp5G0DfI1gxsrEBbb+iJmXRzEliGKi34gcH7wQLaTVME5MTO3TSK1cA6dKEcmLn7x1unG'
        b'adiyYVSYWdK1YallMlziPGZIyYNl+81UFdo2ka61FkwxntQy/N1IqqYOh6ZZNFSEifAIEeqOFDNfA5SJcvKVO8nxTBQjEcl4BTlHTomTPk1ukfLpUD5IOf3jmIuSs3A7'
        b'eFgotgwNxThvbtYeGZKLkxOZH4aOh1MIQ3f1jhKRo17YlcCmjEmhVrDELPpJTDvyIM5DKiVt4YeZqs64OO1+WFoP8lxoXsKWk9xGiG/s16htWOiRzvEYe00IMxWcOOkC'
        b'GVxAPnPFghav2mqchU1ayN060szYFQE67GYtiFy+Em5M53Sk0hoJwzFM53SCLst40oF0fZBNR4vszZf0zM4i95FbMg5QT8Hx9i5x7r0bNz6VJ4OVsgnox7OgXgZ1CUjm'
        b'qHSnzBUaxPxOO7rYl3HmpGGSMYDWJZC3fajzWYIsBeuNSPKCSI0MlzMP7jGVjHh/3tLFFvQevfsY82cEcdI9CD7FA+jArkjRAPY7Z0vWylb7WM1TI6mgSLY4yVOTbVEQ'
        b'jEf2TNORgZQbwlkaQwFM4MVZFtHGeNc6KLaaPAdE2uWmJFe9sXenSJtxntXBcIZlI7il5iwT+NL9/VJo4g6C25jUrM3G2gf1+7MwF3Q6WIkUt2lrgMgBzy8LGR4ZgcxI'
        b'UIv5z520o7eR83ZMGStS7glFCBOdYu7oQEY8fQbbKiJdpDaUnEcyZ5nYzBTAA45jmAaQOpFUV47hV6hJ5x5eDK/SrRki3eomjciQLVF+0PHXIvx4gElK7i+2E4tCcisI'
        b'HrmhGLkIcmWjIoyTqZIxzulY8g6bE0+JyF0Mc5VSRO9WUuhA7pKjlqXZapInyvbfDblBFpXZSlLIGtLG7iCXUPhgaWY/heH3DJexcUcsCrPUKcyb4SQ/72ncQdMIq5ei'
        b'PrfQtlOymWnnISqfsYc7FiXcGugWQbtoGrmWTU5ikzlaTmOYVzKzx5AO5GoiVFzrHwG6mMmSRjOs6Ip/Tkz73dLs/QEoRCbSiDNzkLiytN+IS507EiG5OcgqMbPVI1Gq'
        b'lkHt8rFM43Q3uHwEutB+t80hUzUZUwkFw6AZpP4pP5jVT+uoODe4xs3cKMM67b6GaWdPcmeQVqxt7XnR5vXqMOYVAuJE+dC8RBGhPy/B5UAuJsJq/nJOZG+XjXLyELFv'
        b'sN5FApLHcIGqeGwoMNwYZjIEwOsYOY9kULpR3OhJcCEXcjBndtrLxBK0CXpyRHHlrsuHSOOTzLo5obomunc6ZxTkz5ZAzTLbKH8XJm7suoXT6CJblNy13mIg3oRaC/WG'
        b'wfVRO85DJSV3oxOZ7cdj2X4X7m+2rM6n7zH6Um/JF7C8OrnrmTzOzBiMsqwF/uY6m/SSM7sBK+ZbclHYBehYLGpVthFTwlMezJjlXXIdffielHSM2S/WdjVQbg/3SKHF'
        b'zgDiwiUxuq/A1SUjUkEqbP1KTEePBAfomsAwYrJVHCk8oLCWixX8pe3kppgeLo+yehqu6IyWeqEyN6XkZnQ0M1GUAuvTTigb3IpA2nyRqaKEUwee4mYDHhWGLhDjYzU3'
        b'E+GKeub8FTOgVaEwmNPMGazqLot1dbvbbmGS5X7G9Q1MeQyWmbZgsWuwwo3dMG8sanouRZFNRbVg9bMWcpmVV0etH0I7LTxyKVwVce8R6bEVOUirZAU0Qosim4q/zsG5'
        b'bHTwILGma0fHGNEnoXPLGNKA0J23kzRt4XS7sHyC61tFQL7h6SPZO7gBAyVJYilNN2ybhwGDw3Zx0WSjzbVTK5YCz6WLpTRpPLwYHlns10DTGoYI3lkpGrj/VFU+WOuJ'
        b'lSuckRmgWi7WPZUTwkjjTIstHriF9QAD7zIoJFenw1WLPR64TR6x2chnBcH57QoHuuw9HDQnQCmLVyggx8aNXHYNaDCLdOOMGpBlSNzFIC8gFyjA9i8O61kePxQlZXtm'
        b'S2KsreaQ3FXMv9zg7KqhZWI81rm4pK2yRFyHSC5wnAzT6J00kajdVND4s+D35uVn+xX3ySNc/w5BIBXOYkTmkZObRpoGZbOkXINxVCBYr0sWKULr4rgRIIVG3DasMzwW'
        b'SrGggRuifR4YVj0NGkNQeznWkjPJGWSKcCdNZc3MPTfeCWHrqsKBpr6HHFwzKtgarUePPY42P6cg7eYIbCA9GIHUUTYttQolRdhCb+pGUCWniRhU5MZ40nNIp7DhxeW7'
        b'ug2KRXfoIV0uWGjeVBjNu9fnppAaJm0bxnY+VMO5wQ08TQ5r8SQ9KThoqUJvjtFaUmMQXeg2aYNL0JONnsRQrxdRJoCUGWfTsUpwSoXYcoacXAD55i08uGEOT8hnm34C'
        b'dK6Hwjhu43Y5qYtJVQnG8ZRIotyrpDBiDSmSclLyEG6vwAxgT7rFXatzUCILJwURco7fIdk6zd/dyPYLlziTnnBSghTogT8p9lbRkyo7J6kL5ooOkZ83kwq5d5RvqMAJ'
        b'y+YgvqIqN/auSqJnQv0/OA12ssROlVZy7BCLHl7Rgyx6gCU12aTYmI+uhHwhlzsk229zUGBHVzJ2XCUclsVafM7hbPJU0k//imthq7T4CaZnn3qlOoMdeipTMnXKbHW6'
        b'Nllr2Oc3pOOQP8LEI1evXZkZhkx2fOrVf+Cq1KK0bLU2XZ2YrvFhAldrdLvNA+jpfUNEJaozdimTMpM17ACWSmXy9Mbd/Qe76qSkTGOGQZlh3J2o0SnVOnMXTbJSrR8i'
        b'K0eTnu5nO+TSgiy1Tr1bqcVhFijXp4lnu/TQN3FAit9INyRqkxbQaaZqszUZPuJdVMEVYcFDNNBmPDUj+pOEhtHsNdApaNRJacpM7KQbcSA2N90+y8EM/WqiKX/6OAZ6'
        b'zG2W5qeMNOoNdI7U7rHRvkEz58xRLo+ICV2uDBxBSLJmRN30miw1U8yLfvJSatA1jGqDhp2aJySs1xk1CQlD9H1atll/0eLMtcxzUcZqM1LTNcoQoy5TGaPet1uTYdAr'
        b'l+s06mG66DQGoy5Dv2BgRGVmxoCT+uDVVep0PbtMjZyj1Q+bzFMn59bc8OPaUVGrxITcYCfRY5ooGdj/8oEKdhR7PdKVC+DO29glJCwqWKPhRITrmIEwVkjroChuM7cZ'
        b'c3Ix6/38XlvOmctyd3BKsHvHaZp4mtsX78h5cH+dLQ1IiAhc5s0xFEkgtVCn37d5YBMnUqNyFPdRmqDjgD7NbXB75xbcFLU0TYce/Q5ya+C8cB8pYS2bMcnU6JH0DZwX'
        b'biZdDHTGYlFSTzon7xk8MLwIVSJnaFu7WDH78MCBIckLFmd3jfRoFAeds6Ri5XsOrtmI4+eBaYOCFI7fY66RaoKQ/dBbNrIt+0LSvbP/hHHvApFOIKVCrrxrjl4uliyn'
        b'Sbs3Gz1qDJTrtR6DR48R/uy6knQvJZ1TZg4cO45XiIM3Qk+gYpZy8NSR1CawOzZAeYRih5QZ5Q67foQpNRm6sbacYWATrMHq0pm0s4bsZFKiDyZ3c6zErbrS3eS0aPp6'
        b'HRToDeTSwH7YXOhUScXxyzDOMKfcGGibYj7EdZmyjnTKNg8M40CqxUKmGzrIPT1SutqBkcbCfXGk6zNUeiRP1wf3CzemqnixrTsFR+oJHGwKgl6xpQhq5+nnzrE4Yz6u'
        b'Zz42dSx94GCerY0yIf03wfvNbnpuKjQHIQHMC0BJcIZL3L1E++nL1YIekwOXOuHy7Dfbo6Qz7eQJC6P+4tll/UKMMfFTyecvveK9zFTQEDGxvtKrPLT+el9Lo25j9qXC'
        b'F3MT3Rt8zv2y/YdtU8++Mk96avH6eauOHfT/5GOlKvqd8uBj0T9b9OG20D/lvliwZcb0ktmtnh+//sLjP956WNTXXvSh7/EbM75zdFrs3+X42S/0zZ8fjPrg4EkbjzDP'
        b'zLxFpYuuv9O6evKSfS//K2HCl7u+O/a483HLY3jy8ycRh1qWrD9izHzjhNfZudHp+hlT57R98zjmM2X5sdXZVm0e33/0ycdf7Rj960cf5L4pPE7+4WGub0XmbyqOfBvi'
        b'Fvt1pN2S0pfuuO/p+NA12/ONsd+98sfrAbkvvOZ/LWN705polZWBBkgEaYY2b1/PUF8+NISTQzXvS8q3GCZS+x0Lg/ve0JblF+bjpfIjpT7kFMe5KoUd5BTkGdyxy9Jp'
        b'pDE82hdORTNCoFjLw1FyHJfcFMukk4fuW+iTN16+fpK5CSj+OB+UKDNQiklaoDEDq78SUjoOjnuTUzni4y/Zvl6kwJ/n/KBXRrq8SKdhPKvw48lRUhjpE0ZPbIq1yJF5'
        b'B7hLmg3PsZWG0/AoHAqfE2UAChXpiwvJk5Lu+UYV38d7qqiPciob9vaTXyh0PnZZlKLL3K/JUKaIz1n50cy6pM+W4Xw8/YN20ydSrD0iqASJtYT+Okh4yViJXCL84MDL'
        b'JfwPtryA1+1Ymy3tw/Pf20ppX9rW/y724I86s770qoNEYP9sJR68nYSehIl6qeR9Ah28T4qJu8/KnAb7BJq3+qzi43XGjPj4PkV8fFK6Rp1hzIqPV8n/++mqBB0lYDr6'
        b'wI2OhpaOPvmlo8SMDXuWTpMuLXfM40s5z+Pk6KsgkX9PX41T6HLUxZCG0VAbPvJqkFK4gajCDplNB8eGYxMpjCIl0WFYkNfKOIcs6Ty4rDZSB4tDyGkPj+DgOnagvFLC'
        b'Kbbw5OYYclSsYG/7uw6QUReo8IdHoUlSi8RH52TVn/gWcAOPRQkpgplHSvOlyCMF5JFSxiMFxh2lh4VYi8/II9OQR74nGc4j2ZNzFkRSl7lbqe6nfkNJ3lBCN4ywrf9v'
        b'eKVOs8eo1YlsIkujQ265W6Q9/Y/zDU380f18ABXxWocjandrQnS6TJ0XE6bGluSR6SLVl6orUsbhkxiRK5knJd4xfIYjDUEJ5qp0dapSK9LcpEydTqPPysxIRl7EeKY+'
        b'LdOYnkx5k0iBGOE1k9yRGVKIlk55kJAh+VYrA30NxiwkWmbaxayGfNGT9vChA6l+hC/JnuJLsigjfYyTnCUPY4c/KehkR58VPBXhtcYHrq0XHxukF6IjwiIl6L9wSjEf'
        b'Hrqs136xrkyiX4xi5n4m/zLBL8VbHapOT0lP/Cphx/PvvfDeC2XQVTb/ZMvZhrPtuS2hXScbTs4sVp1vODn5/LEgqcfvOdXzioJ111Q8Q76c9eSywgvjgpwiRZFGETvJ'
        b'vRXcJOgUSBvpDTXQJzizE+3CSc9yvzUIoFDcH45u0CVkQDspV/FDAOBZKMhQoE8hPi06CHoOIuglW0tGS0Tg0zkOAJSsz7rfq/qszP4hIowdfaFPcw4ZXaqjj4HonOiL'
        b'zQDyUHm/GUSe0ddGQB4lXZkHpGfZ9IjwkSZKOqHJuBA7LYcOD1oZm8vi9ZxYGLeQSmR4HVAE9T7S7eGzoGQP3IAr0GvLJZLT9uQiqRGJFekiTXMV2Q5I9ZCFZqwi1yMd'
        b'WYMijtQpsvfQ6/nIFq3JBclSRoXGT7TVkzuOgQI9OEdEOysZS65DsyjtTtQ2fSAaS5KJ1HMK3IVKL3FT86YDnFBkZ8tR3AkOrkIDqY4n9xE5WWa9SU+cBqDPndT5R0G5'
        b'0Q2b7JaRawi962VD6/AScoHd6QOFcNYb4VTC8VAiIYXy4CgwPQWaA9XCCgqaUgab4nOkvMk6xXoAPIWfBJ6pCJ5PnlWEs6gfWoI/EzoozNDuP17KPqPCpDf/rxeYSelM'
        b'Lb3G8HRJOUxBapfMpCQjomRG0tOK9heVITHLlcGY5HUURVditkgyZOqwTMwyJqZr9WkoKHEf62lG9WAsO3Xq9KfkrcBg9bPQTU0XxcieNveKDV7v5YNvK1fSt+DodTPx'
        b'HdXzWhG4gjUEB3v5PCXRYk5YsGaOWBrTSTI7Z4kFMUpNpoC+L2uYAenPT0qVAxIzs57OkPTnp2XJIYv3P1qRS7iRKnJHrMhpbkCwuuM90sPo5gRDuo88K8fUS1hJ9Mry'
        b'8VyA6xc8l5DgUeDmJNbi7tFjuKnr/4SfEjwMhzZy7Jm7HGTWx2g5z61bj9V8yDzzI8prDVC4BXohH/IxIY6R2EDHBibl8SGs6CMeSLmAhPQnaekI4EaK1z4O5D7dxA9d'
        b'N5ObSdpEsIQGrPOCaP1VDLWBXCCpJQ1MSCoCvXLqPCsuK8EnJooJoceQvnK4Q4XsI4VUSgkcY5cT4SqpYidFUBkWw8XEig+a5++25Zydr3CcU4JPICai9drYjwME/U1s'
        b'+v13DtNKeh0gwC7vl9rqN+H5n7/ibvjdhPsbfpt69+cxpya3FCy7FTO56m7oxxWXKs99fXDJl3k9KTuVzgGfrk7cNq0v80Di7LdNtRsMMSvG9GIi+PXnnS/Xlv3heEVP'
        b'8IlPA2cmrv7s2rjjY8f8p82Yf+z8vjBhXd+klEpF8Yubr27zfXG/1S/GOZyN7Ll2zi+9qdPtk9Lywlc+43JqF3/W172188m17etbjOfuzdnXo43Z9sPH8wMNB6aorFm9'
        b'tO0AuceKsT3evFiMYfnaZKCHwg7ZpF4Bl/YNT/bmTG8/3jAVe205RE5QbIdTSanRtDDzxz6+tH+4FZqzXh622YUxAlKMaaBDEY419YNs1YAwFzAJ1qRikoEanZyWLgrP'
        b'gKJoX0wV2ZLlK3ezWgzukHvkBi3r/HGEc1CBqh7mvZbIDXRbOhKds8FcqUEzVt2sVJu21ED5PtyDisXhpDh8oJx0tILOAGmqL8lTSUQGYP1vVWYiJ7ER6zDMEIyRBIiM'
        b'5IjIRugrjyWUnUQswWgxRYus5/Dd1fyLnGXMIGcZLIH6pIjVFlTlx6onqUX15DxAX6jovwzSF7czz6AvUA3d8oGqCWtqx12Y3kcRkxRZSSmcV0nYBn0ImOIt9ufJgxgJ'
        b'1JBiUv3UF0IGKp85HKt8+BR+4Isfkp/0xY88lfTxL4ag2DoRBZ9B3lMY92b51nID/H+72nkmDPdbaigMy0WiHwVduuEgTDq5n0D0L64Qd81uQeF681OFkLcMmeYMqGEn'
        b'bGOhe3N4tC8piCRFbmGxJD+CHx0CLXACA74KP6i4GCcruHNkgtZBtUuqp7y16MMnXyb4WNQLm57vLnvhk4YzktCgywG+yT5j/dRRavlrAX4JXyRsesX19eerHLiYQ3Z/'
        b'rj+tkon7JJU6cmt4uQDFOf0g4poo7trcPQzlFIZ2TPbth6FaRxbAcxeQm97D9oPgpLWwg1yZIW4aHZ0E5ymsDMGUeFvBGs7CCbZptAHBo1bcNXJHLDFvHJGSCHJDjD9+'
        b'xBi3StUYBiLciUU4xvhka/NWiq1EN7b/hhapuHUxYonRIhEbWWTSW1wxavSuLDK5Yw6fjxCbVOuFi6EuPBpq4JLldhfGabniR8KON3H/dtghX358bYjXxmalaw36gdgS'
        b'Dx4wgJT0aopOncoOEobFWX+sqpWzRqyGh3T2DI6Oi1q/brOPMjg0JDg8Ni4Sy+TlUeHxwdErQ3yUy4NZe3xUXOSKkHWq/752HimkWMb+ZpUV56PHDKRMSJfmWHHio9MX'
        b'JdBFvyLnTb9mdypibai42aOSxWP5Qk6roMUWqvbhbxic2sfBRbkt5GtJJdtt8o/1trwVIwmBEaqypNxE0ixAIymM1d4suCBlX4r7V06oy6vto446xSqdQl74QRk4e0qH'
        b'59Z63likXH5x/oN5C1x+tZ28838SkzW1Zevjkhf8xx9yPfzc5kx9NfetFuf/0kT86+on7bveMRw52Tuq/o1IlcDiBYvGhn0sbW+aa46XFaSFpVlHcp4UPRUOGApVgrU/'
        b'nDGwQq8w5VB/wsxdJebLhZDLsimc2vRcOMvhnlAzRs7ZuPLQsIlUDqmZR44XW6w19BZlurM5ZKxn0j1Fa7anSN91bgP3jRsuzXUgUGgnzyGB8t4IgcIQoCp5Fhzb5x3q'
        b'4xU1WIKPhQeCyxjoxBRGkQi6oGeyJ9bULI1hNV7qDwViVLkdEdIcyd1nB5V5F499tXFgF++nBhbdxds+fBfPMqWx7a4M9W5W8oyQyWjBQ8/usjR4ATPe0NwSJoZXutpg'
        b'wPolSY1paahQluDUyeJG4VOV2xBZA1XcjxVxYtH2/2uGlYwIB9ZRrM6JPAhtGL33ljyz0nlGhiVd5CQDlKx0rHM4LEVWHvAYPXO/+CzwQXICWvuf5idN5CEUQMEe8ZGg'
        b'AlJv0595n5F3t0E9JqZjLmyA75dasS+z/jVYZ1fvJ3BaU7mdoI+jM1rlb5GQX9yDKflPCWkpEeqfp/iM/iph2/PvvXCrbOb5hly15FcrTkY5vXEBesraN93Mm3ZC1lo7'
        b'vrU27nTDWUlz7W15a23QBO7Mn13cVp1XyQ0U1aCaNJLyYbk61XeA75PCRAN9mAZM80i9yPij48NYUmX76aQEQSdSxs2Nkh+GNjgtJvb2haSLAdVmuGJGqnUbWN5G1n4c'
        b'TObUvniCxWEP5JH7rMvELaSjH8rIMTuLgoF+c9DAHm4rhUvTw4dpAWf8UJFJcFrAeL9KWvqJ/o9tNNqxhI+uTQOHQdjY/qwfYo1sHrM+TzM//aTz6L9XJe1TUMyLz9RR'
        b'tmDBAUYcD5WZMAByVMgCS5Ab/dIIIEfxK00232KaKav7zS3OEiqgWiWNilqlkqxS8VGrtGV/e8TrQ1A933uX4t62ih2z3FX+yYe94VMMo14s6G1oTFwd8rOPQn7Gv/sb'
        b'ZaOnk/tHm0O//cubntXtTdPTvvp+9cfvJ7terNn3h4f3D1TZyazcPkicW1ZW9uGqI70/OMR5u7ovuPnKywFPLmyVZD/+R7frl4oNNnk7BXjjcMmhD1fFB2977nRZbkfk'
        b'txviVl7666S7gTdjKsoOz1n6pWyBrLHp7aC1RaMrGtNfvBVybtl8r7dHV7quvh5Qu6HpZNQy34v5YYbAK2+2nF/1ZcDFXzwfsUDR+YXH65e/Cajze37FltIQw8yzb8p9'
        b'IsNrOyO+3lqy6j7v/YVX65Vd/1rwbuKE3bD/vsRdGzTnrTfu35f5GrzvvPXn95bnJI778MY/v0vw/9D0RFv1TfSCo7lFjg2VE18atd9597euJb8aMy/s/beWR39RU/fu'
        b'xwdWbfzlbz0Wt2VKt9XPNLxd+HnjuTcj/X+35tNLE7dpDtr3djk+mVXy5bfyjLe3dkdaZZm2PP7w3Xce7P/d4g+uOgaEjgl927R35YQn7997/F+1S2vONP/MaeLvbNbt'
        b'LUh1femb8qyo/T+PGz/Fe8vK1dsfdFy+4bM2v6nI/v2u9S912b32utdW+9c+WtVza/3tW5Vbz9ps8vLernl1+gtrerf+6eSHuicry6Kq/v5ZnscXnjP+VDEvxSf/3N7K'
        b'or//MGNhwLvuL3xZcezjr4pecv7ok90NUz7/+uUHrd++uLT365nHHf+eH/3B2U8/mLQ6qyN/hvPCz17XzKyu+y75sG1dbMetfyp0r976aMLjtiub/lmQ+Y/qVOedH3+j'
        b'/2DXixH/ev6XkO7aGLfy9BHJ8edHxcKrCBFsa+UW1MSnBWEKlXCSefTZySJ3gxIblsAF0okQVvgU8cDavoBcYfsJ5PbYwxbw4hI+ZDsBygLEc9cKcg4uQi+pJ4VIUIp9'
        b'5Zx8Bz9lXiarBsg9b7jqvYY0rvMl+WERUTJOAe08+n8tqWUdRkOPK9azi/1JKfYgRWG0RxtPrkHHhn/zHFbl8O8d2z5TjkxHs9GILwx2rOPj0zPVyfHxDHKyEA74KTw/'
        b'S6Kkmwk/yHlkT7y1lLflJYgMT3gremZLz3EFKf9EEPh/CTL+n4KcfyxY8f8QrPm/Czb8d4It/1+Cgv8/gh3/rWDPfyM48P8pOPJ/E5z4vwqjhK+F0fxfhDH8nwVn/ivB'
        b'hf9SGMv/SRjHfyG48p8L4/k/Cm78HwR3/jPBg/+9MIH/nTCR/60wif9UUPKfCJP5j4Xn5B8JU/gPhan8B8I0/n1hOt8nzOD/Q/Dk3xNU/G8EL/5dwZt/R/Dhfy348r8S'
        b'/Pi3BX/+LSGAf1OYyf9SCOR/IQTJ3xBm8a8Ls/nXhDn8z4W5/KvCPP4VYT7/srCAf0lYyP9MWMS/KCzmibCEB2Ep/4KwjH9eWM4/ElbwD4VgvldYKfTwIdQyg/+su5yi'
        b'nCROEno8xEsdJB4SfqmdxFliO4bnXelfnqzFgb06WUvcJLqJFmDOx8dbYLj9//v6S3STBgCfDkSzLSPH0z8eAexpqEAnVNtCIZSSUnIKSqA+OgJOQakV5zBeOoG0wkWt'
        b'8wJHXn8eu34Nr/3hVd/CSFsIcM7742Vt3+Nc2biCz20WnVydNdnvxOqNbxfL1vZdDHjDt7qmOv/1lD/809XlZxOk+yPerlLmfhuo2Zk4l498d39T92eZ3239xWuy3bvf'
        b'cmlrUoZ8+qvrv/bJ/6Qg+58vesa6/Nb7b37Ri05X9R2psVoU9Zbvt3+0TukybFu7Sf+GvX3OB9+86fOO9m+qxasurJ0dfznY88+Tfq+yZ6V3Ws5+9h+hRMvn4VzonqAC'
        b'OnjSHEbOGWga3GFDeig3aqePY9yNjo7G+n8U6ZFCA+l0ZD00wkrREuHJYELggGJmiNHSiaTJ0cD2PB4e9A0Pi/SKtOLkApKKJt56nLsIWPcCIc97jYzbC1WScI6cTyQ9'
        b'BvaMcu14OD58owVK/CkmIaqRUikHjXGrod0KSpGpNbHNDChYhnMQb0KVTg/cKOfGrRS8ohHn2J5HmZ8N6SRFiD/+XnsoyJFL0ItA52YU4CSphMus0CLNUCGNt6WVZDgp'
        b'tOIEXwncCIAbjIwlZZOzLN33awQ9UEe1cocaAa7gldPi9ma9O4ovVGHPZBl1lmiEZse10jgwKZigZQFQJrYjwcIJ+sEdsWyVcEpyW8bBSYm4i9IbtMI72oeCNeQznXCl'
        b'yEOe3EUoPjqk+JvwPwOL/4MvKumzcFWboTWYcZVyV2t7W/H5FimP73bsORf+e2vB1ryhM1XKyJ6/TjmAB5P6pOmajD6Bngz1ydiWRp+AtZGhT0jWJuEr1mUZfVK9Qdcn'
        b'S9xn0Oj7hMTMzPQ+qTbD0CdLQWDHN506IxXv1mZkGQ190qQ0XZ80U5fcJ0/RpmPV1ifdrc7qk+7XZvXJ1PokrbZPmqbZi11QvK1Wr83QG9QZSZo+OavKktiptibLoO8b'
        b'tTszef7ceHErOlmbqjX0KfRp2hRDvIZWS332WF2lqbUZmuR4zd6kPpv4eD3WnVnx8X1yY4YRi6hBnBMnO0FHNyF1dIdER89EdHTjUEctp6PfSNBRxq2j8aOjX9jV0W86'
        b'6ugXaHT0oXwd3XvSUfjS0YMBHf0yrm4+faHPh+voV6909LuBOvp/H+loZaSjhbWOPnSvo76qo9GjoxuPOlqp6QIHUJMuh20/aq78+9OoyXo8tu5/VqrPKT7e/NmcWh+7'
        b'pQz9/6qUGZkGJW3TJEeprOmjS8mZSWgZ/KBOT8cUoDS7EK0F8LotLoLOoM/RGtL65OmZSep0fZ+dZW2qW9pvRosX0Q8Xif8p1hJamOrpOYfACXJr5mvO4TwrKP4viX9w'
        b'jg=='
    ))))

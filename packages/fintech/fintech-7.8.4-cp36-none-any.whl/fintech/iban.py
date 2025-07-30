
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
        b'eJzNfAlclOe19zsry7C5ISrquDPIJrhE44YosoNrRKMwwCCjrPPOuMUVl2FHARdQcAWRVUBRI2p6Tpo0t0nbm7Y3vdz2tmlv29QmuU3aprn5unzned6ZYVDS5H5ff797'
        b'8TfD8L7Pcp7znPM//3Oed/yF4PQjp9dKeolL6S1L2CrsFLbKsmRZ8hPCVrlBsUuZpTguK5iepTSojgu71WLINrlBnaU6LiuWGVwM8uMymZCl3iC4Zetcvsh2j10VmaTN'
        b'K8iy5Bq0Bdlac45Bm7LfnFOQr4025psNmTnaQn3mbv1OQ4i7+8Yco2hvm2XINuYbRG22JT/TbCzIF7XmAm1mjiFzt1afn6XNNBn0ZoOWjS6GuGf622SfSq/J9NIw+bPo'
        b'zSpYZVa5VWFVWlVWtdXF6mp1s7pbNVYPq6fVy+pt9bGOso62jrGOtY6z+lrHW/2sE6wTrZOs/tmT+ZpdD00uEY4Lh6YcUB+cfFzYIBycclyQCYcnH56yhbRD68zRKZIy'
        b'nZU3jl5jmABKrsANgs49KdeVPteFKAR27bWYvKCBdfmCZTb9gc0u0InlWIptWJacsA5LsDJZh5Wxm1KC1cKcNUp8Mh/KLQuoKVRpZ1PLKqyei6XJWBWTiFWbqX156LqY'
        b'oHiswIrYhHw8g2WxKmEPVLu9TE3b+MxTvdWChyD4CN6Fuf2G5YJlO13MgHOzsc/Nc10MDVoRuykGOgOwJCguEc9scMXSmE009PC5AmISsCopIXlTAN0oCSUh18XEYR22'
        b'bAoIjokNkkGbUjBD6biFK1IzZTaNKOjlZddI9FdsSbaXTemyEjkpXU5Kl3Gly7nSZYflIyndjV4bnlN6vaT0ZYFqYUsoGYU2PWG17xyBX/zPfLnwvTlMrHSPqCULpIu/'
        b'3uEqvLZsOl1L94iRGaSLnyQqhZJXfMgl0hO+L3MRct3p4vQ4P+UfRufsdRPen/OpvH/emxmvCrlMij9PuSC77SJoj75UFP5j0+ai/5IuP/b71LvOWxbwuy2fyf7q91HY'
        b'YmFQsISyzS+DVgVpn3YwIADLQmOC6cqtjQG0BzfgOlYHhcQGxyXKhHxvt2VwIdvCTMsXTheKcBrqPUjFeEGAc3gzxeLHRnsVj8J9EevAalLRn+UClOB1uG4ZRTdn7npZ'
        b'3OhicqHrlQKUrSmwMHWpI/GxGDYZ+1n30wJUbJ1qGc9MrScT7olYiVVQRRrFqwI0TsdbXAA8cRDbxINYC1Vk7nhNgKakmRZfulMILdgvQl92EZu+mqaBCizjnYKwf7kY'
        b'SUvtUdOtswKc3kRWze7IyPBrRGzea2GdzghQvgBf5SKHiy+LOws8WYfLAtTHp0vTXxGxRASyyz4m2XkaKmY/X0zMGkGMfxEqWKNLAjRA/UR+fQeeXS2+iBUaJu4VGsm4'
        b'jY+09kiWSBL37CUbxXPkXtCF9/lCoAqvYbkoBHkLUpcLOIDHpOlv7MOL2Lcn0JPN3inA5XystYylO9Hj4Jpm5Vau+nbqAla4yW94hmEzlIdgNe2YzFWALujaLY3V+wp0'
        b'iRGTsZdtZY0A1RPwBu+CLdMPYB8elVsUkorrNufxjcHL0JGgIZVdxttsom7SPt7Zw/U1y3eSuCp0r1waq2yeSprkYjReEJVQiveYxPUCnDmyjE9yIAJ7RO+N3rZdbIBj'
        b'2MknmYX3sZmmvwWnXNnNGwJclEEVH26LGY9j3w4sdmXT36Tp4Voqv5MQBlbsg0eTzSppnmolHOPqzMbz2IN9UwQPtdSnEWrhLN+bPHxMIJSn4MbcSqOlF3JbhgZsYn2w'
        b'czL2MLmvk6EvJ/n49vRjF9zCvvkqN9atS4Cry7GXi74EL42mXi1Y5mZTzzWowQdcwPlksh3YtxZPuzGt3hbgelgkHzA2C45SrztQa7FZ25kItEoK78BirKZ13V3hKZN6'
        b'XVsOlZLDlcPZZdSvDRuxj91sI0VheaR08wK2IylkVwH2uUim0sRskqs+OGCmBm6m422b/I1H4J60W4+gcrkGK1Jd2Z1+AZqxeKLkko+C8YSGpmzBXjbeXRIEn0iYAGX7'
        b'fDVwFE7sUUkz1eMDka8M703FUg2cHov9TIs9NBXWb5FudezBfs1Yf+xna+4jS4ZXsYPfmjM2XYP1UIv9Kmmmq9gNHZbRdGs31AeI813MTLwSAU5Nmst7TJsAlzRQB5UM'
        b'gJnaL2AN9WBbvClpogYqoNSdTfNAgJawJZZJLE7K4TyUL8TTcBcqVAL0woACr8mSoXOJxV+yGrgI5XsIzyqhjBqcwFPKHBkci8BSi5YajBI1ttvh+Jhc1jaQG1TKxzOJ'
        b'dQrJl26OI3supy0vwGO76O0hlnB/gaaXk+KVLBBa4+mt0syvRsKdSfEkahZ0LhOy5kIfD9PQvxB6sBZLoH0hmd4NUaVPhEq8sSsKrm9NFOaLKjibHmkJ4HpdAHX2pl14'
        b'lgIk+zgf2vGsUphl8cdKpZs/XrTMZeN2YfMrUmPoh1bWOga67I3J8C77wyOlggzspEXHBm8VCdRtg3c6Dd7B2sdDuT/WKNVQnsVFWYpPtmBtDHQwme1tw9k0NPYDbPAP'
        b'VuD9OLhmCWSi1MPt6Q65VfpgrKMlwsAujZasrnXzGCFO66Ihf2jnkiceihm2yE0zpD+6sZL9amNzBJtURRPgJI91azxpF+yyVCoyEvEcPuTjU6RrIE1COSkyBu+r8W4m'
        b'eexMJtLtNBiwd9qDV+zqUa4XJmGfAm8HQYllMWtYTLHqlJMeK5/VT6u3TyIbpiNRnZEoFEG3KzywUGwM5qCKT9azabocelIQapTi2TCyylPZZFcNwjy8rIKqeZu4Yg8K'
        b'64ZtgrRnfM1wCU77Q60CB5JohkCOBDRA40gWcYt1WAAX/NGqdIE6nSWMNa+LxltDrSudJ4GTeMpuHPNfUdGW1e23hLNOpcQfhuzTPgW1pP6z4DzTAOsUjtUquIIDhOZc'
        b'tLsz4fFw87Pri9vIdSZbp9LVRWeZR81D8Rg59rBZGihSSL07JFG5IQaTw1JMXyap9/pKvGPv1cZ7HVcQxO7Hs3AKTmnhGtlWIj5yCZ+DDZYQ6mGGFrbvtnm4q5Gd4PGt'
        b'0L0pYKEkmwiXXbGCbOc6Ny9qfxaP2fu0s1mgL2mYSdokO6cSZZ589Uq8ObSNDoeOWof9WgoVzOKTscklBK2LJbb2cBU+GjJhmuRhnm2qIQUqhRB4qNoF3WmWWdRnP54/'
        b'YOvS9iwUZGzwn6PAh4uzLXNYJIyGB86+KplUJ9+Gs7MmYb8Ce3yhU9JoV8ieZyzE3meDyWEfRSq4sJAchBks3MHSLc4mzj7ZkIC07a9QEMI3EP1hokDp5Dj78N3P2URX'
        b'gD9eV7rEZVkiqG3qku0jSUJXru+hv5TQ65EYuRo6ZwsmPOuKp7F4O3ftQzOw1QlspB2O0qqEuUnz4YoKLuPFZG5zRBXavZy17uRCOrhld7sIvKgin6UYKPVqIXhpnlk4'
        b'ZKyVQ9bHrihIMM9dC2TrVC4vYD9e4ZgWBa+a4jlKUDvJLNYsHI7066HSZZoPXpbQuJdypHPDUI03le+N4mgWAXcJM6BD5GpVYuPBZ3c4XJI+BzsnYQ/bg4ejLJSCCC+b'
        b'Cxza2Q+9TsDnD8VkNHkhUqwpDyPm4uyQTvtasNEfrArKChrdLdNYwuemdEx/29/eWM6w9B4ZV2awNOT5IkLT5wyxi+/9xcmT8DYTs8uFN96NTww2q2qzt4U70vSbsY6Z'
        b'1R2iR33caqfMmD4SCJLZGIIdIWMeNqig6aCK4wA2rsXuYX0kYQjfXWVDXV5SwWns9bUEsY1vJak7h3s1s6woPIFX7G6dkuCyeCze4V49NsVtuHU5sPYUXnYsJgKeqKAa'
        b'i5dK1lW2df+wTvJMtvEXoI9N5UOz3F84CkoWyODiSvckvKTk+6/Pnv5cMLY5FZzFAX+dAu8VEAXlWGPFgWnDNpZIc40TptvhzKIqxHP7pJ2reYXFwGd3joPBKN9J+ECB'
        b'vcQZ27iesDUTb4+I/Lw9lECxPz5RehEJa5IYUA82hD1vvlyKtbmTsEuBXYc1HFcLiAheeg6+aQtuwlnHFgS5LAoJ5F6kzqM5ncODsxUl4R1uxU/g4SweHrdlYNXzul+M'
        b'DWwK6NtKRODELry+VTDtphAfsVpa7SM8vW5ETjZtrmq0Lb53UGTMIXbDZskilnVtWIh38RtOLiSCA7UqM9wkQsmwcDPchEcjx/lKWs8JJyO/SggHpTDAzTw+n1EjuwIk'
        b'iFtEaOzkI6qiBbIUV5eFabbA/fLuITrqYCDQoSLm8CCDtJAohI9XUfbd7c5NLxxfJet1Do42HfPtO7zJH3qVyi17+UYvX7R2pDXwSDQa+v2xTOm6P1UqXlH8f2kEm+Ym'
        b'5BHg/6ICH00slFymBPpkzxMU7suUdzx00k2tCi4V7tIlSKnNEyhdL+7Au46MYxNW87xCvhJuiquxjqebpQJYZ0/lqchCyuPuiNi0H+/IpKpGFVYUSKnANeg+LOIFnaN2'
        b'Eu7Fb6SkHBHXUMJewdLdJsbhGpbY6hYPoFPENjhtYomNlbIQvyP8TmgOPhTJ4a87ai3QvkHK1B7ChXCRuFmZo9wCV+CWlBV24H2oEGkzjmMv+7tKgHK4HslzqyN7wSrO'
        b'8XCXS8Kd3bGCzxTrByfFKdANZUopOb30IqVW7E6gZjMtlIDKUb+BVgtXDnZrfUU8qfNiYzXQQqOL+EJTTStEvDJuqKqDN8fwG9PT55Nipg3VdOBEBB9phStcFjd6OUo6'
        b'eNdDSh9vQONiMXneUEWHwsZJSQGXVLQQOId3scdFqgXUGaCGizw1LEgkuzrqqPbQiNel9BzOwjUxDlocFR88uY/LFpc6SmTNhio+B16RjOP45hkiA3YpxW6kdW4VpBLB'
        b'q6vJOohennRUfXR4W0qxq+VIaSqcd1RKtoGtstUaDmdED6zdq5KWVImlkn34uWKVqIfbQzWUceHSPHcyKLzPwya8J5PKTnXQLml0DRwTxHw87aiv4N390jQ9lFlXi8nT'
        b'vGVSceVStE1x2OZN8a5vLtQ66i5k/wPSTOcPQyn2YfUER+VlLoUwblSVNP8t7Mu3OQOrvUAxXOKz7cU+woG+LQcldyBNnBNC+Z1ICild2Je5yIMtqpnVLrpe5nOtC13P'
        b'KjnQNFSwKbEVKIiYXZ2DfbNFR8XGy1big3rXbdjnLUjlCRquYTZtM1vWEbJ5JnoNnvNykcoD1wMIyPiyLuJVP5rs4RHJ9HqJukUE8gE3Qk8a9i2Fi0VySbXVcPkVycC6'
        b'chirwHZoKFJLG386ERuleyWk6Xrs0xGrc1SOPHfze9vI/R7QZHegyVE5WmorudHCjgWR/BGOwlGeRZKwHJpJQoLoFkfdaH2SdKuUErIa7HsZmxyFo/zV/JZHKhbTTL1q'
        b'i03rNcR3GyVFXZgQjH3COO4CVxnBPYP9vNNiLF7It6sN79o0Xx/mzju5i950px07PeWS4FewLoE76DJoSiW5JzjKU54SDrrhJbhBfRoVniqp9HMdTsuk6tpt7J1Bty7l'
        b'OdWtBtAqWVM3kY8S7AskB3ZUrrBynNSzXoGXNXCPwuNttXTvEoFZia00XXZAAxcODpW18O4ULuPiZVEav3RXtVRNukHp3VkJkLuxZpRmq8ZR7YIGqSIXTtn3OQ3ewCaz'
        b'zThrXUhJbJYDWBGlsbzsVAU7hZ02z94doiGwfewoNWHZK9Lmdh/CBs0YqNjDRrtF2JqxkXfZRZBZq8HrhXtYl3bysiyol/DtAdHIdg3UzXcU1XIoPeUm1rd0n4bWcN6p'
        b'qNaNHTYMcZ+l2UeM3VFVCyAv4MZyL2uRBo6tdCqq9cNdqdO57XBUA3e9vZgeBojEToMrXPAIyre7NDK5F7O8xwKFyItxvMuMlJc0lP6WYI9NdVeJ4EnS3cIOuKvBFg/K'
        b'KOjefdr4yXiV98qjbKBNg1fj3eTSRDcToZzv0CRsGa+ZMttiq2qfn0qknZ8QQN0CTRH2OOp68h1csC3k0Tc1eDZOtG1Dk1I6OpgNd9dB+Uw8KRnII9puClE3OUHaDV0B'
        b'UE4MsMRW1YPOhZuyJdIHJbwUqIS+jVC+SXhpuxovr4cqnVIyypoD2VieEIcVijlQISjwMXFrbHtR2l0rHFfHY1kCNqxQC/IdslBzhGUC61Wvi47HqlCsnKtjh1MwEOjh'
        b'oxinlOr/fljjNTcpOEZJJtwiKFfKoM3DLzqTnSCxHzXzOsF2rMQOQ60CP7Fip1fs1Ephdct2s51XKUuUx4VDqgPqg0p+XqXi51XKw6otQpaCH4Yq3/8dqdxd6/QTxY4z'
        b'Ra0+n59jarMLTNo9+lxjltG8P2RYw2F/xEqnqIG7C/LNBfxENNB+hqo10mh79MZcfUauIYgPuNZgyrNNILJ+w4bK0Ofv1mYWZBn4mSoblY8nWvLsZ7X6zMwCS75Zm2/J'
        b'yzCYtHqTrYkhS6sXh42115CbG+I+7NKSQr1Jn6c10jRLtBtzpONado6b4RglZKQOGcbMJWyZO417DPlBUi8m4KrYqGESGPOfWxH7ySTFGPaZ2RIM+swcbQE1Mo04EV+b'
        b'ab/zZGa7mKTKrz+PmZ1c20YL0SZaRDNbI9P7huTgiHkLF2ojE1JiIrXhIwySZRhRNtFQqOeCBbJPgVoDmYZFbzbwg/D09I0miyE9fZi8z49tk1/SODct21q0G4z5O3MN'
        b'2jUWU4E2Rb8/z5BvFrWRJoP+GVlMBrPFlC8uccyoLch3GGkQXY3W54r8MlPyXqP4zGKGHYz7Cc+e0WqTojlmKAmFu8Qi7IbjDppZjJf5CWxhvJ8wtiCTHcv6e3iPEzhT'
        b'xhse0AHljNCO2yOkrofrvG35KI2wZQ3lzz7pHoUe8dIR7nc13sKPMhYLQli6x59m6AUOGTIN3hc1cC3Bzg6hS6K7aUEh4l5sf8l+JhiL53gHD7zuLXpTKtEqSD0uZBzh'
        b'NwISU7DPk4L7VfuB4D5fPhJcfHGaxoQN2fYDwXW7uOzQuCNTU6gxKiT+dN5HJ8Wbq3CUsLkITuB9G824uDOVT7E2FW5DuQeegXO2E0TVYSmk9OIZitt9omG2WuISNeHQ'
        b'LFHJK3h1m4gUh3T2w0Xi11dsoY0YB7ETi2m+/Xgxg+gdE3pWEZzR4O3oFPvhom4Rv/7CIbRq9qatUEjBpinJFlCURqD5TYsooaU7F9lhLN7jk/hgMyUBe/OgxUUi7dX4'
        b'CK5JeF3jqyclX11qJ+BYny6t5xZxSZG4lnWUnem/iK18osUUN26LUDENTwoSG2zwyOD7e2erWvBx8WMn/B5v+u8VuLyJoVAWEYZnwpWsgihkYPE2nbeUTMBZf1FjxFL7'
        b'zsfbmCiWY+8qcS80ezrOgx/aDhy3ULLzUPRWwF375lNCJzGYRDhxmPbfu8C++yJU8nOkyRt1GtNBlX3zzdIhKZ5ZDJc0hVCRZN9+OD+Rt9+RpdIUiVH2rQ+PlKSNL6Sd'
        b'h7pw28ZjD9ZLA9UVBtLGQ1eSfedhYDcXdjNliv2083AMK+xbnxLJjWIP2flR2nciRo32nZ9J/JcnZlBNjOI2XJph33p3KJVI2sU5BzV7oTjIvvlTQDps9UvE27T5lKjV'
        b'2ncfm7GLd9oNvVAu7l0HDfbtf9lfp5AIygU8ShLunYaX7QZAG19nk/Ac3KUxD2GzfUjowOO2nI5VWshwThnsYy6Hkzo5F398NPaS5czCCrvlwK0gfmfNXOwgw/GCTrvh'
        b'wEMv4xJDmlJklLnTMCrxdE+ccp7PqZ3hb31snLY5pL09Of2jMSXN7/hu3V7k8VLuz16ojbuvmOYq/mT5ic/H/vz4567LT9ZGpryb8Lgg/G8+n+z/xgvFn7u5+w+sPDDq'
        b'9sSZN86asl4K62zqnpmQdDDyj6+//vh+zG+6Hh8+erPzvb++9eYv7qxuvfnp2h9dKvlMM+78vXNRqb8Wf/arH/6xUHt1Qu36+Jnxuxd8tL0kNOPivz+9+E7nJxG/vPxP'
        b'Lr+c+kZ35V7Vzpi0XSGZM6ztP7z34PtP57+0feH0ztmeq3pLNqe+97v4ZYo/Wa7/7bPqf1n2zfoH835x4sCFVX+pXPZh+hsHC5bmvLn+b1dvvTFbqb4Yv/3RH/2fdh5f'
        b'FteHxQen/MTVY4Z/5xHh1Q2Zs6ed07mYuYN2zR47NzggZsvaYDkxwAZ58JoM8xS6kQ+XoW5uSGxQoC4Eq4OIpN8VyQ60yh1wBhrNE1nacQD645ODoTSZCJlaS7mFZp0c'
        b'q7BihpltsFt4EXvaKTD4EJ4JkdHgxfKIQMpbWZXKYxI5eZ/toaO90kNHe4JXw7FALAuVCyHwSIV3Zu81M2qXRGZRiuWJQbFYtQCriK7Nl3vhLbhinskz4hfxfLw0AmF2'
        b'NSOOcAdvKYRxeEJB6Wgl3tXJB+UBOlbWEXRu/NfXfbslfDFuabap4IAhX5stPcYWwljO8kF3HnPT2B8s4olbWOw7IuiUMqXMlb+8ZHKZL/32oZe7jF33kKn5Zzn9VtNv'
        b'V3r3oN/sXUnt1DI/3oq19qK/lKyV3F/GiktCEqs+CTr1oJLNOagg7jToYmMig0pGHQZd0tJMlvy0tEFNWlpmrkGfbylMS9Op//4SdUoTe3LJxAiwiaGsiT1TZ2KcmM97'
        b'jq3Oh63uqPChv1zNpOfv/PQCro/CumHqp30m6m7X/mkfggJ2xn8QHkBLPG0OlidRYleVHKsSvAoVL+BxbOYM3uVFRXxCkkThZSwP7dBslWPXkvUSIjyC6qWc+NfhUYn5'
        b'w6NFmQob6VA5M/hwwfHsmTJbaePtihIF8XYl8XYF5+1KztsVh5U23r6TePuPZM/ydv7woRNxNxXkafV2qj2cVA8n0M8Q5I1/h8ebDEUWo0lib4UGE3H5PIlm2p+IHE60'
        b'ku38iwQJXE8zGvMMa0ymAlMgH0xPd7JGpudMXiauRNGfXcSI3NS2KKnHsyscaQpG6KNz9Tu1RimtyCwwmQxiYUF+FvFQzuvFnAJLbhbjqRLl5AmGLakYmZGuMbIlDxFg'
        b'Snb02vBgs6WQiK2N5nKtET8PYC2C2ES6v8NPlc/xU1WS5UX6vFO1cKTnLksTAuOCoG2j9Agmu5CcEJsoE1y10A6lmsWUnDdtNA6qXxPEZTRK4E9+8tv0kF/p9DH63Ozc'
        b'jA/Tv0OvD9OPtMTod2VX6dsMrYYP0wPfbdO36hMy3bNb9a7ZP8uVCdM+0uQpknVy8wxm8NbYCZpAbMR28gfCv4pES7AEjlOhT4ndMrxvZg5IvO8+3I4PiSN8JKyrxosG'
        b'njsLE+GOMh/qoEUnH+bsI+GAyu7xgxrpedshXPOScC2LIdpojmsm7yE0Ug262q1q0MVmHxKceLA3T9bGeXqFiREgE4MTqRmHGTbge04w0z7aGWbYo74eCmzla5wMt/gy'
        b'ndboBycsTOtwdwzee7bmwA4g4AQxlAq4EqTYHj8fqoqgE1qIfDyGR+5EF2s8sTF0ksSkH0Ef9Gn2eEHDVmJhxAyxXYmnOLc45Ltes6cIb2ADu1NC9AJ65VKh7CR2rRSx'
        b'3ztcCWfxgSDHGpkvlq7k7FSPD2PFcJNhg1yQFQhwbyM2cDxTecBxzZ492IbH1TTeSQEbsvAsYaX0kBc0b2NgNwt7bVhXG8BBcmUAnnYuc+zLZ1UOGBjL5Q+Dh0fmEoTi'
        b'FeiWCXKokrGDuCsjo+QShpIKjpPS07lyq2u2qwMtlV+Jln/5sioHd/PhNY4vxQqGK6z5V9cKviSFZ53/xzP4zFwulmgwP5+zPyMg00tBZqaFYDE/83lB7Vn7mpRIbRSF'
        b'cBODzdUUHjLNBSbKwwstGblGMYcGytjPW9pgPIryepM+97nxVpF3hjjJpmebYuFP6AduiNoYGES/Vq9mv6KS18+j3yRe4KrwVfxGVFRg0HMjOq1JnysWjFh7YIvkei6U'
        b'Kg40ahZD8P2FzyiQ/Xyt2OgYsaDw+ZDIfr5eWBy2ef+wkgd7Al7zXEgZnRRtWc5QpT6BUvByrMSrXz+ySHEF75l44rsgZYIQRv5duDHrYGeSUqp2jDKPERgDfk2WsdSi'
        b'i5KyYXz10GooT4Qr9DlVSKXc6KQEKY14biaUQwmUUKr5inyMzG3Jfj7M75O8BSJofunjDnm8tc8iVV2gzWdtBJSwSu48YR4vJ/D88CFlgPUR0/AxrTJcCMfLeJQP8lHU'
        b'KEErCC+8FpPnsSXNU6q8wG2oPUgs/zIeIyKZIqQYbYWeq9s1AjVwfS0q3SNFHiFspMyOQf967JoVsQBLpVlfWs4vwp0EvBGRs0OaMT6S2rIYoiBcfxKxbafUFm/MsB24'
        b'4R1+AFUHpdKccONlY+a0d5RiD90u+K7PrKYDVfO8IMxjzUczE68EGvS/eSP1/ioXvxe3rIq74eWlGR20OuZX8mVqhctv6mO27t//tyOHfqt5w1PvXTxl9MGUIO+Mn39y'
        b'6sbox7/797JP4sLeH/OdsCkePza3/teJlK75odqtHfdv7Nt3dFHGobNavf+5Jz/LM75ZtG6T/t3IT2bGtCjaNn9WlQvqfVvfO/3t1Em5f87uivjP47/8aY2uqe+906+0'
        b'h7T3vpjTFB/9cEr/eyum/THiclWIzpWnUngMrkIPy9OC5TuxV0rUlls4AYAn++AcMQXGEvICnucJ8NjMH2A6iUfxAYsOlK+xpC0MHoRSu2DGLeJdSIVX1LFYChfN7Gs1'
        b'MIBlSZp4rMhN1DkGHAdWpWs+3DczQ9vqBb2U/MkELIEO+R5ZpHcsz9aOHMGbLO0LTQ6WQyO0CerD8kA4CVYzi5XjKSw323I5YTc28FxuBT4ys8eEJ0UdiIcniVgZb0s5'
        b'BcE7TLGTJqjQyST+4Pq1s7chSuMmZWoUbjihCZMIzRFigbZUjb3LKeHy4kmZl0wpZwnYTHr52V6mMU6UZyhdGlQQ8jsxna/KtBROmdZYB/thY3/sxH7qJjqzH5aLY/mS'
        b'JKjf4UizeL4tjEKrAipWT9LJODWAu+Mn2s5NXGDAfm7SDJXDvqDjCP/saRQK/vJsueOLOLIv/SIOC/kndMovvjMM/9ZL+PklPD+b03QeqZ3PJv6nE6MRAZz9yJ8DcLWU'
        b'Eyxa+8LfzwngpudI4D2REls2YLLbfrFoEtxy1LtbkvhDcq9gO1jJhbAsESs2YEmCfPQauEWu0gz19AGb8aFOSPFxgX7oSTH+/A96Bedsqz/0+m16kJRcfPAGTy++lZGb'
        b'/UGW8G6CLuGdim/umvW27u30CW8EnfM6lf1Guvo7ZmGpu4f7vxXoVBJg9M6z2PDCgRZQO8MOGKOxxCwdYu6VS4jD4Abq4ZE8WL+TO2rqmNlzQ6bA5aHikFQZwovbOHoc'
        b'JrAp08S7QgNWPAMf5kgzqwZg83h8MFQ74oWjVnxAxl09R3Iz+Yi+7LLTYHZ4so/dk6cxD3blBRWT75CnKqRyxsiZiEy6yT2Q9fEjLxFHSx54VHjq5eyDbM1QNyXPSWBo'
        b'wUpe7VqPzX/HweRW4Ws7GHHqL9qG2eeGwlyjWXR4kXT6Q66iZVezTfqd/DTnGY+ye6VeO3/EFHlY44Co5E1JG9enBmmjYtZExW/YlEi5c2RSfFpU8uo1QdrIKH4/LWlT'
        b'4qo163VfnlArRnAeHuoPbHJh30cs/P2s9CBFxGrBsogu5u4wsy8izmXfZCxNWBczlNBgjQ5uuYfjSajf7w71sVC6n6iL2p0l2GH8MWscMK907kx+w1PBKdhKHOeUEq4d'
        b'wm7jxrfvCmIKNY8R3v5t+tsZOeQfH6YnMJ8x1GS1Glr1H6R/Kzt0vU6fQCk5+ZBQFhOeNc8StjDiX8L/Jcz332SGC5HhCypS337H4xsel46HThByrvncqQ3UKSXnKPMp'
        b'ZM6BZXjRXjhdt4GbNnRveYFFTt380OGmPx4bed/F27J4BIRWuG4vZyqm8ltHoDEpnkXl/euDA9SCm58cru43D7Pbkf3CnRIR0SlrH2t3jXmuMg/uHF5S7u73/+AerE/A'
        b'MPcY9Ho2QYdbOybOjQkKTJKSc7glsk3xhYfKcVgM3RSjtNRKHTJKClHERM97Y3UolEnuNPGIMmcZ9o7sSbZ6Hv8mqaOe91XexM7htz9bz3OOWLzwla/P47nQCIGKZULs'
        b'1LTQQBcooA0PHbGST+XqzWZKbDL1FHWGD8rjlz5LKhk+l9ING8uR3n1Vdidlc/8bA6hsxADqmmRhT1O8tA47Ro6gMiz7u+lPwyEOInGhUvoTlrQh/dN8Pym7mAvHoXtT'
        b'puh4XFGFV3hcZV9vhFME0A++PLjaAuvULD7+4oXSl6bDfCuij8ZOE4zf++sahbiZ7nQt9nEEWx5qn6bnZCfo/yk7aP1TghXlJ8UTlvj1XmiYsMT7Z5HzRXcxIrMn0S3e'
        b'XbNlWcSWZe0zo4IVKct2e2455B5FTFYjPA4d+331Wzo1P7qAPjgPryoznw3G9kgMd+C6mT/uXQd94w5jlRN7T+aVdKwioElUCYuS1Ifx3lKOIXvxIj484D0UuuXB0LaN'
        b'n+mQ153GkgDocz7XsR3q9G/hoXvN1ENwDno5gA2HL7iRzaXegw+LCGmPxj8vxlSoUWIjnNtip+tfVW304OGcjJq5DAcuXztwrWFw5SFzl0tx3UNmmugEXYMaBnVpBSZG'
        b'BpwgbMQJSZpJDjBjoywZBmbfGlZtZDFmOsWScmY8jxeOvERKM6t0iqSkaJ0sWidPijYurqhWiZ/TsIH6bZvOGDeMifQ5tTN70bT31Wdw20DyQPLYlIF1635wtPjacnXC'
        b'WNW14o8P3P7g42vrlq7Y8mflkRuPYsvefdpw6+M/PfVeNv7yFK/A4xdu/nPq7t4VT+cFx2W3h703bueHrpqn7366dl9S8NMMz7J9tdc6ImD1+buzT4kNJ27uNMdVLtg9'
        b'blPK5YiZyyZfVezqGHhS5/NGwM3iuLbWllNbn7budPMMaj4zu8Gon/Dt1G/Ebe5pWNDRfNbSsVMx6V9fz+6/fTYvd6fLi8bM8Q//FXd81nNZ4f8f34vZliNemOHffOgb'
        b'pnFvvpDk0mguKq41i2Xfv/R+0K9f+K7qwP2At2eFfH/uT8Z1vfvmgt90icfH/iXcu7B2m0f463kfhzV+/+3tn+yJ25v8gz8dc7kxQV9nzfrWpyVvVrz1bfffn7hZETFt'
        b'm1r124wa/+/u+46m5cKvfrkqOaflgKK2Z+kPO0+96lLZvj3ih09bR78bUPLLwaq3flT1yx81Fb0zMOVvtesHTAnXTYkptaWLoz/O8v9J14n/07g+0nLadZfm7Otv/duf'
        b'f/ftgx9NegLdn35kvvTeQH3wj79ZGbyrduCdbX8ea1gz+Luq+prpU/Je+7259a///J1Pm7w/V9b4lv3n+e7XU0MmBf5l6zd+9fmWP1hf/eDnG3ac7/39wabEsb3f/usv'
        b'KgrTLoSarm76+WPfQzW7m/Mef/LoPxKvfLHR9IfQ8/J3P9h0k1yalzzuuMAjspbilQkyQfaCgFU+Htz1ivAePnbyKmjZ5XCstuWclx8h0LrNsGBp6khogB0beAodLcIp'
        b'LKcEujJYLaTCI/UO+QxK7fskXn0DavDO3LhgLIlNSFIJBKka6JGTU14KlCDgEl7YFs+wmJpgRaxKSMBjGuiWY9tuPPbfPB3Vef23mn/5OCoTc/4R3zhOuKal5Rbos9LS'
        b'OEb8nHnuDLlcLpsv0/JD1dFyV6WvTPrnrpKTH7vy9/99/1zlo2Xsn6tsrILVHPxXyGkFY8e402r8ZP4BctlEb3qNkstM/nasJLiTp6U5oZzn/7/GZabJDkhkE7EjJ+ms'
        b'56ezny0/QFWOgUJHNVaz8Ayl9OnkWhfBa4JiMrR6G3t/+kgunqd2J069GVz+0B1Wjl396/yFyTPcfYtzfjH+81DfN9bfD1gde9V44sZWfe+Rj7q+NT/i12GBZS7RHjnN'
        b'i5KiJ9xI/MGJfOXEzj9GF8X+9I8Fhh1JH3zme+hwd1OlNvqnO97/Rff3Xi/9WcXH30uv6Te/P37/5egpMc2f/TTbq1t3f+uRqvRV367QuJ9/uSgRPe/9ePuvG4x/1S2d'
        b'7b/u3x/PWj1n+dgknaeZMVTyuXIPVplKTqaFsJKXBnq3wRlKPMkpuiXv6B6H9xjw97BmE/clUwQdhQMKuEruWyo1qYj3k5TBAgJUQvXCpaSL0QpKQPCGWXoweKoqPjYx'
        b'MNElF64JaqXcFW9O50UzN3zIvDPOXyXI4gW8kASlZvYdsDx8su5ZhoS1mVAVGk8YUEUBqFohrIUeF/ZoF57ngoz2xAHWx2ehcy+1MH61MlC90MzoNj7G2hzswwry9dDA'
        b'IhucTHQ9YFES1hybwQt2WDNjCkuooBtr47HcRVAGy6ATqw/zWaZ4+fFA7yzIpLk+cFEJLSsCOGXAe3APzmG5jppJJhIXLxO81yk2LcUr0llmBZal2xsEsVXRdIzyEEhq'
        b'8S7ZuBufDK14Gq1zk4MorSqXtggfu26Uk/Lb4M6w/GTyPwZ5/oFvlE99CXQZ841mG3Sxr1IJnozSUFamUMqY87PMzIfTHEZ03BUzGf0JNU1xuP/UQUWuIX9QyY5PBlU8'
        b'px9UUp5gHlRmGTPpnXKU/EGFaDYNqjL2mw3ioDKjoCB3UGHMNw+qsgk56ZdJn7+TehvzCy3mQUVmjmlQUWDKGlRnG3MpgxlU5OkLBxUHjIWDKr2YaTQOKnIM+6gJDe9u'
        b'FI35olmfn2kYVPMMJZOf9RoKzeLgqLyCrMWL0qQSa5Zxp9E8qBFzjNnmNAPLHAY9KdPI0RvzDVlphn2Zg25paSLlYIVpaYNqS76FEoohWJMWO9nEilymheyNfZvMxB4X'
        b'MjG9mdjX+0zMnkystmJiVW0Tyw1N7Au9JkaUTfPZG/N2E4uoJuZbJlZxMLGTDBOjryaWIpjYf7JkYt+uM73A3hjpM7EvzpqY25jY/zNgYqU/U5gDJNl2uDtA8vPVTiDJ'
        b'733han8+aNAnLc322Ra1vpiYPfy/wNLmF5i17J4hK0nnyp7bySrIJJ3QB31uLmH9FJvpMF5M191J/SazuNdozhlU5xZk6nPFQQ/nDM20zK5ApzfJ/pZK/8/WcnaJl8yU'
        b'cqXCldlY/FgWkGT/F0XEgig='
    ))))


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
        b'eJzVfAlYlNfV/zsrMwz7vomDgjKsgoC4LyiCbCrgrjDAAKMIOAsuifvCsIOogIosLqCooCjintzbNGmaJhBMRJq2afstTdqvwYQvZmm//s+9dwZBTdv8n/6f7/nPk7zM'
        b'ee99zz333rP8zrnv+HtuzEdg/PvVZrjUcVncOi6HW8fL4h3i1vFVgs1S7qVPFr+Dx75ppFkCPqcSdRhbijitdD0f7oizhKY+B3hAm6lGn+FxO0XSHIX4u2zz2EULE+Vb'
        b'C7L0eSp5QbZcl6uSL9+pyy3Il0er83WqzFx5oTJzizJHFWRunpKr1pr6Zqmy1fkqrTxbn5+pUxfka+W6Anlmripzi1yZnyXP1KiUOpWccNcGmWd6jBF9AvwvI7N9Dy7F'
        b'XDGvmF8sKBYWi4rFxWbFkmJpsXmxrNii2LLYqti62KbYttiu2L7Yodix2KnYudil2LXYrdi92KOOM7gbnA12BonBzGBpEBqsDeYGe4OFQWpwNHAGgcHG4GJwMIgMVgYn'
        b'g8zgahAb+Aaewc3gYbDNngBrK9k9gc+VuJvWbbenlONzr08w0fDd0/Sdx+2ZsMczmZv8irvbuR2Ctdx2nvSQgp+YOXaPLOF/ezJRId3WnZxCmpgnge+fwXYII9+FbU8P'
        b'eOCt5fST4Wby9Mm4DJckxa/ABlyRpFDga7giNnV5oJibukSIH6LOqfThuSvMOIsFb/M5eXrAxxtzOf0muJmDz9jibqnlihjgUR6bGoOu+GJDwLIEXKNDlckSXBKTCmwr'
        b'cZU/DIErYxJw5SrfmHhcmRiflOoLDYZgGG1FzLJU38CY2AAeuiTkdKjEMQJdQLf0YTDEFFyNHgL3MTxS0SFgA3zLglfEBMThchg6HpfGirgiVCXdYOaUyRuzHFam5dgB'
        b'l+OWxbAkdJ+EsEdi2EMJ7Jw57JQF7KaVwTrbiu4RLFWJcHSP+HSPeGP2iD9mN3h7+MY9euHu6B7lvrhHspf26CLbo5AoWGau93VLeXpebfxWjt7snSHghFx9vIBLj4/d'
        b'Hs9uPpRIOBuuL1Ccnp5X7ezIbkaHiTgJt8CHW5Bu8VHwGu4il2cOtzuyXYQjdtyCN5QjU7/k94REL/w9l0fM+0t+A6/LjJOaLUgP/UTjqhhityekfGV9zFqaLFv+Ke9/'
        b'1uhVX3JDnD4AGgpRaw5sBiy8ry8uDY4JxKXoYoovbHhVAD65LCg2cFkCj8u3ls5NTFcE6x3hEVQmxK1aC3wd3YNtwfUcOpHjTFtwLTpvp9XgarkIiDIOGZbiy3on0lKG'
        b'rmqg5co0MyAqOFSK7qOjerJic9LdtbjHw4L0quZQOepcQpltiMClWlS5LRlWFLdwqBFdxr16ZyJAN6pA+6DNHx/lQ2Mrh85sQWeZcBX4ADqk3YabRUSGKhgpfQ8VAd1C'
        b'Db5aMIbLqEoMTcc5VC2aRB/Soy5zrR6UsJw8UwMzTMCn2YxKcYuD1hKf3U0eaeJQgwSVs5aycHRKi7tDcRkRsA64Ba6kA+Wje/iQFiayHyYKTac5dNK2gC1DJzoUp5VF'
        b'Iyp3M7DD7egwa6pC15dot+PbuBPsGZ/gUCV+uJeuEO54HfdqrX18OfZQ/TbGbRo6iltxtyXqjCMiXOFQE65dQB9xxY2WMk0Yvk8m1AGPLFmmd4D7W30XozIL3LOex/Ek'
        b'HLqKTqLjdDor8Blco8XXwwvJnh7lUNVy1ExbbLbjc7hb7yoUsKU+hk7j43SQIveZMty1B10kg3TCJmxdy/bg4QzcAlPpmsVnvEpxuQcdPjwBN2jxrcTNRN4GDtXwcA1b'
        b'zfvh27XWsDXNxg09iS4GsW2rS8bncbcE3cFXSds5Dp1KjaMP7Z6E70ELPjCbCNAGAmSDTtHFNKC2LNytQy0rRWykqkmoijZlo4voJO62QJcCxeypRtQ4hUoXOBn3QAs+'
        b'PIOsQTvwCw7UuxB2FY6w0/gaakY1RPKzoPK4CzdQKdZ6wNJ1S/NQOXnqKoda0MW1VE/xLdSOTkFbEc+4Qq3oAGpjOty6A5VAE3oQTta1i0NncTWuY88dhG2tgzV3EBu1'
        b'rgbfx/eYKI34EK4lm34K9fLYk63o6Hq28KdcZoOc3fjCetJ0CW6ErGHD7Z+xkLa05pkxVTmD96FW2vYayN8DG4nr1xln0Ihu4FK6JLgR3VXLJBPRWdLUw6HzSXlUDivY'
        b'1AcyfB325jjheBPEwG34INuz0xpfWRHYfKWIDdaAbuEDtGlzLmqQ4R50Gp0gK3kNBnNAFbRpDW7G92RkC/aSaXeDOqMuOWPYkbmXPFWK94vYYC34sI4qYbQAF2t1ryUS'
        b'+QwcOoKPxrHNRJ02Mu1soZCtfD3aB5pOl+JgMCqTmaNq3EyGuc1BZLqJD+tdoc0WtVqgsgiIUDdR+USdiBPgVl4SH1/Vu9PlzcJ3UVkRPgb+pzQeXxdxwlwe2u+Kz+on'
        b'kvaW7bjV2B7KeIi4hROkqILv7IfvKATMmkEF8B1cJuCsYrgCrsAe39DbkECR5wNmjEGLMriMlbiYdpbtwIfjxLB96ADAuSzUiFvZTp9NRYe1unB8bHTebcn6qYT9edQB'
        b'2lILJtARAaapTACXeG5zFDq7LjMygQvTitDxPeDDyBrNx9fztLoAfJgsagmHinegU5TJPHQk0cTiKj6Oj5GvS1QRYcD7uJDzwBVCKT7mwdazCd9N0uIbqG0Pj7nwStQJ'
        b'az0F2pKE0YwN6kHthE8MurrLY5QNui8UWOIuKguqjVyqhcXfbYopAeAYiSwh68CRGmW5YpIlHh8HLpeZMEeF4nkCuizbVfgCeF5bXEFcxRlQRNwmp1xQdao9ro1Bl2FN'
        b'TEzAwxoiQolgwCVQgHulRZRLohZf0WpQGbpGlKeYQ4dQq4teAS278E1cP7owdG3Rvc0yOah6+yp89HV7bpncTLYcd9Ap5aITVsCnY5kpGvqgUn0QDUWg6ideWuAI1Ikr'
        b'yJ9L+PicTCEXqBFtQ+WWVCZrELcWmJXsMgXQWPDPwTQiEJWrjQnDR9jsKgQZTC5wKSdh61HZugQuBveKQfjeMMotGFXhNvD2NHZxuBIiXlCE3oeI1gymdWXsSsGWRQhX'
        b'cu74+grcLcBd6GIic9mHIBZozVEPvsRnW3Y8I1M/iwIE0NfKMRtfMW7vYOPaE2DvrsPqo8sJ4owEbhvqlKDbsbF02TajY6laAAhlm4TM+52emk2XLQ2cVjUR7eroJgog'
        b'BJbg4+hINljbSfBQCSG4SYQqI/EJppzX0AVcDvgC3wVPaUQYSSFUOWNmLB2nV8AXwBBId4kpZ60A33vdhoqknu+rtUIdYWSiJ0E30TFw/kStUvIWv7SN6LYPMLnIdLNY'
        b'aCYGDadO7IgLfkhQC7oyCmkOrqJ7OFfl+JxNBTDqGSuVyV7CXhOBJ63BjWxq1wEHVQI/b28TCIKx7+lDSVsnKpk/6gNgfe7g/SYd66DbEcbUPhRXiVAzPq+l3iYMAvAl'
        b'7bYIlQk6uflRtUd3HN3G2zH57oDPm9h44CtCCbqyls2zIcGV4Ky6XSaYBSpVyRS/CZevHyOXccF6QBuojoBBz8wAxUelIu32KKpmsfj0ZOAG+lBuxkL5sbxsKq1DwTyt'
        b'3hvdNmE2VOJAIa01Kg43jXGJjAHxcyfREXREjlpXuaIj9lwCvm8WmoRYuFKjO6DJljD5RhPKQ+05+kCiLw+3wo6MOlN0ONNo8/jgOt8INnktapJAytJtxYI3bAo4Ifjz'
        b'cIYJGKKWKcxUb+jtTMw6XrJ6mDy6jm+S6Z8QaZXIuM0V4E+PEn71uI2sQCPoX+xqZoIQRmZpZbh2mwlOuqFOvR95yrAegr1Ju0XoXoopDkTJAaW3r7LnkvAZs6AUPXO+'
        b'J8CDlWu3r4k0IbZkL30IDZboOFidyR1UjJOcKQO6HS7kgtBd0WZwje10ZxZBKndZu93cTMQUoGKWLXPCXc6ozMjskonL9sTReDBVQOJrHJ33BHwalQJWBK1+YEKL6OAM'
        b'PQXBB+3wjRd8lAW+CHyuED7uuEcAGtMgpMIsK5wJbPag0zyGxY/Z+jA1PbgsTmuNalGDCXLiXgjk0wj/6+iaZoxBTkBnRxV2rD1uE8GmdKAHdA3N9uZorXPxPh4Dqadh'
        b'6SrZrDtRseNYtwXfxOjQaOQRCHCnDAImEUqVBSrQLXFH50xYF90D/sRdTducZBKp07R2uoLnFnhWaGaPLxhBIurFD4DPVlxhgsbgOZv1EaTxzCp8eszkxplihBBdt0hY'
        b'uBhdmUKgpkGDj0sAyVyYQfUtemcCgOpM3GkC1Xg/6qIjCsHej4LG3dDjTh7TxROoBHXTioSCn/xCzKy0BxOKgiwxDDWLUNPrYrrl4bgXNrDbIhVVkB0/T2Z/CBJIooj4'
        b'CqpC3c8VMXf1+NBp9NrT8SkRhIQWfIQZ490wvI+A/VuozYT2F6I6ytEd16CHz31Rxai7YHfOigSwFJabw3krRGaRMHg1M8fDsLPtwDIHdZiyBHzXh5l3A+QWrXHUkK9R'
        b'ezbZ3xgQlsCtRBVmXkWAEQi/9fiBCtbtOmqaY8bmfBLi+Amm5vfQ5aXPp0zDOuVCAjo+6jEd3YRQt96bgQ18wgl8UCJuN2OI92w2n6qf5nWy3eNsBR3YBNp3idnKNVA/'
        b'dG4r3Ub0APKVM9SFlXFEA68TdPwwSO9NE9kt7uOCnREZeMzDJegAmO5cwPhEFNjAs7h7m7aIzyyuCtWsphPaijvwkXHuH1jMiBu1BFQswHeCIL4Ru9X4QBfgsl7MnF61'
        b'UwITo9dC/SI+4QM+gSBTgm+B4U+GvIaI4SYoIEnbFA9TyuaI77BZnoU9PE2Sr3votilpS8EnGbK+mZQMTfih0pSzuYJVUWVqAPwGTbbooSllg0x/H50Zan1t2YuLfAOV'
        b'glpeZavcBavsi27RIXbhzmzI7pai/ab0DuInbbGQgQ/t1uOTRUYjOooeLKEhGPzdxQ1GJ3LJNEKzfQSMMupFbqArRjeCj83GIKp+B+oWMahRi29kM992x2cstJ+cO2pA'
        b'V0dtQMiF4JMi8LyXQeudaEg9uQfW8iaqsjCaUUMIus6UHoDVhLFq0Qnuyegl28dyXC1C1dEi5p8ezoNMBnLYE+gmn61/M/i9ByzkQghAx8fELgO+Zwy6z4PX8nizmbgG'
        b'UAXdsnO4cw6w88JHTBnx6lQq3CTcE/zcgACIjYNVprWbjh6KUFUOOkvnKp2MK2lRBXWIWIZ6Fh9VUZeRtwAg9NhYyM80CmYDcvVG2CJDOA81gBs7tcA8Ed22oAz5UjeS'
        b'ekMQMCXl4BnPUbWZDxJ1v5iWaJNHnbpCgG/hc5AIMSw7BT8knKTogSmJlwMjsmhRm9H5l3CVCesRT5SO6wBY6EWFYUZVC3fcAzk/2OZxMeN1Oh4fooFGg+4mv6DLBajb'
        b'FPTc8W0Bvh6QwizpCLoZSth0jRpSI+xXs96fRlEICfUv48aN1s/zyIdCK1SMa1lAPjkNtckkuCNAzHL8c5Ajnac+bG9i/ovWdRs1g9+4zES6KsBXtwH4sIO+4uyZwKR7'
        b'vqlgscGWSgOZwA0w1+dQrk7+slYFmM0Ak2DYaj/qnCTToTKpMRbVRkAgpnKWIkMkKX10o9HSxxwX1nQRXVkqM1+JbppKC+DDb7FKyl17fE5WhG7uIfwuQra0QMhcxwO+'
        b'8zi4CrPLx/ueWzbxig+9NzOQEYk6ZUUbcJeY1fXq0M1gatZ2s3NerZmoex1kFIc247PrSGZ+WbMFMq14nhHvH5wrKwqVm6o0+P5OulY63LTi5ewUNk1kR9Msd1QSgi9D'
        b'4lC0mS75ntfzZLhniY+poqN+jaL9Bahk5kuZ+/OEECbrbUvQbq1Ihw/601WfuB0dBFaOuNxUAtpodEGoYrE7KQEVo1OmElAU6mHo9XoG6pFZocZ5ZM/vcahdwme+6XLa'
        b'+jHziAJYaprKxXHOrgVAiFZFFxIUq6mIPGSJ77AeFS8uw1XRtnDecolZBKh/CUuQyvD1uS8mk2B3ogxY/gQuAd0KdRahcr2O9g5FFyaNSwOIPhfvJjvOKhroulAIyPIB'
        b'7f0aPqx+aTOU6KEJ7XrgUqEEH0X3mSQ3UTnufNGlzMHlozY3W4DvpwI+ovC+Q+s2Nk2sgodHc/RxK1QrQqe3oE6FhCqOynW+zGoObidx8AGHLpnhOqoIQSKBDF+L8zXa'
        b'XosfKwgnQZoO91FdCnmgl3jUdsYoF3WGyqSJuIzPdq6N86aM5uRukOnj9xjL2nW4eb3elpQGdnrKtCovU00vfg3d/1moN0+mXT7DaIwQtvBpWs4DHHwMH4DNAT+HqZ+7'
        b'D14FNUrpQRRkNhW4jSQkyGCs6aErRhtEBloEFKLuFEBbBanc6o1i3LQyTCHUu9HaB27Hh3FZ/DJI/G5aCjgBfsAD6HQ/iekqwbE343BpvJhbls3fxAvGrfgWfZKPe2fG'
        b'4cpgXOGvQJfQJTAACxuBYzY+Rp9MQwdwtX9iYAxu9xdywgU8dCkTV2SSKo3pQ45z6EmTDi7HxaaDzzrOwKOHX3wDRw/ABAZZtpQefQn5XIl49OhLRI++hGOOvkRjDrmE'
        b'e0TGo68X7o49+vrtMGyXuXzMJ4oc2Grlynx6UivPLtDIi5R56iy1bmfQuI7jiFh2Tuy3pSBfV0DPfP1Mp8RyNXArUqrzlBl5qgDKcKlKs9U4gJY8N45VhjJ/izyzIEtF'
        b'T40JV8pPq99qOo1WZmYW6PN18nz91gyVRq7UGLuosuRK7The21V5eUHm427NKlRqlFvlahhmljwllx1Ik5PqjFEuQa96IEOdOYtMM0ddpMoPYE8RARfFRo2TQJ3/0ozI'
        b'JxMWRrVDR6agUmbmygugk+aVA9G5aXaOHUxnEhOW8p8fR0fO5o3cguQJeq2OzJGse3JS4PSQiAj5wvjlMQvloa9gkqV6pWxaVaGSCuZHvvnJVaAaeqVORY/609NTNHpV'
        b'evo4eV/mbZSfrThVLeNc5Mnq/Jw8lXyJXlMgX67cuVWVr9PKF2pUyhdk0ah0ek2+dtboiPKC/FElDYC70co8Lb1NFnm7WvvCZMYd94q4F497bROjqQULIMie024TAXbH'
        b'R1kVDR3eQc9yZ8a6ctN0X4i59PQ52gU5HPV0AHd7FqIywm/CWm4tLlaxviJzzoHrEXM26QETkn3ZYXBVijXnkdvE56alx3Pz4zkGVE6nvKaV8bnF4HFpDQiVow6FNfWM'
        b'OfgGR9qkCuNp4z5cTv3udB1u024XcOiAOztrTA5kOU4pBKEHWmuOS0YH2WEjPoTaGGrfBxEE0iZLISkNlBoPHEvcWMZRMxeXyDQiAoEusiNHfE/EeB6HOTbJCgVcHiql'
        b'GXMdOSOjAu7Gpwtk2wRcwkyK20+B971JG6bjttmozIIH+ZEdO6m8bM24XUVHF+JurRiGhIhBcpujy1ADQ8iX8ZU4Lb7O41SolZ1iwnLcZT75XvhWyIhgyudmGs8x21AH'
        b'a7qKT0Pm1SXinLXsIBOfMp5/BfmtlZFlagFcQyLamfW4y1gHyMENuJtM+AC+y+FTkKCmo4MsH7mMT/K02804b3SAFgCr8Ll8+pQDfoAOabfzAdrgfcaj0VuoVMFOLyDg'
        b'3plHWlFtMGtcjS4wjm2uu9hg9/lsLFzqQFu2oR58h4wFgf8UGyxcygpoAMXvaXE37NbFtcY6ZAk6rODTOVvganyXtu5C91lrND5DWaog/zmvReUc5xPNTq89UCnVP/f1'
        b'ZpyF9xB5ZSR+Z1gER1UpNQmXTJ8m5LbhhyA4l4FKeWqhRQpPaw0oIEP4+u6auEQ8zebI20U/TXTjL7p8MjDmja+3SdPf9lqTmrd0o7edbPVmxWbrab+abFUTF1p0tNTP'
        b'umDOmW//8sEfp34v6nG/uTrPX3RwQPfsZ9e/nng5x/UX7z8srXQNPXfqz21739u38XDUka0fxHjOaFX6qnVbHge3eqfuDQrrUv5icGlGcO/Cjw9lxUV6ne10zfF/u+TS'
        b'r25vXtGi6/jL+tOPXE5t7JIpm6Y++cuB+3Zf55cef//Rw/dD9+J3Fs6t6jwWyHP0WZz2Seb3Vru1H35r99PzvinfGv5n5+dLI2/MPP3wuKWj9k93B0PTqu99M2Fyis0J'
        b'mz+dPdp4zuyjbt3G+YcnPlN+8dny/+bdW9F14P7Qm3Vr30xU/XG+qGzF8qgBhdkIWXzta+iOf6BvTCCfE6OT8ev4gegkah0hZ4z4CLrl6B8UGzB5oZ8iiLyEUcJxLnLh'
        b'plWLaPvCXbg1LhidTwpEJUkUYMhW8HElmFTrCNn1NRmYvFxT4hcYxAPmB6Ln8KfjUwtHSBa1MgAMuNv44s129vJOkf/UQD9cGszngtB9Eb7BQ4dGKHQ6hk6qcVlCQCyu'
        b'hJwqTIuP8q0gnysfIRU98HFgqnGExWsAHCsR8CRYSMA54kMC3ItrnBSyIb6vQkMrOT/moiVv0sjl+0yf7xznZGsKdqny5dnsPbIgEoTnDZnTkJBGiF1jvvMJixrQvG/2'
        b'cU+XizgHl0Fnj0F757pZNbNq5xgWP7G2G3RyrVPXqGu3VAue2E9o9m4Lbgnu8n40acYwX+joM+ju89g9sN89sD1rwH16l/bWzms737B7I3lgRuyH7rGDk32HBZzHMt5T'
        b'Cec2uXl6u9kj12mD7vInzp6Dnl7NXs0L63Orlz6xdhp082oKbAg8FVxtRkafXzO/OeyRve+gs+cwx5u6nPeU47ks53060XvQ0bUurSatOeWRox+09k2J6HeOGHzpfvOW'
        b'fucQctt1QtPEhontzo9cQ8i49s71S9vn9XvMJIStY713vaaZV+/bHtTvFklm7uRWH1q/sDrXsHTQ2qle3W89ldx1mFCf0+8w5bFDQL9DQHvKgEOoYckTe7JUT6xdB529'
        b'HjsH9DuTBufQPpvQTx1c6m3r7apj6rfDQ+0O7couXrtrv0NoNe+Js2+77YCzf7uu33l6n830b4aX8DiPKY/dw/vdw7/kwIyeTPQeFsDf77QEwN/1XhzB/STCeolE8JYZ'
        b'D64aAO2cwmJISDZvSAB4acjMiD6GhAQuDJmlpWn0+WlpQ7K0tMw8lTJfXwh3/r4OkZeJ0uFj0iMN8eUaWnsboysnSNeZcPnLPu6ZWsjjTRnh4PJbK+eyLftkw3wRz+GJ'
        b'zK5s5m+F1ocSBiXWTyT23zwVcSIbE/WdlnjFU2J/rkMWIQAv7kZzKnyCF0cSg7JEXJkUK+J2brMqFETKi/QeLEE7gbrj4hNZEqCX8zjZOj5EtX3oHisUdKDrHMsdUPFU'
        b'kjzErM40vdlJPkIT9sglCQCfJQAU/nMA/sXZQgr6BQD6RyH8biEF/YIxoF84Bt4L9giNoP+Fu2PfSfztIO9F0E/fzRyD+jUFW+VKE04fj8jHo+8X0HXK30kCNKpterWG'
        b'Qb9ClQYSga0Mo5peGB2P0pJM4A0E8VsJI6q3qpZoNAUaP8pMCS1Zr8b2RF4iLsP3L07ilcDWOCn2xIszfNUQJBuIzlPmyNUsJ8ks0GhU2sKC/CwAsTQp0OYW6POyCMhl'
        b'eJVmJ8aM5NVwdomaTPk5eoZMSSkPDdTpCwEVGzEyXTUA976kRwAZSPGjwK0oUT+HqGbztinj39xkr22WxPstC0CXJLgnhb3ESe4lxccm8MAaUIlsJipWp6j/+O4CvnYZ'
        b'sPnN509OvRva2FJ7s/7uoRqe+UqX1VFPEso3Lmi8vPY9C5fm2tu1isPq8JQpR0r2t5xoOXGt9rzh/JGWIyEVivqWI171+7tFXPAJi8GQNxT8EXIkgOrC82V+YE24BJcn'
        b'6I0BbSLqFoJVteFOtB8dH5FDR0d8GV2LC1oGYQ1yfxKyeraTqOWGbgjz0QkzhfgfOBbxaHCiLmVIxt5PZmFoLEHj0HyOxaFoM87B8xOnSX2TFw04RfXZRA26Tn7sGtzv'
        b'Gtwl6Z36RtiAa0zJMsPiam8SnZzd61Oqd/XZeEHcMMR9RTaEOUmzIYlJR4fMjNqmITFfQ9yOxn28pGbMBRJhmffzIt5vrIiPSTdSCPke3N8WMY/n/WM933GxD3deNk2g'
        b'nwvEitXk5acXiimkqHQIXYeUpDlAsDEuDFVuQx0z0BV0Ad035zLwUUtIJWrwfook7XXohKzIisdJs3mQlOCOlfkUq0biw/iyrGgbJAOnc3jYAH/c8D2KVe2yUZUW91iH'
        b'7pgr5Pj4KM/JH1AszRMaAfwf1YZqAE5f0PIKyEs3+4xnPOJEfEZWVCTmNuF9PHyYwydRyQZw32Sd9uKrs5j3xRfQLeJ+w33o21+Ll+Fzzys3gaiNVW5QF7pGi02QopSi'
        b'0/7g13mkPtTER5W8KHwbnx7nvCUm2yrknldvwHmLDKb6jRScuHm2ZNSJi/9lTpxUbv76Q5Ub6n3G121+0IURd0e6/+P6xw+UJcjD/+tVicw8KpZWpXu5DvGCgGRdCjIz'
        b'9eCt8zNfFtRUiViyfKE8CiCKhnjzxRC1MnUFmp0B8kJ9Rp5amwuMMnbSnsboEqWC+SjzXuK3CMw8aIxsSrIpevq7Cr/kqBS/APizeDH5E5W0MgT+gnh+i0IX0YaoKL+A'
        b'lziOmZMyT1vwynoKmSRd50JWRQGuWSSw7Cx8YQHJ558K2aMcCwpfjtTk889F63Gb9y8t44xCqdFIZ50YrZ9HrLkNPUDHXgx26EDomHj3A8EOd++k2TJe78pN44bNrdLT'
        b'PRSL7VkJ52aCHefNLV8j4tI3LNE5c6x40g2Bq44UgXA5KuZIGegCvkKLLjx8AHehMmRABlI8PoOv2POkIlxHmd2PseI8uOXJ5tPSA/4rwJWD3J6UlFAtvoivTgfH6cKF'
        b'cCH41BL6gmkY2q+ZLgTepVwoFxqwiLI4M9uWk3M7FnGF6QHfOBYSFgSn+6KThdPJa8PoEmFhG0cd9FR0h7y0bMahh5u55dxydCaHMoncSopVveutbNItTvBlXIr6Ty0f'
        b'C7Vvk4izyWX38hArNM3iRu0Fta+kRNQvlYr3vOH8zaJn8Z+dWBV4PH1hQPbSOa1N3paBEsfPfe7Mbvrg6dxd3DWPLd7ZNuKPdF9U1Nwws9u5YXjTwOXPPJxTFiBDS9Ov'
        b'5+akL+DFlrp9nfGn74TRfx2Osf/bb841/Wflwe3R091/nvfahs3fKMM+KAqa6XXhYGrZ4bdlz77/tvCo1cMP60/82v54dVzxsaW1dnkdmru6DZdV/J+8nd/wX2/O/vwz'
        b'cWnX6lvpMxeZh68q/DdFSvvVpBOOwS7/LlVIaOI+YTKug8QdnVMac3d+4Ca0j0KL5DTeKASJXTYOhOBOObpBgQoul/qRCJE+A7J3ksIHQ6dA8kicGWxUszg2xGPEkwRT'
        b'3IWbZXG4XDHKKQtiTbFQgupR0wjZojx00TsuKZDH8ZcvLeItFIfS/N9rl56k/8EE6CQRGffw/V5HJVR6gELnRSSnF9oYs3q+lWfWCPkdVTSqwdVxuCJutOawCl+znibI'
        b'wWfxAYX0x2Xw5IRiNIFnOEnKsi6IHruef6UY6VdGjPQ6YCRnkpvaOdYpahS1/oYoQENPnL0+cZvSNzV6wG1pn8PSYb7A1mvQ0/exZ2S/Z2Sv/YDn3OqlT8WAruozm6c/'
        b'sp866D6paXbD7GZt286WnWdfe+Q+HXLmT+09H9t799t7Nyc/slfQJNeuenrZjvrQ0j3Nk5uVLVPao1oDewUPLW5bvJH6KDKOiAFdQkqK6l37rSc1Z7Z7tWR3SfunzKQP'
        b'O9VPr9/WbFsf2by9bXfL7rN7P3SPYFWGb2AxXSZB3mvr9cRdDnmvrRfLe8/bLprPofnSKJkAm/PgyiCdjOE3YuhDAghIr0JyP1gkeSm/JceXY5b3z5wxvSX4bq0Zjzfx'
        b'K0hvJ/5YkNcgVnAXZWECBY/CIHwJtScYT75ukzdhjEdfN5Fh3K+0Rl1rOseyVPorLWE2f/TXWIJ/2a+xIDv97v1xXn4lixI/kGRl0xyJ4pGxp0r/21npD4YpwUthSpyo'
        b'n0024/KCtX8nIXshQOEDzqYYZZNDHXr4HnRAu21zuOl933x8gL4+6javEFwLLk3A5cnYEM+3W4IuosPoPGqALxw6rOCW25ihHnyer1408heW1aWnfnjq3TDI6q6Ny+oa'
        b'9RILktWlhx/7cwb3bnfGu23T3oznTv7cylkVHVoXUmafnDZVEL8EfM0s7myX5bdvXVSIaJERH0zFneG4+tWZHWR1V/xGCJqX45PJxmoqviqnTjnQfYTWWm7xcb1/UMDE'
        b'2IDxxVR8YyJ1exEpqFcWh86/NtbRUjeLb5mNEGOc6SaOI44aN00ZU27FV1C9gj/GHokrM/k6sxyVjno60xfq52KNfm6P5MVc8Hlxcmyl8BMneZ/XjAGnyD6byEH7CY/t'
        b'ffrtfZqzBuz9+yz8NZM4U1Yo0hDX/soUkOTx6c8TQPJq/qhMLjxj8vftPu6/t0p4PLsf4Re+In6hRuzFtcgCBP/Q6oUG7v+J1eeA1V8aZzTJhXlqnXbUtNlhItivnNzN'
        b'1ihz6OHgC2ZuchVKedgriybjOvtGJaUmpqxcGyCPilkSFZecmhAgh1Hi0qKSFi8JkC+Mou1piakJi5asVPw4i6ZQKjuH/Fw0cgr5VW6eMJejP6iYqQRAV4bL/clPY0vi'
        b'V8SMpqFCfFSBLpqjhp3wfywqQY3o2k4ONYrNATFWIAN9Y3KlAPR39HFAh53kt8GsXu+J24WodfVE9XeVZzntRugtm2/D7HhmWQ1PcPnIhxvf+8a+8T2FhaJ8pcVNi3CL'
        b'xnhV+ZJPfN6blqqI72jZdcpldsNmF+/9lwNWxQ/MalB+vtl1i0tZTUJ6dP1yXP9W5S993rQ4/Rn3Mbb9znKbQmhEIoWznx+AmKEKfiA+4ECRz9ww1DMW+OC76SaT3I9b'
        b'qE2i46gBV405nEC9Or4VeReTNuegB7g4jiIrXxKYxJzUhY9aUJWDQvjKYEr2YNRMhswhPdQaKzpjvlMjTmNGPLxJyjm4jFrtyzV2arzzB5wW9Nks+KFiO/Rp9hxwmtZn'
        b'M23Q3qVuTs2c2nl9Fl7/V6YdRUx7jLC+Y607QfrjrFtDIgtEe/KTtpkyfxbrURmuCkalzAe6LV6+V5ibgztfbftZxPaFpohPfpVtrEn/a+2flDM2vliTHhv4afE2X7mV'
        b'Js6viPckbSavDRSq4AbggvEROJZ5gTylTgdZcKYSgvd4phQGKLNY2ful/H8cr9FawD8qBbDU//8fHCJJpLU/QBj30n8IiKBKjx9OlpW4mPo9NN8FkmXOJiA33eN+kidH'
        b'a3FbwFfVkHcpppF3CghA4c2mLyhar57wIj55AM7vOUYxApQUVMGy3MXEq3JrssCrHspZzKnv7XIUacm/kvHrL56xWvTF+rtty8fglniLxvcaC/eYJ/c4CKJq0qcmO00X'
        b'iBe0y8TXu9eEpBK3WL5gZ1H8tw7Z9dIFzwrRkrXLP8EH/s1zVax8rUy312nGBXW4heRZ4QUe59DvpP3qe4WY1apr8ANP3I1u/xCs2YXujdA3+Y6Cn6sk2aIxV0yiZ0q4'
        b'EpxjgoibkYhPrRLvQdc2UY+6FzVtfe5RcZcePGp3Dj3KDZxmTw6UnyOg7G0EA+2wowfKyJAWPz7RFJtRd6vZSlGY7STRZnQt7mUBJqKjQtyITqOj4Kh+MFEhjmpMvdyC'
        b'wg/QcWJBu8ZR1MG+xhkr5uYvoCSSss0esJ7YHPqhtQ89oQztdw7tmj3gPL/PZv6nnorHnsH9nsEDniHVskHnSY+dA/udA9uzHjlP/8TNu89n9oDbnD6HOU/cfZq3DLiH'
        b'doX0u4dXSyifoH7noPYdA84EaI1xvmZDMuJJ0wo0BC79/cSMFdvHnAtoEohDHje9WWNc8rNt4JJdf2wiViuezJ2VBQkUgsTEaAUvWsFPjFa3Fn7L05bD2n383czDj54l'
        b'D6S7mA3P+KxZve5rP4Psmaev1QZDae8t38iHTr6J7fybevnQjU8vGwTO6/aq/xbzcKd68xdDswfuJn35H65f1G4Kqn1rReDnlZ+vSHo02+encWEtpWtSL0eel+xc8FmB'
        b'U0aX/uuglIlfqDIjXLdkXH6/9M0zp5TRn3atCr3rVb9WWvP4A1dNX2v1zv8yV4RGfT3d32yk+ReXDmV/VO63rifpXu/SBU0rfrdpx6dLQpZd2GrbP3V56fVDBzQpfctS'
        b'+jc/6lv3Te6Ezz/zCOu7Xb/0PzN5Gw3RdyRln9kFnP951+mrbyy7Y97xmdvl83/smtdS2GR5/TfRYf0Jg/Gnrh3OD//94JH/uiGa/YfEP7XevVbc8+4fNt3o3z2YZN3c'
        b'6LnYbK73V9a/l8wtzZT6qP+s85jaO68keSTs/b7uyKUfnK3d9MaSocP5u2IT96yd94Wj6/3SLSN3Tot7F/71Dy33/3CWNzJwqvf4k88i/ly42/nZHzix2ubZZwKLfmV5'
        b'n43nh133Kt/5w+QnT0PO9LW5nP9gWnTT70UV7/7t/eqBt98bOsef+DuXt4Wbfue46feWv068e3TZhqrP9k+q2X4u9D8j+n8VtLjOb/Hiknbl06ZPTsZfDcyw7uAFzp+R'
        b'J/tl8ud/0i9uHH4i+vXhj6oHNry1WbBrv/lHu+wzd61R/3ZnKw7KCH/9q59nzPvWP2nqyq/fe+37X/qGf3IkP8XtoyOPv/jJ9yG/OPnBrKUeMz/6989+lvIfV5YevXl8'
        b'j+NE80eR13bJkooVW+70nvil48Sn0qanooE9Od9tKSqef+Snc/0iNx7/7e91v/lye+ndK/M++2LVF+9tmP/TDTu1jo7vfdzw1+nzZ//5Z9kf/NvX/xHm+XDCQ/OR7RWG'
        b'6Jb63zR81zz5+0f5Hd/9ZnXG4MeKIw5XngX/9bbzRe83wdXRI5hmfBpfA/yAy8J5HC+Sg/hwH52nMC99M828uvUvZV7oLsC8ySyonENtL7tJD3TUWFULZq+q9KBW8oMl'
        b'QIMVgfhklJgTb+JPFqDbLAesRlVq/2WB2BAbn4i7lok4GbrGx43gynpoB8cUXB5HIhd0weWxAS6kRycfX8IPvBQeP+4FFskPXX70azCvdDNE3NHIvIB89o37MB8rSUvL'
        b'K1BmpaXtGv1GfauTmOP+CuA1msdZOg4LzaTOxKmGlm2v9yp9vUHbHNqsbAk/tat9xcm917y7NL1e1/S9K67t6A56c/E7djjmw9D4T1wI0lU2hJ+SNi/rdwnqcu53ieyb'
        b'k9jvnNi3MqUvdVX/ytUfOq8myNauNr/PxntYwLms4Q2bc3YO1QtrHA2LvhSL3cwNVsMOnJ3roK3LoK37UzOhq7nBctgqgedoPmhh02fnMywg3z+1sKkOHhaRr8NiztIW'
        b'CDNKSBghpYQ5I2SUsACiz8532JJSVpTyHramlI2xzZZSduwxe0o40KbAYUdKOVHKZ9iZUi6soysl3BjhTgkPY78JlPI0UhMpJWcdvSgxicnxdDKlvFmTDyWm0CbF8FRK'
        b'+RrlUFDKzyi+P6UCjFQgpYKMzwVTapqxLYRSoWyA6ZQIY0Q4JSKM/WZQKtIo8UxKzWIdZ1NiDiPmUmKeUar5lFrAMzJZyKP0Ip6RTRSjFxvpL5cwOppnFHUpo2NMdCyj'
        b'l5mej2N0PI+NncDIRCOZxMjlRnIFI1cayWRGphjJVEauMpKrGbnGSK5l5DojuZ6RG0xybWT0JmNzGiPTTWIqGZ1hojMZnWV6XMXobNMy5DA6l9Ehw2pGbzay38LIPNOq'
        b'bmV0vrG5gJGFRnIbIzVGUstInWlsPaOLjM3bGbnDSO5k5C6T5K8x+nVj825G7uEZt3svoxfwjd0X8tl+842SRjF6sal9CaOj+ab9ZnSMkX4ay+hlfM5+0qCdz6Cdgl69'
        b'TP/5fLmW9jBIhzfwOXfvpuCG4I/d/EuWGaKqHQddfB67+Pe7+H/sElgjrOZVhwy6TGiybLBsVrbbDrj414jA07gGfeoQ1OXY7xBhWDI4YWLTuoZ17aKBCUGG2OrM0sRh'
        b'KeceAD7B3OaJ1KY6s17bHtWV9Ug6+xl/rjTsKQeXrwSc+RxysRkWAkmWgnaun9ys7RI+kob/N99W6kI6RBh7AQkm7Oxat7lmc59XyoBTqkH2qdSaDJDcPLl9cZdjl753'
        b'1RtL3vHp81/+SLriGX+K1OUpN4VxWckzsgGaaLZRskdStxG+hTSANLobewAJ/mZsByvppLEdgASnw8RNfiT1+ppvJ51J2mgvm6dCIL8ZzpTwpLG8J3YTz1n0BUYPyJcO'
        b'2MX0WcR8R9+XK1noEuvF/czLPjbMeDphM8RPS/tnjyT+mfhl8xwmj49ZmlSCl0fDFYn+2nlGrBzF4/FsnnFweUouPxY1N4oDuSuySIF6hWWgSPsTuGMZcveU3y/ff/T+'
        b'J++HNnodDjnsVdxyouWIV1kDT3Cs6401Ha5eusBMy0yn2RfedZjifTPe5qRtxqw45zjzqEn+Uw+9/fFbn/zs9FtVarTZt/Ed8xsLbcrW9/b9Cr3DhcW6lK2vX5Fi+F1P'
        b'xxpJbt3iS5FO9mtsphSG6qbpu4q69IU6SdG07RK9oSimqEv3ju4d/TttTy903SzUhehDRdN9px+LeWOkY5pDCW/3B31vlf8qWHFZ8tVk110WP3f1q5/s+q7rzAGeV4Xf'
        b'wMpwhSXFLisFOlRsRv+5vyRcRU8RZeg6H7cnojraIQs17CGZ8jXSIykwH9JDW3xPgFrQucUUh/EL8QlUhqpwFcnqUAWqMuOs0F13O4EnrlfQ1HImtDagQwFxsQl+CWac'
        b'WMiX4IbJI2RHp6Fm1O0/eSugKl4ch+vRzaUj5Jd/W3D1rPHlgHXoGHlNODgOQFwlYK8qAbcUXTNDVVvRgxHyahK+ocT3cBkqnT++iiDmnBcL/XahHoYJO1ClI01GCSfU'
        b'RP8tQsrNHZ0Sogu4MouVCK+hUnySFD3jcJkZJwzk4at70BXc9jpdFp81+bhMQcr6VaQcweOsURu6vkKQig1OI+SfwYlDZbiBdIlGxaRXABGdFl95nBzfFHGAbKspqwRU'
        b'h4/j7mn+SQG4lA4Ie4Af8PGtQLMRUkLDJdnkB8W4HPBlsN+2wDnLGYx10wvRkTRfxaQfxo//EtT4L7xoJ1EA+hLufOEzCkPV+Wodg6HsG4WhDzh6IvmVGyeyH7R0eGzp'
        b'2W/peXrHgKXvvuhBoXlx/P74Pluvc5GPhAG/FFoC9HPz7BM6DfPNRet4v5S4AuLz9H08YXr/hOkDE8L7JG6DEqsqWYnskcOUR5KpgxK7xxL3fol7/cJHEs9Ba9fH1lP6'
        b'rac8svYdtLCrSixJ7HNf85HF2mfiLULRzGccuQ6z6zopZ+GwL+mbkW3wxflLji+aNujoajA3su9zCPpYAnAUbhvfZBYu8uOQn0eUVIAlPLgynzlxSJCnyh8SkrdmhkT0'
        b'PGFImKfW6oaEWepMuBYUQrNAq9MMiTJ26lTaIWFGQUHekECdrxsSZYP/gz8aZX4OPK3OL9TrhgSZuZohQYEma0icrc7TqYDYqiwcEuxSFw6JlNpMtXpIkKvaAV2Avbla'
        b'q87X6pT5maohMa01ZtJ3BVWFOu2Q7daCrJkz0tgBcZY6R60bkmlz1dm6NBWpAQ5Z6vMzc5XqfFVWmmpH5pA0LU2r0pG3rYfE+ny9VpX1PBZoiWan/72PXM48e5bpQv7Z'
        b'Sm0SXP72t7+RF65tebxcAfHr46/D9PpjvDwJXm+aiRc6c286yxZOEnwnMf1SYMgmLc343RhZvnPLHv+v0crzC3Ry0qbKSlRIyMvmWQWZMGP4oszLg/CXZdRlUsOB++aw'
        b'uBqddrtalzskzivIVOZphyzGVlI1BzljCYkVk5gtzGH/2u08DfmhFyma0/PAYQHEtqd8IU8IqYvMcp/Zl+JomPDwSnNOamvU42Wg1X0B896cgn37A5YNSmyemDv1OU8f'
        b'MA/rE4Y94WyqXT7i3OhQ/we/Vxo/'
    ))))

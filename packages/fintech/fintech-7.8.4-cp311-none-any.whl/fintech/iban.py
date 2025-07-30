
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
        b'eJzVfAlc09m1/y8rCWHfdwOKEEhAQBB3ARd2UHFjdCCEICgCJgRFUXGDsCkiakSUVQUUBHHf597O1JnptMGhldLO1Gnn9c10+m/pjNM6ttP+75JAcGk77zPvvc+L8UfO'
        b'79577rn3nnvO95z7S37DmLw4hr9fVaDLCSabSWc2MumsbNYBJp2t5LRymVe8stnnWAxzgWWkVRbZHDaj5J1Dny+M1yph1BZvsNF9fjZ3cv19LHTXTPkCFxaTzVvJCHMl'
        b'/Oc55nHRUcniLYXZmnyluDBHXJyrFKeWFucWFoiX5hUUKxW54iK5YrN8ozLI3DwtN09trJutzMkrUKrFOZoCRXFeYYFaXFwoVuQqFZvF8oJssUKllBcrxZi7Oshc4WEy'
        b'KE/0X4Rn4lN0qWQqWZXsSk4lt5JXya80qxRUCivNK0WVFpWWlVaV1pU2lbaVdpX2lQ6VjpVOlc6VLpWulW6V7pUeJxitu9ZZa6cVaM20llqu1lprrrXXWmiFWkcto+Vo'
        b'bbQuWgctT2ulddKKtK5avpatZWndtB5a2xxPNO+CXZ5spsp98lzu8hIybKbMc/JddMdr8h0Ws9tzt9dKZupry7Yx2znrmG0sYY6EnawwXVVL9N8eTwDfoAorGYkwOV+A'
        b'O5rGZrjb880YJtMi0iWS0UxFN21lhbAGVoFGeUricqiFdSkSWBe3KlXGZ/yWcOF92OJEGre68hmLzKdsRpyZf4oXzWg2oJvg0BoVHBRaLo9FPGrjVsWCXn+olWbCwfgk'
        b'eGSlAFbFrkI8D8HDgbAqBR6KTYKHVvvHJsJDyYkpq/xRgTYY9bY8Nn6Vvyw2TsoCPVymGFQ5RviDvZow1AM8UwJaEPPJLBDPmuDlsdIEWIu6TbReAavjeEwJOCxc775Q'
        b'wTKZDivjdNSjyzHLSjQlZP24aO34aG0FaEXN0QpaoFW20lrnWJG1Q5pdxX1h7dhk7VgvrR37pfVh7WYb1u6VZeNrd+DFtRO9Yu166NplpJgx9VxXBk2/RcuiXQy5uTiW'
        b'wzyLwEPMzC8ThNGbe3ega7ovupeZ3y7eQ2/e9+Uyv090YphFmYkFafFMN5Nvjm4fn+OSP1v0Gar8id+X7GshM9nFTL4QFfy69CSr36yVz1mUGfpLVY5vB709svZL60br'
        b'I/H81Cesv6+V5yqYUUYjw4pQV1iCVgktir8/rA6OlcFqcHYh6E7zR4pwWBoUJ4tPYjEF1sL5EnhVEqxxxkt7HXSCJtgN69QWaMmgjgHHwXmNxhGXtcALSXBAoFbxEFHD'
        b'AG0wuEhKpseBDngaVKpVSI9hHQOqYZOFxgGVJFuB8mmuangNt69nQG0ibCEF6bAXDM7crQaHkB2EbQw4nRpDJEBtL3mDe3AQFbFRUTsDzoBTIirBLdiK5Lm9Wb0Vi3AY'
        b'VbbZRUtOvAHPwYsZajiA1gkeY0B9wRbS0YYkDbywUK3BDY4woAYMwAbSpAxWwIte4IjaErdoYcDJ7bCZNFkPj4LykmVqOIhlO4F4zZCSgiBwMmMBRw1qcY/NDGjaBbWE'
        b'lyW8bgtvwAG1CIvcinhJYDtpUgZrokBfvnobcgfwONqcSnhL44TbN8XBikJwR23N0CY6sBc0aVwwVQHbYD+oB/1w0BKL0MuAFlDLJV1x0XScdALXRWQVLuB2DTGkKwW8'
        b'AtuWg1OgBi0dS8CAvlhPuqi1sAuemgb2q+FlvKgNDDgMr+UTdrPgQRZsCoKDGg6d7EZ/tEJYQC+4F16NhpdEsB/3dAmtgxWoIo1Akww2gfu71NvYlF11IbhBGm2FnfAU'
        b'uLVHDa9jwU8y4AioC6FLdCdyNzwCj6mtDcvatAKcokt+VwTq14H9cFCAizoZcAp2gku0qyOw3ALU+qMyLMV5JIW5PxkuvJWR5bEcDhbzaEeHl4BBUsBzUIErsA4OWvBp'
        b'i9NmjkQ4cHQ+uJa5ABXgWehCrOA1eJcUOdoHwD6wDw7CASx3B1J7OdDRhaqcD1rhqXRkU3GzPga0ieF5ItxUeBjcSofHUZFhitpnpRAZZoD93Bne6D6e1X4GdOSAbsJt'
        b'GaiF12NBA5pwg9odcYQ6OkGHlqjg8UK05izaqN0FNcIl9kvBQDI8iKQbxEU9aILmTqVTd1C0CnSsxiVmVFHOoFEcocveC8+DW2pwBq2gQfLTZvAGndYK0JMDtGkiAS65'
        b'xoCz8GAmEdANbfP2AHhABC9jjleRGKDXjhSJwCC4DHoTRCU82tdJuBfcIvxsSoNB01YRvIZnbwB1hJzDXjrpSDcOgW5wARXiEQ8iXV7qTxrJ4NmVCxh0n0c7akNS7NXY'
        b'oRLOCq8NSF2LsXBaJOxyBw22wUUWs4PgRZGaSydbByplhNGaOHAJXkRdmOMebjLgHDgWpHHHntQSdV0TAevBVVDLYziwnYU2d18KuLmElIOrq2AdqCmBjaAOVPMYbi4L'
        b'dpeCvXDvFA2GLbmgI95QHGpkIgR1M/3ZziFCCYcIC6rjVsAatNCFCljBFJaBDnJ7FWjOSUCSZsETyIZkgdsbyG2rDeBOAhIzGw6CdiYb3AqhC3kFHoA9sBrunRg1OL9C'
        b'Mx2X9SKDfAAehVpwISKvBHTz5EmgDnZuigEd6UnMTDUPHEv1IHoX6geaYcMiNdkUVQyoBBfDNQFYGe7Do2kGFrBeBvrgMdhIqJngAjzGZTxgHVcILsKbVBcPIz7lweZq'
        b'eIVFLfch2/Uaf1QSOa+UsgHXYDs8CLowo1jQN84H3OVy/GA5EScTVrvC5vwJX5IMrmskqCAJaaxxRMjuXURDnJDnIpWngcvfFEO19ZYM9jl7IsOL7cMZBjSXwVYyNbB9'
        b'tgAejQUXI9aAe6B7nEkolgsxkXHgDWUamfiVC+AdvpNahZWnkgEHrIo1gZhDgyuySgZJ+sjMgjvI/1RtEolhDehabc/Ei81E4C6y21gHZ6nFsA1UTDjBuakaKbrvA05y'
        b'xtmMywGbhUg16/DNHiyQTMXbmh5IV/waaAXVoDfYxGueRGYhGJXNBXfgAB0XGlQdJ8sF7CWCbUKOtgmtPKhBCx8Lb/Dh1Rh4hsz1ZnBeMRU0IBtPbAlydWU76Bx1IvW9'
        b'Os7NsFxcWAmrVjDucJAD++G5TdTW9SL3eAVZxYtqczZdsmPWizVzUJEZ7IM648qj2SVjIquWgu7ThetKwl1cTOJnJTFbwSUBuIlc2HnK+TzsFaAlb1GDai41fM3i+Zog'
        b'PBG30bjPYvn6kHw7oEEVOMhIVsFjoCIHbbsmJgS28MAhqwwy1hX8dNDBNYEVu0Az0U40R+3guGEdVvhQAal29lDtPMqBd6SORK3mJKMxtYNBtRUeaxNSz2WgnEyZameM'
        b'gcf6yVulm6pmJdcMNs8jomzzT98JD5rgGFCRQIaVaInmkTLZVoiYTEyYyW6ZuZOHrOgpQK0yrHhTBnVyE+STADrpHJ1JjzAwS0sz0XPEpY5OPeYWCg/zQKtlNDW8x0CN'
        b'C6iCVyfA0hbQRWZpmcJvfCX3etMtbFxCOsBermAqPE70dAboikW++bIJtALt8A7RU1dYnmVU+nGhENNTO9EmJgMme1mGTKsaDORTTajKCwRnQRXiZ0Y9dyNsWkjmMg42'
        b'F2+wnMBqyOI2kn5gBTIRF4w99eCekOMsjYansIKACjFoR/s0Cd41C0WGlIIUzzwEFm/BMxP4DuzNpMC4arvBhkWwECbuNmz6TXB/un8EnQE1aBHAWtRlPxEMDa5vTXGk'
        b'CSL0iiasFlpyjVJdGJ9Fiz3GPW8Y/XE0+j4EFYlXrkdeuTEddKmpyz6NEXb1ZmKinCLS4aXYCRCZ6k5NFMJaC4y2u1EEesftf4wYeTNsolLgGbOgIoRsSReXQJsL8jqH'
        b'JvAZvIDKZuCR9C8BZycsi1Hwu8hjN47vbSR0ELjN2wSOmlO9bAed20AP8sjbeFQF6tYXkI2SMyeUMvNGgvS85FP8OPA21IVTJvtjeaB5sSkyvOBCnEEUMg5Ga7cfHp+w'
        b'UTPxfuEiG3WNAwe2wgqiPwvEqHKlA+LDoii8EZmJK1S1OtZAvJvOTmBMcD2DatCgXD2xUreM+7H7xf24lQd0O2ETMfWgj8usQQjKmkVRafOaNzR+2AWAYwkGc3UkcoKF'
        b'0edwOPASrAQUIqagsKR7z2oTaBsHTpKpM1vgaHTpaCouvbwHO7hmMzYTJqtgh1scQlQTGNgb9JBQfMlmcHTC69RN2ocRXHDZIilqMeidzmTAVhU8JoD1pUuoRz24SroK'
        b'TfsEei6CF6nZaIJ3o4WlyD8Tz4/U8Dg84U/GLQX3EWQ29HYM/TO6y00xYh4zE7TyQIstOER18DTcvxQezkdgGy/3WTRwcBfcpPmDg8ibHjUs+F14waiIpoaWWOsweIqH'
        b'vEA3AulYaGHOWhQY9ZkAe3inTBOChe5BdnfQuEX2rTRynNBIDpoLy03hrOU8s0hwZDWRcRm4AWqRNTtsGhG0L6X6chIeAtoE4s8QE7r1ENPeydhrBagz84ZV3gbL5oyU'
        b'sQ3FKhQ7o0E3bU8hU7dj2/rxTXd8PvboRi7YkYeBq8i3Qa2ErkDnGngrKhMOWplRnNuBhOkgOwWtWAPoNM5cqKnu9dCdMoCUD/QnEEYa2BiEIr9rCGkSh3IZAeOSNI0P'
        b'lscKdW+KVggkMNu+AnnIfWjTJrDIDoAXZG+kvwEHt7LpVjtcrCJyIIVEEIm2n8F/eQuASg7aY1XgKNWFi6BvFryHLPPgVj41efXJ4LJmGiqLhQO2L0ITNh/WYWRyHe16'
        b'tDHKSVAsh9WL4RkUGpuEaPA08g9YM9yLQMsiNNSJEA3ep9BxZwlscEg1CdDQ9J0ks7MYXoQnQWWBSZA2H14mWzNQzaEywUahqYnoo3Pcj+Z4MThBxEIKdBUO2sMOk4AO'
        b'GfhqustuwLtb5OAAKjPspYbsMrqQ3fAyXci+CFjHpopKLMqVCStyBd422F+dBdTJrBEbHgUZR4PQ1BJzfjBw3AHfD5y0g/pMYGcIbOKBM1J4mOrp7RlI6LoANJVXDTvp'
        b'pJeY+DOhzAjyInJRPNY3MfYuU3ZreKBePpVq65U42CPFMbAlm859K6hbRmIO5Ggug2MGdvPWGfYONhfjfis10Wx2DAr6sJrYIM0tR7GiziQC9gSVZJywBxzYYtCTATvj'
        b'9u59cdbCwH0eOOwOzxGGfrAKXAhG8HfQkkfD0g7QgKIzsr9PR8Fbk/wgW2EQzgbJdiPCFmjDWdzZ4NQi8+TVPoRfIgLKLfNQfGwSh4MuhiwoaOFi3In5hSB00/2SOZdw'
        b'4HVQDmsp9m/ZDs4FICUwidvhFXsK9dq32r2EqSKQqaozgD0DqtDwirzBBboG3bnLY8EgivP5lFkzvAcvEcMDziFoXU8FS7d8yd+5w5sceLnsDaoXnchWnE8QmeQL4M1M'
        b'siN82BFGxLh52yTAaAge73Ot1pjRBBUS8mgU0IoEfBrWd8KuDCJLinx8yu+WmRqNi1SUPg4y7rcNaOEG2IfC+NMFExmKmbPo1kGjWWqYICvrCfRmolRSs1kc0EdtTxM4'
        b'jHbkcXhcVGxwREfnGTM7WtC/wM7eNNPRaUQS18FBtFp3N5ukFO5RyeaDy+AWuJcrKsH8uhHOjoHtVN8PZ6A9a3BCyFS9Yldjw3h/E4emgnB46QI7RSW4iwsMOIGipX3E'
        b'n8G93rD81doJBtNhHTywCXakMyKFajMOsloTqRqcRLFTuwKcmEjQ7AAtBEKys8smzH1rjOn68ewM8dVFFDsUwEo6/p7V20FbrGlC5zIyjsEk0D1vnP6JqB3Bxu5dk2yE'
        b'DBzlFQeimSGreRs2uc4BV01yQNm7SEdvZKFBHwd3TLJAbHiWNNroBW+oQZ3ICivAHQZxbwYXCYCQojHXGmUYQNHt5BDN1O61IUwCz6JNj7eWyxYEosaDCFwNobO2yVaT'
        b'tzWclSowi0hcTQPKGyFQOz7cN7PHV/QiLwstRRIT6swDtVt20SRLF2xFm9pQu3UrjQkMCkCzGuAyl4v2BuGtARWZhsoK0DVJjF66q6q5AnCqkKr9fdiMJSE6cQUhse6X'
        b'NuFcDrzLjSWLpAAVxmyPCqffJpkj0/k5ijB52EyJgLh7J81cJegRWWF/eA+BKlhrRsIfWW5ZGdpAcMCwFduiQC9ZIjNY+wZsSUcluMkNDFUubyEly3chi1UJqkRCNl29'
        b'8/ACTeLN0WjQPB0WaQyZ7RPRVlTlroHzUbAFqcJ4fi8daEn/8oUhoAJeEKkN+/SMK+wjvXhxzMFhCxQoEsN3F9uaC5ZERbavlqLbR4HWkNoDvQY0CLQ0G3gihwsG00DN'
        b'KmbNBj7qtlci4RKPvmYdAoQ1ifGwdja8zWE48B4LnBKjAZMtdhVtsfsJsDqRz3iBM+w3WcGbkbN3J9hstiIBHgqeiyBtXaAEn5pZ2HAcEfg5QZrOSpoVmCyLRWt1mstw'
        b'F7GQOJfA/aUK03NgfJ5DDpvwCcMxvvGs9ASjZZFzMbaWIWdjHK0oR0hOxbhspor/wqkYj5yKvXBWhu68cIrMYnZzd/MMp2KvLBs/FdsoYX8yhhbSXGzyisFnv2qxvIAc'
        b'+opzClXiEnl+XnZecWnQpIqTiDh65BywubCguJAcHwcYD5zFeYhbiTwvX56Vr5QShsuUqi2GDtS43SRWWfKCzWJFYbaSHEBjroSfWrPFeLAtVygKNQXF4gLNliylSixX'
        b'Gaoos8Vy9SRe25T5+UHmk27NKZKr5FvEeaibOeK0XHq2jQ+9s8a5BL2qQVaeYg4e5sa8EmWBlLbCAkbHxUySIK/gpRHhlwJNjHJ7MR6CUq7IFReiSqpXdkTGpio17azY'
        b'KCaayn+/n2J8zG/gFiRO0qiL8RjxvK9MkYWFRESIoxJTY6PEoa9gkq18pWxqZZGcCBaAPwWIlUg1NPJiJXlqIDMzTaVRZmZOkvdl3gb56YwT1TKMRbwyr2BjvlK8RKMq'
        b'FKfKS7coC4rV4iiVUv6CLCplsUZVoJ4z3qO4sGBcSaXo7lJ5vprcxpO8LU/9wmAmnQTzmJdPgm2TlxKjJgFXNxrzbOnI0FZns8kZb1axK/MwayM++J13bnkkQyoXIxt8'
        b'F9SgT+tAJ2hk1iXKSeUBM3NGvAWZb5vM/BThFnpK/DzDmnHIWsgwMzITV1nGM8Qgzg6DHcY0UQK8CU4uhUck1oR5GuxZaiyC1TngZCrtFJyb42E8hcychnzCoJwetVg4'
        b'jB9BHnYFOksKTsK24tMww+kjLA9BXvQcoAkYeDQM3jAeP8J+EQLsHeA8jYZqENEiKuKQaBqfcCBQcwKeJxK48xaIttJQa8VacArF1wdocq1TCg4YDy19EK8+5TpSILBG'
        b'IY+aT0OeQ+6gAdbtMBxEabeNn2XGgGYE8Q6AswTvKYEORV3jp5n3kLNrhFdsKBasg8cKxo8z0UQg0F0LmzW2qKw0IENEZucaM38BOLMngUrA2wUHyUhPodlxAvXTwWki'
        b'QSkYBCfU28xINhDqwHnkMyq8DdgetoMmY+ptPYqCq+Fe0CbhEI+1aAesH0/LtYEjoHoGPEqn9QRsXjnR24AU1IO2GDJzCeAMz9jZm9vRaJtdDUe07fYTOcmbsBfUw9M8'
        b'CZvInpMLB8YL16CVqV/tTbNJ4vDxI2zkiXWgqQBcJLomX23GdPq44Aca8h3L1jJEQdA69a8Mm8HF56eMo1PWgpS8ws/msdReaPovxobWrbibDGfYLMgoK9mQ+/Y+G3vO'
        b'HVbhA9GMGa1/8OMHhNywW9LlaesxN+uDRt/gKvsV5ws8Jcd9Av/y7S+/+fDbGxk2g9GrrT8J8t7WM/bTP/3xF4LnKW8tX+/wxZT9l97b6noh9dLU3/7RQysL+aHjUVXM'
        b'P3y+WNffty/Gc8Nx2U9OT7seXHbzlpXnma+tbrMuOUpb3/rZ2GppZq9Np41D/IZbB3LDHbOzvtp74tvAuId7hHXxB/gf9pvlrfU+c6en4Mu/Rp1+/7Nzy7fN7Zr77mfJ'
        b'HX/IinVuiCveEPpjd+/P/3rm4HvrLTg/+fPg71x/uPZox2fazW1egZK577+1Ol8+eOqHz7/qT8ip7Tl90KVh9ud3lV/W5t3/OO36B4cSIwI0n3xj94+PfvnhFEfn7MP3'
        b'xiRmT7FCBMNW0Bgo84+VsRk+aGLPBcdk8MyUp/h8EXS5giOBQXHSAEkQPCyFVQikirnRcPBN0CB76oYBMmj2SAhcnCIDVSkEdoiWsyE+UO176ooZtMciTFIDqwJkQSzE'
        b'fh8bNIL+sDjhUwxIxSwcYRoe1AH3QOU2+rBOiSwAVgezmSBwlwevgOPg3FOyfa+AxrmwJkkaBw8xDH8m2xYMWsXAq09xygjcXliSQJsDxBADJA7jCA9wfOBVeAOiyF0i'
        b'GmX7S1RYY7/TRY2fsRGLy42v547zclSFO5QF4hz6RFoQ9sELRs2JR8jAxA6Tz2zM4g10fVbOjKXyGAeXMYZl6Tni7FGvGbF3PjGnYc6ReY3ztItHrO3GGJGl34iT64m8'
        b'hrwjmxs313NG7D3HGDNb79Zp54Pbg/unDfnMGvaZRW6NsbmOviPuvo/dZY/cZV3ZQ+5hw+5h/errpZdLH9g9WDk0K254Vtwj9zi9e9zIVP/W8DEO4xHPevbE3XfYPRwJ'
        b'4eg7cRmZMk2n0WnGOOjzs2fPnrj66Fxbw7rMhlxnDLvOQFVsvUfcxbrwEWcvTPiNeHm3erdGtU5tzq1fNmLtNMbYojG5ebfImmQng5uD683w2BY2LGydOWTvP2zvj4aG'
        b'WJDWfqksdHUxXp/grsd45AafcXI7kdGQ0Zo25Bgw7BhABopa6adH6J3xm8iJBuIy64mj6+SaXFKzdbPeOQS9xyuGPnH1bJnSNKXLecg1ZNg1xGQs9s6E0C3rWqD3mI3e'
        b'5PazEVtHskS6aTpVK0unavbvCtK7RaI3XTQnN12oLkoX2pirxUPX5emt/dCbFjp46jYOO0x/7CB95CDtShtyCB12CNUuGbE3XXZrVySu5cwRZ+/HztJHzriec+iwc6je'
        b'JvSJg4vOVmens2uM1W0bcpje5dAl72d1KS66Ilb1rBFnf72zf5ftkHPgsHNgV/Ej5zC9TZgaW8K3BLKoSOatSPNoPgfwWOiKT24ZicUoF+vhKAchv1EzA44a5WLgM2qW'
        b'kaHSFGRkjIoyMhT5SnmBpgjd+efbwYLBeAGhEsOWUGFzrsKm21Ttj+OqR9DlGX4h1c/jsljT0Rz8ly9PrJy1eVWbazeXi8bYPJbDiMhOO6tqdu3sJ1zr8oS9SQeSypNG'
        b'BNYjAnut6NkYj+HZTL5bnkL/qXEYc0Y4k7liFcXmIMeHLR08AK+HJyCjAWuS4aGUOB5jVaQAlziR2L9osKVDnvK+d0JiciqK0oNRCMViROls2BcOaogfitriSeMu0BGD'
        b'464V8QrjI7b4xTWis3IcOrFp6EQCJwaFTfwcLgmXOChceiHU2cUl4RLnpXCJ+1JIxNnNNYRLrywbD5dyUbg0wnoxXCIPyJrES6rCLWK5McKZHMtMjlteiEvS/kn4pFJu'
        b'1eSpKGguUqpQCLWFonvjU7uT8W2KEfYiQQJWoB7ztiiXqFSFqgDCTI5Ksl8dFWF5sbg0MnpxEK8MCQyDoi1eHOGrusBx1NJ8+UZxHo3mFIUqlVJdVFiQjeA/CafUuYWa'
        b'/GwcHlCkT+I6Qyz36kBgSR4e8kTcgWJMuThUVqwpQvGEIbogs4bCIn9cQ4o7knzHsICXrFmANXp/LDj/qgdlqxID4qWgJ40+M4tvpCSCs8K4JBYDLoAq0WwEKFvT8tzc'
        b'utjq5YhRzQdHBz1PvRd6uu3oVd39A0dYVitcTrBKL3zik1R7+qKo/lPb1qM3j0oO5rmGpYaHJUorqva2HW87PnD0rPZsRVtFSJ1E11bhrds7yGN+ZWeV+f4nEvZTX4Zk'
        b'WfuAThSAdhusgrVJGoILpPAMm5kCBrnwErwF2p96YQ0HFaAtIYEfFI/QAagz+n83cIVbsDJBwv8XJo0/7uGJMRsV0cfFqS83JYgzT2WoM19qxjhgf2a5mPWRk49+avSQ'
        b'U8ywU4zeJmbEdepj1+BHrsH9ght+D2YOucYOu8ZWxWsX108jXp5l6TPi7K5Lq9+ht/FGbkib8BVeK2qvzUYFRvUdNTMoogojNRU2Qyr3yaKbUWuMpaeG2BsbYlOZH+Nq'
        b'2wyWGIm9mc9iTcMW9V9cvjd7i7G7ThjE9FnN4xDFgwe2gdOG/Jcr2D+RAuuGx1CodBnUglYpZ0PCTHBoK+gF58BdcyYLNljC07ADdpEowTp2majEisWEwF4WChnhBdBn'
        b'OKcBtXxwQFSylYUiOXCVBbUokPACV0mZN+hBkSm8Zh0Kr5hzGTZsYDnBKh6N847vZqlDVWwmHJ5gFTLguh+gpyH5vqBZVFLCZ+BZ2MKCB3HSvgnsM0RMCGx2KAyWf2Am'
        b'tvxg3y4Nxr4bectxwi0eRZgmCbc0cIeK2QaqZwUiX4Pk7EawGxxixQBt+iSnITDuXS0zkW9DToOnNWbchMh5mOcIxp3Hi7m27995HEDO49vX5dqI1ZucaXut6cRmFlf/'
        b'1xmr1ySScOP/9TySIp+IpVYWv5w5ekFAPC+FCoUGeYkCxcuCGnNHS1KjxDEIiqmwF1mMvKWiuFBVKhUXabLy89S5iFFWKalp8GoxSjQeef5L/KKRDQkykU2OF0VDvlQT'
        b'sDImLUCK/ixejP/EpKwIQX+ReAHRodGkICYmQPoSR5MxyfPVha/MgOFBknkuonkvxDUbO7TSohcmEL/+LagwzrGw6GWEgF//HkqYtHjfa+JtHNqZeFjr5KXkscQFUtjw'
        b'Sg87Q/YKHzvhYHMtScbjc55LaCuTiS18WU5uPk25lYbbbU9nYrHd9/hLRCLNn22G94ppzo5B9vPMOhGsJOYpGu7P3FwIaoAWICPCtmcJwYlQwgaGWAWUsCNx5k5api5g'
        b'JGyNDbZLR0CDJT6iCGEiQkMyWTTJ0mvnHobGGcrAPtAVCg+uJCy+3GCT1sIsYpiiTIuouADMAierZtlZUAbgBjweYgkaiYSJsBLUk/PkVPw0amoJvEWYOBeLFvA5/jit'
        b'KP2tZymTlpf1sIdR/xL7snL5weUD5mCGzd31o529+yKrLtx6Nv/0rSlB+2ICftda86ToD79u6k7Y82jkZ6tjHiwSbPvLlx+///7UUraiappqW7qg973/d+vSHx6O/j4y'
        b'yG/n7ExB4Cepv16ZscTc4w2LPw1U3n1QcOvAXTebwBlHytkf9x0qauB58NjLLs7u9tj40R3Pr5q+ds13SBuK+Ps/mjL8NliBHn3Sr7bVlNxrXOh9c4tHk+/UJV+d2fvr'
        b'voXqdV/U87tbp0779u0Gj9YfrQ/+9ndKsxmy1U0HT9XF/qpIN3jFe3Zw3ZavOmTWderYWcHh62Z3rvOWCGhO4zgnhiZfYC/oJgkYGegAuqfYjYNjvtFZoP1FAGREP4Gb'
        b'npIzwIPgNryGXQmoSklxAjoZqApG1WS4SYIZcpGt/LggeIsAJdVqWCVKAMc3wFrJODtHUMkVwE6ofUq+udCX5wfb4aGEFBmLYZewouDBsqdYl96EF5xxLic4RcZm7Bj+'
        b'bnaAyMswCnPQYMzMwFu+ODljBdqSnmKwkpMO9ifAugScQvIBR0gWyXoGZyM8OFci/G6ZGBy5jSdiKFQT0pATuZQdEx8JTEtkUZhWhmCas0nwbed4QtIgORLYGKiNIWhM'
        b'aOmLInGcCohlfeQ2Xe+3dMht2bDbMr3DsjE2x9Z7xMv/sVfkI6/IG/ZDXvOHvebXL6tf9uwj2sTkQrIHuvAxDvqMcyj2nvVzdIrWsCF7v2F7vzGGbes74u7TMrdpbqv6'
        b'fGl7advOzp00aTORgnli7/XYftoj+2mtK4fsJcP2EtOsgZ1WXR9Wtb12uy60erd2d+vUVnnn9K6Ydlmr7AbnvsUtiwerhiIThiMTWmXGFvUhtSU6V721D3q3Krq8O3P6'
        b'hfrps9HbUMOJpjrCdFtbbXXq5sjWbed3te9q29O555F7hN49wpinqp+pxnu7zzGKy7zFNY+y47xly0JXillFFKBiXRjlIKf4Kqj62tzaS7kE/EiNyWr+AVesmQCw68xY'
        b'rCkYov4XLt9rEqFZGMpctopiOBIWTfw776FHs+BEkfFolm096cuF485iO0PzAOTLhdwc9viXCF8Aa/8NXyLcKGE///Ekf7aC+sPXhLE5JAolyMv0xPN/O+5/rUPmvMIh'
        b'82nICxvhPfd/M+SFp4DOxCUvRPEFAfxd4CC8Rk7Tkl3Jc+uwfQV5vsK8BHYiowmrk2DtSqhNZNstAd3IOp8FJ9EHCZPK2mZjBq7ZgIa8/5gSxyGh848z3zv13kwUOA/o'
        b'7sO/vBA6W+DQOdPV5lLFV7dcyn+n6+9OkEeH2+ZOmdsgDavYVSta23/yw3fLe0J1e8M4TKrY9pfvfCHhkXR4Ln6qCDsOa89XuQ7QaU4NdyWKX+5jBySAtYYDABnsDSO+'
        b'Ao27jSHZfwE4anoA8CY4CitIlSR4IkiUgH2JCN6e7E7qwEVyBLCd65CQMh0cmnxCAPtiJWwTO4AtttGkm21UFhODbvxAzHkWQ835bsFro+5J2fQX088sy9kfOYn13rOG'
        b'nCKHnSL1NpEj9p6P7X0f2fu2Zg/ZBw7bB+otAlV48qhN46nwnn5l0I2TKpkTITdGeuPCuqDtrt5MrBWSdouAxcIB/6sv35c1+goDqUZhANNjFcn5l/aGq2X+R+1NDrI3'
        b'PZO268qi/Lxi9bhRoUfsyHKI8d0clXwjOTJ/wcAYjZRcPPOVCbFJlf1jUlYlp61YJxXHxC6JSVi5KkkqRr0kZMSkLF4iFUfFkPKM5FVJ0UtWSL6rLSHA9YeFZszMrZ74'
        b'ODLx8zkqhgB+WKWC9fib7YH4i+ZVictj4aFgH9BpSAHABgnoNgcnS9H/OFBVyoDTfHOEzfeCGg3OeMXDG6DKtDkyIziTtRCeYbxgFxe07wTn895/fpujzkXVN/P2U+tR'
        b'yuJE9Fto18DSDT86/SOJhaS2N7GhaCC9wq0i+VzoOz5/t8s5cM9h7cfnlLWLTtfO2G2v8FtpyYl+zJ6ef00T2vG7HuVFuXRp+AnXj37p9g7vRxZrmZ7397tGfsiMtThl'
        b'sUYlXGIt+OAkbIL94JbJcaEMdkY+nYJHfh6Uh1NbYDAEsAveocbADDaSs0Y0uup1G/AIJw7xrNi+T/FGWwT2eiYQ3OrPL3mTEbqwQVs6T8J9JWzAaj2+/0bNUTCuNmTr'
        b'TD4Ts1FiMBtvChkHFxPz8JpDHGIiFg45LRp2WqS3WfQvjnNCUPVWryGnGcNOM/Q2M9DdE/Ma5h1Z0LhAb+H9XzIlMdiUmIzBf5I1SRL+T1gT1VwsM0uDQ5A00G5jwDQ1'
        b'8HAwqMY2HFSDAT7jtoebu1n8amtThq0N14hu8A8nGE44/scQzicbXjzhMAU55CigQL6FpENegW1wMgQ/vlOkRDcQBpqMNuKo3cmXFxcrVWKFHAGVyUwJ5JFn00OUl7I6'
        b'k3iNZ3j+VYKHJnT+L2EuQbJmPt709zN5/wRywW7Y8ZosiA84RSxtpK8rM8PiFBtFCh5nHIUMAdt2KOqtUyMreW/8C4R82EC+JiCCLeDI65AYHEQfMBrDWGwa6CU9XPHk'
        b'MxaJV/BPlVi8u1nM5L11rpCjLkIlDgt30pON7hdPNhItTv/odG67JPHnmSVHcv0+ZE/7SFDeN9XF/3K58NR733goF91x+/EXWdwexTvngg66/nRx6+3ZR7LX9d84xYMf'
        b'XWwo8ry66H5w5ts5yBDf+sXsD1lfXvXYWOkl4RP8lv4GOPPquB+cmgUv2YLjT/GD796gA54xhv4YYaGNujMezzYyxEk8ZlYyf3dQGbGvO3PgMaBbZmq6wxCKw+ZoAzhm'
        b'HZjCffE5jzenw8tPxXgFr8IB2C5yB1cSXk4bHAPXnuJfhSmwBRUJRhkmJJgCGrjg7GZ4GrZkIjv42kAQ20GTExgLgqaQxuP9tGMSRcz6WYNZX2r+WjRIwuW5Q9ZThq2n'
        b'tIY+svbVW/uSE/fQR86h/XOHnBcOOy/U2yx84iV57BX8yCt4yCtk2CukXjTi7PPYWfbIGT9T4Rw27IzDc9v5H7lN0/vOHXKbN+w2T+8wb8TdVzendfOQe+iwe2h/yLB7'
        b'eL2AcA965BzUtX3IOXLYGYNMEy9gNirCJj2jUIVx4j8Pkem5jsmZlCoJe4ZJEzEH+waN0TdsRb7BFfuBf3H5Xo91jgulzEWrORwJJzl5qYS1VMJOXpq3tvAXLHUrWqaY'
        b'uIa6hv9cY7/c5u1fFZh//tSu2lL0548HFD/kRzikPXVb5ODYnpko1ebMyvwgStplm/S3+r8d+VjqnT2VO2vjnr9+fOqmeqPq467AXMvRfX9unfqZhz38ZrW36Gqa5u1p'
        b'3r8u85sS+1HFp9cv7Qo1//l8R7t1JyvScqaGBX59csaPz8X/FnQuTPhp91fnUg48/Dz/zycfzstQbflTXHpJxW+y735cdkl+y+vic7f9DeHvT/30d93djisuw4BLkpi8'
        b'DwMHv7BwSV98f9g7s6U+OjnyycGUA6JvflNR/pmd/yL52mjb6nftGhuU/n6BT6YHLl+yuqOiufKbT9nSac5tx9fX+n66Qjr1i/7m9XuPfRpwcfrjTNlNqy+g3a6I3K8j'
        b'suxvur7xsHdkaUHKOwOcue/u+L3PNoX1Tee/Pvw2/Snj9nB/5GKvd2y/9D905IdX/7a0WZzy67S11dNPJ//G4i9JudN/8muPUi/nhzW53sGfhP68OuLL6p99s2rLx5vT'
        b'r3g+ftc9fdaDpEf7rS7bb/hUVnz0+la//xjef/uXv4K7Ljvv6nS2flj5mZ/ZmPbpJyGfP/4ZS/Z88YVnDj95+J8u0zIytWVVa7JT//pHh96d4d118UVTD8hrn4R//ET2'
        b'8Sff3vANOPj7nvkNW/eca3H51fYdj8WjTelKb/aKRX+u+UdaWp55zIPPTkx956TD7v2/clEkrz8zR/hw6k+fPTmx67efpvdqdTnD7z7/Rffotyvm35/6wabZf9S0/e5n'
        b'u5dUFdXe+9OVWe3xe7NW/j6+asW5yPk5tVbrvt7wxTbWyqV323/wQ5f/PHR+47Lan8bPC33nt11ZZ7ZYlT36ie3lnOefhN17EvjOnz5QJJf95Mu/d6z9/M0fxcU7zvL7'
        b'5sjtyvotPSqf9r8kfjCmftigrrjjsWPu1/Y3v/Zelv6PLzL2/PjJmMufdh7yktp8AEa/cX6gkEW8pUe2Fm+tufh3LcxCEcxhMaxI/EThwRwS3W7cHjQBaK8j7zRh9W7D'
        b'C0/xFwT9YRvoeNlQ24B7hhPqClBLsLPMA1nRGoR662R8hv8mG1yYORXWwWryFF0WuARbA+Nl8TlQG5eYzGNEYICNTGabBw3Ey1nwZAL2oPCsSIbkqI3DVS6xYQ84liHx'
        b'+G7PtAled/nOT8a90nDhn1YbxwiL8Kt80ovad0FGRn6hPDsjY8f4J2LXz5sZnhgixp3FWDqOcc2EztSYh1Ztq92m864u05bp1Dp1a2irvDP85I7mHV3Lm/bo9vRPQ/9U'
        b'N7yvaG4sv7J9IOhK0IPFDxY/tHsr9gexj0IT9aGJH7lg1C9vDj8pbBa2xg+5BPU7D7lE6uclDzkn61ek6VetHl6x5pHzGr3zGgzt7Y4UNBbobabh58jWssbMGTuH+qhG'
        b'R220NvrZmBlLGMcasZtSLztroZctHRIvGxYvG7KLHbaL1VvEohGMmfPdzMcY40VrNebA2LmO2LqM2LqPmXFd0W100VqOWSWxHM1HLGz0dr5jHPz5iYVNffAYD38c4zOW'
        b'togwI4SAEkJCmFNCRAgLROjt/McsCWVFqGlj1oSyMZTZEsqONrMnhAMpko05EsqJUL5jzoRyoRVdCeFGCXdCeBjqeRLKy0BNIZSYVvQmhI9BjqmEYsh1Gq3gS4jppIJk'
        b'zI9Q/gZpJIQKMDQOJJTUQMkIFWRoF0yoGYayEEKF0g7CCDGTEuGEiDDUm0WoSIPcswk1h1acS4h5lJhPiAUGqRYSahHLwCSKReholoFNDKUXG+klLJNB0+tSlkHsZbQs'
        b'1kjHUTre2DaB0oksKkcSJZMNZAolUw3kckquMJArKZlmIFdRcrWBXEPJtQZyHSXTDeQblFxvlGsDpd80FGdQMtMoppzSWUZaQelsY3MlpXOM5RtfnpJcWhYylkfLNhm6'
        b'2kzJfONsb6F0gaG4kJJFBnIrJVUGUk3JYqMcGkqXGIq3UXK7gSyl5A6jlDspXWYo3kXJ3SyDGuyh9CK2oXoUm+oB2yBpDKUXG8uXUHop27j2lI410nFsk+mIZzP2PiN2'
        b'viN2EnL1Nr59x9axX5w8rXBsPZtxn9YS3BQ85BY47BaILIowmFyq4rUx9Y4jLr6PXQIfuQQOuciGXWQYKEvJ5Qi3nlUfMuLi2WLZZNkq77Idcgkcdgms59XzRhyC+h2H'
        b'HCK0S0Y8p7SkN6V38YY8g4Y9g7Rx9YqqZG0yMknmNiNCG61zvUKn7orpz9YL5w4J5w4L546x5wtnjjHf4fInDmM+D7XEf21qnca4uADNtaEH3dRWdT9XLwwfEoYPC8PH'
        b'2LZClzHmNRfMIwLVGueFC6Yzzq4nNjVs0nunDTmtGnZapRU9EVpT8Ve2Tu1a3O/Yr7mx+sGSh776wFS9cPmQcPmwcPkYezrm+h0uuNcVLNR0vHtcksqamCy90G1I6DYs'
        b'dBtjWwjROrx8wU3dUYVxFrjA45UcrIQ+Y8zLl5c44ALx+HSu1Au9h4Tew0LvMbadcPYY888umIcPqjrOa1IpeRC4KmphtB0D7NyipYajQJtRdkbGv3v+9+8ACpuJSGgy'
        b'iFCtwiHROH6YSvCDMRyKYbFYNjjg+d4v3+sRYqswgrlmFcXl5B2y+wVH/QG6tXzskqZ+oWjUdv8Mm7eDb/6g52yMKPqN5xtz26Z0He2waa6OCRyJur5v458f/fTdt4N/'
        b'Xj7c/oNFYuuP//rR7Tt/8Q0ecJiSmviWpfnDtpzM2d3P7rv/JnfnmrdUqztkHc/EbydV/8Phi+nmMofFj75o7BgAO3IU4b+9dre68+Tn6Tufr5zv6nJt4/+rcjpfqLZ6'
        b'Yx77w6wC3+qQkJvN4g3/8Nx4o/CDKeXvdCc1eoRFxy7mp1h4K34Q1xATJBPmLWFtidUfsiqudX6v9GbTmr+Zv/k3nptzyAPfexLLpxgQmqlS8ZMD4bA6JQWhWPxYgghc'
        b'ZsOuRXCAZI/timE9ztgMwKqUFHAB3sbPGNjCOxzQBvsQhCYZ5srslaAGHIaHE2AnOIbgNqgDh80YKzuOVxm8QbD8YnhuSkJcUkBiSJIZw+eyBfBy4FPyWyEH05ID43kM'
        b'KwFeBncYqFts+RT/MBpvLax4MTsFDgUnICB/CNbCwxxmGRhQ+ZiBw657yEMZ8A44t/zFFnzGebHahRsAjsPLpFbIanCLZEMwp7nwnpGZOzjFBefmQMPXY/pTwQGc7veA'
        b'NxNgjRnDlbFA705QQyYNVoJzG2CNBHHxYdCsVaUgPGC9nLMK1i8jSSJ5SQAtdmTBw1IsNTk0YDFieJWHv+22n4YPJ/HPugSmrAZnpSjUqaHTD++x4XUpPEMyPOCCNB4O'
        b'wloUXAQHbJWxwXEax7hpuKAC3IqR+Lw+gPhewobv8aL2IRHIS4HHC6/xOCSvIK+YxiH0E4lD8ljjjxu4MTz78mT8b8TS4bGl1yNLr9Pbhyz9hy39y5eOcM0rE/cl6m29'
        b'z0YOcaXDXKmeKx3hWpbH4X/IU7p56blOY2xzXjprROCqN74RePfyf+wZ9sgzbMgzfNgzXC9wGxFYHRZVi37qMH1I4Dcs8NML/EYEdo8F7o8E7rqoIYHXsMBLL/AasXZ9'
        b'bD39kfX0IWv/YWt8silEvC3sDidXJ+vd1w5ZrBu2WKe3WPfs2de2jIXzGMPmzZi4jDi6as0NPekdgoYEwcOCYL3xPcZDVXDo4rSZy0Nm/r/5mi5kLByQJSRfX+FxoyMY'
        b'EOEd48aBrix0pf5kyignX1kwysWPEI7yyMHfKDc/T108ys3OU6BrYREq5qiLVaO8rNJipXqUm1VYmD/KySsoHuXlIN+A/qjkBRtR67yCIk3xKEeRqxrlFKqyR/k5efnF'
        b'SkRskReNcnbkFY3y5GpFXt4oJ1e5HVVB7M3z1HkF6mJ5gUI5yicpegV5KltZVKwetd1SmD17VgZ9UiU7b2Ne8ahInZuXU5yhxKnzUUtNgSJXnlegzM5QbleMCjMy1Mpi'
        b'/BWbUb6mQKNWZk/4STW2cJn/7CUWU6+Xbbzgn2NWy1jGgPk1L6TBtixWLgf7rv/L1+/N7WLY8pa5MErMvCW2igriPBcYv8c3apORYfhswBTP3XIm/+q8uKCwWIzLlNnJ'
        b'EgH+/lR2oQKtJ/ogz89HwCfbYFVwghbdN0eqoypWb8srzh3l5xcq5PnqUQvT4xXVfsaQH6aZYrzEzwXz6K/aL1Dhx57wCZt6F7qMcRCoGWNzWVwE8dHFghFZlpuN8Zei'
        b'6RhjTK4rzBmhrcFwxFNjgjY/K1wvXfBg+oPpb/n/wF8vjUfvEYHNiLmTVqp3DhsynzlsPlPPnTnC2OgZm3qXIcZtmHHTG99EvP8PpL2Dgg=='
    ))))

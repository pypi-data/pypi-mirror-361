
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


"""The Python Fintech package"""

__version__ = '7.8.4'

__all__ = ['register', 'LicenseManager', 'FintechLicenseError']

def register(name=None, keycode=None, users=None):
    """
    Registers the Fintech package.

    It is required to call this function once before any submodule
    can be imported. Without a valid license the functionality is
    restricted.

    :param name: The name of the licensee.
    :param keycode: The keycode of the licensed version.
    :param users: The licensed EBICS user ids (Teilnehmer-IDs).
        It must be a string or a list of user ids. Not applicable
        if a license is based on subscription.
    """
    ...


class LicenseManager:
    """
    The LicenseManager class

    The LicenseManager is used to dynamically add or remove EBICS users
    to or from the list of licensed users. Please note that the usage
    is not enabled by default. It is activated upon request only.
    Users that are licensed this way are verified remotely on each
    restricted EBICS request. The transfered data is limited to the
    information which is required to uniquely identify the user.
    """

    def __init__(self, password):
        """
        Initializes a LicenseManager instance.

        :param password: The assigned API password.
        """
        ...

    @property
    def licensee(self):
        """The name of the licensee."""
        ...

    @property
    def keycode(self):
        """The license keycode."""
        ...

    @property
    def userids(self):
        """The registered EBICS user ids (client-side)."""
        ...

    @property
    def expiration(self):
        """The expiration date of the license."""
        ...

    def change_password(self, password):
        """
        Changes the password of the LicenseManager API.

        :param password: The new password.
        """
        ...

    def add_ebics_user(self, hostid, partnerid, userid):
        """
        Adds a new EBICS user to the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: `True` if created, `False` if already existent.
        """
        ...

    def remove_ebics_user(self, hostid, partnerid, userid):
        """
        Removes an existing EBICS user from the license.

        :param hostid: The HostID of the bank.
        :param partnerid: The PartnerID (Kunden-ID).
        :param userid: The UserID (Teilnehmer-ID).

        :returns: The ISO formatted date of final deletion.
        """
        ...

    def count_ebics_users(self):
        """Returns the number of EBICS users that are currently registered."""
        ...

    def list_ebics_users(self):
        """Returns a list of EBICS users that are currently registered (*new in v6.4*)."""
        ...


class FintechLicenseError(Exception):
    """Exception concerning the license"""
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzcvXdclEf+OP60LSxLERUB26KiLLCAvSZiDR0UNUo07MIusAILbkHRRVC6oGDvBhSNFcXey0xMTy6XcjFc0+QuMe3ukivJmbvk+555dpdq1Hw+n98fP3jts88+z5T3'
        b'zLz7vGfmE6bLnwI+UfCxWOGiZ1IZPZvK6rlGzsAbBANbxjWxqZIsJlWq5/VCOaOT6SV6KXzLV8qtMqu8jCljWeZZRi9LYQTG4FY0gWVSFSyz0lMvMyjS3PVyuCrpvQe9'
        b'ehoUa1m9LFXxnGI5u5xxy1a7PRigmJdtUCUXWbPzTarZRpPVkJGtKtBl5OiyDAo1/7kMQPtcTi4CXNrY8Ay2Qwt4+Mgc35YxcKliMlk9tKFcXsxWM2VMMbfSzc6WAZR2'
        b'roxhmdXsai6lwz1AkaXmEzM6dosUPuPh05sUKtCuSWHUqsQ25u/k9bxcAk6SXGDkzGGJIkqrzF/OMZ+Jef829QjTI4S0sAkEQq6KqeIzeReU7GNBmd0VSmfhnaEUEm0a'
        b'uF+NXpSlaPA23DAPV4ctwNW4NmJO9LzoELwe16lxDa7jmZke9vlSfFLFG0Pf/lSwhEK24dq1X2q/0OZmfqUNNoR9rNFFuy3WfaV9M71PRnZmLnd6rf+E0cyabFn89zlq'
        b'zjoMcuBrqGW2OxQbSgpNsGlC8LoIjhmML6ahMwI+iQ+hHdaBkNCKK9So1piO6nF9HKRE61G9jPH04Qfh5mlmN0ih5tu4YLWZIKV4IQ8feE/JNOevNJhUmSJuPN3mqbNY'
        b'DGZrWrrNmGs1mjjSfjJkSn9PVmDNSmfWI3ybkGkzZbTJ0tLMNlNaWpt7WlpGrkFnshWkpan5DjWRyxHW7Enu3cmFFBJACu4DF+/7Uo5jpSy5Cqz0R3K1kcajze74xbiw'
        b'8EQp2q4JQTVJHbs3bLQEH3k+KJeAUunzGiv03uHOFNxkf/BrjC1lKA4tiLRyVnmwyUO7Jv35GX8Pc+DQ3an07TP9l7Lvc+94SFXa527lZ4hZGlM4oLVSjYTRKoMm9BEf'
        b'BppljJKJXCBRacOGqWczFAVQBT4R5I4OhwE41bg+JXKuiAXB4ZpgXB0REpPAMsFjFj8nj0dneTVrGwJ5Fi1Dx9wTNSFxGnQeXVAE43XoJDosMAHomoB2oZ34rI2MpRHv'
        b'EkLRQVSL6iOgyeRbxrgncXgTPhhFU+D6PonkccexnlFCRns+fkHN2/pCmgFoE6qJ06hjEwbjFyWMNIXzVU+1DaCgo5OTR+AX4mh/xsRoOMYd7eDw4XTcZFNBAjnah/fj'
        b'2iS8LhZfQFcSwnFNPDomMD6ojMelcwuhBn9IljMgOS4mLEZDUVPCRLCeeB2fmIXP0PrxdlQ+mLzHFUESRhBY9IJlPq1/wkKjiM4StCYhBq9Xx0DReDOPLocpoacGQZIU'
        b'dB1djRs1OgZvRafx+ji8ISlGwngF8pPxJbQHEpFeQC34NPQApJqMXoxJENN44hZ+JLrWF9IEEigOjkSH3KNhlApwLa6LI41FB4P64D08PoSvolJoC4FpjEEDY3EZ14Yl'
        b'4g0xYeFS6JIzHD6D1qHNtv6QQBeHqkLxhnhcH2WIC1NrYiVM70E83ozO2+nY4oNmdDAuSRODzwwMhX6tiQmLjQiPTpAyYYwE78StgbTPhqPGGEkIASUUXoazjDvez+EL'
        b'+gBbCLxlB6KjcfQlPjSRtCg5OA5IfgOuAwxL1kiZGYIUl6JLeJctiHTABUCBMkhfkxQ/Jzg6Hm9IRA3oYHzSfJI2bJJkFn5B0omrcR15byNl6FUssEy+SqiSVEmrZFXy'
        b'KrcqRZV7lbLKo8qzyqvKu6pXlU9V76o+VX2rfKv6VflV+VcFVPWvGlA1sGpQ1eAqVVVg1ZCqoVXDqoKqhleNqAquUleFVIVWhVVpqsKrIqoiq0ZWjaoaXTWmamzVuMzx'
        b'DrbMVAvAlllgywxlyyxlxcCMUzrc9yQ8vBycozNbXpso9sdRXDecMAzCLfAur+4MA51nbIOJkClETZS+EjVqTRjaiaoJCfloedSCzuNDFIFRFVqLm3AtYCjPcCXpnmzU'
        b'ZJYOIroIuNIUio6ERQNm47MsKmdxWSBqtfUjb8vR1oBQtQZXx6A1DFAeOsqFDlPa/ODdWFw+gIxXGIy8kIqrYlh0DW/B12jGmTNRdRyQGnmHN4S5scADNuMbFJjVQ/Eu'
        b'YC/RBBZB6x3NojP50fTNLFy5OjRczTEcMJV1HmwqtPKKjTDWQhPaEoeOAoUGBkgZaS4XPDaNwp+GK1FlHF6HgYFAXdD4nUNZdIKPpTCiDWa0lyIhC2VumIFb2Xi0DbfQ'
        b'rPGTcVUcxbgwdApfYRnpOK4fPoI30RqzVgeGxgKVJaGNE6HhUZxnTBxtWhHegdbQMoM1GXgrZFvBjQxdLTKKXUNDgcCDoQUmvHke+zQ6jK6Jb/Z4Aa7XRsQSQHa44UZ2'
        b'9ryBNjL8wCvXFVFKUQNF44tjgGfd4FDVtCIbwQztJHwC1yaEAcLbn1OzU9FhuTg0tWg/OoCO4XXkFTqT2Judhzb1oZUNTcK74gj147p4L4GRBnCKBA/aqiC0IRbXRqMT'
        b'kKdYNoCdjWuzaHH4INBfHTDKcALgukK0hn0mFx+nPBSfyZkB3IQUFxoeA32SKGH6ZQtoD947Cr+IDtBmGELRibhQIgZiYWCTWcZNyqGt+Di+kcF1QHqC552VHFBxqliX'
        b'ksNVgypTzAM1cZSaeEpB3Go+pcM9UFP54yk5fKJxegniLE/Dgy+r2r7Uvp5+X1uddR++hXd/e6suapdb9GjWmKnyeGlRmPvCNVO2VdTVKQdG/TuzYdJ5z0qt9G0r8959'
        b'z9WeKrWMajFAVJdxA6G31egGIN36JDVeHyOKLd8ggUel6BzVYobi+oyucs3TR5nLD0LHFtOipuMzCynhhiVAz9fERU13JRyMNgp4Iz4QbCUSZC4qdScJkwBV0QbyXoEb'
        b'ONQYhM7ggwlWwgRwI6pb6UgTH45qaG08KFUtfCBuGmolxIBPqJaEagJxazRIMgkjx2c5VP40qrNSnn+sUEGBoXIhLqwAnQHBIEITFCJJGhTp0Ly66EL0KdWE2oQ8nSWH'
        b'6lhEO5KvlrPk35NVEF2rtzOtWmjj9RZrG28xZ5gJCzR7k6dce5FwT1DV3NdZMs1cwjh1rLIedCzavtNT8RVCKniDFDjBtjFhwAjS8baHK9njRPzjMrknVLEze8I+oSfs'
        b'C/nmQ85COtjzp11fav+pXnzznVsNt+/canj5bMPGXq96Zt6NlzFRE4Qfjr4LejJphgQdN8eF4c3aYOCQcSxwg2NcEXoxkKKCKgwd6opVq/Bxoi6NQnvFDuZ6Hh2b1Zjr'
        b'0oCZEm85jIov064B8/npS3seENB3/VxjQbJUk2LIDbPG8989jAYdJndDKFWngCvPjjSz6EbJ6k4jwTo+KU6Y7HALUpJNFKH2d8Hf3ghPU35afnqmzZKhsxrzTXXw7O+k'
        b'TQJnGwFfYfjKKGCktH+SYkNx43JNYiLRakHn4JlQdEaCd6F1cx4DjPKfBcPNCYOhgTwjOhXV4qbzfsBBY0OhVvQCvkaozAeX8egauo4vPRwNJxE0ZAkigrUn/E9RkWV6'
        b'YoSSzomcbHiwq37KhqsEV/2/mBGT+hU9kcIefhNrmQkP5ik8j318X/uV9lX9pLL72lR05xW/t73fvImSUbL69qvJb9x8Nfn2b24txu+8ufCNZPzOSzu4PscygrPCsu7m'
        b'sozuuHKO7Ec1K/K947HFFnQiOlETjFrinCPdCzfw6FQh3qxmRY4idOVaXYhDkpahyxWpw5tSB+frDZxLDsgsL+V+XBlgyTZmWtMMZnO+OXxKbj6ktjwdTjM5mZqgM2dZ'
        b'2qQ5y8l3BzrqZjxyZkLI5sEuiiKYs62dony+7IGiiKK7CK0NArUdV8eHopr5uCqJWtB4E0iBGpAMiaBAgMK3GdXK5k5k0LqpbmDw1KPzxilnWYlFDQWMu9aSk5WdlZuV'
        b'mPFWdKIuXrf03mHDfe1R3X2w4xWZpHMNb0nf+GaN2KbH7Dv3Dn3Tkb/0VUjNga6kHj31hbmXqxNIyi0dOuHrHjqBGkGlK5JdnUB7ANVOjeCY/uiygA7js2kPJ7NuTp/H'
        b'I7AeNQ2uG4ILifOM+SfnSSxEtF9Ul8TpiKIRrRM21alV43pHfrhD/xetHNg9z2R9KF29Wa4WrCpIumrEJLB7dlDZnRimSRR5ei+wtNEGvBXvt4aRVm9g+1PpDBZ5cKwm'
        b'HG1Igj6oD41BJ4JRjQmfI3kWpskz8W4PqltI8brJkGFdFtEI2lOSZAF4qwDWwI0wKvdRGarwpkWrY+MTE2LB8CIqxnTotmFDJQOL0YmOyNBh2D1spoxsndFk0KcZVlAV'
        b'z6KkAy8dLCUDR4T+EGcWNYgXSNVOFkccyMWah7pQgKTe144Cyk96QIGhtDPGTg2lhnQ0kHtdXAIgArAAKYOa0bmglZKkfpM6jZcTCYia6+R11Ez8n/NagelJ7MsTc0lX'
        b'/Gmom1w/uzFWiHp99W7LR4ufzxoX+mu1jKHKikE/JBQM7M3oHIOOo7VgV+9n0Tn/+dQJdCH/715bvNjgU1EP2B/9Xs89KzpvBmkA7wTV83yBrsRNGyM+/HaFDzOM8dby'
        b'jHaK+vk8xjiu4hRvyYc3A+dNjdPpdYcNhw1faQt01efOzztu+ALI/QutKTPE56gu9WYDOtvQK+RleZ/3juu4ox8fM7Tojut8ZV9w7yqHaCdVfMRG94v1Pf1BZN+P+Ns7'
        b'5y4c4HfqCPv6qbbR73Nvhf1GejRTSfFZ6TPw5M6vgSNTg3I32t87zuHniPIGPRM1cPl4W27PjOSR7EXI1lmyKXoNp+glHyEHjZL8i/qlguX+K0iUjl/Cf7hSQWIOakc8'
        b'kdu28+OeoWDFZBQPSeZDHVjRb3vAQ4JLY9BpGdhSoG4CEuCjT/UlRu6LvR7h02W7+HS5X+Z5Jj3i1g3zlInUZlSiBrwHb8bXpFB/BBOBq0ZQXPkqnXiiGdWpVbb4c0NC'
        b'RQQKWsZTHG5MW6q8s0LOmAn/7unSxqYZ33/6FcFC1L+/1Rdp3hyp4EZ6V9z7bvhrmUMLFzy3yjfpVMXCj5SK0IX31wZ/9PrwV6JNS9e+0SdtZP1Pn2weluh36m71D79J'
        b'/zSsX9FfqwtHBM++6j1yZ8XGj0Lmrzvs/8buhoLR9cU/fLj2jb2ptllHf3807evdNVnPLv9p3YfJ3095f+kLM/SBI/OHDOl9o/Lc+CGLS0bKh7w+uFbtLpovh9GhWaJi'
        b'jIGB9upileF9I61EepjwebzREqZW43XxIZoYmyYkDq2jbuiQ5yToxrQsqmQnonIwvs4kohNWKmJRI97GMR64lB+DtzFU70CXIc2Gzpq4F74iuqmXDhTtrfXTFoSG42pc'
        b'E8YyUrQhRMdp0A1UZQ2Gl2NBam/vaP05CoGGuOw/MJ/rrMSjh7eAYbMtNJb4YeJH4Wawv91RK4f3DkaXRDXoEL46C2zzMLwHbQ1Rh+N60HoZxk8lPI+bUBlNMxFvFw3X'
        b'JFIfyIJjA1ym5PlJBSLItfhELNoyIS6so/GhnGMl+P4Muoj2hyZqYsLUuMZdzTFKOS9fntLJdPsZ81BaYEvPNYqSIpiSMjfJk/UGyuJ+knJ9gKoEBxETMpZKFKwS/kGK'
        b'jHCV06/HKvxdlEtSXmqnXO9Xe6Bc4qsY648OhgYn4HVgLEt74z1gC5/iwHLfPJXWkyHtQGg+8JE7Cc2HJ/aBnfVniqXVMru0minjimV2mWX4Spmdb2Ts0ia2WP4sY3IT'
        b'GCtb1J9lyP8ixuS+HLRmu5zks0tJCVMYPUtymkvtkoJQI1MssUsauSZmJrMkYTFX7FasIOXb3co4czGtSYC7eXZpI99Ey2gUaFplsXs1D+nc7Vwmb2TsimZ2A8syy2ab'
        b'htBcSoBPWe1ml5axALGiWk7uyliaU05zyrvkzLArzYXVSjGHE1aWspdlkeRKy3UHaDZVs9VMIWPeBNBI9FwT62iXMw1rlWZykO5gtTtNd7CaI6V2SSWFFOerJTQFfHdO'
        b'oecbZXpBLykHk3MmU8ZC73ropY0yu0ejXC/Ty5s48sTuYf6V3s3u4csUe1TJqtxByeP1Csglt/MkV7EntNuzjNXLczjzn+2eencYB0+Tt+upYP67Xknqsns2sb7kHaf3'
        b'KPa0cw1g+QKULIES7mV6Tzuk7we8OZODdF6mIXbWzuXw8K633ovcO5776r3t4l2vDvmD9L3E/PSNAGlIbV52L73PePLtAWmm2D3p1Uvf2+5p9yDlkXcmmd2LvCmYZvcg'
        b'v63imJI2eEMb+uQIkMts9yZt0/ctZOBXqvgL8mTBndz5PF8v/iLPoZW99L7wm9H3q+D8GXsvCr831O5X7UFqWKqwezthsJN2lltZu1cZu5a1uovfbtlq/8R5D2S5YJKb'
        b'NCMfcGGqTiKQc4hBamBTzyqQ0BJJMWtnlzIbuWUg6twyHUpmmzwtzaTLM6Slqbk2LjyyjbV2tb0VU3KNFmtGfl7B09+TEjlKoysHZGQbMnLA9mo3z9oTPuBV+eYHbNjn'
        b'BK4HivxMlbWowKAKsnQDVOKkdJUTUHcyO2wncpqzcNUAdBnrALq8HTTggaFUQhb+DAc0k7m2/zhhHsR8Tip94KVTFepybQYVQBUcZFFTUfvAz2JYZjOYMgwqo9WQpwoy'
        b'ktcjgiwjHvSiD8it65FAr707pHTmfuCmyrNZrKp0g+qBl8FozTaYodXQGXD9XHTzPGBHPGCHPHALsjwXHh6+BJ4T3fVBrzBVVr7V2U+T4KNWtkmMJr1hRZtiAQF4FjH4'
        b'4BHUamkTMvILitqEHEMR2MBQc77e0OaWXmQ16MxmHbxYmm80tUnNloJco7VNMBsKzGYySdTmNg8qoCWpfdrcMvJNVmJSmNt4KKlNIKjQJqXdY2mTEFgsbXKLLV28k9AX'
        b'5IHRqkvPNbSxxjYeXrVJLWICNqdNbrSkWW0F8FKwWqzmNqGQXPk8SxZkJ2C0SZbZ8q0GtUePauiTXECHTHZhqdyJjm+R8d5AZAhH/KAc60mFGveTXJA7RJ63Q5tVsr7w'
        b'XMGTJ74OYQjC8e/CTz7ePvDEm/WBTx+pD33nC+mJiPRmBU4K3z7wy5NVcErit+Dk9IknR/yvfiwI1584KLsP5wslQrkcdVelogp8kphRCXhDYlgsKC9pPCgQZRPxUXyh'
        b'k9eeCECpkzQ+hgsILM7ONDJUCGWBwOKLBTtv8VgmtYIiSz5GEHB7eCLW7JydnwIkZA4GEcgCmw+2g7jwZxo5YJi8P9MEYgdEkQBCQCACwzLKLmSxUJ4AZQeD2OKJMAEx'
        b'kQCESMSDRE/Kk+gFKIMnv+AbxCEpZ9kYUciYU/RCwTw9Ec4Su4zWJXW8l4i103K4KQz9LTh+C1OYZVI7JW61JBFoOYmMKB3WOeSS5Lojz9QS8wwy2LzFYG3jdXp9m9RW'
        b'oNdZDeZZ5K28TUbwME9X0CbXGzJ1tlwroC95pDdmWM2JzgLb5IYVBYYMq0FvnkueJZDM0kdgXAefKIlu0Kc5yx3EOkwlgfOmCOfNOpCBDj1BGT/WG94RdAJ9iFg7+AV8'
        b'eIxjCh3VRHij82Q+MEGcvwtFFyR425yUbuYHqZ24Pmlt3aZeGTL5munutHPsbIrDldLVPHIpV3q4VJORZmtA3C9lCuSAZZDRHACY4QFPWCJKy1h3UA2osAKcABHIVvPV'
        b'7uS+hoTLCAAIqV4B4Cgz5S5nppudIziU0kN4DEFs0qfUF3qfACHYidbArJwPFfPknmpMIYDyHFQGoJWxOQyABXd2AKSYN7lT8KSA3EPJHTzhWMbUy87TZ2OriU4DZEA0'
        b'rWopQXqHtgWAQ8mDi3k7LRfSzqqWArLyoNcIJim5h+f0l10wP0vkDxARLccuOMqYAPqmD+ibglWSyRXlsKBLssxKATpLQuSzHn6vlpAoKiANIEs7S/I5fNyAZ8TiaZMV'
        b'6szUgclnAS4DZzXnLDdPJzgWJ2Jju89yHrlQ5DVQ5DeYzWr5Y3PKdrxVplEeWQAV51mmEayNJNhAMJbzpMwNGCQwMD+WKyXME6wBTgBWBgb+Ax+ZnDhmf/LkVkbqMjIM'
        b'BVZLu9zXGzLyzTprZ09te1Ugq8nw0xYBhdNIHvoghzxw/6Xcn2+TkQ4EQhaL1Lsa6uYCaALrnBzjiTAYBG0M4BT+KwMe3ganepFOissj94pfJJrSXeDIHJWNZR2eAxUv'
        b'DBVjAa5OComLT0zUBKuljHt4CTExm8GcvtbN/Sl3fFsWwMXApAKSpXKUAUidro1UfotcdHYAPbplSmhgoLyMTRVczwmzkAGTEIMFyTtJFSMwqVKiEaplbb0cQX6zjbmG'
        b'+Hyd3mB++FQy9etxUCRwog5zGPz/5mSykGgjPmSw+/fhjRZ0Ijg6IRyfxEdiEuYQKz8pPkYzF1cnpQQT7knjVtBafNht0SS82/jpf/Q8nYXe95PiS+1X2i+02Zkhn6p1'
        b'0bqvtK+m98no9Vl2Zm76V9q301Nv/u7WlttnGzZuZA9XTtwXVBG4Y81onhn5kvvi3+xUS6jTOEabic/gOg2JzlqGtkY7YukCbAKqBIjO0ERoA241tLsocAV+oUMo3cne'
        b'1NeBd6BLqNE1c7xquHPumA/0xHupRy8aHcI7QjVk1pib7Jw3hlxrrWQyB+9NHIVql9OACBLmQ2OTYvA5sT/QOlJ9BF4Xj+txHYCBanA9cHAGEuzEO2d54CZ0YaZjDuUR'
        b'DANsA6PJaE1L6+BsZkoU2Z6g5yjYlQHdsCXcmcE1R2Mx5Ga2SXPp25+ZowF6M5P7Zc66zQVwySIEQ7wkzBpmjc/O7r6FnwPh4Zj7tIi5PBADkaLSTKkLe4XHwt7HnAGU'
        b'JdLosNCJ+ESca7RwA894oqOhaA3vbV9tC4cEPuGjyRwqDQJ1pUsGBHeEOpwDJWVx8FC8UYa3hCXQAEJ8ZWGumAfv8g0OBlyM1uB16Mi84NgEXB8WHqOJTQBx6OX2lBdq'
        b'tRHnD67wCErRLMCArdG4Th2bEA+pHUQEScegbdJhgJTVxvDZKbyFmI6/vrfqS+1r6YcNh3ULbz4XtwNdbGjdcbJcXXGkctqepp2tNa1lRxYKr2ZJW3P8Ji18w2/dn0rt'
        b'2wKkI0/Z3SyyGTLL6Pe4bZ7bKupuKfd8znx2yaflqVtATMSj1F/1NK6NQ2fxARr7Jwxi0f54oCGi2+A1o/oSv1pHnxo+HC08n15AaQwfXwnMwEWKLjrMnw6UmI0brcQT'
        b'FcWj66HhmmgNh4/mMVLUzEXOxPXi9MtO1GiLC49NCItB62k4SXI46WUJE/SMJBXtwqXOabjHVwg9MswGUELT8vL1tlwDJZY+DmKRLiNylEhVOTUdVg7ujrGdcjspk1AC'
        b'kA+Rbu1kI3m4wOFE2rG6CMgCF1NHAvLd1AMBPQqcblTkcoHPdFKRUwMltCTPdHtCWuqmHJJKXE4BFy15irTkvQRtE2nJW+hATbx3KK60RUCCDNwA/5Qy5i3/WXoCYtIW'
        b'2YgGhI6qgIXTPKge7flZckLN6MbPRzPoO0UzqNk2NrOrR0U+JVeXl67XPV3BOnwTAmMjgn3ciGTLQ/g63hSHTkQngIhxhkDhrZ3moflRPha0eS7eg6/64BMMOo4re6FS'
        b'fBHfEKdxL6SgfQ5/fR3eyeHaMIfgmcuPxOW4slOrJEyHaAXKL0VFnyNj7eKXPJX2AowxT8dYoOPKrxZSOtw/LGLBZYV05JcT4b4YnUiOI9ON4WJ0QUp0KIk2nA/0rlHj'
        b'DfEx811DKWHQFRtqNCjw9Vn4BJ1cORApzrg02HVhZ/xGMZTD4s1j0aE4dGB4x2LFkGtQH2j4SBjhgnklbn7Cs7ZRDHHeN+IDcXFkvhO0jWB8BLXimmdFhjnHBcB8wCTc'
        b'KsMnUZWv8azs35zFSKob/ODY3C9o5NtrmeEfh+jidblU12i5HDb3K+1b6a+nv50eo9ukfzX9hOF+1McfRDLzQ7n5o8vmVY3+0zenI7ecmv/F6FGlquQ9B8tm7WGHPev5'
        b'/oe3Gl5759bV8tb6kVQ5WVHf7+u3ZqllVjI/i7ajigTnXEwgruwaIbcel4tzKLtD5nZjnWinP9ViivIc8zrjcEUcKo3pyCLbGWQw2kC1mAxcjdaISsyGJFpXRp6M8cCn'
        b'eT9UZ6ZJ0EHU4BcHulv9DLxDnBMPBzXXZzWP6+zLacge3osO+dIkSRwgLI3Bdh/PgVlcgVro/BHejUvxVRJwMksBanLneBN8DB19cm7tSYJI0grM+VbqAqDsepCDXTMl'
        b'nA81g4ixDkxbKCVTItTsGdudUxpWGDIcfLLdkOhcusgEJKKF0m7SPWp21DGJ6unKQFn6crjUE5YR4GDpwNT/1sOMy2J4G5Qw4ElZyXP4SoeoFh5tmohbJbPwpSh0Lggd'
        b'UTND8NY+S3EzuphLYNzr5h/g5XY/iGHujfiWOz9yraqJoXPpb47ZmZTPa72YKO2o35kzVSvEx5dXffuU5+DgwVzyXfZHv5gZhxjj9+k7JJZmeDei/OWg+Mmea6P62M9c'
        b'+UpW19dN9g33h1u89pu1y+ICF7xzcdiU/r9iamS2mg/+88zi5vFuJ7S59+vL0oPeT0bu6T9MyrlmGbf4zWEtH5T1qk5aqrmx7KW8qH+1pNrPTrSU1F33uJrx75c+ecna'
        b'NCvi9vTavyon/+vMC9+GLOj97fkA48yqyTUbG/52W7Y5wDO994T3XzLM2Pz2wKDC9xfvPZISs+ZfHxb8wA79S5h+rkntQfWPGegk6OKijo924l2dlsssx1co6keF4u0u'
        b'JQadALXNNTl4Au0RaXEX2uTemRj1K50WhV2wEu82qjWiapHInCOJqv1wGYwbDKTIvsfppUtG4/VWEruZmTpQ1HqoyoNbUEvkiGyRQ1y3yLoMOqpENUBu/ccKqBbslJOi'
        b'bXExBR1wGRcz3J/MvADbAm8cTCvEp1Cjv4Ml0YyBuJHklTF98RqeRL0fEOdRD+Dr+JIYaYMPo0oCIe3N+XxwFt5GVUJ0GmymA+JKBboE4wRukaOD3IriKZSLjESn5Q57'
        b'CrW6tQfj8oH4bITY2c2TgKM4hN/qgs6yb8NwK9HW8J5YvH8mMJjaeJZhJ4DRuSD1IdTp9qS+AKmL+bh34BkdJmZBUVztVBQV1I1IHDAKTgAuJPUS2D6cN+fLrhz4szyo'
        b'k+oodTxr5zSyx4GVMxcxneywFXBZ1VGNHFDRgxr584BB1XTuQZHmeJCW1qZMS1tm0+WKc0/U2qMaK62vzYMsBtNZLBkG4KUOY/IXeGGOsG1ujpKgFNocEqZjYB3WrJzx'
        b'5jiZL8sph7A2EvVFTJKih7FNQLzmwEnomhTI/kVc08194ZzDtpC2Ol00Bl4v6k0MjTTl9Hy5G3HJULeLhIbfSlxul2SdFXrQBL2XmCF0KdllvUbBxaFzO3zAmTKHPiZU'
        b'y0Afk4A+JlB9TEJ1MGE11NN+/zB9rLvOLUkUV0odnxjutF9RI7rYQevu76HmRO1y+wxUA4n81C4zF8Q6rhGYgJlCtB1doAtnPPEVdBBSMQNdqUJDoqVMgEWYn4+OGaOW'
        b'P8NbYiBhTWnQl9pFNxvA5IxqaY0+X95a1lp2aaeRTZHFyXJkv53+aWplQOWQzz239Tk0arbK40+GkeNH/ybypdEfRgqjm5mRWZMYjcWbtzWrBRrOUYDPCZOFrmYlcOPd'
        b'aBe1SJeDhnnRyTuzZhGDEdSXIyKL2oJ34ssA9iJ8AlgeqhFXZvkYeHTcgkppGEdaLvSLi0Hhs8mUP60yO7WTx6G9juHOmYAFacT462RMMiWKsD5K4A08ccwKX6/s3w1x'
        b'wl05RaqRtvEZuZY2eaYtl9Jam1AAadukVp05y2B9pB4imNeQ+7XkUkYu5S7GUEoJrJMy4vebHljDz8Go5hKJQ5wQjHkluayiPJJSbJ7Bmp2vp9WY7c7u6T7ZW+wCiKxX'
        b'eJF1WGFyhuMGsTYShDseHfRtp2l55+V8IFk2TFZJ0YuoYSW1H0r9ePkfeXKnDXvLYxzTbRKmMyF2moZxESJDwxt/wQo1Anr3IDP/RGrb+qJTIMdBZzjrvsyGz6NqfAG3'
        b'WgvRejk+5w5fXgVK3MowT+FDEnxqqK+NAIgPoQaQsKDdxSfi9aGJ86lFHANfNUkauvYY7Jq9EXOiQahWh4Wj1rnUi3oWXVbgG3q08ZHrpXka+/G/sF66R/5D6C9gET4e'
        b'ig7Hi0OI9qLrCSQAsPc8Hp4c9aILKFFpwTBCf2Ij8dZQdCSYZQLQRnQEVQrmQLzd+PFtFWeJh7RJi17qu67VozRSKfxxcPAObmTKglPB2Q1z9ZVZ7qtSPv5L4vKPr9Su'
        b'eemZZYtPv5I+p+3bj4dfnnhmfr9D61Nafl19wrPszr37E/4y+JXdPskNtWoJddhGoW2oDKwbDBoO2g6SRIqOc6NRVTJ9mwqmzdnQaJAjlynnEcazqAX06Gaq3UTre9EV'
        b'FNf6g1aliaYpvNAafumywVZCWosL0D5IsA4M+0NEfeEZYSILg1aVS11daM1se8fgMYWGK2LnPHLpkLuuoMAAVEi4AeUxvi4eo5wjUFeVnK4jEn5YGQKcIi3XmGEwWQxp'
        b'meb8vLRMY0eLp0NRznopr/gZdy8rpqB0WwmXX3VmJN6nerBqyAzY5Gm4NS5JQ5RO52Cj9UnUPwDforje2iU8Py67QOwf4Nxi9+rRPu+8EnSOzsHguqzseNQaSvp29DiO'
        b'keB9LDqbibaKiFWLD6CtQD+tywvx2WVKecEy5TKBASW5wXcyn2VEu2mEdCJqllrwWdzq5lHoofCU49Ne85YTSl0mYYb5CMX45FM0Dg6flQfGgRQSB1KBr8vRKQ408fXR'
        b'NuJlmQCDXIaO4c1A2TXxIbFh6CjeshyBzRAWTFwP8c61NSlyx0pxlsRgn3GfAeygnnpP0p9Td8mOL6D9P5N9W64CV8zCe+ka4uXTUCuqLViG6pfj8/gCMBsrKM3l0L8X'
        b'8Cl8wQatSRHA8D/gR5uNqr3wEQrvdiLu60FIxsuAGMnzjfxctAvXUuezSgt02K3YXXjbctyqVEiZYTECWpeEtlBF2UYCAN3xtvHoDGAm2jtjMjPZjJvp0m4AZd8IvDlJ'
        b'E4POo0t4GzoZHSNjlE9xeB+qHEi55KjR0e4asnJSkxr3rNjqDowPnaMMbgleI0NXgVyP09qW2VB5ipQsbi8cxgxDh1EVlQXDJoOGmLxMxmi1ytzApWL0bsMkqFA7m4NG'
        b'Kf+2wAgqM3389XSOEYZFABfT5i5eNlBM+1kvSCt8KoG0uUtsoxjqWcoZARoFGH6hxLlUQ51JPcI4NDMflcqLcWm8sWDRbd4SBTSy6ODrCclPJeJIv/8+PTnxUvzmcZqp'
        b'FbHxYQXMcF/fEBPjk6794f3YWUe3zFx7+3n53Lde6nXqwvPM7Jab7J1er9y1bJq99c/fX7v63VP/nlgx8era9f3uNrxzgPW47Wa511x5M2eAZPGg376q9gkY/qb3ttfX'
        b'1trWP5suObZieMzcf2zyO3ttVv37ZcGHAn77jzsZt9/e8F3A9Sknr7mtyl+acLH83fXbH5z77OzugNyDQtZv/rZg4Luvum9/d8MroRfrL3ksla+8/qfjvy/9VFsuWRBx'
        b'4UrftN+dSFq127Sg4tKFN6M1v79ZVmNao/p4fsz1JLP0zz/0/gFd/uTE0O3/bpg0LjZ0/J/cnq71enlo22f/+ZX9hOTGNsXn/941OnL8gqVzAtdf+uGCr7VACP+n9zuS'
        b'kpNNH3gNbvr+y6vJ/6kctvQvH/1XU/KFW3PM/eR7ow+dKTENt01KGaH2ohajCp+MjSP7YtSGEdbBA7qd5vEudIRDTYusRAoNtgPDSNKwDN60iitkp+GN8VRRRBvxUW2o'
        b'yEbwvliRlV96mnLyQegcuhwXHxIuvnbP5dBavAk34+tJVAtFR2eDzCabBJBRlkDRE+S4litGpXin6A67OC44NImARNQTGUB1ncNnUoGAy9FGqmeiyhXokovdRwbTaOEC'
        b'dInWb07EjaG4OiZs8rAYXAvSRMJ4TeEzAc930feFuOUpiSaOTKNC8WpNIug//eKFqBD0ApU0QJplqDIeNXeMoeY0vdApse7deJ+WQoZrZZB4hqBh0Ymn5VQM4f3Qit2h'
        b'sQlgPKP1y4RAFu31Xu0w8fuNWDHMUSbhzFACoHc/dF6IxhUZYhj0adwQpkeHqAx1yk/coqX91pt6X/O6q+9oV9ij/H6PZ/V2tND79ijtqIwkfjWOFaWkMJtElSmppASL'
        b'nVMovDkfsNnhjvPmvVk/zhlOoaQrchXsgJ+UNDqME+PRvlO6e3OCTPmARpX9JEiUP5qrnEL6CPeEhnuHoEdSyO0uivnlHuQp4UVo71B88SEC1Q9tcspUCfO8VQ5icDOq'
        b'VfM2Mt7SQBCttXHi/N043EKm8IoDqL6GygtBINQmohPxDo8u0EUDmXI4CMJlE10v7xGUEQr4F/JclBTGuhHG+jI+kcF3UQd9nSrh83Dpts0E49pogu201QRX1TfT1zVD'
        b'IXmsGQrQSO8NgzFWqDr8zTVkGS1Wg9mismYbuu5/FK7olDbGqjJaVGbDMpvRbNCrrPkq4geGjPCUbHRDFs+q8kl4abohM99sUOlMRSqLLV30h3QqKkNnIuGjxryCfLPV'
        b'oA9XPWsES8hmVdG4VaNe5UBOCpWzbHhhLQIQOpVkNlisZiNxQ3eBdhINzFERg3CSiuzxRO5IGCsp0lE8tLCHLDmGIhJqKuZy/OiSUa8qhD4DmHoswGaBl2J2V/pZ02Nm'
        b'pNA3KqPeogqeZzDmmgzZeQazJmamRd25HEdvO6NsdSrSRlMWCbHVqUgAMgHHWVa4KjEfOq6gAOoiEavdSjJm0lxih8JYpesIQDBWMDaWDLOxwNqtId08J55MV8vFXYxb'
        b'idcrUyKcM4hzn40GjTQlOlYyd+JEdEStwJd4dLFoItoaNWRiXwY34MNK/5GKbkTg7Sx9bmciYBxkwLrIgKvyyvR+wqm5bqEMhI903yNFkwjpKI/pHk7YPa7C4Z1yzRP+'
        b'4oWfpKruq/0kjoXihGcbT617l7MQd2X9r3d/qdVkxuiUmfe1n2vzMr9iTk/TT5oxOiMgxX/GxmzZ0Oirm8fWXyobOzB6eaQtsnTmLv8lfum3c249WOo3zP/myp27/OP8'
        b'a63+/77if3P42tv9IsOEM7l+ij9PWtgvMlyv1d/XSnd6v3lzpydTLhlYMjHQsXsAaN6nU0M1wdEgZ2uo630Xp8GtqaK6cBCfnxuKNxBNexw6IthYXIP2JTz5pJUkbblZ'
        b'V9BlrgqkUJDA+oH8kHLebB9g8D40hnml2uxgXR0C8hxI3uEJKdGxF4EYB9such4B2BFWzEDlzTq4DAHILANc8oZZ4/u7HiTOVIZuO7TeAnoCqgMtmBJGD+up24XRLB91'
        b'RCwoBLPRYS8juvz0I+LReOqQefI19d3IQML05JGQJdqegfsC1IzLRkeOGTUO7MDykWNHQ6NOWa3mwmU2CzWUzoI+cx63gsV/xkuuVHi6ebijelSN6ogPGV9wwyfQDbSW'
        b'mgj/HRvLlI8A9PDWhvxqiEK0G65JYph5phEsGB5Lh0ya40D1Xn+Xs1QHCYr16ftKU6/SSG/h5pVf7Z7HCJvllZn3GfdwnpM8SLvdXNecsrbto5mvSLLcZinOHJ/w6ZLF'
        b'U/rsGPbaux43+MUJKRf/ueTyqB+zKm5Zpw/95qXmrS+/7PHNf5hjR/uoVNsBq+nuNNcmxoh6Jr4yybksLXOxqMdWzwM1uJZuASS6I/Ah/ALI9uto88+FqDw63Mycb01L'
        b'J0a4c77BieajBUDtPhS5SfD+yrDHQnBHcc55EVes988HotEU7ei9Hi6RXdHb5+0e0JuEpi/HDamhTpb/cMzeBgqRiN1ktWNN0qhxPFOIar3D3dExigFzc8U1oqeSTGG3'
        b'n1vF0FWmenRgHqhW21AdoGY4Ez4NX6aJk6PIHnOM9zuBJfEWNkHEoT1DxUAIlSEv7PSIUBGH6JslY9yIVImM9NHGz/R/TnyYPCGObAcgv9svR9E7zyA+fHu0N6NimAml'
        b'I83xH6f6iHtuAAc7jo/iHc+mAHJsmT82Eq8TGOlcFp5ufYpmC3MPYED+yZOtRrst0Fcsa5PiVMl+Sq93l9+ZXq8Vt2Lag7ahgymIFITXSxgWXeC17NO4zkPcgCHDs92r'
        b'Nz8aLBdcHRZL/JbEiqFhGLg+lJgDqCZUgVrxATXQXAWdb/73ChkDQ6ZiZueGjSuxZoxg6Brx5mdGyOWLmMhDQZd6vTZLM74g+e1x62x/46gfoARtIc6emKUgeBKYhFhU'
        b'SUFfY5nMWKE9qlmFc90Fu9ieoyOn6q8zcpZJLjUvlKTn04efDJjK2ME4KXW3+TwfNUBMedZHw/7I3hQYVanlzoorUvownf/QLY3NljHea/LvmP60lD4czD/D7uKDYXTX'
        b'5NzR2wPpw1GmvkmHWS1gQ2mxX9y7YpnNw20+Gv4uwFlaeMd4dAx9uK7vPPYwx0QXzCzIOb3agQeZixri0rlkKaMtzdrhVi6uS7brFgbsYQtYAGnlHX3zdPqQnzEk5w/M'
        b'DoEpgIqUu1bRh8tTByd+yFYDgpTa/casVohjOTFBHcRHSSB7jp9WPY4+vML4smEc4313QtYS+5KnxdrruHfYRp4pOLVyVf4zmYvFh6tGvsRUQ91RBTrj757pw+QSJp4d'
        b'WMx8zzDBqgRj4RtLRICW/I65yDLB7zyVU5RaFC5mTsv2YIA3BJ/qnR72Zr5NfPh0SIEiiSfqyN30ebbpw4wlv3+Ks+yC7lm/acX85JgN70d5v3n8rcIIU+Xt9bsNd7YX'
        b'8c88HzXYW2Zq2ld2cFv20MDkD14rzQnP3qe13K3+1Otq2fiCe6ze381t656Nvf5Y1Pft199ceLbo7Ldb8zz/MDfp2pdnVv8h4sGf3542reTNGXMTbrQZ/Rbe+8+9qhcX'
        b'Wu0LXuJaDp2ZvkJ9tc/ZtePamr3Kc/fcufnqM54hhqESzeHZ6d/+50N1647059/bNWnr+1nlH6nePrL2m682T5IVzz034dT9Le/HXV5x6j9JHz4/9I/J6/qq792a+c3Y'
        b'Q1+/9JbHuSX6i7ODcqdiybWp09Q/flBZYNz74+L55ekJk+fH3PjDgPD9AW9Gl93eGJ9+7V/n51Tljxw8ILw+7Mydzyv++p7HwPC5H0yonX15874CybOTBy5+/2KlImfx'
        b'M+s9THeHm+6N27BMtnyZ13eGTbLn7zXl/muj9Zs7/adMPJHx761p7/RT7Bz/dVL0MxHGEv39vH/92C9l0tzlHy17VXhBcfnZs58t7/PZhM+/n3itMLC+Leu1bz69sPzp'
        b'nH9MvHBGfaBk58TPMHf2YI1atzV3yb9Ov/dc7MplD2TRd9e990miWk69471Rmb/L4YCbUAV1OpSgi9SvMBdd9sUHcHMoro4gu641scl47UwxUrQMX8cX8Vp0MTRWE6cJ'
        b'SZQwSimHr4WgNVQxs0234loLyNt1Hdzmo/FxUWtrCS0BxpEUg44LDDqbJc3lhuBr6AJ1hESsmkXqC1fHOraaZLxwKZ+Pz64UA5saU3F1EVrbzVVzAW3D+6nPIxZVZzt2'
        b'ySlY3DloCUTClSeNIPB+8rnvx9Ys5U7BSaVudgepqwwUWF/O25NTOFeJezo2gSDrKPzg34cdAEJwACfQrXsUZGkc68P7gqRWsNyPHCf/UeAFGkRF3CDcj0peAXkF6g4R'
        b'floZ8HApLuqlErrspU3mMDTbJNR67CC+/+eLCEH3pVtK0fU1G11SnywgHNhV6ofc60Hqk3mwFehqDEh9T3T2MVRaCdkcEnTAqwsm0j20BuGdg+jcFvUH443FxCXc7j2J'
        b'QGcl+PjsOXRjQFSJWgCjXdN56Nxc1IRArHrjCn5QgYEyw5hULtXM0ilM5Z9yk0UO+buZQnY0B50WpVW+oIgUH/5nirTPNM6POOhzPy6YzBhnZN+SWA7Am23KL8bWJXiu'
        b'jVLOfk5aqWNKRr7svoKt/3iux27pd3ebveYumTD8699Nz196++KKmB/++c/ef/ytu7fU3vjmBB1WP/f2pbubQvf9bUu/q3+a/2zK9E8/5/4Q9YUuNNG4Jezmr1+adPnO'
        b'4n8OSdyl3X+j7HvdiKjP7yy+1jBqZ+2IK2tKc1YMPfr7wS/988W0kDvDH9Sf+LVnbop67K9unDftfNtkDbs16Mc+n3l986cIa2/OsT8grh0cRzY5Rg3oSpeNjsVdjnfi'
        b'nTQ6atiycS7vpaBhF8xEJ57LE6OjtuDSpR2HiIQ9xrP5JUwA2ifkQxml1D876mn/jqkSUFmWhPEJ4dFhdGaw6OvcOiOJJGkfPk/UwuN9+MpMUI+qaClydA1grY3QJGrw'
        b'uni1lPEawIM6WJ6GLuMWMXhq1zNoB6pNcug7zv3URgYz/dFGAWyO83anBen7v84ZHptvOImX8o2wDnxDGCBnOW44q5xNgyfFxbMcCWgiuxR5El7xg3mzq7R60o7e/9eA'
        b'b3KRNqlZ1pW0x333kJ0r0FbQUCtcKj3HeI3jl6N9mcF9e5zBJn8WJdseAKRnU3k9lyro+VSJXkiVwkcGH3kWk+oG34ot/BZBL1kvbkZHYggEvVQvo2uz3A1KvVzvVs7o'
        b'FXr39VyqB/xW0t8e9Lcn/Pakv73oby/47U1/96K/vaFE6iyFMn30vcvlqb1ctbGu2vro+9LafOCdnPzrfdeTjenIHo399H70Xe8e3vnrA+i7Po7f/fUDoIa+jl8D9YPg'
        b'l69eoCvLBrd5xot8PUFn0mUZzPdkXZ2txCHYOY2KhoF0SvSoHEYL8fxR96u+yKTLMxInbJFKp9cT96DZkJdfaOjgbexcOGSCRMTj7/Bmiq5El5eS5ghXJecadBaDypRv'
        b'JR5YnZUmtlnIlvidHIsWkkRlMBG3o16VXqRyrEgOd/iKdRlWY6HOSgouyDdR17GB1GjKLersb5xvEV3QUJXO3MFrSn3Ly3VF9GmhwWzMNMJT0kirARoNZRp0GdkPcQg7'
        b'esFRazjtTKtZZ7JkGoj/Wq+z6giQucY8o1XsUGhm5waaMvPNeXRXSNXybGNGdlcHuM1khMIBEqPeYLIaM4scPQXivlNBDwZmW60FlkkREboCY/jS/HyT0RKuN0Q4NpV/'
        b'MNz5OhMGM12XkdM9TXhGljGRbGZRABizPN+sf7ibaArjWLZIF39lSp5w4WKmmn9Q0d0fbTJajbpc40oDjGs3pDRZrDpTRtcZA/Ln8Ik7oRbd4vDDmGWCPpyWHON61d0H'
        b'/hi7oUoTxfUtp/F2g7i+5WFrW3ArahDXt2xG4vbgKQH4IK4duKR9njo4Oiw8HNeTDZXHoe3SVWjnNDVLtzdXBvmTraeTNGRpxXqvwUks44P28HiNrZfxy/svChaydv/y'
        b'/QNkOVlwOrlOXhD26RfaaMeyiHDfYF2sjjvj3y9yeWSEfvHN0w1Nmy+VqWvPlV0qG1mrqbi0/UhZ0L6n6MJMD2bVzl7F8XfBfKDbdu9H1/GezsI7B28j8luU3qgF5C5V'
        b'2y/gLVlUOOPL6FInAT1zuEJcwLkHJPMld2iw2qlFJKINTF9UJchREz4k+nQvoyvPh+IN0WiNbozA8PgKazKiWtEmIdbGJUdnsHQntozhaA06ineJZkcpLifbgsdpZCRi'
        b'+jSHNrBxifgAtYT6xYWRYseMGsszspUsPoca8S6Aegc1StAa2RKA/sQQaGl1QryUAa2QxZfQ5STnGoPHmBskcbZdwn2opt+HbrwJktmXXdmvM/52XtN5RAwvNu9gmEeu'
        b'YjjCick6L+pcxzl92Guc/33+3kPc4MPAePjqK+rYYJYydMsBlvADN6c5YTjCimB0XollLoTLTs6xp62U6Vapc6HWA/+HzpJBNbw+P+OxwMoSwZKnOQwa896HwLQH4DGT'
        b'rRkf9OkwU+accAt/ssoIyzXqLQ+t7AVXZWGkMqde18PEXEauEVi5xgIcXf14QDgGwj3NsKLAaKbS4qFw7HfBMZTA0Z6DiKOuHd+5eieLpztOUhbv2F23StKBxT/eXEC3'
        b'6MRO2xR1ZK6kNslEvCcFrxdAUcRrGbK5ZD3ejvbYyEarMxhP4LSb0TEAtZgpTlFSbpmCWlE5ro0hav2NZ3DdaAH4RC0Xm4BajLnC71nLc5Co+fifB9a+RoMUl+8taGYD'
        b'DlTIm9+/e/XuvVF7EkcWeX3+dfbZjNea7917y7PivchXX2h+9/SLazJ2hewbexgf/qZ+6/nvJ71z5B+addcO3Vr03hv/mLZ9T/BfZd6j/VVvNKkV1MgYDXZESzejB53P'
        b'dPLN609TljWj3zzibI2ZlSOGGOIrHKpBBzhx78kX8fGVZJ4ANfh12Dv7oI2+xeVoEz4vGmUCbpIwQiKLTuEbz4tvj0lRmXMaYWV/h4MmDTglZXelOegUAW8eiUxt53fe'
        b'7mLY48VV0XF4QwQ6HK0QGGEci67Ox9tFHrsrzossnh+L69p3XS9AW8QYlzP9nhL3yhyEmgn7FzfLvIJbxYUie0EyNNH9+qPdNE427oOO8bgyFG/utPPe4zBcoD6DKcNc'
        b'VGClXJdaHO1cV62gmwiJnhM6cdeN6Tlyd1za8Xj7azo2PW7nvS/C5WAPvPfO4/BeBxj/H6tVM7J1piyDGH7hVIScbKCLkgW60uPqVybD8sdVq0hzu69TFRIdZ8jEoxMh'
        b'VNbjA1NF3cel+QSmGaXaUZwlF5KtSPPq+2agD/rhk8g+s3793bdTx/RdMnP7zdSQHUd3yYfvl64xzn9rBvNcdGFbZFbLtfQ1x7/N+3b6Ire+WycLRefLbug+e/mr/tdV'
        b'f4n+26eR6evHT3mlX82NSwcbIr4uOOFt2f6927dBw+PvDx7xfbVv1JWtajfq6whDF7OpLrEKSFlUUVZI6OTdxFFkF8wkdJ3Qazg6GhbMApdazxvwpeGUBKLw5dEiAUxF'
        b'DZ0pAO3DGygVzcPrSUBnBCiSeCMqZxkhgkVncCNqsBKPFtqOqvEpcbvguCS0PsKlOYbiA0wkbpRORHuAWikhX8F7FlKFCLfiSwxViAY+SxnENHwitaMqFYLWcWiNCW+m'
        b'ZD5hsKWDtrQAn2NBWTqHboj7d+5Hh4dT5kZYB25GB5zq0nbfJydirwyKiGlOrOlBg1JM8qTBYAN+CuBWDupCPl2yiyXveijtmne7iPYIXE71QLRv9UC0j6hVzbdJs/Mt'
        b'VqO+zQ3IwmoiSkGbVFQOHr7ciBK24FpqJHEtNZI81lIjIOx709kutj75m6bXE1uJEGMHLUO0M10y/qEULTZEpOdouI+Z6eQL6TpTTneqdjECR7vFnMniT8gcHGczgZWq'
        b'iZnZQ7RRh8glZ05ik5NsnSKV1D3BazZYbWaTZZJKO89sM2hJwJG4wYI+TKWdrcu1iM90ufBQXwRKD9G9TNZfxJj4ROPowZcZC/Fl397c+qX2+Zvv3Lpz6/1bpxsubWsq'
        b'ayqbWNu6s/WFC7X/3dZaObL2SGVTfeCeNTWBFWsk8t07/f3X+iv91xle9/f3j4r0qU4pTd+jYeK/9LDcvqTmKVm5h2Cy6PsQiQvszD3STaJ4vYD3yAljQE1k4sXBGECQ'
        b't4q+2qO4ckFcfAyuWoJqkhLwuvhwtCGCBqKqUZ0EJP1R+ZOTp6dOr08zpBszLFTVpdTp04k6PePIDMSwn1YO7EIjnXOKFo5UFJpHyeUYuRzvLG87ntMhdEi2zJWWkm4L'
        b'XK71QLo3e1o++bNg/Z8S5zM9Eedc6ikD+jSJCEni6zpQaQcf2f//6JRki0lJUoneLavoDKPWR6bRpMtV6Q25hu5BgY9PoR8/8JFQCg357x8eSqEifW7yeTSFfs7Ev+2x'
        b'oKLCQaHDp6JzA1AlSPguBIqaF4t69WF0Gp8QZXcSbnWK7iP4mJUslsMtC1NDY/F6vD4iDqgcbcTnO5HpVLRB5oN34/onJ9Neov/1EZSa6qDULgpeeLfMYsknu1Ck+ZSL'
        b'AE/D5c0eCLC1BwJ8ZG2PONKIrWI6HGn0eDvMl4POm94D6VE8pDRisuWlA7kB6nXwWbd7gjNsZjOIityiDib7L8XKLexp1hIND97Tf/eldvH26JunGpooRo7siJE94mPQ'
        b'Gx3w0Z+585l7y8nLgI80WGg7vjy4KzaGGwAfq7G4pAGQae8MER8JMg5B5wAfe+M1oiZZi3YvJHYeGKiixDDKnMgYIgVsvCRT4a2ruxxm1SP2ZeTbTNYOI2rpAfvk6Q/B'
        b'vm6ZnXGTyx4qG0Q3B8XEs3D5bXdM9Nz/GJjYreb/A0zMAkw0PRQT26OqHxsLVcEhRLEzmlSF48LHhPTAqx8PK0/al/IUK20HxgNWtuNkQeCTYeXnzJ1P3U8M8XRwSRsn'
        b'6YyTYIVsplyyOo4iZTI6TY79itD0RxddakwKqqVIuRytQTXiQYwOLWauZztOTkBVUnQmCF1+DKT0Jj37KJxc6sDJwV0wo2tesdxzD0fDC3D5pAc03NXTvmCPqEzdr+uq'
        b'bVlamj4/Iy2tTUizmXPbPMg1zTll0+buWlJj1Jv3kExN5EJCDcwHGYdruE1eYM4vMJitRW1yp3+VRme0yRw+zDZFBz8i8WhQC4nqWpTfU1KjDf3Fm0Z0cEpuoagCHRZN'
        b'EVTgBHeBbf+Xc31YzkPKcqTT+J6/fQS5ex9WqfRmlZ7erKenj5zOroySdIriqEab8bkEMJbB1uWYYLRGUoLrF3eb4SGUH+XEkM4TzOJev229HatUHKNH9/l+oJq1guw/'
        b'ShypGWQJitlE9LkO+lsi2KGdR9N80dUTXRy1N+HyJedaZQ99wtrIXjWBSrS5fZU9PuVsG5lGeXEMjceIVcjIXlBNNrJZM67mptEQ6vbwabxR+gQR1PgQ3tONF7o7uQgZ'
        b'McdaBKbz4bTtOyT/0tXqpKLu/mBlopqnQTVRJQqGLHr1HleXvTnvI38ajTquUOqMRs19L/6vvoeYXBJnPGvWFMnnfpeyfprVX30pJznt6ODDOZcXrg3elfjyhDGL1oft'
        b'TTox+eCkJQPfC9mf/t+wBwklHp/29yi+Ov9UcPmMsbGfJRZNuzdIGqAY8LuF01M/efrK8D1zpzKfhfaeHDx/xdTzQprPwYKTg9PTfms8Kxsyv1lrmBCb86bb1zFPhXr0'
        b'y15olpQO+XRmoeILS2FBcL+PZh119/e4XPITmBgToiZ4Ulc1vqwDznja6PBWu1zVqNGfNrVyNY1S9vsHr43/yn2mGFTkBR0Dxl7ULUZrv/zUs46QT59+TBikvBmiXZxs'
        b'KGTo+hgEoh9dw7UJmvDE+KT5wY4N1nB9nAxvREeKYLz34ZpZaKskiEHlw91wk39fWppnFo1tzo5N0sbPS5wlVnF6uZREQav0am18ojFV3PfXpPosg/nDPEI7bNuvjd+f'
        b'rBQsZIGc6cP0oPWtnlilnPmrHeXJNq/DcT8duXH3xHPv99r27q3/un//np/hm89/v2j59L6Xg788cemTlt8Fmt554YN+8qzqksY5QUu29u+7Keje1/WfVenz/jH2s1if'
        b'YcPmvdhycfaztabfZz8oKwz+66nnd/3x0JyPfKdX/l5zoLVIl7k3L8gzq+61nbqIl/7otq1xePmXC9SCqJS3rODQjbQ412HV1CuNNuGLdBO0Eai6QIPLezjKnUY4RanF'
        b'jWUPDkbrQjXkCF1cgy4uxPUSxh1fJmGJG1G9OHV5YUJqKF4XQhxqUusC1MhNRJX4ePco+F+6KXPHHQbMFl0n5zdZTt8u1gS7grq9iePbm1NRZkruzchZDDkjnsQhdFCv'
        b'filYR1jzSy4ORir4V3cxqKp62AF4V9Axc2hIIqpzagzJ6DAoDf3RXgEdw1uGduNCPe2R2YELufbI/MWnoPU8I6VwcqA3JO4ODhQf+rcAr3zKgUqmtMfDr5pl9PhA5EBD'
        b'7P9DDjRgKYefUo7pM+HiyIoxrxQXJkwIKgn+n3Kghfl14rL63mrCYZLnShlt7tFUR0D9TF9yAltUhhujnRLgk8GYiQpM3+ykjOFmPh+lVaoiVosPJ/cnyyMKYj1UWmUc'
        b'782IrG1tIYuvLevG2a7hC8bg7WoJ9dz/MHug5o0rHjhSKbxz4JXcxG9fTBih75t/r++dS5a8Z82lb/i+dugQM37Yir/eL5zuvbv4yLvfsUl93x4/7i8RvwrdMuiFl96Z'
        b'28tyOLsud0Vun6e+6n3jrcTaQxMf9N02a1HcD0N+vPvJje8upV83hdwamPWhXM1Sf7hXlu8q1BznPJFevoQz4LKJnXTJJwse7kqSekM7SQ7rRJJAlF5ycnQFJUZClkox'
        b'Upc1v+wqCP8CCG67aI+UI+cdp7200x6zZsA/eqA+kghXgj5wSSS/mARCfVp8g1CfVkBN6Whnt8WL5EO3LY0GsqyWiAcL2NlGhhBdE1fM0XteL8A9b2XJ+5nMkrWLuWKh'
        b'mBw+IKlmrBw9RmnsSpld0sjrJU1sseRZxpRDtvwvGiMeMUXfkMOnJIsY0/PLgWDNm2huknO+nTdPhxSSJvGYKSk9tcMD6pAWy6pZu4wcTaCXrYf0dukUcnjUUzSvBPJa'
        b'IK+WnJEBcEsAPgmFj+SVd8srh7x602CaV0oPiHr8fKXVUjEt/Gbs5ByOPuIxDPTQpiY7o3fzB67iOJxXkQjM2GAomG2m58k+kNismZoJZsJlADdfIWNLXphJvJF5NENX'
        b'rZNY8jY3g8mWZzCTMzrI0rk2KdloX29oU843GckNVVHFvDNE1GrfJbO9WHoEAl2T9Sy5kKXrbezSJ91WS0nOx7GMEhcMB/COPZzkvLiK39NxVgx8/yTQs2PIYrM+5IQY'
        b'ruO9eCce7CF3oinagjeOjwPsjNGMCwnE1WQfA7owQDVIwK0zDN2CJVzbhRNz0w5cXM+mMOR8LzoEnOvgDNqZ5snOhpD9hC0PsSY9aPPSrPlpufmmrMm8Q0knIfierI2c'
        b'GVKYgSpFIMFcBSWB7s5I1C0GX0SnhqMKSRHeltXtjCZXZNkYCquezWHNUmJz6Hk7OVmL1QuNDDmzCSCX+DJNrJ3txxDpRp7QSBSpox2EUT/gglbQxWifc2KDJCszjbm5'
        b'aq6NNbWx2Q9rHGkTaRtt5HTSOAUdPPFoHrnjXJVGMM6JaU5256ynTUyi7ZUyo9Ha4YMkRej6oEesYGZ7XMH8C0+NZDsW32EdaftqvPMxBcxdZkUftkCb+ecBKeLDKdrb'
        b'gAzeWcoordt4SbH48NMwIseSraxKG39mWhJjHDVax9NDXEp2v/mldglxj2w+V3ak7NzOX1cELuBXnt/WVNlU1lTXGn22zMZmeMxQfDL9UOJvpm8IqJTEu/uvmx+4f2DY'
        b'wDfHKt+qU8f7RPns54Jflo8KqlikDD5fOrHCEJgRyWdNYsJT/GOu7QZVlbrr9uO1qDxUg8uWBUc7lztn48M0/C03HpU6Dk0kJyaS3cfIoYlky1Hqd5GjF6fQDVBq4nF9'
        b'GAvqafMgdIzDLZn4hhgTcglVuqFjsZMmEFMS14CaupobEosvPPmK6V55+fqJ48VzSNL0xixjTyEYTIl8jpIGvonHnviy5t+4iql9nArrnBXSjHE9yTbfHjzOdLvJAVEU'
        b'WdcnodYxdCdlci4UOWnY0T1oLdo0Ab0oXY0bVj6cgRDNWGQbRMY1sTTimktsk+gsGUYjqL6vM04ZPKxzF8myDStyjZlF83lHBJwnT3dZ0s8jgTl0SzgABR0TYKAqFiIw'
        b'JS7jq9aHQ0LykoN3qAxUkNOqCDzFDugoQ+MSzR8yVCGf7YTq57Ypc7OZHDCmEhjpwUE8iZgRmW7dSn0oXu8CFVWYKLRka7i9aJ//E/WZCzbznYf1l1v6uDHiUWs6KMnc'
        b'Bs9sjiM9WtCZuFGjY6gBhyvRVaK7eQXyk3Fp94DFx++vchdMv32s3gL4RPGaSeD7PYGPkGUJPofOEfCIVimdSKNecQs/cgLa0S2KznVwIFnXpGeBtxOViTH3tRLOz5dx'
        b'oFAwxbx4kJid60ePJbNI7VxBgJ0lx3o5jvJqGxY5ctToMWPHjZ8wcdr0GTNnzX4mOiY2Lj4hMSl5ztyUefMXPLtwUaooB2g3U6WBBf3AWAiUqxbapOL0R5skI1tntrRJ'
        b'ydYco8eJqoBb14aPHicOTB7vOPCHLjwTz377UcnTbhiJ6gbEjRonWtn4tJSOUT9+Et4U+fAxUjowRS+eZUUoy3zPWTtwpU96xJPR48RxWM47NvhXiCAAspaj7QQIMhSD'
        b'8sShaOYj07MevtEkPUaddR2jDuA81uaS3axGhnnIGTv0wPMt+NgKdCXNuRYbb52f4DYHEOfUXII9cz3QBo4JxheFvNBpxoKAYsFCVLQHHjN2XvtEf1+7EISPjs0AAfOy'
        b'Vvr2GCa4RHhqd4CaE90bUFrggnxy/PYGXBshY9xGc6gJNeKjdI7IhM6gy6Gu1Zb4Et7rWHGJjsx52GHoRkt+mtWYZ7BYdXkFLre5c3cm13QiZ77vykhOUe5Zu6CJ7LzT'
        b'SbGm47/yp4ecij7YBx8lG4htoIoGAK4Jj8F1GrK1Nz4/3Cwpma6e3S1grrODkncEzHVwT8JAuz9hwGq3bVNEL1zXge6VSM9BRy0l6FgcyOANuE4A8X1jXgCnQKdzqIqh'
        b'9yVuugZviUprz4sew9AQV9QyYD66NHT0KNQ6KpIZwsgSWbRbKKbLo5T++HR/VAPvzo9C5wR4ibaz6DxqGEV3LMjHuyV4s4TBJ9AxsmNBb9xM62l5xo+JZG7mCFrtlLhB'
        b'jh0C9s0PZpKZv01x12qn/25irLgRIKrAN6aTnQAH4hZmMjM5NpemnTeZ7GEQHeyl1eZGzXUTC/DJIdZ/wRxFlDZs13R/QBva4gh0kYuLQcfDpIwwADWgchadRnXoBZrn'
        b'XzFRTClTrWEKtD6vPO/wGKStJMv4I61CpHbuvpm8+PDeUuJfPDXQU6VVXunFMcbSf+ZylvfgzU3l57MS34rlpyl/3LTzo883nOvnlfdHfCD/3jThDzfrp92a7nVMtfXN'
        b'29Oi+xZX/n782IMHfa57f/9j+p+DFCbda+uavjl1atT07P3FrZFhJ+TlU4vWF39U+PZGoab35N15md+8MHjRuzPX95+/I7S/W/6Ki+OOnr02qqXZD3/0QczTlzKf+XBm'
        b'+XfNLQ9u7y3p803A8v/X3peAR1FljdbWazqdEEIWiCEEAiQh7Iqyr4EkJEF2EG1DqhM6JN2husMSOwoidjeroIAig4AKIirKpiKiU6XPGR3HdXRsdZxFZwZHnUV/l4zK'
        b'O+fcqk6HJA4zb97/zXvfn/5SVbfq7su555x7lg9u0QaevX/CH3tP/qhn3cjZu64rTfj9NYNvXLbhD3Nv/9kv+uwesPfYC2s+PflGjnvD5XVvPbCme2jIy/uefuLHjz2u'
        b'PT3qpl8nfvdG74r3Jr6xQMw3EzdiUYl2ZkZVO25ErnaCmYPbMbfEwPVmzjD8Yy9aQ+muzZ/aZkSuZRVqdA/QTjNr7ju1QwO0Z7QQSRXHyRQHejM1jSfs6lFtp7WdFoau'
        b'gvFANTNOcniU9hiOqPag+ozECXX8BO1hbeOlO8X7d/A3ExthV3K7AA5decXQYQSBkHxoD38ki67sjDuRmAW7kZmXhFygNO3kIjKDzyIqktSjeeFr5bxRiG6vJGqv8SnV'
        b'bhc5uWxjhP4rLukE5WOOi7dsgmWt7Rzo5fy9C6A3tjm/cMagAhIWR9D3+NARQyVO3aee7sdLMLRPaadp2WpP+bRziEf04bQNA/pYtN3Vhnok/rWTYkI+QZhH16YRoLPQ'
        b'HWUYqUpTUFLSgib4l2ADNmVwqRArHeIEhf08SRnr59xhURaNdOtF5rUaYonKsLC0Hz0IiwcEyJkhVFJFB/I25mcVpx+5ILYz4jUIGaaT58suHRATOtLFpoKOuu43EIAs'
        b'rjlnab0PaBEmWNSZ12SGA4lRU1Njo1tRcIuISkQbm6NSwL06AJgFZuH3NLujNr8b5Z0C6BJ4lUcOLFM+wfii7O7oEhkq+Bk+fxqbvY74uvxI1I2MIyvESlr82bx0QRLR'
        b'UCGZwfWP6F+GztsriT4J3kTmJcthcffW9knaSe2ZhA6IZKxXcXgRkSRMlwNM10EcOHQkDsO9H/sZNihZxH4m/pygDIMhFmQJYohBER2wo7fZFhGHknIogrfkAB2/Q2zY'
        b'EWUTDa+5onXg2CUTVjfUDy6cQCihx1s77prcAdcOvOY6uBbm4/PggglLJownzPo8VpaxrX7CEb2HhEnU7HdXKdXLoqZaxdfUGDUhzwhu9b5VMDAv0vqMilBK1NKIQmKK'
        b'N2qCjoQEVqPQH0LUk9HGJKR2GZGPijonSBIRXKSSjQSD+4o/OmNV18O2dZzMNarHSoF2DGtb1EglOzUiu5oW7sp8s7q7wdEO8Wh3YHmQhgNwdSGVQ+ydERvKOFTYUVLw'
        b'up8/wPnTg4IM2H2Qc6Eqj6D0xit9yQ0Cxu+C/6nctbYWImAgNzEdBobnVvSj2FfEYo9hscm3PLITeWUmxZgei1HRPgb5z6qBdRrl7a1CTg6NDXQmzd2vaEkEqjz1sEwk'
        b'd727AcbEvdJd/wPrMOpoVNwBVEDFLn9K1JkADpHZkkomL73J9CxdSEXq8kITIvQr1WfUHYUDS4vyyUrvEfUo9P4x7HOe66MeNA1co27tWgccXaW3HdEDmOIWi26JfHJy'
        b'6HfzDrHOXGdZbIV36IsT31ncljqbbDFC6KsTQBxqgFsX2+VcdCIB4QTZcYttcUIsnCg7IezQnUxIIWuNSU6SkyFNYrt33eQUeOeMvZHk7nIqvElqF6uHnAbvkknzm1vc'
        b'Te4bEoHwQN1u2+IUuR+FsuXeEOou50EaM9QgR+4D4VRyadGDBq9/NGEajI3bG5gMRFu7uWjwE+cYALeNNU9upTlZMp4NSpJvoTlw/gL8tfKjgRhAHxFHdI93s2ODHbe+'
        b'XLReybO9v7Gq2v1qDAwLzVlxVRt8ccROCUGqKxKVSKLDvGUMA9KvExQbj1A3UFXbmV5b1NZYX+XxuuDzm0YVHEJzj/gqxGJ0KFswyk7hmEKdz2KsT738I0LU5MKdgVZG'
        b'p5p1uG7eNRg8yWJzcnzZmLTD8MSKddDwIAiQYwXySiJUTbHynZf0a6Mku9CB9omxketjw057AM9Yx3Re0Q/PZ5iL56AoC8sFpaeMzAZhLLpuhtWzkvMPkU1BEe+wC/B4'
        b'BgNvLCxVGmfElXn0dq4PlLWilR8S5QtahcFDYMjI2C+uVMWCg8ff0Gq6oaAlz49br7+x3hOI2oGsVAL+VR7YVnEbNlSvyGo9gpoo39gVo9oF4AZ2ZjcZxP9Q1IfPUPGy'
        b'Cz35ZEFYa+ebM9tNxPhUFe2sgIrxfZdtTEPquwA7MBDIszssG1p9PPpRz8SWmfxNgEggDuGVDWFFbELUHpvwXRwmKL0g/V9wMCWqfArffuJgjv+eSio9saYWzLCqvl7J'
        b'4rvEp3rDpy+QsYUe15u7X1wdSN0ppKEaoRfAMEyksIQISJimdR1MwC0C1Y836ocu64MGO/AIHzV5/Q1VjVDVPrGqmpm/A93jZtTiZvW4NAXsXMjha1HXkbUDVYDIVnNK'
        b'fFtY9l137lDWFCHWFCHWFCG+KdjV0BiBVoBQoeTwtI/GNcSDhpYC+frEmISXvvylqpL3g5jfx7ckpUNLWP4dBiXGg0L1hTDUNCxCS3oYEEFJRuSEeZxvgdYghojrOCDo'
        b'00iMrWsR1vVEhiBISjo2DJFN1roElwuwLE/A3eByGXtFOfePzVAq/SG1JOnnS3YdD0vmm9PbLde2zLseqevjJ13GD7WPjRVC2djI9tNHFrZCGllRH1kpPjYRNEoeb6Cw'
        b'OWz4qCtc+KJttKE//EaVjSGPmbq8tCEfCPkkSPpeyHoGjZ8zqwHteydW1D9wlmpwueeyYjrbQq0u11Kfr97l6oGYOrIQmlPbF8Y+E/4+t91oGHQIJiKkLwwrJcjVIPrL'
        b'I4K7F3aZ+/itrBZiRTF0zLdcDGVcA0DZ4w1EkxBVl93V9VVM8hS16gM+doxs7AyYTCnE3qaj64s4wmbFjZ6PMo1pRWaRLgCFfaH9imHRijttBE2pnFgjZJo2srBFIiKJ'
        b'ZyINzKNYRVSqHjbSiyp/zI1S1OZeXV3f5PesdEcTcVdzAcGJpfo/x0rmQAO9/nG5uXRAC5BtEMFk2JHqYYswmjgUWzcML990bKIyGD5cJsXgAbYNMJ12mwbWqR00wK6I'
        b'ESY/h4uHjhOQFQC4wBDWMNpEJJj9QMwfwMNxPpNbIrSYWsxBU1BYCVWilWLKRK9Lgj+fPdfyeB+rfwGYYUbQvsIcNLP38MTVSSihASUlQX6WFiuUbA5aoDRL0IpdG7Sk'
        b'cxBzDMS0tNiCNuWaIO+fC/TpoqANvotjOa8QtCHG4q8KCv4qmWpfB2k9BrOBHXvjAm019UVsK98WdcDKANrSUy/DcEctAZ9L9lQHSPyB9gfYYQIwt5ZGbRgRl5GfsEyd'
        b'fOeJ/0N7j73a5/UzhcEoL+NJCWQa5asVO2YjVMvMrB2hyJ9yXW6sV0DsXBw6FOeQCN6l0qGok9Z3Cq1xM8+cEqJLA6RO22/AeiOOEEpMCzFfKC7O54vz0y4WLaamnDWa'
        b'okixliXyjPBGepqhBr14fdunfqEth8AzQSIlHy9FvD73qBVxnsIumRkY50IM6/KyqHeElbOKggTkoCRgs+HJKSY7kqVUKdWcYk61WO1OySllmOgIsLi01I+OVLeUa1sK'
        b'V5QO0h5XT1SYuMyJUnGxetvcfJ5IyiU3FcUpV2nkixMSWLVdhflmbrhsnjv2cl23XH04QV1bFsuS5xJu1I6q2wTtaK22u8NZEcIIEnpKicEHD+AxOmir0Y1wNFQtd+vY'
        b'ipLTCZSy6CM6SdJJlWSBvG5r2250+eOqYlf3aQ+rOwVtU1lVpydM+OdHNDlGASeT60MUVQd6FyhLCWhXnlk6W2xiCow1ok7rmtHeGcSxyA45Ee5W2Skn3YL20lhjukUd'
        b'U5saGtbote0cWaYtBjViGAEDmy8fR2XybVQm4z3AVSQ+hKSTOqYKxRTbVs28TivgPonPJbHp+yl1nAtRd28MlaLlZ2bvLqaSUNGhxICTZj4bFhYsph7xLfpXbN0oU/gu'
        b'9k8bYCqsKpXGuJr55rR2BcaidI2s6QehhITopRquSqjNFZ1MKIaDITRzuWZLBmXIN2dc1NpYpK6LH09DKfNAEZpRJo3wRoD3SkqYOgLJcqwYDLSAnEElk7Cp+AqLcdAY'
        b'uXPYYdRrhC4N4H/wcJ3gzjwD+WEg0Ensuc7bc8nYD8kdjIiV1dkIWlyuerfX5brO6EJAtFMvKpIidM1BwMYEuFpDDIPggYTbS1coF35zuaqMGWPtZIpSjEtoIZ6ZF3fZ'
        b'OgLjMqJ2pUjWXVyKjtuNZ7veRVsJuY2dhqM3PbY1lOBlZmx/0B3SdTmsaJygWNJFQqycXbSaHWKyaLVZRYdIQFu7ea621Z+PYFt9OKBtqVD3xCBhtvqkpO222LqGgmj6'
        b'zICCd4h1Yp202ORmYmXI5ZPcUp0FUDc9RMf8CCGti62MLwdQkUFJG/HX7DR81mhK5dI6d3WAbP7pnfUvsI8URxdAg8CaFwfFiYOS3rG0f451dAsWlvRDjCM8p1aS4eMl'
        b'Q6AaAwIpxXxHdBQnxCrME8WAm7M7acAPgZ2YNqICl2ZbgNOJL0JGF0CLJCBH1/RkosAEgMQgHVKsF8zcIvbdtGaULirM7zcT4TcU4ljaiL8DPItrtImFdCnCNqIOMJme'
        b'xuyO2kuAQFjNhGYJgOHsjzonEcLYFNDFadtI4UuBas1STHoiBZC/VEIA01AO9ruuO04nJBMuXpLl7dA5hudNaL9CL8mbK+azrG1dtiFhDjFDZM6aI+oh7WHtRKW2sbR8'
        b'MHolUG+dqW2aWb4iDlWZrB629F25puv12TNufRJOQkeKgKeI7Bgi2svoAQMoTUGzpDN9vuVNje3ONE363OkeW3L6dhVuO9UAUN83BpVMDImXAmsa3cp+fLTF2HKdbqfm'
        b'eio1LBnqd3g0dKE59wdqOJgl6UTDb05sIV60cmbBhw2SLjli5ZJF8iupPRa8vq2vZ6pHA7FeHq09uULbWjJosHYaBW+1bYNRCGbnCru2Z6wa7nASFWOPoMcW2MY5Ync4'
        b'aYXxjPwL4tEenhWlhZEA5MJmpGzDHD2bDjBtR771uylkSQVVlKub/AFfg6fZLefUAzGbQ4fzSs5Ad0Bxu9Guq69tHud3bVOWoo9GgxNkjQZ1nD21Xp8CZbRxTHOqvHIO'
        b'EtFoH6NKlj3MAVdOgU4EDcwvyGFkd3u957gqtC+iqr7et8pPxm+UKnSeheZlvUWGLZgcHWf3t88OCC06qhQXls+ElYQ0eTQhrgxiSfyzzuPmweBvl3Rga7cyH7AoH0++'
        b'UlPUQyPVTdqj2imAa9pj2nZ1D6cdT9BuZp5Uj2mn1aPqJnUbiyFOUp/28lfPXNi1q/Tr4laf3HZeZa4x0UmZbbFIMlJm2AXxlMwKO6RE52KibJGtSDvINtkOtIE57nTM'
        b'uthCe6WVpokz6tCXRTmQP0pFcQdzKrEJeR+HolIemGgyv1dskWK8uxQgEHgPCkNytTydUCBJIShTY9y63kFB/wLYZyYHZIWE/IGg6B+FTxSWMiF35EhAWxj3TwgKU1Ha'
        b'wATpTEYc4k5cZXBy6wTZDKSchKRcjOdnQeb5bFzAxN9Dz6AMhWx7N7QNyEbtLuJiu5C/TlsJ4k35up0bin0ZcQgbFXeNZ7ULBS1JCyMqeP2Xblf0AUnXKBIEAdk/39lN'
        b'VrL4jSiymRjdySTsksL35GNHYDQobQRPPLCwcHFCIoc4lM2Q+YPYywJyiHgIoyAq9OAUxh9C2QB/JvGMJOL2OAJCUEL5AaI+Acvcgv1daHCP9kuo26OMphQwv9ioAEgy'
        b'r4fRphz6wnsLAPFijMO+6O8JMKH+znqBvVnhCLI9wwrQNmqagydIUXGaV45KFeh53TS/qr6p4wFjDGViB4zI3ZKFlZzOkWQiIYKyBEfputjWwXcmBktGNH9qYOwOrrmo'
        b'fR9X+7wAXAIEo/zx8ifMxilkSvzgNm7ySKJ4kQ9IQElnTvnJLSFjVyGiASCG9jHR714RNfkU2a0gv9PfVB8gEqOhjQn1QzIRzvb1e9qYTVae2aa183acVwLZkP/eLmah'
        b'Io6QYhc+k7o39/qBlnY4h4wxU4tpTuGqhVnRq0UERIwEiUj7Kw1nGXHnxQNszKWgKPMreVzr+wV8S++M8xUkcpDhCmixG8bc6qqpR8kQL/WawUKtwr7FKaDI/wAxq4Xv'
        b'7xn4D7PNm0K9IKyVOqwevahOt1qaWyj6GqcDB9cgtsQRJKHh/YiSigdQtBu+sVOHlbgu8EmEp34BgExBIQ026Jt5EtwACHaAJ7QXVgysj+HI+/RajTcYB89hZRN7gjfQ'
        b'q2kMCTJXsHNXAeg6nGetafO8y72+Vd62PTYnN8+f22q+Ic+Px7JmZQR2WRpNPwbLlIX4ZjKn47kG44Vm2uKOJEY00eVFUSc00Q0ZfIQdi3KKTIMrmWeHGWkIpoQUvrln'
        b'++6NT9oBQsVYbzVc/KEnzRxEYxChEdiTh2uRmDyTrpmHUAhTkIZh0ByUCPb3CEjspKsO9gXkYx/kZ3PGHmCw88xKPa9PE8VNnAxsK530APWOdu8BO7fEsaOsBsdZGYVB'
        b'G+MxQ4vilmfn7OEGnh0D01TEnrKLksD6LLsjINeLFitgOdg6JdjdsYpTExra0wSXhLC00QkLIPV9BsJi5dKk5B7Jva22NCfpbvefZm5jXGr7td3aY+XaZjRklZ0uqU81'
        b'ZnRqRR3/yN1mDDVJIsLcQEmYiwMDIcEvFyMjSEjoqAgJ6CATk3FekqPWmb7q5cWeeneFglRCO3SknZhEKcd4uYzq9NsDgszTAmR0tUDf6DA0DfmXMLXgaiIuppk4mhbU'
        b'z3NZYxJVrd3RlXGO7HPrzgkQwWy15PkHozAgDhcJB5g9foxHqytqqVrqR5GEqJUEBmWPErWg3L2vKRA1uRrIKw95SI5aXBgD0Os4WYmohDGUlZ0Q6DgVTCZ9VuE6RO+V'
        b'ZvrZ+eZuRid1zgtF4GY3+gldezD5UWQCouahjWu2hnHZAThCML2A8w4j5d1JPIApnmvOC8LikoXlopJ9M6YyKwMXAPWNQOxGkkTT8+OXS8rwAPQj9ju8s8oSy8+I67Wz'
        b'+yp+FZ7IUc/P4VZYSXJp7vluBN6qfU31MvV4VTX5R8jBnvrDnrvw78iEfBvQgNCl1E1RU8Ny6GSlCZ8tlXOIoI+a3IoCUGgNvnTMbvJidP2Lv97tbtThX9QCWw9lVdfl'
        b'co5KWHiSSZf7Ra1XgbRf6cyONGZIoXKt8I3ZJvHC582JsbHAlF2ryjDt0DpO6UE9gXOXN8ZASYfxkIzxuEjWD3dOEzWOTRqTxx/rApPSgM/Eo7qYHG7yYoVyTPrqZ95l'
        b'AM/8ThKak2KVZrH+Ed7FMEo5jqEe7oqhjpaO3ADj+psMVItvTo6br/Sx624qiCsPJ6zOwRYYB5sOIqCbYprXPNLuG7Auq4wOUlbHqnax5pHLBaAY+bL5JkNDlnBvMwln'
        b'xFVSj9ZBGBr/UceacC8azQSDaYjdw+RB8SCWb+PswexbTWNVXe8DNBE7zpCOkVzu1dWdsJcB9MCaHmqKnYMgieBov+5ZHOSZIJzsYjOhnqGhiuBlI162XArjtxEi8SaD'
        b'n885Jafd0Q2Zvw4LHcBlDAVK9wSJPK/UnaAn1ol9tcfs6tkFHbYNi34nddwYPwnF1CWgVWM8JZT+XCzJySHm70cMmUPWGjNxeG2wfXRj1C157MGzLxtsJcygG56AxdO1'
        b'tfkpUal41tTiDmAxho+g3FqA0zEJ2DQAgxAYFWkMINyhbmGhTkKlbQoDUAyYWUjfQjhD0iZh1hoscHjOyjx/ayIEdIfoEDRYlMyIF1ovbayqdUcdfnfA1aj45KZqoAkc'
        b'mNo1f9rsOSWVFdEE/EaWcAGIJbhcus9wl4sJtrvQvYyB1cUsAvzgeMJljDHp00ikF2FacyIW2zmB2RXHWj+0aO02B2qS01DlJQugaIsG4cKutunNrMpcjGpiy2JtmAxV'
        b'Ir52cwpVpN3HinbVMXFxjOd9caOHiw9NqQcFxiCrE5QhYaBr8Qll4IEuFYGWBURgPZOYp+cWEbB8MZ1D0Wx6C6jBfjMTEyG8lFdmhgHDlE3rhW1OwEyl/ZagwLY3GaaR'
        b'xK0XmfzYMM4/fRXPmNmLOF2mjPB4lKD/nAQ+8vLmTJs1Kedz7AImPblacdfYCcGPCquW6lMkagbEobEpQL0YNclNDY1+pgqM05XOVaOmVSj0oLNHGcCjfqYkQs2yS1cC'
        b'V/bi6Y5Jl0h0EpLhoGnhIHE1ZGzZLwAy+z3sGAk0Pqx6UdsMd/1Kd8BTXaWg12qmp4oDVG3wrvAPFXJixn6u5xmNdQClungaM8TuSfobxkPU1xv1Pz0DRQUYv4hfwnzA'
        b'BNSlKZVDOVi018HCvVjYKptbbLKlxc44EC0JMBcSSF420OIAusGRybUkBm3KUiNeMBFG2grb7kzZ1pLoTaKwHcLXyAkt9ljZVix7xZXt6xJ0BAF1zeCWc4oX85Yd6Vwm'
        b'1+iDnJxBp3KXnBh0Ak14V9Cpl7Ep6FDW4dGGDlMgL9kZtGBesthi8zopJpZ+F35F6XRWEn5FeRnZEjQFE4N2QBhsdXhNqHPI3baYITe78hDGgjqaGdSrOI+KKuex5+ee'
        b'x9H+QyjtnZ9/Nee/JhQTr6RVHDduHA1XVHQBNOHnMhqTz4nyk6OWKb4mxQPAiC/JF6Imr3uVazW7rclPZNoFdpIArvd43X4GpBqqlFqP1x/tjoGqpoCPgJtrKcCu5VEr'
        b'vqzxeQEZVnxNXpkdvWzHmSpVu+vro9LCWT5/VJo5rXhuVFpEzxXTFs7NT2Kzm8QHJMpAIrUekz+wBpDpBKyAa5nbU7sMsma1sWMEVz1Ux60/AyUMRZgUN9Qial7KeC82'
        b'b1ODi1IwSWUJn+Gte3WAXv9DP9wJTAKV5Mrn4uJBApG5/3QQgpXMzB/q9k8kncHHtNzQhkoWGQ5iTAsznZOzpWa+gOYCiYGRTIstrqBOuTS0j63m2q8rOkpz0jk/kkV5'
        b'shDhUFMrIBLZhXusFTk663VzJJmo5sLL5iCfxuQtJdmCUC5g0jms5nZUtqhzWq2ECdpae06uUlCVO2eEr+YqxvYnmxL+pgYlBca5tfBSFN2LBuf0G1KY1wHdikm/ofIP'
        b'6Z5ZWqAtjIuga53VGDy/SVyb3tnYTkgqVDi72UBK07jm3tTJWPkRV3Wmb3Yec2qVCvL8BbR2KoD4/hOns/VQk0kmCfioCG2NOmmme4C4r/bV+xQdmrPMDZKPzv3adut4'
        b'o1W88mGsni8jpIyhXkIqqUQibyuX16Ewy5ad+kvKfmxrDAwrB/guscE7eR3oK8/zekFxrIV/0mxVG5NhK+QzyhRjMiRLVkuGlOpMG9iEzjYqHdpd/oTGFSInTL9R28P3'
        b'0U5rZ1D2L4YYVBCSXFFRgQJxYhNCMDWiPqIe0TUkIyv7qBvVPfidVI1fXCDMuodwgesH3ZddyXkudFsi+ncDejf9xpvK53rmdF+U+mlev/cX/fLxiTk/NjW9t/Dmtbnd'
        b'ukdyXns0486eLy06e7rnqudX7D3/s+CMBz/7NOlby7eH9321+v45qaHP/K+87/vdNfJLHz3bZ/qhdY/csW7YO5aVJWLGbvvQPtP2D+g10fXxs/f9jJujmO7clTK076Zn'
        b'vUf4G+Qevyw88ez4d6QvX7r812sfEi0fcVf2271WOy5kbX/q2asXiTXuqxr3ue8dW/m5eHbba6tf2HR89Uu/K5re/bJj7g1p5bPPVZ/6dNeWPwjl52sHnNz/0t+m/vr1'
        b'/NHv/zW68o45S65/I3P00Q8G9LO87Di2Ylz4tZE/euOT5Lm1P/7zs5+PvXbWkpcSG1p7vXjdZ3/IHaLYxrsfadzyp/d+/V3OlPTzs18IrZpwx4XGpLmP7z/S2Df8hvvM'
        b'wYZxB3pEHz2S8fapm9K69f86Z8br8/Zcfdf+0t6Ly8eUziva6rc3mW9LXZO5vfjKF8b8cUzJiZFv/3VZxeyGURuX7ww9smTP4dyvD+4V/vzTlW9ctdIz6eyxrQ0rhBUv'
        b'BkOjvs72WWxnijfd+SG36LUZfyxd/HHr4XUfbHzTdeWdn72+vazPt8HV3z/nH/vslD+e2Ty6IHxiwxn/gKfvbeUXH/rTg1NmFqSdmbfzzyO/ff3OXyae++nvZn124G+9'
        b'Tt5sXxB1nvli51bv63UvHPyFtvBd0+79s29p+fjhgL/3K3uu2nbw46JPBk57fNnLMz3v/XH4T16rnXv32R5fB+5+ccCe+bv3PR5d/NonR9f9qjDwwnN//MWXVfNHPVUx'
        b'T/vSc/pnt1//59dvrZq+osfHB0vDxyOLf3uy5KsvGp479b3wWd2muuJxDz25qfX4kjOVSY4JR775/NW3PO82vr9nTO3JMSeXf735t55t2Q/eULzvlrd2/vrd/S1vHDh8'
        b'LJi9M/vVV8707P3BxDLXf2W9ctMzbzTdGP7mwuRtb+5aXHLZN66FdWc37d12fsGJp++465c9P7Bc6PWdty7zzewLP652PPn9/gEDWpcNOvlYQ+ja677+6zQpu9u45w/d'
        b'8+LkE2W+t56fs1doXilPN+VnDfjLZ5GyV7Z9cuz0w0raq28n1H085NXXrm6YN+7B1SXHkv+081zPdxfuWLLho8ufXvfRlrl3n3vi04xPShoqc9+6ptny7pgPSx60Lz5/'
        b'Yd7QvDkvRIa+fzrg/cWihP9KOri+YPCpZ+c8seOrL378s37daz50tCx5rfT9hpkfzJn2/oQ7Ql/Y7hr/01/UlLon9xh271zXu9kff3v7+Cl/XdS0dvX7/yu6odc9v8kL'
        b'rOl1+7u/7un9akir8FH6orpD5YO+/fPOsd///qfRU9/+fJTnN6c+6T8qP5H5t9g6SN1OB6DbgHCcWVIEq3qbheuhrRPVLeXaSfVJbQs52Zk/ogdGq6RjczWi3a9uxYjd'
        b'1LOiejtfRM4I87UN2mY0jlqibh4yow7y1iJ4BHurqJ7U1moPMdMaZz3qXjK7W1FUwA9Xn+as2ilB3XXFYubP6maTekh3RK5FBqoPxXsirxjDfBYfnz+1nexqsrpTF11V'
        b'b1e3kuGmRdOggnTwa5sxqEA7MR9ZqEnqM6KruHvgcizomHrHNVAHUkctGa9tZLlhkJq4lVkaY7IBwdF2STuqbQ3gpqNu0Z7sjuXnwxOrQkl52SBtS35HoYKbyuzcAvVc'
        b'gAyWnF6j7ouT/tiqrutc+qNW28CqeBw6OuIfTJ6atjWpp+raGt2hpFXaHpt62jWThtWpbVXvieMjny1oz0bW7oE64U6g3Sqk6ztBovoEbgXq6UWA6v1T284PXvJH/Rsz'
        b'+//lkp/LEIP/Jy4GB6zeVyW7XGQ3IoNH2Svz9Whvwcxf+k/6vfMypw1l1AUR/1N4wQYYuCWVF1LguftAXpjVkxfSBECszIP6CxmTnZkZJmmiIGTwV/BCfX9eaAIy2IoH'
        b'9v14IVngc+iaxQu9URZMMNHVkgH5Io9YEAW0gWhq/+zgBSt7g/+5vJAl8Gm84KDvTrom9+cdPokUrAURaihBjn2yIWYG77A4KK9s3urEO9TpGoGHWo8U+ALeUaH8PHaa'
        b'F/6f+d/FpY0EwN66ntPNOazuxMEEmaEqHprQtksBJgpbz7QpzkzxspRcz97fKqI/G+blnN++X7Tjp953JzpurT258Fe/a1n1yXPvVL/wzh2Bp77IbLY1Dwqn7ry/bM+X'
        b'8h9mWb4OPT7+5u8O3X9o3dpvzvWZtnHEq6Omjd4RmtJ9x3XLzyWPVo+/2iPtln2NA7/YUF5VvHq52rt04YjffHXH3z0td8zf1bgtRZ2+W3jxXM1VlVc5Z0785pWN9qa8'
        b'8SN/vPjYHbZddb/5PvjoXN8Xt/xm9ug9vxnyo//1wJ2/f2DZzRu++mJnadbZgQXbN1677+41H1595OgDZxv3Hay9Z+VbrdtOv/Oz0ru/nT39b3njT+/q8W6333/93mef'
        b'H+9tTXjvtlM/sRzf9fXPf//ijpcW3b71vRPzu43Z8audT+x5c+Fy971Nka0PXf5cxUOXP//zh0499+VDpz56zjnv5eAbfXxH7/3M9/yn95+Y/0lGqO7a5x/50VMvHN7V'
        b'ci7trd9NGv5h8/GXnpefC40et6Zv9oDqR/rfsKTky2+KLzyzxeZalN340t9ue2HX9LGnxv7+kY9sX214+euRV1V/8Nbp515554Y/jbj2yeHHer0s/23zqYTHHvow+tex'
        b'T8ruD/703IKfXv7n/qPGlnmf7Ltq2KbJHw9+75lWT+nG2tNvv//iNc13//3hN60fZK46umZp/7u/evOG7x9tuq/u+DczWiKHx28b/9e81JFZT/wtac1ftk9aO0j5yb1r'
        b'c1/85STTvDdnTRfLT75abLn2i1df4KZ8svSWYV8+us3mbAz3zfqddPhK7apDd/5G8C/5rf3tJ35cNPm9cb96Y+363bcee2fnM1+8PfyjTZUfb3rx6e/Fea//Iufs5vxx'
        b'ATw+0h7P0u7W5xIgK4PYZNJu1U47Z4vD1CPqboqmPq3t1TboKI/65AJCCdowHpN2hLCZCerpbMMjqPqkukf3Cao+M4CsCo3XHtJ2FKqPDDJzgrZOvWswf/1UbSN5M519'
        b'9dzCsqICNGqlbSPHf5vLtE0Wrs8cdZ3HlIL2DMmUerq6O79TO+rqU0sl7diUUrJIlgs41Z4yiKZtzseIhWauwZM0SlwOOMQ+5ujsQfVh9W5t05AZEOmkeg/UdAb6UTp6'
        b'JSECTTXqoTJt60CBE7xaWNvIjy/U9lMbyiR1byHaaK+UKk2ceaLgVPdojzCLSs+om6cRLjewaJmX58yrhWHqo9pTzLr7w9r92hNl+DlffUI9VgLIh1V9RlBD2kPqrZR1'
        b'E7QcqlQO2JEQ1I5om/gJl2n3ksUkD6Io6lFtI35TTywbys9Vb1UPU7H1gKncpxsEa5wrceaegl3bqa2lhF71tr5kXxHStUAFD/DF2tPatgCRsJsrgtqmysE8ZLlRvb+I'
        b'n77yGhqMtNUzoKwwoHAFM7Rd6v2oyLQVjVoiTpY30jT1ygo2K3Zot9gTAHEtK9LuU5+wD9Q2Ah75gMT1VJ+W1D3TtKeZRag7LltOhtagZ9DEWhlgp9rj2j3py6ThPRdS'
        b'f3vVrWYYjFKsyp3QP3xxQH2Uvqhb1M3qbYVaeIgFvj1gF/kF16Qyz5N35VyvbQKcDrC1m9T1Hn6ieki7h9Bdt3Z6lkW7tYwAJAxWvplLUNcJ2v01KvNOW3r9InVTZWVR'
        b'ZZ8SHMxyE5cyRlSPutUnycbVYDGpjLnWrayg1NXaEeeN4tRcdXsAuT3qo7nQq0PMXPEafg6n3VurbmIz4Okr1Dt1K3g/0rbqDnO9N7Apd4/2yGRtk3qEzL7co27lOWkp'
        b'r55bXUkNnTQjp6wov7RcW5cI82qOkKad0u5jPpjuvUI9s1LdySZ0Cc6cBPVOQXtAuxliYA/3VdcPg5EEVLrUrov3SkBprBe1termuSyTJ2Hx7S4rGVRSRPWDITjhdWob'
        b'xQrt3muoP69ZoG7E79oxdTvUXOLVexZqOxkZsgsW8VrWsNzZ5dDn+SVQgHa7qJ6ZC6NMdsGOq7vKCkvUhwfmDymFaTpRPZik3SuqaxN7MN8F96rntO1lhTNKtINDYbn1'
        b'5NUD6m03MoNgOxbmapsKSKHullz4eDWvPuW8gWapdm+deldhqYlbM5Av47Q7ARBtphapdw5Q96qHYUVtmoGTC22dQs8EBW3v0oHUoqXavTfC53D5TEk9bOakZF7ds2Qw'
        b'Gaot1I5pR8tKB1VUaPsvH8FzFm2HYNYeU5kn91G+AJrbTLwy5tCBbIFuHUpfhyYuw6/qyWTDrhpZ4xytu3G4WfuR+ngZmY82rPRlqTud6n5xSl0PipKpneG0fb4OJloF'
        b'7Yx6ahXBOe3+buo63TbquRVx0cg26vXqrsAw7IIT6olrEaQUwfoogOGBNboDIMhMANJnZkGazWVF6oMSV64etWjrtDMSjWaZdqstAbos0ohJy3A+BbWDqdpeUTs0QjtO'
        b'k3WFr6d2Rx4Bs8Ezygejqd+Dgvb4cG277hasTHt0sLqbjAEj7YUL7ISgnVDv026mGA316rFCbetMGNE9SWWD8otgBLtni9rtMA1vJfo4abW6t6yyqGT49djOSMmg0iFQ'
        b'lJkbxJm0u2rVHRTppoQifXfaUpkPFByAA9h18tSH0vIkcZQ+9Rz9+hTNRqvRlZW0cVigMsdxfdyTwDrzsHouBwYbqrNykPYITjMAxDMtMBAnpEUe7SSNSo22vwrqoz3m'
        b'gbULWaErn24abG8HgO48TCPfFyp/kDoN1vG+HhZOKuLVh8dCnyE4nFngw7oOwX1su7bP2Muwwr36Ser6pMlsQp/THqotKykvKM9Kt3BmSbCWzmC+/4Zqj2WmkkFhbGoR'
        b'9Kl2P9rsvUs994/OzAz7yqP+Ayik/7hL7HyZqLX9+JBgFax8+5+dTxYkk4MsSWcBpi3wVsGpf2HnI4Z0k25UQrDrz8mCGXMT0PlCars8HXTGQvEF1MuRKJadnaYIq8X2'
        b'1gbZzzzCzDNuuC7+bSNzDE2NLlebBUHjSOEVPr59+ECUg+OrjpQDxWgn+JCIWx3HxA78z8F1KSfzdfCLzA/PR1m1yAC4C3AX4C7CPQ3uEtznhed7OLjbw/NRJzHSG+PX'
        b'YUw+xIfmG9J1LRxK1tWLDVIkqcHUwjeYW4QGSwseHVpkW721wdYi0bO93t6Q0GKi54R6R0Nii5meHfXOhqQWCx5LBpIh9x5w7wb37nBPgXs23LvDHb7jwWqkT5ALJ8E9'
        b'KUgmiSIJQbTvzkeSIV4q3FPg3gPuTrinwT0PRcDhbglKkVzZEkmXxUiGnBjJlJ2RXnJSJEtOjlwmd2uxyiktNrl7pGdQlLlwJoqZR/rKqZF8uUdksJwWqZTTI+VyRmSW'
        b'nBmZLveMlMi9IgVyVmSQfFmkUM6ODJR7R4rlnMhwuU9ktJwbGS/3jUyQ+0WulPMiI+X+kcvlAZFx8sDIRDk/coVcEBkrF0ZGyYMiY+SiyFXy4MgIeUhkmDw0UiYPiwyR'
        b'h0dK5RGROfLIyAz58sg0+YrIJHlUpEi+MnK1fFVktjw6UhG2r+ci/eQxkcmBdHjqJo+NzJTHRabI4yNz5QmRoTIfmRq0wJecsBC0Bm012EupIWcoPdQ7VF4jyRPlSTB+'
        b'9qA94iBRlzYTt85QUig1lAYxM0KZoZ6hXqFsSNMnNCA0ODQkNDQ0KTQtVByaESoNlYXmhOaG5sF86CNPjuVnDTvD1nD+eiFiCzGf8yxfB+WcHOoWSgn10HO/DPLODeWF'
        b'+ofyQwWhQaHhoRGhkaHLQ1eERoWuDF0VGh0aExobGhcaH5oQmhiaHJoKJZeEZoYqoczB8pRYmSYo00RlmqE8VhLm3z9UCCmmh0pqEuSpsdiJIZH8ByRCvJRQd702OaF+'
        b'UJMBUJMpUEJFaFZNd3makaYlIewMJlAJ/SltApSSSP2ZAT2UBan7UvqBkL4wVBQaBvUtpnyuDs2uyZSLY6WLUFeRcpJutOM4tjjCeWFHuCDsCDrCJesFFOugN4PozSD2'
        b'5kZHMIGO2Kcz5wRkCqRNjaRreTbcZpnyVphr4pXEAAlC1vGGtLhu4aW1R55/YH6Oh4meVuUsbfLUBzzefEG5GWFQARaEzNYuzWq5arzENEOxtb0mXQXOQYfLymuGBky+'
        b'BOCu1h2oUVDlwupeXU2CNqQEj0fmvpqowxA1IhEjHk2kNAB8hCc7Gu1uaFTcfj+ExHpfLWpJo0Sa8hrkfR6bfJ4kQbBe5/Fg+jz6MjzPGWLXPtkNUJaMVaDIelRs9DVG'
        b'7ZC77K6pQoUIa42LncMy9cw2YxYxyBw111A+0YRqn6tKqSUHoOi+1LV8lc9bvyb2yg6vvCyzqAOe/YEq3TSoFUI19VW1/qgFnigzGz14/QE/fSVBeyphZZXSFkA5XgxR'
        b'Onpw0lvFTwIRXh/lUw8DWLWUJVDc7pVonR0DKO9AAVN1vbtKiZrrq2CAh0XFpZ5aEk9HqznMf0fUjj6k2TMT/3lRH+SAUlXtRpeRLhdEX+piA2mBJxRgiEouxV0Tdbpk'
        b'j79qab3bVV1VvYyJHsPEkJlRN/R00ioMzO/gtA/FCpBcYCa0BOYaCEWs0AAV2o9F8YCpeAQvkE6usF5o4VckBvl4beOOxlX/kUEpnJxfxsQxCSdwGJO2XR1JiNWo40n4'
        b'GrYApHPAwsrEmgR5gEFCDapmJJEtTY4UNsRwDgmGSUEpbG/ilElhR4spKIQTlqMRKUeL2ZtKIU4ZEnYkcC2mMMcEycL2cAp8cULbHenYF+awBcKXrReC5nAPKFHwzgoK'
        b'Sgm8yw6n1aCpnTIU/YJyukM5Cyh2BqTOwty8o+F973A3iucPdwO4YyH1NkeLFWJawqkQU4K9Avp6ParOLA1KsIPwlJ8Z8tseNkMaG+XaC+LgSDihhXZIr6cL2uDJjk/o'
        b'wChom8Oxtod5SH8W0iWFExMM1ToxnEzfEjPQmjDQdTIXTMBvQQEgbWI6x9S9yAaqjXkyiInYsZ78GfS/PdwTyhWwP4KmVFLZi/XA21TXdKMHdFUgY544/o+ONPr8B7CV'
        b'/ynOM85mnL1k8cBp4KoCU94yw7OZVP9SUHqITK86yPBqGuG5ZsB701BKSHQKyUIWYblWMZWXJOt3AOCFdsukm77z0DJ5XdCXiROGOl9fJqnxywS+ijh8YQl2p4x2CweH'
        b'rxDSSPSEU94UlPyBsAkmojmMvzQYdhEl8oIWZVLQQjo71iCUxiYPLJSeYzlvXbhXuG+4P0z/zBoTWoqCqTuwxR5GuTY75JoQtId7wXJcDhMvKYHLxC1ZhGcnPgcdtOAg'
        b'n2ACIIdJ+gQmGT/2LWiH6V7qHRXuF04M95L5cF/47w//vcMDa/hwNywn3BuXVSogl/C+Z5gPJ4eTESnzWGhZm3Aaw0LqFrRCaxJhwsM9CEsj7MzgWpzhFEAF8I0znYNl'
        b'k0goQgKkAuRAeYrSw5OMMsRmlI9qMXlXwltzuAByTQomhTMoDgADqG9SOIdCOXqoH4X66aE8CuXpoWwKZeuhnkZNKdSLQr30UF8K9dVD/SnUXw9lUShLD+VSKFcPXUah'
        b'y/RQHwr10UO9Yz2HoUwKZWKoJgk2hiJE7YPcVgSZCAigreEB4URocXIw+Ta0BCbR1YJXmi3pOFsgD+j9GjRHrrcmnUONQujR7jjLIFeRjEZI2PcIuOl9YVAieVvJMBTQ'
        b'Zmq82/+VtZs/+D8Afvz3w6irEEZtjsEop27WDOUVzbyT3Iml8IIk8Own/d1qtZPd1lSSfRS+kRKZzGOqgFKN0td2B3mEk+zmNMEO8At+fFc/6S+OlGQxBWAbnpFK3ztM'
        b'DjKy3g6+GUpgBN+YjUyAYEA2h606fDOHuTj4JoZNtJ0DwhK2AcIPcI3JgbdDWzrFUv4NjhCoUw+bdeE4HfCLAOSlDo2yGo1CqyBhCZYJ4h4CgGUba8h6EvFUuqNYejgZ'
        b'jYLSeylIMaGJiWEz7tDQFUkAqBIRbGMIBdzD9m0ZPOaaEE7BZYidRUBMNAGQDdtGAQo4tp1ou9c6jPNPixdsByAI4BQAvqg/J0MuJJ6N/o4oP67dHt95p3b/753Rp80x'
        b'AXeYwwJe7ZYs3gyDkMJn0RyzXzzH7PHD0YyoJqCF4SREg2PDIenDkUrD0QPQM9GfRl8wnIZhstafC/POgVrC9M2+LYU6DzXpLRmkeYChTrp+TLuuB4QvbMlEDVlJOR0U'
        b'/RUGCs5jeRIglLg7m5Qm9HGJkBb2NRPsQDDYLZZmEzIjSNHPJnEBbk2DkbOXX8VRigyW3j+PiHNnKBkI89RQeo1F97ZjjSvFipBfuT2ciG+M1GxPBEzDViMsl5QnoC5n'
        b'YjnbkAkCaR6GNPAG3ttiaeJLvzte9U02tPw7VeKJGfuNeYdESgUaDd1O7inQ8AQ6CUIjmL40xF1XxvTpDN6fEFiqfEgmefh/2hhI1Onxu3xLa1yrFBTUVgSLTsNIvKQb'
        b'xaX5l88TCf8vOSXJ/E/aGt4y63q/bCGhmLtDcNDGgM3N+t4uSWSDCB2Coho0c+MioVtQu/TnjFS7xSqk8A5y+oLbCFy/lV6XiiQ+P4PxKG7Essixh+hf41dex3dv4OVN'
        b'vPyCyVSjQSC/8hYpETTXe5Yqb9NjQ1VgmfJLUt6GB3cVOo5Q3iGlGI+s5FGmQL9HxaqlQPkvq/KjinfUolu5ilr8xkNtvW9pVb0/P/Hf04H5C/4DePT/c/lXDjVwTm5B'
        b'1gT6MhQEq9T+QMMpZJgcPPt1PPBgP6mTn6PTt//6z6z/t4Ud5hRRsswUpcvtfI0o1dn5HFFyDBWlLDs/VpSm2NFSiBXJTUDhBGpnBSrdPMGRewhXPA/Q5dJXZENVIyzL'
        b'gKLs5JmaL5kyYGcpr9G6m7a62t2I5p4UlHPAk5Xqqia/2+WKprpc/qZG4h0iow1VWuBtgqstoHzT3i5FnD7s2Aaf3FTvRnUHhvHBPiklo6ndTk94uJusiewu5KKWoyE1'
        b'KKHWduv/BqfqW+k='
    ))))

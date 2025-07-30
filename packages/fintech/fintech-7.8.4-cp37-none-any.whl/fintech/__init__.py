
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
        b'eJzcvXdclEf+OP60LcBSRERA1EVRWcqCoNiV2EJdVFAQC7uwC6zAAltUcFEUZEFAsGONWEFFwd5jZpKcySfJ5ZJcLiHJXXrT5C65ljP3yX1n5tlddgFbvvf9/fGDFw9P'
        b'mfKemXef98x8Rjn8uKK/OPRnqEIXNZVFqeksWs0cZjSshtPQ1UwbnSXIp7KEalbN1VAqkVqgFqL/4nIPo8gorqaqaZrKoHQzOUrjUuiqX0tTWa40VSFVizSu2W5qMbpK'
        b'yL07uXpoXDfRGZRapBZluS5zzaSWUjomEz2nUS75MpcHga7pBRrpgnJjQYlOOl+rM2pyC6SlqtxCVb7GVcZ+I0JgfiPGFw5demh5Lm1tCYv+RNb/hnB0sVB5tBq1pUZc'
        b'SddR1VQlUyE009VUGmVmqimaWk+vxzWjZ5cCGavItXWJEP1NQn+DcUEc6ZY0SiZV9FB/xZ/Ti3D1J9dylJhSlrNxSsnRlBnUV3zev8zqoPpBRAqKwhAxFsrC5rF2qOhH'
        b'QlXjCJWtQGeoOIUpEt2PA9vBxrQIuBu2pMO68CWwDjZELoxPjw+FTbBRButhI0vNXSwEx+fCcyVx2hHlnYwhDGX8KfvePeW3yqK8+8q7X4ZvD1XFq+4rX8vxyS3IK2L+'
        b'7H9+k//kZdSmFSLDVwdljHE0yrEePLfaDRUbhgtNMcEzRRGhcEskQ40EFzh4DrbD68bhKJ00HV4BDaAZNiehdKAJNBtWiygPb3YE6EzXu6AUMraHCZHpMQbyF/zygdf0'
        b'PH1JhUYnzeMHf2aPh8pg0OiN2TkmbZFRq2NwB+AxovwltAetl9iyovK4PJMut0eUna036bKze9yys3OLNCqdqTQ7W8Y61IQvMlrvju/d8AUXEoAL9sAFf+3FCGmGFpKr'
        b'KRi9GV4ETq2HNUnhckVEKKhPdezX8BgB7ABnxhdhIO7NuEu/JqAmf+z1meRnP73+OYqgiyHGyBjFUXES5caclcPuTLaiy8ezyNczUwrpd5jSaYxUOe1yrg+f5Z+BDMVR'
        b'Ur0HpQxfmBPHv2QLhZSE6hrqIVWG3/SaSJki0MtkeJpzA+3hCJw62JwWtYgf/hB5RAisiwxNSKGpcM/ly8TJoBZulNGmUSjPGHBukBtuy0HUqgjXELgFnAPtHBUAbnFg'
        b'H9gGakyBKNno5Tl4ECNxe7uG4lsR5ZbKwO3g8EoTHma42dvbeZhF1OD5eJiTYauMNfmiNGCLalZShCwxRUAJ0xjYALp9wa5pJDvYDG5Lk0hvJoAteQkRDOUGWhnYDg6A'
        b'g6aROMUucMkDNqTCLYkp8vFyWJ8MTnOUN6hmYRXcUYqqIGDcgrvAmaSE8IQIgpcCajU46QG3sApgcTENRSk0/qAO7oFdOI2A4jgaPAdvghbTCFzHQc0KHp9TkuD2BNgk'
        b'S0BVwB0suA4vK1CP4a5AzYRXkqJj0OcyjyS4NRUV4xnETkOw70BJhqEkSbBqHk6RIADHUvgUHvAsOz4AHkApcE0BYC+scotHQ1UKG2BjEm7wzDIfeICFJxZOR43xx42x'
        b'lObBhnAF3JowJDlcLkRdcoGBFxJLCBzZ8PmFYXBrMupxcApuD5dFJAqowSNYuEMVapLiBGkSWPtMUmpEQhiCrT4hPDFSHp8ipMIpAdwLmov4jr89FR7HIITJ4+FpsDtF'
        b'TlNu8AgDr0TCyyYZTtFgzE4iKRJQWxaEJCE63wobEYItiBBSCEOuzuGEsMp7qSkIw3x7oQ9KXJ+avDAkPhluVSSnLibpuqPCpwrmzUmyMzLGkb22Ej5toRFnZC2cRWAR'
        b'WkQWscXF4mpxs0gs7hYPi6fFyzLI4m0ZbPGxDLH4WoZa/Cz+lgDLMEugZbhlhGWkRWoJsoyyjLYEW8ZYxlrGWUIsMkuoJcwSbomwyC2RlijLeEu0JcYywTLREps3ycp9'
        b'qToOcV8acV+KcF+acF/EfweSCZ5W/uDMfasVhDmsgs/Ds3bWUACP9eMO+mCCywthlSshJ0WELALUYVrxVgILwmVwloEHCZ6Ck6AF7IANCM1YitkADsNjdNxsb4IYYMvY'
        b'qWGgIzweITCoARfBPhpWg3p43eSHh6DGGxwOk0XAugTBfHCSEoJTTNh4uJfPup0BNXiAwtFAcwlTwHUa3AJ7QCeh0NF5cE8SIi38zQXuGkWD4xXgOo+MB8F5cALxk3gM'
        b'EBcPr6fT4MIgVCch7XZ4bGGYXMZQDLiMIKOzUKnVBJyxpXAXwlBEkUJwHp6ghEVMCCKhGpJvim9lEtwCEdtANY5ebqZBZyI4bxpCiOhAHkE7GpW5NQDupZOHrOEbeBme'
        b'HJdEsCychltLKWEsMxRuyyP9phsJr4UlIpJKFYAaMSWMYzyABdWGRw10VIIWUmZIBA3OgipKuJYZj2C/RmoEHbAJnEAkHYKaoRO70jPhRoHJB31Znb0atTwRQ9KK2reH'
        b'nk8LCKWD+mJ4jFCHDOwH7ZiMxeB5BlhWV5IiU0CnG2xIQWoIYwY7JtCzwE1wmB/fPaigenAabsEfwYUALZ0OLwSRBrrCq+B2EiZ82Mhlw02UMIBBCBNMYNHBjf6wIR50'
        b'omyVrJmeD+uW8mNwYzY8izikHIO5Be72o5+l0KgTKj8DjsoQK8EF6nPC5AmofxQCamgBFz1KRLqmQgw2JYVh7g+vDk7EQ+wiZMAuD9iRy1hxn+unxiAlxkLb1RimDiku'
        b'lSwiJIYQEksIiVnPPrkawyq03/z2S8YwE71Y9nrGPeWrOV8r6/K/Rv+5txrj9rnEx9DaPKn7i0vD3TI3Tt+9ubFRMjzuX3ktUy971CqFb0iot5OivvHYMN5PJjKOIg2H'
        b'J+BOXjDBplQZbEoATRFzMcX5juFYuMnTKCVUUQCO9hVfHrAeyy94Fpw0jsFohxKdImQbnoL4Xz1KOQ3utCYeCbZxcFswZySyqibbiBOmIgwFW0H3UpzCFbagYUavjxmx'
        b'BFgJLbHWNMlyhAi4QkyJLBsUBDcZ8YC6JIH6sIh4IqjEK7zhRUS6a4dZta+dzxJQeAGAmT8CqZuHZUyoIDV6iFUX6qPtkLdE1+nhilWGQsau7KwX0/yvB+1K6wfZtSmu'
        b'h1UbjD2sQZ+rxwn1mAfKGAcFitF74/vBtpJJ5g32gqudtChCwM1wWwEmC7hVSHHhcPdIRPfwKDuwxiznUY3JY55QX87vi2jcQIh2+n8LWAPGkR+Hv3dPufzOmy8IV7S8'
        b'9N4LLS9fbNk26K5H3sfJLBU3iXvwlR9SeTHYYxATfi4pPGRYMeKBSTSi9NNMeSDYTlAIdoIjq0BDNqztg0UYhXbCLr4zmYFHwmTUFvXqsxsosRet96F69Vm2JGfVQzqf'
        b'1g+x9zvOUoeL8cLFVFEPPPr2fBm4Bg+HEd0IMVw9aPWlwfPgygJ7z9PWvzQbNGbco3kyWsHDYq3OxbkBHrqS7JKcPJMhV2XUlugacWbCNhiiQnggfnYUMUlCYKmJYRGg'
        b'wU2hwHoqUiNYKgxcEMB9cCO89Rgw8h8DhosNBk2LAwSYIuFZd4DUHFw3qhjRkzcSmJuQuoVI7hpoGxjxojHi0Rj1kLHG/Rrko6mBuJygN4GNp46010d4qoWz1/c4rlrQ'
        b'tz7XgZBd3E5zhkT04sWN005Hrvz8W+V95dfKb3MleUpViOrul6Hnlep2Dfrz/lp5VlWQd0bTrirIkeTH0yCrdmqtuDa+dvoJsTSydWPMcKSsu+dckctogvfjQTXcYQAt'
        b'0aAzXoEMDeuYDoItLOiaBU6hoSJ4yvVlRH1oQJCdqyriiUDCE4EvgxiRF2JIFQGGAm2eMVuj15fo5dOLSlBKw0w5yWDjUZxKn2/oERauwf8dSKWftcfosTajD7ATDSaL'
        b'3Q5Ec9/bkWhi0btx6UOQog3rksOQWkesXGT3XEAtrU9VYMF/Ge4ADaJFU5BeNgvhcbcLvLIe7NIu+uMXAgNG/0PNqwrzC/KL8hW5ClWyatUn7ZqvladUXyNz2xVxmYxy'
        b'ltKcE3Y2X7bh9hN1mJtDpzjyjiFeQv2wXt7BG7eP6BBH8xfn2+nQF9879QVmlsjYakrr0xsMNQxeXwGuc6AdtK4dmJb6OWKekoUz/bCaU6RrI577mjFg1XvQ/8IkFVYV'
        b'4lXc9kaZNHaw59xW9fdKMeHi+X8Qru/ukFmFc5toLRG8U9cqwiMUPJceBC6ySFLfAheM2JIGe+C+qbx8rcpD5nNIYoQcbE1FzW4OSwCdIby8zswW58FzUiMBQAw38uLc'
        b'Oc26kQFwF4dYzVFgIRrJ2nJ4jZQsS0xWpCTOhu3ISkJVo7TBowXDwbaRjljgMN7uJl1ugUqr06izNWtzHQllpJDmf/WBvePew6JUDuNO20Z7uH20cepDDqP9uaTvaE+R'
        b'wz3IeEQqcTwi68akFDTksjJE6UJqTIUgFW6S2QfJNtpDHTgZMeaemHM6cTKOGkhsixVFuM17x7uI1fMpqSb7P+b9hveXr8yPTTKF0xSvkl8YxYVhD1hEAqLLSxSydo/Q'
        b'4BKsgRuJZ2aax4+eOw2jhzELPqZ/yZySO5j3qGz3pbCfZW1Xdon7515z+Jed2d4UHt0oeZzpd1ofSpub58EZytGbW9dqk1RqVbumXXOm4Gtlqaqus13zLaLqb5W6vNBF'
        b'p1VZd1rAxZZBoS+LfRraxR0q5tSODo33p2dVZ1S+om+5tySjlFM3v0/HD923Ocbnx8VfvxM15BL1ReuizEC/rg721a6emHeih8zf+I4l5p0oYUxpHlIHxwX99qVuxHZx'
        b'K+FBeAIcSEJjE4SQlbgYxKCFKZkBjw7MOR7LT7gClaGAoJWUR6txYsR/bb9EMUSIISF3SD0Z4cBi/J1ZzMD103wygnk48wkHzPvQic9g3XfxBngYWTlIQ0R4MKRwMbJE'
        b'QeuSR7hU6T4uVebJXaq40S79cE2iMGE9NgOZ17vgDjY3i6IiqchpeoIYrdnY7UstSJurLHoxLYDHlgtDMAZRpVcEyuQ3Sr0pPebIA1166Gxt6qRuylCPHkL3CiNeG+8B'
        b'orzm/m7vpYMvytpfEUx2HRpPD3/dtW3uEbGu5cCWlz/1+UdK2dyLL4Wt/tufLMH1g4Vnrn5cflEs0e+5lq14cfWWQRlzk/M06suJu0atEga/ljel5D9ZpdcWnj47/Y34'
        b'S+8Xr7nx+ov7T9/YcHxx9k8P3l21p1IdNOhB3d0Xm1XfNf2leWTGR6MVE2tkbsS0gC0ZyAx0tpis9hK4CE+wYG8eYWRz4YU1hnCZDG5JDo1IMEWArnxeGIQuE4Dn4WVw'
        b'2ogZDLw9LBheUIBOIy8rQC08QLnDKnZCoIQ4iFcwZX0sL5epvNZcC7Yaidl+AbYr4fmRYXJYB+sRnQvBViYCEfRWYwiuoQN0BDvbZY5GWSMyirchw62J0I0Ablq7CNwO'
        b'S8TukWRkA7uBbgYeBA1wI4FmFhLrG5GBHB4qk8NmpKJSlJ+UGwKOrzTB88RwWyiA51PhaZ7Zo+p4Pk+su8vZI4zEV3LCE3QhQ6HXTEiD7eVJYKcRa60ZUyXUkjBFRALq'
        b'PIaSiFkx3ObjpNM/wmgTlppyirQ8+w/m6XQqg0w2byIAfGgOXXkzzhXduSJ6ldB6qQOtDnGm1QHUgV57Aue75kCmrzhZcnh0QRM8BmrDQlLgljBwDpmyQkoMuxhQBZ/z'
        b'ITXmCq1Ehk1EsY3I5CzW6M20P1UprBOZhXVUNVMpMosMinIPM3uYMgvb6EpxBqXz4SgjXeiqn0xT+HcppfPNRDqwWYxzmoW4jOmUmsZ5W2g9ZxaUZmmpSsHaI2bBYaaN'
        b'mkut2L2cqXSpdMW1mF2qGX0eqY9Dd2fNwsNsGypnbR6640hqn0q3OhaldDMzeazZdStNU2U7ERxzSS4JglJS52IWVtMoV3Cda50Y31fTJKeY5BQ75HwjgzJL9D/WSfgc'
        b'NngXUGV5GVQLowsmpbpVMwj28Dq6jioU4jsEjUDNtNF86hZa92+SjjYK8xiSdkmdmzXtkjoGl21P+RZJKSSpzHUCayp055TqjJo9LFJzakENMhfnUtU06m13tfCwyOx+'
        b'WKwWqcVtDH5jdkd5u9QuZndfqtLdIrK4IQ2OVbuifGIzi/NVeqAe8Kim1eJCXOMfzR5qNzQyHrpR9vccev9vtQTXaPZoo33xV07tXulhZloY/XwEL03gZfTBag8zyjEU'
        b'ces8BqXz1EnNtJkpZNG36WpPfG99L1Z7mfm7UQ75lepBfH57Glybp9lT7T0J/3dHabaaPcjVUz3Y7GF2x+XhbzoPsyf+UtpqdsfPRn6MvVArvFArfFArGP0DsxdunXoI'
        b'6lNG/yr/hPJ8ju7E9vef8k/4PWrlILUveqbUQzcz/pR5EIHfC9XuV+eOa1jlavaywWBmW1i91EibPavpTbRObHTj76zyyl+R/kBUhMxrXcT4B0y41C4KGas4JKYy9gDk'
        b'I9Ja4VpJm+lV1DamjMPqtFWn7BFnZ+tUxZrsbBnTw8ijemhjHxv6gev0Iq3BmFtSXDrzJ8pqRAupisDcAk1uITKueu2v3oQPWGmJ/gEd/g1NSijJkxrLSzXSMQYnIAU2'
        b'6pfagPTFE7JmLKsZA1eHAK6mnQC2+UyCicxc/Qi+qB+LLv/uhfcbXOkDT5V0tarIpJEiiELGGGRE+D7wM2jKTBpdrkaqNWqKpWO0+PO4MYZxDwaRF/jW/ooj18EOKW25'
        b'H7hIi00GozRHI33gqdEaCzR61GLUEej6jRcB/AE97gE96oHLGMMyuVy+Ar3H2uuDQeHS/BKjrY+moj+ZpEeg1ak1a3tcl2CA52GjDr1CtRp6uNyS0vIerlBTjgxcVHOJ'
        b'WtPjklNu1Kj0ehX6sKpEq+sR6g2lRVpjD6fXlOr1WI73uKSjCkhJMu8el9wSnRFbD/oeFpXUw2E06BGS7jH0CDAshh6xwZTD3wnIB/xCa1TlFGl6aG0Piz71CA18Arqw'
        b'R6w1ZBtNpegjZzQY9T3canxliw35KDsGo0dQZioxamTuA2qeT3NBUinBLgLFNlR8nbLGK1AMFnccjQWhBy1ksfjjBaG3VXn1oH0ZV/KMRSQRj4wvegpAqqwv7SX0IQJU'
        b'jO6x99OD9mJwfgnJ78FgMerB4FzoDeNByvOjA1FZvljIMsTugLdDQBWylOBZUXwK3KoITxRRHtnsFLhDbnehiyk+rICQwbfogoQVs/aPZuowRcTPW0hYsZWcmTUElnkY'
        b'keqK/7RIwB1gKwVmgZkxs9MRwegXIRFIFwrRfyQo/KnDDGKOrD/VhoQOEkIcYvwcFhWGPDOXT1dyazPNHCp9ARK2LBYkSPgdQoSHRYJAjUsUqDlUCouf0H8kCnFJZUW8'
        b'cNGfUnOlZ9RYQAvMIlKbkP+eQSHBQiAgJTHT+WfO+sxNp8o8kAhkiHEnUCD6jcejSIYSO6P4x0TbO5lAPx0PMGvQGHtYlVrdIzSVqlVGjR7PB8jEPSKMe8Wq0h6xWpOn'
        b'MhUZEcriV2ptrlH/rK3AHrFmbakm16hR65Pwu/k4s/AxWObgy8TxBepsW7kjEAszjCVIxiF0wEjmxSMCRjWCXhLaj/FCz14IIUxkpuAq2F1qm82ujwQd4eXhCCfIvFoY'
        b'uCKAu9fD407mB64ZIxGpqd80KIUnQvPcbLaNmbZZMI7mkF25UqNLHR5luh6J91VUqRfCMpRJPwHhhTt6Q2OhWU27ITuHiCWED0jY0XVsnRu+r8fRKRwCAlftikCR5Int'
        b'zkgXM4Pxp68JhZEa9yPxY97HAHBmrB9Q5e1rV6JqWfxE9CRFJYOKYDFg1XQhpY/Fd2YERiWr8yHACRFix+M79IZZgLQ98savDusviADy0DNGdqJh+WVQa2ebcblTK1kz'
        b'KRWl3VInREjKIh2G00nwPXpPnsycvhTLGUQ+qBwzR8oozcCBS3KkaXJGQR6DtM0/0kiHpKkKCeooAZbBGair1OjdeoEtUAmRBuq4rbTVK43wCyv+PaLVKj3xRLL5CIcR'
        b'F9UXrtFPw7g1l8fCXudjCr4QpF1JkF6j18vET8wVe/FVkk34YSmquNjwjB1bEY4yDMZRCWaADIOe/RiCrYwEYbEfwtUAuiJKlZurKTUaeqW6WpNbolcZnR2tvRUgabwc'
        b'V43bYXMukhcY62Ruv5a/sz0i3G2IbPkiV9ib52IHaDJtm1FieXY/ArHeAP+KgIe3waZALMPF5eF7118lfJbZwRFZK5tIW30FFCsdTTwWKsHKpGSFIiJEJqTc5MzgJHgM'
        b'3vBzcmKKrf8NS9BFQ2Uh3S6LIbQutHkustidYt6XgcjPJU9Awu3E1XQWZ3+P+YII8QM+BA9/E1gojsoSEjYr6hlkDZebry3SJJeo1Br9wFO4xEnHoOIQw3GYbmD/bydx'
        b'OYUJe2Smey4ygM6QUlgVnyJPSFmIbffU5ISIRbAuNS0ERy/wgSGbYLvL0jBYo2U3Xednft8pG3xPeV/5rbIgL3R3CAlFu8uHouXcV76Rk3Xnw8yZL+x86WLLtm10e+2U'
        b'Q2M2B5F5iZhzbvnnOmUCfj7uZDSq8QJsjMCxT2VWR3WACVyYzIHauXJiy4Prs5Yi07+5qP+cnR/s4pMcBifBFdAwGJn8TpO1LBvEJJF5waAssC0sIh62wl38XC2Zqc3M'
        b'Mc5GH5UlNGhYY4+fIeE+CfAS3xdgC644Em5Jhs2wMQk+PxQ2gnrYjHgzhdLsdYdtLgutUxyPYQNIs9fqtMbsbEfP8AaqAOsvHnRFQD+kkNsy2KdQDJqivB5hEfn66CmU'
        b'Qny/yla3Xosu+ZggsJFPVaHf/Y4OvUdVPjBqxvKoySJMx9JQmCe0oyf3dLNh/dFTpCAhEcXr4ElrWNPCGWhgYAtLeYBTrBc8DLpM41GK9UN0eM6SxE/2xj8hpCJeMdAJ'
        b'zyaAS4soanmICO4E7aCJoD28BY/hqUaUEWwevjAkBOFdfATcAjrSQxJTYHO4PCEiMYWmdJ4uM+BzYJ+JuLA2Il2hNi1iSTxslCWm4BmBZpTBSjIo9QSwWxi8WKLdM6eS'
        b'NmBL70DSsXvKV3LaNe2qzDut4GpLd+aJGtnmjtpnDrTt7a7vru7IZO/mC7sL/aZmXnh/S1GVeXeAcHyX2cUgmiMyxLzN7PbYvbnxBcmBCOqHLwdn+gr/LUGEQybnN4Nd'
        b'CbAhiUTPcSPotdHgCOyCZ4j7TBEbbXWOzQN7e/1jK+HtTCMO/3JBTe+2Ut3yGEe6Q0QHtsFqI54fmCIHG8PkEfERDCWcCk6DY0wU3ANPkhJAQw7cnyRPTAlPAE12F6SA'
        b'GvOsYF1YFryRaZvJeHKNzj1Xr0FaZHZxidpUpCH04WOjjzLiJGN4m0BCV4zsj6pOuW3EiJEfUQwWWL2UIni4DGF4cim200wRuuicaGanryPNPA4QJ8Kxe6+n2wjHpjxi'
        b'8hHnuTwh+dT0nYKx2+x28vFQEMdf+Fq4y0o+0LLGkX7WJRDqAbfKQLeVfuA5zUAk5EA+4+FZEsI6AXRQfCZCOHAr8zDaGQ73PzxaQN0nWqCHzusbKyCeXqQqzlGrZm5G'
        b'OfWY85gy0MUMr8cYMKiwGjw3AMeG25NAZ3wK2GpHTbjLaS6YjfY2gB2LvGEnDj6qHQSqwC3YSWIjwXXE22utrvVG2ACOwfZwqzRZxI6PMtkbJKAcwgIIM+Q1cgaPqp0Z'
        b'skRWc2g0WTKaHBlNdj030Gjiou0mgiMznIwh65gALiXhmT45P4GfFh+Gw/IWI9kZIYNbkxMW2wdNgESicKHGFd5ONpNpjz/5cZR48nqWilOGf14RSJlwwA6sGi7EBYLO'
        b'VfYy+XBkJP6tURhoJIs3uPhtANcJ50xYBFuTkvA8I9IWQmB9Bs/+FtprXoyQhfRhtwieW7lYq/nuA9qARdHMqe2njd+QYLFX8uTeMlWyqogoC+H6b5Wv57ya80ZOgmq7'
        b'+m5Op+bruE9/H0UtnkYvjqlOt8R8LuuK2tmlMQw5HhVdJV1Qe7x6+b/nHaCDh73S8hsf+p2PXnjzhQ9/4/fanb1C6veT/U4d/adMRLhUvCdotM+RgKtZTtMkLGjhyBRJ'
        b'NGw291dB4HZwnLDDg+AYKcxfmuHM8MApcNrG9LLAxWKiiMyBJ0qtM8yp1rrcwR4DPM/6eYJbvM5zAlYBPFuLpEetOz8VLUfqqPd6FnXrHiWZnBijH09S4HJmw/2oFrdJ'
        b'DGyakUqKyAPdQqS2xXvCpn7RHPAa7H567uuBwzSyS/UlRmKTE/YbYGO/GyhvhjhoONoLWSsSMpNRMbE/79Os1eRaOV+vnu9cMk/rAt6A6LWzHjcvaZ2+dLdnIOy5FF2a'
        b'aZukqCK/f3Vk0CZs9eB55ucND1HuHs4qvFfaA0dYsH0K7BbMg9fiwKUxoENGjYK7fFYNhqeKMHRTRP5clfTPYyjqk3E/MpfH14cX0WQW++PRrXSXiJLemaaJ/jC6QjGC'
        b'Iq9XZ/zoudOTDpGGfUH/4lckXkNpVTtLOMMRTCWrh41pvOUOorw2//l9RdG4nfETJHf87t+h2ib7v2IM1nz4cfzMgLz42JcG/f7nt//54vwHLW+6vlz7w3TZktnjXl07'
        b'p+eHRRf+OGOYztd72teviF/UXIrNmXR49ZoI+WXThQ1Nur/cLPznxXN3jEePJKW1X1W+d37ZclHJqfT7g0M/+O2E0XGNPzVGbt/n8VZe1yzvNeMSr3+f2LPUsOH44fPM'
        b'd82//MA2B4Wd8Py9zJ1EaORG2rgk5gaXQY2DWp4JLxj5iNZkcDRMBM/3napbCc/oCSbL4SYvnviuIpZR10cXUY4mgR4VoAMxYEJVtkEEB8BlUIfGDA0iz5xj1cIViFdX'
        b'k9m7OWBfuk13Acfy5zJRBniJkHFlBryJRxxsd3ccdAE1bCKHjIztAcZ5uHHgHLz4UIugBJzrZxT0tQjGwDbCXfxw+DAquCmS8CG7QSGihsCNLLyYqeJ7ahOwpJPpUXl8'
        b'ELiSwseaeCxmQ0AXzc+v1kxHCl4DXwIOYO5cAY4za5eCNn4Gt3E63G0LVZWNcbB/EnNIw6eBw+EOUm0zvOog1UArfI5Es4Kro+E+VEtTRTJN0ZMpxJ2awPaHEKXL01ro'
        b'Qju/cXNgFYTZhNiYzXq7rsfgwDIOe43RHcd4ewrR1YvxoiuGP5L1OGl/Quu7XgYjehJYGb2ecrKeytBlnZMmaAl01AQfDRKqlHj7XbOtL7KzeyTZ2WUmVRE/00OsM6Ju'
        b'kpp63PFiKJXBkKtBzNNq/P0qr0iPi7UkVAppSAG6aGirCiZmvER+7qZQjEDtYJfCyiVLFf34JENNBbeEYC+4yTh5FmwzxwZchs1bomHVvCJEkZhMRs3WuGDvCPGACIjW'
        b'J7B7QBaojKjXdKjHFLmcQ6l2OxPrPlZV2ep1zRNZlSuuToSUKwFSrjiiXAmIcsVhD6CaD4nto1z1V5UFvKU5A2zxzsSxOjaK7zU1j8TLGBJoBfbGwq6kMrFDGjyVUM9R'
        b'AXO5eNgBdhENkkNW54Uk0IZjY+wJw0LjhVSAgVsMqldqD/mu4gzYmX5/yIJ7yqV3WrBpePdUTXd1d/W1vVo6TZQkKhR9MPvLrNqA7zJqR13w2O1zomi11P1zzfhJMe9G'
        b'vRjzhygu5hg1Pn8qNfk9r4Wf/UXGEfVjItwEzvUNjIBn4UXEcU9sIJajO+I+Db28kXEHTVHwNNzBc5GOwdNIFySB+hnj+JVI3hoWnAHXS4hpaUa5T2IuBGvARhsnQmwI'
        b'XouyKR1PQl+O4cB5aOyzsY1G+IC3jQ9soMJdJT40x4oZZPEN64cscns+njqEPWxukaFHnGcqIjTVw5WitD1Co0qfrzE+VsHg9DhgTF+BL+vwxWwn/bXo0tFHy3jfz5H4'
        b'HwWdjFFgxzMmf70BX4yE/xGaLNYYC0rUpAK9ydYtA0V7rLYDswZdTtrcmthjTGK3J4AToNFKvOCUG8I4sfOytWlSIRq37kl8FF0KCYHKXC1Qhh94dhTlNMnhTHZO0xx2'
        b'sqNIkODDV2PlDzTr4Ex2/vxaWE+wZbhQYEAqwEW3MhPEMv0K7DauhpfcVoMmz1IJ7Ea0CU8IYBd4Hjxvwp5H0DIIHkM56pMVsClMsZgYrQmLFRPiEauKsC2nRURYFy4H'
        b'3YuI//IiuO4Kn0eibdMjF/yyJHbiySIh8/o6WQfkLVJ0PwLcBLfCQHuynR9Q8FQINTidRYL4eVhLuAayQfFKqvpkP7CftAvuCgMdITQVALZxenCN0y7PFAgMeEKi9XrH'
        b'PeWrX32rzLrT1dK2o6O6425H9fiGMrrlUsugu6LuvdNaF/mltfpGV38+ze/8+w33p/r5dlWlR0UbowQxx6L+8hEXU3qCpt7K8m4Z8qXVoRQILoUjM4QsdBIi/eo2OMPE'
        b'gKMCXiu4BTbClrSCsHjCUrhJNDirXEMUF7hnGmwlzgC4JZCK4BN4go3sKnAwgSgug2YibtEF8Xo2vIaskaW4KTToHg7P8XpNFTyP+Gh4SDy4Gde7YgMcGPHYtTFuqtJS'
        b'DSIzTOjODqMN1EI8fyIhs4CudEUoYgHZRdpcjc6gyc7TlxRn52kdbRSHgmy1EibwyBCsdXaiXI8uv+3DIS44hWGlovcucXlJqRFYT7ShLmhKDUNW4GHcMeieF7i7+kSt'
        b'W0PUQH0k37lqcMireCWSNdgiCgxdF4bKuwi2wMaYWIYSwEM0uDgF7iQLKuIWeyA66V6zGl4sk4hLyyRlHIU0v6O+09h8eHIBmQZNBwfhdgO8CLtd3Fe7u3qI4XlwZsQa'
        b'TJFlAirYm6uEpxfyMbub4HFwNikB7JwdHsqPpBh0MaCWTTdNRd8rloGryCTegSi4vmRQcmhiODgFd64JD8EugmTbSpI0sXWlM02BY+CC2xxY5WeaQmHTuVPIZ354VrA3'
        b'rjf37iJXuBnUs4QDRoNj0aChtAw0r4GX4RXEUYyoZ1sWoPK64BUTakkah5B4Szwhtg1IJp4hsO7BEhyZMA3JIsoTbmNHgo5F4Kw/6Zqo5Yn9ilxStAZ2S1yFVHAChzr9'
        b'YBlRak1YbMEWcCEbXECYmDN1GjUNbk0m3ZY63B/uSI1I8AD7kIZ+Lj5BRElmMPBQFqgnPrg1s8DzbhF40V9SBt9cB66GGEQDuER42Aq4UQRuDoadJOI1Ugpb01DVInA5'
        b'mAoWw8OEszNeLpSXz2cMpVQmn1vuxUe8Li0RUhLxLJqSKovmZkxGyi15Pc+IKFHcjO6UyTGBw/m076oRdEpkiKK0rYMmUaYY9DIY7AJnsJUWhk29euLs4cGEnbQNUiuU'
        b'JaBKXFm0TqsIymbJROflrftSWm4kss/4bf7trHUJsZP+TK9L+oEOXuyV9MOiM00fNW/kfM/HLnttU/DGxl3vLolp2uyZ80nMT+EvbIjd37LqjU/MhtaY0TdfeDE3M0ef'
        b'Pnv0877nig5/Unl8zrls4diLg8Kabk+e/W50V/fZvy2K6G58jvWYvHxCUnRTWfXR+lfz9337j/d+t/xuZ8mZyt0ZRWnvnQtNu/zKK7VfLHnpw6KSS2uypr+/9OdPz7xx'
        b'40PDq2NvfvW1a+rw9+cEHGr95fjtkj/dG5S4+GaAeOF9+WsZ57teEu3fPPbHNX9apznMfrA6BPo0Tvvws0EvHfco/s2/tjZEv7Xtu0T5V6Iv5pTNmGkM3jerYOo7ib/I'
        b'fmx6X/DH41dfMu4CXNbr9c1jE6+mdv70k09s2V9WVRUt+Grcjswf//Sp+X+Skn75bJq/6as1W87k1v38yxeGfduWeMb7/sf7QcX8qo9knoTR5g6De8FZcCMJd3tDOGYZ'
        b'LOUGz7PMdNBsxHInBg3OEcRhaGR03mZW089MG0O49xpwkSOcG1TPtzLv0aCDMF/YysFLE6RJyaFynrm4FTFIth4FV4kXaiQ4kYbqik5XkCHGk2YNTOUCcJifdGvG8mo2'
        b'QotUDA5WNUQIotsMvBIEr5Gqy1b7JoXPhrcdgmzLh0mIqhmCaNcSBusSwhH/25FABIiA8pzO5i2fThrsJ4CXkaWOsjYmySIUSIkZmgwuwnNcHLgm4Z1kHt5hclgLzjpF'
        b'HB8GnWT+AtQIEfFjqGCD9xoRxUXQoFO7kPgHYGfR4rDElOSFg2mKC6LBQdAI9vOLTA+ByzHWGGbMhlF2hNVDweVB6UjFbyvjZ192CuD1MDk4D29ZJSaWluNWEBUZ2Uib'
        b'uL46uFrHraTSHueQezLb1NGOHjKgYCPCcFGvMHwWi0KOhBl7Ma6Mlyv6Y7xpfHVlvdC7ALxkANncJIYKXXFIgpgE0nghCeZBQhS8aG9Gwug32GQwspGfzqh2CATEhbzU'
        b'R2DeclSp+dmJs0jnqxlAZmLkXzDJJjEF1EqjGOwqhNdkLFm1rciCVb1zY6AGHqbBkYhwsqfDaNiGVREF6EzmF2S4gUvMCHgGibb9SBPDyDFrVmEYwrdQITwCLqGhPczE'
        b'zPTJZR20PF+bpodDBPrthUDZd0OgnfZDYCxD8nztswKCh84KsGRWgPskGA2jq9ThZ5EmX2swavQGqbFA03e/HbmrU9oEo1RrkOo1ZSatXqOWGkuk2A+LMqK3eN8VvAJU'
        b'WoLjK3M0eSV6jVSlK5caTDm8e8KpqFyVDsdPaotLS/RGjVouzdAis8VklJLATa1aasU/ApWtbPTBWI5AcCpJrzEY9VrsBu4D7VQStyLFdttUKd5TCN/hOE5cpLV41MIB'
        b'shRqynGsJZ/L+tAno1q6GvUZgmnAAkwG9JHPbk8/b3bCnDTyRapVG6Qh6RptkU5TUKzRRyTMNcicy7H2ti3MVCXFbdTl4xhTlRRH32JwbGXJpYoS1HGlpaguHLLZryRt'
        b'HsnFdygaqxwVBgiNFRobQ65eW2rs1xAnB4dHPyPETUHWRyKDfWtGWuHgSNsc3aKMeKRipsUnChZNmQI6ZK7wWvkUsCtu1JQhSJWB7RL/OaDVCe29bGUnOqM9ZUV82o74'
        b'jMUzz+vXTIBhFtF/644IBUpD2IdiYPPNHopgdRPZZ9+eatcmXHT/5WwCvmbCdLVTj37DGLAZH9tw7Z4y4st4lSTva+U3yuK8+8oEFbftG8nrjdrk94vmZQ1vlP6geHf6'
        b'ZY93jdIVqrdfeOcFyrswz6iq+32H4N4ZVYuaupe3Ku+1L8O3MPvFvivudHm9dl4VctFNdN43Sq5Wqr9WCvd6vXZn71+RCfjv8JF090YZQ6QesCBOdTgMqcEn4Vbei7OP'
        b'iRDArUQ0RcArYG8Y3Eo05AZYx5loWO8Fbj39lJAge41eVUpEyYheUbKBGsORyDRXxKf5QF0fvPpXprcyJ4eINCsaO7zBJdoMLBL22StBHicaaT4DER8b0WUUgszg2ys+'
        b'qqiPnWZ+ZqAvS2cg5SQR1rtZUX6AFcG9gmWetywyEcny+aDdU6sGOx4Rj8USv8iTL/92chUIqIFcBSKFCU88BBaBQzFRE6Jjx0+MAVdAlxEZKl1G/eoyk4FYMheRsXwZ'
        b'dsNL8IKnWOLq4eLuhsycOtDIIGsKXnGBnUjqEU3+3rBEamfUPxDVKlf5C8fz6r0+IJ5qoRKxfbBq0uxYK1JblJdZQw66u5EbNOQ3bd5xC7wEb677Z/HvXv84I/iZNwWb'
        b'/5HXui0e6Bb9Mf8vJw8Zv5w7dcnkc0Gbg+uv/C2zZ+ny6cGJDa1zr40Ztj7s6r6Xu+69rzn+y29FwreFkfVHD3j9ve2HL+pyfqaCjwzZ9HOYFYeRenUr1mntFby9oVwC'
        b'2niXQAPcBtpggyvSMB1dBuMMjwreeHzslb7EmJ2DrWTU8X6OKB3DETT2IfEl3nRF+BMhs7U423SDPYz50VFZJEUvKm9Cl6h+qPyW01LLOPRlSODIsMQnRGO4JRLUp0bH'
        b'stRqDuwHDV5yroAMf50fi7HZa5lYGQ7j11MmjIPC4aAb7hDAg0iZkVNypPScIIm1mcgURImvBivDxyARQl42jhHgAAXp9XnK8BfNG3gE4ndACxdjAVGaolGG/ysulH/J'
        b'eCfipeqlLiOVrp2DnuFf3prpRUlRGaGrlck/baigiCPDXV2RBpvgzsUTo+AWbnA8JVxEgzNI7SZZ1oQPoyag/4W+SnND8Qa+nLvLu+ibtAiR5sdrWvVCE9k7IwfsALvT'
        b'AC4JNglCQihWSc+EJ12JiwHU07CFONmsNjYyL2BdeCJ2GmJTg0QxwOYwrLOD+jBk9O5xlcEdsJZM27rGi6jAzK+FVBwleT/TU/whRdY5r/QfJxYvpaJOjLlWtnvY5JD8'
        b'YWXzgrKvc8RM91wzG16gC/AC2RQqBbSZCORFmdMoI0VN/ou/Uu81voxvzpn0mZR4mhtNLajSZ1Ys53cuHF84kzIjA+KbmUq9YGY6n/KdtAg6OPhFjpJWGd6bX5PI9//K'
        b'd+l3PEtElNfGkveeveVPXqpmzqdflIQidrOx0C+vWUdevljiQ0uTlQgRqir9ZJ0zyUuzzki9OPMLJAKrVrea/xBAXn4yfTHdzlDiWi+V249DVvG1P5jeQn9dulBIKavy'
        b'M0N1FeSlclwmlT7NQCOQKt5bWp1FXraNG03/O/A5jiqtqsxc/H40eemdPpJ6L7SBQs00typeUpOX349Npu+viBOg7IXvqdRzyMsxfr50OKq9OEhZuV9TzNc+u/xN+jBL'
        b'iX3VqhLvGQb+5auzX6TqaCr++nylLCytkH95Sl9J/URRcZdXKpd8NN26JZ+l4EPqKmpkwUKlf/zoZ/mXMZQ7hXBHGbZcWSRIGmft5MQyavoKFqkZH+e8s+ZiqXZmXLHA'
        b'cBzlzUmKXrzwxtZ34rzul/f88dbf5aK1P/w4deVvRo+SBgdL//Qx9cyS8y3hnS8+YBT76iU/Ltfr59bd/88nhp+oiptil6Xffyv/Q/qa5jnvntn0yaSSJV7Lvm2/sOKt'
        b'128c1S1cGt9e0tF85vvduzbVfpL1t08/tRxtufRptJt/UcIe/z9M+cOUo6oJL8xdLw3+LN2d+SbkZuP78SvHv7qNm1K2QP/aidbdF08smf+PiarYLr3+TcXVu2888yfN'
        b'K66Bl7b/76jfBoT/8tmutPhJPrnPbP+5fHhmxr2VE8LebdiX48sVRXj6/4Z59/RHz35u1l0LOvPu71RLvc5PXHxeOfI3Hj9XtlSP0EZdfXma/8kD9fKfPYOGh2999oV1'
        b'e5//aPXbGVtOHlnXKnj97R8br24d1vljbMiHczdO1LW9KLxSJlpT5vnPsk2itXXP3nw/d9wPNSUPdp6Uasq/nXBosebuhlfDfkw4cPJfgkP3G1ef3PfGjoqXb6132+K5'
        b'LjLrk8Evf9X4jxnffT7twXUXw82Cl4Y92PnzhJA9c1Min3/Tf8q97Vl/P18+RfO3yLdvffg8U+zp+srvl/0y0py2q2fR5xd+u4FS3GzeOWSfTExESQncBI/ZliSDq0Ot'
        b'PoIj4DxvyF9Bdh/2QkQiXlUEm0EbvQDJnjoipHzk88MSI5IiQhUClK6dkggZeAvv98arYV1wa+ZU3z5e7VJwmDgY0haARsRGUhPAGY5ZirdTG5UwjPg9wMlCSZhcAw7L'
        b'EsOsux96wiq2BN6CV4j/IAKc9XDwqBRGWX0qPrCdTOQjEX8NHAUdEYaBNnMBmxc/7by819PPKz+xEim2yU0idJc7Ct0gCc0xvh5erhztuKkV/j8C/fdDv950MJKBgbSQ'
        b'fHHF2ibrTfsSUS0kOxyIyWIyD5QDOy8qAh4uuG2BR3gxR4/Iain2CIj55yCx/wvL4Fh9Db4nq0Y22wV9NboM7yfovwh1FPR4p8VZsWYi6GcnP1bUC7AtgHS+m3DLMBPe'
        b'IBZchPUyMsmEJ3Ev25y1vc6OSHBRAM8gHXIzmR9YBQ+GwgtI5B22e1dwsKcX3MyOCILneH4tYSiuSIWkrLKIXR7DM8eLy5AaYP5JRMUpJR3sTP7ltuFIYQh8haGkyuTf'
        b'BU2ktMfKfiMwPIe+XNovH944wwNESeZ/N7b47YtfTBKXjYtdcky+xPPNaIbtUH/lWypQ1L3yl+Cf//rXceu/1cX5/bD5/Ceb3Jedvfpl7bLv175U+McfDnnmpgr2vjTP'
        b'XPW3vy494L0zGvz+2MxrPt9XDBoXtO/z56TrRwjufvnl903pry6Zvnhc3doazyM9b2cc2J72QtubGwIbV3+sPP77m798cH3X1EqXG/fTuaEFu0d+PzKy4gWkfBPX3wY2'
        b'1WGv3N6NcuXwHAfPrcvnPaaNcNdwq1dRhPgHOE38ivDUMrIvw0JoAQ22MZKAvbzHCjYn43m8Q1xJEOIt2LlZDjeFg4YkuL13NBEj8A5lQfs6inhX4eVIUINLQqOH/jVY'
        b'R9ADnGXnyiYTFuQL9+NFD5ERijHyCLglWSakPAPZ7CQlvxNeFziyDjSkEh0HVC8MT7Tv5TUMbOPAUbgLttvMQt//Og94Yg5hI1nnMCD8G4iDgEKelRDHJYOXhDK+DL9n'
        b'AuYI+lqUVuFI1zzhEZrrpejB/4/b8hB6x8CJ+tH7z7GO9E6Mnd0zYGdY4ixw1KrdM5RnLJtXBk70m1zGPwYJ3Rtno6azWDWTxanZLIGayxKiPxH6E+dTWS7ov+tOdien'
        b'FjTxu6PhCXxOLVSLyGokN41ELVa71FBqV7VbE5Pljp4l5NmdPHugZw/y7EmePdGzF3keRJ69UInE4YnK9FYPrhFnDbLXRttr81EPIbV5o29i/Kv2bcI7p+FtAoeq/ci3'
        b'wQN881cHkG8+1udh6kBUwxDr03D1CPTkq+aIA2dkj0cyz+JTVDpVvkb/iaiv4xQ795zTSEn8hVOix+XQGrAXj7hS1eU6VbEWO1TLpSq1Grv69JriktUaB8+hc+EoE0qE'
        b'HfRWzyTvFrR7HEkOuXRBkUZl0Eh1JUbsTVUZSWKTAW+n7uQkNOAkUo0OuxDV0pxyqXWprdzq91XlGrWrVUZccGmJjriBNbhGXVG5s+9wsYF3J6OqVHoHDyjxE69RlZO3'
        b'qzV6bZ4WvcWNNGpQo1GZGlVuwUOcu9ZesNYqJ51p1Kt0hjwN9kWrVUYVBrJIW6w18h2KmuncQF1eib6YbFMoXVOgzS3o68w26bSocASJVq3RGbV55daeQpLfqaAHwwuM'
        b'xlLD1MhIValWvqqkRKc1yNWaSOt+5Q/G2j7nocHMUeUW9k8jz83XKvCuDKUIY9aU6NUDO4aweUoW6pHVUHmCJ1iqx5K1UNyDzf39yTqtUasq0lZo0Fj2Q0SdwajS5fb1'
        b'+OMfq0/bBinv1kYP2nwd6rdnFiTYP/X3YT9mM06hgqgYJnB6lcPajz4LP0bI7Us/4mVkDt04AZyyaiREGwmJD5fLYZUONuOdemPBHuE6+XgZzW+Aewhcc8c7G6dGyGH9'
        b'2NmwKZWmvMEBFm58NkpLzzlKGxagZPuWfY1XVYV8+g26hvt+o4y3LiSQLwlRJaqYC/5Do9ZERaqX3znf0rbjWrWs4VLpzupr1eMbIjZf29NRPebQDLIWkaU2ZQ96Lvd1'
        b'ZCrg6L6ofCxMHSeakNhGknObVXRvSCH6e9SK4aBheCWRy44yGbQCfi99cABeBZ1uwcWoxTK7HjEEWDixKYgPp9mXMTYMbo2fwFEsbIct8Aat8xtODBL/sslJS8Ahvg9o'
        b'slsY2Ahq44x4ogw2ewXDhqQIEd5reSiw0EkbJpGpzjWZ/mGgfTouMnoiS4kqaLhvGTzPu9o2zx2KmwVanoV1KclCCimANLwWFWETnE8wXYeDU4l49nUUzxsoHwlZFICV'
        b'8IqhzlhqXzuocAzH1Tc4y+aBY/EYPtkqp/q3MDavXZX99ycfxyi8h0Ew8Aok4vSgVvGTALSCRMraZpqQVrTK3gO93VCCLnsRGGQhUr/qbEuVHvg/dAILVcKqS3IfC1AB'
        b'D5A422qmPAKeAzZ4Hvg4TGHZZsLkj60q31YV5p1ateERVT1nryocV2XT2waYL8st0iKuHGFAzFn2eBCs3e+WrVlbqtUTpv8IKI7YoRiNoejNg+VK3y7vrdzGq4faebV1'
        b'D1eLwIFXP4Ub32mzHEcuiWtAHO8cPOgCOtNgE/oGLlGgWQZqTXgGLQ1Wr2R9wWkEWSVVGaLnY6ueA0cXwYYErKI3PwsbYzhE+w1MIry9Uhs/7kfGgBe3vym4NLzhlUFV'
        b'URJ2zLhAbdXLBUFs8qr4lebltR/JxkY+eP27+wUTOybcvDnlTVX65H/tSF91+fPJJzpyroncQ9b9O/d4xOWpwmnFDTnnXplSmLV35tfbB3/xL8prqD93p1XmSnwL+bCR'
        b'6ccDCf9LyOJKwPNxvA20WbIAu0sTRoObvAMf3mBAPTyTxbvvG0E3aMbe/XVga2/cB9ydQFhcFtwDN8NtG2zeD05B43mOA9bIiulBIeBwH69KfgEpOCgRkCUOSHg4srLJ'
        b'8Cqfdw88D7bEuyXBrZH4dAwulgY3wRmesRbCVnAM79PtDq/1Lv+m0/mQjQvgMjiTRPbQBMfAEftGjRE0WesCd69HPYG3c4+3cmbYOApJptMsrB0BtjptC/ckDBWRm0aX'
        b'qy8vNRKuGujMVWUSEoHhSkIXyda6/TibNbcTa32i/R2tG+v2sla8qe7xAVjrR49mrVYA/j9QheYUqHT5Gj7kwaa82Ki8j2KE9Jsn1Yl0mjVPogoNvOkkh08ZwXixvFQK'
        b'9oBbdpXFQWGBNfCgtuR2PGNYihLu/zDB/dXTiHJ9uDs3Pv/BcFEoLm19LWpHgPfmKdybs9+SnVnZHXf7xx/Pz/7Xp6GhMdzSv4370/iY8VmAzZl3p+Zbd/9hn+f89c+X'
        b'Zzeu+Pg79bqRXcrJM9tjfQ79uUvmQjSDeYOtCgU4shDpFEifQMoz8TZeWLkCNKTiNaPgVHgIohZwhPKATaxm+kyirYx0FcTBbU64bUVscGs1T857pHAv9jLALfgYlj0U'
        b'F0kjgqkBx/idKG+C2jn83rNJqaApMj5mEdbwiHoXBQ8LpwSOI0oP3AkbFsHjg+0KDJ1UDFoJbaYOn4i7cBjoclB6noHbif6yEp+xgRunlfcqN+A02MO375QWb/dvZwig'
        b'M4DwBHAJ1Dw9WXrmEmTLtmFG36Bi/DvVlWzX4kNXjOhDFH0y/zcUH3ziStcA1PmWE3U+BhAZ2yMsKDEYteoeF0QLRh0W9D1CXuAPvOSGUDBnX24jsC+3ETx0uY2Vgj+Z'
        b'TfcxvvHPM2o1NmQw1TnoCrzhZ5fVDyVdHniecOPRfcJcGwPIUekK+5OvneKtbeVzLuAfUeaQJJMOmY0RCXMHCOVxCAuy5cRGMs7mFAYkGwhevcZo0usMU6XKdL1Jo8TR'
        b'PPx+AOpwqXK+qsjAv1MVoZfqcqS8YA1KZ3xqDsQqtOcOfETzOwkMKbynXHnnzRfee+GdF863XNvdVt1WPaWhe2/3cyd3d9eOb+iobWsOag1qCaoL2hSU0SW4+2myiIr1'
        b'cCsZRMtYIv8K5CsJk1i8yMomeBYBqsBxfq5jN9iHV2BGRoA2M2IDPAuAF6MJB5gAz7FJyQnwgCuoT02BW5LlYGskCdiUgUZEkaBz7NOToodKrc7W5GhzDUQzJZTo5UyJ'
        b'SZgOK4b3QX7nfFYiFPI0tRdf9uHLfmdydASPc0i2yp6WkONBdLk1ADm+5ESOj4bov0pwOEzw2YEIbhFxRyGa0/FIhgPSHCjPwRH1/z/aw9kS0lKlvAvJyHuciGWQp9Wp'
        b'iqRqTZGmfxTdk1FdUEEIS6hu/Ju7n4LqBF7P3f30NYqK9XQrjfoAUR2Jnz4WC672CmekK5+wU95mjldpjwyHt22y94w/T3clYBPv4L8yJi8sETbBJmNAZBJocqa9WWCr'
        b'yFsY8fSUN4h3ZT6G+LII8fXRwOT9sv536Q/PJb02AP1ddqK/xwL1iBNsaAvlcILNw7cnZ4k5yD3IGYDyCBoSEtGZinMQtSHMc/AL93pbc016PeL+ReUOtvSvQUoq4BhH'
        b'QiDDai7gQ3K6WtoIOo7vg44LHBDy7qdFNPWtxOXLvz9nEwK52P+VOhOct2uLPDI+IydOprHr8Q7cGBXBwWetIgDUzzSGUngR0T5k8SG7CxmNSFCch9cckTFUiLDxmkgK'
        b'roOGPmcSDYiAuSUmndFhvAwDIWCOeCAE7JdVYQs3XPVwjKMdNK42dPlgABQ76fEoFOtX7X8RxXQPRbHe8OInRi9pSChWwrQ66epY+YTQAXjw49Ftwiu1AoJuzyTMHRDd'
        b'7tf0439E5/jmzy6vvDMNoRtZOFhbjPSLhlSDpA+6gVvgNmF+BrAbXkAYVx4cYdc5wGl4woi3TqxUgQP8CXnOSkeou5+QmgwsQpS2NecJsM0L9+HjkG0Vv+1Un1Hvm/Np'
        b'ce0ounw2AK4954Rrj6tVNrTv4mJRdra6JDc7u4fLNumLetzxNds2wdHjZl8volXrm3AmfA6Tfju+4GNliLe1R1yqLynV6I3lPWKb+5JMc/aIrI7CHtde1xvxIhBjhahI'
        b'hE8TSiJN/NW7Fzh4/izoYmKskd5iN47BEZv2XybQgyEBIf2ujLdboHugZ6Cnh9iE0aYAXIG1vWuH4SXQtDQFWa7I8GWoELBRsAF2whqnqRBMyXGUdWm688wrv5ddz2Dr'
        b'UgzrQJHdnB9I563Fe1Bix2QuXmeh12EdzEHnUiBJ5zxw+mP2RvdxfJ5Bl3uMfdU3R5vwUT3wskts7742sMvWKtucQ6JrHDgrAs2gFWw24bhTcBa2gqtO8cUktjhh6ZNG'
        b'F4M9sN2Jt7nZOATuImsIPuV8NGjvnrhPc7YMLry/f1WikLEk2MRjnRs3isXTQdIiv3X3S0mE5kRa6CqgJ1MkQtNv+8p7VBFeL53kPUPwjd+1/P/MGya7Vrgg+9TI9sLr'
        b'mZtC9ilenjxhaVP4wdTOacenrhj+duiRnP8Nf5Cywf3LYe6VNxd3hdTMmZj4laL8mU9GCANcAz/MnJ312cwbYw8smpVeP3xn6M2Ry2afobO9j5eeG5mT/YH2omjU4mNK'
        b'zeTEwtdcvkuYEeY+tCBTL6ga9eXc1a7fGlaXhgx9f94pN3/36xv+g9T/1uCF/KmORXDLYqvr1+b3BU3KRNglIC29ncskvsySIEvJGmWg9YhiyeDJ79N4I2Xl9PMlGfzL'
        b'mqm+0jeoTLx4c/qsiA384k0T2Ay2wYYM+FxKhBwf9GrbtAs2J4ngNtBRDuvngV2CMRSoGesC2zLAeT5UfA3nUUAjPhinLFq41BrP65EpTP8XjpWUKpMPmEX8Tq+/VHyR'
        b'S+hkyjH681Pa1LerOQOm17K6D8c03XBnx0vmyF75Z5nv5GFLx05TC4bQbw1f1JPyYciy9/bPf3niqBGylsQhl1vf6/xhb/LUnaL/fXH2xsTa2mkBi8///tjCoBXef/zE'
        b'bI7/w/zsNWeDE5c8c6Xm1Zc3D1sRcXnNyW88pyr1d9Zp19+YPzj7veh/f++f8uEHee++lPGpMj95/ajbv5xuGbuz5FsZR9xYufrRvIPX5twFp+C+EoTPp4gR6wer4YkB'
        b'w384sD0bnoPNK/nZvWak3RwOwyc5JuE+FFDDZW7wOj6KF5wjYisFngHXw+CWUOzLEsLTRnCYmQJrS/oHg//ajXgdl8DrDSonX/IoZ8Fl5kjgnBf2IzNetJQR0z74YKCz'
        b'dr7M9nB4Qt5BXP3q/YFp/Tk7x8IV/GMA2dYodQyAIc71S5ODw0IVoLHXS0kNG58NDnLgdBnY68RtBtpC0YHb2LdQfKplPwPP5LjaOM25dNS4qEWE07wnHpRNOM3zKSIq'
        b'EL2h5hcl/yuqfNEdntP8smb6/zNOE5mwaO0fPLtLvpvQw24LXVQaHXh84pdz/6E+tLjWbUL4NYaqeOchnObuM+U0acrHixmqfYo7YSVLYnQ8TRdP8qZujsTQKwPz3abx'
        b'k2vky7CZAmp5tg9mAeGJK6ycZ2+ikLqTFoBZgOQQk0QRFrYG7MP+XSsPG+xmnb2aDBu1uogJrAFvbFQW80HE/3S7wygJd+fkyvP3B9VcfP9uWJfhq9B5y2X0TMQNapkP'
        b'Wz7+09vfVUlX/7xQc3/S9ImTR753ddaMcwuuV/rO2fdG0pzXOtpizn9zObTivUnrbwz3TTE0hoU3nD/0jz1rwb2JD5Z3m3+ZWDj8UvBcGc2bz6fEK5ISyOHe4BA4jg9o'
        b'ZTTghsJJI3u6aNm+tKfW9NJesDPtbaA88dy4D9nDyofQn4RQo76rl/p4kuklvqfeU6uX5HCpYta2cV+Vw+8Dx62qyDLYgjzYyRNdQoqN5sAueEbJgbbZ+U7L8fAf2eKy'
        b'AFFinYDfMd5MH6YwrbUxlQy5Z9Ucumdb6LUhRhqnmUu10CsCljOVXCXeWV5QRxkZfNwBUik9zILDrFrQRlcKMijdCLyne6GrvpQ/PYh8wycLCfg93HWvmfGpNXGkDJz/'
        b'upnVt6BUgjZ8htBZdCckxzLguoSVojraLMI70KtFTSiHWTidKtuHaqkl+QXV+IQYVv8mPgIBtUOwVoegFZA973F+cb/8YpS/B+WfT/LzZ/bE2XOH2HMHPix3C433v68T'
        b'8jnQO8STUZnhGdbd962n8uSYKbWLP+ZVvCbkqkB8WaMpna/HC9nSHwhMxryIyfbDZRAGd+Mxxx/1eP8LPVYIZSK9CmOmi0ZnKtbo8aEMcfhZiPdaV2t6JIt1WnxDNFQ+'
        b'73Qe6Xp3Yuwtlux9T1YqYTVLj6N/euhVT7u/kwQfgmKI5hfFBmD0nEq4uZhEdeKjPPgDQbzJOQ0cWYDl53Ansf4Xk6XpYl5m5JvgXv648thQvGkN2XpAOkIPOzjY7RXs'
        b'FHJg31wacwQzZRCr6TQKn+NEep8hxyTgDYtID+on2EmT7qEND7EZ3Umbso0l2UUluvxprO1cTxZbI8TOAOfAcQMPIbJLYT2/+Z8XqMJaFzUWbBaUg8ujnU7esYdcTSBw'
        b'qulCWi/BNoaaNePTkmg1d5jCJ/EgqAW+VBttpodSWNLhNwRnhNY2kOgIZsxasjjrG4ZvjKAiT1tUJGN6aF0PXfCwhuH24HaRBs7GDXO1jhZHDl4xYR43bfB4sgVYcxI+'
        b'exO1LRU1FF4uSIgQUmNHCMrhWXDkEet06QHX6T7FUYC0Y5EOKyh7F6P9dUMZ9TFFTY7KTZtzM8iVf/lyykt4lZC0K/2LjPNui6wr1NKFZJVb1JI3C3KMMZT24IxlAkM+'
        b'+vLcnzPuKVeQHZYugc7qjupLe3+3OejdU7vbatuqg/bfmpQYf7LaROe6z3H9bPYJxbuz2wJqBclu/ls2S48MDx/+2kTJ642yZO847yOjAoNfFUeP27xUEnK9aspmTVBu'
        b'FJsfQF3dEdC0Yo7M6uk9BXbpwyJC8IJeuB/UkkW94GIUP/9SC26U9p6GN03Ln4dXMpRXSY/ocmFDuAKZf7A5nMb7cmx1w0sqz8KT8UT3TU4EneB0ItkxuZ7G+yrcFK5n'
        b'Rq2Bzz/9suBBxSXqKZP40yay1dp8rbHvZrHWDZjENH8Gj5gOpPUv2Mnq/2rhLy4maUARd8Vp8S/eNRTugDvBdryXZSronjAfPeDddPGpP/iQWGtfTQYnhesN4OrAHAN7'
        b'gXg+gaVdG09ljKJHoDLkarUIskuUXQb3PwtWVKBZW6TNK1/MWk+8oliyHZhqA7hBJtzJNjrgNEe5wc0MvAiOwutgG6gbGBYstfHpKkQG+uDDiDBElVb4CA9jFHrAQzLL'
        b'Aa5HbKDlYtJZYczq5WFYQ+G3O7wCa+CJMNjkDOzgdKOQhQfBEdjyxL2W5wDbI/vMJSd2An96lsqh10iMzlUOHE6KjkmwG3GeQTMmsNPgxrRf2WF5v6LDEHi8LM3r02E4'
        b'GKEAXorDEPIap4DygGcD4BZ2PDItq5wC0ewnwWFRqKYRa0dq1NpRZkofasSsn61mkDpBVbL8iVFmBjF6pswVn9JUGmum8dlN/Caaip7gqPHRMRMmxk6aPOWZ2XPmzpv/'
        b'bHxCYlJyiiJ1wcJFaemLl2RkLs3iBQFm3byaQCONQLsaEbKM6xHykxQ9gtwCld7QI8QbTsTE8sLfpW/rY2L5wSlmbcdXEJEnJNvDkBheeA5cfyYpOrbX1vYcCm4OZ6eC'
        b'A/DCwAMlseKLmrbKYjQsd+38gta/+hBMiYnlh2JNX0w5KBdhCHqH4Vgu3MpGgdqRA+90SI69pu3HXiNgnnx3Q4p6yOkquNAKaFluW4sMdy1OcVkIL4Eu2CFahP5fWuQO'
        b'tjJUCLzKFcOjSdqibXcYA+7C5Aef3lNm3nmls6tFReci4fKyUviGLzXuX9yiT1DnkMmayYiF1ILG+WERCXArbIgUUS4xDGjDREk4vhHsN4fJe5cYxsDzZJWhbPnDDq7W'
        b'GkqyjdpijcGoKi4dyAeOf1n9b+0Dwwzs4XbwWuK05gG5da3TIdYYMc3QMh1va7WVqBQI5gh5AtgXBBsRKx+rF2wAx8G2+U7hZs6eR9Yabubgd0RD6vaEkZ1OQ4rVAs9+'
        b'QzrIGtm5A96OS0LCdits5ChhwDTYxLiaiogucdVlKBWOdQm5MMXEmCmyIB2eB/tcY+B1fTTojo6iRlEiBQ32+wwhH72GFsb4gBvR4HI0uMShb2APDS4PDjbhoCPQATbD'
        b'3fMnwx0CfmV+FeRdc8nj/KgoioqKUviPfzVuPVWEMTlnmYxagF+qvk+bs4is7AddGmiBNWKyJ900ahponk7yZ2aQpfpRUb775rwqSbIerb2aX9kfJfwfITtJh1CEtLei'
        b'BGxMSgBnXMH2cCHFBdLgPJJS1SQLnPkMGkukZWl3BrbKZ/HlVK6cRVasR8nuuwSPL+df5ozl9xKIiuVclWmjKS0tOE0bPkBfjh3RzWt5IfHFOEntf9QnDsYuSV333pDf'
        b'jqhk/gQaNv1GmtNm+Xbe3eVnZv/j8E/i7/ZPfck0Jpj7xfyvOcsPDXvJ/aa+LHn6yquvLcgqiBzxctjQzT+K/ty1py0sQPvm1dKFOyaN+M/f//rS3ktZBZ/WR99cvTf+'
        b'2lc//E72duk3B16JsoxeXDh1weuRl7w+udQd/ffF39evrb9lfnutIhMuMPfsuuq513D3d69kLtslW9tR8WPCsumLr731RuK33wQ1fzRnT+HpiPai7jkK34i/d08uCt/1'
        b'Xf4ffvrrejhcePulB3v+8b+iY3+efRNaZEJ+H7LdsBtJrqVTbfwIOyGYcD6S9tKz48NiQEOfg46HwSNE73OFB4Y4nqcMGsBBJiIMnCJf5f+nvS8Bj6LKGq2t905nD0mA'
        b'EJYAWQFBBFllCYSQgIIEQW1DqhNCku5Q3YEQKy6Adjc7iLKICOKCIiiiuOA2Vc6m//zjOI7OtOOM47jhOK7j6I8z4zvn3KpOBwLivPn/N+99j3xU1626dZdz7z33nHPP'
        b'Mlm/uXKsHkZN3AQ1XGk2aRd0LNajLn2/dsuZZggXavcxL2g3LpqGYytpu/UDnLCMn6To951/eLN/hfwyqRU2HZ8XkM+Y0cNHENoZfybasUk8k2NKvEd0Az3pBtQh8QN4'
        b'gYyA0yjOo9swHlZejqMo5pQj5qwPKHU+LwUp7MJZ/4w7bUH5Bccluu/Aum7oEcWtzj8dxSXrm9uKZ5YUkVY1YrrHh2u3a/eMHC5xg3hJuxXW9zPkSFLbfOU184CFzOK4'
        b'/lx/2Cp21Jnmf92UhtCVd4THqJRR4J8wlmAEGUWLKiklqgX+S7CtWrK5DMjVC/Kowj6eNHKN4+eIKIvmd2tEFmIYconKkoi0D56r4n4BSmaBDKXqbtxqPEAmzjWKE5vB'
        b'eFEVCutFIQvPGiWWiIuz7BnIPN9jbuhWriN/SXMAGA2my9NTWFtG0YgxS1trq09RLsEBl4jVtcakkK89BJQCFhFs7PDFHEEfqhiFMG7rykY5tFT5JeYXZd+ZcWuhgb/C'
        b'+1fjk9Wd2JY7RNNbNYkycB7CjBTQyx5JAPRHVmrbK/V1enQO4zjQwWEVrON++l7tuL5d0h/N0k50IwvjMMWBRbKQyFcOyNdskrFhvGcY6H0IZYx1KCKUSQInKEtgcAVZ'
        b'ghyiKmLEbAwQ2iniIFIJi+ApxavG95BbnMfJFhpYa/WpoeOvnNTe0lxWPInIu0Z/w4TFA4ZcNXTx1XAtLsT7sqJJV06aSOTySWwsCZ0MqRSwcEg/x6xBX61StzRmaVAC'
        b'ba0xC8p84Kc5sBIGhsh+KSZCPTFbK+plKf6YBQAJH9jNas9Fe6egq0P42mtmPiSaxwuiZLoHIA+GDFNIPBms6ftgD7ybnAhqDwEq3ZOhb9Sicxh5Sv4dbRz0QNux1BUn'
        b'L7qdPe6kwQCqW8jgkA5n/IPSjtYryiC87uP3c8EyVZCBTlc5L9q1CMpEvNKbaSrQAl6hPVdFMWVaJ3ElUJ7YCwaG55bPqmFftMa/2Ma+8OeqvLKN3m04/Z1hkCJVx3jn'
        b'KSE/n8YDwEez9fe0CEK1jc14vONr9rXAKPhW+JrPsfJi7lbFF0JTSgTyiS7YsrmNZ0hWskvAk6QMvo10v3cG9PuLh84qLSTeUNtAEN7Ic/21uzxplqHa7aN6NmLGoNVd'
        b'R+mAi7hFok+iMIochkrcLi6zLrMtssMzDJ+Iz2w+2zKHbDNTGF4R8BiaMNsXOeUBGGwA0i7ZvdaxyCUPNNJJsgfSbiMYgRS211vkZDkFvknq9ixVToNnnvgTSU6XM+BJ'
        b'crdcmXIWPEsh02VuUao8KCwC14DGyY5FaXIBpfLkfpBKlwfDN1ZoQb7cH9IZFPogkwQIQ2Ku6TAkPn9oCvBa8UlnygDnmVi1S8ZOAX85WTLvTeaP76RhP/kt/DvFXwxU'
        b'/RSuK4xZZXx8ExaRlxYlxRcPttbW+V6OM09CR5+EZpWdnvEM3o3aidspstYwPU1On8fjlU8JrYZqG3q25Io5WptrG/1eyPBqQgMyExsQz9GtZsGsOY1jBmQBj7kETcM5'
        b'IWbxIuKnZXAWSzJcJm908Y0dKYk148fdhiVeqZuGBde43GW5pnxxbqBTZW91dbMbFxOX+rbGRxyxfPtCklDzRjzemXjKwuLvqqIsNAnKaBmFA8J4bnk2PJGarMFs2aKK'
        b'+AuYnscTFHhiY19lcWbeGigfA1EbY2WvPsUPi/FFp4SyYdAD8iuLi1T5BAeJv/aU5dqizoIgbq8scrkT2EMlFFzZCFvnJVyXeQP5Qq+ij1rPJlv2AoKB3ddHbtbfEU0O'
        b'k5CKncK95AJi6cjpNgsTv6mOe6MUEyGXZ85BglyISfYFCrcN68UcJlHByPPQjzYgE5BC8MumphY2PuaMz/SzSP2Vf8DlU9HgCbHZ3WcNlvhPNrChq4HK37ExNiysFmiY'
        b'hBYq33JnpZpwafylW9PST28alHYGqokrJUZgMkUkJDQiNL+XwTTZKFBbebOtGE3cCGotoL2mxR9sqW2FFvK82Wwr86NvrIWYzcfacH5GxrAVcl+LhmkoxwK88x1pif1g'
        b'xfcM5OGsG0K8G0K8G0JiNxDkPAt3Xk8dofZ370Yj+gsKmcBHIZ0i8udrLC1Bzn9070faaf1g5XcbjrgMCdmfCLQzIkI/ikyMoOQjAcJCgXdCX5AGxDUcEozJJBprGg9K'
        b'TvGTGTkgKaewRbXxeeXyeoGKagz5WrxeE2OVc9/tPFGxQqckyTwOMgKqwzTr1W2xdhXe8xhdnTjVys7VNzZK/qL4iJYbIwr7H42oaIyoZOY1NMikasXCG+SpObYWBoaF'
        b'eOkaZYBFMA4LsQsWhMLPb6htUJhLMrZBEyoewUn28N0hE6/qHPEwzfOF+aaMrqed0+71LgkEmr3eTKlr48zoXhnLYFDn8+NjYfIYFMMeBdYU1Z2rR+KWR/J1D+wuO4RN'
        b'vGHrXA5geYeLk4arABk3+kOxZCTCZV9dc61prB2zhwLsgNfcD96h9iKsc7mexI1WxYdhcnKkOM5yn7ZGWIbyMxpPEyk/3niZJossbJSI8eGZIgJ1AAgkqW7EKD/av7FI'
        b'OzGHr72uuS3YuMIXS8I9zAssJNYY/AKblg8d8wcnDBhAJ6iwPtDXTswGO1AzbAtm11KwV6l4+UNPXVM88KqvZJ4OkFCi+0aBbYqvffw4zmq8BpdGYDHal+F2QVoNV7Nu'
        b'0dYhwZwHxnw/nlvzOdyVQqel06paVKHJqsi0Piw5GJpHCM5n9w08/o433gCOsCISX+5Rrez5ck8N114Cq0pCbQqoLQ/KtHXaoXaraoMabaodgavaenGQWyVGxdbpUB3K'
        b'syoffFhFbQwH5BDHc35JdSCVEnxRFYIvytALyAtfN/LmuqSzaVycpywDkcQqdMTcsCaAY2xslmG4Y7ZQwCs31oVIKYH2A9hRQjCvlsQcmBEXUJBIS8bmfM6RGIf2Gmdd'
        b'wB9k1nQxXsbTDCg0xtcpn+FboU5m/pkqzY/PspFmQaUDJNMRFcqbiK9kbuZSBDefITBOiMWlk8j/RffN1ugEkYZICjugyPmFQnl5IV9emHW6yi/15qDZG+WjeOe+4BhH'
        b'jYwyowyQ/qCdnkBD+wzhZUJDih0vSbwxAakjCTGlzl+olxhsClvzM9FYb3bRLrktdsFt8Uged4qUImVYM6xptgynXYInFqbMt365tjqIUTQ3Vukbi5fPKqm2cDnanfmT'
        b'pfI8PTq/kGehtB/Qt/RhtktkuaRTJEb8otCq79DD3AWydX6K9hRkR2Slb6jVt1bGS+U513XCxOH6oQV6pNuJDuIKUlXyxPGDym/iE3xMtNQ2+UyqROjSeunh8NYY0ku6'
        b'sCz5qW25Ij2Y0BCntldoUPX1xdPPOBHCf8H5XAKjm0KR8FBzHNhaYCAlYFF55pFrEYuhLtSLBktrRb9ckMcmu+Uk+LXLHjl5Lfr1Yme9qTH3tLaWllVGM88kjWlbQX0L'
        b'xq/AZssnMJN8FzPJpAlwFUmyIBmcjaVa+TNnbKTKx5zBE8C+iAuK+Ew2Y18laHmRSPfHSSZadFb27HRuCM0LKqQ4fWTl8+B/R2Zib87fdQtzX6IM4M+6XzqAJmENmRMf'
        b'Sr4jq1t18Sw9k2TGASURHAaLa4ozqcYZPc4gRmsh/vJ6L0uoOvu0nsYz9Vz5RBpCmQeez426YUQbAo5XBkUICMh5Y7NggAWU7ykX4AAmNHdpXLfJwghdGkCEGJFF3cjA'
        b's4vfCNNc3kXr2EnW5iFJW09dOi9iBzkJ1rRzEDw2r7fZ5/d6r06AYcZpFVKGnuUE2I0Q12Ae+RMakHA3OTt9hW+93tqE+s6YnZTjO3qH7EX5OXpGKFs+Ry2MjMMmO0/f'
        b'NnARKYNwDAvi28BgvAyN7wWO7xjQ/pCp3BxQu+i02kW3mOIANC+S5y59q75rWrAQcbR2OJSA8/K0J/VjPknfoe3y94z1UF/QxHrbxWXiMmmRxcdUvVB4J/mkZTYg1IwU'
        b'Hb0jRrQvsjNxG2BBhhUdJDZzMllFLG3OkmW+uhD5ojOg9D1kQw1sO8Z99bskQ/74oIgdvc6s9L9FQBTs2mjOCwutPS8sRNNjZcIcy+uhO2fDQfFI9Ki+vSolxBk8l8F7'
        b'SsB9NjmV4Uxvl7CRqNK5AzYQ3lrgrWxo9fL7rMTrLYIcti5+D8vp6lTCaXwCF2cnfo3meMxZAVxBO9Nf/cxcAzHPJUQltoUMzdY41/t9kFuHFJdICUDieeg/yqbODjOD'
        b'eXSdvjoL+UQqjpF3ed0X63mG+8SSlpp8t11i1JebhbybqB9fqB+bo6+b5df2VJWhStv62VXLE1bqFO0+28ALO3pepLkJi5QIEToTBOJEpCGQYr3NbpsoaSr6zJwdCDS1'
        b'tcYPJC3GXEmPrztjr4rASBqjCUhejGMkC6PXpdCqVp+C0edijrjk7Sw7qbWZ6ox0MYvAUg04R+vK2Ac9WNgNi7fjjJVSAq9uMlcK4ECMfzpeu6ORgZjgqx3qwoPL9U0V'
        b'JWX6cdSD1TeXlXLanSWcdutyp757eGq3k6S4+AMFSbB9cyTQ6EOLiUc2aR8waPtJqV4piSCzx0WsyMNGOLq37GfbOH/q71PJmQha/ta1BUOBlsYOn5zfDGxrPp2jK/lD'
        b'fSHF50Nfo4GuOVt4dj+nlP1i9M9ADlnQdLixwR9QoI4ueWh+rV/OR3YZ3UnUynIjC/CUX2SwOkMLi/IZg93dnDihCd2rqG1uDqwMkv8XpRaDM6HLU3+p6Q4l36DQg92L'
        b'g8VMx4ziwqrZsGqQ+465EuogocP3jUQ2AkZ9q2Rqs9mZ0y06xEVqv7+2VT+urdcf1h8DLKYfXRxEfZ5t+m0UKGxxVTtFVKe3ot82l780+aKeo2NfnbDY5K6jJ2u9hQ69'
        b'HItE0mCyws6HB1522BUlOuISZZtsR/5AdshOoP+tCQdd9kU22h/ttB14Ym5jJVQBk6NUl3fzNBKfhGhjKnONMLlkfo/YKcXlcYOACeAbURmRa+DpvAHZBkHZEJfBTVQF'
        b'4w1QmjkcsA4Scv6qGPTjHaWlHCgdJQ7QDybRE9r7qMI01A+wwJcWMxfJH0I1nCmbXSbUw5tNPG/unFYUiZfheiWZXT+8EK3Y9YydecacXhJFe2Fasa0CqSPT5wRl/Jbm'
        b'Sqviq29s96KGI7F+McF/rogyp/EsByXTvE4QUPFEwLmCnqgl8kidQsHy3CQuiB9k0Uh0cTMmVrBxCVocj+CA4IYIE6FBwsN8FP3wQLJ2iu3bVDz+WcdEP3iQHxxD4iCJ'
        b'BDl57f6QoEp43M/OSWXbRgT1AlM0tE+S7bDpqvQNTiEaEsBB1jUw1FRGNTx3AsLejnnYG+M5YSI0oVkjsCc1UGMNpzJPT67qmGUeHgbFxOl+OSZVY8xty4La5jZfz0QZ'
        b'OypEwZUsNFkNUTXT3hCUMThKFycg5x70T8n9409R94D8b5Z2h3FdwA+YJEQIKZioKMK8ckKRJNyNkxWmEMqCAj7CQYbEKUhR7pgM6hTDKLRjiUHf8pgloMg+BcWXwbbm'
        b'EDESLV2SpXOpL3i6t/AZyRCrcLzbYKacMKMEAbVpM+C+DxqMObP5jt7n6Ge3o8S4dHQWhyo5sPAm0uwZ3SkCiUWaPmSAVYYzjMTs4n421k5VhE0bMCcqkeBTfFbDDklw'
        b'+0ZGBqWoAC8fjLXdW9+MChx+gpgpF52IkJ2Ml0v4c1Nb0+D9b7tYSck4IyE3sqetHKOiM/ZTmlERLvGQHLWoVexFNp5SkbwD1tR+1KSGd+zwAN6G6E6Eu5khQESqkAW7'
        b'8Gqe9CsAZe3niYyFVQJrQkYxpj/FfIJ58BhVtrA7eAIQzWJEjrWaHZoKXi+bX1mX+5v8gZX+ro00f0BBcMAp67UFQTxTtSrpCKz/wo+sDIMpo/DJOM6kXsUuyl4ZzZ+x'
        b'IGJJXj/qIqGfaCjgXQRpVsKUSjFOJLJ4q5DCd+R2B23ip90wE8KXpGgyl3huSTMG6RSkWAR218h1Su2DmcKRYUKHeAe/IfM+1apKhOhLANFL7KhqGWwD9VDSXgHRvcmU'
        b'W5UK3pgaCrqQY+uPDmqAI0dX60Bo2xKkS3ZTbKz0wmXrYIJi6EvCcuxZxjsL8n/RRewDjESU5KYRrM5A3UbVYjUsAUePbPiUeMOpC7O6k/fnGdK1i+QfCd/f3UXyZ2Wm'
        b'9AOu3EMmGYJ2aGaX+FE/WqVvQF9Peb30gw2SdmKUfvQML974j2LBxsmPZGK4TbKDudQ3iQ58czrBgbyBQW6QPg0KI5kQMiVmnx2oaypvbPZVv8+qemtSnOzopt6AOClC'
        b'zDjOpmBGSJB5WneMWRboHR1iZqEsUlKBlfRaSCJpJemkDc3gvPb4Md+pdIx0my8HfIYzfCQeT9kKgmWopIdjRcf61sYg5qNFFbPVLgmiIkHMTop8cqMSs6HOe6AtFLN4'
        b'WyggDAXQjdm8mANI5wT9hpiEOZT5fE/cA84EiyU+qdxEG6QRfWDlO1JNMJ0p2USM5jShtIEzNTpRrIfmfe0rVqVEcL0BDkK8XMP5FxgGsyt4wE481zFGhTUF+FtUJq7G'
        b'76zKTBIBsnL4Jkm5MmSTBYQ2PLPLRjkyh9gNLeyu4JanAOstMVjPg1QNF5cCn0wlZFYXaGuWCdC1deSGPx8B9P7uXfjv/knzCx3A0gEoCTwxS0sTAFeZR+dnc+YRVx6z'
        b'+BQFkE4NPnRf1ubH7MabYLPP12qgu5gN9hgqqu6sazgmYe3JFuMckyMrUoHcHDjJ8YtEI4Bmzx1JcdjjNz2boJRwTGCkDJZpPsJs5E2YK4MB/pIJf2P+4YZooa6wqWFp'
        b'DMY7bFFa4N4QL/XAzbb5sSH5lgQROBrQdCTHG8pynIuMYiSinCACrz+7CBz9AfkAiQ22dMmBUhJmJL3sGTBFCbXhlDSkzgKTOtOhAQDGsFomaZdE7tWUy03QKAu6GtaD'
        b'FY/XC7gWhamFlrh2gZ3IaRi6tIRGGtm6KSHj/xps5iBz/LJMgR8Ch+li4oEpnyCOE6lFMUtdcwBoPgKboa8ieX3tdT3IgwG1wIodnjhgztNXNcuDoo5qniyqe9opCDJY'
        b'o9KAFzSoV5rOR1ZbBZl4i8Gl2iWP05PqRnmtjQwK9cP6jqHo1Aiti+bom1YYYbGTlolO7S7tcLc9wWb80u4el/+gXrgEzGZcBoSamIskOSXMgseIYWvYXm8lsawD9oZU'
        b'xp5S+Bc8oHLAPsEcm+ExVXfGNC0mlc+dVt4N48VpjGkciucNyoDO8pEFNEcNfqFNEWGZhAbPlLbIQsjKUsa+YLoOOuWauworuiB/RUHwVBIkjAjZkDSFiI00pOiRs7W2'
        b'wRdzB30hb6sSkNvqgKp349feBdMvm1cxpzrmwnfkvRUwlMvrNYJIe71Mi9yLMUpMCq3rIPEcg4h1j+ua5WmkVwvrPgmrPZNJPJtc2dASOZU6D1qR31LrJ++W6MMF0UCo'
        b'az4z1xCnk4zYq3j7p8QxgtCRRs3o9ro63hgU8zlMpBBJGDNca+jZWxWYLGuZoFwdAY4U71DZHDhKEbhQ2NfXMNV0uu8UgVYXe3GoA01PYaffZ2W6G0Rh8srqCNCJsmWN'
        b'sDmlUwIe16YK5r51KXcZt5BxJ2T0jkrpX+DKdBYUzJs+95L8L7CrTFWxHXh+JxHkMWHlEmMaxKyw47e2hQhaMYvc1tIaJNkS6TTS4WbMshL1DQxxJcNkBE/6RKhfev4m'
        b'00oHnrRYTIVqMom2kjcDJDjTaK/K4DtcBH/WsJhjpq95hS/UWFeroBySGXDiINSZIqXkxBFp5RkntB8VqHgaE6TCSbca4C0aK4ngS/fA9wBlLuKbCB+yAP9nyeBQ2RRd'
        b'WLB0b5a2y9ZOh2zrdDLZQKdrC9f+DxhvFymmft7pBhrfncN1JqkO5SdmXjUJRhMlD3tkR2eSP4/STkg/JbvgrVm/HetfHureHtWtArWZzTVxyltYtuzuxeVwrW9DSR7V'
        b'g+435CTV02TDO9XD6oH7Aaobrh48XjAwB5Qpe1QblimLnQ5ohYe1gr6E96gJzurE96iuIttUi5qkOmH/dyzDq2uZW07daIXynEoIc6HISrUS15JWfRLN9E7iSMw/iWP+'
        b'fjjrN//51bwvJ5WTXOOUOGHCBBq6mOgFvMHPZ5whnx/jp8RsUwNtSiOgHb4CVZb9vpXedvazqjCJqfA7Sem2udHvCzJ01FKrNDT6g7F0TNS2hQKExrxLAEs1xez4sD7g'
        b'B1pWCbT5ZXYMEsD5KtX5mptj0sK5gWBMmj29fH5MuoLuq6cvnF+YzOY4neRLVIBE1jKWYGgV0MIubIB3qa+xYSkUzVrjxAzeZmiOz7gH/hWqsCg+aEXMuoTJSRz+thYv'
        b'fcGUgyW8h6e+9hA9/s6gzS6m8kn63PMtBh/BGcEi3XRIk0K2HiwYJPMH6DRciZBrEaEPieWs9AVbdpKx7FAxixZdQiVnSFRol1K47uuLjrL60JE7cjOzZCHKoeFTSCRu'
        b'CXdPO8pe1hjOOnLQcoSXrSqfxVQcJdmG2CxkMYSf1jhPLJIIlO2cjlO5U2oVtHHOHxmoH8tk8OR5IdjWonyJc6n4fOy/S8vyBw0rLuhGO8WVzhApkQGXpxN6wLh9w3Rr'
        b'rSmNw5ML03irT4/8D5o8rTZ3EyvX0Y8Ai00fObYns62TaJtzSioqCBbRWqkGRvkVzhC5oUGQTErmMRF6GvPQzG4ERrwu0BxQDBzOCjc5tFe778PdfW6+FG8nhl1RLabs'
        b'CR0zkSEhSv0NDGwUS6TsdUicxRGwcv3ZSbsVvIHolQO8UU2CEOB7e3XqEgc0Q0kXWeLigBSbXcr2ZAwl49xkfevlQVfrcpET9N3aMW0P318/qkVR2S6+7ZMWmlhdXY3q'
        b'ZyIFpYY8jy2fxw1oZfaF21R8SXa6d6YIOPHHbHNe4x55/WBoSXnjC9NXCcEdQLRZBt1XNb9xXvoVGX8uGHTHxk6XlDZtec1t+ftmPj9NmDmqxPrgrt3TH/rZzuV92lr7'
        b'/HjTolvnv/lGv6+Tv54z4ZPPXtx115jQndd+fF3vR9596pMtA+dNrpn1fKQPN+5uz4ZZOdm3CC/fUnXNlcueXztbvEURd24bMLzU9Xz1/cIJ2fLr0pHP5/1G+OuLpdfc'
        b'+aD4zbspY/Jfv2HNI+4+25LeevhBfuQj74ybsWv4j+f9zf7JwFGxv2ru3yntL72y8I2mRTdO/+P2psWlJxr/OHZO+qnfOEo+uGD8eydCmwa/cfVLnmPrvmi5eE6vv3yz'
        b'U96/670Lj/xX6u671u/ue8OHwtdXtV9910vrmp66serbKb/52TNXvmUp0+57wXdE2fgn9a37ThZd1fTjP7zpenfGx6uXZe6+4PW/D73qvt6x1zIX3ph0+7rli79pSKnd'
        b'kPx36c27G291PPDq0V89rMs/fHvokEtn3LgjpTFy7On1z6aPmnqsZXN9wW8U/eCCVR+8eM/YohuG/WTsp3s/GrVn3o73fvjNh7/O+nHKfS98teqWfp9u6ndg8aM3VPx1'
        b'a6bHcuTuu++9/sOvSyv/fNOak2V7n8h4fpjn58XjX+ocf8ORyoMHNox54+C4a18b98AnBwqeOnzxC3cPuHHxpf81+A87tBc+/vSqvJuUfrf+fr9v/hO/VV72XXnyg7LD'
        b'j5YuGrvp0StbRxTd/Ov7fjdryFefbtj1xfAHfvejTdsendVUP+tA+Y7yTXkHYm+3TKr+6mDo3sYVH6w6dDjzP5798INnZn9VtcHf0k9uO/an+SOaN9dXjvesWDM6adyG'
        b'Q3N7XT5te+mrafeUduwLDHzgyx3La96Yf+GHl/zsql/tePeVqR3y18t/5l19vHzczX969bfTD7x5zwT9vsw53/xl4ZsjP3/h0SP231/cd6dnQue7wYN/2bL3g2Vvf23d'
        b'feqBhlUff3PHkS/q/uNb26lLW+7f9fLWST+47N0J7/wtet3oNyp3Rw9/NvXT515+6N7bFr943Z8/y8kb+JMvt++946S+9fkfHe+7YtU/nhumfRX5YOzov1/5Xu++HcfK'
        b'9t71zi9/Ee37XsH1ufqJIWV/X7Hk+sdabh25+dmr5069/sZNm5Yd+vDSH37yl7SjV3946OjGgh9kLvzHvpqHn942a2CZv1i4dsob6ZEvhzxz858v/HzQfMvPXv22aOeW'
        b'6C8Xbll2xcWPf/iR68NPZtgyr1y2d0hrQeCDw7sqLp750qpTTVcUtz2e2jnH1/bt3LxfjpM7hlzUu+JWx+XTNlzW2fLNwS8CHck/vPZX/NttuU02v7q71y/enTDbf8uh'
        b'J968/gNxez/56NYLjn76XI3y9e0Dm36+rl+nOOb9x346ckVhEoVuKtYfG0enkZv16Mi8ObMrSrV12mYbl6nfKOqPztTWUSQj7alpVsw1h06vtU2YI1V7ukPfJ2q3pI+k'
        b'krQd2mF0KlFVWqFtGDazRI9yXJp2s3ZUOyxqjzZqdxkeJnbo95Lz2epF2v7SIjQ/f0zQbkueRubnF+lrg2cGqM7U94raw+4aFlXphH5A23SGsuishslSeZK+jXmJfmak'
        b'j52/OtByGoOjas9N04+LXu25jBD6N+1Xqj1UXF1KJp1GQXjPuofAMI7nOfVifbV+u1NaMTo0Ahs4dkBC1RVVlSX6xsIzDvW56yudLdqt3Hzt2RC53D1aAc0mjQDt7vSz'
        b'K11oR6EDqH2pHdfu1R4MllF4oM1tZ1cf4Fbqu/UT2l0O7XivKnJJukRbqz3Qs7Q33ClpJxbrdzEz/u364br4NnCtfoDv75sARN332XK+Y0O66F9Y2P8rl8IBjCj4v+Ji'
        b'irKaA7Wy10t+Ft6CC1drJQ8F5//nFD0Oj+SGvwxnij0rPSND4IfOFfjcLIEfVGoVBk/JzvFYsidLgsBn86Obh65w83Y7pganCvwA+J+XL/AZVvhvz3UKfJok8FnWrl+P'
        b'A+8xNaAPinSz3PA/Ge8yUvJ4Z8CNdL2QYskdkMG7+6TwTpubd4v4Ps9jh98+vHsxXC8U+HzeXa08GJeuJbqr+f/TuYdLFy2PQLuGM2nku9pPdx46xF9n7jRzZmtR3EMA'
        b'kT3ryRH7ahtbG8df/3M+OADm2ITggdJtFcobk93TT4yN7D686rbSxZ83X7F3aUPsHfdv5DumjHVM92cMKxg2oObvPyqbscW/ZfqmbaLloycW/uqTCyff8EHZdZfePXDV'
        b'mFH9Tz72XuX+gSWuq2ov+cARnuL9dUb92pWD/3Zk7YXp11Wt2vLajEafI3lofzVUuO+jytu+2P7H56Xt3x48OLfm7anpD345a9c197/38ebf3/bhrXuHXzlrxsg977+S'
        b'nfnLPplVw7/Kuv7gCz84dlfa/b9+d9eu6Xm3PrXuxWDDZ1/99L47HvvH/S2jj70y+LlXt6rRzYd9P1yxduzEx795+iObJlwkl34+7bW0379x5RXK2KZXtl77WtGSGa+c'
        b'SKu5JbfpcPOjZb+Y0JR0NL2p6ujIptKjnU0tY49OvXzkG6GfvPHhwXE/b7325IOZ4360f1HN0ab3P/7sft+dgbVftm9xP7n3I2XEb/449Y69T6du3pZac0vnkUE29dC3'
        b'v//RzodKh/z2kfHvbH031bswL/j652u/0erV3XuOBpoWv/3+R8/89cmFT17wUO8q3+cbHqs8+uA7sc9Knlzi+/2fXnj9p0mfDH58fNXHTwxcOeK332yc8uF/vun9z7dH'
        b'Fu6NXf1VceBkS97xywaqdb89/N7RnMDvLvvk5JuvbX3gs/cmfFmw91TJqedr5r7c+taLk975wQwr/8hP+m8W1g2ts2XOv3Rq36RRv5jSu2/oF1P7ie6j6ydseHizuGHE'
        b'D/pvat2Qvudt9/tPPJ+xY+cfnK8/8YPSj1Pe/sdnN1pHqT898rd7nrut8M7Oy+6c//Ebk9Z+9fq9n2YVTgjlw4SqcAaMCbVBX1/CZpT2kH7Yc5k4QrtZX0+ZxqzSbjJJ'
        b'l6UDEogXoFz0g9rNLNrtvks7i/V1p8WP1Nb7WAy6u7Xt2rZi7cjg8SVW2Cxv5K8phdJR21nbAH8Hiyv13X1Ki9C5k76ZwsptqNTX27j+8yxp2q5pRB7lDtfudRWNmtaT'
        b'q3D9IY9+EznomqwdGldZpG/UNxRirmIrN9affJHYpB/rQ/4e5Su0G/W9qfr6YTP1jdDMmRjc4qC2lu3oN+dWVUIjjuo3DhU4wc9P1G9WKdCfdkdZRTH6Hp9j4ayThcVW'
        b'T47MQlhuApLjANFjQ0t5ztouaCe0u0foT2n72XukQx6rxAyFGGNeaLJrzwla2KYfZ7GFn9UeJ6Jv2jygcwSVn8S3Md+TT+iHtJ3aIQSqthrfacf4+dr68QRRe4q2KcEb'
        b'lnDtBU7t+Cjye6RHtFvnouvAPQDZw/BdJ1/u0aOsGydEGO71c9y+Mh4KXMfPmOwimmelYyZUFdE3ZutbC4tm6rchGIDGQsKqYJRlmlN7kmjH1F4XuapLi7QjYytLnUP1'
        b'ddpDGPEzV3tG0nZX6lspzyL9tuHkUgxgUlYBMAPqUtuqH+y1VLpA357BGnkLr2E0a/1x/c5Z2JSdfLm+cxSNgvZg8pRi6MXNM4dhwMKDfI2+u5ia36ivr9XXV+hr+uPY'
        b'Cdfzk7OqWUin3WU1lYQXZ2nbtP0Aayvn0m4U9HsA8DcQRbtykb5aWz9nTmmFflw7jGNZZeHSxonaIe2BBRTTUH9GX6sfrmRxWOdUUyHjpnuuE6d1BNn0eBxm/GpotZVr'
        b'1m7n53H6gdGj2Sjfqx3RnoHVsLlbdFX9Ee0OFssxPF/fx8Oc1+5njjqkJbz2LED8cbY+jnbokcrSwlnwoXWeoD0sZK3Q1lPJivbsFWw+V2i3FOAMcmk7Bf2gfiiLVieG'
        b'f9W3wJCiruzysjLDWWSatkbUb9APzGTU/BHtkfzKipKKUqN1AIq9Hn2dWK3dq7DxWKcf1Y6U649gLmi9hCEn72ujr68ZrG9h3aq6RjsOVHFhBVSg3yJqTw30MsitnQdZ'
        b'KrTDQwuHzSpByjgzWT8gajc0antZ5O2jsLCfSxtTWTyzAhZdLg9jtDHTAM14LaLv0h/T1+P6B35FupTXTnj0O0PkkymaPat4loVLv5iv5PSdldozVOMC7e4MmOM4ySIF'
        b'0NHobACMKuh7rPpm6tDF2v0W7dBSGH4KUCml8Npu7ZZ65vP16bHa3ZXA9Vw4kueUBpu+TbDq92sHWXs2Tktj7i71zZ64x0tx3GAWt1O/QbtTe5q8TVr0nV0OJwFh7p1M'
        b'TUvOgbEk18jm+ixP82j7xKna3cWMF9xWq98R9+2p36Tv7nJG+tTsa1h0z1v03TiZDB+gzwHz0+UHVNTvWKltCqHlfY7+nLYTkUupHhlWBKXBmt0G2GQ2AkY/tARaUao9'
        b'IHFV2iGbfuOkIsZoHmnU9ruQwWzFTytxVmnHCzL0PaJ+LzBvW6gf1qs6Ca2VzdTu0G6rAoTh0u8SYA3cru1ko75P34iVYzcrMrVHS8pw0R0T9GMdVxKsanNKivVNs/XN'
        b'lfoT+sMlhaU4jnki9G2ndhPr5jH92cASwDawLLGz0YqSWcPKZlZZuRLOou/SVusRihE/DKbIYWOr2jinEHgzbSNtVk9q27IKJNExg3nkfRQY2PWweOfALvJoBfkYcmmP'
        b'wHJJ1R5iiOKmwQUw8vqmYMXsFTjdADPPtgEYj0lXLPJQluWwMB+CBsEuEM2YOGcORqhJ1WG326/frj1HE2i8tn/KtHyCHe5SUikPY7Rbu536dL1+XzU2dVilFvF37WnY'
        b'3N6DJG2Nvi3I/NNtB5yxtbKiqqjKxlklYbG+174UmHwyvHy8soY86EJXtd3V6ODZpd8D06Nq3Hn47TVYx//z3M+/3SV+Hkyc2D64cC5BsPOn/zmB02GqLOjhTuIxj4e9'
        b'MU45DK6MafoJTuMOvhMw+pGd4g9kdCvTTeVhHjx2dJMls52OIt2CVWy/njvzb6SVZ1JupqeAWhtBX6it1evtYqrMo4LDfGL/8IaxEV8luvykd3G1BAxIgV5IUDEg+AJc'
        b'l3Ayvwz+ogsiC1BNLDoEfgX4FeBXhN8s+JXg9/LIgkYOfp2RBWjhF+2H+ZdhTj7MhxeYim2dHCq1NYstUjS5xdLJt1g7hRZbJx782WRHs73F0SnRvbPZ2eLqtNC9q9nd'
        b'ktRppXt3s6cludOGx4qhFCg9E35T4TcdftPgNw9+0+EXDY6t8Ntf5SLJ8Juskg+fqEtFl+Z8NAXyZcBvGvxmwq8HfrPgtwAVreHXpkrRAbIt2ksWo9lyUjRH9kR7y8nR'
        b'PnJKtK+c2mmX0zodcno0VxVlLpKDytzRgXJGtFDOjJbJWdE5cq9olZwdnSvnRGfIudEKuXe0SO4TLZH7RovlvOhQuV+0XM6PXiD3j14sD4hOlAdGJ8mDomPkgugoeXD0'
        b'QnlIdII8NDpZLoyOloui4+Xi6EVySXScXBodK5dFR8rDoiPk4dFKeUR0mHxBdJY8MjpPHhWdKV8YnS6Pjl4iXxQtlcdEL5XHRi+TL45WR5xruOggeVx0SqgX3KXK46Oz'
        b'5QnRqfLE6Hx5UnS4zEenqTZ4kx8RVLvqqEcoZYQ94V7hfuGqekmeLF8C4+dUnVE3KaJ0+Xf1hJPDGeEsyJkdzgnnhnuH8+Cb/uEh4bLwsPDw8CXh6eHy8MzwrHBleF54'
        b'fvhymA/95Snx8uwRT8QeKVwjRB1hFq6cleumklPCqeG0cKZRel8oe0C4IDw4XBguCpeELwiPDI8KXxgeHb4oPCY8NnxxeFx4fHhCeGJ4UnhyeEp4GtRcEZ4dngN1lslT'
        b'43VaoE4L1WmF+lhNWP7gcDF8MSNcUe+Sp8VzJ4VFcpOfBPnSwulGa/LDg6AlQ6AlU6GG6vDc+nR5uvlNpyviUV1Uw2D61gW1JBE8swFCfeDrgfT9UPi+OFwaHgHtLady'
        b'Lg1fVp8jl8drF6GtIpUkXefEcex0Rwoi7khRxK26IxVrhDWoPIBPSuhJCXtynVt1kVbaDOaPn5T1mRU5Yoie1czyOearGz1RNjmU3BD69eCW8aZutqFzdyqzIDi0ML+R'
        b'aXzW5i9pa2wONfoLBeUaxDoDE7ads/mg8tb7SQiGumR7LHEvHXgsrDxkmpgUSoDiGnyhegWNGuy+9jpShyFbcjzsDtTH3KY6EKkB8ehhpAVwItw50St1S6viCwYhJTYH'
        b'GtDiGFXFlKeh7JPY6ZOkz4HtOtmOlz14QZCQsnNA9gFmJScPqCIeE1sDrTEnlC776mvR7MBe72Unqsy1T5cTiDg2jlnrqZyYqy7grVUaKEAlRtb0Nq0M+JtXxR854ZGf'
        b'FRZzw30wVGv4yrRDqr65tiEYs8EdFeagG38wFKS3pNhONayoVboSqECLKfqObjz0VAmSKoM/QOU0wxDWLmEfKD7fCnQ+jgnUVKCEpa7ZV6vErBTxZERMXNLYQErh6GyG'
        b'xaeIOTGOMbtn6juPGYMcUmrrfBjt0OuF7Eu8bCBtcIeqBzHJq/jqYx6v3BisXdLs89bV1i1lOr8wMWTmAQ0p5FPC0MJuAelQKQBpJorRgaZ8awyH8uitCR2pdvLtWeTm'
        b'0UOOInnA+sD3Lu9Tw1xnNcSNds+w+vwuD0w4Of8a1x4jOsBpTtp4G1FNzGq28QV4E7EBjnPDssrBdqg8YB+hHs0g8mSKNUPGEWIkn9S3JFWKOJvsyuqIu9OiChFXk6DM'
        b'hHurfyilOOXqiNvFdVoiHFP3ijgjafDGA31390JYWCM2SPddI6jWSCbUKPgfVAVlGzzLi2TVo5+a21BtC+pJh3qOUO5s+LoPlua/AZ73i6RSvg8jqYBxbO35ZDuW3WmH'
        b'vLZIBuSVYJ8AaK9BI5UfAVwl2D94KtPaZN/CK2URK3zpaC+j0ntDTtOzjRNKMb5WHXDnxDuK0GOHchzzOAaHCE/l3AxfJ0eSXIYVmypGUuhtUjY62QUmT+ZUF75TBcC4'
        b'Sb04ZlxFLkIdzGV/XC2O4Apl3gvj4YzkQv0Cwke1ZKCBSTaDB7x/ltrcy4SIKnSbM+7/reOK/v8GMubvJYbGmY2zOVhNKNrDaFWiVlF3xyrYSasnDX2SikwDyE20cDbR'
        b's1Y+i8/lJdEjeIQUvg9+JzrhGawaIb5gUo0diBbMq4KxYDwwzIXGgslIXDDwVsSBi0iwSw3vtoRw4IrhG4nucPJbVCn4EQVwt0bwLwsGXEQNO9WmrFZtZCtjV6E2NnFg'
        b'yeSO5/xLI70jAyODYSHk1FtgGv9EdcD0ndvpjKBumhPKdanOSG9Ymr+GaZfs4nJwYxbh3oP3qpsWH5SkuoBETDamrwtzsHeqczy3/LYazu+PDIokRXrLfGQg/B8M//tF'
        b'htbzkVSsKdIPl1gGEJnwPDfCR1IiKUicNdpokVtwEsNySlXt0KMkmPDwq8LSiHiyuU5PJA1IAnzi6cXBskkiUsEFX5VQAK12KgHu66HXm/hOi/8jeGKNFEGZyWpyJJve'
        b'A2KA9iZH8imVb6QGUWqQkSqgVIGRyqNUnpHKNdtJqd6U6m2kBlJqoJEaTKnBRqoPpfoYqQGUGmCk+lKqr5HqT6n+RqpfHG6YyqFUDqbqk2GTKEUCX+U2IfpEJAB9jQyJ'
        b'JEGPU9SULULwAVWiqw2vNF964XyBMgD29eij2+hNLw6t+ACe6TjPoFSRnC9ICHlE4vS8WJXwuSqZcU7i+kCFqf8t67aw7N8Ad/zP46exiJ9Wd+En1C4U7IYHaqvoYWHM'
        b'JIFnf1YKFoOmwxmQM8Nqxi9Gz9UpEhoUo1ctt5AmOgFrefiz/aUJbjGFTxMxynGu6BaRp4/jNNPuinAacycJWAvY5YjdwGnWCJeA08SIhTZzIFYiDiD0AZcxXe1uXkZ6'
        b'pE/+BSEACIz3WU0LfAZGEQHRrUMOs0PoTCMiwaJAqkMANJzGOrGGVDOVwag2HklB35n0XFIpJ3QvKYLRP3AhJQNSSkI0jSlUQI84Nw/msVRXJA0XHQKKEJZoAZQacVwE'
        b'xN/4BNVzQG6AJgGZ49LD+xT4glSpMWAPfcudB/DS/2fn6nFrgrmUJKDNkWRz8n1EtLZhs8jZNYuciUBHJUQgHVGoAfMkDnTJAPpQAnomEF5isITeYDoL0+ScfhrMLDda'
        b'3NI75+ZcAhtaotuySf8fU90ADERbxAb7FpCksF/Uq2JwnUlO81i6BOQh7J/t5apFiWE4RsSWsDNZYBeBIey0rXKiWIHs5TIkLsQ1OZX/YK5oWFhJ+iYby8C9kBhtDzD9'
        b'6eGMcK96mxE2xt5VE5CNsEqgLbmRJHxmfs92NqAZHLCiqK3t41UL/MrxGhwo2KBvF8C38AzeOOLfxtsBZGhRTUIg7NPNZeJebuMxDJHvgC4DkCnyAvpowEg36A8yUIK0'
        b'p2FmH3dDJcaE0BJFQ07xJf57+8qIeRqD3sCSeu9KBRWmFcEWt2WRSKfaybgRYMGRHf+nAmzk/Dsh99eshoGSuWBS4OomNI+K5GmAxq2SRHb7qBiDlofIklkdHjHbhk/T'
        b'bB5DVJvGF2Yz+QJp9qKZSUwMrgoqD+Ozo3h5BC/HyAVBHTrHCSqPkup+R3PjEuUxum2pDS1VjpO5M9z4ajEKgvI4GaQ0ykoeFQq8d0ysXQJc+9LaIBpFx2yGd6eYLWje'
        b'NDQHlgDHX5j0rwFZYc2/gUz9/1/+mUMInJMbUawQw3kuCNLpBxAeSzYdGeDxwJkHFOxP6uHP3ePTf/7PavyPp61uMc0mibMvhBUo1i/Da75bEof3wbvxU3FdCnYrsYeC'
        b'QP2sRlMX9H8TS+ky50P5nddrrMiW2lZYliFFCfLMbpaM/9nZx0O07qa31/la0f+Rggd9eBJSV9sW9Hm9sQyvN9jWSnI/FJKhMQk8dXm7Esrr3X04JBiZjm8JyG3Nvol0'
        b'BIJ6o5IAFKEAhFBP5zHXc0nG8wEC+aU1tfP+F5WgvmE='
    ))))

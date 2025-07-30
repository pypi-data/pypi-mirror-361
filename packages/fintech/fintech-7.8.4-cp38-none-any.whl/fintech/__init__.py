
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
        b'eJzcvXdclEf+OD5P2QIsRUREFF07CywgWLFhB5YmYsPCLuwCq7jgFgsuiiIsXey9YCygoiBib5mJiamXSy65hJRLckkuXnL3Sa7lzssl35l5dpelGM19vt/fHz948bA7'
        b'z5T3zLz7vGfm96Dbjzv+i8V/phL80IIMoGUyGC17gtVxOl7HlLINTIYoF2SItZyW3w40Eq1IK8b/pUVeZolZWgpKGQYsBoZpPNC5rXY3bmBAhjsDiuRaic4900MrxU8Z'
        b'/exJn146923MYjAOaCUZ7svcl4ClwMAuwd8WALcchdvjQe7peTp56kZzXoFBPldvMOuy8+SFmuzVmlydu4J7JMFgPpKSB48fHUx4NuPSGw7/Sez/TZH4YQM5jBb3Z7u0'
        b'mKkApaCYLXK3MqUY4pPsAmBlSwEDNjObCQQAQ7BdwSVnuw6PGP9NwH99SYU8HaIFQCFP7gB/Ja/T8wkowMLzmxkfPJDqxC+ycsAfhLLfTm8CvUJHKxtLoGNtwMblcE4I'
        b'madCmNcdQkfFXSHkky0R+DPcHsAsUKJ9qD4dVYQtQhWoOmJ+XHpcCKpFNQpU2U+Jajgwe6EYXUJb0S79at+9vCkUFzz23Mdfq/+ozs/5Rv3wy7APtbtCNHGab9SvZfll'
        b'5+Xks5e3DZj4Ntg2XbKw0UPBmofiEkVWdw9cbSiqRDVJFmUIqoJnYGsEC4bANh5d8p9oHoJzodqx6CCshjvQDhWqgSXwdhKshTskwMuXG+w7zuiG8yi4DjZYYSSYKTxI'
        b'4mOfKTnGgiKdQZ4jIMW0Di+NyaQzmjOzLPp8s97AkgEg8wUGyBgvxihzFG3iOvgciyG7Q5KZabQYMjM7PDIzs/N1GoOlMDNTwbm0RB5NjNGLfPYgD1JJIKmYJIGvfFgx'
        b'wzLu9GkZjlNCUflEVVh4shKVi0JgZYpjYMmwhkWLUNPwFfkEhhkrHzKvicDET2KPen0Q8N2AIEAxBy2wsGYpKIydv2jVyg2yzXbM+WQ6ffsofvUkX6ZRBOTqTd4T1EKR'
        b'+1Iu8QEgn9SyKTmJQuLIZeL8xSAA4JyythVLAJ38WHgXnfGAjWEYnAq0Y0FkmjD/Y+DF4HBlMKqICIlPYsDyZdJE1AL3KxiLHJcKWwSveCQrQ7bAVpXSPRhP4yXYyINA'
        b'eIeHh1DpbAudxlITqifTGBECa9BxVEs+S4BHCot2xcCLlkEEvIBC50R3TvKSkMGpqFzBWfxwlmkMvKpSKhKSREC8gEXlwf4JAZbBpP4d8A7aqqKjCavR7fh4JQs84AEW'
        b'NaJtgygI4cuyUXUKqkpICkeVifA8xjG0A/jCUg6ViNAd3EIQqWgPPI7uquLD4pUUMUXAC1VxqB1uTc7KoDCofOLIa1FGH8DzDDwOS9Bt2gBGziPuAjonxaNaRTyPrg8H'
        b'vmg3B2+ORafxcJFeboYX0U1VVDTOoUJ1KfEiWCoG3kO5ybAqBmchuBMCLy8gOeKTaIYUeBEDcZEbM9gTZ6CjWQJ3ooseKyLj8FQVompUoyL99UNHOHTGMAh3ZSDOlQ3v'
        b'wROoOiwZ1cUNiQ8LF+MBaWNRG7wwnb5fAU+4haK6RDzgYQplgmjYQNB3MId2o/2zKarCs7iCXaoUZXwoaoRVeGgr48MSIsLjksQgDIjQQbckCi7cviyUwBAaPhwdjksK'
        b'Z4AHOsmiaz5mSwh5vccCd6qmw1Kah/QpNViFyb0O1WAcS1WKwSxejEoiUL1lBMl+CLagcpy3MiVxfnBcIqpLTkxZiPagUpI1LEY0pzCnCz9jXTnuEcrCbQxmlJyNt4ls'
        b'YpvEJrW52dxtHjaZzdPmZfO2+dj62HxtfW1+tn42f1t/W4BtgC3QNtA2yBZkG2wbYpPbhtqG2YbbRthG2kbZRtuCbQpbiC3UFmZT2sJtEbZI2xhblC3aNtY2zjY+Z4Kd'
        b'GYMKHjNjBjNj4GTGDGXGmB3bmXFOd2bsbWcXXZlxabJlJJnmOxLYRJlFN04xCpUKzALWp1P0j4UH4ElKXslKhRJWYNoJhY3AV83Bi0HxlgGUQlADppFqtAtexrjHAXYL'
        b'E4uqYbWlP367CVYNCoVNYXEiaEOXAQ+3M6g0bwN9N0EE20MVSlSFOUA8Jjx4jg0dhK7Tdxvm6MhUhYUz6Do6B/h4Bt6BlyZa/EmLdapVKkxq+N32BMC7MfC0ER6nKINa'
        b'4Q3YhHlLHIYkAFYDPo6Bbeg8KqclUzCyPBcKG2BbuIIFLLzKZBTCOksAQY9WeBFeVMFzYXDfiniMEeJ8NhjtLqLQBEyeqkJVuKc7mMxVgB/OwGa4A96idRbCPWgnqo6Z'
        b'i5GQwXXWMYnoaB4dmiWwxF1FugGPwpaUMAaIx7P90Wm0Vxi4PdAmCk3A2HoS7VGl4AGIZb3QVriVwoPKB82liI25zpVgJS67gR2TCe9Z+uGX6wvSVKgJHUB1wbgbBmYa'
        b'OgrP0Dcm1OiLB//QtIgEAswBZi46kUsZ0ES0E9oINDUKTNPoPDwHpPAei6cFEyMtax0/Cb/eC5uTwjD2W5npmOHWC8DszHeH5zEXv46qyDvYxqTjYd5HBweVjBujCkuG'
        b'bfMI6fFAHMi6j4RXKE9bgq4PRNVxGXGwGRcrZuZuQMKoofq16RjOrfBeSjgBtIqZB/fZWfrRCHQWsxdSW2h4POZByaJYdB30z+OjRqEmOnYD0d4VqlAiEhLwRHsrgJuY'
        b'hXvh1ZBs1oUICN53VXOwkmNjnGoOW4GVmmIOUxbrpCyOUha7mbNTVu6zqTlcsn5Z7POsaRpOSM9o/Fr9StZX6orcr/B//q2a2ENucdGMPkfu+cLSMI8lW6fsK6upkQXF'
        b'/iunPuaqV7la/IbspbfA24+8trwVr5CYifQLhTULBamFalMUqDaeCq6BI4H/SJ5bgS5QJQaWmdAZV9lmynWoMHiqdpoJsQ+IQKcoBYclYVSr7JSBQ+BOHrUUop0J8JqZ'
        b'SJBlG93n+ZKsKZhHwjqSxx3V48k2o3YKE7ItwQxbyJAYDithPaK5vDhuKLqJbpoJOixFuzaFKuOIJANSdIWNguVw+6aR5lEE3mZ0SkWB6RQPGJjtcB+pZmQIFkntsMmu'
        b'e3XThmgq1YU6+DUa02qqZVFlaLOUEX69GHfG2NeRV8F3cFqTuYMzGbONhB8afUgq21kl/kyQ1NjPUTMtvMVZcWkXLYvgnQcWyudQdRJGTjHmJbcAH4Z5gS/a+mT1OkrA'
        b'OzaH/QXKdQ9+7kDnHliX6RfImYbhhO9/2OT18tfq5ffffL7+wXvP1794pX5nn4deOZ/kMyB2oSjgEYP1Y8p3zsI2WKMKC/ZH9zCbVDGYD5xnN470MxOOPwjtyu9FW4J7'
        b'Uwajez7CwLK9z4rFrM/v1H23AKkPY/QHnbovV5C1qveJwJpugHMOSJEKUg3JBUrAYy/XWaDs6E5IQihVo5iJsArwRgYrFO3obpdJYOx/CxwQWQWrhUkWYB7ghL6zC16G'
        b'gsyCrByLKVtj1hcYakhRylBYSzB+jg1GzZhD0tFJwRAkJxONFmsbHLqdhym2TYQOoTJ48BngyPlZONwcQOjqXUAgulUW2s5hbVNoPF6EtgZiRbCUg3cWJT4ZBccTFGQI'
        b'EmIbj/8FaNiD+TGgN+Yn6prJwXaHONumbNfGO9t+FsbbgwRI2+69kcDnm6pZkwonvPP5l+c/e6T+Rv2V+o/ZslxpjlojmRqsefhlyOUsbaNOrW30/Up9UZOXc0HXqMlj'
        b'XzkcdQo8+DpgWMCwAX85MKzkNubD/uC9QM8LS08qGEoNsHlYgQk2xyVjK0WYadAHDEH1HGzRwXoFI7ARvjur6kYZosxsTb5AGjKBNPxZRsb4YJZVFGjK0+eYM3VGY4Ex'
        b'fEp+Ac5pmhZOCzi4GK8x5po6xKvXk/8uBNTDXmSNRNAbBztJiXD1fS6k9I2vKylNJB28hu6iEqyto4rEUKwMEnM5Aqtybbi7lSnJWFmAV9FuWC1Jm4Sa4W0Aq6a7oWvL'
        b'4vRvj1wsMilwDYOPS1bn5uXm5yZnJ2sSNas+bdR95VWsPqf5Chvt7jmfJHJAd0ncrFwkdOcZh8zDZVhceUo/H7FR7szq2dswGPs4+09y7nHp/5+79J+8HSTqizs/F6tg'
        b'Lv1nwUB4k4eNq2H9k4mqh1Pnv+TqbA+U5pPT9SVHfHgTMVvM/F6V5m48USbiNPyuGoV8fN8D2j+rpZSx5/5dfKRGreApsk5SLKPCORkrS2HKZIF394FXOFg3Cd0xY8UN'
        b'9PNDt6j8xWZ3cIIyHNal4KnfERoPm4OxPMf5l2RiFfS4NIdxM48m+HFjPbwpiPyu+QLRXnQPq3twGzqKblDHS/aSLFq3IiExC7UnJyVgG0tQI0YMFwWhg5GuGOAy154W'
        b'Q3aeRm/QaTN1G7JdyWSImBF+jUMdRRRYjuBcnWTQZMcoxjjMOe8k9zGXef9c5jrvRCuCtegiPBZKbeU4TNg1qiQ8+5jSl48Sg5FFohRs+Fd0mSvH5BMdx8HVqDH4v+Oo'
        b'POhNsEuT88kQJCZJpdq5QK7bsqbfDdP7y1fmju/zErYUqCiA5+DxsFBlPCbPdoDN5pPYwt3BYDnYEk89PYt1f/H+1hAxhE39hPlxyb15DYKH5tB0EPm+BEhBoWbLoryB'
        b'QqKXrm+giYvDn9TL31HOAfpz77ixJgP+Lqt+pNJoNY26Rt036kJNhbJR90dM3H9UG3JC0po0Gffr4ZX6PiEvSv08zmnYc7uadBc1FzT+kj+yb8mGqWPK3mfi+gf2+8tv'
        b'InUl/b4DDw6mLRkU0NLEvNLSEf2bqH5i5p0ocXThVUwGm4K+1P8as10i4OeZLSqHGwNrJ/VwD7zNFqQv6Z1tPJWZ8HkaUx7FK7mAV6OJtuhOfwXNUcbymCHTT4xxRCeu'
        b'CQy1k+X23j4jZKOoRwqfcUG9D7uwHII88AA6jI5gqwgrkcCzCPD9sAE7YtxTHLRMNwct+8tRjYyAWw9UkyVbfMmQD4CtaHcqcReCCBARgS5QxLjjJSIuPrlaYZH5L0oS'
        b'sEUbw1KcTZWtSQzaMBUYCXPu7dHBZOo/+lzDm6oIlq98Q/laqC+M9Cv71PSXvMPu1qWM6vnFwN109uTRGXuCRy0c1yds2PuKl9+8MXrhZ32/f+2nSXP6Tcq+Xz5wZS6X'
        b'cmlU+9++Lmv8vkT9QhDT9nHAgZrU9EUnJbPDiu68u0X/3m8q+hxe2Dop3/vWqs/f3vfRvbeqXrVuUbWrwiN3f1scq/784tKi4R/+jdu1evjFXVqFB+VXa4rm9rSwgD88'
        b'JsEmFrphN3o02NbfagpTKFDVeK/EEGW8xS4jQpaJ4L2QvoI3uQ7ACtQGr8NbybDZbM/hiUq4sVjdPkrZs4pbA6sL0eUeuvVgeAOVmYn7wj0b3goNRxWoMgw1oBPY6Id1'
        b'rBJVwHKBGe/CMrjGxZhbia51s+d2optDaVXDZsNzoQm4bHxi8kp0WoRNl1YWHV2EtpkJ8yjKH49t67AQRTjagZVYAAL0cL+cX7kEv6eW5SW4bbjA93E7hOVz6KTdHrw6'
        b'MpYaEvA4vMmoYCM8FBbsYkjwA8xEhddNSAlNVsbjgUuFN1kgk3JSeMm/i/n1MyaeuNCSla8XhMFYgWhjWGzg+WISFTN+DI+fLGB/4ln8/JHn8PM/PI+fP4hFYkzWMkLI'
        b'o5x19u+1uQFOqiU5b7hQ7cs9LD94PGBDaHASqsKmrxi2+mPbtoWFJX562kC22IXOCDlJHXQ2jCMav5UZAIrFFRKruAKUssUSq8SUXORl5U4Aq7iBKZYuBgY/HpiZ1e7G'
        b'iQwgv0uBwX8J1oqtUlLSKiZ1TAFahpQ1/tMqKlyiB8Uiq+gE2wBmgxX1y9lit2J30oLVrZQ1ZtG2ePzpjFV8gmugdZzgaV6/Yo8KDufzsLI5nNW9jmHA2jpDLC0hw9DJ'
        b'Ktys4lIGw+teISWfShlaSkpLSV1KvWCVGb+skAm5HTDi9L+tzapnDSNojR6lbD1jlFcwFWC1mHzCcIi0bAMj5K5nDD/QfIxZnMPSvAkVHva8CRUsqduZ8y2aU0xzFVaI'
        b'7Lnwpy65Lmi5ExItrxVtx3bkbFDK4BH21IpPSKyeJ6RaiVbawJIUqycue0rrZvX0B8WeNonNA6tznNYdl5NaOVKu2Av336uU0UpXkxbfsnppPfBseBmGOdN5nP6tVkZa'
        b'tHo1MP7kLa/1LPaysvWsMQbDy1B4WWOA1suKS/THjDqHxfm8DXIrY2VXc/hdpNabfLanS7U+VuHTMJfy6do+QnlnHtKat9Vb6zuB/PfEebZZvejTW9vX6mX1JPWRdwYv'
        b'qzd5U1hj9STfzcL8+uBe+OBe+OFesMY/W31I77T98JiyxrvCN1zmPfxJ6kx/V/hG0nEv+2j98Xeg7V/GDgDWPhR+H9x6QIUnaWGVu9XHAYOVq+eMfmbG6l3KbGMMUrOH'
        b'8MkuqgYkpz+W5GOr26Ac85gNk3eRhqxdIlITmnhscjFJrXAvZqzMKrCTXcsTw96uXHZIMzMNmjW6zEwF28GGR3Yw5u7WtfuUfL3JnF2wpnDaPx2iUIwbKRqUnafLXo2t'
        b'rE5DrDPrY05eYHzMhD0ikD12L8iRmzcW6uQjTT1AFTloX+4A1Z+s+VqJ0GZNfAUGu5Sxg53TCRxmjSFUZq77GcZoJFr8D8BuEBGo3cEj0vBjb418nSbfopNjyIJHmhRU'
        b'AD8OMOnWWnSGbJ1cb9atkY/Uk9ejR5pGP+5DE8hHZxJPn31dcjpKP3aTr7GYzPIsnfyxt05vztMZcc/xgODnI8Gb85gZ/ZgZ9thtpGlZeHj4CpxONNjHfcLkuQVmx1jF'
        b'4D+FrEOkN2h1GzrcFxGA5xAbDyfhVk0dfHZB4cYOfrVuI7Z4ccsFWl2HW9ZGs05jNGrwi1UFekOH2GgqzNebO3ijrtBoJEZoh1s6boDWpPDtcMsuMJiJQWHs4HBNHTxB'
        b'iA4xHR5Th4jAYuqQmixZwicRfUES9GZNVr6ug9F3cPhVh9gkZGBWd0j1pkyzpRC/5M0ms7GDX0ee3BpTLi5OwOgQrbUUmHUKz1510V/ywOpkihNXpQ6UfJ3MeTlFMaK6'
        b'8gyRhl6MmCNKK49/pYyPXaGVMX6sO/3uS9NxftYffw7EKf6Mj9gPfxbjVH/qMPVifFgiTWU4FX9jiez0YgVV2Jf1om7VAMbvJ9ziTyzrh0th+coKqy0VqGYSMaCSUF1y'
        b'WAJWZlB7TCY3ycp0ccNLgRC+QGniM/zAkou1ghOASqM3sOTiinkrZwpcKzNjdZb86bGkO8IR+WZlrdwUTDvGVCwLmdVi/B9LjwHgBIs5JjcANGA5hOUSj6UBT+SHSWvl'
        b'cxlcH4/rTsUyjCOyBcvBQ5gCiZQQaUl9Ii2P6+DIN/wfy0VSz9o8Qd4Yz2j5wkYtkdMiq4S2Jba/Fwmt03rYKYB+5+3f+SlgrczKUi+jKBkTcTKZRjqXqeSR7PxE0hQi'
        b'40wyw5xJZ+7gNFpth9hSqNWYdcbZ5K20Q0KQb42msEOq1eVoLPlmjLMkSavPNhuTHBV2SHUbCnXZZp3WOJ+kJZLC4qegmYvHk8QsaDMd9Q7GvMw0imIZj7GFYJmPgAkE'
        b'16jRJGMCWB/Gh2IXXVidFIhuCQvk8bAygqz1JdHFuQlwPwiF10Ro3xpLDzuENE70UNpYj2VVQBZWczwcxo6VccSbdLeRnGqWFj8qyEQzlVjorwKFPhjJcEHjWIwYnjiF'
        b'IaK0lPHARg8VVhglsAhkKrgKD/K5kgTA8BgQ0rw7BkeWI3U6K92sLEGh3jw4BK/JkFJf55cECN5KNAdQdBI3zJHPVHtKxRjP4sYwaKXMaoDBwp+sGJBizuBPwRNj3J5L'
        b'PuEUnuCalaNp/hVEs8FUkIO/E4ynmpe/ldQaU8xZaZ04X3mFGOMphzUb3iAjn3E6/WbljflE5mD6wXVYeVo+H2uc4Vjj5M2iHBZrne8xWJtkQJEMD5OIyGUaGYXTNosc'
        b'kVGYNvCw1TF27zVGMmL1dkjWaYzUQcnlYkTGvNS4er1xBkGwBAEVO32SRH4LmKulmK/DzFv6zLyxE2llmZQrFuKG15hmOFEWoyeLUdMLoyhmfyxhff6UWcpYGUZlf2w2'
        b'BDJFkZrsbF2h2dQp47W67AKjxtzV/9rZAJbLWaRp0g9M1DQkhyasIgke/y2X5zokZNgw7QpVZju75+YEaCLjWIriBKY/GLPewAFFgU/ug0OV0JDq8sln9/9KBGmc4Ejs'
        b'jY1j7LoS4OTD6TrMCmw621SJycnKYIV/kBh4hLPoVBA82cPHKbX/Ny3CDx3IwFpfBktpXuxwaWRwe6SCkwOToFuOiEb5SUuZDN6ZTviDBPMFIfKPvBPZAA8yxFSDlHT0'
        b'sUfpzdXn6xILNFqd8cmrwdSBx+IqMfNxWZbgnros0SMwz8GKeoS9kYU/WV9YaoLNwXFJ4fFT4dmk+cS2T0mMV6ahipQFwYRZLiThJ3AbanRbSjx6elvxfhFdRq4Levlr'
        b'9TfqP6rzckL2BdOot4dC1FvWN+o3sjLuf/j8ngdX6nfuZBrLJx0bWTb0g4IDW6ODQPQlj9wHv1eIqI/Dn4MlqA3VKEmQ1Vol3JYruCYCLTwsR02wjq78pi8I67Hmh26G'
        b'+3KDPUPNBO8H5AxxXfcl7+FzaRw3FB6D7YIzoB5eTHdd952FSuB2tNXdTMTZMrRnM6xe74zUobFF8aidDga8EqaEVaT5CFSViHGqhkTkVaIdmFsDnOegJ2oohAftyyFP'
        b'4Q1Y/dcb9ObMTFc/8haQR1QbL6YosAeOhDsKOJdbTLr8nA5xPn37M8stmMjWks+FjraNBfiRS6iEeABACf497Or9+7nGn4ypMQKmchj5iaAU54id2Mo/FVt7BGn2voAn'
        b'SaYhIv7w3gwVqh4Kz9qnCdVzeKLPcT5RaLslGudIw0hzlSyB0uDNzsArjNa18Ay6LfjR2tMAWB4sQXvgaXSGRgCmoSvwiFAuOBgjYJwSVcGm9OCEJLQjLDweI89NZUIS'
        b'AwzeblPRwQkW6rmZi+4tUC6KQzWKhKTEHHgFF7CTD845Fu4Tj0A3luqvzP4VbyKS5dfjX/ta/XJWo65Rs+T+ARhsvV7fuuTMdkVZU/mMIw0HWytbS5uWcA9zxa2rA2KW'
        b'tL1flV9i3RcoHtNidTNJZklM0W+z+7z2ldU8LzuiB9899P3qegcmIuI5KoqCNaia0sadGBHgBzPwZAwqEzx/leguaiK+tOFoq4s7Tc6vhBfhc2ayKGGFVehgNnzOhRBd'
        b'qBC/3ElJaBOyoapQdB5WhSvjlCwQw1NsJDqBbJSS+7kFqMITksLiYa3DYxmBtmFiGzlPlIGJ/JZjae3ZlT/PbKMOK5yZawq0lnwdJRg/B8GspV40lrc7xYuG9MTdLqUd'
        b'1EmoAZMQEWudpCN6sqRhBfoxOYnIiB+GLkS0x9+ViJ4GSA9Kcrq8Yx2U5FA0CT1Jc9z+N/REGnDa+0568kqm0XPr0W60DxPULFTVnaCyYImFrCDCS8XpT6Cn8bCpGzmh'
        b'5yQWJSm0LRiWd6Em2BzThaCcxLRi3M8HI9jdL/ZgBAXTweR0d5dIp+Rr1mRpNdPKcEkj4UsWUjym72RT7/xciXapYDO2Ao4sgHVO7zra22VRmYvyNcHdab6oGcALqLwP'
        b'LNEU0hXZNHg+nMgaIhKJLEDVYXaJk8aNQef9u/RHBFxCDSinFLR4lsywk1NyVK7zeGY558zydGa5zfyT5DppxmleuHLKSYTqG9DpIhVZPgwX4gIWxIWSAMGFmLqVClSX'
        b'GL+QTGFKuJh0XQTgCZ075hNH9XT95G99ebqo8snQ7PyZ6yKFIGlfPIHXu1QpBElnYN5T4Qj4wLO6ZotbQAw8QNULeC8d3VbBa2i3iqxhxifND0aViwUmOZ8CQJpfiNEH'
        b'tUrQJXRqpv7lN1SsaTUuW7Ul97zxEY1Tezkn3FehSdTkU9UizPhH9etZr2S9kRWv2aV9mNWs+yr2s3ciwcLJzMLo0nRb9OeKlsg9LTpTv9ORUSXyz/1Ty0+XzjnCjBj4'
        b'cv1LfsxvPnr+zec/fCngtfvvs+CdhwEvP79SIaFsEJ30wjPZdcUl2L7oQlZcKpdRRoeaYpa4qiw1S12Z5XOwhOZaBMtgZXeGqEOH7AwxawFVbCQDJ8PqrCS6fJ1iX+Dx'
        b'RJe5ANQ8XVjn2MnAMhUJY0uBhxR0jTtcIQa+mzlUswUdoJVMgbenC1lIJX1gjQh4TGCxwVuPGukSEdyKDq2gYSLwlMIlUoTGicBj/C/nzF4k/iOz0FhgpqY9Zc2BDta8'
        b'Bfiy1NGDTXTWl7hrsCleNK4nX9Rt0GXbuWKnpdC1ZoHsRYIJ0mmpPW3F074w6uUsQFn3OvzYwTikSAn9/asr87Ysw+mbVfKnMI4ncw0S875rEmoVBaOWOehGLGwfCZsU'
        b'YBja67dKDp/Lp2EwUwfwf/MFsd/23cgcHvV4DD8zgKEL4khxgKlP1nmDWHXUh8ZE+QJAk/dL/uL9pp9SWCcPeDDlTaB/oW8DZzqJ35XWlY2sueMJI33K/uf95PzRe+LG'
        b'yu4HfHMfNEwc8LJ5hO7DT+KmBebEjX/Q551/v/39C3Mf17/p/mL5d1MUi2aOfmXDrI7v0to+njrQ4O87+auXpS/o2sdnTTixbr0y/KqlbUut4dvbq7+/cum++bmTqgWN'
        b'19XvXV62/Fz6N31DPvjV2OGxNf+sidh1yOutnLlft0z3XT864eafEzqWmracPnGZ/dOOH7/jdgwNPZO6S+FJUVAC92F1i7DNM7Ch+/ricnScrkAuxdRTTVSVALSzm6py'
        b'FN6l9WSiM4McxAevW7pqKgp0x0z25FjQdnRVsAcc8wgr8JRVihQpiQKzHq8Vr4C74R6qP2GKr0wNhZfhVhfFhs8SYkqfCx9ln/QUaHPOuwgMHMfDam2heQ6p4Araii49'
        b'0YB4svXgr7bbD6PQUTNxVuFBqocn7EyoMg1ddhSXgH5oK4euoGZ/Olax6BxqpgPajG6SvQlCJIvXQi64HzxEl1jhflQxSNhQsCqB7JOQwtPsBnQRtVKbKXEdDeCdAG+7'
        b'mk3EZroCWyjzWRaC7pIsIljfU9JVjTbTXSHwlBxVJzJgAmpgJgJU54Z5TO9E6fZLbXyxk994uLAKymyCHcxms1MPZN2JR5A4VPAnnvX1FuOnD+vDFAX9LOvpohmK7Wmd'
        b'DEbyLLCyxg2gi6m1Hj82ddESbYNctcSfBwk3SlcN3DPtCZmZHbLMzLUWTb6wdkRNOaqK0pY6PMk+LY3JlK3DzNNuKf4XfpUmpsPNXhOuhXaExNjoSEfIeynrI2EZfxnm'
        b'lKF07i/lPYlVslgLhNtj4B0xPAgrY3q4JBwL0iaypuRwueg4raAdARoIymq57W7ExULdKCKqCYqcbpRUjRkPnwEPXXI2361mp3U6BT/s+rTdjZsjsWtdfIUEa10irHXx'
        b'Tq1LRLUunjgVn2yf9tSnRYI+jc3JcnRc5RwRLF9nDBL0aXTPT8FaqPpwE7bLVVvmueTCwhtV8iBwNh+Xgc4K+7rq0KVUlf8Sl1yhIXFiEGjiF07P13/0wUyRKR7nW/yf'
        b'W19/+Jl66f16iM3Jh+e2t5a2lt44qGcWSFSS1ZIPZn6ZUR5YPqzNa5/fmfx1cs/PdWMmRL8b+UL0byP56FNgTG4gmPhbn9R/MfYYPdSCdq3pFnkBj8A2zIPRzWVmEomu'
        b'RvthTWhUuguvFM2gQRuBk7CAzPWk+7JgpbBhylfHwQuFgVRR0WGV7xaqhm1wtwNJKEuCW7FuY9dBnoXcXCORczAGZBJzjrIFXwdb2ALC3GV+DM9JWWwcDuyBMuHOcgKx'
        b'iDu47HxThzTHkk9JrIMvxHk7xGaNMVdnfqq+wRtLyOet5LGNPEqdnGALpauuSsf7Aa684OegU7DJxJNNuIFxI3kUUXZISXSNzpxXoKUNGDc5hqXn2qzVCcpm/Djr8JJK'
        b'WUzFpF50Fe2ApzvpWNp1c13RhMlyMTyLdgygtkGqGwt47Ru4BnVYhMEIeqycdCW9LmsnTtIDNBLxF24ZcyxldCW9AcL+3cFoR5EJKwZXPNZasOyvQNewlFuH2j1y4IV1'
        b'sNa7UIZaAZiKzohQCzbgLNNJx/ejC9jowfpbYjKqDU1eSA3cePyvMkXp2AIMT0RgCVsRFg5b06gn9Aq86Y7uwQMhT92xzNF4jf9l+G2vzGaIMG0X0dVQ2JjonDkgRtdB'
        b'33QOVW+SW4hFU+iHrYBqR//Q3lDYFMyAQLgTnoUneSO8laEfPkHMm8iax/Mrs75Wv/KHP4p/UGfcb6lv2N1U2vSwqXRM9Vqmvr2+z0NJ68HJB9ICFhzwjyr9fHLA5fer'
        b'v4kJ8G8pSY+MMkeKok9hfkLiJN/a4Hsx1k0hojFW8Mw0DbZX6KYsMbzAYqUlestUqjcELxsZShANrIa3AD+BgRcVqVQtGYJuD6G+A1SlzEBXaR7gDbdyqyagXZTNLESl'
        b'eNqq6Ya3Gg6dgucBP4mBrXCXjEZnzneDx1X2kC90OVWI+vKCbU/dt+OhKSzUYcIjpN/V27QFzCdLNEJMvDtTFIKZQma+PltnMOkyc4wFazJz9K5GjEtFjlYpW/gZby0j'
        b'5KCEWoYfv+rGM9q6hHylEQy4EATPqVKURJl0zDG2NUvQlRRq7MPaFEEkd7dR7IODWbQwulp4zGcN2T0n7F650XdpKBna6PEsEKFjzDwzvJKADlCsG4yVym2YZFrXr0NX'
        b'1sqkhWtla2MieOA/mcvth27Q2OU8WGsyYU211c1znae7F2xfJ0WX1xPiXCsCI3z5YtiKcxKBgK1PG7rrCRtUWODQ2cST1cLCcrRvuIXwD3QatebC82g3pufKxJCEMHgO'
        b'7VkfFkxcCImO3S0LpFPQWfs+bQbAU7DNYxbcvpg6QjAnKJv6tOL2suNgFS6+L98dleXI6YaapQZ4A1YXroU71mNyu0YYTH2iGevm17CcvGbBvVnAw62GEEpsWEs/g0oo'
        b'sPuHoXYi1LGdU50oAd5oJ5cGT6ykdcJDqJntWukYbLeQb60ydzEYEc/DKtTuSbVfukkR1Y/Dpkob2xedAWAymIyqYD0dPrTLtBbtTglG9cp4tA9eiouXANlUFh0zwv3U'
        b'ERebVuChJPsUVYuFLjvY3ICxZDW8nXK0FWirBN6eo6NhtvB0Mbq3QAy3ogoARoARwwZTrq9ipYCg7btqddi1TawQZvv7YDGQASDvH6JO7JMyB2vBNPl3uRxxO+b9x0Md'
        b'dlKVIuRlwmnegOoIddijdd6AeuuXLMMsDBtzocQ7VEk9Qi4wBsKaTiALYIm0eDC8qb9wUc+aJmDakNXUJtVPTebG+JT9bsOWXUn7vh1SqXpzaEPwyJMnOPfgEwP7KHYu'
        b'euWt1NfGu6UlznnB7Zvy7EJQdz8+Lerj/JNj/7Gp6HdTNk6BkvyY8uGjUvrxX7QX/X7YjG/b60o3B3W8NzL/y3K+2LL9ZPanaU1/h2EtcZnD6iZuLlisXfZ7/9F9F7yx'
        b'/dA/fvP28pebC5qL5/8mf9n7/xMTffH198u/SH79w/yzNycrt77227vx31//Q+2rG373dr9jpo/K+aHHf9T/dkbq8PQXZ7597aOPXtn753c/Ra8bxruZjt8J2fXQMvXc'
        b'P5n+1x8EDR7a+mpx3sRLvvEfHjtTFNE0qPHr73aOfidFdcjrha9+GtEQcf1x2NnQgZUH+w5JqTFmZv3zc1n4X6WrKj67/HLK6KYvpy/LOPvq7958mBe4YueyzzZv+OuR'
        b'nBFfDn7/qyGPMteVzR2m8KY8ND8YNqvQfk9yDkV1GOEWHPBAlzl29lgzETcYkesZwlvK5jKAXcfMkE6iHN0N3okU+DZm2lNRO+bbAeg2rRIjcyU8qhqMjiaGhAtZPPJZ'
        b'dAo1LqDv4TV0a8JQjP5kZz7hS2QdrpotRkfWC3uZSjEH2BYKd+akEICI/iHBMN1lMbW1r6aG+gJY6+Y+QNUlnBdV+VHlEt7CuuW5UFQxZHJ8WDyVHyLgPYXLGQuvCish'
        b'mKrgBRVZ7cRVK5TJWLnBZvu1/ol8rAXdo6ID7vKKtwc4C8HN8EKsEt3pI7zcHYTuUbhQtQTwypVDyT7rWynCgN1bFhiakIQNYX6oTM7Ao6lZZnqYQJMc7XbETFcSjqMi'
        b'WsRFeLQ/vMrHEYZBKw/DnHuPq6wcDKujx8OTtG9F0ehGV6U8VkrcIug0Vpyf4rV7NgPW1dju16twowIxrVMgziPikKeBzD6sO+vjjv9YX4Y83TkfnBbgjHKQ0UAuX7qD'
        b'gYR8eeF0L9aXBoj5sDLWWO6Qw03sL7S8XSIPSSUPugnNO66KNlUU0Y55I3rITBd5mWimmLnSLIV74ZktCo5uB+fDNwkLbKI+nLC+hs2YeuHgjDPItgFVJ8PmROJ+nYua'
        b'SSx7O4vnpnwe3VCRio7ODFUSnL+kDBHjyT3BRqMjxmyum5rn71D1MvCjxzEOwHmQA9PlKAfW1i/H37mQIPrZhQSOLiTwn47Ak+kud/lJ0+XqTWad0SQ35+m6nyYU7t4l'
        b'b7xZrjfJjbq1Fr1Rp5WbC+TEZYsL4lRyegzZmSovICGdWbqcAqNOrjFslJssWYIno0tV2RoDCdnUryksMJp12nD5Yj02aSxmOY0V1WvldiykUDnqxi/MGzEIXWoy6kxm'
        b'o554jLtBG0ODZOTEpouRkxOTyCcSOkqqtFePe9hLkdW6jSS8Uyhl/9KtoFa+Do8ZhqnXCiwm/FIo7sw/Z2b8rAX0jVyvNcmD03X6fIMub43OqIyfbVJ0rcc+2o7IVo2c'
        b'9NGQS8JaNXIS+EvAcdQVLk8uwANXWIjbIlGiPWrS59BSwoDiucrSEIDwXOG5MWUb9YXmHh3p4frwAt2tEY9kC4lVWRe9eUEEWdxDJ9EBssCXtjgOq5sL4hJEaZMmwSaF'
        b'O7qxcRLcGztsUj9AFiZkA4LgqR4k4OOoP7krCQA7ETBOImBt3jk+v2D9rIcnhzCOnieQKJNxPspUegbz9Qx5sDuWnAt5/5WVR5rpucNOZN9+TdiyftoqjjORYA63P/UN'
        b'qhnjvj3Wb9buX0cUbb+z7cGx+28NfM9t3cmyltzvTlzNSOpb0DDB8ocJ8Ru+HfbBqzuD9rw6bO+OxEnDje6q1neyPtv/H/f3fygQDd350B99b/6f+5I/lz883VEEhxz9'
        b'3QbruCUD339dsv3y395sOLTyiDjo79+NUrBUOqEmeAwdClUGx0UVUafPIVaJbmPpRN3ntfBQcSiqiwiZj3Zg+WdhsJi7Ne6XryqJMtcbNYVU0AzuFDRbwEgSPxxAubgP'
        b'48eI6S6bIoXRzrRcwuLs6O2SQmq0b/AXAlA75ctTAGtihAJUuGCRC4ZhyEz+ncKlBHzSZfGIBEXNN8K2UEfUyEF4VNnLXuVOyTPHVxGRgOX9XNjorR+Mjj8lHoyj7pT/'
        b'5TZ1EejNqSBJtpCFDE3MmujIsVHjx4yLhtdgi9lsXIeJ9dRai4maPFfQZazltaJ21OYtlbl7uXl6wB2wAtaw2OxC19xQMzwBz1GFf9rKBLK1WRo5bntsxeZIwQqAq+JB'
        b'PQCRkQvfmDUxJsWO3YfmZ4lMy/GnP5zo2++lob4lkTL+/q2x4mrm7rbY77iw62+kn4gdfe7Mr/K2JMyfPPBRXOG+1FORr9atnvrgwayt8XvCPvp28vPvjC1f9rvm0L9u'
        b'WRSQ2H+s768C2t96b4M6bsj1M49/65fTl8eITM91OZ+wXBUmU7pqkOwyulwyHjaucnoVAD8JXYbXGNgaAU//XHzI0+O9jAXmzCxiS+PxDnBF62iC1r4YoaU0GL4o7JkQ'
        b'2l6dY9XCGVT985FgNEcnOpOTIyJ7oPNbXfaCkujvHHR0sQOdXVA5DZX1js2oKgJWpkSN58A6WO0Tjm4K854+nm7ILBwL1IlzvPyBhWrMl1CFEe0WoVMYHcNBeBpqoJmn'
        b'bJYQU3HJrQh1/vg+W4QaovR0n+eGj1PUsru+BQLm0Dcnh1HTNLgtW53/t7kiIXHsYhXBPnWWjzpkuUklJE7x6QPkODG8WJ340pAEYZcyqoE1GQsQVr4Xop3rxkWiKh6I'
        b'0xh4oe9cWkg5JRCMBWDiwr7qQf9enivU9C9rK1PCgdhDzCfrDyQslggnNG2HF9DNBUSPX6jog2pFgFMz05LcLeSQrpHYmN3V6YpbGIfNEFQRlkD8jMQkodEQaEco1u25'
        b'YQBWhrorYB2qpQvA7UskAFsBcjD3QvE3AYe2eAG6+bpAN0qq7e8TxagTVcZs5YTC1DfG5/j+naODa94Cz6A2ZinEo5AEkuA+uJtCPtw7BpgxWSb4q9P+s3ys0J0z06aB'
        b'7Xh60lNLjEs8Z4YLx+dppwMrttgnTVcbp6QXCDmPeoUxahYEfCwvMb2nSCqiiXV9fstc4UDAVZ+tBQeix6bRxK/0c5k9LJjY6r11dUBhPU8TZ5v7MRjtJg6RlBQHpBt0'
        b'NHHbajP4Fs/3dx4l6w70WeJBE0+sXMg0siDvYpDG40yQWWjdL7qeCeaAeuWqktwD3P7RNHFv5lJwHffoTxElRQGeaTKa6KkcxiSyQP3v4pLiJUnz+tDEQO0QQII9W1JL'
        b'rO8lTRhGE3OXJjEnWBBZG16yOmDZ+IE0cUy0PxOG4bw9XF1sW7hBaP3e+jeZExxY4qbWFPgzGiFxzJgXQAUDAg7OUrtdGrNQSHw0zQrIzi39SvX4ptgldt6X9hG4zoDU'
        b'iOXqpdHT7Yi0aZEnOYwwti1NHTYm1Y68HW5rQQkDfO55fJLll3lmgP7w7tucqYH4PGbdXzj/ZcNvYn2aV675lXYK8vUe/A9l2CtDh9Rn/6j2Yvhro00tY32zkxv/ra2f'
        b'3P/zvvO0P3kf323as0oydOirC/9+LPPeuVW2C0tFqODjC/Krv5mfe+vU4fWSj05erk/93YIhSz9Shoo80ZK/ffZBxLyhqx/M8Y96b1d41IuTfn+k7dP8bZU/xMa96ObJ'
        b'Pgq+XfNO3Mq1+4a7GT+b+/KYw1kZbx3KGPD+Apiv/uLzE0cLdx4t3fxwV7+JeSP/PefYuCU/vBR6tt4Q/OK2Ed//Nabl4rt38hZd6D/uQYj0vYyP0wd5LLm0bsjOv974'
        b'orwlY55NN+Phu+kvbyseNPmb72d4FZ16/hP//9EeMY66+c307eaW61PdP371hz9dPXw3bUq/j1BY3rF9uS8Efbhm77UZn/qI3r1u8x344UvclBeGT3mx75QH0VP+8PrK'
        b'iZX7rW/Pm/J66NnvbobM+nHZjyOOv7Dx0PRPXn5Dv/7Uo9Vpv7r+29Mn/tny/cl+0z79obytOGXyv+rgoIJla+ceNx4Xf7Gr8asH+0NzV6SdXzn+pQVzfvrLwZCPXv2P'
        b'W56q766aN/6Z+a1y4SrVzl9Ny+RSV+04oPxYIaVSJsQnTTD5i1eHOTZJX9EImtRFuB9zgEh4HVVEkKPKGphUbIzeEYKUb6yE10MTlKrp8KAyJFkEZGIW3YG7CwQHyx54'
        b'FDXZRdRFuEsQU1hExefTVmdPg42YgaTEz4Ol8AJPTogbFjtYCAXYO8E7NFyRIJzSKJqB2oE3KuEK+iymNY8Ygg6GEq+L25AufhfYOFqIjGqFV+Dl7gfNoPpitJ2DLegC'
        b'FpG/cHHf55cvTj+zGil1SE0qcq2uIneojOFZfy8fd55xPZSL/B+M/wfgX19mBCNmB2Et04vuVyOLiL6MP9nN3f23M+1HlmV/FHNiKsildIuHDNfIk7WCwCeLdUExFdE9'
        b'Jx0Su43ZIaKGo4s8/9/v2cPK7w7ymW5uqXeqAbX4EdRDDfgixFUNmEzQ5wxshyftisBwdD3+59VaEYA2iLXB257ojODzvgDL8ugylWoWvORw9jpcJiIQAa+I0IU4uXCc'
        b'6Ol0dLpzVW7cKBpg6oPKuMHwDrxNWSQ/CysUy0sZsgrZtGam/diHSKwjzPbjyOnC07ymC4lFo4k2EUOOhg2bmicH+lEVkxjTcfwmOPeNoJqpXjBSNvdPo/RvX/lignTt'
        b'6PGLToUven/ZXLU8bp2BWfzJ9gNeKZenT9/i++I/3Le7HQ8ODX+v5YtdoRdvfLqv/+3PPQs2TjCn12/81/b19YaYqsUnP/M9kvTny7/67kz/73x3v/wp43tmRsk3H354'
        b'd+eRCyNTD3+ysWT7pn/Kz03d/CDUFPJe/8c77vza65vmsYcWb1k24Wzb8aO7PuH//oXkz2zEiptjFBLh0BrY4N/luGB4s4BGPAmnBQ8aLvhWT8JmzBzwCKOz/ezuSeKc'
        b'PAmPUC9kNjwCG1yniMQkJs6JJ4uBx/gCeApesYcbouZpLvky4c7kJBHwDeFgI7ybRhfoUCm67Eby4PmDRxbZp9ALXuRmr+gnQLNjMGktQpmMLYVqJapKVIiB9yAuc2og'
        b'PfJvAtwG78HqFLsOZF+HwVjUyIGBcCcPn0NVhQ7z0f//Oqd4Zj7iIFzKR0Jc+cggEm/EMqPmyiils2QfKyts5hJTzmHchXPbTfg60o2+/6/h3umkatK0pAdV/3u8K1WT'
        b'aQpCZ2GNU7tngTc8j/aO53JQbXavy9DkxyRjOsN1tEwGp2UzeC2XIdLyGWL8J8F/0lyQ4Yb/u+/h9vBaUa1wshtZ/+e1Yq2E7ozy0Mm0Uq3bdqB113rUshme+LuMfvek'
        b'373wdy/63Zt+98bffej3PvS7D66RekZxnb7avtulGX2crTHO1vy0/WhrvvidlPxq/WvJSW/ksMP+2gD6rm8v7wZoA+k7P/v3gdpBuIV+9m9B2sH4m7+WpwFJQzq8EgVu'
        b'nqQxaHJ1xk8l3b2rxAPYNY+cBnB0yfS0EnoTcfVRf6t2o0GzRk+8rhvlGq2W+AONujUF63Qu7sWuleNCOBPx5dvdl4Lv0OmWpCXC5an5Oo1JJzcUmInLVWOmmS0mcqJ8'
        b'F0+iiWSR6wzEz6iVZ22U23cAh9udw5pss36dxkwqLiwwUF+xjrRoyN/Y1cG40CT4nHFTGqOLm5Q6k9drNtLUdTqjPkePU0knzTrcaVynTpOd9wQPsH0U7K2G08E0GzUG'
        b'U46OOKy1GrOGAJmvX6M3CwOKu9m1g4acAuMaesaifH2ePjuvu8fbYtDjyjEkeq3OYNbnbLSPFBbyXSp6HJRnNheaYiIiNIX68FUFBQa9KVyri7Afzf54lON1Dp7MLE32'
        b'6p55wrNz9cnk3IhCjDHrC4zaJzuJyIF5dNMg3YqVI3rGbYP2VYHHZT2dzwa9Wa/J1xfp8Jz2QEiDyawxZHdfHiA/dge4A2LBB46/6HMNePxmpMY7X/V0eD/DsaLiZEs4'
        b'EUTHBoIn7tnCOnVL5zYTVDedhiZkjB6PqkXkYDjHmnNwXFh4ONpBjiMeD/eLN8Fmlf3AcqsmgpzijEotKUqy5aE2hQG+8AiHtvot1/+rdCJrInvlO9LWkV1dwZ89ws8w'
        b'/0fqOPs2hfBFwZoEDds2oH/k+sgI7fL7l+sbdt8oVVS3l94oHVOtLCv48cb+ptKRx6aWDT2wtU0Etm3qc+sDG7YgiMa9aBnuTHd5zYBpqIkK7PWwkspiMzqFztllceL8'
        b'VS6ieCY6RXOkwx3orAfurEK4a2D+WKw79IM2XhoN6wSjYwdWE2pCUV0cPGoZywMO3WIMaA/aRd+OYklEY2UiHgMGSHNmw3oWboU74QkaCwhrM2ahapVSAti04bCOIac+'
        b'NwoWx1kzrCaVjo0axwFJMLpVxKBDsAKdpyqC96IADPZBcmQ1qkhKFAOs/zHoBtwDTzpC/p9hyY9EwVLh7O8qnLcAPxndfUAU8aL+XdHWuaNREM5NQtyvcT8AT91V0MQK'
        b'2bpuqKxiHX69EufvP/1c4/ueBMGTdz4RxdUKVjkOYlWQsFzHWlUTIwDQdReU0YIfBzEodANUjyYdW6QeD3jiEhhuhNMWZD8TUHkCUNJMu8liPPIEiI44IHrs57IM5lhN'
        b'C/8lIyDNJOxVrzU9sbHjzsbCSGMO7a2XVbfsfD1m20oT5t6KZwNiuwCER6ZuQ6HeSCXDE+E46YRjOIGjswQRPd0HvmvzDnZOD3Gk7Nx+NK1N5MLOn+7177Ha1eXcH1dG'
        b'Sqn40gC0dXSfBagWv4HthCMcdxNCj65MRtfheQYUo8OgGBTD7aiN6o7jUO0QVB1PVXd4F9VE80AKq9mETNSg/+edvRxdw476Kx9U/bLnfbmMX+85KU9ee1o0e8SqyEvW'
        b'5eVl+x+N9boUVLsu7KD5tnXiicLAUf/anZ7xj7FrlQsetIk9A8b92PrWhN+NFu/dPHvtu2NvrCpaOq3x5dq3pvn0G8BCk8KdcsnBmPlV9GCTm+AOu10zegblRejCbNRM'
        b'vKzxMRLB7Y9usbByOTaOyEDHw2YTiSkZOs4lquTEIiHm4xQJXxeMr3VojwjwyQxssa6mTGwYOj3QsWKATmCua49D3IYqaNgGujwJ7qLgVSSlw9OdXK4eXaMem35hU1So'
        b'LgLbVu3recCPZ+BtdC6UApUQ3Z/sVuetjv3qcDvcipoER1DVUtQoHECJLoywn0HJFqASeIjajDHoMDqDquNgcxzm1Bcd3NsXnudQOQb1eJdT7p6F02Lq0xmyjRsLzZTd'
        b'ks65sFuFjIZ3uNPYSHpqcA+WZy/tutfi2c6utJ8Z3MlzT+PH6V547kc/z3PtAPx/qDzNytMYcnVCRIVD3XEQfzdVCmtEz6pFGXTrn1V56v08TR7zMWGLgQ21jbSLdlQp'
        b'G++i4ASgg/q+P+QLVKz/hPN8ZbJ/bKQf/+bB2/+0jM8eGvzVWMWRC0NDXg9uKdOe/fBx1YDL8NXPo3Xv9/Mb7PP5c0et/y6t/PXCv4+eIveXBYzRlC2/8OOK/hWtbreP'
        b'/vCu+LWv/uHdcNiv8G6bwo2iOiadQ6FUVcDKh4aEiTEGI2yybxnYo4DVKWTXKTwXho6ge8EM8EK1nE6ZKkR1VVgCBVQnPUH3lrtg+m2shFD6Pw8PjCH+CFTFAB5thfsi'
        b'yK0bdeg03XMFm7PgXuGcXVUKrA1TRHTqhJHohHiSBV6jMcv5GwKosrNyLb1HQwX3YUInPVgF9w9yKEnr8yg1wq05YoGDVMAGiUMR2ojagIQoQhs5gUOchVdhM2UR1V01'
        b'oXW5v5xIvbMpymU68KN7DDP5jXGn3kk/pmhwNxLpVtjuvDj4RNI0HnLS5Fn8aOmFJt/qQpNPaVDBdYjzCkxmvbbDDWO+2UCkfYdYkPpP3uFD6ZZ37u4ROXf3iH52dw9H'
        b'jXf+05lMN2Od/MzQaonBQ2jNRXUQDEWn4H4iwQqdEMg1Dn+On+0g+yyNYXVPonXSub3PQslU4SsuHKyyGLCZqYyf3Ut8kEuskaMkMapJsS6xRYre4DXqzBajwRQjV6cb'
        b'LTo1CRESzirQhsnVczX5JiFNk48TtRuxJkMUKoP5GfiOew++wyXrc76cy5jICtzs16d8rV55/83n33v+N89frr+xr6G0oXRSdevB1syT+1rLx1SL32oqb9gx9MjWyuf3'
        b'DK0fWqEZMyvyQJ06jrk8cRl4aZNnflSbghNk4aW11k4GEQzPcXb+MHoitV/mwivogpP2I5TwECZ9uBcdoZ5IdGQxuqFKjIeVKUmoKjEc1kXQuFAFrEHnsLiHzei24pcT'
        b'opdGq83UZemzTVRppXTo05UOVYQKi4K6kUTXcnYTRSxIv0byaCKPc10Fp+tFFbxLtkJnXkqkF/DjTi9E+qALkf48RP/PyHBeb2SYRp1amBINAuqR2DcXenRxZ/3/jyJJ'
        b'sfgFKXLBEWUW/FbUeMjRGzT5cq0uX9czYO/ZaXFqgl6gxVW+U3+eFrtT4tvbnLT4NnhphWfyxCJMi0TOxmjnweo0rZMY7ZSIWqdRUnQjW6Tx7+EpDmokUngnaqeHR0fB'
        b'KxNCE1Atqo1QwVoHOcJzKwSKnA7rJL5BqO2XE2MfwTf6FHrMoPTYTTEL71HULhWbu9Gd8aKTzFrw47VeyOxqFzJ7akNPubCHsQGXC3t+/rB1jhrR/OOsXgiMYhulBINl'
        b'TRYmKoxgLk7kTtdstsVoxKw/f6OLXf3f4l7/D6fw9AixxUlDyI1ALfUNFOvGOLEuYlVPvHNiXTTItXmc+906uwTQ+qFjDglQneCCd5PmCeGJdYvUTgEAr8C7BO1SvIUL'
        b'n05HuRMLDNuOXUVAiBhMH2iBNyRyVJLf7U6mXpEsu8BiMLvMn6k3JMuS9oZkPYomOwIWC5/I6AXnA0W4y/jxQS8Id9br5xCuR6P/lxEuDyOc4YkI1xm+/MzIJg8OIfqY'
        b'3iBfNz58bEgvjPfZkA/4eXAU+ZIefeVEvqodXdDvqciX/pZCUODhxXTYnLPURQOxI18OLBHU/0q4LUhAP/jcCjvTW4mumunW25tor1S4R7AH+k2EtkTYKMYc8gqqfAYM'
        b'9CEj+jQEXCWcldUNF7qXtDO5tifjXDt+/L4XnDveBeee1o6if/eNzZLMTG1BdmZmB59pMeZ3eJJnpmNtpMPDuStFrzUeJoXIOr6xgTyeA3Z/bIe00FhQqDOaN3ZIHc5N'
        b'GvzQIbE7EDvcXZx4xJ1A7ReqH1HuTSmKdvG/PkjBxSO4Gz8sZKjmArLpmvfgGZdfVsr4ebLksoAfxdwT/vO+HjiXTMb4eJE/L6lwS+l+dG5TZ5gEak/C5iu2QNlFJhAM'
        b't4q2RPVcSiEkHgvs++S7ruIKocIdfe17P+wzR0+sfiyfs4GcsEk8mNlkY4fRQDQxF80rGVuIXWfSeNU5Ct08pHfx42vWuQmdZ+hORXQAnUTHOjehoxay9NI6m/bNcaNF'
        b'grsE7oAtCRait6CD/eGt7sHKvQQqx6DbT4hVThzUg+d5ODgGacEe4g+63qbaeezvfxPsTxrp6YeVJSs4Gq3yQrgHIAEzb8bF5B8wW+U0/vN1fzEYZIUMnjrZ+0umhH4B'
        b'8kkcz+zIKaJHATdyf5ozUHFjdWrmuSGNq28u2RZ8KPnFiWOX1oYdTWmefDpmRdDbISez/hP2OGmL55cDPYtvL2wJ3j5rXMIfkjfO+HSwONB90IdLZmb8ftqtUUfSpqdX'
        b'Bu0JuT1k2cyI+LQNv/VuLfjT2A5uZ0haYdSg0+O+nP0P7bGF5R5jw26wsX1MwyaL/j5p8sQ9qm+GvTOnZi5MubnlJ2wTVES950k9xIvhxVyHhzhajRrtDmI89kKY7940'
        b'FvDmmxgT1Im1rFaI1olx6wtGSI/hUVJbvTNWCIlDgT8Ii7smAXL1lKFr1IBuOIG30Hk8ydVJynByT67jXDG0AyuZzSoJ2gmbNqLKOXCvaCSA20e5oQa4D92g9WXnkjih'
        b'RJbECb01ihEaOe8lBjIfEUfihD6aMFE41rZ830IyewcYBjCeC/QxuX/mTDackDr1/sjaW57cGNksxcvfr/WfOHDpqMlaUT/mraC0jqQPg5e9d3jui+OGDVbUJ/S7euC9'
        b'5u8OJsbskfznhZlbE8rLRxRODlx4+Z1T84eu8P34U6s17rdzM9dfHDHj2vZXXiwbuEJ5df3ZR94xauP9TfrNt+b2zXwv6oc/D0j68IOcdx8s/kydm7h52N0fz9eP2rMz'
        b'WsFTtTtVJXPcRoTukWhqwRvcBE9RJ/loAE84I4gUbJKDmoQAIlSGjlFJpoWH0PVQZQLZ3oiHUQQ80E3Weyi6xqE2QZLtQFcNoagqRBmOdi5n6D62SWHoUs9w8//2zGHX'
        b'rfhGk6aLy5n0xEWQWXkanEeO+ZayPoyc8FH82XjfUQ25y5ys9LuoT/8tWE2METrZF2ngH71Ivhp596vbUOvo+NCQgC3JsMZFORgIj/LwPLoI9/RgPr0dBOnCfJwHQT4L'
        b'43nGBSB3B+PpI3YnjGfDTx7y/ICJK4QbugZL7YHn624PeT/gVNxvBMaD3KY+M+P5YP6/l/5t4E+Br00ILNoYqpkvlaz2+1XQX1k0VTbWb+L1MWVjXypelzRx5JbgvpOD'
        b'F26YfpXP9D1deGlIVuYH+iuSYQtPqXUTE1a/5van+Kmhnv3zlhhFJcO+nL3O/Y+mdYXB/d+fc85jgKfAeO6PXu9Gu3Igjyv6A0vvfc9vW2i/EioswHcaYOgFYoNGbFwm'
        b'rM/RNwWzRdY2soMgVh02P2+ikCgNEcvKGXpNfOL8dSIgbLevNbJOjiawM3QC1iXA52CVvi3wBY5eSHaj9Xvlq62eiGxiObvy8pE+26+8/zC0JbL+jYXut3xZ69WWCZ6i'
        b'60Ofv3f2A2bGN+e//cdzr7w3ecq4icc3mDZtXHnC/O+w8n3lBxbMytW+vWbh31oKflg3OezQlwGLl/jrpq4Z8t32367+241PWn9kxqUEHaz5VsEIHu4rHrBRZb83HUhX'
        b'sPAuPK7DovBWF83xlwXpdidHra6THEd0JcctwJsst/sJCg0lSRklUOMLzoqe/y8gQE66I/VIOccxgyUuv49dD9aiW3Iz1i4JDYGn0X5CevFJDspT87DB36fHJkDyR8/n'
        b'XIQJskIkHI9vZU4AQm4NbDFLP3NaHn/mzAx5PxvUMyu8lrPFfDE5RF9UAcwsudzBWFjkZRWd4LSiBqZYtBgYBpMj7Fe7G/OFS5PoO3Khkkg4st5w30ou7omkdZDyl62c'
        b'sQbnEjUIlyeJ6RUUgbglcbGkgrFKyEH7Wkktzm8VTwFr9xg207KiUnJBDmd8SC58wPCLMJwierA/KSvtUVaKy75pmEnLCtcVRfYoOehJJeuZte4VYiE3TsG8GNcWLFws'
        b'YL+KKNUKtG4DMIexCovn7smYG+t0hXONs/BIpz8WWcw5yolG4vfBCPqATDB5YSQ7tI3E3lRIjLkE8dx0BssanZFcO0H05w4xOUheq+uQLTToyQeqoAplZwr41XlIZGe1'
        b'9GB/uvuJHPBuHENqYlb90rOmZOSeF1OUsAk3kLNvBCVH38vsN1AId56Q20vc7Tee+Lt8ktn/S+mtJlKGnhoyEpVaVegKPISRNF45PoScAEAj8OWDedQKy1FVj/gE5/nY'
        b'RARZgUmqZRYAcn8VnQCWXgRBjoulA2mMcXSCHJ5reoLx6Em7lmkuyMwvMORO5hwXmnLESKGRU1Pg+eUqCiO2UFGlcD4h2qEiMcASMAqWiTZaJ/S4asgZuzWWgqplVjNG'
        b'GTE2tJyVXBTFaPkTgFw9hAEX+YMGxsr0B0TAkRQqxsT2btB4CnbkBrrx6xEr9EdUlKPPz1ewHYyhg8l7Ut9Il0jXaB9ncvaz7Mi80SsYhFtCUPOKfsQSJ13aQTuYQnuL'
        b'GvRiMGqwaOMYdPMpO4KZXncEP/0ixF6P9nVW7bJFs3PT2xymEHwCwET5tPy5/1msFxK/y6F7keRg+irFB+NGCYm2zfTgFR/5ptX5SzIHAn1CfARHryPp+86er9Ur6FFP'
        b'7aVNpe0Hf1029N1z+xrKG0qHHr4Td77UwmR7znL//cwzye/O3BpYLkr0GFAlkp8MCgt65avXxsler1Ek+sb6nmSDX5RGjSxbKgu+WjKpTDc0O5LLjQExZwasPcxiDZUg'
        b'6Qy0HZWR3cNKtENn3z4M98Oj1C08bpMbvQhQjJriE5MdFwHCXSNo/FqmNzpGTwyphLWpiWhHGIMznGexAlWL6mn5GSPz4fkEGvteic7DQ1gz3cwO84a1v3wDcp81BdpJ'
        b'E4TLNTK1+ly9ufvJtvbDoKSUmAkRBzLG3zgrqXqW5qodzdGCql5l2rUuG4tD8Fvl3HjcxdoU2DqWHvRL7jQit+NWCmOC7Z3rE+FZ8WZ3yZP5BdGCBS5BhFuDQGBscodI'
        b'Y8rW67Ga+xA4ZO7wrgMjydNtyNfnbFxIoKUhFByVtAbPFLr4Tk/ugeeLl/HYbChj0U1Yhg4/GRDCnsm1MVTm+ZGrlgg4xXbgKEmwycZ3ANW95ziA+rmju9wsBjuIGZ3M'
        b'iygg9MxFeBntgLZQchhaJ7B8OjxLT0s7Otj6i8Ys1wGc8d0njZdb1vixwu1gGpcRo5pay9IkVVR0vOP62OEhwHsoNxneTP2/MVzG955psDB0ghzN6TZY1KV5e8wQAqFd'
        b'mwxAJcALXeTGoP1wa49gNee1d8Qm1zKYoROFCRiDzYTdc6UsViJAMSfchWVlMXNn10qtbGGUlSH3UlHYRckdIyLHREWPHTd+wsRJM2bOmj1n7ry4+ARVYlJySur8tAXp'
        b'CxctXrI0Q2D9hFkLKgKDtQH9OkyyCr5DLCxfdIiy8zRGU4eYHG4RPV4Q/G7dex89XpibNZzjCg5OcMcR6S0c6nIP9/aIKmq885pfzFu2Ae/+XMyEMU+eKJkdWbTCbUwU'
        b'UT5ytI7Z0e96RZXo8cJkrHdBFeJBSd+CDhMQ7BORBc/hiTjFRWbAI08+dZFe+804r/3G4Dz1pMUetiIAT7gyhlzuB1tS4DZhlzOmp70Lk9zmo3bYkoYf7Wme/XhYx4Jg'
        b'dJ1fUwyb9AdbzgMTGdAJi5Z/rV6ChY2Gyf5mFxYqL9LL7Ef/i097ZFGwlJGjG7Jp5L7oOlS9DJ6PkAC3aBY2rEIXhVAZW5jRZQtjEDwobGHEnK/sSRd3600FmWb9Gp3J'
        b'rFlT2Js/nPxyxs+dxYhzp3c1gmay9sqsy7vc3k3wcykshW3kXK06qktgeJXh8ahGCXdhwTvKKNqCLsbP7RGK1tX5yNlD0Vxcj3hePX5BEGiPC5aJPuDdY177JNNTitBl'
        b'zLNrVFjS1qGaZeN5IA5k3QsCqBLx2779AZ57H5/g4ikfbZ4LaIHMMfC56CjYGoVKdJFgGJAkM/BwcazA5UpHFeB3V6PksAq28/gl3M/Aq2hbED1lDh2H15ai3UVol7D1'
        b'f+Rs2sz3xQMAxt/ITyZutEbNDbPvsI4PBqk4sSVmbdb7SX7C2QGr4EV4Bg/xDhlLj8SDF/Np5pQcN2LKR37rmSM70z9IqKG9j3BH9CfrN4Y95AZiRKFnOsGWuahOFQ8v'
        b'hIkBPwjekTHw8jph0/9Wj1g8r2BiYaE1qmOpfff5rUnChviWvlm+H8+bLCQe86SHFfiUgFxZaHYA0N//nxcY08dkbFv7zEltTeBnyJKi2qJvrW2/29cjVHXv/r2W1Oej'
        b'Kq63PFg18uCL8x/2qzre8u+zOTd+P+L2vE+++KIs4N5V9pq6tnXG6Udwg/h50fp8zc3x/j6PTyq/2fDNilluvv2N45at/j/tfQl4FFW2cG29ptNZCQlLCBCQrOwimyBL'
        b'IIQkbAoEpU1SHQjpdEJ1h7WjImh3swQUZJPVjc1lkM0FhrHKcRnnjY7OuDSjznNnnk+fOuoMM6P/OedWdTokYXTe/O+b//9e+ktV3aq7L+eec+5ZvnDtL95tyrs+/+YX'
        b'n7ivqO8r4187UfnMF784fEDt0fJo9p9/v+TbR01J78xv/oPls7/eZ21Y+nvXnsKk12f91wPer8fcOaHftsWHs/c2xn+Uf9W7T6zZ8dCwV49NLEu4Zll5c/HuYdaGm+P6'
        b'1f1mzKTya9749MLL3pv37/v9M1+N2zPlqeDXo9/+uFf+3olrnmrOYcJtfbWjvQk+aXu0UzrrwV2hMfvj48drjxsunl0TDcQO6IbTtNxXwiy4Q7eMNlt7WNeT7qrepcvO'
        b'DtKOkcyuGlbPxUjtarc1MXNxR9XH1DPazpwY5QZDtcHXyGyy7a5PK1mu7ihGbWhhCT9u+NQf7s/tn8HFjG+EzcjtAjB0zdWDBhMAGtMeAFkknnEzYQMSHXwPwC3NgsT3'
        b'QZhCbgzT6R1znal8aBShG/+I2GsalGq3i1wztjI7/xGvaoKCHgJjzIRgWbd1CPNub8PuRPaJmL0wb2p+LolgI+A7M2joIGmVxGXzknpPxfymJA6FsR6Ixy1Z3RnXm+ut'
        b'7S6rNvQK8a+NPNFiDnEe9MEZBhoKHSeGkGA0BSQlP2CCfwk2WlM6lwqxukKcgHCAJ8Fd/ZA6JMqikW6tyLwsQyxRqQpJB+B9QDwoQM4MB5bK2lGuUYegONfISW4qo0sD'
        b'kGFX8tGou8hd185FLqEdnWwjuIU+KHIxXn2zqjwNQG4wQZ+OPPsybEeMmJoaG92KMgUHXSLC1xyR/O4VfsAhMAtf7Sp3xOZzo/yRH13WLq+V/YuVTzC+KLvbu+2FKv4B'
        b'ny9GJ6wjti57RUN8VLTqzAuJz/xeEtHqHyOa91doa0oWrkav4+WMHkG7i6VAkPTS9knaSfX23HYoY7RncYgRZSTUlgPUNp04bej8Gob8APY17FCyiH1NfDhBqYJhFmQJ'
        b'YogBEd2Go2vUZhGHk3KogLfkvBu/Q2xxNiebdD7CpQFjbhy3ot5TmDeO0L9a76KxC/pcddOABQvhmpeDz4W5424cdy2h0hexsowh9RxHZB0SIhGzz12pVC+OmBYpDU2N'
        b'ERNyg+DmaVgOQ/MCLcuICKVELI0otqV4IyboSkhgNQq9EmaeiKYXIbXLiHxMNI4aRMkwR0BOThm8kHjCybSn1T3qhpLygsFA54TVx8jdWbic4a5kc9LCXZNjBkiohdug'
        b'HW2OI7fReABiLqRyiKgz8kLxowqMko3XA/xBzlcYEGRA5AOcC5VjBOVavNKXSQFA/V3wP4m7KbmZSBbITewKI8NzS6dSbE80dguL7e0W4JUW+ha6/Jt+hiqVRXj7JSEr'
        b'i4YD+o8m7Fe0DvyVtR5YG5Lb466HYXAvc3uusPwijkbF7UeFTezlp1s716H7J07kmQ0HPFZKZZwv9V7tjHYiT9tmGTCtIIdIR3Uj62Oe663eZxowQAt1rjCNhmBaj9oB'
        b'NHEVolsi95EcuojcJi4xL7FUWOEduo3Edxa3ZYlNthghdCsJYA3Vpa0VdrkP+keAcJzsWGeriJP76uF42Qlhh+4/QQpaa0xygpwIaeLbvEuSk+GdM/pGklPkVHiT0CZW'
        b'FzkN3iWSmjRXkSRnB0UgKlAR2laRLPejUKbcC0Ipcn9IY4YaZMm9IZxK3hq60MhdFYmbDAPj9vonAEHWZuoZ7MHZBpBtZbmTz2NOloxn3WNxhG+mCXDxe/i7xI8ChB8P'
        b'dI7oLtpmRkc6Zj25aH2Sx3VfY2W1+5UojSWs6hFTtcLLI3ZI5FFd8WAYaXCYrIwfQApqgmLiEc76Kxd1pBgWsTV6Kmu9Lvj8m5gqdImtQjRGu7IFo+xkjmmkNTiN5ajr'
        b'ph0RIiYX7gW0LDpUTcNFc6GVxFyVGFs2Jm03PNFiHTQ8uOKj/tiO8IoN/a1JfMcl/b61le0InShX2BMddoL5POME0+nDVDx3YQ6IA6Is1AnKMBnZCMIYdC4Mq6fO7EuT'
        b'TQER7wD1eTxXgTcWliqNM+LKPLri1hk31rJL/MAIn3tJKBwIQ0Y2b3GlKiIOHr/6kml1bnM/H262zIW7HUhHxe9bXgsbKW68hu4S2WrHvonwjZ3xnV0Aa2AvdpMZ+A9E'
        b'g/rUdaTQX003IZlfldFmGsamKWtjH1OM7blMYxJSz/kZ818gp+OwaPQxAkiZgu0y+ZoAcUCcwSsbUoXYgIg9Ot07ORhQukD6/zLQFax622mDOf5zKqmkYk0tmGGlx6Ok'
        b'8Z1iUOnw6Y9tqpRyeZUghw5hDdUKVcdDMJVCEqIcIZrYS2AKbhKojrxRR/SoHmDrW4DpHjF5ffWVjVDdbtHqmpmdf91JZMTiZvX4YcrL3SGHP4m6minHPN3zq5Jj28Ky'
        b'77yDB7GmCNGmCNGmCLFNwe6Gxgg6w1fJ4GkbjWlILVoj8ufok2M8XnrwP1QNuyfE/K5tS5IvawnLv92gRLlMSBaFoKYhEVqSa8AEJQuxEeYRvRlagzghrmS/oE8lMWCA'
        b'YBFW9niGH0hKEjYMzw9Z6+JcLsCrav3uepfL2C2mc3/feKPSC1JLknFgRDgXYl6rurZZsq2Zdz5SC2MnXeGV2sfGypsbHdcifVxhK6RxFfVxlYy4USxJyeQNlDWDDR51'
        b'BJYdM9bQGz6jwsaAR81D/rAB7w35xEn6Xmj0i1Owk759276JFvV3/HwahxFzWDEdbaFWl6uqocHjcnWRWnfQ1LbFsQiEsc9pMxoG5YGMVdJfJQf3XA3iuzxitHtgn9kh'
        b'tBizqQi6BlE3HWNcCYC51uuPJCByLrurPZVMfhQV0/0N7EjY2BswmZKN/U3H0Jfxe82KG138ZLROKwcvfC/Bf9sVw6IVddgImlJZ0UbING1kYZNEZBHPhBWoIYA1SdWD'
        b'h3lRuY75C4rY3CuqPU2+2mXuSDzuay4gMrFU31dYySxooNc3tk8fOnEFyNaP4DLsSh7YJowm5mDrcvHydfsmKlfBh55SDDwQvjcLbTcOrFMbaIBdEaVEfgWXWg4PEpAB'
        b'ANjAQtYw2kgkmP9Awh/Ew24+g7tRaDY1mwOmgFBnBuIe14opAx0MCb5Z7HkRj/cx+heAGWYE7UsdATN7D0/cEgllLqCkTMjP0myFks0BC5RmCVixawOWrhzEXAYxLc22'
        b'gE05HeB9hwMosWGD7+IYzisFbIiz+NSA4FNlqv0SSFvLG6uTzrFxiV4y9UV8K8cWccDaAGqy1iPDcEcs/gaXXFvtJ1EG2h9gh/HD3KqK2DAiLiQf4ZmMArLwxOihvcde'
        b'3eD1MfW8CC/jOQhkGuGrFTNmI1TLzPYbIckXuU4314EQuw8OHTnYI/v+drJQy2z12/lkWuVm3dGeRHY22m7AeiPIYALixbQWc4Siohy+KCftcjlhas1TRmsULto4G8+o'
        b'bSSiGYaAuAjt/tQ1tOsQhCZwpPTBS39en37UkBivWD+Y7RfjLgvr8m+4raGmiFW0SgJvl9Dsl10CGlx0OhKlRCnVnGpOtqTarZJTcpqYYvXtFeoan7bJPrlY21Sqbcpb'
        b'Oi2/zMRljJeKtF31c3L4JpR76aedUINM4WmmSCpPGrkVxQQ5Zm6IbJ6jnlVv143RaLdrT6onStDjKMXQdtTyXNwtgnZscUG7wyAEGSTR5IyCiADfEiVV+EhcfWWdW0dW'
        b'lF4dACmLPqDXtUJaOhfLHq1t9EUrMVPbyHN2dZ+gbdD2q3d1eIaEf745XAwNnEh+/VDoHCheoC0loF55ZhisgvmQF2pEndo1o3kwiGORHXI83K2yU05Yh+bF2H6RFHFM'
        b'aqqvX6lXt2OEOXo+yUgY2Hz5GDqTb6UzGcsBriKxHySd2DGVKXx0YxV4nVqAnRKXFpGgbO5epJ5zIfrujaJStPzM7N3ldBKqKxS3wkkznwn/q7rEtujHGYthdlmU0Xwn'
        b'O6gNMBVWlfLowPKr0toUGI3SObKmH3MSGqLTn4b3DmpzaQcziuFgCM1crlkxhadf1tpopM6Lv5aGUuaBJnSgfBnhjQDvlewQdQQS5mvpoPOAgLxAZQgOZJsKizHQGEaK'
        b'BpJ6jRCmLP6K5+cEdK5vRX+sxJJzEkOuo/b8KPyH1atTHMjicnncXpdrYUwXpl5WJEXonIeAjfFzizhdwIoAgoTbS2dIF35zuSpjSmw3RSnGD2ghklJFnbaOYLh8hXIY'
        b'dodVtl++j5BD1LE4euOi+8J4vEyIbg60EVxhWEdBpCJjWK2i3WwVHWKiDSC/SNzuOO2xW339ta05CLPVR/xROMhzmeqTkrZDveOWzmEgGgszYOA2cYm4RKowuZmYGHL5'
        b'JLe0xAKImx6iI3yEj9YKK+PLAUxkMNJG/DU7DZ41klxetcRd7ScDeXpH/QPsI8XaCcggoOaNDom4qmv78n4c8wi3IMV+JdaRr3XT+cEwaLEBg5Rr+fYIKU6J5THzKrOD'
        b'RlwJ9FiNUnGqrUr2czoJRgjpXGiVBCRpnV25mon5EhgSA3Q4sVYwc/NZDBPEUHRBYP6AmQhAGWJZWonAgzyLbbSMhWLkBFtJPEBpUo2ZHrEXA7GwggnDEjDDlRBxXkfI'
        b'Y5NfF5NtJYt/CIRbJUU5VgJJt6YSjEu7QvfpRGXc5YtzYhusjqF7I9qu1R/kwBTzWRxdoTG4mEMkITn1J+qeHtqJcm39tNJCFI3bML10aesyHTCPm6AesvQdqD7Y+Trt'
        b'FrNOCTOh40TAVnSt1kh3o/UGYJqItjynNzTUNTW2Oc806bMnJbr09E0rBKOprwUA+D2isMnEUHnJv7LRrezDR1uUQdfhpmr2UKkhKcoNs/Kr+lyhfoUsQQf6esXRxXjZ'
        b'2imCD3cYawcgIXpVLNSOak/H9LN6rBUYLtVaivML0RkcGvfLubmwAM2PL7Vru9Xz9e0On6IMEpSghY2cI5ZHD1pfPCMAA3icB32n5IeQBORCZqRtQxw9mw7qq//S3yaS'
        b'5RLULa5u8vkb6mtXueUsD5CzWXQKr2QNcPsVtxsNoTa0zt+czo2wUvRRaPaBrL+gcnLtIm+DAmW08k2zKr1yFpLRaKWiUpZrmYuqrFydDBqQk5vFCO+2CssxVWhbRKXH'
        b'07DcR8ZmlEp0L4X2WL0Fhu2VLB1t97XNDugsOp4U55VOhxWEVHkkLqYMYkr8WI9qJTD0d0mGjJyV2feiw19cJAVAnjysbtAOqzu1n2inAKxpxzntce2xG5pQvMOloYAG'
        b'OrLHjzdrZznRy89cru5qt/SirsAXxiw9ufXQylxjouMyW4VIUlFm2ArxqMwK26REh2OibJGtSD7INtkO5IE55ojMWmGhDdNKENQZceirohRIIKWsqJ1Fk+iMPMChgFQt'
        b'zDSZ3yM2S1H2XTbQCHwtyjpyi3g6pkCqQlBCUZbdtQFB/wIIaAYHlIWELIKA6PPiE4WlDMgdmRLQFsYAFALCJBQzMEE6kxGHGBSKwcxdItTA+xaeNw5izMg/n4prlxh8'
        b'1+CFMMjWd+zMNGJ3Ef/ahdx12jgQY8rRbctQxK7EHWxU3DW1K1woQEm6FBHB6/vh1jgPS4ZyEMBm+P3NbMJpg0axJTKOjTIEibonwOjxF41FK6kTCyQsXIxQyFEcEtws'
        b'YToskrDDkD/EAzKLIqbQeXcy7hDKAviuJo6RRLyeHn4hIKG8ADtjlS2bsKtvMHhHByTZCpvxCkqBk4gGBMCReS0MNOUwDd7bAXhvwTjsi/6egBLq46wV2JulPQLMrE1c'
        b'WcQ0G8+PIuJkrxyRytCxuOmGSk9T++PFKLrEjheRsyULdWadG8lEQARlFo7TnOiGwXck4Eo2KF9E4QUyBVrQto+rG7wAVPwEm3yx0ibMQChkSbzgVk5yAdG6yAEkYKSz'
        b'pXzksI8xqhCtANBCe5focy+NmBoU2a0gp9PX5PETcVHfyn66kvyDs239zkmG5idvWHS1C3ZeEFAz3vydU7QLPVDZzJ7Kr+p+hXa2O4GMMlFRqWgRLj2cPVc3i4B4kdgQ'
        b'aXPl4/wirrx4kI22NSDCFm5RrCiHgm/pnSHri8QNMloBHXbDeFtdNR6UAfFSnxms07nYs/PxUvF3kLCb4PvvWslMZs82maTALl85ekEdbq80q0Jc7AE7imkHsB3peMBF'
        b'DBFYUwdRWBu+sdMG+OqnJxGepvoBGAWENNiUb+dJSgOA1kGe0FxYKbAuZOR4ehONNxgHz19lE3uCN9CnaQzpMZex81bB5aI5dintem+dt2G5t3VfzerTz9fnknl1Px8e'
        b'x5qVfOywRJp6DI4pZfjmOk7HaA12C82yGe0Ji0i8y4tCTWjLGjL4ELs1LWZiJeqHGGm8WUjkV3Vr272xSdtBJ+xj4rbdzMUed9K8QdQFkRiBPdVyzRKTW9I18xD6YArS'
        b'FwyYAxKB+1y/xM63lsBWUAO57BMQ6Bv8O7NSxevTQ1lAJC62ks52gFpHs/CAg1ti2E9Wg8OsDMKgjfGUoS0xi7JjdjCCqa9a6QDoIxGZvqy32oFvvWixDJaBrUMCfUG0'
        b'4tSE6raY/w9CT1qpgVJI/YBxjGKV0rok9gJq3UlqdSkVU33qndq2Vobp8VJtIxqSyuwqqU+raxo7tDOOf+TkNoqGJBAlbqAfzAGAgXzgl8sRD6QYdLSDJHKQZ8lUNBIj'
        b'1ukN1XVFtR53mYLkQBvUo41cxDSO8W0ZgelL9QsyTyuPkdECfaOzzzRkV8KcgquJmJZmYmBaUL/OZdXF+6WySynowjdLbnDrpvsRm7xk6ecrRHk/HC2SBzDX+jAeLauI'
        b'pbLKh1IIESvJBMq1SsSCwvQNTf6IyVVPnmrIM3DE4sIYgEvHCEdEJIyBiq/tKAqcCSZTdFI5CD9IJhzBzK9KMjqpY9YnQjW70U/oWYMJiSLPDzUHVyWGcLUBFELYPJfz'
        b'3qhr4K7iAT7x3CpAzZaYAIaLypjbMZVZmT4XiOz7+hOPkOXF10nKzX6LLGCfwzurrOc2nEMoh4p787mlTiDLJdbjsyGkE3SmsotJBNKqG5o8MnV2ZTU5DsjCTvp49y78'
        b'OzJuTo4NCD3oTuqiiKm+DjpYqaPDtvLZRK9HTG5FAdDTgC8ds5q8GF3/4vO43Y060ItYYLehrGo7XckRCUtPMBmyvLwT9tBEWsgCqaviKKAi9ar4aP9jis51XfI5xktS'
        b'+ss0K2FO8kbPK/1hFCRjFHTmBW6OJmoMmyCmWl+0ySalHp+JAXU5jdvkxYpkmWL45OhhZVVCtKIsxt9DqRiqGBVgAkznls745GiGyA2grL+plWeUGDMv6WPnXZMbUx5O'
        b'TJ0xLTDGNJ0vQNfoytHEgZWU1ViXeqNzFG+0aperC7lcAHGR3Zpjip4gWwmxhsFLjqmkHq2dZDP+z+V0NJ1GMM3gBmL3MLlOPF/lDfUgEtLx0jhVexoAB8SOM4ReJJd7'
        b'RXUHXGMAMbB2B8UOm/3y9c3iIBME4WEnewb1DA3VrXi5DS9rfwg/twYi8SadfLVKTrszyYE8XQs7pTvTWIbmk8q1lmW6O/r45eodS0S7dlo91253sOh3Up2N8odQ5FwC'
        b'8jPKI0KpzgpJTgwypzdi0By01piJc2uDXSKJEazktgZPtGywYzDLaniuFUuqLs5JjkhFMyYVtYN+UXwD1YT8nI4pkAgAEobG2MEd6hUSlkioV01hkyz4zSyk7xKGmtCl'
        b'uBkrsbAhWcv6+S7FQ0B3AQ5Bg9HIjGuhPdDGykXuiMPn9rsalQa5qRpwfQemdt0wedbs4vKySBx+I0uyAKviXC7dS7bLxcTTXehfxcDYovr6VxpKLHt063xPJhldgAHx'
        b'WGzHhGNnPGhdX/JS0myoSVZ9pZfsaqKpGAQJG1tnNjP6cjkaiS2LtmFCFD4Iq5KpKm0+l7WpELIDoyZeQjFjhysP7YwHBMbyWiIoC0NAreITSrIDtSkChQq7/Vom907P'
        b'zSLg8GJXDuWr6S3s/wfMTPSDsE5euT0E+KNsWitsTgS8UzpgCQjGPjaTm8XNMyTCzEx59Ctcp/Z+/WZPnnFd1lfYXCb9uEJx19gJUY8Iy6v06RAxAx7Q2OSnHouY5Kb6'
        b'Rh9T1UUxSToVjZiWo8iCztZkcI36lJIINYt/uGa2cjeezZgMcW3SvDajzBHtXMnElAIaMI7GgFUsYpvq9ixz+2urKxU8MWTaozgI1QbDCf8SYkdlCc+opIMojcXTuCB+'
        b'TnLb0Oeivqqoj+kZaCLA2UX8EuL9JqAOTakcSrCi3QwW7s7CVtncbJMtzXbGO2iOg/GOI0nXL5tREsWRwTXHB2zKs0a8QDyMJnIldsq25nhvJoXtED4tx8FXo2wrlr20'
        b'sW1dAo4A4KDpXB2n/A7zlh1duQyu8R3IyRlwbuGVMXJ8wFlnwaeAk5UDz5kBB1wxb4sOQSBP2RmwYJ6y2GyDWjhZLSglfEcJc1YmfkeJF9kSMAXiA3bAB2xL8Bq3xCEn'
        b'bQJCJGBXGjEW1NbMIFzZRVQvuYhjMOcijvjHwbS3fvXt7K/HFRHH45I4duxYGriI6ALowc9h9CKfFeEnRCwTG5qUWgA+fHGOEDF53ctdK9htZU48Uw+wkxSvp9br9jGg'
        b'VF+pLKr1+iIpGKhs8jcQMHNVAayqi1jxZU2DF/BbpaHJK7MDkyDOVqna7fFEpHkzGnwRafrkojkRaT49l02eNycngc1wEgCQKAOJlHFMPv9KwI/jsAKuxe7aRYsha1Yb'
        b'O0ZweaA6bv0ZqFoowqS4oRYRcxXjodi8TfUuSsGkjSV8hrfuFX56/Xf9T8cxGVKSDZ+DC6iMFpBV91LpJCRQIuYCo4QlnVFH6mho0UToQQw7M6Vgiw6Xm5kzf49qarCl'
        b'J9KyiymoQ34L7VkK13aF0SFYDzqpR0pnmiyEOdSw8otESeF+akXezFrdQkgGaqbwsjnApzGJSUm2IEzzm3QGqTlKMYvEJrUSVm671G1CpYJK1llDG2pGMoY9mXnwNdUr'
        b'6NPuUt4PUUEvKMzKHpjXrx1OFZVcQ/BE2mLOZmgF4wXoemKLDJ7deK5VU2x4B/QRYta3m2JVxHpRB2P1h47sSEPsYh6uCim3ny+X1k0ZkNIfczprDjWPZJJgj4jQ2oiT'
        b'ZnktkOrVDZ4GRYfmLHODgqOzutadOdaGFK/8PlpTDeGlyeBQoekn0lvEYwIdFuvZEoq7HdsaBcXKDr5TlK+F10G+8jSvFxPDJviRNqRaGQbrIJ8RpijDINFildKdqQPI'
        b'040a5lf74hqXillqCydou/nepgAK7UX3f5JmE8vKylCMTaQ012jb1ZO4LNHTBCo0HtfC+J00g8dni5x0o5NHF6UWGGJIVhvXp4vk2wFI3HdSQemcP89NWZS698V18uPH'
        b'P1/wM9Mpb/514+8KhSdtWTzP8ceTh/6j6eEjp07/vOJC8QXf3b53Xkr4a8Kf9n/zq+eXRzKdO3b95bML73JzG8yDn/W3fFIbTn+jb9WO18O2gpStFVmXniqdXrtp5+sr'
        b'q4oakk5UZH/kv+PNR66v2uxNXN205s1Do5+95dzEHq8UvHcgMyX4R/PSeW+E+17aec3Re58dfFNc1cDnR63ctXVRoNfzky58vvGLgpfPFE8/9beHUkbtLPrpf5783UMv'
        b'fZzxy90fz/tkxoj+s9cE455485sF3kVD3hO67mh862z5xezhXz2ecyqrZeSNgz9NvH7Hi5+/9lXuo5NvfC3upr+WuR/7Y8l1Nzwwdf/d2x7MHX7kpZlbtKbfLT70ydvl'
        b'H/Z6deJvxSW/mJWQ/ER4wXOvp4w6WLIg9f1Hv+hVvS5npPPVJzb9eUDK9W+lHPr3ZUO6TEm+u7KnaX71A0m7tjV/s/c5Ie3CtWnDX/tylO3+L9+6J9gv9YWufxRWur7t'
        b'dnxowkt/uHXjky3ZGYeyN8sL9r2wcMuzPR9uvFtsHNX34KH5j+zaP+rWlypWd3nfP7d87Lo/lvz6q5T52/iMqjf6vT6zZs9Nr49d+c7oY71+1u2zop7KrC9eOTbpz4Wv'
        b'Dnwp/PbWvwy57sPeeeeDTTc88c764y/NeUBr9pzs6dnz7ILMJ7PX9/zsNc+DCy7Jz/xq5bbrP1emZIz52UN7X1332w933v/y0WXyiKn/3nvax7trduxafvLU7W/P3Xtu'
        b'xxcvPPfJ8G8qw95lcV1e+ibjdPZrcq/qC4/ff3b9J/et3/i4VpH85jMpvu62+88/93Rk8m+PBuOXv33j9uChFTV/rtVcD56+c+xLTd0/W//bz97/2ZdPhp7vvW/Kt78c'
        b'U3x/3qtnWvpeONjwaCB8T+b7s2eXrn93/Gs3fn1f/t9WH1rw5Z6vvnfsn7JgyUOlH4yrPfIL3nfLmoH/+c2QZVX3frntr3P/FHl9yOIx3933/DW+5rUNL3+994tXPjxd'
        b'/d6LX97qmvR7ccUzpedf+bBox1sPP39IEs6OaRo9dJRv+wdPP5b509FN457ybvPd2XxughZYMzjlt5uOLury7vvDq89dPff9ipKK3JN/vW3EybO/ntb3wYV5Zasjb762'
        b'8eu+77z6zfaVr840/dun3+fu/O1bJ+Sd9SP7L//NW+8+fOuWnmWPz1lxZOiQl/L+bBt3YdcH6p6F6sD/KKp9atO9q3OnfFv+oe2dwa+NPvf2C5N2zZv8u9z7H/vPLU3f'
        b'rf92ztnNo24+6637z/c2vfxS7tOBF16sL7nnzF+6Xzvjz9fN7T6/+4bvVw9/+fzKayxluX+yXPPRqRc++GVOPDmE6aI+rR6no8vNQB9OLy5Q16ubLdpJN9dFWyNqJ7Vt'
        b'6glytKSenRGP8crpzFttgVjqgelcknpWVLdqW7Q7yUVNvBqah4ZKi9WNA6fma2FOXTOdS1bvFNWT6pPaaabNvk5rUZ8i87dlBbm8epv2AGfVTgnqdm2L2kJ2PNWn1HvU'
        b'PW2dcGvrtTPoiFtUfyKoYX8WRjuvPVzh0zapG7RwO/nT7uou0q63Ttd2Q4SfaKdsqLNdICRru7kE9bzoGlbkH4oQ7ai2zwZVIS1SPRt8Zu1ktr+0zYUF3FR1DRcYZZf6'
        b'Wyidek59qEurhOjS4tKSfG1TDgoFpKvnWuUCUCrg1hI7pz6+3J9H6bRHLZ1Lbmj3QDtJduMGv384xJ+urdHW+grJMePmpk6ED6AQ6KC13HJtt009PTOX+qdgvHbSN6pn'
        b'J4zhCSZmM36n9nAdbQfag+puth+MVH8KiN6P2nqueMkZ8U/M7P+XS04fhhz8P3ExWF2ehkrZ5WKOKBEzrDTzZsHM/4jfR1JPp82JAuYi+0+2AeZtEfjUZHhOEfgBMwS+'
        b'WxoeqffJNwv9J6RnOE3p4yVB4NP5qz0C378J4lklOnTPTsRrFl179MJrsomukF+6DZ8SRbymmi5/dliNN/jfpweG0hz03UlXyLN/gwMphO8liIE1Tu8t8JkQM93i4B2U'
        b'V6bTSvf+C/DabRhec8uUZ6OncsH/nf2dXFqJAOytmzkDtb5vxeXmNrLV002tW5Qahq2Hc2aIZdr5ntoe9Y7aL275Oe/rA3Pyi9tHFtxdrFwY75j89MjQ7kdWbi9Y8KVn'
        b'/r7FiyIfON6S904YaZvsTR3Yb2CfuX97rnDKFu+WyS13i6ZPn5j328+Hj7/tk8JbZj7Qd+U1w3pfPPVRycG++XE3VV73iS04wfVmas265f3/+ui64Sm3lK7c8vqUWrct'
        b'YUDvgD/nwKcl27/a9v7PpG3fHz48Y+57E1Me/nrarpuPfPTZ5ne3/+GefYNunDZl6J6PX03v8lqPLqWDvk279fCzz5y4L/nImx/u2jU5856n1v/Ct+iLb188tPfUd0fq'
        b'rz7xav/zv7krEN78iPvny9aNvPbMX85+alGFEXLBl5NeT373wo3zlZF1r961+vXcqimvPp08d2u3ukc8Jwt/PbYu/nhKXenxoXUFx5vr6kcen3j90Av+Fy784fDolxtX'
        b'X3y4y+jnDlbMPV738WdfHHHvb1j39Yotjif3faoMfuv9iXv3nU3afHfS3K3Nj2ZbAse+f/e5nY8VXPW7x8d8cNeHSa55mb43vlz3F7UmsHvP8Ya6Be99/Om5b56c9+SQ'
        b'x7qXur/ceKrk+MMfRL7If7LK/e5/PPvGiyX3x3/e/8yY0s+e6Lt88KYJf/jV265fvTc0Z19k4bd5DRfrM0/P6huo/t0jHx3PaHhn1ucX3379rqNffDT26377LuVf+tnc'
        b'Ga80/v4X4z54ZoqZf/yF3puF9QOqLV3mzJzYM37Yryd07+n/9cReouP4hrEbf7JZ3Dj4md4tjRtT9rzn+PiJn6Xu2Pnv9jeeeKbgs8T3vvtijXlY4MVH//rg+e05+5tn'
        b'7Z/z2YVx675946E3nsoZS5YWHY0ufUJt1Dbk6zNqlqg90Ti4LEBbZ70bkJHL0J1NpQa6s7sPuWPpru6dZzjFFCHOEeYUU9uuPcHMiG8tUNfmQRn3qI/mA3WrreFv1var'
        b'ewnHWZA9PE9boz5VUpCLZqi0zeQab2OJtsHC9Z5tSu7Vh6Jph9WntXvihATDrPllRs0LmplvsI3qY6klEEfbmIOx8sxcwgixYlbd9dm0yytXq6e0DQOnaptEdYt2DydN'
        b'5dUTixvINWeCtqMCvRk/pLUMEDjBy1+LdiCoBdp+qNMDeWgpvdzEmccL5dVONaQeY36PD2qHyJvfxrwBBTxnXiFM0B4arD6utVCV8rVHBpWoZ9A9J1SqGNAOq3peUIOr'
        b'1KPMofKDUMwhbYOfK80HijrAj9POZlKFtJPDYUyOabtWa+vxk3qCn7NiGllSMmera3TDXWS2S9ujnbOrG7U7KKH68DgNMEv13vip6iOQsJkvCmgPMM+LR9WnB8OnM9r2'
        b'8kIe8lzPT5kOuC0yJOq62qG0ECBvuVO17ehqNDx9hLaOxN37DTNNsmjb2Visg/44HQdYq/agdqikwD5AW68+ph6WuG7qOUnd3V8hBHf5fHW3tkHWduVjNfPQHFoJIKVd'
        b'F0tD1H0rqe3zoO+OahsGzEHHi4K6ky8q1XbSl5naXu1cnnZ4uRYaaIFPh/m5s/PIJaN6+OpMbcPcVYDMiZxwKz++r7qdMNwp/uklBBt7aI/DSOWYuTh1jQBVfFA9QhXS'
        b'7tRuB/p9Q3l5QTGOZalphZ9LHi1Co49pm2lFqHtr1VMlzL9seRll4rwFpsqNk7zaw2xQ7tJ2jYIOPKWeGWjm+Nmcdr96dhh9GqE9Pl23VTd/BHMbW6VtYobujvVeCYmO'
        b'kAkR7egtnFTFqz/NUPdRk7Tz6tapJQU500phcs0WJjjTFrioSQHtJ2PZbNZOzC/GuROn7hS0w9peSIn1HV84UtsQI5QrOa8GOmOtqN22GGgIatHpudqBkmK0a0s145za'
        b'ehFohXVl2jo2CNou+EJRTJn9OEni1f1x1bT6tQM3qUdYi0qhu3OKJfXUWC5Z2yoC4bJee5D5Ihh3bV6x+siAnIHT8nER3S+atJ3qbYvUrZR7VoK6uSRvajEQLkM5qRsP'
        b'I75vAFurjw7U7tM24LIHsmaPtp+TZvJAhz2sbvajnMDMlXPykhOmmTi+hNN25lezRPerW33aBiCqWmZyZNYT+iQA8987hFbqNO0BdT+sNPSr6VXv5KREXt3t0c6zZbxb'
        b'Pbm8BEDPQSCPhg/lOYt2t2BeuJSGKFd9YmKsmc74FWSm8xYH8/rzlHa+f4yNTPXJgcxGpnosnvpZ29B7WQkZcjaWpVM9ICZqpya6tFMUw5Y8VjdGmohdjqOlm04FYoX6'
        b'u/rmysstlqr3qi3MZKlXXeNHM9baHT20OxCWFMDSUO/My4XxAerpbqA3p0PBIahBgXpU4krVYxYgmY7fTHRrjtqyIE49q25DcrQRk5fgdErV9ojaQ+phbQcDZQeWAFhE'
        b'SFY4bsnUUgAQcdp9gnamh43NpTWDFLLM2wIpnoANAZfYCUE7AYt1G8UYdp26O09rma5tLsnPKZhmsqLB1UxR2wrk1XkCMjO1c1pLCa5AN1C6m4BizZ82sHBqqZnL50zQ'
        b'L/sgJ6J9T/hgW9gwYyntT5vKc4B8UzfhDpXWTxJhT9pFlDZQ0ceAPAfKt7xcvbeJtg4L1OpxXCVbBzGHsfvt80qmwYxJGzx9Gc422FymW7gM7YQ0X10nMdhwt7rmRqgW'
        b'MvTKAUAI6k97AZkN29zBGgCdOEHKtTtvpY6DrQkm7hlOKuDVR1apW6hd1/cO4EY5sASG82zrXoYV7p4tqWu1A1Y2B0+oP9XuLykuzS21cGZJUO+92qruUY+zSXSPutVO'
        b'Rn9zeIBVm4oLoIe1B2GKLNeO/L2zM8P48Yh/ATrpX+4SPVMmmu0oXLg4QbDyl//sQqJJonORdKB4BN7M/gWJx9hOFkc/LWGUnJ3JEQp2/QlyAJzdSnmnkiJ1689BOWMc'
        b'PLx0kEq1lQ40HYJZXHEr1/431MwzDjmTfUBpEJ/b39TocrWa/jOOGX7Ox7YUHxgt8W2suVL61kbYIZ5Dk5xM1MD3LFyrOJlfAr/wDaEbUAwtfBXcBbgLcBfhngZ3Ce7X'
        b'h26o5eBuD92A2oXhXhh/Ccbkg3zwBkNwrplDoTmPWC+FE+pNzXy9uVmotzTjEaJFtnms9bZmiZ7tHnt9XLOJnuM8jvr4ZjM9OzzO+oRmCx5Q+hMh9y5wT4J7CtyT4Z4J'
        b'9xS4o9qzGe69A1woAe4JATIvFI4LoA12PpwI8VLhngz3LnB3wj0N7v1QnBvuloAU7iNbwl1lMZwux4czZGe4u5wQ7iEnhnvKSc1WObnZJqeEuwVEmQtloMh4uK+cGs6R'
        b'u4QL5bRwudw1XCqnh2fIGeEpcrdwsdw9nCv3COfLPcN5cmZ4gNwrXCRnhYfIvcOj5D7ha+W+4XFydvgauV94mNw/PFy+KjxWHhAeL+eEr5Zzw2PkvPAIOT88Wi4Ij5QL'
        b'w0PlgeHB8qBwiTw4PFAeEp4mDw3PloeFp8rDw5Plq8PXySPCBfI14ZnyyPAseVS4LGRfy4Wz5dHhCf6u8JQkjwlPl8eGJ8rXhufI48KDZD48KWCBL1khIWAN2Gqwl1KD'
        b'zmDXYK9gaY0kj5evg/GzB+xhB4m3tNqmdQYTgqnBNIiZHswIdgt2D2ZCmt7Bq4KFwYHBQcHrgpODRcGpwWnBkuDs4Jzg9TAfessTovlZQ86QNZSzVgjbgswNO8vXQTkn'
        b'BpOCycEueu49Ie8+wX7B/sGcYG4wPzgkODQ4LDg8eHVwRPCa4MjgqODo4Jjg2OC1wXHB8cEJwUlQcnFwerAcyiyUJ0bLNEGZJirTDOWxkjD//sE8SDElWFwTJ0+Kxo4P'
        b'imTbPx7iJQdT9NpkBbOhJldBTSZCCWXBGTUp8mQjTXNcyBmIoxL6U9o4KCWe+jMdeqgHpO5L6QdA+rxgQXAw1LeI8pkZnFWTIRdFSxehriLlJN1ix3FsdoT6hRyh3JAj'
        b'4AgVrxXWoggCvsmnN/nszS2OQBwdtU9hzgNIJYDJ9SOU6FyEDREQpoQV4upsSjc/GhnhlvCGBLiurXypSz/fgJysWiZVWplV1VTr8dd6cwRlBUIfOtvD/bBTE1muGi+x'
        b'z1BSbY9JVxXm6JBZed5QZsmRANAtcvtrFFSgsLpXVJN4Damz49F5Q03EYYgYkWgRj8ZO6gEywpMdjWvXNypunw9CoqdhEeo7oxCa8jLkfRGbfJFkQ7BeF1fgBQXvLnKG'
        b'QHWD7Ab4SjYnUAw9IjY2NEbskLvsrqlEBQdrjYudyTLlylabFFGYHDHXUD6RuOoGV6WyiLxvotNQV93yBq9nZfSVHV55WWYRBzz7/JW6YU8rhGo8lYt8EQs8UWY2evD6'
        b'/D76SsLzVMKySqU1gCK6GKJ09OCkt4qPBCO8DZSPBwawsoolUNzuZWhFHQMo90ABU7XHXalEzJ5KGODBEbGqdhEJnqP9G+ZaI2JHj8zsmYkCvaAPsl+prHajC0eXC6JX'
        b'udhAWuAJBRkikktx10ScLrnWV1nlcbuqK6sXM6limBgyM9CGlhgvCQNy2nnTw0NypGWZMSyBue9BwSo0JYX2X1FMYBIeyAukVSusBQp4abcAH6s13N406t8zDYWT85uo'
        b'RJqODTjYpG1TRxQ9Mxt1PAtfQxaAdA5YWBlYkwAPMEioQXWLTJkc5pAShhjKInEwKSCF7HVW5faQo9kUEEJxdYIyFZ7N3gEU4pSFIUcc12wKcUx8LGQPJcMXJ7Td0RX7'
        b'whyyQLjnWiFgDnWBEgXvAwFBuRveZYbSatBoznYUA4NyUqCcRyl2OqTugbl5V8D7XqEkivdRKAngjoW01NKbrRDTEkqFmBLsFdDXa1EZ5tmABDsIT/mZ66xbUBTYDKls'
        b'lG93iGUY2bFDDnrKgA2e7PhEzoUgPJtj7Q/xlMctkDYhFB9n6MmJoUT6Gp+ONoGB4pO5QBx+CwgAb+O7ckyBi4yY2pjXgah4HfUn5LkPxsEe6galC9gvAVMqKrCks36A'
        b'76epxl2NnggY9urYfHH8tw45ev8LsJp/FDcaZzXOYl16yMmwVcJXUXLILFhJPigZfoki83fEJIaYtyMz4LfpvCQ6BaeQyPfAdKKdfCM5hTaLJUnff2ixvCLoi8UJQ52j'
        b'L5bU2MUCX0UcvJAEe9SgNssHBy8P0kj0hBPfFJB8n5A7enMIf2kw6CJK6gUsyu0BC2njWANQGps8sFy6jeG8cqh7qG+oPyyCjBoTWn6C6Tuj2R5CKTc75BoXsIe6w6J8'
        b'HSZeQhyXgRuzCM9OfA44aNlBPoE4QBET9AlMsn/sW8BOXry8oexQfKi7zIf6wn9/+O8VGlDDh5KwnFAvXFypgGLC+24hPpQYSkTUrNZCi9uEkxgWU1LACq2JhwkP9wAs'
        b'jZAznWt2hpIBIcA3zq4cLJt4QhTiIFU++f3yUw7wXAMtbuGbTd5P4Y05lAt5JgQSQun0HQAC1DYhlEWhLD2UTaFsPdSPQv30UCaFMvVQN6OeFOpOoe56qC+F+uqh/hTq'
        b'r4d6UKiHHupDoT56qCeFeuqh3hTqrYd6RfsNQxkUysBQTQJsDgWI3ge4FgSbCASgraGrQvHQ4sRA4hbB91BAoqsFrzRXuuJcgTyg72vQpLjemq4c6glCf6bgHINcRTL+'
        b'IGHPI/Cm93kBCd8HJEPhv9VceNL/lXWbU/gvADv+5+HTSIRPO1vhE8opClbdULZZdBKkSpZILRl/f5Gs+BXtsKJli2SzwMHb1n9B4JL1Z/ufJAeqMaO5L4eQLNoBjjn5'
        b'Tn//JSU7xEQ+WbTi+el3kskhIq3fBtIZ+l4E6Zj1S4BlQEaHrDqkM4e4GEgnhky0vQMCE7IBAQAQjkmDGyZVdJcAHc2H/74nA+rgQ2bDFADrYBE7pF2jbEajDmOjJFgy'
        b'iIsIAKCTWUPWkugn4AUmaGQimvuk91KAYkIT40Nm3KuhKxIAZMUjAMcQirmH7Jv785hrXCgZlyR2FoEz0QTgNmQbASjhmBgBdwB9AEQBzOPCxOdESEHC2uiRiNJGTeBc'
        b'oQNT/mdn8mmzbqOSozmM2k6Sxc73EFHLp5uIs8nedjbZYzteRiQTEMJQAiLA0Y6X9I4fQB3fBdAy0ZdPXzCchmGysT8JZpgDdX7pm31zN+o61Ie3pJOmAYbadDIgdSFL'
        b'Buq2SrCjLAyIvvUGqs1j7hIgjrj/mpQ30cskQlPYuUywy8AgNltW2ZHpQNp6qRLn5+rsyi+YmRzmJZPSpGMOS7cREe4MJgIBnhrsWmPR3eFYY0qxInSHeqSF4vGdkZrt'
        b'e4BN2GBVsXqa8BrN3YYsD0o5A1LCO/hii6aM1gEQ1OxW394dKedETfNGfTMiNQINhg4mFxJoIwI9+KDJyoZ8xEx1RX/DOFaOGBH8VUoEacj3+R9tuCPirPW5GqpqXMsV'
        b'FMpWBEtUc0bSTTrSPMvhiUz/h3yFZPwrgf7Xzbo6lLFgEuHqoE0ABdbRZqUZ7QQJuBXYRTt5VnHyZptDTLfg22SLU2feJvM56Yzz0Iy5k7MN0bfSp7yA717Eyy/w8hKT'
        b'mkZTPT7ll6QisMpTW6X8Gz3WV/oXK78iZWt4cFeiKwflZVJ7qZWVbMoUqPKIWFkF9PziSh+qZEcsugWqiMVnPCzyNFRVenw58f+cLsuZ+y/Aff/fyz9yXIFzchMyHCI4'
        b'zwVBuvyowmlKpyMFPD5of5TBflIHP0eHb//xn1n/j4bNDjHZIonTh+Paq1mC1yyHJA7qgU9jJuK6FKxmIh4FgdpZhio1pzly4OCK5ey5XPqKrK9shGXpV5QNPNPXJdMD'
        b'7GzkeVp3k1dUuxvRGJOCB4h4UlJd2eRzu1yRVJfL19RIHEFkn6HCCryNc7UGlM/bWpCIUWwdU98gN3ncaGWOGRWVALAkCoAMdXRecysXr7/vI5ABXUPi7/8AgJbPNQ=='
    ))))

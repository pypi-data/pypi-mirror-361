
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
        b'eJzcvQlck0caOPxeOQjhEBARUKOiEkgALzyreHMGxRutJJBEAiFgDgUFRVEDcnrf94UHCt6325l2a7v2brdttt3tta22ttttt9uu223/M/MmIQE8ut9+3+//++DHy3vM'
        b'8czMc88zM59SHj+B6C8J/Vkq0UVLZVNa32xayxUwOlbH6egqporOFiymsoVagVa4ltKItCKtGP0Xl/lbRVZxFVVF09RcyjSOo3Q+hRJzKU1lS2hqeT+tj06S46uVoKuU'
        b'3PuRq79OsoaeS82ntD5an2zJAsk8ysTMQ08zKZ/FcunDSMmsfJ1sepk1v9gkm2owWXV5+bISTV6hZrFOcl+EgLwvxhcOXRx0XB7tbAeL/iTO/xYFutgpPa2ltcxacQVd'
        b'TVVRFcxyYTldRc2kypkqiqZW0itxvRSpl1XluTpEiP5GoL9gXBBHOmUmJe+jclDf48+zjLj6i6sElJhq1volqY2/ZBdQX/B5vx3fCR5STAKGh7FTdlbPumGinx4mV4He'
        b'MHEq22B0D9rAXt+ZSrgNNs2C1Yo5YB1cC6thbfyM5FnJMbAe1slhDaxjqcmzhfDsLLjHMHJbDm2JRVkrx8d+pf5SbdQ/UGcduPO5YlOMJlnzQH03NyQvX29kzq3pOfIt'
        b'ek2SaM5ft8gZa39c2Y65cb6o0FhcZIbNAs8oY+CGeIbqA85z8CysBIetfXG6E2A7PAJuweOgFjTCxjSUGtSDRhHlH8T2ToOHT1By1sFEy824k/iLD7o8DByrNxcv15lk'
        b'en7sxzn8NRaLzmzNybUZjFaDicF9gAeJ6iml/Wmz1JUVlcfpbaY8hygnx2wz5eQ4fHNy8ow6jclWkpMjZz1qwhc5bfbD9774ggsJxwX744LvBTJCmqGF5GobgJtzGl6X'
        b'pCniVMoYUJPp0algl41SDBXAE0ZQY8RQLM+6E/s6s8OXKvkd/e+wDy0LKYIwughryATuXiClXp3bO3P6JCfCfDSefD1eWEC/zdxLEMvUY3ZkjOKzDIplKI56L9qfUkun'
        b'TF3Av5yQJ6KkVPUKqUydvlRRStni0Uu4uwBs9QXNCnAb7kJgVcPGmQlZPA5ExymjYXV8TEoGTS1cIE4vgxvktK0PblOzdZyvKhesVcakKSXRcAM4C5o5Khzc5MCuKdNs'
        b'vUmawt54AOPBFXANNRvfiyjfTAZuCofn+SS1UeAIP8jgaLr3OHPPyllbCEo0bBHYmaaUp8qtGQJKOJMJlYNLtl449zZwCpxIQ0X3gethXUqKkqF8wQ4GNsOmfBvBpNXg'
        b'QAmszYQbUjPgSXgwDtakg1McFQSqWIRua4yoCjx0i9m5aSkKeBCcSVES5BRQ/nADq4rqZsNkM9kPnELfUwRLWIrjaLC/+zLSCxw8CC/z2JwBWsDtFFgvT0Glw80suJYR'
        b'i/oKgzkf3gLNaUOGoq9gbVYabMhMEVABfdkxYC88itJEYGoHm+BZnCYF7CvM4JP4wzPs4LIAlEKGx+kKqNT6JitgDWoQrEvDjQ2Be1iwAxyFx4RpqCWRONmFPvGwVqEC'
        b'bYigGlIUcULUJecZeB7uMpIE4DzcCTfHwoZ0RFg98hRyZaqACu7Nws1JUhumUtScs9a0TGVKLMLUmhRFanxccoYQ3Aa3KQUlgDvVoIqADI/AHfAShiW2fBxKEkdTvvAQ'
        b'Ay8Xj7XJ0fcUeBvsTiPfU1CLpkenIWpvgHUIv6YrhdQkTpiDKqj0ibL1w2Dd7DkJpa3JTJ8RnZwOG1TpmbNxMngoRjFaMGUWPOdmaIwnk91BuLWdRhyStXN2gV1oF9nF'
        b'dh+7xO5rl9r97P72AHugvZs9yB5sD7F3t4fae9jD7D3t4fYIe6S9l723vY9dZu9r72fvb4+yD7APtA+yR9vl9hh7rF1hV9rj7PH2BPtg+xD7UPsw+3B7on6EkwtT1Rzi'
        b'wjTiwhThwjThwogPO7nwWk8uHOBkEt5ceLWKcIgUP1iZpgCbwKHOTILnEPDoMjJ66uELCEmplHKlIhlUY2IJUrPgDDzA2bpjlATbclA/VjMI21iKWUUnwdsLbWFkvLrD'
        b'rbHgBNy9WJEsQAnX0rAKHp5o64E+yqaBg7HyAnhMCasR6gnBSSaWhUdIRlDdfT4emjDYoECDzKXQ4CY4BxsJcXKWnmmwZo4xHX/xoREuntDZeuJcdSsRqtXGl8CjyRgU'
        b'LplGz9fBPlsQ+ppdCNbGBkbEyRmKAZfo7EV6HsbN4BTckQZOjp6pSEGjLzQy0Yg53CAwgnPgemIa3DBVDhG/QNX1p0HLIJZ8WzgeNMDaYnAFYRuNimyg08ENcJxAAk9F'
        b'gb0YEW+CIwjBFDQlTGR6zIX1tlA8GPDos7GpEgRbXVomankS4z8A7CaFdgeNHMZfuNkQG61E2UqZwaBxNA/MWXgbDRrcA07ChmjUChM9Dp4eTIoEWxLAelgbAWviUzEw'
        b'O+ipK8FRMn6hcB/YTohCjglYjMjqoJgBdtgKa0h/JqIOqIW1osUZSA9hyunxA+EpvhVr4AUd4ndH4Ea4AX8D5+lZYAtcz3fcBXDMhFBoP7CrMJFxlDCckWSVEljhenAB'
        b'rIG1oHlIMmhBWSvoqeDwswRf0uFFcBHWMsMz4zCoG+hpNrCZZ/GHI8IQJ8GlxcaloN5RCage+eCWkBuCWnebAFUyeFFaLGb+qXiIfYRgxyIGbIVHi/IYJ95znVQZpMjY'
        b'abcqw1Qj5aWCRUTEECJiCRExK9lHqTJMJyJiVYa3vqviLGOxiLuk7P7yc35zJ1AyKZOUfarm+1GVq/74uiivNsDc90DUWr8BcH3G7kvz7S98M2cQ893KX4rFvt+PuzvY'
        b'f9qlSrnIihktsIPjK3mZFDwA1mfKYX0KL5VCB3BscIGVCK5WsG0On2gUHlBPwVURTLSdwVFwP6HVIIEiAyFRTXuqPmAjBzfmllpxPy9YANfidJmwJh/ezgQNOIUENqEB'
        b'BnvgHisWIVI08OtJInBkJZJhcaCG1MayfQOjrJivjAK3QGusMhkhZCuWVJQYXmDA2hXgOAFGN3IEgYVn+5jpY0gCgF1EDYgRZCJta59TD+qg6ZC3RM9xcEUaSyHjVnRW'
        b'imn+15+W0OZubk2Kc7Bai9XBWsx5ZpzQjFmfnPFQnhgzZgHmYLcGhTOvchdc5aVBYQSOR4oGrM2wLETYKKQ4BaJ7aAfXutaX43gkY/TMU2rL+U/WlhGKXW+ZxFmwTvHK'
        b'bcVXSMu9p76T+0CdnFeg13LnqnqOHEqNfofroWleIUfabjjBIyR0j6QpohH7S6MRqZ9i2MIy2ASOWTEniFarO2i38Ho8wZ+yFL4jma5HwWY1GNv12FWUOJA2h1Dteixb'
        b'nFvwiI6nzd3dfY6zVONisBFHVVIP/Tv2OjjgGxKrhMeysRxC7NZMg9t9YL2712nn30wXMOW81KNVPCjO2ny84fc3FecU5+ptljyN1VBsqsOZCbNgbIPQdTY4F4gZINwT'
        b'hzsnMzVWqVIpMASwkaViwXkB3BUOdj8BCP0TgPBxQaBr8qgfazWjwdbxSGEk1RZmYkIKglUsuAnPpXeNbkMwutEY4ZCBxv03KEd3iXKC9gQuHtrHXR/hoXbOXd+TuGin'
        b'+gK7QvGv3/0DZUlFL8LSx5z67Ev1A/U99Zd5Ur1aE62583nMObXW/EqzTq1tDvpSfUaTrz+ta9bk50oXV2uRbM9eP3q9eP3YY2LZmB2rzwsokOC3+sdSOU3YpX/RJAto'
        b'SVYhc4IfSbAN7qC6wSYWtD7DokEi6Ml15D0dUF+Qk6cx8rgv5XE/lEG8JxDxoOXhlnyD3pqjM5uLzXFjjcUopWVcHMngYkucxrzY4hAWLsP/PSikk3HHmLFsM4e7aQVL'
        b'2G0etPIgyJNWhqN3Y8GePkinhtXpsUh9I2Yt3IR0ihqkcKiQsAeXkGpTK6qYnTWKAhvG+8DLg+E5w/naAIEF68q6128XLs5fbFysylNp0jUFHzc/c0p3T31Scw/Z1xL9'
        b'R3dRkjbh2cq7LqR+qv7y9egTT47RPVBojmjnGLwp+5j+8DR2cb4tHl3xjVdXYP6IGnpG3FfXoTcYKgJc40DzSFDXNR11crv8RqbdWS/gVLMMB//iS1ui0JsPloSkod6s'
        b'XpysObOL21QnlyUG79B+oxbrP0oXUYvfE66SP5RzvGzf4AtbibBVKZQLbCpeZncDF1jQMGC0FQOaCa7nEnkapwT2ftHRqco40JCJWtwYmwJaonnpPC9HrNeCm9aBmKLg'
        b'MXCJl/Io0Rh43iNdONzKgTWgEVwn3o/ZQ5FJh8uWp6arwN5nMlKROcRrBVH9Bb2Se3jigMdo+9lMefkag0mnzdGV5nlSSR8hzf+aI9tH3cGiVB6jTrvGupd7rHHqfR5j'
        b'/ZnUc6xxry4A24dhM7EKrkF2bTIi7bq0DDTkiNaF1IDlgszZYKN7lFzD3cODjRGr7anZppdFxTn/vAddrDJi2Pv1F4u1UymZbtUrZca4s0N3CyZbbkYRWx9cKwRrYpUp'
        b'CE8vUtRyuFsAD9Hg4iTYQHwwa/O+D9gS0HdQwPSP6F/CBBWlvO9kY08Ke1RKWwPqlm+MyeNffpsWROFuSFhUMK9HLx/K0G+2RWApRW/GSaelabSaZl2z7nT+PXWJprql'
        b'WfclIugv1SZ9TNYpzcu5yZoC/doNg5kX+sVMLNhR+aW2YGdhWOGOc9+8sHr06mFV4h0qzVLqzXX6j6XryruPHp4+RZk06lhIqEho/LJyyOl/Si+mr5sh++Fj6fC656R7'
        b'DNRnA/uWZXyH+C0xvrZORGZZfSQ463Q3iEETUwxPsF3zjCdyEi5fY8knKCXjUWqQGDFe1y9RAhFSSMkdUkd6ezCXnt7Mpev6aT4ZwTqc+ZgH1n3gxWGwfaWfCW7D2uSe'
        b'DFIHEQ50R1bnYHDkMd5TuoP3lHksluk9sQw3WtoJy6QqYqzBRtCUBzezFNwFz1PxVDxojSCI8XA5R4mpyvnCJLWi/7IsHlteGYKsYKrVKKTUxqk2E2XG7Liri4POMaxr'
        b'nUJb1qOHv731ghLZJyAh8NuayW/svLj3eXnzS4KRqXFNzOhdsyXTDolNTXtern/hRNuUCy/ELv3H+O391tHB/h/8/Vr25KnzdRE/Rryhavto9Vq1/0DhqVkvHdJPfE7/'
        b'z6v/KXxunarlmuKdby6M77VrXebcZb+mnh33/X9a3un70/Pp/Rp8ata93/rP0J9+EL34bV9q1wC5L+FNNritjNdakWEE23K8baMJsI1YNAOyl1oUcjnckB6jTAHVnM0p'
        b'AWIWCMBt87PEolEOQkbkeRVoQXb7NaszgR+sZIchvCWlwEO9pzjrugRavU0scLO7laioN7hJaaWxcbAa1mC7HjQwyuVwmxU7VWCdEdYQRsqbX5nSjgYYrDYTWMAZ2Bob'
        b'C3aBE6nY/ZGODF1f0MbAvfAsOEeUdXi8/ypkBCti4OZceRxsRAop4ukybhE8n0M6Bh6DbeAakvDwJObxqDqetxM77hJoLLFiHSIH2et70gZFeNoEZbDRasVYHQA3Phub'
        b'L1cpU1DfMZRUzIrh2t5e+vtjjDNhiS3XaODZfhRPo6MZZJoFEcYfQnPoyptrEnQnQbQqpc0yDzrt7k2nXSgB7bYDznfVg0Rf8rLYMJPtnVUUG50BNyBbVYhM0VYkORlQ'
        b'CTbBy3lCJ2VhG9DfRVlxLNbcy+meVIWwWlQurKaqmApRuciiKvMvZwuocmEVXSGeS5lCOMpKF0rMI2kK/86nTKHzkL5bLsY5y4W4jLGUlsZ5m2gzVy4oyTZQFYLSQ+WC'
        b'AkTok6lnty1kKnwqJLiWcp8qxqwn9XHo7ky5sABpzhXCUj2640jqkArfahal9C1n9Gy5pIGmqSVbEByTSS4pglJa7UOgE5ZGVUuqxfi+iiY5xSSn2CPnq3Opcqn5u2op'
        b'n8MF73RqiX4u1cSYokipvlUMgl1RTVdThUJ8h6ARaJkqmk/dRJt+Juloq1DPkLRzqn2daedUM7hsd8o3SUohSVVeLXCmQndeqU5r2QKRltMK1iKbcDKFW1DhpxUWiMr9'
        b'CsR40g5P5VX4lfuhvK1an3K/UKrCzy6y+yKNjdVKUD5xOYvzVfijHvCvorXiQlzjn8v9tb5oZPxN/dzvOfT+Z60U14jfhOKvnNavwr+caWLMUxG8NIGXMUdp/ctRjh6I'
        b'ResZlC7AJCuny5lCFn0bqw3A9873Ym1gOX/XzyO/WtuNz+9Og2sLKA/QBo3A//1QmoZyf3IN0AaX+5f74fLwN5N/eQD+UrKj3A8/W/kxDkStCEStCEGtYMwPywNx67Th'
        b'qE8Z88v8E8rzGbpD+KiNIO8/4Z/we9TKbtoe6JnShq1jelLl3Qj8gaj2ntV+uIYCSXmgC4Zytok1y6x0eUAVvYY2ia2+/J1TSEWqZj0UGZERbVIOfsgoZG75xzhlIDGJ'
        b'sZhajEjrWUkFXU4XUBuZJRxWn51KpEOck2PSFOlycuSMg4lLcNDWDrbyQ8lYo8FizSsuKhn3E+U0loXU8si8fF1eITKl2q2t9oQPWVmx+SGtuE+TEor1MmtZiU42wOIF'
        b'pMBF/TIXkKF4urUcC2jGwlUjgKtoJ8CL28FCLDGKSMmlj2GIZqx1/9wO731c6cMAjWypxmjTyRBE0QMsciJuH4ZZdEtsOlOeTmaw6opkAwz486ABlkEPu5EX+Nb9iiPX'
        b'YI+UrtwPfWRFNotVlquTPQzQGaz5OjNqMeoIdL2POeVDetBDut9DnwGWBXFxcc+it1izeNhNIVtcbHX10Gj0h1qIjUpzIt/a9nupQ2AwaXWlDskc3Iwp2LJDrxAsFgeX'
        b'V1xS5uAKdWXIyEXwFGt1Dp/cMqtOYzZr0IeCYoPJITRbSowGq4Mz60rMZuwZdPjMQhWTkuRBDp+8YpMVGxFmB4tKcnAYORxC0mkWhwDDaHGILbZc/k5APuAXBqsm16hz'
        b'0AYHiz45hBY+AV3oEBssOVZbCfrIWS1Ws4Nbiq9skWUxyo7BcAiW2IqtOrlfl0rob7kgIZXilohiF4K+QjkjFCgGSz+OxnLRnxayWBrycjHIqcf606GMhDxjiUmkJROK'
        b'nsKRVhtKBwpDiDwVo3vs9PSnAxmcX0ry+zNYqvozOBd6w/iT8sLoSFRWKJa5vIMJycR9CnAQnMEGUwZsUClSkU6Tw44qWOV2mos9ieNLdEEijCn9czlVQBGh9CYSYWwF'
        b'V85aIpf4W5EWi/8MSOztYSsE5YJyppwdi8jInIUEI10oRP+R+OhJFTCIZbI9SdQFEk0cEgccFiAWfTm3mK7gSueVc6j06UgEs1i8IJG4r5qIXpQflyjQcqgUFj+h/xwf'
        b'v7HEyIsc80ktV3Jai8W2oFxEahPy3+dSSNwQCEhJzFj+mXM+c2OpJf5IMDLE3S9QIapOxqNIhhK7o/jHVNc7ucCMXf0O1qKzOliNVusQ2kq0GqvOPA5/FTtEGPeKNCUO'
        b'sVan19iMVoSy+JXWkGc1T3MV6BDrSkt0eVad1pyG303FmYVPwDIPPyYOKdDmuMrtjRibZSBBMg6hA0ayQB4RMKoR9JLSYUwgeg5ECMEHBtyygANpMcxCPNuXAmriwQkF'
        b'QokaPJcWCy4L4DZQ7+NlieCaMRKRmjpNelJ42lPv6zJzymnX/ImnZSR24ZUWXarxKNM1SOgXUCWBCMtQJvMwhBd+6A2NRWkV7YtMHiKsSDwPYtBstS++r8ExKRwCAlct'
        b'QaBI9WK3O9KnnMH409GawuwWO/uJJ/MBBoArx1oDVdZcughVy5ZTTu1JVcGgIlgMWBVdiNgfvitHYFSwphACnBAhdjK+Q2+Y6UgHJG/CqrFWgwhAj54xshO9K2wuVTqx'
        b'HJc7uoItJ6WitBuqhQhJWVQ/Z5Lie/SePJVz5hIsfRD5oHLKOVJGyVwcqhSH9E/OKtAzSAf9M400S5pa7o86SoAlMwlNQr8VgpUCPjQJkQbquAZ+JGgVwi9s6DpESzVm'
        b'4o1kFyMcRlzUXLjMPAbj1mQeC9sdkBn4QpB2EUF6ndksFz81V2zHV2kO4YclqOIiywQ3tiIcZRiMo1LMABkGPYcxBFsZKcLiMISr4fTyBE1enq7EammX9VpdXrFZY/V2'
        b'trZXgKTWQlw1bofLw0heYKyT+/63/J11iHC3IbLli3zW3TwfN0AjaddEEsuz+96I9Yb3XB7+6Da41IoFuDg9vpf8V8JngRsckbOy4bTTbUCxsv68++lmf7AL3uiRlq5S'
        b'KaPlQso3joFH4G6PAAeXCMA/ljnooqOykdaXzRB6F7ocGdnsFjHv2kAk6KNHTFnLrRVX0dmc+z3mDSLEE0QkAA9/E9gpjsoWEsIUObo5g+SmGoy69GKNVmfueuKWeOsY'
        b'VBxiOh6TDuzTTzq42E+nKLShuE9OgxNLLeAyPANaopMz4lIyZmCLPjM9RZkFqzNnRmPGSMJBwBrY7DMfHOxveM7xNmPBDP+tkT9/pX6g/lKdr4/ZFo1j0FRL1Hf4KLTc'
        b'B+pXc1/O/Ub9cm6BXqulTmoaFqdoxMShrlT4hiz4VS7gQ9MaYQN2SMA6JQ54WuJ0SEwFm8NtHPpwDTYQV0HQdJPnrN3AdLdHohZutRLWnGxwzubiWdoSsMM1USudQVwW'
        b'Q0MzY+OWKJM9JmmRSnDROgl9W1EgBLXL3CEzJNAnBV7kewJswPXGww3psBHWofpBDWxE3JlCCXb6gS3F8CBokzsnO57ADJDWbzAZrDk5nm7iVVQ+1mL86eXhndAizpXB'
        b'PZli0Rn1DqGRfH38ZEohvi9w1W02oMtiTBbYAUBVot/dnh6+x1XeNXIm8sjJIlzHMlGoF7oRlHv62IKuZ+FEKj7S7JI5uT2UCTaBg0KW8gcn2cCR4KANUwc83i0Kz1uS'
        b'wMn2oCeExs4IgotZYDNcT1ELo0VwCzwIz9pwEKVuGrzMZ4uORhiXrIQbwIlZ0akZsFERl6JMzaCpFD9TgM8z4c/aML8GlfB895nK8dI5ybBOnpqRjlI7SQUlHQa2CaPm'
        b'wBOG8D+GCyzY/lP/7r2v1C/lNuuaNXdy0zVGvWKbXJOqOakJXMyTR8wfqe92TngQvt7/j8ZL/SJk3/y8/+j6CVJFDvjgudef++DulhfefO7Nu2F3f7fTn3qvLGiCrRZR'
        b'DMbjQYiLnYS1aSRYbsU8rjcNDo1AeCzDUFYhcjhLHGZObxlYD27xHjNwCLQS/56JRgTfkeAQtY0Hq8H6EeOITwzuA5emx8Ypy0qSlQwlBEeYBNA8gnjcYoAdrE+LS81Q'
        b'pIB62Bgd5uxoATVgmiAbHl/qmtF4epXOL8+sQ2pkTlGx1mbUEdIIcZHGEuI0Y3ijQEov79MZS71yu+gQ4z0iFiyx2olE8GghwvCUUuQmFyPpKk9y2RLqSS5PAqRrmhnr'
        b'ohmX9ogpR6z3eUrK0XeciHFbK27K8VeRCM8lC4Z5Eg5LgWvgFKEccA2u4bn/NlBp8KYdUAUvd6IfF+1Ugls2PAk3OiCfzwXr4LlHkg8mnu7GR8cLaDsELThofcdoAfFY'
        b'o6YoV6sZtw6PAy7FNgsj5yFkgD2CWcNNaaAlOQM0wNZS4izHbYBbvWaE2SFBFrA5Kwi24BDh9d1AZYiWD/VsA+dmOF3fdbBWwbuSYZPUP4sdDC8muhsjoDwCAwgb5DVy'
        b'Bg+qmw2yRE5zaDBZMpgcGUx2Jfeo4ADfrtjgKDxSF8Cu/mmxsD4tjp/Hn5kci4RX42xEwko5bEhPmd0+YOtKBRQ4oJPAWxXLyfyHdKmgXygbSFFJamOWIImyKdHLESUS'
        b'rwL5wGMk9PnAD8zVilb5+MN9YeBYsA3P5vivzE1LwzONSEuIhjVzefY3w1UxOAwPpsxGuALbRPAs3BFvuBP2d4EFC6G/tPyDev6U9T7SBu6pX9LHBck1mCViNqgwf6l+'
        b'BWkKr+amaDZp7+S26O4lffJOAjV7DD17aNUs+9DP5K0JW1p1lu5HE4ZUyqavP1o1ZQ8dFfFS04sh9NsfYlb5ImaSNPXO6LDT3W7LRYRJjYLVYKN7wgR3ixKZ/u4Jk5QJ'
        b'hF0Ww3OddI+INMIMwfqJ4LoVB8j2GgS3IHbXF5xxcjwvfgduIfUD0xu8DlcPdU40Z6b0WsFX5gfPsWGwLppMZkyHF2xpSN3BSXwmwMbYOKSFBq1kYV3EfKLCFCChBJoo'
        b'Vxo8f+g7gkFG6sH+BF64LwGe4eM5wGWjK6TDGc5hAzt/O+f1x3EaOSXmYisxyAnrDXex3lVUEEO8MxwdiEwVKZnVWD68M9/TlerynFyvXcn3LpkncgFvPbQbWU+an3RO'
        b'Y/q5MxDWXIIujbRLSlSS3+89mbMNmzwzwDXVk9nEI3jEcHAFB5NvGgXbBFPg1SRwcQA4Iaf6wa0hBaBuqhFDN9EvjPtHEJX0bXAZHTH1ucHKbr9QZCr73ugddKuIkiUY'
        b'fhj9gXldopJ/XTIOz3DT0d8GVvf8Jcy/x1rKsPL5fYwFT/X//gVw5uCAujF4vnHyMuOL+9cGyf1EH4V9sJpdm6uLemvjliXB0757s0QfOeOVzOLnBzxsms4cVt9SbNj6'
        b'erIg4vlX3932w8fvl1zefCUlfqrsVvPbNbFJX/XOLj9XZFmVsVJSnv+r+W93rMdPFs498TD/vba/VJhmhQ8JH3P6Qr+JdWvXxJ/LVuX6jtxT8++N50zXg64X9DaFzJ5x'
        b'4NPBY1fFnoj5ZfQ9uR9RwofDS307rgzRFRMt/HgkQfHZ8BLjqX5g1QPuhBe5Rb35+M3ZKX3dBDcx2kP7QIRoF5EYD9AQxq9ZyHQPHqhG41QDz4Njmek8U07UCp/Nha1E'
        b'WQEnpoPDscaCOKVbWYE35xDzAh6F18e2D/UJsMNNvRHDOVTJxfHWKSidBtxY+F9YAMFwMzECkFp5E6wls59L4W24xsl53JlFVHe4GiW5wMIL8BjYR3oTbisEe/lgFgwe'
        b'TjUBtPjPZqPBIS2JJug9ACWvhTWTwAFcEg5bPsqUIp7CK3tbkWJb62Hz4BKQXMM2D+qq7TzLqFpW0lmiXRcQibYWrLbiyUV4GjRNgrXpNEWPBIemUrChG1z9CIr0+a22'
        b'udDNbHw9+AThNNEuTrPSreQxOKyMw/5idMcxQQFCdA1kAunlvR7Ld7zUPqHzXTt3ET0NrIzZTHlZTEvQZYWXCmiP9FQBHw8SqpT4+SU5zhc5OQ5pTs4Sm8bIz/wQi4zo'
        b'maQmhx9e+aSxWPJ0iHM6Db7/yh/i8HGWhEohDclHFx3tVLzETKAozI9ocrBmKNzYziNB7TRvxGeo0eCmEOxEL297eRRcc8mWGKrdS6JjtbwSRJGITEbLrvXBXhHi+RAQ'
        b'bU/g9nxM11hRv5lQn6nyOI9S3ZrySHRxaslOj6te5FSsuGoRUqwESLHiiGIlIIoVh31/ncOVsGLVOVxJxGvJangY3vbSk8GOAt7A7AkPkyQlqTkoQZiPOwkSz7CGo8In'
        b'c8nPzCN642JwAxxDibLgGXeq2JhkIRVu4WbD+nA5QwL0VoKDvXFdlfBmV4XNVJLCgL3vKAIRdk53LEwHNht0A/JYC/bHX5+8AduYydi6PBejeaB+oDbpX879Un1f/bW6'
        b'UH8G2Z7RQ75Sp2he0oveTFoUahma5zdp7PurLX6TEiZJAi16iuohCji9+ndyjg/8OAO2wZuEfYMT8IZXvEUOvESszxLYBjfF8pw2FW4gzLYb3MaHloA1g3NEBPY0UENW'
        b'L1FBOhbp2LVwN2FoaWqwhV9sRLhZFryAGRo4XubSXJ6GTj3DifUIg3KwkUf4SZCLn6yiFBJpCM2xYgaZjBGdUC7OnY+nMqGDzTNaHGK9zUho08GVoLQOoVVjXqyzPlFL'
        b'4cxl+H45vqzAl3I3C8ExaSc6qCrvh3kykcdBJ2dU2HWN2YgZ2z9mK+GjhLaLdNb8Yi2pwGxzdUtX4SNL3cAsQ5fjLsco9jmTyO9FM6a1swAku66KvRe7jZEJwfExHDEl'
        b'3prMEmJK0P+b/oixUV6TJN6k6zVN4iZdikQaPuXaLcwPOttE4Sri+AFXEDJZkDJxwXeJDV5CKsJl2GZdCi/6LgU4MHJ/QIkUtlHUM/CYALYiqbzH9gxG8gawB5xF2WrS'
        b'VbA+VjWbGL4p6F9NpnIOrB4hIPYwaIHVijjQlkWcnxfANQm8LZjy2IXCLInJ+C+jaDtzKAHvAYMnYcvCWNCc7h4iigqPDJ7FwlqBhKwXilwyBtNUukrfEzeIrDWLpqlw'
        b'sJEzwwsKw9j9n1KWdNyVN5/9Sv3yF18iMyxff0/7pToGGV93c+8y53b1XF0euPtqlXzd4HUndvaM+stzTa8s0r77XNMLzIRPs5678/pzIXebQCCxs3Zd6TZxZYtcwK+1'
        b'qIyDtciOwSujkJi4irSv08xQsBbRO+YWCfBweGwyYSJwF6zmRtDgDKiaQ1TF3vBkf7LgoCYGaVZKPlUAWM0WBGWSsv2gHQ1ULbZz8XK8XMQnR9GgTQwOEl4yEOk+t92r'
        b'POA6CwnqCoJHn7iexldTUqJDFIZp3NvZtIqagSdfpGQKUUIvj0HUn2M05OlMFl2O3lxclKM3eNo4HgW5aiX0/9hwrhVuelyJLq91YA7nvUK6Mimy/K5ZkZapxEqnC2tB'
        b'fSZxAKD/GC+K4fGOBgzc7OwbxIn5vtWCfYFFRdn8orbbS2bGDoHncNcOTWQoAdxHIyw/lEVEUMwiUIsopG3ZUnhhiVRcskS6hKPAsTGhY9jFSOPdSJarzkLC7qoFKaht'
        b'Pn5L/ST+YnguqNcyTI9LBFRUEFehDuAXxtYiK3ttGo7hI+OYCK6IQSsD1otAiw1PvcF93X3BKVTuZdS6mFQFOAm3LFNEY/dCumsFykyxc0U0TYEjg8BacN530lS4gThH'
        b'tIj4dz599rPFYJtRAtctz7dh5QVnRMp3bckS0LgMXoKXEUuxgkawy4gKbIWXbagxMzmwOs7EL9I9BG8jBoLAzYDNcDsW38gYqk0X4TBCNgs0g0M2rNYizX4twvWOxXKw'
        b'aRlsk0qEVFQKBzbIZxL1mCwIBLfBZaTSn2eIG/f6GGoM3MKvUUZC/xm4OVOZEoSYwTZwNjlFREmfYeA+axbZSwA2gW0Rvkq8YBC0WtLm8k33YG7gImFjz8LVInCjHzhi'
        b'w1PBsRXg7ExUO7jsE0VFgRM6wuD/muVDBYYlIs1ILc0omM4H0AauRBVG3xZSMrUiWNmHf/lvKRIFsnWIX6mlH48fShGm7AP25GP7TrckFruKaoh7qEtgikGluGI0rJIz'
        b'pDTHHIbiFKQ0xaTUeXwV70bgdfMIPWXq9D2TIygD99KznGUiopgvj/tlNN1UwYSQda/ZftmVqLwdk7tY+xE9ZE5d9f6+CuNcpfnv3xxNztgu9Z9U37zzTv+Ewd/LpGOp'
        b'17I0gwzvvPTFT+Xjrr079AZcG7Rpx7DZ06PPtPR4c2bJrTduvfWHt38aoj6YcKmh6Uc/bXP4zdDC0/DEi73/ffbmhvSo/v6fH5on/9IxKaPhg381/1D2Ruszf1g5fGfT'
        b'Mw2XFT9GfK7/saD13U/uHPnhr1O2B5QdWVf3r6S3uMyaD+0Onx6rdn41xrp8feqWYuG20vf/0jq1rW3MP/+Vf/2wzwf/ebH5uy2DROFb969eYl8x9lD61vjgr7PPnEwS'
        b'mPMtKwY2G0a1rXz+xUubN3yxKzR4wIMcwZm3rkovN7e9p03YF7TrJ22c4l8nuP37Jv0+XHX0zltx43fbE39Vxi+78bV85cLYw4X/ebVp0PrSD1S3+w3oHZj5K22zWI9e'
        b'jJAHEJ1tJDiKtM36WCQWj+BFpxuwQ8kXnmMZeGOpFUukWNg6FXEfRDmNfZil9AR4iZ9Pg7d6FcUmw+ORhLkQ1g6Pw82EdU+AlyempceAltA4nvf4Ghl4BGmXLcTPxWIL'
        b'GS+WJwghoKAdXhLDWqbCOpAAhSgbbo/NVIALJegO6yEiBNMtBl4eBw+RgF5YL4Ab3MxfMo3w/kRQR4oH68D2nrGwOkWhDUlB0hxuEFABY1m9Emwj33tFz0nD851g5zRU'
        b'tFypQkpOj3QuqT8qHEMvRJZ6TSyCcJ1XfDM4PJCP8b8FWxgMVSlch0hfRHFKGrRkocykW3bA9T1iU2ElqMpABjXXlwZ74dkKPlj5ANgEW/mo6YoemDch7pSGiKEHuMQl'
        b'g0Yl786oj5oUWzCBF6q8QF0AdxDIl6gTsHpeDLbHeEdDn9Q+yen3dCawp7nevUvhRwRmVrvAnIbFJUfCmgMZCRMoQX9MEI2vEjYQvQvHyxOQaS8hwV8SEpcjJmFeSMgy'
        b'/iQGIpAOYqSMeZVLTiNT/LfZ7h7xh7iQFzoI1ZueGjdxZqcmIIvNS6bCuvkdxSpCzUVWMdhKQaSWkuXe/ggrTuPJt9MVZP6NzL4thjVEVZsH9qfhtfKwVgVa0p3+W3CR'
        b'gUdj4AXC4/MzM2OV4Cg4olLGCNHQHmCGTlXmsU4dEM8qhLr0QBx+0GlnBcq9twLttbsCY++uD3XPOggeOevAkikk7uMoNIoSmcdPlm6xwWLVmS0ya76u4w4+cRKvtClW'
        b'mcEiM+uW2AxmnVZmLZZhVy/KiN7irVzw6lJZMY7qzNXpi806mcZUJrPYcnkniFdReRoTjto0FJUUm606bZxsrgEZNTarjISLGrQyJ/oRqFxlow/WMgSCV0lmncVqNmBP'
        b'cwdoR5O4GBm26kbL8C5F+A5Hj+IincWjFnaRpVBXhmM5+VzOhw4ZtbKlqM8QTF0WYLOgj3x2d/opE1MmzSRfZAatRRY9S2cwmnT5RTqzMmWyRe5djrO3XcGtGhluo2kx'
        b'jmzVyHDMLwbHVVacTFWMOq6kBNWFQ0I7lWTQk1x8h6KxytVggNBYobGx5JkNJdZODfFyorjXDLhNFF+VDZt64MZgcHpmvGvyL2tuMlJBwQF4aWZyqiBr1ChwQi6BV8tG'
        b'ga1J/UZ1R+oKbJb2TILVXojvXhib6o34lBP1aTfqM/YAfeBTTrF5mZOYR8g6NUKh6tqqc0c3OH1Q7mm937RYrmvvE6cifNZwpKEHY8GzGa0a9iu18vPkPLH+nvq+ukj/'
        b'QJ2SR228nzSkXr67JflUVbfWmqg/v7TrxT8+t8v/SKxx9I7RYUm5r9TFSdtGX1TvHS7dpK6QJ71hfPVQdGuN+g3Fen3CH9YffD0u8s7LuUa9WntPLdyJzLf3Gerre72X'
        b'vQblDHH8RsG2SbHK6GRpFHGc72KU8IyYF0J1/mAP0gqwyjwJ7uFsNKyZvPC3TzAJcpaZNSVEaPRuFxqrqAEcCXKTII7Mx/yG4MXEcrOTD3kEtzkx1uMNLtFlbpEI0nZZ'
        b'8SQhSPMZiKBYjS79EGSW0HZBUUl95DWPNB59gevggVCwH1yLdWF4FyuM202zKUHy+FQkuKeC5gBDd7D3MYFdLHGSPP1qcq/ZfwHV1ey/SGXDkYzw1HRYNTRh2JDEwcOH'
        b'Irui1Wo1L11isxCb5gKy+y7BNngRng8QSyWFy/19/HyRyVMN6hhkXsHLPrAFWfVEBa+NT8XLjsWt3fNiHKNoXi8vzUmmmpB13zR2uaSht4BfPGf4YraBs+Sguz/O/Hf3'
        b'Fw8GJSWFCF5f8Zdbh3Y/dzZ5zQFfSZF959ZksMLwh5WJb+4Mvj/yo/JjQRtC9D3bfjh1pTQ6oWbTX4f+nFgyvP7jt1f8tOWf44Olx3oNqTm1KHD4GztGHXbk9GwKgUff'
        b'K61HuEvUsGPg5CivXR7ApgllY8ExosMN1CPz1OU7gFvAKYo4D4ph9eOCQJ4cvmUutubkYosZdXqYJ0IP5QgSh5A4lSB6ueKpUNlZnGv2wh0P/fjALpKiHZHXoEtCJ0R+'
        b'02v55kT0ZQ7cYX5aHIZ7aKR/xoOazCGJLLUU1AbGwUp+3zOJhSG4/NGCImOJzyCK7NQ1MMmKiriOVW0qjopDBe4niU/1wyYcFZjUK0+hE03l8SdDildpUrImydL0D3tM'
        b'5fGHfOlf6oMlQUJgYZn098VJ/MvZhTwOJq20FGydOZt/mWYIxMx8ZIJxubGoLI3ifQ2b+4BtM2FDGayHW2YPT4AbOEqYRYPTGeAMvz1bUjg1DBX1eumKcpVCzRe1f34b'
        b'na6iRahJy+aNvDKVaHqhkvSZAJeCTA2kwZ+hWDU9DlYvIbsOhIPD4AbvdOMtW2ROwGpFKnYgYtMCWb0VPRAMjbFYQ0fGhES+cCWZAwZlQioSi6GpRuOo+Dtj3qKMOArw'
        b'7zMGicXzqYRjA64u2RYxMnpxxJ+WpaZHCm0YBZJ8noHn1VhKZVAZEWIC8xcFYygrasi3Geqg3ssn8g35QDGe2lHkT1PTK83vKf/Rg7wcphlPlWMzwd+UJS4azad82U9J'
        b'vx7xe46SVVp2+GSnk5e/6N6lx84tFFGBq4vnRSeYycsV1FR6JBOHhnV14bzpQ4vJS0Fhd9oarUdYUFnxXtSFkeRlcYaNes/8CQKzcum8IPkw8rJP8my6maGS1WW5hWcG'
        b'avnafylvotXPzBBS6srF85JK/chL2dJ51JaxVhqBtPy9aMADPz+rPz05aj9HlVRWhC383WDyMrSwD1XXo55CzSzfofj7GPIytjiD/mnCJAHKXhg2v+VZ8nL3wlBawVCB'
        b'MqPlmdtTVHztBVGv0wdYqiQpxBZfO8MJkjX4eaoa1R3Yy2rYoX2Wf5k7vIL6iaKiE9JWJcY/M8HZdd0/pK7QVPSBvqZRYxknNpZr/SiENdGtMQXSz1OdS9fHjFpC1c0S'
        b'IK3io9y3B91dYQg9KxZYmlEHrY6fMDsro/jthMBejV+PfP/DY3+N/ZPi9YkHBb/Q9t7/opOfCYm6cuB4ZJBBcF38xsujrkZ/c/TljcG3N+yHq/9uWre23wr9okV/vlHT'
        b'q/a1zfm6rV9J3m5SVExl/d7/aP39hIilu6SS8q0/+gyHpsMHNUfmHL7203156IRne7RVtty/1nRty7Ut+QMc+cF/DjpX9E7MlQPLVfMPLEr7LGnDDccQ3Wsjrp8yqFYH'
        b'L0+Nzq44tfjGdz57K1eWKKXpbO0icL1wXdX7q678M9w0wXC2+mhO8aFvRw89+cOtb2dPk9dKLn1alBistVF/+uqvogd3tv91TeuYzHDdlDtfvF0yIHXRsDnbNy4Ibr74'
        b'3uYTp99defj8w5DvE+HeA9ohK/70tz99XpR1O/3LJUH1P3XffqV2xYQf5799pVHUnPDiuALFt4GN34aJRj4fPPaFjXf/eXfovj/cHhc6YtCfP5oy88Xvevxl+t827f+h'
        b'uPq8JXtf2MMvr9X84+Hh6GcOPRNsV32SVvP+iuzvxjy8VT3zhuRLvwrFv8cW7H/19/U/Dxg/aH/Zu/c3vnt2RM///OHunVMzX39/23NZN7cGy2+qRgz6+IV3cg7UNFQN'
        b'+0kuJqJGCA+oXGudkSxp5v0Bs8ApXolaENMLXoiF1fF4c7CD9HRwDF4kvoCp/UpiRRNSlWnKGJWAkgoZeBMeAFuIB0OZCLYJ2Xb3NhFP4LzTt7IWbpqGeEdmCjjNjQVH'
        b'8H5s/SazJOPEoRGxcfJUfvfDRESYAbCSLY4ZwscU3BgIa2JBEzJgFR1cJzMTSUBABNgObsWBnd7bwjhjiCRg/2+d4A/87RPUT608il0Sk4jbhZ7itq8UrxDzD5RwtOd2'
        b'WPh/b/Q/DP0G0QOR9IukheSLBGuZbBAdSoS0kOyXICYuCX+UA7snloc/WmS7wpfwehCHyGkMOgTEwvOQ1f+DlXSseS2+JwtP1rlFfBW69Ook4v8a4yniR6Mv+eA02O+U'
        b'8cAOzz1BzgvwpmtI3bsxMYFsHQmvZYIWMtHk9t66XRkLwS4qHlwQwNNwUxCZeNLNhc3tE2kicJTEigbCdWxvuBFcIDxwV38yYVgaEqBOfyHbua/q39LxRrxUUt9ktSK3'
        b'QsG/7LaAaArzNsWo068kl1IGYfAtxnIAfylf1QtHRiVJJ39tHLc7Ayzr9smQPZUNofJXYgTdU6NXr5ny3QPbyL4DX9j84O/f/67+673MtJVD52yq2bgw9cSRbVOz599J'
        b'upWVeG7rh6+vU+xorP85ynq5/+lPjgdvSO6x+Zp286p7gtBxuz5bxI3wO9D02itfb520evjC6ICQsrOtjk97zNk5s2T//fE/Th1z5bU38hf9p+hDyd6vH2xZ/eqsgPHP'
        b'34z7/HYPuYhfynBMCLZ6bLOrjAEbFR7b7A6AJwg3SYZH4RoywX+bbfcfhoFGK15dOx6eF3oOEY44TMfzW+BmONjHFSMWsp/fPKEhYLZHwrIUVYaACophQXMxbCXewjJY'
        b'acQpxiW3+6P8wRl2cmEC+Y63v4OXQG38HHhdqVLCDelyIRUQyeYslpJQJrDOXw1qM526jXsvMKRYt0SAjRzSgfaDZpdJGPo/5wNPzSVcZOsdU4R/I3FEUfQ0KXFPMnhl'
        b'KRPK8DsxYK5gxvt8qDxpmyc+QnftVB38/3JbHkHzGDhRJ5r/d6InzRNEuAkb4GpwHKxzK/cMFZDI6sEhuMNrklng/G+R0u1RO1o6m9Uy2ZyWzRZouWwh+hOhP/FiKtsH'
        b'/ZdsYbdwWkE9v9MansrntEKtiKxp8tVJtWKtz1pKK9H61jPZfuhZSp79yLM/evYnzwHkOQA9B5LnbuQ5EJVIXJuozCBt8Fpxdjd3bbS7thBtd1JbEPomxr/a0Hq8Cxve'
        b'aLCHNox8C+7iW09tOPkW4nyO0EaiGro7n3ppe6OnUC1ZlC/v4/BP5zl9hsakWawzfyzq6CLFbjzvNDISh+GV6Ek5DBbsryNOU22ZSVNkwK7TMplGq8VOPbOuqHipzsNH'
        b'6F04yoQSYU+80wfJOwDdvkWSI0423ajTWHQyU7EV+001VpLYZsFbsXu5Ay04iUxnws5CrSy3TOZctBvn9PBq8qyGpRorLrik2EQcvjpco8lY5u0lnG3hHceoKo3Zw9dJ'
        b'PMLLNGXk7VKd2aA3oLe4kVYdajQqU6fJy3+EG9fZC85a40hnWs0ak0Wvw15nrcaqwUAaDUUGK9+hqJneDTTpi81FZLND2bJ8Q15+R7e1zWRAhSNIDFqdyWrQlzl7CikA'
        b'XgU97JVvtZZYRsfHa0oMcQXFxSaDJU6ri3dudv5woOuzHg1mriavsHOauLzFBhXe9aEEYcyyYrO2a68QMk355X5kRZVe8BQL/liynop7uK6z59hksBo0RsNyHRrLToho'
        b'slg1pryOvn384/ReuyDlHdjowbDYhPptwvQU96fO3uonxLQIVWTtAc0hnlULaxdOf8zyK7x+BGyCN8nyqwxwZJinXhKdrJi9KC4ONuKNfhPBduEKsAHucu7pPSVvQhpK'
        b'lKnEaxvqM2kqyBwJ9rBwNT3U8OLPZsaiQokeXOyOg+fufPEluipC76uTnSsS4uZEa1I1zPme53eM2bG75/l5u3qO3jlmx7l5Y3aszjXK795M76X4+wO59PyfyPZfxr6B'
        b'3+amIEOBqAAtgaCxXSgb4Wa3ACfCG+yO46Nyr8Mr4BxO6JbMYD2s5qUz3JNLwvHAHngZnPVFLZYjZSIjnw+V7g7snBiuAVeIMQDO2sCJWNiQPIyjWHDeBq/TJqTg8/OY'
        b'6T75uB9ANTiG+oIme5GB1fAq2MkbGQcD48EmcBXWpilFZOtmlBq0kKx4X1qwHhe8KHTYkOEsJVpOw11gG9I9cA8HRII6sH8laWl1RrqQQlohDa/CG+C8S5o+xUwdDn8l'
        b'MjvUU2avokKkZM0B1s6X9/DGW/eKRJVnwK+51ltgdx2lx/DJCrzq38C4HHmV7t+fQjzj8x4FQdcrm4gzgCrgY7xoFYnFdc0yIVWpwN0D7d1QjC47GecCp07VuZZAPez5'
        b'yMkrVAmrLc57IkBreYDEOU775THw7HHB8zDEY/rKNQsW98Sq9K6qMDc1aC2PqWq/uyoFrsqlzHUxV5ZnNCA+rbQgdi1/ahB8c3SlJQYzEQOPgeKQG4r+GIr2PFjSdOzy'
        b'9spd3LuHm3s7d4i1Czy49+O9+ms7bnvXeTUs4puYRsLgAXB9JqxH78FFSolosBGcLyT+V7AOngA3wSkabs+lqAqqQhZJAr1iQBU4DGtTiPY+lBuPuUAtkxqZYMhpbGMt'
        b'c1GS0Vd+UP7hD36VCdKqj0cqG+N+l3t6eveXhh45vnBI4sFPPsvc9kv0wZAXq+QDJx/5e8qYQ+euLPzq/ssFJ+SrV22NWLbdh21UZA57dVHkKeGfHs6cVGz4VFD359Dc'
        b'TevlEmLPMMjCbOlo0IBdcK2LJ8Ljw4hZtAycAdew8zQFO/SnL6XE8DoDanJzydeRsDrJ5ewHJ4OdO7gdAnv5uYBK2ArqiN0FV0fheXkVDVoLgZ1nZpeX9eQdLTPARrev'
        b'BbYgPoiZ2TBwPt2LkyXCaszM6uBJvvBmsANsS4MN8YgnbsKnbXCJNLgxIIgvvAm0FcTyy8qTwAXnynJkht8mn0tBtTINAc3z+MvggHNHyPXziREXuGQSrE0GLcm8vEKi'
        b'CpxCeTexcH1OvtcWdE/DURG96Ux55rISK2Grkd5sVS4l0RcSEtpI9u7txNqcub1461PtI+ncubedt+Jde492wVs/fDxvdQLwP9WO9F1qR5PyNabFOj7ewaXPuMi8g66E'
        b'VJ6nVZNMumVPox25tpTpOCuMFBg8S/pMGjjdQYMBe5LBLaTCJMLVhk1zVzAkPqRxWKLfy7FBlQmB3Bs7o36OnMtyI9MlbYuT3941gZo78FzOxfzp1j/PeKl5VUv+cx+f'
        b'Dswe8evnL09ME8RX9+rpOydyeuuZD29OutD3e5/UL3a0aa6tzBYEZ2xbL/fhEfsc3ArXuXQLpLEcgq1IudgJqnnnQc1wcHvufFCbiReRgpOKaJryh/WsLiaFhPeCakV2'
        b'J9SeOxkh9rLhRP1Q+a8CtfFI8aMpLh7pg1tocB6cGUd27YXbOWDnN7ZNywT14BJoik9WuPS9BHhAOApcjeN3otwDtiDm59JhQE0FnTYWniLa0aLR8jRX7YjskAJzEClA'
        b'Qwv49l2BbRRpHq/fgErQhnWcG5P49l2d/IybK8Cj4LRTxwG3h/92ugzII9iW40KNjlHH+He0hGwGE0Iv792BKjpk/l+oPvj0ltYuyPNNL/J8AiBy1iHML7ZYDVqHDyIG'
        b'qwmLeoeQF/ldL+ohJMy5F/QI3At6BI9c0OM0cD7GYZ+dKGqCVouNG0x2HtoCbwy6pfUjaZcHnqfcZHSfMtnFAXI1psLO9OsmeWdb+ZzT+UeUOTrNZkKmpDJlcheBPB5B'
        b'Qa6c2HDG2byCgORdwWvWWW1mk2W0TD3LbNOpcSwPv9mAViFTT9UYLfw7jRG91JYh9QXrUCbrE1iQTycWxKoMS7Y0sxYcly0VbvxK/WruPbLHi0F/RndPfQ89G/UPvjih'
        b'O625m3tScy9PrBdrxbnV0/epk+lzI4dSg77wjew5X84S6dYdtswEtQFgT0ceAQ/DQ0S2KsFuJO5cbGAUaI3Hh9Xsg1fJ0usEKVyflp4CajIz4Ib0ONAQT2I15UndQZ0A'
        b'tMC20b+dFP01Wm2OLteQZyG6KaHEQG9KTMN0uLxXB+T3zuckQiFPUzvxZRe+7PYmR0/wOI9kBe60hBz3osvNLsjxBS9yfDxE/1OCy0cEN60rgssiLipEcyYeyXA4mgfl'
        b'eTin/v9HezhbysxMGe9WsvJeKGIb6A0mjVGm1Rl1nWPono7qdrb4c4Tq9oYe/Oqdq09Ldx5U18OKqA77DYphPbzsKZfhGbjNSXfbnVHKKnASH5LjEr90jB84r4bXrTFY'
        b'8l2DDWBLbCoqpj4+DdRnZoATsNWTAMeDBlEQ2DHqt1NfN97F+QQCzCYE2EENi+uU9X9Lg/vR5W4XNHjJiwafCNRjzsah7ZTH2TiP3gvdpbTmdkF9BBUJmZhsRbmI4hD2'
        b'efiL272weTazGUkAY5mHRf3fIGbDhlzOgmNevjYvxcfv5OubCULe7YCQ/WWeKPkW/aGvjy1PjlCS+It6yzsqioPgblY3D5wh6Jgsj0PIWAxaXPiIhMBRsIfXBeuKzNj4'
        b'QrYjh2SFlyyIESJcvCqS6bI7nHPUJe7lFdtMVo+hsnSFe7nirnCvU1aVKwCx4NHIRnsoXAfR5U9dYNdx/8dhV6dq/0fYtRZhl+mR2NUeW/zUmCWLjsE6mMEkW5oYNyym'
        b'Cxb8ZEy7aBxLE0y7Ka17HKa58WzbJ25MK9AhTMNaPS0p6GSSzIT7dNYgEtYaDzdNcLI9zUoe0SzguBVPGgYFwAM4pEsRB2rmw4sd0GwksAuRfXIc7HwKTAvE/fckRCvg'
        b't7PqMOIdc/5WPDuMLp92gWf7vfDsSbXKe3RccyzKydEW5+XkOLgcm9no8MPXHNd8h8PXvU7EoDXX40z4eCfzJnzBh9YQV6tDXGIuLtGZrWUOsct3SSY+HSKnl9Ahafe7'
        b'EQ8CsVOIdkTYM6Ei0sT/enMED7efHV1sjDPSW+zLMTiC0/3LRPozJEyk05UJ8o30iwyIDPAXk91k4ZkByJY8D2smgwbexQUvZiDDFdmdDBUNVgtWzQE3vCZGMBEnUc4F'
        b'697zsHyUryPYuQTDOU5kl+iHsimleG9L7JTMw+srzCasfXloWyok37zHzXzE3eYOTs/T6PIV414LztFkNeQEE6zyWAze6nLauU6SSAVXFRIRaJRn2vBsNdwIzoBLTxdn'
        b'DLaBA5IuIo0VsNGLq7n9IriHnAH4lPf5ou1b7f6WZda48M4B0wEqPlZPK6FCcvG6JpnxPUX3UhKsGTdJREWqB4rQYEnfD3utYhZlxLvC/mvgWMH9sKuLf50SIb9aOD3n'
        b'ZJ/mwmvz1kTvUv1+5LD59Yq9mS1jjo5+ttdbMYdy/6N4mLHK7/MIv4obs1uj104anvqFqmzCx72F4ZLID+ZNzP503PWBe7LGz6rptSXmRp8FE+NTskrfDWgr/nqYg90Y'
        b'k1UyJPLo8M8n/1O7b/Z632GKq0xSN0u/MYIfRo0ZuSXtQb93ptxlZvpdW/Ur0vpLfVQcmf5K6o163OXxhS0hHO/yBXvgIdLU0QKW2lKG26dOF2kW8dE317sHUafz8MSY'
        b'OrJZEMG/nJoeSrXKFqE+US9MYYIpfte4jWFmWJsBziYq4/Bhsa6twGBjmgjhw4kyWDMFbBUMoMDagT7wIGiCTaSwTzUc9W1BEN6FTHF2hTOY8lqQkEo39sQ1KKaosvn9'
        b'Y89a38eDRh9YQNGvIhWCpNwe70u9l8YPUNjyv80gA7SHRgMU3SzgB+jF2An8AP3O8Mz/NQOU3l3uHKD8oH+wBmHPGtaCYzx6f7xvQP0Yf5ggnST/w79Gft074mb6316P'
        b'zTdfPnD45qxeby+YNjW0W2NI8tVl72mNu9f3j5ibPOvh+ReEOyXalUknNr/y+9R67UulL376r77zt976ZmHK+iN1vRUXDlgvvpe9d/3ZC7DU/uOpX9/8aWnG7281SX42'
        b'CV7+Rtn/1IPYEX6vhv088eHemcMHrPYZL+d4V1ijwuZyUqfDNuepReAIuMQvW9wDj4xxBzb1zM2weR0fPn4m0fGiOXg8VpmK90dCuCAoAK2UL7zGwMtjo4gzLsSGvsMN'
        b'MdgZJwQHwEWwixkFLgZ2DnD/b3cp9lzib7ZovHzh2J3gIXzLORISGEjWIAbSMgavSAykzWfcsoV1cDjGwEPk/tebJ9Pms262iyv4ZxfyuU7mGdaDncBSatbI2bExKlDn'
        b'oc5EgL0cODUGnuxaEfTYXdKDZbp3l/xN7NLroAg3u/Tj2eXvhvhSSGmSdWNlxh09N3Qj1DhylZCKDDnHs8t5kYMdPDXOiPm/gxp/7vX+lJO+PV3UWDErgDSlwshvaVJi'
        b'tkh3RsfyfOluUDA5YOyANC9y4rByyiyinCsU7k4isYuykpIS47hVGfzLt+OEZJVDSfAK6frcsRThw+BkDtiLGfEysIWffeMZMWwucfI0oCe9mNDAIaEjnh9FevF+N8TT'
        b'Sl9heZ4WkvmQ78W/Rf1f0otD/ujRiyWp60SGMSUL+H0e1z9/U/ky4Wns9JfvvnZ19RsXR7zcfRh3//MTk4b0FLy3YK78RnVgn4qbsupXbr1d+oVPH0l5+UcvPPyHoSrr'
        b'xynSvb6fxAnq38j4UP8GHCdffl2x7fMrt1snbLk46y8D/vUJ/dqvz4z47D+iUSt7LaytlNN8/MNJv55pKRlpSMvgj1t7ltGBa+Ckl3782yKaO3IRra6di0R5c5FVVADH'
        b'r2Um/ANzEinhK+bWdj7CE387G/nNG6i1Mw9cqph1bdFY6fH7MLIj+5CDzTOiwCWegaRkuPiHmgMHF8HtXmsi8QIUspNpPmIq1QL+YAB8Zg1mG1VMBUPuWS2H7tkmujTa'
        b'SuM0k6km+tnwhUwFV4EPEBBUU1YGn2qBFHz/ckEBqxWgcgRzKVNvvHV/ocRcwh8dRb7hQ30E88lW/aa75fjIoiRSBs5/rZw1N6FUxEVZegbdCcnpG7guYYWomi4X4YMG'
        b'tKJ6lKNcOJZasgvVsp7kF1Th44FY8+v4pAtcR6kJQSsgRxvg/OJO+cUovwPln0ry8wc2JblzR7tzRz4qdxONjzmoFvI50DskXVCZirnOQxacRzLlllNan56Y7fKT/hIV'
        b'kjA6XclUM96WaNZDgc2qV450nyyEMLgNjzn+aMax2Wa8YZtcZNZgzPTRmWxFOjM+eyMJPwvxlvpanUM622TAN8Rg4POO5ZGufc/N9mLJEQdkHdl0fMH7Yjvogt+6CZcU'
        b'n3VjGcKvTQ7H6DmaCCYxibrFJ7bw574EkeM4OLI8LszjTur8LyY7jIppG5bV4Di8CvalIaxNUSbG4L0QliBmilczyHpzsG0yPOEVAOIOmcBMoZyyiLX0TAqf40UGgCEH'
        b'YmDpRjrRPMxNnbSDtjzCiPcjzcqxFucYi02Lx7DO3fMoFpuHJCgNHokDxxGI80AzghI0xMMafttHrApTA8E6QVkv0NjpeCi3Xx4hBF1Im6XY6tOy5fi0LFrLFVD4JCYE'
        b'tSAUH9NC96Cw3MZvSBuEzjZggfSQGVBK1s7dZ/jGCJbrDUajnHHQJged/6iG4fbgdpEGTsQNkzgHjCNH7DitWtk07A6B1+BJ1B58hHkNPgYdD4iQGthbUAbr+z9m5TTd'
        b'5crpxx8A2WnltJDqvL61fbHgX+YvoT7CSwD7RyzcsWiYc9GVcyFXa8iEwNfSlfzLkcm8fE6Y+lZw0KhCyiBJC6Tx/nfUPc17X6lfIfthtZR8pd7g+6W6SG/VVF88qWvW'
        b'3FPf0ce/eR99P63B4YFfapUhJzV3cgv00aFrqpe2WhPeTRg29FhCCpVSvaGkKbr/nT0h+sEH8kMtkrSheQns4nBqYVXY/XN1SM8m+2yeNfrj5dbOxdbGAOVAuI6fbW4E'
        b'LfJY/hTEoWCb+yDEKeAgv67ngBwfvalQIYMcNhbNVtAowSkGnkEZj5MSyuEW0AROpZKFBTVIxV7J9IQ1/eAtUPvbV213KyrWjhrBnyuSozUsNlg77gzs3C1LTPOnLYnp'
        b'SNr8nJus/h+ty8bFpHUp5S57rc3G7Ao2zIH7UZPrM0HbMISew+L5w53wocC4p1A/jQTHhSvhMZsXv3AfWoydcjyXwOKuij8vhlE5BBpLnsGA4LpIuYVw56N/Rfm6UqNB'
        b'XzabdZ53RrFkHSqoyZxi05HwB7L/ETjFIWNoHQOvBQzsmm9hkY1P0CECMASHsGFoKpywEa8QozIDHorxHjA9Zp8zH5vJCV92O/fC6gnPYWuDwS18hrALSrgFniWQ4s3l'
        b'9o6EG5+6xzxhe2x/+eQmDuNPSNN49BhG8IR+sDJtyNAUYoUinlOPtbmAvuwYcArW/H/YZQhAXpTqO3QZpjE/sDoLA4l9Y8HTyHIaeIYdDFs8DsHlKI9DALEg1NKIqyMl'
        b'qrQfMiNirJjrs1UMUiaoCpY/FqycQTyeWSLBR3GVJJbT+IAu55FcjqiEwUOGDhueOGLkqAkTJ02eMnVackpqWnqGKnP6jKyZs2bPmTtvfjYvA7ByyisJNNIHDEsRDcs5'
        b'h5CfJ3II8vI1ZotDiHf9GJrIi36fjo0fmsiPThHrOp2ESDsh2aKHP0VtJ9wJVqcNSeT9BeMHkHHqwY4eKe56lKROdNG6TqVCY3LHzSho88uPQJShifw4LPNAFAzADHg0'
        b'H1fPbws9gx+EI2yCEq7uejNKcr457T7fHAHz2A0o9U9zvrkNz7iAw2C9xrVGHG6Fe+Ha2Rk+M+BF0JqFLhez/EADQ0XDK1zRYnDMsG30KIEFo/rxwv98pb6TW/pdvp4/'
        b'GkRKjkKXtbL1zZtcmxtshcfgGXxYdgOsjS8NFFE+Qxlw0JLJS4td4EwmXgSaCvfxi82cq0D7+jzqjHKDpTjHaijSWayaopKupiPwL2t+zT0yTNeTDR4eZJy2vEs+vb7T'
        b'eeWjUYc04P2nG+FuvLt9PIFaGZcC65QUNdAsWNUva6pX1J+3G5h1Rv15OIHRmPo+ZYStl18D6wNBnca0m4qs+ofnM+D2tLGgBknaBljHUcJwRjIQnCNaROGgUCqhcCFx'
        b'h/4U6UPxObaVVUTAw0OHgLYhCVQ/SqSiwW7YbLPhec3eMnVcP/Tp0hBwkUPfwHYaXIoYSyJ2S80IdTbj7RLAOWin4uaCLaSW6avCqG+T1XgHvsit83vyCsy+2GiqNfAo'
        b'fskEd19IkVOwwUFQBVaTHQPHaJOoMWALqCWp/aRi6vnEvjh1+h+DJ/FFXA0XUHU55BQI6WfCgQhJCIjmlaAmLQWcVggpLhJuBHYagbOzP8nSGppEvaegaapEbV4yxsaX'
        b'kzBlHJXP/AvdqLPaQvP5l4dWCCltYRjumvQwWksZ8p9/TmB5D33p9XvfKU1tqdwE6fpftfplSz8t0C1ZNm/BQ+7Wuvo1uqa8HpfmFa1Nt1Q1xYb0eX/+2MyJEz96bfv4'
        b'5/96cebY1yt/F9Fj2sd//b1ubdbBw6XzvlkY8nKfGy/M+PxgwZEJeR+fHPi3sb981b9wZnPJQWnxsxJ55o0He4e8cvnVndK8kTNbjgW/85+sdeK/7X3nxNnlmc8v2PPZ'
        b'7m29NH6Tfrg/95NR2lf7ThuU9/Xs1G+zf/hkc2LY7g/uqYf/8N2WL77R3Wm5GDor8b1+g2q3HZvX64zyna/n/vjT9+M+8hk6Pvc/abd/pdMCk36OFciF/CKKzRCNXnwM'
        b'4UcuD0S+jifT9aKRsa6TraNgjetw60PwGlEH0zKXxKZHeO0xN0XHH3u9H1wFF+AVcN0dEO0Mhw6MItvo54NLNtfKkJj/096XwEdVXQ+/bd4smUxCCNkIIQQSSUjYREAW'
        b'EYRICCQgm6IyJnkzIdskvJlAiBMXQGeGVUERFbSKKyiLIuLevme1LtW629Gqta3+sdi6tFqp1e+cc9+bBYLFfv3+X7/v9yc/5r373n13Pffcc849C7RgV9w2RLsjn0rX'
        b'7gE08RROrXZNtcQJzfyUgbmnHsHu3yGFTe2ALcfjBtwzfuzIUYR1Jp2IdawSz6SxEu8SnUBIOgFzSHwRL5CRdgaF8nQaxt3qr2IYirlLiTq87WqDx01xKOMo61/xmy6o'
        b'r3BcomMVrOuKXjHc6sLjMZx2BRCiG4fN1NYFy8tIyb0cEN3DI08fKXFDeEm7fry+l/xuao+2TavVb0f6YBA3SLt9QoNplilzCRwPumwP8xh3NAJsE0aLDCODaAlKannQ'
        b'Av8l2FUtOVwm5MqGPEGYYFKLNnQAwqIimt+tEVloacglqvVhqRmeA5IUoGRG8Eo1SVxqrBEIahQfOJPxoEEoLJuCUp40OjBRFifZMZBpvtPcz2Wuu7C+tR0YDKZP1Vs4'
        b'Y0bOiFFLZ0eHR1Wn4nxLxOLKUSng6QoAoYBF+Ju6PVG734NqXgGMzLuySQksU1/D/KLiOTFeMTTwDbx/PQarzsS27BRNb+IkxUAwBIAU0M0hiwZ2W/2IagyyXstYDfQx'
        b'qV+jHZ4D63igfoukH0RvvEk0YUyUjhOLNCGRrhyQrjkkXmMhPmESYZQxlqWIo0zCN0Gth8kVFAlyiEERI6U3U5QonEQqYQk8pTjl+B5yi/M5xUITK9ccGzrpoildba3D'
        b'h00h2q7J1zj5wqLTLh564VL4HVaK98PLplw05SwilY9gY0neZAikgHVD2jkq+z11asOyqKVRbe/siFpQ3AOX1vaVMDFE9EtREeqJWjtQN071RS0wkPCBzaz2h+judPQ1'
        b'CV+7zcx7RPOMRJRM7w0UypUhComxf4NtRdW12jptdYUW0fZhJCLgvNhBFrnWtHLQfu0Gbbe+NUZcJB0D30OTASS3kMkhEc54B3UtchNOzj8Ur81AIjo5dXRQUIBQD3Ju'
        b'tDAS4G0lXo23s4MCvBG68oIoqczoIc4EyhWzYYJ4bvl5i82vgglf3c6+8hUEebhn73ec+N4gYqSaKO84JhQW0vzAcBL0vk+LIlDX1IpnVp5WTxvMimeFp/UHVmLU2aF6'
        b'AmjyioP+WHysnSTOdpCHDAd5ZrMJOQzB6Ycma48PGzqropQYWm2Dtk/bXIBjziMaswzVHq/s3doco5fHtRwAOXFLRI9EUTM5jIx5ndgsN1uX2OAZRsvEZ1aPtdmuWM0U'
        b'RtMExIa25rYlDqUIY0xAOkVxrrUvSVEGG+lUxQVppxGDQgrZvBYlTUmHb1KTnvVRMuCZK/ZEUvoqmfAkLSlXPyULnqWTjTm3pI8yJCQCF4FW5PYlGUoxpQqUgZDqq5TA'
        b'NzK0oFAZBOlMinjRjyRap0VTZsCceHyBacB5xaAwKVY8otm4vJ1iPaO8He8tBisow9z3sHXJTzjyPfxT/8wRpT+Ni0evq47NcsLSctNSpWjz/o66Bs+vYhyV0J2f0Lbh'
        b'x2c8gf+nxuIei8siiAsjFl9XUD8jZBuoa+zdyi5q72ita/K5IcPrCQ3ol9iAWI7ejfsyjJrbXeayNK0shajFjdsBLYaTWPnhYnknzkx2pyfWjB8nzU2su06aG1z1Styo'
        b'U/3yhwedKvsg3s0kziZmFt0Rm3bE/V3nk7yaN+Iwz8RjFxZ3OQig0CKoYxWUFwiTuOU58MTeInfUKHJQxCvgf16xruH9OYqNfZXFmXkXQ/kYgNyQHztqjvEjonzZMWH4'
        b'CObsF9ep+iecIv7SY5ZLy3qKUSQee4XbL4td7wDmUQ34VzbB1opbsWmCQg7t51ABHSeTObsB4cDu7CFf+b8XTf6TkIyNwv7kCZl8d24SPCZ+UxPzFipyxwmBCBppDANM'
        b'4i9QwHUm9SfoFNVvsRUWfyeQEUhB+BRTpQ4bH3XEYP4kpwHqd/DzmWhwjNjsZPjBEv/FBq6NN1D9BzbGioXVAY2T0EL1e+6kVBUukL8kNa3v8U2D0pKgOwaCKMcIA1iF'
        b'JSREwgTpCJAbBWorb7YV48kHGQAJaFVr8fnb6jqghfDcaLbMgiEYqyJq9bA2nJopOGyR3N9Ew4CXI1/R6Xx3RmI/WPFJgxzrxkjWDSHWDSHWDSGxGzjkPAt4v5Y6Qu1P'
        b'7kYTunsKmIOPEjxV5E/VpF2CnN8l9yPjuH6w8k/YCGL6G2FoZxiIc7XMxA1qIRIoLBh8D06QcRoUEAxgEmOrW4TVfTYjDyT1GLaoLgZXKW43UFlNAU+b223irkrun3u9'
        b'VGXolCSZx0REgSEd1p2dtFjjhfc+R0sTQW34D/WNzZKvLDajlcaMCopIMyoaMyqZeQ3JnVSjWniDfDXn1sKG4Xz8ic8yjIU/NhZifCwImZ/aVFuhsBTJ2BDNUXEJDvJa'
        b'kDwysap+IBqqefKwwJTg9baH2tzu+vb2Vre7nxTfQjOTK2MZDOp9QWwucB6wIgqVjTKGMO3hXiR+eSRtd8A+c4OwyYSjShiW33MxUnEVIOMmXyCahkS64mlorTNN6qO2'
        b'QDs7+zX3g99Te3Gs87jehJGy6sEwR7lSDGc5j1sjLEPlCY0nQCqMNV4hYFGEjRIxRjzTUSBQsNREpYZRY3xoo8giJUXtnq6G1k5/0wpPNBX3MDewmFij/0tyDA0d8/kn'
        b'FxXRySqsD/SRFLXCDtQK24LZtXTsVR/8+W1vXVNd8GqAZJ4ckMwieaPANsXWPn4cY0Wi8NMELEhXM+IuUnhYyrpFW4cEMA+M+xo8z+ZzuYuEHkuPHLQEhRZZVWh9AKkI'
        b'7L7gX8DuG3m8TjLeAI6QEYkvdwVl9ny5azHXVQ51SahoAbUVQJnWHhs8kYNAS/RYgzYc3KA1m4PcQWJgrD32oF19Msj79wdRUcMOOcRJnE8K2pFeAZblpaCAvwr0BPJD'
        b'CU2miIGdW+MCPWYZjARXqT3qhHUBXGVTqwJTHrUG2t1KU0OAdBZoT4BdJQCwVR+1Y0ZcRH4iNBnr8wVHkh7abxwN7T4/s3qM8goed0ChUb5B/RzfCg0Kc69VbX58ks00'
        b'Cyotkkw/YiiSIm6IeQpMF5x8JkUolI0YhSz4QfKGa3SCCEUkjO1Q5IJSobKylK8szTpeQZt6c4/ZG/VorHNfcozrRmaaUQdIg9BuT0NDew3hZkJFqg1/UnkDCKkjCXHB'
        b'Tl3ulxgwDFvzS9FYczbRJjktNsFpcUkuZ7qULmXKmXKGNdNhk+CJhXwCztWv1a6cmOrHiKob5+gbhy2fVV5j4XLPlir1DfpVC0oN1Yk9RfqTcROzbH+tTqFY8YtSmRut'
        b'yAvG6ldDZsRUxQu1jdo1+q3VsUJ5LuUyQd+jRbJPcJxBikyuGIoI8pv4BGcgbXUtHpMwEeI6Mb2c7BozOjWOaJmztb0XDND3XehPaIpDu0XQ12vXauEk9tfEXX4MWR1j'
        b'f9MpLCKq+gOzC2ylBIwrzxyqLbEwM02vaDC6MrpVgzxWxamkwtWmuJS0teiWjScCpk/UOb2zrW2V0dQTKWTaXVAbgzEwsOfyCSwmH2cxmZABfkUSOEjGfirXqJ9yxn5K'
        b'HALxnIzxtNDCIu6TQe7rNGxuJNh9MfKJFp/Mnh3PI6FNSJUUo5VkvgD+d/dL7NKPdbajFvEn3TvtQJ+whtTG5pTvzkqqLpald/LMOMsk4sOo0xR9Uo3n9gpKjO5CPOZ2'
        b'n5dQdc5xPY1l6r3ys2geFR44QSeqkBGdCPheHRKO8+MCnmgCnSQAZTUaZzGpuWICDoYZognEESMSKYkkPLmojjDOwjjdY+NZaBeUyvXWpVMifJAYZ037AeLH6na3enxu'
        b'99KEMcw8rkLK0LvcArsR4BpN1QDCBxLuKientfCt212XUN8J0Ek5/knvkGeq/IGeEepWfqAWRtJhkx3Hbx+4iNQhOIfFse2gBH+GxvYE+z+Z0EGQqdKcUJvokG2iU0y3'
        b'A7oXSRNsiH6fts1firhauz9gIL51xYT7CrRHJP2Ghfr9vaM+VCs0Ud91YrPYLC2xeJg2GMr1JI/UbEUsxFJ0So9o0bbExiRxgAoZarSTRM1BlIQtmlFb3+xpCJA/QWOU'
        b'foTEaC3blnF//WfyIl9sUsTu7BMrPXWxUeOpi4388R3nlLBQ4ylhIQKPlQkwVtBLd06Gg2Jn8RireFV6gDP4L4MPlYATbXGoI5l6L2EjMUhnFNhAeGuBt4qh/Ms3y8T3'
        b'LUFqMs77YTnxTp1vjpqYyNHZiHcjGI86qoBD6GJqrp+bayDqmkrUYmfAUICNccA/Brl1SzHplACknov+o5zq5GNmMJIpx6/OUj6RmmNkXkHyYj3F0K1Y0jKTB7dJjApz'
        b'ihTFWVt/of6E/mCtvm7WnOGo9rZ+9pzlCQTKNO3uFfqV1sH6Gv2B3tdpXsI6JYKEjhCBSDFM0aP9zZ6bWOkcdH06u729pbMjdn5p4RK0ZWjpGdtVGCbTmFDA82IMKVkY'
        b'6S4FVnV41M14a48J4k6ymcqtVGc4zjsCh1X0A60bzj7oxTRyRKwdJyyWcnh1lblYAA1ilCP90CV9EwZZ28NQYYkeITJX31RVPlw/hMq/+ubhFajCs9yh31S1POngKbaI'
        b'Ua4EOzhH8o18Wk88cUyoFUvq92p5GHk/DlXScW3QvcVgb/lj/ziH/L+gtXZDpz/Q3tbU7VEKW4GLLaRTd7VwqCegejzoMrY9DralJ3dXS9knoEsN8qGD5t5Njb52FeqI'
        b'i0cL63xKIXLP6AGkTlGaWESuwjKD6xlaWlbI+O1kE/CEJiRXUdfa2r7STy571DqMpoWea30VpgebQoNa9ycXB+uZTiXF8+fMhoWDzHg0JaEOkkH82Mhxo2DWr5VMzTcb'
        b'c5RGZ77IKBRqd+lXaOu1Oy7R9+sPAS7TD3D6A/navUwN6ElFC8PbzeNV9lr08fO0UPKJWCxq+tKE9abEz6Zkr4VOxexLRNJ4kmH/wxMxG+yNEp2BiYpVsSGroNgVB7AC'
        b'csJJmG2JlXZJG5EcrqjTWAxzgOdRayqT/MPEpHJoH6xwTQBfCr9D7JFiErohwA/wTai7yDXydBaBHISgbohJ5c4KCsYboDdzOeAiJJQFBEW/D+8oDXyGwqEMAvrBZHxC'
        b'V35QmI4aBRb40mLmIolEYDEXl9Z64c0mnjc1w2UUkg/HJUtSvIH4QxRj/Bk7FY063CScdgNksQ0DaSTTSwhl/J7ApUP1eJu63KgQSZxgVPD5T91x6T2SaVUoCKipIiC4'
        b'oFtxidyLp1N8QycJD2KHXDQTcZ7GRAxWLkG69QBOCG6LAAiNEh7/ozCIB8K1R+zaEsSjoXVMGIRH//7xJCCSSLRT0OULCEEJFQTYQapi3YhDvcgUFjVLig223iB9gyBE'
        b'UwJoSF4DU01l1MBzB+Ds6zAPe2M8J2SE9jZrBPZkMdS4mAuyLSKlJmqZj8dDUXGGT4lKNRhF3bKorrXTc4JeaMIxIoqyFKlFNmR2bEbH4xxN4GnXjt2bmLoXxVVy4Pkc'
        b'zgfW0l2RPNoN7T5AKwHCTv5EJRPmVxWKJMFvjMwwhVMWFP4RQjIkUX6KUchkU8cYeqHtS/R7lkct7ariUVG06e9sDRBj0RaXOP2Q6oMruYVPSIa4heOdBnPlANgSBFTD'
        b'zYT7fLQzc+Tw3f1/oJ9JB44xEeMsDtV5YAmeRXA0tkcEkou0hMhuazjCGongRWPWHXT0CGgUFVDwKT5bbB6goJBYQEFxVIYB88C029zeVtT+8NGQmULTs3Boz8afqfwP'
        b'k1/T4f27cd5SMg5QyBPwcYvIqOiE3ZWAK8wlHqij/nWQh27k4BEWSUEEQwcb3rGTBXgboDsR7mYGACcFBbS/Wc2TOgZgrzU80bWwYGB5KCjf9KWbTzAPnrYqFnYHT2BI'
        b's0zMxU5XBbebAVjWQl+Lr32lL76tFhYV+4uOyZcW+/HwVVb74mB9gx/JDJmpY/AJ+odi5KwYJ/XVsfwJKyKa6vahIhM6/4YC/oBDmpUAU+nGcUUWLwvpfHde8tAmfpqE'
        b'pBCYSL6mcImHmgQygkG/COyuieuRukqYtpJheocoCL9hZnJyUCKcXw44XzLOsWBH8EJJtwiI+U0uXVareAM0VPQByBYgneIAi47+84HytiaIm2ymPFnNxnVrZxJk6EvC'
        b'euxd+DsL8n8Zp/5hjEQU8WbQWJ2AxY2qxRpYAvZe+fJpsYZTF2Yl0/unGJA3zgOcDt/fEecBsvqlDwQ23UVxyS9Hc7m4VFI/MEffoG9tRm9dBdmS9pi+dfAJvtnxH4Xy'
        b'jZEiacSCmyQIC5RgEiD45njiA1kFg/Qg5RuUUTKJR3rUNru9oaWyqdVT8zGr6oMpMRLENJKIYaUwsecITv7MgIAM4mreYJ8FekdHnFkoopSCwFy6LSSolEloaUXjObfN'
        b'4DCkmmN9MVBxodLuMUIcIC15zFrsH44qfjhZdOgvN/kxH62qqLWu3o9qBlEbqQEqTWrUivry7Z2BqMXdRtF+KP5x1OrGHEBJJ2g/RCXMoS7ge2MmEBQslhhUOYlOyCBa'
        b'Qea7+5jDdKKsE0coFhZ1A2fqg+JyQ6PArhWr0sO44GB0EDMv5nyLDEvbFTygJ57rnhBE1MW3iOpZq/E7WZ1JQkFWDt8iqRcFrCgsXA1kV7NNMcq5ABUQoQQ0zFueDsy4'
        b'xMZ6PqQWmwSZpeZIH8JmDe2drQoNdF0DBVcoxAH6+KYb8d+9UxaU2oHDg6Gk4Yla2lpgcNX5dLpWO5/49KjFo6qAdRbjQ+d5nT7Mbrzxt3o8HQa+i1phk6GiGk66iKMS'
        b'1p5mMU45OTI/FcjTg4P890g0A2gv3Z0aG3v8pndzp3ID1aklCsEjMmLmmKslkJLM8Y9xuJVARWJXGGhYmvyxDlvUNrg3BE69MLedPmxIoSVBKI62N91psYayHL1Lu0zN'
        b'LCQXlbgLdNV7cqE4unXyABYrscQlQ+kJEEkvezfsKUuoDUHSkEMLTA5NZwkwMIa5M8m/JHKOpy40h0ZdFG9YLyZAbjcgWxSvllpiugc2Iq1h6jISGmlkS1Jhxv/o3JxM'
        b'9mn+skwRIA6OqcUZGypDC2cRzVJDaztQfV4+JjeKSm5PV0MvEmJALbBiRyZOmOP4Vc3yoOSjhidT7N62ChoZrFFtxB+0xFdbTkV6Owcy8RaDabVJLoerjxMluFbyAqCv'
        b'O18/rO9NRfdUtfqmFUZU89Rm0bFSezhpR7AaV9rcY8Ig1CmXgO2MCYRQaXOJpKSHWEAgMSSHbF6ZxLR22Bn6MEaVQvrgqZUddgnmmQ7PrhJZ1MbSjKhUOXd6ZRK+ix3h'
        b'TedQXG8QBnTOj8ygOWcIWgqqS0tIpFHaoggBmaWMXcEUIR5LmbsKKxpduKLYfywVEkZ8c0iaQsUmmlD0qNpR1+iJOv2egLtDbVc6G4Cqd+LX7kUzzptfVVsTTcF35H0X'
        b'8FOK222EAHe7mQa6G+POmARa/ITxB6YQ654Yh/EM0jeHVZ+K1Z7ILp5MzmwcNRzrMx9aUdhW5yPvpOjEBpFAIA7NzKPE8RQj9irW/mkxfCB0Z1Azkl7XxBqDvIXdRAnh'
        b'pDlDU28UFpiEobo0LJFgmBTVgbcUgR8ldUdSc6D7HuA3gmI2h3rT9BT2+WaZ6XVQOby6OgxkomJZI2xO75GA27UGBbZrKdw87jzufJM7kZnt55cUsra4eP6MuVMLv8Su'
        b'MjXGLuD+HUSPR4WV9QYYRGXY7zs6AzRaUYvS2dbhJ0ET6TvSYWfUshL1EAzZJcNjNJ70ieBddupm1mo3nrxYTOVrMqOWyQkC0psZtFNl8t0pNP6sYVH7TE/rCk+gqaFO'
        b'RaEks/zESWgwhUtpiTPSyjNGCE0ekfGBq0yKVMgC8WtEYyXR+NI9sD1AmIv4JswHLMD/WTLJdgQ9X7B0f5a2KXKPXbH2OJiUoCel61uY7RRSXv2sxwkEvjOX60kN2tVn'
        b'zJzBVJhLlEDcpNh7Un0FlHZA+rCSAm/N2m1Y+3I1uTVBZxAozRyuhVPfw7IVZzaXy3V8ACW5gq72o0pq0NVivYZXJwVdrBa4Lwg64RdLthpYA0pUXEErlqiIPXZog4u1'
        b'gb6E96gwzmrE96jColiDlmBq0AF7vb0Zf1OanUqfjTKU51BVzLVcBZ5YZjit5gia5h3BWVhwBOf741DWr1/6ev5fp1SSdOOYOHnyZJq2qOgGnMEvMLS6C6P8tKj1nPZO'
        b'tQlQDl+FSs0+z0p3F7usKk1lqv4OUsZtbfJ5/AwVtdWpjU0+f7QvJuo6A+2Ewtz1gKFaojZ86G33ARWrtnf6FHYk0o6wKjV4Wluj0vlz2/1RafaMygVR6QK6r5lx/oLS'
        b'NAbfdKovUQESWdlY/IFVQAWnYAPcyzxNjcugaNYaB2Zwt0JzPMY9sK5QhUX1QCuicj2Tkdh9nW1u+oIpDUt4D089XQF6/E+jcKcwVVDS+F5gMTgIzogB6qQDm3SyEWGe'
        b'CZhDR4fhfYS8kQj5lFOmHGzJScaSQ4UtWnAJlSRJU2Rzh1K55LWF+Ks9j47fkY+ZpQgRDg2mAiLxSbhz2lDussZw7pGLFie8Igf5LKb6KKEKN88FLIYIVI6xwyIJQm2E'
        b'1+zH8qbVqWgaXXh6u/dMJownTw3+zjb1rwhLw07FaLxieOGQEcOKk6immFgYERIZfrl6+LDB6BsmX15TEodHGKbRV36vnA9q+qw2dxKZ6x5IA4tNP/3M3sy9jqBNzzGp'
        b'rNhfRmulBnjkVzlD3IaGRAopn0dF6GnURZDdBDx4Q3tru2rgb1a4yZu9nrwHJztNfSHWzj2IJS2m2Al9OZH9IYr/DexrFEtE7GVIlsWQr3r5yYm6FbyB5NVdvFFNAv//'
        b'ox1BxSUBiNbHWWKSgHSrTcpxZQ7tRLvP+UP0Pf6UwVqkY7nICfpN/CBtWxdRtzU1NaiCJjIzxB36g9UX6k8ZdohD+uJLsuVdOYXFdx85tm7Ia2MugZorm94LLeD9W4E4'
        b'+6y9Ys6CRn/fxZm/eeP5V3c/8rVv3ZEP1rW1Dt6w9qqNqerUr356x63lhdNmLrdVLfqm6Jfv7kn77uUz//zNnC2v/Ney9x/5+M2Viz/7a811Z09rjFy5LVw1edCKZRu3'
        b'vzp61P3VT89dGc69P+PBCee+eOTi+qXrn169N31i561v35kW+c2E2qOvXFy/773Tvjoy9oC7NiJ23zz+nv5PD+qZlf9mxYfhvTMi4wZ/Wnrj9dmTNtff1+/QuV03fdiU'
        b'3/f+/b/9eUHJqDe+uOky/eMvx3iP+ou+uqf/tZGhPy2+yHfVQ4vmPDXZd/gXz/a76KGP7QPu9tYcuiOveNT6lm0DfvJJ2TfndC99NlU/Y/XboezPz5n96q4Luz1Vi+6Y'
        b'+f6W6zzu3edt3XrPFTcffuP5kbNGTP7umuG7C+bN37bkOq3t3QOH9r69vic6e4P1zcvX9in5/ZjnPxz+pxs3LPjDy48/+v5LCydVVW36a/lzeYNTnzuc/8D35R+NfN8x'
        b'at8j3l/VXLDwF38Syi+59tvblxYN/GTq5Hlp+++oO/23l27x7tgy6doBq0qs8/JeOPxy5KuftaT9/MqPHmqecsZlLyzpueGD6xa/JH5b9ZRzcvvzq//yHPfY8AObRv/u'
        b'6IE/fb7+vQt6Bi464J3w+6e3LJ876pvhr414OXL/C3dtmLfqxecHXrKz395xfY+Obgi8/VPvC/pHFzyQe0317+pu/rq5/e753cp7v1y1feGfP9+rDv3w2ptf3f5av+27'
        b'nr13hWfE85ekbB4xZqNrYru/pfpPTzYffWLtA+tfaft0Tf2Kr+2HBrzT8Osts7fc/8G9DaFHBngfXLfhgReWnPf2z/b+5trr3nj/g8sm67fMT1vyp22/2c/9vetPf6t6'
        b'wX33V5bdm/548N0z7p7809t+l3L1s302/XLp6bXRT9b9pSdy0x9HHnznyV/Mqu1o3vPcZxf/7QXf16vLv3vs7ne+2PLl5Ve99dG2vAv6n3mXx71p+5cpwSO+ER+XHCp+'
        b'+bnLr9p3ccU/3tw1dfO8j47J7y/9r3d2HXj5nZqZhS98/0SfeeE/c++NCTzyXl372A/mO94fPOHrd16bcHHtl/nNV4z7eMOHN+947egfK9779bhRdbuO3dW9aN6zlz7T'
        b'3f7wMyu33bdg2Tf8wGXf/OT67so13i1f3fdQY+4fzw3e8engL5U5lo3ffl+2/ZUbuye8NG7yze8Evhr3xz83Wvv5Pjn4Ykf1ZdrLvpKrDv9k8WcvXL0w6tu64tbnvd/f'
        b'+22/xhcDd339yZlbIwuH7Hz18bZn7/tyXPD2D7ceueLzCTsfWjPxrNP2HP1i1GkPD/77u795//Mbn3/50SUvP3b+t2lvln5X87OJX4xu/55P+/tD4bv/UJpKsQf1m8do'
        b'h/AEEj1Q1c6uqtDWaZutXD/9Sv26TFE/OE/fQ0E1tPv1neMxXy0dWWt36hu1TZizj/a4qG3tp/2ERR/cqT+Cfl4rqrQNI2bO1LaV6xGOy9CuFrWDWshOBu7aNdp12h3k'
        b'LrimogxN1B9KdwjatiX6YQpzqF2v7ekfCzSuPeZPjDWerT9A3kXHaHv1+7TH9d296ow+ot3JmhPWtmn7tfV4uGqfWV627AwUbaZpT4lubY12WwD9aUGOnSK0hGxAjaLw'
        b'nrq5iTnm0jdrIS8ezwcnOKRF2i0Bcmm7JaCvTqi+ak51ub6x9MQz/curndpeB3euFgrg/nSBtk+/9ocVL/St+kHr4DR9RwD1MPVD2tX6Pv9wiuu0uTNeY1JN+n36U1jb'
        b'Sv0mu3bIdS4FY56u36jdeLyA90r9hriE93rtZjL8L9KvXuxPqdPujW8A+0YDPfdjdpt/sheN+zcW9v/LT2kRowf+n/gx5Vet7XWK202eGT6AH65OJp8Gp/7nEF12l+SE'
        b'v0xHui2rb2amwI+cK/B5WQI/pEIWSqbl5LosOWdLgsDn8GNbh65w8jYbpkr6CHwR/C8oFPhMGf7b8hwCnyEJfJYcv7rseI+ponyU42Y54X8a3mWmF/COdlS/dwnplryi'
        b'TN6Zn847rE7eKeL7ApcNrvm880L4PUPgC3lnjXpfTKSW6N/mf8C5l584GY+Ddglnkse3dyW6vkDcrD8+cqax8dwP+BA2Hy2CG4orVxwwV1vbNCV7mugfAEBW/qqvYstz'
        b'vndGpl9dVbHtra73P33679vGb9o59MiKI6f/5VX/1CH3lF/8bv6n+bu5KR+/ee6R2za/av0knCp99vfxu3JT7T19Z8nfrii8Zl9PcUPVW7PXr3rm4I1n3qUfPf1i78V/'
        b'37x61d3/+LN9WPTyWeNnfbLmjgeusGZ+MCVadufjb43xLLxp0qf3vth42wMLf/beW0vLa6ddeu6Bhy//dmxme2D7d9dO/OS7s7Y+vWD4c/fu+Oqrl367+fmtXxctWBr5'
        b'1V0b35M2Pf/wVWVH79ffb1y88+df3D3m169XfXJ0nvxt8U39qx/sd2Puo2P+Xv7nS1/Mf6Prl6+tfUv4zc35X9+24UDRhc+eH2l75on1dWfuvuY6bfqe/CdGLmq4MGfP'
        b'g/dvOOPtq5+5KVhffX3Xh4vUW6deeuvtH72yznJB9Lw/HCp858Xf3HZn3Q0rXpz19vpjCza+VDrw4l8tKDlt39Vrlp39h2Uz71w2/eEvvm/b0NQy/rarf3udfPXpj47e'
        b'Mf+djqkXeysuqhymzmnb+Y8tOx4+a/FpN3/80Jozam8ZveKX2z66aPC708cNefHSX3b0//S/Jj16Z2fg3Ion13d+sOfN977zDHiybGrLa3/87vf5Oz8Y9FHeRxN3flvb'
        b'MNn13p6vvgy9/eHu5Z/N6xx/y99K/jZ9XPo1+y/5csrvfzrDUfDqLwrX538x/pw+xdfNm9rvjNdfObtvxcFXpmZP/svyTSnOkU/bGmaP/LnTX77/accNh7W8t97+QL7w'
        b'aMf6iX87fHlw7sVvXDrn1nd33Tz7mw/LPp+h3PId//qHb7xy/hWlk2mjL9A3rWDANFpfDVvc+nIDmM4TR2n7Z1GegdmzTAKmRNuFm3ucfhmvbSMPWkMzC1nMT32DqN86'
        b'34j5eY92OIAMbo62+bJh2t5yGTbIK/lgxiWNMhFRy5r0x4ZVV5Sh8yedRXLeUK2vt3KD5lv00NSMS7VraDcGQP+JtibmEz3JI/pC2PP3adfrV7I4iAf0x0dUQ8biHH1D'
        b'KWYeJnNp48QWfVc/cmGsH0yHfXz9iJkYqUR7jJNm8tqDk/THqZ364Rprtb5pqMAJPr5Ef/wsexrt8S31+p3D0Ne6V99fa+HkswXXvBRySIQxYq8kkmzojGAFz8ldwqge'
        b'bQ/Ra5cDUXd7Nb4srQKywaY9Jeg3IEV0np2io+hXak/qTwLRB8SNEOS1nSlT9LsGUyv5GdpebY++Dt9oD/IwLpsWACH4KL08d6J2bTV6zJqpHzCdZsFQP0WFOnuAnkEf'
        b'g/BlD4+usCu1g5fQqwnabdpufX3tcB4KXcevOudc7QZ9A4WN1Z84bSjUFwYyrGymjtFXkb6C0V6rX8FzxWMs0z2LmXP6jbP01Sk1+kH9YEVZdYVjqL5O24dBWvO0JyTt'
        b'plEjGfn4QMYsACWc1mHodKwa6MvsZdIcfe1ofTtADDlM2n/hUpiHWdiY7fxobW+lfvVKaqe2Vlunrx+mh0dgjMl7eLVusb69iD7qcGkb9fVAlAGpdTmvP6VtP7tgBaty'
        b'v3aLfl81kZ0btf21MFulMpeiXSnodwa0Bxlw3KnfPldbX1tbUTVR24ETOsfCZUwUtT1jJ5GfJ20X8On3VCMg5vQBzFpDhbguE6drD+k7WeP26XdDJetHyBw/n9MP5Om7'
        b'tIfYpGmP+vW7DAdxo7SbWVRcj3Y9LRD9Wm3fFH29di+58NA2LOekel57cpmNlXqgeVF1ReksbbcWgTbJ84Usfc9oRvWvbtKvR4jWtw3SN1QhJKVo2wX9nrlDieovhZ4f'
        b'hFlFqhhW5qbhhgPMDG2NqF9ROJ4cmmoR/S5tT3VVubZjaVWF4cPOpa8Ta7RD/QMoQk2FVXFXNYbVPSeDkyReu7XkXPp0KEDsDtarOQtKYOhLq6BwfauoPTpqPHOf9bB2'
        b'UBxWpd2vrZs8tHTELADaNH2XqF1xsX4jA/Rt2t0TqofNrBK1wzM4KY8HQHzqHBozZxuA6HpEAJtF7YB2gJPm8dpjZRZajgDxmwuHzbJwfDWnPejVt4sqTVM9zNMeAPJy'
        b'mKi18Cn6/IRRCQr6Du22M6nKGu3AXFh5GE20WoepSOe1mwZ7acmO0SOZ1cDynHE6z1n1LYK2P0XWb5jDIOTW5fXMLybA6R4WRpj8Yuobm2k2psNoXEVOKbV1kuGDjLxS'
        b'OqoZBG3Xtmq70FnRBtFbbbq1c2k/Ec+ZqF9NWarsc2iBpmn7j/NWqu/RWQiIIPAta0xnoWMB4Mx85Cv0fO2xwAjINSC3IV07jPilAtZKGUwRrNktgE9m05hsqK7Qdkvc'
        b'HG2PFeZ29wyCFn2NvnNRykzgLjvww2oEp0x9h1itXwEQsn8ujYKo7SslnKbfoG0YPnMOIIwU/XZBf1jRIpQhS9+AMFde49N2ES+FK+1BQX9Q359JfRwNr/cO0zfNRl/G'
        b'kUB5aQXMYt8CEXD1Wm039bFsWU41LETsZaSqfNYIqEfO1e7gyjmLfqN+h77JGIk7awxiZ2NtKfBj2kbcfLKKpTr9kNhfu5Wq0+9WdRyISG2Dfk8t7SJWaNEDsEq0vX7i'
        b'w/WNFu2m6lkD9McALc1egQAHqHm2lcvVH5Qu0G7V1jHPv+u0LZOhXYBZIzbtydpajCrUR4et7rY5WQQ+ZVOn0sjBNqU9MpOTKnjt/krtIVbJzsbzsLXa3YtGJGxr2OL+'
        b'QyRtTXpfWmu57uLqqjll3fVzrJwsCTZ9CyCJgaz2EOI+6Kt+tbYJ+1sBQ6vficDxxPmn4NfX4Bf/77M8/3E/sbNfYr9+Aj9ciiDY+OP/HMDeMKUVdIQn8ZjHxd4YpxoG'
        b'K8aU+gSHcQffCRiuykY+nTKTynRSeZgHjxidZM1so2NHpyCLXZdzJ/6dLvNMqs00ElA/w+8JdHa43XFOyjwauJ9P7B/eMN7h60THoPQupoKQCv/RGwkqAPifht969FsD'
        b'f5FF4UV4oBI5Da4CXAW4inDNCi/ycnBdGF7UhFdHeBFa90UGYn48ZI7wIT60yCswm7IeDpUUWsU2KZLWZunh2+Qeoc3agwd9smJrtbXZeyS6t7c62lJ6LHTvaHW2pfbI'
        b'dJ/S6mpL67HiMWIgHUrvB9c+cO0L1wy4FsC1L1zR6liG66AgF06Da1qQjk8iKUGy7YikQ75MuGbAtR9cXXDNgmtxkHQjI9agFClS5Ei2IkZyFGckV0mN9FdckXwlLTJA'
        b'Se+xKX167EpGJC8oKlw4F1W4I4OVvpFSJTMyXOkXqVWyInOU7MhcJSdyrpIbqVLyImVK/0i5kh8ZpgyIDFUKIpXKwMhopTAyQRkUOUspikxRBkfGK0MiY5TiyBlKSWSy'
        b'clrkbGVoZKxSGpmklEXGKcMiE5XyyJlKReR0ZXhklDIiUq2MjIxQRkVmKaMj85XTIzOVMZEZyhmRqcrYSIUyLjJPGR85TzkzUhN2rOEiQ5QJkWmBbLjro0yMzFYmRc5R'
        b'JkcWKGdFRip8ZHrQCm8Kw0LQFrR7cZQyQ65QdmhgaI5XUqYoZ8P8OYKOiJOUTuJeYF2htFBmKAty5oRyQ3mh/qEC+GZQ6LTQ8NCI0MjQ1NCMUGVoZmhWqDo0P7QgtBDg'
        b'YZAyNVaeLewK28Kla4SIPcRiy7NynVRyeqhPKCPUzyh9AJRdFCoOlYRKQ2Wh8tDo0OmhMaEzQmND40LjQ2eGJoQmhiaFJofOCk0JnR2aFpoONVeFZodqoc7hyrRYnRao'
        b'00J1ylAfqwnLLwkNgy/ODVV5U5RzYrlTQyJ50U+FfBmhvkZrCkNDoCWnQUvOgRpqQnO9fZXp5jc9KWFXMIVqKKFvU6CWVBrPHBihfPh6MH0/FL4fFqoIjYL2VlI580Ln'
        b'eXOVGbHaRWirSCVJlzlwHnuc4eKwM1wWdgad4ao1AikK4JNyelLOnlzmDKaQNkolc9dPPjXonLt3XTIkBJgNVJhrsat5AXTtwTXzpga2YUR7rF+xf2hpYRNT66wrrO9s'
        b'ag00+UoF9RJEOIMTdpyTuaFye30k9EKFsR2WmKMOPAFW95k2JaUSYLdGT8CrohWDzdPVQFovZEKO59rt3qjT1PohbR8enYy0ATqEOwf6rW7rUD1+P6TE1vZGNDRGfTD1'
        b'cSj7CHb6CKltYLuOdOHPDvzBISGV5nbFA0iVfDygInhU7GjviDqgdMXjrUPrApvXzQ5PmXefuA+IGCKOyl4qJ5rS0O6uUxspkChGQHW3rGz3ta6KPXLAIx8rLOqEe3+g'
        b'znCnaYOUt7Wu0R+1wh0VZqcbnz/gp7ekvk41rKhT4wnUksUUfUc3Lnqq+klrwddO5bTCFNbVsw9Uj2cFOifHBColUMLS0OqpU6MyxUMZFRXrmxpJ9Rv9zbDQFVEHhptm'
        b'90xL5yFjkgNqXYMHI1O63ZC93s0m0gp3qGUQldyqxxt1uZUmf119q8fdUNewjCn2AmAozCEaUj/HhKGlSeED8VgUSS4K34Hme6a/eXTYFGZu3LLIA6SLfEmSe6Iefnn+'
        b'YuY9a23MVvcEY89/5oQJgfOrmJIYkQAOE2hjbURtMNls4zPwJmwF9OaEZZWL7QjygHgELxo7FCgUiYZMIMRwIWlpSUEp7GixqavDzh5LUAintAjqTLiXfUMpxalLw84U'
        b'rscSZkaKQtgRzoA3Lui7MxvHQg5bIT1gjRCUw/3QealvL7qD8V8HTwvCWV50VrMd9bOgpr5Q037KnwPf52N5vivg+cBwH8p3NNwH0I21q5DMxXJ6bJDXGs6EvBJsEqJh'
        b'hfQLGFkJ3dVQmXKL7RpeHRmW4Ut713AqvT/kNN3bOKAU4+ugHe4ceEcRfNCqxT6fYyMR5qmcMHydFk5NMQzXgmI4nd6m5qAnXuDuFC6Ygu+CAqDb1GyO2VORH1E7c+of'
        b'03+jkYUy74EZcYTzoH4BRyhoyURDkhw2HvD+p9TmbHNEgsl+Jpz/WwcUg/4DpMo/SvCMsI3w7K8hJO1ihCqRqqioIws2UuHJwD9RIrVJJxHCOUTMynwWn8dLoktwCel8'
        b'Pn4nOuAZrBshtmT6GHsQLZnXBWPJuGCaS40lk5m4ZOCtiBMXlmCfGpm0iHDihsE3Et0h+FuCkv9oGMNYyWH8y1pDRlQ9AMjq6qCVbGJsQaiNAQ4smrxJnG9ZuH94cLgE'
        b'FkKu1wJg/IugHcB3bo8jjIpoDig3JegI94fF+TaAXVoKl4u7sgj3LrwPOmn5QUnBFKAP0wzwTcEc7F3QMYlbvm0x5/OFh4RTw/29XHgw/C+B/wPDQ718uA/WFB6ISywT'
        b'KEx4nhfmw+nhdKTMmqy0zC0IxLCc+gRt0KNUAHi4BmFphF05XI8rnAH0AD5xZXOwbFKJTkiBr8opwFYXlQD3Xuj1Jr7H4jsKT+RwGZSZFkwL59B7QAzQ3rRwIaUKjdQQ'
        b'Sg0xUsWUKjZSBZQqMFJ5Zjsp1Z9S/Y3UYEoNNlIllCoxUvmUyjdSRZQqMlIDKDXASA2i1CAjNTA2bpjKpVQuprxpsE1UIHUf5DYhAkUkAH0NnxZOhR6nB9OvETpWByX6'
        b'tV4j+HcTvGQjvEAZMPZedORt9Cab85LXu3BfhDMoVSSvCxKOPHkKw+fDghKpTUpJLiL6/B9ZsqXD/wPQxn8/ajoTUdPqOGpCLULBZniolkUXi3AmCTz7kymQDBoKZ0LO'
        b'TNkMNI2erdMlNB9Gj1pOIUN0AMJy8Sf7yxCcYjogPAxHnSc6ReTlY+jMdDBL6Iy5kwSEJQHw2Ax0Joe5BHQmhi20kwOlErYDgQ9ojOljJ+07vRIn/4YIATSMd8umyT0b'
        b'RhEHIqlDKWaHdmOHJFgPSHIIgIEzWCeYCiY67Ebl8HD6GkEtpzdSkPJCB1PDGB0EV1EaYKTUsJWlUM087NhcwmO5KeEMXHE4VIStRAvg07B9HNB+kxIUzAGzAY40lKTx'
        b'Pj1sYwrTQXKrj6sxadX1Pnx9/3uh9ZCcYBIlCWSibnXw+SLeMThyxOEIC8gwh92HlCRQfeE0pHJjwy6xYW8voUHvB1SX6GfDjuksTCMFQ57SgUIEmJtFbx2b82jg0Pbc'
        b'mkN6/phKGmKg2cJW2LaAJoXtYllQ9G8w6Wkey5eAOoTts6syaFHfxWiNiCxhY7LAJgKT2GNd5QiSzjdsc5kSF+BaHOpLzAUNizpJ3+RgGcu3L+aIyXYBw983lBnK9lqN'
        b'wDK2eE1ANVpISzw/nIrPzO/ZxgYkgx1WFbW1a1LQAldvrAY7CjXo2/PhW3gGb+yxb2PtACq0fHFCEKJEs5gkT7ex+IbIeECXYZgpOgN6ZcBYOOgTsr0cSU/DsD7mfkqM'
        b'CoF6VUNW8QX+RzvIiLqa/O72eq97pYrK0apgjdmsSKQ/7WDsCPDgyI//SzE4cv+TEPybsmGIlLBkBKYsjkrjGYDKZUki+3zUhEH7QuTJZLtLzLHi0wyryxDTZvClOUzA'
        b'QFq8aE4SFf2r/Op+fHYAfx7AnwfJ1UADesTxqwdJTb+7talefYhu2+oCy9RDZNUMN546jJSgPkyGJ02KWkCFAvMdFevqgW1fVudH2+eo1fDqFLX6zZvG1vZ6YPlLU/89'
        b'Q1a6+D9Anv4/P//KAQTC5EaL4X+WEwTp+MMHlyWHjgvwaODEwwn2J/Xy5+z16b/+Jxv/Y2nZKWZYJXH2GbACRW8z/hY6JXFkPt5NOgfXpWCTiTsUBOpnzYJSUcXTFhVx'
        b'qopItTRNRRc40fS4HR9K9NxuY4m21XXAOg2oqp9n5rJk9M8OQvbRQpzR1eDpQC9IKh7X4bFIQ12n3+N2RzPdbn9nB0kCUWyGliTwNMUdT6hvJftuSLAtndTWrnS2es6i'
        b'8xDUHZUEIBMFoI56O5y5nEs1nhcJ5KjW1M/7X7lxboM='
    ))))

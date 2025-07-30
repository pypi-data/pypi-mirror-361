
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
        b'eJzcvQlYk0f+OD7vkQMIh6gIeMWzBBJAUbytt5wBRS2ilgQSIAoBcqjQoChquEHF+wJP8ATvs+pM2223x+623V1Lu91eu629tt12u13bbX8z8yYhXGr7/X6f//P84cmb'
        b'N/PO8XlnPvd8ZuZD0OXPE39m4I95I77oQBrQMWmMjm1k9Zye1zNlbBOTJsoGaWIdp+M3Aa1EJ9KJ8be02McisUjLQBnDgKeAcQYP9B5FxQxI82RAcYhOovdM99JJ8VVG'
        b'773p1UfvuZF5CiwFOkma5zJPo6fwHQkicUoK8MhReDwY5LkoRy9PLrLk5Bvl8wxGiz4zR16gzVylzdZ7Krj7EgzofSm58PjSzoRnMm7vw+GPxPFtnogvdpDF6PAbbZKW'
        b'MOWgDJSwxf42pgzDbGPLAAPWMevYFLd7DAnAkGQpOHWme0eJ8WcC/vQlFfO0s1KAQq5uB9+Qx4tyCUjR4TzA3wWmRE1CyJxM8LFQ9qsnW0CPUNLKphIoWTuwc1mcC1Lm'
        b'sSHN6Qqps4HOkPJqayS+R81wM5eiQjtR/SJUrlyCylFVxIKYRfD23JhQVIOqFagCVXNgzmIxOmdBjYaAr4Yw5jBc8vA///mZ5lNNbtbnmhC9cluoNu2HGO3nmlcy+mXm'
        b'ZOWy5zcGTVwGNu6QWN+JVrCW4bjEiumoygtXGkaqTLSqQlFlBAukaMNQeIFH54xwk2UIAQnftQ6cDatgHaqLxzlhDayTAB9/bshQ1GTywFkUXDsbojARZBUuJPGB39Qs'
        b'U36x3ijPErBkeruP1mzWmyzpGVZDrsVgZEkPkIEDQTLGhzHJnEVbuHY+y2rMbJekp5usxvT0dq/09MxcvdZoLUhPV3BuLZFLC2PyIfde5EIqCSYVDyIVf+LHihmWEdMr'
        b'+yPL4sFhwE/kl3Ukfl4I9yyNV4arVaGwIol2sBnWOfpYGSVCLX3R5lwC0mK/F5lXRGBiPfMq80PqO4NLAMWo/8RYjUD0iR/QbMh4d0RSoQOj3nuSPv1dwSrmTRYUzFRo'
        b'pnyZUSgUaS/iAB725K9ZjdJk83DU01cCMOTJX47SKCfMXgisKtLz9anpXrBZicEpR3UpkQsFbAgJV4Wg8ojQ2EQGla0Cy5dJE4rReQVjHUrKtCRN9cKvE6/yDEGV8Bxs'
        b'5kEwaomBt3i4V+JlHYzzwMZQORnOiFBYCfehGnIvAV5JLNqmG09zzFiv7DLeKwfQEYfXYYWCswaSWo7DarQvXqVA+1BDXKIIiFPYgAnovJX0/qRRy+Npd6JmEBurYoEX'
        b'3M1i5K5fSqFcMxheQ1VJqDIuMTw6C1UkwFM88IdlHCpFB9FF3AIZPdgGDw2Oj1XGqiiGilRm4IMqOTU6B49YB5AMN59GF+KhPQ3nEQGeZ+AhVIZ2WQnaesxElwTMToyF'
        b'R2WoRhGLm0DbOXh9NmzFvUVaQDdmwo3xY6NiUU38ZHgF1SbhenyHcVMCUL0jCzyoG0FyxCZa4Hkhgw86y42BB+FunGUYqeVENjzmFYPHqQBVoep48r790H4O1cNd6Ph8'
        b'dM3xPmhjNGpFVUo1qoV10lhluBh3ywUWXUAXp1sHkrbKuaAwVJuA+12ZBC8rVHEi0HcIh7YPHyU01PQEPBGfpIoNw11bEauMi4jkwmMSxUAJRGhPBtwiDG8VHphtBJKw'
        b'cNQwPiYxnAFe6DCLrsBbU60KnGMePIcOxNMcsYmoNjkkHhN/LR6sOlg6OCVZJQazeTEqnaa1jsK5pfAmqsSZK5ISFoTEJOCMbWifOiFpMcmonCyai5rRxU4sjnVnxkcp'
        b'l7czmIdydt4usovtErvU7mH3tHvZZXZvu4/d1+5n72P3t/e197P3twfYB9gD7UH2YPtA+yD7YPsQ+1C73D7MPtw+wj7SPso+2v6EPcSusIfaw+xKu8oebo+wR9rH2Mfa'
        b'o+zj7OPt0VkTHHwalPOYTzOYTwPKpxnKmzF3TnG7741P+zoYSWc+Xaa2Et5Z8vQygW0EzXAyDneuAVvmUiREu2C9mpKaWqWYHqWC5YTS/DUcPAvr/a0BZLT2oFPwoDoE'
        b'VWEk5AC7npmxFB6jFIa2YHSpCIMtyhjMeYbycBMm+GUY9+nDC3A7vBymgBdyVKgcY6UYnmTD/NQCbVYa0XkyZEo89iPhbT6Wgbc80GZKNYGBsDwe0xx+BHfC3bwHA4/B'
        b'+uX0mQnZIzGPiSGgeKBSPoaBF2DDFGt/0mIN3Bo9fHhYuIIFLLzMpMHN6Bp9Ag9mRMbDk1wGJlUxEOeyIWZop3wA7YFHQuIx+mBegpvbBU/zIxh4ZjhG1X748TPjE2YO'
        b'p3jI4CprmYTV8CZ9ATW8BRsIhh7AVFmRpGSAOJodMFQlNHf7KVQWFhcbjGktCb/4DNZnPGMNwk+W5KEjpDp0G7aEhahwqbXsGHgEHqatwaOwSeqPTsej2hD8CkZm+qoA'
        b'OgaoauoKuJPQZkQcAWQ3M28V2klJEh0RDaOUoohVrUWHsHyEt1lox2O6W2BBl+AOeBRtwsNYlajEqG9jnlwFaymcU1BpJtyHeRuqJE/gBWbRgDkUTnQAS/jd8Up4ZKqa'
        b'EB4PxMGsJ2qWCOBs4QMHwmdRVQw8g8uVMPPQUVgmPDqesgTjy0nMPMMJpJXM/FWw1SrHjyJRIyTchdQXFi5GW2Jx96hFYEAOPxb35kHhdfb1hU3xYUQyxKEaFrND4CFm'
        b'4Q4/dDCTdUN+gu+dNSCs/9gZlwbElmM9p4TDlMVSyuIoNbHruBS3+950NfLXXQPi1IZnvprNmafjBOXGzz/T/DbjE0159if4m3+9esZej5goxpAl935uqdIrdcPUnZur'
        b'q2WDZ/wnq37yZZ8tGvFrMvDGfdN8n/XybxUSqt/EoctYglAxhmqSFKgmlkqyZfAYCBjFcythjYWwy3BLRBdZtzxKkHUV6KaFKAlWdHYmJWJlIkatCnZdhxY0FG7l0VZ0'
        b'nKFVDVoQSvIloQp4LDIJ1pIcnqgejzw8Gk6VKWhHezBNCJkSwmEFzjJ9AvDhuGGoNtNCUH/mVFQXpoohIg3Zn8T62EUWbkJ1Cygo6KJhGQXFISWwiBAAGRWKjqKToiRY'
        b'MdGhknVRkmgqVZHa+TyteRVVvojaBNZJGeHfh/FkTH2deRV8O6czW9o5synTRJihyY+ksh1V4ntCVqb+zppp4fXAqXyVPUT5olzqRiTcSMgG1YoB3I1u8ErMG7w0vevi'
        b'kwVMZLPYX6GJ94iHfE94OLDuFjATFPr92rrPNMvv/P5u/fP37ta/cLF+a58XfbLeewWALWNmTOJ/3PYu1qUpQbelwcp4ZQhmnPEM5hGnWLQBnizqo7IQ0sTyfhu62E2D'
        b'Rk3zMZoxqE3ob7bnwbJaDLkdmvJ6IPVjTAGgQ1Pm8jNW9jw+WC8OdA0NKVJOqiFoCErBA5/eB4e+0WnYmhVGNS8GhGD10cTA28gOL3QaHcbxSXECaBNkKaMWXiHI9TId'
        b'b+RjzE/Pz8iymjO1FkO+sZoUpbyHtYbg62C4qT9muLSzkuJg7TNhKrWa6MBYPeFAGLwgQnvRJrT3MeDIfigcHk4g9PVuIBA6Xg8P8JjDxuGW4UVYqibapT8q4+AtBl3o'
        b'HTsJ58J6DrEWuSz+fwNDGdATpxR1zuTk1UNdMFBebeddMPwSbr2pJxg8e6KSmrvf8+YEnBBw3Xpqxib/TzSfa17UfaJJg/d+E/ia3yt3YDJMvn/nxeSX8WfUH+4uR79/'
        b'JfXlZPR7vqFGF8NU/nnMR4Uzczh5AvPp+5ii5g3xHdkwUsFQPuk7Hx4zPxMFz8SosbHjGPs+qJ7DIq7WoGAE/sN35XFdaEeUnqnNFYhHJhBPAMv4YT4nZYqDzTmGLEu6'
        b'3mTKN4VPzc3HOc3Tw2kBJ/vjtaZsc7t41Rry7UZi3exP1kSwxjTERWyE/e10I7bP/XsnNqIoowZ4dWBYGsIWCCpPCMMqJbXG0TZ4Ab98RZIa6x/wMtoOqyQLJ2Ht7kkP'
        b'dGU5tv6t7x/jzUSjf1t5ZVXgyeyc7NxsdaZam6Bd+X6z/hPNSe0nmtwsz6z3chmgf1X88jdG4d0es/+83PrInQX19xOb5K6s3j31iamPqzNIzga3zvjyIZ1BmC66NhGe'
        b'DOvcE+w6eBMMhNd52IwOj++dBLu5lP6H4oHthvi8epEh/PgBxkzEcUrsJ3JJvJboKTFaflu1Qh7dd7fuS400670EDmT/WbzO618K3kJsNyzqN2IJQCS/Won5ChEBXnAj'
        b'6AMvcrB2EtxnCSfv3oY2+1EBj438kDhVONwLt8LaJNwbdWGx8EwI1RhAaro0C9WstozARbJRS6qgUHTOExMTjHbwcGMEslN1aNoguJvWrIhLUCfGYTuOKigWdA2MHCEa'
        b'XIjq3HHDDQu8rcbMHK3BqNel69dmulPTUDEj/JuGOYsosEDCuTqopcWBa4xpuAsjSO6Dbhjxkax3jCCvWDIHnsImL9bbYzAnqI5PxGiBWYMYjMKKbFOxKKlY1GnknChB'
        b'FHQnR6TW56/iyt04Ig960huk6lzSLSvUHlLdPCCfux6u22d+a/nT2dEeEz14IHgAtsAm1BKmisWkfAlgo/0wMwrWYRtiIzxF3Uz54J++Iz1Ch7LJ7zE/BV40jxPcQ6tF'
        b'DIubXBup0gxdV7BKSLyr7gsIEhb46qbWDCsEhp2aEM5sJCPz4d/jtTpts75Z/7mmQFuuatZ/innBpxpjVujCFm3anXp4sb5P6AvSfl4ntezJbS36s9rT2gDJp+zrsuGa'
        b'yZvfYmIGBPf/55uR/b8G4995fs/C1EGBrS3Mb1vbo94c21/M/HGsOKrgODZWnx780p39mGUTUw9WwstwczwdJuIlkcJ6uCmMzY/v3zOfeST34XO05hyKbnIB3Z4gSqon'
        b'/RcUVhnLMzLhjjGN7EBBgR13MOye22eEbBQjSeHjbhj5zkN4FMEqI9qYhu0zrLli/Rmd4fsTG/r4qEd4kZkuXmT21zMn0i8e3XBQpraSBFSvR/uJbQciVqENIMIPPUsx'
        b'Zp9OBH5Mwzr7DE3utgX+AhrVTeZAznpyp5HlrH0amAiT7+nSzqQbWnfd482V+EdE2EbVK2N8YKTfnD/suXTguX5vfsS+OUk0IGZDc87qb5YoNs5hDDPUczMLPX84fm94'
        b'+wf9pzz4R0nDi0HTluwvfDJVuVy37c9bm9dsyHiutPSt07KEJS3b5ibWle8r2v/p7X7LV7558uWFudFvv3o2uMiq//e5i59GHfrrwi+2+b4ycueKGZqPftP67bzv70sm'
        b'nRrh91S1wouyN3iwbyysxSZfN4OPWnvw+lzKhrMV8JBZqVCgyoRQVaxVFZqcTN3eoctEWL29hvZZiBqF7cYybNZdUMMzFodf3BuVDoJbuXFYRu+lKkrRTLilu1McNgRj'
        b'y3FrDjXl8tJhaVg4KkcVxIGRigmillXB7ckW4lYrDkLn3KxKWkkrKnO3K8eNpJQl08KGsDgVurUKlccmYJPeC7ax6AA6HGehTGWbAh6AVQPCwmOVoYpwVIeVZQAC5fzT'
        b'tgCha05hJeIClREr0WXSmCAhqGl6GcuXKxaC0+jZEh01YfZFuayYohkcfQZb06eEqVUaeCMWdx4LZFJOWoIud7IGH2JxigusGbkGQXYoBWKezGI9zA+Trpjpx/D4yv/M'
        b's/xPPMf/l+f5H8UiMSZzGSHs0a66BvTYTJCLiknOa25U/NJDDFDiDXkSG+Nbw0ISUSU2xkctEGNju5WFpagebaINZordKM4ff6ROigvhiIlhY4JAibhcYhOXgzK2RGKT'
        b'mBOKfWxcI7CJm5gS6VPA6M8DC1MUzdCWlwJjQCRWuW1SUs4mJjVMBTqGlDT9ZBMVLDGAEpFN1Mg2gTlgxe7lbIlHiSep3+ZRxpo0tCUe3zXbxI1cE62jkad5A0u8yjmc'
        b'z8vGZnEGYPM8ytQyDCisNs6hpWQYPlm5h01cxmCIPcul5K6MoSWltKS0S8kXbDLT5+UyoYQTVpz+oFBTzxpH0lq9yth6PEDlTDlYDcgdhkekY5sYIXc9Y/yR5mMs4iyW'
        b'5k0u93LkTS5nSd2unK/TnGKaa3W5yJEL33XKdVrHNUp0vE60CVuzc0AZg/vZWydulNi8G6U6iU7axJIUmzcue1LnYfMOACXedondC2uFnM4Tl5PaOFKuxAf3gU8Zo5Ou'
        b'Ii3es/novPCo+BiHu9J5nP6dTkZatPk0MQHkKa/zLvGxsfWsaQaGl6HwsqYhOh8bLjEAM+4sFufzNcptjI1dxeFn0Tpfcu9Il+r8bMLdcLfyabo+QnlXHtKar81X5z+B'
        b'fHvjPOU2H3r11fW1+di8SX3kmdHH5kueFGyzeZPfFmGM/fBb+OG36IffgjV9a/Mjb6frj/uUNT0n/MJl3sV3Ulf6O8Ivko7fso8uAP8GugGb2SBg60Ph98OtB5Z7kxZW'
        b'etr8nDDYuHrOFGxhbL5lzEbGKLV4CXc6wQgPUi96IMnFxr5RNeYBq5R3kpKsQ1JSy524k7IxYa3wLGFszEqwlS3kSRUOzbRdmp5u1Obp09MVbDsbHtnOWLoa9Z5Tcw1m'
        b'S2Z+XsH070kiEcDFgzJz9JmrsBXXYeh1ZHvAyfNNDxjlfQLVA8/8LLmlqEAvH2XuBqbISf1yJ5gBZNLaRgQ5a+bLMchljAPkrA7AMJMMpeJz9UNYpImwxR+dEN8nTT7w'
        b'1cpXa3OtejmGKWSUWUGl8INAs77Qqjdm6uUGiz5PPspAHj8xyvzEgz40gdy6knh67euW01n6gYc8z2q2yDP08ge+eoMlR2/C74y7Al/vC56kB8wTD5jhDzxGmZeFh4ev'
        b'wOlEwX3QRynPzrc4e2ky/ihk7SKDUadf2+65hAA8lxiMOAm3am7nM/MLitr5VfoibEvjlvN1+naPjCKLXmsyafGDlfkGY7vYZC7INVjaeZO+wGQiFm27xyLcAK1J4d/u'
        b'kZlvtBAbxNTO4ZraeYIG7WLaPeZ2EYHF3C41WzOEOxF9QBIMFm1Grr6dMbRz+FG72CxkYFa1Sw3mdIu1AD/kLWaLqZ1fTa5cnjkbFydgtIsKrfkWvcK7Rz31l1ywqpnk'
        b'wlCpExlfJai0hSIXUWt5hkhEGSPmiELL438plo+CsitjAllP+juApuP8bADjzwTTFD9xP3wvxqkB1IeL5SpLJKoMp+JfLJGjPqygJvuzPtTTG8j0+xm3+DPL9sOlsKxl'
        b'6XwNVhL2y4idlYhq1cq48YOxTpPOTYIbjZ2mB4gcFDup4QN8wXKLtYFGQGXRa1hucSW8jTMHF8osWLklHwOWc/s5It1srI2biqnGlIwlIbMa4G8sM4JAI4v5JBcEmrD0'
        b'wRKJxzKAJ1LDrLPx2Qyuj8d1J2PpxRGJgqXgXkx7RDaIdKQ+kY7HdXDkF/7GUpHUU5gjSBnTcR1f0KwjMlpkk9C2xI7nIqF1Wg87FdDfvOM3PxUUymws5WIiNSZfNRlG'
        b'OpbJ5KJ23ZE0hcg0i4wwZ9Zb2jmtTtcuthbotBa9aQ55Km2XEOTL0xa0S3X6LK0114JxliTpDJkWU6Kzwnapfm2BPtOi15kWkDTiYlOIH4Fmbu5VEl2hS3fWOwRzMfNo'
        b'imU8xhaCZX4CJmAsEFODimCXH0P+/RkryYrOZpuE6ftYWBEHKyLIFGSiMGUYBq+I0E64H17pZo+Q5olaRZvrNuELyJRvlpfT+LExzknXrjaTS8nS4Us5GWqmAgv7laDA'
        b'D6MZLmgah1HDG6cwRISWMV7Y+KFCCiMFFn1MOVfuRe4rSNQOjwEhzXticGRZUpdH1MPGEiTqyb4nmE06lTpUvyVA8DaiMYDik7hhjtxTzWkRxnkWN4ZBK2NWAQwWvrNh'
        b'QEo4YwAFT4yxex65wyk8xrZcG0fTAsqJRoPpgGhc5WKC9Q6tK8BGap5ewtlovThvZbkYYyuHtRreKCP3OJ3+svGmAiJzMBXRemy8o44CrHdGYr2Tt4iy2KIPGKxTMqC4'
        b'H+4sEZHKNMALp60TGT2FbxLghekE06iNIXU4XPgY6YiF3C5ZrTVRVyiXjREb81bTqjWmmQTh4gTU7PB+EikuYLKOUoIeM3PpY/PKDiSWpVMuWYAbzjPPdKEwRleW9aNs'
        b'ErNDlrDCYMo8ZawMo3YwRuAhTHGkNjNTX2Axd0h7nT4z36S1dPb0djSAJXQGaZq8ByZyGkxEE1aSBK9fy/W5dgnpNkzLQpWZrtfzcAE0kXFOw3GCEBiCWXFwUHFw7+/g'
        b'VCq0pLpccu/5q0SS1gWOxNHYeMbhTACcfIQwRXcNXi2OT1CrVSFjYLNCDLzCWXQ0flg3R6nU8W1egi96kIZ1vzSWcgCx0+GRxjVIBRcIJkiPLBENWZSWMWm8K51wCwnm'
        b'EkIYI3kmsgMepImpC0TS3scRcDjPkKtPyNfq9KbeZ62p34/FVWJW5DYTwv36mRAng+oxcq9PbrgZngmJSQyH57NiExcQqz8pIVa1EJUnpYQQBkrjZeBG1OyxdC1sNMyL'
        b'kguT3TfXWj7TfK75VJOTFbozREui9l4UovYyPte8lpF2551Rm+82PH+xfutWpnnLpIOjNg/bvSFqMIg655Xt+RuFSJhivAR3zEQXULUK3baS6LBCh98i2MrDLXPCqFtj'
        b'KDyPrnf3WaDL6CA3ZA0QZqjLbTS8wW2CGvhwRtjGDYPnJwievk3ocoYwRY32LRU5pqhx1lrLXFoDLAuAVWtc8UU0KioWXRI6BFaS9iNQZQKqQ9XhczEksALVYS6OXwLt'
        b'8UZNqAEecczBPIJNYHvAYDRY0tPdvdLrQQ7RenyY4uBu6BLuLOCa4zHrc7Paxbn06UPmeDC9FZL7Amfbpnx8yWac3slS/L+vd6fhw0DpHYVnCSjMYaog8lScJXahMf/Y'
        b'aNwtsKnnSUWJWohYqhlr6ogMQ/XoANzMAR94kvNbB49bowCNYbgBL5EpWhKZGoOqYtARZyQZxnqH5+3SQgCWh0hQA7oJN1uJdRM4vQQXOgn30SDGEIydMSpUCVsWhcQl'
        b'ojpleKwqLpEBRl+PaXnRVA0ZGQRvB6NDKaolMahaEZeYgPM6yApnHAd3ikfCpgzD7gl7WDMRPPnfx3ymeSmjWd+sTb2zG16tb0s9vkmxWZPUsmXm/qY9bRVtZS2p3IvZ'
        b'4rZVgZNTXw6szC217QwWj2m1eZglsyXmqDfYnT47N1ffle03gH+u9f9ix1VMXYQNBsNjsBRVxcOqLBKICPghDDw8D14QAmS3oXpY4fK+rVW4/G9oH7pOCQ9dQ1cmCNRZ'
        b'HpHi35k4fbQWMjk/MRZuCQtXxahYIIZHWdiM9kcO1dEpHrRh+qB4uAPWhcclKmNhjcu/KQKj5ovSYB3c45zSe3w90TvTpMe6aXpevs6aq6cE1M9JQIXU+cbyDt968dDu'
        b'2NuptJNaCXVgkiISr4OURL0LIVagJ7OLqEz4YuxEVA0BvRPVo8DqRlkuj3mMk7Kc+imhL2mWx6+gr+yepodcrgIXffmohcja0fCSO30R2rqKjhL6isu2jsE5lqCb492I'
        b'qxfKykb7CHHBFminxDUVXZMKpXqhLGRfJhCXdv3DIyd0nSInFEw7k9XVySKdmqvNy9Bpp29mHA4L6yKCptvDRphR1Rprj3wfbYuHZ2ISYa0Le9GOTtPb3Fh/M9y+0B+d'
        b'AfA02tIHU9ylkTS0DdPXoZEOx341qlI6pFI4PLqQGzMBben0QiLgFg5BOahgBLBkpF0clKOKAI9HmKMjzNNR5dbxKW73DwvLcFkp7hx0Er63RaEN8WS2MlyIW0iJCUOV'
        b'aBMWa3WLMfWrFKg2IXaxazhFADbqPdGzM8fR2ZgHeh58pfAjUzQJQetChEBwc39cHa4S7o9w1SrEgmPlIo7GxxCOmLfeIzCVc/LoQ2hTfDyZLsXKSAiqeErgnAtcDS/G'
        b'WITaUCPuSnRODOsNGQGHROY8wgEiJp0y3afxdy9lhfsrtAnaXKqMKE2fal7N+G3Gaxmx2m26FzPO6D+Z8cEfI8HiKcziqLJF9qiPXmqLbGhdPHrM2FJ58v5jZXP3MyMH'
        b'vFT/G11fX/Dm23frX/r93Zub2urGYP2FA/zooGGz5ioklIlGW2aQAfbme5i7WTdTmEE/MYJx8lAnB4WVSoGJovPoAM2lVE6IJ2wS7UHHu7PKRegWZcgj0bOcY9I8ydGS'
        b'NzoPK1ZxgViTaqHRfJnFsDWehGoLM+vhWPv1X8cNnob7dF+ehUZTnnnK4sxBpjy9JhjgNhbbzecTBbZfM3e0uXsMyzx0ELZ6wUu/nGf7kPCU9AJTvoX6ByjTDnYy7fXA'
        b'n6XeImzns/507sSfKR7fnUfq1+ozHRyyw7zoXLNA+yLBbukw7x41peqYefVxFaBMfTW+1BGmPtzJ1EvBN72zdetyMth71UZzLxrkIzkJifLfNgm1ieaiazPgpVGwRQGG'
        b'JxSiHf1WwiNody6B9fi6IP5bfzDjqxTjiH+yl8f8EDeNoVPwK2fvZlolQB4ZVDTinbFetqGAJtdz3/g2+DIhX4EjQT+lDhxVBgyDLyk5Gt6efP2HUQnTfDZGBv736WU5'
        b'XrWjlUPuZK6V+JaiXaNX9/uArxp1/+MPguRfN+6ceOvnJ6Jf37dpSWS07MSCNv9PQ94XtdjNfyj+OPdqWkzuufkj/Ha9mVbxl9IP/nLxauquV34ac/3db2pf7Vt3x3Ls'
        b'tHmH4obm3vll7yxf0nZgweUv5vRlvxw5zwYHDH1l5dSYA3d2hv0U845l3GevL1iYtPdtL9GOfjnr//W+JMGkvPrdhwpvSmchsFKYCuxkAshgjT83xCuYzifC6sHru8wl'
        b'ohYfrM6o0E1KYuj6CBEhRHQcbVN1szUKUY2F+LvRblgbI9CYcxhhOR4xPISwwmcoaTdaJ14BT8npDOMKuGMOUX/gHqlDA4qEl+FpOoGJyrVheMjz0eFOoy4CA8fzuAU7'
        b'arTMptnCNI9rd3S1OtJyURPcHkiDbOHm8bDUIW5cRSWgPzwwB23g0EWsE58V6PtEITwvROsQwISgzo1o02IuBO1Ch2lk6HQdOiYsnoidSN5MCo+xa5EdXaIcBB5N4rsa'
        b'W1FPcNywfAtt4RlUBg92l3zpHBZ8T8EbVHGchNXxc6gqARMQvIK2TwSYXTUm9kKhHr/USyB2MR8vN75BOU+Ik/Osc6mLrCfxMRKXDL7jWX9fMb72Y/2Y4sEP5UOdFEix'
        b'I62D20geB1bWtBZ0stDWkA7spEzaB/WuTD4cQAwCnZXwTHckpKe3y9LTC63aXGFGitqDVH+l7bZ7kxVrWrM5U4/5qsPc/BV+mham3cNRE66FvhaJ8NGT1yLPpayfhGUC'
        b'ZJht0iVjG9Gzw7vwTXQA3XZRAQsmw1tiuAdWoz3dnBvO6W4zoV+nE0fP6QT1CdCoVlbHbfIgThvqmBFRP4nI5ZhJ1lpwBxpx56kz+S41u8xa4g13KN4ON3GWxKGW8eUS'
        b'rJaJsFrGU7VMRFUxfh1up+P+YZGq3RVvkZqGXvWfmdxJ78Yqw0bBrh2sVbBUzbSg5mD3PFi0o4on4WYeBM/hY555hirwKcEL3POEhcYMgOfFINjML1bHGZjRAYw5Fmfb'
        b'OyfqM83SO/XECn3x5Ka2sraya3sMTIokXrJK8vasv6dtCd4y/ILPzn7Hx86Te3+kHzMh6k+Rz0X9OZKPOgrGZAeDSel+X9oW2xUKniojZCnJ2TB0Lq1bkMcybIYSBqpC'
        b'5+BWdwPyBDoTmS2EiBjQ+acw1NMGYcYHKyLomjF/PQdPw83LBU1mvwnr3AKbQkdgrZNRRcNTTi3lcWjQPbo6C6NBOjEFKa/wd/KK9UDpKevH8JyUxYblwG54E+4qJ9CM'
        b'uJ3LzDW3S7OsuZTS2vkCnLddbNGasvWWR2okvKmU3G8gF7KG2lTmYg/rKXl1VkveCuydQTwMVgWrJu5ywiJMReRSTDkmpds8vSUnX0ebMz3j7KTuU8E2F2Dr8OWE0xUr'
        b'ZTFpE06rnZLcQdjSGCVsQrvdVxxOkYvxkNcuo2aEdSZdZArei8xRLhk8BHSbq+lMjJ1ma1zECGiQ5OMtn+txEqV7gFqQY5lzLaxSmcnCR69CK7qM9YIrqM2yGl3yWg1r'
        b'fAtk2C5pwRblNHRchFr7oHNW4idFe1FZKC5TkaBGNWHqxdQ4jsVfFUkqulB6KTyKjWZ4BpUrw2HbQupuvQive6LbsMr3kQu8ORoh8r8QHgp6Y0OEjv0S/cNgc4JrIJ+C'
        b'O3DORRyqYuFpGuyai5rRbUKKwmuiHWGwJYQBwXArD2/CKhO64W9458OtrJlMs0THPvuZ5rcff6pJu9Na37S9pazlxZayMVWFTP2l+j4vStr2TNm9MHDOJym7A8aWfTQl'
        b'8LeBVZ9PDgxoLV0UOdYSKYo6itkNCeR8/S3/nQfzFCKqTwy34XbDFahSiW15PJDwNBtlLaJ+MFiGjmIrP4Yux4CYqPgJDDy7/kmqqyTBjaie+iBQJdbjjqJWyqN84QZu'
        b'JdwaR13HlonoFM5SSdWZZ+ExjKWTGNgmRReFMLNmHWwwSDotpCmK7I1i3ALVtQUFekyKhDV09mStBwvIzJCMTnp6MsWhmGmk5xoy9UazPj3LlJ+XnmVwN4PcKnK2StnG'
        b'QzzDjJCDku5mfPldF55y4SFRaGTaOB5eCIxPUhF11DnosCaJOA3q8Legw1L7BtsuJ9xsHEcvYX4eQztaBw/65SXMpqt34DWPjDDSyVFPoOPRLBChgwy8mIhuU0FXPBle'
        b'woTUtmY1ulgIq1C5TFpQKCvkQcAULnsI2kaXxosnw2ozVnbbPLxXe3v6SNH5NYRgC+GtkSIw0p8vgRc8aMwAl6vERsXReCyYSIscHrVWFm6Bl3VWQlroUFQmPIW2YxKv'
        b'SAiNU6IW1ABPooY1yhDikkhwru1JkTrWtTNkoeYFr9kWVGMlC75S0CGMWa7yjyiLGQfcmeuJNsOTc+li52x4DHdfVUEhrFuDLqMrmO1YsD59BbWiK9Y4G36XFB5uWAGv'
        b'05Xp8HjuYgrtLni2hCgA2EyqSpAAX7SVW2jUWKllcxFugJe6VbkGtck80dV0MRgZy2OT4Rosp9qzlci+wV6YeC8Q2DF+TgFT5g2j7MBTj62X7UmqWLQTnouJhVfhFQmQ'
        b'TWPRQbRpPXUH4oquPO2lIqs646kPJxie78QA4SXK6VagDRLcxOUlVrLyIpBFJ1Lgdm/c/kgwcgW6SKXCKyM9AMbhyPppRlmoaK4Q/9svVUy2HvArWFGUG7R+GNajaXJr'
        b'oiBBGuMzlJ8ZvYW8SSUSIW+ISRk6yQtQXxMqQ9tGEHswjLibKqiLyY1Hpy7vADIflkpLQuA2Q+A3p4B5LiaUVX5VicltahTZz/Y79evHE736Nb/3hF+urH/fDM3J50oD'
        b'7x1sfjNu6964hIj4skUXZjx59+nk26UR2owPoib/8/Pji/VvXXvjLze+n7pxTeRLgUr/ycoNTVf7nj2d9dXU91788K07c6JHP//7AVvqr8jubeKebhYptw1I3Hv4SlbF'
        b'8THG5KkLnt/fpk4atOSDd75+YcvHRV9FP/9D/3H6fQ3GW296HvzhL4ueiXh+ygXvc3/0sR44rxg88ebmjxPa5WV/PnF7m/WTP0jj9DPerPuv8fm065c+yXn71efWffnN'
        b'6TdP5709M2gaO3PkqddNh97tryxcbfYI/NP23Nrcv9u+nBtkzp0ydsQ7/F9HBczWrvh0Ur/lysLJulHnAn64vTZAHbVi4KsnZ00+GPL1mdQ/vDTp3psb5nMvnlv1328X'
        b'//j871774q1DSSOb+97+5hX5v0q2e3784qfM6394ctb5ogvz1yt8BR1x80BYGk829KhSEu4xE9ZwwAud51hYFW8h4mhMJmzArIasHN4/YjUzE91SU76OTmNdYl+YwEf4'
        b'CahiCGbrmPlSC9a3BO2PTwgNp1z/NjoNgFcui44uMlDNkYOHGEwsV+m+BgQfyXxgFVuC9rAUKGySHoDnwpKUdA+B6viJkRIM07MsJsBrMULjV1FD3iCmM9OH+wcLzoiN'
        b'0+HFMFRO5hqJYEHV60TAdyqXhdoihJe+FVgYTyZecd0KFdpQosa60IAEfgZmkScp/AMwNd8QwrBR/WQSiU3CsFFrNJVIaP9oTIIEMlQlAbxqCmxm4BnMvhqoMIRlC9Cm'
        b'sLhEbF3zw+CmkQw8MBhtplOuVnQSbXCEdxPnE0b+jZPiMZYPgJf5GNtsC1kXa4gvoLIUnX5G6ZClBpZ6YnjUDC+7/CyD0IaOaaPbaMujnIKPZxK7m+/9e5R8VFou7JCW'
        b'84ms5Knz0I/1ZP088Yf1Z8jVk/PDaYGuyAsZDTYLoSsw/HEZH5zuw5KwIhKAJmNNW5xCuoX9hba8W1wkqeT5LhL1Vu9aupWsouIXT+5doK4hzhKKp09bpHDHepVjPxPU'
        b'sL4Pqoqn83uj4UE6xQd3o2oqMWE1PEdwXA3PJKDaJHgbtRF/L7zEomNYoNXRRSHjsZF9Jky1FLaoVaFiPNiNbBS63SeT66IYBjiVQxJj0m1TDODaFoPptDEGa++fFeCa'
        b'vRA91uwFR6dy+PdH4mH2lLv9LdRnG8wWvckst+Tou27jFO7ZKW+sRW4wy036QqvBpNfJLfly4ivGBXEq2aWHLOKV55OA1Ax9Vr5JL9cai+Rma4bgJ+lUVabWSAJODXkF'
        b'+SaLXhcuf8qAbSOrRU4jXQ06uQM/KVTOuvEDSxEGoVNNJr3ZYjIQV3UXaCfTkB45MRUny8lWVeSOBL6SKh3V4zfsocgqfREJThVKOX50KaiTr8Z9hmHqsQKrGT8Uirvy'
        b'z50VOzuFPpEbdGZ5yCK9Ideoz8nTm1Sxc8yKzvU4etsZl6uVk3c0ZpOgXK2cBCwTcJx1hcvV+bjjCgpwWyTGtVtNhixaSuhQPFYZWgIQHis8NuZMk6HA0u1FurlTfEBX'
        b'O8ZLTVesLo2Ft1IinNOLC5+KwVppSkycAe4WLZw0CbYoPNG1oklwx4zhk/oDbBY0y4KwLXaqGy34ORtY0pkWgIMaGBc1sHbfLL9fMXvXzT4jvKX7xi4qNc5H+U73iMTu'
        b'ARkO75VrOvF/ZDCS5rqvJxQ5lq4TDm7Y/8MG1kyci8Mm9f1Mo/p7jFaW9YnmviYv63NNrJbfel/2arUhQS+bmza4Wv61+k9TL/v8ySL/y9037wJ/Q5ZFW/4j98dTos9O'
        b'aet14DP9yiylXlmZoQP7pAHpd1r9XjmvDbl4X7PiztX6DVubyoJ0syK5bC9wcO2Q4GlHFSw1zfrBWngpDNZHqUIED9NeVrUC1VAhh9qGRYahWqJ+81a0O4RBFRlzf/ns'
        b'lih9jUlbQCXSkA6JtB6MIsHQWO5gdu/H9GPEWNpImWKFycHD3GL6HNjulkJqdOyUIETTdgiiRwDWwggFqBTCkhkMx5DRVb8OKVQK3nvIJNY0nG90NtZdnDTSw2JuVLcK'
        b'uvwZc/0VEXFKsjlTs68B7n/6EZFtHHXa/C+t8ReBnlwWErWVxHOhDWm5UZHjxkaPGR8Fr8BWi8W0utBqphbURXQeG0BtWPBd8JXKPH08sCq419sL1sFyWM1iQw5d8UBn'
        b'0LkF1HzIjI4DDaDAg/XTrKxkixzLWMfHgHrwSYlYo/GMnJLlQPiXFnzHmMlE4MWZtv6/GeZfGinj79wYJ65int0442vO74Hyqo+03ydz/vht0BdJipXZIwYP2D9J91LC'
        b'+Q92ryn8ul7rPyo26kefgvE17/9pjeG33x8Sid/w2PHcG/NV45YYP3nN9+qxfnrf/Y7NO6zoNrwajy74dNJAJ8Dr9OlEdIJGO1UKxi3xV5zoB9tUhQ8LbHl04Jop35Ke'
        b'ERVNsT3QHdujCLb7YzyX0oD/YuVj4bmjOuc8iitw/OEhbTRHB5aTrTgiu2H56w9ZC0um3WDtyiyC5benPgTR3bAcVUbAiqSx0RxYDav8wnGOmxQRPvUTLM7IgFCz/wh/'
        b'QA1ZuL/El8UW/HaMnuEgfGl/mnX7BMFmjQwIyCxaKBYQSR4tIlEZ8sho37z2QQsFRKJPbgyWUrs3ct5bmZUj1guJfwuIJ9sSSCNF346pnz5aSDyg8QNyPOaR86r7ppYM'
        b'AHSZYP5sWDEKPpuCalDD4vGRqJIH4oUMPI1fgxa6ww4E40hN4Ym+fgmLhJqmJLUypVz5eAa8tyaVaxDTmoZAbCunQFIPqhEBdA7t4jTMdHQYa5DR+LnXksQOz9/iGGzW'
        b'oHJ4C5Yr44iHk5g5NH4D1YURWwFWhHkq0PWpdH76glIMBg3C4moGkL0V+Lk1FdDl6DF5o6XSpSBSXDgv3pSpmlCQ/Fp02ojBIroh1ky4De4LQfvRBSyCEkEirIdlFPg3'
        b'B0wBFvJGhukjhsY8KbzRW8FPgk1g4nDv5FLTvcxGLU3c4jcd2LDZEjnpYOJxjhVyekapGA3b2EcqLzUHev6tmCa+FPdn5iJXMJz325B/L/+ukPjfp+czDWxyJAM2rLr3'
        b'zPhCmvh+Tn8mko20+IDSktR1p4Jo4skUC/gKtGKWULo6cNGH2TTRPHox08yCmFaReeJPMdOE1udJtzIhXOMgkaY0O3XSywk0cXBKKrgK3hvPy0uLU40DvWniBr8RTAJb'
        b'UOxZUFpyb+AUT5qoGT8EzAHfp3okl9pSV/5uPU08PjiBaWTLn/KUl67anfzFHJpYvyyAUbLArzVcavqbMUxovc/gPzCNHChoHfDGnH+ujHEgg+I5UM4AeavOPKbSa7yQ'
        b'WJRjA98DEBI5ZfPyLU8NEBKD9O+AqwwIac2ds5gfahESV87zBoEk52h57PgiB4LZlhSAUiaV5cB7GW9GvPSM4fOLkxjzYTySTd4TFi+4UfvmDL/PD+764u1l/zCVDojI'
        b'n/gl6POOxO/dAa0MO3PJ2LtxYW2jmZoR8evKpu6S2zd9V+KXPrv6k6+HjRy398uzpsTEf0/U/Wts6ltFt/j85iOvWWMnfOZzo+hvjY23jyfqEq80j5Od1nz5n5d9k4at'
        b'+s9wr6DlsQP2vLe8IPytuMt3562Tj/xwk3jeZNORjPELj4w6tXX31HTFqKyUhPi0BaeG/7CtILLcZIo8WKLLbsw/2U/ks2zUuq0DvP/+89ftq46uqmyTj/r3+NHlxlXF'
        b'Z3cd/lj1fGjkO0tWLPb3ujrvH+8O22WuGq+9VulTtbH+TPPCzd+vLbz3j7LgV2LKnh+/56XiL/Isb932vv9ewbjzr+h/fvfyvmcXTu3/FzQz8vUz35Z/dvUPn74gqtkX'
        b'0gpVDakfRn/5XviX708f8t6wIe+3Jaz+vP/BF+MPxUw48e579+1jP9r1Y+WzKdufq/30UP27T7/x5b3fnzj68e9u7/7A/x9FLycO/88e3b+3rP60Gsp+t2z6iX8XbRd/'
        b'sb35k/98mP8P2/k/3jqZntD/v6cSzn2X3eidGOMxedf6YecW3feeO/3UT2BicN1SZFNIqXNhDjw2zrU+vD9P/RLxFmExdjU6DI+EofIIsnPcpQmwiUmGuxcKLovLmMVe'
        b'nikLi1PFq0LVIiATs+gWqoU1wnrwWyNhpcvJvgWedDjZ0W54hDpcvNEOzDowg46Fp3mADvLiXHY4rFpLxV0a3FKkjQgLV8QJu2eKgC8q5fKXjRG8OQ0lI+F1dLbDn+Py'
        b'5mwz0FiNLLQXnekU9AQvoh3OzXvwfdUvjUHw++Wz5o+tckqdopTK4Qx3OTxMxvBsgI+fJ8+4b5BGvofg70D878+MxGJxENZIfehCPTKt6c8E4G/Pn1iW/UnKiWkpKV2x'
        b'IsPleDIHEdy7RBdUVRFdQtMucRih7SJqWbqJ8v/5kkSsDteRe7pWp96lAdQQVtlNA/hbaO8awBSczwiPoENdFd1rWK70rAOIALRDrBfefBpupQ51uKuIzBu5e5DV8Ewm'
        b'rE8Q4uoi4EUROo0aYS3dBhXuQCf7dEwE0oBYP7SZg+dQ7RB4Fu2g/PH1ORjvxxmx/abJtQ+ZLTDN56fwQDpRSnfAuNM/S0h8IMLaROAsMZBrcselpgLDZ/96RWQ+hJ98'
        b'Z0wcXD3FB86Qzfkid/q+RDhBWvjE5LSj45b4zAjZsHFu8D9U73nu99v+Qex33xeNW94e5jF/3fmz9XeHza/wHB98MVVT4X35Xs0B3QdPT//ngYu3C/fVflrzbsjwAys+'
        b'3Zb031fDP71UF75ZYtg9b9RLH//9u1cXfpJW1iCpvHnC98Jbu84VZ6p32F/5qajgT3dnn6352x//evlM61u/Uyssh4t/ZL5kIpZf9lFIhHilyqSkLhs5ozJ4I4IFwk7O'
        b'8BA6QGk7GDXL3VydxMF1DJ7xgJtplDncZENX3ccJ1jxFolYTyOTjQT4/EV4Vlpocgc2wwT0jZhL+oSQw6hRsXsYIftu6GWqSxeEwI7vmjsuCZ7k58GSaY9cK1FgEqyJU'
        b'ahWqTFCIMZs5Aq8P4tJhbRLdH4PPQfthVRLVgZRxwkTPZiGIciCZCz0CK+F+p5EZ8L/OIx6bgziJmXKQUHcOMogERLHM6HkySv0sWbrLBtD1amLKM0zbcG6HmV9LXqPv'
        b'/zXcW12UTpqWdKP0H6J7p3Qqeo6L8lyEPhNuYIFvNJeFdqEjPU6Bkz+zjOkIJtIxaZyOTeN1XJpIx6eJ8UeCP9JskOaBvz0buAZeJ6oRNtEjsQi8TqyT0JVgXnqZTqrz'
        b'2AR0njqvGjbNG/+W0d/e9LcP/u1Df/vS3774tx/93Yf+9sM1Uh8rrtNf13eTNK2PqzXG1Vo/XX/amj9+JiX/uoAaspke2XJygC6QPuvbw7MgXTB91s/xe6BuEG6hv+PX'
        b'YN0Q/CtAR3cGUAxt90kQ2H2i1qjN1pvel3T1zxIfYuc8chpL0inTo0oYzMRZSD22uiKjNs9A/LZFcq1ORzyKJn1e/mq9m4Oyc+W4EM5E5gkcDlDB++hybNIS4fLkXL3W'
        b'rJcb8y3Eaau10MxWMzkMoJMv0kyyyPVG4qnUyTOK5I4V0OEO97I202JYrbWQigvyjdTbrCctGnOLOrsoF5sFrzVuSmtyc7RSd/QabRFNXa03GbIMOJW8pEWPXxrXqddm'
        b'5vTiQ3b0gqPVcNqZFpPWaM7SE5e3TmvREiBzDXkGi9Ch+DU7v6AxK9+URze0lK/JMWTmdPWZW40GXDmGxKDTGy2GrCJHT2EtoFNFDwbnWCwF5skREdoCQ/jK/HyjwRyu'
        b'00c4NtF/MNr5OAsPZoY2c1X3POGZ2QY12S2jAGPMmnyTrndX0gzgWCRJV5hliX7hMkmO4jP/YHN3N7bRYDFocw3Fejy23RDTaLZojZldJxrIn8OV7oRc8KbjH4ZsI+7H'
        b'mcmxrkfdXeePsbmrWE0niNCpFf69r5aBJ+AB11q02fCW9QlAQ1/Kh6AqWG3rUFNCYpTh4aiObBodDXeJn7EQgUTn9QND4OZ4uHkdzpWkIks2apIY4A/3c2hDwSjDD5+N'
        b'FZnJtgHZpSvJirWQD+7jqzLgvibGsdIifEmINk7LXggaELkmMkK3/M75+qbt18xPlSmqLpVdKxtTpdp8bVdL2aiD0+hiUA5sTO9z6JnL2K6gGz4dXRbWWZALUrwIbiKC'
        b'HJ2YJCxcO48aZbBKRhwKbnKaSOlhsFnYCOs23I22euH3VThPiEgaDvpDOy+Fz6JjwvxtE36/VrKn9HVUGzOOBxy6wRhDRwgPG6RL44VeYPSonOwKx8INOSnUyFmEzqAd'
        b'qCpeJSG7f/vAKiYeXoUNVFeJRGcRtn9whWPHc/A8OgQkxQzaOzBXmPVtg0dNsArW0tcsT0wQA6whMugaLn/NuXjhMWYXSdAuFdwB7oJ7Pegno+soiOJePKAz9rrWbQqC'
        b'u0UIWjbtAuCR6yNaWCFb50WklaxzeXup6//7fr3HIfYGT+/Luqi7AKx0LuxSkJhi51RYCyOA03mJl8mKL3swYMIGOl2bdK7/ehDU6wwbboTT5Wf+EqCk6Q6Dx7S/F4j2'
        b'OyF60M9tls05WRf+WI3lOBsjvNegM/fa2CFXY0rSmFPP62FSLzPXgHm6yoxZu+IXAeGVrl9bYDBRsdErHIddcIwgcHSUIHKpa8d3bt7J6+lGmDNAx9bAdpEbr/8fbOXe'
        b'aVskdy5LpoWeQdcyvUemoBqe7JOPTQKs0N8UjhJoxbR7Fp5i0EHUAkAJKIF1T1IFM7dkBaqKxdo+PAdPoOoobK7BKjYObVhmCGx4VWROw3lW/i14cNVL3nfkMn6N96Qc'
        b'ec0x0ZyRKyPP2ZZvuT/O59zgmtXKPZabtomNKK0gePR/ti9K+25coSrl+Qti78DxP7W9PuGvT4h3rJtT+Kdx11YWL53e/FLN69P9+gexH09QeFJLaMkozPfc+efxgU4W'
        b'SvnncVhJmdvI6auJTzZ2eZYwbYBusLBiOrpEGVjgULSJxLSEoCsdkwrYKi4V/DvnRsEGYrDdThJWFKsZ2Kp8gj5LQucB8d/khXdMObRZn6LhNqGwfryL56HGAAfbw9Zw'
        b'ubA2vx5z9WM0cn1MBDn8hY9m6PkdNyxCXCBsG0OW7qMdacpY19L9cpZWPh3dMAsbeKIGdNmxiSebjzaiMsp11w6FW+ipBDGEo4fA85ipY6l2ikNbRkk77QX4OMwXk6De'
        b'mGkqKrBQDky3jO/gwAqyxYc/dbh40uDN7nzPUdp97cjj7fzp2K+5gw0fw5djPbDhv/wSNuwA5/8DZWt2jtaYrRdiOZzqkZMvdFG9sAb1uFqXUb/mcZUt8srdF8TymMUJ'
        b'mwq0rUFlVAuI0XfRhoaiUsNTpomsmWxk0mx/v3/1MP+yyH6iv778c3LBH6eJlm8Ik09ePH5Bn/GXGpvXlr8eNnJC3u4D48OWvFLf/8vRv2v4W3Ly1Vn1T7z9/Y0zy3fb'
        b'7jIf1ErP5c67mf7O2RHvvpH82UtHTtbvLc7xes5S8aP4Pxeqdv9h/U//bguIG/yzwoO6YOXoMCoP69Bb+sLzxvVhFNv94M5YWJVEVvLCk8oQBvigGg7rhg16tPMJqh31'
        b'RY0agR7MyO5Qchz0gJldi0DMQ+AR4uZAlQzgIxh4zgwvDIL11HHjkQePCpsaxyfBmghBm5TAc0ShjESN4kkjcSUEymy0h5z5AavHOnQlJj4Wa1+E4EVoA+YzjsbRlkCH'
        b'hgWPLxcOJqjPXOjUoqahVkGJgs/CMsEJc8IHHndTofrDAwI7wVrYL6dn30yKh+lOpOkaiU3+J3tSX2gIUzykC/10Kexwi+zplYpNe13kewJfWnsg39cfQr6PaF7BtYtz'
        b'8s0Wg67dAxOHxUh0hXaxoDP0vrSJkjjvWtYkci1rEj3WsiaOTs7z789iuvgDyN9MnY7YUoQs3RQQwRZ1if9eaVt4GYGyY/B97Bwnh8jQGld1p28XS3C8u1AyWfiJC4fE'
        b'W43YklXFzukhiMktIMpZktjtpFinAChFT/Ca9BaryWieLNcsMln1GhLHJOzqoFPKNfO0uWYhTZuLE3VFWB8iapnR8qtYFKc2LD4+i6NrKe7nvP6Z5uk7v7977+6bd8/X'
        b'X9vZVNZUNqmqbU9b+smdbVvGVLVsaaobtn9DxbDNG0TSfXuCgjYGyYIqVbLAwLuR/uUppRn7VS/XgYQ870U56xQcJbAUaaA7C4GHYCVlI/pUWEopG521FDjYAzydRDnE'
        b'hRGz6DLboQlD4hNiYUVSf2MiqkwIh7XEWcoCBawWwTOe6NIvp1AfrU6Xrs8wZJqp9ksJ1K8zgcYT8iwe3IU6OpdzWD5iQYI2k0sLuZzsLHzdjyLh3bIVuPJS6j2NL7d6'
        b'oN7nH0K9D4fv/5Q+sQh+f35P9LmQOtQwiRoFnCSRe26E6uZK+/8fqZJisSlJcsEJZhF8ZtQ2yTIYtblynT5X3z3c8PGJdMm3B4QFT7kbxzyaSOcbH0GmlEg/Q5hIqZPj'
        b'IKovcZEp2ghvOqW9Hh2FrZRO58MdYoFOp60TBPkFdCTOQhaYDMyF28LiUA2qiYiHNUnwKDreiV6fhLUSf7gXVf1yeu0jOGkfQbJplGS7aHrh3Yo6JOqZLqRpOuuixFZ8'
        b'eaUHSrz8EEp8ZLOPOM2JsQO305web0d8pyac0QMNUoSkxGK05mVgusM46Obj7vAcZ1pNJiw2covcLPtfi543+kzizPNxQrIakgOjWuubKGKOeaT0qHFDS8PUGnAv3Kvy'
        b'+FsYMel8nTIKVnn4d1FB9SXxgmvt2ThY7aZazo3GOFmKNlqIu1I5FT2LVcsIVAOPLSDHqLihZKgY4+Q1iRzeGNflOK8ecTAz32q0uA2ouScczJD2hIPdiqqdsZgFvYoK'
        b'wQ9C8fE8vrzdAz6e6P3sqkeD8H+EjzkYH4294mNH+PZj46I8JJSoegajfHV0+LjQHlj34+FmRtUdhuJm3j+GPho3r1T1ip0UN2/4YNykK8arZ67qZB09PVLgmFVqwdNw'
        b'BdUGopuYgboZPxdgk4WipwlteEI4nxKeVHfDzonQLsa4fFP8GOjpRzr2Udi5UtjFrAtqdC3pYJAXekfIS/jyYQ8IeeghCPmoVhUDui4bl6Sn6/Iz09Pb+XSrKbfdm1zT'
        b'ndM97V6uRTwGnWkfKUQiFUxN5HIEOHzK7dICU36B3mQpapc6XbI04KNd4nB7tnu6uR6J/4NaUVQZo3KAEh994V+9d4WbH3M7vlhJx80jaMryXjzj9s9KmX7euPsY9icx'
        b'18s37++Fc8lkjJ8P+fhI6RaBXtC+xBUJgq6iK2p0KRGb09gaZkEI3CBaj8rQgW4TQ4QFzACObQk6z00LO7q193WsiXEMHt2H/IF87lqyTypxvWaSBS8mI9Hx3HQ6NTZV'
        b'Ow+m6bKrI7q4dp/Fl89Y1yp/nqH7uKHLiaipY50/OQBW8EFaVQsYYZedOE8JrEPX4BUrWY4wNmrNYwdnOwOzp6/qCM2+HN+NIXo52QgJD3YsdwCdD+7t2Mf5f3IUOmms'
        b'u/dYplZwNC5ntMgLhAAQEsrJc+9l/sNK41w3eIsBtqzkYF6uMqxwxZPeIJfohR+NnCa6H3gt++e5AxXXViWnnxzavOp66saQveoXJo5bWqM8kHRmyrHJKwa/EXo447/K'
        b'B4nrvf8+0Lvk5uLWkE2zx8d9rC6a+f4QcbDnoHdSZ6V9OP3G6P0Ln1xUMbgh9ObQZbP2KdP9jxWcG5qR/rbhomT44qMa/cS4Va94fBE7Lcx7QE6qSVQ6/O9zVnt+al5d'
        b'EDLgrbknvYK8r6//GZseV5+5xgkesCvoBNxOPdvPwm0klsXl2a5El+jbLhvOAX6qnSXn8OyaOl8ITXqmnz8YqeSxDaNZHp2jFxI92AFAGfNnFsg1trdEawDdUiEcnVqK'
        b'qhJV4eRkZud+b6guXoK2wpbosCJUMRfuEI0CcNNoD9S0Utgm4nwQhmLcVwyYoVHqRzlipDwDJEBWgLVCuSY3UJUrbE+8Mz2eDN17ZZixoSrDkZ9/AmY7TvitZfuomhve'
        b'3BjZbMVL/y4MmDhw6egpOpH1vo/ii9HqplxtfnDQn8v9wtcenRG6+F5GxpUXssfeTx7ybV8vUWhQ8Jc5i15asn3eZkvs2s3ffD16xcCSd65t4//iHzpwgNFy6d67B44/'
        b'+UnpS8w/jv3ni+BEm/blr25kjyvM37d0QHpF2YEx/6n4/r/cqdOjW19eqOCpShQ5cwXxX8Pq4a4zqNj8uXAntadXps1xj5LKyRTIyRkjBU8IgUst8IA5TBVHoqRw/4lA'
        b'9pNe6DqLriQiYZ8VtBVd8g9DlSPghlDi7yPL/CYNnN09vP7X7hvtvq+Byazt5CSniyA75JqNp3GHZOt2KevHyAkjxfemO85qWrh2nkQvuKlavxasFsYEXcyLNPBdD4Kw'
        b'Wt57/JAckKmNM0VhoWpY3aE4DEC3wEB4gIen0uDJbryopx073XiRa8fOX8KHuu3Y2fMslqeTD63WUz4E/KJz47/R/juc8qG4KRIHH3pF8bvU0eulAh/ShP7f8aGI2IVr'
        b'/+zblv+F5njuL+NDL3I/etFXGZpAzpEDmn5eGtmxuGECwYd50oPk5B95aZbf7T9LmGykT6oZuqQixzhDI0tZPMRxYJiRLr6ItA7XJBxLc6yRGA8r0XFh5g5t9O1gb7Go'
        b'1bD7b28I59JdmVqqernNG5G1PCeePr+/z6aLb70Y5lew9bXFnjf8Wdvl1gneoqvD7t4+8TYz8/Pvjvz23pSp4yceWmt+pujpRssPyi07t+xOmZ2teyNv8bet+T+unqLc'
        b'azzw98CnUgP00/KGfr3pz6u+vfZe20/MePXg3a/NVzDUcs9cFh9PN587UkBZwgpWDxtWdtIsf1lAclf61Ok76HNkZ/pcD3xJEEE/QcWhNCqjFGt6zlXR3V8BAXIRIqlH'
        b'yjk3Yyt1+3/Q+15nwpLm/fAsPCIQY2yiQIsitBUM1PCwyYA2dlszST50U9VFmEjLRcKRCDamERASbGJLWHrP6Xh8z1kY8nwOqGdWyJazJXwJOThBVA4sLDnSw2Qs9rGJ'
        b'GjmdqIkpET0FjIPIcQVFK4VjsugTcoCWaCkwYqI13rGRI5rCaQ2kdKuNM1XiXKIm4bgsMT12JBi3Iy6RlDM2CTlaQSepwflt4qmgcJtxHS0rwmU/x2VfIId8YOhFGEoR'
        b'PcqBlJV2KyvFZV8zzqJlhYOpwruVHNRbyXqmUFouFnLjFMyrcW0hwlESjkOn1Dag8wjCvMYmTK57qjG31usL5pnIuqpFD0RWS5ZqookYTBhfnyfjTR6YIshlLKCL6bMJ'
        b'HnrojdY8vYkcNUIU7HYxOSxAp2+XLTYayA1VX4WyswR069jTs6NaengDXQ1GFuOayO4j7czKX7rxl4yc7WMeKyxdDuYcdjU53kDmOHVEOOeGnFjj6TjlJsDtTub4ltKT'
        b'bKQCsiagMh+4IzceY2msKjqU7qhA1h7Ih/CoDTbFdQu6cG1wTtQCGzBLdUwKIOeU0e5nXQd/0G40TXa+Atnu2NyLpelNXyzdkp+em2/MnsI5z8PliA0jxIgdhk1eAozY'
        b'lkUVwg6SRAkDo1HjBLhZVIRuodJuB0u54tTGUWB1zCrGJCOmiI6zkSPBGB3fCMhBUxh0UQBoYmzMAEBEHkmhLyJ2vAgNE2FHraVr3+6zwhuJirMMubkKtp0xtjM5vb0d'
        b'eSnycvQtZ3GO/QXJuPH0ZCErCcqGjVh/PUMsd/xW5Bh6/I5J9IXFYDSsGzNEVBQ+9RHrp5ke108//lmYPa6fdjXhtnq1YwHgDlkhsK2GDCjQjP5DYLiQeC/hecCP6cdh'
        b'5dfD3xoqJC59SgyUgwKp8ns+ZD4w1M/NENGTaL44EfuZZgXdZutSWUvZpT1/2DzsTyd3Nm1pKmuqbos5VWZlMr1ne34467j6T7M2BG8RJXgFVYrkhwcrB78yXvZqtSLB'
        b'f4b/YTbkBenYUW/nb14qC7lcOmmzflgmXWs9dW7Q9qVBDjUWVYxAF8NUITGrUalzrTU8iTZQx8qkNaiZnAbpOgoyB1Wz6EDMXGFGt04fSrdiqUhAdUoGPz+Fbkez6Cyq'
        b'TRcCRKrQ2SB4Ko6YmOahqAIrsOvY4fAUvP7LF2z3ycvXTZognKSSrjNkGyxddyR2bMElpVRNqDmYMb3pqqTycZqrcjZHC8b3KOuuPGQhNtkWMx4dwtZwFapJgm3j6HbN'
        b'MYnjyXIRcrSyo6cmwhPidegIvNk7LyH6s8BBiNBrEs7JYdXtIq0502DACvKLwCmcR3TuKUmOfm2uIatoMQGfBog47MJdK1NpBAHdMwnthGXwFA+80GYWXRd336jdBQkp'
        b'S84QouKwHzl5i8BT4oDOAZfpj4Cq7XOdUD1sCzUPq9EBY1oHZyOqCj2TG24Vo5thqMYBK6yHFRheAivZu+4Aaoj/xb1GoTP9qbce88iIHiecFqd16zOiakb0nR8/NioW'
        b'GxBGrHJSO893GDcFbn3Y0D1+h5nuPVZ3YfAEIZvVpbvoMrk2eBT3CYYyNjEEbnIE1qKz3Bh4Iq9bhJ7r+EOyBFjHYHZPlClgCrEQYcCVsVjFACWccDqaDRv/JWyh1MYW'
        b'jLUx5KQyCrxI3T4ycszYqHHjoydMnDRz1uw5c+fNj4mNi09IVCclL1iYsmjxkqdSl6YJgoGoqYICwWBdwbAa07GCbxcLMybtoswcrcncLiYbhkRFC2qBR9fXj4oWRieP'
        b'c568wgnePLL9Dx0n2DwhIX5sNA0oa0ZXHSM1gJucHdj7OMkcyKITzubKIqPyF2fbmEP9tUdUiYoWxmJNF/LCTPMUrCJAxCZOJOHJwjgc5SLhSXi4900x6THyjOsYeQzR'
        b'r98IE4BeTg0KIy32QXXr4VHnknC0Y3GixwJ0CbYuxJdLC71hLQtC0FU+L2WmYe3wVN5MsKt88sJdP32mScWySMtkYonzgkb8mgU88Q4/3rLXsafBQnQabYRbo8hZ47Wo'
        b'KkICPKJY2FQcQ4VA/wkjwsJhm7rLIk94K6i3M+AN5vx0iyFPb7Zo8wp6crGTf870kasYcQ71rGrQTLYe+fiWhxwET3ceb5o6gWxuVktVDwy4KjwWVWMOP3qt0SRav9Zn'
        b'Xrfou87OTM4RfefmysTj7PW/EQpLtAffbuPcR023hvKEh2fFoy3FWDDXomoeiINZT3RmvrA7QUoAUCZgo0qumRq6fj4QNnA8OAjWRY2FbWMjwXAgUTMjJsJ98ChspJsZ'
        b'w53oWRl+enksvMTjx3AXg+qwOXd5ErpEt03IRW2r6J4JnqgpHIRPF9GWfKODQGTgNyKg0SyfseYZQeMJTw4ByVOxHqDRzBotKQT0BPFZ6OokeAH35Uy0cwqYAk87nJR2'
        b'PIx+uvUkc+6TZI8BkvieDzarLWclZFGl17qFGH3oO6Mb/eHOeFQ1NxaeVooBP4iB56F9hrBtQNFMUJo8TYIVMv8JqVahHt3w6cCWc4EBkRrT1pXBQuLNCRIgW/syj3tH'
        b'+czYOcCQsnInayYsYfhv5XOT78Y9N0OWOPaNPcY+0Ut+t8Kvbsjzvl9FTC1/b0z51d/P/tdhXXjtrO8av/f44tDe8y/Hra278/LLXmPWGUTGu8GZZXFvXPtattHry3vQ'
        b'olfKv5078N7X925s8R8Z/tHKy3/64Pb07eO8lpxMvbOtcG6TKjFpi+g38Uc2eponXt/2Udmpv9wImLM2+18tQ69+UzX85gvpthszUuPvmq//v/a+BDyKMlu0tl7T6TQh'
        b'hIQlhCVIZ2NTWWRfQkIgIIsoIG2S6kCHTidUd1hiB2TR7mZ1RUVEVgHBFUUE0blVLuPojOM6Y8+oM44b87w619FxXvTqO+f8VZ0OSRDnzrvfvPdd8lFdf9Vf//6f/+zn'
        b'rf9w2e+YvX/frSH1srtO7A7/iXt1pu/ggsjunIbPcr699VKfK+c6MW/5m09/vcn3689+92rguvvu/cN7b4zfPe30TV+PePeTPnvjkz5Z/oHbzByi3qDu6UHsC5134fd4'
        b'i9SdTAJ3Ro3VGZhgpnbMiAs+WF3PsMg78uoKrtbuSQQgJ7d3+3wEH3pfrp0l3eWE5vLQOjU2QNvPLEO2q4/WotWHtSlh96FbfTytbmA+f+5BXcHysmsb0YhcqOXHa3c4'
        b'Lz7W3z+DO5raAMeU1wOgaeTlQ4YSUBrTHihZJJ5xSeFoEh18LwyxKkh8P14gAjOdz6JnLMyq8pFRhe5EJW6vqVeqvR4K49nKRP1HIu4Jysccl+xuBeu6oUM4uOECbFQK'
        b'CHX26tKC0sJ8suxBcPjkkOFDJG6A9mxvXlLvUB/VThAYCKpbhs+dhTzavlxf7UbtwWrDKhP/tdGMWsYhgoQRXGNAjGHQzSiSnqawpBSGTfBfgmPZlMVlQK7ukCcs7OVJ'
        b'jVkXlkdFWTS+2yiyyNyQS1SqotJeeB4W9wlQMs9UNyra0cCJcLK4/ii4cgajcMNQYHeK76mHVt7ULrQyoSidHDYoVDsk6qRxU26Vvx5oFaam1FE0aIYViXFTY0ODV1FQ'
        b'bh6XiHw2x6WQd3UIsA0sIuhr8sZtQS9qT4Uw2PEqnxxapnyK+UXZ2z7UMzTvz3h/LrF8HcltuVc0dGVFq84CkficHyQRfTGSP95+2tNAy+0fWY7R6mcx0gU9Ys6Erd1H'
        b'2yNpjw/0tkMtE6OK04uoJeHAHODAWcStw2DpMN17cZzhwJJFHGfi5QlKFUyxIEuQQwyLGG4eg+o2iziVVMJCeErB3vE95IZTUjbR9JorWgaNWTx+dZ2/uGA8oYm+wNKx'
        b'i/pdcu2gRUvgWuDG++L88YvHjyOc+xw2lrG1XuCIJkSaJW4OeiuV6mVx01KlvrEhbkKeEvz461fB1PycNmlchFrilgZUOlMCcRMMJXxgNSq9EArvQoeY8LXHyHxMNHwx'
        b'iZLhz4HC4zLoIfHkT1jdd31z+aws7XCRGgMSMqptU2OzyGhiFqIk5RZupNus3rn4mjaoSBtR5+00GYC9CxkcYvOMCFFCaBykDMDrXn4fFywOCzJg+2HOg2ZDgjIOr/Rm'
        b'ShjoAw/8n8Jdm95MhA2UJnaHaeG5FaWU25/IvZ3lDvQI88p2ehc9/52OukoVcd7eIuTm0lzA4NFq/SttglClzw8bQ/L6vXUwB96VXv8F9l3c0aB4Q2jnikN8pnVkHXpY'
        b'axcFH2aSqwzGXJqqHlC3qXdphwsGTS9yE32JfjdxiHmur7rfNEh93N+5nTnGe2+V5QNM4haKXomijHIYSfR2sdZca1lohWcYXRSfWbyWWptsMVIYfRTgGVqZWxfa5X4Y'
        b'9ALSKbJjk21hitxfT6fKTkg79KAYUsRaY5LTZBd8k9rmWRc5HZ45E08kuaucAU/S2uTqJmfCMxdZl3MLu8gDIiIQHmg/bluYLudRKkfuA6mu8kD4xgwtyJX7QjqDQnB0'
        b'I/rvknjKVJgYbyA0Cai2NkvP4DDONaBrK8+eQmVzsmTcG6Qk30wL4NwP8K+FHw30AIrfjurh+q5MzHTSZvLQ5vSgLWCwobLa++sEKSY09UpqWvH5GTukBamtKHdGSh0W'
        b'q8E24CtguZl4BLKhyqUdmczFbQ3+Sl/AA6/fTGpCt+QmJHK0q1sw6k7nmK1evdPYjgTZ+IqjQtzkwYOAtkWHRnu4aX7XSok2uZLrxk/bTU+iWgdND+542TATPMorNgyz'
        b'J/Ed1/SH1l62I34SjGV/YtoJ4POMmUwCjFIU3LCo1WFRFpYLyqUy8hqEMRiNGnbPSi6YKZvCIv4CyOdRNANPLOyrTM7IK/MYwV2fKGtFCz84zue3CMWDYcrIDTHuVEXE'
        b'yeOvbzFdn9+cF8STNtjg94XidqAslVBwlQ9OUTx1DYMu8q2PYxPnGzpjXXsA1sBB7CW3/R+KBnGqG45hUKIeQjrflN1mGSZ/U9HGL6mYPHI5xiKkkQsxCYJAseph0xiL'
        b'UlS6Yr9MwUbAGhBhCMiGkiN2IG5PLPdOpAtKN/j+L6JOOmLT2y4bLPG/0Mia1kYqGdhSCxZY6fcrmXynqFMWvPqqTZO6nt8kKKFDWEOtQkv7KCylqIT4RpQWdi0swW0C'
        b'tZE32riP5zkKB7/ULcByj5sCwbrKBmhuj0RzzSwugx4wNG7xsnZcnJF3Tyjh76JugMsR1u/im9KT+8KK73yAh7CuCImuCImuCMldweGGzgh6Z5Rsno7RpI740MtTyK0v'
        b'jgl46cVfrLl6b8j5fduepJ/XE1Z+u0lJcKCQQopCS6Mi9CTfgAlKLmIjMqHZzdAbRAhxJ4cEfSmJ+s5GtkcLP4HhB5LSBTuGIkjWuxSPB5AqX8hb5/EYp8UM7sf9YSp9'
        b'4GtJMmROhHAh2tXUvc2WbS2885lakrzoii/UPzZXgfzEvJbo8wpHIc2rqM+rZORNYElKDm/gq9ls8mggsO6kuYbRCBoNNiY84XHz4ia8L5STIulnoTEuTsFOfgnajk2i'
        b'qh8J72pstHmsmo6OUKvHU1Vf7/d4ukmtJ2hG2+pYBkLX57WZDYPsQBYFGfVGYaeEuRrEd3nEaHfDOXOQ387rGoElMDSIuukY4xoAzL5AKJ6GmLnsrfZXMh1VNNkP1TOp'
        b'snE24GfKABxvkmSfxxY2K14M0pTduqwcvPCDBP/b7hiWraTDTtCSyk10QqZlIwvbJKKJeKbtQNsCsCapeuilATQcZBGf4jbv6mp/Y9C30htPxXPNAxQm1hr8KzYyFzoY'
        b'CI7t148oU4BseQSX4VTywzFhdNGNvcvHy9ftu6hcAi96S0nwQPjBLLQ9OLBNbaABDkWCEvkVXHwcShuQ8gdsYAnrGB0kEqx/oN33ocScz+YWC82mZnPYFBZWckDV414x'
        b'ZWOMKCE4h90v5fF3jP4GYIYZQfsKR9jMnsMdVyuh2gbUlAPlWZqtULM5bIHaLGErDm3Y0p2DnCshp6XZFrYpJ8N88AiQo4+FbfBeHMMFpLANcZagGhaCqkytr4VvfWxl'
        b'S7ooHLdoi6k/4ltuW9wBewNISZ9fhumOW0L1HtlXHSJtCDof4IQJwdqqitswI26kIOGZjAKy8MTzobPHXl0fCDKTwzgvo7AECo3z1YoZixGqZeZTj5Dkc1ynh+tgyN1P'
        b'Mpg/FHLBTk5/WfgEO59Ou9ysR1OUyB9J2wNY7wS5kkC8mPaiWygpcfMl7szzFZGpN6eN3ihconM2npHaSEEzDAFxETr9aWjo1CEITeBI6YeXgby+/KgjSXHNLpoDmBTw'
        b'DNvyS1HXJrSKVkng7RK6TrNLQICLTodLckkZ5gxzuiXDbpWcktPE4kIfVM+oB4IYAHbbTG1bwYrphRUm9T71KJc9QSoZMG2emxGWI7RbxiZZaGkUQhQ/cK/TbjZzw2Tz'
        b'PGtXty61eqBSu6/cKFLb7yrguZS1gnasqbadvAihBGlEpScghA8wGR24bdJ9fNRVLvfq+IrSpwM4ZdHndGIrsCUmv3ZfmrY90Tn1bA60xK7uEbQtnokdSpjwXxADcSeo'
        b'YBeFa0S9dqB5gbqUgH7lmUe1hSZmBVkj6vSuGf2qQR6L7JBT4dcqO+W0TeiXjXWmS9wxpbGubo3e2o5R5oQYkxExcPzySZQm30ppMqYDXEViQEiyQXsqfOJoFXidXoCz'
        b'EjcXEaFs9Z6jgfMgAh9IIFO0Ac3s2fmUEhpFlLVCSjOfA/+buiX36Kc50mGzq1zBd3KG2gBXYU2ZlZhXvimzTYWJLJ2ja7o8lBCR5LjsBnY1s4MFxbAwhGcez5ykyrPO'
        b'620iU+fVj6OplHmgCh2opEaYI0B8ZUCUBgJJc2wYTLSArEBlGE5kUoNbdaxyGCpME0mjRihTLn9BOTuBnfmtCJCVOHJO4sd11J+LxoBI3D8sUVdHM2jxePzegMezJGkI'
        b'M86rkjJ0zkXAzoS4pUzDoIbBAwkPmM7QLnzn8VQm1dhuiVKOi+jhJuhhSae9IyguX6Aeht9hk+3nnyQU6XYszt74xMkwAS+TEscDHQUXmNbRkKnEmFaraDdbRYfosgHs'
        b'F4nZrR0dpd2gPnZl0I1QW30wlIDxPJejPiVpd/qGdQ4D0bWaAQNvF2vFWmmhyctUzZDPJ3mlWgugbnqKBP0IH60LrYwzBzCRwUgbcdjsjKMRT59VVeutDpFnQX2gfiID'
        b'CXkFirUTkEFALZCYErGpe/v6fhr7CGGUYr8Q8yjYeuZcNAxaZsAgZRzfHiXFJbEqaV3ldNCJC4GehA0jRo1vSg9xOhFGKOkC6JUEROmaS5mmMAEhMUySiY2CmbuGvTet'
        b'CeiaxPxeM5F/10EeSysJuI9neY1esVSSBkcrgQcITYaxyuP2MiAVVjNtWgJkuAvizomEOjaGdD3bVqL4YqBbk5TgVwlAzTsACURUMPMCQ6eTlCnnb8zJbXA6huyNaLtP'
        b'LyoALZazLLE7kzAxh0haK9oe7exg7cQsbfP0mcXaae1p1F3bMmPmiqRdOkk9bOnvrup8k/ZI2qSElpAYEVAVPWhVvKfRfQMqTUYPqDPq65c3NrSRY5r0pdM1se/0EysK'
        b'06krawC075UATCaGyUuhNQ1eZQ/e2hL8uQ5PVLOfao1KCWaYlW/qd4H2FbMPOrAHLEvsxPM2Tgm8uNHYOAAGR+FA31qibkwMNApEWgHhCm17WWGxdhJVcdVjTm1HcRG6'
        b'xl5h13bNn9BO9pTgj6CqM5ziHHE8etHm4hn9F0ZRHoydUhhFCpCLmpG0jXJ0bzJ4nS3/OZmcsaBNc3VjMFRf52vyyrl+oGZzSR6v5A7yhhSvF93H1rcuYHfnrmsp+2h0'
        b'WEEObdAo2rc0UK9AHa1s09zKgJyLVDT616iUZR8LDZabr1NBg9z5uYzubmsondSEtlVU+v31q4LkP0epxLBe6MU2UGS4k8nVUfZg2+KAzCLRpHj1zBmwhZAoj6ck1UE8'
        b'iZ8a464cpv4WydCjszKfZyT4RQOWtdp9zb2z1S3aI9oTaH33KKc95ppMMeuuHa8dV7eoO9gr7a6+YoC/Ut2a2m7XJSK7L0nadXKruMpcYyJBmW2hSDpSZjgCUUhmheNR'
        b'IrGYKFtkK5INsk22A1lgThKOWRda6KC00hJxxh36hpgJlI9SUdLOHUtiMR7kUE3KB4tM5neLzVKCcTcAaAPeh6qQ3FKeBBRITQhKNMGsGxcW9DeAeGZzQFFIyBwIi8EA'
        b'3lFayobSkR0BfWGsPyEsTEHNAhN8ZzLyEGtCMdi4tUINUnESUnG8IYYxI/e8FLcusfdG4oWwx9ZnTGIat3uIe+1B3jodHIgtuXVXOZSxO/EGGxRvjW+1B3UsyRgjLgSC'
        b'F++z9IhkGBsBbIa//zSbcNWgW3GJ3Iuj+oBLD82YEH7RfLSSOckwwsIl6YLcz6EKhszvxwEWkDPEQxo1UGHwbmJ8IVQBCA4jXpFEXJ6skBCWUE2AaE7ALbfhUF9lcI32'
        b'Smjso4ToC1habEIAEpk3wkRTCSXw3AJweyvmYW/05wSP0Jhno8CerMgKM19ZVgCxcdNclB3FxakBOS5VYJB401WV/sb2osUEosREi8jVkoWVXDKdAht8Ds7SvMRpwXek'
        b'AUueOV9CrQXSKylqO8LV9QGAKCECTMFkNRPmNhWKJD5wKxe5iKhc5P4RJNJZUkGKksiYVIhUAFyhg0sMelfETfWK7FWQyxls9IeIrKhrZT1dSPHB2bZ9ZyXDsJSCWyCn'
        b'yS7YeUFAy3vz907RLvRC0zV7Bt/U8wL9bCd9TDBQS2g94WaFFXF5swhoF+kKkSlYIa4w4siL+9h8W8OizK/kFSsqoOBTeiboNA2SNchkBUTYC/Nt9dT4UfkjQGNmsE0X'
        b'4Mheg5eFP4KCXQvvf99KYDKfv+mkDHb+vtEr6vBspVUV5ZKF66jHHcZ+ZIVJUXgvop/iPtTmhndM0rASdwTeiXBXGgJwFBYy4UTewJOGBoCtfTyhuLBXYGfIyO0MuIwn'
        b'mAdlr7KJ3cETGNNMA2QxWavg8dAaa8mcH1geqF8VaD1Uc/vlBfu1mK/PC6Io1qwU4oC5aOkxKKZU4JOJnI7PGowWWmWz25MU8VRPALWZ0O03FPARDis5VuaZO2WXLsDI'
        b'5M2Ci2/q0XZ4kz9tB5sSrLYaLlnUSesG8RbEYAR25+OaJaawpBv2IfzBL8jYMGwOSwTw80MSk23VwmGAnOv9/JwE4DcYPGalitcXibKISFzsK0l3gFpHf/qAh1uS2E9W'
        b'g8esDMGkjXGVoUdJW7NjhjACq7+20gIwUiKyfdmYtQPhetViBWwGW4cE+qJEw6kL1W2x/4vCUFopgpnw9UFDkGKVMru5+gC17iQubOkY7bYrFrdyYbVHZ2pb0fFVTndJ'
        b'PbNuSIdu2fEfxR1OICNpRIcbSAiLm2CgIPjmfPQDSQYd+SCNHORYMgmAK26dUV+9vMTn91YoSA+0QUDa6EVM5xjjlpGXwYyQIPO0+xgRLdA7kn1mIrMS1hVcTcSyNBP7'
        b'0oImeh6rjiZIFS1dMapyrlzv1SMeIDrZYskLFqOyH84V6QOYfUHMR1srbqmsCqIWQtxKCoGyT4lbUNe+vjEUN3nqKAIQBWuOWzyYA5DpJOWIuIQ5FH8HtDiuA5MpsaQc'
        b'hCGkE5Zg5pu6GIPUMeMTIZudS9JYY9qhyPFD48MmVxR3HEAihM8LuEAVmfDewAOE4rmm6WHYV0CFicroDfiNWalYAEQ2wq+1pG2ml8Yvl5SqkEUWcNThmVXWyzPyrnCy'
        b'3yFInkts3Ody+FQXu53rQsCtur7RL9OQV1ZT1IVcHKpPdt2N/46On+e2Ab0Hg0oDFTfVLYdhVpaTyG3WXKLb4yavogAQqseHjjmNAcyuvwn6vd4GHfzFLXDuUFG+Tndz'
        b'XMLa00yGNRzvhNPURYxLgUK/4Fygkm9TamIW8IvODWMKOcZPUgbKtDZhZfLG+CsDYS4kYy50Hwd4TJqoM2yZmHzBRJdNSh3eExPqfFK3MYANyTUl8cqxwU1piYayHD+G'
        b'XDG0UU7ila/tjFeODo+8AM4Gmlr5Rq6k1UkvOx+a/KT6cHnqzGmBMadJxgBDo1tZk7qOpFyPbakzBkcJJJp2vm2RxwNQF1mublNCjmwlBBsmLz2pkXq2dorN+H8Bp6Pr'
        b'NIOZBkcQh4dpd6KUlTd4FaSqE6B5qvbXAzaIA2eovkge7+rqDjjHAGhgBw9Jnjb7+buc5UFeCELFTs4NGhmaqnV4uQEvGy+Gp1sDmXiTTsVaJafd2cWBfF1LIx7cWkQ7'
        b'qD6GvppmadtXUgR2Udts4lJrRbt2fGW7Q8Ki/5LtbYJPhCrnEtCiCV4RKnculGRXhIUMEiPmiLXGTOxbGxwWXRj1SkF/UKxlg4ODeXhD4VYy3VrjTo9LJbOnlLQDggnU'
        b'A8VPIU5HGuCIAGRBYFSiMYHwC22LCrUSWmlT2iQLITNL6QeGYT3UkjJ7DVY4LHdlXrAlFRJ6GHZIGlxH5ssLvZs2VC71xh1Bb8jToNTLjdWA+jvwa89VU+fMLZtVEU/B'
        b'd+QoFwBWisejRyr3eJiaugcj1BgIXML6/0LziXVf0broM0ldFwBBKlbbMRXZGTNa1zlp6TIXWpJbVxkg76DomAbhwtbW5c1czJyPVWLPEn2YlAASQlM6NaXN64o2DULW'
        b'YIKjvDtp/nD7oef1sMDYX7WCsiQK5CveoUY7kJ8ikKxw8G9k+u903ywCSi9251DVmp4CKrDXzLRACAnllZ1RQCdl00ZhRw9AQ6W9lrDADjQZFpLEbQScPOAaygW3DuEY'
        b'j/oaTlcYI5QdteH/Sl6Y8vLmTp09MfevOARMOXK14q2xEy4fF1ZV6UskbgY0oaExRKMYN8mNdQ1BZvGLWpQkMo2bVqFGg872ZACPxpk+EWqWXbzJt3IrCm5MhjY3mXSb'
        b'USWJ8Pp0YloN4ptSaF5Yw+K2Uq9/pTfkq65UUJzILFBxYqoNrhT+Q9uahLOfWp4RUvtQWYunuUIUntS6YR5EfafRuNM9kE2A1ov4JsqHTEBAmjI4VHBFzxws3ZOlrbK5'
        b'2SZbmu2MwdCcAmsghRRhv2xGRRVHNtecGrYpzxn5wqkww1Y4ZO+Sbc2pgRxK2yF9Uk6Bt0bdVqx7RUPbtoQdYUBRs7jlnPJ7LFt2dOeyuYb3oCRn2Hkzr4yRU8POlTze'
        b'hZ2sHrjPCTvgimVbdKgCZcrOsAXLlMVmG7TCyVpBX8J7VEBndeJ7VIiRLWFTODVsB0TBVovXlFqH3GUbUClhu9KAuaC1Zjqd0yvOoenJOZyDeedwxj+JZL7zq2/mfj2+'
        b'hJgiLeLYsWNp4uKiByAKP4+RlHxunJ8Ut0yub1R8AJD4MrcQNwW8qzyr2c8adyqzHrCTkq/fF/AGGaCqq1SW+gLBeFdMVDaG6gnAeaoAfi2PW/FhTX0A0F+lvjEgM4lK'
        b'BFerVO31++PS1bPrg3FpxtSSeXHpGrqvmHr1PHcaW+GkHSBRARIZ6piCoTWAPqdgAzzLvL6ly6Bo1ho7ZvD4oTle/R4IX6jCpHihFXFzFWOz2AKNdR76gikjS3gPT72r'
        b'Q/T4RyN+pzAVU1Idn2fS7VE5Payog1RSXWRkYtWJZUnn5JHhGvpMEXoRR4+FFGWbDreb4wc0Z4OT3kWbLqmaDhkydJKt5truL5KR9SIhPpJB02UhxqHdVUgkMgtPWSsy'
        b'bzbqHkiy0WyFl81hPpOpU0qyBaFcyKTzUM1tSGpR56VaabXZWnpMqlTQXDt3eH3NKMbUJx8SwcY6BaMFthRcjCl7UXHugMEFee0QroRyG4IosiRzNkNfGMtAtyFbarD2'
        b'JnCtVmSXdUBCIdq9AUpkbL4+NMTY9OGjOrIeO4fSsRYpPy+YT/umAujsTzide4dWSTIpuMdF6GncSavcB3R8db2/XtGhOSvcIPBImNd6Wic7reKVPyRaqSG8NBlMLPQ1'
        b'RRaOKEbQYbFeLOG+O7GfCVCs3Ml3igtu53WQr5zh9WqSeAg/0WlVKzdhE5QzwpTgJrgsVinLmTGIRBpL1I3q4WBKwwqRUx9QzwraLr6vGlFvQL2+BF5ACm9iRUUFarqJ'
        b'jUjeasdTr5yrRdHbR1+ub2g+viMD4ienk8szbu8Cn/+9nAYYuBLf/e/N4YO3A3K34lfbZs7zze26yHVv3oDbtjWnSOmLGxbszN1b+tyUfqWXFpoLi96vuqL2q/+9uOG+'
        b'I/PL5n8T/sP4P4z/+vcvP/hN4WbtlXNvXJ8mv2x6v++0gesfuv2GLu+YVpb2zrpj2JCBpr2XLP/ZqTdvsN0tDPyo35C8qdct/Hj9vXNMK18a9sii+9ePfcz52R0v/2zc'
        b'Naa/vZzTMOFXosVrGzngyRu0x4RXfr7/izG/3DRqz4dnVvfZ99rJ7jV/2akt2vlCfMkb9sIehxf/rvadmT1fXbPr169WXDfxzj8Off9Qdejpf3/isyHHRr5/f9fQnGd3'
        b'lGXuci/5464++8pGH3qHP1Kx4f0Nn/hGHzh1f8/ffmX6ReDzj4RXg13G5RUH71i++JNrx8/85NPwFc4vlgx6Vuk+7zf73MF3d7xuOn2k7tr13X77yNGsBY+vM3d5YfWr'
        b's36dt2vO3Xun//ui1CtmXFW4XUlvzFjd5ZabRr686NMrJr5x6Rt/W1Zya9GIrbV3RB5avOuQ8PcNvcQvXqrRRoV8FU/ft71uhWPF9PBtv/n75fUtQ0/P+Otdcp9r/jj7'
        b'D9On17Yc5pq3v//Ym3uuuOtzdX05/90Hfxnz8vDfvyh+enrT6F9ET6w/fWLa2QMt4xYeLHhg8oz89FPd7vhi5Hdz7vrt/GdeODD7871fHnt8k/3Ohc7TWwt6X3vgo5NT'
        b'X/72lp0pxSXPu759c9G5D3P2XB7MKXmr52+vvPWhNzbf/fqR1w7dcuDFI2+v0Xa8kZrf27erd9N7tctNJx4e3TT4jZldDyz6neWadz/Ln+/43YF30ndsPDt1+U29X5h/'
        b'ZEt+v1+Mro29Pvrdt5/s8lbL8FPHUh/o8fXej3917mXlnPPdy7479fGsyYsOzNQaaz+//bXAayf/+Mbmw71PH/48e03VwgWb6u9dOTOy55kvr5l3eto3jZetCIszm98a'
        b'Pubb9+996Muxr/zAj523qHZg6MP6R+at6Tmqz2t9aq4vG/5ot2fE72e1vPzm6w+PfUarlp76/v4Xp7U0DHjk0brItXu+/WHLX8b2a9owc/wtT5VE3ju+5fCg//3VVz9z'
        b'/vXW8Vv/+G7XO/f0/u34ukUfvXLg4U/e/LVn74ED8Qea5v3HhiX93i5vvuzkowNOCS+P/8q+c8Ec33PP1029btay64VHvz/0m0fOluzZ9MDeu1se3GC7e+RW09Gdh4LH'
        b'frV27/drQ7P/7dDHa4QFX9703q67D258fPfeVeULj57Z9un1+ce+jSj3vdf/jeuferP0gRlH+lXd/uflv5t4b59P+2f0mW+J/sZ3vPep/3AvmXDniCFPXfbQByvHv7Z0'
        b'0PiXJ/X3Vv1x3cMf/mXEtLdPdlv3t5SRnz7xi+JGdyoF4RpdpD1Bss0dQDLO0G7RzpQVqZvVHRaum7Ze1B4frx4lW/XJCxZgtlkoDr9ybrG6HbN0UZ8W1dvUMxJFLB7X'
        b'U1uPvlHL1K2Dtd3qHaWFWozj0tWbRPVx9ZB2L/nECPXRHia/uxVF+VpsHRrFPyGoO9U9YfIeqp7Wjqs3G4HNj5Sz2OZGXHPtpgpqjHrK3vN8fdRj2g7SR02fTVlmYFxs'
        b'Js21lRZmatvzkVeapj4retRoXQi9ruXNTIVWkFlpSN2jF4ZJlPir25lTMSbwD4+2SyXLQsPhq2zt9tFJdZfNLC/UtrlXa3cmawqwr9aV2zntWfVMCM+9pQPhsaFjcLZ7'
        b'Z7ocudq+0AgEtBvXqtFgMcVx2qE9pq1v7FAlgVW0SttlU09qh9W7aE617dpd2l3qwfTOuMWZ85lzgTN52hF2CFyyho6AidpNgN39pPPmghf3iH9iYf+/XNz9GEbw/8TF'
        b'YHz56ytlj4cF8URUsNJMfhN+wt/HUm+nzYlK5yL7n24DdNsi8BnpcN9V4AfNFvgemSho71doFgZOysp2mrImSILAZ/GX+wV+YCPks0okih/gwmsuXXv1wWu6ia5QXpYN'
        b'71wiXjNM5987rMYT/N+vF6YyHfTeSVcoc2C9A8mCHyTIgS3O6ivwOZAzywKEAJWV47TS78BFeO1xKV7zK5TnEtK6yP+s/k4urVg/jtZ1nG6/xO1f3bk3DsTN+1YtaD2o'
        b'1BicPwDez3DObLG3K9337P1VfLA/rM/AJZGiW19S3pjgumnp41e/901z2e6R138w8p70kymv/uzG4W91m7CzuG/DY8GfHW05XD9mw3+ae63OyIm+ffOct8Lvh44tGju3'
        b'5WDptC8blk16veCXn0yadnXmaXXDr7tu3/TMI3mvWOtn/H2+7X8N/G63MuLBHa//Iv3z2ZNWfzFnwjufFH7ifnG9bdAPS67ct++5aQOvPndo2L9N+uW79c8WvZUytvLU'
        b'zdtrvrr28ND8+0fl77ru87Hf7Uu3zNo8/WDVnUtrMtfM+7M7/9V7I8/uGDf/qpbDJ995Zc49302a9mXeuMd3djtmDYZrv1nzTtqNpsAvFn449pry8PKg96WPjpdN+3zR'
        b'sc29S7+oXVz+5+NPPPbaTVOefPCy57cff+K5iuNPPL/yeOOHzznfesX/bl79gQPvpT1/740n5nyWFfnz2OcfuvfMqy9+8Mud4jPpl39QOeyDkseef16+55vGpi9rxlS8'
        b'sLh85aldn335xPfrenZ95vHf/+nkR+N2FKX9/ZUvb75+57QxrpMf/OnDTc2Lfpc53vvFoVffef2ONe8uy79t6fF7t3jzfhNb+pKp4NslI56Z8dDqgqc+9inatU9t8WXM'
        b'qf/8eyVn3K0fHP33xjNfZb7XEuh/mbrghXeX7bnrpZbLvu7zvr/X0V3H3399wgdHX92/KsybUi0PfTc5Jyy7crf0+nLQ3uiw/CP7bxrdY9n+Gy8f/en+yDhzVtWmIn/1'
        b'1t6fVW0Y+9mfuMhIdWhFw+bhM1Zszy5uiBUs/pO5b+CLL5aVHvjks9c9fy+4+8uXLvl64kfPfCfeavrNg1+3uMdS/GY4P8+qD+lraqu2pZAWlXYqk3POEYeq+7WbCa1R'
        b'H54jJFCfS7VjbXCfOdqTzAvQ8TKztqVK0TYnBRMVtXvIvdCl6lF1Z4H6UKH62EQzJ2jr+eu0W9SnQmg0c7X2VPeC8iJAijblo9MqbQcFCtxarm2xcH3nmtLV9dopCmO4'
        b'Vn1YPYuu1VO0U4Z39WTf6nD838d8qz+eq95SDhm1rW7MV2A2jeXSRojL1Vu6UnvC6t6x2pa12qbBpdo2aGspr56YqJ5kOMEznlC5tn2Q9nhfgRMC/Dj1dkCPqItb1Z3a'
        b'bQXTta2L1c3ls0yceYLgVLc46KV6ak4doXXLtHsGFfGcebUwVH1W20I434Is7elyfKvu9bnLAAmxqs8KakQ7NDiEDDF15xr1XkAcC1MmA1Ud5sdP1x5gwU0OqE+pZwGz'
        b'21yobVBvhJfqCX5ek/Ys9cJ9zdLywgqbdlurry91t7qPipyi3azdTl4Uy2CQhWa+xHY1uakept6m3aNtmVWs3qnt4aHAzfy0acNDaBGlbVTvV++B2qKAz+WXajspvOsM'
        b'Qs3y1C1XXGqaskDbQKGstDu0WL8UwGDLi+yDtM0wMUckrse8UvWspO4qrGB5dl+rPUle1GBU0H9aeYWJ675M0jbVDtN2T6PBHpGuHde2DJ7eMBGbchdfot2jPkYdGKSd'
        b'VG8r0KKDZygYifIIv6B6IpufG9bBQANWpz3pFzlhHT9BPVDCgnVHtCcXlRN41E6rG2Ge3GYuRV0vaIfWWliO01MuV7fMmlVUVqABnj2dXNKlXyFCn2+vI2dXDRWDy1lI'
        b'3lkV+L2o3cc514pTJqsHQsjsWZmmHYQGmzl+LjdqjnZAO+KlVjVOHlOgPuLXvdxRlN2CKbQwXIOv07asA3LgKHMwIlXx6jN91bP02XDt1JXlRW7tcOl0+Mw8V8jU9ghs'
        b'DW++TtvH1vCowWW4ZlLUuwTtCEzSCdqVo7VDsEO3MHx6sHan7iczXd0oajc41ftZKccnNJaXFZYVsYZpD1ZyTm2zWKE+DSsT+6M9IS4unzGzDIP0ShKv3ucxUek482PZ'
        b'JptZpm5G6wh3GZSu3Saqp0eou5gT2HtWNxeUqQ8Ocg+eXshpR7VjXJp2QFRvMKtPUveu1A6qR8pHXF9QWga7rAev7luubqeVbV2CjlLV26bjngfyRrqSV89om2Ddo8gw'
        b'o1R9omC6iePLueBK7a5ydSvzRLbdp8ZgUcOSqvWRJ1MYlbCg7Z46lNb2Km1/vrZlsYtFGZVcvLrrGu0E2567A6Hy6YXqwbKKy4bznEW7VTDDWj/FRumea6bqrj5hyz7U'
        b'6uuzn3oL7V/twLV9mZdN9VTPJC+bE2T6/vKB6oZy8hSt+93Tbu/BOdW94uSpPWgrTFT3qht1n6ZV6jZ9qpj71SztURYdbnPFylbPpz2HJfs9VbcuJYJN2yyr9yMcKYKN'
        b'kQ+wcoOG/lG1WwF4zICao9CEIvUBiZupHrNo67PG0arPWaU+mYK0aAN+Wo5rKUPbLS4t0+7nc2lg+6i71xLwKtZumFs6s5iHtu0XtCfVnaOog4tXYkBm6twzPYH0wm11'
        b'QtBOqPdoz9AAXTUvr0DbPkPbUV44Y4y7CKaua44IgOnkQKLHAPzfra0vp30HvS8rnD64tm9x6UwzV8iZtLu1iLqbiN9R6v3X6sfRtlluoN3UbXjSZOZJ6t5V4iCgxHGk'
        b'pgxTj6Br6FmztP1EpaIzpBT1Mdgd6rPqIVq/C7prm2C+oU0rcYEB8J1h4bJTYY2ekK4pAYqUqOj12n7tKWiW9iiUlqJtnIXhfLpocK7tqx7AYP6jl3aBuoC2ZQeSVMSr'
        b'D9ZpexjAfByaegwbPLi8KHF4YYt7qk9qNw+Q1I1jtMOsnIfUE9rD5bCAzqi35M+0cGZJsM41YoE8pT2zkNwGu1c4oddFML7aIVgbsnrqx2RmhjflEf8CpNK/3CUhXyay'
        b'7QG4cCmCYOXP/7MLLpNE8pAsIHoABWf/BYnH3E6WR5eSMGLOzlQMBbt+ByUA2m6lsjPIvrr1z0ElYx5mdCMJrDx4LpjF1eu49n/DzTzjjDNlCFQPCXpDjQ0eT6tzQEO0'
        b'8Dyf3FO8YeTEN507OaWcbVQhUuE/+lFBRYTgc3Ct4mS+Fv5iV0WvQl212CXwK8CvAL8i/GbCrwS/86NX+Tj4tUevQgPEWB/MX4s5+QgfucrQrmvmULPOL9ZJsbQ6UzNf'
        b'Z24W6izNKEi0yDa/tc7WLNG93W+vS2k20X2K31GX2myme4ffWZfWbEExZcgFpXeD3y7w2xV+0+E3B367wi+8R4FrrG+Yi6bBb1qYfBDFUsLo4p2PuSBfBvymw283+HXC'
        b'byb85qHmN/xawlKsn2yJdZfFWJacGsuWnbGeclqsl+yK9Za7NFvl9Gab3DXWIyzKXDQbtctj/eWMmFvuFiuWM2Oz5O6xmXJWbLacHZsm94iVyT1j+XKvWKHcO1Yg58QG'
        b'yX1iJXJubJjcNzZa7hcbJ/ePjZcHxEbKebFL5YGxy+RLYmPlQbEJsjt2uZwfGyMXxEbIhbEr5KLYKLk4NlweHBsqD4mVy0Njg+Vhseny8Nhc+dJYqXxZbKp8eWyiPCJW'
        b'JI+MXSmPis2RR8cqovaNXGyAfEVsUqg73HWRx8RmyGNjk+VxsXny+NgQmY9NCVvgTW5UCFvDthocpYyIM9I90icys0aSJ8gTYf7sYXvMQcovrU5tnZG0SEYkE3JmRbIj'
        b'PSI9IznwTd/IJZHiyODIkMjEyNRISaQ0Mj1SHpkbmReZD+uhrzwpUZ416oxao+6NQswWYSHrWbkOKtkV6RJJj3TTS+8NZfeL5EUGRtyR/EhhZFhkeOTSyGWRyyMjIiMj'
        b'oyKjI1dExkTGRsZFxkcmRCZFpkDNZZEZkVlQZ7E8OVGnCeo0UZ1mqI/VhOUPjBTAF9MiZTUp8pRE7tSISCEEUiFfeqSr3prcyABoySXQkslQQ0Vkdk1XearxTXNK1BlO'
        b'oRoG0rcpUEsqjWcWjFAv+Lo/fT8Ivi+IFEWGQntLqJwrI3NqsuWSRO0itFWkkqS1dpzHZkc0L+qI5kcdYUe0bKOAah70pJCeFLInax3hFFL+mcZiE5BQkRkAIMzoXMMN'
        b'T05mqhXlGnmlRwg9kXC1vKEqrpu4tXTLCw5y5/qY6mllblWjzx/yBdyCshphEUn48Njv1I+WpyZA/DRUZNtt0q2JORI1Ky8aNi9uCcDeUm+oRkFLC6t3dTUp3pDFOwrQ'
        b'62viDkP5iJSOePSIUgdwEu7s6Ki7rkHxBoOQEv31S9EkGnXUlFeh7HPY5XOkIYLtOoeC6nOot3OOM3Su62UvQFtyTIH66nGxob4hbofSZW9NJVpCWGs8TDLLbDBbHVck'
        b'IHTcXEPlxFOq6z2VylKKEYqBTj3LV9UH/GsSj+zwKMAKizvgPhiq1F1/WiFV469cGoxb4I4Ks9FNIBgK0lvSsqcaVlYqrQnU48UUfUc3TnqqBEk9IlBP5fhhAiur2AeK'
        b'17sS/bFjArUfKGGq9nsrlbjZXwkTPDQuVvmWkm46OslhITzidow4ze6ZQtDP9UkOKZXVXowl6fFA9ioPm0gL3KE6Q1zyKN6auNMj+4KVVX6vp7qyehlTPYaFITMvbsgg'
        b'aBEGuduF80NJK9LAzGOWwIIEocoV+ptC77CoLjAFRfICGd8KG4EGXtFDd/+lGxa3d576Y/6jcHH+LaGrpuMGDrZo27QRldLMRhufhrdRC0A6B2ysbGxJmAcYJNSgXUaO'
        b'TIF5yFpDjOaSopgUlqL2Rk7ZEHU0m8JCNGW5oJTCvTkwiFKcsiTqSOGaTVGOKZZF7dF0eOOEvju641iYoxZI994ohM3RblCjEDgYFpRb4VlONLMGPevsRGUwqKcr1PMQ'
        b'5c6Cr3thaYHV8LxPtAvl+zjaBeCOhQzaspqtkNMSzYCcEpwVMNYb0WrmubAEJwhP5ZkbuZtRU9gMX9mo3J6Qy/DEY4cS9C/DNriz4x0FMYL0XI71P8pTGWvh27Roaoph'
        b'UidGXfQ2NQs9BgPhJ3PhFHwXFgDepnbnmK0XeTq1sfgFCcU7Gk8ocw/Mgz3aA2oXcFzCpgy0dMli4wDvT1KLuxsjEW7jDMPt+C9JPfr+C/CefxJ7Glc1ruJgBYFnJ8Nd'
        b'BcN6yyxYSUsoHf5cIourxPSGWFQlM2C7WbwkOgWn4OJ74XeinWIwOYU2m6WLfv7QZnlT0DeLE6barW+WjOTNAm9FnLyoBGfUkDbbByevAL6R6A4XviksBT+NmmAxmqP4'
        b'lwmTLqK+XtiibAhbyGzHGoba2OKB7dJjDBeQoz2j/aMDYRNk15jQPRQs39nN9ijqutmh1JSwPdoTNuXbsPDSUrhsPJhFuHfifdhB2w7KCacAipimL2DSAGTvwvYx3Irb'
        b'A4HogGhqtKfMR/vD/4Hwv090UA0f7YL1RPvg5soAFBOe94jyUVfUhaiZz0Kb24SLGDZTl7AVepMKCx5+w7A1os4srtkZTQeEAJ84u3OwbVIJUUiBrwopvthqKgHuyQbV'
        b'jHpTzabAZ/DUHM2HctPCadEsygNAAVqcFs2lVK6eGkCpAXoqj1J5eiqHUjl6qofRVkr1pFRPPdWfUv311EBKDdRTvSjVS0/1o1Q/PdWbUr31VF9K9dVTfRJjh6lsSmVj'
        b'qiYNDogiRPHD3HYEnQgIoK/RS6Kp0GNX2HWzEHwgLNHVgldaL91xvUAZMP416HRc7013Do0KYUy74jqDUkXyEiHh6CMAp+cFYQmfhyXDTWOrQ/Eu/1f2rrv4XwB+/PfD'
        b'qFEIoza3wijUWBSsujtts+gkaJUukQUz/n0rWfEtOmzNQCtMsxEfGh1xO/4uOdDGGT2BOYRM0Q7Qy8l3+vcXKd0huvh00Ypi1O8lk0NEer8NfDNMwQi+MceYAMGAeI5a'
        b'dfhmjnJJ8E2MmuhQB7QlagO0H+Aa0w5vcxh1iKv8E+Id0JAeNhtuAtiQijgg7TplNTr1NHZKgk2CGIgAYDmddWQjKX4CNmCCTrrQEyg9l8KUE7qYGjXjCQ1DkQaAKhXB'
        b'NqZQ7T1q3zGEx1JToum4CXGwCIiJJgCyUdsIQATHtFd435ys8A5AEMApAHxRv3dBKaS8jVGOqDzuIga163/vej5pNng4tJLRLEqy2PleIpoDFYu4wuxtV5g9eTJWIroJ'
        b'qGE0DVHhxGRI+mQMosnoBgiaGCykN5jOxDT5458Cq86BZsL0zr5jAA0dGtFbssgaAVMdDPzKNgMPKF/Uko0mshKcNw1hMbjHQMR5rFECtBJPZ5PyZ4x1iXAWzjUTnD8w'
        b'2c2WJjuyJMjgL13iQtya3xtlY6RO+iILv19xhAh0Z8QFxHlGpHuNRY+xY02qw4pQ/2bseSo+M75mZyJgGrYaYTlrpQmvidJtyA6hL6vgS3gGb2yJLxNtAOT18tbA4x2Z'
        b'9SR8+yYiRCKlAt2FIafgE+hqAsMCoc/L+kLEWnVvAYZvLbcYF0JVShzpyz/xP9n1R9zpC3rqq2o8qxRU3FYES8LeRtJ9QtLKc/NEwv9DcUey/5WOhLdxC01J2kIuuDro'
        b'cECV9oEA+s3oakjAI8Iu2ilKCyCvNoeYZcGn6RanzuZN591ZjCvRjKVTqA4xuCao/ByfvYSXX+DlZaZXjc5+gsorZETQ5PdVKb+k27rK0DLlV2SrDTfeSgwEobxKhjE+'
        b'WRlAhQLFHhcrq4DWX1YZRIvuuEV3YBW3BI2bpf76qkp/0J36zxky94J/AT79/1z+EcEGrsltyIyI4zoXBOl8oYbTlEXCBxQ0tBd6WHU3HO3/HB0+/cf/zPr/RNrsENMt'
        b'kjjjMtx7NbV4zXVI4pBeeDdmMu5LwWomwlIQqJ8VaHRzkqMIEJ5krp/Ho+/IusoG2JYhRdnCM1Nf8lzApCgv0r6burra24DunBRUfkGZSnVlY9Dr8cQzPJ5gYwNxC5G1'
        b'hkYt8DTF05pQvmjrhiLJJnZMXb3c6Peikzrmk1QCwOISAGXqSLKzjkvVn/fD+MTOhArh/wGwRFmi'
    ))))

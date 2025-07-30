
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
DATEV module of the Python Fintech package.

This module defines functions and classes
to create DATEV data exchange files.
"""

__all__ = ['DatevCSV', 'DatevKNE']

class DatevCSV:
    """DatevCSV format class"""

    def __init__(self, adviser_id, client_id, account_length=4, currency='EUR', initials=None, version=510, first_month=1):
        """
        Initializes the DatevCSV instance.

        :param adviser_id: DATEV number of the accountant
            (Beraternummer). A numeric value up to 7 digits.
        :param client_id: DATEV number of the client
            (Mandantennummer). A numeric value up to 5 digits.
        :param account_length: Length of G/L account numbers
            (Sachkonten). Therefore subledger account numbers
            (Personenkonten) are one digit longer. It must be
            a value between 4 (default) and 8.
        :param currency: Currency code (Währungskennzeichen)
        :param initials: Initials of the creator (Namenskürzel)
        :param version: Version of DATEV format (eg. 510, 710)
        :param first_month: First month of financial year (*new in v6.4.1*).
        """
        ...

    @property
    def adviser_id(self):
        """DATEV adviser number (read-only)"""
        ...

    @property
    def client_id(self):
        """DATEV client number (read-only)"""
        ...

    @property
    def account_length(self):
        """Length of G/L account numbers (read-only)"""
        ...

    @property
    def currency(self):
        """Base currency (read-only)"""
        ...

    @property
    def initials(self):
        """Initials of the creator (read-only)"""
        ...

    @property
    def version(self):
        """Version of DATEV format (read-only)"""
        ...

    @property
    def first_month(self):
        """First month of financial year (read-only)"""
        ...

    def add_entity(self, account, name, street=None, postcode=None, city=None, country=None, vat_id=None, customer_id=None, tag=None, other=None):
        """
        Adds a new debtor or creditor entity.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param account: Account number [Konto]
        :param name: Name [Name (Adressatentyp keine Angabe)]
        :param street: Street [Straße]
        :param postcode: Postal code [Postleitzahl]
        :param city: City [Ort]
        :param country: Country code, ISO-3166 [Land]
        :param vat_id: VAT-ID [EU-Land]+[EU-USt-IdNr.]
        :param customer_id: Customer ID [Kundennummer]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Stammdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D18014404834105739>`_.
        """
        ...

    def add_accounting(self, debitaccount, creditaccount, amount, date, reference=None, postingtext=None, vat_id=None, tag=None, other=None):
        """
        Adds a new accounting record.

        Each record is added to a DATEV data file, grouped by a
        combination of *tag* name and the corresponding financial
        year.

        There are a huge number of possible fields to set. Only
        the most important fields can be set directly by the
        available parameters. Additional fields must be set
        by using the parameter *other*.

        Fields that can be set directly
        (targeted DATEV field names in square brackets):

        :param debitaccount: The debit account [Konto]
        :param creditaccount: The credit account
            [Gegenkonto (ohne BU-Schlüssel)]
        :param amount: The posting amount with not more than
            two decimals.
            [Umsatz (ohne Soll/Haben-Kz)]+[Soll/Haben-Kennzeichen]
        :param date: The booking date. Must be a date object or
            an ISO8601 formatted string [Belegdatum]
        :param reference: Usually the invoice number [Belegfeld 1]
        :param postingtext: The posting text [Buchungstext]
        :param vat_id: The VAT-ID [EU-Land u. USt-IdNr.]
        :param tag: Short description of the dataset. Also used
            in the final file name. Defaults to "Bewegungsdaten".
        :param other: An optional dictionary with extra fields.
            Note that the method arguments take precedence over
            the field values in this dictionary. For possible
            field names and type declarations see
            `DATEV documentation <https://www.datev.de/dnlexom/client/app/index.html#/document/1003221/D36028803343536651>`_.
    
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...


class DatevKNE:
    """
    The DatevKNE class (Postversanddateien)

    *This format is obsolete and not longer accepted by DATEV*.
    """

    def __init__(self, adviserid, advisername, clientid, dfv='', kne=4, mediumid=1, password=''):
        """
        Initializes the DatevKNE instance.

        :param adviserid: DATEV number of the accountant (Beraternummer).
            A numeric value up to 7 digits.
        :param advisername: DATEV name of the accountant (Beratername).
            An alpha-numeric value up to 9 characters.
        :param clientid: DATEV number of the client (Mandantennummer).
            A numeric value up to 5 digits.
        :param dfv: The DFV label (DFV-Kennzeichen). Usually the initials
            of the client name (2 characters).
        :param kne: Length of G/L account numbers (Sachkonten). Therefore
            subledger account numbers (Personenkonten) are one digit longer.
            It must be a value between 4 (default) and 8.
        :param mediumid: The medium id up to 3 digits.
        :param password: The password registered at DATEV, usually unused.
        """
        ...

    @property
    def adviserid(self):
        """Datev adviser number (read-only)"""
        ...

    @property
    def advisername(self):
        """Datev adviser name (read-only)"""
        ...

    @property
    def clientid(self):
        """Datev client number (read-only)"""
        ...

    @property
    def dfv(self):
        """Datev DFV label (read-only)"""
        ...

    @property
    def kne(self):
        """Length of accounting numbers (read-only)"""
        ...

    @property
    def mediumid(self):
        """Data medium id (read-only)"""
        ...

    @property
    def password(self):
        """Datev password (read-only)"""
        ...

    def add(self, inputinfo='', accountingno=None, **data):
        """
        Adds a new accounting entry.

        Each entry is added to a DATEV data file, grouped by a combination
        of *inputinfo*, *accountingno*, year of booking date and entry type.

        :param inputinfo: Some information string about the passed entry.
            For each different value of *inputinfo* a new file is generated.
            It can be an alpha-numeric value up to 16 characters (optional).
        :param accountingno: The accounting number (Abrechnungsnummer) this
            entry is assigned to. For accounting records it can be an integer
            between 1 and 69 (default is 1), for debtor and creditor core
            data it is set to 189.

        Fields for accounting entries:

        :param debitaccount: The debit account (Sollkonto) **mandatory**
        :param creditaccount: The credit account (Gegen-/Habenkonto) **mandatory**
        :param amount: The posting amount **mandatory**
        :param date: The booking date. Must be a date object or an
            ISO8601 formatted string. **mandatory**
        :param voucherfield1: Usually the invoice number (Belegfeld1) [12]
        :param voucherfield2: The due date in form of DDMMYY or the
            payment term id, mostly unused (Belegfeld2) [12]
        :param postingtext: The posting text. Usually the debtor/creditor
            name (Buchungstext) [30]
        :param accountingkey: DATEV accounting key consisting of
            adjustment key and tax key.
    
            Adjustment keys (Berichtigungsschlüssel):
    
            - 1: Steuerschlüssel bei Buchungen mit EU-Tatbestand
            - 2: Generalumkehr
            - 3: Generalumkehr bei aufzuteilender Vorsteuer
            - 4: Aufhebung der Automatik
            - 5: Individueller Umsatzsteuerschlüssel
            - 6: Generalumkehr bei Buchungen mit EU-Tatbestand
            - 7: Generalumkehr bei individuellem Umsatzsteuerschlüssel
            - 8: Generalumkehr bei Aufhebung der Automatik
            - 9: Aufzuteilende Vorsteuer
    
            Tax keys (Steuerschlüssel):
    
            - 1: Umsatzsteuerfrei (mit Vorsteuerabzug)
            - 2: Umsatzsteuer 7%
            - 3: Umsatzsteuer 19%
            - 4: n/a
            - 5: Umsatzsteuer 16%
            - 6: n/a
            - 7: Vorsteuer 16%
            - 8: Vorsteuer 7%
            - 9: Vorsteuer 19%

        :param discount: Discount for early payment (Skonto)
        :param costcenter1: Cost center 1 (Kostenstelle 1) [8]
        :param costcenter2: Cost center 2 (Kostenstelle 2) [8]
        :param vatid: The VAT-ID (USt-ID) [15]
        :param eutaxrate: The EU tax rate (EU-Steuersatz)
        :param currency: Currency, default is EUR (Währung) [4]
        :param exchangerate: Currency exchange rate (Währungskurs)

        Fields for debtor and creditor core data:

        :param account: Account number **mandatory**
        :param name1: Name1 [20] **mandatory**
        :param name2: Name2 [20]
        :param customerid: The customer id [15]
        :param title: Title [1]

            - 1: Herrn/Frau/Frl./Firma
            - 2: Herrn
            - 3: Frau
            - 4: Frl.
            - 5: Firma
            - 6: Eheleute
            - 7: Herrn und Frau

        :param street: Street [36]
        :param postbox: Post office box [10]
        :param postcode: Postal code [10]
        :param city: City [30]
        :param country: Country code, ISO-3166 [2]
        :param phone: Phone [20]
        :param fax: Fax [20]
        :param email: Email [60]
        :param vatid: VAT-ID [15]
        :param bankname: Bank name [27]
        :param bankaccount: Bank account number [10]
        :param bankcode: Bank code [8]
        :param iban: IBAN [34]
        :param bic: BIC [11]
        """
        ...

    def as_dict(self):
        """
        Generates the DATEV files and returns them as a dictionary.

        The keys represent the file names and the values the
        corresponding file data as bytes.
        """
        ...

    def save(self, path):
        """
        Generates and saves all DATEV files.

        :param path: If *path* ends with the extension *.zip*, all files are
            stored in this archive. Otherwise the files are saved in a folder.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzsvXdcW9fZOH7v1UBsjPHAA8sbARJ7GS88MCCWAWMbDxBIAhkhYQ0P7HhiY6b3HnjFe+I9k5yTtmmbJm3a5E1I8zZpmzZO/KZ9k7RN8+34PefcKyEZiTj59I/v7/P5'
        b'WuZK9+xznuc86z7Pub9jXP5x8Dcd/qyT4aJlypkappzVslquiSnndKJlYq1oM2seoxXrJJuZOqlVtYjTSbWSzewmVuej4zazLKOVljC+TQqfb17wm5VZOrtMXm/W2o06'
        b'uVkvt9Xq5EWrbbVmkzzLYLLpqmvlDZrqOk2NTuXnV1prsDrKanV6g0lnlevtpmqbwWyyyjUmrbzaqLFadVY/m1lebdFpbDo534FWY9PIdauqazWmGp1cbzDqrCq/6hHC'
        b'lEbB30j48yfT0sKlmWlmm7lmUbO4WdIsbfZpljX7Nvs1+zcHNAc2BzUHN4c0D2gObR7YHNY8qHlw85Dmoc3hzcOahzeP0I+kSyF7YeQ2ZjPzQkSjdO3IzUwJszZiM8My'
        b'60aui1gAi0anLyqodl3TYfA3kAxATNe1hFH4Fxhl8Hu3WWRK58ivypjBaZGMfSz8RJuK1+E23FKYJ/WZi7fhjkIF7siZV6SUMhNni/FLI3CngrWTSS3Gp6OtOfm4E7fn'
        b'43aW8cM38eUcDl1Dh9FtBWcfAmVw81KVOicmBx1ERySMWMyiLrwX37eHk562WEJJnhK3VPhDGxImCLeKCph4qBsB+UEN6EXUhltjGmA87TkS6GAXakI3OHQzGx+yjyPN'
        b'b0dnp0GZbnQd7w9A21Yut+MbywOW21lmCN4uQu34yAQYLSkai+6gDagNbUcnfGPVyigybKgOCT7M8HFitLkC7atmhWUTwd9wx7JVErjxUGO+G9z0wwWYsdsAZV/gAGYs'
        b'hRlHYcau4wSY1brCjHQ+og/MIniYPZnmkzRaNJRh5JUBny4tYWiiYS5XeoAHZN7TpNF8Yuxc31VPRXJIqzQ+mDuUT7wolyzewoXARqsMeGNqImP0g8TZgeHisKDPxjPM'
        b'RxO/4G7Ht/m8xBp9SWe+B9hr8wODoXTCry0qPxFDk8OLvwjes+adcK7oQ/ZfQ78M+5jpYewxkGGrw6cAVm2xcyMjcWtsthK3ovOlkbn5eHuMKkeZm88ypmB8dZXvlNUK'
        b't7X2d0x3Or/W7vuDISut93euJdfvWtY8i/+SPmsZUGAhGfYwgoUXho8tKVaWcQzuXMSJGHx0Zp59AGQsQtvwtRJIPu3LjGXG6tbYSSP4Cm7lSoqhem1pODMbbcKn7INI'
        b'MzdQF+rAu0WwLS4wsYBubeiCPZTk7F6/FO9mGXwVdTFKRimdQSvgK6MWluTPxR0SJhyf59awI9A11j6e5LTirhqC8tFqQNGWvLmR6Hygf0w23YMqfF6CNs1LoEMsRzcy'
        b'0A0pE4JamcnM5GSJ4Ux8CmftgqyDli+XvBkfhOICtmjeN/Q0XZ9Z+MqAoeHvDV1QeWN6VMnFoIAnM/b9aEqarOoPRePijl9b+M0/fpow7O5rqStX5+85mzwyYs1Bwx9e'
        b'zq1JVe39iLtcWzvXZ+v2BFMp97dLWRcjRw4y7Y5e++GCFYM+ifzxn2+VLrp8KizjyD+Cgg+n/qtx49+/etO28Obfn2h/pdnZ1jmmYnXtytOPr36RuuiLs6mhC1SH0+cZ'
        b'fRUSG9nixUPxTjWs4QPcEY078pW5MbDNQ/FdEW5OxU02QiXEc5dF5yqBED3GO3PyCiSMP7rO4aODS2yEuKJjsIf3RKsUudG4hdIQdApvDsYbRGagRl02QH/GB99Hm/3x'
        b'BSAA52Oy7bD1W2M5ZgC+L0KX0XV0yjacUhK8pwQWvRV+tIsYK34kTmch9whuVnA9XKTCQvBU4U+/vvvlPPPN4Ml6i7lRZwImQdmPCliHbsXUnkCLzqTVWSosumqzRUvw'
        b'0kpGzUyVsaGsjPWDz2D4C4IP+Q6F7xAujLVISdsEpRWiHilfucenosJiN1VU9PhXVFQbdRqTvaGi4nsPWsFafMhvsoFod9PI4ILI4LCck7IcK6VX+xhISUZN+F50Lu5Q'
        b'5yhRayzs+c7YXBadw2eY8ei6pMIc5dyU5J9Y+LbWwkVHGD0weS1bLoI/sYEpl8C3VM+U+2gDmxk9qxVpxU2+5TL6W6KVNsnKfelvH60MfvvxfFUv0vpq/eDeH+6BhsC9'
        b'vzYA7gO0LKWyQT3SYrpSBU/+BfSnWiSMgszQz0Em4hgHn4b6PM0RbRMBzREDzRFRmiOmNEe0TizQHP2zNEfUh+aIefr9RZKEkTF3U3ymV8YcnreaMegOz+SsBaT44Uuf'
        b'Vb5e9UnlLu02zaeV7TWXdJ/A/U+qrmhq9XmasJpzOvH/lgxdNnTRxmUbog4kZI5T+8zc6V+0dVb0LdG5zp2jt4w+sDExkFlUE/y26H8UUhvh0S80qKLVSrwHvygwvGgp'
        b'E4zOiBrxSfSSjUgGVXiHOdrJD0XMKtwdECPyicD76L7IxJvxVjXejXbgtjwQBBRSRoZauVXomJ1uz6zhlFSh/ei0OgddZhhpGheOjqI9NDcVPQpFbYXj8U3g82JGgo+w'
        b'+D4+gx7SXHR1Eu6Mzsb3lNk5ZOPL8E0ONY1FxxWcCxKKnkVNsQMne2QVFQaTwVZRQXdNAFn88hCWfKSsmG0M5mGtcpTid4ukR2zVGfU9YiK69fis0FmsIOVZCHAsvjzW'
        b'C/0STLcEkkuwcxuQThY5t8HZEJdt0Ke/as4F2Z3opRLQS88JyMVRhiYC5OIocokocnHrRJ4YGuMFuSj/xfvxbbzHH3cASDqBDePtJdk82OYWAYubGcIx0/AJ6QCgcScM'
        b'CUdeF9PBdA469FnlJ1f/Bcj2mj42NFqTp3laGVJdqzdWiVvjdfErmfdeCTjyhDnyZ9mEd19WiCnsoKOtEWoBJ3LwJQEt/DJshBjg7hJ0E98Akrwdb1cpa1Bzg0B2h60T'
        b'oy2oI5jiHnrYADdthQ7kyET7CH504ws2wiIXWfF+YMKb1YVKluFWsJnoHmrigch5xAegejU6m8GmqxdQghAtpsqPDWAbQ53AcRbhmxJTEPeITZp6XV8s4CwDnFhAEQBk'
        b'J6baiQBdQa4I4KGP/xiJaXouLIiE37PTkryggAh3EUGH4oBsnGHD9ETWmkDAlfMhYIAH+D+tjOrgWhPsce/GnY4TJzacYZnLBtlSyTWFiN/BHQ3FPBKgTVFO2uCDO22j'
        b'IbfYuLYXB1LxPnccOIq7bUNJG9fRWbyZYMEIcy+RGBko8Dbvux+gbe0L7ZpnoG11h7aEByUBao9khcZo9wBzkQvMBzoBT2S5WifgD4V4BryzO8+bP4EHPJFvWb34OQmA'
        b'G+hZoUl30EsK7ASngnII/43JKcXblErV3OzceXhbYQnIjzGwX7dnz8sGcVLFMjb8yFeKN6I9lGoAj76Ib3qjGiB1OVBGhM4YniQPElsLoVbSxjc+q/wUsMaojxocpcnW'
        b'GAFfLhV9Wtmg2bb3gu6c5pPKN6pe18fuitTkai5oQqqZHw/Jbdr86sEbCyZtWJu1NWxrpbRtzBsBzOrpIVNtpSAQEn4lMaH7/q5imj8+zUtqMBGeZmwtQ9cEwpONtjpw'
        b'Dp9ax1OeLQq7E+ly8XGlO9KdB9QkeuniBHzbQXjQ+Wk8zi238gi51Q9fjyY8CTUZnGxJGedAD7FHgakXL6X2BiLa9fIko58gx4WwjYECpvBlXCkQz256kfFZzAdS1MuQ'
        b'KEYS9aXeiZF7Q10x0r0fN2XLnQpRtdZJhdht7PMrV2KPqCgqMOxfVspSmWbZ9RK1JrvmKaDJT6pq9WGac7pzP+e6w28cOBS+eGiVrurAsvC6g9O7F76e3P6z9luvJ+cl'
        b'Bzx+mvx6SsCWhI8CRrYnT18CrCecSR4S/Oq4r4H1EPjgxwsUBAFSQSXoFUgkCwSKJLe7cBR8D10kLKUpg3IUvKNsPm6LgV0CqpR0qd8kbmxePG10JNoAkg5IMg4pJpvl'
        b'wgvxEc/Q7o8sgQxutVkEkkTWmrGFsGFAlIAsBfXSCVLEQeICvwXyrAvQyTTsTqB3uJGhZ5pXcAUWolkrAomkRPgbaAZ+FRW8oQt+B1RULLdrjHwOTxNl1YAuNWbL6h6Z'
        b'IBlZqfTTI9UbdEatlQpAlAlSgkhxkI7JQV69ahTOFbKQRSkhUyCVZZyYFT5ckCxAEiAJkVEFeUmGRYqb/QVFgpEFcJWTh/bhgOQflWLcdAiuXEwkf63PEa5csofRypZJ'
        b'tb6b2c0s6BN+VF4P7JHONgGpXv1N2CxdlcFmBi0sVm3RafmfT8gMn5AhfxNaprM02musDRq7tbpWY9TJE5+QaXwTkKezNdp08iyLwWpTcFSjePJDAPtfDsLSqM0mmzmj'
        b'AJZWHpmpteisVlhYk211g3weqH8Wk662XmdSZLjcWGt0NXC1aUxaj/VMGht+aDGq5EUAGDPULTNbTM9TzlNjdTqDSSfPNNVoqnSKDLe8DLXd0lila9QZqmtNdlNNxux5'
        b'yjwyKPieV2JT5mgLLKqMTBMsli6jFLidMTazTqNVyedYNFpoSme0Eh5opP2arCvMFmi50dGHxZZRYrNocJcuo8hstek11bX0h1FnsDVqao0ZhVCCdgfrboXvRrtLdcdN'
        b'1UoyOqI4y4WBQJJKXm63QsdGl8HL473mJGSodSZTo0quNlug7QYztGZq1NB+dEJ/Ovkc/NBoM9TIV5hNfdKqDNaMUp1Rp4e8GToQH+tIu5FCksKRJ5+jA8zBp/U2K5kl'
        b'WdK+peVz8hQZs5X5GoPRNZdPUWTk8Hhic81zpCkysjSrXDPgVpFRAlsXBqlzzXCkKTJmaEx1jiWHNSK37qtGUuoIDisL7PXQACTl4dPEUlFHVo1ffkjMmZFZQPJ0Oose'
        b'CAT8LJmfk1WqnGkG2AiLT/eCwVQLuEbaEZY9W2NvsClJP0BpqlRCn8Jvt3X3lE7W3m0SCX0mkdB3EgmeJpHATyKhdxIJrpNI8DCJBG+TSHAZbIKXSSR4n0Rin0kk9p1E'
        b'oqdJJPKTSOydRKLrJBI9TCLR2yQSXQab6GUSid4nkdRnEkl9J5HkaRJJ/CSSeieR5DqJJA+TSPI2iSSXwSZ5mUSS90kk95lEct9JJHuaRDI/ieTeSSS7TiLZwySSvU0i'
        b'2WWwyV4mkew2id6NCPvJYtDpNTx9nGOx4y692VIPhFltJ6TOROcA1FgHSpDjpsECBBmon8naYNFV1zYAvTZBOtBim0VnIyUgv0qnsVTBQsHtLAMRE3RKnt1l2q2EoTSC'
        b'qJAxH5+utcC6Wa20A0L1eP5qNNQbbPJIge0qMsphuUm5Ksg01ZByWfi00WioAR5lkxtM8lIN8EWXCiUUBiSniFpUXRvrZeHKchgFEIxIUt0tQ6gPWeP7VkjwXiHBY4VE'
        b'+QyL3QbZfevR/CTvDSZ5bDDZe4VkWiFfw/NluuYglYB0QtNsulU25w+gRM6fia5Frc5iPCBm6IAd17gkjM8oN5gAGgT+tB+S1QhJhPUClXa7TXC/BfKjsdqA21kMehvB'
        b'Gr2mFsYPhUxaDQzGVAVo64S4zYJP1wAS5Zi0hhUqeRbPP1zvEtzuEt3uktzukt3uUtzuUt3u0tzu0t17j3O/dR9NvPtw4t3HE+8+oPhkD2KKPLJYWFWrIGgoegUjT5mC'
        b'rOQpyyE+ectzkjIP+YWeeyNyl6d0N1HM+xz6yfcmnX2Xwgnee3aT056nGJBKT8XcWEBKHxaQ0pcFpHhiASk8C0jppcYpriwgxQMLSPHGAlJcSH2KFxaQ4p2PpfaZRGrf'
        b'SaR6mkQqP4nU3kmkuk4i1cMkUr1NItVlsKleJpHqfRJpfSaR1ncSaZ4mkcZPIq13Emmuk0jzMIk0b5NIcxlsmpdJpHmfRHqfSaT3nUS6p0mk85NI751Euusk0j1MIt3b'
        b'JNJdBpvuZRLp3icBBLKPrhDnQVmI86gtxAnqQpyLmBLnpjDEedIY4ryqDHGuukGcN6Uhzm0+whCzLLp6rXU1UJl6oNtWs3EFSBIZJbOLMpWUW9msFp0emKCJ8DyPyQme'
        b'kxM9Jyd5Tk72nJziOTnVc3Ka5+R0L9OJIwS9zoQfNuhtOqu8sKiwRBDgCDO3NuhAH+aFyV5m7pLqYN8uSXN0Vfgh4fTPiA01fLogNTjuEtzuEjOKBNOKS+U+Rpf4vkkJ'
        b'fZNAzTESpVhjI3KpvMQOzWnqdcBGNTa7lYi1/Gzk9RqTHdiLvEbHoymwQ09mAIVLFQNh7gYtrfathT2074EpeW67b0FqYupdHTkI33JB5KVLqSf5wiLzvxNcfhOdsNdS'
        b'9Q2bUaDgLMR7wiLn7crkYY2FWM8VMstg8puYyC3ELMo/CSGGVQsxvvdIrA1Gg80y3GnwY5817hHPpRcc9klq3BNxrIzjOHE89QhbYsLddautxOGjJQadFzOyFG5dWc5/'
        b'yLBXowjs8cusrjbbTTZQJnqCZgAG8EqIpkFnfEIMi0+IU8M3w2YBRtSDmEEMpnJeCQJ8NgAVekKssD1iIgy5mfUeQvq8el7EMdeadPISs9EYmw00yqRUNxKLS+9tL9XL'
        b'mK8ul/PViGWN0FOrwWrnE0ie6z2/C+cQQyAv8fMdzZinLKmuNeKHgA1GkFJcbzNm6Iy6Gi2ZDf9TMMP0/k4QNKYMx2JQDYCIiDphszvUODkvJgnKYK/ZSlADqfBOFEAo'
        b'DNvNRhUFoQXandEABegvg0lvlivlmRabYyhCSo6J1HwmkRRL8FQsoU+xRE/FEvsUS/JULKlPsWRPxZL7FEvxVCylT7FUT8VS+xRL81QMpI7CktJ4SFDzgCHSr44mJvRJ'
        b'hBt5vg4oqMM2K7er5L22WUjkEdphLFXJiQTv0MN5I2wvGOV50XkZWXZTHXV31VlqgGQ1EjJD0mfMkyel84xX7yhCjMSe0gW84bM8NJhRThUEMnFLvYZkOlHEU44TVbxV'
        b'S+ivmudMHoX6qeY5k0epfqp5zuRRrJ9qnjN5lOunmudMHgX7qeY5k0fJfqp5ziTV0vur5jmTgjuuX3h7zqUV+0cU75gS3y+qeMmlFftFFi+5tGK/6OIll1bsF2G85NKK'
        b'/aKMl1xasV+k8ZJLK/aLNl5yacV+EcdLLt3x/WIO5JbY8MPqOmBdK4H52qioulJnsOoysoDP91I/IIcak1FDrI3WZZpaC7Rao4MSJh0Rk3rNjwLnJAQv064nhjInkXPw'
        b'UsgilLeXIcsjM02NvIhMnvABMc432IA16rQghGhsz2Q/Q4f7Vu6l5M/mWYz4tlUQE9xysunzHr0NpBKnokU5iZIKPR61AmGmAjcH1g+chgjVeipO1xMGb9MZYFlsTstx'
        b'Dsi+NoPeUKdxpf7lVDF0WpRdxQxenXR5sugqJmXpeF1DZ6giWXkANfKozMpLNt6lNVdrMYwbetYY7fV1ulqHaZsyQcIkLRNAriOybzQRVGN42VdJfqueQ/a1TCSXfiRf'
        b'4nv10KPkG07jGdClGnTBmleAO2Op9Ivb1T7MxJxBVeIAfHiqmwA80CEAL2PdBeA90j3+e/y1SXsG7hmoTdamaEM6fLSpzZLmwOaBepF2oDasCcThcrFOoh2kHdzEaIdo'
        b'h3Zw5VK4D6f3w+i9D9wPp/cj6L0M7kfS+wh67wv3o+i9nN77wf1oej+G3vvD/Vh6P47eB5AR6DnteO2EJll5IB3lwGc+vtqJHX7atGZOGK1YG6lV0NEG8bPa47eH1XNQ'
        b'0odeHbWiOny16dRZTkKjLUKgro82WhtD6wZrJ0GepFlGYzFCaZ5Sq2ryLQ+B1AEwplhtHIxpAPQxUBvf4YgtCGoO1ku0CdrEJhm0EqoNpV4BGT2yWcQre2ZJ2TexfnKX'
        b'f45kOU92+HggtxK8RkVUqSfUNZsg2RMasuHUIJ4QN5wnxDHkCcUdgntPiDfEE+Km8YS4Vih8evw02hVAsSwVBm2PbzXQDZON/AzS8GpNhREEP1ttj6zaDlvKVL26R0bc'
        b'TQ0ao+Cp4a83gKxXUQ/bubZHNHtecUG1TMAnP8bF/Wcq80w8km+ztNmv2UfvJzgDybbJNjMv+DZK18qoM5AvdQaSrfNdwGhFVNkS/2U3TMRtGci/HH48hkadlcZdORfP'
        b'QN0bqnWqPlX6JEwCnUNTL+9di0lCxBXQFWIUEkK6hEXRmGx9WiD/ImcAObA5iJFCJc8k9YFwVMup85/c3iAH8pkq1xpqDDZr33EJw3CCwfMo+GzPI3A++viWMSR/2xjc'
        b'4T9Jnke/yRDmxOY5coWBWT2PhTAbQuaBSajkpbVA+AGddXKrvcqo09bAfJ6rFd6vhNdQoSW5BpqAe378cqMZmJBFJc+xyevtoKdU6Ty2ohEmX6WzrdSRR7/ySK1Or7Eb'
        b'bQoacJfmHRYC3k+SzxR+yauJ7TDS+cTRxeao8NaKY89McmCr1QlMEt9ntsgjef+VOvzQ0ghat7eGBDepSVTFIuIINMPjiEAqInU1KnlyfFyMPDU+zmszLpt2kjyL3Mjp'
        b'DWlObzDBroExylfrNDCwKJNuJXn8uSJFlaSKj1L0Xapv8RQO4IMR9okHlMVx0xmmodJ4NKCKsROSgNvR3mG4LR9dKsLbiD9pLG4pQufGEk/S7DwFbospUKJWvD1vbja6'
        b'nF2Qn5+TzzJ4JzoeYPZBD2m7itEB0lwmjmGKKvN+NH2C0O6FIejss+3SRnEnbskDlohaaKtZs1zabVodABd8hLZ7W+1blseHtOV9VFrLUHfnoWhjhWu0VLZKGUXCUPBV'
        b'dAVdETMpi6VWdArfoiFftBm2TJowhqUxdMY6az5jnwKJpXgTvuVpeHgbtNsWQ4bYrijrnbN0OIPuWfxRdzx6bAjGRSLrKmjmQIpx5Ovv+26IC9jy0Zk7N+9v3X13k0j2'
        b'ls/l2DEFlbMTbv+oKE38uCt38LGOkH3jckOXrdqyYn3QfuXtX+RXnSh4+8KkT2R/uXDlG32ROGyxaPLTzxd/OHfKiLqPht3S1A/NR6NiD136mTlncor54rV/f/Dkrz/I'
        b'mzBtVP12haqxSxFgI5a35Kn4AGqLdYnnCB4vQvuj9fh0PvXJhrV8WI3aCvMUHG7uhSXLDMObxY34XBSNy8Jb0B58xh9WVJHv8MQdhJrFuHWpbEUWbWg56sYnoSE34LHM'
        b'4NFivFvnn4LvUj9bP3QP3YlWRmajm2OVHCNFhzgl2mSkY12BtoRBAwK4JhQTYIWiKyLcFtRgI6IYPm5JiVYpcCu6VwrSmhRd4hKHS2jvk/BpTIJDt/fCZj3ar5AyoStE'
        b'6JEV77cRaW1BzCgyVUHiIiMUAMswcXiLFO/E3Sr0YpiNhpLuxy/iR2RCbTFRKlIWd+Dt0aSs3CpBj1ID187nQ84em/FWUo5aMKHrZQol9Iv2i/AWOz5OvZCTx6B9tOc0'
        b'fNZN3BuG7opRG2oWvNv9vkdkVq/ASeQF6mVKxs+sZ9ZKWSkbwsqEK4kZk9G4MRlHcqRs4wAHJ3bGqBQ4BkI9TMk+tZAoL8t0cskklxmMIwBmJtO/m6qMr9XbSKazFm3E'
        b'QyjNEzJ84mvJbGAORrj6svYdqtOJmRX+qA8pGc9aZhkfRcsWKNge/4peocHhOit2W7ke2WSjpr5Kq5k6ANqxkjZd+nPkfSOQcaE1B8uPBPagVZpNxtUK6EykNVd/68Ca'
        b'+IH5VTjFCM/jssyBS5hjSN+M4vvnK3no/lv7reH7Da5wFx366XyIs3NFv+LFdxqGMH3fCgfn7mcAw5wDCJ+hseqczP77dehg8v10ONLZ4VivgsB36FrAQVmFIBb007O8'
        b't2evosN37zmgwkWS6Kf3sb2Q/hZpw8MY3MIIaEAb18w4A9q+UxCBo7k+QQTHZv+ZpZGwhTOKP6v8ZJC48vWqWv1T5hftP2v/bQCNSJt6UtzzwKLgKEtA24F8v0gJ86Tp'
        b'Aml2EmbcjK5RyoxupqpceAJumY3vulBmfMDUX4CZTwXZQq7hRuvhM7ExxIVY0QJePPs5L079ZXCZQABCfOqBFG5gfu0WWNanfYVfj4+wJXm/fanVZtHpbD2yBrPVRsTh'
        b'HnG1wba6x4cvs7pHukJD1Uj/ahDKzfW8eimyaWp6JGZAdku1vwAMMqogB0CyCGz9nVpioDMuP4g/AUEfJMDcf1sAwDwAYO5PYR5AYe6/LsBFV/xA4kFXzNRqraAMEIlW'
        b'q6si2w3+Vwueb3Id9dF/DnWRKjNUE9HIa+01OhcFDVbEagAFR85HMBBdy6qzqeSFgNJ92iH7vp48XjHUN5gtRK90VKvWmEBZIVVB0bHoqm3G1fKq1aRCn0Y0KzQGo4Z0'
        b'SWV74jdpVZGZGoihDDaW0KSgH5E2+7QBTdutBlMNHZGzGXkUBVbUc6xIljDbWmKt6Dv2PuUjbRpLDfShdZAgUl9OTH9WomtYl9vJ6lZZNNV1OptVMen5VXgeTyfJM914'
        b'iHwRfdi5xFs10vMkOY1dWPStEQxeW+G3xSR5Cf2WLxL86byWd2yfSXJiuARQUdVykas/nde6ZMOBUgpX+aJCi817OX5LQlH+B+0jRp5TUqhMjE9JkS8ixkqvtfl9DOpm'
        b'ZqkyZ5Z8kfAEcEn0Itf4DO+d925/okDzN3LSkKtXsNfqQDBgMWtha8B2tVZbDA02gXERPCUh1XRvZRqtZsBfndaj7g/oREoTRmOkZ+ZQYKvks3gDAN2iY0psmvp6Erxm'
        b'GuPVFEA3AyAWDKBB2FpaAz21RwPLutIADE23CiAubLi+7ZB/BWabjt8mdPPrbLVmLVCSGjto/2QsmjrYgLBpdLA61Tq5GTi7x3b4KZFNQy0bVn6aBqvLkFTyLCBqDoLk'
        b'sRXXbUfsIIDq5EyiaiNMmD+OyKrzXLNSOJHIXE1Hzj8bmVxrszVYJ8XGrly5kj9xQqXVxWpNRt0qc30sL1rGahoaYg0A/FWqWlu9cWyso4nY+Li4xISE+NhZ8Wlx8UlJ'
        b'cUlpiUnxccmpielTKyv6sTp4PgIhtMBO+DnoWftwmzVPkatUFZBYvGi0Lw6dBw1vXImktjCbHm2CjnOTE9GZdfAznonH90qp5n5NLmbgWx6iXGZ8MlTL2CeRoq02dEhN'
        b'ODo6PZkw9bl4GzlNJFdZTKLeiyNJNOh8UOPhCxg92oWu+uK9RAujxxihHagTHUZd6Ai+AcosUfl8GAk+yAX4oVP06KAqdBQdxjdUJLaWRMlC4+SwEo4ZhV70XSvG9/GD'
        b'FGriWB6Bz+EboDXnz8M7GvgJoptSfo7nY4rwtgKo2q6e1wCXwrxcvFfMgHa7yR+02bvF9FAk/+oh/ipFLnqIuvwY31x8EF/icBc+GEdzYxvQLnwjB2qzDKj16AA6waIN'
        b'eHuonUpAh/BpmT/eFqvCLdBlDDqfC+rxNpaRz/EZIBEHR9G4unwWn8I3YqNYhss2oH1sCrqJLtHVfUMtZUApCwmpMAcoFqYytMvG4fgQvrTSGoj34lt8z7LF3JzKUnrq'
        b'h2YC2kGyAgNVoE3fysPXo/EuETNk9XTQwy+h4+gKBTnahB+jq/6qaagDmoDFyyFrImIG4XviYNw9wbCp9C9i60Eo+e+ED5RvZPqhuBDJzw8mGXan/OLoW0d9ln886CGa'
        b'fuKD7IaDpgB0BO31+YvPuLYfBXT9Y+5bmTj37ael2asmnPjZH9sOpCzJOdr5k0HBin2f5x3+2Z2zAy6uPfmT2LKst0YbNMFr0l72bXz3FWbKCM3/Wb1Jsf61siTfnLWH'
        b'79nP3t4d+VVX8IHf/S76R4/sKy8qH374xtuDvkr4/GHJgnVTr0d1H5mokFLLCNqLt6BuVxMLbh1DrSz6wfgQtTpE4uPovtqj1SE6EXVlSPB2dAXfpvHO6I4dnfFXJ0Q+'
        b'a2mRjcc7BIF1LADIxdzAy7SwuFdFxEyDLvHn12xbvCK6ICVCmZOTr47BHQqWGYwfihPQ3tl8XOyNHLRdHROZDUMBCKKLeK+EW43vrnOTSYO+50kx3qNh/TRabQUvxVGh'
        b'eYJDaM4mAbEydjC9un7E9AAPGds40Cn09rYhmCsCedl5PuN4SreAXBaSSzm5kBM6LIvJZQm5LCWXCndR3HNcrz/fZm8jS5xdVDi7CHT2uNTZDxXjNVSudxXj35vgKsZ7'
        b'mpHCtydAS1z5BDGpJ5AXfh23Uk09/SbHleh6fIXHtdW6Hn8iqoCASJy5+DE4p1ntJ9BhYmIJcdDhXCLL+7lJ80EgzwcLEn0Ikej1IYI870fleX+Q5/2oPO9P5Xm/df6C'
        b'PF8L8vx2n/7leY3TD0/On0/0HFLrbBLQwJeWA+uEdQKBFMQBjet5e0RkiJHXWMz2BsgFSVnTlxWZ66sMJo1DOIkCuSWKclWeqRLt3unBSQboVHr7tESU4P+ngPz/WQFx'
        b'3V6TCKD4FKdN61sUEbf9yNfnkxwNeJTGFn2LE6fX7vj9zvcjbHEhjRdoTWZiq7FQkdXkWRBdaSYSo6FeY/Qi8i7qx40VFAnPjqxeR0woEz/eKrO5joyXpKjk+QJ2aei9'
        b'3Fy1DAAP6r3n54EmogClpcTFC8YvggigvZHmFvW6uHodhJMwTpLPs9o1RiPdGYA4K8yGauduXOTiIduvDigQVncw0GC6Ra5etN+qpZHqz2hqbr6a/xcoWjN0K3U1gqfN'
        b'/1O2/i9QthJT4hLS0uISE5MSkxNTUpLjPSpb5J93DYzII33PZpHzz32rA8TMjnkDyCmgxlerbYw9kehsFWXqnHzcGpPjEF3nOtSnWlCeXDSo9eiRbxIoMjepgoDP4guz'
        b'iOqUmOuqPC0ttacTufMI6ghUq3LzQXjt2zDfahd+7NDN2nCbLzqLj+AW+3SoXZ+zzFqYXygcTURan493kMHgbaBE+YHeAS3C/XUQxO+VLIbODqFTvgxIt/v8C/DBeXby'
        b'wG4NujbFmotB8ziIW/ML1eRgozgxM3SGCLfPR2d5nXQT3rrKGpWPOyOhs5MF6lhVDrocyTKjaiSSKbiJd+DaI5nuj++gzuLJMTLcoSwADYtjQhNF6AQ+FUAfRuNTw9A+'
        b'WIx2dBDtcz6RJgfg3iomx3fGozbJqoXoLtU8YwfF03GhE5b8wpwYBTkLNAyfEuEHuGk6BdTa2SLm6+XEMluZ90/f2Qw9grQYdy/wlzJMKWpBu+H6IrpoT4J0PerO8SfL'
        b'BIu5E9/JBv2yA+/GtyLwTqJ2tqGLkJCHO7OJ5rU4XDYHbx1Lj0DFj8rL8A34kYMeozsMrBN6YCdiox+7nGBGPNqQAjp4Zyk9z3Qt3rGQnHPKxMrlTCz0tJsO9RdLfBjt'
        b'wOHkoXqexZjF2MlzP3R6bSJZhA5BLc+OKSNHCsfmzgPgZ+P2kkgFoEC28xBhBbpNlgmdgeFITYFLkvFZO3HFM61E10vwXhW6nZgrYlh8icGXQGPfZ88gw9+Krpf7C/Ao'
        b'7sUPWZ+1kC3Ft0D12iVmUPM834Uzc+3EAwttwedQuzUQ3Vzl0HHnRuK9JTJ3nXbaIGmQcSRVtP3R+QprrrIwP5YodgU5MZKhVJ1V4AMSdBPvWGEnDoP46JTI6NxidJee'
        b'YKOQQrWXOHxjHL5LT9FNqS3gXuXu+zINmoHvL9CM0fFuEqhDHI9vCPYL3j2iXQGzgE9sYf7cSP48HFdHBOgInQ2Aed+HXUMPsGpOxbuiVfghfpwTA3q+FG3nYKQv2AdT'
        b'jdM/R02VQA5vxO0WNg1vQ/sVIhqcgzrxsVXRqunkvEZHRXRyLbUbjMVN+I5Qcy7eAhXR3imUAgw0RUTn4uv17vPE50Yav/73v//9qkjMHK8cRIhN3s2FqxjDzcu/46xT'
        b'QE3asWHFkh1TCvD0kC01K3604sio0H/tGooGnVMUN/gMC4obs0s5Wlt8wo5TNs8aMLekyCqOemNv6x/fHfSzNx6mdv33G1d2BhoXF9sCF+oHqsfM2Yp/4n/h9OP/nmTf'
        b'97rii+hFodn/vD/2n9O+iDh94E85wQls+oz8uc3nwj+9a5wosp1vyT958TfK1JZ/TJjwZsVrr+0M/OCPsk9G15491frpqJEzC9/5Ku3np66I/mfM/pO/fC3ws5iGve+s'
        b'+Sm3v+WNMZ/N2zhuyg+3rjnd1TR19eFhn52/VzY7653w7jMZV+anbJnUvCuhbsQbf23+ojXugW/B6pyG7Sv+Ybv45T7fz19JnbqqCEdJ/vLBileG/Er215AlvhNGpCwo'
        b'89XHvr9z8D9/OivWb9Lv19n8/nRo1H3119y/75QcNXePXvLCN9KlK/Gh+1+FvhR6MOdJ5xc/G5WVv/yMzk8RSJ0o0Dl0veFZjw9NqUhfhI9TawS+p8FH+lgjlqCzgkFC'
        b'AnvkHtpAXRvW4rv4MvX6QLvwFnd7RDjaT89fw1sGLlMLPhvEYyO4bN46kRG3ojv8uZAb1uBD+fhIdBRx3IhhGN+FHFCom/70lC09OoTPRauGoHbCTGIIhnVySkMlfzjX'
        b'eXwC71bnRUkZzjJsCZuKDqOT/Ilfmzj8GF3Mw7eh7RiOEatZ1L0Yt1HLRwPerAX20AFE/4DgsCFdy01E1/Ad21g6InQl0OHXEWp41rMjsAjf5U+Oa0OX0Rn6bHBNjQen'
        b'jXo9tdikmLKtZOspCfui6z0AXwzDO0TomiSFN8UcwCfQAbRB5Gpu4VYDtW7t53wsRch/yPbiyQoTROwNveo4tcSUEjFhPf1wAYIdptcaQ46r420x9I4jjiQRkBvGSqk7'
        b'CXEtCYV7ciCxjAuiziZ+HLlvHOJm5ejtVbDdBPD2kypyIeKKhZyLb9GRi55capw2FU9mG5/nObfYj2+z2tlwlbOlGmc/gc4ueg04BriUuxlwzkW5GnC8Ta1aIohdJLTQ'
        b'/TBzSbNPM0MflrLNftTs4t8sdh5mLtkm3cy8IG2UrpVQM4uUmlkk66Sejn4kjY/qI9MF8TLdpyGwL8a96EMO819qrWd4g/kLZjEjy4ONBpLeoSGR/JHntmlovxV1yJaL'
        b'mPnokiiITVs6jz9OvxvtQjdLUEcp7piXPxffKsK35gWmxMUxzMgBhUNEaOOkJXZCdSLRabSjBHeUJuMdFXG4NQnkKdlyFh9fgy5QRjJsZJijmfIUlpFEsehQMrrNm/aP'
        b'VM8mp5YzRnxpMjM5q5I/h/0I2joGn8IvZtsAPScwQ/G5cp6b3QZuq1bFJSUkD0JbOEa6jkXH8L5llMcGLdbS08H5k8FhNvRwcLQHtxs2rRnPWol/UdwXvrMLHxTMjA+4'
        b'9bvDv55zQhk6Qz6v6uOZBxaEH7i/8HLYuJCjQ58qAiL+3r5uxrQNLS0733zlyaNB3ZYj1rVP07aG+0UuqN75v9KA3Hc/WLh/7i/iaz88/lV32LnW6nnTczbdOnhM8zf5'
        b'a7bA1l/fTcj/8fKfGH5yeeffVozwH6wdiv/5qOuVbbsrj97xnV/0af2Er+6nfhE4yVS3/cvNXzb8NuXuZ6+/HTvhR+YrnV1j/9X48ObH//jqh+uNplvvbcpqWW3KOTRJ'
        b'ciLh8y+qeqzpF/4U3fa3a49/ZbP9bVfWPwf+pqzw5ReWbvv3uIo/v3wjNOLEv78W2dIKWj9fpQilPndx6LEZCNkjehK/D8Ohk+w8dHcmdalDJ+OCgZASIpqFLlA6KkLb'
        b'KeUeG4xPAg28kuqkjoSMhqDDPBU9laYYWuPNPS4QJPAzlPip14MwRdiR1nnkNG8dnxNL2cc4Pb6iLojJma3Ox9tjYQhMEHosqtCiY3TsY9F9UAfa1PQo9wKFOIJFJ/HN'
        b'KTzn2b9yoetJ1QHp+GSMyAcf8+NN6Y/RddRMjoLPKHYcBs8fBH8U7+Y9RDairZXqPHQEn1O4uj4ORpfFw/EFfIta+LPRrfVqh1fjNJAzecfG0GUidMlvKeWpaEMqPubg'
        b'qegKuvyslZ+Y+M8F8K6Uj/IXEPdU4qZ4TMp7kUqZ4AjRUui9k66ZNAafIiwV0PZuL1sFpnoyi0ImGl3C9wVmglsWOfjJHiV/IOoutE3Ze3I9ehRBT66PxEd5htyEDy10'
        b'HNTckOk4LrUzl+dVl2rRXSLU4c7CHHwYbZBA/g7OLIYlei5S+33PlndzquFPwKdcSdvLlWIJz6GOi9R9UUw4EsfBN8+hAoAg8x8x5VP8cwNyxzs7ypz5jo+UE3NB3GDO'
        b'D7iYq0sN3z3PnXx6+UKPD2+HtvZIrDaNxdYjgnLflRVJLOSEVkudk+MYnWyHcpxlcLnMCmdhUo6zgXlb7sX3hx/of8ALS0RZi/ibj/sYEPgAKpsjcEMwxBoF+4hFZ7Nb'
        b'TDSvXq4hdn4Xc8tz2cjldbrVVminwaKzEq9G3o4jGKasTuO8YNTxZNt+1m5v5K1hZDhVq206D3YnJwOVCn/POsPzxyAfR90W1Ib3oe0gql3Hu1D3fNwENKUb/i7ORdsk'
        b'zFAQ6taga6C+E2jF4euwY3cDGFVAEYgrcYuUvkJnLNqHj1MGi9rmK/E+tUolYvAFdC8MtYjQeXwMdVDm3BQlUlWJ6GtbArJz44X379zEFxhnZekYvLcKPQr2xafxyQQm'
        b'KlmSVhBG9bgXcuujVU4tDV8PiQXydoy3yBxItPHcF3eunpcvsF+0LZCaD7hF+Ix6SjqvyIEWp4Fa1Nt674hyYOloo5JU4VAHOyIVPTKMyFwpsW6B/LJFd/LbTwRtnh4y'
        b'q2bln3KXz8v/umUd2z2sZOMJ08y3rPZtS+yDIh/fG77p5Xz9Hx4Fj1C/VJx5onXif29vOXpkflhZccqF356ssjSr//Hqa3e7Xzn9o7+lVB08me8zRXx08qK3fvVKzpfv'
        b'VS+MHZn7zpni33927P3cL3885Ufdv9CMyhq6tHtp7fr1ebpxf9UVK6RUUamV4qsuz0QD0Z1eVz90YhmvNOypBHWm97BfbjxqGpuLzvGu5ffwLdwZjU7UqfI5mOw5Vo1P'
        b'TePZzKHRi/AOEzAx/mUWHOOv4/Bx3B1DmcjSocPc/AephoAejeWVhMmom9LVoNH+jpeSvAT6gJMXoYsShfRbSIYX10ONtYJstt4XhPBU0igWhVFpPAy+Cc0jz1VDgcq5'
        b'EA6hasF39Eo0w+X3z9CmY178EoUuFGyPuEFjq/V8+nkKIxw4TZ44klcgSJ0noIu9noAu0KqPRKyHp4295IpQDqtmBfllNLoSruePNSMDnyTP0cujyK8oOVBbK2/XJiRJ'
        b't4rEsRIzb5Sq0dAQFUM7EmijxbOV2EpO79M6bdMaS3WtYYVOJS8kpvSVBqvOSf9oG3QCtLhGrjcbgdb3Q8zcXijgJGayAnsUoSInx6Jj0dmwN4qycTuICBcVufl56Hxp'
        b'NjlJPUYFIkg23urTEK6ntE+JNwWAaBGTm6/CLQllIJeVgoLeFjsXRA5lJDmlRY1v+wBZ24DOUxIzBzfjjXg36NxExxdNwfeMLNqEL6ZQu6F8alY0KCKr8NlKZtUSvJ2K'
        b'/QZ1TnQhFz+LYYthj6FtSYaSw6li63VC/tpNUzqm0JcVdR0Ni1xf9QmbNjP45VclTEsCU/LqDvb8yz8fvTNkaff1eGvprtKq//O0Zn1spL860/+DCz7DQxvnZmfsXWnX'
        b'flCSl352i1Ickfn+xpeDOlqfJM5q/gV7crJd7ZMRemn5hc6n70XPuW17uifuxJTUbV8umH73c+t/jUv+9bSdZ9+72iL74FPzuTUzP1yb7t9z/Zqi6Tf+V4/e/rK2Y1Rg'
        b'QMq7v93w18Ormr/4QrRybdI/FfcUwdRisaoBP6SLDHg+JDuVBeEZ6AtRkPB+9EhPZEyQqLcLry+T4TbuhWy8gbfbXMO78vANfHOlYGRpxDt80VkOnRo2iErCegm+Txto'
        b'AVldjo5IC7gR6IYvpS5aeSN5RVuMKofmNub642scfgiCbjPfeBdqlqpjUGchf94/Oov3+U/ngBBdr+Rp4160Be7aiE0RCFwpvi5dx0VNZ2ntGaDcnSUyoUKFtuLNeDud'
        b'YHCcqGZiBR0a3vMCOu2krAXoNBDXsQun8f4x+6DGjehY8hwBSOxBpUrBAenrEqEtg1Anpb2SEnSCCtixoLMp8qWTuSG56Jbwvphjw9UEQ4fgxxRJfcM4dEKB+dxqaPo4'
        b'MfXwi4LvoBPSGdzQaRG8HHwok7y+wCEHi4PwFSIHF+HT/JQfjpDxw5IwC6AiOsfFQNmH/ZlkvoVSu1BnMdm57g4u5OPLG1VkNA4HyDIIqLyRJBRSGwOd1JPULnB7GUCD'
        b'O4nuZ5AcX7aXbFvg8u9nyPbmwW4vB3DrGBp3hi5byIMEPj4+mW+c0GxLKkMNN2nkN3mqYyF+d15r8TH1xDRvIa9ytEzhZ0CLz4JLAd8oaQ3olfBPIeG/OPgb+EwkPvG7'
        b'15qrKypozFCPrMFibtBZbKufJ16JuNZTxxxq3KHyNmVsdJn4JQ/7j1ve+kUWC3kJyO8YwSNHJhZzxNjGsGHjOEFt+dYrFyQKAIxi2MGqADaMG1E0LDVoOLWWDM5FR6zk'
        b'pYrWVZOCgkRM4EgOn0D7Y+hzi0GoLcgfKBQhSP744iDy3KWIPJYakSAeC2Lvsf/QG4tqvz3Aw6eAMoXl+AEJZLExzGhmNN6KLvEmn4egT29Uq9C1OMAnMb69FN9ml6f7'
        b'2QnxQzsk+MAk1O1i96FGnyXoNM0PTMZXcVtODBHNEsWgzt7KRm1cLii3Jw3zNAViK0HBx2/t/4zGk3yizdO8XvUUfi/T1+qfiq8fKDlQfODwwZeN+8IGX4ucuTPfp9pv'
        b'ps/M6N3jRNkTyAu2BoxlRuDg26+ZFBJKDZWBuC1aMHZL0aVR+DSXmIhOUkKNrqDdIS40CQjSDnwQXR+Bd/H53cPR42hVrzEct+OHnBI/RFsF9RzvKHKo58BBBgGQQDvH'
        b'p9B9SkqtwCOukae2fHZZ4hJOJ1/cXwRLACheIO3oKoj3AiVYg10J1jhiyyUESgxXi925RcQ9YlKhR8pHkHl6T9JKkrTCieSk7mjO0f4G4fORq/hIn7yuQK24KToyV5kd'
        b'gzbPzkUdsfyDVzneJwnDd7RueDRI+LZ+4XouRhw5GwKQk9OKmnzLRTqxVqyVNDFaqdangyuXwL2M3vvSeync+9F7f3rvA/cB9D6Q3svgPojeB9N7X7gPofcD6L0f9OYD'
        b'vYVqB5I3zWkTYGOw9LQN3/IAIW+Idig5B0ObSPOGaYdDXpA2CXKlNGpGrB2hHQlpwdpkSBNDjVFaOTmzYo/fHm6PSC/aI94jIR9tuJ6DNPItcn7zqfxVzJdwuYqf/a0d'
        b'fSQY2vLrbefZOtqUvmnf76qNPDJQqzjClQ/QheoGaKPCmWUDNzObWXoX7bijJcKoFyIfTySDNfHRxmiVsGqDqH+iD10niValjYW0wdpwqgWk9vhWAO/SZIHETO1FboZ3'
        b'dz2D93KU0vcASp3mdkm/5vbnIFx+vLm9YRrvic7MsgfcmhnBB5b/cEYHM5RlIndMN6gauLl8Ih6/lv2aYxb8PLR6+C/WrGPshJzGrlnpFrNO9Ul0F+136JRAMNp8mJIa'
        b'WQg+n07bGZs2hiGk6+chy2a87DuT+aNjjF+SiyFz/G2JlYz9WtXPRrZfD9wQFyD+TcGMSvHt469HqNUB06sVs++/LJ6Vra8zHnqw/slfcocF1/48afLO8QGNJ0KWpaUm'
        b'3nm3Lf3mz3/6g1CfD05fsxcNzm5c9ZfBPzi4riAh/MbvP716o/JHxdPOHQtfaOlR+PKmxXuVeA9qQ4/RZvLCHaWIkZVytmygfVRK3Is7J0HuVdS9mhqcpRO5AbMNlK4V'
        b'443L/FcX9Ikvl9XPo8HYaBtq8X9WzSZLMmiwDzM+XFKLt0v5cPYX8QYOtU0PJAQ2OlLJF4SVGzJCPBm/hDbwPtR3l4BATt4KtB4dyEEd1HjdTp7cHRahE+gl3Mqbarfj'
        b'4ytpsUWFtFQ+usRAob0idCpgFC9Z7xqHNqM2fJqJBfk1h7z2WIZbOdSEDkfbiAC0ClSbK6htJawHZbPQDtpeCAygpRB3qtADfEDKpKulaJ9oCk9Zn1vG7A33jnCl2AlS'
        b'1k8iY4fSsG/BXso2hjq3yTNvP+Ttmz0S6p3UIybOrT0BvQ+yTOYeX4OpwW6j52t5NhFILOR8T8saciHxGbzoudZtnLF9KP8v3SRQD+P71gBXPR/gKqkgg+4nsjWTc8R0'
        b'u/TiDOoe0Xs6aJ/4VhW0mkOoynPG2gZWuK5cP0Oa5RjSNxEu3feN6FY9fyi5E0r9dDvH2e3IHEdxh0/l9+nVt4KgTUW9ob+w5lxnp4OJmiHXW8z13603vXtvmlX99Jbv'
        b'7C2M9ka8bb9HX9IKm9mmMfbTUZGzo/BSUtThk+uxt+9vmffIhTim7/v+KE+oGCAiovp0A1Np3AWkjibujaBhPNkfySvz8scNYwwXY99mrQrIebNqN5F6szV79v1SG/kH'
        b'tSZA/0nlJ8wXh8NLDrwavik87Zds5W3Jp8tgwW3EiiRKKgBShk/jB57JmUDK0lBrPyIn1cAo3aJvLHPQrTIiYzYOcKUD3zdyuqQPsbnqZqX00AnRPf9Dys5zvJhTgFb4'
        b'AHFtECsn4zS+q86uogviJ/5nNZNcRrCTbfcx7DctkFjJM8bU/EH864B3aF+rytPkaZbpP2W+rB9aPNT8CYWUNl2qCmlScJTtjBuIW3iuMx+1eocU6gLFgvdNGwIVLhET'
        b'E26JUqqI8rGJSyzGR/tTHoIrqCexoVFXUWU0V9f1vuLOAdXFjeEui+1e2u11qxLqAutJj2hn3KwZbXBZ0AfAF9wA7L1P5450wJhIJo7Xr4oAyqLnhLL+2Xdw9n2OJDhi'
        b'1Ib8jX3qr/BhiipH/TNYwlCLqG7EGHQRSuJd2Y1M49xK6km5EnXGo4swt3R8fw2zBl8spe9/z0E38UMCwnp809WFtDSyQMkySahFGpRdTrtiloIQuiCFuNbF+OvrGOpX'
        b'GDmqkHtVyqy6llMf8LHqrjSf4b0kb08g3rX8+UZu7oUERQBZrgCauHoVohP4oB8+lII6LY1Qn+rWIehmqFO3nocuEfWa6NaP8X3q6zdXAlpoyGk6oE6DgqGJP82DRNtD'
        b'H0gMKKqazBhmHJCKrZ3Q3H+fGDy+40QoiguZ9bddSUXTPzzwL0mn5X/9xq3fMP0jU5TqgkGCxfigbNyovBkfvPF0zYPt5h9K/vamv+8v1311MHTPgU2HO325lNyMV6du'
        b'rL92vavl6FuHE3Rjt6YuOTHkjxuW/aCm/iebgicE3fj47a6U34Y1fZqN614c/+XtzPnHfmC9aNv0g/BTL21cPjvjH8wx05g3X3lZ4cPr5AfLCqn1E12fqXIxfqJ9EioC'
        b'2gfa/dVoM77QR3jlhtO9GIpPlXmVAGfju8JeBN3+Jd7x7DC+PBrfWeQfJUi6zlZHoRtifFVroMS4QYPosUPkHZUEKdAlUJYd7UqZuEx8EF2QjihEO6m9sxA/SBd8BirR'
        b'QcFnALesopK7H76FbzrsCkn4kPDUfyzb+wpcr6ZOacVKi0F4vambJFpBKDrHykESHSb4kQWwjSEue5NWdH/rssZSY/VC5jlLpzsp6IDL4j6k4IzbKzD7dFdQLRZ2rZTp'
        b'+yJeGgjnfBGvmD6GkgAREFMiIKFEQLxO4okIOKiKOxGQFtCtPRDvb0C70eMFIuKyNQpvVVB1lfpGlaMWtCd6rnJQWZmSuHr4DOAi8JVMQ8XRVpE1Hgo8OqLj2fTTys8r'
        b'a/Wfaz8ftqZSNVit8dNnaz6v/LSyoDq0Wqb/MM+HOfGxTPZpBLBrgkh16MEI1BaLXgwnJhQEeEG9PlhmeK0YNKqHeL9j7fs3ZksraFwEhXCIK4SNQdTXwm2RaVGHKtPr'
        b'U0ffm0xNQn1IvJhPf6YshfB2uBj6QPhgqDcI0849A5hw+GYJgFhKrQkEzD7PCebn4ui98ByBL8Sho1ElSgDnPpYR4QdsPtorMxQPzWWtxBrNFed+VqnWvPaHyN/m8CJX'
        b'5WeVBn3Uvs8qn1TW6Z9qP6vkWuNSEu3dL8bZr6249mJ8S83v48WJDXqGsZUE/L21o1cgfS6vE7eXZBO7nQtAw1wBapHxbjXEbXOQy7r21nk+yHoOpu0H0DvgYu4D6N1D'
        b'XQHteUBPiIeQZ5An8XtaIuxqyffd1RKv4CaENXgi3g+wxnsTs0WMxIddtQ5tws2oy7D99HXWSuIlhmUP+KwyxwHv90tg135aqdJ8UvkUoP60MkRTq89z7uBzjM/f/5wI'
        b'O5iQjfn4hpQ6QFdM4ZawqbFo6/O/VrcnqEI4VtQF2m4idyOBduNQl2V1q+AZ1D1SvabaZrZ4IdJiy25vMN4Fl5V9YNwW5gpjr4NRBPOeu72OvMSHtyewV+Gu063uCVxh'
        b'tlfX6iy0Srz7bUKPfzU5zEVH3pIa73qT0CPTGqz8KSzEH5i8CN5GDtvV2W2aVfS8WPIkqSdAt6q6VkNOMyVJ/T73UgykgeM9EuLGFN/j5zhlxaB1iUpfQEvYDDajrkdG'
        b'3qVBCvf4k1+OaG+aTI9voi0lWA6ROj4kALHKvIqGpPdIGmrNJl2PSK9Z1SPR1WsMxh6xAer1iKoM1Qquxydz5szCeQWlPeKZhcWzLRdI1xcZF6uGQxYm0o6VzEg4/1dK'
        b'XZXZZple9n10H4IPQ/tsnWpeKs4Z90JsrejPEiZOk3FHF8TwsShtPpOt+HYw4AuHz7CNeGPUUNRFY6NGob3oitW2AnLRHtyEb/mzjA8+xAWhjXgfPfYDX4CMl6KJv+Tl'
        b'yOx8VU7+XLytAF2Owdtjc+dmx6BNo3JjQc4FoUoIK2Lw7kUBM4fFUzcofHfpALx7LlOGX2SYRiafRO3QEJhd+DLeGQryLXFqZicywMav4ft8oNRFfA+fSwScTmTi8aVE'
        b'EL46ed+p2wPQi7gbHYBKHMNGMmhPJX5g5x9p30wXXEUfToGxsIx/OYevrK+io1igT8MXG6GWlGEV5HCJ+6sokanJwufS8U3eEzaZvMr8Oot3vzCWruUgnyjmCHsOxPHK'
        b'GUlGER8VVjNkALqF7kBToEhGMWif3Eqj39BJDdqsVinR0TEqEmWXr8SteSwzBJ0WT6/Ad2iDScvl2gJ2AzkHdq3IIBWAcxlAcAjvCoMmRQwbw6ADAfgRH9nUOX1FNDln'
        b'JId/8BSMOkTDSqsm4y20uW9sQ1aMYBeQULDJ14IKeKfzVegIOhY2FxrzYVglSNlKfJr3VrvjiztBEKUvAxLHsD6oE93HTegKbWtpxLSGvzNfM0xcZXHR8IE8CQYYXUXX'
        b'/fGtxCR0DdQxFTn65BS6yg/uPt5Kn8iJ8PbcfNCYfOM5dADfxXtpg+2FucAcIllYPL9frJ/M8LFNsPIdEbGkOYB5LIMOr8S7aVcZ69DlF7J5NzOYqRRt5caiW/g4bSs3'
        b'RDLhpiiEhjYVzY8W1u2GDgpcm5eYBIoZWba96DA6y8PiWA66oiaHsrSRKROvsCDUBOMsnQoyYRd/xI05bfoy5kNyxm2CNSKLH18OuoduD14MTXJ0tvvxBnyZPtJdDjC9'
        b'TpqciPfgtgKHwZxlhqE9YtSqXEPrY6L5XzckQQNSOr8DDLpHV78oF3CMjqiAh2VQg6jSltbYSAdTnDmw0sZkw6/KxZx4GT+YGNS5EJ/DmxITCNbCBPeNQd10seri1pSj'
        b'bgFpOUDabhZG1T6AIkCVBCZxyZaYDNo3m0AcRS7zOw5vRKfxZtxVH60m55uwjNTAhYdl8VEB29dZcfu6xFRSKQ3GDaCkEQj4ygC8hcdBtBWfxa3oKsMETBaFTEIP+L3a'
        b'he+OTLFDTViySYAg6OYMOuO5eNMENb9KdQMVxAM9IEQ0iBG2gpr1rV3JysnyB2we2MiDFL+EWmSoIzgxFQg+aewgPoAP0NaGjsb75uIuGAkJO1QDhlRzw4EWnOUHcR5f'
        b'GLYCn4KKgFcZMIqxRTQjFm83wQjvq9XkEQNnZqfXGvkaD6cHT8BdUAGGPRkQMRMf4nH+JrqNr6ZEqQlJaycPHqQDOV/9CjrqNxvXaF9mPyFIXbZQJeJHHYp2rMHN+Dy6'
        b'EZckYdgZDOoahU7QxgAfruGXQD3IJY9BRPgxO68QHS6cQhvrMmepwrihLGzf3EeR83mgo6MTcHMhLAQ0BtRgJoOO58yhIw5Cd3G7n0UNZEXKcEvZWHR7LW1nhmao5W2u'
        b'kizliCzdUmEpb04eo84hTjhiMWsFjbYL78Yt1EaiLkwWvGl9ilWD8WEaUBthRudpwEJxNii6yjLeLc0mxdvyY4D6MMycUJ/hqKuKbv2huWg3DTdd78NvAhkGhNmLT6/v'
        b'Pfz57UlcwyyGOt0ap0YmMVRdyy4B0r4bhMkYZubgGFDtt9uJH08yuoL3qfPwNXzG/UEUsBkxMx5dkNjR5ZG8EoBa0ZmKJbhtbnIcbgVCFsoumYOP83M+Ow8fnJCuLsUd'
        b'gAX4IAPUAeYsJ9s3D7WrVSPwTfcAaZYZXygxrARcp/V3zYH9dtifxDgw89Ep9BhG2Ea3P35cHxKN21BnbGw+7sxW5vIqX7yYmVAqSZiOXqRzzhw/vGoaV0sYxmJ1VgUP'
        b'UUDhjZPwYR9o9SUmfjB6CZ1BB+mhTqsgaze0ircGu7fKMRPmSRLxhkp+WEdhIDdicLd6LvBWGpT7iMnnt3Q7voUOlgBH7gDWvobNx4dHLEIdPIM95oc243OD1PP45XgR'
        b'cGIwbuXPidotF7kEoZfhLn41RqE2Mb4tD+cbb4GeYT0CiaMIg88B6XyIjysphc2dQWJUO2PRKXxFlVMAlXOUCWJmODokNqJjQ/gt1kaCdA+DuIIeMXON6BHeO5T2vgYo'
        b'yW5aexN67KzNQe3D4voF6BAfvXRvfggmRkkDg04PMEzkKDlaiTsWEQdKJ/yCB4pwU+EytA2/SDFMhVrtaDe1BqDu4FFo9ygKv2nodgWhYvNRl4riluD9MALdEoN0cXM1'
        b'HfH8YbPxYdgZ6AGjhPk+wFvQbsr0x6MDqBO3AXLXAQFj6tDRyXQjpOJ2vVqpzEGXInNjcuzZEmbgdBHeMxbf5VnUVXyvCB8OIFSFuK5vBeLSEUvlLrwDncEX3QM8Rfg0'
        b'PmNcCQINwZuZLHoYgPZbAwOBQsEOxJdT0XEjef4eXuNfsF4USdAs72Q1v9b38Y4FuA3mbWYy8FUzvgzrwJ9DDvLAcRDdsklAeru6ULkWXckldEE+XIyvjfShtkzfmnHs'
        b'z6GyfKVpxJ01sXHf8LIOcP9WM7WnNjJz0KlGdGKtYeBvp3LWv4OIe+HyviVvvWf6ZVGI9MP0H6kPpyz/ddGMJe/MeO9vt6arjxcdf6p+705DfOhr+4q0lie/bmj6ffTv'
        b'/V/d/Oe0ycybr/zpx+d1yweM/3K1PuGY1TJtQllLgeidzTuODgic9/kPenbMvTcqI3x20pyxe8/fTLW9p4v9a4KudMibL51vXzDxftET8++/+Trv2psDs3569ceL/xiR'
        b'OkZbfnDG5JEDUjvGLvf/d9KPN8799e3Q1tenTyq7ve31GbfLn7QaN7++sGXWH0a/f/lpyHu+7+l0d147Vv5Hyc5HO14oGzz7rzNTJk6WW66lfDR6J741dc6szhmdC9NV'
        b'lpPv/PH0a+cPHRmcLkqv+/jIa6tfk0SrxwwZvb+9Wj9o0Kc/7fr1K4Nj5+ypfvPdf/zmiGV+SmD1b99YOXLurz/82PLZtHNfDRo2rePsz+2Tlvsdfevaj6M/9p1Rnh/1'
        b'1X+tfn/Q8k1pS37d/n+UC+Tpj6ImZi/+/aX56Zmdi/D8n9yI2FvzP9bY0fv/+ucP3kiq2LtOtFT1lfzjuoM/rI/8Td3bkV8XPlb98uq+W0u0QeuWbzdvu9wR+MKMx4rk'
        b'O9fa3u8+uuO/Zn/evuVPPSuPfLRGF/ib/UHBy0ZG5P7r1KcPZ66L+eL0rpRpg967lpry+5rQaVdNFa/F/uvBgPp1ii8uXFit/N/h6+qSXrqR/qcfTD1+YfvCaev8dl4O'
        b'+4NF8bm2sSXpLxl5w3/19T+Cx034hH2xXTHQRog2Oo1uWYihdGt5H/cBwXngGtpJ3ady0ZXVxME1mhjWOXQI6NRN1E0tpNpS1AQyEagTUkY8iwWJ8yR6BOygm1raFkOt'
        b'E6gtuAF23/EAC9TqCF4R6CtlwlCXyAzCaAvvDNs+Dd3yR+djsnmLLr6D93HMAHxfhC43FFEzrQZvrHVzEJtQha7nYv4pTZRmDmqLjUUPgYxQx1UZPsWhNnwjjI7RlllE'
        b'DcKD8V3ezifL57RAW0/YyNaTAA28hB4UwdaCya1gM9EVCa02H22dk4WbXN3OOCXajm7QAdnr0AMhQlCsZvF+3IG60Ql8gPp0TBehLWjnVOLV4XTpwBf5+Lsw6UQSOp6J'
        b'jz1jFgcJ5CU+/u488Ppm6mDhdMKIRwccfhiTGRvlAcfRlcjeQvnoEoiUpxx+GEwFjcAbiu+iXeT8f/Ikg2g0xNdZsHZGp0vQUXQX3R4dRoNF2CExsIo50rUejKJ4s4ga'
        b'/eeXRzjiNRyxGjH4kRkk90f8Q4FL6L4vtIJbOKmb28eNxZ7Owf/OPqE9Io2Wt9jY4OK02KxnVMRTWMyGUpc8P+pBHOr4cKFsnw+kDfMJYceRsGx2GNQgfwGsjBvGytkg'
        b'WiOEDaIlQ2jpEDaMtM41BvaaYmAsbs7IhLh/18A3jq/Va70HOZe5QMxBBMuc5qANzLvD3FyT3Ubh+YE6tfPxL3JimiVOOx9LjRXeH6s3PfsIL4J51lih4I0VG5Zz1EgS'
        b'VyYuWxq/lOGNf4SNo+2rhmfAdidyagQTsQqdpwzJAmLsQ1+8ExFjWDgTjnePpsWBTDTj42xtIrSWwCQU40e0/UPJvuRYvrg46aTBS0YKj+0/XcH7iV1bUjX4G3EVQ6WN'
        b'qZUDEpNUIjE5eJKptqHrvOi2DV1DJ0CZww9AZkX7Gd0QQfWePYM/wjNOf7bw30YV3/J5NoSBnZUWtyJxcZie5RPfmxlIrDWRcSlZw64szeITOVhkoB2yOOnO4OJZILJT'
        b'n6eTIBwfKslHF9FREOjmEdlXsoJF91m0gxcnyJmYLybGSfEtYjIZB/p5Gb5NG/SZxjutxS0fXSsd7Ms/DEVnUrJn+Qv8uzFrFJUUwqzoWByQ08N+JOQb/i/Cp3gx8wre'
        b'gg+j2y/gw2Syd+D/THSSLm9lwRi0NwrvBmAqQTI6ig7QTneJJNQ3Ly6rJADbZfw5plUJ0MxuvJd8JMz8LBZvZdCtMFAzyDqvRae5lVmItDSSGYlaFvNK5mW8Gx3DbTlA'
        b'+i/0OhS3cbmVRfzMz/rgyyVKOQhlV4gsu5MNXYq22on3OTpQXJxkp2EwzKqJYl6b3RCBtzXig4iY41Yzq4GAneGFyt21obNJmCEg2hpmTYWaPnKl1tu/lrJTddUUY9ki'
        b'OX2gOjlHxqNP2fuW4esm8k9ZX01xAPmFqZ+WZfKJ89YLQC4Lr5sR2cgnJkQIQF5xNeyHDal8YsQgAXGkP4xOTUriE/8Qwzs5xqVETY/JL+MTrRJhdVc8jJkbXMAntkwR'
        b'EicEzLSK1jKGnsc/lFiVJArhwej6nTkFoviQ2Refvl5dM6FpdfnYd67NXCyf/3Xoa+/d7N66d8uvfjpCvJzZt61EXrAhTfybgoHl27b8zzdvJl9I+Nml+Z+gmIEH7mnf'
        b'aTm1dbl08Pg9OZei7yVEffV+8+RDhj9fOH7/2k/rfvXW8F8lDnx0oXbV75Y9TP500qlD7ZPenbXwv+R1O0f+4VKYZfX4+t0Rg2oTi/+AUo7+b9eFqzfLr3R0/tdXgXr8'
        b'G4Pd8q+5H3Z9cqbiV5+pHlwKu6+dEpoZOi90r/3HV7P+NBHn7v/jJ1eTHr3M6AKq17/zl0/GDv3/2rvyuKaO7X+zsAeMiPsWEZVdAQVcqoKCIKsCrlUMJEAUCCQguKAi'
        b'oiDigoobigtarSvivtaZvu6LtbW1qVVbtfVVa/f3rH3t+82ZuQkJJBH7+vv8fn88I5PcbbY798w5d873fMtv/ZHZJX3prW9Xrf+58f717s5Jkp0zP6ntvDF8Y2fdmNh5'
        b'a4pfu1m1dqR828n6AKd3tjXe+2DMI7efZn1S7vDkN+k/7S9Ouzzg1wXDOoZcmXlz9Z1HEx8r/X85r+7wYCG3IsmrSwGNSLSXqOF7zK4hE2v4hJFDx0CiroCmEOc/C84j'
        b'E/U+osx4w/R0UohqUU0IPSyKQpXNWgYuJQYNYGPQpUA6raMGfNmWTLlod59mP84UWzod+6F102GijQMDFQIfxwo43ICOu4aJ0BFi9rDYAXiFH4SXApx7JdEoFgmnoV3u'
        b'vuiSXiPbgdYbu3O+hGtb6GQpLHYB3qpCVEPwEXHD7UX4iICoA5Uu9NgcvLyzibuKxDcIlWYxUp5VXUiXAa0RBfaDQnAYrRFwnaaIu/fApbQlxBY5NNqIsYi+a/KY6dpP'
        b'hA6RLtnHgKENPZOM1Ru8Q9I+exIrY1/6QFPlRcTF43VMeQmXUz3BHpXJpnu2VCXURIico3n4Q7xnY92GzJTeTLNB59ApqjVKO5KbXDUwytffH15lCziiyxx1xQdERHwd'
        b'CmAuA8fQ1vGM/qjZ6RXV9uf9XhvRTuagWzEaraWnrY6xIdbhZrFQQG5F3VDmA1SPlhONrRptGqbHF4ATQBzeQN0YSIYVuNaCx0FYMPU5AIeDOLSdYRVO9oiE1ecmtH+g'
        b'sbZajFfSUdCBNM+gsYnwvtZK2yl8MY7WzD4O14GytaOrqZOtQz6r+FEypHy80Wl8yTjIkA/eqV9ibtN6mRg896jONctU59JIBGKhPryAG9W43MinE/l0IR/YdqGhBtzo'
        b'Ga78H3z0wXIkQkeBTAgrqxKhPcWAzXdp1mygYAt+blaAXsZub4dJ8tiMMrXBZHWtRZEkB8o9SeT1v8nvIzTTePpfs46jiuuzEV7xXp1b8qSCw68G9FbmBEy9g8ExWGev'
        b'dxfV/4IVK+poyWBZ8BqFenXQhX+6KExXDXWS1MSwiWFxqclTEyOSdCKtskAnhsABOif+QFJEchLVKGlPsL78z0NRaIDBzRe6FapvL5K2bxMWy8ZF7OLsYutmL7XTB52w'
        b'pSPB1uTjKGIjhG0JWxzVf6Q2LgI3UZexLOLgUXxUaDwP2HBSdBnVJYumoTNqk0VrPX2LdmRLyljxhnaUUrWd/lsxwPDLrtpO4Uk0aYBbtMsAYIyTgUBWonBexilcFO14'
        b'Alkp3W5Pt4FA1pVud6DbQCDrRrc70m0gkO1EtzvTbSCQ7UK3u9JtIJDtRre7023JBnEGB7VS9KgTbrAFGMxsZ0XPrtxsFwCM8Nu99Nudyd8m4WqBwouHk9vRCEtOK9qt'
        b'kGY4KGSKPowclhxzoFSvYoW7ou8y+2lS6A2FR7VgBbMgJCucif1AaWvJ+e0Vvamd4M3TwMbERzytNUFgJ+vZTMkhxgEr8wRuEGB7kucqYJSrWpJOmmx4JwMQnKd3Ir/U'
        b'aVp1NpBOA34dQvsy+kwILazMK2DRrSmYvUXEZcuQTTudA89YBmw//E+60mzPIpAC748iY65ONCeX7MtRKlSFOWSffR5pTZFao6BCgnnIGvPGmoa10scQdyBGmCO/duxk'
        b'CGv1LObYLC/xFz+I2socC339p5ljn00c24ok1iyU/08Sxxr1v6EeEIXcSi3IYUt1yJXJs/Oy5H7mqjJUlp5Fikynsb6t89hap7E1Q1n7HD3yTBpbMvRYWOSxkZNk2fI0'
        b'IEwnP40jTXv5t4jhzHjZzNbCtOq0bz0DjbrCTOX5ipDh/wwSXUuEueZjPVgi0W0jYa7ZTJtJdGV/njBX/4izbmdbMpWCv2FBz7phernAx8Lmt2QaZaZKS3qYyCgiyuhw'
        b'8pUV8retMBdiUj83L2079v7lI6/2nKygl5DLm+U7Km8kRyMJu6MTRvyxykRjBtlmtd+ElLZ8tEQa6chWsud15Dx9D4ITco/YRT0Y52uUaKZZQlpDdpTKxTjHbVJcnyfB'
        b'DXjPizTbLRMkXJfiWBtgunWxX8SyReWotsiQ8URUa47slnp1G3lbn0EVTmjXPG+a7S4/Yo2PjQIPCt/e3WO4QpDs+FIise9a1XcKPkmyjfZJMs5tCV7jgDaivbY0u0ce'
        b'Dpw0NMsOeHOzMsNYLSeiE2pDbuNQuQnlbbO116KSp5yIpbLUk/HFpDhxbrNu23HSWb6PMjvybDzHh6Mthnw5CPdryNdTb9OYZHoOHXTCFRnJKsmsMJF2Jeizwf393nnb'
        b'OTxAMvaD0MWjPMvCH5QKb0wJHzG3wtHeafIYr49eVWzYW/j4Rsj7vZZL8i/aHj0y3H/9uEU7ZqblvzF94bSGL06Jh+PAnMd3dQOCHeLC0rO8Tw/fduLr9nfKZ95x/qO0'
        b'aH5pyqLZD5PSK992u9/5/mvHjyZsX32y551RT/KflmyddkZ88XfBte4h50rFXo7M9LtMevSgiX1JKt40CszLGHyR+oXP8kc7TRlzp8TS99/onIyF0NvX3ziPAegsG2A2'
        b'XG+8WYyPJqLdDIa4Ge1b1NJOdfegdmqCN7VS1VlTjCDnaNMIYRBeMYe+vy/CB/Ee3oKOmc4saGIab6YG4Rh8sYfBHiTj8jQ1CPFaT2ogv4DP4xOtbP0teB219SP6sNpt'
        b'mgQ2pZF5OhFdZNZpHl5TAPAZX9wYzZRWP9yET6F9qFZLX2CQPbFUjSXDOw4ts0Pb8eFpf5nybsBHgkJkZM4t5sIpCa7AtpkQl5Hj0jimhi095yxRNyzQ456B5Cwk5yA5'
        b'D8kFSC5Cconjnu0Ta9+WTJxN2uRFLtSC3Wtk5y3hPjUJEte65m0lh3VMNShKVtBvKSJTnlwoyYgnF3ZZ5cltG6wyQ09haqQ1WanUFH2lnvZqUQOqBTwHd6oBcajXj6yU'
        b'Ot1Qam9W6n/MzytOJTqRlRJnGkrszko00pyev5HiVKL4WClNbijNs1k5krdErT4fA3CWvn/1qoiV8hWG8rvB2wsjfeVP3VG9vmKlxEyTEkn/GnQc4zEsZGBn+nbD4FMb'
        b'ny7iKwKe6PC0Uqda8Pqnq1MQ8EHIW6eONPavJENi8Eu3seiXLqJNEP9i49pmiiUlUEm2lWGJnvw8BEvGhEqtsgSCJQMe2dtX5m0MiybbFGdNTjKmh6E6K6sGsG603a4z'
        b'FDRMlqTOAeuAWdMQmY3HNsvT1IUFPG+RluihlvoG/gFHiBK6RKHKoAwyBbyebdoovr9puEnSbZl83DkzKi78izYwHsmtmWwBwUaGisxTT6ti2WQx7lemjrd6MGWeYWka'
        b'ZXpWLjC68PYbjT5ntqLN40CrVWXm0qHAeFNakXdpZSrjVqmIKZNpgZxFb6IE0JscPNRgqUBJAV6+8P5Dz/YLZxjoftMtGVd0VKro9cAhBX0XOrTtHFQZpg2CVquU2r+O'
        b'QcoTGJMo15OXzNs7B8xn0px53t5/mlNK5kn5o/wYDdPzZG2FP6pN1z8vm5PMAguVJTYn/7ZVwwTZYZXTydPA6RTgJZseEGiZk8kYHcLfxkIla44ql1aUMrCPjYubOhVa'
        b'Zi78LPzLk8/LocFrlRqYmHwpYZvB6jWqUKD1ClklmjJ9B8KeloH6J8VstZjaY0xPRYoPGmSZacwYS6N/I2T0mJC95InM1apYpdQZ5om7FLPJyKD9ARfQCL7yYvjdRs4i'
        b'+BdmkomWvgxTpWcVqCgxlbaZNq31M2sxTz9ZAPA+KwuJcDVkQEawSsZ3EZFQOeSJi0jxS5YXpCnhBaN5Gi0/GRkuLNRodmHOHGWW+f73kwW1OI2WJi/MmF9YoCQzB0Rv'
        b'lk1Sa7S0UhbyGDxMFlaYkaVMK4RHj1wQVlighvltjoULhgyTRecqVHNVZDBnZ5MLGLmbtkXLLVwdbK7Kz99BIeayURlVK+f5qhVqLr/n65ehtCObu/4ZPW92ZzIbyfAm'
        b'sEW9n3skGjc/Q0Na4wl9a6iTPG1+YaaX5eFnfLkspJ/lAWhyYsBQS2eSYZY7sDVvJjs4pGU2wZayCbaWDRkUhvZZySPU+DSLTRtqkpmZdlmc0HisH5Fw/C+qDxCdlMhW'
        b'vSj3TGJzrMUJuxlKCLztZCpkW0TH8Ywhm8pc8keGuQzmoFAr1O8GEKJpNoEtsgm0mg3FK5qQC3pSRsGxMN8MsXiZAd/ILo1IoZIadsg8yUPOD3Fy2y13Q6EGSBaBu57/'
        b'5Ssz0u0iUibKPCfjhiwNeUhJXQZbrooRtLI5M8NuvlL6rLRzCjXa1pWypu5ZUi+pKtl2zc+gooWZvNRvmw5DwaDDZPHwJZseOGhG2y8LZJcF0sss3w09ypRXIfltMJat'
        b'jQMKQSWXwBc5sfV5lqVYlFKjyR0YqZEXkiTbf2Ckimh3lqUWPd2yrIJ8LMsnKMCygLJWMpFKEVlECSOy37JoonUjOpvCfDUsdR7RYpXKAtAs4JsoWMFW9bs0dfEwGSwR'
        b'E/0pA7RWsoP0ueWbChcBAphdJc+WwYbVK9JVBfBAktSquscAz3Am+0Ez9gU93S8oIDiYjDTLdQLEMakQfFkdkRly0tpIIlSsnUQxy+QOwZdserDlE3kxp+dPtTKi9Wjq'
        b'YbJw8otpwtMDQ6yeb3i06SWmi3ZW+1uP0eavZPfHsrAGbDZR0cLD4sntsSwR01TpJMPoMaRoM0+kCcq6teMyH3tI5s4cl6Wx2ZIieTZHwUBoo6OQouKiJxmj4hagOnrN'
        b'il7MdVMWoswO9h3Dw/QO57nE4G2oRg/VQ/VoVy96frvATpwvKWKJR86Lj3pGMUSOphgtw+sHo1MUv+ePjqGV1IN2DtofFROLNqI1BmQUhT+jMryW5jYkjnk9r00rHP5G'
        b'al+OMjLicrxyoQ85G8gOE8BJEB0aHzchKtoxzDc6mcONqGoiVzzYIROvQg0MKJSeIHx1mE7CyBTXF0fwi1FNuEZrLuiRuycEVIpiixEmXIrVaIvEa3AH1fDzXW20X5A8'
        b'Pg9Ql69+IReNlpZ//a7uYe+GDe1/PiAdd0es6mvzYJx/9psrg3Mrsh1ro8aUaZYm1znnS+Y22UUFXHtwMeT2iL+t6FjX59DNqf888qSuauiYw8cVTtd0TQtS9uz9Krp9'
        b'zb+2df6oZkq79zuvfLq15rO03X9ErBy11elE5Fujg/x+u7exbN1bdyvWuW0dkoHsD+sO+dycUXVmXtTnjeddzr6Tphk1+drLDmdvP/HziDykGvN74J4rc0+eL+1vW/LC'
        b'37PvFTfumvGo60ci9YF2TYvji3bJP1h2pLPMdVLl96LT/6rv83Pk9b8LZirHbfoxI66nlz11ryyZlOuDDqNVJrAQx2J6bCiqQCfQQXRBHGvg3+uAt9AFpxmdcKkPakrA'
        b'lQnREBHKNlvojpajM3RRLAcddDJZFHNEOxkqpGgCdXWV4PoYo7UiwzoRLotrsVQ0DFVRFMko737mIiUdy6bBktAqX7pi5xaJz/I8fWiZQzNVH/D0oQsiipCZjy9FxsRG'
        b'AxPmCW6iwBudQ1taozkkf1HUb/BWo8tTELTcZHlqMZdgT8n2xAIXgQcNnQS/wXPQkV+aElK/w27ku5PAVTBfYliEkSsU8SaBO5pfUoP3uNF6lMNzVdxLbJRJc5RPQ0tm'
        b'm12U2uxuvChlUkvzUA4ahgn8iLgVYkMYpv8yF7WS+mKzUp+Hq1xdzNz0r45R+x7M6MdiJOBVHfAObSHAkavFHHkyBKg6uGRmCcOyUDRCEzqCNzvhXaiU3JPJ3GRU6swm'
        b'jHK0JTCJXFiGjzKM7nkOn0ArEIPITx1RwoAqXQu634oX8pDM7SVxQYMZGsUpXYnr0V4ewC+LCBrM8CukuLJ0vDKfOQ/0ZoCDq1mzJL8tljH8Sf+e7SmIYac4L9t2ZD+2'
        b'c4aHhIIYZk0v8M0fGsN2lskYiGGtOlPyTbYLQ+dE4vP9kjQYPEr7cH3QaXSEIY7X4TJl0KBBeJ0DhBHADRwuDUUHaT5JZIQTQdXllTCNr1NyHN93ZWj1SIpe1oNdQvqh'
        b'cx5dWYtK26FVQYPiY/RYl26okZa+GK8eHBSFqhnWBwM9MeyehDZNxes7oWU8SqV8AgtTcRKtSmWAlBfRJsCkMERKl0JaL2m7bO4GaXRisTbjBVcVm8nbd5plEtm+Soir'
        b'uo4nQu8oxYswBFA+A4fIFFmx12Ons52b+rpxnjBC8ub2OOj+ItupK3yFWyLgQl/puyBg9rAObOIPDUdHtc5B+BiqJe0TooMcvpivoRiPDxewm7NkfL5kkpOYAT8knXiE'
        b'iUYVe2F4FNvpPJjdHM4hLft8+2K2M8TGjt7wYwG5kint5WwMDkXbUFVSYmInLpHcmbGkc2VRrJfPiHzJ/gkcADP3kRuWjE/TgbZQ6kL2lxj2l6BKFqCgGp2YSo706qTP'
        b'SY1X0YJfsWFoK84/L7bOqSM/+Ku6BiQlhoUm0tvNydFOMoPA2S7urJWJ8fNis4JncKqXbtcJtcPJzWtIEuSsOxuPR7tF3O7++qc931g6Bl267+P5K+fh6N1gP8MrLavu'
        b'auKN6/Zv7h3l96VIOuT26CvbQysnymL63g5S3yp5u0oRuD7WqaT+q9dWpgwomvjgw5IMTXT1h6ffHPFVfWi5Sz+nienVe5ZHl03J7ZfSXXasY7J0PvpNen1y0+bdtSP2'
        b'7PD5yW/opA/yXvu4eH7KaefBW77r8qM8Mvyah2pd3aHKIoftNaeiE4qy5kRsscvs9/lTv/wdC3c3Xb99JmrRfl0wuvSh80DFD1Vvh6/3jn7pwpiilPu9Pl+48VaQ7/k1'
        b'NjPGPvjh4deC9IUnRl/8abFY9GLAH7NkTQE+37rP/SZZ2WuU4/JTNROVWzWoauCoIZe+a6wf89UZ/9+uvPvesv4P3yspLFk16Xr1G3s0Hz8MQpsX/VKd+tYL+aPG3awe'
        b'EZX+D7ufEjSCBhcvt4KBVKvEBwAIAtM9WtHHdMZv6RlSqqLqRdo0tMOHahDkkD0+L3TBG9G6OfaUgAdtlqQQJRFtwWWxAk7cR4C2L7alni7heDc+a0LAiw9On4cqQhhX'
        b'5D5cg0oZIgY1oLN6coZGomnupVpGMCofH9MCPxw/CNAqsggbhwh0mepFk7V9wdUGr8WNPhBHA5xtItElWnFPGW7Uw1VCiMyhAVZRZSJzKNo2DR82+AKhy7iR+RSBQxG+'
        b'HMcHogzGDc2oGnyCCDbbRUJ3fMaHgUDKXiAai7GfEFpFfYUYomUJ2kDrGDYFXQBAL9qfo1fdyF3YS/sB7xviEIP3zzTBtLigMlG4H6pnREYvLxQB/2RNa0hLb9aVVXgv'
        b'qogJtzPGtLiUiMailbiJZlE03bHZXwiXjRxPakj9hVClL4MfnfODOPLglsSFxBBzA5ySps6kvThWNcGI/wKtFUbjLWo3tIo6LAVlos0m/krkfh6GDgB/JQGqpXdyHtox'
        b'2dhzi4ylcJnB6Qpv7Gwxep11fU6t1+dyW+tzeaC/8XRsQqmQIQWkPHYXcCRSos/1IHulRL9rJqiU8n9CnsbNESgreXyJlEcMAO8Lz7tGNSvr1G7mm9aK5A2UuR4tlbkl'
        b'3A7TwIstCyX5APXQX8z1lvFfrrdW6p95rjc7xvXmjA65GKjezNG8oXNCuzyij7BAQoumowrG3IbWaIG8DZjb0JIiOruiS/gQrvex43CNAwBX8SoJmy63oqYinwQh2i/j'
        b'GH/brqmqBaGBYi0YA98rE154l/K32dzJHGDzVn2XUC5NcY+LfZFb6ynK3hIo69hlmIdTxvdin9f7qfqdev/47aZu7RJmlz+OeferR595f1owf8q48ITjN6+hzkvtT14a'
        b'8H3J66rPst4atkfa4cBU8ZPSWVVv/+uddXsc7r39yhX7Dt+klw9uZ7PsYePvQ2b/+9L616cuy/hJPaXI+a1v74/NmSXPLB/VlFX2y4cfbXXt2GPujbvLnm4rGf3rU8EH'
        b'K4Lcblz0aseAhhVoRzj02ko5pW8D8jY71MiYxC4leTLuNgNvWyd0vAQf5GkvDo7DJ4HOdxmuZUxkwM2G9yczebgFNXbGVVphMz8bY2cjSh6Th3hXZBpumoh2NpO/Mea3'
        b'vmglLcAOHS2MaZ/YzN/GuNsqhlPfz4x+/jCtBKDzlLsNiNsc0GGac3d8fCBIy46o3sskdPEBfIq2OoSowmtI1efgcgMtZt9+xQy/ty0mEwjScB1aT6zxZt621Kmsx07j'
        b'VTnA21ajZtRtQNw2hEWxGOSYEmMYcQ5uwmnwugif7coO+suBtA2fQjV8d4ULu6CyEbSv8weR6xgydReZlfXzMNo3j3YF2otO2fgMnENMBwoppLRtRDlY8pfQtlEOMCrD'
        b'vVvL8MWcn7t15jYQhX85c1tvsT6u8pIWn7tmONz0VbDG4SZmgB56nOL7hKxw+Ir3cm2J5gNPOCNIXxvcVY9zNKB7gTJHyzB5LfjV2v9Hb1DacBtPkaSPiH+1Ym8rFpKp'
        b'VtjJs+10anCDuwhkRa7DaRAkMZGOF7TsnRRaTh69U1obzrmbEK+X4OVegniVr909kbY7maR2C36OWH0eXg5GZH4S/KQ0wPbyEumTDQW/LnHr0/Nv14Oj3Cq3Re16M2Ca'
        b'e/X2o+8dSm9/WPFt3fYFaxZ/+X7S5LnrUhIzv7v74PHVOTWfdv/q99uS24256nsPi2P+eXGnLHY2+vnNgE+HL/jupUl9Tnwz/eK1vRPuxRdlDXn17oPuM768e+PquBFf'
        b'LPu67oelmy58udTn1g+3PCrW3UQji/vPe798U4/NXFDDaemB65NrNo3bM2hcf4/f3B/+MlvhdA/9WDrhdMfxX04YcT9Rd+1K7ZpLNd1n/rS8d+id7V7HXh1/3Ofg4XPe'
        b'bp8f2j0z/e3Kn2v35074Lqa+dse/F/ufzUi95jB7cE3uoccXrzxcdevBO69/Pv7U9iTXhYOGfnwjKiOoy5AH5e4/OfluzHCR3/AS0ZC2C5M9cBXRyZLHCkI5vBo1daAK'
        b'cCh+aaSptzzejGqZv/wldIayAA1A56SGV33oHK5sERgd1+O1rd/Xdf/fGW3PnRAxJNQ/bWYTCkK2T03NVssVqalUDEHEO66bUCgUDBbIiNixFbgK7bvJ3Lp5u41yGzAC'
        b'hNIL9iIXp/6Lubmaa4YHTKQTpqYayZxu/w9aL9B8aHg+oaYg7Fk44gejjTngqFhCO9BJBEypa3BlQuyYqagSrbHjXLqKehJTZalqxOSPOEoYoPUI6Vn5piN53GzOZ9Z3'
        b'6XileuedH6P/QGvHbD47Lzbe9rdPdvz+yWtDUzpuDJ2wrzKy25PDI0f88EZZ/Oz8v23445OKoydcO33zaGXnl9+/l7j7huur10+d9fKZsLfjkW9/PJf96qDSVxKvVgzK'
        b'uoqQvKrnP0LvVHR478Gd/CsdBSE3f3il6buaBLnL7stPI/L/EOy57hn/gYSoEtSWW+ZJoytUJsBSBdBBO0WgJei4EO8nc95WqhUMRkvwkZgEP2ISktNg3m6PL4hQGYd2'
        b'FTiysEfH5k5gXQCYELQbbwfDmHSCq6gX3onW0DfW3okk/+g47zg78ghcIILOvmABPYD3Dx2KqwbacvhIqiCJw3smkRkfHr/hcQKf8TYcXqcSxMAjduBFOu320aJ9lDeQ'
        b'lAX4eidbVOclxGtDmYozOqCT1uioY2ZktBAdwwcX0IvdcTVqiKHisVI4mIUxxStF8YWOzJxbPgmVwWG8BG/nF49wWTHtBykx116mrMFRvHYlwRsGdRBC3C0/mrnnIhty'
        b'zkrfPP64o8Ms1CREJyYupDIhMBiXkuPH8R68TYIqivILcVO+JL9QwHXGa0RoFWrCjHpxPJcZQynWoB0c50QObUFbhXh3gCtF4wyzWUi7e/3AgTFEqgDz4hrYYcd19xCj'
        b'MnQUVZsEuu75f/9MtXzEHJ4hYMzIm2aQDOWpdbZn0aEoVQPYpxLRyJZakAdTBqig6a0TZStzdWLw2NbZFBTmZSt14myVtkAnBoNQJ1bnkcMibYFGZ0NfaevEaWp1tk6k'
        b'yi3Q2WQQSUe+NODgAQQweYUFOlF6lkYnUmsUOltiGhUoyUaOPE8nIlaXzkauTVepdKIsZTE5hWTvqNLqccA627zCtGxVus6OIaW1OidtliqjIFWp0ag1Omdi5WmVqSqt'
        b'GnxQdc6FuelZclWuUpGqLE7XOaSmapWk9qmpOlvms9ksPFlDe2q+g98PIfkKkpuQfAYJrAlqbkByF5JbkAAXn+YOJJ9D8ndIPoLkE0juQfIAkk8h+RKSbyH5BpLbkDyC'
        b'RAfJx5Bch+QxJN9Dct/k9jkaJOmTsUaSlB57ap8BjtnpWf46aWoq/5ufYZ5247eJ8Zs+R56p5PHmcoVSEe9lTxU/YNolpi7PtEtVQ50j6XFNgRaMY51ttjpdnq3VSSaC'
        b'j2iOMgJ6W/Ojvt9aoCt09iNy1IrCbOVIQEfQNwxiIRFaLYdYiBsNjPA/K23Jjg=='
    ))))

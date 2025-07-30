
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
        b'eJzsvQdYW9f5OHzu1WCJYTzxlDcCJPawcWzjiRDDNnhhO0ggAbKFwBrY4G3AYGO88MaO98B7x9vNOU2TdKZN219LkmY2u23aNE2bpsn3nnMlIVkScfL19z3/73n+xlzu'
        b'2es97zrve+476LF/IvidDL/WCfDQo2JUgYo5PafnG1ExbxAdFetFxzjLKL3YIGlAtciqWsQbpHpJA7eRMwQY+AaOQ3ppIQqqVAR8uSZ4WlbR9Hnyqmq93WSQV5fLbZUG'
        b'+aw6W2W1WT7DaLYZyirlNbqyZboKgyo4uKjSaHXm1RvKjWaDVV5uN5fZjNVmq1xn1svLTDqr1WANtlXLyywGnc0gFxrQ62w6uWFlWaXOXGGQlxtNBqsquGyw27CGwe8Q'
        b'+A2hQ6uBRzNq5pr5ZlGzuFnSLG0OaA5sDmoObg5pljWHNoc1hzdHNPdqjmzu3dynuW9zv+b+zQOao5oHNg9qHlw+hE1H4JohLagBrRlaH7l6SAOaj1YPbUAcWjtk7dBC'
        b't/cEmESYjgqFKL/MfZ55+B0Iv71ph8RsrguRIiTfFAjvvw3mkTiujwQhrWlTfQqyj4LIKLxpIGklmwtyZ5OWfNxE2goUpE09d5ZSisZOF5NH5IhdwdmHQtZ0vBc/sqrz'
        b'yDayNY9sJZfwJg4Fq3l8BR8g6xW8vT9kwi0T8B6NOk4tQfgh2SEWc/hIPDlqp73KTMPP0CTctExJNkMlEhRGtojyl42GwrSFULIe78StZEtcDfRpqxofHCJBwfg6j2/g'
        b'o2LWX/xwHW6ALNdkuGXFcju5TvbituWy5XYO9SfbRXhrLd4C/aVZyTm8owK34u3xGi3pVMbQfpPtNCIADRolxg0LyL4y7jEoHeScPRNdTmEx0XdbzvJBjqXkWgCa1/Cw'
        b'lBxbSp4tH7eWL3R7dyxl+eNLSTvTz2sphwlLqdZLkQyhiMkKbdzo6aMQi/xxFqwvQgveDNfm6tMihMjDoiAUATmnLdOa3laYhMg/9JIg+Ks15Gvj+q/RoU5kCobol1Ki'
        b'xH+PRJM/7V3HaYbdShy3ZAQyBUHCp5YD3JUAJE+IMmd8bumlPiREaxZ/Fr47nIv+FK0rfn7BPxecR13IrqSLdButgQVsjZ8dHQ0LfZRsic9Wki24syg6J49sj1OplTl5'
        b'HDKHBz3Vf63XEoQ4R50rLIHnbkJ0AcpDXFPMP/EUN/raLVKvKZblW2gv7HTySWe8vYzcLJyjnMcjXoTIYdyGb9sj6Rgv4yu5hVAFvhM0Eo0shOg+EF0Gw7xJdpFzhXMg'
        b'rRJNJ3tT7L0gQdsnjbRDxeRafDyKx5dzWC1kJzmTTtphCvDGMCVSDi6x96XRp2R4PbnVvzBvNmmTIH4VNzhwsX0spMjJVdxIN0esBqB5c+7saNwZl822q4q0TiSdErxx'
        b'Fmm30zGRrTH4ML4OQyRHUiagCal4pzFi3jDe2gGJz5+rWvKzxDCcIGvSvZrX1dhZGP5c1IADHxxfsFCX1a+0au4t2/A5n9+eTtT1KXN27Pjxu2+terQ1WPW3Vz6/8dpT'
        b'h99vl6XUaE9l2hcZbk/OXLps94a3TtgC9vyg97JjY9RTY5/9ffynG965m3z0vH7Qo73Lzht2/WbT9Udv6vY9XxIfPfE/hya1zvvwzJpjYR2nKqP/1vBq8X/0b0YOe+mN'
        b'P3y0M+Ozv7ymkNgoNiDPJONtS8M1pC2WtOUpcyhOiSS3RaSZtJNnbXSnwmQcqYzFz+ItOUrSos7Nl6AQfJUnh+tG2gZA+nRpdqxKkbNwTqwD34ST9aLqpAobRUdDV5m0'
        b'40Po9NkBOWyJ51EvcleEL44ZZoui2CoV7ya7ymGut5DtZKsIicdx+CpuGqDgu/hohYUCjCKE/fkeDwp7X/abUG6prjeYgbgwsqUCkmOondgVajGY9QZLicVQVm3R06xW'
        b'OQXYiYFcBBfIBcNPP/gNgx/6NxL+RvCRnEXqrFkh6pIKhbsCSkosdnNJSVdISUmZyaAz22tKSr53vxWcJYC+S+iDNjeJdo7RRCLnpRzPSdmT/4rnYfdx6Gsaso+k6VvI'
        b'FbInNoe0adRKvMVCmuMBGWyLz+HQaHxVUpKPr3vsTvpP7PhrrYSHgfIMwC/ouWIR/IqNqFgCf6V6vjhAH9aMyjm9WC9pDCoOZO9SfUBjYHEQew/UB8F7sECey0X6YH0I'
        b'hEMgDMgFwjJ9KIRleo7xGOFd0jls8vLZZH74NWzPMpFbt+joA5yIg7I0rooFrCRqEQFWEgNWEjGsJGaYSLRWXOj27g/x8w406ImVxALi37mSYW40LldrGr12IjKGTFsl'
        b'sRZAzHt9v/lY+9PSD7S79C26j7RbKy4YPoBw8Q8Wkys7EptmHzq2t9cPC3RndSbJOe6c9sfinXFDZNMDfqsasjVkQeb6jwZEzRmwMSojGdW8FLFu1DGFlG0wfHTxsliN'
        b'k3bGSpWDUDg+LaqfQ67b6KoHkPPkQncGwJC7E2VxogAIXmK7iFxajc9qSGuuqgbYCoUUBeIt/EoTucr2J9kLJQCZadT44gh8GdBxBh8VRS7bGCuxi6/GrQXAMHDLxEhC'
        b'DnHkLnlYI1S7nuzBz8Qqsy14B2M2AskNHjcmzVHwbsAq8rXrGOx2BZaUGM1GW0kJ210yOvHFERz9kXJirj5cAACVM5ewqyRdYqvBVN4lpqxhV0CtwWIFLtJCF8RCCWIn'
        b'52w3jEaF0ke4a7vQRha5tsuZCL/bxav1Mv6xPeECvvEO4CvnHaDHM4IoAtDjGeiJGLjxa0WFbu8O0Kt8HPSQH9Czx9Ipvy+ThpA2WK5tQNnJ9kJ8BG/JhpWFdZ09i1HI'
        b'SeSYtFcsaTFmjLeJrAlQKFW97GMthcPosrjIWF2u7hNtRFllualUvCXR9kip/bN2wYsDfvqDA2Ho6OLAdW/uUYiF5X2Aj6zRCHUDzBTgowxskM02AlLD8vAWYPw2A1re'
        b'rlLWCMibXMONaOBaMW5KxhdZJXhzJbkDAIQ3LAMQcUHQ+kRbXwZd+Dw+qilQcmgR3szXclkDyXlhmXmfEAP4s8JgM9oMVQ6goegPlQZzMq4+0rVgrixCVWIGBF1is67K'
        b'0A0nlgihmUgXlDAAoWxCmQtAjoT5BxAf7f2vISgvIcMvlETD+1qyaYAHlACEjMt6HEYixhqLHxkl1iQo8cX+1z7WPv/QF5B8ouW3JNkTfpdwMkGcXHNahC5FBOqV/RQi'
        b'gfjfnIq3dQMJQAhuwqf5lRn4AgMTfEKfDz3Z5QUqApjE4EMCmJwnGwsEPKMlp11gcifNQUn94xCACKs3RFQ8BhFWT4iQCAtOl75LUqsz2b3gQuQGF31cwEFnu9IFHAd7'
        b'wB4+mvaPQCYKwEF5bK5c/D2QiBf94hxNeIKHJN8ez8Bjz2IqAhaRFqVSNTs7Zy5pKSgUeNhsYGeBq76p4pCNPAiSTsBNgjRxDWS8M48DlQBS+CI51w1WpHGWMaDk97w1'
        b'H4oVPZR/rP0IkI+pPKZfjC5bZ2IQVaNr2XPOcFb3gfbnfWpK4xjE5ejO6SLK0Ev9tnDTD/S/YkuI0+v12brA8jdNHErLCH847UXgSenEm0JXOTjGqkR3nhEfxJcEinaf'
        b'J6coUA4e7kbv+tbZhkNi/Aqy1xc04vMqAMhUfEdAftfwrogKfFyASSdAVgDJpFwruU22jAXCN4xcdiN85Cxer3BQH7FfhlMAW6m9hvKZ3YTPFAxMZSBjKOtDHcAj5HFH'
        b'YgJNc8Gq18YAfNZN9RjIUjRb5QLZPZH+QdazVS+J0BOVMZHchcq4Fu6JJUAvgif2CauifGPCvA+RNQciVh7pq9FlV3yiNUz7QPvj0sryPrqzkqsD+ico9RSSNuvOGS4Y'
        b'+JeU2ku6xS8u+MliUkRmEROZFf2b5xaIft0LSJsUSZ8Prz4VDKSNAogeH8CHBaw1UewCkIz5jOUZhLeXCcteTC47V948lqUZZuMm0hqnJm1KfHoQ1Po0P5IcnymAzD2y'
        b'Re5kpPAFsl7gpKan+waGnpAayAtWm8WB0KhWANkiQMKQAXjUh3VjFpqFleoUCSvuHzCAK+qGCSpV210w0dYDGnusMQWfb6GaAUUo5d0oPQWZJrikRFDtwbuspGS5XWcS'
        b'UgT8GlgG0FRRbanrCnTwalbGj3VJy40Gk97KWDJGdhl6ZQDLeuhE1T2Kb8KA6BQV0gFRVB3IiznHDx8WKJPIJBGBdrrqw1S4IcQp7gTKcCtu4LWV5KR/iUeFHpN4+GKx'
        b'XkQlnEN8sWQ30kuPgoRzjGvgQPoJZHQ6qEs63QwYv+7LPtMMpUZbNYiR8RqLQS+8fihwHR/SJr6MnGew1NsrrDU6u7WsUmcyyJMhiY7oS1muwVZvM8hnWIxWWyfPZv3D'
        b'H8GIPz8As6qpNtuqM/NhluXRWXqLwWqFOTbb6mrkc0GGtZgNlVUGsyLTLWCtMFTA06Yz632WM+ts5L7FpJLPgjWqhrLzqi3mJ8nnq7JlBqPZIM8yV+hKDYpMj7RMjd1S'
        b'X2qoNxjLKs12c0Xm9LnKXNop+Du30KZUg7ynyswyw4QZMouAcJris5bp9Cr5TItOD1UZTFZKTk2sXbO1ttoCNdc727DYMgttFh05YsicVW21levKKtmLyWC01esqTZkF'
        b'kIM1BzNvhb/1drfizkDpCto7Kv3LHR2BKJW82G6Fhk1unZcn+k1JytQYzOZ6lVxTbYG6a6qhNnO9jrVjcLRnkM8k9002Y4W8ttrsFVdqtGYWGUyGckibYgDOdRmtN9oR'
        b'pXCmyWcaAHbIyXKblY6STql3bvnMXEXmdGWezmhyTxViFJlqAU5s7mnOOEXmDN1K9wQIKjILYRdDJw3uCc44ReYUnXmZc8phjmjQc9ZozDIKw8p8exVUAFG55CRVtyyj'
        b'syZMP0Sqp2Tl0zSDwVIOuAJeC+erZxQpp1bD2jgmn+0Fo7kSYI3W45j2bJ29xqak7QDSKVU52nS8e8y7r3g69x6DSPIaRJL3IJJ8DSJJGERS9yCS3AeR5GMQSf4GkeTW'
        b'2SQ/g0jyP4hkr0Ekew8i2dcgkoVBJHcPItl9EMk+BpHsbxDJbp1N9jOIZP+DSPEaRIr3IFJ8DSJFGERK9yBS3AeR4mMQKf4GkeLW2RQ/g0jxP4hUr0Gkeg8i1dcgUoVB'
        b'pHYPItV9EKk+BpHqbxCpbp1N9TOIVI9BdG9E2E8Wo6FcJ+DHmRY7OVJebakCxKyxU1RnZmMAbGwA2coZqLEAQgbsZ7bWWAxllTWAr80QD7jYZjHYaA5ILzXoLKUwURCc'
        b'ZqQcg0EpkLssu5USlHrgGjLnk5OVFpg3q5U1QLGeQGNNxiqjTR7tIL2KzGKYbpqvFBLNFTTfDHLSZDJWAI2yyY1meZEO6KJbgUK2BjRlFlMLu1fWTcaVxdALQBjRtLhH'
        b'gqM8JI32LpDkv0CSzwLJ8ikWuw2Svcux9BT/Fab4rDDVf4FUViBPJ9BlNufAlwB/wuJshpU21wtgItdrsntWqyubsBBTDECOK9wiRmcWG82wGnT9WTs0qR6iKOkFLO0R'
        b'TPIMAvrRWW1A7SzGchuFmnJdJfQfMpn1OuiMuRTA1rXiNgs5WQFApDbrjbUq+QyBfriHkjxCyR6hFI9QqkcozSOU7hHK8AiN82w9wTPo2ZtEz+4kevYn0bNDiak+2BR5'
        b'9BzHrFodjIaimzHylejglXwlOdknf2kuVOYjvcB3a5Tv8hXvwYr5H0MP6f64s++SOcl/yx582pNkA1TpK5sHCUjzIgFp3iQgzRcJSBNIQFo3Nk5zJwFpPkhAmj8SkOaG'
        b'6tP8kIA0/3Qs3WsQ6d6DSPc1iHRhEOndg0h3H0S6j0Gk+xtEultn0/0MIt3/IDK8BpHhPYgMX4PIEAaR0T2IDPdBZPgYRIa/QWS4dTbDzyAy/A9inNcgxnkPYpyvQYwT'
        b'BjGuexDj3AcxzscgxvkbxDi3zo7zM4hx/gcBCNJLVkjwISwk+JQWEhziQoIbm5LgITAk+JIYEvyKDAnuskGCP6EhwWM8ji7OsBiq9NY6wDJVgLet1aZa4CQyC6fPylIy'
        b'amWzWgzlQATNlOb5jE7yHZ3sOzrFd3Sq7+g039HpvqMzfEeP8zOcBIrQl5nJ/Zpym8EqL5hVUOhg4Cgxt9YYQB4WmMluYu4W6yTfblEzDaXkPqX0j7ENFUK8g2twhpI8'
        b'QsmZsxzKFbfCXmqXRO+oJO8oEHNMVCjW2ShfKi+0Q3W6KgOQUZ3NbqVsrTAaeZXObAfyIq8wCGAK5NCXGkDhVsRIibtRz4p9a2Yf9fsgSr7r9s7IVEzdsyMH5lvuYHnZ'
        b'VJbTdMckC+9Jbu9UJuzWVH3JZeZ3BlqoOtRCFeUWekYkHKVQXaOFGup1Saw1JqPNMtSlw4vw1OZRi741Hto8Ec/x/5FKeJ7/mk/mf2an9aeS+6ut1CxlcxzuFKPAtHxy'
        b'jV+LH636L6rzyhVBXcFZZWXVdrMNxIeusCmw5oLYoasxmD7sKyjzqGr8y4HTAAqqgLWg+lK5IPgADBsB80AWqpTtElMWyDIGXj+/DxFzqwSOprrSbJAXVptM8dmAksxK'
        b'TT1VsHQHu5Fc5nxNsVwoRhVpFH1ajVa7EEHT3MPCpptJ9X4Cgy80NGWusrCs0kTuw+KbgClxD2ZOMZgMFXo6EOHVoXXpfk9yCEiZzplgDD/lCA2Ove2U2uQCV+SQ/bq1'
        b'VA6pj/HqVN6DzLC7bEwucNTAmjMZIQN7M5rLq+VKeZbF5uyKI0ZtpiUfi6TZknxlS/LKluwrW7JXthRf2VK8sqX6ypbqlS3NV7Y0r2zpvrKle2XL8JUNmIyCwqJEiNAI'
        b'C0OZXQOLTPKKhIA8zwAI06mKldtV8m5VLEQKsOzUjarklGF3it2CzrV7GeW5sbmZM+zmZcy012CpAAxVT7EKjZ8yV54yTqCz5c4sVCfsK94BN0KSjwozi5k8QAduqdLR'
        b'RBeI+EpxgYq/Ykk9FfOdKIBQD8V8Jwog1UMx34kCiPVQzHeiAHI9FPOdKIBgD8V8Jwog2UMx34m02LieivlOZMud0ON6+05lBXsGFP+QktgjqPhJZQV7BBY/qaxgj+Di'
        b'J5UV7BFg/KSygj2CjJ9UVrBHoPGTygr2CDZ+UlnBHgHHTyrb8T1CDqQW2sj9smVAulYA8bUxznSFwWg1ZM4AEt+N/QAd6swmHVUuWpfqKi1Qa4UBcpgNlCvq1jY6KCdF'
        b'eFn2cqoXcyE5Jy2FJIp5uwmyPDrLXC9wxPRAD5BxntEGpNGgBw5EZ3ss+TE87F24G5M/nmYxkVtWB5vgkZLNjnfKbcCVuOQqRkmUjN/xKQQ4Ruqg5kD6gdJQHrqccc9V'
        b'lMDbDEaYFptLUawGVtdmLDcu07lj/2ImB7oUyO5shiA9uh0kurNJMwyCaGEwltKkXFg1ejJmFTgb/4yau3IY+g0t60z2qmWGSqcmmxFBxsUpgIvLt8T442Hj4HHfLw87'
        b'iP8j87Ugt+rLrbn5ZFs8Y2TJVk0A6luKD6eLZbhhpRcjK3Mysks5T0Z2t3R3yO4QPb+79+7eAkPbFqCPa5Y0hzb3LhfpQ/SyxiBgasUGiT5UH9aI9OH6iDa+WArhXiwc'
        b'ycIBEO7Nwn1YOBDCfVm4HwsHQbg/Cw9g4WAIR7HwQBYOgfAgFh7MwjLag3JeP0Q/tDGwOJT1svdjP0H6YW3BemUz7+itWC/XD2e9DRNGtTt4N1dORxbAns5SI9qC9Cpm'
        b'USdhniARUDZAP1I/ipUN18dDmqQ5kPmJRLK00foxjUHFERDbC/o0Vh8NfeoFbfTWK9qcDg5hzeHlEn2MPrYxEGqJdJzpJ3QFTqNG4VML530ZHyx3++eMlgsYRHBj8sjR'
        b'KbFQOzgLdYb5kNmGUxOsD5mlBpUEFLIPqaXNh8zImdrZdGe3pDuzWzLoI5FmoaYOHzJrAAoNioCuYJ2+FpCSpcSo7woqA9RgttHXMJ0gtpSYgLezVXYFltlh15jL6roC'
        b'qT2rUWdymGGElBuBnSupgh1bydruEk2fO0ew87CMg0dZoBsIBjt+mbEOtc3x8LYKapY2BzcHlAc77IICWwIb0Jqg+sjVgcwuKIjZAgWuDSp0e09AehHzDBF/Tn0zPGaP'
        b'/lML3TXWG6zMy8w150Zmz1BmUHkV8YoYD1KHrkrePVXjHf5lgFmoFsjhwOaYM53Z5lUD/Rc9BRCCzYmOFCp5Fi0PqKNMzowI5fYaOSDQdLneWGG0Wb375eiGa5V890JI'
        b'9t0D11nHt/Qh9dv64Ake4+W57C/twsz4XGeqo2NW332h5IYieiATKnlRJaB+2AUGudVeajLoK2A8T1SLYEgiyKhQk1wHVUBY6L/cVA1kyKKSq23yKjtIKqUGn7XoHIMv'
        b'NdhWGOhZrzxabyjX2U02BXMvzPC/Fo5tMV4+1fEmL6PKwmjXEaObklHhrxbnlhrvhFarazGpN2O1RR4tGKwsI/ct9SB3+6vIYSI1nglZlCGBagQYcWCYaEOFSp6amBAn'
        b'T09M8FuN254eL59BA3IWoNWVG82wa6CP8jqDDjoWYzasoOedtWmqFFVijMJ7qp7A8lgmuEb8YmhExi9EkxGq0Zr6jytGduqaMpS0VZHWPHxhFmlRkzZNPL6NN5PNs6jV'
        b'aXaugrTG5SvxFrI9d3Y2vpidn5enzuMQ2YmPyqrJVnyHVfzPKbLxHXwCQrO0cZWZK5CdWiGSUzOCPCp2Vkq2kc25QFKhmUuqxyturJOh0DpW6zh14OQ/cXKEtNq4f42d'
        b'juyjITJ+2CB3365slTKG+svgS+KgCShtsdSKH5AjzD2N1fEoTJq9hBuAkFwbl5WyFtmpNS+5iE/UQtfqx3p1jrRAva1xtINbFfPcOobvWELwNXyV3DcuT0kWWeupkusv'
        b'fxvy01eDjinWJ8ia3jr97I27m9pvbxQF/iogPn5E/lF51NT0z1P6hG34y5ldTTNHNo7evKvRfH9Kx6S7r/Rb9cr00mP5vzk3vjL883N//vxIVq9Znw58U2d9Qbz9I92R'
        b'kEezB/120y9HffXXoy91FWnevlrXueLEq/2S90/45mis4u61YIWMWbqOHD4dt8a7+ZaEjxbxeF952VQbTBvC5wrwRdxa4L6KHBpIGjLIenH9mBTmQzZq1aAQfBS3wIQq'
        b'8pxuXn1xszgQnyLnbFTdNxyffQq3JsYWuK0cranfcHEIuWJntpf5meRBrDI6W8njO+QEkuKDvBI/DGL9ILfwZbwZOuJaLHKPHBCjSHxJRFoTh7AK4ueQK7EqBdkSh9JJ'
        b'J1RwgU8mz65lVsHkYQ3uwK3Uycy1OL3XSVFkrQg/wDfISRtl+PAFcp6coONlPFvLTEdPHeuLUAJpkqrMeLeN0u8Z+OZiyAv1xahoLtJGtsfSXHK8y2yVhOKb5CEbfVoU'
        b'vkEzMmUmtK0cg7dB03ifiDQtIS3CCM9MmOlq2MUsDsS3e0eKcat2lWAtGfw9veC6nWOYySntPVqHVks5KXN2kzpc3sLgSR3eAnmaIuXqezmJsctNJt/ZEWZuSre/ZTJ9'
        b'ZNHHFPqYipweOdNQz8bMgUKp7kqmuEqxSnz49nxIu0+BDq1HB4b6N2z17riHwTPn+GVGpbSHq9FSwdCey1dwXSEl3ZyEZYBrEt08myaYdFWlet3EXlDLZ7RGtxadaV86'
        b'MLujLicXEA0UQ6+sNpvqFJ1cl0hfXfZduhZc4uIufPXMkg2PPlDeooaXL4cJPRCK+OjAE7VcKbQcXuLJU/htvr+reUWPXMf37UhQiZOo++3CQFcXoqborAYXF/D9m3Qx'
        b'1f6aHOJqcqRfHuH7NR5Y4nSC89e2vLttv3zFd2y7UWhbVuIuPvhrf2T3in8LM+KnFx4OCMzfjm9GLn+77+J+8ISeVKJ8Y1lEDs9cfn/1XrLgP1dZ/gn65dafbX1bdhc/'
        b'JztkRBOPiX//KEHBMyzO4fZ6DywuRbiBPCOgcdF45g41hmzBlxgaR+WPI3JA4zPImZ683wJK6NZy93NaBz9j6yPckBnLIJTp/3hNA1yLspD2hXO6NK+Hn9d68HTzql8R'
        b'3BXg2KyCkb/UarMYDLauwJpqq43yz13iMqOtritAyFPXJa3VMbE0pAy4+OoqQVwV2XQVXZJq2AKWshC35aB4Pcy5JHPoaoe4xMxQ10UEYcJNEOVhDigIaZEBFMgACkIY'
        b'FMjYyoeslRW6vTuEzUoQNl+X+BA2s/R6K0gTlCXWG0rppoT/ZQ5bObmBWfY/gbzJpCEmyujklfYKg5uEBzNkNYKEJBfcH6iwZjXYVPICAHqveih2qKInNMaqmmoLFUyd'
        b'xcp0ZpB2aFGQlCyGMpupTl5aRwt4VaKr1RlNOtokEw6opaVVRUdqpLo22HqOKh0CFq3Tqw6o2m41mitYj1zVyGPY4sU8wYzMcIy2kmpJvPvulT/aprNUQBt6J5qi5eVU'
        b'e2ilwop1uZ3ObqlFV7bMYLMqxj+5DkCA2/HyLA9qI1/EzkuX+CtGWx4vZ94Oi77V58FvLcI2GS8vZH/lixwWeH7zO7fTeDnVfcJSMdl0kbsFnt+ydAOCVAtP+aICi81/'
        b'PmGLQlbhhbURJ1cXFiiTE9PS5IuovtNvaWFfg7yaVaRUT5MvchwiLold5O7R4b/xbnRAJXAhIKcVudsR+y0OCAQmsxK2BmxXa5nFWGNzEDcKp9RDnO2tLJO1GuDXoPep'
        b'PABworkpKTKxK4bYYqvk0wQNAtuiIwptuqoq6hhnHuFXl8A2AwAWdKDGsbX0RnbJkQ6mdYURSJ5hJay4Y8N510P/5VfbDMI2YZvfYKus1gMmqbBXAaBBX3TLYAPCpjHA'
        b'7JQZ5NVA+33WIwyJbhqmGrEKwzRa3bqkks8ApOZESD5rcd92VJECoE6vcCozwYCF25usBt8ltY4LnKrLWM+F45UJlTZbjXV8fPyKFSuEizZUekO83mwyrKyuihfY0Hhd'
        b'TU28ERZ/parSVmUaGe+sIj4xISE5KSkxflpiRkJiSkpCSkZySmJCanryuInakm9RW1CK6O1lGJlvp6S7ihyebM1V5ChV+dS3LxZ3xqFaJRpVKKkkp/FedncMPpBSkgx/'
        b'E/HDtSiRNBQz6f9NmRjdXtkPocnaOOvINGSnzMl48gi3aZyi2mzSQu9OyVHOoc7Xc+hlPNvnkxb6ZwA+DrQf78KXg8gecgHvZpYtK4ePINdBEKbCYgCSkAM8uYNvy0KW'
        b'2ikLMS6NPEuuq+gNHrIB1B8XKqdXs/BoGD4lJncD+jKlC96I95M75DoI3XlzyY6aXBHnMb5ZpIU6Zm/VzK2BR0FuDtkjRsCdbAwhJ/HGUrvglT2VHA5RKXLwfXwkGAXl'
        b'8OSwmhxJNbFUcjaGNJHraijOIRHex+HN6Xg9OdmXdXMBacSHQkhLvIpsllug0TjcmQPCdQuH5DMlYrxdz67HWRAbRq7Hx3AoajKfzaWRw3gPm9fpMC8/VUYxrUraqmJk'
        b'p+ZD+Dg+SDqsoTBXN1mz5NEwFLiYn8nhk6zRDHyfnKTpoaE8blKRneRmLrkaS3aJUP86Eb6QtNJOGR7SWERaQlRqvInchi615anprIhQX3JHHD4ftxvfeb1SuKBn1Y5U'
        b'5c/zgnFChOTNdOOv3vj1n3f/eUJL7OU3+0rFr2f/csm9q8HWYONzDV/yqv5Jrdv7D01OXKD7jeR6R8KUU81vb9BdVp0SxS2oSrL+LvJntbe/fGvlio/ybu3/o2KMSZr2'
        b'1M+M+SFdL+8qv3F89EVj12sv1/5zwfmX/1m75u7rp9Pbtqz7Q8ILr86/p3j95/0m/Tjq/CLcMrfxmwnH6v+Dcn4VWxeToZDaqDUVPrmGXHGoaC4vddPSlJOOUBvVZ1Gl'
        b'0j0XNHqoK2KTJVXjyfaleDNT1CzHN+NDqNrr8qrHFDXkENnFmgsbQs4+xuRSBjdvBmmKKGYao5Jgci42X5nFq9V5mjjSpuBQP3JfnFRcy5QwUnzaqomLzoYucCgQn+cT'
        b'S+vwgVUeV4aEfd8Lffw61Abr9PoSgXtjzPMYJ/OcLeNkXCDXjz3df8TsHpJArr63i/ntrsOh5AgVNBDFyGnjRm8WsSymjyX08TR9lNCHlj509FGKPHQevl2DQ4Q6uyvR'
        b'upoodTUR6mpR52qHMfd6WoUHc//7Mf6Ze1/jUwR1yfTUBNDBLHWFCiywMyjVVbG/9A4WQ1eQ49y3zNAVQhkWYBOpVZjQI9egy4LdsDFV1UQ4sfE8yuEHe/D4YcDlhzv4'
        b'/AjK55dHOLj8YMblhwCXH8y4/BDG2QevDSl0e3c7Utoe0DOXr3NZ98mFy5qegJedTh0jhNxyIKgwb8CmApOgc7+0kDIScfIKS7W9BlKBf9Z5E6jqqlKjWedkWWKAm4lh'
        b'tFYgtVQz4LIEpR10CcteNVHh+f+KJf9/Fkvct9t4ulBCjEsn9i3iicf+FMoLUc4KfPJoi77FOtRvc8L+F9pxbHlHnMDmmqupjsfCGFmzb/Z0RTXlI41VOpMfRnhRD/ax'
        b'IF74tpD122OKqYT+llZXL6P9pTEqeZ4DunQsLK8uXQoLD0K/72NGMxWLMtISEh1qMwoIINPR6hZ128767YQLUY6Xz7XadSYT2xkAOLXVxjLXblzkZnrbo2ToQLSey8Cc'
        b'8ha5m+d+q+xGiz8mv3kYgf4fIH5NMawwVDhMeP6vCPZ/gAiWnJaQlJGRkJyckpyanJaWmuhTBKP/epbLJD7lMrlwnDx6Drtpr6YhR2v6wjgD2eldVQPWpWnUeWRLnJrx'
        b'tMDd3qdSlpdwBRLEOvwgKGV1kp16IYyiF1Y+Lle1kquy1CA7NbTBTTLSoFHl5AFjy2omZ4vj/VWMW0lrED4jJhfs9EyKHKgnJ6wFeQWO+5FoC/PJDsi+nbSAhBUMEkk+'
        b'ORkHSS3kTuFifAgfxCeC6LVXe0Py8WFy0U6Z6+rS8dactTrSps4r0NCrlRLEaMAUETDkTfiucH/jdnyJ7LTG0Pt/T+KWaMrIgxxzMZpDwyokEnr7FpNwppMWfCCEPIu3'
        b'zQkkbcp8EL4mk5M8ikwW4WOr8UE7ZYBnDHsK5qP7oFuNN+CdcWp8cw69yTQRt0pWDsQPWc9SCgdbc1i/1HEKGOStPhLUh5wQkXvk9Fi2VH8LZxffrswK1creq5mPhJtV'
        b'm4eT7SFSvBUmqQgVBeNT9hQafY1cTg0h26rHwfxsBint2WyQP9tggW5SmbQVn4dQLtmWTYWyxVGBM0njGiYt4iOkPZhcRyAGbkBIjdRjh9spG0lOB/ZORuEDQDpHiTLy'
        b'iAnsY9KXkXZRMNmEUDyKJyfTTP/85ptvfh0qZtfunsjX5uoXhQtn+DGF7Cpfeflwbe5dw2pkn0Ebu4hP4Q46OW0OMT47bh6sX1t8zlwAh2yytTBaAUCR7bqNWYFvwdTh'
        b'y2SnFEnNoUsASk6ym2fIOailgQ8qJHuSc0SIIxcQubAK7xCsGM7gK+RuiGOZ5ghgI02jgBNIYemxGQIA2CVGuHlu0ML5g9ilgBUL14rJ0W6xeHY02VMYGOoh/k7qKw3D'
        b'HUY7PeseGIxbrTnKgrx4Cj75ZFedQ/5VkP0SfGPgALZfcsiJUnw4OVa4MEchBTnyEQ/wconcZBcP13D5/A+lIMCv0PV+dQBR7XBYPhwjjQPJdYfGgxo8TMed2RTCyOb4'
        b'grzZ0Y763C0fQOo/IyM7svAZdn3vDLxvYKxKHRfDgbS4nU9aHT99GLvX2g4b+KiGSo60PsRbuAx8i+xUiFixSQNhrN3F8gbGL1rCLvLFB1SVrBTegZ9lpcieWDZGspce'
        b'v2iXPD5IBX5kPBfWylsngRi1453LS3Y8lS9KjGiqMFWndaz7eldcY+yswpNvhqUM1k47eaHx5chTk/8gTW+Y1mt2oal42+Tn78z5a9oftvwo+S8/O/P+1T03zjekSgp3'
        b'nh7/61E12oy4CSfwnvRBI2e0KyRry/ImbF4y41dfjxw2efxNpTFrjPzfZ4f8eujSLeMXpLer7m4bP0RauLbytOrTF3PvFX4xZ+TIqWm2jncmfzF50If9i75+EdXfPnnm'
        b'0tbSgC7xpcNbv1h8NXdCdeeEyo/u5OuvVYx7aeeoM7/7dP3fk98YUz3+x5ZLp2dv2GnfcOGv237StO3Y6Vnmw/OkFZ9NXZi1//X6kRPG3j4xZNIbL13Q3a+7sefzfkXV'
        b'r856I+/9qvw9ZGj+ey+E/m3Ec5/YX9n3k38Y8i9Zxr+3dkbTirztr/MPG74ZNPfvv7mYfemRSRL/hysn9z/9zvx//HSUreD3H4X/Y5bl8p9XKULZ7VhLV6/GrfHWsZ6m'
        b'JOW56UxHUUquL/NUUeArejctBeyChyvYKRvuACTQFOJmS7KSbHJoKVLIBaaCWEuurdSo8ki7y3IHhc8TmWbjdpa8gDxaFxsjGIKgoIX4NNnIw1Z/RBqEe7z2BhfFqiiq'
        b'j6OQtI0nG/A+JcKPbBTKohViTW6MFF/F7YhfwqXjRrKF3WXZf2xeEr6Nz+fmxQEmBGC7xuNb7LYx/GwceQR0wWn+IV3Nx04ZG1Bkoxh9Yv/xgo0IBtL0uJ2IVRJKNi1k'
        b'J4fzyD5yjV6keWGxtw2IGLdqFGx6SAe5XmOlW0tJSRadZyk+i3qRHSJ8ZfFi4bLF9iByxF0Hg69P5+ueIm09XLaliPgv6WR8aWfCqOahWxBnGpoiyhysYz+8zKGf6dbS'
        b'0NuXBR0NC/HULGUopPbhpMw4hRqqCPelRUI4jJmuBPPs/rT+HvqO7lYdOh2ZoFcx0Ec5fVTQB7300WKkj6UuXYsvdU7Ak1zfHCzUWe6q2OCqaamrnVBXE92KHXodfrGH'
        b'YudsjH/Fjr+Blknc2C96qO5517ukOaAZsaNVrjmYqWNCmsWuu94lLdIGtEZaH7lawtQvUqZykayVFrq9+ztqp40NQ4/zemECr7fGRhmImoVipM09OXcdKmKxTdGUA9yf'
        b'EzJZm/u3IQnCjfB9yf0xVtwWuFyERGEc2WjIwPvJcfa9gbX43LhC3FZE2ubmzSY3Z5Gbc0PTEhIA6LeS20P6i/CGgWkO1B+bX0jaimrwo9QEsiUFWK3A5Rw5KsIn2HcS'
        b'RpFnyH1HTXgzPg5kShLD4YNhSwVOpGkYPkqvdSd7ItAENIE8msSIEL5cmE5OkFP0TvrrM8egAX3wLka76jRFGlVCShLeQnal8ki6lsPPlONGQc++v3ZNrOPydHK+yHl/'
        b'+pgo46m+nWLre5ClfO+e6QWZ+eJE2c131O9d/4EqcsrkqT/JOlvZ+eGFJcYdk01V81+5/W6g+oVeGahv39EvPHfgcN9rXx364m+msZuigqMXlO3860DZ6SuPrpunTX/h'
        b'6IaGX/1kxtGYbXO50UG/3fZ32b8Dsk7Hznr3R3sMPx6w7+DeroFB724rey4oKuytr/9gTXh71IL3q8jo3M9vRNb/J+Haz1d1db3z1St1GZZBr9nf/qh/+zvp81/4xdZH'
        b'a631r/112KuL/v5OVe3R2aUTr4/6WaOkV8w7qsv7Vph/fKH4fvOZkLzrz+6zffrwnVdDv6hTft26+ueiyzkrG9d+EXD0lVkvrshURDounSYnyXr28YIAtHwUj49zc8mh'
        b'LMGIDz9Lzndj2Uoxvkbu4WuOazml+KYHop2Oj/Bjyd45zB4P7x4MWQWDvEG40RvX5pBrwqX3LTV4N9Wp4wZ8x5NerSXnWFNjF5ILGuDXLgUC97c9Hp8TozD8UFSSYmEo'
        b'VoMv49ukVcPuuxcP5ciZOHycXMWtrLA4iRzuvq+bEg0Rohd2958saNDxNnI7VqVQZ+Z4XJnfu4z1Lg0fS9Mwg8scfNNlc9kPXxQPwvuVjFiAvHCINGseM6aMXCqyQx8u'
        b'gPTRxCakfhzp8KC60gq1B9G14u1M6788C5+lNrGkdXqmwzhSisKHip7GD/F+4R7gTRnrNColvkOuetDccbiB0cAw8jBbIDkcPuHQ/Nf1J+0scVJ2jecN/0eG4KuT8Xo2'
        b'lUk6fNxxwfBy0uC8qxM3igRano2PUd6ObCsA1ngPvYsV7+CrScfcJ8PF/6++HeC0yhG+FMDIVnk32YqnRInZSTJrSTElWTwPfwUSJqMYm/2IGSETDhxoSLCtDHSlu37e'
        b'Eg8X82F8P54SN3erHKEDAgEL6CYdXQGCktraJbHadBZblwjyfVdqJbHQj+pYzC6iVO2iTIwo0ctlL1KiNMJJlNaj3/j/DIF3t/8XDL1EzB5S/OUfvXQPglOXzelK4tDh'
        b'mhyqFYvBZreYWVqVXEePCNw0NU+kXpcvM9RZoZ4ai8FKTSoFFZBDp2V16fUd+iBfavHHVf4mQZFGu1NaZzP4UFl50Fip+wS6meczSVFNGhaBULoXbyfnyTYga1fJLnxt'
        b'PrU6x+dn4xYJGoDXi1bh3eSm8PGSQ/gk2Y0vqEk7rLUKqcRR7JyVNPchxxkFxq3zlWSvRqUSoT6kE0jiZhHunILPMOL9/gSmE0AJtRvLDs0zIaZ1IM1ryCEoS1G8UF46'
        b'guwpxQ8g4ngSikmVZJD9Wia4jVob6SbQ4bN4b3xkFqPOhjC82UnmKWEm5wxAm/FecodRYWDeTz+tEZUzBpcJfNtzGeeA92SsBapPbpbRcjxu4wbjywbj29NHS6yNkP4/'
        b'z/8r76fDw3iQ9d76orxYG7pLH/9c0I7AlAU17aPvhU16Z/7yTWlvHU05yX/R8U1HrwV3jl55e+sLf92/VvXcjr7Tt475+bljpy8FNF6K+8jW+XbNU2/drK746P2bhxXX'
        b'xmpGbtz7TegvbkXNvlYVu+gva58qyn99ycHM5ZveD3/jky+fX04+/YrPHzL6X/sPK6QCJ7/Bhre4HbUmD3EetpImcnQpw43p+Gqq4zpidhcxLNypkbBop5io0h9fqYy1'
        b'4/2qPB6GepbTRONz7AJtsjmc3MWtsPr744VPgfAoxMCTo7PJVQf9mF3kw9g8HR9jssZg0iog/ZOmANkg+nEXDzqF9+KdCum3oBU/Fo46awndcgyXjujGpSaxKFJg6uEv'
        b'xYz02Fb2H6lkAO+GUByF87/V/NECj3cfw1nPPJEBpKOJTq5LXKOzVfq/030KctySTQ8x6cchpK573cVPdK+7w0zxLRHn4wCzG41RjGLV1dI3k8kdoT25VxwdyHi5ulwe'
        b'Q99i5ICVrYKqnKIqw0rqc0s1xzGqemNNTBxryIEzLb4Vz1Z6saDepe7WWcoqjbUGlbyAaudXGK0GF15kdbABsOw6eXm1CWjCtyA5uohBXkgu0PGNjNt4e2Us4LSN2bBt'
        b'ZmUDs5KTl4s7i7LxRdISpwIWIptsCqgx4FY7ddMFvHF7jWYEOQrbLCdPRTYDN1cEGKQ1fjawK8poeruMhtwKwHuHLmSsPDm8VkLa8aVwfJ6pEEQmDm9cXcc0njGF5G4s'
        b'eUAOASCsRCtxUx1DpH0B13bGFgBMiSvnIHKQbCg1/mwMEVlvQeJtfetT777clkm/A7VpXaZi1tOFY/O5Q9xyTtpYdOusSBS5O3HhB2+Hbt6puNPn/eeMo999/uthR55f'
        b'HKE2HV/1uXbmkKfU18rrq2LHdOkK9616tmX6lPW/y8hpKav49efHZRWSw0Hv9hoblHno/EFRwDuKvc88UOfe/k19Xu/A/zn9TfJP/v6Pi+veqxv51av/PqZ87f1+pU+N'
        b'rZ3+wuW5V/7wo1ORqesaG37z4dZfTRp0442bv/rs0I6+zaIfvxcwHY1fMvmGIlxQblwkD3BLLD4dQmcbNkE6hy/hxhUMPxXPK6J+Qew7cpQzu5pAWvk1T+FbDH1Y8Lmh'
        b'5Dq5sUKpWifYmgThMzw+QR5wghhwZjjMMC2/GZh9aT5fQZ4d3HcA40hF+D5ICa2QoiLXMtQsRwi5wpP7BWST8NWc/bCGezRxeFvB6lrgWVUcCpnME4jNE749snn6clpB'
        b'fIGSimO8eVHMlCqGHlOAb96hwRehgTaNQkW2s4GFJ4gqNDFszOXzx3tg3Qdk00jSSBpYz8hO3CyOHYs3xtMjCqVKwQNWPCLCTeQMuWBjROjoihzGm8fnS5B0Aq8Y2x+R'
        b'04ydHQM89jWNC06DFkn78IB0d+E7wocNLmsw0yQ5pmQKH8kNwE1mVnbYarKXtEooULp9K4ucJcfZbIYAij4TyzoFreKzfF7fOHxY0pPO51twuBveFtMd7GlZQ3+CBK1N'
        b'IHMbkgF769TCREBsfagLq9LSAtbudHznwIY89Cr+O9nJC3m7b7evhcc3jyH3hn49fPfAoxsKh7/2dET9+11O0IBcHP8UEuEPD7+9H7vpilro66vLSkqYL1JXYI2lusZg'
        b'sdU9iR8UNclnpjtMzcPYakan2HgE1r7Pf10H1+OqWuhZzTvIIdUE8mJxMCf9Rkzn7ps+o2E2Of5rqeg7/hWHiQAAHLX0iweg+EYsQt8Mnj0wPWxQIMf0ITayj3RYYX8V'
        b'wgayhoWJUOgQnhzLq2HGmuUDU0LwWRtFKiH06GUWPkoe0BOrwUnikVWG/y+/0+R9cBmQz86ebPjsMuoxMxzvK0PDyem+jPtUBqdpVPhKQmoUfgiFyS1uOTmwnJk2luNG'
        b'cprpgPDZSrdv6JHteJMjww4qgwMnnhdHma1kMeDTVj4H7yNHjPXTFBIrhdjy5Zc/1i7+wZUdx9oTm5ZzZQHv8KebZCFRmQc6suLe63O6z3tNudo0TXDIgt3HXjzdkNh0'
        b'rOHYHvUublRv9pGMpZN6FT8bpZAwNLUiQSp4S/bB+5DgLYn3TmG4NQ/Q6MNukV2P9wi4Zj05z3DNxOULHRr0EeSAoERX4nvjBe1zJ9k+EUR28kwEldqdEnvKUJaaPJk0'
        b'atT4IT6d50hcwhvIMfyoJ78YGUhbwMoYSqi1A8NC/dyx0CiqAaZYRwxPyyrXdhJ3iWmBLqnDX83r01D0EjrLatd2oCWH8073yPWOn7f8843sjg98Z6EiNjpHmR2Xg9vi'
        b'1Rn4CjuulZO9kj51M7xAqq/jr/Vv7nd8xNJ7LgBueb2oMahYZBCzr+wh+n29Nr5YAuFAFg5iYSmEg1k4hIUDICxj4VAWDoRwGAuHs3AQhCNYuBcLB0NrAdBapL43/UKf'
        b'Pg72DKfvq+8Hbcscaf31A+idHnolSxuoHwRpYXoVpEqZV45YP1g/BOLoTRxcsxhKDNPL6f0bu4N387tF5aLd4t0S+qOPKuchjv4Vuf4KscJTLORwe4off9cPPxQOdQV3'
        b'1/N4Gf0I77jv99SPPNRbP+oQX9zLEGnopR8dhY72PoYaOBYa4wyxHH2YPaPgrxQIcxLguHWkL7N0DGDzJNEr9DEQ108f5bhrJKgECJJuBjDHzMncS13vKWIINpNS9g1F'
        b'qUtJL/n+Snr6z9sfLlhQ0v98NqAd8Qpm7h42d4Bwej5p1FY0oK8hAM3Smn8bEi1Efla6hvun9JIUJegGbZSpkJ1evhhFHhk9fOtz858GpNEtZAI+aQ1AhRWBETp8ndWz'
        b'LGAEmpa7n34wmZ8aEIDed/aR+RMa7WVf8Vba/1UFV4dsvRq6PkEmfmPbVK341tGfDpVNLts8YomW53f9fmDze38uqX+w8yVpSL9FBe8Gtf3xjacH7A7e9vzPpi+tbY5c'
        b'OnHhqV9Ol5YElDX9qPn9P0zLfOcXWQEVv7rxxf/Mvlp6d9LZe1G1C5MVQYxxHGGeLHweiFwXKUUosIi3hSkY2htLjpBdIFdfZtpp6YohY/leY0GkZjrlhol4p3Bsic9a'
        b'PYyrQ3EzU8fWkVNkPfNh9xC8hTkZHSWpnET2CuL5foSbBWf12GhyZJxSyAe5+g8WT4Ck3SzbOnKXGWuzrppwG9N2A7ruRTpE+Bi5i3cIPvy3ySmTI9vWwTRbHr6AINce'
        b'ET6Bz+aw7uPmCnwet8YD06rGZ3E72cqhQLKFx43U0cBG70EyGNfi1hVQi034bnQb3l4AFGJzAdmmkqJxGim+QVU0+ILjpO2Juctuv/Sh7mg9ScoFSwK5Acw/3aFp5eoj'
        b'Xbvnse9GCnrRLgkzeeoSU4vZLln3qZi5uivIaK6x29htYN2cp7tdusSykb6vp48G5GQ6N3j0M96LQLzSA+/po7ffxfNXUkKH4dftNot3bBP3dlze54O7Lzb1cr5VWTQU'
        b'9XwHR+DQEve59Nulac4ufTnUrXlvx3PVd2k7uKR75fw1PNPV8BC1M7PTdPM7t1vu9PqmwFRSZfTveZ3jarYfFTPk5Zbqqu/eXoVne7qVftvLc7XXh7VHDXu/5+ikJbZq'
        b'm87kt6lZrqaiimhGpwGw3/b+e07cPplxHnl/75CRkAMVfNFnPH3T5jZNXOL4/HqBNLIRsWtbZIPLSpAx59/XkJVe8qE//5B+xDdbt1sf/d6/39foZOUfaD9Af+uIKtz/'
        b'wyj2eV7ts5KPz7YqOHYpSHCqb7w3ijzbjfr2ynFDDywsk/4YiqN+zy4UN4/yrPW93JHEk/t3F3phoss9qDi9G/nwG/j3vyRNeX0G3lm9zwVMAHEIWPLoysD1pgUxt0rZ'
        b'JFVtGVLGAPiHv+ZW/NI48qkpnJV+/DQoa6zwDeYd+gU/2I/34xs7OkU/fVZHPyX5WQH9mOTSLumRlbkKnlEtfIMcGPr4+o0iFx8jXXs1YxiJt04Kp0qjGHI8Qqmiks1G'
        b'kIpOS3uSTsJLmGmzsd5QUmqqLlvW/VE/5zIvro9ym33P3B6fsJUwm1xvQWUX8tCA7ITHAq/VP9fD6vtv32MHOwGAzYTjk7YiAAHRf0Og5pDvkysGArFR/+A+EVVODJ+l'
        b'XfcCjJ0pWwtAlryNz4vpJ53rUT1pWSGcWh1VkcP4PI8seANahVaR+xns5CmWPOzvwX3Sb6BG5ys5lIKpjeUWaRjZMJ9ZiX42hlqJ3l5N+dy6IZMRs3jcNpVZPK6cpa7q'
        b'/eqCjowSwdsTH0pFzluo3MwesykAkfUZFIY8rnk6Rg4Ek4P4DjnDsCezRqkhV2AsrWpBtMf3cItDvO+TbbSc3y62ttDhVt4b/TOqJR4g0mZun9J/3q8zE+aV6t6V/jTu'
        b'gyMv/vpkabDmJxHLt7x7epTtun6dBff94i+Der2VcOCH31xq2TOlAitGTC3SDRg5LfNPLxwonafKzf2o84dh9nubRx786+XfFr0x7o/Dru99fd3Fawr5wZfm/aNpUb9l'
        b'ib9+4zV1ycpNP5K093rt5XVr37gw4mzoXkUA0zdKg60adwVpEllPdaT4nIbpQYNJG94dopk73+vWJxO5b6M7dX4+Pt0jx5gYDRtPHMO4VP3K7JAYB0vsqG4tvkWdXq+L'
        b'yeW5C9hmVqnxM8zAY3o0ZYhhlfEFkLqdlYIwgs9JB+PrZAtTNlRAVQ47OHIJtzusEsiD2cJHQmvGOywL1KPxBqdhwalMhesD437VodKSFRaj4+uuHjxrCTVa47mhwLMO'
        b'dBizybj6CLfdxwp6frdaZ6mw+uFIectuz63fDo/FXlv/dA+f+PRqPL9M7LYrPc6THR8qZl56rg8Vi9mBlgQ2vZhtegnb6OK1kkK3956kTYnXppfmC8ZUB0FguQPCxjl8'
        b'TURNx4YlLGEyseB//IDsXkUap8bOVs5TUnuTgF78UNxCmoyTn/oYWeltmXzDAaoO24F/99xrz13Zcaf9TsOdBXFNiv3Dm+40dDaMa1NvHb5/Q/KigFB0YXDgogIFkHRq'
        b'IZ0QWwSyjpq0l+CL0RhAh5mfcGhQpRgauIzPOheoZ624tIT5bjAwiHAHA1MYM/rwmHuWVdCBS92s/9jHp5kiyhPrd4qF2MdyMiDYAw+jFxAc6OHbv14d8Q8DVFndLAEo'
        b'kDIdBoWEgO8BCT45AG+9gyRfWHB27nYnk1wppIu9l0Micm/yCC4PP7Pa+PH58zxThiz6z8aPtRpdtCH6bbXAtWk/1hrLY/Z+rP1Qu+znPyr/RP+xlt+SkJZsv3YqwX6l'
        b'9sqpxM2J4uSacoRsj2T/fruxm899IuMYj++QU12i24L3cV9wS6Bg/0MNUPu6zXV3GaGqvf7Bap9reffDo9predsH+F9e301+SE8b/C/0ZGGzSxzbXfLfWmTv7e5cZIp1'
        b'V5C2jEJlP/JwHtmTnC1CkgAOb0zCm41/IH/mrPQChhmc+GOtGlb50jphnbN1H2lVug+0n8Baf6KN0FWW55ZFlgWWv5krQmc1AV9qfwnbmmpuFj1NmqjxNsK7gW+jxtu7'
        b'yIEn/8xwV1iJ46pVt2X24Nfr6TLXD3CbbY8CTr2H557tkpbrymzVFj8oXmzp8LfPD9L58gKE1j7+AcFv1xThgilyt2UyNUruCu0W6pcZ6rpCa6vtZZUGCyuS6BlM6gop'
        b'o7fVGOiHYxPdA0ldgXqjVbhmhho4d0lqdTZ6W7HBbgNRlt6oS3dvl8ywsqxSR+97hShFIDt3s1AOy5JJH+xYjo60+15kegJXzGqk5lWJXcHO62SMejc3/EUsh81oMxm6'
        b'Aul3R2jmrhD65nRoZ9Hs3ipWU5LlOC0TQH0qS6tXMh/8LklNZbXZ0CUq163skhiqdEZTl9gI5bpEpcYyBd8VkDV1asHc/KIu8dSCOdMt12jT19FjWhS6pHSdKdNnpV5G'
        b'jpuTpczqmmsOLA/8Hrx0+eP7TORownOflQm89Me91nD/5FHl0WTdqr8Xyh3I9ShujLIa8V5yKxygiyenuZgM3MSsrQL7481WWy25hc+QPeHkZgiHAshBPmxkip2ukX5F'
        b'XCw1+bwYnZ2nUi8j1/Nmk5Z8fDGObI/PmZ0dlxMPXDGwboJ7lBSR9kWyqaQVn2Dc+nhydylpN0pnw3s9yiMbyTEWP3cG7khOSegdL0bcWARMwL6xguX1brKLnE3m8cV6'
        b'hJJR8hp8X+D6N+AtNigQsggAPhqy5S5inSeN05cyI9cZCVSlyqGQYp5cIutJEys2wiyHQmTnNCniFAjvwccGs2L48ES8XrDgTSV38R36IfirHGmv6MPmUJwRi4oQqnyt'
        b'l3bK/EK1Yw73QTcvQ3UL8G7YczEIZvMaaWHHQHGh5KhGpVRRB8I8JTCkNwJyOdQfnxRPno2bWJ27FcMRIN3sijrt4A+DExHjgbLxpULWQXxXhLg4hPeXTBLGdWKNOZbe'
        b'r6JmB2VP4VYUjttEpVMWsMomWvuhOCj+1mjtBG2uQqgMCOcwqAzfItcCEKdE+EBAOsO6E/EValtwEWZ/G/uckjiOw3cHx7Oqfj1+IlqN0IDhGdo5NYMXCDb48fh2r+QU'
        b'KPYInwbZTUXNaC4LSYPM5A41CssDySqItPOJPN7PF7Kq+szXIOBYo/8TqV26NyNGQPn4wRJyjNX1gByC1Y6nTj638Fk2zEWkIUkwgFOTw2QPNV3YxI+Efu5nFc5XMne+'
        b'yvdztHGdpUXCOuAmmN+tySlp5ADIfXTS9pCbuJmtwwAF6dDQi2hayTZmno1byT0UhhtFE9NxC6tzkz0D1cDUlZq1kduNBsTgpIycXQ411oTxbLD7SvERu3CjX+doob58'
        b'QWt/Eu9nYDYQ7xbjLbhjBJsTcm4+uQPl5eS+lI1wP2kmHWyEwdwSRwVsIWHsh1BYjShjuHDD0L70SARYL2ODRDthCJ8l9AYEm/Wjk5MSMiqkbHx7ZekC1D7EO7KdUNsQ'
        b'zAPQXuPIbnJXytY/B3esTE5NyCa7YFqSoNhAmGW6BCn4BG6I1VDb7lJ8j0NSIx8FGOG80PcT+Cg5n5yeMAoDZ8llQOfx4UjW3jp8ZCADQnLJrCZbAAKQbIIogpxIEUpe'
        b'xFemQEGo/SDM23gAklByUODe75Bb+Rp2zDF4AaCGc2IkixD1nbiMDbpmYSDT+FRXaWWjq6cgZg6aClv/meT0FHILxkIrO4DvjWSVzSbt5AT0g3pOasiePgAlZfwgDppi'
        b'9jaHSRPpgIJ4fwiAVyb0ooicEwxFdz49Q6PBF6jhBV/NTSan8EZhp2yuyYYSBurJwU0AgCSbswTYurMkXEPx2VayFV8xwVT15oOmDmK9/qVlFfo7QhHtg7W1P69VCbuB'
        b'XNGSq/h6Qsp4fEeCuCkIH1lNzgtuoftgjm+R1rwluTn0YEZEHnK4IzCdVcbNn4G2IqTdFa/NeS25SKgsGt9LpXWBZLQf0MFUhI+uwvsYSNSFki0asiU3MkOK+Ke5+EV4'
        b'q7BD5kWhBMDhf9NqB78+N0bYIYuH4+0a2Ca31dQaSCzm8BHSjHcITrs7yA7cQNol1KFGhVST0u1UzZmEb6Qyv4s52SBMK+cJFnKkJY9c18YBDkJoZmTAoEKyQbiqaVsB'
        b'OejynaWS9UE12c/DRrw0tPvu7NRqEaWICa8grSmtNkHQ6uAbaSBktUvTCAizcSguz8Su5SbnyXbcrnE/GpuHOzVkO1AaMRqNz0ns5WPY4IrDSkjrbOrVQ46RTYDLIrkl'
        b'/chplgYSBG7UFJE2GPxOAAZyABaovpA5VwOUHqFI2ukCjg/B4mwT+j+6QGIMJ9uFme6Lb5OOEGkK3W/wn3SqmF9tAL6qjoVJySPbspU5QODujKFiY6IYjSmSJJFHBWzM'
        b'AfqBCEquNA7WLv5ZcKYA2olZaaQjgHSSNqjzEfwne8kBhl/C+pOjHpXexVtZrTwaM1eSHA2LRiuQ4Uu4TTNbWdRXKrgXPzDgewySh5CWhEIx3gREuQ3o+ipu8LR1rAgQ'
        b'wX2hmrmkLTOfTsQpRG7kThO8zNfjO2QHdbJ/UOzys2fTMAy3isktctMg7J7mtWQT6QgtS4Ne34f/ZCMv2DxsW8f2tkqdD8XUGaRDmSRGg/BBsSmA7GFlVfgIrHKHCJ9e'
        b'SCkA/E8YyCAnK6TUregYfEKZxEPRDnFVspQ5e0+g3l6taMp8EHKRUSphDurkaiVp1MC6ObuKN4xF4b1FS8le3CKA1SNLGG4XwQxuZ6qE4jls0fCxPviCgMLoIWq8euFY'
        b'Zp8xGN8U0+vQilnhpGGTSAfgUmgf34P/w1QCltgG1V0nrTxuxRsQWoaWFQQwhJSnWaNRKtX4QjQ5HZRD91jvySKyOyCW1ZaBHwIVki2ZQ4Ed/q8xMWQaVEnWa7pvmyfX'
        b'45gLDe4YxRpLm7jaGhqKT80CjATbjVwkt5cyiNqZHIwgwwLRUG1uoWSUQCHw6VRKU0TkMAb5oRpVL81h1lPSZHwfCH327JnUv36rpkDJuicfJCZXBgFCo/IHGTyaexk2'
        b'6aepGvPrKxWTrYhNfNG6tfi8GG/LpoxafZDMeCDieWT9N7C3X899ecmvXjL3zoqQvvnRM88vj3y1d++tzYev/CVzw6gBvO6NoH+Xh43eYeqzcO/2d0L6zTmy4/neuY/4'
        b'cDLy08FfFf5564zBcfcedl5SzN8XlPnDc+f/Pfe3D1oeDA/dHTSnyngy93d/jdzSqZ665+zaZW9e/0XWwFE/Pid9Zt38oKt//ujqR9+k6Qa+Xfj2Ds28n1xWnMj7wR8H'
        b'HMg/3esXP/zh9d+2396Ynrf8NzGXxm2e9p7cPnbRtPeGLzqcMu1W1sH80p1/2jEkv3bLJxs/qb02U1997G8Td0peXDs2YFrYlLTMCaMst19+q9fOE03jX5i2bWp+xjiF'
        b'5dys92+8eGDjob7jAsb95d2NL05/cfTY1hH7hs+/UPF+37bf/GjYO7otmsQDv4ru+Kpk6o/2AbK7/fXUF3bvrfv9uZ1fqw9cfvldY8XA9PGvfP6juwUNC59+yRwxJ+s1'
        b'W2ove9Bfcflrl35wbsepCSe6Pu91+Y9Rcxva3jr/+6fCr69a9HrYnT3Sf14affCy+mb1/Qm/fRD68JlK05R/HJl3ceP2f22yPTx4uEp+/YvWRasLTVWlZ3v/VTnOOsh6'
        b'e2T75n9eevHB5k//o47/cPCkF9Pah+U0zWwK3j76G/Xa/+k1qW/dXk3bkdYLr750a8ZXU97e96/3pn/10aOqs39dtjP9XweejXz0zhfzPgvY99nsT3rn3/zlx+9f7nVt'
        b'z5SSifaPNj89Ku9P418Zv+fRV6KY8P9U/fQDRW/mxjy3BhCTu8fAolUepgu43SyYC+8gB8mW2Hwl3koeUQ+Mg1weuUw6mHzexzCItK7Oo6KDFImncfgBac5k5gcLJ8Tg'
        b'1vAamYXcwG3htXXkSmiQFPXBR0TVpDOZKYj7YhAAQnBnXLZdCZjotqBw7kXuioCt3Y+vseaT5wPb1do7yMNEFu8cyOx+S+H1OG6Nd9jIBgIn9iw5AXubHJ/P9MWLVw9k'
        b'2mVBGRhI9g/N4/V4PT5iozZ/WcY62E15KTCqWi5LSTpZiwMHk70OWzj8DO+whVtKjgoWzsdXVuPz5Iyp22kcHwUxhqZxeBPZ7TAmwddX8kg6lu/1lKBbx4eya9xc4PH1'
        b'fNcXFS5EMdsPLYyvUzDqwG3LgAP0sP3Al/El5mSiw1vnOHORQ1YP0w9yqJqp6cvIQ9KCWyfhY9RVso0KL7mUvDumIXacBJj1G+Q0gwNygjyYSHWn3YrTIyAFuZSneKNg'
        b'rKyslrn5jUTjbYLryBC8mxkYLiSH8DmHuQkzNYkhzzBrk7ipvj4T8J1NW7tEOr2gv1mJULf+Zh1SRXL9ODEXyawFqfd4BPw6fvhIzuuHxn0UOCSCG0U9zbkBUIb+yrhA'
        b'fiAn58JYGWr3TPNGsPwRXB8I8Z8E9qsP7VbHQH/ctf4Wqob7rq56vFCq+zTgBjzO8U6r7PWun98N7MEc2qNP/g/wJ8OjWfhuFmqWuNSDHFNbPNkxvpd6kDYmR4+rLcYK'
        b'aov7U5k3WQiPtLJfmIORoDOkWWPxjum4XYLIZSDOQ9HQYnyAEayxE2sw8JC2HBSFokJxBzPNLVyKTyaLqax+AyWhpJk2VnnvMUEgcFROFWu1sqtD5iJ2ClgXQCMz6jmt'
        b'NjdOkSLwrCHBq7l/8r9bIU3QrQpcGSnwrLPGWkGAPZkmpi5mqMyOWwUifBxfqEhOSRwvhfd9yFBEBKO29fMCkAwd7SWTa01/WT5WqHjnuF4w+AF96LdzlqKxQhciiyMg'
        b'Uqvja7Rxz+esEHK+MEGGBiBtXeAsrWzDgMVCzhFRoRB5e3YYRG5NmyDkfG1tCLAGCaHiCK3szWqVkHPvOBq5f11AhNb0YqSjofJiegXOSoVYrpVd7pftOGI5j49XFeb1'
        b'xydmUzd44LMltRy+u8TEhJFh+Maw5IQEmMvruIMbRd22D5AtgoopawSahlqCw5F2hHpdvIMl6QS88ww9r52JL1EWQrmaMTbh5ORw0hGMepPbCN+C/0rcLuhTWgH1nCQd'
        b'UkDNjQg/C/8BL+wUKrtVDQiynUMl5ChSIuVQcpC1/FUuVQjIF8gma3N3l0UhxlkVzgfRsZ3sGbeU7KE6BI5sQvgmbsOb2erFko58evxH9kahIcAwdyxnh7KDyaVS0qpe'
        b'jE97WlxfxSdZF8JzJhayg6fyeI7s5CLxM3NZdXXkTu/YAEQukLPMB6hlABvm2iXkAD4PPV+PD6M6VIe34V0CF7lzMnTmPI+AKm2jB9a15Bo7GmYL0yWlA0qIlEzWmo4k'
        b'qwSN8+jnimDj/OkB3bflTcbil1dIrEB4UN9/zK7amZlPJkdsqqj906ifv6Ie3Bzxhxo0LXTIxb5v83dw/I5DP7KE7ml6N2nm7/7UK+DotHGSt8UtUxOeHvvclJTMz9bd'
        b'+6xLcfvlcQ37YkKO9Sv6oHFrZfSJo2891/9471/8s3LBjN5/v1D+x/PSYs3h10dk/+Vl1e5Vv5k2dv7ppm2GM6LNH+UUVfc/1X7rysMrz22qM1w61LRpSnNq1//T3JXA'
        b'NXmk/TcHECBAQMQDj4io3CogopUqChYIIAiKVmqMJEA0XDkUrHjjLSogihWQqrUq4l21at3OtNttt93ttVtNt7batYdd7VZ7WHv4zTOThAQShLbf7/uMTPJeM/POO/PM'
        b'87zz/J9/WbZW8e3BWxfKn3oPX9G+uNb4jdc3D/x/nf2pfP27Je/M2ClY0yY7NGLNqLIFN+rSkXxL+TOKV68Oey40/dhxl8FRHzSnr72rW/PLybMP+30WO+nnUWc1U2NP'
        b'a3r/1Tdf/EJuRf2uBTOurUmMrdEFRNdf2vZ2nwGy2zl76t48vCvmHe/0rypK899w/ff3r9/2Xpp19d7Rxu0NN1DRE++PiXt31aqfBt+KXp1/oCi4L53m0PmQhI6r0Xm+'
        b'Hd1ApgXR6YvM0/vmw2kZ6DJRZkJAGzjDR/UaMZ304yYtB+949Azpbu16RlA5ndhzkvBhUCMO9CFlmRxIFxL9BKZtdGYmKRc8Ozfiy2lgh0JwZ8DuxwuIhVeF9lFFJDXd'
        b'G2JkASJ/Aw+vwCsAwBSgQDtYnIPnI3ysdLE8aQc3UmJJb6I1GR0JnEfTvFB1cii8fWjjEe1j/xhaRCCxbZqoq0t4BA/X4MPM18V1mAmcimtd2nmfiEZATO06Huc3S+iP'
        b'NiuZX+kpL1xFzhlDLGRTIAKSklsZJoAYBMyfxkuDnzN7zAbgF6mSk2tqDPwM3ktscNJUrfggU1FstBi5F0OzHnDmrDGo3riRwVAv4x20suV4Nxmzm6YFJJkysVJy+mIW'
        b'+piYu2Kib6jwmqSwiAh4cU0qig8JiNS4iJmf7AAyfLeavW7NLre4JpR53QbGMP12O9o5A05yI01ULXPihHwealIWMOjDbrQZbZXhLQsN1tCHFI2e4hZ368mkBPqlfd8F'
        b'BdpL3RdIL2UxJvAzU0iV0fYks8JKldXsyfoRHGXEalsMFemPGhxpbYXoHGvBVnyGFEfy2jvTonFRdSsujwXWWItPoJOhIXg72m6Jm8RHB1KDzM4Q3Vo/E4JnYMcwCXR5'
        b'VMwT8s0BEXypzuVLPn7k05d8YNuTBkfwpWf4mP7o56bzAP6/nQdCDCAxn2hfD0UCWGgV80UUe7bEs12fgeKtXOe6qHO7J90Zktyxo0LVdbHK1qFI0kagqpCvbfQrnf7X'
        b'NsBGnw4IMupDrAXqN+ZXTB2OwdfYKDL7mpp/wTIU89Ck0DFw+qLuH3T5ny4S0wVCo1ieET89Pk2ePTsjMcso0Kn0RiFEKTC6mw5kJWZnUVWR3izTQn9/XAztMpKEQcuB'
        b'd5pIIPHuMVLMyVPo6eHp7CuSuJijYThTnxln2883Qh84Zt7P73jc/LktvOMc4snz/NXZqW8Cfdk0LVxEZT7ak20S+06cJFvwJD6J1ndauDZT1Oge70i/K6zzovS0XuZv'
        b'Jd/yS7DFRRlI1GSAe3jlC5UuSpGFjNdV6UZBOmITGa8H3fak20DG60W3JXRbRMl63ShZr9hExtuLbvvSbTdK1utGyXrFJjLePnS7L90W1wnzOaiVst8efp0zwHAWeCj7'
        b'9+P2egJgxbTtb97uQ/7286p5ymEmFLsLjQnlvs5rnSTflVL6UqJdcsyV0uYKKcBH9KQEWkM5ZAtvHTMPxOs8iHEQoBxKKXW9lQPoeuVwE6WuLD3xQb0N2DvbTPFKDjE+'
        b'XWkQ8J0Ax5WiWAl9X92RidNmIyQbMOcmWivyq2S+rkQDXNwAlYfAxIxTFAIjq0r1LDY3xc13iBetjeEowa6riZ8N2ItMP+kCsojFSgUeI2X+IqNgYTHZV6RSqg1FZJ+o'
        b'lNR8cYlWqW0n9bXLpmsbfcscAt2VmFVupnVhd0v0rZ7w6ULsgG+6zacLjf2b+XQfTafbiTrXbtiA30ina/VQLPWAIOpd1IIcdlSHYqlCU1qoCLdXlXHSvEJSZB4NVd41'
        b'u2/X5L52iHx70CKPJPcl/ZFFdU6YOlOqUcwHInny0zpQdnBEhxDUjJLObi1sq07bNijSqinsVN5UETImHkEt7IhG2H5cCUfUwt2kEbabaTu18O+gETaPe9bsbEuqVpoe'
        b'WNSjHphZWJhCeZu2pFpVgVpHWpgIKSLLaHcKkxpMj81QDCG1fxNbrxd7o9IrUhLRiz+JsvVuLRRxhjhQUi94El3eHqsuUfaBMMWk8Ntw6lZNEkuIDnmJuR4E9k4t4zIA'
        b'JJg7Y3QoIwHGa3DbdEfZsixleBt+AehqrHNuLhXj/X3LaMa7K8V9T/IoCXBqXbgTIwGeKjJ0yQFMPb2tMryYjc6h9e6oBZ0YTXNNdXPWOjMkSKpX1iTOAHIfnR9NNPz2'
        b'fPF5RXvWyaFZ1g7dK/BWV7SD2DrNND9VH9cYObzGmjcv7DRvGAuL64brwezqXE+8vt3Ms6nnBXyUVPQFd7RvojsLhZjiNkrNI6aqZF5YS3wAcz7nJ+TayzXIbMXYZLkf'
        b'HUUvoiPueD067al+okEl0G0meSQ9MST8zQse/HhxYubTv84NWj35C4W79MS2Ra9Leo8SRgj67/VdcGPLmBbDnVPh9ZvHL445v6137cCdd8M/Cl86zeufb//4ekzYuev/'
        b'FD2Gaz68su781msJ0f22PBt87ZXFDyQTLhSUV13+5K04vHH54XtZ3/nsdHtj5Buv/jVm4pjFrd9xD1/eis8qnj1dk/vQaUOs4u7uYDdqjmXOxccs5qUfPgwdzmRdrkEt'
        b'1GhJmZhsfgXuNcmaU7gZr2bm49psfNCSiRAdoV0MLMTBeJcQH5tbwYh1D0+WgdVla6LiJlQHZuolFTVTnWJRTWjEoGHM9mHMwQ0mK9ovE++Ad+ik4AMWM7qyL8XQ95tE'
        b'Gh1MxmqJl9kYXCJniMo2tCIZjtma+fpoYuhHTmVGaRveh6uJXWZjk5LhSczSSSF6QNSS5qgtZK8twvEp/IKOOtGTrVSqzYY7c2lojcv8CtRI7qj5D9PtLYhMCBFhZcgt'
        b'5yZTfmCecztXMOMNpkFZLVtmAl6idjhgDr4MyZ8geRkSBAmG5BVIXuW4R7PoiLqTiYfNPQUTWUlRRFaW3gruahfh7DrfR08AnG5yiwrlEGc3g9SJoTjby7KiEIZdXVAI'
        b'9xjIKZZb6VMOKzXLXKkHgzrUgGoHv5m416Q7OSx3jqXcwazc30ddbAJWCuVEY3JY5lxLmf6sTCut6reWRxQjh+UpLOUFtatOio5o2Z7TI68xt7JZWXFYA6WlBv3hTYaV'
        b'PtPTMi1IWYs55KjMApsySStbtCCrMoP5DHhNX4tYPGzT8wRWVQEndhjL1MU2nSR0hQriUvBNRqwbDWoszhdbXNqduuXSbgor+Z2TT7c5pVTAqNldSil6ck8YpawZpDpl'
        b'CYxSFlx0SJg0xBqgTbYp5pucZM2HQ7VcVg2gGem+JWgpaLw0q6QI7AlmgEPcOBPKWjG/xKA3ETXpiObqqG3gH5CiqKBJlOp8SpmjN2nmtjdlam8aJJM0W4EpKp4dpRj+'
        b'JVsonhRdGXmjY6xMG2mQmUfGsZFj3a5Mge80WKVB8fO1qrzCYqCwMVl8NDae3Yq29wOdTl1QTLsCI4rpxFamk6qt70pNjJ8CB2w0ZqNmNH3IMeMstg2UNDo4DF6ZmEmP'
        b'4QwL63GeI3OM9ko1vR5Is6DtYsd1n3Qr3/aG4K7VKt0fR5kVBBRRlNwqWBoSUgQGN7mdipCQ30yiJQ2ihFnhjHeqJ1l3QZjVret7Sl8ldUC75Yi+KqJ71bDBf3RJYhVk'
        b'IbEaHSydMzrSMQmVNYbE9BgNKnY76mJaUUpWn5CWNns23Jm9oLnwr1RRUURD7qq0MFWFUYY6i51sVaHIrivUJbOW7VsTNlpGmkeK3Woxhciaj4sUHzXKMbWaNeLG/A7J'
        b'apiQvWREFuvUrFIl+faZypQLSM+g7QEX0LjDinL43U2SJvgXb5OJjr4+U+cV6tWUiUvXzhPXecw6zDNcOhror1UGIlwtGZAerJaamohIqCIy4hJnhGcr9PNV8ErSPm9Y'
        b'uJR0FxYIVWMoWqgqtN/+4dKoDqfR0hSG/CUGvYrMHBCDWjqzRKujlXKQR/R4abwhv1A13wBDj1wQb9CXwPy20MEFY8ZLk4uV6kVq0pk1GnIBY7PTdbhzB1fH2Ktyzxto'
        b'rL1s1FbVKupZtWLt5dezdhlHG7K96R/R8nZ3ZrOeDO8OO9S7xz3R+vbzteRugqBtLXVSzF9iKAh23P2sL5eOHea4A9qcOHqcozNJNyse2ZkolB0c0zGbGEfZxHSVDekU'
        b'lvvrIo9Y69Mc3to4m8zs3JfDCc2ECCQSzvSL6gNEJyWy1SzKg7LYHOtwwm4HHAJ9PZkK2RbRcYJkZFNVTP5IN5fCHBTrmDyzHapom01kh2wiu8yGohpt2BSDKIViAsw3'
        b'YxxeZkFBsksTZ1BJDTukQWSQm7o4eeyOm8GgBVZJMltMMf0Kk1rpdokzpkuDcvD+Qi0ZpKQu0Y6rYgXAbM/MsttUKXNWuoUGra5zpbpS9xypl1SV7L7mZ1HR4m2WAbqn'
        b'w1Co6HhpOnxJ50SOeqr7l0WyyyLpZY6fhhmDalIhTdtgPnfVDyhAlVwCX+TEzuc5lmJJKq22eORUrcJAEk3EyKlqot05llr0dMeyCvJxLJ+gAMcCqquSiVRKLCRKGJH9'
        b'jkUTrRvR2ZT2q+Go8YgWq1LpQbOAb6JgxXSp380vKR8vhVVloj/lg9ZKdpA2d/xQ4SLAB7OrFBopbHR5RZ5aDwOSpF2qewwWDWeyHzTjMNDTw6NGx8SQnua4ToBHJhWC'
        b'ry57ZL6C3O1UIlS6OokimskTgi/pnBjHJ5rEnJkwtosebcZaj5dOJr+YJjwncmyX51uGNr3Edpmvy/Y2I7hNV7Ln41hYA3KbqGiT49PJ43EsEeer80iGyVNI0XZGZCfM'
        b'NSzo22W3Gp/D5y6mguvmvNT1KYOZWyqv9zwKkSvBTSaUHIXIobO5DPm5WMgpB/jBOlpq3JBChhRLx61pMobaS8IXKHBvI8PWjor24wb4z4V1rNwxcUkmMN1lkidj78gZ'
        b'wEWg1WOoa2siqiqRpaIWdMYC7aKwaA6toHm9K6rk+bp95wTRO18NKOMMEF1nBloR5T8qlJwNdInTwKEQtaaksThKHLAbTefKo10LPPpRFFHCkmk0XNLx5KLUzSk+uni2'
        b'YjVOUmA3WlJDX8gmiS1b2LBDbkEN4mC0Lkc9+I3XOB0EAH05YvyW6sspAoXklYLvf5U/6Z5X1C+wStX0p+kvz7ucm7RmyksDVq55zN1L8Z5w8JDtExrvS5bJ7zi1Lrra'
        b'8OPtvh9Pv9kUMtz/XMGnD57cFxc+5p1ycejTZV5+s4tfL80svBucN6Dlyw2XBkjuRIlvbRx4a85bEdGfq3d81uQ38GZ0YUUv9Tv3Vodv9svJfK1+ZusNj4+OqRRfHbp5'
        b'5Jyu9oug2MVjnUP9rv3w1hP94+4vv/aedu24W8mbh3/0q6RRciHU/4yPj+7i/abGi7KnPHUbgyd8XvNt+Ck32cf33xT0i1288t6rt395mLRxhO+miZ/PSJFGjAgWMZ/C'
        b'1Xj1vHZGQtwwFjAkvTX0oBxf9jLTYaEj+HmKIanGGygDiHdUaCjeMC0ZtQo5Z8EsDT8gs5wFx9+YorPmUGRrZ4XeIvcUfTg5LnMdYm9RCa9AjTYLS6gR11RSBke0F7fh'
        b'HdYhmvAevJrlzWI04ZO9qDtmDto5xZahkPPGu9BLlKIwKkMP42dMqD/aoJClJvM4/nReCDqN1nXGfYj/oDDn4PpGF7NgodZmMWs5N01EeQaFPE9eIA3YBL/Bt9DNtJDF'
        b'5/Wn3IPwLeEtEVuWaBRKZbpNwI/2F9cgBqxWr1x7VPFgoVUm7VFILXeywO4S1q4Ax0tYNnV2DPigwZ/AN4lbJ7QEf+oJI1MhqXoZycRGasItdeYEHMak5rWJFN0vXZG0'
        b'MPVpjZJJTXwYt6brDJnolG7MKLxFyJG+xavEa/FmhgiheE3SSdvc9aiR7MnhcvS4nkUaaFiAzmexq3iTUD2+wOHTqGUZLexYFAA7uFl/Gl4xRx88nWEWYhNHRkU742oe'
        b'A3DgZvwcLSAhIjAqWpiJGxngAzX1o3nsWwzADk6y17lS/NSETAbCuNEfMBxcrCRiucZzaCVz6/+Boj242P/O1KU+PiSEnblsCmA4uCCJa6X4iaUx7MwFo9jOPy1ThJ1J'
        b'zmNnzlYDhoMTTUpfkPpmooSdqQ+gQFDRiqSlmv9My2Q7PeZSbmOJpH+Z+ClPP4Yjl6CNgVkZGRkAM3sWr0jg0Ep3vI8B3HfgjcOjRgFnIg/tcsX7IbLGUXc6+bjhhqlZ'
        b'GeSp8vHeEeg5OLJuEb1KP+iJrLRMHtpsjRMZaKBXxaPj6BgFivDUqJXiRGoVBmA+iDXgZ7MGAN/BEG5I4GwK2inHO3KihHGkK0RykXEmyDVeiTeMxbX4CJmoAO2xELUw'
        b'2O8hdGARIDvMuI7T+BzDdjTiQ4z89/RU9FxWhlQADumuT/R2Jo97CoOoHyEXvQhB92Ih+3aAx2JUz+AX0NAtKTQSwajSpWWacpmetWlKpSvdOWpuRVj8sCIWXAPv6D8q'
        b'C5qUTKI5eDWnQFUpNAtJL1+ODEhpqUa7NM+5Hwt6oYEempWB9gYT5QAdLah0xy3oEjpMK+3Uz1vnEUUajL8AHDY4fAkdcFJ/Gqnh66AB3rv5bdH2OEB5VBX803XDvcHr'
        b'YgN/rtqzumZVk9/zTetFafzbL57clqtd89FP0vRJb7k+711yW5KZEDr7seaL965drKhLra9RK2beeP+vOy5++ZEh3+3E8A92vjr8epq2Kj1wU2vZn0+tPZEZsnP+PxLX'
        b'53qMeV9wIn/Gay/Xfv1exUuJeZVb870fDJL+bctC6fctC17sG36scMrct7KTngwcWHOnPqFF1rY/7t1fJxojgn+al/FO47XH1n7lFXjhQa993/U5Uv3Vjbe/ql5e+/D4'
        b'rRkDPn1XMfjSu4q3j+TUHlw1enpqefXG9Q/Fu1ZOWn3r8VXBa3eFF8z9SPLa3EuHNT57zu2+GZf119wva2Z/o0LB6YcMM9NW3os7L5QPfVMm1909nVL+06VZMQ/rwsbi'
        b'LWHnPM5vv3+9T59s/cdVPwb7MjeJXZGkr9qZ0cpwc4cJDZ2W0ol1QWkuBIpEp0YEp5GDInyBj7bjpmgG3FxJnksr0YNSeZwwHDcP4ZEO1+ZJj+WhRqA6xHW5FoJdfgUX'
        b'QR3pK/ELPCuqwzT0AuVNOIOqKXqynOw/KLMT/VuKd+O6RCfXLEaC6YL2ceByQt1NDiipx4mC5AH1DlmOT5pxG+g4PsRwG32W0Xm/95Th4BGTkGPBbZi8amqYXoCfR+un'
        b'tENLUNssiizB50nmRFpx4nh0qJOzDD6qBEgHKXYlhfEOQGdHm1WSQVKqkOzxpg4tOpLvZRk+0dsGzeGJVgsm48a+TDM5Nh21hKJNcR1ZxaaOZ/Q6K/HRRbIS3GiN5fCs'
        b'FCSgA+gEdQxyRTuX2vrMTJtPkRxx+BRj0anCLVLmlQM+OeWoEdxysvUUVRGND6LDEPdxZLEVRKMAbWeYljZyn8918trJRXsAnxNVwqIHjkBnrbExJqejPkROgd9RzuMO'
        b'/FUeEU6QssFQPWVJZz2lVGhiQ+YT7UTCF1EneIkJvQo4CglFUvDJt5sVpaTE9Ec/nzn782+KBrgRLUFowlhITM70/PvOrvwf+ORP5GZiQ6P6QmfCNfs30YF6DVSUkI4q'
        b'ygquqasIhR0L1epgrDkMTzyZ+wP419aQ2zF01Fjsk4+5pNMoKXEV6GwoOoZ3ds09No+FXertT0Zo7VhgX2xnEuORSQCAqt6k14dSGrFBaGs5OhdCZ8IJ+AW0KXTgUOAS'
        b'AyaxhXiVul/xRIEOsBs+d/4eZ80j1qvX0KG9/sUr422T+GgyXZwDC19Ttmx6ddUrrjXuZcP3BAwZ2Xz74ZDPViXN7/UP99ffbPhaNvqdn58/Uf3kkm2+J5JEEv+nXU98'
        b'Pevyluc/6Be/kF/xSjxy/vzqhnYasdsG/+GSthkfRN0a32yM+lvC/QtnJ54tPfjM+u/2XLlaL78379KWrLTsX3ieMw+OmV6/+9e5+35tjY77u/ePN45PmV3JW4Vjp35/'
        b'PdiLidStuCU4FO+bYc0j9lwZHbFlZGa34hGbWg40YuhUEUNVtaG1ZCBuCsOtSgtV2AA3vJdKA3TKby7jCbOQhLngl/j4Ij4/j4m8k+GLGAuZhYMsCbBP+zLkDOq3Z3o+'
        b'ZREzc4ih5/yARmxbARMm2/A6mMs34P3oBTOXWMi8App3EBE1O2QdWMSEiwtUaC275+0F/UjF+YstXGJD0Xl0jIGymmXofKgtidjTeCeqwpcGsPvehc/g9UAkdnSGhUus'
        b'jwHtZXK0FZ+fbcUkFoC2A5UY3o5W0HobfCCAD94yG620kIn1RbWMtw1vCCJa9qblvWypxA4G0BYRoOdRM6nZPrSynU0sDB/CZ/8QMjFKeEXlXEhnObecCw/omk8MREQ7'
        b'n5h2Mdc10qvcptjBZJ8urLNkWsF9+kgGMXPBRGbYQj4Y+otPv9KDfToivio4zhr21Q2fxfMcjQWuVxXpGG6rA0+Y9+8yjLvxhC6RZAgI8ZkcJQZzlvDElMbLL/i30oKJ'
        b'YbZ5KCS5SBf7PCbiMfW+IRNt0iUT6fiSWXFz4jz683Htk6gqmJeuHnRuH183kKjEyb3TE6tl09Ekydqnhwvvrti2ZoKId1006OVGl9KWO7N+7t0n+8TbrWFXY7MNNw7d'
        b'dg0+ejV1+S8TH4y4P2FRxef+Tgbt43P/M/jFgIZGxbWP81PDvvq+9K29C7+cNvYt0amaT+JmDX+x9t4yTe/Ae3Pi3qs4+peX7ry9QDh19oOUzz9ZlvpFZZP2L94jx31W'
        b'l7On7OXHro0dMvnNY3O/frzmP72uj7uwZZPTs0fW/eUL99c/a8ucFeDns3x72ZIxJ4WHjuvnvf+PyclLfP9+pfb0q2/Xb64cd+z8DY+SqzefyphSq6hKvdjwztSnfO8W'
        b'z804duJmhta9Ludyc1JT/Z6Hz+giKgLuSBZm32jbfKex5YOY8XkFkQvcMz9ML/tvS/Lx+PCmJYXv7x1x9+NlvH65+aKUjcECqpfhBnSWGEibiMbCi52EiGFXLUmjsmZo'
        b'aXint0GRqEYoQsfnUJUmNAQdswm/nYcuW73a0Uzq/HbG/3+nE/Y4IYJHYB6EdhMKTRXJ5ZoShVIup4IHTAauP5/P50XzBj3kExHjzPPhi/pLffuH+E70HcHnjQdRNEEk'
        b'8HQfvpxbxOdpP7CMPoGRL5dbvd7p//+gDXjaK5bBCzUF6aODJ899MckxfRlFem+KcEKbyOS8FW8owZenpaINaKsL59lPMBAfQ3vVfotGCnVbyYlXcrIHbhhHdA9fp4c/'
        b'3JGs33bFd+Ur2sC2eQdOPvbG/ilLfp6z5hmf3Lc2D883lD2b2mtL9D1ZZcWN7QWN79/YGPzLMW+5eljY+1d7j8xufr0l4cSw9UeKdFkzn00Jzf3wpuHqegV/Zcteb8Xb'
        b'e6uqpqwLX3Tl0xVD07+4XvZnJ17Ov0pfy/uidtr1gQnLv6298V+BaHrQlRlriFYB1c8gdto5mJ6nwfvqzTK0x82Fc0cn+cTSeQkdpibFYHwuRTYtHJ+As2AGfwyf9MYX'
        b'gSNpdyEzOponJLFGkBVEkwEA1iNpAx/BINySwTg9T+PWdFlyWkgaOqFy4ZyFfBGqK6fDLgw3z8abRjpzvCx8aTZEUzyN19G3nMRa9QtNceJ4Mk9XjqgUDeg8nX6Hhk+B'
        b'4GvVpCS8OXQpUTqC+XjbEnSOzuz+xCg9p7Mcl5bwOLdkPjoeghsZamAzOo7qZfR1LT4XbrKhPPFGQbqSmHGgd6jxOdTIVhFw0xMs/N8p1EZnd77waaqNsjfxztFOnLgX'
        b'H59GmyppUwxEh1EVMYA2hpXSE6LFTpwbOsVHpwfhOiorEvGuAHLCSTFav7jMgE/F5pSJyww8rg/eKkCb+WgPzUeOL+N1MkrHALcixER/dUe7+fjZQYjlE7VUDG0+UlaJ'
        b'24hYqoZXxbDDhfMPFKLVqjibMMkD/+9HWcdB5/oIwWNHDrUDKyjc3EPEYglRmgCw5sSCxzvqQ4FMd6CiZ7BRoFEVG4Xgu2t00htKNSqjUKPW6Y1CMJmMwpJSclig02uN'
        b'TpRM3iicX1KiMQrUxXqjUz6RgORLC0v9QDVSatAbBXmFWqOgRKs0OuerNXoV2ShSlBoFS9SlRieFLk+tNgoKVeXkFJK9m1pnxpAanUsN8zXqPKMLg9nqjO66QnW+Xq7S'
        b'aku0Ro9ShVankqt1JeCNaPQwFOcVKtTFKqVcVZ5ndJXLdSpSe7nc6My896yC3/PZ0/4Wfv8Xkq8guQ7JJ5B8BslHkHwBCfCXav8DyU1IbkByB5KrkPwLki8huQ3JNUhg'
        b'gUl7F5KvIfk3JN9A8jEkH0JihOQeJN9Bcsvm8blZZOv9BIeylZ75QJQPDrt5hRFGiVxu+m2ahx70N21LSxV5CxUFKhN0WaFUKdODRVRrBLpZhUZjopuleqXRjbS/Vq8D'
        b'+m6js6YkT6HRGcXTwXewSJUIba/9wdyKHbzwjaIJRSVKg0YF8HZ2B0IXIsc6drixvhRr/z9dpHv3'
    ))))

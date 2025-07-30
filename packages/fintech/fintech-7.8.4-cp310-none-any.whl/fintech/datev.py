
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
        b'eJzsvQdcVFfaMH7uncLADEXE3sbOADN0BDEWbMBQVGzBAgMzwOgwg1Ms2FtQAVGxYe+KoqLYRU3O2ZLsZt+0rSTZzSbZbIrZ7GaT3ay7Wb/nnDszzMiMMfu+7//3/X+/'
        b'T+RyT2/Pedp5nnM/QE/8E8HvePi1jYGHHhWiclTI6Tk9vwkV8gbRMbFedJyzhuvFBslGtBTZes3jDVK9ZCO3gTMEGPiNHIf00gIUuEkV8Gh10KQJMyfPVlZa9A6TQWkp'
        b'U9orDMppK+wVFrNyitFsN5RWKKt0pYt15QZNUNDMCqPNlVdvKDOaDTZlmcNcajdazDalzqxXlpp0NpvBFmS3KEutBp3doBQa0OvsOqVheWmFzlxuUJYZTQabJqi0v8ew'
        b'BsHvAPiV06GZ4FGDargavkZUI66R1EhrAmpkNYE1QTXyGkVNcE1ITWhNWE23mvCa7jURNT1qetb0quld06emb02/mv5lA9h0yFYP2II2otUDqwNXDdiI5qBVAzciDq0Z'
        b'sGZggcf7MhRYoRLllXrOMQ+/feG3O+2MmM1zAVLJ80wyeI+eIUJipHTIUXHOiIE8cgyDSEsAvkBqyVZyf2Z+znSyhdTnq0h91qxpaikaOVlMHuCjK1Wcg47YgtvwIVtW'
        b'7nNkB9lO6nJJHYeCsnjc2hvfV/GOnpBlHDlK9muz5PhATJYEicUcPkpau7PS5AZuxke1WTFZamitLleC1pCWELJNlBcZA6VpFnxqITmFa8m2mJi4KuhUHdQRhNt4fE2m'
        b'cQyFDGtC8BFIv0pOkAMKvGXZEgdpW6JY4uBQL9IgwnUr8X7oK82ZLMHrcS1uiNWqo2hnSQMNBaB+2THDxHgjqSf3S7kngLOfa+Iq6CoKa4i+3yqW9XOuILcFgHg1DyvI'
        b'sRXk2apxa/gCj3dfK0g70rPLCg4SVvBQVgBSLK8LQMpi0+v5ixGLHJYOy7q8VIJQseKttAghcoYyEIVNsktQcbHCYasWIkOWSJBMrw5A44tj3hg1BzUjUxBED1zTW/xV'
        b'OBr/5+4ruLd7fygvGP0hMgVCwoq8Jq7VZgiF/AnvWN8t+YcQnWb4MnR39IAB/LT3uH/3LjC3og7k0ECCYjI+BstWGzs9MpJsi81Uk224eWZkdi5piNFkqbNzOYRvhZlD'
        b'A58jt8mGLvMvdw07U5h/7x2E6OyXyd3zyz/T/Jb52iHSLvOryLPSHjAYJu0RIwtmqGfz5Hwo4kWIHIZRbXN0gyQ1PiYvgBqGonnk2tDhZLMjDGKtUXzBDIitQADWk+fO'
        b'c4RTWN48gFwmjVBrLJqRGDsC73FE0Oj7ubNII4xcjfA+slWNL+EDrNUgcnR5Qe50Ui/B54sRv5LrT/bi7Y4RkBQlx210N0RrAY635kyPxM0xmWyDakizBF8OwRvI1jGO'
        b'UMj63MSVuA2GNwY5po+RRBtHnrSKbfsgIXHmlAU/iw/BcYrNurezOjYd/u06UWvbS5KwaJlUXnb+6mn58wNvVpiz+fAZTWNWfbHvDTxyzT/Wf/ruG5+s2r1zyvaWr46t'
        b'aVYMMk5c1vBl+YiEjF1rToevKEle1GZPss1ZVR+W9rN0+Z3sK5//Kvvza68kvF31l+f4+Qv+9TX/109i/9BWcXDt6N5fz/35iZM/yP9l3PPfvBoQdHPUjjkp6xN3qiT2'
        b'gXRWrpLmeVpSH03qc5PJbnU2xR7h5JaI1EwmO+0MfWwntzKis9VkS1YO2T48T4Lk+ApPDsPPRjvduXifqjxao8qOdmKXULJOVGGx4PvkNqugDB8cJacz58A7SwApbIvl'
        b'UTdyR4QvDjMJFawnZ8l9mOhtpIHUicbkI3Eah6+Qs3iniu/gI1VWCi4qOfvzHzwo5D3qOabMaqk2mIGUMCKlAQJjWDq2I9hqMOsN1iKrodRi1dOsNiU8ZGPDOBkXBD89'
        b'4TcEfujfcPgbxoXxQZxV6qpZJeqQCoU7AoqKrA5zUVGHvKio1GTQmR1VRUX/cb9VnDWAvkvogzY3jnaOwrKSSHmek3L0Keak/6ZPxxBIKCc1uC06m9Rrs9R4Wyzs/+1x'
        b'I2KzOTQcX5EU4c2kyWtL0n9i51+Gew2UMQCmQM8ViuBXbESFEvgr1fOFAfqQGlTG6cV6yabAQhl7l+oDNskKA9m7TB8I70ECDS4T6YP0cgjLIQzYBMIKfTCEFXqugOKG'
        b'0A7pDDZneWwOP/k3bMxSkUe36KADXNgiFbmIO1QkoCHRFhGgITGgIRFDQ2KGekRrxAUe78soz+IDDYm6oCGxgOZ/iSTT6kWAWsYXK8YsDkTGq6YPxbZpkLLoTt1nxa+W'
        b'fFy8S79F92lxXXmL4WMIF744n7TuiN88/dDxvd1+YCrO153TmSTnufPFPxHvjBmgmBw1oE4+N33dp737zOi94aX9iQPQVXG3HiGPVFI75V2ez8B7o52UMg7vIQ3RUhSK'
        b'z4iqyXp8jG2OPnj7GGeOk6SJ0lMRUsSIAuLwLjtlOCbjRtymJbX4BUsOsA8qKZLhbfxy3JRv7wPJy8glcjOMXKdoTJuFLwIOTuX7VOOzLJWcJxeSASx24Np84A/ESEIO'
        b'ceTO2OksdQ65tyhaDWS/NTOL4gUZucbjTUnknor3gFKRr+3GgLZDVlRkNBvtRUVsW4XAI6wQtg9Arhg2kvhxdagABBpXPmFDSTrENoOprENMecCOgKUGqw3YRStdICsl'
        b'g82cq2VapTWYPkLdO0UBj3munRJ2tutO6dJqKf/EfnADXooT8Mp4J9jxjPqJAOx4BnYiBmr8GlGBx7sv7gL5ATtHDF2GZnwDr5cDb1QLy1wbSxoKMkktXc7p08hRvJ7S'
        b'RODwjku7iQONvwpqkdjioFSsbMVnxRQIf3k6sjTmfY0uR/ewOKy0osxUIt4Wry7+U/Hcl3u/+uJveHR0mmyncpdKzACGNC3DNwBgcp4f7wEvpA6fsw+GZAs58TxpA1Te'
        b'QBo06iqGrweT0zzqu0ZMIYW396aVbCVXJ1GgmdGtE2xwq8xOJ53D6/pp89Uc4vEOfGcpN6EEXxdWlvcJJoAtyw12o91Q6YQUiuyCShScgqsOd6+VO4tQlZite4fYrKs0'
        b'dIKGNUxoJtwNGAwmKAtR6oKJkKM+YMJHO/8r+Oj7AQY+mYBPCHCxAzd1gY1OuJiIjxv/2e0uZ0uAUkuSMgTAYGBRMsIDMB4W89sSHHG/jjsVJ06suoFQy59kSyOWq0QM'
        b'NObNGU4Bg7Tii56opIXU2pV00Xfrwp4EDYCLZfgABY0Ra1gd+GAhafFCJ3XkOMDGyfFOaukfXQAc2LrCQbkCcIXH+ti84UAiLDNd8A7JUp3J0QUaRB7QEOEGCTrfFW40'
        b'ceCpIOFu0j+mGC2ABOWcuTLxfxdbcM7qvYFCkueIhveSeUOpMDeTbAkuUqs10zOzZ5Et+QUCc5oJfKqGQ3ZyL1A6da4jCvLbg/B+J26xkvV+QQjvjDZGqNW8LQ/K7PrN'
        b'158Vf1r8MVlZbCqL+ihGl6kzMfCp0m35w0XDOd3Hxf9VElMasytSl607rwsrRa/0tIomN/VqtcfF6PX6TJ2s7L2cABQfF7phyARgNimxWxFDGgRGUB1VFuLBB5JduIEB'
        b'j1RONjAIrCf3cjtx03G8zk7Zm+5awxPwR47gulgXbtqG6xjDic+C5HDEAwYB/G5R/LSfHGbNJOGN+Fy0OjOL7MHnOikbWV+tcpIWsV9GUgBVqaOK8o9uuhZkkjF2UcHx'
        b'j8P46mAn6Ai5PBGWQLLcENplOwDu6iRqDFB7wKPSBajhe3wAqndrXaQ7b7TFZGs32uK2cM8kzZU/CaFinxAqyjNGbsiV2LIhYsHVB1pdZvlDwEQ/Kakoi9Cdk1zp3StO'
        b'racgVKs7b2gx8K+oiy/p5r8896fzyUwyjZjItJfffmmu6Oc/eKnbqy82hSBxj9BZr+iAcFGag+vw1gm9SwX4cAOHdS3jVYqAN7rBlhw3kwNukmSdz1LxXbwBAw8Uk0Xq'
        b'cXt3EOCkC/mh+GAPBg75uAWfFxgkcgXXupikQLLZNxw8DYeBCGCzW534i8r4YfZwgIoggI7qkE6EQrOwUs0iYan9QwRwO53AQAVWhxtr1fsAhicaUfF5Vireq4IpN0aJ'
        b'JYgnQUVFgk4O3hVFRUscOpOQIqBRWSmAUbnFuqJD5uS9bIy/6pCWGQ0mvY2xWIymMizKIJT1zIWRnyqJCQOhU1NAB0LLyZCYF3PCTwivkCkkYZIImYMxGhfwZbJOTiUZ'
        b'KsfIytMUfDHeNNW/HEP1IV5yDF8o1ouo3HKIL5TsRnrpMZBbjnMbOZBpZAUUtgM7pJPNgOJXPIqYZCgx2i0gE8ZqrQa98PqJwFR8Qpt4FD7bYK12lNuqdA5baYXOZFAm'
        b'QhId0yNFjsFebTcop1iNNnszz+b9kx/BmL9ugnnVWsx2S3oezLMycoLearDZYJbN9hVVylkgkFrNhopKg1mV7hGwlRvK4WnXmfU+y5l1dtJuNWmU02CVLFB2tsVqfpZ8'
        b'vipbbDCaDcoJ5nJdiUGV7pWWrnVYq0sM1QZjaYXZYS5PnzxLnUM7BX9nFdjVWSDFadInmGHCDOkzgVKaYics1uk1yqlWnR6qMphslH6aWLtm21KLFWqudrVhtacX2K06'
        b'ctSQPs1is5fpSivYi8lgtFfrKkzp+ZCDNQczb4O/1Q6P4q5AyTLaOyrKK50dgSiNstBhg4ZNHp1XxvtNSUjXGszmao1Sa7FC3VUWqM1crWPtGJztGZRTSbvJbixXLrWY'
        b'u8SVGG3pMw0mQxmkZRiAMV1M6410RqlcacqpBoAdcqrMbqOjpFPaNbdyao4qfbI6V2c0eaYKMar0LAFO7J5prjhV+hTdcs8ECKrSC2AfQycNngmuOFV6hs682DXlMEc0'
        b'6D1rNGYxhWF1nqMSKoCoHHKK6k4W01kTph8iszIm5NE0g8FaBtgCXgvmZE2ZqZ5ogbVxTj7bC0ZzBcAarcc57Zk6R5VdTdsBtFOicbbpfPead1/xdO69BpHQZRAJXQeR'
        b'4GsQCcIgEjoHkeA5iAQfg0jwN4gEj84m+BlEgv9BJHYZRGLXQST6GkSiMIjEzkEkeg4i0ccgEv0NItGjs4l+BpHofxBJXQaR1HUQSb4GkSQMIqlzEEmeg0jyMYgkf4NI'
        b'8uhskp9BJPkfRHKXQSR3HUSyr0EkC4NI7hxEsucgkn0MItnfIJI9OpvsZxDJXoPo3Iiwn6xGQ5lOwI9TrQ5ytMxirQTErHVQVGdmYwBsbAAhyhWosgJCBuxntlVZDaUV'
        b'VYCvzRAPuNhuNdhpDkgvMeisJTBREJxkpDyDQS2QuwkOGyUo1cA3pM8hpyqsMG82G2uAYj2BxpqMlUa7MtJJelXphTDdNF8JJJrLab4p5JTJZCwHGmVXGs3KmTqgix4F'
        b'Ctga0JRpTMfrWVknGVcXQi8AYUTS4l4JzvKQNLxrgQT/BRJ8FkhUZlgddkjuWo6lJ/mvMMlnhcn+CySzArk6gS6zOQe+BPgTFmc3LLe7XwATuV8TPbPa3NmEhcgwADku'
        b'94gYnl5oNMNq0PVn7dCkaoiipBewtFcwwTsI6EdnswO1sxrL7BRqynQV0H/IZNbroDPmEgBb94rbreRUOQBRlllvXKpRThHoh2cowSuU6BVK8gole4VSvEKjvEKpXqE0'
        b'79bjvIPevYn37k68d3/ivTsUn+yDTVFGznDOqs3JaKg6GSNfiU5eyVeSi33yl+ZGZT7S8323RvkuX/FerJj/MTwl3R939n0yJ/hv2YtPe5ZsgCp9ZfMiASldSEBKVxKQ'
        b'4osEpAgkIKUTG6d4koAUHyQgxR8JSPFA9Sl+SECKfzo2qssgRnUdxChfgxglDGJU5yBGeQ5ilI9BjPI3iFEenR3lZxCj/A8itcsgUrsOItXXIFKFQaR2DiLVcxCpPgaR'
        b'6m8QqR6dTfUziFT/g0jrMoi0roNI8zWINGEQaZ2DSPMcRJqPQaT5G0SaR2fT/Awizf8gAEF2kRXifAgLcT6lhTinuBDnwabEeQkMcb4khji/IkOcp2wQ509oiPMaj7OL'
        b'U6yGSr1tBWCZSsDbNotpKXAS6QWTp01QM2plt1kNZUAEzZTm+YxO8B2d6Ds6yXd0su/oFN/Ro3xHp/qOTvMznDiK0BebSXtVmd1gU+ZPyy9wMnCUmNuqDCAPC8xkJzH3'
        b'iHWRb4+oqYYS0k4p/RNsQ7kQ7+QaXKEEr1Bi+jSncsWjcBe1S3zXqISuUSDmmKhQrLNTvlRZ4IDqdJUGIKM6u8NG2VphNMpKndkB5EVZbhDAFMihLzWAyqOIkRJ3o54V'
        b'+87MPur3QZR81901I1Mxdc6OEphvpZPlZVNZRtOdkyy8J3i8U5mwU1P1iEvPa5ZZqZ7UStWhVnrsLJyZUG26laruOyS2KpPRbh3o1uKFeevzqDHeapdiUtDn8SKek37L'
        b'S3heGi/7mYNWrTKR2zZqbbI1BjeLkQyvw/dT+DWZ+N7/sD4vaEJpqcVhtoP80BGSAYsuyB26KoPpkx6CNo+qxR/1nQRgUAm8BVWZKgXJB4DYCKgHslB9bIeY8kBWag70'
        b'dTtEzKoUWBpLhdmgLLCYTLGZgJPMam011bB0BjuxXPocbaFSKEY1aRR/2ow2hxBB0zzDwq6bShV/AocvNJQxS11QWmEi7bD6JuBKPIPpGQaToVxPByK8OtUune8JTgkp'
        b'3TUTjOOnLKHBubldYptSYIucwl+nmsop9jFmnQp8kBm2l50JBs4aWHMmI2Rgb0ZzmUWpVk6w2l1dccZkmWnJJyJptgRf2RK6ZEv0lS2xS7YkX9mSumRL9pUtuUu2FF/Z'
        b'UrpkG+Ur26gu2VJ9ZQMuI79gZjxEaIWFodyugUUmdImEgDLXABjTpYtVOjTKTl0sRAqw7FKOapSUY3fJ3YLStXMZlTnROelTHObFzCzXYC0HFFVN0QqNz5ilTEoTCG2Z'
        b'KwtVCvuKd8KNkOSjwvRCJhDQgVsrdTTRDSK+Utyg4q9YwtOK+U4UQOgpxXwnCiD1lGK+EwUQe0ox34kCyD2lmO9EAQSfUsx3ogCSTynmO5EWS3taMd+JbLnjnrrevlNZ'
        b'wacDin9IiX8qqPhJZQWfCix+UlnBp4KLn1RW8KkA4yeVFXwqyPhJZQWfCjR+UlnBp4KNn1RW8KmA4yeV7finQg6kFthJe+liIF3LgPjaGWu6zGC0GdKnAInvxH6ADnVm'
        b'k45qF22LdBVWqLXcADnMBsoWdaobnZSTIrwJjjKqGHMjORcthSSKeTsJsjJygrlaYInpiR4g41yjHUijQQ8ciM7+RPITeLhr4U5M/mSa1URu2JxsgldKJjvfKbMDV+IW'
        b'rBglUTN+x6cU4Bypk5oD6QdKQ5noMsY+V1ICbzcYYVrsbk1xFvC6dmOZcbHOE/sXMkHQrUH2ZDME8dHjJNGTTZpiEGQLg7GEJuXAqtGjMZvA2fhn1Dy1w9BvaFlnclQu'
        b'NlS4VNmMCDIuTgVcXJ41yh8TS02u2v0ysX1kf3BQXjhRRu7ZcvLI9ljGyZI6bQDqsRzfKBErRsR34WMVLj7Wznnzsbulu+W75Xp+d/fd3QV+tj4gUBoYpI+pkdQE13Qv'
        b'E+nlesWmQOBrxQaJPlgfsgnpQ/Vh9XyhFMLdWDichQMg3J2FI1hYBuEeLNyThQMh3IuFe7NwEIT7sHBfFpZDuB8L92dhBe1BGa8foB+4SVYYzHra/YmfQP2g+qBAWaBM'
        b'r67hnT0W65X6wazHIcLodgft5sroCAPY01VySH0glNMwEzoJ8+sIg9IB+qH6Yax0qD4W0iQ1Mub1Ec7ShutHbAosDIPYbtCzkfpI6Fk3aKW7XlXv8lgIqQktk+ij9NGb'
        b'ZFBLOJMGNqniOmSTqK33xILZj2KDlB7/XNFKAZUIvkheOZolVmp4ZKUOO58wk+9Y+sasNahIoFJ8Qs1tPmFGzNTYpjO7dZQru5Ua3ljjaRZq9vAJswugcKEK6AjS6ZcC'
        b'drIWGfUdgaWAI8x2+hqiE+SXIhMwefaKDlmpA7aPuXRFh4zarBp1JqdJhrzMCHxdUSVs3QrWdodo8qwZgs2HNQ0epTIPYAxy/jKrnSnoCZepwBppTVBNQFmQ0zhItkW2'
        b'Ea0OrA5cJWPGQYHMIEi2JrDA410wDvqa+lt4zRz9lyV01VhtsDE3Mfd8G5lVQ6lB06VIl4jRIHroKpWd0zTa6SAG6IXqgpweaM750pntXWqg/yIzACvYXThJpVFOoOUB'
        b'f5Qqmc2g0lGlBCw6Sqk3lhvttq79cnbDvUK+eyEk++6B+8TjO/qQ/F198AaN0coc9pd2YWpsjivV2TGb775QmkOxPdAKjXJmBeB/2AEGpc1RYjLoy2E8z1SLYE4iCKpQ'
        b'k1IHVUBY6L/SZAFaZNUos+zKSgeIKyUGn7XonIMvMdiXGeiJrzJSbyjTOUx2FfMPTPW/Fs4tMVo50fmmLKUqw0j3QaOHqlHlrxbXdhrtglabezGpO6LFqowUzFYWk3Zr'
        b'NQjf/ipymkqNZpIW5UqgGgFGnNgl0lCuUSbHx8UoR8XH+a3GYz+PVk6hASUL0OrKjGbYNdBH5QqDDjoWZTYso6eeS1M0SZr4KFXXqXoGU2OF4Prw0NwNKeFvRXWx6ULZ'
        b'dOSg3ib4PjmD75DaXNwyjWzJIvXaWLJ1GrU2zcxRkdqYPDXeRhpyppOd5FgmvpiZl5ublcshshMfU1jyprCK760NRr2BnJpmFed8XdYfOZ6DSJ7sTfFZLdlOtuYAXcVb'
        b'ab342BjPajetUKB8fJpVKwbEBuQ77LipWHFsxhLkiIRI0ljGHOHcHluZGnVUNqnX4XYtviRGKfOlNnyY7GE+Z6ya1IQASqKXV0cWm7ZbwpBjLB32sYxoX70jW3D7Cqi4'
        b'NoZ2sk4126Nz+LZVjq+Se/iwcWFctdi2BuoZ9u2pAa/+NHBdXNjkN3LWNH78XyExE1pF2lY06vlvfrNl7npzwOdnFJ///I9hyxWHtMPk+VNk2vDhge8u35yyNums+m9n'
        b'an+Qcfj8LMfrPT+d9e4HRRuHHHsv+UXy0faQgb8gv+215kRKS/DJrG9Kxzde/4d6648/+sOD6Hfv7H/jw3+ISksif3fqhyqF4OK1qw+5iGtjyT2y1e2TKUKhw0Vl5G6w'
        b'nSruZkQE49p8zxXlkIzc7Es2iqtJwxpmvGsbPEwOk6rKdTjtvnvgGnwTt4pl5LKcWefi03gf3gQVea0hh3oOLgkWyyFth+A60IZr8ZlodeRsWaaaR1J8gFeT8+QMa0U5'
        b'zggVCIvGViwcX8K7cZuI1DrkdsFd7+KSaI2qJ24i24Bfk+IWPnGknI00fTVZj2upD5l7haQofOnIIhG+p11lp8wfuRJJ9tKxOtk32kXnCiN8jZxHcWSzVINriu3Dae57'
        b'5DI5QEdUGxOloXlJPWnAxxYB2wd9tUmCq8lONoP5FeQ2zcdUm9C0GhrG+yxIRDbjI7iRzU9C/liPlp2MI944oy++JYZuN+Orgv1k0H/o4tbp/sKMTykPgtZKV0k56skm'
        b'PKknm4x5s0EML4XYIK66m4ssP+GGEyTYnVI8YB1PHxPoI4M+JiKXy80k9HRzZplQqrOSDHcpVokP551PkNMsFK0fuN+HhWvX/nqZPHPOX2ZdSnu2Ci2CQGCFistTcR3y'
        b'ok5WwtrbPXceTktjTLrKEr1ubDeo5a+C16pHm67UR07k7qzNxQhEAtHQqy1m0wpVM9ch0ltKv0/ngorcDIavvlmpf24ElLdmwcujQUIPhCI+OvB9Wg4t8mYr/Dbfy928'
        b'6qmMx3/akcAiF13324W+7i70ydDZDG5G4Hs3We5q0s1T+2tygLvJoX7ZhP9svLIil3+bv7aVnW37ZS2+Z9tlQtuKIk/pwV/7QztX/Dv4ET+98HJCYC51fA1yu9T9xy4I'
        b'rqq7uCCsGnBfxJx4L+bpBEeoirKH6A3xxrqf1b2veElxSI3GPhD/faNBxTPkrVLirbi2Gj94En8D9paS24wUjCB38QMX+saNpKYThTvx9wt479Oc3AKK6M7ycGxCa9Ha'
        b'iJHVYR7YjGUQyvR6sqbe7jV5nnYH5tdGo9B6tD6kwweW7FKvKqgjwLlHBTN/qc1uNRjsHbIqi81OOecOcanRvqIjQMizokO6VMeEUXkp8O+WSkFIFdl15R0SC0C+tVTu'
        b'sRIUkYe4VoO6ENXI3cJlsPs+gRDhNoeyEOfiy7coYPEVsPhytvgKtuDyNYoCj3fBQ+rrdyU+RMwJer0NZAjKCOsNJXQfwv9Sp52c0sCs+p9BymQyEBNgdMoKR7nBQ66D'
        b'2bEZQS5SCs4PVESzGewaZT7AeZd6KEKopIczxsoqi5WKo65ipTozyDi0KMhHVkOp3bRCWbKCFuhSiW6pzmjS0SaZSECtLG0aOlIjVbPBbnNW6RSraJ1d6oCqHTajuZz1'
        b'yF2NMootXNQzzMgU52grqF6ka9+75I+066zl0IbehZloeSVVHNqoiGJb4qCzW2LVlS422G2q0c8u+QswO1o5wYvAKOexo9IF/orRlkcrmafDvO/0d/Bbi7BFRisL2F/l'
        b'PKf1nd/8rq00WknVnrBUTCKd52l957cs3Xwgy8JTOS/favefT9iekFV4YW3EKLMK8tWJ8SkpynlU1em3tLCnQUqdMFOdNUk5z3l+uCB6nqc3h//GO1EBlbuFgJJW5GlD'
        b'7Lc4IA+YzArYGrBdbaVWY5XdSc8onFJ/b7a3JphsFoBfg96nygDAieam1MfEbgZii61RThL0BmyLDimw6yorqT+ceYhfDQLbDABY0IEq59bSG9ndRDqY1mVGoHKG5bDi'
        b'zg3XtR76L89iNwjbhG1+g73CogdMUu6oBECDvugWwwaETWOA2Sk1KC1A7n3WIwyJbhqmELEJwzTaPLqkUU4BpOZCSD5r8dx2VH0CoE5vXio1wYCFS5dsBt8li533LllK'
        b'Wc+Fk5UxFXZ7lW10bOyyZcuEGzM0ekOs3mwyLLdUxgqcZ6yuqirWCIu/XFNhrzQNjXVVERsfF5eYkBAfOyk+NS4+KSkuKTUxKT4ueVRi2tjiou9QVlAq2NXBMDzPQSk2'
        b'Xk8axtlyVNlqTR716YvGzSALDhs4tkBSYSHX2T0wZAtpwi2JNPc5RzyKT61gAn/EfAmSxbwnolfx/HSOAzmokjR3lUjrEsymky30NpRs9QzqHDsjkvqbzoHK4A+V186Q'
        b'o3gXvhxI9uBmcsfB7i+53p/sIW0g9jYYUoErCEAS0sQr8Hp8x8HEyA34GoirbRp6Lwd1xIX6oQUQfgfh09PxWTG5o+7rGM9yzsUNpA3k7NxZZEeVMEAovt41yGlkSx4U'
        b'rtPOqoJHfk422SNGZBveICenLOSAgxrxhPUkt+UaVTZux0eDUGA2udKdp52e46BMxRy8aS5pywrDB6ACDonwPg6vC4xxUH5pLG7MkJMtsRqyFdqLwc3ZIEpv4ZBy6li7'
        b'RDxVxe7LATboCD5P2mKjOMRnklozl1JGXmBzeyxAihS9P4QCxTnKMWMRm53J+FoQdPmGLRgm6XoWa1U2n5+6gOxnd5YsTh5Mk4KDNWQnuZ5DrkSTXSLUawXZNlWEW8gd'
        b'fMFB7yUIwG34olyDt5EmqAOmL4vOiQj1ILfFofgObjTiLwdJbE2QtUXUqP6v3KD2N3FcmOS9UVmPfnc++rT2i98PEN/D6070C3T8yhyD+5+81xyrbPtm+e/ju2/sMfu5'
        b'uLuBQ2dWR/52S7pDdbi46RcjEmvU09e+mPiDD95L2v8w/qdTc3796q8VSWfT1BUTtZ8aJ2sL37p2+/iCMfPOvv63zx7Z72otHVH/XkHeua+5c/jNygebppvnvrurfu7k'
        b'b16LPv/P0NBjUcBgqqSM3yQ38a35uDZWqybHcbuXRgYGIvCbeBepm6fNwXUWH5oKFJ0oIQ3xlUxlQk4ClyrXhoQ8oZwRy3JxE1M8kFp8ixzyUE/gI+RSJ4ubSLYxJ9ns'
        b'qd2i85bGqrOycrUxpF7FoZ6kXZygyRC8b2unkuPamMhM6AMsIL4wl7TzK1KyvO4CCflPr+jx608bpNPriwQ2jnHOI5ycsyJTwcm4nhx9ev6I6f088Lc3V93dzQF31iFw'
        b'6MGC2qEQuezc6H0h1vn0sYA+FtJHEX0U04eOPkqQl6LDt2OwXKizs5JidxMl7iaC3S3q3O0wxl5Pq/Bk7Ef8ygdj72tYqsAOhZ6a/zmZpY5ggQV2BaW6SvaX3qhi6Ah0'
        b'HvmWGjrklGEBNpEahAk9cQ+2NMgDG1O9TJgLG8+g3H2QF38fAhx+qJPHD6M8flmYk8MPYhy+HDj8IMbhyxlXH7RGXuDx7jxEagh4Ooevcxv1KYUbl56Bj51MHSKE3Eog'
        b'pjBnwKICg6DzvGeQMhExynKrxVEFqcA767oSJ0tlidGsc7ErUcDJRDE6K5BZqghwW4DSDrpl4y41UVn5/4kk/38WSTy32mi6UEKMWwX2HaKJ194UygtRrgp88mfzvsMo'
        b'1G9zwt4X2nFud2ecwOKaLVSlY2VMrNk3a7rMQnlIY6XO5IcJnvcUs1gQLXwbxvrtMcVSQn9LLJbFtL80RqPMdUKXjoWVlpJFsPAg8Ps+WDRTkSg1JS7eqSWjgADyHK1u'
        b'XqfJrN9OuJHkaOUsm0NnMrGdAYCz1GIsde/GeR4Wt0+VCp1I1nsZmDPePE+r3O+U22jxJ2Q3L9vP/wtErwzDMkO503Ln/4lf/xeIX4kpcQmpqXGJiUmJyYkpKcnxPsUv'
        b'+u/pMpnEp0ymFA6QLw0Wo4hS4e68yVUm5EimXON5shsf0Gblkm0xWTn4nlvI8iVbrcX3ApNKcD0TG8iJbHJDEKqoSAWc8gFBrIrIdYxibG8vsk6ryc4FjjbradVOxduA'
        b'eSW1gfhsONnsoKdOC8luctGWn5vvvHGNtkAu4/1zyA4o1UC2gHgVBCIJ1Arh2wXz8SF8AJ8MRPgC2SvPww34rCCG3iTXyQFbNqnPyk3rla+lNyrFiVHvDBGpM5KbTKZa'
        b'GImv26JyyfZIyrxrsmBQ9/DFSA4NKpdIksgVZlIWSg5VyUEs2D5DRurnr1XngezFo/BEET7er8IxkrHfeDM+BfPhPNrOx9typtNr+fD1GfRC0nhcK1m+dqnQrdt98RWh'
        b'V/lkfVJWjIrUS1AEOSkid/G11Wy1KuNEaO5EevBWHGOe2wcJInND1Xy5FKGZ5OYiNBOfht4lQXQiTMMVOZ0nmKad5GYmiJ31pJFcp6JoLb4AoRyyPZNKY/P7VOL9sqmJ'
        b'Wnbn6mBSg6+QNnjLqiIPUBZpBZmPJpAL+BA5RGXzeHIJN6H4clwjXN56m+zPFi5vxYcHotglK0zfPH78eF6KGMlUERS2cjbM6iMc3QdXBKAk9UBE7+SdPWUectCjxZ74'
        b'3kg6QfVOUT4zZja9Wjk2exZARSbZbSZ1BZEqAI9MgEnhLmUVvsGmUGoOXlBI7jIhdzDeWVlA9iRmi1DZbI60INKyGACTXqC9hFwYLSf1bI1mdAKMzMf84Etkl5gcXY1w'
        b'zazA58vxRnZZL35hODnZKQ1PjyR7CmSC9DsKN7gE4HE9pCG4BV9jMvIgcspgy1bn58biOzyFozyn9Ksi+yX4GrlkY2BEdvUjbdGwJfZBV7bHZqukSI4f8KQNt+N6doOw'
        b'rTif/4EULW/Nujj+27k/N3yB2JjGmKVQkGk98LoxMwRLDIAysjU2P3d6pHD7jpe5AzmMzyrIDhW+zbQKACsPKqM1WTFRXDG5jKS4gY8NIifYYk/FW9O0ZnKTCY68lUsd'
        b'QxpUIqFYS1k/oRRpwruEYitwCwOF0uH9tXOj3IXwkWSHcAuUzQ5DnGn3GuBstfGF2v/ibakgPlUlHFmw47k80QTF5s/7WFIO5mZ+o736r3fWDT11ZsqJM21oeHiGdlLy'
        b'W3H1qluIV92WPJd8aOvN31ys+Oi5lUfGvvbrlx+lzJ9h3Rlzc6dha/eT5CeJhVnPzUt37M1V/UU+r2fmbfW3J3IfrX1FPuyHq/Z9lVmWuff1gXb0s+PEYHur5rOmX0fe'
        b'fvRmUOMPLpd8aZdM4VI+3T40M3TH0sJL5+6/MfjTNzYMnPT3wppr2vZuAyxpV/P4cQUD1KHtr9ivGt69PP5NUXvchjW9R395p7xl6kcHouLn/ri4/rNR/Uj+7w1NU2va'
        b'fpO//jdfvKR6LfDevR/nH07++0vvPvp449SSdc0P6qVF0yNe7XX4ixFzLrT8u3Bf9ZvfTv3q2pA/35/X8CBn2Z9aFt345q1qu/bh1D9lvjZu1aTLhthzfzC31qgTVQsK'
        b'ljwOCJ9mzt77L1Uw0yfE4BvMXsTLVmQY2S8q4/BNwSyiPTrXpS7Lx1d8qCbIEZFge7KPNOmdZiNkV5yncoIjO5jWYWS/dK2HvUfobA3ZITLh1pnCZZU7yfGC6CiNihl7'
        b'BD6Pz+HLPD49lRwVbEkukrMrojUU1cdw5LYSIGg7rzbY7RSA1pDTcdrZo3KipIhfwI0ag08wAxK8OUiML+TkxvConBwUazl8dTG5ye5aJfW4DQFFqGcUAdHrLpF0FT+S'
        b'7Bppp+YUeBu+jA8/aQ/yXIXbHIRcX2qnl6Ab8abJzsNC2EQ3Y588LCzBF4QbFdvxqXgb2VpCN5aa0i02391gCnArqU23002ydFq5p96FPOjOrwjBt59yz5Yq7H9ID+NL'
        b'IxNC1Q6dkjjTysym3MFappfhBZ1Mp2YmiF1+JmZaGRqS8SHcQEiNgDhqhULzhbFcNIeCD2Il+XX0LZyr7uWl7uhsV9DkKARtioE+yuijnD7ovY5WI30scmtYfClxAp7l'
        b'FuYgoc4yd8UGd02L3O0Eu5voVOfQTxIUeqpzos74UOf4Gx+9Vt79j56ee1/SLqkJqEHsMJWrCWJKGHmN2H1Ju2SLdCNaLa0OXCVhShcpU7RI1kgLPN59XdJOG+p6SXuI'
        b'wOElx/NIHNFHRHkGefBCNJPFLp4kQbKwXlKgzaZPqhYhB/WvlPUhh224XrZkNjksQqIQLnUu2cvuVMft5GafAlw/E7bOptGzcqeT69PI9VnBKXFxCA3oJcLrYVPfEPTq'
        b'23TlBaR+ZrJ5SRzZlgSclWwJR46R+y6i05JfItSkiJgFNEkSxeEDQ6WMeqwgG4azC9k1+O4YNGYe2cFo0bDSCnKS3mYbh3ejEag3uQQEn9Y1nxwq1GrikrRVCck8kq7h'
        b'8BHgCG8KrOgdvGmw8wZ01/XnL5DN5DA/0thycBhnewiZLhqGVjZMyBbHh02+sCtv9CfTp06YFPpe7pj1lxY8n/r60G0izaaf/Gjp9LfvT7CiLyqGP1e3RfPlZ3/841+y'
        b'Assid4wfvWTTHGVc07u3N3Xrfv6A/uVh/+zfe9GJwu6Ze+u/Ovku/tOBnQ+HD3sHORIXFV531P/pvX+99PWnMRNDPgzKSx360hcng698Mi3ry/n3Vif12vm7acavL/T5'
        b'zf0xW/YcU3/75olXGkd8NHLn8Temfv55vengF9dajePG7U799z9rHv+X+pRZ9MqVn458//bBVmXGvekvf/bt0rOnT79vfm/siN/9+uU1uqIHkR8lf/bbf9RJC3vYAv7y'
        b'136fjio+Of6+Kpwhprm4DWah1kgukNrYAMTjE9ysfLKfYVmyZSo5wdAsuTQBwIai2V7CPY52IzXQcyFZQLD9K/mRAeQEQ7HkVp/nnkSwIEIc6USxB/MZmcIHbPgKI1N5'
        b'8d5GjTfwHYH43CfrQUTIi8laRbbkkoZYfF6MQvB9URE5D71kzMQlsmMQqaXnLfjCcxIkHsjhE7heyoZnXFUe7UEEFTGiKGXAwBjhUvyDuC6UXnqvw0c977239Cb1rPHU'
        b'sWSz1tuikmzDL/TEF8X9YqLYTct6cogc1QrGkiezO+0lwxfRc48HeB+bkO495jFaS3ZW+j4GIM0D2akCvpKAN1LbV2gTWMKLLgPI0IGihUl4ByOns0kLjBbIbeXkToIr'
        b'Mo2FtigtHgvCySlKa2x2F7XhV5BT+J5wrep2vA5IovOaftKAz4iEi/rLyBVGPoOgc/ed17fW4n2d97fWhgpXA7eTjXgdSEkw6MK0fHrvKt7BW+bgs8+Gif9bHwBwWeEI'
        b'1/0zqnXKTbVksSEULzPcTC8npxSLpz+PxTz/b5mI/1Ym5v8lk/D/VEj5R3wA/w9exn/DB/J/54P4v4nl/NdiBf9VWDD/V3EI/2VYKP+XsDD+z3w3/gtxOP8naXf+c2kE'
        b'/1Dag/9M1pP/lO/Ff8L35j/m+/B/5PvyH/H9+D/w/fkP+QH8B/xA/n1+kPT34sEhfE9oJIzSQA9bHqH7AvEL6CQ7HQGCitvWIbHZdVZ7hwjyfV9KJ7FW0Xezm6BZ3FSN'
        b'ETR6C+1FStD6OgkaWq988+mmR0J3/xeswSpUokd/6KKtELy/7C53E6fW1+RUxlgNdofVzNIqlTp6qOCh23kmhbxysWGFDeqpshps1OZSUBo5tWA290mAU4PkS5H+5CGB'
        b'SVC90e6UrLAbfCi5vOiz1HPyPEz42cXQ5DJ5MADXkr34WDRuwFtB9t6Fr87BVwFRXpiOt0hQb7xOtJKqMhiNXImvriWNEoR34UtIgzSZwQ6KuvrPmQ+km1shW4Jr56jJ'
        b'Xq1GI0IReKsINy8nFxnNP5sHKB2FyYNQcU6FdqDwQSPcumYy3pbAyD4tKR1C9pTge+QUOZGAopIlqfi6jNHaqYAwT4LYRx6kg+QnSH3k/HhGa0fQj7MIRJ2SdMBXhxhZ'
        b'J5flwjdijiN8D1AIPogvOiXDeHyfJRWAcHB3GT5WIBTlYQz9E6YY2z/9QmzbCOmHBrbnvgrbKj5s8+//Plr904Xo6kAyYLZVFHMrq3FBzdG/zDp0PDc1Mrj5xW8/epyS'
        b'GrRsZso7fx4zbsNbEycEZwf/6J+7R2iiRoy8FTE7vrDipeKr7yd/nbj9rx2vffzKiR9J8nIfvzD8uZhzWWd/9NsfF71Wv+LWymWJo+Y++vPPjhcplr36D7nmj8PrZ2ld'
        b'B8DrSXOh6zzWTnZ4WRyW9meX6OsM0+h9xbo8Uu+8rlg3giUMxed6RWvK8I1cHsZ4jtPirWMYfo4nB6lte6zw+Q8eyQ18H3KfHMM7yG3BQL81D9+nze4ufsIKXZBKei5k'
        b'aDqdnEnz/J6LCZ9ipC1vlkr6HRjEj+mjzlZEdxpDukPcSFdsChdRQ/RwLlxE0a2C/Ui/7S0R8x44xFn4O80irfD40Bs7hRx8KnZy1tzMdYirdPYK/5e7j0XOi7PpASf9'
        b'HITUfcG7+JkueAc++/cizsfhZifCorjDpltK30wmT9T17D5ydBCjlVllyij6FqUE3GsT1OgUKRmWUzdcqlWO0lQbq6JiWENO7Gj1rZS20csG9W5VuM5aWmFcatAo86nm'
        b'fpnRZnBjQFYHGwDLrlOWWUyA+b8DndGFC+yCzmR5zJlnErmAz0dnwuaYlgmcTHZuDm6emYkvki0xGlV0tRRlkhcCqrJnM6VaCbm8UEu2xmTnashW4PRmki30c1ggNasj'
        b'cTNpJQ/ESEtuBOC9+C65xzRJ/fGZKtIIAvW2GLyRXvotMnF4w4Ru7NNSg4PJzWgAgOUo27i8P25x0C52A+H/THQ+D5LJLG4GIgd0ocZ/aeaKbDchUbl303O58UH8BEXO'
        b'1ZXVy6r/9su/bYhtvXK19UrYhLs/zJiUmt/6m8p3RhwuevnfP38YlCDe1fSq4mC07GruNxVHP4x7v1+a7UyVLaVk7cHzM3+efV7M/fonkevrDk93/OzA72MmJnHPZR4u'
        b'Fv3xb5PWb/hLZP1IS/jUQYO/0t7rEMtC/jbtwIi0tb9e9FaSRbb28ft/LI9aO2Be/tb5PT55S/LZxVeTCh6HHjD0eEP5zmc9FDf3Xe0z9fCafQcP/LTXzySpESPWqEIF'
        b'fv3yNAWb6ykhAPyjOHwJNwKTzD4Sc1ubRflY53fhFofKSC2/eiVw2YwTvlJpJ23k2jKncieQXDLgszw+iZuDBB57R3oBK741BgSrPLwzlO+P7+KdDNfMlUym38CLAWJA'
        b'k+Xk1hzSypP2EWrBtmUd3o8btTF4e77wXQM5kIfW8TzZjw+Fsc5FACe6h1YRm0+didZMJPv4KLwH7xWEhGPk1mrKcKo0wLNejoqhXHNonKgc38C7hME1zMEHhYvhGZol'
        b'1/BhfqiZNLLB9SLX8d7oWHp4ocZHMjUqHrj8oyLggm+NFhRQjXg9vsuY+FgQDaVjxibyvbLwBUF5dZ+ck2idACtF5jGBETw+Dn2/IjR9AB+vpoKQc2oyJuIjfO8KsoWl'
        b'jqgiJ9y8dv1sJ6tNNi9nsgm+FmUV+gWN4nPd8WU+ZiRpe5pO6Dtwtwe+FtNtzJB1jBtZo7WKQKrVkTH/IQUXxp5URxPGdD39H/PrxI+rg93IldYh3HDv/PCBHXnpXvz3'
        b'tJkX8nbeer8UHo8pau/vRu1ofc/Hvj6F4NW+yum9PRlRt3+3SzQgGOc/lUT4w8Nv9yduwKIW+3pLaVERc0rqkFVZLVUGq33FszhEURN9Zs7DlECMcWb0iY1EYN4j/sdV'
        b'dE9dVCs9yPkAOb/zRe82CBKDpPOYh9mLeMwPlwIBhjkUfb+/IWKFKMhZS8/Hitgw+i7q/7jv9JBRsn59OXbpF97bA9fZ6OcnbSEhIhS8jNwcwJPjuMHGDPuG98Lb5fic'
        b'naIXOT2UmUYPY/oH4JsJ4qFkB27+X/g8k09fkq4nmwF57Nt+Kr66YCo+CG+D0eDSbozZTBKv1mpwazppiEuGouQGtyQCNzP7S3wEmVzfy9tkcX8vb0xfNhuRUITUZsVQ'
        b'5iqRXoG2SYdr+WzSWGCc9YaEs1FY1W5897Pi+S+27jjeGL95CVca8AF/ZrNC3id9QsxHEWciPtqcU5yiDZLP3X0889LG+M3HNx5PvbQnaxc3rPurLzZxqCKg29jtD1US'
        b'Af0+IDWU21ZZgD10e0yGZbFE3ZxJ7s/u4WuRAo4ZTe4J2vCG7ngDVa4DxdxKFeyCdh2EiVaGoabFrhVkeSbJj8bXqTBPDpN9DPmZAcfvoAe/QjK5TV5YwBsg+fzTvGQU'
        b'IFkBM2MoorYQDAX19EBBsmEhPP2WhhgQjpizrnRvJnGHmBbokDqd17p8D4peTWdd5d4MtORg/gmEEvKuj6/qMefO4cCHRGarM2OycX1sFju9Va5+juyVRAB83uoCSGHO'
        b'v7bRvMeVH2PoZRcAqbxetCmwUGQQs0/pIfoRvXq+UAJhGQsHsrAUwkEsLGfhAAgrWDiYhWUQDmHhUBYOhHAYC3dj4SBoLQBaC9d3p5/h0z8Hu4TT99D3hLYVzrRe+t70'
        b'eg/9WJbWV98P0kJoCLhc6qQj1vfXD4C4UP04iBNDiUF6Jb2EY3fQbn63qEy0W7xbQn/0fcp4iKN/Re6/QqzwFAs5PJ7iJ9/1gw+FGpF+yG5JI6cfujsInsNcdcH7cCEv'
        b'vI1wv410v0XqVfCMcoej3W8x7je1+03jfot1v8W53+Ldbwnut0TXm+cY9EmH+NOcPvkQX9jNEG7opk/pg451P442ciw0yhViOSKYqaTgBiWDuQ3Qp+rTYPZ7MCPKADbf'
        b'Ev1ofTrE9dT3YT564zsCi4Ce6aYAf8081rucCXhLKII5ppR9cFHqPgmQPNNJwDN+lyxIOAk4EQ6Yq38xNaJXPNCNFM7jjzrqUe+sbwExFJsfTpILkT9ctYr7JvwVMYrT'
        b'9WuMtQifqyVt+ISIuemTeytcnvpeIinFkQGooFwWNrIvq6d92BA0KawdNlTxkIuGavRHVx//Sh9GyfAeEhs9k7n56Y8H1L0UvC5OITp87XQrl/nuNu6bSZ+efIDFMzN1'
        b'i8PHLruhfz7rAy74wAsjr26aEBuREfzHRR/1XBlf07P69tz3jx2MuBHyEz4r1PLbE6lvvZY1onTv/G8/0Tl6Ppz7aUCjpk/ggK9UgQJzVweI8YHwkSlyCl9Qi5BsJm/v'
        b'Sa4wBs0AIzgbnY5r8WV21CgdyXcrIM1MNzwQ+NNtwqmoCK/zMtleS7YLJtunFdPoAWJMWtdZGd5HUjF+DMtWRppwjeDyHh1JruCNaiEf5OrVXzxGRrayY8blMfiE0FNc'
        b'z1TqdxcBwkfdyEERPo6bw1gmvGU4OdyZK5c0ktu4BYQeskeETwZMYgz1OLzdTu8S2BqbRTYCaamjFwVs4/EmfJjcsFMl1Mox5CSuXQb8PNkdk8WoOtSHG/KBzGzNJ9s1'
        b'UpSmleK95EiKgLufmS/tdG0f6EETpAlBnEzSm7m4u5S49LuB7p3zhFe7oDTtkDBrqg4xNcbtUHQeu5ktHYFGc5XDzu4X62RXPa3cJVaqTrKup49NyMWpbvDqZ+yT1KXn'
        b'a74+Mde1l9/Hf1dSRLvv13F3AgSZ465nO27/9f6dV6R2cd/VWLUU3XyPrgQXec6h3y5NcnXp0UCP5ru6rmueqe1NLq/5zhXz1/BUd8MDslyZXdag37tdt6s6BaKiSqN/'
        b'3+1sd7M9qWSiLLNaKr9/e2Xe7emW+20v191eBGuP2gp/39acXvHSIrvFrjP5bWqau6k+M2lGl02x3/b+ZxT/XY6s6T8edf1WIiMb1Uk8en0pfStW1BeKBZrUXBWAPp7b'
        b'hxqOKVSj85Bxc5yYs9HrQV7oOYV+5TdTt1sfWZavU5R9XPwx+vJgn4L9P+izoU/qW1zxUMk7v//g+fsqzs6+z9lMtpdSbOcb05Fj5JYT27XEPIXtZfKi+1uCLswWNJt+'
        b'Jbe6myeOeHYP8YIu7O0FX3dpdKn8k8fw7/+rL+J2Fbmc67YHYigbPT5FsfRA9GYLm5iXl9dADV8Phkq5jsdG2ddNYhtVFM6/GS98m3mHfu6L+/F+fG1H86JLoldv6oTP'
        b'UIrQonbp+hmvqni2aGS/jfr7+1s0lEauhbM1qyPHBUHowmr2fcCtUWoNR87ieyAIbeATyTly/GmyTGgRM5M2VhuKSkyW0sXuTwK6Frj//Oo+HvPvndvrK7cSZt/bVaxp'
        b'RF56kl3wmNtl3X1Znfhv12vLupaewprrq7ciWHzRf1fe5pDvcyy2+Ktn/40bFtsRAIzkoIzYIME2dTq5g7fhC5C3ehw5jKrjqgST1Uuz++ELMOaVq8hNtHIu2cd0x/gS'
        b'vknOet0ERT+ZGpmn5lASrP4mfEQasgK3MevSxlFi9PpyZl0aE5wUh5il5I/D85il5LERq7q/3fvtxWLkSKftXSebcbvrciinoyjZsjCXWkw6QcjrWqjjpCmIavpIjXUd'
        b'lBc0BO1ScsqtBOhppGqAWj47MseY1444Ww1kuZx6ZfjP4kNwXIRo2j9HGj+RjP9cvb938abucW2rA7fm5I4+I19grfvwzDV7m35c2gfbf1U6JcM09ZWcuee+ShnYPWhm'
        b'1Ac7jv3oYFzOzLt//umrMYOm/+pPay+/veBQa1PVuwd+MWohXpHQ8e9fzTBJrjS9/9W02+WOkG8fzev7eVRs3C1dxA+7v/vPAAcZvLnxhCqA6UGTI8l+lxrVqUPFZ3uJ'
        b'yoFRbBQUrffIpkld7oeaWySWkeZJ7OalXLyDHIFdlxTnd9/RTTcrSziq2jiftMujnIyvs058Ygx1mW0Tk8uiOMZs4rtSsoeZi1CuF9YZt4CIDnWK8WlWrRTF4fPS/qNh'
        b'J1P0GGMmB522dKTO7jRw6IHPMH0GgANpdWk0VMVO6wR8s0Tl/t64X5WptGiZ1ej8HqzSY4vLisQczw0E7rSv0yBOAW/iv1WHeWxAVtT7q9Y6a7nND/fJW/d47/rdFAU+'
        b'uevDTvg6+nqy0bxSscem9Dpcdn7QmDn4uT9oLGbnXRLY72K23yVsj4vXSAo83v0RaUmX/S7Nc9CviOJDMh5Tm2/cVjoIDQoNYsIu2ylz8K650dPVs9XUVCWgG4+v4N0D'
        b'8Tpy1njh+TkiG71TU3MikSrLduBfv/TOS63yUTtuN97eeHt/+mbV/sGbb29s3phWn1U3eP/6xGB0QSub1n0Q0G4GYqdW4haQZag+BwOsULOVlWVZHOpXIcZbAM3vdy3J'
        b'07Xl0iLm9MGWPsxj6UNMYqao8pp1llVQi0s9jAbZZ6mZjsobxTeLhdgncrJl3wsP45PL7vP7wF064H/VxyNmW4hqpEwrQdc+4Huu/TPe0yPJ61zlSHKH1Bbgo/g0Xem9'
        b'HBKRu1zuALzTOPq1cWIb1bD//PnnPyvW6iINkSVagS8r/qzYWBb10RfFnxQvLnuo/6yY3xaXkui4+urV03GO1qWtp+O3xgvfOF/yZjC/+XonD/tM1jBe3yWnykWPZY7w'
        b'3OFWwVyImq1W9/CY6c4yQlX7/APTfveiUvd1y5OL2rvBx6L6buoTeujgf3nHCJta4tzWkv+dbe25tOQ2uY8K1LPJnsRMESLnZkoCOLyBHEs36m9ViG3UBWRBY8FnxVnu'
        b'pc3UfVqs0X1c/BCW98rth8VhuoqynNLwUuDkTBw6e1kW/jACtjC1MsX38YVwbQ4+hm87jbyH4i3P/hHijpAi5wWsHmvryYHLqsXUkby3x1R7FXApMLy3Z4e0TFdqt1j9'
        b'4G+x9ZC/LU2PGJY9ufoRNT5W32+XVKGCkXKnzTI1V+4I7pTOFxtWdAQvtThKKwxWViTeO5jQIS+lt9gY6Mdk4z0DCR0yvdEmXD9DTZ87JEt1dnpvscFhB5mU3q9Lt2qH'
        b'wrC8tEJHb3+lUYUsJzWQiu8Icl0fY9R7uNvPYznsRrvJoJKxEzorpT5Wym/5uk85r0NGP0RCq+yQ0zeXmzuLZjdZsfYSrCdpzQHU27LEspx55HdIqiosZkOHqEy3vENi'
        b'qKTf0uU7xEYo2SEqMZZCIGDCxIn5s/Jmdogn5s+YbKXuS9Zr6Al1CF1Kur5UPmAIynmHspTZZXM1sjLZ9+SRNz25uUTO6r03V6nAIx9Bq7lv+Ncl0jhdenxeFBJ8Y2rJ'
        b'YXzPRm6EWiWVCxBPznBR5B7Zxg6e0vqW2exLIY1cl3OIbMQ7A8gBPmQF2cgYW9hEu9dGU6PQi5GZuZqs3OlkSx6+GEMaYrOnZ8b0JneyY4HbBY7M5S9FGucpJpIN+ACz'
        b'jZhK6qWkcTqt6XBZNcqdhtcxS3ALuUguJgJuv00NuLmRCDdGRDFbbHyJXCLXE3mEN5HdKBElVpH9rMjIuamJ5Aw5mhTHIy4S4d34NmkSvgb+gnSh+6IWDqWkygt5cikz'
        b'gBUjx6rxpcRpuC0pToo4FcJ7yINgNvTUxfiGYOWbLIaBzpaQKxxpxFfJNTaXYydFo5no9aEorLjkR/pgJPRuc4YxcSk+kxQH0mYUAnHwlpQ5WS0ODtBq1BrgSxunkIZc'
        b'NdmWw6Fe+JR4/BByktX3C9tgNB5V9ZJXFfc/OdghWMSTjbroxCR8MylOhLgYBFJqE7ntYBYUZ0nDvGiyBTiRI5os4bwsFNeLStTkKqvvwIpeKAaF5QQri8f8RLVaqA+f'
        b'W0oOJwbgB0lxAYhTI9yEDy0Vzltv4v10tNvpN5ZgHo8jcQyH74jxeVbb3MxxaBX6RhkQVzwjd+wwobbnkxISB5NdSbgVZDMNwgfwYXJUmPJmchmfjE5Qa1TZuSA9Bcbz'
        b'0Pf9Y1ldS+VatBvNXRwcVrzo88H9BSgk2/BpfCURn1sE1cGSxyJ8EL9Azgi29Dugo+eFa0hgnGRHmBS/wA8lR8gdVmNvFfDd6OUI6uknTrAjBlthEtKWGJ2clILY1O3p'
        b'j7ewpcDXlP202aQuHVNTie1aZq4WgjeJxuKGpay6/QvSUBWa1i+0uNg6Lnmtcylq8IMpiTrSlJTCs9HuW0Y2sbNoEdk4kbTiq7RSUpvXCWl98W4x3maZI5Q/OAS/kLiQ'
        b'HElKkbLh7dfjFraUq/EefJ0WLiYvQHlhLUOqRKm4rYj154YxHA1DL67hUHH/WyopYmfJJbiB3EkEEbEtgUIujHAvblMz8jmPnEROyOURaSLXJOQqR3anLGEwmjdjXGI0'
        b'2ZkcB/OSQEH0KLku3NFznzSVRGupXSGIoCcjpEa+z/jlrMzc/uRSIjk/YxQtlAp9n03a2LIph8ynQAgQuA1fBr4hQTFGFBZODgquFhcqyIlEspvsH0U35WgKIafJBgZv'
        b'fcmVRVpholTUxJ5cn6oIE/XoSXYIKripgSgMtZbwxcU57SumIsbyl2oHJy4MGJWEWF1NowayVqYbyVXoA3Wp1ErQOIe0lO+XQk474R2fyU7Eu3SjkgCm0qEDZGemsBz3'
        b'NXiDlmxbpKXHFbyFGz+Y1AtupodWFSRWxI5Kgi6PoVB4khxjYx2EL+NdWorO6ugRRnZPaXc+EO9fwjp8vvtK9BVCMPri2acrOSRMwFFyVgIC4g1yNC5JgrgMiBmIz7JF'
        b'CsGnK0F8gGUXkeOwYCJyn8MHyboMVt07E6egOvR6hEJZvOjb4m4CCPbEZxS4bTjeGpcE6GAixb5tKtbnAfhetpbUkEbAK8DTLORiVZWsnvygPigOhUUGFhevOhSfKtSz'
        b'lrTM0YJALSmFsYvFHHRz3Tw2w+TYDBs17g2bTE17V+MXmF4kJAMWjnplzMgE+Vg9W7CSI1tyYwDxoBmz0dTwgH5mfFzYXnXkFq7Vwqw1uTxq6XHPfh7veX5V5xXaI4BS'
        b'idGtGSJUnNMj1iqgz2RyEp8ijVKE78wE5BUDeGgPc2XNl4Vpc9SzvI+1gNCI0XB8XuIYjvcJSGSjBdeQ2unJcSDMI3KLNInDuQXzBworvqkQ12ityTNJPcACaUKk1TGL'
        b'1Y4faMhFrYacxle9PcM5NDxfYhxBWoTeAee4nhyUo+ShsFcoH3lppYM67uEd48nhaFKL7+B7sblke6Y6mwmGWfFiNGKmJIEcULAxF3N9URKqKJSEFY/hIzlhzOQGvjSR'
        b'HAwAgNgPPYH/3RcytBI5gQ61VoMvedfJoxGzJIn4tI2Nalwfck9LzuAH04G4Mp/jeyMrBKPn7WQT3l8AJLleMn0s4ldy/UX4NkuS4DN5WvLCjFnCVJxG5Foq3s88z3HT'
        b'0FgtPrrY6XzvnohBuFZMblQPYH0OyCcwEcEoGPBHO/XQ2I5vsT5PpVd5kwN4Pd3amqw8KJqlThCjfviA2ATcwz2mfpMpepCDIjQM1yJ8D/4/31/wQK/BZ2T4XoRXWR7K'
        b'HhRXkmurGYDmkBP4GqlFKFqHjMhYPIQhk9FLplEzziX4BXd/Q7uLFpGmCay9okjoUqOI+tqgQWgQqSlly052SKC2WyujhcvLAKacZhr98XUx2UZqyoV5vEmuAbNxUAK8'
        b'x0qE78J/stfCKs5clE9qAcW2zEOL0WJAyC2CR3U9OYs3a9XqLNwSmQ37TIQbUffxIsCEO6YzxADsTTu+Rw4q0GDY+vgavUb8OtnMBkPWTcC3gVkYWBDl6W6DGwey7szv'
        b'mWwj+8m+4GDAT7D9oKozpI7B16GVQSgCKacDDlKs1PZ0uuevI2ftpBbEqPVLkAVZRiSyde41z6ElbeQKvphJvfDrtPlq2lOk7CcmrbPxQabOfG/JMO512LLKZWbFF6lb'
        b'o885uZwdpL2CalUBtd1E1aiaXDEZv/7cwtv+Dtzu6wf+seDN5y1vjQ8L+PNvHA+HVTbeOr7pTv/j7/z9Fxnr9+7NmPentnfmLO8duLt90vSBh3sNObU641vZby0//NV7'
        b'IuVf/r588fNjJr3yrzHpRx7WBd75wfmzAYZffhu0cmjfqA9Gdrw5t+nYZz+MeCOmfmaLtOZ3n+u2ah+OXNPSsuj3/wjt0X3xoW8rNwx78eyr3L6Le4t6nKx/7ReyFXkj'
        b'wvKn/KDgl423Xvj7zFvmHqMObRry1o4zjc8NSdxxL69wyD+VbXlDdqa9vGZkwKSQjJA0Y21/zcwjvdL4tE8/3P/ykpfNNSMn5fUcPWa49c60P9a9/PzLaSP/OFkT8en8'
        b'iNszd/x0yBylPK/n5EsZl9KeD78dclv3XPrJLcaDdTXz2vvsVDV8/V7D4IJdK1+IW/LXs9sjm7+8Oqv029oZRccfGpfxbx16uGLjA6JamFVec+vGSemsOaHTG8J+teyD'
        b'vODZNa/+oc/XCwOXpL92rt/DoN9ll4/JLu//50Xvf3C32+KFjYvk7e0nH9WuSv/lrzd89bhlnuR3H6a/+ffq6hubX/13z8tfLrhS/+q0kR/mprVtTr818mb4l6t3BjT9'
        b'mbTs0x8YdDr9lYbTuDFj89ldj2OO2l5+bfLCD998b9+Qt1Pe/vmOoqx/jf7dnR2/+9fNwOA10V9qxv114fuh/3pj0b8/tI6tXf1Sc0j1t4/Uk27M+PjCpHfLWvZlFpxt'
        b'yrv+6NtBD3/2aOj1QlV3wdu5Jhqfx7X5080+TDOoEYIDtzExfC51lI7OIK1Uu87jA1xuOGkRTFyP4X1RwAiBHCHFewOQeBIHewXYR8HIYRcQ9dvAud3FtaFVCitszvrQ'
        b'pcGBUhSBj4os+NwqQbd8kFwZK8fNMZlO1XKyHXUjd0T44gjcLNhibAqJc9uxAbFqEwzZqsk1dn6D1w/oDbjs1LxYp8WsjJzk6YUaZI/gl7Z1MFDF2n74kKAFzAIql8vr'
        b'Y/FGO+U+h5KmFG0ePphPR7eUm5CG7zNlcsYcfMrle47CRwnGcU24XTC72wVMcKPgZ74AEANzgBwADTKc0Wqb7LYMWYWPUuMQ0lrFjENirGSvoEgHnnmnl3EI2ZXGHAfJ'
        b'puAeXuYcdSJ8dZLLnIN6e9CKQsgNpYc5B/AHc6c6jTkmkkbmyL+ikJyi1iP0GAOvG0pFGWpp7ZyD6DQJvtF7tNDkoQQbrkl8Ql3qUpbiuxlsIsPDR0drVORaRraXTyS+'
        b'rGLrYCKHQDapXV0k2I+4bUd640u+PhzwvW1cO0Q6vaDEWY6QW4mD1oZrenJiLpx5oVOfcupT5/7hw7kuPxAn+zRkwDDnTYJB7Jeq7/vySi6EpVP7Z5o3jJbnw7gIeOc5'
        b'2cPwntXBnboZ6I+nXt9KFXHf1yuPF0p16vuvUx6Vd5nBrHf99H3Llz20V1/8H8czxaDwGS1UI3ErBjmmu3gmb7yu53tK9KTuYqSguxD15JF4uZyjh/JL5blI0BZSnmDu'
        b'OISBZ0V4I946EA1MjBcuhblQOQI3Mj5I3Af1IXdnCbwHcC73EqHy/uUJKAFkpg0Cv10iQ2GyJikCeSNRFo7YEd9EHQghiqMiGpkXrRQY17UzVnHfFAI9jdOtDMxYLTD6'
        b'wIAdwU2JIGQAB3sdhE1UCizDUdZiopHcSEySooqxIDMiA9k8hNXT0kuKFKveDkDK4pgZpU5ruIPyMKRc9bIUVRXH/HayVujGiGkQKd7IQWTOn7OyhJxLkoJR7zHV1G4u'
        b'Z+N8q5Bz3XiIrPhUBJGKF7P6Cjl/MQe4gorbPAorjhmYaRFyVo+To4i437DIXpUxQuRlO3QpZ7qI3o1zybQQMXbkOXysL2MiZ1F2m1whFyRLOXxnPEhLdJ24fnhzYtzA'
        b'xVRNM4xeQLpnujCh5UPQpMjPpNT07kPRaifjcAufoXezwvRb8TZgHKTkGquFXMV3+5CDQQhZivANhG+YRrL4cJCrG8hBqEWVj28ifLMwny15zykgZjQCLGQEqZH6/zT3'
        b'JXBNHVvcNzchhBAgAm7gEnEjCIgouBQ3FCqyuIBURYuBBIiGxYQoal2oK+4oYl1wQdx3cF/bmdpX++p71vpeNbWv1Wr3597Wrn5zZm5CgIRi+77f95Efk3tv7p05d+7c'
        b'mXNmzv/8URlrIqdFEk427O88BBXwmdCByQ8d/GvEMFoHH9KLx4jwIg4dx6USmlP4aAWCjFDFqLZc25nEFKad++bMNnb+1pFRdKkV7UU7mDkcpUwOwWtRFShnIlwq8laF'
        b'UAAQujjWAwBAPYcWcUVFJDN6cwtxVR7aT7bkw2dwM9B5tJUdf53ozVV0HVqunMXNwpWz6WovfRYnB5J7yWlL70XeWsWmmC8dzIcX5ot4ESd697H+VsR7IhPE/qzQvJlb'
        b'mpiEw5QL+0+71iVx7rXIOLd7J++1Kli6hXvaaWTQSF+31CNLVxv5G5aXK7utxG+76RfeuPFkwKysLf2bj9nX6Wpqi3Z+6+/GpgT5bIyoKh9Z8Fn4qA07Jj5VbPd6FPrh'
        b'z6le/0lt3u3ZT37zh1vSZkt2Xm/HD0n9ZXPE3QOj1u+sFtX0qIn7++YzqXEJQ3Z9KPYb+97xsF8+/L58x/Z2mrzAi/O/e9bx5c/LB7Z9mD30J/dv37kn2W6+/NsbsrdT'
        b'L6XuDb41pdPEhV7Bj0e0eStm8vm9hvcudimY8MvPWzUlPp1+jB8yc1HykFjvi4P+OXjRxndllotfb4pb0PPVzCy3EUN90/v8c/qpPcdLS3KeBExol/rm8I8u/PT0SpJX'
        b'4Yfffftp/+Yzi7u95JP60Z0xhgXPH4p/fDLnwSOxuhVdVo7qgfY78+XAu1pYl5UHuFJ9ZI4KIoHh5d2SQoJEHN7US4aP86hcEUHHp654Pj5m0yM4vD2SYW6IDUCv1uDT'
        b'lA0IoAxiDu3BleDxmYfW0SESncJlaTCaJoLhCRGeYe7l4jjvwWJ0CJwpmUZ0CJXOQPuHB2RQqH6JiJPO4QPwkkwWWWclWszRwDGohIjiSOnyHk5ViNTcHJCkGxGzBG0W'
        b'40MitA0tlAvqUFF/cFchw+0+cFkR3FXmoQUUfdoFn8OHa/me6PzlQHS8xViJP9HHNjKEarVHjh2TE51HGq317gyRCcrxfKbFLMC7o0CNwSf62nxcoyawytjdny7M2+so'
        b'RKurZDpKDrrIIgocmqMCpCmuQCfraAwitJnqMFO8R9RVYTj0RgHTYVrig0w7PNWFWPvLug8LDg2FuWoRF9rBG+8Vk3d6RxDjZtIT20jwka31jw1sAR6yufgsw1NtB19d'
        b'iJoV78Lh/X0kvAhtGdKRPjJUIcObapEO6biEOga8OpZ5E+1LRAcbuiCg3ahMaIaCD0ISPkNbWZf+eBGRV1BF0cJhgja6F+8shAAps1zmWHWyegoZKsmkOhkxPi/S6pGj'
        b'heiw1R13OXCQ4aVMpcL7cTXTbY/r8AlbACWi8la5jeOJarop0+rV0KSVMgk49VHVKquOaqUwSkQKnoZKICoQKFa+5NOCfFqRD+x7kpSn/zxVkbxZYAXykdyTtpHclbeV'
        b'8XKRnPcVyZ7LxeAfIeMBaEaUF89a5QWKt3N7a0TmWi+4EyS531BP8nW0mlqvKFI3oJOQr1L6lUS2NsJWy3ogMerra5wJCfX/pY7B4BNskVl9Q61bsN7EPCopOgx8tajr'
        b'Bl3Ipwu/dP3PokgfOXj04MT0lHEjY5ItYpOu0CKBsAMWd+GH5JiUZKoE0jtk+uVfD41hBMK6YKiuU6BbcUox3+xFwWCeLuTfw1eqlMlc2TOWUp8Xab2P5BHfTCIE15Db'
        b'BdeQSfmfJa78TzIZ/0zmxv8ok/M/yNz572UK/qnMg38i8+Qfy7z4RzIl/1DWjH8g9Sa5/Vd63zPIk5TfyqXVUDoLn9f7VfshwQMfdeGUKeLx5PU+3WD52sphYxpUn59X'
        b'UuZFeWu9rN9a3rYlXuHqJtF2IgozQDe8siRaV63MxtXrppVT4I5C4Or1oPuedB+4er3ovpLuyyiXr5xy+SoErl4fuu9L9+WUy1dOuXwVAldvS7rfiu4ryiTaziCXtvVm'
        b'vkwK0JzJHlq/1tw2TwCfCPv+1v2W5L9KtFKk7SIA2l1pECn3xV6LlVlulPGXMvCS39won66Egn5k45VQH9oOK0SLmaGgWOxBzIQAbUfKtdtM24Z6DncVuHbjk2J+Lq+D'
        b'/U6x8r+SnxjRrioQaFGA/UqTp4V3RF+fprPOTlAKQNAFwiuylZ9hyjcAWzcg5yGGMSMchRjKuoJCFsabwujrhZY2ggur2tXiJjC3AcGRsElXlGUsrCpQHWmzplnEU/LI'
        b'sVydVm/OJcdkBUTy6flGrbGW7dchzW7dcF3WSOluxMCSC8vE7rZwXU0l2l2gFt9+1GSiXajoP020+8c8uw04dR1GEPiTPLt2D8QmB8Rab0QK8rMzGfJUGkNBjibEkSh9'
        b'VZk5pMhMGtG8cdrfxll/HTD8vkCN/CHrL2mLLPjz0NhUlUGTATTzZNM+nrY6tF6kakZU51CKuqLTug0Mt6sKB8ILgpD34Q84h53xCzsOMeGMc7iJ/MIOM63lHP4L/MLW'
        b'd55VO9tT6bXCA+v5Rw/M2lEIEb+FPZVRl603kRomHRTpx2hzClaZhcdmzoPI23+KxteLGc4tCpQw8dJntdv0hNjWccxp+RW81sZni3bgCkdEvhjiCdvFd104SKFU4Cqa'
        b'aV8vXy4Q4BIt8yaIB40QuIGL0f6hdiy5eM1MB5lSKhv7fLcWkFzRaTZzEhCgAG7gwDeVs4JnhwncwN3wNnTBMTnwofZ2Fom9uOgUWuKOtk9Ipdl+qJYCY4WyoKs22DCq'
        b'FWeGLj8BnZ7iONc9eEFct2T73ObhVW5oHd6CF9L8Wkoo13BYmHdRwvbIWUzMJDyvwDFJMC7GJbVGYD0xT7ijHXnJNNsUrTvnS3StzwI0hqX+ruxZoYOj8U5H+QaiqtlW'
        b'I6dOnmfQfndSaGlH/eEvjvGm5SST0m6VIe+f9eAHK2JGzfr91SV75vkFFreQRd56mxe1ruS7TG19VZ1/wO2gaWvuUe31VgdP11yOTU1od6ps69fmoppF/2h/QvOWx8nY'
        b'G83Kb70z4P3ZT7tUXs5Jylna+9GmOZJ/3m/96u3sItM/j9zZ+s2vKeff3vm6MeZ00c0vdn+x8vj9z3o/m/Ns9huBE4cdmrv+m8jfXtOq5Sw83WlUhY7VMzuJzYmWxPlH'
        b'4MXUlgvF8+Y2cCKXoMUtZBF4GwsPuAOfkdtnwnw+2uM3JGgTOoYP4+LJ1rWFLWgtOZPYQkvqmLHMiN03hIY9yRzt302wjaToANoSyPcswsfpT1OkgBKhJra4SzY1sE14'
        b'IbUWO08PsBmLkj4vg62I16N99D6lyn7wGyoZZz8PwCYByvBharfhxXjxKGK3oTdUtWarYLTuCiwEr2Z8BK0lFjtVY2FaIgTX4BMmOrtBjiRQxTZEyiWiBa6oAq9GO/9n'
        b'doANZQkRI2otPW6uZ7SngLK0UgjLBSJh+z0boTBRPxwTCr8JyVuQIEgwJG9DcgmSdzjuj3l2ZE3JxKPOLanFVtf84tqPytGceUPxXwSkJ0+3aVBOoXNjiCwMmFlblh2v'
        b'MBxqhFf4hbGZinQ7dcqpUGOtQv3crp4EVDn402y+gurktNw0W7ntWbl/jc9YuGdJOlGYnJb5qq1Mf1amnVL1guUtsJZH9CKn5Wls5QXWak6a+gDYF+dMthEYW3UVpxJo'
        b'bRL4wUyHnTrzp5+szRJyVmZ2nTJJLduUILsy1TzDUNOZE5uvbVKm2E4U8GGHd5g62w4nCV2mgjAVvGC/ymkAZEWWwubR7tIkj3bglXXxbjLrlA74NptKOkVPfhHOKXuO'
        b'qQZZAueUDeYcFKwKssdbk30K4SYn2TPmUAWXiQFEJE03Am0F9VMl5+eCKcHsbogeJ4CmNRn55kKByslElFZndQN/QJuigyrR6rMoqU6hoJTXvSmhvmlQTFJt2UJsPAf6'
        b'MPzF2UigNI3Zdz0i7awaVaCVaca5fWNfr0x3b/CiqgIHZxh1mTl5QHIjGHs0Qp5DQWvbgcmkz86jTYFRyTTgMzOp9PZ3pSd2T7YTvhqrPdODPuTIvjazBkrqoQ6GmRIr'
        b'JTKcYeNEznRmidFWqafXA60W1F2fvk2n5cqqe0Nw13qd6X9HqhUIJFKU/kqtCgrKBVub3M6MoKA/TbOlCqSUWiGMmepFsm6EUqtJ178owZXKCTGXM4Kr0KaJUQcF0ijN'
        b'VaCN5qqHWpXWI9w5TZU9kkR4jGYdux19HhWUstcPTUwcNw7uzFGQXPgr0MzIpSF2dUYYpoIph53NRLYTKLxxgRrl3qo7YcLelu7WN8WhWEwZsmfsIsX3DHNOvmaPu7FO'
        b'H9m9JuQoeSPzTHomVH6WYy4z7WTSMmh9wAU0zrCmCLabSOMEf4PrZGKiM2f6zJxCPeXqMtUyyTV8Z53mGaLqAeTYOjPpXG0ZkBasVwlVRHqoXPLGxYwJSdEUZuhgNtIx'
        b's1iIijQXFg7VYM6dostxXP8hqp71TqOlacxZM82FOjJyQLxpVWq+0USFcpJHr36qweasHF2GGV49csFgc2E+jG9TnFwQ0U8Vl6fVT9OTxmwwkAsY352p3p07uTrSkcgv'
        b'XkG9HWWjtxMr98XE6uMovxerl760Imur/g9q3uHBFNaSYdqwntwv3BLtbz/LSO4mEOrWJpMmY6Y5W+28+dlfrurd2XkDrHNij77OziTNLK97QypR9mNE/WwinWUT2Vg2'
        b'pFHY7q+RPPrYn+b01vrWyczBfTkd0ARcIOnhhC2qDxCdlPSt1q48MJmNsU4H7FrYIZDbk6GQ7REdJzCe7OryyD9p5ioYg/o4p9esBSzWzSa8XjbhjWZDsY11+BYDKcni'
        b'UBhvIpxeZsNCsktjxtCeGg6oAslLLjRx8tidV4PZCLyTZLQYImwFq+x0u5gxo1WBr+CqHCN5SYksvZyLYgfDrM3MdlgQypqVaYrZaGooVGPqnjP1kqqSTdf8bCra4Dor'
        b'AE3TYSiwtJ8qCb5UaeFhE5t+WTi7LJxe5vxpWBGrggop7IPp3Fg7oHBWcgl8kRMbnue8FxumMxrzuscaNWaSGEK7x+qJdue816KnO++rIB/n/RMU4LyDaqxk0ivF5BAl'
        b'jPT9zrsmKhvR2bSOxXBWeUSL1ekKQbOAb6JgRTaq32XkF/VTwWIy0Z+yQGslB0idO3+ocBHghNlVGoMKdhq9IlNfCC8kSRtV9xg4Gs5kGzTjYNDTQ3r2iIwkLc25TIBL'
        b'JgLBV6MtMktD7jaWdCqNnUSRzeQJwZcqLdL5iUI3Z6WUbaRFWzHX/VTRZItpwmnhvRs93/Zq00vqrvA1Wt9WJLdwJXs+zjtrwG8TFS16cBJ5PM57xAx9Jskwbggp2sEb'
        b'2QB9Dev4DlfZSjsC5I2bNNdlUvCVlzI5Cm0dh3ajHfG1SLlmgxhWDi9zZRe9BtBWTnVx0CSDLFTPAHwdJ8XGx6G1aA04g1EAnwKdMoBf9t0UQP1ynCxkUpsBmdT/ONaH'
        b'5L7WpRMu4wDUh5YlMkxtqQkts4NFAyi6IhUfCsOnWbTObq+JnvHcIGVPTZp6uokzh5CDaB4uQwu6kQuA3XEEOBiiA8MTWZwkDjzmRnN4WeuiXm7ZbioKIfJLh4hI2/q5'
        b'FGh8Ph77g6GMMwNMf0a4f4NwSCOSaTbD2DJFHd7IFWiDIh6/rsZbg+h0of7qhb0upptk6+a118wr3Vu+lYQmKRdk//D849GDMs894jZHzQy/rX74mbuhU/TrVZHKjf+e'
        b'v+Ky8eue8x4N/uRazclPKvKz/nbK/T2fMQk/BLZb3j7Zo+v4yZVTpf4nR78fcuPdNbcrr95Ny+oz5EP3tK+vftqy1fUIf8ODiLO7+s+w7FgZFbL5XnjOUcXGk79meOy4'
        b'9NHVI7vufXsq+2jNga3jvynqeKk6ofDa2n+teOvxOtPACeh532RTcUvDg4D3nj5L6hWd8kGX4089v/8t2TNq25m2OfnlXz+9kvZ7dcdP9he9869Pfnvwj1fm1hRFf1a1'
        b'TC2jfoSZeL0O8CJatNgumvIiXMG8KXdo1Gh/whS0CFwpKVwEbcPL6FJUPNoo74ZLRrSQx6EDEk5q4ANQRVu6lGTGq9HqRPxGw2UzGdo/vjAMnvR5dHgsW0myW0XCK1Gl'
        b'g5WkswJXCD4wrGf9+Es816oNC7+Ei3ExXe0aPQaXmdBBH7ShIX8hqplUyDBmIag4PiGOPPwtPvxoURDaqm6I91D8j+Kcg2McXb6Khbd4rv1HNgIQIBBUrxNFc7D4PNT9'
        b'kC5d8SI/+i2bxz/n+Ta27ZkK2yqNDdAhBP2onboGp267dSu3F5JfLbHLhOZZF+4x2dHiVcAaB4tXdUR1jveg0Z3AIYlbLLFFd3oB7iXjVGjQ9v0l3Eb7Bv1lZ9Zfqt1c'
        b'upwQUW7oYIlpuBCtYjuqGGgyj4qYiY+EAXyVNCzR7PAwBgcBH/xZRXifO9l7heuAFr3S0pPh1PEafC45IhlvDmOY17MU81pOCyrxme0Txz10AUiHoaMLw9fjs6gS70WV'
        b'gwG7wZAbG1E5c9w/HzoSH5cC3INBPQ5OZ9CQca6TK8E1QTXJcDk0lcEvuNbNermJB3GA3jhTGMq8+5FRGR3B04OK2XnZAvgjz0PRmwsDSIfhky5+7MyKOQrJMXYw4a3B'
        b'U9iZ1Xnu8vWiQI5TTjL8NrMDO9Pk4j5sLc8OnvEoYAf3xEhV90RUpODyYTHs1tAZ8ejkkX5o+ciRHCcayqFi4P5lQJYzKWhZz7CeOUCsKMJVHC5Ga3AVQ1eXoLNobfJI'
        b'DvB6u/AFvBt+XTqZDSf70EZ8gAJF8M4cihWhOBF8dBItk0fz0eGeYRQmQjLaBVi30y8z0MQSbz2sF3Xg8KKBHRLCGHynfDJeBjidcA4fah0ehUtZ1Z/FByIp8iOEQyel'
        b'IfjgSFZ8RTzeACgPdACtYEgPhvMo8GeBAI5HpCWPjB2jogHDmktJM1qXwgJprEJ78SkG9kArxwrx9Zfxw5ujUgbHgBp/5CPjRorJyzRpkuH2uDxWueYMt+jjPD2ouOIz'
        b'SMC4bMJ78JZkqFoOzx/Sl9MEKGkWZk3zjHTxSGjOUffaTReAQ1s90cnkkXhVD7RNzXH9Zrvj7VK0kP42fhquMnmgLZKepNZ4tJ+0O3wAX9CPfHeexNSZVMFWZUpuaTzA'
        b'PhZlb65K/Dlh/MZrj4O+uy0JPi2aMm3gUN8OOzUL7x4pWW1UpN3JaVP1edXQ4KD4f/+69bufvnw0vLMuxXjwhPbGNXH/38r2dTkY9PuS6aVDU3oUxe3cvW5Uaq+yH0af'
        b'6XrlnfnZrz2Ttflgsv+2H3ctTXv65KUFx/9uGZKi/vBlbYU8cUGxTjH408kx6+5FS6Njo99xvXM6uLl7hazi9x140fB2b4f899ctpXe7v2H+ue2Tc8qI8MzNY+8/2/2w'
        b'+6i15ZkfpPS5VLX36k8uuV+qNcW+8X13H++an7FBVFzxbY/Xm3sfqDmuW/vZ+9W6XRMXmD6fUhL/75Rfz8RdvrjhaUGHpPW5Xqf6hTd/5V9tNu3at+LhsYoHty/8Aw1s'
        b'HzKrdPatd0O/Kq00eBVHT+V7bVD70vGMjFz78DZhQJuAzzTmGYEOoho6+OrQRXwYYkGqM/slkp9l+CyPSvEx5gaClhSg+d2Go519ExNEnKSDCFVIUSVzoF8qRbshZiA6'
        b'5W9HilhNfqattXwaXg2YkQC0isFGGGbkNN5NgRBZGbgs3gF+VhWDlgS5uCmb0/JFqDgdfFVW5lB3E+psomxJBR9NBK9mwUfR9igbmKNMSYtPxBdGt41q6FXjHzqUwlCj'
        b'fPAaIGgnlRKRbkWbDMLb2Rh/Ogzvtkd5bEE77FxkDpLT4DXwatWBKCahA216SStcw9h5ysfgI/ECOgOdmsZQHp5ovji6pYg5upSH4Y0Clxg6iCvsMKFH8UqGrtgYI7Pm'
        b'0SufYjw8Z4uHBr7McChb0CYKcWB+MnjVlFpXGTeig1BIzSm0+lXqc3OQKNvUJwc8csYFCgAIVDOHoTd0ShvnJD6MztIC+uSH2GF2OuF5ddx1FtDI6P5op79Dn6NhWjJk'
        b'qbKcOKn8QeBASghDNZVpDTQVSYFE0EgUIiUvo8O8UsCtArhCSeEVPOVN5m2fWqAFhVd8IfWX3pO3IVoOz4AXSuqQD876kmcyN9mPErlAhkbVhQY0a47lr0e4JrZSuhXb'
        b'f7zXOyVesy/LBEqE01DDf5l1DfQUc309xTHlmGuSGdBk6JhO54BxrKunQOFEGcfwArydxn3RuOLzafiiwCEm8IfhzbiEjR778VZVN3yIXAI0YkXoAjrLBr7daHEB8JaP'
        b'4DnKIqbw1y9p1V9iAseH01fC+ieel6NBiiTj3hP/knsOKN60qWZ/n1P9lmz7uPiO6ro8dPqyk9onze//5/oE98fNnq15bWDGfeWoPpre699XP/kyOqGXeNbRS/PalwW0'
        b'cIuS/W3U631OVH26Ys9HfsWTovot0b0eMuGbnjMev6M50KbvWtn2iV+ndh10pGDeBf21k/eP6Te2Rp9ebPNr9PlDzaaVvWvclv/5zamb9bu+WbXx0tJJdz5Qtrvnd+bj'
        b'tMOtu1ZM27pp37denicj/fsvUHvRvkbkilYSxWoprUAridg2XM1owhZ2QAcVRNOoJRKjNGJoK95L7Z/srFAbSxg5bZ40iW8TihnHmAgfSLDRhKFV3pQpDGjC8H4/ekJ2'
        b'ItptIyFDR9FJICKjLGSRXvQEI16Cjlt5xFA53gBcYsAjpkabqfDERCEWsZVHDG3LIR1lkI9A5IVK0YoWdvFv09IYi1igB8P670hOs1GI4TdQNbA1dkBLae+UXegqEIiF'
        b'qlGljUBscA/Wd83DF1G5jT8Mn0CrpFF8ywFz6K+h6CRahbZE1HKIUQax1IH0VyUqIUqZjT8sdKI0mm9FOsxKWp8TOgYO6lILZqSjEtprYmRvy3uprexhU/EuKdrDB/cy'
        b'/U/IwyjDFe3Vwhr0atzcgJAm8YdBH2HjDzNO5xpHfBXVKbs9OWbq1KBH4opbfOyUL8xaHuny6qI62K4Q4xu2k9Te9RFgMzjOHgb2JiSNOyae4WhI70JdronhuOpRgzX7'
        b'S6ZwE57RBZJ0gJ57LMe4wJRSBWXuavGcV/85JjCFBMYXyXPJc5XYe7rsJT8RCyG1DS1GpSbb1IML56FB+/x40meW+qlFSfrEt11EppZEA/7vsvkxK1/Kmz+IaMAtj7x1'
        b'o1WYV+Z3n4mrHja7do9TG4vTe5WP7pQy6pa2VGr85v2MspxNFfm//+3XAwO6DxkgiR08sWLVy78sPjQsK3vjpl8UH1VvL87uMvHluWdiYseWS55fDv9gYsWP8btVGz79'
        b'Zt1/+JgfPL5ctTcpU1e2c/qDVg9fH7Ky6O89dp/7fLn7gKkfLpIdvf/bB7O63OyKTD+M9/Ifen7Vu1/5X/5i+5gbAS2855ZOjY2okew9UpjR63p03Ezf7jfXH7tyvfz9'
        b'2X0fnL4jbn/z8+RNmsUJ5zZ8EPuJ72PNxKt7pt4daXQvmx12Zs3uzl8+/2Jz/LRLbTNWDb+17oMdPb+3xGbfT8jK7TD5Y7XngJNunnsuJY9Y4fc0evBzd96s7cFfUYtp'
        b'iBVfv+l4GVFMRPgEru4DKvAptJApYZWZLvUmf/AhPZ3/2SOjap4EV4Y3nMppT/pGNpdzMqLhbIz//50m+MIJ6XjEtvfQUULRqbL0dEO+RpueTjseYBji/Xi+l0gFkzzP'
        b'pTxM8qj8/Hx9g3wH8l37iehkUJSnuIs7N5ef1kdkvGF798QWPj3dbh7H7/+DOhAZb9peXZAU+h4ag3jQVw4Yy6BRuOGNPmgZtUhKRiSQcWKVK9f3Vc/W4rboUF+9H35X'
        b'ZFoFfUD/f7ct6QtB5l2e/3hfuWT1Dd/it42dDk3aWf3Se1VDZv6atmCT94Qry7tMrUzwWdHrSfzsGXdKsyuu31mq/u1ws3R95+DrN5t3T9l6efvQo52X7M81JadWDveK'
        b'7Dbh43vmm0s0fPH2bc00V7ctXDhkcci0G5/P65j01e2p77iIXrlV8LfMr9aOuN126Nyna+88FMtGB97Y8ynRI2ifcaRfRxiJR7RGu2BeGgiK3VE1T4zx+c2pQk4acine'
        b'HD8CL8cHQ/BRcuoIGLWb4XMQAGdjALM99uJzelYJoLCDgejKoapYT29xu0wjfatMAfhYfFxiUKIrNztXKuFlaBFezAzCLXh5K7ysO67ENVJOlAzAg3OT2E+n0S60ghiL'
        b'63CpCyeKJyN+AC6hkke3QZAfXo/WkhF9eSJgst3VPDEQlxI1gyLeq/GWSFNc4gA833aGPI5HR/A6T2ZPVsknx9PuksHh8wZ54qXiJFLkEioy3hqC98bH9ZlpWy/A1Z1p'
        b'1uNHkM4WFNE8tGuYoGIpfHh8rBlazipkPSoFbAI5o3+BcIIc1fDoGF6LL9L4A6S6lqGV5JxqdDBLgZZMn2rGNVMVU80iriVeJUbLcTlRa+BWdRNmx0MeRPLybsDyx5Fn'
        b'tJHHlcRaK2WxDMrxSjHUf/d40uWshJlh2HMl5tQZvL+TBM1HZ/LrREZu+//+Xav/6rn9QffjoDeqBVAAml/mIbcF/gcLTiEaIK6vFUk6Mf2BdkDtLWKDLs8iAYddi0uh'
        b'ucCgs0gMelOhRQI2k0WSX0B+FpsKjRYXyhhvkWTk5xssYn1eocUli/SD5MsI6/vAGlJgLrSIM3OMFnG+UWuRZukNhTqyk6spsIhn6gssLhpTpl5vEefoisgpJHu53mTF'
        b'jFqkBeYMgz7T4sogtSaLuylHn1WYrjMa840WjwKN0aRL15vywQXR4mHOy8zR6PN02nRdUabFLT3dpCPSp6dbpMxlzy60Pc+e9vew/QiS7yC5A8ltSIDczfgfSL6G5C4k'
        b'/4XkC0iAxdT4ABILJJ9A8g0k9yH5FJKvIAFmOONDSO5B8hiSzyC5BcnHkDyF5AdIvq3z+OTWHnbos4Y9LD3jZ1kWeOdm5oRalOnpwrYwCv3sJ+yrCjSZUzTZOgGerNHq'
        b'tElqGdUYgV1WYzAI7LJUp7TISb0bC03A2G2RGvIzNQaTRTEaHAVzdTFQ58Zn1tqr525vkUXl5mvNBt0AmPGnAQ8knMRVxtdvar69edoU/w+eIiKK'
    ))))

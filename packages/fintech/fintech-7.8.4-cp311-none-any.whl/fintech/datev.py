
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
        b'eJzsvQd8k8fdOP5oeg+QvAePsY0t25L3ZplhvA3YjLBs2ZJtgSw7GgyHYUawwAwDDhgwwYAhZpuwDCFA7tI2TZvUokpRnKalbfq2JPm1Tkua8eZ9+7u7R5IlSyY0Tfvv'
        b'//P5SfbpnlvP9+6+d99xd9/7HWXz4Zh//7odOYcoGbWEqqeWsGSsbdQStpzTw6WcfGTsMyyKOs+yPKs9ZRw2JeedQf7z1lSrKY3nUjYK58u49um3sFCoi3xUKSxKxqug'
        b'3LaJ+F9vcJ+VVzl7Id3YJNMp5XRTHa1tkNNz12kbmlR0vkKlldc20M3S2lXSernE3b2yQaGxpJXJ6xQquYau06lqtYomlYaWqmR0rVKq0cg17tomulYtl2rlNPMCmVQr'
        b'peVraxukqno5XadQyjUS99pQm7qGoX8P3EAfIaeNamO1sds4bdw2Xhu/zaXNtc2tzb3No82zzavNu82nzbdtXNv4NkGbsM2vzb8toC2wLagtuC2kLfQQpQ/RB+jH6131'
        b'LnovPVfvo3fXC/Seeje9n57Sc/S+eqGep/fWB+n99R76QD1fz9az9MH6UP24ujDUHa4bwtjUjhD7Jt4Q7kaxqfVh9qEoJNw+hEVtDNsYXkFFjhm3hlrLeY5aw0LNzy6r'
        b'te3sYPQvwA3AN2NIBSVyL1O6oqcfTONQGEGS6r4J+nz1ekoXhR7grQVrYTvcUV4Bj5fMg3q4u1wEdxcumCvmUzGzufBeFLwmYulwG8eBE/CMprAU7oG7SuGu8eAWi3Iv'
        b'ZIN+eG+5iK3zR0k2gdvpxYUJ8LRrIY/iclngOHwZXtGFoChaAy+hqEIx3AF3Ab2ilEd5w52cMrBtHcqM+w1cz2oA7XBnQjMCaFfhBjGPcgdX2eAa2A9O6SbiFDvhQBBo'
        b'Xwyuw1c9gX7N8zp49XnP53UsKgDu5YBdM6MRqJEo4QpwGbwO2sFefnpisTgOQwz34mcXKiSKC7YWw8u1LJtWC7G02jnkvBTchloOdTIXdTGFutYFoYEbQgAPhABeqNN9'
        b'UPePQ8ghQEjghxAgACFAEOr8EH1oXQjpfDRidriM6nw26XyWQ+ezHTqYtZFt7nyncWN3foCTzg9jOn+pgk/9cm046odqz4yWiRQJPJ3IpmRcH+SrVm6sWssEvjTNjerL'
        b'R7hRXa18Pz6CCTRG8aj13PEUNb1aeVw0njpLKd1R8PwVgdwn46npw4J1rA8C/zZVuUxGKd1QxPplXax+F4pOCpLE/1gdxf8TE3wt4C8+nT6s2GHq77HvBR5gfUgNUbpE'
        b'3LOX4RY31O3tifNiY+HOxAIx3AnOVsYWlcK9CZJCcVEpi4KHQa/Kx20KvOFn13kellrvxNB7mDuPZ9dxFO66Og9r53D/5Z1TN7pzXJx0jmeZGreuTojjYSe7Yr54IZua'
        b'2szmUPAYbGXrfFEE3L0JXKpgI586korMTNLhUsA9eBOerZgfrkIRDdRsb3BJh7qHmgFap8IDiE5sLEmkEkEXuKrzw8nvwnvwNDyA2g3cTBFTaBSC0yQG3lwUWFE6D+7m'
        b'USvBOfYLrNAYeE4Xy7ziLNiGx2J8MWhfiYbQjpJ5seBsQgGZHSTwLA9sWQ8Pkfei4XXYF1xFdYtNnExNng9vK04m/I6jMaK4oKODR9+ecmzzjhMHrh5YFRTJgSvp7a2S'
        b'SzveGp91dDNr+S9ejPjbOk8BZ6Z4prjWq5az1L02ZpHXVq+5Z9oCGoLneNXGfJHS883KSV17Jr4vPBP8Q15B3cTp7hp3j3Mfx2V0HJsreKdn0qunDr/lI/zDJeksXdCy'
        b'RXRlwNKYimDBkTK5Muf5gd3pL3otyPzl9kl9Xj9tOFPcWuJSs1ob0jygDTKGHixb6HmoiA093535fECu98/fPdgfefa31JF3tv7Je+4fT+5MSz7TLKl+o86n5acuqc2I'
        b'Bl7YWxCT8EMR78kE3EYXwLk5xbA3Bu6Oh7tLxUUJaOIbDwc4sA2+BLY9wRMLvIwmsAvxRWKoLywpW57KozzAFTY8Bm5VPcHTdRHoWBsvERWB3cp4PDmimdEHtnKayuYy'
        b'rzgCbuR6wFfrcMvr0GS2E43acfA2B1xEjd5PikBDo02Iemon3At3IdzZH8rNZoEr4IC/yGuIHStSYzz6jo7GCzk03Try+dp/cp26qUWuQiSYEHcJIszy1VOHvNRylUyu'
        b'rlLLa5vUshb7R4zAmnqEgF+2UsPrWZR/cEdl16R9yzqX6fM/DI3uqTOEio2h4mHK22s2i3H3uXawOtJNgsCOKSZ6Ykd+V/K+wo5Ck9+EjiU9vB6NwS/e6Bc/THmMm80y'
        b'0ZP6/C6HnQvr1wzMMojyjKI8A503ZhY3kiWyh9Mz+4R7r/uodH28vjWDMZkGvyyjX9Yw5WKf+CGd8oBO6U8d4BjoyUZ68uiXaA1+CUa/hGGKZ803s2dmH+9EUW/RCZ9e'
        b'n9Ev4/Y12LyMQzJFv+J90rtvtYHOMNIZlgy/D44cjEof4KLvglsedzwMUTMNwbOMwbMGhbNMAv9DWfuzuvINgkijIHLQM/KveNJR41lH5D3EZ/pgyKWqSq1TVVUNeVRV'
        b'1SrlUpWuGYV8R8TwxoTDDjPU43Akng9Gdf40nL4LOV/i3n+BxWIJh6nvw3nkHaBX7Fi1a1WrxzCbxxKaPMbrM3dk78p+xPVpLd5cuq20tdTk6mNyFeg9vhzmUTxf+9DW'
        b'cuarweTpmFsqddU7j8Wxm7itTHcNpi+8Q5Qcs9yI4ZaxlnDQP1dBLeGhX76MvcRF5qan6lgy7ja3Ja7Ex9vmuoQJ4yOfO6JELD27jiNzQU8ehJfkoidX9OQpYyGGukHk'
        b'PsSfTxqtjPTe4/9FY6aWYwMQ10JJNmKAWAybewgXTJGiMZFDHP6OURz+Bi4hchwHIsd1IGScjVwzkXMaNzaR4zghclyGAzmm4FKu1Xw+YiE8l61IpxQfP6JYmjoUE7eV'
        b'ffTtycdOHMhuZ/Fznov6zaeBk+jj2S+P++Fl3lnZls/8k1KrWaafpnv+pPXjRfDz3qSFm7UpEz8pkfZJlfIZJs41juSQ22+v3Jd37Xwz93BAf83Vswfc3puU33Prjeqf'
        b'HmZRcqkwRHhIxH+Cudip4Ca4FI+YwnQdwxbG8ykfcIbTEgD7ngShBFLQAw7GFy9faeEbOZRnAsdFlPwkEM/Gt3S5xbC9BPHIInewlU+5gp3stTwBiYQH4OZZmGAWF4KL'
        b'FMXPWq5gB4G2IFIu3O8FtoP2csQDcyke7PYsZsHb4FX4Gsn6gnt+vLgAxS2Fp3mUK7zGBtvATXhCxBt7/PEsEzMZdkOuVVUKlUJbVdXiw+CPxBJApl4dxUy9WjaVkHRh'
        b'ykCAMT7P4Bvbwe307FppEgZ2Fj8URj8QRvesNAiTjcLk/jyDML2DZQqf2L2qb2Jfct/E7iaU2MMUNgH9uJsEAWgAjpuEch4q3l/cwzUIo43C6EHL3zAHRZIUaoF1IuIP'
        b'cTVyZd0QF0tyQy6r5WoNEvrUmA9R+1vrhXGnuhrPLMx8gll/hzotxSnVZEYhc4qGzWJF4ClhbOf7miv+itH5kJuYuuidy6llOxuZLdaRyYzLOjYZlWwnrCfHzQkz6ThO'
        b'0chjb+SYR6XTuLFHpRUsu1Gpi8evhwcy4R4w4AF3I8TdgxhwuLeigEHweXMJOzoNnuCPKwV7FVlPXuBoZqFMW3+58ujbaWjAnjiQjIbs24Ht2365rKjrN8u2C39Ytj0u'
        b'g79dvsvT83yQ9GTprulTSpJ+xY763HVwx5mYrs2pXtSXBo/Dv0kUccmoAIfSMuE2hWVImcdTEtz+BPc67IcH1fAquBqKGKO9cK9E3GxmgII3csGLDeAWGTwlQJ9mGVlw'
        b'cxMaXGhoCeGVJ5gSRTYEFZeLWRS7HF5azcqbBE6K2DaDCHefZQQholgv1yq08kY0iMZbEc4aRsZRrnkczeJQwsAubfcLg4I49PdhcPTgpJyBSsOkPEPwDGPwjEHhDFNA'
        b'SGfLoY37N/bIDAHxxoD4Qd94m9HAU2NZdYirkjbKR48BHhkD1iEgxkPACUS4mzVKZhQgmGZyWKxAjOtOne8V/19yi6fOe2dz/kMpU/0zjoE4jGV98A48azcCuEudjIHM'
        b'bIVJ9VOKDIHu7TUMzRoZAmMMgGMl05eXJG0svhWz1atAPDOJUx9MfSpx/9nyeSIOwd7AuIoR9Id7q8gIgBcXPonAsN0BB0EbvIrx3y/PYQTM15BRlL0JXjIPAHB2KcUM'
        b'ANgDekSc0USDQ/B9BOE1ThBeY4fw2WaEL3sGhI/E9MS9K83gSw+SP9vJn6C7WoJfzFstVeockH70xJ9uj/VWsBoo+7m/FKH9BIziYzvfF+6rJ6HXOp/zCc5zrHM+VkBQ'
        b'ddx/47zvgPM8JzjPK9PhyQTcdqWxOm7dikqoF4sl8wqKFkB9eQUj3xcgUV/CorTwdTc+7FpIRgk4WR4DLsOOb6MU7hmKrPcjuRoFyrNIuu3o2ylE8r914MoBRZCAkf1r'
        b'/nd8Pj+rQLqM/9HF7e1pyatTbie9+fYvUoxffJ2kfVX2xg9+gsfT4n1Pkt9LqrySnNTzyZ/2cT6u2f5ZQH9SNetYw+qUlN4kbmrzDYRW3cJzU2YicTwcw3gG9iz2sBeU'
        b'93sTWTkWnibS+AuwtQlxeFtGURxw1kxyVoPbyH/VQm9AZ4jdgINnmRGHuLMLK63cnHcCGXHgZfg6GdIqOAAuxuQxHJ2Vnbuq/FZuzipEDfF1zViqbvEyoz/zSAbkBvOA'
        b'XMyhAid2tPRE9XENAWJjgBizW3msD7GYOM0QPN0YPH1QON0USg9T7HFzWIzbMQtRpZ603tzBAAn6+zBcNBg39b7QEDfbEJ5vDM8fDMwfRuUmPvIVdro/9I144BvRE2Xw'
        b'jTH6xgxa/mwGtQszqLEqedRotqmaC2UmZhYJcSoe2PY1a8QJV1MWSrboqZTs+6dpzLi2VSva83IcolYkGmEzHcNqRM6/X43ojI5xyhQ9A59wNHhe3MC6cHTGjxBpingx'
        b'4tg+NPBOHxAjAnUwOSXpQt22z84tDgpcGdT6l+Z9vBLPxfdT6BVef7iV9Oa5N6n33kv5RUrE0ddbg47+Kji/MnfV4VVdKwNXdjW2fhq+oOe/F68aXOb30/vvs6kLGcLn'
        b'4xoR/4bVzWHg2oIpQaMGU0QzGSNrwBUtGSLlcB8j82CqdB10kpzLFm2E7QmFcHcl6BPzKf4KdiQ4CBmGrnTyVLMYdR7eZUQpJEjdW4DQ7Rn0EhjdaNpGMnJBtEOrRiTO'
        b'e4SW4GcymprMo6mBQ4VM6PLviURfWe8qw8QU48QUQ1BKB98UGdOb8zAy9UFkqiEy3RiZjkfSJOLsK+6Y1RVtCgzt9ngYKHoQKOqLMgQmGgMTO/JMdLRV0xMQ1bGhZ6Eh'
        b'IMEYkDDom+BIFMccOoQk2oyc2XjkjKoGluw0zZRZuVKPRs54PDbGdr63QYNV9whB1bi3RV5YAsW8bFXVkHtVFbPCh/yeVVXP66RKJoYh/661aMTXN6nXDbmaZUCNOprM'
        b'enUKuVKmISIfYXoJD0DmC1L1b5tAbbRQGI9azJqUChz/JtPRlu8jQYAez4X6AlNAEHL8g/VzTH4B+vxhLt8L9e5Yji/HK2GYcuK4c7xE2OfguPO9YnHepzi+PC80ez+b'
        b'Q7BHR4hQbxm46AGuwI6iUrgnsYhFuXqyq2eBPQ5cAP78tRpPZKxR+iv2Eq6MI+PKeN3sJTw21UnJ+D18yslH5mK/AGz/tMRF5kqWg92G+LNViE9b97VwlrxGoW1Sy1WJ'
        b'xWq5jPE+9iUo8xhPY1+PXyhXt+jqNc1Snaa2QaqU06koCsP7tWeJXNuildP5aoVGe5ZNMOzxD9GA/fwwEuqKm1TaptwyhFF0bJ5MLddoED6ptOua6QUqrVytkjc0ylWi'
        b'XJsHTb28HrlaqUrmNJ9KqoV31EoJPRfhYxPKu7BJrXqWdM4KWyVXqOR0nqpeWiMX5drF5Rbr1C018ha5orZBpVPV585eIC7BQKHfBRVacaGsTC3JzVOhBpPnViJ2V5mY'
        b't0oqk9Bz1FIZKkqu1GAmWEneq9KsblKjklss71Brcyu0aik8Ls+d26TR1klrG4hHKVdoW6QNytxylIK8DrW8Bv226GyyWx5q1mDosPqWNgOCgiT0Ep0GvVhpAzydPGZM'
        b'Sm6xXKVqkdDFTWpUdnMTKk3VIiXvkZvfJ6fnwDtKraKeXt2kcgirUWhyK+VKeR2KmyFHEvIqXG6sOUhkiaPnyBHuwN46rQbXEjepY2p6Tokod7a4VKpQ2sYyIaLcQgZP'
        b'tLZxljBRbr50rW0EehTlVqAZCwEpt42whIlyZ0hVqyxNjtoIP9q3Gg5ZhXFYXKZrRAWgoBLYi/Xlq3CrMc2PAgtn5JXhOLlcXYfmReStWFSYXyme2YT6xtz4ZCwoVA0I'
        b'13A55mYvkOqatWL8HjTB1kjM7zT77drdWThue7tKpDhUIsWxEinOKpHCVCJlpBIptpVIcVKJlLEqkWIDbMoYlUgZuxKpDpVIdaxEqrNKpDKVSB2pRKptJVKdVCJ1rEqk'
        b'2gCbOkYlUseuRJpDJdIcK5HmrBJpTCXSRiqRZluJNCeVSBurEmk2wKaNUYm0sSuR7lCJdMdKpDurRDpTifSRSqTbViLdSSXSx6pEug2w6WNUIt2uEiMDEY0ntUJeJ2Xm'
        b'xzlqHTxe16RuRBNzsQ5PdSpSBzQby3VoGjE/NKvRhIxmP5WmWS2vbWhG87UKhaO5WKuWa3EKFF8jl6prUEOhx1kKzB3JxQy5y9NpMEFpQRxS7iLY26BG7abRkBfgWY+h'
        b'sUpFo0JLx5pJryh3CWpunK4GRarqcbp82KtUKuoRjdLSChVdKUV00SZDBekDHDOXrPHaFjZCxsVLEBRowojF2e0izPlRVLRjhpSxM6Q4zZBKz1DrtCjaMR+JTxu7wDSn'
        b'BaaPnSGdZCiVMnSZtDniSxB/QsK08rVaqwfNRFZvqm1SjTUZ0xEz5Igc19sEROcuUahQb+D+J+/BUS0oCJNeNEvbPabYP6LpR6rRImqnVtRpMdbUSRsQ/CiRSiZFwKhq'
        b'ENpae1yrhr31CIkKVTLFagmdz9AP26cUu6dUu6c0u6d0u6cMu6dMu6csu6ds+7cn2T/aQ5NsD06yPTzJ9gAlpzthU+jY+eZW1ZgZDdEIY+Qs0swrOYuysE9jxVmnMifx'
        b'5c7fhvkuZ+F2rNjYdXhK/Fjc2T+SOGXsN9vxac+SDE2VzpLZkYAMBxKQ4UgCMpyRgAyGBGSMzMYZtiQgwwkJyBiLBGTYTPUZY5CAjLHpWKZDJTIdK5HprBKZTCUyRyqR'
        b'aVuJTCeVyByrEpk2wGaOUYnMsSuR5VCJLMdKZDmrRBZTiayRSmTZViLLSSWyxqpElg2wWWNUImvsSmQ7VCLbsRLZziqRzVQie6QS2baVyHZSieyxKpFtA2z2GJXIHrsS'
        b'aIJ0kBWSnAgLSU6lhSSzuJBkw6Yk2QkMSc4khqQxRYYkW9kgaSyhIcmuPmYQ89XyRplmHZplGtG8rWlSrkacRG7F7Ll5YkKttBq1vA4RQRWmeU6DU5wHpzoPTnMenO48'
        b'OMN5cKbz4CznwdljVCcJT+irVPBOc51WrqHL55ZXmBk4TMw1zXIkDzPM5Agxtwm1kG+boDnyGngHU/pRbEM9E27mGixPKXZPqblzzcoVm8wOapdkx6AUxyAk5iixUCzV'
        b'Yr6UrtCh4qSNckRGpVqdBrO1TG3oRqlKh8gLXS9n0BSRQ2dqAJFNFgUm7goZyfatiZ2U74QoOS/bMSFRMY20Do2Yb9rM8pKmrMPx5kZm/Ck2fiwTjmiqvmbllp11Vedj'
        b'BeQc7BRQ5iVPdSF2irCSk6dpViq06mKsCWMxukusRzPrLUuJ3pLRoeGVHs2C0XpLEdZbBukLhvmUf6LJL3bYhRvoPUwhB4W5U/4hHQuGuUnjZrK+qGFRPsKd8o6ZO1bu'
        b'WvlZPSvVP/gJhRx9Pv4yikS8KQq8CE7Bcxo+2IH3se5IAGe5lGsGeyPogQf/P9Ml1onchtzzamubdKgtVPVD3jMQwjEyj7RZrnzsx2gSsRr96+BZCAUbEV+D1eI0I3Wh'
        b'AaRA0x5Kgvf2DXEx/6WuRN7P76CABY0MO9XUoJLTFU1KZWIBmg9V4uIWrN0ZeRyZYXMXFS+hmWxYi4fnbo1Co2MCcJztMzPi52ClIyNdMC+asUBcUdughHcQ5ikRR2T7'
        b'mDtDrpTXy3BFGK9Z5TPiTzFLZ7mWliDSBmZH5eaJxSIy0gxLZhY8R1RkZpGTCApY2ESJ0dDWEqHEXAJ5nVKBEhCfQlXXRIvpPLXWAoo5pFCFc44KxMlSnCVLcUiW6ixZ'
        b'qkOyNGfJ0hySpTtLlu6QLMNZsgyHZJnOkmU6JMtylgxxOOUVlckooJjpGMxpy0lgikMgeqBL5Wi2tuiBaZ2EHtEDo0AGly2KWQmNpQWLzM8ofEe6kS6JL8nN16lWkaNU'
        b'cnU9mh5b8JSGw2csoNOyGSJfZ0mCFdLOws14w0Q5KTB3CRFGcMXVjVIcaUURZzFWVBkrW8rTsjmPZFDoKdmcRzIo9ZRsziMZFHtKNueRDMo9JZvzSAYFn5LNeSSDkk/J'
        b'5jwSZ8t+WjbnkaS7k57a385jScanI8rYmJL8VFQZI5ZkfCqyjBFLMj4VXcaIJRmfijBjxJKMT0WZMWJJxqcizRixJONT0WaMWJLxqYgzRiwZ8U/FHBRboYV3alch0rUG'
        b'EV8tYYvXyBUaeW4+IvEjsx+aDqUqpRRrNjUrpQ1qVGq9HKVQyTFLNqLqNFNOPOHl6eqwUs46yVloKYrCM+8IQaZj81QtDDuOVxPRZFyq0CLSKJchDkSqHRU9ah52zDwy'
        b'k4+OUyvhDY2ZTbCLKSBrS3VaxJVYhTpCScSE33EqgZhraqbmiPQjSoMZ+DrCujdiAq+VK1CzaK1a6kLEZ2sVdYpVUtvZfwkRQq3aa1s2gxFdbVYxbdmkfDkj18gVNTiq'
        b'BPUaXpbTMJzN2IyarWYawY3eLFXqGlfJGyxqdEIECRe3CHFxZerFzhlovDO8xYZxvIPj549moiNtmOhMkx/tlIkOHDf5ixRbFjozBHPQIY4ctA8nVFNSBvckpnkTFhru'
        b'Knah/Gq4ngJw146D9rRw0JPYiIMW2nPQiGfmd3p0esjYnYJOAealL/DOIAb3vIsluxv6yqL0PL2XXlDHkXlsc7PfPrSEi492yzy3UTKvC95n0DvOWzcrLuGTOB8U5+sQ'
        b'50LixqG48Q5xriROgOKEDnFuJM4Pxfk7xLmTuAAUF+gQ50HiglBcsEOcJ65fHVsWss11iZe5TQSjvm4XQs+4o1zudi0TrWeb24YrC3NoG29L+3a6d7LqcBu7ENdSYvgZ'
        b'JBicdxspUTZJz2zlxAd/fVGpLrIJDqX6yGJQKp7elRwQHk9S0dvclviisHGoFhGoFuPImwUXJtpLOuZDxt56nzqeLHKb66iSxxM5qEEUO+Q6C5+wm1mx8OtEd9rmYwmm'
        b'mUmUOTlvl+IsTz0Xjwo8AB5jYUy9AvvwFm4iDIk8H2NwHuPWf4w3B48kV9dbkqvxzjJ1NU6C2/sxPnL7GGOyyGXIXSpbjeZldZVCNuRWi2ZHlRZ7vaXMAKxSIvZW2zDk'
        b'WqtDE4eqdt2QKz7AoZAqzVt+POoUiKOtakSTVgN59xBn9oL5zJ4iNd5EWutKjXzw68n2t4OUZbet7RF/cvSXhZCAq3dBDcsc/OXXuZMdewiNd7iP2rHnRnbsuTrs2HNz'
        b'2JXnutHNvGPPaZx1x16DiP05PoBr1wv4U8hUW9Ei1xADCda+U5B9KbVyiUMWh4AcJMBJG+mRJs8xm0ZAkzTW5pltL5jbXqrSOpSAP7Ez0NyqtczsIgmdh/OjWbiWJvuy'
        b'aV0zjWhRJi1T1Cu0Gke4zGBYe9s5FEy0cwisa1bfAkP6t8Fgj2Y5dAn5xSDMSSyxxJoB0ziHBVNuTDMRxZXQlQ2IiqLRJKc1uhqlXFaP6vNMpTAbghhxH5VES1ER6JmB'
        b'n1Y2IYqultCFWrpRh4S+GrnTUqTmytfItWvkeM2ejpXJ66Q6pVZELGNkjd0X5uGVQ880++harPSNtS4V2yiLRWOVYhmaORZs1Vg7ExviaFLTsczGo1XwjrpFrhyzIPO2'
        b'vhwir2LeDhXD4Ih5poqV10vo9OSkBDozOWnMYmzmhhw6Hz/Q5AEXV6dQoVGDYKTXyaUIsDiVfA1et16dIUmTJMeJHJvqWzfHezJHFWVsX4qmqCw6TJ1wJyKI0uHjqwp4'
        b'BH3bS8GFuVBfCHcXzwQ3EuGOuXjXfEGJCLYnlInBTri3ZF4BuFhQVlpaiG0W7AM9nk3wBGwjBVcv9KICKSq2da7a84jAn9LhjY3gdRpstS3YWircA3eUIHYC7LAWCy4s'
        b'MZe8bZ0nBff6kHLP0a4UYoOSfKet9VT7JVPk/D58ZSM4xxzfZ87uF0jEcUWofHCJS2UsAzdBJ18DbrCJCQJSzHwpH/MnvoPJ1Z5zSxcz4OUmgRPOoAOX4B2oRyW3J2Ao'
        b'd4kW2tQb3FJ7gFfBbp7io+VrOJoeXM2LH+3em+vOTvadXv+Xny1Zm+XTXxr8Yf6bAv07odOVN4fqEh/3vlUwVb/Z91dRd+as+HlI7P7jJxJmTErobQ398/SBz5SH1pW6'
        b'BRz42QefqWZzC9+7HF6w88PbmvPHVb/0m6I9+u7FRZyt1z/71b17f726WH38m9kDj4dm+9y+9MlQ/KR7t+8N3VV4ZP6fpG80nw69H/RmU1fNCc3do3E5ercy3+MT4KrU'
        b'3M8yRZ7kfGjsJrgHtI9YDZkAuziUTzSnDo0jch5/0yLQC9qDp5bb9jmLCoZbuS2r4eUnNK7ri3DHSg/U7CJwEhwvtRxG8ANtXFdwANwjR3tAN+rXfaC9HHdzitra0SzK'
        b'P4LrAa+vZQ6cnoLXg+PFsQViNsUHR2rhYbYY9IFect5hcg5AwJab+xX2wg7ct+PBJQ5sT0pgzqTeBX3e8RIR3JlAoQIubAJX2alKsJ/AOQFsxiZX9o70IrwHWkV8avxq'
        b'Dni9VPAkBiVaCLaBXegthL1FQDaEYDDNqICQDr7Il8SC18jpCWUWvIBr1J4QJ8Gp4G64Nx6nAhebaQ3PayFj0wDudYeXcTqibUYvXrpejF4KDnHgi2Bz4RO8JxqczFqK'
        b'YDu80PpiM1cdDAa4oB3cAndE7t/h1DrmIEafWCcnTMdZCLL9uVkvs8mC1S5UBD7d5GWKFHdwjb60SeDfkdqh6dB05ezb1LnJIIgxCmL6Ih4I4gcF8R8GRw1GFxiCC43B'
        b'hYPCQtPEeJTVZyRL9r6NnRsNgklGwaS+cQ/MB6pQljmG4AJjcMGgsMAUIXol/GS4ISLZGJGMMnszmbXWbLZvyjQEZxmDswaFWaaJcT2SvpqHEZkPIjINEdnGiGxnmW3f'
        b'mW8InmMMnjMonPMoJh1XLcoUlYh/I0wRkSRzZDSpscORLi9m9zreQq/GG9DVz2MHn8xSa7CDGTy1lnraBndsXaLa/LHZ5z5GjzzGWfoo5uTXl+bjX+UuLFYtC+9s//7c'
        b'79WuwCm3bOqWd54Lx+6ACctCgMYTArSeWmmNIlw/q0zEGvKoGuH1kKyLm5vIujRppq9dJyuljTUy6VSbtrIEjUPpyOtbqa5KY5i4lSI997WZDpvLtfBssYi+y8RNKuU6'
        b'0VnWEEfWVPsPAFvHAOteZeUIHWFVt9l3qQVMIUpCTpRiMLurLFBOYKBkCnQC5D8A3TYGOp8qe17x2UEMsG/JZAuMoqcym98RWnNbulVZOLpnhzPYrilXWMAMmiHVyK0M'
        b'4ncEq94CloVFfHawwlASdSdOQMCJHJO1/Gd617XKzHI+O1w07lZrcy23NFfkmCzrPwOfZ5UNL/vsMEbiLh1BPYkV9b6FGR4DVOvpsbXIeYltPtRmMU/wn3Wk7d6qbygN'
        b'Xjovqe7F5gbwKVLmtLXlMFvPq7tCM03y861ZxLBA4S5X31hU+hNsTS7yhdW2DIaYHwleNHMYIV6EwQiEfaDHwtfMrxrNYMBj8O6YlgJcqvAkUlXV4mtDokgI4RnweVlM'
        b'mYrcqMAQRO3TuqcaAuKMAXF9FX0V/UJjcp5BPMMonmEImDHoO8PBJIAzaslYBMAUksGXXowvDm+fhFF6FWU+Clbo9u84BUZmnE63OOqcdxZH5D7kYp4HmaNefI1WLZdr'
        b'h1ybmzRaLJEOcWsV2nVDLkyadUP81VKiMPKoRXJxUyOjSOJopfVDvCY0O6hrPWxQxduCKrj6L3GdW3hEOO1lPoDtqvfRs/XuGMf1vnqO3k3vUudNcN0D4br3KFz3JLju'
        b'4YDrng747LHR04zrTuNsj2R//iHPiTIoTybTIGkfi6wyeQ2e/dBfrXlPMi0nuz+eQR9EtBVE1SClG3T1chsNDGpvjaJGie1k4iN1WJmikWsldDmaFBzKwdNwI16MVjQ2'
        b'N6mx4siSrVaqomvkOCstU6jltVrlOrpmHc7gUIh0tVShlOJXEuEd72jXSHBNFXhZAU1N5iLNChBcpkMZqGidRqGqJxBZi6HjCCrEPUOL5Jtr24C1oY6wO6SP1UrV9egd'
        b'Mstcj/PTeKFEg5UJmud1uHVr1NLaVXKtRpTz7Do6ZhTk0Hl2bAG9lGwNWT5WNvzmHJqcKlv6rWfLxiyFGXQ5dAX5pZeadzqPmd4yOHNovMyDuorojpba7nQeMy8ezjn0'
        b'TOTSS8vV2rHTMQMeJWU85B0JdGFFuTg1OSODXoqXdsbMzcwSOfTCvEpx4Sx6qXm/xPL4pbYn58Z++cjkgjVkzAONC7I9rzFmdjQdocZsQEMDDVdNrVrRrDVzCBhPsTUj'
        b'MrbylJomhL9ymVPlHkInnBqTaiWxXks6W0LPYjR8ZIhOrNBKGxvxgXjVxDF1fWQwIMRCADSbh5ZMQeznSlGzrlEglkC+FvW4ecA5loM/ZU1aOTNMyOCXaxuaZGgmqdc1'
        b'IkRDsEhXoQGIBo0ctU6tnG5C7JXTcpgq4UFDVJcappoKjQ1IEjofTWqWCclpKbbDDis6Eapj68C1SlRhxjCwRu48Z7XZNnBTLYGcWUme3KDVNmtyEhPXrFnDWCeUyOSJ'
        b'MpVSvrapMZERKhKlzc2JCtT5ayUN2kZlZKKliMTkpKTUlJTkxFnJWUnJaWlJaVmpaclJ6Zmp2VOrq76DWnF8mY5GT7B36iZNiaioCJwTS8rw0fd4cDaBoqIqeA3wHNiq'
        b'w5ZYWZ4eqegnORrqqWRlE6OXq+FR3bX+2Ppqgn+JP6XDJllATwloL7boRuZBPTZAWSSej01xzI/F9isWQT3+8a5GPA3YDy67wZfAaXCKmOMtxvoXeBXuIfoZF4oHD7PX'
        b'aj1BF7itiyalw3tz4FUJ3F1ciA1+oMKxfUs2PFNPTQCnufB2FbxM9IN58JQrvFoMd5UugB3NqHo2dSttngv1ZSjrruIFzcgpLymCL3EpuBNs8YC9oBW8TM4x51TBMx51'
        b'cAs2gnkHHHen3IrY8Dh8nacjxi3Pgz3YBE4hKoAF7sRQHHCIBVrh3cXE1i+8thCc9ID6RAncgV6bAM4WwV1Qz6qEmyl6Do8LLqYRQ6clxahOVxPjWPCEO8UuYGXAbvA6'
        b'ad5vlvCphIIQbBu35LF4pnlL5Ha4Hbyu8YIvwevozW5ri1mU6zL2HHgZXmKMER8GR5fgeC8vCdwHr5fAK/FwP0cMX6cC1nHAhXWrdYxJkoWzPCSoBNR8hQmFsfAg3M2h'
        b'/OAtrk8ibFUcfudlrgbganzwu8bBYncw3ZP/SPa7zPAN0+4fe/kHS9e+2NoTIrpU5DFbu4+j/+DS7c/2n4kMe/6P03+S+T8xQQ/qP2fzLmT9/hvuT44I7y8VvxaeQ//y'
        b'a21/738lvnDF+MO/CC/EdAY/Cfvf1Q8+OKqN//PVwx8qL/3iJi/lwgexF16PWHXrnXdvPh+1s3v8vE8rd46PiS86ljLvv2SzblV8+OnApJ7fnth4tWDJxoo41y296kJd'
        b'3rkXOoOe7N/NX7iw7UePfrZ79efLkiLYb7Ae/LfL4Z6kWNeVIj6j23sJXIevMCrUSPiaxYYeVqHCl8E1olKEd8ChPAZ3EWLeNms+rSrF+FQe3BsDT5HydOBGDVGlMmpU'
        b'2AUOWlSp8DbYStSO4BVUSKc9vw+Oz7RoFG8BPdHtgh2gG5yKLxMXFpYWJ8Dd7kiIpfzhHW4Ki0XsqIIuIdheDO+BVxNiCxA0qMvBefY6qI8R+f4zNlSdKiKxY2c902qv'
        b'wl0qk1UxPGCLwMrijwTa6SVL3Klgusu/h9ej7d1gCEo3BqV38E2CoK5EI1bxpZgkyR35XdMMwvgR7WPmvvWd6w2CKKMgqkdrjMkZmGeImfpAMHVQMJVoBGferzdElxqC'
        b'y4zBZYPCMtNEUQe/Y80+H5MoDXk2GnwnmabO6OAPBuQYfHNNUXEocJ0BqwtjkW/1Pm+TKNmSjo5CPt0+LwQRtpiRZYqV9Kn7WX3qC9jqarZBGG0Sp/bn9c/on3FhCQqZ'
        b'ahDGmfyDBv1FXcs6OCZfYaf3Q1/RA19RX2Sf2uCbYvRNeeib/cA3e2CSwTfP6Js3aPmzEaPGMWIUZs2ZzdevYAfrDdVnsYPNfKsx066+gJ2L2Lk0huBl02O4c6pHPvSI'
        b'uR71ABbHnPWVCEtkkLLRWJqVlm7fv9LyX67MxKLYObc8inqD8s7z5ojchjxleKe8mdcd8mIkGMsjX9pIfrG5R/mQm3mHUq18yAPzm4jLx/uXmX6wdkGtdUMH+vhaiCnu'
        b'yZdcnIl7h4hpbyTa4TV/FrHN7qYfh0Q/bLudGPCv8yUCn7sTgc+DCHzuDgKfh4NQ577RwyzwOY2ztcn++V6Xpwt8UuvWJJqxjvsMYs1sfBaRSU0j3grhF5JYEL8otb0a'
        b'AfOUCXS9uknXjGKRKCV15FWaGmsUKqmFe41DjG0cYbsYrgtr46yHLzCAVr2SQ0lYz/T/JNT/P0uotkM3B3cUE2LVY3+LpGo31pn8TJClAKfs+tJvORMx5uuYuYR5j3n6'
        b'MIcxEo+qCatD1USmUTmXVNY0YZFC0ShVjiETLX3KqRAkaTo/FzImxHjWY+CtaWpaheHFIRK61IxdUvJMN9WsRB1PNzkXrxCCIAk5KyMp2ayGxoiAxHtc3NKREyNjAmGd'
        b'dHPoBRqdVKkkIwMhzuomRa11NC61OXDyVCWBedK27wZyDn6p7aGUbxXjcfZRorzd0Yf/AEl8hnyNvN68cfX/SeP/AdJ4akZSSlZWUmpqWmp6akZGerJTaRx/ni6i852I'
        b'6DSz8+dEApdypaYvcple7Zn+wnJKh2VxuAtcAm3FhaVwZ0KhVeCeO610tKSN5OxN4HW3tBdKiFjrkq7CEnbeRhsZ2xNchT26DFxqFzzpWSwpKkUCi02ptmXK4BFzsUhW'
        b'b3cDrxSH6WagrLPAVtiqKS8tx5I5OAKOmsX4RbADAbIX6pG07Y4EU1Qoer5VsQyJPUfAKTcKnIcHPcrWIwkWi6bwVjpHU5SeAXcXlpYXYzOeSVwqcAYH1fcMOEFUFqBj'
        b'fLImrhTuiUWvOgpeLE6UFIKLsSxqQj2PBw6uIpJwHjgAb3jAm2DPfFe4W1yGRHA2NT4VbAUvc8AJFH6buU/kENg3DjXILnhHZd2ShERicH0+vk8kGbTz1sLL4BqBrQUJ'
        b'dDc0RQS0wgQRvp5ECE9FtnDga4Wgh/TVR/5sikvdR2BWJ/xM+RxF7kVZCa6Bux58ClyCt6lKqtIPvKrDJuQq54KzHriZUIPugzcLSlDRYDe4DA/A62WkGc+jkBK4pwCL'
        b'58uCXOfAS9OZm01OTYXn4FWKklVThVShN+xigm+VZKTiS1JAD5VMJUP9NB0WBMrFjfj6FYjkikQK9eg45Zd///vfhU0YrbpcfKZXl8zatJjZbeW9Bu+2Ksjk0NXK9UEr'
        b'KB3iq6lMXRhumt1mnU5BwkJ8J1Ni0QKEEwVwV0WsCG6HPQg7CqwXMYnADdKAfJXX8joFuYfJFeyCFyPEFfCl1CIOxULQwAtu63TYdHU27Aj1MPfS/BF8cR3VNvBADOiG'
        b'11Ez7udSoG2B23Nr5DosSsHrfnC7VS1SPC8WvlThaqsBQd9+DjXNj+8Nj04h+AFfgReLNEXi8tJELOGXTYOthVhDxKFEsIsHro0vICop1JT6ynjGkp0oGd8l4wHuseFV'
        b'sN+VXB50Paic/Waw0ZVqlgo+WPwk7U1mXx48Bi8J4FWz9ovZN4dwC+5ILC+dF2sujtmbBl6Dr5p3zx0Dr3jCjmbQTnRD2WHw1XiJeklhQhyL4oO97ER4JIzEZIJ+cK2Y'
        b'qALYYPcKNSsL3J0t4pBWBvvl4PV4SWDSSLZ58FVymc86eA50WLJtT0fZAvNJJZPAfh9LHVPgYWsdX4dnFe9W/JSt2YDkxR7q4MX5ly4Vl8Ek388zd/y86oh/kUiZlf/e'
        b'UlqVFDc/PkIY5//SVWn93/Re7Zdu/2Z/SXfO7q3vS0WGo58d/XXIJtnxbeMi37m/K/PNY5GRHx3NPn8hcMM36gPhol8Nbv/Dc10n3pj+xZe/3uke8FVZxlm3pAN/OqX6'
        b'NCT97KT7i/RHV/54WqVgktvC4v4jF84d9pwnM7jOu3NOo/nR7Cr1x+fqO3+8oXFn+Ndt+V999euX5iV6XPaRx3w8vOWY6ELXkKTmj42fxI17Ysjtu1M+frv3B91Xjv+G'
        b'Lnh0/636l4QppVWFVy4Yf/GE3jrv8ATe79ZpHt768daPy9O83hkI6c5ePG3L2R2b/rreo/5u/7kSD8WZhuVLiht/Wzdp+8LfJvzyhPrL3pNGz6qilYcP1LtfXX2tbtUK'
        b'9TvJEt1U4x9ONK7a+PI94cJs1qJNK1N+vUS806D6xYOPcvqfZ7Vr/G/+dahpzcb6z0rbK86LV937vezLnPciN3+QuMJd/M3d+O2//uREOXvOmroe7ltT5n0y4Y7rxr90'
        b'94i8iK4IHl0dZrsPEI3pkxOwEosF2p+Q7ZWn4M0Mq/6V6K9AK+iy02GhefcyKa0ObMu2UWIxCqxieIHrqmUzmqcL8DQcKLbZodmY5bOQo1yYT3bxLV0eER9HNvGBk2gU'
        b'uj3HBqfBbbCf5K1EoPTES9C7b2A6lIBxcQ9bvArueoJxEd5I5xWXxPERJnaDO8tZmfBmC7M1cDt4bQo40ADOl5QmoLm0mAVehcfhCWK8NRle8YXtaCJ4sdi8hY+/nh0D'
        b'2uY/wepheBBhsnmfHxwAB+z2+uGNfvAu2EVW2eGp6XArTqqf7nQfHwv0Mab+b8EXwTH4MjylwUNVjGkgafZxsIMD+mvBFuYypa2otIFiRj0HtoBtZhVdPbwt8vu+VXRj'
        b'6+7w1EAYi9ZWZwo8b6z/GRHzWwLsFEMjEUSRd4PNKPI2elDBUV3BPbP70i5MMQRlG4OysSLPorObbAiINQbEGgQio0DUN8uYMO1+hCFh5gPBzEHBTKK1y7tfYoieawie'
        b'ZwyeNyicZ5ooMWvtrGVMMQSIjAEigyDOKIjrqzSKp99PNohnPRDMGhTMImXMuL/cED3fEFxhDK4YFFaYJhdiNV+WwTfbFIt1ehsMvtE2WsCY+N4NyL/e4BtlEoR15HTJ'
        b'emYaBLFGQSy2RZ1oContmtInNIRIjCESYnkaB89mMXsWByLRV3ZLdEdkiLa5ySgm3lpiUFfe/pyOHFNmTkf+YEiqQZg2KEx7NPJkCqO7Knr8Dy/tXvowLPFBWGI/xxCW'
        b'ZgxL63BHle6KGxREob8+AfoueSie8kA8ZaCW2XlxP8UozjeI5hhFc96KeCAqHhQVE6BK3moxRD9nCF5iDF4yKFzyYVbuwJyBOffz31r4RrlhcqVxcqUha4ExawFulTSD'
        b'bzpRa7LGTTal52Kgkg3ClEcR0b1BHd4mQUBnTg/XSCc/ECQPCpJN0an9UkN0ZkeZKSAYG98Ol/Rzr7kNTB30L+rgYHCjjMFxjG19U/hEY7ikT2MMT+2Yg5JjlW1PtjFE'
        b'bAiQGAMk/dEPAjIHAzI/DI8ZjC0xhJcaw0sHA0sfBYR01ffUo5wPiG1vU3xil0uPiyEwdjAw1hQU1uPSx+v1fhAkGQySmERiFMc77P3lo9iE/sr7NYPhhegPvS0htWOW'
        b'URjVU2EQiky+AV1uRt+JZg3sJINvstE3edDyZ6NxFTAa11vYuY2d17CDj96pX8fOXcqicX1GZevoEYdfNVr1atW+/gxzjGMNsiVYA/suZaeBRcPteXcWS0EUpP9e93tV'
        b'xp53y2NRb7C883w4tRbbHPhjvRNxP2WvOD1E6V30bnouuRWRrfckN1B56VnmuxF5bGrHqMNQG/hEScpzUJLyHRShvI18s5LUaZztEamyb5XIvBmJrGEpZ+1BFjk8kaBZ'
        b'm05VktDeJO7UvSxfvCLqOWEiktMwGnnB20oN2O36PIfieMPTYDMrC56ezFxzeqO8ugLsroS7F5SGes+D1+fC6wu8MpKSKCosgAM2wyvgMnMJ6U5wCB6qgLsr05PgTg3c'
        b'nIZkItfnWbBHDC8QqS64cEkk2GMpjEXx4lhIuDoJNhOxIAZ0II4R34M4mZKUT44Gp4hYEiGL1T2PyPRpNNdPogKREHiEEREXwW6U91KxJCktJZ1N8TeywMtI6nuNWfk8'
        b'hPhLy8WBCdmWiwOj4HFFx2fJXE0EwmzFL396rOK1sjeTfJd9cOWvdyYX7TzwqOpLdt/jBO/fR3XEln/i0699x0//iwVH/rvwb61f/vZRL/3g7eA///RPF2o3dR6vTnW5'
        b'0tST9YKsdau48fT7u3999fH9HXDON796/0z9ijdcv+r+zZGQz4YmlgRtO+OZxL518YXkP/2fTR8XyZaE7myvccnJTv5t1M8fRrbNfXTuUHvQ9a7Cy0FHrk5vfu7Tkmuh'
        b'b/3P++W+JwU/v0of/6q3/sMA6YSLHaV/2PBfLp/fjEt+O37GZzdeb2i8+ih5+Rd//Pyrvz+58d+rK3l+j//+zaWExX7JmT/5g6DdJenH3rtmPf64a9pf7r4heydya/TF'
        b'd5cJPjj+4faMFWt+9YOFXwxrVxl3/tz/vZbdvzv27u9ebl79cFnAsb5B+ZfuEyI2fcV+8FVj7B/2isY/wcgBL9ZtIBeMulD47sVr4CRrgaCU8EGb4EEkClqYICRfbUGM'
        b'kCu4wjBmu+CpVMIImbkgeMsDMUL1sI05pXDGF3ZZOKFlThihgMkM39Lvo7Wwk3Hw9sia6PIcEp+ZDLYUlyUgoW4vbIM3E8E5LuUN7nKqSluItfw1NQLYXkwuh+SGg1PZ'
        b'LHASvg6OE1ZtrXJGvJVPRcL7HebGMn45qYDG93l8uyQCaKN45HJJuAe8Ro6QwAG/WLAXnCy2P87iDy5yQzgLmDtoWvEplmJ8TAVsjbY5pzJ+JQdcKEFsJh5i4FAC2G3D'
        b'D68JHr2imxRHeOE54O46fCzJcuREg9hiPuUTzlnBnUbqun6uxswIl6gJK4wZ4fXFzC1qveAsGqM3VxfbrdBmUCR2ThoavdZrMLnZUD8BX4N5xovETgDXIuG19aMuK1gO'
        b'jpJ2kolRLVuzsdAG95TjWztAB7sJ9oB20fh/ISeJJw2zksqBjXSpYi5RtN3nyYQQxvE9M+O42IsKmHBIuV+5T9WpwqwEZsTqe6TdK/viDIJ0oyAd32E5wRRCd+cgJiw0'
        b'oru4Y7YpOLxjZsfMRyHh3Vk4cEJ3oTnQJAjsSjOGJDwQJAwKEkwhE3oiDqMkw2w6eLxJGDzMQb+PhIGdpcM85BvmU36hXXmdRUZhzLALDnA1B3SWD7vhZ3drgknDHjjA'
        b'k/IL7JjZxTnuecRzMDrDEJhpDMw0CLOMwqxhL5zAm/ILGvbBPl/sG4d947FPgH1C7PPDPn/kQ28JwP5A7C8bDsL+YOYF7j0yzCdPGYyeagicahBOMwqnDYfgBKEoMYY3'
        b'DD+Eo9SDwuyumV0ze3jk3s21BjrLSGcZQrONodnDE3AimiTKJIk4r3ie9OxbzFzOaQjNNIZmDkfgRBNRouFI7IvC0JQOR2P/JAxNYVfecAx+irU8ifBTnOUpHj8lkJeI'
        b'umZ1lw6LcYAEVzUR+5KwLxn7UrAvFfvSsC8d+zKwLxP7srAvG/tysC8X+yZj3xTsm4p907CPQk4Hf3gGiwoK6eA98vU75Lnfs2t51/K+DENYijEsxeCbavRNHfRNtcRV'
        b'HF98ZHFPfZ+0d6VxUqYhLMsYhsUCo2/2oG/2o/BozAZLiNORbxIGHSrZX9IjQN+FJ0J6QwxCsVEoHiR/poCwQy/sf6EnnRFGHgYkPQhI6g8cyDYEzDYGzB70nW3DV3oz'
        b'fOVFMhyY9U/NEE+jlaq1Qxw0FP4xJtLbwkSO4h/xbfGOg+wiZhy7rYwjvpXGi8VKwGzcP+98b7uvsWrshFsmddM7j8f5j9vsj1i9r3/voI5nrHtoLQfhzcuaSvNqg1qu'
        b'1alVJK6RluJVc5vFi2dacaZXyddpUDnNarkGHx9iVkXMyzwa61K3eYnE2Urx6FVwJbO2hMGpWYcA/5ZdgK5OGVrmHq02sAOfO0BMx17kuwL3w9cbwKuLwKuIUp2fB/Q8'
        b'xB+2cl4ISWMu+j4HzoPr8ADi7iXNmygJeHU+2famhDfBFsLtgvZFYrAP6uHBYomEQwnBDg44i2IZLfmkVRwqKwLLA9Ulz80YRxEtJGxbB/Q4cwHoQvldKC44zUKkswOe'
        b'GWJVEWZ6PTyXHC8pBLvSrcpNcLJCh/mloJBse/Z3D7wFjrgWEXinwJtSRvE5H2xmq1lZNRtIJj7shKcQX70A3JhQSpSprFB4ArzGXELezQFH4IFiydKVqAacPNYLsGuF'
        b'ImZcJUeDhUnughMv7ZuCjw7n16d89fzn3BWzxa9vvrh668DCobc/ojxqYvwn9nakvVB4FdTlsV99cSVn5n63P/9u3y/f46wcHhyIfOLn6+5XcfOra9s/rDlPTW55z9RT'
        b'xI2Mf6Ngx6mN/7Wj8I81ry3/HfulrLx5ydE3shdMb3jpF5+krPt438uvXH7lb/lpn6y7+9lbdbu+Ery/U5oZxa2QxSSvu57VvOPc/87/edXO+sRPCnXTDoRxv1i8tSvz'
        b'V0n3fvxcNee933BaDyZFtn5u3hNXvRz1h83uNHAjcOS862szGEbzIrjjR25Ewoqv3eYrkeBpuJUwRfA8bG2Il5Sy8bnhATboYxWDG3ALk/XaQngdcZdYdfiCtlDMpjzk'
        b'bNgDD/kzPOpFcHrtyAFeuA902OvgmpSEMcuCt+BFwitKQZvtTeSgdY3I9Zk5GlcrR2PlY6SaKjyEbaZYcwjhY/zMO9nm+xBihDiKaFFv2cOorAdRWYaoHGNUDr4WO4/F'
        b'uPtKEGkPME2IOL76yOrBSRkDnIEKw4Q844S8jgLThAREvCdkIt+kuFeUJ5X9qQMuhknTjZOmd8zuit1X3lFOSjdGpT2MynkQlWOImmyMmozZo5ksxjUXHxzWJe2eRDik'
        b'wODj/CP8wQmJ/YL+WkNgjjEwZ5D8mQIn9LgYA2MfBiY/CEzujzUE5hoDcwcDc3EEr9v7YWDig8DEfj7D4AySv2EXLu3fgS0MxaT2yHoRgIOTZqC/gRjm1wLmo4DQDs/v'
        b'dDDor/a0zNzQH9kdDJrt82+5Huo0et9Z1hC3WaptsLsz0Srvb8GUiWe+MxGbwnHRu5L7cvnWexNHqRL+BfcmbhOxf8NhOdmzNUKmMMXQSFdjn1JpS7Ce3WYLboQcurCO'
        b'jsO+OBqxGBpmdwAmRfK12LgWXiyPk7QomuMSyIvMNFHtfK1dg68vkFlX+KXq2gbFarmELscbEtYoNHIr3SNlkAqQ5FK6rkmJGJxvIWIuToiYaxlZyw11B1viC9BUNrcA'
        b'SW9FpSXgbAh4ubIAXIT6BAkSrQrgdpfmjVpy1yQ8Co/DnmI09RWVSuAOJNtWImrVDg6FJs5DMpw4FpubLYY3XMDB3Ck6PNmBm6V+8AA4P7GYmC3gKFlgyzhwl1l4bYVt'
        b'/vEItrVUJji3FpynCQmZmQKOIoJ6L76cTbHmU/AIuAr6FKZNgNLgESHpfPfYvFxvkOR5/cCTOV+VlPS/wQscYGVWtxb1y2uqqajAB7wrs2pmXzh8+6P9gb3+p2etfPGU'
        b'543j0/781bipeT/KjX2HXlsSw/tB40u5nmVvZMYb3llhePzWUl33xyb9tLqrx98PE7T+yP3rG39Rf7wK1HXvWB/441W54qA/KP44N2b+H3vouzd+232KLcj82XP3V1+T'
        b'bqvPXtQwvurFmp0B265c2EX/8kfb/pT2xZyOfm3isa/PfbxyQpv2kCokasaqM+f3i876Z+d+/s0BoWbdT+5//ocOj+iSXy+6uHZD+VfrdNFfPObWNQvrV/8mqHtcxKlY'
        b'0Z2N8Yd+ucL/vwu+ePmHIh9CODyWgVvxBc/BvQlYEOdmssAl+CK8RQhHKBiAXa4vYMEfS+Tkqsp29gZ4fAIhCFHrtPAqvLZGDE6A28yylRt4hQ1Owb01RKKOBh3gIOxL'
        b'JgXsSGBT/DJ2KGp4PdFpKNKXolJ3JEia4YFCEu0B+9n4RtuVjE6kPRfsLk4Ae8rXwlPMjaMe09mwqxxsIZCL4a0k4UpcRGI5tn6xkR0H2sFV8uaMpiTMZYgkcC/YU0Gq'
        b'5pPEqQ9kbmlfBo6rBKCfuV/QcrngBThAXgtOgy3h8Yl4M4c4EZ6SiNiIyh3ngBd5nCeEGXmRHdcURtQdiWU8ij+ZHZCygrw0E1xfBC/NLrZiuZuQDU7EwWsEXHA7CB4u'
        b'mIx1RebGmMEOXO9CAJJ684leYjPXoppgIc7vkjspthx0wbPgNjjJAIVeCfrYCfDaCpHHd9UqeFB261MMGebiCaDFy0oa8CMhwK+aCXCRLyX078w8NHX/1J4oxp4FFuiy'
        b'PwyOGJxoY2JC4IcSTdk/pUfIWJMgifpSLuecy+mXGeJzjfG5TvMFhmKR/7B3t3cHzyQIOJSzP2ff5M7JDwWxDwSxff4GQZJRkDRMuY+LNwVHdMX0RPVx+pYZgnOMwTkd'
        b'M02T4l9ZdXLVicbeRlS4XzJxDrt3cbtkpsAQXHBPZV+aITDJGJg0SP5MwoBDhfsL9xV3FneQ76OQsO7M41OPTO2LMoQkGkMScRkxJkTgXY+49ggxYF3edu9h+8UTx/ye'
        b'sIiuyp6JvTGvJJxM6NP2Vxom5hgn5gzMMoTlGcPyUGlB8ffnm0LDjxccKeipPFzWXdZVNsxBoSSKOJ9h5wllF+bMQQKn0+BhjgUmojr6QZR/Pp/3Qz43393th14s5DL8'
        b'ghvDL3w+BtMwGl+wEGmVihk+wpWF72i1Q5a/YyailbLc0fqCz7Pd0fovuoH8sFsiddl7CkdktnCHr8G0MRuHSJX5I+IxP2z0Lxhlmx2f5JY11VZVEYsjQ67N6qZmuVq7'
        b'7llsmuAzyGTjP1l/IkoEwn2RphMJ/y0L0XiBf/Qa9EgfypDTYrUd+DucoYRjZwhzmMv28kXohBxXyttPv6iH06e5nzv43DJTeERf9uCMFQh/vatZCG2R+4S4j2bnm+bN'
        b'H+ZE4isxn+Z8xhvJNMzFoUUsKnhiV6DJVzzoKzYJM4Z57OCszyjkPMGOvgix50ERXa4mX3xPqkmYjhIEZaIEQZlPsKMvRAnCJ3UtNpEFSJNwGkoQnofAw+4T4urLUJpA'
        b'umOtyTd+0DfeJExEaQKTURJEHbBDjH7aJsjGCXJxglycIJckCJjQ0WDyjRv0jWMSBOAEAThBQK5+DkoQEtkVa/KVDPpKGDBCCBghBAzk6ouHXVleWKx4qssnrd5V0aPp'
        b'T70veCvVFEb3CQYi76e+JcMtX0lavpI0YiXr0bwFpsXLhjlirxko/7O6uBssJQxzSfgKFtPZkf0V96Pfcrk/wRQS3qXtiuvnIBgqBhc+NyiV49fXk9fXk8z1GNgqfKiE'
        b'U87yShmmvruLIbIWyiXhNex0r3wE8D/tqlhBXmHD1FhOBtPekYNe4QavcKNX+DDb3wtNqN/qfMahvCc4ph+5jVUIL8HjmkLEVQRDvcbbm0N5hbHhiaX1OqwCUPiu94AH'
        b'SkCfFnNaHnj33ly8ay80hRsJX53j/Ep5cvU0y3qlvEV19++5Tn7bs9jpcCkjp1ZVqfAIvmQ3Oi2CigidT5j41HlgT7EE9INLqUnpKDe8wXp+LTxIVjYn4YOBzMomuBFa'
        b'UmZZ2pw1g9kK2LMKdMP2wgSshUjVwWtcyhW0s4vArhDFuy41LM1ylKg4PRKbBTlx4HkWJ6PfU78Irlu+S7TLI/DKWc7H9RMvbAqa++eVA/8rye+R1Clvz++a33WI9c7S'
        b'd7adPMg7v8Tfc89zFUE7B3KCKgJzgpYcjgrqKHWte4Rmx5Jv/B7GbRfxCN+2LhO+HC8RITb5rsWAGjsV3Iph1C6tciTYILauGckkI2wdeDGcWao6Cw4tj5dAfRy8ObIr'
        b'Kx0xxzjzMtAJ9lsWmyLADvN6Ezg4j7w4JF2ENxyjOMTGHkORy9lycAReG9MiiWezWo4ETXkV3n7fYvdEeDxskwYT7enjKGGghfPSz3ok8D+UtT+ra9bxoiNFh0u6S5j9'
        b'RfpZmD/L3Z/btabPzSBIMQpSRoLWMjt8UICPH57Fok0BIV1zuhZ2zenc0MFFqfTFtpqLIS4GYojPWF0axY0w2gvMeTAUS4C5DjvoIxD4GiVlYTo2+bJYwZiZcOp8rzdb'
        b'2yG/r/n3r4+w3WYPG7vNKdjWCBqZ7G1u2IKznCvjbKOI5WZ7q8Y8EsdHcS4OcXwS54ri3BziXEicO4rzcIhzJXGMtefRcW4kzhvF+TjEuSOYXRDMvttcl3jIUvWsOpZs'
        b'PILf0xwuwJaXZWkk3A+Fe2O/nq9307vXcWX+KMRHlo5CuChtILZ13Oneye7k1HE6uZ08/JUJ69goDP9yrL9MKONymRQ2Lne0XxbU7aOgZMGdvAMsWUinO3JDLWUhfxiT'
        b'FvnCrb4JVh8ti0DuROtzpNUXZfVFW32TrL4Yqy/W6hNZfXFWX7zFZ1sHWUI3+zRLJu5mY4vP8vHycTJJkBWFegSUk4/9HGxvH9pcRuI/UwaBRmg2iszYxHGvc5EloR72'
        b'I9atXUiv8mTJKMRfJiQmqzKG3KoQ2yjNVyjlxD6o3e4iq/pOTzELSza7i7D5ZS56B6Vnm5V4eE+Ry798T1H9aGrFoRyplTuzp2hTCY8q8B1H7CncDK5gtuP/j8cuylOR'
        b'xqbmVqvipkUxgY289SxtyGc8Kkkacq9RROmSUCA4GlJuZ1fVbmMrogTtLhTsgQcq6l19wTW4lZSUPzeSKgjehXzVNXTdCuoPFjjJVKkI/LWUpcHa0M1/Mhx9OwNRtSsH'
        b'ol9m8bsCcw7nPneIMXi1g/X7oHkfBc39/WuIZs1v5ARefePTmnD6qOgo703JeN6rh68efkP5v+MXDkR7ihL6JqUlr96ilG7/4K1O0AGG3o5ye8jqlG/+hP/Z4nlrlc3h'
        b'IR0/8v7DlVe2rv/R5rkhP71/mEX9pDf0VE+MyI2oQcrU3BhwFLSXY46GQ7lWsrVZC4iio64YtKPvZbJhhh/jDVvZ43hwGzG7tUkDLlk3OqvBrhG7p9FgM9knMgvuCLKx'
        b'JmrbZrdqo4N4DSngJWKcNAL2I2JKrJPGx4pxumRwqRgnDAjlTp6mI3tTBHBLMjjMYcAEu8nmm1140/BRDjgBOuAesv6yYtZ0cAreHUlVCi5QKNFLHHCKgveIsqt+HdgD'
        b'78HDoD0R7kgshLtYlCvcyQbb4LHqJyKUYPo4eBC0r0ElaDnwDNGXgd1gbzncCXeUwz0SPpVdzAcHE0tF/G8R2jBGOpgfHW8dcPb2R7HhPEz4lo2jJkR1cDs9mE2vwsPP'
        b'dT+HHt2H3Sk6skvTM9kwIck4IanD0ySY0BPxQBA5KIjs8+xXP4jNHozNHlC+Vftg6rzBqfPINtdcQ/BkY/DkQeFkU3Qytu050TQxvm9m3/y+mb0SYqk0IppY/jT/hNPk'
        b'zRFRPTxsArUDfW1IPKNsGOKRo11DXHwyeMhzZAOmqmnITaFq1mnJXR/OljAY9YN5Xf7pbZKI2YGtlM2i/NJxLFYWpv7P7Hyva+/dbinUq9551Hcw7smrwk01ljFAm8pb'
        b'rAHmsW0tFi5pNRsDDB257MLB/J9EvQMl+ccNPXpV2XbgPwDjLLadscxEC5DhNkA6mvOU/OMQuldZkeofAG8OAk+92zLvfh1WaCnDcqj2nwPKrQoPgqpGxZh2KJ3AVIRh'
        b'GjGQ6Y8VNnSduqnxuwJTZw+MdO0/AEypPTBCAgw+rP1PtQu/StuklSr/ATjm2uH6UgsaBVXiciwnv8cE6j9k78u3syQ8hiVReCLpMfQVVOdqz8rglQz3UeTLpzx9TWyK'
        b'rvY8E7OAUpw6UcXS4MOjvx0MY2RfbA5zfmD0bz6tOSP8YTV/0vYyod9PAoMCF6aC91IXsH5cHVPIf9efmr3PtXpzioj1BMmwSDBNAV1mSmYhY3dXOVIy2A3bxpI3GfuT'
        b'42zn5xHzl8kUQ7Jk46nA0M4NPfOMAWQhIcwUEtqVzJxnSOs2H0bpyzMEYG3gd7eC6QhFBdt2tbt2/L9ttfvx39HnP1CX44CKznQ5ZlTUJPGQtBub7EW1Khe7udWTXXN/'
        b'3yDE+Vk+9yjWD/YqhNu9uAQRH++WjyBiTlDUbz7l7fJcPN39h1tq3X+eMom//b2S5imxXzdOXxm4JSjr56yds1zrfvCGiP0kHiPiYXgL24tfU7gRXLFBRgdMZIsZW/hb'
        b'NhXg5cA4sQRrU7aA05nsVKCfOaZSxKeKHPFXtMirapRNtatagmxQxT6KIG6iGXGbx1OxCb0b+hcYY3IfxuQ9iMm7H3l/jSGm3BhTjvmfLrnBN2qQ/Dmg7RCPnGL/Fj3H'
        b'TKznGBuaxfZKj0aEwfickXPn+1V6jJ5FMcf/1/WURdA7xFyIRNVx/o3o6yDcOduaYL68Yx77C9anHKrg1tLqTfXj6yhm08ArlTHgPDcU3kDNTrWAwwVks5obvA0Og/Ns'
        b'N0QlXqBeAD1wgFi/mwUGwH47EQ/NlbWrKmPLxCwqDezge89FYh0+2f1mIg9v9lv789Jq5fslLRQ5qbwxv4z9Jp9a21/YmLAv+p00MaXLQcGN4DU/y00adseVzchuc4EG'
        b'2OZPgRPwsDs8Ag6AlxklMzkScg4JJJe80q3KUbNmNHCeQnhrJ1uDl6OOVUw7+vZkNCYNL0b8LV8802tmcq1PvGBmTIUXTMlHQ3K6J0u06/0E+vbi29ulLE5GB9h27tTi'
        b'a9sjXsw+GvSm5LeJ0vz5P95y7tUd42S1MRp/wTLe+ahl6eeWKFXnZ6ir9vm8mZD28Ko8Ne/DN/Z85L16Q6Z2jTYlsfqN/7opn34n+N1a2fTVn7AXXjjxxuaVGedeFv7C'
        b'/Yz7pG0TNkvf3v6esCzt+F9SkqJSY1Lfp96fkllBZgVqZbxk+XaDyIU5eXv9/1b3JQBNHVv/Nxs7yBIksoadSMIOAiKyy46A4C6yBImySYLiVpe64I6CGhA1KmpUVFyL'
        b'Vi2daftsX5eEd/vMo7W1+3uvG7762n5tv/Y/Mzdhx9r3+r7v+0uc5N6Ze+4sZ2bOnJnzO2AfvJsBd9sEkP39gc39VHiemCxUTYdXyRoTngGXhzvXgI0+ZK0WxhINmeCy'
        b'QdeYwwo4EsgckGsDm7PADW/zyfoF6QBRN3CVCy/5wduP8UEW8CxotiDGHnjNihgDdKZDNTwGdhsoG1FB4JyRM2iBN4jVSZDUOUs83FQBNEUS9TC4A7amgVOVIwwO1swW'
        b'ccdcNOK+OOAfAclTK+tkCulq6yFDCLlDxjG2wWeFLeXijjfUp5OgKUnn5Ib3vN11AqF+Gt63qmWVKnT/+qb1asWldefWdedrA+PpwPim9T1l90rBsp5lD1z9NKKpWtcY'
        b'2jVGI4gZmL7VtrSTGM3dtIOki4P+ki6bXjPVOkR1J/Y6TNc4TMdbSqFKRWtUe5Sa1+sk0ThJHngEaAKztR45tEeOxjlHJ3C+LxD3CsRaQQAtCNAIAtCddkvmnjpfKwim'
        b'BcEaQbAOWxuoPDR8b/Sh+d5q/iWnc05dc7SiWFoUq+XHMjFaEvbbG4o7ZGg2YoZmbnHdEvmYcoWRYXjWj8/ZeHweVbkL8LC8fGBYrrf9n93xPmgqpjqtojnZpdyxpnJy'
        b'mI5l0MYRXRwerNnlXDJUc8c4TMcjQzV31FDNGzUcc5/h6YfqMePGH6rHAkQ1zmZG5e0ScA00c0BzHEW5UW6ibKJrrMctMj/qGX8WPIMqu56q94O7yXgdA44+g4ZxcMud'
        b'DOPwGDwjg/FfcuXoeSrt3seHXwvR7wc1Ad2r777atat1Y3F4aGbnzpvNN5WiLSKl+5bPvr/ZLIuY+XLlK/yDN8UvWrRPona8Zv7tNwBJx1jp4AJuoUF3ZyDGOQGoT+8M'
        b'BI3YXohFOVVwQSO4wHlCB90wpIMSEJ1hPETukA6K84s5aKYdNcnlvsCvV+Cnnthl322kFUynBdObeDoHZywxu+qcXJQh/Rz066GnjypUzcN/2HrYOmAIexsPWknUYams'
        b'Dh+pHSmBGFOMkmVABpk1ksdJ/mSYxxsovYIFIxXasVj4iM+vBb+bGGKK8jWMwwdme6Jv5g7hcGPE41jXbEr43Ph/k8/HlqgZhsb3fWG3H2hmwT1AjZgMsdmhepm3jYRD'
        b'XJN233v98GuxiHcvbBRtCVZu3H7c7t5XZXNfeamny7HRXaV08nuz99Ubu2z8XjOx+7KEsyOEVRB64txXJZ+XHXmD1617NeJw8BZZgBxNkkbU3Lk2HiZmBsZ4ijMkxtTA'
        b'GRKGd83Jxpuege2HMMjgbcLF+XouXmBH8Sc1TSO8qnNwb1qt8lbbMTMDZmJfnbMbtq1qTW9Pb0rWCbyUFqoCdYpWEEoLQhGre/up8tXe+E/jEKSxDhrC2GZPwdgji2M2'
        b'yOcDGtbZmNXHLkkN5vdtQ/h9/lPy+3+K/f1QXv+GT+4M6wMDw+hmauieCxnljfXjPO9/kP9HrSjHEskN/I8Xb0uQdH06X1IID4SmciieMQt01oBNLgqZm3I+S46RfM41'
        b'bjj8WjTqBKdIJ3Dfcrb55uZ9LCulIHrS1LkHWcmFVhtg8tRJ5+ZMEsx8uVd5TidgxMePj5lpHzeh8Zsx9LWEVxm8k4UY0OTAFCQx30aLs3H5n2fgfz14R5HeEaW+AwiG'
        b'sM2wGNIHwvV9oHJYH3BThV7gqJPVyV3eZzM7M7sjtOJ4rV8C7Zeg8UjUOiRqrBOHcLnJCC7vMyovLlXU1I0pqZgMYW+GuRdg5h43lysxf68bwt/Lfgt//25oBTjbbaZB'
        b'VJdVLEc0gUGGIBgRBC0C40b0WQ5qnJdJV/VZrqipL62Q1pFSBA+/DOkzL8UuC6TVCmld8NCLkD6TMpmc8TWAQSf6eCuKFdg1rbReUdxA3J7is3x9FtKG0opi7JQT3zpN'
        b'UmLrsOA+M4OvAFnZEMjgMySFQqaolKL2wgcM67Cesw5rmcZymZvdZ1JSXL0Mk+wzx78MoLjkNnGEQt4XUlfGwscQMZZiSU0DgSbu49VW1FRL+zjlxQ19PGlVsaxSxO7j'
        b'ytCTfZwSWSm6MI5PTMwpyJ7Vx03MyUuuU+BhsZ41YvmO6xwfp/lmK2VAgThEkT1gbGaB50yq0azc5H9wIT/K94/TGKNGKbOQrw1ax/qeTc3pWlge8MekeGYUiQFquEEO'
        b'b0yo41HsSfA6PM2aDFtgIzmBVRoBLssVK1AsvG7OcgYXKWPYxrYqXEIA8+GZ4BB/jBp0wS81C1yvDUjLyoWN2eCCGO4NTM9NFacHokU5WgEaANVg83yLRLjHkUzf8OA0'
        b'2Ayb4+bkUlj2zLICN5n7+5IXh2KQCJYvZZIImleB3UR+BTspeNwvPRT1vlAqtKGQQQw7D++Cqyg5m2L5UVamaJ24Ed4gR55S4S6gHDCfZyXD65T5PDa8OBnsJIhisD0n'
        b'FT1oRLFEWDNwExxYG0E0AvngDDjDYAOEc1Ehl/HgZRZsBsfXklrc6OhPzUKsEFR8KrjaeznFGEuALZaIGItiTabAJngQHFwLthPcvbULQzMCJAEYdjBLgha1F8GmTBbl'
        b'ADq4ceB8GqG41M2diqOoyKBq5+LdwT6UXpOyEZ5AJDkUS0yZxwElq4jB09gOtoLr/hiePw2tcj3r0Tp3AtjNKUF5fp6QC890oMQUZR3kGpD0qbicIZdskYmIGVMsCSUD'
        b'atAKruaS5jcDWxeh1bIYW4xwUeY2ilngVircSyjt50yn1lKUIGjVCzOn+aBlA663tXW4wkEXYsUAKt4ULfV3LSBtUQgvpmNjtyx7DwmLMg1mAyXYHEUIRdVkUC24zniv'
        b'mXUGzmcIwVOOckwItXQgZW4LDkeAfaTlysAxcJ4x7EOFQwXeYQS2sj3hLXCCUAuuxOB/lDBohX2paa4rg1USBy5AZWgYGu1RfcFT8AI4gB5n3ETsB0rYnoG9GOyEe7Ce'
        b'4QzsyuJRVmAzJxbu5RGicTMjqVqKCgpK62G/P8GcyWLERLAN0WTjouagpcohcFZYj3fJvS2AmiGYPcBhlCNomQcvc8EOsEFA8rQ0F7Sgx41wAcFu2IWdQYBrpIzT4eY5'
        b'egKoFb2nooJa1XIiQQtoJtn5MsGOwpv7QVaJaxufiWO4DF4Hd8Hx0BDMtGKqbhU4CA8UkI4KWo3AXj3Psik/0MSDV1iwpSGYPDcB3M0ODQ9CVRNCwaPwEjiYDs+SHOaC'
        b'ww7+GdiCErvW5RjJ2JOmwUNkLSlcmBo6BT8TiZaVtUDp403cOIjhOXBLz347wCUKNkVTFjEca3AVXCd1NgFumo0eRHUWTcFno0GbFA0mxFnAzpJ1GUxdicA5LtgDdlMW'
        b'1hx7sA92kjLHykyJ092giU3et5eZME0QvSItdEoYhanVwpOgFW4CBwnnQjWqOZQRDLiYwaNgl7FRKdspLo0x8j2csBI9hlhrKlVoDtqKwVVyf0oiPJORgc8qsGtYBYo4'
        b'iHgX19BicBRcRA+gXMdQK1HWDq+De8ihS5Y/aM3Aw9gufIBBkG5kxzZdDbaSDM9ZvYZ6jNl62f6aB7ZchhGLUfdqAleDwngUK4ECnWHgGHxOSLIMmubA83BnZjo+UcGJ'
        b'ngPvssDhKeAyIeZoMoPahbutd2sAZ1Ee021TreCzmBYaBRKpOZZAVV7AjHttGRjubkcmEsoWseCuiYGodxwgdJqXCqggXIuLpgnqy6sZdW3oFEVGGraE4U405rLAseV5'
        b'5DY4UgMajacwxtBUANy0qh5vI+SBbbCV4LfkpcLtOZJCYl12Dj4XiMb3LDEadyhqhq2xky3qsKRlb4OtbgaUTbgVqPzxUQ8lGxzwjR90hnzXiU3WdEGFE1MOLLJkCgiu'
        b'gA5Li2jYjKYrMWKuNnCHwRc6a10wMHinoP7LnGpBkwuX8gbnePVgP4exbHt2hTXcmYvBhdBgfdGDa8taGAu7mF5xCb4Ab2TMgrsRI8BWai28BbvgXriBHCCG58E5ewNe'
        b'LNd3sB975/BkBZGE+8CNpfCsBNyEh83RxV30SZ7OOCu5uNTEH+4MzIJ7UiXgWF46g4ESzKV8ZvFCwAZ4kZT5q9mOVBjmkGq3xfHTAvUD3xnwnA241QAPG2OQTvSp9iWj'
        b'SgjcKxkgGge2GoiyKZ8CXihscyW8Cm7k5mXkoumUwJDuhxfhnQwJITxF4Z6PpuDdaCYHzfDwGpZzwyzySGxOdkYBUwunKL9V8BroBHtIOQRrckfg8LIoN7CTC7eB0/AG'
        b'bEfDFeHcZ8EdbAGIQWstcYPjNm8FLQym7VZ4dAHu2QFp2YhAmiSESzmBNjSl7uBWgvPupKG9i+FtqyB4mIMVtVhXe4tx52K3es2wR9no0cPwAlRzqzLgUYZHTjqngfNo'
        b'fN+JLmRo/jqdyxjdb3BahY0gmYyD7TyU9wl2nKVFKF9EG3bI2Sa6ATRziC4M9byjTNMdBMet/Bn/NoipAhn8XWdwHXW17Vy4w4LDVPPzSLjY5cODh3n4An3g1ZUkP1nw'
        b'KjgAdgbBnUgWWUYts0FTPTm+fFGUmyEBLVmSNNDpl467m10cB7YsdmWafXd4BqrQS/CwBbYwR58aOWFT1I4zDECV8XCfAaCnVsbkow2VV25piYYm1O/gNV94oTqeMFdj'
        b'njnFx8xldNPj26hMSi8+1cJLRTFwJyp1DVWDGq6dNJJLNXgeSWqpGJB3V0aOhGRP6MQFZ59BfWLPdLLPUm3v5W/EUSG2jKt+ELm40FHfSXehtj6gAN3gPJfoCY2tZZPO'
        b'zuHJN6AKsFnz8qk/z6h5J4hPLd7/j6b26Bv5KzvWeD2Y+iCt+fSaS4pAh78mmt87lNB/POjjjI2uCtFq0eq3X3X45dVY7xteIWsnHncMsk3PcXMTte1d/8UL4toFET9Q'
        b'NTv/esk3bu1Hi/855w87aq70WPH+tPaH7128JHskrtM/6r788OrfIs/NL+78w7qv3ljRnrSJzYcnLk449sfq5zq+ffzsjxYvzfv5BUmNTy3Ynw0+lz6o94u/uTdnQlJ5'
        b'h2TOTIvK2v2P7t0URNuH+dhyIh4vv2hU+Km8YK3djW/f7Gg3pi1ejhZF8Je/NvPd1B1Zye+W+VX7vCzZ0f32zHafl6t2dD+Y+W78jqn2yw8d7z7M/+7jtaFr0pYf8/hq'
        b'Cn9J6vJCm6zZ37PyYpTyLW4eL8Oozx6ZiFwLXird+uHyvJh9ctec/R+ebf9QlhdzslG+9cO5eTFnGj+zfNm8oyHXJvDVkhe2X/hU/fKkLvuta9aZfve3P74a6zLr4/9+'
        b'cBgKzF/45O1zTTu4C7KmJ/da5V8POPD2T91/f7Qz+dME+lLZ8wfKXN/drv3ly7cvN1zPtr23OP5Cy/dJ4W/ePb4roP7SnYm5BZ7z3p71+GOB6O79AOs8543fzO55frb6'
        b'bktbn92s5G3J/93K+mjZrc/vbjj1wT3u6x9FfXYusGVH1oVj0ijfS6b3ty7ZKJ389V87Nq0Tg38Wf7x7+T6lfOE732SFnJn/WtvdO1/NPuHwddOHDx55vNv8folOM/m7'
        b'+3utXC0+e1h8MaohqfynyKt1f3vZt+P7sHz6oqQhZYf/pCVJ67a+lfZ18qdR6YF3f9rbd87tG/+8tUeWvV6T+rXkdrNlQ43yI+Pen9S7bp3q/Dan6PPX/Dom/iH2BfnK'
        b'pfS3yQ4r//DWCfui7ecav/nEreP1wJqgHpEdA3d6qEQ0eApSnDb0HCQ+BJmZS5QZoAteSfPHu45s0MaCR57JQrLiZkbPcRa0OCF5DK1fjChuTGgSC9zx9iXHHZevXgV2'
        b'Tqi1qEMj5+4JKyxNjSg+OCaC+zk14BK4weB+3YHtDubgLBJRWsWphv0uG3iLAy7EhzMGDGhamDsETqskm1itNiWT2Dkx8BTYGYhNVmPBYWI6fJKNhpmVDFzFC8n5ZKcM'
        b'zQgSfhqaYLPYZfxAPSAtOBeA+jQq1AoWG+yKnw+6yf5+AjgCj2CLCWIuAc9XEouJAiGhmDwHXDOAtMEt8DZGq5WDLSTOEg31JweOpMLnlhr5sm2qVjL+qJpXVg/1H3UD'
        b'bjXsFqKVUxdJ4w13p6Pc1srGOEQKmyvIydaMRb4oidea0SdI3cFuAoobC06U4/OqeG8XrZ0ywR6m/Kj0/kZTo3jgBjzkQN7nwDIfusNg2F7wtuSCRnixjrwPHkDSd6ce'
        b'ug3uSgW3DXAcs0CT3n7aOF9/WtUIFWzwwOpl+3/bcng4EBmnuKxsteWghgldEuXXBzw9coc95epBuwR2hfa6RGhc4rtRkN0zt8nsAd9BaXTMvM281bLdUsv3ofk+aj4t'
        b'iuqeTIuStfzkJpbOjo91xLNZDxw9NV4p9/hvTXptkiZ/1qvOrztrvQq0joW0Y6GGX6izc1FN7LXz1dr56viCQxn7M7A5MaKsSlaHagWBtCBwyA30t6JLRgfGaf3jaf94'
        b'rSCBFiQMxkd0+XZO705gNluG3CYWzJVa/0TaP7EnTytIpQWpI6OXMiR7QrSCFFqQMjK6XOs/jfaf1l036p0kukLrP532n95jqxUk0YKkkdFLtP6xtH9sD4t5+uFve3eV'
        b'1j+J9k/qKdEK0mhB2ng5D9YKkmlB8njvZmsFibQg8TdGy7T+cbR/XI/H2MQN0e5PLvc4xKVa/xjaP6YbFSyeFsT/ytMja+1XmmQE8UcSJ/uJjykU9I8IoimBR9NqlY96'
        b'YkdAl6fWIYJ2iMC76XNZOpFEzVfL1fKu0G6j7hW3rXrk99g9cjoy435kbm9kriavQBtZSEcWagNn04GzNaI5SiPlilYrnYOLsrzlGewYuqxzaa9DpMYhkmy3x2pdp9Ou'
        b'0zWIO53c2mPxWyLVhV0pnYu6y25X90oyNZJMnSiwy6jTVcltt3q6RC4eygJVhNqP9gzVoySn6LuSin3G+ITxQ7wd798r8FendOWeS9eIY7tDNeLkHs+eFVpBNi3I1glc'
        b'j5m1mammM1s3GsGibmMU69lTfq+ITlmoTVhEJyzSRi7SCMo0JWU6gYuKg/5S1NNpr6laYQwtjNEKYshb9BueE59zvOLYnaMNzqSDM++hBsilBbm6X0/gojJSreiwui+c'
        b'0iuc0m2kFU6nhShT0wdfGUt7RWuFU2nhVC3G4xlJMUsbnE4Hp9+LNxTsVxIMVk2iPkG6NngGHTxjYIwY53k0xuTQgpzRhZ6hDU6ig4f21REvyNAGp9LBqUOihz2ffo+n'
        b'Dc6mg7M1M3O1gjxakDeaRLY2OIMOzrg3WysooAUFOoFTv8heNPERZe/u8BgH6Je94DEO+kkgpuwnNWW0ZKgitHxRkx43YchGhTmzUYEn8d8GvEfwxxaPQN3bSRAGhs0q'
        b'5/BmxQ7KcMAi1/5Jxn5PDn7XnYvDpsHUZavpw8/4D2zJPUMxKEZkMw6r16lGY/1mHGsMtfrvf9J41Ga0kBqtVvdl1OqXZnIYvUZeg7gxfjrF7NDhBeh6oAZb0Ep8VwMq'
        b'mSvlOrmGWaJ1JPiCZrAf61CpSdSk6WAXsfkF531tQz0cEK0QKiTRmRB/38SE6MRqg2vF3611psgZuU9WM4oyjW9DpdQ1hlGvOBSuJdr92oUNTtrKTCYHmasm5YMLoWGI'
        b'JjhAlYJbtmQpmjcdnIrCukkjDDNLScFVwGh87TyMKbQ6tW5KXZnZH2fEUG7lW+PyR3ZFLa/877muTB7qGpibD1cut9icG8qkDIyzoJDc6ddUVSWeVF7EpNy4jLk5c74i'
        b'85nEMCalWzmzdlVNrxbvtExgUn6QbkZuCjOXiW9Mns/c7HBisqRaUl65w2c6Yxpumg3bks2IsqMAq4R4K1hIuLsL9zFLZpVXWGhQkDHcxKVYXhTYD6/Au+S1fks8qST0'
        b'/dBmLbth5Tr98vZcELiAFvsXC5nV7XRwmVH+XFyLBMXDJuFmWOmCPuZwLxPxXApogYfhGX9cf8+hT9lipmUPRa2GzSgf5xBbSyiJKbxCXquyJocahf12qyx6k02Yk4ce'
        b'UrADNsMD5O/qNB5a32+lwHW4WUiabnI2WnY3QyUS3PHpBtgZwig99oBr2fiU78gDiw5lpOx28UH5EnAR3FqHtT37WLbwGNxAPOksAifhCX+wcR6BemqwjCR3HR3ATXDe'
        b'AVxBv1dRqxZnkpc7g+cwXFQePja7hloDbyaQQYs0yPZoQ2GWZZ7M9GRAQAV5H5TaXyAdiZVZKptpGcuVN6Cc18piL7Rk5D0bZ711iVFqwtGPWcHba6ZtXb19wfHz1xaX'
        b'3rym+JuHcde7V0qg95cvBWVOyOKdnGXDXv/dlPUrc9448513i069+3Cae93t9QFN2/tii/jq67ru5e6Ns/6gdEidebbE3nhBf9NDflHJ7KsxESelq2TPfj/T/ILn+VPX'
        b'sz/8Yt0Pb9nemrMz8c9LP7+3aOvPdV8Gf9m17Lu/9m3+xK3/wXNrJ0y+m1H4HbWs4nJKy5b61eVuFQrL0C5l6cG//Gj/p787ZDq+vnR70Y9tUxffzH/t5b+cm/eB1Z/7'
        b'j80xK59/4cq2lOiQimvbOmO/brAFKTfdmz9/ZeNxt/iN6tPvRf15DdtV/O3VwGWuDr+I9284FfX+C2XALNt99YK5P1aCQkXKyQoHr6+uKl77NK1ttlvrB0fMQ/f8Tccp'
        b'f0tX/2auaRQvKvdvPn+ZdvkbB91/ZeSftL9z44ufv2z/ZlmRy3zPBd8subHqvfxvp2rj3vvTd04/3mlfGb3kzvuFb873/NFq/fsvzfs+5/2cqn0rX7klEhDLBHA7Nhmf'
        b'2wQbYPOTzoODQ+Amc1b0Dnwe7k6BTeSwbrZkMl4DXWejFCf4zJHxlonlhiUsOC3Qm+jH5TKL1D1RiTmwY5iNozG4TawPU8CpXLyYy8L6Vuz8OhMedWZRtvEc7BMJNpPX'
        b'u8F2oMSeo9DbUbfdBLezMEyVB1qKMkvCqeC2FV7mZ8Ibo+0d8TofXAZHSEaFJXgFm5Pmj1boWzgUB15kARXYvpistW3hbdDBnHx3AduYw+/sUFu0bCYupreA3TYzVuL3'
        b'MBjeaO3JoibO4TqBW/ojs/7WpXg1vgcDbuM8ZKJVKyqMNwd0wiY50SewTeczK2gveJ7YdbJtwNZAUhcu60DrcAtLqPQdMLJ8LpdZjbatNRlYrWa5w5MG8MhbCkIEdoIt'
        b'8MIwE8yJ3oYltAU8Qio0CTTJ0JI2VRwQgDdls2EXyiU8y4HNInPG0/MLaMjZCZTsYYahA1ahyUCPiLkVbAfHSJo9GZQTj+KyMbD+UXCK1KdFATgPuu1GHL31hYcY+5jb'
        b'4GzeiGO+g0d88W6p/phvA2xhEMWugRPwGnyuTq8PGVCGFJYRd9dBoA1u0msGKotH6QaIZkANOsmyH9xag2rpYsJoM9QdsIOUDbai8fIiaBHqPQLp3QFNANufyvB0CMZT'
        b'HxebT622GhTB8DVZ2c9nYIL65zlQfIem0CbFvqiWKBVrf2xTLDni8tCa32J539qr19pLlatmXzI+Z6zjO5KPAz6um0HzRff5gb38wC6Wlh9C80O6QrpCu0Jp/hQUjdUA'
        b'nr0YDTqiy0vDj+320vGFTZkqfocT7R7cFazlh9P88Pv8qb38qd3xWn4szY/VU518nx/Uyw/qstHyEbHQroSuxK5Emh/5qy91aEpUcmnBZC3fn+b73+cH9/KDu9y1/DCa'
        b'H9aV15XflU/zo/TJ2s325bTk3OeLevkiNUojpvlidZ46X43SBA/Lf36X17WA+yFpvSFp9/y0Ifl0SL6GP1cze+6/kGpKl7eGP607ZEhdRHSjgkTT/Oj7/LheflwPKjUq'
        b'bCKTwlldx5TyPj+ylx/Zbavlx9D8GMPjbl0ew+oxgUFAZxpo8K2RXT4afkJ3CrnvYKgAc1rgh9YAqELVHupgtQfNlzxFrJ4B+qc4B9s+opxFdo9x8F0kxXfcH6H009p5'
        b'0naej6KcbbxRhI13PwmiKRt7AydprX1pa1+NtS/iL+ae1tqHtvbRWPvo7BxoO2+1HQNL/1C/cOWpuff9pvb64TVeu7mquG2CRhCoTtQIItBSnHvb/BGHJUrGSEMofESx'
        b'3Elon4Lv2GPIIBIaoRwcMt9vrkzUWgtpa6HGWqgb/X4Hx0MN+xtU3A5LxgtPE5eg4KvcNXyvwRPqOi+/jqwuD9or/L5XTK9XTPdsrVcy7ZVMzIZKsJN0B6cm89GHv54C'
        b'pI2c/BqG0YaRHkZ236/wEgobm5EV1FyHJ9m+/adM4XxwwVhkZYG+YjEcGrYCrZuDfzmMgGAjpt515vgEkzcOfHDgiw9FmRhsaQ2/8HEoYkfKYK9hIypyUp8cZSaHPMlh'
        b'uD6LopnxefFZRbPmzkzO7+PIpYo+LoYE7zPXR+Qnz8on609Shf+etnQU6poDbpVB/AwxbpBg7nDYNaMJGCPtiYEHxXduitSR7qDjh/Tz2PywRxQKHuOgMQmxrbOXEiUI'
        b'1FgH6vhhKIFzBErgHPEYB42ZI7DUQjGWWjjGUgvHWGrhBEttKAyaGMOgBWAYtAAMgxYwCidtMk4gxgnEOIGYJLB3aUrVWftprP0YpDV7jLRmj5HW7IMbk/tNOJYB/dR4'
        b'gRnbciYLw889ITQxt5zeT40XOHItA/up8QILI8vgfuopA2uOZRIGmf710IpydVfxVRUa50Cdq6fO20/n5avzEam9VPPwl6e6TLVo8IeXr5qrijZ8ufuoFCoLwxWi46Wc'
        b'p/PAV84YX2GWykznPVkdpsrsd7N2Rv0SBx78SbY6votS3s9Bvx7ynZT5/Tz0C1e/uypUJUfpA/qN8R0Tyt5NZYfJ9JviazPK3gnDRSjT+83xtQVqMKVcFaZc2m+Jr60o'
        b'e2eNS3D/BHxhPfiwDb62pew9VIk4o/12+Jo/GG+Prydi1x6luAT9DvhaMHg9CV87UvauKo4qSbm63wlfOw9eu+Br18H0bvhaSNk7KhNVXGV0vzu+9hiM98TXXqTelek6'
        b'ZzeSyBffpAYCb19nq34KBYj30Yjg7KYMVa5Vp9FuEffdpva6TdW6TaPdpmmdYmmnWJ3ASclRZqon0s5B953De53DGU8eWkEkLYjs53GcECkUNGb0myWwLCf3U/9GmMoO'
        b'snTup35rwJj9YQmzYAXZ3+ooHjTa5lHWszjzciyG6X3M9d/fLMIoVTZDUKpYGJuqhdsyocW4nI1C/XcZ2/Crk3MazUfnjQ2kTKkyN3K23LRxQjm3zHiz6XAV1Dwum5Ly'
        b'9JhVZmPgWfHKzFGcxag4YxJnieKsRsWZkLgJKM56VJwpibNBcbaj4sxInB2K44+KMydx9ihu4qg4C1wnZUJcB2UO7Wx0hXKOsayWWhrSlAmGoC9ZUWP8ezKC0whqk/4d'
        b'aqtH3elg7WGVuTeyieKROdVr3jih0brctMxpVItNQKlMG61IezpvNplnzXBEp8twmsSagNNo0WhZzitz3TzCH9w8mzJHghHl0ccgi2ZkJ/9wcBiSOPbAYYgSllYWy+VC'
        b'v5k1csUKaZ28uLoMz+UyabVo2DPDLibPwoDmjL97IfpVUyKvqZQqpASHvbpGIayswSe3hcWlpdJahbRMWLKKAWWfPBzSvK6cwkYwfabFZStkcnyiu89c/5MczDZhfI+j'
        b'25yy8hV9nGXV6F6VtExWX4XumdSinK+sqSsjggxzyBsf/C41GdJcA572lNRQ26Rt3G28bUbbjIm5NG4dLmoXHqpTI2KtYan3t4f4fbvZCPWwKVEPm4xSD5uOUgGbPGOq'
        b'Vw+PGTdUPfzBI84YAPdp1TKFjJid6z2xGBpNVi1XFFeXSp8e3n6ghqP18Ph6jJeackJZf/q9GGN2JDBn7lGCKmmdaGwP7vFCvRED46RFWF+LMUimCMtkS2SKMVD3h+cC'
        b'N+5APtDvJ+UCRY+Xh2phcWVtRbFkrKxECUsr0CtLEYnxs2Ngr7HrhIkV+mUhrkZZklb/CzUS/ms1gvg6mumQKYXCyuISaaXQD/2UZKDXrZbKSitQRwwQFsjriysrV5Fs'
        b'yRimkI+Zi+FZJ3XrFzKkKsbIvD4jqG9FCzMJBiSmMiMw09Ac+mpBg0R+cWnFshpcFShPKNN1UjQGjOP8oL6kUlqmHwSGU5mJwppqabWeEvF9gK6ZmtIPHWPXcZpCWFUv'
        b'VwhLEKvoq7lEqlgplVYLw4R+ZdLy4vpKhYiMQpHjFtQwfjDVzlwJZWX6Bgv9tQYzDDrM44YrYZ10iUyOahgNdmhMJOwkFtbrm62+ul4uLfsVdw5jGeJOYPaE6gKsKaFY'
        b'zaJqF1v8nbKl6iPRzaKKWQa0Ar0fv5kErmBQyZg7CFjAm0PBLXEW1rP1cHfHjOwpv0oJhtiL2T2Vo3fVviUfXnsyzQzYyYe7sgoGKVPwWK0F7IBtHoTwZrkFJZjTQFEz'
        b'F4vhKncGWSG2IZWQ5YWOJDxE5TkktxToBo3m4HhOJKG5XGxEWWTe4lDCxeLCqtlUPTbCclwEL46Z1zT/fIYS3AKvM9Q2wL2m4AC4BhsZ3J6JJpT12jc41OLFFro1BVR9'
        b'LEVUwXAzIVgBG0fQhI2DauYR2bxhDk66wQ5C98h6M4rf8A5FWS8WV4VlUcSspRweDCNkM2eMoOpnUKMOI3kLnDeHjeC5Z2TPfdPEkd/AdapI3b03ywwEWW/x/SXNvyFy'
        b'gibLTz31EferOmr55+cOL+o1ffv4EQu6pyn2Hz/cXfXWzzzH9G2l5plmi1+Z+2bhgbCfYj93u9thfu/Nzos33nvuowdNvCvv3XI95/c6LW4O+2NYyelPWunkrxXHWwLv'
        b'33vzi6SLNbeUz/E+yIwMFX0c/Yp3ycY3uuM/fmXr50F/uhRy6NviM+sWz+f+pbW5O/l+pc0vlW6TDoV99K3Hdz03P2tr/atLdtMrE659N2PhOa3IjKiMPaayBjTf4Lh0'
        b'UPkdDloYjeqRJeCW4QQYOFY1BC4iSMz4KFfBo45D1eeMo003cIUFlVx4KRTeZVTY+4zBWUaPfhReH2AsvSJ94TrGq/pua3jEH56q1itnGcjgi1bMob0u6QKsAoc7pvkb'
        b'lPyLmPNt4ErsWkZhDdu5GXqN9Ywc8mJHe3CDbEaAS1A5wCkDuxHpJBE4W4XxGgNTER9u0be8QXuOut0pAmHhvdSeAcaQwKvwhpxsrqCrTLKkkBhRWcVgM9hsDI7AM6Dr'
        b'd9aLEEg/G4OMMRzlcLkesaJhEuXpo/JUlapK1aLj1R3VWo9w2iOcQBISN+aKlvWMZwq1e6+dv8bOn+AZztA6ptKOqRp+qs4rEOMZuutTD3pMj++1k2jsJCR5mtYxnXZM'
        b'1/DT8ZLbTpWvylcLji/sWKh1D6XdQwnkof5tzzAuLtQ2vcQzN3k8Res4g3acoeHPQAvRY2ltaa0Z7RnoIVPDQ6v2xbbEqtAbvTV23oxvdq1jAu2YoOEnPHR2I0n/zRe7'
        b'i864nnDVugfT7sG/4TFPb1w7WMOJPqP9LF7GKjHsDqTuKg6u4eA6Dm7g4LlfN74e8LA4wgB7nLYXIalUjp2BD/XMnTOJxcoj3rJ/7/B3OxOCT593mEZTt6ziTX4L8ONm'
        b'A3ThgLg8HiLeYF0ZAPEKUF0NQS5khHWDxDsGpOK/CPxoUTREiH763M3BuTs6kDvXEbkjguJg3v4VLEODMP30ecKbWEOgDN2YPBlk11EV9tsBPLlFSLx++vwsQvn5ZgDS'
        b'cO4Gfb6cmHwNEdD/pTwtMeQJSdpPn6diXEcalqGO/AYl9OKReJ3yf7cFDZLx0+eubHgLOmKd+hCR+t+qKNMig3D99PlZMjo/qOUGhPQh+RGxyR4Gs5sxYJ6dXcoZkk0L'
        b'Sm+fvR8FB0yHYDoYEZ0BdoVn2mjWaN5ogXUGjVblFgMIDyMRtX9/hIdyEfufPNsxtAbxZWXYKWu1dOVQHkF96qncsyajNR6TGGt2isvK0IoGrYuK9Utk4mUV+6wTC5fU'
        b'1dTXMsqdYmFpTVWJrLoYu4EdRRIx6+QBLNjJYuHkodC16Jpg4qJEJTU1y3BWsQKKLOKYbChW1f4GRcfAi6KF+TVVeLnM6Kmw7z49hGxxSU0943QWc4a0bLy6wf9SauqE'
        b'UlwlZbLycrS8QyMTs/AcXih9fRNHtKjalug9E46x5sP/0Dq2tLiaLGOfpMMIjhiychf61dQSJ7uV46/hh9Yrsz4dNUgI/eJL6qSlFdX11UvkeoUG8U84ZkYH+UAuly2p'
        b'JqwQQOpkCGG922ehbGipZGhtj9bxY1I1rNmDSSNHRA0s3fGbgkVirFkUlklLFPg9KEUpWlXL8EXpeNoGwpUy8rxcqiB1Fxn1FDyTgsEqiCZzZFeRSeXRT81zKK8yhZ4A'
        b'U+/kzoDqwy+/prISqztqRMLJk6uwPgkVZ9XkyeMqpkiJh1Fkbg2SnIGqt1oSmIpmpOrfQppB5tVrL2rkpMB6tN6neh53Tubpod01QJg1oJgh3bemZKm0VCEkLTh2H8jP'
        b'iYwICtZrkbGSmOmdAU+XjWHgI9EjFGQramSl0gGGT5BWSpeU43Qi4fzgkIVPQzJE34z1UqY4smqSUdzrk5KysubOxSUbyzE1/ldbvKqKuLWW1uFpUCysQvU8oAYakqGQ'
        b'J2dI3zwYC2l4e+E7w5WCTG8JNPSUMbPFCHkJqJC472Ma6PWhQeO+fhjci0FFOqSboLuoR1bLZUymasrHfGtx2VLEGaQ+8APEt3dxA/499tg4tnJ1GBE50Q7LSisUsiW4'
        b'KPLSikp4G43klaLRfXZcmhIh4pt8hbQeDa4DBBAHy4T6KkIjVBXqcckFklnFihIp1riXjUMJsQvjjLayvmqZtGLs+pcIQ0ckI28rri9fXa+QopkDO7UXFtbUyUmmxqER'
        b'Fi2Mry+vkJbU466HHoivV9Tg+W3ZOA+ERwvTqstkK2SImSsr0QMFVfJixWr5iJKP83TEWFn+7RU0ZSwysiHZqvpt2Yoci95vq5coUpGDVf8rNT/mzVkMJ2PV+Ih8/2ZO'
        b'HFr88jpUGj9ctwN5Ki5ZXb9END77DX1cOMV7fAYcljA4aryUiM2qA4vHZ6nhZCLGIxPxJDKIKQbK9wQakUOTjVu0qGHExijXuBOaHo4KjXD6X0QeQDIpGlsNQ7lfPjPH'
        b'jjthD6JdRQsT0YWQuUIyjl8GupRWo/+IzYV4Doocd8gdgpM1nEzICDIhTyRDILWYKaMwfpYkLUnoV5CvQN94vgkf97EBCC7m0eQCMlLjG0I/1Mn1LI6affxqqK9DInIp'
        b'mi0S9b/EwiGyXXJBntBvNuyoqEOdFOUlbPysDEH/GiQ2cFufKQMp+bL6OvnoTD1J3BtPvCSi5NNLfgMiWvywXa6nk2EInlm0MBt/CeeHBC18+sdCmMdCyGPjt4YBKE0v'
        b'Quqv8dL8SXxAUNTQI/gLJRydbvxRLFVaV1cdmFJXXI+CyoDAFBmS7sYftUjy8ccqTGf88Qm/YPwB6klvRqNScgUSwtDYP/7QRPKGZLaysbMxXuUhKVYqVWDJAn8jASvi'
        b'ifJdSU1DtBAfvkDyUzmWWtENVOfjNyp+CMPTMU8VVwrxxROfKJUpcIdE4RPFPQaTD6dkfhDCYiynS0KDIyIQp42fJwyHhzKEv57IkeXFqLQpaFB5UiICqIdaCH8J50eM'
        b'n1A/zOmHuCdxtAHqL1qYgH4xkvD8kClPTD/Qtckjw3exn1jfBgBB/ZNM+4w/WGPYQCSiJcRno+YZf0QskZUigmmJ6NVj9MhhO8km1Lg7ye9Fcyiu13c87MfktRRjioDA'
        b'BYPj8IgBcAncBfsGAJfART/ymEk2jzLhb+ZRcYst/iTzY/DDFHhfTo8DxWUtcQDHwG1mEzhY4ECJvVKNKOHita6JaxjjwSjY8QyBhpoEbwRQAeHwBrFbiwSX6wdx9aho'
        b'GYHVg8/rQeOuZ61lfb/oCIcKKl7zi7+Eqse7ZPDaQrDHH6VPxy44sbUORnrfBHdkEU8Asyh4GezMoxrCTJeYWRAomr805DCQ/1ERzu/MeXHWz1R9DCa0A2xbOBbmP6aS'
        b'ymy6FQ7bnXVGNdRqIRKB3WRjRpZ2s4Ynt2RR1NaP9pzadzkbxllsrfpsf1iWqtNl8UaHuM4Ynov188nJ+879vdFx62bW9hcn3XL/s9lx8ePIdWntqo6VBVPEq/qPfP3j'
        b'+h9jrwZaX014pS8ordtoTeCnWyLVlhu9bK+0JrjV9Vr37Pmh772KnI7W1+59Xfaw/9lv/zlxD2+G5eQJP/adqVFJ37txy3VN8OPZXbc/7Zav0950fTvlxJdxtSe177os'
        b'yfyH7lHL90ffu0xbpv0kmDXnRJn5n97v1L6p+Pbymk9f+OSR/LOXs/9B56ZOsLedmS38ywL7u48uHnm3+KDuq8WrnjFddePMgo3Tzqe+f+Sg4l6p+q+7zcQPwxs2fLj3'
        b'a5sjVVZX5d92HP75RcsTP79v8fPxKb/wJG4ZnL2fiUzInmkGaFnqHwBuV+ghQwheSE0y8V9XWQtOGPBCMlhrwW5wpSiSbMIuBnvgRn+4PSspJw10cimjSraHEZ9sJhct'
        b'SBmCFWIL7g5AhVwpJy5Lqguch+2fthiN3kIl+6erPYh/OnglDFwZ4VdA4jfgWaDUlEGDuYR4+4Ic84HEDyeEe7F5VRMHPIv6SBfiRwY45YgpeD4jE+yFl9JYFDuPNdlF'
        b'Jprwe7oTx3a9wkH0jxG22hYD+nADAMhl/bbtTFdKKNa4BamXY/9zTkqFhvif0zlhvz/2Ip2vn9KCQYb2Uq3oEHdxtA5htEMYjixg6Xz9VQpsXNNl11XWHXGtsie0J6En'
        b'lI6YcT8iqzci616pNiKPjsjTSvJpSb7Gd5aSqyxstdA5uamM2mNoJ3FTUlOSzt5V5aWx90Ef/Vv9db6TlTjVsei26NaYgZSf4C3R6VrHONoxTsOPw85rF6ijNBPDmzg6'
        b'u4nKMto1QGOHP3pPB7STv9ZBTDuIu3i9DuEah/AHrpM1/tla1xzaNUcjyOlnc+yDdUFRXabdXpqg5B47FDAfbG/kp7bTCiQageT7B05eOFvBg4HO1V9ZpU7UugbRrkEa'
        b'QRDe/+znoAj8zeXYSHR8SVMSzfdS5dPY2kai4YejTxeX+R74fP/AQYhBVCSDgc7RVylRc7SOYtpRrOGL9aRtJOhbjp1YQq5N4kQKTjRLDOJAoXmiPwf68/DvMEGSFfWS'
        b'lVmSH+clgXmSJ+clTx76zWwTT2C2iQd3NjD43W+CAhjBbIP7xE9ktqV4n1hFDYIY5zqxWLgSf6/gdzN9+Ss1hg8dMlkSHzpcvScyXiPVaKR3zPA/442sXMSu+zs1wqux'
        b'2xgzuTczk3+3jEs9LuTjE1wWp81r9O5nzoJtYIu8HgMY7ubCO/AuhUYx1rryqYMwArCxErxgjhpsNnge7qNmL6onVuhGBavyw4OKwxhcv+fRmDa7grxIPWkta23MY+Jj'
        b'9SW5nAEdtAOb6kLDjFaCO3qT//PwIoGStIQXgTI0jAuPgRsMSgDcAo4SQh8nG1ObVyCBQ7i48pRvHWO5f9nVhopJSaao2sWZ7glpjE34KS9r6nWvBHzTYt+yOUzKomUW'
        b'VGdcED5ZVnlqRQCTckWSBaVwjCDHzV5YuoJJKZCYUTEREnwOy+LNGRIm5bxp5tRLlczNKzM9mZtN5cZUZ60TzpLFVJMJTNkmwYO1+TNnOsfMRI2URIGNoWAvKRvcAE8v'
        b'CA0KcgftGMkUdlBw4zM1TNQW2AHP55eumElhLLDTKAbun0TgLOEhJGVsGQAXANvs9PgCu8FGxv7/QOLaUHAWnAgK0gMM2JgR+/9g0M24bXdXgLOUO3wOPEvu16OM3A7F'
        b'wA4owT4qJALcYiABtz9TCJsxVgCifR2FLwAlyUI92AK26cEB9mLMdQM6QC7YTUS5dHBgQv5MIehyxICKV+2NwPGaagKNgNrxrNcgOMDsKQw8gGI+Y8GPq9syzIRScdzx'
        b'YCE+FuDA1KyZ2IRqnOuNb1aunrKSgUYo8IRb8hOXzcRHteGzVDG4E1WJx60OZ3uqJz8P8/ICKpdUqOcz9fkzgSoTbBNRVPQ6c3gc8XYnA9XamATb5JahcEc9qjA2OE/B'
        b'O+AYPCrz/Pw2j5xUOvi3d07NuolkMesjC9+/6ezr9bCWd/fZ/dPvBahOO73qEZb71xP1xskd/LBGq5t1Hx0rq/ywYMV1n+BO6fypfzi8JvaLnIZNfNvUv7yyMG5diNHW'
        b'5j/Nv/fOtNvfzDhYZ+U0v789zOzsP8GN4mTjA3sqs96nbWM+2iYxiQvovG5eO/u9OeWtCs1rlZ4PUj6bMb9/i+fZr+TSVS9r54c8fjVjm8dK7+n3thelfh3yVqOLernN'
        b'psBw9smUGX9Mcvhg9x/255gc4ZhMszx+yWOm13vPdJxTcD6Ngxa7lQ8KlfOqa9UlEbM8Tyzd5djwkTSz/ei1d6b0Tcv98ucd4RXbtjQvPLZ5f0jkuZzHP0WflonW8H0j'
        b'X85f/eZr7c2nit9427pi67dX/7LItXRX7cHXr81LSfnlrQLRP1+p4FRKbge9dWzxOcVr3M67bacPeAjSil5fV382ecWpb+0X/bLebGWBa8bPP6knvxVOy+6s+vgXn0e/'
        b'7K/J/TKj79nn3jbabGyy6AWW7SeNa8yXifiP8aSFxKGdYMNYB9i8sJOWYQIYuAOPEXvpNbAb3vUnUp3ECO5Bw4YJfJ4N9ilWExlSBg7C01jQ3wd2ZrIorjsLHIHXE5gz'
        b'eTcE6wzem4zT9f6bLjPP8RqqGGABe1uCjkew8a4tZKS+y0HgaIYFewwnx8JknmleCjkpOAXuqiCHAS/DWwOnAcGOCQz43jXQ5ceY/FuA0waTfwW8Tuz5l4DT2HFeTqbH'
        b'1BEm/+i5fQyB4+CsQo9NIEBVoIcmMLFjcngX3GwYDgmAjzE6gUYO6ATXwRVSxkXw+XIsQ8PboJWRo1HnVtqTY5VVC8DJDGLLnwlvGSDzrMCznIR58LbeLD6GTRABwAXU'
        b'u7aTM5UEEiA0njSMYyJsZCisttQD6lmt4yQVge0MAN5l76VDsADIUUawyYcDm0HTfD1AIRejN+Azk/7rDEcmYRs8Ssg7ZYMjAxb+QAmbGSv/RNDCHObcEQQ2Dkd4wAcq'
        b'axZywEWwGzYyJ0NPmIHzKFEj3DTqdCg5GrpWKDJ5aoEHD2ZC4dBjcd9Q2AXPoKQjLyqTlSqIaD1Bb4Gf50ZNcmriYRfM5jqhFy0MYmCvtMIoWhjVT3nYiB7hoCmVcbjV'
        b'0DqtfdqAky/iK9q+dV77PLV766KmlIeBU7CXr7PrO9c3JSv9VIVaR38tX/yQ73af79PL91HVnVl5YqVO4KQTuKomtk5ANGiBpMuuVxCmEUzr5msEyT18xoXLrI65XSyt'
        b'IIQWhNwXRPYKIrtttIKpNIHbap9wXyDpFUjUxVpBEC0I6rJFsr0dLQjHcVZ6B1+5DGxfFxu7D6MFYYxJXirtHDwW1e6E7sTuRFoQp0/WnqUVTKYFk+8LgnoFGA+AYJLp'
        b'8QAEkcMyHtftoBGk96SMvlnRk0onFdxPWtSbtEhTtESbVEEnVTx1MhdDTSzqQoWZQgum3BdM60X1hIodR7LqqrJDf3OOu3S4aLF7MxdStYMfVJKk9rRWq3YrVZ2apapD'
        b'BXpyhKtO4Iby1x/uFDTxEeXk5/AYB99FUALX/SuUFVoHX9rB99EUJ3sRxrATYeQ6xB/4VyTl5nGsoq1CtUbrGkq7hiJ2shP0U+Y2EQ+9fM7MODHjyW3j9uRmJfVAe2PA'
        b'AkE0LYi+L4jrFWDAAj2g3yBDGfiq38ZUgopg6o2KgILvbIcVQe3/yM7UOwIxqc++rH4+JXBpshjt8erJh1GJx6tf724f48VFPaW3mE92+x82lp+J11GPsWQ+1G+sETXU'
        b'qxtP77uDq7fyw/5jjQb8doz09vMf8R9b9x01YvEwlscf4+x67H9xbRXo9odnhalIrJuZiqbe9KxMcHZWKpoJGsUBIiMqFW41rl0LLxMZcCmSbruR+HgFnkByPj40z6lk'
        b'oeluDoF88oEny/yNqQRwFONAgefDGecCe9GErfKfAhpz2BQrj4JtCfCUrPVCDkv+CEV/uz9sd+7zViDI4lrzXSAv2WS54qUet35jF5VtpQ2HwxG+2CSu3DfHZtnpgP9O'
        b's8jbmedxfU/IS3flaz9b8pjd7Kyy2PnQ1LPuNYeCL2NWRnZafhYWuv2TC01w5/cF3rfentq2x3Ldurpbyf/spe+nvBHp9GPQ/rfL0ycp75m8mqVs3nEi70Tuxqy2X+a+'
        b'WH3b+0zYnxYct4/dWrLjs82iyTNsXO0SVrb96Jma+mDhinWdLyzcUxF4JyJ185/T75/Kq5OsKP/7j+vzXn9bwvnuzo+9XBd1j9Xayn90Rpz56eit5j98xZ9Ya3Xxi1dC'
        b'uz0SUubWNXyzPPuL940PpiTBM6IJROvl5MP1hx3uqcRpJncKC1yMgmfJZLliEjgFd1rFi7P15sMmcCd73UzwApnpV5osQrMb3MvORpMhmzLKZjvDbtBIlGKhpcTrrjgg'
        b'jcSZwy54Enaz4e0AyKAwOa9BU+RVeG2lHkXYFJxBggUbnIT7zMlUbAKvu2WIMebN9kwkypjHLQAH2VBpDNqIQi5NCtrwGzyWBOZI2FhMmWwEnmcAnnbB0/AwnsZ9Jw1z'
        b'BgpVwQzA023ECYdR3ut90uBuJP0ZLWJ7TgLnGUyiA6yl/oFwxyoTJC8GiNhI/DjGwRh34Abjg3OLEzyEBAS0CDkItwdm8yijGLYD2GVJcl0LWuDVDNgCtg6wrSmfDY5L'
        b'vMmbo0vQ+nYn3B0MOvWVlsAWwCN2jOzTVoUWUTvTEW0DfDIWENETO0h9y+GNEv/ADHCYgQsyAmq2OBI+92/j9hp0Kcx4Z0IQFgfGO3nxCsY/6Am92i7dneJPbJlyKHZ/'
        b'rMqLMavA2qModULnjEtZ57K6vbTi6bR4OrnZk/CHdJB+T6FNmkUnzSK3Hji6azymaB0jacdIDT8SI6tatFngSQsJLHYOh6L3R++LaYm5b+fXa+ennqi1C6LtgrBvTn+d'
        b'o7vSV+Wl5qgXaB2jacfopkSdj/+ZZSeWHa/qqBpUkbWaKbnKMjR9YMKqWeowZuLRkI+O73AobX/aPj1QZVPGQyeX9inHYtti1V5ap0DaKRDT8NUJHI+ZtJmo+DhjSqth'
        b'72Hb+5NA/x4Xd+UslUeH7xnxCbFa0TVL6xFNe0R3J2ld4mmXeERtkn9Pns7Z9VhqW6pqVmt2e7Yyu5+D7pIoEjzCwWNq2L2xAqyQG+t2P8eQJznWprxsPzF5Cu/lKdzk'
        b'qaYvx7JQyEyApswE+M9fnQUZ9sB7FAOatnGZww2t+eUbKAP85hrhr/o3/Q+5OyU+IEXcEYbXzCUpPpv8zhbZjgSTMWNRQxFlnsKgBYMf9vFkCmmVnIGE+cZQOyKb31G3'
        b'PqQxcPVvGPmPaZRLuFEG7OrdsWTyFns4dAyXa2mN0U2s+y0oK/vG2SqOKlG5qqu0J/+eXU+abpKzyr/brju/2/ReImJNq1yMeITCxyTsN6Ji41j9HF+MMvOrwSPekCe5'
        b'+G4eaximTATGlInEmDKRGFMmkmDKOHkq/XTW2EUpg0rjhFFpnDAqjVNEY8YITJlwjCkzBWPKTMGYMlMIpoydUxOiQFCX+MEogV0oSmAX+hgHjYkjEsTiBHEsnCKO9ZiE'
        b'JM3QtwTht4Tgt4Tgt4SMgrYZI4EJqV3UE62yWEp5lx3ziwkxiJNCmaRMUk2i3ad0m9LuCffdU3vdU7Xu6bR7utY5g3bO0Ll6KMtUUbRnVLcP7Rl/33NGr+cMrWca7Zmm'
        b'dU2nXdMfcVguGbh5BJm4klGIOv/AO/qN6lmWkn7q9wkfGWOaj4dSruZEWbr0U78erGCRqlB6aixdtZautKVrP5tviQapXw0ecSgrt9HpB/2ZG4FLoFOO1TlTeEShw6Ms'
        b'HdmwWWEmYmXLktcsYMvnoi7xyeLz6/bm5DwbZ/3ykrkTP5Yd7P3llORa4bI1jw43PPr01ZOvbt653bjqhPu3JW1BD//yvWX344zomekZu73nCr9578c33vlaJi4NLbxs'
        b'/87lnzdeOsgx8nqm93Vuz8G3vop/5PXN159/lJ3sqcuo/bDl1Dd7juy8ZffGL3k3HQrWFdZVF77NffhFuX/eTzdO/lQ040StW9W7jxZF+696eDx/yVqzz8pm9K09Kon/'
        b'2PKQf31LJd18pn3lf1E1m5yX5u/9IUzlvrsik/WGzObWX6sV5yy7eX+edvTHjsQtb+x+pbA86FVd859ndl9M3FhVONWtafkvVfXb6M7HAZ/fmX4rM8B828cBPuH3Ptn9'
        b'4MS+2Sv+IUt3CDvp3xs2YdoXoUtm1ux79JfClUXmj/dnlwUv/GBz3+013cvzntedVK7vvpRjd6X17x82nv0oOvz6a9Wr/M9/8cmBmxuaVwVm/ynki+Nv/dfDSn/OB67t'
        b'/Q5vZtavP/JHEecxQYLtXAU7INZ/seYGRlJwT5GQgZa8AnfGMzuidvDCMFfrYJMvUZEskYI95mbwwDi+08ENuEHkNXIYNHli8J8YdP+FYdqLEaniyL9R4/WIkbvPpKio'
        b'sqa4rKho9cAvImv9mTNg3YgG7zDK0r6fa2zqoJtg2yhvCtm+ctdKpfuOtY1rlXKlXBWiKu4Ib13dvlqd27Zeub7LC/3Vdbtfq+/OvdZwOeBaQE9ST9I92xdTX0rtDcnU'
        b'hGQ+EDgqQ5TF7eGtpu2mqnStIKDLQSuI1MRkax2yNXmzNAWFdN7sXofZGofZDyYKVbb7qluqNdZe/RxKMIfVb0bZ8pviW+wbExoTvu83ZpmmsXS2bk2SUxYaSYpWOIMW'
        b'ztDaptK2qRqLVCywRNqYevVTv0vg52uKhqbfGjzCwePBe7NYMaaO/dSTgqbCR/jr8eDdZ1he+OeTAuXER/jr8eDdbBZlZt3PruOaojHs/2L4iISPmd8clNldE/XZVZhS'
        b'Ah+1udYhtNGi38jEFMlq4wUT6zimzojefzR8RMLHQ+8vNSa1m0dK878fPiLhY+a3oS5HJpJj+70d8dMT7Chg55gg0e+Ru/Sxi4r+xT3x/8xAhrXpi4ef6hhL9rRhY9nT'
        b'MHjh2Vn+GaXXigWzWNZYwv+/F/xuNt14BX3BNJ5DvcixirfhyPxdD7Dk19DNPa+8ULU7yowdb528pugVXtb0pNpJC3o+SVpUHPT3Ny2OZKprPilZWvaht0vKLK7/f/1T'
        b'/Yv6j+18WUjZq/vOxO3bcV5d5r1f/XLuux3fhxp/8+DrrI8eyd7+h1/ND8fyz7plhB9c3bx2XZjzO9cWhJ1t/uPRgjWhoo/vxRpbSd6Z9bHV4XelD65k3Hl3iS+PH2Yh'
        b'jq7964kJezewtgqKd5me9gtOfImdwZ9TvNvyxo9X/nGm59vKlR5fHeu5EbTOyFQ0gahPjEIXY8VKDj7DtisjDBw2pszBFTZUV8OtJMGc6syMHAm8jNNg3YsNvA32FGC3'
        b'RycUJAHYtq4c7AR74V687QF2z0gBe40pK1uOq8CXcVF1ayErIy1rchbcDvYZU0ZctokbOMFEXQWNy+HOQCNwMIxi5VPwJGwBW4jA0TDVzz+dB++A4xQrg4JK0DqVaGSC'
        b'AuFp7OFvD3oZ3BXdwKLMRWzYNEdEtCrmQOkmH4iFd+VoTE5jg6718DmyZRQED4KdGWRzEB+i2ibBblPhDk423ArvkPeuMypC8XBbMnOoEByzMyWU1/sWEtUjcyYPnrfh'
        b'URZ2bHitBtwilG3ngHNgJ0pQSxI4gHM8ygxcZYNrYM9SsqMG9maA58HOkkx4xQI0rlxeD68ut1hez6Ic4F4O2GU1lVSnBdiZnUHAynExHMFGXKg2NjwBDkYRcQq01qNK'
        b'QhXOEwRmIElqDz4Mhq+NKScvLng2EW4T+T21JPV/UrAaMjL5ERErzvDvCULWMCAJk2HYIcWsIfgReLBypHh2G7Lxn86Sf9/StdfS9UiD1tKPtvTbkKLjmm3L3JSpsXE/'
        b'FanlimmuWMMV67iWG9Lw35AfbprhHx3XVzPWR8eVaMb66LiemuGffqN51jw0efx/FTYIKQv+hpwhey9ufZxKaXUfF9tN9/EU9bWV0j5upUyu6OPi7ZQ+bk0tiubIFXV9'
        b'vJJVCqm8j1tSU1PZx5FVK/p45Wh6QV912Myij0csnPs4pRV1fZyaurI+o3JZpUKKLqqKa/s4q2W1fbxiealM1sepkDagJIi8mUxugKfrM6qtL6mUlfYZM0iA8j5zeYWs'
        b'XFEkraurqeuzrC2uk0uLZPIabAnaZ1lfXVpRLKuWlhVJG0r7TIuK5FKU+6KiPiPGcnJw0pbjg1GLn/RPKBzkRxKY4cckw1hxjH+IO21YrDIOnrr+fw5/t1kXy1AvmpnG'
        b'C6kXhVbxAZwfTMqxaXdpRUCfdVGR/rdeJPnBUX8trC0uXVa8RKrHgiwuk5Zli0yI7q/PuKiouLISSWCkZbB2sM8McUudQr5SpqjoM6qsKS2ulPdZ5GEr0yppMuaUuji2'
        b'nrkZNsct+4NJTFVNWX2lNLYuhc1ASsjXoaCfw2KxcJm5/RQOrChzyw3G/dxKaxa/nxoSLnKnTG3umzj1mjgp07UmvrSJbz/FZoVrxLE9Pj0+L/q95KcRp6OPzsRaZzax'
        b'UaxxCNWahdFmYRpumI6y1lDWTQIt5UhTjhrDh2Tv/wEc4lcr'
    ))))

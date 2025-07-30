
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
        b'eJzsvQdYW0f2KH7vVUH0YlxwlTsCJHozbuBGBxvccEECCZARElbBNu4VDMa44G7HuIMrNu4lTmaSTbKbnuxuQja7aZvESTbb95eXzSb/M3OvhGQEcfLf933vfd8z5nKn'
        b'l3PmtDkz92PG6Z8IfqfCr2UiPLRMEVPOFLFaVsttYYo4nahVrBWdYM1jtGKdZDNTKbWoFnE6qVaymd3E6jx03GaWZbTSAsazQuHx7Vqv6amFM+bJq0xam0EnN5XJrRU6'
        b'ef4qa4XJKJ+pN1p1pRXyak1ppaZcp/LyKqzQW+x5tboyvVFnkZfZjKVWvclokWuMWnmpQWOx6CxeVpO81KzTWHVyvgGtxqqR61aWVmiM5Tp5md6gs6i8SocKQxoBv8Pg'
        b'15sMSwuPOqaOrePqRHXiOkmdtM6jTlbnWedV513nU+db51fnXxdQF1gXVNevLriuf92AuoF1g+pC6gbXDakbWjaMToVs7bB6ZjOzdnitdM2wzUwBs2b4ZoZl1g1bN3wB'
        b'TBodvii31D6nHPwOht9+pANiOq8FjMI71yCD9/3FIobEMSNNEcUTfBjbaHjHVz2ScCPenpc9G9fjpjwFbsqYaxqQr5Qy42eI8cNh6JaCtZE68aYltZYMc3kO3ol35OAd'
        b'LOOVwaEOvH+cgrMNIBka8El8MStjSXJEhoQRi1l0HN0baCMTgk7j9gVZGREZSrydFL6AdkkYP9wgykVtC6H4cMjjOQttRI1QSSs6EVENfdoBtXihTg5dX4cv2UZClmXz'
        b'pdnrIc81H1S/YrkNdy73WW5jmYG4WYR24D2oDrpKBlWBr+O9qBE1R2Ypw/DOiiK8AzeTsAczZIwYbZ6Az5ayTmg4xD5lagIzHmLMT4NZ2RABXmw9oOtaDuDFUnhxFF7s'
        b'Ok6A1xZneJHGB/SA1wgeXt+tkDI+DBPQqq6MGD9Hz9BIw3COArE1X50dGxjHR75T68kEMExU/rL1ERunm/jIU2skDPyVP6NdE1G2oJhpZwxeEF0aGyLuyP1yLMN8OP5v'
        b'3M3oz21fMgZPSNg74hDb4dFawUxVx/wu5j15MB8tXfw3/xb/1KHi/A/Y7wftrWlmuhibEhK8ItARgFJj5OzQUNwQma7EDai9EO8rCs3Mwc0RqgxlZg7LGP09J41Ap1ym'
        b'29s+4qn8dLsuD4ZMdpm3Yzq5Pqez7HH0l/aYTp9cM2nVFgyPRXjH2II5ynkcw4mYoSn42Dp0xRZIkPcEPqIv4JbgswwzmhkdG2ELIni7Y1hOwRyoNg+drWBmoI0mmhld'
        b'lcnxXhFqjmGYSCbSN4dmHohP1uK9LHpgYxglo0T79HRZ+OHz+GpBzmzcJGG41WwKujAUb9XYxpJGt8n9CKKHZwGCbs+eHTp4BWqPSJ9LVp8Kt0vQJnQxgPYb3wW0b0Kd'
        b'UhU6yTATmYno5nT9jU2vcpYTkBopyl3yykg/NDVg64eH9LfenzHvH8FD2e3PjYz6YFx8W0L/+kuaVz4e8P6WUyGbA+LqSrw9X/po3P/6/fFU3yHflEVe2b2/MuvcC7PH'
        b'HX6n8813/Sp1C/KGfDGk8KkPN/mk9H8ttvKErmV/TOJL/V+1vHgv6O2MmDXKX8+8EPrutr1/+FC9//niyNDJ/4ldO+DSx3kvpCnnZb0x54Pw/3ll49uvjDV8MunO175r'
        b'Zk04/cUVhcRKljjaq0YPsnBTOG7KUWZGZKBNERImCN8W4TrcmmUlVGYJOoC3hGcqcX1Gdq5Ei9sYb3SVw8cqx1hDIHm5Zny4SpEZTsmIBDUFMv54g8iUnGUlaxjVDxzl'
        b'TWbQBsu+IRLoExOI74rQpQl+tHJ8YelKTEhMM94BtDCZRRvxRXQV3x+l4Lq4UIWZ4IzCm/75GQ+Cft8OmFhmNtXqjMAcKNtRAcvQ1Uzu8jXrjFqdudisKzWZtSSrRU5w'
        b'drKMDWJlrBf8DIBfP/ghf4PgbwAXzJql9poVoi4pX7jLo7jYbDMWF3d5FxeXGnQao626uPhn91vBmj3Iu4Q8SHNTSOf8SOewnJOyHCulTxvpr3JlRHgmbsrKUKKGyEy0'
        b'1QjsIDKTZcaiq5LipeimYy2Sf2Lhr6UCHjrC3oG1a9kiEfyK9UyRBP5KtVyRh9avjiljtWKtZItnkYy+S7UeW2RFnvRdpvWEdy+em5aJtF5abwh7QxhIB4R9tL4Q9tGy'
        b'lL76d0nn0HnKpfP26HugPaUioStkkB52EhHF2Fk0VMLTG1G9COiNGOiNiNIbMaU3onXi3uiNqAe9EfPk+50FPP3NT1vn86pEx+hrzw0RW/Ig5W3zoC/VUcteLvlcvUdb'
        b'r/lCvaP8ou5z9cslRc8sxh27orfOPnpif+BzeZo2jUFynj2v/qV4d8QwnxmqYTu8F6Rs+GJQyJxBm0KSYpnqlwLWh8QrpPziOoqPjAinDI+wu3C0HR+WMv7orKgW3ZhM'
        b'8R89HISudGdZPk/E+ESIPCbhQ3zyFbQVH87CjePZbBADFFJGhhq4lfhOoHUgQYaT6EoJIVdZGegSM2geI03iQmJTrIMgTb88ETXmAYMXl+B7jAQfZYFitaM9NHFcAmoP'
        b'V65GO9IziGQgw9c5tEWL6hWcExKK3K0mipNdsuJivVFvLS6mq8aHzHxRAEt+pKyYrfXnoa2y5+JXi6RLbNEZyrrERGTr8qjRmS0g3ZkJZMyePNYL7RJMN/uSh79jGZBG'
        b'FjmWwbkAp2XQo71SzgndHbilEnCrjBMwi6OcTASYxVHMElHM4taJ3GEW0wtm2cIIycCtcm/cBKDYCewXNxek40YAWO6AjNn5lLdNwSekgfgWvqsPrtnDUjR/8ZnVX6oJ'
        b'jr1YFhkUrsnWfKUOKK0oM5SIG6KV6q/VC158f9qgl585xDLHn5WtHrpTIaagQ3fxcbPGK4s24MAI03IrEbPQZdyOOnEnEONm3KxSVlOqy4G0N2zwOjHaiprnUMQpiMNn'
        b'BeygqKEcg+/ik+VWKjTewRtRa1aeEt3E7SzD1bCpAWgTD0LOLTYAzSvXWfVWXZWAEIRkMSVerA9bG+QAjSMLX5WYArhLbNRU6XriAGcOdOAABT8IU0ypA/zH/ZzB76aN'
        b'/z3UpVccCCfz1pKH77lBAjsK4FZcT9FgoE0vfjVfZAFRhfn0UHgPJNg5k6LBV2quIcYW9U7U6ShxbPVZEXNpmay4eZVCRNGgCO0L7caB8iUUC9DGMVYilU/Fm2R2JJiP'
        b'z3fjAY8EO5fymLQ5AtVTLEjEdwVEwHcH5Qq8rffVD/C29IR3+WPwtrjCW8IDk4C1S1KjMdjcQF3kBPV+DtATSa7CAfrDAe5B72jO/eKP4UFPBFu2TPyEBKDcGfisUKUr'
        b'8CW5tkgyl4dq0TaiThXieqVSNTs9cy6uz0MncgpCqfyYDsKkimWs+IGndBbeYlNAmcLSpJ7osqF/N8ZQbNHhi/p/R7wktsyGIul1b36p/gIQxjAzryxsQJgmXWMAVLmY'
        b'/4W6WlO/77yuTfO5+tWSl8si94RqMjXnNQGlzEsDM7dsfu7QwA5rVIRWq03XyMo+yBYxa5cG7Lo7wS4G3kLn0W5eUMOXJwrYwktqNjOV5HD9SKAKLlQHncW7V6LLedZR'
        b'pIpO3KB0ojx472RnpFOjA1RcxJdKqCL4tK2b+uC74/ERyu+m4WP4YbjSiSvdwTfRlmzcZkcRca9yHo+bUls1Ee+6+ZLBS5DlAthaXwFb+DzOdIhnOd0I+Tj2A0HqZkoU'
        b'K4kOUOXAyn1Bzljp2o6LpuVKi6ha66BFbD375Iqq2C06inL1rf1ucVSoGVblnaVJL/8K0OWXJRVlwZo23bTTba9z10IGRim1BF+2a87rLuq4l1Tqy5rFLy741WJciPOx'
        b'AeeH9nv19WcXiN7uD/zHj8n5NqDyg6HAfwgAJ+IHfjwa4NP4goMBFS7hwduKzmOeqBRNc4C3Ah2lqegw2gFksDEiAzctigaVSrqUG41voNuUKWWlZQuyTKsviDNUmMFH'
        b'/d2DvC/6BMK4xWoWaBPRsBlrABsM1Anok183wSBZ7LTO90fAzzpBvj88bA7IN7nQo8eqV3C5ZqJbK3yJyERYHagIXsXFvKUL3n2Ki5fbNAY+hSeOslLAmXKTeVWXTBCR'
        b'LFQM6pKW6XUGrYVKQpQfUspIEZH2yU5n+9SG+CGQSSkgQyCFZZyYFX44P5mPxEcSILMRBjEU7URN3pmCPiHz4XDTOjXepXWvURDxykWj4IrEWhHRII5yRZIWRittBQ3i'
        b'BLuZBe1CRu1knl3SGUYg26u+DZ6uK9FbTaCRRWaZdVr+9VEAXXmPSBPfBs3TmWtt5ZZqjc1SWqEx6OSxkERG861Pts5aa9XJZ5r1FitEEvXi0S9gtP88BDOUZTJaTSm5'
        b'MMPy0FStWWexwPwarauq5XNBHTQbdRVVOqMixSlgKdeVw9OqMWrdljNqrPi+2aCS5wN8TFB2nslsfJJ87iqr1OmNOnmqsVxTolOkuKSlZNnMtSW6Wp2+tMJoM5anzJir'
        b'zCadgr9zC6zKDNCnVCmpRpgwXUohcD9DZGqlRquSzzJrtFCVzmAhPNFA2zVaakxmqLnW3obZmlJgNWvwcV1KvsliLdOUVtAXg05vrdVUGFLyIAdtDmbeAn9rbU7F7YGS'
        b'FaR3RJGWCx2BKJW8yGaBhg1OnZdH95oSk5KlMxprVfIskxnqrjZBbcZaDW1HJ7Snk8/C9w1Wfbm8xmTsEVeit6QU6gy6MkhL04FAWUnqDRWiFPY0+Swd4A4+XWa1kFGS'
        b'Ke2ZWz4rW5EyQ5mj0RucU/kYRUoGjydW5zR7nCJlpmalcwIEFSkFsIKhkzrnBHucIiVNY6y0TznMEQm6zhqJqSQ4rMy1VUEFEJWNTxPLRSWZNX76ITIjLTWXpOl05jKg'
        b'E/BaMD9jZqFymglgI0w+XQt6YwXgGqlHmPZ0ja3aqiTtAMEpUQltCu8u8+4unsy9yyBiegwipucgYtwNIoYfREz3IGKcBxHjZhAxvQ0ixqmzMb0MIqb3QcT2GERsz0HE'
        b'uhtELD+I2O5BxDoPItbNIGJ7G0SsU2djexlEbO+DiOsxiLieg4hzN4g4fhBx3YOIcx5EnJtBxPU2iDinzsb1Moi43gcR32MQ8T0HEe9uEPH8IOK7BxHvPIh4N4OI720Q'
        b'8U6dje9lEPEug+heiLCezHpdmYanj7PMNny8zGSuAsKcZSOkzkjHANRYB0qRPVBtBoIM1M9oqTbrSiuqgV4bIR5osdWss5IckF6i05hLYKIgOF1PpAWdkmd3qTYLYSi1'
        b'IDGkzMenK8wwbxYLbYBQPZ7HGvRVeqs8VGC9ipQimG6SrwQSjeUk30x82mDQlwOPssr1RnmhBviiU4ECCgOSkk8trM6VdbNxZRH0AghGKCnukiCUh6SxPQvE9F4gxm2B'
        b'WHma2WaF5J7laHpc7xXGua0wvvcC8bRAjobny3TOQS4B+YTGWXUrrY4XoESO11jnrBZHNh4QaTpgx+VOEWNTivRGgAaBP22HJNVCFGG9QKVdgjGuQSA/GosVuJ1ZX2Yl'
        b'WFOmqYD+QyajVgOdMZYA2jogbjXj0+WARBlGrb5GJZ/J8w/nUIxLKNYlFOcSincJJbiEEl1CSS6hZNfWo1yDrr2Jdu1OtGt/ol07FB3vRkyRh84RZtUiCBqKbsHIXaIg'
        b'K7lLsotPvaU5SJmb9Dz3rRG5y128iyjW+xj6SO9NOvspmWN6b9lFTnuSbEAq3WVzYQEJPVhAQk8WkOCOBSTwLCChmxonOLOABDcsIKE3FpDgROoTemEBCb3zscQeg0js'
        b'OYhEd4NI5AeR2D2IROdBJLoZRGJvg0h06mxiL4NI7H0QST0GkdRzEEnuBpHEDyKpexBJzoNIcjOIpN4GkeTU2aReBpHU+yCSewwiuecgkt0NIpkfRHL3IJKdB5HsZhDJ'
        b'vQ0i2amzyb0MIrn3QQCB7KErRLlRFqLcagtRgroQ5SSmRLkoDFHuNIaoXlWGKGfdIKo3pSHKZTxCF2eadVVayyqgMlVAty0mQw1IEikFM/JTlZRbWS1mXRkwQSPheW6j'
        b'Y9xHx7qPjnMfHe8+OsF9dKL76CT30cm9DCeKEPRKI75fXWbVWeR5+XkFggBHmLmlWgf6MC9MdjNzp1g7+3aKmqUrwfcJp39MbCjn4wWpwR6KcQnFpuQLxhWnwj3MLtE9'
        b'o2J6RoGaYyBKscZK5FJ5gQ2q01TpgI1qrDYLEWv50cirNEYbsBd5uY5HU2CH7swACqciesLc9Vpa7Eczu6nfDVNyX3fPjNTE1D07chC+5YLIS6eyjKQLk8y/xzi9E52w'
        b'21L1LZuSq5CZyZ6bmdg/zcTmxu+AEGOpmRjEuySWaoPeah7isO+xj9vyiKvbWrs5ktryRBwr4zhOHE29xNCREXiHhbh4bI9A7WJGlsDhrfnrWHTmv2THK1N4dnmllpaa'
        b'bEYr6A1dfmkAbF7f0FTrDI/681Y8Yvn+dvB0AH8VyBTESCrnNR5AXj2QHMhCbK9dYiL7uFjx7kP83CpeojFVGHXyApPBEJkOJMmozKolBpbuYDeRS5mfVSTnixFDGiGf'
        b'Fr3FxkeQNOcwv+hmEbsfL+DzDaXNVRaUVhjwfQC+AYQS52BKms6gK9eS8fCvgtWl+z1GUJBS7BNCBX4iEeqEtW3X2uS8VCToft1WKkHro7I60fcgM6wuK9ULhBpocwY9'
        b'ZKBvemOZSa6Up5qt9q4IMRlGUvKxSJItxl22mB7ZYt1li+2RLc5dtrge2eLdZYvvkS3BXbaEHtkS3WVL7JEtyV02EDLyCgqjISKLBwwRdnU0MqZHJATkOTogmHZTrNym'
        b'knebYiGSR2m7bVQlJwK7Xe3mba7dYJRnh2enzLQZK6mXq85cDhSqllAVEp82Vx6XzPPZMnsWYhN2Fy/gDZ/kpsKUIqoPkIGbqzQk0YEi7lIcqNJbsZi+irlP5FGoj2Lu'
        b'E3mU6qOY+0Qexfoo5j6RR7k+irlP5FGwj2LuE3mU7KOY+0RSLLmvYu4TKbij+oS3+1RasG9E6R1TovtElV5SacE+kaWXVFqwT3TpJZUW7BNhekmlBftEmV5SacE+kaaX'
        b'VFqwT7TpJZUW7BNxekmlK75PzIHUAiu+X1oJrGsFMF8rlUxX6PQWXcpM4PTd1A/IocZo0BDjomWZpsIMtZbrIIdRR6SibmujwDkJwUu1lRG7mIPI2XkpJBHK282Q5aGp'
        b'xlpeIiYbekCMc/RWYI06LQgiGutjyY/R4Z6Fuyn542lmA75pEcQEl5R0ur1TZgWpxKFXUU6ipGKPWyVAGKnAzYH1A6chMnQZlZ6rCIO36vQwLVaHoTgDRF2rvkxfqXGm'
        b'/kVUD3QYkJ3FDF57dNpIdBaTZup41UKnLyFJ2QA1sjNm4SWb3uU1Z+Mw9Bta1hhsVZW6CrslmzJBwiTN40Cu+1FR1zyePPoQdEPhcd+toBtiI+c8RqGn8AFLdi7ekI13'
        b'RlKBF+/I8mD6l4h9UMtEF2nXxy7tLmNdpd0WaYt3i7eWa+nX0o+Xeps8tBF1kjrfun5lIq231meLJ0i+Yp1E66v128Jo/bUBTVyRFMKBNBxEwx4Q7kfDwTQsg3B/Gh5A'
        b'w54QHkjDg2jYC8IhNDyYhr0hPISGh9KwD+lBGacdph2+RVbkS3vZ77EfT+2IJi+tso4TeivWyrUjaW/9+FG1eLWwZWRkHvRpLzWqyVOrom5xEnqiIgDKemhHa8fQsv7a'
        b'SEiT1MnoeYsgmjZWO26LZ1EAxAZCn8ZrQ6FPgdBGP62iyX54wK/Ov0yiDdOGb5FBLUFUUyhXRHXJphPv62kF876N9JI7/bNHy3n6wp/3ccmhkJgJmM3Ew+0RdcImbneP'
        b'ZLx64VAXFD6PiMPNI+ppTFxuukuZ4+ylzPHkQQ5NPCK+EI+Ik8YjghQKjy4vjbYGKJe5WK/t8iwF+mG0klc/Da/iFBtAALRWdMlKbbC0jKWrumTE61SvMQh+Gt5lepD5'
        b'iqtgWVfQtrtEM+bOyaU9NCdBuFQmYJ+X8Et9eCYzj51O8qyT1nnVeZR5Ce5BsnrZZmatZ610jYy6B3lS9yDZOs8FjFZEZ1f8z70wYJdJI/8y+O7pa3UWegrLMdV66uRQ'
        b'qlP1KNIjYgKoIpoqeffUTBDOXwG5IaYh4YCXMEcao7VHDeRfaBpQCaudRilU8lRSHuhJqZy6BMpt1XKgqolyrb5cb7X07JfQDQdU3PeCT3bfA8cGyI/0If7H+uCKDhPk'
        b'2fQv6cKsyGx7qtAxi/u+EB5EqD/wDpW8sAL4ASC/Tm6xlRh02nIYzxPVwnuX8Ior1CTXQBUQ5vsvN5iAN5lV8gyrvMoG6kuJzm0tGmHwJTrrCh3ZAJaHanVlGpvBqqDH'
        b'75J6h4WwDCbIpwlv8lJiQQx17Ds6WR4VvdViX0IT7NhqcQCTnPYzmeWhvBdLJb5vrgVlvLeKBJ+pCVTzIlIKVMPjiEBYQnXlKnl8dFSEPDE6qtdqnNbwBPlMEpDTAKmu'
        b'TG+EVQN9lK/SaaBjYUbdCrIJWpOgilNFhyl6TtWPeBD78OcTCpcEMnLm4CyvarXPu1GrGNskYr55MJXDjTnoYj6uz8BNWZF4O7zlFaRnK3BjRK4SNeDm7Nnp6FI6OoG2'
        b'5ubkZOSwDN6NWn1M4qW02m1pPswg5p0KJl/to1vqx9gIpUEXfPBul3rR02i3vW68E2/PBg6Kttsrt1e8ZZUPk5RG6122lpxxS4oTqdXZuETC2AibTxqa73x+Kl2lDCOH'
        b'U9BlMZOALuO2xVLLSHyUHv+ileBCcqTuYJJYrvYZnDef71zqFLTJ3ZhxPdTaGEH6tkMxT+gWbkIXSdfQHbM3uoYah+r/eDuXs9RCPTOPNQ97+T3PDVE+Wz88e+v63W17'
        b'b28Syeb85V+jPhJ77Ym2FjSfqJatmbIv4ndDRkZktIyxfti/6D+/H3rzncbcIG/b+Xm/Tl3UNt/WvN63YcOmA4z/hfc8Vhb6v1f4zfauDo0sYce4D5uH5Pzm01tjhh/5'
        b'7IfL1i9LJux9wb81THEnVqPwsRK7XD66EIAaI7Pwien2Ix4ixn+sqAy3BVgJa5g9CW2pwG2oMc8ZnCwzGG8W146KoZVopsz2hulU5KCtqMEmONX2R3VimU5O3b0Xo/to'
        b'J1RBoQbvJ+2QY5kBI8XeuVnUrx/tyTOEK0PTlRwjHYoeosOcci2+TN1/5ajOE8o7wSoIYHUwTQSgfDCceuaOQC34brhKgRsiGEaKO/BDdJGLxVvxQzoOOUAINZJTXA74'
        b'SJmgmgStCD1Al2ZZib8z3ocb8A4y1FxePiN9xAemCRBmmCi8VarCOwvpUQa8Y3gcagzAd/OgxjAVzduEm8NJRrlF4ov3pNCWJfjWUDJ2at+ElpXQLjoQi4+J8NYS/JR1'
        b'DG0ZtU6SoDqntgXZcDC6LUaN6C46ygudXj/zkFn3GRXqdEoaZdYza6SslA1gZcKTnCWT0fNkMo6kSNnaQDsvdpxdybV3hDqcktVgJqe/zFPJI5U80hj7wZhpTN9eqzK+'
        b'VHclqY5StBI3R2weke4Tv0tmA3NouLNra8+uOhybWeGXupSS/qxhlvH+82yugu3yLu4WG+yetJzLzHXJJho0VSVazeRAqOfvpE6n9uxp3wqEXKjNzvRDgUFolSajYZUC'
        b'GhNpTaVP2jGvYocg4b5f5nR4BBO5LQNevh3Bt88XctP8k7brX+wqPPTR+EBH44o+BYyf0w3PYjvv7qMDgx0dCEnTWHQOdv+TGqywN2hn8300OMzR4OheRYGfPlZZsSAY'
        b'9NGyvLvlXoWHn96yT7GTLNFH66O7If0j8oabPrgcLaAH3bg6xnHQ7ccOFjzBISdRrr4+5Wn+hGziwb300NK/VpZUlH3FvLHjlR0f+Tzrc1TPTD4hfhf/SsFRrhLii264'
        b'UuZCfI0QZ6DMhnk8Yd4OfKYHWcbX0S47aU5W9nXyzKOYrCDnU0jr4Wd8bYATraIZevHz53px8V8Aj3EwtxbiYQ+UcAPzO5cTZz3qV3h1eQgrkvfil1qsZp3O2iWrNlms'
        b'RB7uEpfqrau6PPg8q7qkNRqqVnqXglRuquLVTZFVU94lMQGum0u9BViQXvnZ4TGTgNbboSb6Os7p+/GXIpT5CSD3rvcBkPsAyL0pyH0oyL3X+QjK4hZQFt+XuFEWU7Va'
        b'C2gDRKTV6krIaoP/pYIDnFxH3fWfQF+k2gxVRTTyClu5zklDgxmx6EHDkfPnGYiyZdFZVfI8wOge9ZBlX0W2XfRV1SYzUSztxUo1RtBWSFHQdMy6UqthlbxkFSnQoxJN'
        b'jUZv0JAmqXBP3CctKjJSPTGgwboSqhQUJFJnjzqgaptFbyynPXJUIw+jwAp7ghmZKYy2ghg3eva9R/5Qq8ZcDm1o7RSIlJcTk6CFKBuW5TYyuyVmTWmlzmpRTHhyHZ7H'
        b'0wnyVBcWIl9EN0GX9FaMtDxBTo8wLPrRgwy91sIviwnyAvpXvkhwq+s1v335TJATgyaAiuqWi5zd6notSxYcaKXwlC/KM1t7z8cvScjKv9A2IuQZBXnK2OiEBPkiYsTs'
        b'tTS/jkHfTC1UZkyXLxJ2BpeEL3I+ptF7493Ln2jQfEBOKnJ2Du61OBAMmMwKWBqwXC2lZn21VeBbBE/JSWu6tlINFhPgr07rVvkHdCK5CZ8x0Ct0KLBV8um8BYAu0VEF'
        b'Vk1VFTnPZhzVqy2ALgZALOhAtbC0tHp6iY8GpnWFHviZbiVAXFhwPesh/3JNVh2/TOji11krTFqgJOU2UP9JXzSVsABh0ehgdkp1chMwdrf18EMii4aaNiz8MPUWpy6p'
        b'5DOBqNkJkttanJcdMYQAqpMrikoNMGD+diKLzn1JtXBBkamU9pzfM5lYYbVWWyZERq5YsYK/iEKl1UVqjQbdSlNVJC9ZRmqqqyP1APyVqgprlWF0pL2KyOioqNiYmOjI'
        b'6dFJUdFxcVFxSbFx0VHxibHJk9XFfZgdCPfreVgwKJfazdElU6AlW5GpVOWSg3nhqD2CwXW5zJgCSQW+m8Rfu3K5EB2LJRx70/RoJhrXLabae/Q4MSMTv8IyU9XZn2XG'
        b'MTZi3sTbjPh+lp2jz8b15HKRTKV55hxyrHVOKDkiOh9UefgDGhjag654EtVQTr1VVtjWl6BruBN0WaLreYB+d4jzQR34no0IDAWJoId2qsh1F+ToLNSMm0qCc0CnHYHO'
        b'iPFddB4fthFVZyE6NgR3gtqcgzrRzbl4V7XrCPNxfS4U3pE1txoeedmZeJ+YwQ1okzc+PRzdttHLS05EoB3eKgWkoXOgVx/3YjwzOXwct1fx1yudXh6GOzMSc6EGlhGh'
        b'AyzaEGWk9yKh7SN13rg+UoW3Q4MRqD1TogHduJ5l5LMkYrxjOb1DxoA3z8Sd6H5mZBjLcOlswjj8kM5rv1op47NAJWLk6uy3585j6JVNuB614WaLL0zWDXQiKYO2KlvM'
        b'zcJPoUs2cgbXiFvxaZLB11eFd+Mb2fjqstJwvEfEDFwlQhdleC8P8LPlQeH4sLcKqgDQZJA5ETH98R2xP36Atuo3/OljxnIYMi74tUz5ao4XigqQfJCo//YPXcfePOax'
        b'/I/976NWdeKcxWeHbI46t2vAxLZIeec3Kz+M7rd537w/BL6/idkX2NB+uPmLOROeNVdmj8pZUKd846sNL7322bkC07VZLQcOdhzqfKRP9S56c/+8uFPxlyqmvfXp/n/9'
        b'/YXarTWmxLPvra19K/evr6V8+vVff63JuNX5a487Gkvl8I7tfzk+8O3fjsgoDF/4QYxCaqVTch+3ZhADixJ1BLoYWMLxDivZUMLN43OznA0OxNqAbuC71OIQHivBzWgD'
        b'OkBrm4d24YvoIctbW1wsLaWeViL5TsankpxEWnQabREMDiDT4j2R1FQSNHd0+qzwXGVGRk5WBG5SsMwAfF8cMxo9RY/dK1GzX1ZEaDq6oIWuAATRBW5VDbrrIoz6/dwb'
        b'b3o9FOul0WqLefGNSsvj7NJyOjkXK2MH0Kfzj5he6CFja/s5pN3uOgQzhS8vNC9k7Nt5ReRB7ukwLyaPJeSxlDyKyUNNHhpXGdz98V5vvs7uSoodTWgcTfg6WlQ72qHy'
        b'eykV6J3l93fHOcvv7kak8Ozy0RJXPkE+6vLlpV57UKqpon/J9SW6Lk9h/7ZU1+VNZBSQDIl3F98HxzBLvQQCTEwrAXYCnEmEeC8XMd4PBHl/QZQPIKJ8WYAgyHtRQd4b'
        b'BHkvKsh7U0Hea523IMhXgCDf7NG3IK9xOOfJ+fuKnkBcnUEONPC55cAzYZ5AEgU5QON87x6RFSLk5WaTrRpSQUTW9ORBpqoSvVFjl0rCQGAJo+yU56ZEq3d4cJIOOpTd'
        b'HjUR5ff/aR7/N2sezstrAgEUH+OwZf2IBuKyHvnyfJS9Ardi2KIf8erstTl+vfPtCEtciOMlWaOJ2GjMVFY1updAV5iIqKiv0hh6kXUX9eHXChqEe8/WXntMKBPf3xKT'
        b'qZL0l8So5DkCdmloWG4qWQaAB73e/U6gkWg+SQlR0YLRiyACqG2kukXdPq+9dsJBGCfI51psGoOBrgxAnBqTvtSxGhc5ucz2qfwJhNUVDPQw3SJnt9ofVc9I8cdUNBfn'
        b'zf8DNKw03QpdueB68/+0rP8DtKzYhKiYpKSo2Ni42PjYhIT4aLdaFvnXu+olcat6yfkd32qpmN5I97p0tSEuW8bYiIrlXYsasjLQdlSXgxsiMhyKlDvtaT164Bm3aClV'
        b'nQLwqfndihPaMEbQnXZPtyVCcvI4vClLlZlDJNdjoLb0WS9qxI2e6JwMNVBtKnA4OmDJy8kTrisiDczHuyB3M64HDWrlWi/QOaA+iLlTsBgdRYfRKU8GXcD7vXN98UV6'
        b'myy6k4ZPWTJxU0ZOXha55ChKzAxKU6JtIrxjdgVVTBYWhKPT+JIlLAfvDCW7gqoMdCmUZUaUSyT4AEevO8SHl5d641v4GtqIds6R4SZlLqhXHBMUK0In8NEFdBfad3UZ'
        b'zISwC42voFPZs8mdQujGHHKRZzRqlKzUgDJEdlfH4eYVlsz5abRfGREKciloMD4lwveSIiiMOjz5+13/Mn91RKk+g6H6MD4bi055F+OtUoYpZArx/VIKuppZ6Iw3mSBo'
        b'dTe+lQ5qZRPei28QVbMRXYBQNt6ZjpsGW0XM4hDZrHLcSa8v9Vu0CndOQQ/gNYPJkKJ2GxEWNevWxaIN5UTPBpX7+FgbwSF0F9elQZ178kT0qlN0p8rwzQ8//FBVy19u'
        b'KB+pj1iyeCq/u/4Pb/7C2teHrjEMSEpjbGTvT4XODCUT0ySo5+kR88hFw5GZcwEJ0vGOglAFoEJ6hv1aYQW6SadNavTFG9G5JWjPIno9zBrUjA8W4H2xmSLGG91k8UUG'
        b'X1TjUzZyfbQeNVZ7C8DBJwLndGOLzM38oMt4j5hBdXM9F47AO+mVekMGDuFVXaLnzg7F+wpkDqW2ZAxVaqf0l/otQBd5hftKqN6SqczLibTghwR1cgW1VoEPStD1+Fob'
        b'vYDoNN5UE05vtDGKMhVS6PdDDnca9fRi3T+vyOWekzIrOzKqfAb77V/8Pe+BwYFW3YI7eSvGHN4/gqDV9si8nNmh/PU4innolMHZT+IYOueDdw30pIYCdHBKZbgqIyKM'
        b'xbunMFLUzEXihuU0aSg+OgrvQteyqC7Imdkk3I52KkQ2/rIs1Iku8yVRR7FQ8gq6QTFhEd5Tg05Fd5dUFFKzBT6D9+M2fpRWtLl7mMpIPbr/UGSZDJrRn3+zZ8muSbl4'
        b'asDW8prf1hxd//2eQah/m2JOtcdgvyguOEt2qLDi/Y5X5LOnvx2c+6vAtqT5YU91Xq6o+fTB//pHTc2+6+dwvKRgb9mEN8dUq5MiJp57c+78IaNnfvfO3hDJutKciduX'
        b'zHjz+9F/njrhxjB96ji5R5ti2Yj4acMuv5fhv+R87qxnC0ccvuD93ddvP4h78cXdvu//Men1ta/PlI6dOyVmy/BLn7eP//idjQkbh4zfO+y3EQWv6Yr+FP/3342Jef/q'
        b'0P7pe0oNt2d9u/3PexLbrx09r5+r1h4bWXntj8va+7WFtCwqv/Hsu9/nLw0q++3vZZGyr1f+6rXEGFOI6euqqgeSX0cW5P+h6rOq1Bt4eO6AOt+GmGe/ssXu+vvXulyV'
        b'14RP1s3cuuIVv/eDnt78w5C5//j1pF2L1707eOl9zYzoB89e+epgxuf7//bClK+vms++957Clzc/3Egj1wBHOu7vxLvRZt7+ULXSSghRWuZcu/UBsLzNYYFwsj5cw3f4'
        b'O9jOokuR3ll4I77a0/xgoZYFcU5BlsNJA1/Xixn/eSIDkMJ7/PVaO9HGoeFh1EkD34ZV6LmQQ2fQrgrq/1GIHhSGqwiFj2DjfQCXdnJKjyVWat27jTsTsguyssOkDLeE'
        b'TYwZSEukTByMLmTnRHAMEAhxFgtdrcO3+ItJ7+GOGOAFgkcGvhXJSNdw49Wogb8M7incqh4cQEwlbp03hjF0+68E1aGzbp0y8E3cJAYmtK2Y1rcWMLrVQpaXMhRGuY1k'
        b'JJaeQLxLhDqAKp2kppUpenyVmFZgftJQh2BayUUdfVyKpQj4L1la3Nlc/Ih1oVv5pnaXQiIUrKc/nI9gdem2vZCL6njLCw1xxF1kOKQGs1LqNEIcSIIgTK4jlnF+1KXE'
        b'iyPh2oEuNo3uVgVLjQ9vLdGSh448ysiDMBczuVzRrHdYUBzWCycjjceT3Frsxdepc1SsddSkd7Tj62ii21xTCY8iF3NNW5izuaa3oZVKBCGLbH273mEuqfOoY+ieKFvn'
        b'RY0s3nVixx3mknrpZmattFa6RkKNKlJqVJGsk7rbECeVj2Ael+D8eAkubpKI+W4SeVNn/z1nBlNIY7UyCfOBIZhhpqp9LpcNYii/RHtQA2qyoCYZ2oH2LhcxIj82aRh+'
        b'ihq2V3uMLUBNhbhpbs5sfCMf35jrOxDXJ0RFMcywgSK0ESjL07xR+jY+NLQANxXGR80EItAQB2KUbDmLW9PMtJXZheg2qQmdXEQqYxkJ8I7DecMoy8BH4uNQJ8gsE1En'
        b'3sRMnIROUUN0oiYQn8JnOHQoCSQiZhC6gbfaiKN+QElRlioKd4TExcRzjHQdi55C53EDlTf98Ml59nvB0bUJEuFe8EjUqi+9kCWy/AnyNI/YPSPvQa4o2ufmx1lfn5va'
        b'uOX8qLklf0w9uCDk4DsXBwwLmpsSnfSWcviqLdqPA1cy48bNHO7xWW3/a98l/+HAazUnD8qniS+9Hbt0M/rA71bXPwa98fqMF1RvfpnWGrptxsb0j65//Uji9z+bssPr'
        b'X9znu0bxVsvv8+Kzb8wLSvf99w5RzFD83SXduedSO15+7/ZYnz/G9etaG6ovnWR7FP29/nfHbtd8OiH2n40v/eVI48flzxXfS57yp2+aX8m5eDPgwTfWE6nn2dhRwb/I'
        b'OZz358WfzF676MLDzecuDJq5IvzDz9e98J9vA2/nWK4eP5319cr974uuv7b+s4Gzb/o/rQii9xhGp4G4QK7h9wDR4Qh+iE6yc/GWQiuZ6GVShpBUgxcQVUpRjfgeJaiT'
        b'0PUUgZ6im7iDEEpCUIejI5RSohPoEAjVbulpzUigqBnAA4g4i4+L8WWeJXkrnA3iqH0c5VloyzrckpUbkZETjvbi5kh0Xsz4oadFIMuiFkpF8Ta0rxY3gogoBZFHwoiH'
        b's+gkOjGOr38Lfnpk94XVuHEhf2M1vo3beJ54JRhvpzfCo0N4M38rPH8lfAreyefYoC7NylYk4uPOHo8D0CXxkBG8VyQ6oMM3s4g74wrckt3tzRi0TIQu5i7mXUceSKoJ'
        b'az22xNW2381ZxVZa2apg6HOj4JgIms9p3jnRf7hoKdoFnabsrDUX36OsdYRN8IAknDXLfm/lEXQnHhgLVNSQ3m20zzLRwun4upK/w74/3mq/xv4q2oSO0cJyf9RMLsxE'
        b'm8c4XdiM9i/nL+G9F19IJDh0bzXemUduPUW7OFOs15NR3P9fF+PbXWj4a/Apc9J2M6dIwnqolyL1VRQTxsRx8JdnVD5Al/kfMWVX/GYBCfGejTJHuv1Hyok5P24A5wXM'
        b'zNmBhm+eZ1Ie3eyhy4M3Plu6JBarxmztEkG+n8qRJGYTea9yMB6jg/tQxmOAxyVWuAeTMp4NzK/lvXj68B39L7hcCYc1vv1jD6sBf4zKaj+nIVhfDYJRxKyz2sxGmlYl'
        b'1xDjvpON5YkM4/JK3SoL1FNt1lmICyNvvBGsURaHRV6w5LgzaD9urDfwJjDSnZJVVp0bY5ODj0qdJ8zJ952qe2j3AnQMBL79qBltR1fxHnRtProGy+jCbFQvIYrbU4PQ'
        b'BtHq5KWUkRXixuF4L8BQxaAN+JhKg3ZTNVACpPfiXHSNcNnlqHG+Eu/PUqlETDDaLkLtqD2Esuc9npzMg+WZ9lTFUoZy4NiBuA2KjUUX+ZLSUXhfCXqAT+OTMUxYvCQJ'
        b'tSfw2twRfAGf47UyqpItmhM5djQ1JoDqdR23AfvFh9CVQif+i0+m28g9CGV4WyCvsKHrvLZ3DPRdquvtwgfxVWDs+A5qJOU41MQORWdm6s1v/Iq1AFFjvpo4P+dl4aMi'
        b'ibH3pg5rOH3gA/G+zw83HP5onO/bH4aVfRf2asfqggTtjPezln7/Z98XJo/p2tX+wcbP1mrGf7bl5cxfzpyxuDDbWJ3R8vyLtzue1T7z2YTS4mXDiib9ZsLK660n6vb+'
        b'4lTp7LxJ5rctJ+5G/vB+/6IjD+auvvTagcOTX41S/E/250unjN4xftybWCGllHXBYMJq8iJXPuZ8TfZCD+I9lBmiuhUG/sJf/rpffAXvH71KYyWTsRy3oEvhqhyOWY2e'
        b'5lAbm4W2DaM0cx4+rwYmRhQd8eQMJcd464gW3pFKtQHcHDYfbQruzZtbBiyVcroL6JZZ+DYJOohvdXOiRNSskP4I6ejF4VBjKSaLrvtrITy1NIhFwVQ4D4a/hPaRTdUg'
        b'oHZOBEQomvsTfRGXw+OTx2jUU714IwpNKNgucbXGWuH+KvQERrh5mmw3ku8hSB3XoYt7vQ5dRKVi8Yci1s1WYzfZIhTEoqkhbwaDMwF78iNmpOMT5Bll8jDyFiYHqmvh'
        b'jdqENOlWklOtxMYbpqrVV4dF0IYEGml2byK2kKv7tA7DtMZcWqGv0ankecSOvkJv0TnoIK2DDoBm18jLTAag+X0QNQIixxE+B1GT5dIb3tVAtm6Gp8PKyE8HoSMzJxu1'
        b'F6bjznx0CddHqEAWSMfbPKoVnjT3+KyILFhGmTkqvB3EskJQ1RsjZ3NVIHGA1tsuZrLwTQ+0PyKSSt/eoBE04r3oAlH2t6cCPzKwIHO04DpqoFyCL4FAd6cyHMC+klmZ'
        b'hDfQaNGYReF5HBFotrFzGHy4VqL32b1CZOmENN3u4klNKX5ctM/0F3IHLFh38h1RtdRv6vMSxjN0Q5jk5NSPCgy70+urfvfG7JTEsQvH3P3ry980HYxteW7m3bn+NW+/'
        b'3jhm9dl/lpW8/X1h5p0cb+Uo7rll49PuvXr6H4rt89768GJr9MYv2uv+NWpAUuFqv6E7xisnre53qHqScffX68QfXtPfkq768PuMRfii7J/f5R38jwxVWcb8xqKdH/fd'
        b'U+IvL+3sF7/W8GHHc14pi+O/jP/lWwMvqJMPzPmPwp//DkqjBF2h82xBTwO2J7LosgUf5L9AtBPvZ/HJEiJrCp8wk+FGbq0Zn+IF2otiT7xpIO7E11cIJhdPdI5Dp/BB'
        b'GaVF/fEZdJGW3o7bB4PcLs3lhuJDIDmS6uekVKDTU8j32iJUGfAAUoU7OHx/CN5G033R4XWoBbVnRaCdefxHALyncvggOrmCP5XTOAmk0EZiTEzzJEdz1nFhvmOoQWgG'
        b'foDrUCu6SRiGQoWbI4ho6x8lKkd70UO+9I7qCp664h0ewn3qEUupVMoC5R1eER5JthCUKgUHlO+4CG1F18Io7c1PmUEF7EgZOpIrYaQTuYFDcvgJ21UJsvT2MVkOJPUM'
        b'5kD/OANtUka1ezg54tUE84Ha8B4yIWncIHxpGpVnpXirn/2DToX+giwchi/TRtXTa2iHcvAtAIMUtXERIZK+jDM/QqSdCLOYLFpXxxby48mbV2T03A1QZJBReXNJEMTW'
        b'+joIJymd6/JBALMrde6jkxyft5tiW+Hxw2MUe/MAlw8EuDRsP9g8HR655hnklfjRARUR/ikk/B8Ofvs9doqe+MBrTaXFxfT4Tpes2myq1pmtq57k6BBxc6e+MtQCQ6Vh'
        b'ym7oCPjZCP6vm8f6hKOZfKfjY0ZwkpGJxRyxiDFs8BhOUCp+9Mn5iXwA2Aw7QOXDBnND8wcn+g3hRaxT+M5Ii5+FfPXQ4ucnYnyHcfgEejqPbj6JVkd5ozYroRHoJG7z'
        b'Jvsf+WTfY2iMeLQk+L/0TaEtjx+16Lk36JFLbTJ5aCvuKEDH8EMIjGRG4lOogd/EuImagCioUEcO3hUVD1Xgm+zyYHSfF0EP4/0ZglkG3cFP5drtMuhmBG9AemBEnbgx'
        b'g2jDO2LFjHaWDDVymSBGH9TLN/+DsRAEVL1e+KV68TMdu07sjd66nC31+Jg7uzX1DR/vkJTUiE+DzwZ/ujVbnZDl5b2g5cSLZzdHbz2x+cS+jD3smH4vP3NIyiybElg0'
        b'6qxCwtsTWteBiKZSJKFz/OlBenKwfghPTbbEpxF6occbur8BdxXtW0gJe1zaBGKyNhBDQgTL26x98Ub+gyRb8EO0mdBGXnHG7eg6VZ4DbJQ2hgPNOpVFoEhSl8XKlnC6'
        b'oZl9nSbxAbUIZBBdMXEooLRkgDMtGUMMroR2iOFpXuFYIuIuMSnQJeUPc7n7mNEqErXSgeSk7EjOXv8G4edDZ6GO7nWienyeCw/NVKajI0sjMlFTJL8fKsf7JcHoYoQL'
        b'IvUX/lr+5nylRTi51gGwk9OKtngWiXRi+kk3hnzMrYkrkkBYRsOeNCyFsBcNe9OwB4R9aNiXhmUQ9qNhfxr2hHAADQfSsBe05gGtBWn7kc/BaSNgZbDa/toB0LaPkDZQ'
        b'O4hcYaFV0rTB2iGQ5qdVQaqUnmARa4dqh0EcuXiCrRNDiRFaObluosWrhWsRlYlaxC0S8qMNKeMgjvwVOf7ysfxTzOdweooff9eOPOoPdXl11/N4Ge2onnE/76kdfbSf'
        b'dsxRrihQF6QL1I4NYVr7nWA2szQ0zh6iOYKpYyB/tkcGc+IhXLLRn7oMetB5kmgV2jCIG6ANoXQlqsuzGNiKZibIsfR8tYt13FX65x0PpfRjfVKHTVzy5DZx8q/nITEv'
        b'3ib+boiwFS2rNpyfWcJvRf+qvIkZxDKhf1FU5v4wYwIf+YuEtew3HLPgmeGmlDljZYwtmizsOnyz3OUQuaDmoVtog3BCrBk3ejAF5bIAdBA18SZ3ZjRDGCgTVlrycspU'
        b'5jN7N+mZOv3kj0SchX5A7Phfh+246rshykf8h9w0tfhm68vDfaaWKmbcfUY8Pb2s0nD43vpH/8wc7F/xetzE3WN9ak8ELEtKjL31TmPy9dd/9XyQR84r75/usOUPSK9d'
        b'+c8Bzx9alxsT0vnJF1c61S/MmdL2VMjCq0jhSYmXJUxKDLa38V3CcESMrJCzovv9aJoIX8pEjegK3V3D+2ZJx3OB6egSlUjR5mpTDxdkkVosQ5cX8sbguyvQnR6H5uiU'
        b'jC1bEiKpKMNXqbsyPobvDuaPZYeHKvlskGngUFCCxRNnrqaZ0lZa+U/BoSZqVb60mJDhQHyE+FM04lZ6xByfXoqPd2fLwS156CIDufaJQFK+gbfwouMd3BEOenshehok'
        b'ywzyRWIZbuDQFvNSK7l1BV3GZ2BOVkAtlM9CXag5D4TF7Xl4JzrpoZIyyVlStF+L9/Ok9Ynlv+6j18OdSXaMlPWSyNhB9Ai2YM5ka4Mc6+SxLxTy5scuCfUY6hITh9Mu'
        b'n+7tJqOpy1NvrLZZ6SVY7jV3iXkdeV9DHusZu1i41qWfkT1I/1su0qGb/j3pCVtJMel0H6dMUzlhRTi34jhgPbT7Gs8eZ01VUGsWIStP2BXfYueZ66NL0+1d+na4U/M9'
        b'T1ernvxYtwNKfTQ7y9HssAx7druf409q1XG4maBNcZW+ryPGmY5GBxAVQF5mNlX9rDHaW9Os7KO1HEdrwbQ14gH7U9rawrclLbaarBpDHw3lOxoKKSRZ7X6yblv7L59V'
        b'5pie3+Tj2RD9unr6cn9GnX3JMJrnOBcKiEdU2wgfudrnSGAKo79d/Z7YQswv8+80f6l+uSRd06IN/TRL41P2ufpz5m9HQgoOPhey6WF2SNJbrPqm5IvaaQqWErMRIFLv'
        b'RZfJrRLuCZqdmnEj+hA6qQ5GCRf9mpidcM0jUmZtoDMh+LnnmAt6UJsrLtbDno08+gH+/Zf0nYof13cEcFUNFJMjEqHnvTYYBo2fPYNOiG28XylFTv/D7LU1+kVjbZyF'
        b'3AP3h6l/JcD6XL1Lu+CZgyAEXN/VLnr5lib9u1P0+4YezLIH0k0TVArOSi75wg/xBWufcAL1ZxvACneibfxXUOvmZ2omEcNMmFJFNI9NXKw0sC/twb+Yevfqa3XFJQZT'
        b'aWX31+fsQF1cG+I01665XT6KKqFuqe4UiZ2Mi6WhCR4LesD3vAt8e2/TsSLtIKZSi/CRVBEAWfRzv5PpbpuHAlmj/xf7FYhC/16sHrFgUihDvR9TFWgruiDGTXJgS0xt'
        b'1QxqqpyzfjW6wKFtUxhmNbMaH8WtNgJ53IoPAuCcxUPy2c3QXCXLxKHt+E601A8dwjeoU+TROCqJpv8tW20YOq2AoW5+lwvziJtflGa1pt97g1aNb2Oof+ygsjj7nUMu'
        b'rn4NYnSXx5N5Tg5+IBsd8sKH8wdQskf1crNiiZNaDUo1ujCdy8TtS/QNy1dKLDsgy7OLnh/7ijIIRQWLP1gbOSW/rrTWUxudbtwwNWDBh0+NOp8xY0aUctTmT8Qv5WS0'
        b'vXfofVPN9+MW//Wb+wGBfqdygq/u2fXWh8G7Ry4O9Qk8efRvePrJ+UWhsz8a3/joy5p+s+I+/uw3haZhqw+1fPV95at3N7yenXAt8rouWrr2P6/Mu5tWHro4qitFnGj9'
        b'84hfvjAmpPUZhQe/G38+HO0CLRofx62PWRk3LaQ59HgPanMWSFctFtzSVuNT9GYfdEszx83qQm16F0K4toT/SPG5dVO9w8iW/TXEOwjY5dwRqFOMr0xDT1sjSM/uw8Sf'
        b'pz4PRHAFWKOLoAPbl60UnRjFRKHz0qF40zoqVFfahgveX3SDHnWM51ZVQBepneH6Mvyg21ggQ7vS0zhTLr7d/e3ZXm2L0uIVZr3wTVEX8bKYUGmOHQ7i5WDBhcuHrQ1w'
        b'WnC0oOsHjzXmcksvpJsz73Jd383wWNxjfZ91+eRkj+ZyS8XCUnTZcRW+gEtPnDm+gCumWz4SWNliurIldGWL10l647aSHitbmsv7JV81jfTFNxC5gXAEOY2LWqkWSrdM'
        b'5bPx9fDZynlK0ADuLxMzHoHc8Jwk/ZshDyQWovIFFC/buYEYnHahd5793bMdu+7svbP5zoKIrYqDI7fe2dy+ObkpY8fIgxs7JczFCbJVgzqABxO1ZBY+sxT0jQx0KR6d'
        b'CkWAFvT7tCwzpEKM6tHFKfap79t4LC2m5w8ogAOcAWzwo+4NLnNMs9rVk25vNvq9Ymrn6UG2xXz8Y3kpgHeT9dUDwIeCegMwbdw9fInJuE4CEJZSEwGBsscTQrn8x1V7'
        b'SS4PTbKWoi34TgEB5n6WfDl4swjfY3PQdnRfb3jt34yFGJkPSad8qc7SvPhp6EcZvCil/lKtLwvb/6X6kbqy7Cvtl2quISoh1nbtTFTMTltHTceZ6O3R/HeurXN8vkn9'
        b'oFvMfCJXD5fPUxNznBNIg51BapbxvizEZbK/08x2l3ky2Lo/ttoHqPfAw9QD1HsHOYPafYceaaGAe6DH8YtaIixryc8FeM9l7QxwXDcaXQGI432x6ejgcBEj8SB7jRsX'
        b'6BsurxZZyMkHA/fJl+oMB8DTNV+oVZrP1V+pLTX6sq/UAZqKsuzSoFL+29PnfvD4ZmQIrGF6lOIyalzMux77m5awiQszn/xDtl1+xcLdnU7gdhGkawm4awc5zatLAfew'
        b'7pKWaUqtJnMvZFps3tcbkFvgsaIHkBuDnYHca2cU/rzbbLcXLQF8l2+3Hl2pW9XlW2OylVbozLRItGswpsu7lFyYoiMfJI12DsR0ybR6C3/TCXHGJd9gt5ILbnU2q2Yl'
        b'vZSV7BB1+ehWllZoyJWhEKWQ0Y0oczJ5TCAPN1fpki2phbRG4kQU3eVlv9FEr3U6CF5Ec1j1VoOuS0a+Z0Eyd3mTN/sBaxpNr0qiNcWYj5IyHuTMX4lpJT0F3iWprjAZ'
        b'dV2iMs3KLomuSqM3dIn1UK5LVKIvVXBdHqnTpuXNzS3sEk/LmzPDfJE0fYlxMloQABKoEnOVhQxJuGxXSv2F2TpZmeznCL0ioUrXNVTKC70JFWuHnOT+IgGRM+VKXiLv'
        b'DbwA38K3LfimPyAONxy14bNsGL6JjtMFNykfP22x1kAqvuEtimQZD3yY88NNM20EFAEBeH848Rm8FJqeo8rImY3rc9GlCNwcmTk7PSIzEqRXdB6fBQnLfnQH713kMy2M'
        b'l7Zn6HPx3qHoLPmefC2Tkz2Rv8tihyg9Ng534rooMcOOZ0C1PY6u8k7D7SCFnY8FrI5lFLgpdgFuoL5MifgW2ghldqMtURzDhjKoZWoG9U3wCRY57lzA+8iWdxGHL+Mj'
        b'eCfd2VqLzuhi41B7RJSUYRUM2peCNvJ0pqMYnaSepznxq/uRr4dfZfFe3DqGTuPx5PAyDdcG41enrUwczNDOpeITUVDXOSaKZdgwBu0fLee3Tk6h+uQslVJFDrTlKHHD'
        b'DNSYzTID0WnxVLwB7+NvMF080vgNu4FhqtVDN0WuYGjvwtfiThjVrYVRIoaNYNDBSdA7MioTusWFkzs9MngZ0h81iTKSSvCFkbSya6UDzQcBORi5evG/omfwgg+6gu/n'
        b'ktrQiSgPhlUy6JAN76ODHYb3oU0gjtKP8ojx+ZoIFuTdE/gcrW1l0uSVH4m+YZgodVDFOo7vWgi6Z4mNm4Zuow7Qs1QMOjy7gLpp4xbVFOLplDMTXwY9yDOaQweL0V5a'
        b'0xu1mcMXcqEsTJuX2b+Qx76p0CMYJbqLLqMOAHgkcQlpQvW0095j03h/rozUArJNv40bvR510MrypeKKq2wAdWw/oF7Dw2Ao2jQ5Ni4AH05g6IztmzeBXliSHIhaszKJ'
        b'5y3emUW9r/zQFlHK1Mn4Bn5Aq9s6Nznoe/YDhlGrg/ZHAAAIXiWhq2WxcdPRvQSODvIArsf3bPRO0JYU3MnXmGvHr4XoLssMRi1i1IB3oZv8rB+LCIfBnce7E6R0bAfx'
        b'SVRHdz/njq8RKuCB6FctsqBbSbgO3aQ92psQNHkAR2xa6jWJiUP5AVrM6G5sTJ6a4CuMbz86XsRvpbbg9kUCvsIgr3CAsddY3IL3+FF4ocNzcUts/KyxoFOzMVBwFO7g'
        b'4XUbH0C7w7OIz5zBn2Wkei4Enx7NY7T//NhEtBs/RQolQd9TjbSx4XgT3i3gXwPg1VmYbZ+JooBqvI2ua/kYKOc9gizFCdDyACNF2kXBRLujM6VA59EGqZjxCRD1BwpA'
        b'h3tdLbOuF8kJAAzs2BQezdCZ2crYxEp0G2g8qesQPrWaVobv4zZ0DPpAzvJloavRgB2l3BDcqKI9VxXgW7GJ+RFxgFAp0AW8laUARU/j0/hIVlYBaHRAkTkTOzVlCk3B'
        b'zSsjYxND0Z446PVE4ll5A+BEScHOgXJQ13IAVDvQFpDopf04T4BiC+124pJaaxv3OcHphBfnRPNrDe9Hu1Eb6oyalQVqP5vGoOOF+DBF9yTc4QuqQSbZ2RBVgwL5NIuO'
        b'2PAuWhmXOXNirmgQCws3bGJ6CY+Ey1GdP1S1Hm2IAzIwjUGt6GE4P5p7qcQ5vQFtT80GmWUpGzla6FXF6kGjdrJqMpmLH02K5Xu1Dt9DG7JANZYwYjG+JWaBrh7P4w+R'
        b'HhidKjix4nvzVejUCOoKG4g34gv04NWcdNB0lfN4RzBcnxMROxBoD6g9QR5DQJO6S/FioR7ttR/nTMCt4WTP5SCH9uEr2d3XLHOBoqFplPGpfWZn9OPhrMR3EvFekCcj'
        b'GKCSByIAcTfT47OFoXi7nYAD9C/Yd5iAy4iZsei8xIa34DaKyZWD8AHcODs+CiZ1A2h24iB2Cd5oo0MfFjU1qxD40G3cBBiBDwF998fN1E93Bj6O7thPI18MchxGZpmx'
        b'eRJ9Faxj0sEEdDQDH/EmGMTUqgCN6tA5etHRCNRBWGBjZA7emY7uoBvKTF7zixYz4wolMaN5jvGL8YPT94sqCMdY89e84fyo8wCHD+EjIEKjh8z0ZeghPuJPqQuMCzXb'
        b'K8VXJzrq5JhxcyWx+C4sNIqaD9AmfDBrNtoIxBYoAjn3+gCWfxtFD9XMRQXAkZuAq6NT8tXsUCBDrfbzPyfwg6y5aNcwfkLOMPg6fiimExI+Ae0jzgrdB77xw3iYjhGo'
        b'UQxiwYGF/Hq5gq+CqHAERE90n5kIRPy+IpF6r8wDQn6ALHRVRi7MY4YyBh9cKGaGoMNiQxLq4MnifuKbe0REfEAASbajB7gN36akWjQ4yKUwuprHQeEj4ip0YC1PFDoA'
        b'KffiRnjVM+imVY8vzeLPdd+DURwnnosOGPr3EwH+nVmGL4+m3c5BTfisYBlAm1HjCHQA7aJzPsIXXwvn78kCDKPuDfgiusoCT7khBpRqxQeEtY3PjMRHJKQ5Bl3Fx9A9'
        b'dG0gXUUB6LQPbgTppJK4gm+sTO1H/WASU/ChLCXQ0UvKDHQxNJMswH5TRbgF3RxPBxSaAbLGER+GeGIvgWm9Lkc3aEl0O2lWltNd2P7zROgpdMMA8L5Dh+OPTiy0+Krw'
        b'Jl+gWrAe8aUZ6AhFuHMrvWb6iEIJwmWvkeTzZ8VRS8Ro3AiDNzELSk2wbjdQiOObkagDZLh0gm07svKUmRFrUCf0Uj5EjDvw5gRqrPQPGsO+DmXlK/6y+v2kD0KlPHlC'
        b'V9AOYCEXxESGw3fQgdo0fF+fPOQzzvJvEHWrjv9jyZvvGt/KD5B+kPzCzreu53y0Laik5pdP/zm4Kyi0Ze25rxbdHuSpSJ0b/Mc374yUHwvX/lU8+coz+C+yiR4Px5/b'
        b'//yMlpc/S/74paPRqQcW/PMfrb+4O+Ja4skTMWcKFw0O72d9cHDUsjfSn1/2+vBvv7IolM//8vy4p9YXRF/9+tF033VH5L5/UVie0V34429b3jj73D7Zodyzga9Nf67z'
        b'N3tvNyTmLH8l7HKK54xP5b7jF03/dOSiY3EzbqYW5Y7a/addw3JrGr7a9FXNtVla04m/Td4teXHdeI/pfmkJKRPHmG+//mHg7lNbJ7zwvGz6zmm5SckK8/n8z66/eGjT'
        b'0f7JHsl//mTTizNeHDu+cdSBkfMvln/Wf+yyj5v/GvX8mfrsVUdzvr8y8uNfndZk/+6bE6Mzw+8bfr3gh9Mvz6/42/WUpiHHHq3aPvz16v3zrw3ZUhh4a3HO9Elp9ztC'
        b'VpzvGKxVvNb2zzXPVa6a+Yq69JtlNa+d+uopkfHc2DW/LX3lt6e75i/Nta7ffOWFwUd2/efc3AsfeP5h16vzOztztP9av/yIqeFSjo8t7emx5cZSvxXamJF/6H8nMfDp'
        b'KY/GHvvY492yv01r/0tb/odXP5ny0p8nfHJu1Gvm9r9bdttS3v3NruL072L+cH9X8X9u+drWKf82bsrf53204rvfL/v+A/PkhrWo3a/2P9+NnX5zzue/Omcc/ZvG0+1v'
        b'qYvO/fJ/1ocp/9P4fp2iH7WMTRmXbvcQqCp5zEcgRFKh1NLjaOjijKXhkCdHSc4bHGZzYvE1ai4NBqn+PghJoFZIiXCKD09n0QO0OY86/ovno42o0b/ax4yvoyb/Gl/P'
        b'cVOkTDA6LjIBd2uk3qt4G97h7Y3ak+ZFpNvtu4H4rghdwu2ogffgOh9JfV8bBM8vWGUPifcXhy5TF9bK2dNRYyRxGAX54Th13D3FocbB6AjtY+1IfJpah7PJWTi0HYQE'
        b'WQ6nnbDMSrWWxvxhWXnA0urJ2GrY1Oj5tFT+RHxAOAYN6/+Y4FSGHsyl2z7eaBtqFw49i9FhGzmiV9uPd2NrHoavCD4b+LQHxxCfjUnoGrWRWxYNdrKQo3az/eQ2UNgH'
        b'vNV7M+5A96G/ofhUt7OFw9MCXUAP6NyG4QfkLv4kP7urRbefBZDOButYyJO1qJx4dZBtCtBssolnsWD3DMdnRyRL0M0QdJc6d2hCQWaiBtJu66gJ3xMMpNOm03kWBRYL'
        b'xyQcRyRw5yITusFQMI1GR0ZCHcSjoz8Rx+xOHcG4w92V8z/Z57NLpNHylhviduqw3KxnVMRJV8wGUZc7L+q8G2T/4YLYHj8QN9gjgB1Dzkazg6AE+fVhZdxgVs760RIB'
        b'rB/NGUBzB7DBpHau1rfbJAN9cfEDJqa2n3rsjONLddvxL8PjPDELEURymIU2MO8MdvEKdumF+/1yavDjv7HE1EkcBj+WGit63zWveHyHTs48bqwYzxsrFi4X1baLqKQY'
        b'cXNuMcNbASmxaFXB6iDy6nBYDB7DgZWe5A0ElxlftBdeQphs3BkCfPKujTgZ4zPe82Oh/hhGPz9mKkern71OVpJNWlers2+GBjB0m25OpWeuv6CFrCgI5EXW/Iy15WKG'
        b't5qkBmXxfcB30QFjLCgYoGUOxoeZUnzcxm8/7Kguj42TkrOjQAvaGF3cWlpL+CiPpVXcIKKVZ8fNsPFVz44LiJvPTiV6f8S/ZF58J9YnBxgRw0d+FcDxOb+a4+v1Egea'
        b'WL7a55C/hM95a7Dv0D8zNDJbtmA8nzNpoPdilqWs37DNNo/P+e9k7+m/4uUBn6SMdD7SL0la0ymiXTIsy5nIm1iBnW+VUsFxLrq0FN0RM5IaFt0dHkbFn2q8cXRsFLHM'
        b'4GP49hgiSt7HvMJavmYUSFX1BF4lI8wK+/U0pSAh8NLBOu9avG0Rnb0MtA9UrCNexIeYKZKjm8vRbl68ah6xFB8hs3cLNC+QN28RbZqXXjqXjcN7AWWUMOXlytHoAu9H'
        b'oZYM/lDEGwJmzikSBtExenRqFt6L95Ef0MHwNgaBrs/yaLIFpLhdiNQ1jFmBDw5LqqGlDPig1LFxGqyhW6dcZi7i5emASHy4QEnkMBbdwWfwbjZoVi1VeIvSpvOnW6Da'
        b'0yuBpPOIcMqcjy7AyypgQQNW4a0gl5NxTMNbhqALHNlMXoFbVgO3ozu3FCKTSyRrlvODiWiZ5MmbkAPf6OBdD6ZdY3/ZrJ+ZLecscdD3S9X7q3ankJtTtpXXfDzm1bcy'
        b'hnr0+301M9132EfcHRQ5Mrnpj4PPb/gkZtY7fwr0aJ2eLPlIXD8tamnKs2lxKX9ff+/vXS8l/zZcGjl3wFRl6G89Q97In5l6is2rzx38i2lvxRS1lvcfeOVwRaStxnvK'
        b'g2nj53891/v9fTFVVmXKn7IK805+ey/0mHWL7xbf8N+Emi8tqJBbC08tmTV24C/Wn3+68bexa7Mjzg1pG/ZDgCn/r68N/iHt4LpG1b2ho6qXZE4auaW9oOCcNei7ZdPf'
        b'86l8VRW9yFL7/7X3JXBRHdnetxf2ZlNcwKituLA0gigoGI0iIAgCijsqNHQDLau9CBIVFRRUwB1RccMVNO4aBYwzVclMnEy2eU5e7CQaTWbGeZrMGCcm48wkr07V7aa7'
        b'6W4xk/e+7/f7Plqr+95bt7Zbt+qcqvM///VrF04sr11cGe17833vp5vv/JDX9AX34b8+veD7xQcX5sjSm1w+Vv95QXbbnBW9+95PeK/1g4SnMTGZpbLLmctmhZ0a2tYy'
        b'tfmjJ5//1qf3218d+cT/++OX/pQxYMeee6ho2q2IiR+s++eJwf81q6paIQ7srwXNFp9cJbBjhZE3im4Tk4nuPJ2qV0twK93oTwkJqiiAaeeyEDUWYDb9D8QnKnwWmogP'
        b'IDrgrXgXvTrSj3oWActLIsq08daXFxAzjCzDR1B7b4hBJliqg9bjegCYTxERPWrXUjrvDcNvkGinpqO2wRQ/vlEA6Jyh4AGBzsJoA25fYMMMcyRqJlIW0SwZCLI1mmg8'
        b'r/eCAgWLOBE+I0CHuEoqcUwqTgArE3VRl51JONpKhQpHXAdyFqMGysSbUmCyF3B954sHKAKYkFXjKynzNlD/0DJALYaL0Gl0lKU/YCkZtInUMl5BhRoQWvA6HW2FsZFE'
        b'JHktxMz60yiQaNBJao1aiarjDSDKNqIAGkGUQXg9FVhwW9L0ULTPxDi0S2JJRtuZkcHBaBVR3puJGJEgGzUKVqpJMXGrCO8IW0kxnbloJxiY8qaq6LSHibWq+GXyHNqo'
        b'qII3aFEtGQdO0qgNSQ6cWChAB/ARNX3qspkywx4/voDqeTQ93shRKyAyxl4Ffz0GgwJUQ4RRC6MCZlEwH1Wz7FrCqYMfiqKKSTdIoHi7mjkXXrd0joUg5o33GGUxEMRI'
        b'b9lA23EkaojmpSjqParZIEahjeXMycBpfBg18O570lAL777HbbFhG7lHG2JisLijwlSWuTCllgjEQgNq34eKUj7k05d8+pMPHHtQBL8PjdGL/w8fgysaidBVIBXC3qlE'
        b'6ExxVRUeXSILZGzDPM0OeMrUWu0sCb62IiXtNNs+s8iSpCBiCdXRrxT6Tw3iSGA/S8ZRsL5VL4eAWuRSU12w0tU7G2w3Db9gf4laPTKQFBhaUWsMumNP93LpXp9ekpk2'
        b'ZdaUGZmzF6TFpetFGqVWLwaQvd6Nv5AeNzudyn+0eqyB/n23DWqgN5NBW0EdnEVe3j1CRjl4iD3cPRx9nL2cDA4aHOnjdTT7uIrYY2dHQourho+Xg4fAR9Q/VseYzq75'
        b'mA7tDlwqqvGaLVoowWfMdpoNtCbUC5kZ86p4pydlJvU0fCuExl+ieifFMCL1AvTBM1escFI4G3lYXRSuFLAi4XlY3emxBz0GHlZPeuxFj50pT6sr5WmV8DysvemxDz12'
        b'pTytrpSnVcLzsPajx/3psWSnOJeDUil8m4U7HQGSstRd4efLHfIA8AZ/PMBw3I/83y1sECiG84BrJ+qSyK3Gs8Yr14WyuVKOVXLNhTKmiinYxXmhF7SGYki9oIZJ+5Ia'
        b'dyLrD1X4UzZVb8VLVKYfwbOpJqXEPWs0wyjPNtB8kkuMSlUaAJwZQIIkL1ZAH1dZsjGaHQTNBqg0z3pEfpVka0oKgaQZEN7g+ZbxSoLnXWWpljl/pnBvC4fEpqStFvSr'
        b'gU56F57KC3hw+J90X9iZuegERhxF7nK9qKCYnCtSKlS6InLOuZTUp6xErVB30bt241U1dwdl8LTtQvQmV367183oDqoHzKr3HveYWRWa/Cczqz6fWLUbiapVzPtPJFY1'
        b'eQjGcoCvbjulIJdtlaFYKi8szZeHWCtKlDQnn2SZQz1i2+d5tU/zaoXS9QVa5Lk0r6T/MefBsfFzpYXybOAZJz9N/TEHjrLwdMxYy6yWwrzotG0Dwk2awkrh+YKQd+A5'
        b'JLO2CGWtO0WwRTLbQ0JZq4l2kcz+G4SyhvecNTs7kqoU/AMb87wHZhgceI/R/JFUrcxTaUgLk6GKjGi0O8mkOv6x6YrBc/ML87Z6siUTpwLgbeXK27RZsj3LKnne1mPA'
        b'VILal9ojbyUyoxm76vrJEi8izW5hmn14Hy6A4wLWT816aXG8jKN+VWfhbbH2U4Td6Dk00SWL+GQPlkrw0dipNNVOoTtHZKHxm9KzZGErNIxwNQN34jaryZooFqyk6Do+'
        b'z5tAX0W1buiwNISmGzKVuprlwodnSR5oBnI6sDedEAp7l3yyk+JNE04MTjc1p16Dt7igXVEJNK2PZMAsy6XdVWbJvgkqZ2XEG/KJxmWVFbZLhWNlxNdfNRbxihvRJ9cv'
        b'pOkeU7hxPkRcqu+TJfvlvEWsRVEd6phkLd0Ag6rCV7wVtfGptqNTbrhWgrerRhw/zFHL7kUhL4X8tsNdOEUSN/PVH5YEVMU8kLtJz29dftOrT5h4lMjvkM/S+/URh3Vf'
        b'XwxprIsui7y2tc+Ogbu/Cfks1fOjD/5+M1J29d5HzhPw9k8+rrm25U7sWN/6lsA7b5Y983q5I698/Y3P352IN1W2PUn/ttdu19+E/uatdyJfiVi9puz0t9yPv9yCX5e3'
        b'XNq+6EeHjePlt4cEulLlsLcTum7QHnGLwER7xNfxcaqXLXoFH+PXrQeiFlOPo2j9crqPgHbDot/m1Nlisw7mwA3GTWJ8djYjYUVvoIvMPR10F5mbmSYaPoLpNyfL8WbG'
        b'IIuuLOFh4Ogs73QOncBVCfgsajPTkSeLmBpWk7uAqEfbzZU+Epd5TsVHIvsbNHnUtNpMmXecRiu6BN/oxZRP9Abeb6aAps+myuFw1CQhffsSE2JD8EV8RUPXJ8hRMhVp'
        b'Qxy5GajaCe0vXfSzifFG2CKIRibaWiUXQ3liBY5dnLGMP5Y6ATUeGWhZicxhg0H2GgTtEHRA0AkB+JlWvwEB+BZ4rlGrc08ScTerUyAZLDXw6EzUuDXcbTPXat1L3lOo'
        b'nWumUVqyA0qbQ8rAoI5dOZlQycIpu1SyPUM7VhtYPk1EJzuFmm8o1LNBFiWgosBP4VQ1CEl2cs0w5jqY5frTKWz5bMWZRDCyk+MSY44DWI4m4tML5FZtyI1IP3Zykxtz'
        b'C+iSkOSWYNIXI8mtNrSvQR6xk7/CmL8fLE6YCC0/iZbXILTYyTHPLEfSvkZBx7QPCxkGma5zGG1hU3JEfEHAlBzeVmoMC2b7dFcJHDEIeU3VlTrOleRKjIblDjYNy3lN'
        b'6VuHXj1mI1IC3WJPyYho5BfhIjLlHuqWJHARGWHCQTJpkClamRxT+DOJZMqkQgVXVgwgqOi5cmfMKFqaXlIEKgLTrMGPGQ85lmeX6LQ8xY+GCKO22gb+gE5DCU2iUOVS'
        b'shUtL2ybV4pvb+qkkTRbHu+lzYqcC3+JRnIguT29bXSkibYiDTAwkNjWW0zblcnk3V5MacCUbLUyJ78YyE94JY76arNa0K5+oNGo8oppV2AUI914rjRSlWmtVESfybPB'
        b'Y2LQU0bThxwZZVRXIKfRgTJYCzEw4kIMIyVuji0Ni/ZKFb0f6Jag7cZH9ZyuKde8QlBrlVLz85EtBQC5EKVFCpQGBRWBDk2qsyIo6CfTL0kDKNVSCGMsepGk7VAt9ej+'
        b'FyU+ktogbLJFfDSqZ8UwQ2bYpT8KMNIfjQ6UZowOt01fZIru4B+jTsmqoyqmBaUk5bEzZixYADWz5rQV/krlK4qoy1elGiYmGeU2M6q+JgUKt18gu5xM5gsh7G0JNbwp'
        b'VovFxB5TJieS/Zgw26RcplgYw7KQyWtCzpI3slijYoUqybXOcaVYSnoGbQ+4gfq9lZfD7x7S+8DfFLNENHRFTJWTr1VRDidNF8NY93fWZpoh0tHAjazUkcHVmADpwSop'
        b'30RkhCoib1zcnJDZcm22ElYZrTNOhUhJd2GOOQt1RQXKfOvtHyIdYxGN5ibX5VbotEoyc4DPY+ncErWGFspGGmOjpVN0ufnKbB28euSGKTptCcxvBTZuiIiWJhYrVMtV'
        b'pDMXFpIbGA+axqLmNu6OtFbkF2+gcdaSUZkUq+jFijXeWnov1i5RtCG7mv45LW/15GzWk2E50KLcL9wTTaufqya1CYC2NZZJnl2hywu03f1Mb5eOG267A5pFHB1lKybp'
        b'ZsWh3Skm2cUIy2QibSUTaS8Z0imM9bOTxnjTaDarFmWWmJV62ZzQeKweGeH4X1QeIDIpGVsNQ3lAOptjbU7YXVBA4DYnUyE7IjJOQBI5VBaT/6SbS2EOGm+HHt0IIjRP'
        b'JtwimXC7yVC8oRkPXwAl34uF+SbC5m1GfCK7NW4OHanhhDSAvOR8FyeP3XYz6NTARwj87vwvmdREtoubM0saMA8fzVeTl5SUZaztophAI7sSM57mC2VISlOgU2u6F8qe'
        b'uGdLvKSiZM8lP6OINsVsZb9nMgwFcUZLU+BLmhEetrjnt4Wz28LpbbafhgEdyouQBsp7oizb6wcUOkpugS8SsXs826NYglKtLg6NV8t1JCgcFRqvItKd7VGLRrc9VkE6'
        b'tscnyMD2AGUvZzIqxeUTIYyM/baHJlo2IrMprBfDVuMRKVap1IJkAd9EwIq0K99ll5RHS2G7mMhPuSC1khOkzW0/VLgJkLvsLnmhFA7s3pGj0sILSUK74h4DLENM9oMm'
        b'LAM5PWTM6MhI0tNslwmQwqRA8GW3R+bKSW3jyaBiLxLFGpMnBF/SjEjbEflhzkA1aqdHG1DQ0dIY8otJwhnh4+zGN77a9BbznTu77W3AVvN3sudje7AGTDUR0WKmpJDH'
        b'Y3tEzFblkAQTp5KsrbyRZujo7k7SeQal+qnkciSsc2UVPlw2jnHdowbUhi/xsLZ9YyiqiMHa/HELvS0hTcyFTesLNpuFl/uu5AwIp47pALZDJyYC3k6ADorxfmbJO6gv'
        b'91fRErC6Xdmqns+AneF4F97JIHjDcQc3KhkfoUBHdM09MSkZHUXXjJgmCmEuL6BpPQhbJXg78m9gmpzxLK6S04G7GnQ0amQwiQq8e6lgBohOT58x0x/to/6JOHwebZ7F'
        b'lY91ycOtpRTaczuG0g1mvVcq7/3J/MNJJZxuAqRzIiHLmiMiSCWBbURQR0R9cJVh27Ae7ZEEoj0Vqpfc+wg190giEU//tL5hxnTRTK/qU8/e7fz7xoLEp2fWTXvb5VPX'
        b'+O/edfbt/2XUvrfr3JwOX3Q5MLnXXwvvj175ftSafcdb235or0tdsuLQpsSHeP/jFa1fT34yYu9rWd8Ou/er5l2N72+KeVK24J7427wUdezvxjV9NnCadt7Cf34YczRi'
        b'YfzeCTdXPP3NHVXE43pRXWNE8ZeTTy1fkFE9OPh3kTMfzkXzDj4cOvy7pKo5M3676njJ6NGlVSHtug13Xtd9PyJ+yJJRhaMT2j8+3jjz1V2vvnxos6Yy6u5bG+J6d3jd'
        b'GHQz9uoBl8GShz/6bsqYveXG46vTvhr5VqAzA2U0V/YNHoXOChivHQNzzMNN1N04bsmSUizHSnSEp1uSrqBGkR6x6LVgvLECrU1NRKfFnGOhcOjSlYw14orUz9z7Jjo+'
        b'nG6JReKTzC/RpdWFaHNZYeLz9olQWyKFfuDtS6dQh0eOQOzUzd8RuoyOMCeb19AZ1Ehp7tBrTiEBFix3JwZTYEv4Ys+k5EQBuXSUE84SBOGzvt1hGJKfyR03GK7R/SnY'
        b'gTXbn6rkUp0pVZ1Y4CEYRr0fwW+wDHTl96aE1K7Qj3z3FfQSVEiMuzByhSLFzPNG1yo1WF6bbEi5vFDBA8UmiXR53zTWZKnVXammoaa7UmaltI7BoJ6UwJqIqxEbPSk9'
        b'j/An//89wh94JN2J84azYT8/24FzTqgVA4BgjiSfBxDsQdvwQY0O8MT1Yk6sGIHPClap8GWGQgGr/yjckOxGjvJQ+zxuHj6SRmHI8rlD0iPC5pNJgyJrOwBZe46HZe9Y'
        b'tVLw/YivRTBaZ8rjeQDlaQHeOAadxdcZaIRTjsTVFCgQKUBNY/zRVgYy4XJWMSxxzHxHTtL/vhOgNr4YqGagj3RXb05a/qojV5olSeiXwtAEAZHkJPhsKM1Kjqrk4SEX'
        b'KyRc/5X1Qi4tqzA2IZXFXJnpzvWfj+CkbFdpPIt5TQBGCoPFnFeWbMu4JSxmeig5mfw9AN6T5y0az04+mkuKJLlJi/R4SCGPgm/CrehselqaXJjGcYJYDmDKU9nsWK3D'
        b'R8eEhflSfwRk+MBr0alEBiyu165MT+Pw654ABDwOV9rmMDbZnatwlQGYIuYc0K7xAEzBl3E7xZRoK/AJkuYK8gIKAJiCT+PDtB0zAtAJ2OHCFwrAe/0OvJGSGo/CF2QA'
        b'CnIuC+fCUZOcQUM2R4goyMQfnw/hQnA9Psbm4V3K6QxOgjqCuhAlMvKoaF33+uDa9DSpJhowzRf7OKLDeG0x7Um5vVGzqTc+hwDq5H7zSwz1AQ2dOdeF8+r/hMzAWbKY'
        b'QcGsTecudua8JK5wsnCfoyPfpldX4ZOkSXEjXgeHVZx8PK6iiXxc4MMFzD/nSLrxypr5Gta5xigD0tPQoVdwZyDHRa9yw4dRUwTtp95oq0rjPgYfxefCxKSlTwF0vLaf'
        b'asWJaWJNFGmAc88+LtrG8/J+lJL9p1//3d/DpXLtuvS0WR/Okg4ZMuRvwzZ/MP7w4fnzHG8e23LuVf/q8VzEtEPZH3l4x03/h+LmN/9YPrHkj+/6K3em/Wr4jU/7Lk3c'
        b'ELJ41s2yeXuCEk41H3x/3vmVM9/7PFB5YG78gg/T9Jv/vG7sAM8Dj+8duVc79x3HvalLV22Z+2zNoazWT2Kbgv8jJn+/a3LtFaV2csnS+Bh9THtMxYD714Ki3Oqrn/74'
        b'YUrcMQ/HiM+eXc9pWp116feZ/U/cbWk/XjPxnYwfqpbdbA2NbksNa6145N9WoW2or3jaFDalrvXlf6wfWea4Xbh2/19GrfPd0DRS805ureidxj1zH7vf++D7hbN/tfDC'
        b'4sr2zi/vbktWDyv+9bfDxt/eVv+wsC7u97djyhed6FxxcMQvD+5u/Ortue8p/LUz7j0MvbVl+TpcGuijBc+VaAPuxPvtGXGg7WgHP0HLUCvFZ3jimiHBdM4nc7dzgR/u'
        b'EKJt0e4Mu3HyJXwNhLrL6HyygBMPEaD9QnSCmbTsmIXeMHE5eGEi0ALiqmCKH5mLDqJjPD5ls7qL26ADXWYMhp1oB2oBPwunZnZDkEjjHFzwmmHMd+FV3LIE7GLwtiij'
        b'aQzp6nX0aizahF7nHZXitYAroCASr+WM3mYnrh5ksAIC651V5bwRUMirzLZmE9pMRJVT0xnGpeAVhnKJQJ3UtmbIVOrEvCEIX7FEmGSgk1qeD22dE8hZ3pMMrJa4bTLj'
        b'NN41HdwamKJLPPBudA5ViWIKhjJ569hU1G4OP12PLwDApBTfoCWUZU9MMoWWeMSjk6tEseiNsTSBvhNxI5j2kGocscCWZGvoI0zOyWaWQ3gd7jBYD2WPoYknF+ELpm4h'
        b'L46jiJGj6Dwr3a6QPtS0aGqCJUxo6kT6FGehFlQHDeyLOq1ZSJF2O27TWZx94WuZQfgq7i58lYKwxVONCb2EzMLfi0fIAqjDiwhfIHp5EWGsi4TRi//P7PuBzMJRKObB'
        b'Hl68pT+YG/GcYlQMsk9bZr1q3QjMQPJ6yVLyWsMdMPd0aJkpSQe4df4/jxn9+9/nMXNi5Iz4asBSoNeqQyfMqczMeczmoeNs1j4RBlo1UJOBGxoZz01WgM4whOauMu9g'
        b'Jw61opNATYa3okYqGYSljggeok4VcpSZLCBXtWDAA05zjlzpXzJt4mKufoIHCvOKzftPD6/VLZ9ztdu3i9KWCSZPDzikWRuwVegT+GjD2IwpSaq7PhO2PbizNO9ObTva'
        b'8WDylmPD/vjmd7sCzkZXLJ3qfj0h/KDD+Nqn17m74166cfnNMzPXxUe19eu72uvcWytWZ/86ZcE315SnhL3bWmI7awTVGR8W1+s/K/vUb+TQW/tuyD/zrf7ky9hLf/hF'
        b'/Lh/7okqunwwvqBwZ9jH8i3+bSX3Rd+84ynsHLc1Rh7oyXxInyifQpoN1YjApS5lJZuEG+mwPA2fJ+OZKSXZMRj3havQaZ4Xdid6g0hZlHYsk/KKAe3Y0AkUuIeuoiYi'
        b'KG9GW8nUYEE8hqtQE82ijxs+RCbAKtRiyWw2NohGCEIXJyThbWinBTUZGbEO0JllOT6NblBuMrQP7U3l2clUuJVNHFtKKmHkXJJn5jUYHyqlFXDt602Zyd6ANRyemoyo'
        b'v0fpsBqImlEjUIGRPrLHnJ/sgAOb846SqnRQijJ0KCqUpyjD15U076IpQ0zoyVAV2kgpytahnWxePiNaTCnK5qE1rO1ihP2JrH+SJX0OnfZi8zI6Wmacl5We7OoedAPV'
        b'07LVhMkMNGVFqOVn4SmjzFp0TA/qPqZXciFD7VOVwdD4s1OVEVWD92u8xuLzhRXSMkMRSObm6BsGwxPSr5TAXpbQOx3HmeLvemBRCpyEegeVVlmkYQA6C2oy739rjaMH'
        b'z+p1EgwR8Ysfzo5iIZlfhX0Des5EBk+xv0Ba1msC1Ukm+C3SzO9rFEwdOHc/IdFuOscFClJUY4rPizR+ZFbKOnguruFacRXgy/udi1rJ/TFs0rrBwxcPksY1v/dWqF/S'
        b'qK+/7rU3YdmOOL+30/MaD8V+8mjlk8FPBq5e9KzTs25de/Rf8v5RcyYhN6/54V3fM8pV7u/XtTf+oL1YFxbq8sMRZUtHdMnuuVPCb9xy++zKpkcPU1+Lz9957KzW7f10'
        b'5PXXOv8lj/fmpKzAvv1Wftm+0Uv+4d+rvou9kFr9p0cRgxrn6ybNjb+bGOlZj/zOb/1+R92YkxuHJ6w/5n9kdejOo9MeN69KzGgounlr95PG4DuP106cFOkb+fab+3yL'
        b'bi0e8pd+Du5+Tg3DXp9826EqeMVC9Q8l711TzPvU+8rJNxf7Thyfc7ZIe/w9xe/6tlzZf//z9B1ZNdfLn+YccZyY/sG/uNh7uclfVQWK6AIYOrdQgzcnC0rGg3883BBP'
        b'BGEYFfHpAbgTlu6IRHbUjDxH7IxacS1di0t9Be2na3FE2rxKBkjLxbhB+GL31bQB/zM97YUDMs6IDG+a1YBCgJ0zMwtL5IrMTDrOgM98zk8oFArGCqRkXHEU9BI6+0l9'
        b'/IJ8XvEZ+TKMOhOdRR5uIyq55er/ML5cIr0wM9NkUPH7v6D2AvUt47sJJYWZgHn7fTDZkjptMDr2MtEItpBZdWNqMtqItqAruNmJ8/AVDST945LqweERAg0get9/lDBw'
        b'YxQRLXwcfvzua6/JCYWbJmdH9Zp3btZt/e2Byt/FVfwzo3pfr0Xv1o1Y1pLs7z72ScaqFV+uzdt/6/6mwH+d9c5UDZfdut0ndPbBm4djzw+vPVWkSZ/bMj140Sd/0N2u'
        b'lQvXHj7kLf/g0Pr1uO+ER8t+4T2y+cNffrEuWFh89Yu1eXeHH0Q+sZV/23z/byLn0oCn7jOI7EA1p7V4XxnMveiASypsJwC/sRu6IMQnR6IWBntowRf8k1JD8HlSxVSY'
        b'nr3xPnwEd4rQ4WXJTFBoQCdfYc0AOgmowug4Pk2aoZdokBI1UzHFmZxuSUqcETTDCe1O48g45zwanaYr6Kghu4KMVa/hzaGOnCCdw0d8cYeWedGrSyez9dXg6Q6cIInD'
        b'TYvReqZwnhmAOpIS+6CLM8jkXTcD/AW5BQrxVke0iUYYh2pRsyYxDb/WFcE1UUiUwgOedHLvTV7Wq0l0mASNMGO1A1EaN4lS+symxRVN9E1KJEr0HuZSEfwp1qNTTFvr'
        b'mIdfB7EzCzXIEnjRStJbiC8tQVdom/nL8Qaiz20i4tUaWSkfwxVdFKJL6KAnQ7wcjI5Dm0aRWBckqLZsmQ5fXCZZphNw/fAWEaobkUoTkgWhQ0nk/lZ8GtcFA8sgOI/a'
        b'K8QtRB1uYcv+7S+HQtuHJpERpmEW6oDVfDjhxA0YJkZVjmivmVvpgf/nXzHLN87lOeONleGnC9JCiVjdnZkPJqptgn4qEU2ylHqGMbmAjjuD9aJCZbFeDPbVegetrrRQ'
        b'qRcXqjRavRgUQr24pJRcFmm0ar0DXX/Wi7NLSgr1IlWxVu+QSwY+8qUGcwxgUSnVafWinHy1XlSiVugdiWqkVZKDInmpXkS0Lr2DXJOjUulF+cpyEoUk76rSGKC7esdS'
        b'XXahKkfvxDDOGr2bJl+Vq81UqtUlar070fI0ykyVpgQsRvXuuuKcfLmqWKnIVJbn6F0yMzVKUvrMTL0js7DsGktZRQeq/wq/H0EAXHXqzyD4FIL7ENyG4EsI7kLwAALY'
        b'2VPfgeC/IPg9BB9D8AcI/gyBHgIgUFV/DcFDCD6H4CsIPoHgPyH4CIK/QPAYgj+aPT5X48D6fazJwEqvPXPOBTPqnPxReq/MTP43P+E88+OPifKbUyDPU/JIcblCqUgJ'
        b'dKYyIPDVElWX56ulUqLelbS4WqsB5VjvWFiSIy/U6CWzwKKzSBkHra1+Ymg3CyyE3vnlohKFrlA5CbAMdIVBLCQDmGUXG+dDFzz+G25/seY='
    ))))

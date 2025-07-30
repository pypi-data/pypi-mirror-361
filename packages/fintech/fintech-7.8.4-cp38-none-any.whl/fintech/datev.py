
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
        b'eJzsvQdYW9f5MH7u1UCA2NgGT3kjQGIPG8fxNiCWAY9gOyCQANlCYA0PPOINGPDCe28bG0+8Z3JO24ymSZs0HSRpm6RJ4yQdSZtf0jRNvvecKwnJkpykvz7/5/s/z2eZ'
        b'K5179nnf8677vue+hx75J4K/CfBnGQcXHSpDNaiM03E6fj0q4/WiI2Kd6ChnHqET6yXr0EKpRT2X10t1knXcWk7vp+fXcRzSSUuQ/3ql31crA6ZMLJ06S1FXr7MZ9Yr6'
        b'aoW1Vq8oWmatrTcpphlMVn1VraJBW7VQW6NXBwSU1hosjrI6fbXBpLcoqm2mKquh3mRRaE06RZVRa7HoLQHWekWVWa+16hVCBzqtVavQL62q1Zpq9Ipqg1FvUQdUDXSZ'
        b'1hD4GwR/gXRqtXBpQk1cE98kahI3SZqkTX5Nsib/poCmwCZ5U1BTcFNIU2hTWFN4U0RTZFOfpr5N/ZqimqKb+jcNaBpYPYgth2zloGa0Dq0c3BiwYtA6NBsd40vQisHr'
        b'EIdWDVo1eA4sHixDrVJUUOW6vjz89Ye/CDoQMVvjEqQMLDDK4PfucBESo0lQpiLvWfkiZBsJN/EDfBqvI62kpTBvBmkme7JJe6GStOfMLFJJ0eipYvIgoFjJ2eh08fnF'
        b'eJeFtE7NySebSVs+aeNQQA6PL43DO5S8LQqKkG6yFmly4nMkiFzCl8RiDh8mHXiNjY5qMLnqT/PwwVQVaYEGJCiYbBIViIqhtgIKZJKdUKuVnCNNZFN8A4yqDRoKwN08'
        b'voo34Uu2oVAoLoPsgjJX5Lh5ySIb6V4kX2TjED5j7Ue2iHCbVgujHUGHsos04TO4FW9J0OAmlSqWjplsoTf80IARYrxucngV9whyDnAsno5CUYAh+mFQrB5ghyDXDEi8'
        b'kgcIck4I8gyC3CreDsH1j0KQDqKvBwSHCBAMkkqRHMkWihUV8nNTxyB2syWAB7B+meKHKuTihYXCzQ+j/FEoWh3jV1Ehf0MbLtwcMkuMZGjPMvGEijxl8izUiYwBcPv3'
        b'uijxP8LRhL+lXEv7jL+eNEf8OjL6Q0Zr1B6uq64iBE2oSH4ruX/qZ8LtwNLPQpqXqofwRX/gvpnzSvZ61INsaoofp/EO3ARQa02YERNDNiVkq8gm3FkaQy5Yc/PJlnh1'
        b'jio3n0OmEP8nRs3zWPtAx7SnCGvvvnsQXfnqQOfa8j98benukHqsrbzATHu30VWfBdjRVVKsmsXj1gWIFyFyMAnvt4VB1mzyAF82rSyBRoaj4c/gC7Y+cHc03kor8LBz'
        b'TiBUi6aS22QnK89V4/148zjSAY0noISnqm2RdIkO43OwIzqHkA6YvgqpcMs4lhFFTplL8meQdgnen4L45dxAeYFtNK3RTA6Rg3QrxGkAf1vyZsTgzvjsmUVBQ2GDqkmn'
        b'BK/FdyNsdFL4Iu4uHkk24G6Y5jg0jhwvNbz3+T2xZT9klh/rM/9nScE4Ub5B+6ahrKmzJOS56Ki9c57STpzV79SsQa9vyN55ayrJaUwN37oV//Gd5Q+62s3Pji7c+tew'
        b'C29uqN7zi+PPHnz+3pErTSL5+V8NfkPSv3DS4NmRw2eeCA648WL9R+M2XjkX2Zh7fYXqjVkfZf9Y2vHgl50/a31w6JcrvlKtHGWYuvjdwtHDu+7Ms4b+bc3kONP5HcMP'
        b'Pfd5/UNR5l/LapUSKyWh5Dw+To5qSHscac9/Bl9V5VI6Ek5uikhTAtlnpZsTAHT/GXK/b1yuijTn5BVIUCC+zJOD+NJIKyXB+AzZjA/GqZW5cZTE4D3PAJUJIatF9eSO'
        b'xDqYljhIOnFTIF1E2wxyHujCpgQehZHbInxeLbNSKoY3GiNhxTeRLaRN1LgKicdw+PJocknJ9/AxSjNFHWUg+/oPLhQLv+o7rtpc36g3ATthjEoNTEa/eHxPkFlv0unN'
        b'5WZ9Vb1ZR4taKGFE42VcKCfjAuDTF/6C4UO/w+E7lA/nzFJHy0pRj1So3ONXXm62mcrLewLLy6uMeq3J1lBe/h+PW8mZ/ehvCb3Q7p6kgwumgyMKXsrxXAC72obR++TM'
        b'uLhc0q7JUeFNCbD3NyfkcvPJbTQSX5aUk5P4mNvGpP/E9m/GP/VULACRQMeVieBPbEBlEviW6vgyP11wE6rmdGKdZL1/mYz9lur81svK/Nlvmc4ffgcIHLhapAvQBUI6'
        b'ENJATyAt1wVBWq7jGIUI6ZEWs9UqYKv38BvYlVUil2HR6fo5aEYqcrB2aEggRKJmERAiMRAikZMQiRkhEq0S2wlRtTdCJPIgRGKByOuGSia9w4WCoFQhf+uJMGRQ/qVQ'
        b'ZCmEnD+9/+Dj0LyKlys/rNiua9Z+VNFW06X/ENJlz84jl7YmbZhx4OiusB8Vas9ojZKz3NmKl8Tb4gfJp6oHtQXOyVr9UVR0cdTa6MzXuYYXQld9GKqUsv0AxOU4Phun'
        b'cTDIOCkKwadEer9Gspa0s021CN/BV4QS+AI+S0uJkDxe5EfO4Q3W/mzrRuDLmv64m7TmgfCglCIZ3sQvjcVbrdGQ3Qe34L2Uhmly8HnAJXJXmslHJ5GDLJfcBBGhBbcW'
        b'gmwgRnMXScgBjtweRHZb+0FuEVkfFjeG7FBlM7FCRq7yeP2qVCXvgpsib5uMoWqPrLzcYDJYy8vZZpLT5S8L5ehHyom5xhAB/GpHKWETSXrEFr2xukdMZb8ev8V6swXE'
        b'RDMFj5mywE7O0S/dAOYgeglx7g7ayVzn7jgd6rI7PPqr4h/ZA05kS7YjWzVvRzWe8TwRoBrvRDURQzV+lcgXz0M+UM0WC7+Xp5ELgaQdALMZeDbZUpItgG9GET6Oz1M2'
        b'iJ4kR6Vhi6MMDw5NFFkS6cRWHPu4giLdC9UJ4XHaPO0nFaFVtdXGSvGmJFXFXyrmvBD18rO/5ZFKcvht2e5dbUqxlXLWuKcbNND45MUu2JFVYaUiKDlC9pL9IDm2AL3d'
        b'olY1qGJxCxBfSpb7rxLjDbidrGFYph6Bb5Muss6BKgKikCv4ipXOrw+5GKspVIWFc4hfzE3E1/ARAZy8V8wAslijtxqs+jo7clCqhioDODnXGO4Ek7OI0JSYAbtHbNLW'
        b'6XvxwRwqdBPuxAaGCFQOqHIiwuFgV0Tw0sN/nfB46Ac+sSEOfvfFJ3Dro+hALpkEjOjFBnw12MBf2CliGBpz5rYLOrz5tgtCfFLBb0q2Jf4m8USiOKXhFIfOG2RPS15S'
        b'itimHyInXRpXakGuDOKX4oulDCdA2t9FHjhxglzA1yhe9OIEOYYPMV6d9mSaGzqcJQcAJa5r7dzQN2EA8Fs8wV/zCPgt7uCXCNClcO6RLNYabR5IIHJBgkgnJtAFr3Vi'
        b'wr5Q75jg7Mw3VUgXMIHKxly1+AdQBg8mxNmbdscFSYEtge7JnfgWPk+VtVLSrFKpZ2TnziTNhSWC7JkNYqiaQ1Zyz8z7S/HaxQx/YnLJMe/UpFg1ghx2oA85gy8blD2n'
        b'JZYCqBSY1vFxxUeAQcbq2L6x2mytkWFOg7Z551n9Ge2HFa9UvswITa72rDa0Cr3YdxM3dW+/Sxn/sCbG63S6bK2s+g95fihNG3LgkEUpiHjkBDnKCRKeHWcm4w5BwsPH'
        b'rQz98PWiMXb0Iy2zHRRJi49Yh9MGNk7B53opEt5Pzrph30DczHhTGj5CbuPW+NGu9Gj5INbDNGCO7XGUa/Un152MC3dNUdqZh9ineCggqNTWQKXCXr5lDAARUMbEv8Yg'
        b'O9IIZVxpk8CSnFjpsQWATPUyLYacVJGpcyLnznBX5HTvx0Nnc6dQTFt2UiiumftOHc0DK8VesVJUYHj7dR1nyYUbE8dlabTZNZ8AzrxUWVsdqT0juRzVL1GlozjToj2r'
        b'79LzL6oqLmjnvTDnp/M+epGUkiJiJEUxbzw3R/TLsJef3RuMpD8JacjaCayJcpUqXY0DE9aRqw5UIGfITca5yNWBYa4UpriM3B61ioGfdETPJ63xOaQdVDHp03x/5XDS'
        b'hU+yvDp5Za/AA9JOHWmKXkbueYf64+gUiPEWq9lOo6i+jqyhIPjLAQ8ag3tJBy3CanWKBND6xgCQXnqBT6docwK/3Y0yPdK8ki8wUyVdGUSlKsoBQbkIKC8XrGrwW15e'
        b'vsimNQo5ApGUVQHa1NSbl/XI7FKUhUlKPdJqg96oszBhiTFKRiMZLrIxOejtY/UoYQp0UUroFCi9lfFizv7hg2VyiVwSKhNMU501+H4g1UXIDnIc9BEkk/MVc0p9ayLU'
        b'puGmifBlYp2Iah4H+DLJDqSTHgHN4yi3jgOtRMaw2b9HOtUERHzZV5FT9JUGaz3ocwkas14n/HwoyAkPaRdfhc/SmxttNZYGrc1SVas16hUpkEVn9JU8T29ttOoV08wG'
        b'i7WTZ6v+8Ccw48/3wqpq6k3W+qwCWGVFzESdWW+xwBqbrMsaFDNBmTSb9LV1epMyyyVhqdHXwNWqNem81jNpreSu2ahWFAGM6qHurHqz6fuU89bYQr3BpFdMNNVoK/XK'
        b'LLe8LI3N3Fipb9QbqmpNNlNN1tSZqjw6KPieWWJV5YAeps6aaIIF02eVAi80JkxcqNWpFdPNWh00pTdaKIc0sn5NlsX1Zmi50dGH2ZpVYjVryWF9VlG9xVqtraplP4x6'
        b'g7VRW2vMKoQSrDtYeQt8N9pcqjsSlUvo6KgarrAPBG6pFWU2C3RsdBm8IslnTnKWRm8yNaoVmnoztN1QD62ZGrWsH729P71iOrlrtBpqFIvrTR73Kg2WrFK9UV8NeZP0'
        b'IGsupO3G2G8pHXmK6XrAHXKi2mqhs6RL6llaMT1PmTVVla81GF1zhTvKrBwBT6yueY57yqxp2qWuGZBUZpXALoZB6l0zHPeUWZO0poWOJYc1okn3VaN3FlIcVhXY6qAB'
        b'uJVHTlC7x0K6asLyw82cSRMLaJ5eb64GWgE/S2bnTCtVTa4H2NgXn+0Fg6kWcI22Y1/2bK2twaqi/QDRqVTb+7T/dlt3b/fp2rtNItljEsmek0j2NolkYRLJvZNIdp1E'
        b'spdJJPuaRLLLYJN9TCLZ9yRSPCaR4jmJFG+TSBEmkdI7iRTXSaR4mUSKr0mkuAw2xcckUnxPItVjEqmek0j1NolUYRKpvZNIdZ1EqpdJpPqaRKrLYFN9TCLV9yTSPCaR'
        b'5jmJNG+TSBMmkdY7iTTXSaR5mUSar0mkuQw2zcck0twm0bsRYT+ZDfpqrUAfp5tt5HB1vbkOCLPGRkmdic0BqLEeFCRHosEMBBmon8nSYNZX1TYAvTbBfaDFVrPeSktA'
        b'fqVea66EhYLkFAOVGPQqgd1NtFkoQ2kEqSFrNjlRa4Z1s1hYB5TqCTzWaKgzWBUxdtarzCqD5ablKiHTVEPLTSMnjEZDDfAoq8JgUpRqgS+6VChhMKA5Rcw+69pYLxtX'
        b'lcEogGDE0OpuGfb6kDXSs0Ky7wrJXiukKCaZbVbI9qzH8lN9N5jqtcE03xXSWIV8rcCX2ZqDXALyCbtn1S+1On8AJXL+THEtanEWEwAxSQ/suMblxsisMoMJoEHhz/qh'
        b'WY1wi7JeoNJuyWT3JJAfrcUK3M5sqLZSrKnW1sL4oZBJp4XBmCoBbZ0Qt5rJiRpAohyTzrBYrZgm8A/XVLJbKsUtleqWSnNLpbulMtxSmW6pMe69J7on3UeT5D6cJPfx'
        b'JLkPKCnNi5iiiCm2r6rFLmgoewUjb5l2WclblkN88pXnJGVe8gu990blLm/33UQx33N4TL4v6eyHFE723bObnPZ9igGp9FbMjQWke7CAdE8WkO6NBaQLLCC9lxqnu7KA'
        b'dC8sIN0XC0h3IfXpPlhAum8+luExiQzPSWR4m0SGMImM3klkuE4iw8skMnxNIsNlsBk+JpHhexKZHpPI9JxEprdJZAqTyOydRKbrJDK9TCLT1yQyXQab6WMSmb4nMcZj'
        b'EmM8JzHG2yTGCJMY0zuJMa6TGONlEmN8TWKMy2DH+JjEGN+TAALpoSskelEWEr1qC4l2dSHRRUxJdFMYEr1pDIk+VYZEV90g0ZfSkOg2H/sQp5n1dTrLMqAydUC3LfXG'
        b'xSBJZJVMLZqoYtzKajHrq4EJmijP83o72fvtFO+3U73fTvN+O9377QzvtzO93x7jYzqJlKAvNJG7DdVWvUVRWFRYYhfgKDO3NOhBHxaEyV5m7nLXwb5dbk3XV5K7lNM/'
        b'IjbUCPftUoMjleyWSskqshtXXCp7mF2SPG8le94CNcdIlWKtlcqlihIbNKet0wMb1VptFirWCrNR1GlNNmAvihq9gKbADr2ZAZQuVQyUuRt0rNp3FvbSvhem5L1tz4LM'
        b'xNS7OgoQvhV2kZctZTXNty+y8DvZ5TfVCXstVV9xWQWdMjO1fpupZdVMPTaE5yHUf8xMnyX3SCwNRoPVPNhpwwt1t+ZRT5CVbtY8Ec/x/5ZKeJ7/hk/hf8aseU/iTSUW'
        b'6inSUoXPxeNOMZKl86sy8v6L1rxapX9PwMSqqnqbyQraQ0/wJAC5oHVoG/TGh30EWx41gX/VfwogQR1IFtRcqhD0HkBhAxAeKEKtsD1iKgGZR8HPz+/CjZl1gkBTX2vS'
        b'K0rqjcaEbKBIJpWmkdpXepO9NC5rtqZMIVSjdjRKPS0Gi024QfNc08Kem07NfoJ8L3Q0aaaqpKrWSO4C7I0gk7gmsybpjfoaHZ2I8NNudOn9nWzXj7IcK8HkfSoQ6u1b'
        b'26G0KQShyK769Rqp7EofE9WpugeFYXNZmVpgb4F1ZzRAAfbLYKquV6gUE81Wx1Dsd3JMtOYjN2mxZG/Fkj2KpXgrluJRLNVbsVSPYmneiqV5FEv3Vizdo1iGt2IZHsUy'
        b'vRUDGaOwpDQJbmgEwFBZV89uJnvchIQiXw/00mGJVdjUil5LLNwUcNlhGlUrqLzu0LoFk2svGBV5cXlZ02ymhcypVm+uAQLVSIkKvT9ppiJ1jMBmqx1FqEnY23073ghZ'
        b'XhrMKmPqAJ24uU5LM50o4i3HiSq+qiU/rpr3TAGFHlPNe6aAUo+p5j1TQLHHVPOeKaDcY6p5zxRQ8DHVvGcKKPmYat4zabUxj6vmPZOBO/Gx8Paeyyo+HlF8Y0rSY1HF'
        b'Ry6r+Fhk8ZHLKj4WXXzksoqPRRgfuaziY1HGRy6r+Fik8ZHLKj4WbXzksoqPRRwfuWzHPxZzILfESu5WLQTWtQSYr5UJpkv0Bos+axqw+F7qB+RQazJqqW3RskBba4ZW'
        b'a/RQwqSnQlGvsdHOOSnBm2irpmYxJ5Fz8FLIopS3lyErYiaaGgWBmD7PA2Kcb7ACa9TrQALRWh/JfoQOe1bupeSP5pmN5LrFLia45WSzpzvVVpBKnGoV4yQqJu941QHs'
        b'M7Vzc2D9wGmoCF3NhOc6yuCtegMsi9VpJ84BSddqqDYs1LpS/zKmBjrtx65ihqA8ujxHdBWTpukFzUJvqKRZeQA1+mDMIkg2vgU1V9swjBt61hptdQv1tQ5DNmOCTIpT'
        b'ghRXYI71JcLGw+WuTxF2AP++jbk77x9K1uNzekteAdmcwGRZ0qbxQ30qxXJy2dNxS+6QZBdw7pLsDumOwB2BOn5HxI4IQaJt99PFN0magpoiqkW6QJ18vT9ItWK9RBek'
        b'C16PdCG60Ha+TArpMJYOZ2k/SEewdCRLyyDdh6X7srQ/pPuxdBRLB0A6mqX7s3QgpAew9ECWltMRVPO6QbrB62VlQWyUEY98/HVD2gN0qibePlqxTqEbykYbLMxqR8AO'
        b'rprOzI9dHbWGtfvr1MwjTsKiMUKhrp9uuG4EqxuiS4A8SZOMxWqEs7yRulHr/ctC4W4YjGm0LgbGFAZ9ROiU7Y5Yg+CmkGqJLlYXt14GrYQzLWC9MrFHNoV6Z08umfVV'
        b'QoDC5Z/jtkIgIUIEkVuJTomZ+kObaUDKQ+akTb2rHjLfDKoKKOUPqUvNQ+Z8TB1qeoubMxzFzZn0kkSLUFeHh8wbgGKD0q8nQKtbDFTJXG7Q9fhXAW0wWenPYK2gt5Qb'
        b'Qbiz1vbIqmywbUxVy3pk1O/UoDXa3TACqw0gz5XXwZatZX33iKbOLBb8PMxj4FIlc0HBAPsf886ZhB4JdPJvkjYFNPlVB9gdgGTNsnVopX9jwAqZ0wHInzkAyVb5z0E6'
        b'EXOZEH9OQyTcVo3+yxGGaWjUW1hgl3OtDcyPoUqv9qjicWMsqBvaOkXvEo21h3QBSaHWH3vMmH2ttCarRwv0X8wkoARWBx1SqhUTaX2gGVUK5gGosDUogHJmKHSGGoPV'
        b'4jku+zCc0PE+CiHb+wiczzi+Ywxp3zUGd7QYq8hj33QI0xPyHLn2gVm8j4XyGUrhgT+oFaW1QPMB+/UKi63SqNfVwHy+VyuCA4mgnEJLCi00AWlh/ApjPfAfs1qRY1XU'
        b'2UBFqdR7bUVrn3yl3rpET5/xKmJ0+mqtzWhVsoi+TN+wsG+HsYrJ9l+KKmokjHE+WnQxLip9teLYSmMd2GpxApMGENabFTGCo8pCctfcCAq3r4bsrlFjmXZFJRFoRsAR'
        b'O2WJ0deoFWlJifGKjKREn8247OWximk0oWAJ2ly1wQS7BsaoWKbXwsBiTfol9Dnn4nR1qjopVum5VN/Dc1guhCxcnBmKFAgtjV1cYdwStgDZxlO+ZyYnSWs+7ioizTmk'
        b'XZNAWoqoC2l2npK0xheoMA2vubw8b0Y2Pp9dkJ+fk88hsg0fkdeTm3g/a9eMghA19mQ9XSEfFOyHbDTmxAgV2702TDaTljzgo7iF3DGQLe4tr18mR/g82cgalk6g4XEo'
        b'6p2KCuPRBCOyxVB+vIO04xMukVb9xDOy1apYGseCL4hR+jyphWwk21i4GGumOIzG46Fsv+EVeYlDJgjjU5A9pLl3fJvJXZcxQk4bzJ6Os005y2V8+JY5EF+pIHsMQcbB'
        b'nKURGjq8TDvo5Tf9VyfKN7xz6sbV2xs7bq4VyV7zS0gYVnBEET054/PUyOA1fz29fcP04etHtmxfb7o7af+Tt1/vu/z1qZVHC944O7Y25POzf/n88MSwor/1/4PW8rx4'
        b'y0e5udrDgQ9mDPjVxl+M+PrTIy/2lGrevbysc8nxN/um7Bn37ZE45e23/6WUC5FS3fgg6cKtCc7YEBG5j3ejkJGi6siVVgUtcv3JfNxa6ALSPA71J+vESdGN5ALZwMJH'
        b'+uG9iwNhSZX5DnfcPuTgMtwkluHt/kIzO/H5CdCOCwRpQ32D8dmh4sA5YubpTfaSa6PjVDHZKp5WuCvF+3gVvl/PWiB3YHxroYkV+KALzMLxBRFprcAdzJUzuRLfjlMr'
        b'ySYQ0DLIbinu4lPEWSz2bBW5Pg+3AkbuDHeBkBSFLxbhe4npVhqKV4MP1UIPQficQ2Kj47SjIEKJZINUPZ20WCn3xgenkT10Rq3xsWpaDHB2SxwtprBIJpHOIHy0SBj4'
        b'ZdyWyaY+jYmAtGcV9It3i8iGUHyNtUau4m34Bl1od1GxP74pJvfwLtyaUiw4TAb8hxFpvZErzM+UdoqeQSuknJQFnknt4WfBcKXBZzKe5ki5xjAHX3ZGtBQ4BsJ8TOmO'
        b'ME+gl4n0QmUG82TkCJehkZ6Pc1WWCbV6G5nkrMUa8RJ485AOn8rjaDXaO9jVm9VzqG7uzJz9j3mS0jGtQAsEF2WuQMn1BJb3ihHmKOeyuQQajTNq6yp12vFh0MrfaYsu'
        b'PTryvrKTdXtbDhEgBtiFTlVvMi5TdnI9Il191fca2nphaAHlTtHC28jM2XCJhPrmHPjx1RBhBEIVLwP4IT2HlLsLFD677+fsXvlYkeMHD8QOHf9yB0f3OYT+ziFET9Ja'
        b'9E4R4Ad3WePo0ilJ++pykLPL4T4FhP9s4WXljpg0X30revv2KVT8Z33Ly111Bl/9D++F+HdIIj5G4RZewILh+CbkDIb7j4ILHM16BBdsy/9azAJt3/n0lBDOVFv9CfpF'
        b'28/a3pU/J39gO2BA44+Kfxs8TckzzqjEJ6SUZrsT7JH4PtBsaxoj2U/ijbgdyuDVpMsL1QZe0z3tcdFpfuV0T7mGJj0Dn9GNoS5UjBUQ6vR7tKUoJzSegssoWFkLfRAH'
        b'VHE1esstEs2jRWVAj599XwpO/FKL1azXW3tkDfUWK5WTe8RVBuuyHj+hzLIe6WItUzsDq0Bar68T1FGRVVvTI6kHbDdXBbpAgBLtYAcUaERHU6BTjQxyxvwHC6ctVAfb'
        b'AR7YLAeAywHggU6AyxnAA1fJ7crkelAm35Z4USYn6nQW0BaoyKvTV9J9B/+r7D5wCj3z2P8e+iTTdpiqolXU2mr0LhocrIzFABqQQghroMqYRW9VKwoBrz3aoQSgjj56'
        b'MdQ11Jup4umoVqU1gTZDq4ImZNZXWY3LFJXLaAWPRrSLtQajlnbJhH/qQWlR05kaqBENdpe9SbsCRdv0aAOatlkMpho2ImczilgGtNjvsSLT7LOtpdYPz7F7lI+xas01'
        b'0IfOQYlofQU1C1qoMmJZZKOrW2nWVi3UWy3Ksd9fxxfwdaxiohtDUcxlD0Ln+6pGex6rYFEMc78zlsFnK8L2GKsoYd+KuXbPOp/lHdtorIIaNQFUTPec6+pZ57Mu3Xig'
        b'tcJVMbfQbPVdTtiaUFT4wfqIV+SUFKpSktLTFXOpIdNnbWE/gz46sVSVM0Ux1/50cH7cXNdIDd+d95IBqmELCQVtyNU/2Gd1IBywmLWwNWC7WqrMhgarnX9RPKUx2Wxv'
        b'TTRa6gF/9TqvxgFAJ1qachsjO7WHAVutmCJYCNgWHVZi1dbV0cg20zCftgK2GQCxYAAN9q2lM7Bzg7SwrEsMwNX0SwHi9g3n2Q79V1Bv1QvbhG1+vbW2XgeUpMZWB4gG'
        b'Y9EuhA0Im0YPq1OlV9QDe/fajjAlummY6cMiTNNgcRmSWjENiJqDIHltxXXbUUMJoDo9FanKCBMWDkSy6L3XrLCfiVRfxUYuPDcZV2u1NljGJiQsWbJEOMlCrdMn6ExG'
        b'/dL6ugRB0kzQNjQkGAD4S9W11jrj8ARHEwlJiYkpyclJCVOSMhOTUlMTUzNTUpMS0zJSxoyvKP8OswTlfZ7hguEF7Dih/oPnWvKUuSp1QTxo/kdyqMLWCarfiBJJLTmM'
        b'N7BzWtTLyOYU+A4nXUkoCZ9XMs3+4RQJksne80MTKozvDV2ObGMRO1FoPbmjcXDzGXhXP9JMzyrJVRXT+OjiGBowOht0fPgCPo+344v+ZCe5voIdf4Sb8M2lpDtrLmi5'
        b'VBX0QxKyl5fnkS3svKIACekm3Wp6aAZp15LrpBWahsZB2x2CT4rJbbwlgxlWyPawAaQb9On8mWRrg32CwuTwXnI0vog0F0DNNs3MBrgU5uWSnWJENuG1geREipENxTCc'
        b'3AhUK3PxXXwYn/cLQP65PDlMNuJ97Bicmqxk0p0DlTk0iXSL8G4Or54kE05VukbW4K2BpDlBTVpy6mGu7fG4Mxd05mYOKaZLxFlkMzsZh+wgV2JJd0Ish3h8c0Q2ly4i'
        b'u9na3snwQ/JsqwQpKuQT0goR8+dJJNuLLUGwWNdysvNYz7J5/PQFo9iRT7gjbwXNDApSR04g28i1PHI5jmwXoX7LRLgLH4y2UTODZZEyUE1262DgsGw5dElEqA+5JQ55'
        b'gtw2XHnmOZFlHxT73YcdqlfyA3BiqOQPGTlf/f7DgoevrLv5WcDT2gmXBijVb+afSzy9te+4MwmK7i+XvpMUsa7PrLcv3/QfXjo25itzZueJRZqH8p92pT+VaWz5avhX'
        b'ifMOFax7kWt9uRJX/6T6yJifGSYOKCsujCt7bd+pnwW1k+ePTXrzxsev/XnP767O/Prvm2+tXGF78uSbq4KOv3XpVtqAyy1/Ozy79OKQHHPckoIspdRK3aRIRz25zKwu'
        b'+Fa5w/DCjC6xNcwOsaSBbHdgIWTuczdDxKVIyBYA7F3BhnMXdw4L1JCjZK2bAYZaX/oOYqYPLhGv7xVmt811NUCQm+ksRjZ3VmJcwcpQVU5OviaetCs51JfcFSc/RXYK'
        b'p/J04qukQxMfkw2jWIRPAvTwOR52Ftnsdk5H8H96aI7P6NgArU5XLghwTFIe5ZCUs+WcnJNxfdnV9SNmh3/IuMYIp9zb24bdeBEkWBbKkMN9jR7nYZ5HL/Pp5Wl6KaeX'
        b'CnrR0kslcrNleI/zDRTa7G2kwtlFpbOLIGePWmc/TJLX0SbcJPnfjnKV5L3NSOnfI9dRfz67hNQTJMi9jqRUW8e+6VEn+h5/+1PcKn1PIJVSQDakPl7CGJzTrApwIcHU'
        b'6BLqIME0pJ8dkdYr0AeDSB9iF+pDqVBfHWoX6QOYSB8IIn2AU6QPZCJ9wKpAl+dDW/weL9JrnT56CuHoo+8huE6l0Q1CaQVwT1gvkElBItC6HvpHpYZ4RY253tYAuSAs'
        b'az25UX1dpcGkdcgnsSC6xDLGKvBVquk73TnpAJ3Kr0dLVBn+fzrI/591ENdtNpYCSrjjtHF9hy7iti+F+sItRwNeBbK53+Hj6bM7Yd8L/di3uv2eINOa6qnNxsykVpN3'
        b'WXRJPRUaDXVaow+pd+5jvFxBl/Du5+pzxJRCCeOtrK9fSMdL76gV+Xbs0rK0or5yAQAeNHzvzwxNVAfKTE9MspvBKCKAAkebm9vrAetzEE4COVYx02LTGo1sZwDiLK43'
        b'VDl341wXB9rHqoF2AusOBhZZN9fVyfY7FTVa/RFlzc2V8/8CXWuSfom+xu6I8//0rf8L9K2U9MTkzMzElJTUlLSU9PS0JK/6Fv33eCVM4lUJUwjPhsODQZMC+f7ryRXG'
        b'SYP9kI2eFEMupUdpcvLJpnhyvjrHqVB5U6Kewff8U8kGfMVGTZyS8WNBS3LqT4sMVINSRdjSqGRk8tOoc/NBiM3Jw/enPa5R3Epa/fHpbHLeNoEO5yQ+nWgpzC+0n15E'
        b'W59NtkLxLaRZM5Of3BAAygc0CHdulczDB/A+fNwf4XNkV2ABWRvK3Lmq8AOy1ZJL2nPy8Y2hhRp68lGiGEVNEoGMfnYY00jJGTm5bonNJ5tjqLiuzsHnYzg0pEZCLldK'
        b'8NYxrFAMvoK7AskNvLkYpGhylrSrQIHt5FF4iggfVfDs3F5N7jJYCOeZoPRsPHytmJ7Zm2TAW3CrZCm+ncJO7Z0d2CCMqt/Iwpx4JWmXoEhyXETu4GuVDEI3OHqALJrQ'
        b'GVQh558OR0wtJocH4FOB0mjIKEWl+HIZgxveFDo7kC4QrOM2ciM7LxefJWtg1TrINapztuJz0FUe2ZxNda950bLpKQVCc5uKyF7SjZJA/M1BOVGr2HmliXgduZCC8JUs'
        b'hED5Bp13HTsMdQY+Ss8EFOF7c9jhqeQc3mr88ttvv42az5Ap9O+glv8hQiw8hX+h0Y8KoROSYirin4+JRzb6aBCvX4Tv08VpZ0hAmrPjZ1FlNSF3JuBCNmkriVECRmQ7'
        b'jzImh9KU+DpbQakpaD7ZWM4Qbi451a+E7EzJFc0tQxzpQqQL3yZbmSKOj+N7oEfb4VMMCHOi1oEzMrdVElYIXyDbxQg3zfR/Ct/ux87MwtviGu1qLyi9M2LIzhJZkNpF'
        b'xZ1P1qAn+0iD43SC+n1hAr5nyVUV5i/HFL01CQV2RVdJ9khACTtBTjMNf9x83BQnHLyplOJDQ1EgfsCT7lqyjp3h++LEgpifi5uDUIM24s0ov5ixgu8CDOQ43k+6mVHj'
        b'CdykKhYcKwDHSEtCYf6MGHuTrq4L5CA+LSdb8Q0FWzGyBnf7xalz4kHzly4YgrfwCfgmPsMAS07LimFjgHbPmzlyjdzNDJypFNnYgVx7QInsdNTLx9dpRbKDrBHOzd09'
        b'B99x1vSfnIn3ydk8h82M6J3mBnLWPs9gct7w/s71Est4UJf6vGyZv/WJAjIhdEPN4l8vPvDMN9ujcJ8zyuIGv/7BicOK44fqio/aSPq6KWEzSjJV04+8O69z6Su3j/12'
        b'7xcfvP7mb2e+dig4IzIvf9/D7I5n17xz6W8Hcme/bWyPyq+O/LI97dMRi/vk/GvLCvTwl4tPSPauHnjk1JmVv5TbbhpGP2HtHDtIUrKy9oL6b3dKvnhNMXx6unX3exO+'
        b'mDggesfSJ0v//UJo49Vjpw+1Vfn1iE0H8v5nXnfeE7sNtp+/bOl4wfqquViRU3D5He5hzX3N7069ZL5wauaabbY1XS9uPney4Eh1kanjDWnNvyYvy9nzduPwu4qb7w16'
        b'8vcv3tXfXXb12ud9Sx/kTVx54+ANyRvByzOfGpgR85K4+9d/nqC+s3vMrdgP9/wrus/v0rIWa74M/qa+9Bezb4y69c2VtLtLyabKxnXlv03p+PkT73/85F8umU+WhCuD'
        b'mBMH6U4h99x8QfC1UGaVKMJnhXMcj0eVCWaJkMhHfSMEo0QXXiOcz9b6zFzBIQTI7S43mwRp7c8MDslWckLT68iBt+SjkFkiYz+yVzgy9Dw5Rm7GxVJnjgFkbTxC/k/x'
        b'+OT0uYKnSHPMgjg1pfbxgEtP4st4M68ih6ZZKSnCTdEaTV6sFPHzuZXBGUtnWCmCzV+Whc/l5cfz0xqQWMPhK+HkBjvHawrZkAijdHhvSOeNX8GPXhprpb6ScxIm+HLx'
        b'wBdTgiwwWHqa3FS8YZbddwM4zXmPJ4H4+FxmiMEXxxstdF+pzKWUYTG7TxjZKsKXyCXygLmwVE2WCmYWDp/R2M0sjU885pwsZeh/yebizfoSTO0Mveo3s8CUUpHgGfbh'
        b'5Xb7S68Vhp5gLNhgWIqn7iSDITeSkzKnEupgIhxuFg7pYOZyEsCzw876uVk3enu122zkgt1ETy/V9FJDL/TQRbOBXhY4bSnezDV+3+cI5AChzWpnw3pnSwuc/QQ5u+g1'
        b'3BjhUuZmuDkT62q48TW1KomLmEUfhrufkS5p8mtC7Dkp1xTAzC2BTWLnGemSZuk6tFLaGLBC4jSvSJl5RbJK6uuEUNrJEPSoLBcsyHK/r+TRhHl0DBV5ddE6VMrunhgl'
        b'Rv8YyQ4sjn83Ph8x868Fr19uwe2yRXhtiQiJgrlMcq5GYGGnyFHcVoLbS0n7zGfK82eQa0Xk2syg9MREhAb1E+E1w6cy0m7Fh/UlpL00LZFsSgVJCtraaeDIkfDZwtsI'
        b'7uC7ZJe9HWBDC8haSSwHktk6vMdGDVJhw8lN4ST0iFlonLQPG1cRPhNMjpOTPCInKtEoFEXukSbGt/A2sjdEo05MTU7jEe4eKF3F4UPDYph1Ojso1XnguP8k+5HjI8hR'
        b'g/V8vdjyAaUfi/HUwqwCcZL82ns5H3Q/qw6fNGHyTyeeqe182DXfsHWCsW726zf/KMt5PiwT9ekz8vnn9h7sc+XrA198Zhy9MTogZk7Vtk/7y09detBtmjL1+SNr1r32'
        b'02lHYjfP5Eb6/2rzP+T/8pt4Kq7ojz/ZqX8pave+XT39/f+4ueo5/+jgd775nSXx3RFz/lRHRuZ9fjW88d+JV15Z3tPz3tevL8s0D3jL9u5H/Trey5j9/KttD1ZZGt/6'
        b'dMibc+sWH5lROb57xN1//Wy9JCz2PfXF3UtML3WV3W06HZjffWO39W/333sz6Itlqm9aV7wiupi7dP2qL/yOvF70Av93ZTgjlqRlhYEd8++HLFk8PsbNnDCWEcuw7ERG'
        b'RUEmXMsLdBSAdEsg2ZfIqQg7JX0SKBolpkBKw5czd4kFeCfp9EpMA0CwsEiCAnE7s44PwDvoAcAufAiYUA45J6p+2sYKFA8gazQF8SDYbUnAZ8UoGN8n+/ARUTlZnSBw'
        b'h3X4HDTSSp+gpFFxWDyYw8eKJzNLthpvwm29h2GLrBp20DW+jy+y/JI8ssZ5urxwtHwh3iOqX4LvMXe+GtxGrmmoPyQ+UNLrEtkXnxcPIHvIeuGg+02auZpHfB3DF4ji'
        b'8F7cRfYLC9IXr8ZnGTsNjfRwNWTsNHYsm2//iOHUZ9XFZzFkcB1uFz2Nz9QLR51uw/ufduGlwEgz/UTG6j6M0eLD5Hya3XIPstwFcpbxFHwogc2XtC7HZxxn4ZPduFkk'
        b'nIY/DF9hizmkDz7Ye4yvNpCdnelvP6+ZHB5E9lCpjWwupG8E6S6Q4a18/VBy+fvR2//VGfsONxrhRH3Gmqp7WVMCZTzMh5F5MoopW+J5+BbYlByosvARM2YlPDSgKcHv'
        b'UebMd37eEQ8V88F8X54yMFenGmEAApPy62UPPX6C+dnSI7FYtWZrjwjK/VCOJDE30N8mJ+Opd3Ifxnjosa7nOXskEmM8q9EbCh/eP8JA/4tOWHafnK/e97AfCOFVVkds'
        b'h90Oa7SbR8x6q81sYnl1Ci0187tYW76XiVyxUL/MAu00mPUW6uYomHHsdimL0zZvt+l4M20/arY3CsYwOpzKZVa9F7OTGx+Vui6ci7+8jYaOke6FpRgkX1DUW/Blsh1f'
        b'mQ2E8jLcaMHnZuBmCYrCq0XLxU8x3ecpIIzbSAfAUw3CK2lT4xOpwmPRzTbSKTDZ1tkqskujVotQaHokbhGBLrUFr2Ps+f1hfMMWjv6qiK+LkSIbFUmnqYqcFaXDyM5K'
        b'0GRPkGPJCK/Jj02TZC7GJxhTLCN38JZUvNehl1GlbCDuYAyYrKfj72XAuJ00Mw5MjkUIj4BvktuRgtKG7y8FvS2TnK1jzY4DanawRKiWHszjdm4gKBenDeI/hoosa6DA'
        b'X7sS818eGjwpKXT9O3vf7rtUmvOZ+jn/rbJIaaDp7/yr7yxZ2aemtj53cmxDR943f90w4Z1NL21MGfz8HfHkgLNR+QfyJ+fPD5Gpuj6yGt5teOKde3/V93//2m7lldGa'
        b'lLW7vg169freGd11A/71u3//j6z4lzflS/78l9cOhzStWPRW4hMPri4Y8eH5V+0vR9DgDUsfcfQbjtuEZ6NFlQIBvUt24tv4IhBSl6OAh5NjIoFXHiY3zHHqfB7lL+Lx'
        b'GU4zFK9nlHOgIRq3KsoShNdk8ChQz5MjxficcAD1bXwrwtPfm2weYXcebFlhf92JhByx86NYGEmb820nm/BWpfQ7qIcPz0OtpZzuN0Yyh/WSTKNYFC7I5/BNCSB9wir/'
        b't1QSybtQEXvlgu90SzTD5Y+PkKZDPhwT7Y12cj3iBq211vfx6GOR/Rhq+ryRvjxB6jwiXfzYI9JFzLFX/I6I8/KssZdaUcJh0S6mv4xGV7r1/aPR6ATGKnKqFbH0V6wC'
        b'iK5FsGpTiqRfSoNcqZE3Vt1oaIiNZx3ZSaPZu43YQg/y0zkt01pzVa1hsV6tKKSG9CUGi95J/lgbbAKsuFZRXW8Ekv8dtIyCyxn156RlMuEdEuQGuTEzLhs2R1E2SB+5'
        b'+Xm4szQbX8nG50lzvBqEgmyy0a8hjdy20bDYyKfJVQ3spdx8NWkB+ayUxsokjCLrZ4AAooqhB7loyHU/vAufGMR8UVasqicd+BzZlEwuQAMiI4fXVvVhAn4gPkSOxQWt'
        b'AugvRUvDcxi1HCFBcYU82UZaEVeMQPK7Qa4ZXrfOlVjOQO7LfRc+kT8mGCeGHpifNeHmlG27p7zrt2J10YSwsZrsyGwu987Qny3O3lH68eF3M8Pffmv4BwEjL2/7yxsd'
        b'gz7/x7Do1I5rZW09u66HjdzdPbc2LEwxa3TYWNuoW0+/trF77e/En/38qR8F/+ns+88+t/S117oztvnP3/+bcWsbFn72auWcZ1a89qp5wvpn7gx+E4+5Ef7xmCtxjavq'
        b'134+69eGpPe3/KZyi3S0tbxJ9NJPQ15bnjE7YLIyhMnTVeTMeLq214Kp1CfO4PAFEKM3CsJVy6zhNOpmMFltf1GajLTyK4fgPQJluEq2rSDd5OoSu3nFH5/myd0J+Di5'
        b'voyZEgyFcbQ+AIMn7ZVIWsAPxJ0jmUxZQ7bgI/SlcPHqHJqPAsklfoic3NWRs4x4iaJLNPF4c6HwIoDACfw0C0i39wXbDV5NDkpp7YRCFQ+MbSOSruJj8U58TRjZnmi8'
        b'jYq/l4HyKdVkSzydXEiiqAYfXS6oCttK8VYHNcW3yTpGUYtwq12qbCiNi3oqgWyKz1GplTwQvMMivEFPrrFpJZCr+AKTrhMKJOJGJB3H93tmpuCm0oEvkisaipkg1B5i'
        b'2OkfyeOjZUbWMrcQVgc0FGFNbmLodxIfhdfgO2zSEWSLSRCFx4aRNrsgPBfvEN4ZdWEVORfHBiUJWQGc8gwPC4QPPs408x302YUmi+medXdwoR9/wbgiY1E5cpBQHcaS'
        b'ULjbGOSkn7S2QJE77S8JsCI384fvQXbyQtneE+MXw+XbRwj3ur5uLw1w61hpj4GeimjQvDOwGAiI/Z9SInzx8BfxyOlR1A9eV19VXs6Ce3pkDeb6Br3Zuuz7BBZRx3fm'
        b'M8PsL0wWZlyHzUCQxyP/68axx8LRTB+ivEfBuB2xkwHEARyP4POtmEcOufvbyJE8qBj8N1LRD/wWB4vkQnuPtgmt9k2Qc1Lkktv7tplvB87onxE8QMYJforbxuFjlhzY'
        b'XJbgYBFIcU8HDeLJURFezR5PGTP7BuIzVkpzAunTkyL6yGRgMgip18TDybkp/1+80cjzaaOf8JwJdw8fScNWGvsNRUPJSXxOOPr/ED5BLioiNGp8KTENqpPr3KKFpJM9'
        b'eCCbJ5HtcbmqBKnbC+WSx9ko/snITgVe60dac+KpDJYiRjLcyucCeXlgeKFlGWehWK2sHvlxxbxn3959aevRjqQNi7gqv/f4UxvkgdFZE+M/iDwV+cGGvIp0TUDgnB1H'
        b'Xzi1LmnD0XVHd+Zs50ZEsLdRLJgQNnf435US4Z0SZ3Eb2fpEjCNOkQUpho9ieRNXxDhU8SJ82E6AlhoEmtmEO4PxNXy+1/BNrd4RMpabMgp3iUt6VXGmh+N15DzL1ZFj'
        b'+DzeBaSRApTlz+f1ZG/I4wJU5KBbgUSjL6f+CYw0UerrJE0jqPWWkiIxXM3LnTtO3COmFXqk9ogxj3co0bPfzCucO4bWHMo7Wl9t/7zjKiiyx68pgwfFxeSqsuNzcXuC'
        b'8FxVQXaRDWSvJBKvXuaBQn3s35bPXE/TiKMnSgB+8jrRev8ykV7M3jOH6Bvm2vkyCaRlLO3P0lJIB7B0IEv7QVrO0kEsLYN0MEuHsLQ/pENZOoylA6A3P+gtXBdB31Gn'
        b'i4e9wen66PpC33J7Xj9dFD09Q6dief11AyAvWKeGXCmLjxHrBuoGwT165gXXJIYaQ3QKetLFjoAd/A5RtWiHeIeEfnTR1Tzco98i57dwV7iKhRIuV/Gjv3VDD4RAWwG9'
        b'7TxaRzfM895/dtUNPxChG3GALwvTh+vDdCOj0ZGIo2gdx1KjHClWIpI5GwqRQzJYEz/7+R59mBuiH1sniU6pi4V7fXXRzK0wsce/HNiUdhqIxSyi28PW7q5UCA6NUvYW'
        b'QanTwi75Tgt7zfcLQgsQLOwri8Vo4LAwaks33hs4W3jAPWxJGzqQl8ajogr155JRws3dlhXch+P/IUGJ2uVvaMcJb2CdgE+TM67vCs12UyCBcLT6oZIaWcRToVH4mhBj'
        b'v3A4ulu1BX5VVH4TOhb9yTFGFrxnuPXWcDF7Ga55Y79Bbc8FrU6Uiw6mnkzk5/7tk8HyZ0eHZ/+7z6gjkwLmdnx2q/ujOyN/Om3UgPg5xie2jU5t1BbFZvbL6Nf520G5'
        b'Z/5ZuXNaRvSKQW19+g85tDziz21P+g06kPP678qn/3jTwy/RmcPRZX/5RukvCHib8Qka00zfuaMSAa3aXljKW8k9fF3Ivo5P4X24FV/MI03kaD6Ip9LRfBi5l2ylVhEo'
        b'd5tscok3B+J2xfF4EW8D8ZiKUPgoPsPcnh9ZoPiJdIlGRktqcTe5wky6pXhLCgsNb4uLYe8t1uAzy2mpfgPF44xktdBryxPkqDBk3M6s1214+2T6+G6/CB+NwpuFYO9z'
        b'+NaTvaXycVckyCxhZKcIBM9t5CSTjzmoDNNLAAE2h75iWRYMwuomHq8ne/BGK9W58EW8hfa2JCdzUnwOY8XQHt5SCJNtKSSb1VI0RiPFu3T9BJr7veXM3gDwwa60PFnK'
        b'BUhkXBQLBLebTbnGcOf+eeTtiYKRs0fCPJN6xNSxtUfe+1DLVN/jbzA12Kzs6K1eGdTVUVxiXkt/r6aXdcghfq5xG2eCB1d43U0K9TK+HxLfKymnA/cZ3zqRt28R136c'
        b'Yd4De88N9YhyVZs1lNx8n6HUCkMJKnddPZ9DmuIY0leDXbr3jPBW/7Dg8l5Y+ep4urPjQTmOwg6fyh/crzOim6JPeZ3Bd4hzrrPbvlThUFSb6+t+eH817v1pl/rsL9/Z'
        b'XyTrj3rc/oezk5Zb661ao8+uipxdRZfSgg7PXJ/9/e+jpb2+LJJHni8IZGwjaZwIpCCqa1XIl01XCzzp50OkqKgIaLSiIs82rAgZjkScFVmoxTsl8ODHFS9XZmt36GI+'
        b'0GjnzZZXf1jxIfpsf3TJnh9Fr43OnIsqXpf6nVml5KzUTETO4JYUSuBcyRvZTrofJXEG0vYYIZWpgIyesbebOejZLCqVNoa50ofvH0pd4kF2LrpZLT2bffgt/Psvq0Ve'
        b'Y9s91SI7tP45TkxjNDLf5Vcbf5O9VM6Wwy/mFdoCl70XcTKrITCoTWKh5+Dc18dSWB2+/WHFVt2cZ/fgPfjq1k7Ryze07GWLLyO04L503ZnJSp4xo/LAqEcB5QIkskPD'
        b'4EQO4xZmJ8kKXkVNQ7EqspocVlMtZS2fgm8lP07VCClnnsWGRn15pbG+amHvq/AcEJ3XGO2y7O6l3V7cKmEusZ5aB9XHXWwc2+AyxwPQZ90A7btHt53pgDVFK8eLXEUA'
        b'bdEPgLbH3uSQ98dLDNo/yvyC+0SEsr+YWzFkVWQgYnbRupG4E58Tg4B4CXgWaiTr8W7BJ29rf/IAn+PL8VmElqPl+ChZI5yH1AZg24DvPOEmUNJXgsYUqDiUilukwXgN'
        b'OcQ8M4+lM8/MOQ/zKox9pz6NmJfhK0EFprclDi/DK5aVyEYtP+OgVqvjhCR7/KTgZ2hHGxfvQnJqCshqZG8A2RcQzyii4C14jU8AnTxuoJtWvohcNpy6nyKytECR5JG/'
        b'HPmzrGCcGCWqyNoyqd+sX2YlzqrU/lH6cvyHu7e+8MsT4sDK3H63pxwYdkvp/3b8bw8faPjxv+8ohg0c1RF1ufjDvMypuuZYedX62tP/zix5+aWQiI5G5eXJb5veba7+'
        b'+k7aG0sK/vl8l/6L8nPGgObqKztXvrPrx2XyzzOWvNbv0NFFz+nEGf94dcjvtwxrffuU0o/ZVCfg4zGggJOd+IK71ZNcn8nkvlWkI8cutvYnW12d4gLwOSvzFj0NlR7d'
        b'bME5j9JEED8Ps6dIhaQVXw6MtUu3+bYCfMDe7BDcLSYXh+OrbAv7g8x8CsTS4XHslZUU0rgL9GhHw1KUiM9KB4IwyswFKty1UhM/lly0Ow0IDgPnyCbB+nuEnJ4BE11K'
        b'PSxcjA07Biidb832aeeUli8xG+zvPHUTQcup0xjPDQYRtL/dmUzONYa6bEFW0f0lzVpzjcWHgMmbd7jv+A64zPPY8afc3ofp0V1BldhlU7o987W/qJdFwTlf1CtmT6Ek'
        b'sNfFzr0uYXtdvEryOIOXxGOvSwWD13R8fQnuEM2Kom5bQxT4FNNlBYem7UpyLG6GapYKXyiZJ0Z+YfxgE75k+CBrsthCT5Nc8IqYmq224t8899Zzl7be6ri17tac+A3K'
        b'PUM33FrXuW5Me8/lnLahe9Z0S1DXWNky8xfAnKkl16AgN0E/ycGnRPh8DAYMYf4fHBpQK8bNeD+55gDD443a0nIWF8GAHeoKbGMwc7twW29WVDBhS1187NgrlpnJyJ2k'
        b'd4qFu4+UZKDeSefgAeq94b5Azbr2DelxiLnioSYpMzZQePv9b+HtaSCQFAiQpWPW4rYlJRSuu6LweQ6JyB0uH/UzvBqYx7FTOT/qM/7jCo32haxvPoh5N0fLZK2KjysM'
        b'1bG7Pq54WLGw+hPdxxX8psT0FNuVk4m2S4svnUxqSaIv6RYha7H8y3/8vVcm/V5+KG6v1abmPRfIRrpC1iwTXG2oP2cflyXurSM0tcs3/ux2wnEPXOo94NgR5QpH7508'
        b'pBYN3xDNFPauxL57JT8Aml6laM/d64Am3acGfDYfoEl2pmSLZicgiR+H12rIecNPM4N4Cz2a4O1n0j+uyNG9rH3BDs5s7UcVau2HFZ8ASD+pCNXWVudVhVfRF2GL0Olv'
        b'/b7UTYKdStc9hdyR2n2d0/F9LoOcxM3f/8W6PcHl9kNGXcDpJkg3UnA2RrmssVsFh/XBfRP2SKu1VdZ6sw/KLDbv97Vxafj+Eg+At0a6AtznYJQhgs9urwsv9d7tCepV'
        b'rRfql/UELa63VdXqzaxKknsyuSewip7coqcvR01yTST3yHQGi3DkCvUEpu+Gt9ITefU2KyiU9PRYui975PqlVbVaerYp3FLK2HMwMzUvmrPoxcvZv/SJWBlrkXouJfUE'
        b'OI5WMehc4tHnshJWg9Wo75HRl2vQwj2B9JcjzpvdZmc3sZaSzcdoHT8aclhZv5QFo/dIGmrrTfoeUbV2aY9EX6c1GHvEBqjXI6o0VCn5Hr+JkycXziwo7RFPLiyear5C'
        b'u+5Gj9gyKBApZOnTEwsNk7GfDixlzspck6xa9gMkXw/zqcjetPt+qhIk35dyVnJf8onZkkTt8g8T6gVqqSfrqy3kOm7KCgE04skpLhaffEp41NU1kGyzWBeT6yHkWiCH'
        b'/Mg+PjU9uByfFg78OGHGIDu1a4DNZeerc/JnkOYCfD6ebEnInZGNW1PjcxNAfAX5yhE6RDrmyierSRMLbxq+CHhhxwzo5mQqiNz5+L6c+UXhU+RohpnsTqFezdxo+lj6'
        b'5gBWQ4LXzkrhETlA1qEUlII3k22shhR3DCFbzVCBR1wMwjvIVbyJPdpK6jvEeSAJhwLL+BA9uRAJA6Ce5pYZ4RWzoJIUcUp6ZObxFDZrckSeand/FSNyleyRkMsc6UjD'
        b'zWwRrYPjUCn6chUXWjFMvDJSWETcSi6vxDdGQGsc4mIRSJnXyG4bldHKyc35GrVKja/jkzS+Ll9FNuVxqB8+IZ5QPJM1SYYPRRPQH4ZKGyrmxUUOEppciNdOxd1kFzQp'
        b'Qlw8wntAwd8ujHAzuV8dRw8ZyRFEyCRVCG4XVfZdwZp7Vd0XxaMPp4sUFSvGlw0SFBzcno+3jVBAa36IUyG8dwzZJchBq9MjQRLFh2LYe4LE8Ry+jU/nsZai0Xi0Am0d'
        b'Kk2sCK/NjRJamkuuqCLI/pRUDKoSp0Z434on2IifnMLFPU29rfJB//FP4kEz3k/WsoYiGjVoB5ozA4VWLMgLG44YOGepyemYYtoOwDkB4f3Zo9mIxuBzkwWHMpja0xIp'
        b'3sgPD8Z7WEMGFi85J002ocK4LMIqeNOTjuoxmfhBSipIlXSldpJuvJEtvmEa3qShx6+0ks0a5v6F9+LVwXi9aPwS+2G34UBmGlBzrbiiwtwTN1JYfHIN7xpE1pB90CbP'
        b'Jrk7mrSxB7xPLx0BLe5NoY0W9OJWf7xDjDcVk6PCiLaZp0STJqgtZVPbA5rNVgF2ncOmCiMqEGBX7h/cIMrEd1ay0WwOC0cj0M1JclQxbuDkOXbsOj8HMGfjqpRkiqsw'
        b'wV34MLnH1sqEzw20IyuPhhZKyBWO7IheJGykTnJk6HSyJyUtEdYlGaqV4i0MhCWJeEechnrscaiyUmrgoweqWZVVg2LIBtKckkFrZNKos6N4B3vSa5q7yo5xm/BFhOTj'
        b'RGQ3vhYKiLNe0JPPk46GMHIVqsKCjQWs6BMgBCKsicK7NMIyKanHuTxUhLtj+5AbuIVNuSFVhkLRzeiQior4f09R2tH1tv/oVD4lIxWxxvaCCnZIUG27ySXq+t5MQwk1'
        b'EqRcIK3iB5D1RrYcOryRdOBD5BLUBKTKgmGQ42QDQ7cnyBHcMaKfRoO7EOLruQnliayraTorOYtPQg0Y+DhAQ3xkBOsKIHhbQwlYG33OgC/jJmkE70/2zmfD3tjQiP6B'
        b'Pgz1D63oO7A2VcBEfHIc7kpfjrsTUyWIm0Tdx3fXMBhOD/cHPaAvOwxIBDLpfQ7vl05hLf0lYjpqQ4mj/RUVsUtks4TNEYMPG/sH0YZg908GtTH2CWFhjhYkkC2rNEBE'
        b'QG55mkuYT/ayVq7FRqNE9Kw4uKJiRensqcJ4luHd+L4mB98pjgdUE4s5fHhyrdDOerIDd1G/2Rm4HamRGu8vZ963c8i1ahalUJwN2q1qFvNAA8qeH099poDg0Ln4DYgI'
        b'Y2hRC2DswMcqnbGkoO+SPTzeOfTJ3oOgv8kQAd8rKg5BFXkP/OcIExy7CobQIYUJZQG1igcAH7GxR0+r8RV8UVODWx959gSsRYxG4rMS21x8XyBdp0lbHWmdQUNggFTf'
        b'l4jDufmGTEb58XFysZSsI5s0paQdUIHspSEWt0fYqBQBYOkmXRp8XOeIiHbu45GFEoMfkEaqPfZNm0z2B6KcRITvw/+0AULlq/kL4vB2+iQxIZ9szlblCgpekhiNKpUk'
        b'p+NtwrNKWJ9U9OGE4NCKFe/Kwu07+RjZBei53w+Rw6UIP4D/fqRLcFfePwqvjpMXP9oqj0bNlKRQnKQADSfHBuCWRM0M4KYs3vZePGwM5hmxC7eTrpJ8hWEGjdrgl3MD'
        b'yXF8W+h2C97YKBqsmSksxUlga6WwhnQ2ZGc4vuQfLoSbu6zDENwqJtdh6e8waM0eRa6Q/UFoHvDju/B/JDnD/Ao4vBXfpuzjqBRoQwFUzVEli9EAvE9snEyuC5ti31N4'
        b'C9kvAsWsGeF78H853s7OpKpunEnr7iBXeivzUHm/uG7qINYv2YCvDiKt8OMg2YQMyDA6WXg7yC6gqWeoq6RzxOQGOR0SIVpAtuPDjL9nkQ4QBDpEaB6+RdX/WUmMgMfh'
        b'teWUfpwvpId0AWrZ/SEG4mtismnS08KKXcBt08h+4Be3yXmE78B/cnMEw4pw3IXXklYeVfVBC9HCZRMEMreBKhMqVQ7uismlmy1i8ugJIrIDyFGnQCDv423kGNkvRyFj'
        b'AIfgv87MtlDlSLzDNf4EdwTTWE5ykZximCzHN0kLvoFXW4KCgELBBiTn8TV8WuCH0wJRJNojE4VW5P0rIhSxiS/Bu4eSVhHCa2NRPaoHCY+BOh5kkmZY0M0gsGXTIPQ2'
        b'TaGKjVUxQEwuBeEDzCxp4kZyP4e9q1hiWhHVb3bVywJFJtdG4rv4HOyz6+OZhfQ6OWBIVf1NYvkXyLc3n985/7UXTRETQ6V/+OjQjxeFvxkR0dZ08NJfs9aMiOK1v/f/'
        b'V3XwyK3GyKd2bXkvsG/x4a0/jsh7wIeQ4X8b+HXJX9qmDYy/c7/zgnL2bv+sH50996+Zv7rXfG9o0A7/4jrDibzffBq+qTNn8s4zqxb+ofvVif1HvHRWeuiZ2f6X//LR'
        b'5Y++Tdf2f7fk3a2aWT+9qDye/+z7UXsLToW9+qMfdf+q4+bajPxFb8ReGNMy5QOFbfTcKR8MnXswdcr1ifsKKrf9eeuggsWbPln7yeIr03X1Rz8bv03ywqrRflOCJ6Vn'
        b'jRthvvnzd8K2Hd8w9vkpmycXZI5Rms8W/enqC3vXHugzxm/MX/+49oWpL4wc3Tps99DZXTV/6tP+xk+GvKfdpEna+1rM/q/LJ/9kdw7Zc/Obyc/v2LXst2e3fZOz9+LP'
        b'/2ioSftn/4yxr3/+k9uF6556+kVTaPHEt6xpYTb/T3H1WxeePbv15LjjPZ+HXXw/eua69nfO/faJkO7lwbd2Sr+8MHLfxZxr9XfH/epe0P1DtcZJ/3N41vm1W/650Xp/'
        b'38E6RfcXrXNXlBjrKs9EfKoaYxlguTm8o+XLCy/ca/nbv3MSHg588oX0jiG5G6ZvCNgy8tucVb8Oe7LPsl2a9sOtXW++eH3a15Pe3f3PD6Z+/dGDujOfLtyW8c+9N8If'
        b'vPfFrL/77f77jE8iCq794uM/XQy7snNS+XjbRy1Pj8j/89jXx+588LUoNuTfdYMilBHMmlqXnIRbF5Njj7oMOBwGVpFtTOkGcoUP1mXGUSM5j/dx+fiolnmmSucaqVC0'
        b'qwhUCCkST+HwPZBYhdDfO/oU3Boy8skGuRm2dHvI4iB/KYrEh0X1sBd2sVgEI15HbgTizvhsR8R0GFk/nNwW4fN4f5Xg4NoKFOEc9REbhA9SjwW7jxg5kMwst0Msc/F1'
        b'5lwgOKoCKzvO49a0GYILWTe5Arsyh4XhCRY9WT6vix0vBDJcGUYOk4uDYEvBvBZzE3HXQiG+rKOOnHJ6nZHDeCvzPBu8wkppY8KS4cBsF8ymbhosIJAcwzdZTsGSCcyJ'
        b'g+bwtdSFA9+ezyzhWeQgPsxM4aSz1v3MuiXjmAkSn4FJX3L3txChMHxqHPO3IF39mL/FULJmkJu7BYIyh8kmweFio4Ydp0dO4U2klXp40GcRVHmhjs2wAOeXsTWIGyPB'
        b'12vKWb/kDrlkhOXD58pzvNg+yaEyBocBpTLXIEGyYY4QlHGZnBdcWLamDYmd4+rjwRw88OYGb2fg/2A30x6RVidYa5bCxWmteQapw7m+nJgLZ255NMQ6FP7sHz6c8/jQ'
        b'ex/JBoVyI2g4NhcFdeifnJPx/TkFF8zqUK9jWjaUlQ/lIiHFfyLr2xjUa4qB8bia5s3U1PZDY914oVavyf4qXM5ScxBlIk5z0Gr0m/5uzshuo/D90JwZ/YQ3QaEmidPo'
        b'xzEjxQ98dE47UaBHjRSjBSNFZySP/qiiHiwVea+WpSLBEkjZGjk0KgzTQK/BeKcGDR6PLzB+PHRVIaaPJ6LJzTkoegE+JxRu8p+TAm0n15ANKBk3kROs9U8l/ugFxUho'
        b'vCI+X9ofsadzJB6WefQoelP+zPy5gtCas2AlVzvtf5gH2bnCUXYmeHHO2JRUMW7tS9/KgapA5rjKgi3mS5NSUqVjxtOzOJDeL501sVbih9aPGEAf+MdXpA8U2vXjwtDA'
        b'2RNB76kwVg1KEEbw6YIwJBvBbubtN1YLJTtL5Eg+A3Taoor4rZyfUPKKWo4OLEumN43qMRah5PsxgShvZCwC9ToPN9QIJQvDAkGbV9Kb8qey0oWbnU9JUVFsFBvS2yVj'
        b'hNNFFaH9S/JnDCgk7TOpjC1ZTE0AN8llJoFxKaQlJZGaYnDLxBEIb6+QsD6PBQ9HvxnQSuE0af/AckGoJ6vJhWFUSECNyfgoasS7GplwmgIN3if7A+grUfABfBm+yFrS'
        b'IejKR4FUHSX7pZB5Ax/JgKshT2jtgpjcJR2ALqono5CKnpnKup7Mi9EcNXMDjN+jSLQ/8zy0shLI+076kYAmDpLSRoSvLY9g8JlHWjSYtjQoQYQG6ZcyyWsEaRvDXJeb'
        b'YHCu7sunFUwIlOLteGuJigplnAmo6DYuvBqvEZCO3OgXRyNrYMg30dJJOsG/enfOOHwOfiwju6PQspQYQdVanYs34HOwFZcTUG7Qcnwmiz2rZRBpni1Bl4L60cnkPZ8w'
        b'WTAhr/60kjkfkDTEHZlv2B+yWWRJhdH/KKGmblsWPatlY83i9+4eaPq7OfGdIL8Jv/z5UPXWuK+LR5y+PG+yfuitl8MWL/8RFxN2ujmTeze07dcFl0J/9srXv//L3cXm'
        b'V2w/+cO1XNGZke+PHTW8/0sxtal/8P/FIrK0tmxa4D+6jr07M+LP1wr++oucwT//2c7lb2y5ufaw8vWN9b99uHnK5yPOPtjy2qLZv5nwm0uV7cNm/2SS6Ojx/p//n+au'
        b'A66pq+3f3ISwEZCloERFZQUZbqSIBRVZCrgHBhIgGFaGihsEBQcqouJAxT1RwC3a9py39e3b6qu+Xaa71i5fba22tXb4nXETkpAg2n6/7zNykrvOee659z7nee55/s+/'
        b'x6YZXk8PPwmZ9e9HYU07Fo289+uk1pjXo+f8bv+fL6erb91xLr2b+p1tr7d3bBu2//Znk/t8JPugaMHaX1ds9PZ59eUvn/znwdgl1UVTHv0cDdkxNpPt38pek/XWpKZE'
        b'Sb/Zb+3PqTo86U7SB279ldfKVzR7uj4pSzv8x6qWsqnuqe5Rr5dEdQlJDCv96KXzUWXfj1t4vsVl67DGj+bGfnyzj/hwyxPed4OW5+T5BnipsV87GZxlLEdiiGPo5HAe'
        b'aKDA7n1geQyZ2R8D1ieLA/EYdJoFm8EeNzKqJymEulhzvgi5B8SOQIPuMWLKFCT3xePq2CE0QjOdVYPDcCsxZSLBEQZUeeLxNAm7njiJMca3x/BBIzy0gFQ+ujgEZ4rC'
        b'sPUqHiNMAOeWsL1hDdxOEsmAYwXoaWoXmonsLFguJqaWHLxCofxHQR2ox5IE8XOcGD5s5IHd0aCamjMrkA3USINNSKBJYxGONVFmEhsjF661bWMuwm8swcYExmOKwNsX'
        b'VlFSog2wdSA4ADcZEBORF0quffng2Lg+VIIWcNhdb8YIYYsCh6Kum05qGANqenuDLe3MFGKjRCNzEYsZPiyI2ApgfV5bTgF+YQ93YvTFgBrF4mmmNgyxX6bAdVTOFljG'
        b'whOgFtkTY4NDQvDbaSQkPMwn2uIyNTBP2WI+IsMoVtSf/EkkiNWNos3ycTobtEd1ghVc5sUIWB7YGQXO0s5semkihg94Ia+0bVJ/CqhXi/HWg0jDUboj0/gBpN4MYwic'
        b'wCVSX+9IdAMiMzTP09AQBavS1Tj0BOyANS+bsciQoYVstYPUJMuDh0hV6bzRxJIC5+YYGlO8MBqOcAAsg5uCAkNcYQVFVJBMQamwTBeO0KmpMAEOvCMmVa6xSaV04AlY'
        b'XboAN2JQuaGPB/p4oQ9ediKpA9zIHq7cH/ncEfqwXwp74Cw4Dqwdz40RPLXh49lRB9aGALsWOLUZL1gAgwC1DqRui1c7jYr7ZiykWqMpM5NGUL9giwR9rSdfyeS/cite'
        b'8DSBZ5FAXCVmK6PBuSRqFwfsam104Zu6X3hOiQY9ElwWjrAiQRdkOp7M5ZL5Pa1DxviY1JikjPSp4+PStHyVTK0VYDS/1p7bkBaXnkZsP3J61Kz865kilEtQEczqoFl8'
        b'Z5fnBl9ZOQmcHJ2EbjbO1rr8EEISqSI0/jwQuOJtuvWs6Xbd557gvjDQief0p9DKK5a+g1nj60JUfCCo5bS8FeOczp/mDc+2m3XWca6QHGhGfLGC2i6ET7WL7lvK6n/x'
        b'11pL/ZAVjFETXbIFUmupjZ491lZqR7AuDhx7rCNZdiLLmD22C1l2Jss2hF3WjrDLOnDssV3JshtZtiPssnaEXdaBY4/1JMteZNmhVpDNYKmk3XawtUKMZslzlHbvxux2'
        b'wrgPbtlbt+yJ/raw1TxpXw7+bU3yItmv7LLSOduWcNASZli0zZbwvAoITsZmmjPuDWmvtbyV1Pp3WOmIbP/e0j6EA9ZF6kMmIftxHLAJyXFPNhuhpdN13KRoEyWAFflj'
        b'Ig/MzyQpkOJ7X25KIWm0EJiOQdscJRP6VZipKlRg9miMNcdJeCkZJk4CLCtS0zzUBHhukhtZiSOOAqy1thy3GKbj4X6S2WAbmhcUE/NIs+dq+XMK0Lp8mVSuyUfrbIqQ'
        b'5PMKlVJlGwutWfpX4wxUujTftshrsuMmee31Gag6QwCLQfcPOk0Aizv5hQlgn83/2o7r1Sze/gX5Xw0uhl4OnCi8AynQZksyFIgkiqJcidicKMNEWbmoySySjrtjOtqO'
        b'2WjNMM8+R488k40W3Yc0c3Hs6EkihSQTU56jn4bJoANCTNIsUxo1s1IYi0761j/coCvMCM8Jgp6FZ3DhWuK9NZ+QwRIXbid5b81W2saF+xd4b3XPO+12uiSSS7kLFvGs'
        b'C6ZTEly6am5JpJTlyFWoh5FyQjqM3E7BIg132TQFOG30C9HLdqEvTJYvIPSyQ0M9MmLGjvakQcResHYWjiE+rrbIMIvsRiMK2IqRDs6z6fsE1VR3BhmaotBZPXns/CLK'
        b'WAt2ZmbQsGSwssBSlYR3xbDWXUUOcB88MZzUG9PdATPW+odmn8vOyBzCaKLQyogw5D50QFgLLoJlQSS42oAP9hyotAcNHqn0VcQ4QjTrHDp3QtGyMBFD8h3DpqgR7auF'
        b'K+A2VHV8UJphbcvgOluwCe5RkupshXhCmgkNFTbKlUle9Oxh1UTYbE5MWEn8uOhuxJMzEfKMPdgLj3OxCxNZPFfD2ITOXTAnSNOX0eCoJrA/Q2muWn/iq+xEHxpN01br'
        b'BXDUHp1IS5Y8MXcmT7UGVcJqlonfvujChjnETXhzqbg2ptejk1br/WefGbNlTQObuDt8N29cQ7+dg5wGff3Srcw3D6lyNtpPDbtVHPDpzT8ezXas36WAZd4Fa09GBJ9f'
        b'u7jut2+SYjfe8N/2RdKig11ea1m4YvJj+08+ijj2+ODw6IkDig/v/n3PjFbFwzTVlWldfvD9fegi737jgt78qYvV6qFZj9BYThzoyK7Jxv4jAzeHYv8xKpwyr6wfBk8Z'
        b'094iT+0AeYvtG0JAg3lwebhhHcglSyEeoC+sE8ATbBDNBdSIvPJGzgkFVaaOKNgLDtMMFKdA5RwD2Pg8azYC7ARNZKMrqB1O/GRwYSGfc5ThalBHPCgrWI7xlsT1s4PN'
        b'VtT1A+tKiH/ZExyHW6k7D870MfXoV0YTd3rRSE/ifoJXYLOxCwoudFdjbOpE0KqmryfEsAWeUZHXE2gpkbwGKAU18WIhkwTKrUG9FNT/bWa9HtGIoRcGfttSZhQhsuUJ'
        b'20htKcEtyUKqX9LxxiLLwwLF7Su4eBUXr+EC4ALi4h+4eJ1hnk0LY9OZShyNzikAqUsV9sMM3LplzC2j3G7tJX8ejJpdht5usohTm4ikoCjItrYMuG7xqg64bjsPhMzW'
        b'UY8aGFEWhZqiE+pJTxMJiEnwYqynthk6g8liu9P17frSdv8axy4H/hRkIDPJYpuz9G160zYNTKkXo9IVZCBryGJ7En17/m32ksQUbfr8PL65ul7WWSgWJZDqJeiOX1sY'
        b'GDEv3Kbe97HUZo5Rm6iX9aaPQZsBLIUqk3cg+tjY5Cy+gSg4zBw/vSQ4djQqyGwTzuXAch6rHcni65DtoA86t+ow6FxHkmTl2mmSJBnmg+wsRxLZ+XkokgwpkdpViSmS'
        b'9HjiwGBRoCGwGS0TrDTayZDghZi0VAzMm9F5t0/f0HBRWmE+dh6ol42zq3HoZElmoUbNMQ+pkJlqqW/wP8zyIcNdIpVnEw4YNWeGG58U198kYyTqthwud5wZCxj/i9dz'
        b'Fkk68ujCBhv4MSJ/HTGKZY/GsF+ptd7uIRX5x2QqZVm5BZiThXPvSAY5s4K23QcqlTyngNwKlPmkHf2WSiQ3PCs58nRyLNCr6DyYMHKRBw/TOzK4pbCAYPxeREfZi/fQ'
        b'c/ZmWfK9yF0pJ8djFijcd0OHdZ5FKtv4hPBZy2Wqv48Dyh9zHhG2pgBRYGA+9q7R6ZQEBr4wK5TInzBAiSmR0vNU3QEDVKeOf14+JpEFHilLfEwhnRPDCLHRISuTv56V'
        b'KSxAND0s3DKrkiHqg7uMGhk9HXkBEZSwqccmJU2dis/MXAZZ/K9IUpJP8s/KlHiICiaUa3qn2ECg8I4F6pAqyvgVCX1aBuieFLNiUUPIkGAKNR8RapkrzBAjo3thZPCY'
        b'oLXoiSxQyalQhdnmqbekeejOIP2BDyBJeCXz8e9Osg7hfzFGlajIuzJ5Vq5aTqilVG3EZ+2fWYt1ikVhmLxZpkHKVV8BuoPlIq6LkIbKR09c3ERxukSdKcPvH80TYYlF'
        b'6Hah6UIVmvw5slzz/S8WRZjsRlqTaLIXaNQyNHLgRMyiSYVKFRHKQh0Dh4tiNNm5skwNfvTQATEadSEe3+ZYOGDQcFF8gVQ+V45uZoUCHUDp2VQmZ27h6MHmRH7+Dhpi'
        b'rhq5gVj5zyfWUHP1PV+/DCMd2db1z+h5syvT6Z2MXxSayP3cd6Lh6Wcr0dn4477VyyTJXKDJCbB8+xkeLhrS1/INaLRj2DBLe6LbrGBAe+ZLunGQaTWDLVUzuKNq0E2h'
        b'P78O6hhquJvFUxtmVJmZ87I4oHEYPqThuF/EHkA2KdKtOlXun0bHWIsDdhtEEJOvo6GQLiEbxz8BLcoK0B+6zUV4DBraAX+7HlxoXE24STXhHVZDcIhG9ID+hBMwFo83'
        b'gywepsct0kPjJhJNjVeI/NFDzt3i6LJb7gaNEtMkYgJ67lewyMC2i5uYKvKfDPflKtFDimQZaFkUA8hkW2X61ZxQuqpUczRKVXuhOjL3LJmXxJTsvOWnN9FijN75d86G'
        b'IeDO4aJk/CWaHh46s/OHhdPDwslhlq+GDjXKmZDcMnabO7oPCKQUHYK/0I7t97OsxcbKlMqCAaOVEg0qFCEDRsuRdWdZa5HdLesqXI9l/YQbsKygOmoZaaW4XGSEId1v'
        b'WTUR2ZDNJjUvhqXOQ1asTKbGlgX+RgbW4A7tu8zC+cNFeOoY2U/Z2GpFK1CfW76o+CCM6KVHSRQivNDhEVlyNX4gUdmhuUeBzHhP+oNUHIztdHFE2ODB6E6zLBNGECOB'
        b'8FeHd2S2BJ3taKRUOtqJYJDRFcJfoumDLe/IqTkdA2oHd7QOHT1cNAr9opbw9PAhHe6vf7TJIcZzeh32tw5zzR1Jr49lZY2x1shEGxWTjC6PZY2YKc9CFca/jJo280S2'
        b'Q0u3T93O0TlZDWIZQfC7DGaG+J5XzFBWh23gxKCEQLDNFO8WD+kkz7VgAWMTOtkah3PuSRlCYXiT4W63hHgOggcx4c4uzRiy+ww7TyZY9JOQEc32KXBKZWgwcS+WEFoU'
        b'g+UhTIhNNxKsChvhyfEJicl9YYMBnhk2JoHtNFPl/MW8x3mrcbxyZM/0XgzJJ896gNogtC/mAEzBMYLg2LgknKVoELgYn87AJrA6lZk/0DYnBlwk4J++JcnsY7sqmpNo'
        b'ivdIB0aDE3jYwyqw1VxOoni7bsHx6WNJrI3YiPZwLdjqEADXgAr5VucfGNXnqJZ+ynMV1VHJcLxzec57T50GjVtwpHJzSP/dcb2vn5jxj5qKno3BkXEONw9UDeWN87u2'
        b'Yqjw+767HziNbJl27+1FkW9smVGyb1X89otjbt9N3dhHPOSG2upoTvEvm6fIp7b6D1y4xf3a9d/B1GSbXxz3XLhdfn/06uhtD0+NTkhJuKasmnar/7SrI4rKb9zst3Xo'
        b'zSMztR73r6w6efWdC+6/vJtzweaaRH7yyIPL//7hauTogpNxZ5NvfJ1/73JVfOXn//LYW/4Pj3mXv/ZbWAIihkevvFv30HH1G/OiNpQWedv6qu8+7bbKOr3wlU96jGm8'
        b'Lwug6YTBsQhwVg/5AGfBagL56DOKADusYAu8SNn0MOTDzhY054+mU1T7wDqvIFiVEg+OCRhwTipUsL0TYANlGKwOA5sNJsyCQI0O9RE3iUwhjQVbSFI40NzN7CxS2wwS'
        b'XAvrKFCk0QceaEuBJIbNGqMUSH4iEh45al4fwrwHt80Tm1DvgQpYS2JeMVYdHk9IjOcxbOpLoIEXCM/DDe0BGw5/U65wHOJGZq7w7KzRzNVSJsWGsOgJeE48P5IOCf/G'
        b'UYN23KwVS2IPu6NvD0xH5KCfnZFIpclGeTna3lnjuGyDqSrb5xI8QGBQSVvKTv2Z5Jmdr6rrbThfZSSlZaQGSa2Eo46YlQJ9aqXOcBFlIyGL0cFGKhIL357xri9Vkafz'
        b'rbp34RFuO4eYKYU0EN9ZBrapNBiUuxY2g8sCBt1HvMVTwR6K5CAwilK4ErTao+XJTB/QNBnuAttJxL04biE40z0NH4uBqhcZeKoXaCJtLfNYlJTA/kDwGDG5MVSxKuBx'
        b'eCBiIDwzU0iRF+AkPEGwA6BFPQNtOM8KKFJjNrxAqvkwUjiiP0sBEP9c0pXGOwyIcs5meCMJJkMe6UMD8//ku6RLGLoy1ldC97zPd5j1Iz+UYDKm+ITQPb8SO4ZPYclK'
        b'h6XhOXTP1zztfY7gKArn2cGNE2V0z6JCu6GPeGRl4jRZGF0pWGQtUFCREq3tvWkXDegFzsKDLmnjx49nGF4sA0pZR4rzPQhrU+Cl2IhQzAjIg/twbzYHk+5YAFYVpY1H'
        b'5z4SY+sOYLLZs4sIxEMJls9OS5pAEB7w/BwO5DGyB8HKuLyUiWrLkaMuxwAPUBdJ82PAg+AgnhXqhTQaqO8125eCHF5JAWcJtIaZ4Bk+EO6lWI2aEbCaYjWYoJcxsdsB'
        b'AvEFZeAVcBgcBzV6cAaHzID1ieSapzp4yOC+tPEiPr5q7kLQAI7C9XS03QRqwRF9dnm4eQqH0PCCGyiCAve0+0zb8f9iRRi+owiak0Y7da6HbcFDhqwMfm98HpfzqxUc'
        b'Xoi6FKwnKA24nJHAFeAIHYmz3F0nsePxvbzotq0dl1miur+1D+pSsDuAYYYvtocNkaCVXoblLmAF3DNY5RgRKkCdfZSBlxaCOvmPN5dZqdDYzKQHHsvfwNHqvmdb9dB3'
        b'5VC/3yt2LK8p2+lxaKebyzaBViNbP0NZ/vFvouQJ10ZetT3kUnjPeUJs0NTIXa0PP2ktWZ+4uUYumfTFO29tav32Y022XVO/979+vd/nScqKZL/Vx4rfaFnRNCFwS+a7'
        b'cZUzHAe9w2/Knnjltb0lF+KyFq/LdnnSU3Rt7RzRzw15F7zEJ3JfnnU1few0vx419zfHNiQ07ou6+We0NiTgt9njb9R/Ernibhe/i0+67v3J82j13S+u361euvHpye8m'
        b'+ty+KfG9dFNy/ejkjQfLwlIT51evqnzqUFc6cvl3L5UFrKgT58z62PnKrEtHFK47zm27E5X21oxva6Y+kIGA5MOaSUmlD6POCzL6vJ2Qofrx1Lj5v12aMvhpbfAQuDb4'
        b'nOP5DY/veHoq1X/8vCvAjYTJL4Xb4YF2MRCwtLD9AOYygmOyjfMLIkOieNYUIbLELrJggwpWUERmKV+6eCkyfRJ5jKAXD9SDVe5keE5Atkkjx+nnGc0l6IMtoJmCDw/2'
        b'LQoHx/ToDg7asR3spOiLFaAV1iS0A1/AfXCnNSOKs7KFlzSkmUJ0zGW4H7ZSAAYXVQLKw4nos8AmsIOgL7p2FesSfbqBdZQD5gBcEYUOmwc3GUbQ4PCZ5DR65s35LgQj'
        b'MsKXQ4ksYXv7A0qg6AyPgS3jl5oFZgyAu8lwDS9EDAeNmW12CGi2Bico/2IZ0gGnEjhIBTqLLRSY4QSW80f1TKL4mIsxmPaMgjhPh7YBM/yXknSO4Hgi5kvgcB0n4BmC'
        b'zHBazI9NSaSIi61gfxQ8AC+bgWWA8xoi4wwvUJ6l0YEuaNhNiZBaQ0fgcnBex9gAz8FGXSLFU/A8xX1sHdIVXpprHmhTD9YTGkkxvAC3G8cYrUkCu5x1MUZwOay3EJTy'
        b'jPR9hEqF2CcL2tsnRQKO45dFVokza0OC3J05uCnGRjgTdASLvu0MSBSduT/y+Urozd6x8bHjCVkBh5tw5oLl2cdCW/YXFv3Z2HE0YcRqaM89Zv4kTFjIsGniY2qaLGN2'
        b'GmcENG1GqcKmhMW0vn+JiiwXCa4xtVTM83BZJ1MmefR4prbn4ToOqzMMebjQ3UPz6iyC5xZQYq1gpC/qKLGWT38yAIbADU4Y+xcons/MB1VwJzU49ge7BqWwDC+V6Yms'
        b'km3gcJHceuUEVnUEbeydDKPW4myrzrE57zs5L9nzmaC2duxHy+yd1+9edm2i3b6R4y72cgvq7pd88nJAcu8bl25c+9AlbVS8Yt+VcdO+2vz9nLC8BUeO712x029r9qQm'
        b'F16mxrnh5SvfTktQ1rsM7Ld+ZXXvuedCBvgM9UrZtvDnfuENww8MrBZ9tKog52b+5f9cO9UXfPrJozNF72+v+snn1q0V0atnX3q35Endk/6KpjGlEUdOQN6vd62HvTEo'
        b'v2ACR60FzinySHcx8CRo4ri11k2lz/4pR1BOuLH2YFa/NnItq1yqWrakWumosxgBqMHUWf3CqWJbDjcwJsxZU2QsbIUbQCXRC36gDpaZEHMhS2gNC/YiXbSGKBf0YIKV'
        b'RgRbSJ7dLKwrBBcpqqkSPeGXdBxbyGIB2zHH1lik+/AJWIEWUJpgRK+1JDGUn+MOKBcvslWa8/V0hUjB7cUEW2modXx0ANjbM8iAXgtUDCYMW/1hCzl6OPKEzusYtpCd'
        b'gzpgBOsJTw8hW4NGI9WKKbbCUdN6hi3YIiBdNw6U+ekptpiYyZhgazFNKzsT1sI9+lHJazYdl0SgnhzYMzeHY9di4sE5Sq/VFPm3sGsRPiiiyQLba7KljLh3xwRbWCW0'
        b'EWwp5zEdo7PmGzXrK9Blul1m8rlthlJL1xTSDsYwDYrYYslXcoCrKUqrhGEMoVqdCDY8z5Bk2WpZvopirUyIs1z+kpPbiWtyCRW9sGLOZAhTltCZMFsJDZmrnnoEvChT'
        b'lgMeTZ4KUF2iea6RNjxijTuDDWC9Sm+dWWGlWu7YnYUbxWMCeMnyz2T/FKi8kenLb/46rvo8RSm/P/eLPivvPa5UfTbCrkeXkTHfpP7evL73fmZy5UDFvqaSvOy17qeu'
        b'XhvyNCz6868Pv3XxVf9DLQ+LTy39ZpV07orzf27/fNp77/7w9u453zZul5bL43/wFXf9+FZJ9Gm7ml+Pz/qmeZI0Y17uoFF7g999dfH+hPk+XZ8s6+/zoGyLj+pfQdfO'
        b'fRb1flK5Tcv2Txem+P0WO//arNuS6tevXgHfBL35VcOEKb09XJduKF4wqFlw+KR69jv5FTWP/Hc2D5A/bBB3+005S/W69ydNV37rB+22zo/Yu/ZC4JcfH9s9K+vKhi89'
        b'/Atjvh+3c/OOp9tVIbfc55UPCiyePPqXa9fneNc3RXQ7XXEo/+DQx9f9PpgdtPPe9UMx/3Zr/YMdPTM7bMb3AXw1GSyOwQOevQVwNbJIeEORm2HtQ82a2sEzQWWJcVw0'
        b'eccjQw86DncGpydKDHJWt72tQTZqI1aMu3jt37l4/+/cjs9dIKXD1z2OZgsCJrXJyFAUSqQZGUTp4DdbTHeWZXkDeT2fski9CHmurE13kVv3QLdot/4sbzhWQyNs+E72'
        b'/ZYyc1me8n39c8jXshkZBi9tuv8/6AOe8gP9Y4wlxXqI5o39ZqQhbZeIIQ5wKfaJwDqk9atmg70piaAKrLNmnLrxe1iBRnngmERWhemJZnwm7lGFqTvdrJ7+ct955FjF'
        b'qpGZw1wnn0y91UN2M27B79PLt7vOuLqmX/GexD6OAx9OX1zyZWlO/TtfrAr444RLhrxv8Du33Aek73qzIbapb+XRfFXapD3jgmZ8eEdzq1LCljbsdpFc311RAT0i/1v8'
        b'6kKBS/8dN167XRbEFpy7XZrzad9dwC126aPVXzzi2xT5/9y1CZkRWG0LQEs0GrOOgG2wKgW/gMY0vfagmYWH4GFbcstPAq+4J6SIYRPeA4/WKtDiAlv5oCEFbCGVyGLz'
        b'aA8kgIbp2D5fS3rAld8T+VDVxNebBipwCjNhdGCSNSMUsDaJoInaIge7wnq4egCogHVChpfGwL2BYLuOergSrg8ax/ayYngJDKxTQmo9OMJKXoIfPI3Z3lBzGDNtH8DC'
        b'9XGJ1LUpg8fzVMhXrTXYwS6eBScne1MPsnxJJnZ9+qeKOci6E1zFTwZ7fcj7X3ACnLGlswFwuRfJyScdS2qGda624GhfazSOj+XsKoeuLDwF9kDaE+gsqpHRtToGnEH7'
        b'FHH72IEWFpySehGPJh+sAsjjhM0OoHJesQa2FDsUa3jIJgNHPeE6PlgDKnyJlIXJgQmZhMZ0TRA+EUwYu42Fe6yyiZ5J87bFnT4gwRk2IyVTjd/54hXWjLefAJlxdeCy'
        b'UV7iHv/3T5bpg2b7DGVjRve04SEIkaijDU3nQ9LpY//Mgf+Sqf3jRy0Hom58tXyFrEArwIG4Wiu1pkgh0woUcpVaK8AukVZQWIQ281VqpdaK0KRrBZmFhQotX16g1lpl'
        b'I62HvpR43h4zcRRp1Fp+Vq5Syy9USrXCbLlCLUML+ZIiLX+BvEhrJVFlyeVafq5sPtoFVW8nV+nQn1phkSZTIc/SWlNgrEprr8qVZ6szZEploVLrWCRRqmQZclUhDi3U'
        b'OmoKsnIl8gKZNEM2P0trm5GhkiHpMzK0QhqKZ5A+nqVX+xH+/QMu7uICT+8oP8PFV7j4GBff4ALTeSr/i4s7uPgCF/dxcQsXH+HiW1zcw8UnuMAUa8ofcfE9Lr7ExQNc'
        b'fIqLD3GhxcVDXPyEi++MLp+dXp8+jjXQp2TbE5tsHG+blRuidc7I4H5zo82T7tyyqEiSNUeSI+PgxRKpTJocYEOsRMy3KlEoOL5VYkdq7VCPK9UqzFGtFSoKsyQKldYh'
        b'FYf+5cvicG8rf9H1m0nwvNZmRH6hVKOQYQg69bEF1kh5md5iQ9wIHv5/AGC4RWk='
    ))))

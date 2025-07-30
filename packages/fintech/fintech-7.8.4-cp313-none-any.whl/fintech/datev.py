
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
        b'eJzsfWlAm1W68JsVSFgCBAhrX3bCEsK+dYO2lB3akLZ2AQIESBsCzdJVu9laWrpAawW6WOgKtlpqbW211XqOOup1HCIqFB2nM4569XPutFqnXu+943fOeZMQSqjjzNxv'
        b'/nxVTs6+PufZzjnP+xll949j+f1uHXIOUQpKTyVSepaCFUDp2cs5C12oSf8U7DQW44uxxKiEKJaznBdGpVlictBfPSo7h72cH0YpuNYSatZypzBqua0GmmrkuTRK+T8+'
        b'JpibWzlvEd3cUm/SqumWBtrYpKYr1hubWnR0vkZnVNc10a2qulWqRrVMIKhs0hiseevVDRqd2kA3mHR1Rk2LzkCrdPV0nVZlMKgNAmMLXadXq4xqmmmgXmVU0ep1dU0q'
        b'XaOabtBo1QaZoC7IbnzB6E+Ip+Q95FRRVawqdhWnilvFq+JXOVU5V7lUCaqEVa5VblXuVR5VoirPKq8q7ypxlU+Vb5VflaTKvyqgKrAq6BClDFT6Kb2UzkonpZuSq/RQ'
        b'CpTeSleli9JHSSk5SpFSrOQp3ZX+Sl+lUClR8pVsJUsZoAxSeqYG4wVY6awLrgwcn1RdSAilDB4PK0PG/TSVG5wbEkGFOohtoGZwplENLJftUnZZnf1SBqA/bzxULln9'
        b'RkoqKNM6I/+MYg61TuSGfDWum9dyKFME8hbCy/AJ2A53lZcsgG1wb7kU7i1Uwq3iigQ+FT2PC1+ta5GyTHguwX64K8tQWAr3gcvhcE8p3MOiBIVsMAh6ZknZJtxmINtU'
        b'XLgWPhdfyKO4XBY4HpxtCkTxrXAfPF1cGF+YAHehkjzKHe7Ogh2cskecUUka5YD7Z4MtoB3ujm8F/eAF1KM9qA4BuMQGL4An4AVTGO7BqbRHUJ7nXUHb2tUmeGm1K3KP'
        b'J7AoP7ifA/agCNRVnPGxEj5oB/sTixNiUct74H4cAttqnKjACC54HJ6V17HspizQOmVPImdmQBWaNrSWXLSSFFpBJ7TaLmidhWid3dDaeqBV9kQw4I3W2getsx9aZ3+0'
        b'xoHKoNRAyxqzKp3s1piN1phlt8bsCavJymWTNZ4Ua1vjhgfX2G/SGgcza/x1GD/5DEuCaqiJLxelUyTyz/EceQcH+2riH/dMYyKDwpzz32Sjqa+pce3Ma2YiU+K5sQtZ'
        b'IoqaXVOiR7M1QGkFKLp4kYTbmv51JEX9Pvpb9pUk16xvWVqMReLrulmDThQtf8R95ifJx93vUiT6XsZ3Hk96sGLuzN7p91eJy0Z/aowyJaCEMnAhFy1te+KCmBi4O7Eg'
        b'Ae4GA5Ux0WuLSuH+eFlhQlEpi9J5uMxAEHBmwhIJrSM24iUSWpaIN2F5KLxAqULbEnD/iUvQ9OASOE1aAtcyPZ5Dky9ySkBfpGJhwiI2xQYH4SCHgscawQ4TmllKNStJ'
        b'waaocDgQh5yzRSQyFO6uVCxE0U1UbcQ832KTF94TL6+DB+BBhM4T19VQiZHgrMkHRSfDl8FReBDNTgLYAy5SCfAU2ENaRXvjcbhPUboA7uVR7BWSjawgeHQT2efgTNwi'
        b'vKniitF22FWyIAYMxBdINyrxNpfBAR7YVt5Kas8Hp+E2cIlPUdPBFbgHuc/DE5oX04fYho9Q8qJKVXPnywIgl+wof794LH91TKbzNnGuX0b7kUvtxTJFtOf819649cbi'
        b'1vuaR/nTfvVB+sXuhh/fzvryvzzefmpW7/vs2DiXV748qvzT9vea9/028OrC23mpWcmzvQ5p4vdcmebfuHC29xvFYz90JfxenlT2zC7n28H+bw39uHj1jWc/bw7av/56'
        b'n3nds7caZJHLYxcZS2/88d6sWx9LD1wszf72152c/YczKt94qf7Cx8OeeT7fGwNhU9jXX8HpHwn7u4e90/5d99zvzO9Fg6THS+Z9bdg8K2f+hlTDT9Srn8cU1TRIefdC'
        b'8CRdAefXFsO9cXBvaUIRRmJeTmhGr3LgTvhK1j1/vCZPUPq4ogTYVlhSxgtroYTgIhseg92mexiJpMP9cEecTFoUVwW7LKjOA27htCwJIengiQxaiGfehBDT7kQ25bnS'
        b'Bb7EAc8K9Pcw3oYHwDG4A63TblTRHg7F1YP9WSxwsaZE6jbGjpHqMaz8nY4BY36a3jL+b8x3eoO+ZYNah0gmIcYyREjVa2aOuenVunq1vlqvrmvR1+sxLLJxDWwEcz9s'
        b'oe4+yqJ8A7qjDi5vy/8kKLK34aOghE7nDtaot6Rzxigd1pHfnXSw8JbPtF5er2HEJ87sEzdKR/X7XAgeCB40XJ07LM0107kOct2iw3vnnRTYpfTz+tcORWeM+GSafTIt'
        b'ySN0splOHky5yhmmp9vXYhzxiTf7xKNsfXP6eSeLTnrY18Ttb7LVNEpHnnXvc+9fM0ynM3n+GBA+FJF2jXtV+bLQHDFnOGDukHju3WAqWHYnhBL7dWV2ZnbnD3uHD7mG'
        b'f4e3vx7vf6n7GJ+ZozGn6mq9SVddPSasrq7TqlU6UyuK+TtXyh2j6glLpffEiV5WZxbOlYWc/9xC3d/IYrHE9ynk/N7dr33VFuEdNo8lviX0as/6Pddje+mos8ctZ+8f'
        b'7vIonsga+tGAUdURfhx1TpjOmYDYbNwjwbS8Q9RyzDsizlHB0nMUbD0X/fHklJ6Pfp0UHL2zQqCkUlkKLsa6K1l6FxLi4ZCeSeETP8bPLCU7laNwImFXwjBxUdiZhN0U'
        b'Lnr3RjbCtMIx/kIyq18pMM0gU13Hsesi14p7m3AXWQw/dwhXT5EGGALAqbRjXnVcRAA4dgSAOwHVc3K5hABMirURgMYHCQBnEgHgMjT4Xh6XQr+0PF2+fGx1OKVZ8kkt'
        b'z6BCKU9sffFS3dPviEDQ61tc8pYs2Vov9e544yh09v41Z6Dhtcrg1/dJfd+pEXzo926/8P1/a1vRIp8TEy58yzequ43V5rTYH5xiqdv5kYKty71f3/vG5RL5y2LJ+1s7'
        b'UtyoR3a5nhvYJuXfw5wuaAOH4FllSJyN/4njUx7gDGdDNjxM0JjvCrg7bs58WzqHco3nOMXAPgZNbYc7M+EWsLUYtpcgflDKp5zBbva6R8H2e4i3oCLC4NOYmBQXgmfh'
        b'q6UUxc9k+/uCbQyGvJgFzoD2csTtuYHrXIoHj7LgS5Hw/D1MXgqCa+LWxCUUFGLs6gxfYIPtC7lS3tR7gWfFWmQLjDlXV2t0GiPaaB4MjMisEQRD1VAEQ90xsql4+YUZ'
        b'AzOu+pnjcs2imA7uk67dK0fFkq7izuIRcaRZHNm7clicNJhrFqch1BUSdnxVz6r+sP6k7haUVzgaPA39CD719rOU6eV+KI68w6HEEr23bf/zx7gGtbZhjIslkDGnNWq9'
        b'AQkrejxQva9tCHy8nWvwhma2MeZQ9eHIWYZTU5HzX2gbI+zKCv0FO/g7DGuH+JHUaaGcU8d2tD3qbduD2RypbMvWYE/gjTghEzgf+22CNgE7l0O2xqTYqXkjWwfstgbh'
        b'/+AleLpWCPci4NmHuEC4X1EAT4MDDJQtqCAM0yzYx/eE3fCoxrziFY4hDxX7pPRXl+oOo30jAhK0c877+0u8/lMiOdGjCnttT6jrS1pX1zN7RJtiwyuihWfeo9eUXBRd'
        b'lfnw30ul3vpv/jcy/X8+K+USwE4SwG47mEaMzh4M12An2HUPLwg8JIQvok7uaoFbEAXeL0totRDqgE1csAM+A4/fw+vKL09AEM6qQlBsBXC4xXAPo+ZScFBcXI5kEnbZ'
        b'5jWsXPDyRinbDpzxOllhGZGKRrVRY1Q3I3D2soGzLY5AdLoFoudi0Os2Ht/Ys3HYO/aTgMihqOyrleao3OGAvCFx3qhfYNeGzg1dmzo39dYP+8UNieLs4JSnxzzgGFen'
        b'alY/CJ08Ap024JRhJxE5dVbg/HEL9Zc5HBZL8kuB8yA/nDoplHH+5bh7kvzkEEDjkR/cKIf9DwCoDTg9wFM2+DwA+jXrN95n4PPeqXUMXl/w2c9AaJ2zd0Wi8MynIr6J'
        b'7nnvZo87tUTLP927QMoh/B+4gITTcxYIXb7EinfBE4p7NErmbJYh4HwKdW2XA+hsMBDknAVf0cEXwT4GBVvBc1a+lPMgauUQWBwHRoMDYDRMAMYkCzCW/QwwhiN82yXo'
        b'FHSnvi+i7fElgUO9HDfIW6PSmiZB44O4MgM7mRQWjOxwZSkCx2m/ABz10RigHeJIAoYcG47EEiWVyv1/gyd5k8CQx+DJYHiJh9UllbAtIUG2oKBICdvKFUhm27gwvkBZ'
        b'gAQ4GYsywhsufPgsI1nD0/B5eMEecn1Bhz3wWiEXnEWYtfzwIxxDCyp2J+DkpboeBLnnX0eQC+rfeZ3iB4h2h+44sjX0sOc7KueG1B3PK/znSHb4Txf7S76V5PnnLdnW'
        b'LZFvSatoFlR8sljcxI/7xPVMBb8ie0U6n7+98BNXAe09Ki91/sPrYuHWl3O3hh7bivgT0dPCr19kITkLa5K0+qX2UhDoBKcoTyIHzeQwPMQWDthnQ9TB4cw2WAJO3puG'
        b'UhOVEoyj9XIHmyAeniAYOs2bSzaAYsE4ht6eyFT+Kjw438KCiOFRCxcCD5b8LBti48TH+KZWLCuNuVk2ChMke2Qps0fuLuFQkrDeiH7uiF+C2S/hEyxgzBoOmD0knv1x'
        b'EN0xF2Hs3tSzOX05H/rJPgmRDsXOvCk2x84bDskfkuQj8A0OvcOnPH3wNhoRhZpFob0RH4qi7TaTE7OZIrEzcRfZ9duJsmB3qwyRix2MtJopiwyB8Pv9xRi/36F+GZJn'
        b'dpW9lmYi58EhWhqiRrMhdlYl539TMTYZsXPKNMNbv6AMuEdF7x8gePrd3t9IwAkE8b4IV5f4h74gi+PMCSlw8z5zmF4U/2PvC/LHdwo4c6QVi7eK1gRuG016I89f9Zcv'
        b'jtUkzY/ZnnyO88grK11dEaC7hp4vcu1rXTsgb71CUcXThYtmbkGcBgGyQbhlDobgQnDajoOOWMak7swFT1oQNNhRbwHQbNBHYNc7H3TA9vhCuDeBDy7VUvwqdjg/kSB3'
        b'V+/NVsabgrvhS4TzBjdiEDD8DXIlBgaatuOmkdRqMOoRwncfR/g4TAB5OQPId5o4VOC0bt++8N76s6v6Vg2HJZv9kzv4o+HRZ7P7skfCU8zhKR+Fp3UWI5iWBB0X9ghH'
        b'JFKzRNofMSxJ7MhFsjYWsBHoRKTf5VOSyN5Fw37xQ6L4yXRhSigmVMEOiAuxU4QcE2WhClgQbkRA7PVL4BeTMylnjFdN2Hd+g0atrTfoo3Asu+yrvyLIlnpgiQOzTWiS'
        b'BNXVzPEE8rtWV682qbSWFI/q6gaN3mDUanRqXQsS/AmFc65DOKGxRb9+zNkiGTCV60soqxRAuK0M277E4xrzwYugMmrqqlVGo15TazKqDdXVP4ec7NQEEquDxWdDNl7G'
        b'J6jb3n5tGOe0FYz6+SPHN6Bt/qiPX1v+fS7fLep7Ecct/nsBx016X8B3i7kv4rklfEshhyySCVc2C24XCYtK4b7EUPh4EYtydmXXwO1w6ySKhv99h7HgTJYD5QFHz1Nw'
        b'FTwFX8bW8/2pR6gwSuG00IOa9E/hbD1Qsv7qnRUuepdGAaMimKdDnMn6rx5DCT+K56prNcYWvVqXWKxX1zPer0RkIb/CqOBHr0Vq/QZTo6FVZTLUNam0ajoFJeHu/uha'
        b'ojZuMKrpfL3GYBxg65E8S331JtoC3/cghr64RWdsySlD60zH5Nbr1QYDWlSdcX0rrdQZ1XqduqlZrZPm2AUMjepG5BpVunqH5XQqI7yu18roCgQULajsoha97m/J56iy'
        b'VWoEcnSurlFVq5bmTEjLKTbpN9SqN6g1dU06k64xZ54yoQR3Cv0qFcaEwvoyvSwnV4cmTJ1Tibg8bWLuKlW9jJ6vV9WjqtRaA+b9tKRdnWFNix7VvMHaht6YozDqVfC4'
        b'OqeixWBsUNU1EY9WrTFuUDVpc8pRDtIcmnkD+t1gsituDdSuxb3D2kba0hEUJaOXmgyoYa1d5+mkKVOSc4rVOt0GGV3cokd1t7ag2nQbVKQdtaU9NT0fXtcaNY30mhbd'
        b'pLhajSGnUq1VN6C0PDUSkVbhemMsUVJrGj1fjWAHnmowGvAo8ZROzk3PL5HmzEsoVWm09qlMjDSnkIETo32aNU6ak69aZ5+AgtIcBUIbqJNq+wRrnDQnT6VbZZ1yNEc4'
        b'OHHWcMwqDMMJZaZmVAGKKoGnsHp3FZ41ZvpRZGFebhlOU6v1DQgNIq9icWF+ZcKcFrQ2lskne0Gja0KwhuuxTHuBytRqTMDtICxXK7O0afFPmHdH8XjuJwwiedIgkicP'
        b'ItnRIJKZQSSPDyLZfhDJDgaRPNUgku06mzzFIJKnHkTKpEGkTB5EiqNBpDCDSBkfRIr9IFIcDCJlqkGk2HU2ZYpBpEw9iNRJg0idPIhUR4NIZQaROj6IVPtBpDoYROpU'
        b'g0i162zqFINInXoQaZMGkTZ5EGmOBpHGDCJtfBBp9oNIczCItKkGkWbX2bQpBpE2YRDjGxHtJ71G3aBi8ON8vQkeb2jRNyPEXGzCqE5HxoCwsRqJ09ZAqx4hZIT9dIZW'
        b'vbquqRXhax2KR7jYqFcbcQ6UXqtW6WvRRKHgXA1mUdQJDLnLNRkwQdmAGKKcxfBUkx7Nm8FAGsBYj6GxWk2zxkjHWEivNGcpmm6crxYl6hpxvnx4SqvVNCIaZaQ1OrpS'
        b'heiiXQEFWQOcUkGOoewrGyfjCUtRLxDCiMHFJyRYyqOkyMkFkqcukOywQAqdpzcZUfLkciQ9deoKUx1WmDZ1gTRSoFTF0GUy54gvQfwJiTOq1xltHoSJbN4U+6wGWzZm'
        b'IfLUiBw32kVE5izV6NBq4PUn7eCkDSgKk16EpScEkycGEfpRGYyI2uk1DUYMNQ2qJtR/lElXr0Kd0dUisLWtuFEPTzUiICrU1WvWyOh8hn7Yh5InhFImhFInhNImhNIn'
        b'hDImhDInhLImti6fGJzYm6SJ3Uma2J+kiR1KSnPAptAxCy2zarAwGtJxxshRooVXcpRkZZ+mSrOhMgfp5Y5bw3yXo/gJrNjUY3hI+lTc2S/JnDx1yxP4tL8lG0KVjrJN'
        b'IAHpk0hA+mQSkO6IBKQzJCB9HBun25OAdAckIH0qEpBuh+rTpyAB6VPTsYxJg8iYPIgMR4PIYAaRMT6IDPtBZDgYRMZUg8iw62zGFIPImHoQmZMGkTl5EJmOBpHJDCJz'
        b'fBCZ9oPIdDCIzKkGkWnX2cwpBpE59SCyJg0ia/IgshwNIosZRNb4ILLsB5HlYBBZUw0iy66zWVMMImvqQSAEOUlWkDsQFuQOpQW5RVyQ27Ep8gkCg9yRxCCfUmSQ28sG'
        b'8qmEBvmE8Vi6mK9XN9cb1iMs04zwtqFFuwZxEjmKeRW5CYRaGQ16dQMigjpM8xxGJzuOTnEcneo4Os1xdLrj6AzH0ZmOo7OmGI4cI/RVOni9tcGoNtDlFeUKCwOHibmh'
        b'VY3kYYaZHCfmdrFW8m0XNV9dC69jSv8A29DIxFu4BmsoeUIoJafColyxKzxJ7ZI0OSp5chQSc7RYKFYZMV9KK0yoOlWzGpFRldFkwGwtMxq6WaUzIfJCN6oZMEXk0JEa'
        b'QGpXRIOJu6aeFPvZzA7qd0CUHNc9OSNRMY3PDo2Yb9rC8pKpbMDplklm/Ml2fiwTjmuqxlg5RHlaNiDQl2HtWDl2KrCzgLIcsukXYgerAcd4hlatxsioHiuxYozF6A6x'
        b'bs2iN1xkdbBOzZBj1RtKsd7Qv63gDp/yTRz1ibnrxJW4txV8K6B8A+9w5Z5zWPdrWZSHeJe6Y077yu8aWSm+Ae35jOIQK7vBtbQFBnypblf8ozwwwKWc09mb4DFw6l+g'
        b'OWyUCscEuXV1LSadEQkpX13HU+Oeh8CLkXBUrWrtVz6M3hBP7o8BcxHANSMuBmvHaUbGQttFg5AcyoIvu45xMbelr0Le76+jCGUzwzy1NOnUtKJFq00sQNhPl1C8Aety'
        b'xoPj+DRncfFSmimGdXYYUxs0BhMTgdPsw8z+no9VjIwswTSUp0xQ1DVp4XUEZ1rE/9gHc/LUWnVjPR4I47UoeMb9yRZZLMc6E0S2wMyn2oJGrAIizTBgFjFzXCFmETCJ'
        b'WIBFS5QZbWQjEUEsNZDmtBqUgfg0uoYWOoHO1RutXbHEFOpwyQcicbZkR9mSJ2VLcZQtZVK2VEfZUidlS3OULW1StnRH2dInZctwlC1jUrZMR9kQP1OuqExCEcXMwmC+'
        b'Wk0ikydFogBdqka42ar1pU0yelzriyIZWLaqYWU0lg2sEj6j3h1fRrokriQn36RbRd5iqPWNCBluwAgMx+cp6dQshqQ3WLNg9bOjeAvcMEkOKsxZSkQPPHB9swon2kDE'
        b'UYoNVKYqlvywYo4TGRB6SDHHiQxIPaSY40QGxB5SzHEiA3IPKeY4kQHBhxRznMiA5EOKOU7ExbIeVsxxIllu+UPX23EqKfhwQJkaUpIeCipTpJKCDwWWKVJJwYeCyxSp'
        b'pOBDAWaKVFLwoSAzRSop+FCgmSKVFHwo2EyRSgo+FHCmSCU7/qGQg1IVRni9bhUiXWsR8TUSJnitWmNQ5+QjEj+O/RA6VOm0KqzHNKxUNelRrY1qlEOnxgzYuGLTQjkx'
        b'wss1NWAVnA3JWWkpSsKYd5wg0zG5ug0M843PDhEyLtUYEWlU1yMORGV8IPkBPDy58DgmfzBNr4VXDBY2YUJKATlJajAirsQmwhFKkkD4HYfyhmWkFmqOSD+iNJhdbyCM'
        b'ejMm8Ea1Bk2L0aaTLkRctVHToFmlssf+S4nIadNV27MZjKBqd2ZpzyblqxkpRq2pxUklaNXwIZyB4WymZtTs9dCo36hlldbUvErdZFWaEyJIuDh8S5vhqvW1jplktdXB'
        b'rKMh08okh9sxyRmjPvREJlniOf1+8jiLnBE4ziHTyMmB20G7AbxQXlIG9yUSVhnuKXaifGq5rvAVMDCBUXazMsp/QL2aKZ7MKCPWmB9GIVeI/xQc5HrjP4Z5znIKoUIo'
        b'RZiSp3RTeltv369kWW/Y6HnkdadLAKUQKIRZbL0TCbuisBsJO5OwOwp7kLALCYtQ2JOEBSTshcLeJCwkYTEK+5CwKwn7orAfCbvhnqSyFRLyCsB9Qu+9f+bPReGfJSDj'
        b'CVeyLSPiKgIeGJHHxBlBfwL0x0plW2pxsvkm1h2Y5YJqjlAy9wLx4z8Rqt9JEfRA/SJFJMrDUzqTJ4JeJE+w5TWEJ4r3RKMLIaPzsvXEWzEti2V5ZOiu9EjlKWicw1an'
        b'tyJUL250ctkujRpznouf5cxRLPrqM5S0wU9gDdMMhmPexQoGeHosO+nxvZ2v8I0ZvQb78E1cIp1IXb/CcPwVvtzzFb77OZ5dr7dm1xuwswpnwS//vsLv7r5yxaWdxgSq'
        b'+jUIUeqrNfVjLnUIXemM2OuuYuSpai3iN41NY851JrSTdXXrx5zxzXyNSstcexkTkjsy1c0IizSV1TnbwTRuilzb2kJZb2PaP9Alb/1YaIW5Sic0X8xLP36qwHKnzLlS'
        b'YHenDK2Z0tnuTpnLhNtjzrku5E7ZpFj7hx6mk2iOBIVM5zUb1AbycNk26xpyuaMOv1nORnKPqpken5hsy5NkhNuwysvy5tkyQyqdUYDvX8XkIRRktCJAqYzOxfkRsqqj'
        b'yaVY2tRKI5SdQddrGjVGg8zajG3OHbfCJDMt2A5qfqaNtAfbmLiY2XQJ+cVNzE8ssaZaGjYwbWEChUkDIiwyurIJEQsEl2raYKrVqusbUf8clmJutTBSLCpJq1ARFGb6'
        b'Q2tbEKHSy+hCI91sQrJMrZqUUlk6X6s2rlXjg2Y6pl7doDJpjVLyQjxzfK4sQJhNz7H46DqsmYyxnWfaaTSl1lJWgM2mLatvsE0ufnDeoqdjmNswq+B1/QYkaVsLWi54'
        b'ZRMxCrMcqBizRpY9GqNulNFpSfJ4OiNJbitmtyOy6XwcoEkAF2/Q6BCUoT7Q69Uq1HCsTr0WH5auSZelypJipTLBz1wmdmXeI/15tSdFF+zhU601rn6xTZRpJooEr8TD'
        b'a7C9FJyvgG2FcG9xItxVgS8ZF5RIYXt8WQLYDfeXLCgAzxaUlZYWFsC9pSwKdoJe1xZwYjOpd8d8V0oy/VkOVVGjzcmPpUwzUGQKOBvgsFp8ab0E7i0CN+LALvuqcb3b'
        b'17tSq8GzpFqdvzMlmt7Ip2pq4rNWrKZMGHc0wS78brhUNP6CtUCWEFuEWgDPcan05XyDDvaT97ekEqPUiXJNzWBTdI3rqYwspm+ge+3iyX2D++HWcgX63YPGjfu4R7rI'
        b'rm/gml4Ino9aqTHnlbANp1E15+/rL32GX6P4g6chxQndMzsk/OivzrwuAqzX95ypSJIEv9uUtmNraCe+Q+1zJrvbJerIOxLATd3pD4OiXA3dF7vhtnp3gyiaw5fv6Pm3'
        b'pzkjvCuPz2gTtq/sXnF+0eeSNRdDb72x8t/6WT7lqtqaihrnBo8/vCHoWZWTc/hPj67TfnnzD4qyiI9zv1h989d1rG9vz8yg3l7dd+eq6roRP3k5XzTtt3FVUlfy4GXD'
        b'mnjQnmj3zMuj8pFITgPsAsfIiwKwr2Q6aC+3X3M05CcgWsTHuRvSgsh1bbfwcKFTHZp2aan13aoP2Ml1Bpdh/71QXMs1H9AN2uHg3HLLMjNrzKJ8Q7nCBnjgHn6wLpPC'
        b'nXHwSXA0IaYggU3xwWF2AugqIi9v9b4QvxmzLKn/SryoXuA5DmwHz4BtZChwF2qvJw6eh72opt3xFKrhPDsFXrMMZUk1OIL6sH98HcG+VCmf8lrDATdAZ8Q9DEehkeA5'
        b'PF4Ln4V7WbgS7GWAgaLkcAdfVpHNvAU62bIcZUWVxcpwPrgX7o/DmWgDTwefcvMGh5muP7IEZyP6TdQsmpkE1Cjo4sAdFDxKqloEt+jtWrVwd/AyaA8AV7mgvQBckAr+'
        b'jneimGw++EYUXysd87TSqomv48wUc6N3jRMVil/EuY2GJ3RwPxDRt7x9Ow3d2Qc3D3tH94cOe8d9EhAxFFkwHFA4JC4cDYtDeT2YPFkHNw17R/V7kmcfKM/84YCCIXHB'
        b'aKj0bEhfyHBoEsrqjrJ2GPFTJJzVVl3GcEDmkDhzNCz2rKy/diQ0wxyaMRyaNamAre784YD5Q+L5t6PTcCcjRiMS8W/oaGg4LjMaHtnB/XDC8xI35hrxBuxsxM6j2MHa'
        b'bP0m7JDLt5uph900JuYxLP/sLhyTy7r7MC+EM01Hzk9oIu+XO7FYday/UNj9pY9v+/hJ1EXhdM6EC/QsKxIPIkhcSS2kJv+LoBCTwiqTssaE1eOcB5JV8OiJrEJbHktO'
        b'16qaa+tVM+0AwhrlybICENVdORKc8H4wc9f3RwvZslRsZTFiEPmrT2jRaddLB1hjnPqWun+k34JqGyszudv6TuwcQI4YRZKXZLiPx6sPVzM9nMb0kKnCQQf/kZ55VE9k'
        b'gB7WPb+JU5j0fnAS00HpQ5mmf7irTUxXXaqtPM7DOhkwYQ6rDlcxXfTPUxnUNibpnzV7LtVWBuphXQpGkfrjOES6Ej4lq/XPmSfnagtz9rA+0XgtbdO04vAKS9+mZOf+'
        b'OX1zrbbjAB/Wv3C8jOOwJns/WGaBtZ/hGqfop+2hDFZzzGRbXuqMvxD+577T+RteCHPKNMKZZo4hFkXw4SzmvW/v68x7ypKQp/xDUyt53jqfl2afBzdvsan33uQud8+T'
        b'shk25gg4OjNAbk+HbUQYHEIMBLEetAv0Fk0mw7NkDBHeBM9P+VLXqRqjg+rqMZEdYSUxhK7iJ1j4yVeRCyUJ7E49PrNn5rBf7IBiUDySlGtOyh1OyDP75Q2J8iY9yXVE'
        b'iJgXuZj4MDBwATuDyIlijT92+Uuhyy977EJwwAF+GHVCmMCRCsacLFiJearCNxj1arVxzLm1xWDEctIYt05jXD/mxORZP8ZfoyLCvrAOSWMtzYwSgGNUNY7xWtCe1dcJ'
        b'7VbX3bq6mGLO5Dq2t4UAzs3y4NJZ6YGEewEGQKUIifouSqdUdwsgCivd7QDRFQGi0A4QXSeAnDDXlQDipFh7QDTNQDAnyK2vNyBpEotU9epajG3Q/3WWi5q0mrwtITbJ'
        b'kDRLRFMV3WRqVNtJ3GimDBok4dLMsyEsTBvURhldjvaaAKOxZnwGp2lubdFjwd+arU6lQ9IrzookXb26zqhdT9eux3hPoFqj0mhVuEoiHOJrugYkt9ejPiEUhHa0pQqL'
        b'QIzrEKCiJoNG10gQp60YHUsWJRaNIN/SuyasJ5rctiDGqNI3ojL1VvyG89NYn2vAwqZhtQmPvlavqlulNhqk2YIHFAXZdO4E8kYvIyfUK6zZcE3ZNHm6suxnH7DYSjHg'
        b'mE0ryC+9zHJ90pZuBdNsGmuP0dQQ2X6Z/XVJW14MyNn0HOTSy8r1xvF4BrRREuMhdcTThYryhJSk9HR6GdYI23Iz8I/k+9zKhMK59DLLseqKuGX2z2nGKx/fJlgDwQRo'
        b'XND+0rYtO9pIaLBNCFQQOBrq9JpWo4Xq4HXFz9MIbOVqDS1ovdX1RBmClgenYoyvJVbvyGTL6LmMRoSAZJjCqGpuxo9TdWE23QgBDrRwqIFWC2jVa4idPRWahrUaREnU'
        b'69CMWwBORlorazGqGTAiwK02NrXUo53RaGpGC4naUq1CAIiASo1GV6emWxDRJeWYLmKgIqobA9NtjcGuSRmdjzaddUORUvZgiBU7CFSwVcA6LRoAYxDQoGZy1lhsALbU'
        b'kZ4wBz7Tm4zGVkN2YuLatWsZq0ayenVivU6rXtfSnMhwjomq1tZEDVqMdbImY7M2PNFaRWKSXJ6SnJyUODcpU56UmipPzUxJTZKnZaRkzayp/lm1i1eZCQvFcfAIOGMo'
        b'kRYlyEAvfKkMv+eMAwNIbo1Q8Jq8wTFi+CtgKexIQb9JVA3YkRTsSrQXGyp5gq0cYobNdd8cLmXCd3HAVbhrTTEiXj3gDEPAFsA2bKmqKGEhft+9MAZbBVgM2/APomvg'
        b'ALjgAg+Bw+CaiRiFeRXJ5gfhJeRiOdaJ4tXDK7CH7QoPg50mTMLAdR3cAS+5rpYhebgQPyVH1WNTWGxqGjjNhS+BbeCyCdse2pgJuuElsH15MdxTqoQdrWSYtiFWwLYy'
        b'VHJPsbIVOeUlRfAQl4K7wTYhPAWugOvEJiA4Mw2eESKZ/phMWgSug+MCyqWIjTY5OMhcG9oCBxvhpUJUA4vigC4WOFsOtjwKDzKmAM97LRHOq4dtiTK4CzUbDwaKkOTf'
        b'xqLo+TwuHISXiUU0eDkQjxk8NScxlkWxC1jpcAu8Tia5ZDo/yoNDTOW5Pjk3grmrBJ+BL4oNYVw3eAheZpp2Xs6eH1NBjKjVgt3gSQPciaR/eMjNTQY74eUSeDEOHuBQ'
        b'fus54Hw4bCNzzYvNEAbB0zJUA5q/QjwvHMoHXuN6gGfdNQtGqriGmygb2/Xj5o5Sr21y1x3DT7E/P7uO++ZenWSx9qh5ztDz+jf6T8aVnbz/vafI73JK8ytdqYXDlx47'
        b'2LXs2ze/DN5x7tCl4IHo6NR/3w3fLvxT76PbPmEvu1z79pL4r98efFrh9t5n7U2Dc/1u/Bh+4fAPXY/5VfXt/CIkKaahKNdF4VLUk/qWXN27R8r+vOTDTV/JtVGfv+Vj'
        b'Ti3Omr/i922X1c3lf9j40xMjI398ZkHNgcyjp1L6Lvjt/P5XL/13+aPZV49dOOPU86VTfHeI9v3lUj7RD4nASdEDWqZIjnJmA7gALt3Db8TBRQo8W2yvdNkAzxRalS5x'
        b'KTy4H24Dp0llG9fDLqFqjQNt08scwuttFKFVIIwe6AZPP8js7XcjtTwKzsMzcR61ZQmFhaXF8XCvlEX5wuvcZBVqhiz0brg3oZj/SHxMAeoHWmVwjr0erec+qegfMbLm'
        b'UE2DnQnWvGzvrwWq+vpqhtkY87axluORhLv8dwt3WSKgAuheXq/x7GN9jw37p3XwR739uxPN3rFm7+RRWVJHfvcssziO0dNkHHx02Dui1zgSnW2Ozr66wBw9c9h7JlGr'
        b'zLnZaI4sHQ4oGxKXjYZJO/gdazs9RqWpyLPJLIoanZnXwR/yyzaLckYjYlHkejPWucQg35pO91FpkjUfHYF8pk63T739R2Nk/fpBVj823ZZlFkeOJqQM5g7m9S9F4Zlm'
        b'ceyor/+Ir7R7eQdnVCTucu90HxFJzSJpf3i/fliUPCLKMouyrkZ9KMq1Y5A9GQb5ecp6l/ESdl7AzmXsXMHOi9i5ip1r2HlpCpbabjHwvNeM/6PHjTroIXZex21jRhvb'
        b'SPgJGxspd8HqnftEyfPtL1b14CuC/fxM6qowl8ORuoy51uP7nhbmacyNYTmtQb6qmfxyiXEJF8vJe516TIgZHsTm4Xt5zKBt460T2FEjkZUadWDO28kR532ImMlEXDY+'
        b'TmMRa6YuSk/EhWNrp8SybarIwnsLJvDeQsR72x202fPhiMsW5AoJ7z0p1t5Yg6mFN5H3VtmuYtKMIT3Esc7Db2GYEI3YBLQbEHOKWBmVvbVfzO7E0436FlMrSkVcsEpQ'
        b'19Jcq9GprIxTLOKpYgkHwTAQWLFgu+yLG7RJygIsKf9/Zv9hzL490GbjMz4mxqbaeoDpnwDVTH4mylqAcG7LfuYWq606Zlcw9Vg2giWOYVZ1LVgBoifsqY5hOte2YG5R'
        b'06zSWtjXZQ+5l4uYeMc3c209wPuRab+2pWUVbh/HyOhSy+qoSJhuqV2JJhqJksxhpQ4LE5np8iSL1ghPPJJscPFl43dybY3Ytns2rTSYVFotgRS0MGtaNHU2aFxmd4V3'
        b'gjxkQQ8Tp4m8G1xmf613kkSDsz8g1Uy4LPr/QEjJU69VN1qu8vx/QeXvEFRS0uXJmZnylJTUlLSU9PS0JCKo4FYnSiv8SdIKzRwS7wlijFbOztkU/2v+WsqEbaP4Rz5a'
        b'XFgKd8cXWnm3BY4kjc3sUHDDJdUbXmEEjSfAtUyLnIG4/QNE1sCCBrgEukz4xhTcDx4Hh4tlRaWIfXtI3YtAGxZk2mG7CzjrB4+aME0GvU3ghqG8tNxi6woLM4thBznI'
        b'bUMShwCx5qhGFL6mWA6OIvnnGHgJnHShwDn4lLAMtgea8LGdAhzkGYrg3sLS8mLw/BpsJUvOpSR5HLgH9KxibJJfgk8WG2JL4b4YzKvKCsGz2Fo1i5rWyOPBc9mknk1z'
        b'wbNCbG9toTPiKMuQHMKmvGBfWgoH9K1JJIfXyyX5qKrxg2skD4DLCyvQzLyMGNck0M5btxE8TZpEve0Chyz9KoyXYkPO4rBAeJIDXwY98CBZq0VNbKJAHVq3quRPQWit'
        b'sN1BcAgc2SykytAKV1KVaH4fN2G5UpkB9gk3wst4otCUdsIXC5A4thcJRZexiNYOzqFQCdxXgCWU5f7O85XujO3pM+vw+Nvxc5BCqhD2rzfhlxYbY+BTKdX4gC2JSioS'
        b'kazR/p7wINi+HtupphLhSbBD+8NPP/00FsEjEDWY0qJVL1jDnMv/VOFEuSI2ZTC0xZXFz6OYFb0B+9biydlrkWoL4hdhW/SJRUoEDQVwjyJGimCiAHZvwNbniel5Kbiy'
        b'ENuu5uvcVnisY2S3drAVnFXAQylFHIqFGPxBeJ6C52VCRnw+ygcDQssSLRyHF2cHMwOeM/LhAS4FdipdHokMMMWh8sbloNtgEwsXxMBDCudxCZBDZMBZPnx3eGAxEf9z'
        b'wcsbDEUJ5aWJGHbKLDKglObDbh54wQOeJEZ16AzQGUeM6hQJHpXyKSF4lQ0viSuJGfUDq8rYr/OpdYP+r/p/vOR43jvM1Y30YtTLSxbJn7lbgeAK7kosL10Qw9Q14QYD'
        b'PAaegv3grCvsAC+UkGZXwPPgZJysMH4aGEByMR/sZyci0b/DJEaJ8S4S3MKNTUgsYutZmaANPi/lmPARPtguxfatC+NL4HZbubMrSTF4Bh6uwwW7ZZaC7pUmbNSw1HO+'
        b'ZYiwY5VtjKAbtmluXPsdz7ATcdt+a5tOLywtB7NFx/503zfmtNhzlldewR16Q6cw/0JI6UsvR5dFBNwYrX78pzenffnNC8sSlpUfuKn73ZGe++uGf3XP+9SrVFbHSfY3'
        b'v3lz4D2v+mnnkv/7zcBFhu93Hdv3W+lowOYXnbY8xh78LvCTzrvZP3y1SZ28iP7k0NP1qSc2r1yXnP1+WwWM3ituYf32iXXCxR/eu/n0Pu1crUfw6p6e+OdWbpoW2tX0'
        b'3r8/2vq2238deDFo9Y/VpZ935uxbmqTZceLFX7emf3ti/7/PPvmbVwrePfbF9jMv3g4ecHVbltwZu+bCjarFX8UuupedvXA4NH9M/92TpvqcRef/tClDftTVl9b7//WL'
        b'X+/6a/QfZ7V8+9333n+I3v5d2MVjh9z/MLD3szeTA0//sfUZ/Z1ftw1s/O+bh/fe/usX9JnfFr1zzVC8+Fpm1ouPvHNnlzFnyedfryva7/WX1zVxq16Et/4i3Jj0/W8/'
        b'+KD90kf/MWP1fwTe31qWF/7C/cjfJrbN+GCXZ9433N8VbRL+4ds3E2Z8/j+fl44ELH7j/MkTd7N3Ztz+8+8GrldscYuXMtIzOCoCFxHa7Yt+QKhvKPQlAn0sGAS7Jwj0'
        b'49I86AUnsUQPzgiJMeKyFQjtThTnM72IQN8Ft5HmYDd4EmwvDoQ37K70eCziaGF7DLk5UgaefiwuFt/6aAQH4inK5RE2OC1Zco9RE8Vp42SEXuwAx+MxUO5jo4auEmus'
        b'LibwfHFJIBXLp9grWBlK0EUsrDmBfbAPnCspjUeYNBCRIhZ4fmEwMcGZCrfGILqCL3uEwa14RPxH2dEIRV1mrrrs2ZQ36VZIEMtyL8RtcxPJZZqDxmQ7aSrPt541MSdN'
        b'PLCLaDJWbwS7DOBZeBrsLyhLwISPzLMn7OCAQTV8hfRHqAUvFhMtBTgLBmyaitPgJanPP1tTMbUKA8vUtMV0nAM9hjtWWYzLcmN+E3QZ4wlEn5HLZvQZm4RUQETvvP5U'
        b'bKd52D+rg8+oLqYP+8UMe0v7547EzzLHz7oZao6fM+w9h+gucm+WmCMrhgMWDIkXjIbJGN0FU2zGsJ902Du2v3IkYbY5YfbNJHPC3GHvuaRY3s0V5siFwwGKIbFidHoh'
        b'1m9kmkVZozFYmfGYWRRpp/6IjsP6FRR61CyKuOUd3F3fO2fEO8bsHXMrMKZfPBwo65j7qV8gc6XlWvjV+pel5kiLwXhU2FIQq2ZyD2aPZmR35A8FprwvTr1t8ZrFqbeC'
        b'6V7fI8tGghPNwYmDnOHg1A7BqLdvd+ywd8SAd//SkYQZ5oQZV+uGE/JuJpsT8oel898KHZYWkzZL3tpgjnxkOGDpkHjpJ5k51+bfzH9r0Wvlw9MrhzOVeGSpZlEa1smk'
        b'5eD2kszi5NuhkWf9+/w73Ee9/bqyO7N7uSN0kplOGvZOGo1MGVSZIzM6ykb9Akb8ZEMhskHuiy4XXa7OHPIt6uDgbkWMBMSaA1DnYkdDwkZCZOYQWb/BHJLSMf+WX0B3'
        b'Rm+WOTBh2E82GDnsl/FJSPRQTMlwSOmQpPS2X2B3Y28jyo5SR+MSu516nd6XxIz6B/c69fP63If9ZaPSBBTL63H/4XZM/GDlzVpzSGHH/NH4lI65I+IIsziiV2EWS0dF'
        b'ft0uZlGYRWsU9aEoyU5R5M0oit7AzpvY+RV23sLO29h5h7Iqiv5GHdGDwI+belBjZFMajWHnY+QstSmNsEHN1QIWS0OURhrWPeL+UqXRAD+LuibM5XLqrE9j8T/bd1Dw'
        b'1SZ7Bc8hSumkdFFyyZdQ2ErGur6bkmX7Hgqv0u5WtI4fQintTCwr+RPUNrxcPlHmTIqd+rNDkyULd0aycJcTbnVJLbumZOvSeVQliTWsJdxhzDdlNfFprqsp8vkgo7ur'
        b'Aex1Xs1ZD85SHHdWZkAE0btrNoUpwF6wE1ythHuVpQvg5Qp4WemWLpdTVLAfB2xdA3cQZhycQv91KODeyjQ53J0q58JnWijn1SzYCy7AS4T1eQyxPt2oNlITi+LFshRr'
        b'wWHNehNezWmPBIJLfLBFS1HTqenwRjlhcOfMWwFPwtMIbUVRYJuzJNKH1AS3gd1JxTJ5anIam+JvYoH9SPJ5OqGZfCwJ3oBPbLZ9KIQSwiuryZdCEFU9orlfWcw1pCB4'
        b'+ePsOXsri8ugXBScs+vItK2+3P4tbQJhujJjb2zoa4fdTnw76nSbPZO3+PYrJUUL+949lXpA/fmNnoyW6U9Vt7e0DihvvnLmY87VWtZzcw8NHT+S+qPf5q9/+E1gXvmz'
        b'XwhyPUOEV/ODT+y/5pTV3polzPvj5XPnf//Nd3uOduRekC/94tl3BPJPY3eXrU/9/YpZ6bPeesrpVlH9d7wKJ8V7qveNX37y52U7Hp+3qfHESnXim8/03S2aeehy1eFX'
        b'P4z5euHCu+b2sd98J+h9YlHXmWhT0u9X7Plj46++ePmr9z7+/tVPjef2drY9o9CdHNJ/+dzzhoGPWgPeH+sWXaAjZl5cuxweG7r3mWpn2lvm7rGNuSdfrU778urzcb/5'
        b'/d6XXBpeN/tnJU//8//49jaVxxyc/sP/rLjsse3PQe1/DV63/Zv/4zT6+7mX2nOkXoQlgAcQ691DviXkRJkC2OAESwnPF99juFR4Zi5D3cEef4qLqbsf7CTkNAC+oLaQ'
        b'd0Szs+DLhLzDq6CfuSNyfT3HQt7hifpJ9z7dyhMZjuVxcE054cgDXjMRBonbQjKUwWfAy8Vl8Uhe2Z8InuEawFOUO3iFU+2EyDoRVp7cCM/Bdnx+xoPbV1DcEBY4AXbA'
        b'k8wHGJ6Lyoyz/zgDOA9fjuc4gaeXMe3vXw/Pku/MMB+ZARfkzHdmwsEJcil1zSYkulpu9bbEWu71+oJnEbNzCfYR7mMFeBVuL7bc163DsjpzZddrJQecB8cy7uEjwRrE'
        b'nrQ7ZPRqpczBjTvsskyJMBCbprVdoubPL6Y8QjhVfHiGydAFz4DjxeMsHrwiJlyeAO5hlvTkxpnF9ucxqwvXw+0zyHRFwd4c22dxwKtrKC75LA58gpTMnD5j4pcq5hWs'
        b'C0FTyZQ8gsUZNNBy/MUJ0MH2Akda4KnZUq//RX7Jy8ovTf6Ky5hTNfN5HfvLREwMYY+OM+zRnSVulN+0Lm2n9qCug4P5kMZeVc/K/tgR7zSzd9poIH08uye7Y+5oUOjx'
        b'4p7ijnmjASGdc24HhhzP7MnE0dOOF/YUkuiOOaPeku7UkcB4c2D8sHf8aOC03lCc6Q6bDvAaFQfc4aDf22JJV2ln6R0e8t/hUz5B3bmdRSPiaLM4+o4TjnO2xHWVd5bf'
        b'ccExAluuKLM46o4Qxd11pXwk3Zzjrj2uQ5Hpw5KMYXHmHTec2Z3y8b/jgX0i7PPEPi/s88Y+Mfb5YJ8v8pEm/HBIgkNlnWV3/HHlAbhyQW895g1nmONnDEXONEtmDotn'
        b'3QnEmYNQZkuPg3E4BGUfEWf1zOnlkc/9rBumM4eDsu5Mw4k0ScxAiZyzrn2u/UuG6fThoIw7oTgxDCXeCce+CNwBPC+ROBSF4rsKu3PvRONQjDUkxaFYaygOh+JJ9dLu'
        b'ucdLe0rvJOAoGR5jIvbJsS8J+5KxLwX7UrEvDfvSsS8D+zKxLwv7srEvB/umY98M7JuJfHdnIV8H/04ei/IP7ODdFvl0uXa69qzoTx8OTv5AlGKJ6FYcX9KzpLexX9W3'
        b'ciQqwxyVMRyc+YEo67OQyI78UbF/V0lnSZ9376KTgR+JE+5yqGlRt/2CuzZ2buxNQ2z1iJ/c7CcflFzNGvabNySaZ8d8uTPM1zUC2MyhjWGMZzCq9MYxDgLqX8ZpuVs5'
        b'rQeYrDvYuYucZ1kWo+X/g42Wu7FY8ZjFiv+l9+CO8xOpC8Jszr/2SuSPhwTMa1Sj9YWZ5VBGa9El69VGk15H0pppFT4zs1NFk/MqepV6vQHla9WrDfgyNKPDtijZDbaD'
        b'L4tCG587PXgGpmU097j62vVG8uFMe7bO2QFbZ5JiEnUZvAKxkuCp2fGI89kFLsID4PnF4HlwEZxbANp4lARs4WxcVklYqBRsf/8grxYcoSgZJYMvziJKMtFKcIRwfKB9'
        b'MRJpdybAp4plMg4lBrs4YACenU94xdmehIMUiV1rSu5y11FEqwSPc1IsRZ0oLjjNAvgzj12V8OgYq5rwZ6hX2+EurK2yqKpgl2ci7F9DlIVcd/i4PRcId6WxwOEQ0E90'
        b'WQsWga3FiGV8ldAirMsqNhIFGLwGuuPhddCvYAqywV5W0KYS5ut7x0GnEOxwgwfJGDi5rI1qcEnT8F9vUAZ8iv3Dwu34VmvNzY5fiUDI61tctnUnvVHSh43NszhzpN6c'
        b'OVsrnJeJ4s68U/NmzZmKfEW///p3X3u3792XtLTvUPqaku89886UVPheyu64l1Zbc7uhgrq29/H6FyNzf/tFwDte77L1y0Pq5HFJ//GC6o91zg1CtVuDk9TtD2+eeBo+'
        b'6dnn23/A+2yRrP7Qa5+8qa159ZLqmcpaZ3WqKpU6/AVoevPdWc7fbxa8/lOfa6zr0QTqN+bAeSXhUj7hFNIQu9M28W5t8QrrhYvz4NQ9ZvTNbKvRemyxXtAQDnsXk28+'
        b'wZMbIuK84auyUvw5xH5WMTgELjB8znmwH54D7euqEjFTUJjApoRqNuytR8QbP5yZBfYhqLIoUpbUj1/aZRQp4DrcT7i62YWL42SJ8KyNIWK4IfBMrtT5b6bZzjaabaPU'
        b'KkM13nF2lNoSQyj1BxRDqRd6ENyLiGak9GxZX9lIRKY5IvOjiOzOEkR6p4UeX9OzZigq/SrnqmJ4Wm5Hwei0+P515mkZyBcVe1bbpx1MGY6a3THvYPldJyoy544rqmck'
        b'ItUckToSkW2OyP4oYjqpKSC4W9UThYi8JOA4v4c/NC1x0Huw7iNJ9qhkWq+TWRIzIkkyS5IGYz6U5OAoJFaPSBLNksRB/keSjDtOXNq3owAR7ei4s9oTqFFzVN7VaOSQ'
        b'lj2oyBmIHkuCO1z/rlvK+Oa7noVlGvtbyvM8fqFJ/ouo4ABrjNuqMjZN+GCLTb7UYuzMs3ywBT+fxh8AxR+34ts+2sL/J360pQHh6Ut2eBqjVINqDfZptfYYe/w1MO57'
        b'Nl3YQMdiXyyNyKCBOazEuFi9Dls7wGd/sbINmtbYeFKRBenrmaNCA7YWW287gFTp65o0a9Qyuhyfh67VGNQ2RE/KkA6R7Cq6oUWLOMkHsPjkj5U6l5nwl55hX2xeXAm8'
        b'WIC2dUUB4tqLSkvAQGUBYvvb4mWImy6ATzi1umhM+EMFQeAZeKMYPAmfR2igqFQGdyHRphK24e+5Iq49IQYb9yqGV5zAUy2wm1zyg1dAL3gCHkTyMyIL5NUeR8sC2zLA'
        b'HubU6hR4SghOwxtxqIvrqHVcGcG/TmBPVlw5m2KBk3DnQgoengEPaNw4S3mG70k//I4teG0lmC0++tuIsVSxS26z9I25iSHXv1jiceL2G/+muyLeEPvCF77Xf5D+teV4'
        b'VPH2Lxetvj+4PwNeX3/pu/dYbzzOnvXOZzfC3p23ovTIe2u5j/pf4vmOgD+8CvrGbhSmQbNy3U7O+i9uL5i3PLTl090vfHAwcPGMfZr9pdWdZ9/rfuGFau76g49EulZ+'
        b'81HZYAi10eWbqPz+7Smzoq+dPyc+0kif6Op+7MWG3e9/f3DOp59l/fX1s+9W//WzAztXbUz4pmre2m++/W6D5onONXXBo0Unvt174dPM3617NvqxlxrXJ/yf60X13Zf/'
        b'y3NznGKPc+h7Tnf+Y++gj+o/nTo50Ss+niX1IGi2ED7LjQOPB+AFQ1QsgwWeg23+zMejnnSHN7DEZ/l4sjM4VgXb2Y+lbCRfzYFnwRU4AC/BF9bCp50sqngXcJaN5vgU'
        b'OEYEqRREhM+QKnbFsyl+GVvUEAR74on8NhMcnY0/FB0fFyArJOlCOMhGtPBJJHPitRaArdnF8WAfOORTznyhSDibDbsRazBIvl0SOAuewRUkluPXn5sQtQBnYufCNubI'
        b'ocsN9GE5TSqD++PjluLRecg5jfA4uEoGPh0cXG5PXxqnhdeDDuazrYcweYpLxAfVCTJwKlHKRvj/OAeJ03uQsEt0NWcXFhFZN7GMR/Gns+F58LTfZkS6CBXqBQfhc8U2'
        b'mHephSfFbNAHjiwiImQJ2LcA6wwss5LHBj08CdoL50nV0aAH9MF2Otz20VYsmkbGM4nFcBvTMdQs6GcjSfxUfBo8JxX+vZKlkJqgiWcIFRcjgDE3G5XCQUKiPJgvtt4p'
        b'ElFi366MzoyumZ0zeyNGvKPN3tGfBIQOhVlfZXr7kOQZnTN6xSPeUWbvqP7kC9kD2YP1I3E55ricCZklQVjAO+LewbNolA9OZ1Tk/b4j3nKzt/xWQGhvRD+nf/lwQDai'
        b'XFFx+MsxZ5p7BN3cUUkgLtxb+ZFEjiSN6NTbYr+uws7CQ8W3A4OPZ/Rk4Ocz/REjgYnmwMRRROqce5x7xUfdJ1RyKzi0N+xsdF/02fi++H7jYOVwWPbVuR8E595cOBoU'
        b'crygp6C38mjZfQ4VkscyB+d+i9v5XXDuR8G5PxqwNYs3RF7zEnlvJArmzXRhKJ0LQ+k4rL9JO0w0tDYxhaGAvrgofhP4k1VIwYrgjYgCSr79hV9WIkJKFz+aOitM5qCu'
        b'HaHIF9rGD1L0+H6fvgs7T+M0F+bCqEZt0PfjyBPYOc1QcGzlY4wzT7mwjHzaRI+/64rwv+WflMf8sNGfjyNDkvjxU31LXXU187TYuVXf0qrWG9f/Lc9sydMlcq2SqMnv'
        b'2BgFMlfEDKX4/8n5FSYqDx5dja9ci9XB9lUMj7GITZ+7XLab6Ftnyt2njzNguJljfmT5rZDQ/qyhvKq7HJZ7Dev2vPzRBQvvc8Ldou5QyPmOh2PvcJH3bhGLCgi7JUoY'
        b'Faff5bEDMtuK7vIp/9BbovhRcRqK8c9oK0QxIVG3REmj4lkoJiSX1VaGv49E3xLFjYoTUZQkqa1gPCYLx+SQGL9pt0SxTIxfTtt8FBMYfkskYyoKRBUV/8WZ5TaH9S0f'
        b'9b5H0We4mPKa99spt4LpAe9r4a+lvF2PR1DJur1AObpk+X1Oglse6y6FXTyGSjQG7P+2ioUHH35R8Vrk2043p90KDOkxdsde5KC6FOZFj5hValxNIwsxvtX4hiynnOWW'
        b'fI/CLq4HJXCx/34tO80tn/U9hd2/6Fj+bsHfpuOOhZvdQu6zfd3i7lDI+Y5DuU/7DgcZw0iYpLHh1ShDIcLqBnd3DuUWzEZC3lHYlwzOE/ERiQ/bwXYh6DdikifEl0Mq'
        b'Klw3IgIRlMwN54PL/9LPok76YvDkR49OZYQLSoMvwqPYSmsruBBKhTqBASJs1gdwi2VgUJ5GwSfhPooLr7BWm+DzzPnCFS54avx8AclJu5lPkc9DnBUhih2IdF6B7YXx'
        b'WCJK4YJB0I9YgnZ2EbgCOjXlshM8A36bunHbr5m3lpLX39rCKukzyurkdaKUM9Mr/OJ0K87skf92tumb7q+39WzrKe3p+KC1dgHcVi94nF+Z2ulTv1Y+x5kjXHJWcNmJ'
        b'0xhA/XqDUO7WJuURXkKShTrIWGpAAh1jrCEMPEPIotxZZ/eRc3BhAyaZMyy0ejO4tII50Y9nhYH9zIE+vC5kmJznxeCoTZ8LXoA7iU63pXUtKbsG7oAn8Z01nLoMPk05'
        b'r2CrF4CeKV92urbq1YhrV1eTm9WRLMuXzvG1J0w3Z3tSYglD4Nrm3vb2Jd8Bn3u8qKfoSMkwsYyL6F9OZ0732n6XYe/k8fC6Ye+YtrmfeviM+gV2z+9e1PFYBxeltRXb'
        b'C1djXNzqGJ95av4zH2bFfSNOKNvuw6ybRSxWwC/95tkEqBRZfr/7FNU7U/iAPbEk/EQTbRC2xZ4VdzkvjFJwAihsTSyLreeTMB+FnUjYiYSdUdiFhJ1JWIDCQhJ2IWHG'
        b'mhiPWAvj2ayJ4bAQteeE2hMx3whXJCtZqSyFp6V1N0uqF2MrTJFCUsWWVA8cVvKVLkpBKlfhY4kVKVJRLBeV8rXa5LJYAMNWvzip2D4atpnGs/4pvIk9MIHFz3nAb023'
        b'/nKt+R/4fTCehBV+Mg85pZDg8tUshT9OR78B9m2gcKC1HPIH2fmD7fwhimnIpe1iQu38YXb+cDt/hJ0/0s4fZeePtvPH2Pml4/4Hx6uIlbHnsRRxMrbea7l3GLXcSxGP'
        b'4XehlJr0z4ourcaZLfkT/tb8pBUfiz0w5vmwINVJISMw4UustTkRGOApEkmcn0KulzR6I4SchhglxCSr8pHkrEG8PDXhbN2mYsDW0LAC2O5sHdsf46KW8EeK+bYTdaf/'
        b'zRP1yR+YFzAn6onB3Mqv2SL8PDBeUx7L3Kx0dduzgcWSs6mKGlnRJhcm8oj/o4nn2Xd4lFy1cW3+QoqI8Y+CLbmYXsYVS8BTliupE97EI7Tc7kQpGp1FsK+a1POb6vCY'
        b'WE4bRkh54b7N1JfWPhJspgnIhmwD5gSHlpy4VHcEExNwAJtGerfINfT8mT0VIcXu4btdOSVRfm+5N7zgVVtT8HsVdbHn/Bm5PEKw7da7iz6fnZ7BmZMaV7JWLixpjK1z'
        b'fmt5w9VrJa+5vnY+nk7yvbpStN9nx6/4X15krf/mT5+1hrw8863/CZJvyuY08qnXpGLB/USpC6EPheBl8CLWVfaCS5hx4FDOlWwjvAi2Mseu7UjqPAbawQVy90sJd/Kj'
        b'2Z5GeJk5orwRLre/qhbsYnl7Bk9suofFA3fV2gcNCDCTFekPngPbeU2rwBXGIMEeBXiWsUYUF5PAZGw3gX4nyi+IOz2KR26JwYNLkBxKvgIK9pKDZkQNwfNBnvAIB4mU'
        b'ux8l9+eq3ZeP5ykF5ykqz88THuIgsX3fDJIDXoAXskF7ogp0IQG3EO5hUc5wN/6m7QFw8R5W84ADuZWgfS2qhHBKdACqDOwvRxR4VzncJ+NTWcV88NSCDCn/Z/hovEUm'
        b'WRvysu2pieaG1lMMEV3uSU2L6OA+KcT3nsRHHkFewV0BRYf3Th+eJu9wHfWe1hs67B3e7zqoH47Juqp9q2545gJy2SlnOGD6kHj6aGQSNv0TNhoW1z+nf2GvDBskGg2N'
        b'JHaALD8hNG5iNDSil9fBPeRmR2cZ0W6MR67Xj3Hxa58x13FZStcy5qLRtZqMxGKsI1UnI+xZjqXsDAKlI4yUyLY7kVrmyWJlYmEv85cKe4f5sdQzwrS/zxqQxZgIrxoP'
        b'bQorIvarZLUBhG/ijRs9WXp4KWNSJGjcQP4kIyIy/ZPUAx/9/YW9dKu2n/qpbJ7MRBFz2RPs6yS+H5zIdDDEroOTzf/I/pHeCaptoPCwrs1HXdN3UxYE+GNwobWQ9X3P'
        b'P6s/LvjbtOrqZs2U1mtwd4pwd8Yt6vhiRRDdoG9p/qf3Q7XuYf0ondgPMekHft31j/ZiO9MLfrWxxajSPqwLFRNgetnhZRZ7R5W4oPXV2JT9+RebxZlM8nkMyad9OdQH'
        b'S7CvRntz7nqGugfNcqJKDAH4BXv8dtdYSrN3XgHXgNtKvf21Vajb4rLN/5Gtp/hPdoG3bna8J/izBPRun3NZGl7pd1DWUam6/S5F/TWdl9bnJ2Xdw8Z3fFbBAXBMb0cu'
        b'HBKLDHBoKqGKqH3GPO2pwritHMzgYaJQ70VJgroe63ysd8GIX/RoYBC+S5p6fEYPvsfbn2v2SxgSJfz99nIWolVVsO1Oouq8/o6TqH+p/uBvMJpkgY7YIB4R42ann09e'
        b'sO5zd3KP4o3B73FpFjX7POutlzVDu0+zDHIUUXnqxjhs5EmWbK1H0n6JvE5+8LlFUu9KH/cbX89OPrY1JZi6/xqP++6olH0vnsLMCjgnnBooWOBlBi7gQXiRiOLgBnx6'
        b'fR08jVX+sQkyfAS/jZ2SHTWlKO5RTR4Jajaoq2u1LXWrxvztIGhiEoGkWAsktXpRMfH4zvag0hydMxKda47OvRl+c+1wdHkHt8ut061b/b4oYhIojfHIk7qfkboXY6l7'
        b'CXKW2EvdzQiY/H+x1P0gosFaku8aKKuscYixM02lcv5XwKnhQXCafChoMRjr23qf9Q2HihmcdX/pZtEGykQO8dvgy4gDPQLOg3OowAZqA7ggJ7d2wRF4onoOPArOoSna'
        b'SG2EvSLGnMiuR+FhRtAYf/hWGRO2qiyBRaWCXXx3eCqOPBX7zSrm8aF8zbbmSzXBFHn9tGEa8/qp17nB++MlP0QssJhBuTwD9viAx62GXCe8g7JA4wT7rX2wRwAPg0Ng'
        b'YFyvmAz3JttUY3p4hWvRjF2epXkl7RuW4QbKE/Bj6KW6p9E+iXn39uoDW0P3hz6Z+ziLvbBbInl0vUSS1/3klhNn9ojMNfnnpLOz/Pm9S0SVrv7clNcqwa89uQNuDVdi'
        b'G2sK/thQ09bwxDn11oFSNfeWFwh6fdsbcxctol0Uu74OWHG13esYrQ99t7Xr+UfmzW6u33nkjX314QZR9JnmMxVLWTtXbbt68WoHpyFWtuK181dKrpTQm6k5e/3apy9a'
        b'H/3J/Nm3ar+ojTLRH99P5XAyht4l5l9n/lvQp9xPpU7kZCsS7Aed8/Jt52q2U7WDfHJyhm24+AgftLXhMxtJPANIJsKiQ31+3FS7XgB7rdRAtZjc1whMhK8IYy2ikaVK'
        b'cDEU24+5xEViShvcZkEm8DLcUwO2kru2WDhCAALOF4G91rr5lBw8ww9qhZ1EmaihKy1XQ0F7vPUNzOFyItP5BSusCsECuJW549kCngEDUq5DGQaDu82yJ2Ip1uo1RvWY'
        b'yA7ZkBiCYy4xOOa7NV5UcGjH3E8Dp92S0IRSHVzfm3Jwc7/xwmMDj11VjCTmmhNzb9a/VQdXfRISMyTNGQ6ZPiSZbiNq/V747qVfwkXO4NxLLma/rKtzhv1m3QoM6TYe'
        b'yernDQcmfBImG0osGw4rHwoqH5UEjUjizZL4DyQyfNjm1uPGhPsVH0iSRpmbmr1hw+LIfvGFwIHAwSXD0plm8cwPxZHf+qCe2iE7PoPsuCp9o8Eh9eRbEZ4F42E0pa9H'
        b'znI7jHff5PV3nGA9yY+gTgkTOWV1XEdkjNzkYFnVLETJglEgO5VrQYDcCTc5eAgB2iFEe2ULQnXcXB5BgJNip6ank003OZUxGO3KJrgNHETc2DQqy2Ma2AmeIqalicUm'
        b'bwPsikPTY6JS4EXTWh65sAB2LIC9FsQIr8ELG0BvpKZ6txfbkIun96XNl+p6rDp2fcg2/zndcyQlPaHXl38hanDrLxFUmLIVcoPzQbfwaXOcU9pcG5IaFqhul3AoYZyT'
        b'7ASFWDNy3rHfH8F1e2IheDYGoF1CrjyzqMAmuGsD9/829x5gbR3Z3/C9aojeBMhU0XvHFBsw1aab6h5AgABhDBgB7r13HFzA2Ea4IVfkjuM+k+J0tMoGkBPHySabTf7J'
        b'Li5rskl2887MFSCw07Z8z5f1Dpq50+fMnTnnnvM7YLN+9C9Q/Godiic262MonqQQig9iKH4w25Ka4NAn9FIJvRTWSqsenlo4pZn7wMa+385hkE0JHT5z9TjN7bUJ6DUL'
        b'0CE3vVF90HrMFdd7Pv9BVaZHMfz0yClbhTPNR4F0mJv+EQOvWNK0xyDipj1+z1ErRNWMobeRc46I9Tg69KaHKA6L9PQJ1en9T6juN3wF4mYx1EVIbzt8GbRMtwMtaBgO'
        b'lIMJOC5dOW89V4a/zB76v7MXSzsQHe17B93lJ6e+h+7ynLJNytaQ4NVreOtLUj4tLuaL6TfbQhKS6gcSWu9UTRBXrXE5E759eVyw2YR3yt45A+60mVADH+ufuhI8vGC/'
        b'4fOpHjXy+ZShIUPyvURLSFY6hDSaTKhpspaa5llSggm7YxDtDNg4y90Vln02/uiKP2DvJOe2pzUnDwjd5AWKqWphaDNX4+512r3XJqjXLEiHsAx+A2GN77bBKJ2NSKxq'
        b'cLFaFNTqktpcTGpPfi+pTR5PaiNvlBpKV4JMXm162pcb939CZr/hdjdMZvhybgZOLcvznwH3hqawKbh/CVePBmvj4GVptv5hjmwSypG1Mvti6SFEay9jWntP+I4A2BuX'
        b'xcfxj1pkvy54y1TcK5EUr36U0dowIBTmCyNDKUnLZxHcV1sz0cuK2IOvMYaX0jN8QY/W+DYMnkJX75+lMe4wjWlNSou07iq0RCbUIbIxTwid+WnprHqEzvptnOShZ9gn'
        b'k5XupzN6wlV+8WqvhF6XRJVNYq9Zog5h8ccRloZXLi5tqK1/4WHJ16Eohp6wEKK+AQWLdOlpPqanR7+TnkjtrTwvSmEYyvY2ZUwYiTEjMWvEBo4a41Hh2XzJEo1xU21j'
        b'aaWknsxE8NhoiMawFMNkSmoaJPXBupEQDb9MKmPwL7F1pIbbJG7ATl0kjQ3ixcQ1Cdbm0BhJFpdWirEjDpx0geTEiuXBGoNhfEtpmQ4k10WSo0HaUC1B04r1TOobcdCE'
        b'gxc4m8nS8LHDSFylxhD/GsbBIskEhpa0F1K/nMaKKBjUpqR2MYH+0nDrKmtrJBp2uXixhitZIJZWe7M0HCkqqWGXSEtRRC8+MXF6QVa+hpM4PTe5fjteqR30OEYMzzm+'
        b'Kj+po4YNKvdS5LMS1ivFJwNVYBDG//+GJbN7btOWMizZZu/l9HeszTb8IPHkmQu5zCa2K4ftMnjFtJ5LwXXwMAueoH0Qx9VNHtbCfZNlDU3oMbycW2JIU3rwAMsk168x'
        b'imz/FnvQBk/44gv1Wa+UzIDUzBy4OQuc9YO7AtNyUvzSAhFfhS7ywzgbsGWuUWJdBmEFwSWwFpzMhnthC1YQWkplghvp5PTKzQA7Q8OCOJQEbKc9KdBisJzYVSZj1p9F'
        b'4c9NVCgVWrKMuTQdzgXHUXYWBRWRtBcF9ghoopyfNdN/2OYsHWxHly3DOSx4DpzyZYAm9syALagYj2oAO2lvCuxdWMYAgDRnm4MdsxiruokcigvP07DFA7aRKUynfal8'
        b'qjnYxKzY5ahLEHPcBpnDA6gqmsqro31Q/8TgfCNWlgTnQWtAeoB/AIahyfQHt2Pg1gyasgHHOHEF4Cip8D1/ERWHqjCtK45e6V7BsMkBcA1ch2pkIx5zH+1HgVY+2ER6'
        b'l/0S2xfDVaYylmh18IQp2MEucUonlZ3ItKH8qHtFJqLi6BsLwrQ8917QKUaV6VGIP2qn/SnQlhZKVtcLnJqEOB4/rHGL7ptbOH40eCUY3CR1/b1wCrWcKp7JDioOeS2J'
        b'pogySRQFW0PDgJLYMGylAyhwAJ4FlxmrhrWwayk2J8xEnDk8YKgfzAKt2V6ksm/z0qg9VG+ukVmxwd/NvSmyBLNcJ+O6OJQ16lYght/utGVAO9vLQedSsJYxFCBKjxtZ'
        b'rrCngNS12gkb/W5eRcUVZxRZz2OAa/RyvULDwinKqAlP194lsIPor5hi6J50jOm5De4kZpJUHuwwAevZsWCnH6mucGEkVUfJZxsWF+c+1lvGdC0eHBOh+hCx7fDHo9wP'
        b'T7MItE6xczpTXdbw9zuasgV77MM4GE8SdhJ6mMPnosKI3HfCo3hgrdlcgmlkiwiiRVucWT94BOwyqWNHusB9pDM3ai0oN0ruqk8Vz0uJ9GF2KHwFHgRdoSGIVmEzVOAB'
        b'7gM94BJDrooi0D0nUUuuLESuF2i4ZyHoIuPgAqVb6ER0G2/MpENwsTZwlZnig9loUMfgbt90bItBUzwpawI4Ac8SklnWBFpCI1AxeBgq6Ug0AndwhpRLBBfAQS0Fbq3K'
        b'B91oyqPZZoFhpLlpqFsbUEEWlWJKT8LE0SJhYFrXwXa8AGTGvPPgRXCKQxmZsa1SIsm495noU2ZUpZFecXH1A7cKZhHA8cUzQiPCsFWIB66tjQuPMZ2/BXb4zIfnUD8w'
        b'AE86IpBSlh24Yc7Ay/TArbj7YRxKBOX0ZAyHdADuY5BcO4ECbE5Pxx9AwYVZrFo6DnaHk7fL9EA3VIZF5ZfT0YgCuZNJZfGJYGO+dTp+jW3Hn0R5lix9cKSQdPq7acuo'
        b'p5SylGNWbD04sZzZbTxwZTG4GBSG1naPA52A+r4KHidVzZk8A/FaafjzLDzIZ8NbNGiHncGkqv7KadR2qqeGLSr22Tg/niKdLQmCJ3FVKP8FuIZOpIAcrp9AKKwKXs1L'
        b'Ry8THmU+j1VIB4I11qSey9OEVBC1ORxdL+alpS1g5rF61tL0VKw7DNaDNRwODToq9cmQQVdKMWxBPd0Qge2p4sIafchaYZgQbPicmxILd8Mt0/1nMOr5cHOmH3rxoHW2'
        b'0LPjgYOMDtmlfLhvBHcJ7fydPnzYygJ74Y3yUVdKpb7Y+kqJ7s3FGcstZ2rRpg4mVMEWHurHRPTa8gO7OQTpCh5qgBvAWbgxfdw3cnSycCh3cIrbCPeXMtZSB+E1S7tc'
        b'uC0Hm+pzKI4F/dLCRcxS74UH6PR8uINDLc+jYRsFlcZQi4+1GayBV2jX8dhhNOU+nSsNciOzNi8HXITthpQxUCCCQ//gmiaiLwjljnPh6XpfNCOZcGeKfxrDQQdzKI98'
        b'bkg1uEUGnJVhS4VRQWGUWfG8rMmLmJUoBlf9YbseBTrNKXCbwhBGXQSbAFwHrWiQVyqeq5VFeRRwQ0EzvMi8zLtzZqTn4KO0J4fGyFQ3we7Z5ElR8sI8dPzuQMu8I561'
        b'jLaHW7QagLAFdsWkF+CZqAMbaXgcrdkyuIcMhoVo4uI4eDYa7fciJ7ANqwqWkLnEen/NsN0YvVkNKXAD/UPvujPkjCPQWnhjB6RmobKp/iEcyg4cmA5vcqr1wU1mlS6i'
        b'98552M6mbKGcAjexVH8PnzkiT5mljCnNQqXb4R4RZwE4C44w74Fj5lK4jcgZ91FSSoqhqBi7kL3wpn46WsGRjpsUm1qyqxzgJoYNvgAupWAJDNjkRzlRTgloJ5LZ7qbA'
        b'WV8G9Rl1nkhCaMoeXAaHwVYOenvchNqWW838YDvaIGvRqXkd/ZsIWwnlLk7EQml0PKD3CTWfms/xZPbCRbgfXE73908FZ7zS8JZLBucs49hwT5k3Q1ToMF4D243QLpmI'
        b'bkDon8OsRkbGegodDTrIRTFwLwEv2utPGkwryJIZG7Oo0uU02oDwbBVzrj7JMqAEVNx8A7PiaqPCaops68U26PqwjU35ZFK16Aa3Jo0h20Ogg4vuaSkYpm17+nR/0r8E'
        b'cEhkx4HKmUBB5OXRqe50L7s/2YCKq/k48rieHbNTs+YlYLkUOFiOZfZwN9gu9ZLOZsnwN5TIqK/27pubp842eyNCmnfAhavZulbEPfXw+Gf+irvWOdcW9x18OyZJtbR0'
        b'6hcbvtpmeuuHCU9/WGpRHz7hvQDPphMtX73300/3P1arP352epVzA7u3CDxeRC/9MO37JZ/wKtcpL967ejRFyl/3cv2GP95RzT68dM7Jt4x9XvFZ2685Sxud9Xp7sl5Q'
        b'3flTF+rW5oD53k1XX/7iHzXJF0pWmRa/8eCnQ587qG+GTMp6WmTuenjFkSO2k7ZdKP100rUHRocPfLDr9aUL3/I9pLBvqYhKffX/fFqEEWYeQuBmYctLaHG+1FyniWst'
        b'4Vc0130Y11rOD02JrBC9E7I+yu1ghNmfJyRcH0wNCFqf7OY3ge+wsY7WP2HXuNvZz+ZWjq/Rp7mfynreMTsn+vTUml4Jv8+gA/ok9hS21q1z/igJ+LM/DU8cbFaWiz4S'
        b'8xftrptufuND1UVjPbMZL7d98Uao15mT0g3qK65H3U8Kd9dO+2r9j4Vvm4Vtqf6/N758MCehaOdXJydXfhU7oN7j+PdVbxp83uCU4frTyvC3j1dMHSr+4l0/17NP7XIL'
        b'3j5tstAu5Y1qcXjn058qv5l04e03tww9nltSqb6e8vTktx6XnywNu/DaxlrLyUtfuq8ydbEbslgxP7xAEjUn5lFsxtWPym/9a/HbVbO//yzn1Irl83wnzxJdqAn+Y/Wf'
        b'HB68+U8DLxCQuPiI5at5N3anr//T7FuFj6K//Tz5blZhSOMNly8nJy9+1+xBM+ez2M2rnfmf3dYviL/3nWv9/bz1V3+6LFY4Pghef3NtzI2KH51ejYt6bVqicYfw9Ypv'
        b'PjN8cLL7tOWs2d9Xp9e8bzBpkvOF648jflLHVivu0T1T/kVn+Zw8eHa5tyVRoIJdlfDUdKj4OS0qbmWFJYPhsToNdPriL0XgDOxhgQN0JmwG68kzMbqd7UQXMcSt8KhK'
        b'qOAk0eDmolVE8Qr2gGNTwDbTOqN6eAnsMG0y1udRAtAB97LYtSvAfqIwtQzeAqsNwUm/lOGvHrEzzOErbHA2CJwnmmCFQA42jaoow3VgHTHrgXvAGfJlxWh2FdgWqLXs'
        b'AbvBJT48ykKv1v3wJANL9vLCXPJxgxHRVoDD/ExWGXzZ46k5YWHyJqB9TFPRlqwmOn7OElJnCJqXHUAJm4e1n7Wqz+tAB1PnLXSbuKyFLSsELxNgE3T7VxIDqUQXP9g9'
        b'a0S1Deu1ZcBTZLxgLdwYMfqZp81pFFWdvYyRLF+Am5eOV0WLAoe0qmgbJAQdpQ5cghfGKaPBQ/CsVh2tDZ57SkzDD6NDkWi/4Y9z/uiyA3aOzASq/LxvFBdcAetdiV1a'
        b'qP78F4m0J6Rz0GG/P4oshxjNzFUdvBNqFjjBWPhuKWZGuAlsdUbVDOu/gRawntGBAwdj/mNjq7H4HWxxWZnGeFQchaJEBnWXozUHtqIcXbTYXqEqh/A+h/geFGTdmd1s'
        b'8JHAppXXYdhm2G6sFngoBH3eUSrvqB4flXeySpDcTD+wFHxk69rrNvWe4P0Jb07ozct/217lVqC2ndErmNFv6SC3/sDSE3//Sd+djj8MoZrkyYpQtTBwJHYyVNGklKoC'
        b'49S+8WphwmiucKXnySk9CWrhFJ00YuJVrfZNvJOrFqaMf1CF6rgTohZOHf+gXO0b01M/tnryoFLtO+WOhVqYNP5Bhdo39g6NSjz8rW0sUPsm3SlRC1Nf2KtgtTD5hW2w'
        b'1MLE3/xAqvaNu+PygqrIA+efG8eLqpKofaN7UHfjf7bE+JH/7CSOVPV3fzsr60eTKKGL3ENh3RmgdO2zCVfZhA94+5+UKUN7eD1N10zuyO6xeiPT+yJzVJE5vbkF6sgZ'
        b'6sCZvd6zWnmtTW0m/TYOreW7V/bZ+KhsfBRl3VUnq9Q2keQjZazacUovIgc7p47YjljFDOXUk4U9ZbdrrtWo/TP6vQOVvJOOrZyDJr+aYcDBRR6u8FK5hmIsu6laApWz'
        b'uvQ69R7ib5m+KqGvYqoy52Ran19sT2ifX/Id1ztNamFWv9Cxw6DNQD5FLQztExb26N11vVN+r0g19SV1QqEqsrBPWNZbUtYvdOhky6cqpqjcJqtF0SphNKlV+3HK+qrt'
        b'edue6ergjHto0nL6f+mRg5wnb+o06RNFqEQRPTy1aIoK7wem+liV2yS1aLIKm8+PryNTHZx2L570+GcfjQ41UfsoTR08jdlXLyqD9uL05wcyTR08QvfjqktXB6cMPxhT'
        b'Ju0eVx2c1ZudoxbmPl8sSx2cfm+mWljQL7Qb9Lbytn5CWTnbPKWsrIQYp2bC/vSX0+XhKoH3Pl3zFENGMI4vv78PxQW/NZ+DcDmKpa/HUHBqWE6OPyvnWNG0LcbH+z02'
        b'LERO3sbzpk4aho1VmB35/lJJMSAB5MsLFuZSBXojX17oMULc/1SJ7zkhrogaL8T1ZIS49wvY5OtfEG+tr71LKMV8jiHcSgtitI5AhS9APD3lSDkCxVIGhvkq2D+Bja4r'
        b'LSgygZrgUc4knwPdsBPcXBWK6guhQnz1SAMfr8SyGCooyAPkBxfHUUS5hmvHZxLDzxRN85/FMPV/dl9Bf8eiZikzpaIjwXZacePBQqPQMA6FGCTENe+lSsFquIvp33Vw'
        b'bVpoGI/Ki6PAfkoC98HTjLPmSh7Bcw4qD+IdmefHVP4uzxxPQmSQB6dWHhPKdKOkQptoXWzVlSJgcgp9jCghRXkFzfhj3E23GCbn7CnaxPJXC68uW87kvB9jiNglih9U'
        b'vrJGFWjA5OwN0CbOyLXIr2lkEt9rYiCmg3jT2JfpOVq/Pgf8XMCeuYTNLsCyCG4TDV5Jh6cYgcON+WBtaFAQh8Igfm1u2HfS1hmk3Q53FyoJr5nzFsOAiYUMT7UkBrHH'
        b'4MiIItSJFGb+toJb6Ka5wRW2G2AlAvSvzpYUmCpqWo4uYe08lHwV/cv3ZLjcU/MrQGsDxN96/Sl/dLlsJo32eA7rQ62yGjSjGZ2lOLiRMgSbYQvindH/uBSNEhDjuyGU'
        b'LJGQAC20c4Y/HEMFYqUJZ7slIhFdzk6MmgJqlZ0U8AzT7ZbZZnn+mHOlOYh/3k1bBMBtRNUB7HXJBdt9tNgM86IJj2oFjsHbpiJwGk8EtSTIgRHKr4U3QA9oSxnWApsC'
        b'1pB3CVmTDWkMFnjQ1AlT/mHUyAA9mT38ct19RkWRXsiWGsXlc2VNqPMBb1vcLMBY0ILl1y/x1/L5m607Z2y3nXiwp/kvUwYvdHsUpm7/6Mb36T/erklfdPcbv87g81ff'
        b'e6d9qO1Z1I8n8j32vOXLk8X/A5Y8mnrpg1rfNt7Wj6YVzNvOTbdi3QD0Jk2XwfIqxPjvOnX229XevZdPeWT/0dr3iOfCuTcC3XMy5n0i+tv8z4POlv0TbJ1z52rwfu79'
        b'NdU57W+cNwz6oFT9bHH+080fLV32yuUz9xf+1drj8MkJDg3Sufvf2/e2/Ni2Q2aL0qsD32o6fjlx5mkXs1UlFyJ/2OceuvNf/n+a8zH70b8MHdifPHvP8PLcd17iDi06'
        b'9cPtD9Zs7SwP1HPccwCeDN3kvGn5jHkOB5I/KwmPeLQkbtWOP2+eFt2a/OxWd3yEzcaJeW92/4XntSHne4FM89mjz289vVH4uPtdh4dv2N5etHBHrHyptcU34s++cX79'
        b'0YlP3vi6vP5894W3/7nsS84/Uwdv3+tZuXSxdaOT7IuKC0+reK1ffdjnOLV8x80/7PnaaUqV3tw3a254C4n2L+yIfLGWpxM8raP9ywa3iJLnyrqV8HQTUfLL8vfBdieX'
        b'WWCfpxdjq9kCj9fPjdWx9CQs1Ea4nsACmfqEwNUShp3Q2unkTyYsQYwvPGSbjBmITCzlw07IMDBhPBucg9dAD2nZDbTB1Ri9HmMObqGTbTGkhEteDmEzy6aD7T/HYooW'
        b'cythB9jEoBadzamaTPrgy6bY8BwN5DTYSRqQzceiU0Z31TCR0V4Fq8EGBkzjCLjMIBMxGIvk6xDolFjP4tjB3emEFQ2Ax+GRFE/MBWqdohNxvYU7G7G0VwFj7FoGL4QO'
        b'82xwPdxK+DZwg0O4ssBVcFM03DaeL2OYMqAEtwlb2FQDLoVN1+WOCGtUk0J6UbwUvdbhlnFcG8OxoTFsIuyTPeKTdsdgG6IUv4AA/AkQ9ROeZKOXzTp7xlZpHdg3cbxB'
        b'kx7iLI2wQZMV6GZgNnqMswKXkmw707kUh0WDw/AIXM3AbNyAbfPBPvjyWDjGWlPYRkgvLhWs8YS7fk0lcC7czFR3FHQnwk0TR9lwhgV3AFeJ4iLsAvvhPtAMbv8MJ0q4'
        b'0AUvMfAju2DLRLgevdNHeUiGf1xQTEbmD86XO4NzDAr5MAQ5fLngN1lM6aBEaDjY9EBjMso+4jjhH/lsBhd7jg0lsGluaImS0y2x/XYOD80EWIu5z8xNZeYmz1GwuvVO'
        b'6vULbMk/G+1du0/gje5vfYJAlSBQSasFIcoQZWivIAI9ZtAZFa4qgX+fIFzp1ieI7XEbEIjkgi67Trs+52CVc7AyWC2Y2CeYrBJM7olXC2JHavVRCXz6BEEqQZDSXC0I'
        b'VSYoEzEAyC83OoC4XE6f0Ecl9FELfPsEwSpBsNJZLQhT5irzegVR5Dm+9rdMZ6pQoId+ilwFehg8vsd5SrerAecD+kJSVSGp97zUIXl9gtm9M2f/u/kilO59gpieEJ0Z'
        b'CFc5h/eg/k/qE8SpBHF30EgT8WN7RT0aVJ8gUiWI7LFQC6KZMk6dTkqX0flKUAumMAsxpp1IpUefIKFnKnlkwwwZMXnMxV2NxuyiCO4V+P/Ks5F1HoywD7Z4Qtl7Ww5F'
        b'UgLb3eGtXmpL16dR9ubug5Moc6th8vjAzBMRDBP7wMyj39Kmz9JdZemusFRb+j3UMmZcBafPa7LKa/Iw5yluM+0TBioS+4ThiK3k3Da8ZviETXsn048o2jkZI1hbTcU4'
        b'D+ZW+w13G7YmfmAm6tdtxcZ2/+Ldi+WcLuNOY7VNQDNHiyYqd+4VuI3oq/YK3PvdvLoyOzOVLiq3iX1u0Sq36J6ZardkraJ+CXY1Z2PXbPi8fs5vwGQhyjljIFluY6bj'
        b'Dgr+Osx0/AMxHbNtaNoCK+f8LnsQT9IZDb+IMUGQ1cfjytNwMI0mapXEvrA+Cadk4iCGxq7kyC3fm/4KXYN+IlZMX2H7Ee8JL8JaYcwKiX/0SBxE4WASrp0/bAY2/Atr'
        b'vRBjKMbehdgpENVdoktJtNywapLGqCg7Pjc+syh/dnZynoYtkzRoOBg0UmOofZCXnJ/HcGe3R0BZ/iOB2XPwKtidHgmwxbVsNYvAqwzxTDFuCgoeuVAC+wEzz35ByCMu'
        b'SxC2OekRj7J3GzAL7BeEoRT78M0Zo+gpoRg9ZSJBT9ECo/hhYJQAXagUH5ziR1KsHAbMvBg4FavgzcnP+GzjgCEDlnE2/YxvaDxlyJZjHDhkxDMOfkyhYMiMbZxED1I4'
        b'fGRCOTp3Cjore+0DBxxdB9y9Btw8Bzy8FW7yOejPSVdFmbxw9Iebp4IjnzT8x9lD3iA3Go45OsvdWucMuOCY/YCzmzxfbjDg7qMIk2c8cjKztxh0EUyw6Bc4tMkG2ejX'
        b'Q4FdW94gF/3COLzOnaGdMpQ1YFAPp/ApK6dOS1zDoD6OG1BWKLdc0Jo2aIjjRmjIbTJ5WGvVoDGOm1BW9r0OwYOmOGI2Wtgcxy0oK5fORNzHQUscF4w+t8Jxa1S4rRR3'
        b'ftAGx4Wj8Qk4bktZOXay5UmtSwftcNx+NO6A446j+Z1wXERZ2bYlyjmtkwadcdxl9Lkrij9yQ1OOh4L1QlGmx5440d3T3gRRQD5N2Tu1LlekqpzC+5wmq5wmq51i1Hax'
        b'A0K71gyFtco+qM9+osp+oto+Qi2MfMRl25lsTh8ySKCNfZ5QOBxKYQUZ2z+lUMBYghALiFNGTrr3XS5lls9GF7f1c8AxcHAMXz/s4fwJhgiJNR8HlMGqxyASHBfEpc82'
        b'Rf/XI+AIpmNjeexxcU6UniOV50jUQ/ULTMM4eVwGpGJY2FDPnccbAdjgE4ANHNdHcQMS55O4IYobkbg+iRujuAmJG5C4KYqbkbghiZujuAWJG5G4JYoLSNyYGUWe03BP'
        b'86wCcF95ZGQGJGTl2lPP/ZdnTQAcnJ5/Mh7A4Vfqsfmt9fjr/E6iw+k8UQGLiHsYzT1D7NsyTD9vwrgZZTzMm5DZtiUAEeajK5dnF0UTRV029pIZxs2zxzlGylrkOdRb'
        b'Vgj1K7ydNXwCt5aelSx1Rje3peUEj3c4TVRaLZbJRF7YI3mTpF4mrinD722ppMbbwMAnH6M6Mj4BsYvL2hJZbbWkgXFUiZ0ZVtdipUvsLFFS18D4tyRIkz4BBvULKay1'
        b'rdEXlzVJZVgBU2Oo/Un0KPmMzziUzC4rb9Kw59egtAWSMmnjApTGr0O9WlRbX1bKH0fZRGK1ltLVkB/2GkoM0/DMctCcctG88Igys/GIawl+vo5f0Bp9R6pAx9VEgf4Y'
        b'0Rk/Xp8I1J5L1bXTED9CW8wgtUbaICVWf1p45OG5ldbIGsQ1pZJRyM2RyZikheQcdd2JS2r1SrFnTq8ERpuVccDuzTjJixdpVYoZpGRRYx22Wo4QlUkrpA2ygHGtMC7t'
        b'te1g/6K/0Ap6PNxGjUhcXVcp9n9RU1Gi0krURCnxAjriRVO7ki8eE/NU5JWJiAY1OexS/hdHNHH8iBCJMA4gk6bOEFWLSyTVIi/0U9cHpnfAOG+UZFFkpJWxXSFz4RWi'
        b'MxTvkYYQGU4SZRCcI1xqWmDGiO9QZlhor+SJSyuxN1DSJnHGiraIFhC1saRaUqbdE2NLZaOwtobxI4pKEjxUFGdGqt1JzJykNox4UxVrp6VE0rBIIqkRhYm8yhiHlN5k'
        b'E0aOdHx46zDTxMRE0jLthIaOn9Dh/aX1wqmNieolFVIZmhG0l9GWJ8vpJ2rUTmtjDfaW+at+5U0ZKfIZCgtSK7NM64r9ejLMtFaRW2nesEWk1kNDNjGJHJVP5IwYRSJm'
        b'v4Om4IY4IzN4LZBU6p4qoLyofhc6rjg6w7OKasRmS7PBBfDKaK0XwKEX1kx8wOv6m+uoM4LH4EagJFU/XWBMCalZngbZxRlzqidTjTEosSo3AFUMj8B1z3dZR1qSo2vI'
        b'2QM2G2JQzuWk2n+YYzHvLL6JqNjoUqgX1RhOYekV2A2vvHAiUn3zSGUcuFNb32q4Sx/stYbHSH0PHbGY3Gu2XnFxRudKY6oxGp9FprAV1VYpe64+uHlUNDWul1cMwVG4'
        b'3p/Uem0RllAL0zhmxUbx3rnMYsHVxnATHv4pePi5ir2GJTBjan0FnDaEm+uzpVdKX2LJTqFK9OhnG96PMUlwNtIbfJx5V/j+Q/158+yjX11WnWUyddMi+5vdlX4W1VWW'
        b'IPu7nzSlK+NS53pdcez3XWzzMddG7nPr1h39ldsK3/+6Ti+yYnVL54MzJ5flJP8xOubz2c7vBy258vbRaxNDF/3waOGNh5GvPzpU6lG2Mi82oEb5cvGuLdzXtx76oqqw'
        b'/fICYasxlJ/jWk2Y2Fj140Wx/ZkdxZLX56w4+7Fvt3TmnfuWtynvR7c53gZExmQ3rXJYXjYPnNWKzLC8DDSDDSSHDzgPLmnVFMCeaF3n775cxj3L7YKpukI3Ri/YCS3S'
        b'fn0O7AaXkolZa0pDAtgGdhq8SPB2cRKjX3J95gotOl1pBgNOB7tADxFMzqxarJUIxnEZmeBseJBIgaYjer06It4KDiMCrkhwksgEM8AuuBk93BvzArlllTeRM5WATTLU'
        b'tQ0NzwnaEiY8xW4ml+tNQddRuC4ZC0XhRXhFRiSwKJZB7qf+PArtXz1wKFP0X+bSCJSP+fAZOxbJx4aBkX20eALl6tFZqvA+WqN2mYhBeAYsrZsb9q/avUpt6alwVlv6'
        b'EtieaWrblF5BSr9bIIbtcSaZ+my8VIxjt3i1pT/Jlqq2TesVpCGOqDNPITz6kto5FEP5MHWu3L1SbemhMFdb+pDMU9W203oF07SOTdrTUU59JueS3UtaYuWoVnfGR5za'
        b'NqFXkPDQ3olk+V2VO3t3OXY6qp2Dfz2rq3sz549moud9YbyH2d33cdCLAxUO/oADNQ4++HWztREvGONM14hw4FMsVED3TRl+P/30HTaTnEDTucTVWO7vcjKG309HeCHU'
        b'BcOYfw92qGIYMmfk9vVz2EOjZDUMPVSAhqADoMPc7YYvWC8A9fn3YYe00DFGRTq3t58DkMHY9bNwz06O9MxxXM/IHWe0X/8Zps7wDe+X+jMX92cUU8eJ6c/wleu5ifpP'
        b'VpJThO6Dv9SXQtSXJyPgOrMPzGb6ZMf0SecO+R/2Z/1wf9C18Zf6I8Zz81d6eG68Ri+Y4vEIUbL/uFPlw6s2fCX8pZ6VjV01Wyzu17k9/pcWTL9o+Ib5S32peL4vaLVG'
        b'7qY6ffFmEWkjI3ccsZfLKmXrtI7hs4nBHPFAqK9j48ojTCJ2xqBPvBBiH4TGBSZhRiMWr3r/XYvXxgLUGYP4sjLsGqdGskh31dHuIE5ykhFTwUQwpy0uK0NXcHRxF2t5'
        b'KuL7BjtS8BNV1Nc21jHMtlhUWrugRFpDfLQbIHLyGUEF8/ET+egCmKE4wUhDmUpqa+fjpjGjT7gIplnsEX6UUx2paJIor3YB5qcYOQB2CKHFDhOX1DYyrnzwGknKhseC'
        b'eRjsf16Ch1QmLS9H/AR6BzCczNhOaueDuPdBw67Quq8oG2GESsU1hA/6JaY0OFyHlRN51dYR10PVo0yd7jwwDM9z207kFV9SLymtrGmsqZBpOVTi1IJ0ZHRdZDJpRQ1Z'
        b'mgAyRp2KtF6lRFLdXksRs4cYO1LLMBMXTCY9PGqEl8M1B3v7YUmLqExS0oDrRTlKERsmxZHSYfaSUIGU5JdJGsjYI6PQmk3FdrREUjOetKQS2aSRNUV1Sxu0GZh5ICkj'
        b'vKpXXm11NeZPa71FPj4LMMOOml/i4zPC6ZMejamBSRqtYhoabo1/YAp6v9b8UlUMwpmW/ayVkQ5rUc9emB8TK5Nbl3wDRJkjnDIh59qSKklpg4jMIENDedMjw4OCtVIs'
        b'LKRiqDfgxc2MsVOeNE6i0FQrLZWMEEyCpFpSUY7zeYvmBoe89KIqQrTT3ChhuietIR3BuyApKTNz9mzcU+zuCne1TrxkAXGOJanHL18/0QI0LyN8t06DIWMb1E4fhjQY'
        b'O584ZaxUhKGuwGHKIs0yV4UE1GlM+7gMqj406KXnd898yZJhGY8OmaFURKE1MinTaG05qVVcVoVWhowHZyAevsSL8W9mbzPSnzGZZEQcJS2tbJBW4K7ISiur4Q30Zqn2'
        b'njRaxl+E1iWvQdKINvtIBkQBUpF2CGiHLUAUmVzgny9uKJFgEVyZtiRaDsZDTnXjgvmSynptcui4ZFKbuLF8aWODBL2ZsMtD0YzaehlpVFsmbJIovrG8UlLSiEkRZYhv'
        b'bKjF78f52gwTJ4lSa8qkTVK0+NXVKEPBApm4YalsXM+1ucNf1IVfH1DEi4pJdZpd8MvNRr6o/C+PK4oMfHRqxs0MCfKZlcaysnHtPreSut0rr0ete+GxjtQpLlnaWOE9'
        b'uny62UUR7qMLOOZBcJT76DLVBIpHl2RstnD30ekfzYYmdaR9nTyRuskjTUeNyYzaHXlhaZEL0I7R/iLvZ3QGo704vNW98ph35MgLdhQIYZIoEUVETAydGV7pKCqpQf9H'
        b'yyrC75zIl54vFjK2WMi4YiFjihE0BeaVMSM+3z81SeRVkNeA/uL3y8SRbCNoC0zW5AKyk3GCyAsRpXaJ0bSODqOxHh35pehtkaj95SfSOeuSC3JFXjPhscp6RGSorbDR'
        b'pnSAHEYLjyRrGx0uKpvfWC/zHnP8/dzxSY7O0ZNw5AiLHyOmffGZQKAkJomy8B/R3JCgl34+WwiTLYRkG52NYQwK7ZGpjeMLtu48E0AKlAX/QQ9eMhjdJSmS+vqawKn1'
        b'4kYUVAcETpWi02x0V5DHo3sB5xulf1xgdAPolkRUn1yJDhW0l0dJn9SFzpwypprhzqFTUyJpwG9e/BcdEOFjzp+S2sWTRPgjEnr/l+NTEiWgMQSNyYSRMphc4moRjozJ'
        b'USptwASDwjHHDwP/gZ8wP0hBP3yu+4cGh4ejmR5tAyNtoAbwnzErUC5GvZuKiFY3kWBxoBnAf0Rzw4PGbwvtltBdoWEUkEmiBPSLOTnnhkSMeT5CWiTL2M8AY8Y7jB2i'
        b'zcnMx+jmxAgh6AhJiM9C0zG6Q0qkpahAaiKqClHIr/jA1IriG42wabRZtR5VbCSqXKD9onwGrIensfraRvDKsGk1Y1edAbeTcsejiTrsYoO4Yr+h2Q2MzTg40RCgNfbe'
        b'4kNsvcFheIrkT7K0pvyoXkO+qHj5wcQABroCrqXBfmIDfpHYgMPrMQSqAKwHV+elj1oEG85hgW3gIjyHerSbVFe/ECt/1wnYQWK7XY1NVGMgLnYAnINnfVGRNOw9A2tL'
        b'gjNpmQxoIwXPAzncA7blUovD9Cti4HVicmq+dDqBaFRGTRHcn+Vgms/ItxfCwyYvgmfENaUwUkxdhEa4A7QZgc4qb7A2nAjSpN8bnqRleojztEr486Hst9NgnCBmUUjL'
        b'tJZnlhpbg1fUG7aUnBQ1nG2dTDufXn3i9LPaH4tqNRm+2wcig4wO9sXIOi7WzrrZaXfwvS7WvmLN/BkfnuFKi5y3fhKtt2xBi/2HyvC1A9LOrDN5l33jE3OO1Zd2lSpV'
        b'Cv6DT5XC7P35juruH57efcn7k0V35t5V9cq++Pv24xWzJnwy0+hvKeWapC/Lt8x/lnz58/t/iY3Mzgw/XfLJdesFP3jFeDz+2xSrgB2e052OZK7xiHk/LfDin5XxHQt9'
        b'Lz74ytlv2uOqrxeFOUl2tbf/I8Pkvb+WXZ3rI93icK63bOe23iyJ6Vvv1X/w9R+2cJflODT2cwwbnjpNv1DW9gPtPitomrujN59In2mwbbnWNDAYrtFaBxZoRdNmBhiA'
        b'jpj+ASVcy9gGXtIqyzqBthRfuGV6KjgDj4B1HIpXzXKB15KI2J0Nt03RxYCEm+Berdi9zJTANfLBiVBGSUJHJM0zf14oHQ2biZwedoNjQYY+oKN6LBbkMBBksj6jRbsb'
        b'Xpwnw5Tg74VzYVfnAnDNHDazgdJr3lNM5iXwWFZ6BlA2ptIUK5f2AddivE3/m66hTKkxNn5jLVY0RiOSy2EzvzRaC5DnSIn8+pyCFAsxgr1da4Pa0vWBnWe/p1erEQY5'
        b'c5M3dfop2X02YSqbsAFP35N5SktlWU/4+eo7oXcSesOn9YVnqsIz75Wqw3PV/nm9nvmtnNYZbUbYOzevLZrx1r07qd/KUe6mtvIgVfu04sfY8Xf7SIbPsVB6ito2rlcQ'
        b'h53NzFNE9VpPbGb3W1q3lvU5BqgcA9SWAQSIss/OV2Xnq7bxU3LVNhM/cvTp9c1SO07vFU4fZLGtggeConrceoOS71j+ISgZK3ASEyNLldB/kMc29ycKjm4qgZs8j2h9'
        b'+v9B4K8STFRy1IKJ3z3Vo+zdn1A0qsXRV5GodgzqFQb9MMhGCT885VNCZ/TM3H/A1lPBVtv69Qr88DNz/+8J3iA0tk7iUNDNKcmRepVjkGTHftWEn2TNftWai387GiRN'
        b'ZL/qxU8KYr8axEW/GXG7KSNuHxVYYdDZ32WpNI4KxjieHmO3xEYrX4WF7rEUg++VY0fTwVjkHozxCYN/jx4h9mD5YsxxAgXM0WKOcwuoAt4IEuZ/F3d8vTerfoga5wfI'
        b'6blTzp055a5acCh+2ccs7G5kWgKbMaipAM2gQ1bg2ojhO3ZwKLSp6RXwOLioA2WogB3gvCGaNmvQNZOa6Qu6yUG3EHQtz2NK0fA6JQU74SWTatKUnRM6marmsbC/khK7'
        b'GYxxVAM6UQ9g4yNqCVyDrY+mwT2MFVRbBtiIDZaoVENsrlQRRSr5ppxHGRl9yKNExdUPTAwZ+6FlSeZou2Zxqbriak3jcsYspToRJc76lo0SMyoMfJmcd5yMKKGoHTtS'
        b'yVg1zYbJ+fdYlJhymsKJ3VEeTE6Ya0gJ3CpYlFmxUWBiLZPz0HyUyN/CRYnVLkYRTOKBbNSl4iGC1P44fAmlhdFysM7Lzs5GL/YkCtyIAmtyIDND4IwxxPZIaG/Q8BgF'
        b'XjaBa1g+WkQNy+i8bJSsyKNY4AQF14QwABZl6L7QlQdugV1jbZzgTriDae4wOAFuYiunvAaKJjZOB6MYhAqwAx7F7scqxM6UM9wAjzDWPzsCQTs2MDNLCqFC3L2J9Y+L'
        b'PbhF7JVWgP3+lL/RMgYkaGcTQf7WsUyaWQYuw62gmeCY6MOz/LxsERsDiljx0BmyFnTCljhi18QH57zQKXLWcJx5UoeMsR8iS1qrT5kJBGy0RatP09OZSf3cDyVGz2Xh'
        b'xJr8YZjqVnu4Cc0qRrnah80WKPFLmaSOt92tKK/899mIjKNNZoQyqFjuEeBiXjaQe1PUpBWGqBOwE66BXQS8ydYB9cE4NIiDJvo0nq6z8CboBu3Sm+ensmUYke7LowuO'
        b'56dPB3Fmhz++cuMLMb1E/7LF3xMGwWtJ3fWfXoCvh+pvufovi+5/FVXc/+vagQ29vR4r3nln6NsbU34sWryBs69ZuSB19Qr99/edfbyI37E8hpPy3Ye74h9bvf154LWV'
        b'79PhznGnuGeTr8grPksNWKv+yKI5vTaHtXjGqow9C+Y+Tfqj89+D7zU3JLzbGXjTIPAs/aDtWf20wqmrv1hX1pHqc1/EeysN3s156dE36ZcOaqJnJFxdcJPv0HrgzekO'
        b'd2fe++uGexvjHxy7V7/cpX7Bl2VS230fmqffFm3bYn9/6/Fs7qQZ3BrDT6Hrj7NS+TFKVck3xd9U3e6OXZj7NOmbL1aEN86a+P6zgc7yuz/p53+8K+abPzl8zC5I/2xX'
        b'NW9d18mnnZvdTc6vO/rFvQZ4FN4+/+HXi5LsShMnnDr9TeY8tW/blczWsPayIVmV5s371/wbn/355hbxqaWWFTMzKmac99wkabhSsvvTr0oH99Z43zw7KJ59za895GP5'
        b'Jec/NUQA+1OfrJqlyenivOMteIr1/8AJuO75u8nIzWSqYORuQoNW8gk+CefwhSfgXnLnQc/58DoL7IY3YAtjE3QeroYX0DU4g6Y4zjTY2AgOucYQmxOoBEdi0+EpcJwB'
        b'ox5Gom4Dx4nFUza45DXW3GmvPVZqgJ0EHhvdvTaADeOxkeA2PXg9ixIlc/WzpEQ5IQisAzd1jJK8UtDtu4fFmNh0V6P6t2Ua6aLqg0sWDJ73y/DQ0nFWSdZxSdgoaRs4'
        b'TboIOwPhfnAabMseNp0ihlNw91xyJROAzTytxVKO21jVCXAWnGV0J3b5A6X2ronvme3oBn9hdjK5TArgvsnpY6yVTHhovtaxE8CZKmYObzeCE2OslSZYY3ulbHiAPM+B'
        b'G8CudF1jJZPil1awk1zBTWaMx8BOG2KpNB1cGatDARSmZI5WlIONukZI1oi5ORwHbpH114Ot8Go63AePjDVDAhdQBnJ5RQycH2N8BlpQrrGKHGAvvEYMq2bDQwbP6aJE'
        b'+mFtFHQYOpT8G57nR28d+EOg1us8uXvqeJ3H9pUEZsKJeJ3Hfo8M+0VufaIglSiIsWvvE0U1p2Bs8cUYehwjljuI5FbtcxTObYXNUx8GRmDQ8tOrmpNbveQzVLa+KoHf'
        b'Q4ETY70ir+9a1LmoX2jXL3SUW7eZ9gtFfUJ/dAdUootgWJ8wpkfQJ0y+I8CIvfldsztnK2m1MKRPGKkSRvaYq4npfIcpNifBhRRitTBIaaG07BVOxA9MsEt6AmSeoxYG'
        b'KllKdq8wDGtwp/TZB6vsg8dW1ZPQk9grjCPPOzLbMtVCnz5hkEqIbZGEjC2SMHJ8B+N6bPqEaXemvjC98k5KX1KBKqmgL6lQlVTYW1ShTqr8PTkdmHEXdhYq0Qgi0Hyo'
        b'0JSgUcah+eq0lM866qDCmO0OZAa1//AAkojWiom8XkH3Cn1+LhFV0i90Qh0anGgXZP2EsvOyGQqnhI67m1or1TaeQxF2Vt6PTCnnSYNTacrJpaOyrVK+TO0Y2mz4wFL4'
        b'0M2ja1rntJ+dZ1LzzywOGVafe7jKHVtCCSehWVAJsSUUBroYpYVhkhg01/dH3dN3txmyGO2ewveRpb57OKIrj92ZgwJK6NBs9Dw2+C8rvxBs8PFbod4WEf3nbB0bnmQn'
        b'mrYY/L02POW4LhY9zrHLiN8/AkjP1ULAcrSK5NjBC28E/pX3X4R/rUDXcC497hr+PG6zXlYjRtWBJ2MDfLHb9+wUdG6h0wmcjAZb8lNG3JanwI16dTx4gFxewFV0jN3A'
        b'TluIuSI7dkk1DdYuTGYukTeAEm721aPgQXgAm3ZDxUTm9nQMdGf5TmfBW2AzRedS8EAU7JY+mXSJlj1Fj1fBPzDu/cyxW6HW4NcSIjMnOPsZK1K2TmAH/PPMq3+Zns/5'
        b'vwrPNH/szM8zI7bV3KPjLSGwenWHdK33nvfYB6xe3TY3drNTXkCrPmyaKW/v37O6nBu6SXkgIdFzV/Ae5xSzqwPAyLHEyOh4hpER963O7fGg1cd1T2abyI/LK9Ln8WpE'
        b'xvneW+9ncDc2zBMH7PTe6P4e5644YMt0/17j9T9+wXkyk3/dImAopfSi6x79P/+p2Fq4bYvzLvc97inWzufyVniFgsy7xZsFhQHNg2kV2WW98d+ZKmJ3pK6Jd/Ri51u+'
        b'fqf4bb/3m1+/12ZChUV4RKzf6G1KzryVi+EuMvuIX4M7wbUIGpyzR8c6OdGugzXosouOAa0JCR9uY4Gd4SvqQ8lxlAA3g63k8RYC3HSUl8WyhzvtmOPsPDpL12BDY7+A'
        b'VLgFbIKHUSZDqGTBG4sKyZE9v8gWXW0uLcIiFBHcFMii9EEXCxzlcsljt6zEdD9s17olA96CR9CdwDCOBVujwDXS+kTQPBtXHzjdn0XBi3notPdBJ+9hUrbcFZ7B5rhe'
        b'UWP8g4A1LHIVsp4P96COp8Id6JpUUMorZLmCLhnpN+LuroGr2Lf9AngEXb4CvFmUKexggw3wEOwic8Yrsk7HF4lA7KC4BezlRbNsZPAV0rAtuksfTB+hXX0BCzGLl0Bn'
        b'nJCButoIz+Gm4Q5m0sLADV4CS5hdx5j+Xiwu0LlmQTm8TizLt2mH3AS2gJu+WqvgmGU8oGD5wWbQ8h8DQQ1LB0YdvmuMRw5pmbiJcRrC0kqI0pwpgfX+iN0R+2N3x8rd'
        b'+iw9VZaeioTuaSendWeezOxx6/ObovKbcifhjbS7afca+pLyVUn5H9k697pEqG0jsZktelsbtRm1m6Bj3tKGcUPcZ+mlsvRSWPdZBqksgwZsneVuCrZintp2UnNiv4dv'
        b'1/zO+ScWtBm0ctBrGxeW538oDHrEpjzDHgps9qfuTt2b/tDOoSOiLaIjti1W4dZnF6iyC+wX2nbw2/hywUGTMZUMODjLXbo8Oz27/Dr9FA3KfLXLpJ6kDxzi7+T22zt2'
        b'pLSlyPMPZg2xKccEWuUQ/xi384lD/IcO8d/LsKLQa1yLZDfua24GyaH6us4Y69m/qgbJTDzjenGMUSfxHY9NCZ04Okgyy0Q0LcSuF3+PlxLiLMKbrzEswsabYqwuI6v/'
        b'E67/Sxx8jYNvcfAIB09xMIRLcIiUg4E0JzDn/JFDjkV+Z3kLXmjfaU9Tukaev0FV9B5NXFU1SBbIGFkUOQ+tR0w1zf+LslCdecczvXr8f8z8v0trA2z2JKumiTnnIw7H'
        b'2OyxEXYYz+5MbF1yvvRu3puWd1IHJtjLfa9ZXsvr0X8zEbuLz8FmxLFx9BDb09jjEYUC7CsepXJwPJcetvMMx3aekcTOU+vcHtuC2oVvTh+185yI7TwjiJ2npd2AmUe/'
        b'IBilWIZuThxNicUpcTRJ0hYLwsVCdA1Gh1Me89EABimWSSbdJjtv+Yj80tjYHUjqnNDnHKFyjujRVzkn9DmnqJxT1M5pavt0jaNLZ1Sfa5TKNarHQ+Ua3+c6TeU6Te2a'
        b'qnZMQ+N1SKefULQwg37ExnUN8RppY/9nFA6f6OGUQZIyVMOOMnYYpFDwuIlGnWhzVRk7DrEExr6DFAqeID7K6QmOjjqxiraPlo2wvVzK2Jblg471Fnip0ZvOkqruXmLJ'
        b'EtHi/KX6L5Kcd2vWxpkdtrLO/tHG6nLya6ERf+lMbS/8ngMPZqQcuBQefHd+x7G/3R/4aq1Hvabtb4v292V+kV9z3Lf78emHNg94+nsWGkhuZ4ucTn3ptPr9Rcpl31Q+'
        b'uKJw/Yvl0a+skof2lZp98K7bj5yHlRU9Q09DHFXvvxN1b0/Qq6rKKQkfTtphfX3H1+nuZ/M+7gowlibkHVAdtL50zOpbr3cTjfrqTL4WbRS0mgdb5DXP/6Y9xmTre7fv'
        b'c9ef3/7m+1Ym3AnmgvDLTXOr/fo/58neSsreZNfzwdHmvNf/4Hohs0TTy475wz6W5gvzrNdKP3SzeVZusyEn6q3oZx/0nHDuetf4yZmqIouwyUV/s1EfWP7McKHzyrdf'
        b'735W7ap+7eICl9Ozz791Sezu8Fj/9SMvfdz41XLo2JTtmBv59bNvl717v+inu9submj5+vC/qG++S/tb4aA3m/Fosd3eGm6LA2cRL0hHUugaoChjQCfXgGvwFUMx2Dze'
        b'lRaHj3KdIZgk+POawTjnWLPBxZFvIrAN9Hi7jd+M/F8M/hdb/994Wbgxp2Mc+e+5t8a49we2oK+uFZcVFdWHoJc4OTETEJ3+C52YYZSx1SBHT99mwNSiOWTbolbnbcvb'
        b'ZPIQubhzYvtSRU77qvNuyvoe5/ONPTnnF18MuJt0zwKmqEMyPhLatoa0itsmtuvL0xADprRBPGRvdJbKJqs3N7+3YIYqd6baZuZH1iK5RUtNr5kbdmE0ix40oCwEzfG7'
        b'rTYnDIWZ67sNUTjw8tT3H6JQMIiDoXw6Wt+2ecZTCv0ZWkm76du2Wj+l0J/BLJoyMBti1XP0fYeo0fAZCdGWNTAbJA8HG/QpoYfCUGUTutloiMfXFw5Z17P17VF2FD4j'
        b'4WCVHqksl1QzGj5hQlzZI/Lwu8F4Ia2fSg9YOB0z6vWfqhZNU1uk9BqlMCfu1nj7JCvqVSvLJC/tdxIHDQvN9b/3XeR/Qy9YUFQ89pPbiw4aTB4ksCU0QjGcXzBNm+Ev'
        b'LzrB77F6wBeK07zJ1HXDeB5b2ntFny07h5K+bTko2Z5qAOIESauW/tXNwCWS42lfI59r2nsz9MO07/TMbnUNGjyYmWrG2c+b/+SU4sh76TPODCglbxxmTwso+sDaX7LU'
        b'7C9Hvpoe8aSx68iXR+MWPvrp7Rn/rC54P/OnGremS7krFRfTC/P72uxzBR1r1wfcn3ciLeNU8qKBL+Jtt943E4QZ+flEfiAErsXrgz1aSzZG2fqZnQe27lf6xbvgeemK'
        b'xCHRs6ohQUftNcpl/ud8xJSQ76d7MYIPvtxPnw4PCvF1OF2PMgQXWFABrrsx/MVBuCsrfbo/PI9zYR7AvAmVuYERhNrnkSxLEaOoBNvALrgLC7GwfFSPMrEoTGc7RsPb'
        b'hBEQesBt6amZy+Aan0w9isdh8cEhsJY8gkfRZf0ShvjfFsij6DyUkAxbiSEVPJ6JbvUvZ/qmcSk6nYKtiAuQkxt8RhU4jbHLd8K2WNQkhtsx9GbBZng7h9zgl0kSZPgx'
        b'r0T71CCVBZQJsaSw8ULYnU5OPkaAaII4gfNgHztryQpGRHolDm5IT0U811XMADC6FHu1yL6gFVyxJ1xxyjzQoWXYjCxZ8JJ9DjNh1yYXA8Rc+NXBU+CkNoMBuMhC7ElX'
        b'PIODayZGOS4Ygc2LFjbCiwuNFjbWw5s0ZQN3scF2sBueY2raCLvB+nSCjgW2iPF4KLQ6B1jwCDgwkzkUboEdsAvPfWA6OhB24m/gODY5VI+yc+OAdXBtvbfXbz4P/n95'
        b'POhsfC9yUMQN//cLR8UYmycckHMCX7h/Qi+BJ7YU17LfWNBn7IiuSQcXq429Vk/t5xhsyliT0WvufCzyA47ffY4x+vcxx+kTjucnHP+POa5DvDlmXPRaHQ2fkXBwsYgy'
        b'EqyeriOqctKwqyU1Gg7W3ddwGxrrqiUaTrVU1qDhYEGshlNbhx6zZQ31Gm7JkgaJTMMpqa2t1rClNQ0abjk639Cfeqxah93M1jU2aNillfUadm19mYaH2IwGCYosENdp'
        b'2EuldRquWFYqlWrYlZLFKAuq3kAqG7Zx1/DqGkuqpaUaPQYNQKYxlFVKyxuKJPX1tfUa4zpxvUxSJJXVYm1sjXFjTWmlWFojKSuSLC7V6BcVySSo90VFGh6j7Tx6Dsjw'
        b'G6T4l/4TicatAfanJsMczU8//YS/gpvTdBkbv4HHho9I+HteyvjgusvnxQupu0LDeFf29/xyrOBfWhmgMSsq0v7W3hq+t9XGRXXi0vniCokWMUFcJinL8uYTFkujV1Qk'
        b'rq5Gxx7pO+bENAZoPusbZIukDZUaXnVtqbhapjHKxbrWCyTJeC7rxSzt8jOEwFxWohfUljVWS2LrK1iMeY4sAwWDbJqmH6GhcQZNKEPj1XqPOdVmtGCw0JnSN+/j26n4'
        b'dq1pfXxPFd+z1y/2rgf0Uvul9fPNBgyse21C1QZhvZywAcqsWfhHypa09v8ADj9xPw=='
    ))))

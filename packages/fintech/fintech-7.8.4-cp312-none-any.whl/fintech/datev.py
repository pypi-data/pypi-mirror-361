
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
        b'eJzsvQlclMfdOP7syX0Iy334cLPALvfthSJyo4IXHrCwC6wuh3ugYjyjsoooeIJHgMQoKFbUqHjEmJmmTdK0ZcVUpKZN3qZvYt+mryYm6Zse+c/Ms7vswmK07Xv8P58f'
        b'ic/OM9fznZnvfK/5zszvKJM/jv73q9XocZSSUqVUNVXKkrJ2UKVsGWe1DTXhT8o+x2JCShsph03JeOf0KY2UymY5G8XwpVxDnu0s9G4lM5ZhURt4NjVC/nebbDMzSuYu'
        b'pmvrpRqFjK6votU1Mnr+BnVNfR2dJa9Tyypr6AZJ5RpJtUxsa1tSI1cZ8kplVfI6mYqu0tRVquX1dSpaUielKxUSlUqmslXX05VKmUQto5kPSCVqCS1bX1kjqauW0VVy'
        b'hUwltq30NWmRH/pnhzvhA/RopppZzexmTjO3mdfMb7Zqtm62abZttmu2b3Zodmx2anZuntLs0uzaLGh2a3Zv9mj2bPZq9m72afY9Sml9tB5aF6211krroOVqnbS2Wlet'
        b'vdZG66altByts1ag5WkdtV5ad62d1lPL17K1LK231lc7pcoPdbn1Jj82tdvH0J2b/G0oNvWSn+Edhf0NYRa12W+zfzEVZCF2HbWes4xax7KpErILK02Hzhv9c8UN5ZLR'
        b'3kAJbQsV1ii8cwWH4mbHoTEqz6dqQihNCIqE+8COJtgCdxflL4Ba2BoPO4uEsDVn0XwRnwqby4Vv2YBrQpbGH+UFh0EPPK7KKYD74N4CuNcGXGBRtjlsMABbwXkhWyNA'
        b'mRyK4Y28nKgcHsVdEc1lga4AuF+DOx/0wzfAPpwkgrtReR7lCC/VwD2cQjG4iArjPA1BrqAF7olqQBDtzYE3wE4eZQsus8Eb8HqZhsbwnpoRj7JcsvfzAtp1azXw8lr7'
        b'tRoW5QH3c8Be7kYEahDKJovgghawPzpPFIGBhYes4H4cYUX5BHPBy6AbXK5kmXSaj6HTDqDHYe9m1HFoLLloJCk0glZotG3QONuhcXZAY+uERnkKwgFXNNZuaJw90Dh7'
        b'oTH20fpW+ZAxRhNit5VxjNlkjFkmY8w2GU3WZrZ+jMfFGsd4x/gx9pgwxn7MGHsH8Cl7X1uKossVkQE0RSLtbdgUN+FrHh54boArE7n5JRvKOf8unyovVzhExzGR34t4'
        b'lHVNlBU1qzw/s8iW6qMUqC7K1t+L+7TRDnXsJ2Ffsq/GfrT4J5QCU42nwZ2sASuKjglsjHuoLHNZyUT/Yu5XToecWOHOpb9n/d1TlbmLGqU00SghoAH2oKFtiYavwvML'
        b'wsPhnuhsEdwD+krCcwvg/ihxjii3gEXVOdlMB/tgt9kQ2RnarMRDZKcfIp7Z8FB4gKrsjEPA/ZcNwYRpZjVhCOwLlbgPNe7osT4MdBeDftC8ULSYTbE5FDzpiuaBC54H'
        b'vfGyYjaFPgcO2gSBE/C2BtcDjsCzTsULUcLcxTXUXHASdpLsjaATnoEHEQ2PpjZsjgYDMzXOeB70z7GGB1H/iKjG6aJFGlKHc4VncTJoKVgAW3kUeyPLNzdcE4br3h7e'
        b'iGdUZB6aCrthO52/IBz0RWWTSS6GfTywHb4MejRTUN76OtgHLvMpahoFTm+eppDJPzrmzFP9HH9zyaPj708/uW13z8HLB9ckBnE81WsPz1pmb2+9wGPXSEbBSXv72Hx7'
        b'+yv2V/Ym7nVQCPeeXJFonzTruv+MbhvfxL0nH57rpM+2BBd3rPa83OEVM8tWZWuXv8jN511+rxd/fvzIJ1WPqbmDazwl4q3n1DvPSv9Dmlu5/dyRjEWtH9b9SpDU0TQo'
        b'T50/3PFJqM22fHZF4w65Z11N8x8qHknnKl8OH/pl/9I/yn469NatHX7in7ESWqwkHuEl5X8MzXLfJfhFVGF+/JRY1w/udPKpa2+l7+9bJuQ9xRQHtr6UkAdbI2FrgWgF'
        b'uJaLCZcLHOTAZnho8VNMS1fAi4LIXBHU5uQX8iga7rEDF9nwZCVsfor5C9gNt66OFAtzI/VUzQlu5cCelHqw34F8IXXqCjvc2RoRuJAWgTCeTU2BNzjgPNwGLzz1Qjkq'
        b'wuFt2AK6UuEeuB/uRVQ6lQUuOsFuocMoO1yoxOP9Dz5UDuhB01vH/r5zn1alrG+S1SEuSfivGPFOWeOMUQelrE4qU5YpZZX1SmmT+Ssb1/U1evx5K/XkJRbl7t0RenCF'
        b'Nuuhb0h31a98Re3Wbay2xBFXz7bpI3RgW1ZH7IGcB25Tu3ndqntukSN0aK/bBb8+vwHVYOawMENHZ4zP8oAO6p77mq1JdC+vd91QWPI9txR92n06TkfHDcQPcobpaabl'
        b'1ffcolCenjm9vNdyX3MyrYPbW8PUMUKHnHHscextHKaTmAyfegcNBSde5w4uummnC54z7J05JMh87Ef5iR/7UwKPoyntKR1Zw65BQ/ZBX+EJr8QzXug4ymd6ZNSqrEyp'
        b'qSsrG7UrK6tUyCR1mgYU8w8OkyN6lJuNkxJPRiWmAOOGYibOn4oe/7WV+nYji8USfEOhxyeOHi1rtto9ZvNYggd2Li2pn3CddhSMWDs9sHb98xMexXM2vH2nwmTqGD+C'
        b'OmuXyDEjakZJsRzTWN5RSoblRCQlSlmlHPSPK6dKeeiXL2WXWkmttVQVS8rZYVPKhLg7rEttSIiHQraIGrO07CqOlI/e7IhwxEVvVujNfgMLyYc2o/yFpEmFpG8rOSaQ'
        b'cA3ktQpDwmIEtqO4RorUiSk8kkt3G+XSTVxC4TkmFJ5rQss5m7l6Cj8udnImy5lA4bkMkz3hyy1VUWjcZpVHvRNrS8k3XwhkqVailA+6dMffn3ay52BqC8tVfSmb/Z5n'
        b'KN2S+sqU0FK7hT/f3pfW4lfcv0uSWFJmW+mWHR3U+KbQPnHvQnp5R3lgJ+2/QhZW3O48PyzZPTnubUW5NCGjlzv7F+7Up9Om7Nj/iZBPCE4OuArbIvWCzaY0uD+STzmB'
        b'05wmuH3FU0+UYXodOGFIR1IRZa8Ii+JYbWwg1AzcAIfT8mBLPpLxhGD7Jj5lDfaw18MbJU+xDARuwktIvEK8Ii8HnAet8CZF8VPYXtZwOykOd4COItBShKQ4JJMd4lI8'
        b'eIIFb8COGlIcvgX2l0WKslEy7IXnkDAB32CDHfAVuEfImxz7eQYiRZB+1LqsTF4nV5eVNTkx+CE2RBAyVM6QocdqNhUVc2F63/RBD11khs45vI17yL5j9YjA82hee959'
        b'QYhOENK9elgQO5ChEyS2sUb8A7vWdK7pDeyN7ahHee1G/KaiH9sHrh76Mt3cDwUhjzmUwFPpapzx/FGuSqaoGuViHWPUqlGmVCF1ROmGM7gbm8DHE7gcT2Fm4gbgiTse'
        b'/OU4ZwJ6/GUr9Y2KzWIFvMCs/Qqj3iF+MHXKLppTybY0VyqMc4WZKVVsMk/YZpIQx8ZMzjGdM2hGsDdz9PNkXKxxnlSPnyfGz5vME00UCq8D12CXHWxF6LQPy3z7i7MZ'
        b'xFsA34Bt84loNBP28KeAMyvlq3JbeaoZqNQ2t2+Ov59w8jf8noM9B2PRPDoU6/7kcAxcj+QJ+0UKe/tzXgF/Dc3qFrvnr1z2x46Kkw0r37Y/8Yg6r7T13M4TcglLzQS3'
        b'QT9Cc7C3iGC6Hs1LnZ5i7SATHofX4WXEsPfD/WJRgwjsjGM4s/dmLtgJDsArZCYFVsUQXPcHJ3OMqN4Ozj8VkJkkgK15RSIWBQdq2Y2sjCKgFbJNsBoPkQGlEY+olqnl'
        b'alktwmoXI1oY4whiJ+kROxNjYIe6a2PnRp1rxEPvkKHQtMESXWjGsPfsIcHsEQ+fo03tTUc3t2/ulg57RA45R5qgK08ZiD/IrZPUysYjKY8gqRFH8RhZAqbSgKbfbaW+'
        b'nsNhsTxfFE0P8AOpV+1EnP9rJN0iqoZjVF2kHkNU/jwTVDVF00MJ8sY7S9gETa+eFDCkfiKSPmo3oulPCkO7Z7jnbzqJ5OBLB7bFc6i/77T5w+dPhByCYHBgnoeBGBcu'
        b'MNDi7rlPMfmAzQ5qMyQ9v84USa+HP8UjK7dfjHBUNReRXAOKuoE9Qs54Gssh2DiGjioL6KgyQ8dYPToW/gA6BiHCe9S23bYj4a4zbUo4CSYqRfiDvEaJQjMBH8cTzQRz'
        b'hDSCU0OZ0M0ChJBTXwAhldjMYZleEkTkGOkl1iWpKu5/A82coD3yJiAir1CDewpcoLPzVqrQaJZArUgkXpCduwhqi4oZfS0b7s4Xsyg1fNOGD27RmghcohUNuR55QUe5'
        b'OaE1wV6RQO7rVcZRSXED/pJ8/Mub78cRXe76wYsH5YmuHE+B6mhM3KwM29+tDr+5++JB3c6Axfu29Rzp2dVzMKRlN4uDcDz+G+vDA0AT/2FMycXYGPqDctYjKbzX+c5u'
        b'4a9srh1v70Eo7kf95S9TVm/iIwVrKsbiE3A/uGIHD4MWRgsyVYFWqBmhpBOcBK8zE2HKUiO1joVHCLkuAD+Cu0xngmEawNPwJp4Kh9wZ4aQZHoQnGOkkWGKYDeCCXs2K'
        b'9AbdWDZZDg9jLU8vmuyBb/6gaGKUx0f5mgasLjU56JGUeSXTZQkzXZ4s5VCegd3Bvdx7HqKHWMeYOew9a0gw69e+dFsmot3dCWfSe9Lveogf+guHImbcEegi5g77Zw15'
        b'Zj3mUX4Bj/nUFDc8ne47B+icA7qDP3QOM5lUVsykwt0ybjaZAG1F6em8QY2YjieWOcy11BiR/3bJCxJ5Zk6ZWmfMZRAOsc4Q85mesGNrDOdfZo2p+WHCzimUr9gXyqD7'
        b'F0f6Ma0O2Blwsh0h/OsHRYhi91ftGFrUj80VsxLzO1ZfWnrx85fviu0vnrW3j5218sre3sEr+SNfvFvxU8E5yY4HK362ApbA+VDBkX7bezmG+uj9Us66JTGcam9qr2bK'
        b'8kvvIsEDS+dIk38TnjTQdD61HlxgiPo5+CYh+d6w2Y9BUS5sk+hxdDPcTxLBgAYJHy1Iem4V8cG+KIq/ih20GR5lEt8Cr68yiObUMj4RzBfCnQgnnkPDxDhB0yZSNtJf'
        b'VWolov+OYwQXv5vJ2DUcymdqh3tPULf0zJqeNcOBcTqvuDb+SFDYmbSetPtB8bqg+F8FJbbntWV2hIx4+nbZddrd9xTqPIW9wcOe0W0ZSO9m1G2E3MFJT/iUZ0j34mGP'
        b'qCHnqImsYlKEJozCBJ8zMT6Pg1tjQGikF39TjRDa5UUQWozBYBc++jtCaqEDVkGwAIW0e9uyMmZFAoXty8rWaiQKJoVhbNaVaC5V1ys3jFrrNQOVMphQiiq5TCFVEUWA'
        b'SFqEu5GZSMD/IaJjYgTAg9+kV5WLcXoiHp0d1MeuHlpMUbTZIx5e6OHurZ034uahzfqay3cIferMcYh6astxEH5jy3cI/9aZ5yAiXa7B9eWC6zl2uQVwX3QuC5HCDnDa'
        b'nl3OAWcncCn899VCPKlZ48wB7FKulCPlSnkn2KU8NrWEGqCk/NUO1IQ/qZVhYcjwW2q1wRopEjaj/Ll1iMdv+E6QKauQq+uVsrroPKVMygQfOZNBeYTn9Hcui2XKJk21'
        b'qkGiUVXWSBQyOh4lYQi/s8+XqZvUMjpLKVep+9jKuSjy0U8QHn/d6UJRefV16vr0QjRmdHiGVClTqdCI1ak3NNCL6tQyZZ2splZWJ0w3eVFVy6rRUy2pk1osVydRw1tK'
        b'hZiej0a8HpVdXK+se558lipbI5PXyeiMumpJhUyYbpaWnqdRNlXImmTyypo6TV11+txFonwMFPpdVKwW5UgLleL0jDrUYbL0EiQqKaIz1kikYnqeUiJFVckUKixAKch3'
        b'61SN9UpUc5PhG0p1erFaKYFdsvT59Sp1laSyhgQUMrm6SVKjSC9COcjnUM+r0G+TxqS44aViHYYO26doPSAoSkyXalTowwoT4OnYSVPi0vNkdXVNYjqvXonqbqhHtdU1'
        b'Sch3ZPrvyeh58JZCLa+mG+vrJsRVyFXpJTKFrAqlzZYhxWcNrjdcHyU0pNHzZAh34KkqtQq3EnfpxNz0vHxh+lxRgUSuME1lYoTpOQyeqE3TDHHC9CzJetME9CpML0Y0'
        b'AQEpM00wxAnTZ0vq1hi6HPURfjXvNRyzBuOwqFBTiypAUfnwFDYIrsG9xnQ/isyZnVGI02QyZRWiPChYvCQnq0Q0px6Njb7zyVyQ19UgXMP16Ls9W6JpUIvwdxAJqxDr'
        b'v6kPm/W7pXjc92aNiJvQiLiJjYiz1Ig4phFxY42IM21EnIVGxE3WiDgTYOMmaUTc5I2In9CI+ImNiLfUiHimEfFjjYg3bUS8hUbET9aIeBNg4ydpRPzkjUiY0IiEiY1I'
        b'sNSIBKYRCWONSDBtRIKFRiRM1ogEE2ATJmlEwuSNSJzQiMSJjUi01IhEphGJY41ING1EooVGJE7WiEQTYBMnaUSiWSPGJiKaT0q5rErC0Md5Sg3sqqpX1iLCnKfBpK6O'
        b'tAFRYxlSkQ0vDUpEkBH1q1M1KGWVNQ2IXteheESL1UqZGudA6RUyibICdRR6zZRj+UMmYthdhkaFGUoTkkHSl8BTNUrUbyoV+QCmegyPVchr5Wo6XM96hemlqLtxvgqU'
        b'WFeN82XBUwqFvBrxKDUtr6NLJIgvmhQoJmOAU+aTJSXTysbYuKgUQYEIRjgubpagL4+SQiYWiJu8QJzFAvH0bKVGjZInliPpCZNXmGCxwsTJCySSAgUShi+TPkdyCZJP'
        b'SJxatl5tDCBKZAzGm2ZVGbMxAzFbhthxtUlESHqpvA6NBh5/8h2c1ISiMOtFVNrsNc78FZEfiUqNuJ1SXqXGWFMlqUHwo0x1UgkCpq4Coa1xxNVKeKoaIVFOnVTeKKaz'
        b'GP5h+hZn9hZv9pZg9pZo9pZk9pZs9pZi9pZq/vUY81dzaGLNwYk1hyfWHKDYRAtiCh2+UN+rKr2gIRwTjCwl6mUlS0kG8WmyNCMps5BeZPlrWO6yFG8mik3ehmekTyad'
        b'vUjmuMm/bCanPU82RCotZTNjAUkTWEDSRBaQZIkFJDEsIGmMGieZsoAkCywgaTIWkGRC6pMmYQFJk/Ox5AmNSJ7YiGRLjUhmGpE81ohk00YkW2hE8mSNSDYBNnmSRiRP'
        b'3oiUCY1ImdiIFEuNSGEakTLWiBTTRqRYaETKZI1IMQE2ZZJGpEzeiNQJjUid2IhUS41IZRqROtaIVNNGpFpoROpkjUg1ATZ1kkakTt4IRCAn6AoxFpSFGIvaQoxeXYgx'
        b'EVNizBSGGEsaQ8ykKkOMqW4QM5nSEGPWHj2IWUpZrVS1AVGZWkS3VfWKRiRJpBfPnZ8hItxKrVLKqhATrMM8z2J0nOXoeMvRCZajEy1HJ1mOTrYcnWI5OnWS5sRggr6m'
        b'Dt5qqFLLVHTR/KJivQCHmbmqQYb0YUaYHGPmJrEG9m0SNU9WAW9hTj9ObKhm4vVSg+EtzuwtPn2+3rhiUniC2SV2YlTcxCik5iiwUixRY7mULtag6iS1MsRGJWqNCou1'
        b'TGvoWkmdBrEXulrGoClih5bMAEKTInLM3OVSUuwHM1uo3wJTslz3xIzExDTWOzQSvmm9yEu6sgqn6zuZCceZhLFOOGapGmWlF/ZZK7OwiW8efmRT+uUyZQ5+5GIzIk/V'
        b'oJCrlXnYEsZirIPYhqa3DBYQyyBjQ9uE09INlkEhtgx6abMf8yn36BG38CdWXE9HbfaXtpS7z2NuzJQ5rG8rWJSTYLesbU7L6q+qWfHu3ruzGPsgXixROQGtCvvF7Y4C'
        b'fVzK2ndpEnszfAse+h80EGIPIduMysp6DWpgXfWo42yERYwiI2mQKR65MeZBbEH+zjsT4VUtElawRZhmVCk0K+SIlqEs2Cl1lIuFKmUJCn59C0UsqmVkpPqaOhldXK9Q'
        b'RGcjIlcnymvCJpux1zGymb4kr5RmimHTHCbIKrlKw0TgNNN3ZhrPw5ZERmVgPjR7kai4skYBbyF0UiAxx/Q1fbZMIauW4oYwQb0dZywcp1e50g09QVQILGPK9NTCoAfS'
        b'jJyl1ybH7F56PZJI/1iDRJnRfFUTTUNfA/mcQo4ykJC8rqqeFtEZSrUBFH1MTh0uOS4SZ4uzlC1uQrZ4S9niJ2RLsJQtYUK2REvZEidkS7KULWlCtmRL2ZInZEuxlA2J'
        b'LUXFJbEoIo8ZGCw+y0hk3IRI9EIXyBAJNhh3aY2YHjPuokgGlw3WVjGNVQCDIs9YcceGkc6PzE/P0tStITsmZMpqRPOaMJ3C8bMX0QmpDOeuMmTBVmZL8Xq8YZIsVJhe'
        b'SjQM3HBlrQQnGlHEUooRVSYrFvesYpYTGRR6RjHLiQxKPaOY5UQGxZ5RzHIig3LPKGY5kUHBZxSznMig5DOKWU7ExVKfVcxyIhnumGeOt+VUUvDZiDI5psQ+E1UmSSUF'
        b'n4ksk6SSgs9El0lSScFnIswkqaTgM1FmklRS8JlIM0kqKfhMtJkklRR8JuJMkkpm/DMxB6UWq+GtyjWIda1DzFdNZN11MrlKlp6FWPwY9UPkUFKnkGBzpWq1pEaJaq2W'
        b'oRx1Mixnjdkv9ZwTE7wMTRW2tBmJnIGXoiRMeccYMh2eUdfEyNh4iRAR4wK5GrFGmRRJIBL1uORxdHhi4TFKPj5NqYBXVXoxwSwlmywYVamRVGLU1AgnERF5x6JaoW+p'
        b'npsj1o84DZbKq4g8XosZvFomR92iNpqec5DwrJZXyddITKl/KdEsjSZpUzGD0UdNliZNxaQsGaOsyOQVOCkfjRpea1Mxks3kgpqpuRnBjb4sUWhq18hqDLZxwgSJFIed'
        b'bQqVSy1LxdjNtslEcLyF01MMknGQiWScPOJGm0vGnlOmfRs3Jhcn+4yJxXgLXKYf6FXBN+zyC+G+aCIew715VpRbBdcedE81k43tDbIxn41kY4G5bEykYT76Z4f/Sdno'
        b'6Yr/YXm5n3fOiilqg/6T0lqe1kHrSjznbQz+MKVcvCdTar2Dktr0257Te7eV8kmsHYq1N4m1IrEOKNbRJNaaxDqhWGeTWBsSOwXFupjE2pJYVxQrMIm1I7FuKNbdJNYe'
        b'w1vFlnrssC51MGun6w/8s+n3PGdr0vIALVvfdq7Uy6Ttjua9h/7Zon+sKkMvWhlD5rV7n7Mx1C4N1DIef3hDnzP6gpXUx+QLTtIglM7TWpMtfy4k3XeHTakzipuC2uaH'
        b'2jbFCIVrv79Bb9FvGnTUOlXxpFN3WBtrdNnAt9khDB61zsS7beYUL/4u2pY2+TNE0wwxZDa6muXo4ynnY+zGqtYj7BCjXIVD2N2WKDVC+0cYiEd4HB5hb8+x7MpqQ3Yl'
        b'dqVUluMsuKcf4U11jzCmCq1GbSXSRkRflWVy6ahNJaJydWocdJQwE6lMgcRUdc2odaUGEYC6yg2j1tirXS5R6D1e7KrkSDItq0XEp6aw0tpkKuBPEe+szZTB4dJ09y3Z'
        b'yMdCg83VWqHOY7bx8atsieMYQtPdtkbHMRviOGZt4jhmY+IiZr3ZRu84Ni7W1HHsa7yXzqxn8V8O0xR5k0xF9igbx0NOHEEqZeIJRSZEpCHlSlJLj3Vjmn53MiKg2Hym'
        b'3/6s709JnXpCDfgvfDaie2oD1RWK6QxcHlHISpo40dKaBhrxiWRaKq+Wq1UT4dKDYRxBy1AwyZYhMC4S/QAMiT8EgznqpNH55BeDMC8635CqB0xlGRbMVTE/Q9xQTJfU'
        b'IA6HZoiMVmkqFDJpNWrPc9XCeOAwqjiqiZagKtA7Az+tqEfcVimmc9R0rQYpZBUyi7VI9I2vkKnXyfAiOR0ulVVJNAq1kGxOT5l8LPRTJo2eow/RldjKGm5cmzWxzgon'
        b'q8Uw3dIM2KoyDibeC1+vpMMZT5818JaySaaYtCK9p1oa0SWx3IWqYXBET33CZdViOjE2JopOjo2ZtBqT+Z5GZ+EXmrzg6qrkdWjWIBjpDTIJAiyiTrYOLxQ3JokTxLER'
        b'wold9QP+0fbM3qv+FVMomm6lqIbyqP6YdEqDffHhG2D3LNhSAPrnQ20ObM2LhrvnY6/p7HwhbIkqFIE9cH/+gmxwPruwoCCngEXBdnAcnATd9vU2a0i9xUH2lOdLeXxq'
        b'fnnU4WVBTL2gezp83WK9cB/cnY/4P9htXnHwAgru2GBPwdfgflLv9lobytnTmkuVl9vbepYxm+6z3OFRsh830pXsyEU1iEURuegD4EdcKmkFXwX6S8hmYlJHuAufslc3'
        b'8PCm7j2zAygNdiKEHZsCLIEGtajGligM3l7hYgYySRZpNLiutAOXYD98Sx7Q8wVL1Y1BgXc27Y91BDH2c7841XewpMFPfGf6DelWNYdfoF764CXqxwFNOS42S3qyrgjm'
        b'zvzt36M3v5PcUO6dsediuEC29S/Kab/766aD6Z+ouYP2yWFvvqf9NjMp5J2zgtcW9uc+OiY4zuk99vszCeLiw3cO/a6rLuD6o4HArx3e++jJameX338U2r74x3/j6859'
        b'NHtOv3yV75/2lDZOXxL9996MexzwiPMxiPKzXSG0J5tovcFp2A1aok22tTnB2/4hnCp4oozZLbHNEecoYkYc7JzJDDqL8oYvc5tC4LmnWH6bGSqxgx3gFup2YYHBF90N'
        b'NHOtwVk4SLJUs2JBS4OgyGyIWZR7ANcuFg48xUZHcGVaQKQo3LU8W8Sm+OAYWwS2zyVwzlszB8FgMpgu4NwU8CMObFkIbzI77F5FYL4eKRbCVnAC7omiUAX97Hh4BVwk'
        b'7QDnJEALWvBGYOMw8imXHHizkQPeXA+PPSU7ug+sAYdwa/VyKAZSjwUUFZO4Bu7ki13hxaeYMVfD13NQVlRbhBjng61wfyTOR8NroSqeA7gMX2a6cBCeXoNzErMv+rQI'
        b'fRjsEIGjHLgTDMC+p9hLF9wQrR37MtgfZhCCvcEgPnThdL7Q9h/YAYtlhPG7X8kmuikGVmy+C1BHMR7KjVZUAN755zASJGrj3nOmH7i6t6s60g5uGXYN6w246xr50Dt4'
        b'KCR72DtnSJAzEhiJ8joxeVIPbh52De2dchfvakF55g17Zw8JskcChGf8e/yHA2JRVkeUtU2N91rhrMbqkoe9U4YEKSOBEa+KeyvuByTrApKHA1InFDDWnTXsPW9IMO/j'
        b'sEQMZPBIcDT+DRgJCMJlRoJC2rgfmu2ecWBcouvxowE/1uIHPvtAqcIPPLJKNfUsr2lsaS/X/5k4T0/Sq49wkWno8T3q1m+LrFisStbXFH6+6Nbibn4MEsvTOWYbBFgG'
        b'iu5LKPpL1Gpq4l8xhYRkVqGQNWpXNiZGIRUP9wVR8Wj9FtFpCklthVQyw6QhhqgpLAM6UR0l9/1Ed/0Yv+fv9DxOX7FBHgpHvFMqqq9TbBD2sUY50vrKfwjuKgZu2zKj'
        b'3DURbOUu8643QCxAWci+OQxxV9mxMgbeqQy8TIUWwP2H4Kxm4HQqM5fNnh9YD/Pujb3rF8uAK3ymdPdPA65HDJsygzD1/CB7m/XvqmOrGIC9ZktUMqNs9k8DWGUA0CCn'
        b'PT+AfiiL8iDOQAALmlS++9eAaF2mlwCfH0Iaj7qxC1ceW6mHdFIJ8l8DqX2ZiZD5/NAG4QEfw1HxXT+xHkd/QEydBGrj9qJy9DjM1u9uMuyv/tfubXqO/dWcQvmWnyl5'
        b'Krz974B/FN4ujTfyMTtR8b6m+W75g4tKZl9hrY3hVPOphI/472Q7C9mEy2eAN+GOCVz+KAccBgfhzhngDcLla2Ev6B5j835Scy4fCy5PutfZqgzTlLKyJmcTHkNiCOPG'
        b'AjDeJ5drQ3n6dCR0zeicMewR0Vc8ILgfm6GLzRgWzdZ5zB5ynj1hU7MlTsfsacbcjUGI1zBCTPhwKGtsb9DXOTYvtjeIUI52fgDVYxfFEdqOWukpG7MBiK9SK2Uy9ah1'
        b'Q71KjZW6UW6lXL1h1IrJs2GU3yghdhS7SqRa1tcy9hWOWlI9yqtHc1tZaWcy1o6Gsd6LEY1r+ZwyhHwO+u2q1lonLVtri5FR66zlaG20VlWOBCntEFI6GpHSniClnQlS'
        b'2pugn91mez1Sjos1s5t8xLNgN8mQSlVIMcbanVRWgWkU+r9S7y9Ly4hnwnOYTohiT7RyCV2jqZaZGCtQv6rkSNmnmQ1V2O6gkqnFdBGapRPqwcSyFq+pymsb6pXYxmIo'
        b'VimpQ4o7LoqUfqWsUq3YQFdswAUmVCJplMgVEvxJoudib2uVGLdUjq3jiFboq9TbCnCdE+pAVWtU8rpqApGxGjqCDHnEc/RIlr61NdgYOBH2CfnD1RJlNfqG1ECHcXka'
        b'2/tVWO9WrdXg3q1QSirXyNQqYdrzm7MYbE+jM8wYOr2ceDisnKwY/nIaTXY8Lf/BfU+T1sJMrjS6mPzSy/VeuJPmN0zCNBqvVqChImaW5aZeuJOWxdM2jZ6DnvTyIqV6'
        b'8nzMxEZZmQD5RhSdU1wkio9NSqKX4xWKSUsz1CCNXpxRIsrJpJfrl/1XRi433dU1+cfHiAg2JjEvNK7IdC/BpMUR2UGdWYOmBpquqkqlvEGt594YT/EJJ2RuZShU9Qh/'
        b'ZVKLdjCETjg35p0KctYiGWwxnckYw8gUDSxWS2pr8UbjusBJzWJkMiDEQgA06KeWVE5Oe5Sgbl0nRzxath6NuH7CTawH/xXWq2XMNCGTX6auqZciSlKtqUWIhmCRrEET'
        b'EE0aGeqdShldj0Qfi/UwTcKThlj5VEwz5SoTkMR0FiJqBoJksRbTaYdtggjV8VmWlQrUYOYYS5XMcsly/UmW9ZUEcmZBdFqNWt2gSouOXrduHXNQl1gqi5bWKWTr62uj'
        b'Gc0gWtLQEC1Hg79eXKOuVQRFG6qIjo2JiY+Li43OjE2JiU1IiElIiU+IjUlMjk+dUV72whY4l0INsRJcUIF+FdgDr+ULc0XiQrxZORL0RVFUcDGvZhbsYs6nux1aHY9+'
        b'Y8HNdCo2OIYYsuqEPOpQpTs+OCn/nZVzKA1elOOy4Kt5BjvGAqjFR7HlihbikwsWhuM9/0ugFv8g2cMGdIAD4IINPOwCD2rI6WttvvAy7HVBj33EqmFF8WAn2x5oQb8G'
        b'q8g1oKMUXhbD1rwcfEQCqhyf9MampoLXwRHYyYU3JOGaWbim6wlz4eU8uLdgEWxrMG/afKgtRAX35i1qQI+i/Fx4mAs7QQcF94DtdvAUPAd3EK85eDzzJTuxMBfcAl22'
        b'lE2uNzzNhl2wPZ6kgpfh62A/vJyDKmFRHHAUXLJmga2iFAJpCBxcbwe10WK4G302CvTlwr1Qy6Kwyyy8xOPCHnCanLDpWciDl6MjWBQ7G56B11lJsC+DdG+2wor6cZon'
        b'PvzRPly8ktnou8QrWOUAD8Mr5KshTpT1Cva8NeAaGcsoONiAUx0cxLAdXsmHFyPhAQ7lsQFcL+aAftcosugpRQMwYCf2BgdRHaj78OlOrRzKDV7nOqns5dsvDvNU11E+'
        b'pyuLaofyHLfHOFNDnUfYvy9++IdlK5oO5eQ3NIvvzarYezx16xPnFXcl9GBvwejtwi3Dt6GV/YDklzK7tV4/f+gU+9UQ55PFTxukof/5zqX4g6UX/dYue+up8tjuoqCN'
        b'R79RU5+Dd87rdnwx/W9fbApcfv3tguSGiNxF18OLP3x1xe8zVy3S2i4KjFhUcO2TXVvPfnRo0/Sf9gYOrR1aO/hvD+j58d2fnvhJ6rUZ+75ev2LLadH3H1yozxjctmUT'
        b'6z+/jZy7tV7IJ6a5WnAM7BlnZAxxyuRUrdtIzqGIWz49z6LBLTI+CFzjwf10ATkDIIYVZJfHwwbecTbGOWAXMTE65MBdEyVwvgMH7uTAV4khcTY4B09FFoJO2CXKySnI'
        b'i4KtQhblDm9x47LcycEvtSIwmBcVno2AYFHW4Jw4jL3Bb43Q+Z85LtCiZQ4/zI6mMx4hYCuRSssYGa/J1Shzj0USef9zvbyfb0t50928bvWZTT2bhr0S2/gjrl4d0TrX'
        b'iCHXuBFxbFtWx0ydIJIxzSUffGnYNbhbfT8sTReWNrhAFzbjrusMYkmbc6daF1Iw7F04JCgcCRS28dvWtTuNCBNQYLPOOXRkxuw2/pBHms45fSQ4AkVu0GEzWzgKNbY7'
        b'jghjDfnoYBTStDs8cPUaCRf3KgdYvfj4wVSdIGREFD+QMTC7txS9z9AJIkbcve66CztWtHFGnAVHHdsd7zsLdc7C3qBe5bBz3H3nVJ1z6mDoh84ZJirLFEZleZ0y+PSe'
        b'xo8z+NGLH334cRY/sMit7MeP85MoOSaDgfu9fOyPHjubRHkNqz6WhkGItZ/ZKPX7v2DLng226X1LLHtPXti+h1fQz/CTqWt2GWyO0GbUXoq9n/Uy4qgDI/kbXvmSWvKL'
        b'j06TjdroHVQqZaN2WE5D0jF2X2U6wdj+SlsTJuRsYEL7sDpkZUkdOkrOfEWqD14+ZpGjeW20U5BqhI/uJcc0VzkThcjWTCGyIwqRrYlCZGei+thuttMrRONiTbX0r/db'
        b'PVshkhg9UGjm6MbnEPvn4n1kTG4ayR5oEJFEj+QpielB11jmiqKrlfWaBpSKVA3JRF5eX1shr5MYpLsIJPhFELGEkUqwTcnoOI8BNBpCJtSEDSP/T4P7/7MGZzpF0/BA'
        b'MTFGC+0PaHJmc5opz0QZKrAozi7/Adf3ST/H0AzmO3oyoY9jNIK6emy/UxKZv86yJL+uHovc8lqJYhKdYfkznP+RJmbZ/X9SiDF1Y+CtqK9fg+HFMWK6QI9dEvJO11es'
        b'RgNP11tWPxCCIA0yJSkmVm9CxYiA1F9c3fKxjQGTAmEkrmn0IpVGolCQmYEQp7FeXmmcjctN9hU8U4nWE2fzYSB7mJeb7j34QTUXFx+n6pp5uP8f0FRny9bJqvX+if9P'
        b'W/0/oK3GJ8XEpaTExMcnxCfGJyUlxlrUVvHfs1VY/gQVlmacSH4i41Hol45JihSdqcmnNHFYuq+0ysspgHuicozKKNZBy+3Ha6FbwJs2CUj9a9FgpWGTIzjDaJ/wmqkG'
        b'GgsuavCBnms0sC9P7FmfW4BkffOqx1eMD961AWfAbbhLg095lq4BB1VFBUX6gylx5UtgG8q+H2qRKmqL9DZUHXq/XrwCnADH1KHgNRsKKQ5H7ArhK6uI7hYKdqxW5cLW'
        b'nIKiPHwgYAzXFm6nPGdzkH5zYRnJAq/agTdUEQVwXzhWaMQ54HyIWziLmlrN4wXGM7cu3EJ660k7oRxeA/sWWsNWUSFSUNmUSzwH9IC9UZpQlCl6JtIhLxtOmc9fgE8B'
        b'BlcqYO9CfMx8LGjhrc+CPRpyKOCl+XBAFQGOMZDlRAnxifUC+BoH3uTA22SQ1jZwyNJHDH+l/7qaYIqYFUrmqXzBj+zQyJZQJWmwVYOPwmpIxFo4HoHdCIJr2Ug/b4UH'
        b'4RWss7eAc+gtH+7Lhse4WGtd4WU9D26H18lh92A77BAkFcHLKJxD5STPZ07ov5CQhVq8h9gvqNh1YB+TuWetCLzqpz+LP7qxTPHn77//Pmoal8GlrM82dCZVMh47y2bw'
        b'sf+vc0xWq7A3po7S4BO/wI/Sw3HXtOoNHdlRi/GNG9G5ixAeZMO9xeFChA3Zxus1hOAq6jm4HRzhU/w6h5XgGnhDQ8453A2vghPF8HB8LscHXKFYsJ+C/eA46NXgc8Fn'
        b'bCi3g62BYjJGC8cQxtpCF4EfwQNcCjQvslmWs4Ic2hsI37QaMxgsCIeHi63NrAPgIPrkTDe+Y/IaDfEHuZ4Gz6tyRUUFNhHRGIEK9fYBIezggTfgtRUEaHA+XBTJHDgm'
        b'5IOrKZQdeIsNLyfCl8mVEX/QFLF/zKfWDwj/zvm156+cVjBeTq7rX4KX9RYhxvEKX2CwO7qoYEG4vjJ4Gby82NS16yQ4Yw/beLCf3MTAWQDeiBTbwas5UREsig/2s6ML'
        b'wBmSFAJ2zs3DLizwFFKh2UpWCrgBjgo5JBF2rGrEXjoXxsrBvgIN1s7C4FHYgwu2wtv6ghW+pJHhcFBobGSenb6N2OVGrssXc1WNSBPb49n7+sKC4pdjnAtAdffrhxZG'
        b'Li7y/5vd9G+q13/Qy4n3r/mprnBw/fL/3Ofxfcb3p47Paktaf8Dr3arf/unXRz1mDEcD6/UxOzfk/PGzd0evLFjk+lK8dt8b8IZbeudHws9Zb314pC3twcZNRzLUj7ds'
        b'/K0w84B19ctrZwb89T7XA1y2CSh8fI+bHfulJgGGj7zx8PbPW2tG5Hu2zal6qXfOB8F3HP5iZXX7Z1bD12dk7O8SfvKuz6O+bdrIT/s3xb79sOT3r0xv71h6mXv68qdB'
        b'Z7q83ugJPPx0571172fk/Gz9qbTEDytW2Z9w6/z9b2ffLf7wL31vt/3WI5U752F/70t9RUfu+386eHMofVXo1WO7JDOufLXeo/PkhzM2HPhk07wb657krtvrctG7+ugf'
        b'35b7PqKX1732+XCjb/s+5em1V1p+NDjtSV/vnxbMvVX29cHhGStPPjwX+auduj9c27jpzLW027/qUDZ99KfEqz+e2TLTZe1XXyT8SP39wtdXt75yybPv80ULv8z687BT'
        b'8TJlo+C4kLmMAbwFz3uOmXiCEJ4TKw+nahHcynhWDYJbK/RmngHXiZYeHtwPzgLGmwzuiYCddraxFrzJWuBO5mjTnRz3PL0/WDnYiV3CnBZzFEJ4ipzpKIan4LHICIRn'
        b'e5y80fSzWcYGr8N+FinrBI/DlyPFcC84gHlEFEbDfWwRbAtiDqA+B7T1efk1LhF8ir2SlQyb4Q1iGQrTZIFz+QVRbHAdnKO4eSxwqRFoSZUlW3IQL2mFb4LDeicw/kvs'
        b'MHAE7CIWrirwJiIkE3zFWjKJu5iK5xDoTPLBw7H1Jt5nzNLwLHDc4AM2AN4kh7+CY/BljgrPTZEnaMPsjljVpsA2DhhgNzI99BZq8SXGkgVOgguMNYu9YXmZ0O1fbcua'
        b'3MiF5zWRILZutWTpcsTWlDF9vsnDzMwylkAsXtPZjMVrsx3lHdw9tzcBH1I/7JXaxmeMW9OGPcKHXYW9mfejZuqiZt4J0EXNues6h1i3Mu7k60LmD3svGBIsGAkUM9Yt'
        b'ptj0YQ/hsGtEb8l90SydaNadWJ0o865rJik2+85KXcjCYe/iIUHxyLQcbAFL0TmnjoRjc9cmnXOIiYEsLBJb4NDbSzrn4Aeufh3S7jn3XMMf+IT3CoZ9xG2ZDzx8GCe3'
        b'60GD0ptCXYj+cgxUUl8KW+4yDqSNJKe1ZQ35xN8VJHysD+oECQ/86G7348vv+0Xr/KIHOMN+CW22I67uHRE61+A+197S+6LpOtH0wcph0ew7cTpR1rBw3rsBd4V55Jv5'
        b'7zbpQpYNe5cOCUofpqRfn3cn693FbxcNTysZTlmEm5Wgc07EJrvEdPy9WJ0g7uOAkDNePV5tjiOuHkfT2tO6uffpWB0de9c1diQkfkCiC0luKxzx8L7rIR7yFw9wr9lc'
        b'tBmcMeSe28bBYAXf947Qof9dI0b8A+/7i3X+4l6Vzj++bd4DD++O5O5UnY9o2EM8EHLXI/mhf9hQeP6wf8GQZ8HHHj4d1d3VKDuqeCQyusOq2+quZ/iIl1+3VS+vx/Gu'
        b'l3hEKEKxvGOOH4dHDZTcqdD557TNG4mKb8u8LwjWCYK7i3UC4YizR4eNzjlQb1MM/dA51sSM6MqYEQfxA9vYlTfw4yZ+4G1NyjcpgxnxOS2I4xEff2q8PdFoUvwFekyK'
        b'66VGsyI+QnitLYslJ2ZFOesr8nxRs2IvP4UatMvgcCoNxwrgP+O1T02UuQnwKKW10tpoueTiJ7bWnlww4qBl6a9/4rGp3cZ9Ipv4xNzHMzH38U0Me7zNfL25b1zs5Ad4'
        b'T9QtHBnd4nEamxFbF08J3yJLoUpIrNBRLyVWZax/U8CniBxRDq86q0Cr9VrQOZ1DcRxZKYgjEVEayVi74Ctgb2QxaC2BrYsKFsAr8+GVRQ5JMTEU5efBAdtA/wayAhYL'
        b'bgaAV0B7MWwtSYyBexJi0JfWsmA3bF+rX5NCYrWL2FATi+JFsMCxSKSe4PF/qTGQ66+/72maLRwk90jZgVe84WvwdTYFDvlRoZRncQiRicCVeEEc2JYnjkmIS2RT/M0s'
        b'8ApHQr6yaqVNJOKox4wXJTG3JBWq5S8deYmlQuoEtan1TmtxXiGMcT651iX5Lf4e567F1qdW7fQZqEp+9d3sqEuzD2+i8hQ3ZvkG/tu+/IDzuVULp7x36auq3xz/7OLf'
        b'FtjYb5r9gd/2P9/Y7FhOL74Yeuvf30p59EH0b8T/tjv+gEfbk5K3HTrbbv1i+udRP9G47/jx8ZGUyNei++9V+QuXHV3e6jb/RsYvfi4T/+5v/is2JJRObU0qPZRecun7'
        b'zr0LfvX1mx/93OfU2+VvVa/++U9O7l8U9B8L/vO9g8t+DVef0PT0/flTh1/nPXyl7r2w0xu6sv9zy9J3tixb+83vfrf6XnNG96flre/fyCpvvX469o+9SbcV2Uuc47qu'
        b'+/S9/ZfO79Sf+2b88vTDj3LVW+b9SZof8dPv/P1Tp48smHfmN7m/+UsgL+KN7zZvuf9w4ZMVC69svOk0f9oWTsoqaazyc6ELEQ0qEKPuw4OG70uzotjgVdYieAa2kMTZ'
        b'DuBVwuPBWXiUzfB4cFN/inRIxAbY4gpfNjp6Yx6/FOwg3uDgdiO8VQxPW/YIRyzeF/YwF1t1iOBpr4Tx62GcqmXgEMmwfi3i573g1bzCKKSz7I8GZ7mUI7jNKYOnNhMB'
        b'Jdl1FmzBK6rzVvAorj8LvOoxnfGB3wu74IXIcPCW6TU1URyrumnMNTLdm9aBk/Lxt2rVwwP1T2mUngJPwyt5pns7WEi7KnMH57k+SLfrIpngsTX2eWZO/Oijr7Mol9Uc'
        b'0A/aU0lvZIOXE4iwB0/OtrCsh4S9JVIi6oF2eI4NO5D82GLmmO/kz1k134F0e9DCEO+aPBPffyzogevuzE0PV0DnCnhIaLpix94gtiMn0zfC20tQveT2L7hvqv4CMLhv'
        b'EemNctgBTyH9ftfYqeLkSHFwUE1KTwkFzS7wFaSQoOYW4ZPtQRu7HrzmI3T5bxSYXAwC08Rbq0atypgbq0wd8ZgYIh+dYOSjx0sdKI+pRxXtioN1bRwsiFR3SzpX90bc'
        b'c00c8aG70jrT2jJHfAO68jrz2uaOePu3z/nYx78rpTMFR0/tyunMIdFtc0ZcPTsS7vtE6Xyi7rpGjfhM7Q7AmR6zaW+XEYH3Yw76/VjgebSgveAxD4Uf8yk3346M9tz7'
        b'gjCdIOyxFY6z1scdLWovemyDY2yNuUJ1gtDHdijuiT3l5tnB6bLvtB8KSRr2TB4WpDx2wJkdKTevx0445IxDU3DIBYdccUiAQ2445I5C5BMe+M0TvxW2Fz72wpV748pt'
        b'u6VYMpyui5o+FDJD5zljWDDzsQ/O7Isy6yH2w+/+KPtdQWrnnG4eudts/TCdMuyb+ngqTqRJYjJK5Jyx77HvXTpMJw37Jj8OwImBKPFxEA4FYwBwv4Tgt1AUfyCnI+Nx'
        b'GH4LN7wJ8VuE4S0Sv0WR6oUdmV0FnQWPRThKjNsYjUMxOBSLQ3E4FI9DCTiUiENJOJSMQyk4lIpDaTiUjkPTcGg6Ds1AoSczUaiN/3g2i/LyaeN97Ox21L7dvnNlb9Kw'
        b'X9w953h9REdx19LOpd3VvZKe1fdDk3WhycN+KfecU3/nH9KWNSLwOprfnt/j2r34NZ8PBaLHHGpq6Mcefkc3tm/sTkRC9X2PGJ1HzIDnYOqwx9wh57km4pcjI371E6xm'
        b'luVUozyVWqJUj3IQRr+YrOVokLXGiVm/o8ydVpm5cp6lv+jtb/iGBgcWKwpf9Bb1op6rr/DF1I/sUjn/aw7NNUL2d7+fYKll9verDdtt9SteCr0hWilTa5R1JK2WluAF'
        b'VRO79nMtRtJrZBtUqJ4GpUyFt08wBnP9CoDKuAqqt55bWkQcv0CqYJYdMDgVG9QyCwZ+MwnR2oKEqInErGAruDQHtMAjYD/YDVrBGUTqD4BLSxAHvwjOLQBaHuUJtnI2'
        b'wgNNjDnyTY0TPIhkYtiSKqbENuAwscmu4eQj4RGcno/kx5YlIngkTyzmUAKwmwP64EHwGpE7q+djI2o4AqFcsYp2oIjJGhxFan43I3m2gL45VhQXvM5Csf1LRlllxGsI'
        b'caO3WJHinKgIxJN2GuxfbSLGlPcaC+40lSfBSQUSKUG/gIi1GfCtkjzC49hKsBdb1XaCkxp8ZW3CWtBRjAshuPeiZNDK8oXHw4nM6eMJD8CDqA1CByQLZ7A2hm6W75me'
        b'zVFdRImd8xIOt023Zcc6Z1WHbrn5J5tbu5aWNnGW89ozRnwzQk/+fPvI7p0jD35/INT5yru2x6p2PQ7d8NsVn9tO53qeaP5u/aLfvrPw6EAnq9+GLu9+u6n48t787Rdv'
        b'uQgiF1gdv/m069yGjJ7s160WtJQUqU6eV39x7K0vrr5TaBV07OsEH/p4WX79u4vtb0773c0pN3b/OdD1/ubfh07dd/Omwx6le/qRl/ZP12742Ou3761Lq5Xwvnhis//V'
        b'iKiU7UI+sX/kL8PrBMTR5yoSekzd7eFOJwWRDKbNB836Kz/AiRA+ufID23KJCLUO9KZHigvYqK96Z/FYeUgqHyClCj2LkWSGJY0cEZvisO1kbNg9C/Q9xe714BYcBL3o'
        b'wwgTWsYdVcFYaOCFZOa6ksNzIrGYBd9kmUla4DR4RWj93MKAtVEYMIoAElUZnrImZE0fQ0SAjylGBFjoROg6YsghwjOFPYX3g1N0wSm/Ck5rz2+b0+ExMjWgq7GzcSg0'
        b'aZAzWDw8NaMte2RqVO963dRkFAqNOKPoUQzED1oNh85qm9sRfqDosRUVkv7YHtV2PzhBF5xwPzhNF5z2q+Bp+vq8/ToknaFIkPD07uJ38oemRg+4DlR+6Jk24jm120rn'
        b'GX7fM1bnGTsQfs8zHUfxOh3ve0brPKMH+B96Jj+24tLubdlIMAiL75YyH9eFzh4MQw/9952okOmI73v6tdn/Q/sXvjRnBfo++9R0/8Jcpxe82+QUKtjHGuU2SNQ1Zhdh'
        b'GZVYvAnnME9/ERY+wAJfqYwvEOQbL8Myasb/9GVYiB98wmFZcJ0ZYwmYOqskjTikUJgyh+c/hQE3No3OqaIjcCiCRixVxSzSYrIvW4+PssFrlhHiJnlDRBT5kJ7/KC0v'
        b'earwCeBS40KrRFlZI2+UiekivC68Tq6SGXkMqYM0gGSX0FX1CsTQf4BhTLxR2rqQ3PDlC19ZEpmNaMf8bKRz5Bbkg76SbHAeaqPESBfIhrus4G7rBqTDvEGuEJO7gr15'
        b'iNbkFojhbqSVlUAt0iAXILVDFI7PcsyDV62Q2rgNHAGnNxCGEAXPoYiD4BzcEwUHwBGK4iCCvh2+Cc4RDrQZ3ACnvUBrJAJxPbUedC5nrqy+Oh9c8F8QWcSmWAuRvgU6'
        b'I+S9gd4s1Wco8W+NdOuCi7YgxvnNvLurBe2BgXNP/pVttWWWutFdbWftdb579o1B3op39n9e1DTyE9vY1XGfrv/2Tx999DPR7ZdrVz/e/+8zqmTbZG/UTw1sjlB/zuOU'
        b'tl4oDTp7YMu6yvqPSm98cd/tw+MHt/9px1c3/uMzwZavV8QNXDycO9Lbe+td3dZCsMduxJFK2tsR9Rlf88vPvKvWv/2+5yfHbOlVM/t3Nzj+bejOT1f/8tKOs3fr7Xd0'
        b'/fqD25X/Uftua1b5vk/OiHddFy369FWvT4H19G/+a9f94r7PNn1VE/Duyzb5ATBozlLXrM//8OP7DZnXN1Kpn6YeSdkidCImd3C+Hm4lY1SAVDJuMgupo/ASo8weQbrf'
        b'FayqwpY5aXAvuXqshb0J9JWS9KJSV3gZvrGOLB/Ai7CbTdmAM2zwGsWolWAXGp3XcHlxChpVNsUvZPvOhLdJ4dXloB/x6t1R4hz0CLNhU3ZwgA1vCZESjwurPZLyosC+'
        b'InxvnBo2syi7WUiLVcieYnY8EzEeUjraK74I72TfzI4A7QLGKt/uGwNaUzEfF4rh/iisDzvFcKpLeKQo0qBbZ2Cu5cTBV1URpqUAbzE8Zf+U+UvA8chovJYuEgvZiKV0'
        b'ccBOeAG0EoUV7FsP9hPVHK9HRhfyKP40tkcduEWqrgQ/2pJHsNt9DcZvGwEb9GTOZW546wE3wSG8glGITSFMd8xmezpsJq31i4GnDXp0isigRne/RBI94DEHDFM86MLX'
        b'v/FBLxshOzwttPtHVWA7ymzNgGF8XDztmxyMFBy/EpbHZzEsL9eZErgfTW5PPjqjfUZ38D3XsIfeAUOBhh3lrm4kbXr79G7BPdfQ3rgLaX1pA9J7kelm2Tx9sQ563LGN'
        b'p7d6H5x23zVc5xre637PNeaBd0B3cC+nd8WwdxpSj0Mj8eVdp2s7bTu4HdIRTx9ctrukN+FDzxikDYUlfCzwOJrTnnM472Mfv67kzmS8Ka83+J5P9Ajik9ad1t2CE47j'
        b'anngF9AdeCasJ+xMVE9Ur3qgZDgwbTDznl/GnYUjvv5d2Z3Z3SUnCr/lUP6zWUN+GU/wZ37rl4GC36nwgUM/TnGZ68Z7x40319+GYZI2DJN8OgmnHN/72GRs1KQY5mnF'
        b'wtfcmXX99wYlCtuoNyLO6Yl9Xl/4QtMj/FDqtF0sR8gcwjTKmbtoYSG5aEopx7BbF+r/hDzmh43+uY472xfvjJTWV5aVkS34o9YNyvoGmVK94Xk2+eN9jcTDl9jkicZI'
        b'ZAXSZqHgf2SNDAuk45fHxjofX7TXZDzeCgOoqmWRM9eecNkOzl9aU45uPZw+1Z103bIVD/wDelOHZq96ymE5lrM+nps1smDhN5wgh9CveDjiMRcFn+SyKO/AB86iEUHS'
        b'Ux7bO0Wb+4RPeQU8cI4aESSiGK9kbQ6K8Q994Bw7IpiJYvwzWNpCfMkc/cA5ckQQjaI8Y7XZYzGpOCadxHhMfeAcwcR4pGvnoRifoAfOYqYiH1RR3tfWLIc5rC/5CPDO'
        b'4h7Vxfi3Xd+Lf+BH97leD3o7/j0pBr6E9fGCRSNLV3zLETnMZmHoSxD0OPzlKhZucdDF4rdD3rO6M/WBj3+nuiPiIgfVUqxbvEwnkeEKqllI+C3DHtmcIpZD3JcUfuJ6'
        b'UAIXh7+tYCc6ZLG+ovDz6zqWl4Pfl0kYpKB7Dv7fst0dIr/iUI5Tn+DQ2PnN4OqipfgWUZHK0ZFDOcDrHn5s2GMHXiG6Y2E6bLUDvWqwDe7EBk077HQyH7vp+MZxg5S5'
        b'/4vXSz/H1Y5WhRonFF5WXVWMWEIfnwqgApw3Ed2ztsQlTwwGYhJRuWobeJW1djF8lXSITUFaJF6cAM3rTdYnwBGacak5EyeCLfhO86NRWA+K51LWoIWdGxEivyQQ8VR4'
        b'0i+OWo13WuNd1u0sTv+uuyv3Cvcu+6Djy1kr+wc156t2POKfrfxpyVFwCNw6ZpPjEOaeGJV9OkZwsTHudIw6Lnvbh/SbVvENVxGUL00R9pYKeUR0qKlxwn4m5CSYBNiC'
        b'D4OZBboJo4Sn4E2ZgaFhdpYJLiOO5uDPsNGj8GxGpNjgGlCFfbPYokz4JpEM1sPt8Chi31x4zNQsDM+CLoaDv7LFLS9nCrxYoE9dyZaJQeeku7rtG5QyJFnLyrDbZ5PZ'
        b'G2FviymGvc2aQgk8GYakzfzY1f1oSntKR2ZXbmfu8fxhciw54lfp7ekd63pthl3jxt7XD7uGazMfOLmNePh0zOtY3LapjYvStHmmetQoF39wlM8cWvED91u7YnZgBmkA'
        b'2+Rm6y3OLJb3i94RaYaazvrfr36Dj3i0MzniMRrvzybzwwYf9ijjStk7KCmnn2s8JpFHYnkolm8SyyexVijW2iTWisTaoFhbk1hrEssc9sg1O8CRqz/scSzWFsFjheBx'
        b'2mFdaieN0bKqWFJnBJu9Pn4KPqxRGkviXVG8Iw5r+VobrW0VVypAMU7SOBTDRXnd8EGI+kMX8UGLnCoOenLRP57hn9SFHMFoqw9zxoUN6YZfriH/uN/x8eRd6n7CSU5J'
        b'PXD5gyypJ05Hv16m30Dv3oZyKOxjEvY1CftJ/dFzqkkMbRIOMAkHmoSDTMLBJuEQk3CoSTjMJBw+Fh7fXqnwBPt1ljTiBBsfLSlzkU2RRuJpvjqMmvBnoJ2GYyf1+aOe'
        b'Nz/5ikB/5iJzjoBtlZVUhLDAjRyMaUVGnicVoxj3DS42VcL4UZsyxNwlWUi/NVugNxoRsACDTckmC/T4WEcuqhxf8M43Lstb/cuW5Sdc8M6hxjMLW2ZZvmsmWYB3Dp1d'
        b'HvVGtZBx01zs1kp5oi4JWVwuti/PZCLnzn+J9Wc2Rf9XqmSj2FpJafA96EgF2w5eIWe2Gbxb8+G2EFPTGqLRLVZUcbW1M3gD7CJV/TosiMqkKOuNjuUVhzJWUJ8ZwCQk'
        b'TV4iPstRYbcG+y+mHn8/CXGWiwdDXmHxOzzTOtOXLYmfvX6WV5bAi9+R7zEnbI5tZZIrZ06sR9s7h74Ad+YHU9LY6uOcZQ9D+mM2CaNiphfsPUm7dkriTuYL7YX9C+lY'
        b'98HVzvvddv6U/9lF1oY/NvhvTHv3974xm0M46q+q06gOqXfJZzOFNoy29wZiNZdAJ97+iK8mRrqTdQlbDW5sJLzCD3YJQQu4gH3KKHgymh/GnhIFu4i25y8DV+2wA1xV'
        b'3jgXuL4VT4kvQ5sC7AAtq8FZc38xpr9CvHg1KHSGLNmuxdeAM2efRSYkhYuYfCiXhy93WiN8jVn8BRfx+WM58LhfVA5oJavXe7FP2XEO6FkH24jhdQ3UCnEmZ7idyVQA'
        b'+imU5zAHvJYIrzIL3F0i0BxEdnwiLTQH7sUX4e5hI2DPOj4VogwrwOU40LIO9YcajzyqB+wvQsx4dxHcl7NJzKdS8/jgSDE8IuT/gOSM58iEg81cjPPJ/GSzDRTDSVdM'
        b'oaYGt3EP2WGHKsHxZSho+8SWooO6pw1PjWmzH3Gd2h1w1zWo135AeTc8dVDxbuXdGQuIF1X6sPe0IcG0kZBYfMpY4EhgZO+c3oXdYnz22UhACDlyTP/jT+NPjAQEd/Pa'
        b'uIcdTJgto4+N8ogj/ygX7wMbtR9z/6mrH7WR1zVo1OQAb0umTUZD0y93Pbvh0WyTta7lU1isFKympbyomtbJF1J9dgn/1MljvDLc0snOGjKB3XDYUAbb9Gik0mOlzFFD'
        b'vmMHUE84XEis1FLjLlB/XihrGCgdykxH4gWgzWSbHd8VfdcvmoHX3wTeiWeNif+Zw8Zsy4yI8gKQzkOQKvE5OAx8fjmGOgzbov5p8IwndmEUL6uVT3oelgXocjF0Y0d2'
        b'uWPFl65S1tf+82DVmIMlWf8CYBWYgyUgYOEteP8sUPrZwS9T16sliheAaL7Z9Fh+bLn+8LUSXI9hZ9+k4P1PLlRPcPKbKE3wGGni40RObg4Hh8oVCdPYjODwdD6/4luK'
        b'HL+QX86dS8lFf79GqWJQSvv8IoPmyHI9FZPLfq/i3pyf5GaF7ir0Xb04fvaHcYtY75Xzf2FPTfsvq1USNyHrKbb7czznT8Z+YAe4YGBA7qB3Mq2NOQ5riim9HTuIC7M4'
        b'zGekLpSn79FN7Zu6F9z1CBvx8cV+rwld0zuxw3Fvhs5DNOQs+scP45r49WK2yWpWpcs/sJr1v2ifeI7j2fRIcjuUhzTErUVcaqtiaUafLXH/KIv/NSrto0XVsjQ/lu/9'
        b'7A9cgiLTH//x+Pv5Kw1Ioo7LZr8XVZXfKfiJ4PSH+fMXpTwdpd7L5f9CTakcrfKPrRKynxJfgt1L8sfjiCPcZkATA4qATtjO2Ayuwn4FPOaMbecRIjFe2N/OjveAuybV'
        b'+53KyO5JeZOsrEJRX7mmyctkPM2TCFZF6LGqwYUKj8KO5gOLdGHp98MydGEZd4LurBsOK2rjHnVod+iQ3XUOnoBWozyyN/AHNPvZWLOfHJClpmp+LUIwrxdW88fTICwG'
        b'f4VNnIyGc5S5PYCq4vw3oNgEOjRxZVB/GvZb2d8WvMEZsaLml099FNbAuBXHgHZ4GZxDeZsosBXsbgLN8AxZx4N7XP0AtglspED/ko1g23TibcybCXbCDrjDTL1BKFUS'
        b'XihiUQlgN9+xAl4nu92s1nA3f8hxxif42IdGZlFk79b1ELx3a32ufYPE9deeHtQMSpOGcW0AXvQ1HFE9tocLvgyOF2cbENR05xbogZ228NiCAsaMiRUTrzwn2JJjMMnx'
        b'wFVilUMgvipfuuJXXOIc8tf8L4+/Pw1NHN3OgMYwzhzRHIc5sZVOPq5zwood4Oosfky25INGSXm4+znJu9v30C8LQjtuVGzz3iX4d4UKEe1dgX9yqRqcZpd/e/cUaV2Y'
        b'yt3OvXhpyLbg/JCzf1vUkCxInZ2/9eZe0XKOwif9oW/jjtpZx1Nia0sdXvfyGrgZ3OLT8h8p5af/7e5hUPp2ydvcLzkxh9ZffFcFNnEOFVQVVl1iXdrYeDmmJK7hNIv6'
        b'aWVY+d+mCq2I0lU6BfzIsL6mmGFcYeOAFrJVCXZkwP12hq1Fa8PGNCu4M4ZMfrCzCZ7Vz34R7JvAJAyzPwruZXbt3MwB2+wi9AqYUVuDVyqmgstceAF0uBG9x5sHXiHu'
        b'wVj7QtgA+nNBq6FSPsKvs3yhlS8aKKIcllSuNDq1gt1xxK81FXSTNbfV8KLVmF+qNx6+Nna9eoWQa1FNwuhtPKcYiRrrlHK1rMnZZJ6TGEJnBhg681WjC+UX0Jb5wGfq'
        b'iCdNONfBDd3xB7b0qi9s6ts0WHwvOuOO9N1KsOahf/iQMH3Yf9qQ5zQjh+t10flEDXuILnIGMi/b6DxSB+fc9Zj5wMe/Q308tZd310f0MFA8FF04HFg05Fs04ul73zNK'
        b'5xl1z1OMV+AcOh2Y997ie56xI4yHaXfgsCCkV3DBp89nYOmwcIZOMOOeIOSJGwLThNrxGWrHlSirVRZZKd9A8QxXPWKSN6ErVphQum80Lv/AytZBfhD1mp2YU1jJtcTU'
        b'iGcIy2DUISYdTPrYVVxC+LhmniE8Qvi4JoSPZ0LiuJt5esI3LnZywjfxEDKrQsYn7qI0DOCNuFPh5TRq6iq4gxyXT9YFHB3nR6LO0pTmUJpo2EFcFXIWgJMMSQQ3YSfV'
        b'lAOPyd1jRGxyYabm4I+Pvx+HCMh/3Sam/VMxjXHr4vqrdj2+0ZHe2eIV2bkQ/VZxZFXxpwc+kNlUffwBRcXftH2wWY0kNTyOcADuDwQt0TngfDhAs4T4abMonxqozeQC'
        b'Lezb9AyM32qC8WRDvtkwkxiC8TEMxj+e70p5+d33DNd5hve6D7gN8oc9Z7bxHnj4jvj4PeZQnn6fBIWe5Q15iIecxSYYZzXmyqrEu6aVbqwJUpzKimJUdiOnLR6PdgQe'
        b'uQHt/ooPFHJlsUJfhMFaozrNsM3I34gJkWuCbVYI37D50IbgnNV/A85NMCFakucY5CIstBl0RYCDqAV+VGSg3ypwTa6eG81R4Rtbpws/O/7+DIRH57ddPNC+u+f/a+47'
        b'4KK6sv/fm0IvgwwwUofO0HsTkd6GXmxRkTLIKE0GEHtDRbGAFWwManSwYkdjy73JrskmG8YxoaSZbJJNdpMNRo1JdrP533vfAAOC0d39fT5/P/jmvfvuPe/2e86953yP'
        b'6d2/Fc969w1K603rKJO96Vfe38pbZWHV/B4n93WdHOWbH7z1j6zwA+d3lQcX6anmfIX4/0Aqy97or87/GGqwFziT1aaGz2SZPqRPDjrUHclMo+FGgklvClX3pjmmFH9y'
        b'81TUd/ot7OXOCtP7Fl791nZy7oGU5vh+gZM8T5GgEgSgDubsdtK5x8K3h+er0av0XqBXjc2z3kgnG94Rm4772fjZrRzaG8Kd7RXc2X6gXrLHuY3tccMTSxmluWlN5jdt'
        b'9QzH/T/obc9ID8+ydkO9jej+bFicmOM1PQqugXsCktgUV5sG68DJROmm775kyTCT9XH+0wNvh6M+9yrqc34bOndda2ih9VoF4ZOnzJoe+/Mhg7zTBga+8yxzzKzYsZsO'
        b'If7CkkqfrRu34Tc0deFmgpds4FpxKrYhBptA61w6BJy0Rsz4hD2OO9Tj1Jax+WrPQOouJ9Bow1FvSK/zVPe6suFe12dhJw84ze6M73I+ldodrPSMVrnF9DjEKi1ie3ix'
        b'Gj1NZ0xPG9AqKSiqqawed/XU0ehiTAfD1ooTZ26JZh9bhPvY4Ev2MfLJfVqu1Al9f7bImDHRJMaaxGwTG3AOGI7s2S2SLB0wrKusLSqVVJMc+I1+9B/QL8JYtpKKGkm1'
        b'n+aD/4BOsVTGgNBi688Bbl1BDXbZJamtKagnrqOwAsmAgaS+qLQAOzbCQa+SmFj33W9AbwhEVlqsAUh3nMSokdaUSVBdY62Warz4Vy/CF3z+PcaVWPqADvYijEkO6OO7'
        b'IdQ3EkyQsMn3/KsLaaz7gkGECivrCfDdALeqtLJCMsAuKagf4ErKC6RlItYAR4pSDrALpUXoQTs6NjYjLz13gBObkR1fXY2nFbzdNEoyw3WOD7sfVVBDxqH7KHKghRVY'
        b'8aJBNeqV6PwfyGjPLBtWzwzkIkZGKzEj50kz5yfJlr+rZU4xlpTrwaZQGbxiXM2NMKNY8DjtDvcGEZGnRADaZDV16B28rE9T2nA/q4RnBI+BAwQuNTIc7PHABmZn3JLS'
        b'vJPTshbAfbAxHZzxhDt8UrKSPFN8kKiFeHwGPkSLgrteMYjVKyWrV97saXAXOAI2Z1FYOkxzrCSIokiKWB8egC1Hw4JoV2x9emY6iZ/mA24EpML1aHQEUAHwNNhF9PjB'
        b'VbgbnEAJWBQ4A6/RbhTYbQs3McYFu+EVuGcYJ5Om9GezxBXwrBU4TTgxuCHNHaXUovzyaREF9tjCs2SqSwJXBMRaMGpZWhAS9eB5GmW1ew6pw6gV7lQuau4H2tUxER6e'
        b'FMm1J7gJdiJSNFUIWmh3Cuwtm0wAbVa6B4nBxrneXt5YwzDNC25JpSkLcIwThaSZG4Rg1WR7KoqiQjP1661nzq1hCKZl5SJybKoCnqY9KdAKtoBbpEmKYOMcD+MpGJw1'
        b'mRFljME2diHcVUqIfeBpQaGJjRelUzOnZ8lchpi9NmxC1LQpIIfHaC8KtGUUkIIGwja4BklE2K86PAkbKI4nDa7bJjMnhqxp1AqKElBhyyf9MdNQ3VkOgatpAYEAiTyw'
        b'EaynvSmw/xUX5tWNYB7W308LmY9EdV0/FmiFLYmEFAwTU7tRnclLFi88qFfOkIIN4FAcJsWhSn1pHwocgBvAOpKvWbBjCsYjjbKFm4l+5EaWI9gBjhFiv9oyiEnzLcs9'
        b'v5vOY4oYHmQdEBiMiN6GF3CF7QF7Awm8j+sCeEgMLoKbWFJvgtvFxLDACDSwI8FtcI5Q9HAIoxC75+trXp69ck4Js3URXA5OIZJIJr0It+Jy7pPANQQdFzbD9fCUmBBM'
        b'H+lclmA3OAZ3csAWeNqEsVzZDE7Cg4iIFkYtasJlbIWnQBtpSF6GtxgcKWGoMC1pVMUO1QGvMofEiaYU/pgwuW7OjzNXMHmCneAQPBbgj7osuxYXc+9scJsMA9ncuaTH'
        b'Zq1IC2KhHnuBhrsXgf1MRe+axQ0IQiw7uAAv0f4oFdwKNjBt1jkbnPEQe8ImF7gZ9UwtKWtyWBbzag88ANcEhKB0prCdDsV5b7Qn48oLnIeXPZguuAWcoyiDCHZ4HQ/e'
        b'gkdJNsEpeBUcQklZVLyIDkddBFxMIJpPebk+Yqa+RNhE14DHhg3wNbOSMlLmuAgdrMfi2xW7qmy6YyXTsmAXPLM8IARx+DLE6yJibTwBsTaHXeAsBuRpRB1xL+yGO8So'
        b'pxSxrMA6eIgpd7cjvIZScqjZ8DY9BSOAtMIjDOu8z6tGLMbnsMFlrEo6Km4KgVUyc1yM4rOoUg86AvXHwIUk0yK4nuyOpIF2HdRaW1E1mbJ0QXsGyfT7fsupx6hv3ylb'
        b'ZP5VwHKmb2cZBYKLvoFcCs0LR+kYCrTDdnCOUe/aDxuESCpDDc+GR+Blig1v0ajvH4sl5F6fnUBtRb2jWXuVu8LYgSKtqwcPwf2YIJsCR+EaOhaN5FVwG9NOu1Gf2C9G'
        b'E4sWZcdlzaN9UHZvE1pPtCdTqPl8e7zLV1ynp6uH3TVzsF6c7JnM9YbNFIdDg3YTsJMUH82kp+bAXSLMV3lT3iXBtW4oNBNeNDVFXRmbeGcnwc0ZXtMZLX7YmOaJ5iCK'
        b'SpykbcXxZEp3MDBjCFgKytM98Dl2KwvskcSO+JC7W86gaT1YvKKsdXUixSBaNZavhLuM4HUtNJtSnuICMtS0a8HI/D10VH9rBlpiOJQzOMmthcdYzFA7BjqtYVNW0CyB'
        b'L9zCoTiT6LmoG+4mRa6Gl0CzOBdu41DgtUwaCd2wa+UcMj2ANtEqsbcGIBrYxiKj2TmDK02bw3TnteBWADwAmoL1sc06+vOBLQze1O2ZKR6oKtLg9iSvFCJqw0vwWLIf'
        b'h3LJ5frDPVWkwOVsKyoQcwhT50c89nZX9+tbk8FNeGCJizamg/7s0ZgkAvxaUdYYoj5wU7Ifi3LJ4waAo+AS045X0Yy9U5yFllWv+QR26yY4ks5k+Dpsts5Jy4LbuKJa'
        b'irWctrYB7Uw17QoC3eI8XBNoLHTQ8FXEdK8GJxg09ZvmYAODO2cJO5NHZjY70MSBV2bok0VTD7aVoplh7RRDPOWjv1xvosc5Hx4FCjy4vZPTUapkL38OZYVGfgu8wCmD'
        b'R8IYM42d4JAxPDBHn41tCdFfUTxpBgOwA7aPSsxCiQ+AnRJOuTXsYlbrLhu4ETaBA3jwSykp2OrGrPJHDaeIM7HNwXCGjU3ZC8EJuIupaAXo9ER8xHG4D2/SUHbwCkVy'
        b'XAxux3swKOeoY5ENE5qyBpfNnTlwC9w+k5lyd8+bhoq7FR5CgwK8hv5AmwOZQ3TgQaz/z8fgc9QiatGK1WQEuLtOE3t5JYPTaYvdUrB2v2kUGw2sg1DBtEA7GkpHEcUj'
        b'8JYB1nbBCi8NaADiohgvBYfELvDMGMN9uAnKyTwAX4MnODJDQxY2ijxMo7EHz0TCDtLJNgv0KVRcnapFJQbTikqYLQJwBdxKhE2F7qjklVRlDtzO9NumGHgGsW1JqIuB'
        b'bhkGkvcieRVacdC0egXIyWb6a4XOdA9bYG9ARVV8HPrtNA9mqGZZe6OhdT2J7Oovg+c50off3efK8JmL+aPZe/bOqjSNNvjjApe0/WmlA8c7mnuyU9i7/3k8Sizu+Ojp'
        b'SlOnhJiBG15Lk46+K37zT7eE83h2DvmTKvsXH9n68SwHZ8el//qt//Chy4+m/JYYd9jn2x173423H/DPzC59f++nfwlSmZ3Z+rDxh1UffPDkHXdTn/fe65/XoQCVJ4Rx'
        b'Mzb6t5YvFSyJW/CrQ0fzxr63nnzzin/Dt5+nru6cr1+4rT+la7vpky8fl2Z893XLDIe3E5Z+l6f9t8Wleg/yt/765Oy8ksS7Qe/5hd5OBvP8Wx53r/d9nefSklnHOy6I'
        b'4eq+ZtMg3dilrbvcpsE9VmFf0L7eF/JKWro+jW4t0tHObv8iIja0sYGr3fFnnpH967VHjQIaHDsr7zvEhu7/xXq7X8NfkkI/Ex4s1jmR3Q6lG6tcgj7zjA3d1PDICHA3'
        b'Vpno7rNucN5YNVl3hkHHjJ+vppwXyRd8Kdeeu215Zq7vx+6K9VPZnyq/237l5qnPpB80TIt/Y6btP+qmxZ+evblt88C5vnBF8cCV4H3CVefz4n9Jub18/ZESj3X+06P+'
        b'EWJ/St7zVDq/V/u3ydo7+iorDB6mlGinl3G+7dVyjZqhlCWcy5bpr/hr2SLF49lz4v3z9+36ednU3ND8r0/crrhASXT5ITsnX45sLYiwN/385K22+jKD5VElj+IaXkn9'
        b'4sP67/9h8NGcLVX77D+6qPtL5CcnuDEP5/vm/+rb+UXW2ym2AUsj7Jf7x9e/zTvcwvk87O9/NfiM+3D1urcfOB9dHZ9eumXwl9vHWXnQauNgsMTwe8Gvy3993e1JYqJR'
        b'u+APC04fWbvkb3+6qvuO5yznqg/vnfuwIbP2wdx/n7SUFPXzP9lx2zjrySpxnsiUoGaYwPORY+G/7BB/MqLRtS+N6DZXwcOgxQOfIsFusIkF9tNpBbCR7Dv4g2NLEBOG'
        b'5BatkpUUJ44GNz0XEwUvEZq+zoMm4yoDvIZsM64z1NWi+KAdfY1dmQ6uMNBrh8D+XH00ySTVwtOl6pMME3idDc6AVlPGcOrgbMSWDGlPR5Qz5kDR4eTwxRa2wDOgyQcb'
        b'KcHuNGKUdZQFmkItyDkpDa+7kiMQvLp0ZCejJTWNVSwGWxj/n2fBZngWjV9UrkuBrDo62gp0MsZetxBjsIUoZXchxn8Ysw0ofEmF2BrkqqHZtsCLDGxLCLzBKHtvckkn'
        b'SnZokTiNFe2wlh2aUA+S0yAncJ2rD/bPGAdq7nYiUXlbVo7qmGjvpaJJcoxenLEJiTMP3K5i4lhNGqMVh3idrUTrADQicZBo4eEzO3gCdmMBCtuQqXe1PcK4aLbqhAeI'
        b'O7EVAUg8GWfn2yESb3w3wWbmMOs6mra3eJTYPAPpchieJw3iCjoL1Zp47kUjunirwWv/tYHWaHASdkFx8TLDkY0g9Ei2pm5x1CbJZpStgxq8LEBpE3zPJrobXdLvzGrW'
        b'+4hv0arVrt+mf8BQxXdR8HtFYUpRWLe7UhSv5Mc30/2m/I8sHXucEu7y35v81uSenNw/WSud8lSW03v40/tMbeTmKlNXfE4kbhHjAyRESR6vCFAJfIafOgMUdV1SpU+U'
        b'yiNaJYgZiRXc5do5rTtGJZimEUaMw8pUHrF3slWCpLEvFiIad/xVgoSxL0pUHlO7q0eTJy9KVR7T7kxSCeLGvlig8oi8Q6MUD170G+Uqj7g7hSpB8ri58lMJ4sf9Bksl'
        b'iH3hF1KVR9Qdh3FIkRf2E5VjPFISlUdEN8pu9IQpxpZ8wkocJvXEy8rM/GE4JXCQuyjMO7y7HO9bBPeLvDplXQHdWt1114zuyO6yekLFvaFZytCsnuw8Veh0lc+MHtHM'
        b'Vq3WujajPgub1pKWVb0W7koLd0XxuYWdC+9ZhJKTzEiV7bQe1Bes7Noj90cqpncldM7rLr5dca3inldqn8inS6vTtpVz0Oh3I/TbOMiDFW5KxwCM1Jeg7p1y1gntDu0H'
        b'+MDTQynwUCR0ZXWm3POM7A645xl/x/FOnUqQ3iewbddr05NPUwkC7gnmdWu/7nin5G6+MmGuKmaeMnTePUFxT2Fxn8Cmgy1PUExTOk1RCSOUgghCVX18ZX7V8rxld4bK'
        b'L/UuqrGsvue9spFryes6jHqFIUphSLeWSjhNiQcDQz5S6RSuEk5RYrv9sTTSVH4pd6NJjid8NVLUWPWrFJVfIjOoxkuDBmLGswVJVPkNd/ox5MQqv6ShF6PSpNzlqvzS'
        b'ezKzVILsZ5Olq/zEd2eoBHl9AqtBkZnI/BFlZm/xmDIzE2AQnsn7xDvF8mAlX7RX01BGn9ksx6z4y0HU4CnzGXyazcSuctSUeXJowxzbVWaZ0bQlBv17GXMasmHequVG'
        b'KfQDRivsDh/OlFAMLAE5lsG7ulSjtvpYhh61m/s/97kppMbu5royu7mTVrAovjaj+ecUkEAxZzVEzDoEOw0AxmmxTQR7EIOxK4Mg7OXBDgeANTInm1dQk73nMu6xrpdM'
        b'CUC0/b3gDsqfZUpoT+bqUoIiV9wAZcfMqiiicZOVpktFFTuTQHlRKiPNPwlYSftmPeFSvgXLdViZ6o2qdnAYngwI5IjBEbyVRBUZgDZm56WhCG4KCNQqDsNWY5TEcxKh'
        b'cpStRX0RYk38Re2UFTOkf6F5VNmqWMS7zfecGyBhMrE6hEfVLIvGgakLZvOYmNN8kTQaGEBRmfMN9BKLmZhbuIZUZjUJ9LwutWZifkbpUTWr8Bbp/DIjrhMT8+16Peq0'
        b'NQn0dEkWM4Ff+WtTrXNscZbKyiTWjBJQJTi/mkjWeXgLgltHa8F9SNzuAtcYWfNq3NQAX18ORTshyREF7zSex+yA1jhQp1fvwG1V2Kc3iRGkHKznMYoAVeACFqRMSONV'
        b'zIKn4QE9gmlQiyW4c56MwL8fnJ8FD2jhr4AzSPYDV9mgidk82c8qhfgg2Istorzg7lnkm6UxHMp3iglWkCo7myBlCgAatVHv2AX3wD3gQBjcw0X85UYKXPYrY3rOjVLY'
        b'zJwpA3kCZQOvhZJky8tRihHtJ6z6BC6bpghAC9PeNwT6OV5YXqVhCw12TJk0A1wh7T1FG+4lWA3gCGhF1wsi8h0ZuJYO8AhYqgfXUEuR+H+bhGfAc3AtoxcGN+VTy7Xh'
        b'RTKVkBb5bhGHErgwBVqvU8OAWCn2NuHhQm+bQdFZXVIZe4Alw4czJdffu7zn3XQQxd/wfepqTjSnQc/L4UjCNhfvj79+O3HQrKIwu647+uiUkIg1D+3rk0+8+07jN5P9'
        b'/9AXf+Aj2Vd/n7rE5bvEx8k791ZPPsvZY9HUH6acE3Fqdvr7HsYng8w9H+ncZxuFZR8UVC2Uf0Bt7au78ubunUeC1p4Kfs1+duM1/htPNtS7H/7QfdaD+uX6vpYene8b'
        b'5dbaGRX2BmSovupXLuWd+WvyolkDFdE5mx0j7P+yfveVV2s+cHvLR1QX89GTvs5U/q2126Pfb1kw//3DBX+/uWfeY+U0pX7Ge/UhBy/4zb8Uctj/NVPnvKrVR1/7Ddp8'
        b'Zfr1Q4eqz1uW5i+wrXojdmVK5j+kl0s+jT14/HHv+wcfNu764zuH/5jT8/ParHc5bwcs1joIQuduNzvzzZ9F736/Zxl9//zJ/Ol/P7lsw/W25CkPY6c+1P1xf7HPw6db'
        b'37bNskj8t2jpllt//WnHfEWl0aE3D4nD6jxia987t7b6wo82Gz0q3/91j63i3//mPuld+S/4kUhAuHa7OAPEsu8El8fXFx5SBYNbzBl+fJsQHCP6fule7pjXvsxCffM6'
        b'irBdDVuBpJejNmrpaSM4xdifIvkJtCUQta9oeLxE01jIBjbWwA2uDFjiWrguCEsQaXiPD7vci65KpalJ0WxwdjaPkXY22ydgaH6MpriZhvJSjD7h4A/aCYDRdLAWZWaM'
        b'hAlPiEYkzDIkBxIh72YtF2cDHAN7PdgUG56lgTwUlYGMu21icGFI1RUNMQWj7govODPZ3AGvSvFXwmA7gyVJTorMZ3KswI7lDIjkthnZWA5Uw0hi7HlwEBfFmQ1Op4Jr'
        b'TFm2RoOLQ/ZRYCP+DBLd4NVAIiCBq2gUb2WqihHLrGpHBDNwWJcYIxkgufUqA3jZZacpIDkisQznpBoN7hEiaeAGkpGHhbdlap1BNEVtCEFSVJKntzfc4ZOXlIKyCjvZ'
        b'cBdoXkLIrFrtxhhYIQG622OMiRWaX0mBZKHgFIm1HdyG18RcisOiweF6uIbpGdtWws2j0SYXg4uVcD3cR9QH4XGqeEh9EFytnkCD0DpTTL6VBzqz1HK4WgifpAWaimAH'
        b'oRWGHTkysuhGsAG7bhxHFoWvwXNMzrqsQ8ZYczmidA2wOZp8aypsLGHA1hmodfhqGZJ018KmFzLg0kCaGOBge4VlRiMsEX4mYqQOmwH/nm1B8S2aa3aFyemdkX1WNg94'
        b'fKz13MtzUvKc5FkK1jntTu0+viX5s1Bz3b18EeLkevk+Sr5PF63i+3f5dwX08EPQawaEUuGo5Hvd4wd3Od3jR3Y79fOFcv4Jqw6rXns/pb1fl5+KH9TLn6LkT+mOVvEj'
        b'h6m6K/nuvXxfJd+3y0TFD+iK6YrFICLP/2g/EnY5vQJ3pcBdxffo5fsp+X5d9ip+YFd2V04PP4y8xwLArgyGhAK99FRkK9BLv7E5zulyuup93rvXP1npn3zXTeWfc48/'
        b'q2fGrP80XkiX8z3+1G5/jRoIVtoHd6P8h/fyo5T8qDuopLH4tbWiGhWqlx+q5Id2T1LxI5g0dh12XQ4j9RWj4k9jGmLUd0K7XO7xY7oTyCsLpshI1mNYeBUqs4PCr4fv'
        b'9Tvvhtt5MMTab9Ijylpk+jSU4lu2BLe6qUwdH4dZmzgPhlMmZkPd4z7PFXUY5uk+z6XP1KLX1Flp6qwwvWfq+UAtonEVnF63KUq3KUMCaEGb8T2BjyL2niAYCZic2/rX'
        b'9B+xaVE89vNnH08/pmizBAw3YWK2T79FvzX2Pk/Yp/kVC8t99S31cs4Jww5DlYV3M0cNmiq37+E7Dau39vCd+5zcTqR1pHU5KJ2Cep0ilE4R3TNUTvFqxf5C7HHRwqpZ'
        b'/1ntnRfAdSG89ShYl2NY/Bgz1v4xJH/8jOSPWRY0PQkr7LyUIQleaEQ0YeBF9DeI1fmNmDh9g7X8RRZjsFuI5WK1PtZCccYX7FG+2hUrtugMGY8N3WGVFmIkxYC2YFsF'
        b'or1LdCmJohtRRhowyM+Mzo5Oy8+dlRmfM8CWSWoGOBi0ckBf/SInPjeHyF6kBv67bbBn4FoscKWOmHR74vqsZRG8lh+1jA1dHjpQfOt+nmsf3/8xl8UPbIx7qEVZO/Xz'
        b'fPr4gSjEOrgxdQSOJQDDsQQROBY10oonRlrx1sReccchniTEzKaf58bgs5j5NcY/0WEbej/RYxlm0k909A2nPbHkGPo8NdAy9Buk0OVHHtswjn5oRNnad/A7Snusffpt'
        b'Hfud3fqdXPtdRAon+Wz00+moKJbPG7lxclVw5OFDP/Yu8hq5wdCTrb3cqXV2vwN+su63d5LnyvX6nd0VgfLUh3Y860mDDvzJk/r4Nm2yQTa6e8C3assZ5KI7DBxs3xHQ'
        b'IUNRvQe1cYgOZWbXYYopDOriZz3KDMWW81tTBvXxswEqbJtMHti6cNAQPxtRZtY9Nn6DxviBN5LYBD9PoswcOmJxHgdN8TN/5L0ZfjZHiduKcOYHLfCzYOR5Mn62pMxs'
        b'O9jyuNZlg1b42Xrk2QY/247Et8PPQsrMsi1WzmkNH7THzw4j7x3R80MnVOW4KFghFEX6wRUHOrtaG6G2z6Upa7vWFYpkpV1wr90Upd0Uld1UlVVkv8CqNVVhrrT27bUO'
        b'UloHqaxDVILQh1y2lVGj+KleDG3o/gOFr0+TWL6G1g8pdGEMPjAfFA+2eWgaNHEpHtwTl8ueDa7XjpLQ9dW/jxww9oaJBvYGjRE31IgUxui/NsFYMB79VMwa/XyafUqb'
        b'IahLFVsTLVDdRuMSTjGnQXdo02A2h0VJuGrMDu1RmB3cYh0UqqsRqk1C9VCovkaoDgk1QKGGGqG6JNQIhRprhOqRUB4KNdEI1Sehk1CoqUaoAVPiYpuhUhXzD7JImBa5'
        b'EqyOhZbUM/+KzQhmhM2zb57FmHguHfMXpbNM4/4YvZ0utm1kke0dRmVPH7twLdEtFmjUuzF6r9toRNpjcoPObN5I+562HKJFtHbZ2BlsCbfYqmHY98Nsk6UWuiUiuwEG'
        b'm0qcHv/L3lFAjBgseOiVsKisQCYTumVWymrqJNWygopiPKlLJRWiUWlGPbjnYjxIxmsjdtpaWSirLJPUMK5WsbvKskqshondZUqqahiPrQTTcowX0Wq83yXSHtAtKK6T'
        b'yrB65oC++pZoWeowHvRQMLu4pG6AvagChZVLiqW15ShMpwrlfElldXGRjkbtD7vPWENpqtYPedAldmy4+jmo4rmo8rSI+rOh2okG6q6bh33krtQlu2w6Grtsuhr7aTqr'
        b'dNW7bGNCNXfZPnvIHgf4M7lCWiMl9ntqNOih1pBWyGoKKookLw77OVx14WrY0BE3tJiyWkcVe5V1i2E0Y1GEckm1aHwHg9FCtZowAxQtrK3CxtQhwmLpAmnNOGiko3OB'
        b'W204H9j37nNygV5PlIcKYUFZVWmB13hZCRMWlaJPFhEPtxN6cFX3m/HrhHkrdEtD3RVlSVLxH9RI0O/VCOqwjDPQuITpwrKCQkmZ0A3davpXFXmP8VxKOoVs3FyMzjqp'
        b'Wzd/jaoYJ/PqjKBBEy5MJfBRmEqiT+qwH1ymWtDozykoKsWea0meiGNjNLgnAIWtLSyTFKtH92gqmehaWcH4wEWUCCYsemZqSj0njF/HyTXDnokL1NVcKKlZIpFUCAOF'
        b'bsWM81IRmV5CJyzo0MTAVDvzJJQWqxss4PcabGg2UXuAVT8JqyULpDJUw2gWQ5Md6U6ewlp1s9VWYE+svwNz+6xNlzGztf5OsgkltE5m4Z3nldwyqjaCwhYQcAO4OWRF'
        b'qnbNkUlcAWL/H7ADNDL7NlmaLgA3RBnwZFMJVbtYM8otVYz3L637onQp4lkTbAObOWOIgq3hI3QJTay2mqdJtr3KAB7TAlsYH49WBpRgxdtsKnN+GR01i8kuPAnaFo2b'
        b'26EtpAXmxLxWw+q1GzTqgw79aEL1h2nalEHZHhbekxfna1HEhyi8jLLXPC7ZZI+c5bQmtTVwhy7YA0/BI4SeToguxZvvw6Hmz0+dW+TMeFWETdl141GDjeoNO3MR3DY2'
        b'k1f0wVHQDdcRsq9O1aP49TU03tHfZueuJrsZrgPrxyPsxmxIwd2FWEVdg+x1cEofNsJ18IC0OvQQW4YtEbS6ftrw3muGLD8Drfl//TWmsaPvL/sX/eNrnqHXkbeoRvuZ'
        b'O9c0+mxxLBKlfPbFb98mLlvXYP0n5eR5rFt531u7KPLm9VlPl+flv/d5DSf0RNPJNudDsz74JK04617xvuNtgfH3Hu/dGPCn19/56S8nZib4xZ1/952Fhutvr9n5zbG7'
        b'SduTbrWkJsOwxVNC+v5c+9VhP7ZfUdEv0z78OT3cN9vhXsWuvRmWs2foPA2xOjwlG0NLMSofzVQMaMrgp6SO2UP0W83ADB1ZOVVfvBLceEZzg13OmOWeA1cXgaaleCdS'
        b's+txKTvYyoHnYIcvMTIER1AzwDXwyKgNyaHNSHAEXmR2I9dBObjCQAp6wE5UnxhScBHcTrZt4V4LcA12aeOtxOH90vkLGDxg2JBRCo8yO39Du35J9WQXM3QRPAbawIZR'
        b'u7pDe7pwL7hO6qIkaFYYvDCyATm8/bja5rEP/noLPA7Wgy4MCIV5fC94EV6RkY1qoreCOX4vLSoNNGiDQ+ba/2ORl4APmQwxF6NBlywYdN6H9ZMpR5eOIoXoaIXKIQjj'
        b'JfWbmjfX7Fvdslpl6qqwv2fqQRCWElWWST38pD4nH4ywZE8i9Vq4KRnPftH3TL1ItGSVZUoPPwXJmB05CsHRuSr7AIy6xNBc1bJKZeqiMLln6k4iJ6gsE3v4iWrfNgfE'
        b'KKYuE3Npy9JdkXJE1ZlxEqiyjOnhxzywtiNRXoq4veiEbYetyt7v96M6Ojdz3ucJn3WHch7vSVzAl4v4cglfLuPLFXy5+vsWgMOOUMZYAU7QQiLENMrw9PrbT9jedDJN'
        b'Z9PYF0r2S/mYw/NWh5YfdV4/4r8CiNLLH2YyJ4LBGSnCEApOHiqCBpgRw+IO8Ynj4C395wBRalAjg3wNJvTF8zkT5/PQcD5tx+STMFojufzv4I2G2NIXz90rOHcj6EZ2'
        b'TO6GuMBnKvG/yR4nH7GsL56zeShnj4ZRjmbtn8Xk0IrJoQbT+1/mrmEod4iPffHcFeB666GH6s1thP8tGAv6JfuvsziMqjXEgb54PotHt68l3p3UYF3/ZzkbYmdfPGcL'
        b'ns0ZatdhtlgjZyIW2RdmdoiHzRbTi9gaecEA6MRukTi11NUwP9Yi0jh2vqFLHFtit5aGjUYlBsPGyNr/M2PkUhHrCXfSOPJ4dHExdrlUIVmi2T/QGHsh50vxSHpiIuPN'
        b'kILiYiQrIImjQC18Eh9K2EuGp3BBdWVtFbMfUiAsqiwvlFYUYCdPz5BEHdV9GELO3VPorgl+h54Jvh6KVFhZuQhnFe/ZEPGIyUbN0qqX2EIY/lC4MKeyHAuizNYO9hai'
        b'Rp4rKKysZVxK4R4gKZ6obvC/hMpqoQRXSbG0pAQJTmimYkS60YVS1zdxM4WqbYHaF8o40hT+hyTEooIKIiA+b3fAL1hDJha6VVYRF1plE0vHmvXKSH7PTBBCt+jCaklR'
        b'aUVtxQKZequAeEQZN6Mj/UAmky6oIF3Bm9SJBmG1YzWhVLNUUiQ1Iwl5XKpD0rAfaeTgsGGhGH/JT+SJN+OExZLCGvwdFKMIyatS/FA0kRxPeqWUpJdJakjdhYa9QJ9J'
        b'wMbaZPNv7FCRSmThL9znUF6lNWoCTL2TkOFNBbecyrIyvJFQKRK6u5fjnRpUnKXu7hNu+ZASj6LIBI2QTETVW+Hlk4TWpYqXIc1A9qn3BSplpMBqGL8XSo8HJ5Nac7h6'
        b'C9OGtzzI8K0sXCgpqhGSFhx/DORkhAb7+qk3XvG+KjM6vV8sG6OM78PHbD3VVUqLJMMdPkZSJllQguOJhK/4+c99EZL+6maslTDFkVaQjOJRHxeXljZrFi7ZeG7n8L+q'
        b'gqXlxGmdpBovfJ7CclTPwxssGhnyf36G1M2DsTRGtxcOGb3dxowWn6GRMm62GPYvBhUSj31MA30+wHfCz4+COxjafNQYJigUjcgKmZTJVGXJuF8tKF6IegapD5yAeO4r'
        b'qMf348+N429bjiIiI/uu0qLSGukCXBRZUWkZvIFm8jLRs2N2QppeQtRvcmoktWhyHSaAerBUqK4iNEOVoxEXn+eVW1BTKMF72cUTUELdhXF/VVZbvkhSOn79ewkDxkQj'
        b'XyuoLVlWWyNBKwd2GymcXlktI5magEZguDC6tqRUUliLhx5KEF1bU4nXt0UTJAgKFyZXFEvrpKgzl5WhBHnlsoKaZbIxJZ8gdfB4WX75CgoZj4xUI1vlL5et0PHovVy9'
        b'hJGKHKn636n5cQNzmZ6MN53H5Pule6Jm8UuqUWnccN0O56mgcFntAtHE3U8zuTDEeeIOOCqiX9hEMVE3q/ApmLhLjSYTPBGZ4OeRQZ1iuHzPoRGqGW3CooWNIjZOuSZc'
        b'0NRwLGiGU98RfgDxpGhuHZrK3XKYNXbCBXsE7SVcGIsehMwT4nHcxOhRUoH+o24uxGtQ6IRTrgZOzGgy/mPI+D+XDIGUYZaM6dG5XslxQre8nBr0i9eboAmTDUPQMEnj'
        b'88hMjQOEbmiQq7s4avaJq6G2GrHIRWi1iFXfeQo1eLv4vGyh2wx4rLQaDVKUl8CJs6KBfjNCbDhYnakhUrJFtdWyZzP1PHZvIvaSsJIvzvkNs2jRo86PXoyHIXg+4cJ0'
        b'/CN8xd937osn82eS+ZNkE7fGEFCQmoVUP2Nh/Hn9gKAIoST4B0V8Nt7Es1iSpLq6wiehuqAWXcq8fRKkiLubeNYi0SeeqzCdiecn/IGJJ6jnfRnNSvGliAlDc//EUxPJ'
        b'G+LZisfPxkSVh7hYiaQGcxb4FzFYwc/l7wor68OFWF8B8U8lmGtFAajOJ25UnAjDMzGpCsqE+OG5KYqkNXhAoutz2T0GkwrHZG4IYU/Mp3sF+AUHo542cZ4wHBTKEP55'
        b'bo8sKUClTUCTyvMiEUAp1EL4R/hK8MQR1dOceop7Xo8egroKF8agO4YTfsU/5Lnxh4c2STL6fPi59T0EoKVOybTPxJM1hs1CLFpMdDpqnolnxEJpESKYHIs+Pc6I/B3f'
        b'1eoz2i3LWARGxLfO0XULbaz2J701eMEQ/ogHDbvACTUACW8mSVTmQHyvCH2nX/e4nzCVgVd5BXaDBjHcA/ZjWBQGEwUeMCIJxFwGUMnXqEeqJTNVIy/egFs4WquJJ2xv'
        b'yhueCWYQaXbDW6B1NN4U2AMuw7P5JoSY0HYlwd/qMvwh8LNoDkV8pMJtcF29B4qfgt1fYbMCcDolLQuccyHAxxQ2QM+m6gN1F4D91gSX4WRIOusNLcr3ZH2B6Ycz38t+'
        b'm6rF2KF64ETksxjHOYRKEnOeNR2erNY8Rd4G2gxE4Gg9OVKRvjJzKS3D7nDDer7ck/laOoziHZzann9NvKzULSk6Xhz7VkbPuSjBZnD+87gLOcL9tS1GSsfwptVflP28'
        b'8/Od6/aku3737Tt//vOJX9d9bXiGv7ZTddpp3tEVvJvZ1rWzo6s3z8qnmpee851+rebXN6Y6tiVOts4/IuS8mTytdurqHWtrp5Wmfxuz4YZ55dWD21edTZg264Sz6POq'
        b'C+3/DnA/nmI8r/r7Lw9ZLrl2LCNLbLjZ60Lza8d/+PPcsCnbljkfvvlJ9/c3UlMlRq+8s1hsdIK3eWXdK7e+CVl8tT13UendooOR63eEecU0fNf0p4ebfozr+9xyz5O7'
        b'k768kZe+WKk46phwqu7kccsDX5sE/dresvpfdO5bcbMuXxTpkHPIVXCvx4hfM9jBwxb0CwqY88vNqJs0g1N6PsQZDbGgh1dzyLtQeAXs84CbM5LBaQ6ltQTsKWM5vMLY'
        b'esAbGfC8vqb1PDxtxRzDGoJjjzEuIdzlU/O7x5K2FDhUBzeRg1tPlJXTz+Apo/a9QDGAyuwVxOYCrAG3qmVwlwR3Ai83HBnuwAYgzWzQZQ32PyaoIXum8sWpyfSqeoqV'
        b'TbuHwpsi4/+l80aMjCscsYUfY9xpMLzhPWQOn6x2V5ppSwk979n5KhZjjzNWrTVKU8d+K9c+V7dWA4wY6iSv6/DsYt+3COx39ejM6TLtKu4OPl92J+BOTE9wYm9wmjI4'
        b'7W6RKjhb5ZXT45rbymmd3mbQZ2Un12qL6LXyVFp5tsT1mdnKnZRmLoSueyt+3R7eFn5gOMIX+Fhymsoyqocfhd3DzVGE9ZgHNbP7TM1bi3ttvZXoz9SboDr3WnkorTxU'
        b'Fp5d3HsWQR/Zuvd4pKtsM3oEGYMstplfv29Yt1OPb/wd03u+8di8gZjimioFXoNabBOvPr5Xc1wv30nJd5LnEKsILyX+C+riqPhBPz3Wpqydf6BoRMfWQxGrsvXtEfj+'
        b'c5CNAv75WIcS2KN3Jl79lq4KtsrSs4fvid+ZeP1CsHuBv3msiIK6dnEsCop0Y6exob9ObDgbhnPR/Rss3TgB+w19nThT9humXHTPHLkaM0euI0cKuOe9lE3vmE4wcub6'
        b'3E6wkK2BiJllRdN+Tyl0eRkFe+zuanxnHgRIn6N25sFtpBq11HjS/3OHHtXfUGOc9tk9s7Y5M2vbj/ZcSid3G5uKmp961E2P8aMJt4I22CGrzcoGa4J8MYYTGtf0StMK'
        b'xvAX16opOOOPsZUs7WdQM4zhdZKuMBOczEHTyDUmEQ1fo+AlcBt0kk9ly9CalOKClpOCKU+sAxlwqiBwxC4gUAuexEjw2EwXXDJhDFxPgf1aAYGclfAkY9e7FGxj/Jel'
        b'aVEGqTM5lHC+51rDLMbYNmiBCSUsvkJjW90jUhvGilPXGQUKuRwUaFA2fxETM1lkSAlC/ThYg8mvTIuJebvagBIUH6SxVW9amiUTU6avT/E9S7gUb37qFxx3JuYKdz2K'
        b'LwjioECDdR52TKD7FJSl+jexAa/nlsVqCD0buBG05QR6ZGZmojaKw/aB23wZcCU5PBcZ4A22+fr6YtSVYxRc6wgaGNvblhK4JSeTcoTnaYoFjqNXK+DGWmLndgot2Lux'
        b'TfBueHTELhhch5tgBwO/iJaFawG+vssx1CHtRIGdrhmMse0acNoxB9/strKn7OGrsJkx530VbMnHJtnpef6U/xLQSdoWfZZNjHyjbbwor5CFjDnvLnjBFu4CGxZji94R'
        b'c97ZRgw43BlL2JVTApozhRhx66KZFuiYMZ1wSuJasBFb9IrALU0vo3AfUDAWt7iyQ/m6FI+jz8IqW6F6uky9nlihQ/FK+9k48FsvC4aHQnnuANtyMjPBUXgZ19h6qgDs'
        b'ZSDyvtQzo9w8+1moN8/JdJcwCWCLGNzOAa25mUAuoqjwlfqwA9wWk0YK8IG3ZKCj0jDAl4PKfYqCN6fVSIuuRbGJae9K7ymHct9Kh748mynJIdfvbdi5N9vcPnKd4+o7'
        b'bR8mcWWLfPK+bJS9atstjDyyeuP91fMP/kHri46UpFdn2tx+6v/P5T/R7zXfMZh03ls0aGf205Xyuk/ggfp/cZKONdQqvpz+7Xf656XHzLvM+R7LXNfudf/llQx2is3p'
        b'FGrJV+2ZErumtSf9P+AdnbrrVmbRP8Q+Vymx3z5W1w2+vmz63T82Hjkb8NPfppc8vNr3oad34dVfl78vCQ3a1+TY0Oe7PKyt9o9lApelc786eil0+qvf5M6elqvFzZvz'
        b'RV+we9iFj9+6sPIg+0Pnb5ME73fsyHXc+PHFf/Oz7Szy/rjqAw9Trfcj+jw+XbpjVcbmb6Z/+xcq4+uQwCfCXzvPPfgpMN6PH/25qM738Jtnj8zYutpx+aKM6Jyb/RvW'
        b'FFXcu9TVHVfaWvnTUqffzq70+DBrwZ//vvkbt4jffkuVBF0vaFatD9offohOOPeN7fl/cnxK9qz4WXVc/M32ozZ1bRU+9Wv+prIw/KXm46APRfzHmFeNmQz3a/IlwaB9'
        b'Ao2pLHCL2L36gW0i4sjjArglSkOvdeBrLNAyFdwkfFL+XLDfA96GDSlpqTTFsafBIfgqaCP2tPCUW4DY0w1cWsl4dCDuHMCO6Yyq29lp8BD6ZCPcOOKTFtsE7y4lDBHY'
        b'GJ+FOPFVYM0zfv6E8Vxd+Bq8yHzkXE4MaPKGJzV00DACEYFIgiedsO3o5syVIw5qwhOJKl0a3GCLteTmwltjdO0iKojuWx286Y+tireA82rLYmJWnMwm1rFeK/RHVOc4'
        b'4KiG9lyWIQF2ig0Socn2dNwIbxkJzpCiu0jrxMma/gaNaCQjrGfHGHsypqen4fXVHproRoWgAdvvBshIk0T5h4mTNVwRGsXbrmTHgStwJwFmAl1IijmpVpybhEQdDd05'
        b'eGMZIbFgFjgDkJwC92rq54EmuI/R+5ODtdXYLNeuQMPfbwQ8TfT30Ay80UBTee+gpgJfGrzMxDoP14bjGp5pPp4mYh4t0nlhXkOHYTg1tLuwv/JlvBEmQ5ZfLC1ivAdj'
        b'OD8CvmRHTbZq5mKvhPp9Qqdeoa9S6MsAvvQKw5qTsGeO+oNTsasPG6Hc7MBshX3bvOaEBz4h2NvHqdXN8a1u8ulKSw8l3/MB344x5ZRXn1jSsaRPYNUnsJWbtxmj1L0C'
        b'L8TydSG+L/CeYGo3/54g/g4fo93nnpjVMauLVgn8ewWhSkFot4mKIMq0G7cZM4kUBSqBb9ekLtMeQRB+YdRmpHYCkqUS+HSxutg9gkBsBJXUa+2ntPYbTao7pju2RxBF'
        b'3rentaWpBO69Al+lABvmChjDXEHo2AxGdVvcE6TcSRg3vPROUm9cnjIurzdunjJuXk/+AlVc6cvEtGHKPa9jXhcqQUivYKoSVQkqZRSqrw5T+cyjNkrs78SG1KD6Dxcg'
        b'jqgpGsmrFXSPwH2iQESkT4CdswwGWfmaP6Ks3CyeBlMC25a61lKVheuPIVZmokFjyj58MIGm7BzaS9tK5ctVtgHN+v2mggdOLicSOxInrGdCeYLGIcXqdQ5WOmOzYEF4'
        b'ryBKKcBmwRj8aaQvDHWJQRNdL5Q9XWeLp5NGsqfweGiq6xyM+pVLS9ognxLYNBs861Tj+dqOxKnG7w+EL9gjbtGextu9pDVrBpYNHlFjfKMNO+clfly4aoB0jtraCvtI'
        b'0xoGRx/xcvA/cGBV/eNYvvtZTwfa6bUEcO6GZIEHuKCT5Ikm/SQkoaNlCXTmJoEzsNHTW6RFJcGN2lXwDFzL8DCNJnZoUjxjjphAbMfPLqPBujkFDPTmRrh2HkE+gbtn'
        b'UvV1oItBStk0Cxz2QDzXqxksis6m4P4SeE76Da+NI/sKvW7JLtyQdV4P+PJuigsXmZmYtBxJP+tt9O81X387p8dLWJzboffW5+ZVZtOOTPvm2JYCK7PChf5f1D/95OOb'
        b'f5q6bE25++COzyNLdrH+9HWovsKy9iRszV3sdXRlirW7smPGJa/3f6yNf2J5Uh7+2Y2//RL21idTew3Kik3fKj+qmGN1X77ssy0efYb0la2t71RtO/m9LEh1Y75ka5WY'
        b'y6vknd1cpfvrmz1/vPXvI4knL21fO9j77g9/2XjFRPsrwa9/O9ImE21oMp/fYL7w80dS1+87v/j7qu9KnUu1c1qhiWxjs0nC11+9E3DXr38arbMi5MTFvSJjZnm9Da9K'
        b'PcCV1CTicYoTQoOzhtrMHskZsB4tL00Y590zXW1+qQObWCvhdfgag9po64fXBbSEsPQXU1rpLOtc2MFAT+yAx9DKhBZuT2+MC8uyKab0YRcL3ogA3WSJnAW3FyEG5tIS'
        b'Zp8EHC+gdMEJFjhaN4u8F9XAnWJPDO6wOdWbhudgK6UfxYKtYnCB8Vh/oRBbgsDNPhleLG24Cy/t7paZJO2K+XgzEfvSWjwV7hj2pQX3gGZm22jXwjyU8WS4zUsrZAml'
        b'NY/lCE6ANYSrcIbbwRkPAkAxPczLW8SijGE7G2wAe+FxkthnNmKmENfgk86dC7oorQiWBTwKdpJFuTIaXhWD6wuHO6sun4WYcgVsYOBJGpa/grK8jdSYsTWlFcMSoKX4'
        b'KkkLN8+B62BTPtg0ipuKBbeZtOsQV3aFyRg3DDHkWkDB8nSY8V/jIQ5J/8xkpE3AvYYnI1lBHeNg62eKWZJT7Cm++b6QlpB9kS2Rcqf7pq6KmHOJnYnn0jrTup3ue067'
        b'E/PHlNdT7tbcj8v9yNK+xyFEZRmK0SXQvGzQZnDACC3nphb7wlvCd0X0mropTd0U5vdNffst7eVOCrZijsoyvDm2z8XjxKKORcfL2/RaOa3FaH7GaeW5isD3Bb6DbMo1'
        b'8AHfYl9yS/Ie8QMrm/aQtpD2yLZIhdN9K58+gWW7TpuOnH/QaAyVfht7ucMJ1w7XE54dnoqarlyVQ3h33H2b6DvZfda27UltSfLcg+lP2ZRtDN1jE/0Qf+ZTm2h0+4sM'
        b'a2i+4TUpXo/7ph433lRX0yVy9ePfnfOZ+mYcII/CMhintu04GlBqy4U0LcC+j1/GkRfxqCTikC0JxlUHcd+hM7xMsch9umjSWFQDPZrShDZ4AcX+kzRx0lgjKZcx2AQ/'
        b'DBVLZPI/3K/UqEVcb2vG/mNq8xyuzWG7Xnu8gM6lCYbBQw7HkPeDAWVk1sHuiG1der7o9Zy3TO8k90+2lntcM72W0637VuxjNm2UhQExIqPop2xXQ5dHXBLAQbcPs+kh'
        b'cINgDG4QSsANrBz7ed4MAIJVcKN4BNwgCIMbhBBwA1Orfp5LH98PhZgGNMaOhETikCiaBKmT+eJk/pooCUMhP+igvA9SLKM0uk123vQhuRuwsNof1zG51z5EaR/Srau0'
        b'j+m1T1LaJ6nsU1TW4gFbh46wXscwpWNYt4vSMbrXMVHpmKhyTFbZpjxk0zZi+hFFC1Lph2xM66lWLW3o9ZjC10faOGSQhDytYIcZ2vxQR6PvtzneN7R9yuIbejxCEo/d'
        b'Q3w34pwxQQY2yobFUi5lKIE3LVlwFy9SRKdL7T/5FyWLQ62xtt1K0vJe+voo3h8WrN3w6uPVUv0z7w/cWrd5iU/k+qe6FpUDcc4/Fu73fdD/E+9G8abvvMuzjRoOVd76'
        b'dMWUf3npXx3Um/VTfKZi9U/fbXgQ1bb749lrVmXeiGTdmHbo5NfH5iwKmrHI+HT56Y2fSBKPyi+5fnxzoM30jtl77znfXn/j5+nXemz294Z+6vDNkUOLDglmv7dD55X0'
        b'919t/iXwiF9aaUrA/pyURQPFJgnaeSLtw2uftP5dtzO18Km8a8YU13u2l1a1634rWzloeLltxtIz/sWSmo7uL898MOfwt1mbHL4yfvKvPqek0uSQS0emZF/6c6F1QEHh'
        b'gg++ily+dnHY3ZUuKXMy213TjAvMSq8Uf/Vzgq6X2/zshgCXd706f0jb6bK+MvuNP7RcOJH8euRAiWNqX9s8SdWt+fpHfl7w4aGykI/PH4is/Jdq5Vpjk5LEv9xZ+HZI'
        b'u4j9GFc7PzUeNi3lIrGNDqXQsrUPNpLFV1cGzuiH8scBB26Ee4loLoObovFRBWyAB0a7f1T7fjxWInIaO/x0nnv5vxjs/8H04MQsalHk3zPzxJgZY0AnP7+ssqA4P3/Z'
        b'8B1Z7aaijvpvtNoFUoZmgxxtXYt+40nN/k1LWu23rGiTyf3lBR1BB5YpsvavPu/UVd1tf762O+t8/UXv1+PuToJJ9/xTPxJYtvq3FrQFHdCVpyB5qcsCiXw9EelKi/Se'
        b'7NyevOnK7Bn3LGZ8ZC6UT9pV0cNzwq76ZtKDetQkfnN0i1ljzNNAE12nHyl0eermquv1lEKXH3PpCF3L5umPKfTz4yraSdey1fwxhX4G02lKj/eUVc3R9XhKjVyfkCsa'
        b'rnq8QfJysEaXErgo9JUWAY0GT7R0dAVPzavZutYoOro+IdfBhdqEWDYhM3L9gVwJsYfk5U+D0QJaN5nun2R3zKDHK0ElTFRNSuoxSGJWzC3Rgjgd6g0d0zgr9fGFzQAr'
        b'P/8/PK74v+kveLzMH30QNt7SYsLCS8tQH8HTnSyGYmQzP5rm4cMQ5oIN0XgvY4dGTpO1wqnr+tFctvTE1T9wZGdQ0Daen2Rrsh7IFKz/NOJSHu/1jtA1cPONmG9iPvnw'
        b'2qUpn+34bV5Ew77c2ZzXy241NER8cCxpl714ewR3S25EvKNVS5zr2c9Pv9nu/dXf51XPdz33w7e/7dv2S//JtdX1IdbLZ3tH3n9L8t7J71P1wi68tza2vdy9+i2XGaf/'
        b'+e09tx39yTTXkN00ycjsD4M6rfO3TP5q5vzNlh5xZV3xa21+DH3Q98G229y14itLlk86v5L96ibvu39uRsIErsd4MeJdEUeegY/Qt4qNHbQpfXCBBRX4XJ/IFHEAbzBn'
        b'eMHzOBZi3CkT0F4Lb2Dou+1B5Hg0IR6x4k1IftiB95rw1qY2ZYQBMSexbeFu2PmYnIG0xArFyWnuadqUFocFDpfrpFg9VrvM2YeY7yYfLYrOwY61EGu+r56kgW1cuNkj'
        b'hUvRYgrsi4Gt4LoD4fhjBKAJ+9zYjr4Ht4JjoIWm9EUs2AxvOhFxYjrcAi7LhmPoeKOxlswCXWA9n5GUDiNiXWKy9m1WOzfah+VRdjrcac5kuIHOEjOqDTngLNZuCC1g'
        b'UAevgnYZkV0Z/QC4O4NLGZiysBMTJCnh/CWjIu0HTShKFYkyLZRL6YGLLHApt5QxBd67She9v2AwC4kIjUsW18KLiw0W19KUBdzBBltngEYmm02gwURMYB5xWUADWE+h'
        b'BtrPgkfC4GkC5W8MXgVHcO37iNF6gIoLm1fBHThAm7Jy4oD1qeC0yO2F14T/L5cIjcHvRhaLqKF/z1kuRpmk6oyyFZ6NLr+hieCRJcU17TPk9xraKg1tD9arDN3WJPRx'
        b'9Dalrk3tMbE/Fnqf4/khxxD9fcyx+5Tj+inH62OO41Ot2Twuml9Hrk/IdbBeSBnw12Ro7C7ZDbDLJBUDHGy/NMCtqa0qkwxwyqSymgEO3jAa4FRWoddsWU31ALdwaY1E'
        b'NsAprKwsG2BLK2oGuCVo6kI/1VjdEbtVr6qtGWAXlVYPsCuriwe0SqRlNRL0UF5QNcBeJq0a4BbIiqTSAXappB5FQeT1pLIhAJYBrarawjJp0YA2A2IjG9CXlUpLavIl'
        b'1dWV1QOGVQXVMkm+VFaJLTIGDGsrikoLpBWS4nxJfdGAbn6+TIJyn58/oMVYMIwsCDK8+z3/ef+EwpGGIBfsPlSWgdvgt9/w4bQJTRez8VQ8+jpIri8zMeMV7HVtrWgL'
        b'6nUL/WgH9i86JdgIqajUe4CXn6++Vy8Iv1iqn4VVBUWLChZI1EA/BcWS4nSRDhGsBrTz8wvKytD6R/KORa8BPVSf1TWyJdKa0gGtssqigjLZgEE2tocol8TjuqyOYqmb'
        b'n+kIDNcSUV5ZXFsmiaxOYDHmjsTh7CCbpumHqGicQSNK33CN9g+cMh7NH5xnT+ma9OpYKXWsWlPu67j2eEa+7gLdlJ4pfTq8fj3zHosAlV5gDyewn+I1C96nLMmn/h91'
        b'rnne'
    ))))


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
SEPA module of the Python Fintech package.

This module defines functions and classes to work with SEPA.
"""

__all__ = ['Account', 'Amount', 'SEPATransaction', 'SEPACreditTransfer', 'SEPADirectDebit', 'CAMTDocument', 'Mandate', 'MandateManager']

class Account:
    """Account class"""

    def __init__(self, iban, name, country=None, city=None, postcode=None, street=None):
        """
        Initializes the account instance.

        :param iban: Either the IBAN or a 2-tuple in the form of
            either (IBAN, BIC) or (ACCOUNT_NUMBER, BANK_CODE).
            The latter will be converted to the corresponding
            IBAN automatically. An IBAN is checked for validity.
        :param name: The name of the account holder.
        :param country: The country (ISO-3166 ALPHA 2) of the account
            holder (optional).
        :param city: The city of the account holder (optional).
        :param postcode: The postcode of the account holder (optional).
        :param street: The street of the account holder (optional).
        """
        ...

    @property
    def iban(self):
        """The IBAN of this account (read-only)."""
        ...

    @property
    def bic(self):
        """The BIC of this account (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def country(self):
        """The country of the account holder (read-only)."""
        ...

    @property
    def city(self):
        """The city of the account holder (read-only)."""
        ...

    @property
    def postcode(self):
        """The postcode of the account holder (read-only)."""
        ...

    @property
    def street(self):
        """The street of the account holder (read-only)."""
        ...

    @property
    def address(self):
        """Tuple of unstructured address lines (read-only)."""
        ...

    def is_sepa(self):
        """
        Checks if this account seems to be valid
        within the Single Euro Payments Area.
        (added in v6.2.0)
        """
        ...

    def set_ultimate_name(self, name):
        """
        Sets the ultimate name used for SEPA transactions and by
        the :class:`MandateManager`.
        """
        ...

    @property
    def ultimate_name(self):
        """The ultimate name used for SEPA transactions."""
        ...

    def set_originator_id(self, cid=None, cuc=None):
        """
        Sets the originator id of the account holder (new in v6.1.1).

        :param cid: The SEPA creditor id. Required for direct debits
            and in some countries also for credit transfers.
        :param cuc: The CBI unique code (only required in Italy).
        """
        ...

    @property
    def cid(self):
        """The creditor id of the account holder (readonly)."""
        ...

    @property
    def cuc(self):
        """The CBI unique code (CUC) of the account holder (readonly)."""
        ...

    def set_mandate(self, mref, signed, recurrent=False):
        """
        Sets the SEPA mandate for this account.

        :param mref: The mandate reference.
        :param signed: The date of signature. Can be a date object
            or an ISO8601 formatted string.
        :param recurrent: Flag whether this is a recurrent mandate
            or not.
        :returns: A :class:`Mandate` object.
        """
        ...

    @property
    def mandate(self):
        """The assigned mandate (read-only)."""
        ...


class Amount:
    """
    The Amount class with an integrated currency converter.

    Arithmetic operations can be performed directly on this object.
    """

    default_currency = 'EUR'

    exchange_rates = {}

    implicit_conversion = False

    def __init__(self, value, currency=None):
        """
        Initializes the Amount instance.

        :param value: The amount value.
        :param currency: An ISO-4217 currency code. If not specified,
            it is set to the value of the class attribute
            :attr:`default_currency` which is initially set to EUR.
        """
        ...

    @property
    def value(self):
        """The amount value of type ``decimal.Decimal``."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code."""
        ...

    @property
    def decimals(self):
        """The number of decimal places (at least 2). Use the built-in ``round`` to adjust the decimal places."""
        ...

    @classmethod
    def update_exchange_rates(cls):
        """
        Updates the exchange rates based on the data provided by the
        European Central Bank and stores it in the class attribute
        :attr:`exchange_rates`. Usually it is not required to call
        this method directly, since it is called automatically by the
        method :func:`convert`.

        :returns: A boolean flag whether updated exchange rates
            were available or not.
        """
        ...

    def convert(self, currency):
        """
        Converts the amount to another currency on the bases of the
        current exchange rates provided by the European Central Bank.
        The exchange rates are automatically updated once a day and
        cached in memory for further usage.

        :param currency: The ISO-4217 code of the target currency.
        :returns: An :class:`Amount` object in the requested currency.
        """
        ...


class SEPATransaction:
    """
    The SEPATransaction class

    This class cannot be instantiated directly. An instance is returned
    by the method :func:`add_transaction` of a SEPA document instance
    or by the iterator of a :class:`CAMTDocument` instance.

    If it is a batch of other transactions, the instance can be treated
    as an iterable over all underlying transactions.
    """

    @property
    def bank_reference(self):
        """The bank reference, used to uniquely identify a transaction."""
        ...

    @property
    def iban(self):
        """The IBAN of the remote account (IBAN)."""
        ...

    @property
    def bic(self):
        """The BIC of the remote account (BIC)."""
        ...

    @property
    def name(self):
        """The name of the remote account holder."""
        ...

    @property
    def country(self):
        """The country of the remote account holder."""
        ...

    @property
    def address(self):
        """A tuple subclass which holds the address of the remote account holder. The tuple values represent the unstructured address. Structured fields can be accessed by the attributes *country*, *city*, *postcode* and *street*."""
        ...

    @property
    def ultimate_name(self):
        """The ultimate name of the remote account (ABWA/ABWE)."""
        ...

    @property
    def originator_id(self):
        """The creditor or debtor id of the remote account (CRED/DEBT)."""
        ...

    @property
    def amount(self):
        """The transaction amount of type :class:`Amount`. Debits are always signed negative."""
        ...

    @property
    def purpose(self):
        """A tuple of the transaction purpose (SVWZ)."""
        ...

    @property
    def date(self):
        """The booking date or appointed due date."""
        ...

    @property
    def valuta(self):
        """The value date."""
        ...

    @property
    def msgid(self):
        """The message id of the physical PAIN file."""
        ...

    @property
    def kref(self):
        """The id of the logical PAIN file (KREF)."""
        ...

    @property
    def eref(self):
        """The end-to-end reference (EREF)."""
        ...

    @property
    def mref(self):
        """The mandate reference (MREF)."""
        ...

    @property
    def purpose_code(self):
        """The external purpose code (PURP)."""
        ...

    @property
    def cheque(self):
        """The cheque number."""
        ...

    @property
    def info(self):
        """The transaction information (BOOKINGTEXT)."""
        ...

    @property
    def classification(self):
        """The transaction classification. For German banks it is a tuple in the form of (SWIFTCODE, GVC, PRIMANOTA, TEXTKEY), for French banks a tuple in the form of (DOMAINCODE, FAMILYCODE, SUBFAMILYCODE, TRANSACTIONCODE), otherwise a plain string."""
        ...

    @property
    def return_info(self):
        """A tuple of return code and reason."""
        ...

    @property
    def status(self):
        """The transaction status. A value of INFO, PDNG or BOOK."""
        ...

    @property
    def reversal(self):
        """The reversal indicator."""
        ...

    @property
    def batch(self):
        """Flag which indicates a batch transaction."""
        ...

    @property
    def camt_reference(self):
        """The reference to a CAMT file."""
        ...

    def get_account(self):
        """Returns an :class:`Account` instance of the remote account."""
        ...


class SEPACreditTransfer:
    """SEPACreditTransfer class"""

    def __init__(self, account, type='NORM', cutoff=14, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA credit transfer instance.

        Supported pain schemes:

        - pain.001.003.03 (DE)
        - pain.001.001.03
        - pain.001.001.09 (*since v7.6*)
        - pain.001.001.03.ch.02 (CH)
        - pain.001.001.09.ch.03 (CH, *since v7.6*)
        - CBIPaymentRequest.00.04.00 (IT)
        - CBIPaymentRequest.00.04.01 (IT)
        - CBICrossBorderPaymentRequestLogMsg.00.01.01 (IT, *since v7.6*)

        :param account: The local debtor account.
        :param type: The credit transfer priority type (*NORM*, *HIGH*,
            *URGP*, *INST* or *SDVA*). (new in v6.2.0: *INST*,
            new in v7.0.0: *URGP*, new in v7.6.0: *SDVA*)
        :param cutoff: The cut-off time of the debtor's bank.
        :param batch: Flag whether SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.001.001.03* for
            SEPA payments and *pain.001.001.09* for payments in
            currencies other than EUR.
            In Switzerland it is set to *pain.001.001.03.ch.02*,
            in Italy to *CBIPaymentRequest.00.04.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The credit transfer priority type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None, charges='SHAR'):
        """
        Adds a transaction to the SEPACreditTransfer document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote creditor account.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays and
            the given cut-off time). If it is a date object or an
            ISO8601 formatted string, this date is used without
            further validation.
        :param charges: Specifies which party will bear the charges
            associated with the processing of an international
            transaction. Not applicable for SEPA transactions.
            Can be a value of SHAR (SHA), DEBT (OUR) or CRED (BEN).
            *(new in v7.6)*

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPACreditTransfer document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class SEPADirectDebit:
    """SEPADirectDebit class"""

    def __init__(self, account, type='CORE', cutoff=36, batch=True, cat_purpose=None, scheme=None, currency=None):
        """
        Initializes the SEPA direct debit instance.

        Supported pain schemes:

        - pain.008.003.02 (DE)
        - pain.008.001.02
        - pain.008.001.08 (*since v7.6*)
        - pain.008.001.02.ch.01 (CH)
        - CBISDDReqLogMsg.00.01.00 (IT)
        - CBISDDReqLogMsg.00.01.01 (IT)

        :param account: The local creditor account with an appointed
            creditor id.
        :param type: The direct debit type (*CORE* or *B2B*).
        :param cutoff: The cut-off time of the creditor's bank.
        :param batch: Flag if SEPA batch mode is enabled or not.
        :param cat_purpose: The SEPA category purpose code. This code
            is used for special treatments by the local bank and is
            not forwarded to the remote bank. See module attribute
            CATEGORY_PURPOSE_CODES for possible values.
        :param scheme: The PAIN scheme of the document. If not
            specified, the scheme is set to *pain.008.001.02*.
            In Switzerland it is set to *pain.008.001.02.ch.01*,
            in Italy to *CBISDDReqLogMsg.00.01.00*.
        :param currency: The ISO-4217 code of the currency to use.
            It must match with the currency of the local account.
            If not specified, it defaults to the currency of the
            country the local IBAN belongs to.
        """
        ...

    @property
    def type(self):
        """The direct debit type (read-only)."""
        ...

    def add_transaction(self, account, amount, purpose, eref=None, ext_purpose=None, due_date=None):
        """
        Adds a transaction to the SEPADirectDebit document.
        If :attr:`scl_check` is set to ``True``, it is verified that
        the transaction can be routed to the target bank.

        :param account: The remote debtor account with a valid mandate.
        :param amount: The transaction amount as floating point number
            or an instance of :class:`Amount`.
        :param purpose: The transaction purpose text. If the value matches
            a valid ISO creditor reference number (starting with "RF..."),
            it is added as a structured reference. For other structured
            references a tuple can be passed in the form of
            (REFERENCE_NUMBER, PURPOSE_TEXT).
        :param eref: The end-to-end reference (optional).
        :param ext_purpose: The SEPA external purpose code (optional).
            This code is forwarded to the remote bank and the account
            holder. See module attribute EXTERNAL_PURPOSE_CODES for
            possible values.
        :param due_date: The due date. If it is an integer or ``None``,
            the next possible date is calculated starting from today
            plus the given number of days (considering holidays, the
            lead time and the given cut-off time). If it is a date object
            or an ISO8601 formatted string, this date is used without
            further validation.

        :returns: A :class:`SEPATransaction` instance.
        """
        ...

    def render(self):
        """Renders the SEPADirectDebit document and returns it as XML."""
        ...

    @property
    def scheme(self):
        """The document scheme version (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id of this document (read-only)."""
        ...

    @property
    def account(self):
        """The local account (read-only)."""
        ...

    @property
    def cutoff(self):
        """The cut-off time of the local bank (read-only)."""
        ...

    @property
    def batch(self):
        """Flag if batch mode is enabled (read-only)."""
        ...

    @property
    def cat_purpose(self):
        """The category purpose (read-only)."""
        ...

    @property
    def currency(self):
        """The ISO-4217 currency code (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def new_batch(self, kref=None):
        """
        After calling this method additional transactions are added to a new
        batch (``PmtInf`` block). This could be useful if you want to divide
        transactions into different batches with unique KREF ids.

        :param kref: It is possible to set a custom KREF (``PmtInfId``) for
            the new batch (new in v7.2). Be aware that KREF ids should be
            unique over time and that all transactions must be grouped by
            particular SEPA specifications (date, sequence type, etc.) into
            separate batches. This is done automatically if you do not pass
            a custom KREF.
        """
        ...

    def send(self, ebics_client, use_ful=None):
        """
        Sends the SEPA document using the passed EBICS instance.

        :param ebics_client: The :class:`fintech.ebics.EbicsClient` instance.
        :param use_ful: Flag, whether to use the order type
            :func:`fintech.ebics.EbicsClient.FUL` for uploading the document
            or otherwise one of the suitable order types
            :func:`fintech.ebics.EbicsClient.CCT`,
            :func:`fintech.ebics.EbicsClient.CCU`,
            :func:`fintech.ebics.EbicsClient.CIP`,
            :func:`fintech.ebics.EbicsClient.AXZ`,
            :func:`fintech.ebics.EbicsClient.CDD`,
            :func:`fintech.ebics.EbicsClient.CDB`,
            :func:`fintech.ebics.EbicsClient.XE2`,
            :func:`fintech.ebics.EbicsClient.XE3` or
            :func:`fintech.ebics.EbicsClient.XE4`.
            If not specified, *use_ful* is set to ``True`` if the local
            account is originated in France, otherwise it is set to ``False``.
            With EBICS v3.0 the document is always uploaded via
            :func:`fintech.ebics.EbicsClient.BTU`.
        :returns: The EBICS order id.
        """
        ...


class CAMTDocument:
    """
    The CAMTDocument class is used to parse CAMT52, CAMT53 or CAMT54
    documents. An instance can be treated as an iterable over its
    transactions, each represented as an instance of type
    :class:`SEPATransaction`.

    Note: If orders were submitted in batch mode, there are three
    methods to resolve the underlying transactions. Either (A) directly
    within the CAMT52/CAMT53 document, (B) within a separate CAMT54
    document or (C) by a reference to the originally transfered PAIN
    message. The applied method depends on the bank (method B is most
    commonly used).
    """

    def __init__(self, xml, camt54=None):
        """
        Initializes the CAMTDocument instance.

        :param xml: The XML string of a CAMT document to be parsed
            (either CAMT52, CAMT53 or CAMT54).
        :param camt54: In case `xml` is a CAMT52 or CAMT53 document, an
            additional CAMT54 document or a sequence of such documents
            can be passed which are automatically merged with the
            corresponding batch transactions.
        """
        ...

    @property
    def type(self):
        """The CAMT type, eg. *camt.053.001.02* (read-only)."""
        ...

    @property
    def message_id(self):
        """The message id (read-only)."""
        ...

    @property
    def created(self):
        """The date of creation (read-only)."""
        ...

    @property
    def reference_id(self):
        """A unique reference number (read-only)."""
        ...

    @property
    def sequence_id(self):
        """The statement sequence number (read-only)."""
        ...

    @property
    def info(self):
        """Some info text about the document (read-only)."""
        ...

    @property
    def iban(self):
        """The local IBAN (read-only)."""
        ...

    @property
    def bic(self):
        """The local BIC (read-only)."""
        ...

    @property
    def name(self):
        """The name of the account holder (read-only)."""
        ...

    @property
    def currency(self):
        """The currency of the account (read-only)."""
        ...

    @property
    def date_from(self):
        """The start date (read-only)."""
        ...

    @property
    def date_to(self):
        """The end date (read-only)."""
        ...

    @property
    def balance_open(self):
        """The opening balance of type :class:`Amount` (read-only)."""
        ...

    @property
    def balance_close(self):
        """The closing balance of type :class:`Amount` (read-only)."""
        ...


class Mandate:
    """SEPA mandate class."""

    def __init__(self, path):
        """
        Initializes the SEPA mandate instance.

        :param path: The path to a SEPA PDF file.
        """
        ...

    @property
    def mref(self):
        """The mandate reference (read-only)."""
        ...

    @property
    def signed(self):
        """The date of signature (read-only)."""
        ...

    @property
    def b2b(self):
        """Flag if it is a B2B mandate (read-only)."""
        ...

    @property
    def cid(self):
        """The creditor id (read-only)."""
        ...

    @property
    def created(self):
        """The creation date (read-only)."""
        ...

    @property
    def modified(self):
        """The last modification date (read-only)."""
        ...

    @property
    def executed(self):
        """The last execution date (read-only)."""
        ...

    @property
    def closed(self):
        """Flag if the mandate is closed (read-only)."""
        ...

    @property
    def debtor(self):
        """The debtor account (read-only)."""
        ...

    @property
    def creditor(self):
        """The creditor account (read-only)."""
        ...

    @property
    def pdf_path(self):
        """The path to the PDF file (read-only)."""
        ...

    @property
    def recurrent(self):
        """Flag whether this mandate is recurrent or not."""
        ...

    def is_valid(self):
        """Checks if this SEPA mandate is still valid."""
        ...


class MandateManager:
    """
    A MandateManager manages all SEPA mandates that are required
    for SEPA direct debit transactions.

    It stores all mandates as PDF files in a given directory.

    .. warning::

        The MandateManager is still BETA. Don't use for production!
    """

    def __init__(self, path, account):
        """
        Initializes the mandate manager instance.

        :param path: The path to a directory where all mandates
            are stored. If it does not exist it will be created.
        :param account: The creditor account with the full address
            and an appointed creditor id.
        """
        ...

    @property
    def path(self):
        """The path where all mandates are stored (read-only)."""
        ...

    @property
    def account(self):
        """The creditor account (read-only)."""
        ...

    @property
    def scl_check(self):
        """
        Flag whether remote accounts should be verified against
        the SEPA Clearing Directory or not. The initial value is
        set to ``True`` if the *kontocheck* library is available
        and the local account is originated in Germany, otherwise
        it is set to ``False``.
        """
        ...

    def get_mandate(self, mref):
        """
        Get a stored SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Mandate` object.
        """
        ...

    def get_account(self, mref):
        """
        Get the debtor account of a SEPA mandate.

        :param mref: The mandate reference.
        :returns: A :class:`Account` object.
        """
        ...

    def get_pdf(self, mref, save_as=None):
        """
        Get the PDF document of a SEPA mandate.

        All SEPA meta data is removed from the PDF.

        :param mref: The mandate reference.
        :param save_as: If given, it must be the destination path
            where the PDF file is saved.
        :returns: The raw PDF data.
        """
        ...

    def add_mandate(self, account, mref=None, signature=None, recurrent=True, b2b=False, lang=None):
        """
        Adds a new SEPA mandate and creates the corresponding PDF file.
        If :attr:`scl_check` is set to ``True``, it is verified that
        a direct debit transaction can be routed to the target bank.

        :param account: The debtor account with the full address.
        :param mref: The mandate reference. If not specified, a new
            reference number will be created.
        :param signature: The signature which must be the full name
            of the account holder. If given, the mandate is marked
            as signed. Otherwise the method :func:`sign_mandate`
            must be called before the mandate can be used for a
            direct debit.
        :param recurrent: Flag if it is a recurrent mandate or not.
        :param b2b: Flag if it is a B2B mandate or not.
        :param lang: ISO 639-1 language code of the mandate to create.
            Defaults to the language of the account holder's country.
        :returns: The created or passed mandate reference.
        """
        ...

    def sign_mandate(self, document, mref=None, signed=None):
        """
        Updates a SEPA mandate with a signed document.

        :param document: The path to the signed document, which can
            be an image or PDF file.
        :param mref: The mandate reference. If not specified and
            *document* points to an image, the image is scanned for
            a Code39 barcode which represents the mandate reference.
        :param signed: The date of signature. If not specified, the
            current date is used.
        :returns: The mandate reference.
        """
        ...

    def update_mandate(self, mref, executed=None, closed=None):
        """
        Updates the SEPA meta data of a mandate.

        :param mref: The mandate reference.
        :param executed: The last execution date. Can be a date
            object or an ISO8601 formatted string.
        :param closed: Flag if this mandate is closed.
        """
        ...

    def archive_mandates(self, zipfile):
        """
        Archives all closed SEPA mandates.

        Currently not implemented!

        :param zipfile: The path to a zip file.
        """
        ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJy0fQlAVNfV8H3vzcYwDAiIuI87IwzgbtxxBYZNERdinBl4A4wODM6iQnDXDIq4rzEaNWrUaNz3qMm9bZamTdOkzdfO1+VL+zVNmiZN07RNbZv85973ZhhgQG2/X+Ty'
        b'7nv33XOXc892zz3vN6jNPwF+p8CvZwIkIipFlaiUEzmR34hKebtwVCEKxzh3vKiwKzeg5cjT7UnerhKVG7j1nF1t5zdwHBJVxShqo1H9YIm2eEZRlqHaJfqcdoOrwuCt'
        b'shuK6rxVrhrDTEeN115eZai1lS+1VdrTtdq5VQ5PsKxor3DU2D2GCl9NudfhqvEYbDWiodxp83jgrtdlWOFyLzWscHirDBREurZ8SFgfhsJvCvxG036sh8SP/Jyf9wt+'
        b'hV/pV/nVfo0/yq/1R/t1/hi/3h/rj/N38cf7E/yJ/q7+JH83f7K/u7+Hv6e/l7+3v4+/r9/g7+fv7x/gH+gf5B/sH1KRwkZEsyqlUbEBrTLWRzWkbEDzUYNxA+LQ6pTV'
        b'xuKw6xV0NISC8vBh5uB3OPwm0CYq2FAXI2NsgVMD166JAlKgJLiy6pbFT0W+AXCJX+w2mjSRzYV5s0kjaS40kuacWHK7pMikQkNmKMj9kaVGwdcTSpL9ZJvOnJOWYyKb'
        b'ydZ8JdIPJ1fIFqFgep2PVkqeJQfxHTN5YSCUUSKFgsPPi7yvD310Xh2VGkMOsBfzc0izMUeB4sluAd/G9wcaeV9v2pKN+GWyzuwml4aPgCJmsq0QqontJ4zHV4ZKJbaT'
        b'I/iumZyYCCVy8qUCevKyMGwMboJaetEyp8iWhR76EECRrRzS5uBN5CaPL07s7hsIBXT4ADkUTS7HkmsevJncqCVXl+Gm2BiEeg1QkBd06hSyx8j5urMea/E50oTv4tt5'
        b'uWSrgARyj8OHfNPgOUWEDNdEMz6fAgOyxUwOPk224s2FtFG4OaPAZFShWTPUDeQ62QvFe9Cm7c0kt2DItubnFSrxaXwUKRs4cmINvgQFkqHAYrIX30/NNaXlm9I5pOs6'
        b'2CloyQV8OPj+LrI9MTU7bSjZnEd7Fk12TB7Lk5cT08q5NkttRBAHDlA0bY2k6D9FU3+K3+gf6k/1p/lN/nR/hj/TP8w/vGKEjLxcYxQgLw/IyzHk5RnCcqv54rBrQN6K'
        b'tshLG96zHfIulpB3lEKNdAjFZY5+Z0DvGj1iN6/UUoxGKLPi2cTCcWukm1+M06A4uJc5uEdG48hR0s0fVigR/DVkjv6lupwbjM4gpxZu58xMVnyl/TOs8g+HfMlfH/bP'
        b'8i84ZxQ82JV2kLuohvLda+r8I3/gfA6x26/HfRm7J5ZL+QKtcV7JLplxGQWQL4NhOPHbYB01ZcxOSSFbMrIBJ/CZuSm5+WR7Wjq5hdfmmHLzOVQTGzWxL27yTaPzuZ68'
        b'MtrjdS9f5vOQG+QiuUouA7pcItfIlViNTquPEnFjTDTejhvx1uGZI4ePHjZqBL6BLyoQvvdkFDkf3cdnhnqKGshNc15uQU6+mWyHRbyVbAHs30yaoTUpaUPTjaZUfAHw'
        b'7dwcePk4OYUvw1LeSfaSHWQf2U32zEeoW2ZMPL5N9rZCJDqyavjtRudjbJDeCRWCPNF8I0znKgEmmmcTLbDJ5VcLxWHXkSaakytvPdGKAjfFAMcrL3YRPE9Q2H0X33/b'
        b'bFv06ruvXdxxaV8/5ZtnbQtevRn35pOvXt1xbN+xDQ7Ooy6PIVNPpSXtyM4UKnugXGdMj43EqPTS5TtiyFPEj2EUYDy20+WreILDlxbg/ewpWZ9E/KnpMF6b0zikwtt4'
        b'vBefMVk0XtqsNZWqVFNKtomHJ8/yXJXJHu+lRG7uQrI51USa84YpkaqU69mPnEek2dsVHhkzyD3SlI3PI8Qvx3dWcTPx3WgjF+BTjEbBTbsZlvCQPOg6ocLtqrfXGCok'
        b'rpXusdfaJgUEn0Okzz0qSLTT4rl4zq0KvmRUBKJqbNV2D3A4e0Bhc1d6AmqLxe2rsVgC0RZLudNuq/HVWixGvgUcXNNF4Kaz6VbShNY3ncJIhCTunornORVHUwWn+oam'
        b'PjrrZB1+dkY93poKHeYQjw9w08h5fGFmOR8BTdhsjqNowjNEUVQoQogiPBKiVEWiCNp2iJJQ4Etk1Bmf7OPJU/ZbANdngJEJ5Kb04CSso4vmPKUjCnFGRPxkV4z04BTZ'
        b'OYlcKVTGwwMlwteU+CVfF3iQXdGHNBUqJ49G3AxE9k6a4aMQ8U4nPh2dr+TIesR1QfhOQ4JUzUFym+xIzVdaOcTNRsBN8C7pwW2yC+9KTVfp9Yh7EpEXV+Dr0oMTsBg3'
        b'k92z0URyDKF6lA8g4uHBfHI9huxW4oMwH2kobRZ5yRjFYKsTMsfji+RlGGiyCf4LeA+rCe8em/k0EIhX6IOT8B+fFNhU4WfwQXwP38GnalR0bCi7PotPSS/tyl1B7pCX'
        b'e9EnN+C/gTzPoJBz5KIb33kiFgaaHIb/pWbGiPBZchXfhFeukeP00V34j6/jRh/Fc7Ib78YH8J3u+JVYyB2F/2MMvjgGZ+hq8kKmj6cyUvRgswT8FaBtu4ozyFmoaQga'
        b'Avx0Fyu9LB6qAm4PuJOJMvs2BCu/2R+I0n41n0oZPrLg8wsYM8Yn8EYLueIhV1z45nLARnKaGwir91lGNVoRLj6cvlDOWYka0FPAmRq4RhAu3XwDt5NfBvwoqoKtKZac'
        b'4QN8emaAKz/DtSxRtlgC2glOh8db7qqunbSAVkmfJCPfFIZreD2+b5bFFWD8MAvNBaZssgdfgRnfXFhAthrxdWH4cNxkBgZ+xRNNztExuR2NL47G5xwD/vVbzrMZatoU'
        b'u3BU83g9zoybvuIN1a/jJo05eup/km5llX6cvXfmJ/3iSxat+85H+sS/5r+W5R1RWDjimdd6jjsW7/1qUe1bXVNVH/wx7rs7Br6teP+/L4kvXymwlt98O2/PD/Z/+MNn'
        b'SErUwtJbP66c3pzyzukBWzwTD5q39TzU88Zb90/M//zmmnnPzOtT+sGa5w9v/EZYvCxl9NSNMvUshWlrBhRam5puJFvSEBDCc/yIKWQPe2p9ejkIKqQxJ69ACYLImXx8'
        b'iSeHp8FTij998IvAyC6LpCkNJDmQJFWL+QHz8W5vX3g4ZnI+Y5RkC8hnZDM+hy+X5ipRwkiB7BqKj3kpNi8nh+okuj14eIhyP7GsHR01KtoS1jZTF22vKXeJdgulrIym'
        b'9qe4ka3gNPADNO8bjaDgtHCt4zTfxgl6+JsMOXdcGL3lPAFtjcviATWhyu5xUznATalS+9bwbrqo3V1CZJZWkxMks/G3IpBZAzxYDePwQhgOAf4oUA+yaxZZq1hBnlv1'
        b'EHLLuHIrcvtofDmi9tCeL0dJAtixrISKw0I2nfuGPyzuL4lVS1JzSn+IDByyWpd8srAHmsnuZo2JE/8swPKotabZZuikotpC7ZKJAojNcVbdqgV5iBGHaJDA/SMyFZSw'
        b'mStRGTlLNjnujV/OexbC03lf/+RT6++tVRV5tu9XpHz0ydqLBy8v3PL1nAMbuo9LTspMEz8WP7am7VJd7j4+udvwJPM0cc6COcmlBwdmpT2TOC/O/BwVEnY+d0sl8k+O'
        b'LgYBIRrFT+1asHCEkWccW5iS2MLk+9bwJsDFY16qRZDGwWmp6TlpQ43pIL8RWJ/JBnKXHFAszlhk5B4N9bqUV9nLl1rK3XbR4XW5LTJT11PiUUoRUA/znwwI504IQzah'
        b'3CEG1OUuX43XXdc5rtEBdHcN4Rqt5ckQrr0YAdeoAotPDxsOeJYNChLeVpgO8ulm6F8GhqW2Zjgw+Yn4kAr45BG8s51SEcI6JgtygHctsiDHcO7hQn87Fk+brmmHc9Ml'
        b'nNtoTkBOcz7DuXeGeWT0qoMFNqFsKkUv59vTp6G5jJX6yGV8jeo9w8jFGWgYPi9V8e40JbLOhFGaYnV+Z/Jy5AOehVZWZ44AWMPxnRo0fEYmK5hcIqCRGjrgVid2TEZM'
        b'MFD27TcCJmbEUyDmjQAFdwcr+t7SGDR2yGiQvK261IVpUp2uReUjgL+OxM9nopEeDWtTL7wH7xwB4zgKiOkzaNQsC3v/dH1XVPX0HNqmCYsGL0SMF3vwragRMBqj8fP4'
        b'OKRH8RFW+Jq9F1qg9lBgvfYL/RCrGG/D+58YAZMypi4FjQG+v46V3ZTRD6UN2ERHZoIzpljqA9lalzQC5m4s3jsdkt2TWdFK20CUMmA3bQO/q+tqxFhykd6Or8DfJ8iW'
        b'eeiJJC0rqZwPi3bNURgXaxnuUiQ1oHouPoKvwBiOI1dsaNx4soGV3bDGhGp7X6ONLXtnXrU0Mvjgmml0aqdmVaKppYMl2eqZIeMpH51GbuNNkB7Fe1ljfXjHGir3TieH'
        b'8yC5lSnJEM3AOtd5YCBn4GfJPUgPTWMNXlSKn/PAoM3El5ehmU9MZTfJWQ2544HBmbWoAs3KKZVEnZMgB+71wDhkgzq1AWXP6s0AJpJdKwjtc466HuWQqyK7m0Nu4COE'
        b'9i/XMQDlLl0lNboxuQe5Aq02430wneYJxC/V/eKI4eQKtDoP7xwJybPkBhuN31nVKHlAb1A7rXm9h2ZLY6zqPYZcgZ7kz1uJ8vHeqaxk755aNKE2jRJH50+eXilhRDze'
        b'hc+TK9C9gkINKgAJ7yYrvGbuEGR1HKDVTr30tEGipOQwqJN3yBXodmFPvBcVVuADrHT3Rano3fgztOr+orZMKg0C3t255AqMRhFogzsgbV7CSm/vm4w21oh0snv1Mtmk'
        b'ySaN8eRlavWaTQ5xaDagNCubXhiF/nfKAFpW96chMmbWO/GpaBi3OfgavormxOArrOz8Ij36ZxFodZnWvO61I2Qs3kNefCIaxrM4k1xAxfhwqTR/2+32aBjNuc65aO4E'
        b'0sgqKHD3RG/altBuLEpRPiWhNt5XVBoNY1mCrw5CJWR7Iis6D/VBP/bVUViLNtUlS8NevhjvjIahnEdOZqB5cyTi0C+1P/raRqUv69TtYq1c6f0nn4wWqGz+0gA0vxe5'
        b'wIre6tkN/SF2ER30Xp/YbRJmKx0To2EMF9hNaAG5ZGQFp/ZIR1Ni71PovHuQ3FNQ6o/H4Ca4WtgrDy1MJMdY2d0rRqFzT79HF+Fw69I6iVH+IH0EyDvfp41yO+pkRvvW'
        b'qmFo7MDv0JXN9xjZHcg/QxEXOUI24CYY71J8rwKVInxR1nQSQBVpgqF9kjxXhZ4EPLru/Prbb7/NTlKiPWXdKMS82oKnpcrXzxuDTlT9ivbNPWx8HXJceyqb8/SDgf0N'
        b'+cHEd9/KFbISN3349Euln43tOerU4VHvXJnZfKVLg9Ct/8efO7+zd5gh9y9DtZ8VvPnBjP7/27sB9f3++9d2PBN7e8vz63cfmL5Uu+ri3riPcuM3vXrvUHaP9/a8mLb+'
        b'q3PH8v/+7tNZPQOfLoveot84ckNBQGm+86NpT/9o1j+GTbmSfGJa8qkntr77imvAr7Y9WP79G7+5d/iLz8TAl4eNlsJ/1L/+X1dS3n3i++8r094blPZ+13PvjTr3fozz'
        b'PVPKL17Xm8r2f257fl/tlNhl07cvm/Nf+36dWDn22+GmZqXt3IXvnv1T9J73lUvqjSv+/mTCoZ+O2zC1YOivChIcCyoPbWl6bs/AD94ofLHgueZvvn3v0Njs7yhn3658'
        b'Iv7lf3hMn9zb06SaE7N4dcl7f3z9+cnmjz6LPZRS9mzxbhCWqclqdQ55aXp3EHcLqG1uexoHks1LPHmZnNIzSUMrksuppqfJhZBJwWSLZpKGeSK5A6KfAW8HJTvflEtN'
        b'p/HkpkD8YycwURgmcgmIwlt9q8w51LagGst3ryWX2ctj4+I8+LyzOrvAlEJtq2S7gLqQHQK+aB1lVEaUTxSRhIkwqUUvSy2+cgsVnJnIchUSnajg4ngFk5oVHP/tI/3y'
        b'/DeRfxWt8wL/r0f6VfD/bPlVwK/mnwoVzyT2RF4vaLg4EHkArkL3Df3rTgr2zSiAYOUr70ye4tzdgoPA3hNR0DpyJIIoNQgegAaaJYtShfgilabyIZGs0kayVol39yW7'
        b'HyJFUcMsCpOiuEeSoiofTXJXS1Tup3U6UFdRytp5dWmqyiGyFFWyVIuge5ovBtU5ey6rQ0z9LsNn8Y4Ry8hFSSQHgXw3Wevopz0keKjF8q3iG59aS1+9uOPY7jMbjm04'
        b'c3DYpmGHjjUOmXRqkzH5TbOtwFZl36W4lDznQFbasmdKn9G/3kN1dNw+59Ee7+jQD/4Us2fil0aO2dHwQbI+JczC1ifdZMSHgqJ1J/jZQ8JPj9ftK/f6QLa2uO0Vdjeo'
        b'eRKu6uhwrNHwuqBwnRyGAwoPFO4cCbqHkIC+SHd5PLS9aF3ctxHQYBhdGf3GhgTqjHTj0Px042h835Sbjzdn5OabTbmg2IGSjHfiLVqyrh5ffyhKtBasHw0l2gnWwcpb'
        b'o4RKtp2tT0+Jdgu6fGoDopNxDq9lWHEwZRSq6pXFAX+If6LfZDTT8ecF5znPGHj07vFVn1oXscm/tGEZV679zdTX+3/zSrP+lP71itcTTzn39X8t8SPrM3pV3OQD60b0'
        b'RtF/j9as7A66FoXIVValdsUbWmbclC546aaOd6UTNC18l6xvpW0pFkOr7soT1zE6JLdRslojg1ZChqgkjhIud49wVCh/KCr0DKECfXFzGCp83QEqLO2Nd0VUrszZ4ahQ'
        b'h89EkUZ8HZ9/qGYvtDGk/gcW9/bIoC6YyyY9YI1FvRbU8iCyOMUnvbIYkqxAmgWbKCbo/lgSJ91ckScghY6Ky1ZdRX4Cclg/Oi148iC/OvDeb0Ab/4P1zbKqinP2j62n'
        b'bSnlabs+ty549eaOfpuMh7g3K3Jt+6wfi/x7aYZJQ4pKMuNWZL6YOWbEFu2CEd7hicPdpwQ04e3YAyN+KaPMGHKnGr+UVxWdn8YjhZnDl911XgOFjQ+TY5X4OeC3ZFtG'
        b'YT5pLsjB5xSo2xzFaBjVq4+qocfU2Fd6LaLPbhFtXgljEhnG8LFaLlE2ESl43bf8A3evEO4oAgpaPBDltNtEeLPuISYhiuTuPiFcohVtb8Gl+C8j4BLdmCWvFJJ9pIlu'
        b'MOLNhcZ83FxIrmeyrdVB5LKyFG/tWy6ETbEyHHsmSdijYFt/Sr+qQiVjkMBM8QrAIIFhkIJhjbBaURx23ZGermqHQUqJw+yMG4H+Z8xbdGrcysnFEq683F+J5i6VRM23'
        b'qzKQY/NXZUqPjXb/5tTeWy/FrM3UKX61fE5mVuAP083dZ0/pdvLqSyMrmi4ak37yyV9e9JSutBWlaXe98F+vbZu5O/bs7tGjl81OXzl92ebvHX665Mufr5wTtWZg4SW7'
        b'+wvXyr9+e2j2xROON5avTtud/N/Nk2QTJr6Lb4KmRo2N6oH4IuLxca4Ev4jPMRY0BR7tMgf3qovJCfx8BTnppWudXCWHBPOKZLp8m0hzIYc0ZCuPNyqyWL3D8Dp8Cx40'
        b'ZgAtU+RzS8hz+D45QW4xga1iOj5GmvLxOTQQ3wSYG7lZcGNvZ/KYqsNHbVFWV2lvg7E9JBrXXQOYqgeM1QLT43kNH8+DgKRy9w3hrZLiLSArRcWAqtzndVWEE8CIiwXw'
        b'uR+9NrTGYVrpwRYcTvq4A8NmGT5nMheagvibhe+y4e6LjyvIIXzF0zEnpG4ioV1rVKH8T7lhDPx2bYe+fSX07TvibbSHS1kVFWeNKkhJk9B3dLd+aArKtipqrb1OijOl'
        b'mzOG0L3lA7VU5f2qprt00/UUk6RiVaC870tfJt1ENQloIGhUsCQWfRb9hHTzzz16o7EozqcosjZ8mNBVNoxGjURVKM4F68R9PlPexO62SIV06KaoM1jzVjckSTe/7m5E'
        b'ReioXmm1Tp07YYl0831Y7A3oohibaXWPsclNehAzAa1ER6fqiqzu8nS3dPODonHIi5Lr1HHW4W9NTpRufuVJRpnop/MUVusiPRAndvMfPUChRV8sFIqsvCdVbuerpjjo'
        b'TqOTmt0+XjRYuhnbewpai1bWRNda54zpli/d3N6VbranZOth5b82IEfeq59CpdAd3aKLrHli/FPSzV2ze6KRKJvXxFkbji6SSxoKRyMnWlkL6ujwyd3LpZuf5UPP0RdV'
        b'6lqrtnbhIOnmDZUdvYniyrgp1sELnoyVbn5cXom+j6xrlAbr4F8MSpZufgfU9zR0NFYwWBtyqkzSzTGLge+h7PlCpjUvebqsfjetrEdfoZT52jjr6MMZonRz7cQRgDGv'
        b'jopG1vj11culmzsL+qPpaGx3HbKW1Y/LRo5V9a8ipjbf/oO1ZGd+AcmM2/TGpT//5juD8qNylozV3vi460z+THzT3LJRi+3lNT/qtVWojX799ebvvf7NL185+KfiX4+4'
        b'kPSnk698+euEit9smj9r7Lr5KWljX9UNyopNmTXFvu6HE36//szVzHUJC/71xw97uGZMXLv7dM5fp6w//Oy1/pualZPyJxx6Nz9+xb7fzap9YknipB091rk/4p8sOPnN'
        b'4pNbx1yd9tOnyszKve/nzz839PP/OrFszbw/f9f/1dDTUUmf/H57/3kDPznaf8VPTbuWZFwqVQw5PWBF9O+2ftPv6519Lv38dOGIwmMZ71380c0fFKS8P93/xkjbmDFv'
        b'pN1K+Dzhs88XP/3Lxl/c2LB0zhvRlWPEly9+uWLS23/3f9/0p1X/+jL/ByU7Fm5Cp5ybav33H3zvb1Ff/SPDtXPJ3+4ONkqyX2n2kHY8HK8lm4CPD53CdpJGJeHj5hVp'
        b'aSnZIDoBGQatuo7sxC8wCp7Xb3QqvDyUQwofpyDPks34ZbLfGPMQavrwpBNaHW7gp7S4zFaz1FLlcjoobWUEeYFEkJ/QgD6qEQYyQSKOM7CdpTgmVMRzOl6r0IJwoQ3+'
        b'CG3+sivF73S9dPCe7lstEHQNaN/u/iFyDiJsnd3mDqPgnTAYzj0gRLxpFS+3EO/E9zvYKUgev1Si3blkK2nC25hvyXayOQ/mqWtGmgpNJJdU5GYy3tZO71DIfz1LILFT'
        b'Tz9UykdxUZwYzfYNeFBveFHYGFUq2BWiQlRuRBu4UiVcq+RrFVyr5Ws1XGvka41dQdlCBS9GidqNGrgT5QdwpdpiSvR1AXWWKLrtHk9BuSqsPRoUtskwlbIWyREq5BhV'
        b'oZEZjKpRAwxGDQxGxRiMmjEV1Wp1cdh1pL0zAUXSwJUFkknxTL9JxYhua27qh/pZyUXJ06Vg1r8UHg9c/d6Y1nvLMLr3q/jjB5d6dxuZ/WNvQ6P63QUnmnW/vbW+7Hnb'
        b't3uif3Bu+chDXtuS74pfF5TYGg43Lj8/bs+yyfP3/DTuHyd/vfnMU9vf8Vq/d/8Hn300OLPvH+8WJU9K3vmaeHxD04c7NZUV3pfz3im7af77N+jwvD4/+q8pRi1bX9Ue'
        b'vNUctrqeJmthgZ1bxqxa+CK+2NDiPoO3j2H7sCDNHGcvu6PJNbo7fBuva9khXkNk/5oXyJZlzD1OqpvcGTWFx5vtGmnpks3q1HQT3rFY0gdP8Jn4spntD5Md5DLgWxPe'
        b'TrabTXg73q5G0UkAZCNP/HwiIxxkF7mgxU2FsPqXkeOkOdWIzypQbJTgdZEtrG1LlGvY80TyTBo+o0AqDd8dH8d+9rottRg3kbOeDBDh0nMki008OSmQdRPxy5IEeAqo'
        b'zFrcBAp9br6J+to1zW/gyY2B2vYivuaRaUsL7VBbLDX2FRYLoxh9GMVQrJJ2opPYxqAWqIRK/lFw9bEyXqfL70k0QBMQyp0etgcICq3DWxfQ1Lqop4JoD6g8Xrfd7g3o'
        b'fDUtxpLONBWVmzq7ugej4K4idXF0G2kyNEQ8qN3rny3Eo8em9sSjXVtbSXmc/EuXg4euyQa0BFFPDCNXcIYLaCzy1idcKzx2Z5iDhjRwmglOW3WZaJsUA7X8md5Xofq4'
        b'IMTgw0cCWQkgjVxAaaEj5zaF4ISAualnnx5edWeiNi4mD6kzyhKchw7rjf136lVbpFntsNa4iLW2Eq1HI8nIBDT08YTqdlYF+o9HbWmeUODYVx3LeygROPPTN4yvfmr9'
        b'2Pr9sqoKXcX/ODmUqOf/J2qlkWO6EjmKN9azdUoXadoEtkwV6RJ28xFXTozDE2b9C/nJoTVojTapvmsQE1qVkhx8BHc6raVlCYQDMIWGcSQk8TB6nmSG4mid/vMISB4Z'
        b'EBB8+s8YDYhsoW56FktAa7FI7udwrbNYlvlsTukJW0ywYt2uWrsbMJAtOrYGW1beSNZl6tZn83jK7U5ncOm3Xb5nKNJJxaAI6wioH+hvSDZqaBCv5Ln4b3VdmEQBKmKy'
        b'5HRMLlQOjiVbPHk5xlxTugpplwCZXUY2tZvpaPmvZwfXwtRFrlTYI+yJ3RMHvzF7Yh18BQ9X8o/IN6uihChBTKNMP8zrOA4YLmX7UcDAFXYlsH31RgRMPqqZB9avFLUs'
        b'H83yasjrWD6G5TWQ17N8LMtHQT6O5buwvBby8SyfwPLRkE9k+a4sr4N8Est3Y/kYaJkWFkOy2H2jplRPeyNSAaNHM8farANhpafYiwkbsfBub/quPVbsA28LpXGs97Fi'
        b'32ZeNMnGFkE0iP1Y37pA+f4M1gAGKx7yA1l+EMsnSG/vUe/RVAh7FOLgZkFMZ2KJdJiAjpbeH1sRJaaIRlZjItQwlNWQymroKgqMemaA6FPOaOeDIVpD2D/5rnTKodUT'
        b'oyqgcID8GlBQfIyEfgXl6jAEoAtHH1zuBZSKSDJUFB1AeWKDbub6Cr1MXdRMotIAdVEz6qJhFEW9WlMcdi1JVB/+HVC7VRPpv5wah9dhczrq6RGNKrvBJnfIAXzNVlNO'
        b'z3i0fWVcrc1tqzbQzo0zzHDAW272as7UrAKDy22wGYabvL5apx0qYQ8qXO5qg6uiXUX0n116P4W+nGaYmjPNSKtIyZo2rbCkYK6loCR/6ow58CCrwGyZVjh9hjE9YjVz'
        b'AYzT5vVCVSscTqehzG4od9Ush5VvF+nRE9qMcpcbaEqtq0Z01FRGrIX1wObzuqptXke5zemsSzdk1Ui3HR4Ds4ZDfdAfw3IYMxE4W/vmyMNDZ30caxe9Ch6kCQ4v6DTA'
        b'vTp8WWbT0vtyBsaouNA0Ytjo0YasvKLsLMNwY5taI/ZJgmRIcdXSMzk2Z4QBDAKF7sgQ4Spyix+lniBzluoK5v79+iSmLNUmXf8bdbUz2Lc3t+oK2BGWCWSvi9ol09Lp'
        b'KRfzfNJoBhXt6Jp8ybSGXyEny6RDE+ZtqBeHkjOHJMQmTdQjH93HiSbNY5h9sog0Utk8g2wuIusrSGNhMasovyQbn88uyM/PyecQ3kKOR5Hr5JZGcjDqpZJOYSwvj7mh'
        b'FpEvlTYH39PQHepUeHl1P1AQZ2eDXC4L5WSXEZ9BxVlqsp/cKmKVaFLlUxuD03lfQm/ZvmOTD2gM7jG5dI0b+SivdpJ75MVg1bRi0kgP4kA7M+Zkky15KjSLnFRxZnKJ'
        b'XMLbJNflC/gg3utZBhwQb8abyHbahTPknuMnd1fynneghOFHlkHbx9eQzLjp+//399N+djnB0Dz++QEzCna8c5570cATftG7xt8Ods68Eed6tt/7ryh/laZeMPZrMSn2'
        b'2+TVAw+Iq2Nu/3r94ZH3fnTr984J7z1Zf3jRhPfGfFddpy1NmfnVr0b/7Gsu5rOsebsH3XthoelXv8j6pvp60y+71n/0v5OfemrfjFszxoxYtbKi4fKNjLtXvvN+2qA1'
        b'31v1vxUJDaP/FP2D86ZF46tGnxQOmSdHv9XzTW7fzzeWXd9b/tuX3bG2z18d/9Yx96G8oaYM329GvZnzz7/Ebu8/69fWr4zxXmqhxcfJHnImGobJmE824rs+01CyJYNH'
        b'XbFfocH38S2mWuFb5AJoNk2z8a52ngqn8XpJ/dqQhBvN6bn5aTm4mWyXDj71qFXjq4oacjeGiW3JBhjxM3hP2AauCR/p42UHyq7hO+SkvAs2nKN2A6mOrmSjQG6C3vUS'
        b'Uy4TniR3mItlT2erbT+yq7+Xnai5Sy5Oh7mH91PJ5i5jC0N7rGbo2zbJ2WEWvqQGPfEAucC0tlKyPsmMD+ErzG7BECR6Nk+2PTVb8uq8Sbbis2PIdmiE3CgleZYD1XJX'
        b'naSzbifP4TtUHqWvCuQQVy/gbWXktKQTrs8CpfZEPH3bzE7AKcltnsP3+rDa0/FevE3SSSnurxSDKik+utBLWaqC7MGnQaUkzUZ2EA4GeB8+TwdZqi0VX1GSTf0Kpb2L'
        b'nXhDIqstj4OWPM+B8ol34MaBrCl4PzTzRXicnk/beZ2jXtT4EDlmYS/P7z6QNjIfiENO2hP4Mj0mVymMy5J6OZSeKYN3mcQ3kuwCoU8/TZhp7sXmRVsyjL6bBgNdYCrE'
        b'/mwF0uPTwnREtgX31fT/sYGtrVAP0rID2LysD2fL8rxmmELyzOap3UwBerGOT4Icu8d05Dj4VbX54Tk+eP1PrQp0Q4kEpwdBSPJzlKQMTKbJFBRUedtI3y2qwiPr+Ea1'
        b'VEnX1rWzOtNDFTP5nBqi+oYrGoM/jKBotGv/I+uLZ6huS2WgDrXFBUFtsQVKUIN+MGhuSGCirAyEiyAvS3HbbaLJVeOsM6YDDEF0lT9OmxSWMkd5h016MtikBwNpA0Dc'
        b'6hT+IwGuCg4Gk3M7grw4BDm1c5no8RtAjRtuyio7BG4LAU8PF6j+E/haGf4Sjp2b5gqMPKwzm6S2SkjaUWvEoG1FIw9GZ+LW4zemgjXGXRhaGB21o5KOShEdlYxHEdQe'
        b'vyWVYS0xdtaSJaGWmB4u5D0uekgLQ2pFRw2oDiFI5lymuQDscMueQZ5Yg5OdcO+wDf83pqAqo/DgeDsJdhrVPjwGR5v16rHbq9npelB5mFLS7kV64l7WxIpB84HezfC5'
        b'XYYiW121vcbrMWRBb9oLzCnQZeg4vLh8dPrw9Exj5yI1/adE7S30c+XT12Rfb5BoCkxkE14LTE8xhcNncSM+6PhNxX8jDz1Vv6lg9KfW75dl21LsKfEfW98s+wPk+LKP'
        b'El9PPLX4I/3rK1WG7f0OrBsRg2JzCBc1qLK3UcFEg6V4r7mFqWYrEkiTxFTJOp+X7sfgSyPJPioz4ZcUTMhpLTSRtX2YUVtJtsWRprzcAkfLaXTix/fZQ3wJ3yW3zEx0'
        b'4Rdz8NaWDLyBbOrMmKam1qvg0SjJWwqt0S5PAiZUHxtkCXIZ6bVRbStrMZzNh6S2leFsR0TrcOtqQaiYAsUf4glF7QrIzz22J1QlIKq/HV4U272SLcHn9DpAk5apvc8j'
        b'q84svoTXbavx2MLiRJTVtauI1jGOWVbGWfOhDFQFf2yVdrf1IQoe/dfedir70zT2lPS2L5aV6d+3xyEfHXV8cFz3tnqbq6pTtW3gAEf92WqB+RW+efzup9ZcQN20+N9b'
        b'P7YuqfjDqXzx91bFj4xbf5Y2Y+ognXHK8oSiExueODJsk4TEg7+I9vV/zshLOy6byAaVpF9IuoUrqF0gfNRLNwjIFXISVI9W8q0s2+Lz5FZQviXnFbIf1cO2Vz12ryU4'
        b'QYx1MyyNk7EUxENJOAQRsL57EKnavROExWQvimidO2uxEukhlKan0OrDUTr+mQgo3TH0xxFP9G0a3hEneCbECRgrelQUTg+eGKMKXMeeY8zxhjndUDNkyPHmUf3GYL19'
        b'CApLeyteaMm53I5KR43NC210iB1x0Br7CpmuD0sfFsFW0rGBSJSsMKz7Qa9QAJRumGNf5nO45dER4arcaxDtZQ6vJ6JRii54aIHHVR2UxhzAVm1Oj4tVIFUtDXCF3e3p'
        b'2GTlK5daNG1qDjBsxzIfrQ9kmBTKnA3uYKsAVo7XRtn1w+lGe09OTYFvIlxnkOfxBXMB3a9nkSgKTLOzQ16oc0hj3uxsYY4Rn8kxLC5zu1c7FkehqZWp+GZsNdlYwjxY'
        b'RwLzOccsLiJ+WTa6hFWB8GWytwRY2V5uGbmmmf9UthQn4AYo9kfIFR3MPDmN6oBxHhHwcV8WJVvbyMtkn0fvm5dNN1pLSGPaPOZI0ITPzM1OozC25uSRLRzQrBPGlXjf'
        b'QHJqLo/IXnxDt6SuKHapjwpm0ycMynwq3BJUG6qwaL5pnhoVrVHhE+S8w/GrXnMVHhe8Mq2/2fT9O9TLcMbsNbjwq5F5ryp0GI18OSUqbUpKnydfPbVg3euXG7wxwwJ1'
        b'n3VJKv3v5uaEvrpbvz1m/mb3lLhu+fH/MB2YMu57L9/q8Ystd0auGqv//MMrPx/aYO416363d+//2eVR/mVhz/wfP5cx8HbfXzlqjFGSjeEuvuQDMg2t3DZV8i6MruHJ'
        b'Ifwcuc/sI0vm4BPRQ0lzKqORPhM5gi9Jtpq++IoCVPN1iZIt4iVyDr/ELCx4Pd4ctLLc7cO0dPIS3pJjpqaGzfhwcP9bFyd07SYycp1cQvzh1Fqi1fglfF2TXivVf4sc'
        b'tVNhIihK5I0HYeIIucnqXzaIHG17AFaRlLEYn5kvCRtrx5GD4eYJci0P79A9JT3c7iOXwowTRQlQ81WyQ/ZDfCTfGkpKW0hF8PBs/xbin6DiJAagk9mAlFO1Ywetagk2'
        b'gZH4EDnsjCcIYcVaGMNiSDZzQffLdfQn8a8PYw2tWvJ4KjMQtg4ZwrEQQxjGdLUWqteZgvKY6quRtcLXseJ+ItSK8RHJ3bSSaW13AyK0h7o1VbvtFQGVx1FZYxcDUUCo'
        b'fW43qAEzyxVhbaXGcV2QDuZKTKslBBfyR8vOPboKnczCFI1KYGFKYGEKxsKUjG0pViuLw66lbe4PD3bKwqTwY5K4x7hBuLrT8XYU7ZfEC4Lvhk4rdLyzwEZBeou9AiNI'
        b'79mo0pdumGaroVqVTX5WtgS4WkR2Rje9gMMUF44dnTmMbXfRrSiRKrKgcHUIPjT44wwznbZKw4oqu7yZBh2mfW4pEexUR+BrXN4IYNx26EiNZ5whq60cbZW78wj8sL1W'
        b'py3wzUBMaN1P7rRmiKRRMovmlGTDrTkyc+OGx+PdeDe5YiZXchHeR9YOIif05Nmn8X7GWfELQ7qZ001Dc4HW0ipwMz4brCZUfXZuSYocFANkcHKyt46cJs+R/dIJ2KHZ'
        b'vf4ihUrQTuvmQz66tY/3985otxfDJHpTbn5xuEDfhF8cVBxF7j8ZzdqjwAemkCZWiFnIcygbTaWMNcQh4UF2Wm5eeg4+STaYhqoQaTLqluE95KKPKrND8dmYcIaaTftC'
        b'YacATQexPc1ogrIHc5WonrwYhZs9HqMUacbcg7ywgqxn0AWkmMQBVzlNdkkhym5gP7mcKtWQ34Psp45fB/mnlwxgwdnIWnKkaLYxNTdfHkoOJQwRyCFyEV9x3N7+jtLT'
        b'CKVemrWx9zup8SRTpyh661cL7K999+Sx796dGhv366jaA4OHnN5c7+f/cWpvftIrX3168BcLc5RjFx+49Gv1oK7k0zfL6kpGFd/duOVnR7b9cf/bNaVx47+6+s+iP7//'
        b'3I6fn/0w/3jRdzPyhw0tPPbR+NM7rNG9vZ+evJv59NGlPy5TL3T/82dnJ//V/srKaeO+mfjPoek3tcDRWWSd0yD03MDXyDoz43Z8GTdsMr4t6e0Xh3FxQ8PZeStWfpP4'
        b'mbkedH38AhMKisrDZYLzasnP7gVyTmPOyR8KIhbZ0ZdHGtzE43Wg0J+RdK/D+GD/cG4+WB/c2XlZIZ2uKojDd5LNLYH3euDnJVa8F58ToW2FzLlWhXdWOfn+vchhttWz'
        b'uI4cI7vxy8wHt1AKyZIGU5IhkL0GvE7aabhlfyq0l4Cf06bJewlpeRIr1f0f7QBEUwYpkxDG6tNDrF41ksbK0IQYvVb+1bHzOTwz+Wv/pVLWJ4QzW7kuqZUqiXWLNLHT'
        b'pKI11496PPdghVRTRUgmsIdYYRUkL7YWDPr/NIJgEKmtj6wtGqmjXLCDHTHkN0MMuR/lHkBbGS8JMZ9wE6FRQd2WzvAFUPVMY5KbGgbddLPYTU0H1FtRdJVbLGzLwk1j'
        b's7GtjYBALflTaDbC7klAHbQ1U8MQU6UDMa1VXCpFhYlXVeytVhPX5f9oq6kjvHNTYtqdztdqRM3dCj5RoeIU3/IwV32+5UerWJAgXvj3/uoVOm08x2ulUENaRSLHJ7Uu'
        b'Ea8wcHxfhsHfMAq6kKwV8P0MT16BtI/IIW09DyT+zPR2bE8r//V808YhS+RLFaJQqnSgUpWoKFXDr0ZUlkaJqlKtqC6N3qPco9kTt4erEPbEiZpmXiwEYSnaH1chMK9q'
        b'6maks8eI0aKOOV3pm/lSPeRjWT6O5WMh34Xl41k+bo/e3kWKQwRCGPUEivV3qdCICWIidZyCGuP36AFunNi1mXmAs3JdKqgrVje5RALUSZ2wqJ93IpShTlk9xJ4bNaVd'
        b'oW2c2EvsDddJYh+x70ZU2o05WaHSZLG/OAD+dpffGCgOglI9xMHiELjbkzlOodJe4lAxFf729qugpjTRBGX6+BFcp4sZcN1XzBSHwXMDuzdcHAH3+okjxVFwr79c82hx'
        b'DNwdII4Vn4C7A+W748TxcHeQnJsgToTcYDk3SZwMuSFyboqYBbkUBmGqOA2ujex6ujgDroey65niLLhO9UfBdbaYA9dpfg1c54pmuDaJRbJdRhDzxYKNUaXpooKpCbMD'
        b'qqxq5v11tpW8RFe+9EByAJOC24IoSCMOVrptVAaUBLjyupA/Uhuvn9buZG6ooNrudZQbqNuiTTKPlktyKNygoiXUKRlYnHUGV40kLEYS5ox8QGVZbnP67IEoS7AVAWFG'
        b'yZyCBxOqvN7acRkZK1asSLeXl6XbfW5XrQ3+ZHi8Nq8ng+YrVoIA3XJlEm0OZ136ymqnURUQpuUVBYTskpkBIWf6nICQW7QwIJjnzA8IJbMWzDzDB5QSYE0QbiuTWKtd'
        b'kgZKfHmPkhLgVXwj18Bv4ERuqeCJbeCPcseQp6uXF/kGPgnRcMWNfAMg8ypOFBq45chtauCopyO8xR0VaJBjUdUdyiWjRDQGreJqFPBcTa8aEX2vAVkUUKvyGJB7i0rU'
        b'MIIf9aElkj7S1jFOnucWv7i2L3Qk5bORkHQMm1QHu9OJTUsasnHM9ay40DRy+LAx4WgkgmqSU0FFfoOn1l7uqHDYxbSIioHDS9UI4IFBFzgGOagnSigLmorbUebrQLUY'
        b'Rx+Ps4r2ChswlxAaWUFXcZRX0dod0jgBMspwAMHa9+0TOucPujpq2BZVS2+GDPIMCXDpAS7zE8o1PvkW/j0Q0jMzC4zqQFxbsHRHxeasrbIFtPNoT2a43S53QOmpdTq8'
        b'bnrUI6D01cIycXsRsy0w6YGyHvca1OlJd8Z6f8nJ3rwKrYpLlK0eBk7Da0FAqo+VEODxHAUk3Z41rUNJ4i8hN4EgiJCXgKkt0rCpq6u1G6wwJeXA653p06W/Vmu6eyZ6'
        b'RH936TgAG6UOm/V1SMDpyXwVIiNiO3B8EFycDI6u4SV8dMjNXmATEtDYPBbmJBrQ2FfWumpAx+2wKf/g5LCQevSgnHkP+KrLQE+GwZBHwVDrtJXTjVmb1+C02zxew3Bj'
        b'uqHEY2eIXuZzOL0mRw2MmhvGUrRaKZ7axCU+KEgLtK6l/ZZu69NNHAsiEYpKHjrdxDEr/iN5+n/4eSSSU1JLRTOJ3NhXllfZairtBje7VWajWw8uaRcXStkMtW7Xcgfd'
        b'oS2rozfbVUb3eGvtwDmm0aGFzk211SxlhneP1wWCIyMONY9ECGQiEGyShTXJSsfXxxa+RGYoPQoZ3GF8qf9shC09Gi/e7q1ytXCxNIPHARRVroa+Rjfcw71wO+qjXNE4'
        b'GnF+nFVmsBH2Bju1jJS5XDSqr6Ei3ATjY1MhtpmGiCRyhd0Ni3Q5cEdbGfUc6MAY00rApAjV/jybvoD5ZZJrme5UU3ZOGlV6zfOpnYJsy4bLwhJyF29KyU3LMalQdbyG'
        b'3B9ENjMDfncFvgp65EVybXYRPpySa6KRl7enFoBefXyOiZzi0chZysoi3MyCvU4krxR60vNzyd4VGUmqeBSL9wvpuJHslMA34ZP4SGZDuPkipcA01GyaE6zYrARJVYPv'
        b'4LVSKHcL2ZjlYTGS8udMVyIl3s5BWy7j7cwu0b8gx6Utxs1kTwlpJntL8jmkKeTIVdDAj8+Udjg2VStog5RIwAfws/gWh9f2wyelkPPbxyJPtmTRMINGjrrg/XiDR8Dn'
        b'6kcxz4KZ5DDZ6KGjQnaNBeCrOHKeRrKf65hrf13p+S4UWfTjvK7NE+dMtelm7P7j/jeKL61q3vTp2m1dqz57VxRnOqfMOnRi3eC3s5fn3vu84PNbQ0pjNL27XO2+5EHu'
        b'tn29FVdLj33nf4zjxJvH0IaS721bv3XyhfvN34u5cPpn4wb8RHm67nLJud3LD/Ua2fuDD58bVLzfrTiz9a9TUt+Y2PCKLvqLr/Ojs4sbry5+ffs7P+tz6wn35N++3fMH'
        b'c8bW/Pz6qz85MnND7S+Xaf84uPGHO/WHXnNs/uyKf9AfroysWfTtF19O/mB88nf+fujt8XlvjL//l4nLR48zdmE2h5X42BA6NWbSpEYKE3mebOLw+fm5zJ6gMfdINZEt'
        b'ZHNGNjllIc0C0s0UVHgTvivtStzBJ8gN3JQBZTikyKjE9zh8BTdHSVGDrpBjZF1qbn4ePOunJtc4fLj6CfaIXOxFmqgNJX8Y2aVGKgWv6UmekercgjfjG2bWJHivWzo5'
        b'z+Hj5EUD248h1/Dd5IgWHLypQUEupOPnmJFmyjRyCu+ypqYbh6bIH0CIJZeFOvzCYGYmGoyP4INBCwx5hRzh8PN4XRx7lo8Pk4up8luKgsVrOHzRQzZLnrvHcON8amHJ'
        b'SUvHmzPoqoIqDAaAf1pBrq8a5KUu33jjFHzA3LLOnl6CmzOkZTaUvKIk6/ErNcxWhK948XNSX6lNcEc92cyhaJEnh8jaIhba3BaPXzQXmjjELycHYX1krSpijVyIb0+h'
        b'R0Hjnm45ar0Ib/XSU0rkArm81JxvNuenk81p0LF9ZtxcyFo6FG9T4gvkPt7F5mFmCsxDAT6fpkKK6fhULIfvktNTH8N/8t85TdlVIoaW1vSfmZGmUGK2RvrR6uNkAxL1'
        b'K01kvqMK5ldKjUl6TvI2le5Sj1P6l1+r4Op7yWJPRDDB81js4OS/4zHKSa8yYWIPJN9SYYISFsl8hNb1iBB6qvM2QZ1UnuzYqYYFiGHBx0BI4MICxPDs0yOPFDz4ww8i'
        b'iQjTJB4nn9WRJEMqywDLoWwrJJzJkgIVGzyyvN+eI8lbC21EjTaCRWRBoj1/m9teaLFRxtiKjwfZqovye7qvUkclkvYts5VXSbv21fZql7uObQNV+NwSa/awT888nMe3'
        b'Vadai7Fhno5em7sSdJdgyU43UmpCOykShgQ3UoKyFJWA7J5wxf8hokDko+0ayVXpfk8dSl50Q4WKrHkrrNOkwxyDRvZCYweOUMDNhkt5Runmb4zX0cqJd6CCKct+Gv/x'
        b'Qil06tqsNZ6YGB4pn+TINkTOe0t8OYzg4NMjw+hdCeWewR2bIKf1Jcylm//zgeHT3ZcWXwIgS/V94sbhC/iK46n3fsd7TkOV184U5jcP0/8uhh6z/9s7+ji+99TpE9b3'
        b'3370hRzzpkUfvjN1bsG0lG2Wr1dvqe5x+2c/OTdvbNafbLZLK77sNe7SgOF/Vgx7K2XwFs2LP/9p9pnZKzf2e3/qhx+/8beT5S5iyC91/Oy6emxxz0MfaIc+NeYn6sq7'
        b'UfundinU/u6N10cN+mzY+0393/j1nO0DLv/wJ/ei5v+t9KlvRtx6I/3pne9fn6Ax/q5r2eJ3JhxftYZbjkZvIT836hkhzcKXl8nnK/AufIvt/k/pwnwMnOQKOW8OEzhi'
        b'gT6/NE9w4ttRjFyryMnRZnI3vmX82nKLO/g4C0yZlGeU4iOBFBPP4iOVA7+jfGmNAthZX/JKkOi3Ifg6J2Ma88k2stZM9pM9LXsP5PJC1kwPWUfW0q8FpLaE94jGl3ny'
        b'0ohFTFBw5ZFrpKkO3w9FUoLLe8ByGEM/gjeuSU3Xhbgm8Mz5K1j8r+7DsoMM8xzeHc40gWHW4QPeNNozshM3p87Fe9lDaHyrweBB9tvCWTI0+EQ+XisJF2e686lsk0WJ'
        b'vD1US/g+NKyTlx7O99VntnWmuEI20w0YqOYiKwJs7i7ekJqWDyIpDWqfS8WDI8vwbsFNLukjnbZ/VOamlrUGxs6Gh7EzzWjKyFTy0YgkLp6xLBo8RM9YmuQcoacOEXqZ'
        b'WchVtXKKW9Oab3USRYSXyrZ4QeyDJIVvw62SPojArdo0oJ1STmkMU8qpJyFVyuGXms9iRM7Lw7WwgUuCAiIfnmNhnh7wgxwPFIPSh1dAh2j7AjpLjcsiK8yegGAr80gW'
        b'lgjKeyDOEtoLlyyRubx8oFzHwyjy9d2CRpU25dqZC0Ob0DQaXiP71MQG3j2ggWN9QUsFt4H2yd21gTtK+4COcau4mmivIHINLE9LVgiSERGuFfRzFcwSwhc8GBJim9UO'
        b'DzSjvIoxnEFA76l9iinN9AJmjw1BgqO61ukod3gt0oB7HK4aNluBqLl1tZJVig2KbIIKKBl3Dmgkm67L3YG/sN5S66auwHYLKz+bDhaNb6xlnjd6GiyPU4G0wg7IywPX'
        b'6o2IE8+GjcVcpVZQGApqB13CVfBJKDgA8VJtKbSTaVJX3atCk6pv3UqNxQIw3RbLIl42yySGW8ekZx2jYDxrSRAJ5VZspK1QUzSDUQ8D3Qaf1BYaDcDCDjKxExRxLbgv'
        b'P2ollNFrRRBwMsP9o4AJIneMX8UGoYFbKhmmADw34QzvPoZkiyFcs5X4fIRmqCwWp9diKaOtoNVTqbY+JtQO+uyxm8EFR4GfMNFNGar7TAeQ7RZLBdxxvwQ3wqHaI0AN'
        b'zX96+LLpElwQS3lXnAR/CbeUmqnYfXrFNkKliaDt6ABhoTn2ZRbLEl72b9cyAZ//VsuHNYyWaNewkJlQx4aDAtUFTYQSgA66XwPdrA1Of6thr4k0AA8bdkVo9id1OuqV'
        b'MKeeCKNe+e/MtTK47vhJnc81KByWFZGg2iOssJC/Ox3S4EoPOUCHEen265mawCyWpymkiyjMEB180qqHrQTWgRF72I3u5CBGePkNEjbRIU49I7QsMEZKg1FDng/dbdM4'
        b'WPE2UbRYVtMpZ4yDhWAMW/XscUTED8Mv2sBjXMthoNsdDTolbqzGDREGw90e1iMMRnLbwWDLnDO5b1KotyJ32uMrs1ieoW24Q9sQRuTog467q2dNiG7pMD2a5n6ls+6y'
        b'GpuCtFzXipa3hyagMKpCNesQVVF7EaMgkE9s32Vq+Q/oC1zeHOCddnrwyC624AEbho5O0Vgs1T5Awm28vImhZYdTWyEBK/DISLBR2pXBnY0Kq3FPJCRoD6sVEowNH5O4'
        b'9ujQMzRKPduOEqMJXEYLYnQwItEWi9fts4uO5RbLfrowWmivFkSE+vhQY0PF/v329gi1t0dEROYzHt5gHbAsp8vlZk15ng7q63RQE0LtbHn67zc0KdTQpMjkZ9BD26lm'
        b'wYQslhdDTQxDMVfbta8Ib10rubRLeOu8tH102xpa0nK9iF/FrxLkVgobaHsF6aoiiAoBFYwIgAXJm1HNt1E46QwqGJR0BpQrqlxOO3XnrbY5akR7RxKm1mKR6rRYLvAy'
        b'udAyRSaOp6qN4tv6LqEeB0t2LFVSWU7iNNFs6ENrvWPpkYVmq7RYbtIhPtV6iNmDR4GmbYFW+TBotS6PxXInAjT2oGNoiQyaV4LEhaES28N8ttVcdAQblCOL5V5QWolv'
        b'xbbKIkHviIezXl7rBJKjBgSR10LkqgUOe/DIcDZ2CieKLVQbVPidEKS48DVMH7k3oQim0dA6oSeg6MpYitwaL2iczKmDEwVRQdlGN2jGKroiqBbHN/LHpDUirww2EMqC'
        b'T2ilD/qzrVxHTaWh1rVC2gwelik5Rfhqa1008M8DPjM9wA2DlbIlOF0BzTKfrcbrqLeHL6KAGmqqdHhBn7WvrA2qbh3aDGAcGHCL5Y2g5KthYUjpB+7CRkQudIZxGzos'
        b'xow2vn9up1yfx+ny0tBi1EM3oG9tboZ8RYW93OtYLgWmBnLqtHm8FsmYGlBYfG6nmwaMdh+mSYsXYQg/A5qQwh7NrJfSximzhzPF1X2IJozKvECTkzQ5S5PzNKEBTd0X'
        b'aHKZJvSLJe7rNGFy1F2a3KfJqzRhbJXQhG69ud+kyfdoQsPDuH9Ik3dp8iOavE+TH9Pk58ExNsb///FKbOPxsQyS79O9AOoFoUEKQaFU8Aqu5SeOT+T4rh24ICp5rg/H'
        b'D9FwyRxv0HJ6lS5aI8CPQq/QqOhfnUInaJT0Vy9oVHpBr6E/uiidIP0kCZLP9gm8baaHbCXNkjuihmwhd5J5H9lD7nYc+PWnbVwSg6FWKxQs8KuGRX1jgV9p7Dc56hsL'
        b'8ipGsbyaRYFTsihwajnqm47lY1g+ikWBU7IocGo56lscy3dh+WgWBU7JosCp5ahviSzfleVjWBQ4JYsCp2YOjkoxmeW7szyN9NaD5XuyfBzke7F8b5ankd36sHxflqeR'
        b'3Qws34/lE1jkNyWL/EbziSzym5JFfqP5rpAfzPJDWD4J8iksb2T5bizOm5LFeaP5ZMinsbyJ5btDPp3lM1i+B+QzWX4Yy/eE/HCWH8HyvSA/kuVHsXxvyI9m+TEsLzlD'
        b'UtdG6gxJnRpRqYG5M6LSfsyREZX2F6cwCpwViKVHYOa2nC798GLbraDgIcywQnIIujbFqEMF8+4ot9VQ2lhmlz3YvA62ERP0wWBxzoK+bdQNQ9rxsLfem5F3hFq7XVCl'
        b'KOworJVSYpt0ikd0lfuoqB+quVVtLnewQodXsotJrwY3WKZl5c+dLtdg7cDxrlUmp0L2IbEZypgVD6qT9sXCj+qmSSCDfZWdK71uOx2QVvXZPMyXkzaOeXYsh5psTqfB'
        b'RyUsZx3lPa3OALd6uRXPpZorpTr0XICnlKMs0K2hbLA7auR9nFsXZIVeZr48xq0SRGB7FilVsFTJUhVL1SzVsDSKpVoQPOnfaJbTsTSGpXpRgDSWXcextAtL41mawNJE'
        b'lnZlaRJLu7E0maXdWdqDpT1Z2oulvVnah6V9gYELFoPIQdqP3enfwB8dcAxNR0+lgrCrWKVsUByFNXqM82wU4bobWqWo0bF7qmOce4eoBiY/qEFBLYKrFN7BwPQVG3jP'
        b'Ie8QUdOgkAy33hR6t0G5QeDQsuWN0K8l+kaQAz1nc9F6gMwE56gC90+ogDBKQvx2y6TzhcA4xMwAZwnwFssDpWWQZ5DnwaC2lVTZqL9Ti8uUZDM1BnRzgPM7qmXHRJW0'
        b'NShFIhUsDjGgtPjsXjcNFCOdTwjESiHOQ0fV3NMpb6J7dG6qUbjpXosUuuRJJhm0PuUIkp+0Bww11vrcINHaAQSTCtTMkO61BVSWak8lA72UnvxTWuzSH3YOMCb4Gvsc'
        b'GbxUXkX3L1kkXJvX5wHRxG2nFm6bk0Y7qqlwQYvZuDoqHOXMPRmkEYlWhB7bqr0tHQokWpyucpuz9fF7Gom4iu66eqB9bK1CNeyvFKE40MvSZshBkoV1KJdVwnW1J6CF'
        b'Rrq9Hup0zeSqgBrmhc5JQJ8VnBlpJtQeu5c+MKokbwD2XR7V0hX0A+9hwQtWo4dHTmCz+Ssq95UiaoDWRAiSpWl3p8MfnqZxclh6PbNr6CGv4Oq7tRmBxwr4LEU0dv8J'
        b'oY49PONB15EcT5Pbggp5oE6Yy7wIapa2nKZMk8IgeF3yCVTqACgCiXZU1AHhDSOIj+GQyvSOaZ01tmuwsQ8Gtw6dRbfcq13elmOvLJToY8QGcmd3Bjc5BLd1xKz2YGns'
        b'0scIWGXuDGrP1r0Nj5bVBqwcSPTRR7nTQFl9QnCNEQJl/Qeg2XbC3M5A9wuB/u8sgxQ+1uMrk49VMGdzCk92fJGjMXXaLiYkSRWxPUUq09TCa1QeYdFpIsR3SjcUt9yr'
        b'cNgpQFlAgNqhQItbTIj2ewxD5XEamgaXDi/7G4ymNZTtHg6VQloNfYzBKu1ssFJCgzWyfZSSDvAza+r8rAxIZjwilspW0i87a0dqqB0TWh2Op0FA7GWtj8m3bc+0OTOm'
        b'Z0yfMXXuY52Td/+5s/akh9ozh81+GMuWnaWCDvRtvHjSDdNZtBLJZ8m5wlbnkU+HG2rslTaqez86RYFWftVZK4eHWjk0iOpBT6SwBsuc2ZBSPG9+6ePN2V86gz4qBH0I'
        b'I+4u11IqyUpn3EHAra110eNLIBL5pFPxj9Xxv3YGemwIdOzc0GmURwchHc50/60zEONbU7BqWLO2SnsYGtZW1XmoN5qhKCunANa48xGBb5R2jr7uDPik1kPbAtTpqmwN'
        b'05BinjNj5mNEWIR+/70z0Fkh0JInXo1o8rpM8KeFcRtSZjweTOjug85gTg/B7B0x7oIhJf+xO/mPzgDOCgHsJ7kbgkhYQ89tyEtFioVRVDKn6PGA/rMzoLkhoPGMxjEJ'
        b'WT6C8lio821nUPJbaEJbykXlauodQ69TphYWmnMKZs2dseBR6aZME+izDqEXhaD/sS301tJ+umEm0IhZdmhPDZMLPSGVO1LIdyBe83NmzqWB29MMs+ZNSzMUzcnJzyoo'
        b'nJuVZqB9MM9YaExj3jYzKcpUyXV2VNv0wnxYQVJ1M7Pyc/IWStfFJVPDs3PnZBUUZ02bm1PIygIEZgZY4fBQr9Nap43GnpJiczwObeM6G8J5oSHsH0bUJdVIQkwbW4w2'
        b'D4zi40zcvzpDm4UhqKPbTpykwaUbslqOjuUUzCyEKZheMItSeopKj9WSbzpryaJQS7rNZdxeUhthCkWKO67HEBRhrSg7G2pLC42X46aws4gSIHuL+SdcF3mcfvKdAS9r'
        b'TfRaiB11wzZQm1UEphL0CmFbIPNkgJ4hzGVNx7YEmS9UrZ5eS6dV6ZYH/Co2QGqh5ZXMxY2dk7Ww9KgKUvUxwMqW5j8YP0dyVaaWq5CMI4lcLTa0yCJZulHj/oJ2s5om'
        b'bWI3MxsEjTLgptG/jHxYgOc2u0TR9MNtcpV2Qd5kVPHJ7JNLVMdVcfU92yqcYe90PFPUiiYGHaXmSiAjTRPdmnAJ8q4baNLt1NuQX0uHpxeT5Tlyq+lW7jFEt24rW/xp'
        b'oP9qjn4WiholIrqqaWSDhYV+jIy1XIqoFakxUsGO+50Y1hgptK7IybvazNQVbI1S0kM68Jxz2msslhXhrYlsZGDlCowDIm1VMeMH21wK6NsYriaHMKcFaWqC+BKIaW23'
        b'UslmK7XMudlnfAMq2WSllCxWCmawUlB7FYsIEtC1MlapZFuVgtmd9G2sUtHhRimVbM3StBizJEOSvrWxyp3GyejjzqBXwzh5EB8prJr7t5D8iFqGPkDSllJ8ND/8MWNb'
        b'qDu4r/jPYmV0+Ff1aOV0Co1WI+iUPmo+q8XHSONM7I9eHlOrM+aSrakFeenUk5x+NGBolRJfxI3kYMTAivSfZyUK374S+Y2IfalQEBWhLxUq5WsV+2qhdK0W1aIGymr8'
        b'fAUnfaGwNEqKo1GqZfFreRpPA+5GsxKxYhxc68QuYjyUiBETGOVIDCS0wfk8B6jqirCGKsIpAXU/p9TYwlw1LBzdjLbwlTSCgCCGhAMFUwwCUaGvB8NltUu0Oeln4/q3'
        b'NWZSiJbwTRNP0JtjLMd2a4OVaIJ1tCVxdJN3rSBzL8mUqOXqe0WA8/iR7d09O+N/z4SshhGhPdY34mSVfnpn8PxBeI8jqc3orMbGDmsMTTp1iwi6frQEMk+ntc7ssGp4'
        b'sIVWfbHDwemQ1HfmjwHdaYHZmtcyAtUcgtmWq8owGUH/v+GqOygsE9dx/2S+2tZ9P+RVQz9sFXST8kR5AbDskM+cuJYKnh5wzVyi2DW9UiwV3H28Sml/DPKqo2rqx8ch'
        b'efUJBQ9M4XJvNT3VX9YSKmFIm5YOaV1cdNmls+uS4z+L4BI8GceYBEhFR5C8NKXPzc+iV9k0YX4ldHaAo9XWgrYd9PiPDgPBinbgkCXYRHF3UEjSyodKtMyZpB1vZkMM'
        b'5TvGHq2MPS2+PC2z2QZzMuHF5wTZ6RPEku6RgEWWx0JulYlslUgUvAFNRxs4WUASCtpJv6GX6EkESj2fUtEjGFSc2ckvYy5vEqfl3SPpyK6Wrul6CHDetrgYC8nRYOsT'
        b'Ub0pUuu9Lq/NCQSJbj95JsEFpfOu6tpJRi4geHzVEQUlJXvreYrn79E1FXFcWJkCo76tiNTiesOQpQVPWqQJJlzkc/IMuItCEkYnwUmmQaFVgjx2GgR8WMUCs/I6QSPo'
        b'BepUwj4VRa7iIxPJ8T4R+DK5QjanAf2aTs6r8zz4RjvmnCT/9ezhWjFnmFz2IzynLBWoTwn1KKHfEhS1lPXSrwaKespqxS7P6Uvp54OVwIbjxQRgvUp2/lVDg1X54/3d'
        b'K9RiotgV7qvsahaYSvrksFpMptdid7EH8zxRiz1ZvhfLayHfm+X7sHw05PuyvIHldZDvx/L9WT4G8gNYfiDL6yE/iOUHs3ys1KIKQRwipkBb4uD5Ew5kj9uATnDbuNI4'
        b'eB4PPTCKQ+FpF+gNJ6aKaXAdz65NYjpcJ0RliOPkgFw0DEjLtxf10Ns41t8Ef6K/qz/J382fXNGVBcCKKk3co96TJA5v5sTxFA6MicDCYNGgYF3pdwrF0dIzgDRGHMvu'
        b'J4kj2GqeENBRXAx6RAS4ogBXaFQG+FlTA3zOjAA/oxj+zg3w07IDwtRZBQFhutkcEGZNLQoIOcVwlT0HkmnZMwNCQSFcFeVBkTmFkBTPoA9Kze6VjCTNyiky6gP81FkB'
        b'frrZPZdSNz4H6s6eE+DzcgJ8QWGAL8oL8HPgb/EM9wJWYFopFCiBxuS0WvrB6OfM8UH+1oAUY0sRin2ueKTY5+2+CY1QpFjdigIf3c/DR6LxXroOvGRzYTppzmeRRdeu'
        b'bAknyoJ5puewA4V5aTn5s7NhheTSw5j0g8aTyPpYfFWT4Li17iWlh4bYyJ/wxafW31tT7Cm/TrFl25wVzrI026JXf/za1R3DDqwb0RtV/v6vZ1Uf30gxCtKRxUPckGh8'
        b'Ji1bPtXYg7yEupDbAj6Pz5AXpMiU6yxd2LeYbxeSLQCahgU4xK/Em4h0MBK/xM0KfqmZ7KPfapa+1swTPz6/LHjM8OG71XyQWAfPNsonHMey6P6J4VjV+gvIypbdcjf9'
        b'InDkr7sC6WIlBoeKhSBfFoJhpdeF/8S/FeEQY8R2lGvCZpsCbv2JTA1DJq38oXFpBUpheVo+kalpjAIEiwIE0zAEi2JIpVkdVRx2LQXXb41gtG/tvxLYq0D6XkQzObnc'
        b'zOII2gdKYWtNpnQapJZFeaUTX1K0Am/MxqcFRLbVRpMd9bk+6v2Kn8cn6qQ3yUbQpOBdQL1C0zz5oHUuaQaavd08P4Vsnq8BFFYgfAtfiI4h50axo941U1WoqD9IIgar'
        b'c+UkPfLRqR1UxtGT3uQ2h6Sj3ovxYVb6mxoNOjq1H0JWq/OkxYR81KUE38B3u7aKTxs678wOfavxDQEtLFbXqclBFuHFRe6Te+achrJ8cxppNnIouoAnp5bjYz6oGY3C'
        b'xxJTs+n5cLJ7BH6F7MzMxButZtQfXxPwvRJyk0W/JzfTycnUAnpMuDm/JOxseUq6KYU0ZkC5oTQar8uooV+7wC/5qBEh/skeZtKUk+f0ZKiQqhuvx2fxPoaerGF4H97W'
        b'kEqHeyw+a4IS+DY/mmzB53yUGZN1+EW8KVWajXYAAdrsFBaAvShFahbelC2gPnjTVHIxBsboOj7PQsx0wdfIVs9yclkBwM8iDh9EZHse3shg4FvkYn34ByNroeDcFJjF'
        b'prS0/BIaRt9FXgker2+JPElOCDpgzM/gqz662Mm5GfiCWf68HdmSZ1KRuwJKmCWQw/3JOR+lnfgsOZPTMoCmlkj/wQ7BqF1lpKwpg8dbePq5wPvRo8ZK0QCWkv34ONk9'
        b'Gy7ryfWpKD95hI8FwL1eGAMDfmnFchAgNq8gl72qookopiePD3bL81ERZ2wFOeyB+wBwKXkhbV5KrgmwAKglgzQnpaVJKoR3k5taRJ4hV1gMZrInjuxMpYMBg9OUQbYX'
        b'p6QAQWzMKCiRPzCAD+ET7CMDeC0+E4X05AWGU2SvsTiaXCdXPeTYDHJjGW5e4dYtIyA/dRsh4I2JI6RRa4KW3yRN9DsopnQYXeVTLhSP9wr4ZXIhjy2A+p5KpHkCUOn/'
        b'sfcdYFFdW9vnnBmGgaGJgIio2Bl6sQBWEJSOUjR2uqIIwjBgL4jSUZqKoqhgQUVRmoIl7mV6zE2PMc3c5Ev1pt4kxhT/XWaGAQZL7r3f/z//c2PEYc45e++zy9prrb3W'
        b'+86INQoZHMnRWQU1I1Ab5bGEXdMkhNFlG1SmzNNbqqcgtFiLq36ImdsVLnI3++ftq6M/77pc95zjjNkBptNn7PI/kBxwI8DwC5fgAUtsRjaEza788BX9T/Xvef/sYiq/'
        b'eWvV314ueyd6hN35isbpA6WO9ySCLLzhZo3/gjeX+jTYzZs38MYww+jpHuYnDy7e8Gllh/DPsQ6b7P6256lfnu80Xzd17oqw+37DvioMPXSrvuR/AjdOTUiS//DV++4D'
        b'764w+fzZ6+YegR/dujmuJeelp1eOt/a6VGVxu2jg17uRkVvJDdsKueK0RcW6vc998/Zz+7cnXt8U2nnnt/svnLg+NPp4xc0FkmemDflswguxL0lqMvGumD3285HvekwP'
        b'7Xj5S1tFeXh2w/KYt7+5dzk/IOT+4S8si6afur1/YMbUiNDrJ91jnjoz2G2i95bpL35ttdx01uq/Dy7x0atfFJt+7vMldSfemP6rkf07s6PjL9u9sLZQ9Kzj6yXv/D58'
        b'w4c3Z5dBRllHw0nbj/5AJ17+6OaPhbYPfD56v36t5Z/3hr+/rHCL8VH5KEaKWYNX8Q7tzRJVhKk3y9z1dK+c6oeu4gWFtuJJzGieOBk6J2AhHMaYIfZlbFGhCMDhEG1+'
        b'zjEr6WYajWqgABXnmIiXGRtmQpsC2rOMJZxFhijKEpqzSHJJToiYQPfMhnJOyOZ9g9E5isIwarQ5KhmuTeaADlija7TaYDiEOgnC82krrFnIoYC266wA9eLBFB7JQ5aF'
        b'ik2zoX0NtClxfbJBklXCCrRvM0NF2IE6oI4AUfi7qak+V5gzWOrTeMGcZSwRUDlZm8Qz3YlCDUnxDbtDXMIkUOnECev4KQGWtL0eceaoQYlXRhGWDrjFYm8enXfyoogU'
        b'nlkrKYcVVieOEB4rV1zGqSxiPKxN4hXZRhlK6DBFRajEVGpsCM2m2XjZQXtOBm55GBZ+syToUpoXw74umYEOODpDaegqdAabNpIFPJyZgTroe7mZob1QHIia8G43kxM2'
        b'8bPQEXSYIl9snBhLmC2KY1EnOhMYhvBW50Kgzm1QmzgHNaMG2q+OUJ+Gb0tbR/DXsfwPxXrPDAH24DdqZ3PmIBF8arJQZzgFbXT5c1ahYuOZE2hHQPOSDFTsiucV3sYC'
        b'9ThJrDASbR3PkJyOoaoEcjF/tkp66XGyCAGqoQnOUOgqJx5VqmjFHIIjyJaMJQzeKyXccDgmJiAha9hAtcG5FG3+MQJIDs1oj8g/XUm7avMm/PYEdKsUWu1DcVcFCYPQ'
        b'BThK56XzkjiKAL4Crjm7hIdGUFpYnrOBWnGGAZv76CBcWUUoRTV7h0nUWNQgChuYRq8HGyE8syPWprk4Y0UiRIRnYJEAJyAXV0GHqmqVDF8nCGlleNp4Qf0yIR52OmYR'
        b'jS3eHZrUF1EB5VfdgbbjWoLwhHSw18NbKG48w2M/hs6iWnxzuBPKDUSFripJrod7pENPD84Ys6GpxpK8jTCUaDBUUnyxUD4rwkNWsziLbGUT4AoqJwvDGC6j89paOipE'
        b'u1x7Gq+OWECXjjJEdXAAXcwi/pWlcGghftoNqnqq+PRhrF8XhMolXCinjy4QspwsYugbrycLVUV42x/dreEifaxkH7KjIwN7Zo/Aw4Y7HRVGJPmyRyTYUhbBNXd93Zr3'
        b'v5+9lToVqAa/po8GbzhVSglbxYI1BSwVC1a8NW8kiHmVf4A3483wdUP8PcmZlT4wEeErArlmLpIIEqE7dpWdzHX/Rn4O49db9tLKtVheGw1VyVPqYGYx8bdlkkWe6UuM'
        b'QllCXJYmLlmiSFiRtDqpNyCK/mN0RqM0M5NXFZqZRX7QQmhFSvIrdZ0reO0e69BteYy9ocPy0P2OT0Iho79M9Xb9oqlqvOY9K3sidzmNC8x5mGv7vuZw2p5ymqjzL1jr'
        b'7FRYJT3A6R8/SFf1rrJlqqCqZQ9hzflD0xAnXWFYKYrutv1Fwll2VN1f/cR4Y/UPi6bxVyT66i9T3DI3PAmPV2alJyf3W6tIUytlVMV3O+Pb7UhGQHckGGkJjaj+a0S3'
        b'9g8bf4mmAQ40MiIlWRUKsZoEoOBeT0ojqSyJf63TcRcYLdNa0/02w0DTDBqnRaIylhMYN01I41/hcM0se9iAG2mqHNc/XHHPirXqpQJWA99HfLkaJHjmROBIes0mfr3B'
        b'Ro46EXjqOOA281Fan3NUvu/eBetilOufNnY8rT2Zf3LS2I+JMNSJUduDXqhn1IfCTrEiXZmaSPljkzIpmrhd3PI4EiuisywNR9PM1KQ4EkNl509zZ8gAq8BvaQiiChhc'
        b'FX2Uohs8V4UZHhsbnalMio1l7LZJdg6r0tOy0hMI462DXWpKfGYcLpxEmalhdvtlFczqs9oJPL4q+IBhCrLotXVaQWGPBk+PjZ0Vl6rALeyL5keTvbhe//F9hlwUnuJz'
        b'/LhIQbRwgwMnN2z5Ovb5eGnynVARJy3g22rq5TzVnngo9ddoHUzngFPeKrVj0lrmmON7nyOJk5cnUQyzH4kh01NL4LZIhq0f3WPbUSSkLqO92308QgpgBRL3Fjsu6maf'
        b'JbSYZmIVxknPLZXbZvRV301VSbYVrDuWw7Veblgod+zxcnsI2hu+TOwn1A6VISERZlOceay9Q4exGzQu+Q+R1/ZZqurl2sehTEJbqEfqYm8FknhgCkMdgp3QqWjmWiJf'
        b'RIQGhWGroJHn0GlUKPOeBV0p7rtf4RREUK0YkfJ1rMvfCbmxfee7nznFhVJf8t3YL2LTku/GFi0PjsOz4mWOq7KQ8sd+kYuyiFSDOnQZNfSq/qq+DhUWK7BwTo/C2s5D'
        b'J7bowN7Fo3KUMSg1ofMU8i/IZAYqnoBaesw61ZTDKn/FY7ma8RxUqOaglY45aDiC8Aw9xjxUqOZho1gLv79/CkE1UNdmzVwtwHPVpr+5an5Hx1wlCqP7JHT4SWeqY/j4'
        b'dDJTzw8xnpLtLheYa+nKbL8QAoOYgC+JTXl0Yg1UUJjreVMReQYaUQu55Mnj8qrRhZSM6bfFVOyvCl79SeKK5YEJoXhWrPz4pN6F9wa/V/P6vqh9pm5RT23d+KzNTptn'
        b'Ld72Dr1uVPsl9+wJg5SoXepTU213fP/IBZoOpxYFMQ4FvvdIGVmaGRqK11vpHik2NsJDRkRrZy7BQ2Ha31CYfa1DF++n1v8Ay3ry461/LLd/+b5RT0GcOaV6B77G6/Tl'
        b'3BXxK5KN6Cod+INw49ezWHYTpSEM7fKhRi2dRZAHZx/DqOWhtc8Y9grxoIOlS7Ab2vc5NqHRHt2CvB82cVLqiP4GxuTdxzie6RtV8m/SYvoOSt/NVBwenVLY5i4oyNef'
        b'T/MPiTOiO6n4g5xxvL0cujXEPlslPYHvd6cUO/axBllIS/9bIylvdL9boy64Tt01/Nv7UucE76uL4gn+5p06QUF8WZcDrjvGfRF768rz8Yufbt19pMadcpWPuif6viYL'
        b'b0VEYMClNOggLs/jI4iLSDyDR21wDY5Tv04WOg/7u5eA1vSHC7CzX7/OebSfEe/WwgXUFcbOpeRhzhJOCl0CKl+OavsZTdeHLQ8Tl762PQvK7Xc0SXnj+h3NNx7He6AJ'
        b'++X6nF7aqnt/JUdPL0ncgBE1NdSRA0L+AKrR9IgfyNfLH0xPNW3yh+TbJttqTjZlf+1k00h7dmkmwpRwetiF9s5UEoj7TnQ+KFR95rYb2AAoiYq6IQHKN6Kjskys5LSZ'
        b'kpMZcmbEmaEGATrXPkVPOfEUOUhg+C9kzUNVgYF4NCPQmYefHMHOtTLUNhqdkEvokWY22pMIndMU5MyHg90cKnEQK5nX3BGKZqEuaFFKiGrEYS3z1Aa6xTri+bcT7YPD'
        b'MmgnhzttHDoC26bR8hy3DIdc6FAQDxIUcGhnDgG5JmWfswxGlTNlpCvgHIf26Y+i3wfCNT/YFakgEIxQwaGiMHt6ohQxWUK60Mxt3qR1q42CVAeRu2DPXKiAi+QojRRU'
        b'T84mL8E+2mRnK9ysHbBd62UyIF9JQoegk0NttKNw56BCT+3+geasTGiNCnQkvnx2vLYb7TPYFIPKabFppos8YTc6iI54uomx6VDHwVYzmZJojGgrHoL6Hme8KpiZ1XMc'
        b'586ZD9WewVH6XAzsk0AbahiiJIQ9cHlLvO1qT/zJnXMfiI7SbkCHjdHpLVFA4tRcOVdUjupT7z148ODOGjEhMrFzS7aWIZErRwnJE2QeIWo4G6wMB1I68lLX4Bh7KMQN'
        b'iMLCedf8wCCiTpWEUT0qkryWJGRtmvESdBJVKkkaODqWgGpInIb2rfPIC2D9yzVC1Tvah9bOEnQmjBB3dxlhEXIAmpXLcDnRTuiYMX6m3BhtdZPqwdYYOCSBsmjjWeY2'
        b'0imRqAtdgUNwLmD5WoPkQRmGcFmSI0VFBhFGqBm2Q4MbXNkgH44qtkDBZBfYL8FLQ45apo2HGms8x44PUBI/xdRYiR5sg23GnLtUhJpj0IWFUC1BhZCPqh1QHlyBXagM'
        b'VXhHD0nZjE7C1iHoysqRQ1AHKkE7UHvyBsgTudvjVpQOh/P+A8PQVbSHCg861UZ72/DjBU7aPCwycmhKDkfPgVPgJIliIcS2WHY29SS37T5e1eK3PQsdsgTU7kXL5EOC'
        b'uN0c5+amvBD0prWUU5ITYWjH7d1LXqTGgLMzwh/mLV2FKtAZ6IQjvDvKhWOTPaHYDBVBZSwW+Gdgf8w4qF+IG77VMhrlJqGC5XAYLuqvQJfN1qETo+nB8YhJQi8C3iwo'
        b'ps0MdA7WM7ckwTaoUY7/J0ewpw2gA+2Ea9FyXklct1AFO+H0WOq3L8YKFJQFOWF5gafLIKnYDcqhUzmZTJbTE1BzyEPZeuGUi4awl5L1FsmNUtDebBqXsFKMrvY6od5s'
        b'0fOMWut8Gl3wxM0ji88LlcJRYiHwqFDMCaiMn4ku+NHwIzHsQ6WOgbj3SljkUYFrcJBzJAsLoYYinniV2nEIgdiCXEOEwJxI53kCty7adJ0vnFKSlHlsrbWjPTOSWHBA'
        b'0FxVnIjKAg0MjaDv6zJXmg3tcwODw8KdnMNjGM+xVlACFdFQEjkAHUMtI+lE+JsgUHvazWrITH2HdLy7KukmfBUujAohZ0kG0EyOk6TQLKACvLYO0KmCzkGdeVSEPGxp'
        b'IEOtj5mvI/iFwyvgFBZChagCShbbYUv4ImoIHIGuBY7wROfEHNYHtpnjRX4RdtGTfFQUMh6LzhZTAylcMIWWrAwlHLfiOQuFKGKiLRXuqATqrKKgenOmZ7AIS7szHJxJ'
        b'g8s09nEFjypC5M7UHg/HTbKXByu39MxMWGInRbnRUEJfch1elR1RqDQaStEe6CSkRHoOPNofjw4riSqR7ekpyzbh9e1wPXuwXLGfSr+2XLvuqfVQHMpzvBcHZRzKp7yi'
        b'FhK0h4b0PIXOsBM62UIBzqK9JmxLvYAuReGnbMdqHSEbwGFGftSEt9qD9FTWE0rooSzuslr6IOw0lpDghv1oL8PpH8bj2VA9kY1TiR+e93RSbEJXHOXolJgzMhNZhkCp'
        b'kmgv+A2rw/DElqOm4dQDQID62XmpHjcWbdVLnpvBQMiOzRExoT0EnVDBkO0TUDWcQ6fp3gaXoCLJEQuWRDw36IGf0XKRqQk6QtfBULz/NIQEof1wQcNSMFJgD17FIvYC'
        b'FDvPQOXh9FxTskSwRHtlSkbCsAPyodhl3WDKdT2RR41wSMmM6MNYZp4JcVbE00v4teuTzdjmvx2dtMQlmjhpCLLhxDiql8THo07SykApaSSem2Tx6nEjUKWeAdSsVxL3'
        b'SyQqm49XOjXiUSHuOnmfrgnfCMfQNn28r5ZvYcN3yWwDOYjn4KIcCx8DbwEdg/143pKhT/FDx/G8bUW7UJ0CWvQ5AZp4Z9iKClLmtL+vp6jFysPz3LiAqJfSBrpbtE3d'
        b'FTq2ZvzNVRVXl10+MmOd1fmTN9q70uJyCm/4F50KeqvaecSswEnF8wI/uJ48K770nvD2Rm5Rw+YZ03M/CXKY+Mut5z4ftmzZe+9H+LsEVThUDbg7dmXmjDKrEyP/ccjr'
        b'08zpGRtGVtaNXjcr/rMx0wx+mH56m5vh/Qeesx3/UVL7z60fXI4syIqYvBB9PsPxVEn0/eDJFiV3TD86lZ189u75w26Vo8qH5Z47P+lz/btjfMf+6PCWLGVxUavMtf6D'
        b'KQ0nd7/5dNmwjta9QT/MTvPx+zk3+9ySgV5jfvKAl0Z9XW5jvz876eyCT/ftvTg1uib4WkbxJ6+/EPS3I4ucLL9flPR7ysuW/1ie+YPlxpd++MTmt3kHN39+696bh55N'
        b'CFj9yarpuwzLJxnGNac993zTgjFrPvvI99i1O284/7Ho7b3r72zeXhxy9tBSv0V1P255+pflU2q/Gn/4mOcOG9frrns3Vi3NyLqwxuENxzWOtjcj3onYvyzxdu0Hz6RW'
        b'2ceWDqoImLzzaMDp5XfGjvB4x2nSS0M3vP/Ce61LA+Ve/q9wVwwv1bz7+9C0p75ZWzrxzqtHbnpOMH4urtG6qmjJN+5pWT6fnBrT8be4DwOmn63eljQuPXx9a8y8LqNz'
        b't66OPQu/7W5Pee6quOy1ER9FZ+l9/UfUhrKckz89+3ue6OWPbtxZNP76RfdfrO1ckiq6bmXUpFl5KMLmHPrp7efn/VCe13hhdmnZvvUJgzacHX06dvTkmb/6vrp6yaXd'
        b'WflLbnS1j7wz9b0hdzbdsfmOXzP0oux9blqi6fflP3/8YOYn3+Tf+vLeuDm5W14e8fdhK2+Jp73G/z3q7Khpb8Tc+Nx2xFX7B3uUG4J+G/TD4v1mL89zUW79ZdkbE/75'
        b'tavj0MMbPnj5fOjVJneXKovO5Daftc6pdT8MXXI+5wSMmjv0T9GQb01vna2Wj2ExBrscxCQuA2+g6720Ai5MUBmNjZkxFgvoCGd+ijGNjYEjbpQaHa7m2FLRhfaMoaLL'
        b'AyppAIehr/kE6OzN65EvxirSfhoYg1dNXhgNZvOcTqMvpKhNyEZVgyiRWaoC9lKBCnmDtARqJrpIIzsSUac/bmMI2qMlUH2sGKf6zmwrEimE5WJBjlagkGUijYBBVfqc'
        b'Y8imdYyKhBCRoKsxtNCBCXDQ0cFF7op1miInjjNYgNe5tTW95mrq6OiSScjvCp2wEENlgjMWUMfpm0yaqIdqLXswxhC2mBOmjFusFbZTBjKiwoxBuyO6FVoJNzxEDIes'
        b'xtMqBqyAdkcXvC/Kae1YnxU8N8AVFieUi/b6OjpDyVxKWUPjhNxmZblS7QBachK3KFCpNMMYLihIDJ+O4B1ok2DN8oQ5jWzwnYJOd7s21xlTb695kAgdRoewyWFHim2O'
        b'kISooyQioMKZDDI3APJFWG/FuhINfRGjugHokgEi3PauzpSuUJ8zjRCtQGVQxgajZYCpY4QTFI0fQlnT8KyCqwJ0KN3orDNCNegQVTXmQ5GWqnESCth71+r74p3lIpzv'
        b'5r9ptqfnJKg4LFQTMnYea/xkhqlixo4DG5nwAVBLYnyaoI0EKrHIGzgIDaznTsCleBaDkh/68CgSbH7lMz47vPv40fglreAl1Il2qgKYclAXo3TLlzzVK6oGl3sEzmqi'
        b'ajbBbrpQjPCcqocdYkcXebCjhvpuqyhdDnn0BtSAt6N2rEbj7kMNSsrFI0sT4EAYnKQz2ht1rMIbYtzQ7g3xgBF11YzwxwYpVh868ct0qw/7RrGIuWpi+jD9AXVs7tYf'
        b'0G4rNnOvQGE40R/8Z+hWH2agajoUoVg/2AON03EbtUOYsMkrNl+BdmdNosM117yvX6hy7sM8o84olwoZrPdtNwwJDeJRVxgnRPIOwegqC/DqmhFFSPWmD+sm1UOnreRG'
        b'/0rojdz2P4g/+y8EAt027YW0Sd1eYuI17O328pAIUsoXY0apiiS88IBklLHQHwJZZ0IDhKwIlRH+RsB/xA+kIpKfju8UEdojwjXDSI7YX/Y7eZaUYS4Qhj8TQvUhMhdZ'
        b'qe4ypP+aCwRH3EhgoUkm7DcRDT8SBOI+eyAWhD/FIuEPiVj4XaIn/CaRCPcl+sKvEqlwT2wg/GJhKGwVfhbLhJ8kRsI/xcbCj2IT4QexqfC92Ez4TjpA+FZsLv7GyEqi'
        b'ypYzoox9PdxwvbqKOQ9ZvBKLJaJJZhPID28aqpS0tjusoTtvq/uQw/J/bcTlUq0Wzla3MHO3plETNCFP1GO5C//q0J/H0u9VXeSGD+sqOU+T18IfcepKzl15ijj8xKeu'
        b'H78r6AhT8E3OIgSGcampFFdViycYNzCFtCwutQfcKoPqSkxkWIRxdmlJOX0KZcEv9rGxc1ZnBaUlx8baxaemJ6ySu6igcdWBD0pFUrIylUQfrEtX2uXEMVbFxBRChNiX'
        b'w1i7ESlp9MZkiiCgyhhNUrA0UoaPaEeQnuxSEhWPz1lIgA987IJoAAKekYoUAj+L6yHBCHF2CUpFVvpqVqzm1YISY2PlBCin35gN3D/q/iAfU9Lssie5EJpsP9yNOaQz'
        b's1bEZWla2x0WorNE1btRTFwa38SCL3ABBCG3RxepE3KXZ6Yr11AAPZ0l4lfPSklQpsZlsvASFbc9w3NQ2NmThHgn3AW4Wgq3sm4N/jUpK8FFTgehn/AS0qFZSepxUY07'
        b'DT9L601OqRr9xHSaDryGoCnrKrPHADyC3JHndJE7Gqoc7a1QC+dpcgtxs4+H5kGCCVxY3e1oHxPgrkqBIPkP8qQeGRBhA5QEQ9LE2EvlfrSTimBrDLoogc4MN6iyGRY4'
        b'cEzGJjgXiXagppmoapFfUBbWDY6gZunUcKehuPIjUOuPuoavR6fM3OCkD/MOJhDvoN16SWysw1W9GZySqDML4CDWsIqxrhNF6HlbXWAXSaUhaUr63MiVYjgdAbn08Xup'
        b'WJPn7IeQbIsvPR25FJH3uyJFNin45JIxL0422e5mFvDapIQf/xH0grD7ZIuZ1Ywf/T8eX+7b6Ce6mTjo5/Dt/jnKrDBRxZyTC3Je3fS9792w7c+mKf45/1f9cO8bzT9/'
        b'Flk+4MXopN9j14QVbF+y2bB47y6Y13L5b78E7nultHH2igVTj+xbFO/X8ju/cKvNq9mT5TJ2sHQJnZ28eqbKwtGybzZYZTGmTM8AFW1vpgs2b3ai0/REF5pR23Cd51lU'
        b'abGDVh16Sxq6RvUi/S0oX0G8sM72Kh8UHB2HddTdItTsCk1UQV62eZM6o0cPdaEmlRlUjM5SDUciU9AYexJgj/ajWhJkD5US2uYYdEzBguw5YZODHz+Ly2Lcjq2oa5iK'
        b'3FIC5zcRY2HWYFXUfAzUE6MMzqHKXoZZJBygAfpwfCRc6aHihqGL3SH6zilUOdxgAIf7KLhYuUXboJopuF4mqtO6RwaOGJBUP7pCqUpDSAp7qzRYqfGilMGCmCoQJiIa'
        b'18yb944Y0BSljlnRwGo8JGJBLrA7ujfVCvxrvVhFcdR7U+W2mes61u2nISRwFO8vy/AG0wMXQZ0a21/IoahA9FiJsWRHvSfWsaNGJaWp8FJ7grErFWyHTaIyDgvkAL+g'
        b'mVFaAOv9bUtJ8SkJimUJqSm4FEanq0aYSiaIkQkrXOgdLgHk50x6W3+47VqlqvrGhwYpOmmiFAm+sCKJNjM9M5F8gQW+ToGswqHvtw0us2JCYynGnHJNanpcovrt1R2i'
        b's1ACYqrBjCN7hSp+V6FMyWJo8JpG6d4mHtmqmTOjY53+6qMxf/nRoDl/9VHfpxb+5Vr9/f/6o35/9dGnAjz++qOesXb9KFOP8fD4fuJEg5IZQw1TbZISnewcVNPfoUew'
        b'ac9oWBoap1sX6S/GdVZmHIXq7p7DTxLOOp9or0wqZHu6uPVYLTQMlwHksuWEK8xOiftrPeUXHaOjCd1020TGsHaw5ZaS+AiFS8xpccVqFK6BjE07a7qE2+hvQxKnnV43'
        b'krBM0OmwHy4rZAJsXUiOHThy7szc/nI4jzfKFjc3Nz1OgH2wPYjQJu+Jo8EEYehytmO4C1YY0B7oWMuHoKJUWl4YKkNbHcODBXwlF+qsea8cVE/P0TcsXucYHkSeKIiC'
        b'g/wULzgmZwENc23QRXr2BRf0OFGUyIafKkA9CytogP0O+FpzFnTgfR7OTIFqfsQIlMsOQ4rx1qzwwHsdn44uQx6HOoKgk17yhPIIBbSb4v1MGAi74DjvAIeiaNuh0xl/'
        b'QY/z16MOzhVVoX20hcvh0moSoWAwSBWjYDNZLtBDKhM4ZNDdQgUcxk2MgnZ2yNNojA5rNbFhKWmipyp3Gu2dgWrVDZmG6mlD2tEV1pKj6a6q5htYkqz0etglF7HntkMr'
        b'VHfXmTAIV7kSrrJeuQSHpN1V+qFiUiVqHsLOCXdAA+yVZRvgGSCygX0GvCtcgRb6ijLYaiQzJgAyIsjLcuKnjzZlz2yHPBtyjiMz4TnReNRqxE9Hlxcrn+III3gu1pmw'
        b'IhRF43vJKTHWfnHjUcVGrFuXQB66jPuwNhr/UgWXceUVWLmuQpfN9aA6Xs8Y/wjDbSqZYjcQa4hSdNHcFJ2EQvuUl75PFCk+xjVsumm05G8hq9AMM/3vat69F7jxmLPF'
        b'/QCHgrrD76x9y2/wlBvmX7y+PkORYvl25fIj+Tcn/TT8kxHPL03e8mP8lM+rWip+8F16crRr8PTEqNkOQ7yLBk3+qap4f+n5qNLvfG6/9eEWi5LPp5y6eLow8bmfY347'
        b'sn3LO98vjP279z8dHEpPvJrz99Axgy2H34ye7LqnIN7/25+MwtoTP5ozeMNZr/rTxruXPF2xxzjO8dbh8/HZbw3ovGZm/I9xmfWLpu7IOK0oeWVo6usXDO5yId+2H4o1'
        b'zVn0t+bnnr1aN77JtUlR9vZnNX/e2/vJH3o+EfOOGt+SWzB3cH7ktJDuNEaZ9WDi1Yc82E8v+6CLxLesTrS9BAeoY38C1qfp00VYL6911Ip3Nhrh7yTS9xpI3YT2WDVu'
        b'UCnx61ZgJb4DP0fdhA3zB1MMAD1ObILOojwets+EKuoiHgeFKVqpslAdTLJloc2WXoWaJItu9bzFiWnnnlBE3auboAGVOxKnP1Z8xwzkpFCM9V8rE1qpO7roppBBG8Fj'
        b'KLZA2zg4CbloH/XYQrUlVuaL10zAEx/yIxfixTbHgunuF8agZnJFgq8UBKI2DsrN01lb8CpFdeQaKbJQDx3hoAIvGeYl9g8iKZcsCRUVoS51IqrIf6M1q7PEExUosvHs'
        b'5tHxeT4cHEAns1n35MLRqQpUggpIc3YnzMcWhA/U0PZIrWAnfkgPP3QCzi/ioBYdgtOsPZ24NdfwyjbCth06OxyaSFLuTmhlUYJXYTu6rMjOIPXtg7OoCrdgClyjlgu6'
        b'HD4SX8LVoT2u5hwUJaRS0wMbQJdRg8ZkmjyHjTKzmNARaO4n6fIhEc9iBdaCqVmRqNOsMIslXk4Txvz1gPg/ideUeDOFP6RigdJ7dP8h1MaUBF4w5Hv+EWNzRMDXJQ/W'
        b'D+gZwozrV6Op0HRJI201OrOyh2VCoxHx6+zRWCOVmqzGavzpev8midlFHSZJf03haYRR5gfk86BeKFa3xcsigsJvy5bNjImMDAifGRQQxWA/NehWt2Vr4lLS1CmPJOno'
        b'tqFWTiD1XmqyQLUSNkt6omBRUCzivaTWFn0/1jqb/5fc7plziSkoUk0gKWembygiAG2SP0wk1nrCDGyTPhCEv4a+aSY2MzMRCB2cIJ74QLrOgpcOteCVdriilRFwUCsd'
        b'AbVCbhiVmTazxSlm6FyfwF4j1b8KD74nORwB72LAXbViFXQX+0wAvAzwH/KZAHkRGC/2ffdnM4KemTiQfrZItNR8tkochD9b08+DE20ShyTa1soI7Vy+JJlPHJo4LE9K'
        b'0Dur9Kv4RFmVUZW0ypz8SRxeqm8w0mBUons+AQeTYGN3dOIYCnOlTynbxuVxifaJckJJR56tklUJyQJ+ciD+a1ZlnsJ+M8clmlcZVBkmixMdEh1xmaMMnBI9CPgYKTXf'
        b'IN843zzfIllK4bpI6QY0qFZCg2wHJEsSXRPd8qQENVTMLZTRBEPP2+ZkscykFBYU8C05KfO+Rw91s+8NKtY17Zvuu2Dd1SdFke6jyEqk/3q4uXl4+BAV2GetItGHLB4X'
        b'Nzd3/Bcr155y0W1xeERk2G1xYNDswNvimMjZcxr524J/AP5pQKpcFhEeuqBRnEm8Bbf1qMl524Bh/abgj3rJ2HBWPEm17qRaceYhsuLqyI/DZA2Lg8KjGP7jE5bljUVb'
        b'z7IyT9ECo/zn+d73W5GVtcbH1TUnJ8dFkbLWmRgDmSQB1jlBlUDokpC+2jUxybVXC12wyeDm4YLrkwvd5TcKFHEsM4WAKuIOCo2Y6Ru6DNsI98eSRs/0C6ItxP/OiVtH'
        b'xF4k8RgrsnChLm7j8U8s/EhhjXzmfJ66fhpIW42igsJnhwYs8/ONnhn4mEW5Y0l9qMcr35/U68GZmekKhR81XnqWEZq+PEyxnJbkTkoSukvCDbxAyjLt1R/3bfp/qfuW'
        b'OjtPLutRCplumW06yvbO7CDf9irEmxbimdlOrvVfuft9xyd409v6iUnJccrULNr9dCz/72WRUNXfF6tRVbLsGNRGlCMa7QcXoTTlB6MoMU0wefetV0LiBt9RpZiM4+31'
        b'4x6SYHJbSohfs/C8pmqHrlw4mmkym+G19pQnLupn+89QuIpfZCr+pLDXqQdw24y6dGgCD6urUZ/t2QodG7dSs3uT+fklaUt0eJ+8BkN135KsT5rXwKk5SRkeW7KhJmfB'
        b'8HFzFj7O1dfh1QxiacUp65O0fJuMeIgdOxGp/BBfZpSaHdhuDaWBoEqMwqfvjc52vVaOnb1/gPzht5GV98g7vO3sHRQp5Awre5LLRIfHKJItZjv7mYGPvlm1aMnNTnaP'
        b'qqd/gWJnHxT9RE+4P+SJx5UNpIjeje7PbaxyfTEfEcv4VlFOqekM+nuSbKDssd7TZk1mSnpmStY6Bhxs70C2ZULmRTZmB92eRAeyXZN7yObpQNzGDmTXc5C7dB+zTnTx'
        b'cHHzUd2iu5juE1k3equq1O6vJ9KvWdH9vRhDp1C9mg7sCdY/4xQUfqLf7qGHFj49IQPoItONJKFK+e+3Td1wET4a2tq+iBAEnUFzKK/jzJ38h69R5kHiyaceVBoQkBSX'
        b'RSaUQs3LpgWwQY6k+8EdIF5YXE5OXKYqfkCLDoP2jl1UUhJ5V2WqFtWbzqJm+kYHzI6IXLCM8A5FRAUsI5QzUbSVmrN7RkDXbycxIcT6h1JEqfBa1OOmNuBU/mPdR93d'
        b'PmV6TsFK6Hb5OvSSKQ79BgvQEVrD1qmC0df1EjEO7O3Ut6Sk6QZFYNAbWEVVs/CuiEuzC4iJ7Mc3nmYXlZOStT4pM5UOXNZDGs8EYj9rCS+YoKy41HX0wf4lnEP/c1aF'
        b'GcIGpBtKhMx81ZBoYEXYMVU/b5TFYh+0kMV7PNsDEqZfqUVL6nNugLtHpUcp1NO3V7m6x0TF6NhdL2XSjE9KTU9bTkp6hH+daCUGfRQpUxbQAF2odg5UCgtDCDKdiBOg'
        b'nrf3VaWqoVZUMp8GOyz1VGUVPgVXWawD9U/tgQurYfcGgmKqgjAVZStJzCXaC6dRLTGGUQl0oM7J0AEtJOXGGPIEKEZ7UB1NPYOtw4aFaKeEzXsE2qc9NITpBQvcBLTd'
        b'BPKsx8lZ0gJqRAfhALRA7jSVO9iIn46bcJS2E51ClRkyODiLOZGd8KXLNspIfGUK5KOTGu+mNqQqFDivRgdZhswaY+NIguxq7xweY28PRVDiCkVOBMOToZQ6E8/f3oE8'
        b'aoCOWcw13Tw3Ee2ARgpAqgIfDYEueqTx6jJ9YvmvveQaGxowypCjCVEJzsRH3Z37E+gSHAaF+MVdE6AwEgpC5waKIlEhyaWDS+jYujEcuiaWwT4on5iSUDJSpDiCC/ls'
        b'0+YxpedNcmcY7Xxv2Jqcp1P/HuI1+cLg5ZMS/v662x3JTgOrwhe+XfT0gbRfbr9xJOzquX98NG6bmdWCwbkFgsngKT/cbPk1fNrSwZsbvMsXeVoqD7ycWrXq5zWb6n+9'
        b'Meqn/OVHAi5813R3xceDRp1a8vPsA+Ib1w6sWDF+5Pt/nNP/ZODvNm3vX5zuuET6enXwwitJdZvn7VkzYb7ppJcao2bdDrZ8z7X1U5c67mm5MfVeog4oRLscXZwDFw2l'
        b'odENgtt6dJwFMR8KJxh+BEGZJMw5kbgNfTgzlDOJFLnD+XgaGhKP8lEujYauWBvYHYkOudDGYOB2W6DL2oEjsHetCoywGo6xmPJO6FqDzkCuyvvM+6KDTtRlPRNO+mtF'
        b'hsNJNxYc3qiKwS30gQISj5EV0SsaY9lEFvx7Akq9tcEF7UyYV9cJTlH4PjyMW6FEdYcKpXAcbNUGKvSFkzRa29IeFTu6BKFLcNIJ6ydagJKoKIC2Fg6hFrQNioeibdpg'
        b'l1vgCnMUH+PWoWIluowXYAe04sth/CwHOxajWySDA0p/vPJDcQ/E8+6rILcHKoXhv+SE04Dg+fVjTplvJI44iYjEthoSSDzionsgFcQ8izglcHYmgliwIVGtD3SbQ9rg'
        b'dpkZvC7HcnYPkLmwh5lhw04/rhn2JIBzjEvwtt4yirXXHxpWKf7E4OZ0Vahhd3Z5DCW4N1QccVdFBfpG3hYT7tbbYkLjKtfXFVTLQlZJBOttfRXbd+YzvI6seFP1hjKH'
        b'02TFM/vRSGVBGjNM73zTZNMnzH0n0TEnddmRvomJip581ep9VIeXT6OB9TVHk+18iH7oE6vBKonVcZTvpNJnNAhbJFSyb2Rpb+5FRj1MzPRuLTWL9GSWSod/LOtIpddq'
        b'2HkfZSAxci72rA4K3TiFXXJqehzxHNhRrlgVGWZ/cTRxaT2I53oz7/bXih5Wgy5i3KyktUwlztJwya5mYZ79xG3ie1ISiT7X3RXd9H3sHezsKac8eTWqr42MnOXi4jJS'
        b'3o+myaIhaAxyHJlNWozSmpIZZSbTgLuv6yxP80w3A6ZqCqgitXryYeoswz4yYFYAObcJWBYeE+YXEOlkpzZMGGlov9FdNOi4f/LY9DUsCPshJazVZev1w9L6kOLIfxpT'
        b'kPTwwyw1DeqbalbrLE1NCa7LqLPDvRIQGe4b2teA0x2n/JhGnZrEi3WFhkyZTFjVvCHrAtvBSZQvOzY2PD2NSIqHBHCvzequnVLtkj6KSyVB00RAaKZucmb6atxViXH9'
        b'RFqnKpnvbHlKdlKaeubjpZlIonrsE9LTFCm4u0hJuONS6Le4l/ttGCtG2+Mg135NFbV0/MqkhCwmD3TbOFERXhPd3O0Y2S17H9IGJxVeqOp9qQuArE0sFHWWk6zMpGuN'
        b'rnZGWtuvocd2JR+7KJVhpaaaJ7Ho63Atqal48cVlMvOK3axbtigU6QkpdBA0Zt6azHTCGE96EXetarDxQmDTXndnahEx2oVjgy9uzZrUlAQab0gsbrqetGPrda+dmSrG'
        b'+m7iV7Jh29njn3InO7Jt29lHxETKyWCQ7dvO3i8gvJ916KCVLDBR7vAYKQya4C1fjajvxaH0sKDQHtamVKe1OZy57WH/dNSuiZ4fNAlhw8MWSqgmxGBaklUwLQFxRoWJ'
        b'HpySBUcvgHpmY6JOS2pmolrzWQwHptpNrID2ARTVm4Q/pfDU5PNZ5UpAXTLQbrEK1yUe9kfTCH1U5IU132xj6w3UOO1pmepbKQlLCZyAWtQKxSquBkLpEW3PUt5CnB3m'
        b'BToFx+g2UYej8m5ahXMBA7AlU2tN390hEZu26mAlIwK3zU9HbaHK+dRcRC3JT1hbNxkO/ma3vQa4Qi7hfNwsoBnVetEeMoStm1TRU04LLHGduXLlOvx9ABzEpi9F9HEO'
        b'jiDWLytDDypgh+GYwajRsNvenAHboBZfOGqOdqCGaHQ4cS4q9NuM9qNcdBr/qcf/7ly1Fu1Gx/3isW3il5kyd+5K/NCJpZljFqOaVSvMOCibaotqpQuYgZznv0kG7WuM'
        b'BE6AywugiHfFdx9UEqJdOA1HoKjfpkHhYFQ4A5XHYwMbt8mJxMKomrUDjkIV+UyCvGJNId+OQ2fmDrBG+6GYTov16BicVUWZGYxS8K7492tKEiUAl6ajo8QTcCFDRegx'
        b'TwXhs0apjIbda4xNoSJa1fdafgLiGyADpEb4UMPdoG3opJRWZAIFVnjG5kID4zc5RrB/KHiQNsQSdEK9NowQeTa6x6hCG8o3nj0WbVfOpj4NqEPbQrS5kUrRmTl07pBW'
        b'nBkdQlFHSNSgniIYFZnjaV4ElZF4RhbxcC3DeDYerW3KMNKkI7NRUZ+iArvx80lLu4sjvA9VFmNQbjAct0Qn0DErSxGHasIGoGPrUQGFkpoYbKuCR5oEu7XhowQ8tFW4'
        b'otYpeJRyIQ/3MA27QxXxHORHGkWmB9MFaABHY7X8MqFB8mBnl3lQ0AeOSt0o456LBlexF3fZQaU5Kh85j02ro2st1TAScwOfvGw47KspXsJFBhMXQ4ET9aLNJJhBal9P'
        b'Eyqj/h49dJiG7NDYEHN0cqSGbodS7QxBZ9RsO6g+gPA4pqy0O6en2IvNra6LkrC5V8KH+Jp9+EHXlbZNOe3ut/J2ewTXTTOdMfyFph3jhcSQWbdFk2pWxQcMtqmaffFr'
        b'+9/Fl3lLvSTDjnUlG7tszW9+s3G652RPR1FQwOqw6mK/aKcBH+1YNGnn+Jq33zS0X3C8wf7XpPDopv+Z6jFndcJTHZ3ho5c4BHtfchvyj2sVTW/8VDAhyfGTa+dHDEr7'
        b'alvYgpYFNT7VDS8sVG76eb/Bs5F1b8361fu9lZs/WbH1/pWa21/V2cyty3zzYm62SVPBmdMuY1ZJmjoVX7u+FoXgu+jvjOqfe31F9b3hT3+y9Z3KLyZv/fZQ0wPjzeab'
        b'XvA49802k65fPjw+988BJ+2Up/8oW10wN/2dmz9zi+/rh58emrmr8/3cu84/eKW25P024Pb4FV+kmn477Ru773+799XANxe8A69O/8Q2xvVOWdfKbX8M+XZum/6DI59s'
        b'uLkvfOE/HhQ2tbQd2aXMVtjNaT9eI93sn/ll0DLb5U2nDz6VXQwu37a+taW1rvmZmmurXdwiX2z2XnleefHEkS33W+fOCV9kA+OLPcJ/eXGjyXtPWdy9evrPt7bs2dRg'
        b'7xonV6EV7HJAO7s9RBGwh8EHLAhk5BKHURc6h4qd0cXemUsDPFjmUvEEqGd+p8zFxPPUaU7D8yKWzw6B+k1awZYUkebCFlXwHlyw0qI0geNjeHQAzlgwv1lZKr61OMdE'
        b'iykFHbSjZCmoHq9F6tryNsQ7zHmpU08+lnR0gbnNKidu1IZ/QLsWqFxb0ACVDHNiO1yEi+r4ynB0VOV6WwZXWSOrod5DHbiJ8lAdauVhO+pKp94oGzmcJlC4QeiMmJOk'
        b'TkAVwkh0Zh11yE2CAlROcSnwjrDDcSnvGofaaKu94ORILX+a+1OqKEk/P5q3j9rhApR3u9Pm4V978X4MTqUFGUKHQwgqQWdVEl6dPS+Loy2wMdocAmVOhEtO7IS2yrC2'
        b'YTKZvnX2ZtTFaF2YC27SGJUTrtKEhlzKcbcUE38m82YO3Sy4oZ3ZNOkqBuX6h4QGocJeGfMJI0ScG7oocZ0KTTT6Mn1NCvVY4s0kwnmMvYQz8RdNRQXjaAUeKDdWk1S2'
        b'YApc5eHM/PXUi7dmLeFUcQ1zluO6p24YJ9gtWS2XPnbmsul/JgJvlxrjsYoohTqcf9wWw2lGvIlgJpjwRvivRDDDf6Uic97IjAR2Sh4YisQ0iV3KC1sNBfKZJKcLqu9p'
        b'urxgIaJp7fivmSBRpb2TLDMjPZJ3Zi4wB6MJcec9MCIp9AJJQCfX1o/U4WV7whT0bm9Z5vM9s9Uev/+1M8ef15E+riNzfLeeOuNOhwuT22b/uQ4n5mO8bf8hPdOIj4/4'
        b'9lhkCJcs0QT3iB4ruGe5XHQ/to/dEJmUhk1WxaMceNRboLJQiH0ap7B7Kiz0EWbIAPx3WB8zxCmcQRVWwkGsTVWjjhAtqsneSHTF8+37gFxgq6DJ2NIbttJNHR2GrmxH'
        b'j5we+7p6U4eOlVQ3kMHeOeTUQfsoCOtQh2mSLrTDJdhHLmW5YIHrko1/BAfBfnQJS5LRS/UmYcWiixpBy4dBHRT5kVpwKcMIqOQeOEJryBLGQSWWXETcas7wsOJLLapj'
        b'i0WcmFuTLOVinXbPG8GxU7+6IDjjCbs9odzKjeDXH+LQNWgbqCTd5iNdTBJNsMVEoCOnQB5T2Ktxoy+FQJ7MIJMAuTViK2wSKqIpIYHeUOAod3CSErySdTxss0bX2AFi'
        b'GTQuCCE7iuOWcD1OYiUYyVErK69yHJRGwXEsrEvx+KA2vK3OheP0NG8pdMGOKKj2hJJJGtQ4aIUTLAHl0OqJ2KBBx4JVh3lzoIk+th52Y9OBZJiEh7G0lmp+BByCM7TC'
        b'HIEklECLqQzO0+wUG34q5HpSG2nQmLnYIMQdWrIGGwYc7xA6m/bTFjwNtlKjDe2FItWxItoeT9HvJoXAvihUitXZQwSkshSqCSKdNIKH1sFQRTt/yLQyzpaXDpe6xabd'
        b'czNhNm5ewkjOn/OKknGxwvTJU9iXQ+SB3G5uxXJpbKzDDpONXB8yZs1iJBOPkjHL8PLjDnMb+UQukd8hDOaOqGmZl2Nt8kvi+Cc0N76JmaEpaUmNKmJmcSr+pTezNPHm'
        b'L5Fw3I8CXTZKfzJALYvQARrOzI4iDdTKL1TQ/Ak+cqI3nryFqNAbdmT7LZ8xKzkjKHNzGto2lNvoYYbO56Cr9NUOuBhz1twtP/Gc2NCJtpHsfU/IrTgnzn6j1C7Wdu9I'
        b'CUd7VGG2vBecINaNmiicIFzzYClGu+ajRmI4wrFFzHbEhuMlyGfTrdHLDF/LwAN5yBjrSBb8ZOhwovU5DCKOBa8NvF2s04uzJnFq4PcSqPXBkwmqparJtBivbXJlKTqD'
        b'KrClCJ0oj1qLvKt8IztNrklDuJUy4wDYnqnPicbyUyfZqfAll6CmZVCEyhXhBFNKkPF2sBNd/ZcGk1C8Z75EdoGXyY9XeK4PMTgZviY8fJmv4ousJwqhETpl2dBuO9NU'
        b'IK33Qkd9mDdlN7QqZehIADFO8MpCNegCsOWqrwfXsiZAixG06+NVV4kvi+AQBVFEBZtHyjguHJq4udxclI8tR+rQOZUDZ2T2Do5wPhTP/WErgoWFhojlmKW54IFpcQ2G'
        b'Dqvh+KIe2s7DHlQO5SnbWgx4hTde9WGtVkkxQam2MWZ/PPjl7huHam4U/iOj1uul2MlxYbbjxCjtaSeTbXljRkj8irihHx/6p7/34Y8GPbtbwtvkid9/3Xl0mt35QKnX'
        b'pxK/vz+9Y7L94jtFeV5r7sQoJ12onBl2bf25zX80fRURXRC86YPTtVENv92fMLR6ytAhHoUmMTuH3ql15YZgm+OeieXA2FWLLX2i47+5bFj+muO9DanXPzKOzpvXkPlU'
        b'0fiY+z5OsyVOn22MWjDUadaXTkmnxu5/cfWOgqKmvLf+Z33D3w3P7D/p7zUPVkbvny9qyfI+8+7CxSHRT3WMWfTROfT6JR/rSR8bnXVeNKjSZvG78z4Z8emKp/e3f9Zm'
        b'btxatvKHJbtq8rdPe6vL8dOxt1fO//Xb3I9mzGyfdtTjs5luQxrjlsQVXSmed+lUTnnOZw9MVvsfvZo7Pfimp8nuoudurDrofn3Qm19tDvo68dOcBSXfb/EPHTLxkOf1'
        b'X968++eMrwceXPHxzgE/yUZOzLAw9nT9cfFOn23LLNNfeTaieY/FndXnT/1yQpl7beu48+81fT/x9tMrf6l7a9ib/2geav3e92fLf/X58M0Zv+U/Hb5Ib7zL+yV2lt+G'
        b'To1s/V75xmdRd/Z9nffBmMBn3jk+LH7WvGdst1Y8u8Q0aXzM0x/sfuWFuS7POS+dc2JC6dwNx0a+WPrjxWca9lnf+FD8nvF7o15M3WxurTS8u7RZcccrc3jqtbdEQy8b'
        b'ZnneneGz89mUKJ8coe238uYOu2+mLk36zmpkepj3a/rfmX72Z+bgD1dflgRH7P/c1STL9bOa39OPvH/oo5GZm14ZvKFuwfXWwe9e/fiLO6tuj7z42QfbjJTR/9zddKTi'
        b'p0jriUdzV6/N+XlCWHBZ3buT41DyrYUulYYH7ob81HF395s/LmnuivtlRs3egVcGfTHt5e/0z0W+8me62y8/DvpKSHj56xnuf04rPvRp+u2DuXOeW6cHwxctAdHAkjmr'
        b'YjvrFz+3yiHn63UlJsetZ9YdX73gj3C7596PmfDVnRsl13Z/KfP4vNq99sG2wHWm8c+YrjN96Vvb1Vuee77xwDfulzZ8UvepIr9TevXjocKPhvtmXzz77t5FK9fmZ7z0'
        b'7JYhd+sjh1i/22I12WjevVfekL5/6ctMY9uX/0gduivpXRPF3udzDN/d/FLnjXt1hthI6hr909tZhd+7GnQVD8gJ+qrpS/NPHtxYMvJFyyUVr9QoC7/fUu3y7nX8+1cu'
        b'3hU5hfYtCw56TCsqf+C37vcHH9jebB0nKfub693KjaK7y3/b/OJE/fDmQV9Y3/W6m3LLYF2hj0d74Rah1uDZnKddXot+e9vfbo0d9V4uOr3u7fZbw72WfPPs5zfeMPhw'
        b'Yanh1A1f3s24/LdxhZPvrrslj+ZfMFxaULt5veR3q72zIl8+t8YbTpxbfz05I7tyY/Z3S/2X+Pw5rv3Oi5OmDvnsnVntlmH1Vw/eMd5/3cb11VcuvzO3Mfy7q/7XxP8j'
        b'8nX98aXtG4d/PsXs2w8/nvqz8YMfVq+wtHT+88vWC9W3Qt4cELPkV9P/+XryeKcQ+Spq9IoEa22yFNS0QMWXQrlSFpqytLZTcGqYJiOQkxouJAarnT411pfBZTjhiI7C'
        b'US3zjhl3dhnU9lsK13xD8H5n5aS5auomWo4aoIoazQrUOZkan3inOKBFJynyR+3oEg34gGNJJAtQO97DgDAraxFTbofttLTZUGSOin3RPhVJZjdBJtbt8qiJHUJgcB0p'
        b'riEUpamhDeHCdGbDH0S1sQpCZXEGFapUW54zhmuiGdC+MmscuWUv5G9SuOD6nTPD5WRfb6GhNssFKBRx4+G0JArb0yeodekavoHBzU1W4mIkywSH6RtY/EyFFVbd8nJC'
        b'Qh2wwb6En0T8mrR9Qeg0bMVD4hqEGkZACWnfLmEMKgxmDoJiDh0hAHAM/m0YbCMIcAvgCLXQDYKGy6DAmWRxh4g4fXTFFlqFCJSLcunLrUf1UEduCEDn6D3QgncWY1SA'
        b'9YCpI6mLQYF2bCGoNxOgUwNQ2w7ttO60CVDIincOIoC5rajKUJhvhYqYB+Us6pikcAhCV9BBKFtD80t3hetzZqhZlDVGxcsJp9H+lJBgpyAf2EGYOfXgiiCCHZsZQelh'
        b'tMMa743l0BICFyJkqBGb8QbQIaBj60NoC8ZYWY1WKFzkUGSAx0aPM4QyEg7XNY8+nz0WVdP25aMuAzk0004wRpdFA1HXRlZ9PTYIThL/ijMcZC4WHrY7x9LAo8FxWPHB'
        b'Q+m4KNJFbmjvQBwZ5tYi2GoMBbR3TbFaUCVzCYF2ORTjDjCHehNhEW5uNYsHugxdUQov83CeKQYn0VbGb4X2JS2GliAoc0aHSLc7khfQ4wZYiVDNRihheaCHIRe6QsKd'
        b'tDhG4XIGNwTlitHxwXCZjQDsX6JwCRqNatE5I3wbx5lIRNPhtBkd3pXowjRZsHNoBmoKxLNTIefR0cHc4GjxbFxvG21jwlo8wk2oS07aeJWwrBe705L1tqCyEHmYLVQw'
        b'gGs9vAarRFMm6rGgrcrB6DRu9lx0uCdiozNqz2LA4BW2iiAHdE1PjtUlVMWjUn8oY1m4tVNQG7SgAmMo1uN4Ge6nRfNof86Bq8Pt4EBIL4fdSrSdwaXuhTYvynONSqI1'
        b'UI7tcIp5EXPDVqND8SG9fFFoVwQVO/5Yx9zuBedk9rgnMkJxqwxhv4C6hqMLdJ6LvdARgj8Z5sxzBigv3F1A+9xQB50lPoFor8xF7oDHCrdYGq9MEVLgGm4V9eB1OMJF'
        b'Rzw+qEPuEsTglk1RqSjeeyZrdfEIOIVrzUBbUWs40dtO8FCXAhWMGxm1J8rkeGW0DFhOCteDfTy0rUYFbHFXYuW3iDjR/OAc86PxqHMoqlMJ4tHQTCZ/roS8rQgKeVQ/'
        b'E3bRAQiD0+vtp4YwZ7yEkwULcMJuEQtxI4jUhXh0IiBfnhlKEByMXUVSB8SehB1YFp+Alhw4EkpmxUW8kuePpJfGrp6GzYjMmHEk8k1AV/khWNxcpIV6YCP7BPGmYj3/'
        b'aHfcHBRtZiC5pQYLUeXGbj1+ENSwxuyJsglxcUZ5Bj2gY02wiLGmNujO6DToxI3FLXXlOcMZAmpcjYUpXSMlkDdfMWgBgVWlC5U4FogEs8CCF/aGTqWrLXqiWAFlckN0'
        b'1glLLizAL4TyaN8wbrCZ2EEPsWGAEstkXAK5iIrRUaJez+OhKEfJZPNe/Kd0HW4ec6cu5V3HD2W0wufN0AVyMpPthZdrCx6gAfzSRVDKwjJPoNL1cAwoBYiE49EhDnaZ'
        b'L2djd9gBW2SuVH7a4xUCh/DleaiWXrTBsrAAt9k+OMdB4PQH4klQKXhHG7JwyGNzPElka0T2HOJbKaT+VVNBlIj2cqxHt82DCmy4H3fUcBMTqHLU7k6FYuYyXwXdpbA4'
        b'ZSIR7XPmrNFpsfsIBa0eS/BcJtZTR1FD4wCesKgomE73AVPQWWiIZt0tJ32JF1IbnguD1rLVfcQ/MGoO2ZxJEOQ8HpeCR4tSJ283RicVcByacEcaQGEO6U9i5gyEShGq'
        b'c8SzmswUZyWqDnEOXgEX1ajn6atUUANX8IZAPLNwhARWcpKpgh2BwiXVElqTApnSGC+TDgPcnyN434HxTAqfHj0SDkK9AkrIAYEFP2qCFZWO6PIm/D15Dzxly1yCMugN'
        b'xtAoGgP5Xqq1bR6vofLAAn6zGwWFR/vhGN350XG8kg5RoDBXKApzkgeFYXFN/DNQ6IUllNcUCTrqF8OGZXsWtFOP9Eaopk5p5pK2nU25mcM8oilCcm9UdvsemLMxcFbq'
        b'ajmIaSbkKFNGsO3PJ2LVIwMvEYL+2yrCm3ruXAb51oTKTQhrdshSLd5sURiUjGBtKrXG5moNasIzQrW+AgR0ahg6Siew74Yt+ALqgN1UiO/hif8J7WYrpg5vfm348noo'
        b'VwuRCSKDKBuGm1uOTi12VL+DNRT1Ac71XE8XZ2II5JN3gJN4WuCXwO0gL9EuQg1Y3DO6dKgYKVbPZYJov22NFqg9bv0+FpnbgXaZyuydnd0dCLBJB4/320OoksngXajO'
        b'XAZFakVIGmnECXO9sagkTw5BrdCA5Tv+52wwj59txWvReTbt5GUidFGB8hJxuwyDw8hswY9boDwRFEzHWgBxOujFLJRh0Vct5zjehkjPU+NZ5x+ERkdFOJxf7OqKtQe6'
        b'I5mtFKGiTDvW4E7UFQMtTi7+cNyFiIAavJ0N2cLEZXsCurLcSUYg5wQ5PwyL7KtMqaoMhH0KLNUJM4X6fSxQHWcNu8U+oaZUTC/Zgs7LnF3kY2A7fh/JMGEg2oMFHR3x'
        b'c3iOXaKUOOHODnhKT5xHVu+epUtZRx0dPlbh6gDNgXgY9LEAK0SXhUA4toUJrW3QMRFanMOhYzPaQ0TDJh6qJaNpT42kbDvF+tP7AiAPhVw2Z66gNnTZ3VrhEqyUYwmA'
        b'9TVBQFVLLahg84SOGUxzhn3JTkGm9kSwGcMlkXeWoRoufR9heScxJjbh6uBrqLGhw6BwGA9V4SEuYVhAr+OnoAt49pCuHIQ6Z/OwtTsq2xrqaP9PWuasBi7hpCgvlSKX'
        b'yJbLB/xnIG0lj7iuwqOg6bOSTOrKpwc+C3WgG6v/SB2kFP+X4BgTIEAxBQQUYyFHjmQkFNGYRIKzgxxyTYrvIn8s8D1mvPCAIBcLD6yltrzwo5GpGUX3EP4Ui8nhzmh+'
        b'tGCDn8TX7uPvjAmlOnlC+F0sEeOrEmHsA2GrCS/8ITwwkw4j5f0peclwsplAaNgJ1jFBPDbjrfEdthIz3oIgi4hsSX0i4VdzAzP6O/nW2tiaYDXz9vgz/k6v/9qFB7Z6'
        b'1jwpl6KVULRmC9wiqUT41cRA8rNUJvzT8BnhnmGUIUVFJrjIRrwd/jmWJ3XjtvxJ2iv8IflNaiHl1w/WcZDDel+LQPARY6eVmfwaHi1bCR42J/yb7vMkbpvVbR0nSv03'
        b'BFdPE+Of5knicXi4XIx/0DDyRqNewCWZqRzNvo6aGRgQFhBFoUpotjRDLlFo4EZIOzMJijE7k7P4XwEUmazppgNkUpNjt50cCXETC4JEYBjcvwv6/75PkpeFSSa81FRK'
        b'AUoE3uKBMJXBjliLTch9fwoigR/2gNsyzJCeH2HL0kKXj17gpmC1eaEEa2JdQX3S6g1V/yrMH447IkqUqj4baH02xJ9liUb0szH+bKL63lTrswqDpNZAgy9ikWiphS8i'
        b'0sIXsSrVNxhsYJM4VoMvMiTRVoMvQnBJuMThiXZPgC8yolRiYINLHKdBFzFO1kscmThKJ64IQTPpiStif9uUgvBQjmz/pPiUrPuufUBFtK7+C4giXixR3UMu3BbPjIgM'
        b'uC3y8/DLPEJmez35cYx/fGgPL5Zp6fFEeCCqh7yeHPNDXR1N7HQnmB+ZZ1kCDkHnyDxHMYYiA8IiogMo1sfoXjgbUf7+kUkZPdPJ3TLPkxd+nFvdNYAY6obct+6vVA1K'
        b'Rs82yw16lEHGIfMjbagNdedkfkze6A651F8d7plXyD3/OYCMx+S+1VPldZ6EA3BAgS5OUcH4EQw/dDyEnmDNhCqsOWRnoM6FBD2jgIPaSPeUj1N8eQXRX4OnHv3a9HTs'
        b'8/GBcS8nO8RHxBkmf8H9kDvYy5PzNhc3vTpWzlOFJBNVwAFHx6WaaB8etkOrZz+sn1fVESHEtupPQaBxIXaEzGC9da9F9pgwG+a4nxVuD9nMKNzG33VsaP1XeI0M6jsE'
        b'S4PYCv9rWBojJI+LpZFIW03AAkj8/r8TSEO9Lh4BpKFeV4+8w+uxgTR6LtX+gDT6W/EPQbbQuXp13/8EQBa9M7VYUkFcGskHIAlX/aQPaR7TBZPaB/yixzirAC/IrsFA'
        b'LPDO4dB/ps+jkCbULXkSrImU5P/CTPz/AzOhXnE6UBbIf48D9tBz0T4m2IPOBfxfqIe/APVA/uubfKMXHk2D8pWEF1Y3yABUQGno3BwTxtHbfZ6BrhF31zErRYrrxeMi'
        b'BQme+/j3asI3/sWdFckLn751/c3r715/+/r711+//uH1zt0Hy0fsOL991KHG7fLiS08dzRuzo7HmfKH7jhH7tnmKDtdxW6OMhx70kusx1+t+95mqoNlwOEhRAKZEUdcr'
        b'nBwMR7tBAOCCGgiAogCgBnSGuTub5jqoA4O953QfvAZBOcMsrY9YRP0oqxdQT0oAOs48qfmoHO3oS3QXDK1SiYc66vPfkvuumxhBKwd+FgtRJcGr4gc6dJAnTnC3fhwF'
        b'aNj7j6UAPUmW+wo5H56JeLVCpiPD3Q+3jGW496lJk94+sp9trk9Ku+ThAbkJ+r2WhEy9LAjXb75+LyVNRtS0ZJlKSdOnSpoUK2n6VEmTUsVMf7M0SutzDgnNEn28SZeS'
        b'9vBEdW3L8f+LLPWeIF4qzUeVur0a7xUkh/a/iev/TVy3+2/i+n8T1x+duO7Ur36UincBbeqyJ8pjf4jI+N/MY/+PZl+LdCqA5uHU7bMkPo3mXqNdqFgF5+U9l6F5EYe8'
        b'K8oPYellUYFQGKGG4goMhlLKGjafQGDBFVuSYirmUAUqNkCdDuEU7wsOQSFqUuN9aVKqUT400bRqDspoEzKnQZ4qk7txE83khnaFkvhy4DDW9ho1h9daUFyCfrSGq34N'
        b'eRZVQp0BXE5AeUqiasgWD+7OFIWCQCeWvAEFhH2VRgItG4dOop1S30TYQQnFocYfVYb0Un5J1qsTlIU5oTaSHlHGcZEyfShFbStZ2u5ZaEJ5jNIVFxozZ77zvPkkgTc4'
        b'LBQ1RgeipsAwl7FwwDkoDBflKqALMg9UHBnFDUO1JqlwCU7RTIP0JFTM2DM2wLl0DnXErFR64O+DHeB0z8JRvs98kpO6xiOTJKLS1HAxF4uK9VE17IFcJUkKWhuTHUUa'
        b'Qm5UDVc0e0Dz8ouS0eER+ugYupzA4r+PoYYlssyFcMUE96VoAD8Vq9rt1GloY08itqEjEYpyFCSP5BrvCAdUiSRDn9LjaucM4rgZsaHe7pO5lD8PmOspnsVXQheciNk1'
        b'1Tx3htGOyiV7lu14BclurRfWr1rV+bJXS+Qdl0jfUWGX9d5/827gzMrLn25w9fy4atTOBb/m+kanBWyZ+VzAgIqFb4nPDLqSO/2XASHlXw6eHviaVHRRNtvq+SltXdJC'
        b'Udzqm3mj7p9OrWge/NqzZ01i0sZOtMr54ETVn+9WvPDBgZdrvH4YmFqYe6f0rPGLEyomz3G5NGvjMx9+/l6pwzuGU+9+8dqVL255O4x75viQk/f3X038dOO8kGcWXr3p'
        b'9VnezZNvf2ry7if6xmYBtlcOys1YWFZV6sqevNCecFiUOhgKWBBDFdoRoEYWQxcWdud2Qh3aT2m30daF81ly58zgbN43DnXS4+IZqGE947gO14Nd3cmXsBe10KLXoe1o'
        b'Wx+jRIL2iaWo3IEZPI2oPVQ1TZzRPg2tMDptlkVSd2aFz1OdGzvHY3tnnD07h24WjWArJCStO0oNmv1Z+mT9UlStiaKFTrRTUz0Lo4Vq6GRmUznKxe2l70AWaiGuyAS6'
        b'MtNEofNRPT3J98QGI56pzlCTpmE2jhqhCkqahRedRzCe+nYD4RyJfzg2nPqRQwxiHFGjFB3RciMfRiUscK8AuqDBMTiMDQlu/MAtUDtOBAeGOrM4OChC7cSKRLsmqrHk'
        b'DFAhi7s9PF/aK/fyIF7DjNePZV9Cs3dfajnZvzH/MfQRBqDhGpIFSYh8SSajREKOiC3o4bcJPYw2oX/xHapsxvXDe9tOOpMWDR4nabE7X1Gv/3N+/f6pbXXkJgY8jvVp'
        b'd06H9fmo9/oPpycueWR6oi6z7S/lJpJTi765iaPCKSKmAzqSSrMSUS1qeOLMRDgzmeFvtihlariBVNjh6YaaufiZU0UybiTJ6cmDi550M9gkhiOKCdCmlZuITqXQrXpi'
        b'JN4IK/FWXqbJOAyaRneClAEC96ohySaLNfp9ixPHEDiL4WoUSSlEZ9FFTU7hZGijOXsLoQb2M/oqvI3uxbrGrgksgWgbqoM2BXFs4C13ASpDhVgnaGTXdsN+VOwod4Dq'
        b'lerMwrHoCEvcKoq0DkH7goi4VGUWWjLkF3QQnRoVpU4qtNfH2s4+xhdlj8pHk6zCQdDanVWY60uf4hdDLlZfFsMBVQYgFnb1ShJ/aGQPZTTNj6T4HYJrWml+DsG0P14w'
        b'3sVFR04ROLfY8PdDUlmCW8bAUdzdtQWkk+Ll3hPYlx2TgriCZXY8FxtraDE851/L8lvxeIlhncTrQhPDAqk89Z6l4ihxwkI1IygMipxAzYgEFRlwDrUQCBMS1idH7SIP'
        b'rMWEoApoUchwh82EAtNodALK6et4TDPifk/B6suc2FQb04nsHYs3DuKkhosJY5vtd7ZrWWZfyCxU1DO1z8dNydPMvlB0iU6RLFNvmru3H5pUuXujt7D8QT0Jx/kNoxRw'
        b'n9jYcHKealJT0dZNClQxTxOhG277v9GdIqm6O+k0vOiaRrLs4FSAKs1OX8XlhvAmuFOmzrHbia6imgGoiM7DcaiVBJSbohNaiXbTRrLk1gJonEl8VXNRA16Oc1EzOkp1'
        b's01mUK5OtIOLszhpsLAQ1cMlhi3kHYw17koLkmynSbWTJaV8PqpST7EVt2H/vEPK6OfSLHzN/vFNTdiHGU9v/f62pLLkhX22oe0veM8eOGTIs3fcVyVkfPHx0ytKc61N'
        b'Al8yPTx4dHig7T3ZZq5w4LiztgMC7b4/td7qXTuTCUu+jXkr6+Q7Qy/NbR/53A+f+L1UtNGp/oxrwrGYkTPL75tsTEl89ZVbr7k0v17zamHDrNVfzDIc0DGyTjbqpSEj'
        b'F+197ZL/V6FBdqMSPOKyG6wLvWQvjRkZV3Y0buKLPxefsrE2VYwd9PnAAZ+VJvwwJOALbtBW2bMT9GLfSfzE5803tkyp/PHrgQbnfD9fl3rjTFjSskGz8pVLcn9aP3It'
        b't3m/y/6NxYE1s2P3ty03vPF0nckB/kDj95OSF0o/XtYS+X5RTXDKT6u+W32v6OLUmyv/D2/fARfVsf1/791CWXoTC1VFlgVEQSxYURRYioq90UFUiixgV6pIlaYiUqRK'
        b'R6oUxWTGFFM0PZFoEpOYGF+aJlFTjP8puwtY8pL33v+XfEBm9065M2dmTvueU918SXBn4Sff7s6Ncv/XnEBZ/rSrFRXupmP4C16wc7J8+EKvqPrImPX+ohsPVx3bWmb5'
        b'8NKmmUt1p/bM/9z70Of+L0wNPCh+GHFc5dwbVxbPXvfdg/Cg5XfC5j3yKP/11qPbbgUeBtPXvrAGrNlZk/6Bl0vza6fZb7ed3f7Ciq82fDRnYlPHdUH0vB0pLW87/uzl'
        b'Iku+vdWsc3z+ufc/WxD62vWQ2bkPuOjWm/kT3jLakBJ1U78r/IOm8Lu9Mzbf6Nlg9GHk1x9pfeTzccuS2m7Tn1eFx76VP2GWkdHEDw0ebTZs2JhuuOZe3luhhnsDH7n7'
        b'ZL018Y2hppnxzfU3zs5ft8By3+7jF368H/j+1D0HMu+bna88+NPWeMfVvPp7D6rvJB7Ku7g97htB2acWHwV+pHt22aPgP3f++TjDoKy0ptiv5mP+Oc32d4u/ntjrWGMJ'
        b'rls0vqh29MBXWxoSo95d/73vOPHjqk6z37dt/fTTep4zMHnoYVJ/83HcZ5vmfLpipd1RkcPVyU0bd994Iz5/2VD31o4E3XZZXOGy39CfB3WvSdW/etVfvUe2QTDxB8vt'
        b'vTlOb+RfHjff/12HZXu/Nf3oYuJrakvs/7z2ZppTglr+KwFT/X5QPfO7qcOW1cc+fXGAG1AfEA5cmbrY5cO9u9VcYnJtdgvuHy4v++ToqZeD096beM9o3fh36hob336w'
        b'8Fz26m3T8vXK+hbEXdRu++j0FXNn/oDmo+s3DR/m+7WHL5x6vHDQ9+c1fQ0L/ria9U5K5/baTl6/i0Wjz1uBV1N/fC+74C1ZzPhVv575/tLQwW/6uv9c/LFP3wvXHjRe'
        b'qV87sP2SSu047aMJ3731iU3mD6b95m6pu84nXzjpNbfgiF/Vj1/OtFx4yz/+kTg6jlzLF2GumQiemD8CtDaS1T4Ii6gQUhgUpESsLQMX5Bmme2EvdalPRTu/Vx6QZNy+'
        b'EZi1QH3ywEpQMB9j1sT2SBw/OwK1tgSx1fg8No3EbuAKjJkvbBiGmZ2URw6eY7lHAvOdCM5MATIDDYE0J/V5mAUHZPI8V1nSkSCzIniUMN97pSJDeznKTOyJbhobkpsz'
        b'yxaDzFxAqhDdM6XbidSwXNVQCtomK4xOGGWmDZOoU3I+bIAFEthHAGXDaLIUxOITHuHYFCcFmmwRaEUT1cTtcbUms7AdpoCKYTgZbLNjVDCcDPaiWcCvIUGn63HFA7Dj'
        b'4Eg4GTxBM+2BctjjhgFl4ASoUyDK5u6n/sEtTrBXCSg7BDPRxcetXYyGhhmHBSrwlMzG4wko2cY5vDiYPZ0O/hQL+6R7DUlGbjmWbD5IpFiyFpinTnFk+8DASCjZenCB'
        b'TE0wGuRxgiVbaTESTWaLpo6Iqj3WoAOPTk2sipivUWgy1Al+AWPE0PQpAWGwQcioanEbYeUWsizoKm50lCnQYOmgENQbwWTi4u4K05EsiCFho/BgoGIKDxHQYTlYCFaB'
        b'rgQKVqtQinagEeSQ5pch3rJfpLPWx05DjF4eVLOwdesY6jVeYgHrCWgELTnoR4zwMGwE1sBBikqrMbAfiTezwCEmKNwMkccAmSMtRL3tMnsP0KYBKmKVgDOQDeqIoXEH'
        b'qIQDIniOxagzzGXDDDEBnjGmfD5oB8ecKWym2NhNKvYGOb7L9g1jy1ZpkD4sHSwxEEsCz4BTI6Flq8AJWjlRBnpkPmIhSFXCEkA7pAIzOGGHJOxOObJsBzgGzoM+GuQc'
        b'DiyAZ4jcDkpAzQh8mWg5xT0l7QRHCLxsh0SBLrMIoHqCPphrTZFlMFF1BLisjcIQp6htIbiy5bB8BLRsL6ghAw6BDaBCji2DZ+BpRg2Dy+ztqDKhCTHw6Up02V6OUcXo'
        b'slZLKq6nIXYMg8vsPXYZj8CWgQ6YSkh+AWJrCkQJAdb2O5XYMnB2ghy9soYnCgbFBF42DC6DHfAknchkJBN1YXTZNtCnRJdttyfjigZpoBLtBmd4YRhchqgtmVSdBlJg'
        b'BwaXwaYR+DKV+eS03RQF6wmgBAkjR5XIEFgJW+kJUAQaeORkwNgyeH4lknAG5K+j4Ydkqc642HgktCggZrMgRZxMsYcFWJ86G/YO48tAklxTgta5EubKSBAtRaiIch0y'
        b'D5pI2jhOdFAOO0ZAzMA5dGzhhmPWgkw8XpBnNIyBAf3wNCFpTZC1WDaMMBvjOQpjhggilzw2Fp4FBU/gzCYTJBnGmcFGcJTiL04KQSviLY8dlCPRKNAMpo+hSp1scDxA'
        b'utNLiTMDF8A58n6IdufLxPMx1EyBM4MlruSrVfC8iQyc9hyBMgPtSyj+F7HGKQRnBjrBMNAM9s8gyxgGM9wUODOYCc4zKhhoNmsnOQ88YHUCnhZ1tGOw/rN7E6xG4zWG'
        b'Z/kSdI+QrlUCdZVMdIqxnIkOpUHZBv3WSPfsVcIu1oESGs6tV0cmIk3CdNiEmsWUqQ4KONC8bjU95pLQulYh8QiWymEzSBy1hBWzKNWmzvXCaCBwQWcY3BYHiuhF2mQO'
        b'z8sW2dMLUk2BcGNMXPggf/s8sqeiQSksFqGzpZDcNMMIt2LYRSbNE5E1XWu1kQA3mDmPAEoScGydLFdtJcINdHmRC0JXZC9TQttgxcGR6DbTbaSu+hSQJrXzhId9FOC2'
        b'oP2ERje4TqF9euzwHwFEw7gi8n3AXFg9jERbCosYVQJFswLNcWJywoN6WIBYkCrQ8DQaTQFFi0c0LQdWJ8EUmXKWGEYHJu/dyosDBeA8BevVw2J0H3ZipkcNZoo9yJVe'
        b'ZYXmcixI4i/bTA/G8E0gmz5ESKAJJiKWoJRbtBk00o4qplpi/Bk+dHNg3ggE2jl0OJIn8nfjdAtYBQvLYJnHsA62HLVBzuUTc/DRiGYtXVOhA13hTY/0PFiyS4b69kUU'
        b'dVSCTl6dPeDiLt5+v7GUsTsHi6ZJEAkizsybhcmgC03bSW4fYvjqyZJNA1VRMhwRNAMzkJitYRldw5WgjHfgEDgbN41KkO0hz4TmUUwbzMdhr5TgvC36ZGSbXMYQWNsI'
        b'SJtnAg9dvM1SQsXjJ6H597ARe4GmYVwrrPekOKsLiEnLR1/7wDolfBqJovSdE+FpE4KHRYdFjRK9iziSLsIThzGrFcA726XeT+Hu4DFYT+ZGNgVmKYaogA6uQC8OqvfN'
        b'IkwDrAdF2yQH145A3g3D7sbK034I0JXZLLK2mzJZibqz2UZ28XrExA5D7ibjqWe4FQmIkcAHvTMsX4UuPTOYqETc4fwudBOn7raTUcAdOAzTRoHuJsI0eokchWUgT0Qx'
        b'dyAdB7hCnPIgPWGSYQUcxMi7Ebg7cGY/D2ROnUkZxfOzsMbA1t4Wliuhd6uiqZNTzXh0o8K8AwrsXdgmCjY+gd5mNPJuMw+NiwDv0OzTYxrUSUCKCOSL7dAZRLF38Nx2'
        b'unDnLdBlr0DegcK9iBYx9A5mmtFjr9TQSYG9A22ITVDB2DshKCM0YbeOj66NItCN0XcK6B3IDCMzNmsDOIv2EAHe4ZTfI8F3sM6QnpvZC5Zj4F3orhHQu0ngFJky+31o'
        b'E9KoFR6wWDACe7ce0AMIlqAZO0/BdzD5kAJ9h+6nYvrigyARNkphaYgCgYco7STdhf3g1HgF1A4d+oXyLOFozP1irf97eB0BPxFjwpq/wNbJEXZjKcJOh+XznoetU30C'
        b'W8cnRgZ1jFz7Q0fIJ/XNWXPOGP077m9g6VRV+HJ0m4Yc4cb9iZFv3GPhR+rOT6LruD/1+DoEBccnPWNjB27FWNUIGwM4W9ouaoEv/C9xde9xD9WXjMTVGT8fV2f0pPnh'
        b'vwTVHcGGEGzZ/StDCJNk9K9nmEKeMxY0AgxCiL2lwNXxMK7uHVauoxTr/9/h4d5Dnd7EsMEo5n+FhxN+xEm0WFXBCOzblGHsG/3M+LHpImrfOCWBLVqg+ylVNstYg4uC'
        b'SJil9ZRjrJb8X1nyU6i3DfwilSK1Iv0wDv8u0pL/bSD/V53+G8EL44XwcrgQG6W1Cae90UjXTNdK1yHZqzUweo6gzAShwhBhiEoqg7N353AbVFBZnZRFpKyKyhqkrEnK'
        b'aqisRcrapKyOyjqkrEvKIlTWI2V9UtZAZQNSNiRlTVQ2IuUxpKyFysakPJaUtVF5HCmPJ2UdVJ5AyiakrIvKpqRsRsp6qGxOyhakrI/KlqQ8kZQN0gVhrBw7Z0j+xpnA'
        b'VTcYEa9KHrHEqaaL0Nxoo7nRJXNjHSJGT4wJoTEKJUMaixd5r1Kkur/Zwz3hSYldmUY+QWF2SkecuGic80FGn5kx3Zb+60gyJOC/nEY1prDYyezNF43wEZS7vBGwgNyx'
        b'Dn0bFxpLEjhEJ+DEtHGjffxGJnOwNQ8NDN5qHhsaExsqC40a0cQIJ0TswTqqhed5+Yy2G44q+ERj5y6PMHOSkVVmvis0NtRcFh8UGUHclSKiRmAwiP8U+joQ/cRtjQ0d'
        b'3XlkaNzW6BDilo7GHL0jIZRYOOPxCbNjD/bDGpWtwtwtgrg0WS8Sy/1yd4x29ML+UHJXQboQU+XroJhxW3NrV7HisUBzWSh2WYsL/atFwmtovViMgRuBI9wC5Q550bER'
        b'4RFRgTswgkCOPEZTgNERT7yoTBYYTrAjoTQrB3qKvr15SGgMOlJl5tF04MS3z1r+nSumsMho2WgXr+DoyEjsf0xo7wk/Qh8xN8TbHbljSBgcGBk3wymYN+LYEciPHmKH'
        b'wqHt5agwlXRF3iwROUJYdIhwYVpy0zXviDCFOcDfq7afR0zXfGKu5h3k+434W54r6zf2b+DERm2k53uTPc/BEL0d9S1c5+0ld44jKVJIu8PrhlaIOJCibflsr1PrUEpO'
        b'z9uzf4FfIlM7B8NQggPRrg9AQwqgTn60MWUjI0nvOYlrAkNCIqhLqLzfUaSHiXRnfKh8+8ri0b5SHh/Pxm2Mcpyl+Wjw7guMj4uODIyLCCbEGhkaGz4i28xzECCxaFfG'
        b'REeF4Bmme/qvs8eMuuc05QQ32rXAxEeGmeZfxgR2vv1AIm78XRwnvizuyRJ/0JEkYyIOqNZ+WvITrh6PowCsB+c1QSfMh+ew4hD2JsQhEUIMekCWGB4HHYBWAbVI4G4j'
        b'TOoqYo9dArsQ49yEercH5QeZgwGwnZhvhVuQDBznhdihAK96/fUMTdvSB4sTQCc68RfCDBfGBR6N3/Hw8ePH6yL4jOqkGgF2Mtu/ZA8TT3RQ9aAMFpD4yrDIEbbsd+AY'
        b'wWx2+SFDMRePEZmasBWUyGCmFszYZR++n5gckKCpZmPNMtNhkVACS+Npt6XLtolsrEEvOMUynDc700IfNUEQJ7VjDsA2mKZoBbehjn+xjOUcgSWsXEqH0giqYRuS3/JE'
        b'9Ese7GdBA0gZg9rBk4eEjTaVkY3EetggiRq2Szyk2Fkjz5rHrIHFqhNg/k6F30QdHISd9HtrfR6jOoOLcoQ1Yl48FkbCYds+nJrDDqTCMzDf0WEGx2gc4LbDQZATTwSd'
        b'YtgET9BH6v3JE0JG4yC3I3obMb0jCa4SdJLv4XFYSx5gGY1DXCTsAI3xEvzIADwMc2jyD3cWpK9yx0+vcB8Ojs0yS7RVxsBWfZJBB9b6g1yZ17a5WLhcYQd7iMCrD3J5'
        b'oAIcmRSPARqgOxJUjAyvrUidAjO8pFI7b1DN7ZwHyibACyDTEHbADqkByJSK1HFAK8+VfkxomM7M+eaEghL3CxjVGE0hIgrbbB8vJn4T+pAPcsHZZ7SP3Tineq62hhnu'
        b'MNsPO05KV8OzmJIJGRP3GV8Pgd5kdZgGagUC2OfmBSsmgwYx47bLAAnpbTARTT3WFUhhi8/MWbBTOyYWUQvsZa20wRkavLoPkXoqEg07RKoYfoNEGZtF4Bw1/J9xXWgN'
        b'zsNOjZ2kWjM7CSaOJV9JkJyfLlgmiyEqX54GGwAbQAOx+5uDgu0he2Q7YYcGrpTITooaL49RrLYSto7dJIM9pD1wnjUKUsTkroh2QC0cHtVXrwshi0lYqUpX/dimkYte'
        b'vi8eR9mArfAUbFAmfYHpW1fAI952nr6ryeKTGvI5RYJyJwMrdohAPTg1j3rQVs0Cp0dmjCE1l9utoTWwo2IOLGBCYK8qA5M3RHArP+BkWEp5v8MissAlWn+Rziu7fvjg'
        b'wf1b312yWKiqzUv6jB9jmpDIZRQkH9dRy0nuON78kH0/Cq5odlm7yvyGocGR5KvMjHnJvgvHZhwuuPbLSxYLd+5zfPzr1SvRD3xmN9Z/e+mOweo8vdMBDUFhD7LsPvzS'
        b'+Wxg6/J01yAPyyPquxrMr3tGxkxXjzoZ8GXglyficxryOrvyTF7Syvu6pjNy1Zjk7KX9ny9U1TWwOBgstdl6J/TL+dfW793hIR0CL88sTCufeiTA/Vx0Py8wtGtgou2F'
        b'n1Z46+lHOKcXrKl8dHoMWOfqv+1l935wy800+JXiGCeJ2cxrS8q97z1ceOtuUYOXxGxf2O7S5W94Gl+t+vq7t3hfVC23vP3+lb7zbdn7Pv3xSvXXX5j92rD/CnB3efPq'
        b'j523f9vvut6pVTYxMqNi5mtp+bFvf3nihZe6LSecr53xjZqvb/7gj29+afbwypR7aXU3Zn+7+bCaTMX0YrJJu0aRhDs4o9LhWghvqPJ28Tu5930NpwPJumXRrh9muCVI'
        b'vvsBvLjn9d1jFudu/2PO0V/MEu9krjhQ/Ylxw/vX+zJ/6gmxdh18OfrexnUVBxfFWFonD0Wa/ssw7LVLce87bFzm2xBR+XVlYEPSxQbxtt0lx9jv5r+0x+LTz07NNX0r'
        b'ZYrVJ7Pq3vY/sPDj108/btoQLd0z+8Y2V/3ftN9srvz1R/+S39RKPjxcV/7ue/l1mU4/+L51/vesupJ34zS8D/i3adZG/zHmfvQZ9o1Qg07fCy7LP3jQNuElg/tV993a'
        b'f45a+luz4bj3/d4ur5XcaMucV32gzrg8bMXSzEzryul6b9/NvbH4+s4tV9+6U77a8qvfl9U7Le/78AW/cxfZPUt+/uLib5qReaqnJlmKFxHFHx9e4EnsvWEzOMWhXVTP'
        b'SmGJNQUbpqFtWQey0M4/gl3dfUEmPA8zOUYEzqMtNQtcIG69fKNJEg8vNT0VVPsIOw8k+lB7WC2oBn0SuZl8gSk1lM+Vm6xmroCdIGsqiZCAbtR2RhjAWVqDbPKlFjrr'
        b'sCE9Y6qvHQdOCRnhQc5GH1SQ+Gqo1d51qCo2rXrZgwxfYiQGR6a629oQ9KZlnArjj+7hFluQQp0GekDKFGL1n6s/MlKtcCZReE2cqEO0ZTl2wgUwH13L3ESYak5q+qIb'
        b'JEPqa+dhK4YVlmL85l0cPG8Nu+SqtEW6Env9yCcD5M6GfUQp7YIupjqRFOYhruEJRKXqtk1UQ1zhDLrkykJ40YujukIfHtFuRoBGLRqly4vV16CaQpipQ7WAKejmPwYy'
        b'd0s8QAu6zvnhLLqrmp2JxtccXCT4zxERvKQWLDMOlvJ3ggHYTzWvx0AvPAs7vfbDdEV4yH2QWg1Qj4tBHmhE8+zpje0cOVIfuS5yEjwmcNklJP1oLodNMpjjgddCquVj'
        b'B7ukIBvWcYzpUj6o9Y0mKsk4i1XYIH5UDXTATvIMx2i6cbAPXRQtRCO75CAOVzrVx87WW9kRyItiGfNpfHQxD1JDZgCOYUYjji08qFR8wnRbecCzzaAKZPnae86GF71t'
        b'PbxZRmsrb9ZkPxqS7CDizrw8xCAfk5U8eJzmDJ4KOKZLljLWH6YS20C2FGapIM7jNCNU4zQQD0GDGYKzGxejcaHLHevpedvZ/U58ecpupwRQhI0ncbFKS+fGQ5Q+umE9'
        b'HABVFsRwN2y0OwZpQGDQauVNAizizEXa0xgBLGFhvy+oIxtzBujZc2i3yF5KFNuNLKhANxbxTLcGieCIDGbhSPzPDJgJy0E3aWM8zDyAg1bC7r0Ki2IIdbGwA12rZHIj'
        b'pBNoIHbIGLl7giWoFyCizcTu/Nh+yYOnWJC7Hp6mlFc4fqk91rpPhUcleGidLDgDi+ypQj4d7dxSbKWGdTHyoLAwaR6Zjn3gKKJYuXONYAnIRy/cz7Gop3Qa4A2WOOC4'
        b'og7wFLX7RoMmGjfwKJq0ZFhLF3gYgqAHWnl4FjiyxnNBPSwkCARsnToAOllGFZRwIGMPGCAGlbEJsFD0hIMRLNBSuvMPwnK6LA2wNRq0iRHvKaYm824WtIJWGt0OMY3p'
        b'GMdDZICqIMI8CRmtEJ7bck1yQMGBPbAGZO1KgF2aO4f5MAzTngpz3b3txPD0GCHj56aqtWM3OYGipsGTMok64ozFC+ezjMoBzglW29PzoX8sbJFJYrGqH/V3RsCohHLT'
        b'xVHU0aMnFgeF9Nvrga1DviQrn4AxhI18XXTiUGcYxINWTRXhpnELRyJQA6CRm4dO0Xaq0y+FHfaoEQ9bmDMGtYIIVYXR8uEtBD3+FIxe4A3qZYhC4RltHBTnHKvjLCEG'
        b'FsP920VieGa5IlxiGugkTdqBxu2rQPUTdhseyJyIFoI0WQeadWU+hgeU8ZQvwGRyl1jNcMLhPQ2n0QCfy8B5Gp6zAfbCBrRv0Lz6oqF4oG1Kjomp7jCHx0yEdYKZsNyC'
        b'vlDTWJC0NkTmI5Z7VklZRseEtwJngydYkIDI5TJxqJ0iTvImalXBMC0B4tIHZdSqwgNp7F5ddNCTL7MjQZbE007KhdvZ+KCjRTucFwh6zMjgjNE2rBw1Ll83dG/kouvL'
        b'R8CItwjAKdAHU+KIQHEWlmk/mzZ8nWeA0s0s4wJahT6gbSbtuHLKatjhKRkZSQg0oVkhbzq4FnSuXinCXyruFl3YzwMt4lBqiErZCw5LiN3Ybh04LGRU4QAH8t2i5WFT'
        b'ndbDLO8Ny54K84iIPUOs+d+bcv5HJqFnhQ8A6NdfG3yYQ+qhOqwWp84K2QmsBjWxcESh/khHoEqMH0JWnRhKuN9VVfDfWuw49DOBncRasXryzFmqrDExCukQU4oR+swI'
        b'/a/F6eHf6H9V1hQbWn4Tqho94zMh6kOLhG3ELQjl+BUcspH/C19lr+FI7dPomAZiAUWQfIvNGN+NRqVo/FfLwqPNDbeunFoPVXkYrr+2zTBJVg3PsM48+2X+RzESWrB7'
        b'OYmRMLobZYCEaQqtOFEr25qHhtub22DdmL3DDEdFAJen4yX8reGl4uHt/avhnVUM77fxeBxyFat5RMioHv9WZ2GoswZ2SNU/mOren9tnp7JPCwJuJojeMHNSDUP0/3HP'
        b'4ahnMTuk6a/ULPtHPL/7HmX3VovM46MidsaHPgPJ/0/HkErHoOGv0DT+1RD6lEOwwTMgi0NTQHSVSjXlfzOMWMu/WvHzyr7t/aJx2KCosGgSDcE8MCg6Pm5UFKL/sH8c'
        b'Vea5/V8cTXEjouL8R+se6/5XnQFlZ+OGO3P1WPzP+yI7XfpXfb2k6CsWp+D9+y+Q+1eNvqp8AetVz4hlpIjQ8Z+SqzoJMuCPIf/PHcLroxeMxAmgm/Y/7VWV9hoX/dw+'
        b'ryj7HCuPKfEf9qg8GoICd2ADiX90TGjUc7t9W9ntLNwtfpZq7XeMNP09GYTkPzsq0ai0lKMK3hEtC33usN4bPSz88H81rP9F9Mqtz4peyTJPWip4PhFf1swTyDD77FT8'
        b'7r8CXg1SDftsB8sE56vWse923xOzlN3PdI5UykAsYhFhERWCpk15TvjJaQofGmww+HcsFXNIGL7X4Il7fkdolCIO07OCT+IOPsSMBY5w/O8YCyZJo+QZrMUzu/yfr0Xq'
        b'31sLvs+qiE979Xky/PG+xFJpoIZ4b9hnbzAMX8za8J2GSe/p2e5h6GzH5rJPsTL+/kHR0Tv+aipx7aF/MJUn/gaXRvscNZd4zLhnTFDUMjscsVMRIopaZ9l0TaVlljsi'
        b'QLPMQ7PMkVnmkZnlDvL8Rvz9LIrHgh8GzTqOmmVzH6L/d5q4QK78N7Qg6n/QEUwsYkZm/IQvWB0cdkEj12wphR2G+8E0mVasGurMhoNVrD2oh1XEVrIvXGCpxaOPxyTo'
        b'M0RbrzIfFhH1CUHt47hqJNxFthRmePngCBgrl6+0W8MxWxaqgMpJC4mHjRScBrVSLA9ngdyp+ycp9WMCxiZYAJoWwjQy8ChwZIrcoOEOCrFNY4sftUv1w3rQovQBNpzL'
        b'yl2AvRyIKc0LnAHHsHsh1kQxIHMh344FLbACFlDbRjWs40nENt4CBpwMI9hfeBScoFa4I7ALVGNBFYmD/SY+GBaERNXQeaaraJLIi7tAHhEI7TxcQT6fUVPhQO6ESWTu'
        b'DP1MaWAM0AMT+XwWVKyFRaTLFbaeGFMltgM9rJBRm82BWngG1NGoGdkJIBfDgLx5TPQcmlaqeA+pthEWaMIsOx+YDFKIcCnczBlGO8aTVFuHNcFxKcz1ICH3kuEJL5hF'
        b'ppyGIJDME8AcDrQ+RZYiBVm6D5PlaKJkldHK/mOCxO+l9hRB2vsQuitUFXBJlO687smklO6MffRlaEqKiYswRbKEqdD5KQKF82TWoIS45lIP4DHGNBRxxiZ3ulaKhYID'
        b'XqEONoR8VgtBhgw1pNQ3wjNyGHchbFsp8wI9k6eyDKfKmmDUBcXcDoAGkCSFmZs3ykEHsbCN9OQPcnCIloAVyhzpOKPPmU2kmiSShVl6/tS1mKZiqlotN8FG6Elh4pQn'
        b'MjG5mxPrNsmJa8a3xJeyBQPOGlqAs+CwWECq2ujjpDB1Wk9UnU9T/4JcNVgiBe3wgjKtOAv6g4LI/jAGF0IpUmYYJwOrPINgjQ2pvCwBJhIQDsyHp3CSJwzCmQEKiQX2'
        b'IDgHBySoS3u0Q+zFdp4gHVR4s4wlSBPMNjQlY7MMBEelIHXTqJRKoBNkkm89YCU4KfenZkExOM0IVbkxdrA4HoP3psIeWI3dssFxWD3CeXyEY7YYVpEQ9CAXnEBbCbvw'
        b'8929iGoZHykgk+wFq7WC7aBJiwSr8V0D09AWMn+OYzpt2wckqcC8+bCRkIe6CUyXzeWNMJgWBMVTpVC8m+JsOQhKJYrDBebAappZuR92ekvByY2KI+zJAww0gnqyf6ct'
        b'2QgxPIIeRPQUyoQdhGgmLhsrBfnGdp4K+AM6n+jIBDxsWT+6wE4Z5+RgNKWmDvR5PjkQ0ASgXV9NDoSd8eRbeBGWYAgJTpZGDhN6lJydTG3HpTPgcXRCYAVkyfZZDKrd'
        b'By6Qkdjb7JTAY/YkzTs/EJ2GIBOcIYSyCZ4CneiMcbez3QuKcYZDcJzbP46jpvoWqYlklEf85IMKn/jJsIw0YGQOmiRjQOmo9Es6MJFQAszdDfKl+2CZ/BB7xgG2FFaJ'
        b'OfruqTBvGciCHW4gN4GPXqKeQSTXDWma6E2wL04G24XYaLYBHmNAHn8FccvQXQRTYSH63BZDW8ttQf5Mcpndk6pbqTHWDKMTYHt321gaX+DWTt6W2Sz+K2DH2c3L6YdH'
        b'dgncUzlyWu24OjOefhjmpsm8wHPA4Qk0Ts8Nox9+N1V10wBrjmoH2C5af+DpEAyEScQ/+KZJwjEDVA6w+9kYlRBmDTpMd3IhSlGM8D7yvMpswhOs+JDa3PDQqNDdMbHz'
        b'Q9XkByyXaMTEb8C3JswDubLR6tEFGyQwnwY9tfWwQ8t7FIcGGhGLARbyMMpfTwoKHHWCnLHvwB7QYChwS2BA8QpDdMMPws74BXjRquxisWUeZxq3s/cgoaA8Vyy33Gi3'
        b'xv0Z6wg6OXUW5/9p1AiAxYgqMANgCQpM0LEttoOZwxYjZgKoBCWr+aAZpoHiiJxXTVjZZfTKJvdEoX4DUfqLDMpO/jI0sOWimYfzDw8Kw/VM0wxr3Zel5el4L3nxVYtg'
        b'ceyOpNS4MwsrPzr8qsl3rUsWp1g/VJ80P3HB6a9EvbLwzlk1Zx+Uyq4eeKPsxgNbG9P2/Fmm24xuBR13eHOi771yY6fat1znDM1+/ebFhV8xfpu+Tnx906uHpa9e+oyJ'
        b'Na9xuexaN+GYX9ShH0oKXqlo2hxTnWzzc/anrMXZ6at/euvklDNtmcW//7zAbrl9giTuoxz7G6c2v/XN+inbJq9e+uGpomPiO+FvZ15ZvGW1h13CR2rvCr7snpiw6X3T'
        b'3cV7xCm95WdfnGJ9SbN6UmnnT9ZBVhNDbkcFJWzpLpJId45/mx92IJ+t8ljiH/qWodrMGb99Ojkl2faQ0w2bMOF6waLCj8WHssUJ72xwbqiu63j3/Xc3hds+eFAcJBt/'
        b'O8hm1bvb6h6rvJ19/0Wzu4tM998qCb+kyfk7L/b9LcHCsi30yntVzes3p1aVOA4eNHk/YWtQZOabhXOy9ie/p7Yqa1vSXh+9LZPmuu3OuL7v1cWx6TX2hXsT95e8F7Fy'
        b'rXX04R9tbq4H21O/rv+9f+j09WBwyuDkmVePa/l4tQhCkobWuNwxGtw52frm+k/HzgvZnTJZpv+V1mXZ+Oj+5tfXG8zcZWh2V5ZT7vJlfUjuazNeCf3y41cFvi6O8Wsj'
        b'76Axz75YOegevulbh6xlQT/yv3jwY876vdvHfnP3QF9pzOasTfWbY/regVop/suzxk93ePTyLzd96y+vfuOat5dA+9q4jgs7w0xci8NfOdt9ZXXOL+VnB3ebXfx5796m'
        b'oNuLbnyy9YPXH2ppOnb/KY7Y9fEPDt8NnmrPybv8wqz0349vfsnSP+q1Fu1Zb+quqW65ueVKsrXZgryPEyQJ4zPgm85pUQsXz6uJzPxTBHb/qz/jtu78jW9dsm87nfa+'
        b'b6VaS+sLf5jMTTpSar/gpbJDX53YdC5p0e+3grcuCH/4aE7BvOA//3XxYfi0V4Kvi2cTg8Q6cAKWSmH9dHSxg3o+OaXPe4DD1B41GAraRBhkpmaNOGg7IT6nE3XBGR4o'
        b'BX06xCaxDCTOF9mIYQfMdgN9OIXXeG4NSIKN1Jp6GJ5Qk0NKs9yJSRo0y+FjE1XRFdC5YtoIO+s+cJwYlPz9YJ1km/MIS/gm2E66WwfSQDk6ADINR1pgp4FyCqxNQmfw'
        b'BXQLHob5I1kjcGIbBSB1gaNgkLzRTq+pYiGjiZ5Bj5+zgn0R1FDetFND9nTawm27iB0WcfLUtBm1brEMduyFpUpgZ7QGeWEVeHGFwgy7VG6GBV3TKYa0IgaWiKxBqzZm'
        b'kbhV7HwjkCO3Rq/SkmOjQfchbGPdo0XF/8PoAOoWTdz8RHJMUOtOutsini4D50GjvXgEFrh3FZ2MOnByj8xgtxdeHHT8SQWMugYHTsMCbTIcNgSkE0C7LSOewAhBM+do'
        b'vZaszP4EGQ01MHYsTl2LIw34o/knvhd9B2CRSAFcBk1COXbZaQ21b52fDBtEBPNsBbLksOdpoJZCbEtBBT6t08AFEigALQ9/Ngvahb6KLKInZRRv7UbBpxhwDWoEpPIB'
        b'0IKTFGZ6eMBzMfC0lGNUdnI2iBoGyAxqBq6geNclPjg/uye3YfYGalRrAD3uMtgIumC23U5q3FVfy4F+ULqeNCwJgq0i0BCDsZ2wzw6NuYSFbSANUqt9CDwLSmUwOwIc'
        b'lmcphOk+ZO6nGsI2EejS9/SWCJEg0M+CfJABy0mvbvGwEbsWqNlL7dUx92McgFaWPxNxs6cp8D8v3lGOWVNiYQ22T8OscSG6GiliEK1bHayRPZmVERwHeQS7ugL00Xds'
        b'QYJiqgLuCY+HoacI2hP2xpMFPajrrfA7WQsbqeOJVTgNnnB8HzyrjB2hjAvhvAye1wNlhJAWwfrFqPFU3SczS4Zx1Px7AZFagcgoLF5TnuFRDdAEfitVxmEUM3YR2TWb'
        b'EbixiGs9C09Qz4IzXrBHtEqTxCqgAEV4BBwjZuNlRjtJOAYcsRLbk2NpCkvQoDlWRA3QoN6XgI8TZlCyvMgPUWAaQf9mfAwx3ApQAWrkI4QF20WYuJSgxl0yug4nQRvs'
        b'lI3OIgjLvQmmEXQkkOFow4rpIs9YUCUHHnp7kONxCSjjP5nxjzFWZwnusNaX0KV4uqWIIA5h9wQKOhywpJuhygYWYP9ZTHqn4AB6XRUpZwEadtPZqQDdm2GnGWyztVcC'
        b'Icdskkfj2AXKFY5YsGa9PGRJhSld0DNrARYETs+z9UGHNuKxWEaEtjBsRWSSRftuMhDArOWTbDG7BY+QCI2tHKwOWUBmawqo34sEtiB4dipOvFXJLl+HGFp8fjqsBUkS'
        b'e1Dka4s2MNZoqDAiOMjBc+hoPEwxwYmIk2sQ2Wjpw1we9jx2QlJsBiEjC9gXRKdr2F9Ha60KYupbyVKwsAUg2oc5IE/poTbsnTYtSGz0/xv29YRd9b+PjjikjhE2/sS7'
        b'nbDbnxPe+N9rZZlD6gbYtMwnmEb8W4uzIsZtW9aGNSXGbj4xcGuwXCLRCeInqfn7Tz6Pe8TxOKH6T1baRqwVq8NpscaskMOGbpqT0EienXAcMYlroN96BDWozhljwzh6'
        b'0pjVUsXGdq3HE7hxPC05jtIcfcJ/jH8mcLhFDRLT34iVYzE5IYfGnL9X/KTlGM+Cv/1cYmeSzbcfnhUqWvCH1OJ2h4TGBUbskA2p+MftDgqUhY6wj/8HOQqQuIIOIyZW'
        b'lVMoW1XQXzwsoOB8fP9e2cokmX/3tLo13hMTeW5kHBjY8YRY8w+EGsYZntS29QPnxTyqA+wGmYZST1u9XcPxcQLhReKwHymFTVK5TyQSa0ErbKO2gHGgmo86bPGkgYlL'
        b'4RE3RnfECHzl0XbMXPiwCKbBfiS7kqOlyhA2oBanWg93BtKdSWdrkVB/cmRvg4oUu7Q31oj40duBbNAtwV5bLdbuE0C2t72H94oYPB0r3OUxDlgmwFB10m6WqIDQhd9s'
        b'IZW7W4NE2KBw0t5jSbSHi2BlkBTm2FmDhlWkmWkzVrjTURTD4wwzZ5KQAdUbqEd2jSG6/pTJPUAFYgbW0r6tR6g+NoESVe2DSEwkKMpGH1AYg8NBP3t2wHEf0rYpTIRl'
        b'MtrWGJivbG61POQwfrccxBKFHVIFVQJfQrwRQS9e5cmOoz8vnMlRyIbXyroffLPM1MdZe4tatLv6UFFlNc/CYnKsY0eA7ezxLuaZY9XW1WweF7LizNnJt2//yrvt98KY'
        b'5XULLScnO+7KSV1y85cbsqvzHlx36Zy6/qR1z+sv7398JrBE7HO34WZo5OdeJ3c6rW3VK3hQ9kbSzcy4T84u2ne4d6FzDfO52Z53mt7Sev1XSW5v3ZKEZS6F/c3efQkh'
        b'kenH1ry+FswPnRfa59chOFx6ESYK6nuXGbKr+amHq1UKTOZ26O49fEDlpOoG3Tz3l174/HqQWrt+VoiKwYwiB/vdraEhV+2mdN8Yd2lHo1HxbDdua+FbPSWOrqIZR6+7'
        b'3HvHcqpdSNqGxKozF24u2ffRkOVXjxeW3i/aOOH8fa/a6uPN8/Nmu86pC/uiKGfwzpDOgm6vPb9X/KnfsnxJ9zW1O9Z33oxT3zIrbeMRIEm2tC1INszZYv31LbD90/ca'
        b'fmi8KzXz+XD542qNroqfSk8xUR+mX3y932j21YPfLMwcdLhpzn7eJLtzft6xaVddz1u4utXDaWafdOvX9mpfmz59zLd/dI5t1wUz1SqmTHCxCdZ8qfwnfvaDP+xmrri1'
        b'aNmNrNqNe+fZB5vcdrc3HXBc2nzAZNdUzR6JVens2+d3dS3yPH9P45Wy4DONiQO7mQXB81+zefPx7OW3amxiHE98m3NJ6DzlxK17RdXfawz0cw+mdjlk+Hy76fYeYfTO'
        b'BzZ/vHRj+8K2YJvXfplgPrPReM7Mimmv96xIq33DKW7xjYJ/Hfr6k9DfB+oyMkr6vnugZr/yN/uSO86fXDR/9/T6yE+vvtr60bfmHXvU5vVvto+dEnzw4YpXtm3vmPfS'
        b'2v6LXV8XH4/4V0+I782gnze33jH6dbbbd8dfbljX8/L60/fGh3clzbhjsiCk1ORwumvH77a7/1DJMhWt7AsVO8TZE95pMywb5al2Fm2dJz0ZqRujCWVwp9uZKVwmYQM8'
        b'Q90mY6SUP8mOQgeFXGjcDVuJ3GijQj0q++Gp7XJ/vaSNI1z2YO0YKiWcOwRa5H7OsG0jdXU+Bwpp6LgjIB1WzwONT7p2Kvw6N8YSJmZ9NE/BYVsbUh4bc9hq4CRN1NwL'
        b'q10WgwYaoDqBXRQB6sgXQaDO4FD8cNJx2ApzKLddC067w/6ZCh6FOIR20Sg18BgfdPENKfvVGGMvsnG3lNCYYOjdRPocTNETkIkxRPxOMg5ubSDYKWYZwS4WlmrAPBp5'
        b'pxxUzZGJ4y0Uvoo+LoQz2g5PIXEyE7YjqQPHT9uFKqrv4kCTaCuVQUw3yb0Yl8Ea4shohhgy8pY1wn1wcD1ibIUMt5Z1gUloFmmeajVYJfMBxwwVPpl7t5G+JoE6WEmX'
        b'NU7Mj1M6u0YiQUruN5k1n0Rzw3eKBrF9JOuBFsLxIiFsklJWcAc5I8PIVcBK0sAkxOGfwtJGuMZwPAyYGEhDl5Qyq3FMmS7Q+LSXYhI8rvDX7VSXs8Y+EaCUcsaWgDoz'
        b'I3H3FGhDYsBqeFQZgwjdCHWUtW3wxWx1BprHHB666iJ5oIEFR91hPZUTWneBMizf52ARHGRO4QEkDJzcAU9S3rkWVoJCkb03FlNzYMok0BCHGHNdA9420GpFVz9voxCL'
        b'iwQq2AzqhIyqJhcC22U0QkouktgyYKcU5KMbt8N3ZDi72UjYJ6ZfJABXjwQ8eJs9CXmQAx5gA4+Meg/M1EEECy6EjpJgo2A1nZGLoM8Sj2kT2qaYrKkIu+ogIchZE8E5'
        b'EZFR0X5vpXIqPKlKZ6sbCaR9ZBufhmeUMQlD0FLi6fCMWUfQIim7nmLHYZ4znY4+cBochllSsplXz+H7sugObYAXCS34am6Wu7qCEnBSHvG8HFYRYUIFUSISKEGn5Em8'
        b'BTjiTpUxnUh6zxghM4BeMyKjsYxxKN9yBqygYyiGZ0Ab9tjF0wiPODOM6iwuSBRJMt7D7A3jYS8oVXxP+BrK05gZ82Ej7IOF9NhqWC9BdGvi6oPTpcNuLOZ6cUgYqQOZ'
        b'xE0fbd924kRPIIgZQnBipK3FYYNQPxQ2xWFwpBZsBAPPdQuGF0GZ3C/YHWZTxVTlOmMlcwJztmL+UYXR2sCbtgCeo69x8pArxT5mTAUZISONPPCIAHShVzxFlXZnpsJB'
        b'3JYvkv7swXF4Xp5QjMezgKcFREqLhzkTMUZmDriIYTIEIzM7Vqz3/1GY+l+FkxkZLmaqwtXls78pVmlEahBRRUh+dDgjbgIShcaxBuh/LBRhwYfGo8dR6rF4o8qpkwTu'
        b'qn+YqqjGGiBZQI8dxxNyxkj80UPfkNAej/k0ZTUn/FMVh/DAXsmPhfLP1P8U8jSwBPEYyRKPVXmqnBZPg6dOBDY9Tod4D+P+VAVaxCNZD4l7eiQJPD+Rz+LnmSSujv/4'
        b'aXdcIlTJBSjq/Usknv+VW7FcgLIfNd03/r63ilXR3/Eppi9xA3do/Myc6Yb+GIUfHEflRX8MucepaknadJJFneROL0G/hlTkHrZDGiMdXodEI11P5+KnsekoNhL/Woh/'
        b'HcL9qCk9/oZU5G54QxojveOGNEd7pWE/KOLBQyaGroPh/52KYtgH6Q7qfiZel0SGxqjha9lyViwXRKPKcLz/m381+Bo8K148vuZXO4PykdJxsAPFVo+F9fxQeIR9vqcX'
        b'Xg8SVoVRZhRWUXp9cf+Z1xdmezSYJ72+tvnEL0d/h4J+MOjo4DTdedoMR3AOnI2Li03YifhD9KcBYmW6YAfsQZcPjmOuqqGupaYpQnLkEZCN4Xp+y2E+PLFGgEHGfSIR'
        b'rAPHiRgNurhwdIU0g0JsnJRgYBXOFsJj9GEZD/aDo8HxWK8YZgMLsU9KIMyZxkwDyTCdSMvcxEXkcfQLsV8HQXIsqteG6untItXQYX8OZDvysSbQdDoz3X0S8RTYGI+u'
        b'Mnl3PNASQOvh/mwiiG8HOLIfpjpyGIdY58g4LjKhPkZNk7xRT6QWyxhMtgPH8RCz4AVisjbCodEcsSn7FOhzYpykMJnY22eBY4jVyVJ0iC79Yzw91F8WqgyP+dIY7zVo'
        b'+i46sjjSGMyewcyYBs8SqD5oRe9QQF8SVUaTmcHjGAN9VDcMdNMIBqdgq52jAEcZXOHMOIMjsJ9kKQBFaJaTaLe430FwDldlUdU4w3gd9MRsw0mOiKYmg9SZzEzQIiXV'
        b'YCFMxR4HpKIKqERTA/pituDBXlxFZnW3BBQ7IjrUBw2z0NuVgi7iM+Bg7kjGCbqnSlQm0o7AWfnkwPQlG0En/iMLFM1mZq+GZbS3JutDypnJgieNeZbyJQQNFqTmGvwn'
        b'EmcYZinsncPMiQFV1N2jB6TNJAufHGvO4fWDp0E7rngyjiwi7HGGg5iKJ8IiV8bVx4OMUhK4jvTnAAdQ3YnydRinRZchEUeIlKGFdwJpi5nFsAUOkqWPVIHnJYQ2eaBy'
        b'Lpr/YNCBuyoRka5CrEC/DK08C04sYZbA9ml07bIQ33aBziR5w5QxKkF4NlHNmDGU0PL5U/CprA273Rg30BxMXg2RSwNsJJOJ6+ksV9Gj02kIC0m1XbBUTYZXvM52KbMU'
        b'FG6le6kY1u5DVboCyI6QTynZS3hCd4EcMqGIhk4YyXAWggHPZcwytPOOEDpdBXpBAamA9lcH7JizEZzHi4/E2f6xoJV07IF2ap8MrX2Emzvj7gZozQU+8AJdCVwPsey5'
        b'4PxcxTKmeCqmth1cgJgEQB3fg/EAtTr0ZU9ouZD3JDSuClLwHJHNKDtE17Frkh6OF8tglaJnDCglkxuyAb2qhlQxt1MVpwZeTYsQQqcSNSRq4YAizogRZqSg3ZFGv+gD'
        b'2QCvJg+JF/04CnCsYjeeBY1kY7DGAAlmaEGjtLwYr62BpF4UOBIsHyh6U5COFrcjVr6cIcF0OU9vUIOdaD1Xx3oz3powh1T0Bq0wU0E9yTDJAHbMlW+PCjAg3/+WWNYU'
        b'YFQt6PVhfEAzXVM0bSVIEshS7sfTsApUKZYFCYWZtONjAfGwE63peFdfxhe0baTKxLJQLwUVqVjgBdGYiGtVwQ5CCY6w2RR2qmCt4qnlzHJ4GLSRetroSCmltVzp1gKd'
        b'SEiE/ZO3k+lRdeJjb8S541Yw2Gn0GFnHUHh+KaWeJEwFeIjHYO4BVGvdIlJrwaTpInwSH+OtZFaCehu6i0tBFZ9MDKmFqaZseyxei9K5pJbvFomIwyZPWz/GD3RvJbcm'
        b'6NhlgPo6slVONvKjXLGZbenhnwIK3URCLNQHrWJWwc7VVP1bhJYcY+w7DOSTKj/S5UsJSvxIdX9QjLY3iwObn1uNZPHCFdSf6RQs3k+O4vI4HkiJlS/kUU2yDgZ6DiK8'
        b'L8+DhjXMmiWgifq99mguUtw2SeSK8oDpqJYPOEEpvHFdiAgt3mZ2LbMWDCCyIcJaL0iE1Yi0QWsYqsljDGaSJV8ZT+NGwXMiFRzlFpxcx6xDwzpCD9SGjR7yWeGBKnBE'
        b'QjYx2U9enqTmcj+YArIYHOm8fT2zHsnxNA8dyF2IJOcsvESDehuYDTDPhX5eiBapHGThVUjV3shsNJlBaNYKG9BhIabZHphoz9jzQIb8rNdUI4l9IkHpVGYqug5ryWuO'
        b'XwVTscuk8KAFY4F2EPViA2kgFSDJEjdfA05KGMkeeJisAGySwNN++E7MCpzMTIYtbuTj8aAU7ZVC9O6TvRwYhx3wBPk41AFWE48xmG9iy9jCFgM6+jM4arcfGuXceVaM'
        b'FboF68TqlPSOg0Z4jp6SaKomc/jQMpiMb9YgcugHrNFRsiQBfoprF+2NE/QcOQkuxCmOA9ihMoHONKbAKNhNDQilMH0zWXfOHHEM+jrr0ZfCtYQo+J7Yyqg4pB3Q7g2i'
        b'tGTnTpr3sUDSuvxUVIlH3FOy4kiFTTCPvMGmeeAkHQBMIoNnrUAmoRGQRG+gXpiM5jZLImer9ofzghTn8uB0+hbHQKXl8DZCa9qv4ionmEn+lHxTESk20M0CjqtIVBbL'
        b'X1O8UUytFrBwG3bWxKkTcepuVdC2HJzg0JY+rPc1YSzzYheK1Ymz3UIjjuFrYAxAgEb5fi3qgZc4SYMx3tSM3fJsHxjMoR9+pqLK6ATM4jEBARq/7JhCP7yErsJJId5o'
        b'mQM29cxWpx+e3spnVOfW4WhAO054b6Uf/uigzUxgPuIzDgG2l0TyFEwzrFQYDetBAWMe4KW9dCX9cLupDmPu1cRnYgI0fLT05U6BzuqMgVOoCnY0/NJ7Ev1wtYEBY+2E'
        b'ztmFAZt0zeWOhvtmCRhVh34coErDcr8d/VCgg17T+iMeDnFlLV3IEAfq17cZMbZLkJhqHrApRt0dCY6rlpIv2r3RC7gXczicUXNcEH3aXwuN1dyRjJUXsZn5uuQk/u/y'
        b'AtKBsQP61vYzHk6B5LB0CfO1I/nvpwVkq+m64UDzqHdTh2gmWohOFOI8Uw5OeEvwoZEEC3djZTQolIfrIqtYqXtISXF204YJzlGbdPmzHRo+Y82iLueqbNhPX/RrVTQl'
        b'1juxm+Xcyy6OTztPKmOPYe4rXO48SRMuKRMtpcoxI0OCiKiQ0N2x+HZ5VqYlbSSsY+6MMWJI+nqY7c5KfLDncBY8qo72Rba3ly+i6L9IVwXaYIloERjcQUY/03Mdc3ZT'
        b'tgDR2N5jJmvRivj4RMy5uJkva0DdRDNNOQWXfQxWGBz+oeVOe0ld5Te6l8bqfq228wX2km74whULq/5w1tUL4rlc3Tzj5aDASYFNHvEaG899/9E94WCSxOyFlsd2qv1x'
        b'Kz698KD0cbb4dugvS19MGmjUXVSUbeFjlTdpXs2rwprLS0NetXIqXN+VN/vLy1xmiFpoh2Hkl1pdhS7tWddz5n255duN7zd3mpnsN1k4ZY/O5i8tJlgd/cx6j8Yrl/Vn'
        b'eZSDiHsa/Zc7b1tcvTl3Dzvm8pZNllO/UN9jeCBkQWs+r3ew8UOnqM+som46fx+gs2un9oO7jPaCfduHrBfcGRgsXzEjPPDyh0n3b/RvSTiw6+VFRQljjs6fc9Nl+vfG'
        b'kRM+1ayKD920wFLL9FxDibOuhma94bxpIVUHSz+4WVBQvyS2scYhecr9NbLFbhUZ3hL9M54f/pxY4n4q9VJKca+efplfgXVjR+P2lsZP7zr/7JR928lj6e7lVrdeeVR8'
        b'afvQV9rVA14pl2orm702FPy04DsT6JwSUSqbFDlusl3D+l1/nnOKKtuiA8++6Rvd+NviudlLG16JORq7uk3dTv3OBThh7GX+3f4q58Ufd3qfMgvUHnv/x7nhU6ILsp0C'
        b's8tm1vZUr/nZdVl88LTA+I137jq/X+clm5W09uPSCydv7OvZF1F+q+anA8Xr3o7+/S7YsC+iISF4unvm2g+tXr8y7+PXe2oF1VZT1kc0zHqj29PtypWoWONpv06KrzO/'
        b'Zp52oqDNxWrqnuzU1V99/UngWwa/HnSLzziT85o0fzBe3H5xh3f6a/FhU69tli3Q77xSZ+a36oSbQPMDSaiLo9X6Sms3jcONbbLvVuZZxgvuzGz6Y9n9NN/S3dum3V20'
        b'2inxQ6maOOaH6h6Q2OGyuPa0V5NBcldbzft/Tnnjp3+1vbZr0tp3DV+5Wf7no8Pf2r8Y3dy/4tGaR8nfWBxr/oP1zBTNEFiJtYgC28NnPFb6eoOzoNnLV8AI9rOwRseA'
        b'qn67kTBeBrNo3AhQAtv47izo9J5CPeBywPlJUpJTUGo3O8SGZUTwFA+7q2RSW0fRJsTodeJMsEjuAO0wj6fOTpttSrp1QHdshgTmgmZPJN/nOfJDsIXLmJoRBkAeSMOB'
        b'hDxsD4JBDz4jSuDgKbRzyaiWusM+Ra4e7D5nArK5PUiE6KVjbkasKhJ+c6faYEDfIX48CzOQPFxJPSbb0UUr2QD6SKIbDnSyaxCrQZNwrD7ohW4rueucdDxxngPNK6gq'
        b'vwx2LJcjhU6ANOzcLuTghf3wFH3VWlhsKSU+OyyD5B7+GIwLyTWn7of5IMdLChpWKmxl8HwwaVSV20DiLJmrjIyzhB7PE4//v3XGeb6aUuUfao2H1GXBgVH+EZGB4aFE'
        b'ebzw38YaV/zP98Y6TKLupT8c96fyh8c9Uv7wuT+UPwLud+WPkPuNL+T/Rv5V4X5V/qhyD5U/atwD5Y86d1/5I+J+Uf5o8H/ma1CPH9W7GrrqJKo59uNRZy15NP43jReO'
        b'Y47zOaySxk9ghTNVgOuweizW2hnwdFhzUledxA3HHkcc+Uud/It9kKxIolZcJqXf+KqWqP4klv8der9fuZvoHefEGnEKFShviBcRGT5CC/03F2iM0lEHtzWAHXXm4Nv2'
        b'bzjqMEnGXc9w1SGM4Km9Zsq7lFykAsYIHN65ha8KKyc+Fb9WXXGt41ASIzCSrByQxoWpK+PW8v9u3NrR2kisiVRlntRGmvo8XyeKteJoDFwY97/AInNP9S3wIVzDWx48'
        b'pisIr1vAjj0B4xiCiglyXI8Z5LXWNA/yCmt3Dz93fIx4CEDpambmPqH1WFgZMfHQGL4MewZpf/j7vwLcA98Is/78m4BNL5zNS/J5P78ydVpaw8n2jPYUi+IkRxMm6gXh'
        b'1TMpYo6eTFVrIEYO4vA6h2YLGOFcbgw6K09Rq1eOBcx7hiMAvAB6aZCn5mAFOuUZqvEhUfDW0ODt/oT/IpudZOz9W5udOaRqTV3w9pr541jO/jgixLAP24iWFYTPRowg'
        b'e24UdY9VUrcx+ssQc3xz/zZ1M0la155B39gEAgoSnEmoNXAC5LmDbDl+5SnfMwyb8oa5QpAJakHNGuySZSyCZbGwneCx/GDuJKnt+HU4/U82nxGO49RNkJhPRM2SSZES'
        b'WODDwVoRw+myjOZuQi6vz+MIgtPB2dHn52kaOFspTfUGjoRJvXx8QLUBBuOp+nIyL3iSVHnDTMSg+0bVIWzzIZYfz8gwU38zIMlPM2Ynj7n8PbeGZQwvEzEhVsrHu8Tc'
        b'Yc2MtebrnZkdeGILd/MZRDLWLBISrhlfsuQYGZaRr9yb6bf626/jf9nFY3gCdrLWbdLbJ+7yJoQ/xKzdtJuRYdY7/rVfP2n5gsPAU1EEld3qwoR4U+o4CO+LE2IE9LmV'
        b'L4vfvPGFAOOmte7xZJhNL30jRLr1i1uorhVjXOsqwzdnh81sv9W9Ms0EzZhVDCO0Y4v6x8vwhJrMNpDM9MOJCxussW+Kfjvvy5gicgsRmPnbn294V/uyrX/hZQ8Bo8Jy'
        b'03dsJP1O/3j8rqZ3Mc0w4u13V5HPnMaaLrV9F821DWPTcZR89E7NYu9dWejE2Mxs/t6SDE+r9OVf1me9jf76nEn7/Bvy2fc+9258nfU2qvoFc3hrCBGvZ/qDdJjlgcOd'
        b'tiBJGtsRVEEW54mk/dII61l5rKwJtevjUea2Upr73kKN7qbPa2xuvOu4f+llB9GVF7gMwed6KU4lFyLUNmxbxLTvbOHu3BEE5eZdT7GbclP9248C1m5wnby6ee3Vq1dz'
        b'tb9nNr7y6vfb3V/Ic9CH4RNaZY6L6sYeLYpwvT+5cXrO/Zeux87oNztU+PrdMv2Zv44tdmrt/fP7o3mrs05Ff68+69s/fnRN/OJI/cMljpMeN4TpXY3UrpYeM/7kR8/G'
        b'aznF1ik6bfsueFu8v/Kna1c0o9UHv/Ftc3t0PWbQulTFpObloppptQaTuh86fBfwatbgdNOEmMbKaHHYOC3pljqt3K5P3V9dVKK7WlzUbN6dWhD4bcUd89iG0qEJO8bp'
        b'Tf75rcUbxC6ZJ1ardMZ7vtNoX69y66JTS4Lwvb6tZR8eljqVRcyAv/tHG775yzytMX+4P37x8/t3P+/5WXfXsQslEwedlp23N+3OWrc/dsqKvvZZXdcM47+P/+3Q/ZDi'
        b'e1+kf/pYMsWg9IP9L50oOXfJt9flpfD984J3dkz78NydgXcc96Ye2C988PDuN2O+e+eKybpzd77fc//MI/M3/Z3rTl45YafXdWHlB5IyjagbOV9dX3j9T15Z4Kl7az4R'
        b'6xDmcEYwrJCKsZoaO1IKGWE4ZwOOhFN+tQpcAO2YlUP7u2wMRuGqgjwueglLnbkyZYBkIfS2Rc+mr+RPY0GzFc3RBnr3LSJ8owfoQiSSg7FxqqCSOxhnKffoAY1bZXEJ'
        b'CeCElaYWyNXWhh0aO9ElC8t5oCx8CmVqy8LDFaw0H3QTVhq27yTOTdbLIaJHb9DMTNmB+N1Udpk+oMlBx4ABnLAZ4AQ3lHEVruRw5OJO0qgZPA0KFSwtLI0hLC03h1Td'
        b'DBOtETOM3jZlN+lVTcSBQnQQHqN3Tr2dHqoJLsBUsR32dBIGcBNBmQVp12kTuCCxXwCaCTSGAmNA0Ra5q8nyuRLPOaDFDh7xwJlERaCdg2Ubo0iz/rBiltQDHbOwAyaR'
        b'Sd7MhcLDTuTLJfDoQTz9+TCRRpLDF90eSAEKK8cdJIEsL2r4eonR2rlwBqv/W/v9f+I0PYpPHr71yNVZ/g+uTq0pfBKSjXKlRiTYmirJvoP5TT7hQTFXSXPpcIkaiD/l'
        b'E75UizwrZA1wJh/C1+oQnlQDPY05UO4PDYEG4U/VWdP3hHa0F3VyUceOU3KhgiF+TGDc1iF+SGBc4JBaeGicf1xE3I7Qf8qX8mIn4DZN8K/xyjsc92PwT+9w06Fn3OEk'
        b'gVWzAWwkl/jwBa7CGE0Bvd58TO4XgrkR/BselpI1xG4SxFjOhvGUURK4vxUlIexZzCGfeTo4CrrY8b0R7DvZ8CASeTGcHatEEXnrgXM8mAwaXCNufi/hywhW6LO7/wq4'
        b'HXDn2yUBXoHfhqqHfealwozP5/nNmzgijArvuc4MQ5p4qUYTns0/IDyNrbGmSiLg0yUzGe0VM5Ix455cWVx59T9dWZ2Tz1hZzL7uBZUgn86ZYnHTYIl8gScvFqySgrT/'
        b'L4v7zMg3vKcWl+cTEWXQwCNJEx5ajycrF7AjLCjEPfDOjzQekdkDXthnv/3NtZP9V2untT3W7Mm1m/BXazdh9Nrhyuv+8dodf87agV7f+RKfEUvnDlMUKwcrBAHwKKh6'
        b'/tph0TUdrx6bzg/j/7dbE6/c09ku1H0I7+4LjgVIbV13juDdYTmfsLaznc24/VtbtJmYm4dmOaYYkw9/m40Y9wkn+VjOG6s1Q67wXsdyjG0XejLQrGuFLkNjnfSB8/v8'
        b'QAtDwKRHYSoDynX8yPMWGohpds8QMuYBGh/PETI0DEgy7ITVfnbwuMQdpnsieVK4nmN9bCO8H/zCk+1CT5iuPWSS7aIFHHSWhH/w6xHRks9VN6lseM0wf2VB0cCxU7U3'
        b'NZyn5HjP3Osb7apuM19PQ7xqTdgcrWn1IW/HpQWnvfvj4KNv8m6JtcYEe8wpsbVO8ek+lhroP85MMvT9wdyvBjK6vD+esC7ij7u50Y+/5J34UE1zz68vm7o+vCpWpfjB'
        b'dDc/iZ0uZ43NOUJQwtmBizTfKixYqU/ZI19YIVOwR+7BxDE0GFbZEDMQ4pCcYJ8vDsGRjTgVcBi20NqFK+EJqvCDR8cpILO+8hTFFzzWgibEXhMWCwnRLA5/bglbYA6p'
        b'7B3rKg8aI2Bg11SitYN5sJxo5hBvNF7iTjRv/Nm7Z7KgVcuU+vzmwZKZw8pAPg+cw9rAWdxT+xPtpL90HxvSwCduTEiYP74wqUbsH2xa1SgtVosjGe44dJ8/wg6Q+F7H'
        b'3ivKrRyC++E/Aep6aqBcrAWuE6IYGWli4z/d0HqFz9jQxOkgHyROoYexuwe6brfCQTqzZjCVD+tgoe9TJ6aa/F/ZuCcyqRXxijSKVMK4EC6HJeohbjhiUZhqCC+En6qa'
        b'wm7ghwpCBCHCVCZEJUQ1h9sgRGU1UlYnZRVUFpGyBimrorImKWuRshoqa5OyDimro7IuKeuRsgiV9UnZgJQ1UNmQlI1IWROVx5CyMSlrofJYUh5HytqoPJ6UJ5CyDs72'
        b'ht7KJMQ0VXWDLvrWMoIJ1U1hathcdoMu+harw9TQgWYWYo6e0AuxICEgJw6peAdGYa/J3+xG5e3Bib/MI+lXNKvZ6Lw+iOHE5/dT56ia4rBbwsjDQhFfQDLF+D5UU56o'
        b'/L97ov6W8m9TR40a7XDqqOclasL7heaKwn/hlFCBtInlS5aah0XseEbWqVEUhmn8WZpAAokLgIMs2fk4kYyv3Ro5Ag1DvW3tvdRZZhmrMtPRJ55kwu0FeS6imJ1+6DvF'
        b'g3AQ9q5SxXoJnCI6m0YCCzZX1YA9sDZeDjHOtsbpe71ly+WRfUArrKHuS80GIFORnxeHvWdpfl54Gp6kTjit00GFxNObRm+X+PNZRn8KD56Cp2mkGx2QvFEcJ53uyTEs'
        b'bGPgOXUbGvjnwiyQNRZ2SJXpp8FxUEN92EDavliYIbX3pOH+RdEcPBkOO4kDSDAY4OHzFzu1I8HtGMjywhkBYAXP1SKEXj45s2GiFLS4ozEd2Iwb0J7IW+cWS/1bMuFx'
        b'0CjXMnovdcFH9Dlu3xKZPNkRbAX9SHKzQV+7yDiiEAFJ9uA0GfNGj2XOLtLR0aUq1ag3y6nN2N8Bx5pYA2uU4Saa9GkENnh6OywCR6QjsoaPI/Ws0JKdJyntvUHNXnmY'
        b'LjS5GdRk3QV7YaOTg/SJaFvr4EmiHNuzUOB1jca+8yqe7c1Qx6B+voSG7oK1MNsCpq0mF3VEKN95KQ1vZuu7RYDVdNi5zW6zGVr/wpGRtRRRtZCc30Gq/sDwXL+jAYhs'
        b'15vwGDqTFaARDxzH+YK1rDzUlw2ooH46xSBxhiLYF6yYpoj3FQTPwGRCdZFodMdJuC870LZEHu1ruQoNwdQOs4IkzwqWBZPAAM2S3LmZdKQP+0EyJhV0L2uDFLRuHKKG'
        b'07zNsAlWRqhLZ3MydE8zVteOHiiYtxIu1Eir7S7wLk39Y8onDotfWj2LVXGvrnRfdDNkZct4r3Zx8U3VhDcjenU3hP56kn3n1R8uvzP4aK6WwQ6HbvFPAZKAWdde8b79'
        b'7ekXAzbOXf++1Z1HX+VN++BhqoWo52X1ud9Ga1+yuj835ivzn3vK3jL01tpmMKW//XpE9fcN3zd+39TT+FNM+Z3uepeUL3+/rF14tdCsYfzt7w1feaM94bDdmtvt+7/O'
        b'f2ViUTQ7996xrPhvP3vxVVmVrDHK5tzrcdp7vkwM1ypRu7rn7ZLX+F43bonWXNszFP5xw8ydPu95vef5/lzv8hvg9ZMDdxPE/j+6drzX/YFrU+FA3BebP4/qLLjy8qIs'
        b'6017hzaoiSafN3K993PmrTKHd3SX3HA3ijCqtX3H9rcq2yWP3TwWWH9jOflRla3erYuXV364QdRSUeR23dDzt7rrt/aW/3Ho3ifTri9+/Csv4/hx2az94nE0t/QaeJac'
        b'TRIMzuVjtkS4lbAlTkthCuiLlnrZ2NO7VbSDgzXbQA7VnnQFLIJZtj5EnRQaLSDphg/AnnUEA8PbAvNF0uHEKkGgTJ5bZQPMk+eNcFoWafc8XOACQGPOJGzFKdzgURKw'
        b'DHHDofC0OqzUl2fomMRfaY0uf0XqcUYk42AJe5BwW/+Pt++Ay/K8+n4Wew9ZooKislVQFJDlYoMKKLjYUwRkOMABInvI3rKHLNlLUZJz2jQd6UjatE3TNkmbpG+TJu2b'
        b'0TYd+c513w8Iiomxb7/wiz7y3Pc1z/ifc53rHHOsdYKac0tXBrEBm/g7Ne1+BPdY7RSpvIMxf3ZrrVXiAAtQwVefT9OGEn8brxQ/kUCcKCRxgJ2cL0qRxEUPl8PVB+sx'
        b'myWgaBPSS5DHfe0I3djBFTrxtYyD0sVCJ9CZxPvXZkjYNXOnV1Lh5+OrCSSPNXeLoUN9B1+rvRCLXKgNXvp5+tpjDT2QRaBQDW/wKLQF800urOGGwclAmvkRmjncy+RG'
        b'4ekA2dibwQpHcFJQJFDaLCKBNJXOI9xZ75TFjBNcuonzOGoViP385aU5rDm7lKQWig5zAktNQZwuA9P86y1YzW5f+0vTA8rKi9Iv6tuc4i/d3XYkoUJbspgi0G6bjEAT'
        b'e1j411wcP/oRGIdc6DzHXZsj0cFO8ktEOHPdIJ3PDDcKOaycPcloURaT0qr7xYf8vdNN2cs3oPUcb8mtJlpcjbQz5DQcMY+/BNbixlMPpzNx4TRTm6qxYgcojuZHu2CE'
        b'Vfx2cW6QbaehViTQ3CNm8nwPN1pFt0waJ4cxGRNkpgsEmqpiIIRpaSbzdFeTwvPe/2DnQBxun2Wo4hlxu+C6oiLLK6HMnQjLcz45Lp+EmK+qzX6UCUQrct+IRKp8jol/'
        b'acupSj1u7O+l3/M/X6jLy3PvyC7/7mvfYd9kqksR5GNVE6Q3m9au9APIP7NHU8S/ar1itVKYUeHMVusZjQpBjuG/VrnN9MSYnz0X/PqvykX/Co2PL46w1MNSXYSNXD0C'
        b'KUh9lJ//+QohSNOAy4WmxccmfUVpgh8vDojvfrE0AXsrPD0j9TkSkEtTfUtCI2wintrta0vdmh5KDI81io8xik/nS6Hus9m3tArPlyA/VPAVO/D6Us+GXGrx1Oio+PTk'
        b'1OcqAMGlyP/fr9rvXy71tl7aG1/x4T/KJq8Qei45Kj4m/iu29c2lfrdyZQDC09KN+Jci/08GEH0pOjLjq0pe/HZpACZLA+Bfev7eYxZpmrum9/S+31nq23yRuNKXsRZR'
        b'Gd/AcyfXlwuNio4gonnqCN5dGsEGjqu4p5+/dkHM4rIvUutTO/7DUsfGK6j7Py2boLDkR3pq1x8sdb15ueXMVn7RbF7Z/bLeOS33eFiMcCksRlAoyBVcFWYqXBFwzgAh'
        b'5wAQXBMGLPu8WlgMa/ZJ57j8V4TkPH9xgC+CVy2HzFHgxbhormZ0ehwrzP2IDlOj+foWXM3mpOT0J/0KT/gWFjfrCX//mRcVJVzVgUZHj8WqA1ffJnu4V/ia/HfMhByi'
        b'89zMstA9grsc1oVcHYmDImY/JRN+/uJlbKZqnx2FCK7LymVuWNRySzN9FGcTExud/vQM+qzXjxUXfZbPrM0FOcqr6PMMBgmc8CbexgmpzwRrHzk5sPJRUI0XtvJxNZyx'
        b'AA9kleABNuPCf+U0J/bZ4rhod/Fot4Q7zQl56/UPmm+H/SEsIebDsNJYj3B57iRu44y41+oHtMvcPYobRkFsl22wZ8VGSxwI+Fd+3WlPauHzbriq0ldveNrihhcLHwvs'
        b'KhEu7/zz59l39c9X2XdHAcsLM+D9tdu+CXP5bSd7gm27uRIW7Qo2E/HHJSNO+t7eOKvHSEKiJoQ++rnDp3Kvl/H0toAbduw1ia0QJjRgMt7n4dvCNBv6WsnZ4HdRcbEe'
        b'kT7hPuEJb9+RGf+V/msNRxsCgrP3vmSQb3Bs70var9v7vKjcYiUY3yT/z9iJJ4LeVg+AS42RUgonsUTCb7JNyiJVOUVRpsYTW8U3X/b45qzs9KPn2RzVf68Csp8cwNPl'
        b'MnfsxlcRECwdu30T6ez7hGjdz+L80nh0QLJ4pY84zSgtPT4x0ehCeGJ81Ne4e4WC1bSMrF/gIc7b9pPYLIE8PaPu+APx33bOGsSn/OtXkjQGUr+lEPdB2A8jTGN8w5Vj'
        b'/kCfLN+RrfI5OG/mE6bg4pw2ZloRZaaZ978hit2uAwn6Dg0Jeg56zY3FgQl6OqPWUYLi7ZZhJ18+jEYvVny7FVpeOdqt9qrYpt52nWDsE91SjXfN5PlUs23bjC2WjFaB'
        b'QJXo/N5psbsJPOQDzLPJyB7z8rdYcp3wHuFZW84EF2PT1SRz7yXvAudfhfp93Lua3prET3gHJ5fkDOctvuTNvWt1yMt70XXB3LY4YCwO1oNaLlcJjG7GKd59LZGYsfQ1'
        b'bSegm0+2Kws9FlgE1fr+njAkEcgmijaKcJKP4snASW/6raWsQGIIA4FCGIcxyJfqra89FJOPTwvlNpVjngPfVKVpSbgEjdz/Ii6biFCywmBcbP6RZnvKkB6pOgd69B/P'
        b'w1Waf/kq03VxJNIs71qrJeFYlm2DO52LZkskZpYb83ylsqusb8gvWhtvyC/C/jdkeQT9hiwPbd+QX0Sab8gvAcWYxbnx/f/nZSqXCaKN9PEsWzLWCcuMoSw2FIpO/nfy'
        b'X6hK1JV0RPzxSS7pgSq7JXUiI1CEchHcx0Yoe0KRa0r/Tit+/JBRtkavRhAlKmPHbnIFKgWaBVoxMs9+uMi/RWhDKUr5pjx3uGgSL4iWlx7nybP2o1TKhFyUuxK1LYlS'
        b'jVLj2lZY+k6GQK56lAb3W0VuRHpRmmWiqM3cO5rcW9pRa24q0PdK9L2APVEjRz96UTplsgpaClpRW7iMHjLSgi4qBaoF6gUaBVoFejHKUfpRBty7ynzb9CNfo0BjXlsm'
        b'jtrKHazKcKd+rDqRaoEa67FAu2BNgU6BLr2vHmUYtY57X0X6Pvd2jVzUeu59GembatxbOvSGAnd0yd5Q5eZozOZIsxBFbYzaxM1SLUqLs2hM31CV8gj9FR4bnfr2Ttqg'
        b'FTLezWjlE0wx0N9pRuGkE5ZrCna+GJ5uFJ7KXDbnM+KJDVY0FEPAnns+ir6KTGemYHy6UXpqeFJaeCSzhdMeO4b0TCfNk5wq7Wqpl/C0JSuKVFaSUbhRbPyF6CRps8mp'
        b'lx9rxtra6GJ4Kivm5uDw5DknM9Aem+CSxtt3MNDN2uhActLWdKOMtGhuBimpyVEZ3HCNV57ySp1wqbR+T1y5WJn6ZSntC9v6pdQv4kLxs162ePvE45vELddjJ72LCvzc'
        b'4rSe67B3aVWZ5UZbu3wrVjXR2P5z2xZlbeTJ+bKikmlEZNIZRV+KT0tnv7nIVjdC6gSKXgVUSAcktdX5MT1hwV+MZ4Okb2IyqLnwqCgilaeMKSmK/jcKT0lJjk+iDpf7'
        b'ur4G0YgFqx1gq/hxt1hhFu7JPMrT6n3cY8lljlVY5sNlUz3q4eO3VNtuAQtOJSlhj8Q8gzkIEpROrHwd+2BgsQl6UXoeewELFK5iDt7ljyd7YQBysZrwuYdEILNVRijE'
        b'BiiDKu6M1NcI29hN4UsCaNt2CVnGCAZ9ttGnyQAr7MVx7LGx3ywQWwvU9opMHLCGO5cMx5a1fFkxi5DFazDsZJ4vJrbbTAYqsTKLu6Ks4GFgIWJ1VbTxThrexSoO26le'
        b'EycESUu5BJrYCTJYWFyyMNR7aUmOYiFXqqzMkmbbkurLJ6c9kiyH2fKp/Mn5BBZjS9p5lojhVjTksTPtaf141Yh3RGk/o+8/vz0eXeGYIHZTzr/+Ct7/4HiinLL9oRcy'
        b'zDe8UAGzqbY/kxi+rHeg7MOI6e/2Hn7z94q2u6dizPera36x+S+ehW9rNNnaG/yhWe9M3pxpUO1fHPSnG6+de8XqZN/EH4/87E461PkmeB0KW/f2D9r/reN00Gt4AtCg'
        b'Z6YgV2Ptzrd/+nDj/OnuEx8aXXsjMEI32u7DqIXRn9/ZrR2z6QdB0eW2rx640vT2G7qf/nHDz11Sv//vO86f/jyo4fS7IevXxWpovn/qHS0ti4W/zX/3Q5vhN/d8f2v3'
        b'vz/8c/lH76ue3u2W+Na4mTYfuJVzHrq9tVSWggawH4Y41KqSdGH5mSF3YBhwUCLviNMcDHSMsPX28bwG/csO79Ngimt1A7adwU6NxfgqdowZf4Z769IaF28f84Oqyw8x'
        b'sViTw7KhOK8G5fbLYq9Y4BVRTiN/wngPGlO8+TANM1mBgva+VBF0YGMCd7zkgrNYwxJglvrRxp9YZ2kuS0B7UnxkLZTxkfILttsstmExwwyycIflShZZGjvzCL3OjiVP'
        b'kJ6fcqenRpgnuorDF6TzqUs/Dh2EtGmVJMZCuB0FA/zBa1k4zElrPbCAduwQiGxhDkY5P4AY5lOlh3vMziVms5IV6MJ0oI7Ew/Ecf4CX73VwyTKQ1cJ2fChSicFi7v1r'
        b'm5xYUkRvlnKQG5mljkAD6sVwC6dwlK9QMIOTqeyAjnH7MX2O31UDxL5cjXnmPwjJYgUluKu6LM8kd1kJyrex26zlfAUmdxgLuC5HbZYCf6U1DZpOqbDVXF7pwwlvch1u'
        b'xNu+rMbd8sSSsGAvOeMC/dI0iXBrOwu6pn4WO5QV6AjiM8W4sHfbk9FpzxIuvtqhHKuC9I1sB3t5rq64MpfcnSV61xQafslC5JW5UHrDLxVF8tLDM0Nhpu5KBb16zfEl'
        b'7bvsCO0rTiLF/LOrHJytVXoO+0PvJ6vYH08b9zdxN8t8tat5r5LU1fxEZ0uHabZLCv1JDb5MW/8Hp2upV7/q4MdlcYipu1gY3HLlusLXzTkPuTjDJefhs3q7nwgm/v/p'
        b'7U7NEz42rcX1esJ1uUP2EF8O96efB37Ql8+7pn3kBPJFwun7Q2ZCLgLEBoezoARK8OETjEts64j5X+OcTi1gZVq3PEYOaZGJodx1zm/idd7/PKyg3L+K95GVvoQa6Frz'
        b'yP04xT74+FthlcXyeWLdI1ckdELbMhe03npVp3NY8jUR6ZxjrED4jSPSn9EDLfHLcKLP17H51OPCnMUlFvmYe1nCQCAfosh+4e9jh0PM6QODUKRkT3plJF7meLAojTug'
        b'czjzQZj1Ox+G/SDC9D3LcJ/wxJjEiA/D/hCWFPNhWHGsVzh/Q6HGd912+XXvzZqJ09lbu/Ahq74o7R1bLz1Nm5AuscEZLvX3ble4t3pYEVTCAxzBnIN8QuIq6IexRa2B'
        b'xVC9kgA3HlsMWvhq5bDoOk8telZyXOkTf8Irv9Ix7vs8pKnZtgppMlF3BWZpOb8RabbvWuYl19un6pmRYibiHOEaQhOeXjn/+BHSwq14g0vjI9IT8s9LbIVYqgETUOEe'
        b'/7uaNyWc+Hnf6S8rPeR/KBj/lf6vGl9tCGBe8ivMS77oI48XvNSrELeh4Ukf+VecZpQKn99RfkxdUVGSqfe0bVzmL/+aAex7no1TH1hFvT51MCQbmQvv6XKC2W4sDJzk'
        b'hAxJCpklSSF+5kjr3ifMRvfodLKXpcp0uWPk6Qb3udToGN64fSLYZRWbODU6PSM1Kc3ByG2p3Lt0BcKMkiMSyEz/Glt2da0o45fB6IF4fQa6ONxOPHAmyjPo8HGrY8dX'
        b'icwmSZa9UyFBHxYymLqAEpvz3o/ZvVgI2bqcoSe18o4qyWGZBOfivxPxC0GaP71WdXDfB2Efhv0x7LsRcTED0X8I++FoekTwC8E4WjEWfOemmYzpppd+/INffOsXLx4W'
        b'd5/VP6s30ZCTEDLeMNFYou0dHNDgOr6rlDssKvuDRkSuvpksZx9kQDHcJGtnjcKSvROVzFsWo/bYyFkWucuMC7Isyhz4oLcJqNq+aGcl+yxZWhJ5snza+BwytSFcWDAz'
        b'0ILCyEQzhhk+om5kI9Zhpar3I0tf6QSrRrUAs5xQVQtavdbDrQA+w0ON5QoefjpuXZ73gd1pkdKNaFH7fSOeTlHmrqiq8hkgDB5jp2XNc732S8PUOO/4I4y9qh7oF/GP'
        b'PULWHtRE4POwvnbDKqz/FWN9Otc/EUzxDZDBF1Or8nv6kyEtyTGLVyT+++zvxvf5jOy/+uEcwVIjO11JGjMYFTz0Pwg79cKPXxyt2DQ0VteRb1yyg8tmsg0kWX7TZiKO'
        b'U65DoTx3x0gaQUoc3hErIzDA25JM90SpGR+Knd6LYbaQDTn8dQOYiFw8nVr9WNVyUUXZfENiFlxnEZmrEoZ0Z/hePEWLUNdLtLzTqOehTdXCZ6RN6RDMeLZ4Qy4t/EJ0'
        b'aHia39M9xSxMQ6qgZDmbSPYb+olJSb0dsZqfeJFumRM9Spql/pmo1m3J4R+dHs4C18L5wJ1zyRdI47Gs8ovt/l+RPP+OdLEcmDuZc/VbMh/yuYy0dOZD5lkwLT0+iQ/n'
        b'Y5buqk5g3vpdEYTFPP3U+GoO6CVuY2NNDb/ILxfN+WuYjNHzk/5iRamObcE7oUzF1kI/zzlfp2RVQvgswxXq4diB3RbsrpGHAGvX4iSXY2XjseSAIJaaRSJo15c0CtM/'
        b'AM4ba2YhEUgstLka2h8nnRUEpn5MtMC1dRonsR8mYi38qa2jAmzywnvxl+7+WpDWQd8WDR8PemWHoshNWebHbVGvB6krKX1b6RdZdVYHfnzoxrd1dO6GVccb3kw/E/5e'
        b'7w9PmLV1e7zlUlC920nTffbTl6NMd1p+PPT7yX2dWz/RtF9bo7XwfmXpuPaB3+zXSKhSv/vauvw/5cpHqmaUph3+yeG/vVzZ1fD7Q837jqRXbT3mUqybvP1Mqe/rUz/B'
        b'P32YcfZkz7ePJ5R5n/vXVKlj4J8+HcloOO3c8JHZVOurZvKcZwwmoQ6mCYHXLPdtOp7j/JdHYXLDMici5sBdTtefvsCp652bHR45VMsjHmn6WORrem6kF3MdYW6ZmxFq'
        b'oZDzM54xg1kL88V7Ajgfq+Aogrbr0MkZ7zSsMWhf4Wn0whtSZ6PEI0WT91X248QF2/jH/Kvu2Mj1vs5KxmIbttFDiy5SkSXcdV1d05rJPqu77g056SVYTr4e/sbyVVmd'
        b'r6eoKDT8Ul3MFQwRSvjffCkRqf9bIsrUWUX0UYcr/HQcLvARfT2GIEPi0bOPgIQf/TOZCet931BYC3J0/rmKuH7KmGldOQchJ68VloLA+aN8RxYMIEkMT4oNPBQpt4z7'
        b'2ZQ0F7n/GBPh7D4nc2opcme07FxYVKBWoF4gLtCQHgNqxmhKRbtcoQKJdnkS7XKcaJfnxLncNfmAZZ+lov2aZBXR7hYVxeLGk6IvrozhYedf/FkbfzQYmZyaGp2WkpwU'
        b'FZ8U+xVXOUngOoSnp6c6hC3ZVmGc0GQqJNkoLCwwNSM6LMxSGrF+ITqVi47gDoKfaCz8qQe/RpHhSUyUpyaziIrFUNn08FTaC6OI8KSzT9cnK04IH0Niq54PPlXLfJVm'
        b'YgvBDjDTUqIjuRla8qu8qp55dF8hKeNcRHTqM592LhEZP4xHFw8uxsVHxq1QeNyMksLPRa86gmQ+yntxHeKSE6OIsJepz8diwM+Fp5597LB+adPSjPhrE9ZG/ixu92J8'
        b'Gj8CwgBxyVFGDjEZSZFEHvTMIgAPW7WhxdFHhicm0h5HRMckS7Xx0tVpnggyWDg6O2kPX7Wd5TT01JVciqJzMHr8TsWjOOPFfp8WbyxtK8Im4slWlt/M+Jr3mZQg6BLg'
        b'b2Rna2+1g/t3BkkaYsKo6MWtWmyLSJ+nktXDnw9Ex4RnJKanLbLIUlur7vjWNCMe+F7+OnwjpUw2lRQyLOjTM6CzFbBHTSr0VsIeUz8OcejhsEKaTaoIH5wXCJMFMHMB'
        b'R/iasGNQDZ1KF84LYSFKIMRCAbZoQLuZkA8obTAiVUoWtRDbwgUiKBfu11zLXQaPC3eil7x9j/CQydTayhQLt5l7+hJ6GghMwfH0Y/y5NdSYK+zZDp2cowJbznutOG3n'
        b'7ZOjHj5QCCXSo/bIM/LQcQC6ORR1WVdFoCeo2C06HObzU5vDAu7WeuaBiwxXWCxmi+RjBS3NrLxksDxZ4GQhi00HoIibgj/OCi2wSlYg1MZJDQG0sup1XNOfnZETKAuC'
        b'/RWNwixbzlrzGUp+tVGGwOOsjNA1TFknQ5piPcud8IHg5RSWkPwNPxMBd/f8gocGdonYvb8hluaPLKt2Lq0V98bhw/ICdcHfTiiGhfk4798nyGCegfMpO7iL8AGHcdqD'
        b'8xx70gRKLRjsXJoMfeFh6eVj7WllLivAEjPl8w44ykFXiTh20Te0BFpLzQgfQX8gD1mxGavYcTDk4JwCdB2ElkNm8ty19dAMHOWOMGeg/NExZtBOjjgMoR/yuNvjQi/u'
        b'/ngITvLEMZ1hzl0fhyJHX+n1cRjR5yvkTMOI9WNXx2kTR9bgQ7jFve0oC03cDe66K+w2JneDG3OMuQCKA8fV2P1tCfbzlzGl97cFEdybW7EpxEKAd6SXMLnL2zB+lr+9'
        b'3audvnh5G1qgecUtS/7y9n0sNFPiGkrCXpb2zcpryzlfafIB7MNePrdArh1MW+AE3l4Zagqjl/jvZ/C2lcWyywlaW+2gUYzNSenckuLELuxgqQcYUpWmH6CNvM+nsyza'
        b'GMi5qYKC+fQDPVb8Tf6+CxbLUw/4QAE2sgFzAX3G0GfKpR8IPCa9gytNPoBj0dyYAqETR1kQK702vRTIKg7Gvq18WYbbcBeyvaEech8Lka1azzWw3QVuU/94z0nqLFy8'
        b'zz6zj590VQhHCnsWHQe80wCHoZ6niPvQBnVcEEu37VHC1OJooeMuay6/wbUUKAogG6oi6DAr9mclxHIogVboPMGlE1BiefoF6seViLPKrZ35e/74gCiKFXiq9pfswhqB'
        b'SFmAC9hNdK/IFSuJ2rQrDSaxXDU1A8eUcUwNinEmnfYiQexJe1nGkUQG0cFYGvcI3MLGxcfSiIqZT6RXjLdTIY9PtzScAaP0qC92LjV4Mf28QqqKqqzAVCzBG7ahXOaC'
        b'C1AKeTgRDk0ZZOedVz4PZWqpGWKBlqF4N+Yf4KVZx26ttPMZilwrajilgGPUJXt0sXOXM7IkcBplsO0Utz/hJsZpCoLFVxaf0ooWu8lt5QqsJGEZTC+1yY9MH0dpcOvh'
        b'rmQLiYgybl1wdg8Mp0F31qO20lNxksZ3UOyA09e5rMTBLtjAt7UF2llzJJVlBeqyIrwbC1XcgFxg7KoSTqfTUJQVVAjeq1wzyBTBBKutyW1qmiveoE09fJjtqQzOkSLA'
        b'KaiEtiPc+0cCsDPAFyvPbAzAMqwNgDKW57NJiNPWVzgxsVvu5GPtQzMOUA8kC7p5kurHmsw0nFZT2Evfi7BXaA53MSeDlSxbi7fJECQp6b3N18c/iGmUo1Ib3ZLJy1JP'
        b'H13MwWKSH3AjSCFtC5Tx1U/K9Ld6s1ztQltzBwG1f5pbkOSkyzjhQcLD24r4y08i0CDKqccRMdSpYh0nuCs2rhXsFFwykaiH7X15TxQvzYt9LQSBgmxfRfWwCK3EEAFf'
        b'l0PwNxfpB1OyDHknQa0VdsEgqxMF+YLLgssw7859kQgj9DMoEUA5jAoyBZmqWJ3BNLYBzAos5ATbTAWXBJfcznG/E9ucxhKBYI2xIF4Q72rJ1//+dp6uTBr7+Lqw6dzR'
        b'7yb91FV9eNrpd1dfajSxPf95rVPlbOef5d5UN/pos7qqwcFWV8GU/bdEGao5f882fLPQ8Z+aN3701gsffC5RUAgJujvw13uZ/X1fyNTOpSoKP9YtL6pJnTj5ebDhX38Z'
        b'/ldo/P1W66xe5+4TLQoHfhOlNVX+ik3v8c69hyu/l/DirzeZq2X/Xcc7+8jfjyj8bJuD4U9/+P4/1ngm3Gsy2KATN3CzuPut7e4ff+9Imvns9/YYvLi7I31y+9T+CZt3'
        b'gpXCOxuqt1TuKwlpTdDsfrW3YHbku4Ft6tUFIxdkynLv77ycVjzw91bYs+sD+3d+I7dV7su9R4r+eKdbxz3J/tvrvvhc9XTgPw4ec6wdfHXj2fe6Bw/+XeZSb9UvSy69'
        b'Itj9lxd+8L3kV8++d35Gxvc7v20M9J8LXghWPuI+/JnP3tjBTR/kfeb9+vuvbzu5EPGvgc/O7p1V/vPnmxyN5RL7tqedzB9+4Vh4HX5Sf/5n8Y7Hfn3h3N+bdd/wuNBm'
        b'v3+f0/RcwfG/Xh77dcgXe3/w3be2OJikGH5f/oUXkmz+ViKnk/zxz6aq/7zrvXM/3L7mO/+Y+MQqxOTH7/zxzRc++kthwJl7pQOHowOOOL9lmDz+w++HRU9ffNniD767'
        b'gipTX7z0rZhfR54Zjliz8Xo/xOx/7fIdqPbVf/9Tg0uXbxYN9Y/efvlS2IVvWRTETH8ZvvD+Z5+E3G2fNq8sOtL9d92T838V9f3N3Fnh90cmrLR+85av39TxHhvzC+0f'
        b'WP3z4uWzB+ZfcZzP+kmObFeMf6/h+8eyXr7bH6VzOrlvx/eTXi4vGmpKMtgV5LT2t1VOZRO+1x580vG7X22xNVivttdhznZN8vXpN/5V8I/fKZ9YXxLw2sXffipq3dv9'
        b'579v+JHyFzFq4WbW/EWuxm2Ya7EyIELTE0avi6F9/Uau9PQuD2zggATmnOKQhK+YL1g8EQMz3osn5P5cohoN0swFAjGUprvyzY/A3Z28Uygzc1mcnUQeB0hwcdpiAjoV'
        b'lqfIgbYA7NuANXzejllsz1oZIsYCxHASqsRwC2Z286FvMyR7Ztg9kValJc9ShzP3XZi+m4W1GdQELEvJehv41rdhW6zUqXSUIbVlEWwSD5jHed7r3kujmIBBQrlrXZan'
        b'YYN57poJYZaBgxZ+vmF7sUxWINkpJOiVk8BNbosWDrKYPMiHiUdOp3LM5qfe5k9AhfNWWes/igesdeQGbrcDK71JaRrCwFKiWRxS47vsUIGb3hZw13gvjZgU82WRiZDP'
        b'iWFAGKeHVguzueValnaXFq2PezsGSvdYeFjCgnjJwyeHOfxdHOhN9MYbocuiEEXQsS+ED+XLFTLkRaJaDnvCyHToFAbhgPSyTQapl0GCsXAniLtvIyRQkePHe++6SPtX'
        b'Y4kly5FXQsvha0nafhuNsV+MtTDswucC6YEmt8eO+sqwEu/iPM5xlLg/PZ3DXyI7PpKzHnv5HB990IBTDAr7wdwjJMxqtHFDc4GRgxzkPYZDi5DX1Id/tYTVP34M8uo4'
        b'rwmjLeLKUJ/DPIZ37QmGLOHdMcjhX27Yjs0M8u6E2ysg795r3MtabFgW2Oi3AvN2hqQzgKNFa9K6BHob1z2JeWEIpvn7U3XmMElEfFbWiz/ppG4wW5ycuZ6bXrQvV9Wy'
        b'aNup0/4sO+E1kbk13uU6gakdrPzoI7hzPmg9TqngqNAGbggtsVNGAas28VR+00vfG0cI2izukDw2iaD4ANzmNjGaKH/GGxpP8dVJoGibJ1e4e+0hCdzGTpjjfMAaOA+F'
        b'3kSC+Ww5dhEfCeSwQyQPNfQAp8WLE6OZzqStLWU6U92Xy1XDECPckKZakeaI1doEC0AUUm6MudwQImAQ5iywBTu556x9sZigPA0BGyTQokVbxp04T5pjP9eSvzrkWxIq'
        b'oB0SCXR3SVyg3oSrDaAEhTjKdwZ3cGxl9lwuRWdKArfy2/3TufSNxfy2KEGZaLeYFVs7w23wcTK9RphH/CrRXZElrb2fyHAXzZTbtSbHfZxtZ7qTRewuxeuG+/Pk3iQ8'
        b'hBNqF6RCUQH7RcT7E8R4BVJ3OWabpNC+1rhsszIzZeQTK4Jx5fVmav/5PadH3uD/YuHu5Yfq4VFRKw7Vv2AQ65v5ye30hKpceKv2UkZoZeF6LsuzPP1v+HdNeWWRvJD3'
        b'prO8M5pciW0+3JX7JJJdnj1GKPmbRIldrVv28zfZD+U3yHMtszooOpxPW57LIS3h/PKslons57LKOqwIODcaFmor+lJTrCrkq6Cw7DcGXLYaVS4EV5XeUOV+uELeXyqK'
        b'VznMXLY8vFdfgXfNL/nKU/2Zu37JS556eKWn/z9L9y3H9/OoYa5HrjPrpb65U4JA+lT8fKcE1m8/w6HusnUwE78hv3iO+ujqYKRE8Og/WcEy71iwQMDfAOKPBhSkRwNC'
        b'7nCAHQ2ICjQKNAvEBVoxWtKDAUmhbK7gqkymAjvhPS64IsMdBkiuyQQs+8ynRH47QLTKwUBQijTcd+W5AOchD5d6eJcOg5/ubV98YuUloXSps3pZE5ZSn3VkeNKqjswI'
        b'diZhxNUnYk7Hp59API9znh13rNqr+eLwzI24i0CcH3VxHLxXnB8SO+KgoSfxnujVHeNG+5Ojom3tjSLCUzlPLj/h1OiU1Oi0aK7tb3bIzS2g9Bzj8dRDqx1AUPOrp8iQ'
        b'urcXnfvMn/51/t9v6u1dvb7PBr8MFmKjggP2pFh9+LLorCj6ka845C43U8AR7EvMYAEf2B0Qudy36sGcjVjoH7DCyVqEE4JM7FOAsr0enMEtOnnWYo3L4tE4DuIsZziP'
        b'67FSLMHuZE37mJ5w4kux1I4oBISacsVYWCmWAx0ZB+i3Csf9LOAOO7AtxFsBzCPq68Pp2eMMc+MENqwI612y/znjXxykgr2iDL6cb0+KL6sjnARNAl+BryiGv/geZPeF'
        b'QF0k0BsV6V3VC/3sNG+6/6LRNZD7+oH7CcGbpMRdZT4Im71qtIH/+lCnK39r/shZ4U9F7eEqRmFZ47byfCpMfAjtPrYSgTM2CGwENtCSwk3kIt6IWu7jxkIrMjaqmWN3'
        b'GxkfVVjmeWQxeyqrKnHEw8vSiweEOIO3VLwwx53bCleNvU/4exf3T4idj8cp4MwZMyHnc4nYjYUrU+hbwhyfRX+tK+e71N0tJ71gTwtbvej59JJw1AP1MQwkru5ppiGP'
        b'BZoueUwhBx4qXIUBuM2tU5wLc5TPmikIwpRfkNkvdZS4JvCr+FO544JJgcDIVeXVGD2lP11J1WTKgvnMzWS4rYuDCgfOe1LkzJwnssekvtSj2Mdw4Dq4yWCgMoxyT+/E'
        b'iSMWcoKw88x1Ap3Yyj1tQpDrPnOfXMYu5j/BllDe09hzRYglUODLUDGWkPFlJyRAVnqO83uGYZmut7XX0eTH3KI34Q6fxbYGH3hiiXY4D+44s0AFh+Pt/2QhSeskjWiy'
        b'809ORxyTfuWqfvuXp68d63auiXIs/nWv6pt9P5Q5JRGeUtV0FZ2qEL35A7vw4iPGJnIpY0OpxS0v1v/Zzcbb9qXsFz6cn0n+7V6vqYLCd2Q//GOX8Z+sO76zwdR3RkPr'
        b'T4K+9170Niv7ecVQ1mu/8bDyvdUX0xJ8+0rFlnvfevWTl11mP+8ybzwSvaW85rOz+tnGMd0fH76wXbggyHntj1aw/7LSr993P+DxWZDLS0nqH35Ubv9ul+pLGy8r5/ta'
        b'9l/60+f//o1krWGtcaT3mVBnrxfLYxJHwgezTN/L7fE67z71jsuamZ2xu9+uS3jXZO/ZHw0M7/7lVVvP0Ct/NUl73emjV75b0PLJ5576a6x+c8Vy6282/Priri8+HXvd'
        b'cj7qneixgt/c3PfSzRCni9drf17YpvnDufbi12O7Tta8mObZvG7yR9/75cPzTXs2GBm37az+/OCx88Z+U8o3LOfeGve/vSDOWS+yeWnz6W6DncfvKdu2jv1q3/c2BZ76'
        b'yc9e/NdLr796Pz1isHBLh+WbI7/ozvreSJz7xz+6/IXSWLjLW78Yfvf6zBGXnzu2N6/zqbaqD7hY+fmVjN8vfCk2najN8PQ10+GjVu6SMdVngZ2HlwWtJEIe96UctuyU'
        b'3qrDYatFkzbamTMWZLemL7sESAB8bslB0UDWJSMTe3r3NruNIE0UcRVbRBujfTnTS55Yv9SbXluQZpkgqzdFjotqdcWy8xbYZPAo1sXNiS9MNkUcVycNW4Wu9CeykeIY'
        b'X94sAmq5quMkePkilVyBSrvNnLm2ITlgsTyluZClIa7jClRCAZTzS1K0HyotoHTrYu0cVjhHFur5wNoCeACDXJUbGMJqz6UqNwtYxb1tcBnqLGhInpZY6UITU1gnggrs'
        b'vc47H+6rQqOF1WIqfAU5kRUMRHLL6UKicaWZT7ZtndY2MvPjyGjmjjOKdkElM7iTd8MdH6lLR81OfCod8/ibErnBUGxhsMaPD4UkOUoaw0JWsBaamaU5hX3ctlw8xmfF'
        b'5+ryyRpCtapIguNHuWHowzyWrzQmoWin1iayJXHGj+sFssNgyAKbYWw1WxK78AE/2huX9/C2JG9IYtN5qS2pHsvZpMf1gi1c7ZYXe1huRobDDL9kzQ7atCRkx508umjJ'
        b'6Rn/h7Bd679ouj1mvykvj0TgDLi7TAl8IwOOTDhrZc6E4otG8oV8WMJQwy8lIj6JqKJYUSgRyXOFeyTCxb8lQlaGUvquiC8tyZt56tJPfNlJiZrsJ6qLn+lPHa4vTe5P'
        b'MjbWPn6xYdmceKtLlrd3gpZsIGZyLDOz1P+vl9hMsqwz66UeOVvrBLM4lBdTyHwjW0uQs/2tVaytr1qAxbAwJzYcZ9EqlhZDpxwy9RJwAd8yZFvxifVFnLUlZvZWjPKS'
        b'bSV5JtuK5V1wWy2edtG2epRdfyk8louq/T8OA+ffWUw/w7+3Sk5Ja6P9fDwNN5SnxAlxUePMAKNHPQP899ht38EMnnPh6SwaJC09NT4p9qlD4PPePIqNeTyjH//9c11J'
        b'kffjMKiP7a4VSFAfy78qVpaA5yHu2BDaSDAuQJXxioxL4uDoID4VfrYSTJBgP0XqbdkpdSJ2cYevUAzT9ngLCh/l4l86CneDiviEt8fFadn04GG3TqtiY03Yrn3g4vVX'
        b'97nlvPDOEQ/JzFuK+gdkNh6ub3rJcsYDXkvyauh/4+onrS2ZKpvGX/lxzIHwfe/+429jrp9tjbKu8T8X+70bvoXvZ3/rrY8urYv6y4Bf79XpSz85Vvf3XSHnM87dzC76'
        b'S6/LP16yfBjx2enfnU7YtvbkX1/48z+FNv+zScnjCzMZaWWW6ywIFtpPPoIUWI093JdGOnqk52LVVlx5sYEJ3gE5AC3uy1ML2EPRIqhoUuWdf2UwkEgt2G5f6RInPenM'
        b'l64mEH47gPe1swaHOGf7aZkV91n+I/WxTLqrZnC8tkK++z2HfCcJb8A73/iiwIsyXp4rzpa57jHxs7LXFRJ4pShaJoG/WaZrEq/c+04rZSwnXk/R7y4rS+v1flPxKsjZ'
        b'+OdVBOxXz5Dldc2MT2Eemf9WWbYv+p8MXk2NjIu/IM32I01LuyK/0CoSdD/v7Ei8zHlH4s+lJEYz/050lPFTpa10Yo/nuaFfP0s9E8Gq8kril8Gu5aZj2VYowzm+luTq'
        b'UVLsqCpCVz4e72bFe9yUiNIs6UWvGGOWpzT4hV+8OFkxVth300zmZc3IuJjECMvwpJi4PR4Rv/cRC/J+LjfU524m4VC7DNxKUkpfHvse5MN78/MIHo9Cr473yqMxNVWe'
        b'56fggdwjnm9LeHTSeRzz09loYGZrIMtUsQ3HsJQVgeS9OJ6+5y3XSfG/NwzKwSg2Sr62Xpp6OL+ti7SVJloknudgWntldsdnw+O+2Md6WJFU/fRKtlyZTfLRExynhdKn'
        b'xufnNPUfr8JpzzTY1F+z8cj4+QUe8ks9K+AA3FenqHuU7YLdqeVu13HXmLjweM77zcEyTnhw8+IXRf+/jcSfUZKn7qOPqotXrljWOkUlHaFow8psc+oSdXV5kbZQXk1V'
        b'qKioI5Q3kGUnE7S8W77UvGYt1EwyEspv0BZywUtk2w5HSq9wJ+PIslvcIoHpVpkLWJKZ8b8idvcC8j3gNlQ5JWPzdnXIxxm8v2a3HWRH4oisAxZCJVTJk0V3G29sUCFj'
        b'Mg/aYQiqDxyATiWogmLhWnwIM/hQBRodcBLKYTwcprA/UIVd+MzFEae98BBGPeChOz11C4svwwz0w5D1Fejygbt7r+AD7JPDURign3u7oAe6sDf2vM1mbNyB2diRBK14'
        b'E/txHJuvOEEJ9JLtPabrfn6vvw6UbMLs/VcTbLEMH8BM/F7MP+tusCHc4JCDt0yITZa1P3SFGFpBNU7thTnsY/fLk2AAK6mZaQ9CNefM8ZZNKJaqYG8UjmqRkdkOVdhJ'
        b'P/exLmw/Nh22TYCySByWhVaYxvxkWtRKbA3AYRi9eA674eFVuI/1gVCpj51nT2IddO9eg3c94P52KKW5V0K5xgEYCYDcrd40gGls2gMjV3HwCDQKsRea8AbWQAv9fSuO'
        b'bOIm6Ly4XqwENTCJbTaWZMpOx+1R3EsSqiDSELLdz8HNKGq23hfmzSIPJW84hOXx+BCbvbA2RA+GL7nhLIzTNo06yULDEbMgmjermpSnuIXElx52YCf9a8YXCqAlmBaj'
        b'FuotcWaP82YnE20tHD9Gv2jJ2nrSAhtxQF0LC7ACpgLT6LeVqoobcYFl4sIxGKHhjAqw3jbaERtPQbMNzGtim2qEL5THpjtj9lGsXw8loXbyBDhnDbVgNhEW1kJ+LL0+'
        b'lEKGeMMOQ+yM2njshNM2rCY6mIXetHAiuTpsClTWP5WZ5JiFk4an10GTH3Tqn8QRLijsjjxNZpLoqQkGjmCnK5bKQ8FBvLeddrIOBu1pokM0xBnIDaZNuGXlQhRRfAnG'
        b'dddiMS3RfWxXvSbGeSxyN7E8n1EiYkWpzkA+3D7qBuVE9sowjxNrrrjS/vYdhOz1hJcbrJR34l3aoTFoFR+E3sjwTWZQESeBEqPr26BnT0ZmnBrWEjF24h1a29KUsOPw'
        b'YE0wNLnSIMegG3LDscUc6y224CzegxkxjCpgzVqcDpdJwdswGRRy0QWbrwYkwiA201I8MKVJEIXgcJK3IzXRagjNmHM4mNquCob63dAABRHEejkie1+sglEremYc78DA'
        b'1ZNXtdSDr0fsdI/FFo3LOzVwmGZaQqScS1xxYxexVZH7Bh+Ty1uI2G5BIw7tICIfJOKcxcJwrEqEeZrTQbwPRXLY44xVWdCW4e0Wj8NbscCUDIuFK7utr0P+GYUAmNVb'
        b'z5KiYZ/GHkkyLoThuAgrLumEH8SbMKEIpdc8oAFzDN2hPASyMS9KjUyPO/4BQTaRmlv0sd/NXVFb03q7zFrbIGKh2z5YGEAb3IADelBIMiU7HHvtaBvvww3ME2OVH1Ti'
        b'mBG2+GFxMEHpCYkGEV+xLnTSNJhYygu1YStLlskQTF68pA9l66m/YaKpO5eIFgoyNeRZWu8YrMG5KzbahAMa4CbtzSiJrSn5WFUvbNMn26D9xDEcJK7Lw5kNp+GBrzcs'
        b'QJ+CCVSlkUDohXz7aJw4h0XB8MDagPmrT/nDzFqit0EsOwpV3l4apy7iFPXXS4TQehJyiIEWaFo5NjiotTXAZI0/mQRVMldxKgR7Emnx7vjDuBnOykBDhAl0nE/LeI3o'
        b'UZumNk/06AS3GD3SuOcsYDLDHltOSajddryZFA7t55WIL+t3HbaEXvUwb+h3hlKcptWax/q1REcPyVargnEY8YT8k8SueRvxgYezsxM2eEFXlLoi5hG99hBFzcDNTdBk'
        b'dIEIuF7kDPOXBXbWnlh9Nt2Ctm0CegkqFcM94psq4rnmiJOnk0h4dFpicwIt930BEVJxMDXURLvSBXVYc+ogycUFC93j6afPQLsvDbIbK3DSlJij0mWjzSUs1VaAueUk'
        b'SwxSd1ifhjJ1EXOtFK7DZBInMmtUL0MjycpeNx+7TONIGPXLuqIjPuMOJbqQE0NzW6AGekk25do5EwE3yJ2DMugLhWqWFqzfSAWq92AjGX/p9EgOssm0YSsppT7IVhNh'
        b'rhNJkZ41cjCzB+/pbWGB7HDPBh9qX8SupDWXJXGJmA21xLD5WKNGa9VN0+vFeZg4TBvaqYHFIeviiNxyccwVumnV509tJdV0N+SSIZFvxzknrAgjBVZvBv0XiSNKrWk3'
        b'Ot1sSMwVEWGS4jy18+wurDRNwDtX96lm0gBzIZuIuRMmdhiZRoXDBMmbGWVtMlfvYa4y2e/QahNIJAEdl2kARXjLFKagAwbhViZ2yq01oUW+j92HQrbBQ2xRPGROE84n'
        b'ddJOWrv5AEy4xx6lvZyAG2khtKONpA/b4H4mllyAhtNy0VjnFONuzWn0W97ppG7yM0goVLCY8r3uusFYD81noVh0QQ9aiMBpBYnAofVEAo1ygYz/zcleh7AoSQUro4/L'
        b'rTuDwwZQz4hrGzF05yGNKDmOrs9CDe0EydkkDl3M44gFTgsPrg+DdjlsPKoohDEWRFxOTNPACmSNC0jWmqzB7B20vA2GWXhXDu5Bd7S7KTR5m+2HQS1SB0369EK5KrbI'
        b'nTNMIKJpUiN2bLAxw4dB1h7QfCQLawyh1Gv9blIDM4q0Ng+xRO4w9IcxdgkXppxiWOh2Eo7g/dPHSWAw+TtEkoAASLIdNGu5WhzVxJEQqAw7ADcOwj11bHe/fpIWpn13'
        b'lhaUBviEQP9mnLy+bn8YSY4B2o/Bc7Qqg9B88rIQ6w7Zwlzg9izV/ZgDzdDgHEmK+QZtcqeeBq12PnaLYUEDq4J01Q1I8xVrQ8Vpn/BA4t0HtkccEomLq4Oh2hpyfbS3'
        b'aeOdRBhyJe4rTICaLXhjvxCzZQ7Dvah9UHsoHiac/eA+FO6z33/wmgE2Eu2TXOyh/goE50gDdOKYLLQTExTpELOM01LdwhYbeACl+sSjLZvh/lWcPu9MNNtAeq4c6/ae'
        b'x043EinZUUcuQb57MtF/+1Wou7qGqGoq6jL2x+phAwnBDpITxY5YdlzDDoncK7DbnXAREXSP0W4aw2361OW6+5K7OunEAwYwEcDiPGHy8k7i+Ac4sJ+FXpLALYG23esZ'
        b'HkuF0hijrYwSsVLbhZMEnTTMbGiNh7oIjcwLvthCvUwSV9VDVTyNpp8QQa4IyjNo4Uv1s2h6zaQ+B0lrpgVDhzW2Yreev0oAKYq+BB3siMZaT9rfXrx/Cm6H0RDvOsNd'
        b'4uFCe7iJjMkfYF0QNVFwJu4CU0GYc04fJ1JIuIxjnsmhE4o4unbHoSPrNkFVRgWDzT0ROEd0TVNYAhAWOCs8h+UEIJz2WMDMdhi9oLTVXi6V8GvDoWNYtY+mAu1utMEP'
        b'qOeJVFqkaSaAgjdCvi3m7giH29R1MYymZDkpr/dmWagisI2euUuyo/76Bsi2OEa7PSvZQ1KwDubM7Vxw8DQhtFqciyZ0WU5KbID08xSSTMu9boU1mkSzhftOQ7sX1h11'
        b'JcVaEe0KjUHmhDi64b4D9VZOWKQd5tWItW9Dhzr2e0D5jktYpeq7IfYcCbocOeKO1izFUBjd7HDAR89JhQhsCGpVrdZJaM1uK2ra4+SGLfLiQ3jDmJYxezMRfY/GWtLv'
        b'5dTm8CnMPQ01boS1mpwJdpBkInyA90KxBVsdz5O0qoU+0iPdhPJHaZeEh62OQcnmJNLSzTDkj7knsPOUAxT7WPrSsuVC0f6Etf7uRxiCKT59DXojzPBGJGRrZRlhPSmr'
        b'ypM4nUqUU3cEB8Ow0Go71IuIzNp8sMCNiGuBRPpw7GmyRypIbBfp69EST4ZhtSMWQFvyHlr6OzaQ70w0042VO0K0Y3Ya29n7R0B3GM4mnyKp3O6oprjZdre2vq0ZifRJ'
        b'ZSzSOuC3FYpxYTO0BFG7VSpEWg/PQfHRY8Qj905B+xbo1Y7CsSTqspkmevsMcULPyeg1JHyqYNgaRpRoOYuxPhaKNsD46ZQzui4wkEgPDUNjDImHRnECjSs7gAh+0hZu'
        b'OcGDraRr5/DmdW18KEhkcax1AqjPeIMjShLaTNpiThJHlA+IKC/hYDTeuSxPsCdXK4vWMGfLOsK3k4bbNbFanYDk8aOZHlBxfcPmrAzID9c7HKp8lNR3F/uB3F0k+etI'
        b'jtBrTgw2XVFXgaFLtLf3sO2YixKpymlYUAujnhsTSNX2yWB2BtYGRsODrCT6qjniNEGZuxx6AEIP9+FBPFH/RIQe5qVuwB5TIoxO4p3BwCSsvGJE0qGFgd04GkDhGYdz'
        b'ekr0RiVJjjpajhLfEAJ6A1cDrh6Pu7RR2Q8Jr3Zhz0YS3H2nnC+p0uqWAGPdCphNSnHWhGm1dGKTnFSCExXBfrYKJjga4Yc3oC6AHpmGm3I4oBKNhUdYRVT6dUEKNKmR'
        b'nXITWi/heCjR6ug2ZQsvEk+N8eqHEi47k+XUuY54dIRlR1trKqG1rN1OaLNCVxtqkow2HCRmHVqHc+4kt8q4AOVsvJfEpY2rOr8ZezeRaTuAN69Ck6kVib9ZOeosF3tt'
        b'3aNtLxmfiiE2zyF2yGW3A5sUoWoHlp+1xWafzcQMpFywU0sjLYJE4DwOnMCB08Q73cZEhS27CbPM2EIBzqYksWPpSUIozVd0t2uTyKx3ITk/4biJhl4RB2UEGmTwThBp'
        b'y0Ii1mrnszgVpI95ElLSI9HU920iuCbBpotOKSfSdA7THo9tNCeeuQ2VUenQ4nwJijdhkcwpLEmAxr307DhMEuysx6JjpChKCJm0aPuoQpvXluv+RKRDeDczJJHAYn2A'
        b'88HdzDIbtIcet1TzUzBDZHXLF8ay4rVjSAo1qhGNT1ph15Er7lh9yJyo4q7uRszZ5pMQxA7Lj5jJ8ld6HoQae3vKCIRkQ28TkG1XiA+5L44rQgF/x+isDrtjRDKtnY9X'
        b'aZbBEW8LkUCoEugqIJQxLs/FCxnZ72EXBoS66i7st/3QyXdQ4xTCnPdCgdBnj5cAm21wnvsCWj0PYokl/V4Tij0E2JqIkxnuYoFABsf1aIGqsYyYoslVmdZ75JrihpMK'
        b'UOd4VC1ci5RSpTWRQietUC0D61vwpuchX8hPcNYxI0kzgz36maSZOqgHdbeTJLwroCUCbxFUIe7FNjvmbCGzu/KSdcZ+GNBhAO8q9ESHY4ESdKSyNCjVsOAM2cePYK0f'
        b'7SF9T4yYd5A+dkOfgMRrQZAmobfmbbRVt21OmBDV5awjU2DMPITavSXwpz7zokmijpD2raY9JvMm/grkWxPVVQZCxRayEsaJEk4QdKncQvJtGKrsyUbKSw/1hYfeROrd'
        b'pCNKiKDGDcleyiWbrNDe7AoU2BJyu0cSYpSUQTuMGhMOvgONe6L3XBDjLbloNWzwOAv9djibarEB587g4AnPNdAvdyUj2jc1lMRnJXQrMJcBNBjqYw4t7CAJohwSjb2n'
        b'TlBbpbSedSHaCcSwczSEil001V4nA8XjytgaGcaMLmwSY64NmTDZtCrDSEJ0wQZKxTgaYu5vg3nBJNA6HHF0CzFMn60FsAsd/VDhyN1cLIHsVN0MCemlijSaQzc8OHCS'
        b'cGQ1FJtDqxwOxWOFB9S6YHsQWVOlZLM8kFuDJWHGkWb71+KQPNSGQW0qMcgDM9UM7I9MTcVe+qm6qkLDLbI7FkwMPUxiuNIWx/e7X9GIiYIpUxWYVsU2D2KoG7txeJsn'
        b'8XQ/5CNz6hSpkeU+CTkG0BJK/A91Lh4n/E6mHj+hS1iokJT4nO4erEndZksCYvyCmORCDwxZ6cBCRhwO7iYroMJcC5t0mQgnZVew/Tpx59QuAopFzA1l5hdDyhRmtkFz'
        b'OhFUAcychIIk0t/dMHCA+HbY+zoMh5Kl10pbOuzlwLld5sWkX9pOxpIV1QO3dmNbhO7aaxaEOif9mA2BlTFwHzu30x8L+MBIB+qi0yzT9QhuDTrj7BkVzFHBeSG0niFk'
        b'PSPMGBCxurhdJBcec8qQEL3rbOSqdgGHdGQNLmJHFDFHTgSJ5bHDJ7HYS1vHjXTeAtSnsoK3StoyJ0J9jpIEqLA1INKpgxF97N2h5228FyayyBQoCNbzt4p0kyONNkuU'
        b'cf/IMc5DM+6/gTpqgmo7Wph5RZrFeBLJpE5SKg/icDoDps1gBEr2WhB79GJLEv3j1oWd0ERajQR8BSPXLhgzh7vbk1nxWQccjzpJi53ve0yXgU0kKd1zXEiIb54YO8eQ'
        b'eGjMnV0kkRhinwXJ3Qns0joGdzaSUC2HZtdUH4LZrbEEPnNdmWwdg5yriYTv17oSVujSV2NuLR/sy9TcrwgD506TGC7l3QBpkcQFFWc307BIo2HHNZIGc4bsUJJMXOjz'
        b'PSNIwIJ9iSR2Ws7siyW1MIEt0TTCqnTSw7n0BsujejsyCkYSD+/GSV11eLjpBBFEgzb2uFmzFTHHft1onIsn2mEwf4BMh/lUfHBGZq86Nq7dgVX+KSTWSrWwU5PMr+os'
        b'wlLZsHCe0M6kC/Rr+Ju62JqQ9m3H2hB57HBPpkVvNt2asd4sXuewu6YGtmtdz3BQgfx9Ij+i+wEiwiLovUbCoCPjmAeUnCRRe8MCZrWjiTXniTemrx4/R8oyCcrFyHKy'
        b'DxHQmwu/QAK3xelKMPaEWJFkasJBM7i/7wwMb9jsSYKhmm0wbcJDkm2NRAbDGjSNB7hw7bAPNdq9C6rOrXH3p77vraX1uL8fZt1ICheEymx0SSdgMMjZttdCQrmz3iXT'
        b'9jh1Xgb1Ozcw6zbkqJIQpjSx0A9GZK1g+KSsDvQjScHJXUQEI/bH8AEUW8fbE4lWcu6SgY1WJMiYh65RwxLySK4RjebDKJkG+PCiv5UZ7dYgzju7Qb8hNKoZGtDal8Jk'
        b'FDFsl8teAfTrk2gZ2AyN9phtTOJuHIaCsS0Imm1C2M17T2iJCiGlMHKM4ZNO7AhJ3SojjtuLdduw5xIWWcP4pkDMTdoO3Qn7SDF004T7CLW2HCKZA3M+WGwZQqqj2ZzY'
        b'+aaV8fE47Nm95kQqPvQjWqsj5ZG3U1se2hKSYJQEWCu7HO8nRyywkOJPJnslkUspdGfSpEldGWDvNqjNIIVS75dAxERmS72lShLkKRo54LB9PDZ46ZyDeejPwGZ7uOeW'
        b'Sri2n2zX0WPrYSFQsAdvqsjjgphGme+7BuZkmFukyx56Y3U8oO7gWmMfA3syuoppUjjsSKJ8nmhihJhghgjhwXkyPoe0aNkbIyIZ48TEmZJkLROdcos9rwxTJ7E3wd8v'
        b'PuYM4dRxVRpEE6ncQUUc94aSSKg/ZqELZGPcwLIE5XAcCoRbWq5hp7Ow1ct33Q6s3I5j6+JOYbmtiOFWEkN5ZES34bzPpSs0/5IIdVJfHfhwvWQz1GkdxfzIYPcz+3wP'
        b'EYOXOmFt2p4onNtI4ugubWoJWYayRGE4pBRiyMkXJrpraCkbInfCGE5tNCPGbcCuy8Rv5TBqSgZQiYYcaciBlOA11GlJFD44fJ52pwwJIFQowLSmozUJtNbLWtfVthJz'
        b'NZK0eWiJhaHQuvsc8WS9OOOAmJU+J9RdtIK0ybadFot08Q5WuqqlQre2bMJWZmnQbMZIHtbtEHoFejL7KRJnI3FChRhriibfYemoihWGJ9ZJiMabSIOXEoIfyqTlrt0Z'
        b'qBAEd+2wKZjIu4lE9z0lZpDDoGEQrTdZ1Vm0/uU6mBdwiOEfLWpvOHQD9Njg8EFzJFDjtY5WqWQjtFlvIBat3QvNa2h5mtNI8/RFw1iwIdF6k+jozrXQpW8P2RFQtI2w'
        b'rxMJxA1BZmtJVFTFYa4CjEWnXif9lQuTIXakWCaimRQvkUs/bAv9yrtpmW9ho14oLdScJnbGrsG78qaZbnvP68Lt3TDic4UIq4cUYDc26uN0uhf2axLcuUW69H4cKYNM'
        b'xf2ptI+t1EjVxj3p0O0o2YHDLiZwx1kRW9JxSD3mtB70aqifh+o1WOodSw3lQI2lnI0v7SmhDVqZWYmRb4rr7qMJeHcjSYd+YqSWsI24cIjEVz3c9nRzEhB3FBNrEvwm'
        b'4VUF00oxWLCLlDRRacl+GDVQEJI4mAk9RYKvh3ZlllrN01hznHR5GXTJw804yLfHfivSAIXXLkDVnlPI3OSdApg447iWhMo9yI/fSszWpwcdVsTpjcQVo2RXt4Qp6O/C'
        b'+7pQH7jHO8WdFOgduIPDEnrlBkwYaduTxdEFvW4wIGNIu9kCC5vX6BOeLTPHiitYwZam6CKMi1O2ONJvK/dC59bjOEeaEus0TPaaYOseaIgOJtIpxLpU0kwPLp3EkZ17'
        b'gyA3MZ1kY421wA56wy9pR0TQqifG4X0oi4DR84SgKwnDldFqjTmQaM0zsSercA4LUh28Y5xIEBRicZYVLe64spCIb0CZoWPayMaotEtXYdaf/tkFTT5kobfBSIoH3j3O'
        b'6cVJvL/3pDPUm5LOJOvX3QknvQjDjShF7SAw1xBCzLEgF0GILXujvEWGRMysiTQaB/FRDvEnY6QHeN+CZHEDkea0PU7qEdoNxmrF+P0waILN+7dBpZjUW7sKe8JJPZ7g'
        b'0HxWrIcHYYFcryB7I8zPTCaE/QD73Gjzx6FNAeft5BJJ6wwKsSMA722+Ctlk9dVuOaSmFIB1UdzB2jDz8l/Pghq4x/xZXTB3lJWpjCa+nWBmGPZAr4cONl4+uvXENppb'
        b'LQ7sxZzrZHdNGZJqLDwFbUGEtqasZOOSbfRg1EOR+H6IXdK1oWXNTyQGeKCG7achj+DAKOmW8h1YsVaO5tijYIV3r8QRAsyPuAQ3nUgnl0O7mCwmBWw+pndIj6hlyFRG'
        b'fR3OugRBhaqrPAnNe5jtTlhmkIm0XXhXQNq7Fm9tV40+DHknvU33pCco4gP145lbSb4TLnc+dxhupWC1TQCZ1AyJTtjHXSHiKNoKoxoOLMS7QxfuKcJ08OVEc7yzmaTW'
        b'DDZD3hm8d0kR8w8GEFPkkV1yh2ROJdksxrTY9evxtrKiOEYXS04kxJ8OtcUmb1XhQR16bxgqZaFKQ5eYrRpmEpQ9Lbbh9Hrm+CS9nQ3zBjDDDu76DNeRzVca4eJE+L11'
        b'J61FB9xdZ5UElT6biCXKyfRJy4DGnbQH+Z44tVeJEPx9ggUtBzN1sVP5mgzNoOoQNGkpXCFuq6J/VcKCRVLYZWg1JosyV3OPP0zpQYv6bifli3jDC/MMQ+WwLxCq4qAV'
        b'BomIyo+GMGcp9mUwdxft+30SvaOkInKx2xoLr4Vi1XVjUtSEgY7R47f9aD43juN0pjUBM+ghdqkmXV2oFBKRcYIYsg2YNiE82m1H01u4CjXrsSqaYPfUeSKY4Yt6RFeD'
        b'V7HgOhSRJCfscSOYpFM7dme8TUjJjyimcYkRXJlj6tZxUsMkwRJcjI6qmWAFMcFxkyz6ukU/NlJBD7v195jQDi+w9ChDch5h1Ms0gaQekR1Or4UF7NudoESzysP2dGCn'
        b'vzkn9kKVBOr0SJTPX8RGb+gU08deuBdN6ubONZKMt4ifamg/KhXXY5cXSdJBWv5SrLqCC3B/rzYW2cF9K+w08cWSRHbO5ck8VVGHaXXytpBMKVKW4EC0AZH+5GUjYvO5'
        b'Hf7JRHPdWjY0tqrtOli3aYMZNm85SIiB2GM/EcQD7TicUsYmR2PsUSHbMe8U5O7HOVcYVLhE4qWaAFAtieYuAVH9PVm4begB9UpkIPRsV4MOtx3QaEtgIU8vcA3e2bRT'
        b'VhYLj+zHIiW8sf8w2cX3rQljFdjjmFoKTm1T9raBTlusdnNwZblyoElCjN9Nsj4/M8xInV3mmiNZMAc5RkTuw0JCZtcv7CCKqz5KfNuM40occcyFkghfOLuFpEILFiTT'
        b'yvUyaTC1nfBHdUwcdO0hsmZe+Gos1sUJO7JsKmOhUBY644zgjgRGnB1wmlnpmH2EhNikz0VS6g9tZQlbd0GpKeZa0uKM6EDnVahn6SAKN7LTZJkrsnaxgdRyzV5VrCP8'
        b'IHuRwaBcrV1JZPQRpr9BgqISerWw8YDuJRZYEUCr1wT3zlzYDANWMH8IusxkoNGYIFZzMPSfJaNnGLqsQgkEkeK2c0jeCfe8tp7Hzs3Q4AW9FtsP4oQMaZV6T2Oybm/j'
        b'+A7Scf2MUxoDNA/YEswetMaFIBOSb/VHw1RDrwYahBDxFGL2Lh/qo2GT0wbXqwKCmIVnsZ8o6460HLAkA9pY9pxUGdq3AT5/jr0ml/rMHpqzAvAOy/vGJ30jnm43E3PO'
        b'JU9FbW/mWqKdubtHQNvUgLW816kXRlO9WRIJoantdnYnoyaUrzvcsm0NSx0gEQi9IH8/e6caW/mbcO3RIs5Htl2Dc5HladHgOFcY0aqsN8tyi7UGNvSVtxP3e2zGDoJQ'
        b'PvRKjLG9AG8JknhfWAvJqTzeq6YUxrxqG4OlTW2BVgUsMaM31NP9BSTWi934YRVeZsDVV1YgPIQjLgLatErI5XsZVE3h/HBGsZwfrgpbzIR8lTN2Plvq7UWtBUKuBTVC'
        b'i9fD3xMrZMdWUoccwdBa5pIjuh41Ex7i6gFxV9lSEkVcLOZ2nU26L1xdLzATc7/O3iLmfy37P95bbZL47EHKQdJn7X4U1rn5ssDPTORHTXEX3+JVBF+K0gZZLbcJ46vV'
        b'x/3XumnnxV48LRQn6b3WLBTLvpb18a48k25TtbpyO6+KjZvfNrtRb/nqr18JuCZwsYv9joXWJ+ohZz52ev+abWzxdbV/Wd5X+qg98oXZ6Ws+f/t4+yfFUz0fvJZQVjEy'
        b'1yfveO/jQz/7YqN+Xpyf8fS7Zz+8P/2wPln5W5t+tu539ed7Hr6k8u71NyfWaqmUvz0Y9PraA119p/J6W/7X4Nf9245t/lbsrObbtieKPN2sE7UUdv72O/N+85WHzN+f'
        b'zjtm8vHvzigeH9KNyvNSjDd/pfNKXoZsiM3wrgUV+9c9X/f808ymH92TSe7vfrfBS87Bfp/jb46YeTpOqd/7sa/VJyGX7Qe0qqr1/xj+aXt9+heHizwfeNxT+9dfd3x6'
        b'f2v5u40flV+AT/N7TF951WvaxKyxLuS9kBpf+xotxyKhcpVBus93/qx88TunN8d61n/6fdcX6rp/YD/406qh7zp/d5NjnrG2h86VqqHPPC/7CpNTYryboursC3bA3cp2'
        b'i7v/mnUx0LrV6TFy5/2kH5+q/9Yf7FLe2+J0UemvA02O+PtbZumZ//P7X6aHKf/OMPrNHQ8azkx1fHLR2+RllyMnX2zpndmVFR67PUfzu1Vr0yy3FP70Jz/58icXDKob'
        b'NjquGf1J2IKVwo4vXa2+bPB5vec3VU6vxB55aeff4x98XvHpF7F66R+9ceQHYXV9zd/J+p8u241dNv6xjT80fO/yBs35IhnPP8dYh1VmnDxsFd54Ss55dH29ykd/UTz2'
        b'P7G5U41fDiUcfWPPb/MX6i+IzgbHtmbc3mqY/tftx0P/pBr0I2PvP/7F5PVdbfWq9m+ZXk4Mq+5K/KLrTbPE8LWOv/j2+s/P/1n9RePylFKtlnd8fv6+Wszm8k+cPjv/'
        b'1x++IHNd6+J7vv98/a3r/wo5E/TbpFd2ffadf+q89InDl9/Wcimpz/j3u1oL2ccz/v3B1n/vXZD9ac//a+7KY+K47vBcLLssCwsGQzAmHHVivBwm+L5qF0yzLAttXerG'
        b'iTUsy8BOWXaXnVku4wsfhGMN1PWd1LaMCS21Az6w8SX5vUit1KpWJatxJlXUqErUVlEkK25UO5Xd93uz2MjJP60qUaH9mJ3jzbw3b+f9frvv+77eD3eyd+5W7j25NTeG'
        b'SqxIIMzTVwEPkbE28gw5IMbq+hzw28Fbz/nlgZUedXIIp1NmGwmSfo5/NtOQgSRYfTOpbfNX6BSv7mR81hy0mCxkhO+LD4a8O2LJsHyFZ9I7SHGn0ahutDaU0fl0r1Y8'
        b'uQSfam22GJjU9TyJglJUkI0sRTeWKC2xzSF8JR71ov54oyUGj8e3RDG5JIM7ECeQMfQsuqZSS40J84Zv2heFSeGtzaCwR0p3CgY01W7RRVHCZMA+h7sKzU+LNeJ3uEI7'
        b'HqPec9ttaFRBYWMzuUSFjHI9zxVZjy5DifiygYRHG+kFLyED5MVsknPOVGV5XpNlxP91F7ni2Z1kOuuQm06frv8voHt9i6LX76oTRTr9+i4BzsZxS9hMEAt5YuBiWSMn'
        b'8EbWwBs4AxfHJ0YlJlpN1gxrdKIhKUaYk8Sl2rnsJSyzkyvm2BXUO0jgYSpuBqyzpbKlC2AdJ66J+Apx7lV0ids8vSbVkPaadQMpm+eseXBUTun0vjncIi6XvGxcLrNb'
        b'GKPrDFweXUP+yLqzMMPa8HB6KrjRamRT2Zkv4YnwMFjzdKYzH/wbVP7ZzO9XZr9jzFqHZPXGoDOvoYls0Akg5Am8/w2GWFQPbXeNh6QZA3gADMxQDxqIZuKq8YkX+Pm4'
        b'u03efKybVZJZEkKkvrY0bK/E660bx9beafa+3JxoNGYVmaxnUg/c5iauoJHVNkdCwmeDO/4+9+MRNe3Mlhtixz+uz/vD4HDho+Gwxyufe/H2/VUf3Qufvbhg9IMt3ZtK'
        b'jny1PyPl+OSDQ3duxdzblHXk0z8ODfV+UG1avXX5J79Z/Jf3xn/N47dszs1fVt8eLn/81W8PHkoLeC68+8Ugv2GsI/mvawdzqi9aH5T33T3d8q/7BZ7Vn65t+siTdfj1'
        b'efM+bDn8OHzL/Empc+Xyt1/9fHTr76897t+WGVvUtd5idt87WhMTXVB/D69b888V63eV7F2BiiqtHyc1vDn05/SUq+8l/+BPmTj/88BARvDB/V3cgoz7ext+mPq7d09c'
        b'td/iJ9//0rzvC3Fpx+tT9prcFynVovM7JE8iMWtVFeXaRjNmdIFkY8McHk1BpyhrN+Pb6LqjJbsqH0/AfjBXPQHf4NHpN/AeXZfuqkISSXojgPwP3/GQG9HYnshn4MOV'
        b'lLKLevFxBrxWnNFZuIsxCJwRvemnJBHc/0Yr7isk0ekmYHJdwmd+lEVJIkXFeNCGDywEqnA/i/ej3YypgEPH45dF9NPwQbsNTb4QEfESKlk0noqOUUoYCatv4qPAycuP'
        b'bI7bTNKiXr4Shcvo2Kzm4BGHt3AG0zxOHyZH8XmzraKTHua043CuXWAS8UGeZIMj6Cg9dTZkcI7yvMqlxexWPMFE459yBhSuopc9B00kOVbhm68Uk4MdER2zLH51oE0n'
        b'q03hUy+TPNhDttud+uY4fJ4vgt8JdKWqHjySifvmN4JJ3gAJl7/Pous12fTMebEwoYKkIpM47MwjuU0Ri35lQ130wHWpaMjWgq7m4zCw5JtY+FIRd9GQA49VomM20r4n'
        b'JRKRwGmdpOoCM2+7gLrwoW06k/0IGaJ7HHBZpPKk0RlzboGdw4Pt+CCtGxpGU3nKjO0x9rJkDo1vb6D2fS78Nho34wvx+LICVl0BfKmZRCQWhknPETJKopNwWG/jM/ja'
        b'SkpAskFZICF2HO3G1ziStNzC/TplbyTPivsS0ImZrrKmpSo4NpMw4ia+4UDnFpLb2+tIQu+AAHMV1AqFCytBluC7G6M7Q7hXb9C9i/PNeBxfgkBsiKSoRxg8EpWg12i0'
        b'hKTNF3Xm+zJ0k4nqZPEw6emnabO9hPdkw1Z0rD0f1LubI9FaWkhApEN+i5YxtwVfseXDLxu4p4IDl0LG9BKH+oo99PTluLfcVp6f58wvYJnY5I61fAwaxtd02ceTeKrE'
        b'IeAxcmscBaQA8hkiVz+nmCfB3y91I47SgnTbq3mLgOQJdwQPLsenOHx+Wyvtxzn4ZooN0jQHswj9Ah8twfum3YsWzv5T/X80NsydhXDkmXNwCwFjXEyEfQmSadbIki5u'
        b'FksF0SJLT4RdIJzGPQGfYCPr4/9zCtn0n7BYJ1PRWGGRxnslX1Ah45kWpYYCXkkTvLKiakKd7CboD0g+jVfUoBZV265KiibU+v1ejZd9qhZVT+Iq8i/o8jVIWpTsC4RU'
        b'jXd7ghrvD9ZphnrZq0rkTZMroPEdckCLciluWdZ4j9RGdiHFx8iK7FNUl88taYZAqNYru7XYjTqR0elqJAfHBoKSqsr17WJbk1czVvjdjWUyuUhTbfEyyQfqU5pFVvyi'
        b'KjdJpKCmgCaUfa+0TLMEXEFFEskmYHZrCU3+upXLdRsPsU5ukFUt2uV2SwFV0Sy0YqLqJ2Gir0Hjf+ys0MyKR65XRSkY9Ac1S8jn9rhkn1QnSm1uzSSKikSaShS1OJ9f'
        b'9NfWhxQ3NWDSTNNvSHVCPpCfehaF6e29MNgKcVonQDvAboC9ADsprw2gA8AD0ACwC6CJ0mMB/AA/AQBCYdALIAOEALYBuACAvxoMAOwA2AewH0AFAAZx0AewHaANoAWg'
        b'EaCLKtkB1NITAb1uDyx1AzQ/pQ1CRzJNR1RbHn49oqJ7PDLWk/4iuT0FmlUUI8uRoPxRWuR9ZsDlbgQFMqCzwjaprjLXSMl/WrQourxeUdQ7LqUHmqDHGnQD1eBnsKZn'
        b'OgB+zolZM64hdz/kldaBC5wCdrwCIxiM3H//EUqq5iht+t/y6yap'
    ))))

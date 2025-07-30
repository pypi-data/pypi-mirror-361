
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
        b'eJzMfQlAk0f697y5uCEQ7jMoCIGEW0XEA/HgRhG8FQIJEEXAhHhrPUsQ1IAoAbHiUUVFxaNqtWo70+32/idu2mbZbdfudrfHdru0tbttt9/2m5k3QS5b2393vw/CMJmZ'
        b'd+aZ45n5Pc88M++fwKAfrvX/l09ipw0owBJQAZYwCmYXWMJRcrt4YJQfBecUA8A5xvZd7azgcoCSfwr7zw2kWgs0zks5OFyg4A1Nv4PBoXbKYbkwQMGfDxzKJYJvVzrO'
        b'nzU3Tby6RqGtUoprysV1lUrx3A11lTXV4tmq6jplWaW4Vl62Sl6hjHF0LKxUaWxpFcpyVbVSIy7XVpfVqWqqNWJ5tUJcViXXaHBoXY14XY16lXidqq5STIqIcSyLGFSx'
        b'SPznRFpDiKmqB/VMPaeeW8+r59cL6u3q7esd6h3rneqd613qXevd6oX17vUe9aJ6z3qveu96n3rfer96//qA+sD6oPrg+pB6cX1o/Zj6sfVh9eH14+oj2oDORxeo89OF'
        b'6sJ0IToPnb/OXmenE+tcdDydm85RJ9I56xx0XroAHdBxdUJdsC5cN07nqePrXHVBOl+dt85JN0Yn0HF0jG6sLkLnXh6J+8l+SyQHNIQNbfstEgfAAZsjh4biEMnQEAZs'
        b'jdwqmQ/GPjJuHVjPXQzWMQ6VEk5e2eBRkID/RKSxBNahMx9IXPOq7PG3j3hcwANfJzOgJKdhSi7QjiVDLWUWOi5GjaghP2ce0qG9+RK0N7NorkwAImbx0N1SuF3C1Qbi'
        b'lKgVdgdmZ0ozZagBNeXyAWoJdUV7uHkO8LzWGyeAp9GlGNRUTNLwAY/HwKNCdFQbjKPi7eHZaPpYbibaK8nkVQUCD3SAC2/CTqSTcLQBOFEt7NmYnZCIE2SjffmZfLQX'
        b'NQK3UO5kbTiNVxdPJdGZuTRWjE4CV3SBGw+vofM4B0riMXgVPbkuT0PS4MJQEwMcMzmwNxte04YREhtQN7rlhC67oWc0+Mv12mVIj66ugY1uLgAEjuXZLayVMLQ2pQ7u'
        b'EyJRY04WauICLrrDwMPw8AIcGY4jFzvPy4bnI3FT7MlGTbAhn5AE98bmuXvLJAIwZ5bdZmkGTkvIRvXwOrqErmB6cvL5gL+ZgWcWopOoC+qtRT2xXOq8IDpLJs2VxTDA'
        b'2YvrCE+gYzgyCEc6ww7UCE8tis6QRqGGHFIlJ6TnoAuwAT5bxgzq+kRb1/dh52BCPe5+PGJ5eKQK8Ii2x6MY4PHshMezCx67bngsu+PxLsJj2QuPYh88lv3w6A/A3BCE'
        b'R3kI5oFQPLLHYr4gIz5CF6mT6KJ00TqpTqaL0cXq4nTxugRdoi6pPJGOeDx/NDgNG/EcOuKZESOeM2JUM1s51hE/atzAiN81fMQHjjLi57IjPshHAJwBEMatPesRtaUU'
        b'0MBgD8IGAMSVV8wLnSNlAx1kDkCIw+IENROisirZwLAVPID/i+NmTyy56pwHzoAqRxzcmurL8wz+CI+D9yO+4FyLXxc5i6lywBHLphuYXjuc3i+v+rfqRudzgAZvjPrC'
        b'rdWNiewHIbwPfP9Rtgz0AW0MGRktG4ow5zXGzouMRHtiM/BogmcKI7Ny0X5pTCYebzpZVi4Dqt0cpqiRQTuTNB16Gj2nqVOvXaPVQL0MXUe96Cq6jK7hEfYMuuJm7+zo'
        b'6uDiBPdDHWxKiEtKmBA/PhFeh708AO8sdUDn0YUybSbhhOMTUGN2TlZeZm422o8ZvwntwTzTQJguNlIaFSORRcOLsHsCNMCeApzDZdSGmtFBzC6H0AHUuhAAnzgXD4d5'
        b'Q4YgaVcf0hebyRDkkMkaD0IGDzx+OZcOErz0NPCGDRKuwyjdjkO4IwYCZyvXOkhGjXv0IOGNMkh4eWrSy6rS+pt8zTzs25v/8uFXU4+E7l7DcCcYX7nR1LxdPn5sU3Hj'
        b'fKUL4syu+uNr29aP31Ff2scZB1NW+qW0+8Stv1OmDZjvghK6HM69f0pxSV+qjuNW+IOj1R6a1zsk/Af+pJ/Pr4rB/bwHt3MTbMzHw28SAy/BW+jMA1/SFXp0MzI6Zjq8'
        b'jbuhQcoAAdzHkflvekBachzatiRaBq/C+sgMGQdHdXBkAD3zgMwbW+fk46i9E9DenHg+ECxh0HkNPM/meYUUhieOs+ipDHgeN+cWZjY87izh9XEiJWo81MFDR0NaR7xt'
        b'27ZvvVLL1TUbldXicnY9j9Eoa+VT+7halWIjcTgk9XLsfL0N9M/mAE/vtoktEw1JzVNap+hmWkRe7NejKR0p7amdqSZRpFkU+Y4o5p4oxiSKM4viSCKftpSWFIOq29Mk'
        b'ijGTT8I7ouR7omSTKMUsSjE6p3xJekxthx2JoM+hWr5aqcG4QtnHk6srNH12xcVqbXVxcZ9TcXFZlVJera3FIQ8rQ3q4pESM66N2J4EehAUJ8YR/NGsI8V8T8mdxGCao'
        b'H/yQc9/VR6dqWNW0aptTP4fPeFqcPHQTGyY1TbrPc9uWvT13V+62XIu9m8VepHP6uh/P7cKhodvy2d8vyTg75CAFPa4p3NllnNEG5lbCMVwrx/AozwjKeQM8w/+P80z5'
        b'cJ5xHIVnPPK0JMhlAWythjs1OXw8us/glX8hoOEBExb5oJPZOJiRkIWvG13VepLh2Lo4phJuR1fwAsjwAXwG3SqmD0wtdZqCbqFGEj4LoINwp0rrhcMXoZt4MX8a7XLC'
        b'QINxB/DWXHSSZpWObqBn4ZXcaBIxD6DDXuiSlvQxaipBB0oSo2MEgFkK0OmsQJq+EvWGoG0V6ADh8I0gF52AT2nJwPB9Ygk6IADjUQ+QAinaESNxoEWjY2jXsskcAFvg'
        b'TYB24w867MrGnIUGdH0TB6CLEQA9jT/ohEZLuBRehh3wPLwlABgOANSGP3gub6GrOzq+FW1DOAr1JgN0HX/w1+fYqKOoZxm8xQURsBmgI/iDLqDdtGFyN5YiHIGu2wN0'
        b'G39Qiz+lYQ7algZvuQF4FN0CqAt/0KWttD5ecvgUOsEBS8UYLTtFQoOWsMM4eDp3Phe3XyGIABHj19OmSpkHu9ABO0zsWRAH4tDdyWxTBcLbK+bh2b0N8x7cD4rR3pla'
        b'OoHths3wPLqiQVfWMngN6kbbYBsThm6tozPoiCWAjhqC+w7iwVwBNoPlGB1sZho4a8FFwWammdPkgGWKSsriLJ9z+zgxcX1MGcvCRP7BDEz591vH1CqVpq6sZnXt1I0h'
        b'yuqyGoWymExLMalVNWXyKs3UmIcJFpGng9n5yeg7if0Y1nS7d6/sDukOMbgTtztETQhUiedFczQ92Ney9drhVxOOHDvwjOHMgfGG0N3xuyW7J+0O3z3+jb/slu2esnvs'
        b'7sTdq1wrZHO34oWh11m3EG1Y3nNEOuulG+ZTtbFlvLPlM7vz3v9YISuLbOF8UvLi2Z123fUO+LP8fwRn/J/k51gedN18eXfoghRB94VDlw45tMnGN43P+ejag5frLstK'
        b'Xvpk3Ht5C5wnfi4reeHUtZ2T9sbvvrv7xIG3+G8s/yg0bdnXgsTaa7heM+MYUIOXFDrgtvOjo/F4bIiRoD1SgNeFHk5ingNdbsLEAgwmkS4zJ4+PtqNW4AQvcdCRENRI'
        b'V400eG4MXo0uxEox0sYwX7CCMzY+5EEo6ecueBMDVQJJ0B6MnlED7ImSZ/GBKImLWtCuIpp/3Ea437ackbUMnXDEyxkeI3sldsNWltEcjR3tXbLesD3c5zSoVzcO/kKX'
        b'm++sy81cvNx44WnZxc/i46u3twSFdnv2Fj7v+dATGNLP5/iE9gPs6Ob0C4C7R5tdi12zQ6uDLs3i5tcPuC4yi6dX25yWOYb05pzWHD1j8fY3yPUqvcri63fUocOhK6yb'
        b'a/KVmn2l+rR+LvAJYGNxZsHhR5d3LG8v7iwmREio0+yg5+nLSJaZLZkGRVe6yTPS7BmpZ3DGwoB3hOH3hOFd5d1ykzDOLIzDRAgpRQNDE3+60rBj8p1kxq4wxSxMwalE'
        b'nmQdbZ7UOsnoHEgHK8sldn2Mps+xuqZYg0XnSqVGTfpT7fOINmYXQesqSKSfIW1LQKBmLbCthvl4NQwgi96POL/oktjmIAPnXSdzH2NFJCiSP2RF/P8ERTqwosbXVSJA'
        b'2jjO9ciCz2ZtYAUIQVUG0BOpQhtUEl2yBsymoQW1QiAGIDmufEfWZ+EJbNLx050AnoPt4yZEeX7kN4FdTt384cFEuAsdjcMlwwOgdEal6pvgLp6mDkduLyrDs1bT8SPb'
        b'G44dePbAGr+xXLRS/OQ2z5eq4pa/vr/okOQwf6ZP/NNxdol1CTElzwsOMZ+vTL7YeOnAmYzA7kPuh/vyxhUG7Dk27nTvybirCZljzPGn4k72jmksZNbIXnaTjneuvKB4'
        b'rZxjesG582NwMNx/T6dewqFTCGyHd32iZQSRFqBtLCjd5PkggE5McnQxOiZTGiWJwWJMlQI14KVWzFuxeLKE/+g5gQ9YBGqdEdzLKpVlq4rL1EqFqq5GXYzh58ggOjs0'
        b'WGeHOg4QinQafWLD+qb1htA9m3WbDRqDpiuxfX3n+u4xHVsMWyw+gXqtxcOrTdIiaY5ujdalW9y8CRsHGTRHt3Zs7a4whUwwh0ygQWxioUifpp+hn9FqZxhrKDWsMZR2'
        b'RpiEoYRFw4yisK55JlGEWRTRnXRPFGt0jh3CqtwylaLPrqxGW12n3vATOFVKOHVkbZcO5VcN5ld/wpE/4vxS/KomGrnRF/qNVj6l6oaHkh4zCo/+8uqAEQow/ig8OpPl'
        b'0UJ3D6DT5pMG31w2r9jKjpcj3EFhbRoAtSXOXN5yUEhZD+5ABthAVCrx8JAGO1ekNHXEND6oSsW9Ob0k5+rqDEBB1hQVOp+I2yMhtA4kzIdXacreXA5oWulKSqtKqsoH'
        b'FKTBq37oRiIeuYlusBUkTq6kSe+tcAHrN04EYG5JlTxxBaAgDR6sgQcScS2SUJcKJAnRBTaH/YHoUCLuiPHjisD4sdbCDs71AovWFRKyAkMlVSxZqqLFibg5JsCeMWCC'
        b'DO6mKXcsDAKpaXWkrGVdCxayKesmoB2JGHVNhD1VYKIyg6Y0F4qBMX4baZjUb7wL2JTT58NbiXjMJk9fBpLHwn005V9nh4HK/BZS+oyOdWvYyQvp5lfDK9gzCYPHvdjd'
        b'u4wmvi2NBOaiY2TUl6YtiAcU1mJx+FAGvILbMAU2ov0gBZ1F52nyJ9yl4PWpvYRezkztBGsztjmXEKl1xhyMtWdEwFNsi9WjVtSuwa2brkQHQPrkXDa4czrsIGLhTPQM'
        b'uglmxmXRPDZiofqOBjfkrMnVYBa6NpOG2k2FT5PZaHYoht2zw+AdWusnwqYRUDrHCV7GCFyfRwOnVQcQ7s2YBk+BDLh/Ky1sLLrMR6TWmVOqQCbSo2dpY6wbhzETqV4W'
        b'1MF67O5ZxzbSTti+CV3BJGdHzsF4/DoWZggUR6fRk5HoCiY6Zz3aDnKwPN9Cm+OU0A7MnIpFfHGJ9C8TawArR9yCR+ARdAVXJhc1o13YbUMNNL060hE0YckTCEucW51k'
        b'7NAqZtzQFVzJPHQVtYC8SLiHpj1eHgFqVz1F8i69zp0HKCVB6DyWgK7g2uc/Aa+BfLgHPUVTr10YBVqXXSQ5j9nvs8jaMfsq4ZPoCm6WueP88F8aTdqA/UlKJenyzUcS'
        b'V7IjKTYC7SVq/XmcaWAe3FtMU2attQfLoiJIypw/Lq20jqRbWDB82olHlk48ogrQRS+a+E+OrqDHfgpeYEucBRVpLAXV9vCUE27P+eFKMB8LWNtYAXQv/u1xwu1ZKEH1'
        b'oBDWw5s0j1ubAsCnChWpRaq342Q2DyxgNs9wwq1ZtGweKNoML9Ckn/hiyWL5BlJc4L/So9mmRCf8xzvhplwAezdg5zTqoGm/XDEWPODsJcw/475IbuXoC1vRbSfckgvR'
        b'wXDsHGGrcdvZGySHLifNvjleu5ZtHc0i2OpkRwThXgVYVMhOPuETY0HJxJuEgjFLHPKsKeEVAWzEnsX288HiVAVNqfEaD+qY3xCOVJetWcxijNKpCUCneYMQVTB3Qwkb'
        b'mL4qHtRyXiBcPuZXCVuBhENp3RSxCDbiFl+CLiwHS+At1EC7YiO6YwcbcfMurUMdYCm8Ag9Wff39999PduGBpEJ2Wnyn0o7NetyUCeAjp9+TihXwnuADVfVyPV8zD7dr'
        b'4O2bu1sy8+Fc4a8r3lvl1N1948SNHTdi798p++PE/pnHrz+R09RgF/aC/h8fHXspIH5Fau12p+J7H6fL/EXFX2x946+vX/zNmw+K7jaPmfbHybnjVr5SHdt/xPXCP5aG'
        b'87WZd7g7tha8cjHurY8vvtX67rdTp0Qu2r70w+81R48s3eFy+iWdOKrpWLbFRfZp2jJL41T5NA/IODvWx0kDX+iuff1G5p/2BayDNyR/yvNfF1X79JtXL1U0TVn16aST'
        b'u/1ed7qySBhTmnmjyev9qLd3/dUirN6xe9IHu5davD8rWXijfsv7jOvuOckX1uxcs2N+5+1zgk27un8dH/W79/95+CnvlE3fajg+dUduFcx86our5/QXUhL2tr52Z/k7'
        b'T3z1m7fujlsf7PvWjdTtxZdjbrW4v/3tc0fXPXvkw8V3/rZEvuy9C8KnUr7f/a+ZHa+aequfzPKe37xj0e5gbXNU4OtT1n7J3F5QcfTTr7FYSMRe2AE7x6NGaR7ZKdiP'
        b'9gRKGSz9nSO7BT3oLpUcUQPaJ6PYDbVmWxWKU+DVB0SNngJPTs5Ge6PR3lxZltM0so3jgW5wUb0K6SjwG7uyDEt+TdmZ8LwvFhgFyRw/tM3tQQggEugesqdyPiNPFoka'
        b'Ajdh6XE/F7gjPRf2+sM2if1jiIYsIiJDRywWP4REfa5WNKQtKybyy8Zh3ykQ7OawQDCDOxgIxu/ZomOB332Rt15tYPTq1olt01qmmURhZlEYgXqBFp8Afd0QXIiRkp8r'
        b'AX/z+rnE5xtgsPrEY7usvsjobqsvLrHX6kuefKOA9aXNfL6U9WXlvqxmffMXGBctYb3Lio3yMuq9T0vhEx8thfpoKdRHS6E+Wgr10VKoj5ZCfP2AfKVF0Qi2KOpli6KJ'
        b'sEDsiQuzY/1+gYYBf2hYV4HNHyXrLrX5Eyf0qm3+1GnPMzb/TGYO8/LAtxwmnzHOHciskFnIkOKtX5czJQwhgX61JyQU9Duwfv8gQ6nNP3Zcl9rml8b2clg/YANSUp8f'
        b'MyiAOLrMfmfg5a2b1c9xdgl6NySyW9Q9v7u0e36PrykkwRyS0A8E7vHUaZ6DUXydxcfXEN+sxQ97xd/3DeoKeCc04V5oQm+SKTTZHJp8I8EUOsXkO8XAN/BJ6wR3+XUn'
        b'nQwx+caREEtgaNeM9iy9g0UUbNhgFkm65/d69Cy8J0oyipIsAWLD+H4u8Bz/9Z9FgVR8eOjQwafX9nOxH0P3+yIffZKGIsyJaeKZ/uBFf8eZkdwXIxjs2nTeXDyyHy0x'
        b'UAX3IIFhApmXh7GEgiSsBURaIKpuLsO4E3Hg0c4vKtcfdIgG51wncX9UXiCbk2CQvMD9j8sLFY8j09ux8oKx0gXYb5pAYXk7d6xVXnhviSP4iBtLEdUGv+ns0j5VMHY5'
        b'vJZok9Ph1Ymq5KLfczREanvJ255sKx07sIFqD9+eTPWHr+c4H2k68vprvtuPN8WZqND+Yiv0dE4iqsdjBzM9LjhFQj1skhbwX3zGefoVw0pf4+ulr7DyOJYH3nffuHKx'
        b'hKFzeig8hS5Fy1D3lIebRHVov4Q36vxq2+1h51Z/duBo6tTasjotljeL1cpypVpZXabc+ANxdM5dDNg5dwYPePqSXZ3m1NZU3UyLmweegJMaNjRtGDQBW4R48tEX6Ata'
        b'7Q1JXZwu9y5OZ7JJOPYxhGlBH0+DS358lkglLPED1O8Ywh5pPIbxIFzwaOcXE6OTwWOI0bxhYvT/A7bgjsIWgjxW2riIehknNU6BetBl2ARgOzoto7zBi0gClWTH3K9T'
        b'+qZ/NZitEnx3g6chusbUml6WC9Y81KE3Tdc2WcxPx8Vw91x88jWvzxPj6xK0xxtOxSmvbFO2Fxh2+m2L8jUW8RJrTzHgg02iT9ziJ6okHLrDiTqw7NTGKqFAWAkd87AJ'
        b'baMq6knjeawOykVNtFA2HVQuuiHhDh87pKYD3OA7TO/ykBceGUM5IdfKCXOHcYLIh4CNriR2J5QuCN3p3em9vDOZPZk3OGfzuvNY5hDJjCJZt8IkSjSLEo3OiUNHf9lP'
        b'Gv0zyOh/JL0NQ8Z+/n977D+OqpevY/7Lqt4Rm5+jLwuFrMg02ZVYnWRIp5Xk+ESsZ4Wd52fxibEIUMwoySmeZdXqfubBITnNDXQqcX5jQjlQ5R11YjRY2gTjXp9L9py2'
        b'HyDa2zMH4hsZwaH4hLie8l2fr/RL8Vvl+/a+V30bC1P8fJ6f1fxCgniFy4dPxyl3fjzmqby/eP4lKkbwZEy5uJEf9arh1394xf5qc/huv7eeihJ/Vvrpmr8rnMvv53DB'
        b'h7meV3zXW9llNebUXnguJ1f6BOrARGUz8DI8j56huD98E4OFBrQvNj8X7c3LhD084FOggfW8CRzVT9DaulQr19cVK7TKYoW8Trlx6FfKJqutbLKMJ3CJtgRIjQHS7sKe'
        b'xaaAieaAiXp7zC6G9UZRBP50z7yYfzbfJJ1ilk55nrknTTNK0yxiSXfaMRd9psVH3BXfskW/xeKL8VWAQWVQdTPtVZ1VJp8oPa/fBWfe74oZUZc9RCPLI3T0OVQp5QpM'
        b'0oafsn2SQVhqaIX2gyEK2aW8HzUn+EVtCliFrM1SlPwIbEN2F+EmHmspifmJoxPQ7RM7nX25gPIUdxSDAp7DKFyCQ3gj+Ia7lWflqVHjHr2mOIzCU3wWam2ZkwgUYU2k'
        b'2QtuJSWx3HO1ALMU73U+mF4ifcV3JlD9uW0hX0NUHdoH7x5+dQJeTFYPLCbPOI93dvJtmPtryytLFIvgHv3fFbnyZS/xChFP1MBcXtl+H61snzxppeHstu9i9vk/KS03'
        b'VLloJixa517sMlaUHrHQ8TcJXbfPvb924fbVkvdnWkDhrxYjyyvbVzotao2cuLPqY8Wvr/KLeG89WHLI/1CJ4E1nsH36mLVj260bsvPhmVV049QOcOBxFXyaKYIXUO8D'
        b'otyM18BrVqPIujRiFgmfwesUNVjs8ffInoRuogYpfnhvPgPsURMH7kLnoIFm+wTcYY9jdLF4keMp63IZeBedgeeoMD4Hnh6DGnNhD+4nuCttLTMHHkXbJE6PK2gPH/RE'
        b'GWeTuwd42rlCOYilh3xjxW4rR9fygCigTdoibY5pjdGlW0Tebcktyc0prSm6mffdvPoBzyX2XZ8gQ3lXqclHYvaRNPP0jD7eEhiOOTeXyFXercmGNS1T9FMsASFdki7C'
        b'6tKTUlNAjH7mn3387wuD9C4GRVemSRhjFsawX8uOVnZUtq/sXNk9qXtSb+GZaT3TTMEpJuFks3Dy5w58X9cHADu6DCwpegbq8gdNBg5kMsAzQBapo6BMW1dT/ugFlm0e'
        b'BzonlAzauFYXkFlhSJu0k5Tb2UmBNEsNnhXCCd8/tvOLCmIdDnGg13XqUEFsYIeErrr8AUGMWImCcv5/EXWOWHW9R5khQtgZ4lzaa6AV80fJlpWq10Ot66tXoBhMByD5'
        b'fm1d6pHVE9jAvVrWlnNu2QbpP7M2soG8RY7s/mpIdZV5yjg2sCnGg27a9ufWLPsibB4beCA+EGCkEqmfrwy8lhrJBn6SMp4CW3FpWYGftIYNVEvsWPPSxK1V4WtUbOA6'
        b'qQTMxaULEzUzgEMKG/hhxVSwGWPQ55nqAuPGQKshanQqWE/M2x03JbzvN5cN/CYzBdRhOu/PrVPfXhHABh4T+YE4nGf/mPXLJim5bOC1LClYRB53LR9zaWIiG7hyPLu3'
        b'DJZurnrDcSEbeH1FGtiGA59X1XiMWePNBr69kTVuvb+6PGdndRUbeCbbGWC0EPn8WLm0NcGZDfwiMAAkYZLmhq1c9pQimA28J8OtjeveVb6hYLZgPhvYzZ8HusjOtuuq'
        b'qDcirY38xlQFeBkXBOLrxr0mWc0G/ntNBXgdP97rXTk7L3kGG/i+jw8gOxXbFlSkbktJZQOXVrkRsOV7f02F9F+MdWM9OXsjeIBJ6g1fteCsncBakGsCIHoPY3yZx5fp'
        b'vmxgSMQYQAz/hHNqZowJGAdUae8t52qWYX744v/4H5w/uRrFOT8d/toTEfO+ze57c9KsmuZo4d+EXelPugq2AG3szfJXW56eIz0TmfanVyOj0oVfBX+T0dxf/w2PX/3J'
        b'p1OZ5P6pF9b9tefwcy9cqxVVtEX4vn1fOu4I5yPGa+WON0HXZwZUWFvTvq3i34c2PfdHA6+xsql2z8HXYsqyyzKXbI78fOrBOfOzLnnXTD1c+/bpynuWjb8LjP7IJS/S'
        b'S3ysseluxcs1Hzh/6J+54W9nKv/13aQ8yYlln4ZUvrDofa+sqDXXMp92WvralFWzcuM+/92qz56aqj1zccXv7h87E6je/v7fW0Ll5YuW5cG7Fxx/X5JVsHDuYbe3OFt3'
        b'f2O/NeiNrV9OTi+pntN+y3TWu/vEb2UxJ3779zkHnc923+NUzHsu6G+/RvZTjRva//nV4r+uiUNPdgS9+PZT/3x/c/rtz+N/5zW+7Mt/XXz7nT2fLPf48vRfCqYw/yh8'
        b'Irrx6Hd/zj8+7+Kxzf8WHPztgdC/N0u4VCf8BLpSQ/TFTwzHlrwJcDvqYOW4Q7wp2dLIDLR3MbyUjRkcnuNsgAd4dImrQm0F0fjZGQVRDOBpGaK8hnslHj9ziXucVZBo'
        b'c8SDfwYthu5kqi+VV68qrqypUpEFZOPIILos/taqja7lA08ffaK+jhjz6Gb2C4DQU7/F6BaGPxafsK5Cs0+UURhFVLNeBm6zEzUR0ssNoc1Kg7xZ1ZVm8go3CcO73bvn'
        b'nfHq9Tjjf4NjisQrHLESErrr5xncm4sM85oXd8WbPMNMwjAS7KlXNxODJ3eRXt7sjbPyN6hZowX8REGznSG+i9M+sWte95hjC00B0l733tJLPib/SSbhpCFP6WZY3D30'
        b'CkNh17z2xSbvcd3uJu+obrnJK9bkHstGlhoSmiu63JuXm9zH4BAPUnQE9ri562fsWadbZ/ELMnjiVTutS90949g6k1+s2S9WL9AL7j+MMPlFmf2i9AKiG/bS8/SFhniD'
        b'3CQUm4Vii9Db4Gfw64pvD+wMxM2Av48M8hz+DBuQQCo9xiwcMyKANLYPzSShPagzyCQcZ8v00d9tWazBDWkWhtL+Gp3W4c/EG0rZZ36AsBG5/gDxif4U0SSPSIr7zkNk'
        b'Q2Bdafc8wo0e4RZPL4ODwaErtN250xkPET3TzwUiz+HJ7jt77s/fk29IMzkHm52Djc7BJCR3T25DflO+Lv/+mChdriHM5BxiEQUMwVH2fbwNSrn6h6HTw22dksHspCbK'
        b'0VEY6AJJTbRhFEEt5v+oguI/oKqgwtVgZGI7cvclAbysmk5JjuSBJRgWOQCFPbXY5pRzFZxdDkvIwTuegrsLDD1Mt4RPw3kjwgU0nD8i3I6GC0aE2yt5WKzjlnMUdrvs'
        b'h0KsJQ46sJ5Z4jgfYAHMoc8uTaFQKzWavDLBoNqQvqA4ax+wKV5sh+owGCRHhThUZKTHh8rtKSTENDY4DoOEdhQSCkZAQrsRsE+w1c4KCUeN+2n6eX4eu/d+eCE6Nx8Q'
        b'/fcN1AVCIwB7oEM18RxX04Z9F96QavfFu8I451mrF2Ye+WyZLroWHHJMOQ4/CnzebnpP++UPWm5knLzqeKj04/DvP/w+4u59R/ek1+22886b9O5d99vcW/9+snrqPkPv'
        b'x/cD9p1a9I/d1z7Tfa/miZ757MqRy/fuvNavem/8JudNX4397rm1n1wJP9TRsexLn9jet2bdW/HH9z769Bz0++qgRRfNP9ERVbcj7jZTxQ93dfaQONKVb84CWTZsWEDX'
        b'PtvCh7bDK+wBjjtC9WAjW4YbDy/NgCcf+JHIp13RreiHpr9VcDcnER2A16kJ3kp4Fh7JxmLiDnJEjc0b3eLABlX1A2pBr02JjpGxGwUnM+s4cfBYJl2uszLhEdgI96P9'
        b'2TK4H+63A07e8ARq4KB6LFlepprVqUvgNdiYj9dknPGkaAk8ywNuDty6pBwanSZCO2i0FJ7hAYE9MqAbHD9cK/0DcphNhJ6pgo2xWJ518I7JpOf4gAd6mosTPBdPU8B2'
        b'2B6Ek8RIsnJl5KhbI17xr3PQdXQe6f7Xsu22bYNlW7vi4mrluuLijW5WJomxBtAl/CXALuHr7UBAkN7OIvLDU4x7tMUzoC2vJa9rgskzyuwZZfSMwnNiP+C4xxvq6D9L'
        b'QPDR5I7krkVdK3o9egt7l9woMIZNNwWkmQPS9DNtjyedTjmeciz1ZKrJM87sGWf0jLOIQkgB8bYUD2Pe9Qk0LOwqM/lEYbTwjk/CPZ+E3sQbdiaf6Waf6XqeRRyh57W6'
        b'WIJC8T9HS6gE/3O1hITjf85kb9tp0Hzt1Mctq9KoyemzPl6Zqm5Dn31tDTGeVyj7BJo6tVJZ1+esrX64Z/JoHRlp0hL6M0hPtgo7I5qTWHBrOgArFLNysdaOYaYzZM7+'
        b'37m/1IRPpfujDuPBM65p3KHiMmObgDzoBLQZrByIogejmbwzTJ99sdXQU8L08TTKqnJiWAbE7AkG+9Qq+epShXzqRqGtZWwhLox1ZdwGumf25G4DtK9+Qvm7cPm4TH4x'
        b'6UwJoyaWwYPKVmtJh4wo1hWn+NJarGeP/08vtpIt1qHYNnoeu2i3QUUX9qz46UVXsEXbFbPD9bELFg5q6qSe1NEKHlhrsFhOjy+ye3F4mf1/qBMZbSeOm6d6r+JtoBmH'
        b'gwRv/e3wq0nUCvyYbR/h1ZfpTsIOv+SloOafvPdd5ll3iictR8et8/NToewUzfEThEg4gxibzH4DKn2VZtAG6kYvW6MOCabTJVm0CGdX2gPfQH2dYWZnlsknwuwTYRRG'
        b'DJqA+LS3RptV6G7CoHN7RIv2iAI9SFeSqYbOJXL7/wYkpGO21SEKnHVN5mIEQn7wdGqP5zj5amVxcZ9jcTF73QH2OxcXr9HKq9gYOinieVZdU6tU122gk6+a7ISoq4lT'
        b'Y6tsnws50CjXaMqUVVXFxRIeZi82YPD5xod7+NMHZt0VpKlsSO+fJP5la+PYfvsdwXRmJmNJmNDPdXMJ7Ac/7owBPiH6SmPIJPwxeaeYvVN0c/BSp082Bibij0mUZBYl'
        b'6WZacKr1RvFk/DH5pJp9UnUZFq8g/SJj8ET8MXklm72SdbPvu3j1c7gukeQIznDncy5w9W5a9Mh4Onq0FPfc9ES7NXBnek6mJEsWIwCOKzE2QRcXD2EYJ+v/L3fggXnQ'
        b'/SFQVzAEmLdyW91ahfjPpdVNxSnnYJ/1t4dzCvPYuQGgTIH9OALrMSC2nZwXYjjM2+UwDHTzyE0bBMArBD12p3C55wb2OSm45yvscZzDiDg7GueI45xGxNnTOGcc5zIi'
        b'zoHGueI4txFxjjROiOPcR8Q50TgPHCcaEedM4zxxnNeIOBfcBo54HvTeZb/ElW1DBRY/enyGCia0pZyxEOQ7Qixxo7n77QJKN4U/zh9Pa+cGdq+WCK394tYTMLRkRQTO'
        b'kxz84SoCR7S6O80zCFMcPIJiDxoXguPEI+JEttJa7Vrty7mtvJ7QofQoIrHww7HemkD63VXnVu6gGDuCAk9aShguJXxEKV4KLgUIEiyElVF48G2E42DNkjWUvQhlSAzZ'
        b'81dhobiPR6aQ0WaMvDI78PCHnDKga0Qndg7aD70kBS9iDngZ4+KKMAOXP5BGBToBHs6udHGzG0W6s3cYRV7DIfYjFjC7rfbWxW3UuMGL2/vf4BYaUlnyk1mtqlPJq1Qb'
        b'yX0wlUqx3No0KgxF5dVl5EKZ4Y+k1MrV8tVi0kwp4lkq/JSaPpo5Iy1PXKMWy8UJsjptbZUSZ0IjymvUq8U15SMyIj9K9vlI8rBUPCMzXUKyiExLT88vyisszivKnTGr'
        b'AEek5WUXp+fPnCWJGTWbQlxMlbyuDme1TlVVJS5VistqqtfiaV+pIPfcEDLKatR4mq6tqVaoqitGzYXWQK6tq1ktr1OVyauqNsSI06rZYJVGTA07cH64PuK1uM0UGPmN'
        b'JMfaPGT8pFC6iM92a4+teStrqhR4eD3qYSumZZ+3fsFtND9flhg/YYI4LWduRpo4QTIs11HrxJYkjqypJRcAyatGaUBbobg61hKxb3SKHycfGzJl87J9+/n5sXCTzY31'
        b'/4y8hixUA1qYQcjOOY9eVIOui0PJjrA0AF2IIXfZZC9Eumx67U4IPM6Dz6EGP/b00vp9UR9zkzkgrsR1wvxVQJtCnr4Nu9FZujc8F+mICiAWNWBf/nyk40ByZU1uUQYx'
        b'1c7NzcxlANyDjjuga/A0ustutYkFKS8CesYkJ3ttKdCSI2mz4wqJKj86mxwLzpmXQTUAVP5HLRJ4BszHBd5Ms0NtRegYzWW3HXcqpHUsqXLOs24wFQbwE64xQnJOQNrj'
        b'hsmV4UB4ceN01Ai3bX2YPdKRi3cwubEFGWhPjgDMQU8L0KUpaB89LiSHDYs0azBgDIEn0H5SgSfRLtVXS95nNL54MTIK7+xtoVs7T6pe+SI9s7PuZWHXRy2iDxxvz3iH'
        b's3iXs4M+7ePK2Hc/uv3RJ680xi5+dbfXfKHeXvjp/g/yPcY8cbZYuE3yyVTG96N/H11w4s75u6lcw645myNORs844t5m3iJ759W5jffu7P32+bJ7jU0fFXVPNN64oylc'
        b'JN/gcVt81/DdP4IOvrJ2xR/euDRO/W5+/rp+xT8N2jHec5794t3O8vYN7y5Y7nU2//1/++/59IM/3Tx//KbqueqgD9zGFey6WLDz3bf7c94SXLD7JP9XY3Jf+bJv4etv'
        b'tp+WfXX41//6c8o/OTdSvUXvTC/8tjL35JTM47v//vysGL/zvkVNb4tMs43le/8lXR97YrX7pfM3zp/OdN7q37oJRd3+/cfcV38T8q3DQtGRTokHq2M5XwKfc8ItLcmF'
        b'p1K1sii0J5YDvGA9z96jiKZY5YtOE4ug7fAoe5Rg4BwB2jX7gRinCIBPo3Z0Ez6bHZOVK82Ee9F+9qokf3iVVx1tR6WN6fAibCAmehGo02aXWom6H4yhIxzVx2ejfRm5'
        b'aJ8j3AP32TLwQru46MZEuI1Sgm6hHthNjfngjgLJYGu+OMWDWFKbm8lziJYI7Y9G5CImkiHcF5uNq7WPPYQwB3agPfCSHdwPdzlTFRlmkJ2oNTsfdrnKyO1NZIQ5zeOg'
        b'fd7eVMGWRAolB9FyssY5EKL4qINBN3PG02opqySwMQ/uYp/josMM3AfPRrKquZ3ORImG9uPm3QLrMb/y0U0Ow8uj6rEtG+Atm/ZsQHcWNbcu0fUBueUMHYZn4HnYaC/D'
        b'8RJ6XxbbtCznR8MrfLQbns9kN86ue/rBxi1oH84uh8FkHGWgHnUupmSg9vE4ZSNu12P5MbmEyGsMPJwLz7DVfw6eWUyIzCVnOYhhimsFFx6oSJk8jZK5Ngx1YTJtKNs1'
        b'nYu2V8zGXfEMO35uTygnT0txM+fJMnjAFXZz4bl1M+FT8JTE7ZfcjXMDVguzhz+sYIrlLhXGDMXFWNBnp98YWwgVR19nWHF0hQPwHavf1JVk8ok0+0TqeRYfcpDdffy7'
        b'/mFdK0z+SWb/JKNnkkXkbdulM6hbpuqn/tk/zBg+w+SfbvZPN3qmW0TkOK37FHqmeGL75s7N3WvuhcQZQ+LeJQknm/xTzf6pRs9Ui7e/nmsRBelTDIquou6krhyTKN4s'
        b'iu8HfHfJfZ8AQ1rrurYnWp5gycHyjZfEEhL2Tkgczq3Xs1d+1edG2I01z0WYQmaYQ2YYeAbe/bDIdgfsKcOUt21s2di8uXUzqUbgOz4R93wiunndZSafBLNPAiEwlZKT'
        b'YvKfbPafbPScjOuFy3CPsfgHHZV0SNqjO6P16fp0i5dfW3FLcVehySvK7BVFnozp1ppj51CfxT/kqKxD1s0z+cvM/jKc3KpaDAzB/xxs36xqx3FRep5ZONYSKKaR1n/i'
        b'MBopjuiys3gGWDxD9NldPJNnuNkznP1ib/KUmD0l7BeByTPC7BnxuQM/1OMBwA55uN8ZhBIlpose/w5SIbizKgRiLKYmJ+xGFah/fENq+FAjw6pkkEJz0EbVCUAVSsPG'
        b'WQjRQpwHA2pNMtw22TPMNKJ3+MWdX1TTecohFTznmub4MzSd/GKCuB+tdbM2kk3rtuihus9Q2LnEqnX7NrxwAKkTDIVRrQ1ERaqVcoWsprpqgyQGF8dV1JT9RL0kfopX'
        b'XKoqe2walw6hcbGNxjBCIxYFfpDEn6i4pA1IkPhjE7cCp1CfJvGUqOgfhvI/lzaiRlarCXc9Ll3yIY223NZoMYNFhZ9LYuAIElcyw4iVcPASIGc1XpT3H5twBWPdvGAJ'
        b'NwfFbhvctj8kdPxvCS+nhKtvAOtU9dg0VwynOdFGc+zjCDe/JN01P4XulcPpjrfRLftxMernjWR2BqC0PjaZqwmPPQNsPBZXSNUGmKzBO2Fi62gTV9G7bB9J3v8PmwgV'
        b'Es63x0cIn+lEcaARq4ZNZxqlcjW9hbdUyeoTRjxIbua1KlHmq6orcNvM0qprxHPlG1Yrq+s04jTcFiNl3UjcYLjZ8INrJ8QkxMRJflgaHu3iDn5eoYShN6yhzkTUGw1P'
        b'wl0UcfKmM/BsJdqvem36DaCZjBNIG8LJNgi7BeJvnuznHZdQwkwvysmoKvedvHuNy2/mXEkQ14xPnDEheLFPZ9Drz7e7gs5Ux7+eOiPhUWPsqd4UMu/3HYZsZ0KdghVZ'
        b'6tP8sm0ChlVcgc0yq8SCOuBTLLruhjthL2qMRz2Db49Fh9HpB2TIBtklZDNYfCLCA2cFE+vk+cjtFzuy7UFuxXKzDVlrAMW45OAn3XJxAp6+rVOMokhLmOSdsKR7YUm9'
        b'hVcXP8970f7lOmNYkims0BxWqJ/ZmoshZOsWozDsZ23IkD2FEYTUDtmKWe70X7HO2cEyNwF/j3GeiFg2M5gB/8tXR31bP2K8z1fWsepNbVWdarW8zrqSazVWbR69X7tO'
        b'La/WyAfdk126YURGJI8UqjZOKcnFaXBW+J+8Qqku+RGd02i7idYzGP1r9oHA5d/ZgbiSauNiBdCS81qxolWD9EiwB+0cpEt6lCKpAR1WzSyv4muI5W3oS6vY2/XOzDvQ'
        b'cEyUEVumKFnk8qLQ+Cuep3KmT6789XLGNOu78Nr4rsiOs+O67uRJmv+yflfMkyWCN5OAvsa1cv0bEg7l0DweukP1Fiucc4eoLSbAFipAw+PwKNpJLExs4vMMdGeEBL1l'
        b'yw+cjB1k7alR1hXbeoqCto1+ttE/IooyZKaVITcThjSKxloCxhkmd9WZAqTmAKl+psXHX68xJDVvaN3QldCyVb/13eBIo2S2KXiOOXiO0XeOTZQy0s/go0ssj+59BKM+'
        b'4szSm4RfH03xRmbI+aU1mHV9CZv+iPOfu1DqsZC969BKPPYS/ySBq0T0IUjEHBQ3BIc8LjvG4ImaKCzVE8Gws1cDi9cO8NCgrg3QMxVkJ8l2ruK/c/KKbLPkMKNsswxM'
        b'QDVqVYWqWl6Ha6lSPAqAVSvXWVfv+Jj4UZTZj9bgK1g1OW1A2wlUXFCMuEC5RqtSW9tXgX1ldWKFslRVpxl114BMf5gCTc1qm1ChwtBLXqWpoRmwWbNdVK5Uax69p6At'
        b'YylKn5GJQZ1qjZbkhwFzJAFwYrWNKlxWZp2cQLofnkVHM0q0z9MSHJIOd2Vm55G7l+nF3nmyeRkxWbnkgFdDbAHS5czL4BZI4JlM8YpStXqraoUDmLGpqMJttSO6pI0H'
        b'9OanlqghmvaHjwN4GR0sgo3oYArcy6xBz9gvtPen9/IshjsnoivODEEfoHoxfMo3TjsdhzurozSu2gUZxNSuCOmkC5AO7UeN8ExhhpTk35SZg/YweN4+KVkPD+Gc94ah'
        b'U4UcchPvdee5glnaaELSGahzISRlptmIqh3IdO5C2QI7MPcJATzpiw6pivs3sbaXzQWxh19NIdO+6fqBcIzJ9nydbXg/8EnPl5RNzs7n/OTfjXsp7xQ/x3nR8/R0qzb+'
        b'/qfx8XWcNwQdzhNX+839w8ob75Ue88gL22RIaT9r2bbSuLqsuonT8YKjaPHzT77xmWd54ZZffRdZfqWkI6s1xLB9Kzg7KzHgrXd7jry+6F2XBxtSJzf94RXnD9Y8/1Uc'
        b'OT/OBW9uj1iwabnEga4k5ehAPK7RSbR9QAXqVM1Bh+EueJZivfVwL7zgFEUuwyHrCF1tJnni9SYEXuGhi+ikPXsTYrf9tOjwRbKH9y6gu3Afe7bvMrqRnj2bHFkY0PY6'
        b'C7le6DY8RhPItixnlfCDlzJ0SWyP9s2hatgF6A7UYyqvzB2CI0/AHvr8E7Cl5OFNi1atOI+7AnXCy6wSWJ+AWmFjGTwxREW8axElPcJ1BUa7u2HvIAVxhOzHjvtuG7Y+'
        b'PpxIyCWNQ1abIVF0fTRZ18cSZ3IqYhpBo5vxouK1iHk3OMoYvcAUvNAcvNDou3CIutJ6Tnh+b9hVqSlgmjmAKMS8shm6eqY/X2aSZJqCs8zBWUbfLKLHnWYJCOmc9E5A'
        b'7L2A2F6eKWC8OWA8eWIu+0SeKTjfHJxv9M0fVorEMLV7rCkgxhwQQ5JnsMmnP59oGrxGW3Wg7D89/h1sDc+u0wNLxKMXa7otNmS1vj9itR7Sfg1ktd4MBg4W5jszDLlq'
        b'5rGcX9QGqt0hFlx0nfIzVIe8YrwyPPaKfYwI5eQsALtQx1PlzMO15Ie0Bj9ZaVDO2hTyyP05j03gyaEETh51fUkvSh++Pz4KqRJuH2+1WlneJ9CoKqqVij4HvDJq1Wos'
        b'Xc8uG/y2H2dbNVoAuWbHZuhBkYb9gJUSo3OhV3FydK7lzhR38DDuGGbIsYXvMAqSwCH8EdiCt5VvxR2jxg3BHe0/iDvYNwixEgtdwgdrIh5t5EHahl3Abc8OXGfx6P16'
        b'2pLsU/QR3AskTE60OTHidHk1UXjIrXGlKzEUGRWDEFMSDAvm5ydPiIunRiTEwENBlFeq6opHFj/QgSni2VXyCvG6SqXVRAVXmNT5YQpbpR5VfHVN3SjFqJW4ItWaFHHa'
        b'cFGwxFqdHwExA/cFDAIxjnn0NSOoLRttG4pikM66UhZl4KACKyphEjzgAXgAXclGV8rQ9iwQjk66og64DaMZcgkPPIWOzc6OkUVl4SWQ5JGLDtuyGcg+I6so0nphORYi'
        b'0dNBzqg7Gj1LhdKM9ZnAmTeOwbNllMU9HWiTcOB4xezRjRtksCE8K3f+YJG0cb4DuosOzqLkIH00ubtcRtLQHeNMgoGiCSoabNmQIc3KmQPPxmTKogQANUqc16AdqVpy'
        b'GawA3YLXhqAzUhVSeCReYrGYKZXIsvhgIzpdIHDAcudd1C7h0ltzVgvhhSL0LC2cC3hTGXgONqnp9frVE9HFaPbxXHJWox09BZ/lbEInJtI3AMHrqDEmOivX2opMGOwA'
        b'oggubsjn4FOqVxeu4tEjU8WlH+5unkIOu+w+kjwtd8+L8O2yNeCQc/e7woiSxMml8o9a/5TzdNuL6b9LCu0+JP3V2/96avWfteu5zwYfuhH09xvewpme4MCiT+pLzi97'
        b'5t1rn3y+v146JUw/7sA6ruvK8nefLJr2pctvFt3jLli0vP3cy/MDNnwoWW5S/6Hlf97Kn3ZOeWxqc8j4wjHqPP368l9V/uPgW7dysfCArvztztjxL2yNWydep7o3+f/0'
        b'+f3+K6eQhAn27asxDqP32PfCS+OzKTrhlMId6BkmHl5Adx6QV1MlwEvQMAyCsQBsPuwgGOwMn71y+hS8sg6PhwEgh4HsUwTM5YSyMGg/2lmVnZkbhSE0B9jDRm/YxoHb'
        b'F5fQQy9h8DhqGozD0CXYZFUroCPrKFQKlqCrsfDJQS+2gp3oJo1SwavFxO4gE/Yk8nlAUMUZMx+doiYS0ABPwHP0YpV89kZ9Kcbsh4EolosOoltuLPH7xpCXwgzZincr'
        b'4qbAu4US5//V1jlZKkbumzsRZGGdbzaKBsMNayAFajLr7nmpC9EsJpNd4QLmXf9xxoi5Jv95Zv95Rs95FpFPayqJyWW6Zp7MMYdNZL/QZNkm/xyzf47RM2fEzvq7w3fW'
        b'fQyTH2pJ7omkRpGUpplj8s8w+2cYPTPY/fTyrjKTKMosotvViZagKMPy7gmmoARzUIJ+ti1JpUkUaxbFskd1gsYeXdqxtH1553KSwM8w82hWR1Z7TmfOPVGkURRJS5lu'
        b'8k8z+6cZPdPYzepAsSU47J3gmHvBMabgOHNwnCU0qt+OJ/HoB9j5HPBCRQ+IQ3eoHYFvYOvmocoaNxYEfkycT4jzV/Bz9qMf2j8M3ZG2wsWvCSQZrf9OE6DYBay70rgP'
        b's10YJprAwF/I+cXAJNHGHHOYCK67pvF/Cpq0Hnmxt9X4sQHby0O3eUIJMsDrJsUJA8Bi8L6OhEes/M9w8nB5syXe6p3kWXK7jno3YM+PKWrKioupfYCavKuRGiX0cUtV'
        b'ZY+0TOizs+1aEn06VdL1uQzRaVFRYJAQ8TV9ylZZ9//MsXf3YbPFoKG2B9DTBWxj+pHhVcSl08PA4QIex0XYD4hjD1y9dAsNiV38rrLusG6NMSTR6J90I/FlLha2urm9'
        b'6f1cxnXS5wA7D4hzP3GiJWVqPzfJJbwf/Cznc74tr34eCatigGegPtkiJAdPLJ6T+/kczymfA+w8IA49gy8K0EdahOOMwnEWzxScQJSKE4hSHxBHl44TDM4hjeSQzpAs'
        b'0pkH1KWZkNMRFiE5vW/xnElePDKbpMHuA+rSF5Cw+cQahbGPzsdXrF9vESYahYkWz1k4je8ckga7D6iry8BpvIP1iyzCeKMw3uKZjtN4zyJpsPuAurrZw+iZTejJoPRk'
        b'UHoyCD329qTNHuV42rqOZ4g2uowzuYwzu4zr5zi4YLZ/hENObkQMpPIEQeGGDIswzog/CekspUGU0iBKKXZ1ubYhIuoaO6gULxdxP/gh52FRJEQ6pAvnkC7MJOVg9wF1'
        b'aS8OTjOPpJlP08ynaeaTNFZaxnZpupN67Y3jJj1faHTJMrlkmV2y+jnBLmH94Oc7hORsZiCnqUN6aCLpoUmkgyaR/pmkm0N+2aMudBNxJ2qHezWbpuXksfojBjhu5GDM'
        b'uid1xEu6yM+XeeSwi8fQwy4KzhKegruErwJLBAreEjv8Z6/gL3FQCJY4KuzIYZBWfqt9q7CVKee2Cnvshx29iMOCpJNOWM5VOIw4+EAOi7hYD644Dzv44ErjXHCc64g4'
        b'NxrnhuOEI+KEra5Kd+upczt6UsFN515ur3AffphkGC0era60JsIej2HHUYgITPJyL+crRD+SiwjT5blreKgneWlmOUfhtct+iRduC4YegfFW+OwCS3wUvtj1JYdalvhZ'
        b'0/njWH9FAA4JUARiN5AcT1kSpBPgJ4NxXLAOYF8I9oUoxDhGTL+H4u+hijH4+xhrPmNxyFhysGRJmDUkHIeEW/3jsH+c1R+B/RFWfyT2R9IcJdgnob4o7Iuivmjsi9Y5'
        b'YJ8U+6Q6e+yTYZ9MEU9P+5PbC2J3OSyJUfDohktCnyBtNT23cnaIJEnWTTaCPbrCvrkXC8nkpYEVajmRjlnRtmzDwPmHYacMhh6EUeMMVivrVGVickZOzu59lrESOg4g'
        b'QjfOk90vqNogrqlmxejRxFwJp09QvFZepVX2ORTbqOjjzioqyPs2tbKurjYlNnbdunUxyrLSGKVWXVMrx/9iNXXyOk0s+V6+Xq0sf+iTKeSqqg0x61dXkXuZ03Pm9nEz'
        b'imb3cTNnFvRxs+Yu7uNmFyzs4xbNWTT7DKePzxZsbyt3yB7RgLk/uX3oIBfjGo7GbjC2YfemNw97A7OCWUVz0Xhu5nQNRkmPGMgajzr+wzgFZzNnIxbwR77ruYG/mRka'
        b'uoVRcDczazFs2cwoeAo+pYbpGlyHh/lyh1Ep8HtIz5CYjXiK2sgn1yeSEqpxqQo71k9MYYbTsBkUD+i7cH0H1eRR9cVPDJzYU9hTfOjwfvFoWqjhh4ysY/jhGaPhDzxK'
        b't0N7mdUsydk8aMgPbD+xwyGFHuOZny9LSoifOJhFFMoYcWY5UfSINbXKMlW5SqmQjqoOUtUR5RHG+7bjRLRkm4aRZUd5XZ1aVap9hEIphUSnlCiU5XIMOwdYpES8rlJV'
        b'VklyV7HthBnNWg5mnpF1+5iMi2+9VNXUZuhhbSLCNRHfMjF9TNzHZGr/+Hv88y03Ji4uT2LXJxxeLDFxkVfVVsr7HBeQmsxSq2vUfXxNbZWqTi3AvdjH19biKUBtx5Cr'
        b'cFnZyp0AeXIIeDiKJQNBPEipTg133dh+HrDbfY9A2BcAK+F6YvxF7cEtIWPNIUn6DFZeXU/eaNqVdk8UbhSFdy96RzblnmyKSTbNLJuGA6jgmHpjvWmwjOobYOAaZrU7'
        b'djrq+TgTQ7g+VZ9q8fQzzO9K6+bi31kXs89m3+CapKlmaeqNArN0uikyzRyZZgpLMwXNMHnO0M/Sz7qPHyhqztPPsgSHGyq6lO3VndVY1HSyhEpOBx8PNoXGm0PjyQUP'
        b'evz7847O02Z9lNBkayybzPTVEDPPpUO2zQePfToCN9QqxSV4ZJVhYaYqZib7v6QkRn3mp9HJ7hewXf6YdH49hE7btQLfBlA749E5bghBHBtBM0YQ9DiT7soBFOM0cD0C'
        b'l47TPnu5ppieQ+yzV66vralWVj/yzoLhlfoXGan+bKUUnSvfCY6/FxxvCk40k0+qMch2icG3ZdQqWLu6VKkmHWHtAXFtlbyMmCrK68RVSrmmTpwgiREXaZR0rijVqqrq'
        b'ZKpq3GNqXKqipISwulyxUosTkgRDcxnaXANrGb1r1n7gXeNg4F3jjtZrg5hRLB7+I28Ff/+z0eb8oloiNbPzvXJ9WaW8ukIpVtOgUjkx9Khh7RpxKrm4Vl2zVkVsFks3'
        b'kMARmRGrx1olhiXpuBPVuGlmyKtXUSMFTV0Nlunp7Fz9WDOxdRa2kVRMSSohvaOlMy87z5MFYcA4AfcOOQw6ijEYTonRU2XNQ4gkFWtUeEmzZkMeIwasg4+UPqqO1oxS'
        b'yrXVZSklVvQ2ilXZD25IlNbUkDczi8sH73xoaVcohnXDqGvUOqUaTy9rMfSSlxJL3Efsgfyo/ahrHj27iJpifaNlGZlSokjOXki2B9C+DOzNL4rMkmbKBGDt+NUe9ugu'
        b'PFmhjSIPtKGbC2Aj6kXPzAtTRWbJYojdRHQefAYdL5AhLLckzeFXwDPoGvt+3PNTUJsmJjcLHVwn8ABusI2LGmbEwD1r6PnGhAJ4Z/CeQWSeLCpbVsBmuw7H7c/mY3nI'
        b'Ht6Ch6NZ6e8qNMCjmkiq+Ob7FQA+3M+gXngAndOS9/ykwdsb5sO9qLUI7UUHoT6miGwc5DPoKtoJb85mLWZ16DpsIlQlTOcDLjQwcJsv6qRbCqgV7nXTZLA7CtnwAg+4'
        b'E5p3FcCesBL69BrUBo9pSOvwg9AFwN/CoPPoVEShKvnMC4yGGJq8+3nD3nmX8lCc5+b/uXQkOTNgwb/5E6aCF5tuLpoRtTQt53+cSi+ZvS7dkWRv9bg1Zk2QdF72oU9/'
        b'8+43731z7hvBXXmkrHEsJyf5D+7fHbr04oO/rXj9w2WoqGHak1NkE31EL5dy0uIEH6rWzBHedzm/Ys30589+NPe8IePrlOdWv+mbULG56+83Yja4L9EeqUvJf+kN/gHH'
        b'ab3fHP3wd8sPv/mvatPCa2u/8Osc88GdD8oOb+6YvP7m/sSlB1omB6VUcd4eV/VWQa7XUW2r98edmV+99nG9G1ybV2BsvtNw449/C9+460/chrg/xY29u3Xc8Vv8vZ+F'
        b'akPUyw9u/vLf/64zTsrtME8OLsxZv+mLyf8IC3lh87/Bn0I/8M58Ns1T4k43A2Qry+nrkVBjsdAO8GQMPD8GnmL1/CfRIdgZLUN7UENsBtrLBc6zuXmuAi/YwZ4bfAZt'
        b'R3tgYyxOAdthLwN4sQy8Miee3iA9xRGejs7KzfEg12CGMvAIPAX30A0UtTvsJXsbuXboNjoABDyOPTpgvUMMXcND5HI2JakyHT/pw8DjcJuC7q5o0VG0f+TuynLYyVq4'
        b'rIU32ZfXX6sIj46RROGxOBfepVaUbugyd0NJBa0yMqxEt8jGBTy2ybo3kg7b2X0Xw1p0l80dXkTP4Ng8BvbCDjXdHclDeqgjGx+Z0hjYEEu4M5MPymC3WMxD18KnPggn'
        b'raJfBXdmU3bNQrcpx8K9sSzLRqHn+GiHM7xAjWHGBqE7bE3Jll4DA5wUHHg8Cx1GLfm0CZcgA9yXnS9jQD58hrOWSYMX4X6WzkOoyT3bdg1bSRB7EVs31FMS0A6oR1ez'
        b'c7Oz0TXUkhuDGqTZcG8+pTYK7uPDi0nwBG3uTbAePo0a8+B5KTyPZRLeTAbeRrscJcJfXFtLHNskOHR/x4udZYuHLiwbA63IYtRYuuVz0LrlUygE7j5tTi1OxsDxJuEE'
        b's3CCUTjB4h3UVtNS01V2stLkHWv2jn3HO+med5LJe4LZe4KeaxF6tzm3OBuDEnrTTcJkszDZKEy2ePvpywxjmytbK3EKH/+29S3ru5xMPlKzj3TgGGYau100zeQ/3ew/'
        b'3eg53RIY9k6g7F6grFvRO7Fn9Y0lpsAMc2DGO4G59wJzTYH55sB8vYNlbMTpSccnHZt8crKeS+7e9A0w+0Zh2O0XrBdY/AP1ZBvnaE5HTre3KTDOHBhHXgMlo45+Jgb6'
        b'XdnmkDgM9QPGGCZ2JXXbnZxiCog3B8QTE93Atg0tG7p82cvWuhX3fBKMPgmW0HCDgJjnzjJENufbbmhLNnlKzZ5SI/1YRIFdXLM44Z4owShKsEgS9Olmz3HkrORsizis'
        b'i9dVdHrJ8SXHlp1cZhIn4HTkWOY46mBCfEK61hl9YvCHvGgq0pBPC/za4hM05OSjk7oK/Jy9JPautuGnGqfjHv/hgfE9Y3vDLj3b6Pajb5F6pPOLWQ0XASoTEOFviOn/'
        b'gDEDNcDlW03/efRVInYYltpefUBULMPuq/zPvE7k/bdHg6PpLJ6yXnLCyk8EdWN4QyDSgIBiRaUEomqswv1I9GO1HhkGa4eB2NFB60gsVTgSIMsJCBuCGW0QroZgS2I6'
        b's4Gg35GUycsqWWva1crVNeoN1NKnXKtmYaBGXvETdC0PdSdDRblBx93q5OoKZd1Ayh+0lakeMJZhB77NVsaG2wnaVmoGazB/likwexG9mzPwrZrKBXNLcqoFy9kbME5N'
        b'DATJ6/9shwNTP/Sbab1JXn0d6Cc9wAN6+hpLoMcUeskFujgrXOPiwgEM3LkJ7cMocx08qSVvIkH12Wh39jAUa7PLsWG6QmKZuxCjQGJh89DYN3M2wwcbg4UpcG+masGu'
        b'jzkaskk9qfj47oJbxHik7vc3/xzqvWuX7zdcwdqpO7YfPMY9vnSX79k6eeLk0jfMT09rCGieIJ47JnxP/p3Jv/ti7CbOgd3Fp5t/9w/TEUPytOiQNstt/0l/2Hn/o5s3'
        b'P/dPvpK57OICwYN5hjNzmi57fnjws7fsXnnzj7/dvfHDvzelfDhlz9Oat5YG/3besllnA//1xHj3rV/8JTb5+oHkYq3j/JC3fN+8lJE9UXbbYR534dNtbW91Ldqcc7fl'
        b'vYCGvuBnJTsFsHP7stwj0V+tWDXuw7jv1V13b3p2zztdbnxzqzZ47auqsZtMrre223f6nvlA9Af09QPOzvvT7/1TLHGluMkPdW4mN1NgUP3sgOnuibUUq42B5+B5YrSE'
        b'Di6x4WO3BdyqGIzlyI176I4WI4KHzT8YkuSi/RiVoOPoKYo61qyAZ22vBUmJh8eZInt0k+KfldPlBFSMABTzUBvGFDVBFF0VwSvosM3sxAE2YHSF9lfRSxjC0XPoYvTD'
        b'S9Wd4GVOHrqAzqEn4Q5axXh4Hl4aeHlIrojPwLuLYDONm+ULT7DQjMAypIvEyIxBOkrZ3DS4YwCYBaIOGzajwAzuLn9A72y5gXHqNipUZWLqhzQGB12Ge5jiWBBvD09i'
        b'EppYNHp0MTpORCCJFD6JixWs5ATjOlylZaIr8Ahqt5rhLIMHBx/ugXp4nZrq8LE81h0tzUVNsAu1YPJhTxZGo/AAVw1b0XWJw08DUQ5g0J2w1vN2Vnl3o6t1WbR+pwgp'
        b'z4qQFO4gMOzo1I6ppoBoc0A0eW1RgKGucwtrumIJCNFnW3wDzb7RGJB4B7dVtVQ1V7dWEwwU2A947vFsZHfZxcqzlWdW9qy855ts9E22BIYcze7Ibs/tzO1Ow/jHGCjr'
        b'HXs18kbBZVmvjMCZzI7M9uzO7O4wc9RkU+DkG2X3AtOMgWkWT993PGPuecY8vEjWN5DVQfq0TumadU8kMYok9OBf9yyjTzz+ULvmRcalxeallSZJpSlYZQ5WGX1VBHvM'
        b'6g7rkZnDkk2ByfpZpGLae/TtfASiaI0+UvyxPV5mkpSZghXmYIXRV8E+G3ky3xSYiB/0DTrq2uHaVXdyY+8Uk2+a2TcNE4TRzFqDsmuRySfGjMGOMOb/UvcmAFFd9/74'
        b'vbOxL7INMOz7sCsiiriw74OyuCsgA4ii6AyDUXFLXHBHxYiKOhqMqERxJ2oSc07apk2aztB5ldCmIe3La9qX9pHWvn/q+7X9ne+5M8PMMLg17e/9BQ/33nPuud/zPdv3'
        b'nPP9fj+mgCzczi7d1H0OZ+IcGIuZN/FSEGcs6i2KVJxyG2OwcSqe8AJK09+p5rTiC2Y8X6OtjOWGY6uJ9XUL4YScNT3RIbHGExmLkxYR7J7KeS+SmogqfNkTXnjDE0F4'
        b'/KQ6qYBWwZBj5ZqmSv0GoHKIX71cSTczx25cDrlWGlViuWO3jWLDfrtFRAFUBtgUbmOGadvM0oUla9zhl3SaC6FqeffKcwndCUQW13hMHJYEX8jsEfTanyshjUqSpPHg'
        b'MPHMjtSMiFJDDNhaH2e4I6s9fPOTZcWSVtaMvcZr7mhNkW3KcoWklVWbypZW37Q8OlsT2mzikU/OtvJOsXKe6Run6PGa2b3gtI3lwRxJYTwA20zuaBUJZRu9jLLh6gYl'
        b'YWvNCipVbeSnBkVutImku5CRT9hIqZCrQfeG1WsbG2oamiu5vqBsaFpD+8iQXfmGtdw5C1ennAXwkJCKoEO23AksiTQ3/AgyGgIPOVeuVdQS6ay2kr6y0dNQ4WaP50J1'
        b'72bomMlp59Wq52ndY3XusSOMzYQoMhx2bOnx6PUfEE/RiKeQJqCTJJEB0mchOxgmvVh8vrgv7FacNmy2Lmx2Z3Zn9pchMWrpYEJKzys9r/R7PPDvJz8fCj92/pD8jPDZ'
        b'uAXsNwwbupB9TEPSe/0XssN+wV2FZDgS+7U7jj0sMe4YzoTWQ9YLctisZsevZX2Nmt7zTwtpDQlkG205NkRFbhRExpJK4UVKFeB0WMrjxjajdXfQqA8jwjAFdUBuOKLi'
        b'HiwB3oUxei2rwYRJPcq+ybdSL23t3dpDfh4KPnB6SH40YpnGVTa2YEYjX5BWoFjjjS51PP0osELKkz2xgREgKFzJUT22q9tUgg9eQq6zkVx6Dx6XlDBoE1LFQeqs7oI+'
        b'wS0nTehMrXimxnUmR59VO+0chhv71Iy1f62snDXvyJtZU+pb2VX0Lz3zJfSzaZd4Cjj55dq1nu1LWQPb9cUQVVY2guMoJ2Mp4HY5SfKnMK4Q3n6PvGMGyByd3Zek9U7R'
        b'eafA7CXp2EimU7FU4yr9ZxaJ1RcJkBCe8NJmKOqfVZha88KQ2zrrhZms9Z6q855qKEzFAAWfeUph4Jv6YZUMXXt4FsNqkFm7MhnaVtE0TS7mRRu95uLLzGc91vCUnlNy'
        b'jVAwWmwLO+3R4YiwoHadGQvgFk7kDAbZY4Yf3oRMdtA/uGtRT3Lv9AH/KTBaZLCDweHd/n3ht+IHgmeTEcUzkx1+Op+Mh4aGU0xDGRyNPnWocPOUyltjXnlwu5anV/wl'
        b'hEsC1cknZ2jEURrXqH9moxPoOc/1o5nPbHP15h0IbiGJooHVa9f+k+gUGlsIdI6Zz+4c9eb8hdv1QOhqI6HjDpwwIzx9PtBX8iXWbMCxNs7DgZjZOM892ARVDetEaKRi'
        b'iTW36dYZuUJP38uzEgB26G4YvxXmNGM687eMTSLmEn90aKUShlnfnMCa901D0cmUUS2Xm00Z9H4LDFBT9QW3OtzCIkZdoaXbuvqFQ3n3Uq04SScGXdmxvDHWHShdP40z'
        b'Y+qQc8yl2PK0pgRzNVcSk7maPngNigK4KrQKj7ceaVVnc7vHTx9bv4MqtH/OKqS9hY1TbH6BalOqlpvP9HC/C7rOVqt93Mj+RD37HZ6/AuhIuf1Z7OcoMmE/fbDPRPjw'
        b'8e8UgnNFtUorjtOJ4zSucU+pgOXMU9cMNs0mL5UxFqwXPifrOU2QIWdZU3M+EchrwWFSrdykFwmtVYdVsZtUympVo1ml0PuDwIEZjPWZjp0Q/ZlEqvGQ/qs7FJEf9z2r'
        b'RrnimNQofdABjey1p08kHU+vu6B/oFM5WKlth+es7Tra0RK4jvb8NetQWdmsUNXKG1oIO9yM7DA+Ow5DzMJxalg4YeqgX9Ajv4QBv4Q+YZ9S6zdd5zedLHokgV2pPUKt'
        b'JE7jETfsF9RV0OOp9YuHiODOKepwWHpxwNsaj5T/N6zmWWE170XGNF7CC/PakUjHjU1NCo7Z7kZmjz48C/3pObndrPVL0/mlGbjtqZXEazziOW6Ha/0S/jdxW2SF26IX'
        b'atjhL8psG4qJYj5kwf1F6OKHrXZx46L8q1FOCAknBBaciHkRTjSbbBqZlrOVtSzp86ZcQtsp9ecjoLwb3WUzS0fj+ePH1/H03B0SkcZHmEPmZypnnTAXtkSjPB8Srl/R'
        b'1FgLPgJWVzeskdeabtXoNWCNNWBfWcnlSyphgrESDI+uGfdHrTR10YSZpk39Fa3fbJ3f7PbszyTB6rDu6J5arWSyTgLek7+MjOuR967sD9dGztZFzgacyezOaYN+IZ05'
        b'6mTYUNb6TdX5TeUeTCNJV3Pdhiyy/GaCr42ZT8FiAoNva6K4g1lbtjrxPn37hcK/1Zs1TnrfD6OtRM8UOlM2d23sXNUzuXeGVjxNJ56mcZ32EvTaP53e+uehd22T0oxe'
        b'en8fOtNZq+sZY2cqMiGq2SSFGUlm0/gzBl+q3zrfvI0+hfDq5eaE0/t3ofUFmjD6dA00rBNNXU09zb2bteIZOvEMjeuM72KdBirFig3PoLJhTbMZlfT+faDS3UAl9eDW'
        b'lXp4a8dWjWvEd0HZimdSZkdnp2rO2bnJfAVPPjBbQfq1q8DLMudc3LBloACbTetj7GVGb4lCxkxuL03hYto85DxrdiNyvlzAicAbxxRos9kG6Tjb6Lw9IosRmv+scZIy'
        b'SigDq2rmSQhVWG5YUx+0tmk9p/I8MZGznlCtXdsEaCtPeInxQ+xEMpoGGBrpkO06VfWa5oaNtVxz5bzqDdmQnOobmpVD/NpX1lrMZ6Oe9bgxdbRCKAVmFaJ/8gOokGX6'
        b'CnH37Zx7ZHr7dGowkK/1LdD5Fmg8Cga9/NvrO+Xqmp7cc6u1AZO1Xsk6r+R2PpXR9WvhzD5/rfcsnfesp4jrl6iYDdUrTbAwTlb8TU+osrGpGQDE/IADzub6PeS+rq62'
        b'prmhpbYSFDuIcNRYrWyu5NQ8hgSVKkWjYh5wBFxkm5g5G/v8kK3xkMiB6lVw6sNUt4ieNijAATg3o1VDAN6XFSsgaISgCYJ1EECzU6yHABwT0sW44lUIwHOfog0CWE8o'
        b'DkDQDkEHBMch6ILgDATnKJ0QXIAAjOEVfcCffzZk+Bjbaf2ppICFkzaukQAmgTJSYG47LRKA7TQE9oxPYlv+cGCYxtFv0D+wTTboH0wCSWBb0aD73LasQUk2uQqJ1DgG'
        b'Djt5tM3vzFaHqus1kvh+d43TDK3TDJ3TjBGeu9OkEeZpAZilzjQmjWY8/dvzBl1htOAsdj2pxa4ntdglYVu20UY5RuMaM+gxEWyUk8BEOQkslJOogTKXIE3jmjbCY73m'
        b'sCNCvncpyQfCxzQkyewZZ/Ggk/cIL9wpYIR50QDo9tm/GP6I9y8cEcBzGUuzBGbUaJxCtE4hOqcQMLdNAAvcZwSQUyhJb8wRIkjDdfYa4QmcJkOlTDZi08EDRzsnf7B7'
        b'th54sU4lcOxkPRSxTuC2zBCIeE7RYDGvD2x5YFFtDGwFcDVe4Mg6SSEXffCMrFhA0bMSiPhQRCuBPQvvGoOnpQM/aYZAZGCZ1cDRIlOR01QiYI4TuP4jsTZORKIcL3Bj'
        b'nVKBgjGB6CkRIKGODUhEJFyNCUTm1WNSUULgxgsEo8CHaXboLSXejw9QS3AW7WFsvXmqCnTMOkb533igA2luC07dkPLbBHUCOW+HrR6wkL+DkQt6hVYBC0UkzmZMnI0J'
        b'mKFlnK0JmKFlnJ0JmKFlnL0JmKFlnIMJmKFlnKMJmKFlnJMJmKFlnDON8yJx4jFxHEyhN4nzGRPnSuN8SZxkTBwHRehH4vzHxHFQhAEkLnBMnDuNCyJxwWPiOHDBEBIX'
        b'OibO0wR40DLOi8ZFkLjIMXFiGhdF4qRj4rxpXDSJixkT50PjYklc3Jg4XxoXT+ISxsRJaFwiiZs4Js6Pxk0icUlj4vxp3GQSlzwmjrOhn0Jt6FPAhl4+lYTB8mlgPy9P'
        b'paLi9CEX8DVXPuq99wuQA8bYsVsk0mMxWiQDEypqz1VTvQakzOW1eqPh5gaqDmuwuqIwfQZzYjC84vROa801ZPV6ueaGVnCUYOJquApk2mrOXZ68qUYF28bGnM1ya1IY'
        b'Mmxo5hQ3uFcNaq6Z6cXlWfocqsaxdTa7ya/TW41VBy2naiYkO0472dQVciz3SUNZ9bb6zYpaYIhZftVK6hoAiKO2XC0kp+rGxiAV7Fw0bgAp3szHstnLZmsr2NuA5eKf'
        b'Wski4ZgAli0Ke1i6jJqe77FVsc9awjSbLErG0/OxWNTw5Uwrv3IUHhTuBGZ3QrM7kdmdjdmdrdmdndmdwZsHM1ZLncQ6mKV1NLtzMrtzNt7xyZ2LWZyr2d0Eszs3szt3'
        b'szsPsztPszsvszux2Z232Z2P2Z2v2Z3E7M7P7M7f7C7A7C7QeEeWkJVBxjuW3AWbpQwx3LXy1KGMlX/mPM9iljbTjT7BZmGrQB1m7Q250LytKEVykpaergrWBI/7lsj8'
        b'LYUjeYtZGW64P8W2Ck6xp/mbBc3Fo2+RBbLFNqjSrbnEJFcb8mUrzh6a55rn0So0h7tlmf0q0uLsWvkrjS1njwWcrZJXANppHKStrUxxieT/JJkbFscMok8fJqlSRM4Q'
        b'WznEq6x8Em759opqMHwdtZ2lHgWk0iHHUrKGalitdxEg4vT2OXBtfmWDfEhYqaptVgAsEOeqasilcnn1mlWVRlehCqhdBSB2KW5AoISAgtqAY+IhZ3OPu0M2lZyBBslx'
        b'rUqxtklZSz5BF8Y2VKGxuXpIVLlaWU8/vQq8twora7k/1Jerk+G1SjBWIC/VrADjAopcX92sUpLVuaIWNPOqGwFVa01dE6GYMrShrqGGOkEhC3JuCjFGV69uHi3QkEdl'
        b'Y1NNdaO5T3xCL1nkK+rJ+l5USYdwkg39W8nxxa/SguWVlTA869MKyfVq5ZA9IVLRrATXLnRrYciG1AvUyZBzuqFmuJqwUdY2Q4TUnjNPgqFhSLRqPSFBaQJcYGVnhVs+'
        b'w6DHjfajy2ao1Y1iCzLpBu36ysrPYYvld6xBawIOOavYzmZ1etd6TfxMTSD8UrOyZVrfSp1vpcaj8jOx//EtR7aoa7iT+XYBqGkLOmyNWHYcXF1kDAAwhBnx7oLM8O5G'
        b'Ie3O2XXbmYHfGf4GhpLHjoNBITRW/6L+YUAIdeSgf2j+J1wK74cYkur/UPg7Z0MaA3FhUfA32Hgfmwh/pXr6hgNC6WfCwrlUhtSh0otp59POzeyGpdCEBBocLmzP6gwn'
        b'rDg76+SsniStJEEnSQBMwpmDgSHq8hMbAX9w0Mf/bODJwB4PrU+8zoe6xub27Aej43pje2L7Bf0CTeCMTsFnkhD1ZJLM6EF7KftZQKwmrlwzf7E2brE2YIkuYInGe8ln'
        b'HpLOLHVYj1DrEa/zgPMy8jsoDm7fqA7rju0TacUpOnGKxpX+ilNAL8bhRT1dcD4CFd9nx/cg4W3ZugxeF9z4ZlARRsiqtHJqkbVm1ajz4VgOLKK5Se/0GQz35UTQaqjb'
        b'QMQnE7HmhV1gUJWIC8xLkO/JZ0wB4yLMkfbAwml1U/OoM2oKef3CzrIVvS9DmjeQNuox2xxgbyxlAMP9wiB211+GMIkVnpmC7FlQpofNflGePQ1fb1zSAoC0UaeVUiv4'
        b'ev8wdZRx770MdcHm1P08PYiDXFeqlutdg1GnQkCS3uZRD6L2VNLpyozLiFoOwEJqLXkNFkEUPskKLFt8UNnos7qGWvigflVCcicJRi0ijZKFMihaz8roWHLZ0Ez/GtD0'
        b'oqlOfTQHUhf9wvzUvAw/o4CfA0Z+Th6LTjNOX0nPmJ+eQILsFwbLIzT+4GWGyRhzUtPM/PMDukvtcnNP/ZYkZ5ZmZyVkZWeUvwzJH74MyfF8UydBSwwDeyltbiYSqN4w'
        b'1+DSyMJiND4oiyLWcPaxjeurNyj1zuaD1tTWV8NpyotjDyh++DIFmmTe/aIN3c9gGGtSJr0sGhRVNm/+ohceVgllP3oZApPNB9ZIOoU2Na2CVT/neF8RVL12bRN4DiQL'
        b'BBXnqv8lqPvoZaibCtT92XBy/sSl3OhP7SWp+PhlqJgOVISwZiP8ajJgVdfXmvSetSs2KMEKO2hOer6MDHCNL0SfXsX1xy9D30wrdThKV2NTvTlZQVGFpdk5LwG/ofjk'
        b'ZahLN6eOs2NfI49rboojf0ZFtaCo7BclSw8l+pOXISvLnCx/q9gVQVHFL8kqzcvQlGsu2Bpxb4M523+yBFwD7r70AwWHXzKnonTOy4zP2pchsMC8P7rRKYUumvXOzV6U'
        b'U6T2dC9DSLF57UVbThCwGgfbRriOyigpKcyX5ZZnL3ixmUxflf/2MgTOAQL/3cip/7Ik0HwbIT4oh4yzubWE5DV0BaM0bvFy84Xe+QEUCvp1VNn8/JzyzJKs7Nig3HmZ'
        b'sUFzSvOL02Ul5emxQVDMwuyF0lhqfpgD7XiFPs/xcssqKSaDA5ddTnpxftFC7rqsIsP0trw0XVaWnlmeX0LTki/Qbef1DUrwNbG2sRqQ4DjQlRf3efizl+HyPPMOE2/o'
        b'MCEm8yy3P8P1lmo64FQrSRYvPncMvAyFC817zBTLdsDtNMUHpY96acyX5ZSQGs2S5cLkC433JRrtT1+G2CVAbISRWHE5FQq5HTDSaOTQWpteqI/rR+ihl6Gm0mLa1aP0'
        b'UB+oHC21o2cgpkv5F298j16GvuXmXdyf45Zh5gCnMUFwtmNFFDCqdwF1nInJKFXKJjNbZ2czJVcz09C1ItM46siR18qaqmiRa+MpiPmOcitTyZikMp6OKCaY3pnSVWn1'
        b'qdp4kmL6j6QwnqmY73WzVtrrk+mlnPsXOIcyyvLcKmT0RMz6KiVeaqv4HtTB34F4QHcwAXagW8cA4KBgoYL53GYnTUQ3NoEbRpMah/raZsPO9EaJZaWbRNaS15RwfvDt'
        b'NgbsDzeD0nkeCwrmUzWSGT0evT59WbfyNFEzNJKChx4f+LRnDYbFqHN7svrCbkn7yx8s0YYV6MIKjHjPsBU3a3Bi8i3/TkGXk847ftDDu6P4kUfSgEdSX5Zuco7WI1fn'
        b'kavxyDWDh7bezGH1BBbFeq3lcs7AcWzbBiWusW3bYPfWBAMrvKk3e3uKHuUCxrJfKTzGU/02P70xV+aut267J+UpfkGeDQlgB9yKzbOtfm+80lphuBgFVFg0Vxh3sc49'
        b'DDakE0h9PZLEDkhiuf1QjUf8Z2JJZ8bhVzpeaXd5CoMNxjYm5XU0vVtpUgJaDWAIQU9jDEUR0mZk3X67sXYNKYqVjXUasR5KEmBRkiRqmR+rk0zSeEwaFHu3r6PUy6Sh'
        b'1lQO6c49VRIccrY4faEdg/aj0S4E5aa9Z8jJ/PBFpD97sdGLowow5R0S6c9dhNyxi4Ceugjg0IXi7Qw5mp24iPQHLgJ6eOJscbTiYHqyItIfydiOnshwpyHO5icuikCe'
        b'vnErwuAqkkftIcZVDTSHzFTcg15hqZigheOMry0gVUR2oBYIgVe8k98I8+xAzjIBEZ1GmJDSESEvoBxU+Uj4mIZtMgtokzSAJJkJiCQzAZBk5ouDo1jNwRTnYhbgXKRT'
        b'JJJ0ikSSziGjjKYZ4Qk8E0aEInHiNwwJHkNAkjiboIkMehQAlEgRhRIpolAiRQAlIjJLAyX2pyX2pyUmIU3DgaeA2f4Ij/WcNiLke6V+w5DgMQRtOSO2ZhTPBoozKMUZ'
        b'lOIMUywXrtgzoNizoNizoNizaLFHvzPoEQ4gLZGA0RIJEC2RFKHFVNMS+OJJ+eJJ+UJCqmn5zK+YJpgCCaZCgqmQYOqYBEmQIBkSJEOCZJrAL6zTCEoDMCR+AEPiBzAk'
        b'ftPaiiwKEgUFiYaCRENBomlBTD8B7PKg7PKg7CIh/cpoWxzh8T3nsiNCYQBohEL4mIakOToyktBO0trAGdCgx1SSlYRUDQkeQ9BWaEFMERAjo9A3Mgp9I+Ogb0zVU+NA'
        b'PTUB1FMTQD01gaqnPg/nTTsP8C0A+BYAfAtIJqSOC57jwUIPNAYiPiDWGAN7vpMPXFkGnG4f9SZ2Hx3B9x1anNY6SgtacTveHyMrigffXPgQn4leIQSMvGYzRT/DtMah'
        b'gPJNFf12MIv4PKYWlPwsJrxFQvqcP+a5iD4XjHluIxeS3GzbeHWsXLTDdpGd3Ibc2wNUSB1PbkueONA4O3LlCGp/i5zkDlQucBxytxjjihqUzWZApjzDfDebm+9YM4mR'
        b'R+6MhIBZQKVRDq0H2dJEE8cgZQvo5taQXaVcpVdmtwNbs+rGhuYNQyGWJ95AT6WpwpXSYBcdz6Na7YZMbA15GCykg0yQBfys5GqEGdgGk2k4N5nqT3CDpfQ8V/8ngp7M'
        b'hmro74secFKrEeDieOsKq7QZ1ha7YG3xCsNYMRl6ruVf2st+eDd8eNNLfFi/rTTjZT/cNv6HjaJmLP3w85lHGUjiKUJBDphpnS6QEcZtJVR43MvXWxdtY0A+zNL5JWjF'
        b'iToxTGnflXURIYzSN459ERVixixJ9FRSufAAX29jP2oCRURarThBJ4Zp5LtaLozDKG7J0A4VGMwzVKCpFzCj6Z2JyagV41mluV4ga8Xz1uiYY1LxevgdCYk3XSnzLeId'
        b'qBmowPypwqXZqLVnTReRvGFc4apN/IeN/rM0r2e5MY+6bYsz3epZDbgNy0eBOCItuBlpnlzeVMvhC3C+xCiEk8GjLBV9ycoXgIrogEilb8UsuJoNAbWpgjZF5PS1a2vX'
        b'yA1OxBxMPsElHdc2mF8tl49ZidAqJxFH+SaGqVQ1JKZnq1Y8SycGA4oJFexnvqGasDKtb7nOt1zjUT7oHqBzD1U3d28YcE/UuCcOSiJ0khiwIhyQpGkkaYMSiCQ3kzWS'
        b'ydQaq1zrW6HzrdB4VAy6epBh+JFr9IBrdM90rWuKztWgfeKa8pQ+CAqKo33QusWhqfufMf0uAvqdjzUO0BVcF1+Pyzja6w5v6NigcQ16ivXpFMZyDAOZoJXJslgcW1kM'
        b'82TWyxlFs4R5d6kzeKSzthY9zNvvAmU2FDgaql7vFAf4NMQ2m3p/UMAic2OctaI3NzVXN5JhG/TalDPJBUgOTavXzgQcKiXktY3RSKZxvz3rOtO78rpkxgeUM1J2iK9U'
        b'rbayAhbS3K3znEad5etNUmE49uXy7MsigVYyTUdCcapOnKpxTdUvgZ0tl8CjJnK024z2GONqkVs8FvH09a8o5dGtI4t1IzDfuGpMhXZiTaLaDNT+ghljUCYFoxt94Eil'
        b'dY1fEvnVuk/WuU9uyxok651XNEHTya9WnKYTp7XlWXk0ImCdJoJQqw9ErFMiXI0JRBYSsA0Y44wXuLFOwZBuTEBymQ5XlgEnKcP+SsB89J5eTjYVkvFNvCcWdeXFs0wW'
        b'fsumCF/NNJOWDcrJf4JGeczXVFomPzz6w+8SLuID5plcJLeR28rt5PZyB7mj3IlcOctd5K7yCV3OiwRtvDYhkX3diMQrJHKwsM0WIArb3Np86mwAYJDK0jYURtBclral'
        b'zz13MHKvXrEV0xgbvcmJZZw9jeNMTizjHGgcZ3JiGedI4ziTE8s4JxrHmZxYxjnTOM7kxDLOhStvHV8eRkrqSlMmNJDhr9bVfGzpZg+yi1xJajc9bOEEwjWWgha60SuA'
        b'LHS34wAm+dRJuwgQg9ocKOijM+GpK+Wqe5tHm2ebV5u4zbvOUy7dYQcmMR02HV690RbocxPha6QW+PLYMVCVnvQd2964se8QWuLHpPeSx+jhDx2hzxmMJ4bYOUNsiVQ4'
        b'xMvNGOLlZw/xssvI3/IhXmbeED8jVzbEzyosHOLnZswZ4ueXkau8UhJk5uUM8WUl5GpOEUlSWkKCsmyIWFSocIAlCz83f47UeYiXkTvEyypUzIdplZdP8s4rHeIV5Q/x'
        b'ZCVDvDlFQ7xS8rcsW7GYJshcRBJUEGLyx0wE1EZiGwOyEPjB300kIuoHnyHLNQH1gs+34gVfYGfFrz15Ihjj6Z6/RaD3gm81ztQLvmzMupVOKSa+0gUyFQgX6PYW9AA6'
        b'dzPeUxKPDxTjAzFz82Skf4P37Lm4jfT4+HwS4D1FsfnFc/NIny8oxrfQAzIKoEsCZiZ+1QXdmlLSoPm9u5C6mV06v+/UjyadPnf00tFzyz/qONf23o7DrHOp93F2w5Uv'
        b'Qor3hxfZfirMaxR8Jc/4N/ePH54QMckH7d5Y+QcpnyKKrJ+DbjugS7F5YSsN4CgT8D0+egvviqEOras3BeF9JXhvATq3uJgMPrboFO8V9FojfTt5Mj6O9qFD+FBhHDqE'
        b'DtkwDl5bfHh4dxO+SJaa1vYKoeosNKA9TBugQf0ZeqRyEqNHaPdnPMSdsRr3CPJLhaISre8cne8cjcccC6Vngzsybo62GVXWVvwKpiQrXpep5bseffxZVN2AuWg9w+GO'
        b'E8Kq/Vk2EHwoPyP4zuDEYanRaRfPXHVO49cYjWzIP2dDqzsDXcKG6xK7+bsFu4W7RbttSOewJ51DQMYeYZsNGY+4EUhEwWNd65xphyHj9x4Hiw5jRzuM7ZgOYzemU9hu'
        b'sdN3GKtxxg5Tb9lhjDBrJh0mUKYCWHB0FN+qLTSgA5MOsjg1Li5+bl5BBW4rKYuChlsxZz3akYd6+Aw+uNYBt+NjuF8FjsLQfnwGHRx9mXSmkrh5eqiAAnyAzKuHCudH'
        b'4T3zbUmPFDDobXTNAZ3OdkLvoHYKWIBmixhHhlkwJ6oqVprRwKgoFtBJfJ2hiAVxSM1SxALUUUvT35pky5AWZfvn6irH+Kl23HxegV4TmeJi6bELIhwM6AU2zMIymw2o'
        b'P4WCYqFDtRl4OzpXmF9cGIsPSFnGQcbDb+Lb6KQKDHvwdazGb8TkAdIBPpqEeosSE9GOqkImBN3mo3fx7ULVREi2g8Fvx8jAXf2B4goTkISo+LhCtCsKtyVE5xezTJPU'
        b'lkgW1/AFFXT2MH98rBDvyy9KEDEiMcltN8+ZfPAo7Uw0xaxpFTHA9TiSAN3Dp/EZ3hR0QP96FD5HGE2i0QmoFxvGdh3PHt9eTasS38cP0P2yUTJipHoq5kbhQ7F4z5wo'
        b'I7k2DOpCR+3n8/E9FbQM1Ie78O0ym8Vp5CPkM4fwm7QuVjajy8oWfINU3ukKFp1g8CF0c5ZqNnzuCjoTQfh+IDYeHwQ8tLUkXXkUqfZ9sbHFFXn4YCo+U2LAkxjFn8bd'
        b'fEd8qM5PBfMLOojuLyjkoqR4bxEptXsuHx+3w6fRm/gchUVDavSue2S9kdcM41DIQ69vwMdVMSR6Grpa4oL2lwG0Gt6HLpWTkhvKTb/NMCWuNmvxSXSA4mHEoZPoND4K'
        b'tkwb0S38NlOMd6+icGgbvT1JVV1f30Lmgz3r8Y1mEeMk4aHT6AY6UVmjgjXRJvQevqUkUaSZx86LKihFb8eRRkTmEO5boxwmJSF9q9+ewTtjVUnk1Xx8FHfEAHsIu/Yl'
        b'4ENlUVFkQmhLkAGvSpB6dn4F11rRNnTJjjSwAtoe0a3SeAd8Bz57dx06sF7huA7fIeOpvziJj3agvXgvJR7vQO3oFN5HOkFxXDzht5BxQ8f4SXPRVfSAAxL5uk4AQ0FQ'
        b'dEZV0c2N9lxvI1lcy1SuI6tqwr7tpFWjveiApOFn23SMErSv8OdXj3XMaEKJrrt+v2P2x7lu79ppfrLnds3uv+3927b41y+LLr3FW96DSm/j6/P9XUsjvP4md7m85FfD'
        b'894v1cz45i9/2Lx6d8JvTvk4/q4qvWFV4h38m/Uf/2Ja/eSwz0N+/9WPp9vEfPLxxZp9Pzloe2XBiejvz/WceGqbpPOHp/q7r9jNm10RdvQ/Ln5xMVl5bz7vr5Nn95zu'
        b'Tp7xuFM1+4MvefcW7/3DpLaUJaruX574bHv7hd+e2zQ4O9JzUVl+8ruKhoSFLf/dfHbCR39pttcpy79XGPBNVxJ78JOFH/zZs7biZ59uLfcv5D8Y/NmXl6ff++PDff29'
        b'Fw96pX0tXeQ7/NbbzQ/fr1xf4/9fLbG3TqYlJ339xcx57j/67GFd9cW3fvHLE4d9fvm3TRkRqSejPhuySfD/9MCqewGHL/33gj8VS6+V/HdIzfsZgdMf/fDoxl2b/+rz'
        b'qv/Bh2dcflqku3jVb9tbi6V/zfyJZMX3D8rubryx/VRW9h/YfpdlbrPmd6MJuSvfDNu9pWXpvuUul4p3VKLM3Wm/T7pv/+eom+2BS7Qlv972q6ObnaPutH9oX374q3L1'
        b'/skh74R2T/zxp3n1WeerPv9T2Jahn2ZnHNp0r8j27+Excxyuum355ub6/zmUsLr3lx7H+p4k197YFDFzC+Poqh6qmC4NpZLFTHzclsolZlJJbzl6qyGeIoPgTnQB35Z7'
        b'kO6MDibI4vIAHOQaD18gcsiFx9DkktGJXD3WBrqMTpmCbYSiWzTJWn/cjfatd3ayV+DbSnyn2SvQScR4rOOXoddQO8U2QTfwuyqKqIbPrwFENTISd1PJaHOcF95XRBZp'
        b'TvgMn+Hjd1l0Cr2Db1F0lYJMtK8pmRBHhDspbqPUXeWRgRvtoV9Gx0jD70f7XNAbaE8LvrMW31aRTzuIeSsi8X76ZXxTkQjgLRxwS9JkXpwQHaQvs2Q+6CWCYmy0NBPf'
        b'iaejJ8N4BwmWoSv4xmOwYUVtuMu3ML5YxOD9IbwNbBrqiaaE4f5Z+DDp5HtJf9qPzhTwGcE0Fl3HF3EX9+JxnqyQDHVkfOhewlvGJlTiPg4L5SK6iU4qWzyXOq5T4bsu'
        b'pCPud7F1ssd9Li2k3+M769eRAhQLROjtakcO7a+P0LkrJg4fKJrIMqKFaEcwi3ub8S7KPnQcdZKJMQ+9RYjqwwd5m9kc8mz/42AGoB/vT0JE7NyHevOKEZmo4wsK0JFi'
        b'PuOLbgvWt+J3OLhBdXIavjcVEh4kczmpDSKAzubh12fY0zbiSSrvbQB5oaMOag/nBh6vIoGT/wIKPYPa0+ehfQnQ0ISMqGqONy8E9Us4Rt1ZF4POkCrdl6AfNYWMQwkP'
        b'H6tJo9CCQU2kVZG8SfMrAVGCDGtkehcxa6YH4gsCMlLfcaWVJcYX0QlIiM95GZuqM5FXstA51EFxamaj1zdRUMQDRYRP+Sp0lCeegs4+puPrO/gGkWP20Q/IikrIZHsI'
        b'70TvkZS+uEuwbkYzR+3RmErCB390YHQqcy7jF6NrIbQ/tYShK5vJpLqvJD6OyEGFfNIe9/IIaa+hLloddvhVZxI7B3cVxOYTqYaxncpbPhtdoWXFx9J9SCSNQW0l3Afy'
        b'49AbAh4THSXE2x2aKMBNAdq1lKSTxaI9CfrZQ8jgI42B+K5QiPvrKEOmpqP3KB1GWE43dJWP9ovxviVo12NY1DiR8h4hncN8pYT2oEMJdFdkhsC4LxJDGuqBUHt0Ft3F'
        b'ex6DW15yeZ9Myj0C6xmgS7itSCpiihgbMnO+g04/Bh2NzRPReTr1HSJrL1LAvGJS0oMJhXFEbHkrGiQIOKfMRddt0KGgFsoUQmPXRq51IPLKXXyJe03EeJHR4D18hPT8'
        b'f7ZDJoM9qaVDJnpw52mxguFO7OjCqopTxBhp9Ge8Q9o3qiN7UjinW7DvnM/tO4+ifg+LA8DhMOdwDVLksXR3OUfrm6vzBZ2qYTGscyYUsxRgPOFRYNJAYFJf7q2ih24P'
        b'gx+66SZnPazVBhbpAoteHnt8WOwPPu0LyDcie5IHAhM1AbI++a3VD/N1U2SagBpNaU17Lvi7X/rIP37AP75nfW9rf0b/3P4MXcKsh2Ktf77OP789Z9jHv8v/kU/0gE90'
        b'zxStzySdz6R20SDkzU4o5Mo1++EUrakjs8DwsxtPbuyJ7JukDZyiC5zS7jgslhzfeGTj4daO1nbBoLu4s0Vd37VV4x5PfkkWndGasvn634WV+t/wKq1vtc63WuNRPezu'
        b'88g9bMA9TF2hdY/RuYPDoAlFLGFYIXdFySjQ+hbqfAs1HoXDfiFnC04WqDdp/ZJ0fkntdoPufsCLLFYt7vbrWd6zrme5Lnhiv48mOIP8UgoGw2PU89TzesqvLby8sG+D'
        b'Ni5dF5euiUsf4bMRmYAiIskCFBESguocCcnEF6iO5crQt/7WJq4omvCshy3a8GKtr0znK9N4yIbdA4DGOax6+r9NKdKEwq+ea9O14TKtb4nOt0TjUTLsHqxeonGfSH5J'
        b'1lGxFzee33iutbtVF5nyKHLGQOQMbeQsXeSs9iydR5jGI2w4MoZeDgeGU6vgkKgeiS4kmVy7GC2MuRiDra/eUtk/+Oyik4tOLOlaQhOFRnands98FJoyEJqiDZ2mC50G'
        b'qYMGgyJpan0eevPhiEjOoDksgcvSEn7ecHo9GBjMERWhDlOrCNWayOqHuR8UPcpaPJC1WLOkSptVrcuq1oYs14UsB5LbXfTqb9w2xAS9Ez6Dzb4Azq4U5RCfAvtcDjXV'
        b'zUbze5GyZkXt6trnRYkyGRGg61fp/xnHhWcOCHdhT+Mhw+1pfKvf2Fjlz7LUrde/IPyuNkcoXtZFuxnMO87pDvwXthsClwWU8+MdvZuzz3Dm/q2ZcvqLKjd0P+Wo3/r3'
        b'npgrw0eBxrTReQ5XgCA9ElJQlKK2Wh7XtKZxg/SFbbM5rfMhh0q9lVZlg/zFCP2ruV1B3DY9xbHWTL8alKOFMKX6xdXkv/cUNXTrhMJ2sol9YUA5NfgCcy+jFefLUcTp'
        b'kYBPDFVzU13di1HFF5jVcwI1E1I1x5GMgsBByKhpGlBKLfb/AcYpfF64IYqAwFHTgmhqWtBQp7clWA2mIqRWa9eAQyT5P8hCx0qTEfLFyLQDMt0MKhWcGRiYPdQDZKvR'
        b'XvTlqKPujMNfuME5AkmjJiKR5pivBgQ0zjTNlDATukbPwkHBCbTj9I7v+HQnF47rLaB+N7N0J5cZs5PLjtmtZbaw+p1cq3HGndwVz3P0IZJZP8NvAbrZ3SQZdXQGVIPx'
        b'hcXRzGaenRU6xgIZE8rYLTw91VbjTPefv1CxVmCL4Z/ePqaWugIzt5JQBilXNKka5aB+QgbYhroGsMuvrwbbCqt5Nes9rwVlNtZWg0VXUBb1DQQNr0kBaimcDwCYhhtI'
        b'H+aMlxqUVjNT1lIM5aqqcoWqlkzvDVzvj17VtKa5iYz6NauigxobliuqSeZg89ZS3dAIPc9qZmDC1TxmlCOvGdTTOVxjzpZug4mJmtXcOCs7I4E51Y1KQuFYRGH4Z9Zc'
        b'jJ3LpLnwZQ3N0k8YJWytehTxT/1o6ulzR4P3saJXfab+9L8K2Ii9vH/f8UjKcovj+/gO6tOvwbZFI8PKTb8Ea0VXSMd0NXRMvUqOoK6+tnljmFnPVNY0VlImjupkQCq6'
        b'VoKTFbpWCmL8grpmaTxMD5j0+pTmYho95KoyGMUoHoJmw3N9z5W8qKxj9FDkS4NY1g1EJMvgOz1NOmonZS45p/CtIzVsgV7K1wONC+l5Eas/XgVEBYuj0X8CyPiO5zxe'
        b'TYPmoMbncY/lMh6OfPYURRfEosvl3OEDPCgpguMPdGWGJ9rjMG1pRkOEdr9QOYvkcpH5FXei+nZe79GJpOXt/Uth5xd+uzy+X7vf0fGKT/X/iciJ2CVTB5RrZW++EtHv'
        b'fOT+rirRJ45M5Cz7/6w8LeXT7bJZ6Hq69Q2Fd5Zb7CeUimhjDi5b4xCND3CAxYZtT7wXnwpENwX42ha8g+6xBCQZ9qRIc5+5wXzPYRu6/zznrqQPKJ+rDyj1fSBN3wcU'
        b'QYw3rJQ9i1h1hS58Bnf5WUC0JqZAG1CoCyjUeBcORkSr5T3J51Z1r2rP6ihpJz9mR7K0x0x42upGfyQ76oxc8YPn60OEXl/oQy2MAQ13HelEPtBrnhF8Zxi4kVBIHj28'
        b'SK/F9woLS/C9+jiWEbiw6CK+hE6rYJu1drKiMEbmjN+DmCQW3czERxoOJecJlckkdsC/8dSP0k5vP3ruNemBiTuv73zD68PfVf2hKr9GVs37Y1+o9yrvld5lnb9JFCat'
        b'fZPPPAq2+6nm3zj2PsNMx9S/u5GBG72sM5ZWfRlX9YMC25FFQbYTYkYYK4EHf8KkEeapgS0THN4j14iTNKOu3Q0kj9sOzElWfAitYBxiXaDem/TtdDGpdTuo1/GD76zC'
        b'X2XGU1OkohmPijgCIuTw/rVCzrOHTTLXxv/gJ3wl6Fm/s2frqR9NPr19z7mj5+io9/rESYm9dTu+ebX7EzLzMk2fCvCBZjLvToOBtgt3qtA+F/w2OjPeHu3YHdoWvFPK'
        b'M6lcHh2STLSzLVUuqFo2bYQ++nqdHcx4S6xqZhuakpXpeLQpmeh4jP/BYGhIqxj9JLx1vEn4O52Jn9KI/p/JyWNmXmvimkBW3vDzvFCeErg9stkd5LXgnRM7tyc5ia8y'
        b'zu/yKiprDOrwFoIYpw5vuSfF6cHTSnfQV3oOqXQ/vfns80tdT8k9zEzMyg7+Z1cugKv8L6vcMVprRpLMx4e3lXOFSjggeUX2GpXFQbss1efG8ANhkeOCh5OClh0YZiuu'
        b'7fpP27rhj4kMMyRSC8/9PosIQVA507LQHbxvJu6IzY/jMYLZLLqNXttCj3i24Gv41OgJja3wOQYQdA7teQwLg+j56EgMPdrFvagtTsTY4vs8dFiB91lpZtQ8ZczWJ7VL'
        b'oc0slGtmfy6CZkZtUx75TRnwm8LBOZmDIT1/83vKVyPNml/hv6T5KUDUN1MY8zNU+D1og55WFcZAVdWZ+tQ3KKuK2typKqtRZbXNp823zaZN0sYnSwO/Nv+2gDo/ozKZ'
        b'0z9dmWzMFoQ1ZbI0GadL8ho+tk6v3pSNTzMiMc/ZN4TTbQoigQ3qQe0O+MFGBb6Nb7uANgvVsnFF3Tx8b2ugKhUyuYzek1MVmzzS/kpQL+jZmCvZpLqbqtngXa84oNup'
        b'uEsqUkFjwRdi8OvKKLJSuQN37Qzaj27jy1zc61FT8E30DnpbRcjHZxl0GO9Eb1HFoCLUW+GAdizDd0AZ5jaDzuH7NvQt9Dq6jncr0XknsIjAbQzahQ/hY/QtvBsfb3bA'
        b'N6dA88TXGNQZgfq5b+3LRNeV6CRWA1QwPgKaNW/ju1QVZ3MhVXxzZRw3FoVGKhkuqyvpM/HNcPwavg55vUG+67uVZlWCL1QpUTe+PlokfAffU0E/R2+jB+6UXxZswn3N'
        b'CnyrbBU6nhcD2gicTlI76rTbjNvRCZpxOT6SkoTbkxIFDLu+lvCDLHC2o6uqBMqPi6jNTLFODx3hwYuZO2c+PpZUUGbDVOBOEanNswIVbODZOqLuJJIMrBgmMhO34tv0'
        b'cSo+louPotfriJCUwCSgjpDGb/9O/rFCqpD0MHprY/ScSYwqA8rTu7al0ABSQVaSebGwvjyQUFARhe+74D2EirIoKT40Py+/GJZ5xaSVoDulUDjRGqelpeg2zQYfJ7V2'
        b'GtR+TRNCm8J7/EvxnoQSPZvyjOfk5bQ1XUH3HfENfHarainJZrUiwIkMkoed0LZEWyHeVoHPiPDBcqccN1/btFJ0H+2JQu/gM/hadv0rdnXidfb4gWi9LdprV+KI+khN'
        b'difidzZJA3Hb9Hh8UoSOZ0rRzZmT8Qlv1KksVYHoj14VTBHi7Xi7EzPRlo/6KtCNRfiYCO3Bu9GxaLQDv4MPoYPlkoYtqKcGd+BtEvTOyhAJukua9U50p24T3sGfGEVI'
        b'OBCIr2e5F5PVKx2LaDuLdfZlJ/MY2zneCv/sBUWMCoRLFXqD0LavGPXOwW35pOgJeA+5KkFvOJropKG38mTFxXQNfxXfdahBJ5tplttC8pl2hknU2DbYf+63hFHJyMN6'
        b'9Ca+AaU4YccEOQrj1uPt85atQkdQL76Hz7ET0av4wvQkUhtHq0hf7MUnKyLxG4sI0ds8y9GrtaitHqtxv80K9MB1wxYbFYDfqcIj9DS+GWJGZlleXIHQzRP0tdElKfkl'
        b'HQtfscN3Z0wrl7J0oEGn0bYYvA+dlJLgUAI+mB9LBgxSu2JbQSI+v4zbzLhB5seewriC4rI8uo2QDyqfMfOokrixyZNx5u2U2IKi+Py4aNI69kodGxrRParRh05IphgU'
        b'+t4iDBir1Geu0ReI3iX0wUA50Q3dB31Gdjp6jeGhg2wm7kIPVIBrThawN9DNmDzCuf3FXA9IKMiPK+VUcY26nVEtMoOOI7pcvha6/5zSuHk8ZkO5y4YaVxUcfaIzWyYU'
        b'ov45VJskf65eMVe/Z5NXVEKLGz/XtgXfmZtXUCyLjZNRrV/obkalTjpA4/2lE9AFfAHfoE0gbBqfijPtaxpjLyRkENGTwsu44368o1A516AAY4v7eKgNHapWzSGxKVPT'
        b'y0qkxehASX5sfsV83GahZyzG9/MqGNLsL6NtpG6P4P1LgtAV1I+684LRe3nBSeiagCEdc7sbOkFa0G5Of/TUrAh8E990sbPFN1zwzeZ1KpbxUPJrakvwZdxPh9XJstYy'
        b'GKz4DIsOL8a9DO5tZVRgpQvKZPGF0ji6fyUjVEURuahbZG46vzTIFr261pnq30aiQx5lbugqOlCOD1SQriGMZtHJBbV0xwHfC/RwaHFm8YVShsWvk5HE3Y3Wdiw+i98i'
        b'DfEGvlPEMuxUBh9Eh1kVpyyWg08VjmoUOSzi4RO++Co6kkN1X/FxDDpQVAuOz/BX49OcFlxnKv2kEz7kSXXJnNwYUCXDh1E7JRSdL0I9nDKokBGg7TUBLDqP9nlxCrX9'
        b'roUGnVt0WcA4uvJ9UJsnuhGjgr0VdJFU/SXSsKV0owwdxe/G5oNWFJdbBNomrJuLzqlAvkFdNcWFr5BRyQAqRCq9k4eOESHzJG0TZBLdi87GGHWVHOv5G7xdigmZwJm5'
        b'GfhsIWkOhMZl+K6ARWfJENJHZ6YwBT6B98XJ8KEiFm3HZxjRUp4n40VfS0Y3svC++IJi0gxD7aewZCC4gO5zc+i5OrwT+jSJWiwhpX7DFqtpzJYWBBnSGMeYmSxpW7fm'
        b'0EZU4SE0EEhaJ3Rb4RT0KhOMjgrt8PEIFUjnUvwuBv2lPd5rS2R4P9qTYOCPKW9kaLsNbi+dzhX9MupDx2Pwia3x+bFSMvjYTeMROtv8aQ1Nm4nOk5Z7S4lv2pAhoM0D'
        b'v8XGRaLLDefwEF8ZRibKSbO/PTCvsGlotuuyWYn/cSDY293WbmL+k7wnRT/Nufwk8vIvNy4J/l7ePHmIs/aJ26XdX2gKy//8O3fxH0Ons19/HS/xLPz0648/SUn6nNxs'
        b'3bjVzpF/ZMueHI/Af+uZ+chu4VeXIiLmuExqQD3vf9iR9ftTabsnaW+eKLjrFax8/O6HIb9omCxeteJoYfL2Y9V2t7f89vTH83trHvxmvtObSTWNaZ+84dATucSr5HO/'
        b'v3ud8DjxcZXvf/yiPvXHh44vCdnno1v240in7YXbfaJFw18JfnQr6nc/uGJ7frfb1GiXtlm8yL6bsTv/3K1envHR+YrGAfukwx91nMifu6enzXbRl5ePY78nsZELF9SU'
        b'vX/++0Uq/1dLo7940PXJxItlrxdG/7yv/d7FT/6n9U3FpmE88etD3X/Y/+6MSbytr2kvZ67M8Kt/bd/f3Wd872cf5yYU1+35T/cJn7Vrq/lznaa1dPBn3Vmh/I/dqau/'
        b'73VTlzxh0+RLf/s84s7Dz7//6Ejx4k9WXfqsV/fJxv/Kvhr3PefHXz6ZM3/P6qbyTxf/15G7nr/8+QcJf3nl1p/6Yv7wruL4fcm3Mt3OT4r//sO6y/nv/PK1gzce7U6f'
        b'cez8lbimU4H/Z7PP0oyUdeVRv7T/9eSBv+AzH64LOXNs5qGyL/3uDAc1XA4Z2KydFzqc8+WXnyrORZ6+4vW79e+/87Ov2Lq7R2tTXH9ft2Zw2aapR9I65my1varb+Yeh'
        b'e+E/4Kc0XLrx+safO91f5TK99PTKlHq/R5nZNmeDjrZc/qLSZ6T9YsnuK5skrV83/5/3PvzZr9M+Cv1Z4ZeXfqHM3fvJD69+9uF/XBh0/smXS15PwImDP57q8Muqbbd/'
        b'e3ll5qHsj6aduZj9384/mPL5/Mfyv/7x044PhGtX/Nmr8tcn3F+/7vaOLnrwI43w48u824dbsr9yeP29R18V9vz6273X/H507S8Hs/7i8eXMyLPnHvzkh01zZg7/+93h'
        b'4W8PLvxW9munlIFrKr9k3Ts24h+4fLj84adb5VMO/mb4i2/3eK59sM354Nmdn4tbdyQ8/uOy/3nre9m3phb9+Xefz/r49V/+3C2mOHrBnuib138jUj5Y5yV67+S3BbOy'
        b'22V7cxbsOfSTr6/JN/zx5tWCXQUlG/6iu/Gr9aXef+X/KUwzL0G9rV4azukqq1EnGXQs1FQ3kTn09YUOnK7vCWd0CLSM0Q50maFqxntLqD4ufr0OPaCDKGoLoKNoYgxV'
        b'o4wkHf6mAz6/iVNxNlVv9kBHOP3YB0Re7o6Zk2ZUYLVFt3ktZAI7TpfRhU6ozXx0nxyBrxKx8A1Of3ebM8nBMLij22vp4L4Fn6aZR3qhu5bK17cr8YUWvJ0qtZLZ6xQ6'
        b'xK3ShehGKSNayQtgOCVkdAe/Wx+DHqAd0fFSvJdMdnYLYfA5h07QL5PR7PiKmHiY+GJZIkZeZUToIC8uN5CSTeTDUzmFU/A7JiqkLvP4jZvLHkfQZR7a6U8VbolwVTIq'
        b'XItq8EUmsFBAxLr7iKOxAnUnx3AUBONXyUd6eUkpuJdWSSo6upRTv25cBgrYvDgffP8x2NaULMNXlWSWu4sO2K5zwjeUYJBhRRUa3xahd9FZdJGqNJPJ41V0PUavLUrq'
        b'49Z8enDjls9HanSL5E31wq+IwgsNp0UleI+SqmJPwLv5aH+5HVXlnY4O4XtoX45DAqnxOBjkC20YlxL+Cnyhkmtu70lxe0xJLFlV7aORDvhdHnrQiO+W4AM0C3wCHSZz'
        b'7Bn8loUwdBTd5LTeL+H7S/VTX8QkmPnQ28spgfNS8EGDYj56rdjEYhB14Nu09pxwZ4JBnRndRGpGlM8TE5l352OQashMX/lMzdxsfJHM95yeLT5RTxZ95srgek3wVXjn'
        b'ejLb7eQUsvHNVitKyjwmuhbtBCXlihJaeJAYMJG/31sQLy3gTtuEjAvexm9atpzSzwfxYh9pMhwDHNbwZPgwPrVmHd3TiptL+K+fqMnalM7UN8NpcyrF59G7RrGmqR6k'
        b'mhq0izbaSNIsD1qINVECTwXmiA9bVmQUaTLmjhFocA86RtmPj3iRJf0+ae6oNjgR2rzwLoEbPip/DEZAC1cXP0V12mRXTYCO6jfWhOgwp/zfHYlOFhblszxHhlfKRpOG'
        b'vYOWbCN6r7xwyZLYKDKMFIIR6BXeBnQ9TBr1z9Nv/tcGSvD/YKqoMBbq1kLHesjFAs2O8+xi3O2ziKVbjVtF3I52eTATFNbV+igwYSAwoc+m300bmKYLTAO94oCOTSOM'
        b'/YTF7KA4VN3KHZd9FhClkRZ92PzxJq10kTZgsS5gscZ78XBUkcYjfDAsqrtIF5bct7xvXd9yXdi09uLB8NjuJX0hfRP7QnThye2yQXFYj/OAeIpGPIVEXaw8X6kNn6IL'
        b'nzLCZ7xTBlPzNEVLNanwOxg+qU8+EJ6qCU/t36KZWzEwq0Izq4J+Pe/DmVrpQm3AIl3AIo33omF3n87czlx1zomSrpIB9xiNe4xeZbtFG56t9c3R+eZoPHIG/YM6y9Re'
        b'3X5a/3idf/wj/+QB/+S+Gq1/qs4/td1+0N2rM1rjHkZ+BwOlem7wtYGTdYGT+0p1gVPb8ziXIFMPb+7YrF43II7SiKMoPXM0ZUu10qXagGW6gGUa72WDYv+OrT0RuugZ'
        b'GjH8Poz6QTyK18wt12ZU6DIqyBP6mkwzd75ubpVWWqUNqNYFVGu8q4fd/dtTO+t7hD1ydSvnO2KEcZoQy305BVS8Tb48wmP9s9lv+LzAHHCrRsIRhueTA9rTCVO0HjHt'
        b'MnXuoCRZI0nuW6OVZOsk2XBEXsXSry/TBlTqAio13pUjfHgITt0SNWLSArTiqTrx1BFG4Bk7KE3sdB4MCeu06bQZlsaQ6+CER8HJA8HJ2uAUXXDKo+AZA8EztMGzdMGz'
        b'2p0HfYPPxp2MO5HQldBuM+gb3hmjrtf6xut848ktVbRffzitI00dyina00oyqR+aYovWPULnHtHjZlKRpVrfMp1vmcajbNhdTOgC1f5R7yzqSUe2tG+hZcrRBuTqAnI1'
        b'3uBXtXNT56aeyf1ZmsB0bWC6LjB9QJyuEafThIXagCJdQJHGu+j5NcjFHTPBL+xSVl1/sel8kzYiRReRwj0Z5HqKwJNcBoad3Xpya8/63k0PBR84dW7VBsp0gTLyDZ9V'
        b'7GchsZq4xZpltbplDdq4Bm3ISl3ISo3fSlIDJJbUgE/gWeeTzprIxVrvJTpvgG6ivvbg0DpFnapO7VnRz9eGpulC0+ijwcCYztaevJ7ifvZh2AcxmkAZ97X2PNJYPQPb'
        b'F6lte0K1nvE6T0CHgvSxnZt7FugNB/IGaWtb0WOrdZ+oc58IWUIBIs9uPrn5xNaurTQbn9BOX3Vej1zrk6TzoSYZSzmTjMVa3yU63yUajyXDXGV0parXd7f2lWuSC/qX'
        b'DkqCSYec1ZPbt+wbPusN2NYQtgsII0nSNI17JPnl+qnWd4bOd4bGY8YwuEANhRrOYakP1Jj2rPasYUlAZ1Jnc9fGniTy06xLyNDGZOpiMsH0wvuRNHVAmto/VSvN0kmz'
        b'yKf8oC9A2E5dM3p3zFBnD7hLNe5SACDLGvQPVS8/sbg9pz1nWBLSNUsnSSBf8I7sdBn0CBvhu/u4jTCGYBgc5Y4I4VbE+Id15o7YwLUt4xvc5dfpN2IHd/aMT1CXQ6fD'
        b'iAPcORrinODOmbzVVdJZMuICd65MaLQuJEUTkjIyAe7dGL+Qzikj7nDtwfjHaPzy+pwf2mgS8jR+8z6c/2HBtyOeEOfF+IZ0eo+I4dqbkQR2JXQmjPjAnS/jG9DpMSKB'
        b'az/u2h+uA7jrQLgOYkLi1JKRYLgOYaRxvY66qAxNVMZIKDwJ42gIJ9ftwpFY8p7OJ/aRT+KAT2Kfh9Znis5niolByqB/osafRPS98tBb61+g8y9ozxl09Tpuf8S+M1kd'
        b'pXWN0XE+IWMnUVMFdZbWVTro6tHh+Mg1dEB/r+NcS4r92h1NjrECuWOss3A8RF0ZxUCQQA0Sal8xqtua+Pd5EWuE72hehh2QMTYN1kyenhi90I03BUfDuZsHa27oMDeY'
        b'ZcuoIcL/P8PvzHgCTttv26U7MO87OKf78KUsde4kew61QLYN3ASJ/qVqgSukvC8+5VlR4k2va65VBNVUNzZSzF0wLNBjEJPW0ADNoLrRDIqXAziSyzmEu+qgNbXrx2TK'
        b'qbRHVVXNWd2cv6aOtMTljU01q6Txethkg1qwSllbp2oE3dwNTaqg9dVrqEqsvKGlQT5WddaMiIY1NGEd9cCs901Xq+Qc1nGoe0EAOBPUIFeOVawd8yB1bbWienUQOI5O'
        b'Dcqn6rmkJysbAJqYfAdUdauDalTK5qbVXLbGouXLq6qkAGoxrkYz4Y+BH3DZsCaoJSV+EmFFBmHjemBm84rqZiO1o0rTVnPUl43iJVOrBk41mWQA6MlmLDK4/qtXNKnW'
        b'UpwzqzmSojc31KgaqxWc8rVybW2N0R+2MigKHJ7GEhaQz1KIgQ1ryW1tc028lFbCOMrXwNDmWkO96OudGq2sITSrCCNJ/tDqNhhqX95EHQ+uBaRta3maVcDYOn2mcoa9'
        b'jO4bi/FBuYnLjv4GnnNyMnemDbsOlXPw62PcM6B3lpAXwT/Dejk9H0Pq0MX6Q74gWz7qxqfhKPHeukTc4RuQ5x6+bjO+Vop2orcyUcfijPxmdAWfQ322M2Sx/rgLn8Nd'
        b'Weh+4EZ02TURd6Hb9BDGv4A7h1OXtRTUxsxkVOAkFr+H7irp1nhZFNhMgzMQ8mcduldow4SsFOArq/Fu+jpbwzmDcA2si40Pncw0BHTO5CnPk5i2rhpOPXfaPlbklTip'
        b'ipXulxZ91OntPS/p/ayVPqWdq7x/5L33wfZ7X5zP/lX413n3FmxTxCYu85Tw8ST1b698MWXyxJZJXqvW34it+l7dbyYFLXP6Te3195d+KFugEmv+PWRaxC7Zm7Kc8ull'
        b'C26+Hx/9q4QJWQqp5M2P7L3LtgW7/8TO/T/lV6s+/l3zr179z6prv6qtyqvbm9uWKEhaW8cweetDQic3Sh24rZzT6Oo8dDNvrHk6uob2ctssb+Er6EphSRy+uoil237z'
        b'8AWqHoPuoLccTJbx6D66/WwFGQcvbpPgNY8lSjggjYtqwWcMJ0UTcDsf9RWU0wV9Fbrva3BZUl+r3xj0Kqem4KS5bHMeNdtfjg+xuBdfan5MXbH0Vy2lVvuvhJIhfDOb'
        b'YzeBvhSBzgSMeitAb6JOXhzega5z+0098iAHy33KNJ7Adjk+ye3x9KQ7mm3xoIN4p3GbZz06TBgGDWgjvo4PGjZ58Hsp5vs8sMmDdm15pg7s6BreDrw60U5toVZqfE7X'
        b'7R8z3Lp9Wfg46/bBUWNXsgzSiaMBX7aE/TIgkszS0tnsYEbOBzFEUpaCX282sATk5UBq/+hTwg5LAiH5VCLxBoWBpfGJ1q5WakWdPBCYrA1M0QWmdAroOoydMKUzszNT'
        b'LTiR35Xfwzsp65QReV5dqfVN1vkmazySB0Mj1Wk9kzmbV1cPjWsoyITrtOAWPNTcD7OZOnb808S7serY9vwxirhGjr1hroCdGc6y3iCrPCP4bhWw2SEbMhlXktnYuhNd'
        b'KsCwRsdxnNs4vtFtnPBf4Tbui28FVgSYsto1ehRROn0ZrSJVSk6gqaVTCpn/sjPyM8uMyC7x9uNJAbXLG2qUlTWNDSSXVGpwZICHqQNAwpoV8TRFfDaEmTRZlUm24+Sq'
        b'524qtZiKNZpMAUiwspaS2aSQwwMyv1qd/1LrVGtqnkJDfE5FURWF31KtbWyqlhtKb2CI1UwBlNMIpwVTs95IUqlqaAZrKBOirM/Kz6QqM7O8KvZlX6146Vfz57zsq+kL'
        b'Fr30V7OyXv7VjJd9dUH2pJd/NakqaBzZ9TlenjyO0Vp+HRXl9JJkrTw2KFrf/KPNLN/MTfOoUYp10W88g7scRTXF2x5twy9iWzcfFgvcqNCSFJ9o1luoTSCH4sp1J/LB'
        b'lobql+NURnmFFRJSOagZJTfGcHRw3a1B/gz51prSpifnFezBchvGMW+WgAmqaqxNbtF7BdubgHuUDjx6tHoGdzPoxGJ8inPPd8EFbWNW4ZuJiYlChpfP4DPobjinfHEY'
        b'HUKvxcjiw9KJsIVeZwvx7nKqqJKGe9GdGFlBDjrHIzGvslP5JTRiArrREiPLR8c2wRttbBraNkkqoB9yWYT3CNBNqt6DbwgZvi87Y2Y0VQ5Zt7kEnWghMX3N+C6ZJ/Ax'
        b'NhgfC6FE8NAOpXKSAr03l8ewTQy6C2du9FtoW9PGCRIlvuOiIITjN9no+XZUPRFdCYnB4Cscv+GdwCTgi0LqFK9IEKDUK1zi4wUM2i8vkvI4hdBj7MJXnMwoI8JoO1X7'
        b'mIR2kW/2Z1tQt2MzpxR6Dm1fXoVumlJRiM9zCkTno2uA8ledDJTv9pPyOX2enQWkWPie2Sc98G2a54qU2eiUxPx7jugyLcP6MnzFN8OhxU4pYPh2bIIfukKfJ+XhS97r'
        b'HJwULgzDj2Vn4RPcager57r6FoNiioMzy/AdSUxHqSqPCq3ZxYWwmCij9n3gw46sLgjR6EgrWbnsJ7LoA3RCgTpQVzm578APcDc+QlYvHeiBm5AhQnmf44ISdId+ho+v'
        b'oXtlmKxfmJVEEj3J5K/CbZxy0vUWG3w0B7eDKeH+MpIU7WHT8U20reEPS8/xld5gWLxrNlhvnTuaTFYoN7yrez12eXx/XkR+f1FcZuRi/mKnTPuyKe5tn3/vZz+cVz7w'
        b'wyPfEzx6v+vHjuf3TSpbsK09eWfczs3OH/HqRLHMikiH/e84rvjNyv53bu9P3p+9RurnsGDdVzWvXV/l/dNOzeNJqhvxVT94s8nH9VrOtzvfPlrL2kxRJRclf/zRtpmL'
        b'nP6/ikQs+H6aasd7+75M6dzWuiHorPuPDuX+d6H9fJ/Mw1GaZtnXV3NVTYkFU7vXZhYLfvubkMxZLke2rPnV49/8PmPidvFXGzPVti5FgkavhMNrqhc+zN115S/tS35c'
        b'smvLlrC/8uRf5Tqr0ic9Dt19z3Xdk0LdhBtS3ocNG6fU7A268dvZ785xau/6aNfKHPfQehGj9F9+sXRQ6kGPVytU+EzhtEhzrbKrc9AxujCpDFqNL/gbtQ6oygE+n8w5'
        b'udqG9m2IwW15hXFGE0rHWL5NHXqTHl8Wok50lKymGkhPpaupOnSD00W4VY7v8iUxnJ8vAdrB4tfC0DVKjie+5Yzv2Rpcoun9oaFXm+mxLT69HJ8yLJTQHXuDCsWxFEpR'
        b'WB3eFwM6CPlxpD+c4DEkHx7ajtrRZfphfJ8MUG8rHfDt0lCWYfE+stLBvRLOAdpR3MNH+9YmoxskSxK5m/RkdMeNnjLj1+XkTYi87ygicaQlH/ZaTPMswDsnQEwTughZ'
        b'7mFIM76P73ILrYuurXqnZOgA3m3ibMw5jCPoVdyPTitbnO3xXfI2epPBp9DhaXouubYq0X7UFh4A5LQz+Ba6iG/Qlar7DPQaeYt0k1NC8tpFBnfxFtK3luFdxWS4cETb'
        b'0G443b9KeIZ2e9BSCNGdKmXLOvwWOgIf62TwfnQulZY+E5/F/SQO9eFD5GvodTB1PY/eojau6FYe6nRA/fpFrPkKNh1fIauW59g6hlULTDWjVq9KIltvnGBuP0ge0TVe'
        b'FI9b462JoGs8XWBin1tfcJ+bLnAyrO9822cNBsb0NA8EJrXnDrv7jjB+EyZ1kmRJfS0DgTM0gTMGw6P7sgfDpH3JI3zWP5UsavxTP0+dcS+0X/6g4e34B/EjfMbTd1js'
        b'B4s9siQMjbg49fzUnvLexf3hmtjZ2tB0XWh6p+1gYOjZTSc3ndjctblTQD6pX2za9odpA2fpAmdpvGd9YwMZjNgyXiHq8gFPqcZT+qmH96BnsOEOIA43aMIma8TwO5qJ'
        b'QBuYrAtM1ngnD/r4d/mo6wZ8YjU+seMnqB3widH4xFhLQErjGzvs6dOxUBOSqvGEXz0QI99zirUXhq19Bd5XRwx4Rmk8owYlkY8kMQOSmJ4srWSiTjJR4zHxu0oQPuAZ'
        b'qfGMtJbgS6/A9obBpJRb0/vIz0PBB3YPyc9g0qw+wH0LTjcDSQOvWxmsyfpZxLl2cjRdZSkc+GPNg0SMwcs0t4QOhSX02Lb4PqyeFYzRw/RWsnyWwgJ5/OA7XTkbjPVA'
        b'9lJcB9cmYgv4hyFBZUm+bMihMrOitDRblpmfXcbhIRphIYYc1lY3rNF7U1KchwMl+1EvQtyBk9H5leIcBNTZ1Yfm8BEUTQKOdeh2A2WY1Pd/gaoIzAvPUA5RlMNplJln'
        b'/TfAzdYrFgCIzowkQF3Wx+9PelijcS8gvxy2oJ86uU/YX/Fh+KCXZMzliI1A4jzCkKCtcMSR7xQDWGvWA/uZTjWkzf4D4WyeHr0OThC/4bOSGHAaF9NWOOzpP4pZNxMw'
        b'62ZTzLrZFLNuNodZB6eog65xGte4QY8MksY3C9L4guc5CNsKLIAUJwMs4RTocFOgv02hmISm4HjZ8KFc+qFc+qFcdgzqIID1eVKwPk/abUlIse9MUfgAElACkIASgASU'
        b'TKMofKYIewBL6A2whN4AS+g9qy1vxNbFafII89QgiPEJ7rTVeCeQX/U09bRz07unc3dt+YA0Yh1axBq+iAnSCOsEk8nYwJZJZzPZEf561sl/hPlfGSr4jLNn2/zOUI1T'
        b'gNYpQOcUMMKTAGjL04JvyEuBxqSpXA7lGqcQrVOIzilkhDfdCQZi6yG8HGo1FQexAgqS4paZDkEzzDXkWMY3V9CAD8wyW5g66v/+qZUMSMc8wFB3FFdlER8wVTg8lS6B'
        b'HlGFuwZcFTvyA9eArwLoKtzz0WtX+QS5m9ydXnvIPY3XXnIxufam1z5yX7lE7tflsEhQK2wT1bFy/x0W5pOAxtJh08HKHTocO2w73OCnN+BNMoxfMUJt2ZEfeaz+mJYv'
        b'Dx2DBmLDY2qF8rAdjDy8N8ICEcWWy7/DoYNXxyO5u5P/rh1uDdydG/mqW4ddh32dQB7ZG2Xlu3GAJwNfbrNrc2pza/Oos5VHj6HAjmKkiCgqwYQ6kTxmhy2gML7CLuLQ'
        b'FuOH3GA0zVTUyhuaKUJQXa3iySSzfYWxCYLoTqdZoifxKsWa1AZlU6qyWU7/TkpMnDQpFfY6Ul9RylNh7opPTJxI/ifFJyZJ+UMCWUlp8ZAgLz83b0hQUZo75xI7xMvK'
        b'JqEdfLKyRFa08JJAAUuQISHdWxyyozs8igZyKaxrrK5XvshnJ8JnBYo4mPXiIUjgw7SbLyvjoOVeMK9pUqFFXoppNMOyrHnpTzJWNDevTU1IWL9+fbyy4ZU42PVRgDu5'
        b'uBq926r4mqbVCfLaBAsK42tWxCdOiiffk/JG87/Eo9AtikbqT27IrqgkM72oMiM/80kEEJ2ZkU8pJH/nVG+AebEUTmKVzSTT+MTJJCSyB2R2iVUs4uD8koBWx7J8WW5R'
        b'dmVGenlm3nNmNVHK5+gyFvlJisWLmYompTKD7lKZ51HUVF+srKc5TYSceKM5EQLTIS8XC3488R2/UE88rTJP6mCWy/9l7z3gojzyx/8t9KUpvS+4lAWWDlJFeu9NAUW6'
        b'2EAWVOxdqqKiIqIgoi6IigqCWCAzyak5k+ySJ5GYZpK7mHKXYMx9z5iY/Gfm2aUJKd/L5Xe/3/8SXrPrzvPMM+Uzn2fmMzPvDxa30uBp0vYqDcW/TknEiyTiWhqC42Z+'
        b'uPMzu99Q0geKefkF2eUrykj1k7b8D0MXvIA2mZ5LQQw54LQH6MCn3hjMTAVy6A0cDi3SdDnNJsCK2icRy13HkRXo1THESnN1nAFY8UApq7S4vAz1CNqP5GRV4yCLnMSu'
        b'WM9n6JvUl/9GeEAcW+arcoZn+MlPRAis5f8RCIEORXrk3jrN8L1tbAyPu8nnGJmWHDsJN6Aia6TDDNnWoWlwA0wCF8D+aYhnmgKVMZSA6r8dJbCTz/pou+I0K3IRNJ+v'
        b'aH3+hHW5XNIw9A4V/KL5mXW4pPKSkuJSbOLH/VfKaBV6v3ihgDtFGXBtgkP4P38ZVia/eIUX18ZWWIS3u6yZ6+Bh+yuSpPUT1yYo/JcvluohfLE995eeM7OO5NpEJP+m'
        b'O5x/5o5fq+5wElMzPdOSp3TZhl7foNGJefk5ZcWlspgZF0vxmIC+barYlJQWFZcWlVXQ3kxtbPFIwxZlCI81bKdfBbPFIxB8DR4P2OIlT1v8IrflO4zvyPJwcHFw8pZe'
        b'Mn0y45u3nMil0lTHf/YgP9NJz1QwGmwrLdo0cFq6fqyFhE87Y/WQbQPek9mbpJNNj5KVsjNnzNM4KZbOGN1fpyJfMV51bP/eNNvz8H8orhwvteNVaLL6R/YO5meXYYFC'
        b'haqYSuDFu9dmAHjiFUSUztrsUulWQ3yrlDBKaoeblJ+Py1q+Ip+bXYbGjjnlZdNnKyggOSQsLnFhVnxKYnxcUkhWUFxwSBLJ5dg2PwITnWavoLSSaCVE1098QESsjBwt'
        b'azeZSUq69jn9rrjx9VCyxk6nML5caTtFp9jOuK+QtFAJ3U+FpBKn3OtlS5dOdknRqunpojQ7F4266SVUvJNwFTckJXGGdd1V3KS1RWXr80tXkIYr+5nM0wpxhr6EOkxE'
        b'WfaKCnLjzBrOdmaZlUJ/6QYZZwFjyZc2yRgXmN5iMUOJyuhtkhPcHU+6dxIzekatRVJ6Yc0bVY90aCiUie+UdKdvEzIRmthTIgIDYrk5+SuKVxXilH5hbVh5mtGdZixZ'
        b'yzQFu9fDg1FwL6xnM+CpjSx4imkDG+FueiX4iIVJFDigNbY5kqW+BRymt0bi+OAiWC+EJ8AV7MuNduQGz68mgI5V4ASPA886r1ErAbWwD/1/BVTJMdTgThasgaJ15CJY'
        b'CS6gp4OtC8cRLQzGbNjGRvd0w6MEEwJ7wfG1SZtKx8kYM/g8Q2PVOtinopwJrkvpkRtRAWQrnUFgG17sLIE3yfKok6EKvTZqAq6Q5dFja8g+zkxwsHyCw7uxfM3RTh4D'
        b'WpSoqSVip3c2gtgUGxtYDWsdYbU9dkxGe9MT4OWmI1rMlNBQsnxbAE7Cq0JDsJX4WaOdrKXAJrI437mS5gS1rl4bfcWVwyDgErgNDIIjsEbPZ5zTEe4QGQOrUIEdE2Fl'
        b'dEI4OxFUQfz/NXC6wpIBBuU4sFEODhapvpfIEr6DUnlN9YeV8ddVgJP2zYiWiM7W1tYPPzF7ynRY25mho1ikJ/looCZolnf553HrM8KXRrK3vdcc9vrdsC0f2Q4JDrRn'
        b'KIsjNrxZK57lyAvih2gfbGuPWbB/QTTj8/c+/1BFvsMo+fnKh5nQK61B/+nFtO0p+7+2gPDJw3hjJ9tX1Kqflzsn3s5dJXAyT6nJGind8XrvOiWXxstr/l6kc3SDqtNf'
        b'D5csbLPaVPr33fxerU+MEuuaVuZu7Au0MP7uUenf9be+E/VV8/YnRhs+3ZnxacGaW103btQUDX9w/cMvvlPcw/MoPhTPVyNLY+HJsNMOXJFzENBbJttZTvDKXHrj6IG4'
        b'MtqrJnYMao83fCp6KjLUE9nOJWAvWT1bGpZIFiVBl/34ue5lYJBeBKz3d5JuOlWAVyfsO9WGlWSd1A31kCjYDvuxWyu8TgpEAWQtdD3sDYgak5p0cJk+WG2UR1blYDvY'
        b'Bs5N3scJt4N+cuYcnkkkh4/5sB8vXJIlSLz8CLaulK5Awj1x9F7P3s3g4hTPSYXrie8k2nOSiipZW02BXZ60kyuZhytWBPZxBTvjSQ1GLV8kWybWX0gvFAeBG6Qcm5EM'
        b'3kSPwD23h80IgyJ2DDMUtAfSh+1PG8DuqDIognujUflzmM7wlDVf9V9aE8CGwonHUyZ43Zh2HjfRGU8ckwbQ5dkxZumKdW1EPImmI6XpeF/Tc1jTs19viHdHQRyfMuIV'
        b'PFRwZ+ljNnPWArx/FIWjdKjAMDRtNqpXGDEwa/UQG/Dr5UfM5kx7vFRLb8LZLD2L1hViPRf0976pTeOyEU/fG2r96P+hNUNrRtlM2ziyVzWe7FWNJ3tV45kP9YzEZo5i'
        b'PfyHj0MymLZkdyvKlW0YuT6cXB9Org9nPjTijjJYOi4jNoJGuWa1EXvnRjlKn/9QSx8fOQtnNobeNxYMGwtE+RJjN8rYjf71obZ+ffCIjnFDZqtFq3OrBaVjKdLuMhDr'
        b'uKC//rk3fNDHFA9Eo2yGrit9AfqbMN9Wm3DK6eenrjNuf1VjTDmD9CtbNwbP0kWMyQeO0mz/cz2oEHcdp5S9GNfUAxR/iweVAtpZiHwWnsbM5AxhuqqSuUSoQ1VVehZf'
        b'SlwiOPyKudJU3ybYUJsUHpD4QC44JDD5gVxQYkgwX3G6422l38vc1j9QzF2aXVqYLywtZE/hI2rICtyKgkNKM/IRMR1RsVK9UoGYLjQIB1GzclaBxh9LQfxINJ3pIiAv'
        b'D42nJ56jkQ3dprGVjw36X7SAFHC98ZTEe8kYbnnJNDsf7aVD6DHvCPggz4vnntDTJ2YoFw3Rc9BUqLi8bHxiVIZbpUw6bfxVE3LpVIoWml8xJ89eOX7vxOzQv3OzhdyC'
        b'FcXZ2NiGJlVF6JdV5Stz8qefv+DHrRozAeHRsGyLdQBJbbrdknQuJk1UJ2ZDNk0ty19Hz8JwrdAeIlbSh5BmOFWErinKw1OI8aoozSfHylDO6DJwbVBGS0nRyBTBIjHU'
        b'wcHBgj/D5IbePEpOyGVjaRKWlZbnlpWj1MdTduCGyvZeT4ifNr2xe4hklpesyJeJgHRjO5pN4cKiCd9KVJXTpmGTGBIagjcfhGTFpsQEhiTac2Vz4eSQBcn8Ges7nxyJ'
        b'w5WdvypPUFYsQB8T6semuIQ+IvgzKaybzryAfs0vxUcLJ5oXfjY5/N+Y9QHX8M8ZB8Y8dkiletrUlhavyEMqdVo7AhfVSkhibED0izaD6U/R/Uo7Ql55fhY+UUdXBfoX'
        b'F/+LCKxUbnC/KMsvRHKBBGTJktjiVVhT/MzxwnVl40/HieFU0LQRH+nDCmJMdAtKi1eiqsrLnuEc4Ipy2lxbWLQmf5VM8lHXzMOboG1yi1cJi1B14ZRQxRWRX1Etz5gx'
        b'OpmJRi7+xGLSWS3OWZafW0brg+mn1Ulxnh5OzkS4UeOQ8uA82Et9YEnLS6xOuG8ipThtOgXlpaSvkd5OjjbObFug33De3CTpXF7IXbu0KHcpOSlZgZ6yYgXqfNml9Iye'
        b'vnh63SIUFucWkUYYsyyUlBajjkyOpqCqlTY26gi02E9fmeNazoEbW4xUbUnJiqJccjwDG3lIf5p48nP6vhNE64xsqVJET8cvf64NCvn2XDwE4NrEpSTycWPgoQDXJjAk'
        b'doZ+aDvhKKsH3/ZXHLAd2+seMKbqcb6Tx7P9c2doftHAYSbd7nwaVi8fO91Zkq3HUl/CI8NaMv3eUqjI2LrFDI2ylkQHbTBikG3a6oUrsXd6eAKeklo14qxD6cWw3i2Z'
        b'eMd4io+MO7wbXCQxK2A1PIKdi8vFR0vRvkHpycS/dxmsBYOcNWoljmDri7YQ0AqbieUBzeN2KcMaqY9zJXR9sg0/EtTMxecUowS2qeH2kSk/Y/4g8N+LIbMwTVK6CRtu'
        b'T14wYae3Mjjkz+OVL0AxCWAvaH7hYT//JIJNdYhAQYIN2AavjRFM+QoMbydt2A0PM2lf81fUncY2noOeQH937fIKnJ2rCn5RhO8siIzD5hUbkoQ8PAB3qSwBdZYGoENl'
        b'3KoxH26DzSiubTbYBdqTQWteAqgK3AyawHZwDv1/Cn3uXr4O1IMzgTmLQXVgaVFCwrLFpZaZ4OjypZoMuNfPGBVyNzxBTF0ofxfKOfBqiSqLwYI3mCidWkdwELTQkN4r'
        b'2twZ8warDEDVfLA/B+yicwSrc6WZ2oX+0YC/4z3ySzTgHi4DdCXM0rcFB4gJajFoAE1ju/NRw59xBNfNy/PwIwdSQM+YrYmfKoU4l5SXJ8P6EjUNeCBZWvMTCMYlaovA'
        b'MbVE3EIy3GstrjDHuBiwDYiUyJPUYaUuPI/K1l4+H5f8MDifPAbc9kqaDrmNb0y2mdiksBfsUQuDR8C+8mCcyD63sKhYbE6R+v+pA13xRHBQolGghfyGBeqgvDASVM9G'
        b'Ra2GBxNBDahmwsHVamGgtbQcdQ1GcjDYTye0CYvgWFrh4y6gcT6jxtIDuzigQdsSntEBZ8FpXR02AxyNwbTa3oxyf9IpwSA4Mw0gmwVPEnBpjy9qn+1wJ6peclgBHMjJ'
        b'QOKxJ1E1MRbuLI9hYHo5qJ9g9ouO4EcKHFJhpX3qyvip1G1pttQmdxpUYcfLZ4P9cKtveRrO1Zlg0I95opgmCrduQIlOl/yvTTwxUhtlfGsWrYZqZ4cJsTERNq+V2hPd'
        b'NpL9psSsqpsJz9uhKjT2RU8+6OrkBHYuiWJYgF42uAUOwgt8VmxyUZLcennhu2iCub/z8a7k67HQSbu8ee1Bt008gaCSqbAk8OO0gUva5pyTqSqJ6d7cQkbVS3+rdE86'
        b'/COvL+bjl6veTa9u+N770dNnDwZ/NAOVao1/7lKd07PLMevcvKeCUcWa4V0v17Ysiuafb/j+yxobuZoU5e22vT26hm8EBz//k9biozb3vGa/srXN7NGZSIUvrmZmt7n0'
        b'PeBIRM8ue2yfG9k120/SVm/78oKvVuccy8nR/cn2EndZ/K6P3zu49F6EmkGWwoeHM4pN9p8XvV0VI1F4Ravz4p+WD77dof63O7bnNZZovrWFr9lXcTXps+vyxllDqzPK'
        b'f7Rd8n6PMP3JPrNZ216xW7Aq3f593ZqwH/76Y2au85X792pN5fZufkUiMu7xbN6VlK7mFxTR17l089s2J7bdF9xsWZt88d1dz/78jDf/PbtPnM+k73Cv7y71bRs8tS6y'
        b'13t3T1C2lvzAc9XMuO87/mxnuu9vm3ifJx055/HSNxrJey2fnbu+MLt/+0+aD47K1cWVPQg6EGKVE9Pl4uhsEX2m6tKtC9/oN+98uredbWAqfPiK4WXTL11bDI8q6xQY'
        b'REV/miCc95drZ986Ppd6H9Z6DxuVyl/MvxNaxIWzio9WKleDJot5/L+wPn3rvZg33jv3yvuhxlbrvkpd4Jo3+CPbzP/Mp9cD+brkBEYsaPclNkmkIdom0B6NV32L2TDw'
        b'IjgF2yadsYddYD+xd8Kd4d9i8wNoXs/FcE2LeGLtjLcglkpwxhKem4C/hEfhAXIUBemOGhqAuV8f7p94FEUebgfHwOnltJm2BrRFgJq16moqpbAXvVjL4oFITYGhvZqd'
        b'tDKMPIKFPdSNMzJRR95HOJmnUS9pIbZaV1hlhy2qoCd5CsQzT4FGZe4FO7RkB1DkwXEd6QGUJnCcPqy/zxAcnniwpc0L7jCGN2mOZj/oJB7F4iJAlxxDgVOxgmUBB+F+'
        b'YkAF3aDLnUaLniumAc194DqN2Ly6UEFmxLUyHD9FYs0irsrCF22aYsDF5ltwwVhqwQ2RJ3lfgSInMQ/d4DFVTbYOqHUmhtj5ueAAirYHHXIMOXumsgoYWDabNmFfzIV9'
        b'6HWdXTHB/IuNv+C4Ajl14gh2mtvJbOd74ClsPwdHNGkAaCM46BcVHQGqpnAS2Awn0D8LHlBw9IK9NAuyMcGQyE64PbgGL0TGoWGIejDbD3bB83QNHs4GbWMsBKQUFzKR'
        b'eF2BR0gNFupYgxrHGAEf5QIeS/JjceFpcJ6v939iVzquFdn4cmZAksU0NrjpSIWPpA7iCwS0g3grkZVEz5nSc8YmZ58RkzmNqa2houCuGCnLL/ThDBZnLq9dleI6S3GE'
        b'XPd6tRFzmwk+y+vVH/JsKJ7bfZ7nMM+z30TCC6N4YWJN8xEtgwZ/kbvYJUhsGyzWwn8PLazro+qjRnQsWvOGdWzFOraizUPaw44hYseQhxZWOG5UgcFz7o4dnhOIrjM0'
        b'b3FscpQY2lGGdmLD8G6FHo0h92Gn8HrFUe4kZ+e0q3NUNCsPbAXnPGYzrYKJj3QCUUMhpviFMGm6mVerwrCWlVjLasTIYpRsL5dawgOIATyQGMADiQE8kPnQaA6+12lk'
        b'jvVZ7zbvk77tvo1KTx9OPrVCkkmTJZNKkkkjyaSRZNKYD/VM0eXj/MNxDCSmOPLxLnnDCSnqmeIUQ2UphpAUCaWNEAuZBqFMjGLzwVlLpOGE8RLTBMo0QayfQK8SpIjt'
        b'/cS8eWIt/Ic3xxs3bBLrOXWnYcbesHuM2D3mIVfQrT3MdRdz3ft5lHcU+hTHZ6CQQPdSJBaplEWq2Dj1IT4XJJIX6wnQX7fdkDYVkDjskih2SSRPnoCVxPlWmhXEbN1A'
        b'f3ZvuqM+PDdVPDd1RJbdWDq70RLTGMo0RqwfM2I8pzkOFxddrtijSn+TFjyQFDyIFDyIFDyI+dCY2xxNGTtJb0nuyaTcQ3/xrlEV3PQ+97X4w1p8kaVEy4nScsL4PosR'
        b'MytM7XtoZl4f/lcdQ7GRQFQm0XGjdNzu6wQP6wQPpd0pEKcuEmfljoTEixPTxZl5SL50C3DyKKxnocpFSbAaOLjipU8Q2/pItHwpLV984MgZdZlRNv60d+qK6NcdtvcX'
        b'2/uPmFk0ClvdZFIlMXOizJzqAxvCCdKPJ1IVa7mhvxEb1/pgSttyhLRqtFjLCf2N8OzqgxtiHuoZ1CtPWCuZPSMRbtxkXrrsxcNNv0Y/4XWDF0Fuv0011eMFlT8xJi+o'
        b'LLJnMhPJQsgfFf6uyy0i5XmMW+oBqpOXWxRkRoGtKDikQLbZ0hvkFSuVKhkFCmMbbqeiSv4tjuCeLXnBhpGYvyovv1T4S4sJxHIptZZgW1m2kLsgJvoXTCKmjBdNInax'
        b'xHEOMwX2RY0d2wC98JZdwlT/KDVpNi8AkmAzOK+mAwfBMWLW4KGB0TE7MziAZ6AvzjN64UXawUU3uAxvCWVbH+BVUIlGXKAdHCepbHaHdTiyzAGN2xzWoCASg4h4eOl5'
        b'sfxcVTQ/wyaZJDRI3Y6fgRIxNVJjgHp/FbK3Ynb+hrH9Kyw/sA3vX8kEzcS4Y17ESvychb8tUWVssmTQx897w1A62CMSA58mhv3wBAMMwvNwoBx3pOSFKLsHiRcjhQJH'
        b'Y6kPqFVWsI+jXMpGd3SAgwkMeH4e3EFsHXPc4C47vi2mVbM3VzDhNjV9cp4/A41/6kAHGp3hxf5YeYaCLksVHnWi7TLHV9slseBxWCeHM8QA+xjgMLmN7QL2ynyZoCHt'
        b'PuLMxBDsoG87ZbpRaldBcd3kUH8QsW04g4vg1jgfwN6XEAluojomg/C6zfDWOFgADcj3GjL9YHUxTW5INsLGKTl8ZB9eRrp7NthDIwk64W7bMfMROAE7VZn+mWiWS8bl'
        b'sEM5CdTBhhRYBw9hTylKcUzYCPbCnjk6K7Aq1F65d9lTpieL4bRklWYKaZDtYRbzbrAqcYPkuGyIpk1wl+3DrXawuUyk2paJfNQn75VXlIkxthwcYh5hFDI2MhaZbWJW'
        b'sVoZ0/23kZnHyGPuYhmM/XIGpXduLM39rFouWW1lxX6OvfF0MB8oBuSVRhetyuezS/GA9oHcCvQPWuNi8NHYlnLcpdYLplGxpaQfj/vQ9V1RJCzLLV5ZMm8R6n1PsC9j'
        b'pGXFjgX03x3tbmaf8mXlfl6/cIjVL7zBlzgFU07BYxeQ1wmpm0vxaoFvs5Gkxi+JVvSMoH/8vkg3VYO1ANssM1cvSqYpdeEAo+qncZSDBuVH4sDxYhprcRnWZclsYEx4'
        b'Ct5AM5bLG4h0zQUHYCuKW62GZmq5sFKb6WPkQh741TJF7QcsffxA+2KBB/bNi19FnnpaUmkMK0GyaALO0ZvGbsi7SQ1eqA+0KDMdwTVAO+pRB9jceQXdpchgL5llxfQr'
        b'h418JhFDC1APjwhj8dyUxeHCZiY3lfuHiAJ20llahd/I1fhoCi0EpbVs2Vv3X5WB8xNlwLWI/ruT3B3QF3E5oj9vyHUocMj1RpHELZxyCx+7gD5qR4w91eCGEmcNvKrB'
        b'YrBVwF5lpudsLRKjjPToKc5sUFmKySZdDHAU1CXQ7dxGnAlcUYVXFZEiOahXgeKdSspxgTjwcj4+W5HACAC3EoT+pK/DHtAOr3JM4RUbWzt4KRp150hWupMc0R9csN8a'
        b'nC+CVxwjYR+Kkgc7mNg04Fe0f9YJlvAnpMReKci8uWBh8buhmosTZ/MTLtt8l6jtM690JOJL3msSO78DHqvWt3z+fv8jj1VLh7TbhzRe+eZ0iaTzTtDi7bdUbLit8Vms'
        b'v3z4rfW3cWXtjXZfLdvd/rczLFWNwkff33rHcu2aOxvednzrw6N3H7j+Pf3+ki7FLRpbBP+82mPwyW7vZwclFyq+6cx1+cvtGB2tbu3G2t0Rpw6+5XTG6YcK+SMBq710'
        b'Hh0D9pe48LzNmj3yC/tff1W0/c6z55WZnzGj9767Tf6c590n6Q4e685yH6j4ffG0OCXb7T73TOdflp/6TjfZvu/L0uik12o2xo/Me/fCmm/0tZ5yGgc5W27qvy7KiV96'
        b'/+13FhXmupfsfHP1ge+2t3UHP76t3N31bm+2dmtUbmHS7Ks2av0rEj6L1rxir7VZ7wnn9rmHy7aKcpS+qn05pq3avdi255iVo4fq4sT9wMZ5UOFpUXIh6+3Xhq8caDTQ'
        b'Ttr9D4NX/pK+d6v11fywliU/mS05+soCBcPlmnZf6339P2v7FK7fzVK4Z55zFX726uFrc79UuTfgfSAm4RPT4O/1tl1/vd7sqYb1soHEN+Vfi0hJup6b8B514pmt6F7d'
        b'qdfPfuymsHwds+HTII2upb3CvHvfRZQ1p+p9kRz3tu2SjKERueVHLd70Vfuk5rP+TwS71hQa1Dx8c/VCty8U87fe25tjM2oW9Nz963VLN1grvb70XuTS77awH9n+id+4'
        b'ZfFLzQ2NOkPNkfeC/iT8U+Fmj45lfm1PGtuerGvbW6t4/J0Fx+d9mG7x4edKWXWfsi+4VmWWHv9H5rPeL+9/EbPD7MFrdpVXTvZeaGHEX1x/uaA8++L/5Pkzrvlu+zTx'
        b'781zfnikJRzc+mjv377yHl3Ee3qCt+DbH1osvtlo+CTofonyn06YO70x+xpX+En55sZbtx/cWsU3PhJ4riKk+1OLz+YdEdk5Gz5htbZ86Lj+etalrPmSl58/El5Kcftq'
        b'86P05z9+o+o0GP4Xn/WzF+6oXg6q3D4sCVb/0axoQfwcR63qkH7bj3Nf2lnS+vWrK99TefX5rUUNN+3W8bJGkhxDc1dtdSzZ8erVP3+0pSz4869sc7b/rXOxxQ+OWj+e'
        b'azRruP/4BvOxyrZ+3QclF96oS+6zrFznfsP0b3fvK5kanD7vU+bh990FRq1GsPqaf27qffefP7UPnA57y9pEZJT+XnaMzxfMH0/vPPHZT58lU70ePyyv/iq/tM4sZd6z'
        b'6sFY0Y1t3310dL1rz82++Iu+ij+mpy4fXJxluNs3SazC7irWGrn8z9ilGl+9d/1lY7GpbfXe81vzv/bzslu4/3nMw00tYvhG955FNhWrHnoXvVHn9tlO64fsHA/qC7V/'
        b'VKonV0W8s822UdvExrTlvW22/fjL4E/qyR/5LFGsvuj6zjbT91EjPV/Tev9S5p/+Pv9QdGJ5q/MbI3tO/rWFfXNfpe+BlsK7B1t/uER9mdYSp+TXExsmUf7+myTtrz3M'
        b'hkYKd376aOdPHLAlt/m97y6NlK+u+vrw7d6v9705NLgt9ET4urVPZwcpz1W3tGXfvBifZ6n+zmef3IrdlXQxsiQF3Fb9bOnXK94v/6p59q7X5+rP7Qv4R8YKuR8+PPlj'
        b'0+3V7vM37jNvbTmx9/sv9J9set3w+du6T/JfDz1VPPvK98W31ql++PTha9z0JPNlrj1rGz/UWSiq3RJfvvzrjH8UyB0PzF36WOedzy8EWq8vfW/u3HVPBPwm/52pp0RP'
        b'i3cd/vHWV44fPW18fqTqXY3V7zd76Ao36z8/dFynYlNW5cbbsDSx5c0vu7q/dwzVzDDXt+QvJ2zNNLgHbuPYEnshXkephr0yg6QZuCKHxrDHQB+xOS6BF23sXMCtyW6F'
        b'5svRJrVrawzs9OCVSTs3sekuHRyQuqdxXhIF66LGIjWc2LAbni1Eg7Q2YjdMZxVN2EFKmx5BFzgTbD+H5HQVGvLWTzRA6sJrUhuk1ADJAVU0CfU6GiZcRy/uHhXan4rA'
        b'ITwajWd1o+XUbM2JJXGNFTzs7yJzNkQ7GnKErbSJuMMHDAgnHhJXg4NssA30zC9X+5aHrrCzAFuFDujRgtJYvjI/MsobDWPwrl2IXspu8JxCUoYbTfvZCq56yYPjUTJz'
        b's0IWyxY2G9Mc2GuwHXZGRdsqMFiLYtHwdy4HnCK5c0sFu+PtUYs4oukNzt0+liXcVU6ziRoM4SAqlMtktyzH4E3ahrsXHtDhgJ0hsFIAL8HaKDZDEfaw4nR1iOE8FByI'
        b'48ii4BX0ZlQDlaw14Ai8AdGoi94pW206X+bJzjofe7KLBT00n+i0Xwgng0vuF0SgR6uw0hKdSaWpGGUIbSPg3hK8IAga3OG+WEWGJuhml8HGElIoH+MUsLciikBcGQx5'
        b'eJPFhkdAG8l17qoMeCUKXo7jgA4bcDVcAQ0U+ljgtF8aiVYHTYlC7LFJGTUJPG4gz1CBe1mwJt2LtsnvAAdADy6WMh/JFC6zGrjBhpcTtHjgEm3Uv1oOT48ZzC9CEaFB'
        b'+YEOusXr4Ul73IR2DnwVm82w3RYbp2frs+HW9f6kIR284jnwODjpEAWv8mENKro6KwOcXEzTca9HqAn52rFMekgj4sM+UtmgRRdV7BUMrb2E04ZdBqgM8oxZumxwlFNK'
        b'y+rhyC1RsfagynHMHaER2C5nDFvAmWg+3eKHwfVIoUMEuKiKrkG1ocDeEOsPtsJTJIVgcA6c4EQKoleD8+FIJoV8JsMgWQ5UgmthhSpSx05gJzwjzErg4yzewpLXtJDu'
        b'tzvBEbcomQdMeVTTDWw4ABt9HWAnuSAQ7AcDdlN8JoH+JcXx4BgtLSeDXYQRtnw00oN7loEGJqirWEHHnF2AxPIKFx6ENfIMJocBbmguJyUyBj1wYGwRZrWLlAamBvfR'
        b'qxsHQLvhmEcl2G6NXSqhSTe51xFcTh1fXfD2Ij6VdGAPupfI/zHvdRwbVA2ro/nwphMLSUoTC1zngHP06kdHcrqdLQuVJ0bAZCg7s0AjmhKSp7ougWc4oBlcc+DbovZC'
        b'WVYqYhWFr6OrAe7G3lsrHR0iiC9GhgaoY8fBQzlmoJIkPJcBDtjDo+jRq2PxcPMsE7ZE0z3WHZ4uB01yHD7ch2QMpSsPG5mwF3YvpEt7CV4GJ8ZWRBwc7ZlgAIqiSKcp'
        b'0ixEgo9XUdhzUT1WMQHSbHAPidtYPD+KXpYFe8A+BQYnkgXPRs8hcZqb43CjlEbHOqAu7siGgxlKK+FO0i4L1NaifHSGRGNh6MeedGvhLlpdNcOLS9A8rBTvn2eBS47g'
        b'FtMIdhdKt9cPbB5fFkO9lTj9vAqO0B7rGtBErUk2GQpTYnJXLiK3zQmOjZrssm0prF8BruXRKy0H4VV4lM6qY54Jk6Eyn4WktS6SrDhFrJETYnYf9mhGd08khFhpaSNF'
        b'C4/kgevEyZo7vAC6hHAvXwVcsEfpIa19GV1koCkHbsFG2yB18igr0CiAR9A0UxYvn8qE1TlIA5E+XMWB9WRZjMFaLNzAdPTWIu1qGqoNjivglfo18ApqnlnMxYtgPy1L'
        b'xwrhNSHxRctEb7FtSxlw35bldLF64KAATT5glQ3qF4aF8AS6AlTBdlLN8mtBnTAAnIR7bSLX2rIYiuAgywvujKSXz6JtUHFRd8SbJIhIaLDYTIM8L3hApuCrF8pcg8KO'
        b'SOK+VAM2obcoFz+5DtbHCMlbCelSqTbUB+fkyvydYSM8R2vDlpQQeF2OfhGQ2dExJK5y8DqtDW9mukmVIaonJbAbtQrsZaG6PAR20h7DRIrp+E2MD1KkloAjTIHnfPrp'
        b'h4oshAIt1NbKsGot+iDJa8GDbNCCdG49/RbpUoWnpe5QY+AJ7A8VdEWQKA9wLWZ5wtjqGl5a64Y7aAFrBadyOeVqyqhCK+abMwPAdkNyD3MjOC+EtfhQiza4BK4z5yAB'
        b'2k8U8CakBE/QRYlYTS5Rgx1sNDvdYQlvgk4aL7hDALdHzWNP9RbrBHu/xWgseNMbnCaUckdYHWPPj4gBVaA+25F2ccjw9FUAbfAom05rFxpNNUuXFmXLios2+hmBauJD'
        b'EN6cD88SJ4VVtMNW1CL10zptTYEXlBydlEh75Dus5ZBrBKsjwHU9rGpnoQ6KNIEI9BOZUAMteeip46va6kls0LsmJqKAKAPP7AwkEbiHkc6jEsICnTFS8iI8G4/6H4pF'
        b'1WqJ3aEzwd4s0EKLWu0KsJ++k6gRd7YzOKcMu1E74lHQOtDqCI7K202Xf+K/LkPaDCqoxqtlRYgFZ8AAn5ThKhu0OwH6XVmsFDAm1LvhGZnPW9rhrXkk6TebkSbo4ZB3'
        b'IJan87CPCUSwL4Jk1gUcggc5TNQRqmUDHyUGK8ECnKZfolfgIBzkIMWPDYPXQAPswZ32BLxEXqKz4CFzYexGVFaVSEwaxbdrg51sAhUdJGrTBlQKOUAEuvlI5gxxW++C'
        b'x0gDccFlhjAWXnJUsbEFjaCB6GvNZVjQjgSSnJugt/VxeMXewQFVsz+4AY+iN5o52E2/J+tt4VUO7g4sPhTBq0xTNNQm3cmyDPQJkYqHVcrjpdKH9XJRoM8b7M4gt68D'
        b'e1FBTi/jCEjhFExZWqkq5KWViqr6AKwh++Zq7WIFtli2UUc+DPoKiB6wz4c3kQKDZxxtYXc4H2uiG6zwIKRWcewGcyG6tRFeEcTSNpRNTKQBGqQ+CVFNDMDDsCZU+KJT'
        b'whBvus6vopqsFDpElvOROnCHR9C4jcUCDRwv0lv8YdtK6bg5QsMGazo1eI1tIeflv5507OV5KeOnudhcG3yYq0GdlDkb7ONFOcQgXV2B2rKD6QsOwi6iJlK91kZJT3gp'
        b'glqmMxqM0kNM9AIfgNfslsJ2mtwpo3Yu4fD1/z0L9Eq/eIkQy8YL+1LnT/Q3qEBb6dYbzGjAIyv33qpSKshGJ4a+kcxjG162j2a+b2glto6UGEZRhlFi7SjMeDS6b+A4'
        b'bOAodgqQGARSBoH1CiO6hg3L7+vaD+vai1Ikuq6Urms9e0TfuJlzX99hWN9B7Ogv0Z9P6c+vlx/RNxLrR7TKtXPuc92GuW7dKRKuD8X1QT8OhQwp4wtMW3ntdmJ9AfqO'
        b'V4HFepGifLFDRL8c5Rkh5kfWyz0049arjphZNa5tXUM8oKmOaHPro1u1280k2s6UtnM986GW7ihDcZb1iKFRo3ljcHOU9MxYrsTYhTJ26XamjN0lhh6UoUd90Ah3Tn1E'
        b'fcRDQ6MW2ybbEX2D+/q2w/q2En17St/+MZtlpIt5b7r1QaMKDHNea0C7ArrY1GKUkcCaZfSYhPWhI3P4Z33bfE/Oa59XH42y0xot0Xaqj35/jlXrmrMb2zae3Ny+WTLH'
        b'g5rjMTF6xMTqvolg2EQgyr64tHMpenaLSpNKq0e7j0TfkdJ3xD8oNSm16hzVaNbA/+A0cVqD2yPFPK9uDzEvuD9Noh9C6YeMGJs1Kor1A1sDzka0RYjyujMlDgESXiDF'
        b'C5RGBUujCro3ShyCJLxgihf80MBEbDC/NbXVEH1gl23zRxnqBoZD2beXgWUj5rzGNLGJLz5F110wzMfLyiamQ+a37YDdCJfXrixKHea6irnz+hXE3PAhK1RRQUxTVFMo'
        b'RBVlaiE28WxNbl/YbTVs6Unu7c8eXDqwdIRrflauTW4sSmwZ1J8qtowZWiPhxlLcWJSOP07G33RUE6XSvFBkNWziJDaO687uW355OcoAD/CG1rxk/7K9xCOO8ohDzdcY'
        b'JjbOEslRNp7osz9hMH0g/Q7zDblX5e4kUzGLJOGLqfDFEr8syi/rsZF6GNPwWwYOR00ZBoYtak1qrWtat3TrIHm3jmLKspfannXf0m/Y0q9/mcQygrKMkHAjKW7kKJtl'
        b'Hcx8aGbZvOW+2dxhs7n9KhKzIMos6LE82wCli4JRJZysQpPCiLFJS3BTMBJLY8rcRWLsShm7joztJFA0Me1O6Ft4eeEI10rMzRe5dflSdvPQtyHn257A807wvWgqOku8'
        b'JFecnYtCKjpPEpRPBeU/xJcvpS+fj74NJdxOA2l3ku9lUjE54twCcV4BCqmYQknIUipkKUk9UuR8cW7n3G63Hl/KNXgoaShnKIlyjZDYRVJ2kbjECm0KrWXtGylrHwnX'
        b'l+L6jvBsW1XE3IKxJRr8l5BCJSyiEvLRd4ljAeVY8FhN0QM1FQoey6vi0qNg1BCXHgmxtPSTUveUcL0orhdqYhPcxCampEfh1vMVMS/Kd8qL8rpWSmx8KRvfx8ryOEUU'
        b'jKriFJWblHGK0U3RqL3F3DR0vVqnGpKJwsuF/Xk3VlDz4sTxCeLEZHF8MjUvReKRSnmkSmzSKJs0JHzmi5kP7RxxlfmMspn8RUyRrpgf0x3QF3Y5rD/4RjTlGy1xi6Hc'
        b'YsT8peKExPsJqcMJqeK0DCotl0orlCQspRKWPh0JCLytC3SlkoXEKoMKz5AEZFIBmY8V5XCJUPCYrYDzjQIkvoamjUatWqNYKkTmF206bUZMzGUCbRLaXdBdPCQvNk68'
        b'E4rJv8FI9nitGihn3MBujx5/JFF2WKLsDB8vZ3o5IiWEgscML1O9b3FQHzq6hskws0RqiKmD1RAKG1m0F8bS5vVH/Zv9RdnDRo5iI8cRD8+eZUj+GmNFYaKwhwLnxtgR'
        b'K5v2Zd2z2lc2hj3UNyWdIPvsyraVuI7DmsJwqym3KYssuqwkXGeK64x/UG1TFSV2pYkFIf1qEm4oxQ0lwhUucunyRB/9zEGFAYX+0hvrJJ7hlGf4eJ2gFjTliU0iRcEi'
        b'JfTRr015RYrdI0cZSiamqNHux6cPx6ePmFu2G4gKhs3dcHtZ9JsP2g3YYVe1Ed26w7y5Yl5gf6iYFz1UgKTHxwJJj48Flh6Ls0ptSiM8y7PBbcHkwK9HqJiP/pLvuN3z'
        b'EvMXixcslvCyKF4Wus0c32ZObrOkuE5IilAPTL+cPsS8LQfkhpKpkBTJ/FRqfqrEPY1yT3usoZSANRoOR2czTLhEi7UizelG67NZg4YDhrhmVNpUUA9z63TrlqOc5kvs'
        b'Aii7AAk3kOIGoqd6Y1H3xqJuYtoS0hQiu8Gly4uyC7njcs+LilrUqiLhLqa4ix+zVXCloQB1JAurViORlthYIDYO6zbvs7ls0+9yw0fiEka5hI0YmyJ1IjbOQdXOGeAM'
        b'BdwOBsF3ZlMRSyTB2VRwtsQzh/LMQVc1R+GtTqgV6EVYaUOOWNq1ZonKxbxEVNHWA9ZDFi/bvewo8U6kvBPFvBXi1LT7qRnDqRnizMVUZiGVuVySuoJKXTFeiY/Zcs64'
        b'dZ1NR1VwwUKbQmWqM7E9g7J0l3A9KK7HCNeinUNxXZG+Q23KHFQeUEa6RcwrFJV2baAcA9A39LpZCpbeKb23gYrLFufki3PzUUjFFUhCC6nQwof48mX05UHoG+p+iq8q'
        b'iuMTqfgMKj5PnL9UXLAUhVR8kSR8GRW+jKQfI1p9cW3n2u7Sng3U3LA77Duz77CpudESxxjKMQaLS2hbKGoBH6RyJTx/iuc/YuPQil6rRWMLkvgvJY1KWUKlLEXfJa5F'
        b'lGsR0nheqPwoQBoPN5QqaShU/simSGn5J6XuI+H5UjzfSfUm6xWo3syao9BARGxcQIs7qoo8kIdEwoeKypOE5lOh+RLvAsq7ALdjnNg4BrWhwmWF7tV9ZZfL+gNvxEnm'
        b'RuNSOcVQTjG464Y3hY9wHUYZHHOLbuc+j8seODPRbdEjNvyLcp1yI/aCi1GdUSNOzn1yl+W6Uy+p9qiirAkcUNYEDkhCBT737UOG7UOG8iT2UZR9lNh+EemgqcPxSB1m'
        b'SuIXUfGLkGrm2yLVzLdFHZtvS/T2KomNH2Xjh7qMpRXqMZZWqMNY2ot5oSjHapfV+gslTqGUU+hjHY4bqgcU4Dx6jOoyrKzPprWlidIklu5IaB4bqOHaQcHjtcwIpjXS'
        b'fzh8jEIDo29JOEpC+pfHs7DWGy1A80HD+5rcYU1u6yw0zglvCx/R1jkSdiAMjfziJNr2lLY9/iHiQETjysaVR4ubiyXaDpS2g+zHvNZMiamzRNuF0naR/VbQulFi6irR'
        b'dqO03fBvkQci8QBMrkmuMbk5kzJxkI3QjJtVKX2+yELkLLKg9AXd2j0GYn3vUYaKgemQe38F+TL+MmxlotEtXxTcFU3Z+/Xn9K/uz6HsAyiLwKHcYYsIsUXqnaVii2xx'
        b'ejZqDUsrLEjSthMlIcVLbz0MEQsW3tG+Z0xFLJTYpFM26SM2dmKbxG65HlWkftA3NCZIBal3Ql5a9PIi9BrBTYKCx4qKWAgVsRAq42pGwWNFNR30ZkHBY46W5exvGSh4'
        b'zNCapfUtDkZJYMOYZVKv2pgk0TSnNM3xPls9wyPrD6zHfq4newZTng5UOPMEBu9lG9vYR+83+B5jDGeerhgrYJfoDOl0pdxpBojhjMHvRjesYBGQOyF8JrAxujA2li+H'
        b'AkIF6FCdAkAv/ZFBYJBJQeEhMSFJBHlOkI00Ab11DFuOy1+6B9elTmnlv2NeOV07kI31M4PJbXGbTIPSZeCtlZ0sujHG+ORyLDVN9HpEgSrDIpE5YuI+Yo7GPXajyvI8'
        b'1Ag4UKcj/EbM50wbEUIizCZHFKAIwYi5gL7DFkfYjt0xbUQkirAiD/dGEY44wnEswn26iAw6KRThgCLmY6EhoTrDWDCi6zKiKxgtYrrrq48yUFAZPrqKyVDXHWURePWk'
        b'ACOldWsX0FGmNI46TWwXJ16QMWJkJkrq1xoSooGoejTeNozCb0n4MDRyJCBklO2jFk4A1L8UPpYfv3dUjvy+nsnQNq73HNG0Fmtaj2gHj8qztEMx11ybOJ9HYWUwmqDQ'
        b'GRLld4eKFg/l3nEXJySLUxaK0xeJIxeLQ7JGDE1Erv1z+nOHeEPrxF7xIyauKCF1d5SOuvu3OEDaKZSJ6jEibpQdxlIzHGX8q+FjxfG0ya+JcoFsNd4o4/cM6V1G+MRH'
        b'OejTwNsAy2jMlLLs6BkrAe5l+KYrwGq8o3PSFlOO9PNJJiZ7a/0C2ZudpyT9rjzhuwr6zslTJd/V0Hd16e8aE75LKd/NymMEb+0ZCd7sCQRvnWlI2uZjBG/DGQjeRjsZ'
        b'ecZdJv9bgneX6Rmkk88pTHqqxRi/W61APs/sF8nd3Enk7kL+nAcaxA9CUWl+bllwfk5R2TPHF7DdE2L/BWa3J81NdeGzHsgFxSWGPGAHugSWOmE17IIDN/avh2d70uA/'
        b'l99E3Jbe5PnbqdqyxxHOoDOmapf60Tv6MP+6dB6GYKskhsTEJYcQmjZvCsk6KTg4MX/1ZLqpU+l8XOBfc6nzGHJalpFn+jOlOsahnpxnvvKkNHA7lKrITYBZyyqnVBX9'
        b'WsrBUTM9w7k0Gpf6PxVBvXMqgprFeHHDurwUQX0to4R2p1aeSztUg50C6d5I/3l+4DJnzWom7eGpGXaWFm17doElxMtN2gVBxzxEr3oeP3nQvIapkKh/5ej8sllJKklO'
        b'1dFO7EIO49gH8k8kZ/lMqWOnDfAova1BQ1Pq4greCniRYk3DpfWndLrJ9Gougz79lec55bwTt9Gd9i2kyf3fIK1nfOpsxYk862zPP4JnXRqPRYyFsvk5XsP6v45XXchn'
        b'fWSu8Gt51Xmk1jGQFwNLfk9Ytayz/wKsWqYsfvEKz18Nq56sf2aCVc+kxn6GHj2tSpr++t8Ai56KpqIpKtmrMAAFE6Zm4CWN3TadG80XANOT2lkKlcavQhoUjV6HtjOj'
        b'jX6J5izLyW/hORcV/Bfl/P8OylnW46YhGeP/fg1QeXKn/ZVA5Wk78H9xyr8TTlk+NrncD/0zQzkJbzh6EdoLD8C6aJrxET6+tQQMwj0rQRcHnga14HjRG6fuM4VZKBkX'
        b'xfpjr7ofP7lzv5UaU93bwNvrsLOzU1fB9ir7+QdCEm9Td9+5+/bd9+4O3/3g7kCtiWiHidXtO/Vg5O6sN3bGH3tFNVfvyZESi+iI7HQFt03u7+22+pP27iUKr+syZu/V'
        b'fO2ZEV+ebKQQrAInpQQAeBEOEIIu2AVb6f2WNWYVUxG6oGk1YegCUT7NGGhLLZy4zRgc1aUhB+Gwid4reQDs85NtIQCXwBGm8wZ/shvDECNzJoNwMbMB1oFGJbADDvJV'
        b'/heGGzzimBYg++KoaSI9togeq/2jxIsxS7e+uLVMomlPadrf13Qf1nTvLuwvG0q9kzLiETDkcccTs2NTCDs2hbBjU5hk+aRerkFtRM+0YQP+LZz5AlkV/0hH/XFc1RkL'
        b'ra84DVR1ped/LlS1NIc9ZQLz8yzVnXxmbGke7WhoWo7qC1Ujg6gGoqqZAFG1mGE88AI4VeHnT3znKk7IO2fSuFh+8rgYjYqVpeNilhSIqoaBqAUcMi5WnGZcrETGxYov'
        b'jIuVXhj7Km5Wko6Lp40bGxcXoHHxpunGxT8PQ51ogfh/goQ62TeJdLApxYOuRK9nzGn8Lxz1v3BU7n/hqP+Fo/4yHNV+xiHpCvQ+oeeJsob4DazUn1EZfyQr9Q8nfM6O'
        b'pc+bny7zGAN86jHgdZa6BjxOOynxQIFfqDt90iIpHFbFCVKl2MRIWIfPvUWlYU8eSms4DhiBgMarNcpgAFzTL8djYAWeC2fMgQm4sHmSD5MzisQEyeSBKqHU/wnfG3tA'
        b'QemXu6MYHtwLbkXJtsJP8CUyyZMIC3uxb4H7wYAyvOHPK7dHdy5wMRmHEcLKcHsayYFuA4MxaF5BThdlWSsFwJs65fhouRIav3dFTZpslNlGE7KiPdwbQ58SS+Qowrp8'
        b'sJswIcEuLXtYI00sJT5NkJqG4ZCRMdGgA1wHR5PDwfnwGAdBRAxKxZEFLnNcQE1iEsMUNKuv8AX9pOrBKdDvLnQpRYUvhvvhLgbog7Vbyl1RlDnsh41THoB5hyUupRhy'
        b'uA/WGGH0qBxjCahRBIegCLaXk139A4vhtiTZ1dK2SqbvQokxQQNd+owCRXAatoFLBEUgrw17OaXLmOqoOtmzmH4BieQYPDy40gRegX1e4NZaIZvBgoNMO7hLi0AN6vLk'
        b'GegzPjVgSfTZigxG0bqar+SFTDRS9DhYeOiAHwc4ae52LDq2OaNZ7qWQH0Ke6bmEL2rXUezYseqRw4XjA9/Grd/Mi1km76f02oabG76yvOt+i6lYKwk7+xFDcD6tIfdV'
        b'n4Y44SHW9Y+/eXq7obP8A9W7vL7re7e2rdm9zCj9fGr+VY5ahMHeN8XtqXE+rp+ndu/Jqd78KG79Metr3RtCBvVCviry78q5uXDz4K2ca/GdCxqrY4fSvnc4t6hWbdlo'
        b'xPm6jqw3snMSAptM+eWtVezFuadjo5J0hKXHliZ+u6boySdbnua33FGsvKvxcvKGv7i87+LlXar62bFF29/vyj1Z0/G86QtVBZb8zXflgmqdROuC5lJfZKQH9N9ifxMZ'
        b'+6zNhK9JH2fbA87AvigHM89JJ45WwG54jew5z4BVOZOwgRyPYAIN3K1FnzI5wATbo2gPKWCPDzMgDpyi543nipHIj1P9OPCkOQ31269ODgFsAntixyeHtVbjTD/QQ2+H'
        b't9cAF8fES57BmQd6V7HgsdnwPG3LrwaHQJ9s5gn3FDCdwU7YTD+9CpwAxydgCzmgXh0fmQMthuSklBe8CvaPH+OdcIRX000OXoyC+0g6K6x18SnV6xtRMXA3r0LPUofX'
        b'2dFwUJs+GXTOHaA+IAADsJ0c0JnHBOeQDqkhc2NXcA60RrlEYs1xcTOsZcA+zyj65Nh+cDLEDnTArtQxJuEOWCsgTzVGsTftImMIz/EKrCcl0LJmw2OOefRJqiaOwhjX'
        b'rx1cA/tZThpR5JDJ4vLl00L9UsEOzPVTcFwDTvPVf6ddFNiDJXcSSG8Cqcps6gRsOoLeAO3VZTTY518j6GH0mtmRLQe2SPRsKD3MJ5sVQk/RgySGwZRhsFg7+KGW6RjM'
        b'zqPHfyh/2DVK7BpFrgqUGAZRhkFi7aBRVYaRRbNjvSLBwzFn+ZN4P4nhPMpwnlh73oiWYYMPiWid2+7Tzeuxp1wCh+cEiucEkoMDE67UM72vZz2sZy3R41N6fHxPDn24'
        b'IEGcnEElL5FYL5EYZlOG2WLtbJKsWMtWamFg66QxW8vaK7pDhq29xNZe75vaiu1C7ijeU5XYJUtMUyjTFLF+yogJrzkD497SmKLkroX9lsMCf7HAn1wcekfvnrHELkVi'
        b'mkqZpor1Ux8aWVBG9mKjud26YqOAfo96pYdGcxr9WlfXK/1Vz7gxS5Qn0XOl9Fzv6wUN6wUNhd1JFadkihfnjATHiRMWijNyH7OZ+vnYLoJCXJj8iYYO9V8DRfvlXVJE'
        b'pCbzz36DSIVgq8d5xrjVA0lWmDeTGUGMFb93+O8zffyncc0W/SLXbDq7wO8GNbOIJeMZO3jJi0DNVoBWmjTwG5hmhbCDQJQC1qjZjdHMQDcjJ8iPzWFYGAphFxvuXAS3'
        b'06OePS4BQnDRZoI3t0hQQw84dnmhkdhBsA/uoVFlDFAPRIFkwOE1h03W3Z2sslKXx3gz6BuOgEN+hEYGtkdiIBmGkalkE7RYGWjOhu1wlxRH5gj71pDfHcBhF+FqJgMc'
        b'5zLQuA5UeRaQkaiPB7yEUWRgny16aWAWmQPoonFAfRvh7jT1SSiyY+AC4S4lm8DdSRhEthgeoVlkIYEECVSwcT4hkYF2eBzTyDCJDF4H58iz7EAzOEjGxhey5Bgo2lYX'
        b'tpAxMzgKz8FjwlkvwsF6wHlwi1TFM7e9DGMmQ99prmFFR4k1jbVanDqHgUHjTrMa+WppK+gfN6RHMOrRb04hnv4rQ/T/GDjY0t9MhLKdqntmxkENYAtjHVtqYSSF9LdS'
        b'ZaAat3FSiMx94qtH/5jmq8tAcwFNp83/U8RS1GaU4wfZFJVMYXyBrUUE8xUXCA4R6VB3XE4gXrATjTjY2kwfUwFJr9pEkTgadFKQ149TzGXwmaQhY8LgNiG8Bq9ID5sz'
        b'uXCP3P/9tcxGRS7dJ6tlep54CnaZE44WaEIzFrYy0xN2KZTT5+2VVDmlbAZsWUNztFaCdnKPFjjiD68Uwh4ZSAtFe+bSTg6uollLSxzYQ7O0EkBvDE3N63CC2zk2tnaJ'
        b'oGEMpJUAG2kS306PtaAGVE5BaamtKnKrOC4nXIf0w9PP/G4uWJj0Sajm4bw/Kx7IVxc2vul1OEbputydCHWlPx9YLjzg030sN3B2gFN+YkV43eLE9tln1z3Mt9OoSEjp'
        b'/OFj368GT36TdfXvrQFz1u7jJSqnODzwe77pfde3o7ecun4tq/lD96Dl6h52gkVvPhj97tHXoh9udrvXff7NZ3Hrr3xcXXzrpPmWe/XOJw4zDlYtKbtw/9xshx0fX57V'
        b'/FK0I/uJ7ZXMPB7ng81L7imYVvwwd8+XdRWVq9u7rJrcHXOPLtTJ3d9lNffmey8FvvlYqK/19EnjoHzL1e2uzZI/u9sZPSha/ejen5/cyKp89ETFF3L8Dw+9ymhrZCT8'
        b'ZeHiv1lc9n30z1nCS0qDdd9VfCD4yFVu5w7zBSetL9QWdPU/3/a+04LH8YWbXA58eTXVTP4HRtPt7W/dDTk3uzFAOxc++3YJd73SefFju51b9PMd797wWxg63P3Ss9qP'
        b'o/1u5Oqbbr5mu/ezCxKX0X2KJ575dke3d8W2przVu8S675VVClcj2t7uGPqfs5eUPn256yXVhE11oh+3Da0x43lCZw351Oeqnmahj1rfOsK7p7PtqPy9FStMLE4Udf1w'
        b'JeB4ql/FhcgK06rX5nxsHjfoErfna8mCW9c0P2S8ppi575XSqvK9bw+/89ag93VvI1+H8Mrvhh5Unrgt1nnQ5trTeqogszckbUf6hZO9nj+Wg0HNjO8/Wff3Ox+cY31o'
        b'8VJfcHfwl1lWX2xkPQm6n7ntkrXyvaRgwZ33RjTPiQcv/fD30fCP13l3Gy7PXH5v/geFOU9UondWGIrfWKy7qURHbGfT9PT5O93f1Ca1RL9xsnaO3+o3znYo/eCo+WOy'
        b'68G3v3xl6IuOlYceZsIfvphn43+X/7bOtxHv/un2jXknFMvzv7pXkRrmKPzzJuV9eac2vP+emp3xFbV5b/xPpGK+wk9wzoHddo/nJaac1/rRaOcW9pOgT4+te3/rCE/T'
        b'UdHDRvSZ0Pa8u+gfMR1fXrRteGPLKYU24fpdjW+e2/b3W7vXv8L/7v6CN+4+9U74TgB+UkiAxyzezQDrjzXf9eEv+ECtK2rZcYG2TsIbgv6a3lc22Q/vsv/nzaGvlg3+'
        b'0zk00m+X5NXFeiduetbsc3nf9Kli95b5ea9s0H/17QWPHux/SW2g5WF/+3Oe8rMtX1mbzT667NI/tCLTqiNEZZbRrNM1t2/bLVI+Mv/zjx8fSRuY/eFg8sBT74ORfesz'
        b'6zWPpAyYZfe2pwwkWlY1XPjY4HvP7i9q6r/WatubvsJku7XVk7MWWY+63rX65uRxQe3ed4742Hyw6r0dl94Nft1n50+u4KeKpgfv9JcuWvGx4MOdxmkXGT/pLf1L3j2T'
        b'v0apvrLydCi//ImztsFbh2Z/073je9tZsT8WvDSXY/ZmQNKJey26cT9+6rVF75MCq7znhkbMn+aKBj/eXFPI3lljPl+iLvrA3faD+nxx3yLq+iV7w5th9y7sfvbmrYXX'
        b'+hdu99Bo6dDsNRvxX/oP/w6tL39YObpZ6cjW5yAn6dFc1o6YHdtPRLz7549WrYzyGuR0Bdnd/btKcoXabbs1i0N7tRrm2ldES7y+ff1V9dWuA3P6Pzdb4n437rPDqb63'
        b'NL6tsyzXUuEXk3XZUFi9eNLUl+k9gV8VqUkT9asWg32EqL8KadUxfBW4Di7Q6Ib2siXY7yjoWTcZYGWUTuLng0ObLcC5qQirQthdRqb/Hppo/l5D8AfrDScCpzD8h0z/'
        b'Y+AepID3qk6GToELsJtMkp3Wgwsxpi9gp+ZjVsG3tuRlUAbaCHUqF02sS/mRDqsjMKhGxp3yATsV0Ox6u5TlIg/Po1FNX/Jk9NQ1VzLNrwAtYA/oUZ2MmIqHNPcBHoc7'
        b'9KMwX+pwzgTE1BmwlUQLPT2kCKnj2L+OjDAFdoeSVfhFsA1UoRfNrRc5U/DGrCjazHATdoLtBDIFW3PRIBNTptBYaz+xhFgHqEjvrYI3ZZwpLzOSujHK9y5CmkqAuwls'
        b'apw0FQjqaWNES2QCuAg7JrGmzOFl0pDzQk1p1FRCOYZNyUhTsBbdjOP1zdcR1BS47IppUzLUFGgAO2kTU1U6asjrPi/gprTU9cnTneAhuI+DQVGgftUYK2quLY2ZuWrp'
        b'KoxlMjyFNCoKbltDxGfO5kwpKGourKfRKzJQ1CI/UikGcLuA7PQEu9fKDCyuoI82He2yQtXXlseJFajyUXnBKSa8oBRJb4ro9VsEj6P2eAEqkwevwzpiPQI7YA+snISh'
        b'gocX0iQqcAYOSB3sgibz0jUbJpOo/OFN0E8nUgdbwRECosKzGFjFh1XJ4DDGUZnKyYFLs4uI9MTDW/lA5DWFOeULTswl1e+MBi52m6YCp4pReseJqSgGdGdhJEkJOIQG'
        b'RARXAuuz6Z0b+xY70IAlG3iS4KY2wFryTG94FHYR69mCVKn9DBvP+KCOVB84Po9B46b0QR+qW4ybCkbNTfrChXnhdBcCVXK0PwvizKJ/tpS80sojuCk7+9XRfBltCvSi'
        b'roKztHihJS6K5+ox2pQrlOIotoFd8RyMmuoBp8ZxU3BfFi1lu638/cCxqcSpHNglk/EbK8GlYoVJvCl4AdTSyqwTViujqjg3lTmVF0M35Elw3ZImToFdoJ744QADm2En'
        b'XR1bi7cQ6BRo8MJEXAydigG9NBJmK7gAOjF2yh5NIQUOUurURjhAEjaHzTagVziJGaOM+sgBUhvuFXgmgHQB2MGnyVOg3p/O0Bm4DzUkIU+B3QoYPnWLaRQALtNlvcWH'
        b'e+gFEb4n7ZMFHFsBDpJENUANXwiPlo5PBuphL0k0DG5N0QLXptCnVth40Ykegufn4IxuKCyNdpRScaxQBfKIwNyoENLUKdAFOl4gT4ETsJLuXZ1hLlPJU2pcwp6yhU1c'
        b'ujUq4XlQvRHbUSehp7bAPaQEJRXwdFQsOCaFTzEdYS8YJC2hAc/AWx6+k+hTfuAinf/tsNtcCK6EyQBUaE6PJvLHSKSzP+ij8VNJoAOT2TB/Sg7skXZjcBZcEmL6lJzD'
        b'GH8K1GyhXet0KoCDuF5UUHfBCxi90QXgBpr5wm4k/5o0wemaKezAE4bi2LH5Al+BRPmCm4ZRsAFVkMzNNtgFD5KUw9G0/BaHpIrE+AhKGQumCjjAAl3wmBetyWrhKV2b'
        b'EpQ26Wpo2m8BT0pRReqOLIwIUt9MY/II9uoyHKTb4QoL7hPS70RlzL2KCCGK2cRHDuzP59Gye3Q2aIE9c6Zgr0xBNW1jrzNVollRBrp80kpS6tU2eJMGtTUgEd2O5kKH'
        b'kN6m2VdMATwbQfybg8ugcrMQg6+wY5oX4Feo35yiTd3VW6wx+8ocHGUTTXMKSf4hkoFElKsiQsSezKuyDEEX4IbTXRNAr83lonf7OKkqoYCAqsABsB3sXQZ2ToFVTSJV'
        b'pdNIQV14MBzXlrcKXV9okg23s8tgnQ5R5TYZsB0LaxRfGVbzI+iXeG0Gm2EAtslh/2r7iWD7WaH6J5dhow8urCJsZgWAbeAEidfMDAXNoHIqmSqGATvoBql0QbqBrIhs'
        b'yqXXRPCCCOyg0WsBsFcH1qC6Qi+gU9KlCMO1pCacAwqEfHgpDjRZIIHaZ4c0r2YFe2NhBkl3nTI4bIfkD3WIrsAobMqBR1kbIBJ78q6dHYB6VG0MrAowxINGXDgmY5YO'
        b'exPYDfYSTlca3O4jxXSZgDpC6pqZ0gUHYDVJNxEeU6QpV+mmgtWx44wrTCEjErTW2h6j7sARTVrlENZdNWiiO3S733oSW4Nyi15tmKSIxOaoFL56wQq0WExi+imBfQuI'
        b'7BW6gv3TU7hC4QkM4mIn03S2reg9eInOItgP2gWrI8ZhYuDsKnKRsya4JSNxEQoX6MkaA3HB8x6kKyqDVtiJSVxwdxlG+xMQVw1N6TIFHckcgqvyVxvDcJmgToZvdGKz'
        b'MIML7gI3meg+wuC6Cc6Q+gtNcsF6h6cxFcGFRp403CluHajm8LFGBU0EwcUB9ODZEMkpIXCh4e8JFanyIAQu33giEqWol9UQABfqntuxRsQELvSevEAjuLaDVlcOOAdu'
        b'0hgupqk5bCeKRREOlkxBcNlo0hAub7hnC8nWHHDOhOk/gb/lCi7Rb/EOU6RxarABNxFcmsDfapH26JXwSIoQw7fANosx/hY8i162RBmehLvKU9iTAVxqXqSyvEFTEuo6'
        b'AgeB9RT4FrgiJGkngW4uZm/lBGL6lhS9hV65Nwm+axE8iDrEZacXAVxesEGDfk9UwSOwXYbg8uSgN28MM5SDZJm8AzpQKVqjkPjupUFcTN8ANJci9MPdoNXCjrxzz5WO'
        b'k7bMg/k6fxxaCzfrZLv8RK4WfUpdd3rrHFnJe64iPZeU7Pu7ErWMxPo+L7Kz6uVHFRhc838zE8tuWN9Ooi+g9AU/x8TaxMRMLBzOyMSa6edfycLSPqrerP67s7Ckj5NC'
        b'NFoTzia3JYusTma2Z9K1gyOimqJETMJiSO5a2KHRpSEx9qSMPaXMnNbQ9jiJsRtl7PbbiFRTQEfqTeqta9q33Lf2H7b2H1KRWEdR1lES/WhKPxrn8b9cqf/fc6XUcb5x'
        b'T9CV6NtQ+jZYLNSa1CZUjBSJNAEektyVSQn8JDbzKJt5+DflTmUMgwnrDOsO7YjrikNVh5kuKHgsL495ISh4zJ6GF8Lm4Gyg4HEC0w1DqdwwlMoNQ6ncCJRqBQ2lCiRQ'
        b'qsB/HUq1qm3Vb4NSPZZn48yiYFTp94E2RTZFtpa2V1DWAUOlL1dQYQsbIyXG6ZRxulQp4NTU2tRwlYe3haPsZFCC+ZQgRMILpXih+OeotqhuVg+HcgqinCLvOyUNOyWJ'
        b'kxdLnLIopywJbwnFWyK7SlHC86R4no8V5XHdy+O6V8TFQcGoJsPE7NdAn0zMmjOas8Qmc7uDuhVHGfKo1AmDCwcWSuvroZ2gy6fLHwmsZSaztaC1uFtebJnU7zw4d2Du'
        b'kMvLPi/7S3ySKJ8kseVKcdqC+2mZw2mZ4kVZ1KKl1KIVkrSVVNrKpyPzA24rAIWh1bfLQNmdGElYOhWWLpmfQc3PQPWPs87GWZefh7KOAtTX/suI+i8j6vdmRC1kemNE'
        b'lDcmRHljQJQ35kN5YzwUDmZh9TMa/p9Kh/ovFOq3QKFmGG5XKk4kQsX4/p8mQmE4QKmWnJQIxcZEqB/wcr/2H4FzEuIJ5XQkJ7oef8L1OJWs8hFGai36RYqT/UwUJ/uZ'
        b'KE7TRhTQEYIRk5DJsKbwSc8Q4AjBz0ZgIpMTJjIlMPmYyMQnRKZUmsjEVjMfZUwKxohM+AcVGQBp3tCcX8FjsiTEpV8OJ/OYyO+xk3lMnpjH5I1xTN6YxuT9v4Ex4Xwm'
        b'knwmkmclMh+GRIz4oPe5vxrei/jbQpxnWTqjcuT3QNYKFgYm/Z4hvS0F25vKYV04AS/htaRa/cgYh9URMbDansmwAYPyK+EZuH/SHjh16eeT+UhGD+lMZS6lyxFSkXKD'
        b'VgELhw3q0u/a0k8V+rOIXcDuYk+mHOVZklOH+MwhPoOoWqlWqV6pWTm7UrtANU/uBWqRPIuRr5Anv5ORp9ClOIWXpEjilFCc8gtxSiROBcVxXohTJnGqKE7thTgVEqf+'
        b'/zH3JgBRHdn+8O1u9lUFZN/XpheWlh1kR/ZdkF1kC4oiNLjhGjcQF3BtFLVBlAZRW0VtFZVUmYRkTKbb3MQeEzNmz0syE5KYdTLJV1W3QVBn3vhm/u990lbfvrWdOudU'
        b'3bpVv3MKxZk+FWdI4maguJlPxRmRuFkozuypOGMSZ47iLJ6KMyFxs1Gc5VNxpiTOCsVZPxU3g8TZoDjbp+Jmkjg7FGf/VNwsEueA4hyfijMjcU4ozvmpOPNW7WpWpcsW'
        b'vUILcuWKrma3UkiWHCRJnVa9VkMkSVMkyZlEkm4o3rKSTexkPe4bxUan5cZpUJkfXGY/YfWJza6mpmBcS00aDTXVOy0vbxQzaQL8+cy3CJsfkas50wqbAH+KhU7RU+wZ'
        b'NeZ5xJeExggQxTZVNWIPF071K6oa0a/p9ohTcL1ivlNVecULTo1VyxurxFXLphQxxWAS2+1OK+EfWSRNh6BO+5Fejw3RkqpR6wi+dWVVY5WTuHnR0lpiWlW7bIqLDmLr'
        b'haLL0f+mFxqrple+tKrphfpK4rUA0Vxft6KKgGWb8RO8bjW2GZvaQKFTfC0xv/KK5mqskeumG6Vh2y2NWSMjCB+NHCY4znfyiuFOJCt3Eldh87qmqn8mJCxDr1gu9utR'
        b'PsWEUWM8WN9YW1O7rLwOO5jQ+D9ELMDOM55oqFhcXkNci1RhJy112JKXab1TZdVyNGURO9UzhBM7RC9NXAzWsKX14unmaBX1S5diq2uie0/YPKZz2fc5q5bW3depKF/a'
        b'FDCngvPEoEkwjPtRcMCIMbk+RJHuoYsGOzYxuWYGPFPUdWa0sqpNCI6aw6banjCWXqdFcNScp3DUWk9hpTnrtTQ46mfGTcVRf/AL619wRDStK/5j27l/ZE6J+MNYUi5I'
        b'S9WYAuLOUU7KfSx5JGNiLos69rNtbL2qGIX8R73+nzjIIcIJxX5OKsrRuLEQkbSQMWlkCpssZKryli97tjVyZWUtYwCrqXea8mI1b2iu0gwA4mbUMycHoGc7BplmJrzy'
        b'hVqUA/ff8uam+qXlTbUVRN2XVjXWaMwl/4mLkUbUr5fXL6vEHGZGhWk9+p/j3Ccht1Nw7g7pYrxVYQ+DL6p+5HEHm7ivcS+3c9+5sElM1a7Te1F48j1HZlaBDQKj4CA8'
        b'Ay7CTngF4yyauLCNCy6Ddi48CC4AJksqvAJOgoPwCtkByCWGdPCwITwOTmtT1Ayr9dR6b6gg4OHvmjiUVvAYmsYvTN3kpkcxqNkTECMNLrKxxZJnGBUWDg7W/fT7778f'
        b'ytGi9MzTOVTUwro/5ogogout46WTM8LhfpEvm9IGN01CWJngQiKXTaZB2WDXAjHcYQLbVjJnAaamC/W9vViUP9yvA26Y8uybmTOw99k6GuL77DQW3A1uBYHzUI7KcEJx'
        b'HoEeU4swwAGLAnJdl1BtF9i1ghRgWwGHDUmMSzTFgddYYCDDBhWA7S7hAS14fRoVSd4N6Vx4ngcOlyWlCDEyLA9K9OyWwN2kUQYm8BK8yENRYE8ijtULYC8DBxZyOQSu'
        b'DQ4CGYYjwJ0C2CnyDWBTRuAGvLyOvQRug5sIIjgM9K58nEAHJbg6bz27rnY5Oayct3z540gWitypvYG9FB4Cm5q9cPl9hYmwnTGRTMTpsrCJqzBizQToLc5U1zIVDpAT'
        b'u+HmsoXM5ltAbJYAXiZ7gmZgNwcct85pTsTF3UIl9z0+Gp6X5UXAeZmo1NSUFAG7IQIctbMGp+ENsMMCXoAXUszBjhRDA3gBtCdn51BV1TOCasENojI/ZyMlWF6LlcDo'
        b'SlMO1VyEbtrAPiB5RgXYUNUneb4XbEuEO3OwfWjKfCif1FxivZGRpD3L3QBuBSe1teHVQNge7w4GuFT8SnN4NAYcRiwneJtrS0EfvGi6vJG1DoxQbKhgeYADjUT05fCm'
        b'l6Fe4wqWA9hFcbRY3uAMOEVy4a3dK/CiUUMjC24HN1G2IZZbrRPJtQCcyRYvx4gY2GNNcYxYC63hIebQ5FuzwHVxA7xgxGqG51GmjSw3uBWeRtqEM3qDQ0VieBmVCTb7'
        b'Umwwwprt6MFYfexwA72a6i5AGVPdjLxmss25Mx6jx6YIPQMMIaHjY6Cbg3Hm40mwAydgJA9b0wTJGfMTJ3NoeAo2wosobZ2hQzlSQgWUNWMwQhq4vPCpvBiuoe/aogX3'
        b'a8ONzQRlcxHItHKYgnzh0Uw0JOmzkNTPgBu183d/yxKz0dPV1WjhpbyiJWbR5scepF24Wrev7m7x4cFdh/JGinwuZce/9Btr5qOXv9i8+UPz5KTexK5NLjfr9H9xe3H+'
        b'WE7pL587Pqps/uObd9KvCT4HoKvr67WfHRG/+eab974NWrRP6tD04hdqj4+p9yMzztkPJ9x+lNl+P7rmK+p+26c/hBadGVi1vXrvqtZC/dA5pxMstuyT/v3ujle6fYtt'
        b'Q26PK9+zUup+Hv0gZO+HnffCDc7r3n7zdmBsy/4Av10fREg+PdK+9aOvHpwFH9sEWMxPe3+LsfULbWuath3cEAw+fMfr+Nmqo3V14dvv6BcFv6d/ZueYyRd+x8yOqbx/'
        b'S1QVzIn/4PLgxa8bi97/8YOZW26ezY+s6TzzxfjLUveqU70Jv74QnbHq8w8aD70R55q3m6/MfSk45Krngrdbf+iXLkl6dPlc+RdJRr5vJgQ2rTHLDdzr1Vzz8K04C+ES'
        b'92/eNQ7wP/PtVyZNbX3xecpjFzznnCxuMlJdmzd+JOjOazbpfYuD297hDs/effKV28qAwZCjg58aFdbsMvos23r2rvUpnWklVkf3FDxM+Tv/2/D61896jb943n++JOO1'
        b'cHinflv/wnP+q3Y26n9vVjb/WElrgrQ2y7ynvmZ1Z8nO6ks5Fy93+Y2/0/z+B9nK3xb6vdcw5v1y9jdh44JbFz761ejWuN3HX+79+AHtv8H6DO+18M9/t3x4bbDBYmfx'
        b'vd23myMuBKT9oVO761dh8sjtZQ/vpw0vs15056bnjZLMQM7cK/u+/Ja/9PZMs9fz3PaEbQt+440ZD05vezt6juArGhgM3S42Er1TZiLOW3R6bFXQa8YPuK55+1rhIHvD'
        b'xl+XH/dusRqBu9IH31EObvtTXkuSvf31WWc25LYFvOZ6Y1brK8lDLxcb/e0vkXnsisQDUcb1nidaWn9ouRX19t9fqLspUl4u1A/22zIc2n/c6oN1tOni+3/pm/nTCV2P'
        b'9d9/evGz+p83WNu89N6Soqr/Ctv0+yv3v+M4/vJB1zhV8OmxwahV74X99dgvhq8fC23M+0EQ6iP6a1GkqO2texzTOzypY8IPlY0/7d/rWfnt7Ll/13lL3+5RVjk3mgAe'
        b'jOCLoIsnTGOjTi5jgU4wlJK4mBymCLqDgBS0g3N4gEPDHtzBpgyBAt0ZQX0e9JcyWMtez2JeUqouyt7KAv1gfwRoL2JO1nWcNw3hrAUlAh6UEmhINTxWC9p9mGNYdRay'
        b'DcERF3gYbGNgh5vAGX/Uydt8MrAd8Hp2cLk37F/6CM8NasA5PBXwwbDYVCFoyyDIXtDqk8i3B1e8iecyXapsnR4402BFAB/NyeDWdLB2bZEvpyYfHCSVsWoaMOoB7hLo'
        b'UDqlbLALHHSNBL3M6bvrlqZkCJL4GMBjWAIkYJgNR4pmMccYt8Ir1hgn7j0H9E/DiXNBD3Og63H0CD3DWIJ78ac6CtMDm5jDZMHpTBuC+kgEp4onUB/gkj0DnrgCz2+Y'
        b'Bvm4DCXwQFEjQV2ssAjnJYEzXmh8hlJKq4YFt+nCIwS0BbfDW/A0hi1NOZBtZQ0LPcG6tRrQIL+RQbHJ0MPwJsEyUsHouUMOAG2DHaSMxDDYi9icnJYiwPCNdA2upBmc'
        b'cYMHtMPY4BjBCIFbPi5iuCsJiyPFJF0Ah1PYlEOCFuguQtOzK9UE/GINtsCzGNS8R1+TwlgABuLZ8KqPNgFZRoMhDC/xSRfw06ZU5uSnBXfADngSXEcCwSQvZZVOHCKH'
        b'8YLDYCOGsuQWEH6JoKwFtGcIk9P4SWksysQVnHqBE5yJKMVqsBqehN3MFEJzfJ7x4lkBHF2vIlLy3BkMxzC+rV2X0tFng8F6Iy9LAusxnI1mVhhsZQF7KM4S1toVQEqE'
        b'sLg6QXNIKrgOzzFYVbc1pEAzVxvNsZ/wGrykAV5mwSuaw3YxVowcnElOUdWGh1nOiKxrnppzHEEn3AsOGQpThGxwFXaj7IMscBwcRaLDDAOXwCZ4TTxxGiqUANkTuNRa'
        b'XQY4dKN61uTBpBTAs+o94EQ+I//DSP4HpkJKZ5aWgmF9BvLTFb0ewwd3pOoUgw5U/xGMr74C95BYfziAqEXN28Nj667Eh8Cirg83gfMM8hOOZDNYYxbsMcXwazRZl5F2'
        b'mcLeWo1xRBqGIl9jg92gl5UMbjIdDrFly8TRsSwwDM87wX7YyWDWtsODlli+qCMdhfsngLyzwFkO4sMtIwa6uXctHqEyCMiwGl7C0EhwmA3awH4hg848APv/gX8ELe8N'
        b'8Bw4E82MQa26i9HkGMPHilahBl5igbOz4XGmEnkM0sqLkzM8HcpkPmyt5MSj6R8ZpArMfED7yhVw2Ljh8XQROyH0gbvnQkVimgDlyYnXMwEvgstEFl5uYLeYZ0DQovAk'
        b'l0XprmPPgRcCmFFijxNsFfMakdpfisOar1vF9tdFbCGdXYEKOYeanIQGsVNoDrwrg4eNIbQpCzioNTMBbieMF8Au2G+IyufqBzuRMsAgOwIMIsYTo5ibBiuZMsAupLS6'
        b'lMlicDmdEwW7lzGwuFMu4Ko4GRuIsDDGr2P9jIy0R/ilaxZ/HQbiscqMyUmYA/AwMzyeAgcymaMwg1hTYXgAdTNiAJEZnovtHygdeIMYQIArpgycTAFugaMT57iygBy2'
        b'u2bFkrZaJmIFQFQkoW5KRgmfRLiLQ8FeS1d4Sjsoab3mtMut4IQ4nduQtBhs9tbAOmfYc7KgZCGpmq0Hz2BrBAoczyWHYOuzmKr31AO5mIwucFsVxQFbWWvMEpjBGI8N'
        b'w7xkQYrAOx2NLqZgT2YNpzwnmvRHp4TiCcKuwusMcdi1SBuGJ3NLtcERD7dHXFxMX8QijWosyXhCOTIC0YQ5DJzVSQc7QhiI8A0bG8ant36NxtADdJcT/po7xhvimGbE'
        b'n+MaHZ4Jr3HAGbjXmRHpMZ4djzx84AmwFT3d9OB1Nnq+nwKnNf2pJZTgBtOhHGyejhxED7ezXNv/jfNK/pWNMNyaaesNz9oPI14jLaYuMU33k/lHbcYfx+IYNEQ6dIRK'
        b'KqQBKjMubcYdpzgz57HUNnbHPQ57KJ0jFOLRWJVNIm2T2BHbEftw4n64YtGoq8omgbZJ6IhVz7buqJC4Spo6l+1f1sFRO7p0aO03Uts7decfLzlcIhOp7H1oex85i7b3'
        b'v2cffNc+WGGmso+g7SMUi2j7aJTYAB8fV8iA5JjE5KaZJW0mUJoFqANDhxffC0y6G5g0xlUF5tKBuUr/3I442lz40ClM7RSidood19WynjVOoaBDe9yAcvHst+217bHv'
        b'sx+n9GeGk6AzqSNWYq528ehMQRezH1g6SMTS2AlXItoWDmpH1+419xzn3HWcI89ROYbQjiHjFMtaoObyJXHdyQ8c3KUVqDUOPrSDj4TzwNlLZiarVjkH0M4BEh21lb1E'
        b'e9wQFfO9CWXrrnQPVdmE0TZhSvMwtbVdt02HjtqV2xdOu87p0KJnOKndebLovoK+Yto9EN9wUbt5y/z6kmi3UNotUulWOBo45nw7hI6dT8cW4gTOaieB1FhWPbSMFmrg'
        b'PMRXqb1rdxlt76e0L5TnKaKHCxRrx6pVkbl0wHw6oJDhras0urugu5S2F9L2Ito+GKVVJIz6jSSNpNPhaXR4Nh0+nw5nEtu5SP26k7rTaTsf2i6UtptL28Uq7ZaPrhgr'
        b'v7369noa42Gq6HlL6HnLUXr9KYX7MoXjUh46e8pYfdZ9DrSziHbGt0zUDo7oyxClx1BNEQk64tW2Tt2h3REdcRhPoN9torQKk7kNcYf4tHfYqNZtg7uWyUrLZOLpZIHK'
        b'oYB2KFBaFaidPfpsxim2xWIWE0q01QSI1dy9XmUrpG2F8pl3bf2Vtv4PXIRKnxdULrW0S63SrnacQ9mJHppbdaTsT5GK0F9z35qeyL5Ilbk/vtWRonbyIDx18ZEK5Dry'
        b'hmF92jeK9p1H+6aOVapccmiXHBRvqpGEPHtoMS2MpIUJtDBlLFfllE07ZeP8D22dpc7dId0RWO2EJEC9xNJm/wra0pO29KYtfZSiJKUl/qgFIlmePHZ43nDqqOttzzGP'
        b'2z4qQTYtyJZo0VbeqF3dEbStQD77rm2Q0jZIbeektBPSdkK5i8puDnOJtXYD1tNqlloYJluqiB1JGEmhw1OV4aXKzBw6M4/OLKAzS5ULK1XCKlpYhdEhjLYaU1bJrPEZ'
        b'lLcQdyaPT2xdpXHSONlsOXvIZsiBAWypbENo2xDcCB8SPNkSeaTSMgZ91MI5iCU5w/nDxaOi20FjgbcjVcIcWpiDG8J7ZkOQhvnI/VUYA4QvcUPW4YZUstT8EFmawnXE'
        b'Y4RHhyYrQ4vHKu5U36m9s0xZukjFr6D5FagRaZONiMWN4PngRniq7R2ZwcN6nDKcGUKOaLhnybtryZMlqyyDaMsg7Eong/XAwVPplaZySKcd0pVW6WpLZ+KYyE1l6YNa'
        b'hX3zeKudPfvte+17HPscJTqoh9t7SgplOnJzeZXciBnAcFHeahcvqRWKxuhALYsQEkg4agdvSd3j0QKNit2r7jn633X0l4eqHOfSjnNxU8tYD1x4Uu6Y+R3rMfSnzM2n'
        b'c4uV6MMvUbmU0i6lSrtSdUCwRKvbQCrqm6uy8lda+Y9booaR1o2bTFQ4BZcyk8GlyDBgY0DrX0eo/DdPHvxkeeyv51993iTp4bO0KMZZD3rkZMSwWCxHjFD5jwf/KcQL'
        b'Qer06gdTCpNoHc5zeCt+4b/zVjydRROuis9gFxePXRX7TezUkq1OvlNVjdDJG++2CH0DRBM+55/2XPy8XpUH2M9LpxzTiberGTptMZ2abUGn2sppFD0HMdWImAHWfb2y'
        b'CmbX+PlouohpujTJO2fiXJR41Kx2IgViF7n/Q8qwOLms+8Zlk3umZbXPSd5lTJ7eJMs8op2al9U2NFc9w9Pu/4zGLQyNRmUTO2TPTeJVTOKsSRK9MQfFTYiFZPdtcuPt'
        b'3yMTC7nR+Lk1bmR6zxDm1OOTGJZV1xNvx07li+qbm6Yd7PBv0XeSel76bk2nzzZ3+kEE/0NiajAxQ89NDMDEnJ0kxuYxMTFJsf8WLeefm5aXpzGm8SL1/OOTO+t5Kx3D'
        b'lXqwJhjglfuM4ykmPID/G3qCupsBcWVchh0LPx+Jf8BPQ7yptpGS5HaXbZyqOMRfMTN4/RvC4uKhlFDXVP98tL05fSi11vi+/k9QZFy2qLwOAxzK6pdXLXs+slTTh9Bg'
        b'TBYuhdmPr5sKC3rSmfq/KWWTSaor6urFVc9HNo3JvktNIxsX82+R/X9/2lv1k6e9TXJyCsKBk177ly1fsMR4rU2avfrI5LltL1oHF1Ee/RzLDaxDFVwWWbwBZ+fiVUp4'
        b'FQxkTJhDM8uU8NbCZxzZ5oldRJo/Mdesq1qmWdowpZiljboEFmVlt79FOcPlOU9n+8cV3MO9t4bSQLKXJLD+N45m+/+ZAjx13N+zFEArPbf2o4z/0hZjHi//Uoo04FLr'
        b'UeetfpJNImPK5CZ7vnklI5Cn5buG9Yx3iUX19XUaARtpBNxIBNzR9JzS/SfF358m3ob/A/FidBte4PtuLzWBbkMC1tKg2/RaWZojRRh8G9VqqsG2sZHonzg2ZB1H/xnC'
        b'fBrthsTLXs/RiP6ZcZOif+FJ0WNRiJ4QvSPjy32hMzxHABXgKOhkMYiKyBQCKpploW10no1EE7Wwri+thfHpB1rByTVik0Z9eAUvdcNelhCcyyf4kz+Uams1Men5WyML'
        b'qWZf3BB4cRFxCcH4a84iLpfQRTr2mp6dmZ0HWwV5bKo0Shf0wOuwq5nsFCngTSolGYMmykA/2P14R0+b8q7QBqfXAQlDzTnwIgMVgcdBqxbBivgYEVSHGThnxbibMAHb'
        b'p7ibAJ1gJ8mbGhKKt6JSYLvYUpfSErDAGdjLwFbgVdgdix17FsZo/HougvsZrMhJsBk7g8Yr6vAiNx3vLZjWcKrgJrA9lyBNXGC/GVnBhkfFgiQtSl+XDXY7GDIOEdvg'
        b'jkjsPjsWXkUFa7HA8WbQSbLNg4j/eGfWHmzmCnQo/RA2OLmUYnwYDoLj8CDjbkqOXYMSf1OV4ASDiRmGh0JguyAd7AM7yGq4TgnbIsu62R1HdkUFpMDdSXzYny7EPiXa'
        b'CeeJD2qKF6ENd6XD3mmqbTih2juxahtMU+3pij1xQs7/jlLXPKnUBs9QakE60VyulzalN+eGDtLE1FdqKhk4nCMLSMTpcA8YwTvjjO8lcAscI+z3gn0scRI4Bs96cye9'
        b'V0jjCSQsYT44iSUOO+EtgfekyNngPKODw4XwlDg1H/ZixxZ4oxXsABeZqLPwCGwVp4Ibvj6os+ix7JGw9jOqMFgO5ClwB9hVPuE2ZxtsJ4RGN8JuJKcGeJRsszL+gsCB'
        b'MMbZ5cb1UdjZ03FwguxGEm9P8EwiARGFgLZ0jcM0cAXueOzuqZVLEIfNeGSF56LdctB3frIzhTo/HOBqMwikTtDXosldVD+ZFx4B1wiLGhbUoNggcJI44CIul5A27iN5'
        b's93ACHH2BDqcp/l72skjHcoZHLflCb2MuMmTnqQ8NjDOazeCw1DKg7vgcABPiLqckCtITmNRLmCrdsj8DUT/4QgvG/tsSkbs6pl02uQCpUzsZTQtGWbcgjTB46h8HT22'
        b'JZRGk1O2eWAE7n+2dxGwURv2gMvV8FABSQoHV60lnmdSyY46HqA0HcojXxtK4YtL4AWwp9mHwk5CDlVhrAcFhjL+sX+VdLBJF3aAvQFE4l6gC2wXLy+Eh8lWMR6qQKcT'
        b'GVXgVn1wCQ9WJ+czR1dMDFaW8BYZEGeicWswJdkSbsVj4jMGRLixhaiHVzNoxaPakqUEEUBGNbAZXmV07jI8j/IIwOEg4hwfu+/Rymai+sE+SzSIwF2xk37zdZcz48sR'
        b'eKQWjy+o69wEWzTjS407o4674KEINDLBY+AQyUg84XVqoK2Xs8RIkVkUK7jagYK7l3JIXS3wVjkvzR1IBKiraZWj0RV0wz5S3HIdKEVKVgC2JAr4xMnhQfZasLOSIOl8'
        b'0NC7n+cFDsITU/y7PHbusruA6MNM2GnMeIABQ/GTnpZ6waZm7GYI7ixpRjWg9t5M4j97RAQnwAEum9CjX2GPZrwXwDGwZYUWxYIyzKg2eJJ5SvTbmYnheR2CYg3EfqeP'
        b'wkHiqRYqwCV4Be5DUeCIA5/iLw4nT8gfHA0oc6diDjVjYer3ummM22EDe8S2JsyvhXX1Pg7MzddzUOPjMln42TuyyIu5mSM2pqwqt2hRmQtTy3x8mZt/99enZuh9qE0t'
        b'XGjEbVoxfZ7CnhgjnVCQgoZU/ApVgqaga1nLWZVUHnWIxaJ26ldOvsyT6RmbOAa+z1ohxvmdmHeoX/TDa6qWVa1a3jh3TfiTK8hNVY1lZY+9ApPfBIM9xVPwRO4qfTR7'
        b'w6L4HP1tpJRxC/EnJ3c0a7RgzE3zc8qHgVjHYLaeDoObMI4S9c99AnR5XZhEjqNIzsoU5CXix9wTEgUX2QYs7BBy0GghkKIHPx5yDGoN0HDOFTBYFgY7Y8ul7OZrgSGw'
        b'p6Z2t/ffKfECDkV9/4H6Rn5KxrtRM0rDzh+9vfqW06Yt43rnDs7tWR71xdZY990HvL/fuObzQFlCzAHX7zeuqI+gvZdezU2M+CTzk70Ov5iFpX916V7XxviTLptqam52'
        b'ff3un77Z9qvvnraYs21vhbjk//Jafnr3pxsXRsb+ZN9mkd8dOP/N3HuXAwYbD3is+jBcf8P8Be5W5803pflv9bB1uVIflft9/g+GByu93xaOmvjmxSxIKq+9+X3PupTd'
        b'u3+KC7wn+XSYD8taride0OJ8UqzdzI3U4a/Z4i4YMhrkL7scctR4nb/Jg882/FVv/NTa9zNX5C0I2XLePNrVSnYk4YtP17V/mXrF4IXSV94Ic3+PilP96Ni5b92xRQMd'
        b'BlsPb54Vvf7j1ZeO3LHa71esuD+jeoXbp3nOh3S9G744ezgq4vMBpx3Np0P/cvJP0caf0Gd+mXP/gWHcp+OJGQfefvlPAR/PrP71TeOeu17vPfj149wXNg10tl39+c7p'
        b'F2yAyfpv4z/+ePOfjli+s3RfwaxCs5VKmzdeunTwVbvbs6JOc4e0s7JqeiwyLg7feOVutP117bf8LX+Qzzmj9V6soibhw/fF9y3vS65/0eCz43Xrg+cLx3YbRd2L2afH'
        b'87kSwSk5pPzeL7RC0BMh+a7Xfk7o1/GHanwD3E5t217atWlZ8uentpfGd1mOfG5jU/Kot2TO/W9/uSjstW3t7d2ijuNdupFcdHPPkf6zG2q/CjqztLM5Y8GP/bxv+H+4'
        b'H7asVLnJ+sfswDdtHW6cd3MPu6n946fCP7686A3twq/Bhqu6Bg6JIz8vGPl5wydbV9YnVe/1+3Co9Xvlj9o1bxgObXxzW9gZ+9rCsO3vi8ZLuT9kjG2YczTjUOQ1lY//'
        b'+nGrd51LOi2+c/mqdpNFlU9JhG3kB3/lfnijr3o4LOjtnznNnxcmvms2VP3xW4/sP26KDcmo+NjuDyH+Xxa9XeKY/mvJj22LS3/8Lf9L8P7K+s8+dv912VdLhj7+83bR'
        b'GtEHP4e3bTvwZtQPriU73+q81yl85b9+FY/9Sa9RFvLB10FVG4YKjX882nPkuPSzeUE3y36jj9cHt2+OGPJ/AD4rO/Y357Vgz+3+kRjwZ86qrgNnanrZ6zO2zxyLeIO3'
        b'UT3v1/l5/3V6aLHtEBiMsMhd2lIT+fWcNa+3KH9O+fnUuI3r0A+fRsnO3XC5t4P9553CWznf7u1r2cD61TIYuERzNc7ytsGuTDwWb8nwATIt8uwYYfMZpAiUwW5DuCMG'
        b'XOAm6XuhFwY0J54J+jmg2yCI4Iu4i8ERQ28r2M+FFxg/XbbsPGe4nWBQmuF+9JggIEE0Fm8pwTOx40sYUNCu2mJ4scl/IQbAMeC3ZA9CjyWaYyt4SdyVGKDIgBPR1Kqd'
        b'IGlCwH64D170iWrE4DgNMA6N94x7s2pwoR6NOqA7aMqMLRHcYlBxp6CCb4gd0a2C+xtSfbg6lDFK5VGwjGC7csGh2ElM3FQ8XBbYzIGH4DWwkTSpUgB3i1FTu8DIpMPE'
        b'NVmk+nngHBwmkLhFsH/C0SK4VktggKA/CLQZes3KwrM2di5rLti6lBS4GuxbpwG8GaKpyVEKjMwGfQSFswzNBU8Qv6AN6Gl+7rFnUNN0BiYIDi4Xo7ke7CDTRMbHJpQs'
        b'17gqBgezxKlYLG2wrRzJRpsyMGIDab6Bxi+XKTxLPMRiqByfonTAEFvkCIYJVSYz4IUUflKNV+Jj172u8wlCar4QjDAeQYEcTW8nvYKiybGMKfksHAInsU9ROLJs0q1o'
        b'CdhKxLuqDEPudix4AY/56JEbwgLnwXFdJmcH7AZyQ6F+Ldf7sTdTcLCSgbJJPLXEcIcZ6E9KgldS2JRuA9tbD1zXABLhINhl6BXK8+ZNepOEXSVE9jVwUw4GhTVwq9AE'
        b'EoPuDPLZ4BpoLSR5s8FZH0MwsBwJ/3iJABN8mAXP2Xo80kzJWpejzPAUuMKgylzh5iVEptWuXMPkWbw0ng56VbnGAp3wUiRB72bBjVyM+dQXpggN0HwMbgcHKCtwSSsI'
        b'sWmAcZC5J9Nf4xEOO5rU+KnbtQ4c4cB9AdUMiFoCzs0g3iCne4KsALc46FV0bwYj6FM52BYHTd0VcGMK97EHRa1gwtSWkDoGCAz2wjMT/t/gADzD0LF/SQPjyhJsRF1r'
        b'mptlcMmUweNJfF5gugU3A6V57NQSXEClYE4sgOeaDJuL4U1jfdQrnVnRy8BOBhobDXZjH6Fw2MoRSUw7noXo7IMXiSqEgy4oN/QCEn3sBpjx/6eN+EP6y3E0PyUYPzhk'
        b'4IMhfqcZnB3YPSccO/bMwC5kGd+e5hq3svBSSjTq4aghpwQanC72GggOMb6P4ZEKeMpQiF7+sIc9xm1gC8qK2ZC+Ar0gYnelU50GguuggwNbw0A3g+RFb2mXDZOBvE7j'
        b'3Q90CYmc9A2cnnDux0FTmiOMez9wEfQzGjoAR9BgKhBiv4lXNT7+wFAoEZJlAdiEdBu0hpkgRUTN1k1hO4NtmhOzhGFx8CLfLV4onPA5uBzIST4tcBX0M0j5uZ4T3sBR'
        b'X7hO9LAOHkadjZ+Oxm24Gb2R7OHjM79Os+FZ9Lb2Iklii6bZPSTNTi48AKSwFR9LBs6y4QlwYjXDt46F8DB6rUwEQ+iliw16WJnwBhghyle3Al7mZfDhDtj+QjSBzxvC'
        b'm2w06R6azfSeHWA7UBh6o6HiRbibg43X5vgyWrUAcaYN8w2cBAceA6sDOLqeYJABiJ+OZj22IagFJzVmBNiEAPHyPNf5/x5g+K8gQZypJ50IPgOMSGb39w0ez9nXcP/l'
        b'6T1Z6E3SxWdokMn8eFwii+IHjFP1LHv+NySU6qrd+f3FvcU9pX2lUrba1VPm3xsqDVULRNIENd9fGi+Nfzh5rfb2o73DpLoPXd2li/vmjqM+ncCS5w+XMldqnr88UJFw'
        b'PpLmxdK8BJqXQvMylby1ytwiZfEiZdUSVfESOreOzq2nc5vo3JV07lppnNqTJ2saWn3XM1jpGawOjlCskGvLdNR8Ec0PV+SNVl0tpfmpND+f5hfR/IXjFCUoYisrl9CV'
        b'TcrmFvRzAyuO/Q1FrUBfjyiqihXPfGUyX3nMVxFbypYG9OirBXPkeYrq82W0IJ4WJNKCNFqQrRSsV+aVKEsrlTVLVaVL6bxldF4DnbeCzltN561HGQN7DEjGoTLitysW'
        b'5VQKKsbmKXML72TQqaV0aoUmlbef3GPIh/aORnz1DcKedaJRTEiPsdobs5ovGsrAXuFiWEyIWu/FH9KXmcqz73nOves5V+UZRXtGjVMs9xiW2svnnMmgibxpeLXKK5r2'
        b'ilZ6Rf+ESpWjcoSy1UNpaq7vkD3NDUO0DZXQgkg1T3gueDAY5Rsyob3CUHJF47Qf49qcAI9vKA7f8xEOftShvAS9zT0r+1aO63L4QeM6lCho3IjyDxm3NfFz+YZCwSMc'
        b'ME0Yd6CC5ipqxnRUc9PpwAw6MIfGzu6KkAyCotnKsmplzTJlw0pVzUq6bBVd1oIYv5AVjRkfqXISqQMjFNXD9XRgIsmbSwfm04HFE5Hh+Ai1qpcy6PBcOnwBHV5Eh2NR'
        b'R8RjUSvrxMoVLaq6FrpyLV25QSNlKVvpiv36PURccKS5c2lujJKbNVpze4kUQ0QRD51LWbLqoSXMlVoUgnTTY4Q3umKs+vZ6lSiPFuUpC0pUohJpjHRVT+pDT2HfWqmW'
        b'OiiMDppHB6UqgyqVmdnKnAo6sxLXJVI5zUGcRnymBXFKQfYYeyzwjsGEdvhh3Yh+/KuIFkRofgn9hxYP1SuFqaOzRufdtkV3g3oMcRosM6UgbdR/tPp2qCYx4ywwHP2a'
        b'06OHExUMlWqifERDa4Y2oB/BPUYPA8KHi4fL6IAkZUDlWD72wVhGpyE6pXNVTv5YMRwQF3z9GcmhDowJQno7jxakSg3UrgLMlDSW2s1Durov7Z5b8F23YIXNvZCkuyFJ'
        b'qpAUOiRF5ZZKu6Uq3VLVPgHYbVoCzkHOsUehdN70nJYjdvdCUu6iXCFpdEiayi2ddktXkg+uu5ipjQnRKDItr8XIs+vFVfsGyLXlixTWw0tVvnG0b5ymObh5NDcCtTAo'
        b'Ynj18HplUMnYLGVqMZ1UMikpV3elRyDtGvQNZetcxlJooJyZJcrwElV4yfgMysdP6RdNC2PuCRPvChPHzFTCNFqYJp330Fsgc5XVDPCH+IqZd71Dld6hEz2xUeUVSnuF'
        b'Kr1CxzkUT/hkMqRBsoa+Nfc8Q+56hqg8w2jPsHFKF/XkUd0x1m2De1HZd6OyVVG5dFQucx91uBhWEmts5m2bsXzl/Lw7hUqvuTJdOWvAQD5PEX0+GfVomUi2ciB8KFzh'
        b'd5cXruSFq0WhV8IuhJ2PGI6QxaEftCieFiUj1grQiBERLWfLA88bPPT0loplQT1r+9bKG5iRVZGjyBm1xFVdLRspU2Zm3Y3IUkZkofFEwRo2uOcbc9c3hmEyatvcbJY6'
        b'KVOZlX3H5l5S0d2kIlVSCWIuE/PQL1gxc9hG0XjXLxqxcDR/LOt24b34/Lvx+ar4Ajq+AN1UR8YpmjVrRAvKUKiKW0ijMHIhHblQxlbywlRe4Uqv8IdeQsxZZVARFiVx'
        b's6cR5DccFrcM+x1C4TgT6lA8/yEhGka9/YZ4Q0LaO0LpnT9qeduWjs6mo/NJBO0dSntHoktXb6xuKSxZDfOtDoka9VQGJ6POvk7lFvDQK0hmqgxOVHploM9YDPMt1X7o'
        b'GyTV7jNWe/Ckhvivx3C8jIMflMxDc+oZjvf1m1ZVVjWV19aJ7+uWNa1aVC6u+ncwoprTHKc+/Zm91jxtinqOpz4Hr+AdpghUFD3zYxNZLJYT3nH994P/1Jbtdxgaekx/'
        b'DjVsEs3mcDnMSvZhMVCkJPMXZT0+VwUfIUFOIqyy9SAHruyAN7Fp5iTEwQac0ALtxvA6cZoAbsFeNpoa7kFT2iQB2JGRzLcDL5LiHMO04H54wYjLJrtGYASchDdRkeAG'
        b'HHhc3ywgJdWBM7DLGVcYid5lnq7PO6SZh1OdhIMWPGw0dsYrMU2YlJa1HFvhZCWSfYoWtzQ0r15ooecGhtcyHgd2gp3gyIQt+wJ4kpizYwcGJ+BRZv37HBiZnwJ3CbzA'
        b'QC4pzC8gKxFR2QM3EipD3XQo3XXEpUWekRU+dgUvqqIpcj5TtZdm6yEADODdh2JwWM8UvXgfI0v0q0PRe+Y07uTGP2YOmlCfIQVrFaaIcWEziyeLS0mfrzl6GjcNv/pX'
        b'b9ADvdmgj3SG2ocRH3LEDhxUUkXI0by0+reiZjxotnu1rM0sqPawx9Lsmz3K3zY58Boetm7ZEve2wZkX1cnOjYMOg9+ztmzZ7E1zZIccGqOKf5mncH6z9Xdw+5uzN77x'
        b'0OPH/8n+jy2i76rf+eHQ67q/64PPZ+26bv7NEseSz3Vvxdye8fLev8xrfXWJmTH3bP349dnXMysks3/a/cXa+PGGnSYGcX/73HSF5SqLLYdMSo+aee6K3bH4ThcrJOry'
        b'PZePVlqF7xr5TP7mcFLSfI5fpc6pmRWmvwXMOcs51PXZ64VJAwcGWT+XGR595bcCv2rRj9VWXx6/cKGxoEB/zxtLXXdJg0rf2Zv11rEB/WDPgWpO+NZT9PyFxVfZowf3'
        b'ST6pUpTP/1b2cQSIsbvl61i+4PAriRZbStzbPtc/OOjS67r6c+uRQw+XfHjW54KyKz3fvK79euYbzT023305fFZ2YWzHJrhj+aDNewfvNFWUbzlsV/46K2vxVe+8lwe5'
        b'eQZV1JeeCzbp7RoImL/60V7rl2aKPr+ffeqrv7+zYdVZXsShaseMu9l7br7J25nXu4ZuzTtRTe8OzQr69kTpnz14X78hd+Pemx0q8d36pfL6bpcLxj/ev7P/ut89W8PQ'
        b'6y+t3GTaOvutquPlnQVxkbtXx7bI7f8macqJ+2rHgQ9fY4uXDn4lXq2+Y1Ka1u/2F65Xzd1jUd6nclIt7ozHdH/YNN61PTmwoK1r3V8C1Dc/zAhuyj3s99ny9nMfrK94'
        b'76uKD/3bQ/rWz0/sEIq6WlZt/pvx7txU6UdfPXovfDV/ls6bwYZD2Y7D9cW1F63Eh69utq/eHbgqYUNs7LYFryv3vT/v9Hf19pKdRWuDru4yt6x9XWIY/sVo9/szj46m'
        b'mv5haOiLB9omRkplxMiRTw2utyzKP/Xjd14B+WWcjzd/MjfzjcCy470PW1acS+gzs8iTxlr8kkk/+OC7C3tM5m4vfa82451FbqevH2zpb3nUOf6XV4wOvDd0+6qWf86S'
        b'Y7XKO40zI94oWrP41T/bsOZueLP4Gjyzr6RP8XG9k+z8j+xTgUPbAvJaTu9rzos4Ovf3G/u3V71ZdvD4y599tdbwjxlFYf3b/2ZUssiorOazyA9+PCLtH/vid9aCMpMU'
        b'T3Hdb1zfR3h/El5Er91HpptzAsXSKRadj805EzRHBVWCS3htDRuIorfsTi2N/ShQcJlFsM3gOBjG+8NAtjpds1oL9jBLcznwMFBg40VUzamkqdaL5ibkddwNnp5LLL8L'
        b'4WHN2uoicIK8bLs4pk2zbLW1nHL8mTc8SCqoRHUdxitb8ELMxOIWs7BVlcVY9G9bH5ACDoFO5vBzVjSit5WsnsTw4QExaGuasM10hXt1ycor3KZdPmFbTVo9DK42MMeu'
        b'wANaYNgJnGYWcG/O9DX05uHTrUizDM0KMtlwsxU8O2Fk2TkHG8yDgZYGLovSXsmC3XAXPE7oCjMEO0BfDTHcJFabQAaOa045coOXxJojwFaieIOVq9exwek8IGPWm07D'
        b'XjBADDsd9LQZu865ecQUNMUUHDLUATuESITsfFYY3JPKLHrsgx3gtFalZvkKH9B1HGrO/RqAV8C1CftfMLKIMQGu5MSnWTOLLZ3xluRgMnt4mWLgES9WgvNkkaq2Co5M'
        b'HocGJKB7ylodlCaR/DXgtBNe7uPGPj7soVRzNs28InDY1Zix25xusxktJso1G+zkYy9AAD0pt06uQvUvJAKMzrE29PKGe9Mmz9QRpZJcAfA8PnEOMXCXnZiDaB5goUfP'
        b'2QUMe09vgKfxwvou1PRe0I30GQyzQBein6wCaYN9lKEwrREe3MAkakLVzjTnLEYSGSHcdM+H1/DqLHdmFWGWnjG70iuU8ZIwAA/jlXp8ENvkMWzgpjEbnAQ3Vz8SYoa3'
        b'gxugY5rTB7OmSbcP03w+wLPJDMkbI8BFZrlYs1YM5CvxcvF+HaKIdnAQtGOKmhcQZWaWi5FC9RMJFFlBhWFyGg8ehFcnFoYdwR7SlqBEsBX33XmJjw/TO1fHLMTeBFf1'
        b'nvKYMbLElg2HdJEuks6/CVGxEbbjeQgYMUY9OIMFN64pJ2WvBNfNicHvhrqJk93c4UXCJyBB04CdYAdxOTHN3wTqLueZtbbhWeAg7obVyZq1OLIOyqKsqrRc4qGCMWw/'
        b'7YEY147mEzXGZD6hF8xexFtECohMXkZikiamUWnOpI2OVlqIX8cYxxegE3b4MavRSNqX8EJyKrwRzQYdtqCNjAZNtnAfKgdPnUDbBL4iCNzEkxzfQh2zFNDzCHusQsPq'
        b'Sbjt2ZbyGfAi2DtpEG1oxfD3JJpcTU6KYA9KswPs0aVMCjl+4GwpsREPWIJ4i6s2bH5cOQF3wFZtMAxlKaQVKWCzKy4pA7alCtnwCK4TFcThONsBORGUCbiOp1H8JJHD'
        b'hHMQV9AKhv+frlj+98eZ/Jsrlk84FGZeWtzYz7JlIy8tZFlylg5+QdGsS65KYFEOLt0l41QhZ6bbNyTsiNcYqBZwLNAtHEq01c5e/Xa9dj0OfQ4SHWz1Gknb+sgD79qG'
        b'KG1D0Du/JE4Sp7Z3Iaa88ry79mFK+zC1qxu+/Qk2Yp035n7Hh04uVfmUqlzKaJcypV3ZQ1EwLYqjRUlKUe1Y3h8LXy9ULnhBlVZLp9VKdJSOPiorXzXPTxYodx/mDgtH'
        b'3W9zxxLomBwVL5fm5Srzi1S8IomOZJXKykvNFdLcMJobpeTmjSa8mgySx1ao4vLouDyUYEWXiVooGlqqFMYqmpSCGkSJgE4uVi6svptcjeLXqKy81bxgWYTCYsR2xIEO'
        b'wbayvByalzNRuotnn4B28addgpQu2YqAkQg6LI0Oy5boqrmBMnv5ylEtFTee5sYruQVjs5WZC+ikAk29PN+hELKupOSlj2rf1r9toinzoZN7nwntJEKc5Qrxokq4kps9'
        b'qvOqATAYC1RFZdNR2ZoiUEJD2skXJXR0wxaXwTJtufmw412vKKVXlNrNuz+5N1m2UuUWRLsFSeLV3j4o38ouU8Tc4bm0KJEWpdOiLFqUN8HSh0i4dsTaE6/TOAaNUzrW'
        b'DooE8vXQyaPPkNClxleoWnRJOwU//hVKO0XiX0Z9prTTHKVTikJ7xHDEhA5OGdfXDnaQJOBVILs54ybLWdbo1f0/GlZyKHfvvnTaLUSir/bgSitk7kMC2jtc6Z0+ykF/'
        b'SS+Z3DZReWTQHhkSw4e2jrRtADaor2SpPXnSJll8T0tfi9IzXr5kNPpCvSRRkjiuQ3nxUUwSzY+g+bE0fx7NT1XyFymxvXEJnblI5VlBe1ZIEh/auo5TltZJrIfCOfJ8'
        b'vKZYOGp924GOnk9HF0oSpEFdGWqBSJ4wVKoUFClWj6ynI/PoyCIUE9iVrnb1lgbJQuWrla4p6DOawHyj/sLly8xkBQMOQw7YPF/tJpJmqJ18xzls9wh1cPgYTy3wG9dG'
        b'P8YpFDwMCHv8QxI/rkcJAiXx3WmSNLW9kyRHat1V2l0qa7hr76u09/3EzUtmI7NRO3FRad6xLLVfADb7PW87bKvmB6Fy0D1UEAofhkVP/fkNKj2O9YiEknhUjQ7lwhun'
        b'dHHbMX3KOXF4kTyfNRY3FqfMynst5U6KOioFH1mRz2Ji1Bnzp/4kZQj8GVKZsUDlkki7JCrtsACc3LpX33MU3XUUyZNVjpG0Y+Q3lIN1Pl508uTTHkFKjyhFgGSe2tGj'
        b'ex3t6PcNZWOPqvARSbX7jNQBUVJt2sn/YUjUiCMdkja28s46fAxF8CJ8OwAxvi+Cdg1QmI/YKF1j0UftLRzylucPl9AB82jvRGmsWhgqqxiqUwrj0EeRx3yPU2aEehzK'
        b'2Goff5lY7j+wcmglXg6bz3rgP1cZmaPyz6X9c5X83HEDytef9olCqsYNYBKLBlYNrVI4D66VrX0QGKOMLVIFFtOBxUrf4nEO5Rv+UOBDC+YqGmhB9Gju7bK7glylIFfN'
        b'n/MwLGpk7r2wjLthGaqwLDosC4mEW8BiwoEUWZzcXe0zR7Zu1ESZnaeMwh/1vKTbLcqcfHreArn2sImiSeUb95PaSyDT/l6H8glThs1XCfNoYZ7SK++hg6vEEP91GX4j'
        b'1sGj+jgHD/fM0D9lfW0GY4WwQPspU4T/6dNrxlPra//Cw+oBtmYYmFxNW4nNGWzxYth/PPiP2UP8jJt0Htv9WTVuxtdbcLAVB7+h4L5FGfZ0W9HELBeWYbe2tctqiPV5'
        b'4zYcSLGZmBcHJdXVWBPfN5pqvHvfcIqZbKM/To3h6I2/42AXDmah2u/rT1r33dfVmNLdN5pqwXbfeJplGDEZIpYlRCD/sfPc/gXVwO+CzzgWYUI/Tmkh/ZjmGDwIqwV6'
        b'F6WmHYpghA9FwIEd5c5VGjk/NDZvzZe4SzkSW1mVPFZhrmgezVEsGQtQZucrFxQps4qVpYuUlbXKxUuVFcuUwfVKwXKlcYPKuIE2bhhnl7GMQ8ap/1chPvGgkfW4ojjO'
        b'tKMI5uGjCJLwSIzCRyRsjUPDoY2LxEo9Q6CcIVCb4+eCjQglsRE9wkFrMkpg6djxgnqGt3KGt9ocj/GWISiBZcgjHLTOQwns3CSoFh/lDB+1eThKYDcXJbCb+wgHrako'
        b'ga2rxEs9Q6icIVSbR6EEtjGYDBQ+ImFrCkozldQ4TGoCITWBkJrAkDo1DSbVHJNqjkk1F5EEZrYdqCIP5QwPtbkvSmDmjxKY+T/CQWvsEyXgB5Q5eTSh8BEJSSFWTh2r'
        b'1DN4yhk8tflclMYqCqdB4SMStuLHi7WzRE89g6+cwWcoscaUWGNKrEWtSU8wzQczzQ8zzQ8zze8ppqVjpmXiWlD4iISEb/bukkT1DF/lDF8mjT1JY0/SoLA1bVyPZYym'
        b'EM8IdFjGdvjqqUCniIPPaPjfCBkoMVl+74PnW8Q5sU+8xLEoayjTqgLXc6bBqCe9Q7+IggO6xJoPe/qnNOZe+tW6k5Z9Wv/7ln1G1NOWfbXpzem4nVvtwY0seFXkO8c/'
        b'0C9ABK4AeVNT44qGZjF6E5bDYXiBWAVcghdN9YwMTPSNDcEe9MK4E+6FB3IyYSc8lKdNwbPwqqFhHZ/x+Qy2BBAQdjsPu9KDe2A7hzKDR9eZc+A1d7iNQcBvgtvgdXjc'
        b'EaPP/Sg/eCOHbFB41sGjJEudMfrigBcbUdZzKCPsBWeZnJd0wQg4B+UiNCT6U/5ghEc8O7ukwcOkUig185nMehRn3QeONeNBdhY8I9KdK2JjzLsIXltENn2K4a15qCpM'
        b'K4dFmbs3BKEs5XCQsVDYC7Z5iOBNEeLcHGoOPC9mtlH2lwUyTQQj8BbJOgtV1o5yegtIVaAX7HPUYomQlgRQAXblTDa5G7xIWgcO6ZJcbMrcDGUCQ0BCGgeGwYEocBOe'
        b'FKFJRyAVCC6vJ/Yz4UZmpG0ssNdHk4+F850DPYROdLETHPc0EKHnQRAVlAaukWx1M001ktAFPYgd4Co8jPPBGzqMqU9nuRXYHiNC+htMBZvCK4wv5KH0akIlT9c1HFxj'
        b'qpq1iFTEWw9khnAIYEcAIVQIuDqbtMwfXAfHGO5f0fIhInfRCM6jhrgmd3IGZ8AQPAEuIrGFUqHwBjzJ7IMp1rlqRO3ExhIDHRa4aZtzCInz1wTCVlts+xlDxcBucJTY'
        b'cCyBL8JDTH17OK61Zhrml61qxmbD0RsiVsJBbJwQS8WKWYwJjQR0YUOfPaSunnDE+MoQzIpt4DjD+kvJ8AzS9xExknUcFYfSkKZZpcGjDBPhFi7Wad1FmJEoazjoZDRy'
        b'IzwxD0jhRWz9Gk/FV4AjjLVVBNzESHvnApJxFsNKeDOJ4f6tGeBwLDwqRrJOoBLqmsnIs863VtMwHmEk03vOgVZPnHUEdjB5zwZY6MGNYiTvedQ8eFWbWC7YroX7SA7Q'
        b'5w5exO7AwQgWez9mqGwN0cxoKx+wP0SMRJ5IJYIRe9LI2WDIHjPGP34iW/hEvzvbRCoEnbMdeS4Qyz2JSoLXm0kTLVYVMcT2VDAKs0jT5wRRhDUGi8npukMYdEwlU8mg'
        b'q5iMEf6V4LyGqYgxPhNjRDu42oAZG0qqXOm1EJF9GmJ39ilUSnksqTId3ARE7GAzvNAIjsNzGuG7GjJddkdANNgYAC8iMaZSqfBFYyL/2ZXFpDLzAKJrKKtGinC4jJH/'
        b'vpngZAwmFUkxjUqD7YsZj/EycD4CS2Mt7NdkDdfIcQe8RAgVwX5wy2o2vIgEmU6l++YzihPDqChsX1ZNemDvpChOa5E+AaSgF3ak41PGkRwzqAx4dQEhtgi2wlM8Rvo8'
        b'XWcsikI4jHKao05DVO4G6AIdmYgFF5EgM6lMkQ1jozdcNpvJFKPpTGfABZTPCm5hDgg4j0YKOTxYja04s6gs1ISLpMZCvSBGcTZh8WNCD2iTEWYPaCdt9KhrjIJXDJEY'
        b's6ls0A/bSBurPeFlIguSDevMUdRHW1HGAjjEsPXIbHAEnII9hmzskiEnCAyTjfIWeI2v0fOJRwWjAUOgE9d7CZwk6grb1mbMdjNEwsylcm3gGWaX/SY8WjWpP5rBG8sz'
        b'Eypw5t2gj2FwL+yGp2Ev3GiIhDqfmg92M178UYQE3iTZwOZGPjyvGU8PbyCNNQRSR08dQyTOPCoPCfcQYW5DPj7Oncm0iTyXwEYwhLKJbQip9WBPyhInQyTKfCof7BOS'
        b'muAxMBBPVJzDgafAbsocP1+wK0pm4O41tkJD4UVDJMYF1AK4jcso3V6tatIycHQ9lkov6cfM02xInzDWEl4F3fCQPmhHPwqoArBZM6q0NoBTJqGgHYmqkCrMSmEUZmuD'
        b'vgGQgHYkhSKqCLwIbpL6m8GQHZSDE3AfaqyQEs5eQgoJAO1LDaLgPtQWH8rHCuk5buBKvgNoL8a2oc6UM7hqRUp2Becy4A0+3IdK5lE89ATbz9Bni8bFIbAxB3HenXKH'
        b'm+EIQ8kVU7gtERyA+1CTfSnfcLiZVKldV7zOgZjE8Sk+uAUvM8PO9phUETiag6jzoDxgK4trQBRv1XIfMjxuxgeQE/6gTulOujPiLFnR3wR2mmFx2YPrzKg/8bDdCw8x'
        b'ttoXkwsIk5fUk27N8BgPJcY+jOz2o2fGEPOgdkJzAzMgE6BYf/TQJTW08mEHUQik8MxIvUgzMmxNaWa2TqBsGSPHGxa4V8IXJ8fVnajdZFKwD54tYR5kcBNpBgsfY4+T'
        b'nMsjgyVSIQnYwnSVQ4XMhGrRRDHbwR5GYzbqg11MVedQd2PGAI3KJAqYmobnwmMT84FY9MQ+qGkuHIRHuSxNkzPg0RTYxodtifhkc3DO0oUNNmmBI5+RqWRHYxTXgNgV'
        b'ttSziRcL34SP+fmJGmNDUaExhSZVXr4J6hmOrv6am/X6FFIfX9/AtsBCLRZz81ekfthy1XfuL55hdWLmZsl6LQp9O/nmhbNqjbjMzR8dTCkkLivf6uooi9xU5maCrQ6e'
        b'1s7w1TGNtKo2Zm66xc+gEMOCffP+ZLjRz525+aa7AYXGAj1fjxP2m+qqmJtv6ZtTXrgih8HV64PqmZu9DpraE65WZfrZMzfbbThMM1e8W/dBShFF7MfNLGcjLUW1L3tU'
        b'Y+fRRHHZuQkkIid+oohtnvPqA5jUP9hraM1LL1dsMKM+O9yF/70WSSr4QFeXia0+OP+ldBb1mYj8+y6S9BZvNHPQQsMtejxS9VQ9vAkOkilOUP1SA3iMh7rQKmpV3DLN'
        b'eTH2zJR1TwZRBJ/86SqXD8+RGi0Xa6g3yRV08A2ZdjpWaziyfnjRyvV+081EUe9jXiDCKeyt5BBVg81ELdex2thS6ln/0PsMyn96soxO9k4rbEKq8RVyX7t2WWXVKi6H'
        b'GJI2YrKZVRB8QtSkhw+s1mscxBXly8pql+Ijqx7bitbVipsq6pcun2tqgHLhR8JPGymlTw7zGfWTa18xvGCoiD5vMmwyeZu83ZHGxpkuoORYIyNc7ZwSY5H80tNr82xl'
        b'bDEXURC3KnZX7rvLcuaZH7V+tWFt3attHy3pDo5SHJy9xkf79ZPG95ZnsGttzbLOXfPu7H39Eaug5X3Z6FhrYtbLhqafbhqxclsv/f1u5KZPPlJ/02DS6vrGt11dN+4V'
        b'ilocf7ddI9lwSur42e+5vnpDS4ycEu3iWoO3+Kqit1jF7wzeGdygdeK21iutSX2ttZWtBR+3fjRm5umbxF+4Q8EJa7vue+PswEXbluB329fd/ntw1K9aum3HPxR96Gzn'
        b'sX63T2vZh7wP7/207SfBTVeHl368fSI4IXy3Y6vn8r2rDPrbIj/0/NDozaEvD9nUNJh81sCy9GtPUezkKXYs+ePRQ/e9TywOW7z1/u2St1cH7sxOe6vrQcrbHjaFP4df'
        b'Ajr3jjy48erWwp7yX11mum2QilqaH5xWvn49TNklaHiweMmYxaOP7j98YUVNYNTvOYuWn7D54Nire+xH39tZKHr5lLH/L58stjzx6end2bP2b/K+WvT1gtE3fqjb/Nvh'
        b'kj3L3jcL+2n7Beeg/JarNbkN902SZH6ff5bF9ve69rJ37Pw3xUV/jeAXvr3yo4OnLy2EdKO0ru/kq+dzYt7//PLfls49q5Ztcbt2srxi1lnFkjvjsnc/mO/qF8b3axtS'
        b'1Jwxr1T87ZjFq7+HS77+Me1g4t+3BC8Yqf/rkeKMyoBTudxM/1dDTpdVbXnxl35P8Ir7+3o/D6zipewKFm/44dPLg395P23k62XrG5Z8fub31ttVWreuNVu11YkbMu79'
        b'/reWppRbx9/Krxl4u+ZM+bzrzY0jfu9671+0tft9g9c+3/G3Ij+v3042XL/05fv5Nn/YJf/zg0dL1FpLPll7R7B+zkdWs5dmz/LPC/wqsaRJ1lm3siNt0UunwMcXapPm'
        b'uKxfq3Dlfr1yac5eAD5N+v6L3yWXrM/++ql/9c/vfJqedCq7c6hln/65/jfem1VS9e6DP79V+7JF/oD/H2/s/cN+s7dbfzl24Oe9X56JPPi3kWq3zX9KS7ixJvPu3oaQ'
        b'tyq/Dn5zfMnPHX/8afvam13nbn3+l8vzfr6g42CUdLjkpvrLpafObVtn/1PLgT/L7A81uX668p3C0lf+/OOGnK73zr7yXWryXdv8QPcT87+W5Hx/Zck1hxLR90V2GSGl'
        b'J8L7wScr/zzb7aU8e64J49++oRxvyaelZmiDwQWU9loW7IN7GQgGbBe3wHbGoblWIpRHssBFuAUcYazqTqSlYvvOPfCqBS9F4M2iDOERDnt9CZN1ZwR2x4/+rqA3JI4B'
        b'2BrM8iuGlwmmwAVeC+DB3WAoWZvSqoTt+SwwUtfMWB7Bg3AgJUPAg7KkJH6SFmW4gg2PwFPLGaTAwcqiFP5j68EGO/ZqOOTExO0B561QqT6IEq1mrWoWbIOHYR+Jq0Jz'
        b'pOs8Idyl7Q6lFBtcZOWhecUIY961IwDux7aDE5aD8Jo3C701gOtM9A1LuJmXLIBnVmA/69qUkQ4bzfkuwa2kKctDQlOIoxlUqSW8aYj9dRyyZkBLm9DDvBu1BZsi7iWw'
        b'pRfyCBSkSQvcrIJnph8B4supWQxaua7/95ZFz7XvT8bvZ5shTdvd1xgiPX4grJlyTbb0dXU0Pp+a0liURQyrNX6cPcPKRD3DVpIzzsFXLgKZmLmaEzlqRq4eklhtfEVi'
        b'yRWJxVfjOtRMOxSvy1y7ClEKzXVAFAslIj/0mET6zDVJpLlmEpEfBkwiQ+aaJNJcM4nIDyMmkTFzTRKRa4q5waQkd0yYlKbMNUmpuWYSkR8zmEQzmWuSSHPNJCI/ZjGJ'
        b'zJhrkkhzzSQiP8yZRBbMNUmkuWYSkR+zmUSWzDVJpLlmEpEfVkwi68lmWVG+olEztb2TTDz9a9xxMg0OWhPHXSbd3PeFqcx8aDMfvEjsoZ5te2jx3sVSs876/fUdHPUs'
        b'i0O8vTwJ3hj37uCpZgXQswJaY9V2jt2JbWmt8R2BagurQ0V7izpL9pe0Jjycad5h1pEnqewsUc10pWe6tsaobVDB4cbxrG9I2KGD9x0cJRaSFdLyrlUyHVnjgL7K0U/u'
        b'J69QuJyvVllH0NYR41TITJwDhx3Rahu7jli1vYtkvjSgq7gbm6BYBJNAwlJb2R43OGwgDZQ5y+IHPOXRAzzaNVBlFURbBSnJR81DaQMscHE4lJiqnVwk2mpXT4me2tlD'
        b'aiEVS8UyUc+qvlVy5561Kuc5tPOcccrQ2ocEkmi1i7u0vM9DEvvQUThOcex9sCVHg3zmgHgoWKon1XvIE0r11I4u0hcOb5BskAcrVt0VzVOK5qmd3PuNeo1kWT2mfaZS'
        b'UzVOhlI7uUsXSfWl+n36KMYEX/Wg/2pXL9lM/NcXjMiycjpufNi4y7TbFFHrypPFyrJlsX0RElyNREz8tK/qieiLkPurXANUjoG0Y6BECyeMQ2QlyOPkAbJU2jUEp/fE'
        b'AA93tZ3b9zoUotGra2n3UplYJpYHD6wbWqcQq3xiVA6xEs5jVgT0rOlbo3L2p539cd54FhMiRnjyZVmIS66965WeEQpXpWfcqJkkXurclShJVDs6H195eKW0uWt993pE'
        b'jJX9lCY4ufTr9urKtHtM+kwQ613cJLpqd64sQJo2Ts22xpLBoSRO7SGQs3qWSOapXVwlseNsM/t4ltrLW6qt9vDur+2tlRsqclQe0bRHtJSjdvWQzewNkgap3bhqT2+p'
        b'ltqLJ1s0oIcTc2XRPTUoiYf3OKXnLJA1y8VysWLO+dXDq+/6RCl9okZzx9yVmVmved4uUeYV3I0vUMYXqL195M4DXGmsmic6Fz4YrtBSzB8VKQpGTMdmqXipNC+VMXAU'
        b'97ZIW9ReAjXfTx43kCqNxxcxA8nS+HFjypP3HDWiscNd8IAnnJxXo8+Y9ljFWONYxR0D9EPlk0P7TKKTClS8AqRprl79c3vnyt0VesM+KtcY2jUGW8UgRvF85WZyF7nZ'
        b'UKi8Sd6kmHd+3fA6JS9O6fYPP+OemMPf6FHu3t+YEkFEko6ij/vdeBN6UXfqCJ+yj29wn1O7tOa5tvDF2HnY44165n2kH1vBTHnkXMdmLnhTmzxyxGksFmsm3kd/vuA/'
        b'tun+AaLk/2PuOwCiOra/7xaW3hdY+tJZlg6KAooIKrAUFbBgoyOKgCxYsGEHEV0QdUEMC6Iuioodu5lJMX3X3MRNMTG9J5iY8pK8l29m7rLSTMx7vvf/ZL2wd+bOnTt3'
        b'ypnzO+d3hoTYNRrYtRGmNv1hIXYNSGRxhq2NKjTShdbl/ddD646gHh0tuKpz6uh8mavws7AZvsxabiH7f8iYOYI2kTNKvfVSyQ7zCBfJgfF9uBf5f2U9mSJke8meNlj5'
        b'MtuX4TrMKJ7hm5CYjuOF7kzUoyLW8HzLYE9x3z4jPSneaMfLWw68GI4ZV7eGHGBxdzRH2dsFZ3Neqlk1pu35Wx4108FOmSQn6zmD5oIt9w8Iouw32Y97nfWxjaF8ZY2I'
        b'TaRWT9gLz0jAWd5A2B5eNNtu8QTGsPbKoghiWJ8dNSJoFDyVZi9iDxoPWLwakMCM8xYX5C1dRLbw1a6LcOTqRZjL++H+fFAGIpeFUAzV5+LpaHDayJY3jZGN0fBt9k9r'
        b'mtaY2JwoS7zr4K3yGRRnxU4gMxg0gvXeZhWPNn4xcsIMU2aEnsIj9K9qZINVBiWUdtgWTUfD1hyPxFEPT2x0YmSYoGsu8Bxsk/inYgNvLsVzWGLJNgK1Cxld6hq4Qwyb'
        b'UtkU25IlBueoxfqkN72by6F+WYb1PtkludIISsQiBGPL4A20O0hOTcWcdwZp7JIQaeYMcsFsd2OqPy2AoiyyS9b7rWRiPlxNm55uWr6cQ7FnsQLHUP76jHaqlEtpwi0I'
        b'i2dioiVVgj3jDi3Vm/wOOxh3cpO35uTPMaWkWFtc8mJ7embVjys5FEfv9myW17jz5G7fZepRV1fZkSIsp6QxfoTVb6Z/hF6+cX4OZWxWSvJxg3lUf5YrEvaz/RfNCGPy'
        b'dRgt/Ai9NrPpMsqsS0Fof103+n30CdssBet8Bf0yKVblL15tmZ5pusK0/JW4DIriBbCapy2X4i7h8+67xHq82xe7fFif5uRoPva9TvYeUtymzdkBr5u/4P8CGmH6LPZX'
        b'T4VudCb3fe7NoNdx3wq7Romkygxy7vvNla+jmcYvKIHyu+tOTim2X69HE9GCaeepBXPdSfW+v/t9vZraGUdRH1Jb76eSc7m3Pq5XcydfoqiPqG2R/yIgpZ4N6IL1iYRq'
        b'LIyLNpv1bHjZNmnRjOKlXQksKQZEFt3o3ppxuvSdYAsv0QvuXm/tsnq++PKK0nqT9361+6Lpn7LOMdn8JTX855YbqDo71GM+P/ZCfdhn6b9OmHB7Vl5SxoMz/rE1ldUr'
        b'v/v2rrPrmUXPuq6IuRx0Uq/fdWZYduuB70sLU5fYXk6+9OnOZat+uOaXMvcHC6t4R5F8/Je/7qlafMTihN5bU/LaQwJeLg54e8Y3Wzt3Tf5pzIQDRf/StK2vO3Dq+fyU'
        b'iQf+WH8c8G9m96e3xazpkv5840W9ON7t15rD0ukXchY63zX5OaM2hH3+ZYNP3jia91Ks5evT428F/3R/fWBkiJ637J0++dd3FPrjanK//f1Yd5zpRWXA28dXnoOGgqgb'
        b'hw43yH4q2FocJQ6YMTl65Xdv/Lbfr/Pzww3rFYE7ju4Vid/Kz2u7c2z+1SmJe0Kfpn8ut3/J+axJ2KG1ja9/v87zMH/Vl5+//P35z2xsko4fWleZ2uZ3yz7n+tfBau5e'
        b'+aVjRrcbNBP7fo40frb/6I7XC5uMNpzwOfbP6K9+7/159r/eKv1y+Y/c58+9/88JkYY/3qqa++rdwEzzdZGw60TYx5I3H2T8+JP+EWXW2her8qLuLjxRfuGd6dcF47bE'
        b'/bH+TuYU6cdVlh+v0dtjuyjmJ6cjrK+Da9fdbRUf/8F3y9cr3nxvonlR/e+mV7Lf/3De/QmXcy+2nRWfedv+WGF4y0f3Ep1e7ZFavf7FRDO3KyGN7z8bfv73rPm335cc'
        b'mfhPzoysvrjwSpEFo/VoEEK5RIQdMHkUrwjIYC3bzx00ksRqeJ2Lt/wMq6EBkLFj08vA7smMg84W0OWEXVVS/NFQC2HBa9NBzywboi5YBg5YECVDImzAvI8GoINtDPat'
        b'N0YFE3OXY6ATnJVWrlhhagZ2mZvDMybL9Shb+BRnLjgODhZkEU1FIewJeqh0YYGG9eBq0kRGdaIALUawPgX0YCKWLSzQzZsGehgWo1gxUIiTtCoO3kx/UMfmgwvwGklc'
        b'ApqjHqo/WNNwVEx4AnYzrlMHPXOw4oS5paExe/VqsAfWgTbmgffmZKJLRQHY4YOXDZqEbI/F8AxJWwI3gS2ERIohkMqAV9hhy8YTL4nJsInRx9QmJqOb7UHLojE4zYYH'
        b'4Sa4idHY7B8Hd0sSU7TtvIANtoMdBfAUaGbcqI5PY0kerqi8hWy7KXALuW8plGMgtS4tWYReXxTohYfYfOdwkd3/gQMFIe1+hJuEVpfycKmsHvQ3WbOf5mhXyMLpLK6p'
        b'fT/1qIMRZWNfO0Vjbq0yd9XYOe6vbqpWeKpxVCkfGRefWNO0RhGhthPTdmJ8QihbreA3bmjeIOPes7SXCeSeCj21pTdt6d1P+Zs6KN01fMH+xKZEeW57cWtxy9K2pcqQ'
        b'3gx6zFRZopo/jeZPk7E01nzZTFmObGbzGPm029YeKmsPDd9VJlGwG9Oa02RpSH7Yv6JpReOq5lUy7l17J/kMBVdR1WGitg+g7QNkPI2tm2ypwu2oT6eP0rd3qto9inaP'
        b'UttG07bRMo7G1k7Okce26Mnz5IbNJeiEta3cqylaFq2IVeQp3ToKlHG9rO4piqVdqb0Ftz2jVJ5RGgc3tNd3cFYYqR38ZPoagX27fqu+Ql9pqxYE04JgmZ7GWiAPaRov'
        b'G69x8pFLlKxT+sf0ezm9JergyTenqn0ltK9E7ZRMOyXLpmgcXHFsLmyTaxOBt+hZategXk813i7/cs/JTRGniFPqdyR3JaudgnF2L7lYkXO0sLNQmd7rpfYeR3uPUzuM'
        b'px3Go2Ks7fopO8sojaOTPF2eIc9oi5DFM0HWKlvGt41XcpQF3cZqx3B0FglkCU0J8gxFfMs8NV9E80Uqvkgj9FRUdhjLYmUFskJZYWPiELlN4+gqi5fF30OlZyrC5HPb'
        b'ou84Btx2DFA7BtGOQSrHMb2hqGA7YT9lZhPFaDCEbmRXzVEWd5v32aqFk2jhJBz3TagIbY2UR2o8vY5O7ZyqDO+1YVw5+tzUnlHyKRp3H7y35joHarx9yLNm9IapvSNo'
        b'7wi8q/ZUpCstOzKVYYq5XdG9Y257jFN5jMN77IFddb8huhT1VS9vBXp/iuKuZFSmp+hoSmdKr3efp9ozhvaMeeSp5M7kXoEaR/SLRCcsLPfrN+k3GjYbygz757JQpyU9'
        b'lxzu48MDasi50Q6//PLLqGlZLMqC309xTH2HjJRRxtHwkWbOV5kL0Wl5pgwHS0BvvlZCJKCnzRLHSMw5L5lzJdb6L9my0JERq03e5pbnVC5+m5ufU5nztmFRQeWiyuLK'
        b'kr/HIUF4/AeHE2NE8afJZvnhnMLHUvc+Shc+rADL3dj08z87PDH5fC6qbx570OZOt+NcSzE7TsJzrod2zVQhR8drPtya88nzmo+w5tRVbEicBrQlIHTZ28A1uEeShn0U'
        b'YZ0YKpD0iZYwK3CRAzdVrS0e80IPQ657XTj7wIvRBzfWdezp2NO9Z7npR6HevG1vTHrvggnraZO2Yqp8nl7z3jqmo3CGv3O889WtIqa44zxcSIZ+JWsJRnnJ/m+mNkxp'
        b'vrJYZT1ObT2Oth6nMhk3aKvHqwDY3+KZRzhdYOM8rQsF08+ex/1s6C0zcVeroAYcJopmop7mjHvLow9PrBthkeb/y240QnkxWjfipBafOOfHkeKgvqfPxGg7iG8W00Xs'
        b'rTlwiXAbNXUbf1s279VKqjxAL4X3ymN1EenQLiId0UVctV2kFHURU7vaJFmlPENt4k6buKsGPiN7CXzcXvIi6SVD7jpnaC9ZhnuJAHeGRx/+B71kPe4lHG0vYTEm5IXc'
        b'/8t+orP9GNRPjFKJ6XRRHuZiTYWtQDmgzWAbhYBustl3DHB14nN/MaDKP9gwbvIPfuTkvwo4FHf+MlRmdnKVWwRjjZGaiaoV/5ERVZ7jejK1iFGTwN1g/9J0cAL/uYUC'
        b'O+B+8JQD2EMu2OvEo0zmHMN6BJPT5kkUY7l0CV4sSQ+A+8BesEeckMiheHPZLNgO24qLXrvCkuKnlr88bd30KCMYzH99zb+2uHRcfMH+7fN5N2WnK/1+Yr3bMe+LJZGr'
        b'Xmjy+KmgdvPmeZufPtP185aFvzYstsryeemgUbVgKt15eN8Khf8f6R8s4ZeHHXgz797LQLr8uMfYE3HC3Utv/PD529IPpjhq0me+Ev/cD3fZiRFzfwsKeuH6pf0vHPnk'
        b'xBrLb05xF4RLNv2z5Av1rhXP5l283lnx8RdxPtH7eQUpn+/c/Bu786jP+nv7RQZklzEJKJeIA3znW2BDLB5oZQfAA7CRYVbdA5rhZrwTDAQ3Hm4Gy0KBlsyhGRxnEyuu'
        b'hrl4R5iG4wXsRPuybNBAtikLPOA2ib9vKZANotFlryOFZ8EG9BXt18BmtPvcCevQpm092x1znzM71JrVEm2Ak+bKATQbNG9gSCnOp4E2cYK/aB1GpLkRLHByCTxF7unk'
        b'G8Rg5KWgRkewa7BMpP84QgYe9VpaSmZGMcFTfnl+4SIswVQP+UbmE1o7n1TiJUewP7IpsjG6Obo2XmPhLDOV57cvbV2q9FG7hNIuoWqLMNoirDb2Ewtb2XK5l9pCSFsI'
        b'FZa0hUdtrMbaBl1jZY0lspBP7JzlOYxE1siVsWQhGgv+fuMmYyQyx7bMuePkf9vJXzlDTWLgqi2CaeII069PWROBLqTfgDK13J28I7kudWdqbarGxGK3ZIdEbqAIbzFX'
        b'm/jSJr4qE1+NtasstDmiOVrBVVn7KyrRgfmgamCJbtAkqF/xBW4J7p/SfpGW00pnzFz4Bp4LhzTYPDwVrtRNhdLHmAqf7HyIBZIhk46h9vcPz7HQcDfdTxVQWax8Koud'
        b'z8risKlmTrNJs34hu4c91MysliKgBnG5wcBGoUE+Z4vB0Pkui8umCvTyuVuofL0e3hHUWY7rZuIsHknTR2kGI9L0SZohSjMakWZA0oxRmsmINEOSZorSzEakGZE0c5Rm'
        b'MSLNmKRZojSrEWkmJM0apfFHpJmSNBuUZjsizYyk2aE0wYg0c5Jmj9IcRqRZoFbFYIvjFoMsS5LPpRhN2gWWQ9u2i7WLlWWJ8mKIyRCtW04ov1W+Mwkg6Pq2fkpOKXbD'
        b'/DXAaLBaIn3K9FjhMiZJSCLoBQ5JF7HIaj9kwcQdhKxKteiw12BQFCLdyycilqFu6RyOaz35pbNQxP5185Ca43+JpcWVxTklxdUFUhK4csjTFpdKK7H7aaDRiOsiy3Mq'
        b'cpYJ8fiMFOKgg/gvYWWZMIcpYnr8VGFhcUlB4IgrR4yk4cu3S2qVH/pmAreCbWiuhnXTE2Bdmh2oD5il5VgDJ2CtfyCLmsbSjwAXZpGYNvASOAP2GZcvT0dpKCMJv4Xy'
        b'ZhisMC3PgLUpJNQGWoryhAYm4XpkFceG+gGwPoCJGWMEtrPAcRN4nLHBPwVugItiHJBjd+4KSQpeo1rYa8yggtixSuEFeESclBIY4JdEPO+sfcBOuIMDD4CDJkx8lU54'
        b'HZyQhCaxKRY8VWVLwYtzpjDRak6UwRYJKplFsXMNQS8rBHbBp5hYWT1u8LAkMAktoKdS/BPRXY3L2LAlmU1uOj8RnMMLZjbYhTlUYH0yymAG2zmTncER4gQAjoHTsE8C'
        b'ToAOcDIB1Q4XYe7BmWMsJjJRyZIKRjWYBFtT8TOBi+w1VuA0E30HnrCTJKb4rVuKMrAJIgA2gh1LmVA5tctApyQ50Q+2iJJ0UYyofFJtJ3AZQ4fJA/EDsqCMBQ4Uwgbi'
        b'51BRBFslcAcJFJXswApChbYzUlQXPGSJw0ExoaAsVrNAJzi9mDyJIBc1BKbr2rQQte/DeE4KuIkAQ2yJHrZlXnU3LrvESt+WIi4AlaHgeDoFNkmJD8CU1UQe+40x286u'
        b'Ss1OdpyfT2n3onohAAduGha1CXWia3rjxbCJXPp0BrEin/OyYXbJWM+ljOwHeu1gO6qaNpDUYmcWuJwCtzF+XNsKEsSw1gIcCwocEknqFLzOxNTq9itHt0xaOF0XSmom'
        b'qCduI6wV4MyjQj2BHXl6hbP8SM80EfIlgVbspBRiB49eFOqTnAXgIDxcvPOp0xzpMbTgfMXPOpExoQwEW0yIMrMod7hueOLXvF8df+WcmWNiYnLuy/x9pYVfzqx6JV7/'
        b'V48153Z8IzGoy/J3u/vDPya87/za6t0TazbX7Qy/y9Ef9+F3K5fFeaxUZAdFtHxxqn7ZLfu2uVNdyv9YLF2TOO6q6Wei1d9e7skN/+3F3lcXtpzlrPtwisvu/asdMnor'
        b'Lz43d84zynE3e8rnvvjs2YPub8rWvLH65602qacaX+8u75yaehF88frEJasmvHhcaZLVHW/qd2Zv0o1Yr8APs7bGbpXmSX2aw/2anZ8JX5P3Tsazrddu/mT9lfmY9IhX'
        b'rWutts9yui/Ln/bUBjZtdvVLq+/mf/1q9+n6Hz54K9JnSdKij3flLXM+9sMYcZW1qrpS1lDy8j/nhYT9FCptaqEzUtJSFpR8eP6b8AM26k8/2PB6/Dmhr9fiL15xfv8L'
        b'9fXMDd+uL/iH06v+GZdP/MYO/njPe7ZTHnx0gf7w5SX0pW9OPvjDIEC17OfPx+bc9b61Nr544qaXp82vnPflwSu73onf/M4zmXe9s668siJr+TvtR+sWx05PUnldPBy4'
        b'Yu8bfSnzV7zz9vo3EveXzv5w3axJT3vEHy/7quCUTWW8yIGxpWw3gM1ktsNy6fgQJJkmTSIogxc4sVSS7JcDzgQyycYlbNgFLpYxMQYOwqOghxDR16+GJwlUbwDr2evA'
        b'UXCNIXBqHwPlmOBNpMPQwW5wygZs5xrAHg4hcAK7jOGNITR2A1j7THCDC09N1JrLnloBOtdiKiu4m0yaeEe1ARwj9awK9wL1QXBXOJquUM/FU5eUDVsnrnyAsVkR3G4u'
        b'YcjtMiNZsaB+KsOwtdcdHkSXDZpII/Rs4VPcSHgeygl/mqO+H6hPw9Mop8R1MmsWqNWCKLDJehpKIfMoB7aXsFlAZgMPMhDJVXAok/Bh4bCDZCI1W8wZB47OJoASbAbX'
        b'80n4pIaHE6lVRAzczAEdcBO8TPYpi1G2JlQIODEwk1qtEadywEVYW03uMiMxk1QgHVzFaAt+5BlsHEVgDdmq+CxOQ8mJ4DKaH/zISDX2YkMFqAXbSXo+2phshIfhQSYQ'
        b'wUAYArAXyhjWLxk844FK4IFDDL0qmQXNDTmV8HgQ85hXcsEeNIvWkGqQCYlnwLYHJyYyr74pBNThl1Krm42s4GF0RQ8Hbsx0ZkCsPSZo1qsPCqxcy4S3M0a9B160GUNu'
        b'MCkQduIW2Ay6cQQ7PO+bxXGmVoG9D7BUbGiM5tDUgMEB5Er1Bs1ck6r0LWGnE3laM7hlDW7yqdhXXbsWmxVxIt3hSYZlj4v6T1rgw2nNatxUBw5q2UOwm/QVT9CHKxOU'
        b'kIgPZChYmcGt8zngCLy6SGT2hKguMKxOBJVhHBeY/qPaQisjYvoTJDlpubq+YXgu+pekDygQFfFqaxFtLeqnDC0TWASH0IERzm0R7TGtMcpwtWMw7RiMU/Cpia0TlZ4M'
        b'MoGhlUmsuy6+KtFEtUsM7RKjEsRoHH3lE5R8tWMg7RhIisPZElA2P5V4qtplGu0yTSWYpnF2U3i3zZdxm400rv7ydcqMXt+ehWrXaNo1Gp00wVbCPkd9O32VUWr3CNo9'
        b'Ap001zgJ2xNaExSZLWltaeiE4cgTwgCFqTL/1OJji3tXqwNj6cBYtXAyLZyMEk01boEKZ2XlqVXHVvUZqYPi6KA4tVs87RaPEs3+PNHVo31V6yqlgdo1hHYNwRW85+qB'
        b'f2nsndsFrQKFr9peTNuLZTyNtf19ytEyRGMnVExV2fmhzz2fQMVKjbOHYmrbQuWs3ik9C1ROURond8XYtlT8azztFHBfn+vr8IBCBzm3zaTfjBIFKVfTvuP73GnfCXd8'
        b'4277xt2Mu2XJYFxyU427SOHTu6KvmI5IULknqt0TafdEub5GHNIrosXRcn1a4KvxHdObi4qQ67eZavzH97nR/iRBpPEL7rWn/aL6Ymm/iSjVXBMcge9KCwJUgoDHqe2g'
        b'r5G0UyD+PY528r9vqo8fQl/7EBaUjX1z8h1+6G0+DigRRIclqfkSmi9R8SUaf9SjmpNpvuiemxdpYkfX9nGt4xRJTN+SGWisHXFDhuOGTFDZ+aPPPVGw0k7j7KUopJ0D'
        b'lKv69Ho2qJxiNE6eilno7vj3XNopCDWlH25KP1wLbMktCkGP6xvVN5n2jbnjO+W275SbebdC1L4ptG/KQFOuumlIRySp3CVqdwntLsFNGdabSIsn/lVThvaOp/0m9OXQ'
        b'fpNIU4aOx3elBUEqQdDj1Xfw9yzaKRj/noNaFbUmfg597XOQ1ky9ww+/zQ/vndNXRo9JVfPTaH6aip+GmahEqD1Tab6PhmlPGfoZpOYwYWiYwL9Fw6RFpx7ONX821ZRj'
        b'PYiMGtCDLEh/TD3If11BIsW7uDbDUOqMWSzFGWIYqYvabUX2d2upJboktOsuxDEb9dgkPveoMe91bTAQ7v4VI2zpitNJuHt3vPMc2K3qGJiGBLavwNxUf6NOOI6kiPW2'
        b'/iJpcVFpQf5j10yFa/Yja0jNSLXKCoW4qJzKqoqhNfsblVrMVIq7KDc097Fr9Dqu0UldW/lOLckpEhYXCosrhcVStE+fHDpZ13b/Zr1I0M2PqL/xAt8cWikn3Ex5FQX5'
        b'xZVlFcLi/H+3IqQn/cD9GxV5C1fkvK4iLtqK5FQWl5UK/9M2Qe/KcNGysvziwuK/0YXexVXy1nUhH1ylkhxppZApKe8J1q1gVUFeVeXfqNv7Q+vmqasbU9ITqpg+Q3T2'
        b'+NX6cOio8xvo45WD5gXU2ZlS/8PRp78ovyAXddPHrtwnQyvnSqYEUoQwJy+vrKq08j/p7uQ9Dgydx67T50Pfo9uQ8fcf1qpooFYDmvvHrtVXQ2vlNVihiF/lgDZxaM0G'
        b'VewhRLmCwkD2fqqWXcvR2t9TbKpumCZ1HYvoV6kR+lXWCB0qtZ6l1a+OmvboCO+j2d/zHuE3QGrNYvwGCln/Q68BrBWeM0JHi/+RobRycQFq/wr0EtAoGjSgKtCgr0CL'
        b'baUQdZvSssqRat4Rql5d3xmK6M/6YylXireaRvu2H3hxHPYnqGfxiK+A9w72tJ8+tukWsRjYcGeugVZVYB2sVRYQVQHoXYB6msVAT9MKUTcxZ6XrQE/TVfih0X1hUUEl'
        b'2b5hC2ksUeXOZlFOwrYYFd9vkIDHZQS8obIdZnwipv1/417fYfmtiNLaLc6bjcQ3KyyHDT88MdzqafZjWntQtaz/W2uP0YYK6hvHX2jWk+JAMimtvz80Byq29yCWHjWp'
        b'z60S7HHb6tY0Sb4xzJRqEuopcaQChuJ+Lwe2DlEswa3rme4yHm78c3uQiuf/8nVKtV3HQdt1lqCu4yNW5CvHdCztWoo2DGky9DPEJIT0IkvW4xoOPU4VfhpqJFKMu5Q9'
        b'7kOPPjxRIxERm/iFLOYYSrBuD25OpbjmLHB0lgdBQBYlwt0ScSpK2DSH4oaxwNlcsK34I/fn9aSYV2/+8nHYgWjjno7NooaQHzdtPb31kO2tL7NT85Jy2GfslwqWCNLl'
        b'nwXrhZUf4VBP1xlOib4+MCJH20rhzv2w/b5Ch2rLEe1HXloK89I0XIP+ObNZXEtxPzXKwYxliX01Rz/cE3oq81V2YfhjETZkthjt7T5W3b7Fb3OptkPNxe/SEL+yUQ9P'
        b'do4YdUkicwSXLElcgphSWkuf/93ClDJiVYnDjlJSRsJDy9BQtFIqlFYWl5QIV+SUFOf/BfA4mn0ZLzVjKkPAElRtlkBZoKYRrpiT9l5K8R85FEeKB/C+zxsOvBiKFikv'
        b'tEjtaJkp2BzrvjO40X2FcLfhq7jfvhQGq8rZq/0F35c3si90js1/fYm9XBDZshT938d6ZX5D8OyubTksMce216R2dpjwwcrQwGyPnpPbOnbUb3Srd34uLefVwtg+84+n'
        b'vVpJTdrv8PW2F0QGRFFr7wl6xQ91n65ZlBm4wJlmaM4E39gGGqcyaKUkhQWuwoMMXskFmxmbnB5wxlrrFZDCEsAaBvqDN8BGZnHtEWI3CN1syYWHKGsfDjxQCa6R20dj'
        b'gFWiU4WDXVkEV7TwJIY1YngBbiY6XVDrQHG5LNAOd41l3BE6oyfkThLDurRE0MOleCVsd0NYS0CPBaHREnTSnwf3OVFcJxY4A8/OF+k9Wl2Crb0GWdkYFEsXkZf9UKIc'
        b'OEMGeqt2MFWj2Vng1LwOD12hxtFVHq6xc2xeg7+6KfK7lpI/NI5C+Rh8fj35qvTsCXh4/h5f0Jyi4gcrMrrmYQN/Z1mkPEchUFv70dZ+TDaBfTuvlddi0GYgi8U+AklN'
        b'SY3JzcmKEDXfE2VSZty2DlFZhwzcRlY5xFZmFBljVFOZQUZGFSLeYFl64Ml/w9PICmrA7/eRYsZ/S+rAC0Mq81jWo9FrD+LRxgZCFV/iN8nJDc2twLHVKur18Isd2Du/'
        b'bTCwU32bx2zi3uYxW6i3DQa2LW8bDOw3yMxKmkVk+p8DAabUMM5rptU12EBpwFZkKW7sLPYwmms2prnGBx5lZlM7G3szyP1Upl5qUy/a1KufPZdl6t1P/ftHzEzt/bCk'
        b'FewhPMzjMA9zJKZhjsQszJGEhNnWRTZHYyFSWYiYDLY4gy3OYBtZO3UY1TNmabYmLM3WhKUZHQnb8+A8oThPOM4SjnOEkwyDWZrDMUvzWMzSPBazNI8lLM2DuaAnYC7o'
        b'GEwFHYOZoGMIEfTgDJE4QzTOEI0zRJMMgx8Ec1/bEu5rW8J9jY7kWQbnGYPzROAsEThHBMkw+C6YgluAKbgFmIJbMH5ENXA8B8EEnGECzjABZTAwMg3vpx51sCV01iqi'
        b'qVaMV4zviOqKYr7VJvZzLTBz9N84MKzPeA4Xr8ch4INhlw4/MwK72ODKeNA8ZG2z0v7+AYs7e+1HmKfxmgXNVA97qBEVsU0yrbWqtS7Ue5JmaUy5aHthuMVAa4jmQIyz'
        b'DEYxzjJgatdjNMxwDgsgxqhm3HzjETUzfMQ1emgfbTIit5H2+QU9pkNrmu9I7mFF7mK+xXDYdcbkOgpf2ayPfgQ9FkfQPHOcN5DDEP3kO9WyCLM2Y+FlWmtWa1FrWWtd'
        b'Kyg0ybceUabJQF3Qj0GzYSGnh48kXeq4jiUh35kYDOoRmzHjWhNUnjmuYS2/1qbWttYOlWuRbzOiXFNduaTUZv0e2xHl6mlLNCel2aKSDPPtRpRkpm1bwfC2Ra3Ezrcf'
        b'0brm+WZED+Tytpl2gkS/cooKKj4IRxcPkchihUNzYDEO/ZYKc5AEN1iuw3ZpOZXCnAqs4V9eVYxm/SEFFZZVMPnzUVJeJdawFVcKKytySqU5eVgxKR1mvpZYieTEsgrt'
        b'rXR3yZHq1ExIwCwV5giLilcUlGqLLatYPayYwEDhypyK0uLSosjIkfZxWIM17AF18unkKRmxgcL4slKfSmGVtIA8QXlFWX4Vqa7bUOtCNgMttbOH0WfoWCnwSrpXT0ef'
        b'wR4gdScGhvo64gy9/zpxxhYR+4Os4a+ZNPgwG8MBgX3ZQMP8W2aGuveClVSocwx+maNqo3APIi8+P1CYSGCQ/DJUo9IyrMQullbiMyvx+8nVIgEFo2witBXSakqZOo3Q'
        b'n64sxpVEKYVVqLic/HzU2R5Rp9J89F+YU15eVlyKbjgYC/mLHQyPGrmDMU2tmoC++SbC7YND3yborCpgE2xIJkFqZyYkp8JdQWJQTxRp4AbcbgwPw/OrqzCvAgfunzx6'
        b'Ceg6rSHICrjdEF4PWgdlsI8YxiXCM+iaPeLUMfBQQAKX0vNhQbk1lzCCVhaIxPobwDbCCEpZkfVsaRE4mx4Aj6DLDodSnEB4dAxlHs32hIfjq3wpTMCXUYKp+8QMIckM'
        b'X2IMOn1mwCyo8GFTESI90AgvwU0MVXE3aIOnxezC6Ugio6QJ4ATZyiXMIBZ8wslUdrLK2YSqIkHw9kVmSwaeqBLUBM2EtckzcABBf7grxZ+E6JtRpg9r4BUxw9Tc5VMt'
        b'Xa6H/T4wa24T2DF2Q/G0z6ZwpBaow/f9OH3vzNOpMJh/tcjn9OvsraFVnxoLfrHi0XXPcpK8ZAYzLZP2lRZO62lx7/rdM83mwq8OHpsOJUz87Nu7V+w2yNNWLXDrqb7f'
        b'6fHjNzWHnqrZyH7PUvpG0PwxH7b6rf8u1HPfxZk/lG71Tlva9u2l7W4/qScrd4hSfzwYcbAFePr+0rnxpa6vTLOWKM92OwTGtH3huLJy/uvfuM5t7B93A4z5suT4wh8d'
        b'5rn3/KP5tRvxIPSTt5xW05L7K43Knl/39ec+BxILDxxeW71+e+3lf3BffeF9p6LZy98/9kfKZ+VvNrz9dXrMS1fm7vr2yI+f/LM4Y6N67qSFYVncZ6xfXLvwoP7v53Jv'
        b'1MuXtbz4aeHtNPeT6+1b+qb8o9+03Dj9QvYKEZ/s7maDToqxcoXXE9i5rBCwHdYwhk0XYV/8gEka3FrCWJsRizRvHmOVdHE+VEqYnlYFG7XWpuVo30gsMGu9wXmdsRwL'
        b'bpoFToIOE2KxVAQ2wwOSZD9iLAf3+Wrt5crgQVLwfLArajAXIssdXgan4cHJjD1VbYSzhLEuRrsIQz4bboEXQYcXuM4oFc+irLtgPZK/UnHn8ePBHtCI9uHnODP4meSh'
        b'4dWiRHEQ3ME1xPIZDyjZ/txwUvZ8eAB0MoZ6Ois90CVZFxvNuKacQantaAeO2ovrxtJfAA66QyUpc7k92C8OFKXpDdAFsMNcJpAKZafP0dqOoWets8dyYQCSwsEFbsIC'
        b'cIjY7M0HG2EDVhqAzlDSYDxrtinYz2eIFfaXg83YTE5CWHlJvSzBfg7sgMfAbmN4hdEdHAbNQSgXmTDwbBHoQ5mlc1KWgbNMrNCudaHo4l2Yx7ouDQfnhbvAriDsgoMm'
        b'D8x9Pg2c1odXQTPYHWpPauUXhykpdfbCLEfYDg6Ai2sZo8AmcBZu1gbdHJ88KOwmOIp6EDFYrIEdQvRUqEYA3xKeWozvikR/VNwNUAs7REb/xpYPc1IJh7kKE2MMu6Fr'
        b'+VDzr1hm/9c/dS6LErgyeoUE1l0HT5XXVLXDNNphmoo/TWPn0rwBp8QyKTFqh0m0wyQVf5LGzr555f4NTRsUlWo7f9rOX8ZlLMKiW6OVXGWR2nEs7ThWZsDkW9+0XpHP'
        b'uFmj3QYqTcO33S9pkii4ar4XzfdS8b009s5yvnyxkqO296dxWD6WzWRWL1sjcGg3aDVQuYX2zj43T+02SS2IpQWxKkFsPwfnYPIxx/vk+IAafv5RR+Iv/oike/aObXbt'
        b'Lq0uSgO1fQhtH9JP8QZaYVxfuHpQU9wbWfNJuOYuwvai1qKW4rbi9rLWMrVLEO0SdMcl8rZLpNolmnaJ7ptBu8TIOfg5JrGYq5jjfXJ8QA0//6ij9jlGS7qHXuAaRd5t'
        b'O5HKTkRs82LULpNol0kqwSSNsxsxuHMTEYsroQ+xinP3VngqqmifGJVPzs1pzyTfiZ93O36ean62Oj6Hjs9Ru+fS7rnY/E6GfqSYbhy4uMQZcKABN85EH5qz0PEZk5gp'
        b'dpxn7bhTHPWfdWGho5Y1bpDZEZYNH8P2iGGN01kbPUbvdjRGV22ndF7x0jksFssNq4v+3uGJGRrhFf2AYQh12izm79gZaa0L9P4UlB7eCAPYdLTxEJOjMJ0UOlLsHCRi'
        b'/sc2SBUn/8Qu6lF1jTEebNRSYckb5rg2lKeOw6DktVwt+Pe/wckfC/z7/w4nR5ubimvsYc35CEhbvlHIJsjgjhemEUi7fb8O1Ka869gfibJFLMZAe8uyeYNWsYTYiQ8X'
        b'saVQ9ihU23vY65fmlSwiFHJ/Am7PzPqPwO3HvGWc8WCMOy7r/xDjHuKrTvCrWtb/1Fd9BDXGaB2dm1o1EXcEeR6lE6GQ+HJOK0Zhj7e6ZL8kf3Asg3F+wyfSkrEzAjgO'
        b'6ozHg6PgTPFX70XqSWNQOQdO8Rh86lJCz54QjFH9QyL/IDTXaRv/uYKdJibH7XN+957qvS1V4ZKhTj2yyrvPDJMl2FI+84z1q0+KOA+wL50J3L7sTwU60MkjMh3YDerg'
        b'ORKAHGw3nz3CgwR2getaxkagKCe8jqwAWDe4y+MOXwDkTJ+Hm8f/Cbr7cNV6/nG75ABOP0E7CuagUSDApBo2ySxFJo3D9OI/iQ19ktpFQrtIVAKJxtvvT6B8/T+H8h/h'
        b'1/x3qpxiPMTjeXbWX+P6Txbcx74dIjaz9T2YD/ZQCQTgZ9D9JYvIbl8yD72vdnCBIPwMvI9+dhdPjvHUk45BGRb8xCFGGwy+P4Duf5udmJcadyWH/b1gEMJfSFF33A3p'
        b'1uNaRs2/gAAfNust3KyCRzUrefcZlA7un5TFMsD4/igHPgdD+396MKDcvEZH/fUe3RH+Vn0n4xdfru2rsVl/agLwZO0AMAEoWm4wIjdkOtXxa9RQjDmA1pOZV8uq1Udr'
        b'sJ5uQh2uYPyvmA39emSEUmxaQaUwZ0DqGqw4frQ6cVlFQSGjuhthOz6Kxq+ioLKqolQaKYwVRhL/78hs7fvLFpblLinIG8X67S9tDfRSq7ANTKS+F1EnYDgnBNzInD47'
        b'YNZs7O48wtcZ1IQbLoFN4FwVhkktYHeAZIhWDx6sGK7CmmmsDxtWwevFKqcOjrQUXTZlDRqSkcSO6tKew3sC0ALxbfy+kJDgnsJN95fYR861rDAW2PfWOGwrmHT/jfJL'
        b'uR1Ws7aUGOX5SGwcOa2t3lMVryR/HrnUfqngrDwnWnF8TnbJlsVj5ZnPLAIN+frWl78Ys5OwM1W/ans3eauIx2hr6uC1VGNw5qHCBpyEjfMZhUuDE46LiZUiC40eOi9O'
        b'gR1EUbQc1M2H192Gei8ynov1jN8k7FkNTkhg73StOzUrxAc0M+E7LsEjFhKdzoIynrciiw1PWsQQBQLctwzsGLJegYayQQTDRfp/h/ljEGmhMaau0HaraodhA31QGpma'
        b'VmmHeiVeljxlaxXxSs8ekdounLYLxyRqIzb8LEsJs3GefDND7ZWodkiiHZJU/CSNg5vcR+HZEtAWINPXWDs0Ryk8u/xp99Db1qEq61BCYDxB7TCRdpio4k/U2LkM8WEx'
        b'YFY0Asf/uQ2CwcNlTTuh5WIjhD95zgw8pa3VrWUFWX/Ha+WJTW+rHykmVlPMjkJLaURpbYb/NyIiNnI6P+qMVjnSVryscIBc4b8/wcUy93zMCe4R5pvd5fVsKda3312r'
        b'YajCi1mcsaoX+nY2bswZ47Fz0UvToUzvM7T8XwiIp6h3H/DWWKhEbGZnpJgANxKiOLhbB3c7wB3R8CC3OsSe6CVtYAc8iwkL0BDeCxp0lAVwj+/oBp46CzxX9iM6rbat'
        b'yeB01w7OjHksytH1joPfbQc/ZbjaIZh2CEaDzM6leb3KwmuIFPCoYcQwgT/cUv3V/fPxoFmmGzRT5v3poHlio2Qcfgo2w9ujL81ZUbAoR5o6BHXUgU7YpocRBwjqyIgD'
        b'BrVsNIB4/2PMMXc0zHFgDGFIN18bk/6xRlCsDn4uqMzBPi05jL37srIVSL4orChbNlDukxp+zDXa5o7E0CQBnv0xHrmsSlqJ8UhmOpBWFpcyTkBYATUqoMgopYb4TGDc'
        b'GRU+GpipG/m4rhU5K5nmQs/8b2CPRqlVWOpHIshuoU6m+ROBZhroYmSag1BGzIhFGeCoOIkNr4JaipVAwb1rFxCC0K7MdoZbnUtxW1hX/Co/uk6gvXWWhNeDZzIpu8TO'
        b'ZyyVwVjKYI1aeJZEnMZeAg5RrJkUbBXCY8XH3ynlSF9CaTPyhHunh5iBYJPoqJS3dzQ0tNgFB/ebHUna2SIQ+M6csdffYFs0dbrwy9tpTe7nM4/5a17MXvRt6vWLv9Z8'
        b'EOqzYPVzc5w5E3bv2fpS0cvWVgWqreticn781bsoY8+euf88AT58bfOms6Eqp9++yXlBZidqD7y6vtV/qYnzD4b737CNoufClTM63CbbXODCiZLuJR1n53z0zObLNlNX'
        b'teTf+sVWfO57v5Zk1Zur7hdez3k6vCT+tyvP2dyBsjpx5VMve6ZFlvck/BKx1+PFz+yMrMY+OJEtMmC4I2rHzUTC1bxUnXiFpC0GaMM7tKvDQCe4DVxdB2uXMJCWzNZ2'
        b'iHgFj6LtHhGxUsF1Rn67vhBuEiNZ8zS8xoBT4CDolhL5zQvsAVfFfgP8BYZRbNheANph13IiZdlBGdg4CKEi+BSs82UgKtAAlAQNKvTYoMXkTq7Xca9NAgeZ21+EMgcM'
        b'qeEVAJxIIpjaDJf/BN8RDmaZ1tdyjVXbjjIfo/NkLdjEYtaCinn/qaBmYy/LkHsquGobL9rGC2f0UlppHJ3bI1ojMOWxLL6fg86RBHK4jw8PqCHnRjsw0MXINB7l4t4+'
        b'r3We0r43Vu08lnYe22gk48ryMUXvUNDJzmH/qqZVCq5ihmKmYmaXgdpORNuJCJmvPL9xDfrD2qGfYlv6MABTEbpUB9P46PAlBb/FrM1MbobBGB+SRA4YifF5QA05N9pB'
        b'i8AMP33PzlFmTDCSp41tYv05T/tzY4P1nw5joSO0sY2L4MAIblyUPpzIQkdmPTYctB4v5v2lbGtIDYJHmHW6Egu3j+gXZXiN3kTpwJF58/42OPLEFu5MiriYECCIrN6G'
        b'OpdjxibWj4ep+EpySosypubpD5rJrQZm8i68oJswC/p2znbudr3tPLSwY0s2TPRpQqzZzGst0FJvWWuFFnrrWm4tVcup5RdakQVfHy34xsMWfAOy4OuPWPANRizq+usN'
        b'tAv+qGmDJeYP1nNHWfBj8/OxU3NpwcqhXgHYwoax5mGMj/LKKioKpOVlpfnFpUV/QlOGluHInMrKishsnXYmmyylWLAoE2ZnZ1RUFWRn+2vdqVcUVBCDZWKsNqKwnEca'
        b'pwnzckrxAl9Rho2cB/wdK3MqUC8T5uaULn20lDHEBmnYXmFUC6RHyh5/Jq/ghsAmUtLygjzyhP5MK48qfTx0wS+tWpZbUPHY9lS67spU46HD/MrFxXmLh4hB5IlKc5YV'
        b'jFqDMsb3d6AdFpeV5KMhO0ioGuYZvCynYukwg0LdS5MKGQ6AQGEadoJcWSxlaoAkw8Vl+cLIwqrSPNQ9UJ6BzW72qAUN1D4vp6QEvePcgsIyrYymoxVkOkEVdlLG1oA5'
        b'o5YzuA89siV17kSRwuEO/w+dNgfu+yjnTW1ZuaG5I0sZTBvwF9fj+QYJtOlpwrFh4wNCyPcqNIeiQZhfMPCqBspCXZ/pJaP7ksYXFOZUlVRKB4aIrqxR37iPVEi+YqvN'
        b'EZUbIvVqeyZ+lHK09UV/PYbMPkQYth5FGPZJZdjeOhbAk9LQCkwBeA50lSFhRgo3Eso8uAMoQavxiuUsigU2AgWspWAb6ADt2uhJsNOxXJwKd7EoNjg+BuxixcXDs0TC'
        b'BqdB/Ux04QxGoPYNDPCFtUF+iSlItj6WUQ7PVM7CNnJsCjT7GcIzCePAVri3CrtRuhQ7DDHqI1tnoGANMurLW2gAOhLBdoYP2dJk5l4qmKKmZ5d42i2mqjDzNjgFt8Et'
        b'WJ7U2eUxbkf+ooAkPWoCPM8T82BririKkU3jYKMYNs+ATTwkjlDgKXjYiRTOWqc/dQxbgGmSk83TuQzZ8h0vbuRRtgWO1ZT8lFMIc3LMTI6DHZuonpJ3+wUzIj48Zwdr'
        b'4CEcw4lylRhHw50kDgm5YMdsw8XWbCFezk0qgydRVTheGTy6MppwPaYnEGQrEVV+pxjvSnQPkgCPZ8NdCf5JyYGJAWjJhPUik+XwImhh2v0Q6DMYsbPZiVp3kygpJRl0'
        b'ZyToTMfARnjJEBySjpsqMmDoJJVgZ9FgiyfQHAMOgM1gF2mmifAC7NZyJIITKxaygtjgMsO7eGgO6H3IkciC9StBZwjYzZTavgT2SQaRgwk8CEniGR/S/XK8QMNDokLW'
        b'KgG4PB+cIESFPkjO7xUPIgbDNIXgBNiSK2UTeKfan/AUEpZCeBV2Y6ZCM7ilyof0XdgKN2q5CjfBxpF8hXqFJuCIyJg8G2cOR8exyYItPHAcnFrOsCUqwVbQqvNaowzm'
        b'gTPYaQ3sA90kA9gFGjMeeqUtBFdZjFdaDNozEka6G0AB+rQkm7uhAp6i4EV4YiJD1FiDkuu0RJtwVxw2QdwP9zF83FcX5koGqOFQPTYTnk14BJwkTJtzUB+/Sriph/Bs'
        b'WudPdoCHSAELwAHRQ3c47AvnD0/NAZe0FQuCWyN17naUgfdE7G0HromY5+6Cx6slgUMZHFeCUwvAqblM7faAo7MYzRbWas0KZfRal8Fp8l5DYBNUpEMZFvsMIPb1K00F'
        b'fYQW83trvcIiDhlAJlkVqynyBqbGV2LD3DQu6lztCSYUBlpTRUbkScHl5e5Ss4oqeHqGvwk8bQ52wIuVqJWXcBKNWVVY4IabUsB+nMXODp4eyCKF56qwQu4IBx4MBT2E'
        b'wFICmjlMUUyulZXLDStMZ4ImMx7ly+HCTeMjyS0drSvRVAbPSZdbbzBZDhrMK6o4lLUTJwIcRv0aT1S2+vCEdHmVESnGHJ6Hx0wN0fbzXBXOPnDzmIU8vaSIKiGu4lZY'
        b'P4O5AJ5ePaiC1gWcWFDjSwg/BVIHXZkrK8F1Fq4dqpoLOMn1zg8lBYHDsJ2nLeggfIppjQp4DtVvCicyrJDU31gEd0njwDldYWjK5VEWPDY8GRVAcsDtUJ5lDC9UonqY'
        b'GJpWhJfrUabr2RgfhbtJZeD1KaAjPQU2psMGuDcdNOAIbK2sKnAaXqgC5xjo9Ro8tSZ9+nSc/exsuJnKSQkkhtMh8GzAoNKrpdrS4ZZi8r4DQA04KoUXzCv0UMc/wsrO'
        b'8ksqqgrHMwJohJthPZr7JEEpyWmZeKGYCWvDXIhqxh/PgzsTk+EOvNXelGkohT3gGilyFprmLkjg6RIcKp0VScHmQHiAPOv4MFAHzyagyUASgAZLaqITl7IEbRw0iDur'
        b'yHQ8J92hPI+zGIf7m/+csXamd+CKq19nK/FJ9yxHc+ozZjH9JUb7h+8kEZe0AhpEl8FlgHcEq9H66b3aGtYwzbMVHpwPjqPNQDUFN8Jj1fBwNrM03MibJdbHluZg8/RV'
        b'8BQ8TvRLaNaqQa+1Hv1ZTC2Cm4rFgWSfWBybuo8lteNQ1FeG3SdmScpen2TxXpXT86c8q36tnfeZeuzhaD8zIctqssF9uz7Vby7CvcdePJGV8ZZVxoe9E4SBtXH15/Sb'
        b'Jb962B+tvPbVzjrzcUm5u2/849PTZ8N+O/TDnv6n5e8uuL/UZWf32uqn72yJlUmm3E8tCa6Ob1mefoCq9huz64pPw/ztLcfevDTlFvepIzMrYj9A08Q7raXrzKJ+Dw02'
        b'WPRZ3D9Nz5qVrrvzo6P0V/XKX//hFewf+3tV3dkfDZ5qbPaMnzPHzLv/4Is+amXNabu8ma1T9k7/tOczg1d+pqlnvNde+WNyyM9rU72dXl6f+7ly54+ZP6Vtqf+g5ehH'
        b'xdseTO8KWku7v2Fvcd37yNGiHVbvWQc0t9f+lPvPzsyxv33+VdoLHRHuabdOry5ce+ybPWFJL0xMYN31r2+41PPjG77z9r9UO613hTj69if657++OP38N7lvbPrUb7ci'
        b'd7/nlU/Lsj669vtBg+nmSyOXvqsuCbxvcPfAS52bT9scu8P9btv90twdnzy7+PQZAWfd1v6J3016+fjKM/dbdz7bA2aY6h13XTzr8sqVrc2dty32njx02zTDoeO2i983'
        b'kvaoO2MrX3k3/XyQ/o7ZGz+UKFZZ+K7gPJuleCf7pTsLs573SA149+K4m5/Mbv5HXdWUDW/MNP5ydVzcC/9a9Plq0+hTN883hWuWXH8n9L3kpqpe+zXTXyw+Prcl5C1p'
        b'8k8B6Yk/zj3sfDK4LHu2r/2EM0ZLPb6T/ONr9qIXWmHp3LyUN6+tSNf/KcfVb0PN/dPTP9v8eU7Tq+4rNM+9/+554zXv7N0zMWmCy3OvrfbdJrhycqX99/0fN1jV7//s'
        b'l2bby2m7t8/5efzaY1NNot6YEfX1hn6Q/c+Xbv8c/fJ36TH3j7/8Kx2R8OHui12vRbkmfvj7kfd9g/tyHfMS1o7NjnuzbdKzqQVvHMnST7m5Ozh6t6bww10ruxpeKfn0'
        b'bMCFdWGtN1sK/V4bE5y+YLn5+bfyF77V01r8zYf7LD9ex6/7yST+N9aXC67V0p++E5dxNPj92/uO/GDwRvEXkc+XHfy68vRsPeOiLdcsx69u91iREO27KusVv2s1rz/b'
        b'sXpq6WsOsr3PZ7pz56mjPlz7Cye2zn23Pl8USCx3JsNt4Lh4sOEOvAT28CirRA5QLAabGV1kq8cYrRyzFjQhOQa0w8ME0RmLJp7LkgFjojSUJxPlsoTbOWAnaFtEtJGT'
        b'0OJ9w7hk5Ui8F2yCnURXONWfJxkQVq3BOeIXgISwbnKPILgPbB9izw7PbWBM2sHuLGcGMW5JAVt1dvaeQnAQ9GQyTgdHQ5xJUD50Zc2ApT2sAXsZk/PLc1eJgQx2DVNn'
        b'MrpMtFq0kEI4PnEkPAWq00YkKmvDU8CNPgxn7bWJ4Lw4NQU28ChuOGs9PA66LeAu8mQp8Cm4iSg64T6nAecB0Gj2QCs/tlUPcVyYB7rRTqDPh1y7AbaDnSTa4Bp3Jt4g'
        b'2wM18z4GCb8BuuAOiRicRJXaJ5TwKN5qtmcx7GGs7c+uAoeHRF+Ee2EL6GCvR9Is0+bwPLgC5A/x+7lwPyqrbh5T+sVYoBzkNJEAjvDZoGOmG+P9L18OT2Ju8CB9is3j'
        b'gE5WJjjs+gDPx/NDJjOwHpfLCo0F7aAmkLxE0A03psB6fySXosvgjhR/UFeKJJIgDqrYoUIC/fFACzgyCNwXLzfG4D64DnoIaTC8DGtXaiU/sNkaSX4Ls8mjrK1Gwtdg'
        b'MbymEByAp72Zt1NfZjVI1OaB86AzE2xkXsB1cN5xsKi9dA4Wtb3hZiZ5CxI+ewcJ26AV9ZzL4KotQ9N8Cd6IGCFu34BNubA5VhtMEm3/jjwUuU/DLixy2858gGWwCvTi'
        b'exmBe+n80cRtKLMixQTBK564EMasAd0H1nCyx5fNzSQPyEKLoQwHgAxKW+OJ47asZ/uBowYPcPjnLFskVTJimUl6KhbLlsPzprCXFQo2sfxhp55hMGwnbTjJe6lE+2Yw'
        b'K/72BNjKBjvGTCJEEgF2XIm/LxIHlq+XgLqgRHDCl0U5TuWCg4K5TH/ZDk5NJzFCx6CBQ+nDfZGwg23gYPAAq1zXg5b8gTX9SmZ1rhHpo/pIcqrTEg3joZcIL/kh4c6D'
        b'g/r4ZXsmXvTuLChjsixLCUyBO9CuAd0YyrmgDZ4B9UymGtBRjXajsA1nTPNHAgt6J2zKbgw3BslsLcSSccNqcJIUBDrh/qDUgASwEw86CR4bXrBdLzvRgzzparBNSKLY'
        b'7GDeQ/gsY9DAhh1ABrYzr/QsuOxJwJc6eAHU+qP2TmU7wc3zmXEnHwOODfYlIn5E6E4HZsDdcQx800QCpp01XzFA3L3TzBB2ox0iuGRMXkWREI2W+qAAkS/uNAvAriI2'
        b'2kJdzRe5PRk25P/yQYqdkIbpVmpG/NMa1uTk5z/SsGZQGsFrvHkMXrN+Po6v0zwRwxZzWIoizPWB/9I4CgkHc0RPVF9634KbmaoJ6bcK5DFqx0zaMRMjDnMY/uWEWxEv'
        b'R6lFs9Qus2mX2SrBbJ0fTwyBdwYZ1Vg7qax9lenK9F777oU9C/tybgfEqAKYbNqIlyr+eI21XWO0xt5NLlB4dgX2eqrtI2j7iH5K3yawL1Tj6ta+snVly+q21e0bWjeo'
        b'XYNp1+A7rlG3XaPUrhNo1wlyrsbNU2GtyFC6dc3ucOpykvM07l4KD0WeIk/pqVze49NR0lXSO0PtPZZhd77jPuG2+4S+QrX7FNp9ipwrn9Gij4EaHP+T1WLUZiQ30uE2'
        b'R+077ZXhHa5drmpBCC0IUQlCtGlDM1rhjB2OXY5qQQBDbdxvjqpPnoEc7uPDA2rIudEOBOsZJc2CcnLBeJgiXMlSuik5XePVjgG0Y4As/p61nTxKHqWoVDv6047+t0ns'
        b'IdLC09QOCbRDgoqfoLHzGAHQWds0R+yf2DRR4am29qGtff4EoLN12V/SVNJY2lwq49xzEmpcfFQuk5VxpxKOJXQn9STd8Z9023+S2n8y7T9Z5ZJ0M1/j5qdxdNE4urZF'
        b'045ijat7+7rWdS0b2jZohB5HTTtNO8y7zDVCT42Lxz2hZ5cJLQzRuHq0raVdgzQD3z18uqJpjwjdd0/frmTac7zG3RvbcI3RiAJ6nGhRXL+loZttP4UPtpSbb5eJxtW7'
        b'bY1G6IP+8vDrimH+8hTTnuEad1FXoEYUTIsmoqtc8VXoIHIRWPVT6CDj9k+k3LzI3WSmqEs2R9PWhO5mHksTHH7OhA5OUpHPrZRbKSrPLFkKqiR6HdweE9o3Wu0xgfaY'
        b'oLIQasLHnUumwxNUzCcpSzVvAZ20UIU+PotQusJKbeGpcfNS8NHQK1O7jaXdxsrMNKHjzwX1op+bE1UzM+i4TBX6eM2Smckr1Bbu95jWCNN4hWp8/U8ZHjNUhU5W+8bR'
        b'vnGoDhr/MNo/VuU/4+bsZ+bjp47WePsdLe4s7jVTe8fQ3jHMOfT4YpX72F4bjZtHv42xLXpsdJCx+wUUH5t/4ykgbOzF6DPRN43UYRI6TKIin1tzb81Vec+WTZataUzT'
        b'2DrI8hsLmwtlHI2dg2ydvEplF6jk4e5khzqqpSem1o5sjWyJbovGcWQd3/AI782gPSJVdvhD5o+pt/hqUYraJZV2SVUJUvs5lCCqn0c5ebRFK9lKSyUb9Zk7jiG3HUPU'
        b'jmG0Y9go5aDuIufetfNV8ml0+0ot4kziqzaubV6Lv7jLKpvXqOx80Ucxk/mNTgsc281bzZVc5dK+0L4KtWAyLZgs09NYWO83ajKShytCldY9Nr1W3Q690r58mZHaIo62'
        b'iFNZxOEcpk2m8gJFbNtitYUPzRDLoLPmTeYKrtrCi7bwUll44TNmTWbyStybg9UWIbRFiMoiBJ2+Y+F228INDTbdxbaC5qL9ZU1liny1rZi2FeMmxaD5uqZ1inQGaO6n'
        b'9Czd+9lcG3c80Ri3Givi1AJfWuCrIp9f7jq6o8nbZtABTZdtK/FwU6Yz/PHozdq7a5zc+jnoN/nSz0H58DyDthp85rmZCGq49xJMGcs+wDJuzFQrznNW3Km2+s/Zs9Dx'
        b'TTObWZ7Um55es004d4xZ6MiAyjYMqKyDWiuqMLKsA1krVvwl0PzYiyPerWQz/4Yuiww4fWw0y8tBC+EODFBrKAag1oLUM+azWCzimfl/eHxi7oDoAaljhrEU9TRlFmvG'
        b'EXHeNhiw9XrILZXHpR7+02E1CnTYazEAdxMLNn0t2G2sBbvZBO7GYDdFSFI4tTaF1gTq5rKpumEw9To9w1Gs1dAZvRFwNne9nhbqHjVtiG1bOnsUqDuzXOttOBTpJphv'
        b'jhaz1Bm9PRo/HsgxlFijUgu/DirCX4vC5uWUjgrN5WKUXVi8jKBxFX+Cqf87cDMG8Ee9q99A9fyEhDyDIIMD9WBwXqZKGLRHVS9lsNXRoV5hXFl+Qdh4YW5OBcEmmQeu'
        b'KCivKJAWkLL/njEfaUAtMj+cBH40SB0VPzqDrhawHYCrMUL8V4jm38UvDaiR+KVrahU2BgVtYA+4jjY5aYE4akuDeMZQe75944f6KOwSGcJTYKu4KgRdnM/BXAmD0DWM'
        b'msHatPRBeOGacXpUNTxqCBoqQB1RNE8xAYfFSWwKNoALxAoQ1oMjRGN8wceI4lMGTmYW2cmpXE9KimdBddln6aZZh8uXcyj2LBYVY1k1BZ0tBifMxECJlTS1cHc6xvhS'
        b'YO2EZLKPmz3Cp26o4puTaQqPgC1ZJKKYR1E5PMuiiqKoFCqlAm5mCCKXZ/1KWbDnmJgGZxdo5gdXMjprTcukDAbF1JtHvUuVp7Oza5b0rXHxY5Kndk4iqT02S1k0W2jP'
        b'E2avaV29hoEzQYczqAnjUjxQQ4VSoXGgtSoenXYDN4j6RIfZwtqAObArKQXumZFAlBGJWhg4ATe1ZEZCkn8So2GAF+Fu0yRYa0wU//n2oP5xrDJBTTi4vMFwCbwMWkUs'
        b'BhO5BPvghYGg3f4z4wbF7AZKeJ7A2fnWsIsB8hxguy5aXjg8R7oCPLXceiRyqkVNfXX4H9gIrqdxDNdlhJGGmh3LobjU56YmVHZy78L5Wohg0hKmGQvtZ1HnKF+W/qSa'
        b'anlBW0ZFM/aFxykiPaLvzwBb52DYADbrU6vRbr0bbmJwg80rqrGKAdaBI1Q16n7HwbYq3JfABbDPSqxPgXMLMEuNhw95M8Z2aRgzgOcqqWLUsa6CS0zsunO28ViTMicZ'
        b'BxrkUdyxLHCqiiL43joveGkwvAdOgvMkSBvcNp+01kTwFFZDSeaCbQPKJtCJnr62+JnzR7hSOzTr75qtaWi+VvpOsMXziTPOXC+RnH5lXGpnYKyrIu7i9SlHKWdzZyvh'
        b'Zr5wa2zgFLvqoMsVtz+8mnhx4ozdm5a1fH/4PBd6f/evG1Eu3/0u/Vd9yyecd2L2hX0YUlD/2zubT7RMmHbNpk90x+O5te3fvZvREJ4u9s2tb/8m53z3U/tYYcbpLSuX'
        b'1ezLLuuWvnsjdO9r72VEfZd7r2HN2GgflyWvvfj16UNvbF35XvaqmS9/ertZ+HvJxNBX+Genvegx9fMwYfXXla0c6am0D78W3chznWN9PXgq9/1nJqz5oO3uR4FFOyI2'
        b'vNwlespn2tfqF1KSS5ILQq7Odlbe9M6/fr/7s7jLi9Y9nXxe5eYZOZN9e8Ebnm8WnJx8q3nOZztPHMrZrXB/g12RsTX4pwy2t9/aOK/snUlHd3zpVdg2w17cAU49HbzU'
        b'48DPtxZ1b3z2YLbHjwkNS+qeaet5+sHXS2zi59/Y/uKeqKYVyad5B786Js3puvRt0Zvf2Tj/seGpzN9fWz114pjXBKuP5N5aVLT+mW9/sj54jPvpcc7hn1qMW+t+qKYv'
        b'lR18uzHmUtnC91vmRR3mH3km3fQIL+z6jNNJqUe+iMh6br3JKzYX9abwvnjP9o+AC51FNw+/mrFtgsOlhdKDx6R7YcWdZ+3nXxqT1Xbtq/wHn13oclfenDIpy+z4na9s'
        b'vzrn/GPj9KrYYzNvtB78bGdPg2f0Z55hGw/8y+yDC3+kWNiGb+xv7iqKfhD+fZhkw+96etMu1rU5iGyJEtsFdIwXJ4Czxg9dqkqCGUXkWTMrRhtbDWVaFhtsVgL7iErJ'
        b'e1oUMfeF20H9MI+qK+aMfu7cdGyxoaNrBccXsN1BLbhOFKuxAnhdkgiO87SKW9BulcHw19TDjZPESeGwMWXASDgMXYM156utgGzU4HJ+YC8XnrKC55kb7wSXQSOajcDh'
        b'lAQMM3ITWOCsG7hGtG1VUrAbHgY7JMR4QxLghyOVHeCwwSZ4iDSJJ28umoCixoGeJFSzfBa4ag2vkIL91uSKkwLgLrA5kCQaGrPBHtgIzzK3fQoliVGV0POCTvxYhs5s'
        b'IPM0JhrTtcbwpDjAVxvkGlyB9ewAeNKXUc91QTlnkKK6ehxWiBI9dXYVqXQ+PLiaBLFUJmsNsFnwuvlYznzYt4wQ8Mz1BJ3i1ADPfOLngqZutECJeZQjOMAFWCHcxJhA'
        b'b9Hzx9enJKfpUTynSS5sLuwAu4gmfMJ8Z51iNA9eJXMzUYxarGFgi62gF9SgLBj0R9mGqUZNwQHGDrzNcB4pBx6El4YqRimgIHrRaC5sJ1moxaNpRYEc1jBqz23W8ARR'
        b'SoJa2EAUk1grWRYtcv2/1zg+ereFoYfBMtJIPeRAbO/BFn/VjsN9eQclElXkl9rgcCXZLErgoLUTX6y2C6LtcKA3y+mMGiru5mK1V6raIY12IIGn7Jyx03GYxtmtPas1'
        b'q2V+23zZVNlUjY2rLEvBU3LUNv60Dba8xln85AuUY9XOobRzKMpCyIkL0S2sg2hrcguxxtkDm4C3LGhbgDPYy+Pbk1qTWpLbkm9b+6qsfUkNJqkdYmmHWBU/ljFS91XE'
        b'q21EtI0IFxGqnKk1UleEtES2RSrtbjsGy+KwrfogWnRsqx764FGk6Q8PWlv1Eazqdg79lAOqrqMQq2DTGb/8GWqXmbTLTJVgpsbBtd2v1U8xR+0QSDsEyjDlrKNLu7hV'
        b'rMhTO/jRDn6yOI2nT1dCY4psinzsPWd39LR2TvLKprWytYzidJayqreqe53aa4LabSLtNlHO0wg95XoaNy/0l52zgtu0TrZOI/RQcBRTlJm9s7oXqj2j1cIJtHDCQC5t'
        b'VlzD8RoXt/YlrUuUXr08pYvaZRztMk7OuYdD83FsQjW+oUqj3rBu8x7zFlM5V16kcSRKiVCNu9dRv04/ZXpHUFeQPO6eg/OwZ7BzxO2RwvQMidohmXZIVvGTh2l9Rqo5'
        b'/4YfgotYvkwZ3xevcolVu8TSLrGNxjKurEBjbSc3wPryR17o5nPHLeS2W4jaLYx2C0PXzGk001jb9lMWll4avsP+tKY0RYIyX80Po/lhKn6Yhu8mS1F4KrlqfgDND1CR'
        b'zz0HF7lni3ebN3pYvh25JlaxXOmm5vvTfH8V318jcJLFagT28qktRopMtcAPfbMTyMOaVspWapyEcpbGyVmh15Ko5KmdAtE3VEhiU6I8TzFD6aZc3hvbN1mWqObH0PwY'
        b'FT8Gp6Y0pSi81Hxfmu+r4vsO3DRezRfRfJGKL8JnUptSFeFKI9ojrHcq7RGl5kfT/GgVPxql3eF73eZ7oXbli2m+WMUX4/xJTUnySkzvzfdU8T0ZdRIR5oMc4mw40IYb'
        b'Z68PnVjoyOiObBndESaNfaifeDLKolGnNFzySO3RQw3SLaxB+rMJzMgElfIMpVUhYf1RNovFwoTn/8PDE/OS2IJmYtH/a+874Krarrzv5V46l14FaYr0rihSBFF6UYqA'
        b'onQEpUlRRFQU6UWK0nuT3nuR99ZKm5lkgi8m4ZF5qZN5eV8yE0yc5E3KzLf2QX0+80omX2aS7/uGe3+bc8/ZZ5+9117rv9baZ++1BbuUt2B9YCnxxvAQ246Pc4XrKXko'
        b'/drwkKBMskzsxd7tu0NEPDZIlCT3akDozR3c/2sGhNw/abHjywGhjzZwf7V2kVvy+GdeL7x7z8vA7Lv3fcJeYFb6HrvT2rmqfMp0fW55MRs1oqw+IUFHHGxs2ShNWmwO'
        b'm5SdnZOVkn7xU6uwGxH+oynqb+5StHv9T4jOIBXIOc3hsBz4mtsKI9jw2fEZ4E6gJ+cd6mRhy+uzQ91P7hNEaBzZndzZioWq3NxQKL9s/WoXdj9o33W3O8hYf/Tm3NMR'
        b'N7bNOxmtjSn2qjb8bMYk/5rVXx1oK3/XTbHd6VeKQm29uILCjR3Z8MiIbgcJGdHXtrS/M5r8Yf+okvS9E4ffjUu6evGfOo/FuH/53rvy7x1UT04rNbP55/kYG1ujPT/+'
        b'zuTVCN3zk/n4jzrxOdmHWnXuHzP3ePare4a/Mqm+7/C3//ztB3ED37aX0cCrJwd/126XsyxtdCIkQPu9hZ//3qd7/cjZk7/wPF37vY3bv1ltui7dd/WrfifxXyR0z/X/'
        b'q8rgB+aN678xFd+dSFKIw86780hgHcd3HRdn7OQsWQVsIBu10iLw/KHXVivehBks3TW3x2AujDkvUTj4xuwgax5nxCpCEXTqXf3Y3JEXBrkIp3et/UpchkJsguqXk1K4'
        b'KSmLCn/m/YP/0GyUz+Wk9JXhuPcN3P34Zc50/AVv13Q8nvB/uupQY3/tze7QJxpmTzXM2Psr7ebcTZX99N0yNq890bznya4GU+OMTuctDYPa/G6TIY8nGjZPNWyYpeO0'
        b'tc+m22VK88m+o0/3HW2W2jK2/rax4zvGjk+MnZ4aO70og0zLTRWjLSNWpmZd4NY+80fOvc49rv2u397n9A5pVO7FIdkMZ58o6m8p7q0VcVslK5o+5aL1735fW1Gv8NoK'
        b'vleI/ScqTC4S2hvacFcNPmFq8LO74zpThD2vKcKM+D+zIvyzabl/Y4Tjb0vmp2SyUfi/yg3ASJP9ZvgPl/BlxSenXH0Rl/3Flo0fiwT/CQrMY3eAPPU6N6KekpaZmsje'
        b'CSQmGHyqsntBmDfjidPpT3lt8bnqQhiYy+LgGiTD8O5EOm6IMx1GXxvl/GhtSJyGVMpxXE9574MvCrKP032bmj9lgbJ6Gq4/ZWEC1W3sYvgd/n9X+MPRH2SdPG40JvWu'
        b'6pcCB80cJCRCDwVUGf1M6tDfFeYdEhyvsd/L+1awbL/yuKmQGwJxEBS8FmTn7lWYMITi3Tg7FdiMla/N0sPli2xc6KpoN9rGCtzH/jfC7GBlIMNWCSh6zkIOYT0UG+Ms'
        b'g9VprLLEMh+s9tNiLwV8Aq68uMcPRiVhShPrPnuDtW3F2N2ufile2a+2Onv1HvONDBweur7AQ7dEPk9V/cWMDuOPNuF5AX7H3jJ+HfzeUzfdfee8qWj+hzuyvfMpiPIH'
        b'O7JtS7y2I9unVbNF7mM7smUkEEowX+4zkj/rxjtc07Km+WwQPDAw1DMw6/esrYqfsxHPR2FkWXwyLqYPF6OEWwDNvWjmfAUOKTlCmGr9ZQdrtHhv7M3zh86NHeuvN7ah'
        b'kGevxB8K3tiuR5pt18MS9d3tevZ1X9sUWT8RWT8VWe+I7RXF83d4f2zKtuax+eg+14/tzOPDdubxY/vVUPqcS7nNeV7fNodtR6PBtqPRYNvRaDiWee1IKbCdZT4z0f+M'
        b'LWe+L1JljdoU6T4R6T4V6e6IiUR6O7zPSlgr9F5l1X1BltdKkGJbEX0s+egWdkb1JSWzN0XmT0TmT0XmO2KabEebz01YQRav8h/cLSh8yH5p35beviHVKTbmJE8EouQ5'
        b'S77vdmLL2W1HUMBnBfxXpc/EXz5vR8idLRDs1ix+SDAVsqS6lLx50GtT5P1E5P1U5L0jFsTd+d+dMtr58D+qQNSLSu4bUhkKnTLZNHF668SmyOeJyOepyGdHTF1EsPmn'
        b'J+xpvvxXJbnuPitkU2TwRGTwVGSwIyYjsmBbIr2ZsBsN/zDDbvwWbsnZMlZewVnyvLBsH3O+cJ55Yf5BlmI8E2Pxq9gHHbm/IICy8od75DDVu2Rgm40ilOAirqoddoDC'
        b'eJyUOIplUAf1Utyg9l09EdRiMXSTG9Fw4gT0ykI9VPC18TEs4mMRtBzFOaiBmViYx+FQEZtMXoSTLs7wGKa84bEX5bqPFddhEYZhzKoA+vzJcynAdXwkiVMwQp+VQzAA'
        b'fTh48YqdEbbYkq/Tkw6deA+HcQbbClygEgbJ55vW8LriHKQOlfuw0OPmJXusxnVYTHHGkstee/Ri93ge9ROPtLthFQR9kTqW0IDzzrCMj2AWatPJA62jYha8YcExzQzv'
        b'20VjlQgHE3BKhfzJbqjHXvqsYmOMB7aesr8E1fE4LgGdsIAlGTBN7mNnCI7D1LU0Fpn1JqxiUyjUaWHv5XPYCP2H1XDCG1ZtoIraXgc1SidgMgSKjP2oAgvYegQmb+Lo'
        b'aWjh4yC04l18AO30/34yDGEr9F7TFcjCA5jDLjsL7MOF5CMyzjgPpfE6UOiVBvcSqNimAFgzjffM0PPEmhR8jG2++DAy/YQmjOe54xK5eh045SIBzadNw6jllfAQimUO'
        b'hOKsJvZgL/1aDIBSaI8gcjyEJgtcPOJq5LJfVQVnztCJ9hvG58yxBUcUVbAUa2E+NJvO1snLGJJf+YhoNw2TVKEpHjbZJzphSxS02cGaMnbJxwVAzcUcVywMxiZdqIx2'
        b'kMINWNJRgaVU2NCGkot0+1gmlmOzrQ72JhieOetijQ3ECUswmB1LTNeIraFyWlH56U43cE7n/F5oDYRerXM4SRRqwiEpaswccVQr9rphlRSUnsQVG+rIRhh1pFaOUf0W'
        b'oSiC+uC+5TFiiIo8mNHQJqPtMXVmt/wtAXux47WfemUut4rYHmescAA6gt2hhvheDtZwVq3AjTr40Uko1IV2bLaUO4gT1EXT0Ck4CYPxsftMoTZZCJX6t61h4EhufrIC'
        b'PkQ2xX2ISFuVGRMO62oR0OoGrTAN/VAUi+1m2GR+AJfIOFwUwJQ0PtDGhVjxTOwgPzzy2jFsuxmSCqPYRpRYN6FmEIvgeLqfExXRqQNteOdUBJVdHwFNh6EZSuNI9u6I'
        b'OQaQITllSXlmcAhGbp67qaIYcTvuoNdFbFe6flAJx7mFt93U1nW4e4jkqtxLz3//9QPEbfehBcdsictHiTuXsCwW61Nhjdp0ElehXBIHXLH+BnTl+rmn4LgxlppgGW4U'
        b'HLa6DSUXpENgSVOXbSeDj5SOCDNwIwZnxLA2Tz32JN6DWRmouuUNzXhHxwtqIqEQixMUoAuGgkLC7OKVD2jhsLuXjKqylY24tn0YyVCHP5aFUP8244gmlBGoFMbioAN1'
        b'5CrcxWKBCl2oD4Q6nNbH9kCsiMARmBUqEftVaEAvtYRBU3G0HSMulOEYzF3L04JqXXrkOHHVUB4xRGm+khQJxGwSPsDlAjtVaCAy3qPumSLompe6KO+LXVowgd1nz+Ao'
        b'SV4xLuqdh/UAP9iAR9L7oT6bQGEQShwTcTYNyyNg3WoPewUbFQSL2sR0o1gdDPV+vkpR13CenjdIvNB5Du6QCG1Qy+7Y4aiKcch+tSC4QzSfj8SBVKLeUBDMmOKSODTH'
        b'7YcePcPcb4qxQSvqkQ7iSBdyJIgjSfpq2JtEc5jLdcT2KCEV3Y330mOh+4osCWfToVMWMKgY4wfDrlCFC0SzNWzSJm56DBXUuhmY9IGScySzxYa47u3q6oLNvtCXoCiD'
        b'xcS1A8RXi3BvH7TqXyU2bhJzhbXrPAcrH2y4nGNOnTcLg+TrVMAKyU89CV5b3Lnz6YQgvRbYdokovsojdmKr2EegDxrxQdRJwsYNc43wnPMXoDuAatiPtThnQvJRd8zQ'
        b'Lg+rVKVh+XWuJRlpPKVF9Zi/hkWW0rdhLp2DzQfy16GFxR5193fIN4iHqcAbBeqCC15QqQF3kqhhG1TAINGnyMGVeLhZMg2q4VE0NIiol4f1RdBwBFu8oTuHhc5C1pIu'
        b'7CTF9AgKFcSwyIVwZEBNEhaP4IrmAeKHGVixw8eq17AvXe26MDmVrVcjmS3BBwpEqH5q3iCuwewp6tBeJayI3JtM7FaE027QTyRfizIm9TQRmadDHNyT5oK1MaTEmkxh'
        b'+BoJRZUVdUWvux0BXTkxJinPqIOXD2GdySUcunlcPp8qWASFxMy9MGurb5IQC7MEOYtyqtiAK1gkh2We0GkXSjwBPdepAuV43wTmoQdG4X4+9kpq7ycir2K/Z6Q1PMZ2'
        b'GU8zanAJoWQ3ae62EzDrdTGYOnIW7mZHUne2kE7sgtV8rLwKzeclE7HRJcnLitPq9/1ySOWU5BIX1lKeRmcvjQhsgrbLUCF2VRPaicGJgsTg0Hn2EtVyA7sERhm+nlie'
        b'LsK6xHDJvRdwfA80Mc6yJtHt9VSysM79BoPa4kAbhrTpnIGxhpPmuMA/qRsD3ZLYEizDh+lgQpkakplmqM2BGR6h7X41LLQl6jbr3MAJSViB/kQvE2j1gFEV0gatWpS9'
        b'Rh7bJdN0SEPfIqZpVSBxbLYzxcdhVt7QdvoGPtCBKl/dw6QLFmWINo+xUvIUDMcwWYnlZ0Yxe6gjHSdx9Xw4AQaD4DFCAjJCMhygTcXNPFgZJyOhLuYE3D0JK4rY7XX7'
        b'HBGm+/ANFagK8Y+EYSOcu73XI4aQY4T6YzSNqDIKbeeu87HR0x6WQ21uyHvgHWiDZtd4Us13qZN7NZWI2iXYL4ANJawP01DcQ7qvQhVqz/vHhpLgrtufPppKItwQAQ1W'
        b'UOSvaq2KQ6kw5kaiV3YJHhzAux58LBQ/BSsJx+GhZwrMugbCKpQdd/Q4eWsPthDvEy4O0PNKeWmkBHpxWgK6SQjK1UlYZohU97HdDtahSotktN0IVm/iwhVX4tlmUnU1'
        b'2Oh8BXvdCU8KE07nQYlXBvF/901ovKlGXDWfcB2HL2piM4FgD4FEhRNWhys5ILF7LfZ7kW1EDD2gf5jq0EFHfW6H87wUSS2e2AOzIcSFizB3/SBJ/DqOeGAVka2YlF7X'
        b'YV1mk2VBVZK+MeNErFM9xiFBL1WzEDpToDFOKf9qALbTU+ZIqpqgPoVqM0w2QZEY1OQS4au0blDz2kiDjpLizI6AHivsxH7NIFEIKYpHl9SxJxEf+lD/DuJqFHTEUBUn'
        b'XGGCZLjMEe4hE/J1bAyjIkovJF9lWgjvpGnhbCaBywwW7/c8K4NT2raep/digzC3lvhaJz6O2Joa8MqCMMclfhrWkAXhcsQcFm1g6qqssaNkFlmwzZ5nsP44NQS63al7'
        b'1+m5s1lEogUGPxGGUGKPRbaxpAQ2CHOnMpNx7IaLnK4fC2AQh12UbYLAo+m2HhSan6HuXhIeIRhshGUzh2M4ep6MtIe4nEgmZg1psRHS0fNIoFZ02xIfKBPTlh0/D92+'
        b'2BjsRsq1NtENWsLMyOroh9Wj9EDSM2RYrCmQbHdAjyIOe0ONbR7WywfoXUwjpLsjSeLReUMmGqaMjp7w13QREYeNwUN5y71CIlqHjLIjzukdkBJ44l0DomOhEXH9gJI2'
        b'6fgaKnM8CovOwwN3IFxyJTVI0EQ2Aq5EYzt2Ol0huHoIj0iR9JOpP0XdxD9leQYqjdJJTbfBWBAWncXeqKNQ4W8RQJQrgnKPS9pBXqeZFVNx/hYMxpni3XgoVLmhj02k'
        b'qurO4UIWsU7jaRaLpszSBprEiM+6/LHUnbhrgzB9/OJ5ckpqCbfLtTSJxHMx2OCEpdCVcYQFFbKDEldimn6ss41UTXJwDIqD/hhcyogiUO52UpAxsj+sqmVvSog+J4fl'
        b'KicCjUkRbhhBexiVWi8iznqcBhXBZ0hEVqKg+wAMqibgdDo9sI2a2XGBBGHgXKIaYU89jFvBpCwRswKbLkK5Hsycz7ygcQxGUinTOLQkETq0CC5RrQpDiN/n7OG+C6wb'
        b'I9u1795tVXzMS8U2czKeW2A099sMbO8Zc1YE3knnuHKduDIPRxNx6LoUWT1FKjeIgncO7CULd07HRhkbFMmUDA/O94ba23pGN3KhJFbzVLRcMGnvPvaBokME/I0EI3Sb'
        b'C7OaChRFMJZHPbuCXWeOybKZrbChEIMD2HKJvXcTx8JcfBiaCOs30ulSW9x5MmMmOMsByHJYhfUUYv/ZOE0sztLDARNii14SntHQdKwr0CdwaGfmbjJVoOzC0TRNWbqj'
        b'joCjkchRGRBJdt7IzZCb4cl5hnKBSBZrHw4YEm4/inLNk2eB0IFJbi0spWe6KsOCQg4JyZ0sFlQmItBeej9OxQXiXWgMoSwLcE8SR0SJWHbanE2tuwulmdCqQI7KPejM'
        b'w5loth7ZWs7cl9CpJUXR89J1V3KdeveSkE4S1lRqmwiJlg9tyNis1VCFB+n6eidJVMeslffishcBVzX5J3Okj1fS2Yp/rL9ihIP7yL8dwXs3odXEkvBvSZIeV4SD9l6J'
        b'9nkGUUkk5ndIHIpySRJaZaDeFmsu22ObvxEJw6yKUnYc4d8ajpzFkfMkN/0GxIPth8lgWbSHUlzKTIe+HHLCy8hZ1rBRJbxsYotyZ532UcVrk6GaLAZxHAojVVlGrNrg'
        b'ehnnw7SwWAgPcDKRnttB7NbK23fNJfNstvop6uFpQxbfqgPqEnKg3TUPKvZhuXgUVl6CFmfKOwNzZHA2YfkZ0hKVZJa0q/rLQ5fvgdtBxKJjOJEfmUpmYlOI68nDzDcb'
        b'dYQB9yyzKFgkprofANM3UlSTCIFaFIjD5yyx73SBFzZ4mhFPTGgY4h1r/0thWJMD5aYS3IRk8gbmZf18xKHoAo9vzcMK3bzdCCczMOHvh9WCBKnd0CrYlsvdkIwrBn7m'
        b'YrDowOO78cjEqE7jbtAmZPezlNgPDTz+MXa+Hbt3o23NCMjFrcRKPgya8fi+PGy7JrM7XbmYPNE6rLTgwzCuc/F1O2H9YK6ngAXh38dCujZgNclFq5scEX3ylozeOWlo'
        b'dApWiFUhtVRnRbzQS2R6yGz1A3jPxzMASi65qpsS1CzigFY+6aYe6PRRdD9H6F0L7XF4n4wVEmDscmBDLlSvujyrXA8YUWcm3k0YSIzFUlnoyYolqWmADVcoDD+NDwOp'
        b'I+k6yWLxSTrsh0c8wtfSMGWy39qsqb867M7uJ7a7s5c8gWmzSCr3Pi+InlmcSJA6Sfq3gTqaHJyUAiixIt1aFwq1B8hJmCF2OEvGS90BgptxqHckL6k4JzoAHvsRr/eT'
        b'kqgkrprRIY+piLyyMkfTAii1J+NthUBiirRBN0wZkCU8BC1HEo9cFeB9yUQFbPa+DMMOuJRlrofLF3D0rI8aDEsW5CYGZEUTgtZBvzQbNoBmHS28Q4QdJSy6Q+g4GHWW'
        b'yqoiejZGql4imV2mKtQeoqYOuuyRCZfDzvgYzu1qFWCRHXkwhUSVcSQc3bCDKgFORZoF2WFxBGFajxNOHSCpeWTPNnOtIKCtdSJj6D61pzBLI1dIiqk2m9rQD+snzpEl'
        b'2QAVZtApiWMpWOsND49hdxg5U1XktaxLqmFlTCpWGsSbemjjmBQ8jIGHWcSf66byuTgcn5WFg/SpvymiGpc7nIkgH3KcwLjOHmc8vAqUkhJg3kQEC/LY5U2Cdfcwjlv7'
        b'kGwPQwmysZ1yBfLg5+DOHmiPJhyAxmPeZwPPZYWf1SCDqIwU+bLGEXyQZW1PQDFzVUD4MABjluqwkZuMo4fJFag1U8FWDQbkpPBKbW6TlM4fImuxnI1HmQYmkUKFRWto'
        b'yyGeKoXFc1CaTjq8H0ZOkPyO+92G8Why9zqpV8d9j3IDMGsC0jJd5y6SKzUA9w9raN8yJ7tzLpB5EViXBKvYa0PJBq7rq0NjYrZFjiYZXKOuuHRBhHdEuMaHzgu3z8kn'
        b'5g6RAtMgs7L7zYEZAtEJV303has4pi6x5xr2JJBs3IkjYJ4+dQ4rfFXV3clr2YCmLCJliayq+Nlo/2ACnlr7PcQ5jTCphYO2mn4GzjB7g3yB0gjNIMt4d0nSaUunz3Aj'
        b'NDNBevSQVmhwIIKsyVAVZtIJk3pJpawns4BSC6YwCZXO5iQZg9ieTj/uXz0IraTTCNxrGaf2wbQZTNhkkKHfeRRnEs6x4AMBZzSYpYmE0gPhfDL41kim7+iQ+Ex7kYrr'
        b'FOrgI3PC3VnsUzkDQ4YEqjXQ5pblTzZ250WyPIvcGLZOw52bqWTca7uRpdCnpcAGtvzxUb6yhwyMpJ0nGK7aHQDIjicBqL1sRNUifYY9twgIlnVIDjrIv4VHARd4l7D0'
        b'eCohTvuF4xdJLcxieyLVsD6HtHAR3UEWOXbEJ8Bk6qnDOKehCI/3nSVGaFbFAXcrRhEzHNZIxOUU4hlm44+Q37CWhesXxJ0VsUXbFuuDMgnRqlSwV5l8r4YbZEcVwsYV'
        b'tvHKMRhWCjI5Zr+fdG83PoyUwh6vDCJ6m4lxrq5pivopL2Ul7Fa5nXtUBCXHxQKJ30eI+cph8BbhQE/uGW+oPEcoe9ccllQTSSrXSCYWboankaJMhxoBTtPvMQLq5dir'
        b'hLXtLgUROBBpSaDUiqOmsHr8AozrGfkQJjSwDqZOeMwitRA2jCtRM9Zx49Ypfyq0H7o8DkF9mppXED1+RZtIsuoBS+6EwaXR4obHcqA4nbO2YFaWGKEjBCtfObfhVIFq'
        b'aDqox/zbyGBZPswrY1kgTEpYwvg5CXVSHgSCc4eIESYdz+A6VFilOBKL1nHjJSOGloRjbJSuRckCignWiEdLYIq8A3x8LcjSlHpsFNdc3WFYB1oUdPYQ/atgLoGEte+Y'
        b'Mw+GtQhWRoygxRELDQjtZmAsArvCoM0uklCn1AfaEyJJJ0yeYfZJL/ZEZhmLC5KdsdEaB/Kw3Apm9oViUboN9F86Tnqhn1r8iOzWdk/CG1j2xwqLSNIcbWYkzfcsDcKT'
        b'ceCw2tksfBxI/NbIFq4dVJWCrkvpMEXg1UlPmAqUJDHYyAwit72OWKYK+vOp0aSt9uAgCzbUBg9zSac0BV4ipiLXpclClA7FMvpHcdwxBZt91dNgDYZzsc0RVtyzsIno'
        b'dx+nzujCRijvCN4TSeEG09glAWqwLM7GRvocYfCiujc0ntTe40ieVwU1C8edCMvXiDMmSRQWiR3Wr5D/OaZChG+Ji2fik5RsQrhaLRblfvGKHMyfw8FLQYEpSRfIVp2R'
        b'pyq0sthNMjjjB5Xx0HTGXAPIy7iL1ZfkYnEsFO6ruMWcv4GdvgF7bbHOBqf3Jkdhjb0Ys10JiIrJj+7CNf+8AqJAZZwi6a8efKwrNIJGlWAsiY/wunA8wJPEvMoFH2Yf'
        b'ScBlQwKlCerWSnIPJaIJIcZkI3U4lGHA/YCI2Rx/EKZx3tCUxLcZ+66T1NXAlAm5QJVKkqQiRzIj1OihlQm4fuoK9U81koVQKw0Lyk5WBGud11VuKxizqEuEOY8tsCwa'
        b'Og+nwUIA1OceJ5sm2lzpY5xN3u2CQEwDh7DOTSEL+lUlLhkT6HZQU6YJEhtt+b6hPsx9iseleJwVkWzNU8t7LJzksVbn7F4hsXgr6e8qMuHH8onWDw+GSofBhAO2RhB3'
        b'txJyr8gyhxxGdcKI2ORXQ406Fod4MtNHhQobj9aDATscP2mGZM/47mXr+gyhy0qP5POhM7SpEWHasknpPEqE6Qgd4vNWseCD2tCn5QiFcVBuTbavCwGiXpipNkFFfTIW'
        b'ScN0YtZt0ltFMBfpQEplNpGheKVkzil7GJY7TAS+jy2a0USiZWXsvaiGE1Im+e7OVzSg4zBM+hcQSw2Q4uvHFi1cyPHFYWWydO6TDl1NJmWQL+ORRT3YSYXUGx7JgX4n'
        b'oS2OH9sPQ64y2J6DY4pJ5zVhUEnxCjSoYZXfRSroDjywkLQLYOuFCKZaydXXD8h0Oxx8CScMCRmGSYjaYwxxw5Pgqwk6fNxdeCQVFSSWZH4TeNXDgmwSlh4i5Uz8WekB'
        b'U3uk+QQFi9FRBHwD1CVLVGqxklo46fBq6JOCe8lQ4ojDlqQBym5dhfojUcjGyHsJ3i44aROgrEBJijEJ2SNN6LEkKW8heZgin7o9RlrrEK5qQFPoEb9ML1KgQzCE40K6'
        b'5S7M6qs6ksfRB4PuMCKuQ3LUDhtGalpkylabYW0B1jLSlF8jizvzgBOdrXOGXuNwXCZNiY1K+533Y+cRaE6MIL4pw8Ys0kzreedw8qBzGBSl5hAuPrDiOcBgbJ5qXBxR'
        b'PTUZV6E6DqaukPFcR+ZbNVFr+ijBavF+R/IJl2FAEkuzjvoluRAKlGHFDUui74wcn5hvRI7ZxtSXLQnZeTdhKYh+9kGrP7noXTCZ6Y0T4ZxqnMNV53Ou0GRCapPcXy8X'
        b'nPMl821SNsGW7LjmSBKODck4MtYKDfOhMZdPYiTPjVmQIN0hfmaStI6r5oTFzcSeC444p0nGbgQ2yKR4wOh+bPOwhjoBqbhuEcvhophC/uLajYve3mQPFPmGOepjSX4G'
        b'Gdjr+MidGGAGuqRxzUEylbTOKB97QnDF6CZZUO3w8ICngmwINiZw79bG2Rj/7RvwAFbYgFYfLAdTE0lOBtlYEbcubNBbHVuuBxuftabGPcQRZ7xzG2twXofUY1kUdIWR'
        b'tTVvKZGcYacJU94yLOgbZay2I9KWpJIQrCtg93koJpNginRLjS3WaktSGwekLXGiIJkMwJK4PLjnQnq5BroFOKMpjW1nND01iWPGTMQV9+LSsTColXeTIshcwUIvsmdG'
        b'GaAdwgkWOuwh3reRTzwFxef8TI7kXJLBdcXwfGNC9yXfTOx3TTsF9zOxwS6EnGpmh846Jhew1VrGMKV01I/EuEcDVmRgIeJ6qhkOGRFwLWIbFF/AlTwZLDkZQqJRTI7J'
        b'EMFOHTktBkTuJl3skJMRJGlg5dlLKeej7bHVT55/Up3uG4c6CahX0iCRa4DFS3Jsw/oFXTb2SZq7ENb2wCJ7ffdIZy85fVVxx1zIeu88SNTogYm9lulQ57+PBKOGfJ/s'
        b'XGg5SL1Q4oPzzrJkv6+SYdB+Ml8De+VuiVML6j2hVUW6gGSunn7VwYZ5esx16DQgl7JI+UgQzGtCu+JhF7lreNcXi3WiJfFRKNQnQyeMEhvVBEey8VJ8lMsGvKjnVwl9'
        b'p0hFFHFR+G5FG5CeJjPoDOXtCKTG3A3HhXwrss1gAJdJPtahTDYyLvcsyWQXMFVCJmm/A7Vt4yY80MX6RLK6568Qv4xf0yS2Gr2JpbehnJCcTI+7EdAkOJz7PTYstZR5'
        b'5JUQuLFhqfvhpIAJwS4d0w9W2I+1JADh+2/Q5Xati/HSmtivdWQ/9e4GTlyEMUnvGHrEAhlIA2IOuKANG/jo8CVZak8xducAe/9756wz1AuhUZOkbe0amzveK6DDQVhJ'
        b'JF0zdIuQ8T7J0gPqiToZXezzJSQdJcJXYX0BbsCqsyqWO8CqJfbuD8DKVPaGy4eNUyWcItIUHyBMKZcT4kjiHjaJ+ro+yfiybVAGcVu/ih3Vrd5GHRv36Zli24GTZCuQ'
        b'aHgQK6yrJuO8HLY6GeCAiNzG4igo8sBlNxiVZlFVG8jweUjQ3Mcjjl+RgA4db2iSJQdhwEYBetxtocWezIRizVC1YKr+0L6DEhJYdtoDy2Xxrscp8opXrcjEKnXEaYVM'
        b'nLeW87ODXntscD/qRnSZhVYhyX0/wX1Jfoy+IlvMv0xQsAx39InXx/lkmN2+akvs1hAMxbIcVyxHE4JvXD5AgNCOpRlEuEEGBPM2ZHg0JCVD3xHiZzYC34AVGjjrwLYh'
        b'vAhlEtCbrA9DQph0PYoLzD/HwtOEX3P+10ihP7aXINO6D6pMsMiCaDOpDr03oUmJ2LLMkL1MFi+QcLgYSiU/cJbHRrIdJK4x+6dI5VA6+Xtk0rNF8nUwqIItJzTy2MSK'
        b'ECJeK6xcuGoEI5aw5gl9puLQYkC2VVsEDF8mn2cc+iyjyfohve1wNOMgrPgaX8FeI2j2hUFzm5M4K05KpcnHgCzQDpyxJRU3zESkJUT5hD1Z2KNWuBG2n6CtKThGPvpm'
        b'6J5I4p0yLDzkT89o3uei53aTR7Zl2WUcJsNk3VSMiyotcxZXWdDgAOh9ETfYDO+5c+NKUdAqmU0c38GFsmdh7A3woalgd/SqjAyXPj8LvlIQj3+ER300ZcrdZBu3xw9r'
        b'eKQt7vL4Njy6/TE84J5EyGDJ1s4LSRU08/gedJMqLO0G6S3zcWZDZPPpu0NkZARR9bixrRYcFvkFiclBJY9vx2a0NmERt0JfQS4JK/3FDWR5fEce3s+ADq5iGqdxmY2q'
        b'4bLqi2G16YQXm9qGnGdDoKbiAbjK4wfxsDcOH3IXYmTYwoAACVss4obW6rKxgXtGPqzk+5mL2aa8GIkbP2XK5yp8BqvD/HzFxbV4fHMe9ybwxVDc2skzuyNx42w/KzYU'
        b'J8g25XtyW9FzAQyMTgu42cQ2Dr8P/ZboEM9UwJ02VRTbPZ0k4yh+QXk3WnKy6ouTnkfkzio48wJNxQKpKC7cQcrorUTxbKatQ9794OGDLwdpn1b8Ute19771pSXt1NQQ'
        b'f9v1a1LrHsoPQuQdI/ZoGdVleVsYHc8sr/3uz0ouq5r+4KvFt+2+N3H4p4axdwcsv7fW8r0Hv/7WsYsDZu+9s2/9HePfBzfwtR6k2e3/TmKEZ0LolxKiDiQEDyaU/uxB'
        b'SkvdeTvzbLv/8Pud5jv3DJ8n3tz5rtEXBBP/636UXtgv/20g9LyR0e8zfA5eH1l439Q52iG//rfTJt9ocq52aAsZO6JucDbpVxfyM399vvXn/+7X9OPzTdN/+1udiaFD'
        b'uinVVT+3Gjcttf3QNFzRahbC1YLOJ3TbzrT8MuCm+eMVk+ShFd+0pADPVddfvv0357M8HNfqNf72fZNjGv+2NnbqJ1/K+McPar/TE90UJvO9ZM/6mu7G63uPiu1N/ObT'
        b'U6fzvtwxrxkqZhY7/sWeuBy5jh+G/ERouPoTYX7FasyVEOXGml/DV95y+ButztJveph+YUD1iv6W4Leahk7pv3s63PVeX4PkI23s+/m7F5L+GZ2/dLqmyP6LPp0/En86'
        b'B98p+OrFH5sMuH/lH8zLwts/+EH+0Nf+YfznH1hbdDatLndJpv6T6td7J8zSHh7+UPELDVlVK25fXTB0eLauAVJOjv8wtP13sRfcNhxrf/F1/fl3qxxmzfwfaT9zsbwh'
        b'+67jqmPZkOJR2XPrX5wK+eb13Ji4eavx4Su67xt4rHf/+tA71d0u1xcPjep+62eRAUe/cXbOe1X9/bX2bjGT3+dPXZFsG3naOnTnzNOsdom3dAruamX+fVnTzZ/cfOuD'
        b'm+2PtI9+9weCyrZ+g8xKy/c/+JHrLxO2n/02UU/0o68mffBAdur+jon1248lfisVmCeMDqnb9+GCZ887vyJaZOVIHHr73JLt1hevjOUeVdl5+q+uX0v5x3ftrg3o9EqH'
        b'Hn535uiGxwcnO8Tf/+nQv+QYJ8+vf3duKfLvnyn9JKVV7OaK2u/Pbsp97R2dr31DzPKddzqaGlOKz6RUf+uD4oHD//Kg3lN79Yfv/fyyRtoPI5fOmNlKGkxE5f7H18/N'
        b'//rLBRMPDv1Dxm9Tfiv9rb+3j1gNmvpV59vbt+/m7vzH2HeO7f+u1D//0PrvnqW7z9SbynCRZXFBi/C40p+ffY2DpBqdGG45Pin+1asfm+UeenF3AZGSFrdYXgc6Lsru'
        b'g4FPClYgxMlALOdWwgvP4l3ZLLJCukXSIhZcVCErV44U/KKAp5MvlKKjhd1NZqf1oVGWNPdy1ouM13Dh2hWRBE/TTQATKdD8/ABl07OFzuyrcldycVEBKgiiV6UUpEQy'
        b'OKVwVZxnKi8k63gY556zJQa2WjDxKutj8poo+8u8UP2y9AChBCxjZe7L6L/tHrLa7q9KlMJHYtZiWMfN6j9xITsbqqWuUO2yc+1IZZZ/QnE4L0HYXer2nO3/QTpvgvcy'
        b'UCwLx9/5CaFimcdmGvzm1G2pv6LkLx5w4C87gT6Yx0U7cPuMv0+dX//pf7urO6Sio1MzYhOio/NfHXHLN7pkP4pF94l/hbydM3yeSG1HKCmtsaWgXJZda1d+repas0FF'
        b'QVlBc3Zzdrddd2z/oZb89vyh0623m29P7adP1pLBXO7S6bm8aas5q7dOvHXiK8pve3/B+x07/007//c09zTbNce2H2qRbpfu9n2iaTWl8UTzyKZz4BONwM3g0M2wM0+D'
        b'w9/RCN/UCH9PXb9bmUX+3FTczyI1RvB3ZHjKqrXuD9TKjpcd/3BHki/tw99S1qu1HJDbtPR8ou/1VN/ribL3U2XvTTlvFtVAhqfhUia7paa/uc/3iZpvmcwOCbvZU43D'
        b'ZXLfZwvmT2xK6XIHTnSwIyGQdtrhfVoioyi9d4f3+cl+SWmbHd7nJ8o60po7vM9MnMVZ5s9M5IXSB3d4n5nISbHyPj9RVZTWYU34o5IDPC3tMtGO0JPPzvwn02AxPWmT'
        b'Hd4fl9QmPmP/nn909gSfJ6O4I5YhJu24w/vLp8+49PnusYCqVqX+onIJ4vRrS1pjR+yWgPXGX0v6jEuf7x5TjTWrdF9WXMjlOi7F09HdlNL8vrQCV/2LYtJaO7w/PX3G'
        b'pc93j994IJcrlCiluSNmyITtj0ueseQ5d7Rb4O7dvvyz4tIstOX/o/+e7f57/vFr+TKcRJyXlN6/w/trTLt1nnH/n3PpKynhMrgpcJUPFmeZ/7rS5tRn3P/nXPqq2lyG'
        b'S7s0d5Ngmf9602dc+nz3+GUDuMuecuF8af0d3v9BmiV2jGmPPy05LsZnEPqZiQRfeh87+uREQsTK+vxEn+upaDGmgP770mdc+nz3+CXlucsnxLkKhUlIW+zw/u9Ln3Hp'
        b'893jlw3jLruJjCWFO6H8A5QG83ePTSg98+IMO06RIBUjxikisR1vKVM6FfGxrG+muRInhFJ0A5f6SflJ7aUfLN2U0tqJUOQpGzD75SR/Ny1z3+I2KRaxEyyt5b9n5rTk'
        b'/tTMdSnnqdmJbyoadBs8VdzfffrJ7jpQNYP/wtw6/4ncOwIuq8JHbclmEXC63Y8dN+WB6R4PwYug14eyNvifvEz6/7ckm+0EGfOJ0eH+GN8o68dsVfIrt4jtdZcdw/YW'
        b'Z75PCJ/PV2Rrwv8neZn82UKFM75+W1zaXZv3tra8u6kgRX/9Z4Ls00T6r7T+NK3mcJDAXbH4mvV7PzIudeoSOJyW+Bshf0bK8HeyZr9WP7hoVWsU4lZ68Ovf2Hc2/ODv'
        b'fBq/GBOZ9+jD7yZ/r61lUddn5isHSqN+8ZVHhccrTAbv+YYOyoSZDlRdehDSsefncSalvYrWP4z8an/Esy/9/fHbyV9+v6uyIcVuNjyx5FvBf/uO6U8XG45p77XSXmnX'
        b'yo/6xpxs9L/pDBXeVMtKXwtUGm52eTjl9PXGIw4W2X8zBSI0+/ah9wzDtPzC4r/z4bpheG5N1a/m0zNNTg75/dr9SajlQr/mj8/b/ot1+nfV7v97Qdu/65XV2SsF/crN'
        b'/x9Nfvv+7x77Wazm2Flsj+Bwi7LaTy8Vmf+yvC2q+ISKZUREUbWDTs6UvIbuwlT13g+lNk+WuZz4SayeZNmVsn37TX6gaXzkpF5ie8/d7KjvK4f1fyWzeE9W1I8kFof6'
        b'rnxP70uTfKeQ9wPvKUTvnEuVtJ821eOC8ShhDVTFQB8b6A8K4mJFSvJkYUYMh6DOejfoZBHOw7RfkCVOszxBlmIwbkU3rgmg5/o+Lou0cxBUsl0T2R477KW4JA8X4a68'
        b'skA3G0u50b48uXC2VWaAJE9CKMaXl4KOo9z5GMEhBezGSmsJHj+Eh304G8jFGYL2o2zWeY2JZTgWslE+Pk/aSgxaoUZ1N4JqJ7azpZTY8HITJWEgH6awXYEbRJQ/D/Ns'
        b'SbLli4sw4imPFYJAKMIZLsgRtOCgOjTDyKvdraALSrCd24GIGl8N/bsFB/hgtamPEEZUeMrYIIAVDeznSriE9XjXz9ciMAH7DtnzeZJYLyZhBo1c9fk4CaV+dvYs/AYX'
        b'6dlJiqdgIHAygxmu+ofCjdhVnwDu4sEbPHmcENiy2QXccGCyG6zCLFtQZMYiqQp4wtN8OjOTuBvFtfXYuRgzFnwqwILHE9ry2WT5h7tBSDewIhvGUs0tsZpFeE3jwxLW'
        b'neDCmGIbPBQzxyG2drXSnz04gNou5GnfFMJdmIBhrmbaIWa4Dp1+rGosIDcRXtZUDGuTPbnLMpmGeN8l+7WrMj5iMAXDkdwWWLiRi3WyOKOA89lQjouZyOZSzV2BSgUR'
        b'j6ezTyhp5c2xjBmM4yAUwwoXi8WclccjxmsVYyuD5nbjUE3IwIpv5sc2AmuTgSlugNMEWg39YNyEepjt7MTtdhfkA9XWgVinZmkqwfM6KVlAXVrNUewyFHvL4hTO8WHS'
        b'jDqnjoeDkTK7QVc2qIJjbMkpF7hVvIB/g8Shn4WlZUFX5MSu0LUBHOSiqVibvQyisidXCCUph7kijlk5Er0r2JJH6MFyfzGe9AExqDwPL9qxij1JsGZl7mtpEWBpxefJ'
        b'qQlkoDJsl9UewSR2+ZkTn1gRv5EMmUqE7eWp2AuwE0axjuPmkDhck8VBc28LMxZtjHUJ1rLF73VYz0kRjIXbwZrI3Fecx/fjYTN0uJoe+0sM5/7FVf+fyYA4RsmnjLv+'
        b'50wJFr6FmRIp6Sk5L0ZYdQSfOsJK9oUOT1ylMJB9tkSq3xbpviPS7ch7IjJ5KjIp9NwSypT63/XfVDIYOPJEaPFUaLEptNgSigp92GdLqFQYwD5bTO+yz5bQbvPTv1tC'
        b'881P+r52+x8eqG++/G4JrTY/6bslNNr8+HdLaLb58e+OmIS42o6YQFprS85g8w++H76nsIf5clofJVtymmX+Lz9kE0trcRT7saw6XaayXiVbiqpl4uxDmcTVKMv3hbqb'
        b'H/9uCQ02P/59RcMdidNHxZmh/T///rv/JeUQNKqSGWjDEE1N4rgOD7T5x215oCN/3FIAZmLs2ILPji0F7NhWzoMngGN8SnddILNtQWpielY3ydm2eE5uZmritjA1JTtn'
        b'W5iQEk9pRmZi+rYgOydrWzzuek5i9rYwLiMjdVuQkp6zLZ5E5j79y4pNv5i4LZ6Snpmbsy2IT87aFmRkJWxLJKWk5iTSj7TYzG1BfkrmtnhsdnxKyrYgOTGPslDxMinZ'
        b'KenZObHp8YnbEpm5cakp8dtyJ3djnQXEXqab5TKzEnNyUpKuR+elpW5L+WfEX/ZMoUpKx9k7JKazTU22RSnZGdE5KWmJVFBa5rbQ89QJz21RZmxWdmI0XWKxN7eV0jIS'
        b'HA9Hxycnxl+OTki5mJKzLRkbH5+YmZO9LeIaFp2TQd5L+sVtQUSA/7ZsdnJKUk50YlZWRta2KDc9Pjk2JT0xIToxL35bOjo6O5FIFR29LZ+eEZ0Rl5SbHR/L4oNuS7/8'
        b'Qc3JTWe7mnzkXGab8V7te/S5f/r6H4Ehl0izEvL5n/Om6ePAqMDnp4ozf+P/7/TP62zpS7s78N52kD8uFPxGKonEIDE+2WpbMTr6xfELF/g3e1781s+Mjb/M9uthgfzY'
        b'tcSEQFMpLlLZtmR0dGxqanT0bjdzscy+S128LZGaER+bmp31NhudsCQ53Y1/xgV5Y2zxGyln4ufc1ETXLFtJFoWQeOMWJYTffP6OmJAv3OGxRI4nKyqU3BHmHuWr7vBe'
        b'SzNzyTlQ+raU9jtS2s2+T6SMn0oZ7/DE+Ic2LVzfOvDWgbdNvmCyaeFL3y0pxS0Z9TKLTQ37JzIHn8oc3BQe3OIpbvIUazWf8PY85e3ZfPnl6ve/AcRlC2s='
    ))))


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
        b'eJzEvQdAlEf6Pz7vNpZedultERAWWLoN0Yig0rsNCyzsIosIusuqEOyFRSwgGsASwApW7C1GM5PkklwuATEROXNncl7Jfe8SjaZ5Jf+ZeXfXRdBo7u73J2Z33uedPs88'
        b'83meeWb2D8Dkj6v/fliKP5qBAuSBBSCPUTDrQR5HyS01B0P+FJyjDBtSmyu4HKDkH9W/WQo05nM4mCJQ8Axx1jL42UxpTMOAKr55sVTwuNQiZ0pmnGRRhUJbppRUFEsq'
        b'S5SSzKrKkopyyVRVeaWyqESyWF60UL5AGWphkVui0hjiKpTFqnKlRlKsLS+qVFWUayTycoWkqEyu0WBqZYVkWYV6oWSZqrJEQooItSgKMKl+IP7fkrT4B/xRC2qZWk4t'
        b't5ZXy68V1JrVCmvNay1qLWutaq1rbWpta+1q7WsdakW14lrHWqda51qXWtdat1r3Wo9az1qvWu9aSa1P7Yha31q/Wv/akbUBzUDnrPPQuep8dH46b52Dzk0n1JnpJDpr'
        b'HU9nq7PQiXRWOnOdo85dB3RcnZ3OS+evG6kT6/g6G52nzkXnpLPUjdAJdBwdo/PVBejsiwPxWAhXBHJAnZ+hn1dIzQEH1AQannFYaggzYGXgSmkO8B2Gugws584Gyxjz'
        b'9VJOepHpmEbi/0WkU3iUDaqA1Ca9TIjDqIQLeGXrcagg5GCcC9D6E+LRmTmoHtVlpGYhHdqSAs9nSNGWpOmZMgEImMJD12AT3CLlaj1x3Dh0DV1NSQpJkqE6tDmND2zQ'
        b'FinaxE1Htahd60wyhhcdSAQ+4KF2eIjHwDZ0Ee3XeuN38CqscwqmKdOS0Bb0GlwnTeIBB9TEhZcl06QcrRuOJYNX41Iio3CEFLR10oQMnJWtD3c8ap1LX6MdpegaeZ+U'
        b'hraGKchrG3SCG1GQgdO74ggB2qka8m75aFwO2swAiyQO7IYH3bS++O14dEZhiU7blqNL6JwG1qELi9HZJbDe1hoAD1+eGQ9ekTJaFxxTALdpUX1qMtrMBdwAL/QmA3fj'
        b'Srfi14TronBX7EyBxwNxX2xKeSUTbYZ1GWhrRhLcEpYukwrAtClmNaPQWn1uwdUz0Rm0OQZeSkvN4AN+DYMOoO3oTfyadBs8s2R0cLIsBO1YlCYLZYCVI9cCnpuJ39I2'
        b'rxaFByeGBElRO6pLJW2yRA0cdKI0pIgxGfcow7hD/LEzshaPPWZLHmZHAWZbIWZVgJnWEjOtNWZQW8yw9pipRZhhHTGrOmOGdcUs7o5Z3hOzsjdmdB/Mvr6Y+QlbB+gC'
        b'dVJdkC5YF6KT6UJ1YbpwXYQuUheliy6OomyNhUOdpZGtOZStGRO25pgwMLOSo2frp6hGtl7wNFt7DGHrDJatr4ULgBUAduFT72vHr5wPKPFDDQeQiOFTjy4ZnypgicBe'
        b'COwwLdwpXfOZ2RiW+LUbH+BvSfhSwbyqGWNAFyizwOQRES68Rw5gEpjwOOAbzvmIAvsipoxI0JM1LYzHwgJbMKkg8k7ke+mzACXvtn9o+8+UYG9O5l3m3y7O6b8DA0Ab'
        b'Ssb2Ero4Cc+w+rCswEC0KSwRMwzsyg1MTkPbQkKTZMlpDICnFpbbmk9ADTbaKWTAD8P1aLumUr10iVaDLqBudBadRufRKXQOnbEVWlnYmFtbwm1QBzdHhsOWmOjI0RGj'
        b'ouAF2M0D8M055ui4DerQppDCr8FTnimpyeloH7yUlJaCtuFJvhltQlvxPNyC6xQYEhQqlQXDk7ATHsvGWZxGzagR7UQN6DXUhHbMBMA53NoBbXMdxGukawnjPlQQXuMQ'
        b'0Yu5jcEcxi/mUm7AS0cdz8gNXPNBY43DXJNx56zk6rnhKaqRG0qe5gbeEG7gpavJcKou/H4RX5NICv3p4IjXdn8Qu9dnQ0R9I8OtjDyxcdOnX2RmoYZ3Nksvu02N1ypO'
        b'fTEj59c97+95Z+s75YfcNn6Smvkvj5ZvfvjQqvjuhwCEXrOe8/e3pPxHRLDAPRr0Jh7HTbgPN3Mn5wPeOAaeQvtm0LfoCjoJa4NDcffWhTBYemzl+ITK0BsFj0g3oat4'
        b'QOuCZYGJMg5+t4sTESSzh2seOeJ3GY42wTK0JTWCDwR5jBBeRcdfmUVTwVYGD0F9IjyOe2xFBdrHTEUb4A4pb4ATKFVjRgZPPjSkHySrV69+7BhbrK6oVpZLitmFN1Sj'
        b'XCyfOMDVqhTV5INDYmfijx9Wg/tTOUDs1DymcUxLdNMEXUK/yJF9aItpjdkd2ycKvCUK7RWF9onCyUvn5pjGmBZVp7hPFHpLFNkrirwlGtsrGtsniumxinlIxkVthj+k'
        b'ggHzcvkipQav+coBnly9QDNglp+v1pbn5w9Y5ucXlSnl5drFmPKk/gL8UVAgwU1Q2xOiA/6g9U0gb6Pxx+PV4LspHIbx/NzGuX7hasv7HD4jvm3pUD/uc57t+rR+oe1t'
        b'oeiHB1i62hmeHj8kLNEk8AX7LUO5RZzhGKiYcDBXz8E8ysOCYp6Rh/n/NR4eItEshvCwfbrWiRBhk6MmlY/5pgsdg28CeJgsllox5aTxaG0KfsdIp9kAvO6eR+e1JJOl'
        b'M+FZdAavLQxfjZoAPDdvHk0QNleD6gl5Cl6NAJ7YO2GjlnRuvivfEi/hjD08qgbwCjywVKtn1Y3waDB5kwXr0U6AdqNOdJrmNQIvQJuDQwWAmSMnmR2G1zS0cLz67UhA'
        b'TVlkzEpLQFoMOkvL8BuNZdZBnL4JD28ICPGYKzXXEqZHR6xRGw9tHI+HBG3A/+BFdJK2HWd6ArWgowGvklcH8T+4Dr3JrpLbcEesRxfhRXgF54ea8T9ftJlWrciehzbg'
        b'guiLC4AIzWKaH+zAWR+Hh/HKjvEx2ov/oQ1p9JUQ0zth53hE31wlTT8Lj7L12wv3WMMT8DC8Youf2vE/+1fZ/DbCfegs3Ip2oP0cgj4t4Wa0R0t4eMYyh1zUkoMzCwAB'
        b'qAHQLkC745ejvWWoCU+McBCejJrYbPah5hw8u5vNaLvW1ID8QHSFYgUMnFqJoNegM0sZML6agzoZv1j4Bive3vzDj0BzlTCM68crGiJsYLjVFM+ANPe8WcFfXY+oXnei'
        b'8oh/5q9mrPUftzrL7+3Vsy7GhSWtn5T6cEr03XfQqn//+7vpn63+dvWxhZK4xO1i/wPSg5utZF+9y78qCj/64JOMXU0rRQsCvd/ZvW/tt8zjyIbIyU5r3gmb8cONyc3/'
        b'/N28uBxOGdojsvnDRzNm7dnzrzzm8Dy3pG7FvxoLPmkdhy6vPVO2xEw2Om7ZjeQZZi7rPz72RvvH0zP37Dnx75+uxPR8MW4J78wqsGVN2OHWj7FMJU2Fx+GmhOBQjCFD'
        b'COI6xkGHrKMK0dFHBPYsg3UWGBShLiekS0pN5+OePsXBA3N8JJWOqejqClQfgoEiRqqC+Zzqeb5wDWp65EM5ZZWILrloE8aAaD9moTp4LJkPRNFcDLu2WrGlb5YvNQp0'
        b'4ANfoxI9oEYqfEq4PvNDQ4ZEIiFSSy+3BiyV5UUVCmU+kbrVpg9U7vaxcvdBJpa7jv3OLg3Cfk+fTnF37nXxk4CH9wM+x9lHN+2+ANg7NJs1mjWZ6+Ju27r2ix2bpzVO'
        b'a4lvSm1g+p3cWuSNqn4X1zbzVvN2v05un0tIQ9x9LnB2b5FvV+HEXv5t81rnvZ7faN7AaygiqZMak1oU7fF94sBGBsf0kt21c79l599r599e3CnvswvXxfXb0SI74vpc'
        b'xnXEtSzptO8sPeK9y749rtdlXJ9dDI4hEpNVomlcj5XHj99wgWuMxop0p7t5PBBCfx7+ZJcBswFGM2BRXpGvwfpciVKjJpyvdh6mH82M0l8v/iVElJh2X5LJMvB9Bl4G'
        b'3F92Gdgh8AMHLMNeZBkgUIY/aBn4fwplzFlgKxSLgB/+Dp9vBX6aP5mFq2YJSaCBYFj/nOi2hSFgKqVOlNsB3GVjw2d84tM7J42N+u4KS4BlozBcUFo6cWwQoEKqRDo+'
        b'KhyXBJsCC0GhGV+V3vt3voZYDGZVe+z+IHLvmrqOpktNS0b5cl0OhBdHRYSLNfvrIpVXwsPFETM475xuL3yvYNSOrwr/pghy4ByRv5vb9z4v6vj12y5l6RYpFuvE3Ibi'
        b'RPnOwk7Opltr78BsBC7slM1Zt8anZc0ZPpj2jmPvpN9KOY8IJySh7QkYE2lRiwEWyVBn6iOiacJT1XBLcGgSVnpCMUxGdQC4SNCmUt78CrhWyn/2hOQDFgbpZ6N9UYmy'
        b'aGF+kVqpUFVWqPMxBhpKojOzQD8zKznATtQQVb+8xWdTTaumPWr38s4Ru1b0O3v0Ozg2SxulTcG6+Nu2Ti2atpWtKzsX3PQeTd7hNHENkxvMWnxbCluWtAT02vngKSvy'
        b'a8/qEwV0RveKwnqswtRkmA1Tg1ukUgyYFVVoyyvVVS8xM4j2OUwj5pjODw2eH24vMT/URDceAvApUxbq5wVVJp/Ae2bQnPivK3v8IXMigZ0TrS4OwC/EBr8v8Bg3y0fP'
        b'/pumYPYf288FiwvKPk+YDHK1pKvg2ni0hWjFE2oiQASs86Bx4UKs7/kd42L9LfXWxGWAAhgu2o92R5Fp8Xp0JIjE60UjjfxjOlYjed+T4kLujQoFNN/53DlRmGfgGsco'
        b'EIWB/yYa9eJoK8yjbwlAZkHq9qQqNt85cCNqiyKYZM3caBAN92O0Rqu2LU4UhfvbB50dBUaNQSdoFuFmjiBQ4cbBVfMI9ZvAAgi4AzX6ROEaFMFDo8FoDdxA4+5f5AnG'
        b'TtpOivP4RypHH7dxMjwUhQFIFjowBoyJQ5007jpPH6zI+pLu8RgTm8O2AjaPGhVF0EczOjcWjJ1SQ6MK4v1A4qzDAFeh8MqYsWwrYDM8Uw3P4NBMeHgcGJeJOmjkPwRJ'
        b'QaZHMQ8zKGe2dBxbB5FoAjyDezIZHYoBMegI2knjBtnIwCzxe6S+hbmZo9mMpegSfJOoLugU7J4MJnujDWw7OmELeg2r8IC7JB7Ez4OXqOxCB/KtiaIA11YmgIRqfxZ7'
        b'rse9ekGDOxNtcpkCphTCUzRygts0Ig0mwgNTwdRRcI8WAzlQ9UqaBndPOH8amIYOVNKIGPs2qsg8c/NKBImiuRRPFqKDWYi0GCO915KwqDqAgSYpbglGhesQaeB0jChA'
        b'Mjw4mq1y00x0CZ3BVV4uSwEp0aiZ9rKjUxk6g6tchZpSMWS55EU7Y4OFGbBabsUASUHZx6sCAS2yAEPfRnSGNGQDrEsDaXBdHstZThZAHPg7AbArCOnzmM12HVqDzjqi'
        b'M0RJODQ+HaSj06nsopEYAFKjL/Bw1pM/8Uxgx1q+bAE6g9sdVpYBMtABeIxG7VAFgdxZCQzOd3KSII5dH5YwaBc6g3vDbGEmyGScaUyPRa4gPPawAA/03BGJCexAW8VM'
        b't6SiGh3PAllwK1xD4+akCYFdTYwZjpt6fslKPWNexh34miWZzcHZIDsPHqdxVzjZAI9J6TwQXlB2jTAQVXHOzkIXLTm06zfngBzc4a20ydaoHjZa4s4Mh8dzQS5Gzwdp'
        b'LpxUdxAtceTjdtSs4TiyTZ40X25JunILvDYdTI9Ce2hUr2pvEDvpAhcXGNviXME22QEdiLTEHenOzAAz4PlQGvOyoy9IcNmMa1xQ2DaPq29GC+a1TZa4J5cvm4knw/ki'
        b'Gnd8hhPWbhZwcZ/XxOcvZStgg6HlWUvckamwbRaY9cpCGrUAhIG5y3UCXIERcmWVPttdcHsMrMehpRNmg9kFcDWNu9FmFCgRriGSyuG62o1d1LeNiQKKxX/C+RZEChLn'
        b'sMSt2RGgILNQgCf45It2JUDKYaf45nxrWE+m15bIPJDntIpSgzGXXYH1uIOzRs0Bc0Jml/3w008/TZ6IxWJ0JQ8XZjVQyrD5Oo0cDcrCR5CGqb8OmwhUe+59CzSTcL/W'
        b'/5iu7X0/nRNnJ7h75MvWNVlL8sEyszFvr3jLM7XG3OHqvyLsKxLXxld7FTz8ePOYwjeW//HtlLxoq4iI7z7/vwNX/v1V5beHH4+o35dwb2nLh+CauK7UY1aj5doPss9d'
        b'e/hq5eOHwWZL78345CfHr7+KemvNbwv9GsQTrOpQ5hfC7C8C3317SaquqcXhcITvR4XpqbvL3lWcGTm+4rTlyCslp1M+O3bnTNmN4JFXS28svP+Ox6fvWJdtmtPv9LDf'
        b'3rLf8fvuMK/V78R71P1qrH3GkpFOS0Ln381+A2rrf7vZ/c6+R4vOjfPzi/+u86u3vx49L3iB9Ks/T5jwpzqvkH09FjvP3x0z78uKPM29XNGqfxz65G7AV5d3/maH34/o'
        b'1jFlWPy6nWvTdr06qsNz3MBHj8rDlv35B9sJFmVtf33/h0cen4hzNnCOxlUcmWz93esrwfQaef6sy1gBIgZN1Ipa4B6sxqSjutRx5hjqMFjNOcrBC0ImxUjwdSHzxG6E'
        b'OudwZLbw4CNqTz+KLk9IQVuC0ZY0WTKxuTugi9w4tBrVojb4JjVLFaIdeAWqR5tTkogVSTDWPZLjijrhLpqDLWyERzXweGK6LJDY5dE2LrBHDVwXe9i9DG35BXqQEaYM'
        b'2OgRirYon2D46qeeKeaayWExVyLXgLkiNhGkdVfk1KBuYRrGNL/S+MpNkV+/s7sJ+MKAxtWGAK6s+1wScnFv0Yckvu36UGBwpz4UHtWtD40dfzGbDcUlXC9kQ8lp76nZ'
        b'UM6Mnll5bHBufo+8iAbv0lL4JERLoSFaCg3RUmiIlkJDtBQaIqU8oCFaCg2xpdAgWwoJEjVPjMsxY8OuHi3GsI9fe7YhHCTrLDSEo0Z3qw3h2FeuM4ZwAjONec/4lMpk'
        b'MD2ZxsxymZkMKV7/OI8pYEgV6KOQVCH7vjkbdvNsKTSEfUe2qw3hkLBuzgN9OCb2+ohvSFiXdN8Kr3O6Kfc5Vtaed7wDO0WdOZ2FnS6fekc2TsOwuBIrui0R27V3XTzb'
        b'3W/5RPb6RHZH9/mMvYhDE3pdJrTySau92l07ozu8e13C8bM1kETdtwGeI9ontyY3mPeLvFqqekXSzpxuh66ZN0TR/e4SrL6KR+F6iF1+eMQHYs9vAGPtedvZ4z4Xfz/W'
        b'UNziF2cZHwlQpHn8RC6awOBPg32Sixnx2aCbGiNNMDfZUnuag4nlmwLuH4ldkssw9i+rkG4XjAD7LGXcnwXeZA8HmABv7n8NeL+AMmrGAu/IV63mRjLhAOM3q4/ypuuB'
        b'93exFupzZBsWQ5NNEXpggDbI4rCOCc+WEVgECr0qVHPKuBxNDn53YcHHxCTf0TSOmOSPbbwx78NUq72b9354tKM02+VMq4vLJpfg1pjWnJYclwOrH+e4ZL+Z1XLQ5cjq'
        b'0+esJn2SOspq8Scht92srN6y2vMleHudTdh3p6QMa4HfAGs9g+EFdOyJmV2GtqLLUt6wIstgMGfFlRs7uJpKtbaoUovVqny1slipVpYXKauf846KMbJlQ4zpk3mYGYmJ'
        b'vClWl3Db1qEhur5KL9H67fAEb8huELZEt3Pa7VvG9tr5Plc/FAzwNLiUF2fRsYRFn1PTtabsGsdjGIeX0Q9Jwhdg08H64f+QTblD2FSQzoLHxlzYbqlOX0VMuscAbEWr'
        b'pZRTRzljMEU6Kq7AYY2XN5iqurHlMk8Th0lv/fk0y5MRBp7cPKmqOPVH8bufZM6bcifVauPRval7F6+0yDlvmbnj1HbXwI9W29kW3001A0vmWgX7bZBy6E6OWIB2smv1'
        b'/LEs+01B2x95kVpdg6fRuuBQtHr+YJMGb74IHpZynx5c0jwja7o8pes/YcxnvqFsOUrPlpmmbEk2cfCi2h59UxTYFd/NO5p0kXMkHXPobZGsU9EniuqxihrMhkUvxYYT'
        b'CRs+s151pkyY8YuY8EWMd3wd8z8y3hX/vLwUsPLyfI0NEHJwd4QXWHXPK2Lx9I0VPJA40Zlo1yFmK+axRM9VHNBTQCyoBanLltgD1ZkWC65mPukllE4tck3EJteF2ZMR'
        b'HSte33MOC8xRVsrNUywmaT+cdTPuS/G7ZSMFG0f8Lv1P4kNBoYKNocWSeteQdz80j/Z10a05f+pA+FupJzhfhP52+rteAR9FA22vg/13H+m5Fh7PyYJHU9NCOICXwjij'
        b'RnhaLqbwcDmqw/OnPgRtDYZnwjLS0Jb0JHiMB5yzeaMXwR0vYYazLlcur8xXaJX5CnmlsnrwI2XWPD2zzuUBkfNt95DO3JOzu2b3uY9pEGKWbVnei6VkwsmMroy+kAnX'
        b'mRshcf0SaWdch3VDUr+zpD1i+4p+F8+7ImddCoYFLh6tqk5md1mvc1ADD0MJkfMgwxuPFDpgXqaUK3D5VS9jlSZ7kU/VfhswsbvN4b3c9iRrdzP4bZE/gYGfyghL81if'
        b'JszUHJ2AWqXNdMJiAWVs7qDNSZ75ILbFYZ4JC3NX8vSM/RT12V5E5kMYm88y9p7qSKAAnckcrIDmadJZHk7KIE4UiUs4mLHvTXQDqu4oyNeQNefSRe7uD0Zj4SrTC9dz'
        b'VqOsZn+4/J7r+Nn1j5Jnyb/Ye0y6+Wir5G8uknm/zv31nfezUC7/3rIl4DeFKProxnHjN67p0F3Z2IinQPAG1aibE6YXPEwZK//r6tN7Rm3e6xH+8K2aN05wW2+9v7XM'
        b'a7N11P7XDm70b1kTteBTa7DO0SN1sS1WtcjguqD1dnRPyAxwMGM3wn3MdHQu9RFZNZInjmK9luCuVB51WmqZTvWzMegE7IT74OspqC4Ep96SwQAh2syB61dZs3tIZ+Be'
        b'uB6/0YVhzOHpwEtj4DU7tI592eQGL6P6NHgMj8hKqIPrmWlY+VovtXxRxeppjiQGF4OeZZxdVguUJpNr0BOdW+v0c2sxnlvuzSGNIU2huvh+kVPz2MaxTTG6hM9tHe84'
        b'e7YUtxf2OUsbeQ1MQ0S/h38n05pGkDeN1rJk+4R+d+8OPOf2h/S6hzYk3HN2+9zOs0XRntRnF0pCRW0lrSW7S7vGdecefaXXK6bPbvxDc76LjS4RqwdiD12GySQ0J5MQ'
        b'z7yppPqCIm1lRfGz1xi25eZ0LhaYbLWp08lsHNTcVhJzHP74B56MFXgy+j8A+ONlgXmzIAActowcDMyNJmm62PCNwJw4V4Fi/v8A9QyxijsNmZPe7JwMn/wB2IE5835R'
        b'lXl6SqjeeJNFrL5gbLi6wGO8VzhLnO/CukDZMcvK8uI9WOKlMHajSOKx0ip4YjFL/EekA919up61qqY6K4IljlriATDSDLxvVjA3eLIvSxxbEk2glWSS2WKH8ISFLPFW'
        b'EOuVNWlSsdVvZy9giVNdA0EmLv1uzpLCDxemssSfcieCGjw/u93U2eU1NSzxT3NjwXJc0CQHeeSfw3xYonBaDKgk9ZyGAa5XEkts8nUBWC0Jv59TNFeWmsESLZxlYBZJ'
        b'Pq9gssJGTzw5l90km7S0OrVw+hSW+FA1CazGxEz+quySdP06XafgUZ+w+8srQgJtI1nin6usAZ7VgYtdVoTs4kWzxJZR7gBLf2F3scLjpmQkS9zoOBpg+W1n90pZ9scr'
        b'A1mi47ws0I4L6oktDUpJy2WJn2UqwHuk6yo0U2+MmsgSXUcWgw9x8tULSgTZS4JZ4uJIYmPE/elXHPvpmGSW+KmdLfGLc1ldUB2i1upd3zI8XgWPcJUyp5Q5zRpXxRK7'
        b'baIA0VjtbJdEIjd3lhhTPQKQJe16xpIRdqOLgWrn/h1cDRZxoMHjD1uaUtLRJKuNe1NHfr2g6tzqm0Xd8vetq/kp7TMKe/n17427Ljmvi7+3vb8vKc8/bsTszX8+89Pv'
        b'o7Z+c3zVdbOc1kPfX5/YtkWV+iMzbVFyX1nL365H/+XcxElmf9k/omQUOPKaxkV4oXFp7Nkr732zY5TXu/Vu7//4tz1nfaZZiLKz418/niSzDryeeqTqN5/tsi7NntU/'
        b'qy29RxUibdCd/az2ve+/sPmD6/sXfrdz+W//bT9DnO33gL+l9Z1PfTp4/4csr5+6J3X8wj/hSLV218zmNw+HHg4cl/OrHzxdzI9GeI1c9HVDTMxH+Y9j/v7XY9p7Fvtd'
        b'L73+w+/nxoxbeuX6V04xJ7LS/ul+J/WfXztXuv2rrnzLt+vFlheqWhqzvr3819NZP479aNThmq8f50+8OifL8/UfFi6StmV825b39cKU2/N/83+B3ndi744+YvGvC033'
        b'/vh1ldP08+vu/d258cRa30/XSbmsW8IWtHc+BVRhGegA2jYIUcFtaC/rLHaqFJ5NWSoMCUxEW1LwrIZHOVXKGfTd7MVoYzBODrvR2SAG8LQMqiuDnVKHX7igvMia42BY'
        b'cwx/JkuPPZG+hfLyhfklFWUqItOrh5LoIjRLb+tbzAdi54bKpnG6hPsCgNXiFb22fv3Ofu25GK712AURY5hjC7fRknoiNMhbfBqVxM+hPa7XkfgpdNp3ZnU5djt0uV3k'
        b'9AbG9FKHBDv7hqwW+8bpLVmNs9sjesV+vXZ+hCxuUDea44C9qEHe6ISzcmtR051ZkiK70awlop3TOqY9q3NEx8xe95Bu++7CU869buN67cYNSqWb3G/v0KBoyW3Pap3d'
        b'6zSy077XKahT3usY1msfxr4sbIlsXNBu3ziv134EpjiQogNwwNa+YfKmZbddyVIZ167unNyxrM81rFHwuYHS5xrUIHggxK1uyG2JaJH32Un67ZxaXdsjdnvg9uKw6eNt'
        b'3CZDNDYc2aLusxthGiZd6IxTRO727LUbyaYeGjakWNJn5/NAMLR401gRLYU41nDlmaYepiZRbgQAPBhrGgH3rIOIhSHtcTcc/PvFjq3m7T67rfC4NRCvFJHY8LbPwf+u'
        b'lXhbRl1GS9xNKy8STqtL25xxd0SQLq3Fr9fKu1/kPghZCAd4VUq5+vlg4onNusCUm9UzCaAYyr8nDKgCa63fz+ZjrfU+eEnVleJ806Wcp/9+uAkY7CdKclYD5GHUYA4U'
        b'ZtQRkUOtKeZ55GQGT8FZDwwnL/L4lMI1oQgohWdCMaMUvglFqORhTYJbzFEI1gsNqCPPXAeWM3kWOQAjDuGAWZxCoVZqNEUCk+oKDchjKTBo2oajFhgGEd9yDlVPqL95'
        b'sZCCIVyhOgsjGDKjYEhgAobMTGCPYKWZHgw9RX22CWioiwA/nZofR6GTr+QQ90C0BvgAHw/YwXrOzT88jaPZikNiT87uDyL2+uzteK2j6Uxi90Yf6h6sPrFxU2RkpVoc'
        b'pT3tNPtgeHFEUdb7WW/N+vDt9xo4udyigxFvVd6KLBxzbWNEvWNO5ajNU/t/w1/qM97p1Ut2R5LH3t334d6yq19M2nV8o3yU6KZ16t6/jUp9ULZ41LHmcZO87rydbiOx'
        b'7WgTvfeH9Ve2S7GCYg1mzPU+6zxKakG93aLRHvMUE5EPD6LLnCq4Fx2gr60K4U6DrxrWXd7g6t2PjwdSTWP6DHgpGB2Bb5r40kVVovU0bTy6kkePKrB5oyuzpnBgHdqA'
        b'9tEtJrRmiizYDG4KlbFm0wOccPi6grVbbVmaAuvxyrQtRWYBV8NtcJsZsHTioFp4Eu6knjpz0ekMWJ+B1yS0JVgKj/AAzviMrTm3EtVKafHhWD/aiHO5AN/A0UJgFw8I'
        b'hBxXeIChGaAdy1fB+jCsQMGzE0KTyBkKspN1kIvWaOZTy+7CbJy6PixUmowuTk+TkeMP9Rx0oSj7P9ajVq821aPM8vPLlcvy86tt9VMgVE+gCxhR9IkWtdwMuHs2mN0W'
        b'ufaL3ZvTG9PbR98UB90WubdW9rt7tY1tHds+a9/8bofu3NN5F7N7/Cb1ucc1JBjiRh+O6YjZH3tTHH5b5G0gksc7zh4tM9uLep0ju6MumvU5T2rg9UsCGng7rPs9ffCX'
        b'Rb+PFH/Z9Hv74y+rfmf3BksTuWc5wC0q06iDSDt4RarKqgHh4gpNJdmoGBBoKtVKZeWAlbb8iWX42VYP0jcF9M/E8rGAiMan++WfJPp4/PFvLBi1ZgwziXkIyOdLiEYq'
        b'hvcIQsAxyzGDFS7GMME96ASvAaVg6B8WWuulTHoXMyDM1/tSSZkBnkZZVkxcQoCEHVphbJl8UaFCPrHaztAGA8Wa0a8Fq0Fnwsm0I2m0V39RTUpwTXDp/HwyAFJGvZj0'
        b'z5NaqJeQThxSARsc46G+AuKTbkfcfnkF1rMVMM83jP0LV8LWpBK5J+cfmf/LK7GArYRZPst2L1wFO5OBiD4ZeyR2aBWM1tYCwB47YXcd8Hr2/8ueAzddZe5/ntGMwITJ'
        b'trN2fxBNvSc7jJbat4C31R4VWFTD87DWGvapatGb6AIVmY5RRmmI2hKkHJNJSESO0Xqq0phs6VQ7GjpuEJnKKGLPJSC7RAhcPFoS2pJbk/ucA3rsAkwkBZ8Ox3DTn1pt'
        b'TY5grCDDNHxpDswTQ/63cuHLoSHKZ40CH9BhGcLFqzb5wwJMiKWKfJEyP3/AIj+fPR6Kw1b5+Uu08jL2DRVDWLKpKxYr1ZVVVNypVeSD8KJ6oaHWA9bkkIkcgxhlWVl+'
        b'vpSHpwRLMD1z8mQfcJJRzhE7dLUBAn1P3meTVq4H9y3AJCaB6Y8c/T3X1trjwQjg7N3rPa7PKUY3DQv/Xo+oPlG0LuE2pkrG9znH6hJvO3r2eo3pcxyrm3rX2vERh2sd'
        b'+JALbJxoiA6IlnXROOeuSU2SJstCBcACnZhXSpbXFrh+EPNZ6r8fRuOB3mn/BC0qGIIOZ4JuLv7fFv9vp/+2Jt8qTjFH/zzo/2Oco3p4R9GmP8GaGMQZjgfaYQjHW29u'
        b'RIg8cjKYIEmF4JjZUf0WDEWcfIUQU81NqGaUaoGpliZUIaVaYaq1CdWcUm0w1daEakGpdphqb0K1pFQHTBWZUK0oVYypjiZUa9waCywVnNYL82ye9I4CI99jzgY0TFts'
        b'hRG2iwkWtqX5ua4HSluFG85Rb5vPsxvUx7bH3A1lKUbifIivOFfhYdJj9jQfT1wvL5N6OVCqN6ZKTKiiwXnj/83w/8JiQuEd8zHUQRGAATZHf5STjJONzrbYXDHCpFQx'
        b'zd8X5+9nkr9jFde8WBqIkX0RXSIfB1iYqvN6KnvoetAbsv2nwqrQAI9Mv+FmW3qRmQmT2gC9hCRnjHcKBx/IxqLaHAtrLq46YzyDSroO6ASY4WyoCDcbpDMIzQdpBDgs'
        b'NBHWZiuFehH+FNXUgPr5j7gXBjWK/CWVqypV8jJVNTljXqKUyPVdoMIASV5eRA6pP50kZrFcLV8kId0RI5miwqnUNGnS5Lh0SYVaIpdEyiq1i8uUOBP6orhCvUhSUTwk'
        b'I/KnZNMHksQhkslJ8VKSRWBcfHzG9PTc/PTpaZOnZOMXcekp+fEZCVOkocNmk4uLKZNXVuKslqnKyiSFSklRRflSLBqVCnJ2nlSjqEKNRdniinKFqnzBsLnQFsi1lRWL'
        b'5JWqInlZWVWoJK6cJas0ErqXi/PD7ZEsxX2mwNhmaHX03UP4JIbWi4QMNwEYuhcr1Aql+pmJ9fiNTa9/wH2UkyGLihg9WhKXmpkYJ4mUPpXrsG1iS5IEViwmlwrIy4bp'
        b'QEOhuDn6EnFo+Bq/SD4GxMXmZXj65fmx4InNjQ3/grwGLSFGHd6IX6zS6aF4BVqNLpPNrWVLQ0LRVrQ5ZSbSpdAD/t5wHw++McmOmosPjt0K7q2K5YDwgnJuxXygHY2J'
        b'8MIr5XSLKxPpiIIZhupwKCMnaSmbx/RE4l+YlpZEjjlvQvvM0flYyLqP719qBlJV7oB4QWeNGgO0wZg4ZkwG8VeMhK3BODmqS81KfKJbou1S2AVy4sxQcza8QjOpTMEC'
        b'YBWRPAWpv1llxhq2/VU8UDbaieyzp1YvCwJaGanpOk8ByToPtRuyRjpywD8H657ZiWhTqgBMQwcF6BRcK6WnAJ1E6KRmCdzPEC/rbaT6u1GLCjZE8DV8vIi8HzWwYnuE'
        b'zdpw8UbvDRbihNmpLm+srWtyvu8yMnQLd6TNJ+/wnC78qjyW1/woS3Vq31LVtTevrfpp2qUFtgWrmU2fcie4rfliz9xqTsPrXXdis6euyz79B6dJVxf+K67+zbySq581'
        b'vbXkYcef182f/Jm/eWPRxgdrzv1tetbCe+rsniOP5NEDK2fw05Mnnui73b38NwPo4uh/vt349awLR7ryNl676p7+uwdjvv7g8bj8ELfLRyb90fGfmpOfn933j6ZTk999'
        b'd5pMGhczo3PPdwt+v721aV5Fy1e+OV2r3/tu7drEWd/UVa4vs7ktzak9ZKO0uS1+tPHRd4/bCkduOPR2R1fH6L9UZHyv+VXEmMoNP9znnV6clHmgROrAHth5I9PJMiW5'
        b'FG2WpmllQWhTGAc4wlqeEDajTayr68GVq1hHV9Sdn2ri6WqPTj+SkCx2orqRKbABrQlNTgtJglvQNvb6BTd4llfOzaXeCgGvhgTLAtH5YqOLlxfaRo3rQnQ1KQVthYcz'
        b'E9Pw11ZDake0nosuatFeWovJM0KDQ9FZdOhpP5wIeOwR4RJfBl7CXLLVwgNtC0bkTgc2u7AU3KqtrI/sNHjKDG6DO9XUvoHafDDfZ8hgHXzDLYOykWUWB22dDijeT/Mu'
        b'hfW4MugK3EMrxEe7GHR5hBU16EerBUQVOFFE03HRbgZu1aJj1KjDsYwjKVMi0Ot0MvLRZQ6DriylHR4KdbBhsOHF1txzKrcSrYVXH5FDQnAbWguIZaVtEbmmg9y7wfYq'
        b'O7WD4Rk+2oCOjKVllWWiTpwb3INbvzWVwTVpY2CD8lVWZelAe6aSt7uyQ9NILc8zcDe8BA/Qt2WJfqSaacTJmOyh2yxA9RxuTG40m7YVtRPzTYYB4trES6dxp45YTvsu'
        b'qWY6SRuC+zddlsgDNrATnajgJiTaS23/m3sY5OyH0dpjavPBSocKg4H8fKyPsnI11EChGlUOw2pU882Bi297dJ9zYAPvtrP7HTe/9vl9btE94ujbIieyndGi3j7xnptf'
        b'j//kPrf4HnH8bZFbq6Z9zO6aziU3vMPvkDfj+9xie8Sx/U5uDdzbImL+n94Z3Z56UxRx19m9Ja5xWfOqxlU3nQP7vf1ueYf3eod3i7vlp5wv+l1ccimgz3tyK++uX2Cr'
        b'eQuvpajf2b25urG6qaaB1+/sccs5oNc5oJPXWXTTOZIWFdPnNr5HPB7Xrd/Ns03aKt0d3Bjf7+janN+Y35570zGoU3srbNqNsGn9bt5tslZZJ6/PTdYQbzA1eXjjL3PD'
        b'k94MNTKogXfTzrffQ0Jf6r8kfuTlbUlAv9j9tti7ndcn9iffwj6xlHwL+sQBD835Pg4k2n0r4OPfwNtpbaKP2rP6qI58EP+wYZW6nzfnPz3iZHQLTMxYJmb+NkDND08N'
        b'tzdRaYn72k+rwfevYpX2le8B/iAOBK+8rD1rvyAKnLGc+B/Zs/j5BGs+23qir77BejLriQGnJbctb1ce7eLH/rlGjErQA8ZzBvgQqFbKFbKK8rIqaSgujquoKPrF5h6c'
        b'npdfqCp64drOGVTb2btms7X1I7XFcPi5lf3FpjnaqQSXvnA15+MY6v3kPa1e8POB7X9eS9KX6nIcfuEaygd15Lxd89iahppC6F9a2fDnVLaUM5RmsIBysFSVsxYUOo9f'
        b'uDEKMgVtjI1pnXfLM+yGZ5hJ5z8Po/8v2kNtmRz1WaCXRi/clAVDmxJ1w5N1rX0c9iIqwv+iOetNmrPwZZpTOrQ5ETc8I9jmyH5eR/lvTIwuhlb8heu8iEzeU8AwecNz'
        b'qXaOK2i6DSLRM6qkjF5D98yK/r+0PC+Qch7vG6LLxRM9XCNRPSUZNUrlInpRHlb+qXo+JCG5PE9vk8hRlS/AfTBFq66QZMqrFinLKzWSONzmoapjIO4Y3D044dLRoZGh'
        b'4dLnK5fD7cbmShmqRmXAvROCKbzjCdHlSQw84oAOq868+w+ehpxauOLPIZZz1moe/ZelkYqIok3c6WcKHJVInCZflDcXnd3lemiE1+xRTu7rXMf2AbdvLFxOR0p5rOax'
        b'E3Who09QZKyAxZHcBB668IiY5uGbFa9izSARvSkcRjNAF1ALxaLwBDyRZ7zyDV1Fe9hL3y6NoD6icKdCmUJROtw/jjOfCUM7M55psjcj1nJyA4itgSv1BAoqyZYZ2Uos'
        b'sSSe+RMaJ/SIAvv9pLf8onv9ortzL8w+Nfs671fCt4TvVfb4Rff55TYk7EgjkG9F44oeO79fZMx/G9ANvMG1WWxqxp9n+ZJODSvZ2UhA2wu45RNPSQbPmP+FWz6ZMbVD'
        b'GDRHWcma97RllapF8kr92q3V6K1Z9M7KSrW8XCM3uXuysGpIRiSPGGoejSlIw3FwVvhLvkCpLvgZm8vQPSO9F/UY3jZwlomhtpSLSi3QjsHEWVjB3D6cMWWwKUU51sSY'
        b'As8mqP6W+g5H8wrJdUYqOTDQ0dSVtbWuQ+T5u8STxQqwLnSkpM3+rQz5h0vlBYFfhK75Zs2IxZdGtl9O/9Pyi6n+3AVuoDTIqvj6PSmHzqgIdLLSMsVUkw9HZ6kyj/Zl'
        b'PSL3by5C14KJZjmMWgnXwA5WtXQUPufklYkLmUZZmW8YIQrPql0NbDrk1aCDLTVk+vSIfG+7j2yv7HMPaUi47ezWEt1U1R65feUdr8Ae6dQ+r2k9LtOo6vKJna/pMQB2'
        b'4tQ9Y/Y8w///AzKJnl27asN0ImcBluDp5PIf3cHxktjWZnBlXnid3EggJLmLjKzttzzDb3iGm6zrLzp3QrEslJJCyIUbg440GJeGUvDEd6gZUMdpsqFhcJ7+7x5oILb/'
        b'VGYY279RKlSoVQtU5fJK3BqV4lnApVy5TL8GRoRGDGNhfbZZWcHabmlHGU5C4YJCJdnKJVqVWt+PChwqqpQolIWqSs2wpmwik3ANNBWLDIhehYGKvExTQTNgs2aHolip'
        b'1jzb0K0tYmsUPzkJQyDVEi3JD+PPQAJ3JGpDrXBZSZVyAoCeL9qGnnwSpmvJyhavQetT0tFm/Z2X6bKsxNDkNHJ+oi4sG14ESJealcjNlsKuJMn8QrV6pWq+OZi8wHZR'
        b'YII2AqcfNQZ1Ejut0f77JDWAp9FOYjHamQ3PMUvQOeHMZbCRHvzLHI12ojNW5MqHThDuAl+vRie15HQfA1ejjRob7YxE4lo0HelCZiAd2obqYVduYggpY3NSKtrEYHl6'
        b'QLocvuaHDuVyANoJL1iVFWSi9fO0xCDhgmq1xko1l5N6LTbmmTlTNsMMZK4SwAOur6jG/L6eoyHmjI6vi3d/EEOkce/+Jn8MbsRLmsNR/8PXpJuPuvocG/lu+qGQGamf'
        b'HO2odBaJ4gN6cttby2blRsT9pfBNh/SLt1P3pk6fdC5xdPiYx+BbjfyvH3/xjjhFvvHLkD9NjdzJvx37Rmix4LJLp6Dc4vRvZ41v7b0jeDQ7dnzqm02u7/1h9YMg17Fz'
        b'QLmf5LDsC6n5I3dA+mWZGi8uBjOdZXkJeo2DdmP800UNqAvnelgGkesE6lAL2oKFuUH6e8MzPHQyOJIaCjHYOh1ATznCrQK9CRZeQztZU+g11I5eSzGxSVrZFXpxHf2j'
        b'qfFVKZhkWFf4cJeJkRidCmLT69ApePQJBnuTYVAz3A1fW0nTR0fC3fpLoZxhg4nxFq6todbUJWHjqEnUYMA8I4UN8LwrdXNbFabA74z2y1qkg7tTZ/3cIbbVTy1UT4QG'
        b'uUtq0FIw6BVdqPbqF6oCK+Lz/ApBcDXba+54BfUEz+jzmtnjMtNonWuIJ4fecrr9LoScCrnp/gpdvuKvF/VKk/q8kntckvtFTjgHd++2ca3jbrmH9bqHdfNuuo+i8dL7'
        b'vDJ6XDIGZSbt9L3pHkpfT7oe1WtcCvWmPfK109zUcZZdEI0i/NmrIvWbHbQs3hmyLA7qizrG5FROhhXDeBD/WY+X9Rh5TTASHLKM+I+Marx8LJhfeGXsIBrkEWDQICOo'
        b'BeKJKH+esvsf6LrFrP8Uj9w08MJVPTC4quOHFfTx0+Of3j0dptJS7gBvkVpZPCDQqBaUKxUD5niJ0qrVWFks4plU1crQnmr8sdPcsNtPV3ah0ZmE0VnTi8M4OptiK7rO'
        b'8/A6b9zTX8E3H7SK4zDfZEXnreTr1/mnqIPW+dbnrvPs1fQsbKdLpqn+/OydftIF7IJpSGs8xvzsTVvaYWwqmgR3NqHJia0hVBIvLydqulz/rrAUL/3DrvnEnwAvwzkZ'
        b'Y0eHR1BPArLLryBGFqzBP7N44zjFSKaWyRdIlpUo9X4KuMGkzU9iGBr1rOLLKyqHKUatxA0p18RI4p7Whwr0zfkZ0GA83moEDRbp2ngcHgs3o52DUQPS4bUqEbWS5Wp6'
        b'IqZm65EAE+kAm2ATOpOCziQDf3TABu2Cx10o+ED71PKUUFlQMtoCm1YEs5mwORgzT0yeHpgso5eKYj0KHfS0IocyV1K9bO1ser1iyaaygqC37SayelkEOozXySd6GWxG'
        b'B010M1lyWo7pLnd9jjleCDcGaWNwWstlQaiexsDK3TZ0rCY4iUCOYAJCNptscSeGJKeGJsmCBADVS62WFKFdWiKGY2HjqkFgKAnWVYUQGJORE4gXOqx2hUhlyXxQjQ6b'
        b'wy3wBLom5dIbZucth4doyVyQreRNZPC62opBDF1mT8O26cFs6jTiEd6qjuS8iq7CN7RENnkJ4flgdBF2J6exPRnMAFEAF+1Ogc2qQy7v8DTEJM751+92fxCF0U2UEdno'
        b'cc3U9lKnkCOOp+oXnLIPbzWXR2JwszDAfXMb3PN3zoxfm8/89dp7FqPbS4vX/7VME33uWOCfTleqteqTxWsHPmbE8q/vre36yxdrjxSsPWr3l3sffPFu5Y+ln8oELTbt'
        b'pe+GzL8TFH7no41feG1MH91u/c+L3y5TH+j+GKOiL+9t/vPqruteH71ltccVhBXKOOPfxcCH9MRi1IhWp1BUwCmEjbCTiRgHdY+IvgW3oaNouwH2DII8q6Ix6IEHclgn'
        b'9S3o5GwCnrrIsBkAFEFPp+Fxus9ZshQeTklKC8IwlQOEsL5qBgeuQbWogXWk3w1P+uqxTw5sH7RBfnIle9NTF1wL17JZV86hp5Dnwz0U1oyOJwNSl0HPii1FGwVlnBHw'
        b'DR+ac6Ibngn19sEhGImyF96G4NEK42IAuxZdYCt/Hh7GMKoebZsLL5hs03JjQtAaqdV/tLFKFoGhu6qWBAPoJUy1yBQY6IkUHg0AFh4VWhMz2NjtY++4jewJyOxzy+oR'
        b'Z5GLKmK3x7YnHE7tSL3lN+aG3xj6OqXPLbVHnGqy63rHZNcVp2odT40BN0Qh9MW0PrfEHnEi2W8tbi+6KQq67RnUObrPM7JhKksruSkK6/f0bZvTOmf3vIap/SJX1nF2'
        b'd+oNUSDNYlKfW1yPOI7scXpI+r38bnmF9nqF9nmF9/sEPTDjSR0eAp6PiO5vWgAXj+aaxpqeQcYGWxZb/ZF8/Il8/Bn8kj3NJ1vZg3c19SjsEQEGw3X2YQP++ifGXynW'
        b'DBNMdjaDXxZ/vS4IBScsx/0y/KV3jRca6vTCwOa9wVZ8H7K04oWHLrTGldnUbC/lEX/iLk46Lm+q1Em9iqRdTT7WAPaQh6KiKD+f7gKryQ0FdOt5gFuoKnrm/vOAmWE/'
        b'i5hRqRlowHqQtYViYBP0/IimMjTW/n9zMtP+qclnwgwbAfVjZjvTlTBAE/FkWA8e8DjWdt8IgY1ja1QHv6Ooy69L0+Md1eMWfSnqfe5tN88u7qn4R1zGZtzdqDH9MRO/'
        b'50Zb+z8E5IOPifd5OPSgjAFij9t2Af3i8Y/4HPEEXcIDARC537Yb2S+OwRRRrC4eU/Rx4kiceIZGcva+bRfUL07AJOepjG6aPlbY4Fguktt2Uf3iKZjkMo3RJWKSk9dt'
        b'u4h+cTwmOU1hdFOf5DWV5JWI8/pWKLT2/0ZMm9bOawm+aT3yW465dTDxug64T0IPxMDT/7ZdeE9kPJuVJ84qje0NUYcvTvAdx9Faok+AQw9CDM2aRpqVxNB26UlZhJSD'
        b'SWwGvh2aruhTwp6R497KvWmd/D3Hy9rvEcAfJLsU5j55fjDRUOsxpNbj6qaxjuBkVXbixGpS01ndmQEWUIe2VXPQVrjfd8ivBgA644gnuMNgT3AFJ4+n4ObxVSBPoODl'
        b'meH/hQp+nrlCkGehMCM+1DNBN594F+s9xRnqZWx3TGj0Zw7DkN1SZ1fMVZibeBYTP2trvVe3ldGz2IZSrTHVxoRqS6m2mGpnQiWl2Sjt9YcEzagLsK3OvliosH/if20s'
        b'z4HENtbW7piD0WubqBIkvX0xXyEaJqUIly1e/+RZTH72ppijcFwvzHPE7WKoV7iTwnk9yHNWuOBPF+Lvneeqj+eG37op3DHFXeGBPz2IF3eep06AU3rhd146gEPeOOSt'
        b'kOA3Evrsg599FCPw8wh9Pr6Y4qvwwxQ/PcUfU/z14ZE4PFIfDsDhAH04EIcDaY5SHJLSUBAOBdFQMA4F68xxKASHQnRCHJLhkEwRTo9fkvOioevN80KreFjiRgwI4hZR'
        b'h+8jg1A5EaHsC9bnm/15LaxwkB8MWaCWE02DVROKqowOxU+57Q72IFfjDBYpK1VFEnIwQ85uphSx2g4mEAUG58naOsuqJBXlrEoynMog5QwI8pfKy7TKAfN8Qy0GuFOm'
        b'Z6c/ji2prFwcExa2bNmyUGVRYahSq65YLMdfYZpKeaUmjDwXL8dq2pOQTCFXlVWFLl9URi79i0/NHOAmTp86wE1KyB7gJmfOHuCmZM8c4E6fNmtqF2eAzxYsNJQ7yI5t'
        b'9J/1Y4gdGy92HI3V8Aseu71VY/yhNAWzEOsRGrsaTil3aGwDq2psKvkGmoJTw6nG2pLpT6/V8WsYw/MKRsGtYZYCtV8No+Ap+LQ8ptQMDPlTcI21EBCganiqxoKkmk/u'
        b'MyK5leO8FWZsmGxmPympBuQbtX5cf0sw5M9QfxzTeGa4Sog1c/PP84fTzJ/2vtfz4hPn+6cTPEvfpaPFattyNg9KeY4JnB3WGOrfnpMhi46MGGPK6gqspCcVE+VXolms'
        b'LFIVq5SKkGFVZFUlUagxyDL42dOSDcYVdlphnV2tKtQ+Q8mOIa9jChTKYjlGEkZWL8Bau6qohOSuYvsJTxh9OXgSDG3bl4SjHjuqyunu/5PWBPhrAgaY0AEm/Esigr/8'
        b'Cf895oaGh6dLzQbsni6W7FjLyxaXyAcsZpCWTFGrK9QDfM3iMlWlmoNHcYCvXYynsprLkGvhWEBLjk6qyfHFp4EJYQOJiYGQetzZsuNsdLj7HUElOwDrXynGa36/t+8t'
        b'7+he7+iGRALvlzdNaI+7IfLvnHVLNqFXNuGm7BUKx2MvLu81wnoX95Ypuy0a+P0ipxb/xth+sWtLTntcF7dzysmUrpSL3L6Q2IvZvSGT+gLjev3iej0n94onN065i6NN'
        b'b0xvmHLby79dubscY3fLfh/pYa8Orz6fiAbeTpv/9Pgj7bNngVxDTxgw7reDnLjm7Jpjsv9mytiUvaoWKyUFmG2KMPgsC01gvwsKQtUHf2mNi1nnGu5L1PiHQTWev4s9'
        b'LvrYnXobDj+xBlWNY6ha+nOq9jxZWcob+s7S6OLEpaw5IJRr8umZnAGhcvniinJl+TNPoz7dwH8Q5nRjG6hoK20tveUV0esV0ecVdcsrthf/82SPpz4uoj6B2kWFSjUZ'
        b'Hv24SBaXyYuIP5G8UlKmlGsqJZHSUMl0jZKKh0KtqqxSpirH46jGpSqwModnt1xRqsURSYTBuQzuOuMyRG+IExp/5g8Yf+bPQn8BAzNoQ/U/9UoqlnI+/2o4cT59MdFx'
        b'WFGuXF5UIi9foJSoKalQTvaLK1jnIxxLLlmsrliqIo5FhVWEOCQz4pq0WImRQzweLDXugsny8oV0D1RTWYE1MCp4y19IyOoFrKFK+bRKBWQUtFSosiKcyHrj3iceBXIA'
        b'ahgHEPKLpcrKkoonKCZEolHh1UqfDUlGvMlMj1E9q436jGLIb57GFOgB1jCeJM+1vxZWVJBfUZMUmxp6tXQoFE8Nw7DLzzKlGguXpRgdyQuJW9wzTL4/4+Rlk06P1qBL'
        b'aK00WJaYFEKsaCkziTWUOFxtTsmYHpgckiSrWiQAixyE6JoZukB/P9PCnhwKQN3oXFZgsoz8bN624HR4Du3LlqFDHCCDXdHT+Au8hFqyczmVj/ZoQtPgWdicjHYuEzgA'
        b'W9jMDYUHYQt7smcj2iM3tZIGpsuCUmTZAfCSIfMUPtZGhPAK35UeurVfEq2hV56nxaP1fMCH2xjUDa/Bw7S8OXBbZY5jGtyCdkxHW9DO6cRImsGgswE1U+kvkU2Ax5fj'
        b'CqFt6FwyH3BhCwNXz0KbtRJSmc1oK1qrSWRNpynwFNwBT/CAPa4xPIbaltPf+IIn4a5SDeka2I624gqsYNBxK9iVqzpqdpmnMSM37DeGrMhMS+FG2O19v/jM7s9WSiZ3'
        b'6NZeg/WbzH5as+BL/0yXiuPLd819g/9d0L91/06KOmc+uVCTFPn11aqHfzr608bwgPVfjI3dc0Qoj0t7X8j98vSu3JvTu/v+/k7fjFhHFOc/k/+W+qs/r1nz7qZD71sp'
        b'7mz7+uHmv6yvKXRRzS51nXfF6VDSicolxaWOr1X++IrXxt+AH9OObv/S/VbVVf7vI29c3n4wQ/QK+r8/VIxYsOEvaXemeq+aGbnun+ovtrpfPnIvsu6tz37reT39Uu/C'
        b'rWWjv89e9OXjPRby6hvXgw5dlFb9auuMnrTfdT3aJvroi9gLB0cs+kvG5VZFIfq72VdL/qo8XVvUrLLf+61l/99tYy5ONHvHQWrPbju/7jWS3mNvPgPVmwGejIHH4Wvw'
        b'NN0XhkfgeVQfLEOb0FEVqgtLRFu4wGoqVwBfy6WplSNiYH2YDG1AR9EmBvDCGHgG7YEXWcPrZbQ1Jzg5benEVPzKh4F70TZYx5bajs7DM8Ssm4a2w1NmQMDjCL3hDnoU'
        b'yTPbPIVUyT0gBadzZuA+tCGZ7qRbmLs+ZVIeARuMG+kcdJGtdR08yASjTrNQaVCg/gd1bdFpbhXqWEoLqPBCO1OSQorhm+T3dOm1lM2u7G9RXoDN8DTNHx6Aq3FCXjoD'
        b'u83M6UGqArTBl1h7k0JCYV0YmZXzYDfOQiLhofPWuNXkWr9Jr05OwbN0Djqtn6hwSxiZqQIQhN7go7VwA24mMTDDE7Zy2k64E+1JIZsXdQywVBDb9wa0gXWN3IWaOSkZ'
        b'aD/qlDGAs5SJswqm9YxGF1GT6a02HDyn9lQtXkb9MtPRGrQrJS0FrRmXkhaK6kJS4JYMapsOglv58GSGklq/PeF6eBrVp8Pj2f4hAsBLYODVBPSa1O6/bk8jHwbBN9ig'
        b'7chK1vzBi0m1hx41DPuW2rgT2fND93PtgL1zs2WjZY/HqJt2o/udPJsrGivaiw6XdJT0OYXdcorudYrucxrdwO23c2q2arTq8Yzsjr9pN/a2k2uLb1MJpju7NS9vXN5u'
        b'2eccoj+DNLIn4JU+t0k94kn9Hn63PGS9HrJORfeYrkUX8/o8Em95pPV6pPV5ZDSY9/sGHB7XMW7/+AbuTTtJv4v7LZegXpcgDJtdvRoE/W4eDWb9HpK21NbUTqdPPcIb'
        b'EjAUb0/p9Q7HSNx9RHt0p1nHhD73CEx39miuaqxqd+lzDupU3HCO7PfxbxEQ/7opLYGNGYYLbcZ+Ig65bw08I+7bALFnO/eWJLJXEnlDFNkvjWyIvykeSY4WTb0t8Wuf'
        b'fjivI2//3E8lkQ2J/c7e7ctuOIf2e/i0B7Zk4KxbBffNgE/UfSFw8WowPTRkqaZ3eb/8sSB6uc3TB4Ji8SA9fyx/MpjQyRVgr9oyjD256OZlbvxXkx/HxOiTqEuDvGWN'
        b'W6LUPY5v/CFSPr3tFxjv+yUmBcF/zWO2BKO5T4dDc/EsHNGfi2eVDwJOMTogCMOI6fWgjiA8jV7tHQoe9HvNT6HCpzDg8JhvKBTJHYov5QTDDIJcBgRUQaAZ2WivIuBx'
        b'aM3kRSWsr9si5aIKdRX1CyjWqlkUpaG/U//zcOxpq8Jg7cfkbEelXL0Aq/CGmM/dWS83bq2zDGnYWTfAXgJWlRpTG90vcNSje92/l1gByfxI8pMOIbOc9feh/mDtAd62'
        b'qSREj29H2bDEe5rzQLLyW8y2k5b0j/qjA/tLsXut0TWNNTyXZ80BDNoK0HG0FyOyaeRdfVpUylMg0LCHr8dFJ1aihlziOTcT4zOyK//EFw+vANVedjHjl6lmnD3I1fwB'
        b'Z5jx0U1t4wTya6cb9p5VWTo6NuVJ1vxwCfi6l4XsWe21+iA3+bwwIvdLWLz0bZ/qpDudUyYnnU744B+/O1N0rcm2vcFqT99336e0X89VN2eOB7+JkK151P+J+/WEQ5/f'
        b'2+jaM/Ob4tCilg9R+pTP/mIZ0RSeE5GyVxc098gXf039q1fUOMsFmRWamcd/dW/bsVXJb4/424J58MYn7l+1lTge5R70+teRNWZ9R//xeJrZd9kBN+Ou9QZE3Vnd9n9r'
        b'/3pnqe/jD9zF55MfzJyy3GGDtv6jRRfvXP7y321Fd76RCzzCI3NfXS6VV/6Ds/BvMRMUh6U2dNVHXZU2wbLA6bOf/IjFa6MpGqlB9YoUY/fxgO2MqApumVDxyB+/NIcn'
        b'5pr0uH41R8fhTsOKng5PsQU0W2B0gP9bOYvchU3uwV4wn+KWqRYcvBwPWovhnhGG5ViL2ileygtFe8kW8kTYoYclcCtqov57fvAQ2hVsuCn+VWcesISnOehohAd7H/Yx'
        b'MUZU9K5sdKqUA+hl2UL9Broz3AfPsZAJXg7XIxrUDt9gD4cftHcnmAY1ZDyBNQZMEwebH5G7AzzQWagjaojTCuKSnjGoOzjoNNzE5IcJ4YEUuJa9+e6c3zKiMsCLNlKM'
        b'oQSlHC8feJLefe8IO2CbfsMeHkYXTHfsUdNICuBKl8PXg0PSsNqh/3VZW9gED0u4alifLzV/OehhDkwupNOfIdFrhtU2+pVJ/0xxRZAeVyjsgYdf28TWiX3uweSqfPeW'
        b'yrYVrStuiEL63b0bUvpdPG65BPe6BOOl3smruayxrKm8gXvb2cP4orPoZElXydHSGy5j+z2821JaU3andcbd8JB1+14IPBV4Mfu0jECDpNak3SmdfreCxvfifx7jLxbd'
        b'8IjrF7vcEof2ikNvisNxhm0WrdQS50yOtLRPuSGS6s+sdE7pdY6groizeubk35pT0ov/SUv6vFQ9Liqy2k/p9Dsp65L1+o3t9RjbMIU0Q3uD/O6Td7u21znEkLSoV1rU'
        b'56XocVGwiQI7Mno9onB8F882m1ab9srD1R3V3RP6XOIa+LedPVuU7bP6nEN77EJNrx5nTZfUavkCl4Sy144PuiU0naCFp8YkkKPHB8TzP82eYTwevKSLo/oz8KzLznaA'
        b'Z9vIaoY96rcUqF0UzJPdBBxLMDSWcSdAQMyACs7LxTcvlnLTH3P8VY95/qGRxVIe7dMBq/zyiny9/UozwJUXaqgtbqjdbcAu3+jYxm74VDsbLMRPvUgmvUucqVaDu3ru'
        b'SrjlN6oX/xONwnx+wLddcbi0o3R/WK97RI844q67z4H4Tt5Jiy6L/Rm97lE9Yvbg5aDtHOMPHAjJdg6nGbBbKHVcw46lemkN84wuH4ZKNnjUWcMPh9oD58QfSh8+pydb'
        b'POXSSuOGjoKp4exmFJzh0+ym20HPeMPba/ZkGwnHEg6NtQLT6ZDy06udjBhvkUqDh6GohKKjam6MJKDaLIAa4wIGmAApnx1xkWrR4jJVkaoyn50MGlVFOZ0kA+a5VYvZ'
        b'nQSWB9jTagN8CiUHhOxeIX452OVaYjy0NmCTv1itxChLmU+TVDsaGGQQOYuwB2k7FojEp0fZPuMmln9YVVnZuLJTfNKzy/OG82jMJ7fco264R/X7SQ+ndaR1+12QnZL1'
        b'+U1qnfLHEcEDYWMuiq95XvF8j/+xza9t7nMZ2SxymaXvbOY+YDxnM3c9fIhwxMLG2aPBauj2gNE2loo/dmIIryDmV+b5Q6wf0GFYhgzoXj7dTuClVwvZdgcGVPMCQvAo'
        b'cAKkanLUQcphpZnx/KHkybUWuIfU9C5Tw64LS5jL0Ru2f1gDbodFdkdfiDkVc3zVdd6vrJF1j3N6j1360MYZj7GRSUia9jLCqJijFxjk9wwemxFhIfHXsPUfKhXM8sk1'
        b'g7jiNsaK0+d8jtEgT37xJeFwckdyN++C9SnrHt+Jvc4Te+wmsvUe9iTiVKAXocyQ6oEaRsEY5vwKZvg21DALOcY2DDCxXRw1ucKAZWv9IMxmDIOgb4ogP7+M3CxibWwJ'
        b'eSzEUR76sg0xLsJTuqP6XMbgxZO916MdL5jSHjvp/7ZFbnrPLDwqnNgJ6qKfa4tycFvwY/HwbYnucxn7pC3T2Yvdn9OW14FRAmMpVscxSuDoZ/DZsJJuYSAAyxm1K/MM'
        b'PsSphqGSVDnPWlwZ9i31XmMZlvekf5460fhEauG+Ui4Z1FfkkRSuSQRPSylPn7a81rzOUSfHd43v9Rz9DRY2k5l+H//Dnh2e3f4XQk+F9vpMwuLIMZ65+3MdatxVI5Ui'
        b'zME2wMp4tQRFQM8Z4vLBQ0weF3P0Pod4iN2920e1TuhxDuyxC/zfsmaCyWSb+LOcuWDwLCOPJIpayejdBv9n9ZyrR0JkCk38+Sm0YHD/ksdlpKIqY0WHlbrEI5EsKT+/'
        b'oDy5KsH6Z5YHsn80aHlgCa9y9L/4QLjU2X3IHbLD92S5voL/SV+SUyTUyMWtIWviMPu7hjyMnBHcxX0ihikYGTQ/rZnB89PQerzEyBWKQUsMfV5JpFk02/ZhRDOr4ODZ'
        b'RwynrHqRe3hex7w+56geu6ihvWMcvpHgeXxmMnT6jfjq53ERWdnZ2pus7JSwjlSfuoQCetKssaZ9St/Pid7/yshZvPTIydRVLzFaGm3hYEDw/zH3HgBRZNn+cFUnYgMS'
        b'bKAJTRKa0ICAASNIDg0SzAot3SiKgB3MzqijYyMGFAOIAUwDjgGzo86o9+5O2tndRpwF2Zm3+t6G9zYyM05Y3+7sd++t6gSNozj7vr+huupW1a1z8zn3/M45+PpNPHDW'
        b'2xzhppqPYGve6YfrnkzxG3+o5hlKLGqeJOBY2iTgLKp5H/9mPvbj1abrEcUY3GKeU/d4C9um4CHQmh4uHnYxw9itF651YlPG7XeR12qzEbeuwp4/VEqLccO31RI2eXLU'
        b'Hit01VbtQa5340rAgXKt1rfPxFKDp/T/YOwwrs/V23+oBRnaLVqQJOzHnen15y8XFlyKdXMFvdLgcXpuIzu9VCPjoRXLDK0Xb1CnsjKtWqdSVq1CFeNuqhhT2iE8r+RT'
        b'gxkXP0mvX2y3X2wXv0vT4zcJCUbiwOPJLckd/G5xjMEz5rGfBK8dHV7dfrLG9EfioLYwRhbrEY83eI7/v69oznMrmvOSc9gzTuxL17Qz4pira2vVTFV7mKranHgcD6Ln'
        b'1rW2x2+yua69usUyg6fMWNdh6Jn/J+pa8Ny6Frz0ehH2slVtR1zIW89S+PotPNB32RzoJgn+9+Y64aM64ZnqJOJF6kRr2mSyXbYNtLl0L/7sAtI/iY8MHqk1W/tz7LPk'
        b'Ge7zn6nkkDkT1a0AdTxUNWgtJqzUAWt+SmCu8X7+6qW11SpsDrxCUVWjVFlu3LCIT1P9O5aVMfmiJhhlagJj0kXczbFhzbDdfE2P3/TG9M9QTw59K7I9skPVI8bONn8b'
        b'HtOhvLisc9nNsJ7w6ThgVHrzxEd+wW1JzA5yj98EfDURPbSicwUaKkhy8ps6QNFeU58TTSKV+iH+2mmYzjxoiX3+pgyJL7PEqk+S65t4gvVlawOtjdrj61rWNS/vSLw4'
        b'pXNKj2iiwW3iKxF/nv+DxC99EeLrajVWxJPr23hAtdqUX0wDqsiCRK3piWGIMsHOf3BiIEDPYuv++hzyFYutySfX7+Ge6Geq+yMVTH9rre3QXtzYubFHNMXgNuXHEs0w'
        b'j6LW/QCZVTVaKzLJ9X0Oa+5FyPRtTsSzf9PrBrcxPxZtlT9ImwNZqBSMr1yLpQun/MRKbPTDHkhb5vUMs1Fg6hdtFGtIgSZQvL+mdjL3DiXHvGeNJ2IlV8ljmN51FoRv'
        b'HGb71OZuO6deYJqmuS8ySZIm48v/B58/CyZQ3aqaJZK62tUM2Dc+jjEV0NXV1WKf+884cbJ+Oh5Npb7GXtlvv1KnqNFWrVMx/ZPxO9Vvh3JaUqXV9HNVa+oGLWVm31PM'
        b'hGqufkKBVfWzKR/g6i9kqr/Pw7d55r5JBCqf3eObY/DMeTQaOxuu6MhsX9EdkNgzOqmRy3LkrIw7o8u/x3vacJx5J+GsvTD5sYPMKdXPWNI01bVaHFzFG5fZxRo8g64r'
        b'K1UV2qpVTJRexAdVKzTaMgar0c8r06mr1UW4Dmbjg9kw0zSs++1NGiUnAo5gILQEuENUDeoSfCAL2EJ8KMcH7E5UvRQfluMD8QeJPd6p8X6zehU+YFFb/Ro+bMGHrfiA'
        b'RQg19lmi3okPjfiAjSfVzfhwGB+OEjrxoR0fTuLDOVw//+44nEOsPVmdJMb6r2OtvT7BYk8tzVh7CnhCtwFHyidOn/04MNTg7NfnH6iX9/kHoYM4UJ/X5zFTn9YnTkdn'
        b'weEG58D/FHq2pLeHtC8xiGXveDwUTvmG4yEciy0Ypw7gsy8iKS//R24RjPmkVzqtT2ftNaP6POOxvWYCMdfEKZMHOPToQvopn+tdhI04HSkXUZ/Q+1tOmDDgSwodcLY+'
        b'+CAa4KHLL1BLuoj6EQUVD4XB2H4yFt8MYZ9AlwPT0ROjv+DwhIkklM4APvva2UHo/3Q0LSygvxTQwmlfCjjCyC/tOcKor+15wqgvnWmh1Jz21J4WRjwVcIWJXzrS6NJ4'
        b'JvsaVVUifjjqa4FAOOFrN/PBTjj1qTstTH4qYA9T8SEcH6TfCvjCxAEKHRhLTowfBjvAFtiigTvhrlhwEFwlBp323hzdRnfbQSDxPvoBvrUpJ/GNxtXzKnHgR3s2BA93'
        b'K6XkneMPCsEjQKl2Fql2FoF5zKn2FoF5zKkOFoF5zKmOFoF5zKlOFoF5zKnOFoF5zKlCi8A85lQXkjoapYosUpmgO94o1cci1Y2k+qJUsUUqE1jHD6X6W6QygXUCUGqg'
        b'RaoHSZWg1CCLVCZITjBKDbFI9SKpoSg1zCJ1NEkdg1LDLVJFJDUCpUotUr1JaiRKjbJI9SGp0Sg1xiLVl6TKUGqsRaqYpMah1HiLVD+SOhalJlik+pPURJSaZJHKGKeO'
        b'I8ap47FxqnICOgYpJ2LD1LXJiM+b1O+KHeKUmF33PemiB+EAjX7rLB5iowMNegwbPhArjApFDV4JF6tYKz5tFUHhGW0lSEAZo30fNpdg4G4qa2AeCwe0No/AW5sWfgbL'
        b'8bqrYHz6KGsrdHgjy5SzVW61amOGVVpGz8y8akTXzUjJL0ljcygfxvjQ6iK7krX1UEgWE604yo4BRVr6QYxmPmksK2sEq1WrcIVY5afQEJtbTByxwFiFclJUV0t0WLSq'
        b'Xos5DSsHi1YvW3F8mIXBoKWvpiPe7wAPM1RqO8xUYVxVvb2OHo6x0ppYJ9vwBBObxVVSG7hlJmmVXPGsrvhWVwKrKzurK3urKwerK6NxO2UJdkXpTlZPOVtdCa2uXExX'
        b'XHTlanXPzepqlNWVu9WVh9WVp9WVl9XVaKsrkdWVt9WVj9WVr9WV2OrKz+rK3+oqwOoq0HSFmNkyiemKRldBVk8GG682cJZlUkP+GOs6jVqoYncbeBv5G3jLsoc+q+Qb'
        b'+4VGoETPEM0NryZ4mKcFxqfVo5RYEs0Z+kwrvYHXSh/lbuRp8010cjeYdl40LtoCU3526ItWltHamZbvbOAbA6bR1M4lPNyTHDZwl5nq1Pyn3hQiTcPJwdAYLmH47eXq'
        b'0yjvZ0nM1DZkInz+VEd0rBn9dFk/p6zsWdjgt5cqsMmZ2WqNmOlKpf3ORYhzq1rB2t0KGMgvE+6QW1al7OeX6VRaNXasz7j06HdlYlSbfJKpT+Aa7sQHHK9aXYsPxNH7'
        b'zymCpLFyyYcETQbbjXKs06mRJK9CnyDsuB3BXGkV/YKyFZol5NPLsTc4fpmK+SG+4YTG18pIiFm7soqlGJdMon4qtDoNkgnUKgwGUlTjSBY1lbWIYlKhVZVVFcRDABID'
        b'mGXAdFuxQmsuUL9nWXVthaLa2qstDvO6FKOpNYg+Mg2jbMgvE/61369sUJUjCRpNseyzfHS+QtPviIhUazXY7wERaPrtULvgNul3STG2DNMSdhqVFt+QOjIWB3jw9wuW'
        b'r0YkaCxcCNuQ4BimHU9ozIxtZtZJLF3RIDKNMXV/g0W5Y7RJAattS2lZbZBN7Q6cSgw+FvX4lhk8yz4T+WN0U1tFjyiykYexnrz99qaALSQmS194FA7YEmoK6iKxCupi'
        b'jNty0sEquovxNzCEhBmWBFuGIGYTA4KJwTSbaP0TJsXvBxsfZX9w1Jf9LsZnjISFRuDfINN1dBz+lbK0PQ4IIZ8JDWOeMj4dIn1rcvvkM1P35jamNYfhnfBpLdM6Eh6K'
        b'Y/sCg9tKWta18Pp8/I8HtgR2eH7qI+uLjLkYfTb6HZ4hcEoz7zNizuJJXGNGG2JKDLPnd8fM7wlYYPBe8JmnuDmtLbSD/6mnbMCVCh37hRvlHdwW+lZ0e3SX4KFovMFt'
        b'vEE03hx6+RU8IakBPby1tffgvmG0SnbnWrlqNodgmFxCbDFqlpudFEYzzpq1tawPSGzxqkS8TlXlWsTBWHAWr2A5Tja02qkRlMSLS1lGVhljHaYGWzmsqNWavVSSSImv'
        b'ElSlYyREemMizU41raPTDKURx3EcuctP9fmRkCi2UY+WEWoG0chGYBxxx31ucJphiQzARJp9eEltBKf5sem8PRI6g6zp/HWKhInoqdEtZh3lENccmDjWPooNHvLcQhBx'
        b'ismIoJmx9FOHXsOSC4lOYCMciUxSbE6rrFLhD7KiBModPWC2njKxEhpJJFupkdHotEpLfo1hZiIJbjeSCdMS+Qrd9JOR1GwErtlfmGo2cahn+WHGVErq7JRYdEh/hcGP'
        b'qIUjmW2jrImebOX+F/tuVy22dgQ8mPgZRelpsWnpqSUjJJ7FNPxkJMTLuJYeOhYcXsAUooh0RguGlDXxM3oWGWR7JpOkEc/0jKVd9WrFWg3r5FZSo1qiwFu6r1S0n46k'
        b'aGOth2mkcZgaje0sSscyqZKI4lmz572SP2b1+yMhNcl6eg4ny3Rt7XIs3DNOgJHMX1dXiz1vIRlCx7gNHvm8hwj8YCR0TsB0fmHU4j1zLTF5NBo5PezQ+3Ak9EzC9ATQ'
        b'VivGCjTtKZaoLMZb3dK1Gmz3KSlMyZajabL6FSjtpNUfjYTSqTZa2Exhde0SawIlEblF6Rmv1hM/HgmdKdZ0Mta0NcoYbW0M+jGzjZKI9JETyEQiUf9sJASmWRPob9Pz'
        b'tiQif+TUsXPOJyOhLtOa8zaHpQtizJKRiFmDHfaw8w3jb72wtKjw1Zr65yOhNcd6MLuTdYuI56yjolcaJYaRkJRv3biRg1chvAOATb7weURqQUFutjyzJH3OSBdOdirs'
        b'HgmphZjUx6ba+9tgUq03MWSSDDSFZ6oQ8TVEANOYNoltRYNHC9Hs7IwSHNM9WpI5a0a0pLAoOz9FXlCSEi3BBc5NnyuNJvZWGbjDL2XzHC63tIJ8NLMw2WWk5GfnzWXO'
        b'i0tTLS9LilLkxSkzSrILyLPoC2TjenWVBhvJ11UrcIAZxrf8q9T3g5HU9yzrkSV74M+Yaz4LtljXmY0iZlgpyHSl0KA8XmVo/WIkxM61HlrjBncOZvNLJkkxO2zLlmcU'
        b'oGZOk2fixR737VdaTn85ErIXYLKDTWSLSgizymzPoT6lxJ259hXELTQt/GokdJUNWubZqAXE/yFDlcqsbrHcsniV+b9nJJQutp4V/JkaNK5K2EGGBCuUbDAhJrTLBtoE'
        b'tbdBn+akbSTLGhpjKoaBBw5jb7eG1jgP9w7xCsfZQNtGvqBUG9ahxg31DVSZ5ZOOQ59Ui22n2y5zGf/595cJh6ahJ12GphqVAfRzh/2zSUWMmw2seDNJOoy0ZlYB2pbm'
        b'ZFJ79X3c/v+LizkoWjXZZ8dewdX/RAcp1yKkNdkFxvVnMmhwWqLSGrfx14kHdziLmyr0mgZvT3+3icK2Xxv3bcS7nRNaJjwQT+nwvOjT6dOVdiPrUpYhYsoDcc49zw98'
        b'7vs0pj0KjepI6wq9Ib0kvVlyd8E7C3pCc0wBJFEW8Uk3/C/5N/OOC1uED71lfZ7eh/L35vd6JnR7JnSl9SZmdCdmPPTMHBRv0qpP4z+kT+MudIhaS7wDyksY+7KhQwtD'
        b'bYYOLaPJUS1eAEisJWy38hw8WxE1/PBWu9nG5hr1WpZY2yWDzaWkHHUfSunnYU2BDZtUe1aHUGarEMwdNW4r1hLSQ9TrEYrdF2CL4+hucXQPAWl/JhI3pzataXR9zt5x'
        b'zvOKOPplYv2ybUJUWcby8Um3sm10W62qQeWzoZUgN1bj4kmGKV6veGy3eKzBc2yfyJuUTS4NsYUTI4oPguzqdxmkvCJDhYws86D6B8WOp36hte5KwKqu7FhuW52OHxKw'
        b'ais+o7XiEaUVD+usSOCFfmcrhZWA1VfxiO7JZZBmyslSMSVgNVr2ZoUWo0xysVZYqcUctq+rJfgshEMQ68PiuazDi6mv40EyGJvRjbVB2D0swXI5CN2+HS0T+n2hpKmA'
        b'McQfftFTPieghNbLze72J2NH+lOf75Lf4hnWH/007I8+hfHIT5IGODyv2Kd8gSgOpbkwfvP7PHOw0/w8Wp+PHmOTMAn+JUwS9tIvHeDQXhOf8rmjk/UZX9gbPzAdfyDV'
        b'7PIfUTEFUzGNUEFe7PMMw+79w4l3fxZmhunySmFgZkNfY1PG4ZQJlikJOCWJpPiFkvgC2OG+30R9nvljEfhjkeRj7FuYRs9UJgYBqeABDtdrJv2Uzw8ownXsTIlDHrmh'
        b'KXMCelCcrM81Z5aHM5MzgQlYOFwMhsPFEjicjcKwDYgJDUjSy58ywQtood+XAq5Q8pUjV+jDIMqwd59EeJfntEpY5yzNAZtj4M4oeZ4Mu8qBe7hU5FI+6IKN4MyQyLP4'
        b'z1c4Si8G2ZqxZVupeVwOpcK4MtNMOI9PUrgWKQKSwrNIsVPy0bv2ek4lrRRstZ/noLRD147Y9XwlR2mPUpzIPQd05oyRZvOEa50Qg+jc7zGoX+dVaayDiXGMM+BUZgak'
        b'rXgNDroyzZcYtVtmmvOWYK7ENLWvZdl7HtnM6XcoU+pYzKkDtv9QVFdp1/YHD1YRY2rKLFFGGqNlYiSHgE+Nmdgb8zDaKEos/Fv72cjV5Ox6E55AA5kJlNWCBkmJTpT9'
        b'GRNhDlE7cjXXP57D29qkzxQEFvO32Oxw5ASwctUEzghJ2I5JWP1KJLAy0sSRkqAfngQTFyIjJLyoGYOZwwjEa0KybcrwejFs/yH8xQ6uycQU8xFpjKFMjyjO4Bb3Y5oA'
        b'IOIIjcMYAZBFbQjTylJKOIVdmFAMmDJaKvSKZd1iWY8o1uAW+yKc5JIf5CSHqSiGm2zETejPMTahpccfk8nM95RtozeNJUyONgOMbHuOsN3wJNBDBHrDtrxmQ+Yib7gS'
        b'oy4bshfxK+SkNQPgLOB76A3noW8scx2aZjaVpZk5kit/FmO5cbECux5fbPYwHz6ojsOtH1fWqhjX2Yx/IBJAxOjtkTBHSFqaQ7MTKOHP1JPw2WR8IMYRuJchTq6uTlWj'
        b'NDoGcrL4BPPosPZ9XIVSOYRbJR0B3WjCfRBHcCJ9MKgtquP1h6Jpn/mGGEKLe3xLDJ4lfR4BvR4h3R4hbdq31ravfeAR1yce0yuO6hZHMYY/D8ST+8T47sZ2dJ5IrClK'
        b'enxLDZ6lfW6evW4h3W4hvW6R3W6RHZM+dRv/nCGIAYLmIThoXrDyyDFksAXjweZjq5CEkT+CiymkzEOtaa3BTTKUFJOHUYxgsp660qg9dAVnCVXBWejNeIGyaU1joy/v'
        b'5ez05aH3NloYYVdwaJKy2mid1c/V6Faox+CWtPBH0U9rrcyy+dparaLadkHJreO4oDjuPJ78fC+l9YgnXkrrWNmccjyrJeu4vFXeldYtntgjSja4Jf/9gXgiWZ13+Mvs'
        b'5VKXwYKI2bqEdE1zrzTx7AwLn8VhG0CdzyEi/SDuHbeviXcfhxvKFo+zEVOOQZGIf/9SwBNKEQvp6dftl9DjkahPeyQK7JZM6hFN1mdZnH7Jo4Xx2LYgDpsz+H0tsBNO'
        b'wOYHQV+hy0kMT4gDja1yFLMsIeYHYVeekSWEV2B9tIym0uB5uzxwOtyKLzTiVb/6T7wd5WvJF6K/HPKXe4Q/j4ujyigFSjulvdJB6ah0UjorhejMRemqdFOOOuIyj6fn'
        b'6PmI73NH3B4f8YB8vT0O6KR31/tU2uHQTISDtCPBmIwcpD1J8dpKKUefE1nZINix+H+RlQ2CHYv/F1nZINix+H+RlQ2CHYv/F1nZINix+H+RlQ2CHYv/N6e6MvRXcpWh'
        b'iHI38oysCo1alZtxD+EUvZue54aec2eDOY1C5adJKCd3coYDOXk4MCG0uMSFr8AUB1eod0G140bqx0PvqffSj9aL9N6VXsqIrQ7YJmE21WWH/o8+JzXF64nD30K1yVVG'
        b'WYTi8jI9a38u2vJZEgzK/NzotZFoGMb3O+N+aUS699OF/XSBlN/PyUzt52Sn93PSi9FvST9nRlY/NzVT3s9Ny83t52amFvZzs4vRWVYROszIyujnygvQWWEeeqSoAB2K'
        b'0/GNeblq7K0evZFdKHXp56Rm9nPSctVFeHrnZKO8s4r6OXnZ/Rx5QT+nMK+fU4R+i9PVs8gDM+ahB0oRMdlDjFsJoJ1xkcGEFj5EEZ/IFBIxeMQjMtfKIzLPwcrfsWVQ'
        b'YZp6jfsaj/WIPCjV5BEZG0MPkaDItGnym8uT6/BYhm114CYeelpYXyCDu/LhrqiZ5vCyJLCrLJu4Bc2Lzs6fmYWGYw52qgo6edRUd/gG3OIKrsLzq6r+/PE9riYJZVk+'
        b'ZkXrx2OPtjddVXY2te9v19/eupd2LPKePeNR/s6wvLju6FkCZ8NHvGKfT+61CKhGiX0A1SjlkvCeq8vgdifQGb0aHMgyxi8dBW9xwfkJ4CRxrRoHLsEr3vA6bCiAOxAl'
        b'2BV7K2eN4DXi9RVcgxdhJ2gAe+Ce3BiwB/3dBbvsKKfRHLgdHoKNSBiytX+Bq2UQqNXTsqsZEa14hGnwhEViffpTnqLm6G6PMWQ5LujxLTR4FlqiWY3+apil0c4Mu1Xj'
        b'gEG2fHYSW0k2IuYPEXMZT8jYxw+ORa7wp+nAlw2DeUAQRp12iuNWWDJrLsa+guMuHrAzxsLeztvO3y7Yboe6riPqujw0D/D1dmhuYGYDAQlm51bpQrozmhvrnUzd2YF0'
        b'Z3uL7uxg0XHtX3Ngu/OgVMtwLdbd2RQ3xtSdA+UkunFOHDiaaww8iHpvTIwMh0gmEYZRt8oqLVxdC94EW7NAB5eCu+ucYCPcBI/qsLvT1zTLTK/Cm6AD9/WCmFmsR+cc'
        b'uAutSHtyZ0fA+tn2aMDwKPAOuOgknKElbqU3uQsoZRHqoZJy59r5IkqHm9mOA/ZrhIxL6RUxFDwP9sLN5PG3JjhQT7kS3NbO+1Ar6KLxYNwOz6VaRUg2eUgm3qXtqLnF'
        b'2MOv3dricST0R6AK3snNzs+NhruktAJcpZzkHHgG7pukwzPOZLB1TVQWdkQNd4bApoS4OLC1PJcKBte44D1ehQ5Lf+Ak7CpFK+7uLDT2Sy1cWEfIYiKgPiI3NhLHga6V'
        b'2sMrBb6kUPSaZbmwITsvVkAJYZNAxHEBRxhTAeJK2xUcVEbhuo4RULPgZgG4xRkHDs5m3Gw3w1sqchOcHFdaaEfZr+Q4OgbqxqF7ufAyvFNs9XX87ZkRcE80rC+MYGjM'
        b'rMrH74EjoMlxNtyaqMO2LuAOfINfjCiIkIGLVAQ8ZkeiRnvCdydpVsHLPIoGLfCMA4XZiVRdCrrFh0dBB7yrQZW9K1oGd+NAL3Xo0ZII1MwN0dH5pVlwd4HRzbc5kiU8'
        b'xXWGe6aDJh22XRFJ4M1c3AuY21K4Iw8V2iOTC4/GwSMkOMqiYqg3VS+Vxaeccjng4Hp/HfbxDLav0hXjiC6wAXSWIOJvgKumcpNPU1SBm12dG7ylw2JoPNgfA5tm4ijI'
        b'sINaR+V7w+M6Mu3dAbfQ1HelAOyHl1avgldB/Wp4WYsaSMxBRT8qJTUcAd9eoUHJqEtHz4rIiUG9Bs3lzIfY6s0H9fCN0kJUCtAEbzpS4GClDvtBgscX4jUA1Q2qq4ZY'
        b'uKc4IgJNz/pYOVtR8HwK00PBJtDpQOUodNhIRwv2+zshYq9q4I2VYNdqtfNKeB3VWwLqxde5YOvsYtJR3cBpHPg5B5xE/T4/RoYqnE+5gwNccAHsA1fIgBlfwKfOzUOt'
        b'Pb28unpdKMU0/LtLyzQr+dSEONS2FNihlVU9DfHgarA+/A+pTw6UTKkFcW7XPDjxgfLvxkyf/7BzYWOyrvZ1+4awkhBdltuyt7u0k745y/1P0UD4+lN9obqsbdtDf/ne'
        b'7W//+ot3Yr/Pj+bo6tqu3si6fKJ/377/cte+/o/vTz3OavVeXnD10Ml3z+0XNfz1fpOqp3isxnXi2d9fkIAA93avGu9lNVRxNJg7+QQnsLnaM+K30m2q8sAO6emmzF/e'
        b'S6tamfmhWDglpzDpl91FDh/eD74cMeqvz3Z+evqdn6b94f1Y/YcHvk/aVTVmmmBya1neV8H6sx3S31/jv1d9eNzZ18SB/2je8SzoX17C+dLrgu/mR06o27BuUvjC0ke/'
        b'UHx9IL3vg7PavIZPViz7vjU9t/f+7r8MtHc9GLfs+KkTNzw+9e8+sLEn/Hrpb2M+PyBPTou9PivUL7hHkrnxlsc/7x6lxv95822/SKeHTdcDN7VeE6WApG1n7ox9p2T1'
        b'b6+tnfUwf6Dyvf715/XOu6Unfu9Qrxj4U3fR+schD47y71xJ+PynobPGv7Gu/3Kc3dWHU+7dLT/c1P27uX/8/vHOryo3Z5Sm3bIrzEh8cDhT//6zT9JPlf7XTunvexw7'
        b'9pe5/HdG+9/pfE/w99LNhzeMDXnyZ5/uhCvB35b5vt164j8+1Lwt/41D67+ov/jtdPj7F9IQJoDLbnjG1ckfdOI5xJpBCIZ72VA0s+ElNIbB7lh5TBYPvjGTcgIXOfB0'
        b'DLz4FNumSVLAO8Qb+qJKU4x04gt9kQtxlw53FqIx3bDaReiohtc08LpWKIA35ZTnSm4xbKp7ihcel+mgNbeABIgBDc50Cti9mDiNd0CrCWJN8pAYg9aXDtjBhe/RoBVu'
        b'TiSfXlMlRpQh7koK9Vm80kWIsgsceBK2gb3k9fnZY0GD6yp4vQ5e0wkFlJMoUstZCu7C/cTHeyZ8yz4qJgI7089cy7jT3w6bSc7TwK3piFGLTvaJlMrIjElR3hLeohiw'
        b'j3EPfx1uBfpcWb6A4qwFu8B5ejLsdCcfjcJMHBrYO9A8hKguW86bSINL4C1wg3GxfxXud85FUxt6c9GMdXQsbAedT2PxHbR2gl2aVc4rdfCGK9gBdrraC51glyPscl2F'
        b'Rju8vnolKkQ+T4Dqc2syE4WoFXbMj4qBu/LiaYqOEMyl4TlwG/F2+KYMTQvHYEMWOI+YhI1wM7xKZyBKDhLWrtAN1APE9DWAc1l4mtojy8nnogmK8gXXeKsjQAthICXp'
        b'oA0/tRst1agd7OA1sJ1yms6BB0tR/8BPoL5QhL3vox6wAXQaZ5vReTwh3DWTsJiwFVxLBA2xuI/xKbgXHhGUc4LBe7NJTYP62nB0k50v+eA2PEE5FXDggaRkEowoackG'
        b'nD3qfwWYYUAfQCu5gAqEp8EOeJUHr0SAN0hHhfUrwDH2UdJVKRfQUebKTYNtuSRYEDzjBq+TWE+78mhqbaYgmyOCXVomhsCmhX74XZS9PK8AMbl78ujCjZQvPMJbiepz'
        b'Hykq3FqOGOCGAvP65VIMW8XcfHATXiU0KPLgYfSALAaxOrlccBFsRl1yBwe+VQKOk84BT3EU6IGcaLgPXs+GuxHvNYGzGJyAt55iDbGfK5fcRXeAvoD5SjbqniFwT2QE'
        b'H7Xg7RiGL99SDTejJ+XRoD6WXTn4qE5uwFMiPh/umMoU6si8YFSoi/BkgUVoCHdwgYu65yZw6OkE9FAdqsijeJQQmSUOHDaKLah77IllNhCMuwdRaB3bFeIIjteC+qc4'
        b'ulogPL7B9G6BCu6yfBd0Qn2eVEDlUXbgMmiRPsUMkkgANpFVb0+UCgk69aiQWfmotLtjc1ExdjNqq0xwyQ7s8QMHyAQCTqbmMT0kdD0wviCgRlNcxHGA+n+7Yw2jhd5g'
        b'xxpEs+M1SJJgVDpErrnKYeKXVvtjU7HwjvEPRQlEsmEDlD4WBWBvkA9FEWQLMaPHN9PgmflEFEiCncZ2B8b2BiZ0ByZ0Zd7Iu5R3z/1ekCEx7Z6qJzDvxYOgPhH59wWG'
        b'dyR1B8Y9CJB3KW+suLTiXnb3OPmDgApDUUVjJnYyvLBlYa+/rNtf1rH64obODTdTb840xE67J+rxz27MeOzjf9y/xb/XJ7LbJ7JjXI/P2EbBI5E/+dL0e+O6jY5k+gLD'
        b'sG+qjvCusT2B4xqdWY/ETRsaeX0eouZVbUtaXu/2kH3uG/qgePaDuWWGsPIeX4XBU/HYw6fXI7TbI7St9KFHFCps7uVckntOj2+uwTP3sV8wdmDXtr7HL6HR4ZGHX5vo'
        b'Lb92v47FHSsNQfE3fbqDUlGm/WFRHSUX53bO7Vr7MCZlgEuPmYF9tIvTsI92L3QUUJ6BbUi4lHWtvrH+8nryhbR7q7rD8nt85QZP+ROPgLZJD8fldYfksWWb1B0m7/Et'
        b'MHgWPPYIalvQ7RGPMomIxoEkTm7oDR/fHT6+N3xKd/iUnvBpjWmfeoY+Do9qTHuIfgPDiGVjcESHuDs4CZ27mqwkmTtGe0XWGpNx9Ny6gDwSEv5WcnvyW1Pbp/aGjO8O'
        b'Gd8TMhE/LOmThJOH2SxYC8gx4YxNZmgsk6NFpFpWc0gsNvHXnR8Fj2nT9YZP6w6f9iBccS/zg7z7eb1p87vT5hsWlPekKXqCFzfyDrhaiNijWJdERstiHlYAqLE3IXUC'
        b'3qRxqlBoTUbCAk3FUtUK1YvGz7AYZXg4lbN/TGPtBwfZDSyvYxdn/0Kj7NvlSGAvoL+l8PELcnwJ6V2DWeJTgkTqqtM07ogBhJ00tnEmlTCcitG6JKaQuVbQ0ZFbth1/'
        b'jnLT9pefWYNWIzB20eQ7gymKhI3bIIlQqxTKmNqa6rXSV44o3O9UxtpslFUpX47kf1qDgmMe+DOOdJ9F27IEqdKYy2NZgFeJhnz/OZp02zTjXUsLs6SAEmL/ga0/TAZh'
        b'PwZtUtwBK3Ta2srKl6OPy7PqBrHELECnjUEZSbDrAbPNCqaZGBO/MsHEQNjrpXusAJNqxgVHElxwVSULBF6BUeCozVU12HGK8kerVucyi5nu5Qh2wAS7GLXOjFEIRi8v'
        b'wbHlTEZoP0ptBr10x3TGxJnR3+HDB+m2JtHy6ybdeTnFwIlY51RcsnWJlZumWIQbabJ1SVlsXdIWm5TUazS7dTkodfity6E78QK5bWeYizB1NImJjR0hGaNgm7QCrxwF'
        b'G8dNxF4SbcZUzrCMxWwNH9ZINEtrddVKrGNHc21VZRU29l2iwKBjm3lpWR9MkhnVKgW2zJCkEQ8juEOxwZqJDRdeJqvQeGXsDapsB3vWqEgQx/LyErVOhZbfKmakRy6v'
        b'rdHWogWgYnmkpLpqsVqBMse2K8aw0DYzw/YX2iFzG3rNiNJkAisyNjFrLUxNbObGWMuYCMxQVGsQhUNDGhKnR5adwjRoTJ2CK6+aWHuV0mCJ80j4960fTzja3hTUQHvw'
        b'EupeK71OUZO+QCxjipQmEodiaSwjcLDihrvMJHDALnAaDTE34xBjMQe8yiUq7bpQqzGmqaguIxWIRhuuD81UGX6KyAb4fazzqJZQfhLspMLgaanaYCFm1kwU0aqUG7Hi'
        b'auxd9cW+6MZjFRt/30Q9XSihafeXVWw0CiRUm1MU17aj6Eoy7tnopHyiuqBZPRx25WzSqr1yZNIX08NNwjdmwnOsmGmSMbHqoT4vMicanC1htsVxApLmwQG8Jw/eBvVO'
        b'E/1WV221q+WQgG3Xm+a0fvz5Gax7eyfrTlM86i6emkNxsE+6822foHNjMsa8KW+Ted9tkh5zOHN23+YEIXWu2GHeopNSLtnQKYNt8N3BVCBJFxz2HCLszgfHyA4APAje'
        b'TR0UIToWNMI3jSGis8RkB2AUuAWbmU6aBLYNFosng2MvoplD3VbzQt1Ww3bbCKbbfqGWUN7+baW9YVMehE35LCDSEJXTE5Br8M59NCayI+nk8sa0AwVWmjrSnYXPEwxY'
        b'TZ3Zq6kavFgHR7T5Gjs4DrG3EnVwn5eJroerXcohupgS+N7EXLIRWQZ38Vxp8BY8LCPKD3Bx9srcKDm6sxA08xJwkPDbQF8159e/4xMt7c+Wh7V+PPno5qb2N6S74rdd'
        b'2nZy9Id/LP/r9hPl2RVyBedL7+Xey7yLm/8Qx0+oQ+OlN9jhodcOpnZ+AAdu6efVVP51o23XC2mlAKaV+nj2T+dJ7EdFfePJHTV2wJ4KCutQdpt9txq/PmyLWH9dDXF7'
        b'DPNdV2MLoO9+Mx+1gMPLtADGIdtetMspRslPwh5TlZx/w7K95IcnFbR6eP6PM0eDdTCzMt9p/Tjx6Ob69qZ2MiWcq9xquO98ZNb6GGrFYV7yhY1oEcG6U7h7+lzz3hiz'
        b'MQbemP3cfTXYli3lWLQAh4xWC3jlYMU1wVWSRhexQ3N6EOUttgGtNLa2jYXF3NoWevLhPxdksZx8/fpLLifPaet/O4M2pKWpIS3Nk5dUXRMF8DR4NnDwS25dcQezCvv2'
        b'JvhTju0c76fdRvjpIA6AgZ8O3qhgcKekfRyY9hnIQO3j95JL/XPyDrVc29ODXrIx7nD+32mMobGo0bAL/e5bDgGIfBj0N8K0bc3+3V7aMdnncrN33PTRUWf6lnkLPxV/'
        b'cu8Rh/psA39qwQG09uK6nAm3gf2wIRrvnvOmg7OzaXDNLZrseIOdMo/BA/N5o7IJvAmOx8A9RJmREwevR5HYv1ipexa028PbHLDXPshGlyDQ7SF7VwSzTbqEhOkST/Nw'
        b'lzDitnv9xnX7jevxm2Dh3f/Fe8pzPhlu2VNyR9RTLGEtfsbmws4FD3jZhLVgcJsLcVZshLcJ9B4E/GYCuel99L56O70YSYyU3k/vrw+o9DNBXoQ/GuRlSG8bCnmZLCcs'
        b'AOILgZ4FZKTJKYzHcGcagIEGNPnDY05qeA1ec12ZB9/GejmMDHADpzjwFrzB1eE4mPkejgQZkIU6SgE4NwQeAN6FWyJMKBHUk+Cba5zANdShpAKG3WiAR8BZDdbuU7AR'
        b'3ApHvTY/ndzyg51yeEUnwCgCJ3CWAnvBm/A0wYOA7bB5hhO8zsfxq8EFeIMC7aBRTnT7xfC0TIPxvVCfHE2BN5NFOlx+7xWVTrgPwYvgXDoFmkGLL5PVDQ+4U4Mj0MF9'
        b'WGVJgR3wbdhKsANrXO0o59ATAkpSHp0jX00R7Ax6dS/YB6/ASzi3k4jt3UOBg7mwjUGqvAfeyTIWB25fg4oDd4ItOsw6BYPtoJNU16Bagl0po7RqeLU4KwprUxkcRSNo'
        b'dtg4L4k404ZNqJ5uJMDGhDgeRcPjqNDHKbgJ6kGHDjPgXBFoIfgfcN3dCAEinrcxmqlwNjyQkFNsR5XCZgG8poO3dXgIwV3wPVifgM6m58ZT8dPKSe3BrXn+EGPHEd93'
        b'K5aKVeZXf/evf/1LPIdH2U84zMEoitWLxJRuBh6N4NCEXNNnoD4rGkseu2JzSiNgfRaaaFrgzuIIKdwzOys7H0sB+aiXgOtFuHiCGuHCOHiD5AMP8VB1NsAGy+dwl0LT'
        b'U31sQT4SWN5lKsoS14Q709vgtjO8LAXbddhQSvo6eFuI3tkrBJvi7PlwUyk8JoC7S4QZ7r72k4vAbdQbj8GL6UvWOFSKVjrCO4LV9mCHA3gP7CpwBl3wDXgqDr67XhoI'
        b'9ZNk8LAAHJohBVemJsIWb9BcUKnDtrerUQ1h/eRmIRVvzwVdpeDyPHhAAOrhdnAgEmxFctAesLtEXPUa6ICbxODdZcFicAPsRKLL9cp17uvhVm58BKJiVyC8lOaRDxrn'
        b'q3FPI91trkpMJ2Zst6PcyjcuCgmmyAiDDeNAM2zIB+cKoT4blT0W1hcSXJoJSAPOZ8nz87PzQf1rSLpDo8GpAr4BGLzYx6FZVOOaiXZI4lh2d6E/pZOjxKUS2IIL0eJA'
        b'SZzRyaxFy8E+cA4N63Y6HmyBpycloOZoKgfXkHB5uDQcnpyHSN7kVQLejQBbVEC/BAl8N+2Wgjtua8X2pG97wpNutqjMisnhu3th2CfolKJ/qCuSEeYAbyRXlEhpHdY3'
        b'V41eiZsfLUxwd7aDJhrNF6h1Rfa8OLgthIi5qPvfBjcWiHJjcvKLs4igmY3haVGzCNLU1Od3Z0Xn5MmyYyJR59ghda6Cu5IIDmluqc/zUEgEggSugVYWhgQachBpREcx'
        b'PgfDsKaDTTTFAbvpGUH5OhwzszBrWlQWqrKd+Uzfj83JjilioIJDkGhZSA6vg5fhXoCGfmFRzCwOtbbEde1EuEWHvfYmasS5RAOePZPFDLJifFZeASmjbKb9Knh9ZlZO'
        b'vjw6Rk5AiXicsfizKdmz68jMDHcWjQKns8Fx0vCL13Ap3hxUD1S589vpWsTJkdlLBG6Jcxm1PXwzikvZwy4O0CegkYh7NzwAdnsVF0jz0YjIjs4unW0DCUmhvn4WbEJN'
        b'ug/uXCBBg/MmOJUVBO5mBSWAizwKFXSzA7zjDlrQ33MEp8UHR+AWeGXyBnjF1cEeXnaFV7QrdTTlqeGiRcOeYNSS7OKL8TzFRfPbufzlFDw32U6HTbdW20tzpTH54CrZ'
        b'1ZAjqiKs2RcutVBiD7aMma4jMJ4jo+AbxWBXCdxVmg8Ow3M0xY+kwWG0QOwlLbpw6hynVS6TeDT60EE0hQhBA1kPk/h4JyUPJU9AY+gOEmtcwJtMlocy4Lu5ZjCE0zxw'
        b'ZhwHXgBvgBMErAeuLIowgne4aFY9GUqDVnDVkxRszQr4DobBgFNCjIShY+FZBVnfiuD19bABI9f4FC8AXvegwQk/TzIgwLF8uC+XRQeCszzK2Q3uA4e4XqiuL+hwPEBw'
        b'Bu4qQlV9CXVrKdlBic7GaA4muzFgE78StLgwkRguwPPZpnkanN1Ao1Zv5oAD40czK2DXkpAoE7bCeUmCHdc1CZ4hlTLdY3ku6giIQB5sge/S4Hg8PKHDAA801b2NluGG'
        b'GDmGkKSAdynBQo4X3AvvkCqBzeDERthAsDa8cWhpbaNBJxoQzBePJ8EOPJTRvQAFOEqDk3AzmsTJ8voGvIg3k5i7U8FdcI1GfUxfToCBaBo9DZuN1KJeiocvbAMn+VQQ'
        b'aOI7lMQRdGqmTIjGen2BHK299bGmGvJ0tqgjOdhsh5boy6hbYILHRwE9BkJJY8DuOgHlMJGDvnQGvMf0gD2osDfRInVVA6/YURx4HlwEZ+kYtBIfqxrXMo2r8UBL5s+W'
        b'Ptg2K7/g19PdPr/m/0F2lt7Be9L07+q+i9xWlON0/uz11KzSX76rXnD6j2c+vp/i2f716RtPDE5nn4WAPX/uu+Q/6Xb7xOoja2srf7PzeO/frzw7NP2Qx9+hbuL7ET0Z'
        b'/d8lhxp+++YnPt8rb0nGh9Zd/NncY5vXzxn77S9ClWkf9N6NiNrmubZ028GJ20aDT8Y5JJXEiz/dNubp9z5B9zW//fnP7sz80t87VZRYFJM4669/U5wK1Vamz4YZF5p2'
        b'GBrO3v+V/SeXlvn+z39t2LIhQ/jnxYIvb9z/ff62w1vh/B27f1+UmDhnoXeHTuL83qnyXxWPWb5m1N2tk1alSRsO//Nn0l1fgea/7pikVu28pfY88OcG97K1dbU5mvvC'
        b'fJ2uKmf5Y+hy7tuxv+Rnzgx//Ifk+r+uiJn96198/bhMsWjpf/xv86fulTucfz3x+1TFB9uy/9LGe23p5V+9O80wJypxW+cf4752LWvdtW3MdwW/e//ZwfBJH9z9aqHs'
        b'/W+jfvO7ohTdkgdiTehf1TXBNWNTvnV4r/UPH3y84PdTrvesl+RvCPvgW47dnT/Jd3xu2PKzWfdb1XMP1X6ocXjtH3+Y+27R8cn3M+c8ec9v9pWVf7vgt3FB7v/6/fUP'
        b'+1c/TDpz69Hj22O3n3/LOeeeQ+Sli/5zfj75L4pTwl/E+C/b3yV8eO0tw7WWL/92dPPRh32/WDbH+xEnXNPYFHdw7JtCl2mNf6oM0Aoasn+xeNzm/q8Vv/rprPsrb3d8'
        b'mXXhzNSG+/nrvpq7esPoLXt2J32wdM5o1blV0X/43HPj9YUDP6//xPWPf1yzVChfsnx3wX/Jph3Yq53W95NHRz+a8Otsn5CQz7P/EnldfHdmdAZw7Du3cjao/zXX7g86'
        b'2ZW/T0p33Vv7x7jfnPyNw689fmf38Tft9X9K+PqTURML14/e+98Lv1tU7xf8ZUq9X9CX2fV3KHFvheI/HtxrS3tc1dszsPtP/736buao9Q4uF8IntDqpts0G4GvPBQvK'
        b'Ghwv1N6DX1e/f5e+tlvzzTebvz+j8Loi85q7418J4OP/6EyaKZ618n2h4klC18QH4Su/n7t37rY/1//k2PI/TtnmtWvuX2q+T78fW/ALx5n/zIn8zfd0wWmXa8c+l4YR'
        b'uJi4Dh6yRNdRTtMLaznwIOI4LhKwIA30oCm3IAZcAZcwOJJOWQbPPcXTJ7wbA1vJ/LljJjN/jolh8Hi7JsOTBI+ZrwP6AktA5vgkgriDLRKwxwiiBvt9+JQ9uMZZBc7D'
        b'BoJRKwH7qqym9Wy4A03rsNWXwOi0buCuxazumIQm9WmwngHztcPjXmawKEaKOi/jwNMl4BqRypPg1cmM9MwHF4CeEizjBEydzqAEL/uCvVGRMincEQ0uoJI4zMVTzVUp'
        b'g5vrgG9ERcnwWhdNwzsVlADs5sSgleYyU6Rt4GwkWr8j4Xl43gh0c53FrXYtekqWhdtgB4bCYWT4ngJLrjtNQAXm8hAbdwecYr50SAEuRREyKHgUHEVfOsdJQEJFKwP8'
        b'bHg9ncGMvgbrKQY02jKJbPcHhYLNGrDLfqUQXtZgzLirvdCI3ZyCPs7CN+E1AWKtT8wimqb58J0y3BSwE82d5k1892wuaJOBu+SZjZngPbToZfHAHqI/KCDg0VFwOxfs'
        b'LAPvMtDELWOXA8TC7YhdBt6LwdN6rh3lWsBdCvaDK6SvFaHVoiGqIBpJUg3krhN8T5zHgTfg0VjSAJHwJNjC8kAB4KSRB5KnkZ6YBa/DI8Y1D2wtREteQhZBGSJRuB4c'
        b'xVZGcCvYNQhFrIPnCRQVHEUc5Fkj+BKcq6Mw+lI17ym204j3zbG9H2NGEMLdXnbgcgLY8ZQsd2+i3LaAhqkBg/GrBLw6BjQQ6CjsdA+3CaeMjCgPQ/w9kkFvMTDodngW'
        b'nkWNnoPY6e2M5oVPucJN3Npx4DDpYePAcbQAN6BOw1SCUw1iaPQc2JrAJ/3CHXaCy+blWY9YnbdVcQzi97BjlJmh8YlA/Ex6LYOtPu6KOCgrfiYEvo3YmYuwi2iDnMB5'
        b'KdAvGp6ZWTqKFKDWD3EYDQS8CjdPYvGr1Gj4Js99CWgmu17xsCnPWMtIZnihna/jYnCHmW3eRDV4ITcvOxicRvNQER05tYYZtaeTw3KjI7LwkGubio3H3uasRX1qhzTi'
        b'34fK/L89EKWXpap5aKC1QcjQftdBkYkYtwSmHblBd8leoAuf2R4uCaIkocc3tGxgEKBddjfdewInYzhlwKH1+9b3iULaNnSLEj4LiDBI8z7U/nL9R+u7pfN6AuYbvOc/'
        b'jsgzeIb1hUa8ldee1xua1B2a1LW4a6UhdGJjfl9Y9FsL2hd0BXfFG8KSGuV9otAOlweicTi9rL3sYdi4mzJD3sLu5IV9YWO7lA/Ckm++ZphZ+mBaKflU1odTu6VzewLm'
        b'GbznPfbwaclsy2gteOARxQJOV3WHpff4Zhg8Mx75S9pGY3xmj7+s1z+p2z+pq6LHP7nRsc9jdHNkt0doX6CULRq3JzCxq6g7cEJjFjZRn9C0sW3lA1EE+V6hoXhht3Rh'
        b'T8Aig/eiPpE/Bsp2jOmNnNKN/omm3Iv4QHZfZphZ8jCVoU9umDm7d2Z5N/onLe8JUBi8FU88/JuXdPA7lG0bHnok4i+Mb9pg/MIAh/ZPp7/icgIz6AGK45OBAaKx47o9'
        b'oxrlbZmPxEldNQ/F6STrRT0BZQbvsici1BgPRRP6pHHNLn3BoS12j6VR6CwotjcoqTsoqSdofG/QlO6gKT1B0xpd+nyDjse0xLTGNto98g1rW9LjK0NnHqMbVzdNbgt5'
        b'4BFGKs5YZyj9tR6PMR3uxhot6vEtNngWP/EQscb7bWP3vUaoyegJyDR4Yw9sLes7Em+mPQxMeSBKIbdyewLyDN55zweyig5N3Te1bclbte21D8eM72N7VWDo8ddbXu9Y'
        b'fXF95/p7vA+E94XNrz8MlH8WHG2ImW9YpOpdVNWN/sVU9QQvM/gte+wdcNylxcUQPv+h9wLi1Kg9uWPpTe7DkMmPAqM6ss7m36TvhX4QdT8KZbI365FXYJt9R8hDL9mj'
        b'wOiOORgenIVD+y7tsH/oEd8XGH58Y8vG1tfRgz4hbVkdyoc+DE56fo/vAoPngifGoKZtq9/a0L6hq+RBUs7NhX3ioLaMlmkdmV2LvuLS3ul0Iw+VDj04uWVyt0c40zF7'
        b'fKcYPKc8xm7JUKWHELdk2JHD3rQn4gAmmG5nQoe2Nza1Oza1J2oGxkp790qTu6XJNyf0SNNQzn4ZdGMaRg97H5qyd0pb+gMPKQ6pktbnH9K2uGX+3ozH4mAM4OgVx3aL'
        b'YxvTnniH93mGfsn18HF/IhIP8NEv9ocVOmCHzgbsKdQx/A77DTjgK0fKR3Lc6bDTgBO+cjbeE+IrF/TO8YLDBQOu+MqNConsDR7/IHj8wCicozvlFzzgge94Uv5RD/yy'
        b'ulzu2Rlisx74zfpw9oc53w144adGU77BAyL8lDclDjweezh2wAen+1K+AQNifOaHz/zxWQA+C8RnEio4ZiAIvxVMSWMuOnc690akPohIHQjBd0Pxl8PQWSN/IBq90+sT'
        b'3e0T3esT1+0T1+XZ4zOOwMMf+aOLrjX3vHv8cxoz+txGH3Lc69ic1Bbx0C2qL3psI49xk9GW1u0m7XPzPOS819mYgqO8iPwanS00H4GM5uMwBtERjxHh+BBFEMiqNSZc'
        b'noXHhpeBH/9IywRm1YaAmG3ZDXxt8ugz3IoQiVU1WRSLbJ4ZRNPFBNlsfXwZfDP2EXNZkMKh7nOcUoRcKU1cXMhfAM9D67EDB8G/Bc+DEXOPODYQcymVWpVaUqGoriah'
        b'7jCKlw39h2qqCleRotoqAh4ThECpZKLaKCQ1qtVDMmUQohHl5YUrtNk1laiVFlfXViyXythohUYMnk6jqtRVYyDc2lqdZLWihuDPlFWrqpRDcWpWRFTVkAcridc/1tuN'
        b'SsO4wGEi7Uiwi3dJlVIzFMU2JCG5TqFWrJBgZ4XJkmyChUO9XFOFIwKi72BcnEJSodNoa1cw2ZqKlq0sL5diT9DDwgdR/RjrA59W1UhWjZeNRVWRiqpxNa5M7VKF1kSt'
        b'GaFoM0e2bCRMIYELMzhAlAEOWmhVRUZnQkvUtbo6EqnEZo6o6NqqCl21Qs0gHTV1qgqTD0aNJAK7XItGVYA+S5zsrq1DlypthUxKGmEYpCOuUK3K2C5suxOEeA2iWYcq'
        b'EuWPe91aY+sra4krozoc4NJWnlYNMLRNf0DB7Shn9v0aMuBmVuUIt8ADROkYq2KUjlgMiJgFdlra/YJjcJfJ9pcLtnLAcR0OggeOgYPgGKuHkdhzsarn1so4uN83IMsj'
        b'bOVGeLEIbAPnZ4D981OzteBt2A667KfIkfR0JtofHoHt8EgauB24Dpx1i1sHb5MNc87SbKqRogp9lpYvK3VWMARJoJ4mu5jFEdgoD1uZox8uvIHkyuBlPPj2ujnVJLKj'
        b'go81rWviZ5TnzZ9V1XfDna85ipIPh9OMT4uJDbSHMr5ix+m4M3HnK7d0Lfcpal7u/bH3jn9sejY37tPR2fu74NeXqE/rys92Lq4on/Nze8X4+FVjRy/XXlaurDg7X6jx'
        b'cB29+sv/mvUbfuKVrJ317U2dTaMqb3xU4Lj8upNB91nYlrreS0G327dcaq7fG8T3jvziSJzX0U+8ds4Nbv7mVNfsL8bGhSb8VHM/LdJnwnyqeF9Awed6qRMRqWPAIXBr'
        b'0O4MuAzOcuDBNeVEKpqC2mEba7ZKV4FbKQL45lNsGQ4PTpENgzCIhLtti1p1kwmuD24RwDMacB7eXp8lj4kwbuWPgo1c0AVvw5PMPsttuBVeNe7h8Cl4LpTZwznJoB/S'
        b'4d1C1irUO4siVqEK2Eyk0angTrjJJpR2gm9ngKMppDijUpOYnQ0XsI/Z2cidRaRLeCZRy+4oxURmISJMO0rgLtjO2OhdmjpmqDWpb6E3lsfHCp5iR5WVY6F+iDgOD4IL'
        b'jEiOuq0Atv8gGs4sZTlgrx1kLA9CpZnSiWSFQwtgyWpRmG3Jqo817kIsda8o8oEo8rcB4QMULZ1O96VmYB72Cy4tlWNjssACbEzmU0A/EQcijhDlhvjH1g1GW72k7sCk'
        b'nsDxzTzEtrfMaOO1ZndwDssRI9pW1uObZPBM6gsJPzG5I5Gx5iKewh4ghmdlt1vEr1jvjlZwycjnMTJD4ZJ87hB4nqkiTloCJGeE0bT3SwMk6X47tDCWoZXRtuM8wjTQ'
        b'Jnc8jDMerskZD/9Hc8aDmYbveDaYhmJVDRt7yzoEsE7DMBEqMo2jNSc9NXtGsUVY3+FWXtXiqgpNWUV1FcolmSDqjY7BK3FQnoqlMvKELB0fZ5DHhosWbJErW4vJxCQg'
        b'2mQTgIPxaVSEzFq1EiegNc3mmsNGPx6WBllGaV45iROhq6uuVSiNpTdWiM1McdgqU9wHvByyFj8aXZWWiUFsIsr2SviDVM2YUVIePdJXS0f8anbhSF9NmTNvxF9NSxv5'
        b'q6kjfXVO+tiRv5pQLhmGX3yBlxOHscrIriTsE8u9qZTRkki2+0damXZY254QaLdtdms4i5IMtYLEtTT34ZcxHpmNGXRmVliVIIuzGi3E6IWJbsYMJ/TBVVWKkdVUakmp'
        b'DRKSGZfiGmaOYehghluV8gd4yqEwNi85YduaEgWUs/IUj5KU55WGRlFE5z5r3SqNEwfehWewpzIKtMDmOHJDumw1vBIXF8enOPbwZjYFj/lWE0U3aHGEm9Dfd6PkMoz0'
        b'OEjnUow3oAJ4bR08BFqj5DkcdGMLPQE2gwsESgDOTrcHO9Oi5Nn4FT09OdlOymOyOxSzDl6BV1zhZT7FTfbypadwy4meef2iQnSjSwtvoCUBdo6DB+gguB12EvLKwHvg'
        b'Zins0oxVcyi6lgI3FIUM53wWNEs18LqrGlE+HlyAZ+hIH8B49wHnwTuIp8WgLcS6xFKxsG05g0W7ChrsMBYN3IANGI9GgZ3h8LaUwyja98CmcjON4GouIhJuB4cImQtl'
        b'+JaRTrAfbMaEzuAypevKyTYSAy+WY2JilAwtpyPAu+CNBeYChHKlXPI92LwcbLf43rkc/L078DxDzY54scX3tsGb+HvgUDyDVTwyf7nTKgcNj+Lmgp0OdCzcC5ga83co'
        b'cxKqXSmU4UFwKJqeNga2Mq+cGU1jhb2TC00h+UDkTE8TziSu6+pAI7yai/n4YmIZgyFBiLGn4AmwbwMSG3bCreAO2D8XdoEjJQCja+/AU3AfquL94I47H1uudDnPgReq'
        b'SB9ANXatuBjVLbxbRlHLqGw6j3GxhXjAd2ATNsDZOWVNMSawnk5ZDA9WhZTs4Wuwv8Bdci9sStHelESEAwUSDk7F5cQ/HKu9nNT1K3SuWh4Xp7U7dUl32ctr1WXlpfKZ'
        b'vzyy4hf3CvfvB5yt56TV0j9r5lzui/+UXnhvs/TW4VGpvWN/FScvj87JffLhf75/9pBd8dU343c5XDju0PFmYMPfC28d9PnvdSnRlXGfxl18883UOO4nd9PzPLy/8tw0'
        b'WR4XG3D718U3kUTC2/x7xwpN/Ceq+xM2HAPCceJTZfuj/zm5/J9LNj/76UcPfumkfTegUM4pdvlzZBXnzGXlR/tUsYGf/eZL5f/8YfufZofmTgv+7AB6jNt7cUfZ6/XJ'
        b'C/ZQ33hObo1Pd7sdM92n3Vcy8ZCwcpFHyJJkKls7+1jLcaknYfXjUBc7npsn58GjZo0sRtnc3UA0MGUi9IBJHXsB7iUecsANDbmrDEiIyo0ZBW+bzI2co7l2cK/iKUY1'
        b'roe7VPFTjRJMCmheR6SH2DhwKYrx1sJ7XQC20vCNCeAAo13ej/rTObN3Gx48Dt4h/m0awQ5GI3QwMJFoNDteZ2QTIpjAXdPI3UBwCh6MyoG7wHltLub77WEDB2wWrCGq'
        b'5Wly2Aq322uc4DUMQ2qgYAe4Cc4z3ltOh65Br3WChrok7ABuOxq4eUjewvdywBkH9OgOfE+A7umxl5kDUlKY2fBgSOFMfAdnWU/BfWhiOE3Ub5OxxtPaY8waNKV1cNOc'
        b'J5J3wXvRUrAJtGtWodFCgzPY3c5VmhRkDugAx3SgSwN2Aj2mpxF79mmGh4iQ5QouZ01wQa/x0WtvoXEKOuFBRn+8vTonJxTNEs5Yu38Bq5hPwtNMCd/AWkjtCs2qlfhr'
        b'zRT2GgnOMDrE9kJwAraI0D30MXCQgjuWlzCS18Fx1RoMdbQQFsE7KURe5MNjSJh4gb1LLEzgtcVsGKZBzPS6UdbGPiiJSFTYHRiWqGrGmCSquO7AuC73riBDYCKWqHwb'
        b'p/UFRnVouwMTGjOfePg2b2Bdmax6EDilLyyyK70vVNqVhCQr/+TfJE95J+Sm8m7VO1W3ZQNcysv3P0V+fSFj3prQPqGj5OL8zvk3wwzR03tCUprt+wJDjq9vWd+6sZmH'
        b'8mcFOfuboT2B0wze0/q8gtpKHnhJH3l6G09xpJq1e9caQhO7RYnmV3g9gUkG7yQcC9ynxaet8oFP9LA3VQ98oobe9PI5NHfvXENwcrdXsjF6zuCHHg/zVtuYB14RfeJw'
        b'1ql0Wo843uAZ/+o3wx54hQ+5+bvRgX0J429MujLpHu8DB+jwKGHaAJ8TlIIEWhxzY4DijEqlLYRPAePyw9lS+FELuEMNDwSU0bMmI3/iSM42esx9o+j5v5uob15Hoqf0'
        b'ZUVPo8UNZmvU57GJu2iQ5+Z+XllBtrzfqWxGaVFRunxGdnoxE1DG5NG536lOUVXDOudQH8WaA0ezAwpGs1CIH8ZuTdRH8IG4MYHWnp+JI2i8f0+kbVJkqe//AypqDFz5'
        b'AaW0ugCrHawc/p7EDlRmMxFkBlwocUBbcRf3ZsK9im6PHD3WeYn82pK6+DdLPwzrGy0ecvqFHU/sos/92pkrjPrWcaqwgv6SwscvpnNILBTpV1xaHKXPfYIjnEj7PKfi'
        b'MCjTmTAovsGP3GL6PFNRkm8arc8xB5tJxLFgxpFQMGz4lHT8XiZtGfkFB2PxSmWCpbBhV3AMF/FEEnaFjbGCY8F4T9NnfWPvKkz8QkL5BHV7x7ZPPDkJ/eizv+bRwjjs'
        b'StsPH5IH7KkUegb9LXc1LfT/ljIfvyDHL9VcysWrJeShMOAbjliIika5BA7gsy+T8Y2Sh8Lgp5xJwlQa3wn5gpwy/rgleD2AJ+HOQW6Baco3Mxoc4FXFw3Yrnt7ot/+r'
        b'rdgNtye2wTI74p7HxU64GQfcR3isC27mHDvidkB/8Tl2yI3dcTPp5nM35Silu9KDnHsqvUzno5UidO5Nzn2Uvkqx0u+I0zyeiq8XVNJK/60myxvsuJt1MU0rndDRGTub'
        b'Rv/djf/PBbxtxzzrgP4qw1n9EVcZaOGA2o5Dqfis++1gk6Nte3Pe6D/OnVPJYfP1YH/d8G+VOd2dpQH/OqD/jpU8Zci5UCsaIrA7ckyF3kEv1LvrPSvtlWEW1DgQl9wC'
        b'4nh3VKWAuO121FNr6HlOxLWOtN8dj5sZJMA3ceNeqVI/G2slmg19gAkHavXQMxmS85KrNLXJGq2S/I6Nixs7NhmLi8lrNMpkPEvJ4uLi0X8kiCZIuf08eUFRfj8vKzsz'
        b'q59XWpRZ2En3c9LS0dEBf7KsQJ43t5Onxkx/P59sz/Q7MLHeq9Apv7JasUTzMp+Nx5/lqUlUdik+RHLxBJstL2Yib7xkXhOl/EF5qRNJhsVps1KepS7VauuSY2NXr14t'
        b'01SticGCsxq7l4mpYF1byCpqV8QqVbGDKJQh8TpurAx9T8ox59/JIb7D1UuIV5l+h7yCGSl5ZUiefjYGEz0jNZtQiH4LFWvxDFiEFUgaLcpUFpeIjmiVwZl10upSJtIJ'
        b'DpXe71ycLc/MSy9LTSmZkfWCWcVLuQxdpiI/Gz/oxRnqWo0mlQj61nnk1S7J1ywhOcXjnDjmnBCBk3FeroPq45nv8IV65mWz8qROVrng7qaeZiPviWocH3pwJhNJJgnq'
        b'6fje8B+Pfxb1EiXtt1OqKhW6ai2pftKW/z9Zpw7xNEFRNjxN4ITxKYuckHjgEMDaTYDL46pGC8/QxIKY3/RBK2s/fOcbIeXYxhHZhwxjQdxvX6au1WlRn2eC6FhPJjLj'
        b'TStj4nVSytv/JU1EcQjo535hCt/CUHS1dASGop12DEfVaoOtOmrkraysSR2N1cuEJBvGmpQmtqPYSTpxj17paLIUdf4xnaM/2WJnQ72QzXjTqVqnslAyVJAqZFTceMp/'
        b'jlKhWFdXV6vG+5V1JKYyYUU1yUMfjJEMGpaSiLR06fMfw8P6B5+YKImI1FRhffmq8bJxkS+QJTNTSCJmZP3ww+yMgB+OlvzQd4afrSQR2SUv9Ub8c9540YkHZzGY6OH0'
        b'N+weNLNZyzg6UqoWa2vVpnCww72JV2fmtcHdpk5dVauu0q5lAixFROI1PxIRhFf9SNtb+pGYF8DP4JU5EutvIvGSGimVmSEd42RjZXHJ7CO2szGjP+LIo2yu5uRxJJnJ'
        b'eriCMS7n2KLZcBvH1E+4hniOG7Z6iKYy2dpTFhlktl27sZ6uhqXJ7K+NIYwZr4Mdr2HXZiYAkA18D/6D7umw3hCr1Igqg4CPVAot7lCoUGsH+8bD8Jdh3G1hdQjKZ7VC'
        b'zWKVLMIJk9qRFKtUuKy6apVEoUVc3GKd1jZZM1JK0jMLiuaWFZYWFRYUp5fh+O3FhEoTToi4/rIBNmIriZmEmPopTMmWG10+GtvNKMizihzbsBqzcocoDJkczLqXyEFz'
        b'SuSwwCTSQnXMONWQShz07sRIpnTGR6pqbPsCY/zWIf6X0QdhKFKNJL20aBglVY2keHWVdp1KXU0aTvsc4pkJcZixhAZMtlZRvZa8OPwMFzl8n2Ud7jENYvbDh3s+2yQm'
        b'n3yMvniYEmkZnJVFBDard628OQ47a5GchijwUPWwTJrG2H0H5Wu7TYhIYjlSslNT5JLFquramiU4px9QdDkM4b/cGPBUPtg7HjZJU3PhbtjIpTjwJB3hAZoYLwpXwZVU'
        b'Bli1Jk5AYFXwTqE5tga8CHfCw8aIIlSuHTwP2sExHTYeASfAaXgXy+xgJ7yB/l4B9TwKbgJ6IdzKgQ3gGtxHrHjhXnBoea7ZAh+lnLNzhye46D09rNdhTqoYHp9ezFgx'
        b'g2vTho3GkV+K7bfgDUcHeF0m5RAaJ/gSjdMlcIhV2jjT0+D2HFI+2A5uzXECZ+BmRtcTTU/jAr0Oc1xaeBNcM4dusfAQYLJdrhMKi3D0lYhgTYy8NCIC7oA7Y7H1VWcJ'
        b'G9wlBm+mH/KgwXsrM4haKW8c3xQBhAqZAfdkwHeIurGGY0d9FueHw7XkeRbLKMY6fRe46GIZEiRLlpMP61GBY4ugPm9mFrcI1GNnBmDHa/AdcHptGAXu8pxgs2xS1eu3'
        b'6/iaT1Am3yourmjMdwRxbtuWLOtPrPdK23vCbuVfsj/jbb25PLf9Qc1nux4XLfAsMOQeLnrG/ah6X8vf3n0SH/j3bZz3T2z6beuvD+090Zy6I8vtb989dZs+KstXIH93'
        b'a4Z7WOKUPQtqtk7q2bxId3+g1vDsVCb865JNfz4BfXM/lKeP3fvh35bO1LjHfD9nO/xt/Slt9eet2+Y3rus7cuXMmxtOhn0UdTxxo2jP0d/Nd6/8w0cd78f4zPqmpvJv'
        b'3ZsWBf7vr/0WVDad/tWBW6GzG37y0ZFrWxx/8hfXk22x18VVUiHZzF8DN/tFyWKyYsCeXA4lAKc4cTIeQVplc5OZYEskYNSpiGgMGrOjXIq48So2YBPcUgKazcgvrF2B'
        b'1xeuEk5ktAFH4Vaw24xaK4O7CXCNAw+CK+AIo9U4AbfDFqPWB5wDF1Lg4UpGvXMEdIBLpDOD1nkWdnTwHGglOpPM1+BWExbMBAQDW93tS+YyWdzmOBp1KiVwq9ERPzcN'
        b'noc3CQ4MjaHNlcP49OfB2+AuvBJZxVi13QqB27H1sVUQBuGsRfAYfJOx1rsM2sBBNBovgDMmk0QatC6aw9zeB/ako091gBYyhq+i+/l0Bjy9hNTElOXwPJo38lBFLKbh'
        b'KXApHraCc1LnV9qLxdt3lvhvCz/WNqUuS5fxHEaz8lQZRY0abRgd0RHa7Tbhpuhe6IcCQ2Fp38S0e5UfLn3KpUfNwfYqvgHHxS3iRkGfT2DbOIOPtJGP9SM2bIc8RGbb'
        b'BVFwW3W3aOznARF9EybfFd4W3l81wKUjCwjArZAA3ArpxyKxAeUhisWmMhQdSbBwX6DHMsljWeSxLPqJWNIXEdPMOyLsi45v5j30lj7x8G7O6PWL6faL6VA99Et8jFUx'
        b'focW7F3QFtwWb/AK6/C86NPp0+019ub4u5NuTbL0fD/ApSZn0gavsRYCrdAC+f9caXJ4oByOgmmFy3/BBsnHYvBkigXhz47ELsW/flnH4sR7ZpsgjupymjQyx+Ksv2x+'
        b'GRYNhnPua6scRhe/u1A51BgEybj4lb2A/DHY0TfehizOSinq56Wlp5b082YUpadJ7WzZY6i/MUbO7LerWKpQL1FprOR8V2Op9ehwwH5Yr1HYZ5Sd3gXJ+VjidyXeodz0'
        b'oypd/w2+oTCgsMOWxJ+iVCI21BK/buR4bGz2mnjloRsHlZJkzMknl5vcJZbbQD9Fs5ynyQUwBtAPtTdAX7ckqAJxtouRBFGr05rlCS2ueC0rbb2QHMtKIEy/eAFRVrHC'
        b'/K4lOUy6RKGRVFbXKvBuEpJFqlBKjW7FYpVtth9/rsa0c4KZSCPMMoXkZgsxxVBhJd9ZkmGU7rSqNYzwgmuFcYO8ggH/D4PmR89UKTHnba4KtYqYcyDKmDJIIhChalI0'
        b'wlkHF2XIZLJg6TAyAQMgI5YpCtybNFq1rkKrQ7mbc5ZJMoz4S4v7NvMzvUN6pq6uWmXsAiy4FQkhuLBITlqBqtJmHhFF6RnpWE+aXiYvzU9NL4qWGEXIkvQ5JdJh61tF'
        b'TFFwZatqlDHa2hj0Y1E/EbV1jGnOc3JYY0sqR6kqNTbpsZTKn5sd/mMS2nENP0+mNrmlZnu1zdyW1lYr0axpU/yWoFpJL5Kn5A0VtW1br7yg+K3UqcqwJQtTFehKgq9I'
        b'h2X7DR4XWtUS1C9QBykvl9fW4JniOWY9a7Tmr+PMcC5I2sKmNHiCMHXdSnXtClRVSsX/x957wEV1rA//Z3fpSxWkg4C0pRdREJVelwXpSlGRjhRhxYZdVBBFUFQQFVAR'
        b'EBEQFVAEnEmiJhpZ1rhoYqI3xSQ3RcU0U3xn5iy4EE353fu5v/f//q/3Ztmdc2bO1GdmnjPP93mN/U12Ia3lTM9cmZo71vPR0EzBByEtk/Ny+ZmounBKqOIySSiq5ddm'
        b'jE5GUjfEkSwmndW8pVmpyStoefDq3WhkmOtMB0fSuVHjkPLgPNiIHT2Iy0uUNXhsIqH4ynTSCgvIWCOjnZgUvX5LTk9is40ixVtgvtGqjEy0q8YWSmvQU7Kz0eBLKqA3'
        b'wvTNr5YtfH5eciZphPEN+fKCPDSQyfF0VLXixkYDge72r67Ml1LOzigUbc2Tli/PzkwmR7SxboSMJ0mLq1ePHR9aZiSJhSJ6Op7fjSzRJ8fGCM/yRpZh0REc3Bh4tjey'
        b'9PYLfc04tJIwIZvJsfoLhm3j5129xkX9JAfZf3SO/k/0AtNC6b1/Nyw1wXv/IHgZ+9bEm38T2q8m2bG+tUGGUjSSk8YQw4cJPmKFwEG0sygRKwRK0MahnIJtGgv8SYqp'
        b'CqABHNYdoxhSYBfog1tIvMR4eEAWbBqnH1JoT9IEeqLIy39zsBduXa0+WZUgViM0mBZy0U1s2LQMloldV2J/qFFinBfX1iom0CY4WgrU/oHegKAR2/3UQJl3PH1wtAke'
        b'gSdhBygeP+2pyPAApxQLY9BVb1gx5Q+f9vtHvXRdHG45TnjjwNPwlAw120EDdixxpg+YHg+c6ghq2OMaCXgB7C1cja74z4dNXOIc0zY4DCsl6HSk4V64TcFMB7QoEG1A'
        b'twv66AWNnnAzPIyuHZsCtoETUaA+JRyUem8Ah8AW0Ir+h8/ubV+2GlSAk95LF4Gd3gWZ4eFZiwrMEkDNsgxVCpbP1QeHI8Bm0nhr4JF4P5QteGG5IpNiwj6GPSzLKIzE'
        b'u0CetGS2wHm4e0LWYKkOKPUElUvBtgkZ2gaPwSr8HR+PXaICdxhR4HS4mjboDSM14RMGamEdOC8+oSvPsJ8CLxTi3gvOwkawdVw7w4kRAy6XFxZGwYrlSipwb5Sljrji'
        b'JVQ3WGODW2eMhzdOgtwMmuXIU5RhiSZsAzUbCj3Rc9Jc4IE/5JDiSFESzSkzBV7G6NAdSgHgMugq9MMNem66P2gGpVxJL9a7wen5pN+glLmEz4c60z5pfjDYOQV1751w'
        b'XwQoAzsZcCBfKQCeViR8RXDSE5z6XTKBRAUAasBBogaImZAi2MYGVRpm8ORU0AQaNaeyKFDDUwONgfBooQdKUg5egttfwQ5lwgZYhR50bg5qny2KKbAYVTA5qQz2LqXg'
        b'jgjFCHgO7CbZwqjggxKqspAgTrCt3au8uhr5j+VLaeKYkaHgkcIpoFIVdhdGoSS1dG3GQGvhgX8l5demGxEM2iw1QJ+FMS2gesEla7EKLiwE1FBwDzgDB8jZOCJskhLk'
        b'xD6KsYNieA5elHBSDLdFcJihUZklzt3S/PfQJrI/OHF31Duh0EH13JH02hNf1A4fUFCVrXhwY/e0B9dkowI1A1uivOJOKbjJ9vROCXgj4BOLuz2FgR0/XzP7+t2vvjp9'
        b'ufbbx7Jqb9R+8Cg3uGJ1mm1Jj2pmQOB602X7H/q+OZ27Ozyk9AZX9ZO7h+boO8bu29EsCJD/7EPlqk2LvnOYpti0+mPwoP+Me5bTx6U2y7PnWzs28ba3zO31tVyp01D+'
        b'Y+p8LdWyJP+zL0rlv2FGc+73HXRVdrwXw7NccA4MMd9cn3Zz7ahDQOvQwsSba3cI961ft/TBDJe3jz5eq7BzkZfA/pNtXVqLyma/f6QdfLG6bK3R7bDfWkQKXzKULLoH'
        b'e60ffHf5jJ73D1sW5od3L7w2euzModgCgVV0+PWn5eG/yK0Oe9Mjt7oxwDfg+DrzrMEvW09XO3R90pxYcELQeCd+5c8nF4VF2X5Z+NuzBzIH5ucYn3T8+LLhcu/7w2uU'
        b'XQx+VJ32dbibVWHj+xlHClaxVy0+v6jlUJr1MWcX/z2pMdmPjTqbir9XL9pgl7/o4dftRauLHp9f9mR23uOKuy1d/uo7ZG/odBd8/7BQds39ZdWfLn+kqfRg2fsP738e'
        b'nHqNV5X1wPyj2F9PDxnfOL+PN+xq6VDo3J0GTuxZr5P8LuvUnBfMpGPVty6rczSJotB3oRpW5Gn7SvKw4GbQSRSFSkgy7R3XEx6Gp8QWrpg+dgY0EYNQLdAPDtB6QlC8'
        b'cSXDyxTSuC0LcBH00iMGnGC/PJMOt2kS2lMUF26BTUwJShg+kn4knjxZFZ6ciWRDDTw0wSUs8QerDStovd2uGWCPmCOmxBOTxJiwsXAtrWM8ph/xUgnZrfbSINUPZR0X'
        b'PgJ0mkXOnqgmXQk6wFaaRlWxyhMVvHjskDs54g6O5NHP3gRaQBN22LESHA0Cp6UomWymCWyEXaRSQL8LxhoT/62wzH8Rwz5pFe3nthf2+IrVmuAYfOmDlOULa0AvAVdF'
        b'ehm8VHzmLpyk+uwCZUxa79mNFiL7xWAo2DVbzIZiTYXbYQ3RXC5XztsAG9AdNqBFipKyYYCLsDSZaGhD4Y4p4zrTubBx3HftOthM4hbBpjnWdrbwCGjHrm+J/tkn/ZkF'
        b'LtxltGw5zQ0JAqX2k2miDqDKD/TI2IML8TRzbf9cGdKBAuXADpvgMLQCUfZlzYXt4BxdybtAizQ2QobNsAW7pyVmyGutaR10G6zQAGX2POd8Ww7Kw1ymUSZs4Gj9bxye'
        b'xXJ1bG35emCHyStUbK8COeEzwdgPQ5ot9vpp3mx+W8vxrsH0ev9m33ZeCw+zkPwfvFpNa2TapNigKDJyFBg5ElCTkUuF0oixpYS7ywrlB6aWItMZAtMZIlNXgalrj4HQ'
        b'NGBI1XhEXeegR6VHs8uQk8+Qla9A3feBiUUld2SqSX3K8FSr5g2DGsP2fg9MzCu5j2UoU8eOUMF07wou5hTZ19gLda2HdQM7ZLpVOlUGXQQOgRWyj43GHGZ2rvpA1/Qx'
        b'xTCfiTXG7F42dpXkS7xr+hHvmn4Mmo/jVulWLzOsbn5Xz0SsN/Yi6mJvoi72ZjzUmy72bnl8To3cA4kj7S9jxJAYsSRGLOOBliG6LmZCjVGuJONpGYrj+ZF4/iSePwMz'
        b'edwPudMoKaFh+JB2+JgSPHrIZu6Q6TyB+jyUaW39g+sr1w9pOXTE0tijYRfeAyPbDo1hI5ceU9Fs7vBsrmB+POEgRQtNYob0Y7BfUxSnWVqgZdthPagh8ooQeEUMO0WQ'
        b'h4kRWQ+1DBuKOtZfUx6eFTMikZcQoSFvSJs3oj8do306ZLsVzyqKC+BNCuBDCuDDeKBvVBdSEyLSdxjWd+iI6k7oTBC5+A+7+L/y7scKuPrdK91F6hyBOqfZ7La6w8g0'
        b'88rAB9OMKwI/mao7pGfbvEIw1Xcw9lraUEzi0OLkEb/5QxFxQwkpoyyGZhqjgolqY5p5BbOKjStqPKkhK/fb6nPuGlui3hvUEtSjOWzjcXeaSf0MuhWF0xwqvKsCCWAJ'
        b'u3BtVhSozxixdMZuUM1GxDUeIkC5MbWu8K3iPdDSqZCXUO9PeS3Y56UiuSDl98YHf2VYYwOn3/N4/t6IrpCWdDGaaMNgRBD4TgTjKfn8O28C8E61UcaFOs/2oia+CpAZ'
        b'28NmoI/9MuRYI30gWbZEroRKkxk/4Cj9bzvgmMFhPl/yu611RGpuSmoB/8903EShJt7EYxVOEt9oAS/kT3bqhtTknTontNALzwWb56/ivjwXHz6ZY14WK14Qm4NzEtgM'
        b'eBi0KU1Fy/oGsvCFzWAPuCCx9h1f9+b7g36uNTHfDAWt8AxePkvDXfRLbLTovgSbiGsHNigzwtdW2KH1hN1K9DEdDARjIzXTRdKzQOUMsqubaYW2gCj95eAYSsEQOyS4'
        b'7EQS15eDZ9GOZQtaGkmcRYhRJeqGTZEs1U4m/rbEJiVWk1Y35K2Bl5xz0WKhwtkBtRA8SoGB1aCWeBywBOcpYrxqj1YkevZusJZWa3SAzTFs+QJlUIWR4C0UbIPF5uTl'
        b'PBPsSrLO0udYYc7kGgbcnAAu03Gag9Zx8XJJHtSESlMymkxF0BdAShMEB6Qj4W7UJNj7xGY5VIfbTUlpVoMzoDESdHLG6eMUPA12m5JDr7Keemw2ODO+x/cD54jWgQur'
        b'HNAyphtUjZvy7mcYF8GTJMn12EwQdmWB3WPWrrqMucvgCdpEdpeaDTsPDKANENosIxEHmmJpq9oyZy/YtSDnpRZjISwj+Gm4xVE/EiVWFY0WGfujeQxKLoxhbYw2PZVe'
        b'pNIVXffod7BcmZTDEuXb2a604qc3aHrCEAu/f1qy9P2k2XRgFjvQvJZhxEASw2rTiiQ6MM1AMU3ARC0zf4nNFisdOnCUoaVYwlyATzqs2+Y6nSL8bbRkPgXPEyvecZA7'
        b'PJUyxnJHi2vSEPHgIKxlu8IdElqIoHR6Y7cF7UK72XCbBryQr4TWzBoMd9DkSx4Z4iE7b5SpTQ5XNCebYmdlBMq5J4PJxhvssVZA23RSY2GwEuxkg02zxhUPoI1F94Tq'
        b'AtABu5Sd2EpIALPMGRhhM8BhkB63ZJkuPxSc0bKXophshhHokyKPWaMD97FnwMsr4QUVJk7N1UGXXFgK6+ayC7B59WnKHO5CK/pNS2nu++ZwcAl2KcILRTayqOfsQ3eg'
        b'QdlLngI6FE0xjSycAlW54Wi12Evi6MJj8BDb0iok3xp2hqCWDGbGgUOgjHQrQ1CMaq7LPhh2g4Oz0FVpsJUBDzgszrRfkCDF90VS2oDRfXnhz8v0ozX6V31/uat2/SeX'
        b'O83vmV/YuSWjVlONfSHKN6Nhi6V/xS7fXNN/nHyr2dlSen/g7ZIDO0vqjY61btFQm1ppYqVwrOTBRyY/bk3/5l3076dvZgvvfGXvzP/mp/7R+1c/KHr3q95f1iSVtpW2'
        b'tZRrPO/OrZP/pnh5yq21Mbk8Drej7u382uTv5h8N3Px2cfOMzrPGbxd8ejL7VlDkDabno7UZ3mknlrftfOwUauicLWfPtfX70PtzmYauFW2f/5j6jc8Nt6YHn2aeCziy'
        b'tPmi563k4ublvp9Hrkj9eTa3x8/nVlZ9eqPhPU5IQG9w7nXr9q/5ZaeuhKcYSM/+x9qS4+98ub/7ZHmpQdEXqvffP9P21s2M9n98dv9t5+iL79TVKE6/lzXb641T8ctb'
        b'deOXv5MlY/URq61rMKvVTTVye/Xlvvc4AfcerXG/eYPZPby248Tyr3i93yy2Nt5x+sec5OF0d+pYdOaJp2q88Bd6m17I7Q697RGg9utUzroPLubzct82uKt56Dv/D3V9'
        b'2zKf8YyycgrDf8j3cv5AMUD64ZetP8POFtlkofbQPJs0raL5V/ukm+1ObS3df9skOGvz3rSwoG+zBstlRtzaUhxbpqTPeHfartGk+4+gvleO6J/a3Y2f2z4ovfp1ik/5'
        b'+4yuz8t31Mp//BGjL7uwKv69Ix98tuvNj9Vf7OqzkRleoZ9hdUr9g+DkAq0S/qxuv88MjL95OPNXw5tfOs6Wf/aj8+qoQz+GGvd/v+HmykPdZun5xc4ffrnnveVTf1AO'
        b'z1+8dOqmbVEhb0StWPht2I3nVMqRbD/RlYilMx02ri98zpuTot+4o+fr6tU5KXfj1N65Myx1JGz6iU+Tvvm0XPHdt/555/uoAw4fBlpcy5odM3IwdZP9qYD6wm3xSvem'
        b'fToThs44/ih9qpPHzOLGj7Zebbhjsem9W3c1C/sKS9ZMORU44pH+dk1u56Lh/tFj+dtn9bStD26/t6bt6RdvrKUifa/k3/z+q/1L4mvNzPd0f+zy8bkRN9XF0r1LHh28'
        b'b7B19dGts3ccaV5z18Pr9IPiIw3pHjuuS9+KLeSrz2YcnfXDmWSVeUUuopOHnbufzbov+vXem22tXWl9XVdjb59JbpfNvLlWqb33zvLPd67fktD9xR3FmkfsoedTzuUy'
        b'liVezr4TVh1r9Fl0rpJT9Z3B3CLP5x+6X3NfLfxo0y+U2rtB5uCjZ+lR3+pF87/2aVtc+/RG4k07e4/0vrU+xYWGGSom726xKZjFv/Sh4k/fPi41rvlULfn7jZ+6fPfo'
        b'gX7KPJXThd9pdp/qVi/aMvrlvt4Pg95c1XftJ9nv5+x8oty93abwO7s8pfQf5w7KOkffgP6dZz58tOjzw0bSOW0PWM3UkbcFH3y0+huzWFW3Hz7jPVq0dmbHmXlSfScd'
        b'/QXbo1gyb5jFsmT6q97zLNBMUNJ+zGnd/IlN5ikG659mMazrj/agi199E8Waxli3M2uwfq6Xy+Np1i+Sc48LLkbf+qxpfuLTH1SXs6LrvKTv3/+e30wdTqyW/cpWi7rg'
        b'9eTD20/6Nz3pL77TXv9d7YmdR5ZVX5T5ZeaGnE/+udKn9RfN1V9Lf/f+Kk/u1p9cfD4sGxzQ+UGlPyiwX/O9H3wuF4neftB14vDGn+tOj3R270nZFh/jsalfo+RXi8FF'
        b'UR5861TbgeXLUt7a+GlbVN6uqwOhegMPP5Ptv36o/wPNpYsGvH598UjLNsot8v7tp79ufJQz+8WvghcDPt/u0WpM8lD4rZNSzCz88buDXfZ7RbdkF37vfejt2EdA/a23'
        b'X6jkHrdMe+HR2/bCoDF+VWPpjE+Ubr7x0YnVv+nOuxqq8kW7KKj79sYdH+x9zv5c+UzTF4p7n+uvtSqIjftJK2RnqOBnBU42OZ+Fpu+T4AT2QQpbIiTdkI65IEVCu5Zo'
        b'WbTRXH8aK1lAnZ6EniUwnaZq94PN6r87vQU2wx2LFEEr0VUYRIP9XLibO36DigMLngJ96WZwB1EyxIHiNRMt9EEzC57T8nVXJLi0qJRV5HLh/FedJevKVSePgcWK+BQY'
        b'AWfb2gWGoEWQZoiUNzitlDiNNr2vmQFrabx8Wp4Ng6bLL04SQ7qtYDtf0m5TCQ6w4tM9waYcUl/y/kF8O/RU24JQjjxaqXZhBbcNaM6GpSxqBmyViQRV88ljwOEp02mt'
        b'DmMBSkdmMdMKnAedzwg05WhWATfEKtVUhmImMtByE5wjdQwqgogzWPsgE9gHd+G87WGagfP+RMni5garuTaW5qAPI7jF/G1ZUEM0WaAc1MIyNiyxLZwGO+EuLouSheeY'
        b'YVM0iZYpGJR74ovkEuxC06oSKGEuL4R9fFhPtDRJDsQ5UAc8LHZYwgAt2bPpovRYmuHItmAn7LQNQk9WYMbGsokmLB02F/GtgmD5crhTFdSjJfaeUFlKFXSwVoCdoIs+'
        b'xliyZDE32CYInEW1VU5R0vAykwWr4SGaONcPe1CW0J9jXHg2jA1aLGUoedjNBI3S8KK4WcABNz64lIhR/fKobaQpBViO36jtDKOPQh4CJeAUzqM8BxUBl14J9LFAMSxV'
        b'h43RtI6qFu6RsoZtypKKQNgcTGdikxQ5ervL2o6jAPoSLa2wrm2KNgtuYoIDYg6fNNzEtuOCPngSXuDAMlQPysx42AAraTXXADgIDvNDGWSRBHeAUtAcrEo7+m2Fm9FK'
        b'tQtVE24Aa7ADnsFFkabUNFloLdUHT5MejpY+ZfACN9QGlNrT/l3ArkzUgfXAFilwcg3YRwqCGsaJbxcE2hXRPRSlLMOydvNYCstJVelbgi52sG1IPmgLRP2Uz7XkMCid'
        b'KKkAsMWT1mlehiWgls/B2eynnMNAr4o2rQvd6QQOc8f8HklTeNdhBQfmWETQespDTHAMY/Mlkflwz/Q8WA+P0gOrDW6HbXzQYRtkxUGrR1DFALtnRpGnuoPWeOzgTJpi'
        b'sCkXfVTDsJvU6nzQCDZx18Ejkk4osHr5iCc5P8sDu2RgGS9nDKnPAMdS3Ek1BM+BJVzr2ROI+qyp5nYk2RjYbMtGsqrWElVCfgjKjgIuwKUM0EAiwwtwSzIqTdLyYJ4t'
        b'g5J3ZIJqtN1qpfvrdrR1KWfbcaLnWKH2QpmWy2RmwspQWhe6F7apWqO2sQvCnndQRYDdLNkVS2ExjyQdBw9ksS3t8pHw2xeKl69NDFjnB7aRSnYoAtvZHDRKujCPEyct'
        b'DasZ8LwGHRdUmYM2rh04OUHZu9WYvtiz2o6P8tNuR0rLgqUMcByccKALdCBpOaojR/q1kwzFDmbCJnhAkW67reiJFXxwigrhoH0r9hiBRpAiE9SDLda0+DgAj4KLfNRw'
        b'BSGY/qRkz4IdoENOkUf69krQFEmkBgV78EAqBWemggrSQJoOsA52+Ydi531oGwz6GXqRyqQa3cA21CHKdMFZyVcDcmJ5A7cz4ADeg8AuGfEm5AQ8S4vwbaDL4OUpe/I2'
        b'A5yRzkYFaiY9TQOe8+aDy6Yku/YMSsGTCVpSVxK1+0zQiLb92O8FPZxRaXHGNZCAzgLb4cFkJyIxvFAjd/FhORrtZ2xQb0Di/iwvBt2ooyplNY3G7cCyZetRIviSMdyL'
        b'tyIxDLjTRPzGZAM8ATuJV5YSivbKkmpLmkIZHgMn8HvKlaA0HHahVlRjLAoB5bR3hS2UN76mMlcGDeSjaGO3lkk/rIOHJEGXBui2h6WWaPjAo+g6rIuk3wHMheUot5ah'
        b'ScGrrJiULNjHdLNcSr8gOeqNnbRANGzxS2LSb1SYrDy1FLDNiSS9GjTxrMFeWCbh4YqlogTOE6GD5D44yCfTGZK9WHqCHlCLJKg2aJVyXAA6SKFyYLc3PYFk5JNNWS3q'
        b'1XxwgQyJhaBvKuxahxoQy094Ft2gAM+jvhAaRBNtyufCXjwph4ADGC0Ww7CV0aW9exTDI7CSj9pZHpauQn/IhlAd7mNtgDtBHRdsJbWmIg8ucO2lxe6yULc3hV10t78I'
        b'9iKxW2bPsy0AJeK3C1y4hb7YgSRrMRtWwvZCJXlUpcYML7AJFtMN0ZA0jw932XotQBnSYEwH28B2MhXMA51YVpMTEPnoBrwGaGFRYLsZ6IE19HiqXwUriDsxN9BLCy3a'
        b'nRjq8X20E5qDsBdtYDEl1R7u5NlwsGtCe6yXWR+G5JjrHBlwbAmLbr8mcECLfrky/mYForlqLnHSg53NKKQjIVkG9uajUfw7h14SXkKi4Rk5+1gZ+g3VKW1YwSZ32eaD'
        b's/ZEJKuhIYpExjnYQRejB4PhysJeil7lSFYQOMkDe8AWsQGCMppDCkB1KEc80vyY4FQwPEMP4T2wHpTwzZzQVSzvDzBAuU8IHbEBHuTySSwiTlxYnNXy8ASoJs5aQPks'
        b'9Vf7OVECVdjVCTyfQdpCMxbuHisEDzSR56jBCyzU007DE/SceWkRWs5Z2kbASkmHaGJnaLDfnfRAtwTQy0bilcyYLNjNAM3rnWjJV5kDm9lwpy04kypeOMlRzHBF0Egi'
        b'emrlowyAQ2jiwxC1c2hMuvuS2pOHe0EFLqJCMA93FxRRAxSz4kxhiZocWeapTYllc9B8rYsNjDbBbeqwmgyXDRbwGD8UdtorWCLBakWkuWoWC+xMWEW6ZiF7FeyKDrCx'
        b's8NioAZNee7zxOtGfXN2MA/sN0GSlsMwzILbSB2EK8IGPpL8sFQeFQSXAtZl4hEMK6RmwwHYTi9QauE+UMG2teNkqaHCyBgy1eEOdVIJbAdN4jt1BuwOtbXCvRmN3gOo'
        b'Z3bSM0/dEhO+vdUy0A87AjlY/PQxA0HNFNLU1rDVBHbZhqLu3g9asWxYz4D7lcTNA/vAMQOxuxpJXzVoeOyaAk+CdvoBO5ZG87MK7IILOUgOoLmJyQRVS8Buuisfgi0+'
        b'4pV2kIollm9KsJeFekCDG+xwIJngO6KuWAZ2zJpg+nEY7SxwveUi6XOZa8dTXY4E9RrGHCNYSq+FzhrpYpsQcMSLmIU4wj1r6E6xKQtWEXQZmusk2GX5Szg6/7v0H1zY'
        b'V5zLk/RII1NANPtrdV7xzoO+RF5eLmfTLy/XORAn8lVrPtA1H7IIFupyhzS4GIilV6Mn0rEX6NgPOXgJdbwrZEY0dQ8uq1wm0rQRaNo0Rws1nStYI9r6dewatkjbTqBt'
        b'N2TvIdT2rJAe0dYb1g6ql2piN7BFRjMERjM6ooVG7ihs0G9QHl83rDdtsm6wHtK2Rb/ot2zDWsHNqcN2QT1SItcggWvQECe4QurBNKMKxbvTzOtX1m5EXzSM6jWapjVM'
        b'E2o4VjAeqmve1dWr9q3j1nDFZijJQn2nDkeBvotQd2aFz4jR9MqgB7p6dVY1ViPaOiJtK4G2lVDbZpTF1NOs8HksQxmb1ns1yFQEfWJoUuE/Mp3TNKdhzvF5FSEj6EEh'
        b'Ag2HipAPpqNnY1ckxzcIp8+UvDJiYC4ysBUY2DYntWe0ZKAH1CnUKNTPbHJvcBdq2+PfcjVy9VNrVfBXVEf1vk3BDcHDpm4dM4dNfXtihdp+I/rTqmWHtb3rvZqCGoKa'
        b'UzoSBHZeQlNvcbivODytY53Azkdo6vtAx2BYx7M+pl4X/cG+TDwF9p6jlLKO7mDS1awrWSPGptWxwwZzaMubjjQBZ85TimlgOGiM4dYjRqZN8g3yzTECI+dho3k9MsNG'
        b'gYPmqDZ8GIaoMgxNhg1c66OaFjYs7DAXmLmSmD1JAxm9GSNGxk1SDVISF4fNfHpihs14gyuFRqEoCQ/Dx6oohbqFNQubzQUGDsP6YR1J3cs6l6FHm14xHVwJbYQzw1CL'
        b'VAcM6y9ulhJZugosXdHXnvCBuN64a4xbUtelrkWJeIkCXqIwcJFw7uJRPeUAhu5jQ0pHt06pRql+5bGNHVOfUgwLLmMsPzHYn5HIbK7AbG5PltAsSGgU/JTFtPBlPJhm'
        b'hr3ciKbNEkyb1aMgnOYzKs3S0X0shxOTqZEZ0Teo863xRb1Jv0FfZOwkMHYS6juPjL+JFeg7jFKyBoYd4d0LOxeOGJkPG6U2z2if0zJHZD1PYD0P/Rx0vOp6xfWa762Q'
        b'6yGikMWCkMVDS5KHkpKHQlKEPqkPcJSMsSieAmtP9HMw/GrsldhrUbcSrieIeEsFvKVDyWlDKWlDvHShXwZ5SnCzY/usllkdM7rndM4ROfsKnH0HIweXDjkHCa2DcbFl'
        b'GmTqV+AOKbJwF1i4C43mjJha1SsMG6UNhUeLwhMF4Ymi8NTh8FShfZogPPWaRgejW75Tvse0hz/I7OG85+A7FJ4qsE8bVZKdaTgqrYgqRRdXCuq74kqZ9BRXgYWr0MgN'
        b'tbGBIRkyuAXnNDPapVukm1Pac1pyhJZzRuWlUUKKOCH5GnmcEKpH1NrDRrHoTqUWJdQZ0jvTe1IGsnuzRfPCBPPChuaHD0VEDc2LFs6MEVrGot5mvIjxwNqerjH3YWv3'
        b'xyzKymGYw+vw6g7oDOjxHQjpDRHNCRHMCRHO4A1zMobCI0ThMYLwmKHYeFFssiA2WRSbLohNvx2eMeLlfVXziqa4W6EOFS/0ShiVlTIwHGXJoJyqUrqGh/Tq1Z9SqFc0'
        b'G7dbtliOGBi/7L0G/h1pZ/MGpYf1I675oz5n4Iv6nOkxlWbNYSPvjpndHp0eqENZ644uY7jZa45SboZaFf7PVjKoaWbVTOxvqIDw4j2ak4b17EdmunZndWYJ9J2rQ1sC'
        b'Htg6VoeOmFs2ZTVkdag15FQHYBdLuIMnNeU05OC6C6gJwI2Ax6pJu3mLudDIEf9WbFBsjmiPbYkdtvXrURIa+ZMeE9js1O7a4oq+9DAGZHplegoGVveuFroGkuKiNjE0'
        b'HTYIbvZtlkN/ejREbsECt+Ahl+CnlJyBIWoE0fw4wfy4EWOzJp0GneY0gfEM3BQmPcYD1r3W2MEYkkAdmgLTWcOm3j3+w6Yhg2moL7ib4L5g0iTXIDdiatbk2+BLy5yh'
        b'mf5DHP9hTtS1GbfcrrsNcxYNLVgkNF2MohiTKGYiIweBkQPqGGhsxXXGDTKuSl2RGowS+UUL/KKFnjFCl9hRFblwJJKmUAZGRAjV+9LHYGiJpDag26uL60OhQQGNlhkt'
        b'MzqkRA6eAgdPobWX0MgbPWo27qkGhnV+NX5jNzq1u7W4iaz9BNZ+15xw1kTcRAE3sV5BaLRolKWAakqXMjE/ptesPqRvO6wf0GHcbdlp2eM04N7rLnQKGNE3FOk7oyYc'
        b'1l+K6pndyx70uup7xffaFFHQEkHQEqFvktB1KboLz0Z1YTVhTylU+/TYE7fdiJn1scXNhcOmEahuLXotBk2wUL5qf8VeODti2DR7KCZWFBMviIkfSlgkSkgXJKSLEpYJ'
        b'EpYJY7JJ7Y2ypBwNHyvgcvnX+I+JwIim+IZ4kZmLwMxFaDRzxMiEnnSdkYxHEgy1I2NAvlceyYhh0/TmAuz0S2TvJbD3Qj/RnJFxJeNaAXYsJwpLEoQlDS1NHUpOHQpL'
        b'E/qnP8BRssai+AjsfdBPNKBkr8sOzY8QzY8XzI8XzU8RzE8ZSs0YSssYmp8pDMwiD+I157evalnVUdBd1FkkmhUgmBVwjXVtytCsEKE9D3cX/wZ/1CDuLe60NBWaeoxY'
        b'2tWjuTFzKDpWFL1EEL1EFJ0xHJ0hdM4URGdci0IiIKgzqCdl0HnQuyfzvRmBQ9EZAudMJMTcTJAQI62H6iW4JlhcL5Oe4i6wdheazhmrRwNSj9PolYMLWi8M66fRHR7V'
        b'ScqVFNRD3K+7i7gpAm6K0D9VODsNtyxq1WF9HmpTmU6ZjvzuFZ0rerwHwnrDhKhcDjw8cANrAkeM7J5SbGOTDsfumZ0zcTZCGkJGLDntUi1SIza27dwW7oiDY7dUp1RH'
        b'TJciypCtHeqrtu4iGz+Bjd9gitCGO2yTSMZljGA+Em0JwvmJSLxyrNBQ5lgRqZsrtJyLxoiZORoiZjbDpv4oT0qdSj3pQgf/0ansGSY4BzMfa1LmFk2xDbHNsUIzl1Ed'
        b'JST8VjGCGBa631NBDB29p2pIWj32YlLTpj9Ok6LUdEWqRgJVo3o1tOoIbAgc0Zh6MKAyAK2vULmFGjb4d1BlUE1ObZ5Qw078qzqlPkFg6CjUcBoLSKtfJzB0FmrMwAHB'
        b'lcF48SNVI1UdVZdQkyAysBMY2JHVkX6dYo2iSJsj0OY0mzQ7opVgh0a3TqfOkPbsp5SCjuGgS88a8kU8K901MkZrRk4Dp9m3PaQlRGQzV2Azt2dpT/6QjZfAxHswWWAS'
        b'NGwScy1j2CRpKC4J1amZOe4B4qpvjkRCc+xwlZ/AxW/YduE1jVv61/VFQQsFQQuFlnEjltbDlhEdUt2KnYq0PEE/0ZQdcyXmmh9MRPLezHxUVhZ3IHlUlbJKUzVH2epm'
        b'U55R6mrqTywpNYPqyNuqxiNaugfXVq7dt25IdfpPT32kKId0xk9PlzCpGVkMYjA+bKq3Ws7uS2u91UoO9NEo+VehvF6/B8Cni5ZMWPMXfINBX69f8OvLoGhuFMF8/VDo'
        b'wGBMeUL9TdbXCiYBxmI63RfKKKWo0NBQjhT6KEjCFD3FSZjWgucUwZxF+gT68fwiCZiV4MhoTmvtOFwV57xgK66FqQXF/6ldFNnZvx6faoZr8xUYSAofEdvIQNVYTD2R'
        b'YiqpoiFpEsEYMXAZMUbrB+sn8tKm2JsfCZs7Yjx9cpgfCZs2HpaGwmxHjG3p+6zG75scFozCzMkzZqMw+/Ewl0lh8XRcFGaHwjwZOFDfdkTTaUTT9kkmw0VbuSTwcS6D'
        b'UtYcZTKUDDC/VPMx/vbUEJNNY4eswwQL4u/qTWuJ7FW/wn/GYiiHMB74B494+X3PclcKZIxK45DHUvj7k7UMSkP/rqrFiIbvM2mmhj+jxPepHEmnJbXTv3nRleTrLoLw'
        b'KEH0QkFc4lDwoiG/xXd1DVqce6f3Jl8xvbJ6yG3+iIEziqrsgoarPwOVKCjsB1YAU0l3lCKfsuQS/vpDhJQ3S8n0Owp/0rBV/GYlV9qLoFZp2Ig8fXYsVpWLduxz4mTg'
        b'zrWgacLBNLb472gK5q2q/wlvlZUiJ/4uL/FdAX1npyiS70rou7I4XEXiu5i9elh+nKuq8RquKuuVXNWpE5imBuNcVc3fcVW1iqkU7dM6/26u6mndVhmJHBiOU1WV0qRT'
        b'9P6Ap6o/gaeazpl2T4VwiDMLUpNX+KYuzVzx3P53MFWJq/8CSdWVZug5cZj3pHzCIvzusbydvAussYCxxR/2rL+ONHWlIVBOf4uDKo7k+vdZp2OPI8wpR8w6LXDFCFAW'
        b'oZIWuGE0qUKEHy8syo8wTk0n8UUjfX0jUvMnku4cCtxxgf/KrY7jINCxjDzXfl2q43TQiXnmyE9IA7dDwW+SiNGxyinAaM+CF/jS657hWBCAS/2/DQZNnwwGZVKTj7VK'
        b'02CqcNCdTXsDiQCVFBN7AwEXwD7aSPLSjLlsgvmHJaBvHnEQ4J1Z55vL4mMzDJm3/kmwofuMyxjqJxzSljk4aDjGOCUdVEl7ECJL3Q6W7nG87HqQw6BfaTSBKmvalAUe'
        b'1hO/xM4Bvb9HjNLsT+1Jo2siWhRrVzFaNMVV8kj/iJ7RGEpf1eh/Ahx97UOnyErQRpNc/we00QIu6/9amihmixjL/FWaaAqpH4xLxHbx/06U6Njw+xOU6Njw/dM7XP8y'
        b'SnSiRHgdSvR1guUP2J6vFBKvvv9voDwnE1BoY/2kXGxnj0Emr8FyjEd7lcem3+E/J7SzGPmJJyca44kmKKvXEzT+jLU5lpO/Q9vMTPsvaPP/HdDm2Ih7BWcS//sruMuJ'
        b'g/Yv4i5fOYD/C7v8t8AupUOjCueiH86aIQSoCPbG/46pCPfC3SG0OXngy9f3YADuYMNGfKgzk5n6GYOPTd4PO86pfdvlSEMxQ2a2zmy3tXc3z4i0SLeIt+BbcC2KLP6Z'
        b'tbLEZrqPQrJFwBz1BJdITT2WjOVndg9vPizujKyOcfZewNu1X/HwF9SqxUoXA5U50vRZryZncARzDYvgwTG7UlArNo7d7b3uJdnQBjaDrS/RhjKG9HnRw9Nh7fhhT1gJ'
        b'esYNaPNgP3nzHpYCL3Lh0aVjzD5HuAVWkDfvcRm+bC44DfsnownlYOs6jsL/QB+AFxGvpPj9fikjifDzp9dPz5a7UWqaFXn1KwSqLh3pPSsGY65Fj8z0Gpx5zRUD/KIZ'
        b'RPFdIVWlNKJleLBob9EkFJ729P8cBu+1JdKWlWTg5bj+jxh4BQmsScv1v8O+K1hEuz14Jffudxkfg955o4xLQO9MXjPr/g50J/PHtojJshIZZE9YZUpPXGWiNaa8eJXJ'
        b'FFPslDDFLo1NVpmyE1aZcmSVKSuxypSTWE/KbpATrzInhU5YZa5/1Srzjwl2kjvs/yfwdRM57OKlm5jploMmOwzX+i/R7r9EO6P/Eu3+S7T7c6KdzWsXeNlo3qB3XWMN'
        b'8TcAd38gMv6TgLv/MJZtSijRfOmpgp1cWJaWEjQGZUsF52kiuyv6mAF3gXaaGxMZCEvDbGPErCsrUBYMd2MLH24shpbLETthjLCRBxdVvIgBN9wKLyZj1T88z/g9aQ2e'
        b'LSA5MPabzweHYfEY9R22wXLtQmd0RdkOdJITvJLIdNgSMJmazqTAPlgnD/tsjAsd8MK1H7aYvgRIwZJAG9puHZbw0BKdWE4sRuvZsxZyXihPhwutcaQLWYu482dOWr1j'
        b'JpYNLOfZBGGjmAi2LNy9bHEhJhCgpfEpWA3LxClGz4+1jYkF2+FmzPYK5oWAlqhA0BbIs7MN4qFk7JngLNsJlEVEUobgsHI2PGdHe0zeBXfATXzYDhvGfRHDrhWFTuia'
        b'vxpsnPQAjKpa7lQA6vwwoorw4qSoJaBMFuyHm8CJQkecs45QRqT4ZlgM6seaLApFjJCogvg0WdAIm+E+YkJuvNGdXaCM6pKlxjCE2+bCS2sKiclJaRQ5pt+9io8t6AcY'
        b'sBX0WKOdwxliCy1KkabkEgalKM8lNvJZ4VTmrx+Gs/gMtDCMu1l4ZC8vl4DiD1e82GQ1f5tq0cUvL7xjeCy2Y0Hxka1WxXv9WnNlSlPf8/lkb0jGBnf/U4/TTj/64aZe'
        b'/G/lGz0Zb36yL5LTc2bduzth8KHNCW3/jKqzXnOUd+JkeOsB6819N7qf5WQZfgvL+Va/3F9/bCV7tWyXyUcz9x/9ahF1o+K7tQfUp1+vWvDA8ua3pcwu3ymf3T0zyg1p'
        b'zOI/0pgZOW9FzRVLvl3pN4kHWFYp33qv3WP4845fDRsfJS8T3dye11l1sfyMs4rw45+Fo+9zwjZG7N148vSJR5v8jT9/tmlNYlPjsfq7t0KvbLj//Frjs1/efu/jj47O'
        b'D1ST3nbq0Ec/yTwUSYe/CDg2/xRHlVYHn42bOcFQgsOOYWWb5JJjxjbSEA0ZZ6sxPvwY82khrCGnX4tCFbiowtvHXALDPWD/mP1FG9wJy6bbjJvi0UgmWBf/zIgiTLsO'
        b'0DAZDd8M2vEeLAulQs7QbvOB+1EnOuc93ivYuUxYm7+APD1OwZULL4Ed49s70DSdtrPaZJzAhfXg3GSLoKo48nDNEC47Ce62IpZyv7NXjNQne1AWLAcVNFQKj/JS9Axl'
        b'iIkEl1ghs+Flch7aVhmNwzLapmAeA425ZtC63pPe3p7LwLYd22CvUzCWHO0U7Aa1eaTOQzzhFgmYVAzYDLeC42JaVqA0bLAO5tnBkmDSKijz6hYsWLse0Gew54NecNba'
        b'bt0M23EcUx48+cySIh4ULmkTHBM4A7e8AsnUI2MPW2E5R/nf9BIcv8U3moBBkgCmTJu823oV/6iARtg/8XX/u/wjzOOZdnBj5cbbWpZkM+wj1PUd0vB9oG5IOET0EbvB'
        b'1GFnLrnsLdT1GdLweaxI6ZlgiFGFLMYB4StzhbrzhjTmjajrHnTf614/Cx+/7TDttum0ETl5C5y8h6d7k4PNY/dpGYq0LARaFre1OCQ8fCgqXhS1RID+b7FEqJs0pJFE'
        b'0qp0H1K3Em/X61c0rWlY0+E3bOH2gaHVkLXfNdlbitcVBdZRQsPoIe3oEQPTuvhD8c1R7QtbFvaYDdt6kNv8r2nhAyYC62ihYcyQdswDPRORno1Az2ZYb1aH5rCeV8/M'
        b'CrkHetMPza3Pr5D7REu/enFzikDLZzDgWsxQdMLQoqUjvmFD4QuH4pNHWQztVEwAUkuVdOCr/FeYOn9+rIR0hYn4nL/RFfyw4gD7AHmxifohYDaDEcT4nsKf/5Le4H8L'
        b'lJP4p6CcV22l/02UHCOakgN3gMtY/vwpJwec1X0pI8Y5OcumkiUSWh+MI3JW2jmADmqpz1wWmzKBp1lo7j6wlnbz4hFOGJPZM8YYOXtMCT+EAapCMfxGKhHWieE3lXAT'
        b'mZjVIpnkNaxnfG52VLANRcAd8CS8HO88hrdpXkkIN0hsbycokIW+4DTcNxueJ5Qbe3BAmn45eiB1OR90mudj08JyCpTCE2APefwsB3jSmubbzIbFGHEDD8NGwg/ZiOT2'
        b'XgK5CQUnEmjIDTwON5OLsBPug7sjwV69cdTNHrAL7CYronTp4Egx40YfZY1gbprgebJIUZsN9rJpIg24kEExrLiehcRKau8isDkS7guaTJ+B5zwLaKCMWzmlz6C0lyil'
        b'h6rEe9LsmFVTTChfPKzc15osNZWhA4fiA6kKinJYklWY9XN6CB0411aRQjm39MwpsmEvsKUDZ1tpUjYUpTo/umjOQXY8jZ6JgRWocB1wYCJ9RoyeQZMD7Qpp5TzQxBaj'
        b'ZRxAPabL7IEnSLJX02Wwz2HVwdVZNg/tuBSHQeNlauHu1dgYU2pNILHFDIYHSFJKjvA0W0yDAfWe8gxX0Ab20qyeDngA9LDhCZ6YCwNq1FTpJugBtUmECSMLmxeJoTBc'
        b'sL0Qy5roIjM22IJHdzgVrghOkseYqzuzU+BeSysJIEyXXSG9HFgLq2geTAg8FjTGg4EVoD2z8gMuk9+IWvn4d9TlBT+XfRCl8e7NkLS0R73C+3dXpttaZ2S2Wlq+Gee1'
        b'rsNKYefwli12x3a3xyekxnx9atZOlaor284smKpWpqBZGOeroeF7ogT9sywx+bF9dYHF9RR+v15e1rINQU/v8/tH7//Q+8N3b9eW/1MxffvlyuXPuu6ttnleoL/4jc9H'
        b'l47sOwMNv8i/sSq5fZDzIDq4r3jKsqUdRiEfRj9IDO1L/IgdHNWUObB3Serzb6fE7y4yn3l0ytYjZ47P8bktUxK3+/L6vHk3o8P3118s6H+aUlakdo8x++zakuQbulE7'
        b'LpulH+8//fmlk1lnl32vfDIqiDfXL3zrlIXvfrLgTvTC986nLoxOVfnyAwXBmk13Uqa9MaX01spFX4oiPi3rO/z8YUL58LXl2z4Oayt973FimKuvs03tVOP31xjFbb3X'
        b'uHe46sJHjK9qb8/ezyscud4md19JwGYkW38WnL8o5Z+8tnzHAMbHZps6ze1dfva3ze89mlfUY7A/sT4+M4/RtsmitTAq1PV7r5uxy6MWXXccUIp7aNX8nW7zd3Gq6aXJ'
        b'jpeufLy2vK1UyXHB7ZxV04fUL3z1Hnhjlfo/9L4azp416lSk+dET91+D4j9t7TELeDPnjhXFbql+t1m765vutLnUwku/PnPtuX9I6dlHvkeOGh/Uif9CudzWLUBX9r7s'
        b'4a3fPNVv61QaLrDojth98/KTU5f620LmeSVrfF05fVbLO06Pf/jkvurlHcdlvv6hYNfNpicKnfU/P5p3bd1G5XdOyKh4te2gdNOoosK+HQ23ps/flvrrL7a/hdS9t3dl'
        b'1cFdc3+xvCrT/WX4JZ/WhPN3WNURCmeE2Xvq5C/s91s6+8Y7T6qfpN99fiP2PYvNi+2jfzuXM8ObVRL3T5dzV531uV8UKZ8dGAzvj716fGQk+ObNF16R71kuGz2wR7DK'
        b'+kZnNLc/I+bRLYN7fslZuvH3/QRbVw4t/OL5s7dmhl8YCef5zPzByXeH6nrpetve3Dth8wLqb8kEHP8g50Cb6sPTA8YWKnctbqwZqXk31Py7tUoO3Z+El78967TtlbVr'
        b'li7LalzHdljzNKekn3XckBX+kfTIz/rc937d+uKN9fpLLuh8EDBod/37gMZd67kbbny978Z3pvbwrtFnSV8uZ286X+2/NuiNnx/tiHvHYj77HqvtuKJyc0YoZ1ZewNn0'
        b'c3crd3Yd2WbwReS17UWaLTevjyoZNh15pPejwmc/fW/jemvWj1o3Rr9euPOTn2TuCNG3n/c8+knmoxcWt14o/qh1bVTpnu3TXzbq/FTH3xW3bM83N+3rZ/+8Rq5n8yn7'
        b'hi1PdF9MjaK+33iDdedA++a82n8YvPekf/OTUK9n8SUb0ltHPnrr9vmHBl/+knLfcMX5t7/dHD3t8I0NVNy9G2f2Pf5N7iv3hUX35r51x+PTuKvfvvXZRq+7o8+LUtEY'
        b'+S37bnj0T87NZQFfDVArw357O/ztXzZ8nHHq6sZHjVW9edc/vKmbp82t0fNZ177g3QW/Mr6ru3nJaoX5SfVAj3Mv9h2cq1beFAk6FPxWfTbYnvHs8S//sC9+VP/5gR8O'
        b'f36i43Lgh/Vhavy39v2yWP+4ZdrPfeqp2pmrOgPdRs9WHfH46obOi/TvFdXKhxdG19zQj67cyLovKPL4eo73t/N+3bIjcnGkym+sH5uk5j19j7OcwCDUQSmPPXn34goP'
        b'jwFXjoAqss+YlQD7rR1WTMTackEN2WcoocjHrN2zJxNXFsnp0aa9B4vADi7abOybRFxJhyUWtNlxKey0QdvDiMmoFCVzWElsKi29HWlMig1aaJwWg1LQ1yqSA54PPMEP'
        b'VJ3MSvGEFQUELwvPyiuKUSmcYLv8ICtillpmg+b1UhblDoplQFcMPEV2Rcqw1UNMwNWRpVkpsJZH0xbOGKOCYiQKil0Dzo8xUTZBMd53K6hS5OYn21hKQFHmABotDFrZ'
        b'nuxMNNGLwSdiJgqooK2LF9vpsMFWePl3XBTYB8sXiTeCcPsSWEYjURigCVNRwDGjMaDIYXiKrTKFxB/jorB5ZJc6KxduH+OioI31ZTQ5vwSj7Aa0gXoiKIFbMRkFre6q'
        b'fMbAKEdX0dATVB87YNckJkp9OGhcRdu8pruv508EorC8YFkSrCdl9wxJYWuAk5ORKOrSK+mCdW1Ywmavs+NKoEzA0Xlka24B2/T5VqBDjDIBzfKgizbmPcrHPL8xjIkd'
        b'aCl6STEB7bCJJK0Hz64a2yCHwX5yRI0NztCEm054OYwdaqvIgZfgFlRicJyB2qdvDV3kTV6FsMzKdTLLIAXsdCW1uhCcBnUBsFUSkTLORzEANBPAB5yS5k/LnEBI8QgD'
        b'50gR9OXSCR4Fr6dhKQeW8jmMxbCCMpSSAp3gAjhCZ+QgvAjLuWg07pgIRJmTHU7fcAQ2LLcGzaB3EhElb20iXb+o06XyacN4dxliGo9aoZe82TYBR21hF+goEPNQQB+4'
        b'FEiqZ6YGOMqdoPeQ8oFnQGUiXXlo7TcdlolRKLA8D9NQYCUoJg2uD/clcSfSUNSdp6J89JPIi8GpQPYEGsq0AHAJ9sjTpvyH5zOsZcEuVJpxHoqS8zPa6Wa5DBv1eTuO'
        b'BAxlrjItRFrg2WhreAiemMRDWQoaposVHgfVMQ0lNGXjGAsFlqWToS23HJwUs1DK4JbIMRQK6EM5xlFT4HZ4dBx7HRCBWSgrY+iaOAP3gnq+GIQyHbTRLJQDdjSv6HS2'
        b'JVcChALOh8KmgnjScMozQRd/IgUFiTiU2FSwg/Qe03x5PtgOKyXZBfLgFJc2oa8CpxfBLgWwe4yFcgYMrKez1AOaQtBqXIxBqYV9GIUCDnFpHsIhcM78JSO9Up2wUFbB'
        b'TSTDeagSWsnyG+4Gm2kYSgUYIDHzzaO5aLe2ayIOJXueAS2DLk+Zx5eAM8DGUHAqA5wncA044JnBB/sLXglDgQfB4Y00QeHiorVop3ZpEg1FzELZAA+QJ1nMQ4KMhqGE'
        b'wH5pMQwlTZaulxOoK50npPQ40EdgKOAUg66XUjOsgz67YiXsioalNA0FVc8BImqswR4pfFEmTk2MQzEOpjWbzSjPh9G6n4ahWC4gOJSYBWJaDWidzYfHVsNyy5c8FLgd'
        b'9NMHUM7OdE0AzYTNgMYSVkufR6XRhh1S1uC0Kd1HzoISTTboZ0ruOVJVaCxANSGRYMWkElFN8mEdmTCk0Oangz2WJB4LCmAvExzmIbFUTINaCjwz2ZYY6QB2wQYpvDU1'
        b'sYSn6amsCexOt5ZksIATcIcKmmzOkGzPj0/j01OlPM1h4bJmgCrKwF0KVILty+jarIK1tjSHJcQmcYzDkgjb6Fm/EtSDvWKM1TiGxT8egxkcSdH0IhiEw8KALYmEw7IR'
        b'dpJOEAcugqN89ZWvILGAOjRCthGQgq1HFJdWmILqBZjD4qhKRpVFFpppumDHqknUFDNTSMOzchbEcOFFcHzsjcsYMAXuXkHzUiptmWO0FHvQLwlMGcOlwFOcMf7SWaa4'
        b'ouDJtaiusJ+BLawVG7hkfRUJtsCuNLgNd1YuRx7u5ASJJ38dsFkqALbAzXQnOp4aCLsMYDW+jRRWFh5meoEuc1rC70/jgDLQCwcm8lF44HA+ycdGeMB8/A0KrdtudYe1'
        b'SM7X0kNzC8ppx5iCGV40mccAraB7FYmM1gAb+OipaC6Ee6RBhzWSyaprWOsCQCMN4+pSirNGY2ov6oVogYYVDrCGWTQVnqR7eD/sVuJjRy6leCHZaRiCssGg1Kay1qO2'
        b'OvTMiQw8UIv6ZdlfgMaA07DFvnAFyZm6deQYcSU0TOMlcAUcyyE90BW7LuFLkJe8QTFeE7nSw+qcM59P479gL5LIGAEGz2qRmDLwQjgWrSWSlCm5LLCZMGFcQVPeOBNG'
        b'e/0EKgxGwqCF2jnSyb1hXcZYDoPgSV0JsE2jDenLLlNA99g4G8PBwGZwgEbCJIKzJKur5sImNs2D0YP1BAkDxngkMu7T2eAIVwxTESNhjFFOcURfsDOGTfNgQFcBQcKg'
        b'vLbSILrLOnF8UAnbf8eFQe3Su5SmuOyAtQw2qHeh2TBwW+pGusddgJfRGKTBMFYeKi+5MByxzDoKd6fDLpoLA4rlCRpm0WKS6MI5cBMb9TQp0EHQMKCJQ/eUc1rrCosm'
        b'wmHGyDAeqEBE1u5KBAOYCxOMBkMlTYZBC+xm0moJfqmwzBJsw28jXqJh7MB+cjWXC4/xUWe1t5Ikw9QjcUEWQSdc8aSB2TAhPh5iMoxaFJ2xhqVx2DcQ2XtMZMNMAa2m'
        b'9KugI24J/AlQmFLYikRgK5obsTzWz0XryS405tomw2HcYI8YmrZnPVrVlY1jYTY48xj+oMbjGVZKrpwL27h2PJklqwkWBmyJJ4PPTBsctIYNMXi+fcl+AbvAKY7mfxj3'
        b'gqeUyTrk39l9ak5W0EtQXgwV6Fc0UXP+NcqL3rC2+++ALhXSj2UoI+N/I6HFWqBtLdS2/TuEllcH/jU4i0at8r8PziJ+iNgOvD68Kaohqtn8eAIqMQ5DddDMIKbI5DVR'
        b'q4pQ31UMe6j3bwprCBPqz/h7fJSXzA3lGuX6lU0bGzaKLDwEFh6DCkILrlA7BOfov7CT/9/DTpRxTnF31xRqW+I+oVSjJFF8McJDwlY+qj2hJUFkO1dgO1doOQ+HyrfI'
        b'Y3hBQEtAh39rGKoejtWotLSZ+Shr3B6exdbRHQ1nzMA4lBkEh5L9r+JQchty/w4OZVSahVpN7l+mhgTXBNcX4De+IgsvgYXXYMHVNVfWiAIWCgIWVgcL9ePEoxknptSg'
        b'hOsusCEQZSW+JV5k6ymw9RTZ+gls/YSm/vgat4Hbwexmd7JFDj4CBx+RQ7DAIVjkEClwiByKWiR0WCw0XTJ2n6zQ1HVUVhpXKRqPj1Upg2l/hTpiMK0uvia+bnHN4mGD'
        b'WR0+HbJPKWlU5PCBhb0LxTX1wNoWkzDaPU55oJ5mYXssr0N62Cyyx3FgVu+sQaer7lfcr3pc8RC6Rw6b5QzFLhDFJghiE4YSF4sSMwSJGaLEbEFi9u3YnBFPr6syV2QG'
        b'86+uuLLiGk8YECf0jEcVj7MsPQ/jZv6LJ/kvnuR/iidZyJiN6SSzx+AkqxgYTrKB9X8bnOT/20ySQhbNJIl4ySR510GPP8fuM1O9FQy7fyuT5DVr0xJZCSAJb86/ACT5'
        b'HgNJ8AaSAElYGEjyGFuRaPwnaCJ8rFN5FUiEroFRXAOT8QcPMYsl9BUQEZtXQERsXgERmRyWRofZjhj4jQNDAiekZ/u6MMwGccBskHAGh7BBYmg2CEvJWMwGQd+eKhCm'
        b'R/O8K9NfQwYxkyCD4O9PQsfJIK6YDDL774NB8AMiGA/8gkbcPX5geSjhw0/4Ez8mAj0Gf//Bm5nNxEwQ/PmSCYK2nJ2wlmBBYKkNF1QG8+zyg3hwpw2DsgQD0jneMycc'
        b'w1EW/x19jpkgUycTQeKkxokamI2hTqgZ8mKahvKEUI0JvxRe/spkpbFOs8YYHSlmxFII2wlhuyHFEqUS5RLVkiklGmmKKVISbA1pJpUqkyJdTKXInJYdJ3zIklA5FCov'
        b'ESpHQhVQKFsiVJ6EKqJQJYlQBRKqjEJVJELZJFQVhapJhCqS0CkoVF0iVImEaqDQqRKhyiRUE4VqSYSqkFBtFKojEapKQnVRqJ5EqBoJ1UehBhKhU0ioIQqdJhGqTkKN'
        b'UKixRKhGiXQaI8WkWC5uKvk2HX3TLKFQjbNQfcuUyJWwUX2roPpWI/Vtiq5rrWHKF3PM7yn6ePGifMVHuh5eYE6yssJmDpJ30KiS8UP6K/Kwo3g+fY+Lkw3915m4Vcff'
        b'ZkxIbOzkGN/OyEvCfkhsDkMsocVGN+jqitQC4vU9b2VqAfo10f5H0gO8jVFqUnKGUUHq8oJUfmquRBISBkrYHm5CCq+zAJh4fm3Cj9A8bPgRlIZKRw7HrUotSDXiFy7N'
        b'ySSmDJm5EgbmxLYCXU5C/63IKEid+PCc1BUZeSnE5hblOS97ZSo5aVeIp4nsNdhGY4KLeyO/TGLuYOnFEVv5ZU80AsG2EmIzIroh7MXtMFbjNkaW3pyx25KM+KnYnGVF'
        b'6h81Em5DSx8OtkpPkjAZEhvr5BVkpmfmJmVj82gxKQpVATb9nlRQPj8pnRjGp2LEQDa2nKNLb5SSuhzNi3yjPDrjxO7HUnzNG/ewnDz+RPOP5LycHGzNSPreJBujUA7z'
        b'Hmt1TvY9meSknBUuM5JZk8QdOXW4Dn3sV6RNGQ9SZHDIIoHEJKaMtFBSQQNHtYSRpkwOW7KYVOm4WeJ6KXLYkiVx2FJK4lgla4OU+LDlpFBJuspDLHH/FJcxYci93ibl'
        b'dWZKqB5oC6UFvBCxiQ0eBEkk3ZctjNqSmKGhAfxq2zXLVLrjvW50/wHGgTTCbGyNn5yE5MMSlKUltKkQndh4IpKdNCn31VZ+KSmZtGGZ+LkTOinuzvmFqeKBzi9EI3Bc'
        b'0LzafH2C+d2qjEwUA4/TpMIVeTlJKzKTSbfOSS1IF5sh/YEhfAEav8vzclNwDdOjf8LI/ePDsLLU5MOwhqF8rO8/f/JMl+AHa86pFZzrnAtlnDtZc89u5lOZ6+UaNZbS'
        b'sz62sYFH4YVC0AUrYTd+/72CA0s5WPPLgQdgTyg4C+g4oDE/inhQj6L94Dk5g1ZpUAcuUNQGagM4lUSOSc6ZTg64BqaxlmRPT1WmyAFRUAtap4Auphla67pT7mAP2Jf9'
        b'44sXL963kqZQJNWN3ktCWFI6FDkDaegGjxgxaMfsVc4OTErajTHfAXRzmIXE+XIPaIFH+XCnMixdRZ+SCQm1k1cAfVaWDMoJVslYwz3gxFpVzzkr2TiIyYuNZMwyCEfx'
        b'yavdPfNgp2R0Bfxu9xw25TCZLW0Czs0Ve+fLdmbjy5hdfxE0gSP4/EqLIUrFDqdyFpSAgxNyEWSVH8qBndZBXDt8TicGVsNj4JCcPjy7lDbZ6WKCRtiFrq+Fx8gtci7M'
        b'XHgYHOGwCoknHfwyZBs3FLbDE3CXLax0dnBhUorrmctgP7hM0rDJB63cUH+wZ+y6DKW4gZkdBxvoR2xSC+CGgp3w5Nh1BqW4kZkTbVxohctUjTONXx1gu6PAUHRTeKDk'
        b'MSRflXUyslrrYRs5BQ02wyq4Gb8AAb3+sDTcFl4gb0DUQTkL1JmD2kI/nCVwDPZLHri2JEem5qOEQ7hcW2b+XHBEH14GO6fCs/AsVwPs5BqsZCugCiwLjoikUtNUZ6mx'
        b'SNc5akZ6gzY7ZIlNdewsqnAhCtRSBx2vSB1bgNkHR1vC0sB5EXBXJDa74kbDjvEOTI56hwVJTzFTgNtAo7Q07PUzAy0cym+VBjwSDndwxL4em+bCHtilsrwA9RT0rTuN'
        b'YR5kRR/TbQOVS9lyBStRF5CC+/0ZVuByCDn0G5UL22CXYj6Jc3qqP8M0ZwltN3YanIal/OX4QALFUnQHvYwlLqCeftJAPCzn58OzijjWplw7hik47YT6EzlFcmwjmw8v'
        b'kBRBX+AMhiZoh420z8sWsKfg5dNgHTjOMPXVIb49QQ3YDtpQl9mbNrHFQd+Gwpk4cgUrEF3eRTc6LOHZBodFk5YnN9PVWeMFS8Em2EXBumw2aI73JZsBcAl3xMmR4V5u'
        b'NEVNL5KCVVPYpNN5gUrtSJwODzailkHySJ4BL6Muezjz9uZMJt8CTaFhAb/djL2ZK/RU/bDwA9fcD87lbjgkpWz7jzCjBoUGTYa3vpWyvlV4vmfzfN+DERcsvXnNwec0'
        b'p86KvWyivM3iGmu5T59S+5U3Uq6eWZmQU2ZVqb80LK3/p7TP3v/uOfdTa/6ChN3vP7k9mHQ9/ZLmrcB3d+15AErf3wo+uvTryqZDH8eq5t5ReWzx8QVt4Y9qkTa5Z5JO'
        b'LB12CT8RYKSVpyl73PLh+afrgj//WGW9kfqxq7yFJk77ee9T08t9ZU8++jBB+UvTKzkJfPb2a37nDvoZmft+Gm/8j53vONTdmlLUD0asVjgVHNtiZRqbO+NOa1bYm1Wt'
        b'7vc/lb2pv7JQeFL/5pl/cizi3XYbGpxvGrUtuCOfcKf2ynNzl6fpysLcQ73Tw9ac5T2ek3dvk873MVMDgqvPl7/5zdKv/C6NJH6Y82TGl2cL3zrUv33/0KbZ7Xf9vjzK'
        b'8Ga5FT3d7vL+2rdjQlo6533etv/WlKYtUz80dbo55UL8nV2aP10XaNn8+vmpobXZH7oXf22YdCnvoOhYxPu7VL5y8m7kP38+0sct/rqhUDmBc/Wz1Sm7dywLXL18lZnf'
        b'jvXfWHylYBZ99r2gT6xfSAUf3vbTjy9O2q55/1yuLRjt+qDo9Ld+1Xd/Ci54c9emYHvq5/wRvayshHmOcx+vmXn5fNVXX7QpbnB5c9Vmod3Bd8y9t/DSRIJf5d+6c2QF'
        b'U3YgoZp545O1Msc3R27MMrmeXrz78/i1ytSKD97x/3yD3fOyyPpby6yfbkj193yx0efFO6dspCuTt3bkxBW0fK3Y5KJynkddPFd2bK7f+mseke97vzWQfL2ps3Dq7YVh'
        b'UU/Lf/zo2zALK8/soR9PfSFKDD0ZfeDb0r73Vyb4W1e8VZ99J3hLV8D11H8E7lk77dlUh/bj78q5fP5d/cZb8w2c05vLL+m8EDYn7/hxcSur08vAnjfwIsKgRz3l9ubC'
        b'PoMPH3bNUu7e6Jm63oSdn6bJa9MY+W76uQvDiW5rLil8nLkOfczf4FT5TH6jx1dR/o7f9Zx/+GBhv+qOvB/n+W41F3ntY6yOjqp39tusEPruxSIOvMgTrb/2ppvuzxUb'
        b'Vznf6qb+sYpn/3+Yew+4JrN0f/xNQg9VUHqvISQBIr333hFERFCKolggYO9dsYA1IEoQlSAqQVTA7jkzI+60vOBMguvMOL3s7gxOc8rOzv+c8waVmdnfve7uvffvx094'
        b'yynPac97yvf5PjvfEZ+H2x2vLx9L+uGnYxsox0Hz78L28GIYBzvXZunwhRlspArk5aCDlRYFLxIQH+wBQ/CsGxr1jUg97MSWvllwN5vigutIM0QXMYC0C3ZgOz8lXRdF'
        b'34mG4TZWBNyv8S1zFZyIwchUcBMeQyt8DTLVMpM5zB5EH86toFGEPrA7tDAIUaeM7RIaxMBnpGCoCimCXSIH2JuFLfDWs73BLtj+Lf4cWiDdvgXFxKDKdCHYlUWQmWCn'
        b'KNnHmxDw6FKl6+zhTT2kU4/MIglOdy5Og3v1cn6Dsb2wjJx/F5WCTnwuvRK2w70CHUpnDtsVHCliEB5HQbOLp25aliDFB6MsuOASxp3eANcIGMAXXnPB/hQxsmAywjdp'
        b'BmOk2biERSwwLewnc+DEwKskgw3g2EoJPpdHE6Dup2fz8DA8TmSLTc4hJ/OnfODAhNMWJ3iKqcNO0AjP81PAeTTz0JofpMWC20ErOMY0305d2IthJfjc3haefnp0bwPb'
        b'tGojCjVurjAwCWPNWCYMTk60ngH6tKMvwSVUyakZaQJ8wJ6JY4Nj8AoK6wYPa4eBm0DK+Ia6BQ/USeDeFNweacaZAngpjU05JLLBbi00BzkNzjNUQt2RsAWDUrE7On1N'
        b'KKMENhyC10Abg3DrdtNHWWYKkHbX5Ihyc/IDt7K1UDpXeAwgqJ9TDM+ir9tkNzTwCIMkSFqdBxqzVoKrwtQMn5QMFmW8gBPsBRqZ1rwJ9xRI0iP9MM5Cg7EwCuDocuII'
        b'kIEPrhDcFfatBW+lwUZdSkefbYiRM6S3c9Gn5oyEYGI4i1aCc6y18Ba4SMCi8cVhz1CFN2cuYtmCY66kBXVhX8hTgBw8ERHLAifqwF6SYRgaJJcJ0isMbiWgQ23YyoJX'
        b'I8E20j5mvAKuMI34FzprDa6zQLu/Can0SHANnNC4TwOD7r8DDRr7MYC/veBKLQHuYdielw2akM6EHWRI2IKOEvwGdoHryyfcn4E2cJZx1AN2zMFAr93pOhR2c9WMRjbY'
        b'ZwabSR3PiQSXcJH287Fk/aAHnmGBLu8aAnGJWFnKuBAshbsIatbSh0Tyq6ogDj/BCS6BC2nDq2wWPCcgEI9lfLiRICspNndKBMtpHuM0LRhezkViPAeqnAIulLlxYKMv'
        b'ZFp0JuhzIV65RD6wi0GsgVY22FVYSOopZu2634H4MYIfHAvAIP79YAupp5zICjRZ1vjru5wEtrLABeE0UhP2IfhVCjwwMdnToYwrOAlhWt8K0Ns1cKgeNK5YDi8Z1T6b'
        b'OGIeLRHcl5whQKHzEsCBSj1juLeCQboch1vBJQnfAO6qWbeCx6J017Gnw3PziRzeIfC0hF/Hq4kiHVu3ku0P5HVkPFv4gY2ooCk+cfBwCtibxceAdW1qKjyrZQb6wNCE'
        b'B87j4CIXLRN44Ay4xSQCzrIj6kE76XBzTZFab8yqhK0pGLqFeqUuZZzJiYZt2qQbu4PdppJU7NOUBQfgKXCKZWprTUQzRV2tGfvJQl1eRvBQeJSQNlgVlDABh9KAobJi'
        b'OWD3PKBglMwlsCUeb6WvJpZ8FJBn1zL+5pA+QOs9AkNkW0SyWK7gBp+gzBZEoJ7bmIUESUFjlGgCUTLY6g/3cihXeEY7SAteYgb0UJWDJJOnsVtIY1Gm9nMNODngwHwG'
        b'w9WSshz70HSCCuxGE82QF5BGNUTDZ6+E0R4csA3NSC+xVoOroJWBLvaiNU8jPxVchicEaQLvTKRFTOZz5oJbfkS61CrUwM+kWxxO0Gvoa5WpTfHmaKMF6CnJtz44oV3g'
        b'LDzD9A/n6b/tIVmBaP4cBi7oZMLjsJV0jtnguu0zo3XYDYdYcIspkBMoli/sAPu4+O1ERzaDV5HyvMBBH7qTYlIfQqRQjvLx98YMbM1A3zI9eI0NmufCmwwjQG80Wu5h'
        b'N18LwenfoLnQIqmdZ/u/C5z65yc2uB0m7UL80cENYUqb+vzG02TitzZtBlW1MBbpRQdpuSzgvjlPbWPX7tHioXSOGJTcjhu1SW6OezTxKHxw3m3XUZvEprixadZSV2n9'
        b'wSVNHLWjS5PWIUO1vVN7YUthe0lLiVw8ai9SsGh7f5V9MG0fPGg+ah8xOI+2j0EBDbCHmlktsxhgEwpInplbqswFtLlAaR6gDgzFwApVYAodmDLMGw3MV/rnN8XftxA+'
        b'cgpTO4WoneIe62pZT2nSHjegXDy7bDtsz9g3pzTFSS3ULh7Naehi2kNLB6lEFveWpZfa0RWDNlSO02nH6Yq8+44hap6PNL4t9aGDu6wcSeogknIeOnvJzeVVo84BUp0x'
        b'K/txE8pFhPSurbvSPXTUJkxpEaa2tmu3abFp0tHgtFSu02nX6U1a902d1O58eUxHUdfsjtkq90DaPRA/dVG7ecv9OlJUbqG0W6jKLYp2ixpxm3U7cNj5TogqbgYdN0MV'
        b'N4uOm4UDO485CeRVvUu6l6iEMRid5RRLWPbsXTEYQmXvR9v7jdjPUhQMxvQVDa4drqKj8umAGaqAWXTALKZKXWUxLUXtc1rmMMe/KnsxbS9mah/FHEy87TeUcitzKFMV'
        b'nkGHZ6jCc+nwXFX4DDp8hip8Fh3OpGLnIvNrSWnPbMlU2YloO5HKLpS2C1XZRdJ2kSq7ONoubsRu2e3lw3PvrLq7/s56VdIsOmmWKqmSTqpUJS2ikxapkpbRSctQWvqT'
        b'JPKl7X2flwhn9sjZU87qsO5y6HBQOYtpZ7HKOZh2xq+M1Q6O6A/3z/auTQlqW6f20JbQ9oiWiKZ4fKKt36KPcWIjVmFyt15eN6/Xp9tH5R1Ge4fd1rprcMdgxDKVsBbM'
        b'HHUoUloVqZ09umxO2Ui1x2wdpA3t61vWj9oKFWajtv4PXYRK0YJRl2qlXfW4NuXiM65DTbU+mnYgrUMsa+ha3bG6M4q28D+ShnqDg9u4KeXsiRtlzEWk0FHU9ukz59gq'
        b'3yTaN0nlm077pg9XjLrkoTAmpDkVud0LVcIoWhilEibSwkSVMI0Wpg3njzrl4nQe2TrLnFtC2iPaIpri8MH28ublDKWDytKbtvRWWYpoS5FSnDJimTImECviMJ5qIL0v'
        b'/bbrXc87nsMed0Sjglyp1n0rb7WtA64fla2AthVgRoYgtZ2Tyk44YidUuNB209+yE+JRsKF1w5gwbDDuVuJQ4q20oTQGljUSPkeZncfAIFTZRXR2kSp7Dp09R1lWMSqs'
        b'RAMlixkQdrzxKZS3EI9Dj49sXTvi5dMU7G6bXoduh1G34LdtQ/4fpVBEjVjGjgnR8Bso7CvEQIHb4rtBd4KGA+9EjQrzcCH4/6QQohE7kcKftgt4y06EC7Gudd2YT8ig'
        b'6y2PIQ+MJFGFptKhqSOhs4fL36y6V/Vm9b3qN5fcW6KcM2/UpxxJn6GRPhRJzxdh6T3V9rh7GYyZW2v4wVWWfNqSL0+9bxn00MFT6ZUx6pCptMocs3SWecjd7luK1M6e'
        b'XfYd9p2OLTpj9p5yHYWFolJheN8+Qu3iJbOS6vzZ0V3KGXPw1mgTpBDbV7asVDn6047+itD7jpHvuPCHLd60ftVamV+oyp89kj9b6VMy6jJHaTdHHRAs1SKoTnFXZEfk'
        b'iJX/Y33KyQPJbGHzHEWGGYNjOIZJ59u0/vuIhv/iM4I/E8/YMv67H48UPRQ1Cr3/eSP1JCuWxWI5PqHQDwY/OL4A+EGCdxrbdURULzeU8y/Rbc7/r+g2JxdggmvzPMr4'
        b'Oa5Nv4kjUXKm6ONUOV/o5I2PO4S+AeIJauLfU2/+SxJvxRKfYr+oxAos8Rn2hMS2WGLNSZxTdcUk2f7liuxmPdArLWeObF9Mun4sXd/T+nQmTHqEPq7KiSSI+SD/bRlx'
        b'1fFYD4xKnx5dlla/oKBXsKBaT6vRI8apYUl1bUPlHxBM/rvSVjHSGpZOHGW9sLBDWFjjp8J641qV1KNqJcdkT0/I/lMCk7Gk/8I98/rksSTMW4opvpdULSXEn05z5y1t'
        b'qJ/EGP4fkrSDelFJb02W1DZ/Mtf1f0Ys+QuLBbBYZ5+KZfNMrNiUuH9fqgVYqvMvLNXLkyqrrpf6F/UdqRRn1otmP4yzd2FNVIpX/h/wo0+Q5v6nhqoB4QEtxaycLybs'
        b'q/h7iL9lGylpfntpa+lzHYyQfTLK8D8lpx4jZ/3SF5PyjclK2lpDIfsfkm3BhHKeN7cGIxtKly6rXPJiAtKTlXMwFhCnwhzE1zyP+/ktO/F/ZvAi+Y2fyl9es1RS+WIF'
        b'uI8L8AY1qQA4mX+rAP97joKqfuso6GndPQUzcDKrX/nmFItsP+QNfMS4/KnYhZ3+aImXneFQYffZH31zl8ciG0Uu4KoBs/kI9/Kj4aaJzccC2PwHnn5cMUubxW8mnDWV'
        b'SzSbFTgM9vJTk8iirOyOrmleozR1eUG/Pv88CxUewgEU49NnUSLrX3Dq8/8X907U71pNKzO/uvejFG3iMDDvXAlptgPNYnvKoIP9WqRV/UWmCn/fJstZf7AImLd0aY2m'
        b'UQw0jVJHGuUFW+P/kfiD55uj9t9vDowWwz3ym9XUBFoMNYiWBi2mt5Olob5n8GLUThMNVoyNmuopyf06jv6khngeN4Yahb2eo2mq3zz95wMMY9bFk5rKMZMgXirgZnji'
        b'GT4BtoOjLLfpsJUgdQKrtTA2Izkwvaxm3MOKIsiESnAaHpQY1+njCCfNwWEW3uu8wpC4OZIIwbrJZYYpWWYUQwG8GQzhMxG4x1PMZ9hFMZfvnjR0kYnpfXOzcwUFbGpO'
        b'tC7ogHvWEcDOksSqtFQMQgD7nh19aVPe5eA4aNcGPV6hDLziHOgEV55CLwrhNlaZkyvh11tRGo0y84eHJlvQL5jJcK51Qdk8fGxDDpe0BJFxLHDeBJwhSI/yOXCLhktv'
        b'lZ0xC26Kh80kTRskkYKfCo5wyXY03p43mc+ptFuWT6pG1wVuRyXsdoB7eIIULUpflw32pZsxku6qzWQs37W0YA+8iI+QQAtJdREq01a+EB6JSvHhCXQo/RA2OA3koJGJ'
        b'uGe91gSjTiA4BdtZoNvUlbxKYQEpPLgYNgoyyfaxTgl7ao1ugzsu35CeURrcl+IjxBbxjaSiGWJUfgRuQG24l8eb1HO5Ez23Hvdcg0k9d3K/nXDU8D/cZ7m/67OCTNIt'
        b'12cQyJCTb1XvtLrMfIphRjyQW+gJuzQUMoRApmwpeWNQFwu2rdBY2RMLeyDX8CkfAWfhVqPV/NRJzQn3C0k3AEfW1BjD0xPnjKy14BqXeXENytZL0sGBBSI0CPRY9kvA'
        b'RQY8JC0AR9Pgbrg7Pl2H0HpgGj/cxsawG7YuBFufcZpgQhO4J5m8BUdc0PjYsuIpWQ1hqmmBp4mYJp6F8AQ8+BuymqnrQAdB5hGwHTyJcj3smJyHrp0pZ0zczdMmfIxA'
        b'BrrhQCamFp8cH3aAQTIW9MEheGXx1KfUMZg4Bl4B/QRsFAs2wm2gBzTyf0tZM3ORBn6GetZFvhDIPJ8jw4Gt8AqDb+ss1+PDvfCMB1+IhpSQJ0jNYKEP9jbtkBXwCDMW'
        b't81dDHaALc9z0MAuHQPm5dB0voa+AHVwKJ2lx7ZEpetpwAdAdaXgEv/3LA3w8GoNCwIXXCPqhBMgJFwZ6fhMOQ0rHbAbDRk9sINFeRRqL6qOaRChYB7gWAyGOzzP/wCO'
        b'w4u/4YDIBJt0YVP8OmZ89htaRYLepzqIVQYGwDnSrLEz9FGEmSWTNVAAOEqgVnEW4OAkHQc3wQNP9RzScfElTOfo5fmBzXDoOW2FdNU02MW8vYZ0xXnUXJs1TCOYZgQ0'
        b'QykRrgScrIcH+M9om0EP7I5hEGaDsNvkmeoAB0qR9jBJZCp9Cw/s8EXJTugdDIM8CHcxnXxoARYGYxWC52Kuyn028AR5syocDIJ9oJWfIUBjTWsu1pyWpJOAxlzQjzpY'
        b'NbyeLPAh7GxH2GtBG7zZ4ETh+dtW1IW8QhMnk1AwBBQb4Hamo13TBfsEsG0SJYwJGjfnSF9IABsdJ2k8uM/2OaWHFF6miMdmYJ4D4HwkaIQXV8KNy7Uw+yr6HpigQhAk'
        b'TSMcTJTAPh10eRj0sTGR62ADQb/CwVoWkC2GB9E7H8onBBwhX70/1RpQSC3o+QbW+f1gUscQkq6u4ZC5mW/gx5n71yQwDwcCNZorcPkcNxdv5uE2Q4bP1Hf5HPPD/BLm'
        b'YU2JHoVmMr6+Ht/N+bJm3uRJBmdCM2J8ZxpSpHi5UYKmSOtYa1krWRI2i6qgjrCOsljUHkMtpDnPc5CCJRuCZM7EfsAW+j5gLZfgqZUTs9x4oB8+v3JJ5cpldZGrw3+7'
        b'GVtfWVdailYfeLNAEikk9wSx/OzZ09iV+mhGhdvrMzxhU8aX0TNLlXn5t3NA0bAbLEJ3P5Lp2WbTKSzC3g82oq/4RcJtsR8eFAhTCEVMak62oCB5UnvumaVpT9DPNmBR'
        b'8Dg8a1iGlNsWMsRtwdFs2B+LdDlPAHcz6BEyXOxmaKEMWsHBauE7JyjJclR7ofP2vVVYnGUeY3FibMlXpw+9Kzt96E+XNzu/ZFWeHqecvvC+VfnOHJeFFVt9A8JrzEUV'
        b'n+w96rH3/YQfOTdn/No5/0q/u6LrGO+HeY5Xr4nfe3L8q7YI8eg/kiOdD7UdyDyfkjkvjLs1eYQnSV3bfuJm6oNu/wdnzT/Y2uIumHagI872pmClgT4QRBU+2Ox/TWvF'
        b'3yycaqJAtX7xTJ+1Wk8M7rquN9zvXK7/q7rwwZyul6JF2/bMDXbbbti4bP72rl/ESyprzKZkG1XHXLGO0mlL0HnjYvJL11u4xz//eJ7F6/NuH2sMvP/drdVRj0I/GVr+'
        b'XZfpnDH10l0neNYXb8f8vW3LbkdXVxfQ88pq/dMDWRUWMwOiTqYsp5zKXQLduI1Tjnz0zT9Cli4eqF6RGf+jyxT7t/76+brNB77cnuEzwvM+6l28bLBCWrhV9XqTz8uF'
        b'Of8wEt8sZJWd2/uKuv96+pazXXR8/Ib934EH9pWfr7dU1M41uvrLwndmdlh+99oaf8kFz763Lu3bU7LYPdPQ2/Snu1P1Sk6yi1RG7weZvSKo+GvgF04ff3ltuG1P42Ce'
        b'Za3P1bxNAf673twV/Gp3+uqf/v7X/P3gwnvXv1/z5aDursOm+ustH+8pFKQfnnOnpH3ZW1f3mv2Y8Lro6t+13vP9kFOeKw7ca53XWrshfr/73/pO/fi62Y+Vr4sW/YNT'
        b'fne09fGwNIfec/eVPda/fHLCZc/8Ku+m6r3GoyuX/PXU2ePXx9/800c3Y1+7utPtvdjppS7lva/Ne/VQcogk9b2SX9S7Dhs86Hkz84Lzu1d+KV92Eww532V37pu75PW2'
        b'etXijz95XTn8+e3hz3sSth+vfnv0SZXOV/vHB3YGjnjWzd6zX7nll7cKRnvOv60s/G5t7HGV7Lt30xtLfj5ndczh2Fcu0hCRqGVTTVfCK2uqvhGoG45bN9/xfvXA/MOx'
        b'qy5x0688euWXzz5d893yK6zLn538npNtEnGoa2hR97XEDRU5JaLBmXW/Ss5t/nnL+1frwNrepTte3joAf/Yv6Iv8NunnfwhfW2y00OzQxzdiBJu9r+jIK7fNSzn9zhur'
        b'3tx0ru2LyoKo7asD1r3z5Xdj76d2geL1U5e/c/0v15f8ZdtPb365b/ffrx0uav643fR1evmi2XDZwJGQR442875xUV2Jf3fX7rbhr4qaPt395bbuzOr9DtGf3PpshTd3'
        b'805w7Y7IPOeHlCyeu2fflxczbjZHdYimr/+75V/9Ay712fNCGLTc2er5mPIGz0eAXIt8Xa6DfnOykl/uHMTFFFT66zK80PoAzYbNQBcHfSj6kwiIK8HSk+vtAy5jRjpC'
        b'NGTLLgCKWAYDuXWJJ4FeIUW9FHZgsrlLGh7FXNiM5zEYpfUUG8ayBfu4JCKnGFwEB8G1pwg+FtxuuIgRVgp36cLesueAYyxwIsSQpDoX7nYH7ZjZ7PlJnR1kMGVgC+iD'
        b'ckO4lxSoNl3E06GMUDAP8wyCXkFvj8ALkj9imwsw4cCjcBM4QcTLMIebJPDiujgGPUYhBXgNDjEYvF1I1fVr6OJQVcKLNhg9dh1cZWBnrWjaeYPrhWYEZ/HUjp3PisxM'
        b'YQo2BDtRMv0MpyKqqF0UuA73UUyyR+Fuc7A9djIBIrhmXEiSRSUsX20wQSdIuAQDgJzEXM+FF8DOZb+hDASyunKG4ehEIJRjsrXdPhSacxyqAefYYgMjBpcGD4KTaT7W'
        b'Wc9Tk/pCBge3pFRrgvsQrcCjUa1j7sMk0ESSFVfBg4Q1kUVpe4CthDYR3BBoCPXgPnjY3h/V8278TUCf5RAW6JvNEJbWwx0RXGGw8fNkjQ1wCxNzD5pcKSSohnsKUlLg'
        b'QBqb0q1le892ZWC18kxwhesFe0HPc5R4UGHGQJf6F8M+sDccg6pqGbSaQSEbXM2Euxmolj9s44LuZQRzpQ3PwDbQysKeZzwJIguNi0gUFdwEpwkmi+U6AxwiAkfEwBNL'
        b'QQc3NYOvg5YzV1lorofmmwzG9fKy1fCUGV6w6AvThAZ47mYFLmsFFWgYDkvhALyuIbea4MyjLNDE9joc4MCDsC2K4D8lUFEv+T2zXRXYyAHtKHQLk9ulCHgTs8ahCWzz'
        b'85Rw8GgeU3/n0RzzsobPCpWyehUGzfIgg6KCA1VAYVvE/QM2WXAF7mBgdAecI7nFvyXoIzjmfQSu6LI2yRa0cBuM9NHQdGbFpHFJznkoQLcE7vMi4FZtsJmXwIJ7XWCj'
        b'hohWAE6CQRMNmxlDZSZDKZKaH4AH7SQMlWsk2IFawhPeYujEWoHClKuB1unAHbnT2C7L4R6SYWo22IyGOSqt4nkKNKNoJs3jQLHSyVVDgkYY0MTODDj4MGw2k/yW/CwW'
        b'tHPgTlR9t77FUzOujh83FUj1UGtiqrJ4C4Y6rS2cG5r4x0xlfqhDkIw3wkZvwlSGZvi12Q5sczPAsPlloxpqwV37JLxujPohKrBuGtsZdCYxcL6TcDs4jGqpcYI/jZCn'
        b'NWiIgi1RZlc0ZMd47XDCjHAdnwJdDM3pZrgZ7lwfCBt9MpESh/tRIC4azfBCGeqIOIEF5fCUSwF5v4cHdxKPORfYsHMmgx1GmqMJdPIxB5wjWpexQQcrG3Sh6sCpLw5B'
        b'uR/P5mf5YKc7BGbOhTfZqGsfhEcZtdcNL7lxvZPAZbgP1VkGazpa598gPcoF9qAlnaySqbfnkMegf7aGZw22gGaL7D8E2y/x4jn/32Py/jt4C2fq90Rov8PvMRN/g2fT'
        b'+dW8//bMn+zKlqDlxA9knv9tfDKL8gmQ6ardfTBArXOOjK129ZT7nwxVC8SyRLWPf0fCI82VLEHt7cdgqWS6j1zdZQtPRioKB+ZcnKPm+ysCBxP7omh+nIqfSPMTVfw0'
        b'mp+m4mfT/OwR/lplfrFy9jxl5SJ69iI6v0aVv5TOX6rKr6fz61X5K+j8Far8tXT+Wlm82pMvr+9d1b1qxDNYHRwxuFyhLddR+4hVPuG0T/hgwe3KoTm0T7rKp5D2KVT5'
        b'FNM+xSqfMtqn7GuKEhSzlRWLVBX1dEW9smHNOEVtYMWzH6PZCfOnkpXAfoL/ZDN32cxdAXNXwNwVM3fFbBlbFtChrxZMVxQMVvWV0oIElSCZFiSrBBm0IEMlyKUFuSOC'
        b'9cqCEuWcCuX8xfScxXTBElVBLV1QqypYThcsVxWsogtWqQrW0wXrUWqBHQYkte7SCfqkOFoQxyQ6IigfTlLmz7qXpUqfQ6fPUaWX0+nlmkjefgqPbpHKO4b2jkEt5RvE'
        b'0KTE0L4xKERIh5Ha2wc99xH3Zp3LQlXo5YOJrM6aKHJVnpG0Z+RbntFqL1Gvcbexon5gVd+qt7xixrUpQfhjHcovWO0jlK/qzlDzfHvtu+1VvDCaF4bE7C3pLlEJomhB'
        b'lJov7A3uDtakoPIKo73CRrxiBut+/2RcmxPg8Q3F8fF8okN5CToaOld8rcvxCRrXocRB44aUf8i3tsZ+LozQ4w5UUOTg/GEdOjKTDsxSBebRgXmqwAI6sEAVWEwHFqMW'
        b'DYphK0urlPOXKGtX0PNX0KUrVaVr6NI1qKXKWDG4pfAflF4U7SRWB0aghlqqCkymA5NVgVkk0Xw6MF8VWEgHFqoCZ9OBsyfChmP3Q5V3sujwfFX4TDp8piq8mA4vVoWX'
        b'0eG4L0Uk4L6krJEol6+ha9bQFWtVFRvoig1PmG6k6U0yttI1mHYKeYRqz7HbUcWLpHmRKl4szYsd4eXcnn930Z1FMp0xV568qnfR2UVj4pBBgkq7vXy46s76UXGBsqiE'
        b'FpfIYmUrO9IfeQoxO5tMSx0UxtA1qYLS6aD0kaAKZXauMq+czq7AGYppp+mohZjWUQniaUH8iCB3mD0ceM9gopv59ZbibhZDC2KePSLEXZjtTPNI6N+7sHth79LupSPC'
        b'9NtTbifdsUVvgjq4OPDT9h8RZNz2v111J1QTa4LNLZzmh6NH0zv0cPCi7qLeOd1zNGFE4t7V3at7N3RvQA+COwwfBYRjVN9AaV+pKiCFDkgZCagYLmQo80rpjFJVRgWd'
        b'gQoni6Sd/HFXdOh2kOmoff2ZroIUECM8M2CSaEGSSpBOC9JlBmOuArWbh2xVR4bKLZh2Cx60UYWk0CEpoyFp993S1aIAhjgr8b4oUZY0OaTlLbshO1VIGh2SNhqS8ZZb'
        b'5jiH8k3CTqyF03tnn5uN1N2k8FMxtdrT1N9yS0fhhaHv+wYo5g1a9y0e9Y3XSMvIr+JF0LwIVIqgCDzoBtb3rR8JKhmeokyfTaeUPG1IV3elR+Coa9Dgc5hLZXbJSHjJ'
        b'uCkl8lP6xdDCWJUwmRYmD5uPCjNkSe97C+Tze3wGzUa8QyfGdd19r9DHHIovZN6Meoei3iSv7Vit8gyhPUPue4bd1h1m3TFQRefS0bn3o/NRKWNZKaxhszs2w4XKGQX3'
        b'Zim9IuW6Cla3gSJpMKYvdQyltaInfNBvhB+uFocOhPWF9UfI49GlSpxAixNU4tQRcao6IkbBVgT2Gbzv6S0P6lyrqEV6eyjvtiVO+FqpMjtnJCIHaaxBVp+ByjeW9o29'
        b'7xs/bKnMyb1no0opplOK76eUqP2CB836bAbrRvxibhcO59yZpUoopBMK7ycUjUXF02QrajS+bDSqTM5W8pGqCX/kJcTFVgYV49p9Rm+mqdxvOSxeKW5Ivn+vsFuIdKO3'
        b'Xy+/m49vVN4RtHfEiHfhbcu7tndsVTG5dEyuKqaQjikk4VTeobR3qMo7ivaOkumOuXp3z1eHRN/2VAanomG6jnYLeN8rSBmcTHtlDceiH5n2I98gmfYpI7UH/xT3cSkH'
        b'fU5/JIRJW5K1y0SsYf1cG/TngVsiF/3R+DN7oF+/sqKyfm51jeSBbmn9ynlzJZX/DmJT49ns+VkCc4Saqk1RLzA74OBNwFAU8aeN1JO4ZBaL5YR9nDm9wNnqN3gb9JgO'
        b'n+rhBnJ4HLJxW46mq6fXCxkXEBP+Hy6C7cRyfcYc2J2mMUFkoABzTPksygZ0aqHJ3H4gYwyc94BT8Dh+gKalKQKwOwtuXKJJzzFMCx7yjuexGzQLxwF40RWcn5RdJtxJ'
        b'cuODvqmTc8M82k/zKzdoIIYn7WgVeBGff7RkpYHzXskZwpSMnGXYTCknmZxIZKC5cdlUPbeEauK+CW4GZ+zTMmFTzGTTbj7cTYgQ4DnQBw6kwb0CL9CdTxLyC8hJXqOj'
        b'kTHUTYdqAL0k80ieEM2P96IZrQxvoqKpbiGTs9dzJ6qzQaueCd+W1E0DPFI5qWaOw47nq0YIb5BjEnARyGdJJpICTVaa1GZovJviguEVfNUGPXCS50P6arXOxmVsSTyH'
        b'ovTbCm4UvrNoNNviVlDG1UsZUaqGRYUDoS/tdXZx8fbfbsLRNXfUSqjo3Kw6uUK5oyLd3lPmIk1tvvFZ9Pef/Xm86O/lfy8NT5H0H3o42GP7ZYf1pw/f+2pt+8O1wnXy'
        b'xaapxsNlJw5+9J7N2JtLQrYOaumpcr/Nys7SFT9M/mI/6OphfTx26sSxFOvOP6dtVVufWXfuu8Jf2Uf1a0M/mLbcoPlh9qdqKEmq//bXsN3BaUZPdofOSI3+sHJXadEd'
        b'PZtXLzzKc90SWld4f/Bjz7F48w37QavhwjWJt5de2GN6WTweZvlNmOXXb5+2s3E3bF9+8Exb89v8r1TcIe7czDecrzjfecPr6yIX2+Eiw18W/xLm+MpbHdV2iwOMg8xf'
        b'OhzyvVGRkc1Ktd2qWQYRxw/6Lj8UsVg53bgoqfqc3aySJidh8gfKmE8tD99I+ao79VyX9yaT0NLcDxuMfP/qbzXYfeTgg7LvS3x7eAU94Oybm470bNj5jwPxy4tc/iJf'
        b'tffthR0B+v3HvvtuvWdwlPOiXzf63KozKK779q1fwcqMlscWY3uqvrawiyi5/9Kxb79495Bq/MyNot6/vb4moHf01f57T86ENY/Yqw76q16yXjrX8b38fXdO/ePmMe28'
        b'byvvt4f89cvilD0ld77JUL48tKzxI+nNG9vlazdEKI+tTfgAno0/88OX+kGN3asjd7uarPp5b1R1xpQZr3804O6ze9QxQ/DlXvOQqUGH1THSayFSqr/rRvRY0E+7rm57'
        b'/FN0x5o5smxxgPTLnKoYY4Nz66X6ftOkZQ2dFz5/z/bT27N+DDt7Q/KplKdIvbuoccbx0PuJbTmR5//hIs1MU2cmySzrX2uM/avH/eCbfy5rP5928VLzob7qTQ+63hC3'
        b'NV67J+4Moz5bYrb77NR3ur73/kT5hdBA/5PRLxIXVFztfeXUkv6ujm2f/a1jH6yJSE9dseuXtAs5879fMyaY63noh85TRy4nJF1oPt+78qLdt/lF+S/tKlzhsVwi+OZu'
        b'SmCXmSytb99Lf5srejm41bPW950nwR/br+WMfTbOmrk2b8q6IJ75e7pW9p8sMv8qecnL52O/O39nVvaYu7H9NNpE31arOHqJ/uZuB+FffqgcHaif0rg0cFr7d9scsneX'
        b'+sKuq79e6zmo+mjNJ+6vR/xqNO1Vwx/mmfJ8idWjYQi4+k+tHuGZ6AnDRz1juC1L41gDHkEK8JmNJdjKZoELwYx/3DT3+me7smilfIoFrsPdYCtZOs8AN+HFZzZ+Rc7E'
        b'yo+Tg/TeHmZz7yZsmvt0DzWbg62gt4HjxMtAPBiC8ucsQGcsneSGFmnlHWRjgJtt/mz7Cuw2m9jBSgwg+z314MCcNI0DXlvQFJMymzFgPGWsP2G+yMLug1zBvnyylTUH'
        b'7q+fWOvzeaYm4Cy8RNb89vCwFrgUuJzs1lllwMtc0FbhzWdc9aCScc3ZcMsMcIqUzMEfHIE92th+vJbHorRXsGBbDRxidp07YUsMtm1E5fcAgxQYAh3gOilMWYaNBHaa'
        b'kX3H/ZnYxtRgBRv0LII7SMwAAeh/zvaxG7axVi9LZUw1j4FDgVwhajx2IcsNKMLgYT5TUvTpWqTZnqrWpoAcfX92kDJMA0dRi/Xzc5HKnWQhW7uQtK0hOGZNPCxRGB4B'
        b'5eAwC2xeDPvInopBVTIXKe8uMPC7zTjv2aTjaEngDtR5mp9t5+HNPGz9i/vGQg8/Ys2YmR4P+idZM6ZrvBRfBVfgEbzhdBA2PbfhBK/NJtJFw7NIpHPJT/fXprFdwE2N'
        b'TxceOAYVEuzgHNudckC3VSULfaUGrMnbyrnwKt5F34t3uDngErwxhQVapqBOSfaiTsFztVxhRh0Toh6eEKKszSw4C4HMkYgWBHeBVi7ohq1g1zKm2vSM2BWwHx4iZatF'
        b'8bbD/lXJv3EtdRruLSajENXYELj1x0QIlQ7PqBD0wPnMTGZ77XLeXAnf7zd7w2isMU25Gu9TwxNazzaImc3hrbCDdIJKeAvceLoDPGUhCzSb6ZOOmp2JesQx7FpG44ED'
        b'+wabukiz4Qo3hYBGB7j1D3a2QjVeebbUoHI1pjFjOKsYdLPgRngVHCSpp4FDsPWZWSzYMZ8FtyyTMLvBfSWwk0/8qyXD088TMCzIYkgF+kAP3Prcvhve76wIQEPNqlLL'
        b'ZSbcT/pByFp7Yu4OZZqJh14wex4440iUyDQz0I3tfTWzLiALmyimo5UWPAvaIONrTRf01MH+THATd1XU7tibjUE6GzQFMKJ4G8AdKJ35upgSB+x6HmDmO0vHnFP6LT5Y'
        b'N2kA/X+kXIVRk0yGb0I5yRTpgyA8ebKq1kyfwH5dyngWxy/LifGyMSsw7ff5ecOda0CbNrjEn8G4pNkcBVvIdPWsURbchXsTSYfDcU5dqzlCAa0LKsAWTJTxlCXDL+R/'
        b'dGNS7396Y/I3nLDMmsOJ/UeGYWTNQXYfW9Ca5Eey+zi+MpFFObi0lxwvaUoglpinbaTaamcvzODf6SDVwdadUS1RKlsRbStSBI7YhqD1cku82t7lmeGromDEPkzt6tYS'
        b'/xG22Ewadn9TdE+kSp1Do/+iOaMupUq70kfiYIZ4XyVOocUpI+Lq4YI3Z6FF78wFoxnVUh2lo4i28h3j+yncB3h9vAFhn/C2+13eHd5wIh2bN8rPVxYW0/xiqY50JW3l'
        b'peYJmY0yFS+a5kWP8ApuJ95NvZM6vHw0vgCFWd5irBaKMY3+iDBusH5EMB8JJbgnUKXOplNnK8uq6NQqFGw1beU9xscbC7ZDtrcchhxUIel0CDYT5edN5OTi2SXoEKhc'
        b'/GkXf5VLEO0SNOKSOxhwK2IoQhWWQYdlqMJy6bBcqe4YL1Cx4rbWKC9hhFc0PE2ZPZNOKdLIwvftDekOebZtM8LPvK19V/+O/l3jO8aanB45uXcZdxgznOWoEXhCZhMj'
        b'nOaFj/Byb+tg49nhwNHoXE2iKDzhOPelnXyl2mOObnJthcWAY5/jiFe02s0b+5mQrxh1C5ImqL1FKM6KFhPUCgORfZEqcTItTlaJM2lxpkqcQ4tzVOICWlww0QyPUE9A'
        b'HQA1vyPeHBlxDBpKfOTkgbN7JqKaecDkzzxSOQXTTsG/eRFKO4WqnKJopyj8wrDDsMukw4Rx7jHilDaojdnmbxkPGauC0+jgtHF97WAHaSLem7Gb/sR4Gcva5zsK/45X'
        b'cCh3767MjkyVWwjtFiLVH/Pgyd17Bd0ClXc47R0+4p15h3M7BRqPemRJuY9sHVW2ASO2AWOefHlC55oRzwTFotsxfUtbkh/rUF4+8hSGRVvlE0f7xKl8kmifJJVPOu2T'
        b'PuIzT4ltbEvo7BJV9jw6e96oZ7k0+X1b10fC6YpCvFc367b1XYc7DqqYGXTMDFXMLDpmljRRFtSSpRaIFYndc0YExYOrbq0fWq+KKqCjClRRxXRUMQoR2JI55uotD1Ws'
        b'ol3TbieiH2n8GM9HXtTjgA3ex9xQpfqOc9juEerg8GG+WuD3WBvdPAoII3+lCeN6lCBQmnA8Y8zeSWZ9bI68dsTe9yM3r24btRMPRfSOY435BSgq+23VPkEoDrp/FBbD'
        b'XHxDsd3jWS0JqPgu/PfdxMrp8eMUy72QdS9emVPwapo6Ou0xB9+rs2YwFyg/HUrgj/NjRvaoS7LSLhn7YnFrX9WySuUoph3FitS3HKPQM08flUcQ7RE04hE9GCBNUjt6'
        b'tK9rWady9Bt19FOLxDLtU4bqgGiZ9n0n/0ch0bcchxxVIRl0SMbwijfX3VunId4PnocDBKhdvbsiOiJUrgG0a8CgBd73o13j1N7CXu9ub0XhQElfiSogiUb/vZNlcWph'
        b'qLy8t6a7hhbGDxbcF8bL2WMif4X/uRUP/SOVUXmj/vlKn/xxA8rXXyWKHhFF47finpWDzmfXPgyMVcYVjwbOVvrOVgtEKkEkLYgcrKUFMbfz75beKR0R5Kt9pj8Ki74V'
        b'ORSpCsuiw7LeDsvpTpPHK9zVounydbeNlbkFI9EF6qSUu2vurFHmFdJJMxXaA8Z9xkjx+MaPa1PhuSxU6TzhuDMlSmB960GJwpRhM0aFBUqvgkcOrm3cryWoTXwecygH'
        b'/o+EJn1rkdEsfdbYlCD0y+xYmTJw/XTt32H2/9UPiunvdqz+G9+PdyYMi/H+1AoM+7fFhsW22LDY9kUMAL7DGZ3HVmdWdRvw9Ub8swn//IR+HkwtxRSq5fXMtlgp5kut'
        b'XjKf2DzXbcY/x7AZkisHBdXVWMQ+MHze7PQB9zmzzjohDr0Tx/sZ/+zCP8YsjN57alH2QFdjtPXA8HkLqQdGk+yNiIUKMYwg1cSb+r93NIlnsH9AAT/Rai1aqNUmMUsH'
        b'4cZah0T9ATPAGxqZjttR7jylofMHRhYt7h0cqW13ZV/ckMVQw528wUX3AujcQnpmsTJnNj1nHl1RTS9crCxfogxeqhQsu29U+4RdyjIKeULhX0zaXscaJ08ex3MmSNiT'
        b'MAl7CmtnPOruNi5jpgK1hR96ZCPemYqeWDqOmXqrLYLQE8uQnUnoiZ3bmKlIbRGOnthF7kxHT2xdx0yFaoto9MQ2lrUzDT3SpB2P005k0tY8wmlbiMkTc9sxUw+1hS96'
        b'Yu6/M+5ZmBgcJo6JZuU0ZspXW0SiR1bRrJ34Q2DtPGbqw6RkLd6Z8kxKEZbS73kpM7GU2Swipr37mKkv88gePcr4Vo9l5PqtDsvI7olOMcfI7QmFf8fJL0Mdi1Ekbm5c'
        b'yW9mxSzKGsrhZnhOqxJsBLJJaNWnTLXYIO6wLrFQwtzilMYkRr9K96m1ktZ/zFppwR+ZwEy2Vpqf2ZBFEZTvXkOx73T/QL8AMRgAivr6uuW1DRK0dFDAS/AivIKWK5dh'
        b'v4meoYGxvhEXzc13gj3wADycl43Ww0cLtKlU2AkvwCEuF3SuJLvDC0AH6EsCmwmqtZGPGbrQmq6RQ5nD4xx41dqW4InBdjZsEmM6Unie8qP8MlYTxL42GIgnwdFPONzE'
        b'AZvrULxezEh70LcBDxI3uMVArEWBQQ/Kn/KHjZkEql/sAY9MZLdsoSYazg4OpjL53YRnIsVsCnYbU2JK7Ab2MnvOPeAGWtchGVFEDouyKAQb3XFuzUUNJui9Q4GbWIda'
        b'F0RNp6bbwz4G1t8KZE5PSyc3QBGnoNwacbR+b4b/9yLYBI+JsZlQLxVABYAmCSleMqrYHqZ8okSM0+WwKQtzHFEKGol9BTyOluSdYm0K7gT7qUAqMA7uIlHRqrhzAZOn'
        b'KAGlTqKyOIS87SKpGdAsAO1iDrXWigpCK/tTBqRmVhXna2TVBR2oVsBRtMgawvG21TPRDvqDfrEutcaYCqaCuaCLwYn3QEXC+mhGVl1XTVZNCSQKlIt0QD9m0KdCqJBI'
        b'eJnUy1rU5rsmGsEL3kI14jLReCecSCuYmS4A/VoYJHOcCqVCE+BJhtX1dCHcjbLC7YZUsjmScD9pPXCUy6DPz0E5uCjRoszgYSqWihUx5gE+4HLQchbJEkV21TRCDexk'
        b'IkkF3hLU4rsWUHFUHByEgyRSJrgeyCedkgM6wikLsGseboFcHmm5ZNADLqBvOTi/noqn4kEf3E+qPw5ctWDqEWU2C5wV6c5DdYnrkQ22NGDlbrYhV8KiDOFWKoFKgEN+'
        b'pH+BAbililQiirYsRaQ7halJeCmIZFeDynVJglr7KjxAJVKJIfAYc1TTDXfAIbhFoikcrlJ8ydFUaC04znSXU2iQnpdwUAQRlUQloc6wqYFApI7NQEMLx0CVfRFeqIEX'
        b'wXXc/F0otmEd6dwJBSkSXUoXdFHJVHKkDWnEFZm1TEPAi76oy6FI4ZosYQc4TwrqOCsLosafD5uoFColVYfEAy3gbLVGWPSncxUfVxAzBLdWkPYIA0OOGKkJW+E+KpVK'
        b'XbeIqFTvnHXwEDz2tHJFogl1QUbULtDNlLTdEGWLmvMaOEClUWmgF7YzQ/gQGFpXtIpIvQVerNNEhKfhVcZm44ID2AH7cZMiVZNOpYMzYBsxvTAAbWDXRO/RQlW3mUQn'
        b'rYq6y1nGuugsaEmD/SzUncAmKoPK4LsyWmArvAS6JjrSZjiEY4czrZtQzPQIP9AC+7Wp0nVUJpVZM42Iu9p0ztOihobogpMTjTIzjzGw2gguYlQsBxtDZFFZ4Dg4wgyS'
        b'C9k2Ez1J15kyr0dDlLRLIzzAKJ1bsI8H+3WpWfAqlU1l26OIZGPrMAd1JxItFo+uxdmkWQyTiJAVuhu4xBkrlUPlwB5P0ntQ5Q0uYHrPJsxiXUfG5GWUEsqvk8Nkt3cR'
        b'PMZFg/kKl8qlctGLm6Ri/JGMR0mlkKio+7iiWiajGak0kic8JJnDZVNBrlQelWcFu8l3YwU4CU/Zg6ZnnYgokomOUKDLDOpTq2AvV4fiw8tUPpUPZPOIBQxS74fgNjgg'
        b'fFq3GpU+0Zy7kfLGqqthNeznsiiwCWymZlAz/FyJtrMGvYFABs6TKGBLHdOMXD0my/5soOBqU7FzqQKqAN4A/RrjMmuBRkSwCVfQeSQ0UXYXwAFGs+7jgRtcDpWpTxVS'
        b'hUvAYdLAdnH1C9NJL+egWVcQ7i6MiQ044QPOcnUpuAleoWZSM7lFpC0swNW1mhrhoI9cBzhJBjIztHZo2LQH0De4DTRSGMgso4qoIvT9PkaEYMND5qBRi1oIb1CzqFmF'
        b'5iQvHugDh0Ajm1pTRRVTxXCnNtOmckEFPKiNtEkhJaTwBlw/abAYeDAaHuRQhnWUiBLFaUju+8A1cR45V9mODe/skOrBaVcXBcODaKDujqb4qJ2k8BozgFsswc08FlZ1'
        b'pyh3yh3NJTYzPb4F9BfAg7rY2+1JypfyBQcWkISS4AGwFVscOSRjmyPYt4iUKD0mIA+JuCuO8qA80OzkGs+AaZDNPnAHoyg58OgaXE9oPOKv+VxwjFFSA6ATHp6YlBxD'
        b'gj/9AMcDOdEJzu5AyigEsBlcg+0atcmolMvgFmMjdiMqhTQ82wlj1vuBFCcRZkzGKezIn85kARvt4QkUc57m63k1idEce1Y0aBqUD9um6cLNT1XsWdDKpHEWHslhxICb'
        b'SDHgUSFJoz+TSeNkDNzC9HK439KZZKJJoxnuYSYM1zKQ+BNDKQHsQMNf020kC5hcLuehb8Sl2on5QdxEOYfgMR6LGJ6JwFnrNLjLB+5Kxt5tQWsC6GWDTWHwzKdkZtlU'
        b'F80zIFZbV9ZhPwjBYcZUWbp9pD1jytVYakRZUXrhJtllhhXrdZmHbkH6lCm10U+nrKxmOLCBebh+zRTKjSrLYFFlsxcmOzEPK5yxTfXKcP3oMsM/eU1nHhoZm1B2VJmp'
        b'rm+Z4eJV+sxDkZsOmuX+UKntVJY+a14w89BgjRnlRGVncZeV1ZwO0ViXuXhhi7VgT2PTsvQ+Dwnz0NnbgvKipAFUdNlaHfEqTZpTce7Brroo91MmEcxD04XYtk1WokOV'
        b'1UDLZRSxyjWNt0QdNFnfxKlstr62hOKx8xPJi5o4nIRvsFF0WY15Wi4T+vvpukhWtRPXqawmuDyJ+rS1Bf+7F0Uy+Isdfrss1dCpzKepwo/6VEz+fRNFxlyBL6aJRp/7'
        b'TiilllJL4U0dMkAlOfAEX5dyMKFWUivnwVbGOpYxxYgOmuhtuVrPdTbLOpLfD7ZY9uCVRk5ldj15dkwp/5qP60PtyI4uC08LW8w8PJo+k1JQevbcsjKbD0TzUSkzM6vt'
        b'f9JiS3zQGp59JGjboXsS2wSLV64VHzj/+pGKVdNn1fDfYM9NmcnWSh7ebH8kWD9t3rLkQ1rfHs7b01PX1A3kc9qDd7V6T7N82V3V1nZrJ7/w7A+WX2fsT8xxjskPuPX5'
        b'xzd6b61/p/O9+b9mKwvW9ZQ1PVAlu8a9UXbkNZekT3KcGqWun+a4vCpv4soPNI4P26y9uE9nLL5xNvAf2hy4Sq/no7l2Y6rZn3rt63tid8Jz/4faXydcj7+5x/yjlOux'
        b'N3erhlW1u9dylh5Y+v70HwPfdX7vZeuvfd51ffP98FUsy3tP+hIvfDhyc/2px6zIl5J+sDrat4k/uHvRD1rtka9FjRTYBsy0v6T76qbWv9tLf7hR/P7ahXXrlZHK2r90'
        b'fS+zr/BwbZr7yWsf/fDhm1MWH205vmfw9VWLanb3b+O9sX3psTO/xh0An65LdF9So6NSvSU6I9n+N+tEu7kv7V0/h9fSnN4e2RkY+DjhYZjVl69/fM53/vc3LxYdnT/l'
        b'9Ya3ij5Iz7x45+Epx5RXz0mT0+rWfW/7RbfteXD4Ejiarzp+q7u5azXrT9M6p/5gd6Rmiu01u+Jvwj/81I0vaT55/OhakeV3VkGzXz7iYNUy4N5y9IM3qk+vNuIZFTfm'
        b'Sj+ZGnQitLzKL9xdu+ZvLRGjO+19u4590dr/122Wo7v7Dc521xT9KebzW29uXliZ+O4el8682jD+/uXfH+6pr4udykvTHpj9sve2jp8uGG/4+YL/2c+9npSmDnT273O4'
        b'5nu2zLnFvuf4pwsLdy7y5IZdz1lzdf6l2PlZXyV+FUaf+3PXm+ZXbfO72lQ//DV5rKAo66tfv/81fVtCTVHW2YuDiz/7StT1+cvzqyNqHszaZ/P20YWPsr54dOL+gd5X'
        b'3j61/fUFSRH2DnD7+f5fL49WK6by3z717jWeUWH7wg/ufDy7c0fiWtXDlhXL90nq95a/N/jamc9kfpWerx2oOuiQFPlF7t3tr75tsm+3qOHoV3m82ryvfsyLsOharXx/'
        b'1g8fqu3HV3VeaQ1/vb24RFLakLFj6hVBTsyi3bcKLoJej29H9lzpNKv/+e+OF9M+0H01z/+wz94N/RGiopY3Cl9Ke2Ug4+iTqr8PXQBRo3+/CDckm18IPZHW42iapH77'
        b'iffAL1ptCrOg0/Y8E8bU6DxaXpy2BQp8HJiRnqVNaa9lwVPglpiB8m+K04ONomS4l+ObQWkls0A/POBIjgrN4WHnNLgPaf+0sgDsap0Lj3HYpesZnMMWIHVGSfbDAYk2'
        b'vAb7KI4Byw+2rSdnaHXFQM6H+8C5VO2FaIWpVYEt0E6uZM5me4AC7MM88ylQAS77pGhR3OVseGzNasY0ocVrTprPhInSEtCNrZQSwADDeQ67p6J0Rd4scAmepbQaWGgx'
        b'eAZsJae2Xnb4gBTu1UbTkd1xoJ9VsAZcIsIWmGMbMo15Eti1irFQygHnSaI68XxCUAA387yx0bMOG96AMrCHJDoXtOqlESsIVu58SssSG2kIiNXIqkxwmoFKpK1Zzorh'
        b'epOSWywFe30zSIQUcB4lHsy2Bq1LyQlmPLxqkIbKlV07iZ0fbIcneG7/9zYN/8JWI54V/7EVxGRjCI0hhKR87pLS6sVz51eufu6anDV+rMXwz9Sjj/PUWNbOhHG2qZWx'
        b'2tRWmjfOwVcuArmEuZoedducXD0ib7XxFXlLrshbfDWuQ5nZofe6zLWrEIXQXAdEs1AgcqPHBNJnrkkgzTUTiNwYMIG4zDUJpLlmApEbQyaQEXONAz3WXDOByI0xE8iE'
        b'uSYpaa6ZQOTGlAlkxlyTQJprJhC5mcIEMmeuSSDNNROI3FgwgaYy1ySQ5poJRG6mMYEsmWsSSHPNBCI3ViTQY2vm2ld821xt7ySXTP7ztaMp9tr52EVDQo292983F6mn'
        b'2R5d2LxQZn5waRNHPWXqUX4zX1oud8eHNE380SkBO+PUdo7YG/CujJ0JTYHqqVZHi5uLD5bsTHzfzKKpQFrRXDJq5roz9qGNqEkH7xk7SpfL5raslOvI67r1aUc/hZ+i'
        b'fNClr0plHdEUo7axa4obs3eRBZyYLWWprWwJKWug3Fme0O2piOnm066Bb1kFjXMoB++P+MFSE7WTi1Rb7eop1Rtz9uiQyMWdKxXOHWvfdp4ujVG7uMvmdnhI4953FKr5'
        b'Qnmtwqxb0h3cofeIL5TpqR1dZAtaNyiCB1eOiJPwSSt2Ap5zygQFRUGc3GXzOvXlOR3Gp/THLSmXAFR1brxuM1mwVE9t5YS9ireZqF358jh5riwCZe/o0iGWreyMUPjT'
        b'rgGjjoFSLfw2HuWZqIhXBChdQ3AgT7Wd27c6FMrb69jibokiuGfdoIQWxdIOcVIOU4SAztVvO/sj8T19UPYrFa4d60c8IwZdRzzjb5tLE2TOrcmo/C7iR47O7StaVsga'
        b'jq1HeVnZa0RycunS7dCVa3cao4pxcZPqqt15KM0MabzaQ6BgdSySJqldXKVxahcPtZe3TFvt4d1V3VGt4A7mjXrEyDhqVw+52ckgtRtP7ekt01J78eXzuvVwOJ48pmO+'
        b'jDPm4S1v6JMMTu9fNSKKvp0/7K7MzrnneadEWVA0klCk9hYpnLt5sjg1X4xPwwe1BmfcFg+aDE8Z5acztkeSk2vUXgK1j58ivjtdloAvYrtTZQmPjSj09p+lPZpQhIaR'
        b'u+AhXzisPVw+XHfPYFSUd8/gtp9CG/tEH4y5bDxsQIsYJEERzS9CjezqhQl9Fe6Den2i+66xar6vwlzhIg/tqx9M6l+n5Mer3OKVbvHjnpSr59e6lLv/11GUT8jX+pRN'
        b'5LguZes7vhot4Jx+RK9881kSHaTuXjWzSvcyZU7sDB5wqhfPf6HDOsLWVTZZu9a1YgT5c2r12gREHLs0lmSwWCyzryn08yKnb++g6JOcNeKMySY/ITHS/Y2zRj3iR5Yh'
        b'MqKqDJ46adT5jzlp/N2pw+/d9Nll/jF/WxmWmM3wt+3UqmL/DzC4/U46zu+k084ky5w5mQx7iayyMl3YkEcR7HkQOGlAlslnCgu9NEReXskpecl4OpGiTQWt0fGCQxXV'
        b'p978jCUJQhG++8vGY3+afrxSu+Og8za/Y7s2dSRfPejX2MzinNs+ssfQ/TXfPoszb2Ufzthz3PCOYZs1lfm1ntmM8zw2Y297s0ySNuHOARxeohPOtgQ3aokh8/q6sD90'
        b'J4I33LVgbwzcymM/1x/xJ3ziK88tX1BZvqi0eklF5crVjqXYnWkpZpF9ZsbwXADy7feimG//gmw0TqY21R4I0LhTP5Ty0MZD6TnB3G9p1aT3HDOd9gNW9R8NG4n2xOhg'
        b'BsZJPDD+K0GmGjzjqftufjYaLSYvMlDWo5iE9ccjH2xK88nEmEStBniG0rFhG0BpGdmDKgMHsK3CgUw2ZQwOs81Y1AIJ6Q2L9dmUoQ8xDUnvMU2neCySVh68AM6kpYMu'
        b'v8xMTNukl8WWuMNzJMobXC4VX+FDUaZlhhvK6hlWxfdjqDyju5eW1XIodgGLkkWQrYDTodrUIbywjy7zmesym6rBvtG91mnjTZO56NJwzKoq4iolwbth/icH8mY0fLeC'
        b'g2ZJHG2We5YDyU3LSos6N38aTqJm3GgtY8ZyxNn9Q9R+3ODvKe7jzSQc21GH8i2wR5PCMp/d/lZMuHgY8CFqAuMxd8rY8qQEHwp0tHzz4ccorsfIVcpqozOxwtnblZw3'
        b'w2i50TKb0Hw0bxawDrH7Jbh5F5f48YU2h1N8vLu9sMW9eR/no7AdZPNBgnuDbmXbqAldcM/nHhojuiy2/9UTJN99v749ivvJ+iCKt/1H8min8xejaNh5z0yjvD9dTx69'
        b't8aiEemLkisFVIl8nEg3cja8kUZ/Pzi1kNq2roc8q+pc0kijqB9KDlLb3+cwm+WH4VVD2JhSDuSEOEesRemBRnYq3ARuVC+v+lBb8gSlrMVzbMjPWPTnaNPjJSlvfwH7'
        b'pv455cPs1ckmzt+OxH3OO6rc0JT35ZYO/49khzykY3Ey5bl73aZfu953HBu7rCrwTknUff36um8+eX1l6ch7P/LD7cM/5u764OjIRtk2noPotVMWytXpOUs7/wIsKpWJ'
        b'soeubtLab7Q2mLxupnP5YfzNjUeqChIXTztQ+XDf2zcTh7vyw34NOjuw++2he2bLfHX3HC1lebtvog6rXG5/VHnunbdLY3Sjtl/bF2vgW3S67Z0v3u6oLN+ek/Qrb5vD'
        b'pz2fD39kMbcqxKt1i4OS+ubjkL/YXHtt2cExp5nfbHo1xS7ko5WVIR98udriq79UJxhA9w0zPv3FoKVPscc+9Mfrmek5676esTfuQuOfxfN0Xz80b39D6/0rqfSMbfmN'
        b'79WV1t7VrzsaennPz7/Ith7623s3Q8vfTtFdFD129s6wxMerIVXypX3m+dain9vaex798smShY1nKow/ro36PuZhCuu9v51xLNgw3vSr5br1me/+9PknsiPvrTSOuvbO'
        b'nc/ftX+t4NGNrNUPX7J2D/v+pZDBMY8vWfsfbm/886bG0Je+SXqvY5rbnw4av1Le9qXVz75fLfteR/JgU8hYhuqnb27uXbB66YYT9BsXrj6yt/plRU/9jOqH3mvF6xa4'
        b'ttq5OcS9y+1rUtnd2i7+wXDFBye6VsEZ2uGlkVpBy0QHXo76JbttyyUrnimzvt4N5KArjYcNinR0dCmd+WzvKHeGJqEVHGOh9aCWbRrDxqUHmthLV6cQ5bwY7E7FiOpV'
        b'cCADjXItPxY4VwgZ30bwiF0kWpMuAKewY569mINJD3Sw18Mt7gQJC4dgC1dSv3y5kTHYZ2ICLxrWIgXf4TENnuCA48Ggh2RfCFrhRYzHvzgfr9OZRXoOlDJi98XAHbAx'
        b'A5xDo8WQDbayknTAPgbC3Al7E/ipzJoYyuFlSieXbeEI9jKFavIBjUi4AniawPzJihmey2cwzL314AQ/FZwGpwTM7gClz2WDg2AL3M3Evgm2wkEUnYfeU1ARgp3luQYy'
        b'nvSC4xmait0++Ny6i9LB3CY6YBfZVZgP+zHNINyZkg5uVKAPGhf0seFxMGDEGBGcBxfmp6XEJmdoqrqEXSlJI+VJADtWT3wGMW0ORb6DJ0Ebs8+xDZV3G+GsS+fpQCnc'
        b'ROmEsS2ihTzL/wPErwR3jX+C69WssZ9951Y/d02+s7fYzOetKpulZWSNVq9TrXcmqE3MlSaO2IHG6ubVMrdRS88mLXy3pnmNLGjUkt+kNWbpJLM4uKFJ630za6mbTPu+'
        b'mYfcRW1hdTSlOUU6r726pfrYIrmfIl8VkEgHJDaljFokNbHU5hZNuU1zmwKkSSPmrmMWjjL2oSz0Bcd+RQ6ubNJ6aG0nzZFpyRo6DEetBU06Y9OcZc5dnh2eci9F4qhL'
        b'2Oi0cLRWnGYp5UhjWrSl5U016NZ8mtT9QLgsRlYud+6olMcpWN0JskxF5YhbmNrGuSlObWMvM6BtvJt01VbW7botujJd+bRRK98mbbW5ldTvQMiYnaec1avbravgKGpo'
        b'39jbiaNeaaN26U0JahtHtGi0tMUrulm0o0jhRjsGtmg9snPuiJPrdqbTdr5NCWM2aDHYVdVRJc9TuI96BI/ahKBI5pZqW7Q2luZLg5risXea+mMhco68sptL205visdz'
        b'meTmZGm+LL6l+L4FT+3kJqvv4DbFNFU2VTWlPJ3qqG0dm+MfoZRmyMTScMZ9yqitaMQ2QOGP0rV0YpapTs5kacaRV3ebDE4bdYpGz2ydZP6toWo3967EjkT5dMXUUbeg'
        b'QWfaLUyaoHbxZJZpHp5E8HyFeNQjCK/Q3GR5crOOGXKxLFwRMOIajBdrE8uzcX20lEEdxN1DhqpZlo7SceN1ZXRkKDwG3Ubdov74Pr0jXWE16haK7kzNjuo26x7Sf1LE'
        b'oqZ4Pp7Fokwtnvajyd3rN13PxEJp4oSeSWc0YV5otbnlzrQn83EqSjOPnyRGqCPfoZKCUsSce2LtlHBdZi5o+EBr2dz6BQ+0KubWz32gP7+yvrS+ur7mxWx1CaTyeScq'
        b'zPzxEllYPRtLFgaahRV2mlKJp4qu36GFleuLzBczUJrl7OdWCk+XKRUUs0wh7LDaaEFFVXGessFq/cfYYH9HNv1UgOfIptE8lHxPusBluCMtSwB2gYH/j7nvgIvq2P6/'
        b'W4Cl996WztKbIggogkhHpYjYWKooglIsKIqdpjSRXQFZUHFBFBAV7GYm7eUleayQBxiTl5i8JC8vL09NMeXll//M3F1YBBPNz/f5/fXDssy9d+7MmZkzZ875nnNAkzsx'
        b'1SEmqgMGWXAfrLXM+deRv7GIMnAk4e3mtwJa9w71VbQ3tDd0NWxR/2SDvaIHJ+ujaBYVu5j91S/SENWsp4mPz0qTbEwdj+AUJ5v+J2FmWGTEKc/WLycpzzLEOaO684bV'
        b'5skdEBQLLmMY7OAzsLDkJJ4qd1C4hgd6+qsSZceCn8qo77OXo7E2f5FhJj7V/5fDPCPo78xhZsXmHIy1Y5Lh++Bv98jwSQfPNnLLHF2WkYdXgtfmLIoKe4u9/orPcw1f'
        b'4fThK5wxfNIg8I/y0PCpG9YWCRLeU7OeOXZXnnfsbpKxm/aeZPmx24THzujljF0WHjuWdOwYNNIyi/1fGL0DT4+ewozRU4kl8Bsk6ZyEA1FgwEZ69iQHT1C1kRzLRuwt'
        b'madtf+VQmz/e88PGknmkMCWGqCBS31BKdeHpeNPm17tKFLawO7IL+evmMIKloZ/PBHjHY2MGBQ+oILkMnNQBl8nt8zyxRZyaF+yUGv2hRyBFAxdE8KJnvCs87hweAZvB'
        b'bRaluJLJ0PLLSRpxYhW2oDs+P+bW/JZXa3vDHKmuYk1PtFqry8I5bws2LDdaEVIMvkg5pJMkyFUPURnZYC+OzIroy/UPcU1XD6njVToZCLqN7GtPpHSavO6y1eVK/189'
        b'Evs9PTK2pNWlh2xTthn+1Dqt4nWLeNHK+0OlSgkHP3D7Pjapdg1npKz9zvHX9nd5VWnG9zT4tfYf2qL9ScqVoNo9xvuN53lTF7qsjBWNeRxaOdIIG0qcoVDZ1RGDEhTB'
        b'CabrQnhQ6uMLbu3GhhwsSy5SlgruoNKHCLnp4JoXQTMg6T0OntqEwxJXIwkaSZHXaSG3OhvHSCYmLgvQKg3E50I7CJpwtmPIlRWRr2EFA2eEtgbHQRW5ugT2wQZpNG2F'
        b'PfCG1Fh1PYkW2lsXwkbncHjciNiW2L4McCFQn3THAe5bhy1g7k5yIfocC3lKz7Mt4gUpteXQy1sN88jNGVnr8J5bMu0vsrg7KakxB/Nmoyb/Ov+GgPLQCS1zQUbbRuFG'
        b'scOIhdeIlnd58KdaBrVbBHYjWlyRtkTLpjx4XFcf3aij+6mhuYCPpYU6di2j1nNcS69JtU4VyVDBwuQxMxeJmYt42YiZ+6iWx2MlSlfvIYdS166Jroiujh1X06qJqogS'
        b'cEQ+Qs1RNcdxXctarybfOt+mgLoAEXtY10VUdFfXpTyUSBZyHEep4O+4b+zfDPFBaCGVEGjG8yZmPNNIsEqO7zwpfGG+g5GZ0xa9svT3N9iboFG9icqkUhgZVAozg5HC'
        b'YlIrqD4W+lFDP0pZzB7mOan2s5wi2liCAMca2SxOBusAR8ZpUthMKlMhg32AylDoUTwn5XMpiqRUCZVy5EqVSKkyKlWRK+WQUlVUqiZXqkxK1VGphlypCinVRKVacqWq'
        b'pFQblerIlaqRUl1UqidXqk5K9VGpgVypBik1RKVGcqWapNQYlZrIlWohamC9r+kBToo2ucMiB3G7TG0ZTU4zjjJStNFdWJutjDi6GbpTZ4c54sOW95Ri+HnY8eMnVxX5'
        b'A1j84qXB3E30JS7JBOM27TqPQTayaRuJsoyLb0YfjRy5TACTg0UEAuXJLUXxZcp9P+2f1kL8LyIvpyiHn5tTkllIEjJN61VOXmERdmxxU5nxnP9mfgF/ExfPen8uTpKD'
        b'v3GL8rl8uoqloWHcrJzcTLcZT86Y4dO3NYvYYmf0fTesh2LncMTOloYngOPoEO6aJI2BAs7Dchc3BrWEoeSLWOCJYjcKp6uILlbdvCU+FV5AV2W3JnC2qm9OgOUxJPA1'
        b'ElzTuRw12BtVTLPUWxjkBsXgoFwM9wZQRaBp3qjqcmccILsmKoZhC44gZi5k7rSEBwjuyQvc9HKGQyWRMXTmbmcGpevAQpteTTodu/48PL4tyiuSSTFgL7gJOnFUTl8a'
        b'MTwYA8rQDhLNoJhpLnkMT9AFO+n981aMVpQsqbsqvAT785lQmLtaCnw9CVroraUCR+3Ged994QHYxloEjwYVSwEWlwyjwPlw1ChchSa85WbDSoaNCXSo+HZn0ChVeMQw'
        b'wAFTtP8MMndawV4ak39tTnJURIwTusyE5z2JRhPs3Z5MV30InN40lUYAXIK3cSqBFNhPnnUBx2xhFeidLx+udzOolSEwT/tEkUTrzLXLcxnuLDBI1NybM0ATrKJw/PrJ'
        b'3AzghAUZHV9wJXVaXgVwM0CLpb9Hg2i2j29kUxwtAyWslg6wcqIISi1nEbyEszQUz7OirJbCBiKoGDlgjFwjA+vAO1JcsIadIBxvghZdZ1Q5Tp0QsUs+eQI8Opc8KVmB'
        b'BKLU02gNp+Z+wYygaBrWgxa1KDRPzk7L6VAGzpPLqzO9p2VzsJuL8zkgAeAQPcAd4FoweiXO5pCAek4ndOjSIYlFwhWAaJaUC+AwW5pyAQ1/Gd2IoWBYgScKOY+5MykN'
        b'dVMoYq1ZFZ7TZNahUNiCNoI4fsqZxOt5wEPvsq6DVv3CvUtFjU7FX5WN9v7jxGtpD+/UJjU6+ZlfE978csmw+5f3Nf9R3GduaLrvntrVdx/5PflY982dj/cybXXqKj50'
        b'W/hO4mLrc9qL38/9hquodtVQdU10xvwb6zYN2HR/cexLz9Ivc46lHbnF/+LC3y5ueNXO2/NtUWZBKDzztrCpU0ccf6fi1Tm636ff/Iu26dU1kjcffD9/qP+1GP+hwKr5'
        b'P3xwqulvY7uimk62RwVc+0rtgzun/jw/K9L162HR45zR9tw1r5mtWOfz+Q/Gib3D6171NI/8C/doxmqlvmtL3xza4u2T+L6/4LOCmthPWz8o2RCb0/63G199418W2f/X'
        b'Xe9G+7ZfeAUW5BYo/dxTFuPy1XJ+/Fmlm/GC1qWffvX6v7pa/vHeZ1/fmLB6N3G1eCj3Xdutf3l1XcP51WoXV0/c1lW7Z2P+l++6H+3ge/1QemuuQ9S8rluvZKftst+Q'
        b'lJZltyHpwQ/3/2q156Fw+y77Xx8KW7798cPCDYeDtr2rseXCg0WvhbS9I0SSdqn9hb/0bN6xpNPj11UP33nzz2d2lwT/6SelHQ+E7Sf+wTORhr1V3OIMrumGTwltsA3e'
        b'JJrezfDm7qhoJzf6mipa57dzmfA0mn7ddPAN7EJwnYR5JSZCUJOHGFQVsxTsB320yrVnrjoOq8KLKXaFLXNpQ54+mk2c/A3E0mcBqu2nTH3gNhAWT4scszuXtDJ3BYZy'
        b'wxowCKsJn8Tniw0udBThDnBWEVS5y9gkaug++0ImPAGbVtLRVo7M5UmjyoCGMEYw4htnSPsZTGP0HOGe8NpcmoEawJNsfyT7imnFbWcIqEMv7oY1cZiPsnIZSQaraCBZ'
        b'OayMAVXO4HwcYaMsnLqnFlyEV+hWnd+IFmRVnIyTasB94MZ61jwkAJ8ksYHVQNtGUJUJ9uOwJ1PsVMeXBdrhYVBP0+8iPBkJqswj4qYYqs5OzLrgXnLDmkJtkhmNZqeI'
        b'J/bC6mWo7+AkuEBHZjkXmo/ukLJURJv6RDsmFCFC3qTHv8JihbMb2MecjPZ7lOm6xpKOQVwOW9dOJl4jHFATHAbVyqwi2A4F5Pl85VR0hz5PyokUOYim1+HxbzF/8wat'
        b'SxHxOtzc5diRDjzDgnstQT9tTKhRhQdJbBWSXEY1LBHNHzgI+oGAHDk2whbcfBnP11gOb4awwsCx3d/y0NXodLQ/x7rKcrlglgUGvOVSuSwsVtIG9bCcNAdn+nDHs2hy'
        b'J9aAp2B/NssfnIGHCDkz2StBVSE4FCfH13TmscANJ3CC3MDOcgVVEXDQPTwCtZpeGDoaLNAJbm3labwkXBs2DMrj16alUtaSSoKTWZTJmWcpi1ZobIin9VGi0FFd3rip'
        b'ZW2oVLFr3uYr9MVBMsQ+I6YeuJguCRIGiW1HTd3vWzgO84JGLBYMGy2YMHUU642YumF9siXJgh42YrFk2GjJuLmVyF64mqS9tnQRJ/Q5dq0dsQxAf6thjJvDWcd2R/H8'
        b'EWtfnL183IyLQVWixOY4ksl9+p84t3lG7/qu9X07RiYz1U9YuYmLerd3bR9SGXEPGbEKxWncZy3EOby3C7eLOSOWnvj1H1na4F/jxuZtRkIjkeOIsXOtIknNzRWFSQyd'
        b'PnZww6nkw4RrxUl9i7vWDJvNx2nq5wpj8S8/iZnrN0psRxMBu0XtoQbFcxfvkDj6DVlLHAPHHEMkjiF3Qt7UHnGMEqhPWPP6tg7lSHzDR60jBErjzp59PIlzgEBp1Mhx'
        b'3HFOXxp6TqDUoj7u4jdkJXEhF3jjTh59xhKn+UPBEqcgdFVz3MNXwG5TE6q9Z+T6+02T+9NfYuaGf89DZ9Bv1JWkLdbCGeej66LH9LwkejjEsrvEO3JUL2rcBY00vjCq'
        b'x/vIyo4QztSybZ5wnihyxNS9ljOha4opFC4xdPmY5zFubifKkpi7ircPKXTtGTZbMG5mK0pCb8K/V0rM3BGNnPAbMWKQ54m65Dh/aJHEccGY42KJ4+I76W96jjjG0DTa'
        b'fkdZ4hs5ah2FaeTdFyFxDvo9Gnn1+UmcAof4EqeFhEZefohGGkKN94zcn6dx8n+nSMw88O9kRC5EJmmjCZli62LH9Hwkej59yUP5kjmxo3pxOGIDr4uHSIUu4szumFSN'
        b'GnKnczU6rsHlPxTXQKrYn1rOv7WaN8vU+/j4viYeH9+/pV7sDE9SyAoVeVSXqs8fS4dOcgkxfiOF82SzZSlL30HNlsuJbE3yiktPcFM5sV9e6nMe457SusKc7Lxnpxif'
        b'0cZh3MZHjGltlGUXx1Xxi4oLXl52Xfa6NK+0527bCG7bVPJmx7BcfjY3J4ubU8TNKUTn2UVeiybp+VISoBf8jXqB4f3r9OaZkYy0BZkZOUX5BS8lbzwmWsFn7Bdo0gRu'
        b'0lQaYgtpk+gc8S+PTmgklddtys/Iycp5gal2HzduKu20A8nFzS8s4tI1pf9XWpm5PTO9uOgFWvm36a20nWwlXdPLa2K2bMWS4CTP38AH01esk2xVFMlxF7Q86Fpf2spV'
        b'WpeRmYYm9nM38+/Tm2lJGAup4uXlFp8cZdmye+7WfTF9lK2mrd2X1r5sWftkeujnbt8/p7fPTl6RhwdapsWb3kb5109PkowBwcxylhRiSzGpikl9ZSmD6C8pOf0lQ05T'
        b'Se1mSPWXT5U+2yQ2E2Kr+AwA8H89gfN6HvOn5BmaTvyPLJtt6zMRNQsQSdGKkVs8BWipF6DtuYiLpkNeftFMZekMhems+bx9MszZJJ/3r2q1mbfpjN6yfN4Mav4I85Ou'
        b'd3kMcu7OhDfAIDl524Fjk6pLcvJmsGfJHn0dR3qylM2byQZPIWmzsjOLpiX3TlvBoMxITMBhPacXTCf9XG/7txxg99tVK/5QYunnscxT5Yz/imX+ObDiaEzXDDcxC7Fa'
        b'cKynbsoynzPHhmVU5PW69+qyOwvtWNmKVIaE/Zrnn9HoEq1BNeyC+2WKFenYloByPLyBoOy3bfcF4HepXygdax1KeuRFY+3gLJ5zamNtaGPcNCM+GWx1xnMa8Z/r1d/L'
        b'm/Vz8MAbv6hZn8ekVfBHlphFEb0U2wce1GSAs7DVh1yZpwJFUc6x+EpYsjcDDAARaMkpbdnCKsR5QcfmaGHc/d6G9v28I54H+w+eMnjzy9TY9Eg+86LxRqMNRvGCzz0U'
        b'yLJ7JeT9cuXQzpuy2T/b6QQP+BQRsM97ifYMIhCKm9MUH2dzvk1ewWBrO3+nwdD2+ohrK86QGHoPa3lPW2mzkfy53vW1jMToXd+txCRW/l8lbZ++ttiEBdOJrykpbuLl'
        b'MmK0SfwUM4OLhmC0fyEtvSC2O93GVcgtLMrJzeVu5efmZPyOuWomhkYxNiGMWAsuWpVQHNT1zau9twrmnc/LufezBruwAF0pXrK2GV4gqAc7xJT1vJO8mJkCj8zK7WUP'
        b'XJJfNXYWlnnlJr/9QKGy8KPRvYs79/ULDtcxrv9yWS1arfXtOWqt0efaLy5mzlFbeV/gtAIWF3llPXpwvJcvfpCW+uYDmFAHWv7F3JJtZ5NtQulnGgX8pYPHIQo8RcNd'
        b'zpO6Mg80fTXAFdYScGwVjeY967Rq0r6FjVsUaGbuVAXX6Ku1/KhJUxG2E8EhsJ+500+fVh0KLMExZ5rJ2IRMWb/gLR7tetybCZsmDVFg/y4GpWnDSgaNe4hWeCUcCoiK'
        b'APuy6aTtDNDmv55oNHfDcnNnWBEXAXrYIaCSUsxlWufA47Q+uC4JnImK2JMGelwUKbYZA1wE3Rt5Cs8++2PMjBx2gZNTuI4M8pQcJCshS2wbPe0fliCmZmTWVFpfOm5K'
        b'4LE763eKMs5u7Ng4borxiU2763eLbXtdu13R3x/pGTXF1MXc1fMQJZxd1b6qljGhiwEMRqO6ThiKqihUbObUBmPQbGRdZEO0yFOiZzum6yTRdRIn3NX1pKucBkaYZZuc'
        b'FYsgh8soMFOUF+9k3fpZbqd8UvjCOyVmmNK8xrqzhWCUi7WIARQFn2Eqs9DRuwAriAv2KGCiy85v9ziyM9I9RfrQcE+RFtTvcWQi8T2OTIIl/In0iqf+v1fqYujoLPEQ'
        b'/4wBHDLr/kZMKwNZKESmutZjRUpDX+gtLBI4jarbPWGuZKjbP6bwJ45taP+QFDzaypTFEZyH4wj6kzCCBhYTWjy6xMC/PGwq+iAOLKi7kEHCD0qLvHCRDymRBhb0wYEF'
        b'55LAgtJ4hIE4HuECEo5QWuKPSwJIifRlOCCiwSIGeZu0aA4u8iUl0sdwZEUjP/mK5uOSwPLw7zgq6j6PDChjK4mRe7vfqfnoV3nEE7aWutlDCn3QMQqJXeQaqASX4cCk'
        b'Jl8l3QgcZYLr8JzdNGapI/39TRBaXo3Gs6BXFNGPEfqhepgyrAaBQqiX65TrZin8cdQKXQuS3pQPcKRoFSOC+OBMQ3xwplrRozKJnsH7kyp6PztDVe79yrPeq4COE2py'
        b'd6lM65dRj7qsTRnGpFYdUq/mAeXJJ1Qnn6BkT2E8j/THqEfrnCJ9pzL6n2FSziARHmmoiHq5RrlWuXa5brlRllqGtlytatPbIf3hoB/lLFaPzjmpZ2eGKUEKKRDwiWq5'
        b'GqpPE7exXK9cv9yg3BDVq5WhK1ev+ox6pXXi9vboydWrIK1Rk9RmgGpSztCXq0lDjp4GU/RE9GFmGMpRVHOHBpKYze5pSNcp+sXPziz42Ac9Mm2zDuZOvwPv8Oh3IZeP'
        b'Nnf5LR8DXfhFXH4BVo9uKc5BzGdaRVnoMEbuz0CX0ouwOiGniFtUwM8r5KdjzUzhU3iYiCIkQuQXSF81+RZ+4eT5GckeeVw+Nztna2aetNr8gh1PVePmxt3GL8jLycv2'
        b'958JuMFH86c6OCm6LFqcEOzGDc3PcyjiFhdmkh5sLsjPKCbNtZoOS2LSqvQTzKccfCf9afPQR6PCpIMvUxZMlCCTlCZdexVemmsvEto+Tnl6OAlhnwInyWS2TTIC/CF8'
        b'0iT98bkcTQL5QZv1AI5nChngDDduBNELZ+SjFqEDOzdze05hES7ZhschTaoGzZxFjpQ2SKr0ods0QxW0LQc3El3JKkbV8TMy0KR6RpvyMtAPl795c35OHnqhvEr4d4RY'
        b'ReppIVY9thhHbN6MGPstjDCS5bQKnzTFwnp4BIp3RJMMVMvDo2Nl6SHAbXhYFZ6BjUBMJ7A66OY/exXoKXAsUGpM3goPK5dmwx4CA4KtfhawAR26wtmUAhTnODCgYAek'
        b'o44WsYHAGU3N7XBIidq+HtYQ9FXQcngr3hV2wovwDNjv40Wx3CjNAKZtIjhXjH2K4Q0TO5LbeNKXGgPJli53TYLXQSuT8uUpgDrQHkFgQwWoDxXOTCwnKFOFG/OJOH9j'
        b'D4vK1ValsGPuv5dzKDrnWK2V/RTsZjksj16G0324wKMxqeAEnVVjWb4SLFOCl2n89BFwJrMQdm7fooDt7RSo9IEXc3IUwpmFOmjCu35Y2vxWEDoX+OFzQWGTBxznVZ8z'
        b'tuqxDxNtMGB2C2sTBrL7+d3vPnhV75+flv3jywd32qtMmy/offZetNZWV5ZG6Y0fcp23Mr988MbZfXVYQ3D+kNVBhawGHkZMpx/ndl7QS/qqfaVCkSG4oedxQPj6m7Vj'
        b'++DfgSBtzubCyh9rQcv5BtbEUfswcfOE5L5LZc6DDYJND7Z/arvlz2c2l9luFA6XHgy0/VJ48R1jo8raEVWH5SUff/Fp9eE3Vqizat9Q+qTYi7XjoYD5U82ZhjlRjJFD'
        b'Kq9b5/T9K1JQsLJbkMZb7fEz32e4NMxi+5srvBy9jbz0vI97e3qFMktfe3NYd/UrZn9a+m651Vpl7c/fpqhf3cM+jtrG06NhI/2wfGdUyWIpSI7hWQDO0ZlW6pKhWIZq'
        b'cYKV8HSgDNUCxOAQfTg5D+p8MFQN9MCDNFwNQ9VgB7hNJ/oRZPo7T2FuenTBhZX+BJ+dvg5ewKCbfEoKuyGQm0Y6v5Obd9H0ROdH4AXQD04bkZfqOIJjUbAFdtHoRJ4i'
        b'pazHBO2gBQzR2UfaQuAlWIWEptgYHmhBM8gJyZfgEmtZEKijs4+0UqDH2R1WYplKcd0KIGa6BIJ2An3wgLdUYBUQgWsyvI8U7LMPHiUPZ2wGLeg8hqjFtmKAMlgOWmEz'
        b'qKWPcnthD2ifSg3fEYvdJ8HlVELR3YaG0nTTsIKklS+F3a5IFgVX2OGgVpXQJRMxBtEk5kIxABzXZarDrkza57QL1G0AVXGxUYg4vaAmTtpAbdDEAjXwrDp9IqzcvAuD'
        b'SRDj0IFXad6hEc+K4YV+i1fWsm1qsGpHHIk5hbPnHMXumuCoe5QrSfKDI20uAf1KoGY3uE46rOMbBKvkwIanQSdozightN4BBlbT+XJIsKVmcFKWMGctKCfQJzYq2os6'
        b'hFoD6LeBg+ASPIpEZ1TdbSVwg6fyB84ZOEYG9ykfMmJqNpy+c0/Hjyxj0OfOsJXo3GmJT5v3TWyH7cJGTJYM6y0ZN7Ro2lO/hxQtGDFZOKy3cNzQuGlb3bamPXV7REUj'
        b'hi61bBmiJEAYIGaLs0dM59ZyZHftrtstyhg1RLK+QVNUXZSIPapnN2FsLlgvZo0au/Qxx41M2jhCzrCVV9+KwVX9qyRWC0eNgp+wKBPXYWOXj4xN2wyFhm0WQgsxZ9TY'
        b'k7Rj3pCPRNaYj+WrsuC2ZQuzm3Pa8oX5IxbuYxb+Egv/EYuAoWUSiwUCFqn0I9Qh7AOYfteQR5AvC0YsFg4bLRw3t8LglnErHsFKcB0IKsXaXlQ85rBA4rDgrgP/zpI3'
        b'ol+JHgtdJQldNbw6dSSUP2KdVstu1HxiTLf2pycq0i+FBNFqZhmmw4JzPcIsWK/rKISZKr1uoRDmIPUcVJEDFmBp6DnQBXT4lUk8wXOMsKmqnMtgYTI6glvhWCxWL4op'
        b'ECg6UmJV7z+GKZAaiBR+0zj0dA9kNqIA1WnwAu9JYWqm9CQnKb0kvAGxTXf9BhriWa1eoCpvoi5gKz7lWjE9OAyLtluVs6UK/5druZrhivf/keUKta1giPkUcWY1Mt0q'
        b'lrCIkckxb890E1PhLhY1f5T5aeYtHoNkE4NXkeAzOI2/0rx1N7yA2CvatU49y9Rk/9R4FqbnriPBWn7D4rQ85X9pcXrOl4aoyhmeQlJenuFpmlshUY6XM/4rboUzfH9n'
        b'zkR2bHEAhaMqNJWgjRztx2txAgPZIGLHiopop0gX0J1A+1jggrhoDI4F50CFqp81GMxZ/8oBdqEfqsWg9e+0u9/V8BsNnjOE3KQ6+0OxIjej2w28k8qd3fV7vVlUT6Ly'
        b'6vwiHutbcpqoV0YiftXsYsGcRHnBAG3gx+nJdxleWE7jmgWmT0cxYsNeKHQngg9LAw7JT1EvVsykAACv7PwNi80U6wfPO3tkhjMePWUfJaMpa2QuShyzC7xrF0hwnpEj'
        b'FlHDRlE4PtpMe5rSb9vTnuGh9iLNi1GdMq49WZHyosY1THkek7h76AfZYNsaOLkNSaPYtrYRlBOfmOXgsiK2rYWCDnSFGNduwuocj/tlLPJm//vXiaVzunHt69SI9Fg+'
        b'87ERNq8t+kZmYGNRY1bKI2WR0ohQv2MFmKIJxDQxehZNyCBZUpO2toUpDI628/d6LG2vhxzKym4Wa5vCswfkhV69SHXK9PZ9cMqLmt5wHCrEVLEifhqTmXQcXk/RFjip'
        b'y5liOaNcCW0qCpNsRuGlsRm0qfzUOUMJsSSziMuXiQfyCrlnq282FWRm0aqSGYDGWTQsBZlFxQV5hf7cYK4/ccjzT5USO5Wbn7YhM30WgMXvmPcUYovnYp7Si/7fJsc3'
        b'rPNOXLrCNWlF+FNOaSd8ab80UOajvAGcBM3EMc0CbYQDUdMUKVNaA6wySIB1aGmoKsEjAeBKzqKP9jMLsTC0xvJM81v+xOx/teFMgytinj1Z+4Yvq7X2jH86IPB8bYNR'
        b'kvei5Nd22fV4SPRejz3uNFdxaLWuzfBa+wP3Ul43ed1lbvRI2dcP7qS5GzROfKamtvi+3f3NpkKtre95KP5QT1ZQdrdui9ZiniLtQ3zG2HryWAyqtjLAhRBYTo6fas44'
        b'OJ306ImO1w2y4+cgOE0cKkAt2vJbVaPAflA+eTaXHcyNoICcu0HdHnRIu1IaNXmq90GHOeIocd4E1EbJlEpp4DCDUk1hwgtL4JFvcXACxKKbLOF1cHjWyHSYp4t3v4hD'
        b's1zUHFXsvyudXCUmT61NuWuEMayXcu8izL1tRaFiW4xdHjH0wbFMpp+2yDlp0Z0EiV3EiEnksF7khImVyLbZtVZpXNekaX7dfJHtWZd2Fzpr5F1dLxLuLnDEJGhYLwgd'
        b'+WrlEdAcmvkTG9tv2wU5UzuAlOckYsPgb/QrQXY+wWw/E3Mdo4cviHkuKHqmYJNG0eKrNF4CJQWGvfRIFz9dnpXbFM0EA+ZnyTxU//vMJ5h+53Myn1lRQF7DWQpEaDC5'
        b'MRcDT9obeFXsr+oYrCKvC4cq/+o16pHhye/GMVaUqL96KOy3yecxiXRTsDKahG2hPW7AEGgltjoT2MouAYd0aTeqG/BiQVQEuL1V6qFEe3zCHsbsQKFJ8Igp8xmTSkpl'
        b'slis6MXyMGEVgzK1HDNxkpg4iX1GTDzQEjC0wAtlWMtu2j76rFlOh3Wcktl/7/UZcqLMd4tXvagbvg9uDZOOCaBUyN+auY5fGDvNVDKpQc+lZHsqMZXQeyoHHSWpLMX/'
        b'gqFkPY/5cdpshhLZZMf2pgxpbr/nmurBk7axzCI+RhzzaVzipvytaJPGSQ9l9b6sdUI/IyWrP7anEKuYCzaibCouLMJGFHrdFhbl5NFgbaxumNUKQqsgpiFVsVEMVT6b'
        b'BWZyieK2FvC30eRCfX5hg4lKbDGeJbmgCackI1IBFMJbz5IMpsQCXydiF7CEzfOdsW94OLwFL1OwEQ6CShLS0k6NGZ/4owWOhsmm2EJGkVUTsUckrWRTnIQw7MacW620'
        b'iUqgDfL4wwheme8chypbDi6Y4RAlJ1Jzvv8nUCh8FV3UWfDxprhgFeCh1fKBT85fjlaJt/U+YAX8oBOnUOMXnpcSzFPeN1i24pH2L6djNurdsz2gPjAw4O3+nSLMXvvT'
        b'3dSSFIvu/X+JL7XpFCyOgr1rV2eEztkx4fifEs0vv3dSfWfLGxpHXYQBHz9YZb7xgKkDZ9vcvx/rPfiu9ed3+O8qO7/t8soxSY1uinCHdczZM/2gLXuisnPbJ1Xf2J9+'
        b'ePDdJbzjynZHTQ5s0fjzz/9zvn9xzAr7BPPI7SfzOkDj69s/0mh9/APj8Fy3z209eBwaANReChr8FOVU9xfALUui4l4FOtyQgALLVKepxzcvI/rgxGR4TWozSM+Wl0zQ'
        b'uVKqe29Bx8xe0Jk+pUNvtQP7aD/QI1Bs7ewEr4L9blJHTeX5TNAGW2E1nX69ExxOmtShZ8ErRI0u06HD63m0AvwA6I2C9e7TbQj9EWA/acEc0GZEK/9BQ4gCpYi1/1qg'
        b'4n+jhubKRwdUksYpKTGYhW+icsKyJTTLflSw6g/IN/o4RCB7VN9OrCNVRzf71YY+YVEG9g8VcQrxVcJVYuO+4BHzuXUqtezaDAylklNhG5o0ba/bLmKLlomWizgjhjwS'
        b'IE6QUbezlj2ha4JV1tmiInmVtUivRUOqUjatVa0tqlV9oo/eNqxv99MTLVkxrQl+RUk7hMMCTjoheizIUQjRVoJ6CiEWUk2wstzWs0rxd6UsZUpOCUxvSdlYzHoGafPl'
        b'VcCr8HZk9egFVcAFyygCqiVqarIxKU96TdFQKXNFHMEml5+Xna4kx7p0ZKyrGu9UavROdZh1mH1Y4bAi2rEwjgTHsVIjWBLNci20h2mX66AdTBedEXE2Ub0sHbKTKaGd'
        b'THVyJ+OQnUxJbifjyO1ZSrs50p3sqVJ5RdTHu9mz7GTBGRnY5yovc9t0mCa2d9O2dRoKkJ5fUJBZuDk/LyMnL/s3oo2g/cWfX1RU4J86edBOJXsE3jHzuampCQXFmamp'
        b'LlJvr62ZBQStRiAiMyrjPxMSwk3n5+GdqyAfI9xk7hNF/AI0B7hp/LyNz94+pyECnpJWZ8UDPHNT/a2NGBMCAxYKN2emkx660FSedVud8hrMK96Ullnw3OiGyUlJN2PK'
        b's2/b+pz09dP2d9KjPP6mzFlbkE87GsnosD4/NwMtKDlp4Sk3pE38go1PwXgmB62QSzsrunHjsBfGtpxCugVI5Fmfn8H1zyrOS0fTA90jOxSlzlqRrPXp/NxcNMZpmVn5'
        b'UuFjMgoQPQmKsUcUxuDwZ61Hfg49k5KTiGx/7tP+iFNeI7L3Pst7RFpXmlfazFrkvRp/53nMVZCkFh/Hnevt5+pJ/i5GHA4twoxM2VDJ6kJTn54lszuzhGZm8Ytziwpl'
        b'S2SyrllH3KGQS/7EWKkZjZsmzklnJu7KZnT4Qt+eQxidJuXpzpDyHGKJsJYCW0oKvQqQgJUPxRtxztWbsINIXhaumqpbtzAoBiwHnWwkRey24jHIM5vgBdjlHAuPMigm'
        b'OLrEnhESBS8TmRE0B2Wjh5bR0qGjm6sjLHd3Wg33RsQgWbE7YTO8WJSEkSpMChxzUp4HroPzJCISHIAnS6dBa+jAEsvD2OGyGA3pazmgvdiKSIx5u9QotPU5asVvjD4f'
        b'voNONABuhcLTWETCyBizTIKNoTHgLjzXSAUq0FkRnjB2IX0wgWfUnGG9IsXQpmKwFR10gS5S9eEsEvxPi9pQnPtGlB0dQPDfKkjqQoLHR4w0tWN56+jCn6PpbAcPbUpc'
        b'1itxaIGVpYNoeAochWdwEHkc6CiRREUmT1zeyUEVUx5cxfTowZAtVDHeOZWS0mGVa2RMfDhtCrjmGwGrUSewjD0J8kHXwl0io90iXJ0UKVjFU9sCL2YRmhfZ6c3Q3VXz'
        b'QBVoR+Ie6EoInwRtoNPvVWVwigIDYTwOCdmzI2qBFGgATmdKAxuBASAkKST3JG6ejGtEMdwZYD8dSeko6IK9sIoEwjAC++nIRi5ZJHhPIjzvIQ1slBFPhzbSYunDHniM'
        b'BkM17+BG0RE9XEAlHV4IdKykk7uisbviDE8lyYcYwgGGlq4lz4Jj8ECJNLyQ4xo6utBOKCLRhdRhJ9adyYUXAuV5slgdJLwQHIzjqZJ61MBtPD1xtJdM2EAHxlIBItK3'
        b'3DCc7k/qNqAKu+iwWMmupG8miwKcp1yPPL2kXgFdoJ/UqwwugiuTQbEEsIeCgxQ8TAeJuuAH98pUg0EhDE8DOEgCQUUgybmVRMUKdyJxsXBMLLS8KglJdpvjBF9uYdPC'
        b'YuGYWJG2dNyqNpZFVBIUywXFwo4ILXCIzu57VhGUT/o5cMF1OiQWqIRVpLf+66yiAqzkIy3hOEvqmfRwgEZQL4uYFQOvSvUn4DK4Rbq0yWpOPKxNxK9pVSym8mA1OECi'
        b'V/EV2WSpcG2LXI4tYVPEOuKojqheBRvi2BRTLQ5UU/A2KI/lqdCBeA+EwBuFGgXFsF8N9mui9g0W4Vyn4LTuBlZENhggaZ05aI1Wy99lkQIHC+GlYqz46WTBVrUEOp3t'
        b'SW103CT3mUfSd24r2qJcoK6hSDmy2HAf6OfRr22D++B5OFAMLxVuUdsCjmgWFLMoeChQ14zli8agt9iVPtpcUivcUqwC++F1eAXVpgkvK6M/LhXjZ2RNWLBWUcEomNS7'
        b'EbbDevoJ0hf6BnjSVDeTFQzOoilhTQ58AWBw8i5ZC3lRlAW4wLaHl+BVklMVlEWCvXKVFRXASywqJ0x3McsfXoM1dLyvM/OdpqpCPFaR0lJkwkOwAV5YvEaaHP4yOKcK'
        b'rxSh9qgpqxcowO4USn03EwxkwWt0gtejySnxsFk1BtbFo2NhYzw4ghM/nGDAK+BmBhnzDX7gcvzSpfiN+2Evn+KDo840bL4c7lsjX/sCcJOu3ZZDnrTxVihExCtQ2OlE'
        b'MWEnwwkIwukd46hODqxCDC/KPSY6LhHvDcvx8oT1Vu7Lwl0w96uOiIaViBmAfYnKhfAMuE1q1OWGRsEjLIrhTyWC6/AYaId10mzaUGQJB8IRN4hyRcsmlm0CDlDaoIUF'
        b'jruaEDbs62NCoZdzPOZm7BJqG9K8uWepM5WACvvUtqYlGm6g6CSt1A8LpF8cF/LYhMPzYf9KcA6cTMIMlNoBykEZnaT3GOiGLeDcHDe0KZQgfnYJHqSTIFfCvbrO8GI+'
        b'hnpS22FXKF18iM5K34wryqFy+BxyYMv5d6EGs9CYRVFGUXtbkz7YOLpQ62/vlNpdvX/56u6/u20qLNHvKhf/sOzVDs7yxafDtV1vuZW/P7i6/4ytuPT95a8aPmr/V/MP'
        b'Bb+M/cey5XSE27/ePTTqPPZp1p5vfn7n7Tz7bwa+qSpfHPtpza/Lx1eHfHUu7fhYxvyjBq1rvtx4zONa1GFJ4vzz1Tr3hyfyTs9Leu2XJ18eqP5i4pcghWq39EPvmMW5'
        b'Ht73+fe33tkQWnSw6V5yqarPfwJu1cHr635l7tb5kv+WU3TcJ7fiFulofVjveerTtxxU/pr7XUr4qe2st6rdjD8335D6L7jt6wcq3k8Kbv9w7G2z9f/Y8OnP867pBO3P'
        b'GIve4rPobStO1Tbt3Sd+av1m23t+y60/+5EJQofOfm8yMPCD+weqP3wAHvy0SPinezff/vcdfbeEzSlDXZn//Phgg4dnkHJZi7Zby/4gnWUdZklczYxWzdr7TrzBv73L'
        b'i1V5An48+WBM67VPTZKs7DVPnl0s3tK4boXNjxdLXHdoVCRrmb/5ULH+lRjb/Ru0sx85fdV0fuk1u/f1wnsGP3rz/TN126Js/t0YFuR4ZDXvyC7b95M/Tz6cV/6e5r/h'
        b'3BRD0/N7j3y28dTVifUWV5yy5hbfV9v4921uPU29Ff8+/obFsiyF72xKliv/8+GlJ3on33zf/p9vHXl8VmW0c79i8z9ef+LQ+EXQl6/1e/0U++eEol01aWGBb4jbPNc+'
        b'qLjg7F/yfdiBvP1f2xRpVXXH6aUlOv5DeNcutuDu7ayVVe+YN7dbBdxW/SVbf1nx8t1ig2jGlla1v0Y5Laj7LjH+xPL7fTyzPSvn/afi7eafzOeBid0nMkeql/8n+pfG'
        b'1YfbDI/6vMIVLjrsU/Lpgks+VzZzJw7q/qJ5/o7TiZBFUTZl2w+FDnxbwX49/6dW5uE/tf25/E5a1dvp55fN+XgDIy/mdeWm7/h/V+iQ1Ngbbj24JtC8uj5H58MN9nsO'
        b'ii8ney/47tWhMcE9v1f99zl+sO1dz5vBad1HtCv9UlmP3vqsrO/8w5Kq7Zfje/lvlI9+qM9/UL5ALyfk1a8VjWvnZ4Rv++hS/r6D9ZbvwQXXG2Muhihl/Fz65eXQXXFC'
        b'/paeIkuB5tjWN43PPXpkmevBvry0iedGDHPwEris6TwNhpMILlM6ESwgQiJHK0HbmsNBjkyMgRfNGe6wRYVotjxNwKkoGegiDt8BxXAvpQ0Ps0A1HIIHiXpNH3R6yEFy'
        b'pcq1bUDIAc0JtGnxdNQqEjtyzvpJOO62EmKn2AAbcHi5uNioSeQonyPFjiqBI+RxvVWghijmgkETrZtDAtZ5cknZaz0NbAXHUik6LwhsiiE4kKWgH4imQ1ulOjkoAsfD'
        b'cXZz2vi4D1Sgn3PSuMuloFwaevm6LzFbWuC4mbEx8IgibFWi2D4MJDDO/1YaC7IaHqe1dkieaZSq7eDBdBqHXIbklNuT+r7tYC+t8kuEQwRVa4wu9kkznsBrKRTJeLIQ'
        b'nCD6QDfYnRzlDC6gVhfuVqQUdzBtwXlwhW5xIxSbR9HGWJwDBravp9PApGymw0wL18ELtJrUFhyXBhbsAKfoVlXCWiCMkkm81uAwjVSGjQVkMkSux4SocldCB5cOEwVG'
        b'Yga8TS6YgNpi4vDF96d9NqHIkNZ/dqOjST9Wv6I5UoWoEePCsAUtlK47C6KWwjO0GlUABzfSNl4gVCD4X2LjBQeBkDYPH4ZX4HmZBDgnluG5Hhwl/bGDSKyRCuGwiiMV'
        b'wvVyyAxY5BsjFbRBN2ikJe1NtBeqBTiBJEda1FZJnRK1T/PIk2G710kFbe8UaRjPNmloP9AeCC47w/0xTwvafNhJk/giaNKRStrgykJa1AaXoom52gs7wk4TtRci+sqL'
        b'2vne9EAeZMQ7e4NmVA9t1UZvgWWs/AQgdXk9Di7Nxxlo3ONcF2oy8bR02qrwrT2+VDMPEXeACU5NyWZb4GV12MfwAvsYLrBDQdktk5DB2GNplGxc4F4fJLCfYBJA9zF6'
        b'+KrQ9LwhjUoOKtwjwHlHBhrtJtMwNmhVgjeIhn0pOAivkLDnc9AKigFDFJp2TI5Oybd4nwbXLXXAOT9X6a5+Ak1iAno/4AFvSIME0pkjlqhTujYsxE7qtpLl774BHefI'
        b'DW4xsBIdHRgU2J9mCgVsJKLXO5NaFFeGkVviXJCsggaESRnOYcMWeHkBbCr+Fp9tQAds1aariXUNR3Plyg685KJwfiQ72KaQCppAM6H4dngWCEiM9sooiyRCcVVwhAnb'
        b'i7aTcY1cCzoJ0qHCBVwrRRSPZZqho+810pB1mWgdVYEzoJvA+OUw/KB6Jz3Jj8Ib2+GA5lZXJ3AA8VfMDJVhFxOcj19E5zg+WoT4ZpW7K8/RlbETCfnK2Uxw0WgNz+rl'
        b'xC/8L38Qo+5TSpSyGf+kyAp+RsYzkRVy14jlwVCBNhbvXk3ixgfVB4mypR7XJHCib+/8rvlD8dfW3Em8Gxj/ZqZgwahpIkGPh7/p+5f5f5ov4SWNWKwYNlohj5eX4Sl0'
        b'zYZ1Hbvi+4zPrR3i33VdQIPYR0z8hvX8xnUNawMmjK1Etmfd2t36bEeNfYe8xunkqM072vYI94xYeoxZzpdYzh+xDBSwJ6xsRQliq/YVp8wEihPWdu3pYlvxli6HU7l9'
        b'yyT2c0esfcesAyXWgUNZI9aLBWzBMqESNlfglESMFpVJy8VZ43Zjsc8py1EjT2nZ1EUdfPGU6aiR6xNNymTeQy3KzALbU0Q+YobYSuQ3YupaG/qRrqFwvqhoxNTlrq4L'
        b'6dCSEZPwYb3wCUOb6ZYbXX0SBD+oLkhkO6rrMMNyM25g0ZRbl9uQV8v6yIw7buFw12KROKQ3vCv8XOSYy0KJy8IRl0V3LSLvZIxbOY2bWuAwhgHCgDFTZ4mp87ildVup'
        b'sLR5zzjX5qx6u/opzXGu7biFzUdcW5wRd4zrKeF64oiRu4S7xizdJZbu49Ou2DicDWgPGLPxldj4Tr9i64jTCo3Z+kls/cat7Wm0zByJ9ZxxnmuvWZfZGC9Ewgt5pK1s'
        b'ZfDQgLJyxI+OW9q37RTuHOc6kL9snM4uaF8g+8vWeczWR2LrM27Nw0M9zvMY4wVJeEGoCkuDRzwLI51a9sMgyspuqhG16mh64PQBY7qud3Vdxz18BtX61cY8Ikc8Iv8U'
        b'M2ybUhszYeMgZveqdamNOQZIHANGbAKHtbjjPvMGo/ujx3zCR3zChyNThletuRu5dthhHbom0pFo2U5Y2aEJnt+eP2I1t1Zj3Mtv0H3A/U7Q8PKEuyGJw3ZJtRqCAomW'
        b'9Ucy8nhLbLzH7bzGHV16lbuUh70WjTiGINqNu3iPuQRLXILvuiy7s+KN1a+sxn1GT8jS8mqM2C+QFaFuO7c737We26c/bmXzSF/VQKeW+ciI0jMf9547GNAfcEflPe+o'
        b'P60ctl9Ru6h2Z13chIFJQ1Yta9zQpL5UUHzX0E2siE1xhngC+Av9mwNqQ8cNTUdtfPoSJDb+EkN/siDD3tST8GJGLGKHjWI/MrUmPilMsfawqfOYqafE1HPE1Pvp59D8'
        b'ELDvGzqK9SToJUUS2uBIkkM17MJfrWuLsM+IxNBRtBx9oCIj0zZNoaaYLd445DVUMGK0qFZhXEu3SaVOReAj8hLr9up36ffpdJn0FQ5l1KqMaoXgq+p16oJMUbBw/aiW'
        b'A/5bs05TxB7VssPfNeo0BEX0LPWQWHqManmi0jEtK4kWYg34fgOjpuy67Kb8unxRxoiBM6YLbRItrSsVxY8a8h4y2frWeA2rClVFIaNGjjjFuB7dpFEtHOahVvXJHiZa'
        b'0RJj35+/3cqkzGweU0z0DM1t8DoSx49aeo6bWT1iUVyvhyx08ScCRwWmi4JWBLLGjLWTVaixQIVkJaVxFbtkL9a4JwN90mZMfdqMOWkkLFiPbZmT5sGCnN81bT73PoAF'
        b'tlT63/QdgDaHts6GOpPj+ZXYJLoI3flrGfVk2WoGg7GI8YTCn9+RzxfxjsHW2LOKvtSgajCTxWPd48gAMFNBKdLZ1NS/ST1/Ofpo1JKZRAl8R0lqEFWVGkSZxCSKDaIU'
        b'cWNnletn6RJzKJtJVUwaN0sVlKfBdtB3BTnDJ3u3gtQc+lSpPITt43jmLObQxM1Sx5rp1lBiF+RL7VqTiJ9n2xhld0x3hS6SmujkqnCRWurS+Xmzmm/SsCWWS7JMY1PL'
        b's+2uf8QkiY28s77VSdY8Jy5xdybWI1k7aFsg3SRs2EVNz6Ptb7ObA7kh+RmZ3n7cNH4BsV/RHS7I3FyQWZhJ6n4xJBMhoNR6+3RE09nMrqj62cO8SY16MpMmtiL+ntXr'
        b'RW1cHOppG5dlbDHOJw27Y9yRWBznBo+gky48D685L/sNKNNRnjI68O4LKvbCvKkf9G+S2ZSIIQabWWB5XPw001JUUAk8qwyOwNPpRBe4BwrdaQwUOtBugY1I4O8jWsZ7'
        b'SqqUHsXha2qlRocF29B+PqqJ+vHqJL1xbFkSgzpWU7wYlRq6glZnIHbx9scnA1gTj+1BMdFE+F8xw1Vluq6UlagOO0EduEk0lqAGNoF+OIA615lNxVAxLtZ0XCex9k+R'
        b'Fykum/JIzRRwyhNpVee4cGECuVyzNCVVlzXEoFLLNvxgcGsRfTmsYyGdFXneBsYo8wttNjd1Z3ZBIEVc2mFFQYY3m1rrRnlRXugYXVMcihvQB0WpxLzHVJIa+GC5a2QM'
        b'bMCGLXSEjZCaDElO8Khl4ZEukfTBFA7CGvVI0AvKyXBoqYHeWZHq5hGzIdIsYBePQevRzy6CrQQ0Kpfnrw10kVx/YbCd2Dx0wD5Qhu0/3qB1MnIUcye4BYXFOEAa2AvE'
        b'rFmMbZExJsXY1OY4GXEK3XlLuRSc3UMo1bQdZx/jqmtSqblLihWlquWFG2g6BgessF/KXM+gFpaVjHt+ElhQjp028RWeAqHpClDtDM7hRAnVWOEcZEInYWkifmjnsGkW'
        b'HiFH05uwrETDKmudsxK1PAirmucupDXTbRaYOuhLAziGVc1Z8DQxP0WDI5n4CI5mTpUixYZlsHsuA/TGRxJyRK3fEeUWCZvY0w1EsAO0E4vXnhxjqXYCPdodg5UT8Da8'
        b'mfPGqkp2IQdx/J1JO440xOSPemgd+te8v03U2L5fdP2DTk4iR8tB4/68x5rzEh+st/o00qw+cvG5/qQHn+kruZVb1ln8uLd6oDhos2Pu6RivHZ+1jn3yqOa9uI6/7htf'
        b'8MpXgkjTkl3dhoMnKwq677bGlf/4fWP3xXdHF7GvLPpm84Jjbd6HxbqJ3X9+3e/1bi2b7G4f/8OP9yZvDe2O1A7srPz2VHH+h+2RXg+//vZC/72uSD/v9z7UiigrfzXp'
        b'kwt/evDhO6qLbP8eus6+oT7w/J6uHa33371utme47Wryve7SbWdYR9+0/1LRxnqwQvOLhV7/eLy05M720Qu+bzSev/N3zz7zC1mff7fzYIatcVzt1h9zF3oHKY11GLfx'
        b'D3Xe3HBQQ+V9hsfmBf434xJHm8RDe906Ay1U/rF/Xaa4/2Ty5w/aWpOPOqlt8zH/9qqW6fzB5uPM0szupZ/Hf5P//XLFX/cEcQUBlsnpu4L68jQYcV8Xxp/5YHBpmNbj'
        b'xiur1b+J+5+334jv++Xna5deX1V6NrHLLTSnwWnx2Q96Oppd2VrfayfeGJMIlx3TE29P++fDRevUvXf8J+F1rX+vCfT+eetfM5jK6wYL9b/x/uWQd/m6moGDPvpxmz64'
        b'earY6vX77/yy48bjT0xLT/fmmliPCI9vn9v/YVpoQNsw58ekJ63rvvhV+5eCSgvtXvtykUORb++bG5ePzD9cv7F66eMPfjy+hz/26dGwtt2sL/7c/ErHdzwDomTbDc47'
        b'ywCOxT5YcbdiOY3VbgSCDKK1W7x+KrwAYmBXiWrCFjT6yHSw4CI8JwdyNNxEO8w7wJOy0GrUEtiJQ6vBk6lEz8SB+6CQDubEhrWbiXKvewdpUF6xqxQT6QMuY9VrEayh'
        b'3exqGEnYHQMeCp/NIwNUgUFStzq1ADGdcGyHYiumhDPAANwLymlVZJsxbIkiFv0o1yBwyQnnD2lmMcE1ZaIsSYGNsMNZmi6a7R2I01RDESwjCiltN3jZOdJVH5TL55OG'
        b'hzXJW4OT1J1RawJgHemVsjkT1M53oMM/VEQ5OdO5/cC1eJLeb5c3ra4SlphNV2NSuir6WItZAHvoNBZdqF8VWKVoBYVAHC0Fm2rOZa2GNbvoEJwNW6OJKgrWxLiYlETi'
        b'vchZkTIFzWzQ6hlExmIdvG2PH42JjlOg4t0UzZhsIIJV5Pk1oK9kmsqM0kXXbmKlGWJQ3USrbwRvgqMytVk2FEg1Z7TaLFWW/+UCbIqUKc5i86dUZwsU1YjWDB7Kc5cp'
        b'zeBFsB8rzqZpzdBfLXSikhuwpQRrrZTTsN6KVlplJ/Is/+81Us8+omBiygtCM/VUspyG8tCvEtOn/fPkLhJV1WtMWlWVm8qgjEwmQbHrRw3diWol5M56iV3siEncsF7c'
        b'hKH5uLlVW4owpXl1XdiEvqVIUcwa1XeZMHcSzx0x96oNw9ECs9DDuu7j5jYYItu8pjZsXNdYENoWKYxsjr6r60hqXThiEjysF4xRto6i0FF9nni5FGUr8mz2FxtKTD1q'
        b'QzDY1uljQ5MJUy5xKV02YrF82Gj5uIllm5PQSZQ8YuJWG/IQTUaLNmehsyh9xMSpNmTc1uFseHt4XUztYsHcj8yt0esNzQRF9buwpitJXNxX3FUqsQscsQoSKI5zbQUK'
        b'41Z26JuhuYhdXzrBtREtFif2JXWtldgGjHADZZfxB+69hVXbBuEGsV2fothixGKegPWxqeWEo1ef9zlNobqALcieMLUet7Y769TuJI4/5S4I+cjEXK5xE4ampPtRIybR'
        b'w3rRckqBGWqu3wUoWziLQ4dCRy2C61Rr2bWZ47qGAk590Ex1mJXDmJWnxMpzxMob3ZdcpzGhazCuZ9IUVxcnChdnjOp5T+hZiWzF7FE914cWlJFZreojU8rUstkeEVPP'
        b'kNwXLNoithrVcxlHV4PHjYwFYUIVUaLEyAn9ZWgk8K7fNm7GFTDGzcxFCsIIsaLEzA39hR7GmdXTRcvEVuItfcFDi2ojRvUW4PKYuhiR3aieo+wFoTifOPoeWxcr8hGr'
        b'SGy8+8IkNvNH9QJQ6ZienUTPDpFBzxnfE1kXKSga1bOlNRBbGGiSSPR5P5HcGEBTP9KH9ZaPQmSQFAxtQGsRTipScmEdX47aYNZ1imueqUeY0iVcx7qE31qVKqgfhTh+'
        b'1X+wMiGVwWA4YV2C0/f444VcaFkkvTHptCXuPlfxKd0Bphg5P5Wgj0ZlOd0Bq1ypnCnN4UjrDyisQchSm9QWKL5UbUHwbG5AMm3BVCLHSa8e4gz0kl3e6GdkYT3p52bJ'
        b'YeDGDaFxsaQpz8D7Eg85rFJAt0bEx82b6+GJj/Cb+EUY1VlYVJCTl/3MJtDxRKcwrk/HWaevv7DzLyeWHKhWw6uq5EQDzuk+2/t36kSVHxhGZ+k7jIQyW3Aq6insWbUL'
        b'jUw7aQX3yaBnaEO/wqCxZ0ttacBS23x4yQaceCrjI4a2scGJnCD2XFYhjjxj/L7g4FFPHeChxs5cFZvLubHvY/2ANxpVVVgK1fF3TvuVHFryaQNnX3u40Wjytvp3d278'
        b'+rSygcY34Z98+d3DK+wFc2qyvsr88r3hfx3fueq+6KNY/dIsQ7tfk/72QdLe/UFLu5mZ+m+H3fiXSUvSxRX7+x1d/lThzWr6s/P+9MBX1m7/MGc4W9W1ct1bob/+/Fnc'
        b'yVJ7zuKGxfq/9LktXvL4A9ZfH9h8fesET4EIXdYOaVO+xR3wKhJsIzxoG+gVcMRq0rnYEXZIfXeS4E0awXA2HTTPgBeALljB5oBKeIQITTvBbSQYYtEN1sMzcuIbFt4W'
        b'pdKmt8bt4Aq8hETdSfM2I9EWNr3k1GEz5QuNYrIsJyUM86d42fTLRMboo2hHnEUZf8ARx9BWlDBi6IQtP6aCYomu7biDc22owOSunu2EvvmEoZXIURwyaugxYePRZzRi'
        b'4y/gjDu4jzn4SRz8Rhzm4zslaK/QNR7WtRu3w08a1cWO2zhjG8KpoDGb+WibGbEJRFtjikSLS1I7i0Lf0+LJuXJqyvnTTDLSP7iFFGrO3B/ojeFVvDH8NjF3qEldb/DW'
        b'kJ8+uTW8yK7wHe4R455SSc5mrOr8v04d8FPXTJ+ZgvT1OVul4UelCVmmBTydheGH0NrG3B1EPZmzaXNuJlawZmZYPXNzkBLg6XCaqPh5Mv3OZK/sWBIx0ggeBhdoNIu8'
        b'umgaLhuc9KbSDDk54NyinE9WDzELcYiai+0rcbgQOg5Rhmd6ZbHX+awDF9v6Kn+ITOZ38KpboxNz1dQ8rtq/rrNVcH+DosAo25/6qkt5e+irPDbhCTvgTXiGZkzoaHdF'
        b'CpU5lUFOmAEKvpMwGSiEzfSRewUYoCMR9iWC85gvwWZw4qmIB/DQYhLVLhyc9YQDmBv1w2pXWB4Bj8SAChY84hwRs0X6QBQ4pwT6tFN/OzfDPS0+PciymV04mS1h0rzy'
        b'1A2EkXjSjOThwkwGpWcwaQd2GNV1oiPK3XGYZBz3DXgjBs7DWs4z8zi89oz1OyOPwzuKcnkcntUyoZpcHof8DLQqTV80LDlpXcF5BlYAxsYmhMUW/Iibq/U7YcqnYr3h'
        b'WCwkOALxJif+e8RqRcRNwlpIX3jG/7eHWGPqqcjlM+VjO0zyp6Ija2D72gpZMHNlda3HBjiYuU37tlF19ydMc/V0Bg5i7vGQfH0UJIthHoFjmEcxSBBzaTRyHDLc0K98'
        b'yfccTXWfR9ynAoQ/UNcT2oyqW3zPVFe3xFVaPsTfHluQ16EL3zA5dMB0dAF9e6xHt6NwVN35CdNI3QxfcnmIvz32wZdWdHlftZmwtOnS6w/5lsXQ8PtoYeh4wMInrF0M'
        b'dbMnFP78RgEVP2Tjr493sfBD6V2s/virelfXD/ssGVUPf8KMIzfjz2/oT3RbBOMhKX+8mjxj06XbldDvOOw4/5XQUfWIJ0wDdadvKfSB741E96Kvj4PwnfGj6lbfMlXU'
        b'XfAV60f4G+18jbFeEaBeDTGHvsl46PAy/hId58qkHB0UtoJq0FP8LRNjueJhHWgF9YH5sNlDCxyCg/C6vu9cUJYOexX9YTmoA/UcUAFb4T5LdVALDwIR6AENoaGgQxXU'
        b'g0qGKbwFBuEtdSD0h5fAUXCRDy7DrgR1DKLbD3sDA8At0BcObi1Bd9XAyh1gEPG0Hrdd4FQ0uBCwC7G6s0qwD3Sj/9fmgDPgFOzM3uJlB4WesAy254GT8ADsghdh865A'
        b'UAU6YQXoN1yyJSDOAFTZwLKQ0g3e8AiSUwdzAuChjUtMLPkmYf5RCiu9drrFgVMrzVxBA7wcAK7Cs2AA1OaBbtTdKnAlHFzx2+QEa7zWwWp12JkB+3SRlCYC9bAD/b8O'
        b'j6eGwBNLvTeAI+nwPGL0SEY7lA/6YR08GQ/Pg75tm+BpcKsUXIdNCaDOGHZsXAWPg9O++vBCOOgA5eC6B6LxfvSyo9qhoDce7HeIQo24Ak/MA72l8NwyIGTATiRH74PH'
        b'QAv6XbMeiOEJ0LHNgqUKjoFLsM3LBZ6CV9bPUwmAl8HhdDNQtmQTOJCBqm2KATd46WH5lmHwaA68BZsjYeNKI3B+ezAcAhfRUPUFKgLBMl4i6nsVaAQHVewT4IARbIcd'
        b'6K/BGCSotiQjgjSCJhc4OC/ILtBWTxdeTEIFLTsdVjmjmdOtpQsPw1pwOaEQldZpqFjD2+iJbtgPelFz+ijY5J05HwpXg2YvcEMHtmmkxYCj2UVBsGw5bLIAVevmcuBt'
        b'MGSmC4ZywW1TcCgbPd6zGVZAgacZ7MiwTkoJdIcNaC4Mgc5CPpp2x+GJBDXj1SV583fCS2ZrzMGJWNBhvAr2Ivo0QTEHdeYSmlMnYMdCWM0BhxfDax5oKI+Dc36olz2o'
        b'fYNgfzIahRrXBWhKVG4HFw1NYSWiz3Uo0tjNgjdgxRJb2LKsuIZJMq0LwFXQujwYHEUzXw3cgAP6uxaiIT67GJRZgBYocFXzgRfQAPWDk6zFoDOdb8MDtevZoIq7xx2c'
        b'mVdcsl4TNqL52AHFiLTVm1NXgJv6yeDEQnACR+AF+/mwxQk2OdvDIXgNDLJAnzI8Zgqv8BU2w1ZwKXHltgWwuRTUFMfngnOwGRHjpiPqCZoj8Hxe1HxUy0kz0Az3Lk3G'
        b'finJoMkXNflwGlqAe5l+MbAe9Lmiey5CMeguXVWqq5W8J81nSTZs0d7how3Po+5WoQm9H3V03xy0uCqWWEbb7rBH060GCGGPJ5rq59D0HILlfFifC26gbi2G10GFEjwT'
        b'BOt3grbiqOAceN4BHnZEx8nbu3zd9oBDa5XjwZCRBQ5iDc9qz2Pnw9up8CIT1m434C+GB8CACqjeHQ4EcK/ZEnB0JSiDBzM0QRsQx8UneqXr2BvDruAlKno6bh4Kpt6J'
        b'aCG1RsPyeOJ11W2EVk0PKOPDzrloLK+DffAgC9bHgjrYz4UtsbAyGXaDAbY2mn6VhmiN1QDMnA6u88LEBeWwB1zatt0YHLFA7zuPZpV4O5oQh0u0OWhBDGTBY/DqLi89'
        b'0IBoeAANTx9iXpc52RqRsM0YCVeilCR4Dq27g3DQcg24GRMFboOzyragvhCxhU5wyC8TDmyCFcngppsJtiusjgODpmjSnYNHloP6qEjt1dvgZfS+TjQXTq4CewnGuhfs'
        b'9YLndB3ibfXjwF5E8Msr4ZlcnEo8DlzkwSEFIEizBe2oTSeK30NzMgAOICbVujwQ1OApidp91RlcKvaDLavZqF4RPJDHB6ItqmhlNs1Z6gI6tVKjQFcQRpYiat2ATaZo'
        b'Ht0ClahrF0FvBDi0Ci3Yg9bwZnhQUCAURIJTGVoq8CCasmfQjBoEB9BBnrsVzeEmZhC4sYOa6xYBGzYWOaNhGwCdSMisBNfQ4qlHq645bdWaPMQ+Olxg8wZE7uvYaaYS'
        b'zdRucAoch8dWL0as8baz4YqiNWuBKAa18DSshZcc0eKoW2DttR1W6ymDq/LzFS2Q40uNUTsub4P7XZX3gEt5hGMe09gBhIhVdgZHzy2xSgd9sTt3GbDWLgFVhmBvFurY'
        b'bVRBJ2JN++cGodkrUNoEjoCz60CDOhriLq46aJgHheFAVIRu2QtxT9rgSbQvnQVlmky4PxAxkTP6SmBwHrxmZI8mw0VwzQve0tsGT+Xp72Cvz4VloBEt2EPwmCYi1GnU'
        b'vU54AwwsRaPZoQ0rV5qvR3NtP+xfCE4jkt9Y7YB2pwsrt5uhudu+KRDWpqI9rIkHurah5VDthoaiI9gLcbkKNCvR3rnaZ+McWOe4AYpLF2mUoAbuB2VoJneAAU+uYwYf'
        b'DCB+M6imBxvgNbhfDUOWYXkYOOmVgOYEaN+BGlEBaxzBZTRrzoGaEtihZGqLCH0dng5b6Q5uwRaVMCfU6UPoORHavJtDwcCS7OVoMAfAvsKVaEiFaFtsA9dLYNVWIFij'
        b'lAmPB2YtcSMbe01UEdpxDhUjrlCL7jkesMQwGTaB5o2gkrnVCLSgGY6oiGY4OJmyAbX0Nmxj2eVHhsGKPHVYl7lCyXwtPG8CmvDsckcruiNMG54xJTMb9s9BKw4x2zwi'
        b'ZdyAvc7wCmOxRSoQKUHhchUG6MfOY0fRshGA2iJwkUIM11YflnkiGgvMdsILSuAaOJ25xBGcCAHndNGGcMIY3X5UA7YobTLbgObNCU20HAVePHgr0S0cNC/bCY+ZgepI'
        b'C194ZD24CQdVEHVuwSqlpaArFa8YPmPzaiwVtebBXnh9zQrEMzAL7kHMAEki+XNBs+5C5+U6sHclqEsNBfsWg2taULRkzypEGpHvTl1QHR+9EnTZwUt7zENSEfPoRiNy'
        b'bhOiyznQvGoHAx4P8wZXEzx2aoTAvaAZCILS0e68Dw11h5E2ovcheJoFbmvD+kRDLRO0/VXqgdo10fwEtHxvei/zz0ULuSEZNLiB/dF67npQnAt6FqIFWL4BHLOH+0IY'
        b'sExhKbiWsQg0huWAgaBYcB2UL/ILWbzbBArRCkCs8Qx632FqE9oEOmC/IhChpVBhgJbMRUStGtjiBW6CamO0UlvswPVSeGVLEJq5ArTbHYXHA7bAjmDEVcoylm0Hh5bk'
        b'o1UgKgXHS/XRvLqcsQN2ZRtBAeKD7YhVVM6HR1Zoz4Vo0tfC00uQgISm9RmuL2pDK/p2aqHv9iVaaGcMNQED8WgeDoJLO3zQur8Ju0NgNSLbQbTptflaYMGsAFRncR3w'
        b'XIR1egsIP+hAzSwDJ3PA8TTtkq0xsAW95f+V9yVQUWXX2lVUMRTzPCjIrMwgKPMoyjwoMqOUDIWAyFBQiogCIrPMMs8yKjIIiIAg6b0TO+l0EozdrU2n0+nOPPXD1m7f'
        b'n87rvH2r7O738jp5yVr/WvnX+tF16ta95557zz57f/vbp+7Zd4lsqwvasuhubhItqJSCJhEJ/preRepeH3nQaXKchfEwYoeDOKYbqXScfMVktjaOCLAjmMZ3Au+fgIFT'
        b'dIuz3jBLllzrBleRMfUN7IyhJmqSM88xXggrzurhYj5BzAJWmQUkyuP87v0BxwwYCBa1SjFJAgXMeo4o6sNXPMIaV9hnsYl4hJerNdxzgPlzCvvcZIXEZLsDYrHtEPUF'
        b'hv1ohDfo0otCktIyg0PxJlDthJX7U2CArl0P8/kXvRT3hJL2zqXiENVhlqV0lRlCuXUsDfcK15XAsBNWrZx9cPok8bQOXBUQx2yC6+LVL3eRoK2yzBavM0/M1B46CcMh'
        b'2BnlS861ReALPTFWxDrG4L47Xa2JKMkwrKuQdQ/AiCreDIKm/cXYphxuePos4V2FLJnH4EV5Psybux8O0/VSIg27DR3KtgZcEtqAvLobLhnuleME4BVjkmO5OWn9uNpu'
        b'8vFNzDrnE1h5Eq77ASGTN3lCAifiCLjGx34c9CggwOqASXInY8T352mY2EdtY6HBPJc8dR/cjsTKRLxxwh3qw2zCSWyVUOefvTsy8BjDYupPXoaJVEu8kgblGheNsIsc'
        b'VmsSLgtJdTqP4fQprLV1gC4p0rOhMKzxI+3aJGSfOX2SIpMWQu86PV0S8dIpbPfAGhjKcyXRTzlCtTcpzRi27k/QzHDGfge3yFQYO4UreScInYc9VOTNnVw09ZwsCdqX'
        b'FLFO43DEPvKIm+bQH0MNtymRcj04C/VRsWQlaydgeC9MaKbjnVy6Zh/1dCCZbGE8SaBF8NMGM3Ywp0DyrMeu01BnCAsn85N1fOBWDlWagZ4MAogeTjbdWPlxUvklJ2j2'
        b'go195HNX8WqZJj5g5WCfNelCnaPoCYO3lRfPMEpZkSvWyQ3SyWKcFuDUBTnC4UqNiyTCir0GxHKX9B3UsV2VuGRcVEkQtJQZml8UQXWK7lG+YhQ58VHmH1QeJOzvJByh'
        b'07wY5lSqqgS3i2lo13Ao1keBHOYybKqcwnHsySaHOymN5SLsiBbAxsVcOtSXepLYzKyYQAARiPuwkUXKv5iqi1VCQxy3IL24QaYzHZ2LraVGhA79DN/NpBuoTXY/q6tA'
        b'Z7QScnSSMBrCE4jr3bp0/FJcZrGJYgQSZR3FcRMC7skT3sXKJNsGYEy3BVZy873VYVmliCRTISRS0RIf4cQzw/nUCLwCFPq2wDJclcVbSgKsPWbNZCK4AjX50KtCwcpV'
        b'GCzGBT6p6ry9onUIwVNPlmpA9gVvCp9uGJCJzhHYNOy24JIsOxyIcLboaML1XCPDI2Srtw1wNZBwq5EilCVyyGu5zGJHbCswxwlTinFv4dVLMOMGvRa2hIArsnS9Spxw'
        b'ChQ4FRufyCBDryCDqBSRLfTKQ9t+bDrjhH1h5mQOixpqhamEgOt4KxFvnSTLGTMmFex3IeJyzwlqcCU/F0aLKBavpZhZx0GTELPLh/Bq0cOU7rwlExqJNUjjVAz5y1rS'
        b'1HbvM3g3Rg+ruHAd5wR03QHStl6W6Xmv/MRC7aM0xHdMrMhiBqA1vQj6vYuh3hTrpE9gQzb0eFLdBVgi4tmFdbHkJxqY14tohinDUMjeskjS0Ns4W5KQQ3Sx67j3ERcm'
        b'QJt2g3E/odUJuEda1RwOdy5maWYQBvWokIIv2eLosdJAbA+wIqWY1THBCvuw7BhmMaKjpYx4/bUjDJ24eCo0WJrFtmdhvRnOiR+WOyeEmZikL9eWM4EOXpc8RbdCYd1S'
        b'YkyotRSL7cvCnjDoEjekHXgUF+OZBZhsH9p9FlskCSs6LMlv1HkyP8mwWewQFgOTWCduyxB67U8R6jTYsJlnRHHwMHSKgjgsFoVuxDMHyB01kln0+iqSyOcuyxsm8aDT'
        b'I0olRYPcUqsdKcMNElIHw9j34tXggHCozvbWtiSouYfjeiXkm0ZgMFjVL4nQuwX6U7GZyArZLw45M/MuFH23FtuJ/OGWNkPyLsG4IAVrFGBEmEJG0w6b3lAedww7ImgY'
        b'6TiZYtUR2hyDSRaTwCBGnRhcnz2N1oBjohkpXYUBxQN3rBKo3WZWJF2zSkCdmyPRtdMwU4yTVQrVduRbW6OhZS+FCgukDIlEXlr3Er7NQJsbBUpVRfxweBBKyj5GTqIB'
        b'HqQyEYg+xU2VFJvVulmWQo0T8bc1gol5cgjDMG9MlHgKelwFruc42CwrUMHuoDNw0xlXhNaGuJqM04nBWnBTtlQkCBfyCUFbYYzHTB5At74eVpBspwmNKggdJ04kUlvX'
        b'SKSdCZrZZLWrdBctB6m3E1675OMUcTDtlDj46uVgpSOFMuUkmBkkHN10hGscnE+winTEqni65REPnN9LZjPpZA3M+tib0OJBfKiZulQu1BExr2dpKaQ+jMHG4SQik+1Q'
        b'bwWDsng7C1uCoMMHh2MoqrpG4cuGrBY2nDJOs/TfjbfloOMUdAjJTDYslUV4M00oxAn613ZJiW63zjk2nsLIGcLiVidc8A8sVctIh7sWSrCsjENBZFZXXHDGPpgs+yZU'
        b'IzO9U6dCEfwSVOyCfj6hAHT6BCVGJAnjEnWYcIEc+aqOK14X2jsRTCyc4xA6jMNtW23YFGXitAsFAy1WGtirw+A4ObwahzKy0bsHyUrqmAkpy4gMcqhwzx76ikinauBe'
        b'EtTkkg8fg1uHyXpnQstghk9B3yAN6UyIu3gOZp1DTmYo6TQFVOPQ7KKz+7I18c6lCCaOwNYMuI83HKjYxA0jbegUFNoU6RLhmvbGlWQlrFDCdTYMJpeR0iuIJhlWtZJO'
        b'fv+vJmcIRme9jXxVzuFtbZld53EknYyjIpWA+c7RJKwP0dT2o8BlE7qEJMtqBU3pRH5YFMFAi9Mu0ptOmNPDif26ocaesMg8GVwTrxtpm+YnSz5t5ViseJZmIdKQLtIL'
        b'7c4kkXV56sFCLkHSDXIpG5m4LIJlS5iDBk9rMo0J7M+lL83nDkAv+TSC9xZGT0fhjhXMOuQR0x90x4X0JJJydXisDkM1kUB6PI5NdG+djLpCn+znTiAhyyBXHyetCXYX'
        b'cVQjFqZMCFOboM9XGEYke/A0Uc9KXwZa70DFpRxi97t9iSeM6qkwk1thOFmi7i8Pt86eJBS+JpkHKEwj9W85Y063Rf4MRy4TEqzqB1AAUAEDFOnCZHgyKxtrDuUQ6vQn'
        b'HzpNjmER+wV0k21F5Igr6SRi5TiQlg5zOUddcElHFR6YJpIydGviuJ8dIxQrvKkjwNUs0huG59+i2GFdiBvJ0p6q2LN7P7ZF5hOqXdPAG+rYiO0XiUuVw2YBkZ0lH7ip'
        b'Fmnh42RG7ncYOxLkcCQwj+TeZ7FPtMcyS/tooLoaDmuUidyVoPqQVATp/C1SwDqYuMy8IE0UGwQNSYS0V6xhRVNAZrlOdrF8Ke4sucpcaOLgHfp+m4jeaso5wtt+r9J4'
        b'HE+wJWfXi9OWcP9QMswYmgcTKLQzY0zj8ICgrYfAYUaNurGBm5ePhlGjYweh7axWYCRde203yeO+P6z4EQjX8KVNfIqSUkSPmVRRlgdh4Dg2fBXaxtGlG6HrgCET3SZE'
        b'KbDhrjrWRsCcjC3MJMlow00k/Fs6SFow5xaLG1Bvl+VG+tkqnjO5ZWJLEMbM0fWo2UAVIRopaDXMU2AgFYAPzkfaWtJoTeO6tx/c1IceFf1dJPtrsJROxjrq48mCm3oE'
        b'K7fMoccNy40J6hbgdjwOxUCfYwKhTk0w9KcnkE+Yi2UIyg0cSRDuk+ZkemKnPY4XY50dLJhGY2WuA4xlHyK/MEYdniTS2h9AeAOrYVhvk0Ceo8+KrPmqrXFcJo67aCUK'
        b'8UEEqVsn+Y6qA5pyMJSdC/MEXoN0hfkIWbKCzfxICttbSV2uwVgJdZu81S6csIcOEfmTrohsUiYKW7pslHKhSt7IHWfcsrA7RPssrMNNEfa5wZqfELtIes04H7sHNqNZ'
        b'rnhVSQ43OXSX1eFasCrNzIyMusHEae0g6Dyye5cbhVz11CWc8SAQXyeNmCMTuEdqsFFAsedtDRJ7T2oaYzkZmRaEqY1SJ/xOFyjC3SScyI6MyMpIJpq6oEy30Ev+dloe'
        b'F0KhIQ26Yq11gCKMK9iYrZiCt6OhWcP31MmLOBgSbrAfWx3wjkHmCWxykmJoK2FQFcXQQ7geVlxKvW9IVSXHNYIP9nDNoVMjCqvT4gOTD4UHkIVf88KOQtd0XDUhPJql'
        b'IW2guFCGT+BwWyFBXwwwDGhfJ0F2px0gXnPXxJLMthtHmXw2TTBvQeFPg5os+cZb+fFadNGGdNw4WkBj04jEDlp4sKzuYUeINnhBo0xlH5lWD8HNAxus5cOgy1myyHEt'
        b'kR8RmjxYP/zfFJvi2mWOlA5OYauvihDGNGWy9xHgDlBf7hAcdu5nh0QHM7FTGq6k4aISGdVdJr2PjYcytugnGnBJw3vJc18j+n67hITdcSCaFwOzztgbTxFmL6H2mgIT'
        b'jcO0fgxJmyJqaNLGquMBDO/RoMZm+IYw7ogzR6yQyEyIAQmowQSG7AzJNjs8oU+LJNNXSB5nUgB34vWhQ0kNeqWiDuyGUT03KE+FOnsivl4Eh4YxlrsJJdoysZIHdwTC'
        b'MnJblbCU4EwuZVHAYHiDbNFRJ7ip6EIybsYeXT5JaVUdb5zWwlk5ixI/zwIdGHCBubBS0qpx8ntj2KOHy0UheFOdWE4zudD7meQKSuT9hTSIg9RIm4lrEYx5cPfjjI8Z'
        b'THnLY38R3lbNOKkLE2qqBdCuhddCT1NDFXDdRtYxnAaUSAYJZoVrFJ7v6xKVjbMmBA03yYb6T5ngZgAhVxcMBPt5scgw6skqiXsTbrXBskIG1hwk38w8WOQP87t4bEKC'
        b'e/wThHnjNCgr1GqVmlYcufBGGJWDq5lQ7YY3bZnfri6fgzbXE8jMkt9gwWKyx27CkzWoztpHdjapCyO2ZOQ9ZBLzFFL3n+LpHcT7OtAV7RqaH0jucwqmcIZLp1yBRSNN'
        b'Nwo3RmHCD25J65Mp9cOmuZYeMdlGK2wpxRZGNHXnYYGTv9eD9rZ6wo19cbhKfhI71cw8zXDQFboF8aQ5tdgpJKe0UZyEcwc8Y6Ayp4iA8bodyxkmUoo1U1NJ6jmZeB8a'
        b'U2G+gLhzK1G3RpLWHXfC1SozN4oIV7FG6B6a4cWsSsL6i7Yk3AVFNuneLUWGF9NA9qQXFl+ClUj6Ogq9YRSbD8FcfhDOxold4hLe90zyhi4LcpcU+QZ64VIIUbc5hfT9'
        b'xOG6E8g2NmVTiaiVm0ibidhkRRr6IYwRVZAuM1a0gfetCYS7CX+X3XBJlyhuPLbLZ/nDtBn2+dtDK4f82rASU8NLNYsixfWLp4OCiAdUhsS4GWF1SR7R6g2c9KOhX4Ah'
        b'Hq47y+aQw5lm48hxXDO/BOUU8HXsDVBROI6d6eLf1WaYKf6yi3Ad1piZrFFYjaL+kY1MMJNExG/HYSJIG3suRO1LtKeedeAtT6woo5Drrj75xNoTMBRDLOuurUxmnqMu'
        b'zAfJnyP9HqDxWsRGR5JrdQ5ZwIYKDp+EKqIC8+RXmvZjy25Z6uY4zxZnSzOJ/FWnFsNVL/LHTTDMwQVdHvbF6gbokrrctpBWNcAVnxhoUfaVI8hcw/JAojLTDKAdxFkW'
        b'ee4ObHZQFhyFqqRQC9eibHncUI0r2UfoTnzc++xRaM7HdsfjFEwzDHTRLbOUtKNuH8yruYeSBY/owJo8LMdfyLHCKXNCrXvYB1XJuFYsj9VHjpNVVFE8MkWY00qxijHJ'
        b'u2sPDijKczJ0sCExO+sk3wl7Q5XZR7TpvBlolYE2NR3xTzf3shWDre1xeQ8z60leuxzWd8E95oe7SX0DCveupfp4EW8fPECyGIFZA9tcaA0zFSea7A4qFEHPARqG6mC8'
        b'66lAzP0+kYL+IyU6eEPxsjT1oC0AejV4pWRubfStFTatc09dgEFjCiYr1V0j4a4u9Ku6eCmexyshWKXPl8XJaGjLhEGYJj1qikpgZkpxUsRMddHQ3yfonScHUYljdlh7'
        b'mW9MHprITyzVHYigzlyJw+USO2JkME7G0k5OulYhIVWUSOY4BIwjIS465kx927wE1/dgm4Do9t0CUpiZ87qkV9OXsKYM6gjGiXRciacrjx8W/YyZj1ogIjD6lSH4MlNS'
        b'zXHkgQm/sn2MolTMsIWMIM7sIh3u1zudxtPFMT1XMxreTZw9Dbdlg07RVZaJH41LOePybtjESZdsBepSFQ4XAfP7b0WiJwlpKJYLnbqE5evnsScUbnBocwLWBORupi4T'
        b'NDaTSV2n8WiV34OjIQSl0yT+a9hWiptw31MT65zhvi3eMAvHhhzmd65gZpoq/SgJqGovgUqdIhdvCXaR6i9dMCI7X90fmUc6N6bhSLfX5qCNnaaGlti39wjxBTIPf1KI'
        b'Dc1MvKuIvR7GOK5EMWPVCaj0x1VfmOYVE760E/npIGweZZHWr8nAgH4QdClQfDDuoAIjfvuhx4moQpVutBZOmR6QkcHaY/5Yp4BX/I9SPHzfjvhVjRveUcnHu/aKoY5w'
        b'wwnb/dx9SS6L0Msl2x8jsK8uOWWkClM2NKidxLIqjEjdZ9jEysrO7SeNa4+CKgWxYqzyCb83z+wlUOjHmjyS2gQDBncdiHm0Z2TCqCupNDP93o71OrjoTEFN62molYEb'
        b'mUYwxYU5b3dcZiJzLD+GTOqh80w6fCcZ4tSjcM0CK21IMHPacOMSdKmRftSaML8kS5fKOJ+OppaveypjJ3EHmfMMAarUOJhLsR4pzxUCiVaY0MCewzrFzGMVx0lyvbCW'
        b'fM4cbtnCegCMWkpDjzGRq754uHmG4p0ZGLXlE/0hr+3snncA1kL2FeANc+gOgQlrhyO4KE0upSvYmCLaAVzYTw7uJmMlPcfVDzsRvZ62w80YM8K2rqhTyvxL0bsSSHFq'
        b'sfxgGF2j29TL0PcSi8hl7Rm8mYErllKSLKkb2JiOM0JJxkRJvkSc1xdPHCXCbOCrfL1E6ddYFFaXWHIkq3yrsYl/EidDmTklVxZ2HkuRLBStpBtZoe5WhzLvcGY7sPCa'
        b'uYE4Cy7Uh4fhpjKzBJTLYvvTOSKYEV/nEgFLxymNr2bHqIENuj3xGrPKYvHLgUdDmfcyONJBGM8UH0ktwiEfAr2GMDrLjcXE1Tgqbs6CjI7iIZevp9Wk+dScOA9UF04d'
        b'Ij63gA2WdFokC28k0VniQ7V4NQOv7sKGcMncWiuxt1bxmtg90jowVfLVVJyRy6vcxAYM1sO9M6Eh1JY1tUAQVyURQ4u3G93FwH+ZjmPDiiU7QPz+UEnq33OShL4Ozh/a'
        b'RxkqsSw5knSRxlKS3Xubo99Q1ZWki/xD0Zc7nxXpegeyIiylIqgp8brdLKNjmZzCfyPEKv9krir6e1Hv+Wrqv7eQ827xvdcUnBvejVucS/mgy0y/8LsVt+JCzFfNow9Z'
        b'CIOPHYyUfxJt9+eKMkfbBHVu2o7f+Mcv1z4tyfAsy0j3tXK0iNFrS7n5vdprbzjrtRf0tAT3tGX1tCb0tP9xwf9XAj9tQfC5NxZu/1lrU/bghzoP2/Yffcn7PPDBjxQO'
        b'lb6fPf8L+/Ln2ez7zg3bZ+4FvIHK04f8dN59/5cKsrxHv5hMln6meDLh3z60Hno/5fOEN+wfNZRPm/3g7T9/kjXY7OZ7zOkUd+oHQoefP3yxL+bAf/xQa6d1X7FW6Z95'
        b'3m/6l058bnlOw9l66UcFP7tXUv6RS2/PKGfY/LJ0Pyui4FvgG1x0ej1R3kLh+t0zWcMHDKTuPefly7yhbsB+ssINGLHpbmoGmyt9vzD5UYVSlPLauc2nOvpcHxnB5+Hd'
        b'7tcery06Zmw9Ff3unbfQ86HlD7818tBt8JcXwhbfTCr99mRJ/Sdb2r/7onrh47GDWmlP4he9oj/+yPvj86XZnpWWu5St138om+/2zuPoq6G/vdPw64nLqhlQGO3Q9QZv'
        b'MLAz4jdv2IrONt34wZ9MhLFb77994MybBX/8yMI9rftAyo96H7q7OJ43+vQ/3jonnD3l0vCW0ut7njy65v77iac37ycURkWWrOrkNBu892HYj6LsX8SY/m523aX9s+9a'
        b'ftLfPjji/e8vfD7UeHYu6peqP/704m8fXvjdZth763kXf5nJSq4Mn9b8KPn3S669Xl6H/V0DB4rejNkx9Xyj4Wdxr6n8/C3zAqhxrXvuLRWd/9PAEYvHvC1uXqrPw6Pf'
        b'vxhcqeIYUcD+4N2ldxKbH7nu7c3stfiD5UWHpLc9phu9vo8fXn7inDMXYffcWF/hAO/17bTXh65MZPZmZHb+KnNQ++PoxDHzxAmtxPE45+T7z4fOLC2b/rTMf7P5nWed'
        b'r/f9xeSPXzyeu/SZ0nKKl+Hiky9iPM0m8hrqh3/Q+caMzvX3bDs87C3OJ1m9HIz7abLVRzVT8kMinc1VubVLmgV5W5/3vXDciSh9mfUnH4u0hIUnMZbyLxgkCrTOviRN'
        b'KCDBoSZmTl+ywrTLhaKlKvX/mVBRzgZHxStvY4l43vjGN6G5YhsX5zywT/JStt5DvgpCJZ4SUYQGFaFIyFEk477HYemXcOXM4IH4TdjeFG5WflXrPC6fL1CSYen6nsAH'
        b'HHIofdjwgskb7sz8Clx4TrFAhPdUoB6uqcgpyeO8yjms9JJmWSpziRgvwNQLJh0wOx37U0y/qTI0fnmBcK4MrFKbi+InrQsOwKzCqzrM8g9mjfyklL33+RfMG/TK1A/g'
        b'jGEhNMoV0E0Wkqes+4YG8a4MxXCDLHF2vNOq+OCrrMVGdGf/MzmeJ8xaRv31M7dy/w8V//IVtP/aJ5+jWOLlu75/5+9vPhj9t/8kD9PL8fk5eSnpfH7JV1vip+V/T2Hk'
        b'X/7ylz+Xs3Zi2SwlrR2uLE/nXRX1FseG893G9aU9hcOOwykjB/tKpo71lt0xmxeuGN8RrRy7U7xo99rh76pj0I8dw36iu6vbsTul52Afbzjkka7dvM4jXdctz4hHOhFb'
        b'UdFbMbGPouJ+rBP3E22jYfX23C1Vsx0OSzeevSPPUtds8WvVqj20I8PS8apVeKpltGUa8kgrpFae9uhaPdFxeaTjUqv4M2OnJ8aHHxkf3pLbI972eGTsQdufynB4Hi/l'
        b'VXkGL81keQ6fqevzdD/zlKYtZS7vwEtFOZ7uS01Vnv4Oiyn2svR21yq95AawmT1M+TJKypBnscOiokXwgvnYOcxmyau+lMqT4rm9ZH1dfiIun3Po4I744E66NG0/5em8'
        b'lLrMoWuxvi6fS0qqqys5gct83zkkx9LfsyWn+zOeivi001I8vc9YTPlfqzLfd6Kpbd2XUiY8jxcsKsTHd5ivL0PYidI8JnPUN3y8kHzslMiLu3BSlmf2kvV1+UxcDus/'
        b'F3++6gqzueOrIj4hSpqp+nW5Iy67c56LP1+dID6QLbmCrwxT9evyM3H5qqJ4d4BiHJtn9AmLKV8KpXx4us9ZVHx2SIrNc/tUhs0zfSmjxNPdMRK3x5eiIWEx5Wfi8lVL'
        b'zObOYWlxlRgZns1L1l+Xn4jLV9WZzR1fpX2y3J1o9l4qo9iSbQsqY1/toe1nWTI0LlI7QXKWtCv+v1X6q/KZSOYwV07qWahcqJyB1Jac3vN4VZa6ca3fe1r7Wtg/sfJY'
        b'8Xtk5b1S9Mjq8FuqxsPGj1TNho/9WHUf6bm2xc+1jP+3Oib/WB39v1fnGdUxeKZCt/XvO/5FbDYvmP2uuuGY4pZtwGOjwMfqQVuKQZIF0MN+umHyrDflNcIMXqVROyi8'
        b'//des/z/USFepHPqG1Mn/CM4K3zKLE35CmKtv4T1/1POenmczWarMmvxvrFglm6r/jNJ4JiRfE1Kxk+d9Zq6gp8BJ8uHL5QuDKVx7Na/LGj5XgjHT7X64juDtj3pbT3f'
        b'Nss9bGw3xdU58VOo/MUes6CXR6SeDbuMfKGZ/J2aHXMDD17tb71Lyx7zRTqfuhk15Ai/a95c2qZ5NEjtO9ePVt26HtX4u+vHKnuvH39m/vCdeItne5O/0276zjtvnRzP'
        b'O+MX8avvtZ9wef0zwyfJW4nrHwvf3vr5m1u/DggODLZ122KHGggfr8zWF735IOJp0juxrs63hd9x+CXMP7wQHPm26GFn7nxaKf+g6Iet31t4U7qmU+77Jwc5b//47PIP'
        b'Tk65r31f1G769uO+fru/vPfRLpulrepGJdfffOuIjlfxzp1Ggz8cMvE1NP5MLaWco2/yUK2pdfiKRv9Hiv7RBU2aOivf1sqeMsWDuzI/krm34t/0UYFr0wecc792af14'
        b'4zcNv80/uOr1zKZr4PpG07dfx7B1V9P9i18kbD5Xe9h9+1r+Jxxp1+zDZZ9aGkqSI9/Xz2DC4cjICzgtzhgiy1KABSmc0jGXEM9RHbgaGmlLRJYqUSC8zqyGUcN1DozQ'
        b'ty4x0eXD3RJogGZJXmRm/liWpYyrQnXOngRY2FYPtzsfGrxfMdwqXJYlw5WSU1MT56PBGZzEJWywp2j3OEvZAUfPcMR3VbAXW6yxyYLJEXyNDVV4k8Wzk4JeHMQZMcnE'
        b'GViR+TLNMhc2BRFsCoPrsFySX6dZT5zd2vZVBWWcK8V6ToT9fvFlTaH54qsEOfp4m0mQc/6EOGeMpjzMSRoND8bGy26WwVyWOrZzmOe5WeJUNCXYBZuhITYRB53Y/EKW'
        b'LLZJyVxSlEhyng/3Qh2d6MxQbIINd3GeaWOOxyW8J66QByumzPHgcAoRVmCTOa6Ms5z9xylcYNbBGSX7YYMVk0KHI85N1XWMDfexLUuy4rl2N/NyFGwMt2FRj7tT9rPh'
        b'NtSVSl552J3pYW2LjUxqH+iHhbMU6eOSJCuzK93MhDWTWzyMtjaDIoPDqe9c1u5LXLhiXiS59x6s1w1lbiwL56n7JHSWgqUUthThsGRh91U+LBYyFUpdXx2XD5aCeazU'
        b'FIcxZbCxTwEXVKL18W4hjcO9fFwqoEBFicXSN+XKkm4MvFI3aPUUrw+1Vj/FNMcibeuVwhswpygeWKiGjZhX6cFZnP08ySt6qqFbHLlgX8LZUJixoJGtD91FfbomToUf'
        b'GQyN9hG2ljKswCOypfHJ4qEqStmlQJ1ZYmfmsNjYysIJUrVqsX5owVVoYFZjQEeSOG2PdCkbx3AOO8QSO6IWwRy0xVp7oMGw+nJ15y4RF6oF0WKBBJ3HTZJ4PZOMPkwK'
        b'Vnks3l4pJvs2TIrXyKvH4oJ1iK1Nsmy4rR2bpajFkdf1E9vK0QJRKA1HqB2d2szMmGMz3biGEwcHoSNcot11KgLrIBsrRRkmVwAzFtgihbNCixeSl+u4YIc1M98TysJ1'
        b'd+zeA7WWPv+KmOdf7tP+L3lGJt/I3whO/jkfySxOZXxkVm5W0asw5PssJgz5opz1XJ8lrfFUSfOJ0p5HSnv6ix8rWZQHPOXK14RVhG2pGY+5vsW1eY+r9B5X7T2uygdc'
        b'x0dcxw+41rT95X/tD7h273PN3+da7UjJSGvtSHF4eu8rGn8qz5I2fJ9rTOe+lDnmLn2ESPP/+vGp5GMno4h0U7M88t9fXKAt1d2fsNhMo7o7HPr8/BcK2rRDWuupqma9'
        b'NO2S1vpToRWjgQoy/nos1FPyt+TgXil/GxZasJltSw6zbaPg785BNzaVEhJmtc3JEeQK+0gg29JFovwcwTY3J6uwaJubnpVGZV6+IHebU1gk3JZOvVAkKNzmpubl5Wxz'
        b'snKLtqUziHDQhzAl97RgWzorN19UtM1JyxRuc/KE6dsyGVk5RQL6cjYlf5tTkpW/LZ1SmJaVtc3JFBRTFWpePqswK7ewKCU3TbAtky9KzclK21Y8IlkiH55yhk5WzBcK'
        b'ioqyMi7wi8/mbMuF5aWdCciim+SlOjkLcpnEottKWYV5/KKsswJq6Gz+Njfg6OGAbaX8FGGhgE+HmBQn22pn89LdXCTvpeSnZ53OKtqWTUlLE+QXFW4riTvGL8oj/pR7'
        b'epsTHx62rVCYmZVRxBcIhXnCbSVRblpmSlauIJ0vKE7b5vH5hQISFZ+/rZybx89LzRAVpolfoLzN+/ILdUeUy2QW/Zreiofn1D/4Z2T0tdaKCyb7bmGsWGHpj4idCpud'
        b'I82QuG8qn4vLf5rYGcj42bJes1Xwc+X8SS6DhliQlmm3rcrnv9p+RTD/tOvVd6P8lLQzTD5YJrcBc0yQHmEpJ14Mvi3L56fk5PD5ki6Il4tvE03clsnJS0vJKRRuMNzf'
        b'iHRQssRcvBReMmngSWMlyhF4C81kmcQM1O8QKkjH2exnUlw2d0eRpaBULvsJV+TO1tzJF7FZPLUncrsfye3uDnlLbt+Wjfdre9HikU3IUznVd+W1t3ScHssf2OIeeJel'
        b'2qL7NmuX+Fr/CZN+ufY='
    ))))


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
        b'eJzEfQlck0f6/7y5CHcg4b6CgBAg4VQRT8CDGyTEoyoQIEgUAROiYrX1qkXxANESvABP8ETRaq1WO9Pttt1uSza1INvt2t2223a7u1rtZXd//c/Mm0AQ2227+/v9+YTJ'
        b'vPPOPc88832eeWbyZ2Dzx7V831+Nnb1ACXQgBugYJeMLdJxF3AJ7MOpPyRnHsL4IS4jaEYdyF/HHgHGWkEn4vxynTeMsEowBSp41hYZZZDcGLBrKQQqW8O2XyAQPlzoo'
        b'Z+anSJfXlBuqNNKaCmldpUaaX19XWVMtnaWtrtOUVUpr1WXL1Es0CgeHwkqt3hq3XFOhrdbopRWG6rI6bU21XqquLpeWVan1ehxaVyNdVaNbJl2lrauUkiIUDmXhNo0h'
        b'TXAk7X+InSJQxBRxirhFvCJ+kaDIrkhYZF/kUORY5FTkXORS5FokKnIrci8SF0mKPIo8i7yKvIt8inyL/Ir8iwKKAouCiqRFwUVjikKKQovCisYWhe8FKi+Vv8pHFawK'
        b'VQWp3FW+KqHKTiVVOat4KleVg0qsclLZqzxUfiqg4qpEqkBVmGqsSqLiq1xUASpvlafKUTVGJVBxVIwqRBWuckuMICOzVFgdURg63NvVskCgihh+VsmG/VKQEpEiCwXB'
        b'jwmtAFO4QaCCsa+UcXLLbMc4Hv+LSbfwKFksATKX3Coh9ju4cQEPdMRzQUnV35MDgSGMxIbdIagRbc3LnoMa0I48GdqRocqXC9AB1AnCZ/LQDRe4U8Y1+OG4enR6eVZG'
        b'dBnakyFHW9H2HD5wQdu4uRPQdYMXfg93oB7Ui2Nk8FcvADweA9vhJtRtCMLv0LFieCWKpsrJQDtkGTzUiZ4B7qiFC6/O1Mo4Bl8caxbcDzdmxSfgGFloZ14Gv2AFcA3m'
        b'TkqMNgTi1/a4pmfJ64wc+haega24Cme5cWgPasR5BJBaHFWjbegUfF5PYuHy0HYGOGRwYA86FGgIxTHWKdEZR3TBFV2CB9BLergVXa5FF1fARldnAPxDeHZV8IqMMfiQ'
        b'au+sR72oMTsTbefCDngVcNFLDNzPWYzfy0hhm2F3cRY8E4F7ZFsWPJmHtsOteaRycEdMrlwmALNn2q19GvXg+N6kuwNIF+FKZefxAQ9d569l0FE5JK9J+2Ebuo6upcLm'
        b'qEx5dI5cwQAnD64DOgm34wikcVPhIdylO9RR6dGRaGs2aZojauKgs/Aw2lfG2JBBgpUMXiHJ4oswKWA65WH6FGA6FmLaBZiKHTEVO2OKdcUU7IapXIwp2APTrhemYB9M'
        b'8354DgRg2g7ClB+M6TkEzwZC5+GqCJVMFamKUkWr5CqFKkYVq4pTxasSVImJCRY6Zwodbeicg+mcsaFzzgiKZlI4lM5HhQ7RecWjdO4/is7zWDo/vNoOzAW4t6Ul0RN8'
        b'nQENvK3npu5liK+kyj33STbw6Fj7+GSuFIeVROeVLWIDb83mVYgYEQDTS7JXOswC3aDKAQfHZnkX7nf4BM+ZD8K/4DwfF1qvAFWExWZPNzI9dkAa6xOb9F585aqdbHDc'
        b'wi9c97gyEXenC13+Z/4Gp2QwCAwxZIwbguBRTMiNMXMiItC2mHRMObC7MCIzB+2KVmTIM3MYtMkTVLvaT0EbYY8hDaeJmuKsr9OtXGHQo8uYgC6iC+h5dB5dQr2uQicH'
        b'F3tnR7gLNsDt8bGJ8ePjxiXAy7CHB+BLC+3RUdSGzuByDNmk7ONoBzqalZ2Zm5GThXbhGb8dz5WdeFruwPWJiI5UyORR8BzsgqcLcB4XUCtqhvvQObQXNaHnUAvaMw8A'
        b'r1hnd7QreQS1kTEgLOB+BaE2DuHGmN4YTGP8RK6FHjiFPBt64AaOGG0Vd8TIc1K4lB5GhQ7Rw+ZH6YE3ih54uToyoNpbY98C+tnYt2psT2/ZoTdEb3q/8tp6JtU7p/Nw'
        b'fVLh5vgiJS+ubNs+WNm1Uzr3vaVfeKcaNw2cH/it5I2SN3i33t4g2/V2tofgLSfwt6eEyV8myvgPCG/Idcfd04j7bxdmDngyP4euT2TgecNK+hbtC9JEKVADvADPoq3R'
        b'DBDAnRy5Ah58QPjAMngdNUbJI9DminQ5B7/bx5Gja2gTfQn3BsOtUXK0Q5efHccHgicYdAYdQiceeFAeuAeeQY3p8AwAnHXQaMfMcs2X8QY5ETIdJlow7OhJR0jXr18/'
        b'6DG5QlezRlMtrWCXY4VeU6ueOsg1aMt17jgSh8TOx84368HdWRwg8Wyd0DzBmNgypWHGgNiDfWhPbkveP9ksjugXK0xihVkcS156tSY3Jxu1XRKzWNEvjjeJ4/vFSSZx'
        b'klmc3OeUfJ8MjM4OOzLBoH21erlGj5GAZpCn1i3RD9oVF+sM1cXFg47FxWVVGnW1oRaHDNdfQGZriRQ3QedGAt2tzgzyNhE7D9eDr2dyGCbgAxevxmXrHe9y+IzktqN7'
        b'48QPeK6bcwaErreF4m/u8QFfZH16eJ/QxB5BKDjqGMMt4zyOgioJEXMtRMyjZCxI5A2RMf+/SMZLHiVjh1Fk7JZLV1d0DE/Xk4vhTn02Hz91A3gCNqMmA+ma+QUB8Igu'
        b'C79gZAA9OyHf4IlDfeA1LuxEG1EvXmwYPoCXYDteqiX4lSu8jDpzolAjeTMToL0q2ExfYHJ+Cb24NsIRL+6MG4Avroa7DITu9HitvIhenBRFXswBaD+6irbQN2gT3OkR'
        b'DfdHKQSAWQjQCfQsbKCZzUfn8eJ6ZhxqmYOf1oCc2eiigQwg3OIEt9U/hVrwEEeDaCk8LrM3kFYHYV64G25PnITHBcMD9Ey5Bw1fFBeN+V3TkyT4GOmKRjUNH1eJOouC'
        b'4Ys4H9SKP/CQgjZ9LdoLW2FjMqJvLuMPXnU7aZK5AXDzyhr4IobP6CD+TIDnaLinFzSOhecQfXEdfxZmsz2yM0CIumrhi67Y34E/6IwL7XS0FR5wXalBRzgEhzpOnW4Q'
        b'0Q7khsHnMpU4l3AQvmI1zRu1OWD2/MIq1ILnQiyIhacNtJrwJXRsiT/uyxbUit/AXaAY9frTV4kYG/XqUe9KBsCr6zioiwlNRM+wDC39lBujf5OMcOWidU15jhuni37V'
        b'/uLVj9snR8yo++xOp9LtA9kn780ULmk8m1L3G86nfg88Hr60o82767ca4x/+eK3+2o5vN85NKDR43pEJfELTd2d4yi5op7u8oA//y403p5/aXXMjcvmtzBNhayq/cD/y'
        b'8et/zutfuvh3La7ySZXt9aY/fRv20cEp8af+mLf5b8LVsU+6vnhrl/rIwZ2Mq7JyUu+ktU6XHt5zK8/db4qEKZ6lG1LvLg+6cubigodyfc7ir6JWjXE+OemZ1zQtr3xf'
        b'Xnb81A7HA3/xc0wN3jPgjLkqabce46gohQxtiwZJGN0J4GlOArPkAcGf8XArxpCZctSQkZ3LB47wPAe+6I4OwkPrHtAZch2eAKgxGqNHuSB4DhAUcUKEsO1BMJlWsAFt'
        b'oasu2oYRoQGux8N3OpMPxIlctBttWk4574JpqHuYpafBKzzC0Z+aJBM+wlt/0NGTAZJKCdOysK1BR011WU25ppgwXZ3Uym5/y7Lbr/Ixu/UY8PJuEg4EBHdJegpvSoY9'
        b'/kH3+Byv4IbZdwXAzb3Vrtmuxb4h5X1XnwGJR+vs5tnGtJbsJmbA09eobtEOePu027fZd4R2cc3e0U0pd7nAy8+o3qvFiQPD2he3LT5U3GzfxCNpM5ozjOVmScRu5h4X'
        b'BMrviPz6RWEmUVhHRZfaLIptSBkQ0eI6U8zeEw+nGFd0Le0OanfrTDF5TzSLkvF7sYQsCy0T+5z8v/2CC3yS9U6EoCPt0yRCOEGAXZbv2w0y+kGH6ppiPRbrKjV6HRlk'
        b'nddjes5uiN1b+L3U6mSQ1xMt/D4P83u/uwA7P5fp7xWEgWOOsT+F6RPswh/B9P+PsYt9bhXpD8NSMcAiy/z7nJLJ1UUUn5aOzQBNmIscXVbicL9IDmbR0Hfq3HApIP+p'
        b'NSVOg8LVLJRtW+sAMAvz/iqwJHrBTHfA8qKzXuhKQiwuCbaAem4p2uOmvbGghdGvJFPsvZO9ZW1viODpV0Sw8o3XgODl7XNTnZxkk50++VP2XKW3t/uGa3Ufi16VdkXE'
        b'xz7zuxe2B2f75q88nNTn/6q0IvtWcHZsi3qpsqPCrpeX0AMM/ARe74XYTzgajKnm7/FO9blTre79oqQkX30nmws+9HAVTC1tnybjsPN3Wzy8gEFRej28ZAVFdWjvAyrV'
        b'XYTnk6MUGdGRMgXGyWgrbpaUh3aXFTnAXTL+D89HPmBBkGUyupVVasqWFZfpNOXauhpdMUZAEdYpWcZOyXt1HCASNyU0rjYGN65t03ck7F/dNWb/ugEv/wF3j1ZZs6wl'
        b'qiHtfVdPo779qbanupb0B403BY0nr3GylKbUJjtjiLHUuMIYbhIFN6TcFod2zDGLw7sSTeKYPqcYHRkF6+TglmnLB+3KagzVdbr6nzE3IqzOQtu5ocdzw5fMDd+fMTd0'
        b'ITj1KDRPybHcMieo7GiL5ZkR8+E/le1GgSD+qPkwg5Xt5AVi8KYui/TGomfCfSzEn4fFNUk1Rvi1JVUS/zxQSNdnGV79iRQch+WkvSBOJKRxV0TxQR2g4l10Nm8hOyfg'
        b'C2g/7EzgkTWmC0v58asm0cizS7hAJCLiXEm2bOFiQAEBPIT2oS0JmGQS0AGMRhKWooM09qwFzuDDOtzG/BKnObpVgEIdvDztgDsTMAxJFGlAYiQ6SWHCKvSsKAH3+Tgn'
        b'ORgHD0hoBmv4HsBYoSJ1m7w4XwZYmNE6G11OwD0yfix8EYyXLKZRF9r7gxljDaQs/99OX81GhXsCghMw8JgAO+BJMKGY5QLdEVIgCt5CemftH6qmWRqxFR6FNxIwXSXB'
        b'F+E+7F5NpbHLp4eBzXGtpA5jzj0ptzRiA7o0G/Zi38SnYSOYqE5h5WepDJSvPk5Is3R1jifbl2thgxPsxV2ZjA5j5JUci66xcrVSDk5nXyQ1Lp3Ii2dr7AgPaoickorl'
        b'mwaQGp1rwCgLpIXq9Lh709AhO5DGK6cxfeAZPpEIZqATcCeYMdmOxX/wSq4ed+NMeAA+C2ai9fAIjR0AN6WRqT8rVAFmwefQLhbKXcOi7Dk97qHZsAO9BGajo8UshL0O'
        b'n4GbyCxLhxdxRdLhZtRLMwpNgbsRaXjGk+NAhgbjVxI6D55PRaSNmbOlIBO2+bB9egD2oOuoF1c9CzbFYOckjx3CA0+loV5c+ezsOpANuypph2T6CsB04Ev0FFVVSh+2'
        b'92bOfgL14gbloF74PKAKLBp5pa8j+CYkCgBRSZWpooAdFnjQ4IF6cTNzC9E1kKuEe2jcwAnh4E1PI8m4tMY1k83YA/fNGdSL257ngoclD11eTiP/KzgSbI44STJOTV7t'
        b'aMl4z1yCmHF/5DtGgXwh3Ezjvr3GGwyElJPxXntAEM0OYSK6mkfUsHPgcynYOcRmO+BuDwr9QkjUqo+qxllIuQEeRUZH3G8FQiUocEhjqzvGBcRykvGSVlK1N+gpSw0u'
        b'oYPooiPuSmWVGijRmWCWwndKsx1xRxYWoDZQ6IQ20Bz6kv1A1/Qa0obJfxfEsg2WrEOdjrgnVXgynMbuTnSDRs6KDwTGpU+S4hZ9kxhiIfCzqAt1O+KunAsPJIO5oUk0'
        b'7nVhCFjrsJXM/9JCUS2gU9d+ITrsiPtx3lINJoT2IBrzr1meYEb6E6TP/QWJqWzMRSvQBUfcifM1sAnMNyhozCkyBQgVXiPlp3bYcdjyGdjujScWRqDwykKwoB710Lhz'
        b'CxPBe5nvkskYP1Xuxs5n3ph4EDGBwP+SeF11AhuYsSYOSCN+TSZ5aXdUJpBxWJLcjkWM/bARd/kTaFcmeAKe9WMb3ACPLIaNuH8XKvB/MdpZ9c3333//7VIeqIpzo9zR'
        b'GQjZvIMLxoPo2vdI29zfmF0NtPMcD3D1abhvn/W4a2h+PZeTItpyagnfbeYK9Mwtvtd4Dy/JK9ytXjH/TNhqb5daeufDVxrvZawt/l4riIv76oNTD74wGOYZ3oy5997h'
        b'1bnKrYH5Z/Ka3ZaIkV4aK/909pM3Zids+yjipS1bPpq47v73vTW5i0uQT+SVhuYV0U32xg/H7P7Q/bnXJXNfUx19fdzpFr+B0MsX95v+/vzKVRdfPPWHKX+rSGut1w2+'
        b'tezFjr+Nyfxwqstraf7NGv+W8KSwt/ODT3U1GyIubNB/wWktF8/7cFz1awsvvjbpPVdVXucOl8CTs/L4G+d3XIjvWfL9u1/+9Yn4U8ufOLR0TNCW1558fUL+yaT7D3fE'
        b'j3npi2uRn7/03eWnXvrWfPDXfd2hMzlfZn8Z9tF+9dXKY8G7myb/o+2QY/TbX8mffLi72vsv1397YSHf55WKiYt8zuvrX19RE708IbzMo30td5x7xuTGWCz2ENkGnVqX'
        b'hEWXXKLU3RXtG89g1niKg86K0Wmq9hFjftBNsJEFGKUycocSioy8+fBsFtqBugOj0I4ceWZ0Bh+Ljle46FkJepZKNQHw6GQs1WzPyiBKI0ESB+1B53wmCh5QxfyR5dP0'
        b'8MxkdD09Vx5BFPRoFxe4oSYu7JHBZ3+B5DMEUgZdLGDLUFZMJCAd2ZqgSGsuh0Va6Vwr0oprJPjqjtizSWdkmia0Tmue1i8ONYlDB7z8bFAXxjM+LgRmzbnLJT5vP6PF'
        b'Jw3psPgiorosvtiEHosvadKVAtaXMuNmKevLzHlNx/qUc/vmP8F6FxX3qcuo9w4thU98tBTqo6VQHy2F+mgp1EdLoT5Syj3qo6VQH1sK9bKlEC8R7CS4HDvW7+NvHPIH'
        b'h3YUWP2R8q5Sqz9hfI/O6p887SZj9c9gZjOvDT1lM3lMX/5QZoXMPIYUb3lczJQwpAr0UUiqUHDXnvX7BhhLrf6QsR06qz86podzz+JPnnxzzBfE35Bx1wl4eDbMvMtx'
        b'cg54LyiiS9yl7Crt8n43KL55dlMKFmyNca2GO94BHX79wfGm4PieRHNw0hXsm2LynrKPT9oc2JXYGWTyjt3Hv+cMpAl3XUDAmI7Utswm+wFxoLHeJJZ1KXvcu+eZxYkD'
        b'flIs1krG4TpIvL95wAeSgPuAcQ647eV/l4u/H+opnItMcU+bBtA0hxlO3FccGexalZBcTIw/DLOpxtEGZcdbHQKEqcbxW6Jx5DKM288VPlsEIeCIo4L7b4E22aIBNkCb'
        b'+18E2qM2C0cLnnYWoL3CqXopE0vQWvRns/ItQFutdtRlcCLIQuvU6JtsEShv+MIXqEBZqcciZelsuE175oKepy8k/VWWS1Xu0J+o3LM7VwjrFHrhEff8HbLCnNgje0Xc'
        b'tDFNrW9JoP+b/m/e5OxxrhBWVKj7+G/8JW5zrCxuc/zNW73z62Nju2Jrnwfgj/+y/9XgEhlDNUVJqD08So7a5w8xRTm84CDjPZY5WXXhLGPyZRmTvk5nKKszYFmwWKep'
        b'0Og01WUaXZKVSc0ErEI8lYdpjai5WyY3zLjt6t6U2Fhv4VcDIjx3mwqahMbEDk6HmzHJJAr5UYFPMMjT46J+OgUmWZ2NthSYwmMY958j4pGEP4HyRop4/03KGyXicUdR'
        b'niCXQhZB5SpHHdHBnq6CRgDb4CV4lBLfcxMSQSWoLSZgKFGQAmZpX/3Hfo5+Fn7VcWkHS2XeLJXVKULyD/kopxpNkpNZ3Mjdr6GbIniUl+g6Vvxm+Th+xJsTXT48lvBs'
        b'rPQ3LF3dqhfuSnlZxqFLrRZ2w8s2S+3SQHl+HF1qx1fDVlYHUYL22KghijDI6pVxHx1L0sQhkvN+RPEwTHBTrQSXZCG4fFuCI1sseDHsSOwXR5jEEd1pPbxTGVc4p3Ix'
        b'+d0Wy7vKzeKEPqeEkTRW9rNobKrV2WpLY3m/iMZ+imqNr2L+f6rWBCyH+1uCC9lD9o71jJvS4mzZJr6YzceoF0hjPT9b7pfmzwaCcC7NJnbWruic8dFA6+5yH+hLcciH'
        b'JwREXSb9NaauVwj1rbfP9gmuC8yfuudl39eyxooKS0G35tXDnpl2CU/YM7fuMbfi7BI+1cXFfhjPXfBmyZyOqR3rtkdO94eHXxG9yetN8WrQ+6z7g493khkobzrlBaZg'
        b'mqQbBde94LFV9fBUdk40B/CyGHhhHNrGArhD6IQXho7wkhvaGZOXg3bkZsDTPOBVwBufhzb9DN2Yc7VmdV1xuUFTXK6u0+hmWOnyCQtdLuIBsddtv+iuwnMLuheY/SY0'
        b'CTF1GlcTVjfjXF53njl6yk3GHJ0yIJV1pXQ6N2UMeEk74lrWDXgH3BF7NWThpdvbv03bxeyvMnlFNvHwci/2GqEO45GSB+2rNOpyXIn6n6MtnmF1dgEbjdhCTMUBRCP2'
        b'c7YIWY2Y1b6K/AmsVFRNSJnHWhthYuaoBFRXbKcSJgosBM0dsUHICxxBrireCNLlpvAoQY8K/eEl234UQfNZgs7Tx2Oc8okrA0p0IfMrWNpNyOJhgp5f6zS9xGlNwCSg'
        b'5dWfBfpN+M0TH73YW7Yf80xPC88MTItIEyUE1r8qmuscMWnOrg3B+zyOj9k8zmjaYw8V/N/x3wj278y+Or1IYdeXPT47Ia3tzFcg5wPBBe+0K3u8N7Zld17WKsz830t+'
        b'az9hv9L+6BZuxVTjrv6D0vupA82/3XReXfHh+c0XMMM9zgVBJ92ROgzLPlTv2zpvKt2asQOoC27iwMOMCp5Np4Q/Ad3IJhZFaCM8zWdtihzQ81RkWgevOmehrdE46Y48'
        b'BmTVCNF2DtwMr6JjD6gxzY1ktAu/bIiRwyZ4CE+bHAbegFdQI80ZbSqFe1FjDjwNQFUZTsjMRkdnyBx/qrzzKEESHYhV/BmaUk5LNDYzKtc6ozZYZlQtnlF+rdHN0S2K'
        b'hrQBsWdrUnNSS3LDjI9dPd7zCjBWdJSavWTNvCZmwD+si2nLIYiYRjKuaJky4BfUiefZkWiTn6Jpxodevh+IAozlHRlmkYL4ytor2yr3L+2e2FN4apopMNksmnTfnu/t'
        b'0pCOIbvEvyHPZuLZk4mHZxtZSwcFZYa6moofXj/Y5lKlqGUCWmZgrtVps87A7/AMrMEzMOwLPAPDfi5kNgoiQJdjwkjIPKQaposKfwgyE6smkMj/XwEvo2yPPEfNwSB2'
        b'Dn6h/A3Ygydgj1eJ/WY3i5nRLpzfdADSv36qZNHNbAUbKNPZEy10bfXykuhvZlm0OHOnOZINm+nJ/iVOt2dYpvC//N3JHlBJAyiZfLeslg0MnO8PMF4o4SwqmbwqwNcS'
        b'GDoOIyQQ0ZVaootgZGzgKjcBcAJA2BJVEt0iVbKBi6URIB+XfmdZSeqrdmI2UDdhKliLY+ZOKHG3y81mA58LmwxWA7A6en5JPNIzbGBTzCRQB8D8BEmJ7rYuig28W+8D'
        b'sMAQu01TMvnP2hw2cGpgNJiPk3OLS8Zox8SzgYLZdLNqevm6EqeE8HVs4KQV08F63PUfrCjR3crMZQMXJBL2BbxfSi2pej9oChv4iqMzMe/ydlyIA0O1bODBMj+AEcj0'
        b'D3xL1h5aFc4GMpXjQRUu/ai8xH1KYRob6OCdDzrwd5i+JPNDrwlsYPYTGvAazjMxpWSWfu5ENrBwRQV4E4s1H4eUzDoqTGUDt+OJEY3zHAwrWTtYkcwGXhhPwYTwjXEl'
        b'TpJpltH8MG4NeIDllBb3Es/8J93ZwMqpCUSalAbzS+K/VFvyvOQ+hhi1zPfglnDeXuYAtJ/m+nP1Kkz3A2eUO1peyH0lVrTlYNJb6xT9OknPE1sjD2f2pl8TuDCpg/fS'
        b'f18gd9bWu60urrj2VmdoetIzv27/y/e/PhQa89nsT0pD6m4lwe1vZ85Lfvr4J4vtO/WLTaHP72Fy/+ZgcqhNOdxlv+m01nXyx2MLnvuuwsM7sOXVDbVz0JOKibMv5TVv'
        b'Fob9paNMV5o25YH0g6p9yknhB33DysfOPSG+6KB7kJSqeXeqpK59aVLI1VdfLKlRTlv/p9oPK1+B6Nk5s71TXvjueNGH7zRu/44XmPDW0g+7y5b/0/P3U7aapsuPnCjz'
        b'/qsuRPr5muXVooWDN5izVZdOpSx73YeXoJt674b3pAUrX7h51jPybEruP6OuHPrmj9GfSK6I/+D7hv3rntX6SSHXP9PeGnv9i7P/WLbt0/ffDdr16lvSVcUPXgr85OKn'
        b'1859X2i+/MUbLq8XvaWP+5v/Pyam/etvr373T7spFyJvb/vkG8fyP8+VawNl3AfEnBQdRSfgBQydhnBTxSorcioJfUAMDNFJtAW2Z0VHpKMdWQwQomfhbniKU4/D26iw'
        b'AE/DTYYonEEkA3h18wwM2rp2qcz9Fy4iP2WdcbeuM9Y/m+XGjSw3perqZcWVNVVaytLnWdecQovOrZYPJF5NdS0TG2bcFQAswK4zu4YOeIV2FGJM1ieKJBopDyO32ZEa'
        b'ATSpjcHNGqO6WduRYvIgJgJdbl1zuj163Lt9r3BMEckmag0gcmuaY3RrVhnnNC/oiDNJQk2iUBIsadI122OPm7hJ3eyJs/I16uimKElR0GxnjOvgtE3omNM1pnOeyS+6'
        b'x62n9LyXyXeiSTRxRKqG1AE396ZyY2HHnLYFJs+xXW4mz8gutckjxuQWw74sbV7S4da82OQ2Bj+7S5rD8ZerW1Nq46rbPmRdTOnQdaV2rjL7xDQLPrCGmH0imwT3hLjF'
        b'TYXGOKPaLJIOiDzbfDri9vvjtmK/7eNt3B5rNNYfb9SZRWNs/aT7vHCK+P0BJtFYNvVovzXFCrMo+J5gdPG2seKMpTjW48qzTf2YmiT4ktX+XpJtBNyr7mIWcXSkmN3D'
        b'BiQebfYdwfud8Jg1MRigiyXWt7fcw+44SXblbc0zprzjFEj8OVtztufdGRPZkGMMNTkFDYj9RsAI4SCvXqPW/ThyGFYWl9jSLiVU6py1ogcihS7gYyn0HviZoijF77YL'
        b'Ns/yfd8IrOqOReSsBNBxlIwOC52BQGlPDf04iVwlh2CIpYyOR85FKLm+wHrmQSegITybEDsawrcJEdIQgU2I/SI+lhS4iRylHcnZijJ0DkqhzlEFpjA6p1CAUYbDoF1K'
        b'eblOo9d/+jVpgcCmBUIr5FgNrMK09bwDRkDEnptDJRFq450otOAgQaGDDQ6ywzhIYIOD7EYgHkGKHcVBo0J/WBYZvU/Pz2U31K+i/eiMEvtWwbZgEDwf7mNN1/K/+par'
        b'34d9F6Z4L8970YUT56TXf/bXdYvGj50rEIz3TIaveD34nX2cNC6247v93xVvu3Lcfflzr+08mOR1+U6Dz+eu39wq44bOeOb4wLN7/7BhsWna8kOVK4o3ZPyq888rl4QF'
        b'Pvy7scHwm4Ndi9pU02YXzLlcFXG9wv/7py4cLCy79ccDPdz9341f1SKqzEmrEl/fUVk360Lz4lm3/pHwxe7Wr+6ec72b4jXe6yuZA2vAux1dYIY4PzxZISSMH75YRd/C'
        b'zWvG2Bj/TsSCxUUGnneYRyWaCa5wM2vEFgb3AtaITYgOU7HkKbgZPUePDNCMk9EmIXqRA7dq5FQsSYPPwlNRCnm6fIEn0T8d5cTCxsXsetWkjYaNcBc6Dk+jXVlyuAvu'
        b'sgOOnhz0LNquoOuVPTy9DDbm4fVoObyMdkTJ4EkecLXn1nHQRbbeuxaV0gjRsBtu5PKAQMjxgT3oOVrCE57ICBtjsMikyEA78+DzdXQz6RgXbZgDT9EMEmHTYhzFQ6aQ'
        b'ZebIyfGDRg66DPdN+I8lp/XrbSUnu+Lias2q4uJBV8uUUFgC6GJGZHwiQK22A34BTXbvi30GJH6tuc25HePfkUS+L/Y7VDfgF9ie1JbUMf9EUY97T+HlJ64U9IVON/ul'
        b'NM2wxk08kdyZfGTyO5LY98VB1kDy+J6Xv3FeR5nJK74n4Yqd2Wt6E29AGt7E2+M8EBCMvxwGgmX4y2UgKAx/OQ14+TU52vBBx0FuWZVeF0nawSvT1tUPCmtr9HVkD2xQ'
        b'oK/TaTR1g06G6mH18w+rOUjflNA/G1UHEX10Wuz8k0QhB7b+B7NKgx3DTGceAOL+DGZJWfFBgRyccUwaKWox1tntT2e3ChSA0X+YcVXKmNxuZlBYbDFjkjGDPL2mqoIY'
        b'ZgApO5zCyVXq5aXl6qmDIut4WkOcGct6sB50zTiXczKH9uQvqskSXBNcOr+YdLqM0elI/wzXQqcnDhZcgAsOvG8pU3LO96TvLy+zki3Tvtg6xD9WrqtNuYXnik4W/fJy'
        b'N7Pl2hWzBPVjpYpsejjx3OSTk0eXOqQmJWpNcoCD3Q/AS9b/p90Abq62Hr7E1Y/BAe5FG3rL9r0hgh2yqcNq1osO3CUCkJ3Jeena32UM3eleCjsKrNwNs7ap8AbmbqHo'
        b'qIxjM6UIAxlSeWr1NrtAgx5W2hwRTDkOAfsEPlcKgbe/cUZ7Zlum2Su8TxRuM+/5dAgeN5mpqtXmKMN64hAtkDszrHL/Si38eTiHUtJuvKIfdpRzZTwdseDUrSBOPXHW'
        b'0jrlkj+ZM56exeQABuaoDsXF7AFM7HcqLl5hUFdZ3rgWF1dodfq6Km21prqmuJhyGsy8dDW1Gl1dPeVoumXEqSLOcmtTBj2KcX+p67Rlxeq6Op221FCn0eP8nMnBDrVe'
        b'X6apqioulvHwLGEDbM95DG/QTR/icE9YHYKD9AQVfrsF3HUA05kZzED8+K+5rs7+9wBxxgCvIFPQRLNncsPs22I/k3+CWZzYMOM2DpVOMntNbki/7RFgCpxg9khqmHXH'
        b'2eNLDtc54j4XuHh+RXx09OhRv7Eu6KI+O0OWKVcIgEM82rkUr6twJ9o8glAdLd/3P8cDN9VtJIxUcnQ8H7AAzxTsuuJ/keXbmXzHchI5lucR/0ruRAEFoOEEfmIgZz2W'
        b'J8Iwjs9C0SHIyKeHcjG4VNophRM5GH6SZ3v87ECfhfTZET870Wd7+uyMn13oswN9dsXPIvrsSJ/d8LM7fXaiz2L8LKHPzvTZAz970mcXXEMHzBW8SL10rsOtVfJwqPdE'
        b'hrbACYNonxFQV0Tz8fUFi0RKP5wTV+c2oqdclf4TOcoInJqYXXOVAY+0252mD8T1CKL1ENNnKX4Ops+Skbnhfzv8L0zkYpenHDORq5SpSN3Yo4+kf11Uron2ypBHyvGg'
        b'+YbifMNovp7KsTqvJTzMsSIxOC+jK5zWB4/9GlcHyyN7YNmB7Ltpsew9yCOT6XFTJbfMzoaSXKwsbwvhuMKRB5gx97XH/JeLa8oMHdEkfYMBPKYLFwtXthsB74WBI8C7'
        b'SjiC/9qlCClXHhVqy5XVEzGzc8io1tZp1VXaNeQUdqVGqrY0VIshi7q6jBzjTq5V69TLpaTBydKZWhxLR6NmpKbkSmt0UrU0Xl5nqK3S4ET0RUWNbrm0psKBaCw0bPwI'
        b'EjlampqRJiNJIlLS0vJUuYXFuaqc1JkF+EVKblZxWt6MmTIFTVaIs6nC/AUnXaWtqpKWaqRlNdUrMWfSlJPT4qSYshodZuC1NdXl2uolNBWtkdpQV7Oc8Cd1VVW9QppS'
        b'zQZr9VK6LYvT4/pJV+I2l2PkoLA2j4xkMi2X+Kxn263dUVlTVa7RDUW2oB82vuUBt1GZJ0+IGz9empKdn54ijZc9kgutI5uTNKKmlhyDV1fJhjPF1bHkiH2Pr8Hj0lnB'
        b'CJvW+vTT07Oggk3N+n9C2hGcckhgHVrSnXLp8WsdvAbJwckd0Qpi3po1DzVk0cPkQUVCeJgHr0nQNqoVjVi1E/gzA1L72JLqc3nuwECUArANPeNOt23yUQMRoWLQ1nxi'
        b'WApb85RsTqp0eCY9NycnIwfLbdvQYXv0PGoV0Sxbgu2AE5iexpGWRH+TMhEYogHZSNpQRuzjonBitDV7TrpCjAUoi/SEdstgN1Cm2KFW1ISMrPH1arIhLIpmQEl0au0y'
        b'VofrUkK2jiNW8KeXVL1Z7Mge9sXi4UZ0wDZz1JCdaYDX0HZc2ZiCdLQtWwBmo2MCdB52O7HGyEfhevi8PqliBTnntws3oQR2ajPufMPoCZDTLg1aV5BSvSlW5O/kd1P0'
        b'uwMni/SfcTNVH/XFzIC/6T6RfmZ32mtnPps9+P3K4PMvJ53Jm/R+2+0Fvzl3yzXp9npDgDrpYMW/VsvuFYGa/idvznjuvtuK8be8L/1L8NXUSYd6yv565Yad4Mxf95V/'
        b'51Gpfcf3wMvdEQ1Rb7UXnlEE/OWb6J3lnqEGcUjSuIp/2n0Q4+vQ9qfd7rMmTOo+EhC37uRLu6PfOfp03qfp1+4vfF/+8etLzu3fMely2eC4vj/d2Lrk86JQpVt8dnXA'
        b'wd/LOysGrju9YK6H8/8wePPqlzU3P5L1HvTc+N5bp/naZ0tTFPs/bTv27HOBJyd/WFD7zvfGD9oj95dOf+bZ5zxvvf7l85P/UL9zWaPLa7tuCBcknr7zrcydPSDSBXcs'
        b'c8SdLMsxyCPRtrnBMRzgAZ/lCcfBJiobJ8MTqK0wf9jK0mpjmQWffSAlHX8cNcVmKWDnwsyc6Ay4A+2i5/6BL7zIq9bC3VQ+r0AHYE/UtGS5jdXRFh49Y4ZOzR+ThXam'
        b'56CdGDfgxHDDKpLeA23moivwpIpuW4agTaXDB1nqZlttSGTw9ANKMjcWA0wwOIMoRK4SwNkdRGdIljFZuGE7WQPN2fC8Hdw1D75AmwZPrUKXMFGdz8qTk/sHCFE5zuHg'
        b'yLvlVOmwDB1GV2EjaptsbRQf7WPQ1RAxqxVYX4h2wEbYkcym5aL9DNwJLwZQVB3Kw6U3OniiXew85aOrHAb1LqMqg3p4Dl6kmBs2i2NsVQ5oN9rxYCyOMilvCmwshHvw'
        b'Wxm9AYLtXDazKNjLR8+gwytpPVGHEj4LG/WwHWeYzeCKtDOwCe6AN2jnL431gY1r0a48RQ6p5PMM3B+J9tHxRxegUYRbuCsHjwexdSV2sC5LuMnwedhClTKek1fhemaX'
        b'GCwYzyWNO8seZ0wGBW6B2xQkdfQygDs6V57OAy6wiztj9ZMy1/+m9p4cbxjSdNjqOzA81+JlF4NmkQVXKKwhVP4oZlj5o8geeId0JJq9Ipp473v5vecb2lFk9k3skyTe'
        b'FnsStb5R1zL1Q9/QvrBUs29anyTtfbFvm75jwv61XSvMQbHvkTeTzL6T+ySTBzx9m7i3xUQVrupK7MjuF8eZxHF3vPyMKc2rWp9ufrrfK8LkFTEQFNofFGsKiu2R9KjP'
        b'e10JvbLihXBzUGob705oRJu9kWcsG/Dya13TvKZlbRNvwMu/3yvc5BXexesq6/eKN3nF0zKTzb6T+iST3hd7DvgGtMvaZPujmtMGPHxai5uLOwr7PSJNHpFdhv6Y2fgz'
        b'4BvULm+Td/HMvvKmNKvKxT8If9lbnyzqmLGRTbx3RCED/lL60vIlDSUvb0vDByR+tyVBHTyzJIx8C80SGfkWmCXh9+35we4k2l0nEBzWxNvrbCPJubGS3A7i7CTO4ySf'
        b'f6/mfnT0yUiX2KhzbNTfR4hzFDtBRCIk1ljfrwdfP4klwmlfA+yQHfRpP1etc1SQCC46Tvtlap0lrFqHX0xA3g+oF4aJ1arNmT+s4TAWtj+x7wnaqw/DCofAIYERGHhZ'
        b'cUSETqMul9dUV9XLFLg4bnlN2X9SXV5xqbbsh5QhXdhZOKKCC/YtYCsYSiqIoeiP1u8/60eCIX+sZkU4UNdNnmiNon4cd/7nFSMaJF0t9v9YpdQjumvxvsVs5RS2IPeX'
        b'1i/2R+pXwBkdZtV6cTC3VLOaGjonf6z+5WQ6uQzVv21xf0DM7wJibLr4x4D1/14TdFeBhZn8WO2XjK59wu8CWGvPhzE/Bdr/b7dg+b9pwdLRLYj7XUAc2wL5vxcv/htE'
        b'3s3Quv5YNZeTuXcZWOdebCGVXXGdbNX0UgvRSavotWU/WLf/W2VqpYyzptQhjcixeqn2Ee6l12iW06vUsLBMxVsHcp2aRSZXYhkZt3KmQVcjzVfXL9dU1+mlKbhVCocI'
        b'3FTcYBxx5XhFvCJWNlK4G7KHtNn4K5Qx9OYK1FsMb0RRCMWDu8dOZ+BJtF6r/cf4z7n6ZPzeI/ALVptL9Li7L3l7p3pvNMZp1n+2PmdBz7YL6m2CBEHCgvhnYz+WnkKl'
        b'+x24S3yB4xrBXzfky3gs1Ns9ZhzFarZIDR6AL87wRdseEIWxNBA1jkDiVhgOG9ApDMUbp7Cw96wLPGK53Qtw4fE59HIvdKyemnagBse6LAKHcYINgFPExKCd835Qk2xH'
        b'VMaaWvWgq3VFtARQ9Eb2aMh+VaUjMe2e0jzFJI4YCJX1hyaaQhN7Ci8vOL/gJu/XwpeFr9X1hSb2hRY2zdiTQ1DVuuZ1faLQX6Rjfp04b2Cn1lbHvNjxZ+6lb2RnDkFB'
        b'P8G6mxjiMZjU/3esu5dgUp/noNTUsXopQ1Wddrm6zrJKGvQWNQ69jrBOp67Wq22uFSytdyBpkqm2LrkkB4fhpPhLvUSjK3lEeTF6P8JiZBucRnQSn0wGsSXVMjs1MJCR'
        b'xdLDS1iGGaWUyIMH4fUfUUpg2tO+VvcSR0/Mll2EO9irF/aEvn1TBDt45W3xv10Zvz5FoRSGxE8zmpY6cNPGTOCmJRbyIgStORontYP6rQ2/OZpQe5wB114V/r3jTRmH'
        b'moQHZcMjQ6Iw3AuvoG1WYRj2YDmW3KKIuqoKyVavVSSDW+1GSWVPwo4fOU5jY3ak19QVWweDwpxBH+ssGPWKzodxlvmwlswHkzjktt/YjjqzX3TTjNtevsbElvqO+Jan'
        b'3guM6JPNMgfO7vOeTYH+LVGIrbU4OxN2/sB0+AEz8beJ04edNYyNmfgKPCu8iZm49390ccLPhIQuI3vmx9anLQSGkbuhyDLaHxD7u4BYmyX0p04EBWZf5NpCHbkXYYSB'
        b'+5AlRxUYNi/ZC6hZLdGbD5vW/nfN2zfjGf358Iyu0WmXaKvVdbjy2vIfggTVmlWWhSlOEScbVkaXactZhSVtt/WkDc5IIS3QrDBodZZuKce+sjppuaZUW6en+lfCH3CO'
        b'+prlVlCrxeu7ukpfQxOwWbE9WaHR6Ye1s4YytsS01AyMFLQrDCQ9BmMRBBVIddZScd4ZdWqCExz+zeEUYa6ByH5w/ZPwYFYu2m65KDBXPiddkZlDrN23xhSghuw56Vy4'
        b'EV0ukMHuDGlRqU73lLbIHqQucV0OL2kMcTiLGmgkixt4ylaxOZQFgBfIpV+NaC+zAl0SznNAvVT56Iy2V6NeJ0xtaP3TqAvAQ9PQFsN0/Eb4NDqodzHMTSe3W6pQQ/Rc'
        b'1EDs62F3YXo0LqCQqF0ystE2BrO3o7LV8LlQdLyQA9BeeNkp396d3pc5wbfeqgydmE2qVDuUY/48+Vw7kP+0AB4VwA3agP7FPP1uMqdyjL1lBwlflLyC+SInNHa9YE/u'
        b'hxUlDRVbtgoS9sWnzu/eHpydctr4kBz8Ugo3ufcJOj6tml8Y1zm4G9pdfEZc7agUtijyvXYvfjNDXdKqU++r4Hi80ijzfNPJ7Hh5g9+vBJ7lvfcebpq42e0T1+z7+Yvf'
        b'9IXbPy7teFs/oP4i+M3pgXbbW9+62SYAT/p51vFWyOzZ8wXrw/0wz7fqmhyr4T54gIP2g4oHhDEkrc1zjEQ7yJ2nl+AZzFWpWhLz4SDYyyP3UKDnqE7LHT0Dd0fJ58LN'
        b'wxrFdAOrlTqNtqG2rGFlNHASSaVcjyh0mjUIOgx7UaeN0pNweXd4mDB63yep7m4dPEZIyE9iATkswtk4h6oN5y1DFx65U2flAimvCHXBJqoym1eshY2w1cNWGReGelnw'
        b'dAN1ZOG3F+F2G3WcN7r2704crX9k4Rie88Xa8pELx4hXdOE4blk4SpyAxKt5GoFIa1vXvhcY2Rc11xw4r8973pB6qSmNnFVS9oRejj4f3e83zeQ3ja4oaTfLTLIMc2Bm'
        b'n3fmgNgTZ+IX1D6xbWK/X4zJL6aH1+83zuQ3jkbNNQfm9XnnjchS1hXS76cw+SlojOk3E0xDa5RFQ0W+9trb2kWyK9UQ5/3h5YqaRY5Yrz4gzp+ws9W6XpFDFXlODONP'
        b'zCL9f665QKsgHJxwjP9lKqEKq44Fs9ofW606iTTVA6zSVBwVs4f58Y/Jev+hqCejtTP8qAbo6MjaTXosA09TpT26VfeYesq4g7zlOk3FoECvXVKtKR+0x0uLQafDklQZ'
        b'z6Z2TtYmEJuMqfbWzV66wAqHtvwZlTO9Z4mjckl0siy3vEKbLd1qfuCIxVTFH7Gw8lL4dLkdFWq73KrJ7vXwisve3c2CYbrY2YqPw2sraSS71FnjDh1gHd4zpF3AxqJR'
        b'cPeRMDURnhXSNHU1kULVlnelS/EiTFdfsl2MF0hlXtL42Di6UUw2ecuJYgALqEPZD/VssnRWlXqJdFWlxrLtjCtM6jwcw1pJa/bVNbgpyToNrki1Plma8qgUUGKpjuLf'
        b'SbkOufQ+Xrz0dqITI9fnp/WowbIYqNJxYIFltWXi3WELbEG9Wag3E4Shoy5oH1zvZphM8jk4yy5LIY/MxPx9jk3yoYzTM1URlgsPMXK/imUHdCzACXUthluoONLomU4v'
        b'g/MpK4m8NCMTGMaTXI/51owSRtrtsDyCZRF5Zo7SVhRpVNqjG3AXvEElGW+4Hdddig7SaHQTKgPXZXsUWeyHcQQWraMzsxUZ8kgBQI0ypxUG+IyBcDbYileXyyM2U0mD'
        b'SNEReA1Bu4KnZUXL5Jl8sAadsMfyxkt+Mi69GRttK5qKGuWZeLFszeEC3lQGnkLn0UF6LzZqXAnPRdEMskpqcshBjDbOk+gE2kkvJsfL66nZUZk5bE9OQsYoBojDuWh/'
        b'fJ32hQVcRn8KR/Lgzu/9M5GvfF5Zb5/YUUdFqYTsRKNpjxvM1PA+K3v5SN6ODcyL26TjDy8vS72wQ7U1eLPzq64Vz+/jqH5rP++3G4/uk2/2WXBdNXHL0rmht6KnX1oU'
        b'/N7x7MqzH4CHGwJC7ZT7f8NX/WZz51zQ9VxUg5+55rhT7fVFwdtTrl1RldwT++2O8pk+lTP48q7fbxbtLFk5pcJ4SPSWv4vR4fMVnfBmGwMkqdMbgrKOL8IAg6wQC9Eu'
        b'2JFFl154EV3jlDJx6fAa3Wpc6D7dAi5gOzo5ClwkylkT5ufggYphiJKzGoMUDFDsHSl+Gf8UbMvKyInEebSh3TitEDZy4Aa4p5CCA3/UsM4GWmTCS1YZMi6JPfpyIAfe'
        b'wBlH5WdYTmaiZ1PZC4xbFsH1yFhCNjDpWWRBFWcMapJQ0FKw2Iceuclj7+IsQJui8WjFcDFObIddtGaTx9fQnTxLvUvRWXYn7/wkmdN/tPtG2PDorTdHAjUsHGNQbIs/'
        b'LIEUedwBLPIodSYqnKTWpPd8x/aF55t95/RJ5pBT+pNbJ3fMOJHdmd0fOgF/6Osss292nyTbZmvuPZutOZyqbRKVe83iaPpittk3vU+STjblKjrK+sWRJnHk7YDIrvHm'
        b'gPimWWxwZb84xiSOGQgIaV/YtnD/4qZZA2If1iJxf7ZZHEEzmm72TemTpJAtMH/pQGBof6DCFKgwB8YOBEfes+PJ3O8DXrCYbn85AG//1rXNa/tGSNeuLGb5K3E+J87f'
        b'wC/Z8hre9Ry56WVBN98Sh/x+wwnrrtc/MbrJcmaYKLLrFUVE8qifC3HaBTHgnGPyLzdmlhFjZsvY/xiQeG2k0jiYLHx4WaHL4NA6aaslljmwSvNzxPmYONRa81PinAB0'
        b'F9iiNdT9i4RdJI6ZDAePWHF2c3Jx3WbJvHXkALduM3GeIQ4xISMW8+U1ZcXF7Fbis8CyfznILdWW/eAm5qCddSOFqguJdmTQeYRWgkWgw9j1W5rK0jpdA6C7pf8rJ93c'
        b'HpmtNnSz3eoQMKM3kr3xLeAej+Ms+kIIXDzaEjr5nWXdod36vqCEPt/EFxJe5972Dejmnk+7x2VcJt5JmDCQPPVrbqJz2JcAO/f5OPAuD/vuVWE27H9bFD4gmXSPz5FM'
        b'aZhxTwDEfrdFYwckyThEPLkhDYdY4qSQOGkMjeQVdFsUOSCZQa7sncU0zLbEihkZy1t6W5QwIJmJg7xnMw3pOMgz8LYobkCShoM8ZzINs4bzmkXySsd5fSUUOod9IaFN'
        b'6+AZo0zOY7/i2DtHEUPW8LvEd08CAsJui2L74tPYrAJwVjlsb4g7Q3CCrzkeztK7ADuWVNh3L9rattmkbRkMbZwlaA4JUuIgNpeQTn134nlh39iJLxeanDO/5gQ6h34F'
        b'sEOyy2Lukud7U61Vn0CqPrFxNmtgSxfxBvECfXYuK80ywKEQ7l/DQTvhsYpRF6CTv/vxmO1OdR9tYavk6vhKnk4QizmVkq8T4n97pUDnoLTTYTlf5+QDFvCpJajQYoHL'
        b'UCtQkdJ+IkcZh0G2o0qUyFU6PGL56bzIZchy1nkiR+dKn13wsyt9FtFnEX52o8/EftVlkbvlyJUdtdJ0VbklCpXutpavQ/mLSfyhuomU4on0uBlN65bIV0oem0qyyIVY'
        b'3w7bp5Kf7UjkKD2p/a0nbgljscX1Unr7Ap03sbvV+RBLW52vJa4ffe+n9Mdh/sSyVhdALGl1gSoBTh1E3wapAPZLqV+qDMZvg2nIGBoyhtjJ6kIs+YXSsFBlGA4Ls4SN'
        b'pWFjLU/h9Cnc8hRBnyIsTzL6JKO5R1J/JPVHUX8U9UdTf7TKHvvl1C9XCbFfQf0KZTw96kaO6sVYjurFKGN1sUv4WEJNGBSkLKdmum8SM901DoQrsyGspS77g0JY4iA/'
        b'hrBEpyaiBis3lNUPGZTqsOiTosMRl2vqtGVSYv+uZvcSylgxBgcQSQWnZdWJVfXSmmpWFrHKEjLOoKB4pbrKoBm0L7aWMMidqSrIfTi5sq6uNjkmZtWqVQpNWalCY9DV'
        b'1KrxVwyxo9fHkOeK1VjGGvbJy9XaqnrF6uVV5B6ztOz8QW66atYgN2NGwSA3M3/BIDerYN4gVzV7/qxuziCfLVhoLXeEtnfINnMqsWInYii51Iv+lWOM9PjFkd3LUQ39'
        b'AJSSSV6F43uQLcsC7uj4VpodytkF41a+9a2So+LIsYA1/PNSRK+sYqzP1YySq2KITKIOxSUwSp6ST8tnCmytqK25cYdqJSBFWJ/kmJvIcYDcmeSYx8f52LF+sgU7XJoK'
        b'VA2J67g1jmDU35DIDaqGjmUuEWK4YL/mH6MMpi3kNtpemg4KKyGr2Tg0xEahzI5WMjVRVubJE+PjJthSZzkWpDMqiEAr1ddqyrQVWk15NBVztXVECMao1WoKTXO2qjBY'
        b'yh86nEFTJJPH5JJyTYUar/hDFFqCJWttWSXJTcu2C9O2JV9MuwqHT8lgP/TQVtMN5eHahYfpwwcZxSAT+ylBzJ9+j/8echWxsbkyu0HRo8WQHVN1VW2letBhLqnpTJ2u'
        b'RjfI19dWaet0Qjwug3xDLZ5lOnuGXGrFwlExQVwSZjRWIGNic/UkxUCDruw4DBnSvU/AQitgL96X4KV4ICikPyjRFJTYlE4g+uqWKR0pZnFY1/x++RSTfEq/fJpJPo3i'
        b'6clXVpuG0Lm3n3Hmfocm/oDY0xjWMnlA4mNUdqR0c7tmnsvqzrrCNUdPvlJgip5ujkgxhaaYAlJNktTmmXdwNFVzbtPM24FhHZr91Rh8Ow4Ey04Edgaag+OaeHtd/tND'
        b'aLTbfshSy9oZVkOtL0cY9izct9BmP8mWNikF1ddqpCWYUsowLqxSzGC/S0oUulO/tMasKpEd3B+A2KEE1o2oZdE+9sDcQz9qTvb4+TGiOhxrdXJ/pDo/xr0KeKPfRQ6d'
        b'NeRSihwUqvXF9LTDoFCzuramWlP9g+fxSKO+I3ToyzaqvH1p29L+wDhTYJw5MKE/cLIJfwLYE3oPy6gJmGF5qUZHhsHS/9LaKnUZsT9R10mrNGp9nTReppCq9Bo600sN'
        b'2qo6ubYaj5cOj2I5lrrwxFWXLzXgiCTCyFxGdtfQwkDvuRIO/WoYGPrVMIehs+XMiI3A/9SKhWgmiQGcg6qWCBYsH9WsLqtUVy/RSHU0qFRNdjZrWOMVHEstrdXVrNQS'
        b'Q5XSehLoQExZajV4hU7DQ6DDjUxVVy+j23v6uhos5lAuWf1YjmjhhtYii2mRJaRfDZQDsvyVMN6hbT3cr+RAiQNd9TFQqKwZRgPRUr0Ws35LMhKN2A/ZHkOx1tmSMJn8'
        b'CmJyiQWAlJA1w0ZhWVpTQ34hSVphq/k00K4qf6SbKG9fpdHhabwSIwZ1KTFksuhA/83pfZdc9ifKnoHH4M4oeXpGNDEOyJpHFIZoZzr25qkiMqMDUW8GXruXuwvRDX90'
        b'zEDsCQLFCYkzYSPqQZfmRGTKFWRzMCoXXkKHC+ToOAckzuYvQVuL2F/Vu4wOuuoVOZlo7yqBO3CFN+xhK1eRuMygIG+3wE3onK0OMSJXHpklL7Bmm8UH5SI97BLCF+1X'
        b'UtFiEjyDLusj0NZIeJk1UYe7GFyVfYXsTwLuXj1NCXegPSq0A+1VEf1hHtqewKCL6GrxLKp+hOdxkzfSOp1Dz/ABFxoZuH55KvvjhZdhC3xGn87qF7PgWQV6iQfccJ3h'
        b'6Ux0gP15pg3oEs4gIhNtf4psB/LXMehM4spC7ba5oTw94RJVCYfWzcnJ4saJDlZdCLp96UyBaMaeJ3hP/rU7UCKpKfoq/vWbG8M7vyzU3bsTc+/75O790tCVMRnvX2v7'
        b'+v3PleX37juv3MjZ/XbDbxsUN3PnHHf6/eFMU98zhuPjD7217LPtFSk9ssMnizi/qt/5jwHNmvJyofsptz/E31/uPjGydiVcmZR1oilW82mbqu/XvSH/4zgJffu94fd/'
        b'X9iwanJeW+6+we5xV3bzisoLxr18z7+o/elen78FXH1jfNY/Ln95znh97NbWtkWqkvx/3eXffevT7L+8czfj1sHZWdeS3720/n/4HX9uccjVHdS5Kr8tfvhwavW7ywbE'
        b'X8nujf2b/ZMPW1Z81uL84uxZz39+/i//cv76YeyJaQEBXQv7gqa9GxWlifqzzI3dSd2PnoOb6RXVqFEGr9kBnpyBZ6bBS+zpBmM8fD5KjrahrTHpaAcXOBXDXbO4Angd'
        b'dtNtSnhmRgJsjCE/pPcMvMEAXgwDexP1VInqAI/D3VGZOdleKvwimIEHoRF1UTUl2od2wEtZGTmwGV2MzLEDAh4HU/Ramk6xGh3IolUKQ/twSi8GHl5bQK3L4HH0HDoz'
        b'YZx1e/dR7atOwO7edqENhVEKWWSE5ccyXdGFwuXcetiaxl5AdxYegkeowh+1WzSoi2vZmh1FVwLZrOHVxfhdLgN7psE2ekwF7kTrY6LKiYY0I1oBt8aQeYopTirloefD'
        b'4ZUH5Hc9DegiPJU1PG3hjpjM6Az5NHhOACLRNT7aGILaqT7WAffIObalRNW/lVzpcDiinIP2E+M5tqbPw23wJdSETmflyRnAWcmkpKMXqIqZtxRet1ySgU6m4YlFL8k4'
        b'DK8/IEe9lqI9sD0rJysrR4G2RmfBHXm4pvDCMj6IhDv58Bxuyks0m8CZ6AZqzIVnouFFdFEAeDMYeB2dhBdkov+6Wok4I+5OGlIEe7AMtXjkGjDob0FOj31LdcOp7OGM'
        b'u4Ui4ObV6tjs2Oc/7h3R+AHPgNaa5pqOshOVnZVmz5h+z0STZ6LZc3wTd0Dk2erU7NQXEN+T9o4o6banjzGkpRKHe/m2rm5e3eFo9oq2HPAY2xc+zew7vU8yfcA/tN9f'
        b'bvKXd5X3TOhefuUJs396v3+OyT/H7J/XZD8QEn5iYufEI5OauO+IpAPefv3ekSbvSIxTfQKbBAO+/k12A/7S9uy27C7Pd/1jm2Zg+NuRZQqKxejXb0xHYpdd5xSzXxwO'
        b'9/JvrW+u7/A2e0V2lZu94geCw4yCgbGRxojmPOs9GUnvSqLvOYOAuLsuQBLQwe2Xxpuk8WZx/IAsvintHclYclJj1m1paIfqxBOdTxxZ9K40vil9wCvolpdiwD/YmIcz'
        b'3Se4ZweCE+4KgXdgk+35C0fdUvBL1M3sfRmPnq0gw6Mjv1fwvXUPnVwt9KQrw7iR6zJ+zl3eOvJLdhjbERlkhDnk0F4hNaDiD/14IJ/eDgps7gflFAr+iyaRlRg3zSW4'
        b'KY0FDpYTuyyAJ8APr/sEKwxhZAt8IlhKb5EOHazbpo/grUfQlfSx6EpBFSyPpFQT9DEC7FixSg0BRWQPuJ7AMocydVklayC1XLO8RldPt6ArDDoW3+jZ34weJRyPRP82'
        b'1u91at0SLKlaY47Y9K0e2vVl57N109cKCAms0+httUE/wVqL7sKOj3YiFxJG1Mq00a85PMWeB10dSW9ojMhfW75ofI6aDTxZ9nzVYXAXE870Fd7pH6vYA5/d6AY8IcrV'
        b'OztzAIN2AnRGVmOYTZeIydE2TFxVjK5i+DW0v2yFI4XEdmoehkZkx5jYYrGGWHhNWBMoSs5Rau0yL3L1n+EMx5XmGprPO8BY0ZaY8/1zG2c6bvvdzFdePrZp0yYPXnFw'
        b'zvTayDG5K7+c+WDd9S0DLy9zOBb29Uff7XpR+Q2zIxM8+dXfv5uxI7lgt/gjfsdxfcDyT1RMuG9f57Z//n2W98DV7x++u6/wTW1I4Z9W7fH5w7jnfL/rzpz/96oX9uj3'
        b'Rv+x8I9zXM/vezjlHfWrp37V4MRdZpxf8fGE04MPD/T73Z72UWRE8YdTVlybX5P3h5vNz8+LAWd/8/edS8pmpq+7sviPv9LcylNnjX0+pO7TiceOZGV+v7tpgcm3Z5x3'
        b't+5Q3zQm4HPNhMaXfZ0++j53fOzatcw78yOOvLxV5sKupC+lEOuqiHR5Grxq/aHVG3APa8J0CF6vywqrHepIHnCdy60qXUeXUAwv1oeNXkIt6+duA9oIjeNYS/Fd62aJ'
        b'ULvlDlt6f61yDTUCWxjPeXT5Y9c+vJhexOvfMXSUzeFwBZc1I8MwAD1fDtvhJQVFEQq0Jz7Keqsz6kXdPOAIL3DQKe8JtIG1sGUMe8kte8FtD+yFN9CxIpqtYMGSKAv4'
        b'wBCiDh2GPRMn0A1k2AiPwKO2GCIVHhmGEc5zH8hxrCnwKtxD5IB81E0ObeaN6A0OugC3McUxQpzRRtTB9vcu3C2Ho+i+sQiu5wPBUk5gKHyO2iUvRBdzrFvK8Bq8GGlj'
        b'l4zBEoUjcDvG/9uj0FkmOgdLAJZfaXSFLVwdOs6X2f+8td4e2FwtZTHUt0hYgy6WZd3yTBfysZaFvNwN+Ie2T22bavaLIrdc+xnr2te1rTOLowf8gpqyBrz9+72jTN5R'
        b'eG31DGytaq5qqW7ivu/lP/Siq+xcZXflqaVm76QB/6D2rLas/TldKWZ/eU/I5YjzEVcKeuVkLc5oy9if1RXaHznJhD/+k66Umf1TBiTe/RKFSaJ4RxKLM2x3aKO6Ji9y'
        b'bqBjplkssxwM6Jpp9oqjVmjz+xYW9y+sNOGPrNIcqO3z1uIltiv0nLxbbgpNMvknNc0kjTCYyQ+qBHUYMLqwJiwzycrMgeV93uUkSURnnsk/Acf2Dmh3aXPpqDuxpnNN'
        b'zxSzd0oT/7ZXgFHTMd/spegTKWxvD2Z1c1Qt9xOu/mNvDh5x918hSUquO43g2Bhl57gxjP8XP9PITfdn8ENXGxnBD6uAVI8960TVz95E1T2suMYxBaNjDimcBUS7peT8'
        b'vPj2m2Xc3IecMO1DXpgivkLGo5056FRcXVNsUdfoB7nqUj1VN41WLQ2KiofMpiw7Dl5W3ecjLzJJD5NjOOvBHQtJzegPHWcKHWcWj8PEfTSko/zE0s6lR2JMfnF9krg7'
        b'fsFH07p45xy6HY7kmfwS+iTs6bMR+wlDd5IT7dZUzl7AauoLueMsnWrdA1A/TXT5PzAAjwklOwzqBT80PEO5+tNc+aNjPD7X4T2GvOiFQ7sJSkbFmcy4kJ2Jx6ai77iP'
        b'rz19x0uwG97NwPGEo+NV43CqO+TnrvEcgmTLtXo8RGWVFPys4SZLw9fYhVOtVfggEy7js9Qg1i6vrdKWaeuKWY6l19ZU05kzaF9YX8vqz1n6YM8IDfIp8hsUsptX+OVI'
        b'O1zp0FGhQZfiWh0xOtAUs0k8rMQzIngOIR1iNIA5JDFF0XTM7RdHmzBPxPLCU81PdUnOBXQHmL3GYzLq90vAn4FQ2Ymczpye0Mvy83Jz6PS2mR+Nifp9zIQrkhsB1wJe'
        b'47/t8qbLXS4jn8/cB0zIAuYuYAIWMHf8gwnDxEzIy7/JabRSfEhvlY+dqRhmK5lCZsy/GeuhkX0MHbEjm8Cnamle7hoh2/yI8DW88Gg8GJxwmY5c1CXjsJxu6PCXdPjw'
        b'Pu4oHb2t0LrlwAYs4lhUvd9sALdj4nsSLyefTz779E3er51fce7zyu0T5Y5u4NDpIzJPSfN+Ds9K5AzxFE7uQzvCT6Rherb+oxmHHbm4i1TcZaji9LmYM6SiJj/iMONE'
        b'ZmdmD++y83nnvpCpJq+pfaKpbL0feyRsFrBwWmZU9chWHmNlC9XM49ugYpI5loMynNxB5v8x9yYAUV1n+/idlXUAWWSHYROGZQABURSVVdYBGXBXQDZRBJwBcY1rFMUF'
        b'd1ATQY3ijuK+xZyTNmmatkMmLUjS1vRr035tkmIW06RN8j/vuXc2FtGYfr+/y5177nbes7/nnOd93kln+CrIILZ2c4UAhslsIXBJERcWVgF/gkSfEgguJI984ccmRD84'
        b'p3RGaV1iyaDK8ha0pXQ7yzR2sv9uioINpcKfFK+qHiktZaZpIcHyodMSTZQMQ1oKWBrnp6TlCsN10nQLNJ8/qJOeMFzHOXTnF5dGNEWe/m1XmKMOlwtDXYX3/YeNkb1L'
        b't1vYSiw05NkAizRDh0byr2yZSf5BcDFUanAeO6gD8/Q5Nqd1TkfMpYlnJnZ7jvua9EOJvF6fgNOe7Z6dATfkl+XdPlNJT+WUxHs0Uj7rt5zA6vkAM4sXN4thQnR7XqzK'
        b'9JRyrzYtdwjW8rmVDVLu7t7vOQdp7IL+u3V1s1HrmzxiVa0wbXYQhEdUy3gcNO6/Jud5bi8R2tTkkdtUhWneQrABBF2uF3TIbhhwczDOjDzK6G37TLqqocYL2NAxGS/Y'
        b'C6v5HMU7VFFn90FEk0PnZBUn4IvkJcz3qvnQJ8ySDrXpqfsC3W2GehFyRmDolamKYtI0HXimTVOXdjLiFJeWmow4NPwSdG5j2ZQP0VOz8yDS6mBBk85ETs9vn691jtLY'
        b'RQ3OGX3RAf/Q8PliVGzcfvSOp9UgGOZZ2Y2GeXphEwhP8YoMNUnas4ZM1Ebqh3+SUrN85lLbTEstTNX0HCWlrl9oqhtAeAs0mV1Dtm19vgdx+R48cs7Tnr15pHxnJTHK'
        b'd3oBHNhSl48k3109W0TAWgSz2zCNXdhTch5IT546TRGzjtV1Mg6b+6Jnzv1yChfos1HU1KUTPb4MyBbKSo3ajmioEhlSWyflsrS+yqRcaHgXZAZgdAcObx+6yzSOsv+T'
        b'JkRUzFdGKkpWeKOipBf2Q63a9/QR49RI5ebDvFhrsnpqaVs9Z1sLZ9vas5esVWFhnaq+rLRyOckge30G6a8d4nNIlkEKjIe0xyO82yO8U9Sp1npMJHMnd+9jca1xHaJu'
        b'9zCNY9gjDymMJB1O3R7y5pSH7j5tAXSy5h6rcYz9f5nj/KfmOP852hfoAOHPneXWRK2uqqlRsXnuoM9zw8Vj0KxGyvQ6rcckQ6Y7dbvLNY5yXaYHkGf+f5Xp4qdmuvg5'
        b'FYGA581zM0pAbdqBQfg0dAGnhuwC9HP+v+vyhqJF84WD8ibo2fJmrn79qmBIjFcBz5DOZ3+2nvzW+kG5kbwbatmPe44+EfG0J6L5OgVcTGohyR4yZFNtq9NU5RIbcr1P'
        b'1LCopqoMbFCXFldWl5YZr/hwAEl9GVgWFrLfJcUwSl8MukuXoM4DscvT6vwKrcfU5pQPSbX2Px3cHtxRpnUHHsI/B4Z1lF5afGbxzQBt4FTwK5Py0MO3LQYWo7Ue4+F8'
        b'wqWlZ5aSFkNmVB6T+xme0+SnMNInMiNp38HD1GWjmmqYPg6nk1OHExUmlZKGb0Kf68ZlBRk0646tal3VsqQj+lL8mXit8wSN3YQXEj5WNKLwi55F+NoatYnwNHwHWtTN'
        b'IWc3+haVZyTiXP0TwwjF098dqWeg6Mg5ppX1KeIXLzQVn4bvQzX00Of90RK2ph2p6ai7tPbMWq1zvMYu/qeauNHZ+ZYRxKysrjMRk4bf4HPWSlRMt5ZoGAT2rdPYjfm/'
        b'k82CDlnFLIGo0SAGV940mVR6AC9j6xztMMsI+nrRxnC2AaTfjCNvF1sxRvVDyTdF7isFSiGrEIcZiV49zIrrkGv1/Hyxvn8WjNxDUjVLpADjOeZbX4p1rayukNbWNLBo'
        b'2cgIFiZfX1tbAxTh3/Ij5H28SNKPeutqZZ/5svri6rrKVWVs/WQphfrMyJcqKuvUfYKyFbUDxjIDrZDUCG8O2U8lMMl+7spbRgpEr4Nby/R9EymmPF3rlqFxzHg4GhhY'
        b'SzqmtS/t9orWjo5pFnCqOjcHTur01LpMGVplJ/UBINQU+X2Gqt9ukJDIoSwEVTweK6m6qqYOXDB4QthmANrJpqy8vKykrnI567SUKEhVxeq6Qha/0ScsrFdVqWZDlMBI'
        b'a2RrqG/lfeb6LSsrCrhgAa4sCofu9EEtYgezcjgARaCqBg51cFgBh9VwWAeHTXDYCgeYm6v2wOEgHFrhAJMNVRscKKvDGThcgEMXHK7D4TYc7sHhARwwHH4FB2q7+N92'
        b'1TfIgJHb8jTjcQewUlKv5LEWjGKhxK7fknGNaEx/5O2vsfbo9fRuVPR6+pCDu3djVq/D9MbkXvcUcuYbqLH2/pPEsTWl3a+9QuMuv+XQLYn/mu8gGdvPkANY5U3uh+Dj'
        b'YMbJ86FdEGsX6JTCa0zhDBFDeh0jwRAxitohwpVJ/Xze6FzeY5HAJQ+sEy0ZG+deicvX/ACJ1xcMHMhnXeHg3C8kwccKHjntI2KUdEt8wSYwvJ8hB3jCj3sMrk0lj41+'
        b'zBdKoqnvjX44e2JtIfH8ajRPksP7XMyTTPlczJcEf27Ol4Q8MRdKQj635klkhmtfmfMkQV+JBZLozy15JKg7kz8hmRYND4c8EYsl45/YGQ5mkslf2fMkcV+JucNkOATC'
        b'Qfa1WCSJ/pIhB4OJYqoXOqrGO/BO1kTR3IWfho7Wo9dR+yDgNPz54kMeYL0GmyhSyixBgTBaCN7jFptzbjuEboxSpBTr3XaYkbA5DZsbufEQ6912sMaIYr3bDtaNh1jv'
        b'toN14yHWu+1g3XiI9W47WDceELYxcuMhpsaNEHYmYRcaZt1zuJKwGw2PomF3EvagYdb9hicJe9Ew637Dm4SlNOxIwz4k7EvDrBsNPxL2p+HRNBxAwmNo2JmGA0k4iIZd'
        b'aFhGwsE07ErDISQcSsNuNBxGwnIadqfhcBKOoGEPGo4k4bE07EnDUSQcTcNeNBxDwuNomDV3jOXMHceDuaNyAjn6KuPA0FE5UeVfMYkojfF9tkCQkm/gUKvsJr15cS4p'
        b'eEsd1ZjRXc4XCLkFoH9qYVBSXA3D0MIyzhysrpLi4HR2AtQZhc5QDEwFWMBaWaklB7ozNQ+A1UYjRrciGOiKWRKX0pqSelhV0n/NskalQ+5V1rFbwOzjOhxcUkJ2fjL3'
        b'VpGxtVp6OWe3UCxdSDemyWssjNCYTS6U/bROds4wsk5VBgm0LFZTG0uImFogLCdvF1dVSethYlK1EoZqE2o6SxM1CcZ9gAx9sVwADtdBC9HP8MzZuRy0wnzzLN7weslc'
        b'veYxNDZAr6UIlEyBoEo/y6MhoUlIZBISm4TMTELmJiELk5DOtpkxhoCS61YmT1mbhCQmIRt9SEBCtib37ExCo0xC9iYhB5OQo0nIySQ02iTkbBJyMQm5moTcTELuJiEP'
        b'k5CnScjLJOStDwlJSKoP8UjIx+RJX12ogJ83jRn0R5fXDkxaHTdLTykQ5qUPflIp0tUKvd2qGK4WCOkGiTBHNsx74oHvFTvQ95i8jMFPA+KgQAjHKEG1cG627vqs6IHr'
        b'GdRqNkcfixmRw8Rqdu50w7sFohiuDkuZ7OXgrErK5FuQ6YUgT5/nhj/5ZoPiImFnwK4I6JTDXKH6OYnn2xi2IxvU1T29Y6Mbnal9vMI+fmHhtwED315UDMZUBvsraj0q'
        b'k/VZ54Hp9lLOHFTMQnRZP2QC4IcTFdaX1amAAJzlaemzZR0e6+moKJEGy7BB6TMowwZl3QAijT6bAXxzZoUsVpp8sbZeRSbNZSQKquqaUcBUXXGfuHCpuoJGvQSovkSF'
        b'ZewPJf6S6F4rpO4dzQpLFgGOmPrlK66rVxN9W1UGaJ3iKqDSry6vIRLTDK0sryyhNuVExWY7ff3t4qV1hgT1ORZW1ZQUVw1gWDUnMQHaWU3ko500+Qz9Zd0w9nkUDshy'
        b'MlklnTH3rIicL1X3WRIhVXVqsIinM4Y+M1IuUCZkiqsrGbYkzNRldXBDZslC86Gb6BMvaSAiqI2IWIeYLLG6MHR9BpsLgx/LPucBYur8fP4RZk2g1JNZ0x+c3Vvq2hJa'
        b'GzTyye95T6Y2EQu0boUax8IPnT0Be9RWonUObhYCOlO431zvJIL6gegNDAEnEf56RxJSE0cSOl8RJyxMPErofr39qItPqa+x+0/uopcvNeLlLpr+BMjgfV/do9wPeJrY'
        b'b6N7RieYfxD8+ujDoRHwK+Nke+TlR6PxD2Cf0j3tJzs9qX3Sqcl7MpuTYeV5SuuUjiiWxbDX27ctv3VVq7DX1fOYd6t3h2OPq/w9V3lvcNil0HOht4Ua7/gW4Ydg9aEj'
        b'MwzVhOVrZs7tDpur9ZqncZn3oaN7S3KH6HeO8se2jP/Yx3aMi2+b/+nQ9tBOcY9zbLdzrMYuVuMca3B++gKkfar/4Q1vuewysIboTJjtBSakuAZe+Un51MKheomBpS6U'
        b'pcWtq+Fo/sCis5ToPZXlK4mWY6SJvIBNM11khMX74Yx/+XzgIWOMvTyMMXWMAWYIS2vqDJyD1Enaizh4uDiCPC4gT6deHlM/GIPFAW9tP04auobVNYI07kPkjrEPjAHi'
        b'cC7Y/jvuL0AeL5DHQPEkG8LtxU8oEs2iN0YQycdUpA8SpKyjPXX9Qo7fhNI3gBycMRDnteCp8lKbGvZDFCcME5Fa8hpMKCjX+hB+EORSpeFaeWUZRMjNAsjXyQMG0yGD'
        b'W1BpMJd/waHktLKO/uq8WART1Gsw6xIi+AUy8b0RMjEIMvF9fSZGD2bRHqb+JyTOTAgnh5QXIilV/Xn4/o7KF2Iq3yQTBlXgsC5baMqlOlDOpLyU5PDklMT8F/BaQwT8'
        b'ywhyygXG/AzzDs9j5c2jtclI3eMM0nRcEgMsseTSZErGzdqNVTUUr1RzbKLS6rKKYliMfKFUfDxCKsaaNqlgXZPSWZUZJYTT9qRByhkz5/zIvOXYOv46glQxpn1hIB3U'
        b'amqWwNSZ5VAlM+ra2hrgMSJ6dz3LuvpC1fJvI4g0HkRy5OtEss3X88z8+Ki5MvrfEaKeCFEH8Ex64qWkjymuKDNqBrWLVqrB4lCam5CuIH1S1QsIdYan+vsIQk0eoogM'
        b'wlTVVJjKIg3KzEtJfbEW+Y8RREowFYn262XVpWF1NWHkx6AQSYNSfrwsnFedT0aQJdlUFs8h+YOlQdkvJgiR4NMRBJlmqikaPED5sMarZGJUDZQoXONmKaBzC/JyX0ys'
        b'z0YQK8O0OdnTXp7OHznWlx/fv5DSeTxC7NmmpRM8sM+G2SjYDsF5UGJOTma6Ylp+yqwfO6Jwvd7nI0iVC1IJ9Hnyz4FSmc6d5dJU0gtOKyNyVlONX61fuRzK/TDptmem'
        b'p+aDU+FQ6bQZSaHS3Lz07ARFTn5CqBTSlpkyWxZK7XBSoXIu4r453NeSc7JJ22Y/l5qQnZ41mz1XFiQaB/PzEhTKhKT89Bz6LImBrqY2VKrBFrq2qhicT7Bs1y/SNXwx'
        b'QtbOMG0F8vc8WTO+b32NBjx2KYJtAsW0wyhWk3x+kSL/5whyzTZtBuMGFjm7kiKXJhgYqdIVqTmk8JIV02AUhMr5QjnXP4KE80BCmX7wcc6nGhe7rEMqRSnUxpof2Vq5'
        b'oebrEUQoHDD+cRzolKmNFaDMsF5vPJ/90Uo0kebLEYRaaNpYPdl80XXsQD8ghU2GIQZiPczgOE+Pgh5CFP3S5OXhIClGlicunOXJUBCtYWylDG8D8eFwb1fz8vm+zCy7'
        b'oeAI5I0hDP10C7EFTJXxk5aDn9RL7z7cE0PnTJXo6ffzJIOvkSdtBl/VLSZLn1odvp2Yx1IpwLaOXn9npxuGzaOhpyNymbnqT1B1+XAY4FWVrs1St0xCqG0CI9erdOUQ'
        b'clKPSbeqKKvTL/26D1wYMrpZRl5Tr2Xo8iGY7Kw9tBbWyMa3ju9xj+9wvOR6xrUz+Uba5TRNUHyPe8YDx7dc33BtTn7oH9KRfEN2WXYz//V5t+Zp/TP0ntjIByJjbnhe'
        b'9mwRHpO0St53kfc6uhzK3pPd4xjV7RjVmdwTndodnfq+47QBjtuGboBQlQ4wFTyKXM1nzYIGtzQAPgxeANNZi9RAh059qoDZwVPARvOY4Vu7vgLaDYec1O2eGCMhw43h'
        b'SYtYh5DfgLBCWGUewtLQnFt/LhwqOewdFZQZZ9/m4Nzj4E/+UVvS0G73UC2F1H7o7N6SuG9Fs+1Tcjb/WRI7eth2M0Q/4a8rJ7ohokupiFa0oY0qq8qqSUqHWNumNxog'
        b'odJhEtrjPrbbfazGcWyvswuL8ZECStmweM82JdpsYHpO107p8KECtkR26wM6btUTOIAOSpUudicEJp10DsHukzyCM1AU6VRHBaSQVKun0zF2AwWWKugMmmrZVMmg4yUd'
        b'1lUfwQF2VujcUSELGBZ5RJf7KVaoz2bAlg1t7LRvMHQLAh7XI/RJTHdsxNyGjRmnratS4JNibrNGxO7VCOlWjRB2aiiHfZ+1yTaNmNulEdIdF5sB+zFWxtsxYm4fx9yw'
        b'jcNuodiYbtOoJvO59qpKgbN0OFCI0TP7Q1L18rgDgAzU3/I4UJCFxO7r0XKJRz9DDo9LeYzXGMoYnvdYxPfK5zUqDITkk4BqfPLTScuNnuHIuqcAWXcCy1lOL/XzhU7h'
        b'j0Vi5whyzYZlFu91zABa8SxeYzZ5jLsEInjms5eAx1zWz+c5TXgsEoyOa0x9bK6LYCpEkGggRSdSxIMUU6gU9MVexwAgQA+k/OccXgnkckpg8UqDX+OujIMr442vRMGV'
        b'GHrFw58ysAMbuceExixDZEEQWTCNjHsLZHRMZFnaaQb38wVO03mPRSKvPMhja8bd76Ed6fTHkwfd4xozDR/Lgo8pWOp2DlcVBriqcIqrGiIxXAGCoF4xjYqvWHp3nsTj'
        b'c7FAIv3KUiBxZVFJYHyD9+JX8Umr5ZJaa1kG3hGiyJIDqQveLWCCF4lq8DHUuRxtHuS/Ev58ARz5AOI0RSi5kZY1j4I23fTduEpMrwiNrpjRKyKjK+ZKMXnXooAfzQP0'
        b'0mJzlaXSnFyxAkLuaD4gmMg1a3qfEqyrJIBiUtkorVW2FRIyUNj0OQzoFLMq1XWVa4nEJh6T+LrefDztzWfZGfSoWdIqfb8/K6JK31+Hg7alH6AqOCVWSHu2PovC0noO'
        b'0WgB1gbFVZV1K/t8B26SgjCFxggbtc5UDsaFPnP9R8x139AZzUmNiIc9hviqnoV4PXT+rmzn7+mz37LXR7bfhj2MCTI4ufzxO1De/OH30oaUTLeftgW0+QaGGQIt/pwL'
        b'H0XDi6CqIPe2QkyrXigmbuZWPEJMjcPHpNeO5DSmZ8W+G/SdZOjiFw4tAIwBw9YDqu1sF+htF0GrSWbtKrTOERq7iJ8SN06EozIOgxynA9UgVZqTlGorO0FQAAnp4O3s'
        b'lrHWOVxjF/4sGm7FiBruMBnFarnNUISJukmmCfGM3s4CPFY+zWSq1BQkxjMhahnKDGrIKkAJ72WUx2DoOeYQ80P6ji30WkPNEynBDchmgIAZAdjIF60Hv5NnO/iawRBT'
        b'Cj0f5RMKM15DWQr0zwsNbN6BA3I80PTx0poyluyYJaahLhN0LIFU/SEzuiIe1y1SDUwFVgQqgBCx+Hqoc0RXq60tqy7VMdJYGUXBPjqsjZiguLR0kP5MqwW5sQ9qJMBQ'
        b'aI30aQvpWNfjPKXbecqHbn4af6XWLV/jmN/r4NXj4Nft4NdWd3pl+0qtQ0Sv+5ge95Bu9xDOfMR9Uq+73+m17eQsmiLy87VuBRrHgl47xx47v247vx674G674I6Jv7WL'
        b'fUqLBIycoUUO6CZM+B4Gtb00yCTXoVJJ5xZHIZ0SxtDy9q3U2EkHi2JCPmnakzkwM3hqfjiJ1oFJc2GYmlFD2mMMUZ1z+dluLIZMza82svNV89kr5XqjZoG6fqlKQRso'
        b'T5/YPl6dieWvqK6mjijPQyaW3joGiQXiPegP3S4na90nXEnuWHYsrTXtmOKo4nJyt/sErXOcxi7um/fcJ9Bhd7t3hLlM2GdjOmLT0Yedz8DooJDZDTknMZgu0DpsqL4G'
        b'9Z1q84AWpAWlWqNX6QUDFXmoDHo1fgGfO4BWowawIFHjPxcLJTKiRDp6dHtEaR2iG5MfOnt3SydqnSc1phmdfi7kSSIBoR4BoHiPJ2IzyXgAsfvAtYmsVghjgKc30umE'
        b'M/BOY7UQd+FtoXIek4wvmGUtw7dNNEMdoPMLsDuY7DZQMyR/BfSvUC5SCQGtrjRTmistlJZKK3CMo7QhZ7ZKO+Uopb3cRiUq4BeIiN7nQHU9cQE4gDcHNzgF9gWu0Was'
        b'UxuiR5qz6HO9HmlBr4x2Y5TOSheKbzfX489dKL7dXI8/d6H4dnM9/tyF4tvN9fhzF4pvN9fjz10ovt1cjz+HsB0rV7QAMOhEolH0fkQEM2+UAYibzBvHU40iT9rrHdrY'
        b'k9TxOHc2DvScdWbj6MVQV0ICyvAq1nvwlBTYkNTb0fQ7FDgWOBWMLnAucIl2Yt3eLOapnFyZ2WbUBdBoZfAEnnIsxEfySsA6vTFySDRa/6S5Mox9UucCx+gpZ2W4yqUi'
        b'hIyxUX3W0LZ0gO7KEwJohLl9vByZqI8/LbGPn57Sx09Rkt/8Pn5SWp8gcZqiT5CcmdknmJaY2ydIV5KztDxySEpL7RMocshZbhZ5JC+HHJQpcGNOpkoCA7ZgWnou0eX5'
        b'idP6+MmZKuC/IN8l307L6+NnpffxFTl9/NysPn4e+VWmqLbSB5LmkAcKiDDpg6wlKdgbuvTJfL3zceDOZchcQqh3PS7+aV2PKwZNmmgvqud3FSrqAbyLd6CT+BQ0tjq8'
        b'LUeOd2aDv06Dl07qG1OeTukqs0LTs6en+TSQJpgBtJ/ojJCZjDfaoqv4LO6qjD+3XaiOJd8MWffPrhJwR+mIHuHmt3/1wO5XbzOiN3acyl0eXBLtkOUXGt14gCfYHPFG'
        b'/tmI2usMY39b1GDfLxNQJk18Mg1vt0JnQtN01OOj8G2BO7qFLuAruJNlNz3Ft8VNOXh7RjY+WCkHbu4j/BXe+DVKqh4pwxtQE9qNd49alhmGdqPdZozVaD7eugodIlOe'
        b'oRYrhGwfZwzedDSucTrkJvT6anAYR90lejKOzi2h7zmMoWNzjtYtV+OYa4za1JGksCOlmQFeqgK65qEYJan5HedO0CCM6jUS8RWBkZfkYk8ezxtcCHo/rwvBg+IxzCmr'
        b'SEGJscpmo6sfMARMNtM58V0gXCBaIF5gRiqsJamwQtINiArMSNfAdgZi6uXLLtqGq8Tm+VZGldiCVGJzo0psYVJdzRMsaCUedHX4Sqz34KGvxN6KengZXxSWZ1L3a7xq'
        b'1t1sWJgcHMxS56xQlQpyG9DmNNQhYPCuWivcLMQnqJdafCoKHc3UeW6bnkbaQJgdPjGDIxzOIKPPNrw7c2YQ3jbTnDQSIUPq4SUrCdqBb1JziPFTxcy85bA7U2S9ynsd'
        b'o3OYcChdLZHgbUt0rMdoPWqlL7zsb8F8Yj8GCjlr0Uo/dsDD280TTTzLysOC7SyMGJDNmNlKs5X4TCT16LAuKTUzPTsztHYM3injMVYKPj6Fz+Ez9bDAbIE3oQMhacCU'
        b'jPdF4Y34eEQE2lyUyfiiawJ0H99HnfUR5LmYEHQvRAGUtzuzC4xYloPkYUG4MTwYHcdHwY1ujcycNG50jk1ZEz5gnYmb0rPCxYikkhE7821kFrR+s84mto3HL4dAloeJ'
        b'0YEJjBjd5o8LwHdYR7iXcpJC2OLA13PNGPNlfEt8D79aDwshsWgbblWyQqDj6K5eENLpBFEf7rlBenHNGHQU7bOciV9bUA9VIhtvxjuURIogdAk1k+OWsVTexfgQuqFe'
        b'TjqO5lghw0OtwOJ7VlWfQO4Vl+ODJD07Q+V4F3gCqSWP5QeREm8KDc0uSPMjd3fl6AipDc798EmBNd6NGtFV1gHHvem4bdF8nSd7vD0rTMw4TBPgV0RoE3Xh62uFz3MZ'
        b'HYHvZxcQxTOTjw7iy7irPpTcT0GteLMSvH/gJnQm3yjZJOqZ6HY4mQjn2JnV4hu4td6R1hYxOor3gXXEKnRTzGTX4L3UmQfaOjOc5AhRki43LMdX0bYGfKVOzEjc+SSK'
        b'beasG+PLkyeryWVSxbOiQ2cEZYSFkizIoJGF5xlymKQC7cM3LRm3VfS9ReiV+BDIHJJZTeF4tzIoiHTPjeEKkkGQTbkz8V7cBDWVVPUzFsw4dKMe/CSgjgnxVvg6vqrG'
        b'N5ahnQ0q62X4OurCNxnGOUqANpNe/dV6yo68Kz8ZX5mKm0gbyA6TkxwXMfbogABdJE930rbT7i9iiuaQLJhaFOoTOI+huRExG19XLxMBPzM6G8eg7cn4aOUWp3E8Nazu'
        b'n8jYdCA/U4ki7P5w1XGOV+X0qSLHrfu81rw7fl5y/IrP/zR+X1XOq0e7H2+c9+6W7wK+L4w9EPqm4/4F74U//P0/P5imCnydOVLywDxkH7P9n3+u2NAjftA1i9EsvPKv'
        b'dQ4uZ+zu1vADvh/1b7OQ7y0+OMovOnv2pegD/1r95tyvG2L+1sk//NU6/97jO+x/efrEP3IW/n3vuuNzftCEef6+IOvXaX/cvuoXB3ePOXVx3hTmQ8s7/97L9zhyvnTb'
        b'7w5b3L26VrLjwq6/LvnkxoVEm3miWynJlV1HmuadP5O08b0LSfJ3Fv7v7epZki+YqN8+WVr1sylj31W1H9lSmrGsMM6mxKrL3Schc//PDi9IOTc/907AJ63XHlVbN22v'
        b'X/NBjLrv+yjseXFGy9Z3o745EVW856Pej/rml/6ue/61v67+uL1s7IyZB14b+/tfbjpT7Ol0/t/uV9R3bn59p8lFLXYU/c9f718L+/L2H/7tcucP3xa1/8/RNR/8XdNT'
        b'vPrCrv90ZXdt+N/QrtU5MZ8+mme3OHzPZ9OmeE1cbhuVOMk7raH45w65b/49ruOtg+5qaeZn9r+/+MXeHdd/s3f1tJrauIlF+YFv3nsQ3M5b4mXn9vnsrMYCrfuN1t1O'
        b'C9yir/wNtZXsyjvhfLX9s+/SQv75YduKv2ZU3P+y2ubTD3sPuLz15EvPvV/XFJ4vXRD2H5kfpROvWySqwPsHaQ7owrLYL6GllpMuchtp3GhXuAKdQ5vC0oBv/BIfv1aF'
        b'L9An0L5i3MqxeLutCzPi8HZFVym3OD4chy6gpgYbiaUKH0FN+JoaX6+TiBnHZQIluoaus5Tnh3OjMnPC0BW8n3Upgk/gu9SdSyDetRZvjMJNWRl4h4AR4Ps8dETOo/Lj'
        b'18MmE/GI6iVD60nTouJd5OMT7gvo/Wx0uRI12S7H12vxtXoSp5UzuoP38RfNTqSuTNBRF3yL8sHzJ8o4Ovi97jRhuA2fQzeIHhcaLMtOkdPelGFcpMIF6IIH6wdlF27F'
        b'rZnybHTAQ8zwV/Im4Ut4K5U50vsl1LqANPztpIciQgsn8NDlNeVsSjvy8OZM0ulloU7y2gJeOL5s+SX0aui4Y7Z6ufWyenzDFm1HO2zNJZa403Y56QLw9YZlRPxsYYBU'
        b'jG4tQXspvboMn8SHQ8LwzqxIXiluY8Szefi8M+76Ehq5AG1wwk1p6MKKZQzDX8tLRRejqceYye7ZiCiCTeh8WrZaQoaQ3fKMbAHjhq4JG/AxvJFNfiM6roTHdpGxHG2d'
        b'T7KfaIRT+fgg6hTQz9ijrWgDUMbTzoeMptfYDmh0lpCM4qiLZkQ6bp2FyOBEKphIivYy4iK+Lz7NVj58mERObkL/WagmPaiIscrh4wOkGKm7mHr/hfB5UvlyQKMgHRwZ'
        b'59EmfEXMELVViLtEeBsr62trRnNPhiugitqgDnQarxckz8asy5qFa9ER6hJoZxbPLIcRp/OdK9BRqjvXLSPDexP9vCI1MisH7cS7s3iMGz4qXIb3+FEW+un4FCQ1xzCi'
        b'2SjJB88LstExdJuVYRc6R4aPphx5GN5W4J6TKSA1cTsfn8b38XXWrdE2fJfkalNORmg6ydX1RE8zH89fiNfHs/4Fzjeg13R3USPJ+HAnfxJXehifCQ4SEfX8FilY2ut3'
        b'1BWTBxWhaFs4N6AklolIntwQiRLX0USRSv4yPrAIv0oF0rszsEcXBbgpMvNL0ABtpgZA0yCzGPFowzyGlMjucNN9pRAyrO30s0THFuJbX8rp+I0OkcJnXx7wKjqDG128'
        b'smRiJosxQ1fQNjv2ldfxFVc6EO4GN/DobhEp9GxwKRSeSZKwi92/moYum6Hdsgm038iapWArByLP70db2RfEzGjSBbxO4jrzXydrMHYJZEzWQDd1nAbMddjdHDrZecCn'
        b'k53HVZ5gJBXYEdvjHNXtHEVnPJzTyEfOXkBO2OMc1O3MumhP1bpN0zhO+9jZm7qhDO/2Du/xjur2juqcdiPrctYD+wc+mujkB2Va76znck/5sbNnr3dgR0y3d0SPl6Kz'
        b'9MbSy0sfpHePU/R4lWjySpqnAdvt/Nb5PZ7ybk95R8OlNWfW3Ey8OV0TPuWBs9YzvTn1kavnMc9Wzx7X4G5X8D3vOrZZ/AdnT9ax/INx3Trmkl7vACBD6gjsHKv1Htds'
        b'zVHj7lvTLOx1cG5Z3lbRuk7rIP+9m79WOVM7u1ATUKR1K9Y4Fj9ycO1x8O928G8r6HEI6XYIIUnOvJFJI8jQumVqHDMfefgCd1rbaq1HVLPFHxw82pxPe7R7dCzsWKbx'
        b'ibzpqvVJJN/9ICCkI//S7DOzO1f+NiyhX8AbkwRU4u7JQCXuRI5k0PFuCyVCdDbcWH1jNY0h+cHy7oBsrZtC46j42MGrbeL747K0fllc8iZ2Byi0bjkax5xHDj5t87QO'
        b'keQjQaHgB+HEmp7A2O7A2J7A+O7AeG3glObk3zr6PwoMaU5+n/x6B1ATP9+gDvdu3xhybqs3F2Tv6Az3OLNElnT4yDz6iF/g6bj2uNOT2yf3+MV2+8Vq/SbAw9JeaSB9'
        b'mPsEZwo4JpA1TvQPZ79o5EaU20akposQu/VD3zFt9T2BU7oDp/QEFj+Y9lbWG1k9yXO7k+dq5hVpk4u1vgubhQdsjebgozgaHB3OSgg7BipgW1eBSX2fVUlxnd5aVqwu'
        b'WVS2tOxZ3T8YtThoWkXcH327MzQ41bskrhswnwcSrR9I+/p6CZnQ5/C+ZuD4OT0+x8SeOp54TRzDXLNKYAQv4LQUbHtpmofbZDXtKXS7q/8yQbn+aDyt6r2n7Hi+T+59'
        b'a4qmDQJMpp4bghVcyrkPkAapyopLw2qqq1bKXsDukcWb91kVcvYYhZWlTxPwO1MYcth7nixX67ehQ9l0VKoN0huL+yLI+D89BdYKEsKKpJE9kFc+NeYAUw69fdWLSsJu'
        b'X4O9eH1dTXn506QRCE0KNJxaCdTXhZHXpGAqbzA3AQmp2etPklGq8SPUNDEIZoAkB1NIcmU5h0FeCghyUnpl1UAAUvrTyESyzLrQqPt5mngWIF6kPt+oqQfApCvAz5je'
        b'jusnyamgESqUNYhiwI8HDu++2FQg47j0e90LGZ3TdsoxJOAWFpl8Iz9y1TwvIrLRwiLPZAmRSeDRhcVBV59ndVysGJrzsAjk41HfwcCyo/MWLPhpvQV/+51lqrEzXFPE'
        b'sVqqXlRTX1UKW96ks6N+0qXFFcWAU7as44h7pElVZcVgdSFNpqQVUC84T7nUbIpzf85ZHVSqLTkv6EVF+ar6MjJoVbINL3hJTXVdDelZS5YES6sqF6qKyYfABkXnf9cS'
        b'DCnqBnUi5BEdtJH1gcfasaw0Mg+xNHHrXlSUWlylJjEP8Eynr6v6shEoKs/d2SakLjyCv/qwq6Sr4eg7dsjuzfUW+S7joxiZhG8n3iPj0YmdPBQd1WvenNaN9/qyivdC'
        b'dJfUbDtdzea254XlFWV1ff4mA526pKqQZgIZ8iCd6slyeIpqyPA+bAdUSRkPKTAVaByNV/05jJWp+kA3HIp00G/VP6Elg+s8O3JdHc1QL45fzZfyePbPu7y/R+zDtFuF'
        b'Coam311E2xfnwVFEF/B5+j0ofr7wJ/TeWP5Me1Dx5HwKuF4zTKdOqdhygkX4bVnBGaHobD67NA0XcrJgURqdQ9usJpBZ5P7KXb9LEFE16nRrCLvtdP4NhrdtrLW1z44E'
        b'6xbmlO/LRzb4HHYd4/buonfMiwNrXhu7JSKIl73xcVKLqqXo7Huu4+cyVevN3G1sZAJ2fncKb1ltJFDn1OHndx5rqd/cSXjH3AZ0ZDi3uRb4MK2NCnSezL4HVEdSFxX4'
        b'KqmOlSueZXeK1E/1M9VPNVc/g9j6+UQlZVw8yawkIJ78+9ArWBOSofXK1LhkPhwT3BFzYklz8oEck90qWm8dnqb7crtVBrJI1ddQk/9FDm5CI3dny0hNdoXdKtfncXcG'
        b'uxkyPt05EKA2dDYzEx9A7eCmV2jLQ6fxYXSZrgDPckcnM0Pm4+0KuBXFQ13Tsisnn90noC3pnf+4d5W8+o70Lbt3SpHLu0E/a/7ZHrPSrWO3XmmJMIva8M2OUTveeHdV'
        b'VvDdcuujlczRD8Wa3hVsDowAbjamyNTnf9/oocuFlgRH99orNP9qjtR8VMjXjoJRY/vNGZ+AbgPtpS7uYfPcNG7VN5Dj35KDra7vgOnEXJLjFs+T2RuZ4Xh+6ZjMp2Oe'
        b'kIx6/P/KqLdo5N6C9Pvj/r5ApIb29mR6RFfJYdLW2960Qy6k589y9blqKaiwYrI+W1HO77P7C+n/ofah3bjdcejVHXZhCN92GLQ2hDfj3TK+UZbzaQM0whQO3BymYEJa'
        b'xs5sATye6sO4uA+BJ9QV7xCDgqF4jbZ/KVjne+DGMBoanqx7zqHhKcVbxPzXVZqKgYU7eFAXKvIr/3Fwk1ANq8o+oY1dJUffaf7126023/syZgd4F/55RQeyHDBcsyDL'
        b'gQtYLLqSFogFWyD9qaRAPJ5zXKYgKR6piv7G43KKz3Nm/mP+/8PMHzQOD/b1S1pW0cMlfAps+DTYAfKeQjZ8rBOyrN+odZE2OinfdUxN+upsRO0pAXMgXhD+cjwZLOmO'
        b'8LVl42BTZSc6Bau7wqk8dA3dWvjlOGh81+zw2ac1Pl3LW1qhb3vlfhThMQZtkrKuVsPEDD5mY47v8NEetGPtEDWA4pEHLWFSIDKtAVK2BnyZBTVAB0bu8RjX7TFO6zHe'
        b'iOf82SsGxdGZkYoRaFwxMn9UxTDGYXjoyuYkVAynIXEYAMayoTSsOjiWuMCBgrX0oKwC1wK3ArMCdzKJYgo8CjwLvKI99BgNyf8tRmOSgo7gxfgMepVDDnijJgocQJvR'
        b'MRY6QNf5bzPuVqqSfHwNX7OFrWK6eW2HTvLxbUvUXA/ded0EfJnuXqeRqpGDzg+3ge0wlt3CxltWWKFrPHRHJqb+qEvxTRs1vh6JATWJmxm0wxe3UyXiJXRrCu6qH5ck'
        b'JjeOMWgPPu5ez26r4XP5Vvg6UTlfhV3mawxqT1pI36nFe/ENdR3PmQd7TAzagvYF0xuTYvys1OgyVBp8iUEtZEA5RG+g7ah9hrpBGsgH2xcI7qmiW9tR5WLGmmSf0qfI'
        b'emZAFkOjxidWZ8Fmvr0VfOgEgw6iVnyMBWKcskcnSUrQZdSmS4oTaqkH/FUDOowO01xiM6cCb9TnD+6sU+GryrQQ2M1jd/mbUYvFWvSKYz20O/wKXo/PReHmqAj8WoSQ'
        b'4ZG8IFcOiOvD4e71UQ4mOBUdofD03Jn4QFSG0owpwC1ifCIMX5uJD9ZDW0E73GyjGHQBdzJMJBM5KZa92oheXYn3CcxDwbglXLmq6l8//PDDJaEIalDaw6yiqlfGBTL1'
        b'yQzdvWtfm6mPCTemhcLUYGd4RkEQ3kZEUAbhG2Qmh3fPTEvPBvU8G7ZQr+dB6sTVkvkC3FI/lXxo7Aw1gNqMn4J6RLqgbeE5JH+8cOtA5+NQhc6hO9b4ylrcVD+ffCQh'
        b'JVNC3tgjQesjzEV4fQF+VYx35UtS7d3MJ+WhO+gefhVfSqlYYVHuvMwS3xU3mKPtFjnWqBNvwieX20fge6tl3rhxohwfFqNDSTLUNTkat7qglhJSE5WQNYfx+TwR3oA3'
        b'SJhIcwHqLEBX5pASQNvwVnQgGG3G9/ButCvfvfIl1IHXu6N7i33d0Q10OwrtQC+j6+Wr8WZBZBARY6c3vpzskO0Up4IqRuuZJNGdF81nautdiuarfGoZWmGmzsAHcFM2'
        b'Op+LG9NJysPxtlwKndJDPMgMTTHOKjubzr0u4htWJTXodfrB8Og0pplhgq6VFgVbeZcy9cAGjw+KFkAKWi0YqTU5mbFgCdpL5j63cTsvEm3Er02MIiWxrwhdw+fx4YJA'
        b'fGIOEXe9k2hxPtpYhhorcBu+abYI3bVbiU7WUBlt8Guo2UjIGXF6MdPCMkT2ToBHRGdk5B9pVvicBakTl/C2fBmvHjbg0FZ8HpyJN+H9DmT4wbvSQ0lHQYrX2VwYQSZ8'
        b'19nuxQnfzgzLyFam0clfOoCoQqCy7Uibaqjzu9JCM7Lk6WHBpHJsl1lXovWr6mEIIEXc4miMkSGzvEODcTIGjAzav4SIB91lQd0MgAjxGD7axctQJOFbK+rBh2AqaZ1X'
        b'Q9JI1u3IZit/eEZ6WB6LaTPFawFeKDyTzJVroeXn5oXN4DMr821Xok7PejAbRhtI/7Q7E++ytyXtKH06B3Hj5tppWTk0sfLp5svx9elpGdmK0DAFBdBBW9NjpGifjHfk'
        b'jUKvocv2tAZcHs8HnaLoa+ui0MTQKqKj0R4qCB8wy5RbzQojI3+mgDHHnXzUqKish72W2eg+PqjMkWWzfuMLZg6B2IM95rNoPSnWvXjHPCnpfm+ik2k+6HV5SppPFLok'
        b'ZPAVvMGe9IhHzephToCvknJsI/1ll62FOXqVCHzFFnfVLavnMY5qQU4pOsgi1M7i02iXEror20oB6eDOM4Az6KRYrHgntDlTFkZXHhREsKCBVonzpeb4qDfaiG7G0f5y'
        b'zUq1kug+d/D2fLyzgLQOUTCPNODtzuzYcWZprdVyGx6J5SCDNlaQvuQmvsOCuO5Z5OCmrMle5OZ42HHvxPfqYfjHZ/CF+QBJPESaBLdDbzWHjy9a4V00Y0PwoXwWQIJ2'
        b'1+owJLZB9bDLW+WJ2gGOQbEYVS+Fu1rSV6xzUTsLrCrE90SM0IuHjqPXImh86HV8JgTga3LSQe0MkaGzQsbaTuBEGuyr9YHwwC50ADWTei2jKxuh6YAqgG+JiJZ2DF1H'
        b'60Xlpfg4xbrhlyfjLmgozev0TPO4hY8OjF1CM19FxtWukKCw0kLaJkSMdYXAFh2zpoMzGcvO1mWS+kAaIRFSyEPHQpxoPibMnYubwhQAZrBFXYx4Pt8pHZ1hB6xzpGPY'
        b'h5vkGdmkZI8LGOE4HukINkfRT+KtebOhQVvMEdBUnyDzwQ3sAHoRdZHa1URuyhEpWOFkHjqXb047izB0PCmEa7akcM+iIznQdkWMD9onskBbguhgWJmK75Kmvi1HQUpi'
        b'G0msDLXHDMoiBdpghpvRpWU0Ia7o5UUhcklReqiM9D0WE/joNdyUQxOCLobjDlJ7r6px12K02Yzh4wu8MLQ7qPLzv/cL1EDH9Uj43c4ZmTV9U+0WTIkQ89/wWZbltbko'
        b'7b1TJ9MX753ad3Z7cEG8z6e/ztijamzueN/q/rWC3d/ZfvrDp72PfvZEfnVy6C9/HRv1x3d/veO77x/ZbpAHfJ4k+WZHZZb3375Ym9amyHZVX//XK98n3n3jF/GfBXr5'
        b'5KQU/yx59/XzD2+Yuy764jvnnU6JkmVloi6JKAqF7tscp5oTFuP1XbdtqUNz479P7XD/88IWR/OVd7f79fpt/sf58avejP/8z+KuE99dPbjt/Js7qxwfPUjd2qlSje1L'
        b'/O68QnT0qOJS0oP2etHroi3jHCOr/d/TlBZU//z8637KfZ8FaX4r/NXil9NOMxdsPhItW7zzpcys2Futu3fdvrJ00ld/1rb8RvS5TPNd/Scpn3XFKGf++53HE95895ta'
        b'/rQNHcpi2/DY7aP+k79jekz+2JeO7o/5wb3P/EKrreTdnQcqxv9qcXVYzFsfdB54sv9iYH9SU0z597Mqdmr+dDDYPd3zPfzbKxr+ulfkV/6QrX7ww8O/3fgf91//vHPf'
        b'9vsHdrXesvyy2vLTbS7/bpq0ekn9vavV775fkn099n2nhivH0DjtV7xfnZ6x8XbPyVXx68svTr59Nawia9Z/vvmjujjj+8jvxtg29p6+vyP3Hz5dF9e8Y7P1dsf1qilX'
        b'319+5fEuz0Va5cu/PyHUjnlk+euWezc3zRvffNssRPLE9+HE7Ij3/Nb+LvWziuRVvY9zj90qaSi+HDj7zVimzre1QyO841fs+ebtL+c98T37e89Y574PVn56M+ffG2cG'
        b'FtiefiXoC+cr879aLZwkW3Ws/q9fuK/5ZPQSuVXT3cbl4WVWjx3fndEQrjzWc2XX24kxFx1EvlffeuPwrFWX/ZsDtlWM/zn/k0/+8I5q+V6puPxPlSmvvfrzmtSJq3q2'
        b'BNTOurC7q/rjR9/1/O8rO077pTgGdPhqfzX1jv8nO5yPxTzh//3m/fw/ijN+/dv56/fODFp5bv+X0z9fILs19Rdmr/05ZvzNBaolK39wiLq9bpdyvEZZUPxm/F/M3P50'
        b'6cHPvnKLetJ29dstH9wUP/oo7lHAvJq2bf/4dPs/vWJuTBy35nfVVzt3zPF2mrP9n+Orm2petrxk/tnfHBaP/2rpJ8f/Z8PlZE2OpXvZm6Fxki9yp6/+6/Lol96/N3VK'
        b'SP/P/lL6p7/IZWu/s7JW/OzJx4myAGodgC+h+9EUDOa/GBqpHgu2HG/6EvpQG3StNBNWGfnLecmFCfhqLYVdRaIN4/VdKxlcjoYTnaKTNVk4vBzdsspEbQ4UOmgMHMSH'
        b'0S2KmMKX0UnPEIUTvswibImii67xl6vwFYofqwwi/XOWAt2SmPT5RIV5hc6H8fHU5Wynj+8s03X6RH3igIs78aHVFNqYju+ysDEW2Yjuoy4K1Btf5cROp0X4Fr7HiBfz'
        b'vVKz6QQ+YnxJSLAIXZTL8HYyBFrMJn3SOnydptnNBb8SIofRMJTHi2fEaBc/rL6cCoxetw/KlKO95gZElu0MQRUZ++5SwNu0uaRXbKKY5t05oHBPJtMgqnOLGe9MIX51'
        b'FeqguD8YGZtD2NjJQENmhug8P2o5n715lBTXKyyo0QNf51CNbcIvAcGOD6DbzmqS9pOu5ssk+IoaIM9D4AzxNTHRNy7IKeAsPQTdDDFdf7dPFyx3Rm1kaN7AAs428DMy'
        b'dUv+ObTIR+GtghS0jyjY911oLUrNxRtRU7gAtZGyDoNeP9OMsc0RLFLjXbS8g1FzTEhOqGoamWg10btW+D4f37Bzo+Vphe85ZMrXTjPRjohOdZdFYx7Fr8yDkdAO7edG'
        b'QtSRSCMuxtd5gzCunmSMvuC7gkUiHiFjyiYdQJDMFvZSiCAZI1u/BJ5/VQrqGHpNJoXEfwY3GvBuV7NpUZJKdArf0sEs0ebR2aY4S1LMO1jY3318bq4p7I+C/urxBg73'
        b'F4/vUSHLbVAXGQfXyjLY7RIRY4vXC2oQ0bHo/VnoBoDzSXWpwBchI0SMVTUfH8F72FUntGMtqfwweHvgDm7wDsaH6b2J+GW8hdV2loVyyg4+IqfZLscbXSlUf5ujsa4z'
        b'I4TKj7ejzejQ0JqOYj7oOZPwIbqR44fuousg39baMLlCD7QcjbcI7RGAfcGiIYhorneHWf5CnUlD4xLRHj5tsBK02T8zK530Qnk8vBWfJYWNzrPGT9uFeF9m6BzUFUQ6'
        b'kkwwfjrHX4mOmcuC/nsYwv/bA92zkhr9GexqagCOsc92gPsY1u5evyA44C5dF4wVsSvD+T6M1P/YmtY1LFKx0+ymvdZ7EmD+vA6tPrS619mvbY3WOepDryCNLOvtut+s'
        b'/sXqbtkcrddcjcvcR0FZGseAXv+g01ntWT3+Md3+MZ0LO5dp/Cc0Z/cGhJ6e1z6v07czUhMQ06zodfbXOo+Dq4XthT0B47oDxt2Ua+Pm9waM7SzVBsTdfEkzvUA7pYBG'
        b'lPb25G7ZbK3XHI3LnEcOrq3T2lKP5GgdQjhM5PLugBStW6rGMfWhp7RtNOAHtZ7yHs+Ybs+YzhKtZ1yzZa/D6JZgrYN/r7eMS5hA6x3dmdftPb45DUyux+9b27ZM6xxE'
        b'48vVKOd3y+ZrvRZoXBb0OnsCorNjTE9wfHdwvNY5/kHQW/I35Jrp+T2JBd2JrIgKzfSZPdOLusk/WZHWq1jjUvyRg2dLRYeoo7RtTY9DdLdDNMQTu2+NLp5+Ps8zhfeF'
        b'gO+dyutn+K6pAGMMH9ftGNKsaJv20D2ms7rHPaXbPYVGsEDrVahxKewXMB6pPOCfieg063Ee3+08vlcW0WLT6+vfavZIFkLOfMJ7fGK6fWK0PrE9PvHdPvFanynNNr1u'
        b'PsfCWsOOhDebPXQLaKvQusnJmcPo5oZ9k9r8tA4BNDN1+Uiuv6R1GNNhr8vlPK2bUuOo/NjBmTNQbxu77yUqWKrWa5rGBcjQWld3RN9M7vZO0Don0FuZWq8sjUvW08GX'
        b'zocmH5rcVnG6pr2mZ0xs95jYXq6qefsfW9e6rqPh0uozqx8I35K8IWlZ9ztvxYe+oZqwuZoFZT0LKrvJv7BKre9ijcdikjPSHMhCV+9jNq02msC577vMewJEPe1xHYtu'
        b'Cnr8JnX7TXroHdKRdin7Ju+B/1shb4R0eyv2pD108m4z7/DrcZJ3O8kfeod2zAKYaxo4RF3UYd7jENntENnrHXhsbevaI+vI465+bWkdpT2uUd2uLPZ3rtZtnsZx3kc6'
        b'n5BtDafXtK/pzO+Jybg5v9fdpy21dUrHtM4FXwh4Lim8ZiFJNHlwUuskrUMgW4e1bvEax/hHQBLmR/5RkjBgMNiT/JG7F+uL9ExUR11PeGJ3eKI2JAmQvy49srhuWdzN'
        b'8VpZMvkyqRbNyQCEdTkUvye+LUXrIAM3Gcm9nn5tC1vn7kl95O4LiAzWc0Rz8kcugb2O/p8LHFztP3J27xeRX+B78u83I2f95gypLx6HPfotIGTJuEqPWR226reCkLXu'
        b'ngRCNuSdYzmHc/ptIWTH+AX3+Ma+5xvbPwq+aM94+PY7wB1HxjOkxyOt0+aBmSY8rcdjxtsz3874V78TPDWacfPtd4anXBh372Phh8P7XeG6G+Pm1e8OZx5w5glnXnDm'
        b'DWdSxjes3wfe8mVkYZesz1j3BCW+F5TY7wd3/SHmAHLWLOoPJe/0uIZ2u4b2uEZ0u0Z0Ompdx1Gw80NPEuhc8cBF65nRnNprN/qQ5R7Llpi2oPftQnpDxzYLWYaItuRu'
        b'O1mvneMh6z3WuivgucPZo9naaLvEm90u+RXsiFCihBw4KCmYtmyFHs1mRELwPEjan2g8AbVuEB53KDh8OCBMI8ghWMh5tqTo3Ok+PJ6SonNNj/30+DxIXSBD6RInCJg3'
        b'BFYJNgIZj1I0KJ4BrsMrEBUwBeL/HlynWEaEsEworytTSUuKq6qoHzMAqXJ+2sgYWgmDZ3GViXszltm+tJR1QVIsrS5rsGRhkkFFRblL69Kry0mmL6yqKVkiA/AZuI/T'
        b'4dfq1WXl9VUANltZUy9tKK6mWLDSyuWVpWWWJpFUVtMb5ZSSjiNqKVOz7C2s2xMpEJBLK0vVckvLuNpiVfFSKTDlxUnTKc6MVEJ1JbhrI98BzFmxtKReXVezlH1NL2p6'
        b'aVGRDFiQLUHvAGAbSQ8H+wyC08pq6fJY+ViSlESS7AZIfN2i4jp97AZ0Hv0CJxv1EUcRrSxejrwAHuNMkqjjsalQ1dTXUv8S9AskKXWVJfVVxSoW2aeuLSvRE/qppUHA'
        b'2RVKkkSiocy0K2tJsKyuRC6jmUa/oS6DDKkr0+UbVw4UgFxNZKonGUG+B6W+UlcapTWUJacWvP7BN0wybABKb/CesqWCXdU6iTtQF5llT8Evw9Yf3ffDp/Addt8PVtum'
        b'o1OxRhaieI83ayTKGYjWhddngW5+BJ/Hu7htEam5AHZebi+LwPvdvNIcApatxZfy0MvoQhLaPzcxvQ6dw+2o0zxeEepJ5lLt+GgyuuO9KiwLnbWLECyky9YBSelM84qr'
        b'AtIvWIan5jL1dAawD5+MgsVEl5XZyiCw1AKDZDABN2N8FwthLwgdoK/fHStkzB038pmpRVldDROYytNNC/nqs+TO+KAAFofm8eZ6i40tkT/b6LqpNatV+smkLUUf54qX'
        b'SEMiN/JKxVanVkmCXgl644Hdr2xiXxZ1HBYor8ndBZtkfptfeccFmWtf4Zdu7hQuK/l7xMu3Dpg1/fubZed+kzI2frrHorh99knmfu9+VjTjnGzqsra13RtrY7t87rw7'
        b'+qNxRbGXFwVFCAXfHcMWSndU9UsX/42VqyPuyMMFSZFKG+cs/1c2RAmYt5eOnvTl9zIrOqW09ED3dNZx3HIImfryyQRsz1S6IuIWkM8tiCws4iXgZrz5yzhyWYBfg0nw'
        b'wPnNXTKJeorhFZkN76U2Udn4Cr6oxpvJpPpCmiIsSLfEPgo3C1Anuj6VzgRHoVOoU2enLkIvx7DrJvgU2kJXCNBhvFUUEjZmDjUcZK0G8T28ns6jvW3wIWo2CEaDVege'
        b'LxWdxx3sFPsYOjUqJGxJDiwtsOsKhWgzu5qyx82SswIN85lttJiDLuGTFO6Hb+NDZKqmMzw0ng47pggbIolsAF6T4KvlA6fD+LTKYAaXLh4RZGaY4VgAAwXLz2kKMtNf'
        b'p7MasC+BWc2CgKFnNb2c6Q9RXnucg8m/P3sFkmFMNpXXm5gK+uFjAU+mAFMj7xwY31xzeB+7exMli3yNqGRH1ujsuWK6vWO03rEtQqIgtya1CY+kd/CPKIhu11aodYvR'
        b'OMaA4c+kjmjW1ofyTr1HdIhl3XZBv+OIAE2QhnlP0w0GIw2nwEg9lRxOGCMNkwJ4PBcYlV2eG2nI6zMjw1EhGY+G5mGjgzFPz+DC8rcI9Pwtop+QvwUG45tECEtlWTXn'
        b'6cjUD2q9mh2cy2j3TMaKlMT0JKWxn1NuBCxbWFmiLiypqiRvxVHkt47fuhx8q5QsktMn5ClwTKKPGbtL5b7C5UucFGDpoXpcOngcU5dRMWpUpXCBjD10rOBcug4bhzy1'
        b'IKuI+iKor62qKS7VpUaXQPoRcAek9yUAwxRnDKKur6xjHa/qI1U/W6xJSflFoc/6aMEzP5qe+6yPJsya88xfTU5+9kcTn/XRWSljn/3RqCIppwc9w8PRRXL6aHo565ue'
        b'1VLKSkOlwVz1CTaB+5vaGVDUMqtmDGdBkKoqps7uDHViOAMC+MxMUAzZVrE8Sh5hUruoAQPriomtfiSC5ZXFz5bSxPwCEkUcy6OsZtsUGw9bHStLB+hGgyFRTgqqQuyK'
        b'MgPMj11u8LLQz+zsWDqLSUTfOKi2AnxQ24x1DGpFB+bQrcNpuEOFuyLmzIiIEDH8dAa/ijbgGyxOqAmfJCOsQk6GaNykQAd5mUrUzO5AH7JGe0MUGXyGj26j42gjb7wv'
        b'bmW3Ww/NyA1RwAojboHxiTdpDWqSCem9ZalVsJGejVpt8RURI3DjxS+aSz+4zp/oCV24c0F9Hb5BhlV8gOdjV8SKcYMMhCfUY1VAenOlrIZBNwrxWVaMnS5oJ1Al4Du2'
        b'KiI+PsULnuxCE5yNgLtmH9EqbgkoFigZ7aY3pJNWqkELZHCzBT7JoB34TpqMTz+3ynsdiIe3ZOrFy0LXqMJpl4DugXwktZsMEuIdFtQLOhn19+Ed5LN4D96tlwRfRK+x'
        b'm/KXi+JY+dHWGpB/NNolE7DcNc3oNG6lsZ5g9LGGWrOb0NfHEF2IxFqETxkiRbstKbgjFJ0rs1ruhTos1EJGYMEL95jJZkoHvo+vWElW4wMqW6JOhfKmoMuzaWzz8FX6'
        b'watECTtuZcNjBNa8KXjDmHpg3MNto9G5TNBKldQmAsAmRE1l8HG0dw1RgncQneou2o+O5pPAfnyXVI69RAvej+7aixh8Uw60B9azkvEBKp0jfh2dVeJmcroYnaxh0gvG'
        b'0TTNQK+Tl/Y54UtgfbFDCSD8bbyERbmVv7vyRKh24TFM1NalAK23Q25U040gmu5G19kun7sk9u6d7eqS6Lqx9fwkF5c9StXDxN7otmD7X5KLszbO6vxb2XX+OwGnBLND'
        b'p77t9u7ody++Zf/mrjP2f/OyyZquTDV/5S2Xd8xv/Mpmkds0u9gZUSsiUpJcs1sefRzB+21/yWWzjL9GCr7zaZR5t1dZSlydxA2p6zJrg5KZ3/MdRZ9LNqxRREwRHcrZ'
        b'eOt8QrWzcOv+iHE38IcdG38prO6U2Dkk/2LsBrNfCJf9Z8y/vN8qFof3ev+8aF1G0Tu4xGJhUzSv4YrwF3v/4jDZ/9jb+8r4U/ZabC9tXe/h/Q49nv1XduOMrf+wf/Dq'
        b'r5e6fOOyUXT5A+FBB0uR9udVEUql64S5jOXtyZMDhTJHulAvc1yVaWBZsMI3MmFLj49vUMV1rCybKNt4M242ogLho0aqgi5Au9HdECNrE6Ac2hwqMCNt7B7dH1iHLuL9'
        b'rFaOrqKNy3kJCaiJarZyV3QiBJ1xKwpNEzFCtJmHN6H9PJa2YR/qGA9MHtV2Rlwe6Czm9ih3u+E2na7tV8RtURIRWqjE3hWLQ2CvLz0MddnwGXPcxEcbVuNNrD59Jy9J'
        b'bYWv8RjeTNSFmxjcYY9fpbfcY9At1FQbA93CIVIZt5LGVFLM8occmewGt8QMbxWp7KQO77GW0F2c8XgjUFDUxpAPLkG78TbKFa5gk3HdP9eIIyN8LWXJECRb5tD4ppGs'
        b'2a6msJtStAmdIrEo0Q36VTXuilaTCUcjNPFbIlLrSayXPdkUvA48EOQ9Ebm33xadZvDRsFKWWmU/ujGH9Bqkt+aFl6CLDH4FHfSjKVhBpkDb1MuXkciCeKgFCPXaG+gd'
        b'J7wP7SB3INm3K9FBBm+f6E03GG0L8En1wEnPNXSXTnxi5xKF+BmWtEAh5rZGOLsgNVEW+0aZ2p+QS3RWAMz7MCuoHqOfFUR0e0d02nf6aLyjYVbgtmdKr3dIR123d1Tz'
        b'tI8d3FrWcJQNy7Xe8b0BwZ0pvf6yzhgyO/CM+2Nc/C2/m6WvV96qvCPvFzBObh87e/T6jTk9vn18R/6luWfm3gzQhE7V+iW0mPd6+x1b3br6yNoWIfk+Nxkx13pP0bhM'
        b'eWzGuHj2mzOjfdvytU6yh44uvU4+9BT8jKzcs1LjH611jja8J9R6x2hcYsD1r2ura1u51jV02JtlWteQQTeJsG6hj5xcD83eM1vjG6d1itM5QBn45KNB32XfahujdQrq'
        b'dQ/k6HaTte6RGsfIF78ZoHUKHHTzL6O9e6Nib0y8OvGB8C2LNy36oqb0i/g+CWR6Bk4H+hn+qESe0VRKzNIbWBur/SrqNm8AnF3M6GgG2dnULHgGnFW9oQO0A8vgOjKb'
        b'kj33RMpe9RKfdRVSt6KyVM369AAnHn02xm68y1Sqv7DPldRUl1dWqCzguUd04biwvHJFWSnrlNy6sFJdWFqztExdV1mi+gGkfQgPWVJn4era4pIylZa9YDDDEhXCtABc'
        b'qtdXlupMR0DpUv0G7Jldh6LN7RMW5qQrSORJBXl5KYqk9BQly76op9Pts6otrqzmKBJUGhqpgRiAXQPXc0mofgMHyh3xjSntLrUeoCvNdBJL855y77r9/2DrFTrYETZb'
        b'Vev53AGIWNXzWGce/TaMu1ebslNwM+pBSbdDRiPszDh7tMV0im4WvB3QO9p90OljM6G7TWPmE2uBJORry8mSElKv4fh4Kp96pJB9IeC5hzRmfgR+JmS9jpPBGcVU1hmF'
        b'm+9Du7Bex0RyyS2Z15hhcPkRDR45xlGHHJwTixR4bxrP2P8GuMRwSmRdVnDOL8CThvsE6vyC83QBHjlcpjSmfW1uK4l+LGVcfbpdwtsnnJhIfhrTnwh5kgigLvaAQxzp'
        b'xxJ4SbyvBQ08iefXjOH4BT1+rhIwNk6tft0Sr6/57hJZP0MOX5Br3v0Q/DwO7uZ3S3yf8CdKEnlwx+8LesoSI3tzGnauKVnrrJVEt3CbJqx8CbeaTDt07OpfbAE2ZEew'
        b'MTLlQ1YJgQuZ5UGWCzkmZPYc+JAtyV84B15kYEVmrxvORyntlQ5KR3rupBytP3dWupBzV3rupnRXeig95VYq0TxxgTiap/SC1RI9w6+ZngeYp7QmR/hvTv7b6/4rvSeY'
        b'eTFejFLGbX4IlNIBLMHm88R6fmS/CXyVheGb5L8V+c+P5nPfc+B+7eA3wnDdnosbfuF9y2ih0l8ZwMUdDEzQEHuBRYGkwL7AMdqc5VA2ksKS8iWLKS3qqGgxx6tspQxS'
        b'WRcw8TyVhPJihPTZw/CcRL0dU6bw8jJVJTiMW+VmOfgO6xDS8ls5mWnGVapr4tR1pfR3bETE2LFxMEGNW6EujYNOSR4REUn+k6lulEzQJ1Tk5GX3CdPSp6X1CQvypuWe'
        b'4fXxk1PI0QKiKcxRZM0+I1TBnKdPRBdQ+ixY39WV5FRUXlVcoX6eaCMhWqFqCfRk4KdEtRQYmoXpCiXrHOE5vzVBJhrwLVUD/aAyeUbCt4mL6upq48LDGxoa5OrKFWEw'
        b'VVcBN0hYCUd6IC+pWRpeWhY+QEI5mdBHjJWT+GR8w/fP8CmFs6qFUoL0WWTlJCVkFZIZ/bdjQOikxHQqIfnNLV4JWlUebLWo68hH5RHR5EhGFvjYGZ5qC+uMYhnIaq1M'
        b'V0zLSilMTMhPSnvGT0XKBKxc+iR/GzvgxSRVjVqdSJcaTL+RVVORra6gX4qEL/ENXyICroNv2Q7Ij2/dhk/Ut05DZp7MyuQrUN1UG4f49gTVZrg64CMT6EeiVJvg3vCR'
        b'R34b8hwp7TMrLSsvrq+qo9lPy/L/JXnHyJauLP5896oCtAlv05sH4HO4DbdUopO5AmoEWzz5B70RLGN24MIHvAtmd4cxgu0zL1TV1NeRms96OzHtRuS6myb2sKtkRPd+'
        b'TrNHcJei2kUO8SIjs8cG2Y8wezxjxqpLvx5CZ9LoFCcT20hLXVauZ3S74kPYRvKoJSRwVFN26mhLvd2j9U9o91gh4xfvJXlgmc7yqFSuKjNapme92bObu9CNGy3LK+tr'
        b'a2tUsKJZSz3jUk1SHWdpGSYd0KykQckpMtPL0AwHXZkgDQpWV8LO7/JY+bjgIV5hW640KClt8E2uRcLNUOnA7wzfO0iD0vOf+kSk0RPP2pDhlYFC6HYguFVhdrmVpZop'
        b'LVtYB27iOT+cuidhNGMfG1gMtarKGlVl3UrWS0xQMIyRwSRCGCWD2UXxYBgr4RqMXMGwAxEMQ06wTG7Y/B8nHyuPiOMeYV8z4AIi6C3uK4bL4+hl9lM6QVl2LE7UITiv'
        b'2PQFqintlT55dALFbsTo92FopRuamYrj/NHHaaCXYiNm6+tA5ihga9JDNUrZLR1yXg87TbBpQxf3KQykrLgOCpQIuXIgURcAHSrZjRnYECDvNRSrOJSIkR9VmjqpsqwM'
        b'ZK+vKpMW1xEtZGF9HRttUkJ+yrScvNmF4LI8R5lSCF6mlVQKPaKDkhip9YlkGxWbPuqfnmOG0+WrbnGE26pgARKG7Qq6xcS+YdhdCB7QpoL1EBGag7VsvVbTRA94dkIw'
        b'K63ukcpq+h5HjUX0LXZHA0Ah1dKUgjxuG6VaqmyorFtVpqqiGVn3FGHYBs7VRVLh0uuKq1bSB4dvwcGGOsFxdLEZZqDugprEZZmexovd8eMkrGMRK0ZulEyeNaFu07fS'
        b'obeISPK4QVytqx4DvsPmGVVRjWtaemKCQrqwrKqmugLeHLD1YjFo9LVTUDs11BKAt+B9mXgXbsabEBnX+PgELwi9jtro0nw9PpOXiZvEuF0PWkG7LQ0093J0G+1VSyR8'
        b'Bm/DLSzFP34FnWMNEc9Yod0wS0M78A3ytwttEzISvJmfCAZjJI4myhwfo5yXaTA1Zhh7fFyA7uDDaEcK3k4512fh4wlK3GhhOcDOcyAdPjUAuWFpgQ++JONT7SIHb6iG'
        b'7QMrG3Qf32C3D9bhnXSTo3QuumAlUdmWo1Z208EBNddnkxuxsWYGVwjLUozsoPXmmbUSSR74QggKUxQEBeHteEc43h4KrPUsrX+YGNZ4HXiu2aks/Od1dBy1AgG/kMEv'
        b'o10cA//9MXQD7OxoMHqv9bCRFlX90nYNUz8RXmnyVBjT8qfJM7LxNpLe8DzcmDU9TZCHtvmgfWC1jW+h11YGkEiEVrhlMbpQ+WF/BE/dCwqOWdfS5sv2GyOstyhD91//'
        b'0/G3bq3469/+9OfLHX/9vbPD+O6IZTYfngl95+/7/nX/1MKEi6Xp7/2Q+d6fT/4hd2OUde584cpdbiXWkYnbfB0u3BbnTzD7zavvRew32+6WmTx5T+YPvxKW7xUt/TDi'
        b'rNLP+o+vM2ejUorf+GTzYlHumFe8dvZ4PrTeMbXyu10V59fei3x/zPfLWyW3096f+239b5w6v6mc6bsz8Ss7z6VdvWXrSjMa9n2zptTq07iJ14/fPRXy16ZRbu/u/2Di'
        b'qfsfy6ceyCz89KXjZh8EfLcgJvvA17b/meeb85mjTEKXltH2ZM8Q+bRpYSx25SQ/Ap2QsbYrB1eksb5PwINLKABxzBj0KtpqkyeIrAhhDQj2TBynR9QwnriLLvOjDfF0'
        b'62E2OkbqIMCBYlC7iYEUap5NybjR0RVoL916wLtzKL35wWms6cmhanQl04ijGV0sAaOgMryJM1NaI9EBa1hYDRHzHoXWjFpHoUjO7ni3Cfs1eh3fo2v7eSyPNrq5ZM1g'
        b'Im0xY4bPszzaNaiRfqkQbxGxhOc6unO0bTUwnjui/XRN3ys3lDOoOh+t234xi2CNrW7K0E4SCzTeq+hsJrmdzUtFe/3ZfYIT+B7eRbqOLB6DLs/mL+RFor3xMusXWnWD'
        b'1RpjYKoROfOQGr0xRbOIXdv/sjSEGTX6/2PvPeCiOtYG7rOFujSl9wVpCywdpIogIL0XEQtIR4qwgL1XwAI2QKSpCCgKiAiICs4k0dwUd7O5WWIS400xzSQmeGOqfjNz'
        b'dhGM5k3ue7/3fb/fd/Mzhz1l5kyfeeY8z/8R6th0WYg0PId1xy1uygtjkya8gsZzbuY9ZDFmLcKq4gYmrYaNhrXyE/qmbR4ifV6tHN6hf471g6buU6VqXfO2QrGuywcm'
        b'NhOevmOqV1RB5QMWwzaGqAnFEjWhWMZdXUOhqaNY1xEr+lMMW6JR9B16bCF5LJQ8Fsq4Z8idsOE3sI+rTtg7N7Df1uPd09RrCJEY8UVG/K5siZGbyMjtLv4UYFS/pG5J'
        b'm3mbs1DbkvZrLtZ2GZ475jPmMx0z/YBF+S5kCLVdpkkzqtO0kv9QxHixxhF2TjdDZ3gavxc7dIvCMhB2IkM0hFNsMbP3h79K7iXMvnZ5Z6qf4/vfAfeWrWC92DPq81qQ'
        b'DN27D+WirBs/SvCdDn9i4fwsWBfvNyWEBsTfZgcFBybeZi+IDw7iKTxPI7zMGQuQmWTXPzMvoyw3WzBDxFOX5bkaHeYpvhB/g+E3CklqSMTDwp46wdxoJM1yU/9/C3KT'
        b'cRMLewFZWWiFN11pV7ZYec7e3dQyUxktd7zxotY7fer7RPpzVGHspYu8KaYn1hImQM/pL8xEi8QVaPGMJPqnS+lyXJTlUkHhuSKTdLFN1+xzpCba8Tj97PTX0de5GQJu'
        b'TmFJBt5EQMvufHSluKJoRXaZTE8LJUom5OL1mkzHLICETp96ywzRY/prZIJHefYael2Oc0WzSYtojWWpCjK6lp+FF6lPszLlplyaJq4NSkgZSSpZlJrHhzg4OJjzpMtj'
        b'WvuHqKtn4NoUlJdVZJZXoNiexuTADZEpn027T8JPPUNaQsWqwmxZlUg18dD6GyceLfmLUFGQMDbxwSHB+ItS8PLopKjA4Hh7rkyaSQxelMibKp9soq+OCye7OItfXsJH'
        b'f6blz6ZkFa1/Py3EmucJdOhqdhnW058u0M0IjpM1Jd/hEvkj8YwrY7xKWw0JnVdSiAT650tuXJSr4PjogMjfS220SvsLJDeZC2o6K+iMi89Ig5DWG25nSFhF9YIqKD09'
        b'uqQY95xpuvpryp/GjgPjUEhQwPrzuMNMNY2cspIilNWsDKmSfWEFvYGTm1+ZXSxrSagpZ2EtMZvMkmJBPsouDokynk+uolKZejEdbLoYz5uebDopJSsKsjPL6f5CC0IJ'
        b'MZ4eTs6ksaDCI+nD77CXwsGl6SdyN27LqNOTcDkVZaRtkt5A7ACeSnP0sOrNTZBKVwLu6rx8JKBhM4K1KJZCJJ5nZ5TRMhb9MN23BIISJNSXS19FK5eWlaCGTnRNUVFI'
        b'Cx81LLoZ0Zl/2osduNFIqstYtaowP5PoZ2Kxl7TH6WYOdNtbQPeZDGknR7HjGYRrg448ey6eR7g2MUnxPFxYeD7h2gQGR0vbre00OwwPnq3yNGW8gKmh5xlfrNOVWv8L'
        b'EdE0mtbO2gpPGkqBZZT8HHAWyYBlc8nqgggv1woVKBW3KCaFhJdP/QJo7T1XMFKJxUJwki11/BagGkLILCuLygTwUgFZQBLuWCoR1MBZ0OSPGV+wWVcG+TIH2xKJS6yV'
        b'XqxnxMgCcJlIkrAmwaciAj0S6LkY1kg9h2EHdYlSYk0E3zY51F4FtoQn/ZEfNcz/6g2eBWoWwitEsI2E1Vgd8CAtPNKCIxhGEmsKhXVy2tX/4G3PvioHtNoTRJPMhWSc'
        b'zRTJiCdPeTtpwT4wCGj+GrwE6kCtii6WTGmxdIl7BXZuDnohkrUjCNyNHx6DZVM6GjmUyp3KlvqgWxlUycTB+XArPI5unJgNdoJTiaAtKw5UBW4Cx8A2VNRnwUn0d9fK'
        b'NaAWnA5csQxUB5blx8UVLCuzXAIaV+ZpYD9I7av8jJCIA/tIM9ikAA6vhQc58NIqFSbFhFcYjqDeh4C6lsNG/xemC1YlgXZ9UDUf1K0AO2ekaSc8AQ/j31hbL10d7uZS'
        b'oCdulh68tplo5MW6wqvggienUqYvyNKuyMYlcRm2w6NTIjovWUpxW1VRkQhrV6mqw4OJ0hqeJrtjkR3XDeE9wZbAuKfIM7AVdCmSt6jBPTrwHNgOOirmoTdpqWPHVn+A'
        b'2cOhEi1nz6hPOAh2qy4EW+IJuQq0wT7YEjHdkeg+0FMITsWShoMijiAIKtSaDskJwkH1bNTAq+GheCS9VjPgWCmK6mJWRQyOqhHuQlLYM1HFhj6V/5JnRAd2csBhLUt4'
        b'Wht0gg4dbRa6WI9iiZoFOmD9bMKCg3WBhdMQebKMMVEJH0bvuegLLqBmtxNsgztQGRPlSXBwBeYJqcSDPaC1Ip5us4dB7zT3kZFhvHC+QzLcY4/qqu/ZQpOlT3Vmz0El'
        b'11wxG9TBVthfsQjndwh2Z8jIQnGhz4t+ZtREA/TF0ceHa4Er60APGXA04RFwkmzI2EfIHCLuAk1EN4b4jwT98PQqu1DsWkzqQ3Km/8gROIp93ucHrrvAFjxGosYbLpwj'
        b'SVExYL5G89FND5I4WhrXf9RWW3FCYY6CWZmHaMep0ajIvQp7X+F4vFLz5HqN9W9X33Qo/OLyKHs97/47kVfWfvvG/fuVszexiowY5976SCj/2Mhx2QMthtD8gHtmrOnW'
        b'zdmlaftunL8cYr+i5oqW0y3xJ9rua+crq53SOddTdftmyp3XF65QPddRwzz35Zk50fHDfTf2HNN+0NrkLbbp3zP3Mjwy22Xipc/GUi/uifvsvPPlkHkKfvK2H6766dqF'
        b'oM25ZuOMhre96iPClfbqV5pqf1CY6009ytjFz/zA/cjHWuvtzmy4pCEWfp64RtV69vrgFb33PIHK9nXldsWNX21Q7fxW/o0tK3+Q5BV/6saavX+ehuOcAruXylcIuwXN'
        b'A1feND0aEt05eyhJbftY6Jdnj1md3s27xmia3F+99krWmw+dl3235Y0vyj7yPt6xstJzctbXer96WI4Z+H10B/Tc0Htoe8w475yn4Jcf54z8yBxPuF7mL3qy2fv9o5U5'
        b'q6M+qHjzypDz5KW3OR/8NhB9TuF02kqBgvGrW+998sruLw3enZXaqHtlbV7tuoSm8oRvH4dy86s8TIsXpTy4tz9v3zv5DWsWbJ4VtdHA4rHv34RNPp/z1N7sGEj6uPCe'
        b'5q11EvBtmI9Jl15piaLqw4YPHH5utBj9dcNPNd3NCl4Xi0FKnq9g8syimF/nHV62idHxj/KrG37i6RCVTFXtPLzxYw2GptNgYA88Q3Zj0uA1cOoZGzPm3CR4NBdeJjta'
        b'Nqjvj+I9JXA4ibjMA13gMtmMEdj7TteiXcxU9YDnYTXoJXdtdWEzbCue6VAPTQc9ZMPJxA4clHnrk3nqW5OLffXZgSGCg4FdYDe8KvUKKOPmbAADsAPWgR0k7fOXg5Oc'
        b'CHh88+/gPopp5AEwAo+Bxqc7aopgEJ6FY8xKWMej1Ue3gA4NV3fi+lSmkuvDp83XrrFhHabMh4EeNiW/BtYWMs2zwXFSKLagBnYQ5hAb7CPe9cCWBNpt2ilwCjZLN8Iy'
        b'1KY8xbGC4G7YT3bKvBxBtfQBNM32z9gto7fKKBoYgx5rMJL5L5USUYIytWE9uEZ0Zg3jWeAM9vK33x57fGbbM8BlC7iXhikdKVpg5+ABzkzfaMO7bFawlVbwHU71tHOg'
        b'9ylTjclO5V5dGrayFdRXRESGgaps2OP4LGfPCQzLO/puJG1raQXYT9pOKGzVsQ+PQYsWtSCWHzzpTzOCuuAoPCv1HEjJz15KTAC3upGiz4dbtEGNYxSfhxIA6zP9mFyw'
        b'fRNP939Dsw4X5guAJk+Nz2+bP2ez5nn0EjsWDRrP4WPHbFZdVhJdZ5Gu87vGc9pCuoJ6o7qjMAUk5O7zN/e4Fp0q7SoSrrOI60wAJVz3WtUJM5tpjshq1e5a2Egs3EQW'
        b'bhILT5GF57Cx2GKhUMNsQlO/3r/Ov8td6LJAaBsk1gy6a25dFzGhbd6WJda27do0riV2DL5rblUX8UCesnAWzQmsjcAsDsdGR7GBncQgtE9+SL1ffdxd5BRaq/CAK3Nk'
        b'dmn1+wYWDyiGlQfeZeSMcL5jMayCiNezYOL1LJhBwx686rza5MWaVncMzaV7jQFkizGQbDEGMu4ZzpF6HTvp26D4491p+rdPgySTICkkSArjrq4Jui+FoUjhLg9YlB4P'
        b'vVHH4GlwXRNp8GASPIQED2Fg0IRPqw+NUhGbxAn14mQbqElCez+hxTyx5jwUlZ5R/ca6jSJdp74Umu8hdo+6y+X3aYm57sMWEu8I9O+d2DQC/EgSmycLjZKx6zkUpkvu'
        b'LV1+n924liQgXhQQL3aJJy+TImLu6ZqcXt+3UTw3eWJaSiLFJlFCvagJozmtMa0xfQpDKkMq0uQHkuQvIMlfwLhrxG2NbIyUGDmhf32JQ0v6l0jcQ9C/5z79QBlXgk+d'
        b'j0STJ9LkdVlKNJ1Emk4TplZ1oXdNzWpDP9E2EBryu8pF2kHjKTdzhMlLhcszJ4JjhfGLhUuyJlkMnRxGLRMVh6lVLfMwB5fUVGxCW/TDV6Tpe8fMBrXjsO6wYR2xvf+7'
        b'puZtbnSNik2dagMPhxJyCPa016Ui1nSbsHHFruosJ6SlHilGCbKwqw06HHVXV79Wadre8OwXEiue7k+Wdf1eafrP9HEs6v0eNDGNLXEdHWrlpnt+W2rPYMQTnkQ8LmV0'
        b'/Cv7x1h+PS3vQV3iBDBmbiDLyyRb7HV+njzRe6KVFBWSFJMoN/kpDSi5fy/rf9185fjs4qzsMsF/tTdKNpakwjveKskQcBdFRT4joZtQz0rovOgKXHrgEDwFr0Y8NT2P'
        b'exbbW5PyDMAV9GfbofX2cXBOVRv0KFZwyfTNS5H5S1eHTTOXu1aAlouxcQZoF1SCc/A0/phJr5zZa0gMsD4XbsFr6nIHtDhwqDSyQH/CsZW3xTK5uYbriYAb4stHa2mw'
        b'VR9TtU0oUDsXnCASZqATEjroT9H0Z2juJhvjDWSPIXMli2JTenOYVLr9stQA+ttzAloqtRBCN0UxYAsFzq0DY6DJgmwzrE1Cc98hFiqbDdiWLh/uIvZ8PCSO1XKUfBLL'
        b'MPG2G3+t3rWZ3oDoBg2gxY5nixYu7LUMd7AFbtWCx0iS83zgrgj8vS7anCtHyeswVRSLSJLD4YGYBLiPTaTzc2CQAgcSwABJXTqSv/oJXVfK1r2AIc+GlSTCFapgbErA'
        b'R8uuQX/GArp497p4Y/u5KeM5fXDWDB6TfkQeRUs6GuwrtbsDw1Z+sMOa3qepVQLdeJsEycrojQfgHlt12E6bCZppT9vHgJfhgD/cbUkUAGYtT04A++BhXziSBPfBIxjd'
        b'qxjDgBc3yJOSf23zfsqIEVug7pTu8I+MCHrLx3m9ORVEeZYoUOkrXA1y6Yuu6hiAPb9QIT29YJ+fHH3xULoKpUd5Ilk+PfLz2aX0xTXLdSl7SiOEzU1fMubvTtFtZw8Y'
        b'0JBCi58Ci7UjMbIYyZ4ddPFsc4Yd07YgImC3I1r+jdCahC3gBDyE7paqogWwFqMcbvEB9VHklSwWNjG9aYleWeiRW47d6ZDNls48o6l6CIVb/Y1RjZO4usF2uGtq5wEJ'
        b'wDWO4CiDBHLXS4MDKJQCxbJClbfSD7S78hi0KWmzPxgVRK8DrXjlz+QwuEpgC202iY0mWziV8JI6k8R4DvZ6LoLX6Ko7CQbAbg5qk9QS1JV7sKR/kC9VjwTHAuGAin82'
        b'vKSAqvUQBXsK4AhhxyvMwRQdeF6PiqPiUJAW8qbZcHcEx8bWDvajtnIuElVnOHPxWriVhhxvA22gHQ44hsOhSC6oYlByYDsDHkVr39H8nX63WIIiNCb7/2b/RupvK42C'
        b'9Vree//RsrLlPw1bXaqSnLp0NDH4wCVefyDP65RZ9r3kzJqd6QVyr2kraQdVm9qcaFOcrVW3bduebdtC43jBQUFaQbMCfg3TYG/+bvOqbyorS4o/zL0kyP/1puP6tT9s'
        b'bP2s8UBz4+pH3zy0WrlPknr2ndC+bz5c9gS8s/SVaLu9znWK37RGXSx4P+OTA502Vse5Z9+Qv2mgPCAvCt+Vur9+UST760Xv3ZjYG+bHWhPPOPBK3Rer1kQ/eLLpHZPZ'
        b'+a+vPfUxl/dt9hd++0ovvNbwdu227xs71x4rDs+6/UXy4JtBHoUlp91v6wcsa2vMiHznK94HoKH+XNPPp0Kd6zhrgqw6Bu5dWeIz5vJV9trGnLCLykbBzWFqrYPNJX8/'
        b'U9gt/HXp40q/+gONA+/t/PvkJPz+2Dy/WV+ObNi9886DLzuKc155bZL3+TrroE7Gl9/rtzUoCirFo+a9H7SefPRp1/32Lo+Y42/6zipWT31UF3iz6fM3dPklF30+vrDB'
        b'9IHbfe174mOTa3b9tiXjJcNvMkPzH/868qbGZ+te7/k2mG/5zn7br9ca5K5KS3xdYct7H4GRa/OuLu3/MCBTVaVjp5Xekdn6R1zu160p+e31gNe+ZfNvfS8fzF+7cXPw'
        b'R8OzPdXOy18r2FES8pNv3lcJiSfDd9UtSbxasacsL27I9rc5l35ucP6yu07FS4fhWvND61y2r7Fco8PY7hO/6r38Ut7bh057/T1pmOHwxTeeq+o/jdA64vcO2/tRfGST'
        b'j83H7Jd/bvkh88yHyVtcN75+4GzjVrfoV/J7vk5S3hby7qSS1SsHr7ZcrHjnQlnl2KDruHXzPsPjcr+qL5ps3farZthGNb+8N+RfufaZ5rwnu1f8/L3Ky2fuX6tT/czj'
        b'0j8SUwXH+zmbv3c3+HTfwwN3wnJHXmmwO+Jx/IfQBc1OhtETYDe18Gjrzs+9qg1+9Q90fi2pNHzfxydjv9qgUtIbpdv2yw3qTGuXuu2nqg0bZ/3cXzjaVWUc9hbr9roh'
        b'fVddk85Fn/+U+AmvIaFoDbjNT1d4zLxjPbR9dfZil6UnHn13RfNQ1rfVb57Sevfcw1K/k1f85a6+d5y35MmphYlGZd80vLWisiIz3uLe6c+94r4RxCToZth98PjJe8G3'
        b'jvwz6PLa4McOFWeW9L7U6v5ZTTPnbPzoSyqluh1nK0eWpvI4a192PnOwe03wgqLvfIOWb/m8huJ/V/86v9bLER5PsQl/c+OhVUOewq8fzd7svt9sSc2y7V9y5xoNmLV5'
        b'fX1LYfjLI0VnsviPUwQfPPA/o1r8a/nYWcF9uRLN+fbfOatG//rkjVSfBtWfz5SDLx9u9jw97/1NrVdL39vxei/r4ksfttlsFnvPvv/5int9mkOXbrQYjts6HvnwRF5X'
        b'7Ef1Xyx1srsj/3pfy/jeU/URvxob7Pwh6o3XXP/22qiQ4/2Pl1LKnD+TW795e7Ou/Gdyk5N+4ysNOKd0Et7Td7k0eMk1r3Dk0sBno8uKctNvlxXl3hoavP3m+NjLt9/c'
        b'dL+owIf13ljKe1fVPeW7vlZ5zC8Y/co3wjQ28qvR0bfzNituvO3/8Xy5H3+xeSei74fNKle3NOu4btO+r1mb9s5hR7tP7WJ/StizSU109tKdl994KVd/06Ez20vCsj99'
        b'ZLDnQ9WCh45bzrpUnaV2OgbkWB7r/jo44E5K/9rrg8InT/b2XDzqP9l6oQN8b/rY0fHWmPzXr4ceKdkSfnRzRNxaq1/2n7it8pPJJ3v//mq96cdDB8o/rOeIH+2LtPhS'
        b'4fMnrRtWVt+pv3nG/d2qJ3V3ahLZm39abvQP21+bDNYOf/R31V+3X77vy12h806I4JTVu643mw5cW5fhe09VFKMlPvyxy+bTi779bcnFZXeq192/7KS1sQCu1Dpwv+it'
        b'14Ka147cSfjy0x8d2/hfetutDt1cv2HRL0fWf3O4ucTF7A3ek7d4hQSlAy7B4eBn/OaB0dQp13n6qbRq0Wm0kpFusYC94KCMnwz6N9MbIvvhNibR9wG7jWbsRIBm2Eo/'
        b'0gOa4NEIvD11HB6eekbdiZWrDhrJdoa7KzhK9kzgZaZsQ4jsqqTBGppwezTW53fqR7BaZ2pPBS2mLtBRgYvZ+EmMjw1h8h1CI6PlKJ1ItirscyXbKhtL06RoZTAYx6DZ'
        b'yvCaLQksb4rWk2hda5wpXdkyKFU4xpoPT4LjDzGTHw6iddsZgQN6Oz8HNpVF85TQQneA6HzBKhblBs/KJyzzpvdHqmO1pNs7aDFWi161nGkLzm0m+yOlKKaDEZHgGDxt'
        b'K08xlzLmgg4pmDkSXAOjqFYc0Xo6APbhJB5gWub5k303HbgbVEXYYwItB16QQWjZYIzeUtqBpngO3MOH/ShJHfYRLEoBXmTGcGELvevWFIH9GezhY8gAeiQCDqAJWxXs'
        b'QYublWZk4yiJK0eg/gTorw+vge4ieI4kOX4BbKfj5heEh6E3KzNTQnxpBbNjgiKBbRjcvwp/GIEHohUoDdDHSo0oV4c9tOn4bnAYDkUQJBPs30RRcvAqkwUugq30flaj'
        b'JTiAPRhciOGA7lh42kaeUoJDTNCRHU4/sK28RIBh1UoOKKKLcJ8cpYxZWTXwvD3dykbBEdiM0wdqbZV4sA/ljoWydoWlCffok4K1QAmYthcI+uBOuN0N7peGt1mCK9LO'
        b'gadsY4s33Gbr4Q8Yu+AW0FhCwueByys5DhHwEq8UOxtBJaDGTAPV8qTcVsMTsFsQjQTBeHpJ1TUH7CHMYpTeQww4QDJO4ofVctQsHRZoDgKNoE2L6A9GwC69iGh7UOUo'
        b'9X8gR2mDo4ZgGxucXg+kZbgDdMFdAoewlRagVwU9R1Fq8iz/tWCQVALctmo5J5wfWQrOhaL2KeAxKLiTrZ/IXgi6GIQnpp0fh69S+rHwGt49bQqi4z0O2/IieFEUOE/7'
        b'BZFDne8wyzczny6Z0/CQHko2EjmuzcRGw0NSQgG8gCqiVxBmy0OLTXCYEQgOg30pqM+Qz64t8vAKKtoaOYqxFLRxsEx33oS0V76ZrWyPGS1Xr0zR14+BJjre88naNFGa'
        b'5kmPwSq05u6zphvdIbAL9sg2UGEXVhmUutA45Ec6yxzlUI4NKorSyEhwBiVNGR5jglG4S5HcjYPnC1C2wqPgZbCPz6CUnJloFKmHJ8ndHDgayXHg2WJuPLiAE6+Yz8wH'
        b'9enk3VzQZGWHqgl0w6MOYbSTCnWwj7UC7JVyyNESvgtsRa8vjV6MZEu07u1kwFa0Fm6ie+pheFaXw0MNDBXMZtArhzpEAwMNCmc06HG3D8XUPm3vF+VuGFxGSd1KCjWQ'
        b'8kbdAWeYBasY8LwCWtMPLqGjPoA5fxHko9UqsMNBnuKEM2EnKtR9dLlVwdGVgkgeqjRUl0vR8h31JRUmWr2PwDZS7AFlYDuqTBfQxCuLxHQbVUeWIugqJFqoPNBnQ4YN'
        b'KhLFMIwaDSOWDKyuaErZieSoMngRydPgGsPCxRAeXkRi5KRmTP9UAPt9kGh5ClY9xBsMm1QKBdHL/GUiDLpzhhRhEuj2jnDgg8bVM1D38CyLVqethVfBZdzoyiLhNVdH'
        b'BqU8nwm6tYvJ/LYZtoRgt1N7cad2hMN2eMLAydZC4zSsB4fm0tNgBxoGLgjgfp4yOG8PL+Fh/wJWMO1U1Ndg25rAEbo6jq1CpTNA30XdpBpVaDIDDXb79Ok23gB64yPQ'
        b'DLoF7qU9FTjCRhVaZ3jPei7+4lkJBypLUVXOYiwzXU7v0Y9EzEN3DBXL5SkGaMFfBHcW0I3nCA+0IqkJVtmgDgVbGGA/qActYGQ+ffsgaJiF0mwTvhp1wX22TEoBHGJ6'
        b'gZZoMlZutLLHitwxDmvwjkwVaUHqTFYW1k+meSNnYuBZqaMV0KUtcwdTDZrpMrmKxpmLAjK3odFYOpSqgU49cJbtDLvhblL+xRmgj54P0Ixlglt4E2rhBmCILrEDMYXS'
        b'8RResEHPoOqBg6hZOCwgmY+aC0fxPA0OWqFbzGQGH+xXpF9/HjbAawJU40qoynaXrEa/SHhNeIgFWivAedoB4rA5PIF9zBAPM3AEjICTsE6T3PMzxqrU+OsDKsYqJiWP'
        b'Pz8055PWpmou4FSoKqFyNWOADioADhfQ2tV1lbBOAPfa+GK2ixZjjieoI8WplqRMMgJ7ch3CSuFePl4UdLMsUW+mu7pAAZ6S+UnbDAenfO+ohD20QrcVsy0JsdARVvuC'
        b'HVH2vLAoNMzTTiEoT195cAINxfQID7cvn0e+uIDjRqHTvrgcS3mI7RLARdiOlhL4a/M07zczmflwVyyKNgmeV3REDeYoPYIPoqI5xiHP8kvJKD0LdVJjNrrcQ8+vvotQ'
        b'n6iJiQSXQNfURz+1BFaUIThNWngc3wi1CNTVwNXVuKsFM8GZDSxyKwkNWwfwTTz4H2XA4xFgf3kG6fd+wWAE3UHJOi4bStxZStZJBNO42mX1DOZ/OaZpyRwcbZHLAaf1'
        b'yYDlBJuzZYknb5kFL7HAhXBwKhkMkCbjvwrWPXUchJ0GoYH28JTjoEOwgzQLeziqzyHzJgsOMcJAFRqir4BOUvSb4BFNDqymV079oA47h6CYcSEo+7h1rMnLRLNBOAOF'
        b'vMjgLgEt69DUh8tWKwH247wrw51gAM0lA6SzaIEdLLjH35WEhbvRQLGTw6MoxrINBmhShrsVSR9ZCIfTBNGw3xGtOMhYrlHAytsMqpPQiouGuIL6Ejhg7+CAR4FGNMwv'
        b'QtNfL7qLG3JlONjOCQf7rVAPYPIYJi5o2DQjHcPOV4BGf1ilJM0PShDsrtSDtWxvVMStJFGzwIVQDh9lCdahriVvwtQMmUdagl8JZnfizVs+3ArabHFrRv32KJp+TpI6'
        b'nRsMagSOtrAvlAuv8PDYc4UZ6gnP0N9V2xYZwQF+NByKDMtFY8JGBjyCOkovvRJq0XCFNWjtHg2bwI6Z3hvgcXCVVFJOQqnAIbyCp+RgDavQzMRkgsNxqJLwKskcjqHE'
        b'keX2fNBqH6Zug8c2VTjC8kJzdBvdh7rBeWWZEQGxIODA5hBUlAfpb8JX0L3tEQ4mYFsUGqjXMnzRIuwMXU8tOmAUTbk66XhEwuYFWz1JPQRbe9MApjlgL18GYEKd8BJP'
        b'/3+XGYITx/39f9P9M8iXkU8Ct/Wf83mTvkW+aq7j0F81NzgR98mYAfS+gZXQOlxsECHUisBsH8NGQ4m+o0jfUegUINYPrJWf0DGoX1m3UqJjL9Kx70oS67jWsib0jFo5'
        b'jRyJnoNIz0Ho6C/Wm18rN6FnKNELa2N3cto5Eq6biOvWlyTm+qBr48EvKeH7Jm0WnXbtdiI9Pjqjv7tJdMO7siUOYcNsiWeYyDPsbV54LfuuKbdW5V1Tq7bKps3ohxa3'
        b'TavTtN1UrOVcy7inqfOugWFDUGtEY4TUqCFTbOTS5ywychcbeNQumODOqQu7a2DYattoO6GnL9GzFenZivXsJ1lMQ53aBQ/kKTOLtoB2+dqwT0zMa0Mm5vA6fdt9T86r'
        b'jZzQ4oq0nGoj35+D3ox5+yc3ied4PL0+YWwlMeaLjPldGb153Xko8lblRuU2j06fdh+xniM+V2xUbNNuUsc/Ufm0BXWGt4dLLLz6PCQWQcMpYr3gCSPT4woSvcC2gM6w'
        b'9rCurL4lIocAsUWg9HqQ9HpO3waRwwKxRdBdfWOJ/vy25FMG6A/G9c8XOc5/RKnpGzzAh/GMGwXXCybMLI6nSIx9aSuOvhwRz/cRxTQ2GTfDxNkJrkWnUrtSV7KI6yrh'
        b'zhuWl3BDx61QcSxgmKDSMDGXGHu2JXamtqf2WYksPUnI4YyxvJG8Ca5ZJ7udPe2mxHLBcLLEMmq8UsyNRlH4mzzQQDG0pjamdlmJjJ0kRjF9GUMr+1eiV1tctxivhPZi'
        b'jxhUJccXSoyWd7ElNp4iG0/0czhubPHI4puMW+xX2TcTJVFLRVFLxaHLxH7LJw3VFjIMHphQ+gatqo2qqCY292k/ohjWEQxZepJpFx9+Iku/4QKxZZiYG/6IxbQOYtw1'
        b'tcQeHiSmc0Wmc4eVxaYLJuVYqKgUcWTyjfITRsatQY1BqDkZtRtJzFxEZi5iI9eJqc+zIiOnR5SCsckDfOiLG0rtT53gWkm42V1uvb7dvhK7eSK7eeh03PmG53XPm0G3'
        b'Il+NlEQuF0UuF6ZnCjMyhZFZ4gXZd3GQPFmQ+SK7+eh0PO5GyvWUm4m3lry6RBK1QhS1QpiZI8zKEUblioPzyFvCu5x753bP7XMb8u33lbgGiVyDxhPGVwhdw8R24Tjv'
        b'8u3ybeW4YUqsfUTWPmKu74SF7SllCTdHGJckiVsqilsqict+Ky5b7JiDjje1hpT6lYYthgXjzGHeO05BorhskWPOpKqCh8mknAoqFwNcLqgNS8vlmXd4iqw9xVwvVM3G'
        b'JqTb4Er07WL0ynXLdWX1FnUXiW18J5XkUEQqOCKlRiUcESpKVOESbgp6UrVbFbWH3P7c4ayxwpFCybwY0bwYYWycMD5ROC9J7JEstklBDc5sGeOunSNdXj7o3wMWZesk'
        b'4UX1BQwt7F84HDQWORIp8Y0U+UaK3aIkvDxhXLwkLlkUlyxMSZOkZIpSMiUpuaKUXHFc3o8TAYE3dK7rSJsWalRp4oAlkwpsY5NJljxKqgax0WrTfEShltFl1mvTbTNh'
        b'bPa0BRuH9OUMlYzLSYzib4agdmccxMA9SL1LR8IN7PMY8u/3R43KzmByJcPLUWeS8jLRrQ15WMmgTC0bmNi3RhkBOft3ZYgNHSc8PIcK+gtERq4N0d0L7/KdG6InrGw6'
        b'C9oL+ma1FzUsvKtnQhp5RmdRexEuvIWNC3Et4P5q3mvVbSXmOuNzlXaVrvjelO4UCT94WFXMDSENJrTLpdez2xP9GGaMyY/ID5eNrRlZI/YMJdlFlWJiITEO7wrqUUR/'
        b'hrUkXuEir/C33cMfUYrGJqgWJLGLRbGLJ8wsO/Xb9btyRGZuuC7Mh83G7EbssNcdNBT16Ygs5kosAodDJBaR4zmoMfiY48Zg3qnYrjhhYdkZ1B5EjztCjxARL0TCS7zp'
        b'dsvrVS8Jb5lw0TKxxXIUxIwEsZRwnURcJ9QyUNda3L94nHGDfZ09nigJThIFJ4nnJ4vdUybVFePQsDSbMuaSgagtiNaRoUelWWMGIwa4PJTblVFncet262NLnOaLnOaL'
        b'7QLE3ED0Km/cVI1NWoMbg2UPuvR6dXtJ7IJFdsE3XUjSIpaKIpa2KQu5yyZZyqikDChzq07DLs23jfgSo4V9ZkM2/TbDLmM+Iz5il4UTRiYSI1dUhRKjFaicOSOc8YAb'
        b'QdeDbs6WhKWLwtLFQRlizxXoKTwltcY0xjyiUOn3MXDnk9bdhKVd5/KuColFPCpb6xHrcXM8MN9wvO4o9o6XWBQKk1MkyWmi5DThkmWSJbmiJbmSJStFS1aKkwtJ6U2y'
        b'2M4mD5RxvkIaQ2TDYHxnWnuaxNJdZOku5npMcM3pmdcVjfNoFENljg8oxUojSmickFjkdpVhzzcSxwCRYwA6RZNH3vW8m2XY5ZIkJkMUkyFckS3MzBbG5IhDcu/iIAWy'
        b'IAtEjgvQKepVCq8qCGPjJbFpotg0SWyWKDZLmJ0nzMkTxuaLQwvIi6K6SntXd6/uKxta379eMnehaO7Cm6ybs4VzI8WOUbjNhLSHoFrx6fahR1Sxhf+EjcMpNFPmC5NS'
        b'JEnpoqR0SVLeW0l5Ytd8dLyZOBTWHzacNe46Hjic/45bqCgpT+SajwYyL3M0kJEKREUT3hguLZpn3uEjsvMRW/jKitKYFKUpvYJwR+sGiVEO3eZRiWRdz0KNxOdVH0lE'
        b'ligiSxySLfbOwZWLKlZiFIWqVb5fvq90qLy/fDhwLGYkRoxy5RSF+25oY+gE1+ERxTEz73Me8uj3wMmIbI+csOH1srvZE/b83ojuiAkn5yF2P7sveUAFJYjvgJor30di'
        b'HyyyDx7PEttHSOyXkq6ZLIpFw9sScexSNMTybFFv5tmSkbdYbOOHuomlFeollvYSixCUJtV+1eFcsVPIpDbHzRynwOOBDmVl3ZnSntKVIrZ0n9RXRePfakYYw9rgERXG'
        b'0Dd8OAsNWN8FMCnTOQ9y2NQsA4kGV6TBbZuFViCh7aETWtr1C+sWonUWyrdYyx6fh9WFNRY1lYi1HKRnDVltS0QmzmItF9mFnLYNIhNXsZYbvhBeF44XQuxGdkNi65LG'
        b'JRJjB5GxA1kpGbWqNKpI9HgiPV6XeZezUI/fpzWk368v0vN+RCnrm4y7X1lLfkhnpne5ZmjtyGvndQX1RnZHSuz9RPZ+wyuGS4X2ASLzwPFMkXmYxDz5Zp7EPEO4OAOV'
        b'qaUVbgHSou9KQOOmTPEqWOQeLOGn3tS6ZfSqkSQsVRSWKrZZPGFjJ7GJ72MPqfSr0EMKOkWTdvL15JvBcCka8i2tJhUUcANSQkWpoKqtM8nRtJz9kNKcpfmdDTXLuCHh'
        b'bQ2zCV2D+nV16w5tEGrM+en7BWzKKZfx0/fpTMqtgCFQQ2vwv/ONA+YrOXxniP6oOdEqU0rPgwO9WB7ASknpM9b/Zc5sdHBBByN5Ka7/py3UowonBmP299Rf5AedpjFb'
        b'y7E+FeZB8uQJ6+oLnPrE6OhoHhsdyjowk0vteaDHMgaDMJMSFoQGRwUnELQjzTYixr1vTuEZSaIxmbGsCr9Gu6z6f0qiwltT818MYMxnSQ+YHSeoQdn5aRf1HZupqoF6'
        b'oXk8Y8LYfcIMrRrsvlOSs8D+qsg1vwmzOc9eCybXTKeu5aBr/AkzPv2c7dRzz14LR9esyDu80TXHqWvuz1xLo8Oiaw7o2nwGvmjEn9BxmdDhf5fPcNdT2xP6oJhBqek8'
        b'ZGJWIgv9eoB/fW+CgYgpQrsY0aK0dw1NuxNGNK8LvmMx1CIZd0PCJwKCH7F8VLFROT5OyuHrD9j493frGJSW0bsa1hNaQd/JMbVCGHuCvlcksXVn94d0Lbue+aq7KC5R'
        b'lJQqWrxUGL5MGLz8XQPjbteROSOZ1y2urxF6xU4Yu6Kgau6on4YwUL7CYh6xFjJVDf5J4eOkArmFfz6KZweyVC0eUfj4gBxpXiP5XNgXvZjgGmmGhZLMKINJ+S6Wj0iC'
        b'1fAy7J+h7MaR/p3MwdRGzT9BbWQnKEl/K0/7zUG/VRJUyW819Ftdel1j2m8pwdFBaYrOqP1COiP7uXRGHSkh0XSKzqj7XDqjngGVoJ9g8G+kMxp6yZM3c6fYjKpucglG'
        b'/wWV0VhKZTSZRmXM4ZndVifQ5Pyy7MzyoOwV+eX5/0CD1Dpd5Wcu/0UeoydN8nLhMW+zF8TEB99mBboElhXjrrsKH7De01+JyxnF9ZdoitJAnn+dmCh7HSELOWNiYtl6'
        b'DBhgEbZh2QasqK4cHxwVkxhMSIkWz1AKE4KC4rNLZ/K9nMo24Qz/mUedp3CCsoT8rPeiWKcYgzPTzFOaEQeuh7IA9jRQoaxwyhbgQT4Q33rRO5zLqnGu//fxgnnP4gWZ'
        b'1LO6sXJSvOAxuA2cArVWAnhpys/BgrW0tt6AsS6nshS0RGLy4B6sDnuemZ+jPIcl4KHbrOU/YvCgBtDAVH/9c+avC/T0Zuvr673V2Hc2NuNupAJ18md2jvlsHoP+5nR4'
        b'CdiW5jzDuoXn+3tIIZlhb+s906dmwgnx5iqGE2Z5TlfznzDkynjgGtx/BVkYjq7NVpiGLMzw/BeQhWUHWP+HkYTYZ1Ap+0VIwixS4pgphy3S/wqPUNZ7nuERynrb7654'
        b'vpBHOLODyniEL+rX0wCCz+2T9P0/4AM+y7qgzdozirGFOkZYSIEOU49hxy2/YwjOKDcpNxCP5TQbEI3ntjyHPwv0k73pj5B++Tn/ofn9z9H8ZC3S9s8z92Y24hcw957b'
        b'oP9/StyTi06s8MPTxE4u7IwueT7aDR6E+yJpK+nQp8aeYAzu5sCOWbAmP/5WHkOAje71MhYMfKzGOfY3jTcolpmKmVH//fnHeDtcd/B3eO2w3OG34++Hjc3Pjmu8rgfq'
        b'IDvlDa2XXtnCcGsrV57LWuBmHenW8OrhWSA8OzL37usU1Zqr1H1kOU+OfHazCYghlormi6RMNXgthHztg13aK6cx1QpgHY1Vw0g1sMeFfBtWBH3g2hS5DAzD7indQQsm'
        b'+UwK9oNLmRHWyYQbhr/q5ajTunDb1OEZToQPbPqdfWkAaOIp/wvCI56WnosS+/3kO50jFkJPvg9XeVGzdGpL2spFGu59ucPl48k3kyY8AsY9bnpiilgSg2yV1rIPq0rd'
        b'Vj8D49Kb8z8H4opH7UxPYTqIq8jzXwJxlbWxnlnY/VkA1w4eI7rsxB/gt35X6jL2ViBK+DT2lvkLJpzf8bbk/9h2LVNhWgI5M5YocjOXKChXStIlClMK01LFMC03jnSJ'
        b'ojBjiaKIligK05YoijMWIwoBimSJ8rur05evGV+z/0uQ1nSJ6/8kRWsmeVi6rpCiqYrQzIGZRf8Ba/0HrPUfsNa/BNayn1p9FKKRb7rX7L/E2ZrWhf6dnK1/M21qNk2b'
        b'CgGX+VOwqeVJmDfcCTpo4LAnXj0cNgPttOpqQiisiuET81bHuNBwuI/4p07BWF7FyhB4CltCYuyFErhcFk5buB5xhcdmkqQqKLYUJAVOJZIUpC0EV+BxSwI1lgKNq8Hp'
        b'Ciwx50WCazLFQru4F3CBmdget78ctirBK6BhdQUfr2326618iseBe0LtaatcuCcK7gVXkiOIkvdya8UAeDi0wpEiKoKt8hHPrAutwC7M/LGH+6Ow3j5FxXMUULYvgG0V'
        b'/hTRG+9ZAWtQlDi+pNgUfnIKBheFR0WC7sRQcC40yoEfFhUHRj3hHkcmuMBxATXxCZQJOK5WaMwluRfAljJwHNTS3h+x60e0fNxLksQMmP1M5BjAs8qlDBN3CAtr01o2'
        b'lQ5qFMCReNhb4YyTNBoYnyB7VFpTiTgIOAjrSO7prKflKIAOuB220RszuxPAMKdMTTWlmEmxZjH8wAisp80o+8FIKByAQ6sFoBM2YDvhMYYdn0GMPC8rylGK3EzsilzF'
        b'cJMTlX+7tkFOoImWISM/8poTrhYDJ415PrVPtsRqBO5sDzRedCY6df64z0u6SkrOp5hVO1WW/mxxpaQ3+mM3v6EzD1Z89c0vPq/dCZk7nsf4vP1QmHBlasmqcIZQdNVC'
        b'4ZrBr/8ccFzr/+3ksdnhHleUhW/41Tj8enMWw4h58m7WiXnNO7/U7jud4HXyVAv/5Je9d7o/TFqVJheuUZZsqfxdzaikjFN34/h7D/6mS/lsK145ftbj1KvzXB5vuuH/'
        b'qVHlerGaP/edhoGWpSs2pbSsev2rppabbzm7Ov6zPGF/bHtLR5PlZf+axm8cb/gJ9j75buKLH8edDSfNw9eNHWg7eKnsjN328BO3zsCzmxvm2k7AT4ZPftCxXDtzi9nP'
        b'O1+/tum6Jrtevfxnt49TIngaNLOlFdXwfoysgTvByHS17lQG/cCuOLVngTU6YBAeLYf7aK3p0xgEddFF6hmdEQB2gSNE80/DDp58hiijnQQ74AEzWpxoAaOp0zHIqE1U'
        b'yzyMn9xIm5lUg13OU61OjuIUM8FpLhIRzoF+Wpv7tB04zwX9EVPiBLikQpQES0xB1UxgDqh1h+cXryW6rmZRsAccBbufsbiaMrcCLXm0imQzGAM76FyAQQPc+6vQi9Tg'
        b'KCsSXT9GVCS9sA9KWMMPj+LBbSyKPY8BzsIdmvSu4JYwMFIMr0S4hOPxpJdC487OLBIM9HLBRXq7sGzKQ+XIAlJ2PqkZduFR9AhjB/ZaMShNaxZsAhfn0Lr9mytlNBlw'
        b'CVwkUtoRsIcAb2wzSwlO5vcsGVcPTJOB12ANT+3f9H0Of2qciXGZhnAxfXbB/zx+y3qa2vxdkM+/wG/BJBHT+s11myW6NiJdGyKALRAbBAm1gu5qmhCYCq0INJ4tdo0g'
        b'twPFBguEWgseqFCG5pjEUquAWSb4jp/YYJ5Qa96EpkG9T71P21ysLdhnMWTfby9xCRS5BIrnBBIdTNlzuiYSXWuRrrVElyfS5ZFbccLENEliugj9s04XG2QItTJIdHU+'
        b'Ik1bqZTYVt65tn1tX7DY2ut9E1uhXfBNhVsqr6qI7BLFJklCvaQJY4vWtNa0rsTe1O7UYUsx3588FnJTF38GF9kliU2ShXrJdw3NJYb2IkN7ieHcPh2JYcCwR63iXcM5'
        b'rX5tpbWKn+gaNSzvyhLpLhhfeDNZmLREuGzFRFCMMC5VmJY5yWLoZWOGyazs6U4T1f4MD+S//vRN2sRM9Mc07kcemvGDsaCKGfdPkJy60JvBCCPYj7D/npz6v8f58Psd'
        b'5+N5otu/CPngRlcEoN/rQB3rzyA+QAfYO9XnpxgfXNhMu2ToDHeRMT5cqQon0EetWODH4lDmsIcFd2wCl8kErAivpdDOChx0pWy8I1q0b+vLBbAbs/DY2MLvIgF4KDDJ'
        b'9KtjhiEd8/NZVHrhwvkcijw/K8mXIDrQiC6ldIxlo1UX2QjaBev5mNGhDo9hRge4HEpergEPgbEN4JyglIFXThSoioNHaU7CuTBwBiM60NjdTDAdcGtZII3vuLbIiyA6'
        b'0PBaG01DOkBNAYmw3Bc2wrFsKagDQzrgBXvaX/VpNNJvIZQOuBuekJI6ehZx182SD3HHK0Uzc4LTsDVYS/gJ1vCcKuFlTMEy4JZswssIsieF8Jn3AcqIsSiTckovFqyM'
        b'pIEXqSWYl5HurUqlB55VNaIv8lTDqFrqAV8lPb0gxDmbvvjFMlVKj4p1UIxNL2xw16Av2hphXsa4QJ2bbgRXraR5GX4WaMohuAwreHQaMYPwMvZJKabwBKq5WoLEgAOm'
        b'hIrhA1vgARKtARMzMea7o2hVzmcwKSnDIs8aDAii8SpgHRgk9l8npBgRUA93gybCsMiEgwRj4cmrJHUJz/nryVkTggXBV3iBfjrIgLIaHFDB7ArYakLjK9b6EHoFPG5s'
        b'xyGGdccxv8JpAamRUjSpNtD4CjTNwlPwMsZXCOAYcVseLA8v0vCKMHg5UgavgDvg/vwf5xvKCf6GKvjsx1FXF/1Skxas1fL++01Zj4oPnn630PS9tywvXRwsfPmt2NXZ'
        b'2l9lSj66XGElcdCpyzPV+uoDEB8UFKAVpKV1UW5WjaKysnlHdWBadShmWAQs3vFY6TEn2kNQYvVog8CnKm0y4mDJmz+9Ofdbwb2t7+u/0/NO6sA7N/uO3Nr/pq7PR66V'
        b'izL2VkW+vclN3FO6u079kY3V8Zt2WRvXZGf2RtY2vhpUvfjjvVENa77fcmPfWqN/7Hz33jFvzRE9QdORyrG1W9e94rFMuO9ac//42aaPfuFumvfRrJbOgXvbljQsnzBY'
        b'cyX0qsVi+eqDf7NYuNv99bkrkzy+utV8eIwTsDXl9Tv/EH709qm9+jkdS91fLl7z3Xh1s+Ena1ULliiIVCn+g33ceKsf3o1MCw5Y+WHge58aRcYmpvGi13fsaXcoO7Vd'
        b'5caV0tccPii5WGSZeUfO7afrwqzohJY3+1Sd9rKhn4rJh9HnLC5rnhilMp0/esvTuujqpzbfnLZJv6LrpPOjyUBvRmHO248/iPBzPzv6d8VvvjppusX53QO7DAWR1x9H'
        b'Jhy+FRt5eFzRT3FwHnvwG4VSk/ZFLxU/WLN3xQfOx9+4aJJ88kfP2NMHfjhZEB27l5XvvNgnccfaguxb1g02ox/UXUz64dSRC509Rxjzugv3BaS+5NjzU1Pt2Edfrvy8'
        b'1t2w4Zfz0cOT30TovxZcnfSu+PEFgXpa5ZnC4r39Hd/+lFGg/ePVgdXCxuW3Ghzn8H3aP4ydux5Wrf/R/u6DHwUaRXFvtz1ZW11nXH3rZKn7gYUZPZm8Kx/Ma97y5XJ2'
        b'V8ur9xPqlm+7ExF7IPvDlxfHVbyqmDf3H42HB1dVr+i/lzt7NL3pS3hhcPG42sPgK50p21dn1GSta7z0cYV1yKvnAm79nLJledTKzX/3OBa0fHvX4DK45kq0c9SHhrW/'
        b'RVW/dd988aNX4gy++M10P1uusenevaxlejrvVYTEflLS+Peq/vy1BoNZj2u+jn7tx87HqV2KOkf7dv6t6rXre8xKNhqe+Hb+w6VbdH5an/PbW59t/HySERxW7B0erfvb'
        b'S2uA7epj8esVPjtytjmuYv1vZukO3x+w+dutxWnbJlN6msqyLh5g7L7hv/XzTqc7Xhrfum7ZGO18TrL8V+tvHBk5TSWb5O5/dPt0XdSE7k+St02y3v8w1u74yytCTmge'
        b'kPM8N3i1drlo27dfRYR/NhRrfVlwTvul2UrOyz6/+qn3etdV97/x+2XNbx+s/23yztb13/pmwbOs7qjuUhWTs4s/1luhsuTjickPzr/i7KSKf6kmf6z3o0JP6f3P7px+'
        b'xbnvt83ub8qNixbuyxSWxH38fo7jxoXORfd/OPPuY8aXFz/8mKssfJR55ujnHpcVB7cUyrlu07zv8oCfX3er+2ZK+iet3J9dg3pvF+h+VfXm7A2aH84v2Zsc/MVV+ftz'
        b'ty3+p3dsknlltsY/dO+mRq8rWJ36yaOVZ5Y//PrR49Zabfjr6Tcdmv75Wb332DbfJ6oPxYfiNinE+T5WCM5e9ot18KD297oPUtOse799Rfejwo826o4xR5XOGsY+ad7g'
        b'F/St/IWfy977YW7+e7/15H7wQfwAJ2bw8taTyy2/juK+0vnZ+Ohjq3ifom+s3/ui++wr8csWPD7doOP1hus5puTktyZu6768c8tqtVX3eyefVP0SUaB/xH3d+VHN7UZj'
        b'cj+fuDb0t7Q+gaaJeJOq8RPdy8ydV7bM4q0ixnRL4H5w6vdySmkELanAY4m0gWcz2I1mxyn6JhhdR8gQOrCbiFKaHvDKlCOYPLh7GhjClETAhrtTMRViiggRDKoxFAKe'
        b'8SSiEDyFRI1rMpYD3yEUbs2SwRxAG9xJ7M3moAG6l+Y5wAFbeynPIWYlLc3tiQDbBE8XMWiAH+QQoEOy+UMb/MDFYniIpjmU8cIdSsNsYf9cbMMrxTn4gB3yYIDhSlvd'
        b'XkNi6CBtbx4KhuxooAPsgn1E/ouFQ+GE2gCG0ZyyV4ptWC015ePCc7Y0tiGCQYE62EG4DfCKCvmKVQaO0+wCmbVeA6gi4AYwBOuI8JoNTmZMPUDsmEEDPEiTG7ThIJFN'
        b'WXK+BN0Ar1UQegPohqc4tB19u426FN0QxqB8YRNmN6C5nHZddCLQ9znwBnjAtxweRmIvjkAbVCsReEOHFt4HouENjWCUpH49uIKazBXOFL9hCt4QBI7TJue9mnAAidv7'
        b'pAiHp/iGLNhFf407h169Hadxit0A25YSfAO4upQU4VK0EByj+QsYvpAIjmL+ghvopgXzKls0tXfIEQQD4S/MAl10/qo3PA+/ANvTQGMpqCfybR5ssCeS8WzQJBONl8Ih'
        b'cm8VPLeGE81XAdtieCjr4CQDnod15nSyz3ujNR02tn5qaq0qIMbWx+Bx0p3gUXBOjqAdULDep3gHmu0AB0ELbbV/BVXXoMAhTIZ2ANcqMN0BHiggVp0lwRwCd8DLcFjF'
        b'o/kO4ICWCZsN+kEzvEC30b1wt0EEL0rGcQBblhGUw7o46W1WJUYeyCgOEaCNgBzmh5CccuCxldiWFfa50qa8YD8cRQ1Yj+6Nl2G3CTwuJTlgjAPogSfoTZutsKYCnoic'
        b'uf8Bz6OUHaYtWXf5YYgC7sjYGpSmOZzgSWEIcCfoyMWYhWdouNou8+iyaWLCE6DTRwpzmCI52MEx2hR8n30wITnwGdRicJAGOWxzIG+28IJXpRwHlOw1YARjHOBVSFv9'
        b'5sLqAMxxkDEcwGFLgnFYZ0Ii1lgKD2KEAxgNjpYhHHxAB53oQXBMhSY46KXguKUAh0vwEm1oOqgmT/MbFGG/FN9b5EKizQBdoIPgG+ApPZrgAE7OKyX3ysLhFnA8n8Y3'
        b'yNgNqf7kldyy2bB+/hS6QcZtALVS09l8FYwg4UktrWEPExtb5/Hp/lE3Nw30JNLkBoJtKETDBq5ZTbSeraW5DWitS6MbDEEnvfGTUOki9da1L0OGeYaNMbTF/DXKm165'
        b'h+aShXs9PEbbNYOTy2a4I6sFVwi5YXsp7eerGe5aHw8b6LTKrMnB0QrSYeZEF02BGzC1AZwwmQ5u2AlHSLeujAM9hNswR3sGuQFjG8Bhd5K1zaA1XUptADuKI6XQBj8B'
        b'UQyYy99EGM8UvGqCgQ2r4TDJsi/sNyfABjCIhBya2AAuhZFKDYJb5fA9FGiXG81sKAPbSKYK4QgaxAizAewHZ6Tchha7bLoD7IRjxjSywZZJgeYMmtgwYkEjD46jwFWk'
        b'6x0F+5VRJ8J71YMowXqwj20Hd5mSOrSLcJ4SVVyWYkElFVaRqtBRgKP0lqQlOIx3JTfDPWTkTcDMkFzQypHFiVuqMjjIBD2m3iRLi+BWuAdFy0sABKCCJFnzDC860W2w'
        b'tTIe9thNDVqYE7EAHKHtzGuZjgJ61lSaokSAanjN2IcN6jajvknGjdESL3rqSQSXImWUiDQ5GlmzF+4wtg6Y4kRMQSJQbx0gqQuzBcQxHZ7wjggwJgKFOUjWB5nWcFhK'
        b'icCICD3Um55SIkpBOz007AejKZgSAbfAEUKKACej4WUaizAEd9jQ75ZyHWC3EUE7gPNo4sLjg7LKuqkPMAwqGW6jyQ7zwCWCpUrOBTVStsMxJVj9PLbDPA9ZTgc0n5YW'
        b'3nXYxloMqsvBVVBFsqMGDprjthrBM7FAcfHCpGsBfbCVvRCcMaS3aQ1hK/0QyasbaFOAx5kBZuAUPQ4f9wOXMcZhahiGw+Asxji4sWnj+MvrQI+Dycwdbti0Ca1hcGk5'
        b'w9NoKsEby3CXQLqxPB9upwfh5jl8AXptDGpKB+zQGKyxluUGT23wA1vpgTYS9NqhJoiWa1EMygzWKcJG5nozaW8FvcngvAAP/1V4YYmzxqBmabO8YctGL7SOIB9vtgTB'
        b's2glN/bHhAsZ3kJtI4nZFYyCnb/DQzig8eQUmjS66b150BuEpoTjNCxGRooBtfSWuZ9JLr4Bd4GjNL4I7IsHu+iR6sJCtGghociQunUVQeEcVCPd1mOl3xTAAp7Onp5C'
        b'ArCQLyF1n+gFen4H30gHzeAkPClH8hCwBozN5FegmnFbQegV5aBOSlYAA6AW4ytADZ8mWICuNCm9wiYJtnGm0R72ghZMr1CFW8jwkFgA6zC+wsGbBliAltw5dLPs1A4n'
        b'9ApMrliePY1dATqcyCipCLbqba4k8AqCrqiGDfT01+sIzjwLr3BB60RLHVJybrATrW4wu2IZbKbxFeAExGgfMhtdS4PnOJjdgi6NYXoFqMmQfqWBPUkYX6HtPQNgQegV'
        b'6wroT0ComJUxvALuWBNOwys2L6VTVYPm304pvsKWQXmDkzS9QiefNPCYMHCWZlegati4jqArOPA03Tf2wDOwkYZXwJbKSBm9YmsQXVRt8DCPpldgcoV61lN2hddKuodc'
        b'DEDj67ANja+YgleAI2iNi2OIgWc2S1lxUnIFajlXCb3CVoEkLxjuZMjQFctBPe3/UjuJwLtAtU1whEOUPAW2RWBsRXYxKef0Bag/ETgFn0kcHtB0ipw0ns7/MIwCd6U/'
        b'IFEQo67bOs9+opnGoLBQpr/MJPr+dxkUhhI9n9/hJmrlHshTXLN/Iz/CTqRnJ9bj/3l+xPMu/Tl0hFaT2r8PHSF9idQytS2uM7E9scvq5BKUW3wN5b+LQYwjySehs+pi'
        b'I0+pBXpbSGdMe4zYyO2vgRuekgDUGtUwt6F9s8TaX2TtP64sto4Q60XiFP2HwvAfCgNKqhpOKm7yOmI9G9wuVBtVp+VfyhaYZsGb2Luke4mE7yfi+4lt5uGrSt1K2KR6'
        b'YffCvpCzMah8eLaTcnKWVpOsKStdFkffYDKO4YY5DW6E01D4X3Mauv6Q01DcXvxXOA2TcixUbYr/bZxBeGN4Wxn+wiuxDhBZB4yX3Vh7fa1kYapoYWpDuNBosbRH48hU'
        b'21Vx2YW2h6KkpHWnSfjzRfz5KEEifrDYIgTfi2iP6GMOcfo5EqcFIqcFEqdwkVO4xClB5JQgTFwmdloutkiXPacgtvCcVJDDRYr7pAZlbPpncAjGpq1pjWmtyxuXS4zn'
        b'9i24qPCIkkNZjhtLHUmVltRdOz62z+/17/VHTc2a31nSJyexTBh2Hps7Mnfc5YbPdZ8b/tf9xT4JEssiYcoiScoSUcoS4dLlkqV5oqV5kqWFoqWF4pSiHyfmB9yQvy4/'
        b'Xnqj/Hr5zSjxwsXi+Wmo5HGa5eZhEMZ/wAn/ASf8N8AJqQxvzE3wlmETVjMwNmET6/8aNuH/27SEChZNS4inaQnYabtQzXgN1+FLyniNpcO/lZXwHjrsUZjGSojy/ZdZ'
        b'CQwZJsELRfoFVpYimAQWxiS4oUs8rf8JsoEAi4DPgxrQuZ7Llh6w8bVg8XOYBvbPYRrYP4dp8Oy1HPoaf8I4eIpfEDojPv6LrmFUgRNGFcQxeARVkEyjCliqZlJUAfr1'
        b'vTKBC3TNuz7nBaACSwIqsJwGKsC/v4ueAhV4YlCB91/nFODXxDPuBodN+Pg/YvmrZjO+p/ARvyYevQb/fhTILGRiRAE+PiBHGlFgQUuqe8AJAimAVfbhUQ6lYVGw2p5B'
        b'2YAxOdgBLxdxHGdo6qhJ/05ewIQC7efxCcrkpqz8sb2+JrHkV5Ja+KvNuKo140z56ZkTy42VwPZiJlgT4xRsmoJNVVSSVJPUkjSSZidpuakkyD1j7y+/BL01Qd6ASlBI'
        b'UPRilimScyV0rkzOlcg5B52rkHNlcq6KztXIOYecq6NzDXKuQs5nofPZ5FyVnGuicy1yrkbOtdG5DjlXJ+e66FyPnGuQc310bkDOZ5FzQ3RuRM5nk3NjdG5CzjXJuSk6'
        b'55JzLXJuhs7Nybl2kpwbI2EOoRjokN8W5LduEoVKiYXKSD5JMYmDykgdldEsUkaW5Am9BKsy/VyWUg7P5rbKgoCoxCCpdlb+XEWKyrBCo4QyNg2YfovGHUwpxpeXYB/S'
        b'AvoZdxd7+q8r8dCMf7kpyzS+BA7cgGl2K1IzDmJeKjUOQXfLs8uIk+iSyuwydCZQnu4k2p6bnZGZxy3LXlWWLcgunhZsmjEMto5SfpEGvoOycnQJNngIy0EpJEpqq7PL'
        b'srmCihVF+cQEIL94mpUtsTlAtzPQ/+V5ZdnZykXZ5XklWcQ4EqWhpLAym2i5VeBtgsK12F5hhldrbnA+MRWwCeBJbbgK1ypjWwKp2QpdaI7SMpOVlD3XJpDHlT6WwRVk'
        b'Y3ON8uxnCxSXsc0CHjbLzZhmtiI1KCkpy8/NL84oxPanUqQmyh62lUWZEAgycon1bzbtmRvdoXPGzcpelV2MMlhCJ5DYo9hI7wXiWi8qEZQrZ5YUFWHbM9IGeA7K0Tzm'
        b'bdaaosLb8pkZReXubpmsZ8YGosW3CR3mqdDGZkco0i4VUP9lEmMzug+rozarkcRwU5OqJ7ISpxmOFbNNqKRp5IQk9gxFRFYAm6gn/u7qDGv4AsZzrOFnNPBphvBSQxmU'
        b'M9pGZlFUpNRIhLg+J+GeqjSikieGSag70NZLNtl09b+ob0yzEifF5o2NjTMzUG9KR69Mp41X6MBTgaY3E6nD+IysrHza1EgaL3d6E8ENqLQiW9o9BBWobU91Sdqad4ZB'
        b'Fe0XHrf4jIrykqKM8vxM0oiKsstyp3mBl9oBl6FesKqkOAuXCN1vZnp1nzFJKFDPqnOaRAvw3uNcw68GRCn7H9nxzpTzXuVdquG9c2GrgMrfqNgR8yo9K9mhQxTYHQUG'
        b'YJ21KxzCn2HLebCKBy6BGvxh6gKgQ4AOsBPUE8/FicT5mSI4mwPOylHUJoMgahPYAYaJwt+pSibFXY2NYtMjP0uRp8iz2uCaHRhAw54PHF2LDoMRhT8+efJEZZ4cFRqC'
        b'lm3z01Vq0o1oj2tGBmCI+EGGh12dmJScF2MubIyNXMxjEo/JLuCUtgBWW4MaNVi1mtbiiIx2ULK1YVAu8LC8HbWMVhY8rQoPwi2pHHyDGcWYmzNPGgO4BI+DbhTHVATK'
        b'+IPjARM+gzL3ljM3AHtoP2B7PEE7B9/H++eXQZcqA3SrwToUDTG3aY0BHdNjAbvsysJsS6N5sN8uLMIBq5IkwwZFIzTl1xG1w5wVoBs7FYcDsvuK7sziONjFYxE3aWbw'
        b'qhx2vM2Hda5O7kxKZSOsD2SuBOfAVqKYCPY7bnx6X55S2RQHupiFprCeBAd7NV2f3mZQKptBK9zJLIJbjSswasQvFxVsDW0dE4qfiwuFVcvB4FNFmSB1BV3YUUSUeA3A'
        b'MOzBW/JgL+iHVXF8eIlsyWuC/SzQCmrBhYpgXAp7/eKmawxjl+jBidgpOqyKjIjgM0v9QLMRvAqqteEFeCFCC1RHcJQxzzw8PoHKztGY6wQOkYZzOlaOmu+jhRuDvZK3'
        b'JlWxGF2cU6bybOy0k/t9juFJoDrMBlaFwr0J2DYoIgn2TbVeoqwcEyY32xIjujvk5OBIsCXo5lHBq7VgMzwCR1CZk28Sh4qM4ID6qjLUSOCwFrzKsOKVkzYLO2zsOYpl'
        b'lajy2WkFDFt3dxIA9kfpwwGVUhKgB9bMZliYGtMUmB54HF4UrCIfx1kqq+EgIz0INND3toNO0C8ohRdUcLgt8EAew2KuB2pKOM7wbF0BvESiBFfAbjjK0LFYR2scn9EG'
        b'F5++DlxaxrCYBbeT+lZSQRUys74PGDGLwB54ucIDh90eYTTdj3sUPzwmKXQqAC7McnARlSfYAgdQcy7kgC6tVFL5/t7lz4aEI2BrEqqQ9Wx4GOxWpX0FnkBr1s71VgnS'
        b'ekFDkRIDXjVdl5+1uocpCECz1Xffa/895b1i8XyNpZ/dG65863LYbbdPzQ5HzEqKCG7a9lbNGmpHbfjL3yw+oxioxUwULtLu2lKrsYH9q+ZHO3v/0Zxq7VN5+asCw7d3'
        b'W6lfuuEqePP1lg/+WXxk8+xljXOuXLderD/7t/P/dMzqDVdsPa0Tt+n1Ffp38rJ/ibn6SrTly46vlYX5z3OoXbTMfKcF98qmLXWMdi93zqB7I+dcgNbAZP684IelO9S5'
        b'GZXLOoNVD569vVjPWevr7hbH3lP3jCV9hof+H+beAy7KY+sff3aXjhQFBekdli2UpVfpvTdBmhQRxUKzYS9YsKBYAAsgKsXCIhbAAs6YiElUHtE8izFqYhJjmpp4o8m9'
        b'Sf4z8yyWJPfe95b3/f39+FmeMuXMnDPnmXLO93xTMKCnEMq5f+6DfOvU7PeqU3MT/Penr/ORWX+msmTJIv5QKFO1f9PzO9eMTRmxz7wbR8qOd5wxK983m5n0YUFcxYbp'
        b'Nw22LWmJWBApLt5x3SXVWzw+O715df975qd4e91cljq0uz1YZ6ylxlvnsiW/m9GvGhUuGAG/fqDdrvWwyyA/7dnyWVunvMNcsyh8YQZ1T559fLNjMbPj/GhwbY5CyBcj'
        b'P30aPv24u2t9zJY5f7l1d67GX27pFl0bjssxzYi7PGd2iaHBR7snf9cxy+2di/nVGq45O1/Yfnrvtuw7w/wHm73GP2wp9ds3/YPqtp88vI9tHcj9i51SSNI7a2MfbG6+'
        b'PsN2s0vi9d8eb7mXevzbOKkevH5rsVD0Qdyx3SGRt/XbDbyMtj6zP2aRv/OoSa977JkVl6sCua0T8jecbmTcRT+Hw3SzmZ5DL9+ZYG7q/Ky+5Deby1uSNSxPr1x8eYnt'
        b'aenRGa1xLm4xqIXqQ1u/vm92rq7xl1GV0T2HJy4eiLfMtfoVhPeuijpnsJkx+Oii+Z6vvCZvvqv2lB+wTrxs9qSjLwpcE0IOgtNrV8wcmtWp8cvHR7dfzNN0Mbn+acEh'
        b'lQ80+1d0/vzJB3lrnpU/bqmGVZLs96JvF42Mbk5Ruu+6Nd7N8KusR+H3nmUErjM4PjTZsquoff9jCXN9CVjh8u3SW4vCv81dMHy9/PaTuzOVmVrzb3Mr3/9UdWH5dw9H'
        b'v4lL/klP4+AXf91/e9uKgbC/Xk1b6q/T9Re6ePhR3XvFw3ovn+9tzDoQtMRvH++vtKtfT2PCdeP07Z9U3/6hT+u95crv/bho8rvv1n3Zoreolbm137Szo+XJjeoUm5LU'
        b'bZb3jn82oeqosqff0eXav2Sd3qQx9xxz/6N7g/dHf1P+8t6HydVF/ABymLvQJ8IbnBaIY7hIR7RzotDQ20aOTifqxYEa0IVVIlKU2LdNHZzngpY4pI62wtMksw/oB8fg'
        b'KW1BRLQyyr6B45sdSI6Xp2MUDrBNk0TGkptRgkZ4iLwUWcN2HJGyM44Fm1LK5VrAljHLu5Xz1JB62FiV7hCHHcSWc+0Vxc/FFDF6WQnWoIzY6C5aDDbGgYvFJAQU2OAQ'
        b'LrQnaCTKVA6aUhy3m8SestaCI8pvWYVqOYJusIFXBI4ZsUYpA+UzsHnmAGyPgFtESpRSNtcSdoJ61mADHgc9UXGiCCG2BFAHp7jgCBeeB11KpHhTUAf3Y6vUHOu346aD'
        b'aniRtejbAuqUiZdgAdz7NiwIbGCji9jDLbES0PjqHJmcIrssYw0GOkEvYkiPCG4eh4MgyA+RS5RYY5jzYJW9IAK1lkMpFIHdoIcDq8ERDnERzEFfhk5i+tAJ9o8dM5ND'
        b'ZgO4T6EUMXEXqT4YduewFqCrYTVrygX7YTspYwbSyCtRh0fGRInwoXAsLkEhACW2grsUvUEf2EBsd8BeK9gNj8Oj5XBLBOZOlGasCJ6K4lImoQrgsF02MSdBUznEop4I'
        b'uE1V/lYjZEoaF/b5gDWs3VIHPOINN+ShGmNFwpixClF1Zk4K8LAvHGDNDjtgs+DtU/EzcBfYKU4mvVLkZgVq4sSRMcKIGA6lOZMDLvI8SsF6cqg+nQ9q2GgWckMADVc0'
        b'mdvFU/Zh5RZunQgacK/pTMaWsTXKlJIqd9w8QyLtIXCNUjmx3ODNhs0WnKVwYwTpQxyapvONWEXeXI5hKKglJTqBGss3Yu8Eg24OOADWsJF5/KwsSNSaRtjLhjNShI0c'
        b'2F8BWFu6OUh+d6iLo0jAjk40lvZwQJMROE56ayoam+flpm0Guqxx2xuWbYZAyo6nPitwVGMpa2bG2pjpRbBtHYDN0eg5OB6PwwnJTdNa7YnkZaDZZDM2RsImbTy41wTX'
        b'vTUc7GLlss7YCjdqmwBT1gOPzeOANngO7CYWMC6wNpq163SGB4hpJ5qcbpObeVeakhafgydY0xZF2M/lgH2wn7XF2F8Kts/0Y+0AsRUgkmI2HhmoyazCfJ018bUl4ARw'
        b'ggdruHAda5+9VhUegE2LiL8va6+kAhq5YGMkPEVcS8EBZ6RBds79u16zPeAMoTIPTcqPosm0PCLWaaQyznHQuNgN1xC2eSK1d4F9TyaFSpRmwXwtXohw0XPi/b4VqaTt'
        b'oGbhAnhKoxTPMv2RzJKJJoYccoBbw2NEKFNSiIom2BlH+ow3F/RO9igXqKFJP59DKS/jusRA1poYNs6J80NiKyhjBV65kOvsA9eyDr49oaALNThCuKgyAmyJE2Cja0Vq'
        b'IuxUGA/Xg+3yqIum4NQc2KeOy2aLAJ1cX4iWD2zXngfts0ghqAgkqcqUZiw4GcybgmbmTaxNkz/YAarzyyOxJToHnuVoozbuIoOiBOyCG7BBjzvcx9r0NKixcaPgaj1s'
        b'0QMb/d806gGbcmAfMUEx1tLF5tXldqyBtQsqkIjAXngGHLSwKyc2dDh00kJ4lg3b2KKEJrs1cYiKCDxDxcrBIRzWWcEtPMoSHlF0twf9pMVuwXB7eSw/kUNs8Il1mLYx'
        b'LwHWwxZihpSdmU4MnhvSKTZ2Xb8CaaffCigtZ7uIB9ZpwW2cJXC3PuGCaVWZIFIUJbKPRVpFqwitOQZ4040nEMLm2sADb9A1Dm4nZldwIzZy5Gcrgr1wm/g5WdudhEfy'
        b'3pQMIhZo0XOCiEacG5pue4MTSrFYo5DuUJ+Q/BqTcSZcxYFrFsxizfO6q7LU0St4LiJ8TJDHw34eOL44mZCcKgQtHh4CYj+Ivmwq8BwXbF8cTVT2LCTTW4n9EUQDN/bt'
        b'6DlgE1rRGP7fGvz8/fMGYqv8RzOgPwHGmvjmttDbqFhtiqw10KxApCBN6vObXRkdPq3DlxkYNdk02Ayb+/aWDwaNGIRvD3ow9sinN2/QcsQgtDZodNLkesv6irq5tTyZ'
        b'qUWtws5xMmOzprSGtKashqx2yYixg5RDGzszxh60sUevzoixb28ebRyAEqrhmA8ZDRmsVQ5KSJ7p6DE6Ihr/d5W5eWGLAMYtgnaLGOKPuCXfck6uDb6lK35g5i0z85SZ'
        b'BT1TVpg8oVbxqRplYdtm2GJ4xHh7RG2QzMJme1Rt0F09k/pyRs9uRM9OZmqJTQ0YUxfa1EWaxJh60qaeMr6wPnhf5F0T6+b8EROHet5dc7t2nRFz13qlUX3jZ1qUhQMa'
        b'jYbWw9ZeIwbew7resslGTQYNBrVKcvMixtKFtnSpVbilbSazFrQHtKS3ZbZkMtZutLUbfmohs7Jvd2qJYKy8aCsvxsqftvJnrDIG3YbML3kyQSl0UAoTlEEHZeDE5qNm'
        b'ovYZXXM75jLiAGxWZBZIEMiMLdkTfCfa2IkxzpCm9gZ0p/cuHZpB+yfTrimMawbtmsF2p2VzQEN6U3ZDNnteyRhLaGMJ2/MoZ2/ooFNfxEBsXyzjE0P7xDA+ibRPIuOT'
        b'QvukMD4ZtA9bipFFs1NDRFNsQyxj5EAbOTBGXrSRF2PkRxv5MUZBtFEQYzR/cMHQ9EuLryy/tJwJy6DDMpiwQjqskAmbTYfNZsLm02HzUVmqb1HkSCJ7vKYIV/bA3Lad'
        b'0zK5zaTFhDGX0OYSxtyDNsevNGUmpuiP+kfGlrUhMkOzJq8GrybfBt/aYHwEq9qgig2cGH3vdqsufge/S9ghZOy9aXvvQYUrapfURvQiiWv91BGT9GH9dJm5TZvBIYN6'
        b'xVFDk/rKpuUNy0cMxdLxtw2d71qIhx1mjlgUDxsVP1OkLIRPlaiJk/dE7YhqkTRXti1pWdLqT+s674lC0mBi9VSbMrfFTBm1cJAqSUu7VeUHr45htGMY4xhNO0YPFYxY'
        b'JKE0WoSd0sSOWYzYnxb7M+JQWhzKiKNocdRQ8ohZIi7ngaF5s3mDZ5PvPl8ktXoGexZsXzAGPWBP69kzeg60nsOwJOK2XsSoSCINwlZAZ6O7owctr9hesh2yueQwIkqs'
        b'V7ilby8zNMH9wxiKaEORdNKIobvMyIwxEt80EkstaCOX20ZiPAhWNK0YFXv3Bg2E9oUORPVFscZEjE/2cHwSe27PxKfT8elMfDYdnz2cWzAiLkSDJI4dEEb8pxMoezEe'
        b'gzafGVq2BLdPknI7DLpMOkxGrDw+NPT8B62Q+t/WCxwVo9F3Nq07DZ9sD0quuF9yH3K75D8iTsKNEPydRjjcNHKQOtNGrreNHHAjljUtGxV69loO2PTZYNMHxiuS9opk'
        b'vDKH8m/MuDrjRvHV4htzr84dzs4bEeYj6mPk1Hsh6gUOmHpbmTEWL7V7OpPlwLuMnoDWE7RHMnrutJ77XRPbYbuYEZPYYf3YUT3zZpt2K7YVMnPbNuMW41bTBqVRY9t2'
        b'JamutFA6jjH2pY19ZRZ2zfr1Sh+ZWtfzRk3skfLDSgVpxaZFDYsYU2fa1FnqxZj60aZ+H1sIhnRvTP5g8nByGpOcOZKcOSzMGrHIHjbKlrl61CsQ00RJm1+L34i+8/eq'
        b'lJnNUy1K1+ANTIfx7CH8fXym/EDhf34c/0++KPiL8Rre4Q/fkTIr9LGIUEEJMS7RX1dSL+ICORyOKUZ5MMVH96b/wtF9Od6CbFZypKTq3rx/C5lwxj9DJnz7szcGS3gc'
        b'VfwGLKHT2LkgOXATmhUWic3s8SmG2NFVMgag+keUwn+L4iJMsYz7dykus0EdLMX03eGO0WeI6ZMfdJkVF7xFyb/dbR2cOyo5+eyJ5T+ipQfTcvZVX5kTeDWCQTbDjGTH'
        b'IHz/MUW4W/icOxo5r87+cor/IVlnMFm2r7rIJsCscm5xaWXhn2D6/ZdoG5czdvb0T0jrw6Q5vSLNHvdYeQXqMnKK9eoA679JXpnwn0jU+bclXpw0D8MFz50xj+Ammk3P'
        b'm1dZ8Rba8H+JriPUP6Zr4G26DJPfRuH9j4kg0KUn/gkRABMhfUWEwWsiAiOC/nMaZmIaev4JDe+81RFlp6n/RL/Ycf5xZUO4MhyfnG2wXfKfYCyPYX/+V5QNGj5qBJ4x'
        b'B4Mn/iPS3sffFvxdWEnVJzflNOa8IRgEgZFVPv8VweBjFUioqpj3j2i6/rYKnCxH2fzvUqKRkze9BB/V58ybXzj3H5FDv636PDA5OA97bl3ypvHI7+FU/2vKUPMVtfkl'
        b'88oL/xG5tzC5t6i3yMWZ/iNy/y9jUsz4fUyKV3316uyfF1sc8f1LqhzvgG03uvs6ukSyvockfz/F1+BqO1/ms8B78+E6sHFsJw7sd3i1GQfO+P5JUIkIxOk7ur9bvpcU'
        b'zpWv3nEaHFCiJJRD6RvtqdpeNaxt8S+GkMBVlEUjXjF49OFuwCEkZody/o0YEv9/ZpNCbHJxwYtcBRJ8aujOMsyn2utDo1xqtbPySc57h/zYPvsjE9Zz/mQPJW/evBI5'
        b'F9TkXCgjXPgXux8XXhaniCN2vdH9pf9592NrJbxF9MNSasxaCTFAQW6tpJLCkYNjs/ZKVIrWK1slbvIbMNhzeSZvdfybdkuICdwAHmHNH57+fdZgu2LJW6wxjSWn8omg'
        b'tRCf2IO+KeyhPcfKJJfYrRz1UaRQ95jFmywoKQ3NYUHIYB88BQ+Va5aBNSaqOP1BjtivkJg2FAcokPTUgmIhryyRYsFX60CNM3FEZvEeE+AGfJaxMTpWKAIX4UaHxPhE'
        b'USqXyp6iDFpE/qzpylooFUdFws3gMAfWgK2vj3wUKft8RXC0pJJFxOoD+8F6bIpwxIO1RuDkmuQRcDFwXBPufe3eDLrgennk+iWZlXI0iRMYtgERo4ZBKZUpBREHHI+A'
        b'u0jRTk5gs4BvDw/D+hg5OpoqPE0MEuAasAHUCcAFIGW3YPE2tFYRr1B1aTJrUbO2MoXsc4oiFPyNKVVlLtgKzqGnxNThDGxLjIoQgibYGIFKVuCAJnAuhTU0OAb3wIv4'
        b'CI8vUkIJtlKqnlxw2G4CISnGsBJDoMDTcHWMHAOFCw+RV1GgLQ7WSExFsWTbVCmLOxHU2ldiGBjQCtrguii4NQJ0w1ocJSEa1qDOHwOyFPgqIpXYFfmWFKuPSfECLMVq'
        b'b0nx2zL8Gtb9f1l+1f8gv6JYIqUm7lhKh7LGTckt8ffSo1hDlONGM8tj+XAbWMcfg/sA2xxJZ8WDcznlEfY+sJc/5hINT0wnrDWDnXCnIFIEO83fZCxYBbeyAtcAL4aU'
        b'R8eirmwmB2+cpWDDvEp88pAHT4F15dj/mgsOSVQ4xgvBEXbAHEHi1cSiMXBNDLM5DuA8ekX4vdM9kyBQ7AIX8HkbC0EBpFlsG5rgkTyCKwL6LWPksCILw4mIJRhq/A5P'
        b'BOyZONGCTwzXCCScvnVeEkWlgxrUz+aI7sN8RZIziqv7u5xws9dEq2C2yhOFCRjXIx6ewy68BNcD9pVW4sNjGwxvi/FEYDU4M4YpQgBFwGG4gW1PDdxJ0A4IWonqfHAI'
        b'o5W4wN5KfLCTKTIQoGrFfPsYMV8UGcOhLCJBA1in6JkED5DqHeCq8W+CgyimwjZNUC03wgEds+We5hwKHoVrlFS4evmwmQTFMwQHwEVBKuLLn3jUE391eLKg0oY0Ec8A'
        b'cLeuc0A8wfE3ojAqNNhEho5NmuLsGYgcZ6JDEOPb8fH/K3d9B7D3j+XHglXKsBYN3QNEEmZqwH6skzaUjemkAFUiXTPBPnjyDcgFlfxUopFswVlijrRElYOV3lsaz2PC'
        b'mM6Du0ED0Vxwi5s70VvgFNz+SnHBg3AHK2/nl6/AeWvyY+SYEGAdOEb613W+MwZAQJ23I2YMWncN2MUqrYsoIdKHchVChRIlsnYhKdMHIsWIdc8uODCme9KiWH12AMkz'
        b'EmJ8EtcOez0ouBXuBH3EONFASUsQIwJ756CBpjAdqVDNKlIcH+yYgcQsXCREvafi5wV2c5d6xhAoxomm8NQf0ALMQVMMhguA+yaxda4thDVvAXekWWh5qRFJmADWOWFt'
        b'9ztN1xn6StnZgHo+l4Ws7IDN8AKS2pMLFBD5q/JhOwXbVEAtobIYfRP7y2G3EoWhzw/BXRSoLVUnLJ4BW5B6rlOiYFcqJaSESFJqyCcwbpwapUtp2ypo5wpTlXJYzMmp'
        b'saj51GCCGpUr3JMyg32oooTV1nwt7pTc6L/mZLAPY5eNo/Sp8GCN+NxxaeO92IeFYSqUNrXSmJObK3ySlvP2fIM3phYxoLsl0qJ4uqdDhWtR1Lzxvhw7ebICLtawSdQC'
        b'apeiGRUzHutTM6RE3XkEdhUtYMnUiXuHK3a8w1lQjmdYZuyy4o6qT1Hh3MJF88v87vj8/kirorAsJ0fsQ5bu5X5ick8MeV8/e5W7UBVNtTD7HqOV5nBw7s2pOcNJyVfS'
        b'h6wup6Prn8gUbbXeZA7BaAVnk5B810BsM1InEkcQTI9IK9ibEC9KDf8jg7eBHq4aB8PvdI7LRRLfXokPFg3h2nCkz/kiuIlYn7BWFNlTjVIUwDHQCOuKQ2o/ocoPoG6c'
        b'ra19e+rsOJ0A3Qvnvt19cWXgNLvP6dMqIboBifEJG82DVVryZiwY5/SuTOXgeFsbq+U/xj09F/23kHsN18UCiSiI1vp+1bf3fB/dLX9y/szHH1xbrfVI+2WILOLJrwoP'
        b'tJM38u7cb+wvs61vuf6u+ZSPeM3ihcWrbTV3vLz/zjkF3qdflRwo0Iyx4ExK/mymAtUdYWxocSeHo3m2/ezaJsW6QxXCCMO8dN8fP9j4vZiXuvTw3Hvakk/G9fVeOZ/b'
        b'OO5xXAEj9V5/9H5q94+rt+aKY0Iuhmr8FLnAJO8vJzYs+esHbjP2aFxZ0Mz57dHMlhcVV84ld+lPvT373ImKzComt3Vb9AdXdm59wN9tIflwVnrLmXFLqfSLW+3Ad+JZ'
        b'R9J/3pSRmaB+bXu68cTvVEtL1JU3adR6rrHNP+J6mnk5fIc39Imr/tGo3w5qfbks+5G+IHa7orfVtbpzob/6el+8Z/jZvSd7PqqAms+/kr4LTUYuXTH5sTh8syTq5vQv'
        b'Qmd/9uSDT/l95X/rKPHfq949WpJRI6iWXfvwWfitjZf9vw4+uC12c2TOlFSNzUfMz9wbicr+9pGS7g1p9FpuxZJNlfVOnpu0p6Y4Zj9ZnTc5Q7fyRMeIT3369wWu1inX'
        b'LIN+Fb6/QyMo5MK5r69uMsrYLTDpsocjF3e9u/NmffJ7O2K8rQs2C94tnx0a4nTm5wXeLXdj7Q5/e3FXZ2RH587sqWlOHfrnPtzMf0fWMyP6aOnH7o7Zdzouz/rxtpdj'
        b'x4WTP7q0+oz/hX9DpB4cY1Fm5TjzottlzW/LfvB5P0zQLb5w67OLeV6eP1y4Xl2jc6rmffcl4+JWLO35dI1vj2bj0o88i32/3Pf5l1/OYb4J8u3R+tinKv5o2DKNplBL'
        b'tc/2B9x3LH/paPhd/vLq2TfTZt+c1z77b9OGt478uoqe/v292KZ7S25ON86ZuV1LKdP32B691RHfBJqfb+sxfHnk/gnzgdyvvK9lPaeHdJ8s2hEz7/1vrvS/+/mLwMdn'
        b'pjyy+vUy937/4PrF1zOfddAbP9j4tfXCH77/6PamY1+XvzBaevnXgo3brA1Vb+gcF1g8Sdd/0nvh+XO7Dx32/vwi/5eTj+clfWrIjSu3aH2pNCH0mO4mszT1rHaLrvbj'
        b'HfN/NREqJX1WcyLsiezGJ/PvnbD2erF8z33OSztD6zala8tvqPU0fp5+qWbo0W7ZBEFon7L008RbRaVpBYeP1GRN3dnTkbg+9+DjY7k5Z/ZXrt8zWfp98fMF77x3/5O7'
        b'P0y3/fjn26O3Yx9M/7S17qfnhnfOf3t5WQtfjtrUgr5R9WQC0xAB2hXIp+h8CjzA2redgvs91eEmviqayKvaoUWGSIkaD9p46MN7wIAtYJsb3KBuj1HGsMGVClxVYshN'
        b'NYQnWGuPs6B6Igsj5gfOEvMzx0xivWAwzR+bVIEtYJ3crIpjmAXXs/ZH52HXOGz5hm2giPUbB1bDQ7CBrbEf1oJ6YnQ1KdVuDDoLXEgiZk+BOI4GngJeiHo9AzQBrSzo'
        b'ymFwqgi3pxLsiyiNduArURoolc1seJEYXRXD3sWv4MTCwInfGV1poWLIrG4Xp1hucQW7lxCjK3gInGPN13aC0+AkgQTDRlegbRy2u0JTvKMs4v5GsC9HneC5cNHn/WAy'
        b'xw+uySamNh6gN0COlzfBD5tVmYExqyqkWI++jWcHT/iDc/OrWLCfjR6wuVzMnw33sBZNGCHOGuwmOzXRhaDudyBw+WgG3QykYDMLPXdw1kICdChEJEiUwDGuRA/lJW1Z'
        b'jxZQ3a+QKFXAbisMRAm2jyd0RceAThbTDhMNB0JZUDu4F6xmQwgMwFXRGBEvlkOBrioWEc/JidCcOA/0oY5Gc8T0cswnBU8O6K4Ch0nGeMVlr1H4VBSjMQjfWcR9nHEc'
        b'lMJT5XBTRAQ8G4XNKddkl3LtZ+aSjMlwV+Yr0DOVeLAlkpthC2pY+7F+0Aq3YrOjUtaoSy2NC86rgn40H2YhfbaBg27qoGM+i+61CfYpgkYO7BJ7sqJ8cDY8J7daQpQd'
        b'0+VYZpqy4rAWnlBRj4yJBbsFSmgB1M8B2+G+dGJ8lVcGT2CjQlVxlFiNQBjthxf0wWkFd9CVREx1AotwCmKzuAa0vwZH00UrAVgH6yNZpKMNS8zl+GWz4EoMYfYGfllx'
        b'FdvCHaC95A3AL2V4Bq7DiF/jQB9rEtgDL5qwmEXodcp4FrLogjZra9YHW8EOgr62uuQ1ciiLGgr3TGRFsdYk+fcAbHPUwEU+bCNGXx46FeqVGsnwqCoal+acAEkAqVgJ'
        b'9EzEeHbELBScBBsVQzhwy3QDIoD28Bxf3U40GfTYjyFVwU2s9TLsiNBgMTrr4RZiRjZOwHZ5Azg8R11udoZWolswEJ16CXmXuGLOG+hWKnBLAcVNcEp4hVnWjWQLtlRF'
        b'jqFbgf3FhFWTqyiCbmUNGzDA1ZvwVrtYeCvUWdvBToJExa0y53NMgt0Icwo0UlgOvgFBhfTAYQJDFZ/GDvx1oMsUw1Chen1AK4ahSgZHWIVWwwnEDkFI9FBblcvg6Siu'
        b'ORwAjSRjIiceI2OVWIrHgLFAG2DHAtxbBhtYPFtihb2TGGKHsjCxqMItsAXWCGOR2obbUAJ1NHjnh8ETNuAAaxh4AIl8PUmxmQ83kCgoJ7iBSPJbx1WRuieCnQl4hUoh'
        b'/dy/HLQgUo4AOR7eAbBnpiBOiFLXEMNsdXiRmwB2I41/AKwnucuXAKm6PdyKtfs+tLDjuCDlcIElbhVcZYD6TAfueNNYl6cMquWAfcZoKbb1TyzU4YW58BjShHzz//e2'
        b'a/8TYwRz6o9AV3+wc2PXBWqvZ/t3+P/jhQHZu81Aq42XeBnwPDicQwldm5Vl1kJsyNWa3cyVWdq2O7d6yUSS5lCZ0Lkl5IH8qjlEZu/E2hw1Kz+wtG6e1eYnTTubfTZb'
        b'JnDuDe32pwVBjCCUFoQygihaEMUI4mlBPCNYOpw8bbhwNp05m04uYZLn0cnzmOQKOrmCSV5IJy9kkpfSyUubg2W2gvaKrsUdi0dsPWQevlJFmVDCCH1ooU9v6mBhXzYt'
        b'jGaEabQwjRFOo4XTGGEuLcx9QVGiadzhgtlMQQVdUDFcWfWUolZwgrnPKGoB+6eQE8J9gf/Es3fx7F0qe5fK3k1j76Zxm7nNri2qMpFL74zuHFoUwojCaVE4I4qhRTGM'
        b'KJEWJTKi5cOpWcNFc+jsOXTqXCa1lE4tZVIX0KkLmNTFdOpiJnU5nbocFeTWooYK6sgZw8IJokVBY+XlD4VdjWOis+nobCY6n47Ol6e3d+pwYOwDaPsAxBRHdxbqIoB2'
        b'DEDvPVs0ZPZC9Fwo6Yo7Foe6zE6IAYm6tKSJjK0fbevH2E4ZsZ0is3Po0uzQlFacXdy9+EO7gGeKlMjnmRLl5CETitsXd8TI+I5dxh3GDN+b5nsjEruyOrIYkT8t8pcJ'
        b'xF0eHR7yEhg7b9rOm7EL6C3745OnijxXmx8ontD2hRJlJ2qpbF34QpkndH+qREncn46jnD2fGWo6WbB0PzWh3P16i4aUaL9Y2i2OcUui3ZIYt1TaLZVxm0a7TUNccA/g'
        b'DufMGC6aO1y6kC5aSOcsYnKq6Jwq9CqXE4AZhP+g8vxpM4nMzbd7HuMWTruFM25xpMhk2i2ZcUuj3dIYt0zaLXMspQ+OG1N4KY72SWZ8ptI+UxmfabTPNMYnl/bBAuQb'
        b'ggVouKR8eEEVXVJFFyxlClbQBStesLIjF6Fm7rClB23m+QD1nWmHKcP3o/l+DD+Q5gcy/ITBoiuzL81uVrpnyW+f0TW7a/aoxLOXWGoNLhiacWn5iCR1OD2LlmQ1BzYv'
        b'aol+YCvGOFvNCjJ3bxZxh3GPpt2jGfeC4fjE4aR8Or4AVyihzVwQf1jeMKJgWhSMhHCIO+R2VW1MwJy6crCIBdCigNePCAIThq2SPxI7d83qmNU1r2MeI44enDAYdskQ'
        b'vXFvUceJX3Efifmg8+CMS17yXGO4XD60wAc9cmlRwcnTO9K7sjuy5WkcJF1LOpZ0rehYgR54tIx74OqDLd3O5nTnMK4RtGsE41owlMZCn+XQMTlMTAEdgxrX7EebOWNB'
        b'NOkwaVaSOTqzgoKUDUs8O1jCaFEYI4qmRdHNavcsRTIrm+bFLTGMlQdt5dFrwHhG0J4RI55Rt6yiZQ6uLPZR6C2H0Oawt1PqDRj1GTGeUbRn1IhnzIdWsc94lGMYDnor'
        b'dunKPJaJVNtb6SdijKxXpX9oFY3Si70+cXSV5vVO7p4z4hgsp5aln+H70nxf1Ap3Xzzkzi7vXs64Zw1NGI7OpCOyXjHS0nrYxo2xdB+2dO99wxRxOD7rlk/WU23KwWnY'
        b'KYAWBzLicFocPqQzIo5pDvvEXtRedFTYO37E3mtsYJfdsvNCFAnE7Jvb9l5IoNpLW5Ywtp60rScLETeoPMS5pMZMSaSnJDJTkukpyai5gZwIztD4SwZDacMpqVczhu38'
        b'2pWlnA41aVhvQHfkKCpx4VGfXqcRgY9M4nXWu9u7x7c9GF0ykhBaEsJIItF/mW+AlCt161b7xNa+3b11qbQUaey+pEE9XPC5nOH4hBHfBKS7ejndaoxjIO0YyDgG047B'
        b'Q3rDCYlXDZiIaXTENCYiC3WNzMmjd3y3QW/ZiFPAYNpQwqUMJiSNDkljQtLpkPRR/2A6OJeemjMSnDvin9vOHRZ437TzeWAnxr0w7D4N9/drzCp5dz/ncfg5mLUC5y5x'
        b'hxipS3unLkGHAN8w9r60vS9jnzaod8XwkiETkEgHJDIBaXRAGknH2HvR9l6MvT9t79+sfM/S/kSRzHPKoO2wRyQauMtoK9dP7NyHPcJpu7ihQPTTrPjA0b1Z8ZCGzEZw'
        b'WP37HB76mP5EMHHWhFvlG3KGBEmO6M9d41A/9EcemuqOasWigsKK6cUl5XeUcyoW5U0vL/xPbBnlQarenCKwp6w7FNFPHfrh4a0/L/To55XUi6BwDodjhs0Xzf6Fo9Yf'
        b'8FboPiUhdUzdncfnkf1b8XywOwqeBg2RbAhHAt2P8WErWQcucHJZlNwlb8wJRwDXUwagVQHUwAYx2SIsisWBLXEkbmGECGyKY8sCA8spU28FuNMshs9lN8hXwtUKUbBX'
        b'/c3K5oFathBYE/P7qooy5DWhpUo7QSDIghcEAuwtdNwuPEYcEZMwH3tehIBDJEo5xljmULkTVazg6lRy5AI2g+2gLwpNoNvecoDmzkFT0Ab2eK8fTZsPRcEtIrRIT54P'
        b'6nJxkU6uCeFyMr2slCiwLpT48oODSW5vxkon1SfYRcImUP/6hDUTNKpoKeaQk1i4Hq4H7X/snllodUO6R5REYlPC2gK4v1xenLwoeFEnNkUepxI3D6/JZ6xQAQfhariT'
        b'iGLxiyUmCuVLeBR1lfPZhbT3545M0TX2XvCp1fW/0jYaLvrB9s2HA4sDOGrqh4JX293crByiu4p7ONxu0ZWHvCl5l3Z891Lp4krjpjWXVzs82Gqq0ybpsNEdzz8pKb/R'
        b'1/Xw66vZv0b85DOr1fKzE/lWy+3bmwwGbwfpTs/qbzL629pl17LeOdI7oJPtu3+WB/+7/KhMy4x5m4etOAt//vr7L69PGFIIM1hZ8WPP0ivJRaMK54xFvStaONdT4ccf'
        b'uoFzayasbkw01rNysrGc21lXoHxi7u2AB4fbA+2/CJkbkXjspff09Xe/P/L4h2n7qYRf2yYfyp98KEjrts5oxbuheYK66hsO70R4732ssXRF+kBe0d823baWpYT4eXdO'
        b'nP8FMGpccUPv/dPGM2zyZ3d0L1b1h5eF7+kPTK6o/uwDs5+X6v+Srrqw6vGXX09/7uzWYFCZqPKL94TLiqXXJO2rHMTGTMQS4bvPpz5vdXpaPdP2+KmImBMRi060q5Y/'
        b'3THz0Y1dEzJ0A/ibBiVX6nfGtg9NvHpnd8Hx45P8CzI1L0TUX7D6qMjrk8q/cc5EHHi28Ef1eU1gwGjZtwOOC3ZNjkuYfrVumdqZE5e8U1tSMlor+wOZmTUnRpznLJQc'
        b'uhncJXQ4PcX33KeNRX0x6/m/vnvzp6lC04Uaw6mHck48dPFR9h1/bVfSGv7d3OWWax1bbl7+chl15IOZX07LeLnbCvhebfx0b3x9xm77HUUNLZMP0La/Fds3hN8sV7+/'
        b'y1FwXf/dO6on3rGWTSwqcPnhbo+mwcCTrz6SlsV9dPv8N0uLihcsEYNeV+U+QdYWmUtMz6H+XSpOP778YefXc4O/mNzcVKIGvEsGblxoqw9J28twn188c1h53/kPf/zS'
        b'+fSiL7ak69Z0a8cJJsW5LThw9EbszOZbqw6lvnjH9eSEloMeP9+5FLZiiZ/28W1NOe2ffD4z9vTXEi2dPfvd232/Da562JV0nbt5x5qzp0beu3jOa9HDeU6VRsnft/Qu'
        b'0blYd79mwe3Rhh8v+Fx72N37yOzmpp3TAtbMy01/ejvN4143b3hKtPLR7rolHP8JDZ6asWV++X5HHjnUjvrk5L/rnrFHMmFN4ckH+55q6geI4KP4yYb+k0RPk0pFP+9R'
        b'aJhn8VzpaTYtoG9K2i2Kb1p8TY08qN0/Rc059au4SX1hX91Y/0nK2pPNn7oZfC5z3f1DxrHqH6dVFJz5JOfjp2m59+M0dC59HFXhW9p+WOs3Su/c9fkKpnzH50I0FN3B'
        b'hXLWE2z5/Dd8wf7oIugJe8j203JdNIyx0yHe3mQdEzngBDgD28nOBVcE9pBt2mbbV9u0YL8uWYunwlbQXh7Lf9MdDi21O3kJaJ3dxW4/nAgE9XhLlaMxtqHqDlvJpmdI'
        b'Imj8g8+kHdgtd5uEHR7y/YRU1Td3spaBBopsZMEOsJMFnV4fXoADreoEkVCrGfAiqVoD1MMmsnEGdloRjz/QCzcRl00hPAEaxxx28fk5PIV3AkpV0PJ/lwI4hbRlO9na'
        b'0oONEBEpYOOyoAbC7hx1HS5cAzuK2S3jvfC4nzqoxXvZm0v5HEpxIQfuM4Wb2eATh83jsEcgdgeEnXAf6Esex25wH4K7wfZyeSwb7JqJqjymtpALjsIzK8gmywx7sL+c'
        b'rwrqwE654yBnCagGp8im4FJ4Dh5SF/OVIsABipvG8Uafvr3kTSqodXwVXqYbNIB22JBOGB3oDNpgTxXnLf9SXshCwHaXImjxK7ePSLLBHxtiaLEa9rLY8AXaGeqh3LcC'
        b'+7Dbc0AKz7JbSXVggID+t1OiNzzKZ/iTPZXFPkjE5KDk8CiUvukUiL4rHeym7xpwGm90yvejEkAnpRzFNdcDR9jN5uPo69mqDs8pyHff8M4b2BLH7vhuWCQpx5Gu4wOw'
        b'0yYPdHDANrMEdu+9TgcQh+YtSBbw/jcPnOKgfjkI9rP+ju1+FerimDKcAnRUoK4brwsu6vNmgYYQUrgoGXTi7VnSZXp6lIoGtwDWxxA+eoMeWP1mSCE0hk6wYYXgmims'
        b'2+5uuKOAwAuAvfCCHGLg7+ALgAM+7Jbwyjmqb+wYR8OjeNO4H7YtZqMYwHq4Tx0c5o5tGrMbxtY+pKeWgCZwUj0yxgFuf70tvAlJPn7Jw37/UYbg7JgvMw4PtRyuJnxC'
        b'ZILa3+19TYKdZPvrGMrJ8qkfdKD6a9DkB/aBXjyq4zhwZRpsYF+3wnasbjqE6P358LE4RdnwGBElG7ARHpJH3AJ7Hd4AN4C1VWRTc4a9xRuu9GQ/lIMUGKVfqGAhQjTg'
        b'DshBBO7GrrFkDrPElFLx4OYhSd9N8AWmB7J+s2/P4pTBXspUXwF2osG6ld1K7IR1gXIo/RoSyAS2q6hFc1Ef9IN64oKrAtZhf/UCeAFbjojAxjct2BwzlHRwZM3n9ihl'
        b'nhlseO2Bi0Rp05ua97UHbgyftHI6mhCirvYGu1/NyMA2ZUozg+cELsIm1jF5B1y1guDa7Afdv6vbHm5QBKdAR6I88NZOsBbNhNehQbQtDm7EMkaK4/HMveA+dut6Z7YB'
        b'rKkyFr4GpEC5dv+v7meq/G/vZ/4OMJRdrYRw/8xpl2xkkk3LBrSQ+QlvWj5dFMqhTCyasvZn1YYQR8fDBvWKMnM7jOzealKvhJ0n/Rv8GUMH2tBB6jZi6ImW3g3BMmOL'
        b'136l0tQRY2+ZpVVD8GfYITJsyPqGw1UHJjKbRv8dskcscoaNch5IPFgsdkYSQUsiGEnxUOqNDLRsnjpzJKa4XmnY1IHWdxwVOEmtz/K7+WfF3eJB6yv8S/yhUDowaUSQ'
        b'PJw2jRZMq1eqX0Tr28n4YnbHjeFPoflTGH7qYOiVyEuRQwtGglNRmgUNmjKxBGOrM+Kg3gpGVISIEl0VMZGZdGTmcO4MOnIGSraE1rcfFeA9CsM+wwGTPhPGM5r2xF6Y'
        b'gqSxmixs20QtIsbCmbZwZizcaQt3xiKx13XAt8+X8Y6hvWMY70TaO7FeeZTvJl04qDDCD2H46UOThuOn0hHpcloEjl2eHZ6vd4AYQeyg4hXVS6pXNC9pymt6YGbdptmi'
        b'ycJYIybwxex+iA/N92H4iYNK2Dd1yG1kSqK8UJSewF470maO9Yr3TK3aFaW6Z027TUfspsis7HH8gfaFI1bu9SEye4f6hQ1aiAdn/br9GEk4LQlnJLG0JJaRJNCSBEaS'
        b'SktSx5jwAMkBYj9ivinZZTF1vxj6wMwGV/aaQBn7gK2dfcSYedBmHr974UWbeTFm/rSZP34xrmVcm1aLFhvugTGL6lXE+OMDmn2ajEcU7RH1VFXRw6Q+FG/yGLm80JzP'
        b'mSz8kcK/Twt4lLV9W2xLLGPlSVt51quO2vDbrbtEHSLG3oe292HsYy/xBiOg5ohNXL36A0NTxtAV/R+1FbSHtFYxtiHS2YMB3fMawp8pUXbC9ggWU5kRBtHCIEYYRgvD'
        b'GGE02RfPG8YOrFl0fBYTn0fH543Y5teHf2Fo+UDsIk3Dm34Zg5OvmFwyYQJS6IAUJiCDDsioD212b4iTiSTS0I5sRjStd/HA8r7ljH8q7Z/K+E+j/aehFG4NsaOW9u1e'
        b'tGXUYCj6qQ8e5Qvb04+aYD/yUSvUpY5PeVxrX5mHz5BAJnJ6pohuHrh6k7/1IU9VKJHb/phRY7PmyXuz20tHjB0/s7LrMJCZ8VE2+yDOqJOrtLDHUCZ0RznQ/QPvAPbi'
        b'B4prHcxpCPlRibIQfGIlGXYJfkpxrNM4V4OHE1Lfj5JNiXrGw/eyuBT2AtWmRImc98ewI3rEInzYKBzH5bBqWtywmDGV0KYSaSRj6n/T1B89thUyNu60jTtjM6XXtT5M'
        b'ZmrTtKxhGWPqhP4PmzrJHCTNiofGyVyn3DJzfuA5ZcC0z5TxjKE9Y4YW3lh2dZkcgt0jr1nxlpmrzNK+zbfFl7F0pS1de3Xx9uGIZZDMXtxl32EvTTub1Z3FuIbR6L99'
        b'eHOQTOzUVdJZQouDe1NviYPbuaMOzlJnDMJ+19lv2D9pxDl5WJj8VI1ydGYcpqD/+L3k6KJe86NL77oFDgdNG3HLHHbMfMqjHH0eiBwYkR8t8ustpUUBg8lXci7ljIiS'
        b'R4UuD7ynDPj1+THecbR33IfeCR1R7cFSa5mDS8eyQc3hxNTbU1JlYRFXqi5VDSel0WFTpYpnNbs1eytGHIOfKVI+iRwkdnzxM3PKIYTz3IZy8B72ThkRpw7bpT4wsdyv'
        b'/rwcsUb4PY8yEfxEcLPXThufqcf5aLIf+mX3urRZX4Bdin9wCPh3Pyjaf9jrevP7UXYF1fTxmLMu3u1aiH0KDPFulyF21jX8V7wL/oqboHNHMScn39XljkpOTvnMwsKK'
        b'8rIw3Jxg/NOFUtxRyiF+Y2VC/EQVezb44asA/NOGKXuGn41i8k7hWwf8whk7P0zMwXCk+RXs0VwOxh4tnltUlsdD75RzFs0pmZc3q+wGdm0zKFuDs67FP+vwTzX+4eCC'
        b'38fFEU/l9fjnOq6niJQg93W9M+5NF9M76m84dZal4tRbcD4uLmsrvtLFnh+qr3zX7ijLHcbujHvTX+uOxlv+UKxHDfHrIIzYgPtu4v/dwSleRP0JDPmYcNxTkP9gaOTy'
        b'NYjMlxiIfJyG9lMjypo/PM78Uw3dBusWXr1hR2F3UJ9uX+WlpN7ZV13pxDR66rThhEw6O48uKKZnzRnOnzvsMW9YNJ/WKH3BzeFoeL6g8O8z8osRxMs4T8nzZ8G8MSzw'
        b'MIwFHsHZEIyGlIHFqLZIpotVpYFkQyR6omc6qm0v08UqUM9zQxh6YmQ1qu0g0/VBT4z8NkSjJ4aWo9pime4U9MQwkLMhCj2Slx2Myw5ly5Y/wmXrSsgTHcNRbRuZriN6'
        b'ouO8Ieh1GqxndYPYbPpmo9oCma4feqQ/hbMBf28mm49qC9mSJks2RLym0gFT6fQmlbGYyngOIdPYelTbkX1kjB7F/EWFo2H5FyWOhtELpWk8jFiOf38gv68Ry8FWuAlU'
        b'l78NhDMZ7kYrncmwXaEQngW1b9ndvgKjLUE/fsrEzQpjZVNyPx9VF+VXLlcK/0WXq7V/5tfztstVUWxlLLoudBVLHF2c3ZxcJeAskFZUlC0orSxHCw8pPAVPwjOgPhAt'
        b'lU7DHi2VcWqaqhrqYBvYADZjALKkeLgd7klVxMbyferqaIW+kexyw7pstA7DNrk16fCUACNuwW2whkfpwP082O+YQBBFDYpAl0SElvQU5UQ5gQ2wjnjkeIP+QJIc/fBC'
        b'fMDqMpStC2WD62cSa/E4VO6ABKxKRi1xppzhcbCaZKxSyME14up4xaCZzYjrA4cVKvHYg2vhwYmSKDxLl1AST2fWS+c87IlBVZFs2CLuLNca5zkJ1lVqoff6oD5c4u6k'
        b'RFEulEtwNPFQAJ1+cIBtH84WjHJOQHXVoHxJmoRG1D9boFQCDmPN50q5woOlrLvRHrh9Cts6lBEO6PK4lK4ObtzFLOKOEVEOqyVgPbiIlKUb5Saew5ry1yqtYGvDuaoL'
        b'cS4OyrXMkJiZg/3gJDwqgdXwLNKn7pT7OCAlhCJh3bFMTqgyaEEdAqSWoA/lDAc1hAnpsHeWBO4wRHLqQXnAAdDHelHsnQ/bWDqVLVFdYHMSypQALpLWRcEuVdAD9hWh'
        b'a0/KE8nIhUq8TiwKAgfGOgXis4BGnoWceaAeDrA9UwvbQRPoqRyH2OdFeY1HNcqtvOqMMcsR38y4iNDt4CjLvZpYklEBlV1fjhbMbShjIBUIts4lfWMJtwWQSlFeS8wF'
        b'sBv2o3xlVqRDwTF4NLtczwsxPYgKgv1iluvd89GgJXLJAy0+lC5opDAb0GqYpXIr7IU7ys1hDWJ8MBU8DTYSKqfmxbPdiRuplKWchwjF3YlGyGoWZ3k1vAA3lMNW0Ig4'
        b'H0KFaBiTIxo0gPaDw6RHcVakQ5QnsDyEe+FFwgpuCdxYXgb3Is6HUqF48BFPhzhwAfaRXCphrJjiG568X5XsSF4XsAP0ly9C83gqjAoDq8EqwhAruNGbpAarMdzwTLAF'
        b'nMdC0IZyBoBqktUQ7AN7y03BPiQC4VQ4rFtCsoLjQjjA8gNndYSrwXkfeaV5sI8MqCBnvLfLx3OlCCpCyLY0Cx5bKucH+vEHLbiTWE62gn4WS7gDXlCDPboqiJORVKQv'
        b'3M6qjXX5mWzfpiSNyTppKB5Y8Dw4zPbweVAN+mAPB+M4RFFR4JwLOyjPIdm4QCheA0/isV8Dd+bjatdDtqVBsBE1piczAvE0moqugjtIB8MGpAM6x0QI9V1DNMlPGAu2'
        b'lZEhBo+AfctRXngcsTWGigEX4RF2iB1QhvVjkrR6LjgHT/qwjAWd8SzB/XYYGG0VbEGcjaViDdFowTnTUlxeyZKyGYaPG2NNtnyswFPauijnUW/E1jgkCJ1gIxH5heCE'
        b'+pgoKZtTOnliwpZFiOtkw7p+BlLIPQ7+iKPxVHwE3MvqnvOglWLzBJIRdgq0Er6Ewz1sdTsqVNVBG8T+9AlUAtgE1hBCfcERA1aKVmFRQFTOcgC7ME8uoHGMB9ky2DhR'
        b'PRnuQPxMpBJBXTorQs2gF64nHUMyIvGJQ6ODiMJq2MrWuS4OVKsbwBbEzCQqCdaBLeyBYjfSZl2EWtCkMzZssG8OKw4L4VFWlLbBHtCo7g/2IaYmU8m5IeyZ7np4WMT2'
        b'rSVW1WMKfoyrLfFs7h36sFZ9AWxBTEWf5Fz0/cLaTwNuB70kPVhThrXfrvko0wLISu9c0KupDldCvFhIpVLBAS2iUhZORSOZpRGswpzsLGA1X1s26SOH2Gh1uCsBsTKN'
        b'SkNc7SenxbOxbyoRdR6ag7mjEYxy7IL7WUaumQOPqYNWRcTIqdTUQqQoMD/84R6Mgsd+U8HBkolkUJN+na9OMqqDw7mgJgKfJacjFb8WDTDc2YWwG4fG9YQXEaMyqAx7'
        b'cIo8nwT3RYIacJFCTJhGTUO8OsZqwW0purAOrgKdqKliSgxbvFi62lyt0fPdQagxDpRDGVxJknPRvOB4EtwIDqEbc8p8CRoirFwlqaPk65aj4gWUAB6ErNSAHanLk6J8'
        b'UN9bU9bgImhiKz05Ex5GcnAmErXakXKEncuIsgF1CxRgXRkH8VlICWfrsgyshk0zkgwnIfpsKBtwELby1Qg3bGLgSVZXoh6KF2PdpYu/6/CgNunDInAYe7HJ5yY4Kuur'
        b'L3GvBqsW+vEnfEwpoD7ZZs32MxY/bXCU/TCfh5vhSsJ0rhmaPbiDdlyGGThLhty0SmwOPqazsz14eXKdvx9sIGR4gC7FMVWpPDsbrh5Tseh7cZH9UjUViFkiEB9wK0D1'
        b'fFxELmwi6nYS2FPJyjep5CQSg7yxMroqWRV1Oi9DXgkeTjszlAPl4qKIRhFRDS2oD46N6aIg3EgLgGrst4a9fA6hIxk0gJYouFEIN4aLuJQKPBsFurhgVQw8+IhMMGvL'
        b'pvDViCMaHcgj8AJmqXNK5ha6sd5pmQuxyxplNz9jdnSaky77MMFJlUK8dXR0mCOU+huzD68ZTqDwXLtWqWDpM64z+/D9bNZnfHBqWXTJ7Dj2oUuyFoXI1x/MnDvuAncu'
        b'+3AgVRlPdrXn65ZFqyZYsw87ZmijGTLl0VxQKjxClbIP/eaoU0i3q+RmLBDGGSWyDz/WmkjZESe4CiOGp8A+NB7PerivLJkbfVB9DvtwZiXbzPkz88Z9aqxDES9jt6RJ'
        b'SDwp7XjjmZmmuVEUn5scSl68W8U2YL7K8nHGqnPZ1K6zlQitD8KLhMLJ7tSjxgb876o/qWDDHPZtfFR+NM96AvVIQv794M8i71ejiVQLrHEHtWgYzqPmgd6xL+Qp9IGt'
        b'FuTDBjSCFlGL/JA+Iv6+RBh2F8BDr0Qu1um1yAWAbaTaPXPYJtQmTPeJjc5nG1s1g+0WM99in1XOQezDEceplBSx70F0+ZJ1EemosbGxxXNSbnPKXRFJdj+vX5eclWaY'
        b'onuhPMLMaqnVuJ+qraZ8q+y6UrThcuLx3auByn7fPbHHJyacWvY4K0sQ9ctEn6/yf1P9rf2GX9/uj1/EzlgdM3zMter6hRf7lv3o+aLgu22/mD+Y2W1j5lT2qdk6l1Ld'
        b'/Mvj3t2Y/tkGnXqr2OmN9WGrPHh7PGosutc6d6+27672KtX84bJS4+VJkzbUTPUqrX9k4PfgK6+52vM+nVQ6+exG04MxmZfsSzVMxz95IC41Nry8rTvibwrTLmv6Wd+D'
        b'bs/8/CyXb1W+7PDU+pn5gth9xsrbpDW+S9d1dW/jLXqptN4j4+p3HndUJ00KGR73xTKnlx/V0n+dMW9ZqvbqA5ZrDgSUw43H0q41P25T9q2d8dmXtb9cmXbz3QKlG8sL'
        b'f2WifN7XoD+s+jp5OEN3lsLyvdndavuVMrsFL/pPha2x/nr8qZ7Atf5nO65PjfdILe6582VKgaWu5bup667L7CZL+vPmbbV9aP8wTrNTdeEul+hZ56/t4vtvna3aZR68'
        b'dZ5P999EJwuuNq0Z1rEJkw75NMj8Exfzvw76Oa76UXVSXEfJUr22b9IWxT7J9vNdZnd75wHN+wuWPyre0rZi2tHwlL7pjeOfuzqXgY9cDqic/fxMdNis/kj928aP3zPM'
        b'XLztoP2X5maJgY9S7jVd/Dn7y4a2R0kPi+cOpTbEdf7twx99Lx5f/d5R7oFRzUm7q765eqtU7bx7oI/gsufPPk+6lxfNGPRZYvO4ROx34dZI9beP13UkXqsYGvjWatmu'
        b'UO8DLxZeP7j/CVT/aH3qE7e4pQulPy93+/bk1+/89tWN35w/sLgV8nnnaGXEtd+mXs+reNivcjhKo+zLk2W/fG+mtTz+8MvfjkZ1Ktxu2Nj5w1SlHyvXVbXtPhopyBN1'
        b'RN5cL5nVcUezv9vife2y+ym3Z8Z+u8/nyfwnzwdfPgx7Pylpa45xouHDZFHI7Y0nN3Xm3n9XcmX6tF0p7zjvvDrx6NezO7Nair9SizmS8dX3v/6Neb7Tc8/0TeXzM5+8'
        b'l0K7fry/8Ej/hOXLNny1ZN/X4UsOf/njuUTbcy87rj1pPJBUuGJ5+Kn48j0DyhGidy7uaL60aVP3lf5vIutafsvUuZeTcC/rscg6tX7qQMiHNT12gcyK8Q8d7nP+upfe'
        b's/EhX4t1SFkFdgHsgbQ5JjpOkVJcij407Rw0cPuDyQmlB2gpgTUO4WjVfAQfSSuEc0AP7ANr2TPpWvT93BgFt6KvQpQIdqvYcyh1/IWLU2QdLOong72o8B54Vt24XJHi'
        b'qXGcUAUbyEG9IxeuEcCt4BgnL1KRUijABhmtJqw1wu7QUowrHyFEk65TEQqU+gIu3AtO6LK+T+Bw4WunKjQDXYO9qoQlxFQhI9EEFepQBQYQLQqVHLgxZQLrf7TZHmwU'
        b'iOEWRYpbjieUnNSF2eSo1wxNT4+xzlT+oPOVNxXYUkGIKYkEnSy2sQrcjL27lbgo+0ZYzx7ZH5gMpVHE5+3EeESPgh4HHLStJP4uqXNgNTboQBOWU+DoAk5ASTlrA9Cd'
        b'T7y3NkdFgOMUpeQBO+ZzJy+2JC+Xec2MUkh4G5SfVzSB4lv9v/fG+De2IfEH9s/9N95245C7cJTnT5+bUzxnelFh2ZdorkXOOUcVWGCdihgONTGQsyHkKVdbX1OmbVif'
        b'9JSHryxE7eXslYv/oA65ekDeKuIr8pZckbf46qkSNd4IvVdmry3FKIX82nUKByUiNypsIlX2miSSX7OJyI0am0idvSaJ5NdsInIzjk2kwV7jRM/k12wicqPJJtJir0lJ'
        b'8ms2EbnRZhONZ69JIvk1m4jcTGAT6bDXJJH8mk1EbnTZRBPZa5JIfs0mIjeT2ER67DVJJL9mE5EbfZLo2WT22lEyqCMzNmsvf/vP96baOLTkMws5vjQOuc7oONA6DrJJ'
        b'hntmbZ/VrFM3r5YnmzBxj2C7oD6/3RofFNUKhie4bgiSGZni6LQbYzaEyCbq75m2fVpd1obQT8br1qbWF2zPGhlvuSHwroFDrRLeTDatX9A8vWFRu1KHKm3qJHWS5vda'
        b'dM9gJvvWBsgMjGqDRo0tml0PZNZzZPqGbPj39pAOW2lAh4C2dPtQ3/0ZjzKx/0zgUa8lM7OoV5RZ2tarjJrbtJS3S1oXSc1bln5o7lIfILOwbrGpD/rCVCwTiKXjO8o7'
        b'PFpUHgjEzSoyU4u9K6QeI5IwfLaLQ1EnHNJCiQ6qPDCzbs5rVW1PaNE8rPpMj7JwRf1lxe8Y3+xRryLTN8OxrfdpySwF7UHtic2+qFpTixZJ86JWX6kzbek6YupWr4Df'
        b'BqP6QqXBUtdhS896lXumtqNGVs+VKFOLZru9czrKpR5Hl/WW0w6BtElQPY8l3bV1yYfmzohsW2HLIqlly3LG1rfXkrENHtSpD9kbjtpsIXlgat60sGFhc+Xe5agefWM5'
        b'OWYWbcotyu2KrZqoMyys6pVl1nxUXkx9sMxGJOW0zK4Pk1lY1mPEbZmdfbOizMa+rbilWKremzRiE9DMk1natI9vdR+14sts7ZsVZHaC9rwOFZyO3x7QUtTMu2dj317Z'
        b'Xd7r0rN4xGHKYPKQ9XB8wlXbS1nDqekjIekyewepeQe/OUgmkOCz916F3pRBSa/W0IQRQTTrJVXeWiWzE8mETtLgjujmEHwR2BHZHPKjBoXe/r2yb4ekP9OmrEV3BeIh'
        b'xaH8obKraiMOSe+pDTpJFXFU7t6AM5pX1WgH1m4hnRakI+Za2mFEXql1r0q3A2MZSFsGygSOUh2pRbtXd0VvWM+yYUEwYxU8bBX8zJaytH2uTFk7P/enhJ7PVSkDv2fK'
        b'lKHj0yVoAWf20/fKlGMyp1wJLzq8DWMstNkTQrU7vOI5Rf/S4SCBHst9W5US9Ul+zo3ZuuP4uuUxHA5n/A8U+vlXDv4eouxvBUHENZJdfgLIpPy7IIgqJJwpC8pEuai9'
        b'Cn6o9F8MfviHg4c/huMziv1zJLo8TDOXRaJLUXDh/t9g0fH+QJ9iLFnd1E9EMw5dTF5udJ2mAcXCAp2WOOBVcpqdHKbMLjy3KCIpHE8bIhQp9yolO9hrV7y+7lsFEjz5'
        b'vdO/9OQ3YsjBD2ZaXx6s1dCyuzaoDfQvD63kRLec4ga5SKKF9Vd1O513Oa0NWLdKwqO+maxY9Ze9fC6ZdoTDzWAgys5tLC6Dkg9XD6yDvWxokMaqEnWwBm79O6FB4ErY'
        b'zue+IZD4uz32TVfPn1mYPzuneG5B4aI7pjk4/GcOhp197Yz5RgLywcd+BPiDPzMeDZSJtaV1rvKA3jsj7hrYDNuOQfHr6deqvIGzp3iHU/xn4wZNPOXDgx0ZT/HIQAJO'
        b'TVR7jbX3Y1E8Ghla/8qgWI1ykr01Q7AJtEQJY7EJpIJ9IaVkwFWDzbCWLJ+ngAHQK4B74uGOWC7FHc+hUkAP4XtaAFnXq6xTyBXWhKtRfA7ZAc51CIjyU4uOjcWgUypx'
        b'3HJFuJ+k79NktxE+08mN1tIJkAN1r3JN0qzWmF/Ko7ipHGrffrLe75xD9hFUiqJzox8GLqdKcADunAwFvDNCUaEfKDybqldSQJXjra2QiN+SUir/spA3eRvFU+RY+80h'
        b'tcXrsFsRITG5477KCmKdapKzbzzkHunHaD3qTVyS7okf2TwIvyvKjX5cVcqmG11U/1AxYCqGH9TMcCvH51vLZjU8fHnrcy7eQNOPGSY+QVH7v0hK0VigUT1/fjKaB4s4'
        b'Ox9YlmMOfqL4lSDzJTav7LDD7uI63bzPZnxNNhfKMcNjDmaODN7Xuiq8isaCMofrvGQTqRdu/XaEMhtGwkDxdy8ij5QKPhlRKLtMUfaUva87eRQy4lzDWZpJUVlUVtlW'
        b'Qt2cM6tqqrfT6OpTat1KJ/LsoM7GGic9GrHoIVU9n0+QnmaNS4I1EWkRBONHokCpgBpu5FLL4sfF87jlqqhxZxvtK5OzZn/kqHthx+cvLSOTPm/Ncj9TcGSn0wxZ0A/S'
        b'nbt9vysUTJ2goLRmd8J7Zkvsn7s/X7bmlx2/XMy6uv3RB2WBjtuv+z768u7srM/vv3QYVm5sSoo4ALfdWqkQtLN3mXrzkYmrrodtvD23UrCz/aA48OakT6WyLv1PfrOc'
        b'fHzmhcBL8a5dn4prjqTczMparFGdUjzF+1ftOX2fTvhs5aroD7dR7htG4ldGX9hmbZet8dfRmOeVtxydja8e+6B04aNRx/erxz1cufxEw5XFrjqCE/mep4y8ZuQqLTH7'
        b'acma6wpfFL8I/Uv2loD7ynP1Fn8ma9GKer9urau71pbHX/Ukt+04bjt12odFmmlmrdLNnK6hXGfre9/Uis/tv1jmOq0068vka2rDG7vsv34vI07B6N7CijsGpllqDZfr'
        b'9t51/m1v/bV5ezf80mBeFse7q1dYo+ctqPjubtkH3OvHWheffW/hko0/bLX9ufXlFxsDKu9uO29178nCWV/f+6j4gEvRy40XGh/sHdnzosJ/HtNRsSXFfdtwXeO+x7ce'
        b'ljoPLnyUYrr8RE+1f/nGDyV7Pgk27nPnJPXH3u2HS/167vz4WfXMxP0KHts+P/bJN9Cn7gffD2qoLw49Pn/ty0I9+rsNvywJ/Yi2KawSbKn57UlzbfZfNRtTa8QHr7Vc'
        b'FfUIGveNJC09AGYvUo4ZGL8wbI90ikPUy+8fO2cMGl/97jduy/a5OpOkfG2yHp0u5EXxsTeUkj/cSikVce39C9nIV/Ntokz8sVsSgRRTAbXceeCg3A7dGVbjk6IYcB5u'
        b'iRGiT5cTBxwD7WANu+xurJBEgYOF5FsAt2AEKRXQwl1uCy8QM9qASmwkvmpcxYIFGppgq5YWPDmuVJGaBA/wwP7oPHYNemE2XCeYiTQ3WoGPrb9LwFG5GXwh2ANrQCfY'
        b'HAOO4Q33tZwweAbuZrOemQN7BZFkActJSaGUErm6sB+uY7OezQSno4AUQ9oRTwOyIDYHzf8fc+8B0OS1948/GYSww94QlhDCHiJDFBkCYaiAexABAUXQBBy4t4gjiEoC'
        b'KMFFcOLGbc/pur0dpLEleK1Xeztve1uttna9b3/nnCcJQbS3va/v//3fXh/yrHPOc8b3fOfnSzuEH4OyxcLY4OxQXbVmFkzQDM5DGVEJ2MBry5EsLUB3qdpanPnOD56O'
        b'J3L2uCn5OpQV2MGiCMwKEtjlepidjXADhkncmgV3w4s5aP+yAGeYcD9Uggt00q04HmrUyKxcXW/PYpbx4S5Ssgs8ki/SbXtgPbhOtr5CKS3dnxtnS/D2cgQcVyeKk4i+'
        b'dB88LnD+P3AnJlBlL3Aa1knPg5urhMXRSc/nmfT+Nm8Cg23liuRSR1ckRdnYq228cdqL+qZ6pb/GOVDGxmcrmlYo4zTOQhl7wJmvdGheI2M/sHWV+ytNbtuOUPlqHVxa'
        b'spqy5HM7KhWVbQtUkT2F/bEZ6tgMWVafw3gZQ2vvIJskE8ti5eM19n4DDt5K5p58tE3jbCDNy2Tsu64e8olKtrKu01LjGirjDDj5KH26AjsDVUE9GRrfRI1TEhIBnZzl'
        b'LHmKwkReIqtCp/ZO8oDmJGWKskTl01mmSu1hdKcr83rKNP6JWjcfWarWzVNprnYLlplqXVw7TBWmSlONS4TMRGvvIo9sjh/wCFQxTpt2m/aweqrUEeNuZWiCRBqPHFm6'
        b'1s1blnrP2R0JbMrpau/wHn81lrB+vO/h05mqMj2Uo/aIkKUPuAUoxV3zOuepkDgzSuMWj96xd9a6I5FXXiiPk6XhhDK1bfEqVreF2j1GloZ5lcymTHmhYsZtB4GW76+s'
        b'7bSQpcjKZPNkWQZGRuvu3ZR2H5VSJE+ic51o3MP73WN7omRp95z5tOjJ9yGiF0tV2W3T66Thj0XX3PnKqLYErX9AV0Znhiqmx1HjH9fro/ZPlKdrfQNpMWxEIGlwYU+0'
        b'ZkQclsD8lQUq284iVbQyqSdW4zdKi4Qxvfj1yAzJKWheBIxQlilzUCn+gq7cztyeEb3+Gv8xzz/P6czpcdH4J6Aznm2LaZPpHrOn0xiUXeAP0xkUz8EweYbOqWfmm42D'
        b'2oaPrsmLZBiwWmvvvFX0tByX8oHtiJ+lVmj2vsLMNMu2Yr1lZZ7tbkpzeZZ32IvEtRV32KXiWvEds/Ky2jm1lbVVfy5gmHhnGuc4oTlDvGjIwcFcJzPh9CZlmDP0+wHJ'
        b'TH5/hj3chzjMEqaRAGCQP+ZRtPxBQGxNkKxExbAMoLXslwhaW/GsDGJCDcfDRmwnsdfsX+UrysfhGcT2hohkWIQduMSC65eA7soJtdFsErtQt3/TuZIDSM5QvsoDDsDl'
        b'7Yq/HAa3FKdnWlN+biz3w+PpUWI92+FY+jEQKis8aoO0ykxPq/CGidOQVUwiachKVZVq+1F9lqOMmHyOhI0HiYMPz+P1OZTeHZYeUlw2ORTpmX3sBFs+CQ2p558ZTbzx'
        b'/R+P5jCJ19AEYxB6rx8XMKXYs4H35BN6pIrs6LGqeOtVimNu+aVleyUVfpEVsOHrPzRW0iFjZakfKx3o/KNqNFZWzrJaeeEHlr7DB8rkjw4ULpgcphoP1EI8UC4vZ6Aq'
        b'8ECxdAPFoH0jY9j/K0NV/u8XnnkejY6rWpZOREcWkhi3s4nsSE0lktWmeC/mSja17KH37epRjnGTycW6EiI08rlUsaWDaZrOwJyCxoS9dgIXjdKYbDeKyJEr4Qm3gjlr'
        b'sIWBghsx4NR2Wt9wuQRLbPJ6U36x5V9qomgZlgU7wfUCBtwXCvcJM7MQizWNyQDHV1Z+uedztlSJnlgT23CuRIHmkxutU6gNW8BttMu0ij7aWpxRoMpz2f8G7x3zZqsy'
        b'7ryosvXHSueZ/PWf0Z9Ebo6qGFvkPz1Seax8XXe4yfsmOZ3bU76eWlVmVfZ+WUkx9+NXfd/Y/I2vCcf/l7VHf2b+i9361x1/e+PHReaWo74usxGbDDRGxG8M3WpaMIvn'
        b'fdQlgq343jXVleX6zsDbY8W3VIj0MKjDAY7vCj4RcGmWrQHKwDlhaFBm5DicIRm0MkOBzJGwn9GlcL0INGKnySFst8qb3JZm+IuK4BZM/xrhjnxsXNqOWF+gyCB87wx4'
        b'AWwXRVUM4vkdZy7ngq0036uwgZfAccIVcxH33sDAyZl9nbLIXR8og0fA5TpdjkydEakK8fM6RMa9lUK4GdzIJAYfdhyOXL4EOp7QKM1bMxEvvgneIGG2BvNUA1grMP0j'
        b'ex1ejjpDC72kLTH5XVQ6bw7eSCXO+hV9mNLZWTD1dWlJaEpoTtqaNsDzlJd2LFAsUAVqvKI0vOitKZ/wnGSL5QEaHl9pq+b5bU3R2jtuTbtnZ/+Js6dcjHf+JjZiBnkO'
        b'LRZNFvJCZYpiar9HiNojRDVR4xF+mxfx1JRCnKLPQy5lZbsrpyFne57WkrdL1CCSc5UxCpvblkGoxJa4priWpN1JSnaffYiy9n37kK1phEcwIjKmkq/wB7F/FzGEdIBu'
        b'r6dpDf5kcphhboQDIiW05iH1JwkOprVD1rqZ7u9j7HGUbLWXmklJGAWUhFnAkLAKmBK2KzUNkQ50tET/TGOYBax4tGsQnSlx1cZ60xhuARsTJj2BkZjM5PhSBSZuVAGn'
        b'wDSeKTEl51x0bkbOueTcHJ1bkHMzcm6Jzq3IuTk5t0bnNuTcgpzz0LktObck53bo3J6cW5FzB3TuSM6tybkTOncm5zbk3AWdu5JzHjl3Q+fu5NwWfQ3WrXrgr5DYkbv8'
        b'CGqm3SDRTGOMZEjs0HNYa2yGSLEneda+wEviUO6NiKjPHdNccTWOtqhcgEaq3tG8IH1CCn8hfY1PMsWEmQsYZKsZQvTN9PQWh9skc40SBhh6mOzUZgbyz3m5yQLqC8yz'
        b'qitrK8VVlfVlUpJOaUjbK6ultThYJMzcPGGRWCJeyMeLMYGPU+PgX/zaGr6YfmVCWgZ/XmUVenTYNBu6pXjlEQiWbG9bISYkEzKR4Bo6WY94ssscnIRbQ8IY1HiGaRw4'
        b'N5pAsFTBm+CGxaLFBeiW/tFC7hKrRYVway62UDtODUF0soTPtZyVSqcrgGtHYdT2XBbXicZsRyRSSeOgN85JE2IU7F2iXEbgQkQ/FcwV1p602+xN2AyPCbNzw0iGaiFj'
        b'ETxE2QeyYNtioCIFJ4Dj8IAoKpsZDvdQDHgao98qomivWOWS8Yhi5zCADMgo5lxGJNeUzppxajTYLNKnM7eogcfBFSZUgJYcGrCmhZtJaDnGcGzMyWWArWAnZQ07WOPy'
        b'QTPxN0OVbgbbROBkJmoZKsQJnKBs/FhTYbOU+GiyMDKPTj+A3j82EdH9S8wVHDPaL08BWyJEWbnB6DbTE14iCkGwzgVeowHdDweAK0YZBIpWMmEXOAVb6LuH5vsSrN3t'
        b'LHAYnNOB7YaDKzRnIIetfiRNQzq4TjFxnob9cDPZrGEP3LyAZGLINYFXPOlMDNawkZQqgjsCh2ZUAC0JLMe5HKIZXlFK1LrLEjOKqw7NZ1DEkSsAQ5cWYKDco8ShEu7x'
        b'JJxCbBXxJavQZBSHbKyIxhpq3KtWq2qHJk6oBmspX5w4AZWwnbz5KxdDzFNBh82Kcz4L9KCTYIBrYGMCTucAutlrwFY6nUNxLu23vgf2gCYMlqlL5QC7p+uyOZyCl8lX'
        b'z0GlH9Ilc8gBRygznMwB3phGHHFrvScIDbkWKuYPy7bQ7EZGeyHYMgFPFyLjhDPhQbgFTQcla1bdrMp832/Y0i5EswsvNB8pFOXBCN4F+8CFrRvf916YMk7mGCKb2mcy'
        b'7mPzvb9OO8MwYzeOdL7v4bEz1lncfmdnwdVck2mlI6K/feeN8L+UfLdp2ST+gUfv+o79oO5C5BcB43jhtqlfVf309gqHy85WH7m857TsHyfPeZ6o8BY9XZNrW//PL5Jg'
        b'wm+bl1/qeRhgl5s3d1TKO7ZbN50NfW/K0cR8i/tRviw3s5+mfm5ycNXSSU7TtNUWIy/2ZFlcLBGveMf1+o+nXp9x7Qk1++MHZaYP671m3ztbMF+8K6cw+fsZ8gs3phY/'
        b'zludOsL5x5SfOybErq+MTNxtvv5fohXOa5ee8N2Q/be+tycsfS2kJX7knqX1XyqKX33957YglpdzbLlk118nTHF+ML/4GKetnrWO5z79jL2je/xHdfOqonze+/Jy4jvz'
        b'D17/9HvxjA37gxMLlszen/H1gc03A68vLpnw6e3/nh229mrJx90/BF8vP7p+zrfRh+JsX/3ivwq+zHWrt78QH9mGDoufnLq6e8wX6Erzmi9yf/jnqq/iry+8PuMSJ7Fo'
        b'ydGvL977LObX0dfr7afUJCxZnHhR9VuJ65OOr7qW7ln5K/PTb2p22ecKaPzbOeAcOEkIHlUNL9PMk8V0WlN5cMp8UU5wGM1WWVSBbSOZ8PCoJbQWtWU+uEHQW4lJDe6Y'
        b'huhVI3OVB9xFwypsWAF3WJD04HprlyPYwmaDDi5cP5NgD2fxQNMw6BeBi84q5giv0exdLzwJ2ybBgxjxH9NNwuRj5o/QxeuV8CRoDNeTTcpC6gz2MWEr7IKtxI0I7HfM'
        b'xm5E8fA8AYaZB7roBp6ODkQvDlJUrOFlI/71bEISVJC+yQLHEVHORzQVXgatFKuKMVkEOmkfqyNwEw56ycdktXgyIj4diLpagP2k5wpWIv6zMV9HWMHJXMq6gjWqbAX5'
        b'bLA/Cd9FzOggYYXrV1J2cSzQCW8ABfmwGtBUiIowEFa4AbXfbgULXPIGRwlkiSu4kU4aQNNWymIi3OuJvhwcQ0XgIcqDKtiMntDRV8oiAKzFSYaUbmLC67uC9SYTELM/'
        b'COG7kxma40cKL+ct1SdYI3TQGdE2GzNWLTwFdtLDchHI8if5kocwRaI4XKYrXAtv0Drly3PBFjwsBoIELhZSdvAIC66zWUkjrlxHDT1CIFFIfhkLNJHacpjwEtxsQ0P+'
        b'7AUbEc1qzNdtAOAKOEVZp7Iy0NDuJGgbYA9cB08J84ja5dlMMSNMEPUaW2dqi4ZUTiNUN4C9EtzxZGdG+zI8wKesy1kJUeAY6bDV8Phqeth0BE4aRtmNYoFr8WF0AUfn'
        b'RKMGZ2bhA14UdhGUnTULHM2HWwTWL8nlC5vYhiL0GiWh5+kYuqH55yezdPnnC2jFjzJNl3/e3VuWplOVenbEKeIwjIUqRuMegS/TV5IVySp/GtrirldQnyBZ4zWmz2XM'
        b'gHuQykHjHiZLu+fuTTKBZ2i8xve5jNd6+ihHKGbi1M8D3iGqwp6g7tka7yScth77ggV2BXUGqRI1vnE4g7fWg489j5RFbfkkm/nQU5zfu/R0RXdFz3KNIVv7gE+Yqvb0'
        b'su5lveaa8FSNTxpOZf7ciziP9TLFMhVX4x2Jq7/v7Yf/aF09O1wULsogjatQxiHpqfnKDI1z8IPAMJxOPUMxWzW5J717Vp9HIk7VPlKRh//Eqz1CH5uyg9zk7HbLh9aU'
        b'IFy1XB0U3+urDhrdH5SqDkq9lfqmrSZIJLca8BX0LOmtVMdlqn2z5KZaYWSPQC1MkpvedgnSBsX2zEXvyU3brbQh8b0+6hByQ6ANjuhxVQcn9qaog5PRXRttRJyc3WGp'
        b'sPzAJfTfN83oNEHtEYb/jkIi4WMrU12LeTjrek5TTr9DlNohqmdkb7g6Ovu2g0gbggYb37jtILjvE0A6zt27Y5RilDJb4x4u496zd8c9lKlxDnkgiNB6BijnqT1DVct6'
        b'TbrX9HmM0Xr4KyejmvDfaWqPcNRHwbhG7FkniESfFJTYO04dNKY/KF0dlH6r5M1ITVAu3UfLbpmp47LVviLcR9E9WWph8r/ro6ieeHXw6F6xOngs6aOoeNRH1grrD1zC'
        b'/0jjjM+nqz0i8N+pqLtQN+kaTboprymv3yFG7RDTM7W3Rh2bd9shH0MrCLoFqKvQTZzdHHfVXmsjYdmSxh5gv0Aj94c05oOL2igheBwqcZGxJD2rAEvS3/9JSZrkfG3l'
        b'BFPHLGL/s1zgJHGQ/4vzIA9SH30a8HdQs42SD/uSNNs6EW0wjfTLyfuty4JrOkdaWV794ozb8ag3+3CzHJhDmqXPuI3fFtfWSV5C3lldJlf2nLlRc3+vORrcnB5DLwVl'
        b'VInL+ZXz+JW1/EopElPHRY0z9NpLSRYs+ZR6cfpi3KIPh7bIg2SUlZSVVtbWSF5KfnSSNVpo8vutGMCtGMwK7KVrBZ0Q/eX0RgU9RGZzFtaUVs6r/P1pcxe3ZzCpcyDJ'
        b'Yi2W1vLpl0teZsPK9Q0rW1ZWUvc7GeRxw/4+tGH+hobRL7/0VpnSGBy/26aPh66xYP2krjUiAWh20wW9tBzPpnNKy+aiSfp7Lft0aMu8yeonb728lNwb9cOnXzW/16Av'
        b'hg6fz5DV9tKaZJjqetX07zXpq6FNCjDWm+ER1CvNhjbLuMahiYmx8yqziGVwBqUKjRSA1Qwv1GwjhSBjiOqPSmEQheCwqy823Q13BuW8wFmVtO5/N20yal19hDmZ/0sr'
        b'ylDvSVAXoqlvtAokZXRy+Fo+GvHqmtpndJHPTYct+cybRdJh/+vmZJxm2d3ZkBBbQwksmNbf/ixg0FFIyjlVSCKpHPOMLJtgIXpOIuZvMS6et34nN7Rs0J90XnlZ7ZDE'
        b'2HOnMCgPAoHX5xD8JzMz49okM9GM+9bIW/T7GVP+o8zMf8SAjMby/ysD8vBZiIbNNeVblhTjNopFfx809Ze+9SbF8dnOGRtvGSF799YAk0rzY+386iEaQT5FtKjtIUbK'
        b'CNgBTusHEfaA7b9vZJY8/bdDKtUNqR2lkxTRkAYKVbGHFsjS9uYPsTuTMbVn/EG7M65aUoyu/mBsd67E4+v6Z+3OAibR3Lr7wosi0SrYhWO/2DYM0AWvgZt0wt422Gkt'
        b'EvLh8Tx8L5oBzhWDnZVvvTaKKcUpXmPj52I3bv4bvLdKgcvbQa/JXntU2GRauiWqLcIket3y7bbbX3m7PifYsj2U2snnNJft0s/k5/HsJDja8KX/Qoc7tsM6mXSrO92t'
        b'Wjb3+6lTGGxb4Q/WDNuo+3x/tXN0Hy96yJp5Xq8Or0kiRn36jb5PUdk/TMN9avZyksmTNcMmVJHOAk0ZLPkvnzaGmqdiD3UpzR0gajjUkiPlS2srq6r4S8RVlaXPEMbh'
        b'LhqcvMIMoiKvcVxBcRnKRSyKv0RbO2JSpUNoO0u6Ct3ZcmH29VG0rd0O0csYZa25Hys1wW+ClX11bMN6S37B1IcqSgHYhXDzGyN8egQeafL16TtC/e56eHE4Jpyvw94t'
        b'4Yonz+WWccVRZeOiZ6xlBHm9uqP7DYfOlsitzpdWBm0Ic2al8ryPbiued1wQ0d8VLTnKonz+bvdjV4KAS3tq7vWzFGI9UYo1rSmirMFF1nhwcQaNwrqB7W+w9FC5M4il'
        b'p34B0R3OpdwM9hJEGKKIvQSeTyekvlZgbmQDwgYg0JsH23AerSc0JMZRcJpYY5LjidqQGGNAcxBRhUZbgJtY8ZUzS5epvNiPbs661ZnCYnAUNuRngRNsilPF9AUndZ6u'
        b'HWDfJBG6HAI6wQ0OxfZggLNwyzSByYuFXeyuYWQw51ZK55DRHRQg9VfI6qmnZ/jDekSUXDxaVrWs0roT78oVLSuUpV0LuhZo3bGnW8vqltUq/9Ohp0PR+X0Hl5bcptx+'
        b'hwhlYdeMzhkyxoA9Np+79NsHq+2DsTMjR8Fp48pSsNtldlN2c44yUu3gT99WFWrsI+lSh9jDn7OhPdccbuQPIKnCGoGF6PCLXognoUJki8Pm8D+1zxE6aCkZg8v8DJee'
        b'g38RKMBJ+Fc+PmBkHEkGPnyN6XQRh3ivGkiSJAld0KUAdnwx0N8gxh/2ApB8jYeKhURZiQCfvoMBBbl6sekOVy+n3OHQLP0dDs1T3+HqWdk7XINTxL8M/UJw+6z+51pR'
        b'7M74HBw+N47ugA3cUic9Dh/Tivcdh7J2VEQrauXBaquAp8xpDKsRjylyZFHWIx6SC4+WMPXwdaMwfF0CQa9z8hrgCegrTglbMwZB7zCenf1YBkG9012KwpdiyBUdnl0M'
        b'xrMbSfDsdDB4ozEM3hiCgqe7koCvJJErusowDp/TOAapTXcpFl+KI1d0r2FAP5d444IwLqrL6K2ZP3DNrWIeOVGuPmqX8M74Q4noz9asp2yelcdjCh1oaDysVV8O2mE3'
        b'PKdXgVPmYBc8BnYywVU27BxCfO10fx9jlVCy63MdMTjEEcMF/aMKWPFM4iBgVWRXZB9j8mcdMOh3Ee9mTtwYaAcMtwhqptkzLg9mg/UWWMQzyA5mgWpkY3cNoxrNn3nO'
        b'BPH/VkOesBjyBS4F1vHMAndSmh0pj4efns8wPG9peN7wDnZB0f1zKbCN53hRXlSBRxGDoAfSjhJWRdZFvCLbIvsilxhL7CIypEyroW3Q/eOif2aoL+zjWQWexLXFhDhe'
        b'WBRZotJscPuKHIoci5yKnFGpPOxoMqRU62Gl6krEbS1wJKWa6MqzIWU5oXLMsIPKkHJsjPrQGfch6hcmdlsx6kVegavEttzGrFzgdcdaR+DRHxyEXmltQVH1X5un8Ide'
        b'x7s/+ivli9HGb8wOYFcPcS1fLMH6w8V1lYi0mM9DMhN5phSdltRiWb6yll8rEVdLxSVY+SENMzfPqkVsRI1EV6ShNLHUIMoi/qOaL+aXVy4pq9YVVSNZjl4NC+MvFUuq'
        b'K6vLExLMzbHlBUvDzzTYwKaMSy9MCeOn1VQH1vLrpGV83LpFkprSOtIUH3MBk1YRv8N8JubTEGC5CB2STQwxn0w9xCTxqDE1RHuavMRozwrEhv08zKNGz4It1H/jH3Kq'
        b'MXQdlnbROBn3N+k9PHhkLErD+FlEy1lag2pEYi+/bFmltBZfWYq7cq5O3Yce1Feo04bQdQ7TkSytxI1Ad+bVodfFpaVovHV1Vpeif3zxokU1ldWoQGNt5jM8JYd6lqe0'
        b'yqsbTeHsHIh5ajFOqBTulWmwBcLdcEcOyXw0KTMnT583AdyEWyzgkbL5dWGohED/IOPXB19Gr2QJsuGGIuzHsgRuMVsFldOIV0Y12JcHm7EJ8zyQZ7Ipk0AGlE+E1wiW'
        b'Fse1QmhKzTfD6EDgMFTSSFNdoKOgIBQehWfhkSiKFUbFVtokMf1T4fG6QHS/Csis4LkJq+F2oSH2FbszTZgUOplJxQlMQBNYB7tpsK69dWCHkEnV21JSSloYRzjr2xLs'
        b'fMIfaU0V59wWZVJ1OKFMITyRrvf8OJKHPwluzZmIM0SEwJ25dG6qiTWmcG0OaCM+R7MsxNLFJjjL6xEK7qLAtkDQWpn0bgZD6oF26fnbju+Y9FfsI+Lxt+WjCh18Nga/'
        b'2jnCzs501GfrC61XUpkXD3nxtmSvmsmfcoPxza/hFt2a821p/pO+nvXt12/XfydbDYUW/323qv9T7rKJPl+l+fzzo2xe2M9xeRcXdeeOende0ud1Y69/5XVbZfFpoc9X'
        b'qzZ53X3EmxEN/VY/Cky9wEn+y0SQvq7goN2Rni6PTz/+5uoNv01XV3/zrdVHlgdu1s8b9Y/LdlWbHx2waehfOFJyaPLZVR1eqjGfX2+8leg66uoXY6QJR2sCbD7/6kbz'
        b'5Wu/UU6/rJn44fsnV/3wYe/U9QcXb712ULX4nfHxK6usPpc3LBI1/vXk7vYpAwsOSMenZE1tOPOoZIPw7jceym0XYuR2G17RfJWTe8aJ5dhRl37xJ8aV41EL1x8TOBDn'
        b'Awt4CbQSry2KORfsAzsZkWB/OW1dPwauuw71rfCqwd4VXCQrbyOCQDXc5Ux7ToH14DzxnmLCrgBd/g9wHHTNFmaC7XDroMtsOeymPTsOwU2+tN8HUDjRrh9MeBhegBtJ'
        b'0aVV8DzGe1k81difdhe8TL/dzQRrRcRXTgj3hAk4lJkDE4kOx2APsaFHh1TCRsR95OGpFMyhwFHQag3OsybCHlPaA7lxBNwmDIfbQiaAK4hB4QAVMyTZmbzMg4fADp3T'
        b'yT5wkMRyE6+TVfAakXDGFaYIs+Gp5FzUa2wfBtifVEdD6XQtgIdIBFwaaA2h6Ag4sC+daF9Gg5N8nRMEbCCJykNRu1rhaWdwkZ0515Zu1h6Xetrsv8sH9wnHnmkF95eR'
        b'iEHQCI5wQGN+ngjn3WgEJ+pIy2xBCwvsmjmNdnc4gTrhMvZmMBAPuMnJuoCVW1xBMsTAk1U56LMwGBBoxI3Jx3ma4E6wM1wUSvLDYGDE8eCMKdjlDnfSmr+DYPdo2JgD'
        b'zoLm7MGE8/AcWE8qzYctZro0Kzo0HLgpGqdZAQ325NOtpoFj6KtQk4C+Pg4Fz4MuJ1TUzcIygfl/wKtjdINnoGlo7wXnoZvqUCeGKQxaCsyYhqRAbyz73XXz7wvI0LiN'
        b'73MYr3X2alnTsoZcGqNxG9vnMFbr7NqytGlpy5qmNcpajXOIjK33aUhSJKnYqnKN+0gZV//U6qbVytJ+Z6HaGbHNTi2iJpGSfdshYMDVU16hYt12Delhal3cOrgKbp9P'
        b'VM+USzPOzFD7jL3tkvKURbmF9rmG3Hd173BWOHd4KbxU3H7XSLVrJGnNqN4Ytb5JD4xL8+J3lCvK2yo7ahQ1Gq/wfq8EtVeCxiupd6Laa4ycRcq9jz4LR3iVaJwFxP1i'
        b'jMZrbJ/LWK2nD/aw0PoIiMGeH0hcI3xHKOv6A8eoA8f0B4pvjX8j55Wc/rQZ6rQZfTOLNWlije9cGXuvzVNXVPAHriE/PzXX/ZCSNS/0zghhvWoekTGa9XqIeUaC6euj'
        b'zcdb6OLCzI2s25h1+QMmbho3w2DUNrJoozlEuVsYxYBJpyJh2AfjZvj8WYu2giOgui1i/jOLts5MY/J79pBhs1Jv3E5CX2Bk3I42sEHD+R4jnuclWbuJAfWjF9viJU2o'
        b'j8fgFhoMqJICzjOu9EMhO1i0jaaIbdCPv1wrzbConf+/WWkkXzOf6aDnGl4yeBITYngRvCY4V2IX0/7WoOGFIbBk2jDXChi0J99hHrxpIJ9gV4meghLqOQ5ee5H5ZcQz'
        b'U05aUjWHwHj8jhVm0vT/oRVGgaZHqoWRFSZ1+suzwgyJDiMa5SLG/1J02B+AhmHn1SVRBAC9TrelGrZT7KXfkBOcHQKOFdIO+2SvBTddc7KIwhU0WMTDPRmVK+2PM6Xj'
        b'UClLrinOlSjq7qBpcOIVitEQZWnpsz3FUk4d9d3Uts6n1XWE29sVb3HFR6I2RwQxctc/SpVL5MXH3ncdFU1VlXJ+szQRsJ5E4OkiA5uATL/Hd63+3S2eAzeQ/IhlsG0+'
        b'cZKdDfY/BzsGtNOpBAsL4O5hG3l9BpmILkt/x8AxSLqf/tGZqTcmCeiZ+cNUNDNdPJVF/QGj0f+Js2C2xkvU5yIaGBH8HBuT6e/bmF4QdUQsTR1oDufqdxZsaZqC57Ar'
        b'VrP+KXMTjjrSmZs84bVyEXYQRkzsFdreVAUO0zEEJzPEIiSbMeBFuIU2NzHh6coBhg9bGoPu53F3YhOfkbkp6pPXiLlpy1l5hGn0up8GDU6VVPtdTp+0Uwe282+U54Of'
        b'/RMeFZcXjQoZB0/KYH0aO53BtRU+dWDZRj3kUj4Bw+xPJi/u8edULFGi/h5nMWiFepoy/c9aoTDOD6KDWMc8hHQYYjrnU7QxShdjxCliFJmibcDEQDxMXiLxwJqQeebj'
        b'y2r5Yv2Gbax/GlR9LJSUzaPVEMMc2sLMEyRltXWSamkCP4WfQOKoEop1Q1TMr5k7v6zkWRP/cEuWSV4dNlkKzOKIPIS1sUUTkJx3eUro5ClDYo/0gUdgbYzZfJPVdO5n'
        b'RbKz6BnlxBBpHK6bTU2yMIU7ePBwpebRK5S0Br1W+tcH50r2Y0r2Kg/YASe0reUo+LVeqVzhyJ/483LOTOAUZHBFrODd4I1bOB7VZp6lWF1WsvZ4dpmleNK49/e+4fKW'
        b'y6ubK8P6NnlMnbk2/UhRPCvVN64vr7p3fw73b+Nci9Au+f5dxoGlVpsurBJwiPRVDHbD3XSMQTnYQEubsAO00I7kKrixEst0q3ShBLREVzOZSDj8ubOwoOu3cGgYARe2'
        b'+BOBbwxampd0UvLIlLmMyIwZxACX6ARlIoOoBbbnUhbTmfAUvORPkkPGwHZwYljsAeU9v5BG5DoLDv2Z6FAjFBELHB2qmzJ33J5Zt0b3yMpdQK+qR7WYgvor01T+2AlV'
        b'4xyD0R6GyS1E3Bh3q1AdkKVxy+5zyB5w81H6t4XKTLX2bi2JTYlK/66QzhA6TZ/GPoqgfY3WuCX3OSQj+Ulm7M3KpWkwsfz8vr2LO0iIdZShGwsJxzCQvzElLsOUweXR'
        b'n43/PPpClqKUoplCXcA5ZXAueukoD/V1hCLUDncUq5mnDyP8nxOIFLrMFxCI5zqT3LkXyCB4bqfbf6Dx6Rxw9Pg4l9zOg8stOy1TcuTBiC2Npnawv7BiXSz0FDCJWA+P'
        b'LLAmaBRJaC4bwh0oN7ifXQ/2wou0puaANbisC74DO8F2pi76DuwOf76/icFBIRnvSc+b27puI3Pbh57bDwtnMCh37363YLVbsCpG4xaBpiuSetG87uMFDNmZXjQjaQS6'
        b'QW4WVy85jeZfqX5nQvPvh/QZfxbrAG/hSCogMdCmUvGSsjliad4Qnb1BV1xN6fcoorOn9yguEqeoGM7/isYex8B+Z5iV2IZRqsti+tw5mWKwo5TVirEzqJh2O1tYswTt'
        b'cDjtmr6cPzqB6Wd0vZKAFfnEchKCtfcL66S1WHtPLxhpbWU17RqLpWOijqcl5CGOhNiAggorNV4buG6JeCn9eajN/1ZTb55XF41n7n4vDDlt2DVfsGNOnK3bMwVwO+Hn'
        b'xqDbPULYC9uzmRQjk4J74Q14hUDi+bSXECy9RWzEAr6pYNRupt1M0sU0jl/E5NtuymWjqELakkqckdaTlOnz4KF8VNokCrbCC3BvpSI2iCV9F91/8vRxnSzXGvB5m7wn'
        b'VLgf8urUzv8YhF297ddLueXOVFR8FFs9cxnvW+F/vTIidNybftF/t3w8aqtNjgwsshfmTElJPCkeN2f2mcoTaSlX/nZx112nW5uuXhux+XPmmH/mbc9cuPfoN7HbWvek'
        b'bTqwvP5kd8a5WZtebTi27K0FR1lvXDuRfG53t2LLP6pbWys7P/OacrE5Y+26xPLliQ0N7e99xam4Js/c4hcuyh//z/qs7R/tqf3ogOMSeGpS+PQrB+0a3hF5/H3FPqXv'
        b'bw1Hb5R8/Iaz6zx+y96JOnyISHDVTmjAWYBNYAc4BToin+gsE5srBkMCKW7SVLyTw13gLK0mbYKtpkZqa3BssWE7l8NtBPDNhQd2CrN16lt40QPsNy0nbEIEuOQpDNaH'
        b'qpnBm/MTmaCjFPQSgpcINuUOVeH624dyKKLAhb2AznEfa4WGqNEIBgIqwCVwBh7KpJXiF0DTTKJ4zsqG13WKZ7hz6v9EB8o3Bhgz1QFH3HF6DulE1wnZ1NBk85Fkxn/G'
        b'EjhivDH2bccAlZ1OHdoWL0t7yqKcRjzk4DTHMxQzVK49KRrPkU3mNKiUkQLV2a1lWdMyJVs5UTlJydU4C8gTTStk7Hv2blhXWq6sNdaVKh3arXWKTHeZhaxWZvHUEdX0'
        b'gWPAz0956DJ6ltyhVZCvWNqm8lggyi7VhwV55qleptDHPDVCp4I0M9oAev5tlI3UjDLSPtIbw1X81jV0qDFWPs7AG4PPd39S+SiZSBF3SKIMJVuEmSF0hPZvqcFuN+wq'
        b'cXV5iakR1bLTUy2c/DLZkt4zZrNms2ebzOagvQM7BWBDuiVxDLAp4qHdxLYI4zjYI+kHpx10iLHT7SmmhRZGewoX7SmmRnsKd8juYZrCJXvKsKvGe4q4Gm1v5imlpTju'
        b'pLps6VBfPGxFpS2ytIG4pEYiKZMuqqkurawuNwJSQJtBgri2VpJQbBBEiwmBx9tVDb+4uFBSV1ZcHKKLcFlSJiFORMS2by5+oR2fXyKuxtuKpAY7Guld0WvFErQ++HPF'
        b'1QsG964hduJneLbnWonD/siuh3c5bKaWLiorIS0OoXuJ7GmD8UzVdQvnlkleaMM2TBO6msGAo6UVlSUVQzZP0sJq8cIyUkMNHT2h/46KmqpSRByMtt5nYisWiiULykpp'
        b'+7eUT4dFhfHzsQf60kopXQPiBypqSvkJ8+qqS9BwoWf0AkgxeVHfmhJxVRXq87ll82p0O7cBJoQelDocxoGdHcTkPeMxNHy5wQMtgf9sjNOgB7y+XL0nvO7duVFzh79l'
        b'HBn1zPN43SG2pCCfPzI6PjSSnNchaoombWmZviv176KpRI9SGGl8Wtk8cV1VrVQ/xQzvPncEAqV8OiHv8md5F93I46YtQiw++vUcTmoIS2M/jKUJpIGswAEOuCSNgkrY'
        b'KkHcRA2FdqZTfDpt5MUisMdiSWblYgbFgFsp2G4eI2AQSAh4IAKcEOaBjaAN7sSJMnYyUr3BxjpMAIAc7Mq0WLJ4Is0TBYWFBsGt4cFZuYg9Ola4CJ6tnTwBNIJ9xC0A'
        b'7Ak2GwXabImtfxrYDRRDHBloIYF4MYAGL4LGUTKbCzoXpxEmaayjFXXLYSRFTSi2XBUtpYgfAtzB5sHG/AgjPwTa4zVEEJptQo0WcmDrZLibfGIB6ALrhXA3h2LYUuCM'
        b'BTgQ7k9KjvY1pZQz0P7PL7Y8XTOFxusyjTCh2sMcUb3FIVUSP/rix96IsrkTk1TI5fRlFMk7VgfPQhU8hEi4ReIaymINaCLooeSFwGwutX2MP95Eqr5AjHxdMkUQVg+C'
        b'7QSfpSCT6GmzUNu3CzFjafgOdCMzJDsnLAs7bawL5lCwUWC5eDnoqRuJi7gimI95003gxlD+dLsA8TWgu1DHnQo4FFgHL5uBQ6ADnMoQcGlElBZ4He5Dnd8Ed+cYmXTr'
        b'hTQGyGV4E5WKeKdO2J7DIbgmFvAKPRmO55TAxhIMzoWBOwiqCdxSQFBNCvPYNKiJLfoMHa4Jy7ESHiIg29ZiJ1GZuS6On8CKLEYfQwBiFGLQQsOK1NTTmF8EVaR6Aaky'
        b'FVzO0EGKEDyR9dFADluS6nD8AzwDD4wQDgvL52UYQEUug+0CCzL7I+CV1Tj8P4TgOxBUHHgqlbRg3ELQMOgqjR2lfcDaFagLj9H4M6cdnYw9osF5eJWGxVlEryuVL2wT'
        b'RU0cgzl+GhRnI/pqfCsN7oc3sKv1dn/iY8GIRJ1+nPax2QkOgCasX0Nd2KADx2FCRQA4TeBWEnBmOD0yTnAtgXCgcXHgKaCiG7Yb7B5N4+JUwssGV2wkcmwhI8IPACcG'
        b'/byxkzdULluxHEkqBGlADtZxaP0e6KomWAQ00ArYV0e6JWuWjR43h4jt8Bw8ikT3RtBIz4XTYNeYAigzBfuK8Ol+qho2ww0Ew6a70IRaNNuBLB9ehA0tzCwE19LQBzWD'
        b'feBGPptiWlLw5hq+wJxO07gObpgttZbUwTOW8IwN2AYv1TIoeyRItcxnZYEjsIkkgwydBbYPfUoKz2dl1mHFw1EW3B+LJhUG5wfnBaDZ+MGltYvN0LRvklhZc6ggFhvJ'
        b'VbsWEW9V5zzUYefq4HnpYsvFYIeNpI5F2YfaebDiPBCZI4rQ46AVnJUurjMnRdnAC2Zo5p2vw4/DS/XwAmoDasGY2RyT2HKSMRDclII2wwukkegBe0uwtoyVYgVayUOF'
        b'+eCy4RncvhErSeu8wCn2iJlgA5kGZSXZRuXUSuB51Lp0uDudlQCPFpLkmnBfLGwfLAhRXQ7F4zBhSww8BTcvJmPpswQqLODFWtQUSzMriQk1foLVaiY4Vy0ifVCTObcg'
        b'FzYVwB2wYSXcWwB2YOD0ViQdgZPBdB7JuayCCTGLJ+D6NlDiArCZvMgCPcIh5cJ2eJaUDNexifeZCWiALVI0Z4/AizboASY8ygiGZ8PoDWRPCNpWGrPM4VVEcsJzc/KL'
        b'sA/ZJJ2MHYKp4fasHLgNEQWwvshMiobqAKEn4CzYtkyEE14xEqgAqIB7wJZYOlvjWijzhecyEVkQhaK1k8em6kGjLWhnoYm3GZ4nlPmhixvV7lhFUbzipGXOpjS5TlkR'
        b'TPkndOOLc6NWZVN0NkPqxzG6H0FjBWw6rd5F0AK6Aba8LwdrU6jl5mzSSUnw+BxwHO279ah5x6j6nAqS3RLnxHYV4gx8YIcdtcxsDtmQ2IlABRvRj0qwFq6jKuF20E2k'
        b'lMqOLz4zkfqgvWb2l3H7Jy/Mvz2Wd+CH+prrcfXXZnbeveDhcvvWpq3j2ek71MrIcXc/4vxj1bgHN9Sn/9tuzYjfXqmsXBGa+DcHH/GX7z5+Ozr6auLVml/WpGx3eXNM'
        b'/j8e/TNwbY989tof12+NnbzXNib/Sf6FPY1LbHovyi/f6FAv/3Rq/udVa6eNfiDd8MPVOSz5/Ke//b1ia6Wq5Eb1p0mTo5Oe9lMlM703LGqeNjvxy5ITy/NGw8Wr/+5T'
        b'Xunx4ft7ipaXuL1xPJVK7tm5XfG631eO2pALoX1AvmpHHNyUOdei9oG4kDUA3vmvt51n7Bv9S/1cq8tXH3Cr9r55au/9a7xIPm/hxbwf++1m7/xWJX0ytuqszwMz+fF5'
        b'odcefxE3zeLXbyYsnjX/7iez/D79KAHYCqemByrif/L71+bZ8+JObJ5618zLtuCEZ2GEPXj3YsPXwQ3fPrldK70jAst7nrYM2I9L9GKxDkmjyxc5FN0rvjrfesXRi1nl'
        b'zq9OeBL52+dpq1ekrc5oejpXeKrryITWN6Xm/h8cqvgkpfKTxvffbDnSNP5I0+lsv/xP4u91xPSsmPT9oV8up3/4mu+C4qafppdWOym2HNmmCM+fnnLh17dMLnwXm/Xe'
        b'Ww8j9648VHfm6U8XFiWdUN57feprI745dn5L/1+/PZO5+LXTjz+Y/2vdVLOb4JBnd/OlucduK6eE/nDnzeULX539147HrR97ZdZM+lr0yT/nJeQkXjEpTNwpL6oYOemd'
        b'8V/XdmtOPrL2znlbKbhbu2XUxPcSAnzP2L+jOvAV2CEc+MR9YsCKf6TvGim6vrtdGfC1w6ZY55ErAoWBs2sWit+71xVbsen4T9Obv2nOFX/+bXPj6CvZ2lVtnF9bfF9/'
        b'b8ul3bnaB39X/utS472Upv/aUOXN+ns8dfOniYnv80rO5ke9XvPYduny8vmv3kjYmti8GDzwmp5sP23Fg7821DyK/HvyqY/fqTx7emPelktnvz3Jfbrj/b/4hHHTvty5'
        b'7/GT/Vu7r4wNuufdXnzk213K48U/sY//8vADyY6aLyaqVkzbuHNuh2P6ujOJiT0mKyzeq1B85dVb8fj+26NuhhxJPNkb0X+x+Ae/B/0P5nfxv5W43n9qdaz9XPxdYczn'
        b'v1GvT73yy/uLBWE0QlOPabpwqF0adPPtslhAac8iOh/YyHJBLM1kcF7H0YBdo4nCCO4CR6eK9DbyfAzmhtiKZbZwCwtstx9JF38tnTccZmrJEi48DM4SldUsXwfsCRkD'
        b'L+pg5JiwCyrnEOt6EGiHjYOee0Rthfcz2nUPnIZNxBfTJ22FEF4Hm7MNfoXgBOwgpS8W+ArDwGmgIuj6tGOhLbxC2j9rsuswv0KskpLAhkxwI4notVbPXgiOZ4MNfJIE'
        b'T4d7iriooyTtXjo4xRCC/U55uXAHh2LHMEC3OIPUGw5Os4ThsBPxt9tC9G6Sy+eQMr1T0V7uBi8ORTztBttpX8jzcAtXBBszwU2SKoBOFLA/mg4Fa08BB0TCEWPBKdRe'
        b'DsVZzvT3gOeIN+FyJ3BG9EzWBHh67mooh9dJN8FGD7GwtMYIhhU26VMXHB8N20UGztfMgZmC9m3ExLrRurd1YA/ivhphYy1sDzdFksxBRhG8XEAX2wyPxYhA92JixCCB'
        b'a7lgPenhPHgS1RqCOFO0J8FtuSEMCiqA3D6cBfeCfZE0atNWeG4UsQXCzTG05yVtC+wE3aT8MaAJ9KJpBmSgW8cJrgHX6GYfBtutUbMOFRoz46jdXeTNWHAD7aCNI12M'
        b'WO60XPJmmg+U0yw37Jg1yHKDzUH0IJyCZ3ki2AWajNlu8UjybuG4QprnBji19iDXHTGejNFS2J5uxHVb5CJRrxtseIK5bhbcCLuGc92zQbee7ZYCGanEDGylcCnC6Nnk'
        b'WVQHXMuqCQZH6YmwzWwCzt0AzlmE52Mk4NVMxGJve4KtUUAmRTwBzZbBTXAzYc0WwwtWsIcRBdYzQuBBEzNn0EqbmTbF4ozE+uHhwlYmB/SCbQvRdCSLfKcA7tMlpAQN'
        b'4VngZBCDcp8FLmWwwf4JK+lhaAA34WUCOhyL1g9lCjuZtnlccC3lCZ2dHO6w1+3tByDa2+sktML5PLzE1sGD6VDZy2GrvR8LjfV2PU7dDXA5kH4mLBduQ6IEqt3FHsrZ'
        b'oD2GLkZUAJTkifwQxLOggWFSzrFsqARdYxD3uZkYlMHpGEg/FJ4Xih2r0cITzfLCyyQAdpgUww1zCLmKnuJKsjNvQxL2QXrWWIAdTLSOj8NrpOMloBnK0Jy2qcpDD6KO'
        b'z2N6FOhNdk1Cic572hucoR2oifO0Ux7tZKwaVwHP2SwJBV0jaGJoBruZaNXtAgfppdRgy0JDESoIwnOnnFm0GJxlLBT4vBzssv/lAzEpPj//5bOBgXcsxKWlLzTDG90j'
        b'OvcAE9pUuXomgW5ObklWluvCTgliWtzpxO7E3oKbs24V9Y8ueLNMPuZD9yLirpv5Ztx7iX9JVAsma7ym9LlMMXZT1lve7T3U9kHdBT2ux2f3ijWhY2ivYY1bfJ9DvNbe'
        b'uSlpwNVH6d8V1hnW43/bNa43SktnEmxb3rFGsUbjHdHvnaj2TtR4j5azB3z8lYUqn84phzzknAHfgM4Slb9qcXfgoaqeieoRIzW+cf2+o9W+o3vnaXzT5Wz5RIUp1tTj'
        b'tB6MdnOD0r7LtdNVFXPI+7ZLpO7a4E07fPOQ+22X0Kc2lNuohzzKwwubEZQxKobKRxmvcQ+Vpd23d1YkKms17iEa+xDyQeM1bpl9DpkDzn5DbRY6JOrkpmSlf799oNo+'
        b'cJjNQuvk1VLVVNVcLWPd9+BrvQL7vcapUk9ndmcez+4PGasOGasJGdfvlX2rVOsTrHX3wvhlSYqkfneh2l2o9fbtWKVY1bZGy/frsuq0OmSj5ftrvfzu8/1x9sh+fqSa'
        b'H4mh4lYqVvZ7h6u9w7VD7vgFdiV1JvX7xan94obe8Q/CiTr6/ePV/vFa3xG0a0Ws2jdWKwg97dHt0S9IVQtSH9ma+Tg9dKJ8gvCrWu8RHSsUK7T8QHLmF9w1pnOM/sxf'
        b'2O8fo/aP0foK8GhrBRH9gmS1IBkV4e30SODlYidjP0ymfAIGGyGzQjOkJakpqd8+FP1fGxFzyfKMZX9E9u2I7Ldy+/yny3IH/AJV7NOW3Zb9QUnqoCSN3+g+Hl8bM+pS'
        b'zpmc/pjM2zGZfdnT+2bM0mTP7gucg+4p7dQ8/wGfADTHazprND4jZdbaqPhL4efDbyX3TSrUpBb1BUyWWcslap7vfX33RKv9orUBUdqgkNNm3WZ9UeM0Qamo77Qh0f0h'
        b'KeqQlP6QibemvDHzlZn4m9Eb+jSW1poRY/SX0GcLO4X9viN7HLU+fo8cLZzsZMwfXCgHT230yEtJZ5JumX8YLXprWt+IKbJxshVN+QNObs3zZCxslVolr+t3DlNxsCHK'
        b'GU+ABEVCW5IsTevsftsvpqdQ7ZegcU4gazLjTQe1IFfjldfnkveQRbkkPuRQHn4kKICpsu1zF/a7R6rdIzXu0c++jqaJnH3XOUjloEZ11appoxvJutK8UpeOZfcKtXOQ'
        b'chI6oAsu7h02ChsVW7WgN6pXonEZJzPR8uxbzJvM5THKKJX9acduxx67brceaW+pzFzNS8V3rZqs5GXKFEXFbV4gPrdpslGyb/MC8G/rJmt5LT1VI9TeEbd5kehqP89H'
        b'zUMkAj/v5NJS3lTeUtNUoyzVOAlx59BGwVVNq5QF/c4CtbPgIZPt6IuXs4XCQpl62yUI5+J1oFt1m4dj3mUWT9cw0eL+0DXulydLmKh7HlNM9A5NePB6UhX0e0eqvSO1'
        b'Hj6PWBQ/6iEL3f9ZSnbV+HHJ0zxZ2njbaeHUgKf5tBDTgXDhdE/WHQ8GOurjzokxz2A9k1zHtjmD3Uxy4z+C0XvuroD55GL6f0P3A9oo+AjX9B06bMNGQezQ+9ta6unE'
        b'mQwGYxzjKYWPP5Djn4lMwMZHFWcU1WuRwmIJWHe4eu+MwVj6EjY1+D+D3n8bOiTz9EZB4kpiqjMJWuhMgkxiFMQmQYpE5rKKHGPsdQZBdqGRea/axGuIC0mRyRDTHzvF'
        b'hBgEh10dYhA8x6Ao86JFujCGofZAYkkT6yxLBgeUQSuc/srQENFandHL6JUQne2rRFxNDDBzsa2RTxJVY+PJoGXxPzHSYbMlKTVYX10wn4SBEvuOvh7aekZXiU2VqCnV'
        b'tEWLNqDxU2tKy6Lj+XPFEmJBohssKVskKZOWkbJ+31GGfLDOHvks1ODzDIuoOFKx3iymN+phO9uzdqZ/Z1UajmXvnVeH05rCm+AwVCGGMz8M7kAipHDiM74yoeCgsYPp'
        b'ToEZPA2vwcPEzQaug0p4BQt8OstHJGybmIktGnBrfsEQa0497DIDO0J4RJccCfbCg0LYCy4b3GxOwm1Eizd7jTnlQMlWWPGKLe3K3ejoBiG3sECfgvNUGZVrUjcez24o'
        b'AzIhUIUgGewAZrvhrgJshcnNIbz1lGF+/EM1kqwiK3h0FNxClHyloAfJRWiqhwioXCo3L4l27nml+GeKx6RcenxnV8nD80bTqkStYmwhuT3SbTp1l6IixtZ9u2BZCaXT'
        b'NGYcHEvuLi1dwLjNvB9uxi9eobQpoEhF4CY4lhDNpnjgOhVFReUsr0vFHbkrzJvY01BDm3U2Nbg1NDsXNmNjEpIRsybq8wzgtH8TM7NDsmm5D16Cu6yyqyVkQKJiUUdi'
        b'9r9wzO86PuncnuAWeFPAqPMhLciG3cb5qZD0csKEojNUgWuwi6iDg8DuQiNbCzsQw9IEQyWpvMArmNQNToLW55m1ggwvImH+htmqWiAn/fQlHU5caUIVV3W4p+gUt2Pn'
        b'073oXz6ZOo8I01irTcUu3lalkg8x1Am+IzAh6lywD8iDsTYXdE2illPLwWV7Wm/bEOmORT4ff6oeiX17XMjT8VDmKTTF0NHncNA0Eqp6aBvq2lRwBCt0c4GCqqQqYRvo'
        b'os00Z0DPLCznoqnTyKHYIxlwN9iJ5O5DUhpY/zDqnQ5RWDbYWaRHhaYtMfASoO1uoD0BNuvSCWAVQEUMOAj2BVcO5K81kXqhDTDGY/KOwr9Wa8Y6XF/9xmKvJZMCc+2b'
        b'Y0wc2QMBjU6vOE3mv7N/ou+ZbYXBI13PpHzsrIVTej4J/DHkm95H2nk5opDXznx7+fO7byiuef03lTyveLW85MY/Hr1+5Zfvn/z42VHTh68IP654tOxTloNql9N7MVGd'
        b'v3pZ5Hz4zqPVb97b9eNf7Ja97r3w6yvv3kgf6AqevMj7rN/Fxr01xSVgXsi1/Ibvvjn56c+Jj9Iu3Ps6e4rfpJ1qwZ6FMv7a9BHeV9Kd6vtrGIc3KU/5ShkzRPlfxH3w'
        b'0Qf52dePL/91W33L97lHJHHvO40Uuc03m791XcOP44pWzS4R1YNXIjoYnT8uMgOvXVw0uVDzlvCpcJblkQ22D2Z9ffuh9ZJNC+57fj1hJ1hRP2NPygeH58Ve/f5OmPCz'
        b'7gNvm1TmZKaOL/poS+HPoP9E1rsJ1fJx374S/7170VfVW4W/ZA68WqqeLVo+rjrrp2kagXAlf8NvYzb5LrvvMCLpv75ysK6YzsgY1Xv2seca+1CPesfNq/Y/eLX4Te2T'
        b'v48Oviiq6599772K8dH7FPFJR3++8MtPtWZXT+/9/Enkw3cnRYtEU6uqzxYfO7Wj4JMHmRfTV3wVfGmhtOOtzLRR747O+o29LPjQR+GO16UBnaFLqr+rXvja1V8a7JOu'
        b'fud82/ZqxETfkBHNfgdiahUf8lqsPELbj637R86q/r73WvtiX33MSZvge9vhvQfpX9psu3vHQl5Qxaj5emn4nHhp7wWQv4b64Ngi4ccdAiei6QtNmD/oVwfWwzPg1JKZ'
        b'tKroRHiBkeZs9gocT10CGohmZIQowEj7GSnVO9QVmNLvXhbOx7FP4AK4YYB28gebiKZhqjdsExl0ajvAWdABtoATpDlctCL2GBzxJs0B+2vhJRL0Bo+JOdhzHm6Z/bxk'
        b'1t6htEKvhVmLKFImNgKxMxnwKFSAc+BKMa2ROz0WnBbRYVA7k0ShwRj9vY3FhHvAPtKyilih0Ciz6ha0Jq/BHmui3CxGNFYuHEyBmhGEk6BmAjq7KrwJUa+i9pDvMstK'
        b'8GQCGbjGp4sFG6cIQ4PGwOuZhtxWh0AbUfKYgTYSWj6oSoSNixkU0SSaw720Xi4uG6v0IrKBKkenLLYZyZrpBFQkzzeipAqoIEog0AM64a5cRMXRXiXkUO6gjQ32w550'
        b'Ug7YNxt04QJycVR4Tr4JxfFgsuFWcJB0D3/iEmOlFWyaaUIRpVUZ6CRtHWkDt5EnZoJuI60V0VnBKzV0H8uXWRorrXi2tNpqDNwrJKpvoBRN1iusEhl6lZVBYZUBr9ID'
        b'uQEedBlUGYWsKWeCsxWgW+D9f68QerFMgHvp99VE+mRexi5Rd9yfjbMyukk0Ra8xaU1RVTGDcnEzeGNW9DuHq53DiWYj9VaFOiBP45bf55B/z9lT6+nTMV0xvW1mU8aA'
        b'o7eSo2L1O4aoHUMGPINVIzWeUbIMjFs2DxVhH662D9d6+mEPzbZZsgytvas8rSNbkd2Wo7EPImWP1bil9DmkYCfPIGXabUeBapLOyVMZ2Zagcla7R8hSsa9n8GfObvfc'
        b'+SQWb6LGa1KfyyStm3dHsCJYOVXjFiZLRTKxu1eHUCFUlmjcgmWpWv/ArszOzKZcWfp9T19UubOHvLZ5JdY3TVbV9dR1r1IHjNb4JMs5Wr6/3ETrE4B+OXsq2c2rBvh+'
        b'ynRVUc/k7tlq/yQNf7T+Nj7gHvDy6ZivmK8KUHlpvEbJWZ+5ew8ERfVEH7dRWMnZ8vJ77r5a34Cu4M5gVcGhcHnqfTdPo4bdc3Ynny7SuOX0OeQYiePDVE1/xD3WS6hK'
        b'601Te6U0WWDllLOc25I8XCHlE9jvE6n2idT4RMvYsqlN1vfsnbQObi35TfnKTFXpbYfoAQcskDuEPvSiXDxkFo/cKXfvthGoHx2cyVMpysUqn9sOIVp0N0Xr4irPUJgr'
        b'i9QuwejM2UUe3bxU68GXM7QenoosFUftEYZ+o1dxeuAS5USVj2px7zhZltphDL6a25SrDLjtEKQvPA1nxkW/85rylDEqc7VfdE+G2i/xtkMSutrvEKB2CFCiRgrxM9lN'
        b'2fLa2w7+tNSPKJpT8IeOgp8JID3wdxSFsv4aai5K0vngOtFi+2MOZYQK93Lk9OeuU1zycMF9UHi3McVPooM5aq90DLr0Kxbei5HwHoxld/rwZ9x6AYvk7CQftxh/poTz'
        b'jKyOe4ZIUyvRIdnMSFZnIVmdqUuARsvrFJbYYywN0jnnJUrnGDvzgUE0H0yBZojwIIEgfzIuiX5GD+ZHP/ccKPEwfirt9kmq0rmnkrAlLK+jW1kF+aNGRkRi+XmhuBY7'
        b'QUprJZXV5YYqaJTAQZfOZyGR6fv/NkqSS0dJVvjCi0MDPiYJfkfymQFbM2j/tc1Q5q3PTgbOJ+m8sFiI+8e3x8DO1UZOWEhGlGO0TXAgjTjQuMEDIqP8Z4Vgv97Nqwxu'
        b'rrQqaDWRYjeT4DtZ5/6heIv3OBMce5UHbIHnYFhl4AvDKh/06cMqC0hYJbB7+xMo4xbav817y+XtE9YO38dxxesULaq/3OIB69pYETf87U2L4q2VHs6Z1vNmh4m4Il6i'
        b'081X7lpc8NkoaHBMY/4UUpws5QVWz2LnlJq03Tr0Ku8VrrSTmZrAQpL2+gEXs8OvCUxoBuQckns6aX4TyTrXdTkzG+Epmnc4C3uXGgdygCNuOJID9CLukEhF8kXwyLNW'
        b'9x2wFXOehZaER0lAIvcWIF/+jHWW8FPhiNFxpZm19jnY6EssvnvgIWL1bQKyl5xMZ/i2b11HlpVh4/d8ZuMfepvOBE/RgRnjSv+zwAxnf2WhxjkY7zru8rr37f21gUJZ'
        b'mtztfQf/e46eA84+yiBVar9zhNo5YsAvosdF45cg52oDw/sD49WB8ZrARPywGhFye1e1fYA2AL/s0pSn9RNi5fqh5H6/RLQHaPxGox1ruprHJ5lHP+AJjELsbIwiLAy0'
        b'7z+k7lKb4aSbptkumGa7osNyY5pdU2Kg2Q//LM3+BTeecce0vnIRVhP+3+OA11eap0hKKiqX6PAGdVkOhiAZIoqcSuv2qpYT5V/lwkVVZVg9WVbqY6DWuk96FmQPXX5e'
        b'0srh9JGdVxeJV5IKHBciqfEq7Z/xYpfjuc7cSngOnK0sjJ3HkKagV2dc66BxyjHGyXp55Gvj5DmuPiFWqkxfb1ZqjDAnWR65MatlxzrG0Uc3g/dGtnqOKH+Lsv/H2xQ1'
        b'921O0vIiAZsIClap4DqSyTqExu4fh+BhOjTsDDgL94OD4OwQHxDQ6byQ3J8Dt1cSerLAYmicNzfkCfbyjLCLh+cwETkDt4fCrVm0NjMrdzHcEaZ7XASOmyKx6yRc+29S'
        b'cvPE9NDpV7fUAJ1usA8/8wBZ/zH0+n84toxBOTgZjJqBNKAwDUx1K9Cw3u86CTROwj6ecDi4upvp81fdMHB1H/ygLzooLI3A1WtK0Upy/9OgwmzJxwwcxTSnZF75HDy3'
        b'JDK8+sUsXesk7zGw0i0vrzAjT4KRcQR2fwQ7eBAxigBGkNhwEqBLgrGI8YUwcYQqkA8ikMCu/7fyoSv1DJzwcNZzKUd3wBim0go9tLCZFe87Jwwt7Ne5VG0V/pTpaVXC'
        b'eEjhIwYWjnhILjxK1uMKZ2FcYRGDAAvrEIIxjK9z/NbxT7k2VjGP+M+A9n5s5aDwU1t5PWVaWXnjIr0f4l/feZFK0Y0nTC4NYoxuoF/fOdCtkaqthE+ZLlYejyh0wPdD'
        b'HuLT72Lw/Snd0Zf9Brz9uh3OpD5iMazj749N0yaNfcpaybDyeErh4yNyfGyCbj5k45/frWThV0u6WWcKLjtcruiLGa+2ynzKzCev4OP35IjrymI8JNe/m0ne8eu27y48'
        b'E9QXlPhKmtoq6ynTySr4Bwod8LPZ6Fn087tk/GSB2srne6a5VQi+4/sY/6JDbLGuyX5qkgGqGGyeDi/g3znYHSko0GTJDNBa9xhNNRFYJwL7we7RNbAtgodYvkvwqmPc'
        b'SLC2BJ7mJMCtoAns5oIGuB+u97YCMrgJKMEJ0JyWBg5agN1gG8Md3gCX4A0roEiA58FOcFYMLsDuQismPAU2wNOjk8AN0JMJboxHT+2C25aDS6AbnAhbCQ7lgFNJK+F1'
        b'2GUKe8Ax9N+VWHAEHIJHyxdHBUBFJFwLO6vBAcRYdiOmqm3laNCIYdbBGefxi5PynUCjH1ybump+NNwBr4NLlUlw84Lxbt5it4wEkcm0qBVh+eDQNI9Q0AwvJIHLsAvx'
        b'bbJqcAyxSI3gYia4GL8wGO6KQsTTCh4thT32iJVVgt3wIPrvKtxXnApbJ0TPBztK4EkOOAAuws014AxsggcK4EnQs3QhPAxurAJXYUshaHKFBxfMgPvA4ThHeCoTXI0A'
        b'29G3N4GdtmngdAHYEChCDbgIW0eB06vg8YlAwYBHQStcD/eAdvR3VwVQIf7v4FIvlgXYA87DjqgQ2A4voB3gYsUo8yR4AWwp8QBrxy8EG0tR0S254JqgJKPGOwPurIQ3'
        b'YFs23DvNBZxclgJ78VYBe0ZzgHyioAh9eyPYCzaZjyiE51xgJzyIzi7lgi2gfSrqkL2gJQReGpUcMNrfwR6enYwutK8InCGECniMZw+3QBm4UChFV5uszX0Rv9mFeu8M'
        b'YnkvgB4KtkSXJULFTNAWBa7ZwQ7rublgZ3ltMlw7CbZ4gcY5I7nwJuj1sAe9VeCmO9hcjl4/sQg2QHmkBzxY6jt5+uhw2IzmQi84KhWjabcPthZaus6sr05cAc97zPIE'
        b'rXngoOsMDNMEWqCKiz7mPJpTrfDgWLidC7akwysROAYLHI/HsJGofZfAhqloFHaFjkFTYtsycNbZHW5D/XMVKq1Xs+A12DDeH24YU7cDzfu41agj909KATvRvLcE1+A5'
        b'x5Vj0QB3pYO1XqAdykMtcZQB1iUfYKWDoyViPwGQVbBBI39NODgyqq6+wgbuRbPxIFShjt2+qHgKuO44FbSOBa1IPjgMNohhezBsEY6AvfAKuMQCPWZwjzu8KDZZhDbz'
        b'80XTlo6BbasKqsBx2Ib64XoQ+gg0ReDJalEiKuKAB2iD6yZMRWXvngpa4oB8FEDTYC5afuuY8blwN+gJxcEbiHk5tmrGKnve1DVzY8aXw3bb5TG28CT62EY0nTeglbE+'
        b'Fi2thvHeOf7LR6AJtwso4IlINNGPownaC7eK4e4qcA19Vjq8ChpM4ZFkuHsF6KgTpVTCk4FwSxCSEW+ujAtbAzbPNisAvS5eiJnYDrtsR7Fr4M1ieJYJZcucxOlwIzhn'
        b'DravzgRyuM5jPNg5DayFm0ptQAdQ5RcURZXYjXCF3SnjzR3swiJM3KOL0DLanwO3FqABlsNjLmAroitrxfDoSDSSVxE7tokFd+eBJniGD9vz4Lap8Bg4x7ZFk2+bM+KF'
        b'dgFMmjbNicKdC7bCE+D80mWuYIcXqu8kmlOqZWg6bKm35aLlcG4e3AMvr4xyAM1ADjZisxUiXRe45dbZsMMVcVrK6ZPhcbTyNsFL3rPA9VwRuAm6zPzBbikiCkfB5vgy'
        b'eG4hbJgKroe5YbX9zHxwyR1NueNwxySwW5RtO3MpWq2XEHVSwQMzwDq0gG6iz1oXBY/bBxb4O+ZjYBB4YRo8UoW6TpUPzgpgrwmQz/UHneizuus+QDPSA003GZqSo8Eu'
        b'PCVRuy8Lwfm6eNg+k43KVcKN1WKgXGyB1mVL7IQQcJRXLALdyWA7vIh66xpscUdT6QbYhj7tLDiNSP4MtFw3+cLrmcnJo6E8Gxwq5ZnDTWjKHkGT6hLY6Ada+UvQHG5h'
        b'JoNry6mRYVnw/5X3HUBxZVfar+km5wwiCBAZgRBIIiMQEiAySCJJqEVokkhqQEKgAGLIGURGCJEkcs4g/jnH47W9Y1vyeHbGTK5Zz7hs7w6a0VhO6/nPbTRj75Tt3a3a'
        b'Kv9VP1Ldft3v9n33nnvOd75z+93z2i4X2NG0LcAoccFaWCfTaSWb6006n5BD4DF4EHszSdwbHClSLSnrOAxBB969cIqAcdtON6Yg4SIMhFIPh7EZF63JOFqOmzkVYb2W'
        b'PKz9pb6SgXRE6FM/lq5hub38bVjMkWDmXZXr0E1gOeobcqzYNBlmw0pu6PAvBkCdLpSl0sC2qYFRklP5MW/S3i7ZbGiAh0JoU6YpHjNRhjZX7A6EgQKqUoZsJPexn7zS'
        b'QyhVlcJyL4KQEW1ZWHHFdT1LUoZ5WHfCx1rXcChH+7ogPQtLoZ0MtjKHvntXlWQ1TCMcxU1YiKAJHVTH2jijdFK3cpzzgWGS+uYFK3JP03FFhuzniGwvbL5ETqzTBsau'
        b'kUXUO9BsDPo6EczVkGKS87xw5PJRbLHOxEc3T6gUs81hUErKPAgLh02sUxJhgSBnRUkL23Ady5Ww2h/6nc6SSsCD69SBGmyyJhh4ABPQVIyDsgbmJOcNHPaPOwSPsU/B'
        b'35b6XUkYOUCeu/ckLASkRdFcLsCd/Dia0W7yifdhoxjrrkJXgqwIO7xSAxwkXr0puIDcTWUhW0Fgjy3xDNCNxU7ovQy1Ulf1oI8UnIRICg798ZnUy228z7fIDfLHmhxl'
        b'bBHFyBpdxKl90MmU6xAZ9KC/OpRDZ+FPSbMvk43OMbDNkXCMTZyxw2XeKeNLMCCL3VEKPJhjG6MayWy6oLkA5jkCXHNtLD1MAu4yLMFpWViHYVGANfT4wYQmuYMefare'
        b'qIJ9stmGmaQ3Papkjl1ONvj4nEMg9EaW4F1DqA8ydiFPsKJAsnmMdbIRMHaJmUsiL+8Co0P3cnAGNxJiCDAYBE8SEhAJyT0GvZo+dlEaOBMHLZdOwp1TsK6GAwG3z5Ng'
        b'BlxKNKH+TEgcjFng4m0jv0uEHOM0HxPZJJUJ6D1/nYcd/s6wdtaxRMUPy6AXuryTyTHfoUke1FMnaVfiMB+21bH1nK7aPvJ8tVrQnBCSeJZsd8s50j2LrLgtFtocoDxE'
        b'65AWPsqCSR+yvupMuGuJd/x4WCodAespJ6DdPwMWvMNgA6pPuPmdurUPu0n9CRdH6HpVXDZ5gEGck4EBsoMaHbKXeRJVE/Y5wRbU65OZ9lkQg9nefxOXr3iT2naRt2vE'
        b'Ds8rOOhLqFKaElkElQG5ZAIDN6HjpjYp1lLKdRxL08MuwsEHBBW1HtgQo34MSeObcTiA6BHp9IiJC3XjHh0N+bgUBaiRZzy5DxbOkCKuwOL1I2T3Wzjuh/UkuQrye/dd'
        b'jBktE0N9qokVU0Zs0TouwYNB6mkp9GdAR5J68dVQ7KOrLJJhdUJrBvVmjEhBuRQ0FpLs6/VLaIS95EQnyHfmx8IDB+zHYb1w5TPkKx5m6uADEbafpikexY0LcO8SdXHa'
        b'G6bJjKvd2MZW+nwLO85RE1UX068yL4Rl2fq4kMd+3sUKc/94BZw1OOwfaaQBlYVNpNg0jntapNg0hG9ohB2u8rKxkWiEl6sdrDjC7FVFKzdZMVsf9Y/G1hM0FBjwpTne'
        b'oisviElIywyGYs2g0hnLDyfCPbp0LczmlXgpGQfDFs4k4X2qM03w0Xl7P5TaRdOErwpcCQs7YM322HGcSCCS1o5rIiKZjeTHxslFLyEhW/lte7yrQWpbfSIBBoKwI8qH'
        b'fGuzyAe6z9kS7xiGDXe6WiMxkgHYVCXrvgcP1HAsEBoPF2GrSuj+tGzCujJZMpD+EgUhzFq4nwzR81ImHZuEdhV7IwHJ7J6Chhsu7reU4/vjHVMSY6kF6f2IugG5+EZq'
        b'c+oClifAXV8gZPImR0jgRBQB14VEcvs9rhBgtcND8ibsXqVZmiVehH001FnkEGj0wmQ4lsfj4AV3qA05GEpiK4cav0yD8IBIRmJqE27BaJIN3kmGUs0SE+wkf9VyHpfF'
        b'pDkdkThxCavtHaFTitTsfghW+ZJybROqT6UlUFjSTMhdo68HW4mpuHgJ2zywCu7nupLwHzlBpTdpzTC2HI7TSj3mFp4Ew5dwNfcCAfOAh6qChbOLlr6zDaH6ohLWaJ4M'
        b'syJ/uG0Bfeeo3VZlUq3H2VAbFU02sn4BBixhVCsF53Lokr000HsXyRJGzou0CX9aYcoBZhRJnLXYmQY1+2E+Ie+i7nEYz6JKU9CdSgjRzc+kXpWeIYVfdIYmL9iyIo+7'
        b'hq/c1sLHXBb22mHH1aDCt0gnrXAjmalkWY5EI7dII4twQoSPrssR7SnXLCEBllkaEcVdNHTUwDY1IpIxUcWB0Hx7vwUx1JJCqEzUixAqRZETH2L/oPwogT9LGU/f9GLM'
        b'6YaaMkwW0dyu4/3o44rkMJdhW/USjmB3Jjnch9JYWojtZ0WwVZJDp3qTEojNTEsIBBCB2ICtDNL+hSQ9rBDvxxFrUoxBsp2JsznYcsOErKqPUd506kD1RfdsPUX6Rgsh'
        b'RweJoy40jrje+M0zN2PSi8yUwpAo6xCOmBF2P7zgXaTCshQBM91mWM3J89aAZdUCMpMyMZGK5tgwZ3lznE0KwzvQcYaqLMMrsjiuLMLqSDuWz/AOVOVBjyqFKq9AfxHO'
        b'C0lXZw8p2QURPHVnqPlnXvem4GnQiGx0hsCmzsBaQOJsdyTC2ayrBXdzTPafImOdNMK1AMKtBopPFskjr+ewLXzYesUCRw9QhDuOr9yEHmt7gr9VWbpYOY46B4ici0wv'
        b'pJKZl5E5lBeSJfQoQOthbLzsjL0hFmQMC5rq+UkEf5s4Ho/jCWQ3w6akgX0uxFpWnKEKV/NyYKiAwvBqCpd1HbUILjuPE8wveBygbjenQwNxBml8dI6cZTUpapv3ZVw6'
        b'p48VAriLMyK67j1Sth7uwDWvvPh8nQia3zkzW7KXe9CSUgB93kVQewBrpC9gXSZ0e1LdeVgk1tmJNdHkJOqImPRphajA/SDL2+GkoJM4XRyXRVyx84z3KRcWm024wYiv'
        b'2PYCrJBKNYXCXEmGViohULcq6feiPQ5F3gjANn9b0ohpXTMsOxSSeQ4bA7DJRkZyLxo1uZEQfFqa4x3ioDuQvlRhK7lvUoAj0PH1tmnSl2W8a4/1kh3VWiSjzWA7KY7n'
        b'w+FECdlmBZbttVbpC+VsYyHvOGdPMunGRrO9FAArttTDOqzjcbwginWJ5Pbegm5Jc3jXh6RVd5AnuT3zASl/v7tzYSCf/bKjcpRE1YYNZBo9Pkok+ZlbCvvPy0OHR5Rq'
        b'oiZ1qsWBFGKQxDxJ8mpnzN0SXzntHwqVmd46NoQ4KziiX0w+6gH0n1bzPU8w3gx9SdhEvIVMGe8fY6svbG9lkUOhH4zrMLZ3E0ZEiVilCA/EidShNtj2htKYSGwPoxml'
        b'82SSFafocBgecgS0Vec0iMr1HqKJu+cUb076V2ZEccGcbRy128SF0zUrRIStM+SH22jGKdbJuAGVDuRjW85CsyWFDPOkF/HEY1osSZpT0OpGAVNFgTAUHgeT0g+zre+k'
        b'XvOGFDyVE/mrdrO5AVXOROLWSVyz5BYGYNaUSPEj6HYVuV7lY5OsSBW7Ai/D2DFcFdvtx7WLOBF/WhvGZG8UikLFQgLSFhiWZ+sH0GWoj2Uk3AmCpDICydEL8WyDJsmz'
        b'I04rk0x3jbrQfJSGOuq1TyFGCfuTL0kisB4+ljtRPFNKUplCgtNtJ6jn42ycbbgTVsQStD3wwFlLMp+HzuxBErWEt80eyB7QUQelYt1CAXmo5nwawzBsnTxPpLINam2h'
        b'XxYnM7A5ENqP48A5Cq3qKYbZktXGukumyTZ+BjgpB+2XoF1M5rJlo1KIY8liMY7Sv9abytTdmmPRsRRLThEmtzjjvF/ADfXUFFiyVoZlFbwfSOZ1xwWnDp0mCx+DSmQr'
        b'PDWqFMYvQtk+6BMSGkDH8cD4sPPimHhdYkXV5M7XdF3xrviQM8HF/FU+WcAITNrrwHZhOk64UEjQbKuJPboMzMnpVTneJsNaOkqssYatS9mEpZJbhZVD0FtAClUFK+eh'
        b'Koc8+TCMnyQrngq+DVNCMop+mtKpIHfJMswmn5zN/fNpFFWNQJOLrsEtO+Kfi2EsmsCWVCKag46MbeKWiQ50iPIPFugR65rwxtWLylimjJs86L94+/wZbCh8KMVuWdUx'
        b'+vYCDUHptLeJj+pVnNSR2XcNH6SQYZQlETjPRZzH2iAtHV+KXrahU0yirFTUko4XhkQR/DQ77yO16YAZfRw9rBds6gkLJRQTVMXqhdsn+8qSX1uNjJas1MyH76eL9EDb'
        b'MRLIpgINYD6HQGaQ3MpWOi4XwrINzECdpx2ZxSj25dCbpqtHoIdle2iEZqamQzBnC9OOuUT4+91xPuU8CbkyNFqX0U0krB6J4RHn2ySDLjMk25kLIDfXLzDEh3YECws4'
        b'pBkNj8jHmRG6NkKvjziEuHZ/GjHQch8GsnNQdjOLeL6BDxGGIX1VtsIVgg+LNfwUYDw7gfC4fm85ID+ZDKD5sgX1jNwaPrhFQLBmSHZwj6JdeBh6kcvEqhNZhDh9F0+k'
        b'kX9YwD4RdbK1gJxxOX2DmDneS06BmawIF1zUVYPHB+LZz9JaOOLrwIRii2O6IlzLILVhXH+c4odNMW5dlPZUw26Dw9gankeIVq+JgxoUhrWVEJ0qhe0rRHkWj8OYerj1'
        b'cWdzcsED2B4nhw8CcknuvdZWhcY2GToRARrqOKB5u9BdGSpPSIWRyo+T/tXA6C3CgQeF0YFQd56Q9o4drGqJyCo3ySyWb8Zkk8fMgUY+ztH7SWJ7a4lXCW/7vG7E4kic'
        b'PYFSD07YwMaJizC13+I0YUIbm2Oah8cEa92EDVPqNIwt3L4VEcJu5j8KrdnaAeF07XUDkseGH6z6EgBXCaXNjhecggZJgIsrUdZw7wzWfRPgxtDFG6DzyH4W48ZFKfJg'
        b'SQOrw2BGxh6mzsvowBgSAC4eJT2YcYvGLah1yHAjDW2RrJyMm9kThrGVum71g1BBkEYqWgmzFB/g42vh9jY0WxO46e0LY4bQrWq4j2RfD4spZKtDxz05GNPnXyBcGbeA'
        b'bjcsNSWsm4fJWLx/Dnqd4gh2qk5DX0oceYSZaEZTBvFBnNhKmp/uiR2HcKQIaxxg/sBZLM9xhOHME+QVhmnID4m89vkT4MBaCNYejCO/0WtL5vyKvWlMOo64aMeL8XEY'
        b'aVsHeY6KI1pycD8zB2YJvfrpCrNhsmQH23nhFLy3kMLUw3AxDZt81T4cPQTtheRNOsMySZ0oeuk8qJwDFQom7jjlloFdQTrZsAljhdjrBuu+YnLHYxTFzkYbw/ZZzhVf'
        b'UZbDbT71sjJUG9ak2QLJkBuMpukEQscpg31uFHnV0pBwyoNQfJN0YoaMYIUUYesKRaCTmiT27qRkZjip6dYEqg1SF3zTrijB0nkczQwPy0i9SGR1XoW60EPedkIB54Oh'
        b'Lhk6o+10gQKNO9iQqZSIk2ehSdPnUkIJ9geFGh3GFkecM0q/gI3OUoy8EgpVUCR9HzdDim7Q6OuS1MhzPcDHxgIL6NCMwsrk2ICLJ0L9ycDrvbA93zUF18wIkaZpUuso'
        b'PJQRMtagGGcogRiG2mzTf1fyEZjDJTMbtnMfh66TvTXCrDVFQXXqsuQcx/NitemidSm4FXGF5qYBiRs0y8OyhocDYVr/dc3bqlZkXN2ENo8PYrUQ+l2yySY38wtPEqO5'
        b'Ak0x/0mxKbxd5kvp4iNs8VEVw7CWTKYVQe49yU0xo9hxmBd09jQLoJJxNRkXlMmslmjoDw56qGCzYbyRgOUxJdddTwRospiE3X7krPw5mD6GPbGk3D3sHlxFFpPDhOE5'
        b'kjYF1tCogxVn/Bnr0aTGpoT7YcQJp07ZIlGZICMSUJ0Z3JdsEmn3hF5tkkxvPrmchyKYizUkJe+RijpiAEP6blCaBDWHiP96ERbuP2cjwMcGBBSt6VguD3Mi8W1yXOWw'
        b'GHeMvMqCiMF4nWxBhDOMKbmQkJuwW09IYlrTwME0bZyWsy729byiC/dcYCbkBqnVCHm+YezWx+WCIBzTIJ7TRE50I528QbGCn5hmsZ8aaTVzLYBhD8FhnDpuDo+8FbCv'
        b'ACfVUhP0YFRd7Qq0aWN9cBo1VAZ3D8o6hdKMEs0gyawKTELzfFyiMnHajLBhjIyo75IZbvsTeHXCvdO+Xoyo1pJZEgsn6GqFZcVUrDpK3pl0tM4PZvfJ8wgKVoQXCPZG'
        b'aFZWqdUKde0YcuINMCQHr6RDpRuO2RP+V9+6Cq2uF5Atlg9ysHDRw4AAZR0qM6zI0B7qwQN7svJusolZYtN9l+T1j+KGLnSedQ3OCyAP+gge4ZSAvnIHFky03CjwGIJR'
        b'XxiXNiRb6oNtC219IrINtth8A5uZaGquwTw/z9KDPm3xhEGrGFwjV4kd6uae5tjvCl2iWFKdauwQk1/aKjqPM0c8z0F5VgEh410H7hiMJhZpJSWR1LPScQMakmD2ClHn'
        b'FiJvDSStOXcC1gpzNwoM17BK7B6c6kUwUI21JfYk3HklHinfuBKjxTSR3Sn5RTdhNZzeDkFPCAXp92EmLxCnYyRecRE3PM97Q6c1eUwKgAO8cDGIyNuMYsphYnFdcWQc'
        b'27JJRNVKzSgWbCyU4rOsTpqJzJDKSJ+ZJW3hhh0BcRep57IbLuoRz43FNoUMP5gwx16/Q9DCJ+82oMxqeKllUMy4WZIWGEhUoDzonJsJVhbnErfewoe+NPvzcF8eN4/J'
        b'ZpHTmeDhgzO4bnETSin6a7f0V1U8gx0pkt/Xpthi/+0SuAvrbE1rCNaiaIhkJ6NsvYhI7giMBupg9/Uoq/hDNLh2HPfEstvYiEuG5BmrL8B9dofZkr1Meq6THswGKrBc'
        b'LlSxwYnkWplFFrCligMJUEFsYJYcS+NhbDaQpTGOyNvj9I10on+VSUXwihe55EYi/+T7+TivJ4+90Xr+eqQyk9bSaka4evwcNKv4yBFurmNpANGZCYZqR3GaZZxoxyZH'
        b'FVEEVJwPtnYtyFTALbWYYiuCeGLl3tkR0JSHbU5nKLRmPHTBLf0GaUiNFcyquweTFT/QhXUFWI69nmWLjywIulawFyou4nqRAlaeOkOWUUEde0TA00IRiykJvNMY7ykp'
        b'8FN1sS4+MyNB6Iw9wSq8Uzr0vSlokYFWdV2yuDZYyVQ6bXcIl43ZAii57lLY3Acr7Ge8h4ZGFPXVJx33Ivbef4Tk8QCmjexzoCXkANlFIwU++YXQfYTmofI0LnkqEn/f'
        b'IGbQd6pYFweVbknTCFr9oUdT/gaZXCu9a4Ftu5xL16HflGLKcg3XcFjSgz41Fy+la3gnCCsMhbL48Cy0pkM/TJAiNUbFsUVTfFjIlr1o7jcIf2fJS5TjsANW3xKakpsm'
        b'DhRNde+F0WDuxOBysQMRMxghg2kjT12tGJdUGE8meR+YNyE+OnyMxrZ9E+4aY6uIWPfSFbZZ8ZoeKdbETay6DTWE5cQ87sRC50X1wo8YUep2xfZv7MCHLU81xUi2xXVm'
        b'HjeJUjXHZrKBGPMSOt2nn5Ysr4fD+q7mNLnbOJ0Gk7KBl+gay0SRRqSO4bIBbONDl0xFGlAFDhQA+xm4LN4TWgXQoUdQvnkNu4NhkE+Ho7AuInfz6BYhYxOZ012aihYF'
        b'YxwKInhcITSdIOnXY+sN3IYNTy2sOQYb9jhoHop1WewXr9NswSolguRTYUm4UqMkwHHRPtL+xesmZOprh8NzSeWGNZ2of62OOthxYL8N9lqeIs5AFuJH+rCllY5LStjj'
        b'YYojyhQ4VlyAcj9c84EJ+SKCmDYiQO0Ez0McKf26DNwzDIRORYoSRhxV4YHvYeh2JrpQoXdWGx8dOCIjg9WRflijiHf8Iigo3nBg+SrdcE41D5cOKQU7waAztvm6+5Bg'
        b'FqBHQLY/THhfWXzJRI1tC10jOFiDMhPS9ikeMbPbVw+TwrVFQYWiRC/WhATh25ctCRT6sCqXJDfKwGDJkdhHW2o6DLmSRrOF+Das1cWFYyxbURpUy8Bgugk8EsCMtzsu'
        b's/AcSyMJwxZDrpFTf+wsQ8x6COqtsfwge0akDgzehE51UsxqM/absvQNmWNpZ6nlu54q2EH8QeYaI0HlmkdzKOIjRn+HMKIFRjWx+6RuEbvF4gxJrgfWL161gHF72PSH'
        b'IRtp6DYlgtUbC2OXKeSZgiF7IVEgctzH3HOPwHqQ1RUctICuIBi1czyFC9LkVTpPm1JYew/nD5OPG2NG0n1G46QzkewJB9w+Z07w1hl1SUV48+y+OFKeaiw9GkLX6Drg'
        b'td/nJkcEs/oyKcEoDrx8LhJdAVbzX+YFzL/MMgPysXJvx+NDEstSvpMZlH2TrLYJm2z4kkR7Z44GBrOVJVcOag9Tl5btJe1p3oayYJZuiufIUuUPI/ttpFVyKloDWGL2'
        b'GgHH82Oq00Qz2xEh2eaZrwz9L9fKsq5gbaCAesduD7IkulcazBLvO3GudsTWhk9JVrYuHcnBuhCq78ZRtEE4Sxcak5w5SjDQ+/XqWnA8Wc8clFJrrMvS7EmrdTb0tXAu'
        b'JQIHZbUl/UrDfhZBhkoW12BdzFg/BdCSbakD8Njj5YKcFmllt9JtG97emceGxH6CqC07DldDsVpVILm+EiHyzDfrcX5JhL1LkTY8f8kjCiV7YV01pPzf50uet5JVEnyG'
        b's+FLPv7sBv+EJSf5OERTXW4vHWKsqpT4D3t1lbgMERdmIxVGTUl2zmZYvXlekL9LWBUfrttw959y3vFRq+y0PfvZ1jviQ7bLNmuvvSeO0UhzteIrCgJ5So6l4W4yvM8V'
        b'rn+gFGD3g5bJ77hH9N3+5CvXhY1//aijILjpeVDC74eFMikRlSmx/ilnv5tywTIlajQlPjUl+pOUizopkR0pcdEpX664XhxXyF9xeP21Rsvfyu68f83U+8tXfvLqzy3e'
        b'/P662zsjv34nUsfzx5d/rVRUpf5WTEVRxFxXyi+VFV59a/az/1BusOtKLzle+b1fGRebOhbc/Jdxle/Hv9L882PvqS3rR//03T8O1NV80Fb1/EPF9bDi59LvNf1zUe6q'
        b'SZRW060JhU49i59vfVT5aMozM1pmOvBnr/G/W/WTpKDggXf+JbBm4dDPz5q7hp3p++RG68fmF9paX/OIiqqNvGPwk51Yszf5GSOf7IBt6/tgdtX64wolzfnrkbq/GHnd'
        b'/fD8sozbwgeRE6nXf9g/PmsV/2phyKVa6+zXB8oSfpmjGv5M5g/+Up//2qHgAj83YKri54dLPjE9UzD5kaeDdZTByqNOXvL+pt1a1xV/jdrXbRryDfvf14h+PbH4kYtR'
        b'8tsj3T/49WRIYWW7Vdbx9k+mxDezBz+uNnvL8eSS+i9dvmtklfGl7MKn6b+P/GxTKnbE6BAoOadVhdgNRz/BN358ySf0A/EnH6T+wM353xuO/LTbMa2ycuPD59p6ydJf'
        b'veYU5fjj4QrdQN80YeHzp/WKP6pXfve3l+edN1PiZXS6l4/MxXtPvvNpwJqD0v6DX/zMFu1/FJmq/VZelVOu9cLgj5L73q8W1b9hMD9+907tW2+fL/Oo7S06sbE4bfv5'
        b'j56/n5afe6msvyTpszL1MpkXb/f94ulnRWlj77h9ekT1qnN4/dNbxs5T9dqblqm8+Nezmpy35d8uDX1biu/+pOLfRlU8ZhVLZlVzPyz9GEd/ZcNV2Vz5svyXR10HN6Te'
        b'WzNuxUPSmX/U9lye+dh2veMXO4fk1TWcpcJG18OFH3n3/tL7dsWGy5s3n92+9tWnH3410TUy8btpB+NNLJZT2f7B0MwXZRuWj9PLhLe5BBOO73jQRuE5M2fo8LpGKCDB'
        b'oCM3sTE7Q7KtwfwMbH29aQFbw/7iLmMVF0kSLy98GPCth0IF471vtraS33hF8rQJg2xsUxQryysTM6jDGXVVcaESew4VnzMsFsglWO9lBJslVtn6TbVruHztCs6rKctw'
        b'ej588jVrsC7J2GbphJ35V5WuFOKKKtRCvaqcsgLOql6V5mxUBFCmjpPusCW5CRrLw479tZrQIGmcWg4VyCRFwBpFLM2S26pzoYaG/E2DcjhA0fNDqUM4L/2cPbDcnwhk'
        b'PjTIXaEu5pODrPkrTeKSTMZZ8iZ3Tzxnab2VsdfqLzPyfivtG12wQR7nc22ivn3frdz/Q8U/fIPqP/buZ/bMWRMTE5+/8/c3b47+2397d9fLCYVZuYkpQqHYQZbjJHfO'
        b'CwQc99VXX/2xlNuN5nHK2rsCWXndn6lqNDvVXesyrbvRnT/gNJD44Ghv8aPI3ttz5rPiVdO5wtXIuaIFh1dPfk8DA99wCnlXb1+XU1di99Fe+YGgp3oOs7pP9VyfeIY9'
        b'1Q17EnX2ybnop1Exb+jGvKtjMqDRlvNEzZylforl7SpwGlrNvi3a1Sd2ZThdr2rFt7VNnhwIeqodVK1An+jZvqXr8lTXpVrpQ1Pnt0xPPjU9+UTOWHLs8dTUg45/I8OX'
        b'93ihoCZv9Iyj4oW5rLzjM46KFxqG8novPKXpSEUgf+SFkpy83jOOihdaavKGn1Nlw11LTt+gWvmFwJ8nb/iMY+WLKKn98tbPOCqaRc/Zy+5JHqeg9kIqV0re7QX35/KL'
        b'vZJPJ3clJ3dTpOn4bXndF1K3+HRB7s/lc0nJ6urtfUHA3u+ekOMMjZ/I6X0oryr5WpqUvP4LjpV/WZW93z1Lbeu9kDKT9/iSo0Jyfpe9fRHEi5eWZ6mS/srLl3svu8UK'
        b'kiEkyMqbv+D+XH4uKQcMv5C8vhwKO9z1UZV8IUqaVf1z+UxSdmV9IXl9+QV2uJu5dwUfGVb12+XLipIP/JViePImX3CsfCGWOi6v9yVHxYsTUjwSIUfFb2R48gdeyCiz'
        b'6aJi10TSslCKJof7c/myTXa4e1JaUuWcjPzBF9y3yy/2yr3q7HDXR9lKVrB7lmdJZRRv79iayuiXn9DxswwZmiGp3UA5G/oo9j9V+lb5rFDmpEBO6lmwXLCckdQTOf0v'
        b'YtU4DdNq33e0rZp579p6rPo+tfVeLXhqe/KnaqYDpk/VzAci31CzesbndKw/1jb9r+qY/ffqGP69OjR6HaPPValbv931K+Dx5E/zfqaxf1jpib3/GyYBb2gEPlEK3Ntz'
        b'POBrGOLKve6qGar4MlXYUfG7f+9JsP8fFZItPn9lL/R/E3sliCsp7L5G+d+Vci/O8Hg8Nbbx7m8X/5PUZ2wSX+XL+Gpyr2oq+hrzM1YsVHj5gTSFSx3/JGr+fpiUr1pl'
        b'yb/0NyTKpHK8uEHL1ZPKvIZf8Z+bG+v9qdx07DuKsqG/03p857NfDfOSh/+w+x/3/rQ+EfVjTafvmddlib9ncdr4d1oRgepvWo+6W9yNKu+5Gxk2lRu5b8T6Ow9LY2OT'
        b'cqd+ndBjYCBerNcRf3Dwh8en1z5K/2Ljh3OjqBza2as9dcL2+/2fx9red/63nVMDJ66e+86PfpPd4PfDrss9hTkZln0xBbVnj74dEbq8+JlO9w/cnsRFr732p0Cl8YR7'
        b'W4NT7lm/9Nj+xbjxQ3fZU0Ij8c3zuf9HXmnxaVkNP/YX4K960zXv8HfkkgOLXO80aQq6PtRKk7vSqHjy0UcaMavf1Tqc+ii50eBdM99amcl9//7kZGWJ54fqbvELGfpX'
        b'X9v4p9/8xFsnea7n31OtXuv9470Lb34Wsbk5/VrbUa3LH9//ND08/dPkT38rPB5aGv7PA542+yWpYu2PwAy7J4FFxuHhkuwcspwizEvho2B1SQ0LrIGh4HB7nGM1wu2l'
        b'YEKTU8dNPjwIPSepERMIo1DHgnNRDEtQxBaSZTkVDb6xPixIEr3gsDufPUkiVJZTwDEZgZQcNMZK0nJDkyMP6w5R8HuGM2C/zCTA0F6W2Q1vqLDDRmuWWKSeB/Uwxsk7'
        b'SLFbo/mSrYBZOIR39ki0dDhMc4IwHrtdPXwvYfcdqHELPn1QGRZP27/MPKyCtfwwYtDjkjQt0BwJ25LENGegYi/fMywRBzZh3V2BmoN7TYeexgab0wK8A6OcBrbxYR3H'
        b'Cl5muPbGueCgg2FHnXmueJ+TxVYpGW+Y28sfcy4m2Mn5NHtMCsuwhSvGnKop38Mobi/T8GqeLTt9OlRyVuhIfZvmH4aePEnLp3GYGH8de1Z3E18RH3OCSB5s6PAkyXVh'
        b'7ATbpY4NoQe5QAEnOMyDyeNuez16VIizdvbYEMJjiwCcIJsHq+E4KNkqfQbrYNqO5dQOYRcNpZELOIOTRjcFcAfbj+5l/p08AfOWOBjMOkaDJ7lzijZS2Hzca2/Ldin7'
        b'sRj6NPP/ooLCaSmYLVGRhCMnSQkWFXFeFZeMM/KhBlfycPEK1Kkqc5zhAYEsTmRIpkc1GV/BcZiSbCS1Y41xpHQ9UjjoAP2S6XE4e4x6ytJhw6b31xmxyy2fs8eBs70J'
        b'2BoMU9Y0t7XBRjewXpL3Pfw0NBwKs7eR4QJOyd6AEd+9XaHz7NmAijiLi+zRRi3Qgy0cjmI/du1JrY56y7ZqhLIcOblYJ32Dh8P2xnuasG0HI+ykPXus0ZWXu0D34ahj'
        b'oQAqA4L2xDIqwFWSey1LwB4iBb0KnLylFE1hB27tdaGG3dEEc7BoF2R/MNTegccpafMVcAnKJeK4aicfTFMT7EANsCUuGZqSbU7TmY/9fpESjTGILMIRoV3gQVuWJYBN'
        b'CzazjWOlQXux6LaZoR1bDQrmlPywKxm7bY7/IwKif7hz+19ykWw/+d+IXP5nznLo60ISo/wzx2KUP5VyXxhy0ppvK2u9pWz8VNm4r+gNZetS/7cFClUhZSFP1E2HXX8q'
        b'OPiOQPkdgfo7AtUPBE5PBU4fCOzo+Ov/Oh8IHN4TWLwnsN2VkpHW3pXiy+u/p2T6pQInvf89gSl994VMpLv0KaLQ/+XLb/ZedlMLSC21SsN/+/w6HakZfEE0lhrV2+XT'
        b'6x/+VVGHPpDWfltNq1aaPpLW/n2+LVM9RRm/fRzuU/Gz46M1z8+BQ1seO7bjs2MHJT8vPnryqNwjYrY7/CxRjvhH7Om+0gWFeVmiHUFWRn7BjiAlI5nK3DxRzg4/v0C8'
        b'I510ne2bFiTl5mbt8DNyCnakUynqoxdxYk6aaEc6IyevsGCHn5wu3uHnilN2ZFIzsgpE9CY7MW+HX5yRtyOdmJ+ckbHDTxcVURVqXiEjPyMnvyAxJ1m0I5NXmJSVkbyj'
        b'dGpvx3xo4mX6slKeWFRQkJF6XViUnbUjF5KbfNk/gzopn+R8TJTDsnbuKGfk5woLMrJF1FB23o7AP+Kk/45yXqI4XySkUyxlyY56dm6Km8veYwuFKRlpGQU7sonJyaK8'
        b'gvwdZcnAhAW5FMTmpO3wY0NDdhTz0zNSC4QisThXvKNcmJOcnpiRI0oRioqSd+SFwnwRiUoo3FHJyRXmJqUW5idLHoa7I//1GxpOYQ5L6/lniiuZnkv/zT8Tk28pLEv3'
        b'mR8tUVj6I4anyuNlSTMi99fK55Lyf8zwjGV8HbhXHRR93fi/l0ulKRYlpzvsqAmFL49fRvm/3/fyvUleYvJlllyVpTpg50QpYTZykt3iO7JCYWJWllC4NwTJpvI/sM9l'
        b'snKTE7Pyxe8z/n+VkVfJRnTJhvm9xQRPmqvCLJG3uJjO8Ni4Q6kgHefxnkkJeIJdJU5RuVT2c0GhO09rN6+Qx8mrvyVn8FTOoCvoLTmrp3JWTw56v2qJ1m8cDHpbTu1n'
        b'CjpPdJ3fUDjyRHDkZ5xas96b3D7J5f4vUpDzDg=='
    ))))

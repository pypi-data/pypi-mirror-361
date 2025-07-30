
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
        b'eJy0vQdcG0f2OD67qoAQGGMMrnJHIJpbbGI7xgXTwYAbdiIJVgLZoljFFVdsC4yxHfee2HHvNu4lvsykfe9yucvVRHeXcsnlm3Yll2tf332T/5vZlZBoIfl9//Bh2Jnd'
        b'nTflzWvz5u2HKOCHh7+p8OecBImAylAlKuMETuA3oTLeIlssF2QNXO1QQW5RNKAlSmfyQt6iFBQN3EbOorLwDRyHBGUJCqnUqx4vDi2ZWZShq64V3HaLrtaqc1VZdEUr'
        b'XVW1NbpMW43LUlGlqzNXLDFXWpJDQ0urbE7fs4LFaquxOHVWd02Fy1Zb49SZawRdhd3sdEKpq1a3vNaxRLfc5qrSURDJoRWjpPYnwF88/IXRPqyCxIM8nIf3yDxyj8Kj'
        b'9Kg8ak+IJ9QT5tF4wj1aT4Qn0tPLE+Xp7Yn29PHEePp6Yj1xnn6e/p4BnoGeQZ7BHp1niGeoZ5hnuGeEZ6RnlDWejYZ6TXyjvAGt0a9S1sc3oBJUr29AHFobv1Y/H8YN'
        b'RmCTXlZQ4RtWThrW3rRZcja0JUgfUWBXw/UwlQzRsr8MqspbUT0SuYdDBh/Ex22kmTQV5s0mjaSlUE9asucULVckKdGomXLyCN+YqJe5+8OjZPv08bnkhdHZhuwk0kS2'
        b'5SuQlmyVFTyFT7j70qrOklt4c262gZxZlq1AcjmHnyMN89xD6Lun8BayNZG9lp9NWvTZchRFdpNj+AUZvodvjNPz7gH0uc3kwZO5o8fAI7lkeyFUEzGExydlTzrxHfbA'
        b'5Cn4Eb2fnS/e1pLL5LRalkbOkD1Qx0DajvP4GD7spE8ANLKNQ2n42dBsHl/FJ4a6R9IndpKb+EwYuR5BbjpxE7ldR24sxc3pZHdEOEIDhslV+Bw+r+fccfDwhHTyiDTn'
        b'5eBT5DDZJkMy8iKHD6/AZ+A+RQGodmt+LrmjwpfiYWC25pJtuKmQtg63pBQk6ZVo1kxV/ewCqbrJ5CFpIa3QsrxCBVLUc0+Ra+RkP3IC7veB+1XTxybmJBnyk5I5RHY+'
        b'pekjCx1pgXt0BobgF3ITswwJpCmPdou8SFrDyE6eXM6MreAkFJDB3xgfCuykmBmMl+j/FTM98R69J8GT6DF4kjzJnhRPqifNM9o6RsJXrjEE8JUHfOUYvvIMX7m1vISv'
        b'VYH4Shs7pAO+2kR8fW6pEmkQivype6l9HhAIVjioD8+QeH2lkFe57Cmx0OhQo0iEUp/v5zBM18WJhTOXyRH816FKsz0jJgLZQ6Hwtcy4rOUhn4xA6INRf+VvpW0Kv4Hs'
        b'IXDjibKD3FXVD+YqpppG/9YxbaVbLN5u/2vEnoi4yfKi97mvY/f0ViIvchvgxrwQQNVm0pwyOz6ebA1PTsmCqcfnSuNz8skOQ3J2Uk4+h2oiQiYjssk9k6LJyQn4lNPl'
        b'WLbU7SS318C7V8kNcp3cgum/SVoj1JpQbUh4GN6BG/G20aljR49PGzcG38ZX5Qi/uDCEXIInj7mz6Rp5Hl/BLbl5OQXZgHc7YNVuI1sB15sAr5pT4g0JyfqkRHjkLL5Y'
        b'DBVcJ/vJs2Qv2Un2wYLbM6N8HkJ9U8Ojnhnrxxk6oHR06Cp2pvqomcwqk+aUb4RZXCODOeXZnMrYnPJrZdKcVranQbIOcyovcFCabwuZf1nhnABX1W+rc81vlH9iqrJe'
        b'tGRx1xfHXo89vOGB4VfFp61byrZoTxs+1r7ab4v1tCFmZ1aqrLIfink5bKh5tl7hostoCUqGIWwl96HrO+iylE/k8DW8v5DdJTdGxiYmw8g0GfAd0sghJd7OJ63GF1x0'
        b'ieGLkVmJSfFZSbH4EQ+3DvFJcytcjIQ9Wjc1MYm05KUVkJMKpCzjyKUJ+KiL9qUKb+iXFkOas/Al4F9ruMyIKXrOy8fr9TIH7W9bcg497jPJ6qhdZanRWUUGlOy01Jmn'
        b'eGVum0CHwamkIzU9lIviHPTSQcdJL/eG1JirLU5gVhav3OyodHpVRqPDXWM0esOMxgq7xVzjrjMa9XwbLLimyO5Q0URBE1rfDApDS2G8GMkrOZ5TstQdQ8fm7Nh5idBF'
        b'DhXi0zw+wE3HHnIvs4Jvhwxs/kZTZOAZOsitcj86yLpFB2v7Je6vzo8OvQvc0XA9RU/2xBY486Dh5BzCZ8hVfJU1Ep/E1+fh/eRELtzj9Ih4AP0PMQJJNkyGG8dg1luB'
        b'gHIKhG+uyWcvhVeSVvwQHyXN9MZMBEi/iVxxU8hjyN0n3bg5DHgW1wvh+wLZ746Cch15oCJ7IxJp+WxEDg9fyx6PIo1F5PCsxGQl4hYicmY2aWWPTyA3cmauILtnw/Uq'
        b'lG8gx1k3oHVbs8huGHlDOmCHAVboXX2IuxfcWkhOjXySp4xt3gBIFgvshWi8m5xaTYtPrSM7IZ2NT7EbdWTLMHwfKiL7S8ZAgreSCyJbqH2GsPLbgNBN8I9cx/fEoWpY'
        b'gtfj+zDO5Ci5SDbDv6HQLvpSLrkymbA7D8kWsg3+4dt1DM7oUbPw/QhKS5aSrZSinMdbWM9hBl6cQF6ApoUVpqEwAHbGHUGhNGo0JVDTqNRsNIqLY6PRhxwYQnYD5qWS'
        b'ncko1YbFppIGZcEyfASIzX64h3cg40rc4o6FO2ryPCzZVidpXQbc6y6+wZOz3PChlYw0+KkRLyEhw5h+kFSievR05BqunmsEWdAhr+ee5ZfKqezD1o24eHgvn5zq5Sr0'
        b'nLg45L4F8Th0kt3mdFXUVtdNmU+rpPUrkXsq7dXuoeR+riRrMHadRfbgViClTYUFZJse35KNHo2bc/EuvB0/hJaHkYsIPyD3woDrv0hu2P4V8geFcw8d0K3vjtj+ULux'
        b'KLrhJ/rGRa8899JLb732F+5AS4is6a1LaR+lN4XJ8n79MnnyX1f5muqvTl36YG+/0ONR22Kdr25ynnYtqn96lDIlY9WBX/33bGfcjVmtldYVw/9ue33POztPvPbV/Bxn'
        b'1SvDspJv/67P0WWxjvVNcxfmvXwqurn+5b35x5YMXvfR5d/W/XvQ2o+iXF98cyXm9+cHp4aP3P9vHkhlLJs6/GhZYrKebAXGhVtTlPgiPyYVX3JReaoIHx0M8gZpzM4r'
        b'AB7SqoA5v8YDJj1LDokk8UheHWk2gEAGEiF5ME75DD8sltxx6ehMX8tdwZgg2QpyFmnCF3NgHZHTvcfKyK5Y0shoMYzTZvqURKfxgVWMVE95ogPd1MvbFbSbSW+Ypaai'
        b'VrAYKTFlZHQQxZcsOSfn1NKvnAuF30g+iovkNFws59AGkFfO6Q2tqTU6QcCvsjgdlME7KG3q2BLeEUmvI/xUlVaT7aeqd6MCqepgKIkg1/DFYEySO9NRP7JLvpy8uKAb'
        b'6spYbRB17Z7ZVrVntv614qeuIaIA1TKsN6IyftETKxYNHCjJSpPysxCIhak/XVOXYB6jQJms9NnBkSApoQm6pArN+hKd+Ojap8MQEAv1+xHL8ozr8hEjEP3JRnJlTOqy'
        b'ejldPqh8FTltS//pWeRcCDdf2XPpc9NnwNLzzG9Y4/d9sv7qwesLtgrFBxri0oG/H4pLh//NhvX2V7WvWjMHbRka1rgo9Mc/yg2dnrh7eOMrO3FoedOYX4x2pf56/Rum'
        b'H1lDre+/gVC/sdGfat/X8wwdQ/Aucpsx77WpEu8G+WaHi2JCDazbvYnJ2YYEfTIIYYCP58hhhGJ18mfIjRKJMHwrkvWqqLJULDFWOCyCzVXrMEocm817WSxDtUhIAbV6'
        b'BaCWrMImeFUVte4al2Nl95hFSaejtx+zGJfwQzgThFl6KBk+dAwgVRZoM3h7YTKIl03QsxRgDDuAhU/Gh5Xk/DhymniGB6kAfhxj4hwHWNYmznEMw7oW0YPEOdrGER0w'
        b'bJiIYTMXRgGGZQ0PQ6ZJ3rwECZlW6XoBMqXOVteZ8tLiZ6NSVnoplMrj86MippryRpuWiihWtYrqpEWJamQyNHCTxcIhYzUoFs23y4tMmrHRNWJh5rQ+oHFXDQybahqw'
        b'1TxILBw/fgCagLKWwJOLJtpXiIWXI4eAEtzo4OtMi0Y+mSwWOqePQFkoa5Z2qomfUZ8mFv4tU4+K0CfxyGTi/zNULxb+PTwJzUe6iaoiE+8yLhMLV4+hukh8SojOpJm8'
        b'ZrFYSOJDYX2czYqINBn6oZVi4YsRI1EeWlGm1pmGLljqFgs1kxNRKTpQq4k0lf8ta6RYqJgYh1JRXTRnMg2w201i4aX0EFBl/lLPm0yaP8VLdWZN0qIByLRUkWoypJmr'
        b'xcIFA/qhsehtNxdpqn8/u14svB81GE1CpjhVqqne7pIavzByGEiEZ5O0yDSttUTqZlNuDDKg52fLdKZJ7w6cJBaq56agRehfcyNSTUNDJ0gj369sLKpC6qn8VFPxR8Ml'
        b'7Wpv7mjAhH8BzTBFveTKEgtzJ6QhE/pEhepMfJphMtIPd1MyGl+LT4yhy3MjSkNpesQKybnQdWPkaGk4Go1G46PZTFoKG7N0DI/S8Q1QYcdQ9Z2V4rsgnlyEGShKgR6P'
        b'VZQw6QM/eppcGMMhLd6HxqFxA/EdsbgBN8wCukaa1Wg8Go9vh7JiNfHg3WNkiFx2oyfQE+RsLSsGwegCuTlGhfBeN2DShLgssXjrkHTcCv/vKNBENHEEPsuEIC6vCrfK'
        b'kWIISkfp45azsiesFlgWpMmOpqFpJrP4+ouKlSBmkA0z0XQ0nVzEmxjpxM/hJgeI/ngnuQoTMiMVN7LHC/rjZieHxuFjaCaaCbLGVbGWJvKIvOhUoCdzUSbKJHt1bDTS'
        b'Y8qcwEZ3g6A5C80i94tYKYjH2wucKjQCN1E8L5rFIFbgK/NJKx3BecC9svFdIlatCO9PoCPkDr6JclBOFtkuNvCsAoOExqNImKpclGskL7A+ThwYSlqVaGE6YHbeqDpW'
        b'xbo4fIG0cmjeOpSP8oG7i31ZVwSCAEgRE0GsLUAF+MBUUUhtBXV3PWmFhm/Cz6FC0D02wlSwbu7H98tJqwqZ8R5YjUXpuWLxNtJgDkNoJEhcs9Fs3FrA+pmTgs+Hyan8'
        b'24KKUXEZz0ROfJCcIY1hMOQb8SGgTyWgITxkz1cNrQ0DuWV7Lay/UlC494lIcpocVYRxCO+ag+A3GfpP+zkmOiNMgYZo0Fw0Fz8SkRdfSbOFyVAi3ovmoXnLFosDdRBf'
        b'iwxTUcF/ExCL+TH4sNjoZtw6CTcjlAIDuwAtKJOLj28snY2b5VTO3o/KUFktyOe9xUl7Ad/EzdDuU2uBCSxcnM/W0c2Z45EdVfHhOlPUT3OBgv3rm2++mV9C6acpXzHV'
        b'ZD8TOlcs3K5X0MJI5VST4c2J85Ht1t0+CucvoY60X/yyekdaAZ8Ru/m9p8asvx+68ZPPnl//yqAfbA+rk4UaTq5Os2ZnzdfrDp4bP3L6rIuTVaq/xpaOfnnXg8+++fr3'
        b'D1PO6vYWfXzPXpIfuen5r4tjFAn1H499tk+xOfHitTeV41IOpP5hxJW3J/2o7IH18MB3r/5oYeifD3x5LOLGF18+W/jFNx8Nurj6nQdX3hv2WqL7swGvvpnz6oGHD/RX'
        b'Hizbeknzh3ezpx4/OuXyACH2pR/99TdNDT//xzeH8NG178onVLxAWl9565Mn+uVfe10z13rsT0WD5GnPPhp6b8TgdT/9PD39nY9BoqUKgT7XAiJpASyQIyPygNNzILRe'
        b'4Mnl+pFMvzeRHaJ+XzpJEhHWkbMuahq015FNIKQlkucqSEt+Uo4hWwG63h0Z8UTj7Uy+mAoK0C6QVrflZuNLU4aBpjCBj1M4XVTGGzmVmgsvZaXEFSTFU1Mm2SFDvchO'
        b'GSgDh8k9vaJTyULWmRgQIG9oJXnDXWGkwi0TNqh5GQkaTs5TUUPNR3P0N4qXg1DQj+ZlkUwMoX9KzhHtF0RkIIi4K7qTPzhHH7/oEc3YuU/0OBZkKqB20uR8ci9A9siH'
        b'RLS66mEtH8e7FXh3CN7SjdxBDY8oQO7gem4a7FyyVYlyx2cqjbIcmCcqMtmztLMkucOzKDSvkprlI00aY1aKKK8OCSsYkyonrdRqQ+VVfDTTRs5Zeed0uOmOWfm56Yc/'
        b'ji6vsn4ifGb6xLRYlFx3ZZlDlX8tPlASW3ZweIZhS7Q1MvfI8X3HG65t4c5uH9H/7BYgcQ+Ohle1vKnnGN4sSyQHEpPm4luAdj659DjZ6hM6u5n/fuL8O10Od4XLDVKn'
        b'0WGxWhyg6oi4oKGjsQ7xatBnmNgZEzDbcic83P109/VPN31xo3+61wdN91jGOleArgtzvYFcFuc8JVmfkJ+sT8rJx00pOfm5STmg4RQoEH4Wbw0lG8pIQ7eTHyx0dj/5'
        b'QUIn/eE7TL6yQLQvHNAmghKyP4z2kOrjB3vh7QwBloSPA0kFmP10U3FCqgxl2q7+/W2Z8wko+mnS15+b3mDz/AX8zzPbrQvjPjLHz/3E9Bm6XnwA1JRSUU2Z+h+T8k0N'
        b'+ubXobvu9AWtg9kT75EGspPRFHFygfB7ksjJCYwukBfxHXISmKknUPkQFQ98t680V11jQGw7jSN4/kPF+Q9Rc1T5cMQGzn7Ft85+nH/26YtNtMJINvvof4Lmn24ZjCeX'
        b'yaWA9U5uj2tTNwKnfyU+F0IayV3S1K1eK2tnNexer+2wkdXRiKwUV39tqjahjJ8ASqxJo1JOEWXPjcvkUxJ46Buwxz+XSRrs+05ZqoXuAiCT5rmpw5Gt1a6TOfMg/5O5'
        b'sy7UfWL6wvR6OTVAf2I6a37dmjKa/2vc4bji2Na49fbT0SNDthSM1P1Y83sVmuNOPZM6bszWMa7R0aM3y/7nJc2ROLTtb3FfRP5kcjIgCR1cGJFT+AK+kJdv4JE8qTyX'
        b'w9fxA/ICwxF8zmwHngUD+wA3pBTmk5aCbHxRjvoWy8eH47M9VU7DaywrXEbBbTEKZpeIH1EifkTwXCjwCGoD4YErOPr58UTuldOHvSF2i1mA91Z+i+WD7jQ5Bvjxhla0'
        b'IwBvvgrSUKl9gWyAbp0hzbn4UjxuKtSTi1X5uKUwm3LXEeS6osxKjlXIpJlVBCLKeBFR5GyPSuFRWpUSssiYiVkOyCJjyCJnyCJbK+9KRVV2QBaFiCxnZlNFBa14P8w0'
        b'+l4/rYgXf81ke0NV8wpNdlWCAtmGzPmScxrhzku/eGfgNr32B6ka+ZrshuHPp7y+/K+en+Hn98zcMN7x0j9+fXNr5oWB4SuKd+5+66PhDXPf4/sNcDQ1J/7i5FsXbGc/'
        b'fXreE5kDo377s/cUI25vGf6NMuHrlOvvv/LD7Ne+4v45Pnby8HdAgKFUODcsnlzNYqYzFeLxCW4OuUIeslsgER7Jz6Vjt6SvuIcKsuxVF9uAXU8u23LpgmwmLYUcUuNb'
        b'aWQbjzdlDWJUat4gfAluNaYk8SCPH0TyfA4/Ii34BZGGPSSbQEzZXEGa8/FFoK94EzcLnyAt3cktyi5vtcdMTaWlHWLGiogZBygJgosWEDOU0/A8r+ZjeMdAP3oqKHoC'
        b'TlKM8yor3K5aayBN63RFANrSReUYFIyqtNKDAaj6aUx7Mx1uXJibW5hEsdSPos+Qh4PxCTk5PGRi59yM8kb/HiqyKnrI0YK2QcLhr08HHB0s4mhEwY/QnjQr6F2m7HFF'
        b'c0UcFZ7UoaljN/OgTE96o3i5WKjThKDICdNVyGTSnKhaKxa+rA5F0alxcng9730oYYXTa6PQ8PoVAMo04MGS0WLh58kD0YSpAgdyU/1PM2ZKBo8xoN9rhsuBco7eZJPq'
        b'vJeoQpoVlTKkM9l7xfQXC71PxqOiFds4gF5+45kFYuHPBz2F6gXQzlNNDuv0GWLhryZNQisGvMkDoOLf21aLhWvs6cgV/XcFtNMxfsE4yeRgiUOpmqO0zgGPxkuAQlAS'
        b'mq95UQWvly/OKBcLb47rhXTq4dS6YFg3fYBY+NSIDLRe0ySDwqiTowvFwq8mw/KOnaiEHmneXCZZlXY9qUGxVaAMFpnyvllYInGNwn5obNEgOvIDNpt6i4UnnwL1K7aG'
        b'9r0Yx0qsZIK1CD0/4HU5AFocEdZXLMweaUGvqzM4ADRSvny+WPjcJCt6A9lU8HpmRG6oWHhMGYMM8a8qoXBSYn/JXmIcqEUDhAUqGLq8d63RYuHFhNXob643VNCkmE/X'
        b'RYmFR2rHICHyEKwr0+jPB9WJhQfdw9AM9QDAWVN5/4lFyPbFX17gnHrIG14Nn/NsfgFJjdz82rWv/rzr9KZXxxkmqG9/cqJvbMi5Z3e+vvWVFZYY669fqIva/tLE2MNj'
        b'N/74X6vXjvnwzHAhY+WXxzeGlidYe88oUk2YVhRvmPADzYiXUPysqZYNS465XiotS31fPveb1f/afrv8oWrUtZETUciyfr/aGn0r5s5npb95Oz/qiX3/Patu4rs7+21w'
        b'fMw/WXBqrfHUtidc/75z/+XtoQk/njPvYsKfrpx79Y8nP/5z5M8vnNWs+PRQ36M1w385e8Sfrv1z1yHdtb9u7D22afVPJu5+1Lz2xELDvH77Dt5/e3/Vo5/debPfnh/N'
        b'2OGx4Ms129/5fb/fJt/4n6+8/5vzxZQ/L7rvmlS37H//kfVYc+zR34anlH89dE3+75/+499mPlh7bL23VffHzY17VjZW/udMYf2g42u/4b6ebfvBJdA4RAluX+0ixp0D'
        b'OLMc36fMGT9HTojs/Up0n1xDfNZKIKItuZT6XuBXWshFJv6TveT53vPIzUSoIoFDcjdHmvCBafrwb6Gf3550Q50DjdaU+paba5YYq2rtNkpPGQkuFUnwRLUMiDD8DWcS'
        b'QiSnY3sjkUxaiOI1crpnwrOdE/iVtfvPrrQyDTwfxYUC+VZzDp2ffIMUutJidgRQ7G7YCecY4ifWtIrLAcT6F9GBxDoJygrw9oUisc4BXbsZb2fODjtIUx5MkEGJJpNr'
        b'SnyfJ3fIPnwgSHdQSP+dVkgs1LUMlfFCGLOD86CS8IJsU0iZzCIX5IJiE2rgyhRwrZSulXCtkq5VcK2WrtUWOWUDVl4IEUI3qaEkxAOCb1koE0g0XlWGIDgsTmdBhVKC'
        b'rw5kI+mUjYguOH6XHKtaYibKRjUwExUwEyVjJirGTJRrVV3tqXeUjhUFzGBlxVvx6RK40GQPQUO0TtHv4vgst9zphKut50YM3Jqm5dM08j/+eMQHZTmLEwa9FPbJCpQv'
        b'Lz5f8rwroeSL1i/femPxrK926Q0fVv2s4uk5B94bVb5obPThZZZ33wx/eZltBXZ/9u7BZXf+85v0GnPU519PCdv8X2+N2d1UsbH5g9mNJot20PyNFz5I/vyfqom/GLjw'
        b'2Bl9qLgRuC0X36ErCESSG6N9K4ictTKbzhz8Yr24S1hEbvgdOshOcl7cxLy6lhySNjHxnZWIbWIOIzvYu1HDyE4qfGaTltWgwUDN5D6PmyaTfWxxhuH9NYnJSaC7JeC9'
        b'8OZJPhUfJHuZRQhfnEqO4ma8g+zITcI78A4VCoupKQQFD58U2K6SipzBZ3BzIaxs0pKox+flKIJswftCZC58cokomG3Cp/A+9owBn5ODNHweKdV83AR8iFWBT+N95AZu'
        b'TgHZLDmbbC8s6s8MT6dkZMNTetbG3FWge4O6nZOfxKEw0rwUZLjbqZM6yufqHlOPNuqgMhprLMuNxrY903UgXLO9UjUXA6IZvYrilNLvqggJkZOl98SVrvbKKuxOtnMF'
        b'mqfNtdKrrqulG+uCxat0uhwWi8urcde0GTK6UzOUDrqp5KDqg7gXRu1NDupe6Yj3k4hhkPwngERs6RdAIjq00i+8cdIfXQROugTr0WJRaeAK9JxXbZS26eBa7rTYrW1e'
        b'BOJwqSfZzdXlgnlKONRC1wxaFemD5bv1rcCsIjCFkY4UEL4EPww/IEciJFofjJ42P8ToG/Vuao3oca1SO1VGcQa7qTOyQ51BUnIyEm0+QB57Jh9v+naLj6zA9pgTFE5K'
        b'Pv7wp798bvqE2XA01vftHBpPorX8+8/8Q88xIoCvkP34Cizlo5y0DtkaDCHnJQeRzhVqmzPA9Nbmm7UOfmNW9fFNe9BTPoMOG6g2HOeDGF2Cf+xSIInifJr6evj9izYQ'
        b'jzsHAuSc/ujDAF+N1C3MaPSGGo2i5zJca4zGpW6zXbzDVgosR0dtncXhWimuqBHByyqFdZe6kZmdzgqL3e5b1x2tRoBj4mPwCOvCUEj+iSTLoVqBuKhIDcd+eTcb+034'
        b'AnnoxM/xedn6nKRkJQpdTG1klwcHTXCY9N8JKkQbW+bKZHtkeyL2RMJf+J4IG2/l4Ur6FfgWpWCgbDvAazUS2CZl3CHAguUWBTBu1SYEbDqkhQfmrRBCWT6M5VWQ17B8'
        b'OMurIa9l+QiWD4F8JMv3YvlQyEexfG+WD4N8NMv3YXkN5GNYvi/Lh0PLQgHnY4W4TeoyLe2JQEWEfi0ca7MGxI3+wgAmLkTAuwPpu5YIYRC8LSuLZD2PEAa38EKSZAOR'
        b'CTphCOtbL3h+KIM1jMGKgvxwlh/B8r3Ft/eo9qitsj1yYWSLTEhmwoXof05HS+uJsIYI8YKe1RgNNSSwGhJZDX0EGVuJKSC8VDCy+HhUqC7gRyoVneKD7uiVXrkNRE6v'
        b'nOJgZyhXUKGSJpwuEq1vdWdSQiFKQSF08KRJ9bkoa61aiYComEykBgKiYgREzQiIaq0aCIjYbPkH/wNLNqhZ9Ce7xuayme22VdSLv8qiM0udsAFzMtdU0GMA7V9JrzM7'
        b'zNU62qF03UwbvOVgr2ZPyyjQ1Tp0Zt3oJJe7zm6BStgNa62jWldr7VAR/bGI78fTlw26adnT9bSK+Izp0wvnFJQaC+bkT5tZDDcyCnKN0wtnzNQnd1pNKYCxm10uqGq5'
        b'zW7XlVt0FbU1y2CFWwR6OoE2o6LWAbSjrrZGsNVUdloL64HZ7aqtNrtsFWa7fWWyLqNGLLY5dcz2DPVBf3TLYMwEYFcdmyMND53pdNYueuU7a+EbXlA9BIujy5clriu+'
        b'L2VgjEoKk8akjR+vy8grysrQjda3q7XTPomQdPG1dfTYhtneyQD6gEJ3JIhw1XmLe1KPj+eKdfly378+kduKtYnX36OuIHN5RwuopsBNFyQ+SZ5bRE2GhmTqUpE7jzTm'
        b'km3ZlnwFonYv/IBcwneYQcE1ZzsawKH44aNN2lVVmchNHbVXkk3kLLMZFpFGei4jhTTBVWEJqyZ/Tha5izfgS1kF+fnZ+RzCW8mJEHJr0iRW412jivrwo18NNWkUlXOR'
        b'm0oJ+NIUcoXusSbmUq/BvNlZbbI12UWu4zN6fA6VZKiAoR/OYPVsczK3f12R3GT/rcos2j/mZtLNbxT7ToYp7yVjNXJTFoev5eDzgZWTxjxQH6G1KcVZZGueEx9Uolnk'
        b'lJJcIxvIs6J3wnZ8YbWTbMAHllJP5B20E88utR3838cy5xtwv+r53BE7cmv4tMgZv1n2kx2FSN/fwW9/aeDbmT98lbfttJrnHwp/eO5uRsFOZ93YH7758YK1Tyff7ZV6'
        b'4LBKc/sn92dU/unTn/bp+79zfr4hufS/f/7suz//fNzJYWtK6vd4nt9c3vL1Fz8+o2n54zOZlbv+VJX5k9W3969bsvZX5zxrv/royYEN/3UxTz/WuerfltrWy8ZVrScf'
        b'GSxf7/y0+b9G/rXw01fsC9/J+PFerWHdY8Pw5bq+f/lodEzr+UXz1pbW6I6o6gods++OrjxlWdj7fvyouOTa47ZZv0lw6aOYtFRVWB0GA6TPdyclkK3D+qXwqA/2yNUZ'
        b'A5hapMEHsUfcY/dvsIfiezy5vIQ0ihsaG3FrTG5yTr4hG7eQHXSMZSjb2Q/fkNeQg6I7PWnInNu2aYYbB/JJ+AzxuKi0Qp4DXe+Qf7eJ1oAvGGklfcgmGbmDz05iLSEH'
        b'yDV9wL7aI0BGaW8tN91F0YncmAx43Qx/OxIJPXkj7V3mQs8A3ycvo9v0s/A1Fah3d/oyhS1sIfaIlgXACCUKm42P4U08xcIH7P5A0BSbfZ1SkEOgiN7gyD1yh1wRbenH'
        b'h+JzVN+jb8vIYQ4NgS6cJWfFu3fm4r30/Vx2SEpB7iWW8Ry5q2cet/j2QtIYpE+SQxEoAtRJrdxF2SbMx3CqK7bo2XEpQ/bIVDrCYmWJuFVBNgOGXxHV4rN9IlhdeRy0'
        b'4zkubAXeCYJwk7iVcH1WX7iZnE/beIvT4SP48IhUUe29Si6QfbSN+dTVwZCtwBuSkbZSlj4E5ociyGrcmgovS/LccHIfaafLMkkjuSxOywa8UU3fN8BIU2dXcrIv0uKz'
        b'shn4/jzfbpb2/9n61V5cB1nYBsxdUmUzfZJ6mpr5ZWp40SlCzml5DRfDU/OWRnIKjoQ/Zbtfngrh8KvhQcETyW6yD0CBKByHiII8JYSOicinrLYTrdt0gB5r53qVWEnv'
        b'4NpZnQn+ipnw/SQkg4P0hw9HBuoPHZrec92UijvdaHzzA/RfCYZP/308otQvHVG+BZKEj3HFOyxmIam2xr5SnwxQZEJtxbe2aJPYIrmx3FbRTYMW+hr0eDgFD5JVt9B7'
        b'qlIrmILVDdxn/HATuxd+vhv4KgbeQb18uwFu9gNPDpScvi/8UAn+Ys437jwsK7OogzKk7KYtQvBAdCdTfbeGsJngHTN8i6CbNlT625DSE1ns+wyI2I5R3bdjsb8dSd8u'
        b'xX0XtBCXJ2tDN+Cr/eBTS5liApADrW86aUp1dnbGudMWfH8DjozNmfzxiQ5C6XSqUDh1tnbr0mmxVLMz1aDFMD2jw4v0nLWkXJWAMgM9mul21OqKzCurLTUupy4DetBR'
        b'Bo6HbkJn4cVl45NHJ6fqu5aS6Y8CdTSbl0pHbwf1w5cSKS9DeNvT8qkcPh9PTtrWzr7IM48W/i8TqQtRlvn1j+OLPzG9Xk4difjyj6NfjT79zMfaV1codTuG/OjZAxta'
        b'FehlEjI7/RW9nB2TwefxHvwwkFlSTkn24B3ALa+Qk+whC9ncL0gakkQhfNQI0pB9PBOoJk7Gh+lZZHpvAbkhHkVOUbqoI19V7Hx8PjKXiST8M1wK3o23dWf5UlFzk+8g'
        b'jeRktA4tC+ViqGlVIvfSMwXf0eSVA0ldEMvapQ023QbXDy9T9teNNxG1DiAP1yNvIsk28NjTARVKLC7RIuC2u2ygD0uk3O2UFGAWSMDlMNc4zQEBAcpXdqiI1pHObCLp'
        b'pnx4BqqCf+ZKi8PUjZpGfzoaOSVHlTljdyA0YiKPUk3JS6xpovI1ew3e26XuhZvIWdC/OuheJnzWVrR+kJydsz28u/pzU4759Z0tHxuKP2Uujl8In5nkb+m3vWOYmTBC'
        b'o5+6rHfRyYaJx9I2D2G4mxgadvPBID3PpFX5GHwvGzcH6Ao+TWHuWiatZuJD2iBplcmqS6cESKvkKN4huSJ92zam0+Iy+uaGMWWGnZE+7FyHOJ9MtyrOh0Md3inwAWMI'
        b'OTEYZTtxeGJPtCEvdQ9bFYS8jYEuT90A7qmYow1+rRsivyWYx/QUbZN9x4woWevc9Yo5tTCHFmow9Du1dOd45bO5ga7R0ebmX1q1DlulrcbsgnbZhK7YYY1luUSy05LT'
        b'OrFsdG3OEUSbCeuyz2MSACXrii1L3TaHNCICXFW4dIKl3OZydmpCogsbWuCsrfaJVDbgkma7s5ZVIFYtDqrV4nB2bWByV4gtmj4tG/ivbamb1gfiSDzltTqHr1UAK9tl'
        b'pty3e/rQcV9XXeB+CjEf1A2w7AvoVjiLO1CQNDvLfx6smDTmzc6SFevxuWzdM+XkId7icKy1PROCplVGVOMbLubhSZo48mygcYTDmwLqQPg62TsHGNVebim5qZ5HTpIW'
        b'8YDz4QKyhbRqQM+1IXIW4WMD+rgz4EYMvhXj1LrnZlG/8Dmk0TCX7dA343OlWYbcJ+hhkG3ZeWQrB6TppH4F3jecnC7lEdmLb2uKyE58iQVTIAcnAvFoxhtkbS2r89da'
        b'NC9prgoVrVPik2RPL9tF7wiZcwm8lb1qZdK2++HrUyOn/7n3lAXrZ8fKlc/fTcjS63pHhraOOzO1YsHaVVti//jlgV5RA0vMH/6w7/Rdpavk8qUn5rx5V9774JTXZ7Qs'
        b'ab3emvz303t/8srKf8139nm3/icvLv/pe1/drl6/antm4iv/VvT9YvBt4TN9CDMLLA/Dm4AaSxozCqvhQYfeQw7jU1UuKjiTY4PxjbAEesCA0kIgl3gLOchI5mDcKidX'
        b'8BnSKjqTHH4Gn/SZRsg5kAUO8Un4QRkDgzesxNQy4t9v1kTK8KnBfciueYwmu6PJpWCCTJoGMZpsiGa19x+Nz+HrFp+kIIoJ+O5C9rYJ78cvBjsqk1PMnhL9FHt7YjrZ'
        b'OAhvDzQr4J31eBc7W5E4ilztPTXAqoAPz+YkR74eOapQotlGInynK4e2UfjeatDIRSqvkWi9mFO2I71BtRT42sAoqZ/2dUf4ZQGPtVH/IkiaKNWN9lH/9eh/oruk/0GN'
        b'6KHCB2ou0LFuqP5xP9VPY1pWG5nrTr34TkonbYO7O1X7pL8NT3ZK3abPmd7eVN9Ja6h7ULXDYvUqnbbKGovgDQG67HY4QKDPrJBLLaWWa42P7E0T+VJbCCXkCZP8ZTRW'
        b'jcSl5I0K4FIK4FJyxqUUjEvJ1yokLlUFXOpgt1xKDBklSm6M4AcqK13vD9G+iOTe967fWb9rUz/rufgWewVGjZaZqZqWrJturqE6kVm6V74YGFenHIvuQgETKSmcMD41'
        b'je0/0b0hgSqeoC51Cd4/4Om6TLu5Ure8yiLtbkGHaZ/bnvB1qivwNbWuTsA4LNCRGme6LqO9SGySuvMtLK+jThZa4KbaL/CfLRHBHI80SuR3ThYUFUvMixsdBerObtKa'
        b'S1pz0AjyCD8kJ7XkEE8OuCfTiq7g9erc5KSEHCCpgXX46sbHyIXZWTlz4qVQCCBMk1MDNeQsvjFU9AlNEI/N71y5erF50Ejkpq7rlVPxzU6k81FkAwjoSTn5JYGyeXNJ'
        b'CDVe4+fdNOYZuUZuLCLN7CFmuc6mrHJOXCJloIEbI1mGnLzk7KQEJSLNes1SfI00udMokzgdEx+0h0L7Q1WDeKDaIIEboslGfVKOAq0iZ0JwS8havYwpuZUJSQDWgQ/k'
        b'5MuQfAqHL5AN88RN/APkAj6VKL6eT52oDj4dw6+ehLe7qc8Q2YE3kObEnHw6jBFkP4wkh3qPkpHD5BreblOu/rHMuRmeO3PkxMA374eTVI28qNjYzI3e7Hk98tOfjWpJ'
        b'uJemLoy8Z1r2+tXTv1j05fonj4xT3h389uwvm3814fX0XS9cvGxefOvE2x/u+yinaunJY6f7NE+/HV94e1JS3Dv5DQ8u9dN/XZVT907LhMQ7O4f0VbyX/nCeNaK+5U7C'
        b'2z/7/Knz3/zL8OErYd6VXHV0gvWj0cCwaWfH4auyXGjgBsbJ+HIuDR8Jc1EfxHnkaHEQp66xBfDpp/AJxiunUa8tOsPn8I1Arn94JdnKrOTQ9Yf4fm52fgLITzyiFvFN'
        b'Rh5vmB3KrOQz4ohPdSoeGKg8kdP4KmthBjnozs0GeajZ4IuZZk0T2TC+C7NLmuLIrULmkKq080PxvkK2+zKYnTiiHquFLPwGblHlG2A6UmQgu5EmJkZkLsEHAiz8ZDd+'
        b'pGAmfk1vkVlq/o+M8mGUEUqkg3FzQxs3H0t5uVbi4xp2BkD807CDKrxofe8dyFKlmiSOrhQ51ByazKXJvGC2HvLdvGnlYk3z/Ex/rp/rLaDI247z/2ZoIOfvrJk9Nbar'
        b'fS90w3Nf9/PcIZRZACllrMPPa4Is63LmHsTDH5epj3HQI3cOShgc1F5CXf6E2gqjke0eOKjsz3YZvLJyW0WXGxlelc8MTA04TBH2hgepqkw8CpCbFrC3pPaJE9br/2jT'
        b'pyt0c1DKG0dH6hm4UMvlfDQgFOIGjeOZ4NjjlNeGDgrjqXDJh3LRMYF3ojjdYHrF4gmSs+QEvuUk5ytoiJwURvdCV/FAtXeTC0GMLFT67/y6nX+TMKdMLsjLFDZUphQU'
        b'ZSr4UwvKshBhblmoEF4WtkexR70ncg9nle2JFLQtvDAPRJ4wT6RVJkQIkcxzR2MJF3oJUcwvKbqFL9NCvg/Lx7B8BOT7snwsy0fu0Vp6iaFlQJSiDjYRnl5WtRAn9KO+'
        b'SFBj1B4twI0U+rcwt2j2XC+rQhggDJSe6A11DhIGM+fnaHiG+jlR3yR1WR9oGycMFYbBdYwwXBixCZX1FUYKo+B/LPM2QmVx0hsJQiI81U8wCElQ2l9IFlLg/wAhVUiD'
        b'/wM9SqhptDAGnhnkQXA9VhgH14OF8cITcF/HyiYIE6FsiJAuPAllQ6WaJwmToXSYMEV4CkqHS6VThQwoHSHlpgnTITdSys0QZkJulJTLFGZBLp5ByBKy4VrPrnOEXLhO'
        b'YNd5Qj5cJ3pC4LpAKIRrg0cN10XCbLhOEuZLBhSZUCKUbgopSxYUTABd4FVmVDOHqvNB0g9d2OIN0adKDC8Kgh0NFFfpMFOJThTHKlb63X3aOdUEe2g5oIJqi8tWoaPe'
        b'f2bRblkhSpVQQAVFqFO0iNhX6mprRNGvM9HMqzQuM9vdFm+I0dcGr2zmnOKCx5OqXK669JSU5cuXJ1sqypMtbkdtnRn+pThdZpczheatK0AYbrtKEsw2+8rkFdV2r2x6'
        b'XpFXljUn0yvLnlHsleUULfDKcovneWVzZs3P1PNehQhW7YPqt1nR/37PlrWUqvLOUEpZ1/CNXD3fwAncEplTV88v5hpAiXAYXLzA1/MxiIaKbeTrAY3XcIKsnluidCyq'
        b'56jbILzHLZbRALNCSBw8F4ui0RNoDVejhvsqetWI6Hv1yCiHekG3gCuloGY7HqEfGDvTK9p7nEkz3OZw1v6FrqR1Ng6irmAW62Al3ZifxAFLZz5dJYVJY0enPRGIQAKo'
        b'GNlWKrrrnHWWCpvVZhEMnQr4NhdVB4C1+XzLGGSfjiciK2gcDlu5uwsVIZ3eTjcJFqsZuIYfhUygc9gqqmjtNnGcAA0lOIBcHfv2KZ31x31sNWyjqK03o0Y4R3m5ZC+X'
        b'+imVMz6l7PaxLDk1teDTb+BHr/JGtodNtznM9roqszd0Lu3OTIej1uFVOOvsNpeDEm+vwl0Hq8RB4yD4NjiqaVKDuj21zRjru35xIVQO7CJGslboeCrjrIoQsaDn+/Li'
        b'djRrVjdSwt/9u/I+AP5N+aT2eMNmb2WdRWeCWakAPm5PniH+N5mSAcYU1AMXcWmbWui+Wf/yCy/9mWtA57jYObBI5NuCbUCL+TA/UBmbCq/a7DQy50uv2rKirrYGVNVu'
        b'GvJvf0Mq2Ga9u7oc1F0YCGkEdHV2cwXdETW7dHaL2enSjdYn6+Y4LQzPy902uyvJVgMj5oBxFEwmiqZmYbEbHqQPBNfSxV4qO+vDsRAI/oDQ/rM+HLOxd72vSq0Xf+qM'
        b'ysypo2KWSGEsKyqqzDWVFp2DFZWb6WZArbh9Ck+ZdXWO2mU2ujVavpIWdqiMbq7WWYBNTIfhdECHpplrljCzuNNVC0Igowc1PVr70rr3NcnImmSiY+pma12kLJQE+c3h'
        b'MKbUF7WTjTUantviqqptY1kGndMGRFSqhr5Gd7cDPVq76qNUUToN8J1ukrhpJzt03Ro1ymtraeRVnTXQeuJmUyG0m4ZOqeJyiwMW5TJghuZyuk3fhR3FL0nSldcx8om2'
        b'gJ2Jyymh4e9A2ccn8D6qu+bOo0YGsj0LLgvnxOcYspOUqDpKTR7JVrP41KPwhVGYRhu+OTs+J4kGxd2RWIBvzowjJ4qTyGkejZ2lqKwhV5gNoAS3RDuT83PI3uXKKFAr'
        b'N6EIvF+WrML3RM/NF1NWBhod4guSEnKTin315irQInJMiFTj+2QjuShaFa4kTiD3Sp3xUshwBd7Bkat4C9kkBvw+V5MMQMmeOaSF7J2Tz6E1uEldyJEbK2ZlMudMO976'
        b'NG2SAsnwgSyyg8Prx+FGdpqbnMKH8T5nlmjYyV1egy/LUS9oML5ILpIdLCr5NHKEXB46xhnPgv0o1nDkEjmIN5Ta6rf8kne+CU+8dXfawJbJxdMyIjet/sd+VULm3Idh'
        b'K0Jfb8wK32bYde5n/Yb+dL1p/NJdk5v++0v5kc0LTnx66E9f36vkdvc63vf4oOGx2WPH/s3Q1IA3rv5of7/oXRPvDT31598VfiD8LXdyzpzfT2poVixY8eTfEnYf95Cf'
        b'HbwQc/fW35r2pawesfL9zW9pBx9+6QNbZuLAy/u+mn+u3x9mNz/7q4pJ33x5fsTfn9sXPvZHP69Tj1rjUVZemfzV4sVP/cI8edf+Xx978I39TsqDGydmfnXt2JWGq6+8'
        b'fuTyu/m1B16suXNh8jXXb/S9RB/ErXi/jsUxIs0qJE/CF+Zy+BK+l8zMFnkV+GZiEtlKmlKySItMQ04iTaZMOYYcF0/qnSF3I3FzCjzBIXkKvlTKsaCoDSwQ8qx1ZYk5'
        b'+XlwZ0ivHA4fHY5PMlMGzOpN89I8agzJVyGlnFeT9anszrrl5HYuawy81LdyFYdPTI9jXqB4a0p+WALeTYOi+00xAYaYHHxF9Fe8oKTRVfQJPjTKI1ciyHXZStKKHzAY'
        b'KnLXJRpo5HIFOUhjzx8ayNwg+6+Ynii9JS8gjXEcvkpOjhHBH8Z38RZqJCEXyP1sQzJuSqGLC2rR6eTklgEfZxs7uAVfH5vbts6c+AFuSRHXWgJ5oCAb8Z0YNnSKkvFi'
        b'T6k9r4kTKlGYwJPDo6NcUQwZ95EXcwt7lydxiF/GZYDMT009y+QTxHORMD74+DrxXOQdckts4536Mbn5ubn5yaTJUIQf5PriFiTg7Qp8Be8gZ8QtpTuwHLaT5gJ8yaBE'
        b'8hnG+Rx+iC+s+A4+id/nbGEfkRIag4k/MwNR4UIyA61D2lAWkZUKRtRVM5q5Y9IziJHMGKRlpVqpNIoTN4FWDZAknE6B+L1S2CnC7+OEyYmvMtGhAZJv2pl/GoIOHHbb'
        b'GKiLSoydu7CwOCcsGBYIA1xAnBOefd2hazcWKgr8qjNRYLrIy6TzLaLER+UUYC2UPfmFLkkioOKBUxLlO3IeyfrfTqRoJ0B0LjB05GOlHYUTM2WAQfzaxz5rKV+nWx8r'
        b'qeTRsWXmiipx77zaUl3rWMl2aqxuh8iCneyLHt/Oy9trSsHiaYDroMvsqAS1xPdkt3sdNf7NDhErfHsdPpmJSjoWZ6A23w3Ll6HON/7FSB6hGvSf4eNpsLO8l2uk0BH/'
        b'ihuIhOF1tHDRvtB0sfCDdbfQCm5+vRpNXfp2xCs6tnf/dAy57wwP5xGXNIlsR+TSOPzQPQtuTMDn8Q0/UcsYKokPvo0Vkafiy6V0/30esPfmlNlZhlzfjj4QoFWDItMH'
        b'z7T9p/pHMucZqHAK/mN+S5oWp0bK//mmdkhkenSvLy/Wr8dRz/4uLufMf42b9VrYCnXE+0+/HaP43ReL5174YsiKq9fLCjd8+PyyadZnnn+1/0vTQibX7P/tOzNe7CV/'
        b'eeLPM9//5LVLH5o+vNjyXs6C5aMStk8o6f/5cj7hd2vPDX5T2du4OWpa/+f++e64EeGRZfqlCcktE4b9e9Efdzjc7/3yD0/tnjWgdf/bg3/YsKvumSF/OPWXTX96rJhV'
        b'N37H5rf1WtE7/giwrsSs+ragXklDyAVGxPWmlFx//+UoYi7eSi7L7OvimMcT3oG39wlgBowT4Mv4Rhs3IC+QR8xhb9EwfM8f5udhGI30gw+Si4ywZwPf2e2n7IysR5QH'
        b'EPYH+CZr6ER80Jibja/hB/4tAryrQjxLcIgceSqxLWZFGL7OyxdSXkaeY1xxcGI0jQhETo1LgU6ygEBFKjGu9wMTvgd8ceFciTMCW0zGF9h59eywGZQnMn64JCmII5Ln'
        b'tC6qeEVrVjMxNBuaLQ3FibHSaPDkOt7KGVPU+CS5qReZ00b8LN6eSK5OYLshCqRczA9aS+6JzH0f3jE82KFhNdnH9kmi60SPCE+f2ERDPtsPYUHGI/DuoeNkDnwqqrOj'
        b'5T3lXSpJI2DcanQgtxov8ikl40NaUOxFjkSjYWjZdobonqDlVmklpiBVFex7VhPMmLqJjMGLz7b5IdCttHhomDOmjR2tR97AiEbtYQfp1rRWpltTuZ3q1vBHjWD9BM7F'
        b'w7WsgYuBBwQ+KOc7l/2YH2F7LB+RPNoKXaEt82qMNbVGSfd1emXmcifTzTvXw72RRv/+tGhRzOF9J6t5GDZ+VV+fbaTdc0GGP//GMN2JaGTx/xt4R2Y9x3qDlsgcU2mv'
        b'HAlQQnuBqLGvJsYlE7h6lqdPWmWiMRCu5fQbAoyr8gWPR/l5ZLXNCU2oqGLcZQQQd2pnYpowvYBZYwPQ21ZdZ7dV2FxGcbidttoaNkvekNKVdaJhSRwS0YrkVTBW7FWL'
        b'VtlaRxd+uFpjncMCLMpiZM/P5n0OjzRcFsU+Xs5iM6zq4xuyoOc7TDobMIo0ArVjskGhg2TlY0QTE3Q9SqwpnnbPIHYSGtdm9RLntMOXFOjpGwDtMBoX8dJ3FFCglUu8'
        b'1zkWRrEG+fBQagybBxXFMhj2TlrQHqtURnpA3shO//jAa/3g2S2//MUHQo/1rQFO4Br4NWxA6rkl4vYctIGbBNDpx5LECeRF6Ns7aYLSaLS7jMZyXmLUCOZoVbi/DfTe'
        b'd2oC55sTftLk79IGi9Fo7aoNlk7a4Pfw9y+job4FsoSv1YmtAQLBl0itpFeiES5wXgJa1QU6Q+MsS43GxbxkQxTROKiB9H5QA3nfIGnYIFHgGt/Wqc+FvbvRqIEe1wXg'
        b'RBuoms7Gorv5kPtRYsp3mI5KmHZnF9NR+V1RQsFoMEWJKd8FJUARMS7vqg2WduvS74VOR9xHJtqOngRQ9k6pADWJGY2rO6UC4j1/j4NE2+Gd9rgv3cxBjGLzDbyv91wi'
        b'EFJ/533m+LYRqO60cUAizIJgNK718xsYidBAMsFud4d+i9nuj99b23H8W8aeUkVWaUPnVDEYYA/GI7b9eDACwSV9z/FwusuNxi1djge73fl4aFnzwr7XiLBqmzsfkWCQ'
        b'QSNCfRH8JErrQowcQT66/ZiI+wNebUGtKxsYs4WeEbII3Y1NF8dgjMZqNyDs9kCCJQ8eIvZAj1BGWj9nejBArNI9nQ9QMMCgAZoUOEC6jsjT3z9k/dsNmSTcUVRK6QEq'
        b'dT5cYUajy+G2CLZlRuN+3ndyiNH4UB4GLcrfCf9j368f/fz96NdZP0SemfL9O6IBBmqvrXWwJj7XSU96+3vS9tz360qMvysxnXWFSUHciO/dExWLCmQ0numkEwE4XBtI'
        b'heQoYI+hCHUUC8T2u2gP6CY6tLXtehG/hl8jk/oha6A9kolX1sA+eZUwZgAWNAjWsSvBvZO39c6rWF5Va7dQ5+Bqs61GsHQlK4cajWKdRuMVXlp9koDB0wPeq3r5++t7'
        b'rnP5mIqjItsLY1PT0Km00xUHZPHUKo3GO53KoezWt4ENbQO76TuArat1Go33OwXLbnUONpqBdYkgOT8JtYpbrE3B89INdFD6jMYXO4XObvVIxKjsgYiholvmIDe91Cks'
        b'duv/TJwJYQvcDFW+HAAtMnD105sOF2pn3fWvH7r+6YpZghyRLtComesJJ8gEOeVbfalWSlcK1VHpsUVx7Ugrhs2/ouBTWunjoWzH2VZTqaurXS7uWaeliq4b7rq6Whr3'
        b'5zGfmuzl0mD1rPJNm1e91G2ucdlWWQIXllcFNVXaXKCrW1bU+RTTLk0hMAoMuNH4WhsZUbNgodrA0ZAeAnylxkvRJ0DpqKTXNPK+w0aTxTShR3QcdjbkdA7o8OlT2rkp'
        b'OhZJsJ32WheNNraC5rXBlnXIW62WCpdtmRhcGki33ex0GUUbsldudDvsjkZa2zaatDk8+nHaq/YbLsKY0VbcF2Ymf6bCO7bShFGpXTShX/Rz7KPJAZrQmNKOQzQ5QpNj'
        b'NHmOJlQQcpygyUmanKIJ5f2OszQ5T5OLNKFxTh3XadJKkxs0uUmTWzS5TZNHvvnQR/3/40DZzn3FDMkbdLuDhkhVq+ScnJdzAb9AT6P7dPCZlPGcLh7+hmhU2jCNTC1T'
        b'y9VyrVL8r5FpFGr2R0u0avYbAqXSL/uG8Vh8kXeSbfggbiItojOlOpZ3kwPkeb853LfC6I/z7Xa+lL7gqVY5C+OqZhHgWBhXGgdOigDHQrYKISyvYhHhFCwinEqKAKdh'
        b'+XCWD2ER4RQsIpxKigAXyfK9WD6MRYRTMM9LlRQBLprl+7B8OIsIp2AR4VTMM1MhxLJ8HMvTqG/9WL4/y0daqI8lzQ9keRrlbRDLD2Z5GuVNx/JDWL43iwKnYFHgaD6a'
        b'RYFTsChwNN8H8iNZfhTLx0A+nuX1LN+XxXxTsJhvNB8LeQPLJ7F8HOSTWT6F5ftBPpXl01i+P+RHs/wYlh8A+bEsP47lB0J+PMs/wfKDAjw2B0semzrmq4nKhki+mkOF'
        b'qYzyZXgj6Emc0razqx9cbb/d5TvuGfCQFI6u3WPUOYR5qlSYayjRLLdIDnguG9ts8vmTsPhnPtc86lIi7upYgvefpF2vYBcSqssFHLQ1URJtFg8TCbUVbqqE+GsOqq3W'
        b'4avQ5hLNgeKrvk2k6Rn5pTOkGkxd+A0GZbKtkj+MWVfOjJdQnbj3F3gQ2CCC9PVV8gp1OSx0QILqMzuZEyptHPNSWQY1me12nZuKY/aVlCkFnTAOetnPjKmGSckL9c5w'
        b'VnGUL2pA7KHcMQ418ktCHP18HNLFbLbAG2UCcEOjmMpZqmCpkqUqlqpZGsLSUJBT6f8wltOwNJylWitNI9h1JEt7sTSKpb1ZGs3SPiyNYWlflsayNI6l/Vjan6UDWDqQ'
        b'pYNYOliQQaoTOEiHsJKhK6rq+cXDGtAM9PQikI7laxT18sXDBXkDt5NzakEOkPdFa+Q1/VipgpY64gUlSAAj6uXUFrpG7hoJEoG8gYfnp7pgHdfLRau1K56W1ysaZBxa'
        b'+pd5qBFgL9Y2cuzJcpd+I7SCia7qAscdKkOME5dAhwXT/ZLI9HJGL280PlYYRzhHOB+PaP9+lZk6cLX5gIlW4wSvphjkAlu15FepFPdAxXCkMqNN8CqMbovLQQPMiEcn'
        b'vBFimHL/sTkHlZ4c9ICzgx4oZsFwxPAr+UwWCD5hCZKhuNkNNda5HSDzWgAEkwNUbAPBZfYqjdXOSgZ6CT15qDBaxH/sHGK47zX2sS14qaKKbtSy+Ldml9sJwojDQq37'
        b'ZjuNj1RjrYUWsyG1WW0VzLka5A+RYPhvm6tdbR3yRhvttRVme/AZfxp1uIpuLzuhfWzBQjXsvxiN2DvA2G7IQc6FxSg9q4Draqc3FBrpcDmpyziTpLwqmBc6J15thm9m'
        b'xJlQOS0u6YbTaXHQCtkNENaYywP7nINyyXL6lfGAOAnV6NujNLDZfY9KiWVMSoxiTh3tY2upO5R08cuL/6OYXYpuqVFrMQ01v6pvuxHpcaBnyWH156hbh9Uomc+PNrY9'
        b'IL9D7aRS5jxRs6TtnKdBjLvgqpXOw1L/RgGots26EmhxAI3ssX+tpBFN6r65fXzNfTwyOPQW9TWornW1HcNlcUd7cBJYsuY91T3cWD/c4JhbHcHSQKc9DnqV0T3U/sG9'
        b'DYy41Q6sFHW0p739lmBbg/xw9Z0E2/qeoKt6FNBpiB/0bzJ0YqxZp7tcOiTCHOgpPMnjR4rt1G27mOQkVsT2VqmgUwevUSGFBcHpJFpUsq6krcxqs1CAktQAtcMDbf5A'
        b'fl7g1CVI45RggEubi/33xeVKYDupCWJ4rIQeD1Z+94MV7x+ssR0Do3SBnxnT5mWkQDKz52vjF923ItHfiklBB/VpBBJLefCR/fatmV48c0bKjJnTSnveml9235pkf2uK'
        b'2cwHsG/JQ8x3GqCd61KybgYLlCI6atmXm1c6pVPruhpLpZlq3j1u46+6b+NofxsTfEjuc74KaK7Eo3XxJXPnlfV8fH7dPexxftijGFmvrV1CxVrx3D1Iu3V1tfQQFkhF'
        b'bvGkfo8Bv9094Al+wBGl/nM1PQMgWbDe6R7Ak8FUqxrWqbnSEoB8dVUrndT1TleUkV0A69re8755uwc9JXhQ20DaayuDIeric4tnZvZ8Nn/TPeAMP2DR5bBGSHLVJsG/'
        b'Nlati5/ZM4gSB/5t9xBn+CEO7DQChC4+v2fgJBL3u+7BzfKDGyL6VII4WEMPnkiLQ4zDUTSnuKjnIN/tHmSOH2QUo2dMNpZO0PR4FD/oHkZ+GwVoT6WoPE29geh1/LTC'
        b'wtzsglmlM+f3hEJKsH/fPewiP+w/t4cdLOMn6zKBIsyyQGtqmPzn9GvbnUWBB0I1LzuzlMZyN+hmzZ1u0BUVZ+dnFBSWZhh0tAe5MxfoDcy/KJOiSpVUZ1e1zSjMh1Uj'
        b'VpeZkZ+dt0C8LpkzLTBbWpxRUJIxvTS7kD0LEJgFYLnNSZ1q6+xmGuBKjA7S0wH8sPsBnOsfwKEB5FtUh0SENLMFaHbCGPYUKd/rHuYCP8zx7SdN1NmSdRltp92yCzIL'
        b'YfhnFMyiNJ0iUY8Jzvvdt2ORvx19Sxk/F9VEmDyBYk1tz2XQ/+4ekLGNmksRW9jpSRGMpc3iE6hr9HSsP+oedHkwiWsjbdS3XEeNVO2YB90Q8W+EzJXAOQuYW14s2zBk'
        b'7l51A+i1eLKWbnzAn7wBUiN9XsHc+BT0TSNLF1PTiKqB4wK44OMni0Xfa2qm8ssvojDVZjDrXNhK1qsdP6NdfJom7WI5M1sDdTB00O9/+nbtJ6DO9orC6GfWpEotMslD'
        b'AoEGG8tc9Khz6Kr+7ZXJgHc6nyVqNBM4aXO+VNwE6HyK6KZDraxtl6qD4up3v2m/OxbkcOTQsh0yRDd1KwN25XgH3YfyyqnhoQsXPLVkljDSoZEcSthJjU6aIj7YeZ+j'
        b'g5pCQ+8KPs9MZsfytUXBxq1rf0C7pcZoXN6uLZ0YDthzBfphnW1AMYMG2zLyatsZpyb4saYNYZ7x4Yo3PNg2pZRMUyqJQ7Mv6XqVkllKIVql5MwoJac2KRaKxKsJMkgp'
        b'JXuUnNmWtO0sT2GBhielZLFStxmsRGORNtgg5QjjJNRx0A9aOei3oXoesc3xGiRvUWsP3edSa+R81OgeBNdQdAy38R3Dc3RM5d2H89CEqmVqBfsi8TqylQtbFl6n0eeQ'
        b'bSPw7sSCvGR6BIx+CSChSoGv4qPxQbtNPq9jJ92AbNttEvhNiH0mUCbI/Z8JVEjXSvbJQPFaJagENTyr9vBWTvw8YFmIECZooCyUBa7lhXBBC6Vh7Aka1UNdphEjepSF'
        b'C70ZkYv29m6HuXk2UKJ9W2HywLVM/fQpLTUyNwwjRzeUjXwljVUgE/yag5yJ794Q/5d54bK6VjDb6efbhrY3OVJoxsD9DafPSyOGY7uovkrUvjraEyi6+bpe5vekkr4n'
        b'N6ATOD0/FV/VIz1ki9+a1ym0Hn+3TZKDhnLdQvP4oPW0vmHd19fYaX1BXmY+9w3f1PIODV3Iw7uumK72rQHcoqtp6Eimv8V3IwBmBx7JyEtLANT2/FCCygjy/wU/3Pnt'
        b'PZR4om+RBzlvFaA25ydnlAsAS4cFmPPWEplzrHS4QMau6ZV8icwxyaUQt7Egr1ysou5/nM/1SVbwOClQSq2moQPK22IxjGrXylHBjwu1FvGwvHgogcWH8R3RYwQepJkW'
        b'36IUv9Y+gl6NpAnzCqHzA9yorg60Yd9phLAAEOzRLlysZGZB2O0XbaRQXRr2vwNfZcMLz3eOO6ES7vhRNnAmO+IN/RDikYC5jOsMWEcpyu9NHc3WiEiz69EM1MBJKCsr'
        b'CJJW/S/QMxKUXj6tocdCqBDyLL+U+n9v8vmc06/2+Tzv6LfrvJyrwxqD5Hlfq5VoVVJnrXbVusx2IEF0W8g5BS4oVa+trptCP4/hdFd3Id4o2HvPfduYsKcK9Nr2ok2b'
        b'IwxDlDYcaZMCmFCQyEmj70j2SwbdxD0ZAg+tkUkDDhxXKX4HUC2j7iDU3YPFKaAfVSX7gQfjI0aRDbfxYNJKmgwAawa5pMojl8lzQaw4Rvrv3M4FsWKYWPYrO6Iok1GH'
        b'D+ruQT/6J4RSRks/7ydoKWMVeh3RltEv9SqA6UYJvYHRKtjBWzUNgeWJ8sRZVUK00AfKlRaVECP0lb7uqxJi6TUNkcXcQlRCf5YfwPKhkB/I8oNYPgzyg1lex/IayA9h'
        b'+aEsHw75YSw/nOW1kB/B8iNZPkJskVUmjBLioS2RFpUVWSIb0HauLBLuRUHr9UIC3OkFPeGERMEA11HsOklIhuvewkQpwBeNMNL2eUQt9DOS9bS3J9rTxxPj6euJtfZh'
        b'AbdCyqL3qPbECKNbOCGdQoHRkLGQWzTIWB/6KUFhPNx7ksF5QpjAymOEMWwNT/JqKAb6HBW8XJGXK9QrvPysaV4+e6aXn1kC/0u9/PQsr2zarAKvbEZurlc2a1qRV5Zd'
        b'AldZxZBMz8r0ygoK4aooDx4pLoSkZCa9UZbLvMjgjewivdbLT5vl5WfkOkZTesZnQ91ZxV4+L9vLFxR6+aI8L18M/0tmOsazB6aXwQNzoDHZ/gXvC3nO/BGkDwmI8brk'
        b'/oDn8i4DnvvIeRB+dgzgLy9wZyEWJOCiO2wZuVYSXuciTYXJpCWfhhv1BxmdzUJ7JmezY4x5huz82VmwEHLo8U/6tdIpZGMEvlE0zqb8zcvISfepYn4+83PTZ6bXP46P'
        b'ijdnme1We7nB/Eb5Z6bF9BOobyB0b7olV3n4lbV6mfhRpkdTyPawFNyIzxmyfEcpe5F7MnxpopodpOyNL9IYAYVkK4ClX2A+THaSrfwK/PwqVkONM1X6GPIgfN//PWT6'
        b'NeSL+IhIGnqyO8z7CLL/QKX4O4F6FK6KDsSh4G8MK9p2px1/oUnn35qQiU8M9z/mh3ydUiZ6NBatD/r9aVAI/05bUKGWZpiCC/5apZohTaj01W5xlYlRfdq+VqluDAFE'
        b'CgFEUjNECmGIpF4b0tkXvOWos7C3/QtYWNkccisl1xdrEJAmKSmZxqZlwV3pzM4pWhSxHG/KwmdliGyvCyM78UlywU3pPdmTQZ5rexfwqzBprnR2O4e0AP3dkTsvnjTN'
        b'U4N2JEf4IH6I7+IrYeH2ZewE+TNKJdKoMzikM9n/PrYOuWkDl+Jb6fQEOZeBOHaC/CkxJm5EcQiKnL9JhUwm+2rlNOSmkixprokOiksbfJBchTdCFQtKVCt1C1h8liRH'
        b'cW52fq6BtOi5kHEorIAnp1OJx61D9ED5biExi544J7vxRfuY1FS8yZSLhuKbMvziLHJWDIS7mxzHLyQW0CPILflzAk6rxycnxZPGlITsfG4Kvo5q9WrSWk5uszC41eTq'
        b'slzSnJ2XokTKvvhFLa+NzWcNSijFWxPpMCfBHXwP3yB3+fGra91TaefOxS1PFKegMzCz42HFbGNB1YvixQbhzVkyNAhvDse3XeQEA4A3kxfwOecycl2eFoM4fBCRHRZ8'
        b'ngX5j11ILgV+qrEOniqNh4lrNpCbFgP92iINiS8e0W8LR0lOyjRkhzOMBerFV/D1fF/4eLI1L0mJTxlR71kycnQ+NIGGpsJN2QVtI5bkC9q/GT/C50oD+kPh8Hgrj/BN'
        b'/ChsHDlaykIK4I14zxCyezZcDum1CuWT58k29xDILajGF4C7X1u+jNzATcvJdZeS3Ma7UXh/HlDtGn7kpp+deGpGnBNuzaWfC4jPSYKpByLIYBVLo1aP79B2Kenk3glF'
        b'NfiMmxJv7EnNTKSDQb/3l0J2lMTHA5FrTCmYE/ClgHnkDsLr8bkQRO7Pc1OagI9E421h5Ba54SS3l+KW5Q7NUnILZvMB6jtGhjcNx/tYOCF4ayduJc30S3tJyTC8isH4'
        b'MorCe2X4chrZxHB+mVqO1FN/zqGpJkPcnCzkpi79+HJdjJN+OnKImn08cvZa2979sZyTfqLptSOfzSnOLiBTI7+Iq23640XB+fZXyjfrN/6WHO/z8vyhzw4con1zc6/i'
        b'Wb+P/DLy2Mu9V6BRP3xz6B+Kx/zu6Tm/m3zrFzNCFhxdPu/lH55fPuKH8bn/I5xaMO/a/vdyhQEfnvh92rWvjvcu//VnLaPcX14sT3H/9dyKV29Hl/xDfSrl3fUJ7gPr'
        b'ml6rOd867458wPAb9R96D/3wk1+0/mDA4brnIi6VXZj2h/fqLuTecSbuWTrxSMPtX0UdPnQq37D0+ISc+PDrg+t65U74tedPp98MvxDz6JPer9449UXEkY/furD5/2Pv'
        b'PcCivLL/8XcKdegCdh3FwtCxi2IBkT5IsxfK0BRpM4NdQUEEBATpghUVFQSlKqDJPcluYkzvbnovpmyym2RN+98yMwwwoMnufp/f8382RBi473t7Oefccz4fF+n7yZGZ'
        b'O2blH9ePeyXO7K3OnLfcQ99fq0z7OOVM+OR/Sua4b0wXfH/f7Xz3U05PbprrUDV9q2f6j/d+2/yzxPTldtn6j22tnr3numRNwpmsiffn+N3pLtx3dmxvdl/Biy1prS9/'
        b'OO+JQtOSJXaSf+b/9Ni1xPcWHnLvsRi9M7+l/cNNnlU7f434oGiBVfXfmjcffWbNYyeKnH7Ti5gRZB5x6nfB9IX59+q7JHb0lBu/CRWJtM7AsO2qU3BVCk2fA6UT8YpS'
        b'kTGhGktOhFr4cB6Vzqbg0KieMJ4yRAJUjvIH8N7AYailZ2W45W5UuGMidJiZGmdAhxw6Fab6nHW6IDwdLlFKpiRUjOoCQ5x5ZugmxfvZBHkUfEECtaNV7AxWfBU/A9Tt'
        b'Vh3icIIU74TFBgkc8ROORsdw/a7y4ZzFcoreFDNqByo0z4TONOhQ4iJF42NG8xNRN8qmeBHoyBpbLdbNHvyq81YHihexOQTqKPWDHWRp2B8I9QOqM2AYToehyz7QJVgf'
        b'byLtHH8XbzGqSWBQEyfQyXS88grwTnFUAD04WbiQh9d0HZxgrx5CZ+AM5Z9azWcMVFnGCqoLtKLjC+WZJulK6DJHBeiouaGpMbSaZ+KlCJ070nETgpeiXKE+upG4idFa'
        b'5kWibkdnKApy53H666AezvCgaaaC4k+Fo5sRUOiHmrkgG46/j7fSzI7iaWzC22o2KgxBnavxXtbkF4zwaedCYM7HoQ7hDtQDJawl1+ONKLkF4dQsDDJI8OZEywiTRw66'
        b'SeEvcE/egsNqAk8RlLLNgLMNEpru0qcDuCUKtaFCVzLH9Dj9KLtV/KnoNJTR17dDDuTiRNX+qoeb38mJQvhQAX2oVEEiHOEUugBHVYxgIeRUxhsOPi31fVE9NxnOC6Et'
        b'GlroXLWLZzyd/dRhmaie8GzGbVAxgMItPDYErKsoCHeWPwdZ/NELJ1CYcLhtg66TtxOCcAHSoBBK1crjxkGdMN1qC+0OPVS7iBB9ag4TM1y7q+GCYGhZSKfbNrjNI4Qf'
        b'zliYCBRI4CCejQV8uGi/i3ZFCmpMR4UBqCYkwMkfn+2c4QJ+jHM6w80q24rXCElA+agSitERFe2pP56cDvZ6kI1qzemSWwFHIvGTUieU76ra1PWi4TLujC49PZSjIklD'
        b'9Vv1aVXU2Cz4VCE79FUBnpln4KhiPnnoJNwOJQtkgBiOK1DiOlAPdcTnS5Hd5PXG6BS6sUxB2IOhcwU+wnW+iy7BkSCJPpaXs7ggzgBdh97tCoJ0PttuuS722YjRjH+2'
        b'n312LGTTtsYICN47mR844264oHpJH6u+Ari9DG7rlrH/83Sq1ERAZfWUobK6pzHPkDCo8oW8MQTZFP+05Y3hm/CETN8nXpp8awqePY5AduHPJAjPhG+M9zQiZ/f7hJJ7'
        b'MX2t36hR2GaQDM6swUwNMFaFMKmdhoXEbpZBZnQGYUK9J4qNVmj8f/XlsYlx2+MGg60YPBriWQhPlWlGKPlGM6EFhZFfqVlmFU+7v7qG0TCeGUDKqrt1jwoWb7CFtWkk'
        b'uFWNvXtgUY9s6FbdRYePbJh+oLkQtqf8JeogB1Y/sQoHZRDn66O5varaKtqiclfaMiInzq+aijjpcnFKkvfX7c9wsJLr4RFKJwobK31SBPVtIp5Nf4pyNkc9wrFKRWp8'
        b'/AhlCjRlUp5T/LwzfkFMvO37faxIPah/8p9hGH2IH4K+pgIO1A8hKV7leLCdOHrgHo9LIbEisj/FuWuyRWsNj1AJI00lqBcU8YBIIEhwGhfBPzHYspHbbaIpcubwSMYD'
        b'C1aVSzdTDeofscdq0OGZkYAjsSv7eLv199LrdwIAzOP2c/t5uowEA7BbNEYCw35ztkC7NCdaWjzvEclbCZGfkqcDWZD8N4AoaKAvhVwsT0xVJssoj2tcBsUTF0cnRBMP'
        b'DJ15adiWvJPjookvkngFDTohg6jCwqUOfCpocJUnT5JuLF0VanhUVESGMi4qirHMxokdtqWmKFJjCfOsgzg5KSYjGmdOvLXUqLvDUgAqhqxmAo2vutZn0IPMC2yXlnPV'
        b'w+HTo6JWRifLcQ2Hgv7ReClO6z/ekCEWSJNe/8ckPTkRq7+rkH0Z9ZSpV4whtfgZFvC6nreT8Jiecg0616klCSxFYJ1HS5BAXQvVNy6D7niE8QlxDPSMUlweGPQ1afe0'
        b'AUeKPDZ5C+3b/isMksFwpLA8NbZmP5gZwcy3EKpurQedm1ncdyZaJyclfpoqihKpRDDUMVMlhUGpo7qhpJVYLCaYtPkhRE9CnXA8kGhaWNmALlM3dG3xf4hMVo2I9nAb'
        b'8GI2Il1wc7A4SOwr+UEOAU7ocgS1GY0ZTWzB+SFBlBnqCsoXLfSyS3Jx3seTE5NW0fz3voxysfo86m7Me9H2VpLoIGr7vR/1U9lnUSnx96MKEgKi8XwIMuBO9BhOMRJK'
        b'BAqC7TQV8tFtXbLoAEl0dzCWRbegq0xC794L+ZQICVe9VwcCL5xBlQpCzwd9SxdozTX1REO96DqebFgsvvhI9mE8+eSqyWera/JNoeSuD5+AOBN1ef2Y/SPSvPY/Rudk'
        b'FJ6T44adk59p24uV3viJ9XDWTj0poWj/o05KRymZlNfGmy6ePEvCp7bHiagpEU9WVBKEk4TmPHQRbk2npkE4B+2oFL8DHdBLEmfzUNvoaUm/B30upIyttZ95b0vwiw3C'
        b'M2Lr+41xiQmJCckJAbHSaGk077ux28ZsHRO+9lM3vdlpFwTck44PrhhFra5T32Zqm8+HHR0jTV8PP0S2JsYWwt22uodIXdrwQ6EdhI7HwHzYMfjeQluiHqa8/wCX+SMu'
        b'cbwrX01P0JMThNDuy9O+jFpQ8xleoYmqu5hR3/GfeDIb78zEhA+dhr5YjbRxe0QlFKugYejmkJEa5FYx/JZtP+RKg/pXDLNDD0fbTcqYMuxwvG820hXKQH+OPyuZcOob'
        b'e+2hGHpACqURSbfLt/Dk5M9vvPxVYLTJ5NV0FIQSnsNTjf1S3VA/g1PcSB3pOERzY84jj37WkfynDduJ75iMpCUOct78d3ox/pEm9OOvN3ByYnV8EA+O0YTU/m7M1ng6'
        b'peuO4ONF/JXgZFQbPl4oiOvNfegyFDoR440QnUPly3ioYxmqUxDfSGjAm9flRzG7QFWgZtLDaUeGON/sMtqR2lvhMJx01ucMoYePSj32DTOIpiOuBpeh6jfzWX3kQST5'
        b'zxx2EP824iCqyiLVG3ClOEE9ADEcvVIkF/YmVD9QX9nz8yypbDLg4j5PL28svWoclzc+b0L8BM11o2jE68YBGxpx47IeMv6zpOw25+TKLewqbGwAuQzjm7kYsHuTXHQL'
        b'skQZ0IEO44HvMCd3J+ROh7NADXy4GYPa6G1SABxaSi90/PAAhqCm4W51NkEVu9WBwztFqAMd1KOHXhi0Gcihk0MHoRzPo2McOgp1UEzrtmt2OrQp9Xegg8RoyqHScVBE'
        b'z1APN9Qjgk49OLgcp3Rw6EwU5NJXFsI5dF2u4KUG4IQjHDo8EfXQW5qlB+CMSC6cPonwgXKoevMu+vwKuL1DvoOPrmPRAMo4VKBADfSq562x+pzTiskcJ44y+ecyN05J'
        b'eRXy4Tq6QO64hKgKEe7kcxyqhNvpSmp67IPsQNoVg3oAWhUZ0B7u50js5yGZ7G7rGKo22ocuwRXaDWtR88LZqMcSjs12E3I83FrIguz9SmKW3LYLnRlwqYp/UPCU0FVr'
        b'oGJ2QLgBB5XWkVCtTwSHEKUlqUspujyduP+4r4OLnLtiPb3L3QNnFUD8u1xHoSucK2pA2bSxiQo97olE/N6yqOR1K/04JeHh3Qa1GYGaouBcGhzxowzfRa4BkfaQj6sR'
        b'bi+BkjV+/kT2ORpMhZ4w0jj9FNNN0JJEScLhOLqWQDwgtJ8jk4VISq4hqi7yc3EONdVcFZNZcgX1mODePrZLSVyuraFwsSl+o9QUZYnWuxnqQVYknNSH4gjTlVbjDBeH'
        b'oR7c/SehxSdhp1H86HRj6NXfYYgKjEJMUCscggY36NsjmQxHFrlArT6q8pagtiVzoGYM4T11UhJfbCjDUz5fD9Xsg2zINuXcDQWoNRJdXw8V+igf8lCFA8qBPihBxRHj'
        b'k/ajRsgaj/q2Th2PutBR/Gpn/B7IEbjb41oUTYZrK0YFy7FUTDYC2scbIsfzXnFLFXIWUZv2SOI4unhMgXpkDCGR1brbHANHtHhkr0KXKBZOwxma55rp/vjwn87joqIC'
        b'5hrbcsow/MdQvFpv6uE21BhxYhNiZa+G5tWbt6Ey1IS1kzM8d7zWzi+ajcfkeBTqgCaojZwJ59bjemfZRKCDcehIAi6h2yAR9Vrswr1aTGe3FM+WUl1V9XMO0LNCNRY2'
        b'xJEFXZLg//E6gitGWBm6JIqQ8Oj1qi9WSZvINEAlU+CEKxT7O+FtAQ/0aEOh2/zltDeUU3YHDuLEpYy4J1DWcKy4BRKTpB24hkSzC8KD0Dz8DbFTippNnl0QT0FXcd3o'
        b'nXwpPnfKiChP9DHI4qNinvdCJyXx/tiHzkY4Qr27H6790WDmkuEa4O8cxpwxhjgB+GEtL43sAavCnFfzuV0R5rugx4wOzF7aCHID4h+q8spQaYh+QSHb9GhzXUINM6Ez'
        b'1C8gWOrkLKVeH2TFaTwC6AYMR8Ms0Xl0dRGdBHXj+VxdCnFZiQpaaWaDjzIlPa9PLwgOVF3b4AO1lb8VFaMjnjIl8Xm19FsXHiJxghPBjE8kco0ORxMOz/rLuOvzURkc'
        b'3SjGmmo3avCbgm77TZmNWoQcXIdsPPDT51PHg7BkPOht0GZuZAjXzaFNka7k4WVb7SUXhKyVse3zPNxUhk9BJ8muJcC7XBOH538+Ok99RxQCqA6UOFNtWYqrZD9QcBBw'
        b'S1DfJrEhOjhqGyUPQnVmqCUcFUVAEWEO0nPgYfX3MqrF0+4oG9YKOB8tyjTjkQHu4kEl3lTsoYLyCo13Gwtt4/yIU0CbAceHZp6zBZyWWNJtMhBOpEJhEM8PXeB4Czgo'
        b'tnRnvhVXsH7XHRgkReegXH1hJlrPh6tYBc6m+aYuyYDCKab0cld9tduWRg8tNzjvSC9I8QnoSm5I8UwtoxVNwGfKVSjc6BzI0Pgn8dBZVOFIGZTEqDeFTJpteO8pcpSg'
        b'y0LOxEJgg6pn01iHdEPIx1NeQnV3gsfPri31uMmQNwNl6cWjwwqKvHVgM5zX7OaE3rmab5SMe+gi1NHpkjkZzjraO0MDus7u3ziTBIH57ghadVS6B2oCZev9NRwEW1A5'
        b'TRmrHwWFzlIoCRo1kcfpb+LboJvbaUp6MODtwgdO0ktY4TweumQ4j+m5VaiHC0RdcNqZJuHmnoPj82n/maZb4eVbsce5n6D6GrrJBJKL0IXOOdIljff0HlcpnrvE80MP'
        b'L+Xjekbo8mZ6XFroEdbmZAOmh6N8V13dI0XZBnAMT8g+2noLfER0krtxCd6RjBbywwkZ9lJ0WaJPawVHY6GYSClroFAlpEyHLJZ0PX42EVJQHZxVSSnJ0M7aWQ+tu6iY'
        b'cihdJabgml2hU0y2yoZIKahIJaZEQz6VR/ahAgMspjiiZpWcAic2s3IO4h39FhZV4BK5tqeyis/+5J9+//13s7VCbm+0LT2939psz9E/rk/Q4+6usaB/zFwo4ZLCZ/5T'
        b'KN+Nj6OPk3p8wm+kjHe3mH4jb/WVTRsqpzd/ZLdEvnBNlUPulV+WhQmz3996+qDI/i8B0+f7NHLnvLIKxJFfiN89Nuvd90OeMmi4a9chNXZJeKd3F4zN2NWQWzltJrq8'
        b'Pq3x1eTld47MuuryCU9v8Uvvr1r7L/+X2tajQkXQwZee3+q0Ve+3A65ud4Rxq5yzOpueeiI5hm93pt2twOP8A7f5vNzzd1Z0ZGXGHyya5etk33Xd+tX5722YMPenarv6'
        b'tZf+1r49bmLY6zlxvZWRiV71Ya8H7C6+afljkHCRM3xh+y/PUe98/oXZ6tc+WuGxw+M5/W2v+4x/x2x07197RsXZnG258dfc10Xv3ZD8w/NKd5iy16k7LubirJ6Vsvem'
        b'vmz5VxfB/R83vuJuWvXknIboiSfWfrr6M2fHrW51Rb8UfxjzboTkjsWubYlFeytOhl+85ntb8Pb3ifrf2I598/Ybrk/8MN/dPl6xLM/x45D78WnP+2bsPLDgVGqVcwJv'
        b'6Qe9n+9q6NkWuSnl68vXrH+o6m3eUWe6sqR4zWPxVU8tTn9jxo7ajC3fvHSpIiytdsqeH2xnB93YVn/wE2fp6198Uvvc6Rcvfl+x/sLLtxKOen5oZ77wSZOwkg7PH3LD'
        b'PR/b+3V1vnfC0k+8b37zfI95M+qbf9fr7V8aDP7xQt8oF7eW7pQa2w/s3mr/7telW3dPgN+/+sGjZtKccbF73SMnnf5giWfnS4eVH/T02b/q0Sj1f2V78Wc+W5zOJR2s'
        b'NXhgceQjLtLrgP78U6veBQ/k8clTTzy1NyHtmVGJb22MrvospiEkCNVk7UySf/17fexur5A1ffd8pB1zdr6t/KvitcfvOzq6hU9647EpD+4u2OAf7VG8rWwNUjY+H/zM'
        b's283pK7Y8/fRKz34oXc8JNOpzwGURuPlRXww0Bl/lRsGc8KIn0uJsqBr92pqzk20I34zZuggdf2A1jDUwXbQKCuygaatYx4bZwMTiLsO6pzezyHCvHVuoRtUeV2HGier'
        b'Xd70OEPUwYf21MxUG+riEAZHA4jXZPuoAXt6PMqhLg6b4BA6C4WbA7Q39ei9zJvkCtZkuqg3UUQU89BgzkQp0M14Zs7vXc1U213TGO8J6oVapvVWorJJjg4uEijA2r3R'
        b'Ov48dAidn4aO0ErFYoW6xZEQ6+U7odYVeG9FxXxnfJAdZH1I5LbzlKcmCS5oqGoEyehIHHUyQcc8dlFqMyxwhWBx7li/8K3PTQ4UYmnvBpRT352wKUpHWouMORwupomP'
        b'RUMP5tVTJAihzkTrvFUkOehYIjU2z13iL0dFhummcF1OvP0GOPVA1kbm1wMd+ujWdOhh7huFUAZ1jgNNyGIotPIXoNOoLpE9dBW1zgtU265D2HFZtMkS8gRYMexZRPtm'
        b'3Qrq84LH2TnBh9IgGnDmIYJE793UacZoFKp2DHFyHIfVrUKaKIJbfHx4lJnR1+FqACocIBrBrT3oCDQnU78tqILm7YFTVvcfdqa7ad2wcNEYq+1ZxuHTspL5lqFrUElH'
        b'NQyfMUdUDjkoF64Qpxz+6EXQwDxMavErVcROMhqVDOtlwjxMUKOYejbhiXACXSbrZZBfk/kU6tl0GNqZW1EeVthLmMNNv7MNHHTS8rfJZU49DjOB8OkFOCpmq7jxzCFL'
        b'kDoG15Iki3BLsRSN58pMyGK0eqIUPpzwmMUsQSdRJ3FqRz0u/ce0JXSyxCwowId2IcrapSXNJHnTkYHj64VEmMHHd6G2NOOHqmkTDPEZd1SnOAM90MzkmRZ7ugB4e8Jx'
        b'DZ2hdaWWZ5MtHBZazfehRljUY+fMDFJw5VGtsLy1zIeuGTX5BAb584jnaxU/jOeAFZuTtHkr9sFFDVsfoeozQ1d2bUZdEpN/xylHMuG/iPr6b7gI3TMfBHlJrW4vcNxQ'
        b'q9ssYh82pHw1FpQjyYqAuvEZnJuxCthtHE4nqcR6RmDjCEq5EH8WqqiTzdg/vr4qB0PqUmRFGQMt+MYCaxXJMgOLM8QpZvQncVQyw3kT9yRjPgk2Zl/9iLZ8nAOf/mRf'
        b'JKCY8OuYqPJiwYMaO96gZmv7JTGfIRocNop8G01dkuJ2atwZtGKt+q2MNv9no6f2arLShH2RGlKmIFapURrXJmrsjMG/Ogxr7HzDawAH4kidJOHRUDPpCFev5PKVR8F7'
        b'H371KqBmbOH7b/J1uCksj1cQnsPo5GQKTapFG4wrlURqE508ALGUgVvJZAy7L1qcErdjSKbMvcU+KmrVdoV/SnxUlDgmOTV2m8RFhS6rdnxQyuPilcnE+2BXqlK8I5qR'
        b'L8qSCF/iUEpj7UokpdAH42lsviqeM07OgjwZnqCYoCSJk2TyR6c2JJACHmJ/6oCA5588iSC44nKIM0K0OFYpV6RuZ9lqmuYvi4qSEMCZYX02cP+o+4N8TEoRZ853IUzZ'
        b'Xrgbd5DOVCRGKzS17XcL0Zmjqm0UVpZ6MDHnC5wBAZkd0EXqcNmEjFRlGoWb05kjbroiKVaZHJ3B3EtU7PYMKUEutieB6k64C3CxFMBkVxr+NU4R6yKhgzCMewnpUEWc'
        b'elxU406dy1IGc1iqRl+WSoN10wggsa48BwzACByQ6mDWgTZ6IynV/dBZW9SIxWR00U4VssI3UyyiSjHUoqOpA6IbUlAfC3Cg0Q1YXFCGkOfOwOU0PWbYFBsKiPX0Zrob'
        b'lI+b5Ddqevo+aAlDuagBa+bN3qh8g5e/Ap/hZ1CroafUaSLU4bfrVqCeybvRZQs3dAZKqOHpiqcfd4x7ao8wKiqgTDqHUxKXAgsoC4NCLKCEE7LeEhIlQ8KODLipWIM9'
        b'vFVI7Lp76etPbxByhpz9NJNlUSa9vh5c0vuGVkJ5Bk55ozF3+p1rpjnLTPReTP3m+gTrZZZzlnmNttjkFVN/zP8FL0MjadDr4k3zdo9LyC17wfwvM3PMnSQ/PnfnxtuH'
        b'crpiBOcKJ2z4Zrno0LtnZzibzp+w6x+vF01zcS/52bfg9xv79Z4L/3jCmY4Gs6OXbE0aPzFY8OW4kwaxEhEVfEwU0KpyDvdYrKWX6K9lesmlKb5jCc2hisB3tYfCg/4Z'
        b'esl7D7n8qkYDhQ1UH0jdtD3RhZBgZzkx8jrbq21dlnBMgKWkK1gHIVKlhXeKlvoCnWuwBpOJu1alSTRhabHV0Xkq1gpUTvM8aHKA01R/gQszcO2OQh5zm6dO8wvRNeY/'
        b'3kTq54w1iDP9RJiQnUQrhgqiULEIelHTAHZGpln17KXCqakZ3Ibj6KIO8ZQIp7jQDuppsgm1bVX5gjeh87p8waHTRX0X9zAnEiMSsUcXKZVH7HXJIwe4BUSGILIFljEE'
        b'RO4gEscgRwJNRgOZG20HHt463ElsBx6icfjXc+QQFes6RLO4d62Gd2bQ1IE4huKzZQs+XDRoBeoQ1uFcCgVHBMMGsKod/X4S6jhBw+NSVGiiA/HLlXJ2osbRPQ1vwD5e'
        b'/t7hWpjkwx1DcTFJsfItsclJOBfGsqvGaYonuIqxiS70CRcf8t2bPjYc1LlWrqr+8KBOiU4ar0SCvyuPo9VMzZCRP+ANXucGrIJuH7YOLisjg6IoNpsyLTk1WqZuvbpD'
        b'dGZKQD41WGvkbFB55MqVSQoGoK6plO5j4aG18vaOiHL6s69G/ulX/Vf92VeXr13/p0tdseLPv+r1Z19d6zPrz786O0o8jPD0CC/PGcYv1D+esb0wUSZO5iR2UE1/hwHO'
        b'pQO9X6lPnG7ZYzif1pUZ0RTKun8O/xH31TVEWmW7QuZsF7cBq4W63TIIWbaccIGZSdF/rqe8IiJ1VKGfhZvsMawebLklyUYQsIScrphrW0ayXWKiz5lw0/jksn/mBDsW'
        b'+GyFpajtK+QiPrlLI8HSx1SW+LrdMmhzc3PT4+BoHN+f2ENOKpkzRTbcQD079zpKXbCEgCp5gUoHmrDFFMogL91RGsDHfz/IW4Dyo9gd1XEzdBJLVLWOUn/yyhHeYrgK'
        b'vRIhvZZAXY7oNL1Ug+u4tKopgnE8T7gxjyVWWcfitFYFdOFKFaBuPlTwptgzL0PvJHQaHUbn5bMy+BwvFeeUrrpsghxUiPLl0GmOj66oeD5c4DlA02LaZDHkjqL+AVCP'
        b'Ol0514momN3/VE7ztoMecgOiuv6wghOsEuegZmd/DetQE6niAStaVJo3atHUEFWk0Qqu2EfvAp2hD/JUtUC16AitB8qC20ziPQG55AKmpL/+IqiidYEmOJwhyjTCgxiE'
        b'OgVGPFc4FMf68go6inpEphnmeHTRcYETbynchEss7SRciMR1aReR68DL8QITnFgdrNxAciyFbqgJJHJqOIVpILfHWHDl4Cwq24vzLMWy8VHcb72oHNVF4F/KscDXQKyZ'
        b'UI56rfSgIkbPFH8LRrlwdLF4FBbwrMxRYwRqlPDZXWwtFn7rNN20CB0mvbQpmCYujFjc30lNrrSToBDaJQLW9xXmCzRv7kwjL87woi/6ykL6x79tDX0RXULMEQa1Rsey'
        b'XoIbUEW6SRybZKEM5csJZMKnSnHkC55ScLM2+PbHky/Pya680JzzxF+ekHT72Jp9W/74yklO+vp5Z1ZPb3N3y+DMsquraxZyF6M+ONXg7ej6/O0fpy9qm/5MwJ09N86e'
        b'vG5/w2Gjb1j6d07rDj4v8yma/fi27Nkvh32amju3Zntp96dPvb/ZcRH0HX3LKMji+VH/1O+LLE8sa//o9sVL7794YMply31msxUf3vm24I6H/IPKlRvEP5stWnR9+n1B'
        b'5pKaA+OUhV9vWVH47aG3vlsV8sMHq5TzVzfX9a766VBL8Yx5q8xM2xe+bdqXfTWkyzv1zAn/yZ03J72zWGan/KTM6pvsb76tcn717aX3LNcVf7JRYk2NhhtRL7QFopux'
        b'/fGO1NSPylAXlaShB+WgblVwLseTMmM/6ttAUyPgOOQ7+oRreVSbOAkMwm2pdrBRugXn1KbRDmbZMYPodciFakcWLDrRQIhyeHDIF11nZvx6OLFHE1dLYk/LWFxtG9yg'
        b'FtMNqXAKalDewMuLTLxQmqjGgmrmQq0vOudIXGeILG0IhXyUjU7OZ7L/KdQ2BQ7DebkIOngcDwo5aNQzZ7L/NWhzRs2bUGHaXLzGIA+vbJQH1dQIjm4ZLVoxjiTp4yS8'
        b'FEoj9eiVgMI8A+uceSSF5JfPQdm6/QrV7XgBXFRFq6KbqFQVsUrCVWNcmWH1vDgG3ZooJ3fyPHSBgxOoATWpGOlFlrj5R+R4vR0h1TnGQbv3bvbaRbi0zwCu4Pf08HsX'
        b'8T4zDb9GkgLw4qxd54s3EhOsRKOrpEcr0thbvYsn+OEdJDOdFFaNN2u8SR6jSaG4nmccUQNOw0WhSrJ9Vu+gSg9/1hKVKoaKpYO0sRy8oHUHZ47gUy2UY0mb6imrdesp'
        b'UUQzIfZLwvRNrKfMDsqn+or6y4QGThrz1fZKzT+s3xjydlsOdI/GJUrVkCo0ltJEWzrPiB+o3vDUbUjSKDXxmqBHQuPz+AiazeMD3LSH1gPnzudUNHBSyehBMFX3hFtC'
        b'/KX3RFu8I8PCfKTe/j7hDI9TA191T5QWnZSiioikYZn3jPtDBlUBnOThQVGc0QNhrijqFTF1UlWNtop10Lj/l+ztGa5EjxSogOkMDSwEZOzNBGZ6Y5bx8adHBsvkW1iY'
        b'8M0I75pw3k5DnvVEQx7FVPGGcplooJmCBs3kjfMVJq1GrQN8hk1UP+UOvIEkbDK+zEXmKnOTGdYJZUYy93hONot+Fslmx3P4N/LZlOBKyeap/j6fUILRz5aEFEy2mH62'
        b'lnkSSjD62Ua2TLZc5kU/28pGy8bIxtaJCL1bnn48TzZONj7HkMBulhuU82Te5SblhuVW5Es2ochAtiKPYHzpY61YLJtCMasMKG2aHcXfmk5o38h75aJyfjwfvzUK/7Mo'
        b't0piv1nh3KzKjcqN44UyH5kE57eS4IeRHPOM8kzzrPKs4w1lDjJHmrMRddLVp067lvH6MieZc44hgfkUcutFVOP2vWdFloE35YOgeG3xcRkPZg2QTYc+oGI1037ogQsW'
        b'dD2S5KkecoWM/pzl5jZrlgeRlz12ymUeZGm4uLm5439YEp99TygNCQu+J/Tz9/W7J4wM8111j7/C554RKWxLiDRoHd69DDiKLUc003tGjLgjCX/Ui8f6tfyPFOhOC/SX'
        b'hkf8wbcW3hOGr1i9/IFXokKR5uHqumPHDhd50k5nogdkkGhW51hVrKBLbOp2V1mc66BSXbC24DbLBedMob8yfMmmYBQU4r08aAtWBx7MINXx9vKnZeOfq6J3ke0ojBiD'
        b'5QqciYvbHPw9Yy55zyTcX+ob5LPFa3mEt98jvur+YP6g57wzUuVyL6qGDHwlKDUhWJ5AX3QnL5oPasuDccNX8IGNzoZLRANyIQM/NNtBf1g4TF6D/7yQ/nnkWg2f5v7A'
        b'8Q/0xT0DWVx8tDJZQQeCDuV/J/ZBVwQJVQpiFOiECAsth6k8Qv0DsVZSmvRM+0w+DS755dTxwGga4BMdSINLdrw0QnDJPUNCkKrAE3f46Cny5ctQUQcufxf1u48eplCC'
        b'G+aJP8mn6j6as7gnB4QqjFSqxIAdpat0nKdh6kP1c+JkGiEdENegGSUS9U/jGjg1RycDSYs31sQsGA8bs8BY7ITvHzTQYar0Z7HBSbvjtAyWjG2H3R2R3XMEA2W4mj5X'
        b'nEY5EagoIfcY+qCzeNC6Etuv8JGM/BhZSw99YqHY3kGeRC6iMue7zHN4hCzZ8hTbe/s9/GHVoiUPO4kfVs7wC1ts7x/xh95wH+GNR90ESBaDKz2cLVhlz2KGHxa2reJZ'
        b'UiP9D/cmOe7Ya4OnTVpGUmpGkmIXw+a1dyAHKOGvIkeog27zoAM5WMkz5OxzILZgB3KeOUhc+u9K57nMcnHzUD2iO5v+a1U3+qgq1/4/z6N/ZlkP1zAGI6Fqmg6ICNY/'
        b'M+UUJWLY7qG3Dx4D4/7pItMN+KCK2x+2Tv3IDh4a+tah0A0ERkFzs67j4pz8h9Mo3R4xz1OzKL3Vj4tWkAklV1ORaeFgkHvlYcADiGkV57MjOkPlBKDFFEF7RxweF0fa'
        b'qkzWYjfTmZX38ggf35CwdVsI/U5IuM8Wwr8STmupuYBnnGvDdhLbhFj/UI4kFaSKetzUKpTKKKz7vrrfUEwvH1gO/XZch0F7isOwN/50hNLYOpUzxrZBW4wDa536kaQU'
        b'3cgGDCMDC5RqNtrE6BSxT2TYMAbvFHH4jiTF7riMZDpwihEqzzbEYdYSXjD+iujkXfTF4Xc4h+HnrArcgw1IP+YHmfmqIdHgf7C7p2FapGAODFrg3QPeHYDcMuyuRXMa'
        b'chmAu0clMMnV03dQvrrHREVi2F8uJY+MiUtOTUkgOY1gNCdyjOEQ6cmCSU+CODs4HgjF06AMjgk4Ppzj2cP1bdT6uG3Tpn58Tb40xQxubaeG3cA9qGw0ukIARVVwonAI'
        b'LjEAxg6UFY2V0+mGaegodOGvNpQv5Ewhhw+Fa3fRMHy4AY2oOlALVVQNcGrvIp/Xj8Q5AIUzWC+Az81Fh8wgB51i1UAVe+2pNdjLHot+xBiMGlE5g3O86WctMs2wm2WO'
        b'm+jEWxq0XkmgLqEINUzSwlbtr4ImcibN1DTMHvLD4dYae2dppL09FMBRVyhwIrCaDDfUmVjTqkbx4HjESmY/P7OaOCmjWooIqsIDRSW+9FrirDe5luCiHrePcupJ3MZR'
        b'kFczqLLRBgn1cwkIhnzcXNcwOBIU6icIQ1ddUT6JroMb6Pyu6Ry6LRRBNaoMUCEQwKl9qIO2fsFCVeu3baf2f3TaYxtuu9EiVdtR4YGksZWpfDkhvZ/ZEzu9qM8YLbPI'
        b'+XHe079Ou2Zzf5/dhsfj/dN5pbPj+I+Hj1k0eYb5Zyfnid6df/f+CvFPd1/MsowKPXPY+3h96OR/ffXEY0WZkogn1+88fbcwdGvDuCvtAZ4nXrzwvey8xDblPc+4790M'
        b'r7/80YV83596ar6+IvzpCavCnze19D7+pHj7vM/lngdjHae9XWj+cezFX4M3vRt+T3HRdbzXTOPnXU2uujpEREpMqWUvfC4UOro4M1+GBr4rynOLgosq+Di4oGD4xsR7'
        b'1Yn4ZxjYBXBmYQJ3dBpKqL3VAasArdrG1pNwnhhcd6JTNB3d3j9DCz4wPFXlIbIAyhQsyOcQKkPN0KcxA0PODGqpjUIHUW7/zBWuTaP+2nPRVQbWl4NyUKWo39NiLVSr'
        b'nS1Q82IGDnkkAp3ShgOMRFeYfRVOb6fuGDHmeKAHAAvu96XQgipcQdSTzuzOZejKUooFSYEgM8eroSA3w3Vqjk20R+eJGRyVpfU7vTuaMHeTGqwzleNi8Bo1HgftODmY'
        b't3Ir1NMeQN2QJ4FTcAVvDUG4C2J47qHLB4AOGP9bJjINap3HcPrVXiuescoZlRAXCKk5VUj/EcZhMz6fN2EYbUiF1CYd6vA5omI0kq/InwCZCx5RqeuY9FCl7g8Czult'
        b'IdLvCJhYRXpquDldxWn4kl0eQcIeChV3TxjutzzsnpCwod4TEmJUtTI60MmWubASj9Z7Bio27QGaqLn6oPLjNBH2TBc1UWmjpgy0O8883vwR4ujVOmmjLp10uUxGCfy0'
        b'mDtUZ7IOy55Gmhuq2saLPYis6RGlgTSJ0nHX76SSjTSQW8R3cqir6WBSQ8bcSzT8folXQTpOodIHHknTUsnIGnrbhylbjAeLvauDhTZaLo5PTo0mRgcxpVxVMUwO52gT'
        b'nTKA320wee1wtRiggehil1XE7WTitUJDyrqd+X0O48iJn0mSEdmwvyv6GfJYG8T2lKKdNI3KflPDVrq4uEyVDCO1MncJ6pQcTWaTFiGzJmfGRcmk6f50nflp3umnllRN'
        b'AZUr10CiSZ152If5rPQhNzE+W6SRwV4+YU5itZLDuDiHdf+iXsjDc7GmpjGv7BFy2KlLbxyG+HSE7Mh/GrWS9PBIWp8GBk41q3XmpmbU1qUginGv+IRJlwcNVQZ1Oy4/'
        b'ooKoZttiXaHhJCYTVjVvyLrAOnUcJZyOipKmppCdYgSP7p2K/tIpdy3po+hk4kVNNgjN1I3PSN2Ou0oWPYzrdbKS2eESkjLjUtQzHy9NGXH7sY9NTZEn4e4iOeGOS6J/'
        b'xb08bMVYNtrWC4l2M1UMzTFb42IVbD/QrS+FhyyY5+YuZhyyrD2kDk4qeFBVe6k5gaxNvCnqzCdemUHXGl3tjA12WKWRHUIe4nCVkqZmaifO6btwKcnJePFFZzBVjT2s'
        b'e2+Ry1Njk+ggaFTGtIxUQrhOehF3rWqw8UJg0153Z2pxHoqlWHmMTktLToqlDolEe6frSdvZXvfa8VYRvvezqpLzWWyPv0ucxOSUFtuHRIZJyGCQ01ps7+UjHWYdOmhF'
        b'D8yTODxCTIPGu2u5ZqsfRHs0kteoRnM11Km5Tmaa63gRUVxV6ik6DDmj+WZwPI7qXIbzDIjOJbZzjUpWSJI55vJVBh2Z6LZMS22dA+Urqaq7HhrGyaFTSmRSBl9TwjFH'
        b'q25USb23rsG1CUIVVsw2mwiq7G5GN73IRWy/prvVV63rylC7klCSLoCT+DcawnkpglB2RKggEQKdHVb7OQVEanNPYK2xC5Vpa70MZqbFxxIVzhvHmlEATVihoV5Q1mOZ'
        b'5mcZoiR+CYlWkP0HynKi2B9qPptQezGc0QBkSPQ5DzdraIXWGbSD5qCzUcQpaxaqZFolVE5Q7sIJs6ega4EUIcg5IIQo1fY0Dz3c27nG08eiS8b9auwyXL1TUAF1OPGs'
        b'FYlViECnZaEo32s/qsWa1RX8dQ7/PLxtJzqGLnjFbEYFXhlJoaFbN2dM34hqtiVacFDsOQHVjYeztFqb3MNF0JlmMo0wXPChl+dqEUtxYMIIFuKw9YL8sSh/GSqNQbkD'
        b'KpMLxwzhLJSTX8v2otwoc8gTc6gp1HIMOoNqmRNaJVabzhKvrNFwWchR37U6VK2UkbRq6IBcjYFBspqhBUWmeSxVKiPgWJqpOZRFqLpey/pAjA5kfNSAImpYHZSNGg2p'
        b'/5cZHLGFZjiGyijJSOIBj4FwTdADRwYBFpEXI+y1RxQ6UJ6pL+TIKSgK9KLG0YHazEZFqGkVnTY420CKboLn0nE9eQAqsMKzuwCOh2GFsQKPUQEPbqeb+nrCTWUwzmq/'
        b'LxwblFOpOc7Mrx8Xf/WAPFGuCJVbT4cLNugiOm9rI8D6aDCBQ7mJzis9cY5eqH2+DhQmPpwJ1oNyXFL7YjxGByEH9y914ENlMRzkhZmEoUvLaLAMyrbdFhgEuSEaa0+Q'
        b'vyTA2UUXZ4m6WqYD1wzusXqlFSpFXVBMZ9WazagHP0kxKUL9gv5wzujqXq3MwwKsUe+WCcyWdRw64fAaV20L0qQA6nVDaVns4DpqVhPpMBYddHGymkgHchWEZ5H8S/pC'
        b'1KAnP4MVrB9SngsO9Sx5xc2iY+IiaebxPuNXv/nYzGLuBxdfmFp/dYNRkdnTpT+sftrG+ri+KOnqM643Ji8ranzx1xxHyQ8zxSf7eC/ujH9nz/f3xz7j1dSYeLjDXha8'
        b'7LdjZ80O/8P5cugZh4PTfT65ciPsXOXvjoLX9MDji2sW461tNr5V+9yPk58uzvz58Nwbz/3j1JuraqbuOm2zbV79WOfeO41fX/CeaeFrc+Xq/clvzr18oPfHiA8Pb20+'
        b'+9vZ0lfbs54Z1fP+ou64lb9+G36n9cgXj6e2tF34/G7Dg3dX/Xrw8rMOvleuVit+t30q1Kvzm+s/jFl/+n7a5oOLnv5iqtNMz2lffb73+3efDvhsxiuml66uvBVbdfl+'
        b'36KgRZ8v4r924SnbJYt+qnt2iembVwMm1f3w1ie3jH7Z9cHLrzT+mPxp9Q/l1j//y+fd073VW7oP/m7+hN17IY+9/r2pwScLE/L/dmiPuzxywYVnGme+PD499kaHYm7l'
        b'jzP5LrVpDj95rwuY3rHT5dzkvgU/nGi78X3c171Pt8yBnw/06M9obkK7nli6/EDpjHNr3qj43LtW/vInT29JyHn5L/NMfza//Ns/DJ4Z1VIkOSSxpZaYeUYTAl1QSaDG'
        b'qERNSnjzZ7aqvLBobaoLTrQsmseHytGomzosLobbCoOgfkNVjTV9LX1aSqC2fyQ6jSoJxM1Z1MtsRzXQhTqZjyRqhwa1dQhdRmdZ3NDtGYQAcAdlRrkyeQA5Cmrxp4XI'
        b'oHZJPwkLAU1Ap9z5cH4f6qTOhEHoAtRqWcNcUa+JOvTomA1rXicupUZtqwtF51S+kTPRDdY5kBVE3S5RNlTocczxEnJRDnOcbJ+OOghOrj9qEnL60Ahnk/lT0WXoov6P'
        b'AYvQ0R2ohqFNUDqTw6upDW4UzuE4MbGhtqh+Vg5ig7OEIywO/5AbnIYmvOEOZfhQm+EOBtDM0CG4Ap1qtiYWDQ+X0VGBjQM0UyfNJNRLH3BCl+CEs5ATOvHwRtcczV6v'
        b'S0aN/VY8yEe3BCpGl+z1DMChYEmY2hwaC9Woge/mt57WMgmdDAgM8kf5LESNsJ5oQS25oW5911Uonw74Knzu3iITqQF3DwHfCsGChdkKgedkaGNephVQxdMQthiGkOgz'
        b'aPGjaX6ojfCyuAY7S3Ad8MzJ8uSLY3ZIDB85ntn8v+NqF6MGkTwynB3xALfEmGfCpyHrfBMeCXC34OsLDHlWFmY00JwErxOGDGMaeE64MMgnfVVAuoVgDH8M/kn+jaPh'
        b'7Rb4kzXPUM+MhKXxqZWSb8azprmTUHR9/u6pOuxrg+KsdRgnhzOUZVQN9PR89E7XDiKv0hFJriOI/BgxEk4bzmqZxX1nr223fISG6vYGItgO1KrH/Eu4eH2NX5DgYZj3'
        b'D6KGaAxhcSlYWZU/zHRH7QQq3YRoptFy8drgoBEUEALCaDtEAXGWUhnM3IRwJWmRRA4CvCtcYz8EoQKqfLGw2GxqszNCOZUKKUljB53q16FBfaxjySNPBV210gRLBvmo'
        b'ol862OFEBQM4t3ItERoULlCAmha6umTifTaAOJFP26w3Hy7NYjdUtUaoBReBv7USaMpJBLryKjTTxAxUtJVeApIbQGtUTC8BUXYaVaVWb+JzQnuyFUc5fbjUXaUVHZzG'
        b'n01QLjnOBN3iwUl8XNigKnb11rcQjtP4E1QpcOVcHXdSSd1oTIbIaCbKySCQcZew7qWPWmiCPBy6HSUOwXqcHioQ7uJBduJa2miLQIfAQKzrFOHzQ6rH6dvyTeLRFdYf'
        b'XTjzcCiaNEZIrhw5VILPkVwWpdGHKuaHM2w6dAi1M3w6m93s0qwXVQSw2BJUPJtdju1ir1XCMStNIMaUrTQOYwrk0cTd0B6nid5AOaiMRvC0TaL134gapokoFSNcN8ON'
        b'c9iK+mgll0OjUh2ssmcXjVW5gjoojtvEPZbhuF3lkVCfCUVQQaDvDEN40O4jYkHZXiXcBP+FeAuPkn6klDDsySTOjlshPozXU5SXQ8Yc9sdMBz/uWFQA/luUQ9L4WG4A'
        b'T7K+euqKORVPsi1eYNxWbi9Pxsl4ufyx3CE1Y3IiFh4/J2oBCWBdLssISkqJU3MmC5PJL0MRfPG3Tfoa4mQK+w9ltjOobzK70DRSi7tQRoMbeGHzsMjevBBu4MmcvxBy'
        b'M5etjE/3z9ifgrIncntnWaBraybShu2NM+XGcGF8blWU01OrAllr7zrZck7J7/A4cdRG+axEjgL6wUEhuQZuWx08ELVQLghB1Rwd95VwaAPVE/kcHN9A9UT/tSwwp3ls'
        b'JE5JN8Wz5fwCgTVvERzXp2Xdl+pzJnv/ScoKstunxzLyQTcXqwJyTo8lqh8qh2wWqnN9ega04bllgPO0FszgeSYskvDoipg8zVcuheZVRLTji3jicXP+9Cgl4FHKqGV8'
        b'Pyd4GlbrjDqeTohl/K1Za4DoEjiOKmaKMqHTnM+hEzLchgULNtJqWkH3FlGG0odEjjVhfSzamb6gD9nzoM0kYgV0GuClexwnSgIoPO1arHc1kuJ5o0O5UDhoTGPCUDW6'
        b'ES6yRzlQ7+AI14LwzA7grw9FjXQphU/D4+NqgG4FQBdO0kOHeFCZDMckfNqLWD7tWskWaPxYsj7ToZJeakcauar6vWwv6Xd3KEra7a+vJ/fFzfWcaBcXGSi3jrS+1XXq'
        b'+zt3l6Fl4ml89xzLyWMs9XyePHKkxT5x7zTLfxruDq+YtHvtqte2FwSc66xc/c+DFT7rypc+dgflbltdKRr9m/7rlXGhLhv/Vf+y55TsgPrP5be++VKe+q78ueBP4pZf'
        b'/vmrwALF5TVK2zHbJ2SE1Te+tON98zTzW7FKRUBM1S/Wt5TjHNIlUckL/Y69uNNynesDw5Pmz110M5oVbNM7Md5sVdO/Oq57/LbEcbXRpdqtxr421jYb/C871gfVGDfV'
        b'Vo5p859r7vJh0bqKnwt/nzF3w+yOiOnK8W88sKwQVn2xbNx3K+FwJ8+pPXJ2zuLgtaLkRa9+27kq+OSGaw/Srn4441X529vC7V5dPT/i6jlJq90c2ZcTO4on6nUW1XZO'
        b'qT715W91kXf/8elPgWd+Gl8gvbRZr7N+/TNXf7pz/1h33/2oPsdX/rJ7TVJgzae7L+mN/tXkK/vkTyc6/Za//oWWF1+zjrTau7b9tndXYcecu0E3vtuy6ujT4TVvx11w'
        b'/yTc/MXuyBsvr3nt2fqdwr8LpR8vactbubZ0Ud/fi9x/6mvd95Rb0tdVHTOfjfh6xW3e28/XNNw5Hr9+cZyZtaXk3g+58E/rZ6sOZj4Z/kn21IMX2pbLR91dHj1J2NYX'
        b'leUZ0fT0Zf0v9/8aUP96+6GVLZE5u3ba3nwlZGLi5OyJBz0d7t59ULPgxe2nS3ieJkcrSqB4bX2P+4F3R7XOLNyROPMrh9f+ktTdN315iVfe+g9/FJb/1bjpo4pdWy1a'
        b'0qo8n91z+oPejlde/6rl24AXS6KKW9a8WiR/7o3f/1IQ0lP61YwrH46f47L/2cWHTJSK71d9vfmHZNN93zj9VjVn9vPznm2rrjZ6+nsDX5H0pYB7jsFh/oWxNVWdE8u+'
        b'PmD2l0UHJt1tqvtC9K30k83Pf1gfM3nzHLOPfPYf9HxyyWuZuf96PKbgX+vutu387Pt//vZDw3c7HvytsOqFdzd/M+HHHy+kfO1iENXSav6bw1eSn3eZLEx56+VmF+mz'
        b'hSkVvziv+z7F9NMDRpnjFu1/s3fq7bykb3YU1/W+/nP4F9/4/1pyaJ/Nzpd7K38OFTz15Vt/mxB4vjberOKHcy8ve/fYb495vvxNTNgv1Qm/rz2z7O1f3/G/+rPY5ce/'
        b'x9dsL57pczL8qcyeOuulD1a3Jv2wM6wg8eWGn16sPb1J/XnWHoPcG9vCCuY+4//3cwdkYT/8vcGwLT3sOZMZPtU119e8ufSEQejouxu+3CLv/Ogdfdg053mb97p/+XpH'
        b'sqP5Ty7zv0HvHOoz33BsT1LYO9vfP2DwnPCbA2aK0gt3JBuvO/+QPP6u8onJb8z7664XPly3cGapNN3x45e3Bd15smOX8u9Vu3LH/+pt/Lj89X1HpeI3n5xZc8L208d+'
        b'zHxBsvdWC7y09MDzwfMOfX/ive+9Fby+sSuvvAZv5mbETi77XTp6nqOvzVe+JXl/N6p9Dt5xmjjm7uKbc4+OXvGrpPqDzb8cTRV/1CaYMOlU1jPv5i/9zcen/c7eDe9/'
        b'024TG6ZcGdnyq7n5Brv7FZsl2xhUWwnKDhY5YLXuBmEHGcqnolxAVVMjb2hxlKLOSQOC+qDDj+q+ClSPTmmrdVi86mR6HR+yWKxdRQJB5SgKlKCTcFzN5WnuJkjAGnkd'
        b'Uw5LUFWqSgUVotNaiupS1EAxOcRb0QXygB3q1a2mQoeKE1OBiieqGTEpHaY1KmKMmKgONTJtPHs1ynV0gUPoKMUsVAMWtsA1hpTYu3yTnIi8llhbVAUemcJtwTIocFHM'
        b'JA8cXRAgJ2ToWfibc4ZUQgSANuqpA/kCbg5c0Q/fjIqpl4/5aGcic57lMRuF/ha+A3SZM/S+lgBoDQyCriQHrLhv4s1HFcbMa+UclM9xJLJDjCuWtEn9SvjTUfksmuq0'
        b'DOUFOsERVKaF7bYLOtazsNDyKQ4iOCJAJ5zhGhwNFHAG0M4PiZxK7R2J6JwlTsVJVlCPU6ENH0+mJKS5F0rgJosCLYF2rMoXUmiUNSiH4uGiLkatEIu6NuEMUlEZzsPZ'
        b'HxduzF+DasfTvg/YFyF38IfiNBokWiIlSDqnLVCrQIEuo2YWO3lcGhkYEOPCGDj1oI8vgCyoYD5DZ5ZshLZAuB4iQpfs9bkxqM4IuvjoPDSjDvqEOTq9V07wH42wOoKF'
        b'1F7IMYZicvNQi27RJzLGLyXtM8Ld0yCBVtoBpqhXMIoQZNMWWNtArSrEFVWgQ8zWsgcVsMlaJybS7FFHF4mxvQMhu4dKV6sxuI64C/JZC44tSRW5QI5PIHRKoBD3gBl/'
        b'w9q91IZhgkoWYCGoCw7xmHjRiM5H045fBtek0IYbTQaFQljqcXGo2NJWgGp2omvU60uOWlBvoBS1RGqTi3Lj0UEhugD1o6kxKBS6UIXcxR/hydNkgh/iODN9wVJoSGZM'
        b'W23oCuoVBRDLl3NQOmr2w1NULuFxYyOEvnixtqhmnv8OuWTKeFLLWxy6AdVwiRnMGsnHQEkwKkLnM0IonqIZKhcsRtc86NqJhhp0neAxOix31MZj3A3n2PS7DTkoW+7v'
        b'IMGC1/EgASrn4ayyUQ3tHzGqxw+0QeH6jXocT0Q4mVpn0PdseR5alrwY1EyDnROxxkcWkQAaJzK6az0uTUJhGv1RE6txDrRFapulxsBNgtMIt9EFBqF5DeWjPJE97of0'
        b'IFyrVSuMoZaPetwX0eFcBc2Rji4WUCgJCHbmcUbufFQNF0RsHV5C7QI81qecJQ543Arx5pfET4IjY2jJadHonCMeIhc73J0M3NkcFQliUBU6SLOOw/tah8jecqVLupQI'
        b'gRd5cAquMWpkITpmLpLADVSLV0obyVoPqnnQIeXTBm9bsIpZ0vAEzNpHLWl4JbBKnUF9cXgRkLbiLe2SAPJ56Nw0qKaperhlgcxQj/XwdsBTgQ8X0dEDtFQ+1p7LyeDM'
        b'Q50ZQQT5wdRVYIiXUbcqBHsrysNbApZ4L5Cp0U1A/EsldNmYrliKVY4M4kJHZiAfK8TjUTPqZXUqhlovdSj6YguVkfU4lFEw3GmoHU9ZqccsjWqwjdZmAXQoiJchVhhr'
        b'tI3CRg4qBM6pcIlUNiPIlcehUyjfeBkfXcL91UWXlDw6TE5AU9l6xZOxLUi5leC45wugap8pXQ58OWqV40XXglokxuiqE3SSDf063vTGWggdluLzh7R75hwezqTIFOpZ'
        b'mt5qHhSMilZZns/ND4SCyTYq42pkKpvnlatQjxyuQx7eVjKhTcgJLXmbTVE2zZA3SUnSLkG5Qp/joZPUURZ62Hy8njAKKweQb88nAfcdAjiJn8DnVynryjbjFaTGR0X2'
        b'ATsc+JwBOs5fCIdxR5MtAs6jW6iO+NSG+EPlWHKFRieJOV8gg2J0mk6eNDPOUbN7eKI+go4e5ky3x3nxkC2XJh8gJxbeZFUb5Bh0ReguSGLl1++2wTsonBc7U7VGD53A'
        b'03YWOstO6io4gVV5tkPSvjKFGmPowNPBLYL5VN604pHzd88c4lG5mueMRzef8bJVwQ0POR5nI8jfgX/g7FdDBY8jMB54dJuhge2vR9FZVBpI4VqhO5hBrh9cxCCKu21m'
        b'oULXhb7MROvJF6Ny3DNkS1vjCYUipakRn7NHzYIpvOV7ceeT2bfEfKIcjqLLLuTuwJpnh/rM2MZRB61bWUuw5uefDkedSWsuCabPdKbzzwN17CEw9N3btJHo8ZmRa8Sk'
        b'gBtwNojQeJ+DFsLhUBDsJPEPxjs3vQrQ4xYs1kdnffi0sDFQz3Bxi/3wir/Zb5dORF0KEmcugiZHioE8EhI8Orc3Eq4auqKaJJrrzjF8EX3OOZ1tuIXQbYlXKDpn7UKP'
        b'M7i4EU4zzuxePMfUvNmEM/sUOkW7O2kPapBLJWyRxUOBsQ8fXXbwo306fls8SeJzqyMEqJKHilGxP8NjOIcnKU4JhVuqbWSuwAgd4tilQgEewk4taNxklNffBoqMOwVO'
        b'sOlcg0+LenUbaFGTSRM6BagBj+xB5gxdy3k42m/CuzCd0gOR9OFiHJt2dW742KPHYUqwALp4qHHqQjqhHfHiuSnClSreqpaIDDl+qDSBzbbLcMtOhM8zHpcYLYB2shTr'
        b'UCG7HDoDNVNJM40DgslECRTxiOUwR4CXR4/qJMVHdqEcb+Sn8fTkjeMgF91cTscmNj4WSwLXXLEYQbfqxXDSYqsAFaBqlMsWWi0UoUZoc3Jx4XMO0CyAGnysQY0enbUy'
        b'KBWKAlDBRLwK+BLeJMheys730+jcbHkQylrij/vMCArUbRoDx4QeYuiktUo1Xy1ynulKm6U/iT8KLqNLDE1Zic93vGeiph2OUmcHMqXx2q1cgMqZ6HdlDN6pXR3RRQdo'
        b'9ZOQ3aeX7+e2nV1DXUWdMwgORxU0SpldYx8PKlBJKJtruX7oCME51oAcm7iqYI7haADNwRULD91ylwClBG8BesTH4Lwxn4/Kk8VM7j6HKtap5OgDgf7m9mRnM4UbgoWT'
        b'QtnWWYAPvKvMm5scRDPhCnHnxgIJmwNNxDc+0AV6oDMY79a7eIs3i2lvTp2nwMfpYiyQMC9vdEHIMqxF51GBY8BOvQGQJHPQYYnlfwfxVv8h6QyCgsXo6mdQgz+9+TEk'
        b'tjTdNz8HOAdDCjRMvmx5xjwrCrRB4DasGaggn0B2sGcMKVSHIX7OmmfNH0cY0/m2vAkG43hT+RY8a8qebsIz403jT+ONw5/EegSS2IxvzSc/p/GXCS14k3hjhGYU7pjm'
        b'Te6XeBa8cYIJ+Lst/tsk/ji+Fa2FrckYXAK5gXIS6MrXAr8zhr7PoI+N+bZ8Y7xJjxOqoUQYi7sYf5+Bc5jAm6FvyNs9VseFDOur4aheH97t/RdE9birJxB7ItnMhrkg'
        b'yuI+sdW+Ihq+Rrgu6eQCKoN8kzMDpoL9IKzGEuGg5IzdWol6uhIz9jKTqCYJf9aAC+A39z9CMo8m4x9z2QOktIwsHu269MFVGfIMv/8ZdTKPpYxQYX2WdIxH4rKlUlxQ'
        b'Ofm9gnyrpD2B/0r/JjEZBL2SsZGjIevh3n4+wT7hFGyFhpQz7JVVGsAUMnSEGUAV9W79fwGJQnpAM3dSyDIll4vx+KehUChUQXgL/p2fhgILC7J2OZ71YgaZQtaUPv59'
        b'0gHOSEllkSrUitpFmShn0dBbCT63eL0+3jv7nAZgDRirfsqNh2KmzJTZyyQygzqhzFDmEM/JHOlnI5kT/uxMPxurcFXIZ3OZu2yWbDb9bKnCUiGfrWSjZNYymzojDTaK'
        b'rWy0FjbKfC1slDFFBrIFGmyUCbKJGmyUSbLJORxBS/kD2ChTi/RlCzXIKKbxejI72TSdmCjTZTMGYaJ43DOn0ECU/HtFXEyS4oHrEEAUrdR/Aw1lAQven3VP6B0S5nNP'
        b'4DXLi24O6q2BIKBkZJI/7CDfduJvfyRrdwKb8ceeX/DHsU7UJdGwV/eBWCd0t7lnHOYTHBLhQxFPpg2CIwlfsSIsLn1gqD3DO3mkR/thSjQNHjNcrhoEkYE1lhgNyIOM'
        b'x9BMzQd3k+68Rih8uBT3jGLSUf9ZYJHEh5Oq6jEHY2iASnTDHY6pAA4puGGmH70Ui4pdKcLS1ikKS0aQ1erQ5WVJs77s48mJLGrt//yXUU/F+EXfjXf4IDDaOP4zboXs'
        b'u4NjF8zmFm4Xtvc8J+ExbaHXG13eio6orG7M4hYEfcNQppaovV1oWNlwMg/5EhO5YfeYQevxT8KTWBkQ+KiRjnzy9e0AmJJhi340jBLigfJfwyghcMpT9B8Vo0RGG0FA'
        b'GEgsw38SoES9ph4CUKJeRw99YsEjA5QMXJrDAZQMt2BHQAzRuYx1P/8HAEIGR62xAIvoFBIbQYLPhgml0rymC1N2CKjIgHFWAYmQs4eBg+Dzx2H4qKeHIXioa/JHMDyS'
        b'4v8H3/H/H/gO9YrTgV5B/nsUEI2Bi/YRQTR0LuD/QWj8QQgN8t/QQCQ9aYRyMf4l2iRMN5YDlEFRkIoaWX2FAwX7eBy6DXkiOL8cmpPKombz5AQVI/X5eYS+/bP3EuPv'
        b'xNyP+uK9+1FfRn0d9XnUN1Hb4xNkftH33zuS8EXUnRiXefbR/tFb45NjgqIN498L+rbUgFMcNHlvuruEobuihtidKn/hKYEEQMFtJzpE7Xb+qBS6B6MncDO3EvQEaDNh'
        b'GAYNcBF1aQMUECqtLoZQcMqKWo0y4bqDChnABGpjeO5Bq5nVsgWuQoUoEGXjgoawTZz2Uju9/kegA2Y8TAhaySAE9HVJI/9vYASMeSTJ6otJI0tWjwoUkEiBAjLKeP0y'
        b'ng6YAC8DNUzAkJI0GAFThzkwh+ICSPRHdm6ONVBVmnSsSL3ElhERz2CQkCciYl68SCXkGVAhzxALeQZUyDOkQp7BfkMtIW+fLiFv5KB/be31/xcR/wPB1VSSkyoMfjs+'
        b'a0g88v9AAP4HAiD+HwjA/0AAHg4C4DSsfJWM935tXrg/hAkwwpbxf4kJ8F+LZBfoFCAtmaEpBZ1fRSLZsVR4Qc0Mh07MVS4gElUrtIxn/iPhfpAfBVkharA0vwAoorRs'
        b'a+whf40hDUFAZajQCN00jKXx6YZwcKI6Pj1070AsNnt0gznAt2OhTm5qik7tUkfFjxmjJHZ7lB0J7ZRtHpdyYiTANOLQBKeMoFcYr3TGby5D2UaBQdIJ0KwKkIUjfk4s'
        b'JAaOBGMZmXpPbZlpuDwFLlC6dyjKgOpAaIsZJDuTUGInKA5mTnFhIgMoQu3ospIICCaJJNIdZ4dqoJdkGblqjfPqNSQkOiA4CF2K8EPNfsEuzv7BOBtXProumoUKw8K5'
        b'SajOLBldm0sdzlNtEuWzMhJQnoqgBHXBMSW5WYlGt6CTZt+fNYnvTZuVEQZHwqGchdkLuShUaIAq0JkoJbmaIfQHHeHqh1UDhcrnRLD3NI3fEG+AzttAF3VuT94EtSIO'
        b'6jLMcFcKLHme48czV/oeK0ScePI9oGuHnKDz3eY5wnF0jAYoyO0I9R7H4y+LSlbYpXJJM8sf58nv4pSbZfzIEk8z5GaSW9/gf+K3a+5yw+dezBW5rTU8b3X5peLPvWzb'
        b'Mk5OOj875iPDBWHTnyhbfPvHf/lfODjroP1fPXlXXrq2v2HLgvwP0MsmDXUFS7zdJl00ibPeke2wLHWvb43g7u6PF0kVAdWvtBnGLG6LLRuVM3tJQ9UieUK1WXj2vyrX'
        b'fb3vu42tLj+23rDxSv21tnzLzpaVz+wRyT8u6ZkYtvnQlvleDyryv2i59HfXprz589qmee5t3ffZpenL48pTfAtcO2X2MyfK7oZEtWwZvcrfqXW9xIJdsTfD9ehAF+cJ'
        b'6OqAMNlYL3bFXgwVcAYVOioHRMryoRLyUSPVWVCxFSoNDHG2Q3ksVHbtUpqzQShqwOpbVqx2HCsfzrt4qcg9ZqxUh7CiC1Za+ozbRPp+CNwkngOJqEYzuJRn2Xc1c8wp'
        b'wRP2JFGWUD3qZpfs81RuXFdRz47AhcGDeEzwaitTEAMoZKGTeiIHvP5KUK4uR+TdKJvRXUAd3jtIIK4fukycbCAfq2Zm0CMIwguziLpzmKKzBoRGHFX10z2jdjumMJba'
        b'wvnAWQH7lpEtoIXDO0XtJsbMMUHmmMzTtk5DNhQzn4RDcMPKMQAvMAfUBqUBtAGjZgrgxHRnWqIU713dWA/FxaqR/Nzgdgj1hBFDeRwJXC1CJ9XBq4MDV6HRZqiOJfoP'
        b'howGPEx/TKOBowJDylFsqK9P4eesVRzH5GLfgmfFM+Ob8Un67smDtSXdEZ9GjxLx2a9l6g1/u2owPEWwjsBOn0dSNfvE2qrmw5r0H47tTJQIH2x6aGynLg3tDwd2Egz0'
        b'oYGddlJ6sKBiuJ2piuy09Xn02E4a2LkSlSrJ4l10AHpVkZ0nw0lwJ2rlYrw9BSJuKjQJIAev8+MsNDMf8vfKM1ErKu0P7rRGlSxa6zrckuG3oc9AHbZp4UB3/8lWAkqH'
        b'ZjFqZ1D6DjMWlzln+QQWlonOZ3IsLBMdQyU0Wmu7HjoMx+EWXvycK+cqiGYBV7liUzlxPxiPivARi/Jj4CoDpMhzRFdoXObWTI6GZUKpKhwSVaNGYiUyDwzsD80koLF0'
        b'm60XjQ2HIly1+Lk0MnOfCwuwbIJDG1hcppU3x6IyoQXVsmY2jobTNIhyMTrLkSBKKDWgIkwSdENfOPTtZuGS2rGS+OsG7Ypc72JuAo8b89impJSqJXNZqOAkHzuOBCRG'
        b'peyLGe2xjf1x/1hCdsu5fWu6J+Cl7ev+vWjJPxaHd9OgPw7Ph9TL2VvF4eKE99B0/2AocIJSFQMUlOEtNZ95PEpQ59atgllYdglEZdAmF+Gu84Yj5hFwkwHM+o4z4XAP'
        b'27sF7jP53d6btTTCwZZzwrNjlfnOvfvmOjMQETkcxnObBLKqAiXRTXRTEyy5Ey6x4NqDqHs0i4n0hhKOxESiisk0128nUCxbiyiJIihhoROnCnC0GW0tlypRj9qL2U3x'
        b'f9ixAsP+jqUTrQJlwTEW4Yi6oZEg9CxAx1fS2TkTz6AmeoikTaVBjuZ+bEo3kLhIaDNZmdAf5oiyY2nzMr2xeAY3yZ4RyoXikSmj/WR1AFWK7EmMowlfFeWImlNodsZr'
        b'ppgRqjhX7ShHdGlVko3sGz35MVy8Qdbvygh/uc18i8o5z+x5PjX5bkzsiWfvT5vyhHth9rRpvDaZHJUtEE7g20uPPf79GPm3y8N9pjSaRJTWbnkse9TtnDvuT0qelHw6'
        b'YYH8oy8rJ8V5f/zCud8efDnJvznk8gcOyowzv1e+8NLTi64HFM0JcJwZaPmL4a32WUsfW/CSe+tL/mMjw851HnXU03/xZ3Tng90ff2n1dlrYTOCPzQ++o9jfajUjd+7G'
        b'I5YbLiivV0d+3tB4fGzkvGSYU29/Yt71Z41CVz7m/F5l0XbRgs5Lnz++9F6rycaW498+UBz/q031jds/+XZ5PK8sgdrZpbeX7T2f8rdPTn9buv4T42uRHm3OBY9vMd0g'
        b'GP/CT5N9E5sFP/3tXlae2+vffvlA4ma32LjNRVa86kJh9mt2Ow692fiz11cz3rCfNe+Es/S77o7VC7+KOXH+tucnb2T+kPPm+6W2u5/09Hn7w7qLE95++qRbz2Iv6e9l'
        b'dQce74W7PVGrd+tf+/GXuvLcV6/0/iuvumJ3xeZ9XU/f/dr/oxtPpN8NXfNO3lfZ+x67O+arrB+bvtt3ZP+RzxbElN8Y3fn8nfU2a977Km/it3N3F036Vr6otd53Qv2y'
        b'zUWRlz8wm2X+YO17uQtfefL7fcvykkx3H/v580U/lW5+5sO/RitPKdq6vzaUn0JLvv/004jGZ0+3nVzvvOSa6WeBzy52+Ftk8t8+kdvLE6WvhpZa3my803S//puXz8ru'
        b'3rzf4dnUfq41ttXf7a+7Loz6Vvpa6KeGLaFnDEKXPFNw+sUrSTccGr+wvnzLbcv/x9t3wFV1LP+fc+69tEuTJjYEROXSiwh2sdJRKXYBpYjSL4hdVBAEKdJEFBERUEBU'
        b'QFFEedmJxsQ0Y5qkxySaxEQT0/OS/LecixejviTv/X/xE2DP2bN1dndmZ74z32YuM5h21GKr7NehP+gdCfls6YMRcYf077xopFczesqkd2el3HZ5JSJvS3C39YtNszyM'
        b'MzrvH3zF/uXM7b9tf+Wqe6pr3u9z5c4ndnxwNOS+bpDV1wn1IXc+/mNCzucuH5h8XvXciarbi19NPTisKHFscfrd624jnvu5dvh7vhafv10fM7Howdijq2Lff/V0rfsd'
        b'r5f/iB1RXFK0f3HzrZEXJsbGvnhv+28PMkpvfL1t48UDD7Zf4GJNrhekr8uGS3EJ4WMvW/fURu2L7P2X04NNp4vWuveUfnn9OZumDSfv6H1UtOzMEPujgwP4VsfPQ97w'
        b'vT3+1ZNvtpz56mj2xOTfPR2TplaZrf8oNkP43fPte6++6rEi57j17V+nn1xsssJp4+WPP3zl4vcv76nbNvP1aYe/VMbXfFbnnL0vTld+cZCnteOu7xonfrXnzvU2jcP3'
        b'Os1v3x0Wqb/u3vDLD9zf85rct+HZruBvBo+1mp2TeeiHOGP3e88uvl69RXb0+pUvT4xVJFM0HZxF2TMJy63GbmORsKqf5UaXUB5l+9dC9zDRbU0QXOgP6deG2W2K2Npv'
        b'sZqi/4xRtkIF7SPgP2hCJ5hEc9h6pv/mEQT+pw79g11GVDiYkzhBBdaLtaZwPYbVi0E9zHSkQ6IXOtbeSR2nB8fQGWaffQSdgVNKOBqqHiKMIvVQOSpKJ3ygHipAp5RO'
        b'FKen8MPsRxE+hQiYRwXWm4SyNfBmlzeP1hedRKAY0OyvklUIXk8CLAK5UhOdR5WueNDUUXm7w5gpcYmtn78DQeTBXlSiQuWhapTFRqoRXTBhyDssyvfgY04E5qEj0MK0'
        b'SrloJ6qWozY/MZc6OG82VFEZJgpadBkyb/NsjgLzkmE3NSc3RlUZrHxHqEdNIjJPAu10qNaiXnsRmpeNJTkVPI9h847OoJLMem8oiVvp76cOzduLcpl8mIuOOYjYvPjR'
        b'FJ3HoHnjUR2Tkw7FTWLIPLgIOyg6T0TmNQ9noMsDcHSd3H4tAecNAObFzGBi4m50YpzciYDqUB6ZHQasQ4dhJ+35Kqh3UgbxBCWXTZF1mAx6aN+CvBb2I+sgN10E11Fk'
        b'HR6JGmbYfg5dcGD2R9ACjaKUp5zNoi/uXouqLRPlQY66CtxxVM9DW6aETpu5F4lFj+omU8CNOtoG1Q1jisQWqBrsHyQi9hLWq2P20L7ptAK9ZROUVgkEs/cQsOc1jYFi'
        b'mqE3RO7nGJBKeG/YrYDdSid7Bc9ZSKXoNJyEYtp+Kzgy2F8vjuDy1EB5w9ezyTkfgcrtnaHWSeE3AJTnJsIBwmG3CwVyjJrDMSCHhoT5XLq4woyhz/gIdJjg8aAhks3n'
        b'CSyX72OQvDhUoia3HzKnfZqAtkeJkLy4QRyF5DliYqFrvsfBTlxA3tGiqyiJKToO++jrMagC7WB4vG0SgshjeDx0YD4lw5moIIAADANRO2pQIfJ8zFnJuZAVLHciaDyU'
        b'vV4FyMM0sofS0PjQqfaWeMLynJ0GAPKOo4OMCiq9faEad9RWHZFXnkA/toEOAfUmyBUDAXmY0cqh7dq8ES9rhslDe1E3c2+VZM9QJO2o1ZNh8nwXcwyRZwEX6MI03zCX'
        b'AvKgEDUTUB4D5NVCNvsyK3ylUgIXKQJHhaSxX8Xoss0JtdBNgICVjlA43uoxdOKEzEUiGi/Kg6NYvBniDQh0mqI6EYpnPEz0d7ZOl2LZoGtNpDIoM1jFwXovZLFiY9BR'
        b'fy103mmgbzZLS1rgNjs4TwFC85UEIkTxQXAigB4kK1Axyu0H4eFTo1QE4qlgeIA3TIpbGSRFB5VQ1A/Cgx5U/xCIZwU5bBOtgB0TzPBW0aGC6VEo3hwoYZdb2TqYJiE/'
        b'eLwIxttiRgfKEk6YQ6ET8aTYD8Ub5soophcfdqUEjFeL50MFxsP72gU2/NXLI0QwHpxZwzEsnrOMUUvXkAzcZFu/TG5iPxBvD9pB+4OLO4RqKTgILxHIwwPRHghncIvN'
        b'4ZTUXmFCi8+EukWMeZ4ANSL3bAYNbO3thx7IwRSVJIioFG/8hoKQi1LT5LTUQFSN5cczhBp1UKmAWkPhAJvlRmifh44byEV0EZZNraFmNTszO/XQTgYAtJlENiOC/5sM'
        b'FSJ+aBqqUSr8yCmozQCAkDsM78UjJmGy1kCn2Oo/TlZaAOb86YnSDwOEbHSSNnElHEdNIgwQ02grnSuGA9yA9tD+pfnDEXK2b9RXAQH34UGnY9e7EVpFICBUhYtYQBUQ'
        b'cBGqp9+PgqZMigJ0hHa6v9QnQj47S/emoXIs1tVGUa+uasg9lDOermVdtAuK6KU+3oSGpPZD90jsCXJtYYAaNQkaTw21t2HaANzeooXsVKpMR4fpcI3GZwwZMSwXwg5J'
        b'+iqBHtr2UGtBiNVfoQ35Ct8MhYjGGoK2S+c6o3OUBudBxUaWCb/dpYl7qgkHBe9JeLukJ2MZao9DBYOsgh9ekRKInjfevdkVJDo7VLyjRydhb//dK1Syg9vQA8qhgAwV'
        b'dA5id574vLvIzoYDeqhQiSsOluNdvCYIiu3xjmu4QbJZmcaArLWay+2hKIAyYfbk1gH2C5ugJZXdOLcF2yuJZ9XdePs6qW1Pu8dzg0wlW0ZjoZogNKZB/dB+5GIbppEn'
        b'oRcZdLE3lrZLuhgqVLi/wQz5J8L+ukLZvWoiOk3Bv/7GdNsh0F/UO4RR/yHIHUsx5lDnzTGMeQbazraQbCgnoZn3ogYKHVaBnKPmUtCmBj6VTzJsIj6G2h5pIgUnkkjP'
        b'dGI2xG4Qm2gFVQxhydCVuovo5MvgKGpXIW0ZLDF5ZD8wcf8ctos0bEMVFJgITTM4hkzEi6uYDn7qZNQpFzF80CgToYkrEINjj4QCbwpNhAuQy4ngxEI2MXiE19PdB+Wg'
        b'3SI8UQVOtHehp/4ifEgWyDFHgxeuH4Emwp6NjOBaN0M+Ayf6Dhc3EIpNdJaI8a1hvxkDJjqhWo4BE8P1aKEKXdQu98ODWCQCE1HeCjoYuOpMZYAKlIhOLlHHJaIqbbbn'
        b'dYyFzo3r5I4PkYk5Y2mbAtA+1EkOEvsgR5QV0I9MnI8Os328BZ2CHqUzwSUORbUqaCK6OJ8dYageM9XNC6DDUR2auD2TbTgn0CHMDFJsIiqFKhGfKKITUe9qeop4hQRS'
        b'bKJ3EkUnUmTiXFs62qPx6dsMHUOsqdigjkxEF6CHDpr1lLB+YGIwHKJxZuCUNe22Hp7yI/5O6LSHCEvEZweTr0JQ8yp2GwbHoLAfgIhPM4X+/z3ikOKnqNZAIDdbT9Ma'
        b'bOOGqECHhpInwQ21+uGGRvifCQ1vY4jTBGr4H2CGEi0REiilEEBzrUcBh0YUYmhCcxDHlLpSc96Mlwpz/iugoflAoKHZo6qB/y3KME9TRHY8VVuRxf0yAGv4hEYphLQj'
        b'RCFSz/8JYzjwzV95pA4ZlDDkH0HypDX9+VuPJ5b6pDca7O+OfiQg+fFYzF/aIZLxr8L9jP8vkX61uO6PCEp0AffPkX5aEkMNEdk3RoXsM8Ip8+nUbyY0oDrMg6ku0Oea'
        b'qq7Qec4W9coSA8YPsN3VF38rd/wJ0LdEWq5Zrl1uHCuQn+X64t8m4m8d9jteEiuJlhQK0Xb9mi0SmUg3Vy9XP9eQBhfXjZZGyyiQThajEa0RrZnNRWtFaxcKSzRxWoem'
        b'5TSthdO6NK1H09o4rU/TBjStg9OGND2IpuU4bUTTxjSti9MmNG1K03o4bUbTg2laH6fNaXoITRvg9FCaHkbThjg9nKZH0PQgnLag6ZE0bYTTljRtRdPGOG1N06No2iRX'
        b'FsuTkOzZWktM6d9josfiv82osaaEav20cuV4bAzw2AyiY2MbrcA5BkcL1ImhfZ/uTO/A0Fmi+u6js8IjhprEUko9B0MS9tv5pCeT8BxKlsfDzYH9dqfBLMhf4wYUptIS'
        b'Kp0svdVMEEWLOoplEO328Nv0mDQaayN5HYlHnD7QhFA97oaDZUzUqtWWaTEpaTHKmCS1ItRsHIlZ7IASnmRENFBXOSARlExsx3xjLWkgXqVlZkxajKUyY2ViPLWGik9S'
        b'g4hQ8yz8Ogr/n746LWZg5Ykx6auTo6nVPG5zcsK6GKpVzSCbZMIGYuY1ILCI5ex4ajFl660QjX0TBtqREXMr0RKRTYSzOA+qEXewtJ2hUGWLslTGEIu49JinTRKZQ9uZ'
        b'CoIriVKzOhTt/ZLT4uPik6ISCMBBRJPjISDgjUc6qlRGxVFoSwwLoIJzsd5bRsek4FNBaZnMGk5NB23FdzMIhSUmKwdakK1KTkwkRs2U9h4xUwxSCH2S9YkJfRqrohLT'
        b'PcatkohbjUzcdqjii/hVFYFqmrmqsGZyun3weAMRYvVFFbkkT2Mnt0W6UWOzhKrIpVRFLtkqVbNq/oX/C9C1AYvnyQZqT7JZxD1i5oqLAgNEezsawYaW+3Cu8KxQm1S8'
        b'FB9vyGobw0joSev0KZAqOpwTCTJmVRRe6ZG4SZHMbpAV1l+IOrk9Ia5QVHR0PLMyFesdQG6EMFMzYsQlq8zAa6l/y3g8lGSALS4LF0RWXFRGenJiVHr8KkqgiTFpcWrB'
        b'gJ4ASknDKzElOSmajDBbx08P7tN/rumJRDbQhME+SEkuAnZZLe+4/qO9ojld8bzibIHuNcWb7duVXPwWrYYrmQ/I5xlOHLsDgm5ivgNdxEdYOhZSFOgsZtd7vRVQidoR'
        b'+wg1QBZcpOxwKFPYV8AlH3QM2lELbsNWbis6A43MdbGXQO0SXMJ/H34/TpOjatdxJo7QiIWuDlzCJG4SXEDdNPMtQUZM2CxdxtT6lG6azmVQqZ74kGmEMiKpu7u4QLm7'
        b'i8DJJvDz0GFFBrlb0xqN8pWQrw+7M5n6IiAIzqAuJ207W55zg3IN+2SUT+tdYIYFxOwUOXkhBPKe0DSFGmcMQofRpf4i0B7UjovRIWXxnPVEmTVshzLaT5+AcDl7LIFu'
        b'LdRG1AohbOiOQ+Ec9VagJtSU5muHJXY4be/r70RUKOFQpTUc9+MwixxzGJ3Rgw720mgBFmk9hCRumUJCfULDHtQ9wdOChFFxhL3uLh4Cp7tFWAuVUEeHBU7gTl7Ug9qH'
        b'OTQ43a1CAqp2zKCXPycnoTzUio4+zMBzutuERChEBzMIf412YFnyPAvS4hPqQ7LN91HXEM0yMIcczcEpqzIscfZwTBg7mOQ63xETChFajVGR9jAJDWBal0FiNJoMghJ1'
        b'L+iq4DawO8Df31FInYJqhsNFlG8K7dDub4Ly/VEhOiHXwaRT4LcghIuJNfRENdCVsYR0oSgK7XxMacQM1NkvzBZ2+8CeEJwq9g+DU4xiV2/CNEttcoJ9ZUajdSAHNchk'
        b'cH72aHRcwc3ONIEa2DeCWTY0GZD7WIOUNEwOeFrqg/gxg8PoRFtCE6qTaxGXAhIpytbg7XCNzBCmOyoTOnRT6TetqFDgbQxQKyWv2cPclSlB5FZYogsto/hIP70M0Utl'
        b'NmpSpkK7LvkoaxWq5G1gLzpGycDPgtzxnaUFYtG8DWXzZk7Qm8GifUDNkK2o4dEpRBesMzzJ+/2Qo6MeaSfQ0S/YXyPMpz+/OGQoCzo4qE2Qo2NeuLVEgkCNqE024Fu0'
        b'g1yOBYfNcwxnX3FQykXDOS0SHXZ7wk9//PFHQrCUrdDY9qnPzQ/D4grlvxfMCX5kBW5C5WoLcHQgG/AKyBmNf1T2r0BUjbrEMvAaPzXhYSlkzQ9YhBlRdDDxhELdw0UI'
        b'ZxfjRQjHUTUuhkiIqMOUqDrVFuL5uY9dh0ZQQsffyGW1ahFCGdrHluGmwbS7I/XF7o5/UznEbQYW8ag9x0zUi/aqEc5JtJsfg3JmUhOqVVNWqAgHStfzdugcNNKKvKEW'
        b'etRI56gFb4N2hdOKUgNUO5/9yEVaszn6cONy8aHGPR/3DQFksMkoZkaoEwx0QBFvJgnMYE5H60jDVFXAdg9MaAfQXlrc0s1iZ+bMcjsdPZWLL8q4JFUW4T241FuZWHYt'
        b'ydjVZFdisft+m7LpN8aXvPar46fhyDHRN0sn43KzkdHNrO7TwkGfMLfnV2bf1ass6Tj+Gb/ovomDodwiy9Q+PG9u5M3Rz309rvzalQm3p/3xzc8JwXuS86/ccKh23XDk'
        b'ecsdOrH5fcNMDfydfpROe17vC+v6/dalVYivkJqvR2+FRrdI67n6nOYTqSGc/pAtQ3/dkb7zzpmQDuuT8avtLy0y8V+5OKDngUlhrZ/O9jGbPvm5Pi7A9VNfg23nX9BV'
        b'lvoUbd795Sv+jZ9/WBa97t6Namun9vTfp34+NtHNIa+9Mdkh5li7m3y2bdRzEz6f1PfA6YBPh1u5Ud8Bvw7fhQfcJtyt3lXaWBXmcunDZRfGOrkq3E13JH15sWpdeOoH'
        b'Q25/cXC+U8ON2Of6hr8IOx6M+K3OceIHry1ausu0qbWowmPfyQKHtjNelVPfXxgscztVFhr02Ws/f+DqdxslvOW/+jvlOavGu4XPDrtzac+WB3bJ7W4GC++/l7a86NCq'
        b'7wKWBs/49bnEzaOCDu+y+G5t92zzCceiPlUe8Bl5O+LysIkfdWu8VRfdqxfqWdP98evDVp2x6A286JmadlSnnev6cPy73s+teSt4kcmQHX3LbW+GhbY8+72HyzszXgnY'
        b'V3e7ftSavDMjrr32r47EMQn3JWPNIoetu/9J648vXX6nd8MPvuiX+Qe0fn3J4+P6j6YYW17rjrkeemPb+jVXb82+2zv5JffJK757+5txl3fdircOnvKNxkX84N6nEZMz'
        b'PvnmF4dP4y+1r712P3tuzN1egw2uLYqvf9v60/QXb3a5XPpIY9P8XyO9Jr8e/ayBfZBewNtRZ91+WvmTfOLH3xz6aP2hSh29irpGu/KP1gdPtTx3u6dm5Rv6LYY/GmjP'
        b'j69rf6c9OsLxpnHpl/8Wzlwx+GnxVYU31WHFz4ueAwftnQIFTObHeH9tKGdKH8yPmKOCAGt0kpwD+HSAfIGTox5M8G4jmfqrDW84cNLeN0ATf5vHTxkxml0xVy+Osh87'
        b'YoCRBN6BdrKXFdCJl09BpKMzM3DWiBRwHWOYqqh2Dd5rClDLAhKIjZgvbxXs4GRiOj37uzh0FBU4E316gBPaHRyKOqlxAMpz9nGwozBgTS4C800noHE9s8jogRp0Bh99'
        b'3f5/svjoQnmszlNLZuG9uS4CF1XoqMFprBBGEftopm+pgkbU6i9ATbCjrwPRCshRJ3FOfFFC3xv4wHl1d9PE2gRqdaQrfJfRBvCoYa16KCZqxI73jhqpFpxAbUzjcQpK'
        b'A9hNsgI3uFS8Sl7MHByHYx6wDjpQm5f6TbKnPTNzL0JHFtj7ohN4n5fGoX3+POwysWJ3zC3m5AK4WM3/HSrCrBQ3FA5KU+H0WFrADNRCtJtUpXtuGurAcyqgfOqQGxUt'
        b'y8Cj7Rfo7+iH8mPx+AWJt9Q2UCGbhMpgF71oj0WnUyNRrRIKfcnM+OsHOUKnv8BZzJGiBnTaharI5qOzvnBQm9hFFGuLGfRmC0Qdi+mNmt03QTaUSPGWX+Ac5OgQqFaf'
        b'pasUGqALLtHhckJlnBLKR/S77aMX4yhfRCxU2o1EVZgbKQh28gt08A3kOf3VEi8e5VA1Txo+ynND0QHGX4kqAT0PiaY7YkGj4OjWCFQw1Y5Atf2hQJPT0BZ0oceGKhu0'
        b'proqqQJHshYf6+f4zdDtRr/yhmNE/cjc0QroEqbTan7YijSmvqhNC1A5WJXAIRNXHh3iRdffWjHoIp4lXFUxc1Yrg2oeywYHIZ8RZ7Ub6pU7+TuRT5vxyunlUe1E6GG2'
        b'GmcoSz7Q5SzVdKdRZbc2083beOLm1C4m2miVvllvMx3KqTZQrsTzX6yuqIYWqGRDkYtOjiRaSRLHSwIH4PhoHhUlraCdkk4aQfpUbE8a1oHqQnjMieelsg434BmoFO04'
        b'5KgC9uOF6JZM32nbT0YFRG8karhk0C3wRtNpQ0eOQmehQlsZpLIHgHzcU7IZeeAX9WRKodL7oVGAEWqTQIG3knmCvQS7llCPpkRjuQLqicVTtYB2Y+58D1M1n5pqpYey'
        b'HrEz67cx27yIjXghjxdkB/PdLIEzwXhjQ21mEyn52MC5AMxeHGfvqdymwelHS2YbQCvdozDhFYaigsx10KmXSjhqtMePMdUE9O8MRT6BjviTkNla+htRKauwBNo9lfY6'
        b'mJFSbET7eU5zizBuFTB7syRo3Ky0TyOEjmrhoIzTjBHcUPZMOv8SaMM8fgExwEGFwTTmpYwzxWTSgzs0CO2DQlEXVWIkJ6XjQpIjcRGoWZiCdkML0+ZexHzVRbgwQ1UQ'
        b'JlRNTj9IMt01mM6KdAEqdkVHlX7ExIyHLt5wLjAXt7wGFFN93lB03J/o8y6hbjoXPqPRSaLPm44O9fsbpQo9LE3to5+6Qy5x/Eu2nVabycR66kQ8faFEFeujULaS6tCJ'
        b'e1zYN4liVzJRDZ7JgmDcDF+8XoiJPd0fnH2gUMKNgkaZpwUqY5v2CdSBLiqDFIKRaFvnz3OGIyTz17NlPBrP0kHig5w6G6/m0PmJZqqduB7wG7qtSFAOpvlifqMUihlZ'
        b'Z49fr4fO2/s5+jvaBeGNxSBOEjVsJt29Mtyg9mHjmPIVH2FBMk6xAvZvlaEDhk7U/m81FGf200eW7kOhi9BH8HgseExCbRpBJAgdsxODPSMf+qnSRdt52Ik6Uugw26Iu'
        b'1C7HL5ct8FHR8iDolqATqCmBfZ43Kd6eHj+Oo6FSg9OCCwLa6xpKP1+nbT3APSpVP6Lt6JLUaHWYQu+/V0/8jzSGj/NC0Yl//Ad94DYuRoc3FAhmSIMfzusS7JBAlRwE'
        b'V0R1bBpU16YhaNG/9HEufd6CH8Pb8kaCIX2mhZ8RhYghfjMUPzHjzQSCPzLDaaJTtMClaVAlyYAnPPmnT78kiCVWEtEKbjRVvyJ81CGGjOnjuoka6cJARJLufzUTElbc'
        b'w9L7R9OX2PGTnes/qPyyuPNj1JV+j+/H/8gZxgktlTOMgdX0e8JwVWkq6FW/g2VMnJOlHbm7dHLxcFf5/HmcY4z/2MA41sCwpzfwlKqBvwwjLREvvi3jowfU+RdHo08r'
        b'YhXThjylxo7+Gq0onp2CuGMt6YfEK8Pfqjeb1asX0X/THxH/tMrP9lc+xtsyIyk+NSPmMa4b/k4LYlkLdCNUd8BPb8D5/gbYkd4r03H36T1y/xXyP2mESIwfcU+d657+'
        b'up1CkomXqaTYZOr8wjJqZXJG+gCnVf9kENImP73+3oG0puZE6W9VJhL2tKdXhvorG/qwshm+M/8JfaV5P72uy/112ZO6kqIeOgFT+U1hjiP+UeXRT6/8an/ltqGPcZGl'
        b'asA/GOI+Hep3IoJ4gXhKA64NnFbqPIIt63+ykLRYnenJT6nx5f4ah4huRv55fXoRK6MSiHIrIjklJukplV7vr9SLVEpyM51Lgrqy9lGvNP9oG9Xvb9OqhGRlzFMa9frA'
        b'RpHs/7hRA0C4/61XVJ57VLMkCYp/00hTpiSceMGDDOLfVP4i8T+myWnt5s/y+GCjPO9SVJjSL/1Q0WckNGLpJxodeIJbUwOVbRXhX/8jL7WNi9to8siZnxCTFBHx152a'
        b'kgrfIiNPrsX/I7uRxbUMcG362Mr/r2ZBGhQaP9zmFqckj1dfM35vi3+UbuyHL2LpSMHbBYc/JLI/j3Mt9/fGec2feKuVyckJf2egSY19f2Ogj+k+jbNjtfePNGkF0bAT'
        b'omMa9ofOYFXew5iWnc/V69ewC3kyPAcSPAcCnQMJnQNhq+Rxc0CgAbr4f/cBczAyiHlOOb92iqjjQftGC5DF28SYULWmyzYpp2X7h5SbHukAG+Zy9BY/GRWiXUr9NG2e'
        b'i0UXBDjCO22BnRnErGsilEAnvTlhvhuI25M9/viPIOIJZQHKR5fmLXAMF7gV0zVRXRTUZtBoIrWoDXb4+xGFDsKrrQdy6BUZua+ScXarZKglE/KoikKyClWLmioonC7R'
        b'5SMHT2U6w1YsaR5R2YPbox7nfoPwTjmD09aiimlQIN5BTUTnpI48OmEVTxVghqjXhMXuNQ6lGPFN8oyhtK979Il0qg1lWEAl4jqWUGNQDjoXSjUjwzbCOSoNOvom20s5'
        b'bU0BFUE+CwE6WVvOvGigs/FSKY9qoWS5iEg3RI3kilPhOHqmBqc9QUANM+1peVKodRfDssFOqKDwLyheTDsQqYyHAscgKlaifahJY7lgCj2ojY7hbCj09ociX+K7cRGq'
        b'DYACOubMDYX9FBkUoi5oHUBychXJzXpIcgMJju93UqciNh1GbAsx/fyJ4OLUCY70U+tPBOcSRMmqeJqUOxaASQ+T1fPSSI4ONTqFjpIYUuRGWIIqUTm6wOPBzEL76MhY'
        b'omObWcwxCSr3gGMk5lg5pgqqbDyMeiXiJQKbo2VQL4mBS3CMEng6Khvef8vYjEr5zZbQSOdo+hZ0SBngHApYhMMy6wjUhI7TT9zwyO72h/wAQlEMibItjKrxIB/tTVMF'
        b'wpLAJW85CYTVBvn0u42zoV4VxkxqETeWR0ecl7PvKmasVAtiNgIdpJipscuoNUKGIfmBLs0iJ7GVBF3irCYLChnr3jG8Lo6pfeuG6ui3mjas5Fw9VKuKJSZ1wANZyqNu'
        b'D3SJqttN4dg8+4F4qbFQJ1kJNeg0Hdm5JG41QWM5LoYTIhgLHTOhIYlHzo+zx5U64aXhpHD0C0Q7tXjOGuXIJqBudIHVvo9ASVUByWznMvSTrhjgWrFZIQ+MZSb2PKeh'
        b'JQxGh6GQ2i6gAsiGCvvH4AimxzAz/WGKDHJtvl4ynMI4AugNMtlJUD5ZBVBhxI1ZKFtrhbKYXrjeGBNMwZPjKxnALjwtQWi7JpQsgArawPV+0PFQ913L8ZG4jIN03Ieu'
        b'Qv0IE3vo2NK/o+SlUS8ES9fO7N+0Bm5Y1njLmoZJjCzbcdA9o3/bkTqiKgO87QyDXGZ+0pUOl1ggLKlFiAeP6rWhmbZrCNoxkSE+OOnUaegwj1oEVMcw/uWz8WIugAtw'
        b'XtwOyFaQqk+/W+klETcQ6Xi8G5/GG8hWdI7t87kJ6AimXJ7jvcZAF1F1nB/OvAnoQp09DbgljUpdi7e/2PXMlKMFz1YHJi0fR4dAdBrtIOjgSmFzPJyl5BG3YeNAcISv'
        b'N2oS0RHx4bSxtpA/pz9UWXokRSrBLkwdxABmGhRpq3atR7esWFRLd62JtBh9C9SJCaZ9HTSjw1KOh2McNAWjetoxDw9rJZzWoJqwVn9y/XsUHaEdg9Nx0AVl+JWDSxzn'
        b'gOrQBboDJdvpcNnkotUw0mFliB9zNZFqJXCTtchJHOkQOmsqe2g6Xo/L8hzPkfDdHzsms4efjNfmQhU2JFh5wki5MND9BuVMyP+k3Zu55fpb+M18im40F473y1QhWiVR'
        b'Me5DjEzOr3uEq/5Fe3JcTFLM+pS0qTHaomMIKZexCP8KnwHNyv7rcHbXGS7AXuYP18HXEZ+zxXhZqnvegDKiUygz8kel7oYrx8NxdHwDOm4qm72OQ1XzTfGZXbWQ+ozZ'
        b'Gk5oBAjap8zRyZd6gvKbP88x3IfOE/5y4FShDkGH56AGmnUj8VnVSg1uoD5ED+/HCke8WZKS9vAalPyHh0lRqzl0U63+DMxcHB5uRk+Bf2kJxEiAUvdhV3SQTnUUNKpm'
        b'Wh+K6UxrT4VD/VN9eiGe6jHoVPxnRn2C8j08QuXDbWNCLyQZe5vU7H/vzMUVvRfXtQf5zPjYpugBh0L2+m/jjIyOW9vO0e+es/fWOLPq3Yb+p/VWy5tfNwnNu+fj/czg'
        b'efM/lRvKMr9OCpihc++Q8uvzxec70u4G3LX9IO70lvtLO65qmLm9VH/w3aH5qXN1HI82nKgfPlXm5u/6YV/4sj5+0uejjG+FxNhb1Qwxczn1L424776oLn2mtn7Ep7MW'
        b'X9Uv/GDBDJea0Gt17jODBn9b9evP016SaF6I2XR3zr57nhcOu+/zmm8/fdDywQr7Ba/XzPGfWO82b4zHB6tyA+LGTjoW+svdwyeUdppBL8699trONVdXTv0hzGzNHL0J'
        b'c7fevdeRt//drKjwEV9G/0tzrtnh7cd8bzo35K7fdX/t53qzrpatqfcsPd7qsNXlPf/YMYvDdwTNCKm/dc3Ucf9Ft5r3dtz8fENL/NkMx1/fMnV8vq2u2JtzrIKfRj6r'
        b'7AtLcriS+OlK/UujkkrSYqZE1uWlXZpQG7zhwcST36Zc+2nOpmPjBeO18xK2v9509cDR8fNfAuuMGqueWesr7yem1VobXB1R0h3wxdhPHBcsPdo27/3hH43/aANqyU6e'
        b'/6PHoqZ3R2ZPMll8+OquH/QDT8yOtkiPMj57f5LDsRkJhQ/mPPfe66HPvJt3/sbzQ8+f/eb3pd1ehbd+cBpxOiZpy2tzPtA/7xey8PPqtQa9ep67cybXZD0z4s6ddrsb'
        b'PW/ecfzCP/3NBgv/lITi3qh/O22d/Q7our720aFl2ufbAswKE6znhs1wemfmXbepC02P+Tp/9XNG7fH8ZbN/TFptl7E3NfrHk+3PWt15zz34/VXxL52p89l8n/uDb/78'
        b'Yt/Y5WGBX6f3vfPTy7ruZ35XxP949IPFfVsyX3hTMmbKrckb9p26tuiTF4reXV9847vTQ7+Se6a9vsft/rx1ZVtsNmk5Jv1gmx74xoeDvrpuUWN8ZdNbGbOKv/mqZeK6'
        b'n49vbt1a98ULI7Ve/OBZ47yrQyN/K17maRJSODg49NaEW3e9ul6x2XTl3WciTDLHf3zTQzFBhXPPRVmEG0DH8HE/HnWZ8agn3YB5GDiDeZFqOeQrBKj21bbFrLejBjcI'
        b'NUnQQeiFHFqCJmaMWuR2CmjHqztjroTTGiaEa6JDVH1tjOo0VNrrbaidhAfNQ3vpdxZQlqimkYVsdIofZos66HdzDNHZh2rzLLSHh10Ry+l3U6LGqClroVjBE2MAKKTa'
        b'ZS20Hf/9kJ0agXIIP1UnRiqetXAd6Y1vaoCzQoPTgz2j9CVjtFEr06ef1h7xUFlLQN0DocnGqJO2zRHVCERXuxidU6lro/EreiaemTFR6RWirq2VzmJAtjInqJbb4j2t'
        b'aKKUE0L5qejCKBYQsGCRiUoVmxRFLCLyQ5mmvModKvvD0G4NU8HeS8OZWvIAaokSw7pKYLcHOoPP+xS0jzkZKINK2K8MILOCN1Z/GZ6knZyOroCZ2xNwVozdZ4oO289y'
        b'JEYBDgTo2Cq4wwXUwBCT+KxcytxT+GcsEZ1T+Clow0ygcqQc7USHHkG+h25TGZDsNZMvnK6Omce5W5jqrwM1ELmJOJTAUySdgHLgPI+Zge0eLMhhRSzsZ4B9nOss7GKI'
        b'/SGaTMNX47xJCfm+vtDlb4oOCJxmqmCX5sRwnA2JkMWw0wG411kMPA0XYS99nQClqJFoLVOZUngdp7NQQN2miPkYQOcGwzm5NW7p8RSq2pShah5OWkIWtaTRmG9CvoWs'
        b'uaLSsy2RNigSM0V1cr9Aew0sSHQvIqrovZjsGBQ2XwvtIYKCtpO/k04s7CBslDk6I/VErbCdRao87rFJxECivVhGUMVXNUGFEiiLULJMzbJQVRTUxSSaqjr4GY6HMx8J'
        b'cARzcSJmOMA1VIQMb0P7meL06DA4Dx2uswagHfPRcVrDYNgFO+WPehHBJ3e3AD1z8DonMrFWKpYhH8ZxRY3DRPw2Jq1cSuPjEYlCS0OqSqzgJHTw3gbMn0XUQm/lYMiC'
        b'IltqWCKbzeOGRrKFcW6zDQvDKYGuoRo8OpYIB+gbhQWqFDXQcAY6ieByiQHt0X7UgorkKWiXGpp9Cd5M6Ey2o2NBKoys/yZ0kmFkodGDkVCHKexg8Tsl0DkK9eAVrIV2'
        b'MGukHSAKjTp+qMdkIEg2LJpSghPKhnI84zMtRThr6TZqvGA5atZDNCux6Ya9D+GseHzz6EB4L0Z1ckzYux4CWkegQgayrRgCBcRgE1NgEGzHvDan6S9Y4U9Fw5dLY2aI'
        b'wT8lsB/ttsTCINqD55e8dE9ERfaoyXmgSdfRxcxSrHo98crqEIT3b8zR8Zi3O8DJ8YKGtsWomVY+OsSYZtijgDwfKTqqg9+3CZjxQvlsO9iBt9oqIvhBG9qBuVJUx8+z'
        b'jKfFz0dlG+yDHfCSJnKJJrRBNieHSwJ0oXOwi3Y7A3aNlNthCeE4lEqIwes4zFJW0ZozYq0fsfWxQiUSTZSNSmjpa1dAL2ZF1WzczKBINHMzy1SY/X+G8D2qqP3vPW32'
        b'6RAwVQQFNVDm/gXC6v/na8dtnAkDyUopaJb81OfHUAW5A2/HW1CFOYGkEuiswDMVN4OoChq6gi1vxtsKRrw+by5QNbkY/ZP91hWGUjQhUbmTPEPxX0N5Q4HE/WRQWkN+'
        b'uGQoVZnr4HyW/HD8j5RkSEujwF6BXFNuVDyqeCa9jXCaTFVVyqlOD3vPRBZpn3b6+uiY9Kj4BGWfZkT6+pVRyhi1+9N/EBYDi0FvESX6m/2a9DfwXxIi+BCk6F+4cc3i'
        b'/mAuP3Xozwxf/JXHEtT9qKD0RDHJ7c+CEjce9hs4wJ6NCgnDPZxcrq1yngS7eeo/CS9MBuQshEPojL9oPdmvNRiK6sdDkRQVRMhpNm90Ee0LdFZrQ7BY4MhJUiiHZkuV'
        b'GHR6IpSrKkPH3Wll2li+ohbnhcqhj6uKbO24LuhRUItyyMU7+FF7Ytt1wtYn0Mk3cH4KGQ4SyUW2jTrG4LlIUy0blGNK7+DiJBupwf4M1KRus38Q7WcXtZ3o3EJ/KHTE'
        b'XFHo3E20LFeP+T5iKyfaaHBotxf1nL3CiYqR/bFkWL225JoEZS0Tb0qWoWotA1s4RW9TksbMQNXE5OfxIzNuPEWrOJigc0pWlhE09N+6hIkOqsk9UaE/z8Vu00JHRltQ'
        b'OfOVWMyReE0hl9gBJVuXcPGN73fJlATBc+eL2JiQKck3pptvvbc5KOG5n9fc6Ay6tvDn33XyBmXczZs32sbaakZlSImTrZdvru5t2aiEyheG+V/Onujmnh5958XkO8HT'
        b'dfO23355SMmiu2+98qDnlSn33jtveC1oxcLO4BzzjdqH/F87an6p5qNXsj81vRzidy72hfkz2rVrp1VOGhnffWHGcMtgG83XJqY32F53arg7Yuby+dZb6883+3nGVPtn'
        b'Fqfd+lRR/1306CPlt1+3SnljivBZ/a2Or+4n5MZdj/wm7LV3khtR9e/ZO7U/DJMsCLE6tWTNqVebv9TY/UriG/OsUw8r91j/HjNu7+ITSRWBbyw4EpkKbwrr4ePEM5Va'
        b'jq93x/w6PvjGZ/E7BjdLFi68YGWakHp4+d0Pr2QPTvgd2S1VuDu8fqJi6cLE6oqsTsfXAu0ai656vdj7pd/PoUvDY96/Pi3slfADLa1Nd7q+X//pvtN74oLGuHk+6LBs'
        b'iSv3uLJ9WdmX9y4eXfPWB0E97878esSX98f+6LFusGKLTe+8+z8HrXjDOkZW3NXp/PPv5rNsnunUfDFk8BujlUsiLT6Sm3YLIw7fLtjvbO0S/Myy8Zvaq80vRH9z+vJb'
        b'jkVbrs3Ue8715c/zRp9x29lW2PZJ0NdF+1vjI96Kvv329X+Xzc/uu/HR6sxfmkOtTZ9rnqZ/csng8DFz+gpXrVhnudhry7GLO5y37jv0x9oPX2htyX2nz6PLZFJK4PJ9'
        b'B6pWOAh33yxEuzctsclY7uluutLCcqlX9+7NH90xe/WdqqtpVaOHv6dY+9O7NaF7+kJHm81/bdGhO7u6Pce4fz9Vr7h0zGfPLLc7eFkz+u32bX4h7z33o3bVrppQk5f/'
        b'bZIQ/Xb8W/dL50bf27/qHNp/+dqUEc2XNpZ8fG/EDxHfHq3ozFj62rM73zp/93Ozb70euKf/6BH0wjGPlzUvxkkmutxbP31RzDuxWrXG9YuTp3dETi89tPePX5yHnzXo'
        b'MP+3wiWduJkPWUvO2Ic2kVCNup9gFInlgiP0SF/iaa4ywlwFvRLA0kebdBHz9AXnM1USJfQmELVDz3Rb5l2mxxiaMYOV6muHDpuqWf654WIpo3EObxanRNEPTmpI47Dk'
        b'F76NCWjVE7BwAEeeZCCKJQ3m7qcTLhr1M94i1w1n9aSe0DWNylzQNAeVYI65yD/YkXk9X6xDec5UQ8wWF456aN2IWlEpNW/EJRzDldfCKRW7QjqPqyJMywiokKLOKFTE'
        b'ONB9yjXyQagSiyJFYhflxgLs1JEwm/C6ZXCU2JynKnhupL4sk4eDujbMgVcuXHIWDR+J+TmHzmtBEWMPC4ZvUG6ZJHriy8R5dDIF1II5wZ2Mr90TvUI0jETnMdOLBd+N'
        b'ULiW8djFcMoEtUM25ns1OGEhP0mGuulATAxHR1U89l7YjnnssFHMWrcYutezCY6GI2qGtMRZIZPUKlHpbOoikIjdF6ibuB2Qj/Yw4afM0ZBJFIuwLDrANSFUGjGBrTJl'
        b'er/7FTy4tVQowVJQOWPGy+yJqoLaP8IuVDrABYvhdMr2xkOvvJ9l7kRHGMtsOp72erQsSOXtKiCOSAjoLKqlTc9QQL2SxIgglqmo2EyCjvO4w3udmMFtHT74eslNQCFR'
        b'gaBCdEaCOnm0fws6TTNMXIuFD6fANJKDREnGUhQewkEmkjXhMaxnHVCaKMeNIsMmQ0UanJaeEA3HsKxJx3Yv2kF8FtulU/eIas4RpXhsqZVyD2aeG9ShFK6OT0JSdA9m'
        b'El6JUqE0jnwo4FLxFs4NZdTTgWqgSa4SbpVeTLxFh6GRLbvcjAgmxkIDnMeiLJZjoUST3cVA2ZB+95brnYmDS3RoAh2JsIQJqGBm8GMQKKMiRLkBHYATUOBP13OmuzSY'
        b'hyxX5joT9Q5DR0TTWXQQupiLxWBrNkYFesQ3HAFu4CXUpO4qdKYRNa7G414jVxMdqLDGc+YxePYqpNaoJZHV0op6oJmY/pLxi5mPidVLWJmaSXcU6DCLRwc1VG/V2J+R'
        b'5lJohn1QxySoXeiCA3TI4DAhVzzvxG+bToCASlAuKqNFha2itRB+B+1WV+C4oDNGSzSM9bGQTMGm5dBEbqTZbjvd80kGxmmJdBwM0SmlyMSkLGRMpianv0TiihqhjVo2'
        b'O6OW1f5itUQiVNcdQZ4MdaLWNLagTttCFSkrGHZjemgjdEVLk0isUGscHa3JUGtKHBZRoA1eUVUUbNPqrjD6/yhT/a8cF6k7JtJTGc+c+2vSVSKRcLSoyTH+XzAUzLB8'
        b'Y4ZlIBP8D8tAWBIyp2EOiPRjhIUCI0GLyl7DJRZpWErCKRPJUGpqbE7DIAjEoFgg/1PnQ7hMXZIWtCT6El1q8qyBpTFitmxEypSx4AlGvFRgNWpJtIQ/G/FSWUqUm5hB'
        b'yVv/SzNkUW6yGzCM7/0NS5WGp9sg0+YTYzDzxznv6TONID4VVqUz8TCCOFAgUZmpEx/q04d68knEP/o0RYvcPl11E9k+uZq5atpQkptEC0pbTn5MID9I8ME+7X77vz5N'
        b'0SyvT1fdXq5Pb4ClGrWMolY7dEDY+Jv+3908PLRVOoer9yTzsRKntPSlglRw4MespK6A+P/pT0FXoiuh6rf1PujQo3Ivzy2BnUPgmDQmcvrjbbzIuFO3N1x/IGrNfnsv'
        b'4an2XgNMP8jp5cg9au+1IChjHke9nDajw+4u49yM3ca7erijLnQqPT1tXWqGEm/TpzB31g5n8elwBjoMtHR19LX15KiY4I2gFCpC5mGWZ1+4jIM2OC+XE6f4TLFdB8dR'
        b'jjs9O6DXlXPFxfRQj/dwHA6bukuJN81kN84NOlJYbIcd+BxtdsfbzRSZO+eOd9wsmn0GZA1y1yC4lBXjuHFYHC/JMMCPpxnPcsdDNpj34DxiUC2NQgF549Ld8Qy7DRnP'
        b'jcfbczvTN/dgHrXFHY/rbLTHk/OE5mhW4XZ8ru511yQITxsvzssMKmgpqHWkBerAf0ywmsBNGI0aaTNQjjaUYwaZ41bJJ3IT5dDLOnPIHGrIiOL5nMHNWIYKaesgO0WT'
        b'qIfXbJ3JzZxsSusbjs5Cg5KoSVuSZ3Gz4Dw6R+uzhuNblLgrYRGzcQsb0WnWuvyFrkoZZWGz52DuoQpVUesYVIGF+FNKCblsh9K53FzodGWdLzGDcqUm+cLGh/PxWUOz'
        b'T0H7TIB0Bk7CCV/OF8pwOaR8I7TDgmhXiAbklB/n5wR7aIc8Uf0WIII4noA8f87fms0OHNPAzG0Haf0F5wAuALImMmOJPZgUSoA4FcPUUBeIx+FkAAv+UQw5kIWPexJq'
        b'akwQF+SAysSJXo2b3iEhXpjR6WAuOFiPPd+LDm6DDjIfpY7zuHmeeKaJBc5w2Ccn+nh7qJ7PzV+UyIahE5/B+XIpZU2aFnAL0M7ptBQLKEZNcoH6STgWwoXAvgxaCsr3'
        b'hkty3P7NklAuNDWQdXZYnJy0fA8cCOPCMDd5iQ5lDMofLCdjfywsnAtH+xLoU3O0HTXISbOLNi/kFsrtGV20o0ptOW407tQibpEh7GSPsybORAVkGOpXLOYWj0OVrNlH'
        b'8brAUiJpd1PEEm4JygunzZs8dSEqoKMesZRbGm4mjgh081AmI0Cyo06c03xxBCfAYXsoIyRQYeLMOeMFdZy20GqyNTFVsoR8K84KsoFRzBIPPEFlpOwL0GLP2WP5Yjuj'
        b'3VZUODEE938rKh7NjYbtQ2jplpgGa6FMk7pA7XHhXPjFrEuVhsRzClmKbZkOnIPLYtpy+XiUHYKbONF5DDfGBA4rHOjV0VZLK2KyoMQSX4E9QVCSy3MJZww1xM/CCTzS'
        b'lnT54LZdpO/wDwnakYar8TSGkzgTOoxaaZiWDViUJWWRYmgWzNbvFQsqw5sKlaPyY2S4BJqF50xGS1zhAn7du5RaIg7xx9RQ0F+GEXFXesoYtwe6x0Yze672LaiRtYPk'
        b'EDjjuSbG+LULKqBWNXiVbEc7WQksA9EEmfA4iyM6SZswYupIsQ5NVJfGGaPzEncz6HZdSK/x4LwOOs0q0BzFkQ/LoRq63fEux/yw6wxRtQ+3y5qbuZWNwqo5rH3Ho6PF'
        b'EbIU2ChWY2mvG4o0mV+bBtinQwvAmUZxtG9nvPH7LNRM65fOXmNPZ0GC6iZzpG+VqAy64/B2QCWF7JWwkzWfNEJzJWcA7aQL0D1oFO3eijmzaPPpazyCDYto74V57Kr1'
        b'WPxm8g4LSyfFeSBJMuGkF4OgiU4lqpPG0ueYCNuhHfWkESrMMUZNOFOGOx3qADi4lHWVZZmMd7qFrJixsJu21gFyWWvFAV3JCeGMIFB5PCOsoxI3ksHTu3/OWGsKaCaB'
        b'zUmh6yZa005oT2Pveoyg2x8KaGMzUBVRzKpIk+RBda5sUND5kbQlg/H5WKQaWJxlMjFPpQMDF9fQUoZjWaWkf2Q10ZE0AnfMYl1ONmJ2lmcNNFSDq2lFx8yC4KMPrKBD'
        b'Px/PMns3Q5x81OgC3Wtn0yZMztRmQ7qdjBchvAoJEM8d3TZwkBni1uNdqo02keaZzMpoT4Pu6atpI6FBQskvZUb/HBOLLzZc1pF0SGfwS2knduBFxwZFzEQHZIEZswlD'
        b'XXPYOt2ZRqgcFS6D7mgoo0Q6zwUvGnEZb0+j3XTBe283ykK59DIfzo7Ga50uMAln4imZitqh25ytYQPZRHG+JVhAw4SD+9LLJn2DnK2R7ejUPHEBkSyTudE6eCfA741o'
        b'9cOGSvv3IryAsdxWT9c4Frtz2CicQ5WRD6ebVOKaIpIM3jvpXGTgvesk2yMsebqOqlbjIUIttAnLoEZQLWL83Uos/a2l1KAzjtK2WfygfqKFHZPJMdbBSBtOon20Amev'
        b'OawJsJ10gYxhcQReqLPYAupBOcRjr71qR8VV9EIxK0M6nk13+zq8vxX0E9QMzGYWs5Fak8jorSSFWgbQ1zPpNMduxm04jsUKtjK65wLxleQAu0l4PS10UkA9Omj78Mjb'
        b'lJ8sSZtOje6CvAVOqlWKz4pI3fjlIcwS77UVupy5SS3PzYtMaNI1Zw+HYfHK0HC3BhcZGTBWawV7+PUEI85mtQ0+UiI36w/fxB4qR8g4rWX3iG5Ad9u4yezheisDbrgl'
        b'FlpcInW/zAhkD5eu0+B0bfV5zjIywGz+bPZw+LxBnGXAWQmXEpmwalAAe/iqk5wzGb5EwhlG6r61xoo9PKw04WxX18twRZvtFoi1v7zJjHNY1qWByxzutyiGC51zu3o/'
        b'+e/5abfd6X8PprHDefc4qCR7ChcXmIxXfbHIKCogG120J6fnfqv13HpoXcqMiekp0jAGZQ8gADi6Xpz/vJABFotSFbdOVlWcaLPI4lr1x7OKE7EYfbL4pOiY9apwVrrc'
        b'k8JZGeg8DGdF8HgajmH2QcQwlxoEBgYEQwU6hk4NsFJ8JDoYOgnVcm9oSqGjNcRwEXcq+t88ntWhz+v4cAod+vj9oRJOOk+TzGtCwqp0NrLO6ZgsFlUKhCw+DRKHe/I8'
        b'Lc4wZYQmIYtDYfHsYYOrMWfjsB93IHLydUcL9vDZKVJOa7ozT0wTf0wwZQ9vbMZkEb1AA5NFQMmqMexhdpAmp7voDUIWCfNXLmcPpycZcpbDpwmELDQ8xM/rFmKymPy1'
        b'FJNFgHNgAnuYG4XJIn24Jq5osn1cjOg9aQomi0hvCS5zGWgZYyE/dA59MdYCN2tRtQZpVpb3Wpb7qwxMmMvwSFtGOtwZN4Q9bJfhnDZniW2lbqJBJnu41Qs/3DyN0KBD'
        b'6gRd9tBrDH4Y+hN5qOvgsAJXFhQUfyP1J06Zjifv+2CXKQsCg028DU98ffO9m/dGVN68udys977cxDRgvI2fSerlZJuPTu3emw3yKisrp5Sqmd/Hj9PXLNsdd+t6/TfP'
        b'rf/2k+d/kngNec/EINxgFxy90Pz+prDvNx7W1x6qn3a1nhs8u3zeHFnY6/PmSiyuvPqs1+ZOw8OF+t1V0w3KvHJueO3s8MpVHHxOtuzZ0cuujItNkS10LVh77vf4N+eV'
        b'Bh+clWPy5W8+QRVepyemG40tbzOadO4b77jUryvGv7D6/Ker3IJKVxWet7j8wicLRmwB4Bs23ip43v+7CakNffcMb0+4HZLrUjz3B7NJQ/IDow7sGRYoD7q8Zvqwssar'
        b'SYsic+Wtmz9eeaD7yAnbhuv36lKOmE5++VxBo827bldDj7z3bKDO3Ssv/PBC+opquwvLvio9nqoI27R2/IwPmvf/klS0tvFlj7a7XgsKzm1Ns8+VfZc4zTt03RSnW74r'
        b'vO44l8wsKG++/m6Jjf/hzCWdQ9/Veq9K+kHJuzduLSstix/q9tKID375OHXnFIer41d8ml3R/NvII5+NMHH8dtrvScUbo68cOXBz6qc/vV2muNmQkPnR6RE3N7/y3ILm'
        b'D6Tn4jpuBmzLzf70VPSQRsWk8q9mjd2fOtl9a/MRwXPDZv+Cj0d6//ym3q1V73ceiVg0nvcEna+V9m82XnZ8Me7i+kKXVX1GH5ilzw26tmb2yfOOb4z6+urBlxbFvD3q'
        b'+r23Bxv2Vq77LnVEl/SDGJ2Wsy8svzCtsmHugXeqnp837a08SZLcyXDzm2PfqC/+4czcA5qXf+xscPnXzq7Z+s/euh0eNf3NYa3S6DFeWmu1v8n+LXhWovvME0tCj9ws'
        b'fqNyxSvlbhffqPv+2rDX7lzYHHG5a/CXoX2/a45+8d0XbeYq9OmVvByLBqfIFTHeKmScbDOPt4VeOOoF9UyZ0Yb2QzMUMGcVUlRq4sOjjgVoD73mNsRHDkFM4JPL39GO'
        b'5+B0ohwOSARohFb6uck4/HkH/telJH4p8tABHd4VmpAYe+MYqjG3hyLU6ifjpJZzo3nUsxBKRS1KKjrvH+zo6+vgK+Xs4Ix8HQnU0JZBWx0AnahLtMJjNnh4s76wAdXO'
        b'ZeqinmlDcLnOuEnShdCQwePN7/hqqvyI9razp0GVpOi8gDr4cFQDO5l26sIQ6jhfZYGHDgZNIAZ4FczDE5aFu2aJ6BcZl8braghwcQjU0gqN0CEo96d2PrhK+5TBPDoS'
        b'KWG+pnIs0SmqTkNdcUSj5s4M0zZbrx7o2skN7XGRxKFzroph/7e2O0++9tT8m7fLfTrKVVFJEfGJUXEx9JL5Ejn7/ooJzzYuUCp6n3j8Px2BeaTQocY4+pIx1Fs98XtB'
        b'TH7MqO8Kfeo5n/jFIMY7zPuFETH2kZjg39bUlwXxW29IjYUEagSkQ38T8yFb8RqbXVBLcX5D3olP+6T/YlPSJ4lPjFO7U/6Lw/Npv7UNKesCsbYhrtb/krVNFvecudrN'
        b'MWM5DhFB1T5o9nz1c17Gma2Qai1MGuBRuP/WkbiQUEM78iL8TIjV6fckLH2iJ2EGpVC7e9QV/x9492gR9PgbT6K4w3UKscJfxLVmP4prFf5Ul4xB3OrMiPfYqniBiwzQ'
        b'17XlmP1MDepNJozwQlv/yMkMIWnr4xviQ9anr4zz3KRh6zc9PtriskxJQNXyjVlfRvpEvRhrW3on8sWVq2Mjo22jAqLOy9fEJqy8G6lF4bLx2zXypNkKQbTkDYJWf5Wj'
        b'HA0rs8nCYMxhdTN/YIcgN0FuR7Rrj1fHr4NaFSjlMVfZffJVq2NWrY2g/B9dRC5/fRFt42xZqIiNIyOI9+wI4vPhoYmZWskqkubj1QhaGEC3t/vp9jP8l6mOGKv5L9Jt'
        b'FveVvjrlzqTbZLkr9ZLmg/aIfsr+BKAhMKhAKNJA+fjsyUMN6Gg40Wmay4lDPDjJhMoCqBvj7xC0BMt0RbBHymkMFXQMtOjd2IJwA1TC20NpkMAJg/CZVIBOMcnESxKd'
        b'KZC/IhM22szFPdxobOtj7x8QNHJREIknphUsKMMcGcPoJLc+yNlS4NJtfV1OSe7iFu8bGqKXkir50IlEYeIqDtKsmYtlm9+SGFJ8zahpI7gEMpwrHGQkxi7HzUlw+MDH'
        b'g/ueUxJB4ofuBSFhGZs6vs+UcBIZP3rT20qKSN7tfksgSNH0bfJnNWipg6w0VnzN4yIsI3W3bJVwNN+6/HdvyQiIOWmovo2+ktxK73TedutTYeFCjhvDmZ/8SUlGYIjs'
        b'QEiY3jq9FzJTQolAwJf/JijJKfVyWcwQV6o7Pm5LrD+MT0s+md5Mt2+KD2878O4Ng+e3r3V4Hq8STV5wG2lI6y3+eeUNQhLcJAfF7W/po/Gf3bmBKciO+7bMboYLfTSy'
        b'5tcCTCfLOcnN5Q5Haet6pYMLrnPjJ3Hcx1zO3gD6zCOqo+C6NOs4x93idq2zpFcMlklTocDXYeggslrcMaeMCgQ/lG1IWWcnpTRpoTjAq20cGD+9VC6zjBHow4QzwX5c'
        b'/KaJObyShJKwe2A/uzQ46FMX3StfHY0vm2qhu21ppL7rymfyZ7qAoB+5ffVo6Rurn0V7SwTr5O3r5frIe1GKeXjrFV/7t0PfjPv1wStJFm+MOmg/Y8GPb0q2P7daa6Pn'
        b'8CvNO1cLTgHjRpS+PN9VYb7WbseSjx80LbyekR/WJCnZe+7wt77OlvnDwgzWDL76w0Zz89U49f5+bsUfjs+fauzOObz5Gd+Tq698PPTVA1oJV898G6h/6ZPS8I0ePTFb'
        b'3g+6efdSdfqSax7Tht4PS/vYbsKGa5UBBv7D113RXtDx/r/GzW5/f/aomztPe1ZrmH32xdh3Vp/XsU0a/+Nip5ufHTr9e5DX8E9/vlQ0fnnOiHfMltx3P57ZuuHN6e+/'
        b'leL4sqXNgm3l737B2b611/ekb9y+zd2LDV/+cp//9VXnQ8G5r6TX1S256MUNtb9d8rk5a/bS3fnLPitfnuTvZdDe/VLQmuWxAZ4v/t55Y63VH14vN6efG/1+Ty3y3D73'
        b'SlLO0L7Sr12T4jfl3+60f2fsoTdmbbP7d+9HBgef3zpj5vxtFyt+/i68OSnxdfMbBaXN29LkkxeOfU0pfP3xtJz2qk9av1YYUtbPEnIX+CugEJ0xdbTV4DTiBDtUAp3M'
        b'YqN4OWokvBHs9mZgWi1UIiR7sBB1K0ypS+rCQAduIZzjpK48ak0YTlkqNyhfTpmwUKUvFBIknBaqE7aieh1mGNGNjsBeZfq6dXr6qMjAAF10g3bdVHxwwiEJqkHH/JiR'
        b'Sl4wCWxFuVKUD1mclPClqBrKGZvYhiqhHQ6hA1AQiFqJyXc2Pxe6MBdJmrd52yh7PygYRAELPKexQDBBRatZv3ZAh57IJKJcqOOkhE00EEMuol5omYz5S9Q1UuSIteUC'
        b'KsP/WMxU1AJ5cBZ/rhiyzpHYFmlECqMsoZhytc4JKfZOiuSZaoCVw/OZ0U4z7BqJi4U8X8hBNSQsrBydFqAGKpipEHSvQhX+voHQESoO9nIhBrUyP4voeCrZpfFBB8fg'
        b'FD3s8FHnB+fYp7XpqJAigWFfaoACT+MkwYSD7P9S2f5PDJsHMKEPjz66tVX9nfNzrL6MBmGijKY+ZiwN6XlKwi0Z8paUVSRMIwmXRBhOXeokjblZIzkJ66lBWUzCrBIm'
        b'k9iSC/gttSZnFg9i+YQdTbvTz17K+qQpUemr+6TRUelRfdpxMekR6fHpCTF/l+GUpH1ByvyS/Pi8/wgn9Zj87SP8awv1I5x6Zz1NPDoWOMN+fMKqneOanFmg1MQTtawS'
        b'RKZNqs4DEh6G6rz5WEm/swPhqZ414h7lAvvvz/q5QGmQgqf3o2GozMI/2NiA2PrQK05Mx0aoS4KXXLlf/Gd3/XklWWO1bVZfRqKAO5FfRAZE3Y3Rif0wgeeGtUlSzC6q'
        b'OUKRPNHMoE+PzMpA6rL7O9S1Ou1u/3xL2ex8OdBORZ0FEx6dRPJx2N+exBOG6pNIWFRUMVKBRVI8WEGOUAv56tM4eqYsFM5A6f9sHmMfnUfJn+ZREhQ/ytmDp6EoTE0+'
        b'+DKSzFBC7MpTxdE+UYz/HvmOxK9m0V+cJeV/N0tr0756dJa+eNosfTFwlsjHi/72LDUPmCUC20cnib+NIDZNqBpdGjBNUCuLhI7xj58mYjqUSyaKz5XGSv/JgpM8dqJ0'
        b'ghj/fXr0Un8HVDg56CH7nQxHKOe6w9RC2Cy9OkSS8tE2L4tMLfpw1nQJbmDWbKJUuB/jxG5lO5fxWHqrWq+FJypj6ziOsu+66EhmCDrBcb5QjY8SLOyO86G5z4VoYpnz'
        b'3ARNy8iAXWPDOOYVow1tz3SDEyGOUGnv4yvhNBYLPD6T6uLHDdaVKDNxFr/BlSP2XNAT5utK3/r161FDpx/JsdcUjGYUlB3crqV19+puX9vtSzZk9iXM6Zg982MoPbLb'
        b'7wfZivQThrZlfUFarVobnItub7g989sr01+9XF308qiEV+PtZcWf5r/8XHbkj8qM3v1rxt9cdq7gWvEHv3+e9kzUb5IqneEnlg1VaLErrjxUBMfsHWdgCZR4BUfVgmMK'
        b'yqLHpwM6NHJ6AGV0HnI5C9E5yg7EojoPb+KOBO9mmNsJJl4x9mBWAxUF0oITzaLgVNiAK7AN2nCRFjx6eTRq8XOHIgra3c0TZ+TWkYghgbei3SP6r7HIJdYRzCpdxJTV'
        b'xJC6lVHuSlRs70MvpaSePGpLWyt+uHcZtPipY1QpPhU1/Wkt4lXzVHOtPl2yj6ZEx0aQE48u0Kl/Z4EmkRsafRHqZU6PZyM+7Wu1RRtGapE+gpj6UzOFtHvkmzBVu2gR'
        b'S//20m0yUl+6lvjL1TNc2f7q44vPSjaWWM4tHAnZUmi0XjZgP9QWfyvNHok2Vy4p1y3XjBWihUKeXtoID70GxWpFS6Kl2Vo7+SXSGFm0LFojm4vWjNYqFJZo4LQ2TevQ'
        b'tCZOy2lal6a1cFqPpvVpWhunDWjakKZ1cHoQTRvRtBynjWnahKZ1cdqUps1oWg+nB9O0OU3r4/QQmh5K0wY4PYymh9O0IYmIh3s1ItoiW2vJoBhZLBczaCdXxC8ZhN+Q'
        b'CyptvGeNjLbEb42iregRYt2nGRiVRGwSf3EcEOOIBEazTGSvWNS3gTGQMGdIdubHb5NEYUZdMlE7PDq05GTT7t8wpU/cMCV0w5T+svM/htYa0MKHobWeFMiKrAgWS4v8'
        b'RUJmRbEi5s2aYxkbn/CYqFz91ERoWOtPm7ZVUIaCbEX7PKGGrmvDbSTeTrBjuAjnQicgz8GJ5+bymp5QEp1BoC+oNBx2ylNSQ/ArVb5QrVjUsE4vJRTyaAxl4nVrlaWW'
        b'7njopseCNapHF6g3HWhGuyUsgHKQBdup9zvpsujIqNLYXxUd2RV2UuV0KuxbZO8X6BRsSp2k2/Oc8VjiuL1jPS3YFBpQjr+bn8DxcHIFOsZhces07KdKWwN0YAreQGnk'
        b'bxdo5F1NBzHzm3Oobow/c6UP3QQCIU8WMNeaDx30FnUpapiATkfQzZXgfwsCiMd9qJXMQOVwjl5LmKGqGaib90cnfAKdHIlHfoNRkkU+g+hLd/1J7AZw+XziUlsLdQmb'
        b'oFzsT9JqKMEylR10okM4i0BvNND2UJRD+zNmbZroyQkVTBUD2c+EI3SghqGWdOaoAXZCl0SMO78ZuliEnH26cMKfOrYXVqDmUbwzPu32sEP5EpyYxpxioaqxMhrp+0jG'
        b'Wjb6ByQRDz1bWU2VUsdWwdBCj9akcDHwy7ofF78ZsoLF4EKtkGUBVdBEXWVxVqjHHDPb1GBhv3L2AHdV1FcV2hkjm0DC89Ii880kdKm5zMnXq5UbcMw3XCWUERsE4kJr'
        b'/RjiRItH3RNgFzNxOIAKzKLQoUecaElW4n2zlXZwpAuqJB60kqAp0FHlQauHGSvNinV61MWVo/RhJOp4xMxVoAKqocQ9jdAFlRPw1OjDYclyHzwU5F5pnosYUscMTP81'
        b'bCi7bPrCUDU+B9INTQezh6snqh7en31liQ17OHSKKkxP56KXDedx8aEHPhGUxDr7q7jBW0onLQAXw12ZMZfba3585+OM/OFZpZePHSq68pL+i1VDdMY2vPvhHEVkms7L'
        b'z68ZZTlTo/r7H9fafLV16KavChfWrDF7v3P6KU/nYR+01M1JnvjusCjT9Rdujs4ecelI8IykZ575IanJN8dDs3zR/cVvPFB0nH3VauxnffOCvYyDcpRRo5b9dKutdebz'
        b'v1U9qNJ0HexqMPr7nLkmG4tiYv7lXgeS8SPHpf900G3K+hSfUcO+eBvVf3xv1mvlYwM+cXjtVWH5kmNjxzUtblryqWub0/unAosuLF8QWHPEvm7IjQWrLTItbqBvar4/'
        b't+Rb+99v7P/S74sla57vOBpVmXJ2xTf5evdy747pOnG53eSa/OzrQSNDH7xcWe0Yprx2sfO7107vq1zxyzvt0fohK/5of31s5S/PfvvZiwtqF1de//aVl5ctXPDWgl6H'
        b'aymVjt8Xxyy/ukX2R8HiGO2vrbb9Ij13pcwyYY9iKL1uMUdNq+iehkrHiuwKnFvHIHXH8fLc7x9g50Tew2nMYcgTBDiKalA+zTAanRLh/wXQOI6qBkjQ6C2oCfWKId+9'
        b'NtIYKAKqUA+DItWKkKczOQqdnP9Y1B3aDjVSOMnDccqtBaK8pURT4+gnUwRKKL+Ml1Ypu6E5DdnORKKmoeMDJ6MDeKtSCv+Pt++Aqyq79r6F3psCioLY6CLYQEERBaQq'
        b'xV64dJAmRREbSK/Se29KkS5YQCZrvSST+pKZZJLMS3kz7yUzmUnvmSQv39r7XK6g6MyY977wywj3nnP2Pnuv8l9lr4Utm3BcKITSkCSPIEouX4ZBsQcMGfMzMClQj/d5'
        b'p5MAfOiwKDlXY4eS67b1fHniNOKgLMjJF0qwWCKSJoqP00oN8yldh+oUXnfVf6c6K/nQKYYqvGcquH1yYrAgXfxcKxLMN+VVMfxhxp2HnUhwPrqhkJ0Gu6XQjV04JrzV'
        b'XBBdFESiMwV65NLT4JoUZqE5nF8QT7zYxifAoigB/jBGr32MXhsrznMEfMpxDevsQEKUbPpZfCIRaW6WYBdB4Ef8BY4Fetnysg438cliZYcIEA4FrtY4ikPWirKy/Kyb'
        b'rro0A3KChUOB9Xbx/Fu7s7vZWTYVNYkpTKTxVdXZF8V2o3gbVKctCiID7GfJW5WH+NN345ASP4PmG2CPZfE0byIbnIURIizuyiuB23vhKQnDsiB5wT6RjqfUizRfhhX7'
        b'vjZZT7DrFkWWYdaSunyiA5mq+jgDVUJhmOow/cgk3hBnUefqxEpd4Q428HU0NaTh2Eatd1OINIM9UpiLhWnheNMwDPIzcz5HsPMZHDXQkcKAPdy2Vn65K0n9dY9jKNod'
        b'jH8eWH9LpKHBQb0WD9+qiQVPHDsXxNuj8x9WS0GDB4SZV01FrKVkxE8IafBGCIufCj9aEj0eGP4812uIs/XkUPP5Lgfyk0U/X+4LUPvMTkqJcKvNsmVK/dzmRo3Z0rNE'
        b'L0z2s1Zv/6HolXXGv6Gx2MpAMYKii4El7x0gh7TP6um/TtsCeQls1Qvp8bHJr2wk8K3FCQnDLzYSYPfJMjLTPmc5cHknAaULEU4Rrxj0bcWgVl6JsliL+BiL+AyhrexB'
        b'p4OKNXidgvbHXr3+7yhGNuOlvtOio+IzUtI+d6sG+WhvvLovxA8Uo62XjyZ0Z/j8bydfWPULSSlR8THxr9zSHypG3cqL9svSMyyE2yJfd/jYxeGjs6IjM1/dmuIniuE3'
        b'KYYXbnu9sWMWaZkfjnvVyO8rRrZZJKuMJSxF9CU84jXHj4qOIFJ5xfg/VYxvznmJX/8v9Q5Qv7BIoa8Y9kPFsBuW0fRrDawgtEU/0isG/lgx8OalljVb80Wzevng8rG5'
        b'Ens+kUWsSGQRFYvyRDfE2SrXRdxBIOYOAtFN8UoeVfaoFz2qai9JmvkcpeClXIwqfXJyxZbRnL6uxEXzvtoZcaxh+TMqS4sW+kfwvtbJKRkv+haW+RcWt+MF731HioOU'
        b'V/qvmPx3Vun/W998Vun/kz9Yy8tP3HG4xdHqUqiKQ1eVXKFY6yU16C8sHlfmnX4+O5C4JVLNNl/UW4q3fJYJExMbnRH42QvTs2n8WkN+evMzK+ocUe3SAvWZTCHCNDQQ'
        b'xp1iYA4ehBOew3pbxZJg9fPZMELm4LyKJsxDg/L/XVDmxRQr2tbKI7NSHpRpL6xhQZmEmF+El8d+OZsHZWh7LWelA5fX0vYKZf18sfGF/Q3FPCVXH+j+tKBNWvhr77Tm'
        b'q3c6PTpjGXxLWr7by0M5z65QTOpPr7Hv5cuCOQzm4cgm7BS2XWXfp+46WQds1200scR0jbVQ6F4Xenf7HVPjBKGkK4a7OKEt1MsqMoFhP+y4yu9SchbT0/qgK94565qE'
        b'R4KGZ/IuxvpE+sv8ZQnv3YuOi42L9Y/0lQXKxL8zuWiSYHLqVsjJDxyVnVNnRKLxR2q/zy55IT9t5Vy1tBNyyhHKh32eTZNqqepIsvVf2LjFkVfcoOdG/tVr7Ezd0qS0'
        b'FcZfWRrzeJpQu1+kiKd9mkyOIZkc8IJA9WQ5eOmCxicJvNw7nG6RnhGfmGhxWZYYH/UKR69YtJIuUQkM9eLet5EN10Rq9qxfmsXlk3b6a+JXBX1bms7uvptS+HH4NyOs'
        b'fuYr04r5kH77b5lVg+gt/8NO1v7h+jHrCy3dLL4R3Ke6SmY9Lhocif4wfEj2YXhijM3vBmVvRiTFiEodoyZ2On/H0Yf+vesYO2W0OffB3T/kfP1niWLRf8YY/1R7o7Wa'
        b'UKjkNo642T6Lf0ArVIl0YEbqDQvXhEyaQRjRs5W7PcQiNZddzCXMAkr86x0nsF+eY8n9q5P4mPlYN+KoYGTXwl112yXCxtD5BPMZm0IFD4KZqcP9Z55bY6jkztuDmkJS'
        b'dt2RZMGWVjpyiDWNCEoWMlp64Cnm2hIrHoERJZFKoi02SSwNdIT8nTJ8Ao/86Bs7FZESy+AxE8MkVCgvaoxPi3qpxadf4DvLWebQ52UZQxWe88z/z7Oh1VhZjCUW4OLj'
        b'X6bYVpzfMj2nRjP722twVZHBiiapYkLWhivVtVhSwIKH4I6zRZKSQZbGkiXTfsDqWagtmhHvqi0i+ndVBHD8roqAW99VWwSS76otYkEuH/jrCGvxrzeFXCJ7fkMTu8hW'
        b'yZ/+UlNSElud/dfLSuhoakkEH/WMPlH9VJiGwt+jAZUSeIJzULFMZRvI/02//XzcUKXOpE4UJalg0TTVIu0igyLDGOXPHi8U7iIsoRmlla/G4oUxomg1HqFTY8+O0q4Q'
        b'81RyTXquUpROlC5/rrriO2XCrXpR+vxTDT4bkyiDCknUJn6PAb/LKGpVvjp9r0nfi9gVdar0YxK1ukIlajMvkKEs74+iXaRTpFekX2RYZBKjFWUatYbfpyU8l37U6tRp'
        b'rmsrpFFbeIxUmQfyWCMfnSJdNlqRUdGqotVFxnS/XpRZ1Dp+v7b8fn53nWrUerp/Kx+T3anL71pNd6jzSCS7Q4e/3wb2fvQGkijLqI38DXWjDDnWt3pXR0749I8sNjrt'
        b'vR20McuEuIfF8iuY5Kd/0y1kJPSXqgIWOpRlWMjSmH/lUmY8EfiyB8UQXufXR9FXkRnMgovPsMhIkyWnyyKZ+Zr+XITxSAaplpQ0+VCKUWTpCgOIdFKyhcwiNv5ydLL8'
        b'sSlpV597jIODxRVZGuuE5ur6YgiT2VbPvaBCpR08HOrhYHEoJXlrhkVmejR/g9S0lKhMPt0Ny4O2ck9ZEIvcSuVkvuw8A6+ioqigwrZdUUVFWix96UkGedT2vdPPbwxf'
        b'oucCt4taOWnxVV4rdqtYSWaE0XYuXf4VrS2253yrohwsjnB3U1QKzYisM4vorPj0DPbJFbaiEXI/TfQKSEE+IblhLczpBXP7SjybJH0Tk0mPk0VFEXm8ZE7JUfR/C1lq'
        b'akp8Mg241B31CpiyDEMpYIp2YKYbBwhK2L20eGmEqY8iLIc1WOHPC40G+/gHLhYfgwUs0sT+DJwROtEUucLjpU94dj/dhcPYIXe+X8Yi9RuHQ3go1GknTmAtQWUfJZHy'
        b'VsjFejE2QTnM8qO+6l5Qw076ZgVBrygL7mABl8n7CX3Mh9jjAE5iv3qik0jqINLdJ9mE4zCayRwMNH49Fi3tyWXFUM9R+qRO6MW121oZqvEezvESG4ZQt9ZWwrpG5x8R'
        b'pbuncdgWriURTbtq8t9OHwsQ8VKsOJgFQ8/ilcFYzPt9VdhhZQAv3LoW74mOpahiDuRhPrcUwmFCPx2qzl1iBU/uiKD0JNbEH5n8uSj9C/Ttgx0Th++46ICj3uF/7rm0'
        b'yyLRwKC4N1X9gMR1jfGbPh6WdYGGuz2lf37fsS13Ym2p6T/2f22qSPbtd3Sd/ntwa2HYL0+3lTo8KAk4dS37o3s7L9ZmfXfDY7uMd4s+3Gcl2aqz5Y8fzX/4ZrV9+er1'
        b'q9Xmf6O+UWvm++/l/0xv1m/rH/+0OUV969f/8J1Eyw3GYGNgo7u3yiS7KaIk8B/Wub/4zs5Ht/KPfuknCd/85kbVr+ws2hcTEb11duzrgb/8euj55LpPfhh+53e/k8oM'
        b'9iWpDVsb8UylizIs4oF/vE/wUhIh3g7tZ4WqdIM+UMsDd0JIDquyFwN3hlAoRLgaM3B2sZvStjghBI+D8pLiMKaL+UtSoHroZxT7DPmt5ngf5hfDiqKsVCGqGIDF/FtX'
        b'fLRnWYoUdm2BCaxUk5dQxAlo9cM5HBOSLqxVROpGEujeA/n8gmBsNcAy0vyBARnHacdtVAgzT0uPQR8IBQmjMB+bbbdhKQMGKnAvHQoldobnOGI+zKJnZfAQe3hMUxHQ'
        b'tDMRUruqT3kSYPYnG3GDGFroke2qe3mY0F090fZZt4M9CRJnfIRC73lr7AwXwmwsiMpaJrDj4vYqImOYUfJJgza+YLF4l3D7YmhJxdB/p0QbK6GPb4cd9t1gFQD9Dm5h'
        b'NfaEielDoxTuQK7QEBznN/mxYBnLJ5yBYoHbdUKkAbiAMxnMF5YZaINl++P5WVOWcM4PCUHlNj97XvWRVa3whglVuGMGQ3wjDKAgY0nDCzFtyTS04pAPn9MOgvIDQhlF'
        b'fgAzH3sWyyj6YgMPc5po4D12WImGEcaLhjmsVBGtpsctwIDLi+lknyU9e6UgWejntQRcGGxU4anoOjypXIv3CWfp6Ou5XSCEs7KNlyvjl3TtVqjaJabCK4KCUuHaFUJZ'
        b'a0l0pbt+PsshR/TB0gOOL53yZw0kKX+aK3if5mJc6/mhFOEtZ4UGf1FlL1HP/0qb7rdErwzH7Nf8HI7yRW27zFftKAAkBoykn9Fbnf//zVudTxAscyUIxv63zGGdFp2U'
        b'kqHoakxYMi4lMzGKQZ/L0WncLrSQxcoYMlvxWYr8O8/EaFkaa5V7SAHH5B5vDo3iBejH/C6ZzA2z4sPSozMYpAsPD03LjA4PXwza2FxMSc5I4UcrbSwS4yPSZPRwFiG8'
        b'LItPlEUkRr8UUWUoGlUv7ivdlpIWHxufzFAdw+Pe0WlEeVftLFLYclyJT1/5aUJMUjFBL1liOs3wdb35U7IMwZs/+1s95s1X4+ck1OLPDIjftrxlLeZpBZmG8JiJR292'
        b'BhMWJbJcPK72/l/351/I3vIcv6ZHJl7gy/4vufU9X0toLSxz7B+muw+7Y5Pg32Xe3QfsF/8ge6yxDVyyPNgAU2LzFTz8Jut13LA+/hXZ/Nz3WCT+zNn8n+EQtVIgLxkD'
        b'NfvYabnlqpXlfJb42/jaJWIJDIUKGaDssyB/lsoDw1Ci6eITEB/x9beV0plb5w+Vfh+HOxj8PPzrEf8pu1RhZWAt85cl8hPUH4Ynx/wivDTWVyZQUuv31dy/+Ia1lJd0'
        b'PgFNMP/86LcsVlLt3tgqnLCulmL+srQrX+xbWu+8GHs5jYrxkQfRqIlu4IskegOqFsMCr1bTisDE5/ZxR7Asls9Etp8So1ghcX2FQEXAa1Hyg2XJ695097Hz0PCZKBnq'
        b'yOh5MW5hclDnCN6JsJbw6MRmaEnDZrjt9yxwASXYzLNZtXH+JLZt9lsSuGiEwviPoiulvESCtf6XnwtcWB6MTYz1jQzkwQtTFryQhy5iRKIv2qnLyn/7YujiFUEn2Wvv'
        b'7QktDT2lbJOX7e2LYYxPmcXB19q8N5bGmV4+GxJ6zMG6snRhC80y8km6KJN8UVbIF+krk99Jh38y8IKC8SYVJFvER0sdWi93miSlRccIDooXMopW8GukRWdkpiWnu1p4'
        b'KLrcy9863CIlIoF0+yv8ESuDGuXATLb9IUcdsczphpzuw46esD9+YsU0ecjZoZ6ARVDG7fMUK8wVzHMxdj5zXSwz0UXBmqpYAZPQHP/2ritK6QFsHju//XH4L8I/Cv9K'
        b'RFzMUDSLxbwZMSKLi7E7bi3zFX+1WPyDgPJ1WhYTp7+05kt2MV2nG+x+lvgzy7vdfQbvGG2pStSOdJTGqohyD+tvhlBrFW7HbYQ5JTJbYRYKFad3XHYKwRaa/AF5sivZ'
        b'X5txVLANgy4Lfa7CrzGDeRu0Wy/PdHXZl8H8Ip7YH8eN7ROa3NTW0M+Q1+frxtt+3EMDnQ7cbNM8LcHRi978yHUyLOx6IT+W2L9QLqlXWy7j1JdbHUvrY7CzQ3JS4bzr'
        b'+nl5N1XIJ1TjXZuy1zzHNUsevzzvL2y5UF45miIRLnuGMUxojqGvxdyjRkuZ+xXTXJmvX8hWeRViWIxXPliRozNezBFKiVk8l/J/z+AewpifgcHFK+IcgrTfcPqjJJ1B'
        b'gr96//pjgigfhsfFjETfk7159fsRWjyXweYTpa3jCdYSDhxUDmM3P8Alz7olOp9lDpc12K6UrblK4KhK7PP0y4KnQory4hkPLHFYhJorR641X1vn3BKx7NSVCEG+K6+k'
        b'V/FLCJTNJ+q1CLRD59MIVD4v+aDvqqbLLkdfkKUHruzUZ1mwcj2kwi1Xlc/h0o9YyZ5cJF4W44iS19v/TKTroYjHRGfIWCqgTEiXSkq5TIqNVchffO7/Ft0L98gXyJV5'
        b'/nkkxo7ZdkmZ6RnM5hX4MD2D2YcsRZH5KFa08QS/xbL0NmYf0sNXihUoWI7NNU12RVgueudXcBojNL0XOE0jMJPXh28yI31TtkyVQrvTy7Wpf6xw5ihfBQd0jtqyg14+'
        b'IqzfjbO8MI2GuzeraDP5QDtVSaTULM7I3CucMrJRvvlnoTSM1rT0qig0bZ6ogPvAXQ4Cq1pRaBtEzwoWYUsKdManWjVL0gvo2+qvOQaUd+scPKbl+eRXbucdlZS/8HvP'
        b'HFFum0Vtzg932m1Kz3raoKnx9g63n1vXfedDn111rmcl1rO/bN+yefjH5sFaJrVjh2v1vnfov/QL1/1pz4YPU2zyBrW/4ry2tfCTuEjfkNa/2rlu3/foC1fUC0f/9qTw'
        b'4yfZ737n/tc6MzUG1P5nXvXr28wnzm2yvmgjPyIcB604ZesDc1j77MxtxiVBxgydJmOGa23o9H/m0fVxEBzdD+HOdewKXuLrXtTb0KrGnb4mB/EeK0hitej3bcdpV0F3'
        b't1liia2NAxbDgjNvjqm+VwKdMIgPhXyucm/zK7eW+34X/b7px4Tp9W7ZxZzd0O635EgwzfW2PGFCGYttt5EJN6fwV0vsIC/uJbpT5bO6Tt9VlZ8f5nLU5/PLUT0teT0O'
        b'A57xb8DPGmiJjcTZq1eQYjTQco8pl6BrJJ8BDkiXXPtM5JrRnymvJXJrVy8VuS+ZLC1k0OK55nfVFQnyQk6EuoSdjE6UJceGekWqyrmZvYbBIjcHMjHMTsMy96EGD4ez'
        b'ELykSLdIr0hapC+PuhrEGMjFs2qxOolnNRLPqlw8q3HxrHpTbYl4vqm0gnj2iIpimfTJ0VeW50Ex55gQ2hQisZEpaWnR6akpyVHMhffyg7AkNF1lGRlpruEK0yd8mWNM'
        b'8NzZyf1lChcii7W/8DDZS2PrFpGyZCaO01JYOspiInGGLI3W3yJClnzx5TphWUD2OUi1Yjj2pZriVdqFLQSLF6enRkfyN7QTVnlFXfHs/EZyZlJEdNpnDi4rCEuYxrOD'
        b'GFfi4iPjlikt/kbJsqSVvZcpgiN1cR3iUhKjiJiXqMDncuOTZGkXn8uHUGxauoVwkMTBImjRYyrcHp0RlxJl4RqTmRxJ5EHXLKLn8BUftDj7SFliYjRzOMekyDWq4rC5'
        b'QASZLE2fJTPIVnzOUhp66Uoqsg9dLZ4/ZfIsQ3tx3JdlasufFeEU8eJTlp5V+ZT7mWQg+BESZLHL2cV+O/87k6QLMWFU9OJWLT6LSF+gkpVdzYeiY2SZiRnpiyyieNaK'
        b'O7413YL/yZJOXpjcMowip0z2KqlkIdBvnwFhKaALq0K35gXoYhPIXVJGh6EzHQZwwSmNgEOKiGzpOhwU8mxLN8GgJhQfv3xJLBJjsQjboABbrMW8bUq8Cc7YYtchMoXF'
        b'IglUij1PQTd3LGCesUzz8qVjAvCxcrC3wuJtNkcCCAMNhabiZMZxliFgeVEigjob9T1e2MxTCnS8sH9pcgMunPURTI1gn8VThZHn1aD7oAcHQ72sGLdIZJWaHq/1Tka4'
        b'KJMdNcR+Q17bv9wWOk8vZiYIKZd21va+yiI3WxVssc8Q+ruMwl2tLMJMWKMiEuuLoONIIn90ThSrvSLSO3Drlt0H2vKa3LpbhAPQFtei/E+ayIQPd16XcGgosk30jzQ/'
        b'IuJNTA6Eb8BeKL/OaxxqrsV7vFgXv/4XmWoMRjqKVl21y/BRE2qYr4Kn+ryMQIgPdwsfoXmX2zLgqMiuoC987Hz9HY4Q5smLUSGoYa11CSexLXOniB/zLsfW5wCoD2Ek'
        b'kwzfAH8YDPVRRN/JYHukDr0q0OdlrcYp4DgMmAiB42Mmi8fvD94UWuMUwjjO+MHYVvkJfPE2lzWcNkJxHFqEw/fZHvKz9yJoEJoYFGPx7men75VgAGb4+XstE+HgfgG0'
        b'QK5wLH6Tr/xY/PEt/N7Vey88OxB/BUflZ+JpTwv5kfrQ/djLzsRDN5QrDsVnwoPMjezBxSfZZi4/Fk+/ae2WH4s/omWtKbRBrsT8VXzJYQIa5ZUbYO6UUEkhH+fgrpCo'
        b'i8NhiuINISA/ud+JlcDT2fVgeHn9hjJD/oYa2Al9fqlYKC/hwNq9TGMBx/zu17HXD4t15CUcxNs9ffk9bvZH5dUbxDiwRyjeECUfEaZNVi8t3KANd+S1GzAvlhdgsN0A'
        b'E4rsX5x3EUo3YDM0Cq/UTlzdJ2QXh+LMswIOndt4klBcXPSzlBss3yCvEnDVkU/tZKovK+5gBsNL7H4rMacec00oZ4lCwfZQlaIikkaL92LFCb7Im4M2hJD5UxV21F7l'
        b'DHayypzQoQGtnLRSLaCbgfyTWBukJJJoiXDBPdlag5eqkMSrpOukZeIEVGhr4YQulOJsBi1xgvTIHlgQakVNwchp4aLFK9JxOhNq05jTYkCK7f4wK1yZD7X6S6+8knFJ'
        b'PU1bB3sMVERWUiW8jS2beBEbG6KXSpzKxOn0S3AP6rQuQYVuWqZUZGgm3R2Gubz5NZkgFRvTL2Vq8GfpGsAoPlDHCRqbXS7MQlm0/7yKclgif+otnIIF4Qa8f1QxU2WR'
        b'YbTUAyodeZU5FW0oZtdArv/SOaqI1sOo0hYteRehSMxVkT8p10hYlTScpvkdlroaYq/QNaY+GBcU87sigRwSuCoiPRUJSbsZyBMqKndDFTZo4kwGzuLU3nQtdW1aN+2b'
        b'ElbUN1VeuyLrLO3e0aO0eZAfIlLGR2KoXneAp4cp0a0hAVgdghVYHwIVKhtZDdMWMWmEbIFgH2RDifD8WzC+7PlDrpxuklWwLR1ndNNg1lRZJMEBsY0llnNpRi/GFEEZ'
        b'iUG/bQH+QWFMXQQzbXIR7pAlbcdkYvkRfywlEwtuh6mn34QiLtA3H7p2Cjv8WOl2sasI61g3UT6fGNb0YcqHRAOMB/vZExsFKon0oU0KDbrruWBeFbpGtEMkUvvN0UvX'
        b'N27bJEjrT6xtRKH0od7WLMmmbftFQucQ0V/2y3+xOmCtJGiSaXb4HYYjsY/+uiq66oFdnNvVcZzWfRi7/UlLZIuyI6BPaHVWCSNQbKt3neXeibLUnHmWXJafHZap4QRT'
        b'r6L4lEu8xsav1wg1Nr5ll273C8ttQuGNu0qCMsrZkaDV4+QsfPgdH+HDcIe4xB9E6Qgfem8WPjwqifb/635NUfybOU7idFaE6l3Zl5KC9yav3a63Lu3EWzf7/xg0mfiD'
        b'hn/+dZeXr7HLwfeViqUPzfaIlNXg3QpxcqSl6Nz3vy0+q+RyqNQi9s1jwX2+zd6/GvKbmPr9z9x0ipwjr5V+1dC2PueXVj/ft7Zu4+qppAazH35tuPbjHE/jX9fqz0rO'
        b'Z/1xzUSDt/Lbmxy2JUZobnzo1v07ydkvp5s+vPf3iwW/HFzt7XWzOazvyAPtQZ2nbx7dnNij/GXP/x7tOzf5bcklp5ywiQavh98f3NucmpCfev6rzV+dduz5wqMNHrtO'
        b'nPuLm6fDJ7lNP37LtN3wg8CvqV/Z79f4N4ep5qQffL34iKNxtPGqP1//YtK/XRtynNSoGj7q5+ooKT1x1GjXRVe9oejQ9QfP5Ox9u/v0Fy4e1/7GF3/hVvvLd0Wn3gk1'
        b'1+p5EP3+ZvN1WbZz5/58+cNfFs62/rhy7kfv//TLav9Y/5dBn3ubpw181dvzfd9Zc/6q//Dx9omE78Uey234Qcr5+zd+9LTuhqQ226zne+vOD//6nXXuJjX/9d66DoMd'
        b'b9laWqV2Vv7l3nsb3VUuLIz88m93XHo170U4xKa0aHzPzdB04p5Z2/vuH+zL8h8ycav9qXSs1/Y/9uUP/eZR5I8PJB+8YLj2wG/rf/QoZe5U/y6V/4mOfBD5ocPMb/94'
        b'8q5nS4beP/IelSee/ffo7P9MPtQZufun/xy8+vHoF1bvPR7tmn7tw38+abz3nscbQd/p+GZW65U9u2X10l9H1n75L+a/yTow97Vrc7d+Au9s/ujoB206/5gRr3tU8bsf'
        b'X3IrU3H7tv0Hf63I/mjX0EfZ/2z+VcST28Odu3X2X3kz6Zd/sOr72Lg2an3dfiX1hECH7/wk5ecbA3766Gt/fyta2jnf+5e39we89dsvvllo7cAz6zAHpuG2EFTFtpuK'
        b'6LTBESl00Vej/KTKGqy09RM9wxvrsYdnp2E7luI4L5atl8Yy4YL4JfpYJIXyK9DB0+rOEiJqUTiH4qyfuYfW4BxP3JOk4cPFNEjsIqXEEyG9vPgMoR/nTvPMPX24/2Lq'
        b'Hso7kw8E88Ns/tDLSpcIPqZWJ6GW7l2cwT4ht/A0PJTXpiW98JSHh0JYu8ZlHia8h03PvEwwwJ+yH6fwCfDScwT+sP2yUNEuDbuEbM0WZ1ywDQzACijDNhWR0g4xDJ6A'
        b'dj67TEuYF9Il1S8sOqAGoUdev/b6s44PUWFy95VKGnde+eJ9VuO9zNqeJUM0C/V24Z68xN4OqL/kZ0vKrtzPB8pVRCpXJZvwKbYKdWP6rSS8zu8RHPNdUogYy2GSO+V2'
        b'QkscTy89cEbu74MOSyEv9d4lKPXj6NRPR5EdCqPbhTdth9vwEMuS1MiSUCUro0ccBuVQI6R3DsCsEg/ZNygTAmWnmiI1uSfv0qUQLLMjBAmTWEN3YmmAHcGHbVKsj8EK'
        b'IQGz9jI89VNkWsMclAuBPEIlQmFACe3alB99ka9AamsC+KysYIIpKIaY7WBgETJH+QtrXLGDZXkz2Ikl0C6HxmdCBf9hATboLkHGels5LoaGVULpkyKCztUCMIYn0CqH'
        b'xjiGNcL3BUbY+AweG59brBjVlClUeSkMPs/BcftxBTZ2gDsZDAbhQxy+uQI2hvJ9cnCM9fHC0rRl8WJXvkIQ04J1ktfFHGkKdkGZ4OcspA0sYoWQtwXZp1tLGHXaEMWW'
        b'ZGzhXASVbO3swjiS4ijqEj7QxnGxE9wW22GPsvq2q8JQj4hEuvz4FpHWb2fbpIYtEii1xA6+lUE4CAtC1Uc7cz8o2XaENxBf66UE7ZeUhEWtJlvkNq8p6XtiJ/GRSBW7'
        b'JWq3oI8LFJz3wXnSwNMbBQ2MY+f4k1V9CK2wojRE1J2KIrqGG6VYeQO7uTwIIAofEwrXQAMOOARgKYF+Gh2blAhaTMTz2BneobUQLguyI2iBo1toiyQi451K++HhLd4U'
        b'3BKfYMtiadNnZU2jME9e2fR8rJAv/ej6Gl4Cs5RXxsEqNZEmVEiwG7ocOHntiSZAwfzjdA1xFy19oMQM5kMFD/Z0AOtdw7OpWS41seKYPJ8aq7z4AGm6+BindC/LI9MD'
        b'WEMQZVBC4m4ofbHtS8VO2hB7ax2ctWJUFCuBSRsta91//UTZMzfx/2EX8aWRc1lU1LLI+UcMtH0+z/kuLd7HW4U3S1msjC2kHbP61yZiA4mOIjFZTSLh1a8l8oRk+u25'
        b'Ji8aUiXx0h8dqRp/EhtFQyw4u9V4FW0l7qPX4PV8WI1tPT4HHbGOxIAfilxs+LKGV/fR4UnROrzyth6P868QOV2yHHL/vrrgpFd4z9PWMce9wm+etn65z/9fq3OuKk+6'
        b'VjyYj8gHs1GMzeMFlvRbqaa8YOXnihfkiP7i8Kog7ZIlsJa+q7YYI312HjNSSYD2IhWR4DHjXjPWY5qHAYQwgbo8TCDmgQIWJpAU6RcZFEmLDGMM5UECpWKVPNEN5WwV'
        b'Fr0NEV1X5kECpZvKzypYvBciWSFIEJYqT7xeHiPg3nKZ3NurCO6+3PO+eMXy81kZcsf1kkfYyf3XkbLkFZ2aESw+YcF7HDEH5MujEa/jqGehjxVHtVmcno0FP4PFfaqL'
        b'8xA85MKUWLiDpp4seKVXdpJbeKZERTu7WETI0rhXV3jhtOjUtOj0aP7szxe05gsoj2k8X5ZppWAEPX7l1GS5q3vR0c9865/mC/48nl/Ws0hX9Lzn1zwwk2UeeEL+Zb9n'
        b'ndyPPUsAwxy3F6LWldbqhEPybnEPr4v6Ie5jlTsnsSbch7kdsTgoZJmzNRvvqkMFtGKj0H75CZZaHY5ShLvPOXMrW9lYU9Tn78Caz/g/PHdVaD4T8ZOEEO3B06mXpLz5'
        b'TI0LTzrGCl8ctIV7DD0X450Q5iIN8Ofa9MRiAq8ie3e5o0Aaloj12jigLhY6Rw+dPsN7fgekYC5p+oUooZTAX1f/TaQnEZmMO40oL4SczxQs/e83HwjlXztvPSP6oUjk'
        b'eGDn3PptQSbbha+9eoReotJVCeJUuyFlMsGv/f2ko4iPZExg6SlrFu+ETzaKnHSgg/cGupKIncvc3cWsjmwt8/QSPDwi957zHk5+x3x87XyFynw4S3ijVEXbF3IlmSyV'
        b'0ULGmjq/NItvEzxYnnoAxTBnLTTWctiEVULZZgYnptYtbSMwZy8UUi3GkZuCK/QC9ipcoR4XBL9ztyXMrOB2FpzOVtCarKh2ALnwVP0GkMnAV+onByUivXOMPsMTjx6z'
        b'kHtWDiQI6/im9nHRNL3aAbdyU99dXz2u6NjKHenWyoLPZeEo1sIw/XYVZmFadBUngrkXJRiapTDM0F6Mtig77qTQ/b0D6zGfH3XcindFWVCRKLQzn3XGXGRtzuNxAG6L'
        b'4o9AJfeontkMIwziYh0OEBmVkZ21SwxjkHdKXln1Ej5+rqwqFoZLzyVCPXegucMMdDFDYJzgHqtyyA0BjfD4nPjDyumNRHnFl//pVuWWbrRdq3Dzf/ztvR/97XfRhmn5'
        b'LTY7PT2OHPYO3nS40Ffq/LTZ6Jr1T1V2P7ZMVVZeKDL/QlC31/nKtbsnf+z9lu0R8w09D8uffG2r55pzB740ZiX782n/adM/vXfJ/r7SqVjnp/XN+eV/c4weiXH3KR49'
        b'+knnX+6v3R+/1Tnz5/9WHfyTIiWtCct2z+++s2lOevtOqvTPb2S98aO1X/jRnbstHw1qRIaYbcYtM98x2/jP8JqAyndDJzaPpd8klO06c8Lx3sXvXp/8zvCv4gY+Mf+u'
        b'/Td+sC7Tzzm69Py61F9M331n8m+JX1X67Uf/dfpnIwuqU38e/NnpwYv92afbfmgX9ItrP0rb+dc/Xhow/k1wSePh/MTgjW+fOzVv62Jj+m/m286kezrvdbvfWfGrt7f8'
        b'u3170oGt/whN2HNswzedjX75o4zu3zaOvH+w7fIOtcn/LvwPA7ebhm9WVW13+PncXKL+h5aZP5xY2/XDLX/84dtl9/c26X84+ffvD/WcOKbxX6UBgyFP72rPXx89tvVL'
        b'b7j/l9H9n97KGLg5uuvA2K7Ur2t99P6FjPOXw2L/Z/XfGxdGtlQ1/j3KWui7oxeYausD1X7PclTgjrze5TFsg27BaMXHV55ZrRXYJ5g1naZ2WAxNK6SpuAoom8zweYbO'
        b'o5aU3pBYXrzJ659GJIX5HcGSS7xcBzNrL5Dhz52J19fa+kJDhCK1Jeqc0OhnzspiWdYpzGHvkvMBkmP8jUJDUpml9eCg0NuSNbaEcQ8hN+YOTkPTks6Wmti6FkulkhsG'
        b'gsU3jXkkeLHSBaaF7pW8R1D3fsECG3M3Yy13KmlJZpa08hlcxS3p6946tjSbI+pi9kbq6yRQFWYulIk9iYW0UAO29s+6BcCsu2BW1eOEpmDGc/swGp8qrHgsuCU3eNyg'
        b'h9nTcM9f7qzR3YXV0Co9e5zMP2bD7biFt20P4XygkNxIYpSUha2KaC2Z19AOT7byieh54Kh5GHsE7yyoYiZRIlN8UCjs8gjHDsrLl5bY6dJCKAzFkFQ+hhIsYK4tNEIb'
        b'v+o5O1EDx/hk1yIZWdCJbUtMxUU78ZyIb2R80p4lRiJpzunl/S82CNVcrTed5RZaPDxVWGi7ofZfhOeG/4c22XOGmdbSfARumQ0xAf/5LLNbIgctbidpyBtdqsltIhPe'
        b'kYg+kdI3EvabHre1Fv9lfYxYDyNWI1WDW1WL9pset6K0eIcjduBJR94yU4l3NdLgmVPsv9lrnz95sOR95KaVimDUbFQYOsy6WGJL6f1vr6+10pLBbBQjcoPKmhkaWott'
        b'Jz6fQUUmleNSk+pV776Y/6XJJqIlec6cUrTQPCjiqdrKZEAJfQgk3KSSMqMqRkthQCm90oBihyo9VkqCXTSgnjUjUOS08lTY/+UEbuGexWI9wn0rlNZ0sPAUEmj4VF6S'
        b'GMTzvZmVRZceCQnas8txO7NqkmQZLP0jPYMd6XzpFIQqQc+SYZ4vfih8/7mPi6gJx0V2xkHuK3Dm6ePLYeZ2KPTioWc3LICZZS0F8AGOSE/i3TUcYerB8PalZa9msRYX'
        b'JNf0d/DA3YEohr2ea1mAeQ7Sg+ugLb7w4D+U0m/QZfkW2+1Lt7MaD0q/fiewuPsDcfE/7sVauFfvy4Ge1E35Wv1v/3fLT793ti/D+Qm+0TFYLNNfX2qUFPHJo5vV9f/4'
        b'wdWwLyWdqXuzqSj739/aUdQ653DoxvjGLKfvlEhln0iP3f6l9uavtX3U2up9xf7bUf/c++fIdKd7V3r7PjA3/8Cy7HqOtbLgj57BkWu2PkcznyGGq5py7RrOvOJLixSQ'
        b'bG+W3LjixTWMll2yHCokYflStIDd2C7ETqoJP3ct0YYnaSsWtSHky/vTsYBFG4ucblOFQuiQ+8v7Q5edOfmXlMQSGa6TydlsmRQPfB0pfku0ZvF8itCueFGSM3mdve45'
        b'abN81OWydrnoWSJrP19dbxKk/H7N5dJUOKxOn119bUFaYrlUkL761Vhh2+z4VOZq+V+pgrl4hm3wxazUtMi4+MvySknyOrzLajOtICk9Bc9F4lXu6ohPSk2MZs6a6KgN'
        b'L5Wq8pd5vl4QffxpbV5EK8olpUB+Hu0S5EMfQaTjvsRbz5ugz/KeIozV4qE3Id61ZVqUzhq+rOu89XH4B//2ZsSbEb8IT4ixq7GS+Yon/82kxbTVxK+p1bTFJMTktume'
        b'M6L2CTWX9f7WSoJ7vIRZAWQY5GLvMz7X85TXQqkNYmbBwPmlpU6w9CjHfwegD7uWmgRpBxZz1/PxbgZvQlMJnddxinH4BEkC1sOS+2Zu0m8Bl+SSwQ+GVWGcjNOFT20M'
        b'pycTtnaRptI5l+55PS51YTyqKD2qcKg+N8LyIzl2y/lwhdqjdgqnrwP91sxY68DrsFaO6OfLzoZ+2jxZWQrlwMBQr0BrSaDwf71Pqdn3rG6IjP3HhMsI9htLb+c+a46z'
        b'uIzgbyMshen/Na7+jBI7TY+mpKMpPymnpqkksbBYWpBPT09LYqa3WlNDvHoNE8Qi8ZYbBmKHZAOxhTlPUlJeTbr4hXPSEpHVVr1I5ctwWyfzDxJe5bKIRT6hxi0FWx31'
        b'oJA1s1i1exfkROKYiivZe9VQo0bWWDveNteGKsIHXTACtYcOQY8m1ECpeC0+JRjwVBuaXcksrYRJGTzAwVBtFp7NwzG3ffAUxn3gqTdddQdLmftnEEYcrkOvP4zuu06m'
        b'9V1VHCdjawge74R+6MWB2EtOm7F5O+ZgdzJ0YD4O4iS2XneDMhig2U4Ye1/aF7QayjZijueNBGfeIm42fh8WXvReYy5b4+Xqp3zK6ZpDEPSeMrOHWnywj8zCu2RAVyXD'
        b'EGnnMpjxgRmXJBu843QBy7VxIArHDQnWdEEN9tDPE2wI98SWo84JUBGJ91Wgg/BCYQpMYDV2hJBpOH4lCfvg6Q14go2hUG2KPRfPYAP07V6Foz7wxJHswTwaqFL/EIyF'
        b'QN5WP5rADLbsgbEbOHwMmsU4AC2s/ye00b934uAetkDPlfVSTagjO7LTyQ57cSZuj8Y+fABFkWaQ450E+VH02MYAmLOO9Eox98LKeBbU98X6UyZwP8sDH8IkbdO4mwo0'
        b'HbMOo/cug3oo0NgSilMmBE566K/ZACiCNoJz9HujHc7ucd/stsnIECeP0wdt17aescVmHNIzxCKsggeh6fRptY6GJS7QHUM4AWM0nXERNjpH78Xms9DqBHMG2KkTEQCV'
        b'sRnumBOMjeuh7MIuNVyAh2aGkVgBDxNhYS0UsiJMI6lkRTdtN8OeKMvjp922YS2RwkMYSJcR1TVgS6iW6dns5L3XcNrs3DpoCYQe0zM4RkvUiPfU6H2miaRasOcAlqtB'
        b'0WF87Eg72QDDLvSiJGBxFvJO0ibcsd9PFFGaBZPGa7GUlugJdunclOIclnhvglmjzApG+HM7WYmpYA+oJLrXgjmcWnX9AG3w3cOQsx7asMleaweO0hZNQIf0MAxEyjZa'
        b'Q1WcEpRZ3NoG/Xsys+N0WYEB6MF7tLjlqeEnYH7VSWg5AC0wQc/Ok2GbDTbabsGHrDasFMbVsW4tzsiUU7EdpsNOXdmPrTdCEmEYW2kh5q3oLYhE8H6y3156RIcZtGLu'
        b'0ZP07JqT0LgbmqAogngvV+ISgDUwznpuTuI9GLpx5oah3slbETu8Y7FN/+oOfbxPr1pGtJxHbHF7J/FVibe5/6arW4ja7kAzjmwnKh8m6nyIxTKsSYQ5eqfDLCNAFfvd'
        b'seYadGb6ecTj/a1YZEX2wsL13Q63oPC8egg8NIFx2XpWSA7v6u9RSsGFcJyUYFXWatlhzIcpDSi/6QNNmGvmDZWnIAcLonShE+4FhYQ5RRpsMcVBD28NIwMHR+W1zmHE'
        b'Ru3+WBxCO9yEQyZQTHIlR4YDu2grn8BtLJBiTSBU44QFtgUyED0EU0r6RIClxtBDb8JEU8EFJ7a4UIwjMH0lyxQq1tN494mo7mURPRRl66sRS0zFYB0+uu5kBLW0jPm0'
        b'PeMkuh6oxer4YqcpjGLX6eM4TJxXgLPm52A+wA8W4K76JqhJJ6EwAIUu0TiVhCUnYd5hDXPbnQ2C2bVEc8NYEQw1fr76Z6+QnTRL0ukedpwhuNFM7zAGuU44bLg1ZNOq'
        b'IDIIavDBKexPZFlEQTBpjQ+VoSliEyGOhfWZ3yGKVIeJY0SQbnCHESTN+pEtTGe6YNtZJXpqF+Yny6DrkiZxZuPOo3YwoBfuB4PuUI4ztFZz2LiWCOkplNKLTcLYESg8'
        b'QwxbYInzPu7ubtjkC71RehpYQATbTyQ1C/kbocXiMlFwo8Qd5q6KdjkcwdqLGba0aVMwQLioFB4T59QQy7VGnDmXTOKjxw5bE2ixn7BkzVIi1SHohQasO3uYxOKCrfGJ'
        b'jHPnoSuAZtiHVThtxRqa77d0ysJyI3V4tJRgiT0ajprSPB5cwTx79VswncwlZp3OVWgmUTng4b8re0MkjAdeu75aet4byowhN4ZebIEeMECiKW+XO5Fvk2oSmWZ3L0Ct'
        b'Nm3woIU21O7BZh/oyqBLcpG9SSd2kE66Czm6EsxzYwoK+7F/lSrM7sHHJluIHCbhsRM+NbqCvcmrrirFJWIO1BPLFmKdLi1WH73iAM7B1FHazx59LD21Lo6oLQ8nGEKc'
        b'w7mzW0k7jZ7KMiPq7U5yw6pw0mGN1jB4hRii3IG2o8fDicRcCdEl6c6zOy7uxGqrBLx346BONk0yD3KIlntgaruFVZQMpkjizGoZkVn9GPO0sNgLOpxCiSag+ypNoATv'
        b'WMED6IZhuJONPaprN9FCP8E+r1Pb4Cm2aXjZ0EsXkozsIsXdegimvGODaTOn4Hb6KdrSZlKJnfAkG8suQ9M51WhscIvxduBK/Y5fBmmcwkwSC1V0TcM+b+OT2AitF6FU'
        b'ctkE2oi+aRWJvqHjdALNcgE7pZtTfL2wJFkbq6NPqK47j/fXQCOjrm3Ezz1e+jC0PfNtIuytMLGHSdpkDjDmcMwWZ8SH14dDlyo2B2uIYYKlC1cSzzRBVQZMikjablqF'
        b'OdtpeZvMruGoKjyGvmhvK2jxhGFDUgYtpnR5pQ62qSaZJRDZtOgSLzY5WePTMAcfaD12DevMoNx3/W7SA7MatDJPsUz1KAyGM26RiVPPMjzUnoxj+OTcCZIWTP6OkBgg'
        b'BJKyC1oND9gGG+DYKagOPwS3D8NjPezyvnWGlqVr9zVDKA/xPwWDm3H61jrPcBIbQ7Qbw0m0JsPQeuaqGBu8nOFRqOM1HU/MhVZoco8kzXyblWk00ae1LsQ+KSzoY02Y'
        b'sd4a0nulRlB1zl8WSqw773zMNZGYuPYk1DpAnr/RNiO8lwgjB4j5ihOgbgve9hRjjvJReBx1EOq94mHKPRCeQPFBF8/DN9dgM1E/CcV+Gq9IlEQaoAcnVKCL2KBkNbHL'
        b'JC3VHWxzgnkoNyUubdsMT27gzCV3otgm0nOV2LDvEvZ4kETJiTqWBYXeKUT9XTeg4cYqoqkHUVdxMNYEm0gCdpOYKGVnB/R3IRF7FfZ5EzAicu632E1zaGcW14HdWd56'
        b'pBMPrYGpEKLBWZi+ytLt5nHIE8tp2QrYkYLd6xkgS4PyGIutjA6x2mg/lwU9NM0c6IiHBpKSpfrZlwOwjQaaJrZqhJp4mtAgQYI8CVRm0tqXm16jN2wlDTpMijP9JHQ7'
        b'YAf2mQRph5CiuJuwGrujsf4IbfEAPjkL7eE0y1F3GCUmLnYhk45x+Tw2hNEjis7HXWYqCHOTTHEqlSTMJBZs8jqtgeNrt3sdW+dBYrlKwhIpEwl/tAfTWygwhC0+FCdh'
        b'JWEItz22MOsI45c1t7qophGGbfI6jjUH6W2gy4P2eJ5GnkqjdZphEuikJRQ6Y952GbTT0KUwnnrNTWu9H8zjWAR20jWjJDwab5lDju1x2vCHSntIFDbAI5td+3H4HKG0'
        b'enwUTQizkpTYEOnnB0hCLe+WPdYZENkWHzwHXb7YEHyAFGtV9AFoDrMh0NEHT1xptEqCI10wp0u83Q7dejjoA5Xbs7BGJ8A8NokkXa4qMUjHNY0LML7Z9ZC/iZs20dgI'
        b'1OvYr1OiNWvXMHDBafMtalIvvL2BljFnM9F9vz6LoFTSM++fxbxzUOcBJJfcSQuSaCJ8gI8vYBt27L1E4qoe7pIy6SOkP067JD5qfxzKNieTlm6FkSDMO409Z12h1N8u'
        b'gJYtD0o8E9YGeR9jIKb03E0YiLDG25GQY3jNAhtJXVWfwZk0Ip6GYzgcjsX2jtAoIUrr9MciD6KvBZLp92PPkU1SRXK7xNSElng6HGv3YhF0puyhpb/nBIXuRDN9WL39'
        b'lFHMLpegCOgLx4cpZ0kod+3V1djsvNvI1NmaJPq0FpYYHgrcSspwYTO0hdFTa7SJsJ4mQWnwcWKSx2ehawsMGEXhRDIN2Eqv2X6eWKH/TPQqligK9x1gTJO15sPGWCgx'
        b'h8lzqeeN98NQIl10H5pjSD40SxNoVjkhRO7TznDHDea3krp9lEEcmH/LCJ+KErHVFhtOhmd+jxFl2xHiJyLK3GROk/NEk1k4HI33rqoR6skzvEZLmLtlHSHcaTNHA6zV'
        b'Iyh5IjjbB6pumW++lgmFMpOjF7SCSYX3sh/I20mSv4EkCd3mxlDTdT1tGMmirX2Mncf3a5KqnIEF3XBSq80JpG7vKmNOJtaHRsP8tWT6qjXiHGGZUQ4fgODDE5iPJ+Kf'
        b'ijDBgjRz7Lciuugh1hkOTcbq6xYkH9oY3I2jCRSfd00y0aQ7qkl2NNB6lAWcIpw3dCPkxom4LEutQCTE2ov9liS67551z9LhBWYZ51bBw+RUdwOY0c0gLslNI0hRdTLQ'
        b'WX0TjkcE4m1oCKFLZiBfFYe0o7H4GGsYSx8XpUKLLtkp+dCRhZMXiFTHt2nZ+tKCNsfreSVcdSfjqWcdsegYy3Nea6VEa1nvSGCzytgI6pItzA8Tr46sw0feJLkqSDhM'
        b'kzp+nMxz6GsubcaBjWTdDmH+DWixsicB+FCVBsvDAWfvaOesDWdjiMtziRvyMokRWjSgZjtWXnTGVv/NxAtThvrpEST95nDoNA6dI7bp20Ak2Lab8MqsM1nxD1OToTeD'
        b'EE4xmcr6bsaORiQvG/ezus97N9LEq+KggiCDMt4LI21ZTLRa634RH4SZYoES1OFYNI3cTvTWItp4xS31dPrqo7TDE5Y23D1QHZUBbe5ZULoRS5TPYlkCNO+jaydhmlBn'
        b'I5YcJ0VRRrikzchfBzp9t9wKIhodwdHsU4mEFRtD3A/vZqbZsAv0e6TZnIVZIqo7ATBxLd4ohkRQsy6R+LQ99h677o21XjZEE6PGlpi7zT8hjFZvbL21Cs/OORyKk35H'
        b'cHq3ski8TYSlHif58aRUKLT2I12/AI/kZ4lIEOQLJbOJA/L8bMPDJSLxARE2y8J5Iokt4e5+P/s1e1RE4v30MU3nNj/ppk1vc5t55aFnjVgk9hVha9I54YBtLi64M6f+'
        b'COaIeUpUB4nWO5neUvquE2vdaZlqyd6txJYDWrTqYzc1zM+oQ8PeYF2ZIemlagcihx5ap3qG2Ldg/hGvAChMcF9tTcJmFvtNs0k5dUPHET2PMyS/q6AtAu8QYCEOxs5d'
        b'zOdC1nd1lkOmJwytZiDvBvRHy7BIE7rTZMQ2tbDgDjknjmF9IO0kfU+TKjhMv/bBXRFJ2KIwA0Jwrdtow9qdTm9iNZHXkT0wYXOKnntHFERjFkSTUB0jHVxLO00WTvx1'
        b'KHQg5VodClVbyFSYJHo4TQCmegsJuftQ40JmUkHGhQB46kfk3kdqoozIatKMTKY8MsuKXayvQ5EzobfHJCXGSR90wfgGwsL3oHlP9J7LUryjGq2LTT4XYXAXPkyzNcdH'
        b'53H49JFVMKh6PTM6IO0CydBq6FNnbgNoMjPFXFrYYRJGuSQfB86epmeV03o2nDJKYJ1XaQpVO+lVB9zWaJzQwo7IcG53tUgxz4nsmBxalftIknTBCcqlOH7KJsgJC06S'
        b'UOvei+NbiHHuOtsCO3ExCFV7CRDdoffJSTPOVCLVVJVO79AH84fOEJqshVIb6FDFkXis8oH6/dgVRiZVOdku86qrsCx8Q6S151ocUYP6cKhPIzaZt9bJxMHItDQcoJ+a'
        b'G9o03ZJdx0+SBXmfRHG1M056el/Xj4mCB1baMKODnT6MEHfj/W1HiLcHoRCZb6dEl+z3achdA20XSA5Aw36f04Fn0k6cNiY4VEx6/JHxHqxL2+ZMgmLyspTkQz+M2K+G'
        b'hcw4HN5NlkCVjSG2GDMxTvquyPEWEfODnQQXS5g3yjow+FLMTXZSYxu0ZhBJFcHsGShKJiXeB0OHiH/v+92C+xfI5uugTb3v68r9L3NS4rHOM7FkS/XDnd3Ga2/aEvSc'
        b'DmRmBFbHwBPscaT/LOC8xWpoiE63yzAhwDXsjg/Pa2OuNs6JoeM8wevhjMxB5pmpoi0oed41Q4J01N3igO5lHFmtsuYKdkcRc+RGkGieOHoGS32NVnvQjQvQmEbLWahp'
        b'pHz6gn8wiZ4q5zVEOg0wZooD2038NuyDqWtkEBSdNAmyj/RQJa328Nhx7qOZDDKnQVqgdhctypwGvcJkMkmlHlIq83E4kwkz1jAGZftsiTUGsC2Z/rhzeQe0kFYjEVXF'
        b'SLUXJmxg1DGF0H6HK05GnaGFLgw4bsywJpKk7j8hJikyR0yda0b8M+FNSq5DyQzv2pLkbdIgRu81PA73LEmyVkLrgTR/wtodsQQ/8w4wATsBuTcSCeSvPUB4oddUlzm3'
        b'/PFutoGnBgwlnSNZXC64AtIjiQmqLm6mmd1mnYBukjB4ZEa80E5WLtwNOC9KwKKDiSR12s4fjCXdMIVt0TTJmgxSxXl0ByFzbI+MgrHEo7tx2lgPnm48TdTQZIT9Hg5s'
        b'UWxw0DgaH8UT6TCsP0T2w1wazp9X3qeHzWu3Y01QKkm1ckPsMSC5XHuN0FQOLFwixDO9Hwb1g6z2O2/iKXf1p9Sw2zuF1r3Vamvmeuv41Ue9DfSxy/BWpqs2FB6UBBLZ'
        b'DxEFlsDATZIF3ZnHfaDsDEna27bw0CiaOHOOWGPmxokk0pfJUCnFCfp7hKDeI9llkrdtbtdPYv8pexJMLThsDU8Onof75puPkFyoZXtM+/CURFszyYf7+vQa87hw86g/'
        b'PbRvJ9QkrfIOorEfr2XdlTzhoQcJ4aILypb7yVg+lvldRq0N0JYC7SFYpjBvT9DoFdC4w5xZuKeCNcXwwACLA2FMxR7un1FZDYNIUnB6JxHCmMtxnIdSh3gXek41d5sM'
        b'WdqTIGN+umZ9OygguUY0WgjjZB3g0ytB9ta0XcM45+4Bg2bQrGu2hha/HKajiF179+8TwaApiZahzdDsgjkbSNxNwshJ7AyDVqdTJHmKjkBb1CnWGfw4wyg92H0qbauy'
        b'NG4fNmzD/iwscYDJjaGYl+wIfQkHSTH0sU5WBF3bvEjmwCN/LLU7Raqj1Yb4Od9+w4k47N+96nQaPg0kYmsg5VGww0gNOhOSYZwEWAeNMB6oSmywkBpEhns10Us59GXT'
        b'S5O6WoMD26A+kxRKY2ACURNZLo122slQoGHhivdd4rHJd3USzMFgJra6wGOPNGyktbuD48fXw0KoaA/ma6vhgpRmWRiwCh4pM9dIrwsMxK72gYbDa9e4kNVVSq+E9/eS'
        b'IJ8jkhhjpfKIDuYvkQE6QirUkNa9OSKSsU5MnBWJ1grJWY/YS1rw4AwOJAQFxsecJ7A6qUOzaCGdO6xB+APKIqHxuK0xkJ1xGysStGQ4Egp3DA+En7uGHb4B67ZjtSNO'
        b'rIs7i5XOEgZeSQ4VkC3diXP+WddpAcoi9Eh/dePT9UqbocEwGAsjT3qfPxjgRSxe7ob16Xui8JElyaRRdjqNrEOVCyQgRjRPmXEhw2R3Ha1lU+QOmMAHltbEuk3Ye5U4'
        b'rhLGrdgpOn1VUpFDqSdX0aBlUTh/9BJtDwEkd6hShxmDvQ4k1TquGt7S3Urs1Uzy5qkdFl+Ajt1JMHPlUKYnYZpr8GTNMsIm43ZGKjHGe1h9QDcN+oxUEraSzG2nV5kg'
        b'idiwXewbeoQZUJH4MBKntImvHtCbd9vt1cEqs9PrlIjCW0h/lxOGH8mmta7fEaoeBqO7sOUkEXcLCe7Hmswih2GzMFpsMquhcjUWhHgx6GNID7t/wRz6nfD+YRskPOO7'
        b'jtanzBI6HcyJPev3QesqWpjWdNI6d6Nh4qQZkXmLJHjHWug1dYGcCCjZRuDXjYSheZj1WhITNXGYpw4T0Wm3SHHlwfSpXaRTpqKZEC9TzTjqDINau2mB72CzyQVaokcG'
        b'2BO7CkfVrLI99l0yhvbdMObvAhPXibD6Sfn1YbMpzmT44qABgZ07pEefxJE6yNbwTKNN7KDn1FjuyYC+vUrb8f7+TXDPXQPbMnBEL+acCQzo612C2lVY7hdLD8qFOjtV'
        b'pwDaUMIatDIPlSwCUg/sDk7AUUuSDYPERm3hlrjgRdKrEdqPeLiJiDdKiTEJgpPsqoEZzRgs2kkKmqFZTxhfoy4mYTB74SzJvX7alYf01AL9VSdIj1dArxrkx0GhCw7a'
        b'kwIovnkZavacReYn7xHB1Pm9a0mkPIbC+K3EandNoNue+LyZWGKcDOu2cHXTnfjEGBpD9/ilepMKvQf38L4S3XIbpiyMXMjq6IUBDxhSNiNWaoOFzatMifcqbLDqOlax'
        b'pSm5ApPS1C176dPqfdCz9QQ+Il2JDfqb9m3Cjj3QFH2SSKcYG9JIMc1nncGxHfvCIC8xgyRjnYNoFwzIsowiImjVE+PwCVREwPglws/VrCQFrdaEKwnWgk0uZBc+wqI0'
        b'V78YN2BVuEuv2dPiTmqJifiGtBg2po1sjkrPugEPg+jPXmjxJyO9E8ZSfXD0BFeL0/hk3xl3aLRitRew09sNp30JwY1pRm0nKNd0iphjQTWC8FqOpQMUZIqlrDtP3yXG'
        b'R7lEzoyR5vGJLUniJqLOGRecNiGsexJrNeI9YXgTtnpug2opabcubXaFm148WYxz12J9fAgK5PmGuVhgYXYK4et5vOtBmz8Jneo4t0s1kXTOsBi7Q/Dx5huQQ5Zf/RYv'
        b'Xc0QbIjiobX7zNF/6xrUwWPm0OqFR8H0hsQmA8xZREC3HwZ8VmPz1eCtp7fRu9Xj0D7MvYWV+MCMNGPxWegMI6z1wF4lLsXJBMZ9NIjvR+jCCida1sJEYoB5Xew6BwWE'
        b'BsZJs1Rux6q1qvSO/er2OHo9jgBgYUQW5LuRSq6ELilOmqhj63ETLxOilhErZb11+HB/GFTpJOHAATUSmo8xhxXvH2YibSeOikh/1+MdR53oo1Bwxs9qT0aCBs7rncje'
        b'SiKegLl70lG4k4q1TiFkVzMgOuUSd53oo2QrjOu7+hEbdxvDYw2YOXk10QbvbSbBNYutUHAeH2dpYOHhEOKLAjJMWGGIajJaNtB6N67Hdi0NaYwxlp1OiD93wRlb/HTE'
        b'h1fTffehWgVq9I2J32phNkHriO02nFnP/J+kuHNgbg3MsvjdXbN1ZPSVR+x3IwDfsYOWoxtG19knQ7X/RuKKSrJ90jOheQdtQ+ERfLBPkyA8a6XXdjjbGHu0birTG9R4'
        b'QYuh+nViuBr6qxoWbJPDr0LHBjIp8wz2BMEDE2jT2+2mdQVv+2KB2QVVvBsKNXHQAcNER5XBp5jDFO9mMpcXbf0Tkr7jpCLysM8Bi29e2EBqmiDQcbq2PZBe5vYJnMl2'
        b'IFwG/cQutaSpizVPRWSeJobsBKZKCI727aJ3W7gBdeuxJppA94NLRDD3r5gQXQ3fwKJbUEKSnJDH7ZPQqKqS+WPCSV5YflDBBQeYX+rOCdLBJL4S9lsE627CKuKAE5uu'
        b'0ddtprGR6ibYZ7pnE+3tAo7GwoiqTzgNMUP4qF+yC2fWwgLe3Z2gSe9TgF0ZwOK/uaf3QY0SNJiQKJ+7gs1+0COlXwfgcTQr+HGTxOIdYqY62olqjfXY60tidBjYaZGa'
        b'67gAT/YZYckueGKPPZsCsCyRxbmOMEdV1FFamoItJFBKtJRwKHoN0f30VQvi8Ufbg1KI2voMnWhuNY6rsWGjuTW2bjlMWIF4w5NIYd4oDh9oYcveDdivTWZjwVnI88RH'
        b'B2BYPYtkSy1hn3qSy70iovfHKtBu5gONmmQf9DvqQrfHdmh2JphQYBK6Cu9t3KGigsXHPLFEE297HiWT+IkDwasiF5zQTcUH27T8nKDHGWs9XA/QokxBixJxfR8J+sLs'
        b'cAs9dgrrEQmCR5BrQYR+X0yg7Nbl7URrtcFQoMlJ4tEFkt0LF7eQOGjDohRatQEmBh44QpkFAY/amDjo3UP0zFzwtVhqjFO7yK6pjoViFeiJs4B7SjDm7oozzD7HnGMk'
        b'wKb9r/DzVCoEq3uh3Arz7GhtxlZDzw1o1CeyLLZkoWTl6yq7YkPpyXX7dLCBsIPKFYZ/8gx3JpO5R3D+NgmJahgwxOZDxlkssyKEFq8FHp+/vBmG7GHOC3qtlaF5A2Gr'
        b'1pMweJHsnfvQa3+B0A/p7V2uKTvgse/WS9izGZp8YcDW8TBOKZNGaTyygazadpzcTvptkLFIc4jBIWcC2MMOuBC2iWRbY3C4zoUboWtOEe0UY85OfxqjaaOb+YEbrPRU'
        b'8UUcxAYVa4lQhqeTVqaLF8rhVXKgSya2UcIHQiGtMmKhu+mscht0yYu39WMud2BB7pWwZ7fF4YLYJhbGhaNQj4J1+U0h5vyeMHocT2Ad9YUiPztoihWLxHtEtLWFOCLU'
        b'qS0xyPbDymgXkUjsKKL1bbzAfV7a0LKenZGC3itKIrEn3WLuzL+Qka5u9jsCLcfkbjVPWOBPsnDDOr+g83slIrGTiCE7qOM3mCYzD5k/3I6kG1xEhGxajYUSZPftff2w'
        b'YjO2LNb0KcMG4Zv5M6lYZs3OVNA9QayX7e2twpmufBJq7CC8X6LgjKs+v53f4k4Qt8vPlr4vlTvv1kM/vyWY6LPUz5cQyBQ9zFaExXvShVF6riIrdVBmFSZ33uHwCWux'
        b'F29rxA+rOR0TSsCNn09JjEs2FllL+ccWe6RC0eDDcVpDe9YIBYXOnhM+TL0g85/eFyFiiWde/GnCyTYJ3zsDfHxoyZYPYp3YJnwjn6e+c6Kw373efO+Yu81aKmzSA2hz'
        b'9bPDgmz59m034p+HCmdkfPC+fPdEB3niNZmBT6GNb98EFMv3j8BaLs2CP2+E1EOnX1D0bvlmmTvyFbEl8d5Fe5UAC/K9UsFuec9uP4LUd2lTZFnyLcEmE4G2hgnu59CW'
        b'BByUbwnmZVkLRzFNsw/7+WL9QfnC48yG+Pd/ul6a/pSW5J1fOd6o/XKKoYfJF2Ov/OjtpK2V7b/6w4+fvH1tg6qeb45SRJbdbZ/qHLPbdT5q3p9cdrn0vtFvZ393eS4t'
        b'VefNt+IW/jz/k6+3vt957iffbDe9OxX+xsPxpx1ZP3F8u/RB/8d5ERU5d11Ud3kHLQRvvuA4qOdrnX/CreKp5sdf+2t9rs8X/iIzG/6al+fV/R/85quHpsOzPtLMNN37'
        b'29hUnzf26qfX9x6tDk4ucP7kK19V3aPy+w2V710/9Pinb+46VjL0pPg/8k8Ee/y0JKlb5cGVY7srQ95xnjzQr3PJ5rs9+woyJUecHvTfdFtz8nsTo2//w2jNqe/9Z7nv'
        b'wT/d66t+T6siKyD65JpB5W/lxyR85c5XA46tq6nzP6rbo3y/z3Cvr/9H/+j7j2/dNPZ4MnVh/Ozbp77XbnHN7a1t3w32u3zyfSeH2q8729pObvzb5XWuVZvr7ZuUcWdb'
        b'Zmx12+ZvvLXhVOe6hu2jp/p+tmnrmU1XfrnH9duHJ7+28SunzevO/Pz3Kidm+oK3NE+tdcv4419G7/3Ke/4HTQ+Nb/zijz9/ENlysUHtyfbRs4PfG33v1Kr0rc1/31AQ'
        b'uC1grlXrk+1vnFLRGFj77Se7Mv5ntfpf/1rku7fprT+0xNz5xSaV7YfS3iwxstuiVv/t9/757csSNNmw9/0p2T/n7NUdb83U3Trg9dXgsa8O/Ozj7aXbfxeZ/Wtx/O9/'
        b'9a0ryd+XlUfenm390tr42LsnPolqab96ecv2L/75aEH6R2HXm99ukv3oP09MNW1s9Oj4Y5fd78s/mHjj5vzC7t93nqvwkX7vzJ+++dYoWKZ9vfbtq7efPql/9K5fyr2s'
        b'/9fctQdFceTh2Zl98VjAFV8rIqLmRFgUkIf4fqHL7oKoET21ppZlgImwu+wDBRGD3mlAFgLG5ynKaVQiGhAFETVJtxUlSalXVzlyU+bieeWl6vSP3Hln1WlSuf71AHrx'
        b'r7u6Kq6m+JiZ7umZ6Z6Z/hr6+36h/zgV6cgzPRX7bqcUmuwBnx8Vfv+rR2ttqnPrcHpKe835F2FdHbs2PbFN1Fydfy316W8eL9ja23qn6htD//prf8r98++u1f5h7Pf9'
        b'C6znHvb7D6/+iD2+71Zt5HvlzQv+9oV490Xi3b7Jd1uffSU0H2yY+03D9YSythPNrWd/GNPRnytU98UEUuGdioyYrsPXrQntkt/Nej1upJOC9RbUEmQmJOSj16SCk9EF'
        b'Ove/gPDpzteCSjCrsmRxn2EtzTVuG8nk1gXoCEnaS76JTaFuXzChN90cE1Gh1K6KpS5KU/EpfijXFty1pVSnZpZPHbuQI90uGZV6wUOTdNYtuMlTFlzqw92hqBbVhS7H'
        b'u7S6QNweWqZiYkKUZGhwFjXRKctkqH8GVf9b5oGcyC+fIBydVDNWpRr1TEWNA2ZCTdlBCstQiVp8hp2BjvG0QFsGavMgv7aUXKOHEIaan5a3DTWQ8vBlNbphQr3UcmYN'
        b'DJ46h+xmsnDPa44zqGf862GFkoZ3au6wQ0wE7Xb+X0AOGs/zxU5bPs/TueqnGehxWJZVzFJEUWWentVySoWWU7Nk4UJUer0+ICwyTBOm1geGj1Sy4aax0Sk7mFmsIh1m'
        b'rSuV5NioHUyc4Y2lsM2nKLTyfHb7LHktd768rRm73rAojAvh9GHxO5gpGfJeMxvDTmdjCcaqE+gaXYJVoAM0vPLjnjE045tzfw6383Lee+LwN/WwPWIKuTLoDHSoIrD6'
        b'9YRAs/a7Xo3EFUX24JP4GG4iDK+LvOTke1STbUE1qEHDhIzjJuDqLaLt6EXWY1AwTMV5c7K/L5NbFLb7XCG/r89yoC8vOvpKS95GV3lw6F+2h9V8PXtFvGJezPet3U8X'
        b'VWq3SY3plTv++uWqmtop2+/NMd787Hl4hPPhLzetT9+w8wMp/ajh6v2Ev6f1X3r/w8pnb37cHNgzs7N+fFndmi8uZH4llq2uD95wdGxXT+Gh0tzf7p+wP6l1549V5RfP'
        b'VUQcefL4/rcL71XcuOOdeLt6+nptxYlHN1u+/C654sXoNQd7zn490nj+lnTQ/6M494c588Z91mjwFHRFz87ZcP+teEuPbvFETvte+8xf+Ed86nqQVzuu64+f3Aphn0Tf'
        b'jHxW+rZ2T9riOuWttE9i7rz7MMK48YE+t2jyEk3/7ZwH6u4rS8Zc/7Z8VG5f7sfPPr1x5rtHY1KbNt67ZYuZSI2edFPmALXLzqYKYg0Tgd8OQhdZfNaIWqkobSH6wGrO'
        b'NuIOyATT+EfgawYzh1oUPqq/zkWncDPaG006rYYBqzA/bQo9F4kPhNOOLQofjANnWKuGUStZJzquRSfwZaqGw3W5eryX9Cp7ZhDCt5o0bRWuo2rxtHTcGIurF+D6aSCB'
        b'rlMwAfEsOmLF3bI0vhcd20K7OtQQAbYJWQrUPh/vk53metcnmtGZpaY4Ez2WpIfgWi4LHUJtsjnfGexHXWZTXBRuHJTPV6GTtK+dgDrB1hcOs5qwP8akJEx738/AQfBq'
        b'cjo9+QyP0kwGus2ZcVnJSQpGg5tYNRmxX5Vl/TfIQLTHnJhEDjbLbhyhk3ADauPmFMpRpVZmWSDZZJVTQ/AFMiLbwyXYkCzQWxi2Ce+FIH9thHw3kKFAjgL14hsjBy59'
        b'0hSQOlrxJTaOYZQJCtS2EvsHZEf4HG6JNZKb60SHQf5fokBX3rJSczEyej2ILseCxNACJ7aSQVI9qSElM367Eu0k5KJDto87L+4ww7WBNx2p9lGJQTEsSe1CzVS+NG7K'
        b'bM8rySsWBZpY1I4Ol1ADudG4GlUH4Yuh+LIH1eBuF75UivY60YFQHcNETFZqUB2+KAvmW3LwO9QPMBaKYxgf8gehIyz+dTK+JLv++dE7ceCgt8E2GK4Y/pmAdlP+wSeg'
        b'ekKJVOj8NNLK4IRGo/Blm5B/RpYxhhCWZZpKB9ol11o3Pp0bhNvxJfAob9Shtxl8OjFS9iXYT2hVM8wtp6p+VaUCdQr4VBU+TtX2hLh8GASpRvAnLzWW4UMytTL4lGg3'
        b'7kDyxaZNgrkdSUb4xw+usbBMwBssoVgnt9Pz5ziqYjONcVYjFb6i3uBRXCCuM9AHLhD+FmomDWOOJ4eSt4hc+8gkHz7O4eaRNlkaWheWGrsibjrIW0mdk4e/Iwi/y+IL'
        b'lZuo5cMKtD81Fu3B72eS0ZGZwYc2pA8GNpo2/B/3/1EXMXoYeMbLaNQu6ItCtFT6r6VLOLV20w5IUEH2BpZuYKumHzBaIzk5x38uoRtcZsqqMkoWpktcseBwrySdmqTy'
        b'+lzFgqQsFj1eSZkv2gk6XYJD4jxet6TKK/cKHkmZ53QWS5zo8EqqAkKVyC+3zVEoSCrR4fJ5Jc5e5JY4pztfUheIxV6BbJTYXBJXIboklc1jF0WJKxK2kiyk+EDRA8GE'
        b'bQ67IKldvrxi0S4FL5PFnFbbZnJwsMsteL1iQTm/taRY0lqc9s0ZIrnIgLykFMEBdlqSTvQ4ea9YIpCCSlySMmPl0gxJ57K5PQJPkkDFLo0ocebPTpVjlPD5YqHolTQ2'
        b'u11weT2Sjt4Y73US5ucolLh1VosU5CkSC7y84HY73ZLO57AX2USHkM8LW+1SAM97BFJVPC+FOJy8M6/A57HTCFFSwOAGuR2fA/y0XtIwub6nuTOAqJkBVgCsBAAnNncW'
        b'wCIAE0AqQApANsBcgCSA+QCzARYDzAFIA1gKkAkwEyARYAGAFWAN1RMDLAGYBTAPwAKwHGAZQDpADkAyQAK9SNAZroK1tQALh1ST8CAFDFGqf/78FUpF055rC8iTItiL'
        b'4qUwnh9YH2DYzw0D21Eum30zmKmBmBfShPysGC3VP0oanrcVF/O8/MhSheRj2K+Wg7m678CedYPc9yfBvSXtXNLuvmJhPmx5MggoWSWr/e9fnTfDqUPivwA/3wG5'
    ))))


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
        b'eJy0vQdAVFe6OH7unUrvgn2sMMAAghVLRBHpIMWCxmHgDjAKDE6xBRuiAyJiwa4RjSYau9g17ZzdlN1sdjdb3u5k3yZ5+b1Nspvdl2yyJW7J/zvn3hlmAJHkvb/I4Z5z'
        b'7z3fKd/52vnOdz9CHv9k8DsXfq2zIBFQGapGZZzACXwzKuONsi65IDvNWcYLcqNiO1qttCYs541KQbGda+KMKiO/neOQoCxGPlVa1aNVvsULCtM0dWbBXmvUmKs0thqj'
        b'pnCDrcZcr8kw1duMlTWaBkPlakO1McHXt6TGZHU9KxirTPVGq6bKXl9pM5nrrRpDvaCprDVYrVBqM2vWmS2rNetMthoNBZHgWxkttT8WfmPg14/2YSMkDuTgHLxD5pA7'
        b'FA6lQ+VQO3wcvg4/h78jwBHoCHIEO0IcoY4wR7gjwjHEEemIcgx1DHMMd4xwjHSMcox2aBxjHGMd4xzjHRMcEx3RVTFsNNSbYlrk29Em7UZlY8x2VIwatdsRhzbHbNYu'
        b'hXGDEajWyvIrXcPKwW8y/IbRZsnZ0BYjbVB+rRqul9bLEC3bi9blvjhPj+y0M/gAbtlE2kkraSOtBbmLSAtpL9CS9qzSQp0SRS+Qk1fwJXJUK7MPhad19aU5WfFZOnh8'
        b'dx6+XqZAgWSXLP8Zmz0C7pJTZfggvjKVPqJAcjmHT41faB9N72yzjYxjL+VlkXZtlhxvw+dQKDkgw/dD8EMtbx8GT4WmVeYkp8ADOWRPQZYiFp9GQWNkM0lbgH0k3J6W'
        b'jx/S+1l57DY+S/YD+CuySeQs2Q1VDKfduRi81JqVh49vJnsAGtnNId8sHl/DreX2cXB/+QKyy4/cCCK3rLiV3GkgN9fgtqAANCsRjRgnV5FmvEPLsa7CwGwrmICPkrbc'
        b'bLJbhmTkZQ4fJw473Kezj18eic/l4MsxWeTYah3ZlUN249YC2jLcnpiv0yrRwgWqRrwPn5QqLICRfJZ0k93LZ+flFiiQopEjZ/FWfB7uD4H7dnxbE5etW0yuxOfpEjjk'
        b'HyHzHWmEm6xf+3FLRVxmfDreGUtac2m//MhenlzxW1XJeaypFNfk76U46Y2R6H+Lk44Yh9YR64hzxDt0jgRHoiPJMcmRXJUiYSrX4gOYygOmcgxTeYap3Ga+P0yljR3e'
        b'B1P1IqbmL1ai9HS4rSmPz5icg1jhf2zh0SfjA+Gq3H/UYqnwmwo1Or90DJSV+38zf4pYqIpXoHRdJFCY8tw/rFiDLqBaXygeumqo/KtQNPfzsHsj3+JvTwoZ3sXV+sCN'
        b'AMVR7poKaZKG1uf/NTkqeAlixTErvgzqDOJiPkfvr/x51N2RUciJ7AlsMsjuUbBe2hIXxcSQXYkNZHcmYAC+UBKTnUc64hOydNl5HKoP8pldRo7a59NXri3G5602y9o1'
        b'diu5Q66Rm+QGuU2uk1ukO0jt72tWBfoE+OEO3IJ3JydNTp46aUoKvoOvyQHPlvuQy+Scrz0b6knFz5OmnNzs/Ky8HNIBi3U32QWY3goruC1xSWxMfGyCVheHr+Lz+FIR'
        b'VHCDHCb7yEGylxwiB0jnEoQikwJCcTs57UYbOvgq+I2kM5HkImWyKpk0rXwLTOQmGUwrz6ZVxqaV3yyTprWqNwGS95lWeb6Fzrdp97V63joDrqbiz3MMK179yWvX9l4/'
        b'NEbx5ouGpa/eDX5z+as3954+dHq7ibOqKgPIvOfjv6kasjczSVY9DGXXBgzb9kutwkYpBXR3LzkOU7ALBgEWp3wG2eHL4evaFTbaDR+NT1wCDE5rPIfs5KoS7+F15HSm'
        b'jS6zktB5cbqYTB2PyEmyTYmP8Tp8fCh7zRc/8InTkfbcSQpEjpUoyzhy2Y9ct4Wz5a60k7ZMfBmhIPIyv4nLaJiu5Zx8jFYrs9COeiQ8JI8iZlVZzBuN9ZoqkQUlWI0N'
        b'hjlOmd0k0PtWJR2u+b5cKGdRul7Syp0+9YY6oxXYldEpN1iqrU6VXm+x1+v1Tj+9vrLWaKi3N+j1Wr4HHFxTpLfQObQoaELrS6cw6GJBLwfzSo7nlCy1036SPQm4KY5c'
        b'K4CucojHR7j5uBU/m1HJ90IJNouUnwAdoUghr5K7kUI2eKSgc+/bBynC8u1sYB/i7RZrrmIGUHtELiD8gk8uu0GO447InFxFUTLitIg4SBc+ZKdVpPlNIt0FCvKQ3EGc'
        b'AuFbAcmsW/gufnkLaStQ4J3kEOIWIMD758kR9g52ZGzyy1OQO/gm4kIQfpA9RgTS4kv2xcGNV/wQtwhgkpZq9sJMvIcciUtQxuJTiFuOyAtPlzAetwo/IF3kwCI0A7+E'
        b'0EaUhy/gZ+2hcCeBnA0nB2DsF1jjUTxuw9u1PuyGDl81z4ShJc9Fkh2I7IhKZRDI3o2Bz0DxUnyFnEPkXDk0lSIoEIfnYQE/gJrwSxvJYUQOLyEviq291agm9EYC0JA7'
        b'CHrTEspuhJFnl+MHMM74WA05CZitIpdEluzArZMIvTM3hbyEyEu4EyhSGGM398l+/CAIpmQs6ULwf749hI5UG7kYRp6Dhi0T/JBf0hzWB3IL7yUniqGeWLwzGkVHx4uT'
        b't3MmuUQOAK7kko4klIRfwLdYJ2AWyWmgOIdVCpgLhDuQfgp5wR4Ft0LIVbKDdFtJN966eS3gHznPjR+BLzES4aZKvCchoUu+GjWip4M3cY1cCwiEFnkjt49fI6eoxpaO'
        b'uH54J5+Q5OQqtVzPSmRr4pHvrFqT1VZprmuYs5RWSe8okX0O7dvd8eRUjiR1MOadSTpxNxDV1oJ8stvGa/FtWXIybssBwt9t9SOXAGnJfT98DUjrHtPPGkvk1oNQz+jv'
        b'bZmw56XApsLw7T/+dIH8+6dee+2nb3zOHWn3kbX+9LJhTWik8sjkLz4PDDw87WDb8vcaTavXT9w577x85Lh3oqzvNGsj3z/x95th2w+nbTzyy4+77o24ubC7uuruG38x'
        b'vd356yNn3vhoaba15vuVe1fUP4hL/WNwy+Llud87F2797RrjgY+dC0df6Bxe//5HHStWDnv0zcUdZ38R9IFZO2WBLxBMujY40lkfl6Alu+LRRNKClPgSnxKAX2LEdAK+'
        b'uAYED9KSlZuvQH7xtfg6D7TxMD5ho/MVNgw/R9riQSzTKfE9vAMpV/Ljikm7jQp266unMUZYDMtiF4hbpBVfylagsMkysr+cXLBRwWcLuQKYwGh1MD4ikmug1eHL+1BO'
        b'rbw3KfWeRaefsb7SLBj1lJYyKjqK4kqmnJNzaulHzvnCTzAfygVz/lwUZwn0oK6c1elbb9ZbQcKvMVotlMtbKGXq2xLeEkyvg9xElVaT5Saq90I9iSoTcXeXlnkjkRwN'
        b'I/vXkf3ydSHkzAC0lbFbL9o6MMOteTLD9RHlqK9yQ9F49DlMSHnjnlGSyITDskAFWD/dt7w8+3uN81AGK313ZTDSoKRY34by3NeM08RH1xX5onDU8LQiuDz3t4UzESMF'
        b'VaRVm5JEDtnlVEhGFVXINOzuZIV1Gdw7+5HlD+W/L6+pyjW8XRVz6IMvPtl67eiNZbuEoiPbh6ZGDUmKFz4RPimPT5bdGDozKjJ5yPE0oWhpUVTZ0fFp8TvDFwfnnKD8'
        b'/55S4JdPLQa+r0TjfhXRlPCllrdRciYHVHpI2XfYdGDgjHmXWW0jGIEnW9fHJWTFx2oTQAQjrUGpCEVp5CvJLaNEDZ6IXSGVNcbK1fpKi1Ew2cwWvcSp2YSXRTEcC4QU'
        b'cCrEA6dklSbBqao02+ttlg0DoxQdPkuYG6VoLcvdEF7wQimqYlhX4JcAnzJB38F7ChJAtmyNX4e3kdZEDGsJWPdsfFxJno8iR710ADd2MWGOA/zqEeY4hluPl9GbPXGL'
        b'NnJCH9waK+KWsBRwKyYOBqF8hNOvWEIjeT2gkf9oHjWU+39WPxOVsNKxDQqk9lfyVCD/OH2ZiFxf+gAhaKCDWF7bEbFSLPxzbACKmnxPiQrL/f+UGigWanwiUMzkY/T1'
        b'WacL5WLhKNUINN02hoMnZ/3EnCEWFsZq0NwR52QAvjFv8Six8MaK8ShzlpGqA/PM1gax0JyqRYVJyzlQHPhhDVax8PmkeLS0Zj6FXjFTu1wsnAB6sH/5MKqM1C401YqF'
        b'98L8UHjh1wgFl/unKtLEQl/tRJRb7qBPVhypKRMLl2TEopIV/hw8yf/36jqxMHhtFErSvK4C6CvW1lWKhW2cDwoOH06b5H8voFEsjNUHohElf5KjpPLaSZsNYuHfG4ej'
        b'yfJ6WmdjXEiUWLh+0ig0K+obBE/OWjPKTyw0RI5F6Y0dMHnlY4XgUrFwf0kkiheu8NDOWdvmjhQLl6sT0Ar0MxW8Pvb8ojyxcO3Gyahm1n4lDF3yCaNdLPz94mQk5H4K'
        b'KFdeFDstSCxcFp+Eyhv+zsHIj/1oZSbSjheFnPvkBXKXaqX4+dWT0KQwsk2Ux/aD+r0tBdqlwK8ko2RyNlB8/oWl+FgKIAV+dmYKSsHb8G47JcSjCsmOFBB8VPjCZDQ5'
        b'wigKJafIw6QUaEf6liloCihgD5gEkxNkSgHUBYF/Kigat8lhUa55oBmaAsvjmWHT0DRgQ7dYvWRbzsoUWDDkhGU6mh4Uw+rFF0n3JNwNV4GrZqAZ0DjWtrX4+DTcDU3O'
        b'wHdTUSq5j0+zx8MDyW66PPCLuH0emjcLv8QAkhv4wngqZ+BX0uej+bUjxWYcCw6jsj++V5yO0vGOdPHZbSCIWjk6SiEL0IK4JFb6DL5AXrJCVzaXZADQNpU4RDfwtlFW'
        b'KuudzF6IFpIzZL+dsangXCv0ZHhxJspcRDpYDXnkYBahHRmVnIWy8BUtk9oW4xPLCe0IPoE7s1E2iHDPi/LlbXIBFKpu2ujmZTkoJ5Y0sS6uI/dqSDdt9nV8NBflFtWw'
        b'52dU4S7STZt9GLg/yMLH4Hk6rI34bhDphpaPeSYf5Udmskpmkaa1pBsabibHClDBYnJSnMUbNlBqu6HpAu4oRIVhK1xD0raCmtfWkCOL0KIZKWLnj5CHK/xo06+RS0Wo'
        b'iOwfIs7jgWhy3g/aHRNSjIrrlGLN3fgo2e0Hzc5YXoJKyKkscXqvk334nh80u7q8FJXidoP4dDM5Sp7zg0bjrSsWo8VbUljNq+cv96OD/VzxErSEdKx2KS1HoQqKOLtw'
        b'51K0lHRNYK2eV1qO2+gD5yqWoWXk1kZxXPdrYeDaoNlkK7lVhsrWgM5A+dkzoNZ04zaGJHjrcrSc3CJXa//+zTff3B8JJHNEMAcrLz5cqxUXWXIuMOa5Q1WwcIu+WF2O'
        b'TG+GdsutP6UQFLPrOmbW85Oimj++86N/5JVvl40JUHV9xP9mK+/7ScbkzH2/Khy//+nTmc/nnaz4W+iIluLC0Oc6a178+vmoTWmKGb7GF3429Rd8mvr3ZuO+MW+80Tzx'
        b'Rq7lRLNiyLIzVUcjFi+rPNnuuPTWkPc+u/bD6L/GfJbyYYrqZuOHe8e9/O/8WUu/+vOtf50Y/fN/WUc81ZH8RtX9xSs3/DH8uM+73Qe25s486fd+6NsfGL/56Huvmf7x'
        b'/qGGv/3oOKqutUUt/+fQp6sSzvw09H9mb9/+69KfXdRMfDfizDLjMzLV0dRTtTtAbqVsPZ5sx5dA+synRq8On9Wg0Pvhizy5go9FM8EWn4omLVQiGIFPu0QCcjDIRg2G'
        b'M5+2g0QWR9rzdNnUIgms83YouSsDpejSIvb2cFhVIJnuzsmKUlLVXjmdH1qN9zDRduMI4rDiy5n5uhhquSQdMhB97oaQvTJ8LQMf1ir6lSbk/bF+DxkjUJIx7JV6Ksky'
        b'AYPyeiT4c3I+mAoZfDhHf0J5OQgCw2heFgyiRzATP5ScJdwtfMhA+LBXDiRzcJYIt7gRzji4S9x41sssMB5K/MhzZT3ixqxxCXnwh5lakZZsVeADuLtsAEGDmhqRh6DB'
        b'DShoDMJqpBIFjaBF/gj0kKX/LivPvT9tmiRoHM4GBoyQumJ0eXzeDF8krrO7oN62pySJkukIZQVuXmd65Y3XFVZqg5vc+tUfystevbb39IEL209vv3B00o5Jx09njt2h'
        b'NX4U9WaOId9QY9wvvx5VdCQtfs3Osp2Brw9TdqUequ0a9s5k9OMvA57dk6DlmBg6f3i8ZEOi+IZP+ujyqRn3iZM/TJx8q81ir7TZQczUW4xVRgsoNSIi+NPB2IJ4NWgu'
        b'TM4c4jHVcis8PPBcR7rnmr7Y5J7rrV5zPYnyrNmk1T3XiQna2LwErS47D7cmZufl6LJBj8lXLLAjvA/v8gVK3DpuwIn3ljAHnngvCdNVoffEK/NFM9VhcgHf97PgPdTu'
        b'QLXuo7iJ3BIlynEgmIyAfoNgMoprQBmmjb4T5dZpcOvftZ/9oXwFm+br29dwlb4fzXt97L3A5wNfr3o9/PnaQ2PPhf+ufGegMvipI9tSPp0SgAJ3+0WP0oGGQQdtPb6J'
        b'u12TW0NuU3oyq5rRIhO+WempYeBd0ZKK0aSRJunxUx/VS7fwnnhfceJ91NwQmHhLlOe0Vz5x2oe6p52+2EorDGbTjr72mvhEKIupKOxZ44JVVCqYRuEx82gDvuBDWvDW'
        b'3AHVVlkvk+C3tBP3N/Fscv+4LmisDU2nkmzuc/4qkfdtj1OsH84HUyne/5uaGLHwv7UyXoXoVbm/eksQMn3k+DNnzYf8yaJT42dcbPik/LPyNytqqi4ZPyk/b3izKjH5'
        b'9+VLX727dwwsfe7NqmzD/vJPBP7dtzWbUWGpyupbnPLc9PnR88cUT987+u1Xj3LopCZkXPQNCTnwiRnx+GJuXjyfQvYieQ6HbySRvYxbTKghZ4FPwbBeJUcSC/JIe34W'
        b'viRHkUXyqeT2sMGqoAH1xvU2vWA36gWDTcSNUBE3gnjOF7gCNXHwwAssw9w4InfK6cNOn1qjQYD3NjzBsEG3XSwj3DhDK+rwwJkvQ3szBrJTiZ8lbXSzC7cWaPGFmjzc'
        b'XsA2+SaQG4oykJt2VsqkmVV4IspUEVHkbCdK4VBWKSVkkTH7sRyQRcaQRc6QRbZZ3t9eEa1S2QdZFBJ7GJMy+W3uTYoCljW12SJePDVdsd4gY8iS+6+ECGQa0Tmdt1bA'
        b'nbxzE0fuvh6wNclf/v7aoqS0X74VeLNTG2xblP0gu/K2+njFopMrt6S+sCNS+f0zmhkbR35WM1mr/7q8Mizyv5sWhh8+/5t7Syb8uD364OcL/xy+fKLqm53V37wyVJFz'
        b'bG3tx6rZpUNHjksFyYUuSHKA7CBXmHFMhfhc0BbOcKX4FXKGGdVIE3mePKQbpWQ/Piptlk6Gm3Re5uP2dJBVLuTQpdlG2gs4pCa7edyMr84T8bCL3K6BOy2JOts4Hsnz'
        b'OPzKyMnslpU8pDDz8CWEeHwzDzdzC2frBhJWlI+91Rs5/auNvXAzSsTNoYCVIK0EAm76cv48z6v5IbxlpBtDFRRDAS1p55zKSrvNXOVJ0vpdFIC5dF1ZRnljK630qAe2'
        b'fjrEE1vpFi8+RK23OeSiqUBH0dWNq6PxGTk5jk+RQ/0zs8lIkmLohimqUgySoXmZ4wLgN6IPqo4WUfUP436AOtN+Jge1Pat52iwRVbdOG4Pmzl2poCaLXdFjxcKKUWoU'
        b'nPQCj8rLc3+pr5eIHbCJ8Kjv09fjJwbPFQufFsLQ+Ny3KPqveFG1QSzMKhqBpqevp7aRRjzfJhaeWjoF1ahn0zUBgzpdLLw5RIn8hUg53Wm1LJZsI3fDtagwfTq1Toxt'
        b'njpRLHSsfAo1qofJgChbnqkeIxbGl89G60t+iABQsjFrhlh4eWoqsiWtpe0s+svIjWLha9lRKCkToJWXrwjUJYqFx+ri0dLGr2TM3rJ+qFgYPj0EaRpiqQ2ndvEzkuYz'
        b'avZctFV4SQWFoUpOLRb+ba4cqaefUFGWcDNb6uZlmIOomkzapNpfzJ4sjeeaYWjy9Ls8NGnWntnSIKetnopqa8OouSb0zAZO6lHgItQVZaHT4TsjYo5YWGQQ0Jvhz1Az'
        b'iLI1QyMW5tqq0dvpb8vg9YlOEy8WvjVjCIqf3k1NK42/WD1JLJxRHIhGjPhGCUPnv2WBNO//eGoj+qpESy1IQ1pmbZLsQuOSkbDiS8D08tAfWFeLhflTxqH06U9RS9tY'
        b'eUQqMt3WTeCtoAmhDe+eKN03u4gkBe9YcuifVz+YHrU8JPyD0hHNy8++qVi7E6e8/cGuitKj82wz5llk+XjSdFXch+u7lm0qMK/7y+t/bV3S/ffClRsmVR34Al+cPeLV'
        b'uPAhI8qb9nfJOmVdN16d0p5a+QNdVAPf9s3sxjeWX//sNVhEa+c2ndx1a+yOW4orqb9MtR34Xvt/f82t2DXtrLKrcwbZWXzh/SXaDwPyRq/9+FeFGffu/b6p9LV/TTh4'
        b'd+Qvvvrj/I0RnduW3f/9gjeGZxkL9y2vrc46eHjp201hJfveO2rN2BL5z8w7R67+XJey7nRi0SvvXntnWOcP09v+YcRX6ne99V/DfpNw8+svnf/K/mzO/6x4yTarYe2/'
        b'/pr5yD/y3+8+N6v107avptz6WfQXjzbIX/xx01cLWua+pcBD//1p2ClVzPtb0NikVQ+bdFoZo61Dx2YzNg0sOjrdk0mH41ZGt0fxuCsnHm/D+2MyQRgC0gv65gZytYyR'
        b'13Xk/NA4eDuWQ+T+WLmdI63PkG5twBNo6JOTASi0p4WaUuAKQ/1qfY251kRpKiPDJSIZnqGWASGG3/FMUAjmNGwHJJgJDaG8v5zujPBsfwR+ZL3+sqtAmT88H8r5AglX'
        b'cxaNm4SDILrBaLB4UO0BWApnGeMm2LSKKx4E++fhvc3c+Eh1UA6j1dmgZrfhPcyxoWPietD5YXrilWg2ua4kd6PWeOkNCumvtQoSI3UfQ2W84McM3jyoI7wga/Ypkxnl'
        b'glxQNKPtXJkCrpXStRKuVdK1Cq7V0rXaKKc8oIoXfATfZjWU+DhA+C3zZUKJv1OVJggWo9WaX6mU4KulX0byUymlFJ1t3M43VWqJkyhb1MBJVMBJlIyTqBgnUW5WPW7T'
        b'vK9OrMhnZqYxuHNpMf2LiEMzhnTrRP+KzqkfIasdrsaP3j1y1/UQnBQs/6bgkPBC8/fSw9MU78S82qpUz276PGLfiqFFLzzM+uvv1v5Vm3fk92+d/UdgqaHxVOvGt5fE'
        b'OQ+ueSU8+B+3Pth2Oq/jnZuVb77yI7s97EjH347G+Ou/erM8+SevvnVtAj469GTKAeuk3xg3/Au9eW30tOR/an3ZAlLiDtxKXhyeE++5gIrISdFzY1tklMtvAz/0k/YC'
        b'yTH8PDPIkG68g5M2KtkuJenMTlGlsFfVU/hk8pLocsXqJQ943IodxMHgLiP38Pm4BJ2olp/l8W58KAl342M2KkKQ5hnJuA2LLjMdOTpoZIcK+Q3hiSOd3GOPjCbnyDnc'
        b'VgDLm7TH4YukVYtflKMgH5ltBj7BYMzF+2axJ+LxBTlSqnkrOTqUWvBsGtb4GvwybksEuSwhixpOSFelAoWSczJQoc/juzbmyXUY3wQtoS1xC0rQZufpqCNXG0/u4P2x'
        b'fYV19aBpSA+NUOn19cZ1en3P/ugWkLTZvihVLwPZVSinlH42BkkYnSC9J653tVNWWWtlm1WggppsG5zqBjPdQBeMTqXVZjEabU5/e32PKWMgnUNpodtIFqpLiNtfE2lC'
        b'3Q8tMW5CQWW3f3oQip3DPAhFn1a6RThO+qXLwUrXYSNaJWoQXL6Wc6r10s4cXMutxloPbwFxuNSzag11FYJhTgDU8iWtcWOwC5br1mCBKfR0pID8xbphuAFZ4iAJhJct'
        b'gNnoiTXWiDX66F2jPkCtQYOutVmsVaUXZ3CAOoP71OklK1M3OGr4ATr5HaRk+o9HvWmbLN80OpjnrHShCT+a8ofyT8rfBtXdv+qD6j/mylDY5zxe0KHl2ELENyeTC2wl'
        b'4pfwDtdqHGpNl/xA+leuTVYP21uPF9YW+BmyMcI1615PuQw7bJx6UJz34nax7qGjBrFQzqW1b4WfzwM90bh/IEDW6T+tH6CrnjqA6fVOX71e9FKGa3+9fo3dUCveYQsF'
        b'VqPF3GC02DaIC2qC96pKYt2lDmMGq7XSWFvrWtZ9rUeAYuJj8AjrwlhI/oYk06FagbjQYH+O/YheuvgkPoafteZmabN1CUrkiy+Q3auAjEY+4zW/ftJf627Ogz1zZSBd'
        b'dgZ1BsNvQGeQia/i4Ur6Efh2pRBP2beHn2owsE/KwH2AFcuNCmDgqmYE7NqnnQcmrhB8Wd6P5VWQ92f5AJZXQz6Q5YNY3gfywSwfwvK+kA9l+TCW94N8OMtHsLw/5Iew'
        b'fCTLB0DLfAHlo4ShzeqyQNoTgYoKw9o51mZ/EDuGCyOY2BAE746k7xqDhFHwtqwsmPU8SBjdzgs6yR4iEzTCGNa3EHh+LIM1jsEKhfx4lp/A8mHi252qTnWVrFMuTGyX'
        b'CQlMyBB9zeloBTqCqnyEGEHLagyHGmJZDXGshghBxkhAIggxlYwqPor21Xj8k0pFB3ivO1qlU24CudMppzjYH8rlV6qkCaeLJNC1uDMonRClIR86eNKkupySA6sCJfqh'
        b'YrKRGuiHitEPNaMfqs1qoB8yRj/kH34NKOzVLPovq95kMxlqTRupx36NUWOQOmEC3mSor6Qu/71fSW0wWAx1GtqhVM0CE7xlYa9mzUvL15gtGoMmWWezN9QaoRJ2o8ps'
        b'qdOYq/pURP8Zxfdj6MvxmnlZ87W0ipi0+fMLSvNL9PmlefMWFMGNtPwc/fyC9AXahH6rKQEwtQabDapaZ6qt1VQYNZXm+rWwwo0CPYlAm1FptgDtaDDXC6b66n5rYT0w'
        b'2G3mOoPNVGmord2QoEmrF4tNVg2zQUN90B/NWhgzAbhV3+ZIw0NnOpW1i165zlW4hhf0D8FoeezLEtMV35cyMEbFBbqUSVOnatJyCzPTNMnaXrX22ycRkibG3ECPaBhq'
        b'+xlAF1DojgQRrvpv8WDqcbFcsS5X7rvXJzJbsTbx+jvU5WU672sN9c8Xj3NcJ8+RE9RoGE+O4+0J9BREzhLSkkN254kWMPzQSG4yu8LDOR1oBIeikiLLog9Fb0B26pmt'
        b'I10TmPmQ3MCOQtJCRe1E0gpXBcViNaWZdFM0Ly8rj0N4FznjQ26DqP2AVZlTpET+IDwkKc+O2h5RgOxUlMC7NqXSTda4HOofmLsoc3SUKGJT8ZpujV9AxWkqcph0G1kl'
        b'lgbxnErSkIaRKSsli+5JjZxqWZqkIcdjjqxPQXYqm+DbhiyPmoOmLCIt9LQGtDSxKJPsylWiheScklxPxeeYW+oovI9ctZID5OQa6iHSAW0z4UumCz9ukFt/AvebgxdY'
        b'Zk/omFk/b1Lwgjf++rDj6+b0M2Piyod+tm1q0bC4fU3phpi87cf/sXbvn+8ZRi4ru5JnzZizrvHctu0/rvrz54f/WNr01u/qk0oiP8v66Nl3plR/tO237/7hre/LNi3Z'
        b'tPd4l6Oi/YsfVg0Pm/zVzKN5+9YvmLb8ZcfJWXXXDzy78BNV9DeffrYr9we6HROfP6z/655b07Iax1/4Ou+d//nNZ02JE/99+h+fxn3MleX+8dU/W3Pn/Vlp4XIS5k+5'
        b'+Lr9o5yPlPg329btb3u9dOq92w9vt9/RLPzi/W8+7syO3h2qDWWazQrQdnb7wSBp8+y6WFC+HORMIo8isEOuHhHEHjHAyBx3b7TjFtzp3mqvJV1si2MZfomcyEnIzovP'
        b'wu2kQzwWMwzflDeG1OM9I5n+towcZdvxK/At1/aobjnZa6MyC+hnneSye/eJ1oC3kgu0lgjSLCN3nxnKTDSxU8j1nn22ofg8aRX32cLwaRvdw5pLruAjMO9QRRyhZ24y'
        b'83BHNdvJzIHu7RE36xfi6yro9+VVTGA04fN5opGBemwkAWb4LeLJnmFzmGo5fja+htugReR+GOuWghzjyP1n8G5mra8md/KpsEkRSoZ3QDeOc3jPU/PYzRXkYil9N8dX'
        b'YItMQe7zHD6ayVwQyAF8Ot2tU2rzSJtLpQwEtZUqP6BnnsfbqNbYrmUnpMTRFRdsnD4CdyvIDnwtXVSPX/SxsNpyOWjIwWByisN7l4q+DMQRRQ7CzYQ82si2UnKbw8fn'
        b'jGVD+gwMRBdtZB71dYjHV+dnKVBgtSwVX0xmA4CPkyMApq2AiXVacgUku8D5sgxhOVNafWfm0LfjYYTzdeRCdqYcBeLzsnR8Md+1sxX4vzaB9RbXQRY2AXOXNNkMl6Q+'
        b'Sc08Mf150SVCzgXy/twQntq4/CX/32D4Vfb64akQDj/+POh3ItlNcAHIF4VjH1GQp2TQQg05/YrWPTrAoJVzrUqsJMy7dlZnrLtiJnzT45CjvfSHjyZ66g99mj5YRVKh'
        b'p+LOAArfUpfC1wPDpf4+mlDilo4o3wJJwsW4YixGg6Az19du0CYAFJlgrhxsi+T6ClPlAA1a7mrQo/EUPEhWA0IfvI5OxZkB4K50w40bWPj5duDFXlu0qEdj7Ae4wQ08'
        b'wVNy+q7wfSX4qzjXAPCwrAyiDsqQcoC2CN4DMZBM9e0awoaCtyxwLYIB2lDtbkPiYGSxb9eOZo92RA/cjlXuduieLMV9e6xkbRgAfJ0bfFIJU0wAsqfxTSNNqaaWnWfu'
        b'twXf3X4jY7Zp+aMzfYTS+VShsGpMvdal1WisY+enQYthekafF+mZakm5KgZlBnq0wG4xawoNG+qM9TarJg160FcGjoFuQmfhxbVTE5ITkrSPl5LpPwXqaz4v0XLMVSwF'
        b'v7gxjh7SwFcEJJ/L4RfXzjWZX+7gmHPLz5v2/6H87YpMw5u/iyn6pPzNis8gx1f8Lvz18OdX/i7w9fVKTceYI9tSrncFoO+d80lp/plWLvL7jvopjFOS4wWMWbo5ZQvp'
        b'ZFLU02RrqpcM5JJ/6uLI3QgLEylU4SAViOeOSfNI6egx7ubYSUSydzU+lyMjTUwc4VdyiSsiB7J6qaipyXVeRnI02oLW+nJDqFVVIvXSM/nf0tyVA0mDF7vaH+httfWu'
        b'H16mrG8AryJqGUAOblBeRTK2fuSPHH3QoNhoE60B9lqbCXRhiYzbrZLyywIG2CyGeqvB4+B/xYY+FdE6Upk9JLU8D56BquCPodpoKR9ARaP/+to3JYcVzaY9KKp+Do+S'
        b'ygMvjotB9umI+sOPJ88zvau3zvUSlagfo3dFzzatzMqTW2kNun+G/aE82/Dmo32/iy/6tPyT8lVVnwm/L5f/VLv71/ELYif4a+euDSs8u33Gs5N2UNSVodg/+R099aqW'
        b'F/dHOmRkn4eKIKoH+J6vXI0vL2KSajl+aezj5FTcjZvsIKiSk/ik5JX0pK1Mq9Gmd00P48kMQYNdCLoFcS6RbuNQFxr1eSffBYzhZKo31vbj+8Se6MHfPEg2euFvi6f3'
        b'0wCAn0jYq0RxI9D7tQFo/E5vFjNYzE1wnSuibif9e2Exxxbm1ELthW7HloF8sERLofxD0DP6mtzcq8tsMVWb6g02aJdJeBw3rDeukyj2pIRJ/Rg2Hm/NEUSTCeuyy3ES'
        b'ACVoioxr7CaLNCICXFXaNIKxwmSz9mtBomsbWmA117kkKhMwSUOt1cwqEKsWB7XKaLE+3r5krxRbNH9eFrBf0xo7rQ+kkRjKajUWV6sAVpbNQJnvwCSirwOkOt8+m1KD'
        b'Y0FkR04+3Q1nQQbydYsy3Z6aRaQld1EmOTNPVqTFF7I0Kyssls2mlT5oXnVQXRLea2enbZrmgZbqaXRh75Oz5BVWB8I3yEGqth7k1pBb6iUZ+B47nItfIPsUpJvsI0f8'
        b'YerJeYSfJfQQzly4uQlesAbaF2fSvc1ScraUtMQvplv1oNVeKMmMp6B2Z+WSXRzQp7Pa9fgQELUSHoFaese/kFvIbDZkP34OVHSPpjW4qyxcolusQoVblPZIfJacXmri'
        b'ZlYqrPXw1qgj+3VvP6BuewsWbcFmLsMQHLX19TNAVA38u7Nub827zrcbv/5kWMVN+z+2Xnv3t6NrT3wtvKkLenqGwDfdrTk0ecRr8neL1+hKbRf/5Pzqw8n3HT/Ovvi5'
        b'zrpr89WuLR+//zvl77unHDu/fOXy1zUHLzdpfZhSHId344dAlJfiB0xtBp3Zr54nx5MtNurfgC+Nr/OLpQcMKDl0Uc3RuFuemUiu2sge5iseHYIfMH/iVXifZBCZbmNK'
        b'9QhybyFIAmQnecVlDUP+wbKIGnJcPNLYkl/rt2F1b5osV9fjnUxMGFoBQoBHeBJyG1/Bx5XTRUnkHt43Mg4fJCc9XJZFO8rsPFHnb3qKNLutCeQUZwUqvpdcJWeYPWEe'
        b'2VHvMieQ23DzLsgg10Ikj75BeatQqtlDI1znKcf2kPgwNWjkIpn3l4i9mFP2or1eteS72sBIqZv4DUT5ZR6P9ZD/RZC0UvIf7iL/W9HX4Y9lAF6NGCwDkOuBkA1A9k+7'
        b'yf4kpmX10LmB1ItBahfN7jbYB1K1z7rbMLNf8ja/dH5vU30/raE+QnUWY5VTaTVV1xsFpw8QZrvFAgJ9RqVcaim1XPu76N48kTH1hEtCDj/Jb8a/yl9iU/IWBbApBbAp'
        b'OWNTCsam5JsVPRLgh0cHZFNieChRemMU31NZefz+EO2LSO9d77qd9h9v6mc9F99ir8Co0TIDVdMSNPMN9VQnMkj3KlYB5+qXZdFdKOAixQXTpyZNYvtPdG9IoIonqEuP'
        b'Be8e8FRNRq2hWrOuxijtbkGHaZ97nnB16nHg6822fsBYjNCRemuqJq23WFwudecJPK+vTuabL0bIaUol97x5HmkRzZVZpZlQVCSyMLx3WTyXHIoP4AOkO4d0Z6MJ5Gwg'
        b'OYZPmdgGhgFfG52ToIvNBpLqWYO75szs0hgp2gFI0uRc7JyR/uT8qHlMOA9LpYfjUVKHuXzVq+GLReF8Nd4HdLFHOCcv4q0emyK67LxiT9m8rdiHvIJfxpftM+HlsaQ7'
        b'irSxZ5jBOosyyTjKNnt4M6iD8dnFuD03IUsXq0SkTeu/ZjZ5aKeCG2nCO0F59GTltD8UdAxQbpDA47W6MXh3tgJtJC/44PbhpEsrE4NwOHD3JgZbhuRPLZnD4Yv4zga2'
        b'ib/ARk7HkQOLxBryqDPVUf4Z0kUusdtxKalx2Xl0FFNWwjhyKCxaRo7jo6TJdPCVSwprCzxT9x8jR77zIIAk+csLi/RtXPIOx5vBn777RnvsvUnqguCMzffK12aOqRuW'
        b'/aOIoLskK/bVv4WlLP5n19mK9SOXxV99serFw4WT3vvPLz6y/TrPr8Lxp0OnVm0+FrZ/+ZR/Hoop+SKnePcPxvy8URURWnt6e/3TTr9u1f0M3dq9E944dflR5fLX2yLP'
        b'/iHo4N24ipP3gFmzzl4DRronhzEzvoLsmMZNwrsybJTZlJP9sT2MegV2ePJqctUfH2f8MB5fJg6YZjevx8e3UHbfOJLdTie38NUccs0nKy8WRCgeqXEbj7cJ+Bbj1hXZ'
        b'RaL6FLPWi1mDRnSI6e2mnFgpMJqRHKXu/uTGeMZoZeQa3k03Mpgv6nh8UFnLjxUEZi3AZ2rxK8xhtQBwl+wi5xry4mE6EmXkoBqfEp85hC/h+z3W/SwFvoYPMfM+yHGt'
        b'IrP0/z8yyvtRRiiRDsbN43u4+WQlO6KodvNyX+nXnx1a4UXre5gnS5Vqkji6UuRQi2myhCZLvdm6z7dzqZWLNS11M/0lbq5XBskLvTj/e2M9OX9/zRwsz1e7XhiA577p'
        b'5rljKLMAUspYh5vXeFnW5cw9iIdfLkM7xEJP8FmoucRCZX3q8SeYK/V6tntgoUSD7TI4ZRWmysduZDhVLjMwNeIwTdgZ4KWrMvHIQ24qY29J7RMnLOT/aNPncehmoQf6'
        b'htJ5WgkXarmcDweEQtyoKTwTHAed8oG+o/x4Klzyvlz4EM87oZxmNL0So/614hOLrLn54n4dh3x9ozfyZE9xqBcT85X+Wv/dy7dJ4MvkgqxMYUJlSkFepoJftaAo8xGU'
        b'Zb6CqsyvU9Gp7gzu5KpkncGCup0XCkDc8XMEV8mYuzH12vE3Bgh+gj/zYQps58sCIR/E8sEsHwT5EJYPZfngzkBjiBhBBsQo6lwT5AipUgthQjj1Q4IaQzsDAW6wENHO'
        b'XKPZcyFV1LMpUnoiDOqkPk3UATocnqE+TsOE4c3qsghoGyeMEEbC9RBhlDC6GZVFMp8lVBYljBXGwd+h0hvjhQnw1DBhohANpcOZHxIqGyHECnHwd6RDCTXFCzp4ZpQD'
        b'wXWCkAjXo4UkYRLc17CyZCEFysYIk4UpUDZWqnmqMA1KxwnThRlQOl4qTRVmQukEKTdLmA25iVJujvAU5KKl3FwhDXIxDMI8YT5ca9l1urAArmPZdYawEK7jHD5wnSlk'
        b'wXW8Qw3X2UIOXOuEQsl6IhPyhPxmn7IEQc62MhY5lWl1zJnqRS/Jhy5q8YboTyWGEQWhjoaDq7YYqDQnimKVG9yuPr0cary9syxQQZ3RZqrUUM8/g2i3rBQlSiigQiLU'
        b'KZpDajdozPWi2NefWKblnUr9WkOt3ej00bta4ZQtKC3KfzSrxmZrSE1MXLduXYKxsiLBaLeYGwzwJ9FqM9isiTRftR5E4Z4rnWAw1W5IWF9Xq1U6ZfNzC52yzNIMpywr'
        b'vcgpyy5c5pTlFC1xykoXLs0AyAoRsNoF12208tqhaKRUlbf6Usq6iW/hGvntnMCtlllHNfJd3GlkjbXxAt/ID0E0KGwL3wiIvIkTZI3caqWlrJGjToPwFtclo6FkBeVQ'
        b'eC4KhaNpaBNXr4b7KnrVguh7jUgvh1oVp4GO65WCmmlOPh/q+9MqevubSXPc427W+4XHyepsFERNwSDWwUoGsD6Jw5XKPLqKC3STkydN80QhARSMrCoquGusDcZKU5XJ'
        b'KMT3K96bbFQZAMbm8ixjkF0anoiuoG9YTBX2xygIqfR2arlgrDIAz3CjUDloHKbKGlq7SRwnQEQJDiBX3759Suf8UYSpnm0T9fQmeoI12sklOLmkTykz+PQb+PdIlpCU'
        b'lK9VOYN7g6V7HIbahhqD03cx7ckCi8VscSqsDbUmm0WgbEthb4AlYjGint0NalaymNGAx7YZR/2tW07wlQOfCJfMFBqeCjcbg0QEGPyGvCgjsGYNIB78xb0d7wLg3o3X'
        b'9UYZNnEbGoyacpiQSmDgtQnp4t/y8gSA8RQatGu4OEKPb9bf3VLLcOYT0D8aegHjXcCCJWB09a7i/dxjIWNT4VQbrHrmdelUG9c3mOtBRx2gIf9wN6SS7dLb6ypAz4WB'
        b'kEZA01BrqKRboQabptZosNo0ydoETanVyFC8wm6qtelM9TBiFhhHobycYqhBWGWHB+kD3rV4b6J6H/bhWPwDd9Rn92EfjlnXB9xQ/fBP/RGY0gYqX4nExbi+ssZQX23U'
        b'WFhRhYFuA5jFfVN4yqBpsJjXmuieaMUGWtinMrqr2mAEHjEfhtMCHZpnqF/NDOJWmxmkP0YK6ge17KUl72qSnjWpnI6pnS1zkahQ6uM2hMOYUifUfnbVaAxuo63G3MOv'
        b'4jVWE9BPqRr6Gt3W9nRlfVwfpYpSaRTv1HKJlfazPTegNaPCbKbBVTVVnmYTO5sKodc09EsQ1xktsCjXAh80VND9+ccYUNxiJAuWhnrbQgLz7Tq4Jq2LyYtxukx7UFY8'
        b'1VlzllD7AtmTCZcFpTHZ8Vk6JaoLVZNXyLOj2Bm6EeS4DTTAa+TWophsHY192xGXj2+RM0U68jyPyCV8cfJCRfUCcpKFky7BTeRla0JeNjlIjpO765ShKAgfliVswmdZ'
        b'lAjSRE4gT5tDTL4uNkdXJNXdireTjhwFiKRq/IA8rBZF545N5KaVxcqhXnAxM3AHR67FkDYWvBsfDUkqxu2ks5S0k4Ob8LOl1OhQwJGb+EVzBguGZFidQpukQDJ8ZB05'
        b'z+Gt+PA4O92cxG3T8QNrZgJpbmCGnRx8RY5CoMH4Euj7bD9/6TzcbI1hYX4UkdM3ceRytKrEJD9ZJ2PxkT65tjiifWZRU1pw8zN/9T/xVlBsRsm/Ij8PPxJydFjUsvHF'
        b'5yaE1MxNOj73xhtHsmZ1RH8Q/07V0//6+/1qxYGQ05HnRr3ctC9j/vwfH5uujl+f0RQ3RT3ZOnnV+K9e+of2xBXb6VG3fNc8+9r3mxIaR278xVs/IZs/fbu0bcXyR3N/'
        b'+HHkmJc+2vHTwP9577UPTRlxI68c+nL9hdC/rNy17+fzZ/3rzy9OWFPwgyH7/2IY3/zcw7Sm7v/47dfDV70y6kdfFhe8vGVy9Nfk+Qjt/qC/2IY3V+9+54vfvffVrk+/'
        b'HF24Iu10+1PaEDHKwOEimHQawYi0qZBcV0e6OHwZ7wwQz5q16fHpOB3ZRVoTyb4tmaRdhvwzZMoteCezPKy3kK24LREe4JA8kdyL53A3uR0k2lMOLCStcdl5uXBrDD44'
        b'ncMncfsUdos04yNJOVl5sXkqpAQcfCDn1asKWY1++E56DmsPvBYpD+HwGXIZ32L7JRtLSWvv/ZL6cpcVZiLZz9pMbkzIj0vQxgIi4e5xDJeCyA3ZhonkZWZGmUkeDnEF'
        b'mE+OoGaUw9XiUBwjBxfESegnz8fP+3H4GjkN1VIjSbmVPKAmkqz4BNyaqKM2NHw2UYE0Gjm5vbHGRpXjOHK9MqdnoeE2fBy3J4qrLZY8VJCmKHxeHNg70evFbmaNx8fp'
        b'EuGQn8CT40P9xWjRx/ARfCWnQLdlJYf4tVwaPuMvHn88QjpSV+Kj3ocjSSd+TnSRvYS346acvJycvATSGl8QkuMKXhCL9yjw1TBylA1zEd5HtpO2fHw5Xonk6eRgAYdf'
        b'0qR/C5fE73KyMEKkh3pvFsCsQDSOrmQF2oICfVnsVSoeUU/NcOaNSU8gBjNbUKAUSVMsDeXEPaCNIyQ5p18gbseU8Qh9Nx9MTnyVCRDbIfmml/Vnu9dxwwEbA3VRubF/'
        b'LxYW8oTFwgKRgPMIecKzDzk83pOFCgS/7E8gmC9yNOl4iyj3UWkFGAxlUm7RS5ILqJBglWT5vvxHMv73Eix6iRH9iw19uVlJXxHFQNmgF9d2MVEz5e5052MDlT/6tsxQ'
        b'WSPundcZ68yWDWyjpspuERmxlX2848kcvbeq5C2kengO2gyWatBLXE8OuNVR797rELHCtdXhkpyovGO0eir0AzD+/s91q0XfoBkRLNZZTNeSDbWTGmrEow+dT4+kwZBi'
        b'tmaVzzq4wCwWKmS30XrAlq7pb68c/fQlkYOSG2beGhDAo+FAkMgeRC4LeA/7boCRNOXk9JIhXLsqlKWeIi8ytlpCt+CXAIunGyU9G/pAgDaOCk4FWeGhaW/SnzjrC1Dn'
        b'TZKc1z4zECcFp1f/R+CYxtTwkEWday59VbJ4193umGkBpkM7wwp/decDNML/vck2c4Z58g9CfIIWL5554OOfXBy572jk+daJhjFpd3/3uu/3J742LvfoVJ89m2fd2fNS'
        b'wIGpa47/4PZMctT5q7s5Xe/+8fCjDy5N+7A084P3Pn84ckVxUcfBP42P//45LlI4dfFfi6786cH9f1b/eWvxX5s/uj4rZsI7cZkrr8w6c/zl9c3TH9QWaAPZPvwafJ5c'
        b'pxvxiRmugwkleYyYh0zH16UdIxgB4jDJUdBiWS2MyB1GlCPJ6TJPtuBiCeHhIlMYhg8wCMF4R6MU76dxHE/D/ZCL61kN+CqwqbNusu4m6mTrdJGu162zUXxYvaFcZG3z'
        b'/FlAIHIpge3lR+GjMXE0phRuJQfFkBV++AZPLgI72cZcAfB9cn+aGBGIR/nYwUICkXP1YrChDnJutoszziPX5fnAGZWkiTFGf7wrrBdjVKAZOsYX8/FhG4vQcHYK2Rcn'
        b'Ms32As+hGJWZyJMbeBenT1Tjs6MbRE7cSvaSbio6aseQLoCpXMWPwtuAgYsMfp35qZI+rmZy9Wa1GKED7ymOi88jdEsEX8omOxtAAsAHZJYAcrW/o+WD5V4qSTNg/CrZ'
        b'k19NFTmVUjxNwA2ReBKNiRHI9jNE/4RAbmOgxBakqry9z8zerGmA+Bi8+GyPI8IOSGKgLuuQHoa0FTk9Yxv1hu2lY1OiwnRs6tdLdWz4pXawYQJn4+Fatp0bAg8IvFfO'
        b'FWjrET/B9Eg+ISEZWBBrmdNfX2/WSzqw1SkzVFiZjt6/Pu4M1rs3qEWjYjbvOlrNw7DxGyNdNpJez3lZ/tw7w7mQtLA4/9t5S0Yjx3qDVsssc2mvLLGNXBftBTrNbeLq'
        b'h9hkAtfI8vTJKploD4RrOf1WAOshn/8o2s0l60xWaEJlDeMvE4C8U1MT04jpBcwaG4AwU11DranSZNOLw201mevZLDl9SjY0iAYmcUhEa5JTwZixUy2aZs2WxzjjBuob'
        b'LEZgUkY9e34R73J5pIGzAOcCeTmLzbAxwjVkXs/3mXQ2YBRpBGrKhEGgxsxVXBU/RDxzAF0PFWuKod2LFzsJjeuxfolz2ueLCfT4DYC26PUreOl7CcjT2iXe6x8LQ1mD'
        b'XHjo2RgVxTIY9n5a0BurVHp6Ql7Pjv+4wAe6wbNbbgmM/pW7oEexNdAF+CBwp/lNbEAaudXuNnCzADr9PpI4gbwIfU8/TVDq9bU2vb6Cl1g1gjnaGOBuA733rZrAuZrA'
        b'z5r9bdpg1OurHtcGY682uLEiwXMZjXUtkNW8WSO2BggEXywSC3YlGuM858WjVY9BZ2iccY1ev4qXbIkiGns1kN73aqDbHujPBokC93edhHD5sQ80GvXQ4wYPnOgBVd97'
        b'LJ40H3I3Ssz5FtNRDdNufcx0VH9blFC4UWLOt0EJUEX06x7XBmOvdel2Racj7iITPUeSPCh7v1SAmsb0+mf6pQLiPXePvYTb8f32OJLu5iBGsfntvIs+c3FASN2dd5nl'
        b'e0agvt/GAYkwCIJev9nNb2AkfD3JBLvdZ314oB9t3mmuxyx/+gljT6kiq3R7/1TRG+AgxiOq93iICKn7juNhtVfo9TsfOx7sdv/jEcia5/edRoRV29b/iHiDlCEPEkWd'
        b'EdwkKtCGGDmCfHjfMaH7BM7AfLMtCxizkR4SMgoDjc1jzsLo9XV2QNg9ngRL7j1E7IFBoYy0ZfLCIAaIVdrZ/wB5A/RCmVmeA6TpizzD3UM2vNeQSbGWKSolDgKV+h8u'
        b'P73eZrEbBdNavf4w7zo+xGi8Lw+DFuruhPux79aPYe5+DOuvH1WMQCZ+9474AwOtNZstrImn+ulJmLsnPc99t64McXdlSH9dEVf3hO/cExULC6TXv9BPJzxw2OxJheSe'
        b'7S9E3mJBT/tttAd0Hx3a2nO9gt/Eb5JJ/ZBtpz2SiVdVvFuH4POdShgzAAsaBOvYVe/eyXt651SsqzHXGql3cJ3BVC8YHycr++r1Yp16/VXeFR1dFDB4esJ7Y4i7v67n'
        b'+pePqTgqsj0/NjU9JGUwcjCLp1at19/tVw5lt54E1rcHbPW3ANtgtur1D/oFy271DzacgbWJIDk3CW0Wt1pbvedlAOig9On1L/cLnd0alIhRNQgRQ0W3zkFueq1fWOzW'
        b'oGA1DwKWD1vgBqjyex7Qgj1XP71poUEU+18/dP3TFbMaWYJtoFEz7xNOkAlyyrcioSmb6EqhOirfwp8W1460YtiAKPI/pZU+Gst2nk311ZoG8zpx73pSkui9YW9oMNPA'
        b'P4/4pAQnNwlWz0bXtDnVa+yGeptpo9FzYTlVUFO1yQa6unF9g0sxfawpBEaBAdfr3+ghI2oWMjTQczSkh8RxpUOiTezle2h5WqrPWmu20RBi62k+0NteDvmqKmOlzbRW'
        b'DB0N5LjWYLXpRcuwU663W2ot1KXYspsmPV6Mbjx1qt3GCD9mihX3fJkhn6nlll00YZRnP006aXKIJkdoQiNGW47R5ARNnqXJKZpQ4cZyhiZnaXKOJpSfW87T5EWaXKIJ'
        b'jWBquUET+jUdy02a3KLJbZrcockrrjHWhv7/4xXZyzWlApK3OSn+qVol5+S8nPP4ARoZHtHHEVLGc5oY+B3jrwr085epZWq5Wh6oFP/6y/wVavZLSwLV7McHSqUf8VPE'
        b'J3Rkr5XsJu3MRZLcwC1IHcXb5eSyl5OkXPpr/VUvJ0lXZNQqOYvRqmZh3ViMVhrcTQrrxuKxCj4sr2Jh3hQszJtKCuvmz/IBLO/DwrwpWJg3lRTWLZjlQ1jej4V5U7Aw'
        b'byoprFs4y0ewfAAL86ZgYd5UzOVSIUSx/FCWp6HchrH8cJYPhvwIlh/J8jR02yiWH83yNHSbhuXHsHwYC+2mYKHdaD6chXZTsNBuNB8B+YksH83yQyAfw/Jalo9kgdwU'
        b'LJAbzUdBPp7ldSw/FPIJLJ/I8sMgn8Tyk1h+OOSTWT6F5UdAfjLLT2H5kZCfyvLTWF50z6TOltQ9k7pZojINc7BEZWOYayUqGyvMZdQszRlEj9eU9JxI/fBa700s1yFO'
        b'j4ekGHO9HqOOH8wLpdJQTwlhhVHyq7OZ2BaSy1eEBTVzedxRdxFxr8bovask7WV5u4dQ/czj+Gw5JbsG8YSQYK60U8XCXbNXbWaLq0KTTTTxia+6tobmp+WVpEs1lD/G'
        b'HdArk1Ul+boYNBXMIAnViTt6nsd740WQrr5K7p42i5EOiFd9BivzLqWNYx4oa6EmQ22txk5FrNoNlNF4nRv2etnNYKnWSMkL3RqwVnGU11mCKb8bilr41T6WKBfPszEr'
        b'7Gluk0wA/qYXUzlLFSxVslTFUjVLfVjqC5In/evHcv4sDWBpoCCDNIhdB7M0hKWhLA1jaThLI1g6hKWRLI1i6VCWDmPpcJaOYOlIlo5i6Wjg1DK9RuAgHcNKxq6vaeS7'
        b'xp1G6ejpFSDvyjcpGuVdsEJPc3s5K1CaRnkk2iSvH8ZKlbTUMlFQAU+f0Cin1s1NcttE4PHy7Tw8P8cWLagb5aId2hZDyxsV22UcWvOnJagFergqsIVjT5bbtE3QCiaM'
        b'+uRb7lKpYIq4APosl4EXBGMLGU5O7+T1+kcK/QTrBOujCb0rqTFQ/6weFy/RGBzr9C8Cdm+qk9wmleLmphhmVKY3CU6F3m60WWjgGPFIhDNIjEHuPg5noYeWLXNpMo8m'
        b'NMiNGFYln4kD3icnQeATd7Ghxga7BURZI4BgooCK7QvYDE6lvs5azUCvpicKFXqj+IedLwxwvcY+oQUvVdbQHVgW1tZgs1tBHrEYqdHeUEvjHtVXmaHFbFxNVaZK5jgN'
        b'IohIM9y3DXW2ng45w/W15kpDrffhfRpMuIbuG1uhfWzNQjXsrxhk2DlC32vIQXyF9Sg9q4DrOqvTFxppsVmpOzgTppwqmBc6J87ANNfMiDOhshpt0g2r1WihFbIbWqXo'
        b'y0ANGE7l6nX0O+EeARDq0ZPDL7DZfZ8Kf2VM+Atm3hq9Y2ap+5Q85ocX/4YycxPdKaNGYBpHfmNkrxEZdPxmSXP4GRrQHzUU1B7RTTaqNyC3v+ysEuYVUb+65/xmvBhQ'
        b'wWaWzrlS90UBCLepagOQYw8yOWj3Wam5swduboSruY8meofUok4EdWZbz/FaFk908GGl5g4MN8oN1zuWVl+wNIDpoKHOGxjqcO/eekbS6gVWiiY62GhJTwiiNcoNV9tP'
        b'EK3/HegnBGoa4wb9XppGjCFrtVdIB0CYazyFJ7nySDGbBmwXE57EitiWKZV1GuA1KqewADf9RIFK0BT3lFWZjBSgJDhA7fBAj6OPmxdYNbHSOMXGw6XJxv664m3Fsg3S'
        b'WDHsVexgz50z6j/AYMW4B2ty34gnj8HPtHlL0hIhWTAILJXW5M8HbkWcuxWzvA7g09Aixgrvo/i9WzO/aEF6YvqCeSWDXzO/GLg1Ce7WFLGZ92DfkuuXy9m/l09Sgiad'
        b'RUARPbBq1xk2WKXT6Jp6Y7WBKt+DRvJfDtzGZHcbY11I7vKq8miuxKM1McWLl5QNPhLafwwMe4obdjQj62bzairZiufpQeBtaDDTA1YgGtnFE/iDRtZfDQx4uhtwUIn7'
        b'xMzgAEgz/+uBAcz0plp1sE4N1UYP5Guo2WClPnWawrSsfFjXtYOfUOfAoOd4D2oPyFpztTdETUxO0YKMwa+99wYGnOYGLPoS1gs6m1kHf3pYtSZmweAgSqP8m4Ehprsh'
        b'juw3soMmJu9bgfvPgcEtdIMbIzpLgjhYT8+VSItDjK9RWFpUOPgx/e3AILPdIEMZPWOysXRAZtAI8+HAMPJ6KEBvKkXlaerkQ69j5hUU5GTlLyxZsHQwFFJaiP81MOxC'
        b'N+z/6Q3bW8ZP0GQARVhohNbUM/nP6la4+4vuDoRqSVZGCY3RHq9ZuHh+vKawKCsvLb+gJC1eQ3uQs2CZNp65DWVQVKmR6nxcbekFebBqxOoy0vKycpeJ18Wl8zyzJUVp'
        b'+cVp80uyCtizAIEZAdaZrNRbtqHWQCNXiVE/BjuAHw08gIvdAzjWg3yL6pCIkAa2AA1WGMPBroP3B4a5zA1zau9JE3W2BE1az2G2rPyMAhj+9PyFlKZTJBp03z8YuB0r'
        b'3O2ILGH8XFQTYfIEijXmwa+QjwcGpO+h5lIkFnYuUgRj7DH6eOoagyUA/29g0BXeJK6HtFGncQ21U/ViHvR19/7GYgmcNZ9520WxfUDmxdUwgl6LZ2bpfgb8yrdDqqfP'
        b'K5h3noK+qWdplxJS1WmO85igRzOLRKdqaqlyyy+iMNVjM+tf2ErQqi3v0i7SSAC9YzQzWwMNYWApRz2b8TNQf1tAfvQbalKlRpnk+IBAg41innfU53Pj8N7KpMc7/c8S'
        b'tZsJLv+uEnEfoP8povsOZlnP5lMfxdXtVdPvKcooaX4sgXTv9jSie7XVHv48vIVuLznl1PDwGM86tWSW0NOvhkl+IuwIRj9NER/sv8/hHk0RQ+q6R4AZs1xtUbBxe7yb'
        b'X62xXq9f16st/RgO2HP52nH97UExgwbbNXIG9jJOzXBjTQ/C6F244gzwtk0pJdOUSuLQ7Gu5TqVkllKIVik5M0rJqU2KhRhx+nsZpJSSPUrObEuBvSxPfp6GJ6VksVL3'
        b'GKxEY1Ggt0HK4sdJqGOh36mysE8+MSQbTCQ2yxuQ/JRae+hWl9pfzocmDyJohqJvGI1vGXajbyofOEyHv69aplaw77j6j8b3/dYGNPhrs8nuuPzcBOrATgP7x9ZsmK3A'
        b'1+JIc59oivSflW5B9uw3CXwzYl8BlAly91cAFdK1kn0RULxWCSpBDc+qHXwVJ379r8xHDMVR5sti0vI0JAeU+rEngoRguPYXQoRQeCJACGM0LtwZ1gtxc02gQ7s2w+Se'
        b'S5kebaSkVM+cK/Qc3SbW89U0CIFMcLMaOZPenT7uL+/CZZ1ZMNTSj7KN7W1xpND0njscVpfvxRCO7aO6KlG76uhNn+j261aZ2z9K+krciH7gfOsz709QQ3a6jXn9Qhv0'
        b'19gkUWAsNyA0hwvaYEWccQPX19Jvfe7Jps4KLqeMHj8QGmTTMv7xFdPFvsuDWTxuGvpS6cd5SUjiiwfMPiySUZd2D6i92aEEldHj/wt2uPfJPZRYoueBAbfHCzUzuVya'
        b'rKE2ACwdAWAuWatl1slwzdyX2DW9kq+WWWbZFOJWFuSVXSrq1Me5/OZk+Y90nkJqHQ0MUNETaSG6VyujvR8XzEbxKLx41ICFfnEdvWP0HYSZdteiFD/IPoFeTaQJ8/Wg'
        b'8wPMqKEBlGHXGQM/DxDs0cc4TskMgnDALdlIEbj82d8+bJUNLzzfP+74Srjj9q/xnMm+eEM/b3jCYy6H9gesrxDl9q8MZ2tEpNmNKB1t5yTAsnwvYdX9Aj35QOnl0/70'
        b'sAeVQfbxa6hXd5XLk5x+jM/lT0c/SefkbH3WGCRdrlYr0UZdf622mW2GWiBBdFfIOgcuKFU31zXMoV+9sNrrHiPdKNh7p540JuypfG1gb8mmxxWGIUoPjvQIAUwmiOOk'
        b'0bckuAWDAaKajIGHNsmkAQeGqxQ/76eWUYcQ6vDBvttEbuOjKf1wYNJNWqvImXgAlU4uq3L9yVkvRjxE+mvdw3kxYphW9iM7oSiTUYcP6u5Bv+Qn+FI2S7/ZJwRStiqE'
        b'nAgso5/hVQDLDRXCgM0q2HFaNY1t5Qh1DK1SCeFCBJQrjSoWx0r8dK9KiKLXwlBhGHMLUQnDWX4Ey/tCfiTLj2J5P8iPZnkNy/tDfgzLj2X5AMiPY/nxLB8I+QksP5Hl'
        b'g8QWVcmEaCEG2hJsVFUhY/B2tIcrC4Z7odB6rRALd0KgJ5wQJ8TDdSi71gkJcB0mzJAid9HoIT3fPAyEfgaznoY5wh0RjiGOSEdUVQSLlOVTFt6p6hwiJLdzQiqFAqMh'
        b'Y/GyaPSwCPp9QGEq3JvJ4EwTprPyIUIKW0iznP4U/1yOCk6u0MkVaBVOfuE8J5+1wMkvKIa/JU5+fqZTNm9hvlOWnpPjlC2cV+iUZRXDVWYRJPMzM5yy/AK4KsyFR4oK'
        b'ICleQG+U5VhMjAQtzCrUBjr5eQudfHqOJZlSMz4L6s4scvK5WU4+v8DJF+Y6+SL4W7zAMpU9ML8MHiiFxmS5l7srkDnzR5C+ECAG4pK7w5jLHxvGHPX+qrKLd3ifvpXn'
        b'27MQCyF5nHRRjLfROKMzChJIex4NI9oTPJSF7UzIYocTc+Oz8hZlktb4bHqqk36CdA5pCsI3q+eYcv6+hbfSXaq/K/f+ofz35W/+LiY0xpBpqK2qrYg3rHj156/d3Dvp'
        b'yLa376TIUM1w5f+s2aSVsTD8GNbWbD98gTSTQ/GZruORIeS+DF9OK2WnKxeRh/MJ/RgVgKXxA47z5A7Zu96Syo6KVuSSFvadY69vHF8iB4mjMN51XPHJW8O8ixy7D0mK'
        b'P9Opl+DGcE8c8v5usKJna9ryOU36/4iETHxivPsxN+QblC7Rc6DuY5Diz0+8AvP324JKtTTDFJz3JyjVDGl8pU9yi6tMjNjT8wlKdYsPIJIPIJKaIZIPQyT1Zp/+PmEr'
        b'R/19hW9EPgsYS46sINtyXFEEAWl0uEmnS6ChZ1ncVnwhPrO0cB1uzsTnZYjsafAje8k1/KydKqgLBXK1513ArwLdYulAdjZpBxLckbMkhrQuUYfjPYCqcoTv4at+Afic'
        b'+PW8E7NVNMDy+vzx5f6TVWVIPBh+eBHZYw3A3YUBPBJPho+eyR4fstYHBSOkWWkuj78TVodYNJn8TVneseNdh6Pp8XCTfrEKLStWbQBcvcgiv5Bta/ErOVl56VNz4km7'
        b'lkN++Tx5nnTr7XTVriJ71HGZ9CQ5OZCSlISby3PQWHxLlpSOX44lx+30nNrajIa4fHqouD2v1OMEekyCLoa0JMZm5XFk9yhk1qqB93RU2GkIjGgTfiGHtGXlJiqn49tI'
        b'GckH4lPkJsNCMfrt6dEhcXSkdcqnxiIlvs9P5aRA9viSGe+JE2ehP2iN5OKiGBYwvTBGbBbekSlDo/COAHyHHC9mEWfwmUiddW31UHJDjjh8FJGOZWvtaXQ4TuDmqewT'
        b'jNLnFxvWkhslMTB3bfHxeaViqPu0SPH0fU+oSXJW5g/M9Qg+btfQ6h/q8aEc6btxZFeuTonCFsrwPryPnIT1fIfhCj65hbT2jBxDlJt4mxSRv6dDiygwHu/iEb6FX/Gb'
        b'oubFLhwgl4DWHKCBPjcirjRvM8woA74nXwZDfX3dWqiudR25YVOigOE8vo7b8VG8Z4udRrkgneRumRXuLabfAYjJxi3kJR0gANBDBq8opqdhSgrrri+KiGafJyCtW8ih'
        b'ODoi9FMAiaSjOCYGaF1LYn6px5cARgJub8UXfBB5mdywj4X3QvELsX7kNrlpJXfW4PZ1Fv81eCs09DZCkSky3DxzNosXVE5uNJA2+mkSXQKMsALeOyiLIxfwFdxKTjG8'
        b'//4M9j3JmA1p5bk3xkYihlP4BXKpwCp9GpIcwC/gXbgLnzAFffIWZ10NLKn6cnBpUVY+mRt8YpT5i9D90y/++i3Zej7xTZ8//b93x752CP16SPTH8+b+/jf/bD46s+C/'
        b'hm5As98Z+99Fawt0//mzqbfUmZeMIYd5Q4B+btfctoqy7M68P4YHhT9/6IZPkUpR9lRySM3qe2vejK4O+ERY/EXmHsuv//b2nMMn9tU8TFt0YPvaiV/uT5n1VegXX7Re'
        b'Ppj0C1PFhOmTfnVKNWxxYdoXPzTNUTy46dvZzu0suzJ+wYvnvj/xzHl+d+i+DV+PXv1e+KLP/z/2vgMsyisL+5vCUIYmAnYcC8rQiw2UKCBIHZRiwQJIR6QNg6KioiAg'
        b'YAUrYkFUVBSkWTGes2mmb5pxYxLTNn2zMZti2n/v/WaGNqDJ7v7P//zPhggD33d7O+fcc953vNm9mp0pI791+sFwu9ODIwmK/TMX10T7bdzkXlJT8Ellu7eR68L4pLQZ'
        b'E1fe3HPw+V8qvReYPFWp2oobEj1aJ17LmD4i5JNtif84Un/jweG7n4dWtCV8cjr73UJlS8HCJ+98+LfKoZHPbNib/e7kd5/d8IrdNpMd+Rs3jnpw4elnag1HbPJ1/tAz'
        b'6GlpreuKPS+ufSo25fS1jVPXtrquDbEu+Gy503sJraLRlu8uPPHT2Ljk7R8E/VixSV67w2vje/IJ7EBcCl2wX0qXas/DsADqoQlarBlggBM5/6rJ2oId86Gcp1ySwkUh'
        b'NmBlGk+kcNYCKvoDDjgsMzBfxSMo752xFirWmJoY5WI7bLdXYkeeiYSzzBFFQhmcYpA+GVDlFRKO9XjNSQ3pU+3CYwGVQxPdQHrwMLSlwWHcjWV85k14Eq9Sak0ol5I6'
        b'YBmr4AUhyasMqlkNycc9ZJOpMMvHjmxsV5lIUuEQJx0mTE0cxbAl8BgcC2M0EsIpQTx6RYI96yAjIrV0OfTleMAWvLYCSxezxNAhg10hzla4PUzCCQsEs+AaNjIkJ29z'
        b'H7IEt5P9glRd7CnYMA9aliSz9k5ZDltDcHucrZpkCi/hsTyqFoz2sVfmG+eosNOMLI9KMwMTI2w2yyerETvW5JhI4FQkFyaWwJUxbjw0RSnuXuzghFWhbgJS2H5OskSA'
        b'58fr8Q9LcB+VrQJhC16EJiJ4FAoC4ORyhtuNZD/Hy5ShogLOB4ZBeWow7nSmaOYjoV28Jgb3MUylaRtiGYuF3WpKR1QRSkSeOUKSbe1yNj6W0BDG+Dm7twPrUHFUmsls'
        b'EU8lXw8X4QBUuNBJppeOjZwkTjjeEXi0CjKYruSZAjoobQndzfQ4abgQa+IN8qj04ohnPNTUmOH0bCZFYPnSdNJpY7FBTLamVrjMw16UBE7p5tAMFC8yVhODdYazobAM'
        b'nMCguKpCBTEmnCRIOAyP4xk2xIbBdgzd28lZEWrjEc7IVwXcSKwV5+DmANaPEeunU/JOzWEyQs6ZRorCho1hLXRIwx2UySN/nRORJkJEZPZtF+LpNRGs4GXS8eRhsGMQ'
        b'EQs4gxnCTetX2pJNnQJiQfFqKNY8hDI1i2mQk5Czt9ODq1CNRc5pefTAWAOlEeRFhSNZgfxOjrtVpKfHYqeeHl5ZwmTTNVAVTevRjeFmARdELngMK9xX59EjBWqHONJV'
        b'wCRwjfhNFthOF7lyTS8l1IGcKFUTjOBoOFzJY7wyO7HYlqaVB/RPTQ65slC5hAvl9OHSsGF5riSBO0nR2JtFVheFLJmW54k4vWMym5LBsAfP0flAXtWkkRCNVzQFbuBN'
        b'vAkVusXr/zw9KrMNMDE9s7+Y7m0kMKCMqEKxYDgFLCU/rQXDhcYCMa/oU+9MoTkDwx5JMbiEFiymzlhoJCJitlDSwxeU3odJevzGrMFWfcRv3gzMawBG6ogkjbOwmBrM'
        b'culOmEuZTe9KE+LztH6/EmVCatLqpL7YKfqPB2EWLlBnmruAfmOZsIIi6K/MHjNf0LO/OgdQLp7vRbKqu3WPy2uqH8u3aTAUVa2hu3dRf9TCHTm4Rfqh9iLYjvGRaOIb'
        b'+PrJ1LAmfThcH8/dVd1WaazaTSl2UI6bX7UVcdTl2pSm7K7bHyLPVF8r0GvhQUqnuhpfuk0U82miHk1/ikJWO8IJqrys5ORByhRpy2S8peR9J5JARr3su32raD2YX/Kf'
        b'afQj/A8k2grYM/+DtGS1w8Fq6uBBejwpk4aJJP6pDjCO7bGGB6mEobYSzPuJej6kUGg3rWvgnyDQfQRAsbG2yMkDAxT3LlhdLttMtTB+9ITQIr7z9gGOBq4UCtZJNnDM'
        b'PiBg9gFuo2Bx961Br8x08bvppmN1ZKUlCx6TjDVVLr6vEuiACqT/9SL+6e1DoZQpU7NUGYmMlzUplyGEy+JT4qnnhc68tOxJfhlJ8dQHSTaXRZzQQVRD3DLHPTXYt9qD'
        b'J003RK4aBzwuLipXlRQXx7PGJsnsV2Vl5mUlUCZZe1lG2srceJI59dLSgOkOyOmX1281U7h79XU+jyXIe38V9HCqejQgelxcQHyGktSwP4ofC5Xievwn6DfEIkVaUuZY'
        b'kZIK3omeoi/inl1pkPw+EUoNJnqWCzo6POUChoaaSaSnSxpJQpDTU5YgYkQNFGmuWvpc7oiTU5J4DDPGWbmpz5fNuom9jhRlQkYs69vuuwuawUBErwINWGY3NhlFwTcX'
        b'q6+r+5ybm7lvjXucnKq55I0V+pOkvQU43O3QU17CfdTKieVr4EK4gihE0IF7Q0LCiVqFzdhp4gqnnvgPEcRqAM4eQcwqVqgofuliou+f7isQUotKeah9sCOcjeLNRPQP'
        b'4aFBYQJohUoOzhGtztMNatPej50vUFLw5KC/3Frb+kWcs8XncS+stLO2jw9ldt8v4z6Ny0z+Mm57SnA8mREvcNw+Y4Ohx56Vi/Joqk2k3BMDiaPRWNstkcJOC6L5MLjY'
        b'atgDh3hM3fbIfjSEeDHPi2cqbMOuxCDcr0twJVLr3tmPZRgmU0+pnnrWuqbeOHbB+OjpRzLRlNcNxD8oa2v3a2xGxpEZOXLAGflpT0OxinqGTY7H5sebktCCdd1z0kFB'
        b'52TLKJNZeMlTLuRNRJ14cwOdrXBjtIATmwnIlLkK9czKKnkC62iicNxPHnlQMOU6qzSvH58TMgrWWf/8ZlVKYEIomQ/p988kpaakpmSkBCco4hXxgm9HrBp+bGX68MjF'
        b'f3fV88g+JeCesjeMDR+rucbsaTkfcHwMtb098CBZGxuZi9dZ6x4kTWkDD0aP0zaejILZgKPwwLynRD1Aef8BbnKdNzz9lzjZlb3OGAmUVB1eGmD14+kvyGp8YWVqsjHZ'
        b'm0Xc0G+EkLKa7MzT2arKyhtACe2vgsYYUSUU92N1v6Hq41Ax8J5t1+86g3lWDLBFD8TFTcsYN+B43Dcd7PqktyfHnxVNdG63/U9IsSIq7frFNwVK+mf9420h8WQQMgTc'
        b'hA/E/oIAkHaLdf09DI5yg3WkQz/VjXcbefzDjuY/ccBOfNd4MDWxj9fmv9OLxY++syQz+pMRH+gpqWHljdxih3hKU7/sybZdyR8dP+h2oMhjDDfhJ9G3Pywj5wsDgd0H'
        b'F6AIKxyp+QbPZFDO+3bsVOYxL1nYDpsHm/OJUNvP8gKN0MnblyLhCEN7DXPCo1gl4QzwmhB2jzYYYBBNBl0Nzv31b95Z9bEHkeY/ecBB/Nugg9jtGMv1uk4crRmAlRy7'
        b'TqSX9cZMQdBc1wtLhzDhpNelfale6Qh2zTiydFTp6OTR2qtG6aBXjb3GnzpwWfYbf0cFT9h8Hm7G03swOIXbQl0k/EXYCf7gYPdvAqw3leZiO7abyVLppQm7zTGHk0K8'
        b'ikfF7B5pItRBqxIvjY7JWxhIBjIcztMbnYFvc3DbWimZPvWr5RIVj668D/cp6T0MtzEAd3FQuRpO8LQQW6AJD2OrSsKYCkmRHOyGnXBKxVMJiOGoFDvolcsp3IftHByf'
        b'aMI/qpiHh5R5ZCyxUYBlHGyDnXiMP4RLyEQ8K6WdYURkxoscHCCpO9mdllwPtyopNCKexku4h4Pt7pPZjU/qAnoxemcKJ4sL9ZdM59jb86BtOb3oIjkpwrCe1NBwInvg'
        b'jFdkfHugOZc1KNtKNZX+uiN8Jr30gi0+fXsIm/NysS0y0IFa1PlLr11wwLBwQiwj1YSrK6DKA3d54AHY5SomA3OUw824Gw+pqLZJxIjtzr2uXTUYKwvmL8Iaj+BIfS4a'
        b'D0jwHFZje0y6aghJZOsg9eC4RdDBuXFupBc2qyia7Kw4N9wr4sbjNs6Fc/FYkfHj77//vieF3njZBejPiXM86DaaU/nSQovWYVOItiAsC2SM3lUuwdF2WE5qEGknx52L'
        b'AoOokFQZRqbGJBl0RNC2STJNlsOFaJaNPp6NpA4SPV+kE4nKVC7h6u5RXyNDC5xhV8l0Gp2Da8Z4aSZeUcWTbIKIBFZlQhLtNoHNrgZ6uDka6yS4I8okwIKIZttGGsyK'
        b'gGtwA+vwon/KWsPkYTlGeF2yxgC2G4YbQzNuxZOueGO9fCyWzXTGQxLY7yeH1iem4MHhcMAHSlTRdByOYatMD4uwyIRzMxBBczRcisEauOwrgXIshRp7KMYbuBN2RI1K'
        b'2whncPMouJE+fhR0QiWUQEfyeiwWudmRSlSNxZa5Q8OICL2Z7RhsnhnrjRRMEb5vKTSPK3x1uoxjrLSTibBZ1YNCVksfa2fnBOewXX332YNF9gJ2ShOsp7MsH6QEcru4'
        b'5lmCuDj7gNmzORWFSJbFjqKNOGjIyYzJh4UrVhFl4DxZ08cFbrAFG2Z6kBHZG0dW6Xk8FD0Z62NIjTev87SKgi1JUJaCx/CyfipcNy+YPV5F5R4zIvQW66pjoFOwnoUV'
        b'dXGBRjn5n6wpPGc4DUqx0w73RskFKqZkNFkQMYhMAnJokNZeg5NBjmTHIKM8zEDs6oan2E6D26BoQ0hfOlwX2K2DEVdDh7tdbpw2c6qK+sa5jhE98tqYvzReZ0AdI3aQ'
        b'ytHlvAbavKnEL+CEsENgBYf8VixTUc8Qy6mLHAJJt1WG8fPfJTjIiQz9rgjeSaOvZ8CCQKIHZtM77/kRTguFXEGUWQGZTaoIklUAVMziL+yDFqgdNtQ6ZGBoOGum8wKD'
        b'fOxYEBgcpnB0UkTz9MEaPwGfiSGLstnejJURQ6ABajPY4P9jopCowWc8zLi4jIMOBeSoY/vq2MkrQ5zpfQ7p9LoQETlzm4VQJsI21Xy2acEh98hweRgPNR+9CMv6OaBw'
        b'ZLafhc1kXPdg5TIZ0WQvw8nAcRbT4GbgOA+4KObIBlpkAQdn417mFTBZD2rpjZaZoQF5UgL7zLA1L0cl4CyVonBzrGUHUv4iuBFJtiuyzMuCRWSTO09ZTQ55Mz8PB7iG'
        b'u0LkTkypVpB62fV17l8uM4AyPAVbVNDI4Ka8yOBci4SqKKyKhqOUNUjPXgCH4CIU88fEniUm0nxTASlpH4c7NpLtcS+WsS5yhI4lpL5tykSyebTqc0JsEjjhbiiWD1HR'
        b'w5T0hQNWhJKkJtA0gyQWjGDphAlQHhKaH6N1zZDGCPEC7C1gBQoTTdhlb8sGzX0vHBZEsFOw0Bd3h+B2/saUzKJzLtjpzhKtW+7AHBJisYyy09gI4AR0evPMSKehHovI'
        b'xMHiEczZA86KOWNzkRXsxxssEiLGy5FMejnT7ykCP3+XSVRXPW4SbNZLxouufE4tsDVAs5ljLTQ6UF7nA0Kogc1O6iMILzg52OGBDfyy0eOMU0RmcAUvsHPVCHYvDgly'
        b'JOfzRcavQykIqqCWPTPDCwFY4aQIJR1Mrx8ly4VWYbiVtc4XD8zFCudg3MWopqcJoFGfjCDtEpdpCrLa4Wo0fUCaXY8NuIc9SRiKByk59aLZ9BEjp76wkXl5QB2em+Og'
        b'XtlkAtOlrceNg730zrHdEM5ascmEO/GqK9kKyqnGDuUu2i5asl7bSXqcAor0cZf3JF5aOoStNvSyXI5bbMnOZOgphIbZ0JwW/cy/xMpCIjX84/Ut/pHXMof6WB45eKRw'
        b'7Vcqi5tvKoQ5NrP8j9iPneNTtNliwXL/1EWXTrQ/v0S+Uu9qwKWP9ox/6muz+Q9G2OlNjX1S/+QHL9wpgrr1L3v//Z2DM1tnvTTXKWhPepR8cUr6xrC6IQXzZ8WuPVlQ'
        b'+9nuMx9NDtoo3/3TkjlbtrycPj5Y77ffX/C4vfbKomWtFzDAMnHWhPvK1ZYlVzym21s/XW9XOnvD0qf/dvnSy1s+CP7kxI+S6y/+Zn20+ah/zfmlr6clNsrdRq5YE/CW'
        b'm23VSWevh+94bLSVP6v6p/TzMfX/WO4xI2nM6W+++Ms6yzVxX969va/1Gfk/lL9HRKc7VUi/zvn8+qzEyOwfRjsUXrwddzA3dUvwhY9/GWPvvfRglWezUXOsMkbyeuwp'
        b'j7Bf3V19jkw58fW0E2J8+pVOp2FfnHpe9tYrhUVvvaL6bMmakZ7fSVI/f8X00lI7r9/TZ88flZWe/eUrxd8vuv3Vj9Y1okVBu369n9iyt3SacOOzz33/wocZa5q2P3jR'
        b'ZPWJ0PjCWzPfrqu69emrW62af/KsNnPqePWllTavF3qln7Qc7ffAYmhlQeelh2bvtN95Y9QhiJ/zjEN7ZYromQMzAm5NeNrbJaG0ffTTo9/yC/173YgleRtbh79a/rev'
        b'BNcjfn7a1VD1ryOKz17oMlO4NR0zDit7OMPs/e+Gri9s874v/inr2r5Xv8z+wu3W7xttC8p26H93eXeN84Q1b06+ErP+qbK5b688elXU8l3KkHU2yWabA79/xf+a953P'
        b'Pn1B8ZHBTfnPkzZ/W3NrTCx8aHTx/YgPLD/88s7cd9ycFO/84N5w+ruMNxxWf3xy3yRYn3n4+7uHNyXpJb+At1sDC9PNpwcbvdaxbOhyg/Xw8IXi/M8nbXSIGfu7sOWg'
        b'3q+vhMptmTfIGHN2Xw/1C+kR2cOlgSyQPKozTQoyZvZSYb4AjwzxWQ97eMquzjQ4pt1/CnCXC9mku5gTii/ZuTfzLjBWZGPtRVBei5eZGqfasFDtSpYIxWTlGEC7MB9r'
        b'sIU9XQIlgpBQfdjce1ccMZH3bqihQi/dFvfjye59ES/Cdnb1v5DIA2eJ8mlMpNwdPX10YCs0M0or8rgcLlEBYCOWy9WkIfkxzMNjCZyCGw72znJSxjHsIMq04RKycC1g'
        b'G3scvhJKHZyxDI6Qrb/ckexNsEPohBfwKtN8F81bQE7KIHut1wFld4mGszw1yz65kjpXULElvFt4lXBjQ8TpeB3r5AV837ZMxeMOzvINk3E7KV8C54UelktZzYnUeXid'
        b'g5PdhOmBGmYZcqI25DEuDj+VEqoMckzwkpK60nV7y2BbtNphhgvDdgl0xcAh5kqBTbh/Rg/rJHTBRWqrtQgSwTHY4807Fe2eijUhGiNxOOmX2mVk2IdgqQgqfWQ811j7'
        b'yqlASeNDzV2cGI2gPmcWLkp19GRD4jwd6x2IXAJtjnTo2GMpdgmxMxeO8BkUO0KJWsi4uV4rY0xTk5CRnbyFHJTkvKiFTs158cRMVr/Z8bCz22uLCKX7tW7MZHfv4i0S'
        b'58Mobb2LUz4ep24vzOkFNs9kXka+1gU67RGWCb2dOWaRXmPSZxGcX651FcJWcoT39BV6IipvEhMW4HxSf4cWclRf551aiEB9Kph3CyoZlUrGe9P4YA1zjhluFmWJs1jX'
        b'jIokda4Iw+Z4ygFHKXOkmUKq5vLOPIlZHD3ayGQv0Rxu2DSMb3UHnBnKZIGlMo0oQNSgcpZtdng8FQSqXHsJAiTJTVZ9ok5ehIs6ZAFHLNPIAlW2bADm4b5lpIJOzgo8'
        b'DtdDNU5D1rhNbDEc6vOYm3L1Wl2dTFSgTt3GTmr1eQLO5FHNc8WU6SGhQWQPiiANUNjHT2C95kW68hpPboeHRmj47SKhTG7877i9yEf/FyFV//i3bpO7WR88SWbWeoV8'
        b'62fWcqcGWANG8GLOSIXMKUmekAdKM1BDplmT5/QpNU9RQDYK6y0mn8VqzmFT/h/JiX6yIJ9oHhaMZM+cOu+QHIxZuBeFYaPc9qbsJ3UFMiV5UwcgIyEN4+W/uuFihSQH'
        b'IfvJf9FQXUpIY6zOi4/L0xrK+jS7p+cP75XD4q6G0m/DmNNP0lqtw0CPMKZuM57V/7XR0/gNWWgjqmgNGbUOX6mhWuchHmeX/Go/oDXxjm8v2sDBOkkuYFFcikEuN+n1'
        b'poAh4z76clPErO3i+28LdTgC+CTnUWrA+IwMhvvZg2+XVCqN1iY+oxccKA8blZjIo+LFyzKT1vTLlHcgsYuLm786LygzOS5OtjIjK2GV3FkN3apxLVApk5JVGfR+vyBL'
        b'JVsTz/MVJqZRisH+XMA9K5GWyV5MZlHv6lDJJCUfP8kj9cko/pAsLVH5+GyANFjfSxbErvjJ/FOmUXhUUg697o+XJaiUeVmr+Wy1TQtKjIuTUyiXAb0iSP9o+oN+TMuU'
        b'5U93phTTvqQb19DOzEuNz9PWttvxQmeO6rYxzFbmI8S7N5AMKIJrry7SRKKm5GapshmQm84cSdPz0hJUGfG5vAOHmhGexyBQyuxoDLgj6QJSLIMGKcgmvyblJTjL2SAM'
        b'4MBBOzQvSTMu6nFn7luZfWkf1aOfmMXiYLMp2q+uPHsNwCC0iQJOF22ikYK3B++Dy6nqYBBqABdjsakhtPI2cCpTWcGJJ6RDF/SOHNBGDSyNZhyJZmFQojYLygxE1PZ4'
        b'NccVq0faBA61zSnEixFQAk1+UJ0jX+oblEdO9OPQbOCtcBxDJOjjWDsXro1dB2fNXZfGMLuNYmmg5L5IJuDi4tIzhGM51UTyx1DYu5FqymGRlCh5J408oQE9+tx4KHVM'
        b'FxPdunI5S93uoDepkkbmzInL+EThzKXdOOMoVOZTGcHB2/b2DZOtrpb+93+uq/pphMwvsWhKhsDK5MWaXaFbR98+afhignT9a7JXxxR6nRqyxO71E7GvFDZve/1wQNjL'
        b'916N/XjsjMxZH03etibLeZGe20dX3y8eV5X/07jzC48+fSP+8surx4f+/c3XJ+Sfj53/whi3Y8t/2+Y9qm5PvVzKhEY8bBVAVZP9Xn1Vk+NE0mfQGtG4LUSWG67xkm+H'
        b'q3levFjbAo29xI08rBnsapVdrJLh4OW7LqLBXFBSA6mTncZYNAR3meE+ETRDVTIvtB1eFuCwdL5C46nNVBgoxTImsOba4DG1IzpzQt+bhOfHqp+N0aNu6ERK2heodUNv'
        b'wf287H8JyyN453sm3q9wc4Ibdqw/IqEirU9kwQS4TtWqmcgLpiFwDJt6+LDzUql+LC+XYkcuL5huJ6Ud6C+ZwiHcpZFM7VZoLrse5ahhSMPh2CJl8oidLnlkEzeDyhBU'
        b'tiAyhojKHVTi6HNVr82oN9Whde/DW4fLhnXvQzSJ/FpPD1GZrkN0M/eexcDuAto6UNdLcrbEksNFCwSgiQ8dyGlPVCYaMDpUxG7axPd/FOs4QSOTMtU4nb3BwVVK/kRN'
        b'Ynsa2YD9fYP8InsAfg90DCWtTEtQxiZkpJFceGJaDQJSMkUsTEh1Zm84+9Pvfuy1gXDEe+Sq7g8v5vbnqPX7o8i2yiRWzazcRPoHssHr3IDVuOgD1sE5IDo0jqGeqbIz'
        b'suITNa3XdIjOTCl8phbFjJ4Nap9XpSotj0cn11ZK97HwyFr5+UXFOf7ZpNF/OmnQ/D+b1GdxzJ8ude7cP5/U988mXezv/ueTesTJBhCeHiPxlAE8L4OSeXoUXpRJSnSU'
        b'2aunv30v983e/qXM70y37DGQ12hAbjwDie6ew3/EQXQRlVb5XSHfw9m112phjq08OCu/nEiB+Wnxf66nfKOidVShm7ia7jF8PfjllpY4iIAl5npQsGoFrKE8L/XQSSyo'
        b'2HyXW2HomYlPcOz6xHmJNW7Ho0opvWw/xsHB+QlMGovFxpkTyUHX6urqqscJgzisw3YoVVHLpUFoLNTPc1A404u4fYKQ8FksCXbMxiPQhW0OimAhebJFMIMIFG0syZwx'
        b'QVDl5KCgtgYoE8wyCZaL2a2Die946OTYhRRe0uNEIwXe8+E873RQAuehNnQBedich53kPMcawbiRsJVdBmIdXJztk6Z0J2eaIIuDTjfYzXLcgM1WeN1biR1m5NgS4imB'
        b'fTIW8WlKiRhxDfdOgRvk6HHhXKAqgg8zLkrHHTPwJO8swDwFsEQqF7L7BixZHYgn6YVzj0pC5UJeaq1e8cSMib2riG0ZLGEAVmAbEbGae9YFDrixjh+NBwwWx3RXPwR3'
        b'yEUsmSOcgf3YMKVXeY64k++UU6QBbSFY2rtIJ97hwQ5qYBvsCJXmG5LhFxkKXBa5sXsaaB0BFdGkTSa5ZhwnchTMHgPHVWrDZ9e0ADhP79ikpgJOZCyY7Qa7VBRSngh1'
        b'24JDqHAbyVxm6X0tkXY5PAF7NpDhqcRiIidVQ20U+aUar+NJ3EPk6Goyo/bCdQs9rFmpZ0K+hVFfj1myoUQetDCDM9hunHbsvrNY+R0po+IJo+hXvBV/cTXXe/9gzrTD'
        b'X2ZZT5zoZa+45fTX7M2vjn/q2RL/lhI/ga/7GD3bktdyDOb6h70omKFn5fKc9bVcj98+KXCcmetn4iCf/Zxnu6X/c9a/jd+1vSal/IPlJwNeX/zhkeTFQ19UPdxnO/TK'
        b'c16Zns033xgf1vyyKEtv0u7X2urfnBvsvyvOqzHN6LnCnZG/vlR43H5B4fceecnK37cnjrjy4SHJ4fqfTQ+PuSP8XnB45ydf6y//4DuXsyW/+2RdeTky5qvIt/zSkz4u'
        b'+WXshkLXHJOkWJ9zH147vv+VF//51SsOnz53Zs3pmH9lfX2tqOOTSpufBJuWRBY8MNu2Y3mX/RC5JR/Seg4uQdVMaA8J7W2Pl+A+ZmZc6DgFdsDxnmGpcBgOe/Lhpifn'
        b'UQ+WbQ49Yt2MHUX6ZEAbmRA/C8oiYb9Qc8ngkw2dvJGejJI9Fq9lsfN6nBiKBbh1jQsr0R2OhBnM6BVOCi1QnctKTMGd0IHn4YpDH9m8HA4yy2eAJRF/i6DegRrpqYua'
        b'AVYIoSiMNIdOwhQosfHAbUopttOb3goOz3hNYsI5Ho+RpRCdJHsqRTYoJSuQLJy9PA/5zpmkOpfhAn0q4agTEe7GY3iWtUWCDdkrSQ3JM5plOUcm4HVs52E4jhDV41yP'
        b'cE2sthLz8ZqT8QKr0XDYNmTVRiW7eYZTRDEiTalgkbMjZcnTTJVQCWW0Rrs4bJu0liVZgHUxBTkkiR5Jcpoj0/0IXuEjdI8qsG6Dgix2sssK4AKHRwqG8Ub2zaTnmuEi'
        b'NCvzc2hRBzistFzPCsKjI9YthGvkASkI9hElIrKAVd92lAWes+2vLBFNKQ0aBohQHMSxWKwkwjBTJRbqViXiqPJATYyUvVqsNmhSTD9mxFR/GbPoQSOhxqSo/UdUEAPB'
        b'uiG9fYRJiQoNpAgLKDTuKUDnJvfWQASaNqRp9Y5kbeRfKvl0axDl41YvX+X+9SC5i1ghCvr/sD4gTXfFseFBirvSWL/oiAh/hV+QfyQPRqkFb7orzY5Py1SHBbLYxLtG'
        b'3XFz6ihG+nKfUMb43iBPDPOJWiOZNsVaxXfQyP+XTOK5LlTVE6lh2Qz0zUV07E1FpnrD5wjJp8dGihSamxsLTSnvmHjaWgOB5RgDAfNnhK3YsEa6yL33tYWAGzlPnJYK'
        b'x3u5zRqrfyrtBb05yCgMFQ9BVStWg1DxnykUlSH5op8pJBUFpOL/3v3ZnGI+Jg5lny0TrbSfrROHkc/D2ecRiSMTRyWOrpVSdrNSSbIgcUyiTbEBxZys1q8WJEqrjasN'
        b'qi3oV+LYKv1Et1IKcSUheuvERFsG2aTPWMEmF3OJdolyynpG01VLq4XJQpJqKPlnXm2Rxv9mQXKzqDasNkoWJ9onOpD83Cl8Fs2x1LDUpNSi1DLZgIFO0ZwNmZ+qhPmt'
        b'DkmWJLokuhYbUIxLMRcjZf70Hnct6CrwY1wIDKwsOSn3oXsv6bH/C2pSr54vPXQmoqhXmjLLS5mXyH66u7q6u3tRidZrrTLRi64MZ1dXN/KPyMoectFdsSI8IuyuODBo'
        b'XuBdcXTEvPlE7RfO9SffDWmRseGK0CVkC6NK/109pkHeNeSpK9LIR71kogcr/0ixbrRYcW4OXU659JuSLlBxkCKSxy38g3l5kv2qd16561iGkXMX+jz0Tc3Ly/ZycVmz'
        b'Zo2zMm2tE5Xtc2kMqFOCOsLOOSFrtUtikkufGjoTDcDV3ZmUJxd2508+U+Ss3HksEPiuYWi4n09oLBH5H06ilfbzDWI1JD/nxxfQ/SyCGnyVeSRTZ9cp5DvZ2nL4IOKp'
        b'fHY0rPCucWSQYl6of6yvT5Rf4GNm5UY235xeTX44vU9Cv9wspdKX6SK98wjNSglTprCc3GhOwu6cSM0207zM+vTHw5EDN+qhlc7Ok0t75UKnW/9s+/zBc4C8+v7Zk/15'
        b'8FoN/MztocMf6J67+olJyfGqjDw2ZmwC/EeCDvqF0egK3eA1lxY8FiM1h2qt39052Edki8RDG/iojsCyCBrVMelJGvgothPIM/wHieq4a0CZRvPI5B84bol+zeOBSHtv'
        b'Os6atI8fH7CTNMybfFKO1y0PbOae6hUjMFipcn3+/J6v4xCP0J7kdDp/RhHJohS9ogqMND1M4w9ZVAGnYcfk4cmSjbQRA0YDRgxobgK36OuwYwbxoblp65J6WDN5khv+'
        b'Yolu3INYLyM1ZLSybEZFwIQYpVf/F51kfRaXzI7s2oO/RhfUI9/wlNnZK9PoLVX+dOdp9o+RJb9GZXZ+gY9+Wb1y6cuOskeVM/DqltkFRf2hFG6DpHjcnYBm0bfSAxmK'
        b'1cYu3irER02r6Y00APsDpaRnLJ+s77TJzk3Lyk3LK+Axce3s6clNaaPo2W2v23ZoT090+g49X+2podieHoz2cufui9Rpzu7Orl7qV3Rn033n6speVefa/edp7M981gM1'
        b'jEdxUDdNB0ID3z+TlQykYcDuYVcTXr3D7tki0423oA6bH7BO3cAKXlri1P7ICRTFQHvtruNWnf5HnjGWO2q7ZzZTduWfFJ9HJ5RSwwDWA4aCXjoPELtP7a4knzXxuWoP'
        b'gR4EDax3ZJFJSbStqowepGI6s/LzifKfFx6xJJay3oRH+sdS2pNIVkvt7TxPdTZgJ/GbEN8/jJpIjWiiGTeN8qa2GOu+zO62IrObCT6HbiOvfZ89xX5AdwA2Qtn8OlXy'
        b'RGl9thh7vnWaV9IydQML8BAVRIrV8MCmxmfK/KMjBrCGZ8oi16TlrUvKzWADlzdI5fkNcYC1RBZMUF58RgFLOPAOZz/wnFVja/AD0g25QWe+eki08Bv8xdQALcrjvRt6'
        b'gGb3StsLOGXAXYvl1O+mgHSPWmpSaqZvn3x1j4maO7C7XMbZuDIpIyszheY0iEWdyiOG/UQoM16ESpF7417q67dLxAkDoBjrBXZw0o49m4cHJbw3A7RBizqkb3cM787A'
        b'zEVboGu80kSN5TlqKjZBzQKGfOgXj9XS/GVKk2yoxE7y1QrlYs4Ei4VYkbqUxWqZQRPuCOkB6amBF7UbLe+Oc+kNfxmmFyzkpsJWUyz2hhtyIW/53rIWD2ptv3jA0Vgw'
        b'e8J49sgLjsEptcHYHrc4CmbjdTirCiePzF2FPdBNu6uhDVDJNjGJoPimdk6KaDs73I6VLrjdEYvwGIW05EE7nag1b/9QwYqcAGb33kQelyrzNVCccBUv4s7ZeIZdXmwc'
        b'JWGXF64LJwQYCZw4FTXMKLDItwdGJ57FqkWBzsFhWE6a7RKBZaELAkURUE4j2PAKNBTYcnBTLMUDUJeWdt/nBZGS2mQW/OBgW+VttHWOecmaZNWm1712TVsUPCrQY7Fd'
        b'cXOMfXHg+w3PD/nOqM61Ncjjm8KdPyRPcTWQXhQHFG/1F+zMfXCy68POYVueC/rHvdrnLpQ036lKibBv+HT1ukDPBf/4a1LeB5dKsn6Ks15ncSLV495Uw7JN0w/eHzfk'
        b'/uebptv945tV1en131058uRy24DPh4198EzMz9euJt9RNTwnXfnSpI5YebrLgzkoN2HWxRBsmODg7BTohF2zqQfDSaFrcA7zEh3vu5YHC6bOD460tVBKMYNNI0Ru6VjP'
        b'7LqGPiq10XYUntbYbROgkfcHaVgJRQx9T+0N4p2mRt87DPuYKXk27oBijSE5LsonAUt5j/FivIwHNfNQBO0az+zZ45gbNFzEFrwohWbY3w+50QD3qt1RjmBRQLeZdm50'
        b'oNpKC7V4grlfRI+M7wfPpwbnMx2HrTk+zDwtx63Q4RAB+/viKK4IWMnMsBEp9lpTOpRLeOf2w/58S/bgZuq7wdZbG7W174W2MEEAHhzO0sbhebxIlnoo6YKVAmyGTjey'
        b'YJt7BfIb/VsmNy0UnNdAqtMGC4GR2v+UonSImXlWzP5R+l5ToVAwcgBFRw1/pujv4zm4zjOIe8ifQG4LG1Rfa7d5pL72uChuPLTaXb1YKtMOAjRVRT7xGG66itOSDzs/'
        b'htzcH3+NmsEiA30i7oopuehdMeUZ1WiavT1reb9V6sZ6V19NTp1bLegTvG6mOYUCOW3wOq9oGqtVTRMeC7vULNnsMULUNQrnGV0Kp09iorI3ibLmwNVhMdSKav311mSZ'
        b'FxUkveK0cCFxOm75HdWCjxbOinpN9ncy7UsUyLPhUh2+W5zNo72Xpxb2H0uNUgvAWsrYR2lSPLcUn1YHs2u8UpackRVPzQoyRmOqZm0cyMUmPrMXZ1pfQtiBatFLvdDF'
        b'2JqXtJaXnfO0RKereY/PAVw4yTtpiVTw6+6KbtY5vg0yO0Z7TpvGBLvxEQHOzs7j5QOIpLyjBHNHjqezqQfJsTZnnt+RF5W7n+vMT5umm65RPQXUTly9yRt15mEX4R/g'
        b'Ty94/GMV0WG+/hGOMo0Gw/NbDuj4xfyPB+Y3zcrm/bEHyWGtLqVwADLRQbKj/2l1RtrDg6l0Wog19azWmZuGpVqX9icjveIfofAJ7a/p6XZZfkztT0NhxXeFlueXTlj1'
        b'vKHrgijMSYzEOS5OkZVJd4pBfLnX5nWXzvhgaR/FZ1D/abpBaKducm7WatJVifEDOF1nqHgjW0paflKmZuaTpZlIHX7sErIylWmku2hOpOPS2F9JLw9YMT6bnqYJec9m'
        b'qlmPV6YnJeTx+4FuZSgyfMY0VzcZz8vKt4fWwVENvaluL7MV0LVJNkWd+SSrctlaY6udZ1gdUCPkTyIvWaRaA9Own1O39AJSSkYGWXzxubwexr+se29RKrMS0tggaPXB'
        b'7NwsSmJOe5F0rXqwyULgp73uzuzBIyhTEM0wPjs7Iy2BuSJS1Zytp55u9rrXjp+aRL2bqZQe0jI78l3uKKNHtcwuPDpCTgeDHtkyO19/xQDr0L5H3MA0uf1jRDNo/bp8'
        b'tFt9Hy6hwfxFtWqpgU61dKzasr8f27K0nvSzBVTzvImXmezDlKlyI7UnmPdGR32LdI65aC0RJVBtdM5kNbfEEK8Anl/gau446hc1H9rVrlEeceyB7XoHhrpiZUuxzznY'
        b'txYuRjFP/eH6UESx2vqor54JRIGFcmhW0VtlOAh1uBUr1DwHBuT9KDWSQIiT/cJAx+BoDWQDXM7ur83y2CwX/YdAxQI4z/syHYN6OMe02TysUzszjbFRUYcHPB0yXldh'
        b'M7CuX3ndhXVTxSyw0yJMyCWcl6sl0QGujGA9h5f8VURPnp6tdq3KVqgofaE3tkBHCEPdcQoOH4r7qbLM56JH1I0SI9sR0GjUrZ3OIfpvLXlwwgJK4GQUHEtcAOW+G+EQ'
        b'bIFz5Kue/Ny2ai3sglO+K1fAdt/ctAUL0lfk2i6Dg6tSzTnc4T0aaofMZl0xdwIFqu/I9sPrxkJOiNcFLrALD/FdcZZoVge1NetbLSwfAeVzoFoEu1dCSa8qleAJrKaf'
        b'qftXnBmWyjg4v2DIcLyAzWxOjFjhIc03lMJFtfsZnsLrqjjywAZKxFqTgXyhGl4nW6WKwl3ZJma4J0rd4z2sCdSIQIdFg8NRmZSqxqIh6uoZA+bjZopl1mSuLlRRiTtH'
        b'KGJUFmr0I7w8uR8AEk0V1WsoqVujyTy4gi0MZ3Au7oOSEAVWGmCTli6oCs7PZ3OG5BzCcEHIRNqrpwyG7RZkem/HvRFEBd8uwJs5JvNw+zIevqMDrkBzSE/aIZpPINHP'
        b'2+GARo1d2CtLKJFCtaUtnrKC09BgbSUiyySM4og0kClO75egEXfrsUb2bpgQj2M1KaltFhmdLUQv304d8eA67Fk5FY5zWBphHDFinaZeN/17mG9Cg+TBTs5q/o/eWEjq'
        b'WpnwywWuDtUsT9JtR1QWsJu06JpqCZ1TFXAK6zVADgsCu7OHPX6PXUJ39hHBlqTyF7CSt5XtXmzALEOZm9Q0LVhqwvx52H6TNwUOU3Ya6FzQl6AGulZjKaUvTGsdHyVQ'
        b'NhCt6vsFYWELZmb+bY75vTG5V07Ovd2R4fBPffmyT8w9fexP7+QS3t8ifVby2finLpXHxX0ZPE+2fpin7y776F2ik5a5Ykx690KqzCTl3ZRtHq3uu6NeP3S3xC4xqeqX'
        b'cXPvDV11qshLr/p1uYPi68/mqmJ+myd+47uP/nXs2ty/xuR8vndVbkdZ55WVrzWcW7NC+cmZnz4oX11Wu/XFG99/dCbE9rNWn3sZ+TVxxsNWXDlf8O2pwquts3x+33D8'
        b'zYfnAhZ+Y+m90e9nQVPl+dWbgt4Ml/wrbtH+VyNvPRC+HLs2+dWEtS/bvujxzcYnz/3w6pr3U+sPS7O+OeJ3eF5WRPj0qze4J0b//vBqpOS9CdnP3bZ6dlWWMDfohQ/r'
        b'nr3wZPS4h5aF6d95jvy5OmOZzbofs+/bv+ntO9t03YET954+tPq6Yn7nh1Peez+m8rUXn9w07x3R70N/Odzys+Knoa3HVh+/Mab9+nt/3+vjt2nIa0nnqsOvffn1nGNN'
        b'jUelKxSn9oSMezNl61fnh2ftL034eIR9409lho0/fbPu/pOBtq2/pT75xZOFo/M/UC4rP/RyPCZZrXnXrfP+wuf/+rfws5d/07f2afk+arHcmtmtZk3JC5lq0INsgBqX'
        b'0vE0czc0tHftabXipHhaQM1WqeN4z7om2LaQGq2GYzkfxlS5iLkUitw29PS4lEIxg4a5PI5ZetJGr6BWosQRPVwud8IhZmLaYDFXSzFCzkQnOw3DCNkGef/JdZ6MxESN'
        b'jrAxnuEjLFvG+3uWiaQ0zsgsso8lzA72sYo5Q1e41rdyPNzgzXSzcQdzklwClWnUZxOqntC6bdqGsjq7WwVRvNkgOC/mJHADdmcIx2fCDmY4jIcWN4YngQfxDGMBgbN5'
        b'vOFtD1yOg4pR2NHNaMFb3nDrLMYdQbYUcmjosL3hdRs1N4b5emY/k5nP1fAcsYh3PIb7KPxNOdTk8ag0DWPJC45KqKMka2JHAVxdCLt4R81jcB0byTE7D8/1sdwZqGEG'
        b'4DhexwvM/inkJOSgPE4NoPaz+bgrsvG5hQhwV2gQlLv0BSNyhcsSl9VYznrYEPfFQkVUUDjDpgonEoTpXJE3Vi9nPRyOxydrY8vmLKIUJ3Ky1TKZqgGLTKHCJcxJTiog'
        b'yfQWyuASHJEbPHbEstl/x1NvpQaHsYzKhbrMhpu4J4wExkIWlC40FtAQdnOhRGQgsDDnQ8lpeDplmdB8MmD+nRJ1yLm5aLhwOPlJ/1mzAHbKOWEpMNAzpYFnQmaUFJoK'
        b'LFjuNNhcIlw3Xoc5rU8ktQ5b5EBWsdz9vR1FH7/Te4aJ79cRK64jTHwXNVJOpJ2py0i5mfvWrqeZ8jEaqtuvhzKlMOsd7yTCJUu0Hj6iR+HGP4zrpxlEJGUSpVT5KBMd'
        b'sweodRCqgcYrZYvDQgdRNChKhE0/RcNRwVOw7cQttiHd/psLesLBWaxmV1KL7PpFhWItNJlYxUMjA4ryhSOURqwzTge9HHRBDV5gIoAc2vP4yyE4toyXAQJHsQzwmgyq'
        b'6KM8Z7KlOufjDiPyM5j6n09coTcd6ufyysEVPE2UA5K/mCRZJbDhYNcErOOfNc4kkqr2Kg/rBdGpRNNnytJYMYVuM58u5OIy3pycw/EYVJdS8CCFgXSl2Jx13BAl0bBa'
        b'oIKFdkAHHqAyoYhLmkijTGygjkc5a4G9eEpqSASXqAkCbKQnVHUMr2RtdrdxkNtTLJECQbAD2eCqxKygcXiOSIt7oCuEXqAo9DiJtdAYr/vy+JYLoTwyaR55l+TQToYj'
        b'B7r4KJGdhVBNAdzU4G1wCG/g+RTYoQ6DKVivDQSZBR2zjfEKrzjeGDqzV1wJ7B4xbpotezY8Brt6RqTgFmjxVtqwBs/gMqWMxZCWtmu1vRd2sDEbAZtn9ogrwZMZs30X'
        b'sytOOIqnpkZCFVa746VorMIaCgpnEC7ANhe8zvp9lMkObrTgU6XENS7TMDKU11w7XMZzc7lnHaRcnO8b6Yv4PyYsD+J2cZ/aG8TFBXv7zON60QxrFxwVFBnNsDVZYtwx'
        b'boMgkUsUlAhHcMc1hMPFRFD8jAIK0iBVn8Tc0LTMJA3lsDiD/tIfBpd8Wy7R8g4zFQKvQksGwyrn7yIN1XItUaTanXAPi44QREzzJDOyHMo9sSR/TkByTlDuxkwoGsNt'
        b'cDeHlsxY1rICuQk3nDMPlsyPM/aX6vPNDR5pzTly7+eayOJG31kj5tTAjVDlrsX1Y5h+PrhPDetHRPMrbDYlQes0qhWqVUKsgXoXcr5v5/kli4e5koc5JkTssSSDhedm'
        b'LvRlJTrm0MvXGSMEsjhH8+lPcHIhG3YTw4naaYQN02aPgRP8ZD4L9ZHaEKRpi1ywfQI/v7qgcw62kkT6nGiSAHfjGW+scpcLeCH/yBhsViqolAedYqFUIPPAc396LFPI'
        b'WOYe4p1PDwu01NG5tQKdaMbkW1OPYWS1bcTSVdJ87DAT0nbASaiekQRV/BLaI1guHQHtVAeh6+sgdq7iE21NnIytxtihzy2DOgHuJY+x3oghutri4SWkDlkO3AJuwVo8'
        b'xRLo46ksqZ29A7YU4OZQsgaChTGBeJEt4/FivGA7EltdgrGTPNKDrQLch5ehLO3VthMi5QLSiLfFXyVFhygtoy27Oo8+uP3CHF+ZuYWNW3GZWWXZlhMr5/5lkeWUJ/aU'
        b'rRN/GdVQamNdrTp8wv2JkSHn1t26feJ85qbNNSXSt847DnP+xeSC0/Mnll3+dubp9b7CipmFL/1QWPj1Vw8u751R/tZr97638r96epHqAz2v1mdvq84H/23bvWfG3Nn3'
        b'6v20f67OVd55Ov3MnUk7W5JcAv7ypOFzM+4/07ws2/mnlv2pZ7/L+3Ky9fwvC/xGjCk8anntx6gXp/40wWj79sa/vFFzf26S1fn0C7m3DlSda1xjlfXC2deX/zL9wsGY'
        b'hc9HL5te1zg2umVNg+nJ3crqbf8MEx3IOvs298GUlphT1m1Kk1XSNz66YnXN7JRXeoT3G0emTc1dnefX4FUrnjlXdOqJ82+2JDzZseC1KWJl5L0jHtsPfj16k9xyk5/b'
        b'srOLilaffvOSU8ft/LL3VnQ0vzc1PeHmF20NlcrW17dIN23LF6/6+3LHh+Uxr1x89c1lf4/5xufV30zvOb/5V5nHxy9t8nGzD6/5ynlClfvRmd88XRncdME9P93f75tn'
        b'dtd4v71i5Er/dNXT0x6+/0P8V/OKy98XvL1+/IHQpm+mH9OfsSeqYPwBi5AkfelOy9U//3Xk/Vktnzj4nH4q4u2tJfovfiMJk3yyy9Ws6O0Vrk/aOH+fGL1VdXNjk3Pq'
        b'XZ8JsVHFBYnW/3rp3jtbvl9wHhfvNPRorRvqcF30Xc6xeZtbvjU8Xx9wOv8v7/0w8c3Ip2a27c23Wj9hVH5K0CsJrxx/80dvw4//KXQoqPG+98Oiy8/X3feYvzvL6V/t'
        b'1xyuR/444cDQL6Lb66sn5N90W/la5tznF4+5d8KtZdWt1rL58343O/l99DOvv/LDmx9syvHICfVYe+F02rIPfrn17harzg++D94b9c7K2E8aVktO/nz0mQ/23uSSF156'
        b'OP58ZONrOT+enFE6dIegoPxoXHhr1Y3V8RtdD6zcaP3A0frhhhs3xzT+cu+3/BO233W+5vnyrzcaD//guD7uYovJb15fOf1cYOmWee+tpmmXPinuDPmt48uCi9s+vFl7'
        b'5n1jxS/B35z9xeZ44XtL9hScfnD69fd2PzzK/Tzym+Rv1n2+zUSWlZ3V6lKTLlGeaRtVJ3h46jv9rw9+PWXSU1Vrv985zOj1e1/VfnD1h1+/HZ1V8+onayM+8ixPXXM7'
        b'KAez9A6vrJjc8M20sO2jLhh6vWgdHnx/9SHLRcn/2OX6Q2hwS4qnPPPHnaG3N3Ydq7OMn6a4/fZvJw08Ir+3/9vfI1xqJQ++f/hWrcOVNU9mD3tRqXfH5ebPy18L9u56'
        b'vvWH5nefecit8vm6wbCgs+R304/E/9hkmrd70vPyZe5OHaGjXgj7ceyhaT83vnV/iadL3Us5DqtCb3/cXqD6aX9ByahfJ3x7S/lW4RaFzPOp0+X3HL598oeO6cvubIj9'
        b'uaHwftfhDMlPo/7+y61rZe9+h9EfytZ0vXOn9OP3Pvsg+eOyE6JPc2Z7BUU2vnewYeuvB+d1Pnx1yxmXIvnXT738o8R31mvPxOdIMn57qe6pm8uGNFm89f7vCxwin9uy'
        b'7Ej0GyG/i+Zfm7f9bLJ8FXO5cF4aylOSlM/Hmn6UJHKsZmpZ4GQsUyus0DFS41dibsHU8+VWUxxgt2U/b4xp6bw2fAU7lodQtf7wRu1zM1dRihIO8y8UDfFkquckIrj1'
        b'1E6z8ByD/dsAp+ZodNMAZV/PEHIYHhjOMppmjnVQARds+vJHmkyJYVqhEvaNp5GNFH+wG3swltSDySo3sNKPZB+eBVe1gUomeFM0B7fhTqaBLseiXKUzKdspVyEnx70b'
        b'EeBamTsOlou4KXhOEgk1IUyRtMRGuBkGh0I09gdJrNB+5hBmsYBteAIuhYTaS7gpxsLlgulwiTeDrFTMwnaiImO5CxGuaf12Cm1ToJZprVZD9Hiwtnw4oQFrG5PJhiCS'
        b'SOg3pVjmhC1YCadjQkTkvGkThs+Zx1pGBJB9WfRx/Ej6Qgi2klPGBMqIbACXRMx6YDLWh0HdMERYLINKaBw9knVaVgRu4bN2SoP2IFKwkXAR7scbzCkJW6EhV2kfhDuy'
        b'WSzpToU+Zw7NIitlHpzHU6wrEtZjNRTDvhA1b6Ue3hCK4sbxtokdUEma3BqCl8LXjpBCo52EKO+dQqKHV43iPXa6oC1LSeEkobLQkAyMHmeEO4RYIdzEx8e2yGbQ+hHZ'
        b'94ihHJtJ+0SkcddFQ30NeJX+EFYu7REECx2WuHXIUpb5Mi6cDqCDs9zIzp4aLCyGi3zxCG72HMXSmo/G/VLnEOyQSyywgrTdVLgUj9szYE8Topkove0UAl40ODNnDltR'
        b'E1PIhGglDaVd7UDrrccNsaZk0M1wkIhMHazfIpLhekgPBk44mU3m6ijYIoZT7uQdRtWArauVzkHYNBEuGpPXOM5UIpoNZ+J4dzDYmyUNdgrNgaZAMiOV0AqX5QJuRJR4'
        b'HtZrQEbPJcxX4i7YLqeV7KJrsQgPalhst2NXiDwMN6/mcaf1yKqrFs3aANdY1yiIvkWq72rfG1MR2rGSz7sMrmUrg+zlRGqCaoE9NkOVo5hNJldsXkmGdANW6HECKQfX'
        b'ycRoZk2SSJYyk5w1lvdEa663ZdN/ZJaaCZpBLdIFBCfwCFxhSfWhcSm/mMat6oZbdIAK3kaIWwKkdqQfRuDenFBSJyM8JIRr0BHLch5C4dZJa4icvq3AScAZugnhgD9s'
        b'4UOPz+GlTVJnuT22jIVaWmmDNGGaP15mHRWOB8IcyAiJoIKMBUM3NoMq0UrcCpWstXFwVrDpCVJ4joLKbqcFeNS2kJW6BE7biN2lctL8VpqtHh4QYLuC3yAKCvEwtZRp'
        b'zGQ1uBOuTuVpbrF+JrSQOU9bKcJyARz1g3q4Chd4VMpKq7EhoUFyKywPdnKWcNJgIZ7GkoQ8NYXD9bVkWELhqjw3lGI3mLiIDPKgiU/aBNvIJGjFUigJpXPiMgcX4LSC'
        b'N75tXreGKBS51C9OCF2CADgxigjHTayD1xOdtr5nhPpw3AeHoYpsnnQ2LMTdWbxMjyehiwr1cJgcHnQircBa2EORSU/gnl723dT1rCNsIwvpNCLaVEduqIuAM5ojhMZ5'
        b'fjxp1tYQvKx0xjaKecqvVDIZ6fZlSXZc3A+H1vPv7Sb9d0OJO+RGcMERO+j2fQlqZOTFEeZie9iBW1grMhfOgf3kCGhlL1BZe6GAbCzb4CIbSiVZs1U8KK9rASNSvgn7'
        b'eWuxDx7xx830RiYfW8mIDRGsgJ0FfL91wuExSh4N/hg0CKCOw52+6sh1GziykUj2WG5H1gnWCWCLPtRJ8ljCKGO8SupsF7xmrre9kMzwvUKiJeIRftPeEpNMnV7Dh0AL'
        b'tbSUs5liJhQlUkZ5vuAzY6GZYm9LsakbITxdwoNwHcXtVkp2TJFtle6LZMaeIXvjcDgndjMjewztkHQBdiyAK/wGz3SPw2T+AtFg2dgtwqOp6m4/mi5nPWaE7WRyyJby'
        b'tveK5Dh6NJO/B+A24UKB06rh/LlwwAYuKS1nk+40xPI1tFdp9kNxrwiORumzOWNKDusDlF6AoY3jVROo98STbCD8Qu1NiDSgscN6C2XYkM5cVMcYJktVJoakM8cJgpb7'
        b'EC2pjocWuGkD55VYSVnAmtYKLQUTcC/WsEZMwItYx1qRGO5MhEH6jgk2imzT3fkT5pphgRaJ/cgCLRA77hCxU3/MKmRusxSeN8xRHhQG5bPxrAvzdNXjZsySwAnYH8DL'
        b'MnvwFFaw24pYrOlhep4ER/NoFHq6D25mEMb9gNAZPiwUkz2ZbYDReMHABW7idn4ydMSGStmrTjlsyx1CFimZd1VQL1LfWZBi2xIpr7Q11GgvPSixdDyc1tB3HxtGJoRc'
        b'PoZfZ/5Cchy1iFn36ZFjuIs+pLv5PnJGFsAOqRnbURyjYD95QnbQK5odZarIEPYn8FcHNXh1yqQCHTi3GpDbVtzGT4k9E0Zo2sAKGoIdIrIaG4nGfQEuMUfiXAMi/bAT'
        b'kZwEffDkDfG4F6vr+OFzpOw4FGEnkVXImjsDVw1ZGyeluUtxOxOD0o0pCDInXMBwrelkjc5wJrt8MPV/bxMop0IdHEtlQogjtFkqAxaTShmRA6KVSRCWUCyiUuJSHvOB'
        b'7L3zpVF4Ts5xgpEcWaQH8Sjr9ifw4mKlAltciADB9mvzdBGlNoHtkimstsNCR2Gro7MzXf4HBSRlFZyQTOJXzx7Y7iKl8x/apwrlAhtoWsKYq+GcEk8pyRaP5Ybq5pAF'
        b'vJMuXtwl9loH/N4CR6bjNtgF9VIn1i6JjXDoYjUe9Co86ccIahRORMbab08nNVm4+4YE85ImltsrXcihHbgUm+V077kuDITKiSxfObRirX8utjopeINEoQBrphnwM7GS'
        b'rKbrWGEWzijOe2EVW/HbGlxKW6d0DlaFrJeTtU/ENaEQquGsK0vvCkXOvMwMZ5Y4BpnZ0V3NBK+IPGnObD3CWdKq0z18tMMEQHogALbMYYJXIVxRhTiHkd12Z4ywQDDL'
        b'1YbvjRLoglLed5scJjeFKwVu9lDMsjROxHYerQQPwgUtYgk5V1rkQ/47yLWSRzzncSr4mFpJLjPrs/sdA2oJ032/s4mzN2CAwTz8sJHAgqFxUEwOSx4cUEhxPfh3DBie'
        b'hwF5z1JgKRwpGC6wFloLRuuPFIwXmqt5xo0FpoKJwomCkeSTTI9CC5sKLYX050ThHLG5wEYwXGzKYItZ3vQWSWAuGCkaTb5bk7/ZCEcKLVgtrI2HkxIopoijSFe+5iTN'
        b'cJaehzA2EloLjcguPVKswRvh+c5l5PskksNowSSJgWDdCB3XLnxfDUSK+uhu774GOkK6ejS1BtJdfoBroM3cJ9Y9L4IGrhEpmkXC7xLQ0GGFQi4m35h/t9y4DwxJ7nKO'
        b'RVJH+gX6h/lHMuARFunM45DM14KH0BrmUiYrvrWW/zfgQUgXTdN2USadjfSmLJn8NBCLxWrEadG/89NAZG5OpygnsJzFw4cMZ8T1nMBmE2eoYujpjXDRRYdt3Uk4H29w'
        b's2IkVNtc0SsC3kj9U2k0OH6IKNFA/dmwx2cj8lmaaMw+m5DPpuq/m/X4rMYSqTXU4oRYJlr1wAkR9cAJsa7ST5ykxQkZlThaixNCsUW4xLGJsj+AEzKuSpI4WYsSYpKs'
        b'lzg+cYJOfBCKSNITHyRVbnfXjKHkMDLouUkr0/IeuvQDB+nx9N9ABpnBR5O7y4V3xX7hEf53Rb7uvmQ+5fHGeIpXoUYDyc2nM3sN/bZW8Pi4HTP4GEn3PwT2oU40448D'
        b'emiKYyGZbmpAj24QDxFrUe5GBhIU4R8WHuXP8Dwm9sHSiJw7NyIpp3c8uKsaxuOxXnbTQl1oavRw+ED5atEueldebtgrDzpK/TM169tjuvMapPCBnrjl7mBb2X8UBOMx'
        b'6KL1FOxKdt4cqFBix8qh3fh8x/Cqihd2zsIRaX4OXMR6AY87Vgs7Rqd53bkqVFJF6pBbISUGD4x/Idn+g5B4o+RvfT/lvt0yYoYH57la3Hbjolygdh0ZOd0BGi2ItKf1'
        b'24FiiwF4NXdq/DlYnNRA5z39ktEzc93wPqv0T0JpWOhTgKXBjjv69U0vSI0Bi348PI0TFE+DOlr8V/E0xkkeF08jkbWEAgZQ1/z/JJiGZmE9AkxDs5ge+caMxwbT6L0+'
        b'BwLTGGjVDoJuoXMt637/D4BZ9A3C4uMF4jOpqz+NpRogMkibTBc4aj8AjF7jrAa9oIcSD2RBDib7gYN4HoU2oanJH8GbSEv+H9TE/z9QE5oVpwNpgf73OIAPvRftYwI+'
        b'6FzA/4N7+INwD/S//nE1eooolTdH7+5ORfbAG+iBNYB7sCpUzZDb7VoMN6HNE0ul2DATdqdlfdUiVvqRbEY1ZVGm70/fT02OefLOrddvvX3rzVvvzIu79ddb7966uuvI'
        b'7nElLVsn1DVulVdcuXOs2Lak8WBLuVvJuANFHiKu6JrJ1DMZcj1mflqd7Ep9Ymdgu5MaE2AuNjCD2QjcYsyjAkDXcDUwgAYUADrgGG+zKfLBDnaDOhxO9HYArkU+8t89'
        b'f6Mm6h3azAVu0DaTmcbGpk6S9gvphy1QabAMWzSenf+OX6s2HH7So+SgAD4sXqJLIPl/I+59+GMJV5/bDC5cPW7weyoLfs/dI+gW83SEvvuSOvGh7/1K0sa9jx/guNQR'
        b'6y4Z3IM3Qb/H4pJqFtgcKuDp9xHxpFTIS5aqRTx9JuIZEBFPn4l4BkzE099o0O0Ne79Ql4g3eAR7T7X2/4vw9d4wYGq5SR3TvZqcNDS49n8R7f+LaJf9L6L9fxHtj45o'
        b'dxxQusoge39PerM/FOA+yJbxfzPA/b8Wli3SKT5aKHj/5gro8mFh2WNieIoz04SZPB4YJfIcbyXk3SgiA7EcD4jDNZBegcFYxQjGFlFELQPmaA97oMIQrkITHGcRkFiK'
        b'Z1SakOsUPNsbNGzybFaBAKhMV5qY2MFmoTrG2x+aVPSOITVhjOaiuyeeF56FE70wvYQc7MWjhngdK6NVlKgJTmJLbHcsKZYFOvJRH1gWpiFVjZ1sQKqz1wfO4k6VC03U'
        b'RIMCQvoIzzQ81hF3hOHpUN4dLEKqTxq+N52Fmoim4RXK1cryjJ6/yGnhokDKMrxXHhwWCo1RgdAUGObsFBRG8nERwiWpO1RERHI2UGuaQfpkH3NYj1oOxUr3XKyfribd'
        b'UExS0WsXIiZfx44+2dNo1Wz33AgsU2ERHzcu5uKgQh9qpsN51pAUPA8nIzUvq0crKgXr+HTaHliarA8NTv58EMhmPLRcCgfxaq4p6U/REIH3HLzILI6GUCslPXM1FDvX'
        b'KGkYyk2BgwvuYi74L5jqxT0tZFRyoTbijVxa5N0wESMpLfP+Onpniwm4mvu/nP/lX4rmzHvO8oXd2/Q+WGd3IXeipaf8yLb5y2ImBX7/7MTGIbYe2da7zV+898ON328m'
        b'3rYb9yk5euJqZr7p987Karv5ikuiiPpDxzzbDc+ueEc8SWD/YUjw6GMXql0OHggM9LxXLjskjf3rWkMYMfaDj156fUR+6TT88vmA52+YbVya/5H+4qGjim8/tLWfrcys'
        b'8Px78verN3Z94fZt8pIr30kffBUbfv/o4tdd3lHtyfv16V+P/W2M4e31nl8H/XOT04jgIH3PhpTmH8y2vBRc9b2X3JxdFqeH49WQ3oGf8gkZpvG8y0Ap3ODUsZ94FUt6'
        b'cNhhE+7QhH+eguMh4U7Lh/D8FzOgib9G3o2XhvFRmnlDe7BY4+VkPvMLsAerqXYDZ+b2xSyrnct8HzZZbOCni0i/mziYLPATTC0LUOINqjXhUbjM8MLc4Jw7u31fCmfT'
        b'2XKJwa6ejm4nVDyRdUsKbKV+t9i1hPeu6+13iy2OTPsyKXThG0BXbTnRzkzxmohM84ZQ2OrIU07cNCokquo1d96NhpEXb4HtzPOgACsyQtyDrbCR7gMXOeyEaihjnWY9'
        b'QuKwLqYnMQg5Ypmq2IxtcNghmKwxe2yTB7O6D50sIq0+iCd55zRKvdFB9dFheF2jj+JWvMYHaTZ7w9kQPkLTFBp1BWnCAb/+6pb0PxgiGfwoVTKbBUqKDBjrroFEwtDV'
        b'LNWsvUaM7ZcGUZoK6fN1Y/sqTrojHA0fJ8KxW+HUG/gCVn9g0lsdgYz+j6V13pD11Dof1aT/Qizj8kfGMupS1v5wICMF7u4fyDhBwVAVVgbigYHiGMm+bpgySBzj8AUq'
        b'unSX4a7hDtoQxng9aOZW+nmLpNx4PC/CYqiBLp5N6vp0AyUUwTYt0CXbwg6xsKKJAg73QnM6jVFkAYp4qoBt/13TRYzc6xuvrIxz0kA+QMlyGO5IxdYeYYhw04fkRJuI'
        b'N6biCZJXjY+a6ap8CPt7SIAdHslTUocEcsZCOTS688Ff2+ZB27xV2hhELHKDTlaKDe5xCiEH+LkeAYiwJ4Q/zNqxDrZKlkR2hyBil5glM8fTcbAzvkcQIjksS9czwBSo'
        b'M1ptNFwbMmg/3JQnBTkNW+EaiwpUhwTidit1VGAM7mcdscOdRgVyw18J2OT8g00SHxGXlUOjAknvTMvydUz15v94Rk6jAjnXOGmK/Zrxy/58VOAfjyS7qt8dSUbR+uAM'
        b'nlgu5blOHIOxMSHMOScojAKi7lZTJeEeaKXYJtT5Tw4dIncivoSQY6hVKSU954dlZlHe0MXaZRtvzJGJZOdqm2bckerGN3Z82DDOkXR69rC00cqlhRwfZNk2ZSgfEuiI'
        b'ZZqoQHVIYMEqfgBr0qGczM7G7sC/mWunsizvzeERV7Pd12e0pa8jTeWD+3YpxythLzQyp17q0Ovo9Ke7NvUPd63IoLtr6bwVkTVyGLc5dsfpzcgQs4qmrcNGrBFJu0P0'
        b'9oTyba4oiMbWVSNZkB4foWcLW1U00hlLTPGydBhNvoBb4IHHWIJk4ToaoQfXieDaog7Ry05R0fMcymAHXsLWuLm9YvSGYXXamcNfi5VHSOFdpz9TRT2XaznPvOnsiuSA'
        b'1yxW7n6lLOzLw6uLjcue2rxavOJJ4VafuAmHG8xPlbzh97z+mLMTDJ4WmwzJ/26Y+b0n/mkrnlcabqqo9fzxy/rY5DfMLcSlX97e79J6zv6L6I832uR/tOH3i77P79gg'
        b'e+C6r+GvZ/cczO7Sjx15cHTcl2ljF38me5DbuODwT1eEH675KCE+cd30TlXRhegIfaeiyifFS2ZMP1DhXvyG/YKcyjuOjltK7Mwmzx0Seu58cnrSDYsl99aeesLZ3eyy'
        b'4B3XrjTu50mO67/ZOcnRvf1y555vHuYdeSbpwJXZv86bftdFFV4ydd74n4b98+OraZ9vhQCjg3Z/Wfjps1PsJJtsM6wy5ny4afTxdtP3s86NsYFlTdP/tTduW4HlxyP3'
        b'e4YerDFrs77yxe1/XX35jczNVbKEhOuNe2ZlOkf5Xruz8tOsTbkZDutPvJO823rd235vnJga+ZJyR2ZKePVMR1/F7ydqF8Xlu7dKX8h9Xtbxt5eCliy+Efz5zr9Uvu7w'
        b'3e33Pn9hg2uRx9kt269+O+7LCXdskgPS9K+n1Hzpl+dyIqFswSfPNBcGWNvfEGTN/nJz06vnvtt85Jrwbxtvv5rzkdXihuCxsgfHqjxXVJdeXXvB7FPXJh+z3Nmr9Xd+'
        b'+sasjR8sXNN2+CnVMwdmmv78el1sw7LV4iP/sky/f7DRJzb9YdqbLxS+Vjn7i0DvKeeMXKoMlkcvqf7XS/9K260wdEte/v0hm4V3/948tNnQdXLBqchvuuyuf++2ot7X'
        b'7HriNiuf+ujXIqKP2f9mER37VOyDNaGdG0/b1G07UlS49dPEDdOeeOb33988/qBiSl7Rd8vuT9rys+mD63O+HP/ZdtejFm9UDnv3l5AnXGa/Lfje4ujupF/yzH/94ZPf'
        b'PYw2HlHccp+hd/NGieJ4xXtKo8jMrqC/uu087Pbye4pnNlooMxwKTiZU7Pv0Tvhv73+a/23gM9ZOr7YcnTVhjMeDfTu+qiXvfDvsi7UH8v4Pb98B11Sy/X/vTUILTUBE'
        b'BMWCEgJYELFgQ1EgNKVYadLEpQgBG3YRpIqACCrSBKSICIgUwd0zbq9ufetWt/fe35b/lCQEdX27+97/Jx8Dkzt36pmZc+ac7zlPPbXFNvKLTyqr1gzq/nDJYrnn4B+/'
        b'P53SMf8L3VlTj0U0dk/97IfFyfVTvMe9/Zvev/V3GO2ofqvAbfOE2yc3FyzR0X86a8Ul5c73mvLWTx6KWhuV7F3Tqnfrx0Mp49tejre3f3H3l9+X9/0Y6/v20TM3+Z9e'
        b'66ypq1t0LX/+jwt7Tb47vfuL9+vXPbXz988WffmUwy/uK38TDSyaYBn9zi+euxJXKT76vm9M9MLz7hbRWeuPZ7hx+3I/tkr4Q/gg6sdn1ngseKsINVRn9VwvfmfRsbKS'
        b'KY8ueuuh3/2Cngl95/DW13+flNj/aXu8UpbKcAJdrnBFBXhTcd1telqMtz5mncl632UAByngDbqTtALgNaALlC+Hc6hvkVyNeEMHwzSgNxjIZIbgl+ahaoJ6U0HeUMMi'
        b'hnqbiough2BJIKoiOhkVVC0DHVGj1bC0P0Blo1XQZSiXzRmFVgPMiDO42jmUjc+NEW4G2sNUeDU5as0gcaTX6KKDKriazNcmBR9GjtSUmMHVFkG2Dj6NDkEeg4YcQ2eX'
        b'K2BATxuwNh4dYrYtpahEIR+3eBQwTc+UIU5qt8sIMA0G4RpBvDNkGqrbzJo5CP3oqAqb1oXLKVSD01AD6mJD0RaDWtXoNQJOM9ykhqdhOa+QxembgipswkcgatASokub'
        b'LYz1Ur16ROSsQqdBI9TQyl2hGM6NRqdJoZYC1DKMUmnrDeE44Eo70CFtdBoa3smaVoCaYIjB06TQAoehXANQg5pJbKrzUW8ABajpu2SZj+DTiHxJiQlKkkSkjSp0mr2/'
        b'Cp+2P4Q+Rq3Qjuooyswf1cnUMDNPOEt7buBM4DqmSg3OzBLPCelcws6td+DM0BFbCjWrmgeddHBmrcbN7E0ZFQESVQBzdYOGUC2cliYYBzgbyggCoIFHHToTKYHHoCEj'
        b'Cj5RI0+gQoeBT8zxCiEnfhi0TqYANqpRZCA2DYLNBouKlKZOjUOlShcfhl/zCGEINleeAlRScLcHKIKNivd5MpS3DFUpZTw3USyGy/xsNjpNNlCpkPkzjNos1KqCqUVM'
        b'po8XoAv7CK6LrWcTuKaCqSUtpxK63np01AblaAEbit1202HdtscDzsFlBsyiILWUSFW8TTm6rr7qMkblatkd9aJcSjFS4nwwAS+/EagaHoNKaKUNWjYFDWg8JB1GA2qg'
        b'2rjVjBayk4IpTi3Nz2T2CEytSeXqKhMz4L2kP6gTGv3VQDU0jIboeMag83EEqIYrz8HTrkKqZfoxGEtRsj4BqjGUGu7YSRVSbc88eh3gaqmUGqFybZwaXEtirzZZoIvS'
        b'7dB5B1TNTeVOCZ0lAW6hzVYbsDaA2naxpwXoAnSnZWgD1hqgHBjkD+U6ZyqoZzhUAJ1quBrkjmHjcdIVnSPTQ5AlcNaSgUtQA7BQomI4nTQDTlLElwqsVq7HSKtIGYEu'
        b'4P1BC7A2AS8jtl3lTEzbnDk6nqo1LpIFFLYPUsLZvRq+Fl1irq3icD9yR66iMFdZzHBq/lJGGLlwAXpYW+EUlGogNNlQRlEb6CSct1JqI9V2o34tsNpGb0r3uPN5SRSq'
        b'hnLRqRG4mgqrtsWBdiEjSo66J+4YhVPTh6MUAAFd/lEKp+0Up0ZQakut2YJumyZWyjGjrIVR08OLnfTaKthcuWUHxagxfBo0bKUvJUSjQZvAUQi1c/PwUNECm6XTKT7N'
        b'F53fqQao2SSxXpzAwu1FMhpWAQZ4sZBr0Cu4oVaoUyzH7PJBWkLQAxOp04tcKNOw1HAiks4tHqgWGFIshma1u/3Zq5PYjlo7UyJVlwnD5oQgDaBUgHbzLErKiah8DF6G'
        b'UhXkBouqU+D6NAY+qdkKFxmEaKbcWwWJC4Z6duXXsMZGKfMlB6E+wcRt2kGPI9tFYjgBuQ6UXiNQeZoUNfKjEXFhWJomTQtDeUkqxDDq8oZDGkAcHNzDkEJlm/FuUGBl'
        b'TWExBBHnDuV0xHYthEqlFh7uLD4MRzBxK+AyI90mcg2dDXkaYBw0bIBT7HLuICpBZax6imOD83YqKBuc1KPtm4tKxrMr/klQTY9xFZbtChzOmEbXzZZFd4DZZo511cay'
        b'7fZiPM5R1Ok4MljknrUGS/uHRRn2cJrR+0HUiiepm3A5Xun6KF/mQ09wETceDolXQ58D28HLoDKL5QqbRnusi84Ky9HZiXTZrZ9AvPupVQuonFylEtga9Liz/aN/OhxU'
        b'39m7mKsvYeNX0OE+AOfjw/RRwcj1JxzlGRFdh+J1Shm6HIhJ6bhcRvbRi5zpbtHe6RG04BnrY+Xk8vY4nOQUxCsRqhKycAfyaPenQdkYJXEemkdaRbrFh67kxowV7TOC'
        b'KxkEzgGFMDhjBMuXDJ13wfm0oHyuqJ4Na/1yZ20UHBxKZ0C48/OBnS+hcBblE0Qs3maOz1ADYtNRHaVvC7iKBdQT6NII9BqK4LqUEX+zewJ7E2+mFSKG/Z2Nstmlc50u'
        b'OjGC07N1uxOp57OdDdzhQHdtrOEcL4Y2bEDNmfToT1mNhlUrjCH0lkCdBqS3HOWzppyGHBcrqBtB6sEF1AfnKZFvg2ZnhtMzXUAJhuD0Jpuxjb0Tb85oCE6MYPXwcVdi'
        b'wvixc07Qp9QA9XJwmSNgPZdQutWZwRD0oJOGUjVWbxeqpZQmVkZpI/VmoEMErIfZt8YH6K4y2wHzmMFaYD28kIf3UfMo1MmLpFZQSaiMAvXKk1XmV0chlwD1potHoHpq'
        b'mN4GXC9p0FIHR6nUdgSih1fSIboyYidBF8PoWcMRZw1Ezxcvd0IIu5Khl2L00HlvbzVGD/XCBbashqByOeqGepk2Sg9qMZ2RvSJuMd42NRC9K3BxBKaHTotZCVeh14gA'
        b'9WT6kzBfqEbqoeL1tAQT7/Eq5xYUpQedqF6N1GtGp9jp3e4PR3CVraPAequ80UW2w1dD7UbFdkwI/vig2s17EO9V7MUu3NR6eimGhm1GQohvlcmM/+/xdxRmRTUHwv3A'
        b'd+xnvBqCZyr6M/CdngZ8Z4Z/LGgEF1OcJsC7/wC6E+mpAHJiCoiz0rsTfmdGAXcWNIcxgfGJrXhLXiys+q9gd1ajYXeWd6oH/reYu2O6KqzHfTUWB7lfRiHv/qRRuHaC'
        b'MEjvVsPuROTjnoi79HMk418F25n/X+LsanDdtwkUcS33z3F2eiJTHRWubroaV2eGU1bLqOoiCF3ZqrmdVl9N85wDXMf8/WFJciS0jDKQNVb9Vh6+C1C3UVyuW65fbh4v'
        b'kM9yY9XfFqrfBux3oiheFCsqEmIdNVojEs3GMNco1zjXlAa6NiTAPApkk8TpxOrE6mZzJMB3kbBRF6cNaFpK03o4bUjTRjStj9PGNG1C0wY4bUrTY2haitNmNG1O04Y4'
        b'bUHTY2naCKctaXocTRvjtBVNj6dpE5y2pukJNG2K0zY0bUvTY3B6Ik1PomkznLaj6ck0bY7TU2h6Kk1b5ErieRU8byz9mwQM19toSW0iRVSjppcrxWNjgsdmDB0bh1gZ'
        b'zjEuVqBOC+W3DFcs9w9Rh7u/3SvcYQ9JDJK0czAkn8acJiOVhHRQsjxuc5zYb1caAIH8NXdUYWoNnNLFbrmWpZ/KcI0CBlTmcfhpRlw6jc+QuoMEqM0YbamnHavByS4u'
        b'OmarXXrc9vQ4ZVyKVhFapoTE+nRUCX9mqzNaDzgqEZBKTLR84u1oZFal3c649Dg7ZeaW5ERqdJSYooXDoFZQ+HE0/p+xNT1udOXJcRlbU2OpaTpuc2rSjjiqscwkm0/S'
        b'bmJNNSoYhZ1XIjVMclguU9nUJo021yJWTSqDPzYRM1XzoB5xJzsHT5k6W7SdMo4YnmXE3W+SyBw6rJAR8Ea0lnGfyqwuNT0xITElOomgCFSYZTwEBCFxR0eVyugEih+J'
        b'Y0E3cC7We7vYuO14t1XapbKGUws9B9UzT0JhyanK0YZaManJycR2mNLeHdaAATLhlmhXctItnZjo5Ay3uTEi1VYjUW07VLFEPHSq0GC6uepQWFK6ffB4AxHijVXqZ9Ex'
        b'nSPcPvEenb0iqn4WU/WzaL9YCx/2C/8X8GGjFs+f24H9mWkg7hGzClzv76cya6NRT2i5I3OFZ4WafuKleG97UYc4RkJ/tk7vg1uiw7mQwE9iovFKj8JNimLmeawwTSHa'
        b'5PYnsWiiY2MTmTGnqt5R5EYIMy0zTrVklZl4LWm2jHvjNUaZvLIQM2TFRWdmpCZHZyTGUAJNjktP0Aog8yfIj3S8ErenpsSSEWbr+P4BYTTnmpGKyEabB9gGKIls1vP5'
        b'8u6bP8plrRmyx2W9BbKXu0IrDym5xH16jeNepkb0mcSkHpq84AR0oxPoKnFElYElJRn0QoGMXK3uDgH2CjRGQBHlMUOoRt53KuZ+2yTEzVw+t5/bvwD6qf41P5T4HfZe'
        b'K3BRTmNN9nBM+5obDeXQLXDoDKrgFnGLvOFE0k9//PFHzToxFpaWTdBfFuWUFG3NZVJLp8swiOrRNTRE3SqjctdZAidZwAfpJ8oECqdHjVCDLitRvjHK28k0AlhE1Hd0'
        b'hn4HnpuDynXkUBbOXJ7WmM2UQjZqdMRPBH/eXcA9E6gH5sWoB7XDYejSLsiAfPDclIWSKYbTqK42y3GjdJov+1qEBnhoQdnOuAg6dlW2MDCqHT6OWA5Gl+U+igRU70IU'
        b'E2GoUs8mfTpVvPrDFeLwCeWjKpyDPtZzE1JQ8w6ZKJM6kOs3Q+00+MZlcmNzwnWWm8AZ7hMeQGVwnY4OGpisTzIIWMaiz3U4w/1CEpahL7LRG8aC0ADJkaTDMvCc4QEh'
        b'ORNdyyRaFFTOj2WRPbxDLCHfG2d0XuM9onfhuZUmuuN2B1BdfDK0bVe6BlPXLWucUS+VBs2hWAQ1fnA2czXOstGceLUaMUJRB0RBeX7oILqgUDgLaYuh2gYLePljURfq'
        b'UlhAvkJqgLqgwHdtMBcXb+oO3atYuFQ/CSaHXRHCsii/855ZHI3RAcdQxaI7a1gqZmFuimb6hjqgPG9UGIxTxxWhqFNDxNS0EUvyZvYGWK5tlEhQv5c9tMg4r50WqHrt'
        b'HjzkVELPhUYsAnYTz4sm29MxlaA+fvoD6czA5OAUdEK6M1KPIPyxROGIalE+86Wdja6FYYH1HKo3TKNvtfPTpkI1XR0ec0OVyz2200tZkSEfhbLH05dmwFF0SolHoTIN'
        b'dRmSlw7y01ajbExORES2xOSRo4Rq1IB6aZlwjbckJgBUoT9xPmZtu5fOHqkOqiA/k17mFkIuaqV0kztVe9bXoLZMd5xh7RK4xGK6iGezqC7+zr6BoXT2aXbVvMFB1I3X'
        b'TJIULmDRPDvTha62bahZOyAMfTXIOYy8YoLXaR6HSrlY1KfHbYK2xMs/ZPLKYszMXTe1TS57MuWFZRY5H1o+Wmz747l5jeWLnK8+n+6zyazWM/xya/bKebUpq/jpa0/O'
        b'37B+a/yRMadTHJdy0n/br7ez9ODkYe2mxx/sUjzj90aQy5mvF/zx87NnUx/p3ZER+kL2ym8HSicXL7j50tkv1v3oeSb4meJ0o4Uz7VdOzuu5XmBvNq3h9cdnz3xlzEqX'
        b'lRFvvFj5g+RJ35/TPtv+YmbDK2HO3/oWi4LT+p4VRbx/O6t1+68h7zz19M15e37/aPyalWt8bj8ekviRz7TxXzX2Xp/iU6xbM2121qRXLLpO1Cl3BC1Nbqh79lGzXx8J'
        b'0ml1erLe0fMjq7LiurHvzjvj0OUzpqnPPTw2uHfexcUfnR4TfXhy23KPB8I3rXZZ4qJwE6e8Wy1f+Gnnl9cyMwMcmvMTpVM/71lvkdD+5dsmn7d/Xz0h8cOHJW2bbWSn'
        b'kvZXnYoOz4/5+MF935fLw119dj8v/+BA7oVKueXA3IdvPnt7Ts0sd7OZR/5t8J1za77Lk/l9p6OWvBr39gLxs+Vvj/n6fN+Bf+XsvFGyXjD5yfxasd6t8MNPfDiv1Pip'
        b'6zruGTcyw183rft53jI8+AkvnZma6bZ/3a5XotLP7/24YNM7vX2i4o87ykodntfrGZwyV17TMvW1Vw4m2XpcceGfXa148e03m6ITH3w1bO2cn3jzfZcnz7v93vkfn35k'
        b'wvXdO4J8f1kzIe3bp93eOXJ78eeW2Q/oB3y11KP7wRVTv4k894H+ROvFvR5PH27W92iT2X4X8NVzbz55fVfYodwffB56YW/cyxXxsoLpdX/sD7utXJAz1H1bFOH+peei'
        b'04kfST4/Ev8qsvm8e+h0aLhtxrEWw+GtPwhfdu/a5Do/UCGxftLuIceSh7YGzlvW+eG1qi0vGrdM/neuuLZn2avbxnddyvlM/5s3fxdeEps12b8pW05vr1ZCZ4YcdcI1'
        b'F38Br68LvCJqMb2Lk8Quh2J8ShXAJbKv4P0G5QucFK7hlYZ3ePryWnc4IkeD6JyPny5++Ri/eJ8BvWtz3x7HvLDCUT+1attzLbs5vLYpEApmQosT3vV7vCWcTpQwZTo6'
        b'wbxOHlkLdST80MxAq0BifLpfcEy1znAmjwpC8P+ZRBPq5wJ5gVSfC8dmejs5omK8zxUqdLlIfC6TcE/M4ys6CSSsMVH3FKCzo5zTOgGrD+VEolJyBYaK9HhnHU4nQphq'
        b'vZLeYbmgZijTRfmKQGcfJ6JflEIP8ah6yZveNrruhDI5lKy4yy+uiR+tPJN46ZQmo9x7REyut6A1WJuhbiVUwiHqqEvjpasByph2Fx1FncxJ1zKqQqE3gOsWMB+zlZax'
        b'cj+xD1zEx7g4gUc5ewzotLlI48ml9SjvXdY2cAadFac5Qwe9uNs+bg3qNoVejdYNb/ktVH1gj04BnhV8NhXM9PVXOJMbvABVKdPQScmipZDP3A+emwOHlSZQi4p8yJQo'
        b'jAOcUY9C4CauEkOjGWpld83V4eZEiX0ctU/XV2Uw8hJQP66c1pcCNdCB21sPl2YGODv5a1VnN1uM2ZouKGRWCHmbt0+Ca+w6c+Qus8WATQbqD4cCfCAehCO+/k4+/jxn'
        b'vFU0H85BI32+D3UEK/18YAjayfU4u8Q1chPpei5TaaGhK5je9Rcq4KwlKtDldPQFQ+jcRa+HTXxClUmohjrHEz3A77WEAkbKl6Efn+ndKwO0lJTQlsHuQA+h88T1LVy0'
        b'1Fa+oWpzVZVRUupa0RcKlxM1pgSd5tEAOq9k/a3GbSqTYrbvkIuC3le38nisTi5kd/1HMG1cU87Y9Sd+M7erdA14XvPhiBIKccFausH+MNr8uVCvdnl51letUUTXPVU+'
        b'StGRNXjxD6UGUkWkCJ3hoTgDetgtfs1eW9QdjHJmouNy0rpuHpqhnGO0eW7BStQ932TEP+wAcyWdoYPKVTYxqA1d8yd66AGBh55UOsw620OV0LpQo7nVQ03MxqRfDEeg'
        b'YLdjoBaQwAw6RKggFPVTtYsVFAG5pb4ENYFqAxc9OC1AHqpYQofMDg99p9Qc873a1kEjpkGQP47qLryzqDPJhnVylbb7Cg8dS11U7jLzAlC3XLYoSMVR6XDGsSIvfOKX'
        b'ZhAgiSlUEETPzh2oxyhNy3InD47PRMXe/piBb3bGLwV76RlHopNsx7uSNVdpBJfkBphllvGc7j5hroeLWvHeAa3K+dPk6YzmdeOEOagG1VLdxORw1IN7nKdPDCegKJCG'
        b'4pNwY1GreAwe3xOMyhpRh70U1USRwlkZ0CosRnlRTOedb4368cLx2YkukEIwoepyxgGiZT5whakrz03cpMTsYKUvMQvi0VXeFErw3kkliWYZJ0UlcFTjNLHXnO27ZdCK'
        b'mpS20Xf4TcS0WAVnmer5vBgVKeEk6tHYvaAqOEPJAC+cs0uU81ypI0/i6dPPg5o7oUEsmxzHW9M13GLcHh+8WOlmMdMbFYm4qahJ4k4UD7TjE2AoQRmO6gNkKqsoBc+Z'
        b'2orWxGSytp8VT1Si9mSN42R9KGcdvop6Y5VOO9hgieAovwddhzrmNzF0ndzXeQlcUTg7BuAtxiRBFG2FzlNchCV0bIUCc3RSq2UE15JHrGZkERIafSw/g8pIx+C4DhQo'
        b'0Nl7EUrgPMypLoIOnQB0Jlqlclaslus7aBv5bN7IvGtXBMAZ6Swd8khNzWPQgAhLotVTKAmF7IJj8lSopYcQPt/00KAAJ2aiCjpRkTDgjgrmoP67fT2uRpdkRv/9Hfj/'
        b'SNtzL4cCPfjjP+hyDnBxBrypQDAfOrwNb0iwHwK9SSe4EKof0aF6Eh1Bj/5ljHMZ8xP56bwDbyaY0u/08Hfk1t0UP7HG31jylviJGf5tzBN90ERcmg69iR/1DU9+jOmb'
        b'BHHCSiIanT1jta+h7vRtIGG6lAGiqxgcjSgx/K9mQsSKGyldM5o+xBabyDX/QV1zkOufrq2wuXc//qNfg+y/5NfgIn6D+TUYXY3GqcFs9W04vU52sotLcLFzJPdjLrPc'
        b'XNXOW+7l4+CvNjD0/g3sVDfwlwmkJarLVbvE2FF1/sXKbulFxrAb9/vU2K2pcTKFJlM8brwdfZEA7P9JvUaRmtvkyMT7Vd6rqXz6crvMlMS0zLh7oPD/TguYf4tbhpHq'
        b'e8b7N6Bf0wBH0ntlBu4+vavUXFP+k0ao5vo2d9+5vqap2yU4lbgLSolPpX4M7KK3pGZmjPI+9I/qX3z/+q+PpjUtbzh/q7IEVtmy+1cGmsqsRyrz9FnxT2Y33fP+dT2s'
        b'qUtO6kqJHvHmpHaBwXwA/KOOxt2/8sc0lTuE3MPXkboB/6DmWwbUhUAkAfTfpwFPjp5W6geALet/UqceqzMj9T41PqOpcbzKY8Q/qC9evXVsiU4iCpTI1O1xKfep9Kam'
        b'0vmkUpKb3esnaSsE73Qw8o+2M2NNm2KSUpVx92nUi6MbRbL/40b9Nz4u4+/0cclzd2ovRAGJ1Z+8xikJL/jE528TZ5V60g/i3/YTcXrH+CuxVTJe5ed+F8KssZnLHRIQ'
        b'5Iz/EyeVJmq7GCKK/0de6gCXsMfijjM/KS4lMvKvu6gkFb5C2A3idOA/shsHubZRjirvWfn/H0+jd8+COCAkcXuqTKwkXx91qFJEG8YnJbydxHNiL37VgqwRIrt7nGu4'
        b'vzfO2+7irbakpib9nYEmNd76GwN9wfB+nB2rXTPSpDaixSVEx7S4I1491Y6gmCaXzzXSaHGFYxI8ByI8BwKdAxGdA2G/6F4rgZhBG+L/rqPmYBLz9goN4rlKjb4gGOXx'
        b'01D+Pqo/K7KS7HUTMf8K1pPiOZa/BNqnKI3T9Un+ejjmxLt4qvwxfOApsaph+ZOOBVhw1BuGg7kDvVOhqHxoRuXUq0WhAuX5BRBHF2uD1jqHCVzEMl2oQ2WonVrfoPNQ'
        b'Nk/hSz3fF4/cnUk4xxgDVCeBNtv1VIESj8XXY0q1JmS7go+CLm+q6trjD/Ua9x2oiAjcKuPeUlyHKjKMHrnxUZALKrEzlGzh4eIYaKKKPQm6YKHG/S6dxKNDG1ED1bEZ'
        b'okJowoIrllqVqCCAlIsl1zh9dC6ElhppgjpIX2XOPnFQLeb0dQUongCXaKkzoMeXeb8Qiz1W8FCzDXJZrNUy6LUkGCmZ81gvHU5/gQCN+1AbfbYXytEFDZgHTjjy0JKJ'
        b'KulkhLll4S50ozbnACpt6oQLY/enM6fg1V5hClTsQ/zy+aECOtjMr4B8sRxdl+AxKUBDo8hQqibDlSNkOJoIeY0PMjUBGjACXIdp6v5ESJqrfxcRugRQSjP1IZpazq5z'
        b'y36nM/GrGZQ7DWqhXRkg84IaDSAF9ThRFZjNgRCljyOfprHq3TCRDr/H8t1yOJ9I50czOahxKYNYZy+KU/oFrDJV3TzabWHY1z6Ui4aUJMyHoIdqknlbcoPK3NOUoyZU'
        b'p1CBB+Yl8jOh2Y/FtGx29yKYifmoYQQ2YR9JG7EN5aDzFPGC8mPUoJckdJUSkNuGuaOCgpuK4FjEWFQLtVT/TXu3TAGHgqEZTuC/J3OT4RQ6JJPQt9f4LLrjbXQScsb6'
        b'QQVTG+ZAD3Wz4WQ5QwM9gU4FXRJQKqAKeSJumhr3osK8wAnIZiNxKShAPhO1kNhPajzNvnlUV+uzHTrwOpK74EXhjq64yJx9/XluChyVLIDODBZg96QxHGPoFYZcWQe9'
        b'qBmybdjTHhvIU5lKY0LVmwgNwjgYhn5KrfvRBbys7h0XpRidIxbX0LeAqZgLoAWdoDb5fvSOmewikE/pfzq6gobWSR6AQ9CdSewZcTkHUTPRgWhCyKASi7trCYBDuqgE'
        b'zsMAnXe/YGjC20oEOqPWscLQBKYAP+S1TRG0SL2zqHcVaISqTHIgwbB33F0bFx7yWrp54Z1rPSqj40F0vzV0/0mCerYF4f1nL3TSnSIaWlPxuwdQvRrXsGqtKuRz7Qpi'
        b'wa+ESrURv4+MUuRq6Efl+JF6J0CtC4WxyVlqLfRhKdlD4CzkqUGBqGAvnXU56oYruL2HoAe/yM/nUDHKN2EK6lY4kyT3d4YjRKMijsYb4cQJtERPuO6mQNcxGXk7O1HM'
        b'Z4Ww1xau0+17KipB19RW76gUiu+ITXMUalmzskWoRK7BwxkmiOwyTezREB1JxzmQf/cGFpfGtjC8f8ElO5nAyL4AtZKPrh1ijseU1EPuU3WgnQ3lMrighLJkdFmHaLHw'
        b'AabwpsD2ZahGicq2wQn8vRPnlGRLD7FxZlIOv6a3bGKW30yXAOZK4KYbczXxHGZU9nsYsi+/jJfQTes57yzDby2Wsy/9VjBPBF/ZpDuVm9izL/OW6nH4WJzFbclImhO0'
        b'crTbBcrLkP+kJ3u5cON9/F5+u2EsF4Z30zQhVi0lMH5FFXmZ33EHH/6LvkdCXErcru3pS+L0Ve4AxFzmRvxrPt4r77gbRSeYH1QnH2fIx3+cGuVpAZWJMEmUmSmg1NV0'
        b'yzzUgmmlCkp2Q8tYidcODirXjMVnTh26SB3AoisOjkR3j9dimbOLD4We+K4Jcg7z1pq8+bHq8we6BQOeQ9Wo1TBq7WRqKgM9lqkwLManqswZ5as0R2RJ2ISKoR1Oo1OJ'
        b'Le9E88p3cadu/BoYF7Io9YUgiyXDveaLnlkUsLG58dke/2CHoHOtcz7QtZt8s+Xw7VYv9wu+L9h7/hh2bMdXwjcPvvj4CatK0+sNItH1g3kt17nZ27+4PGHjwhu/D3+5'
        b'98O0Ly+bvTpV/tT3dl07Dsj1Llo9Ulv43O1VNUavnZU94h83cf5PsY/56UNQxdy+sQ+uMRk/YaJCMSclcDkHFhWdupcuycb/+uoTFTsqx746/MOZ0tlBPm661ePTB6bk'
        b'9tf88YJHdMzVpHEpGT/v75YurL6RtzHC4rnME12C1xs+PRfmzJnqe/6DgU4Tx0W3Vja+fuSNivTzUz97zMopbWZH4eQ5OcNPPRJ6sdhI9HPdddHkj17nZrXlZM6BcfOe'
        b'fTRzpdET+x9efCM4+63tqceLis5fm3/rbWfdqvePmgxkrXn2hqL0ps/WbRl7++vtu0/N6D6zZU/6m76nkyOe/D3TS9HV9pFozLGmyod+mnTD9YmTKTdynD/eYjy8YsXU'
        b'j7/ZyM1wyti7b0nNN/GhAR/ccP58QlLDRpOM9oDLC9bWTE4tubXMbcYHLZ9a3JbAC9njHt9X6GG3c9knZi01Je4+yaUDfrtdszdlJ+hfMh32emPdw9bv/273etNjNl4v'
        b'n7x66YGnp367cnXSsdd+sv0gbsmc3AUXdQ9OePrToo+qi8Mez9T98a2Qoz42qV8+P6Zqz6cNlr/Mezz0bF/+K5tf+ym5z+ezG94zuLR1PaE+FVsjlF8Zfy9Z+KnnODOb'
        b'DSjV6npu5M0tS1cUfvfTkkjrCa0ep6XJG5bM/il90qDhs3ELOtJnfv5zpm5s1dXnhtxePrnwsbCSxX1PmOk27Fy3dN1AycubP+++MW7pjQMHfQfWfXphqvzxgBlDV770'
        b'cw3/tKZ0R+Av1Y1vXJ2e5Mx9kfjhzX9nhz/ieerqz7/IAl5A2zIid03VLZplvvSd6veWlGZZnckZXt3U2uU48YXFG48ooW9n6IrvxG8Nt0efqnn+0U/GdU3/bXHOzxN2'
        b'CZans9b/0VD3iVnsb+8HbzjA69gsXPTg7QV9zQf4ty4tfvtFe9kChl+FM1HkrMfrMR8uiOmefQ0fwkyLl+8yQ0pAZPoOmJF21uHGYNY6L1qE9/fjaJBh86CNuDBpR0OO'
        b'MtTFkEMThLB4HaazGbZMQN3L4LxGbT1mL9O0Vm2GQQoULcbcjwYseh4GVagpuIpPah+4CBWoT60ul2bRhyv1CTc6E+W5Qc+IjnY4iEnU/Vh0OEVxpqWofoRpQh27mHbt'
        b'BBqEVmmQI+lWmt9MmQ5nhHNN93qAxk4bh0/LEuVoFS20oqKR8IYnUR1D0pRGT1CqNbQbdTl0fD7KY0/Oe7toRSUUx/MRdjxVk03ZvVJKo2sJIagG6vglEwQ2TA3QuR11'
        b'xzpo1K+rWfTZ3TZTVdBkFTBZ3w0P2+AaFn3WCB1RusgykrUgvnWLWS9zRYB5TTIjeDtUSDgDQyElEmony5mWsm+eA8WnY5kbH2DQiRoFVywdFNNKXVeiYwrUNodGtlU7'
        b'D1iI2un4ukMD6h8VPxPzTW08upJ2gHbeBqplI4E3l7rzqEbkyab8OirEHSQqz5l7ycSIF/BwGS5BLpvy43Fm0gVwmQb9VOOood2DPvRKhjqlKQyjfB8fdFUhcLppgiMc'
        b'ZiBbXPCxFGnqVBrKXYVoRZViZs3QBTk6JAZhGtP9GqwTMBdyGbOrXSxSpJnjbim0bKeKSwk+BA5n8ugSKtxK52t32DilSqUZg8r5qejYejZ+R9dgTsfXHzcoV66DZYMB'
        b'Hk5g9r6IaWj75vut36Mk1pwuChcDIlFZwRWxOybpkwylWZiwTBVKjoWBhEOojWLmikRYOM2BqyzbCRFq0IanXvaEsxp0KjoNFcypXr1jJp6MWj0C59QCc9ahY7Sx1ugg'
        b'WWoaSJorwZGf3I3bYsf43PJFUnQVndPy9qAJRdxvR5WWO9AQOqrB2KoAtlPw8+FxqjCdS/HQHZJmGmFiusIiQS6fy6KfojPo+AwCWaaWJBIv4lmLR0VREmbMQ4xEK6QO'
        b'znp2GkyifyBdFFmhu5RoCM5ptM1LoZzWFQuFISM4Y3TRWJiyyItOZqxpmNQpdgTzRzCMUAiVTH99yBqVSF1kEahDA2Jcga4zrWyLv/MIhrHQaI8GwWiKFzJpqD/mejul'
        b'DGwIR1AOPxEdgi46T8Z4bGoxxzw6OqAacogGUBOzv8jD4sN1TVxA1AjNgjlqk7OAzJJkJf7mDMo3xtSIu6yrECYvj2GL+TSmkMMEBInljo4RIGTBODbAg1lwTTt+9ngb'
        b'wRlOQwMDt15H13xRgVMAsWU9jjNI8WpGOZaowxA1U3KNRL0RNEOhDB2jLhk7BLh2AO9JxxQU2+69fjNxYoB5SKiT7OCD5jOU8EpU6y0PJBZhBdSQS4qGhbnEcndnItOB'
        b'D0MpOiV1RMV4zPxFqI2fa2zDRrsJchTEROE8HTEt254YuMCoMgeaXe9lxjYUS8ydDWWW/5+RYHeqYv97X4i3DAgkJ5KaxlNm/AnCmv/ni8UDnAWDMIoppJF8GvPTqQrc'
        b'iXfkJ1KVOAEMEmCjwDMlNgMQCjqGggNvyTsIZrwxbyVQRbgqUiH7bShYU1AaUaqTPNb4L2veVCAxChnQ0ZS3EVlTpbgBzmfH2+AfUpIpLY3CLgVyEblHdqdqmfQ20sWD'
        b'KqOUS1xGes9EDPEt/YxdsXEZ0YlJylu6kRm7tkQr47RuSP9BDAMstrxM1OQvaXTlL+K/RERQIVL6X7hTPcj9wZwyGtDPTB/8Vqjt7DsFm42o4q/LNtw8VGXiZIs6ZCJ2'
        b'p9OyI0OBBh20ndvMRUczqYlegQ66plCZSap1AolwlrOGBjEUpEsyaYDXE/j8ateqX2VYWYx7OmmRGJXjzaEQC6101+uF43MVvI12bdAXQWtLhbMWd1aGKuepKtODUmY6'
        b'jQ98vPMTG66LDt57UbG/i4//mu1kSGjYDeK0gOeixupNwyJcDr2+WAHX4ahCZZcNuSK1JTc6kkXvYdamYfEYFTljXigEFz9AC5vttsZb1cqF03S4wDR6sZuMj+vSkcgf'
        b'xLOPYh2r3EHrxnYznNYzweJeNRP1Lvla3zU8qHaSanhQvRfr2UUY2K28o6xQ6kxY2Mz6Rvif+AN6UG8dneiy8GVO2YeJd+emx+KCB1PMl1tUn3pl8NMrQwE2M3aA/Fpk'
        b'jnWj31FTT0+wsFJsja27HGez6GhB1fRVtxrzehvySvyX+1SXTnF7a9lDukFeFhZnqzIPrezO+vB15bOLf3wmZXp82saw2JrYernh4z99dnx6/jtPDV439B+SbDJDc0M3'
        b'6/voJn3j3WUS2zPoOb9kxlouz0TaVdJgNKd5tcXl5hu7Lrxa7zBk/5LfnqxpVzYOm/0gK/CfkyBrMX/v18WC07KHZ6wb05f/YN3t79qmfRmQnH3u9sHJwYfD9L19vB6s'
        b'73/4ieLw3sd+ai5w9LUynni18Ov+9+cmX82PCQttX7nq0bHjpG+H5r7y4ukxGy9knkpetPTyt+ZTZ4bYtkrCH/vovRaXqAMTRDk/Nb77UsWLHzx48WKP9bYXfuC7PijJ'
        b'+Trp9Wnjq/e/MNHx65BNxTFvPX2gvqJg3roln+tsfj2yxX5utH7gyrXeh6f5PaHv4/hbUMeTv2S9ZRH+Y/K7zUs8vpx/9K3E2t8WVAebP/jj0UL/3ufrLZWnL6eF6641'
        b'zNZf7Rw1PHDB5dUznk1F5lNCji5c+TQE6P6R9KtV1ZM7JrXtvjw593raTwPocvfc54M+e7e4uEX2/sSMlp327yfWBcadF4WXTpixuft4xZjEyNVDb9z89Kz+OsPw65Mi'
        b'Mh3n7jS8WmRese7BDXP3XPit0P9Z5dN/LAhqDHjp0VMDideDkt6+9c7A6xuf9/NbnPTpqkceNXL223Dqc7+qyl1fWX6f8vZaiHxxUPLdvOnpC54y+/6L92ZnfGHs8WTv'
        b'mmK3vJanhj/KH3hlxo5P9j2/eF7oU8EPd/z8nd7E01/MbGn99/wDq5remT52fM3ZKa91vboGfWD/4uvrHkl2eVcXvXquOCTr66i8pVdf2/+wX9K2gemPP5j7skn/xZif'
        b'bpe5hlx1S7nR5fYFfyXB9punhnNtD7ssembFd4eD0p/7pORI54ppuwMOXz3APyM2y4k4IZvFrLL7w2YQi8e1UPAnRo9qg0cPVEBZDKs44thMY10JFwALGx2mUMYYkDo4'
        b'uZXKkFR+xPLVQSxDoupoyl4k4LP8DOatFqwfbdUHF1Al5ayWjs+Sq22iF6PzWM6DPjhDLZaXxEOT9A7jT8hzU9t/bkyl/JGTHAq1ue3kJMZvz5VSJj4F9QYqAp1nBDBf'
        b'1KgK2pmY1o46oZ7w906xzGhxDRylFs5m6CyoYj2jy6TXqIcYGQ+4ijhbdFIMPdBnR1mg/XARS6UToBdLHsWqvknNBXRkRTDl6laiXF46CzO+qDBNhnnvnTw6Ow2VUfYW'
        b'82FGSmbLGIz68aSgEw600ER0RaS0Qm0q92jEwNRgpwBtWdBP2z0WHV2o1Ng67uT4PZ6onxa5BLVNxgzuYnRGhxPW8Ysw632ZPrDDTGiLyl1ZFnRgXjo0kMkOp9LhKpvZ'
        b'DBmUTNXYx45LoTzrfDgF2dRbG8dUI+d5OAwXFzJ/QwNQi3o1XuJgCOVoyQ5R0EiLmIoGUQvqtpuo7RMD5frTCwb/uWlaLjFUloyoF1WJzaBwDx3D/TA8Qalii5fCEcYZ'
        b'Z02lpLMfVaGzUvONWk6HElADfS083E5JXPcTM1MRtCxGjTwcj7Vi5IwqVxMZv4iI4iLoSQ7loQoLot0qp12RblIXf1Rvlc7yZOCBG2Mh2haxnImb51F/JpEZiUQZPlaH'
        b'0zMSYlPSGbfdAUXuqDsYLqnc02lc063AnC0xYkhDpVsJJCJo6T1BESOQCIPxlLiXwtnZSiztnRktww5YJbC11wV9idJAaNKSYbEAu4QZRkfhtXocCy1MRsWzhAfhxDpd'
        b'lSH8XEMFlkkatZ0L7kVXmVemofnQCAX7vO8BJDFFp+ngh05eggoUbOEGoqPQwqODi62ZqFM/Fw2PuLiLQBd4dGQMFDPuvxjVi+R3YDAmB4sjMEtzhHL/LqglQDkiGtDw'
        b'7zwWDPE+JJ6CGn2YtX07loCPELNiergfC+c4vfnClsBFVCaLCUTV6mca5gaupPLcJCsxaoVmlU/IcuJIudvXghAnnm3iLsvAT4ASCSpkvpmaocUWF0R4GcjbhvdHLaZj'
        b'1kYdcysshdNN9RI6Awc1huTZeHf5ExthE7hCx2H35I0aHgWdxAJbPo0StlE0eyGcoJdREz3gooLVPEo7jaekHxoleB+6hCpoWUlLd5OyArGQ5wLNy1UBx0SiydCpsgpH'
        b'A552WNavCia4GRVqBnUvlJn9fxSa/ld+Y7T9whip7V/6/pr4lExEGD1qNYz/C6Yk4DoWXKxJCHYi5GBRx4p6hSHijRkVbPSocGUjmpiOxSCcshBZU2thK+qJXiA2wQL5'
        b'T32/4DINSVrQExmLDKnVsg4Wt4jlMS1TwvzXm/FigdWoJ9IT7rbDpcKSSjBiNiEv/y8tiVWCkeOoYXzjbxibNN7fjJg2n9hzWd0zrPrYSAK9j8lg8l8kwdmTMLnU2Qv1'
        b'/UI9viTjj1u6KqPaW4baVq63pFoWp+nWJPcC8l4E+VhIPkgouFv6GhO+W7oqy7pbhtomb7eMRhmbUeMmanhDB4SN/9j/u6uFEXOjPly9O5mPLTilZywWxIITP30LdRnD'
        b'/08/BUORoYhKSSReh4UyHBXdId3y3Hh0QRwHZ2PubahFQuZQ/yicJiywrsZoS7iv0dZWbVsNctg6c3caba0OyAzgqK+4y0mus+bOmTfbzRWuQmdGRvqOtMyI/Uq8UXdi'
        b'hqwLswmXyeZtomdoYKxvJIXjcAwKsbB4MjgInUCnwiQc6kD9UimUWTHDjMOBrq5cKAxy3GxuNjoIB6kZBBbcL8FlV/GkfRw3h5uDT7tjDHV/AboCXAXiC5bYk7iiDjjG'
        b'Xhi2g3JXHXQdOjluLjcXdVixF67gd6+48tBmwnFunBuJYkJVwDuXQa6rBIagn+PmcfM2PsA8npcppa6iyZvxxHPuqAEOMVuQM6gGLrrqwgkYxvwXNx/1obPMAUEVqsU7'
        b'eDeHxexDHLeAW5A6jbZn21K4TPjhAdSKRWduIboaxdpzIgDOK8XQgS5xnCfniXmcokwT8uD4rkClYO6OBXVuhd8kNjidO6FOqbMSXcFsK7cSLrCgBVhEKIPjSh6VxXGc'
        b'F+e1Bspo9mVwFNUqJfigKeO4VdyqgBBWyjA6hM4rRfuhheNWc6s9XGhXH/AWlLrjUAXHeXPecE4FMEc9btCDujmo3cNxPpwPqlvH6mxG1btQt3jZYo7z5XxRN5Sw76/A'
        b'WV3ULRAGjOMUnGLZBhZbaB6cRd06xnCO4/w4P8ygHma1Js9D3Twq1cF8JuePKvQzTfG3xlME1C1x3sRxAVwAlIxjQ3UUMHOEukWoFq+MQC4QnQ9ipgl9WJLJQ926BJ/D'
        b'cUFc0B4ooKVvGxsm5QgdUof1kGNHBwCdgnPovFQ8FVP5Wm7tctTGyh/Ci61UKoyHo8QQNhjXdoT1qcguWKqDeZWruB9cCJSiITY25yB3hZSHclSJOS1CtDPZADeiw7ZS'
        b'CRQpOC6MC4uAoT3G60UWUtHitRy3jltnKKWdXJsINVLdsXCQ49Zz69fNY2U2hMAwFHAxgCdiA7fBEJWxxl1FRy2hQIxZkEKO28htRKd0VAEHUMcSKBCMoZ7jNnGbIB93'
        b'h/QdKpNnoTIJ6sO5XDiXhfGqNkftJ6qJ66iOBr5YD4Usd/t6uBrMpZJSJnOTHxhPmxjAO6AyIYZMmhz/pNLuBWFK7gzmrQGXYM/ZowpT1pB8VG6MynRRLuQSA4dZNugk'
        b'zS/AkCUq0+HJ106cE1ywZzVWzUgOlmSSFTSdm26GcmRO7HrtxH4sixArggI5QUGS2FIi6RzOHFWLsDTTxFMLJgXkoH76DH+I4PC+Rek4xyWSo86N5jBc6qguAz+Ph8Z0'
        b'dREV0MIM9FBJOH6b5uCNoI2zsMeP59hTTwdyTK9dI80QOaw3w+8X4Ay+ATQD5toqoJ41gWSYAXUCZ2GOMzitpmY9Yagrjr1OHkePx095/HTHTvb6KY9NquJ1oS4duom/'
        b'i378HF00oq3boOvHCtedCoUO7F0sxR/MVDnD7UDV6saRZhWh5imqEcCUWkFNxCymQwMbnnQ7gurtUI2AcjHz8HHVDg3TMnCeqag2QNVBdCaIPa+YhI7K6RSIoM4D1Y5j'
        b'/duJsukIe6LsSawLpBm6cAGKtqg6EbSODsHEMNRKO0EzTN9jxrohi6NR2WZI8dbCqme9wLXHQKOqF+H2LOpJ2bRo+gQOE6cecA2uGeCZhGZSC7TSsUyYHcS6yXKslnuo'
        b'aWFAlMk8wFpFq2qi431BsUVNDA3oCruOrDCMHukMG1R96FUPSSmcZg4wjlvDUVrZEdSVTlDd6hxXEmlVQdDE6Ebdoo126eqZbd1Ax81l68iw0iaj4x5sYKAikoUmad7i'
        b'qGmMLtSjrr3qPsegDkY/7XBdrh5b3cmoCbWrOu0+k07+En0xe+aJ5744YYT4z9AqIhNIxDgyrodIE9JRPlTiKk6SPEeYlSA6DGfH0FbSLB74uLukKsZqDZ3BWag8STOu'
        b'qnUQjs6ohsR1Ih1ZcywDDWl6o1pv+JgcVA1L2Epqe7bI+gG2Vo+kp+5nw5GIGpm5Yg+US9VL+VA6ZiGy1aReaMpM6GrwehhkK01khwo5C3f81AZVUELel+CoaqMI6uFa'
        b'qq16K3AVM/K4BIWLVAuJZEBn0SkPthvAlXmsCdk8atPsSCKCvFetdqjaSXPMCnUbmXRcRt+UdNU4QK0Os3usQ5UTaScEO36GEXsdb5fDtJG8XZJ6NbNm5G1ho+CVxmji'
        b'islyDQXjqam31VB5A9QxmujY7cragA7BNY89eJgYWR1HnbQMXeiVsTlgfW1DtVtUhUShYtoN8Xg4PTKhup4bPFVjRaxLKWGhZsP5atJcAbU71AugZa2MpzuX464lChq6'
        b'0NtZSNTl9OCSgClo0P5DylGWpC+TGVBbuIGl1JROz0IclfTMAQNmIPdguhGxmjN9OTTK78eMfexLK0d9YjVn55wY5WS3SfXlrlnmHBb/oyoNovZOclzDvhQto+bDs7JW'
        b'RSW9YZGoKlMw4fD4zPrMPcrwSesV7MsBX11iCu8dZh9lWDxhCfvy1HxTDhO23tldUU5pxo7sy76JBsQOMOgN26ikQbed7MvwAAvOAbeTWx5l07M6XRVnKIXWvmudT5TT'
        b'82b72ZcLdxJPVdysakmU37exSzlq5hw/35JEJNo13inKI1M6A0t/Iavog76p1JRwe5BXlGG732SWOz+KBhvauts+ym+OUwL34ekq8u/xpbSCzftpT7jjdlFO+SETuA9d'
        b'6b9vl9IzHAZNpuEJ8scUmMqlhi2mX+7cNV2u60L4ll3cLlRjwAyOCRmawGlrLTLTS1ZTWaQHrazOk4ZS8pZPjtqbOlnCunh8Dh2M9Zf9ojySl+8ZbdWo8RtGaCNBZdfI'
        b'Ih5pIh1lqxAetySJKbFxu9SBjgy5Pwt0ZGIwEuiIiKiofVqkXIxOBRDbXmo26O8XiEn2PmGj4BI6LV2uC320C2K9DRwWFZa9vy1qz3xfMzwhAQGJfxxdIVFm4Gqqx/R7'
        b'rX0ywGKN6cWsrPg9TR8+/ty3N2Y45k/5pPZt0d6AzeNXwBazqe0BDy7ztLFrWvFJx8aY7lkfm0TdLOv74IHNfemJm7tj49545O16ZWpo9cLQD1/PWWi3df5jdgU2m99b'
        b'czB3iq9Dw2HHbVYrbN/96uYyc+eem8vHmc/P/bbvYEFf9pOVN8ZufnjpZje/2wtToqzd06SufUWvovEr1sxLn3LFp+5NoyknLzw2vkU0I31eXOt7tq//3PTC/G8jJsRl'
        b'vDft1THjZzzR+cgb+gYnH7+xcD4MLXl4z/eDj/tmWPWv/fxKXvfZr1v8K9G+LGm1xZXU9Amxr0f5bncM2bfx89Megz7Fts9c/ibvW+dPnvOWWf8+3nv1V9Ymzz/jFVwS'
        b'YBKb/9CO91Yt2LEibkaj05d+eeEumY+V95u2VV+d5/lsetUTO3KebII4l5QFa/9942T3mVPvPdf9gnjN6x2Xc39u/6726jJj57XtOd2iUqdDw1tvt6a7pa2e9lPre5YB'
        b'yjWreluemGey71PforbNaOrNtfJzmQ9v+7G5M/SHbyx/Nvlj1+HpjxVKhkKOjzu3cI5so0fb0Ud7V/4cYBu45bebj9Y/3bSo2lBP4XNo6MSczJtvv1r0zJx3K933tx+2'
        b'eWX33nDpu3m1ez/N+Xp2gvVDqU5V018pm3IuPea8/5EJlYqEz2eaN/kr3kk4nPJk4qD1Q7opPt9XvtaVsDhE9sP6n177QXLj0oxNv/QUf3j4y1n29pveL37puH3VzXcs'
        b'm4JfvBT3zvSr4lcs9i6c8TL61/AP25Nn/nHy5bERb7//oYf7w+/ufvK5GZ8aRbg9ntFfVT71nY7fFNnJny91fP6z3G3hl877yd46c+j7tjm1t01+Lr5x9XeDsfN+FzbM'
        b'ebMzYazMmF4KrshUkstVTM4SVILlG8leHp2PN2a2NMRTCXXTgOohhxN785jge9AwvXxdlwp5ChqpT+HsaJjFc1J0RiQEwCV6MxwOBVHUF9lVpWTRak5kwM9eAtfoI1Mr'
        b'dzkqhnZfyWoPThxLbA2vQzfzQO4FjcRxj4+TjwEqFHPSHQI64xnPLpRzp4UqVPZo0DCXmaQtgV764nhUSaz6i2c68likFWfyKA+qUT5Vluh4Z8rhwngXEgNGgG4+DJ9u'
        b'zM9KeuhyZoyGCkWoF9UyczSUHccUI+VYlC2RqxAeV/dJOEMdAQ1BF8pj16k1mKmpV1DTF95kCycex0O91VjmS+Xkciyf6aG6QGemcpoLB5lhWDZqkmhFIOLGQTl1beQD'
        b'FbIJ/7cWLX9+V6j7N69kbxkoY6JTIhOToxPi6M3sMNmd/4phywHOX6zyunDvHwOBeWIwoCYqxqLp1MM2MUchhjCW1GeDMfX2TfxBEJMW5vXBjJjAiCzw7ynUhwPxtW1K'
        b'TWgEahpjQH8ToxoHGmVUfasrxvlNeRc+/V3NbaDoligxOUHrIvYvDs97GhsUUtYgsUEhN51/4aqV/DxqpXXdyli0JiyNV8pHnUGSddacZYRYzz50lLdWA/WhSOJraqH8'
        b'eBXESog30HhpFf+pl1YG0dW6riMH5t0Rtm0D7n1JSOwrcJ1CvPBPUbXCXXVJAuhxesCb8HYPinkuynDpA2s4iuOwiNhJ2MZ1Diwu7xoHbx8j92BvskB9JJx7lo6DJZ/o'
        b'Jp8oURIt3G8/eX4a5R39VLxD6UdRmx/sLDl0oi7rtezZR1uqLuddPjK58pCrLZf6os5rg7tlAlOX5duvU1DnMPMhm8Ti9BDw6oVy6qho0mo0dKeemimpoSQNXSIgEjWu'
        b'4h6Xv7ekMVvjYh6IpOwJXUGz/voKOsA5MN/2eyZFErfEkcTRwYjVlVbJanrmE7WoWRhFtB9oiPZ9/NdYA1WA2b9ItAe5z421yZY4EkDlPFRDwcwAZ28oVCEu7rCVgrMk'
        b'hIqCOlsq1oF8aITzYXjAh6ykqFq6mYo3bnAR1Smc8E4M7URJKuZ0rAUDNDifWVRdmgBVciB3wqUBAieM4bF8iYopsWxfh8nSn/Q1ykkumsWp5Ah0FF1EjQq/gABnFx10'
        b'3ITTCxSUKI8JD3UBBtxzu2X4tIpyemiMPqckd0ovpf0r2Gh7ujRNRELIcMiWcs+fx0u4aT5jCBjVaZrZSi6JDO2cNRIiZ3DcKifhUyvRmv2cklxWzd73YnBo5ifffL9T'
        b'xIkkvH3vZFrb5Wgx5y2ypHjWsVO9OCXB6f4QO57gUKTTPuKkQ8Y0X2+YDudhgkfDLirJKWg8y7fD/5d38YQZy3I546UmSnK7G7R1+bvvC6lTyN2X1drVSnIkOT28c3BT'
        b'cKjRDqPtIfhQdObL59UryXk85Zd0qoptcSCmreaXi/aI3nN1ops7RU3nf9X0gsnjTo/7SHof43R5YU6hEa2Xb0h/gdCM8wFO9u1E+tUET+MXMB05rv+cc3QF+tXytVYF'
        b'mJDCg825cN99tHUv/JxVcJNb0MRx73BHvz5Dv/OKeqfgpthhkOPe5XJ0P6Wygg8asEcFPhTO4ypGddCHD/0CwZdHBxMfWPkIp2zBBScIYV5rH0p5cZnhlYQ5j/vteM3z'
        b'yZS1Lx6/sOftG6u5xeUmnWGOJ1rneV7QPR4i86pebPfDg7rTDjxncvvBR7d/op/VZXaq8Ptff/31s58e93joEdPS3d+N0ZsyffVzR38Pb13lnQIXFSkruxY4lk747uGQ'
        b'4NmVtr/vzZt+dGbz9zlPb51hNyNt+fsmg0enbQvZ5968bLh737PLopdZ7M0wX/nvK9MerfjEUsdcGnatXjKubPysAfFnW199Yt3YLY/b22Y0/VH9NdpR8/Qnq/NfaHtq'
        b'9xvL2kPy5KH55xb3G+/416UPjWFBStRbXl2zp814taB/Xr9O7xcfFO77ZrORw7Ylr+x2eRWLZ3/YLRHe//1yQMRVOLRP6nzj6FeiTRFzZ318rfiBNTppU379sTUs8GCX'
        b'7cfftc/XfWn8uLKfrv2W6bzLcWfT0mbznyd0f+je/aFH4EcGT7fKN7bIN8bXzHnyN69Vr9hkT+ha/Ub0y81N3e/8+mVuoa/Xv26/USP/6Uu7Ke/2na8IW7v40eaeNx/V'
        b'/W4HfPZh0BuReX8c/0p/yZN738kpfSMyx/yDvfKXds19y6Qhorxz+HGX7TEujR+YwbtLn66qKe4+KjOlXNNiuIJHVYaK0DWocXbQ4XQSBEclMzVxR+fDCG9EEXxSdBZP'
        b'd4mQGubGUCor8JZRQNRTxagfi4ji2Ty0r0YtlFezhxOplBPzIWhjXThsht+tE/ajE67UTmUMXMhSHoDhjB07jIyh2MQEdRmmSThLdE6E96Y8KKJcm3laEOVMwyN8JYwz'
        b'3cYMJVBPGBDFyykbf6IJEiCbX40GVFgJqIL+RXJf/Lh0OTX/0VkrWECngcr0HZqhjzYNnYcr+CllE/duY2bdRIt/CbOYjB9eBK2cvlSAMk8FHaudcegEflUGRXDKmdjf'
        b'6EQJUw2YXVE6qhLLXWRwMEEN4RBcUSnzgemdhJdMwRpS7jEfEr9SCpcFVI16glmbjomhSuHjT4cZlSZxeuFCHOpA15lRRc4slE+POSkMzlQdc5i9PszevQRVmyjKFZ1B'
        b'V/1keP4WCRYboei/1E7/E1PfUQzoyMlHj8/Kv3N8zjCW0KAxlMk0xkylqSroPDEcsKNsImEYSXgXwmwaUsdgzLUYyUnYTh3KXhJGlTCYxLpawE+pfTUzEVCVT1jR9A81'
        b'rKXklnh7dMbWW+LY6IzoW/oJcRmRGYkZSXF/l9kUpX9MyvyEfHykOcFJPRZ/+wT/YuKdjKeOEabP0Qe47v6JnKW/2AKdWREjqLg1sTbzR/gXqh/m40UaJL/w111JqAu8'
        b'050HPrztCJVel6ECLCouRBUEa02uAzGPZwZXRVi660Y1ib+FPCFWkq3hxxfe+jTqo6hPovyiP4sziH875Ss/ETehRLR2qFfL+YfoT/Xyt4zIrIymLse/Q11b0z/VzLeY'
        b'zc4now07tDkw4c5JJC+H/u1JvGiqPYmEQR07A8iA4dEKcMZ772WtueTsV0hCdFDT/2wm73LMIrprJkUBiXMKHhNTD/9rbb9hU5QUvyX2sVLvaD3qJmfSqyLvgN1/cZKU'
        b'/90kPZD+2Z2T9PH9Junj0ZNEXl7/tyep9a5JmgwDG+QBbJLgOKoYNUmoRhJlsOXek0SsbXLJNPG54njxX5ymUbIdmaK7YzAYBDAIwVV/1ISZ79isEdYbWtMoU2qWPknY'
        b'a9FuzG2/fWBXwp5g+mW6mcCJ17+By4kyTDdSXZSvwrsit/maIbc9elLJjDUshjxRSJcEw0X85/JYlM3BuenQTbMn2utwhrErdDC36/fSrAPMV0csdKK+YGdUIff2EXE6'
        b'qH3mBoE3sUm8mOwvVu7BGW7ftrV9apExzLJYebMqbckTH4bolPzLs0Ik8feVn3j+kIPDObn78Rx7u6zmyp4ftz4SGvR1xQuhVhuqqr4qn+woz3E1mzdtOB69m/6dywNr'
        b'PEsvZ//rTIBDuM2218x+/Dnn5X8bvPPVzTN/PIyWfNYQ0/h1W+C/50bMTl4qGzuxcdZ0mZ76UC9GvXJnByiGTm/iDRtOC84oF/VTViUQmsQaJofTQxexuIO5HCyLFDCM'
        b'5ImFYVS/QQL9EuTlOV0SJSE7YB27dcpP2K/QwDJXrKZRnS+ymM+L9I2hjTAijaiUiMA8ccQ9ZRU6y5iY4g2QrbrOIndZu5XkNqtcl/mzvWizUu7tZAUniTGm2J2HDnRo'
        b'BX1vbFISuyVbCq0jmM3uyLuWI1449zqgRhapIdlJt8fGR5Izj67RJX9njaaQ+xljFfzJih7QZnz651rrNozUIr4DRXRXM4X0L8g7Yep20SI2/e3V22ymvXrJoeQV/4AC'
        b'OtzpJuvtg09Mb2raOglli1GTA1SM2hL1Vb+VlnfE8SoXlRuW68YLsUIRT69shBG/OPF6saJYcbbeEX6jOE4SK4nVyeZidWP1ioSNOjitT9MGNK2L01KaNqRpPZw2omlj'
        b'mtbHaROaNqVpA5weQ9NmNC3FaXOatqBpQ5weS9OWNG2E0+No2oqmjXF6PE1b07QJTk+gaRuaNiWxxnCvbGMnZuttHBMniefixhzhivmNY/ATcj2ljzeuSbF2+KlZ7GTK'
        b'D0y5pesfnULM+H5xHhU9hoScsktmj1g8rdHRZTBvSDbnUXul5uKKKHSo0yFquEaHlhxu+ppdU/ynu6YqbtEvR/5j0KJRLRwJWvRnIYLIimBRishfJBhRNCsiaOUqu/jE'
        b'pHvEO9JQE6Fhvbt27okBmTKysBu2J8gJHWLBqIOEMwl0pgFFZq7xhovomJMLz63mdd0TdSnUCl2K2S/dnhaMH6hzheiRGwMS9LeQeZSKIbYBdnqGeIfpYM6mQheMhHo1'
        b'RCehbcNSqsqFI1NtWTBXhT+P8nxVwVy7gOndURkqcZT7+rsQpCp1ES7nOfMZInRmOZxhLsDyLBYq5vgKHI/ljiOoldgpHZ9DzX7sPV0UqgjFhrv42ajKkFVZbI8uKFxU'
        b'3uThGAxLUwVU5Y/KqApbx0tG91WChC3wI/7mUY1Igto9Z6PL9JZpFgyvU8BFb38XZ1KAyVSREXSsXwB9zCdPNuqDy+wOMMCfXwuleH++irvUk0qvlKbvMMdylSN+KpAw'
        b'QeS2Ag7Ngw5mRNA+ntc4LUKtISzidgMeDLo7n/Ql5iojsbFj0TCckQRRs6pJ/lCo9g2FTmzjZ260oWdn1BQsto0EPHfYCfW7ltLKDPbBoLb/piQDEu4cFRnSK6uKKImv'
        b'PUf9pxku3OvF0RGVB6AzxEHjZA4fsXWTYUhET+G2VLHHvwWa12mhz1Rye0ZG0i6QGP8wN01hrtpempz96Hv/ShFFvCWQv6KSHvKfytFmCaiOBmJXhytHHTCAf4r86OTp'
        b'oRZolt/hNOqA5RZFJD36zbegS3LmMcpkAfMZBaegm4VSKsKCQNuf+HU6KIHT8vhgpJrEjqCZhEKo0DBTwCRQKzJCreEcDCa6F34pURJL5MV94ftKB1PQLEMvn6rLNh/+'
        b'1nvrrcd0Mz5782LBuDrJ2tojZWsiPvEav/E9888a39qQv2bSstecXhwSt7TF/KvslQi31o17wo8cbdj/5niXX9403vjdAGqwvHj4zVSTvId1Ip+bEeG+/siR3z4/1G6w'
        b'WHfe7Le7uz4Mfjm2dvmO9k3JWeHPVX0UkhHZY1n9729DXq77zLD+y9VLC5cc3z8txW4wZsKcGc+P37G+AZmHfbnjva9kcZlfPlRneyZohs5Ei5rgNNf90VMGt67W+ez1'
        b'ZYuuSAc/C7no8cgXn4z99D2Pz0vTPwipjHFLuGJ55VhZwtWMvR+mrO34SR7h/cHAiY3ebr9WzL1m/1nvA19sHv+RaZV/ymt6cZPLX/HzKQ5o3RPju8U39I3tlj6WDzuV'
        b'Ov1S77T+Dy+fpQ4fT7H/rd5pyvvXH9/svlbaUlPu9a8431+aXn8/PfKZP7aEWUt3PnfgV+6HmFPfVz0js1Z5eMALqEXOzkXMZTj7QgeUIObxw9MO+hR+ji7sKVxaLk0S'
        b'0PnlfoyrGoCSVRSjTq/zQ9fT2LT7UiCXhSDOg3OoTaqK2hG1STtuRyEunzDX0gQ4NHJFj9rh4uhYAqhhPmWxhOkknDf0ESUL3dYItzt3CePOiqeI8MGu3tS4NKkUs1Gn'
        b'Ua8F0/vlLYULCqb0Q5iv45eHRDK9Xw3KHkujc7g4O4oN2V5nic6JF8atZ14QCrDgOgQFgWS7EyXxi5LCoCqe3chUorYQEh2cbHciVMNDawrRBHnTp+vxPnGKRNEYiaAB'
        b'TbHzJ6WycRmYBUVUW1QUGE72LdW+Z+Yugjq99bRtYr1t+H286cGhCap9zyxLBFfRdShgwcChlgQtCFTve1yEnXQN7vUYyKZN8LISkWgEbOPjvCRSewHVwgWoZ0PWLcBp'
        b'B3RO2z+B4IwPn4MU/zULBgiQOlBrszLRF22HQxmQhwZo+cSGGZWgXpqLbh06esL4GDhBC4iIW0xm5NhMgkpU7xxmqFGEGVjoZKOfFwUtNAoNdTcHdVApxdSDrpqgYUp6'
        b'EdA/nsQ7V+3OxitE01DLKrcgGsEg1CpTjtnzg1Quu9cOsyxTd4wDOk97K1pHlB3ouOa4NE4QzV22cAkeSmrodRHVGNLZgsqJmi3IbL4IrkmcmcOdC6glk/COPlASq+Eh'
        b'zYzxrG6CTpnkzy+B9P8p8kDjnL/z77DjBzgDA8qMG1Klqx7P7tAIBIYGYqY/xC+AAVXjkvswHd5QbEHBMAbUbb/6W/ZjKJhSde7fyW/A7zFVsYh3+uRXgWg+Gi3G6/3l'
        b'60WBveo4api2/20xodRGGzZzV2P/qkvu17n7esV+GreLOd7X1KDxuT+FerpXsaIj3t//uZP9W7qRysSElPu6vX9O3SBWvdrtPXkvOiMz/W86r1bVK47cMmfLfSp9QVOp'
        b'w6qk6AS7xHi7xAwWaNNzjqdmDP6JV/K19x//lzU121DH1OlxsYkZqel/O7CAqrbr949i8Kqmtomq2lgsgb/fO5U7f/3I5NTYxPjE+07p65paZ1AX89HKDDv2Wsw/rT5B'
        b'XX3crriYzPsHUnhLU/00TfXstX9Wt4aWKQ7sfjW/o6nZUU1WGVpLCtMXK+IfDb1uZGzcFkwq96n/fU39k+haovn/maf7ePWAqyn0PtV+pKl28iia/m9c7Otr7n/uU/Gn'
        b'morttSViMuZqcXh05aq66SF2p/kJrzE/4Y5xWLDnsWDPUcGe/3/MfQdc1ue1/zvYewkoqKg42IoTFAUHe8kQcLGnLNngAEX23htkT9lLAUnPSZuk7e1I25s0TdKkK2mS'
        b'Nk3b9LZNb/s/z+/3gqCY1Xs/9x8/UXjf33jGGd8znnM4w15wW7iRO5Q96lmvtdxzUl2+QuHyFReC/4ZNdDn6So8K5zoNp0SxFs5PqCwpnO92wHX6jU9IedYnsM4vsLId'
        b'zzjefymYkebq0pe98BOuLn0EK4gu1yf0bfjRJz8xEnI4xBpmGOKycBY4uZmvWOccYmWJG88pmR64cjSXa0zz5ZFEtkA2a/uK4lqd5pMclojI8BT3L19HnQ3jYwXJOcUv'
        b'ralzBDVr66lzib+22EfQb8rtDKu+zAAd1pk4r6wHVj1V8ceFg/6wJKMIS6ou/3vhlGfzomhXQ8ybBVw4xbijhYVTYiI+CiqN5IIpsd/+PRnnPxaj6jclu6sVAnm0uYkw'
        b'4/z07k7CzBeFW5KCvvY+K37+PieHp6xDb/Hr93p9EObJFauD+svX2PXSdWEY5pIm22U2jXYdH2Lrl9l2E3du240VsQgeOxuJOLfYaS9c5ggCB+QFUqpC6L96jj/f+eAs'
        b'VnP3bMU2gdRBIUxp20ZrWjwQcmGc3rPvX4t0DHUNdv2bVnDMuwPhUZFRka6hzsHuwcI/6l7TjdH19n9vv/TBxD6xYLxV7j+vv/NMYtnGSWZJ/hLS4UthfZVdEyvJqoiy'
        b'1J/ZuZU3b7hDT735919ja2rXZpNt8P6NpTEXDOOrygtWg2FfJJOjSCa7PSNQz7DkuWRe45MEXu/VTTZITomOjTVIC46NDvscB61QsJEukXH34dtFH8zOEsjRNWrXemNe'
        b'P2XuEx1t96J0ciB9YyoT92HQ90L2/cY5WCniffrJVENc7XrOy8g16GTyhHZlmNGrd/8YoOBqOxSz2boxRtdat6Wp+ESMrva4eZigeL9p0KWXPUW5aPCNym+2Q+t/eGnJ'
        b'viq2bDioLHj1N7qn+hSN5PhqJ204hHkmayIWKjAr3nTOYTvfcFLX1lDixTXHMTch78WFtoPcl7ewwVXiEFUPZ18yf2goTPC1Ne4HRZmsETDHYJTz72IxDPE51gtYA9Pr'
        b'Ha7uev4wiQ1c7rZYLskFGoSSTgZC6KA35fKDroF6XDIhLnSCESmBTKwIlrFrJ8v75u50xbHzLrZ76UtTGYGUvhAmM7FxRVd8UaBKLjo5kNtUjlvOflVu0eSr73H/c+nL'
        b'rLiE1Brjb+Xxz1NpG45vnYaTpRs/+xoMVaCxoTW6OiAjzY2qN6wp08BFzfzYIonJFktijuOk11nVBrkVC+INuRUw/4YMj4vfkOEh6xtyKxjyDbkVGMiJBm46/Fr8+90L'
        b'14idj2lg19gqudJvckRA+y7/+8UTVBSVRJwL/CAyz9rUqqdHAavVoVwEC6nQuU5da0j+Tb77dKhPpla3VhAmKmMBMNkC5QKNAs0I6S8f4uPvIhyhGKZ0T46F+CIE4XJc'
        b'UE2OPTtMuUzI5X4r0nOlwlTCVLnnyq9+J02QVS1MnftUgRuNbphGmSjMkLtHg7tLK2zTPXn6XpG+F7AramXpj26YdplM2G6uCIS0pGmHcoFKgVqBeoFmgW6EUtjmsC3c'
        b'fUr8c+mPXK08jVWvTBy2hwtrSnOxN9ZxRqVAlb2tQKtgU4F2gQ7drxamH7aVu19Zcj93d61s2Da6fy/3TnanKneXNt0hzwUP2R0q3Px2sPnRDERhO8N2cTNUDdPk0NS+'
        b'N1QkhE//BEeGJ717iDZmnfy2M1h/BRP69G+yQTDJ+7VagEX7glMMgpOYa+V6ajQR+LoHRRBU564Po69CU5jxFp1ikJIUHJ8cHMos1+SngoJOKaRVEpIkr1p9S3Dyqu1D'
        b'6ijeINggMjotPF7y2ISkzKceY25ukB6cxFp2WVs/G3VkZtVTE1zVZqfP+diZG5xNiN+bYpCaHM7NIDEpISyVG+6O9XFWiZPMgwVb1x5AWF8pZLVKCNv21Uoh4kLxc48e'
        b'iDlbVerdi09vDLdET8VaVxRy3MpUvla4dXUlmf1F27l2+Tc0tNiec1sVZm7gxHmawhJoRGSYGYRnRCensE/S2YqGSFw04RuABMmAJDY1P6ZnLO30aDZI+iYilR4XHBZG'
        b'5PGcMcWH0f8GwYmJCdHx9MK1nqjPQShs65492KHsztlAfrgQ+KT8pouf42rwDKuxzPW8I1TYYYmFl6Or+0ohMdLFBYrYe3t3KqvuYuZk+uT+c1C/9hF0l8TpnoYF8rd2'
        b'8L2fbLSw0FANawgkO0oJpPcKsdEKBvjyGu2sYLYJEVjGyVOCDMjT4oLJgdgB973NkB2P77UUiM0FqiegDupFhjehlyuZCg8zjj5pEMWOh9D7PT2v2nFtoY4aSUPVDlO+'
        b'wkYZ3k83ITWSDHNiQfIV7OBw2kc2IoEt91OQ0h/sTgq4uXnhuOGTaKIXFnJdp8pMsdzNlAZazNXNO58gizn6UMvZBZauAYSlkq9Ls+P+rK5FMeZE+ycKhMnfpG9fbgs7'
        b'V8HSl5Tys/uV4zJP9TgblMNugfzr/pb3d24qsuxTNI24Y2L42rv7W4V7FXPN/nX75uzmTc3vlinZvO9e6nzY5bzx0LTz5W+/8SPvl/ynjhT5mXV9cM85+Zc/Dt+xMzEk'
        b'+NWCLDRqMAtIevhDOFPk+TMMKlNWGUi//mi8OuHqpMux3fA4a5N8k5p21Q8+TbSZeFzwyntRP+nQePlCW82HDnLnFi8kv3dsXO3Ur95xcB0Z+uTXJkuaRw9fsTjlfDti'
        b'/Nz1vwu3v3hqJjjISIuP9vXhCI5JwvQ4CnUhwgM4D6V8nKP2MNSvBOyMr0HpmojdpBp3v2MqPuQi5lCSKOn0g/0ZWMoHzO7L35QEEg/jNJ+x1MLnQWGbB+ZykUSlndwF'
        b'XCBxL1ZzT7X1xpzVY3+CGJjjEprOiHjEugizMHke7rvw2RFGMgJ5LRF04h14xA97Fgu0sISUvjvbc2MZAsvTYpgQn4cKkGRw1foQET7AehMLLGbAQAYGRKZQSKCYLy4I'
        b'xfphMPQkmMmHMrHejStWGRdsQJiZlswmUmqHENqwJ5QLS168hvP4GBfWVO0XHQzV5WrdwTwswbwkwsZsUyLxZmsXMxmBDsxKOd7CWW7NzprAWAiUr+J8GU2RcoA7V3AP'
        b'ujW8WZE7F6jwIPg9LRmZOjSIaWIDTtzMtpiosCjZKpureEPzVrGbHTSkMA/YVpyPM2cJFuxUKEsR587zQLmFixlX15A11HGACVmoUNvKRzbLTkPPStLDIajm+zRIYS0f'
        b'K5vBGq/VKoHYky4pFCh1FarSuLR+WgHoZ5nJ9BbudUG32QEigbZAjMuQA8XPJn99mXTqjUJjPl/VCLBiiFGGSx1X4ZLAlbhe1ix9fBtnEvBBrCyd9Xr4OZ2lV7XsGivh'
        b'c0KBYv7aDQJYeoo0GeuvZjTkCN5bexjxuUP+si5v6S9yAJ9QlDiAn3nValDr4KryflZbr9HMXyvKJQm5vSr43CDMqZVBfhn3+IqiXeeh3s9jI4aJxP/f+agZ+krdCH2x'
        b'/9a5qZPC4xJSVjvvEoyMSkiNDWOoJy08iTMJDYIjgxko2/BZq9lyZ2LDg5NYO9ezq0hM4ufmUFE0j/qYtyWVOV82fFhyeApDc0FBPkmp4UFBK6Ea42sJ8SkJ3ElIY4PY'
        b'6JCkYHo4iwumBUfHBofEhj8XTKWsNlNe2Ve6LSEpOjI6ngE6BsUdwpOI8jJNDRLYcqRHJ2/8ND4SuTpA++DYZBrh1/XhO0y5SnE+fL1IX86H39sR8Y6rrECuSDgr0DAS'
        b'cvJRHpcILj2Rj7jk4PhEQGqsHEn9H3TjB2bteYpjk0NjA7mF/7e8+We+lthaXufPZ36cqziXtmqy4wz7wdXDDKvDVExWlQg7YVa/oWdfd5uKjabD52Tgcy7HAuGXzsD/'
        b'Eieepdy55mdauBRCOq3nae3K0jSLXI2dTWHIh8/YZB94uHLpj8NQpGjlBo+jz7qki5Mt6DFWRpEfBplrfBD03ZB92sbBrsGxEbEhHwVNvvV+UHzER0HFkc7c4QtZQb2i'
        b'nMbid4zEKVyV/GoVXJS8ede5z9XsUKbPJVvh4Bas2vBANBbulMIxT2jj8BSWnFLkKfRs+urySwj0/OmVWMDnK+nVaMRX9muHMEX8pUj2CwITGySZbxCdcPtaVDyzLtGc'
        b'de518/LdiIiPQNUXUDEXqNA9reIEZXBP0h4C8qDWkg9UlEE9H6nwgWK+9mFNNNzj7oKuHXyo4tTp6IVmRTFXymD553KSUEVwzLtbavlQRWykc6g7F6zYvCZYESEQfNNU'
        b'Prj0L88GKz4nzhT8tXfWT0lBTSpL93k7+2zg4gtGcfprbd0La0NLzx8NiTvmV91YsLCFZrnzJFikSbRIr4oW8eemqZP+/nvfM8rFgdRP8Ao2WuvHer6vJC4pPIL3SzyT'
        b'Q7SBOyMpPCU1KT7Z2sButQu7ZNZBBgkhMaTXP8cNsTGgkXZPPcTRIk4rcZYXI3tfTz+zC34b5rNDzqFt0CgfE4tVXI8PKLsdxpvoMI0PnvgtVu10zkb3UpQl+m90iO7+'
        b'8felkj3oPuX50x8GfRT0QdArIVERQ+Es/uL/gj+OV074994zkt6361s/+O7rL77+DU9xz7XN1371lu5U452YgMnGqaaSVmd/70bbycOl31Bq3SyoMVPPdIwwkuFssOup'
        b'10yuwN3VFFgyW6thic8dxByvJ1YhVMIQbxlu4ivlX7yB95jBjA8DjVYFKmcww10c4PNPR2DIYCUvHuo1hQeU+Y4CQVADcy6c5UaLMMpZb4oXySi338KJayi3t3kirbdj'
        b'1/rUWMjBpXU8+3zbY21RC3beR0I0HBdbf1UuTuRzCeW47kNZW57inzWPX5/zd2G9cN44nCLiL3uCM3ToET5fi81Htday+ecMc2MOfyZT5fNgwwpvz2zI2ynP5gclRKyc'
        b'JfnfZ3U7/p1fgtU3jokSsP3Vpa3CZJa6/JFs5odBl1847PaDbxDL1Xfm7yg5wBVlsQCpG74ZRiLebzGFY4bcuVZJzi004TJzumzBNqmsczF8mHEYH1txJzPuQQ2Xccsf'
        b'zcCJ8BXAuXHcWvFr659sActN3YgUJPvyuRQrfA6JsvGEfS0SbVf5IhKVjEvy0jdkk4PTwgODk9039uuzHFiJTpLhLFiZL+nVjyS7MmQju3KFfFmYI0xSWP5LEa/dakgm'
        b'PCWYJQIG88lScQlppORYKfiV5/5PUT5/j2SBrJnznwvGmDIbLy41OYXZvjwnJqcwO5ElKDJfxYa2Hu+/WJfcxuxEevhG4YJVpmNjTQpO55eL5vw5vMZo6VnvvoJ7Kgvw'
        b'HjTDmY20ahC2b6BY5WO24gIHDZOhLNCEHc1yJKYqEGAd3MdFrmBMzHS1t+/xq6zSjJRAqkmYsqWa85oLiYblPPeLWJUb6/03BD6c94Sv7tyPU2dNPOhpXlhkLMBmD2yK'
        b'No/9rXQyKUnB3c/i3L77QEVkpyZ+x/2923d37JNr1xFJyf3K0HCv0Ora65ctVaq7K9645a2t1dfltmzr+GdNS83Te7Wu+zz8eNsh+YBd3/G+qxL6m2tNL/ZGnfuFfL6N'
        b'yjEMsPb+0NjC1fWDi1kfDhvOdCq9rY3fNXtc9qPUH739w7fe/uGr3+obvf3B+yM7/5pe4X/5lO/wHgPhoJEc3zaoVR/GTRzDnZ7o8IuqnG85DarYIRX59HWeXetEzp+p'
        b'fChz1d+9ortlYJzUdz728v0Sl43CTJy9tJj3l/P9QiPU8T7lBZzAWhPjYPeVUxTyx0XQYUPIgfl/fbAWGte5fyW+Xw28L+UIHVDIPcWTVTxivu+zUMC7v/nDvFUa3OiP'
        b'Y5WMxGeN97fwbmuchLvPUaAyX9aL+oas5OAvJ0odv7ooVVOSlNLQ4FL+NbjDBkpCLWGW9gaCjF603nnKCdHNoi+BCcRrrn0idfXo14SvJXVrtNdK3ecMlhbSY+VA8hvy'
        b'qxnyfGaEnIgdaY4Njo/0sQ+VlTA0m4bGCkOzVgncMVbmSVTgguIsEC8qUC1QKxAXqEtirxoRGhIJLVsoTxJajiS0LCeh5TgJLXtbbo2Evi21gYS2CwtjqfTx4enrE6GY'
        b'n4wPcPLx2NCEpKTw5MSE+DDmzXv+CVaSm9bBKSlJ1kGrllDQOh8Z78QzlbjOVr2JLOL+zMOCnxthNwgNjmcSOSmBJaWsZBKnBCfR+huEBMdfe75aWBeWfQpXbRiUfa6y'
        b'+DwFwxaCRY2TE8NDuRma8qu8obp4coAjPjUuJDzpS4eYVwmLH8aTkxjpUdGhUev0Fjej+OC4jR2ZCbxPdWUdohJiw4iY12jBp5Lj44KTrj2VFbG6ackG/EkScwOPFecp'
        b'f3t4SlRCmIF1RGp8KJEHXbMCoYM2fNDK6EODY2PDme85IkGiVFdPifNEkMry9FlKQ/CGz1lLQ89dydX0Q2uDp4+ZPEnRXnnv81K1Jc8KsQx59ilrD6t8wf1MMhAC8fYw'
        b'OHLQyuwA93sqSRdiwrDwla1aeRaRPk8lG3udz4ZHBKfGpiSvsMjqszbc8b3JBtyvLPXkmcGtgykSymRTSSQzgX76EiBrFb2oSgTdevSy151DIeeh+6w+TiVbksAXJghg'
        b'Du7BPb5kSRuZBLlO0opp14UCIRaS1sYemDYScvdZQP05M2hh7jIylaFceAbrkzg8FIslanTPeR777DM324eFFsZObgSDhnwScTLlgieXMAC1xpexVf4YNG3mEgFwFB6Q'
        b'Il+bJ0EGh83mdTkOoVfloBPyzvOFtRWVBPq69E7PoNiQs3aC1L1MRV/cxKADl6Qw4MPlKfC5l6ZGZs7SAhsTGWzejj08ahpP32/CmptAlZ1QXQDtuHCJe/LhWFnBP3S3'
        b'sTqBptcNHPnqK0l0++UD/KHvN0MlJVk+9RMJYrezathBpvtSzwv4tjRFFjewm9UexM4ogWKUCldoi7u+NVhO8F1lMryYWHbcLOB805ALZSIsMcMRmHJ283bk/MRONIFS'
        b'EwYhVzMu6AtHU2dXcyczYxkBlhgpXbeGO9yi38Z2o2dAaKmRs5srDPpI8KfRliCa6R18KA/dydhkbyTHH5xfOCRYc25eBmqE0BKAk9wKaeHDM9lQsnJ2XmhhCt3cQfSb'
        b'OMc2a+XoPBRDtRC6jmMOd0Tc+7SbC96F4jVnUrnj8xVQwB/l701kRXlWjrHjHWwWwiMoVeCbONT5Yd9Tx9iDoF0cYo513JD349hefAjVksPskqPsNeb8SfYFJ5g0wTKc'
        b'PrrxWfYIuAsFRorck2AA6lxWiy/AOHYJYRge7OYPut/FecyD5pjVGgyS1N07gdz3h82g38TZDduhx3xd+YWT9nyeem12hAk+WCnAIMC5CJjk3cKNtC9mUSuOJuEBbMB6'
        b'fmXqIqHCBRqxeeU8Mld/wcGNKyQWCQtQ/kwBBpxVE59WhXL+AY8tz63LB74E3WJ/6A3nyzuUYGPsbWxcLcEgqb8wZMHNaFM85Dx1tB/Gd4ivbMY5vj4DSYe7aQkrNRok'
        b'XgDv/dykoreeYvlDXmZQdkRGIA4XHt+ObfyYarHN19ssw+wCVvp6ss55ZkJo344LXDGF6/bSgiAHrnin0l9drvAJTNAaFA+jmTTXGg8pgUhJgMs+0GqkwDUdwVZ3aElW'
        b'SUrFCSWcUCU6m0uhpY8RZ8CS0zk/vsFzH5buS1aBEce1lyXjdCpzbfSJSbzVeXBXGoqhYO3D0lOuyycpq8AUlsoI9oml8K4vtnPvlTWBPpxKxenk60rXoUw1KVUs0NRn'
        b'/TcajkK9Ju8snaRxJ19PVeCepYoz8mR4TKcqwTTeo3tWhnDqqoy0Jbbw3WLuamLV6i0rV2iGi6EU8u2w04urzgt1ZKNMrV6WjsuwwI9URrANRqX2QMtmvrRbt3fWmqel'
        b'JOE0DfOcGBeh3PooCQzuojETyOeu6jghed5kioxATYblGS1BC8eIW7KgShFnU9KghkalJK9McF75tgimoFeP39gi38Pex4+YXfD0ZNsqjQ+FUIUd8JhvPwJ1UOrthlXe'
        b'xI113lAmRQTTjO1eQpzFKejhizK33cZ89hKYwO71b9GCGUkVEx8sScZZVfpCRPv6WFVobHEu9TB7hTW0YQmJShcLN1cPX6ZZvCRGtykTmqVOrlwKGdRLEzv7yifDPeQj'
        b'M+pQD5MurLWpm6LQmpHoIyzkMuFUoN8WpxyxLCzJyMWMGM1diq5uFUN9FDzihHh1mp7g3t5YVtz2RKxcFC/ZfZxMBLUhY+xDUeThSwK+nYbgr6ckP+yzNZLiZKoZ1pPF'
        b'P0w/ZZKEKRZkYl0a98VJyCFZMkwqOgt6cUmQJUuEwLR2EkzDIpexh0RFgoxsLOK7RTXQoIexhDGf4hlBNPZrR7/4ToY4+RrLvdt9Os7reLyWndqD3ze99bePy7MXtv3s'
        b'rxV/26vdKS4XyMjvsjK1aqwb+cnr8l4ev5Ae3Pr6R0L9PyfKiV7cfExBqL5j7Ma3zkp5/2no7Q8/+GDoVaweOmPmItSrfXXn73z1TPtaTH+6UKVT0LDtsyMnu5rmNWz/'
        b'+U2TF7O+952mPedTh0Lbvi/1X3t92u4q6jfcVRw+dfH94J/+MnHPsus1r7C/KzcJAl/3NEsZkXKQTnrNy+L9P7z9ywylazt36wWHOvwl7LtOu+6dk+/f49ul3tZx2NAx'
        b'MkJwIvZl+59r/kjPuk/zF9+NsfrNNyIDchbcU4duWLcVFR3V+Ylgk+qVb956sSD8ZM1M/5TlUcVvX5PSsuh8OfWN1BeOlgy8WXBENn3k5tS910yPHtL5Ubpr1n2bsAAj'
        b'hyC1uPbDZpoW8++/HvDuR0NTeVPXvjd6fOHdj8RXFxV/+PFES/G9i6dNOmt/4DQQNvxu70LP72c2f3j7hnbdf//i19rD/2zSV2988W8ns7b+wfnGnEKGT+Wvzax3RvV4'
        b'3/N85+Smf/7yzEtzFh8u/FNWuS92uPE7v/1wFHxfulc2P6Z/+ZXQ72V8aj6668+uF+Yu3zdpWZTx/X2Sw2L5m4e6rf9zm1b+7x6OLZ7fa333X94OEcOdHzo6NPzM2ChK'
        b'w+DvesmZ97vTzN/77C/2f7aa9P5nR/PRseOBoS994NObpvq75TetzijPiY4dWTD+tdnbvxn55EPXb/5625FM2X/denuz5sd/3Pbxz/88njqROWDprjAX9weVlDc6HX5n'
        b'av3xxAcBvzryQdFbA1nv/MH78AtpmTqnTsLR749Ezv3lHy/0f+e9mozf+/5cWv4D97eHl6/8UNa6Ye+RPym2KN/8e32XR7ZwYuofBX8NMzLnamXIsUgoQ4RJBGiehKI1'
        b'nMRw/xbyzQtgOBAGDSH/CaLAUmjgPNGGMMF1RHDE4vNccNyDu0YdC0gQJsMcdxFOQAV2cG4gWIS89WGcFJKIXFpc/7FwF9Ljj1ZgI18qaHEz33O53o+d3fNwhwLoZel6'
        b'61L1bkMRFwny0zXkswildkCxNHMlzTlzTp6d+5iniKUQkqDJlaQRwkQU50fCJiyBOt6RhK3Z631JUo46mMf70x/gzAmu1BwDdtAK7XypOejV5IvULQn3mbi7YZmMQOoQ'
        b'1OOQEAZlsYkvQ7cIdy/xXiaH7ZLcSOyDYT5jdNI++0luppQV5AmEMLHbi1uWgwk4wMrhsmq5udjCl8PFR3CPv7UTena6mMAojfc4DpOSzhQZwuwJzvHlCzW3/W3WVAjm'
        b'ywObQwnnd7sIBU6rRWlccFgIo1uc+ZlWYbUBLtx+Oh2UpszPtGkHjuHAdVZ43kKWLIkuoS8Oq3C0ko0L+NBFcnYJOsyF0JFBtMK0hk0Ya+RoiuU+MEP7R6vhZkoIwEKM'
        b'dZvhLjfk04QSXHDs3JNsSy5eh2NH+Ejf3XiYv4oNTzDYmXBuRKkEhZ/AYWjKJjjsgSN83+peP6UnoBdzrQnzeuNDPvP1AaHFYhcYtXwK9abQxrGbr8tB8RPMS5s+T5g3'
        b'aSuf0/ooOvMpxGvpJg6BQnzAb/qMsjXOR60HvPPQxvU4huI92EOIF8bPPwfx4pItX8elUHcTewYfpaTXYA4Nu0qcEIVF3HvsYZY1xSuy8DCDkeMiRpTGBJerUxiyFt7c'
        b'vhb9XKdBZdOCjgst4a7QFLuk5Wm8gxypqfucCAJa25WdkcNmERQbYQ5fVKfGHnokRRihyILvXK9nLwXFVtCWHsbXKxqAWUXWzoQtyGFiHoEsdorkBJI+7bdhkhiB05Xn'
        b'iOyycIm2nU2RdHSSibvZuZA1ZW01d4kJ7zZc5V4eDeMEfrhaNOZuWOzsZk7vxkYpA+yGVkNXztOcjZ1K3CWkgD1MCQPQ1ogEOoelTuGghNF7bxwzcXfw40uNPlNmNBNb'
        b'uVns0AxyicZlNpBifj8UmanXqZolyXSGMVLiLGRNVyxBEa24u0gf5+P47co1YnB/fa70JZH4PE458Rm+j7ApmqDUsqVqmkQQyuOgiPb0IZTxy1iBNbAYDgu0FWZG+xjt'
        b'RIpo7cbOGKn++yfFnjh+/xd7YK8NiAeHha0LiH/AkNVX84UfUeK6UMtwXUtWylTzOcWsGLWuUEOkspp1LCcScaWoRZJsY/rpqW4rCmIp4do/KmI57knsLQpC3n0tx5W0'
        b'luK87gpciR5W8FqNG4OKUEWkwXVjWem8soUr2KPCZTyrcGWw1bjw/Qbh0DXLIfHYy/Nu91V/eJI+c8WvesKTtq734v97Rcdl+fc8eTD3Ru5lxqvv5iIAO+inYkVJ7civ'
        b'FAHIEfzV/PMir2uWwEj8htxK4PPJOctQKR5/C2QEa/xgngIBf6iKd/zLSxz/Qs71zxz/ogL1Ao0CcYFmhKbE7S9VKJMruCWdJcNCst6Cm9Kc21/qtvQat7+3aAO3v2+i'
        b'JKt6vdef838HS/y3qxHb5/vSV65Yf+4qReKKXvMIU4lHOjQ4fkM3ZQiLOBhwzYaYS/H58YWv43pnwYwN32q8MjxjA+5sFeclXRkH7/Pmh8QCGDT0eN7PvLHb2+BMQlj4'
        b'QSuDkOAkzk/LTzgpPDEpPDmce/ZXi0RzCyiJUjxdaWmj8AI9fuO8Y4nzesV1z7zlX+Td/Sq+3I0bCG13Tz1KP+/CWgasV5uQn38mxcv/8pNYdLmRPI7BCAymsgPL1hb0'
        b'xYrftOjsadfzjsyTiIUe3uv8p1nYLw9l0HONM0DjMrCFj2ELsPIa1pkgX3n6hfOKrCWjnIHO7djrZ1P57i9+GOS9/7xyoqT7S/6dVBbJxGocyDCBAQaVC7HCm/k73Vw5'
        b'ber3TGouQcw5HHxi2EsLxL7KBH5rcY47eHZgbypO3YJaId+uuhOW+QoBLjKf+eQIDKQE+4PC/Z06AniT/PUmWx/u631yl+T+KJoXCoJyYo45SvnzX9t32caygKFhQozw'
        b'xyKBmoFlxnF7N/4MXSuWOB9MxSIpvt/5YkbqGaaOG6Fafa0HGwvNnN2whjluCRI6SXziXEcll/OGuxydTZ15vMfqsio748KlVJYoA0UXfZ94cyH31ufm6snH3LxpxDca'
        b'MITcOL5G/Qr02X+Zr+mPuTjLeQADcCx+vT8Tp1RuQAMucUmCUIn50k/ejYM3nnIm71u9F+7AY/lbV/E+t4aXfLhuoQI182uu51KCJe4P2xj+wN/Psi7E+AmjhALbnCz/'
        b'NNktq71GOc+4kTTvFb0H1TgIw7jAemBmCjKhHVq5bxQhB5rJoGuDuwzxERXWQjvXKVN4brcJ69Ary7XK9LvBdwRvJoyNJeehgeE9QnxLMZLys9AeytKw1bgDXiVkXR0R'
        b'EgLrRr7H6y15bHHBOZWniptegRxP3lt8J+oW2XflcqsVY6GLhlwc/f3D/VLJbUR1nd/bZlNpk6x1QCl/988+e/etz/4Yrpl0r9n48Bk7p3OyWp5hA4eUko/WhFj0vjle'
        b'Nip32c7ut/9t8g+52wqH/5j05nzVpyerrzq9YWaodfQX//z7Nyrt/fa/41c7nm2+56fqKu/eNpuRClDtyzY6KC/eBrUTzZm7djx0/W32L9JH/9XT9t0f96o7ON/6eOf+'
        b'nrspKpuOa34iVlvMS/+Dum7FfPaO+X994ull5Rs8NNkd9XpP81D2D//z501R3d3W2rGvfNj6c6+J7vzfKad8cPHwdrOZoePNg/90SHVJTtv71quuTSM6Dh/p/W505qOT'
        b'LSfsFv8+X2c1/KfjyX+Y+JXX4KXeixdb3zL9/kfX3ko6/LdPo/t0rP/rD16FDd/UltE0afr9tz+48srVVwz+mfLTapOY6P+OSumwzhr9bYjY+rf9Xm81KUSfPP2fV910'
        b'Psh+xdjsxWiHXAOX0flthx79a89+27Pfmu75zj/sS2z9Jt7NvyL7tyMTv65v/+jNH/7Z9rW/vXRh01Kx1/yViVdSvz033dlfsfuDF7Verzh27trftl8Z6GhR/sGUcqvl'
        b'1tf637f8eOh7/7jxh8B/igSBDfuO/MNImzc5u6A2wgQ6j61JIU2DPA4ui24Tba8zVadvkWE8B9Mc3lYPwvpnUlCkoAAq5FICOQPKAEfinxTVwCVciBXtTMYS3vkxBa2H'
        b'XOAh1D4pyJGZxA+qBkcvmxjDkPNq7gpxegNna+y4CTMbt0Y7g804lgTd3CMcsCQOS/ZgC9dxUtJtcsCBm5cyPMbllW6TUCxlLGk3Kc8fjdTAnm0mZup8Fx2+cw9JpOaV'
        b'45a1ULTaY4c12PGDfqjBDnveNJ2MSTChEXFTkt8qgsdQD5XhIbyV3b8rzsRsH1fF31eZ1fGXyuIM+HM45cwZ8E+s97RMzn6nQY5zL86+GO+C93azjNsBV4mPRvWI+DLO'
        b'neX8OFvJ8LnPW2kVblgXRrKUtIaJjEAPWqSg7awpN7xIqNVhN7NefwIZWFTRF0lhP3Rw+4k9objA24IrAhMfR3PmYlIaZy0meztLbMV47FprLkIrPoBR/khrB5mUPdxl'
        b'64zFnbBw6tzFFOa8d7wAsyt9KRzPYuXT9iI0Yidvr83ossbfT2w1RVrPSciHkn8Tq2v+LxpoT1lpSmvTDTgzbYhJ+69mpmULzJU4o0lB0n5STmIg6XK9gugTMX0jYj+p'
        b'cYbXyr+swxDrLsRqoCpwJtaKMafGmVRKXO8hdrBJRdLIUorrN6TAJUaxv7P0nj5nsGY+EjtLhrdwdq5aPczUWGNYqf1Pr6+R1JqXGa++kbOu9jGrQ2mlHcRXs67Ivtq/'
        b'1r76vLmvpHcpsIEoip6yrRg25XDpaQGXji1N1hTfH0DE2VdiZmFFKK1aU1Kfa02x45N2G6W5rlhTT5oErGatcsmu/8NJ2vw9KxV5+Ps2KJ1pbnCGz4/hhvKcvB8up5uZ'
        b'XHSpk7fHsSP7DzATJy44hWV3JKeww5vPHQJfCuhJrsvTxQ3577/y4RA5dx5yVqVcWptA4Jf0uYgTRvfY8wHlNuiJ5eLNLLa5WoPK3ymaCxBCxTW8sy7YjKX7RTeMDnKR'
        b'NijGMuYx5+LZolNrWgqctrWOfsPLUzr5Dl2209TQrHhCmXWk+TiwVW23yZnvCwoPqLm8INAy99y5I2xfm8zRl7T/0qdr9JO3fnTjg0Mve7x8+f5/3AuR/8nVl47mRr++'
        b'62cv/crrZ9988YXM0vdywjqPv3td7ZduSwNXIhZjtKZuGdWPjpap7f/srz/uuBJqMhry6a1fxsVY/Ohi+p3lfwnid+9668K3jaQ59R1NlkaPta/JGtywF/o4f2dkUPj6'
        b'cgTYbCK6BfWpnB9P+8j1taiBTVgSsXDewfvx6k6arteGYj/emw3FqZyHXRmqPXkf+T6c4N3k1zXXnSj5t9TDGumtksox2Dr57f515He2YMvK6RO+ffCKDGeSOmvrU3Jm'
        b'/VvXS9n1QmeNlP1qFbtJhHL3K6yXo5wINabPMr+2CC3auVaEfv7UWMnarOhE5nH5HylwuVJ7b/DZdNOk0KjoNEkhJEmF3XWllzaQkWd4B0ZsJufxiI5LjA1nPpvwsB3P'
        b'laeSyTxdDog+/qLGK4INJZKUO99KZRanmTnGWOrpjKYbUOm4itJDdOSisSw++rvX/otfvOPyb7MT3f4vvP6N6coJx657RtIva4RGRVR9FhtiGhwfERXiKumQ1t8il6Cy'
        b'y0iKY29LrICuVebGfjnib+edHHvHZeJiTMRTMSyCxQ95/LcoNlxvFWBBCH+urB/KU9ix4bSt2ItTjLknsJR1leQ9NE6whGNu1yV3ucCwLCHJSRz5wnZtasH83q4QVTLH'
        b'pse+HptaMSZdLSu66lh96g3rz9uYrGfEDeqKmqw6fwn8C5oYb9l+Hd7KEfx23SHQLxonqz0h7e7uY+9uJHLn/1f7gpp8T4qDBLO/dDhJw35iieuc75qDWJyQ4GbDL8Xm'
        b'/21I/SVFdpIq/aiiKDkIJ6coJTIwWFtwT01NSaSvpq2oINTewiSxQLjnlobQPF5DaLCdS0CC4VNQvnogWsp89Ui0SLBvr3Sa39XUT+gNqpuhndR9tU0CtuxXg3yyEBc2'
        b'HT0COaE4JmONhclQAlVQLUf2WBve3a4MlZgH92EEas6ehS5FqIZioR4+JgjwWBmarHEaymEyGGZw0EeZZR3l4pjNCbJ2xh3hsQNdVYHFmWR5D8KI+U3odoXREzfJnu6X'
        b'xXEYoj+PDkMvdGNf5HXL3dh0AHOwMx7a8R4O4iS23LSh0fRhEUzoOFw/4aENJbsw58ytmIOEOJZgLvoE5l9z2LI9eIu9tYt0gOUNcw/oDtA3I7N25gQ8JANxCirjYYh1'
        b'1oBZR5i1ijPGCstALFXGvjAc1yRIcx+qsYv+LGB9EBningdjoCwUH8jQKs1ifgJMYBW2e5OVOJ4ehz3w+BYsYIMPVG3GrmuXsB56jm7CUUdY2A+lNPcqKFc/C2PekLvX'
        b'hQYwi83HYOwWDp+HJiHhjma8i7XQSv9WRMEANkNX+jaxIomgaeywNMVunI06pnACZ6AgVB9yHOLgXhg9tsENFo1C7RO222N5ND7GFmesC9CFBxl2OE9ypg3HbWSg8byR'
        b'L827BOogT2GPD07pYid20W9zblAArf60GHXQYIpzx07utjHU0sTJC/RB6429l0wIvA2paWIBGbQzPsn0aZWKwk5cpjuGcALGaDjjAmw4GH4cmy5DiyUsamCHSogblEem'
        b'nGRndRu2QUngETlchnl9TZiPhWU9yI+k20cSyYxuPKCPXWE7L1y0scAaooN56EsOJqqrx2Yfpc2Xs+KP38Bp/StbodkdujZfwjFanwYckKPJTBM9NWOXLZbKQcE5fLSf'
        b'trEehq1oliM0vjnI9acdqDA7ReRQnAGTOnpYzGpD4X2V22JcxCIHQ8fjqeUi5iKAoZvQ5mVHHNKyXwkWcWrTTVva3P5zkLMNWrHRTOkQjtL2TEC7+Bz0hQbvMoLKKCko'
        b'Mci2gN5jqVlRqlhHlNiFA7SwpYlBfrC0yR+abaEZJqAHcoOx1RgbTPbgPD6COTGMy2OtHs4GSydiG0z7BqSfwpZb3rEwjC20Dkv7aBJEHvgg3uU4PaJdH1rwjqc/Pbva'
        b'HxqOQiMUhBDf3RFZuWE1jJvRNZM4AEO3Lt3SVPPPDjnkEImt6pmH1PEBV5TiPlHfEtw9TDxV5LDd1TBzD1FaBTThyAGi8GGizHksDMbqWFikOZ3DBSiSxd6TWH0DOlJd'
        b'7KLxwV4s2EdWwvLNo+bZkH9V3hvmdbexUnHYr35MKgGXg3BShJUZ2sHn8B5MKUDpbUdoxDv6DlAeADmYF6YKHTDg4e1rGaqxZzMO2jkoaGmY75fWO+hL/NPmioXetLuN'
        b'OKQLhSRQcoKx7wht4wLcxTwxVrtDFU4YYKs7FvvjEExJqRPlFetAF02jkGRSXqAlW1koxBGYTs/YDGXboCMAiuAB0dRABpFDQZa6HLHDVATW4sObllpQQ8t4j7ZnnMTW'
        b'jFykijN2bIZRvH/xAg4T1+Xh3PYrsOTmAsvQL28I1ckkEPog3yocp+KwyB+WzLcwb91lD5jTI5IbxjIvqHZxVr+cjjP0vj6ihfZLcIcYaJlmdscShzX3ehtu8oA7tOYz'
        b'Adgby/LXPWDSCOeloTHEkPBGF0yk/oSRZCdHKW1eNlDBaJIG/tAEplOtsPWyFD34Pt6LD4b71xWJMRsOe5pCn1qQCwyehFKcpRVbxAY9dqCX5WzDJIw5Qf4l4te8nbjk'
        b'ePKkDTY6Q3eYmgLmEc320rvm4N4uaDZIIyJuEJ2ExUzBEXMnrLmWYkJbNwV9hIqK4RHxTjUxXUvIpSvxJD26TLElhpZ8QUDEVEzUOgTdUI+1l8+RVFw20fFLuXIV7rvR'
        b'CHuwEqf3EXdUndppmYGlWvLwcC3NEofUe26mccykY66ZfDZMx3MCs1Ylk3UOxz471yNZO0Jh3P3GTW3xVQco0YE7ETSxZXpAH0mm3CMniYIbZeOgDPoDoUaZ9njQQBlq'
        b'jmGTI9xPoUvuIJtJB7aTSuqHHFUR5tqQDOndJAtzx/CR7h6ihkl4ZImPtdKxO35TplRULOZAHe1DPtaq0kL10PT6cBGmPGk7u9SxOGBrFNFbLk7YQg8t+eLlvaSYRgMy'
        b'9Il+O+NssDKI1FeDEQymE0uUmtNWdNlZkpArIk4gtXn50LXDWLUvBgdunVbJogHmQg5RcxdMHTDYFxYMUyRw5pS0sAYfYa4SFtpDu6UP0QN0ZtIAirBiH8wQyQxDRRZ2'
        b'yeoZ0iIvYI99gAU8xlYFe2OacD5JyPtYCC1nYcoh0os2cgruJgfQdjaRNuyAhSwsSYPGK7LhWG8T4WDO6fMKlxRSNvmpJBUq6Zr6Ew46/tgALdegWJSmC61E3rSCRN7Q'
        b'fjGGRrlMxvzuBGd7LIpXxqpwP9mtV0ns9G3aAg2MuCyIqbvs1TXoiT8kyvaW2sREbTwHMBZxzARnhee2BcF9WWzyUhDChBfXHLYJG6EyBSYFJG4NN2HOAVrgRv0bOCoL'
        b'j6An3GEfNJ+BYU1SBs2b6fJyFWyVjdOPIaJpViVmbLQ0wse+5o7Qcv4G1upDqfO2o6QH5hRobR5jiawnDAYxXgkWJl5mUKgtHsdw4YofiQsmgEdIDhD8SDgCLZq2Jl4a'
        b'OBYAVUFn4e45eKSG9x2yL9HC3D96QxNKvV0DYHA3TmdvPRNEcmOI9mM4jlZlGFouZQqx3v4gPPTZf0PlDN6BFmg8GUpq+S5tcpeuOgvEYY8YltWx2ldHbQvpvWItqLzi'
        b'GuxDjLt08Lx1LLFwjT/UmEOuq5aFFg7EwogtsV5hDNTuwbtnhJgj7QmPwk5DnX00TJ10hwUoPG115tztLdhEtE+CsZfeVyCIIxXQhRMycJ+YoEibmGWSlqoCWy1hCUo3'
        b'E4+27oaFWzh7/STRbCMpunKsP3Edu+xInuSEnc+AfIcEov/7t6D+1iaiqpmwTByM1MVGEoGdJCSKj2OZn/oRJHKvxB4HQkVE0L0GR2kMbfRTt+3RDAc1Uopnt8CUN1Hh'
        b'HExnHqI7y3YQ4Bs6g6W0cnmk9TqObmOALAlKIwz2MmLEKq1TnDDoopHmQHs01IeoZ6W5YSu9aJoYqwGqo2lAgwQJckVQnsqS+jffoBm2kAodJs2Z7A+d5tiOPboeyt6k'
        b'LPpjtLEzHOucaIv7cOEytAXRKEdPwiixcaEV3EPG50tY70uPKLgalcbUEN6J24xTiSRfJjHP0P6iAo7rHbA/vzVAlFpBVH107ymiahY4XEEQJjgvjMNyQhA2x0xgbj+M'
        b'pynutZJNIvTaaH8Bq0/TPOC+HW3wEr12KokWaZYJIP+dkH8Qcw8EQxu9txjGE2/YKG1zYVZkCDsHQqPMg4bs7ZBjcoF2e17qGEnBenhofOQUDl8hfFaHD8MJW5aTChsi'
        b'BT2DJNNys82wVoOdcT59Be47Y72XLWnWynBbaPI1JsjRAwvW9LZyAiP3YVGVWLsNOtVw0BHKD2RgtYrb9sg4EnR3ZIk72m8oBML4buuzrro2ykRgI1CnYrZVihasTUHD'
        b'Cqe375ET2+PdHbSGObuJ6HvV9UjBl9MzH1zG3CtQawcklk6SDiTJRAABHwViK7Yfv07Sqg76SY/0EMYfpy0SeppdgJLd8aSjW2DEA3MvYtdlayh2NT0EJW60crlQdCZG'
        b'z8PhPEMxxVduQ1+IEd4NhRzNGwbYQMqq6hLOJhHl1J/H4SAsNNsPDSIisw5XLLAj4lomqf4g8grrrk2Su2izLq3ydBDWHMcC6Eg4Rqs/YAn5J4lmerDqQIBWxBErjxDo'
        b'CcL5hMsklu8fV1XYffCo1uaDRiTTp5WwSPOs+15Shcu7odWXnlqtTIT1OA6KvS4QqT+6DPf3QJ9WGE6w3oQtNNO2q+ygxaXwTSR9quGBOYwp0noWY0MkFG2HySuJV3VO'
        b'wVAsXfQAmiJIPjSJY2hUOd5E7tMHocIGlvaSsn2I97K18LEgFltMsP4wzqW+IeJ6Ftxl7OeFd+I5qlwiqszA4XAcyJQj1JOreYNW8M6erYRwp/X3a2CNGkFJP68sR6jM'
        b'3r77RirkB+t6Bip5kf7uZn8g9zCJ/noSJHSbDUNNN9WUYSSDNvcRdlw4pUi6chaWVYOwF5tiSNf2S2NOKtb5hMPSjXj6qiXkCg1qlMMOQNhhAZaiifynQnQxL2k79u4j'
        b'yugi5hn2iceqmwYECFoZ3I2iARRetY7TVaQ7qkh01NNylLgFENQbuuV9yy8qY6eSOxJi7cbenSS5+y+fzFCh1S0BxriVMB+feFIDZlVTiE/uJBGeqPR3PyhviOMh7ngX'
        b'6r3pklm4J4tDyuFYeJ51bKWPCxKhWZXMlHvQnoGTgUSs4xZKJs4knJqi1exjMk+S4dS1lZh0jERNid4+KVrLuv0ENit1tKA23mD7OeLWka340IGkVhnZJtOkjx/Fs9Jj'
        b'WH19N/btIst2CO/dguZ9ZiT85mXpZbnYd9Ah/GDGjssRxOd3iB9yU4kVmhWg+gCWXzuILa67WWNxTfXkEBJ+izh0EYeuEOP07CAKbD1KgGXuINQegAKcT4yH7hSywAvJ'
        b'UtbZr0XysuEUyfmp47to5JVRUEagQRoHfElbFhKt1py8hjO+mzFPCmpxLJxe3cbiw4Jd6TaJF5O1PWmLJ3Yas94RUBWWAq0nM6B4FxZJX8aSGGg6QddOwjRhzgYsukCK'
        b'ooSQSauWqwp0OO/J9iAaHcHRrIBYQooN3ifPHWWm2bAV9NolGV+GOaKqCjeYuBGtFUFSqEmVSHzaDLvP33TAGntjIopRnZ14x8I1xpeW7xE2GsnwVdnuE6ENuzhJ08vn'
        b'BEILARl4i1DBHShSpcHksbM/zBch4E//FGzhUke2wnCii4kI+g4JhLYCbFKBO3zGT6m+kouZjKWrQHiKPoahCyu134pJ9pVgiZBgTZFA6CzAFmMt7jjPPuyPxxJToQ5M'
        b'cwlS7dBlkeok5opMNQfSUtVgGXFHs60SrfzYbYXtl+Sh/riXarAm6aYqc6KJLlqrOobZ9+A9J3s3yI85qW1EAmcOezdnkYLqhHYnNbtLJMYroTUEKwi0EBtjxxHmdCHz'
        b'uyrDPPUMDGkzqHcLesODsUAROpOCiXdqYPkk5Pidxzp32k36njgy7xz92AP9rJpIga8G4bgWC9q0NsuLhkR+d7aSRTBhHEDPrRB40DvzwkmwjpESrqHdJjMn+ibkm5OC'
        b'rfKByj1kLEwSTVwkEFO1h9brAVRbka2UlxLoBo9dWAYZaYsSFtvWJ7spl8yZQiujm1BwkPUzJlExTmqBnT0kRDwATcfCj6WJsUI2XBUbHa/B4BGcTzLZjg+v4vBFp00w'
        b'KHszNdwtKZDkaBX0yDPXATTqb8Y7tLDDJJHukIzsu3yRnlVK61kfoBVDnPuQhlB5mKbaZ7NFwU8J20ODOOOrWYy5lmTJ5NCqPECSpsuWUCrG8QBjD0vM8yfJ1nkcx/cQ'
        b'6/QfNAF21mIQKo9z51JKICdJJ1WKNFRlMs2hB5bOXiJEWQPFxtAuiyPRWOkIdafwvi8ZVaVkvSzJbsKSoB2hRmf0cEQO6oKgLolYZclIJTWVVn4wNCkJ++hP9S1lGnHR'
        b'kQv+ZEk+IJFcdRAnzzjcVI8Ig5l9yjCrgh2OxF13j+IDCydi8EHIR+bfKVIlO34a7myB1kCSB1B/yvGi+6Ukv4s6hIoKSaM/1DmGtUkWB0lgTKaJSU70woiZNiynRuHw'
        b'UTIJKo01sVmHiXNSewX7s4lVZw4TaixiHikj9whSqzBnAS0pRFMFMHcJCuJJmffA0Fli4gcu2fAgkMy+dtrVB87WnBNmUUy6puNSJJlUvVBxVEfvtgnhz2l3Zk1gVQQs'
        b'YNd++msZlwy0oT482TRFl1DX8Emcv6qMd5RxUQjtV7MvsdmmDjBNRoRCJPSUh4bk6ehJA1vVNBzRltmSjp1hxB53QkhCT3hewmJnLW07MmCWoSGJVjNfUUv6YqCrFwmg'
        b'yoNbiHjqYWwz9h3QddlxAqZukFlQ4K/rYRZqJ0vKbf78Bc5VM+mxnV7SDDVHaE0WFWgOk/Ekm7pItyxF4WwqzBrBGJScMCHm6MPWePqlIu0QNJNyI0FVyYi1GyaMYXR/'
        b'AmH+dmucDLtE65zvdkGHIU4kgd3rJyTkt0hsfUefOGjCgXRdu5Q+9puQ/J3Cbs0LMLCT5Fs5tNgmuRLcbo8kBJpry2TsBNy5FUs4X8+WJFT3ZlXm33LF/iyNMwowFHeF'
        b'JGAp7wtIDiUeqLy2m4ZFig07b5MseKhPrNBGpi70u10VxGDB6VgSOq1XT0eSepjC1nAaYXUKqeNcuoOQObaFhsFYrOdRnNZRg8e7LhItNGphr505WxFjHNQJx4fRRDYM'
        b'7g+RCbGYhEtXpU+oYZPeAaz2SCShVqqJXRpkhtXcIECVA8vXCfRMn4JBdY99pw4akhK+j3UBctjpkECL3rJvb+o2o2htTwcNdbyvmZ1qrQz5p0XuXCumAaLOvtskCjpT'
        b'LzhCySUStHdNYF4rnBhzkdhi9pZfHOnMeCgX4wT9PkJo72FwGonbVpub/tgbYEZyqRmHjWDh9FV4sH23E4kFQnQi2sJJ2ofHJNyaWLkCdZrJEi7f9nSl5/Ychuq4TQ4e'
        b'9PpHerQkC2dg3o7EcEGg9M5TKWLP1NdEnL5oioQ2byxZtXH96P1l0HBoOzNzA7wUhTCjgYXuMCZjBg8uyWizbg07YPow0cGY1QVcgmLzaCui0CrOczK004wkGfPWNamb'
        b'Qh4JNiLRfBgnKwEfp3uYGdGGDePiSTsY1IcmVf0ttPylMB1G7Np96oQABjeTYBnaDU1WmLOD5N0kjPhjhy+0WAaQ3ClwgtawANIKYxcYUunCzoCkvdLiqBNYb4G9GVhk'
        b'DpO7fDA3fj/0xJwmzdBDE+4n/NpqTxIHHrpisSksQlcA6Y8WY+Lpe2Y7/KKw9+imi0n42J1Irp40SN4hLTnoiImHcWJq0pI47i5LnLCc6EEWfBVreAA97IAP6awt2GcB'
        b'damkVRrcY4imyIppMFWOhzwFA2t8YBWNjc7acfTGwVRssYJHdknYQOtXgeMXtsGyj+AY3lOWw2UxjTTfbRM8lGZekm4r6IvUdoT6c3pbrMgCK6Zp4YPjJM0XiTDGiBPm'
        b'iBqWrpMZOqJJC98UEsq4JyJqH0nWMtFlu8jrSjBzCftiPNyjI64SZp1UoSE0k9YdVsBJFygJhYYLJjpA1sZdLItRCsYRH6jQtA26cgPbnd22HsCq/TixNeoylh8UMQxL'
        b'ciiPLOoOXHTNuEmzLwlRIw3WiY+3Se2Gek0vzA/1d7h62s2euLzUBuuSj4Xhw50kk0ZpW0vITJQheIEjigH6nJBhoruWFrIx9BBM4MxOI+LeRuzOJKYrh/F9ZAqVqMuS'
        b'khxK9N9ELy0JwyXP67Q3ZUgYoVIeZjWOm5NUa8/UzFbdSxzWRCLnsSkWBkL70TjCKtPnUs+KWSViGE5YR9tk586KRTo4gFW2qknQoyUTs5ekbhtNZoJkYv0BobOPEzOk'
        b'QnE+FKdYkuIMzb3T9LgKVupf3CpFRN5MOryUwPxIFq123SEfeV8YPYLN/kTfzSS6HykyyxyG9X1pucnChnJtzPO2Z/BHkx72IHA79Frig3PGSJjGeSutUMlO6DDfTgxa'
        b'dwJaNtHStCST4ukPhwl/faL0ZpHXIT3o3mwFOewIGYFgG5KI232N9EhWVEdhrjxMhCdlk+7KhemAI6RVpsKZGC+RTfE8CINKR2mJK7BJN5AW6aEGdkVuwlG5fVl2J67r'
        b'QNtRGHO9SUTVS8qvB5s242yKMw5qENqpID26EEXaIEvhTBKtZDs9pHrnsRToOS51AB+cMoSBkwrYmoIjahFXdKFPXe061GzCUpdIetAdqDWVtXSj/SSwQcsyL2Xglmh7'
        b'1CsGR3eSbBgkFmoN2onL9iS8GqDNyc5GQHxRTExJOJxEVzXMKkZgwWFS0EShJWdgfIu8kITBXOBlkny9tCXz9NQ89U1+pMfLoFsO7kVBvhUOmpEKKLydBtXHLiPzlncJ'
        b'YOrqcT0SKY8gP3ovsVm/LnSaEY83EUeMk3XdGiS/+TAu6ECDzzGXRAfSoAMwgA+kWGEJmDLQsiLToxv67GBIWp84qRWWd2/aTHC2zBgrb2IlW5qidJgUJ+45Tp9WnYCu'
        b'vX74kFQl1qsbnjDE9mPQGO5PdFOI9UmkmpYyLuHYoRO+kBubQpKx1lxwBPqCM7RCQmjVY6NwAcpCYPw6AegqgnBltFoT1iRY8wyt2OFTLEiydomwISFQiMU3zGhxJ5WE'
        b'RHlDSgwc00Y2hSVn3IJ5D/q1G5pdyVLvgLFERxz1I7nbaUsDmMaFE5dOQsM+0ptkCDvY4LQzQZYxxbADhOUaA4g5lmVDCLDl7ITC3anSjJEaiUXqGCfdIYJmrLSECyYk'
        b'jhvp01krnNYlxOuPNQrRZ2DYEFvOWECVmJTcfWV2hY1aNBmPizciHR0JEeQ6+1oZYH5WAkGkJey3IwqYhA55XDwiG0uKZ1iInd74aPctyCEbsG6PvaqiN9aHcUG2B8zh'
        b'n30DauERc211w0MvmiYxSh/zHBHc7YU+R21syvTae9GCZleHQyfwTjaW44w+acfCy9DhS3hrxkwmKsFSF8YdFWhaI3RhmSWtbX4sccGSKt6/QjrxDo6Teik/gJV6sjTH'
        b'XnkzHL0ZRSgwPyQD7tmQZi6H+2Kc1JXHlgu69rpEMiP7pNW24vwpX6hUsZUjqfkIcxwI0QwzmXYYRwWkw+uwYr9KuCfkXXLZdywlRgGX1Pyy9pKAJ2x+Ms4TKhKxxtKb'
        b'7GsGRaesom4ShRTthXF1axfi4k4deKQAs/6ZscY4sJvk1hy2QN5VfJShgPnnvIkz8sg2GeCi3gUHHeHxDlrvhm3YpqQgjtDBkosx0VcCD2Kzi4rwnDbd+gCqZKBaXYeY'
        b'rgbmYpScTCxwdhvzhJL2zoHFLTDHQnn9+lvJ9CsNOWVDGL79EC1HJ4xuNYuHKtddxBrlZAElp0LTIdqGfCecOaFIKH6BwEHruSwd7FK6LU2TqLaHZk35m8R11fRbFSyb'
        b'xAdlQvsOEta5Gsc8YEYXWtWO2iil411nzNMPlMV+H6iOgnYYJjoq9wpgrlPsT2XOL9r6BZK/46QmcrHHHAtvB+4gPU0w6AJd2+ZOk7nrh7NZ5gTPoJd4poZUdaFiQEjq'
        b'ReLKDmDqhFBpzxGa2/ItqN2G1eEEvGeuE8E8SNcluhq+hQXZUESynBVL9Kc3k2Gb+i6DS00sbrrKCbbMTVXhR4qY5FjMKQMvVUOsJC7wM7xBX7dujgyV18WezccMaYuX'
        b'cTQSRmQdg+g1swSUekVHcFYPlrH/aIwizSkP76cAiwbfuXgCqqWgXpcE+mI6NrlAl5h+7INH4aRxBm6TfKwghqql3ahS2IbdziRPh2nxS7H6JqvBckILi47Aghl2Gbph'
        b'SSyLeTkxv1WYJy1P3h6SLEVKUjgUvoVofzrTgDj94QGPBCK6Hk1LGlv1fm2s37XdCFv2nCPMQPxxhji0n2a+pBWFM0rYfHwH9iqTEZl3GXLP4ENbGJbPIEFTQyCojoR0'
        b'NzsF/EgG2vQdoUGRbIXe/arQaXcAmg4SZMjT9dmEA7sOychg4fkzWKSId894koG8YE44q8AKJ1QTccZCycUSug5ijZ21LS3MFDRLEff3kNTPzwoyUGOHsx6SQHgIdwyI'
        b'5h8ICZ1lpx0gmqvxgjxFjjQeBpIgX762h8RCKxYk0Mr1MXEws5/2siYiCrqPEVFPc+WDi3Vw6ggZOFWRUCgDXVEGMCAFYyetcZaZ6phznqTYtGs66fXHB9kJim4o3Ye5'
        b'prQ4Y9rQdQsa1IlCCney6LL0TZkjkT705NoTKlhPEEImnQGhXM3D8WT3EbS/S5KiCvo0semsTgbLsvCmlWuGR1fTdsOQGSzaQ7eRNDTtIJDV4g+D18j2eQDdZoEEg0h9'
        b'H7FOOASPnPdex67d0OgMfSb7z+GUNDuY4bSD7Ns2nDxAmm6Q8UmTt8bZgwS1h81x2deQBFyDV5BK4C2fLQFEPIWYc9iV3tG4y2a77S0BgczCa0QIXduMRPzBoiVSlXdW'
        b'S9yU04z6hMaZ4fyxqGmL7GTMNVst0UZUN20k5txVYSKodjEVpuKCQHhMQHvUpcd9HhovcsFyAa3eA4FwvwBLA5L4klSt5lvZ+X5CVpsEwjN0RyIOcQ6u7E0w4OIkHYe5'
        b'vLPMIJDGxh7lscPExYNAXL9AaCngsiTyOPfWNVy4hSWu0pB/RCC0EmCFOT7kboiygxnmXIs34l1rMLpP0tGZxHN1EJYYSWelCYQe7CDO2GG+wk/jCTIkS9xkSIB0cR62'
        b'qquQyx3wCrXMcjERJWny7jiZbCMh9ygSLRX7XJylA88KhCYCWuBObOJXqzRFzPnjoD+Ed8fJ4JyR0J5rScSdRTukJxK86KUiYCXbrmbGCozE3Mf9UWLBTU+uO51ro7kt'
        b'X9RnKEAsyFFmme1BSpPOcgKWT2bPPY07uBatN/V3YfILJKm2ncm9VRPg8TNbrbyX0tLS5O7duxWIjz/+TOVKlF7UoNSrVcPa8oNmqj6iwaGq0bf6T34q/+ncXzJC8vIL'
        b'jKt/feP3f/t9a9P122m3j6f3v6nyUs716Fs2n/w8uG/TNZfXPvvblh2Byf+lnjb98cVNN6t6Th/qVbv0yeG/mz+weO81mV+Uf4IvDw5nnfnbqf96542zcODmpz5Xdrvf'
        b'lb8q63zi18a1fbV+v1DJnjQ/fTPfYudNe4uQV3c7zBZZ1v78pUWZxSoN44LZPGeft15aivmVv8cr+nUxP/Y00vm1yUjNwG7vgPdf2/HNR8Wpdb9/bdd/PBLt9YkJa3CW'
        b'UW71rPA2Dhjs1z69q3lg9ylWicnTy9LepjRiunL0pxdCvD7e9Vbx7Ge6b7xp89IfXdPd0uGjVJeOWpfdPx3x+c5A6cHvT5t+Z/ajn/pGOcgOqryUovT9xNfezEyqP+Tc'
        b'Mi0be8F+PqK9uUr6p4YPQ/26Na8YLtysHvnULrNXmJAY7uIc3mq18MMzfh7vFH94+82Ob7249H7omMdY2w8ud7/4ulvir72W0qS/b9xx/JVfVRilZEW/81bYDyqE7psT'
        b'XS360uPe/4ebhvwfVbXT9nf+1vc/tv3USWmni+WH39Ivkd95LuXP2dNXcnco1WxVeT0q8e36e43LS5XLgfnFXmMv5//m2oG75//YnfXxjuhPPt6fOPqz86XBrXMt37oU'
        b'Hd7vkBVe3RaQtmf/Kx93Kn080PDJd1rh0IeP7jd/w/Sh0vf8VV/W+H6Gyp8+ek3mxsF//fQnlT++vrT7X6a/szQNqsrUTm1PfCc+YvQ/4WjtcsFFr4qjEwN/mw4LK/F+'
        b'1R8s+00/89bz+r3WhfHiwyOh4pbXswqD9I6//s1tf7l+/0OU/dPO23+SLdD74L8/Pv7Lvq0ON7/zZtNrn1zK/dffI6PrshcO6/x47Afvhbn/8E+LL//pF0WR9jeuameW'
        b'd2R8b/o936r3PtX8/n+1/sv1V1o/nij+Wbbwk7f9DD1uGynwlZmZe3GJ2FqYzAQBiZTyA05cDrsIuxTXJbkmy/Ap7IG4yFUhIU3diM2KpCm6NzyrRkZAoSNfO+NOuJFi'
        b'krK8Mqn7EuzyU01KVSIdPScW6GdJybFcDb45XSeOGREcbVi5NB1n068rywh0bcWkHDptuZNVuLhLJzlNKQ4Hr6finCoUQ6mqnLICjqumSQuMVKRwJHUr14OHgMaQJ135'
        b'zGVQRg+Wglzu2W5SMvDwNJTyJV3GYYimvfo4OcgPxH6RBUnBR1xaLyywbKtkKJO7TiNMJq1XtO6pDqb8Q3FGBh7vd05hBSoN4Z7e02VUntRQIZjeIi2PEzHPdsQ5+H+b'
        b'bvp//peRPidz/3/5i290HhgYmxAcFhjI5V/30V8CE5FIJDwkNOAOmmmI5MRSQjmxjIj+iFWkNTQ05NW2qcmqyWgoaGlKibScdHceyRYcEgmtWSa2lBTda5AtMN2y5yz7'
        b'PfCIUI7P0Q49xP/kd5L/XVY3YIudmlhFrKFmni0wtOc/dREZiYxFJvS3icwB7ifuj5I0O9a2Zc3/SearWczipO+w6TzJ5bb8v9/q/zMSE/KLwWVVsyVifQqTGVQQvJa4'
        b'tomUAX0ChTgeQiZEBVawhmFQxCqTYa2sQGWzeCvUe0fr578tTNYXCgT1qXi47BVnsZ1a/nBkYM0rrvWvhGipv+l5wHz+RL7spycLg9JVdjTkvH3v1Kfan5TdVNsO7Wk9'
        b'Kj8PvDnj07XTafuf3fUmph9LvfRhRqhf/ffq7w/NqvTnm6cr2XzvcNxvTTpubRrvP23+3ZFduzZNDWukNb9Vuwu19+b/v+KuLSaKKwzP7uyVZVEQsd4tXmBZF+Smolal'
        b'CnTZC4hiL7aZLMMAo8vuOjubgtJaV0VxBWuxFzGl1DRKVSwgIDYa4zkx6UNr2oe+nLRpX5qYXuwlaZpqmvT8ZxY1fWvTxGzy7Z79z8yc2+z5/8183996d3bTV1+qUtV3'
        b'3vPf3hD6fzy/4PCy+2v+KJs+1jdU9LVZGajOii+Q1+9uKetIZH0T/75o1vjes1d/33Z/9NcN3ef2ncvZVFYn3v50+5KcnYkdnx1yXCm/I3L7M7I6hwvRE2kveke657f9'
        b'MpLg9lpGjvPzslF6T/rim1b/7s7oB5MbbW9PolLyyec37Urm5K35d7+o+FnafutOov632cPXJxbmdvxldPz0UpvY41jIGFDZKA45krtq0FU0VsPIsWbOhkb1eHB6O2NZ'
        b'vExd+RueGhceobVqalx6fALE4a7x6P3VOMGqRNC1Qm1CgKDP/s0ZxqN0QjL4BWVLWHLYGbGFHnfVCl+ez8yZDHqLHR3QNr7LvgacKDBxNAZO6LZyNOq4xmmbwCl0JN2J'
        b'e3Jdc5iq2zEdZ83X02jkMh5kDOMZ6Hr5XHxsSlPL4NfRfaMLvcv4vDuW4kPwUL2LWVfWGbk0fJT3h/ENdtmqrFTa4F7PQz44OrmMDQjvmKWd0efG3Q63wbSHy8C9PA03'
        b'+tFJjU0e3+r0VC/3z/SUFus4M35Db0IXmpNtXo3e8xQV00OZfpbRhvq5aU/ya8M4mUP3AD6yEyq4fcyOxtNpwy7xhbU5mjDVEPqomoaCJ3EC8tMd5znDFh3d7d4s17Ti'
        b'+tFEnR2ebcDdvuUcZyjUoYsCTmrQfYx60SQN9K47Xbgb2OytOjSZU8+6VarbANq8CS9c1ke7reARAzf3FQOKLy3RONmD+EN82uP2paBxUNHwwYjbHHoaw596njV+YzuO'
        b'R90+NFD6wJ7i1qNhI36NeSJOdBCdseHRaXg8irrwlQge240S0+wcPoz3c/MWG8xu1KON08GZ2YxhNB93OmEoQGqij7o6mfiMRm4/tORVHJ/3iCCcDp2mPoDqoMaybajP'
        b'g4Zy3XQxdLuYwBeTPaxxo+4Cv8th4qoqzB14YrbGHizCcRsexmO6ffgYp8MnOHy2pJzR722OPHha2upkJHVjh47G3qN4v5YHcIj6IANgdoGOtsYVwm8167k5MQPqhFTD'
        b'bMZsm8x0uI/SJXOhBHd59Zx1mZ4urSPoPLvELBq3veasdhUsWu5z5eu41Jl8Cu2ZlgJoMBdPeOi0ePLp4fTucZj8+CA3o5jH/egi7kpOS3Y+kKPG8aU8EB+GScGvA29j'
        b'EB3Xkm8M4D58wllt5NrwoM7D4Xdwb+ZUJp7cx//j/j9tEVmPwc94mEY5AntRmoUx2S3slclkyyxJXiVQuUCuDCTDMpIiYrQmH/r3tLCp1wqNKcWchTzCB6WQUks3NWJU'
        b'Y5GgRAxBOaoSQ6MsUqRRWojwUVUhxoZ2VYoSQ0M4HCS8HFKJsYm6SvRNCYSaJWKUQ5GYSnixRSF8WGkkpiY5qEq00BqIEH6PHCHGQFSUZcK3SG20Cj19ihyFLLiBkCgR'
        b'UyTWEJRFklqhMRR9gV304NSIIqmq3NQutLUGicUbFndVyrSR1obilVIIpKKIXY6GBVVuleiJWiPEUFm7uZLYIwElKgnUBKRskt4abixbpWXUEBrlZlkl5oAoShE1Suys'
        b'Y4Iapp5fqJnwz/m8xBZtkZtUQVKUsELssZDYEpBDUqMgtYnEKghRiQ6VIJC0UFgINzTFoiJLaUSsUwXanVgItKIeumHaeOcqFeCoVQNUAdQA1AH4ADYCPAOwEqAUwA+w'
        b'FqAI4CmA1QDlAGsAVgFsAnADFAAUAqwH8AKAkpmyDeBpgGKAdQAegEqAzQBlALUAJQArWBG4c1vgUz3AhgdMQFhI1gcu1Z8vPOJSMds9SxNdKZLYkk+mC0Lyc9LDvjcn'
        b'WV4UCYi7QCgMGKpgkxr9Dgvj9BGzIASCQUHQlixj/f0A35u0PKTKbfjm2Snf9x9ZqYllHZ33WFBaD6UoJAo16KmP8N9vnfpMpv73N4N3Y5I='
    ))))

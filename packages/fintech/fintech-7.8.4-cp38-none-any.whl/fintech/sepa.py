
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
        b'eJy0vQl8E8f1OL67OixfsjG2uUHcli3JxtxnsMHg28YHhzlk2SvbAtkyOgCDOW2QwRhz3yFAgECAcN8E0pk0pW2atvnm22+jpEeaJk2atE3TfPttaJv838ysZMkXkP7+'
        b'9sfrndnZeW9m3rz35s2btx9y7X5k8Dcd/hxT4CJyJVwlV8KLvCg0ciWCWXZcLspO8PZhotysaOCWKR2GhYJZKSoa+E28OcgsNPA8JyoLueAKbdDjpSGFafkpmmqb6LKa'
        b'NbYKjbPKrMmvc1bZajSzLDVOc3mVptZUvsxUaTaEhBRVWRzesqK5wlJjdmgqXDXlToutxqEx1YiacqvJ4YBcp02z0mZfpllpcVZpCAhDSPlIvzbEw18c/IWSdqyDi5tz'
        b'827BLXPL3Qq30h3kVrmD3SHuUHeYO9ytdke4I9093FHunu5od4w71t3L3dvdx93X3c/d3z3APdA9yK1xD3YPcQ91D3MPd49wj6yIoz2iWhvXJG/g1mpXh9THNXDzuJNC'
        b'IVevbeB4bl3cOu186D/aE7Lccv8u5uEvGf56EvTktJsLOW1ErlUF96fmyjjIq5qoKLW+11/PuYZB5vzCaPwqasDNeGte9hzchFvytLglozhfr+RGpsnxw3G4UStz9Yei'
        b'g/FL+HZWhgzf1mXo8Va8PUfBqfE2We5QdNYVCwXwDnRiDbofmpWhy1BwcjmPXsAbs10aeITc+Ay+nkDfysnALdoM+QB0mYvCe2Tobm/UohVc/UgNN/Qzs5JHQ4EsvCMv'
        b'Q5GPX+UiBssmV+LN9PlIvAe9Qgpk5NDnWWgHoPCKbFRKMtRAkMRuvGGJI6M3boUSAAxv57mQDAFdxpeTXMNJgUa0eXwovhoRi1rxDQfaim/V4uvLUXNEOMf1HyoPwufw'
        b'Ay3v6k3KHseX9EsH4ubsTLxdxsnwAx4d6YsvwGNCBP2xuyALXYyD3tiWhbejrXkEKdSSmIua8EW9VsnNTguqTwyTaktAB9EdfA2Qys5TcIp6PrQYn6pDL8PjGHhckIqa'
        b'EzKLbHpdjt7Ac2ExspDBwfCMtuoyupiZkI7O4ku6eLw1m7QqFO8U8CtrppTz7ebYaC8B7CX0GUid3H9Kn+44t9Yd705w69x6t8Gd6E5yj3InV4yWqJZvCgaqFYBqeR/V'
        b'CpRq+XWCRLWN7amWIN2vA9UaGdWKq5VcGMdFliaIOk1lNEczP5shEFLmpi+pCDuQVccyWxUqLpLjkl7LXW8Ne24yy7w7XsHBf81rWWW6uuBC7hxnDYHsX2j6yL+K4qZ/'
        b'Ubgk4Uvh5qilFU7eGgwP3k06xJdOKovgppcmv59cPeVrjmY/nP1lxMF87SAh/7f8N70/mqvmPJwrAR4MS0CnYPI0J86Ji8PbEtOBFNC5orjMHNyqM2ToM3N4riZizdDg'
        b'qTnjXTOhfDm6j046nPYVy10OfAtfxtfxVXwTX8E38LUIVViIOjgct44PRa2oCW1PThqTPG7U2NHoFros59CDhcH4Ir632JVOZtTDPGNWdmZuRk4Wbg1Bm2HqbsfbgOa3'
        b'4hZAJ04Xb9DqE9AldBZdKIAKruIDeBfeh3fi/XgP3juP43olhUelGgLIh/RpEPz1IiMxxsveZBUyaXiFJhjMtTIYXsE3vDI6vMI6mTS8VZ0xJXmH4ZXn2sm4W7In/kXm'
        b'mAh3m0snZ5kWvfaz713eeWX/YMWjl03zX7sd+ajXjIWvXd95Yv+JBgvvCCoPx6lndLE705NklaFc5rbwCaGfahXOfrRD1kbhw6Tx0A2tZL7KJ/LoCr6DLzj7wPOq4OgE'
        b'A/TSVnwXvajjOSXaIegJ73MS3gWjeGVNgj4uHZ8dqxfg4WFBbyhzknk7A11HlxP0uCUbn0S7Rik4ZQmPL1o19CHaCyzpBr7ZCzeno4scJ6zlZ6Gj+LKW9whxWq3MThrs'
        b'dxHg8jhmSoXdttpco6lgosrgMNeapnlkLotInjuUpNtmhPBRvF3pfUkr9wTXmKrNDhBrZo/cZK90eIKMRrurxmj0hBqN5VazqcZVazRqhTZwcE8mgZ2MqV1BLqQ+QocO'
        b'NYHxIFJQ8gIfQq+Uh4/HL6N7CdBWnhPQQeiuO/yM+ZZZ5UInVEIHdByhEoHSibxC7qMT2bPTCSGHkA500jPXFQ33Sa5+jmxoAT6H7pZx6CV0AT9wkZJleG9tFjzhtagF'
        b'vQL8v4ecvlAXhI/ia8BoeQWPbnLoxmR8lLZwMroKnL+ZPElbgBo4mBN78W36Tn8HPhcKUo3vgXaWcugeuoDu0AcafEBMIA/moC1LOHwEX0cbKXR8aBrQhkHJ8QtXDeBA'
        b'QF4ZxvIb8K5EvGcO3K5GDwu4nAEqVxTpNnkw3gNjgF7CB3ScDrmrtcH0hWTUNHgydHIsPoE3c3gzuhZNIQOxtqKHa+BJDD6ET3P4tDGTPrBmTkb3oKZUvAkf4GByX0at'
        b'Emh0QcDkUf4wfIvDt4Y7qHzJGAfNuQedjPeiXfh5Dj+Prg2lb5jx4RRMnlSgTSBw8asTeQrCUqNC9yIA2dPApY6DNLSjbQzEHXRjDn4RkELbo0O50GR82gXluMXlRYVQ'
        b'jRNtHsmNzCyiZYuABV3Ge4Be0JZVSVySEt2jw1CJNocCIzpAHrTim304Iz6EztBHpfiSiK858LUVNXlAhvgsP0yHHlB2EcCtBH/G0pfUydVziyPX8vV8EyiQdnk9v0tY'
        b'LieKEp1C9HJO8AiGJA9ffo5vm5F0bnhCplgtDme5rbp22nzvNFQCFBXnmgq3A9DW9CyqmSxCd5ic16dDZ14DlrI1Lxdv16KbsuRk1JyFdgP6ofgCh+7ju6HoMmoutjy4'
        b'lC93uKGa2PsrhrdMjkJJkTNWfhQZpXph07XaTXudJxpzZ8xQXF+RVjH/NxvRA+3yT4a92mcqPj8qLHX4J/OXf+9w1jjrncc3U8IykkZdnXlwWt5wx/NjNz3/wZKfNl89'
        b'Mm7mlB1Loq5+ZZ+6KHLM8fxLA0dPPZK1o9+RfrfOPX6Uc+fDdUf/9er9G//6prrh+ocRp94aaWsaDVyTcPmR+G5JgkFrV+JtOmgtkM5o1IKfZxz1SgLekpCpx00Z2bl9'
        b'hyu4UHRFwM/je2gvfRddrs7AzbqMpaNwC6iLyiXCUHwEbXIOhmep6AB+kQpGvA2UMLwVXchUcD3HyPCmSLx7NdpBIeD9ISCxJIYdinZ4efYJfKMD69TK2/PSdsMXaq4p'
        b't4lmI2GmlI2OIESSLuflvIoXOPrLC98oZSrICYE8tRDJq/kwvjdvj/Rjs7zDE1JjMzpgSVBldtiJ+LcTvtQRI8FO5rS9h4+7kmoyfNz1TpQ/dyW9gjc70IYsSbtlBCTn'
        b'+uLdcrypeCU+j1qfwGepNA7gs0+Wx50uEjrK42CmbhnG9+RgXaD5F1c6ZcCc/kyJKq/K4HZyXO3gstLMM3FZ3Cya+01xD07DcROurSjV1Yy0sKIF/UI44B3pe/qWZjvG'
        b'TeYo60GvJBlHJ4EGswH0dbQHePY9tNvyjvtXCscCePyjfyo+K/1jaVVFtunNirj9n2y4fOjqgm1iwcGGPpN6xybpxE/ET0p1ybKrfSb37pUcG/HhkRSxYH5B75JDw1J0'
        b'W6LnRmYdJfrBHaUoLBxXCJpBX27oL2I2/NCpFajkxxdAL3gIEvwkuhmX7pXuyXiPcwB5emssPp9gyNCtQ7fjtQbQ2/BWjuutkS/Bh/po+aejvR7lVebyZcZyu1m0OG12'
        b'oyTIKRmU9KYUqIYrUFpPP0qTlVtET1C5zVXjtNd1T2iEH9tjfIRGalnog/BSAKGRNSo+GTMeiCw9B++sg2XZjjwDaKRboWWJCOYaCPep6IgSn5mOzndYPvgojup/PNBc'
        b'm/7HU3p7RvWeIDy8A70NYfQ2P6kntz0yD+5KpzSprBJpvauP5G7XpwDJler2FYdzRTT32moFV5oDc2x6afbifqWM4DaslnEHy8ldadg17QiW+Y0tnBtWMgpEYGmYbLGd'
        b'ZX7bI4Y73jOfvD7lf9bUssygtf25KYkuUnLR8ZRRLPO+bDB3fU0DAd9/3mANywwXh3FTEg6Q14ecXJPPMo/P1HIb4o4D8NIhKf0iWeZbqXru7NAbpM4hFbOTWOa6EUou'
        b'bhaojJrS7MNjqlnmD6eEcAcnasnyRtfDKLLMn68ZwT1aeJSUTN21pgfLdC6P525PfIWUTP3V4hqWeWVyb+5RvEig9/908XKW+ddJwdyY+JEkU2exLGaZNQkR3P3hz4Ee'
        b'VWqdvK63hNLyvtzvF1lJnVOyFkSwzBvJg7i4zPWk5KIhPWQsc3HpUE4c3kw6ucwxaRDLtFtjuTF9lhA8p/TMSmCZfYoTuXe0D8nrqYNlWSyT7z+We2fNL0jXRT3sG8sy'
        b'+yYmcxvER6TOqH8815dlvrMwiZu+8nXS86n3ooI57TAX4a7peHs8WdaOmo63caPw9iSmhuyFFVTTaCCpZPzAACrUQx0tjRpWzxwNU2x0FYjg0WhTKs1VIzd+fjTI9DHV'
        b'KdwYdLGMlb1gLB8NU2BsGTrBjcU3RFrzGHwb3xoNhDsOvwzcYJwVFESi4MyPKR4Nc2R8/1Ju/Gh83EX5/Vh8fTRMmgkTC7gJPLpBq51Q3A9dg/8T0TF0gZtoGM0QvjS9'
        b'EF0DfCchYEhwPbKEaoX4kH0hmRmp+AZ6gUs14Y20kgq8ZagD2jEjHDVxMxag52nuzAH4EFFNZqrRPm5mFTrFqr64cpID2pGGrwDANLwBN1DsqvDBxQ5oyKy5o7hZM/Fl'
        b'yo9xC3oRveKAlswGJfc4NxtfAuWYYKKdje47oDHpaAPeDlf3KJrdD+22Y9KejDG4gcvAF8Mo0LG4EYOqA5hnWtEuLtOOr1CgU5ON+BognmVEm7ismBrWyCPo8HB8DTDP'
        b'Fudz2SvRXknxbczH1wDzHLwPXeJyStFZWlwAdXcLvgao59YmcLloxwBWy8bFhfgaYJ6Hr6EHXF5wfzaM96NH4muAeP5qGMf82SuY8nwDlm6bia1uDmjsp7k5QbiJFp+I'
        b'zqNjoYB3QfBiriAZ3aZ1o4fBUaGAdmEeauYK8RkYYFJ4jgpvCgW0i/Cri0GdPRVP2zhlQHooYF2sxXu5YvyggNXQiDbLQgHnuXg3DMPcpatpdhXag8+HAtLz8NZ53LxR'
        b'6CJry0G8b3ooID0f7czl5uNrw9lQ3lyAmxCZbAtgdC5zCxabWP4WQGkTaga0S2ThXAm+PJ3ip0W7F6JmwHvhqgncQry9xPqPb7/99tJYBfcPRy/KLONHSXwxutd4bljI'
        b'L8mUjfqsZxxnOfbnP8kcP4cnWT/9bXXr5FxZSuTM85XKhvDef1s4f9qK38l2Ludrppfu1KwZcqXx9d+pfjIz9u2dy7lNv5q8eWytZkeK6sMNquJ3LjW8fGDxzdMmx2+2'
        b'1/7Pj7Z8cemVuedzf1qYarroWj36F59c2VHZME027t2yfxrHie4e9z6/8lP+jcExs/sXOpC28uj67D2fDF9j+mBuy4dv376e8Cvj+3d+v7t1h+n0x6NL5n724l+2Z5zO'
        b'Gr5mdWtszNp/r9yXF7Jg1Dvmb2//4tJP/if7+5VnfhBf1ePjho/fK7Lf+934+Ip/uwf97sKkscNHSlaBOWjfNNBRc4nRrBVW/aHofA46LeBXJhRTHXZcipGs+vUCuou3'
        b'MMUAbUcvUs1gHd4QBMoarIZz9PhSSCaxakbh2zLsNuKLzGqwZaEd1NftWRmw9h+0mFNOEPrETXZq4FGvReiWA11Mz9XHQYnrxPKJW2VcD7xTBguCvcu0ik5VCnln8t9P'
        b'0VBLioar3EiUXaplWImUFcN4OeizoGkIkq7r/8t/h7x/KZVy0Cd6Q43RMjVoMJGgNZP/9lgvTloZ6DCu8u5UF97ey4s8fU/kvFrLsQDjA1HW6/G2Qqa1gMoyGB3IM+SA'
        b'6kItvZwWb1CgPWgLvvoEjYWYOzk/jYV/osbylBpyENNY8mPDORDjca+tq9B9IsyWNJbChVTvVf1Mt0x3bM48jk7wsnWDQe0FlspRrRe1LrPg128rHDPg2QZDzmelJa9d'
        b'3nliz7mGEw3nDo3aPOrIifQhm7W9H2WZck1V5t3yK70LDqbolm8p2aJ+o6/y+KT91uN93xpTHMP99G/hx8KmaHlKwnhjWoIJPWBkzEiYmMm9qms3xNSXEZPDaXeVO12g'
        b'uxrt5gqzHdZRjLDCSGes5wQVLJKo8trbb+DlDijc/cj38Y08eXGTb+Q3BIw8Eex412R8DYYevYg3sOFPNGjjcwxafWYO2pqYmZOlz4RlU66CQ7vQthC8cdbgJ5JBoOL6'
        b'ZDLooLh6Kw4kA2UulaGj0TZ0JtQOK4vDxKYCa/1DVQIlhVRxDFcFfDc5vdTeM2M4N8uyO+153jEeHm2b2vpZ6SI66FcalvPlIR+mvjHkjvqM+o2KN6LPWPcPOR39cWnq'
        b'm1vUysjnDm4EVUO9I1SrXgvrGNKB6eg2yK1z+ETAUL88ny1jHuDd0xIMafjFDF3gMgZdDZXGrGtK6N1u/RJIByGMDoJVfCzQgb2vPxWUP5EK+vmogLy4lVQYSamA+7oD'
        b'HaTg83injwX4r1oS0V2lHxnUoXPBuAnvRQ+fuGSWtTNNfkcTdmeUwNTo4RHD0mQTqG7dSy5p9neUCkMSx9Yqz6mXscwleULyfoGtVcaGJ3CWa68eFhxZkD4/pP6z0s9L'
        b'H5VVVVwwf1J61vSoIjH5k9L5r93eORj4Av+oIvXnmabdpZ+IwttvatadWBw0I8gRUjj6xQkzRs4YnJ8Hi14ll18QuezdzRKx4Bv4KH4enc/O0QmcPIsPRy+gq33wHUos'
        b'+nx8CqQi3hGzKDEvB7fkZqALcq5XgXxcNtr0tGve8BrzKqdRdJmNosnJCCWSEUpkCB8NckIFo6rm7f195CL3yElRT7DVbBLhrbonWFcIqvaBPvIhFbX6kc/fApa9QyBP'
        b'ge7hzbiZbMqhrXnaHNSSl6EbNAvEx3B8VVGCDiWUy/yGVeFPLZMYtcjpjpnCraxQShQjo8ZsOVCMzEcxckoxsnVyiWIqO1v0KjtQjIJRzDBY+hA5mFSXopqsX8SIY5WF'
        b'7VQljdjnuGeScZY5bybxjjJ4cu/0HwZsvxK+ISlM/psVBUkpv/ih+vpebaTzb+PmZN7LLL+pOlI25/kl6ye9tLmX8vsnNRNXD/i8aszXpeU9e320aXb0gbPv35k3/Kct'
        b'I/d9MfvL6IUjgr7dUvntwz6KrMMrrH8ImlrcZ8D0N0BZIrI5cngZbkbn4nFzYhAnoJN8MdqKbjMbylGYawfadnYPoaNAUBfwWaplTbTh1ix0Cx8js7UZt+TxnApvF1Bj'
        b'lY6KqMWZxBSImxKBa8lz+FXw6kN8fhXbQbmBzxEjYA+0OQd0ZoDbyM/Gp0K7U5CUXT5qT6RhleZ2NNqX0WgfoE9BTvWZED5MEASVEPUvudI+yEetCkKtQKKEAD3KcpfT'
        b'VuHP6TqdHkDFxM5n1wRSLqn0kB/lfhrrT7lDSf8eRC8My8rTt5EtdPQgdBLvRBflsHQ6jXZ1LfAmcJLeQ7Z5uQrFMwi9DoQbDn8xHQh3ECPchbk/5vbC2F4Wxyy6ODmT'
        b'Ee6fFRri1zEhSf128O7kVSxzAR9MN2OTxt2aendwT5YZvCiUKklJIy71VS5YzTJXyKnFkUta1zRyzSSBZVZP789Bq+KSDD/o/6MRoSwzsXosEayapGD97E1hIdK0GRhE'
        b'94eTYt+t+9O6KSxz4jgtl0+gm95M1o6QuO/4iOe4ehCJSRNXOZUx8SxzbukUbhUBpG1U/NBQyDKrZk/inATP4C/nvT8+TTKC9ujDJZE6a16p0PES8vVrddx88jq/siBy'
        b'qoNlTlnKDKNJs+rGndNK0KdZp8PAQ2bdz5b8e1myZKdaIs35FbsG9VoiWXW+LQ6jCmZS7PvV/7VwlrSPPbofN4agtITLiMjNZpmT88dzxHyTtOA3Sz5IKJA6ZPoc7jgB'
        b'NDZ+EB4znmWG9hG5RwSQ7C3dxkSVZGwZUsm9SV6X9RvypzWVLPNv/WM5Hclcpxs2f80Clrl1ZQTXn3TdiP5Jzudms8zvq1ZzXxGUskYvHj1Hsv8uXiCxtuBj0266JJTO'
        b'Bw+lm45Jc7ZFT49fw1l+Gf0jzjEc6HlP0p7iXTkFOCls80e//Hr573afaRwxtv/mhV+F9J0vbulzdf+8dw8ubv3Zog17atVvbbS+H2b9/V++zvjyyOuVS/S/m1H30feL'
        b'3nyx15Lnfxu25MTl33Kj98qnHu/P7VO8UveOotBikg8IHXn58W/wyvsx/9vj6Mycq0FRn79zIUZr1dWOvTLuxJFhf9b9NOK39vtDx3Ifvam4eTTz3w8y+9iqWk0rt+pj'
        b'inaMX3zl5dvGPW/8+9THtkFvnz8+a/6p87/Jvr/rVMO290230l9+9fWlPY4e3/G+/ujox+7fzr77A/uL034ypfFB+g9atlSvmHloxKQpp4Pv3ZlY8cMBy1+o+r8/3PhB'
        b'yy/XTr09wjVl+YoZH4ckrP9DxpLX/5X28f53DzWv+vbUx/GPLqRyhTdTJ+Bv6z/+W9jjj4JWbLecT8vSyqjQLgtFL1OhzUT2CHzKJ7UXL2bbKS/jBnQapP7ZLF1cOihK'
        b'MFXReaEO749gGzbn08YmwPvxPCd3oVtoH4+3og1qbfgT2OmTL90wa38rOWHGZaaaZcYqm9VCmCvlyHMZR56okgFPhr9hVHuI5DV0byaSahJRQpg8BDg1ME32K2v3n939'
        b'Qd4/DHg6rFSBn8NKdYiPm4OqWmc22f0YeDfyhbcP9fFuUsUrfrz7nWh/3k18QCZPwBco68a7+uZlwjq/Ge3AraCdtuKt2TBGOiU3FV9R4tupkR3WFwrpv6MCLmbiEMeV'
        b'CGIotbsLsHwRRFljcInMLBfloqKRa+BLFHCvlO6VcB8k3QfBvUq6V5nlRB5UCGKwGNKogpxgN+jGJSFUuQ3zBKWIot3scOSWK/1wUUl/lPVPIzKFuQz5XIgqVJJkUTap'
        b'QLIEgWRR+iRLEJUsynVBXa2qicjquKpW5DLj1lnZ3ELyfws6OJgbjDbgPcw/JLPfA8HhgrvX7+oGbLvSAyVFyr/N2y++1Pj6zOgUxVtxr21VqqZu+iJm16I+BS/dz/j7'
        b'xydKVvxdm3Pwjz889U91san+ha2rEzz7lj+Mjvznjd9uPJHT+tb18kcPf+Jy9TzY+n+H4sKMXz0qTf7Zaz+8PBwd6vP86D2OUe+b6/7NPbo8aPzqNG0IW2LvHVKVpcMb'
        b'evjPqrgMZ1+KcRj1n/M5nUxAx8keZqOJvloxCzckGLR4mw658TZpi3WO00mU2VJYPW4BZRVtQqfjMljN+J6Atqah82zCHkInsxMM+nT9HLreOyUk4YvojpPoE6CAbYA1'
        b'aDNqBd1LPwqW/K2oNYgLjRWweyzoZYRlrJmGb6HmPJjyz6GruCVBi16WcxHBMiduQq8y7et+HxctoUPn5uEmOadUCX0E9NBJlBfcXDQRNSeC3mbIwDvy0Ks8tYCdluGN'
        b'NnyLth65R6DtUMagzQwbmqMnbmnNAr5lRsc6KvSqp2YpbSwjyGisMa80GimjGMgYxVq5tIEbSzfViJ+MUvpdHSFRtkF6j01+lUdWbnXQ/TNYsVqcdR5VrY1s9Ytmj9Lh'
        b'tJvNTk+Yq6bNENLdukRpJx6hdmKwYjtyxBfQriWXeB/XIBte//LjGlv6+nGNDlgGqHa89Eemg4MqGdxSpqrxued4j8oobRjCvdxhtvr5NrAuU02xmqrLRNO0cKjlb6TG'
        b'1ZFeeN5HTwWwEQBqeY/CSHrMrvdB8YGyJ8JFDa/aQTHinroRUGew0dv/XdYb8Uz1VrF6g4xsNLusNbLTWgO0aeJAS8xHwD3/Q+ORwLXndrJcy9cRH3AOsqQaOfvPn5V+'
        b'cuh86Zuw6g+r+G12ENfzrwL+zSyvXe92LnrVOzfJxLQUCn1qejGKFjqdLeEWh581r82XbD38xq6O8VJBQCnmFSOzG0gtbWTvD0Dv60JiWouCnnNEMbLewH2h9ifszkEA'
        b'kyc/2lAgXiNxYjMaPSFGI/PIhvswo3G5y2RlT+jUgflpt9Wa7UB3dIrRGdc2z8bQxhKnN5PDUW62Wr0Tvf1kPUdIjRWDIrQJZK3xf6RnyA6RSkGp6duoHmE8/RVAplOu'
        b'ftiCtjmyM7SZeoOSC1kq4Dv4RexejW93GOVQ6b9jO+8nwvkS2V7Z3oi9kfAXvjfCIlQIcCf9ikKLUtQREe/njRsJ4pUI+WAQ13KzAoR8UCMHIj24RQBBrxBDaDqUpoMg'
        b'HUbT4TStgrSapiNoOhjSkTTdg6ZDIB1F0z1pOhTS0TQdQ9NhkI6l6V40HQ6YhcAE6C32aVSVqElLRKJO9G3hKc5hoJr0E/tT1SIC3h1A3jVHiAPhbVlJJG15hDioRRD1'
        b'kjVFJmrEwbRtPaD8EAprKIUVBelhND2cpnuyt/cG7VVVyPbKxREtMtFAlRDmXU96S+2OqAgW40QtrTEaaoinNSTQGmJEGWUJiaDolFNu+XhkiMbvR8plbv8BT7RKj9wC'
        b'KqpHTqixM+LLLQ/yG3wyYdTeaZ5JOAfTmIJJB0oD63W/VleoJY4SRPUnFXCUIB9HUVGOErROBRxFRvUn+QdfA1EHoEd+MmosTovJallNzitUmTUmqTEWkF+mmnJy4KH9'
        b'K5NqTXZTtYY0bJImzQJv2emrGakpuRqbXWPSJOudrlqrGSqhDyps9mqNraJDReTHzN6PIy/rNKkZM7SkiriUGTPyinOLjLnFOalpBfAgJTfLOCNvZprW0Gk1RQDGanI6'
        b'oaqVFqtVU2bWlNtqVsCcN4vkHAZBo9xmB25Sa6sRLTWVndZCW2ByOW3VJqel3GS11hk0KTUs2+LQULM21Aft0ayAPhNBknVER+oeMuKTKF7kznuqxNu9sGQBadXly5JQ'
        b'Zu9LCeijwjz96FHjxmlSsvPTUzTJ2na1dtomBkkTZ6slB1RM1k460AsUmiNBhLvOMX6aerzCmNXlTX33+pgQZrWx++9QVwcLfEd7alguPdMRn44uE7OjzkDOfGSBHptF'
        b'T6dA6sQgdFKO7g/FW6glQjC1Rk/gJwhcUqmhMW4J5yKmswx0GG/EzTnoQj5uImp4It4Kd3mFrJ7idLKNm5OTsRI35vAc2oZPBuObw/A1WqN1tTLVIKN+PWGPBo9gpwKS'
        b'8f4VZF84IYu4PmbPSQcNXFK/8W4tOsdVJxamBOEDyWgfreSjiULuNbYxoLPlzGdWkwHj5bHvC3QLQbehz1TORSQ0fgWW7LfRi8/5V4+byAEVQDexIB1vy1Zys/FpJb6i'
        b'mMW8727jg3mO5QrOkM3hVoL/bnzHsr38v2WOn8Fj04jhw1sn16SOikz7wd/vt37dOPPk4ITSPp9vHFfQN2HbppmmuJyGI/9csfPLO6YBC0peyXHMmray/vTGhp9WfPnF'
        b'gT8Vb/rhxzVJRb0+z/jw2FtjKz/c+Ou3P/vh92Vr563deeS4u6zlrz+u6NdzzFeTD+XsWpU2fuED9/NTqq/sOTb7k6CR3744+9PPt2X/SL95xJkDxr/vuDE+o37Yua9z'
        b'3vrL+59vShzxzYl/fprwB74k+0+vfenITv1SaeezDDPGnn/D9WHWh0r0/saVu5vfKB535+b9my23NLP/+ptv/7AvMy7pf7VRdP99Hr6HDodCB2lzXPp4vC1R4PAmfDwG'
        b'ueUqvB+9SA0mmXjnGn/vADu+GApLO/xKZQj1YkUn8AV8LcuQmaPLQC24lZ0DQjtkfdF1eQ26W8IUtU0OdIieHbiGjnv35epLnNSuexNIs8m3o+Wtwtg3BjfK8G10BDfS'
        b'pSB6Yewy4oTYtnU3H+0ku3dFaKuT6F86dKYKxhxqSMDkoJG0S5oFbdvBXAtGTJiNrgSh1iq0mzauGt/FLzGTMiWKsuGhcwQofBHdZjuGm9EGBWqmKO1BxwhaCnyYh7du'
        b'4xa2OHTr8aUJNUQHJRXI8BEemrB3Kd0RQFeWDiRvQxenoZsw2xT4rsCjzXWsPZvW2NnKkzhQ7EYPfEvPlBonEaMDgI4P4E3DyPqyRUsPhrE+ZlM3AV1T4M2AyXWvZes6'
        b'uo721tE6s3nA5QUe7US78C6GzLaqOVB4Ezw25BBMb/KIeOlfo29X9UWnCKo5xFMDb5UT27q6UjZJj++xvbKXFhvhTaLtDcN7iMKnniGbNXgebQnevqCAvKyD3s7F29HL'
        b'xGdXjc7KZq5Re7fK1P+xAa29Jg+KsgXkvLTwTfcq8aNU1Jc0TFBRu5icVwthfKxALGRhPPNrJl4ayna/AvzSu38plbAYZDzY4AWRy3TnYLYEeI5cpnPexW07zbttgfDU'
        b'q3ltEKskJrB2WqfBVzHVzVPhMihgefHhCP/lRQfUn2XhrDAS/afLleF878qwDYp3tfx4eJFPWSJiDBQLrxyLs5tNot5WY63TGgCGTLSVP/V6lSzgjWWW8i5RWuhF6fEw'
        b'ggCoWt3CfxbACroO6xLyEh/khO71oWdHgFgV7ERIdgnc5ANu8Fem/hP4IRL8pbzXriHAFDOxxSojz66wEQO7ojtF69lRqaCo2PN8E6IrLCp9WCQ+jYr2XTuFYaLtDpOl'
        b'Pkz0T1bvnpU42FRlWHSFQLUPgaQiumYB2P62O400rBorPejdJQ7/mdFHRrGVPz7ZQW+dQdYcDo2l3Ux1mM3V9IA5LHToUqTDi+TQubT+KoT1DrQszWW3afJNddXmGqdD'
        b'kwIt6agmx0FzodHw4opxhmRDkrZ7RZr8KLiOVvgi6RjyPHTXmUDPpcino13refQyvhdk2a/7k0D76LX/k31W+mZZ+r/vmx59HFfwSemjss8hLZR9HP1G9JklH6vfWKXU'
        b'tA6mzkuvvxQ8tmG7Vk5l8BoD2iCJUXRrKDv5QqXopNVUX5s7moh+r5q0rdarKTE9SV/NTiS9iu6hQ37nsXEL2sGTowzXnMScgxoW2LKoriIsGY628ol4f1B39rIgYqby'
        b'HheSvJzWcytC+Fhio5WkgFSGSUn72Pa1tRnHyD5WbYD02q0OtPoG1gjaw3Qo+AQHJmI94Nz8UzswMdOH/LG7Ax0Ump3MYuCyOi2wXpb4usshLZBpSAWn3VTjMPmFRiir'
        b'61ARqWMStZ1MKs2BMlAV/DNVmu2lT1jGkZ+OVlHJLabPstYViWxxpjaXi5yLtL8O70/qZm3mwge8y7O2tVnhesvhiD8L1C9i4XuvfFaaCcSqK/i09JPSpRWfi38slf9c'
        b'u/1dXVr88I9eDdNOX9Ez/1TDxGOjNhOyDefiPw898PnPtQLbZdlfhff7LyPQdnRD4OgyogAfdBLRgY70qOhUjQWt9UWvKluqkHygnrRH6jA7jd4BokLa37OK/PJebW91'
        b'Hy9BdXgn1wuMKliEyrr3tKIlDD5KJscfVwdQcpO/r1U3gJ9FIVMHvtolw98SKHGelnoN3mNTZI3Wtd8XdZ6hjjPExuhznnmS15fE/z+AtUhHE51vptnslkpLjckJ+FnE'
        b'roRkjXmlxL5HGUZ1Ygjp2vojMhMLbbrXdxMAGTQF5uUui13qGRHuyp0a0VxmcTo6tTiReQ4YOGzVXnXLApLTZHXYaAWsata5FWa7o2t7lKucYTQjNQNksmW5i9QHakoc'
        b'kb8auxcrgJXhNBGJ/GR20dHvUpVLz+OCNLmGbmTlkg133JxYj2/NicvVz0n3OY0W4KbsOemyAi06l6FZUma3r7MsCeZSKyOqZ4S4yBYCegGfRvdxM9pb4WeraXufQ1fx'
        b'vmKAs49fjm+o5oHo2kFPKC9GN/AGfI2ctQnjyeY1h46tVbpS4FEsOq12oD1ok9o1N524rhfjJt1c6gzQjM4VpesImO0Z2XgbD9zqlHYV2j8MnykSOLwP3QrLN1hdOspS'
        b'0BGZv4mnFqoj7pysyvx5+rlBXP56JTrles7y6cpTnKMG3hq+7h39m/eIo2DanPXIxs8yRfbe8MZJYLAm4e0pNzfkXBFazF9/0rfsuuufGy6//etB1qNfi4/0EYuFTber'
        b'9o/p/z35l/a3C5fri53n/+z56oMxd90/zTz/hd6xbd2l4+v/8JuPlX+8Nvbw2YVLFr6h2feeVhvMdoDPDUYPgUPjl4PI8pqsrUNrBHwkvZ6aUCYNwttD40FOu8ew8C9e'
        b'a8wgdE2OL02aRwX3AnywR5tXc+o4Qb8whNV+EB2wgF4wd6nXgMaFRcpiXMhN2TPegy6N9GPP+GZSosSd0TXcSFf3IfhMGm4eBL3oF8UFba9ldopTETPb7C7Th/icph+g'
        b'V1gBN9oH2Dejh+iov+kB2nKaWn+yMxxAIQ/RYT/LwxJ0XvIhfCq3GMJF2ziF9/DokDaW31MFi3fG9sMk5s9Syna8OKCWXC8OlLH7WGF3kkDmV6xNHCyGy1Ze2jKj4mAD'
        b'93V0lwIhAIlnEQhyI7C0LsXACZ8YGEUXYm38rrvVxzMujbUUC1fXa/JTPiwmd8roZhTPaG/k7wQf4o5UbTdXeJQOS2WNWfQEA4t22e2g588ql/vhSmzeYV4OOIuJqrYw'
        b'U5w7VPLOCasIkwSXvEkBgksBgkvuE1wKKrjk6xR+e0uHuhVcLLwW0+2oDPBfy3S9w0TaxCSA913fSYKuNwtoD7C36CvQeyTPRFZzBs0MUw1ZMpmkZ2VLQZZ1KsTIPhbI'
        b'lcK8CeOSRtEdLLK7JJIVKqymugTv6/hJmllWU6VmZZVZ2h+DBpM2t5XwNqor8DU2Zydg7GZoSI1jkialvdJcKjXnKaRgxyVbSC4NKITvA/fZ75OCVARa8SHclMO4cXE6'
        b'5BZIQo1PjgLRtIcctbmWyQ3Hp9T4MHLHuSZDRYuS8fNZBn18JvDZOX6v05p74LOk8vTM4jgpHgRo2/j0gDB8dhw6yJza89NJkICkJNdo1/oBKzgqYYeBCnymo/pu70EU'
        b'eH1mTqG/8t5cGIwfTsqk2KD9NrQFN9Mi1OidQcRmAhGk29cM8NtXSddlZhsy9PFKDjdrw5bj5hIXWac+h18aEbADk6HDD+KIMM4rjAM2Dgq6TqvPVHCr8UvBqCUKv6qV'
        b'uagxf/didHtxFgUt4+TTeHQenUWnWRiuF1ahwyD0NyWwGnKIv9YhYQ3ahc/TAsl4UzRI9dsJmTlST/Jcz5EyfKQ/vm65fvwr3kGOv/xxScalwwPeuheOk8Lk+QXGZj55'
        b's/tR5Kdvv9eygbP3jDymyfze5ztTPWP2Hk4YWOveU7Th0siKC/+YlfH9LyZdnb+k+CdFiSfKbro/fO/Tq0diX1dP1f3mv/81ZuSwA0tX7Ykr+mtW4fYfZZ39Wh0/7Jep'
        b'Qb96XJX45sBP+t74Zcr+/utv/rF1bZ/EgTuPrd93JCHt9++DBCccfSzaZsC7B2RR6SaU8aPQjRQnkT54r2DDO3ETkd+dCe+pw5iI3IbPozt1sUQJ8NcA8FH0IhXi49Ce'
        b'VdjdKysjJx7UKoFToWYBbYTx3UjfH4A3o4NUiM+O9kGgMjw1k55LWJkCRNTkf/zgBdQynHnI7XjOmTCzCm/No86wSqswBB1A29nabeuKqhWSz2wei0Sig/FIlIGq1YAu'
        b'UNSW1GF3bxhS7+6Ad2sgzMKEZ9j/I3t+KBGMEvug0t3QJt3HKGl4CJVPtodIf2H0CA0x3Qv/DlGs7ukvZKW6JBmvZNKasA07cb+2mwMFffCzefPKWU1mnxog+mRgJVxe'
        b'aqcLvDfEXxfoDM2nkr8VTP6qvC91KYMf+WTwYCI0gKVSEeKTOf4mP62cuh4J8MfP0sbaiU3BTs7i2cnCj/gXirZyo5FuPdhJHDK6ReGREbv8dJLsZBfEE+S1HBOTD10t'
        b'e8ID17JEZfLTpSrpW9520SHr8f9oz6grkrOTNVIfMlJb4EYlyOXR7HTvt3KBY8Px7cBxlLi+Ucq+43+5OiSMjwqBFIutIw/ho2Pbl4niNYPYPeOiG9CxiY7sXLY3yHMh'
        b'qwV0CpjBDnRyRQe5FyL9d3zTzrlKFErkoqxEYeFKlKK8JAj+VKKiJFhUloSIQSWhexV7VXsj9/IVsr2RoqpFEPNAUwp1R1bIqE80cRsKM4eLoWIYdaJStwglakhH0HQk'
        b'TUdAugdNR9F05F61uQeLwAMaGPHsiXD3qFCJPcVo4ggFNUbtVQPcSDGmhfpv03I9KohrVS+pRE+okzhVES/taChDnKz6iv0aVSUxgBsv9hcHwH2sOFAc1MiV9KJOU1xJ'
        b'b3GIOBT+95HeGCYOh1J9xRHiSMjtRx2huJL+YryYAP8HuJVQk07UQ5mBbg7uDWIi3A8Sk8RR8FxD85LF0ZA3WBwjjoW8IVLN48TxkDtUnCBOhNxhUu4kcTLkDpdSU8Sp'
        b'kBohpaaJz0FqpJSaLqZAKo5CSBVnwL2W3s8U0+A+nt7PEmfDfYI7GO7TxQy417lVcJ8pZsG9XsyXTDEyMUfMbQwuMYhyqp3P8ShTqqk318sBChPhAewBc+hi0VtBFyTR'
        b'9SrtJqIEMg2uvM7nY9TOkyfQPcwOFVSbnZZyDXFCNDFjaDlTRCGD6JZQJ7OrWOs0thqmLXamzWkFj9K4wmR1mT3BRi8WHllacUHu4ylVTmftpMTElStXGszlZQazy26r'
        b'NcG/RIfT5HQkknTFKtCg2+70oslirTOsqrZqlR7ZjOx8jyy9eJZHljGzwCPLzF/gkWUVzPPIimfPn3VO8CgYYJUXboAVLGD/o56wYcERQljxWqGJrxcaeJFfJnMMrBeO'
        b'8yc4R7xTEIV6IZYj8XibhHog5rW8KKvnlyntJfU88VyEt/jjMhLFV1T2gXK9uWhuPLeWr1HB8yBy18SR9+o5oxxqVZwAxm9Uiio6uMEfGDtbkLR3dpPGuc3Xrf0LXan5'
        b'tCfYIsPE6qA53ZiyWJdNou5khXn6McmjxvuTkQhrk4wKovNrHLXmckuFxSzqOl0ZWJxkHQHS0OvWRiF7F4mMZGGpYreUubpYW0wijyeViuYKE4gZHxmVwmLFUl5Farew'
        b'fgJilOAAgXVs26dkzB/HWGroBlRba0YOd4z08AYPn/QpkR+ffgs/j2WGpKRcbZAnsj1Ysm1istZWmTwhc0lL0ux2m92jcNRaLU77ciLpFK5amCZ2O0dNClSDIARmX8t1'
        b'ewydCuFf+5SLEDkIjWjJ2qERiE60OoIRwLM5ADDFgqLWpU7xv77tfy8I3+6/vj3R0KGrqzVrSmFIykHqWw0z2f/SUoOdrNKfGq1zPO2lLtH6h0/V6Ud9EDonxA7gBC+4'
        b'SAkcmcNLhVCfC76MDohHZXIYqeOnR2VeVWurgUVul6j804dKOfUJcFWXwTIZukLqA02t1VRONlxNTo3VbHI4Nclag6bYYaZkXuayWJ16Sw30mR16UiwtJVRqEpe6oCAp'
        b'EFhLx63awJNJPA3w4Au67TuZxFOz/RO3bT/4c2fMpriWqGeM0ZhXlVeZairNGjvNKjORfQYb252FUiZNrd22wkJ2XsvqSGaHysjeba0ZZMYM0qnQsFRTzTJqaXc4baA8'
        b'UrZQ81QsQJr+XpSMFKVS0rcuOuUZgyGcyGdhh74l3rCdbN2RUOhmZ5WtTX7pNA4L8FKpGvIa2UT396ntqo1SRZNIMPVJpZJo7WQPsFujSJnNRmLXair8rS8uOhRiu2Ho'
        b'lDmuNNtheq4AuWgqI94AXdhhAlRLQkxyrr1JRZ1Lg+fVCa4EPTEYbC0rJO6kxEaBd6TDbV5xXKYuQ6/kqqNU+GGmw0VWA0V5I2H5eBnfmBOXqScRhlsTctENfLJAD6vW'
        b'XbhZ4MbMVlRWoSv0YMEcfDrDYcjJxPtWKqPmowtcBDogM+AT6Db170T78InZ49Axf9tFXK4+Pktf4K09SwEKqgrdQxdjaY3V6HiYI24NOinFZFegVh5fRgfxRqZuX1+v'
        b'r4opRC14bzFuwfuKidUij8fXx+P9s1jcdvcU3EhwUnBpvWToII82WPEhF/ER1PUY5FDjk+nMmpGFXpFzPQBfdAHfxzepvaRiNT7viAvGx2h4JMVaHl/Ebry/yLJ9Bi9z'
        b'/ABKXNn33zEtk2tS54TN/NM/P0qJKhj86qs7dwzIH9o3YVeqIiPm3fAxS7bozRN1Gz767XstUyp33OgbOWlI1eh3vnq+v36yqupG6tbvFTof1c7glef3DlD89/E+61c8'
        b'bPlR+KWz704a+t99ztZdTbuwZ8WR/mMGHPhgUcYZw0ehp5I9ofr+K2t/qQ7NGZ1e2HT96A9a33p3yZ2J9uc++vFzF0/Vvn+7euP5V1uUH/zrB9r7n2n+PHTA/zT8V9R7'
        b'KyOyfjn+7dvLp/7vj8svPFca+YegA1OzX8hLHvPc2gE3tD2Yp+HxIrSfxnzCzUEcPoEfyvU8ujjCRvcaMlwxCXq8DW9NTMctMrQ/hgubJVNqk+nDvmgvvoiaE6EAz6Fr'
        b'NfJEHl0bgS8xQ8bhmYsSMnOy6Sb2cflgHj2PzkpuDY76lKyM8sU58TlBnFIuqNBhdJG9dLsf3pFFseG5zAx5Lx6dVOOLzPP06CDUQi03S1FrJ8YbtC+cWW/uoEvp6Bra'
        b'lWDQxsdJNBSBr8rq1i2n0Hm8zSZZXnox28shjranCm3KTpBeQBvwHXkujy7j3TOY6+xOvB0dI3aVDN0odMSAtiaSOQW1aDRyfBO4HUXyFN49MKttfqGWRDbBcqzx+L4C'
        b'b5rcg/mqumEm7WEtJZbArXwSusqFigI+YjI7SRS0ScvRpaw8Pb82nhNW8CnRGmreUaJN6CE9DH1gddvJTcDqGAN/EbrmQFZOVlaOAW/VZXkDL6yvi0c7FOgSemE924W6'
        b'hc5W4OZcdFGn5NADdE8+k0ev4iu48RncIL/L8ccYxgeNgaxf8IpByYC0nlMTv09mOiL+odHUB5Qck2RmJTXzGpVyiecoPSzZX9J0OgWS6z1RRQ86fhe/T569ShWI3XD5'
        b'tp3ZqCHgTGS3yEBdRHfs2lWGRm+hob9AJeD9orcI9Dsa3bvLNIJC8IvOFIIZTKJJ52yYBki0FhAwREj5lDBJLyBKgkPS6zvKH2kPoZ1i0U6N6Fxt6CjNijqqKCYiBgOk'
        b'tleI2oh0JxsodUT/6IiZqbyKbcpXm6tt9jq631PhsjNB7KDfUHmyRG+/bApUV/18FZ0meyWsUbwlu90xqfFtmTDq8O6YeDUnou+YHf4L/CcI/s4PoauYA9Kv57DIG1zP'
        b'suyRA0zsGIYmbAANRTJ9Wf0Ut0M6m/GLlbeSxnFfADlOX34w9dACGm5SMVPrCA8XgGHu4GwLQQ4ewC+7SDhoDbDX81nttAjvxoxXshaRTf15IODJPosOX13pcxQAhrR6'
        b'YOQktF9uSSxS8Y6zHIkiHpzTMlmNkiJnVv6PenD9pOgeyy98VTR3Z23lnEnhlv1beuavsn2Pn9D7puWTX2//dVVjz+iI2Ng1w396otfkIaN/Grlne9mZptq3Wlr29t08'
        b'+2Dyxegd6+qrB6zpN8LydsmPb05Ghzy/vD4nf/CXn950rK39xZEv4qM/eO+L+39aVFjQuvnP0RNjDyiP7lz7yt9n3777lz9++cIPZep3m4/+/aOU9ImXIv9m/6DHrz4K'
        b'XbV5wv3ckVq1k0YcPR02N0E/pLQtblkRbmLipwU1ojNZ+Bhu9VMyIubKrJmDncOggAnvRVs7ERHLp3BMRKAX1XSXQIW2T6B7YCx2ETqMG4rz1tONjDR0c1EHLi+gVzjG'
        b'5lfhOyyc48mx6DQVdbgRH2YbDfMKGJpnQdTvSmgLlpUyJRRdFfB5jfcg/atoB94kBTkaEkfCHKGHuGEQi57UPDBTkpRoK7rGMUkJwozuU6ShM2gXk5SBYnLhXHzTYKbH'
        b'P0wg6KlSijaiMxnQgoAOEfBVtI03JqrQKXwOn6JdHoQbZQlZ8/Ah4hyh4JRLhYEZFfRYfwnebw88GUM2W/ALWSp8Fm2jjpah+CV0O8Gh1eWAGioFb49Ae2T2OFtnB+Kf'
        b'VpwFSUsEKsCm+AuwcUx0KekhhrBvBSHkG0FQfSPIIv8tyIm4CqHBJ9U+Lwg1v1otSQyp0kCft7WBUqubYB8CK9vm7kC+mxMHdTli22TVBs7jH7OpPewOC3DCZ+gCnFRL'
        b'FuDwR0xlfUXeKcC9rIGPhQKiEJDyRmR6LAy3PJYPNyRXQHMIdp4wY43NKC2RHR6ZqczBLCqdLNY9kUbf5jezPGYK3oPgAnScsLqX14jSrlwH86Bv1zkbLk30uwoNgn1W'
        b'PU/bwy2T2aeTdtnj6/njpB3cCX4tXxPrlIl8PU2TkhUyZjSEezn5NgM19wm5j0f6xGe1xQFolFdRwTMc+D6xR9GlMrmBsaNd0NNSXWu1lFucRtbpDoutho6VJ7iorpZZ'
        b'oWinSCYnj4JKaY+K2XBt9i6cgNXGWrsZpJfZSMvPEbx+jyQwGFCeWiAUqYRxXx3j7biANzodfNptNOApsXpCVxC751K+Qohlph/ogChWWxxppI411b7GN6jqQCxVRiPA'
        b'tBuNiwh+VA/yt4axZ12TYRTFxEuIEhZ0GIIImUGv+4FuR09BRnKW30jPInkhq32Q6aMAxYzcy72Ae1P6Pw6UIPInhLW0E+r5ZT7w/JRzgv0FTrIQwj2dh893gobSaLQ6'
        b'jcYyQZLcHIzO6nAfHuTZM6PB0wkHaAhTptpPE1BnuoBsNhoruoJs7gSyjwYM/lNniHdSLBNsGoYDsAWik9J8cscOyKzx4tIF0QJK5uVG41LB67hOiTUEGKcfYqREB8R8'
        b'psEw2iUEaJjvXI7QTRfUQDNr/UigDU5NZx3wpK6Xe7uen9Ztz1fCuDq66PnK7zLmCu/8E6Z1P+aw+DCu7AqyuZPZ5vNsJ13rnfVS157j/Rh2x7lNjGBG45pO5zZ7FtDO'
        b'ADV2WKft7EX2cTjKhoUGwTfdEs7J2qYbZaze2B/P+3LboQfz3ySKRuM6nxihS0k/HkAfdzoF/CiNIHiCb7N73+iq6wmrozU2dM7qOkJ7iu7o3b47KAnwejsJa2+/3nmz'
        b'Ha4yo3FLl82mj7tutpoiEtrWcGJ5t9/srtm0xubOm90Rmozz4zNkre3jM2onR3kKpKPbN5ye9JJ51Lk2ZwZIVDM5XGQW2+iBdkZXB2aMxmoXEOMOQdrK4KjaFtArtMAz'
        b'EQOs7u931yu0xr2d90pHaAHEMMW/VzQdyaKfr5/6tesnSRkjRJLYRiRd9Euo0ei0u8yiZYXReKAdTxagd6J8CPuKfXec+/pw7tsZzo2UtyU+GekwEGlWm81O0XmhE6x7'
        b'+rBuK/fd0Y71oR3bGdpsPg5/ItZBNHCQ0fhSJwj7EaGtPY+Q++OazwUK5TZcnQRbsr0NeLXdLxLWCmtlEs6yBoK9jN1V+OPvUUIfAWjQ2imPfZ3zZ7TepQlhtB7Fyiqb'
        b'1Uz8fqtNlhrR3JV2GmI0sjqNxkuCN4A6bXGYQI56h3y7uoev1d6SXWukRA9kkimUDkZDoMbRmXSiIdgqjcbbnap/9NHTwAtpg1fxJHi1NofReK9TePRR1/CiKTwng8X7'
        b'yT6653kwYDy6gg6LK6PxQafQ6aOnlvu0nZe7gWSpAQXme51Coo/+H0EKphPYBBW+7gcr0n92k4f2Bq4TE2vA/CazZBlnj3TCypU6gvCiTJQTIdMLEFlLZgdZCQpNwgk2'
        b'X6RZQolMkfspqfTxELoBbKmp1NTaVrIt5FFJzJHCVVtrIwGAHgtJBg8/CmZMk3fIPKrlLlON07La7D+ZPEFQU6XFCWti86pa7/KvSwME9AQFbjT+oI19qGi0UbV/j0iF'
        b'mGwi3aJNbOc5aF8q1eew2pwkuBjxsvOoA83WkK6oMJc7LStYAGpguVaTw2lkhlmP3OiyW+0HSG1HyIW4PzAfRB+NelS+RX8otYSyLVdqT6eLXzuJK824zQlyeZFcXiKX'
        b'c+TyMrmcJ5eL5HKJXK6QC9W+bpHLHXK5Sy5UCL9KLg/J5XvkgsmFbOPZyaea7D8klx+Ry4/J5U1yecfbx9qo/398Gtt5idjg8ibZSyCeEyqZXCEX5LzfL/DF6JguHBYV'
        b'xJ924EgBhry3RuBDlOrQMJlKppKr5Gol+x8mC1Oo6B/JUavobzDkSr8uatG71XuqA2/HLcyHUdUbbRYEF2pI7ODBKJf+O37ZzoPRG1e1Qk6jvKpo0Dca5ZWEfpOCvtGI'
        b'rmIwTQfRIHAKGgQuSAr6FkbT4TQdTIPAKWgQuCAp6FskTfeg6VAaBE5Bg8AFSUHfomk6hqbDaRA4BQ0CF0T9IRVib5ruQ9Mk0Ftfmu5H05GQ7k/TA2iaBHYbSNODaJoE'
        b'dtPQ9GCa7kkDvylo4DeSjqaB3xQ08BtJx0B6BE2PpOlYSMfRtJame9Ewbwoa5o2ke0NaR9N6mu4DaQNNJ9J0X0gn0fQomu4H6WSaHk3T/SE9hqbH0vQASI+j6fE0zXwn'
        b'iSck8Z0kPpBciYZ6P3Ilg6nfI1cyRJxOeVuKJ4IcmSlqO3/6weX2O0reo5p+haQIdO2KES8M6hJSbqohbLHMLDm8OS10P8fruEFDnXld4YjvBts4MQdu8UgbS4G+GmQN'
        b'5XdYtpQwYRM79SPayl1kTeCrOaA2m91bocXJzGrsVe8+zYyUnKKZUg2lXfjpBSQyKiTHE5OmjBoBoTq2veZ/mFfHQHrbKvliOu1m0iEB9Zkc1PWTIEfdQVZATSarVeMi'
        b'Spa1joidgFPCAS8HCFyy5iMMh9joHWU8kX72SCIB+3BNwrJge2+vFHRS6+cJfq1MBIlnZFc5vSroVUmvQfSqotdgeg0B/ZP8D6WpMHoNp1e1KINrBL2PpNce9BpFrz3p'
        b'NZpeY+g1ll570Wtveu1Dr33ptR+99qfXAfQ6kF4HgeyWGTUiD9fBNGdIvXB86AluJrd4Eei88rWKevlxmKMn+J28A3hPvbwXt1Ze05fmKkmufZgYBDJ+eL2cGBXXyp0j'
        b'QObLGwQoP8U5UlTVy5n11xlH8usVDTKeW/55E7RuqbqJp+UWObWbAAPmBppr/wnREcayCdBhunQ/IaiQmOXhjR7BaHysMA53DHc8Ht6+kioTcZZq87diptd4T1gBCH9L'
        b'teTPqGQ7jSwcqcxoET0Ko8vstJO4MeyAgyeCBTP3HXGzzyTiiez42YnB3E5O8rJYJiVUOQg8GQkKINtShhprXXZQbM0AgioGQdQe7zR5lMZqRyUFvYycFlQYzewfPTsY'
        b'7n2NfgoMXiqvItuhNAiuyelygHZiNxNDuclKgh/VVNgAY9qvlgpLOfVqBoWE8QzfY1O1s61Bnmij1VZusgYe1CchiKvIJq4D8KNzFqqh/1loYk9/Y7suB3UW5qNUVgH3'
        b'1Q5PCCBpdzqIrzZVrTxBMC5kTDzqFO/IsJEIcpid0gOHw2wnFdIHWiVzMCB2CI9y2UryTXS/gAf13JPDLdDR/Q1RBUuoKhhJXSjah89Sdcjp4ldg/yOpoSiMflyYXKP4'
        b'1b3a9cgzRX5mgZjtn3Bc146iUbAEYv6rvduD8jmyTimiTgo1y9pOZepYAAWnTTrFSrwJRWDdloo6YMh+jPIZ/FrJYss+oztkY7zIPh4RGFmL7OhX25xtR2dplNFnOL9r'
        b'T+8Obm8f3MCAWh3BkrCmzwA1qzuo/QJb6x9Mqx1YKcboU5+Z7j6O1kAfXG0ncbT+U9CF3YEe7AP9XoqGRZZ1uMqk0xnUZ53Ak/xqpHBN3eJFlSdWEd2qJLpOLbxG9BQa'
        b'0qaTAFAGTWFbXoXFTABKigPUDgXavG58ssChiZf6KV4HtxYn/e8NtxVPNyXjWcyr+GforAXddVacr7PGdIxv0gV9pqTOS0mES9oznW23f9odHgk+PKYEHLAnIUTMZYFH'
        b'7dvjM6MgbWbizLTUomfD54/d4WPw4VNAR99PhEu+WF4//HZOQgbNTBrrhLlEWVea6hzSKXNNjbnSRJbjT4elZJz+rDssk31YxntJ3evo5IewJKk1cYVz55U8QzA0gP55'
        b'd9DH+qCPpMzdZltGNFx2Vh4U39paGzkFBSqSi52uf/ogfQD6T92BnuADHVHkO9TyzCD+3B2IyYEcrBrmrKnS7EeGtVV1DuLspslPyciFOW59BuDnePtfugM+LbBr24Ba'
        b'bZWBMDVxWQVps56N8r/oDnSKDzRz9KsR9U6bHv61CW5NXNrTw5R23P7aHcyZPpgDOo3foInLeeZGftkdwNk+gIOZNyOoiDXkAIg0VVg8jfzigvxniCwJQP/WHdBMH9Ao'
        b'yuOoxiydZXmmEIV/7w5KThtPaM+5iJ5NnG7IfVxqXl5WRu7sorT5T8s3JY70f91Bz/dB/0t76IHav0EzC3jEbDPgU0P1QodvKd5ZNHhgXvMyZhWRmO46zey5M3Sa/IKM'
        b'nJTcvKIUnYa0ISttgVZHnXhmEZKpkursqraZeTkwg1h1s1JyMrIXsPvC4lT/ZFFBSm5hyoyijDxaFiBQ88BKi4M4tdZaTSRyFYvx8Sy0+Y/uunCurwuH+DF1tlRihGmi'
        b'k9HkgF58FuL8qjuoC3xQx7UfOLaiM2hS2k6gZeTOyoMhmJk7m3B6QkrPhMn/dofJIh8mvYqotGfLSBhCkdCO7SnnisRm/9UdKGMbj5fir9AjjQyQuc0s5L8WeZZ2ft0d'
        b'8LJAptfG7IiXt4bYsjoRKl4nE7orMlcC6MilnnC96Y4hdbGq7U/u2aFXsgsCf/IGuBpJeQX1nFOQN430elwJ16ATPO830x9PLmCe0MSi5dNxmMrVZlvrXCUzaFX2P5Bm'
        b'LiOXdkGdqU2ChC2wV3N0o7Ut8nO7raNQ8sk2qUqzzLv/COvc3vSrS8Qnc3W/9gtOv3e6HiliXRN5aeO0iIHsbJjIboVN1rZt1WF563OQ6fIQZG9pjOxqstN7giM7u5Vt'
        b'rjnQ/m9IW+XESNGpB5xKMmAYyTfJJF8QYhboDBlWsOt2R/shw2Lv+nqBmr682CjYOqQLhzyrucZoXNkOm06MDLRcrnZoZ7tX1PhB95s86naGrOd8lNNGNFYvvXjCA+1Y'
        b'SsmMFSRJbvrdXo9SMmEpmAVLTg1YcmK/osFFPGEBxiulZLuSUzuUup2VKtTfSKWUrFuqNuMWMyypA41X9mG8RD72EeQujpc68amistnfh8vPiWWIbG+pZPLQqORnDI4R'
        b'1FXQjP8w6EZX/5VPG7QjLEQlUynod2enDwwKxXvGrgivDdNm4u0JudkG4qdOvicQX6VAl9EVQ6cRGcmPYxXnv6MlCo0c/VKhTJT7vlSokO6V9KuF7D5IDBJVUFblFip4'
        b'9oXCkmAWiaMkhMa6FUhEDsgNpSUixEi4DxN7iFFQIlzsSbWwaE/PduSebYFVutwPUbk/EyCe74QRG6kTh5EnW9NGoZLEIJCJvuWWnK4JPMG+bwbDbbVNNFnJR+OGtLdr'
        b'EohG/30Uh9fHI5Gne7feSlTeOtpzN7Llu0Hmc6aSvmLXvxM4z3bknbp09OS7EX1bfAbDTqF9hy/F2Sd3B8/thfcsNU7prsamLmv0DTpxk/A6g3hVP8FOvjxrn9pV1YRZ'
        b'bPMTOF0NRud8visPDUnrbIMaKGgpd2rxg9peqEpQKT9/CqHa+GShuvPJbZQEa/tjAT5vm1yuzY3KEeUE0JKjP3X5WiZzjIF76jJF78mdfJnMPsWpYBtnkFYeDyKegHzb'
        b'R0Mf6/0V32oSH6CsLeTCyHaYjgwsLtrM7CQ8O1BAI8F4T95RKQFq0VFOmqDsA/PTyN1z5EJ9TcgIgUirrYXltvckQagfCFq0C2ctmUkU98j8zg+oJKdscpKlEwFNuxne'
        b'6ZqKQiQqavPyaRvTdhQ0El486jemfToD1rlS5nPOjKbzhfHyem4m18BLWpIst4MK7HuJnHIgfHRxGDneQXSaXcJy4t7NPk0JfZVAeree3ZN54eGd7SkyAi7HZZKztRIA'
        b'rNZ3hr/T5jRZgTmRXSnHNLghPN9WXTtNy3tkDld1p/qSgr71wpP6hpbK1arb60ptbjmUaNropU2toFrGTF4aBftsn6rRTbCTSVBorUzqdBDISvYBQpWMOKQQhxMajAC9'
        b'PD8r1E88o+sWSULja3irzsBzM/HFoGweNXeQ07HSf8cOPkBOw+jSX9lRRYmMeJwQfxPyoUExhEhh8klBUU2krtjjqLqEfElYARI5SuwJUlhBD9iqSOQrd5S7T0WQGC3G'
        b'QL7SHESjXLGvDweJvcm92EfsS/1SgsR+NN2fpkMgPYCmB9J0KKQH0bSGpsMgPZimh9B0OKSH0vQwmlZDejhNj6DpCIZRhUwcKcYBLpHmoArOHNnA7eBLIuFZFGCvFePh'
        b'SQ9oCS8miDq4j6L3etEA9z3FiVJcLxJPpO2TjGpoZyRtaU93tDvGHevu5e5dEUPjaAWXRO8N2hsrJrfw4iQCBXpDRqNpkdhiMeTzheI4eDaZwhkvTqD5seJoOpGneMII'
        b'CXo9JTx8vofP0yo8wuxUj5CR5hHSCuF/kUeYke6Rpc7O9chmZmV5ZLNT8z2yjEK4Sy+Ay4z0WR5Zbh7c5WdDkYI8uBSmkQclWfYVlCPNzsjXqj1C6myPMDPLnkWYm5AB'
        b'dacXeITsDI+Qm+cR8rM9QgH8L0yz59ECM0qgQDEgkxEw671x06lDhPRxAhaqS+6Lmi7vNmo6s7908qnUjlG+5bkusquGL+GX0QEyA5x4a54Bt+SQ+KTpvninJCBogiGD'
        b'HlPM1mXkzEmHWZFJDnqic3J0Hz3kpuFNEei6Ee2yzNj0V8FBQnb8bc+xz0r/WPro47ioOFO6yVph/f3zZTrTotfe+d71naMObrym4KrGB4Ue+YVWRk9MTitGO0PROV26'
        b'C+/ED6RDkz3wXRm6+BxuZUc8X1mfg8mHsgA2CTNwREC71q9CD8ulb23hUxrvt5rbPtR8Yw52h6d4zy0+eada8PJo37lJ9juBuDCujvanqMAPICvadsrtCsKcOv3QK3Ar'
        b'WmKEr5gP8lXCqMhBWN95SPb7s4DvAnSKQbnKb5wJyMDvZaooCYVI3xhn845F9Wn7XqaqKRjIKhjISuUjq2BKVqp1wV19b5wJkvZk1T+XfvMPPViBXszKzsW78GEWiBAo'
        b'Sa83kBC3NEYsGe3i/JWoMR2dlXF4R20o3jkS73SRQAMz8F0xyxvAkBBcnn6udHA7E7cAd27NmheHt85TAdXKaYCN0OK8cLQVnaCHx7UTlVwY98XAIE1pdq+xKzkahCUW'
        b'nUO7vcfHq/EJDl/EG/vS8l8ZVVwkd7BKKC3N/sfKeI7KhTy0Y0pAgFvf6engiCIWH35BYVAdOlHBvme7C2/pk5WRg7cMztLhFi3PheYK+Ay6v9w1mHTHS/guPpmQTo6c'
        b'T0FNeM/opCTUWJrFDUE3ZOjBqHIXkasWfGdYQi45dtySU+x3XD0uudagj8NNifEkjq9Nq8LX6uewaLo7M/DGLNyckZ2IdmUrOWUvQY1ahlKidNFPr91KwTsSSGfr0a4J'
        b'UADdFcb1RC+6SHiLMny9ZwIbCArszgQJng/anDj6tbz8OIYV2pwu4waizeHoVq/F9Ez+0iJ817ECX5VzPDqkGM3h1qg8F7Fu4JO5o/y/GVkLhYriYPSadbqc4lEjWKB9'
        b'dka/LVYlPiULA8l7P5ZGx1mGb6zMkj7tiLdl65Vcz9noZbRRhp83yl1EY0DnRgxt6zF923cA4oAZ3GlrBoEjoG0Ch26gh6Fjs6e4SEyT+DET8Z45UMuLM7nVXM783i76'
        b'VfZj5oHk2wMrV+DraOtKfNWp5ML7FfcR0CF8V0c/mhKONyxywAO80TKXfH4gLlMPgw5skQIqiGvDSMmhPfh2CIcb0T3XaMLj8U10PIH0A/RLcyJuLYyLA4bXlJgLnXFm'
        b'st/nB9AGdC6YS0CbXEPgvegY9EIovomvO/Ct5ahlpT1sOb7Jcb1Go1fwCRlq1JhplyWteA43k2+j6A3QrQouCu1De/rKoNBtfJtS+4UoOQnPtCZkemkYmlDJZkceOt2P'
        b'fMISvYQa2Ucs0Q18w/KVNZp3WIFRjUqbVFyQVdAwPfL5gUrVCwcb6/9qU/+2x5SUuXfHHzG05J+OzX/l0Ruvv/zWjqFJa1p/P8rOrXn0UvyRoKl/+a+p4e8M0VzZXVek'
        b'aoypl6WEl/z+v1JPWpdOXn9cc2Vp2s5fxv3s8a4r009/9MaI1s9jjj9f8vXQd2/gB5V/nyi2zvzwf/+2zVp07s2Qt2p/3vL9P/S6uR8VvbT19G9nrl//52XzU4O/Tnyp'
        b'7vd/eTvzbMzj3lV39kb/Qq8fN3jz8NLeze/85Jv57535/9h7D7CozvR9+ExhKEMTUcGCY2foiA0ssaF0lGJXOooibQC7gqL0ohTBigoqqIggIIoanyd9TXZTN6upu+nJ'
        b'pppsYorfW2aGAQY12d3f9V3/a0Vh5Jzznre/T73vsl+GbPlkzbbNp0fdTRv5xLsT3/X8KL1zT/iKQbH/mhC6rGHDS8vujhl5ysu+rsXZLHf+FwcnZlQfvzThvOL4paSU'
        b'6lJrD3mI97Xnl7lNHdu2qeSHlya3fe7hfKCk5vjuLf96+9ZHy8UxpckeJYEjvgncveX45jHfzTllM2XanZ9+2nj72tCRqvGxv7h7Fn081tY1BTb7FnxTcPOloE2/xn/9'
        b'0evvOS//YPymyl/ybptvXnnpo11ZNcqCCe9feCBSdpYs9VigHMMwcYKWbuZHYvdxmJJADsSFSZyxsV20gawlKMH2BM72JIeLYqzHZjk7UqE0FXIZCsFaSU/QZ8yFPAYh'
        b'hM2YTSGENpmbmaRhmwrb081kgnWqBIrxVCgWzOWcT6VemEORfwRxJtkBKkRztqQyNIfExPG6TFH7Z4ng8JxJDM3BGg5BLiX+XAfZpAaYx6rXJMZTW9axxq2Yjzeh0CIT'
        b'21OwLYO8NWmsfIh4HTQtYUWvXopljK5iqY0azoJs8sdY0XYDbCmfBOyHvG4uT8ooMQQq0+lRtBEq3f0pVYR4C163Ec3A9tFcgLgeCYfIqisgOwSpstQT67aI4FKiij0F'
        b'B0cEaZitYqBO5DppfToN/rFUSFSZpqkZ2GFB1kSRhZGZCTZbZJIFiO2bUknFLSWBUhl0eqrxrvE8VuNBR2csDnDHY1gpEmTLRXgezi1jnem8fA4W+sAFImrswM5JogWT'
        b'8DRDShqLpydT7s1COO8TCOSEc6Hw6EOhTYq1ULAJD+J5jrldihWkcylLJ5wbQmmQCgOIrDNbjFWkq6sZ1ddKPAqH1dShcBkuavaCwQFSMyLutXE8jSq8lAqFrnSKjYLj'
        b'BoIsUjwaGiK5ONW6kux9ha5BT0Az38oMBHmwGCvhEuYy1BAo3ZaqphsLpgcyeQc5JWXCSKwfPkiKrXAaT7DxcsNOyNXye9J5ildmM2Iy63DeY0XQRLqWwnYVB5AbC0mX'
        b'+YqHREM9a/AAvLSFoYc7uwQFBDOSWJEwFI9IyROpcXM5eMiFScMpv6j2GBkFJ81DJYGkTzhBqTE0raPUpe6DnIkw4S8hk7FAjGewCbI5/tReC8qeFuznRNp72hdLiMI4'
        b'TRwN59ekU+EsDgqwmV0mlyCPiAZr+Zt8ncWCg70BZi/BG6y2rlNmkfuCnCDfVb2rG5Au6diVYWCAZVDF7kkck0rr0g3GYkV252I4LWFHQlY6PWCgbKk7XR89pHIi4JS6'
        b'esb3tCM7khOmeIwJHIdqp3RqrPMhsnCT/mfxCDk9GzAvQCkTAgRDaMEWqE6npj48u26Nmv2W0tnqJ8Dl9LekpIMcgexChCedI+Ry8VLQPCIjarGELO4mOKtf5P7Pk7ky'
        b'AwIT3dP6iu4zTURGlL9VLBXZULBT8nOwyEZsSmFQGM+rqchSbEmum4iGkt+JBaMHRhIrlvxnKjaREPFbLNMJWaUOOZnO/5g5eVAvsZzbkVkFG0zUaVSamGYptbKl0f5L'
        b'm0Z1QXlMVLo2PFmmilkXtzGuN7iK4WN0R4NRWoJIXWjaBvqNFcJeRE9wbjZfL9Lts45+lI4/9SCF1d+638M7Yxihble/KKxaW3nPl/0uIzkLFE16mEH7vtYbbc/IUDSJ'
        b'GLx2CjXmSQ94+98XlUvaKo9QR1FFPIRq51dtRZz0xV0lqLrr9kcpPplvur/3U92Nv98ujAVc0XCrP0x5y30JND4+Iz05Pr7ft0q0b2Ucq+RuZ3K7gqYEdId+0ZqwEOo/'
        b'1PA0xcPGX6atgAMLhUiIV8c+bKQRJ6TX45JoTkvsH+4C0wid1dxvNYy11WCBWTQMYy2FhdPGMP7etzO7ddHDBtxU+8oJ/cMc93yxznvZ5qqFAqS8M1oEeW4/EGiezQ7R'
        b'VpPtgtZ+IGL2A2GnaJkmbb6X/UBj4+4NFdc/iawbe3O86HdQyFImpgyRHuhB+qcHH1HP8A6VQrUuOSMxlrHJxqUx9HFF1NooGhSitywtqdO8xLgoGiylmM+SZujAqiFz'
        b'WayhGkhcHWaUoB9yV40xHhkZlpYRFxnJuW7jFA4bkpPSk2Mo/62DIjEhOi2KFE7DyTTgvP2SD6b3WeUUTl8dZcCxCXmY2had6K9Hg61HRi6ISlSRGvZFBWTZXkKvP6I+'
        b'wy0JShhm+KVYRSMgvra583mLbeRz0Ubx790mEliBqMNUpRQxmRaupMAJLm10ixojh3FhwwequBlO1NthJI1fG8fQ0L5jHqNdvb7sto7tcd6oYhIjWPd2e0BoATrUtNwp'
        b'1M1Ju4M0yVKqdn/3OkazhG9NdQ5SRicFV+LW9zK24n5H3VZRoZWIdpeU5I4gojxBO5b7M/2L6GsdZm5rVv6HCW31Lk7NAu1jM6a2HThF5PCDanlRKyxS40t+gAORoRvD'
        b'uB2J/iI4YBNWMfqpc5Av94RaPJjwzydPGajotvRn/62fR7pYfRZ5O9p+sENUALUUR38R+UlkUvwXkQVr/aLITAiQCFX33jAxGhDxoVLCJFwi4J7A1t6v7yWrplFlhYir'
        b'dtjBIApVW3GfLs+SL5b2QOs948V14qZMuN57ngmD8dp0OtGwwfexjMlk3qnU826wvnk3inouH2PukUK4FCnVAfnvn15Qg+61XTs9d5HpObTf6fmJrnE5w5s2vxJq1zzO'
        b'/IQrrrrz0zGIzs9Lw8xmLIW9SjGzKS2C3YP9xXCYzV2phQjOED3nICPB3hGBZ/1x7072mNRDBK32eCpBEjFbyk6Xg7Mvb1jrExNAJsT698/GrVu7bu0gx8S1fjFBUUFR'
        b'om9tN9istwld9rGbgUdKvCA87WQc9a9bGleorrG9f5gCbWcztUHvGA02NbGUbh2sf4z4qIgfMhY6B/AeMggW/Q7Cd5a6wnY/7/sPEqv36yLqu9zJ5nz4QZhIRc0nsqgL'
        b'n5OFeTt6XbxpaUL8e0SnsDYXv3fdkGzQ1BI7CMrxjI7aCXsW62ie/eis2A5n+wxcr6ANNkJ6d2/7Pv4QFr3RvVn3wyNOSx3V73i8b/4wj0vf+JB/R0LR4FE+xkEpDQpL'
        b'eO/7AImK/trLYqR/lCk7JecFSZUih+3ibqmvzynIvOf9H4KOfTQ8HpbS/6FHyxvbbwe+Y/ow7VFPLOl/pQf7SpZkNkdPui5SUQNX5fRRjlFP3vmECBurnrxcdqLGvTrb'
        b'QyKMuS/5bsR9csww8PdT0Og7A05ioRO180hni6AN99mn08AFMnEPj+xjZBkqPGyyL8P93NhUJ3FzZPCwzjLBCK9hG1SLYT/sDuhn+MY/dBW49FXQeShtv8NHy5vQ7/Dd'
        b'fejwdYfpCn38jsM1XR4vML8j9fObMk1B4+kX5w5g4kkPf3+uQa4t80cOzR2WOzx+uNYnKf/9Pkka/GLdZ+SdgtiBFOYKl7mvjPrBCrB5iNg8IYP7yhRsUJdAqTwN27DN'
        b'grpYsGXXiHSZYAl1YryK5QsZcSYWCHCT+n6W+JAhDIbz3PtjhWf6cwDhvs1yaMuAZqWMHX6wbzVcVTksoe4bAcsEKMIznsybB5ehiRynrZDnlyGjdJgC7N8BxewpPBU1'
        b'VB4El7CdjCG2CXBiERZlMNN11eIBKreR6WRUMY+UHghdzDVn6IXX5AZwgvYDXhSgGlulGdyibyOoMHcVxV7EAwIUKLGCuYaGZxjSHrR0k2WZPBuSLLBKpa4mXdWKB3bi'
        b'JVrQKWo5boEaVinZQtyjUiV0twRyYU8GnXMu0LqD9VIv1xg2p6fh5VAfR2qHD18EtWbURVYG1cY7TMw58svxYVDlgWUeeB3b3aSCiHQDZkHlRMbf4TBF0cMryyFibmAx'
        b'9RQvWoqVHn6hhkI4VsuwLdMwg64YK7K28rEcy6n7zV1w35rAfm0GlWswV4w0nsxVcN0I7Yk/Pnjw4DNj5h5TuMneHq+MGChkUEMZHFjq4K9BoyFirQ9jHC929Qu3x3wf'
        b'ERmVolB7JZYu9fGlElJRIJOLQujoy5LMVuOZZdwnetkikEZVyAJ1b6QTiWwV+a7B6j7SxSyn8+ccXDPFFs+YjChalb3+2GlG7t9vBlluRgaYFY7HZFgSZrbAaqjRjBA8'
        b'OBKuwXU8hhe91242jh+SaoJdsk1GUGAcbArNuAfr3PD6NuVIzJvugodkcHCeElpnTcIaG6iGcmjMCCFvmQcNiQaYjdlmgruRBJrDoWUFVspIP+ZCpQPkkLEphZKwYQk7'
        b'4SxmDYPr60cPw1IT6CBTYC+0x2/DHIm7PalE8Ui8NH9gYIAl2zLYLCufO0w0SSwYNc+yDX1vmFLIoBsq5A0e2ZfHNljrHPXG7HBdLtsm7JDHxC5gBf7Dxpcz4w76RLzP'
        b'aaeQQdHnFpLt+zxtQo2xoDClJvo1G+AAnCcr+YTIHXZj/XQPMhblkWRTP4+HwifgqRWkvlmDwmB3HOStxVq8koZHDddBl+UWaE/lUQ1Vvtjep5rXyNIiVfVx9jOwGkTj'
        b'YqBBSf4y3lZj7AiCijCliIUBkGl6hbl+C6k1vsTXiWwTE6GdDPIQI6lbCmaz8AcsmA0H/fVS8zo+MVwvNW+B0jQBcoYxTmDohBaD3h5m8sYCjZe5t4s5HlpJ/ejOgM0S'
        b'FRX2AwaIBDGUiOZBe1rGQlrmJbIr1jr6kP4rCuRrwNXP1zmEh3H0iRqAii0+RAtMoRvAohDnJWJhS5jFFrshGYvpJPBdwZ36vovVQR1q/dEnIJi11GWxUSa2L/bxCwxy'
        b'cg5i4SJ0tWkjCbBlOdlGSKuLQgZAvUkimwRZYyVMF3Zbkmwb5DKMHKMs/sF4xC5/F7XTxwiKB2OzGPLg4Eg2R0zgjGNosDKQA9aHL9UToUJOdGyELDKqB7BolYIosVeg'
        b'zmeU3Ta46TPKAy5KBWzBbCuogStYzk4Rs0y602KrhbERtlhga3pqBhGVsQDyVZJgOGHI4zYqNmJHKNmtJsMpPwnZ484LeF7ixba4zXgcr/ornZk6HUTqZa+EU3iiV/bA'
        b'aoURmcR18gzq3yIq62U4FQrFYVhM+YcMPDDfQQSHdkI+P3I600fKM80he4eIvKuKbCk7sJbFrRhhI1FrW/GyClpXYquhIMYLImeswAblAPboKCKenCCzpzolgDw7TcCS'
        b'MVDNNmpog/oA/4DVIVq3m3yFGJs2hLCCh8OJmcw93EXewF3EIjiMR8n5wKgA6qHTizpc4YKK+lxFZCVBJ++bDmidzIIYxIpAA0FqJ4KTcHEAD7PJNYGTZPbY4WkWFQKN'
        b'UsHUUjJo55oMGlS1iYxCE5n6SqbkO/lSd6E/488ZT8awONQgHm5iB+syLEhJ8tcBGIOLvkjEsEo8tI4Hzpwd6OpojzchW+PHM10rsVgcyY7cieshy9/XaamWLlkxknVW'
        b'gNNKLHQOYj5Kmdmg1eJBa/AMP76PyJFIki5+8zZQ2uspImiwXM+uZDiQSe3sF4bt9AJp7Knh2MT7qGjREMqTTYMyNFzZHtYsGiSNDK4jWdVF2MBqR2YwXdYGwigoNzAm'
        b'B15nBhWko+FYGNkGmKIO+aSlZP629u2cIMg2xDJoHs5emwr1a6mLXUm2JeNZmZ5iqLeHnISE+uEGqh1EZPh8nLV36LWku7Mtu6bbKQus4la6hrQP/FPpjP13Kp9QeBco'
        b'fG3rVlxRiG7VhtmJxgTsDhdEDqFXFLsUGbPGpOz3iiizSKnsLD9i/co/X3rp9jv/HOH54nxn3wPrw5TL1q7fGXhswJZFMyI213m+eG9Z2Lenxt6seO4XJ8WcW2snD6gX'
        b'P9j1kW1c11uOTcv/emGBdeyMMe+rNlq3pYU7FS2MMt/1Y3txR2rccQPvytve35htzv3VeVbUE3LH5R0Nd58LCU2c1PVlUdOYgmG+M9PvdSb/4hdS9vnfh7w2fcG71+JT'
        b'Xrga9P5fL31v/+WTb7ZVOq8tHfjOx7fqG19bMXjIWx8/tWXLc6ff+9JzybdrKm9NfL/K2KGz6rtNZ+9tjKtKixwUefOjOtN1BUbNAfGHZHGRu72S5r+9Yb7xvuITXy1z'
        b'eSPwYFTTiZ/FF/d//krHl5MyPzH7y1MnVsd2LEp/8PrO2qqk9SlfvJLzw9IX/vnj4ErJ0vz9v76/+VJ5R6L0l7J//LPm1cRNFwq+e9Fs48mAqB23pv/tWPGtT17dM6j5'
        b'J88KC+f2l18abfeGxGt9nfXwOd9ZDSza3NFy3+Kt1jdfH3YIonyedWwrip/3bPW0BbdinpnpOia3bcQzw18fE/DxMdsV6TtbbV7Nv/tPUZfVz8+4GWd8fzTo09s3LILc'
        b'LtQm1gz+LMHuyU8n/HB/3TYw/vbdTGf82/tvxOx+8Kvft0YjLD5JHeO4et+X54PT2n4ocM9veXHW9/uiP/3z3HszbtsJ+784UZi5rfnVl2uOPjdgZ+gPgcKHjnum38h5'
        b'dtCaW/VPKV/54s2ctyZvLHn7XxPrz9xLfN1144d1VeOf2vZl9Ut3Du+KM4h/6tQLrT471ltO9TN59dKqgWuMtsH925e/eC3w3pLLT/xqcKlNZnvuJ+U45tBfMwpKoTDY'
        b'gOxcJT2CIJLHcqaRTnK0lfsHO5Od8byIMVYtgGoW6TFTSh8oCMAmBd94dg5jbnmy617DSh3eDvLoaU3MzJworroVe67QhJsZCEa+eAXaxJmwD0pYHAK2RGC+fwB2Tuy5'
        b'JWIlFLAYFEesU9BNcRPk6uyJdbibNWoTnlpPydSLJmpCJXhIzzRoZsEjQcPWcb3RQJAFT1kvthsLHZwobGK8o4OLEgucaKhDIzYvJ2sWc1fyuJerrrDXkTLb5TuRXWkq'
        b'US9KxM5pmMWqnLQKL/pr5M09ZOtVk8OQ/fkkD/TIcl9G4y/IEVDhBKXB3XKrTBjpL8VjE+EKV5evYzlUOaqrIYucA+fFHrOCGVeK6wbMZ/E8YkEmJoLZIbGzw0Zmy4Wj'
        b'2KpUQbFRqhm2qGjAXa8QG6LTmMmEQGyTwQ0jOM2cAeugBC7TcRBwj46V1spXArVEA6ll4+mfuJYcFD5wBNqZdTiYRfcMwFwJUbiy43ngyKkN5HSnzPWuzuxgPZzubyhY'
        b'BEvWzQxlAz4+ItAxOBrKnYi6QrnRyCzDG2LsCPdmbd4wUdktXaQuYsIFNtqweTYJyvzIGZEcqjkjglNYvWJwNzTTyK4UqNAN7pLABbwKeWz6Rk/GS+qIGDJkeHCWr3jI'
        b'EhdGVDMPToToje7A6nmuPYI7BuFeZvnG60ReL9QTXLSDnKtt0k0rHflAV83arBPjog5wgcvrNTEucC6dddoIOOxAhpkT7oyFPEZnlyVJJscUj7bB2shdVEg+SNSNIs5s'
        b'J08S42FsCeEzpXE+mfPkYMPdeFRzsC1yYC13NZaxo3/VUs3RT47gS3ywjo3GDjKk0EG6TPfwx9LYdHr6j4fTUNLf6U866IhBvCUW88VegCUJpI7aoCKsW0y6ejDuk1oN'
        b'g3xu4zmzyVt/HI0eA08AlLMgnC6jdKpczjOL8g/wheZxZO8JETlAvZT3zGWshU7Gl8fI8lzhMOPLu4jNStN/JxhGOfy/iAz7+791W9otegFhMjsWRSXqY8eaSO2uRowN'
        b'xpLxEMkeiOk/sew39k9iKqYJPBRBjuO+DSb30jvFIvEDqYTiylGMcqlIRvlkGOiwOf9HyqWfrMgnGtRjxQj8LGlwDynDVE3cR36SKzQxipQmNlUHDZmzgCCphIYLmYiN'
        b'xBTdln51o+GKSVli9pN/yUTiL2WDKa+NqbpcnvyntaH16hBu8+NRQjyChyVzOdFvbixAKG5zd0hBd25Ut+dh0P/ZuCqNdGo4S1PDtFxtpZy0gUbM0LiP/NehX0Pjm3N7'
        b'0BM+rJOUIpYaFvQIzyf1fYoY4O/jeT45JKb0/b+J9QQIzIlPpxSEUYmJDNJUh9eXVC6B1ioqsQfSKUfDio3lcH9RiqS4TX0K5eEm9pGRizam+ybFR0YqohOTYzYoXdSo'
        b'tJqQgwxVXHxGIvX7b0nOUGyK4ryIsQmUyrAv57BuJRKS2I3xLElfnZMZp+KJmhyCUEHBlBQJsarHZx2k2AJeCl/m+ifzUJVAkV/Je2gYQJQiJkOVnryRF6ttmm9sZKSS'
        b'YtH0Gy1B+kfTH/RjQpIic6oLpbSeS7pxE+3M9HVR6dradgdk6C1R3TYGR8siinjYAymAgtP26CJNyuvatOSMFIZRp7dE0vT0hJiMxKg0HtihZqHnkAkqhT1NPHciXUBe'
        b'yxBNtqSQ/8alx7go2SD0E9hBOzQ9TjMu6nFnAV9Jvekl1aMfm8wSblMokLG+MnsMwCPoGUWCPnpGE24fd90eSc3jWA+VzEROc0mKuB+BYRnEEAExW28OQig2SSAHLhjy'
        b'lLJ902Vq46HCSEINlFdT3bBiqJ3PwHGpO/BiCOyFC/OgYuVc33Q4hyeg2WhmkNMIPEI+EuX3yHy4NnIrNFq6qcYy007NQl+bb8QKkRAZ6dAqCxQyJlBp4HQiFSKIJBNK'
        b'SXVLaaoMTQyCozT5a/R6KZ6DSjjDCli7wGDRU2JLQZgdmbhhtKuQsK/8ZUFF8/fu3v1p3AvXzfa4WXu///Ox4p9sFfNisycligaZvVhZFrBn+At1xi/GyLe9qnh5xA6v'
        b'0wOW2792MuIvO5r3vXZ4QeCf33454sOR0z6YsG9TsstSA/cPrr6XM6o486dR55ccf+Z61JU/bxwd8PEbkW+8NibzfMSi2yPca1f/tm/msGPF7yt5iD5ewEbksdxYqsBG'
        b'HTXGG0uZ4Axn3aBAHXw/Fo6L5hAR42g6NbCv9hjwaOHERaobIFwr46E0+4YNVFFTqrO92pgEdUSUHoBlEmiG47O5sFVFJV4dXQfayAC3ijMxx4MJcaTq+11onDvU+wS4'
        b'q8Pc545hQhzuTvXUhrlvhCrRAqIBVbDH5HAICogqABdstVSVeM6M98eRgQFq/QtLtummLEATkWWpAXUrFkToC5M/IaGSLJS5s3htJVGvSnrKstC0XTdeexsUqv1sjwzl'
        b'MKZJdmy5MtnFQZ/sskuYxiQWipP/gHyXUMmESiS9/PnaonpyKbr2PND7EECK+R3dB2s++e8perAq9B2sWcK7Vv3HFGjrQEM2yTkTQQ6aHggEmizU/oL9JHmSh+agasLu'
        b'fpTqOVVD45LUsKQ9sdAzVPyUjWP7HNmUvef6zgvVwTfv72iKi06IUUXEJCaQUjgprgbIKZ4CM8asc2F3uHjT7/PYbf3BpuuUqu4XLxYi6KSNEaQwvqo4Vs3ktFj6C7Lp'
        b'692U1TDw/dbBZUF4QCSDcstISUyOitW0XtMhegulWKFaaDZ6XqijZlUZCekcjF1bKf1HxSNrNW9eWKTTH300/A8/6rvojz46Z9mKP/zW+fP/+KNz/+ijy7wn/vFHPSIV'
        b'/QhUj/HwpH6iNH3jOTcMF2/iYp0UDurp79Aj1LNnLCqLUdMvj/QXYbogLYohYnfP4d8TTLqUSrB8V8j0cHHrsVpYECzHoeXLibwwMyHqj/XU3LBwPVXoJs2mewyvB19u'
        b'CbGPELqkgg7Tq1boGsg5sb9WyZjP/T2/eNN5aYsE7l/wiJmwViWn/vlaAWrIIZ3FXCPjxnhgq5ubG17H8waC2FfAY1AE+dxb0G6D1xypqSfIhXrvqkT+LtjCXAyroRjK'
        b'Ha0tgvyIdgu7RdOgQeOGaVk/2hGyoSHIlz6TJ5oBe7FRKeUOnmbohArmy8KW5WMMBMlQ0UxoghpWl4HDtpFLzenY4Qs3yUGPlaJRcGoa8yMuNolQYQN2TSTHnChZgA68'
        b'Ppd7VW4EQYUK2y3SaBAhaQKeFjngEU/2lLkxkQbLoQzquUsezsJxHmYwIRPy5CqdgImTUKwUsxKhEQpS1XWMh728khshm8cS1GOBnbqWUG2qriVemccdTQWwey2vTAd0'
        b'qiuzJo3VxZ7IUhdUmabaFhhgqVLCHlvpRI2W7IXYOJ6/cDV2cP9UHuSZq184Dk9oXkjkMv7GygC4IM80VkEpVEoFibHIlYgqTWzMcf86O7lZmsW4GYIgcRI94YjFfIj2'
        b'zF1BHXRyc99hIkFiKnqC+ukzlpJLS+yw3J9KvaEs1pZ6e4kYLJDeObCdyNhFmANdUAFHwmDvAmghQ9lFROYDRM6ugC4rA6yMNjAj3wLJkBfNUAwkYqKVBRE4UxKm/eQj'
        b'VlEkTXh9Rvhfpgc95WYpe68mdcrhLzzkVlYjBp15b3DCtCfXFdp0Ntu3p9hv9jl9qrYuxcs8++zZBk/hTO3fg1uebnqr6OZPM6tGdJ7YV1lx/IMjKwpOxsp3DfB5+oXW'
        b'+d+4hIxZf/6bII/z+R957fjTgfy3Ykd0DH/z3XX7x7/5cXaHuPy5hDuLN4yuH+3jdvS1D24827Dz4xuLKs/O+tnWq7Vzl3dL0VupgXtefHlH7ovmiaKfs15cqNq0xyX1'
        b'/pDX4UFtx1ursj5WXvih4fNRbS3fzv3N4sas6iv7Wi7Wvv7N23/x/+SjHzM/GXQv9rW7oRfuT/3X27NXqhZYbC+9eb5h+y+G+86tvivsUFpzs3npVjyvASHYuUJjyh/n'
        b'wq+emEq9ojT7NQlKNZZ8K2jlboKclGBHdTAy1C2m7lpTJ4lhGOxmdvxAS6z23wnFXKwXzcGDmMW9FkcGL2b5+AOgxUCQQo4I9wRu5pbDc3DZRJO9SkbwJM1gFcGlwXCF'
        b'VYhsEvtGM3FdPlkjsIszl2M9e9pGCtccqYkf98ANKgQbYaGYLPurUMRePGwi1KqgY5oc26iDuFDAs5hnzOX88+5WUAiNG1MmU+iEXLIAyXTO4y89Tsoog8IhmJ0yWUau'
        b'5lEchGsaxva8VdgJhVhmkTKZlpovkLl3ES+zGg3Hs7Y6WaGwe7lUYFmhPlG8KxpVRiqib17MNCfPwmkBD8NRL37pYNg01eZAsvHl0RqVCdR5fZyrS62RQ1UJeDnT3IA8'
        b'dIZoFJBjzpoxczB0qKDOD9vJLiCCJgGPwhnMZ+ORBMXOKjc8mZlKX1UtYFHcWnbBSZmqMsNrmankPVBF94sjMpYfGzmF1I+qUCskWiVKrUBNGNtP2uNDwpGlKiIVM+0i'
        b'Wr92EUm1CWqNpAmK4gcyomVImZ2U2zjFTNfQfJmytEQTscb+qP1HniD3PhA/2DqgZ5QxeXuQBseEZSua6krVaQU91BMWTUhaU6xVSQq0SYVF5NOth+glt3rEOvetBdHJ'
        b'qCbCkqmClEN6AUXdkUYE+wbdkUfMCw8J8Q6a5+sdyiE2tQBSd+QpUQlJmmxDmvZ4x0QnHY8ZL7WplzpZknt6Ak0x3ClqvGSKFmsV756h/3+yraf5UC1QosaJNDK0lIgF'
        b'9Zeoz6dfZTJzA5vZ1KIuFf9B/EuppaWp2JxytEmFB1O2GImsRxiJWMxLONbDnl5pAyJh6ELVWGkCHMd9faJzTdU/VQ6inqRtFDaLQ2YdkapBs/hnCp1lTL7oZwqhRQG0'
        b'+O+7P1tSCMvYgeyzdewg7efBsUPIZxv22TZ2aOyw2OFH5JQOLlcWL4odEWuXY0QhNCsMK0Sx8grTCqMKK/oVO7LYMNY9l0JyyYj2OzZ2HIOYMmQ0ahNyhFj7WCWliaPP'
        b'VcgrxPFi8tRA8s+ywiqB/8+KlGZVYVxhEi+NdYh1JOVNpHBftMRc41yzXKtc63gjBpJFSzZmwbEyFiw7IF4W6xrrlmNEITulwgo5y9LxuGNFF808Rh3B8NXi49LuT+wh'
        b'f/a9Qc2CpnvTfRcizHolqJK9VOmx7OdEN7eJE72oTOy1WRXrRReSi5ubO/lHpG0PpeSONCg4JPCO1Md3oc8daXjIwkUNojvi+d7kuzF9ZURwUMDyBmkaNR3cMWA66B1j'
        b'jrGbQD4axBNNWvV7XutOXytNq6Srr4p+O0jXs9Q3KJQDL/7OsjzJ5tazrLQTrMDQ+Uvm3J+7Lj09xcvVddOmTS6qhM3OVDtIo3mozjHqfD6XmOSNrrFxrr1q6EJ0CLeJ'
        b'LuR9SnF3+Q1ihvSVFkmxDEkHBQTPmxMQQZSG++NppefN9WU1JD8XRW2h218INSOr0kmhLm6TyHeyE9LCGkRpQSJmATpM62oa6hu0MMA7Yu6csHk+j1mUO9mrK3s0+f7U'
        b'Xg/OS0tWqeYybaZnGQHJawNVa1lJ7rQkcXdJpIINtCyLXv1xf2j/jbo/SG/nKeU9SqHTLe28nrI905rob3sV4skK8Ui7QK/1/3L3+46/o6V3DGPj4qMyEtNZ97Ox/I+m'
        b'LPQJXKd/9CV9MP1HBAcXyzMhJ95cE763AGsSvgpR8GwQ3ysxLBskgMiEE0S/vGrf9sNDskHuGFH21XQyo/vPfaJfCzlEas+dxEXzbP/ZBUSCFGaST6rR+mWALOHpHhkG'
        b'D3tLgyE/s9frObgTtac3nZOf0lqEBfXJSTDR9CmVEVhOgqDhBeUoaPEm2nwDk4fmG2jMmrsN9Zg1fXlWb8LWOB3jJif44b4nugs/xJgZqiHmVaQwugUmwKi8+t7orOi1'
        b'UhT2872VD7+NrrRH3uGpsHdQJVBHVuZUlykOj1EkX7wK+3k+j75ZvUjpzU6KR72n/w1EYe8b9ruecH/IE4+7F9Aiele6P7ux2vbFjUQ84VpN7aShDejvSXpg8sd6T5uU'
        b'tITktIT0LRyf196BHsOUNIsexA76TYkO9Him99DD0oHajR3oKeegdOn2tU5xmeji5qW+RX8x3W5ZN3arutTuX09hv+ZF99cwDgqhbpoeyAfePxNUDPWh3+5hHguvnhn7'
        b'bJHpB3BQZ9z3W6dulAYvLW1sXyAGCoqg9czrcbzTP+QaY/ijpnxmQmVRAXFR6XRCqTT8Zzq4FtQv3U/aPzXDknI2RaWpgwh0aCdY7yhC4+JoWzMSdSjV9BY1b06Y98Lg'
        b'kOURlN8nONQ7glK7hLJaah34nOit307imxDvH0bFpIZJ0YybRnFTG5D1+7u7jcrMUcFL6Lb5OvTaUxz6jRhgI5TC16mK08T12mIceOs0tyQk6cck4IgXRCTVsOCui0pS'
        b'eIeH9GMcT1KEbkpI30q0STZw6Q+pPN8Q+1lLZMH4pkclbmEP9r/DOfQ/Z9VQHXxAuhE86MxXD4kWzYP7qfppUToPgNAB8O7xbA8kln53LVZSH8cB6R613KTSTN9e5eof'
        b'EzVzYvd7GWNldFxictJaWtIjDOxUFjHuIzxZBHGT7EXcByepobQEy/yhQSKI8ZTIPhwPMNkqYfOm7pzASushYnOscuYxDyxX7sLWYIYa6oA1IhpwekE2kKm8cEOJbVTl'
        b'hSLsIF+tkC8VzDBHDLWkvAHBHO3hOtRhlb9uPhcDMoXiZQ9B2Qw08BMLk2GPOebI8Iw6m349tONebgf2Hqe2A7fN5lbl9jDYTU3H0AAHufGYxjeyZBtoiBqhA6XaXRNt'
        b'rkuKmVkIBVO1dw4Kt7cnDxa5YoEMrzgxFE0GDupMbXsHB4qwDM8sYL22CCqSOexn4FgR1AhYOkCdQ/jOVJ5DuGhdUmJ+ppOQMZPW8IaXgy4YqI+LXyDmkya7hmBewGIf'
        b'SQjk0xQ47IT6LTRFY5wAN6VyrMYKLEn4++1vJKrjpJiVnx4ZV+xvArMt55/ZduCnscvlSdcPrLwVOOZA1nNj/2R0S1ExvbRs1agJlxdONftqUPhMG5ucmiHiMXDrZNbC'
        b'zr99tTXk3W/vym9t+nL/8y57m9+sHFkX5vfy3yb5eoZ8/EpCyt9b9t78+qXb98bOfzn+6gYrywdJk34dO+D9L3ZNtU/+2r9iff29zhFPbhy34LMhX3337IqfD189/W56'
        b'/fPy6JLxa24qE12/r5+kNOPRD21Lxjq6OLPwBrdZUCd2wzq4xtH7OuHKOA5TTPGVnWjABuT7GwrmIRL3UIU68gJOwzXHoK2QpxN8Ic7Ey3iEF3IAaxlanTr0fQPe0EIA'
        b'nsUrHM7wJOy14aAhtZupjXmmES+8ES/Bme4JidWTebw3np7HbvBeI5P7Q0uwNgpeE4IxH/cxw63bSszRMdziZU+14dZ0IwvCnQa7sUUfMiDk4LWRWC9FmtzDigqFpu2O'
        b'LtiV7uvUE8rR1Z6Zl5caYgO3sWOHRBstX4ll3DB9ZBgcJy+ii+/ysunkeqBowYYk1vyEnVhB1nuASLAMEUeL3KFqbg9oCJN/y+6mhZub35/utN2K290eSCU8ppXifUhF'
        b'Rg9kYvpTTGNEGJ+xuVgsGtqPDqQGWlODz6wT6bMhb+yB5xb4ULWrze6RatfvwXbjnId3DCIYoF1/wFPFBoIa2U3fC7XMyS6PIfj2RmWjJqlQnzkhd6SUF/WOlFKkKg31'
        b'xdDyCFUasHrHUM2sndYl0pPBbqE5RAIEbQY71xdN1RqjGUfOzrWIt3jMPHUJQyiQvn9Wn944JzZW1ZMHWnNu6rHiaSWuvupnvMKLyoNekVrEkEg9vnsntfyiBbSi8ZF9'
        b'w0l7cxpySl+qkndLpem0F9PVMvtjaUNqOVbLevsohYiTXvFn9VDTRqkU8YnJUdRKoGAcrGqSyf4CZ6KSehC69Wa07a8WPbQEfYSz6XGbuQicruVo3chjO/sJ1iT3JMRS'
        b'+a27K7pp8XgbFPaMu502jclno0MWuLi4jFb2I1ny8AcWeBxFZ5MOU7O2ZE5FySXe7ut6y9M+080sqZ4C6tCsnjyTesuwD/Fe4E19NN4RQeGBc71DnBQaRYSTcfYbzsUi'
        b'jfsnZU1O4ZHXDylhsz7drh/204cUR/9oVT/aww/TzLQga+pZrbc0DdW2PiVOQXrFOyRoTkBfhU1/cPJjKnEahizeFVqSYjph1fOGrgui98YxHurIyKDkJLpTPCRqe3N6'
        b'99sZhS3to6hEGilNNwjt1I1PS95Iuio2qp/w6sQMbitbm5AZl6SZ+WRpxtIwHvuY5CRVAukuWhLpuAT2W9LL/VaMF6NrYVDqNlNN2Ry9Pi4mne8H+nWa0OBpU9zcFZxE'
        b'lreH1sFJDcupbi9T+enaJJui3nLiM9LYWmOrnZPB9qvY8RPJSxGqVqQ0FO40AH0LeUtiIll8UWlcneI3699bVKrkmAQ2CFq1LiUtmTKx014kXasebLIQ+LTX35k6BIeK'
        b'IKLgRaWkJCbEsABDqmGz9aQbUK9/7cxTM8F3E6rSw1phT74rnRT0yFbYB4eHKOlg0KNbYT/XO6ifdeigkyEwRenwGHkL2mitOdqtvhcl0cOiQHtol0Z6tcuRQSz8yBNP'
        b'jmFB8x14UBs0n4eXmRjEFKJzdlwhipyUYXp34WaBp4OXxi8jamXsSkZHQbRKOAidC1gckLM0UBvpFD4FirZgLnuTB9QT8b5Vi8JyEU9AVSg0hjF1NHA8HiXaKDQZ9VFI'
        b'sdAd6jMCqewO9UuwUM2QQMkzwux5tLi/s8MSH6JXdDn5hfevlnI6g4veA6BwFZZzxJo8c8xmWqkx3jBXq6VnfTMoa+vMNKjt+TZLPK77Qr0v6+abWWyvhZtQygQvN2ts'
        b'nq3Opo+GG3iQaLyzoMqCK7xwxC1jC+20rF2e/gyCx9kvmKq8vBADPIB7TcbZQoNJt6Y5m1T9CLlw0gr2Ej09d2YY1MYuhvy5O+EQ7IZz5OsU+blvw2Yog9Nzo9dAwdy0'
        b'hMWL169JG7cKajassxSwZOZwOIKVcJFr4sfEkCWnoPZleNCUKADYJXLdlJpBZeeJy7Cpd83OPNFdOcy3hfzZsD8a9urUKoz87yRW0M80pivSAnMVApxfPMAGslfwqXQG'
        b'9g+TZxpDLpSreExZ5vAMGkgC1SNDtLq/cokacyclIyMMy1LMLPBAmLrPdcwC1BpAB0aDzMGQaaB5u2twIGTDWaNMY/IOc8wbjBfwVHDGbPqarnE0dbc3IpIO6A99Kkxn'
        b'NHdZyoiWDLlmC6EO9mdQYZ6G1O3012UdKobzi9isIaX6M6QQMpWOpGO5gcoPCqzI/C7A8hCiTBeI8Gaq2UKswnMZVG5f5OhGC4I2yOpRmE+3NrpEt8xy2CuHCutxeHoQ'
        b'nIH6wYMkAtQEDoB67NrGYHvWRUMjbR9cheO9mibGE1hBKn15Bhmg3ZhDephF18GBaAFzQ0xDhuPpDMoGDKfwMNHWuy0xAb5KP2cXM2d9/CGaipn1XKKk045mWMH+NLyc'
        b'sZyOfBNcJ+9X4zss9uld+EOLxmY427v4ED9r6MLi+Wwur4EbAjXxDMM2Ru5C9iyshlYWoMPBbPaQLjrMOW16Eto4O8INdyijFIkJX83eJ1LVE2XruW2nAhdfD3prtuU7'
        b'I7Zd/+HojidFB8vmK+2/s5whCn/l47GT/N6vdNkfuD/67Q+sEmqvLmzeZmInqj85d4bwobLUcvFHd2eOqf/m9r88/lGzvMbHYX3gP+dat7Qs2Dno5Jf5k1+dfVTs91nF'
        b'oAk3P5mfseK3hdLX733wfe21+a+sSP2s3PWDRNWt0/5Lv7r+0e3F37098K6lp+Hhbf98fvFBv1fW7rl/9W/hu91Xbf6w5aNnDv/w0SvfSn/9bu+Kz0cOXX4r9N7mnB+G'
        b'rbBdfneWzxvBsoy4pSNPndn9se2xJ76+ffLZr4/5H7r55M+ii7Pmv5t9qjgp6PqtTeYb7a77znz7kx+sf0z55fM/Bdlu/+uT4xyXKi5eN35unHvpttHXhKV7Pwm91/Dy'
        b'x+u+CG1J3fLJ+7j33LJNZr9O+ySqIHPYhvZvvOa8XfLqW9Bmc+Zw9s15b0l2Wfz2+ps7zsx42mndynUXFzp/9a+fYv/yl+NPp//N4cOpqzO3KP7yxmt/NnCdEPp8veXn'
        b'rbcylxR1/Akvfevs0OD5bM5rR66vmuYW8vz5J4Z+7ZUyMvfojyOa5r/4cfP7LQXTv6p+MzT5/SV/euVucOOPP1kMjmixXt+iHMyjDUvxBnT5w+50HZoCaiaabMQydbbC'
        b'YajptkAFGAp2UMYsUGQ1lTMTzMqtUELxF04a8SBHuDyRxUaGzyLF6RD+1DhziIRGnlYEDdOiqM1nFjUUamw+8TtY1N3sOfN6k5XgcVPrVEkonJjC7oBGaEpnrCgcPyEK'
        b'cjmEAuzBE6xlloNm6kA8qI1blrOMtkEXsznthLIdDO60LUjH9gbnQjhXxT5ytufREM2lUOGjCdGEFrzOo0ILVxgwQNpT2OgL56WCLFE8muxCp3lwYiPWbWXIE9VQz6En'
        b'AqSs2kHYRUFnIVekQ5PBjGreWMuT83MzkVF6OEVO78u4IcXW2dDMajgMiqFaw5lEE+SfMKIp8lJSQ9q9k4xmkYtOeJKcaw1SQeokgqvJcIh3XiU0wE2K/NLDGgdddmue'
        b'sGbxkIkO6xxdnHcoeeZWndhtAlxlRj8ow3YPmvCe3ys3Ho4YSojYcUXmGos3WAXJxr0CCsOXBzP8qmAiUZjPl8zEM6ShrIdzyHFziOaVYaGXNq8MrkAhq78EKqATCl0D'
        b'w/CIs5LUYqZYMQdrlEaPncJs8d+JxdunwWisoiKjPpvgLmGWichUzHLWxaYimu1uKZZJjERWljS7XPpAJqHZ65Soguex0wx0GsUpU+eiW0psxDbkJ/03mOW3U9oKa5GR'
        b'gTnNPBPr2Bxp3voDam+Uis3FPBddJt46Wo8FrleiddCj0tG7TWlpN3tmrT3+EOhmkd/Uk0quJ4u8jFo26ULQa9nMEr6117VtPkZD+4/moQhszOTHA0SEeJk2rkfySLj5'
        b'dUrp/cg+6kRIXBLRZFWPsusxI4JacaFqa5RKsSww4BHaCeUxs+ujnTgFMdxCzJ0Obf66vI69AOUKlxI5qsm+D6AFHoELZoPWYCFDm8KjWAelPU56yFmrZa/DkhlMEl2O'
        b'RcZUYoBTYzQSg5cPL6ARSrFOtXESuZruQvZdl0zyzY9Goo9dYzB1Ku5nBQzBc3G0fDyERaQEO7KvBCXwRI7duJ8CTa+fxdx4ah+eC1xmKlb9UjX223gbwcwrnjPfQZst'
        b'VngkwgUs83ATiJp1TICbs+AaT7boguphMeka8EeionBv4A5jOCY3TlttQzHZGqheRoRvBhe53HOK42Q3pQOFJdkiwuwkT+aWSx4D9f70QAkyEGRrRIPFpngUqrkycM0F'
        b'joQS5agWi6W0PpS8qTGSXXM3Xh0aBecoXKUG/Y2IjSXM5egFLc7yOMgxS1PrNuHQwTvhVBoZoFa47MnyS9TJJenQwNo7gorC2LrenmWmqJN1zuNF1q74wZRg83A0I0wk'
        b'b3SAajzE1YcL/kOxddEK6ljk+lsgGQ3qChrkExAKxVgRTvbiynCskQSKBKNgEV62gxrW7Y1PlArDRYKN24QWW1cTBVd3h0jGCNQv4iYqGiFVePBf5gdpEBq9Z5ds8hT6'
        b'cB1rV59CUHMdDybrTagVtotihVjRXrGtcELLekzkyk+pzkCZZebEpgUkJMU1qHmPpYnkP72Jm6lVf7VMh/qY+WaXGMNpFrLMfJGwd6WTsUYUxgMsWUIUMsUTO8m1fE/c'
        b'mzl7QXyqb9rOJMgeIWyfaAmX5kAHp49cYiqQAbB3W5AbsV+2g7c4b+pgwYlCqdrVh7hPy+AAs9Bhpk4d6oENqCKC/BFJsM8CNjWSrDBHHkgUyPYUjQaJ1djE53QnWZil'
        b'cnLcnsD2VDMiH1mLpm/HQ+yVZ0eo0VvHuyw7vm2CoBSzAZ5LSr8kJ+fqQe2E2sTR6shZWgLN8knRTKmjiiOWTOBTtxX32pBv2WQ1mKUZCpLxZC4dDlajRA6AI1tVQdDk'
        b'gCekglguUmDOon9rRNeSEU0Duusj/fa0SOhDvk3H8EKPMaQtmDoP9sjh4MBMbLcQ0xZMW4/1fFqXr4UucgkPUoWFLDCocd7C4wHaiexzEltNsR2zsNaQLL9ycsMYOJxB'
        b'X7JVNQAKUuTk02JhsWUcX3jX4RI2yO0dHPFSAFkEqdjgJ16hwMPsqudCIu+1uvphB7lmYAbHYI+ICMLNfgmfpv5dqlpAauzw4+C4cP9S63DrGx3Hfj305b7sfXb7bG2e'
        b'iXpy6hiLAc/+9ezZUyW7x4zeU/DXxRsOdAZOHvXMW2lzTg02Hj8opsj9qbB/5qW+D4P8Y1Z9PewXgxyDDQhfHWlMOhOVeu2ln25c/HNnxpeeHdETftjacrdLUfHF8/4T'
        b'fxDXrHjhhdixJnf3vf3siDer9t+f9nN7msebzzTmP7fELmrDmpy87FOVqfc8l7lMW/rT/iH+4Z89/1ypc+1zW7xtbH8b/vHy7eEv1X17V1xwQOn94fdLnF6xWuI50Dbm'
        b'qQUfvrnSMv9a2oTGar8Vz88Pm3yswW7w/k0nTOqqFucc+ibQrPrpEckvfGoU/dqloaetJnkYbyhv/FrlMbF0/MTzZ9ePnj45/E91+yfv95lpkFk41P31KpvI3KyN4Rmh'
        b'MbcDYze9bBR9tfBe1aK39p0MP3tT3B44+Y3Edu+rR3/96NDe7RGN47+1bWvIK7dekXJ/07q7y2IexLx/sVH0a/J61XiP53+035A8t2PP5fUV1aO/c7Z/5iflK0e961L/'
        b'7mH4Ts6JEe9OzozeG/hj+dkXmtI77swteOqzoo33boWO+0EB6V8LHx8zj7fyf2CW7jp6+X2nmNbE/PSIL5Un2ndubGsIqut86pOd7fPvR34559U7tZ2yj0bF28landdm'
        b'zTzw8djw4vRdOxyX1N9punPQ//aMq1nfvfTW7d0/uJ9/9pK5m8fUs/n1XxGB4ZM5kXV1rTMSY6NzBzaXRM6sebCwuGHElqQw/PJI/D379Gkbfnlp3k9hJYO6fEq//zXj'
        b's5YzCRYOFzs++K7tmijulZtZNSOPNI5YU5/3drLp3fUTTq4ek/Fj+aHIa1Yz9hiF3/str6H24wuVu05t/aJ669eJwY2+JanlXR5LXss79HnGuJOyn2ZMCPSAow+Gv/Hd'
        b'Mtes5e8V3DD6fFzsFf9rT9kNf1v87cSZt+wmDNuyMX7npOo1Wz9S3R68dftf7pbMmvna3aArRe9kep0525HrteWvhwx/GP23924uula4xm5h0cgvPw8bNkh1r3j3zVue'
        b'X72+6Jel0QO6CkbcHOz07VdzJn9/9OnwTV4Pvv7b9BmV30VGGK6xeMdnVaDq6/HfT/5pu9/3kcZnvljf+NrKt4ZdibkaWm01dcbstcccUz5Kyt363rJ3XX/4JnPAxvzT'
        b'Occ98jKvVVstjYhPrHI6dOCtYYfI57XpTyyfNK5z6qRxTb+Vn86p2XZ67J+XB+SfS/6m4osTyqj4f1Qc+STY2EPlffzAjonf/PjRtrVfT5kgT7K9vbj2q1eMyyK6/qV8'
        b'1afr623Lvopa7NpVmrHvq7qE35Il75q+Jn1gkd10tiZa/OdDsuWnjT9y+MUioPyXpz5/r7Bs53PHbqeM8Q94/qfPP37wZOBv+7+9dRTv26yu3Wx4/KlM14uit/+6xrHj'
        b'02M/yLd9f2NYonnb4bo7t3623vHp54XPzHn769sb5v3Y3OL82pp7HSPtQlrz3/U8+cP3a0cc/SzX//xvprcnrjz+6ot7Nh+dZV74zjunN32x/J7/mVHeXwzdPrDerX7S'
        b'c08ZL17zq8Xdm/PzZ32g3MDw3KAskGzLDuRUrk/VsJnoUplsmsOU0ZAlA3XhO47DNarJhsBRHghycRJe6tb1Yrw1sRcWeJ6bAG4o8bg/OQXZ9bT59LqFm2TtQOxi2uJA'
        b'oiOf6Q4EwTaxRmeFK5EMhUMOHUQZpXeQQ+uaXq3VLI2XtZHcyvkqGVflfMhW01VCvYrlEmIh5s7tBjHclU4xDKOJTs/YKqul5D6tlLvIm2gWZnhTMptIXheYfjp7NRxV'
        b'uZA3O6cFKekx38rCbzBfIkyaBvl4ThYaBDysxBmuT/PXWCdk2LgzQuwA+0dxKtQavLjLP8ABj4vJEbRaNFUKx7nV4mbgVjIUrkSwJg/FLIJS8bjlWMbGwQIP7uhGfIMm'
        b'yKeQb1LYzfTd1MyNcsxzxktY5C8RDPGkB14WB0MtkfBYrE85dA7R3kCqfc6DHDJmkEfkAls4wANh6p6AM1gowuMMDIVhyy6Gw6z4ecbYyh939qVvP4dHTcRLsRjOsFkw'
        b'yzZJ5eCLJSlYsGkclmJpkKFgCc2S9FA4os5khUo45c+AVCh3cRY5NK+LJbjHg/X8ejgWja3+2BIshwZ72RLIEoyxg4JPXoQ9bBolYjW0qSgopDEZHQN7OCuYYIkYC6d7'
        b'c8jMq1huSmtorMRmLEpbQnrBDLokA/GKD0/cdMMLjpjjTSPRNAaXeXiZo/hVEWn4Ch1MRxelCXQss3egVg0rGwlmbcXjashOuA6Nchd/bFdSblEjKVSbi1fakCKYDHQe'
        b'6qBF5Qa1NNGDyglnJ2xmhU8l8vRFbCUNp33vCC3JtBUGwoDBEqhx38VNJufsFvj3ZPscBrvnT5bC6a3rWPvhwhIsV7n4wkVTe2cswD0OgmAukzzhSUaAljBGCg1yP+eA'
        b'VLjgQ+anSikSbMPM5dKFROM5zcLJtpIK1KjgIJxX0hreIEKgDR7m3KpBeM5fDV8Ne+GgrwFZgRWSGdCE7eztAzzgkhaq0TRJg9SINbiPp+jewL2eKsyBU74OSjG1roig'
        b'2A3qWNeswloiA650wEIDQSQXoIsUe4FN6RHTvLpNeFgp8NRoL+SLYTBWjcbCMXiGYy8yEMelcIF3R7MD5uuYp8jOsJthOG6cr+bGgLz1cnvSE6kBSnH8WjJZDonhmi8W'
        b'84Tjo3gqgzYo0FlExEZocRdDNZnUrayn5m5bIXdROpDhIjU2GjkiQZyAVSrWU5ZQP9ORDJALGc5gzMZm0lUWUCyJnoNHWaVXTcNz5L2pZBYYTCQi4hmynFTQzN66CrKG'
        b'yJVkebTSgg1GZ2K1CNss4Srvw0PQDAf8JzthiZPWprYNS/i+dRKrrFQ019iFWeMkmC+CU7FreWMLcR/U+HNjvQyP+ghyP8pK2y6wy9bOeFJFxiUtgMja0ORC1r2rxIg8'
        b'0sqLPo77WURoIdlQ6cy4IkDTWGxizbGdgblkbVzDHEq3QNRluCEa5j2BPRgOJ6ASC0cYarmbRXAYasWsD4NxzxAq21OMVLVw36rG31xL5mCJJnQQa+CIxihM1ibfBS+E'
        b'kpnKauwqmrxFMJkthgbFTMZvLIvAUhWFUOWrlemxOesCKDJ6vgQPYj1UMYAnA6xAspeXkOXc5EQ2G7Kht5C7bC0nwmGpQxLksia4QzP1cGquGoQmLBFhge1qtksvhurx'
        b'zMyaNUuNLH45lo9UHZ6j2GUt6ZnYSgZq3eABojUD8Byr/Cg4PoNRutditUwQwTEBS+HGTm6U3Is3I8nrTuJVV8y3JwsFj5E7IHcamx+zyH53ntTZ3m+Tg5js4XutoFzs'
        b'iRVLOKrVJWyLo8GvwdTsku8El+A0nScWYknsLHNWwDJomeOo2UHwIBxnWOMLSW0Yk/exKckqdmyRTZZukmSLtIFzRgOl7lg6ka+LvInpfJunvWGPx+Ewmb+4ZzTbY+av'
        b'wwvqTZJ2FzlEa8i6aiNzYjt2quGSk8lKJCdwANY5iATxEpEznDDiLL83TeCiioy4MeZvogN/KRZOkLcMxHIJHDeEGtbn3ps3+UNNnLOfBsMcCwexC+EhO6i5ltlqA+Di'
        b'TLFCGsJ2Fzr+s+VEvd6XYWZMenSUaI5lCnskIhM7VFjkjIcxl9TFWjRGHMW3++wU0pmsIb6pWAQHsNGZnvQNknHYAFfYBqMYj3k9YN0L1zBYd6iTpduT6y6LcD8DEHPF'
        b'gkAnpW8g2bvVmMrTiDZcMUMGJ+nc57vVWeyCm8zPQW3V0DBAba4esoOBFxtnUPQDsjF0A6z3wZ7FG1gnhGOTkevCGH7i1flOk7MbnVOTcB/beAeQNQqnPN3YDaF4ndr6'
        b'NXTWk8WkHZTNGkrhGj/wSyepyIRgyyx8mWDiLYZGuGLL1+CZWFsVnsUmcp1u6FUiKMEszigfQdThQ/zBILi2nW4okyXGpL17mFwZZDZBH3huKqn/eMgyiB8UxuDjMIes'
        b'okJNCyS4m71pALZTGLk8sp0y3+BFvGFOprTpQD3w9KRLSvi66oLLeFIOV+Egmf0CWVYdItLnZ8gBRC9Hk72wSo4FGunIaD3R1MWL/aCeL+dGLBkrJyN/gBwIIvLwZbIm'
        b'8doM3suNtptpU038AumMEa8nz1tDjgTzFKkMoRfLZhnJ5bBXKQiioWSFL4nisuR+bFqkCsJLrib2eHmxA9u1LddLoCACTvBduwhKsYwUemKJk4sL3QtqKEHBISJQMPp5'
        b'vLBU7hcInZhNtl2lyG6SE+uRINgDdSqy12O+cXeTbLAM2p2kXhHQxVdF0yyp3Jm1R2YbbSceSHbmeu5byh48gDHfBDmTFWqEexbSFVwVEcz6wli6SOXqgM0+SroB7SEC'
        b'XpfYBxq8ObrHYjiNrc5B3ECxbtkOcmbPm8qauwhK1ujCIM9L1qAgQ1kCH6OqYatULn4ZSrL+DfDaZsFELIYKsmN3qKnX4XCAWpz2tbCXbqZbmxl2SjzFBry7GhLwChGl'
        b'WvEoD9XmgdpDyJlNF/sC2B3n7xJIJk4b2ay3iGbMg/28J645m9IQbiKrnCa7QLTIHavCuEANVw2ZfY4BmQDlpKdgJrGrlAP+O6i3skdc56AVPLlWlsZs/cwVtITaxPS7'
        b'gnYJDkYMeJgDGZuIrBg4B4XosGYwgjIKaczCxo3UYMb082By1Vo8lDKZPxBLBouGPhAbDRUpvhNbWIosH0jFJr+JpRT82Fw0VjxWNJR8Gn5f/JvYjAIVm5InrH4Ry+jn'
        b'sWLZA3uR+a9i8rylyE5k+Zv4T7LpJgwemQEdU7hjkaXI5lexbDj5Sd8mFQ0n321+EhtbkXfR/5PfmtmQulBYEvsHpCyDh7ybXB1O7qXlcuBkI1KGNamPESnR/AeZ3Oie'
        b'+GlTfw2ECednV5Dv4+mbRTa/iWltfxX/LLM2Em211ePh4T2vw9X6qIHTSVp+lgzVcGpepNpiPz6mLOGjwbpepv7rQF7M8uQ7RDQnOShIKSXfWMR5g2kvTJO09QJLyQ6d'
        b'5+Md6B3KUExYCjUHNVmvRSKhNUyjvinuobP+P8Eama7toAN0Lhuo/ZtGYqlMjXf9i9TwP/jptmyqWGRuYaRBLSFTWuCG5QfWMzUoJDbsqgn5LJVortrtEkwy6PkOV8hx'
        b'0G3Wd4JOKNfa9cXCjBUyLIAWPYgkJuqfKpOHI5JIYo3Un411PpuQz/JYU/bZjHw2V//eQuezGp3kiLEWecQ6dpAO8ohEB3lkcLFh7Hgt8siw2OFa5BGKViLEjoxV/A7k'
        b'kVHFstgJWtwRs3iD2NGxY/QijlCME13EkXil/R0LBtPDyKznx0UnpN937QM3onP138AamcZT2icqxXek84JDvO9I5k6cm1ZNJ/4h+u2I6PFBP6bxnMyJvwspRP3QtN+P'
        b'BqJ5HUsBdadoIGn1PGGH4naknWZIRCHegcFh3gwFZGwvBI7Q+fND4lJ7Jp67pZ2lDX6cW921UBmaity36a9ULX5GzzorjXuUQcch7XVdEA5N56T9lbboDXqpv3e4p12m'
        b'9/wfQmf05a41COIBqvuJOMkRBynA396NFOMvPZT5iGzGQZU80wOOUNwvil12BE/YJAyKniVSUYnti5//+Xnkc9E+UbfjHf7ub1wXZRL/ifDtbttpHoLnRunl058pRVz5'
        b'Oobn4LqjxkB1YROzUflDdT90nm2aUBGWqdWffEC/FPSs3GrTa4U9JgaHlaEGrbi/44x+fd0Di6P/V7XTsXyRAm3QKIz/OtAGTZgaJXtcoI1YVmOKJECD/f+TKBuapfAI'
        b'lA3NUnrkHdMeG2Wj5+rsD2Wjv0X+ENgLvQtW//2/A+Wid1oXz0CISqLJAzQ7q59cI+1j+kBU+yBj9BhnNRoGPSg4wgU5LBz6Twt6FAyFpia/B4giIf5/GBT/72BQaFac'
        b'HggG+udxkCB6LtrHRILQu4D/hwPxB3Ag6J++mToGQWGMuTkpWNBgEEDjtJ4wBHgAiwPU7LvdwclwE3PlWD8+KaEQFkhV80ghry5d4Rj1SeQn762LX/Hkm7deu/W3W2/c'
        b'euvWK7feuXW17Oj+UXsv7RlzrGGPsrDzzdqccXsbai7NcMt33zuqOrvVQMj+q9li2U2lAbffn8BrcFENFIBXB7CA2iQ8zIxsSXAGb/YCCjDEHDjEkAKmJ3EX7dFgS51U'
        b'fKnLALUDds9qZkJRQDGDvQgQCaMgh5pQvOAqt451+lr0CIO2C+JZ/iOhTRMB+u9Ew2oz5J0eJeIs0M2Ul+mTQH5/GrzNY0k+n9k9XPL5vbnwaZ0ijQymJw9+rqGgzoPv'
        b'8yZtEvzofs64PonvsodH5sYY9loPcs2aoHFvuYa9pDM5lc/i5WrpzJBJZ0ZEOjPUSmdGTDoz3GmkA4O2Q5909vB0dl0t8f+JXPae0F5qkUed4L2RHBI00/Z/6e3/S29X'
        b'/C+9/X/p7Y9Ob3fqVzBKJCeALqvZ78p2f8iW8X+Z7f5fzdGW6JX8rDivGeYZQ64/dJlqcL6GiM09UjnGF7XBO3ivV8MM3TQP9cH8YA7S5brYxw+LGanYUgqQZcSC5+EA'
        b'FBrDVTyNZ1hqA1wwxRNaHLBayqGrm3qNl1JZzLSx79pheIAhiakTvqvnZ1BXANRb0xQNtceaI3RBCY186I3SJRagHI8bYxecmJtBBas0yLXrzijFPB8ndUpHXiAWweEx'
        b'nHo1YoLRHLM5GVQwccZmPOCvFXqjQrnYS/NjnbAkkAd5hcgNsXguHs6YI7D4ryvzsDCQ87iGL1rqvGQpzfL1CwyAhjAfuOAT6OLsG0iKcBVDiwSz5ROhMCRUsIMj5olY'
        b'BzdZtoXLAMybGa3ScmlI8HSGB20A3sCjmtLxHJap30DzVlMmptFkVZY9LhUiodAQKtMwl9Gaw2G8ui5Uc6d6rML4E+qqGkRhm7Ay3hDqoUbOKuFABqZEnmZO+tEoUDJA'
        b'NHNKBosHhxNQF4at2LFJJaHBPPVivClyhEPYyqLqB46UCkbW4YbC7MgApddSIeH+jsMi1ctUqgoyCi+9ZAZult5/zvziKV/Far/TkSWTnGannkwZm3OkImjeoVNxu2Mt'
        b'xvsW29dkt+blrPvyxle/PhgXusD4lv21Q1nhXy579++Dy+dnp1VJyg69Zvr2jeBFxX93cDP+y9B3F/1dyDi3HZ+aP/eFT+dIXx7x04Fn/C1f+tFywqbTLzVPv2cbHzFl'
        b'+ZfXv7vbMuZiVKC10YXv/cN+u1V8ttNK9dLMN5f+sv3j1R+83ZL26ZCPPoz48zNPpKq2vJ9ZVueafD7p6rsHardXhHoXPNjw/CI/r+c8Z2bN3CHsbvZLbpcrLbkLvBhz'
        b'42mcD5zAXN3kT+zCEh4C0ERUkXrd/E/IhZNqCLITRMdgOAY7hmGui7+W5OIq7uZZnHAlpTtFEy/CFTXNNZ6FSzzo8Qw0jdVVT4geU6iGIduMN5juE4HHpdp5aYA1eIRz'
        b'DEOjhPmV0yWRIVDElR/mPCbrkj24Ds9gdnf0mgHsUXN074lhmZbpcGA+7oPjNMBWX3Qt7sUaNVsdHJrEG4Jdi+gKpmFY5nhNEgAXdrJgjAV4No3yHAdKBMyFLsZzvBHb'
        b'mXLmY4EtU0j1J/rRHeGigB1ToYV7+s9iFlaq7cmD4TiPecSsgVx1y8Xd2xz9yLJzUKn8mJo6cIIEKYs4j40aBQ3Y4giNWKTGoKN6ZQyeTWesieehepi+RE2J4GZDdpYr'
        b'Mldox5t9Kejk/8EUyUWPUgpTWKKkxIhR8hrJZNRbLLJWU/pSvzT9Mhebi420SY9bR/ZWq/RnNho/TmZjd1KjQf9ef8P+uXD1JDB6P5ZOel2hq5M+qkn/pRzGtUrp/dWP'
        b'zGHUp8z9oQRG6rrom8A4JoidP5Z4ccbD8xf75C5GYrU6fRGP4fkMGom+HgqhjKUv1j7BMxihWYieN1MiF0bjeQnZzA7AYZ74dD19G8O1xCuwT53DCDczmRixbhRU0mel'
        b'2GrJkxPhKJ5lh8QYuZgnIGaa+/qOjRZ4otFRaIBOPG7voZuBCDlYzlMQj2FWHBzM1OYg5s7l0srRUbgPb+JxVSqN6iwRIB9OBrFHRmLbysWjHLuTEG23MEfWQszx9d9K'
        b'4UV4HuJgsWmmHS8sC8rI3tE5LLQ7B3GlM2uqGbl2KMw6VDcH0ZEc+ww+snT0DjF0ybXpgmbuGWzPy7Yip0M7dugkBmqyAldZcLibiBJ1UuD2EQOnpvBsuDhhNE8KjNpj'
        b'Otp9PP9lwQYfnhTofU2WPinm30sKzHm8FLKrhropZD60SW2OWKmmLnEi22qqbyAWOOH+uXBCHWSEByhXGY/xU0K7ZCIRcfzhALaq5KTT5mGeRZgv5LEmmXioUwFlCY7C'
        b'okG8nd8qNamAFcErzCM4eMY0UuLJvqmAsBf3qyTBy6GUM7BV4SFyNF2CKnl3vh8Rq4pZwVZmnDrOTfa0xZSNGYJSxAbPdgHW0xBeqQmcYxG8I+X/F10rMeqdnWedAqd2'
        b'ZMq7k/OwA9p45uHNgSOgAIg4pknOs4cWNitD8IKU5eYZ4nkoVOfmyWZl0DTnMdgsI8v3rDo5b0EAX7L7ErCW5uYZYAFPz/MTr0h1ZkvQxIvy163C3ZrsPJ6aVwMtCVea'
        b'siWqKvL68MO5GWH+qkHe1l9++WnNz4dyvvZ5zsxy9prdF/NmzzawPilev0g0KHD77EK37OkHjT9sXPuP4okr4l53Wr7stdsjL61a7LJ8mcuqzsz3LZqd/vTVkS83jAtx'
        b'eenod0e/OnJ3x/3tb+91OZm9yu7amKLhz7nGDRjXErLg9YlD3rF4z9/x1TFFklPZlcbf1ZbJ2jpdrG1mlr1r5Nh6eO85eeCpqvFfmMTmTLl96p35oxqN3jjr/aJ79Hdn'
        b'8z6a3zDkwe1h7Ysnb9g/dWPk4dbRFlkrn3Q+t1G+7O7Z9aduSAo3jrFtGNe1+NUPvvI671X1a+KKXyMCrj2zM2b/byU/bn310ovG74/ZNarl1lPt3gN+HBZ1OPIfsgfP'
        b'DLjz4bTfNrQ+W76s4fNG/5pjIo+nIxZv/KYmtGL5htoLz729JPDw4ohrI9olttPLn13//Lur6/2Uqo76XT8fi9n25sDX1+QWuX1+I2T1HfcPf3nu5R1f5H+Wmlvm0e7w'
        b'8VK3n2s8hfjrMZbb4ILv8jev+72+OjXwkFn8P/zKayZ87HbU6/ygtOO7Z5pt21dj+1nWtiVK7+Pe9xTRFT8N/6Kssv6Fwe+N2DcidXJ8ue2mDX+N/Plf07wKu5Iv+Vcu'
        b'j7XLcP9z4WdvWv5rQfaxMzOrjWcFb9rtWv3iLzte/urLH90KPw9y22T1w4HDERe2bzTd27ZR8kJI4b++CzqxccKWLYoXPzjw//H2HXBVHcv/55x7uZRL72JDVKSjoihi'
        b'V5SOgqIiVZoo/QIiIoqABUQFUUQ6IkpTkKKASjKb8tIT03wmpueZRFN8Mb3433Lv5WLJS/Le/xc+QfaU3T2zs7szO/OdsSvwNQhZtb3m8L0Vpf+Iho5nDN6JK63dU7v3'
        b'pfztReu2m7y3NfbVRU/9EvTZIk+z9Tr3Mr1D2jXWTI1flenq9uywut8P7vOG345KeeK95RkL3eovP33/fv/KrzuuvaIWmF76i/pXVm/9xHf7NNvC/EltVY4Fn+6bb1/r'
        b'X7Cz8tbH5rVPz/0l8ic9n533/YxSta0bfgmalT/p93rNy7ferp6m8+02s7d+em7r+jP1qYl625uj9r21ef0Z+3E3V05IuN442+Ktz3dem+5y/7Wuja/jZ/TWo6DmqLjg'
        b'rT/+1ri3qiptQdeuMcfe+E39fpbsn7KJx6O8t9XFzfW//sOVzR/PfDHnm4V7dmqf+n3hpxc3Sd9+JnvsxY/GoYwJr9nHVQ9PXJf0otYYXjb++vprLXbod7PF9RvOvOHv'
        b'OPWN7b9cfCfi47ChuKWp9ejcskVzstW9DLTfHfPqWNMfzUrCnb/87fTK9yrH1NycUjv+1ZdOnz14TfaVr8b5lz7Tcil9Rz82qefKwZ+7/zmjZlHv+Nght19MT4i6qtHQ'
        b'irsZyeb7Voapv/HO4rs3kXGzzTcX9F6t1mkPd3Ta/9bzi8bt+/yz+mDbFIohw2pYJxpmsnj97EeI49CJqpkXRgk6BXsp4i1l8UjkltCVTFg/AXuNlXA3NOyjjDUM3Vhu'
        b'JnrJXOjHm1ongVnJQW8KyBs0GNBKsIxxVQWmFgSXfOUwNbyVHmTeri3otDeWTHYroWoEqAYdqIsK76n2qATVRspUs2RRpBoMx2cQ6RANQBcqlUPVbL3xbkTgLMQCFLqG'
        b'oNXcoVACPVj/PcJsSK0Zi3y2YHVBgVcjYLUa1KIAyxSjQ/aWC5XANAJLQyeTmF9vNV4G6ykwbcBDjk1rF7ZDpxPt6TLUuFOOO+uFOjk4rVcIQGVy/F8iujRVd4oKNE2J'
        b'S5OgbubBe9YuA8740RztcliaZBvTcLqy4DR7FWpNKTJNS1iXh2um6t8RXIcClsZAaXB5FsOlodJEWoMPVpKafKAdlSihaVcEEQzMZH77BSF6qrA0HQUq7aAeG6UTFstH'
        b'MGmoQSzHpPl402+3GYMuj4WGEVSaEpNW5071OlcfcwoogzYZw5TpChvToZw6W4ejGsxEF1G7TAkoQ2WLWOL1lkRVRBmFk6GeQIYoQwfNmVd7B9ahm+egOntVxNt2Y3oz'
        b'GOrhvFQr199R2xZ/M5zisXTQgwaYZtgoWuqqpYo0kaNMkqGStV8qhaEH4WqLYTfsEUMLdOdQyopQvj60bFVA1uRwNch3pVXMgpoNBK6GKuekEVEcHbBloLUJYjF0j9eh'
        b'vbQygYOm0xXANAUozWWdHKwJbdBigw4ocWkKVNpyrKNS4aAEepZMTZepIBis4+mdVah91cR4BsNiiLTdkM+AeOX6eJhGMGn1UMnUeqgCOdStFaptYAgLWCUquDSDRMow'
        b'HitQtSoqbTeqpqg0Ceyj9x1hH9QpYWmYWINyYJpVCpuHZXroJPkgKHal0DSCS9OXR4WSwiFjgkuDdjxvGTYtQUjIxPxCeHGlvyMqhQYlOE0BTFuznnW7HB0LkWrMkkPT'
        b'KC4NtcIe2q0kGaqUQrP1CDaNItPQefkZAxzwXJ+j5qMKTMveSbl0ZjQaWA0XZaqoNCNbNjnPowPrFKA0qzg5Ju0SHKf9yYYTk3xQgxxFIoeQoOo4eujiZRYRiqroUsDg'
        b'aNAyhSFWqqDTPmkSlnJH0Giodwxbps6rz4I6KGZHsMow70NW7BMuGOpRYRYPZReVZjdDO4NFHYNO2IsOwkmfB4KUQYd8NUZHoBKOKKAyalj/YliZovksqNZlvER2jUal'
        b'labR7stRacenUmTMbKyrtTwClOYFNfpiOyxQDtKvtEyQop7IXUpUGsGkbUJtDGG1B6qhlcDSJKh5CoOl9Sygt/zVoF1m5a2EpRnw4VCwko1FHdRyBJUmgWHUJEel4X2u'
        b'RQHOzUeFmugY6lGFpWFFkA5VBDTPoqg0aENtFJlGYGnrc+giOxkuq1N8DJ4y5NC0D3fYHPo0UZfYPhyVMq6uTnSlQS8GUJFSso6R89YMtCedHq/BZbxPkiO2pXg3IutQ'
        b'VDQqkSqqxVy5Hl3ltKBcgA4PX/rBq6BmsdQaHbdh6BqsrlpBdTZt0ksbepRIOGiPp0A4KPalfV4Ix7fL8KYIhRvwvqipBMONdxdD2eKNik3vbKw0MkIJhqNIuLWoj1LM'
        b'Lm+pChDOaJUcBhePB4nuWF0JsygKjieZBSgMLteCcgAqhLYtKig4rJPX0/oZDA6VLGXcujccnUrkfUZwcNmoji3OvVHaUMaNoNcUyDU4E0vnsi46ZcTMAPMIfodg1xhw'
        b'7cR0enKHClHD/AeRa3ByigK8RoFrlRm0LrVJpjImPGAicZAfy+mjPaIMLBmcolgkbXTUhaAnfWw1UbGtlxyLNGbzSsgXr4T9UM+6fCUcVbDHUIcT/Vp1VCMswdPmCttm'
        b'92TOdgsZQaopcGoH0TCroAYd9Bw5pIWL3uyMFjXBWbYs1IdBoz9mIHZGSs9HF6OTjLmvzuXw7todgFnpsD1edNtWcPrbRbnz/Ok4m6fBBXsCDzo8ZrwPOYJAVcIOOAV1'
        b'dG2IGos5/6Afmc/29Ot41I4GOQMT0U44mJoxgy7pJVtHYfew2LH7EfA3ht2DnkC26HSYoWIF9o1sUHDMWo59g1KOUaUBlaNzChgsnIFhBoSFqyso93ubZ+EvviBTQVyn'
        b'wUn6URZY2z8CXXPkqF8F4jdfRCG0ttOmE3yeFh7GB/tI8XlwbBnbCxtQsY2ij6SVRVPlAEMPTHdqs7oKA1BI5pkF3l8ewudNQE1ynCFUosH1glQFnJcEx9jaUAz7OYbN'
        b'k2kwdB4nrPZaRj+R2McqAiZIVXB5C/EnEgJmOgcrYXkSOEDfZLg81AIX6C4Sgi4jktijVarA5q2QR6Vs8EV75dg8unRYeDBo3uxA1qeiHe6ReBB7VHF5tVg6Ini/0Pil'
        b'UsxkWnhnJ6g8aHaga4qRKVx9GJWXtx0dEc+D5s203gzMsG14F4cjcmQeweVdhPOMTw/hPeYYQ+b5jWfYPALMmxLD+tyfBvsoNA9vjH0Unkehebuhj9H40lxrPMdaxyng'
        b'eQScN8GHmVmuWKIjI+g8bbwLHVbA8/BntjEBoWibaASfd3YHw+etY7lkUJ2tNfStHMHnKdF5Hj6MZC14kh4wmaLIo8LAeXrTM8h5S4rjch8nP4nVOArMQz1hbIUtcEOd'
        b'9GjMe8NIKnEf1Gmr+3+Pt6OwKGZU+COwHfsZo4Dc6YseD7bTUILtDOmPmNfl9XHZ8ldBos//RXCduoYc7CamgDaN+/j5+/TnusT1Ibjd74KYQeuM6Ru6xORBIXrmvCkv'
        b'xrU68brkfcl/CbN7Q3v+aJid+eNgdqYPWiD+W4zdfnWFU+AfmUF2cz+PQto9phu4bYJISH9HAbMTEZjdP3j50aSt0f8dPO553OiHBD+Yy/2P4HHXJfYCr6v2SCjctAeg'
        b'cIp7982XZJKdguQwk6LjSQ+eavOcDQyrJUE3HHjIb1ZX/q9sz0P4txBxhXqFZoVRnEB+V+jK/zaW/6vF/k0QxYliRKVCjJ3S8kTS52jv09mnu0+fZrrWJjg6ijtTi5XE'
        b'SGLUCzmS4btUCFHHZS1altKyBi5r07IOLWvisi4t69GyFi7r07IBLUtx2ZCWjWhZG5eNadmElnVw2ZSWzWhZF5fNaXkMLevhsgUtj6VlfVweR8vjadkAlyfQ8kRaNsRl'
        b'S1qeRMtGuGxFy5Np2XifWhwvR9OZ0L9JxnCNEFPqdymiVjmNfVJMGz1MGwNKG5sYW/yEWYxA44ja39BetsRvzXK5ae3DfuEBf0vi8KT6BAPeKd11MlJI/ggZe2b2TAf2'
        b'rwvNtkD+mjWqMoUFT+ZkuUTFk1DuGEexBHL3O3w3IzadJoNIySJJbTNGewKqJoZwsIyNit5smR6bmh4ri01WqULFVZH4uI6q4XG+QKPtiKMK/inEBcwrzpJmc5VZbotN'
        b'j7WUZW5KSqBOTQnJKhAN6mWFb0fh/zM2p8eObjwpNmNzSgz1Wsd9TknMiqUWz0yy3iRuJ95aozJfWHokUMcnmyW2cs/dxNHuYMRrSu5QyAbCWT4OCoo7WNostVU8FmUp'
        b'iyWObRmxfzRIZAxtltkSXEeUivOg3G0vJT0hPiE5KpEADOSwZEwCAp544ENlsqh4Ci2JZRk+8FPs6y1jYlPxAiuzTGEdpx6ANvJ7SwmHJaXIRjuCRackJREPZcp7D3gb'
        b'+tsKN0TZSYk3JNFRSRmzZ0WLVJYdNfnSQ41R3viXHDCmvk+Rf0tKlxAeLyJCnK7cjC3aLyngdopztHJFSjO2mJqxRXliuRm70Fb84c/8n4CQjZpEj/c3e5wLIv4y5n24'
        b'3s9X7j5HU63QekfGDI8OdTHFU/LRfqk2sYyVHjdf/wDaRMk6jyBUoqPwjI/EXYpkboCsMmUlqmz3mAQ4UTExCcxpVN7uKLYjDJqWGSufurJMPKeUS8ejIR2jXGtZXhsy'
        b'86IyM1KSojISoimjJsWmx6tkrXkMOCQdz8jUlOQYQmE2n/84C82oPU5Hzmyj3QzG+8uIyvTGmeye136wt23LsH3Otr/E9q0L+bLXfucSdmqczr5D3fapwx3sN8Ryfw8q'
        b'QxfJOWEG1hpsoR9KbNFxuAD5Mqx59ZOX4PTyyVRGXUON8CSMDMqHdtx8HhpAQ/h3HVyiJlynUBHXFUwMmpEO+5Lmc/LgxBOsoQev9+4kODPnHo16E3+8f/9+eKqYMx+D'
        b'a1wcmbg1XV3uZXAc+qJpUGZU4TI9B7UJnJobvwoKsM6cSWOzVxnGyFCxLjqwjZkVsGKpaWfDY+WrjJuJKiT2qBHV0obzFmyUQjHKx3c5wY+fA70auBKiMc6Aaqx6qdSi'
        b'hX9ByQRHnrOap2YVgCqoLVYbGtKl5DZW+yahITTIY723UQtXYkt60m3vNKon2pledliLRt32Xj5OxLwRjE5ojHMLYEFXO7BGXoR65PeCsP6uMVtIjplkK8okmpUdeYAk'
        b'+nBEZbDbwWX6bIHT3ilsRf3M9gv7N2gobg/44tsSTjtPSETHcunrCaiGV9w+iwbxfZ7T3iUkQWkqHWuUjy44sPwhnms8yYOrPVXNNstRNarQUzdDfVCaSc0WFfroDFMl'
        b'VzsuN0b9VJU0gkPkfKjIInMlR2PPVq1S9WdRJGBBB3x9fByFtAVQOw5dgWK45GSCLqALPsZQ7CPVIhk1vQODuNg4/TlQ6khZZ+kyMdc8U59wg3bLijlc5kaORqodXvKI'
        b'BoiLp7P3Wht0wBMdDCJ+lT5rUZeSiakrDdb/DadqoSI4raaGBjymQrUHtNpyHtuMUa0BlGGyE2betAhzeY9eajpmEVTrgi7x1tC9njmb9ECfllQjPQuPPlxOE/N2mAVO'
        b'U8bIJLlbUI92GnltCVaGO/gp6MoMBtEeRFXQI0slp7ycKFtTm4+EfLjEps7pXGtZGrqgjV/TgS60m58yGR2RRzbWRG3ovAxr2KRS+1C4zJsmBWfKD/u7sWorby99AWkO'
        b'zkJ3JrVAVEITtMvHHh2GPcqxd4GLmSQABzqJGe+AajYaP0fvgLWe7BX8uJyssBtr1i3ZHKpPlMLZFLSfrRKFqDxm9Mt2S/DrqxyD2WscKudi0CUNLnBbwtteO3jZHjzX'
        b'/6X9Q9JR9xSjJfrPbvvhrVvu7/9UPveAUbX+e4XxntlzNV11Pa7ySatOlhlsNX5ab3XDzb2nrnvaDBYXw9uTF3JNTQ1NzUsrKtYYeL905+ePTqz88LsXd/3e8+0734UM'
        b'DZ6tPZHZPjjdcnH+55u+uGO2bXK1+xP7BlaMT58RtNxw/J1VXuKxcz9oMf63yZ6yfWURM2afEz2pPnBvblZ+75WvpO3/ajxy7dU1oRqWhVbLU8Z7TB2fbftPq8MX+6s2'
        b'PV+mmyc7dvuXcs9DGer9Q5YbvHdMnOLiPvFt4+6yKJnt57lfj7snOrH/cx9k3nb5xZKm/V3RSwf3rvW9kWj3greV92fhti+0JCWt+OX6bPumE5uCn8l+efDkMjPf50Or'
        b'Gt7JvtXzstZXG/uczIP8Y183XXEjodvm5fXv317U2/PWtuTmWjOzjvS05tALP8X+4+PBKWGXO+OfP1pXdSr38/jXh6Mq/EykSdMab9b/Zj899mtktK5762qTjHDTp/pO'
        b'LG196bW0/YcSPvbcfGuVes3+qRkN7i1bC8tqp76xyNvsVviz1WP+/a7+HI+YcHHbC8HfdeZsbT4X8/Lamp9C1WbqX3x6fJrZbZekOVE3j1ufvWlUtiGqf2niOp2e2fcq'
        b'3tFe8LWjn86vOmg1cnGc1vGDyS21TWGJHxz453tmY8/Xv7qqvOtlvV97n7jcG3L/6vczr7554pl7E+vcXpDdi6j72fzw60khdTnPBK2sO/bU50+aH+65+JvZK1r/nlu7'
        b'8N/jNtT9HNTjOisg++1fF03Q1ppeH/jub37Dmibfum9eJyu9efbK67ldVeU7r27sbzuDTF2OvTftpfpXd55zqzvTuNQv1jzI5PlvYp59z/nd7hb7LXHmfU8//9TVAv1j'
        b'Eju9sXvvuBxZ+dSu78bOrjIIz9lhu4T67a5ej8rs8bR18sO6JZzlfVIWsyPwPVCAdtOgmPuJW3wAKkb7wwROCpcFvBTvQY309M4dnfaz10aDXr7q+PX9/IJMhTGmEbVA'
        b'kyKGK3QbMds4OrKU3a7D60odlDhTsycqSuYkkYIVKoZ99GTdbak5CXToHOAooEp7TpIn2IUnZJDDBegfMxO/Rqypvk5wIMB7A+oiNmHY7+zpYEfzTatzEXhT7kRl6+ih'
        b'185ID2bj5+JUrPzz5tOzS311/CkluIJSR8nEHZwkXJhsilgsUzhijS77BDh6OdjawmXUS769lxi8YZCZNi8aQ7PcycAQNakkNE6EOnY0ewguQYvCtTltnkp+Ze9keh44'
        b'B+W7KSJ5OXmxw8IdqEtuNicOd4pIXgvT2GHhNrhI31wDp6HQ3gs68eYtXoQa4nm0F8460FNXHWcTctbt58ipKSJ9+fKcBaoRp8H5HSxw3CC0SZWmOx/igw35qJgOvRm0'
        b'LcAk9vbzcSTnfv7kfWhCpfjhKeiYmvvcpbQVzzluMuhwRaVeZDB8dP0dUa+PwE1YIcYC0QZKgAx0EWqICfywpj8WmUrZEzoeAhrABCC2CXtUoAslk+c4+zs6+Ckaww1Z'
        b'zhCj03ijqGWnrmcWQqXi2DMQtaixY8+xUMIORQ/wuJIAJ28/aJju4OXHc7qbRXO3+tND0bUaMMz2aSiZLT/x1ZktUsfszY7h4Vj0ImoaOOiDStSjUBUn0RS0UWEkCwJ8'
        b'yhkVy+jpvCjeZSufOwOzB3lNQPvHKC2cWKpoI1ZO6EOnKANbu+sqzXRYziGGughf+t4KQwdqdCLWTzgWzqmhkzwatJd7UYhRSaLUyYceaDcsQW081GtOpfYAaN+op2q8'
        b'3JNHomqOGC8H0RDl6Cw4NEMGp1YQM6LchLgKTjAylmOKHlRExMR75mlqfkQXJ1EyJuI5W0lsTsW+Ek601hlV85iDS9Upw0TBWU3yRYftcddy0VXUw8MZFy26hmijvilK'
        b'M33YErjsbcXa64d+1KTwoVFbn4E/dlDg0VVzStpdUIf6ZYFoLxUFiLE3Q0Q5SwPtxcsPHlBq6J0He6it1xDOiVBJvA8LRFdhAp0UkkAtUdAB7ZwGnBTgQM5ORq5GLLH1'
        b'S2H3mMd49s/awCbCnng4jMVOZhl3cUF9PJybIKWNbEAnrditDDiOjhPRScLpxog8oGk7XYzQUThsCyXbslCvThoTw4yyiCBGANzO6JCnnyN+I8hDQxeaWRzMZRZ6Mnst'
        b'LBLb8qh1Pqe+U5iVaUrHzcsH9crs0+nB/lxUzanHCjMXO1GrhSh1Gv5UL2ICCpiMjtPEfmqcCWoTG+BpW0sHz3k5HJGSesn7mpZ4KWkTFkBjFFvKSqBqJqsCleRBKWZM'
        b'dU7XX7R48wbaq1ytMBlUwGFv4jfEo4u8vjU6zEycvXgQG+WmGSxInUZFS+xonZ5TAxTGGVQ7eSRwoho6wSZOCdZVDijcYlZqwlkPtvSgcqwVNcjgeCw1i5KIn4DpyGz0'
        b'B90n4n7ifnjh6UgXA2dPVDQGlYq4yXjezxkDTczQcn7NRpm/LXWYgnOogxj9OP3xotWam1nrl8dOlMkjKE/D2tgAKl1BP2g7XipllEicKAnvN0V8TqoB49ZazK277b0d'
        b'fRzhQIKdP15G9OJFUajDgyW9OpyyY6RrtnCEmdHwJuWvxtmGq2GVqQiGMqgyUQFHSUxPBV8EohMKCZ0wRoArFkDd4ZzEPwdVs3iOaBguKjyA8F52kHoBrZMyP55aaMS7'
        b'CLmLOdgJDVMmNkCDIjwDyqFZTo+ZUGpPdxpHyRZ0HM+hIQHK4AIqolNqRZalwrTkSFZiFdNSM/TY6vz3Zpz/kTnoUWEFSHrU/2Ds2cXFavH6AsGLSPhxvDYxsAj0ZP03'
        b'iZo+NfGQxFjEDCIRNOhfuvg5XX4Cb83b8IaCPkm8hX/G0Wf1qZlEwpvyprhOQ/yvLv7RwE9rCRLB9MErPPnRpeYm8q5Ejl0x5nNMVI+bHohuYKvGUCMfERPGx6ORKNr/'
        b'1ViIWHUjtSvp6UXctsn1/2CR2c0NWKvaZB79Hf+jaAmdGpw8WsLoZpShEmYoTr/p8bGDZWy8k6UdOQdzmj7bRRHH5eHICX+qe4Wke2l/1L0uRfd+Hkv6IT9KtUyIGdXi'
        b'n2osHjfWyt/QiIhmZ+yPbbNH2eYkCnWm+N44S/oaAez/5ZbJZ9ryN3QilCfIEQmPb75f2bz1EsvM5IS0zNhH4Pr/Zh+0IxSnin/UhQFlF+wIBWQZmAT0XFJ5JPl3u0EZ'
        b'0uKPRvyysm2noBQSPSg5LoXGRrCM2pSSmTEqGNHfI0M6iS7z2PaHR3OcSnCcv9eY5x81BsrGLEYaW+q17O9xd7rPH7X1tKKtdJKg+s9/wME/qvQfyg+wWfOIkEaKeB1/'
        b'+XM2M3bVoiEHIkgAgMd24YXRA0ajBrBJ+7e405YsEbTVjJTHtvmyss0x8ggTf7PFzYqlYVNUIjGGRKSkxiY/ttnXlM3OJc2SZ9kJfaKqie/BkCR/u1e6yl5FJ6bIYh/b'
        b'rTdGd4s8/F9167+NW1n4qLiVPPegRULkn/CZe5xYRkRTtY/iSATKS8MacR+8iLWgYv7imxq2PJXvDLHaydQdOGchj3VPtB04PekxcSdtFK4yRK7+j9LTLi4+x/iBPT4x'
        b'Njki4vFRJ0kDb2vIqfMfxYndXPuo2JOPbOx/OgLxf24ExP5rEvbd5wUZuZz29Xs+UdrL++M+8BVx4mm8zfdXRpjtYRp3c4zG6UX8Q8JLRMSmlJTEPyIgefvGXyDgWe0/'
        b'kshYa6MoSHpL2iQMxKytIwE6FYGhmMWV36ejtLYK+9UwbUWYtoKStiJKWyFP9DjuJj53JCWjyyjaTmRRWVdbQZniWB/t5qFhwRQ0BDXUynV7kpjTmG9D7BoO63McORo+'
        b'Q2elpUw3XZM83sSjfVDnFDSTWkFCtdU4Dd9dEmIT+ylqBZdJfDu3o4tokJ6KMFg+iXBx0Af/4U/CXgSuCnQMFrhwuAhDi9WxKjWUzSJ5tEUs8CFRQErgEDnrQqXW7LhL'
        b'jbOLVoN2Z3tmkjg3DXoV1gptHhUti3RFR6nJKs1d5AMXElXST1AX3qwcZtA6DXtQJzmwIcdKnNiRH58MneisDsPw7spTAnthnw/KR1XQQi1V6Aw6tJhqoXb+RB3Xw5P8'
        b'SLwo1gYdWsMsXZenQrP9GpKc46Cto5eY01QX4BA0QyOlnQecRxdZLBCxmPdaCvVb1tJRsMKKZI39gqVOXg62jhJO041AZBrNmQWlfhlWfpXQHXRqA7TCWXSKvjhfPwWV'
        b'OPoTlTEESjhJmGACV6A6kywsqHuyiw865EXC7PmiEl8zf0J0FmLAfoEaKkWlOg/xpFTBk8tHeHI0R/LKAGV/hhsfmunUK/UhbnTypxw3bwXmOI6znJ51x/F2nLY8fewB'
        b'dAXtl/knOY/AUOAqqqQ8MA1za7PMC3XnjDjxulrT0VqHKdEbijpUBwwPFpyFJmbcPcGPkfnOnk/PD7fyucFogI4StM9ylPk6Yw73R70a/Hhog152o9ptCsUNcAL0pBLc'
        b'QIMdHQUvVGmACYyuaqjgJsInMZYYRt2okUBdyqByBO4yEV2gt40lcHkE77IUqsUU7iJC7dRsTRPeGqALzqgaXSXb8CRuEvSNsVWjXwiV81H+yNtW6Bx7WwOOMnve6YVQ'
        b'gO9vjR2BnSSiqzSnLEGqDKs7PYR2gXw4RskeinqTURF10fdWImlyUDPLn3oMHY2wx80SNM2BXD8nW0dvPx7zcZGaG9oPRxgeuGWZtRy+shjaJAy/sj6d1i7D49Ygd43m'
        b'OYmGQLKzmDkE0PmvrQGXHkiAEh2q4l+tPp4tE0fHZ1InfF96QkxWFFtrKKbnJ9br1LZmT6GxdlB7hAmxWMi9yyfZPMq33B/y1dGRVYHMfFqESmfJUlG7o2JtidyBJxy1'
        b'LOyGvVAGTQt9HlxbIH8RdfnLgcpU1cWLrFwTbZRrF+pApWzwDkPPZnpofAX1KtYhvAqVoyOsE6XGqNbHcZ27EsEA9VDBZgT+E+3GE398uNJbHy+z3XT5ckyRKJYEsh7E'
        b'wCGTySyXLFzagi7jlWQStCtxgOlwimVp7dtshlmY50imKn4uhw4F4X5SUMwEKLf384YWkjlIHMXj9TAfzyBqKarAk2l4MwxjHvN0dKBIz+NCLqpYTu3waGgXL4eQLLJ5'
        b'wLOdR8O0T0b+aFgBM0E1jmoUZuIvpZSUuNiprl9k9ZpH4HnKBUw301agBElBPSQaFLqQRdJdH7VBZ/FavQNVs22icEuiDHVLcMNlHDpGokWcQC0Ux+66CarTMtBRCcc5'
        b'cA7owji6k33nKuXwfNeYvuL38afmRLHYAbmu8szWwVu13tGYxy4uDVCTr1dvWlk4hrKL5u7y0APW29IjV8Swi03TNDl9EmJhhan+gIXPwyEWqDxI/iffk8uF6e7kc/lU'
        b'7RguGC+oaUKMQu5m4o48yTKf9YC8fUNzfnxscmx2avrCWE35AismUQBCKCGmoasy+cGnIzQqDj5JHiYS39TByxGK8R+Vo6IsoKMiTN2jhj5Q7qK/yRW1Qut2aDVR88ji'
        b'4MRqE9STgK5kLqbs5UryESFirznq6ORFwSbeq1c5Bns+MIpkCKFH0IID2TxJad6mHYn6Amg0htAs1I8XbFtHVDxi+OE80fFxa8XQAcXGCfObTgmyZ/AXG49bFRs0kPzO'
        b'Yv3asPJymy+uJj7/b8f3X/60pqjY2OmausY18wTTmV2CdpUkUNxzTFTgYfiZKHTVIoNPxh7MXdz2xpIvchfH7evd9GzRP35473LVP2sbP/poku+7p96XbJqTb2tuYFZh'
        b'/tzZ881lz8942Su/rvxEQUNR2mqbOYU9lU/F3OPDKp6vLtDvPRX2ZembjlNXLnol+7Ont9dO3DBcELjHq93kH1XRZ86XVFT/ekbtxqnkn/h3P0/PvCh1k7Ye7S13Onp7'
        b'3TPPj/su/rXi56L8121w1P3A3Lcu+0v9Qz+37Fb70u+pS2f2NC8sOrDf7kSARXCt1pJfew0LXpLmp59cM/nMxhtBp5v9zqKBlLWLsw91Bz65yt8jZOs42ycu2+3qr7X/'
        b'fn5bcXnKk9OsV6Yv83klrLr2nde+7Rl6qyfxVvD3r4wNOXnTcuJnq7Z9Jzx9Xz98+sKfjcZ89+qZcTnPgtW9tS6FsjFmId/nOb58u8rK9Lum70r1PJP2ub71r+uG7ef3'
        b'b1v/5ZGQN154N/PQXa2Ptz/TficvYH7Mtn98YdFev3/bhi8vDL68XXrwl4M7Ds4xd07/we/K0wPrDl50u/BU2Xijce+EvPCUcKX9h3sLdxZMdfCr8QxZIL4R/1zyU8kV'
        b'C37Y/ENYUJ1HQtbbdw/IQqa8sjNrTdyh5x2fzbtzpkxWlin5bXFKtV3wTzUvZ/v+rPV+WixnW3fptalPT7z2ds+852dEL9je/FYLvLFJb+utpZ2Hzy67p7PVa5nahmGf'
        b'jtaFbnot/d77rku6n52z4Ysjv064fusZ7kJx9eSqn8un3Tt8Pn4o45V56wN+uHFv7u3EnWbH/xlyv6Jjx42vrW7nTY/eOOnsE/Ne8Q/MGl+ys68za+G1BN1Wi1eKW9Ku'
        b'HZA9F9RX/bJV7ZNvGGTtvTarq7H+rvbNu+ue6d36+pR7Ne85JgZWfn296YtFXQc6G29+M+Hm4mdePvLFLoOW0t1fbnPu+k0irhnUCi9Y9Kt0XLJriHerrRu1vMQbwxBe'
        b'7NDJsc5wVkzX5strUBOzMlTiqVAhJQAxTRssO2MJ0cAZnYUzIqhBZaiZmaQ70N4I9wypnS26wFBAY4Vg6EYVDOhH8ohTkyQMGDBEaAI0MpvPcXcO9WSgPucRRGgeamXW'
        b'266tWC71gna8LlBrNjFl+6AGdrPGD8/1HmdUYKSCeVSzYN0pziWQQ98Z81RTG55E5+hdk2nQHBNBvyjN19lWwungh6xRw3hmHyyHvdseSFGIe4537wFmUF3BaAYFUIHO'
        b'yJg1dTmqpQbVraGs/WF0aIZMBcmJmh3C0R44TE1QqHEjtEspBkeQwvAafmGuByPGYARJZUrspTnoCkM274dTzC+ifS2nQB5LoUiQA4+hZwsD8AxGwm6ZkxU0qiB5Y+Uu'
        b'F6tQ0XqZLxkaArSCCms1TktbgIYl+vRdg7WokaLQHfCuBx3CMjjlQhIr0ptBcHhOyiaVxLUkOECTHHgMR2fMkI5GHTfDIUz6q7GsVwd3wQGpCma5di2qd5cbndE5rAc1'
        b'YEIXrwkhay3e4dx4zDM9roy+pWlucHC2SibPBCFh1yR2r1bGh0fKULGXF1ZpBE49TbCDpk2MMS4FopNqUDWSpt1bCIE+Z2YNK4TWCJJUMI3YbFdAvoTTWifAIDqdylw3'
        b'KlAVGpRCayo1QaoBMcHjiXEedqN2NngHvUJkzD45BkqN+ckzgZnqsHa121nqjaWjA372EqwMDPJQtgb6qKE2AUsOJ4mzgKaTj5MWDQR3GfaaQ594DjoCRdTjIQzOQaMc'
        b'g6bEtM7AbWDBGB2FcgmtSXc9Kh+VhhF/YQ6cYfjTZabyZLPQoA1NuXLQ5ghic9ibdfXgRixH9YxAzbZ6oWPQOZ1BG/v8o+B87qMiOkBjCEsnG2I3Ap/Vx6Mux89C/0SG'
        b'nz1iAi3STBhcqkjpCGfnsjE/DK3BBIxM/T3UPLAghvWSUuifxdDRXagtAvOLnkoWwMGN7NZhN7hCjMZ4PWqVx1M4wTwx3Hctlo5giNFeK6udsbQ1DRhKwpp2oWruQE5Y'
        b'jWrG0ioTPdFpqZMGqh+BJy5HVSzF5GlUtEklbyB+c22oHJ94CbVQ5wbAeuEqgiXkBMyEtvwE3Y2UgCZYsH8ISjgm05xACacn05ZRM6qBLqkSRmi4ymg+OkBZOzEAS7VD'
        b'K4l/LOZC/L3qPsIkzVh6T+aJ6lCPAzRA/wiyMSuYUXZ/BFTYq4YbgT7U6zgHr6Xkg5LgEtShEgd/vIKTSPHl6DDPSfFkxrPwGF5SiVI2O4FIUA5E8EL7PeFCjhg/cU5A'
        b'p1DfJjYGl1A11dmwwBgELdDIr0pFjZQlsOYjtg9wQMX0XCNylzonRVcxXdC5RMYSe1HrJqkdOoSpNTfaj58FezEZKbPuC4dTRmMYxVTccELw5kHIGbiDuFareJsFxiid'
        b'zc5OtzX9/w3uesCC+t8HQLyhRZAzEdRzncrd7xEp/D+fw+7ijBk0UUzBiuS3Lm9NLdcOvB2xN1MYnxZvyOvzAs9szwTWp/27tkiQCN9q6dnwpryNYMjr8uYCtWHL8w6y'
        b'f7UFC2KhFog93JDYuQUt3pzXF0i+QXMNXYHYtceJLKg9G/dEsOS17ovJ/4LW7/R/EalVwkloEH9TBrIUyNlkju2DVmJCgQin+dSmJFvoNEIRpmGIb2hmZMfEZkQlJMpu'
        b'qEdkZG+KksWqWMH/RloCrLX8Tkx7vynN3r/iv0RET5lJBuA/H7Pu5u6rxmXMJAYtVBADl2Qqbj5/TaWBowacK6rSc0DtMlsRO7c44mcsT7S+GEpYQBsN1EnPHFCNJTri'
        b'sxb1ejPPRoWXE2cBp8RQMg8rllSEKYZL81S6EMCqg/0x3ER3Mdab9wVi1ZXMaO31aFjeGJRtYY0ZGrNKjnrhe9CImh7dGJTOy7Qnz/WI0R57Eguh08bTz8nLb3UqIQdN'
        b'okEiFPBcJGpcYaIxJXcpPf4cZzLfR+lAzXPaqGM9cbc/lUhDNEL3xDE+TnAZlTpiAWkNrWrG7NWe8vA+86ZIuB3O1L06BTrQeUUiD5LFgzVro/ROVONCd6XCSQ29Bcns'
        b'RHIIdS15mCqob7KcKi3Qkkk8IKJwfUOyB2pby8ILb7Sn30VEobhdGtAUyiXcPWysJmvAbLvkjSOxQUPJRkuMa6vGn9/25Xf2eu7+YL84W315rZbHG56exvsjNUsdZh0/'
        b'GH2m4UTC9GtOfr0mzZ5Rcyr2z4x4wmzVvzVtmrKeHtgWZvlax+FXBn54Vxaf1XPSRN1KT9csfG7U1I/fD4/70PelonX+N57YMll9y6/XzwZsutQTI0xXX1GQMKHStzXy'
        b'nU12izw/ePWLsrQtwa4fhs6LhZ1lZetiZi/wG7BvsTPaKoT0Oj/x9Gc/vjh+xranXgy2jijN/qFWPy5YouVtEr52+trq3T4tT715aXDFi5+ZnRp8c+HisMUmp6Rtn1/r'
        b'nbfONfH1L0IPLX3GIrfgp+Nhd28kDD3/hdOthPQ664yktz8IST8deqh+MDC457ZI7deDt0NkXhZbNvqc7//y1XHT7V/s3el5yT7dzW3bpHl3e8eGLhu+uetV61Mvz5xW'
        b'y338+zXHY63eBWvOnJ7lb5/gaJJwJWJGe9yX0Z+8MH/nCys3FL74zp1vppWEzToW9Hn0J1cr2tNc7N0XHBuwmOrkmtOwM/aSptOFyi9NBm1thn5ULzxX3N5wq6J/Wd7s'
        b'HOFTu9pn0yNq9L91roqInRB/fKruoZ3vvnbg3ptWBe3fn4tdEvyFT8Fz57a89Ypw5uoqj4+sKu9l7T1f4t0ceOLnj3+cN/QPqxnX+l9Z81p+zHPflJWkzx6wmX//fH57'
        b'zNsaKVv2vbeq5onSf/r1zKjcPn3DB71Z30au2Xbj7dDSrOcL7gr/LH/P8ROfnItPvvfkio6oyuZtF5/4ZmCORuvJVU9mFp0fGrzyvlnvt/lz59/VSXz9xLWOHzxf/TSl'
        b'OWriB/dtK+Z97eUyvOTmlMzr1jefKHm/e3fv/Lk5e1Z8bDg0Z8fcZ812XPrB+6eWlIHjBgUa/oteOr41/bjs3ldu70rWur/Lz3tl6gKzT/LHvFNjuX1S89wQN63SbKeP'
        b'Lu7iM2X6Oa8Z2k6nvok2UJM32jXxQcdE0+3UNRFLKd1MjK/B4qDCExL18X7oFJxDJ7KZLHMajovJMbBcc4w2hstuO+nWvgxqDIgv3mpUxOKXyV3x3KGdvVo8zkHhqYx1'
        b'u/xItFcd1bHQFN2wT/uh2MskOTBz0hStoS0Im7E0eQGdVJWsqVS9UotJ6yWQ70FiT+fAIRZ+ukeXyiPrUD+qonL8yunM0/AEVktIywvmRihkEfLFqJdIJN5QxI1Hx8TQ'
        b'6wRlLJLcHriAiqVYx6BRvHzioQ0LVEYCKkCXUS/TAltRbx5x8k6z5fFCdZJT28ajGrRnARMfG7fbySZryF0RYQDVODHf8P1YVR2WyUOebbOF3UlYvt4mQDsa2slcL/uk'
        b'aI/CVRGK+PS4nOyZTMoqQ42wD6tMktxATljHu+MVkvnNo32TYa9MH/Uro5HByQXMDToCqz89SgiQhNNFR5YRV9bLMExHX4ADWOWwo+svsX9Yw3HYAydCKBnGoYvCg6rC'
        b'5QiqLcTIybAIr+YVCm0D6qGY+atPX8+ivFVISNycjPkjyaeVDohYZWcOmMciTWRQAydGCcWoE44zbfCcJgzKNQCo3EUDCaEyN9p49jhULCOx+4mjqAha+ZAkvAGcQU30'
        b'0zaP8yWafilRxUXQy8+BIqyo1ZlTwqitRoekTn7pUGbGnsnADRsYi7a4QQ2TXKuw7lYsNYd9uFOMdho6Qgzu11HGInWwF4u5ygB0WHeXyCPQaUEVnYubg8xHYRYeBCyQ'
        b'qCIMtBAhD3gOZ9CxzUoNFm/PDXIV1mYMo1Xn9O0K/VUfDTMVFu+TwPJsuweLsMqi0E9PREPZ0ij63noC5/JRxE2rRRdoEEGsEFRQ5RQuooNLR4M+SlGzQhC3wFzG/MhJ'
        b'4FpU4sPmdACPjgeh3Xiqdck1fnQ+QDWeXSueQwUkfBflfE28Bw/ao5MwqAjQOAKcWEKZZbyXpQyObx9RFahuxnPmsWIrOM2itMAF6PCAki2oVb7BcxpzhU3JE9hn1K+e'
        b'THx1R0s0vkbcRHMxaoNaezryeZgN9jGOxSPf55uKhRgtXwGOoI48FoSpCpOUuF0Qow6mhCMccFaRO6aHSIwwnQoziHyECmHfVky5gp2PWnJHXH4lqIY2vgM6Vo8SH9U5'
        b'3STXENEMqDShsTBn4nlwgYpQrFXUBPlKAzXarwa9sXg+0fhPC1ERqSoAK31ONHUYp7sqVSSaNF6HTo6wCBhWYFygA2ooygWOoipbw/+PGtT/KjyMavgXa4VPy1t/TpdK'
        b'0qbZ1Immg/8X9AVTfhzWWCxIXnWi7WCdx5yGfiF6jiEW94kWRDQt41811CekY40Il41FFlitYpnPtYhH8X2BxOEgCakFEpVDg9fFehq5KpFf0xJJsHYl3CdXJSINQUOk'
        b'K9KmnskSgWhtLMSMhhqLb2/Ii/FV0iMt/OzDnrZUh5LrS8yl9/f/pa+wXF9yGkXkm3/BLeX0HzsK0+4TXy7zR+ZCN4kgIProDKYWRhDEPElAS9Oh0+zoNCd6Gf51Q13u'
        b'NHtDW9WH9YZU1ZvUhTy9iLy3lfxaTH7tJO1oKp34bqjLPetuaKs6vN3QGe1oRtybqIsOJQijv8n/3SnEiJPRB7j5OWQ88jgabEZXLDjw1pvkQWFE/0f/irVF2iKqYEEr'
        b'Xk4uPqgM89wYdBb2BoljoRYOPN6Raz7HsZgonDJTsLrSqUv4605dNF4n96BT10r/TF/89wo31OgyfdZM1xmzXeAidGVkpGelZcrwet+FBb4LeMfqRn2oR8/WTUNbS1dT'
        b'RwqHsVx2EJWjY0Gr8A5XGaxGdrMBqdQzidpy0VUrdJV4lcyYPIabEYGG6dUkOGTqIiZLdvEubiYqXpCpzxHXkONZLngYXSZCB+cyJoteTEH1K10kHDcrCQa4WeIMenEX'
        b'li0I484er8PNNoMq1tQxdBhOu2AWcNXfybmmjadXoRe1Ortgis6Zinf9OVlG9OpUOKflok7CzDdCPTd31irme5KP9qhDD/7LDc6u4NzQAQ9WRzdUumDxGuvZfq7cvLQ4'
        b'etUY1aUTAi6Fw2nc0uVQzJ6tnSaR4Y9YlricW4Yl3TPyXiyBThn+jOWaodxyF9RKr2bCGXUZSX4BtTM5j1BooFeD9LGYq0ayo5SacytiUTV1N8FkP2kkw9+xEro9uZXW'
        b'uDlCCageqyPDH+K504DzXI320GfXY/GnAJHv8Nqyk/OC5pnUUwYd3gp1xPDCeQdAGeeNRfuTtBLpxGhE4ilgkdyK85lqSLvhuW0X6sE99s1GhzlfCzhCH+XR0VzUg/vs'
        b'N8+Q8xOSaHvueqRe3GV/KF/G+aPqeNbeGaiEfNSDOx3gDce5ADO0j9I5BM7noR51YoA5kEOtYCXshWOesIdGr4erKJ9bjfahA2xo90NtmhR3PHDuEi6QuBiQx1OhBSql'
        b'ArHFXEVnuCDMnf20P3BqkpcUd31NOJzg1kAfDNFmbbDidkaK+74WhgK5tQSwS2ufpY9OS3Hvgxei01ywM26TfGnkBLgqFRGuLAjk1oXNpRej4Gq4FHd8PTo+n1sfOId5'
        b'aRzThzIowX9tAKwachvwRGFeH3ASzm6DEjEJ2leNmvDvStymMVsT2jB9SnDvN0JrIv5VuIDRoB1KsIx0FPfHCV1V45w8YB9zmBjA4nkNy4YB3aiacyZ2PsZdg1CeRv2Q'
        b'nDdxk1CVfLgLUGk8OioQzOh5K84edqMiRp6rrpOCeDIJuuE0NzVAzo1xU2ejo/jbpk/z4KajC5DPvnjSOOaJkRnAOUxGh+nFWKPcINxBa2dUxln7wWlbB+paEoi6E1DJ'
        b'BDvibmBPkI8kPZWIM0K1IjQ4cTPzUbqKF5JWegf/EsGedHy/E6ta5/EzMBBM/XkcJLqKOuRPlGHBktRiCPuZ099Z3QR7/MIp3Ap5iueMp5IKMIFYtIlG1DaNuj2wWgw5'
        b'ozisIpSQZ86jNupshYa1gPWRPiLgGd2kZYSfsEGXWCN7jSJZDfL7omCeVNAGZ1kF9ehoFlYh9oTQp9ShEXcVBvAjarnUA0Zr7TxWv/pkzhhPt27yejZqYclCzqF8OKTo'
        b'Ie6aFf7OPWJKCMdZ1JVnQwa6YO8KVxgZLAU5KbMwE9Hb0IpaaAX4gcmc0QRn+oEToIJ2bzFUoiF7VGxCR0IEjfM5Y/J5WL24yPrfn0bMwQoyqW/ijLar0/7HLGF+Vd1w'
        b'cjn9AnrfEH9ELfRRGvQFsOFsXrQSlWxeQ/vAvoMNOfmKdCil7iPQgQ670Ruwh0TtgMtkSAdWwRnaG7kTVxYWxxlLsGfmc0az8TCSirQms0EtnIcuyb+XEBX3F+rCKEmw'
        b'ZtZE28JFT/zIaehUfJazggsJbXx1KOW2YtbvpI0VoAukM5cj6W3bZPpVsa5oj4KupDvkiXoopKRBfXCcUs90Ieqyl5MWP4OJC6dhmBDH3I15Wu1GZcS4JO+IOjTheqJT'
        b'6Fdb4mV9HN1E8lfbo64AOY3VJ8lJh2d6N+PBUjFmlBJoySa3lyp5YBccYlzUAGWoDZXouhPy5hPSESY8hh9ZiQppG+GoA52w1/MmHaUPzJfXAcMebBBPG+BFp2S7hpyy'
        b'8gkhJ5loIX1oZSbWgEpQ3Wz558gnnpzhN1gw97k+1AXyeVuQzhlbwmnKLeWogI5xXBjVuVvQEfZMfrr8e/FEOEWnDF61CqGLzTgRZxw2dw6+Ox4Tg3xsfApxEGbLCjQx'
        b'NmpMZAzQ7UeJHoV6QTGhyCN4WLCyXkoXh3x0no6+GFXtUq5QZF5Phv1kYix3pK3kqGN5Rjn2tBXY60ZpEYcG6cK+cLOO/fJsuipY8mxWbchjA7pTsaBQht+Emz8PuwkR'
        b'ZhhTEpjhpf+ikoXRHjwYzpspDQS8PdLjgFJJDH65XyBdwGsE+QZSwfYptAWX0FWM/PQb8RzIRicYDY/n0f5vI9l3lCOpvhQTqRsvoJRKHXFs5p/DdG5QMOYy/MTpXPqB'
        b'PLpiy9NeBGIdu9QHndOlyRBJpjQNOC9A/liDW1SOPJK+2FaLetGl5Iq4uZnkr0iH3FUb5E54Btpcc+4svMdH+n4WOJ1dNHHT5KZsxNwUGZnoOc9Bnuco25BLXU687SPH'
        b'+WaYsYtXZoq5RGcay8lh83ondtEoUJe7MwarQtMjfcOmarKL8z0l3GcRmHUsI321Z/mxiy3h+tzckJVYRoh02Oo2hV1cu0uLO7IN6236kQ52y+Stv7DFGL8eRBoaFzpf'
        b'xC5+ba7Grco2IRd9L2IZk14U3ETc8klEgYxMnKGVxlHf6J9whz+ZtYG0Pi4sNAJrh2tW0Bu74sRcQywNP+QrmpTKnv7cUZ17kbMgTyd+OjmTu3Wyivz33CLmzGirzn0m'
        b'0LsO02Pmcrdc6H/fLqK79gysRLSRhQyLxLstuJQQB7pr50F3sr06CTzfgiXX7PHRzEOZzFhUhDfW9tGshvrHMV7pRAW0UdEyM+4bcThpNNQzMYF9qmibMTfXbRXpfG44'
        b'P+5hv0hlpDAyZePlnpEsP5IyL1K8HANyQy0hOSY2O50Ido9KjKSnpZoYaQFdONVC7f3JGZLc2bDYzzcAHfujNFN4Uz8pXYIFIZZo6lvX9dwTNlE8ZrQQ/5D1eFj8/RMG'
        b'TuSJZGtx47aui/0CX0g2WqJ/pyrs6xu342v63j78jdYrizU+WGzoKUh+VR+Y9GJrTLPY4/pz+cteSViSqOv5O6d7276+zCXiiXxRff6q5a9INoxb4R4U9uabYSFnjfbs'
        b'FZm5ZX9TtpLni20aD2q1nY3iMx2slov8lm9uLNUdXA9qoU9NDX3GxOFju3Mfzkv+wDo5Su1imnr7pZK+8+17y0M/mrKlftPOe5NWt3rXVM1LM4yPCFXblvp1ycvvfbU1'
        b'qeK1A0f/FRdT81Rs6S9hxcfS7kYuDlpQczL0I+mNrQa3ruu0eqx/dtmOktqDd1/OTnnuRwjstni1K/rfd85McL/TrXXgW4O+hBbj0l0frW65PlNttdgyyPfXp6IXBffv'
        b'asmL9b4ja/VrebGo9eSd62Y5/ftaxw2Gupo4ye4+UWZxaeawWuu+ukyDFXe7nuFd05uWpBwdd6Ox1cJZc0VDQMi8tQMnf3YxzFrb9ZLMIS32eNuLF0xuiLeEfmox4QVJ'
        b'30ehs9euPPNxz8eXP/0tetHngZUvLu330q+P73LYKM6Shs/V//q5lMSAN39ZdL17s+tLznda1HTjnn8j9vsnXp650rQ7aum5bz/y9Anf8pnmtN4xJ/Rvt+SHvf5JTshT'
        b'Qckv9iakim5/1DQtpSXn8l4TI81/+153/ClkbcHk1u8Hphq9FX0s7Zdrw7FBlQf79e5tH78z6mLVtfLO9HeSS8Pu7p8L3s/MMzk88d1PPE/4rY5ZuMfvk3uHv61PaP5m'
        b'nPPCfw3YPpd8XVd0ofWD2KO++6oT3CZ9dX2R1bc1PYYvRXWsCPExvF+/4EJZTe2XcR/33P3h7hzt789O/1n61bJrhVyGrS49Zp2OtTdy+oo5lnh+daCTuTxqtmY2oUnq'
        b'eGGXoVpnT3LsLvbkMUv3bqdnkk4o39mHZu/zIUGypbvQXlQtErDoVMGOb/PtsYzTI6UJTS5i/VCkxc9Aw4a0XreZqN0+MAsdgg5vNU4cw8Nl6NWjZ5k6W+A4icnj5eBF'
        b'3FYOo71ZJMR8Wzbz+zqVg074wFEoGeXIRqLQMM+7IjSEDtprxaNDzrhX4kweHYB8gTbqgC5ssicJYqCLGEN6+GAohRZ6a9uUmahkvQG11Sj818J0WY0Xdwhy7Icap40q'
        b'10kEdGWCH70XBue8fWbDSeorg1sz46EJXY6n8cmhM86YGKx2oQZqsIrLYxG8W+HQLBatCIowyUbiFXnb2479v/WBefyRofpfPLe9oSWLjkqOSEiKio+lx7c/koX3z7jC'
        b'7OL8xAINiMz/z3/flRiwcA1a1BlGS2Qlj47NYmkb46sSerRrTINGGMuPkvV5Q3IiJjLGf1nSyOFaNHq3Bi8WxDQABI3DjX+saRpTLVoikb+t8Bsz+XSi4rO9RHRDlJAU'
        b'r3KS+ycJqy0oNhxS1xDxbZlFKPpnfFt2c8+aq3q3UEXkONQa2fv7QLtyk6Lz3TRcrIEn/EMRXLUU2yU5pVVBFPJyBJcQp6WM3Cr+w8itDHDwwJEeQR08nN17vP/jDxWJ'
        b'Zw9uX4gT/gI+9KF2yX/CQ+2q+dMtOGkeyfmZul7AUuGJMdEcDbYpwzoTkTnX2ciRhzaeXkFEXzvo5Q+1atycHRIb02kJCzxzeRkxEp15bt/tSM+oF+Nsyj+LDH2i60h+'
        b'WWPhjKLWOW9UdR/oLph0Ir9HjUu5K/kx2tlWoGuIBjo+38cFL5XyQDOS+YIZ9O+iLtuzPQRiOl+24VHhjeDUEgWK4xGHyjek0Ztjo7dGUFGGTsnpf35K7uJsWNj8nIkR'
        b'JIBxBAmPMOLkpVKzgs35BBUmF0bxsq6Sl3XwXyZEeHL987y8m/tSV5WbCUPCkEYclJB003BQDu54yDWLYIn80CEJVgpOQ3Mw8fI0l87GC24tnJJDo2LxXnXOx4Fktjko'
        b'5iQWmVJBKySRnZD1YOmt2x6V++NlxICHOizlMd3hRU+R/mER1R18h1IXkhyd1EWgELXAGR9ff39HJwmnESBMRRUy3KlT9KXf5khDVolsiCCv/fm0+ZyMCMLXkrYH6aSm'
        b'iTjh0qVgnrszhUrcb81Sm7dSoGJ44mcW9lwiIWt5itjYTEQHUPuf5s0WdpyMbDHLO/mgtZnfbRNxIrXjfvzUrJ9pa8/rqwWO5VggUXf7uZyMyLDCm5M/Fggw8yNrqVc2'
        b'e85MfcJXHFNE7HZpsuccks9+rEZAxY6NugW/yoi8u9rD7+NP8bvW3F5185h1MnJWN3Pt8qC1Olk6qQ6ta7Ag7MhX5MbLCFFnXJ5j72Sw38vBrtWGOHEYdYs+2X+B7hQU'
        b'f92d987res85POelxqnzwpd7ZhaupO0aRX/2OuEX7gdX202L6KXn/3X6dcxDdtz6T+yeDKWXXv7AqQSvEWHcBJOw/gbau28cfy4h2ds/4n5YVGQRTa9V5Hxc8hp+9WOu'
        b'du3ejz5kCMpzMgdU4kVxQy5iLDaUCAao0dsD9ie8vTFfkLXgei1rQz0Cl/jfXKzdFz/zOd/f1bUq6lel7XU68nxbZYPDZxYbziY1ty13WBB42njGrtVlHnpHQncfXbPA'
        b'zyxsU8DOlVff8HsmJy8vL+vXzRM+fEu//KcPJ+sv9z3UIP3No83aM/mZTp/kpRfc7MrH3nt6TdCMEwb1v3scBTMUd8HlyNFLDf8+c3Op4ey2CS/aHvk68X2XVeb6avXv'
        b'ar/2XuUn1wNvQuSmJ4vX9X60yVW0onL3+M6NP7UtdRhovvLyvWGXq+9/dWHDb4vTco657dN5yvvYpcDTn/3z6O3Ip/J6MvRfXi0aciovneT2XJ1z33OzuzIjXrk+7ZU3'
        b'dzf9S1Z7q3znuQ0/vv/0yoZ3F7313O3guV0pjUWXDPMiX2iXxNW+neb4vKV/4f3wN78Ys6p/cm2dya2Gea9vMa1/P2+n6fxjpz5//1r3r6VPf3v7aVndtIyiuDdNas/a'
        b'h8TXzyvZNFYXtP/ZmDy9Pej1DXd/2zZr25jK4ukf3ay//9vkmf5bt3y+vK3yxwrXoezD77144uad9h+2ZqtXfsMvfD7jo0+t/3kzbG6UU2Wgn/oL303/YoHm7XDX/Iv/'
        b'8t5yzjI3hz9YXncreIKtPl04baAL+n1siYOhhJPEQ/t6wc4SrlLh0yx9HpGxGFJQA44ISatT8Ppdrcgcd8SDeIL4OdCjlYgZPHRkoCMMOFAIe+GQD13hUSlBjWlAo5Cq'
        b'n4cXmosKXMlRB1lGVpaOLhzS00MXtNPwRorqRHhJroJaVAH7mZP1MX8Ne4WEC60hRMjdMZ458fQ6QzMq8YMOIogW8ot9V+q5Mg+tJld0zt5bLlBKAuGkt2AMJ3xojVuD'
        b'CWxGLmtaRFBps4XlT8TftDcYi6ny9jSlwiI0DEdlM5kD0+n1qBu/aetI3CgkkWnopDAZChDLpIea0SXUpAIcSVUXXKAmk8mrJ2EPtJGa93v5wn4Z3qGk0C2g2l3A4iDO'
        b'mh7n4+Unp3SYsDo4Fjp52l2XxBCfkV2NgxbBLBido7e2zFxAsbS+tnjo3LEgPCAYJ0f+l3buv+NLPEqGHdnr6IZ5/K9smNN01WgOGipr6vKmvL48RJg+lSLF8tBhJBMM'
        b'kTm1aRAxbbmrgAZPQo4RJ299Kq+KBeLMLWbO3PQ9QxpyjGV50eDT9ZQSptoNcWpUxuYb4piojKgbmvGxGREZCRmJsX9V5hSlG5A6DckvfeWOTdox/ss79lcTVHds6u9c'
        b'hWfVabxnoxqZ6ratzpn6iY1hCHVGCyoyGumRUvQjgi+1JvNxImXIAOE/hgx4pPAn5h4ODoJ3cHIImZKABrC+Bgec6fmhlxpcgHOcIVwUoT3CzITLXQd5GdFAb63P2VJ6'
        b'O/KzyC8ifaPuxGrFfeCrzo0tEwWdWa4SSET0WGv/DR0yRqM5ze6vcNrmdCPl6IvZWNFRe7T8JTw4pOTltX95SDv1H1QpksYvZeQaGc9xq8mITl2mtsaL/5+P5yODvYge'
        b'Gk+Rf0LZW8+IaBaANWslbKAS4zbFeEaxoDsT3xFt/937pdw/OViy/26wtqYbPzhYBn80WAajB4u8vP4vD1bbqMEie5ZreKS9/+jBgroxdLRQvVokNMHxxw8YaXsfGTJ+'
        b'nzhO/N9MQTJcD+ds0PJXiND1MKQij6/TFbSgCzVTYfXG5glC7vRDmlzqh7t+nP3MdHrxSUGgXeW8ohwydwaxs+DGHJ5czf4gNSZi0G4rR2V9E2iBI0HQSdo5bI0KOajT'
        b'R730+X9PlRCFVL9hmkx7/gQNjnYGT/5jUBLkiI7be8LeyV4iTrJB4I2gMKGzYJFYlokfOWnbNP5Fd12Yrl/4YVXahI8Ez3d3f2z5WuC5PRW6ywfOveugU9OzcvH3fh83'
        b'/5b3UqGdxVWtvXalpUVjJrr5ehx3+ke21et3r46fZ7ygouzTjudWvD0ms6v1u6l3B7PGj91/6uXXbn9V9lZCrUhau+u37xe9lxbi2lw5/syH62016P45K07L3tGG2Dgk'
        b'cBLOoF7BEeVvZfrkahO56AMts+XST0qgLT09S3dC533I8oaFn7wVASTmxEEsf6BexNLixqK9UMkgotAHF5Sna33QTiWFmO2h0E6FE3QASyd5ZnBYsIKOGVTI2JYExSMH'
        b'ZRJ0AhUJ6IoTFDMhoxMVowZ7d9TgSU+8xHN4OAftBrTPY+fl4EovLxh1/qZr89DExFPoURvYyHTVJmtrakxcBNkT6Wxd+FdmazLx9NMlxzt0CyfbtyGfbqIygwk73xA/'
        b'AGJ6qJtCuil5J1rRL1rFxr88j88YPriPQi/eK7vYuuvphfdTRsyJeO4cjBajFvugh5ZITfm/MtMH8oBViCq0K9TjhBihlKdHO8JIeJ44jRhRjLhQo4APEceqxajFSAq5'
        b'GPUYjVIhRILLmrSsRcvquCylZW1a1sBlHVrWpWVNXNajZX1a1sJlA1o2pGUpLhvRsjEta+OyCS2b0rIOLpvRsjkt6+LyGFq2oGU9XB5Ly+NoWZ/kKsNfNT5mQqFGiEGs'
        b'WhwXa1DAHeJDDPAdcoyliRexiTGW+K5hzCS6s1jdUPeLSiZOgz87jso6Q1JWWSaxWywf1+isNFh+JIv1Q2un8nBrMSePf0Qd4Sh5ycanqVxFxX+4isrzHv1c8B+THo3q'
        b'6UjSo8elGCLzg2U5In+RZEZRrIpVy1dYxiUkPiJf0ijOIlyt8dBKPsE/k+yOi5xQib2nPA9KgGMwQ1x5Qqc35tP9Dk48t5JXn4OG0BUaWWfehHBpaloQvqN4co1GFhw1'
        b'10ldQ1IOs2SzXLSlhjYqjaY292VQhmsqQcegbCTRLKp1oor+ShepPVyGqzSZ7Egq2U5UylxEOtHgXPsYKPT2Y9HH7XnOaJoIVcMe1MwC3BSiqyRiVzvsnektcDw6z6GL'
        b'W/yoUXOOkYtPgkDSJNMUyWjQjlnALzjPhHxU7ePk7UfD00tTBCzzNkAb83koRcVwlmZyJ7DdEl8/3gTVc7qoXrQ0jKEFc9Sx+AmdnrhT+H0LKac3WbR+mzkzfp9Bp9EB'
        b'fBdOMX2KfBRcFHZsQg20+R3okI5PDmrw8rPDtwV6uAHEV6eU9a4KeneZQpciCbg8BfhRaGEbbzkMEsLDGW3VjN2pc5kb12UsuB/2SYejLGZVOO8cAbvprQ2oEa/bgpFK'
        b'/nVoS2VNlqcmzdulkoKdRpRCJ2AvPeWKTqIRujT6PSId2sw3cdQyLEAjnA/irHxpfCpUF0S352tONDiOftOKSIfZedPIgZsl6dYe6NG0JymJafSoUaGjoASO0HdfWkvl'
        b'Aw1/aaR22hQnjp7t6cTLfCbbquZQn4b6KZ2hDnXtUAllBcVrWTQrSyikH7wISifaG49RDWW1EfKpz6zZ0lz7hyJCzULHFMGmSH5Xxn8kyMJhwihUz3AW0N65mBMaRGGb'
        b'oDNBrWIdT1OfimW2O8uHktF0bQ+vqu5xt37rv/H+P9Qz7rzXWWLWaBPYUHB0dfgXHmNCPjG6c/r9DcWrJy5+x+GNK+LW9ujrR98On90WkhNWUHQq772f39MNuTeITpl2'
        b'7nkvRe/A05KIV6eFz1lfUPDbl/kdWgvUXWd80HPhVtBbMQ1Lsjo2Ju0Ie7XqszUZEb2mtb98u+atxjvaTV+vXHRw4eG8KcmWQ9FjZ067NiZr/SlkFPx11iff2MZmfv1k'
        b'4/jqVdMkE4zrg9Jc8qKshjavlNx5d7F7n3TozprO+c989YXJ7U/mf1me/q81J6Jnx/eZ9u0/Gn8xI/dWcuC5H+3DPf81WBbiOfvX47MuT73Tv/Wr0DGf6Vf5Jb+jETup'
        b'4m1fr0P+bTnR3pu8195MNfUyfdqh3OHnJof19z28Ftl8bjX1tyYHq0+HnwudEyhtra/wuB7r/XOLaNO7n6ZHvHx/U7CFdNuru37lvo+p/P6ZXFsLKmlMTMslZskDqkLI'
        b'MDpJRRR3aIoPNvbxtXNid6WJAmpGHQsZmqsQrwc9eJJ0wAEsopLjITWaKnenHXSyUAMDUDmTpQJBbcGKs3qaCwQdR5fY2VE3OgOFUrftj0lZEIW6mX1U3ZdYaTBLT4E6'
        b'LHtaCFroQDTF3iRaQi2q3EF0acUCJ5UJ6GSKO0WjLYezc30mugeQuBYEJteCRTu6BA2qB9GUH05QCYcVC58pqhPPQ/vC6EmOVRJx8DReF0BWPVEiH4xlwCO0OythjyGU'
        b'6OUF0IVPhOp5ODLOnYqMpugcXGGpOcjCZ43KaWoO1ITaGFCnJygJz8cSvF4fVln+OMM5ImhEJ6GWJXsomxAGJePQlQDlEsgZ7hDBxVxMEEr+86gL6hdDLQ2RKl8Dpavx'
        b'd6O69XT0tkZ6uqNWkgJBvghKpwqoITSSDnssXid2y4MqGGxjYRUcJ41ncTJKoIlXJpqg2LNBqOT0NEUZ+rCXna6VWafRJ/CagRpRkZiEmhsDTca0b2ttSTovdNnEWSUK'
        b'niE6LUL5fhHs/QbJImhyoQgxunRIMeOgi/FiepdI2xUk6zpbnTXHc7rLRCugVyODbKZ4Tb2ymilvD0ecQ+fD1bjFmeoGUAoHKSV9tMQ0M4wiR/sZdI7TjRfNQ83QT3tr'
        b'kgp1+In63ICRJYgznCuCy1vRYfqEZBPuKV6qT6mKmIa6IqJCLbBVe/wZkubfBUAQow6V1i8R2eLPSuu7OC0tGj2BYYA0eHYAR5A4NCk0/SFRCwguR0sQsDQv4SW/SdSN'
        b'KSpHi2YIUF5nPz9LNPSpWfivvqPF5+jLZcgHkwDIMT36o/V+jT99RimwV51GkSv1L2sT5eNUUTwPdfbPx/82/aPA6i/hfrFI/8oWlEH+rWhwfbmMOhJs/u9F9Y9n0aPV'
        b'I2QJ8cl/EGf/VUWHWPOKOPvkraiMzPS/EU1b3rI4YtPMTY9t9nVlszYrEqPiLRPiLBMy/h9z7wGX5XkuDr+DvZeCgoKKykbAgSgqouwlQ0FR9pQ9HOAAkb1B9hCQvWXK'
        b'kuS6Tps0p81J09MkzUk60pGkTXebpml68r/u53lBUMzqOd/5wi+K7/s897z25Ht4nrQ+uXoK36hodtolwRfcwBurM+txdbLToiLjMpLTvlE3A66Q/vtfdN8/Wp1tu2Q2'
        b'vn3Bv1QaXT4kMTkyLjruC671ndV593I17cPSMwz4lyL+lQXEriwg6lpUROYX9W/4yeoCDFcXwL/0L88uyyeoPX/u91bnNlkBrow1qEVQxg/wL6wgMiqcgOa5K/jl6gr0'
        b'Oazinv7mhfjvrhz7CrQ+d+IPVifesQ66v/HUMStTr5iNnjv1b1an3r1WcWYnv6I1r59+zewce3s6mkW4Gs0iKBLkCW4KsxRuCFbtAELODiC4JXyeAZwN+awBXO4Lomi+'
        b'Zo11MYeRUp8Gbti/l4O8q7FRXJPjjFjWRfoJ/KVF8U0auCbDSckZz5oTnjEprFzSM/b8NP97Qq58vlP1DVY+X45zucgV/3hZOFORaizkhJZd4nAmEhdg/xq9nhNvD0DO'
        b'c4q731xJNuba5Xx1seO2QDZLf4W7re70SXxMdExUhtfzq8KzaX/P2DfLkf3K7DtHULu2OjwXd+yMzRo4KZH1cAoKsM50dftY/XRIDAtHFMCSjCJJ7HVX/sc9NNFfLdyK'
        b'blTlFzuFnIdmv48m89DER38UOnalLIbz0SSQFv+fYnzfhW6Wk88fwN1YXnVZc69wF5ak7LYkfJkHJ+32N75kxS++5PSoDH6aXOFTQVh3hGsn//gbXHWZ2tNXHQA9rJCl'
        b'5K5hescXXzUpDOyqTRSxeCvmSIpEBe7BTh4IpFRh4boQ+iAHy/mApxYozeLfkrJJkBfC5DXsi3vj6DUpjlhtvT1yOcYlwiPMIyz+Z/1RsTGxMR4RbmFeYcI/6Vw+v0Mn'
        b'Xscv8P190jYpvULBeIvcD//L8JnQtI3D1NKiJDDC1+76OtcjVpJVEWWpP3NF/OB3n76U9VP+7htcyr21gWgbTPx8ust50Pgq+IJVD9pXob4xRH09nyGdjiz+Lp3n+kRr'
        b'15t+0w3SM+ISEgyuhCXERX6JFVco2IiDyHj5O3HmM/t92QI5ekZN8WdXGr2arsbJd7wqTg+hb2RG834T+mq40a/cwpSiP6DfzDTENR6nfY09Qo+lP9xcFWn8+p0/BSl4'
        b'nBiM32LXGK9jp9PSVHI0XmfzuEWkoGSfWeiFl33Q4MWqb7VD6/d8tWRfF1s3/FuajVjw+gc6Di3mxnK8VaD4nLWpRAeFHshneqgKzIidL0gae2IXNmmZPjH0HsNyZuu1'
        b'vShpGppo6P7EYIr5nM1UOpKPaxnBGmvCIB1cXG8GtoJRzrDB6q5Vr1hkcSaBNQvcJQ4kKlvB1zxqVjhJqAi9uMA3YoD7tEje19V0ytWUsNEVm2nZw1ICmQTRThyW49Zs'
        b'gi3Y6+4Kw/gQ8s1kBFJ6QpggvnVXwp++1MclF5cewl0uhzanvi7aaPK1BLn/WVA0Vx1Dao1CuDL8Gg72nDU9YWmW9Og/vgFKFWpsqJOuLsFYc6OSEmtqR3Autkh2LGKm'
        b'jbHQxDRGT96WW9Eg3pZbEeXfluGl4rdleHH1bbkV6fFtuVXhL2plOzwB+9fbJq4hPNr062V2SmzBciIpsZJQ78L/VjUHFUUlEWdwhrybZquMQ1qgABUizCEGuoALOPkM'
        b'v9aQ/J1+52l3ocw9nXuCSFE5c6LJFioXahRqRkt/dTch/xYJFIqRSnflmJswWhAlxznm5NjYkcrlQi7OXJHGlYpUiVTlxpVf/U6a5Fa1SHXuUwVuNTqRGuWiSEPuHQ3u'
        b'La3ITXfl6XtF+l7AnrgnSz86kZvLZSJ3c0UppCX9R5QLVQrVCtULNQt1opUit0Ru5d5T4selH7l78rRW3XJx5B7ONSrN+e5YJx2VQlU2W6FW4abCzYXa9L5apF7kNu59'
        b'Zcn73Nv3ZCO30/t7uTnZm6rcW5vpDXnOAcneUOH2t4Ptj3YgitwZuYvboWqkJqeOGb2tIsEK+issJirtZ/vpYtaRdQeD9U8wXkB/pxuEERtYyxyYpzAswyAsjVlfUjPj'
        b'CPrXDRRNsjr3fCR9FZHBtLq4DIOMtLCk9LAIptamP+VQdM0gZpOcJplqdZaw9FWFiLhUkkGYQUzclagkybDJadefGsbCwuBqWBprMmZn96zHkulaT21wlcmdPO3vYGFw'
        b'Kjlpb4ZBZnoUt4OUtOTITG65O9b7aiV2tDg6v2cSHtZXL1mtXMKufrV6ibhI/IWpDmLuwqR+dv7pC+KO6il/7Qq/TlzZ0jdy2a6eKFPE6FrXXsOGGhe7e+7KIi0MXDmT'
        b'VGQyrYg0NIOoa3HpGeyTq+xkwyW2nKgNZAjJgiQqN7+mZxTxq3FskfRNdCYNFxYZSWDynDUlRdL/BmEpKclxSTThWpPVlwgw7BqfTSRR9uJE5kTMxYG1hUVdVi3eWJOC'
        b'DVjuwRU39XXx8FopiQrLWKiIParnMpmu7JjEUtk3GMAKR9hrEnfqFSyUvwn9+Ih3fU7Cgg/kQAXWkjztIiWQ3ivERlgiSZvPC8Ncf1OjWJYCK7iGU8jXPoAuyIciPxy3'
        b'M8denMAea4HYQqB6VGR4UoErqOp6231tBywjzr/Od746ZJySKg3Vm6CWr6MxzVKrTeERPBSxbiDpbtjJyXOnr/HhUimhtzxsLS0FfF+b+yLse+KO9MUirr1WuRlWeML9'
        b'rXzltTPJssQzHkhxuoIJNJqmp0qzZDtW6UEAJdgtiDt9pluY/hJ9/crPdU9XsrgopYLbfZ6dR19xH5R6b2tCsKgqp3y32ETD5Z7VxVArxeAdcyqFP1OyDdJJ+Pvffj75'
        b'vX4f7UPWf+k4YmUS8B+nB/pfN4lZSDW+7O29LeJ7bxteOlBkolj36bcHLucXvVCc76r/64sHI78zXb55u9vdt1UUh8e/vf39xNZXR37xm4aPNLyKx3+/WHa3Xi26+rU/'
        b'plx82F4Y5/39/uO7q0bsdr9ZqfanayO/+ui1WbWQlD+I95z94R/+VPfjat2Wigb93cet3jI4/t+Cv40dP/ftD4y1+DbTrRZW7kzC7MFc3ud/Q4dTS69jGXTy7j5YcFvn'
        b'7oP2K7zbZ9A4g/nc8THeeeJ33yoJu4YZWejgwiRYDfka3hmpgxXcq+pmicwReQuG1/oi56Cf+/b6AdYLShItBTVQxEdMeZ3jpeLuDFkSXFmkhTGrU9huoMVc6wOevCet'
        b'/gouYelVE5IIvNilm8iQUD0lPgN3sZOv7tcnizUEvo9MLbGEiQwy0C8yg0ao4Xxp3plKXHFxiQvUKoA5QZ3iOKHY9hIWklDtIdwKQwKpHUJog0Yc4YPXE7EVe2+t7U9g'
        b's82QrxH6GBY3SbxzLHOnmGtvYC4j0IYZKRdSTe/xFRNnSZruhG5YWPVKyWiKlKEAprlsKazFir0X7Vg1P3dWK49foDo0iKESprFYsn0YV2ZV/LDV+wnaq/iJPa9ARwYz'
        b'82HnEeiil1lqKyuQyOURQYWluzlXy5GVkHAWiuChLI1aiw28xJ8PY2ewlAufgGpvSQTFGXu+MuYIqS4PTVktROg1WlcOEe5LyjKq4oIGS2mimYrpww7JtDKCzTTWciZO'
        b'Phtk9lXCujfysfkzwvl1NIbDLPRchgtgV+GC0ZW4/tssiH07pz/wfrAs7fVc+jm9sFd58Bpf2Bf4FMX8sxt4wHQVaTN2bDNfXd/IEby/NjfyuUv+Os4K6S+2Gh9VlFiN'
        b'n5ls1S9ms8rUn+Xiazj2N3SUcT6cjC/y4RxfWWKaCQtmW8tg15mtObsgFym4ahf8KobrZ+yC/58YrmNIab0hfGo7K+f0jEXSJ8hBxNmY//irD1ZszO9+j1mZhTNL7xkL'
        b'MwwFLKiJFPp+qMKiFVRdj6a4AC1fYmpOu8X6iO55ChLSIxJCuKTKr2VDdvxGCLC8zop8mt42DDzxxIg8zX7x8DbHGlPaYZDC6h6xfkNzss52FXvMg+UvCR/nTF+Fwq8V'
        b'Pv4V7clSvLQH9Vjo9TTZZgGFxR6YA0MmbmYw6M/HF7IPvT1YjAkMQbHiYZnrceW/bZNK5xpz//H6b0ItNH4d+t1wo80mYR5hCdEJ4R+FfhCaFP1RaEmMm+0bEht1vZGc'
        b'pf4+YzFX/ndTlNzq1Hgf5zbmGhzPsPXlI4H6oMVAUhc7iTj505FAgtV6vTC77Vlwc8S7DOJ249xKjMEXU/8VK3hazleFv/Xm7WcM7Ott3J7fCBSnNZ4GxZi9JLc8BxaD'
        b'6SieD4yc6VrnpIpryE6JtVseH0M5D6QXoUtKVQh9xOz5CM8yWQ+JiXwWJqRsWFmLMlyKe8NnSMhRuVc6sp+2dyfEuEV4cRbvLZd14nWc6lcs3mLBt0zlQ32/9azF+wu8'
        b'EnnCb2r2PqekoCaVpfO8G1xj/f6S6U9+ozt7Ya1n4vnLIArIUPf5VIEZ81ikNlEFaaIL0qt0QfylAdHMJdn7jF7oHJVBCrGEU661ejxfo05Mi4rmtddnglI2UHrTojIy'
        b'05LS7QwcVnuMS3YfapAcHk96+JcoqxuzPWmvTEYhYQwGYRFLJbAf4HPO/Oy5p8Kn+djpOJiDnP3y8dCNE1ybi2h7HHNfo9oyvXZFg+PqY4+QgumrKIvlWIjlcUq/n5ZO'
        b'96b3bh397W9CPwr9deh3wmOjB6OYGT/whUAcr3oY2HPXWNpo17df++5b//bWiz7i7ssE8/Wzk4258UETjZNNpa1ugX6NJyYOlL2o1LpFUGuufn3bz41lJDVRuqDb1IWm'
        b'HXsSY7nLidMsTsKI7hrdAUZ0uAhKdWyT1FnHMRjldaoVagi58pxOdSaei1EM1oU695Xwa7gXaoUFUMtpPZHu5u4rAn06LAgFiudFpL1PBXEqBk667VzThSAUF9ZRW6wN'
        b'XIe5zxdI11ZYYMkmEsjhcNnu6+JyCh+pJscVF8na+hQyrRmelwQGJJFknNH7ifS8Ie0fEPGPPZGZ7WkI/2+E86Naa3H+C5b5fHR/JuLhywSAFe/X9IaInvFszEly9EoK'
        b'w/8+3jvwc35FvN/Yy0ZC5/meIKl0piGalpz6TWjwC6+9SLhX31mwo9SqMdfm478rCyxflMqqMDIW8Q0ca9RhhMv94eM7w7CAs+hvxTaprFSs5tDg0j7scOdDYAPxwUoq'
        b'wG2cXXEvbewTNfzG/Oi2gMU+bgQUkpuRSLHHRCtS7HHR2lkjvxFItqt8GUhKZjfm8eBt2fSwK1EhYelezzf9skVIGJIMp+TIfE3Db/hGht8VcGUW8UhJ1fSvBKwOq9b7'
        b'qIwwFlAWxgfWJCZfIQ7H6pyvjPs/Ben8O5KDsmP2Yc5ub8aMwomZ6RnMKMxjXnpGXBIfZsfU1g2turwquy44ipntafCNLMqrSMbWmhZ2lT8u2vOX4BYD42cNwApemQyO'
        b'sdT46BdxVHWcWWGqHEeN0uMstCJo3WzKEn9cpBQFWHcFB7nKJWNnHvsFDMSxoidSAqkmYYYen5kavV9a7b/4citmv7h8TeDPqdJcRssFcbCpNw3kG5YtwGYsvBbnNfCi'
        b'IJ1VXt7z4gPP75qrnHRQE//U6/1/Sjn6qB0991ODHEFu691fuJ54detBw5//of/dlomOfZsSP5U+2XW/qknNrrPowSuJ6X2uL2sEbdfI0LEJ+bOhxWlTjcq3wgvtvVLq'
        b'X/3P+VdsNGvn63/8qYlrolHe7Lf+8IutP/n2h/Pxv/9g9PexcRF+2sczM86q//tnny3IftdC/0TIbph/21iOL3R2Jwy7dLHddE1uBPFIvuzaAhSKiHN7wOy63AcoFHAm'
        b'rhvwCHLXM27i2limIiWH/TDN18OYhqUMqMY7nIGQtw6aenJEK+wklJma4P1NK20P5Y+I4L42LvFqdxG04eiKfXCtcRBHsErKhTS/IX6VNXSdnTtxftU2yttFY+h7zjBa'
        b'CKXZpvgAG9cZNkc2bcxCjWW+qnHtbVlJ3ilHQl2+PglVW6n0oCFS46o9yHEOei1h1uYNSBtNtN6mxnF6B9GXSwWkEzx59olo4Ej/TP5GdLh281o6/JzF0kFyRjyOEMuv'
        b'Rl7zvvZ9zFsvlRCWFOPvFCG7BrXZVjRWUNuX0WaWP8nMTwqcN5V5cEWFqoVqheJCdYnDTiNaQ0KzZYvkiWbLEc2WXaXZchzNlr0l90SR+NktqQ1otkNkJAvUToq6uj64'
        b'hnmqeK8Y78SLSE5Li0pPSU6KjEuK+YLUSaKkdmEZGWl2oasKUihHDRlvSDYIDfVPy4wKDTWThIhfiUrjQhc4d+0zg4U91z1rEBGWxGh0WjILd1iJTc0IS6N7MAgPS7r8'
        b'fEaxzpf3lGS1oSfvuezji1gOOwjmakxPiYrgdmjGn/KGDORJgkBSZmJ4VNpX9kuuAhi/jCeR/leJAsau42TcjpLCEqM2XEEyH1a9cg6xyQmRBNRr+OJTQdeJYWmXn3Kp'
        b'r15augGfp2Bh4M0CZq/GpfMrIOYemxxpYBedmRRB4EHPrAjToRsOtLL6iLCEBLrj8KjoZAmbXU1T5oEgk8V/M3942IbjrIWh557kamibncHTSQxPAnxX5n1eoK9krHDr'
        b'8GdHWZsK8SXvMwpBMomft8FBm8PmVty/M4nKEBJGRq1c1cpYBPo8lGwcd3wqKjosMyEjfQVFVsfa8Mb3phtw/2RxC88sbp3gIoFMtpUUUhTot68gdq2TZ1QlBG+9PLPX'
        b'i3Ps2sGQZbp1minOkUyRLIDZ01DFeWRdYAn7Fa+kBqQJBUIsEmDrOa4sNsd2y0NCmfkM28+S0gwVQkecwKVMZlTWOoxN9NYZXhwysjA3wiJLE1fPMy4w6J+CExlnfXyh'
        b'HHuYjxnumcjbYjX0cz07oQ6Hie2udY3zOscTp3jEJTkNU+jcfYEXksKUMrYJ9rHq2gmLO2wFXJ44jT2MbUyeWPVq87F8ZsbmbtiE09ICe1MZbD52i+92snjxvCnWyAiE'
        b'6oLUm9CeBIvc2AlbZF1yJHXs3siWlMkuzpbefEPI19H7Lyt9/sN+oSj+75LifSaKQbyQdgDuyzNNSaAoCPFRDMUyriQU97yiu9zBn4oMWPlvM+dd6YJMVk0CGnEOOrHU'
        b'3M3Tz4Wz+brS4stMmVS5uhH6wsXMzcPC1dxE5gjMM1FUKRUXsYY7eOHl6BW5FGtwYFU2LTMm0QgG/F1WvbeQi3Py8IB16nMyluOS32+RmNMj8TUKxCoWnKsRy1I5EJFL'
        b'TnDHEg+cwSE+V1sOFzkwoOPMj8BSSaq22JUlax+6yeV/h0Mjq3i2LlU7K3STXQKfHb4EXVjkvpIvLXZhGdN4B+q5+vmXHLF1TcY0ly4NS0fCcfIm3wS3yWKbqYUxLLs9'
        b'SZkOgQdcyvQJqGWNNZ5JapQWHuZzpo2wz1iRX/39bHnuxEmiOw/jLN3/AI7ydf3qlQ+xEFCoIgn7Sb4/Vp/nc+cnoSPQdG2uP5TCPAv09NDhhj7piTPu1m5YvWsl1Z8O'
        b'b4oPiq6R2cmMTVAfwLv+WaNAvjzMQCw8Wpvsnwb52GSLM1zEnR7m2axL9ucy/a9DzslsKOSbJDQcg8kn6f4sshQmoTnwNtznxteBUhkudDUICp6k+/tBHx/RV3YRc9Zk'
        b'kHPp47AcexGrsI4/lAU3uMfKsj24uLYiAI7u5facFYzjfubY62suEw6PBOIo4RFcUuTOazcsQaUfqUhVAT4kZMuYC3EcuqEdJrCPS92PC5G2tZIUqPy1nrGAg0miPx2s'
        b'5zjWemPhTSmBSEmAy0dgzliBqxXlBMty6SppmfhQCR+qQgnOZtBFxCdiodgVqq35hsG5OzPWP5NO1yANi9Ai2Iq9YmxTwxHuSWyCwrC1j17NSJVPU1aRgSJYFhiJpfCO'
        b'ozZ/UKP+MjiZiVPpqUqpUK6alikWaOr5WYgP7YdWznYKHYRclempmQrcSKo4LY8PaV72uGQFguOXZHShWRr6D/CVB+qdPFZfWHlGMwpKoEjssBfKuYc8XY+sPuOOfSsr'
        b'FGyHUak90GfNtf7ArvMwuGaojDScogWexi7oENtBawJfFb8XyiNXn4JZaLlKpFlGoCbDer6XHuF2akLbmFbEmQxakJK8Mon1ytiIzbdEMOlvxGHift04ulYfH3ar0jgn'
        b'vInTUC1nyt2PO9RBiZ8nVvthOdb5QTmrj9ks9N5PCvIoMQsGGAY4Gbt+glCcYuOHwCI3wWZ3j3ScUaVvRFgFvdgrNMEyKOA08T3YfxhLiU66W3rqZXp4B7DAJV+JGm7G'
        b'aGaZqweWMJvwnQD59Is4z1EzBxiGNndWelxoJ7BJwHvQeJY/k2qsxTqcdCHq4W5OaOYlJVDfQoSxVUykMleWo96Ht+paj4hjWdXVYBl7Z56kb9tmYhEh7mcf7pxV8xTw'
        b'vSEEnxyX/GJ0wliKb+FUfHQTDNEv1wnbt1z39eVjqypw4TYMEWfOYr/3ZUHfJY45QVeoC9fWQEDq5+A1rMdhvm/SsAJrF0W/xQn24uM4qMDOuL9tPy+dnkAsJy4hKNH3'
        b'SNJ/nVCL3t120fe9kK7bNR8uJ7z090NOr8+9rK6x94TeC798QWh0Qs3o3IsTD9VCL771fWFw1eFTJQYxL5/x7XZrmnW3C1BQ+cl3s48cOWIzf98vdTjKInQpeGt3W3jp'
        b'tzIKdx85lHblxofjl98TN5eaCn/x6qUdbzy89Mp+lZL0bb/OsHh0pPc9vdaYOZ3WkM++f/Jvf1b5R/rfo87XdA1e8Pvlz/582SRfpe6nBo6/8/317t/+JFtPJWzoxHfO'
        b'N75VfHhLmr9imM+/pW4yPVP6hne8RnftoOw7Y9859ZMfuGc59mU4teqYF77zDzOblDcfVmQ6v5RudWVz1wed7z0eeVR67bj3+xMZGTV9P6xJixd+S9HId9vstpShKP/f'
        b'nWy5cyQgafrOm8NvTKn94KrHfN+2yKB/lw1VSzTTtPzRB6+dD/vt/HTTtO4bSecXon570PInf//gb695nT5p3lnn4/aBof/E9//wykX/K81lUbOHS1+59cf4vIC/nVSR'
        b'84i8qb308bWRuQvXj7788h9k2tT2v25ywyjl/p8+/+PjX7Y0ZCZ+vrTV72CA2S/+knnhZ/NRn51/55yKxfs79i7e0q4XZu0pvfDqa3XbfpxjMj0n/vGppGa/LfGyJSXf'
        b'mxtbDHCyy/ncT/aHSZ5v5qpY/M3/3vffcvzLoV9NjORFW9Q6pu/6VK/R+HPv7x15c2TsYUTUcPhk4a/uV1r44IhAZejmpj9b/D7VdyGqCz4TtByFz6ucHd+7eeyn2KIy'
        b'YzG8vf/ug+8m6S7u2jb7QZhN6RvZ3XYyPyrPSjg4+FHQZ6f+On7x1Y9e2vvJD/1+3jTSpjeX8fcEPYvW9xYMHH77ney/zpp+ekLzerT18UM/euGlZONPPtE2Mvns6Ov9'
        b'xhZ8NFL3RRwyXe9O1oAqF1cx0cKZfVwRiZ1BJ5kUEQHlvBARAN1c0oSc6U73Fc+2N1cORl3tCBFxKHNS5aKr3KHKYcUMdBva18bEtcjywWXVOAC16yrRFKthH3SncDNc'
        b't9n8dPxWQDAXwaWfxkfNVUDHDokFCadgnIsxK5P4gLDNCwYkEWZQGc4HmZGcOsC50rHDG5bWmpFGvdeGmU3v58covbr5SZEzEfQJZG6JdkKDPOd/0oH686ZenkgHI7XP'
        b'Z78QBmQkvbVhkNhPmyRkzgt7eeOS9VZu12EkkqwxSmHTdWaXwjZo4kbdtFu0Up3VgKBDJlS0S92fM8q54lCauykR4TJ3GRy1EshcFxni6GnO3BXkwuQ5WudBWFhTq/YW'
        b'3NHm2ymXuWDeijUPu2yYQU8ErdxqrTdhBxcjCHU7+DBBFiMYbcuXkPMDVl2p1BLuAw0qgi5hAJbv4a2ETbiAXXwqgRQsOLG8Fxix5RwUgdAC01hqRqIgvYwlnmZM3LoH'
        b's5ZirHPCLh4AHly65v4k8k7xvAiq3RkjM+JAL3W/ASdy0cy8zHUgir+WYhiRXpV6Y6GIF3vzFblV+eMd/VXhliSpLibeZjpxb+7ExzD1lHgbdHnTGRfOKhm+J2BVtsU6'
        b'OU64nT7Jne85rHF/WraNhcFwIyjgM4BK1XCZoM03+Ylsq2LLRXdEeapvJNgqw2NJNaDmGL7acBtrfk1juPGOSZoEc4iFbUnGIXnuotJI1WItz4otvc1F0G7FoNFEmW6R'
        b'VafXVDu0It64YxGTcFJxWhnHhdZwR2iGXdLyJD7xLYShEMuBVQ+2lCYJl7saOWwWQclFT+7uIrHmJF/5zx2KLfle7rpOJHvUSzHrq5AfhGFNMastuAnKXQ8Q2ghksVMk'
        b'pwKD3OUd8SG1UMIcWy9mEXwP8dusxVZFSQ0TvriqQPMGju4SY4W6N0eVFB1hhH/AwhNLSFyn2bHxBuRLQStWhHHuYU+c2sk9421mTjrsAK2liMiL9gGp4yo4yEfV5Mbf'
        b'fLrQJeEFVAZICl22pXIwIeWxn6uDWMKDjCKUi7ytsFM5gYfxJZEU56YuNhMdwzqBjJdIzxXzefLZh3nYx2lva6NnoffkGRKCB/ju2X3GIpxUvSKxhMvjgEj/FozAo708'
        b'KOfBojZdhDmNNG5sxEAnRgQTJ62NVf/1bKMnpt7/xdbPa53gYZGR65zgf2JS1Nezfh9U4lovy3DdNFaqJvPBpaw2so5QQ6SyGn4qJxIJN7MmzZKwU/pNJCNc9/OJlKKU'
        b'cN3PJ1IfyejLcePx/T94s7Uc/a/ElY2RYo2fP5ZRkhGyOsxq3FpUhCoiDaEKZ4nn+4Js5YrAqHAhsCpCEbdOFa7ozDMuyDXHIrHVy/MG91VLeNopZoRftYGnnV5vv//X'
        b'amHL8vM8GZibkZvMYnVuzvbvSr+VKEoyX76W7T9H8InFF3lh1xyBsfhtuRXn55OcvQgpwZP/ZARrLF8sRpkz6fMmf3mJyV/IGf2ZyV9UqF6oUSgu1IzWlBj8pYpk8gQ3'
        b'pbMUmGtWYvCX5gz+UreknwQU/MxPtIHBPyBFEmy73t7PWb7DJJbbVe/t863oK0+sT9PJkBih1wxhJrFFR4QlbWigDGe+BgOunQ4zJj7fs/BNjO7MjbHhrCYryzMx4FJx'
        b'OPvoyjp4aze/JOa6oKUn8RbmjQ3eBo7JkVE2hw3Cw9I4Cy2/4bSolLSo9Chu7K/nleYOUOKfeLqGz0aOBRp+45oTErP1itGe2cm/zK77da24G/e30ffKZFFvytjCYphW'
        b'+2qf8YFWWHhuuBdUGMvjGFanZbLARGymz0fWmkxdmG8bi7z9VmyneEfb2NxNWpCFffJQHozLvC2rGSoP815tBWaPrINHOMBpxPdvKwheO2rGdRnc4i5pTuI+Zc83J3nn'
        b'huisUFB2PvMUfeqxM94U+pnwXISVfsze6enB8dhzXJztmhhb7IH2pzR7cYAy9rp68qbcUWXSkLm2zNo4KfDMwCE+5fxD8aeCbh1DKcG+0Cid24XXeK38raYT/tzXRgYX'
        b'BB0eC0JBaE78JwElSfzXTl0neHPtznjhlPmAtMAg9Mjn9goCPt9qKRHnuN7deAfGBdYO/txWoNRmy1r7NRaZu3liLTPckqDoKrGJu7Den6RAlLmfcXEzc+PlQJKfKpXd'
        b'sEWGM21c0k1inRwWj39p4B4XY4AL+sZ8AfXjO6ByXcF5AY5BM19wXgEr+Pak92DAyZRW2HZsbTFTnIccDhzOmYqYKJKH8+tnXzEkG63mxkMuPJa/yYx73FG9f0ssyIhj'
        b'cBqaUKK2SWIGORHPH2SWyjmBz85EoeBETlagUdWRNFnGLphZ3Fiav78lNyzgrSM44Ci4fkXS0lwv/QAv/8GdBPqj4zJvSsk/c4Jv+fiYpKlrZrt5iJyCGdbSk36Nw0bs'
        b'E8Qdwyne5DyRyfnwSSLGUtJAY6QOCmFMBxq5MzGEWhh/yvoJQ+Hii/b6vK24xZc1w+UlO9srXFlSb8M4J/njUuntBHGG70rbV9mnazooFfS8u1S59Oc3DzeoacYPTu3T'
        b'uuefYXjaN7J/v9bHHiXpbol45uXTL5xWeGVpGSp/2tdd8fG+9sSpLH3XMcO/bt1ZopuS/d+hLg9sPvjjEbfJm6Z73hZe+d4/fd3iIn/U8rs8j+4PU98s2zLU9B+vn2ow'
        b'+mflZ9/ODJmu3bLg/57LQEiioKCx+tXOhAjRj1848onoXIpiWfY7j7XfOWb/i3uVATqlvzDSOfiw+72QqY+v7nnrp/1KWy78ye79Ma2P+sOzhSPzZ78n6z7964o9g8eH'
        b'kuJe+V3HhWaj2r8kVF7seXe6/t1DtXuKzuk3WEdl3oq5cuwXraaZA/6ekw9a/l79z+4LFk7Lx7z+Irpk/UfrC47JJ3f8/GLQkumPjH9UdDz44Pt34s8f2/pun1K7u11Q'
        b'rtenI/7Z3c222wzi9F9SzLwdqR7z3tQDh6rD2sEfb333c60PdhhEtP4gLivvdMekT+q3RvMzWnzSPccOJiXbdfz5LxFDB4pLLp02DrZ8q9vul5fPf/83L+llhie8pWrr'
        b'5P53/bb++6WbXmvZpGdt3lD4wf7fDr762YFP9C0H5Bo26Zwy3sxpxPYxmRLNVQ6quVAUnEjlFKIkvH+Iaa55kSsJbkxzPb6Vr8E5jJ0pEgMEVuHSuqy8AbsMSZ35WSgm'
        b'fUud4MJ1tTxDmaEkCsb7JK/dktpVy5V1wClc5hW+ggvQzdsecAj6uAiWY95cfOmJLFhUNMGa4I3remLfEW50T7zPJH+um2ImtPMNFRsO8NErIzCF91daKh7FZdZVkbVU'
        b'dLnFZxOWH2Ddv/kGLzRHNd82ccmbOxb7PTtN3XBeek0HGKiNx1Z+6HJCNtZZOxnvW3Kbk98mgiqiBlPcskKhS83UHLqwaaWmvMj8AixxupsQHmk+pdPj/BlNptJnh/Ha'
        b'XS7W7GYKNvR7SIw2qgexJ0ocDOU2vOVlGptUOb0MKz2JjBLLuAAFpjICXWgh9dJlN59ENwiPnDi7S/tJrjudjJ5IypfOnqsCVB+Fo+tVSA0s0mQqJDTs4y+fLvbUWiUy'
        b'XYFXI0mHTMJhPsS476ScRIckMtJpvkaH1IPCDM69MIe9WI2VLhsokhItsk6XN2WMw5w1ncpmuGf+RI+DORj/F6V3zf9F1e0p/U1pbcgBp8ANMk7w9RS42wILJU6RUpC0'
        b'S5STqEw6XFMb+kRM34jYb2qS5on836wVDmuDw2ptKnBK14qap8YpWUpckxyWscSrYQrcn5u5eTS4P7N0n05BWLMfieYlw+s8bqt6EFM+1qhaav/T52sstWYyi9UZOX3L'
        b'm+kfSiudCb6evkUa1761GtcX7X0l1MuaLcRGtIG2xbg/J6GyVEI+D0NSpF7EaVxipnNFK63qV1Jfql/dJf3KYaMg2BX96kml+tWYVi4U9n84ZJt/Z6XuC//eBgUaLQwc'
        b'+VgZbinPiQHiIryZEkaPuvp52x7cZ8WUnsSwDBbpkZ6RFpcU89wl8AVnnsS9PF0mj//+G+WNyPExrhoirN0gxlUBezeWP7NjnHgP9F2oYP2oR1w8vXB61QsdCENH+CoG'
        b'ozi32X1tuXl4uE2UrYv1vANuAbuIUPJObnuoXuPnPgl9UBN38rNhQXouE9c+/6t5iYMC7NM69b73D97+4MfiopfULDtlU9TVzqsVW/yg/Edlsy5J8XdHo7f/fmBn8g8M'
        b'ju9Izz2oWbLbP3vbT5R6wyoT9GvdE7U1xe9btYtr8n939yWHskN/7brS9MfBM9/9uCdwfv7gyRc++rnf7SvlI49Kfvi38tmBJY/L70r/93+Lkwx3vfPbz42luUR+kc+B'
        b'k2lrY1tDIZc3aj7CBqLwpWureptriG5qQh7PMpqxW1rRHYbOPxXeKiW3C9okmecB8HA9k4RhXwHHJGECi3jJYhFK9LFUkeYrtVyxqt+1WJd38i+xjTVUXSWTQ7h1dN3r'
        b'm9D124KtKzkqfBvcFdrOKHjWtqfoz/pZ11Pf9cRoDfX9elWjibRy71uvp68caT1Dn13/xqS1eOda0vrFW2MlUrPiUphN5n+0jKIkk+DTgWdDUtMiYuOuSCrtSKq7rqvt'
        b'swHtdORNHQnXOdtIXGJKQhSz7kRF7ngunZVs6uk6M/TxV+kKItiQUkl5caEW6iIY5PsqcmQKHypuGPEUri0XhyWpcbq3iqS5vO+CqZDfhP4z/OXwwBfeenGq6qFL111j'
        b'6Zc1ImKjE8LNwpKiY8M9WEquh1jQ1yKXvP9DYyne+zWj47sG3btZatlJyOdRftzamfd+5WL/EyWCHmngJcl+wtl14ezQGSEp5T9AYiJXN2XqKrYz174lPsQy1h4Ry0PT'
        b'mUHH1TNVQiSIaMjC+E0Y+9I+Y2ph/P2uAFg6h7K23wxlDzOEXS1euWqOfWqG9dXJfdcj5frCjU+e4PDMn35rUpJ0t/naeJYj+HBdDumXrZNVWZD28vJ38jIWefH/q31J'
        b'VbgnNSZYoiuX+cblGnGB7pzFmxPDOILB7YY/ii3/22L3VyTfaYfoVxVFiWQmJ5JSVBBu1n+6wJuampJITqilKidUUaDvt8rxjc8/lxIJ+DoKn++5pSG0SNIQGujLCbmI'
        b'OyxQxqGV/OooGH2SYi0SGO2VvoLd0Jv5JxGrNvoA+6ANauyTsWWfGhTgLC5sOnQQciJwTMaOEKcaauRInWvDO/rKUIX50AHDUHvqFHQpQg2UCHXxMcziY2VosmMlE2Ei'
        b'DKZxwF+ZxSzl4Zj9UXgM4y7w2JmeqsSS6yRfDMCwxQ144AGjR2/gEqtCMw6D9DN/AHpoPb0xqda7sckKc7AzCdpJ2xvACWy5YQ+l0IvF8FDbOfWo92Yo3YU5jjfjbUjp'
        b'XYLZuKNYcNl5q37YVic7d+kg62wLb3gQpGcOtTh9FOZol5NQlQSDWE3DzLjAzOFEE6y0DsEyZeyNxHFNEoE6oIaknS6SeepDHbHZxyYeyiNwRAbaYQYLkon1V2O7H+nv'
        b'41cT6Qgf34QFbPCH6i3YdfkC1kP3oU046gIL+6CM9l4NFeqnYMwP8va60wJmsNkWxm7i0BloEmIvNOMdvAet9HdlLPRjM3Rd3S5WhHvMOGBthg9wJtZW4ShOQ2GEHuQ4'
        b'J8LdSBq2wRMWjSOckvWdsCIOH2OLG9YF6cDINQd8RBJIG47by0DjGeMAqPVm9mOog3yFPf44qYOd2EX/mvWEQmgNpPOogwYznLU9ttveUEsTJ87SB63Zey+YYhMOqmli'
        b'IVbBtH86fVqtorATl+mNQXwIY7SicQE22EQdwaZgaLGGRQ28rxLuCRUxGccwxxcbtkNpyEE5XIZHeprwKAGWdaEghl4fTiEtvNFKD7sid549b2+JtQQKj6A3PYygrh6b'
        b'/ZW2BGclHcnGKb2L26DZC7q2XCBS3QoN2C9H9zhFINWMXSewTA4KT+P8PrrJehg6zJq10PpmIS+QLqHS/Dhrw3QNJrR1sYSOaAE7VG6JcRGLnQ1P3MgsFzFR8BjUQpuv'
        b'A1QQ2CvBIk5uunGCNW05DTnboRUbzZX2k2R8hzbcLj4NvRFhu4yhKlYKSg1uW0KPbWZWrCrWETB2EQvpxLKU0HOwtCkQmk9AMzyEbsgLw1YTbDDdg49wHmbFMC6P93Rx'
        b'Jkw6BdtgKiDo6nFsuemXAEPYQuewZESbIAjBkST3IzREux60YK5PII1dEwgNh6ARCsMJ9XJFhz2xBsbN6ZkJ7IfBmxduaqoF3g7f7xyDrerX96vTpS8S8+0gAFyCOwcI'
        b'rYqd9T0Mr+8hYKuEJhy2IiAfIuB8hEVhWJPAAgcMTuMCFMtizzGsyYb7me4OcTiyFwuNSLFYvnHI4jYUXJL3g0c621llMuxTt5VKxuVQnBBh1bXNYadJx5hUgLJbLtCI'
        b'uXrOUBEEOZgfqQr3od/bL8A6QmPPFhxwcFbQ0rDYJ61rE0Ao1Oahy5bgRxfciIM6UERkJScMew9y5VXuYL4Ya7ygGh8aYKsXlgTiIExKqRPwlWhDF+2EUab8EGt2uFCE'
        b'wzB19doWKN/OglQIpvqvETgUZqnLEUZMRuM9nLthrUVX3gh36XrGiXJNy8WouOH9LTCKHefP4hAhXj7O6l+EJU93WIY+eUOoSSea0AsFh6NwMhGLA2HJYiuz+QV7w6wu'
        b'gdwQlvtCjbubevBVnKb5egkW2i+QqNFEexiDXGsc0tzrZ7jJG3LpzKeDsCeBTq/fGyaM8ZE0NIYbQmcsFGT+J0HkISuYI4C0h0oGkLTqOVOYyjyMrcFSNGoH3k0Kg45U'
        b'RcLKhgM+ZtCrFuoOA8dInZmhs1rEBl0CpMdQQhubgDFXKLhAyJq/E5dcjh2zx0Y3eBCppoD5BLA9BFKzcHcXNBtcIQhuEB2DxeuCgxauWHs5w5TubRJ6SWIqgXlCnBrC'
        b'uJbwCxeTiHR0mWFLPB32goAgqYRAdZCFq+O94NNEFZdNtc9lXLwEHZ60wm6swikjQo3q4zutr2GZljzMrQVYQo96ny20jumrmGcufxumkjiCeU/lOjQRpex18DiYtSMC'
        b'xr2yb2wWX3KGUm3IjaaNLdMAvUSW8g4eI9hplE2EcugLgVpluuABA2WotcUmF+jIoEdyke3kPrYTS+qDHFUR5tkTAenZJAuztjivs4dAYQLmrfGx1lV8kLTpulRsAuZA'
        b'HaFrAd5TpYPqpu31ki436UN32aWOJUHbWDRSHj48QULmIi4G7yXGNBp0TY8gtzPRHqtCiX01GMPAVcKHMgu6ii4Ha6JwxQSTxDaD918+gNVG8dh/86RKFs7T8nIxD3II'
        b'lrtg0srAKDIMJonizCppkaY/j3lKWOQE7db+BBPQeZ0WUYyVRjANnTAElVnYJatrSAe9gN1OQZbwGFsVnExo0wVEIjuIb7ecgknnGF+6zEm4kx5EV9pEHPE+LGRh6RVo'
        b'vCgbhfX20c4WHE+vdM8ghlOQSWShip6pP+qsHUjKcstlKBFd0YFWgm86RYJvaD8fT6tcJvV/d7KbExYnKWN11DnZbZdwZCs0MOiyJHzuclKH1huZrxNge6QRCSJKm8TJ'
        b'F4s4ZoozwtPbQ6FDFpt8FYTwkIUHVxDONEJVBkwIiNoabsIcKzriRr1sHJWFeeiOcjaCZkf7mzCkSdygeQu9UKGCrbKJevEEOM2qhI2N1sb4OMDCBVrOZOM9PShz236I'
        b'GMGsAp3NYyyV9YGBUIYvYcKUYCYOtSXhGC5cPEf0glHgYSIEJIIkH4QWzROmvho4FgTVoafgzmmYV8MO59sX6GA6DmVrQpmfRxAM7Map29scQ4lwDNJ9DCXSqQxBy4Xr'
        b'Qqx3soE5/33ZKo6YCy3QeCyCWPMduuQuHXU67QLsFsOyOtYEaKttZSFaWlB10SPMn5B3yeaMXQKhcW0g1FpAnoeWpRb2J8DwCUK/oni4twfvOAoxR9oH5iNPQp1THEwe'
        b'84IFKDp52PH0ra0sMaGJyGIPzVcoSCQe0IUPZaCDIK14MyHMBB1VJbZawxKUbSE8bd0NCzdxJvUYwW0jcboKrD+ail0ORFNyIs9cgwLnZMKBjptQf3MTQdV05HUciNHB'
        b'RqKBnUQoSo5g+Tn1g0ggX4XdziQZEUD3GByiNbTRbw9OHLrmrEZc8dRWmPQjKJyFqev7CeuXcNARy+jY8onn3T+0nUlkaVAWbbCXQSJWax3nqEEXLTMH2uOgPlw964on'
        b'ttIsU4RZDVATR6sZIIEgTwQVmaykz5Zs2l4LMdAh4pvpgdBpQSpbt463sh/xib74zdgZhXWudL+9uBAMbaG0xNFjMEp4XHQY7iJD9CWsD6AhCi/FXmEcCHMTt+BkChGY'
        b'Ccw3dDqvgOO6Vk5ntgVAcWYVgfU5aJMlsKYdrEoQpvhImIgVJEHY25rC7D4Yv6K497BsGgmwjU5nseYk7QQ6HOh+l2jiyTQ6oxlGgwJ3QoEN5lmFQRvNXALjKdn2Stvd'
        b'YQnHwvE+i8wn8tFwWx9yTM/SZT+SsiVCWA9zJgeP49BFks/qcC6KxMsKYmGDxKCnkchaHhZfu22O9zQIaotOXoQON6z3PUGctSrqBDQFsOLk3bBgRxNWkDzSAYuqhNxt'
        b'0KmGAy5QYXUNa1Q89WMSaZxcWcKP9myFEBjfbXfKQ8demUBsGOpUzLdJ0am1KWgcxin9PXJiJ7yzgw4yZzeBfY+6LvH4ChpzJBjzLsI9ByDCdIzYINEmkhFwPgRbsf1I'
        b'KtGrOuhjpjfWlJHuSehjfhZKdycRm26BYW/MO49dwXZQ4mHmSSeXB8WO8brezmeYFFNy8Rb0hhvjnQjI0cw2wAbiV9UXcCaNYKf+DA6FYpH5PmgQEaDd98BCBwKvZRZe'
        b'GnORdJIqFle4RYdOeSoUa49gIdxPtmXdO62h4BhBTTdWWwVpRR887B0O3aH4KDmYqHLHEVWF3TaHtLbYGBNZn1LCYs1TXnuJGy7vhtYAGrVGmUDrcSKU+J4lHJkPho49'
        b'0KsViQ+TaMIW2mbbJcKEngtRm4j41MCIBYwp0mGWYEMMFOvDxMWUS9rHYTCBHhqBpmgiD03ieFpVjh8B/JQNVNrD0l7it3N497YWPhYkYIsp1t+E2cy3CCjdTAieCChz'
        b'kziYXCKYvIZDUdh/XY5knjzNbDq/3D3bSL6d0tungbVqJEie881ygarb+ruzM6EgTMcnRMmXGPgD9gN5B4ju1xMVodfsmcx0Q00Zhq/Rvc7j/bPHFYlZzsCyaij2YFM8'
        b'Mds+aczJxDr/KFjKTqKvWsIvkiQzygkPQMLDAizFEfBPhutgfpo+9hgRUHQR6gz5J2H1DQOiDa1M2I2lBRRdskvUUaQ3qolu1NNhlHoGkZQ3eNPv5rnYazuVvJDk1QfY'
        b's5PIdl/wsWsqdLalwBC3Ch4lpRzTgBnVDMKS3DQSKKoCvWzkDXE83Ivls/nRIzNwVxYHlaOw6Iwp8+TeobG6oDAFmlVZ40Zov4YTIQSr45ZKpm5EoJri1Jzirx8j1alr'
        b'G6HpGLPt6hpJ0XnW7SNxs0pbC+4lGeifJnwd3oZzzkS5ykk7mSKGPJ/EQvCxJnU39u4i9XYQ796EZiNzIoCPZGmyPOy1cY6yubYjOJowPZfQIS+TMKFZAWqssOKyDbZ4'
        b'7CZkmNRUTw8nAriIg+dx8CLhTfcOgsHWQyS1zNpAIT5KSYIHGaSDF5GurL1Piwhmw3Gi8pNHdtGyq2KhnEQGaewPIF5ZRKBae+wyTgdswXwpuIdjUTRvG4Fbs2DXVfuU'
        b'8+mbfeiOH+40IXxpg+rIDGg9dg1KdmGxdDCWxkPTUXp2AqZI6mzA4rPEJkpJLmnV8lCB+257bnsTiA7jaFYQS+Vp8Dt2+hDTzIYOQ49DmkkwzBJYVXrCw+w4rWiiQE2q'
        b'BOFT5vjgzA1nrHUyIagY1d6JuZYe8QF0duXSxjJ86s2o6mZ310iYlBYILQX0TtUZ7vOgFCV3LL8No1z6EM04bMdFBNE11Wi6m4ZuEgmEJwTYJHuGy9SRuqnqbk7I3CIj'
        b'EB5nSWajMMDn/HTY7mPh8Pt9hQKhm4DwdUKHj2DJ20TLLDUzhEb6xkXAWN29TGexQHBYm46njVhROSFF8wklOu+xWwr6F+Sh/oivapgmsaRqCwKDLjqhOiar78G7rk6e'
        b'UBB/bLMxUZlZ7NmSRXypE9pd1RwuEO2ugtZwrCRBhbAX7x9kxhbSuauvWWQ6wuBmJt7dhJ6oMCxUhM60MEKZWlg+BjnnzmCdF90hfU+ImH+afu2GPhbFXBigwWoQWrLG'
        b'ydbnDQnicreRJvDQJIjGrRR405z5UURNx4j31l5jiWe6cTegwIL4arU/VO0hJWGCIOE8CS7Ve+i0RqDmMClI+RkhnvDYncC8m/hDKQHUhB4pS3mkkBUdNr4BhTYkt80T'
        b'hRgnRtAB4ztIEu6HJtso2ytirJSNUsVGl8swcBAfpZnq49wlHDrvugkGZG9kRnmmhRDxrIZueWYvgEa9LZhLBztEhCiXCGNv8Hkaq4zOsz5IK56QdY6WUHWAttprv1Xh'
        b'nBK2R4RyGlczTbQJ86xJicmhgxlBoqLL1lAmxvEgE29rzA8kmtZ5BMf3EM702ZgCS9wYgKojJAtV0pZy0rQzpYgtVaXTNrph6dQFEiRrocQE2mVxOA6rXKDuOHYEkD5V'
        b'RorLkuwmLA3dEWHsqIvDclAXCnVphCNLxiqZOBCRloa99FNzU5lWXHzwbCCpjyNEiattcMLR+YZ6dCRMGynDjAredyGcunMIRyxdCa0HoACZXadYlZT3KcjdCq0hRAKg'
        b'/rjLea8LaefOa5MwVEQ8fE7bFu+lWdoQjZi4IibS0APD5pthOTMWhw6xlp4mmtiszag48brCfbcJQacPkKRYzCxRxl7RxEth1hJaMgimCmH2AhQmEfvuhsFThLoj7rdh'
        b'JITUvXa61RE3O87ysigmFnP/QgypUj1QeUhb95YpyZxTXkyDwOpoWMCuffTHMi4ZbIb6qHSzDB3WXfcYPrqkjLnKuCiE9kskV89KZ/Yzo0whTAQ/bZQhAjp6zOCE6hUc'
        b'3iyz9Sp2RhJy5IYTSX7ocwFL3LQ2O5DKsgwNaXSWBYpa0udDPHyJBFTZbCXQqYexLdhrpeO+4yhMZpMiUBio420e4SBLHO3RmbOcdWbCW58maYbag3Qiiwq0g4kkoi1d'
        b'xFCWYnEmE2aMYQxKj5oSavRiaxL9o/LKfmgmjkbEqYqB6gN4aAKj+5JJym+3w4nIC3TKBZ5ntRltQaLQPeeEJOwtElLn6hH+PHQmBtcupYd9pkRzJ/GB5lno30kEtQJa'
        b'TqR5kIDdHkNiZ94JRlcfQu7NBJLsdU+QlPBgiyozaXlgX5aGowIMJl4kElzGWwDSIwgDqi7vpmXdIbjpvEWUYE6PEKGNFFzo87wkiMfCkwlEclovnYyhw57E1ihaYU0G'
        b'8eA8eoPEcWyLiISxBJ9DOKWtBo93nSdIaNTCHgcLdiImOKAdhXNxBDRMwB8kpWExDZcuSR9VwyZdK6zxTiGSVqaJXRqkeNVmkwyVA8upJOdMHYcBdW+j4zaGxHk7sC5I'
        b'Djudk+nQW4z2Zm43jtvs46yhjh2atzPtlKHgpMiLAH6QoK8Yem8RIejMPOsCpReIzN4xhUdaUYSTi4QUMzfPJRKTTIIKMT6kfw9jvgxd0lzYFaK3rfY3ArEnyJwIUzMO'
        b'GcPCyUswor/blehCLbtjuofHRNqaiDiMqNNOlnD5lo8Hjdt9AGoSNzl70/TzunQkC47wyIGIcGGI9M7jGTAVnflDBqwjOwkX2vywdFWxPUcLKIeG/fpMtw3yVRTCtAYW'
        b'ecGYjDmMXJDZDANIVHDqAAHC2OGzuAQlFnGHCUSrOYPJ4E5zImTMQtekbgb5RNcIRgtgnDQDfHzV29yYbmwIF485wIAeNKnqbaXzL4OpSMLWB8ePstRVoiuDu6HpMObs'
        b'IFo3AcOBeD8AWqyDWG9oV2iNDCKmMHaWySZd2BmUtldaHHsU6y2x5xoWW8DELn/MS9oH3fEniTF00477SGZtdSKCA3MeWGIWRKyjxYTQ+a75jnOx2HNo0/k0fOxF8FZP'
        b'zCN/v5Yc3I9PgnGiXu00w7iXLKHBcoo3KezVBDJl0J1FmyZ2tRV7LaEukxhKg1c8ARRpLQ1mykmQr2BghyOH47DRbXMiLBJXxpbDMO+Qhg10dpU4fnY7LPsLbPGushwu'
        b'i2mVBZ6bYE6aGUUeHIbemM0uUH9ad+th0rhKaEs4coSo+CKr2U5oMEtwsJRKiuewJh16U3gEQ53oWCMiquWiYIeYVCWYvoC98d5ecdGXSEqdUKElNLPoVwWccIfSCGg4'
        b'a6oNpF3cwfJ4pTAc9odKzROhF7Ox3c1zmxVW78OH22KDscJGxKRWIkL5pEDfx0WPazdo96XhasS8OvHxdqndUK/piwURgc6XTno6EYqX2WNdum0kzu0kgjTKav6TWiiT'
        b'qRhC9GFYMUiPozGMbt+jo2yM2A8PcXqnMSFvIz64TjhXAeNGpPyUqssShxxMCdxE05ZG4pJPKt1OOZKAUCUPMxpHLFgb7euat1X3EoI1EcV5bIZFIdB+KBFm/EiJcBSz'
        b'vFGXiHWATYrtjFikjf1YfUI1Dbq1ZOL3Es1to908JIpYbyV083dlmlMEPorASWXCq2nafKfZERWs0ju/TYogvBkLtYmFl5EIP5xFJ163318+AEYPYnMgwXcz0e55RaaP'
        b'w5BeAB05adVQsRnz/ZyY9KNJ442E6EOPNY6cNkESady2sX4dO+G+hT5haN1RaNlEh9OSTnynLwoeBuoRpDeLfPfrwoMthyEnHIotSfK1J5KoH2CsS8SiJhbz5OFhVNpt'
        b'Yl15MBV0kNjKZBSj46WyGT42MKB0iA65Ept0QuiY5jSwK2YTjsoZZTkcTSWZ7xCMedwgwOoh3teNTVtwJsMNBzRI2KkkNroQS+wgS8Exje6xnQap2WmbAd1HpKxw5Lgh'
        b'9B9TwNYMHFaLvqgDvepqqVC7CcvcY2igXLhnJmvtSTdKggYdyyMpA8+UE4d843F0J9GGAUKj1tCduOxE1KsB2lwd7AWEGyWEmCR8s6ojMKMYjYUHiD+z0GhHGN8qLyRi'
        b'MBsSTHSvh27lEY2ar77pHLHxcnggxzouFhzGAXPiAUW3rkCNbTAyC3mXACYvHdElkjIPBXF7CdX6dFgU5RjJOYukS+Zja6j8lgO4oA0N/rbuKc7EQvuhH0ek6JU7MGmg'
        b'dZj0jQfQ6wCD0nqETa2wvHvTFpJmy02w6gZWsaMpvgoT4pQ9R+jT6qPQtfcczhGvxHp1w6OG2G4LjVGBBDpFWJ9GvGnp2gUc2380APISMogy3rMQHITesGta4eF06gmx'
        b'uADl4TCeSvJzNYlv5XRaD+2IsOYbHiadcA4L0+zco+2JEBRhSTaT/ieUhAR5g0pMNqaLbIpMv3YTHnnTPx9Aswdp5/dhLMUFR89xnHEKF45eOAYNRsQ1Sfd1tscpNxLf'
        b'xhQjrUiOawwi5FiWDSdhLWfnQZzNFItZRu9sOsOjXIJlhkhLuGBKlLiRQHPmME7pkKwbiLUKcY4wZIgtjpZQLSYG16HMnrBXiyNNcTE7xsWFpIE8t4DDBliQlUzy9RL2'
        b'OdDlT7BaNosHZROI5wwJsdMP53ffhBzS+er2OKkq+mF9JOdTG2Em/tvZcA/mmS3rAcz50g4JR3qZoYik3B7oddmMTdd99563pL3V4eBRzL2NFTitR5yxKBjuB5CsNW0u'
        b'E5tsrQPjLgqE98P0YLk1HWtBAiHAkip2XIR8EgjGWTMcK6zSlaU99sib4+iNWJL/CsKvwV17YskV0CEmlUoeW87qOOkQtAwbSattw0fHA6BK5YQcEc15zHEmaWaIEbQD'
        b'OCog7GeaRR1W7lOJ8oH8C+5GthnxCrikdi5rL9F4EsuPJfpAZQrWWvuRQs0E0cnDsTcIQIr3wri6nTshcac2zCvATOD1BBPs302UaxZbIP8Szl9TwILTfoQY+aSZ9LM2'
        b'gKS17KADb9iObUoK4mhtLD0fH3cxxAab3VWEpzfTeyNQLQM16tqEcLUwG6/kamqJM9uZ4ZM4dw4sboVZ5rrr09tGWl9Z+HF7Et/b99N5dMLoNvMkqPbYRWhRQcpPeiY0'
        b'7ad7KHDF6aOKJMAvkGDQejpLG7uUbknTDmqcoFlT/gZhXA39qxqWTZNCr0P7DtIp8zRsvWFaB1rVDtkrXcU7bpivFyKLff5QEwvtMESAVOEbxIyl2JfJjF109wtEe8eJ'
        b'SeRhtwUW3QrZQXyaZKCz9GybF23mzjmcybIg2Qx6CF9qiVUXKQaFZ54njLwPjJmQSNp9kPa2fBPubceaKJK6p1MJYkau6hBgDd3EwttQTHScRI87gdCQCvOZ75KkJEuU'
        b'+dEqIpxgZqnKc8SGiYLFHzfwVTXEKkKCc4bZ9HXrlpgIeR3s3mJrSLe7jKMxMCzrEkqTzJCI1CM6iDO6sIx9h+IVaUf52JEBzPebe/4o1EhBvQ6R8sWr2OQOXWL6tRfm'
        b'o4jX9N8iylhJ+HSP7qJaYTs+cCNKOkRHX4Y1N3AZFo5qYfFBWDDHLkNPLE1gTi5XZqeK9KHDyd9DNKVYSQoHo7YS6E9dNyA0n7PyTiZ469a0prXV7NuM9bv0jbFlz2mS'
        b'GAg9HAkYlrRicVoJm4/swB5lUhvzgyHPEedOwJD8NVaImsSfOiLNDwQE9fMy0KbnAg2KpCL07FOFTgcraLIhYSFfx38T9u/aLyODRWccsVgR7zj6kFa8YEESVuFhfKia'
        b'gtOWSu7W0GWDtQ52J+hQJqFZihC/m2h9QVaogRpL5JojWjAHuQYE6iNCkstuX7EiaKv1hXxFDijmQoh8L1/eQxShFQuT6dR6GSWY3keSR210LDywJXBm1vdaLNHGyYOk'
        b'11THQJEMdMUaQL8UjB2zwxmmn2POGSJgUx5XiZs/tpEhsfoBlBlhnhkdzNhm6LoJDeoElUU7mR9Z+obMwRh/GvneURWsJ9lB5ioTgfI0DySRukcS/R0iEtXQq4lNp7Sv'
        b'sZAKPzq5Zpi/dGU3DJrDohM8MJaGph0kXrUEwsBlUnlG4IF5CNxP02Js+6Bd8n6Yd9ubil27odENek33ncZJaeIpDa47SK1twwkr4nADDEea/DRO2ZCIPWSBywGGRN0a'
        b'fENVQm76bw0i0CnCnAMeNEvjLnv9EzdZBkLRZRxQOW8s4kriyMIclkqK4mCuloiviZPFG48qjHA03TqNlXJTxj4BiVmkUop5C9Xd4Ch3M9VgoUBoK2AWMi3uFXiciq3u'
        b'WLEDpgUC4T4BlgXjPc5EtSM5g+VLQWeilEDoSK/gTCo/Sy5ORbi7noUxiXGMfuYkDRIIqMZuuHsTOI3TIqyZ5awSc3iTVzHk2GGpB/RZ03uHBVjprs8voVDzujuJjhVY'
        b'LbGqYfmulfEqtJj905ikrQf0lreAaPtyOt9w4QFJb00sTnlKmzevVdO1tfGv3cHhI+6mpFSMSwxyxLQbjYW8ba/qJnS7u8mdpAFNBXTeRUJJOTPC8CVmlVO/umKVm9xr'
        b'LHTievJwSWxWYr7bWU5GrEe/rb3AWMx9rOrMf+xzK9rsQy05vipQnyX/4QuWtz1+ejRLwMLMnLjRuKy3uJNZXtLptDyBkc6Rm7XnvHUdtPJjrl4ckDnSomRxwqg378Ol'
        b'v6ns2CFftTM3Y+rMnbu+n2m96L75l7/7lfHxHP2WyZ/XFV8vMhv7W3v6cpPNt5YXbgXP/yDpVavQ4As/+Y9/Xm3c8q23X/+rw0Onl998R3x327vnfHoeu/juaPYtGvl0'
        b'6z9GR5IbpMWpL30S1zrQMtX5WWV24L4zP9N5nNWZZPJqnvqinon9L038e+6d+7DixszoyRsFYztvOI2Fv27+0kxx/H++89Ji9GK1m4nzTL7Ur3/380v2rwZ6//vRuqz9'
        b'PgPqvzQdro01rDX6u6fLw9GIi33/3G89fDnVq8fh4/7I739X/fVHHTUN+6fVzr/mZv531+vGg441Nam/DjvqqPthwbbde/566/XffvCoshPfvWr2HxlvTmv2vrnrn767'
        b'5CeuDzRYNYW2bwmq3vaj2d+8Vqw30BphVxDz6De/Ex12P9/taCc+aPmgddLle690JVS/M/2b7+cn1bx7zPWNT/sXB3MO2U7uDrB+sdX+g6hzya9tevPWO/rlxf94zXss'
        b'5D8uds5tLv7+yE+/G5D1u/O/C7C6WvMdfb8P/vL6dye/Ey7I04t6zWqp8dJ0559n3QxfPu5//sXu3jf3Zyfstbp79DuLuulme4ruff/7n3//irjA6uQVw9AHL966oBH+'
        b'36/6/rdwi4X7kklLc/K/GX375coPpwu7v3ccO9KxIlxP8+i7Sj92O9J26cNaY7v0jD1W3/qHT/nV/xy6btNnhfPG/dFWzhalfxuWjWrKPlop/Wn5i29/9/bZA2aerck/'
        b'+on7wtbSwPD23W179TKOR4x+/Po2k3bHXQMv1Qa+fsNpYuJ7Z6wDv63gHPRH5zm/wG9tfeNhrmdC2D923Nn2UbjqP2xf6Byt3P7dIduKgz8sDLkqU/H3liUbxT9eyPv8'
        b'k/e3BNxYOKD9w/uvvSnl9cpn2t6fnVk0+7P3/U/2Xgv41fKt927/7JBM5uB7H4c8XjgzP59lrMAFv9sQZbpL+Gx9mycpFdjkxUXCmm23U3TfQ2Lq06HtIku+9nLrbos1'
        b'fROeJLUx748Uyf1tmM+neD20ECqmKcsrE5svVU3LVCK638GKmokFellSclcTuUD5dMzNXn3qKs5cTVWWEeicSNwlBhZVVc9VNQkmuaQh/YpSKomko5k4y6qelanKKSvg'
        b'uOoVaYGxihQO6xpksKBUW5yzYk8+/RSU84MTM5uREXhKycCcCPjudqRMjtorro4mh30ifBxqif0HM6zoaw/SzBrToVyOXp5IJ4ZX/PSYSjhCQ+K0DCljnTCeYURvxZiQ'
        b'9DVJykXek2Jzz5RimYGJZ7u42fzfxpz+n/9hrMdR2P+//MF32A4JSUgOiwwJ4YKwX2OxtKYikUi4X7j9c5GI5aRpiOTEUkI5sYyIfsQq0hoaGvJq29Vk1WQ0FLQ0pURa'
        b'rjo76fnbAhtWqMSWBWWLpUTs9+23aSyhzu5T7LMQkfAoH7IdIRLasb/PrX4ioxO01UFNrCLWUBMJzW4LdomEp/hvdolMRMb0vyn9mSMYluKeFplxn7CfHEGvFAuz/ofM'
        b'anlxOa6MypP/0wJWg57FaT9lG38S+m39fw8U/2fAKOQPgwvCZkdkygCANa0QvJmytlcV15lrnGTiRySGVGKBPFaylmJQDJWyApUt4m0kwizGfbJXLJ2uJxQIjqkLDpQ7'
        b'e4kd1E4P7XXOPvrzfSo6d6tcRHfld+rlSY/r7zCcXxpfnAgt/MvF2X2H3jPQu9Me7WP+Y8slhbp+l9dll37gZDZi+eIf7X78Vl3P5O7+wREc6Pz3bY6V6Z4XPn3l/xV3'
        b'dTFRXFF4dmf/AMGfilogqDW1LssuIlVr/an1f10WNESrUJguyyyM7M4OM7MVBNqK+IOAWtGIqEih0RYVt6jRgJrm3ppq0zZt0j70vpjW9MEU08e2pg+9586iTd/aNDGb'
        b'fOzsvXP33nPucs9Z+L5TLVjHPj6SUvDL3Q13xgZbz4QW/3w3fqctcKpx3/M7F5b/sHlJV87vv554aXTw8w/u3f66Oc1yKXSh8LfdWR8d3du3Pt/XU5xVmna//871vpEv'
        b'1z7qleTl398O/1n84OH9h/c2Hfquu+BK+r028tNWLfBFZNLjGSv7WvfODnfM38dPLwkH7dlNYy98mr1q7AG3/4DSGvxsg9JScvrHLKfnG/TikNK5aIGu7MmyynX7G/Vv'
        b'G09uqTveZAtffmRPFt41uS6U71r5lXMmY1mtRLvLGOW/D98uLmZ8WzuXgobN9GwaSGesjNX4Gj7lK3bjT6iti0EOa/9ObjK+ydMk+lqCJpxdQbNt6pJmfN7Q3IKvfKhL'
        b'pvDZqHcOo5ZTf8VdUCLFb+dsFrMHjzimL2ItuMtJp3A9hNvzaJBawuEBfNlpEEYuvVvmohG72wOiG7jDxCV5zDSrGETHGNkknWYLe/CNonEVL0uRCcUlF5O0y8NHS31e'
        b'GrDeyvW6E+1p+CBftBq1Gm97MGPOVHQ2oakGjHMPbmGrmY/joJAL9/i9uNPptUQLuSm4i0cjGuo2WOFXX8PnfRtzi9DNZQsLTDStPmq24SHUYlQ77UXnMn0LCujNPiZe'
        b'gWh2x02czS8twYYumIUusg16eP2sw5ZMOrkhPh+1VTJS9qvo7Fx8xoPboYzdYZ6zbDahUXyg3NC8G0Ht6eka0AD9uXSsfBPNum+hA4llSanZNLVy404Q64uY0I2Zs9ms'
        b'GlMrXKBXV0jfcdYsr58u3MJlNltQi4xHDUr5MO5YQY12i4dibx1+sHiKE3RF4/gIsyp8c4jPal4zHnnaJdlrRvHp243I5aId30zBwxNzp+FrGmrD1xV8tY7GJqkclzXH'
        b'Yqe5xDE2UsqMBqAlnXgZd7jACPQV1GPG/fg93GcwiU4uT0Oja56IzzHlubJp7ODHrUF80YcuzaOuBTExJqpY7EWdeUX4+Otup41bv9be9Eq+Ya5+NCqkUJ9eBZnu91fR'
        b'NA6fc+PjrHFpxWb4L2pGfLc2mWie3o8/xIcyjAq5u0tpynuF8YzycuBvROMUo4yYBe3LxD3GNu1GcXSKWvwgbquhwVdboZlLmmtG7Qsa2WZpXIIHXDTdxV3uXL/bY+Im'
        b'pPPJeAgPM6OvWpbro37xeeiGO4wPO21ooJB7roDHvTOpqZhbTgeaXRvwadSfmwPaxuAVfATKbMVRDws0I1B+jH5kB10bacbm43C3KzZeeWjes/8F/z8dE9OeQVTytICv'
        b'AudRmoMR5B3sMZXppDkStExgf0GoAdpkUxJqZbQnL/97Jtn4Y75BrmIBQw7hw6Ks7qDnGrHqMSUsEktY0nRiqZKCFKOKKBNe01VirWzQRY1YKqPRMOElWSfWEA2s6A81'
        b'IFeLxCrJSkwnfLBGJXxUrSK2kBTWRXoRCSiE3yUpxBrQgpJE+BqxnnahwydLmiRrekAOisSmxCrDUpBMWGsQG/2BWnrzBEUVdV0KNQj1kTBxFEaDteskOsmkyoJFogxa'
        b'VCRV0qKCLkVEOlBEIZZ1m9asI6lKQNVEgTYBx5tMjkSrliw2inUIVVK1pBN7IBgUFV0jqWxhgh6lcaJcTfht/kKSotVIIV0QVTWqktSYHKwJSLJYJYj1QZIkCJpITSUI'
        b'JE2OCtHKUEwLsvpJJGn8gi4nJoMY1dNQzLD3PBWUgtU6ABngbYAGAB2gGiAKUA7wJkAMoBJgO0AVAESzag1AAKACYAeAArAVYBtTpAMA/qG6C6CRcekAShnlFgAmpkYA'
        b'agHeAtgJUAbwBhsZ6Hb18KwJIPSEPAgbKelJWPVH6d/CKtb22BGiO0UM1njIJEFIPE/E448zEtezlECwFpTIgNgKbWJVkdPBaIDELgiBcFgQjC3LiIJAiCM2o7Sp+gBe'
        b'eWc8/v1HPWTiWEb9HguLK4BDx/h3FhokOP77R2fLVCY0+BdFhjCy'
    ))))

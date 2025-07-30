
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
        b'eJy0fQlAFEe6cHX3XDBcIiLe483AMCDetwgiNwioEY0zAz3A6MDgHF5BY0QdFBHjfV/xvuKtUVezVfuS7G6SPd/b7LzskZfdbLLJHjledtdkk/+r6p5hONXd94s0XdXV'
        b'9dXx1XfVV1+/j9r9E+B3Bvy6psBFRGWoCpVxIifyG1AZbxWOKUThOOccJiqsyga0HLmMC3mrSlQ2cOs5q9rKN3AcElUlKKRKr360JLRkVlGarsYheuxWnaNS56626opW'
        b'uasdtbpMW63bWlGtq7NULLVUWY2hoaXVNpe/rGittNVaXbpKT22F2+aodekstaKuwm5xuSDX7dCtcDiX6lbY3NU6CsIYWjEyqA8J8BsPv1raj01w8SIv5+W9glfhVXpV'
        b'XrVX4w3xhnq13jBvuDfCG+mN8vbwRnt7emO8vbyx3t7eOG8fb19vP29/7wDvQO8gr8472DvEO9Q7zDvcO8I7sjKejYhmTXyjogGt0a+Oro9vQPNRvb4BcWht/Fp9SdB9'
        b'CowjjMgGvVBQETzUHPymwm9P2kwFG+4SpI8ssGvg/j2PgGjeDKslrw+nQZ6hkMh7xk6ayObCaWvz5pBG0lyoJ83Zc4uSVGjkLAV5iBvJbb3g6Qcl8c5nqnNTyZVsQ3YS'
        b'2Uy25itRBNkiFITj7Z5YeE6O4z1hudkGB2nKViKFgsNH8f40zyB4VIgPk4eJ7KX8bNKsz1agaLKTXJ4o4LvkRLKe9wyAUqOWkk25qaOhQC7ZVgh1RA7G+8geYTI5S054'
        b'+kAJq72aFsjOl55HkMsOThhVgA9BDayJd8lZ9QBy2EVLADCylUOh2Ty+Mn6iZwg8TycPE7TkWiS56cKbye06cmMZboqcmBaOUP+hCrULH9ZznjgoOLJ/FGnKy4H+HyJb'
        b'BSSQBxw+aCXr4PEIeKwZsTIXX4qHcdiSO3cF2Yo3F9IW4ebkgiS9Cs2epa6fR85A4b50XDZMDseH8S5yHVqUV6hEynqOnCR3SBMUoL3C2/HlVfhoWWJOkiE/ycihsF5C'
        b'KGnC1+E5HZc6sh8349P4QWKWIYFszqO90pLtPLlMtiys4NqttNH+6T9EsbQtjqJ/F0u98V69N8Gb6DV4k7xGb7I3xTvKm1o5WsZdrjEEcJcH3OUY7vIMX7m1fEnQfVe4'
        b'SxvfrwPumiTc/axKjcIQikqZ9+PwHXMXIJb5dW8JoVNi/1gYN3+5lDk2U4OiIC9lHgqNjpgsZRYPUyD4q0vJ/HmkdU0GOofsoZD9bVYfxRfRaMZfe67iFq7YMurhsIec'
        b'PQQefDFiH2cvtEaiGebUd53Pqa2IZTdGfB5ZOjpxEF/0W+6buN9PP4l8yJNC5/ghvkB2w0JqSp4TH4+P49NkS3IWoAc+Vxqfk09aDMbspJx8DtVGhkwl56I8GWxBleCN'
        b'Lrdz+TKPK/N5cptcITfINXKLXCU3yfVITVhoREi4FrfgRrw1NWVM6rhRY0fj2/iKAuEHC0PIJZj/B55cCn07vo7P5OblFGTn55IWWMZbyRZYAJtJMzQo3pBg1Ccl4pfx'
        b'WXyxGCq4RnZpyV7yIjR4O9kD63DXfIR6p4RHL8Hn26ATHVs1/Pb2E29G9IRKQZ5uvhEmdY0A082z6RbYFPNrhZKge3m6qzsjVYoO060ocFI8sL3z5VnONRHuRvxzbK5l'
        b'0as//u5a45XtV/cMVr5x3vLMq3ei3lj46o3tx/ccb7BxLnVFOJl52hC7PStFqNKinC3hE34zSq9009WHz5MXMAwDDEgLXcqJOYqJHL5K9mW7abd6w1CfTDTCkG02cKim'
        b'vwpv45OSY92UoD0bsyQxKT4riUcTyUUVPsAn4QfkLHuN7Cd3TYlJpDlvlBJl4DOqMo5cGr2SPYuCMb0By/cBvp6FLyHEr+Ey8bVFes7Hx+v1gpP2NejCw+VRrymVTsdq'
        b'a62uUuJhRpe1zjLNJ3hsIn3uUtERSw/lojmnyv+SXuELqbXUWF3A76w+hcVZ5fKpTSanp9Zk8mlNpgq71VLrqTOZ9HwrOLin68FJp9WppBdaH8VGV38K40EUr+J4TsWu'
        b'/Nc8D/PEoW9oihH5UnIHX02EfnOIx/tU+BiXnkWaMiv4TtCGzew0ijY8QxxFpSKAOMITI05VZ3QitAPi9CzwxMD92plqVx4+gXdA38g5hM/o8SueXhQProRwuXlARY8r'
        b'EadHxAtr5EX2in7AAnK9sIAcgQdKhG8CZ7gqvbKFnMU3SVPh+AXwaBYiu214v4eCBba0qVabP18D+T0QvoePLGf5WnxqdmJ+fAFkz0HkID5Gzko1NQtkT6IRn52oQtxC'
        b'RM6QzfgKe0J2FACG7pwzBV+E1GqUTw6QDZ4ecD9c5SA7YXLwQWRAhhr8UB/CYCwjO8juyTzCL+QjshH+65RSTdfI0ezneETu4muInIL/+GwIqynXbMX3VGiNDZG98F8/'
        b'Xyr/AG+JI5APXTyMyG34v3Ipm2N8AW/AB/A9AVg6OY7o08PK0WysyLFlhQQe4IYxiHwH/uObNqm2TfjADHwvEqXiPVAK/pMr0xn0Rc/jFvISj8x2EJ60ZNMsD1BnpJwI'
        b'1E9AExPQSDSSHJ3Aah9FGshGslON4vBLKAWlAPncytgxuQwM8CpQqr2keQigFm5BJnKONLKHCdDWV8h1F7m+HJCSnC0iLdwwfC+BEZI29IwPJjmUOFShevRs1BqunmsE'
        b'wdOpqOde5JcpKNKxFcYu53gfb0zxcRXnuNYFy5aOL3SK3eZyVzhq6qY9A+nPKQwPpZNLksn5XBBjnq0IiAVZZBe+DhR5M2DaVj2+JaSm4qZcvAMariUXEb5P7mrxlUHk'
        b'ii36v4/yLi/U8vWf04c3T47AKVEZK0Zy5Zqj66/XrTff2eU+vqFWMVZ36lri9nfefQE/0F/9qPKD7M/DfvTaj7W7zf9xYPTbr5jTX//9L5SjMrJT8RfL3tx/4eTQd/qq'
        b'9E3XDo/bemfQ/YxhH/3u2vSh1TNOL54aOnVBr8TLl8bUlv/zxQvOH/7quc9WfPbTr7+6/b//Uzv9dPPI+b97AISU4fB5a36iUU+2ZA83IKTCF/nRljFuSjQW1pJXQHYh'
        b'jdl5gPlafBXW3zWeHAYcuMkoYhm5HEuaDCDY4ZvzQbJULeaHiviUm8qfKrwT32aMk2wBeQ0WxkW8A2/LUaKeYwRA9Y1YqkM7YF4rEVdMzJgJRFxDdnWgp3pFewLbbtK0'
        b'1toKh2g1UQrLaKuOTluWglNwGvjhv1EJGrgPhfsIPoqL4MK4OM7ZI4jqci5faK3D5ALVodrqclLBwEkJUse28E6Kas7oALGl1WQHiO0r0V0TWyo2p8eU5crCMOBQCX4R'
        b'0EiB+pIdihUgbB96DNFlvLoN0f0/59YhknD2R6EnGobQMx+Emut7DpspiVwXJmej7fA3stKck7U6CWWyXG5yDwQDvnLianPYs7l5UtEzA7QI1r+mpp/ZsHFKCpJo5jG8'
        b'zTU6RQEyymUqK6FyhE/ZtG+d410L4PHJt7752PxHc3VlnuXNyvg9H667sv/agi1i8b6GPpPiYlMM4ofih2ZDqnCtz+S43qmxB9PE4meK4+78sGz/sDTDpph5UbmHqPTw'
        b'ikrkF44rAbmhLxr6X73WrXldzzN0d2v7Jk7FzRL/Z8yfXE5xU/k0fezMRGO2IUFvBLGObAbCuxbF6RSL+5Iteu7JcLBHRbW1YqmpwmkVbW6H0yRz+Qg60mVxDBMj4Ap4'
        b'FxOEd0KFTfSpKxyeWrdzVfdoR3vgjA2gHa1lYQDtznSDdgZKbW/hGz0A67JAicLbCo0gv26GjiYDP2zBpwYB65+KD6rIaXIFH+ugfgRwkMmLHGBhq7zIMQx8MvWgAwbS'
        b'jgzvgIFDJAw8nsUwMOv7keYpuLhaRraZE6MYskUuN4dx08pQKctdmMN0gZXFBWa7bfoKCQV1c3mK35oPI8x5fxibLGWuzAtDwGFSXisyG3oV8VLmW8tjqCVgxvDZ5ik3'
        b'8+KlzHc1/dEEhOLvlJoXNT6fIGWKKh21e0zYu9xc/6Np9VImt3g4yoKSQ2eZ+TcWxkiZr9bEoyKAvrTWXL7UIisyxlUGBGzFfHuBecgMtSBl1o1QUT2o+vIwc5ihX76U'
        b'WVYeytbPwYHmvDPh06XM0PIRKA+g9zOaZ/ZJU0qZH6xMRKUgovaPNvMfhwyQMrfNiANui1b+osrcfzsXIWX+RhfC1Kj7teawj2vKpcwdFREIUGjCllFmAxn/nPy6tS8a'
        b'AyNoijVP+Ued3KT3wgchwADdlLHmRbnh0fI67z2EippRY7TmIT9bYJMynwuJBQEHxY0wmuv/qlgkZU581ogWQY+WTDfzPx/tkDIN9WNRNfxdlGlOTaocKGXOKBwNmICy'
        b'dgrm4vDQ2VLm63GjkBkAPVtv5g/A8tEPY0JH/8Sk0YgcrQFJA41KIqdY5gpyt99oBT5USy0nqbPHMCErBR8hu0bz+DhppBr16Fxyw0Op+BB8jxwcrarBOxD0eYyR3GTZ'
        b'+Ao5jA+P5nolgv6JxvbHjUz0ITeXlIxWFpMXEBqHxgFvZ7lLoOyJ0ULJ8wiNR+PnkJcZRMg8MmC0mrQA7Z6AJoD0JlXdg9wFKfQ6wnv1MCxo4rQU1ur5Qy34ugJvdCA0'
        b'CU0qsrKyy134JZfiGbwZUB/NBIXvmicSsvPw+XwXbwFUTEfpIWNZ3gx8oMylWjaFyv4Zlf0k4e4MfpFsd3GU5yI0C80iu3WsXvJSFLnnUpJmWH+ZKJO8Mom1IR7fXOYS'
        b'FuA7CM1Gs+1hUtl7ZDd+0aW2kQswKygr0sCyQ0PXkOugNuHLlAFm62AsGMh1+HQ9ua4gh0cilINy8GVyndXtwadiyHVeVQDiK8odMUcqfW1qGLmuAlX7KvQK5ZGd+Byr'
        b'XVg8nlznQE/ejVA+yp8jT8si/BIo4teVSrIOoQJUMHohqwbvSwf97boA8sRGhApRIW6qZg+igNdcJdfV5Bi+i2BBFi3G+9iU4XMaUQtTAPdz0BzyYrzU1cPPkWNaBbkO'
        b'5KAYFZN9qfKs5+BjWj7KhYBAlcQRr1T4Fm4kJ7Uq8jAZtChUOjRd4nKbQZfYouXwNtKA0Fw0FxCsWYLZSNaFapVU1ZmH5sUDmkSxqSjuqxVKTYABaH4YOSKh335yYaJW'
        b'PRgki2fQM+QCPiVlHx+Wi5sQaQE9egFaMA/fZtku61TcpACpH7hzGSqbTrZKEvwFsg8fwU38BHyMcouF5A55yf73b7/9duEgRjCzzmaaDX/tWSYtsYwR45Adlm1sojm1'
        b'd5IL2Y7OExSun8CTf47bWtMyuUBIi8q4UBXb7/NRqjfxX6/2HPTq/uRXwzWGYW8cyVi3YcMyfuyhA5sNJwe/jxT3Vvx2xqH1ca9xPc6fNannJt+zJ5I//7N83b3icRue'
        b'96Q1l03NPxu69OJ/Hrya5jUeyV9tv/pWxL1vr017LuydP6xL3xQ3++f9XTN/uwvk3r/vG/aT7C/xTy/1m31qmXXv3cO/vvO7HS3b1l76j6obF1+b/Zu+75eNHv5cfUts'
        b'rzV/v/eDkXMXXA21fhv/4S8+WHr5f0b/glz56bXV34zbvejlj0r/48KKvwlLJ0889EYkCMDUDJc/UQtCbAE1wLUYqAXuErmJL1ArnJd8x001kXmwiF9ITAIFcn2r2IBf'
        b'VLPXyTbNUpDmQHfOT8oxZCtR9GIQ+u8IxPssOeimdkDSPAhUnCayFd8ZlJtNTQeqCXyfIXidezAliQX4hAtfyipIiqeGVNIiAG04TWAaBSA/gPp6ZadSh6IzESFIFomQ'
        b'ZRFPhYnKxUwQoVIAEsM4BQjAIIzwMRz9CftapVKAkBBHc4QIEFKiQEwOg7/O3v469QKIKZ6K7qQTzhnnB87eE5FfMDnSjfGBGuPx1tTxrXIJKLxeYz69YcZgPVmnxDvJ'
        b'enzjMTIJNYiiIJmEe2KZpIMponOpWC3JJC2xTHqITxnXK+nP/VJkmeReiCTrpszbXZZYY0OSTu/MAEkX4Ye1TNAlm8hu21aHS+lKpxVnlnxsLnv1yvbjO881HG84t3/U'
        b'xlEHj2cN2aiPeyPXUmCptu5QXI0r3pdmWLapbFPEa31VxybtsR/r+/YYtCDmR5+HH6n5hZ5jMu20PiOoQYt4nQHk3DzYL7N2gyJ9JRRxuZ2eCrcHhFaT01ppdYIiJaFL'
        b'GB2L5xGvAWRgUmufIHRQuKBw9/jQN4AP9MX1AXxY1w0+UDM32ZlGHgQQItmoT8g36pNy8vHm5Jz83KQc0J1AIcUv4i2hyTCmLxjw5cfiRlt59d/ADT+AtrihksxUDvzC'
        b'nCh8WkttFFT731+NrzH0eLucyThRl9PNqVGgmWXasv4UoXCNh0dFxq8+Ni9ieHC1YRlXEfr+zNeGvBJxOuK1yk0/fC3mtH3PkFMxH5g3Raiipu97YXQ4itiqHanwyPpM'
        b'zmIbM2biIwl+feakjREmNT6UFlBogKS9TJUaptGQqynyLHaNG3HtVJm2mBEqYUaIhosFzHD2C8aLisfiRf8AXtAXN9MKBzK8QP/oBjOoPT4dv5zdSimm5AXpMMGosQqf'
        b'CyGN5FzpY1VpoZ398slV6U736DpDDDb/W6ZHorxxk0ACNedVF8j6cdMKJVIsB/Y/w2y4HKaXMr87ByqZSsfPnNeyWotsjb/+o8JFtwMeDv/Lx+ZPzG+UV1detH5oPmuJ'
        b'rzCkfmh+5tU72wcD6eDeqMyx7DB/KPI/fVO39viz6nS1K7Rk9EtFMRPSR6YPLipkRvQ566O2DnoXkIcS62gQ3E7jC3n5Bh7h7+AzilwOXwvBLW46HYuwdxkwRrItuTCf'
        b'NBeQ4zOz8UUF6l2sGDcd73pSlTi81rrSbRI9VpNocUvIEyUhT1Qo8B5mmgGl2DkggEIKn4IW9YXYrRYR3lr1GFMMbatzUAClaEUtQSj1eTdasQ5KDB6xmDTRXT+8uVCf'
        b'j5sLs+dHUjY+nFxTluEGsUIImmNlMArNlFBIwTbjlF5VpUpGI4GZwRWARgJDIwVDHWGtoiToXkajys70YVUHNFJKaKTNTUUfat+kyOE0zvRIGDOkVImGqXtSNMq75FiM'
        b'bB9FjlW6yumr//nCgK1Xw9elhCl+s7w45fCnaf/1/Ygbu3oo3XNy7uVU3NIcLJ9zePHzk85s7K36jxO6iasHfFI95h/mip69f79+dszes+++Mn/4j5pH7v7r7M9iFo5Q'
        b'f7up6tuHfZS5B5bb/6CeWtKn34F+IENRujepUM9sffjlhWrE4xPcXMcgybrYjJsrc8nDftkG/+axJopZF/Ehnnwnl67eJtJcyCFNGjlFtvJ4A2kezZCT3OoBekvTVPIS'
        b'aUwGxqbI5/BDciCD7eGQK0U60pSPL87LRwBwAzebnCEPuhOVVF0+ao+yYVXWdhjbV8LYPoCtvIKjEhLIRzzPa/jorxUqpy6Au0qKu4CwFB19qgqP21EZTAs7XSyA03QP'
        b'2zm4LR7TSvcH4fFHsV3jMX0f78zHt3ILkxgak0v4FYrKdNAH4RMKcnAIvtI1j5yBZPmJbiijSuW/wCc74HE4/PbqgMeDJDz+U+kP44r4eAFFmW2a2bJp4i+Crm8ltw6h'
        b'OnP9w+Hz5G3f5BDdaWrtMZvtKybI276zLKGqJdRaE2U2pIxJkTJ7rIqu+0bIomtj0drqqVLmYnv/Sj1fB1zWvGhmmknKfG3k2Jzz3I/pgon2aZNkC0yJOmooD4inM9v7'
        b'rZokE+PIeHGncIxCL/+1Sa5TO2t6hpP/O6XlqScNs2RrSdTUqBf5v1JA0WeyNFLmnpDJZV8IH9J2pj5atlbK7Du3z4yLvJnWOWVgOicbmlYmTZqPrtDXh2hEUcosmB0V'
        b'tkeYQQck7E2bbBgpy5gxpVKAwa8zF98eXytlVjmU7iZe4iSW+bKdKjM/vPYAzA/UaR86Mx3Z6XzfH9Q3er5ARRFz/ZglrNwL9nGTvkbv0J4X33bESi8nzy8KixNmUDAJ'
        b'FxaNkzLHecSiBn47B2Aq/xo/Ucr8gb0ydIawj4PXR/wsOVwumRc74iQ1c+nM/b+Z6JIyFRmRurvUnpZitvfI10qZDzJWL/4L+pCDBsX+ipfncndOavEp9Aajc+Ny1PLA'
        b'jR1i3CQ00swhz4+YjWyfffe20jUSsPo/t3vnvphWQFKiZr1+9Wff25x7IHrHz+tian+SuPXns4YPu2Yeu3jjxl/+r+Yt5YSQP/y2/9bmft+t/Prgnx98++bfEz/dP//6'
        b'34sWr/pU9bMPN85XT1g/P94w4dWw4WnqePUM6wtLB/7vpnNXUtb3fOabv7w3+ddb7qpHztn5yTrF5F5LZ4Uu1S7Kv+j5cMTmhT/8XLjT/y9Z4TMmfq7qV3BqrenU1vFj'
        b'1rzzrDm9X8JrB40Ldr/7cvb7f7542jHopxeOZe47dWFx3v0XTzZsebd8cu75+99zxh46tuXdtw+NfvTVb2fffb38lPGtKRseZP0zh0yafCKvZ9LAn2549lf9r/9u253c'
        b'G//83Pd+zidHvrxcMKDw0K+2v4Lxb/5hSC5/NMT1w0/enHV/bfGaXmLs4HX6hbpD7z0/7fNVin9+I6yLsr3dMk0vuCl9IesrJgBj70e2+3l7gLGTi/gso6/9JpDzuYbB'
        b'HGgVzblAnEEhXtVHxXZs8EYnuZ8IryZwSOHBR/F9jmyeOEQf/hgC+/hLN+Q72MhOyXO5pXapqdpht1Fyy2j0PIlGT9QIQKXhdxiTLqI4HdvoiWKSRjQfpggF2s1zodKP'
        b'0O6vdPcHRf8woPKgBQOFBy14aIC+g3i7ympxBpH0bjgO5xwWoOa0istB1PznMd3b6hMW8hItzyFbSRPexrw/WsjmPJgqfG2OQYWmkqsqcge/RPZ0UE+U8l9XJVys1CkP'
        b'lfGillntedCCeFHYEFImWBWiQlRuQA1cmRLuVfK9Cu7V8r0a7jXyvcaqoDyikhdDxNANGsgJ8YJMXRbKqH+YT50mik6ry1VQoQpqi0b+ZWwgk/IZyWEp4MBUqZG5japR'
        b'A9xGDdxGxbiNmnEY1Vp1SdB9V9yGsrOOGruyQNrWf+hUleBzZAPcD0aDyQlyX/JG+STzC6XLA3dH3skcsOVqD5wSpfi2cI94ZsP3MmLSlG/Hv7pZpZm6/q+9XlzUp/jM'
        b'/ewvP1j+pT5/3x+/f/KriLmW+qObVyf6di97GHNUGfXVzd++cDy/5e0bFW88fMvj6bmv5W/748NMX7xhTv3xq9+/Mhzv73N49E7XqHetq/6J3rgyaPzU4/pQJiINXjNW'
        b'XZdrCF5phYOYBBRObg8vKQreHqUeLuur2QodQfbgi2zj1oD6yBu3g2Yx35i+5Bo+koZ3M182qVZyj8ebs+vZAh5P9hJ4MykriewxUKXxJJ8STa5JtKEFn8cPcRNuIS25'
        b'xGtJwi24RY20sTzx4jOTmWKgB3Q8h5sKgQSQ5kQ9Pg9UY68CRYYIbgHvYy2fsgrfYiUM+JyNwEOVhu+zijSz94eRdemjn8FNySDXGbMlK080OSWQF/AGfJIJhzn4DjkJ'
        b'JYx6vBdfz8lPona5Jp7cJrdnd9QBNE9MZVqpiNpkqrWuMJn4wKJ8HkR2eYM4lm3TUbcclfyzOlLGbqP8nkQPND6hwu5iO3Kg+Nrcq3yaOgd1HRCtPpXL7bRa3b4wT22r'
        b'haU7VUblpJ6oTmoRk/b49PRCPVSdiQFCQt0Uvw4iJJv6dklIOrS5jQDIyb8ltDK6QuvREsngwRWc43wak7whCfcKl9Ve2eo5IQ2gZordUlMuWqaFQy1OqtOtjvLD8z96'
        b'IoDVAFDP+ZQmOn5OYwBKAJSTav4RfihPU2eIyT8bXdYb+VT1bpDqVZukue2y1qhOa20jc09Ckl0K6OnTS9sddlHpPx61p39Cge21X/6cc1HzW8uNqI/NH5qf/fjN8urK'
        b'sMrf5qlRz095cmy0nmNL1lmFb+ImsmuxtGqlJYuPD5QQne90EYXbXEHWw1aPtufhJ3Z1Lz86tCklOd8IzmRaS+tqCAZgDIzlGLhEc35njnXw89eIrvG9c4DABeg/vRZw'
        b'2kQd60wmX6jJJLmPw32YybTMY7FLT9j6gkXsdNRZnYCObB2yZdm6GMewrlNHPIvLVWG12/3UoP2KPkcxUCoGRViH6E733+g40R0b6maGvo3uEcaxH56XnJSXkB2prrxs'
        b'fU6SUYVC8VZhCRBf0sB1mHCt/Ne1lQvi81yZsEvYFbkrCn7Dd0Xa+Eoe7uQfkW9WiQYqBwQ5DEcBD6aSQAjwdIVVCZKAegMCvh/SzIM0oBRDWVrL0mpIh7F0OEtrIB3B'
        b'0pEsHQLpKJbuwdKhkI5m6Z4srYV0DEv3YukwSMeydG+WDoeWhcKaiBP7bNCURdCeiFTm6NvMsTaHgfzST+zP5I9IeHcAfdcaKQ6Et4WyKNbzSHFQMy8myVYZQdSJg1nf'
        b'ekD5IQzWUAYrGtLDWHo4S/eU3t6l3qWpFHYpxBHNgmhkkop0DICOVoQ3sjJEjBf1rMYYqCGB1ZDIauglCoxKJIM0VMEI6KORobqgf3KudD6hzRO9yqewgVjrU1BM7Azx'
        b'CirUQZNPl06Ef8UXU2IiiVUhdADlifV7iEdURshERs2ELA0QGTUjMhpGWNRrNSVB90BkBEZkFO/9AxC7TTPpv+xam9tmsdtW0wMW1VadRe6UDRidpbaCntBo/8qkOovT'
        b'UqOjHZykm2WDt5zs1eyZaQU6h1Nn0aUmuT11ditUwh5UOpw1Okdlh4roP6v0fjx92aCbmZ2up1XEp6WnF84tKDUVzM2fOasYHqQV5JrSCzNm6Y2dVlMKYOwWtxuqWmGz'
        b'23XlVl2Fo3Y5rHurSA+O0GZUOJxAUeoctaKttqrTWlgPLB63o8bitlVY7PZVRl1arZRtc+mYGR3qg/7olsOYicDkOjZHHh4685NYu+id/xiMf3hB3aGMrKuXZX4tvS8n'
        b'YIxKCpNGjxo3TpeWV5SVpkvVt6u10z5JkHTxjjp6osZi72QA/UChOzJEuOu8xU9Sj59PS3X5U/96fRJ/lmqT7v+FujqY9zvaZcMK2MGRafh+HrVjGoz4FH6FnlHJnU8a'
        b'c9lhGmp/w/fxMbyLWTEG6FrQ77hJPEoxG8v5YchDveEnhZFTzJxZRBqpxJ5MNsNdYQmtYzs5CvXMzaJ7xPn52fkcdWA+EUJugV54gVUZ0V+FPrQMpMYWw4HiBchDxcVR'
        b'g2fRPefEXOp8mTcnKyCtK/AhfIjs0ONzqCRNTfYOXyM53KQLKCyd8mJzXqQ2UzK5fGFToH2ImZbDUrky5KGsGe8DrRNUgDnB9ZPGPFBVocHJxVlkS54KzSanVORqrUdy'
        b'h7g2gRwmzaTFtYw6cLdAFxSptnV/GMm7fgyP3/59v+Etk2tnjoqa9fqX91v+sSHjxOBEc59PXhhX3Ddxy/oMS3x+w8Gvlm//7BXLgAVll/NdmdNW1J96ofT5hh9VfvbX'
        b'vX+au/77H9SmlPb+JPv9I2+PrXr/hV//9OPv/4ewZv6a7QePecubP/1hZb+eY76YvD//xZWzxi984D08pebqziOzP1SP/PajT7bk/SBp44jTe01fbrs5Prt+2Ll/5L/9'
        b'l3c/WZ884pvjX32U+AeuLO9Pr37mypv5mcrJ5RrTx154zfN+7vsq/O4LK3Y0vTZ33Cu37t9qvq2b/elvvv3D7pz4gkZ9NFN0yBnQ0W6Pxke1MEj6fE9SAtmSzKNe2KvQ'
        b'rHUxp8OcSvywjfcBqH94u51cnjyL6WNzyOHcXGNOviEbw+jlIXwhh2qCffENRe0ifIZpgtiLt6vYJiC5ukDeBJwW6aYi0wATvtp3amDHDGpgr/ciGwRypw/ZzjYK8Va8'
        b'jzxYjR+0cX9kO4XlNjedcXILH1wFsw0VJBJ6Jkremc2FHm0bO1fyWpiNr6pxi4KcZzpoLy5WMmAwZNDO4TXkIryzF5+ThuZlfBXvAXmTtYi8RJ3PleQAR+6SHfgIE0hD'
        b'B5J9eGMuVSNpFQI5SL1pmkskn4org8rp23SJhZEHSnj5Ls+Rq5NYj2JgabQEa6hUOx0fL7jJTrLeTRcs2RZOGpJTqBLarGcH2KQRlpZsIr6uJBsHjpBAncLbyWVyoJJV'
        b'mMdBS45yeLszhWnvz7nJttpx8MiYT9t4i8MH00ewEXCVg0ILTcwHYsAM8RFV48hLwqSyeqnabRkEBO5Cv6AXkR71vJC5Am9geDGe3CqlLxtglJl3cAQ+i2/1EjJGaP07'
        b'bxH/tr2tvTgP8rENWLusFGf5JflRGua5GsZrmBlNwUXwYVwsTw1qYZzkU00dRlTtfngqptOfr1UqUA0lsmv0gyiQROYQSQ+YTi8zkF/xbSdwt2oJT6zp69VSJbFta2d1'
        b'JgcqZiI53cYb1EbHeH9E1zpGh448kd5YKSnVShMVgLrUGp8J0qRlKH5N+tHw0oC0RPkYSBZ+RhbvtFrEJEetfZXeCDAE0VHxNG1SmMptFV02aaG/SY+G0QaArNUt/Kcb'
        b'DCbodgV5cQByYvcC0b/WACe1snYJ3BIAbgyWpv4d+KEy/CWcbGTR87DgLJLGKiFrV60R2w5Fd5LW0zeFmTR4Z2FgeXTViqpAK5KfREb7VwdFaklCdy1ZEmhJ0uPlu6dF'
        b'jg0MO6VWdNWAmkADUkqZ0gKwg618OnladXZ2NL3LNvzfGIQENnaKRyc6CLDpVPlw6WztVqzLaq1hR+NB42E6SYcX6XF5WRErAcUHejjL43Toiiyraqy1bpcuDXrUUV6O'
        b'h25D5+HF5eOMqcYUffcSNf2nRB1t9qV6zsM2mvavxi8nko14K+OAihkcPk9uR9ue/8LAuehp+NWxyo/Nb5ZnWeKt8cUfmt8o/wRSfPkHMfsqXos5vfiDiNdWqnQtg/e9'
        b'MFpA3/s8ZPwXWK9g0ge+A3LG5WD+mo7XURYrZJDD0cwtk9xNn96p3LQYbyZ3+uOLko/CrkFUcEdp0nPpPLkCf4c5RRgWxOUy0YVfzBEv3po8nZzuzpqmpmYr/+kl2cPq'
        b'ebQ8lIulplyZIchlJPbpHNu+tlbTGd0Pq2vD1nZ0YzprXz8IGTPgtcf4T1H7AvJyT+0/JVsXHnk7IEiJ1S3ZFDx2tw00apnwe1yyCs2iRLidllqXJSjaQ/mqDhXROiYx'
        b'K8skcz6Ugargj6XK6jQ/RtGj/zqaUmUHnKTpLai/8tdKqr19PE2FPBMoOh3ugS8F1Dd8ekQ7Da5T7W0KWW+btmya4KI1LP7dyo/NOYDHhuKPzB/uGmteUvmJ+Eez4if6'
        b'rb80zEoYHqafsbxn0cmGiUdGbQR8vg4i6hLtbTJczzN8HgRy9dUOSga+MUahGUUa3MzHdnNVn3bSrsLSVt7Fu8k+2QXrcVuwLqvb5J8hxsaDHbvoD+eXDlf38WNWh3cK'
        b'/MCYQEbRrXtHL1YiOYDg9Gjm6jYI3ti1q1c3zXgKruCLaPtqlwxiU1sO9aTIbPQf8aK0pWvHMzoQkqsONU4G3HWe1O1M5hfvgSrT0bYXWIAOp63KVmtxQzttYlfMtda6'
        b'Qib3o4yjOrGgdG02EiXbDBsCv5MpADLqiq3LPDanPEIi3FW4daIVFFFXp6YquvyhBS5HjV9MswHHtdhdDlaBVLU0yJVWp6trQ5anQmpR+sxs4OW2ZR5aH4g38ZRv65z+'
        b'VgGsbLeFcvLHU5GO3qCaAs9Uuhh3F+AmfHxKbgHd3WfBJQqS5mQFvFmLSWPenCyhWI/PZesWlzuda22LQ9DMqsgaD9nDXKSnEq+yrXnnJby+9X2Er5Hdc4HB7eaWkZua'
        b'+aBJS8flh8fQozhhMPP4ZbKXnEX4yNx8Txpt0wGLyhXhmZdFN2TnkkbDPOZx0ITPlWYZKJSt2XlkCwfU66R+Jd4zjJwu5RHZTQ8v3A4rwuuf91DpMXp6ZnCz6gIVFs1P'
        b'mqdGRc+rLIX4JL41wXb4y3zeVQuv3D5Rl/TmvfB1KUeywmbNeR47uExLVNy616KjZ4Xy2u0fXFXat/SqNvxw9i+iXmq4zVlOXfrNLyd8/v3tCwfeVSiW/cRge6ch5OSZ'
        b'/yk7/+G8X938iNjckUd3z3tv4Qcx/1yc9u3bD98K/3nV0jFzbt9/dqHuwI+/1IdIpzZuVeFzQLJBN8e3yB6mn2treXKQPMDX3NSfzuIZqE2g5zooufRT1UH0cNaLeB15'
        b'OQ+vlyJG3OpPdiQmxZeSU0EnSiczCwA5NhR7c5kRImSFZIYIixJ64WOI2XbwqUx8px3VHgUD7lVoyDnczKwE+EA/fICFrKHiBd6CG5iI0WOAbEUh22PaWW3IcdKkUyxe'
        b'gg+zNijwRrI5YLnAjfgks17gh7KT5R56KsxvvqgIZwYMcvB52Z3xifxxKEVtpRb+Q69DWplBTw2nkhlCmMwWpJSqHV1uU0uBvw2M5AfIYnc8Qggq1soonoXLZs7fpHXs'
        b'5x9d+99006SnYRUKExC5LhnE8QCDGMVUulYK2J0e8xRqTJW0U62gB4C6bMXJQCsmd0r60uemt98v6KQ91Cuqxmmt9Klctqpaq+gLAaLtcTpBU8isUAS1lZrPw/w0sUBi'
        b'Yq0htpBXK3sFhVWGySxN0agElqYElqZgLE3J2JhirbIk6D6Ipe3vlqVJIcYkYZBxh2CtqOtNK9o3iTf43w0chuh6/4GNhPQWewVGkeZZqH5o1KVbaqnyZZGflS8BLtcp'
        b'e6NbY8BxSgonjEsZxTbF6IaVSHVe0Mu6BB+YgEm6TLulSrei2ipvuUGHaZ9bS/g71RX4Woe7EzBOK3Sk1jVJl9ZeyjbL3XkC/thR+QstYBGUyBZyjRxvyx1Jo2xInZsF'
        b'WcUys+QU5IXUaLwT7yTXc8n1HDScnIwgB3qQMx6qT5OrdVm5xqSEHCDkwTUEas7qTzbnzI2Xo1yAdE5ODQgjZ4WxTNq/uJLFOlCozObQgoRxyEP1LXKJbA4F1rGAnOhk'
        b'vyYpJ78kWNhvKgkhD+f1ZOFDepHdNJgUK8Js6dmUrSZSRhu8T5NlyMkzZiclqBBpAqahCVsWQxo81OuAXMFHyO02fD+bNNQaKL8uLIkHGg8SvUGflKNEq8mZENzcB5/V'
        b'C5IyfSslmYEm10YJSDGNwxfILbzTI/EwYU6i9DI0ebpbQ/bzz61OZEHKgMO/ND4xJ18eRA71HCkA6LPk4Ap82ta46ivORT1ytaG/G/D2vXCSEqYoKjY1cakbvW9EffTT'
        b'15sTXhmlKYx6xbw8a3BN35y3ekXeIdkJr/6t5+h5Xx87Wb5ywALDy+crz+8tGvXfv/r0ffcv87Xl3j/vObpk7YGeOxaO/XpPfOmnuSVbfzD45/XqXtH24w21z/q019V3'
        b'M5OWbx/++tFLRuujioWvNfU++XHk7juJ5f85Ftg7O1F8h1xLBc5bD2PEIb6cG1Va45a85PGJSm3CyJWdcXZgpydGStGlXowbyaQDM7mc2yoc4J0RjGuOyiLnc7PzE0DU'
        b'4pGC7NbgJh6/0MsgHWzYMBE/DLD10mWtez7Zs9mWQWF2Ea0Tn8de+UgE2fastJOzw/kcNCsD3y9kLrkqOz9kUB4TWBLJURpazgDClBRTxQBTkSzELCa7o2xsywCfV1e1'
        b'2W8YMCqiSphETuMNEicN+z/aJtBSvihTDcbqja2sfoyKxbjQBBh9qPwbxg760B0B/p+hytU9g3msXJfM8FUS66bUwinSi7Ut1w95Op9ihVSTNSATiAEWWAWXM+0Eg/8e'
        b'0rVg0Fmjn4YZa/wvdcmQ3wgw5MGUcwBdZXwkwHiCLYl6BXNr4uGXy9THOsfRSuiBQie1KFAHR9FRYTKx/Q0n3WRm+yA+gZr7Z9BkJ1stPrXfIE3NR0zF9oW3VXmpNBUk'
        b'ZlWxt/z9YhPY4/9oY6orBHRSFaoPnbd6uNHwCkUMp/pWQWfq24HjGIp9oxL+xb+KiNAwLjqUl0IGKUK5mNj2JaI53SDpnoV51KdoXXkF0lYjh0LJ4drVPFD3neM78LtQ'
        b'+a/rm3b+WiJfphCFMqUNlalERZkafjWisixEVJWFiuoy7S7lLs2uqF1cpbArStQ082IhSEpab1SlwHyxqSdSmDVc1IphzC8ropkvi4B0JEtHsXQkpHuwdDRLR+2KsPaQ'
        b'IgmBBEadhSK9PSo1Yk8xhvpWQY3RuyIAbpTYq5n5jbNyPSqpt1ZvuURPqJP6aVHv8BgoQ/22+or9NmjKekHbOLG/OADuY8WB4qANqKw388NCZXHiEHEo/O0jvzFMHA6l'
        b'+oojxJGQ24/5VqGy/mKCmAh/B3hVUJNBTIIyA70I7o1iMtwPElPEUfBcx/JSxdGQN1gcI46FvCFyzePE8ZA7VJwgToTcYXLuJHEy5A6XU1PEqZAaIaemidMhNVJOzRDT'
        b'IBXPIMwU0+Fez+4zxFlwn8DuM8XZcJ/oDYH7LDEb7g1eDdzniLlwnyQWyUYaQcwXCzaElBlFBdMR5vhUaTXMQex8G0GJLnvpgeQjJkWuBRmQBhCsclqo8CdJbhWrAu5K'
        b'7ZyC2nqcOaGCGqvbVqGjPo0WyWpaIQmgkEFlSqhTsrTYV+kctZKU2JkUp+d9KtNyi91j9YWY/K3wCbPmFhc8mlLtdtdNSk5esWKF0VpRbrR6nI46C/xJdrktblcyTVeu'
        b'BMm59S5JtNjsq4wra+x6lU9IzyvyCVlzM31CdkaxT8gpWuATcovn+4S5s5/JPMf7lBJgjR9uG/tYm50UShbqeVcopb5r+Eaunm/gRG6p4BpYzx/jjiNXgpsX+Xo+FtFY'
        b'xI18PSDzGk4U6rnlyFlWz1FnSHiLOybQCMaiqg+Ui0MxaDxaw9Vq4Lma3jUi+l49MimgVuVxoPUmlahh24sh75k6U0Ta+83J89zqNtf+ha7EezYSknJhkepgOd0Yt6Qh'
        b'm8Q800oKk8akjhofjEYi6CTZlVTW17nqrBW2SptVNHSqEdjcVH8ABuj3kGOQ/UqihLKgojht5Z4udIpJ9PEks2ittABnCaCRGZQUW0U1rd0mjRMgowwHEKxj3z6ic/6o'
        b'l62WbWG19mbkcNdIH2f0cSkfUZbx0bfw75FgTEkp0Kt9Ue3B0l0Xi72u2uILnUd7MsvpdDh9Sled3eZ2LqPMTempg2XidCJmYGAiBEUw5xrU7Ql6xnd/TblUDKP9CuAY'
        b'MbLtQ8dToWh1pIQAT+9KoOdY07oUI/434EjgBxHwI0hqjzRs6lbVWXVmmJIKYPR2Y4b012w2OumJnac4NsBGqctm/T0g3fRj3gydI2IHcLwfXJQMjq7hJbw2MBoCmxCf'
        b'xuIyMR9Sn8a6ss5RC8ptl035KtCUCuZd4KkpB/UYhkIeA12d3VJBt24tbp3danG5dal6o26uy8rQvNxjs7uTbLUwZk4YSdFsplhqEZd4oCAt0LaWjpu+bU9EcSw+RSDg'
        b'eOBEFMcM+k+8AfzenzsjOnPrqGQmERzryopqS22VVedkWeUWuhPhkPZ5oZRFV+d0LLfRPdzyVTSzQ2V0F7jOCrwjnQ4udHCmpXYps8G73A6QGxl5qH0iUiCTAX+TTKxJ'
        b'ZjrGHrb0JUJDKVLA9g5jTB1sO9nro+Hgre5qRysfM+hcNqCpcjX0NbotH+ym21Uf5Yom0YDyk8wyi+1k07Bbo0i5w0HD9Ooqg60vHjYVYrtp6JRIrrA6YZkuB/5oKaf+'
        b'BV3YYdqImOyILWpvUoko8FCahc/ih5mJSVnZBqr25s6nNgqyLQtuC+fG5xiyk1TL8GFUE60hD8k5vIN5teaOWAoK5RVyc058ThKNpdySWIBvkhPFSeR0eiyPxsxWViVO'
        b'YUJwYS1+eS5uchnzc8juFapoFIn3CkayfxE7zThiWHaw0YIG0j5WkJSQm1TsrzhXCYKqBt9TLmNHIMrxd6rS5rji5Xj0StzCkSsOcodFgy/tRw6U4Gayay5pJrvn5nPW'
        b'gUhTyJEbz0zLZPaMKHxyILQE38WbcpRIwPs4vA7fT/ZQk/lafKW/K0uyZuSK5AC+rEA9oK34Ij5AbkgRsx4WVWX0dcWzaE7KNRy5hO9Vldryv0lWuuiR5NV5qb2aJ9fO'
        b'nBOW8aevfp8WfXb7rxdnvR5RPLRvU1a2cnP89l9teO2HV04ZRmrNEz/9U+aR0a+XhWsG9LjRZ8mjrG17BihulB3/3m/1k8Q7L6GGuT/Ytn6r6au/ZP5+2/Szv5w09D/7'
        b'nF11bdbFncsP9h8zYO97i7JPG38/4GSqr2dS/7/VvROuzR+dVdJ449DrLW//8sgrE53fvrnXVJb93p1l/726kZv/XJ9w/I/X9Pc/1n2TOemy+szwW/0ic9+5/dM7y77z'
        b'P78f9V8vpzR+3vDDfnlnnk89O319/Cx9D7aDEdeH3KOzk/vMJNKkRookDl8iZ7OZTcG0kpwiO/CJxCSyhWxOziLNAgrLFFTx5Ih0FvjgOLwdNyUnZUIBDimSOXwdNwyU'
        b'Qj8cIxcGJObk6x158GQwhw/3J6eZdWYluTY4KZEaUPLVSKXgNVnkPrOr2OmOVS5tDDlEXsmF13pz+ITdwSLKTib74+QdGXw/sqPpZh+5ytocWk+OJRr1CTLykHPkOIok'
        b'14RV4fOYkWURj0/lwjK4iXf7Q1JMxlulzZybWfgOswuNsgDaKQo4fIXsm88MMFZ1LbWuZBuM4+vw5mS6kuB1nU5BblkT3fRcz3I93pPbuqxwczJgEL5FLiSpUAK5ryTr'
        b'yf5S1kQbvpvSh2xiPc2lRsDNHNKKPDm48jk3Cyp3f9CK3MIkDllX8su5tDFYCiSGH5IjE6SToviB3n9YVEPWuYfRlzZBw8/n5ufm5hvJZkMui/+wZCo0MgFvU+KXYbE0'
        b'SFamFnUlaSrAlybiHQYVUmRw+Du91U/hW/mvnLfsJRE/U1t6z8xH1JVENh89jyKoM6lkOKJOpzHMsZSey5SMShGSK6qcS91R2enM/rKY0ymQAv/pLHay8l9xJuWkV5n0'
        b'sAMu37YzGjV0cwiz26ZBzVSM7NrNhsWYYZHNQDrggmLM8OxzIk/malMJssF/dSYbpEvMTT7FIwmFVJABXkP5VUAuk0UEKi+4ZFG/IyuStxPayRjtJIrOJYiOjK20o7Ri'
        b'oRyxDQP381MHZfR0L2UVFUU6tsxSUS3t3NdYaxzOVWzrp9LjlHiyi31S5vHMvb0m1VaCDXKEdFucVaC2+Et2u3lSG9g9kbDEv3niF6Ko6GN1Bev8j5EBOj8Hr5Gcl1JW'
        b'h6O4jO00IEjYyefk0LG22gFogn2bQCOk7C6Sw5E8s/gWWmkrAzScseydCeudjC8K6fiEK5zsXxUO+E220Y2QQwkeGvbaQ17CzbntJAr/Po3EavHlUuoCMB+YPd12afUo'
        b'APpUMGD1wKhJpAHfsvVqeMS7zkGVl36Tki8HSa/6RcStX0dNG7ClccK81QmJWXeuR+3+2fZK2wRu499i+69rsBzc9Oe3PmzOnJD2qdlytfdn/SddFVI/V4z6fvyILZoz'
        b'776TdW7Oyg2jfjbzvQ9f33uqwkHi88tsv7ylnlDS7+B/hSb8qvJ85Nurey7eOKQ25sgvLi3N+WPKzw4Pef1/iluGXvvRf36jmf+3Z5/9ZvQrr0977sWfXZ6i0f+hV/ni'
        b't6ccm/o899zmCa8Zz+gjGFG1kBv4QOJYvCEosnTWWEbtF00ChhMYBgUwo6aoeYIdWNYh5ppFXgTifLoN5yBXyelkJpX5OceuNImpfmc4/a5PU+ziZDnQEn7Qg5H/BOwV'
        b'Wok/OYkv+wMASeQf7wTuy3i2F2brWK4/IBPM4nF8dIWVMblUsglfTyyEApcCcUG0NOj7BXJQilZQjO9FQQP8EZkKxuCHK4ZIrgTrF1QmygIbcE5yfRq+gi+QF9hBFHze'
        b'hE/I/FPmnovG+/kn3jrOnYSYW+YDfJEJqdnQ+MCAROMtlJvy5BrewpmSNfgk9qrZqOvxGUciOYj3su0WJVIt4QdmT2NdCdfirdIuDLmY0uboDT6YwfwvKgHyrkRDPgim'
        b'NDw9iIqR5CFej3cKTrwRb+vsgP6Tcju1rDYw/jYlmL+Nkzibih2cCPuW50O/4XnNN7wQ9U9eQbkZjUISwbid5C8Rwa2OkFmIXGlbv7k1bZlaN/FIeKlsq2PELrjEQ12u'
        b'Ya2sbB3ydR1oqn1LOqjqlPwwVZ3q3VRVh19qVOsrcm4e7oUGLhYKiHyblD+c3iN+uO2RYrgxFRgWa6svzFTrMMnKtMsnWMpdku2lE7XeF2UKbI9LNsoc3n8enYdh5Ff3'
        b'9ptb2pXrYEgM7EvnwaWRfUWigXdm1nOsP2ip4JxB++VMqOeO0X6g49warjbWLYhcPUvTkpWCZF6EewX9EgVzeeULHo0McNUamwuaUVHN+NFwYAfUcsWUaXoDM8mGoKet'
        b'ps5uq7C5TdKgu2yOWjZzvpDSVXWSvYoNimyc8ikZ8/ZpJGuvw9mFt3GEqc5pBaZmNbHyc3j5UDpisV9VMGAUPykWrO7lH7g2b3Q6+WzY6MoUqX0UhoJaSJdwlXysZK2B'
        b'AYiWaounnTRIXXU+F5jUiLat1JhMANNpMi2i7WNiUrDdTHrWNRpGs5b4EVFuBZsGNUUzGPUg0O3wSW2iQQRM7DSUH3JEADJ71EZuo/cKP+A4hv/HABNE7ji/hg1CPbc0'
        b'AJ6bco53HkWyLRHu2ao83EkzVCaT3W0ylfMyQ0cwO6vDA+2gz566GZx/LvgpU52nKKjTXUC2mkyVXUG2dgI5gAPG4KUzxL8olvIOndSGJdxSasZi+fSOuU1Jk0Hb0gXS'
        b'QpOsy0ymJbzfQ54hayiQ0aCG0RIdGhYwIoaxIaFAw/x2SwlAF0NQC92sC0KBVji1nQ3A44Ze4R96blq3I18F8+rqYuSr/pU5V/pRj5/W/ZyDbmJa0RVkayerLeAsT4fW'
        b'v+rlICznuCCC3XFtUzOZyfRcp2tbetamn22k22Gd9rM33fFBjAzzDTybYDrYieeE1uXGCKs/BMnhQG675sH6t4iiybQ2wEaY3hlEA9jjTpdAEKbRBh4PGo6bXQ09JXWs'
        b'xobOSV1HaE8wHHHth0OiPknO6xTujc677fKUm0ybuuw2e9x1tyNYQ7StHWfH7W51121WY1Pn3e4ITUBBdIbaKQN0JsKNGE2BdEz7jks7Bb6IAoc7GziqlR5ksoqt+MAG'
        b'o6uTOSZTjQeQcRsvb3ogJsS1GRVW4ImRQQok5Lzf3aiwGnd1PiodobVBhinBo6LriBb9AuPUr904ycIYRZLkViTpYly0JpPb6bGKtuUm0952NJmH0YkONDhQ7F9vc99A'
        b'm/t21maJtiU/vtFhwNLsDoeTNedoJ63uGWh1a7l/vdmxgWbHdtZsiRcMf2yr1Sxikcl0ppMGByGhoz2NUAS3tQi1ZcqtbXXT1tKNcGhX6/0ifg2/RpDbLDTQ1gvSXWVw'
        b'+30qGCMADVI7o7HfQ8GE1q+oUELrU66odtit1EO4xmKrFa1dSaehJpNUp8n0Mi8TFanHYTw9bB767eoegV77S3YtkVI5UOJMWjYZMin0SxydcScWIK7KZLrTqfjHHj0J'
        b'vNCngFfncJlM9zqFxx51DS+GwXNLsLh2NM+5r818dAUdlCuT6UGn0Nmjp+L7zivdQLLVggDz3U4hsUf/R5BC2AK2QIXfC4IVFby66UNnA+rEAttmfdNVshQ5o9yguTKX'
        b'EU4URAVlMr2hIWvo6qCaIN/IH5fWi7xKWBOVBR/RSh8NYVvFttoqXZ1jhbTZPCpFcrnw1NU5aNShR3yK0ceNghXT6J8yn2aZx1Lrtq22Bi8mnxpqqrK5QSe2rqzzq39d'
        b'miNgJBhwk+n1VvKhYeFRI4JHRC4k8SY6LPrkdm6FziVyfS67w02jmtFvZvsi2lq1IV1Zaa1w25ZLMbSB5NotLrdJstf6FCaP0+7cS2s7SC/Uxi05KAZw1KcJKP1aZiCV'
        b'NmWZ8Z0pv04aGluiNsfp5SV6OUMv1HjoPE8vF+jlEr28TC9X6YVJX7fp5RV6uUsvjAl/h14e0st36YXQy+v0Qnf8nN+nlx/Qyw/phQZgd/7cP8b66P8/Do/t/EkccHmT'
        b'bjxQHwuNoFAqeAUX9AN0MaZXF16NSup6O3Ak9WqM0/FcqCpCGyZoBI1Co4hQSX/DhDClhv3SnAgN+wmBXPmHffO6nNwil1xkK2lm3o4zyBGkieM9eN+sDs6OCvmv6512'
        b'zo7+0K+VChaIVsNCzrFAtDTwnBxyjgWdFUNYWs1C0ClZCDq1HHIujKXDWTqEhaBTshB0ajnkXBRL92BpLQtBp2Qh6NRyyLkYlu7F0uEsBJ2ShaBTM9dJpRjH0n1YmoaZ'
        b'68vS/Vg6CtL9WXoAS9OwcgNZehBL07ByOpYezNI9Wdg5JQs7R9MxLOyckoWdo+lekB7B0iNZOhbS8SytZ+neLMickgWZo+k4SBtYOoml+0DayNLJLN0X0iksPYql+0E6'
        b'laVHs3R/SI9h6bEsPQDS41h6PEtLbpbUaZK6WVJ3SVSmY46SqGwwc5FEZUPEGUxOTPNF0lM1pa2HWN+70n6nyX/OM6iQHP+uXTHqqMG8RiostZQulltl3zi3je3z+H07'
        b'WIA1v9ccde+QNlSsbbd+5A2ntu4cVIkKOnFrplTYIh0MEh0VHqoUBGpuU5vD6a/Q5pbsatKr/v2b9LT80gy5BnMXLn1tEtmVsm+KRVfOrIBQnbTtFnwi2CCB9PdVdtt0'
        b'O610QNrUZ3ExL1HaOOYxshxqstjtOg+VsuyrKN9pc9S4zcttOC5V+ijFoTZyVzlH2Z8zirLAPqiR93DOOD8bdDPz53FujSACyzNJVwW7KtlVxa5qdtWwawi7hoIASv9q'
        b'WSqMXcPZNUIU4BrJ7qPYtQe7RrNrT3aNYdde7BrLrr3ZNY5d+7BrX3btx6792XUAuw5k10HAvAWTTuTgOpjlDKnnjw09jjLQs4tA6FWsUdYrjsEaPc5t51xAe+oVvdEa'
        b'RW1flquiuc5hohqY/PB6BbUqrlG4RwDTV9Dg+K4p7pGipl4hmX/d8TS/XtkgcGjZJ43QuyURjRwrtygHrYcWMCEhpMD5FhUSxkoLoMNy6X5BMC6R6eNMPt5keqQ0DXcN'
        b'dz0a3r6Sagv1p2p1yZJsr3pfWDFwf1uN7PqoknYgpUCogskm+pQmj9XtpMFqpOMPvkgp/HrgFJwzg/InuhHopBZzJ93LkQKolDHpoO0hSpAApa1mqLHO4wTJ1gogmGSg'
        b'ZgZ5t8WnMtW4qhjopfRgodJklf6wY4bh/tfYh83gpYpquk3KovJa3B4XiCdOK7WUW+w04lJtpQNazMbVVmmrYA7QIJFINCPw2FLjbu2QL8Zkd1RY7G1P+9OYyNV0c9cF'
        b'7WNrFqphf6VYyb7+pnZDDvIsrEe5rBLua1y+UGik0+2ibt1MtvKpYV7onPgi0vwzI82E2mV10wd6leR+QA0PPtXSFfSL8EExE+rR4yM2sNn8DZX9ypjsF8UcLNpH7NJ0'
        b'yOnih5f+RjHLUBj7ljK9RnOre7cbgacOPQ2C54cIde1DGg06j+TaGtceVMDHdUopc1aoXdp6UNMgRV1wO+QDrtTBUARSbatcBQQ4iDA+pcurM727xvbyN/bRiLbhu+jO'
        b'fo3D3XqqlsUyfZrwVVndwY0LwG0btasjWBo89Smg5nYHtV/b3gZH7GoHVo5k+uSj3G2wroEBuPpOgnX9u6BLugM9OAD6v9N0Uvxal6dcPrjB3NkpPNm/Ro4J1W27mLAk'
        b'VcT2JqlsUwevUbmEhcXpJMqUUVfSmldps1KAsqAAtUOBVu+bAO136RLkcUowwK3Nzf76Y3olsF3IBCmwVsJT4MeC7gYrPjBYYzoGRekCP9Nmzk9Lhsuspzr27vyou3Yk'
        b'Btoxpc3ZexpvxFre9hR++/akF8/KSM6YNbP0CdsjBaJ3/rG79hgD7Slmsx/EsmWfLL+LfjtnIaMugwVGkVyj7Cssq1zywXNdrbXKQvXvp2rlx921MjXQygQ/qvsdnoIa'
        b'LHNmXXzJvPllT0FZAPon3UEfG4A+khF3h2MplWil4/Mg6NbVOegBKRCJPNKB+ycP9gag/9Qd6AkB0JGlgfMuTw3iz92BmNyWgtXAmrVUWYPQsK56lYs6vemK0rILYI3b'
        b'n2Jiz3HOv3QHfFrboW0FandUtYWpi88tnpX5dJj/1+5ApwVASw5/tWKS25EEf1oZty5+1pPDlA+hfNodzIwAzAGdhnTQxec/dSc/6w7g7ADAwZJXI4iEtfRsiLxUpFAb'
        b'RXOLi54O6OfdAc0JAI1mNI5JyPIxl6eJ0un8sjso+a00oT3lonI19bKh9/EzCwtzswtml8565knpprxq/tYd9KIA9L+0h95W2jfqMoFGzLZCe2qZXOgKqN6dxZwH4jU/'
        b'O7OURo436GbPSzfoioqz89MKCkvTDDrah9xZC/QG5rWTSVGmWq6zq9oyCvNhBUnVZablZ+ctkO5L5s4MTpYWpxWUpKWXZheysgCBmQNW2FzUubXObqFhrqSwH0+DJn/v'
        b'bgjnBYZwSBBRl1QjCTEtbDFaXDCKT0PMv+gO6oIA1HHtJ07S4Iy6tNbDadkFmYUwBRkFsymlp6j0VCj0v921ZFGgJb1LGbeX1EaYQpHijuPp1srX3YEytdJ4OSQLO+0o'
        b'AbK2moGCdZGnEXn+0R3w8rZEr5XYUW9vHbVddcJU/F4lbBtkngzQVcBc3+LYFiHzqarrT++l87B02wN+FQ1wNdHySuYqp6Rvmtj1mAqu6uMcFzR2jyYXSx7R1IIVkHEk'
        b'kavVlta5SGbUa5x/oN1cSi/t4kgzGwQNYuCsQWxntTXYdLu9Ii39qJxcpVXwbziCnhvHPgJFXTJX92uvcAa90/VMUWua6Pf+K5VAdjZNdHvCIbTuU3VQbwMeMV2ej4yT'
        b'58gZQbd2jyO6lVsl7ZTJUX6/oX1VUKNEpy5vGtlgYaKfR5OdP6hZoLPGSAW77ndMUGOkAL+BUWCmLn9rlJIe0oUHnt1aazKtaNeaTowMrFyBfmhn21XM+ME2mHwR7QxX'
        b'0wOY04o0dj+++MLb2q1UstlKLXNu9uVhn0o2WSkli5WCGawU1F7FAo/4wtoYq1SyrUrB7E4R7axS2mCjlEq2ZmlajVmSISmirbHKOZST0cc5nN7RD2L6Q6c9wbbSu3D5'
        b'CbUM0f0sjaDQRqc+ZcgMdVehNP7NUBxd/VU9aSiPsFCNoFF66NmsZ/Rkh3Z5eF2YPodcxLvJ1sSCPCN1VqdfLkioVuIr5K6m0wCO9J9rJQrewxL5DYh9PlEQFYHPJyrl'
        b'exX7lKJ0rxbVogbKarx8JSd9NrEsRArTURbKIufyNFwH5GpZiUgxCu7DxB5iNJQIF3sy8h7j69kO4fNsoKcrghqqCCYDFC0pKTYxvw0TR3ejTXwVDVAgiAHOqGBagS8k'
        b'8KVjuK1xiBY7/YrdkPaWTArRFLxz4vK7dRg5tl3rr0Tjr6M9faO7vOuEgP+U/Fm9/p3Aebrz8MxIQ78R1nUw1oDJsFNoT/WxOpnZTuoOntcP72lqnNxdjY1d1hiYdOoZ'
        b'4ff/aKX3w2itU7qqmpKLLUEsp6vJ6JzSd+WUIctdrVDbslpGn5qDoLZnqzJURtGfgK1WPZ6tbn98H2XW2v4kQMDBhkYr9HtOuaLdAFr27WdeXksF1xi4Z15S7J7eKZYK'
        b'zilupbRVBmnVMTV1/uOCzjskBYu+NTR4QHlrPIaR7Vo6sm1x0WGVjsdLZwhYmBj/GTzGJ0AwOoTkBcpYlXMqvZtGL8y9hM4QMLW6OlC4/YcHtEEgWNEu/LMEiyjuFIKO'
        b'DGhkP2x6lKUTFs2GGd7pGotCZSxq8H8KIGhO22HQCHjxUNCc9ukMWOdiWcAfM4atF4mW16MM1CCtG/Zh2fZCcOAlKh9QOvpsGD3RQaWaF/llzKNbYri8M4GObr10T9eF'
        b'j3O3x8hIuBwLkKSkztrudrgtdiBMdA/KNQ1uKL131NRN03M+weWp6VRaUrK3jj5uXFipAn1Ee0mp1QuHIUwrrrQKFUzGSOfkGXBmBgSNbqKgTIRCawR5wIEdq6RPHWoE'
        b'6n9C/UvYx6rqyLk1fvYcxJrJdbLZAM3JIDuLyCV1Ht5Jzndg0rHyX9cOrg2ThqllP8IhZZlAHUyoewn9qqEYSlkw/X6hGEFZrtjjUEQZ/baxEthxtNgTWLCSnbfV0JhY'
        b'3mhvn0q1GCP2gnyVVc3iX0nfQ1aLcfRe7CP2ZW4oarEfS/dn6VBID2DpgSythfQgltaxdBikB7P0EJYOh/RQlh7G0hGQHs7SI1g6UmpRpSCOFOOhLVFWdSWyIWtUAzrJ'
        b'bePKouB5NPRALybA0x7QG05MFA1wH83uk0Qj3PcUJ8pRv2i0kdZvQEZAX6NYb3t6Y7y9vLHe3t64yl4sylZIWcwu9a5YMbWZEydRKDAiAou1RSOP9aLfSxTHwbPJDM54'
        b'cQLLjxVHs5U8xRdG8dDvHOHjinxcoV7p42fP9PHZs3z8rBL4W+rj07N8wszZBT4hIzfXJ8yeWeQTskvgLqsYLulZmT6hoBDuivKgSHEhXEpm0Qdluc7ljCTNzi7SR/j4'
        b'mbN9fEauM4dSNz4b6s4q9vF52T6+oNDHF+X5+GL4WzLLWcAKpJdBgbnQmOw2y94fb535QMjfOpACeSkC0dYVTxRtXeLxnXyutWN0cEUBO00bRk6TO9rliFwNr3OTzYVG'
        b'0pxP45e2Ri1lAUON2ezgYp4hO39OFqyTHHryk364dRpZH4lv4P2LbMPQ95QuGtzv9e3kY/MfzfHW+Oh4S5bFXmkv33nFYFn06s+/e2P7KPaBjOoS1afqFr0ghcc+nojP'
        b'avE5Q5b/5GSPXmvJXQFfIo1zpdjWD+0j8Mv4MKGf5wLQNBjBQX4lORnKIlOnks1K+SvSSfgi3hH0GWmebPQfYHz8njXvp9WBA5TSzwTqvbg6Jhix2n6ZWdm6Z+5UUELV'
        b'6admgXKxEiMDxQKQr1GiRWMiBg5GSj8/7uYjA522p0ITNOm0AW2/2qlheBUqfw5dWoxSIKDWr3ZqGkMA10IA1zQM10IYfmnWhpQE3Xf1aXTaz44fLuxf4KEMYE3P5Fx/'
        b'8EJAq6Qk4xz8CjmQlSNFlKUYMLdoBd6Qhc8KiGyr05Lt+FoOi627lOwRWt8FDCxMmief7s4hzUDAW3Lnx5PN8zVA1xUIvwLY8gBpw8mDOnbEfHhf9eIGIQ4hndn+xdC+'
        b'yEPpeH98ZYkrXD5fjveQu+QSvvAMK/+NWhMdyusQMpvD1MC3PHRuFq3CB4Mjy/D4brsD52q0oES9yrKAhZUR8CZ8KDc7P9dAmvUc0lqTC3hy2uD0QLWoYEL/xCy8M4oe'
        b'TCc7R6ek4A3mXDQE3xTwA0DfLezbh+TM/PmJBfRYcnP+3KAD7fHGpHjSmJxAY/469JrEEHJ9OL7KotH0xPfCcklTdl6yCql686QlIoJswDcZmrLYOeTW8wsT6UgnQQF8'
        b'lyd38ZVxeDs55aHmiWHk/PREaR46gFOTBwBxTjyL/V4UL7ULb8wS0EC8MRzfnkj2s37jF8j6nq7l5JoCcXg/WozPAW/dQl7wzICHy/DDAdK3K9l3K/FWfHZ+HZQtjYdZ'
        b'bDIY8udKEfyl4/ytkS7JSSGMtBhnssGD2s7h5lz5g3tkSx5+meyC/vScLZDDReSCZzIt1EL2kEOtw5fU+omB1vGbk9XHA5B4vIVH+CZ+qB0LNV/0UOzV5OBNZOecZExd'
        b'k1ejfNzskIA34St4AwgLV1csJzfw5hXkGjfQrULh/Xi8HzfrpNjJN/hVLnLNPY9+2iA+JwlQwBA7PIfSTuhXfGujVAjEjDuhQIY3eEZRcow3WRLpUMDwNCWTlpL4eKCJ'
        b'jckFc4O/bIDX4XMh+DtZaGSIh0arKZmBt2rJLXLDRW4vw80rcAPZ5wxbRm4h1Hu0AK09Wc7iEUGRA+QIaaIfYkkyZuVpnytQomi8W8CX8dkKhvncBGX9NBRFP8KZV72Y'
        b'l1YK2Utewqddy8jLJUr5i5qkyWPDS4bxrqVAyD5ZP2tucW5xw4yowwNVBl30tH+8mPzNW9yU9SPfyPlb5c96DT1XrI2ft7P5J+ff3jY05bmW341yon6fnfvBB2k/+spd'
        b'KIwNybKLfSt5i2CaUbS+x0djdsZ/7CsY9P2WS8U9vjcu9MZacVhRn1dufn/4c0L1yxe/2PzJTy2/0X7V/9rsE1+utqWNO787L/XtavPQ6KMTx/3ixPm3e978bcZf6v7c'
        b'55mGTV/s/dmiz7609c3ZOPDR/2PvPcCiurb28XNmhmFgaCJiV+wMvcTeUZSOUuwKSFEUaQNiFxGkijQVFUVFERAUREQFMa6VdtNz001uyk1uersm9yYxJv53mRnqWHK/'
        b'+z3/5/d8IcLAOWfvfdZua6291vsuuDDOIPr1nE1z9shNRhfPu/PsbWuDTx0/bdr+5dr35lz6ZNaa65Ed6ue/TDb0XWkw1nxd8LKpIevqvy3Ojvhy4wtPuvb7bcVnGb8O'
        b'3p4h+evgr+XP/url2jz2YMtXBePU84IMP//io3vVS96dNPq7kB9LZ3/fMX3Z7Iku//5l0ic1dfM6cmd/3z8halbNAByycPvsm/u3Lv0k+OVMu93zzT4x8H7Gt8JlTfHa'
        b'9s8uNr/9t/bQLb+t+Hj48jdyvlf+2m/J9I82ee67L8ZU257IavvFcO6pwqDPB6vGMNzncZC9vXPLJIOI7ppsz1yxhrM11GEpXiRTSsvpqIQbMrgowbOQjadYGXh6gqD0'
        b'NXbrRReKJQHsho3JiyA/zczUOBlb1HglxVQuWCVFrpQGa0mnBuJFyGLYQZLNojuemQsHHNmGPYrMtUodkwR2wHkXEY6RleE0JwE9Cul4hFGRFqgwh7WudjlckGDViFHs'
        b'jvFJWAL55pvxSiK2kMFXmUoqVw6UrCer2U0OLFS2GQ/bdwHAwGbHKF+GgRECDRPsndZCYU+G0fmDU+jUli/DI76Ug0KyVRwTPwNLsIOzZFbOxjIy9fLIOkHaLZtqNEyE'
        b'JihcysAolk7z7GTYasR2ZwqvzqEkKl2i1JtNklKxNRCyzSEPCswVpsbYaL6ZTEa8kpZEGu8vk5Nt6cY6jv10FnPS7B1xv5+rKMiXizakxvrdBvzFyse7Yr4XNBCFZKcI'
        b'6aYLKLYY5wk7t4iUQZSgfKj38gey6zn5+FOC1pappN/SfEdwfSobDlPpBVLYd7IZ+BFdyBGuz5HgIYUDuyMCz4ZTfIyVU7QrAVkHrP1kplgJF5koZGGUT9SZjjADQR4u'
        b'wWY4NhpuQAUbGD5xeIJc1SxjBqT3jkN1oAQPmsMBhk412HmyhvAskO7N/piOxxyJxkikNxLPykhp+7GIj9P9ZAEs17GjwaFgDQGpdP5MOM6ENZtsiXUU94uIi0jLWxJs'
        b'OBAOTGCwGmThgysMiNzRKcAvkPHWisIQrNjsL0sab8qxyrMWJ1DuU76ZTGf7iVmw1B8qNrDB6mu5hXKSOBKlwlcqKIdhC9kO8Bze5PDsWIF78SiTeoCPgzfRFQTFFMla'
        b'aFzLXpVUXws3yWV2DXI0PLDeZFja2bqPMcA9eM2W9Z4Cs/E8uTHAAXKdbR0xn6/sBkQkrQYGWMnptfqRmi+x9jDNwsGQorhYwgUp5m/HqhRqPuMNQzxNZ0c3lR1y4YBz'
        b'd5PWnmwv+8cYG7pAJRzBs2yw4p6Vk7s9uy5Q9zTZqnP8VHLBTzCES0QbOsEIeeGcAk7RHQmKffvi5O3KyLszliHfkz9dIntKvvMouErEDtpH5MSAluJNOCLrWyH/n+eZ'
        b'Za4GptgnUv20u2I/01hUUGpZiUwcRPFSyU9rcZDEhKKlMApaE9FCYkGuG4tDaArufYXUkuUEmkiMpUQ1l8i7BLbSYzt5l9+Yy3lADyWd+5pZ82qNNdlV2khnGfXEJVPx'
        b'JU+m5qIyMiJFF7QsV0euj94U3ROBxfARhFGrSF4vagpNZnSWrBBWEd29uWs9VuwqsVY9BskLD2Cr7ftdHyOWhgZV87fUC+qqc2V1r+yx3OoseHDTg1zgd3Un2LaMU0Wb'
        b'rMFbZ6MBRukGkP+44LW3lWGayKuwBzD3/K5riENfsVqx6s62PTb3qCZ+iZ1n66uf2nO8/hEhLEiLhmj9aS5eDTOBYVhkakpCTIzeWqW6Whn5K7nbkdxuQ9MGOsPFaEtY'
        b'2PWfakbyyAf1v1zXADsWPhEbo4mX2ESjVIjUo+Np3kvUnxaBSViXua23GUa6ZrBgLhq6sY5CyuniHv8UF3HBgzrcRFflBP2oyd0r7lIvW2h1cII0mVUHSM99CwLNxdkp'
        b'brPcITDfgsj8CcIuMbjLZ31+LK13vCfcnH6W2ymsBTHin+C4zVTJPk4V+4AxpP91oznqHiKitlGvT0iNi2J0t9HJDNzcJmJdBA0s6bMsHVfUvLjoCBpwZTOfJdrQjtYg'
        b'8bJ4RQ1OuSZUKbZvJF8NhHl4eEhyanR4OCfjjbax25gQn5IQSQl67WziYtcmR5DCaUiaFvNXL9thSq9ZT9H6NZEKHOeQh7pt7RJB9nAs9/DwBRFxatLC3giDLENM6PGf'
        b'2KvbpQGx36GNgZpq5g0Ru78Or9793FpFzEcvEj0rT2z94IJKZFhwxj5QwlXVbkrIdguihuABaOAOPLHnkZMsZl00A1T7kZ057e7xNWLb2G77jzoyLoyJt/MchRbQhTiX'
        b'Hyt1MubuIK9kQSpV02yDHptsunDHRO82m0o3GijEOmhWdlcAsdi+62viofF4GZqJJpgbSO0suIKlvsxYI9ZLq6nLlgX/JcLdPh2D2gncywlNq0rtj4eYy6OLdkndNbl+'
        b'dj4OUBfC/VD0D4F+jOjqPOQqiRGxbypewapYkzn/lqipEjNRNvHrcCfLcIOvwl9ca2ttF+HHvM/fhH8RHh/zTXjeOp8IMkT8pMIhY0W/w9+qpCl0zcOrRJtu6Fk/0W6n'
        b'ws1eCi7u8+UAuPmheKAnZ+MUKNQhBGdCORuAmGk2sdcAdAtkejAxCEofyT1NxqNaMx6t+xqPo+iZ6COMSVII1z1lXbgF9HMcaqHCduiG7S4ybIfoHbZf6HdXM6o1YsZd'
        b't33YqDV16jlo7QPooG0aajrDHG+oJJxi7AaxGvfy8SwzFzFzLJwbCseYuwoOqWEPf0rmLhqRad6MmYGx/VbOl6qpd879tf0b13lF+pHhseHjmuj16zpeW78ubp1PZEBE'
        b'QIR4Z/DGQRsGBS/73MXAPTFGEJ52MIo4e1x75trVm68fAkEne2Z59Nll1ibGFrJt1n13Ge8kyQO6psu+nUH6xFxvn/xooV9j11P7f4E2/jHWBLKyD13uIaqpG+Lui15f'
        b'k8n74tr1MSZBp9nq3v+O5Kmp3mR1p6fJLml48GGGsCPc7GILQ6U71vTqzB4RI6zX+lz4bXsdu7DQkc51Xg9BOi11lN4++vgBZOl91vc/rvLo7Z/eO68sICT22J03pGr6'
        b'51H3fvaNMElsZ10jU4l2Du2damWvbZUd6uvfVe17mZA8Ukb/LkrLG6tXrB/o30X11PRfkWvmox3IknEfEnNaoqYOOtmTxvYRX4Q/t3bVk5eL7G6fOkKPTU2FMb9I/1nX'
        b'SrYtuqIsWoynV8NBzHegvibZHBFaVkEOmxaQNx9qH8NBNCEAKp2wnnvLsqEmxp5h2TrKBdwHFQpsk0DxWmjV06njHjhjnHr7BXjUr95OpeVN0Nup7z1Gp3bGFwu9DkaH'
        b'aTuA0kJrWGFNmLmijU+QZPdjOlC3KIVsg+zB7MB0SPbQ7GExw3SHpspHPjRd33M80Ngdq17jwSGAH6dlw7WZsG9tl1M9M6I5nORHevT0BxuwY5gyGVuwxZye/uClFDml'
        b'paAckgfxOmRAATtDhbol49ihlBfp3ECo151M+fgvhv0hvY+mcN8WJbTgqRiVnGFyw4XBM9X0UEnAIgFzXKHAFgtZI4kuVgoV2Jwqp150Aa8nQjEUQQ1n/GyDrClKvEKP'
        b'jlqEueTXU2T0XeH0F+fc8Iw6hfQ45giYjmdh3wL/VCqMMSqsVFJp4EUBqydAuS228d19rwUUqiloJJYIcBYOQx4227HDq8blciFlyTB6zOvwZNxYgVd/CDqG0fM6WlYV'
        b'URzC4RC0D2CVOFtgm+6N4OB0KFg5NJXGJWEuFI9iwuqUERMQNqZAARxNxsvBXvb0pIAf4hVBudFOovW1c3HkyiTuWOTuIhNEIo5tkE1e7TycZ0d80Ian8HrXg+RpUOml'
        b'hblZvGgpHnT3CTYUQrFcTvr0qkEqtcexcaYT5WJ3haz1guuc3an96MDB3BikkXHOhkGCMxZsjvvl/v37VwfKhPoh/ekRnsmH7sYCY1xXQH2Ur64SzPFilOv7nX1CbTGX'
        b'1B5sq8IDS728qQpWIJr5M90riL6bPN50NZx+gnPlZkI6XKZxIdpb6Y10QFGNzTlQI6Sux+J0HJ2H/WQYt5ngpSewNnUtKWgJXMBzpuShYlNId1EYYHoonpBjYYjpAssh'
        b'ihlB0EYUvBN40ROvYem6LUYxA5OMsV2epoA8o0ATaMS9eMYFb2xXjcSc6U54VA6H56mgedYTeGQQlEMjHEgNJdUsng1N1AO/x1RwVUihMRQurcCDcsjFbDhoB5l4gyiH'
        b'hSFDY3dBDaYPhRsbRg+FVtLBWXAlZjtmSl1tSSv2j8Sm+f2hFbP94Ri0sfWEjbe/yoaKgsN6mWARvrNk6hMCO3iGs3iJGiz+vQh7O89yu3D2XsBWJeTBnshJkMUKdUvw'
        b'Ek66kEUwPNxuh+1oIZUmlsABCZygb3LESLAxIR+WrNlIDNt6MpBOia6QgWenu5NuKQ0n87Uej4bGj5uAVStI29MHhEBGNOSsw5N41XA9tFtsxdPeLBxj8gaHLq2EesjU'
        b'tdTL0cfAcgCN8IFaFfmfHvieN8JWF6wOUYk8gsFjMh0HZEvBQm8HsmqQjh6okBF97IYLpGNTKiXOtIbrWOPbnYP4ApkmD+QhzlOZxMJByEt1oyOuWg7nup6IC2kPOBMX'
        b'8LAvad8gPlRPwUlqW4iCBApFrMGj81ZDU6oPFeceOIll9l5EgAX+fEI4+3g7BvEYlJ5RFou9iA2aSBeDRUGOSyTC1hBzuIqtW6GALH/UxwY1AyGbxyN4L9aEpWisWC+/'
        b'QMa77LRYsRmvLPby8Q9wcAwI5fzNujiIpVK4lsjWbSwI6gdnLUPZUNg8WiKM7W9KPoXH3ZVFkr2XxXBsTsIrvtrzKgU2SpRDIAf2kjFPhwqeUZkFB6r8KSK/u5+Dd+hS'
        b'HmrTLcxGIFOgjnRTLpRgwSobYlBfhTNeo+Cm1yh3uCgTyBDeYwlHJsPx1JFsfV8igarVZBVtNjdS4CVzbE5JShUFK7U0cDKWM4EnJWFxMF27pGTRqxfUUIb1RM6XU+mp'
        b'k33YOl+VIzPpAxwwA9K9Q227qyJSYbWNggzkk9DB0L98XKA6mGxLuD+UTBMDOxEuMNqkhqls49gE1yBbudmMbP54SFjSn6wxpRvYej/TEBtJQy+rsdlQkGCDuBurHCeM'
        b'V/Xju8EJPANk3PqRB6cIa8gCUEhmVQfjeto2Djt0QUZYYyQKyhUSvAAdeJNdxxtkSF3vcqwtRkA1HCNVl/P9MQcv2OvOiCFH5oyH5KzWJDyu4GEXBoJshEi2yzI4PdSH'
        b'lbobLqm1sSzEQD6G9TLBxEI6AE+MYtkkWAStU8kMUDFHAyUrwAO+K0jf0cLGQ7pBDFbHp7ID/b27sEG3yItkaJRL4PQmOBgNZUymeBUOYKW9ZvpA4zADwWSd1HwDZLDd'
        b'EBp2GHRSNRT7QeUOB9Z8O7tBUEhWy3zHAHa+Kl8tGWAKF/g8O4fn4jCfHUTLJonElG+E2mC4ppEI2Qbp/Jey1943EKrGL+N1lVoMZhThjB/cxhzOL7BIpaekUXgaDuua'
        b'uD+QTnEDYRSUGkAV1hklz2MMY09g+zSyJDAnAeQ695AOE00A7DHES4lYhOWjWEsHGEKuvZO3g4qsVEZTJcZYTbSHVjgXu3v/eol6N1EoTK+t8wxui39vjkX79BGqPMvo'
        b'lc5BV/q/cGBG8e2Ds20882y8B59ZUXNSuHVStnThk4ri8AFz0p+3cnpupNfxVxSrzrw88Bfpqujvxk7ISmltdm9u3b4wwH2xd8mZDaGKt44cDStd99TB58KcZvy1Imab'
        b'rc+vy0vCvOZvH7bLuujkR/lDcj323J99p8DtgzdeuLh86f4Vn0bNGPOxepPVxGq7sEEHQHXv4/ee+OCZgzutrQ4m2935/smV3yT8s99vy5c9X+f97Qrro2urPk5NSBmw'
        b'eJXvVydPv7L6k8MlGbUv7553I/KnvRvl5+q/tdo1YOWBeyMKVh97N/nfUz7e+Z1/SO1bbjc/cprw8gvznpCnvdJUcqBOcchost+i51sqds+p3ujeXCY9L/zmOMFzzo1o'
        b't9ffsJf0D0lyrAtwNHb5ZsTdQ/9Y+7eQLwMnpoR9PDEx9Ppbx/eZ3RCPTrm8/wvrvH/ffD/w07/6mxVuGvLaHz7X+n84Wv2Rm+vp6YUDpy/9d1zak+ZTP/h3RUzbxoOV'
        b'CfHrm1+wemtpe+m3784ctHrbZcmk2dl3mp6edHv5U7/XLVzYUpYxZv2ayIx+3x9acj93unXbjoWRU376csvZQ6/Vfz9ozLPPbX3u6ufRnzZWY3nVhvQvZ7jMy385wXre'
        b'tKRzM9OXrv1w0PhTTrtfVR1/9+dbRtUDrExfnzPrxqWd92B5Zdz0YaP+iHx7dMXw+JkLfvnQeZz5on+mn3jr0hueX2zbOSl0o/PIEtuj3wSfcz70h8P8l/CbfhZ/GVG3'
        b'Pk0+ffjxd3OHfTw55kPZog7Xq58YzXD6p/F4y9Vn3m0yurbp6LC276P9Xvny6bqV77zoPc4/5+f33RpaJt9/xvjFHMOz64q/eiM8zF7l90Ky/5ZRcdlvHol9p/bYFzfW'
        b'B/whuZ8mHyyOUI3jHsMSoPFWnfEbWIzVhoKSBnCQJfU0C72ZjftWaiNv4KT/XLIyXmdhKkS5PI3NnZEqZZucnSQsVgIvbYciHVe8LtyHrNN1inBo5TFBx4h6V2uvi+xQ'
        b'QIuEbr2b50A+uyGCGBTnOhfJRjimWSU3QRNnZinBXLuua+RQvAbHPCS8+LbVRGfWBiXZYRGN/GFBSddHs1iPWLxKFsdyPGHfhWQlOZEHYuyD8u32dk4qzCOWodFyyRNE'
        b'UmehEspZyIqVGm+G4hV7SvGX60AWKSiUOJJFq43VTBSYc5DBmXGat2jJcZZI47ZALXPo+geSsvJZhOCBwE7dVi6M9JX1gyw8Adm8GUTShbhvMFbZa1oih3qJO2RCBzPL'
        b'8YThQrKOd41MSoQG5miG8jCoU8N+RZIpXlLT4MFuYUKQ3Z9HCmGLHDoisYCT2ZzD2o323d3Hlt5SOD+WqDD1UM279ow73V40jutA1vn9MFu6EI9Dwe4JLOhHaUO0WqJB'
        b'5Tk79mMe1gJfQ8E8ULoe6rCd3bFkB160D3SgPUQu4ulZZNBhhwRbiXF3gb07sRGiu2kecHEKUT3SYR/rvTCi3DXpdhBoIkKphIyhrANSF23oHuON16WWpOAGyAvngsuG'
        b'TI/IGV0DfQYmRrEIlAhIn6tzZ5AdsqSbS6Nb1AoUu/AIlGJibZjF9BksJUuDKrjMeP7GQ7m5ntgdg4GziWZweQ1r/Q5PoP3tY0/smAMa3iFzTJcm4OGpbPS5+JD9yJ8y'
        b'7Dl4L1pkICjjqfldgxeZYLbMJlNat9sRnYsYg3jRlk0YaIyjKqNOOYDT0Ayn+29nxU6AYmWnchBqxFUDqLJjYxbOO0JzT9XAg+imOtVgri8LKtpCtu8S0r6uQVLWuE9m'
        b'McQSTxhxn1HZ4hHdXUZJRLAP8hpBJZ6cygLqIKMfUfP9vMlqFCTi0cV2QWo+Y/fjWbzASQQ1DIJwZupWLHVQmfwn4T2qYf9FENzH/9bp+DfvAfnJ3GKfCkJvt5gbdfkq'
        b'GPGNBSNgkt+X0H8S+R/sn9REQpOXKHYeR7yzJvfSOyWi5L5MShH1KBy7TJRT6hyGr2zG/5Fy6SdL8okGKlkyYkMLGrBEyjDREBqSn+SK8X2ZxEQTAmVGf5PS0CdjiUJC'
        b'IXzpVyfkr4SUImE/+ZdclHwnt6bkPSaaEnm6o8791kMU3HnIY554PBJLX7NnAUgs3Cl6S2dIRGdGWOcRyID/tR5VKbq0cKa2hcn7dI2y14VNMY9lFvnVTq/H8h2PBxA2'
        b'PkhkKpGlxwU85JyWntSKDOL48c5ptWEO70r6CHOYG5NCSRkj4uIYmGsX0mPSyFjauoi4bhivHBcsKooDH0bYxEen9SqUB9HYhocv2pTiHR8THm6zNi4hcqPKSYPHqw2c'
        b'SFVHx6TG0eiFrQmpNmkRnCkyKpaSO/YmZO7aiNh4dmMMgyvQ5KZGq3nCKgdjtKGwUjaxUepH52GkKAvTbLxZAAMZnepYinlL6qHBDBE2kanqlIRNvFjdq3lHhYerKCqP'
        b'3pgPIh+tPOjH2HibzZOdKO+3BxFjGhVmyvqIFF1rO8NK+ixR824MiJfFSfHgDVIAheXtJiJt6u+65ITURIbW12eJ5NVTYiNT4yKSeXiKOjE6UgceobaxpQn4DkQEpFqG'
        b'7bI1kfwanRLppGKdoCc8hQo0JVrbL5p+Z2Fs8T0JNzW9H5XAEo8TKYRzX2V264CHEFaKQl+Elcbc0Y6nII9oiDo3+zisk5hh1RjuaKfbLdYYYnpnnsVNojDuT+uaZwEH'
        b'pqVSUFpfqAnSuB1tFFLq27ye5IJlQ0Z49R+XtBMvBhFNrGEelK308E6B8xOXkKobFTMDHIZjBVHfK+ZD28htUGfhgrXYxBxBawd4CUWL+kuF8HDjz2ZGc78/NAWbYn4U'
        b'pBO9JpgSEB+gCTs0FcpQGL1BhueTFOxhU2LmK4YdMBTmhMf9IDERYoUDPgZqmsaoWvPbuOdvmO51sfL8+LcTL30vDB6tfLXRICR2/YXMqKPPza09ueezaOX2121eG75z'
        b'WrXobftG/fQvJu3ot/31k/+8Nu3u+XvSc8PW/vLTZ0HF/Z4Pib4XnlO1epdx/tPPJjUs/+Dz3zzLA/bXLly/PHWR3zhvR9eTR+7njBlade+OSsltgWt4ZkynlSPd4Ke1'
        b'cfINmVYRKIvhFg6xUI5vFufitSU8/PkIlkPXY18D1cMOuKDSDYqYpgytO23V1P3qaKv1O/WD0yFYJIVGbJcypcsALm0P2tzdCNqMRXiY6alGIzZ0Ru5jK54XsT4okYf1'
        b'15gQ+0UTuw8deGOnuGA6ZjG7LBwvJHUaBeIAieMObGBqtxnptczxE3tbZoqhcJPZAGvUxOrKn+rZty6bPZMFom/A6pReqqwB5mm0WdwDN7FWc3r30HgTI5pNyGYpU2Hs'
        b'+lJhdgtTmOJCmQHuk+9SqqBQxaRHXIGuqO5ckk7dd/deBJgSfkfnLptDfq2iu6xTX7tsuvDhA5Il9bSIRqOSzSaM7Dbd4Bi0Gbn64hilOdJHysfVEiL/Iutjiw2Ojteg'
        b'tXaHhE9V8y03mi16ZIX29PCeF9wF5l3fPhW9NjZSHRYZF0tK4ZzBWnyrGIpXGbneid3h5Em/z2O36UOP71KqRj7TWNSjgy7skaIbq6NZMxOSo+gfyA7Q5wqtQcPX2wan'
        b'BaF+4QzhLjUxLiEiSvv2WoH0WSiFUNUh1tHNQxMYrE6NTeGY9LpG9b1vPLRV8+aFhDv82UdD//Sj3ov+7KNzl63407XOn//nH/X4s48u83T784+6h9vo0a4e4eEn9ASe'
        b'esdwjhyu60RHOdjYaYa/Xbfo1e7htSy8rm/lRF/Q7ILkCAYU3jmGHyc+dilVZ/mqsNndyaXbbGFxvRyel08nUuHm2Ig/JymPkNA+mtDJKU7XGN4OPt1iox6igcmELoy3'
        b'Og2sP6cMPxhuKJgIOf5Km3C/9PW7BXZQsArb8bhaSXaOof3xpABH4MBGdrawLohs380uLo5OLgaCxFvAE7DHiKXuejoOtg9wIopELlUeDom+Qyx4zOAFokkctQ/wgWyy'
        b'E0kgQ5wCWVjNAxFO2oXZB3g7wFX6TI44AyrgmErGztumQjPsZWdfK4iCdslAkA4RZ2I9VPIAjVwshevkcmPKbF9sJTs/HhRHbXbhxV6HHDipdkseDifIfpRA9I+ZK/lB'
        b'VLkSDqvxijm2byT7mwSrRTs4EcFeAM/j1XH0YN96k+AsOBNF5RwLfZBAuSYAA1rxIg1ZKMD0cJWEtUOCRweyRmLNKl0ji7Gdp32fgxosZY3Egq26Vs4N4oKp83agTYE6'
        b'PKFrS501kz+W7ZpN2o8XlmvaDy1TVFJWKCnyzAZe5SXSRk2dK6GZtScEDg5mFdLTdl2NETIulxozD+VmIyhMIaNAaiQ6k1sq2JVYGZxQmiZDnaG5IEgdxNlQDSd4K9um'
        b'kwY242UlVmGJmShITcTZNompFHMRjmGrhS9VfoNZoDA9K15KQ0pOQ8kOom0XYCa0QxlUhFilkV/LyKA6gyWkN8ug3dIAD641MCXf/MlwKJhh05/ojJbmUDMaj8Y2vKqQ'
        b'qSms54dj3EJfvRGALhaGP7Sp7xbvqvase+qZp4J/sF6+JT1435k74XPfvBUhhLoNlY7Z2/xPi5zcI0cMP1KV/zLhy1eff+HXtN2V0YZOtVHj/rF3VZD/3LLv/rJ6a1Dt'
        b'p8szpgxt+a3GauLBpCX96/eYpf50aH7/q35DLrzb/N5XU8waR25zko3f80nNqduyvEjnD54oKf39u3PXb/zucfD03bh1X0Qt/G7AX55IxKmpkzx/Hj5patPgb6STvn1p'
        b'Vsq0Z78MC3H/ee8H98rPXZ1SHd/2xumSgcm7f/jHX54aV7Za/tLL3+9bM2/p563zEk5+veZ7pyc2fvj+5pkDYuYF3su5+aLK8Q+xaMLqv1QfVVlxVT1rB1zTOv2VUG6v'
        b'8fkTGWZxn3hjAOka6vQ/ZaP1+5MuuYAneEzZtXjcZ6+JpVZDDtW6TRykhpA/hxPNl5CxeYgo+xHYyE405tpCM1PF4QpkQB6FJBiEF70MBBlkirjXCXN4tfXuizT5uiUx'
        b'PGVXhCYyOk7wy2d8obCbGo83qCofn8Zb1Qjp2GZPA1WojqzAGysxXwJ7fLGcHbFgVswTaiW2TJLTQ+Z8MmYTtnBS+3RsgouQnzgxOY6iR2QLWERMPJ69u3cqnKSXPFLk'
        b'5BIZgcUboIK/SymUmNFLUAuFtMhcetRzDK7znOhKzNrE8mCRHstrsrZZImzAFH6yclyAPPVmM9yHh8jjUC3gMazDFu5F7pgVrYYCItt2aKeNKhLwsg0cYI1KDsMO8iB1'
        b'AhuQB88JWDEdM/lxUZPlQDL1TaAtlNjHcIHUsjaGXRmTBvvUm5NIH3fQ2soFLFjpzK74+MAFeuXiHFIRHKJ4DGcn8sOKtmBsp+bVLujoamFx82pvkJ6szweEUsvUREtm'
        b'Nkh43zZIOLU5qPuSWSHkn4y5VLk7VMLsEe2XCcvKNJZoHZa6f+QJcu99yf1t/bpHRJO6A7QQLyxZ06Srjp2c282EYXGM5F0KdGZLri6nMp98uvUA2+XWA6K0e7eJWHHU'
        b'WmG5ZAGqgT3QtW7LwgK9A24rw+aFBgV5Bszz9gzmqKQ61K3bysSI2HhtsiXNAb1t3CUbkfk+dXmoXVJGM7qjczGwrixRY5qxd+TCGvL/J6d88kJqN9J8Vhp4pjC0kNKx'
        b'oPhdLjczGDSHOt1lkj8JDiqzsLCQmFHGOplwf9JWhWg1XMGjoybCPh9togNeVWuOq0RhyEJZLNlzzvWKBzbR/FTbid0Z7CioGAcUq5BpIMX4ZwosZkS+6GcKMEbhxfjf'
        b'Oz9bUHTPqP7ss1XUAN1n66iB5PMg9nlw1JCooVHDKpSUGy9bHiNGDY8akamg6KJlhmVilLLMpExRZkm/okbuN4xyzaaAZXJiC4+NGsfAtwwZp9yETCHKNkpFOfPoc2XK'
        b'MkmMhDzVn/yzKLOM5b9ZktIsy4zKjGNkUXZR9qQ8NwqGRkvMNso2zbbMtopRMPgwWrIRC8CVs4DcfjHyKOcol0wFRTOVCSuUzLZ2v21Jp8c8xqvB4OdiopPvunXTQnvf'
        b'oKGE63rTXSei0k6LVSdMU6dEsZ9uLi5ubtOoZjxtizpqGp0yTi4uruQf0bndVdLbsoDAIP/bMi/vhV63ZaFBCxfVircl8z3JdyNaZVhggN/yWlkydSTcNmCW6G0jDkAc'
        b'Sz4axBB7Wv041brSamXJZXSeHaTfDtGZK/MOCOaYlI9Z1lSyqHUvK/kkKzB4/pK5dz3Wp6QkTnN2TktLc1LHbnGkNkIyTbh1jNQkKjpFJmxyjop27tFCJ2JJuLg5kfpU'
        b'ks7yayUMAy05jMI8EgH5Bc6b6xdGTIe742mj53l4sxaSn4sittKFLoh6ltUppFAnlyfId7Lm0cJqxWR/jhR5lLbVJNg7YKGfZ5jH3JB5Xo9YlCtZo8u6vfLdyT0enJec'
        b'oFZ7MJumexl+Cev81etYSa60JElnSaSBNbQs8x7yuDtE/0vdHdCn8FTKbqXQ4ZZ8vo+ypyY30L/2KGQqK8Q9uZ5e01+56137x3jT24ZR0TERqXEpTPysL/8ryRJ9otf1'
        b'lYTCzYiLUGvOowA3AVEhieUU4x/7dmQ/A5adsqDoOd8Ik3JTXXZKXvoDslNuKygnbQoZ2fqztujXQo4i231FcdI+qz+v4TJ5jZnkk9qlbx0gXXj6AbkND6qz1pDv2bF9'
        b'bNwbdbs3Half0jaFBPTKhjDWSphGx7JsCEFLncoB4mKMdZkOxo+U6SBlnSn7OMOwD9enN09mjt0W3cUByrmR+GEVXaMf4PAM1pIY2yQypgqmyKin9b7R0abHPLKxne+p'
        b'evBtdB4+9I6pNrZ26lh68rV5stMku0cokk9tG9t5Xg+/WTOF6c0ONg+rR//yYmPrHfJYT7g+4IlHXSloET0brc+3rPGPcUcSzzPXsGJpGRf0PUm3U/5Yz2GTmBybkByb'
        b'spUDG9va0U2a8o3Rbdqub3ejHd286T10K7WjvmU7ugfaqZw6D2cnObk5uUzT3NJ3MZ3nuC7sVk2pnX+exP7Mi9b3YhwbQ/NqfSBfcPlMUDPwC73iYacb07oDFbBJ1jeO'
        b'hQZoQG+bOsEqpukYdnvjUVBsCN1Rfh8n9fQ/co2RI1J3P3OzsjCC6IgUOqDUWuq4LvAe9CBbD9oBddWSctIikjVRB10YO5h0bIKjo+m7psZ1YaPrs6h5c0M8FwYGLQ+j'
        b'1EiBwZ5hlBUnmLVSd+LPOfL0CokvQlw+jMVKgxaj7TetAadxMvd9QN7peGaHGbyETr+wXY81xU5viAHroUQ+T9WcYa/HEmPH3057S2x831AMHPiDKKxawuD1EfE2nqFB'
        b'ehzo8TbBabEp26KT41jHpTyg8XxB1DOXyITxTomI28oe1L/C2ekfsxrEEt4hnUAmdORrukQHasLPsvS8UQqPmOiCfN7t2W6ANHpXLVZSr8MFIh6NVqXWDt8e5fbdJxrS'
        b'yc56Gdnn2ui4hPh1tKSHOOGphmLUS6UyD2A5AhPi4AaW+mIhFkmpJxiysEq0hTNQxzSu1d6WLERiOZRqkhEhm6erMw/1cMjFGrWpaaoLh1XFBtgHJSyHxBtOzKcmMRRg'
        b'K/lqhlyZYDpzMGZKMD8JalMpuekUOKsN0tVkjy3ZPbpXOk53CFJ/Ax8Jsbf3UqDTDKxRSXiW4LmpI5ivmPqJ8cYQE3E2FE9mHu1NeACzlKYUG126AuocxNmrwlkaD57E'
        b'7K4os53t0GXQJJqaBlGcWVvHgFBbW8zDAmfMc6CYolAL5/EyRU51pI6/w/1FUtzFBawxLjSIl0KiwmlDjoqKB7Y7sjMPSYyh4paEIdM6jLGaJbDsQ8gZsrULSupSLycf'
        b'f8wl7+wchDl+i72kQUTM9Ota/4lwdus4AW7KlFgesyIWE94W1SepP8F17rj9rsYwx8JzXUzpN7ArvmRF4798rmS8ZGM5N6p/0DgLE2j9UfGXAckeaS2Dt3z/4/0UWcax'
        b'6AjFDONBUY3PLX3htcl3rjzfOHN/7osltTXLoz/1uhYzuf/4lwy/U1Vc98iPinC+VHWk0uRi0+ARrkk/7J68aHpt9vT3PkwtnvzO0xuvJf/yvnlRdchfvxr3209Neb87'
        b'Xr/+t7/7HLcuK/z0YpjLcy5GMb+pTLlPdC8ehlp7J0cvuIQnWWzEGYnLcLzIgjUWmUk4rjPFonag4R2GglmQdCy0uRLNfy938t6ATLxKvbz+g7uEa8RhCXPyrorErC6h'
        b'9DPHa4JMZkEZCzKJgYIA30BHTMcG7nlOdmPPYRtece4ciSxWnIzaS3FRESyiFg5hOxylMRtbt/eEz9wbxG4ZbodXdcCGWmcuFkDZfKjDHBZ+nER6uYLds3SHFiuxG07i'
        b'vM0c0vGCJR63d/KGKlkPSEuoNGD+31kB0K6Lul8OF5kDfiAc557uFms4QKqh8+4y9c6fghJ/cQHehH3caV1gBk1kyvthzhAihbWiK1yGqm5oF8b/kQtOB8I3R59RtcOS'
        b'OuKkPCaWopnIRMV9uYT+lNDgEsYEbSaRiEP0mEIauDkN5M46sS+3clw3jDv/B9piLSMe0xZ7HLw7TpV52yCMQf7pA+PaTz5xtLu+KtQxUDs9ghbcE6mOeq+CveYG3ZZR'
        b'ftnbMko1qzLsKy6XR73SINjbhhpG8uQ2sY+EenPtjhIi6BLquRFpojEjTTnSeLZ5jPljps1rjcmavozJuVFR6u682trNtA/Hn04N622TxthMo0ritHAdEEp4H4f+Dhql'
        b'RgfuRaMsewel9uSI5BTJ1F7vVFVTqDRTNIr8I5lIGuVWxyL8MCuJk4jxZ/ug+o1Q28TEJURQF4IN47TVkHbqi7iJiO9GkNeTIVhfK7qZDn0R+KZEb+F6cYqO83YTjxDV'
        b'E/JJ7omNokpdpyg6aQb5O9jYkoYms1djStvooAVOTk6jVXrUTR43wcKXI+ho6sJ8rSuZU3tyNbjzep/l6Z7pZOrUDAFNTFd33s4+y7AN8lzgSQ9wPMMCQv09PIMcbLTW'
        b'CSc31RsHxuKV9ZPcJiTy+O0HlLClL4NPD5vsA4qj/+nsQSrhB5lrOsA5zajuszQtdXlflp0NkYpnUMBcv95WXN8hzo9o2Wn5xrgodKTPdMBqxg2dF8QYjma83uHhAQnx'
        b'dKV4QOz3lpTO2hklMJVRRByNt6YLhG7oxiQnbCKiiorQE6Qdl8odaOtiN0fHa0c+mZpRNP7HNjIhXh1LxEVLIoKLZX8lUtbbMF5MV7eDqutraiiw126Ijkzh60Hfhk5w'
        b'4JRJLq42nJSXvw9tg4MGslTzvswPQOcmWRT7LCcmNZnNNTbbObmuXmuP70zTbII11pVaw3lKw9i3klri4sjki0jmNha/ue+1Ra1OiIxlnaCz9RKTEyizPZUiEa2ms8lE'
        b'4MO+b2F2IYy0CSBWX0RiYlxsJItMpGY3m09dw/L7njvz+JoR0UlQSzdtG1vyXeVgQ7duG9vA0CAV7Qy6hdvYengG6JmHdl3yDCap7B4h+0EX5jVXt9T3IHl6UPhoN5NT'
        b'0afJOZJ78U1l0M6MyoXTNTblJsxjuhAzkfamGG4YK3ITyUqVqKEkaMe6nYy9YwpUcktzGmQt4KFVRzzhMBRjaye0S4EpNrJrSmJnHJyAWV0AYQ5h9q4QZqLCaZvR3EQd'
        b'K3QxUpmJChnTUn1paZlLMBvzNVQSlG8khCEZLIyzD/B1tFvi5eATqt9W5WgxFz37Qb5/LHuRCdtnY+MUnalK7dRCOJC6nFZVD2cpxkavulhNxLDO01NbJ2XPYlsdxoVK'
        b'LkxzscLGLdDBKl5LLK+rE7BBYwnTSKsGyEjdSvXNGCzxZXBAjj6B1BTmpRhgCWYZjxsMtcZa+xPOzsE9WEEunLaELDgTAiejFkOuxy44ChlwnnxVTSEmXAbs27gFiqDa'
        b'Y+0ayPNIjl28eMOa5HGr4MjG9RYCFs4cBhVwAgpZFy2CklV4HauVeCXRRCJIsF10xr2mDNAFrobjdUhfpbd1mDsYcudQuKqsbs3KwtNYRj/TcLBwc8y2EaB+cb9BeALq'
        b'mVcgwhzOQKG3crORJiINMqUMqgZz4aKJziugWqKB/UlMTQ3BokRTcywJ0Yi9i8MgbRv1FNDe0cKBaBFyYA/UKFglZphjjQ3QKGfMKNA+Sd0TnQlL8Vg39CH6YEi3LsUW'
        b'yDZd6IUVqZ7UtQH7NkM6ZPt2ZW/aD/WL2NghJfsyeBIyoEoN1D6QZ0lGeB6WBpEuyhPxZpLpQsickurPpgKNa9SWsz5CV5JXp5G6pFuBkKWEMqtxWD0AzsFZ6wFSAY74'
        b'9yMDBFoZFsyomXC5D0QlCZ7CMlLL5RmkczIwkwiXReVByVrBLwmzg0yC4MzIVMqJiIXybV3cM37eKh9Hp64UKzqQJk2TTLvOmOWQxeBljqdaQvFQKGbjCXPjJ2txJBZ7'
        b'PaDsqbIHl06LDvKxgvZlcJJNr1F4DvM4DY7TUu7ywTxnFrfDIkS84CqU2HvpCIDmenahAHLAk5RpMnb9+RKZ+iyxtj5btMJ/8Y2A9+dYfDB8+42O6b+lS80Ui42fnyEL'
        b'nDNgW4DHGOOV1+dPOmn19fiBZ/Z8NeLWd6o7ipw843+ItoFbM3NKEn4umP/Jke/XPePe7Fa27I2Mr2pto5bvuffWwr9ZbqwuHGJgNcDVvjD+izkTV8wanbFhRfL11/3H'
        b'Jp2asvk1g9Vff1Xh3/+Vm1Ne8vZ+M3Bh3M5PreK+ulxVcnTZ6UlfvvHzP65bFny8J/jtuutp1R03L8+Yfz+lzvru4QWTPuqX+/a2e1n/Vjgq6xsqx8VmH7/e8mPCrVL8'
        b'0fiV2VueuRW5paqg7v6Tx0a8clP+4RJv39XDp+79XnZ77JaqtZff+Fe/Hzbff/vn41Y70p4cfN5+f3viM1Vuxlvf6f/u1KvvLxxYFbhn1vSdlQUvhX7x8b2sHxelGe58'
        b'++tdedsGbFjy8bQ1q//1+r09G28HTpbfT78q/mF0b82HOxvaM1/caL/+txuHrhzb8eqvR8KefuIvMz4L9E++Nu5V6zcCZM4TxnhH27w17vim+kHr1r238x+j7Gqn3coM'
        b'GX4z7B33kheu/u3LH6Ylfn/3+C/uF+a/eeTDxEPZx99+0Xz3+eWffVM75N4u6aT8S66Vbipr7pGqWTJY4zmCRqzRIQ2MCGPBlEFwkCzsWpfUNQ9O0EF9UsNCmEsKi+Aw'
        b'7mOpTyOU1CU1eR53ObVhI1ZpJkAumSf7dXGYF7CQRwEWx9lYYktX+AU4JmIHC85bjGexEq6t6M3pIg3GGtzDWuc3h+45nIsjK5oTxzCABrKqMFeUK5zcrktV2oX7Ov1e'
        b'UBbBwiOD+kFDZ9TlsDXMH/eEI/c0VUntrcmE4cQiPJpzqsCTxZtILZUUgNcb88h2UC8T5HGS0XAwhUVjjp5MIzMpsMFwV8kasjwfgEtcLOnkhds6GUTyduoCJzF/MkuN'
        b'soEizO5GSKJxsuF5Z+5nw6u2zB+ZCEfCNfn2GzFbBXU84b6/yPO7LoyZB4emkBscKPedzEGE665wjTejAq5TT6aGc8Zol85FhxUaaIipZMrnUV+nNzRoXZ0GMayF/tOg'
        b'ztfPG3Kde6IiucBVOTakOeP5MObLM5xCNn46esjmAh2zAok+YTZfOhPTIYNXkmbK0tMcoJhzy5DB1m7Mmj9dTZlWnP3JenZWReqfKbHBWjygUjxyXrT5fydCL0uLIFlC'
        b'dcW+3IO7hVnGoomEpcBLTESaPG8hkUsVoqWFCY/8lNJkeMrkwdPiaVI7jfSUa9LbLaSDJIPIT/rPmqXLU14PK1FhYEYz2CQa96PEjKbXi4r7MomZhCe3yyXbRvfhfuuR'
        b'qx3wsPz2Tj9ackf3zLdHF3/XtPSOPnLT+0hLL6JOTgqk1qeTM124Y6vfzfkIr60/Boh6WJn3jweQCDFyXTSQ9HFQ+O+G97IsgqLjiVGrfpiLj/kTNDYMtWAj1DbL/P0e'
        b'YqhQWMURvQwVhwCmo8U64HFfmnE6C/ZpeTJ1uHYc0y5/qW2vDFSyADSYDsDjtoyEzXjRri7bvm7TX6aCDmzwYbqoT6gd0xw852gOixRwgWUgkxWELNvkUooTWXfxKGQ7'
        b'bSYffGj8+tg1BpOhFIpYCQMS8SotXzZxqSCOEKBoJNTwnI3zAyVdjvcq8SQ73jsymZlaP6mlwlNW1JMb7lcdt1jgCS71sVDP4CwFQewP1/CEADehPZLhUi7YRBZPBkFp'
        b'4yY4D0zksF+lo/CG0ihZOtpQELGW2GYDoJJfORiyxF5lR5FOoGXxVpEYD1fkTF+KJvueL91XAgwEuT2UWktMcK8JP8urwMN4Mxj3y+hRhhC5BQ6sgBPs0qoRcEMHOpdr'
        b'gfXEaIp0YiIIxBxXjW0TvJ1aN5fgsiZhBxp4ZgrLSoGmgTQxxZ6jx8XB0ZGalBYDsn9ehsYh4kx7DkmKrXOHKhnBJNla0gXRbjpc4sboRXtZ52FjFpQSK85rI6cLbIaL'
        b'kBEM+7EslOgDhUTXPUgB7RSBIim8ypCJ/WlZoVAwZZZEcAmPf8t4Gjd7fxkyRji5lJJnh699YtsQ/seGZV7C+4PGMHBIXOAi9KKP1s0/Wjmjj7YmM044KewQo4QoMUsy'
        b'WDilJZJeT3TML+lpAKXemRuV7BcbH12roZKWxZFfenJh04GxWq45lGAHtnMn4iUW58xPKI202jCWsLwKMWjSVLxGLKjcqWTMYNbmOQtikryTd8XDnuHCDjcLaPIdyt4L'
        b'ppNaKcDpovC49bOC+ctaBVkL71svo4b/qjfMRwls+ozAU9NZB03FMz2hCLf0Y92xYRN0aI3HEXie2Y+H57AuDIPmgeRSkilRjnYEWInTMcOK1RU/iLzXsCGMIVQ91F5Q'
        b'Sfh47cBT8zSjSBhGR1EZ1vEcrcvz+2mMxbR+NIGpOVhz1ptP7mkmzxiSsXB04nhx5gSoV4k8XvGok4s6gCiEFCpWkChFm1Q49x/1IWWkT75F132g354ShV4M5rTXGnS9'
        b'xibU8a1Bys14xVwiSKEGm4zEKQuwmI/xRgnuV1IzhcwlE2Kg78QONmsWE6OsEJtN8IohMc6LyXQrJbes8uNPlcIxPKekty3EZmExXMZqNp3cF69S2trZY5OfSBaOU4LC'
        b'R7ICb3LgQ7IsniG1Nzv7YKufKBhA2w7YK+IhKDSNDayxk6oXkPneKE6PDvU9YBVq1dF64veaL+MHrf8ionxPxDD5Dvc7Fkk79udN+8p2ymi3mi3DW7yq8za4uX52SDmk'
        b'xculdlBkwajqDQsLlAMvLBvyScaHHznbOCwbar3r85DU6ab576W+/PPO1Jcb1K9cO74s9/XSv73leSoqcE1J7icvvLhogVPk4tvjv5l1ISn+1qTLJoXNCXbTsxtMA5+q'
        b'TlasHOg6+u6Sk5cHVOyN3tt8cOj03JCDJwr+9pSQV7E089Brr3gXPx365iq71jEna77wWbV644TR58ND1cXuC+JW+VcYFN+2T/v70QvRLaueSv32i7sR/aYP/HpOe8Xo'
        b'LbffHOGydGlzv6fWh09MfSnhH5ZvjQ/95POYqBH+0SHB/wrZd+JOcu3ZCUGD/fb87fSClBuO8ndGha8Mnbe94N3ab5w2zPVLK+6wzHtv0WXffy198krtZ1tLNxVvWncz'
        b'9YM5Hc6hyl8v3w55xtvX8epHaeunL4u8H/naxTqj3xM2qJ3Uf/nFdmOCR+veyxvKyt1+dLR95lfVpePRZ5L+rlZ+kFk9/MM3YzbMd/yltOb5C3Gttz3y3lA8O+nuR7WW'
        b'2y0ibu9OVwf+5l7b755pivPowbeWPxPzruW7HRDssen3218sOu6lzn3t97jcb27B3uobc9WmL857cYZJzMpbwvYzz3nbHUjZvdN+ydnbF6Ydtn9xxvX0H1/+9v30f7vW'
        b'P9tk5uI+uSa33/viXdmre5/08l63ddkLbxSMDx9+a9ulLQv31w73jA9Bk0D3bVbTKibu+vzUjronfdZEPXv3jyGp775+2TD0jZV3fj26utLN4Gb6kZEVdYNXn835W8IT'
        b'722YcHr1mNSfSo+Gt302e68i9ac/ci6c+nz/wd2fLFj75b77cYF13oVJpe3uC94vWLnRdNzfx/86Y4LjTDh+f9hbPy5zTl/+UV6H4utxUVd9254aUX/S9NPobRkzAybd'
        b'OfrivRrXGz85fFbu+NMvJ1sbPvppUcLK19y2vWccuDjBPPXOhdT24Q2lpn8oW9q++UfSU7983BEwcbGr/dXFdyZP+fzGkLz7PqPvLW365O17nn/MrKnucL/61ZJfzCtv'
        b'PB081fzfqR+Z3t//htl6sw/OdIyvDKz92Pnjsm/T7f5l/bP8u/LvrKqfKjR79chA44prw4PMh3392z9mfeBU5fha2Q9q+Wvxh4PXGh4efGxcfvWZH/ZVP2V2wf16pcPR'
        b'Ehh61HL6L6XVmUe2V595bnlA7vD3/656d14wvPiMauprlZYxnz0/a9xvUV/98NLPL3+0MeDQ+27lVXM+PNvf5ua974KvH5n22s+NH+DpNVtGfm3yoffr9+L73x9cY/TB'
        b'gfQLNUeSJa98NX75dYPP7O6Zp+Tfe8PonweKdj534sWkMb5+f8n6euAfT/r/UZx86zjeHbT65BbDyrExF2vEv70d0Nb45YnNvtv/1TE0zqzl2Jnbt36z2vml/Ovbd35Z'
        b'/sa+HyKiF9bc+CJh8rQzMcGTZ5z+97/WDT/+1QLf+j9MXnRbWfn6S3u3RIzM9gxL+Ovkf5vcPft60eimiX/0P/vqwRdfedpo8erfzS2vzi9vsVdtZKBwcEI078nZQnSg'
        b'ZRrOlmi8znlAT7gv0RmwkS48oISuVBwKjix/N3R2ntbK87RYI0UebTF8K3b4ks1P5QQVfpo7zF2k66ZiDSsgBg+s05qreBNKOxP9XHczWDc1dkzsw1qFw5s0USET4DIr'
        b'KSQSbtAbu7N4rsQC0yfW8EzFQ2aTOgERvRIYJOIRF46IeHzcDDWHelPM5dlJpnhTOodolRUptuSGIRRaUe1EKTSSA1R0a29mcTiYKxWewGqilZ2XBxP7nXkeYjAfTvtq'
        b'6ZrlZDsoDZPYLV3AMymP416Zr5+dnBjQgmS1OBmqZjBjdfAEX9IXzkR9Js/sWgoHJOPG4HnWdP812KRFjlsLtQw8bmv/+UzCm0dgiRJzHLEJC3wpv3GxYIiXJYGj4DRH'
        b'0Lw0lKglmhuIupfri81khzGFHAm2Q/o0bswXzZqkxa2F9v6TRKjFmxq8PqO4zfxxR29RAmTbMpYsxYuRHGvxFFSsUdt5Y2EidQQvxlY8EGAoWECjNAWvbeZhTWeI2u6r'
        b'YQs1gLOr8YZEiqVYxku4SOzwkxSk81IgHMLjSqi1lQtG2CqBsyMxl3tDWo2WqinAJLa4G5EuMhCMsVCC+T7TWOclQ8Fo2kIjFbThQWykciDv1y7tP8ade4Iu7Vim87Lc'
        b'xH3M0wInljBfhRP5y2nam/ZOKmMi4st21J1hOUiK6TNhP3++qX+C0skXr6gwX4T6bYLCTLISSsN40ugVyINMNU0CIVqCM6RDTbALl/xxOB+DzeS9qejtnWDvIPIOBkI/'
        b'aykcwQuOGnZQKII83wAHrCO7PeVC1RChDoUMGVRD1izuR9ubCHlqJ2+4aIKZ9CZBMJNLZ2PBRuaI2omXHJQ+jnPD/JKgwYuMUrVKFAaHyBZiPZxLoVwUI42hlP5RwA5h'
        b'xyC4NtORjZ6ICXDCl+FjwzFvBlZpBmXSGXAemniwVR6mQxFDe5w0tCvWI3mDNp6Jm0+U/Ea1t52KKFALoQbKRNg/CbP4YL/pC5eIcPMNBFEpbF0D7ZsjWZ/ZkYcKmPtu'
        b'NFQ7d/He1UMVmw2WWDdYBwQZNppCQe7GBi6LHNLLOXx+Wa231zmmPOewy6ugJVZpS2SwFmuT/EirjPGoBNqWQRkbzivx8ET6Pv6OIl4xFoxcJVD+BBlo9JoPnExWOqns'
        b'SH/lG0CLoaCIlcR67OQ5ySXQhNX2pHOcvLHNh0Mxm8N+6VqoX8WHSZFdNKk4iQwFAyw2hnMiMSkboZ3H0B3Gs6FKFR7g0jAgo7AQy0VsGefJET+b47FW50wbNJS60wy3'
        b'sREWlTKJjH76ltI1FpgrQtUOyGftHZHk5uvnrZoAe3wcneSC0keC56CW007jYTgIJbRfkrdDtl+AE5nzzlJFKh7lSwpekrOFQMCrApkNV+ECnsI6ds3UDKrIAp9M4+Mk'
        b'plgEHeJQM7zC09/LoZGa9hqnKlRTxg3KZ11BVkqqqA8basS0+tWuTKeHBixk7fGYMoI5gqEJ8rpAzo7CVg2gLRloLbS55IY9yX7OomA8RwK1g4ewaWIxyEtNkVj5RCUD'
        b'kTbdiqy+RJMuwsPL4RpbTRa7QaEaC1XrDY3hggNeoY6JS+TOwRYystX58bU+C+pIo5u11wwwY/kSEfPgKjaxN/BzgwbmXYUMKYUNdp6crPFlY62KntpsxmbSR0QSl/qJ'
        b'azAbjvKFYN9oA3pVjmf7CyKcEPCA/Uw2MBbOomeszphrS22MDks8QS5j+TBW6hKyZh4ibbb1SbOTYCZcEQyhVDIVTm9hw24eWZ720PjXQOpXKY8juxcdIeYSadQaCy65'
        b'ajmxucmSIMNjfOmgOOZk6djLwirxJLTDGXWACs9gLdm4yAKrWSIHwXmZK7RCJismImUhX+aZSKopmDsZv1CmCZtMcnbksl8DV1VMbsbYIoGOeGzhsAU3RlGqZoqmOnun'
        b'IFkiOkLNQNYnkhlL1KTDjTA3jfxg5ffHUikcnQuVCZjHn06HsmUabPT+E8lkrxoC1VyqF8YlMz8tddKqLWZKbOD8PA0kwdIAZaqpEZHpUr9R4lwyw87xqXQI8jeoscBR'
        b'TCXqhsRKHEN6jisJZL+qTOTv4e0VkkTvIRt9rXTcOihim5XpqpGdoPE7LThs/ME0srGr6OOVmEEkQnF0nTHP30Hl7U+WbA0685SteGyGHE5jK1xhIovH0xM13mk8ihk+'
        b'Wvf0VGhkEMiLY/EyQ1nuG7kdWpP58heKFxTOxFbnrvUMzB6kZHc6JpHq8+m624/MVDJlC7nf3hHaRmk4vkeHO+sovn0DmXSiBsFNMhpU8XF8knlKoG6nlGtIFWRY0qFC'
        b'l3KsdoVDIhTGGPFl/vQGvEQvJUNlIF9NJkqNproxjz1Wh9ClsQ/g+fGQHo/FBjFwaDSTyXjTCdrGB+xKUrG2X5HCmenYyPfMcwFbewLeG+FphnlvBFn9+d4wA/cp2R4o'
        b'RaJOtIpQY0iWJzqKqb9qjxLzNOrQ1JWCQpAshjbNrjIK964kC7yPKEhdyWy5TOfh4XkcDK+Y6E4H6Rsa+/jTIUJmiBVkSnfYYA5Uy1I4UD9RFWqVZCiIQ4QJHpg1mCyT'
        b'tNqEObHqAGxyNra1SwljS7XFBinkzYEsJjw/rFiMzQ5OTlSuN4hmdYRsZyJks53ZYDacV5KR745NgkQljjBbyNojjdim9vMmc7eISMtI90bCICySTQsex9pjge0jlI7s'
        b'feSRcHWEpP+sYL7GlcCZWEarE+BoJ67F/WQgk9l6CGuhnitl10OgVu1sh41eKglZyTLIqtMu8Rq8jYkpZCpcwWbHAO6LGB29U8SDGzlwugLKKCphL/TkUGiwXAV8LYdC'
        b'yPFSO/mkjkxQkWlP1DWJhEybm3iSLyXu0zXas/caOGxuS9czU7wmnbp2Kn+8yYNy3OsitKF0qr+4gPROE5/3R+H4eF8nf3kMHBYkW8UZWD6UCTLCxJHGbYuyYB62fX44'
        b'G9XjlgVpcU2wJJgIguKarI9T9fvvwOXKH3Kdw1XwJFt5MvPes+OeJdTz1fdxz27BTsGwijn2sbFoyUA6KFSHFYMcpMc1ChYprtDgH9PP1uSqlWQIpXO/L5Fai0PuSxRD'
        b'RJsfJeYWosV9mcT4D4mM4iWbiWMlY8Uh5NOwu5I/JKYU4diEPGF5TyKnn8dK5PdtRbPfJeR5C3GEaPGH5AX5dGOGqMwQkilOsmghDvpdIh9GftLaZOIw8n3QrxIjS1IX'
        b'/Z381XQQaQsFJ7G9T8oyeEDd5Oowci8tlyMuK0gZVqQ9ClKi2b/lSsVPkqdNfLVQJpyk3oZ8H09rFgf9IaGt/V3ym9xKIW4b3MfZDZd8F1Lah3Vcl+TlZ0hXDZOTPqME'
        b'mnrOktKFz6z1nybpbxFpBsuivyLS3OSAAJWMfGNB5rUmPbBNkjcILFE7eJ6Xp79nMEMzYYnVHNwkVodIQtubTFnP+Lmc1f8K5sh0nbiK6cimR2+ZdP2QyOQa2Ox7MsP/'
        b'wU8vyidLRDNzBTuvJIK+bzVTi0xCB53kD5mU/nXEbsE4lSLADJuNdRpvPRTM6+awlwgzVsiJ5XMCTvdKvzfW/FQbPxibRBql0Hw26vLZmHxWRpmwz6bks5nm7+ZdPmtw'
        b'SiqMdBgkVlEDumCQSLtgkFjvN4war8MgGRo1TIdBQnFLhKiRUTaPgUEyar88aoIOgcQ0xiBqdNSYPrFHKNpJd+wR29vmDJqH8XXPj14bm3LXuRfwSJer/wHqyBSevu6m'
        b'ktyWzQsM8rwt9XDzSD5MB/kR+u2Y+OjwH1N4/qXbY2GGaB6a8vi4INrqWLqnK8UFST7Ds3MogkfyWYY+FOTpHxjiyfBAxvbA4giePz8oOql7krlL8jn6wo9yq6sONEPb'
        b'kLuD9JWqQ9Lo3maVUbcyaD8kv9EVjkMrnOS36Bu9SS/pq8M1uZne898F0XhEpl2DAHYaNH/1EmwYQfH/tNh/lFycZ3tCNlQqNyeJwjI4zNDMKpY+EdveulZUjyKXX6h6'
        b'4uvw59Z6RbwYY/d33wjjmC+EOxmDp6wUpubajZC9+rGtSuSKdJYfnsXLW7qF/cAeKz2Eope14SDUCtarH9AvG7pXbhvUY549IhaHpaFGynq3M/r1wwMwOfRX3EL790UK'
        b'uEEduv9rgBsUa3iU/FEBN6JYyymiAI3v/59E29BOk4egbWin2UPvmPLIaBvdZ64+tA19C8AD4C/6nMx93/8YaBc9M7l40kFEPM0XoAlZetKLdI/1BbjaCyGjWz9rUDHo'
        b'JsKRLshGYqc/E+hhcBTaljwOIEVszP9hUfy/g0WhnXF9QDHQ/x4FEaL7pH1ERIg+J/D/4UH8CTwI+l/v5ByDgJBUyi+DZYtDu4AR4DGs6QJIgCW430/D+qsNnxdprE+2'
        b'Es/G4NHYLz87LFXTUCG3MQaU0/yLj9bHrHjynVtv3Hr31lvXw269f+uvtz64db3oePGorKa9Y07U7lXlX3vnZOa4rNojTbmuWaPK97hLhT1tphO/kasMeBDxzU3TaBgt'
        b'j6EdCPUSFzwxh/nSwiAfr/TEDIDLHhQ2wHWm5gBWPR+ruybmQwEe4wewu6TcAbtn8HDmVqFOlTTKdH1eSx/RAgfiujA1QIuDLvx5PzZog0D/k2BYXa687cO0nwXanHl5'
        b'X6rI4yfED3okheirByTG623FI2XFZ6rEgOSrolZR6yMj3sNQE8bUuyZdOvxoPVterxR4+YPDdCMNe0wPpXaKUIqXbMMeSpuSqm0xSo3SZsiUNgVR2gyZ0qZgiprhLkVw'
        b'l89dEtt39qW0PTixvath+f9EVnt35C+NJqRJ9d5E9g6ac/t/ie7/l+hu83+J7v+X6P7wRHcHvfpSHNkJurKkPVbe+wOWjP/NvPf/ara2tE+F0DKAU0mcxxosWoXXOqnS'
        b'JGaUspSjgFFX/Zyd23m0RLAX5gY6LtHkwPrgfkZPtpQiaCngAu5lwfRQAvlGcH2bLw+Y3ysz7woTNoroXp1J2DfceQDz4eETWfI3ZmCDBmesyCqVnhUMo2nAuvNsBuJl'
        b'DBV94HhJ6NFmpRG2E8WthJHUY5PZqM78UszxcuAZHZijIXY1wOPBQtgExVys2pBKuR7XRGO6bw9dmObJOmChPxZt4/FfQUpD0pjE1Nm0iiysxAYdU2zooqWO1vZLltKc'
        b'Xx9/P6gN8YIGL38nR29/Uo6zBC4p3SA/KFgYARVmcUPnsJc3gz3YoqbuW2gZwyg5sBYyU+nBDJzEs5jerfglS2kSa6JbMs1bPUAU+RonevgYDvmGcBDaoSOVKlaYK8eM'
        b'YO3dmv4K4U9pX15YGYPNQw3hrDce5dHsJ0xxnzLZDNpDiTSl/cSZtljDgsUHudJgwdY0aMRyNc0zuSnawxENmd3IJTKKB7A+yyfcb1m/UCF2TNsEifpVciV08YDQAzPN'
        b'wMUk69szX85OifzUqmJvltJlmYexZd1focwpxdV+wvrvb3lPG7Pg5fQxdqOsf3v6w+2BxueGuf5Ut9w15/mGL1a+M8XWI6jqq/R/nVy4ftKm+deftQ/69GNJ/AvFBm4L'
        b'v73i8fc5y1a+furZGOfDY1fNuP3Ory5n3Zuaru48FnQ3et74G2lb1/39uaUuE4wz3K+rbH8uWuV97dMRf7ff1fG6ZMa0H2KOXksu/eHOxXUfn7hcE3b5G6tjd/3ffOmy'
        b'74KXt08Mqf/HzcHPVjT+c4Pf5qLhs7Lf9Un77T2VNloFz07pgiXmZ8jCgCDDl4W7LMJMKNQkhLpBlW9nQmgi5vLojptYh5ksIxTOQTHNCU3FS/zUux3yt/KEzfnmAV3y'
        b'Na9jOSt9Fh5NoAaLNWT3wCmT4B7mnU2CgqV8yMzm/cy4ixPSWGDQDEto46ZQMl6gR8y7xrF3ssBqNzZX8NSOLrFs00mtNALHYh4WayJtJ8K1zmBbTaQtBUZjrfObY8Ub'
        b'T2dsrp9oiacFM2yT+sFFqGfvvoq8SwPlTo500bAnn4cya2amzcZa0mg3H4kwUybiRQFbodWHvdJoKLSkzubNmNvpbz4CN5nI4lPxnL2PP++P1XCatL3/BCkeg2oNVZ8l'
        b'HpyL5YmdJqbEZfgiFhKLdaQt+3z9cB/e1Jes6ayAo73Z7JT/g1mSfg8zDBNZrqRUwUh+FXI5PUwWrTQkwfTYmn6ZScwkCpb3uG1kT2Oq7+RGo0dJbuzMazTQHxBgqJ9f'
        b't48cRs9Hsktv2Oi3Sx/2gv8LaYyrH5rG2JdB96dyGOlZR+8cxjEBqXPJ58QwbPDVMHz3lcBYj0cfkMQIbRsY9+jk6XCtM4sRGoW182ZKlcJorJfi+YGYORYPsL3KPmCo'
        b'GvPgCsNB4LmMcGkpp3O6nCRiKQ1TcneR8SRFOA7FbIu4NU3KqMJOTt3p8NFGc4E/cHzXMpqGiLluNBORpSFagCYbq3o8VGDpZg+aiSg44wnYyxKTRCPcq94EF5Jo0Gch'
        b'Tf27lKTBB4XzcnuV3U68RqNtWSZi4VKeH5iJN+AGy0XE+vk0HdFaYjIIqtiep7RVBSdjuTYXEQ6QhUrDA9YGxTNoLuIyzGHpiDQXEa9H87Y3QzbWE72G7M+HaQKhINrh'
        b'6aGpdA2MGAnFwcuZHkJzBLvkB8ZgGxNHRFShMEwUBtmsSwzYlzySZ8d5rh4tzCc/iwLSRkeaL+V/PB3nJRQJgsvJuFi7VCHhP8sPfMTcsutap0zqQvJtqh3kaJhPHMgi'
        b'mzQSK7z9Mc8BizURSVgCzRQLhQYAquCK1I1oOL5Qgs1qJRHZPMwxD4EGF/Y2P8wyFYhobYUhux1e857FXzHWyVogupdFuGfCMO+NXhxNA8rheDxLC2Q5gbBnfpe0QGxd'
        b'z/p8LNESC2n2H5yFcpoBaCVO37yUFeq1lVLPCRaJy1Ic3g8YIKhEntdWa7JFvQELaHAvC+3FSq//SKQxjyZSqUIrUnZ8up+M23SasIfXvGnOnpE4hXIusSZCwcYByh2Q'
        b'rUnZI7vcdT5dyB67Fzuwee1wmrOnyddbPpll7Xq4blAug8Pk02Jh8RTM4KnBrXiVjFGHRZqEPZ6sdwhOsmw9yICro3myHpTNYvl6NFmPtK0mNvbHd2Tqg6QBy27npYb4'
        b'qgd4Wn333ZdHfjua+YPXc6YWc9bk5fQr/uXQwqI02T+zxn5U5Tnsh5ej1zZ99e6WqsIlyyf6DrSa+ONCh6VlvgMPKZdeWP6L1CHv79PP/RaUeyhf/fmOz6d/vrlyVlja'
        b'qfz1Noef6bBcYPbp25dyLJerqjYcUX5v+MPZg1+OembPa08+n7l1kdfe26sGGheMeO77rIPvvgRvZlUv9u2/2cDNY+hnixNOW4TKNr5x+rNBTVtD5qtPv5F//1PT92qO'
        b'tjx3bFLjS8uLDZ90/OjQm1cM6jeFtCz+cM/TV4oL3rD8oCb2TprpkuEv7Jrc8MfI6tWRN5u8vh/T8VZKnNrjl+ek89868s4VW8numXHSuPc/+lClnuLRNuzZ3Zt+2mJp'
        b'n7o6VfV6aXj1L/Z1/rPUeW4bTS8PvrayLtb9q42tcGVU5PY78x1/basKUUV/d/mnhLQpV/JnLv5283OK5s+Gvnl2ePDLzsP+hidqTqQopkbaJ/8h+9HKffut+lSTtYFt'
        b'E1XKtqW1dwNWlcYcX37z/aiYD4dVB2e3eHzn3vh747ojR06ZXV13MOinqfPNbRYceQXNViyvixM/UDbOu/BMnMsn8d8Oibs/ofDl0d8bfhMUbX3E+Xr5557/+qvFzwv2'
        b'rKmeWW40KzAt42L5/ns73/z+u5YI67dvvPz+0EaM39Vyp8XV6q0rpra+jh+8ND3r/+PtO+CiuLb/Z2aXpSxNQMSGiIIsS1OsYMFCBJaigg1FOojSF7AXEJEuUgSxIEWp'
        b'goKKNMk7N72YvPSYnpjeY6op/m+ZRbDkJXnv/wufIHfmzu3ltO85l0/eeMKj+snxLfozPDcv/jBl4QvjZ1kf1u0atzz++KwMswz92dofze34zrbfNPr5RU/8GvjJIq8x'
        b'6wy+T/cJPqcTZDNtZbr9vGcHtX1/Wu426Hq+67w699q0JJuPf7ntvP37H/V+3zjV5tUr+959+19ui6b86BSX7xKQuyXm6bBP55yq8G/819XHb6YUXos4sef8991nrk56'
        b'QTrhgO4nf5j5heXejhW+/vWHj7zRb29lpu/9Ydwrny6f8IanZdxrtavx3zOW/1SyfFzG5oqc9J2VM595ZnDmF698j58veOUbs7iqYxXj/ghrCo+J2Wj0RegSm/Tb732Q'
        b'6LTjq9SxZ9M+jsv5IHvPOwWznVCb9td6X9gX3vq16p18v43jP0h4s1Ct/+KOZYumb/jt959feqytZJTLq5lFNgktM754R3brGbczGVsUtdc27HvrlvnX12eZZv06IWPi'
        b'rV+ytpWY/evhk/xAeOa+C5/88MLbg9/W/BQti53jHauddvOyXf33F91NodW1F3w/mL1s/RvxjvV74y8bfGyUsPx1/2t/mDzz9nsh9dvd5hSi+nbJZwmnf/4qXG+V2fbX'
        b'tT95Nmd1h/kYz62/jJo069MvZ3yjSEojxhppG6fLE/i70W8iQQ65IGLfKlM8lMsg+67g12c4Sq5vmhI/DPl2mnhOEn2clEI+826DOtFlFXToUQDcMPQb9G+lxtxR6KjF'
        b'cMzaPjTAYGsGkIsZEoob6cEcUy3DraFy1EawawS5lojZIfJeAlXe6hlw9Q4VI0LX7ARKpadOCRZhawofpxTv2dBH0C0a6Jo7ZMvwDXQJqqip7DJ8mR9kwJqlswl0LVSw'
        b'j4Qe+m7e/N0Unga5aRShRvBpqNaHDVRRJFxRpaOLIkaNAdRc4CBt4k64OkYOOah9CKXGEGqoTkH1SIvdUJl8/p3Xw/Fp+HZkAIGcIDhKEGruSsL5EICaDYOXeUMRnJNj'
        b'Fq9HA1KjCDWfyXQKlgaNugNP02DTUIuLJG2DH/3cEp2H4wSdRpBzFKFG4GmQG0ObLkj1GTRNDs3QrDeETLOAcsr5TVhIUIEKlK/rNA1a7yDTdKczzFAROuUnR4MmFJ02'
        b'HJmWAucZy3oADuN7BsrglAZgRtFlqAtaqLVzNDq9Xs1BpogvgyYtqKajFrRu3jBsmQgsQ/2TJCQqLGpniKQKlE0NjXZa3WH9ytEhESCEGjAJ4O+oD1dQrYJg8+p51I5J'
        b'UKbdq0FXoQ0V7IIBEXxyB3kSgy7RPMtTULfK34HC1uCywUjk2lEf5m+7AB1A+Wpon0rRa0PQtR2YaZ9Mb1pjCzk6yvs4+qYQ8hvlKRh8zVIqhQuz4Sxt7DKOLMwzPIWq'
        b'3cGpmUIRncWFkcuVwfoEpTYco7YM7ads827c1aNqf0UiKiDIBgprMA+hw2uqC5moK3CFiFCDfihez5qdj/LgskYCthB1a7j6WAavmox68UIiADXUiIoJ2UwgaviH2biv'
        b'wrzxYRECqti7RQNRg1qURRvsZgFdFKSW4jt50xBGDTo30L3mAJ1OygTUwmBqDKMWh7LpnHrMQ5lybyjQwNQoRg0uRzK4XiX+aVI64sVMcWrDQGoNenQsbDy3EozafOgi'
        b'MDWKUbOGbnbUlLhBI4Oo4ROEodQIQg2VR9JWGS+CbIJQ85QMOXzCtFgHC4MJg5Z4IyxSUZgaBamlraTtHY8ORKuoC7lUVKoBqaHTHrQ1XnBYR61nTWAlQ5iS9TNobbYo'
        b'Fy7gbTCAMkWUGrTzwHB6qDpgMwWoNS+mGDUCUEOXNtJ3bnOhighclyqGBV89r2LQgRM+Hmpc6sEhGnb8eNp1JaaZj6sWwdWRTu7jUeY2Wmh6CDpNwS++KQka0AwB2BL2'
        b'DzqhxPQucBpqSBDxaahSgCt0octQAXQTcBqDpo3Fh8MwdJq/6LIqxX6aCE2TGhDCkiDTRjNNfDJmCetVcHAZ9fxFgGmOcIiNxyXU6E6RaQlETIwnZxS/aWssszcshorN'
        b'akztZxJsmghMC4XDbJWfwSuyi2LT8OlXQvBpFJz2EBQyYVtziqV65SwRncaQaZEbGG7WbwIFy+ANMhqaiGT0Em6vBTovVaJSHWab0I66FsjNfIbT0Cn2DGpUDfWQpVLC'
        b'WY1pwXTMsw7QRu2JNJATYRop0g3ffngh6kGpAG3uzqxH1daoUW5nr9iN6XC83DBLao1KUIUIlIU+vOcYhMgMCkU43A50jtpEJG+wVaNWdJBehva6Q1i4ie5SOAIVK9l1'
        b'locG14iQ6dJNlLwnWLjkeNq8yXPgmIgXRp2O6iEkXBCcpItMNxRaoWAS5nEJNoYg4az0GeJ+EK5EjYDCTYIWDRquBjVjqoGwThY2ZipHH110mVx0BAon2UwHPBZaaNRq'
        b'zI9T/Now9JoNaqG3CT/VWIXn8cAQgk3Er8ERfOwQ40v9rQn3Q68t207wawS8xqNjbGGUbYci9dAoERlnVgKckKSZT6cF2QH1gEIIG12Ur0DlUOQt3u1jIVO6HFWjk3Q+'
        b'DDE1dBR1TcHXO85Ll4E2OiEslixil1Cz1Wp8Q5TbBtwxmCFgNcdgdp7VueODWBTh41VeopHI4lV9ju0XdNmOSERnwqBGJGqOLzh6t7ZrwX41rjMAL6fDSnzKGu/QhmOS'
        b'3dPhEl2E0xPhrFLYRGI9HFYROQM6JuwKmM1w6ZehPVRNXIvmESqRdI3nRo1Gl4Mke6B8UxpxIwYN+I648icQPjy223HrRQgfXt50ImX4i64hFJyIgYtfKsHFdaEOtgLb'
        b'oNySYnd9IXelBgs7SfQvoMLcaS1+izol9D4jiGuUAyVsZ1W5LVN7QD79WIP61TanswZVCdD1IJyeFjrpETNRSsfdFi7PGQIZighDmbME79lyfOSQTqzw2aWc530XUo/B'
        b'9FzQQTo1ylVQJceEQb0uReoRmB5c3MGumkKos8E0YfAdXBvF6VXCfrbF81EmapI7KTLSCVaPAvXwIdNLq07Ce7ZgGFDPaaUI1cM3RqUThYItnBgkh2NTGVAPHYRcXQae'
        b'rPJG5zVAPRGmBwV7JZAPA6KIHR0zCiBQPejeTdF6BKmnSKAbUwd6ULsc2pYSmCpB6k3YTM+U+dxMNb7gKEoP9UeOAOqhCkwqkXJD1sBxAtXD51opgetZCqbotCkdjCWG'
        b'mE4r2IV3CIPrabB6x2CALgY/NBCmRifhuAjXY1C9SSIGPDo1lEH1UJ8FOaoIVg/K57EdUO0WNhyrN9NLROuZhMkZMeE4neD08B4+YzsE1HOCfroINs4ntJETiFi9YUC9'
        b'WZhioPTlybk6IlCvbS3F6vnxD+0VgeAJqB+dUEGTn5OfjOL07KVs7lsxldSmhFqnO9HGCSRPQCUKw/97EB5FR1FVwoo/Q+Cxn7EaHJ6x5MEIPJ0hBJ4J/ZHyhrwxTlv9'
        b'JsiM+b+JuNPWERFwUopy07mN89+mP6/JZt+DwftDkDK8nRn9wpAoOihuz4I356W4VCfekHwv+y+xdy/pzx+JvbN4EPbO/G5tw38LvMslChACZvtTBch+7tafwO8e0Cjc'
        b'EgJTSL2uwd5JCPbucV4USSpM/+8wc0/iSt8jEMN47n+EmXtNphR4Q61h+Lhpw/Bx4jOLxekEzw15+Do5o5Fco/pwIrymkmse3/yDWgmwH1XeYzZrKP6rzroHGhcsLdcu'
        b'1y03jRHI73JD8W8z8V899m+cJEYSJSkSouyHtEwkcI7+IYNDhoeMaThsfQKxo5A0rWhZlCxKO5sjYcCLhGBtnNajaTlN6+C0Pk0b0LQuThvStBFN6+G0MU2Pomk5TpvQ'
        b'tClN6+O0GU2PpmkDnDan6TE0bYjTFjQ9lqaNcHocTY+naWOcnkDTE2l6FE5b0vQkmjbBaSuankzTpjhtTdNTaNrskFYMLwLtRtO/SVhxnWBzamcpoRo4nUNyPDZGeGxG'
        b'0bGxi1LgHGOiBKqwUF7XX7rYL2iZqD5777Jwl10lMWwanoNh8obMctKSSMQINcsza4YD+9eVxlcgf80cUZhGS6d2slo8zGJQNICjUALRzA6/TYtOpeEfkjJIbNu0kRZ/'
        b'w0NBOFhFh0dutkqNTk6NVkcnDitimEkisWkdUcKDbH5G6gpHJPyTiKmXd4wVDeqqttoWnRptpU6PSIijxktxicMQGtSaCr8Ox/+nbU6NHll5QnTa5qQoarSO25wUnxFN'
        b'tZrp5ISJ30GsskbEurDyjKMGTnaLFaKlbvxIsy9iHSUaDrKJcBbnQTPiDlZ2SxSabOFW6mhiwJYW/WeTRObQbqmCwDrChxkJiuZ5SalxsXGJ4fEEXyCik/EQEOzEXR1V'
        b'q8NjKbIkmsX0wLlY762iopPxkaq2SmINp5Z+duK7JWSFJSSpRxp8RSYlJBCLZLr27rIq9FcI1yXbE+KvyyLDE9JmzYyUDDt2tMSjh6qdVuFfIm5M+5Am8pacHiE8PkSE'
        b'GENRZS3JlR3g9kh3muyWUJW1lKqpJXulgcP+HmaUfIv/C0iyEZvpwfZlDzI5xD1k1obr/HxFczkaZIWWe2fu8CxRk1K8Ne9vh2oXzZbUg/btnyCc6PC6EaBKZDje+WG4'
        b'SWHM7I8VNlTI8OX3gNA34VFRccxIVKx3xPIjCzUlPVrcwup0vLeGjpD7IztGmNKyiDZkB4anpyUlhKfFRdIFmxCdGjssXs0DMCKpeGcmJyVGkRFm+/rP48+MuOsMxEU3'
        b'0qRgor+aEM1nPop91rfr3z8pFS1piicVlwsUr3Rmqrm4PTpnFtoyNSYx6EC1qIH4L4ZaTF4fQd3Ei1UaZiEUcBkKFOgodAL7Cs7gP+souRrEdJztmHkrCTaBVtyGvdxe'
        b'VIXOUbWtvROzE3CZfXXeFl9/Lp24b46PhEFvV+jCR787574VnYn/+fbt25ZW1OrMymXNzIm+4WYcVXnqoJKd1A0zKnd1ETgbS615/Ao0CCcVAvW3PB4VoMZJMWqUb4jy'
        b'tjGdAmYwde3teG4GKpcpMadB7Q+gPghy5PaB0/ELwY+fg3oNcBFW+I01OojKWQGbRrMi9MgvnrN207KWGaUzjr4QdcjZYwnqnb+bh+YplrgE4oFHFjtvRAO8fbTsMQ+N'
        b'Lii9VU5Eo7EGVelMkEIeVRaPXxmGupTj8RCwlzqzhERUCT0KCXO6WoeOrUcXI0hkD0d0xNVllsDp7xG2wkFTaowAHfGoGhXBhTsZZJz+XiEe86ml6YTBsnaDg3AeCu9k'
        b'4Dn9fUICnrNj6UqcITQWmmnwERIHZKVXkBfJuNJruLZmmZH2GLQfWtOJkFALLqI2tS+mr/oIR7nSEV2mzKQpFEugJgz6071Iw3KgAE4Ot1zRRF1Beb4qlaOQsgBOTkAD'
        b'kD8adaJOTzinMoN8lVyPuGjyWRXIRccYz4HBOOZGWUeLLYaHOiI8A1259A2khktzUd3wChZ53omnU+Tss9oO5XmhwkBiR6lajc4PrV9qLxngrWVio4f57jNaWqjH0waa'
        b'FZznNjN0Es//CTz4ZJq3hxGFvFFyKl4k6MpsyOJtUc08Zo8ysBma5DqpGXgBSGfAIG+P2uAcsx1pQq2oCHXpp9Dv2iDXnZ+63oWuO1t3R3UylexK9INm8WGoJ4B5pK5F'
        b'ebbqFNSpTz7Z77WFnyqBftGpsQdcRjVqdJmWB/1Wk3nzcG/6mSVqJvI2TU3rM/ipHOpiC6cS+lDuBqu7p90Bz6I7W1iHUc3wwDN+jj6oHBoDVnsNfSLOGZ7qLg7VxMuh'
        b'Cdqgja6aRSamd308fUnA6hWOa9gnHCrlotAVHS4cHYizfuR5LXUm3t/Tc8sTytzVptONH7c5ufvqzZPOeWVzU3Te89uek32oLKxsxY3xz+d4d32gP6Ps2wKzwpeSi2ag'
        b'qPa6um9+0J+0v7budF1DhJ2ieYbvljXfPTr9MHz3Vejtt373PnqpteB63vpY/zG3pHYuIb4nD7y/KUqt/bPVq01LnWLyveoOTLTPC9uj/Wb5kqtLXL5z+U4Zc/hzj2/2'
        b'Oi3IC7Fy9vr4zOqbK7ziNmds1LHKtl6WNNHT5stditetA7ovH4t46ojhXnXF57+UehWnHbrca7Xep2/SVNeTAT+aXTgSrlbE7Uua9KNgUfCpElm09D9TUJd7PsK3N2d1'
        b'4Rvx1k/7WPtsbi2PLstI8vl13SzH0pK6qog1j21/rHe2zMmismfG4u5vr8VUjP7CPTbEpe7Ek2efNbrUFbH4RNfVV/dt/vjc17Ciz85p/YffreiJuNla8nj6yt7tG56r'
        b'mLbAdfkvLzx3dh+yO27/0XH/Je6Ldr0aBm8fmtYe+XKW/Sf9Drnjpx9cVVb/gc7EsseOPP/jEcO5owo+8djmu1Z3intB075yp2sDeXNc3+2xSSx4ol8nqLLtsw0/XFsR'
        b'cu2Ecq46VGuG8bZHF6RM+qnxR29wM/BbscvKugvSDr7WYh/T+oliztidb2+otv/585z6/Nhgn3U/Ka/JH6le97hp1ytjxnecfGHFF2//kVkjq6pc8+WClzY91m3yYtUf'
        b'yDVyR/HtpwPHv5fiNv5o49FvXyqJnZfS6wIfXLx8+/31D1k2vrX0VOTTgbtiXun9SPfrqtuP1+/lYwLz33rn+9mnI/Zqf7ml/cK4S9uqf5oTmPrwT0+t+SHttbCYxl+9'
        b'b4bsfHjW4zdfWt3UrB/ZsmTsqYwv/oBidUzOyvFtvl+466xsrv/uSuITCyU7lvz21jvez4/yKx9ULKZyH5ckL6UTakADfgLeUU28apEhU/S1Qe9UfG51kBMEnywoX+Dg'
        b'zHI59JN9fBGa6NfS5VFKb6gRfLXxx7n8gjj8nAiKt6FsdAZ/V3rHhStRg++B00wDUjR7iQmJfOLM3CrIwgRrObrEfF2V45NmPwyEEBW9cwAxY90r2KMm9zQiWbBMAvIZ'
        b'0aD6OkFegI8DykKV3qgYcp29HOwpzlObC8U38TlzuEALdJGj/MlRqru1+mOWMtltI+yHCnRhNRGaoSJHGSfbJEyBnIdYY44qglUBjt4ORO4LneiSHC4KqH+qlEmdsyaj'
        b'CtzDClR8l0/dTagFVTIXaVlwCi7IVXggTw1hLzV2zAvQUVbNMXxH5KideTQwXGhoY8/Eq1X+m2SqOx6+iMwQVcMBKqn0I7owPAfn8PUtjY034lEOOqfFqs5zToMCd6ij'
        b'fnjvOAAbh05IU1xRE9P6lO3DI9jluw9d1OjtFomW0NC7GhM8Bc4+flA3UeVI5H/+YhFTUYWWO6qNp0uFKNAy1KhIHx33JhOjMvR3RBdVAmf5kBTOoGYDKkgcg04YEMRD'
        b'lzc6rCtmMPAUUE+cM5V24x4dI3gKZzgNh/wdHfyGVWc1XYrOaEE+E2N2zyNqfCoHzdPi1i+kYtDte2ktVqgdH/YFeOEWBDj5+Dl4+/Gc4WbJXBjQoe893aFL6cIEwKLk'
        b'12CWRBtOwlVa+EQ4MUolOvorVKECbU6mK+iHzqCrfVGQUk2F9JKtgSib343qd9CPeHzt5w654ISrW1AhPx4GtjIVLuwPHHIniU7puPFwyn0T/U46UWftGuqFkbrn1ELV'
        b'POp9CNVRxdRYe3O5k4pKtVt0lDzUoBNTqPs+OxiALKLBPA9n7+NiE992l8SoPSnQs1ONSYqWwCFVIqodx9ZUp/lOOEs0nBoHmaP4TVA9jb6c6m1D9E5Eb0mMy7uhn4di'
        b'OLebCYSvQgPe3bhHh5WkcV3QN4eHRtSNetn0tEzCJHIXnoMGKBTV9OgUFDF9XwEe9OMmiRozGqK07hX4dYidCxMw+XVE7U88rAyZLZ5CDUwbUKeyJ5PKVL4oO53kMIF2'
        b'CSqwhHNMgH7cDI6Qll/cqdFO6UC1AHmWUM9WdIMDKpfbe6KzD7AlaptJ2zF6A3E5ynzVSjDZn2nKQ7udBaskz88Llduw15SIknGGURJPPCZl1FEkOoGOwHEo2JaBLhqk'
        b'aIiyq7jEIiUBdTujYi8/R/xVoKeOITQlshOgACqgVq1EzV56mFxW8Jz2HmHmfDHKuXoLOqNWLoDsVLbmtaOFGWmjRLfFqGw27jOUJXkTFVEAjfGnxY1GLdJRcHoSnRMt'
        b'GIiVo7wF6PQ2sQBoERZ4MzzEXL1FZtCDi6Df44WqzRn6SzzcoJ3qsVNQLpxQ+0CZBzEk4lE3b7xCzvwrdq2EYrkC1awVFTdBMMgMaVpgYNGQ4gblmg65WISzHP10vsIP'
        b'v2830pjJYOL3IrsZjqDz6JAaFeIF14NZCuIPFGVnMH1YHVyBXNxQvFv0tnrj/UnPB2cvVCThpqCzWnNmzaE9mmawQe2vSPFmtlOFISqeM54oWRmBDjPrpFyoNVArAqGG'
        b'OViGnkiopOPsMAXPARshCWYVmvGVttOdeYUdt3Ub6oZ6pY+jytHeH58qRrGS8NlwMo14J/NfhTtA2yW2iiBi8oh1jWITKkWXtPB6aFan2eOsOzck4aUBbUEjVgdbGQGz'
        b'MWXqDu0yf+iFTDoegXjznLvjfMhQzqMDqGgbHebQpEA5ecPg/FmozJlo/nolcM4F1bDtVpYIg0oVlM4hVw++23RQnwBHUMteuqWIV2NvzAdOWnm3f0gTyLdRGPz3mp3/'
        b'kYbofj4GSHzU/6D/2cdF6/HGAgGOyPgJvD7RuQhUvP67TMuYan1IoCyiGZEJOvQvQ5zPkLfkbXk73kQwJkG48M8EmteYak5kvDlvjss0wf8a4h8dnFtPkAnmdz/hyY8h'
        b'1UCRb2UiiMWM3zl6uOTpLncHCi0GIXmP6DHeHwlL0f+v5kLCirtT+tB4emOGUj2fjOefK2n2cz22D1bT3L9Xf8l9Qux/dJ9wTmNWflc1Q74TpmvE41S+7GAVHetkZU8E'
        b'ZE4us1w1fl7udaXwl5q3mTQv+c+ad17TvFvjSTtEWatVXNSIGv9SZTG4smb+uk5oJBPCP7DOrqE6J1PMMwX6xljRzwhy/2/XTJxYKPjrBqFDIubQuAdXf3moetvFVumJ'
        b'cSnp0fcB+P/dNmxmbdAP1Ygb/6wJPUNNsCcjoE7DQ0AFlkOyyn/aDLogx/7ZjPcP1e0UmES8CyXGJFEnCVbhEUnpaSOcFf2zYUglrmceWP/gyBU3zHnOP+us159VBkOV'
        b'jbtT2RLvpf9sdaeq/qyuRzV1pZJgvn99tAr/rNAnhjpgF3Qfl0caxx3/dMvoUd8DocQTwAOb8PTICaPuA9im/UcTpiBHBK01LemBdV4bqnOs6GriH9a4WXM0RITHEy1J'
        b'aFJydOIDq/33ULVzSbUkLxPdxw/XAd7tm+SfLSbcKsOhVkXGJ6mjH9isl0Y2i2T+r5r1v/J5mX0/n5c8d7fKQuIf1/T4SamaEuVv1hH3lTox7/q67NLmdPL4y+kvK3jm'
        b'Nf9KEBxH3VoUlz2cC0L9Mx/gtnKaxqiGkNn/kajax8XuNLvrso+PTgwNfbDTSlLBq4TKIG65/iOVsZ9r/RPXlfet+v/LxGz+axMj9Q+K23B0oURNHu8ICVCF60f4xrz7'
        b'DGbwFbx9gN6dtXjvyF/g2MinZvP30DahoRFJSfF/Nqzk6+t/Y1ib/mRY71/3iHElbSctIGIApru94/VT41aK6W/5QwZDulshVwuPuASPuEBHXEJHWdgrCRz294PcvxLz'
        b'QBLV0XXEiE/yZyEOi13GE02BBc90BfxUVB1EVWYTDZjK7OFNsfpVW/RY7EB0bmKG2jB1NzqhS7LX8U6oDfKoVmUwjuVP9o+IPx/nx1HPEhPRfmrC20G0OkoG8yc+MgpV'
        b'+A9/4jZj1YpVjmsEbpOHNtTO2kz1bvaY1StV+RB1ABQ7+/gxuRl0EmbQPlILWjfDfga67dBDNepkf9SP+pkWhA+DLlRONVURWqhE4wkE8/M5Q7bBwWiQfr0EtaJaYsWu'
        b'cpxIpFRSRx7OobowVnQPykNVSoW9F6rTQIShEGrSCU9IYh61K9FVa8bJEqYes7LRcEodRHU2FkpoIJ1VOPrGeUs5XW0Bs+KFUVSbqTV/scrbYS0q8MalSnmogfJUOrRJ'
        b'0GxI4FUKy5mYy9SdJ8CZZXCMfrNHPZoggcagYxooULhAv9HDI9SKCoJ8Hf0p3ykLEUYvSKaDiC6MhywVkao6EXPfAjraqHCOE/FUoFyghYpmxd2zMuWalel7Z2WOXJf8'
        b'kJOz/2pNksbr3rMmnfzpyhMS2Eqy8t6mn+cmFQGtlUsgn0bqQAchU8S0TLVl70rtYJAGZNKCItE8WIVyGXz2ymSoV5qGj5wqtRHzYdICR+EIFUjCAUNOspXfnZCRTjbM'
        b'KCiwU5NwIcL8WTr8RHNoFlHokIX2s0jkAtSi1k28MypJZq5x2tDpxWKcIHdvEYgBA3gOSVUTdMeI0Z0MNonQmWxzuprW4S1UQZAzkE3weUPRnVZJqBKcQnZRp8n4wAC4'
        b'gv+czE1WCQot+imxrXUjn863Hf4llOrSOp0fgioxwtKSSQy/Mp6jmwPVQ6W5cjGU3oOaOeNJh20vOsArNWgclAXHCCJnI1SnE6G95wQ4rMQVOins/ZwUjj5+PGftA3lw'
        b'UGseVEA9XZpTrLapfL2l6KriTqQmwy207HlGcFq0tcZDeB4vWx1hTAr0UX2wVBJzP3vttFhqsR3j4ZpOkQWlYxOpUb8vFTKTgwTyyRZInMjZrtXaGrUgfTrpZjMMaBMl'
        b'yIOM1f208GGUy/lDpjYqga4Ypo0tIk56mGZ1zAp6qqRCDx3wFVCVohoGNkidSY+UFSifbjoj1BmlObigA/UOHV6akwvVTaFrJRIVraJHDz54oDOJnT14NorZei4YD5dp'
        b'cCDYv51BIuAAlIvA7iR0itj/45fFYaJLlNIp9B3RUwzgd+QwCIbz7DywsWMn9yBx8E8j3qGBYHaKuO+jx0sI5GTgdUskkwOoai5eVQkKun7i0AVOSQIRoYGxnDQcH4HG'
        b'MEjbPxaarPDK8nJ0ICBRdBWuwFFhN6rWo3OIt1Ular07qg032X8RsZaPg9Ns8bZBJhTjXBuhw/5OHCfU6kzDFZhDoxM7v7ZAw/AjbOgAw3v3jEKgPR8/ZS4UoM4M4mai'
        b'3BA1cQRxhfpp9yI22anRBRnBPF1GFcTRRMNKaiqCanU8UZm/Gr9y4BxQw0p6j821kHP4Mx2Plbv0B6fJmduBs1ECPSCf35MU/0v8fPbQUc3sCDizPb7PzRMdM5zQZ14L'
        b'3k2N9tVNT2APv9yky+Ft7FKyLUN/+lbnex0zUMqR/E/2x24uxHAPv5tP1o/i1uCDNEWIGuL7KAkkRmnmM+4i0a/rzo+NTozenpy6MFpXJNTT13PEV87Z3eq7pKXoCPOU'
        b'6uDtCPn4j8oRjhlQGVFLlJmooNTVOGI23kjNO6B5tJZnBgdVU1DJytGoay06Rt1a6U+GHKK5R4ehMBaVOTp5U/SKz8oVjmu87rmBcK4uQY8nUvcW/bBUlEUNZRIjLJU+'
        b'jgpHlH9Hb4T/reMmrJZCW4ok7lnDR6XqZ3FXc83aogN7Et/wMD4ZUlpq99nV+Kc6Hd/47suN19Y3eb1nvWe/VdGRmPBpyodPxz3seX7DPJd1UzMXPqyldWN81u4DR4y8'
        b'KtxWt+z2iImNe7RYfuTrgR2uXe5LbR5dYNH36+CsqYl6ps87KHRmv/+tR/KzB+tP1gsL581Ynhl1fbXvlckn5i9/7IOfnlq9cburcVZag3LA680VqT/fvNjYP9X55pQP'
        b'tpl9fDrhkuCmvvF99Cj1i7cveux8zXFR9oYQp6Rti2P/5bZS+eSM3r3Rbb4r940798mJp560b3508oSsa1M6vvzXHx5jghbvjDT/YVnJK9NcYlI8P3wxZ+W0wsmL2qeG'
        b'fbfk4RO2rzzx5NHvlykSpny24quto6xOTXZYlvzwtGdeyY/g7Z2fqvH9OH/e4SZ7/+7TpvVTBs6+rn717McZN774vv0Hhzd6jvx+szqma/wnkrFPtZ9AP096RH197R9V'
        b'jy/4MNLwqmlMyXeertmup8yCP9rr+NTnn9bZP7Xjg4KMlQmHbF85+5rQ7FyyzevL08HlBS+l5yTXfOPwnk1qjbXRkxNLe30/W34jZFVfQ/uKtye8x79n+d5quPnSHr/2'
        b'wK9s3jPId1gRFah96Owr1p0eiU8m9Bx4J8y74jH/Z4osha+6omZHzPY55X7l13angPq5fa0/vzbPqe5jp3n2gcs/zImc9m3CjcLok4vfLhvf29KS5j8tf8XXL078den5'
        b'7V88NsZi8HDocy80Rzc0Gj3yXfanwe83Xx9rqpzyhfG+wEsXJ2e1vXOwJY932zbNtuNA/OjX0efPuM0dOPRRj1t2W/qp96/nbgi9pXP72x/iK7/yXv7yl5aNJ4u+ftMl'
        b'8POa0vTu3691fdUXeNkyS6fw5o0nOlvXvV9gcOEXPqDr0Mub18wtqvcvVU0qcHSXux/IQ8/o9yQ25exe4ppW35Gd8mpv3ieKqxta8kKutpqvuV1b3ZIeNru/aM67eeqH'
        b'336vYfD8c77do5t+PB7b8ruexYQ+YVPW7R+dx9yaoz4Yo5jHFH4dKMeKkgBNUpRpSk/n/plwkqoY1qJcOT5RK+QoX+Gta4cJZ0wfjoJGCZyIhrNM9ZWPSlGH3F6BOhm0'
        b'KAAdGC+s2abNED6HoEIphj5swoQtUVDHs9hokJm+RtS6bl7CYKXxwCLUBUC/C1OKO63ipLE8yoFcG6bvb7LyFdWxcAIuiwhKM9TI1E9nk+xFKshwlUgFaaMWqm6JhVxU'
        b'I8eUQh3pS4qvs0LGGeCMttCICljwvgJoX3ufwIeroZ8qZtNRDWtDA5xFWWqG8FwLR5hmthj66Vs5VEKHqJfFD3uYbjYQ9bIWXoYqOCun6B7BFK4G8QvxZXGMjdVpY2cx'
        b'fCcqR/uJ5hVTe0xrO4BOQqHczskeHSQw5iEQs50RnUQz1AfdLG5lAOSJmGA9PEPkY1N8zat9FXrEQwI+BFVanJ6+AKfJtNF6x+CDloLaHeyhlSDm2gTX9TK2OBqEGNUd'
        b'PwO9k4mrgWkoi6qn9CLXamJsok7I0SCY4chSho0bhCaUSWN0uq3RwJ93MpsIwymb8UfES0ChZJ4tJ53HwwXUgFrpS70MT/kdwDWmZlrjhDjUzZDKDnvhtBrle3ujbhWx'
        b'szihnyLYzwyjHRkPfdPkQ/hX6IzxEYLXm7DAj1CzikQpRB2SFKb01VsrQC/0GLApPYIKg+XQnIyzhIwjja3mUccCdI5pHMvRCcihQQ7xOu2ZZMZPcVzP9PCF46Bb7uOn'
        b'lIVAB6b+e3m8HC5AH4Me2qPThL7XdVI56RGaqRUPrwVcks7BtHM2NUExdkeHRTjbEDrWbBXmMookqMw9kpnydGFqJf+eqI5WWymSFQZ3ULFRCtSgBoYRFXGfbaiEYD9h'
        b'wJ92wnRCsGiD4uMgWqGE2TLnBtCNjsgfwmNwr08IdFTGsKEViybSXbEOzjkND0kJLVDC1Mk50AHtNEakoTYnmcwvDpjFxnYQnYcCEnQTXVQtQhUCp+XJoyKpnM5ZxNRd'
        b'NLrgdHw0iLDFY6LqegbeaGUs1m8ppoqJonlGCF0EW4nHLjlFFe5DmQyUHC/aLlmZoDb5MKQjakaVnLAStcyhn3qhXh0alBBPU4MIdkQlK6gyHo5jRvviXVEJDeESRTuu'
        b'gEFqRYL2j7KVU1Ai3sk5Ct4ydSv9eDaUJg4hE8XatdAgQyYmwWXm3/2SHzpKgwhGbmW4xBWia5GNeDGeJNa2eBHiLuMtC6dUwmSoQnV0nMKCPVlQw1Q4JiIl4Vw07ZK3'
        b'q0S005oBB0VTrRnQyuYte5ETKnDwh+xAfHhjiovHB1Qrif3bCdlMi1wJvQE0Sy+qJp7Hcqkrx3YB1WdAKVvlV6APLpFovJhaXANnoZZfAQOolhlUnNo0WhngAGcdCY1P'
        b'7bfk6KqAuqE3ji2M1ojtcntUjEfMfbQfPxO/uSoCJqEtXI2XcNvd9jx7F9OmRUN5BLNh25k6ZMXGTNhGQZ/C/P83QuwuDex/70nxuh4B44RSI3hKdr9JiPD/LLDdx5kx'
        b'tKOU4h/Jb0Pelmq+HXh7oq+myEA93oQ3JgJC+kOQgvp/6EsEmXBTz8iON+ftBBPekLcQqA5cjG/I/tUXxhENt0D06SZET46pZAveWCBxDS10DAWiF58gGUf14bglghWv'
        b'd1tK/hf0/qD/S0ip+jQmgDlDbQrG+MlOxd1aZdL/UKf5VAelXuh0ZzwYeyG9rpu2PSo6LTwuXn1dOzRte0S4OnqYDv0fRDjALMvvRBX425DS/Ff8lwSXqfYgw/+f5a77'
        b'udsPdvGYTuRVqB7virq/xOb44F12P06Hm42OGTk4oEMKCRPpFGfAIQI+v6CJ5k5DuZ/UZ0KIQh4dUPk4TIN8aj05pCsYB/VSXOvAdOotERWuhkPDGhEgljXJXbqAeAJA'
        b'J+wxF0v2+FiohQFV2q7hleH7mwldbCbAQVxZ6Pz71aWTQs2ow6Fmh3J6CJGWnrPz8nPy9luZTMaDhuggHhB4Lmy0zlRUAscpC+4HDQ6qMHTsbmP+3qW05YsXpapQkSMm'
        b'lIJoMdNnrfTCbTMaTVrnNhXTbjx1hBzgZYsK0qFsKEzIWlar3TDxx0ao1jHahi4zOQk+aLPuPyTW0IbK8YXWQ1EjIZDvrL6rrNWig2LSpaI4dAxTRTH7dKBOhUriUkpa'
        b'eHUDXsVfeehHBz6d+KKH2cnKiW9cMJ2W8OJZxw7hwxDjz9tXPDpON0/LOspVL8Jaa5qiLWbqspL42RVr2zq9pj5SPTri9VnvPJ/kofMtf2Kstm6eX+qeaz0fn3K3HJNn'
        b'vbzBbEFMrm1+3UcD7+SY/5HlmBdebd+e3bB0do/z69ozrm+YPOGJI2YeL0QG7Bx9fbLrreK6HyueaIgpqP6+Msj100mlsFPL57XQ9Z+XjlU+4caPmWASNtltYW/x8+nZ'
        b'hkVna2x2/PDomqqxBmOr3Po/8/jMXmb+nMPRuekRR754ZrWBjf6h4g2eP6ItvRnBSHHcfnVdw7Gvt/D9n35zdMv42oPB6i+uPl3WO1+xvfaV9z6L62goO3RdaXJpelTT'
        b'pHkhW70dtRO2fvjyyuMZhiWXl7o91p1eWZ52y+/XTx7puJ467td3fm+8nvHyR/aNC/i1RmsS5z27/pr6yK4dVct3lJb1T8+9Ub1x36Sq6uNXI7OsPT4K+fibLp10l3rX'
        b'LUtuLFzb6R380sWqf5dGXzA8Y6FnWnQ5U+uz/t6wd8yq9syvXbK2Ycr3z3yZ8cRzndphTtdvrvuywDT158BDHfMmxK55ZFyx5EeT/IDvs6t3Vix99ddKvU3bJfbTQ179'
        b'8LETHWYXDNPefGf8go5yr8dcfvn12+iPl7W+5PXmsa4Wyafv/3vBxPL4Wz6trd/9FipZ+9lGyZuv+O1SpeitNV/74SulRyO2fP3R3ie7Lpvb/jvvrVYz05z4lNvjvnv0'
        b'9889ksKUjxtYlBxfbVCzISl39Rst0PvIzLSlb1mWDO6adOTtvLiIelv/EwHvWHu+ukfpl679nNzFoLvV7pcbytcSni52O1r5jXpb0Yb2G5FnItPPX+l7pPIN9+2P+W4J'
        b'7rV5cuvuvhdde+oDb7xXFvi95eb+0a2vbB/zyfwzXm4xr0hcM0KyftatjXrT8tfS+bbvFSy6aGy4qvqawiWN7B5vqN16t6njvWaOJpMNUasTYwj2Q2MwMZ5Eef6ieSUP'
        b'7ao99OVceyr2d87AG6xJyjhJdAZzGZTOODsByu/Y9cExdEg07IOTwGxPdVA22k/4PkxcMINowvmdSWYGxkf1UZX8/l7kKuAS6oBqb1ZRJ2oeg+luKIfWIdqb0d1wOZmR'
        b'JOVQj6qpW2shg8c9X2w0kRJ369HB1SKdb8a7oaNTrKSUNdyLTkOzxuyYCLvRRebJBlVIUeVauBi0h5lOHkDVcFGOWZBi0YsJh9rlpgI6gPrM2ADmojq1PD5AhQpTFJgO'
        b'38Zj3gJTY4xl6sUJzN4cIK+YbSMmqa5SunYOlG9Xi47ViIFpRqzeNgFaleggYyz3y7cT28f60aL5I78TnURXaK8g1w31YKJXxglrMYE9x32DNWM4T+FG1qtRnf6QwzN0'
        b'0ZiSo+HrgHDBpRvuMpPdBrVsqqAfKtT23oshixyeVCWShTo2Movyq5BvKUc1xFPRvRxFFYjWjQWWHPG8BvUjLONPoXpKTy9Bl4k7Iijbdk/4axN0AfbTXo9Fx5Ui0bzY'
        b'npDNmGRei6op37EIX8nNpBWHRfcj1HVRE5xmvnCujMtQk6AAkKtFDFAl0MzDYbiMG0dJ3kxXjogCihJiCKsuAcwnHEsERvIGBaLjcie/VPIemtNMoRVXPcpMsgX1ikG1'
        b'j0MFOkz4STxyY9B+PHg6BkLUJpTDVmiPLhld0dWdnQyz2VDKfN1By540EhFgNdTvGgmUuA9IwkYPzmFesZ6JCI5KoZGsXZG/laODlMX1hU7aIx9TOCGHMiVjcjUs7j62'
        b'rYnAGmVhtkYbnVfKNIxszXQ6kBNQVYYKncA/4r1PPBXimWtnKIpya2L3PwJpEjWdUemoyYsWvwMqbFABJgzgdDzZ1wE82o93YDadw1WBeEtBs0Maah/ym2eCztCRCt+D'
        b'ypQIs2VOdyM0YBCO03UyZTcqxTszdJ2GhaCMG89ZROP7nHBPpAtLQ72Iga+DN5xHtWTB6swVIlAfDNCjJQBVT2avR5A3kyykmESrRy0wgFcFmfiAGfhwYf5fCqgHLhKv'
        b'VM9XgBIba2bj3LCDxyURmgbynH3kmN8bokJcgmWmmPaopwdvLMrHf9/35A2YjRt5TmNKbI0aGLN03n43FNhYDaMntTnDYMl0V5yB6CygEbWg8ypN1WK9qHER0f+gXC24'
        b'CFdRM/M2eHppMqb+rmBi53AAZgudaLAyzlAimQyNUEenLHIp8biHecphsBrc7XyFyf9HDut/5ZFmuMcZG41xzEt/jddK0KdR3QknhP/HXIw5PwHzNONIfHfCDWGeyIJ6'
        b'myF8kAlmCAiXRDgxs990tC1TMceE02aScZjtIhHYST7MMtwWMD8mYF6JuADR4Q0xF0eeycRnehIZ5r2E2+SpTKIj6EgMJfrU7lkmEJ6O2B3j+rSYG30TXoqfkvbo4bz3'
        b'Wu5SHkvkp5jB8O//S0tkkZ9yHjHEb/0NO5Yzf8cMmXaGWIpZ3Dci++hQgt2PTGNMZCgB6pMwuDQoO43RTiOzl+Bf17VFk9zr+sMtZK/Lh9uqziC5iWIpdSv55UF+7SH1'
        b'6A6ZCF7XFu32rusPN6e7bjDSjI3YTFELHzo8bDZG/99JLO7YKL2Dq59DZmcvR73bGEoFB942QvRHI/k/+leqL9GXUA3tLG8oHuKUoStmCJs9FjVJo1G394ONwZZxHPPH'
        b'wg0FK9YeMgwT/nmUanJ/OnJ3G4Yt908nNqyrYqHb1WXmjNnTZ7lCN5xPS0vNSEn3nKvGx+F5TAd2YkLlArqEuox09PUMdQ3kmIzIxfd7KaoIXIGOoMo1WpgIxASYHE7O'
        b'oBYVMyAHjrhy0/BZPJ2bbriJeXw/hNrggqtUggZwDpynFg5SVXFk8HJXAR/FZ4nJimskZLK4AxehHOW5yqALL8+Z3MxpcI4plus8Ic+VD9yFB5qbhU4m09ybUDVqdNWK'
        b'R30cN5ubjc7CAM1tBH1Q5SoZgw7jNcLNcZPRp+PW2rpqbwBc4VxuLr7UL7KnY3YDAU9v5rh53Dzo0Wf+Bw6gKktMg6ehHMyXc27OcIm1oztktZren5iU45ZsSqamLXDR'
        b'FeWoBUx/44Ys5ZYumpxOvM6bGkjVsh3TiefZZahvIi1g52RUoOZR83qO8+Q8Ues0+jQMeiertRaSK/wh7iHUsIA+hY4gR7UEj+B5jlvOLXeQs6a12aFzam08Od0c58V5'
        b'jUHdbKRLMDmeTYHgOzALhJmgOmfm7aEyyhZhdqIRHcD0EucDp+A8Ld8OzuqgLky8xnGcilPNimK1loxaiLpkVvik8OV80cFUNjFVoaRwHurDOc6P8/NEx9nzbl2ySLTg'
        b'tBvH+XP+UMGxIanYhwmcLskufOoEcAEmcJY+5lETpmS0nWA/x63gVsxBtXTpQJOQLud0nan/fJS1keZFtdAJB+TSvQl4tXKr0IFV9LGfDJXKBdSBOojtbSDkrRZzz5wv'
        b'l6FKsqCCuKAJqJy1rxZqV8p5TMd1YvITE6BFhqKlgjxZrjUX0yBruDWY3qlnQ1ULZ1CXXLILTnJ4u61F7XCGNXD/dlu5tj4m7NZx60bDCTYTl2ZAOxRwG4Ixi4WZrAJ0'
        b'lDZlDBpYCgXSCMjmuGAuGPXMpI8N/DB5WCDAueUct4Hb4IGXNillJh7XA6hMaxNkcpwT54SKjWn29XABc5llEmiLojE4pu9jlWY6Qk0gh7JNqOESOoYGaYc8FYGoTAjB'
        b'RI6SU8JpdIU+jYuG8kDeBfDM23A2a+EkW26JE1CZtgIaOc6Fc0F5s9mUlULOZlQmk3lS6w0Y2MEely+EtkCt7fhPW84WdzhX4cCkcOehMoVaKRQoCe4SMx3Z0IUKJJwp'
        b'OilBvah7LfV04DTdV0kiZeFfEsxN1cxJxRk6cAZ1ILOcylKM1hSCM6SvSRUL2IHO0AzQho5AL/7cE6ppJp4zs8HvoQaOUycbKFOLuD8cKmQc6jbBZRTgPJvNmbeFA3hA'
        b'WCtIhgyoFjgzU/zeWUGrkECtCfucvMbcVTZ+z5M6yjeyAgqgy4rk0HPEubShFjcSenAGr3hq2DMqYB8rXnsK+XBrCOrdEMe61+y3RdMy3KTg3dZi923xAmAi0QlK/O0y'
        b'C9z5VCtB7LwUWqlAESp3xtPPcbum0E6R46d3HZxirw9boYP4nYcNHd7a+axbRnhVUHxqLqbya9nQkCZoy6URYsOhcCttXyoU6dCm0/e6ZOhYzwtxFUQoiyqCoUZsAusE'
        b'5MvYNJNurME7jYXyRX0uJBuZ5E7UiVnpwkAySo04k/9e1pyj1qHiMqA5dsvni6VgVusIm+xOsy1iZWQ0A+FChDgiyhB60ULFUo87HSLtafFkrSHzvQkdouOSPMuUVnQA'
        b'daayVwXj8JLsw32i7F0Nao/TDCtpDZQ7a2Z0MWJDa6dClUq6rmmObRbz2cDs0aENXTFPMtQMbahzhyOaziYtp/O6A8od8ccBbHFrTxZ7unoBXVB+G1AmeWGDKpTaS4am'
        b'HfajC2wcesY6k/dWuhLidpl2AypwjkhooQVMR8c2kj13lBczzBeLmGBFuxi+G7O2moEkQxU/h9h5sWEKHENthGLHklhgYifI7G7eQPPQcUBXvakMfbIDymR780AqHYEa'
        b'zJL2LrZl+6IJSomFnHJKOM2Sqdnci52oGdn6ZbvYnpJwZnMk6ZjL74US1MVWQ/6oDLF9EqiD/qm2mp0PTaifjoI97lqOuHNIlil688W9n+XG/OvUwgHdoQNIgqqIJpZu'
        b'gVV4A5E+wnF8L+cMm+l+vKVSNccDEndZgZsXLqMWqnEuwYpnRWDen401lITEaXYw/s4GXYpga2HibtqTQBhQDi1ZlAUXtmvWNcpBJ2kN/gF4jgqUgdNIKzOhX1xM0G9B'
        b'+2GAmvzYHNC+Tp4UoSmgFreB1LEAimffmU1tdHjfEs1otaHDtI55qC9BsyKX0h46TcMlXEanFDzthwzK3FQoD7ocHVAeCcamAx0CZOKtm/0xJRlLUj0UetTAzpCnrqCS'
        b'27gw36eDUpnV3XU3fWKKF1a9Oiz+xbU72EPvIGqKZyxPCvPNUNqzhyvtTDkiOkjTDptvznmwh7NGUfO+ua+owuIrZA+xh80rjTg81ckfzQnTb5+pYg9nhtH4QWFTbMPi'
        b'XzU2ZA9fXTuKwzPq0bMrTH+NmxN76GSrR4wLvXIswvS3m4ayh7vXmXF2uEn13mETnlxlyh5e2khrt5B5hemnBQjsobCQeby6LQvTv+oUzlFz6a8njiEhkbxenha2+3eL'
        b'OZg3DHqIvlhmR+2ow557KCy+3nE7y31OT0baOvfmtDDfLfba3MfVx8h/Ty6iFdT40Lfbs+zC9H3sTbmPXel/NxfRy3WaNwlJIYGTqJTjkrikJY6MmKn3gUp8qrSY4y+5'
        b'7ZCdxAyXqZitDe/rlmGrzWzoEJWgSyzO0xYa0ilsuX3YxqN+E1hPkw1H0zHpWxK2e59ZyL0Wk0P+yMimjxVtJlncpTshrETEyHWtuMSo6O2pxLz9fgGXjDBDzowlF+Bf'
        b'U9AJW6U/MRimloh+vgGogtlGBqOK+8etwgRbtXwxHIRS2vjQ1es5TAVzZ7eGuWWHz8Yz4u8f97Z/i0S9Gle8be1Fv1VUNTXg6v/FIztmp38x/6nW+fIzHnoJmebCDaPe'
        b'peUvr1RearKOG+PwVZs+hFj9Ilk3d8PC+q1X92vJF0pq892d8tcVzld/Ne+nN3dFNZlm5RwQ8pPfq82esTtohadB+sznH5kQXLV8/+wlyz45XWB5a93DWhsfsdn42GiH'
        b'9+3b33NLfNc2MVy3O0X76SsFFR1P55RGvD91S03Enu8nrzzmc6LZLcUkNnSj1rbkrwuuvXNwznW7etNpSv8n53pnzvrqJ8Was/u1p/j84L8lP2/aJ6eXbryxxGMivJpt'
        b'b3l9wxc3Crc99taUD3RVj25Z5r4gMMJZ/Xp45WqPjflNqsAzm38zPZz6aI6iALSP+bxv47TrQufv6h+2BkYfbg2ZMcupcUtnXKjFa5Zn9657t7pZXaTULn7p4R9ef/a5'
        b'jfptBS72h/x+vLDGzED2+Y3nbc9s6beyyFwY9+lL7z70kZ/3awb/euW5Cw1WXTOjjhY9bPv8Ddmcb9fN3rwmpiVo4sni54pVR386/HtDwJ4Z6l9s9+4+9a+6+PfecNz+'
        b'lUf/tMFvZ67++nbYi3W/zBw8X1Hxeo39i6Wv73F/Wv/Y49W6Vx692Rf83Sr39mTheKbu+S3XX5sxubtT71TKrha/42+sGz1mwY7jn32rd9R36hPq8G03tq5OKG5wu1Hs'
        b'+1r+6msTfW4X+4XM2Lnz9HOfW+j1PV2+OqGiL2NrfN7yR0YdTX2leftv75ZMCc+pe2KP9PgTYy0rF77YDvL+39a9v6I0pGviQ1GB/2ot8T2M2o4a//TFpCO7rq3L+8hq'
        b'TV+wyuR2TULnyS9jPuj69qdv5xRebu7/acxXy144OD9dYUglhu7WAUT0itesFqe1m4dGyEcNAdDC1BP1MrwdC5izB6kXtIXx5Gxlmo1AEnuUBANUOdrrxvCcHB2XCFCH'
        b'ztHX6Zjp6CFxE1C3WouT6KF8qOanwwBqoiWvtkVNSlQMbT5anDTKHzqI0ilvHVVwxM2FXuL/x9vBe4ejlJNnCOh42E5RD5MwXuWwAF0cHkQHqqyZHubgDELRFDvb85w0'
        b'HVUu4vEWPO1KdUfpqG+S0olEnxGgiw+ZuQa17aAy5pVwidIIzKqNk84L3UKMjLK20/q2QFOE6H0Cs3v9Wpy+TEAD6vH003i8fa+oqPUMrnAMvobLeajbibKp+ibeeJ9G'
        b'VYU6ohdj0uwyC3uC6g1VqAhTuXcFPKqIUIz/v7WNebCwUPtvymuv66kjwxND4xLCY6Op2PYqOXX/ionMPs5PKrptuP+P9FvZKObMQY+auuhJrEV32sz5thl+KqOiWTPq'
        b'UsJMFAQb8yZEhiUxw39ZUVfjetTdtw4vFaTUPQR13I1/bGm0Uz2aIq7CrfEXM/hUPUEjAJRcl8QlxA6TxP7F4ZELmjuDlNWnK8YH/QuyVvLzuMWDrVcIAbwR35KXRl47'
        b'Wpz5JqkHatRRoKp7HMDqae4/H27IAayMekpmYC0hRm/I8av0Lzl+vS+OlgANdLh7XX8+WD5IPJXjdggxwj+Ai94jFST/CffUr+VP71mbWMH6a4H8FaZfbjmVS6dRevvh'
        b'IEeoyrV2It7QbgJ0eHkHepG97a3Fzdkls0NN0+Om2oZI1MRq5oeqUZ+HeYU/E2NX+knYxofPl2Qeqc2efrD52IW8CwcmV2V2aXErm5K+lf386iqFQM+01PiJKkzrD2pc'
        b'1MjmC2PcNzMD5oPrMS1wj4rczFWMfXwUMx0iiOM+guLr8sjN0ZFbQym9Qreey1/fevs4O+aJf+ekUOITOZQ4VLhj5jWsZM1G4OOGbQNhxGo3GFrt+viv0Xqi5Pcvrvb9'
        b'3JeGD17vRLZvpkugHs7+jl5QiA7P4Cnk4x4QCsEY+aFiGeTDGWhYQzxlWsjRyd0hDKRZilqTVQ7+qDjKEBVKOdk4QQ9yUQPD9tXEpSlRqb/ACaNgELJ4Dp1eTpfNRblE'
        b'+I2u6jDflyZbknCfLELPXtwIX39/RycZVG/gdAIENVzazriGQPmWAYEQpGHxn1st59REMNVpnhhokJwi2fYRCXrDDbxECey3grXMdwmYmvQIi/efv5KLJyNcOl2Le9Nt'
        b'Dt1Rr6+7Mv4RTk0o59LX9gSuTv9BsWCbhJNo8TYqFa3txhKtCStYEQ4H+YWcmtCsZb9O+UAgEM3wxXLb2zTfFWPZljgJHgmrsPiEFYtYPh3v0R9oEZDx/CWG855SE/o2'
        b'56mODz4UzuUTmZjF5zvU5Ap9caEQuPrSIYMMg+QgzGo58uV73lGTtb218RyN8tds5+Mn8QngTC9Ibsi20suBorO7Tde9aPSkw5PeWm0FnDYvzPjhWVqvFD59kSwdbmG+'
        b'4rMb9NGCXwNexMvJnqsJsi+cQB+dd3u7AB8dIdx6l5B/t9LW9Z1OLPg39/M3HPc+d/AZHfpsVpNrwb+lHa9x3AdczrvOTDR1NIUg37wpishVijnJHkwxFAg+qDcx7teK'
        b'5VJ1Fy7ZPkrwXLU48WUP/UuxM570/SNJfvCPhlzXoOc91y4Q+pyMd32umrnKc6nywjdeXnz6Xptl5hOserhpzXMNtB8+tVvX06ctdvDj2MeNPuIv55Q8M2dSplVEqvSn'
        b'10IbtmTdiHmz54bt1OP11j2LB6u22Mtcq2tsq83aDY4/ec3D//2spyZlaHu/1HQr0T9zd+yvpzJhv93PN2Jyf2yf+vjRz8xlpvI1/XWjx3SNdemVfrH5rac2jI540mZi'
        b'2tl9T/0c3vdczA9THv10ffuOtz3agvKUq/NPLegxfOiLOSrt5nmJYe94dk6fOu31mwePb5S4b7tZvee7jQZ2WxbenF/5hWts8237hcKHf1zw39QNmXvkjo9UvKR9uX9L'
        b'2Cs7Jr5ap//+ss+cV587xUe7v/Bp9/sTgmKDn33/5osdh7MaU2f+PnagZPDC9r0926/dzG5/vq23zjTd8/Pe178IjF0ZjxbbL81oGv/MZy+lrdl9e+KzCY8dHPVQ/+83'
        b'B/cteyzOz/Gkzq68gLiuw0afvFz4+rO1O/c5fyXfIStIVv9m/tDNX94a/68ffuHcuub+VvrFH8Envqn8tfls/YdnLX54quGzlT8e2KC2OaHUeWNfYPrp1KZjCmN6qEbB'
        b'2U0qBSpyRLlKOxknixXsodeO0mYWqCmYeJ+kOELoccfzXiIkhUMZJesCrEKJFYifA4cOwCFOOp2HNmgHFljIaSmBgZOTHxWhAu2EQPxtrbDXMpRq4Y2I8FSdlpFhYAjF'
        b'1n5GRqhTPwXfu+gU5nJN9jIqtWcfqhepW2iF05jCxeRtmCE1Jg/dk4EK/KAN31KQjdnAdn75JkNmcl+IOd9DSh9SNxTFYaJStkowQ6VrmdlPuT0B/VJqc+oyTG9iWnNe'
        b'OotEVYoyIQ/TqazKFdDI6coFKEMXZjMrdJQ9A3+pcIT2TUQHIwsTpqxeTl/hs4KCSFA5nHIQUSRj41ipV6BFovTR0cLD6+2L7yw5XBDQSbyXDtHm2qErUKXy9qNDPBY6'
        b'OZ0QIRrT+8wqzBfak1X0tpPTiJ3kwkOX4BTrS9nkKRRk66uGLAWeOXfBLEP2Xyq4/4mR8QgS9s4VSO/Ro3/nHp1mqEWj3VAi1ZA3541Fz2PGlPyUih7JSMwZQqzqU99k'
        b'+tRGgOQknsyI7bcxJXSlArHxljIbb/qdHfVkxuLJ6PCphkOkqdZ1aXJ42ubr0qjwtPDrurHRaaFpcWnx0X+XWJWkGpMyR5FfRkMXOanH7G9f5F9Z/jnhCnnQvPnOTS66'
        b'/DT3k6KavWbamyOFYZQcadwQoUi8pVE1Mh8jGfIpIPxznwKaCu72LIKvd6p2uShBlZiHIzDwPAcXf5SHaUET6JagrPQxcXnTZkrVZJ801o3+POyTsM/CfMO/iNaLeddX'
        b'mxt/zuiIJLArdJgTEskDVf3XDcisjVx79n9n7W1ONRlaD1I2e3Qe70+oCXdPMvl49d+e5HPGD55k6vXzUhB0scEbmmfI8qRTbbNUKygVzv/fTrTknomW+Me5bHuNozEJ'
        b'5nn5s0kccyQ+JiLKK1wn5t14npv0kyTmp/V/cRrV/900bk01vXsajf9sGo1HTiP5eN3fnsaW/zCNKy1VSv8Rk4ivmhI2i6hGK4yD/gdPIzEsOkQmkj8kjZH+LyaSTOK9'
        b'cSX0/ClxbxtmS0l7VIqqNMQ96kXVlPLd4zlJ2C3ltj/v+um+K2PLdtCHrzhRkH6yhTTMIT3ShgmSf9jBk6dht7aFh+qsUHBUc74qHbUEwjl/4gYIZXNwSguV0NzrJFSS'
        b'b2fjFBZftDiCoy2xJi6cAx3RUaWXt80KCSdbLxAX0c1xbkZTJOoMnOPWtLCJz/QZCNONs9879u2CZRKvNI95Oqugwr9Xf9mVYt/zU18KC1RcVQ2Gutbm5xzOqvWJjAx/'
        b'TGUYeOSM6QzzKLdTlSGH6vpmdJ6Y9fonbnWGsy9dnWr5cXuk5MKr83a+Nf8Ft3PqsNqbj3+9Rnn1jSlJc/tvv5NlOd7ocQULOmozB/UrHe284CCqIa6+oVpwdGOhUNdB'
        b'o0pDNxnt1WJkE3RPYE6uqtFBKFaReFeYegpA/anEQ04hpmOsRDfF+9FxpYg8hV7UqRHQHRSjfUMd2g/d0MpInOqlKI8njsat4TKmvWgNZegSqsEk0CE4RaVuosQNZUE5'
        b'k/ENuI9RelGhGZSgK9I5PLSjc87MfjcbHfG9I8rLgIsUoQoXxt2zbfEGu99VeGcz65MzOTkqJpTcroJmMf/lvZxIjAUNiYSJEgPMBWmq2bD9TZb1deldOKl7mimkjibf'
        b'RGraRYvY8Ld3eaPJg3c5VYEXo/rR7LD28t4MA/hyZmM8CWVL0VkotLnnONUV/1WPuyuSWbmkXL9cO0aIEop4Kl0S7jgDitGJkkRJs3UO8MHSaK0orShZNhelHaVTJATL'
        b'cFqXpvVoWhun5TStT9M6OG1A04Y0rYvTRjRtTNN6OD2Kpk1oWo7TpjRtRtP6OD2aps1p2gCnx9C0BU0b4vRYmh5H00Y4PZ6mJ9C0MYm2hns1McoyWyd4VLRWDBfHRY86'
        b'wDXwxXzwKPyWSNN08TE3KcoK5zCJmkwPMOvr2n7hicT28JbjiJg5JPCWVQJ7xaKKjYypg2lTcrjfc7rqao4/4jySelyiJnV0iMmFqTt0zkr/0jkroc2U3jrwH0M3jWjx'
        b'ndBNDwqURHYOi9VE/iIhmcJZESuWPWQVExd/n6hPI1YZWe/3ChIt/SluDY7EomP0ICABXQIc14gQLziHch1QDlxw4rnlvPacLagyndgIrkqdKU9OCcQvxZzorLZXkA6R'
        b'ZZAgysT7CCbuIq109FFDNDNbKcDcWCbzm8NJF6LBVB5aUT300rdw0A1VYxZvyazhgXEd0Gmqh541HXUoffyY2/RVqE7Jc6bTJOi4HZxk/oI64TzsV83wEThUosejDg51'
        b'SzfQi8YgZIqKxnuGLDhGYj7LoUx0JGUuUVHv+ltm4vrkSQI6FoTqGKV6CkrgMDuU84jjFJxh2mZDVCNZ4hDKDAB6xshVcM4Lt4l454dLUIOvonVwRsm6c9HUD1cbCn1E'
        b'PEm6A93CrinobLrofX4AZau8N6IcP3ucQaBSFMjchnpo0xwmOrPw5egiOqRx3bTMifnsacKM9RXRvQNx7oB63Xk4ngKX6EhsQueMmXMsuAhFJGA3tEARm4CrDnBJ9IDF'
        b'SS2hkHC8+KQaoG8XToJ2TfB4dC5M48gqaS0VqZWaEEV2cqTUI8xBucSPY6ZleahgRSCxWEI1xLaMh3x6hZcpieL84XXaOPMtr1Qi3aM2NFeN0em7nFahzs3W1GnVWQv6'
        b'6WvxRL3+fJSMC/P9zjeZRYmCJi1CIlEvWpzUARNM9Ty+DQeC2FwNos4A5TAvWvh8LaeetEKglFIPaXAAziqdUD8MDgtuv1lFnRwRpBIqv9fhVTo6IcYojkGtTlT8tQVX'
        b'Wk+WDLmwyayFQ6EhOi0JWQi1cauC3xVoONdbo6fuKe1bhVyMPbd96Hdj7tfdWoNHjE43NNan1IdbjDHzz/FJTK43c/lF2vee+/qERyJlXl2922LXrn08MmDTrpebtnyY'
        b'bmBefCvu4102Fz9JP7TcMVhr4J2JJgUGV08H9Ceel2n/+oZk/eidhvERDzd6PvfT+rJM2esXEi99mb64se7XOu26S588U9P4gmF0rMXvVrdWfr/++8iUpa+ffK1kXsW1'
        b'JjRu4qnzO7sjDz338GdvH1jqPr3W32C+3cLY9z/6DZZl/LvY4LWDmRkxlRkvNwfvKHzrB+UrT+64bvPom80uj2/515YpW8ZOey7xw5+vpQa3/fLiZeUmr496K6pVs347'
        b'une76rWEOW/2zHh+8ozjb14e/dRGu45jpRNOBv3wWPkj5S297zmUOuSvn7r+e89jXX8UlO5d8YKnzy3PY8uf2lfWk3jmo1WLFDfPP13+vd/6mNTQx25HBFvIt7ls/42T'
        b'ZFZxP7+gGMccrLSQTS6SKtI5cGAUplTwLi3ThGTIhl6Vr70TznBhHMkjjxdQw9pk+joOurejAgd0eIG/qIIg8X/3wBFrSiVNhE50Qa5aN/Oe2CargimqBB2BXOi6V6eA'
        b'jqGjolbhBDA3Igq4SBxhHYaD0fSkI0RzsAGj1jJRrS4mBVjwb5RtRI4dtYCqg1AJVXEmwiV9quN0gANCBr+Y+A6gDH4NnIZK/OU6VKc5BZUEBHZK6rYTGsUg0uNQBxQE'
        b'kDNQEo/OoVZ+jSHH5GBVwfh8Io5UfUl4s5pV63hM63WiTA0R2k0DTmgijeDO9tBoIxdjKLRolb+SKsQ0ZyFUosM4m8kcCdTig5JRoqjbNpkEcGAnIpxC5STLLgl0b16Q'
        b'xkyJcpfTNpADcX0Y6fpK3HV0FDeDTFHCDmIbG+BNDsRxC/DYym0EdBploUJKp0rQWbnSSYrTwyLxzLCmcEMJbvGRIUexFOSGWoKMdCVpqHMyWzyXgwjOKMALszLsGJHp'
        b'CGOhdR2LPnEY9XmRedGcIUwwgc4Qw6tuTXT6KgfUSLFoPn7QSLFjcryGULe9OSPVG1AfasV10IMbH9pxkGm4VPIQqtmaRpRiZtAwnnF++KiZaXpPNHSPdO1RONXMlvOV'
        b'xAlkzIcu0oT/R917wGV1nw3D92DvLSoq4mCjgqKgIoiyh4IIiMqeMpQtiKLIBtkbUbbsjWza62qa9mnSnTZJm6QzHUnTNn3Spm365Lv+59wgKGbYp9/7vuEXveU+5z+v'
        b'PXFUJVpsu29nKh/81R3HXxhHiaBPh85L44gYFjxJrGdBP3EKLOuehE9e8qx3ZBihoSKGHqKF3cbSzzdcyb9ogsVqTwNWIvELC/a3BAoKXCUHPt9ITshb/VjeD9fzmvth'
        b'BV9ZFpCCSESCv4xQ5l8yslpcDpAC1+1g9ff8zz9k5NQ4J/aXfUdBmKUmES6fbmggySBSXW9AkPvChlER/+q+dcd19UsrHtV6z88ZembpX7yWufZnFYl/dSU268kMqw0L'
        b'DLhGARIR9knh/BfvUGAsfFM2OCU2OvEzegZ8d2VB/PQrPQPYW6GpackvXotcKjjMMuy50/5gdVojp/jQaP3YKP3YVL5R6UnLk6un8GLV5C8LPuMGfrQ6sx5X8zs5MiI2'
        b'NSn5hTszJL/7Wff9xups2yWz8a0YXmx3kuLy8sEJSRGxUbGfca0/XZ3XkKvPH5qSqs+/FP6/soDIzMjwtM/qRfHO6gJ2ry6Af+nFZ1+FaS4d7vlz/2J1bpMV4Epdg1oE'
        b'ZfwA/8YKIiLDCGieu4Jfr65gB4dV3NMv3lQgauXYV6D1uRP/dnXineug+9/tZyC/am967tTvrU69Z61ezU5+RaleP/2a2Tlm93TMjXA15kZQJMgT5AizNG4IOHOBkDMR'
        b'CG4Kfdd8fl6Jdjb0s/Z1uc+I+XnBAvGSVtP/CNiwaTEHiRkxkVxn59QY1kL7CTwmR/INKLjOyolJqc9aH56xQKxc2jNug0Lnv4m5lgA/7//zSksAriGA9k+nW14xFvL1'
        b'AppDoY3r5EcS8MXgNTIwieHdzylNf2Ml75mBwJeQSm4JZLN2rLC71a0+CeWJio5M9Xp+TXs27R8Zd2fM7wtz91xBzfNr26cxgymJgfI4IRELsW7VJsKKLD0Vt8MpErCI'
        b'3fBYRpH+bsP+/38dRM8GjdFNG1oqiTgH0fxPM5iDKC7q/ZCyaM495CEWGEyL95p0/+YdSRMIqIi/uHLhGofWXPhOePR57qPkmy9884qfffMpkan8NLnCp4LIbgvXTv7X'
        b'F7j/ss9wH7E7Sk2BhS94/6RssPuH3vMmivRNUaaxiLPayAVDPQ8cUqpCX3vovRXL54Mu2GvzL0lZCU/qw0QYTMX+vWOXOMWSvp04evBKtEu4R6hHaNzPH0XGRMdEe4S7'
        b'hXqFCj/UvaIbp+sb8Jv90lZXpwWC0dnvvi/3l4mgZ2LsNo63S46UgAo3zZe6J7GSrIooS/2Zu+IHz3v6dtZP+cEL3E7t8yPqNljG84k158fja/sLVv14X5Zkez5Dbx1Z'
        b'eGEKLzoQgV5vXk7RT0mNjY/XTw+Nj434HEuxULAR+5HxOufEGeneO5EtkKNn1Nw/SNTV/J/LsTt/4i2dEkzfBF48+17It8OM3nULVYr6LX0y0xBXe5z2MfYIsUsZ06mM'
        b'MP7+nQ8DFTzs++M22zbG6drqtjSVHIvT1Rm1iBCU7DcLCfrGGdT/auVLbdA6p/6qj5bs98WWDVZiwfd/q+sAacZyfBPNWhtoNYVhmFjRb0m5VYFpsTMuQjtnLpBPx0lT'
        b'3s7CjK/bbJg1+egRXpPvDsEBPpSGt8wWQyuzzmJXNPe9yy6s4RHLH8Z4osMZm09jF6ec2+oSAkE/PH5i/mWmX2wx5D1q5TiCD9yxF9o51Z1rMeF5gfsuGJs2mxKSusKg'
        b'lCASHsnEiwyc4R5nwMnEIXN3WFKi78xkBFJ6QhiPhrsSjva5/jW52JRg7mo5VDr1ZVFJky+UyP3PYsK50h5Sa3TKleHX8LznrOkJE7SgR//5AmhW+Hzv2gYLMtbcqCLG'
        b'mtIXnLMvgh2SmKl3TMxI/pRVwpBbUUnelFvRDd6U4cXsN2V4+fdNuRVx9E25VWkycmVzPIn79ztMriFNOvTxCjsztmA5kZRYSagX9J8qRqGiqCbiHBJS0KO9ylakBQqW'
        b'MAP3RDAPearPsHUNyd8pBU87KmVqdWsFEaJy5rqTLVQu1CjUjJL+4g5K/i2SPxQjlO7KMQcl5xKUk7gE5dj4EcrlQi7QXpHGlopQiVDlxpZf/U6aRGC1CHXutwrcinQj'
        b'NMpFEbu5dzS4t7QitO/K0/eK9L2APVErSz+6ETrlMhF7uMIa0pJeK8qFKoVqheqFmoW6UUoRmyO2cO8p8ePSj1ytPK13a7k4Yi/nmJXmvIasd5BKoSqbrVCrULtQp3AT'
        b'va8WoRexjXtfWfI+93atbMR2et+Qm5O9qcq9pUNvyHOuT/aGCre/nWx/tANRhEHELm6HqhGanL5j9KaKBC/or9DoyOSfH6TLWUfkHfTXP8E4A/2doh9KTGEtq2C+ydBU'
        b'/dBkZtC5lhZL8L9uoCgS97nnI+ir8FSmKMam6qcmhyamhIYzTTnlKRemayqxnqRkyVSrs4SmrOpYxLMS9UP1o2PTIxMlwyYlX39qGAsL/YzQZNaDzdb2WR8pU9+e2uAq'
        b'yzt5+pyDhf6ppETDVP20lEhuB1eTkyLSuOXuXO8llhjqYuj8nsn4WF+BZbX6Crv61Qos4iLxF8r1EHN6n9TPLzx9UdyRPeUpXuHiCStbeyFn8erJMp2OrnftdWyovDEY'
        b'4K4uwkLflbN2RSTRikjZ04/MjE1JZb/JYCccJjETRW4gWUgWJNHm+TU9o+NnxLJF0jdRaTRcaEQEgctz1pQYQf/rh169mhSbSBOutYZ9jljDrvNZB7iyF5dzikPnDzOH'
        b'70r9VJdVPx9WY7kHK3Z6EVv3+bh4eK1URoNlLFQk/WrJPY3JrpugF+48Z4g5HKU3JZ6BdCyUz4EHUMinUHRDPdSTyOFlvjXdRUogbSjERges5krC7JffY0pQtwWbMgWZ'
        b'CUf5TP9KaD3ga449OJ6F7dhtKRBbCFSPiXbvxNE0QwFX/5+VJXnS7suI8+vzbb4OG0vn4DJUZeZwhUqsPLDEVMSKAKcIUnRwjBPwIFYkkLoRJ2ZZPanJpwRpLO7OwyPs'
        b'ie/TB4u4LmLlZnhPCzo8+eKxZ5NkMVefr3FzUM0h5RoMa0kz/4oASrbFxf4i+PfClLeZfPkXXc/K417iA2r573xs+E2ZD0u1bp9y+KrwZ3urjM70H7QwcH7T6ED349CW'
        b'9ju7Xrc5p1KtuT9duzzqoHfSf7/6ulLFfifvfxk4H8/RxIE/mbn5RS54FST07AjK/taPfjdoe+6QkVeIdWyAreg9ueisj/75/bNdB5PPZwa0Zz64ul9jca/eyB/l/qx8'
        b'LnzXG/9wi+94pWDi/U1/Vfh1QfqlPsf2pfO/P7LrLde3o2e+p2mb5p74m5NLP63+lvTZP3z0O5Mf9iz914chR4srbX/tE+0x+MknFSoVlosu7oe//eHWXxw7cuPhG/8S'
        b'fxp6arZZ3ViLL5e/GACTXOgB1KcJWOQBzl7iBExP67OK7tgm84y3UT2QkwTPWyS4e7huUVvTtwny+LQnqbNYvRKuVQcjXLjWxRhOLLXEeiN3DxOoTrLgH+AcoNAHJdzX'
        b'dtDPCgqsBHNBy2kumOsQFPFCcT824h13LtyDlciU17ppLIJ2aMEqXhWf3Y9dWEoigtfWcwwITGRI5J4Unz0pafhgYYhNpvuwxAwGoIlkCBl4JDLDR9jCF9KEMX9WXf2J'
        b'9xWqsEyUE495fBeM5mwcI6GbFROchHGpnUK4fzqC990NQ0MmF1MPDZC/ElOPgzmpLNIqCrstuLLv7ZxjkKnArJ2cDGHjtJQLbaCSr3NZi2OwxCkLYhhgpyOjKVKGQmzg'
        b'HKw5OHwTSqEN2ry93Fk1QH6Z6tAghorD5twQJtjnyNx7XlnBKwRAxVfsCSWOqUzk9cdGFuLC8ndZ+UcuaUoFH8K9fe7mXLFKVijDGcZkoQJnIvi0hkX9YyuBHDghI2lX'
        b'1hHO+fgSNeCuqYUA7jxd8hEfQAtXX9QmHYtoR1ADeUSSYGVSGYGOQIzLaTD2bPjbFwld38ild46Rzy+jT9iw8HoZLkhfhQu4VxLuZ59Jt7DktAve7Za1aT3Pfk4b8VWO'
        b'vMb19hkuTDH/7AYOt62KkjivL6GN5Ap+8/zE0edu4MvYyKU/20h9TFFipH5mslU3nNUqo3+Ws6/h4i/ol2P29OSUz3IZnVhZYrIxC7Fby3TXWcmP8XITk5fE/8/Zye+S'
        b'wpstfGp7K+f2jKHTeGCrNGfSHhN8Q2LS/tvbHmKBXJFw6kGvsZBvalLtCs0sc2MVf6HQYxWFDbDlc6zayTms4erep8AiJTw+mEs1/VLmascXwo3lzzBYMwCzOIaFTwyW'
        b'U+yDh7c5MbG1JAvrnzFeY68rM1Hqblc5Hg5TnxMSzxnSCoUvFBIf/cVM11K8lAhjUG31NJlnEZDFHjexx8TNDPrPSeIhi1g6FhcbOADFijbKOBgrs91YlMIoUgy6vhdi'
        b'ofH7kFfCjHRMQj1CdUXxUfFh74f8NiQx6v2Qkmg3Sb5EvZHcvq//3VjMsRhrqPJ9eu5n+Esm9hGLgUk3HsCKTwWuC1uCcd8nBcNH5LbzlarbdsCjVTA8SLLAWk7iCVUr'
        b'MRCfzS5WLO7Jt74oVK43pT9jzL+9zp7u+UIAOvUZodoMQBV1CPa+PICapmA1s5XrnlRx3Q65xiIu49nDCGtXbOushpQQeo9u4yNUH2P7vhXz+lEYE8JEGt6N/WGtlSjl'
        b'IH2/NJ76tH09Ptot3IuzsG9eY2H/NDVKIHjJTD7U+dSzFvbPcIfcEb6omd1fSUFNKkv3ede5xtr+OdOffKEL/MrzXSLPXxSRTIbUz6cb9gLOBM/ohjRRDulVyiH+UkHe'
        b'Pc9onM6RqaRqS/jtWrvK83X1hOTIKF4vfiaSZgN1OjkyNS05McVW32G1ybvkFEL0k8LiSMP/HDV4Y6Yp7ZXGWgFvxrwUTsxn6OB3xt/8vL8LKwBm91RIuAXRtdyD8nEw'
        b'pszFj1ubYaP7Uyozpx9e9cd7EvXQR1EWy2VyYg85KQpTvOmlh7qb3wt5P+T3Id8Mi4nqj2QOg4CvBOBo5VhA911jaaNdX//uK69/7fWvnhF3XSEcmGi8HRc43jjRVNrq'
        b'FuDbaD9+qOyrSq2xgpqPx0zVMz78h7EMrzB0QSu08VoSNsG8gNOSNKGW703QCnm0vDW6CKtvyqJBz2MX72cexjtQr8i6R3ueubhOQbMkbYn5ylSILvBR5aKb5qTZkeZf'
        b'LfFYErG45+6hf3zVSqB4QYTDMAGNXHEKqNnqsFH7hskrHEEm2tK+DqOfL+auLVnBkmsksMPhuO2XxfGrfLidHFfPJWvLU2i1ZnheiOiThMNxpvUnMvmGDKJPxD/2RBI/'
        b'RkOceyFaMKz1fFrwGYt+Phl4Jmzji4oOEoHwH1MbEoDUZwNokqJW0jX+8/TAgZ/zC9KDjb19JML+IaBJOoWpx1tSkt4LufiV736VMLO+vWBn6YHG21bbBPuk/gZS2cpo'
        b'LOLCaG/KQxGX88TFrdJfnbw3YQvel8pyAklka1cUDLm7rqQ92KhyiQ9QDd0rnq6NXba7Xph93RKwuM6NoENyNRK5+LhoRS62E62dNeKFILXtM1zFn7EWYx5Z3pRNCU2P'
        b'DA5N8Xq+DZrpsxL+JcNpVDIvaIEO28gCvQLFzEQfIalD/4Vg2GHVnRCZGsqC5kL5YKGEpHRiiKxy/Mq4/1sIwL8jOTBbZqjmHAlmzDqdkJaSyqzTPEKmpMYm8qGETFfe'
        b'0LzM68/rAsCYH4EG38i0vYp7bK3JoRn8cdGePwflGHA/a4lW8EpjoqATSY55z/LgDRnwLZiVjwvAIb7ezgi2Yq6pG8EazCi6CLDOEIe5ijE6r3/Ft6Lbj5WakRJINQlT'
        b'E77DGXrDpYn/Xf2xrMA+ROnlKAPBOb4GI2Nx9tgPRabebKxyGPARYLNJQmzkJ0HClDb6NvDvjyPLTVVEDmqnBuajM/Ic//wDPcEHtx3VNCIGtOV03gjXdXnzWn5T0EOb'
        b'zWh70sSvw6TvN1c/7HH+hVzD9ial/IKP6upao1xSd0XnJf/iNwZ3q6vP1t/5hqzRST8NuD730uhPcp22DZSnnPnemY+/VtXZ+CunlpNnJ18deu30n3+2Z6l87JsLdlkz'
        b'C4s96XWTW1zvX9sJO9776Ftvhid/Koj8yET8172StFxS1prP8XKAwXZeCtDHYY4Mhfuzfrfw8JLZuoQQzOcttBc2p/H839dnHf/H4ii+c9L8BU/OWpmMjwWcsXK3BW9G'
        b'bcE7KaYwmWpiIUlUkD8qgge4iNOcuRLbzmCJpE0l1kHuU/ZKU5ISWJxAZhIsrNpqNT35zrAeR/hsjnwcTOcsrbyVla6nSWR2BZc3Zr/GMl/U3PemrCRHl6OzLl+ezqqt'
        b'1NfYK1Lj+nPIcQEFRsIsnQ0oHk203srHSQn2os+XKEjPePLsGgMf/TPphYh1jc7zifVzlk7HyhkZOWotvxp6zscGELgI3pSKD02MPucULrsG79nGNFbw/gIj4CzPlBnE'
        b'FDjfL/M3iwpVC9UKxYXqEveiRpSGhLDLFskTYZcjwi7LEXY5jpjL3pTzXfP5SYTQz29KbUDYHSIiWMR6YmTG+gAh5lfjfXi8yzE8KTk5MuVqUmJEbGL0Z6SYErm1DU1N'
        b'TbYNWVW+QjiSyRhIkn5IyLnktMiQEDNJrHx6ZDIXcsE5mZ8ZLPS5TmX98NBERsiTk1iYxkqQbmpoMt2Hflho4pXnc5N1nsenpLIN/Y7P5TGfxZfYQTDHaMrVyHBuh2b8'
        b'KW/IZZ5kSiSmJYRFJn9hL+oqoPHLeJLykBETGx6zjt1xO0oMTYjccAVJfHz5yjnEJMVHEHCvYZ5PRZ8nhCZfeSoQYPXSUvT5hA0LfW8WKZwRm8KvgCSAmKQIfduotMRw'
        b'Ag96ZkUgD9lwoJXVh4fGx9Mdh0VGJUl48WpaNw8EaSwQnnnxQzccZy0MPfckV8P0bPWfzuZ4Etm8Mu/zIpwlY4VZhj07ytqckM95n1EKElx8vfWtrWzMD3D/TiNqQ0gY'
        b'EblyVStjEejzULJxwPWpyKjQtPjUlBUUWR1rwxs3TNHn/smiLZ5Z3DrpRgKZbCtXScmgT19ANlsn9KhKCN96ocfQi4tKPRJ3MMWS2IEwyQbuCOCxGvRxMs1p7PVTTL9G'
        b'9Jh4Zsd2AUk4j3YZCzmbGjbggx3MTsf6kd9jTVaEjmmynC/+0AWco9fO8hKTkYW5ERbtM3H1JOGp/9xVHMfR86nneYc41JrIH7lxOI1ZWK/BFA2z1oUPIzm8svLEfR9+'
        b'WQ7aSaEv4ESodgWuxHmAbUCIxy+9IgRcUvFBS6jBUoeza1zwfDCimbG5m7TguKkMNqem80LboDLJbNvhNlbLCITqAmjDilhuZD1NrhKKvuyekPhLDtmS6ufaXFHyEG/3'
        b'EKVZa0lFdYESV5TcJVsqRGlbtiwvwGE7zERjpwiqcI4VLVTE+aNcdS7ulZGTcqwIu2A2OiQ+332XIO0oe+UuaW2PuBR9XxfOzuxKqy8zZYJnmamGjGQv9JWLmZuHhau5'
        b'iYwAS42Vrh2P5CTXk0dcnpFby4xJToK+c7zUegGmmXeZdjsrD51wH4acjOX4vPYmuE8XytyhuZskqe1CEqdGrvG7qRPhEp/YLrqMzUbCfXJ8twFF0h77uaz2vdjNJbYL'
        b'oeMWVnOZ4564FOi+Ji1USQ3LNMXaat4c/DgaQC1LK8dKfT6zXAhzTiZcQFyUDxSvySmHHmgScDnlu3dzy7kWtct0f7LFmnRyDWm+I/GS+55nk8n5THJ1A+moDH9jRe7e'
        b'sxKhkJ30UWzk6iEIYcAsg1v0XkcpUyi2fxK9ymJXWTMd7px8o/VM1+QAaxpCLiyJscXDgCsdgMswu4srhCDEEZhkrYoeC2GR71ZzHwYsJGarMPODwgOeeI9PsJ8+CoXu'
        b'K/m/iklYeFOETdckPUEy95DIubYUwjkoFXC1EOgG8/gBlrZtf1INAScPcxGxcPc49+0umQx3eCi/JuL2sSgbZjBfEs6CnUlrsupNLwi4pHrMxXHuLnK2YYk7PoSHruuK'
        b'JWAXLnBbPgMN9lw4TC9O+JAkLY4UHj2MpXylhU4chAlfUp0q/c6w/n3mMdDPet3npnJ1DT7x5Ar0749yC4kvO+Al4OAi8CS9Voo13lICkdJRdXam5XDHWIE7jWMRt1JU'
        b'ktNwTAnHoB4bVaEEH6fSRcSJXaPTOew3tcWq1We471NwMo0ZQnpwAevFeB9bsJEL1THBGaijZ7ECKlafz0i9Jp+srCIjMBJL4R3Wr5DbS2KSDMEATqZcU7pmpgDlqslp'
        b'YoGmnvhwcipngr2MjzVSrqUpcGOo4pQ8jm3GQZpZ6RqBoWQNJy7LSJ9x4RtdNJ7HxdUX8H7CyjOakWIHuOvGdU85CT1Bq8/wC8P5IFrbdhiW2uuEA3yPgWl8KLP62MVA'
        b'OpFknKTVnRbbWh3mHnHB+asp8MBldSwcT5URqMmIcPgo5vH9PcacYEiRNCVaiJK8Mkn1yjdxJlwEEwQ63Ry2XwjBe3SbZ86wy5TG2avXWIfOZSOuEoSKVaavJ1b5YjnW'
        b'+UK5lAfeIVhpFuK0GIu4J4LwTsxTE0AhtNIMMGzIoeVZa7yfgtOq8kn0rQh7hCbbaWrGUgwtsQNLiSC67/P08PZjzMNHopCbMcJY5uqhHI8lpJTBHT/5FGmY4QbcfoKZ'
        b'iqf9WcV3oa0Aa6GL7p4txiXjKE64EK1wNyfM8pISqEPrWXsxAVUu5HFE2sFui4Doash3N4VcfCXAn6fcmgGmAhaP0bkj5KTJVRUB34hD8PEJyQcje2MpLgJLC1uhGQYI'
        b'OUmVui64HibL92ca04uEASm860RESJCFS1YcA76EU9hgKouNsMT1kPCVdDCDuf2mWCo4QypNrCDWB6dj2+VLpFNy6N8/8XZM8HFP1HRQG/pg80/+MvXy319v+uTEu6o+'
        b'37BV/FF8oH6Xmbtwb3VkuVjjbMVdy5Nx+0R29jpWPt/OPSKt+DX1I0LDn6VV5N296+R7ye+PaWkZr/1gsezDXeZWwp98s+vPkzVJ443xExG/cfOq+Pa2dM+b9t0zWn/6'
        b'6e+sfnXB2q3x7eJPTsnaGks//o7RCeGPxgKkyt41+GNce3Zg6aLPzVkjl7OvDff9/md/izO5q1IbcuL0Ryd/v/TXxF0qBaN1IxHmHh+8/r7SkcH8/Ze/cVbb+Gzpab0f'
        b'73Z52W/TzZG9NTmuHhZL31c/6NX2/f/+284j72bnPwifeCD+4Ga18ccTLs5z3Z0+rTYzH8n98bdvZExW/THS1VjR+eVAn4/qfBX3t+VV/Tbme5seX4ArF69qhiTVBpn/'
        b'Mt/0kO3+bzam+h99NN6snKv/k4C9H/zk/e9eCP1D81Tf1Hs/SgyYj/2Dzr5L2Y3w3W+73TH/al2I2592B4z//E8fpgVMNpecnn/jaMPst0zLR97sTba3P7l1/re3Cv1b'
        b'JvwKZY03/zTzZal7k0qqSq29C8sz0X9+NzLhaI1X+RstQa/8+lep1/BQaebUzKLNaMWxXzX+eDgPnL8TcRON58ZffS9kz/T0d7Y+8tyjfTv9Kx//V9Q7h982O/mHXf/T'
        b'/a+43p6mkX/95ZJ2z39ffuX+T/Hi9OQ7r0QeszTs+M5S04efvr5wPOhrW+ZMDbQ3JzQf+snR7sczL5V/bKYm+9pSSWZhhs3wWwbnHdIF5X8M3fbntyszH6hmpr52Z0ve'
        b'7++V2HgMKai/9dr3YP7Hr4Srv+Vv/stAv+P7+03mfnTr0dzJP55ptPrX9dszWREGne/++Rvdf3k55TdY4fTSp1eXg0++Fn495vd2B6Zynfd949a/ZAWm/7L7Q6ixBRe5'
        b'dRibdpiuD3/ScIVB6BLDw/1QwTd+boCCcyuyg1eEcJ9xCuf23sVIh/uKH92be0AdC3EWbouhTAbKOXfQdQVoUoQB7Hd/Jl7PGe9w5poEPTX3FelQ0Q0HRSLiRZO7uNe1'
        b'SEIpfTqqLAwGxFARBf28narRCvOIqROVniXezNmTbHz5ELE2mMVGUwvjw25YshL7pg+9nMEdSnTMTC9gscVGoW/4yJ+PfCuFQRu+QlxLBJPf+ApxXljDWbJyiBSbenmm'
        b'KmG5jEDqoBD6tvlzM8tDK9QzM1MitJqtxPPFocTNVcpHuzEDVTsxM67RAysNd5fkWq5CLowbsgq5sOxivlIhV2M77wHoZvXQ3E1h+Aqdapk7MeXrot34AGe4oXcQc+52'
        b'h06vJxWD+XrB0JPNrdh3+wFTF7OTm/k6MKwITPlh3vY2RKyy3V0PetdEMbIYxuZ43nA2gY/4xmT7ZElh6CARYknoRwIhF66ZEUh02tXsStBKyg492s5XX6nIgk5WPYZA'
        b'pJQOxNOMuP0+vGcsxjq4L6kYXE9LdfdY4/SzwDZibRcgjxsdS1Ohb0X00pIWHiDKXMXBTrQe8z56uJ3FvidSr7kJ78lsOkHgyGTbDChZkW1JXuIrphzCEY2nhNsFnBNr'
        b'q1vwvUYmCLwfMfk2yWtVvFX14Z2gU1i7aa18WxnEi7ckBzRz1x9yBMpMVbFlrYhLa6lM3cOG7pO7+DwhF8s9paOwEqa42wyFx9BB4OvG+zulN0G9QBVzxUkyMM4djEYq'
        b'V7h4Hy7aeLPSiTdFJpctUrko5onME6vyDkk713BKGUeFlnBHFkaEZtghLU9i+R2++kxvKLa4k6ZTtHpDctgsgpKtmM+3555NhrqVQorFao77XGHISCjY6iQF9x2xkTvP'
        b'0yy72B2LfNiRHCIcEshiu0gOygJSOb7ZciqL8c1lfY5v5kAzj4RTJJovSyq7MCwk+NHchWXnxERURnCeD8MpxwEY4h+y8Iy+iCUkwtP02CgFraSo3ebz2u7iQqApdNmw'
        b'57zNzFnWJpGaTYekTmCuC3fyUHEYxp4qILpSPBQewbB0iCl28l7sCpqVKy1Zwt+NIt0vLosIX+voEV5XULjFHOE3SC4tNqPD9xLpQaEXf6LDqaw3I4v35aN94aEHH/Dr'
        b'n8w/0EaYV4gTqukSiiiPfQHyIhg6ix0cCVCww24SHMz2mRsbMQiKFsH4lVhj1X8/W+qJIfg/2IV7rXs9NCJinXv9QyZnfTnbuDVrsKLChcRq8RVuWF0b4XauPrWc0Eyo'
        b'IVJZDZeVE4mEOswULQmTpU9Pt3T5WEpRSrju52Op92V2yHHj8c1ceKO2HP2vxFXVkWI9uP8qoyQjZLWx1bi1qAhVRBpCFc5OL8fV2tnC1chR4UJ2VYSsRo4KFxSwgQ91'
        b'zbFILPnyvDl+1TKe7MhM9Ks28eRT6637/159cll+nicDczPyk63OzXkGXOhTiaKkU8uX8gzkCj62+OKO3DUHYix+U27Fb/okAzFcSvDkPxnBGnvYRYGAzyfiHQLyEoeA'
        b'kHMJMIeAqFC9UKNQXKgZpSlxB0gVyeQJcqSzNJhX119wQ5pzAUjdlPZd8/lJqMLPfUUbuAP8rkqChNd7Azi7eKjErrvqAH6+jX3lifUpR6kSE/WaIcwklurw0MQNzZdh'
        b'zBOhz/U9YqbG5/sdXsQkz5wcG85qsrI8E30urYiznq6sg7eF80tijg1aeiJvf97YHK7vmBQRaWWjHxaazNlv+Q0nR15NjkyJ5Mb+co5t7gAl3ounSx1t5Hag4TcuxSEx'
        b'aq+Y9JkV/fOsvl/Wxrtxs6IdXmks7voI3I8ijuQtaXV+9ow/PMbW53q37xnL4wgsQGXaAXrZ7agBkwhX7KkuzMSIRd6+EsMq5sMUb1zNwl55KNdJ5c2GneqYz3nEXQTp'
        b'2I91gTDJadG+WxWOhfDtZJTuCMP4djKDD5O5djJ1hXw7mQ/STjOeO2aBw6bwiEnYRVjhy4yhnh4c5/XnIn/Xhv2u2gI4S4DYT1lhN/bAYApv682FEZhH1iTFk5VmHvHc'
        b'Df18Tv2c5j+P/FmoLyXYHxKpu2foEK/Mv95kf4638B4I0jsvmBEKQnLjZi42W/NfO3XYc9826sa5viN+JC3QDwn6c3Yg31Ebe6IvW0mxJuowu8WSllvH7QYfYRnJDWts'
        b'3Fhk7uaJNcysS7Kkq8RmzvVqcj/r4mbmJimr+RgrlGHwqhvkJ6exIHLoOoNNEnuvNFR8XqiCfBzchSVJLdA9OKHD10eGGdKVJHIT3wvAWmK8VVPGDtN1VtBMuJvtBUtc'
        b'oCLUXYAxyexbMPdZg7PR6qtwG5bkc/bKcWe1JUYUkSbkO1ZtTkiQmE/s4/iTdDrhr2MoJL5in5sVYOeUkyzDmAizmhtLc6eqTYL7bRgQMItKhMZ1HFaTNFnfD6UkHTLR'
        b'EBugOst4D2c9UXKHXpbAlynAEsfMDCiQXI2uPIlGzKKC5VAS63qNt4Teg1nO70+iMpbKYImGQMpaSCDTDX18qdMed6xaW4CUGUpJqem7JMD7HITt2G0pqfDqqMqrC/h4'
        b'Z+yngdnilCHW9Ecx7HjV8r0f2Kt9PfrH753YevRW67fyFQvVtA+lap3zN7BVkLI9W67m1qX157oJ5cS9GrJ/k3vvXslvfr45U2Hp0M4Lgc33//6HVw4/mHrb5+DvZX5w'
        b'6a1Ap8met28cejP9O699Pf5h+HxwXPeQRXZ2Znf59KLNdPhex3fLp7+3R+FvVe/MomHqeHhDsa3MR7+M1W9vtHr36tLEVxcM9xb+ILrgr6UNP8zJdog6tuNPxdf3vxV0'
        b'6K3vzN8pHaspjvTZPPh6wLW/73vzH0Fbx382ozAb8f6Bf1bU/yLT4I1DQ6PycXYRFzs/mHljVjYlxj7imHaGgWWi/R4D5482/+OXUzPfsX71jOqew7ba76dcqbDT8smd'
        b'E/r95f3B6JtRJ8L+9pLoL49ef1lmKfPV196Ld19U7r6XqPjDvHOVQ/+oeSe/9uJfPnw7rNMks+/jMMfG/1b84e89pq7Znulf3H7c9pMfnW7tc3S+4vIbH7fXdr15y//3'
        b'xroHrn274XdKf2r6caiB5jVTtw/uXoi7KeX8fuir/r/bu9nkqnTtGxZf68n42ZW3//TLfxr8q+71kh2v6Jp/dCtVePzHW39huNU28rzP/Y5vTZrW/j3jV8ufSB/UbarH'
        b'LmMdvp5EO+Zr81EsYdjEq7zaUMcpiH4hCu7rlF0WutqOFdm8PtEP5dCl+IzdYp+LHJRYcmoeAdt8mqQiBdYYSwlYRYo4uM/pZnKJOMSF8OFIkkQnbrfjzRL9OHSRC4Ah'
        b'vWaKt1jgGBbz/dfuH4XGjWJcJ6RIh1zCEZPT/CCVOLpb0gwTHxCsuwhhQgkqOA0Vx3EJbq/2w+S6YcLCLbEIl0m/4OwIBVgKfZKuQKQ8L/BdgZygnRv9MLSYrnbwYe17'
        b'VEgVrUni64GmQA/OmtKyuABF+W0iU0LaSuyJ4+0xPVBryOr5m5srSKr5Y9FZ3hbQtT9gxRRwCFpWrQFiUqq68AFnC0iGyQiml8MjD4nFR9VabCVz0Y90qt3cyu6y9AI+'
        b'UJKoKzESU6iBGRnBVmghfRTroZJbZQ6O0E8p3wC34ZK0QEZPJEU7HeKTNsZJBcuVKJ5lBAWryifTPOdggn+qHvtgekXz5PRO6DFdUT2hlYcUuWzsM31G61SC3hN0yo+5'
        b'Wz2cetwUC+D+xrqndAiWX+DtTd30Sj1d66rah/lSMA5TF/9NcV/zP6jrPaXwKa2NVeA0vn7GJL6cxndLYKHEaV4KkmaZcpJGmmZcZyL6jZi+EUlxepcU9xz/N+tnxHoZ'
        b'sdqlCpyWtqIXqnFamRLX6YjlXfF6mwL3pw43jwb3Z9bWp/Mi1uxHoqrJ8EqS66rixPSTNbqZ2v/2+RpLrZls3+qMnILmxVQTkh1TPNg5fzkFjVS0/c9X0T7rJFbiyA6w'
        b'ZVmKNlDPmDjLibJeAi5OXJoUMr43gIhT0cRMSYtSWlXIpL6UQuawUeDtikL2pEHAahwtF377vxw9zr+zUv6Gf2+DwpcW+o586A23lOeEFHHB5kxro0ddfb2PWO8/wLSk'
        b'hNBUFjiSkpocmxj93CXwdXeehNE8XW6Q//6FUlvk+NSWbDWckwiMsAjzny+vWgQ78U7kRXjouerexnws4Cs+7YY6PnShAuduPSkodQ7GOQ93ApZxr6cYnF/rPseZOCHv'
        b'Pt/tHFv0xg+FKbn0UJCjg3nJmDLs1zr1xwf37R9GC76mW7QnRKDg7mKsZtmV0jxjMz16+CWXvrd/9kHb2zW+I6Gn3lVKcNJyf/RXuxxdj38J39Cp8U6I1hQbfs3dfvxn'
        b'387c/lKmv2Hcg81Jb5a8saRVOnBll5SHTvA/JpLiX/IfXLqy4P6HyAvvDetuP5HksetnvzlkLM3LAw+OQZOkwAAOinn7+gje5viRnMmJNXkzelDIxcxeIk7Dcezyw1j0'
        b'RNh4rP/ETxLsy9fZnhNA91OGdNLwxjj2eQMa+RUsk1jfLLHSR+OgCDqEfjlQuC4r5t/iJGsIvUoah23rSL3Xi5D6W4ItKxk0fF/kFXLPiHvWtqeI0PpZ1xPk9RRpDUH+'
        b'coW5idpy7x9YT3I5ast8uddfmNoWGzyf2n72RlkV2qzYq8ye8x+pRLlSGa/v2aDX5PCY2HRJBSJJId11NY82IKeOvLkk/jpnX4lNuBofySxEkRE7n0t6JZt7uu4O/fqL'
        b'9GcRbEi8pLzS2M1hHYzr8V00/TAPWjeMrmJaQNgmudhL+2MNfYNEXOfiLR9Gs/TzgK+8/tXJyjGXjrvG0t/QCI+Jig8zC02MignzkGQa97YWzcqVa1oZS3EycMq+MEkG'
        b'XSHMSvxsnXwA+iUcxYZ1ake8PrTDw2iODNhH4/gKFcCy42u8pWpYncq2YoePSVeYYCRgDMtYM0zeHuTqeY1XFaxhRuAOA7IwSlJ1yef2iVML5W93BcxSODQ+8mJobMOQ'
        b'eLX+56ph96kZ1heFP7seUdeXvHzyBId7zAjbpLRCZr4s7uUKfvcZ2bCft2pWbULay+uck5exyIv/X+1zauc9qbzBEni5zD0uKYoLtufs6pzsxpEUbm/8wWz+T8vqX5DA'
        b'J1vTRxVFSZ0AOZGUooJQZ8fTZfDU1NREckItVTmhigJ9v0VOKPOpFDvYT/fe1BBaJGoI9XfI8Y29jjjIrCaLQ9nh1XxxkcDIUDoda3E07U805Y09x+A+VB9Pwpb9akyF'
        b'wnntw9aQG44jMrZYBFVQLUfq3328s0OZ9M58eAiDUHPqFHQoQjWUCLeS8vsYl5ShyRYn4R6Mh8IU9p1TZpmkeThy/BgswagLLDnTUxVYcp1U2z4YtLgBnR4wfOwGLmKv'
        b'LI6S/t8Pc4egGzqxJ/qa5R5sOoC52J4IbXiX9MhxbLlxHEpJFy6GsU3O145560DpLsx1zImzwnKSeh7HHsOCK85bdoRucbJ1lw60zLbwhs5APXOowaljMIu9MAGVidDP'
        b'mk3AtAtM2ySYYIVlMJYpY08EjmqSUPQQqrGDfuaxPsQRm89YxUF5OA7JQBtMY0EScfsqbPPFIRjNSMAuWMqBeWw4B1WbseNKEOnCXYe1cdgF5vdDGe29Cu6pn4IRX8gz'
        b'dKcFTGPzERjJwYGz0CTEHmjGO1hLem0zVsTAI2yGjoztYkWohUl8YGmGnTgdc0ThGE5BYbge5DonwN0IGrbBExaMw52SdjjhvVhcwhY3rAvUhaFMB5yBcbqm0eMy0HjW'
        b'2I9F9UId5CvsPYcTutiOHfSvx54shiyADqMOGszw8RG7Pcd3a2ni+Hn6RWu2YZApNmG/miZzn8PUuRT6bZWKggEu0xv9OEbi1RSM+m8XYINV5FFsuggtlrCggQ9Uwjzh'
        b'XnSqHeb6YMN2KA22liPhaEZPE2biYXkrFETTAINXSV9vPKCHHREG5y8c34c1BAkz0JMSSkBXj83nlDZfzEo8mo2Tepe2QbMXdGwOIpmrFRrwkRxtZ5Igqhk77LFMDgpP'
        b'4xwzY9bDgA0LG6EVPoa8ALqDCvMTBBAlmTC+aSuW0AnN40OVm2JcwGLn3ZpQnlZKQL/JGObgvo8D3COoV2J1irVv2NP19p6G3O3Qio3mSgdZbjVtuU18GnrCQ3cZQ2WM'
        b'FJTq39oH3UfSsmJUieAXQwc+oqMtuxriD4vaAdBsD80wBl2QF4qtJthguhdncA4ei2FUHmu34nSo9FW8D5N+gRknsCXHNx4GsIXOYdGINkEAgkOJ7kdpiDY9aMHbZwJo'
        b'7OoAaDgMjVAYRph3W2TjidUwak7PjOMj6M8JytFUC7gVdtA5GlvVrx9UxyFkZtmHBH+LcOcQYVWx8w6P3df3EqxVQBMOHiAYHyDYnMGiUKyOhwXa02mch2JZ7LbD6mx4'
        b'kObuEItDhlhoRJrG8o3DFreg4LK8L8zobmeV2rBX/YhUEi6H4LgIKzN1Qk/jXZhQgLKbLtCIt/Wc4V4g5GJ+hCo8gEfevn6W4Rp7N2Ofg7OClobFfumtVn6EQfc9sMiX'
        b'brcR+3WhiEhKbij2WNM1zsMdzBdjtRdU4VjKJn1s9cKSAOyHCSl1gr6STdBBG2F0KT/Ykp0tFOEgTGZkboby7TTjEIHUo0yChsIsdTnCh4koInWzNyy1oIZO8S7dzijR'
        b'rSm5aBU3fLAZhvHhhfM4QGiXj493XIJF0p6WoVd+N1SnEEXogQKbSJxIwOIAWLTYwqyEF73h8VaCuAEs94Fqdzf1ixk4RfP1ECi0BcFtwqBl2thtSxzQNPTdre3NcoZx'
        b'KhC74+nwHnnDuDHOSENj2G5ox97otNdErKVdZBbB43GoYPBIq541hck0G2y9KEWjPsS7iaHw8JoioWXDoTNm0KMW4g59dlCG03RaC9iwleBoCUpoY+Mw4goFQYSt+Qa4'
        b'6GJndxwb3aAzQk2BlMFi0mnaaal3d0GzfjoBcIPIDhauC6wtXLHmSqopXdsE9JC4VAJzhDfVhHAtYUGXEol2dJhhSxwd9jwLCy0hSO2HTqjH2ouniSYum27yT710mVRP'
        b'WmEXVhKqlsKCEWFH1QkDy0ws05KH2bUwSxhSf2YzrWUqA/PM5W/BZCJHMmtVrkMT0coeBw/rrJ3hMOqVfUNHfNkZSjfB7Sja3DIN0EO0Kc/ajiC4UTYByqE3GGqU6ZL7'
        b'9JWh5gg2ucDDVHrkNrLdPMA2Ykq9kKsqwrzjtLBubVl4fATndPcSOIzDnCUuaWVgZ6L2damYeMyFOsLYAqxVpcPqoi324AJMnKH77FDHksBtMQRteThmD1107AsXDYk1'
        b'DQdm6hH8ticcx8oQYmANxtCXQShRZkHX0eFgSUSumOCSGOfFg1cOYZVRHD7KOamSRQvMg1yC5Q6YOKBvFBEKE0RwHitpYQ0p/3lKWOQEbZbnCCag/TotoBgrjGCKpNcB'
        b'qMjCDtmtu+mg57HLKXAfLGGrgpMJbbiAKORD4totp2DCOdqHLnMC7qQE0pU2ET98APNZWJoOjZdkI7H+eJSzBcfRK9xTid0UpBFVqKRn6o85bwrABmi5AiWidF1oJfim'
        b'EyT4hrYLcbTKZXwg3pPk5oTFicpYFekvu+0yDm2BBgZd+wijO5zUCUHn034o4lp2LdIOidYmcgLGAo6Y4rTw9PYQeCiLTT4KQhhjscn3CG0aoTIVxgVEb3drY+4BOuFG'
        b'vWwcliVa3RXpbATNjjCgSdygeTOrXKGCrbIJenEENc2qhI6Nlsa45GfhAi1ns7FWD8rcth8mRvBYgQ5nCUtlz0BfCEOYUOHVi0wWup+IIzh/yZ8IBqPAg0QJSAJJsoYW'
        b'TXtTHw0cCYSqkFNw5zTMqeFD51tBrLPZ4WxNKPP1CIS+PTh5a5tjCFGOfrqQgQQ6lgFoCbouxHonK5g9tz9bxRFvQws02oUTZ75DZ9Chq07HXYBdYlhWx2q/TWpbiPGV'
        b'aEHlJY/Qc4S9i1ZnbeMJj2sCoMYC8jy09mnho3gYtCf8K4qD2r14x1GIudJnYC7iJNQ5xcKEnRfMQ9FJG8fTN7dgEwE/0cVumq9QkEA8oAPHZOAhYUGxDmHLOB1VBbZa'
        b'wiKUbSZEbd0D8zk4fc2OgLaRON09rD92DTsciKjkRpzNhALnJEKAhzlQn6NNYDUVcR37onWxkYhgO1GKkqNY7q9ujQTvldjlTIIRQXS3/mGWHUOfOu0PZzqrEVc8tQUm'
        b'fAkMH8Pk9YOE8ovY74hldGz5RCQeHN7OBLJkKIvSN2SgiFVaJzhS0EHLzIW2WKgPU89K98RWYGTlLkFZdSytpm8bYVQN5ongXhqdfdlmlqXRQjx0gFhnSgC0W2Abdul6'
        b'K/sSKPbG6WB7JNa50hX34PxFuB9Cqxy2I0WxC4ts4C4yRF/Eej8aovByTDrjQ3g7YTNOXCUCM475u50uKODo1gNOZ7cFhaRVMwMsrfI2wTVtYlWIMMUZYQLeIyHi+BFT'
        b'eLwfRtMVDW1kk0mEbXQ6j9UnaTPw0IH11KSJJ5LpmKYZDQowgAIrzDsQCvdp5hIYvZp9XGm7OyziSBg+wOktRCmGab8Nt3ZArul5uvIZqSNEC+th1sT6BA5cIjmtDmcj'
        b'Sca8R5ysn9j0FBJly7tljrUaBLhFJy/BQzes97En/loZaQ9NfiYkeHTBvC1NeI9EkoewoEoIfh/a1bDPBe4dyMRqFc8d0QlE7m7LEoq0ZSsEw+ge21MeuseVCcoGoU7F'
        b'fJsUndp9BQ0bnNyxV07shHd20kHm7iHI71bfSmz+Ho05dBHzLkGtAxBxsiNWSPSJxAScC8ZWbDt6jWhWHfQSnegiWX+U7kl4xvw8lO5JJFbdAoPemHcBOy7aQomHmSed'
        b'XB4UO8Zt9XY+ywSZkks3oSfMGO+EQ65mtj42EM+qCsLpZAKf+rM4EIJF5vuhQcS6XXtgoQNB2DIR9qHoS6SVVBLxLt6sS6c8GYI1R7EQHiQdodN/ZAkFdgQ1XVh1IFAr'
        b'ytrGOwy6QnAm6SJR5odHVRX2WB3W2mxlTGR9UgmLNU95GRJHXN4DrX40arUygdZSApT4nCc0mbsID/dCj1YEjiXShC20zfuXCRm6gyK1if5Uw5AFjCjSYZZgQzQU74Dx'
        b'S1cvbzoB/fH00BA0RRGFaBLH0apyfbEPJq2g4jgsGhLPncW7t7RwSRCPLaYkPY/hfNrrBJZeOH2eQeXtRA4oFwkoM3EgEh9dlyPBJ08zmw7w9t5tJONO6u3XwBo1Eib9'
        b'fbJcoPLWjj3ZaVAQqnsmWMmHuHgn+4G8Q0T864mS0GvHmeB0Q00ZBjPpYufwwfkTisQtp2FZNQS7sSmOuG2vNOamYd25SFjMTqSvWsIukTgzzEkQQBLEPCzGEvRPhOli'
        b'fvIO7DYiqOgg3Bk4l4hVN/SJPrQygTeGFlB02TZBV5HeqCLaUU+nUeoZSKJef45vjn8M6TFFmQZKXkhyayd2GxD57r1ol6nC7LHAsLcSZhKv2mnAtGoq4cntZJIqKgO8'
        b'rOR342iYF6ua5EuPTMNdWexXjsSis6zbK/268Co0q5KychfaMnE8mIB1dJ+SqRsRqaZYNae463Y0ccc2wtMR1tl2q5EUnWfdfpI5KzdpQW2i/o7ThLCD23DWmahXOWko'
        b'k8SV5xJZ1D9WX9uDPbtIw+3HuznQbGRORHBGllXMxR4r50irzJ0XowjPbxM+5KURKjQrQPUBvHfFCls89hA2TGiqp4QREVzA/gvYf4kQp2sn6whxmHVWt4JCnLmaCJ2p'
        b'pIYXkbq8aT/LqmlgYdkTR3fRsitjoJzkBml85Ef8sohgtcbuCk75bWZez1ociaR57xO8NQt2ZRy/eiFF5wzd8ZiBCSHMfaiKSIVWu0wo2YXF0hexNA6ajtGz4zBJomcD'
        b'Fp8nVlFKwkmrlocKPHDbe8ubYHQQh7MC40lgbPC1O32YaWcDNtDtkGxyER4TWFV4wlh2rFYUkaAmVQLxSXPsPHvDGWucTAgqhjcZ4O19HnF+eG8btBjLcMErfsFe7q7S'
        b'AuE+AQ12F0u8sZevWTePyxfcJYlLvnTEtcT0W/kkonJoSXA3FQmE9oItcth0lS/6vNNRiSUgCE8IbB1J9uihI+dKIY8e4hSoUqFA6CbwtsMWf6jm4rP2EHVtwlIzIQvQ'
        b'UjqMbTuhK81ZLBCcPh5FB1SD5YQUzfZKdN4jNxV2BMlD/VEf1VBN4klVFgQGHXRCdUxg34t3XZ08oSDOTseYyMxj7N6cRYypHdpc1RyCiHJXQmsYVpCwQtiLD6yZvYU0'
        b'76pMizRH6NdhMl4OdEeGYqEitCeHEsrUwLId5PqfxTovukP6nhAx/zR97IJeAdHWQj8NEuBa9tFV3be8sJsg7vY2UgfGTAJp3AqBN82ZH0nkdIT4bw3dMSk4sTegwIIY'
        b'a9U5qNxLmsI4QcIFEl6q9hJ5G4JqG9KS8lODPWHJnUVuEIMoJYAa12MHSVpZkY3xDSi0IsltjijEKHGChzC6k0ThR9B0JPJIuhgrZCNVsdHlCvRZ40yy6Q6cvYwDF1y1'
        b'oU/2RlqkZ3IwUc8q6JJnNgNo1NuMt+lgB4gQ3SbK2HPxAo1VRudZH6jFgrVmaQmVh2irPce3KPgrYVt4CKd2NYsxz5LUmFw6lSEkGrpsCWViHA008bbE/AAiaO1HcXQv'
        b'IUyvFWsdW0JEtvIoCUMVtJ/c5E1pUsSUKlNoD12weCqIgKoGSkygTRYHY7HSBepO4EM/0qjKSG1ZlNXG0pCd4caOW3FQDupCoC6ZEGTRWCUN+8KTk7GHfqpzlGm5xdbn'
        b'A0iBHCIyXGWF447ON9SjImDKSBmmVfCBCyHUncM4tM+VcLoPCpDZdYpVSXufhNtboDWYdMIBogFQf8LlgldQsv+FTSQRFREXn910BGuT91kRkRhPFxNt6IZBcx1YTovB'
        b'gcOkDFSaaGLzJkbGidsV7r9FGDp1iMTFYmaNMvaKIm4Kj/dBSyoBVSE8DoLCRGLgXdB/itBtyP0WDAWT0tdG1zrkZsuZXxbExGMeBEWTMtUNFYc3bb1pSoLnpBfTI7Aq'
        b'ivCyYz9DTlzU14H6yBSzVF3C2wE7nLmsjLeVcUEIbZdJuL4TnNbH1AUiJ0lPW2aIgg7b6durpuOgjsyWDGyPIOy4HUY0eexMEJa4aek4kOKyDA3JdJ4FilrSF4I9fIjq'
        b'VFptIdiph5HN2HNA133nMZjIJm2gMEDX2zzcQZZY2szZ85yJZtx7B03SDDXWdCILCrSD8UQiSB1Me4nB6TSYNoYRKD1mSrjRg62J9I+K9IPQTCyNKHslg9VOGDOB4f1J'
        b'JOq32eJ4RBCdcoHn+U1M0EQi0d3+QhL3Fgirb+sRAo05E4drk9LDXlMiuhPYqXkeHhkQRb0HLfbJHiRlt0WT4JlnzwjrGNzOiSfxfqs9yQmdm1WZXcsDe7M0HBWgP+ES'
        b'0eAy3g6QEk4oUHllD6vtQ7DTfpNIwawek1NJxYVez8uCOCw8Gc9iWS+fjCaeMIGtkbTC6lRiwnn0Bsuevh8eASPxZw7j5CY1WNp1gSChUQu7HSzYiZhg36ZInI0loGFS'
        b'fj9pDgvJrsT9Fy9LH1PDpq0HsNr7KpG1Mk3s0CAFrCabBKlcWL5Gws7kCehT9zY6YbWbOO9DrAuUw3bnJDr3FiPDtO3GsTpnnDXU8aHmrTRbZSg4KfIiuO8nACyGnptE'
        b'DNrTzrtAaRCR2jumMKMVSai5QLgxneOfQIwyEe6JSQwapxvMh9nQdCK4rcdvBGB3oDlRpmYcMIb5k5dhaMceVyIMNeyOuTSsOqLqwzCkTjtZxOWbZzxo0K5DUJ2g7exN'
        b'c89tZYFnjjDjQFS4MFja4EQqkcFRzmyjhL2pcN8XS1d1W3+avRwaDu5g6m2gj6IQpjSwyAtGZMxhOQKGgmR0oA+JEk4Sm4ERm/OkHZdYxNoQlFZxlpN+A3MiZsxS16Ru'
        b'BvlE2whMC2CU1ANcyvA2N6ZLG8AFOwfo04MmVb0tdAVlMBlBCNt54pgA+jYTeenfA002mLuTSN44DAbgAz9osQwk6lPoCq0Rgawc/3kmn3Rge2CyobQ45hjW78PuTCy2'
        b'gPFd5zAvcT90xZ0k5tBFm+4lwbXViegOzHpgiVkgsY8WE8Lou+Y7/WOw+7D2hWRc8iKQqycGkn9QSw4exCXCKBGxNpph1EuWMGH5qjcp7lUENWXQlUWbJpa1BXv2QV0a'
        b'nWaDVxzBFOktDWbKiZCvoG+LQzax2OimkwAL0JeGLTYw55CMDXR2FTh6fjssnxMcwbvKcrgsplUWeGrDrDSzjnTaQE+0jgvUn966xYbUrhKWcjh0lJmjCCpGCBMeEygs'
        b'XiMFdFCTDr0pLJxhT1SMEVGectFFh+hrSjAVhD1x3l6xUZdJUh1XoSU0E9MdUMBxdygNh4bzppuAVIw7WB6nFIqD56BC0z7kUja2uXluO4BV+3FsW8xFvGclYpIr0aF8'
        b'UqQf4IJH5g3afWmYGjGwdlzaLrUH6jV9sCA8wPnySU8nwvKy41iXciQCZw2IJg3TlZaSbigTTARiUDFQjyMyjHDX0kE2hh+EMZwyMCbsbcTO64Rx92DUiJULVZclHtl/'
        b'NUCbZRBG4OKZa3Q35UgiQqU8TGsctSCq1nZd85aqIaFXE5GcJTMsCoa2wwmElT030uxJpjE8rLwOsEm1nRaLNhHjqbJXTYYuLZk4Q6K592krY0QR6w8I3c65Mt0pHGfC'
        b'cUKZ8GqKdt5udlQFK/UubJMi8G4mBl5GAvxgFp113cFz8n4wbI3NAQTZzUS45xSZOg4Den502KRUwz0dzPd1YrKPJg02FLwDui1x6LQJkkDjto3Op9QAHljsIPSsOwYt'
        b'2nQwLSnEdHojYSxAj2C8WeRzcCt0braB3DAo3kdy73Gihzv8jLcSmaiOwTx5GItMvkV8Kw8mA62Jp0xEMiJeKpt6xgr6lA7DmLwiwVuTbjAd0qwGdkRr47CcUZbDsWub'
        b'4P5hGPG4QUDVTayvC5s243SqG/ZpkLBTQVx0Poa4QZaCYzLdYRsNUm1wJBW6jkodwKETu+GRnQK2puKgWtQlXehRV7sGNdpY5h5NA92GWjNZS0+6T5I16GBmpPQ9r9of'
        b'9onDYQOiC32EQq0hBrjsRMSrAe67OhxnUdwlrIcbHeICUdlpxSgsPETsmSC01BFGt8gLiRA8Dr5IZK+bLmWGRs1X1/YnLl4OnXJwNwYKbLDPnFhA0c10qD5yEZmZvEMA'
        b'E5ePbiVyMgcFsYaEZr260G5OON5EGDFKKnVriPzmQzi/CRrOHXG/6kwc9BE8wiEpeuUOTOhr2ZC+0Qk9DtAvrUeY1ArLe7Q3kzRbboKVN7CSHU1xBoyLr+49Sr+tOgYd'
        b'hv44S6wS69V3H9uNbUegMTKAS5WsTybWtJgZhCMHj/lBXnwqUcVaC4E19IRmaoWF0anHx+A8lIfB6DWSn6tIgiun0xqzJaKav9uG9MFZLEy2dY86TkSgCEuyzelwx5WE'
        b'BHv9Skw2potsikjJzIEZb/pnJzR7sNZ4MHLVBYf9OcY4ifPHguygwYiYJum+zsdx0o0kuBHFiAMkjTUGEm4sy4aRvJZrcN0/TUhIZHBJmiHRbYJlhkWLOG9KNLiRQHPa'
        b'Bid1SdINwBqFWEcY2I0tjvugSkys7aEye+K4WiwpMQvZ0S4uJArkufnZ6GNBVhJJ14vY60BXPw4P5HHBWjaeGM6AENt9cW5PDuSSxle310lV0RfrIziv2hCz8t/KhlqY'
        b'Y6asTpj1of0RjvQwIxGJud3Q46KDTdd9DC/so53VYf8xvH0L7+GUHrHFoovwwI8ErSlzmZgkS10YdVEgpB+kB8st6VAL4lmKtCo+vAT5JA2MEk+5dwArt8rSHrvlzXH4'
        b'RgwJfwVhmXD3OPHje/BQjOO68thyXtdJl2Bl0EhabRvOnPCDShV7OSKXc5jrTKLMACNmh3BYQJy7Div2q0Segfwgd6MjqXEKuKjmn2VIlJ1kcruEM1BxFWssfUmVZhLo'
        b'hE3MDQKNYkPa2wCMqtu6E5Vs3wRzCjAdcD3eBB/tIbL1GFsg/zLOZSpgwWlfQot80kseEdGpIp1lJx14w3a8r6QgjtqEpRfiYi8FW2Gzu4rwtA69NwRVMlCtvonQrQYe'
        b'xym5mu7DaVYTqZt4di4sbIHHzHnXq7eNdL6ysBPHSX5vO0jn0Q7D28wTocpjFyHFPVJ9UtKg6SDdQ4ErTh1TJOl9nkSC1tNZm7BD6aY07aLaCZo15W8QvlXTv6pg2TQx'
        b'5DqQ3jmNeRpHvGFKF1rVDh9XysA7bpivFyyLveegOgbaaOs1eM8nkJlLSUFmti66+3mivaPEIPKwywKLbgbvJA5NAtB5eva+F23mjj9OZ1mwvKNuwpYaYtJFioFhaRcI'
        b'Hx8AYyQkj3ZZ096Wc6B2O1ZHksg9dY0gZihDlwBrIAcLb0Ex0XESOu4EQIPrnrSfM5G+6yJB6woe2DObVIU/iwKHhrgT+j6qu7GScMB/dzZ93bqZkHg0OlxeF7s2H9lN'
        b'l7yMw9EwKOsSQvNMk3zULbLG6a2wjL2H4xRpU/n4MBWYA/j2hWNQLQX1ukTNFzKwyR06xPSxB+Yiid08ukmksYLZBeg6qhS2Y6cbkdIBOv0yrL6ByzB/TAuLrWHeHDt2'
        b'e2JpPHN1sdjLiYgzdD75e4moFCtJYX/kFoL+yev6hOezB7yTCOy6NC1pbdX7dbB+1w5jbNl7msQFwhBHgodFrRicUsLmozuxW5lUx/yLkOeIs/YwIJ9J9KWGZJ86os2d'
        b'AgL8ORm4r+cCDYqkInTvV4V2hwPQZMVSKnTPaeOjXQdlZLDorCMWK+IdxzOkFs9bkHhVaINjqldxap+SuyV0WGGNg609HcoENEsR7ncRsS/ICtFXYylhs0QOZuG2PkH7'
        b'kJCEslvpBwjganwgX5GDi1nSK2H5yl4iCq1YmESn1sOIwdR+EjxqomKg8whBNDPB12DJJpywJr2mKhqKZKAjRh8eScGInS1OMwUdc88SDZv0yCCGvmQlQ2J1J5QZYZ4Z'
        b'HcyIDnTkQIM6AWaRAXMmS9+QsY4+RyPXHlPBepIdZDKY/JOneSiR1D0S5+8QnaiCHk1sOrUpk4VV+NLJNcPc5fQ90G/Osig6jaWhaSfJVi0B0HeFVJ4h6DQPJumHuLa1'
        b'bdJBmHMzvIYde6DRDXpM95/GCWliKQ2uO0mpvY/jB4jB9TEkafLVOGVF0vWABS777Sby1uATohKcc25LIAFOEeYe8qA5Gncd32GfIyDZsugKAUE1dBiLOBNUMtw/zcrx'
        b'sGI8hIL3WEGe3Umc1SrzwCVJxThmYBPA4+sHjcXcN7p4W92dmZSOCLBgB62nNZu3Zy3Dw3R3Vo5CuF+AtacJXx7gDF9KbuEstrDMKymB0FHgxco0eeIin9p1Hxb2S+xj'
        b'J8NIHJs5QYtj1i53nNN1ZxVyLQXuFxjtjOJecMRFWSz1oBdsBNhsjxWX0vjsv+Hr2LdiToMpQ6zFaiNJ4whXzLuEpcb0jjdLtCMFH3rP8xmMS+HGWOrJGdUwj/V5bgrm'
        b'vtA7ZiExwBHpnWUSKxQbC7mFxR8gqdqNBjMVpMMsFkVKFkBqMpdQwtvhjK2xRW6nsdCJ60LEpb8d2MsVkhPstx5O6dxxRmAs5rMPs0X8r9NvCc8eP8DXIYqSk/xyr/Xl'
        b'r9zKFrCAMiduNC5fLjb4rePSKaNEq/ZHeuXU+HtvddDKj8649DtrmXBxe4bHHxcz5ORdc7Xk3Z237nExeslbfSHi7AeJbR+KPx6zOXq5qbHwGx9m/dHmby02vp/M//Pl'
        b'uqO/TLeRKbvy3j/zP1Wx6gwImrMz+5Hc35uzi0Y7/6nQ/8NNrsanfqAwdig4/J2pj/7QH6L/ge6J8pS0H0QYffrL7doe544UjFzubykZC5EaUaxrS9bu//5/DaQ6nwj6'
        b'u9qDn9+4+50Yu73Hk8NaHjm9mvPKla9v7etKjg965PgLuw/2XPt2lpPOo4+rdp/17naqHRn1ar/tcembSaea0+6knfyn5zdGh1+Srst6o7f6tJVzDOypaz14VrFdeuiH'
        b'Pg9qG3pszWKbHm7/utVk1fA7fmE+O/Tfunfvn7q2PxW//KFHhuPR0KxFS/1DPs7Whq6bG1zfbarze6NOfPS2V2rV75M9Xv4T8aBLu6NdS1Ndor/ybkRZik6fTWB1QnV2'
        b'usZbv935xi9rIoYq/mtAITPPKshnT80rb5TapX8kfenaH17+1/caZ3aI/1vmv3+q3XylSvcthW9f7P7N8K8va6f0Nn5yIN9r36vHWsxkDnztbIHeD0p/57fV9tbAqTuf'
        b'YLe2R2zWpQnDdAX8RtUrswdeDrvjsnnbv3Yk/DhcqjPCWWy95f3He3a++0ezX++orRr/4ZXx7r/LlIW2fjJzOdvlzU+slGwP/8Fo7/5v/uDVnw1N/uB3NTebeqy8oxV+'
        b'sKD6WqbzYvPhFJmJwa15cSp/+dV45neyXM7PvKwY0PWO2uCrn0T77fr+N/5+/pPFyYGxu5HvBv7oOjj8zerduH1vtf/C5mBl1rHiyFejd5se1duTpz2YXOt3q/Zo/qHB'
        b'cHHL62Cdvt3g9Ze2//VarqPe7/7x8VdfefnaQrfdJ3NWV+Gd9+8HFr2z5ZOXT3zn0S9+MjTb9T93l37088lXbv35azvwW5afvl98q8Q/8n/eM/yfTTfDz0SbJH4qvSXo'
        b'bHXCW8YKfMmWAmtijaUeHB0xIL5zD3qyuGwpL8h3eTarjmSNe3LpMM/nwA3jgs2THLgdmLs2DY6QcDKbe+4Y8fgOxWRleWXi76WqyWlKpDCUElN+LBboZUnJXYMCvoBI'
        b'M/12aPXBjL0ZOJ1xTVlGoGsvhmHSOVNZ4bnz53E+BQci0pWupeFjVSiBMlU5ZQUcVU2XFhirSJFYOwbDqeaM4LhiVYrkOZqufe2zUL4yuqeUDMwGu3AFP7SIPzxUXB1O'
        b'jsj2EvaK9hG1LufaE1lig1QKlMtdoyWmnIwmVle8wYg4JQNLcdjLLRimlEmXWCnyIoMP19V54Yu87Dr9bB87q/+z8aX/x/8w1uNo7P8tf/AdyIOD45NCI4KDufDr7zK2'
        b'YSoSiYQHhds/FYlY0pqGSE4sJZQTy4j+v+KuPTaKIozv6x59HdejYKlQrVVse20BKwiCJpVSrddrEcEqCus99tqVu71ldw9bBWmtktCjgqDBGkWo2iqCtooKSlFnVDTE'
        b'+IiKjkZBA/EtGiRR42O+2bYYE//QmJDN/W5vd3Zv55vZne/bzO/30UX0OHw+X4a30OvyOn2ZeWMlIa8u/yxafjVXBdInM2E6tigJsF64mp6Lzz+nBrbJAj/HnqwdEfgL'
        b'4btpdIsz/5qCaq/oEX1egS9fzRULfI29p1goE0rpx0+xndshsdJCOdsCSzvXJ8EE61+do3LmwN7I/8vHWDg6wVk0DkHFT076Pu/Ud4pT1hl52xhswjWYCMQoTXhkcAf1'
        b'f06+BU9S75wi+ly7nzo16/F6yJeG1qL1Ls4zQZyEdmvqp0Myb+YDb/3YuundsxrEau+8x5o/jb95NJHtLDp7Bh8bd2Ca2/uze6N2aUO8es3xJc9OPe2ziRM7t8TmO77f'
        b'vPS37xa/e/aXnZ+oxePf33yodVLyG/LOh76FF7x/+I5tB3q27d/TV7HqyFNPCCcWvnb7nlT0ofCKRajho2/16AdHXh7YvwrfFQg2xcqaFzj++O3I6wt+mnX+hwfbXuzY'
        b'+l787q8u2jB3erjoi56jd89N//DjtfOrjl6UWNqivVEwe/yxqSf6nz6ePL6kxD/98LvWWXsefmbPRyf6PxZD7UVS7cDUNd2ZY2fq017xrDj80v5C4Zvil3nP8tvc+2dW'
        b'r5P6Z+JZlW+9NO653a/maG/P7cq+8bUrDhWOaa1Z+/vXyqSDrze/eILc0nvs29N69euqD3SXnmGrW6VpEACvL7aDC9vYyJi5Li4LPSngR/KdrEwWfjAcaKwAlnZjI0xY'
        b'z6VObg/eJtJgaBC/YGtZbcTdpbRBem+G9gAZAXjhQ9vDJxZSb72dMUNO5/GGFWg75HAJujinJLjpsHKPNSw5TFsRp6dQb/VKrpLDD064nlGiedQxyY/vKAFy8To+F23l'
        b'MioFNqvucZvjPkTjTDZU4k21IHTWwKOBZLXNYm+HKXkBGiBtriuvq7B1xDgP7hIbcI/KDj+XnqovUFdOw43BUfm2F0pZvVfijjZ7EA7W0drVSZwPb4qiQZFGh7tQu81E'
        b'35GZG7i8vGF6FY8euYFz4Y2CEz+B0iNM9E343sB5VaDwZkthjClC21CnOFvOY7VbEK6E3XVBe68HP4624B5xGtoXsCltvXjIjdOQpe++CKTpk67g0fOLDVuEa+0cGral'
        b'cXewqayc46RpPI2Fe2wSDg1u035/Be6eHQNdwASPdqPnJ9q87o5L8FY/yOPVw78GqWkk7vRVuA8PSejWNvycrfPWAzH7Pnr5cHHUBtT6XFapQC36WI3ddXaifjRIbbzX'
        b'/EuRzDqBRq+7h3NWLYVXc1n4yTH4aROtxc/qeNdy6qy0aTk0CimWXHR0t1tqCG9B6dloB+Mp+eF8oM98r4B7Y+hh2xQbUH89E3l+QD0pd3flZKb4dn4T6gygnSW0kbsC'
        b'3HjIIdQIlUPdUxoqSp3cpfNcK4vw3hGbbsf9WXgA7wJt8DszYBJtX+YMZjejoLVNh2nVwfpGB+dYyVMn467JzG5LQox7BLSjKWXDfCOuIEUt3SGhNROQLUJIY6ku9Ci1'
        b'fBeoKtYLaF8plzFZQOkUvQlYhx1Au2rRA4v8l1eUBysqeS57nJiZCDCTetBefGeAtk2gkh5NbyR66WOrqKO3UcRbvCLrMnhw5S2480L/ZeVlQAuFVsEbgN3xaDUTm1uO'
        b'Owr8EMEFOHcuvucMvHMkPVLJqX/g/0/DxvhT4KWcTGmsw/jkcTNGvZsteUyJzT1M2gQeGLgesOYbTmFMS4rav+eUjSxTbWIVcyDKiBhXNEOlgxtxWCk9rhAprpoWkaJq'
        b'hGJSVzQimpZBHOE2SzGJFE4m40RUNYs4YtTRol9GSGtWiEPV9JRFxEiLQcSkESXOmBq3FPojEdKJeJOqE0fIjKgqEVuUVlqEnj5TNVXNtEJaRCFOPRWOqxGSPc8mOAZD'
        b'y+jB2bqhWJYaa5NbE3Hirk9GltWq9CIzwlUzFA10rUiOaiZlS00o9EQJnUi182tqSY4eMkxFpruA/k1yE8norAvstCByVG1WLeIKRSKKbpkkh1VMtpLUb9SaiXh1sJ5k'
        b'mS1qzJIVw0gaJCelRVpCqqZEZaU1QjJk2VSoqWSZeLSknAzHUmaEpXMiGSM/aHVSGghbnXTNbHuXGMvAedMBEgApgFYA4AsakPTG0ACuA7gWwAIIAVzNWLQASwGaAa4H'
        b'WAKgAiQBFgE0AUQB4K+NNoCbGI8O4BqAMMBygDjADQDgNxsrABYDXMXODFS7G2HtZiakN0ojhI6UMepm/bz4H90sVvIXd4z2GyXSUkm8sjy8Puyt/1Iw/PtMPRRZBhpn'
        b'QHeFfUq0odTNCIHEJcuheFyW7Q7MKIOQNo447UyuxuewZdWId/y3DNHEPYf2glRcuRgyzZmQdFUCt+G/30iL8piw4Z8EZNXo'
    ))))

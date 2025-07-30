
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
IBAN module of the Python Fintech package.

This module defines functions to check and create IBANs.
"""

__all__ = ['check_iban', 'create_iban', 'check_bic', 'get_bic', 'parse_iban', 'get_bankname']

def check_iban(iban, bic=None, country=None, sepa=False):
    """
    Checks an IBAN for validity.

    If the *kontocheck* package is available, for German IBANs the
    bank code and the checksum of the account number are checked as
    well.

    :param iban: The IBAN to be checked.
    :param bic: If given, IBAN and BIC are checked in the
        context of each other.
    :param country: If given, the IBAN is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param sepa: If *sepa* evaluates to ``True``, the IBAN is
        checked to be valid in the Single Euro Payments Area.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def create_iban(bankcode, account, bic=False):
    """
    Creates an IBAN from a German bank code and account number.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.

    :param bankcode: The German bank code.
    :param account: The account number.
    :param bic: Flag if the corresponding BIC should be returned as well.
    :returns: Either the IBAN or a 2-tuple in the form of (IBAN, BIC).
    """
    ...


def check_bic(bic, country=None, scl=False):
    """
    Checks a BIC for validity.

    :param bic: The BIC to be checked.
    :param country: If given, the BIC is checked in the
        context of this country. Must be an ISO-3166 ALPHA 2
        code.
    :param scl: If set to ``True``, the BIC is checked for occurrence
        in the SEPA Clearing Directory, published by the German Central
        Bank. If set to a value of *SCT*, *SDD*, *COR1*, or *B2B*, *SCC*,
        the BIC is also checked to be valid for this payment order type.
        The *kontocheck* package is required for this option.
        Otherwise a *RuntimeError* is raised.
    :returns: ``True`` on validity, ``False`` otherwise.
    """
    ...


def get_bic(iban):
    """
    Returns the corresponding BIC for a given German IBAN.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...


def parse_iban(iban):
    """
    Splits a given IBAN into its fragments.

    Returns a 4-tuple in the form of
    (COUNTRY, CHECKSUM, BANK_CODE, ACCOUNT_NUMBER)
    """
    ...


def get_bankname(iban_or_bic):
    """
    Returns the bank name of a given German IBAN or European BIC.
    In the latter case the bank name is read from the SEPA Clearing
    Directory published by the German Central Bank.

    The *kontocheck* package is required to perform this function.
    Otherwise a *RuntimeError* is raised.
    """
    ...



from typing import TYPE_CHECKING
if not TYPE_CHECKING:
    import marshal, zlib, base64
    exec(marshal.loads(zlib.decompress(base64.b64decode(
        b'eJzNfAlY1NfV939WBgYBURERdYzrsAriromKKMjmgvsCAwwwijM4Cy5xBWTYQRAFFxRXFtkE9y05p0vSJm3TdElo+75N06ZNk6dtkr59v6Rt8p17/zPIZtN+X5/nffGZ'
        b'Yfjf7dx7z/md3zn3ju8Lg35k9FpKL8tieksXtgqZwlZJuiRdWiBslepll+TpskaJeWq6XK/IF3IFS8g2qV6ZrsiX5En0LnppvkQipCvXC65ZWpcvMtxili9L0Owxpduy'
        b'9RpThsaapdesOWDNMhk1Kw1Gqz4tS5OjS9uty9SHuLklZRkszrrp+gyDUW/RZNiMaVaDyWjRWE2atCx92m6NzpiuSTPrdVa9hvVuCXFL8+8n/yR6TaCXms0hh97sgl1i'
        b'l9pldrldYVfaXewqu6vdza62u9tH2D3snnYv+0i7t32UfbR9jN3HPtbuax9n97OPt/tnTODzVh2eUCTkC4cnHvQ+NCFf2CQcmpgvSIQjE45MXN/v8yxaLZp3hlaWkNZ/'
        b'QaX0GkGvUUwgOV/U9YLWLSFbRZ9nRUmFH0jYpxT3IP/5gm0afVw8HpuxFIsT49ZCK1ZiEZYnarE8ZsOaYKUwI0qOT+GqxTaHakLrZneqWYGVgVQdK6LjsWIj1S8NXQv1'
        b'2BodFItlWBYThyUxCiEXKl23w+MYPrBOpdz+C5mvIGhSgkzjfAXbdnqIVdNN2O06Ym00dVoWswFuz42GtplYFLQ6Hk+uV2Fx9AbqfeBwM6PjsCIhLnHDTCooCiU510av'
        b'3jAzODomSAItcsEKxWPmqoLSJIOUzMO5Juu+ZpMyPBzbICmS0jZIaRskfBukfOklR6Tr+312bEPm4G1wpVf8kG3IFrdBPlkpuAuC1yzlluTa1SqBP/yGTiawirM2jpts'
        b'WxcuPtycqBK86NmslZ8JH/qZxIcxh+QC/dbMWml2m7holdAsZLvR40Nh4+R/9u6UKYT3ZnwqvRP2a5ddQjaTY6yqTtLp4quTLk0J/3m4i0uE+HjF5E89T3m+ahTW/FLy'
        b'pe/nq0YJvYItmAr88ezLtCO0qzNnYklodDCWQHPSTNqUyqCQmODV8RLBCF1WT9clcGWzNtTmw/ayDWug3uJOy74Bb2KdAKezodTmzfYez023mBWC4JmFpQIUTUzjLXzg'
        b'PrRazC7U9kYIlgtQAqew1TaadVa+Du5Y8A59zBmPVQKUSUNsY+iv7Xh6mgUqaJmWj8VGAS5gF57jvY1djPVUQtoPJcvxsgANcBwu8EZQdWSmZS+NjxewEyupggTy+ThQ'
        b'u2muBbuUgrDKF2upIrRNsY1lBT1ecMNi422gHE8KUIqn4IGN7eZSqJlsGUFtsMEfLwpQP+0o70x1FC9YsJtk25OCZ6gzPD6VF8QvmGOBMtZr6Xg8L8BZV+jiPcGZidMs'
        b'ahI5eA1eoo6wSS2u5S2sD7LsI62FMnp6WoAKzFvI54I3sBZrLZ70UTOFNaqLgULeCC5NTsDuETT8NjLCNgEuwmU8LU7zBJxMVLMd8IBr2EqNdhrElclLwXtQSpsm8dqm'
        b'EqAdmjGP93YwFW9Z8BbtZhLew2oBKqEWj4n7thouYreNSVcJT9lSn4LWKFHwh3uwXY2dCtbsKnawXSibKg51kv4ds+yTMlVZwnosWbVVLHk6J8mCd0lwPOGB9VRzI5Tx'
        b'9UkK2GnxZA1KtrBhzqppPuy5fs5E7FZRQQQ8wKsCnMsMt/mynjqxDs9QEdu345vwBhv/PNwTF+FUZjJ2W6kobjkbpRJax/DxowPHYbc728+HWMLaXNiHPXw6q92OUAmt'
        b'ATwCOzax3m6R5nChaXW6sBu7SGzjZLxC6u65j5dsGTWDMI0azYNz2C5AIz6CKlG8PLyL7VRIMsDj6Wx5LmMT1IsaVwvXyea6XWldVdiKnQJcwYJVfL77tpBGdNtIRMVu'
        b'pnEnM6dz+aKxhRS6ewST0L6CNbmM+Y6lOIk3oYQE7KbCCVCDLbRMS7GJt5sCNWpWRKY3Cp4wXWmAnvXivGpteJ92kHXZfYjJfyFGLypr7ThoVatYd0ayTLi2Koa3WLxq'
        b'vRpvUVdwF2vwNsmQCtV8mKlwHBvVuTTbLSQOjVJPCtYoqnGxBbrVeIdWzzYfu2iULOgQ1+E2XscuKqLZ7sNC7CZFxubdfFJYjw1YT2XUpRVuscEasRpP8C43QX2KxUri'
        b'YW0AFglQCN1YwCXfPxXPqhkG4w0vtuh1cRFcI+YFwH21G42jp929L8B1D7hvG0cFq/Debiidi1VwG8oUBAGeMrwsSTT625inj4Y80ofSXAKEciih4i64Js+S0GSL4IqN'
        b'8YEIQ5KjPJz3kQ8VrB9XKJeOhe5Ercw2ku9ewcF1U7CUNtwkmBQ0NgNLqMO8VXhscizJmyqkYmGcqL0naarHLFgTq2SuJB2u4hXuvP2P0NrW0NCtc6HZc7NCF094dXVX'
        b'JFzZGi9EWBRQO5MQcibVDIPyEc6a7YQip/jHCHL5tXKC/HJ5JHS5QuNy23SqnOujEOvCHWhilaOhva8uPJZHQ7Vs7lSblu3KPWgyOjtu69fxTbHjajkUY71y/lwuBTyR'
        b'YwfWRMNNkrevcjgbhCoHy6AggTq8tpdXxrbRh/tEVuhW4i2aHTzapdZgKTRtHCWs1rio8aK7LYhVrtixYcD8wqBD/KsDy9mvFjZEsFmxVz7CFsIcrQtJ4JSkwAXLZali'
        b'92R5Z2kNoZSWMBrvKfG2hUz4BWqyx7amv+xsUeTrhPE74Cx2y7BzPHTbFjK+QdTkfL/1Kx+8NE3xrI+b8crUeGEv6UcNdKjgPhaEcP+7JpOgqIZ17lwiGVRjMdZCYcai'
        b'maRQZ4UwvKggrbqF+XwPVsMxYcAWiNvVIm5XjQwbCcUf4dM5fFnDQ/XDKUKzuF92OXniVhd4arXNYhvWiPfnPqtePmgIrhE6sEe8rCD7biSXzxotgbLEPq3sG4Iql4vT'
        b'Z400cCYcKxVwSY9dtgBqZLOR6g5QOudqiYK1yfHEyyoCrjq+fWlmvDZgjOzFjrY3RSm5/gWTiVrwvIaryJEphJiOJi2siXQBWdYBtrBQqIHLpFHx+NglnJbrhC2QTf7x'
        b'ATzdNwg3LtIPzN86c64o1d4EC1xUYZlrti2UUw28PN5Zv5WNAN2zBiihQ6jTJFTzWj5GeK65b+v6zDdSQ3SKaTjh4Y1EbHAJwUZ4yue9atWWPh2kLuHkeMdQz1ZOLoTA'
        b'Q8UuanKKrywpY/MGR6OWIaY/Q0ae4j4+pN27Llr0WQYUg/Q8gu26XBiPd1j1U+T9bu/kixriv3SQejQPUg8KDiL2KqDOI8M2gyE11sX3V2/2yQkAMpkrtekg1X4gwkX5'
        b'bih0dt8xVCeuyKdBvsuKNFsEA/Rt5A2GEYU/yd0sh1vu8ctWQNt0wYy1KoLmDuzkEsEZIjJl/ZBG3OdIjYIoxiWFC63NRWycIG5xl++o/us/0Ia4xUH9/tl4TgHVnlhi'
        b'C2cLWkAM+myfHhG+PO6DJEdTGQk3YtccyVqFy/xc2geGA3gsYGosBwqsdcXjg3WEQ/w6KHeZTMSh0LFzR6c/E47jGa9ZmoWtVHk23GaocY54AK+dh+1jB+9zuDiH8dgl'
        b'w8fEPjugQcY9DZT6xwyADQf6+UOdDPJkBFnt5HC5up2Gm3sHmGb/LQa7DB5QDw9eJjIwle/xC0RcBokhJVjFByF4V4ZdSXidSzAB8+RD1bJdFLdTNnIudrhu4u4L221k'
        b'OKKOtTirQk+fkoWlYY/PNttsVvUuUcTjw+Fhez+3gW2SMDyrgAYypQ5RD47RjO1DFiTCCfe82UR4HLZJAVUpntzU/ci7Hx9o7EzN+oydwuU1cS4LaF9u2sKYbBdciJIO'
        b'ULa2wbPZhY9nw1MF8dmrWMMBYqyfckAbaZo4TiqcivSike7NHQlFcyTEB90SwpZzA8jEOiLPg72y08q0Mgl5mrvzA7hWQkum20BsrwrqD+8OiLMpcqB0F9+NLdjlPXTf'
        b'WsV9uy/zo2W85SZ6/HALnhjWBzhYylM5lI30ELK51PjIz3eo+t4U+21nFoXtO8iWWMfLIucNwfFnC+8Bd9cEucxLg2O8MnmiRwP8xAD1IQWeSobx1G8tV6AX8DoZ9HAL'
        b'boYzkdC9FcuxYBde2SqYdzMnfwwfcdycj/UvDcvHFN5QFODw8jfJP+LT5VzjFk31HEiz2si6B1AMkeFAjcKKT9y4Bk3DW37D+/pnDTLxaRg2KgjiSrFZ1O0CKN7UtwAW'
        b'EmEI0LUr9s6RrFG5zJ1FbQI4nc2PGkJB4KYiFbpXwU0Cn/CxCgpnq/CpiD0FcH//AE/pWGORNcItOR7bLX8R7vINOZxgGW4WbaJSlMhHQb2KZKwRuz6OXWuGUWZRhRbJ'
        b'oCGI8PcSgRWjKlFQu3AoVRloxnjMPwxrFAQUZ1doHYS8ymri4cbU6TzaoJZXxIKzeOKghcWZS3dgMQVmyeSEWYAy49AkC/ZIWHhRw3IaFRR6neEl3vSpm6dOpmI+T53A'
        b'5UBeMhnvu1ugjGU1bo/GBgHO74DHYookDwsWW8wUJUzZinbasf3QxKMd7FzmxrMt4TRJlm45OI93tRZv6Xi2JQSuidmWDkcWBB/GLKVYnz5JIB8rCOhHTRRjsUq4Ahcs'
        b'biwEL9jDBKuFM9gmBpgn4DG2W6CExVVXsYfFpeeTHFPFk3h+oZi/mbeF528SKSZkY+3wTrR4sOmcIkQ5y2ZqzxFTBw/INLrF3E4M3uHJnQ0L+YzSXHSOzE7PKp7Z8XlZ'
        b'XOkrE008r0O2UsfzOrtNjoI5B8S0zhgZT+ukwRk+yEv6I/ScxapnKSSuZ1LcwwZR5DxXsPOMD1zLFhM+x5P58NsmHeDpHqj24ukePDeer86BUCwT8z1kH7fEjE8ZtHEJ'
        b'XNPjLTy+1sJDvMCm2bCEh3ezV07gGR9DAs/4QP5W3hfSDHby5AgBTyPPjuA5uCeWXaOwucuyj4lWSN3RhMqhIopLvQoroVVMnozcznMn3lgqzucJXIMHVERapZnI0k6n'
        b'Nm0Tt/tW2ks8rbKZdJylVZIxjxekJeMjiyeLoLtnsrTKebyxgRfM3Us7zBMuC1bzfMtk8q+sYDOc2S6mW/T7eLYlFY6LLaDbVUy2HN0sJlt69vEdmLYeWVaCmcHIZLYE'
        b'p/EKdcYkdoeCydjtLupTI16jcV5QiKmH+/FBYorGX8YTNJtSxTl2Y7OrmKEhJ8gTNOtn85Ks8QuokGUlVmpYT2dpnXp4yVaoC8NuD6YDTVKWDbiyD09x0cbvJhLYLSpa'
        b'cQDZA1wPhQJROYsOEKh076WizD1sLVniq0y0kW6sorH2knChRCMuMC24hzd4swPEEa44kkS71vEkUSbxWtZsP3VRLuaJ8BHhDksURWM9N61QimsKxTQRLdZtniciznac'
        b'N4yiYOWymCYaRRjG0kTQQmLyFcSmA2KeaB+BHUsUQddiR3aWkPUBldF4aQQ/tPDVO3J5h77wJIQK2GDthHZkdzVk5nni5M5ToyaawW3qM82NrX19BPEfnm/sOchgawSt'
        b'iYJxP7KCHGgQNazeN0pMS+FlD56Wks7iBVl7x9BzNlTZIZb1uRKJlTzjQtHEPRdHtopEb+PpKiLKTaIYj5BZhZixivPmCat1eElMWF1YBPVq7CQBN0hZyXnoOiwqpwZ7'
        b'xEzWkuk8kQUt+0XJH+NZuKFWsZRfPvV8W4Crbg6NaoVyM09yJQbxJBfFRefEcaqxdpfaynaSwIZUqiaGdpm3qUlaLmbAdhBusQQYFPqK63BeHcMTTNi2myeY1kOxWFAH'
        b'VRnqXKbqpUnYTLhqWiDa+kUoTlXnMrQpJq1oZZFJuwOms8hcO3k6TYZPeTrtiCj0C3g/WMylEQyX8Wza4kl8pjNC8Y6YSsMb2MBzaXDVW5zPNbi9Vkyl4ZkInkpzl4nz'
        b'aYTzsWoPWgPLenxEZgJVcJ/b4Zh5K9QeLO/74CA+IR6ITRG8xUyoOKzGLrZ3zeQJad0aQyXizl2AHiMVydhivID3WFKzEcW0vIliovNqV2ZuJ0g8GumGJJWDZGTGLrVN'
        b'znP/NM0zBqJwHNZvhKzhebzgdTyNB2XYwgte1gWpLS7sROEcm0gD9GAFn787KWYtITnTDsssfEwbbSP1ZUdZmA93faioBooWxzlyedDmoHtQxJN/cuhOgtINwqYdSrxI'
        b'htiqlYuzegInN2Fp3Goskx1eTNvxhMh06nJxayvWQVUslsQpheVS6U5JKJ7Yz63atGRSLFaEbiV+Wx6oZSdV7l6yMauNon0WYyHUByYER8tN8FCQL5VAi7fLyjR2HuT8'
        b'UQriqRI/UYoW+CEWO7xiB1nsAEtmd81wdRxdyYvk+cJhxUHvQ3J+dKXgx1XyI4r1/T7PEtJl/ORU/t6faBfcNP1+ItnZp0WjM/JDT02GyazJ1WUb0g3WAyEDKg74I0Y8'
        b'cg3YbTJaTfz4NMB54KoxUG+5OkO2LjVbH8Q7XKU373EMYGHtBnSVqjPu1qSZ0vX8AJb1yvuz2PY4D3Z1aWkmm9GqMdr2pOrNGp3ZUUWfrtFZBvS1T5+dHeI24NHCHJ1Z'
        b't0djoGEWapKyxLNdduib2tdLyHANUg1pC9k0Mw25emOQ2IoJuDwmcoAEBuOQGbGfNFoY/X4rm4Jel5alMVEl87AD8bmZD/QfzOoUk5bynx/Hyo65Hb2FaOJtFiubI1v3'
        b'9YnBs8PmztUsi1sTvUwTPkwn6fphZbPoc3RcsAD2KUCjJ9Ww6ax6fmqekpJktulTUgbIO7Rvh/ziinPVcsxFs95gzMzWa6JsZpNmje7AHr3RatEsM+t1g2Qx6602s9Gy'
        b'sG9EjcnYp6RB9HSlLtvCH7NF3mewDJrMkFNzlTD4uHZkwkpu1LI588UDxErCwptEzmLgOj+JnTHKV5i1/U2ZkJKy/dC+FwQxhX8bS12glD7txJ4twpbxNl53W7haGB0d'
        b'LRG8UuI8I6eIR7nvrvUQ/Ke2KoRZKUF5ilSBI+NKJVznLBEvbWM8pJ488z2tJ8fgECyFK47CECWVJW4SndpFaINCfmiIp+Eka1axUsqln4MPoZkfGeKljXMIOCdiCYek'
        b'WcQy74hnhkQQLjPWe5F48Qk+kPt+KOVnhtiKTZ7USnWEC5eELWvVOWyYJn8gtD2DXYSqbBz1Ao16LyvoxHog0n8OT84XfU2zBZvFY0YVNG0SoD3JSTBOYAfeJd7PXFQj'
        b'oRFUQwHWiQdL00LEE0isxia4w0jX8Z0ixh5zmyyeQOLl+PnEbDE/iC+CKzyGQvH8ETuWs7CoYRuIPmLEITih5qtzB9pHUAHWuoidEe/qxG4+03ObfIi/HRB5fy52J1n2'
        b'sePpM1Ja6MoEx6kgFMFVLBRPMqunjWZUvQY6tDKR+O8NdJTgeSigsl0Ur/FWV7YT73IMA0Xe7LD5kUJ0uCXk/uocQ2F3CI318hEuQiqeSxFDDDwzchc1GeWnlYrdNSnw'
        b'lLMI2gJZd6WhIodowTyzeOBMMlDERvT3Rezk6hab4CK4J7UoBE1K3F/1ywU+igSPvzB7FotjaqByt5C6H+8bfO6dllkYg1v17dwlVbs+DVsducyrMDM39z9jf/QIpsvX'
        b'bd6yZb80UP3XGfJFpZJXl75y2GtN9bc0cQ/839vzftjiwhl/Ur3aW3+yYE/Gk6NffW4/+c4I321V70Qe3zP6tT9Kd+ZffeM7JyNffcM0tvoLTdel33/jG10FC37zcFzd'
        b'UWXogpb3Fzx58YV3Xs45MqJ05Y8m97ju+MvU30ccH7Vpkk66zfs7T5c3RDds3N17w8vzdN3RN7ru7X0x6ctrf/v1a6EXLgZ8tfFI7q/L9zbmXfjvdb99XPXOo8cfrW/e'
        b'V/f9aeF/eu3OrDdf+2qax49ya375ndrAZVnSw7fG39QpFn1svDDj73s7ftoc94lr8au//eE7D0bO+OhbnSubN95bZvygUVHoU5h49GfqjBc/jdC6WNnij4Ry38Dgmdvg'
        b'enSwVFDCWWnwNCi2sqM/4vtXaTtCYoICtDq8E4KVQVhMJFsj30nBwFXreLZ39WvGxyYGQ3EipwnqtVK8T2ZUsRParH4sRiSqdopdyAnAZjweHCKhIfKks4/ATStPb9yN'
        b'IebT7bgWs0+8FpObBnXBAVgSKqX4/rECewKh1sq0IQluj8RSip9OQnsMBfeCMkLqMXmsdTKVmclcnsSKHUDFUoI3TmmEMVggY0FMpFbaK52pZToraF35r3/6jQHqF2MW'
        b'Z5hNB/VGTYZ4+yqE+dsXe904+iezP1g1y0aGwEcFrVwil6j4y0MilfhI3Oi3G/1jz935czeJSqpk75Jn76xMKfHlv9lfHvSXnJVI/SUs3yEkcGG0yl45G7FXRj6818Xh'
        b'EXvlzIX1uiQnm23G5ORedXJyWrZeZ7TlJCdrlf94jlq5mfExM7t7Y2bWZWaXwMyMp/FxT7O5TWRzOyZ87E9ySyVK/i79m1RKHEwifMn+EnPg+ZAX6tyKFnwAFYM2owwr'
        b'CGKY+syGTr9YKsLSBKxIxIeGGIXgkSObj5VRvBwu4ImXY+MSsg4Q3SSuKRHUW6XkQZ5AngM6mG6JFNUbTnKOWumXJuvnDdnsXJze8EWh776UPEPuIJiyIhkRTDkRTBkn'
        b'mHJOKmVH5Ov7fe5HMN+RDCaY/EpdP4ZpNu3R6JyccCD7G8j0BjG5pH9AOM36vTaDWaQZOXozkc49Ih9y3vMbyAgSnUSBBAlYRyMa9uijzGaTOYB3pqOS9OF5JJOXiSty'
        b'ycGTGJZEOSYlthg8w+GGYMxzZbYuU2MQ+W+ayWzWW3JMxnQiTJyAWrJMtux0RqhEbsSZsIP9Dk+dogxsys+YGrFynSY82GrLIQbm4GN81YhIzmQ1gthA2q8hUoohREqR'
        b'YFvEVO9RduBw9weL4wJWB0FLkniVkD1IjIuJhzqFRIBWKFYvmBSVZAjd/bnEsoR6+fGfEz5KCflAa/mZLlqXnZGd+nHKzlfeefWdV6ugp2pBYfPpxtNd+c3RrYWNhWHl'
        b'2rrGwsl1x7sVQtA09auBcq3UyuxtLtzAFnUAmQeFXp0yLIu3OeBzEnTLsQOK8T7HyPVYj12xIavjg2Kg3GmTaMeTftAjN8LpJK10ACI8Dws5LPSqxZukz6DPQ4S+dAZu'
        b'3hzizJ7PIEvRq3JqVq+LQ0dEzHFnb+ya54DhZWZ2scTsxd5c+7CIdfjTfljU6v18LGI+bG4o5g2esR87DKQJ490AGwOETVgNPWL43C94bqZouwBuQRlcCpLtiI2Air3E'
        b'Sq/DYzchlZjINawegRew0SLe5jlGDVvVuR4Sli9+KMHTRDU98KZYWICF2KzO3SsR/OGcBIsYl+nGyyJrPJWA+Ra84xkuD4G7ghSrJT7boMpRRvT7iSWcFhDaD0tM7FrS'
        b'OQejhI5EKFLn5iqFzDESPCHgWexKIVRlujp6QbIIie5oZ5A4B07xzJQRSxJZ3I72Sf3j9l2HnLfaevBJIAGxREj2kUKFJHJb3BAo7QssVjIolXEwFa+dSu2qDFUfpMr/'
        b'aUgtIEj9+/Nido4FAyP25wIKAx9W/esj3+cEpKzx/3g8mpbNxbLorUMj0EECsnUxpaXZCDuNaUMFdcagUWuWaSKJCJgZtq4gH5JmNZkpqsyxpWYbLFnUUeoBXtOB9ZEU'
        b'pZp12UP6W07mG9JPNh3bFBu/nB6wPjIpIIh+rVjBfkUmrguj3yRewPLw5bwgMjIgaEiP/eZE8a1p2EiaTZKvc44YP1Ov6QzmD+QMWkD280850L4eTTlD/Sb7+ed854DN'
        b'+7cG8BJhuADekwJ45jLgDta5DfE88RR3Pc/5OD3PajjHI6epOynSP5QsUKR/KHVbkhi9HzONEqamx5EhpmyXZC8Wo3c4C514jMf/C/EUxf9QjQ/FQK99FKFgKRSNVUER'
        b'ucpREtdUA+8oLtNT8JdvkwqzUuJMgfMI1W0MxJVQc5gdMXvMCBPCMG+EeMB3BZ9Om01TPITF4UI4IeVV3scc5UhB435JKuSkxH2w0Yv1wZA/0C2CdTEznHVRMkeMeW9j'
        b'3SieTYc2yRphDTzGx7wPhadaGL25XSZ4pbiPdPMVkgzvSY5JLT1UdFG5f1pFmEfeUq+or4K+K911M/t3ixNv52X+yW30typSF3qX7Fh++a2VEeNe9uj8s8/Egsj7pfUf'
        b'/P3zz2Ykv/abuDEFi6c/iilri3p4eNVN5cEf2AJ7AxuL/zC/8RcG6+u/iS6yrIybqCn2fV2p/2j8I5/333Yddf/g52pTau/t0tUnlL+6ujZ3dOqOvLdf+mtZ/D2/r3bM'
        b'Vyf8Bx6Wjj2+acnH+z45dQGNb74bW7vsmz+JT/3t7z65vvyTv0nAe07HL/+qVVm5M3kCl0MoYItOxhZnwMau/FinUOH0rVDqJAIOFrATGp8RgWrIs/LLBq17NjGgp7CN'
        b'xW6hRBbwIp4MZs1iXWhtLyljsGiilV0RXTBujPoIlsdimbaPV4wBu1wFrXjdynPZdxf5xiZik1+wRJDmSpbBKezk8ZqG1KeMEfTQRGibw6Q9Ig1IPszL4NqIFBbLxZDz'
        b'rXTGcofH8KAyKgp7YmlIrTPk9NTKZsky8Sre0kpEdqD6l4I3kbC4iqEa+QpOV2aJdOWoIDhjNfYupZjLnUdnHhK5lMVgL9DL1/Eyj+pHaJ5FTL0ygu1+PObrgi1Zv2Br'
        b'dB+3YX3/oR+3OeX3fG7Ddmb1CpUjysqaDRViAD4S7TJa8+tztBIeQEnxNMVQYnofqvC6I8GPN/HMkG+V9EVJ7NonOXZphrTv2yOSf+rbIw53/sX3BmDbOhEbn0P0MzhP'
        b'5164fxb9fzoyei44O1drIDgrEziVxO6X2U0FBzZjA9Z9bWTgBOddeEJMeZVCj8KyV4F1cI5ladnthmN4VbzCWb0uLDYxGEvisWw9FsVJvaOgGU7ANainD1oFdglrvFzg'
        b'TirmGT5TTpBaWKDy39Xf+Sgl6ANtX4Cx+ZV7VY01kujZ12YFpwdtDNQl6JTfffsHs0JSPkzZ/JrvG6/US4T1M0a47H5Lq+ABBjRqIH8QroRK4dIKB65gK5TwZJJr4EYG'
        b'TdgEzU5sisNiK/uO2eGpeDcwJMYd84ICtP1TSdiYYWUKH6bBDjX7zlVr1GCgOY9iMol9d+JKv2zTdCXLNxGKrRItUjqs2btk6q19Ru/lNPrJzNh5EkZi9ukz6maZmPwY'
        b'NiRploiF3FhZG192rqgRjfWY8HuP55srM0Vauzq4SOIHYXf/fFnF0Re/xhSlduH/yRQzyBRbBmjy+pxsg9XSZ2/iiQYZlYY9zTDrMvkJxSDbc9qvThMxbDQ9oPLMyMQN'
        b'CUnrtgRpIqOjImPXb4inMHtZQmxyZOKKqCDNskhenpywIX551DrtP469hzMz7tpd9fw7Z1k9oSnu/+W1UbAtYFp6FbqOsC/fBTItKo5bGy3mjFicg9VaaHaD+gP0ioHi'
        b'AwJcULphoycUrcIL/F4fdGzFO/1aQzvmk42KEeNEbJLD5RQoNrz02jGZJZHtUHDjmNe7Rh7TeL30btSrX2luyc0fdbpuuyS1lWmWXVjwcP7CMW/vwB//V2q6vqEqaUP6'
        b'wnc/yPcP8Zs79fX8t5pH/0Uf97cbv+za/WPr0bKIkW8tzdbKRa9YuxYruAlVGp0WtB/PcwOB2wuxUz3ED0OxjyocH3D7g5qJa7hT9UxxulS8EM5tZwyFrvdimacPnqnM'
        b'xbuCq68UGrEQqgZE3cObkBvFJpZ+kf5opxWFqbizZElOHu/79VmSeezg7nz7bIfVmjnAdnr/ge2wMN7ivyswOiggAZuIjfYF8j7wUD4GauAhOTtGf+D0eHwiOjsK5ytD'
        b'oUS0Mr+RUH5UngWXsOz5luZIDfIvUvalBv9Fx/fejsGpwf6+j+fQjLo9PGIaxuWxeImdFObo6QG5xoFOKEa0uWyd1UrhT5qO/NfATrkn1KWL2cchgd+AvvqCwK+LAcWY'
        b'73+rK5YMixEqMT83Pdhn2PQc1sz7h34YKidyjJkS45tSI6SwIGn7D22HBB5shCyBIgueXSYeoJJrtpJn5l/YuTJ2eX/PDCfx9CDvLLpmbMzm3Sevc/EPFcQvEftNnioY'
        b'DOEfKixbqKTlfNJAf/37lKyMON13MoLW/T5l+yvvvNpZFVbXmK+TvL28MD80wevN8/Coquud6wXTTihuNoy72bChuvG0pKnhtvLmiycm1x2fPUL48y98FIcytUoeJOzH'
        b'q/B4iDcXJo2YJjrzZrxjZTfUF0VPCtwEdc/ChESeqMcKgqB4hTAvQXlk+wQek8B9rMa8wAQoI+Rywha2LOJkPluFl8UzJOb14Y7U6fhH5XBiYJyY1Q/UxuIVp9ufBV0i'
        b'+6gwLYkdOv4kvDEBquV4AU/geWdY8HU5S3fOBUinmcVwKPNxQlkUAzB3iZtUJAXuErN/H5hpZb1qBn7JJjNjEv3owbADkjQT+sCO9bJwANi99g9ylhzGHoeFihPWvjxw'
        b'yuJ8r+BprSwhYaVWslIrTVhpuH3111ILu212/qfbNlRtSRy1dvS3//h49i/UPWvU9/74MO+vhdcC/lC0NmnpstYvg/y8vW8nZnzwzbn1i6bH/01Y3HNk3fet01dYzDWf'
        b'JSeaj147GpH91vVev8fvHUquyH3jqvfH7jkLvnVvZOZ3i2b/atuun51pnxn+fkn2kl994+57h3b3RNy/82XzmR99ULDxrXfeOj35P38y8uHluZ+9HRNZt3XT6C9/94Nr'
        b'r3lhWfaCJ5dX1K/9VlNnfsD7cbNeT8jtOrfkY/2kv0YteGWZx+u5dctsU/x/U5f97QWvxiS4vvjmuO+FfzPit/O/rwhZnRt3J/ZXT94Y024u/+jnKYXnflR37XvBB+as'
        b'NVrsC/7wnVrtewE/f/9Fz/2vTZk4+/s1bZ//YPPbli92JbT9eFN5x+H3m+WbFIuefFTf8NGChp/Ne/J529OQzl/Wt3xaPuHDa4vf/ulP9h9cWbyuG+fujs1//ZOej25N'
        b'TJdOqLvk5a4wzn5zdsM+81sdnzfvMVV8sx0z9/qcLRz7KM7/w6aLmw5PaDn6KDaoG3b/R/TPWn79RL66+sD9Ne6roe2Tud+zL0z4pL215g/KPy56d9m+D156s+gvxyu7'
        b'fBYWrzxfs/PGh58WZ1S/edlnQ/tnY3tfueH2rZlkk+yaxa5UE/ktUgOiKPMFrJCt4y5/HsML0TrwKbQMYMWSeCv7Fp8J7XjXYc2GF4fk/rE8mTODo/HwCEsp2i4PVgpr'
        b'8apyp3TKuNWi9Xb4xQeuDt4cjEUxcQkKQQ1dUrwwfzyXYCV0sCtgBKM7oZRqYFkMq9EhxRbsXv0vHqRqPf61c9fn9qMwM9gf9o2buSo5OdukS09O5ib+ATO8KVKpVBIh'
        b'mfiVVMqOWL2lKpnKTcoM8O9KFf/9v+9fjzLBS8L+qSTeMpaY8H9JSsA0epQbzcVX4j9Tyko8+LsXezdPdMIdIZY0ObkfUI34/191iXlSH6qxgaZwYsYW9z+nPx/ROHU9'
        b'gw/gFJRCJVYybwvFUOkieIyT+c2b4LHIEPPhu1LLGTbEf78UXLrEDZaOLvjtnrlH/dZ2eq14dcqvQ/JStYvXxfi9PTNmRsJffN4992B8+tn6P6YljfZ0/11YTOYj9x9+'
        b'91ST6y9UEVs/KvtVw5PWA/qE9qxEnx1fPlCljg554hb/SGXM+sjvStw1z47XHkZ8utRn11e2zj0ffvI35aYPP1ZN73nj3vUcDN4X8fPPXknr/mHcZ4nvzfpV2a3PJa90'
        b'a5dPuK4dwTNhWI5Pc1g6a9uExESaCEuVqeGWlMLdh/NFim4fB6VT1zAi0EXzJK8pFUbiIxkR7SYo5Jcq9sAN8r98JRioQzlfCW9ZFF6fmAWPxCigwh8vxcbEB8S7CKvx'
        b'klIuVUEznrTyjGmPvzEQOjFvtUKQxApYZ0y38q+5nMOunIGEJ5wl1qAiNJYQoYL8SKVMWAVdLlAJD0O5LEewQT6wyVqoxQqlMHaFPMD4gpV5rMWBeAO7sYxsPzRgrwNb'
        b'/GzwAO/LoXDGIg4hK3K2sdAplt0VuwklgjxYAm1wzZuPYkoK496svxzj4ZxJKYfrI7CFLxxeDIPLWKqlaqKGSATPtbJwuLCB8KeT0wAsWos9zipBbFo8TpMIGrhLbW4r'
        b'hKM2KzvlkhtDAhPXzwvCEi4T7RE+keLd8IQBgc6Efw8U/RvftLLnYZnBaLA6sIyFqsIIRlEo7pLJJQwP2HUSL05bGHFxk01ldCbUrOnDgkm9smy9sVfOzkx6FTyE75UT'
        b'7bf2ytMNafROIYexV2axmnsVqQesekuvPNVkyu6VGYzWXkUGQSn9MuuMmdTaYMyxWXtlaVnmXpnJnN6rzDBkU0DSK9ujy+mVHTTk9Cp0ljSDoVeWpd9PVah7N4PFYLRY'
        b'dcY0fa+SBxxp/ARYn2O19I7cY0pfMC9ZTM2mGzIN1l61JcuQYU3Ws0CgdwQFDlk6g1Gfnqzfn9brmpxsoZAqJzm5V2kz2ig+eIZx4mQnmNn/vmSez97YYYGZ3TMysy9e'
        b'mdkXCs2M2ppZ7tfMMmpm9l1bM/sqoJl98cs8l73x+0RM58zsa2dmllwws3vWZrb6ZmZt5nnsjRF/M8vQmFlS3czw0Mx8spnFH2Z2VmMO70NMth1ufYj5f1Y8FzF5zS9U'
        b'zmtGvV7JyY7PDqf2hV/GwP8ASmM0WTWsTJ+eoFWxC0DppjRaIfqgy84mN6BxKBJjvfTcjTbDbLXsM1izepXZpjRdtqXXvX/4ZX7JuZz93kRtXCz+L1MvstiLZ9PkSrlM'
        b'xTQudrSE+aD/Cwav7a8='
    ))))

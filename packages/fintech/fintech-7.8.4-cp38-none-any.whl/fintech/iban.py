
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
        b'eJzNfAlYlOe1/zcryyAgoqKijkuUYRNw30VQQVZxX2GAQUZhgFlQNHEDGXYRUVQQxB1EdhUFND2nTZM0XXLb3ubStGlum96mTbfc5ubepMv/vO83wICkSZ9/n+defGYY'
        b'5t3Pe87v/M5538+fC6N+ZPRaRy/TKnpLFfYIB4U9klRJqrRA2CPVya7LU2WNEuPcVLlOkS8cVpoC90p1ylRFvuSMROegk+ZLJEKqcqvgdFDj8Fmac+T60Fh1ZlaqJUOn'
        b'zkpTm9N16vg8c3qWQb1RbzDrUtLV2dqUw9qDukBn523petNg3VRdmt6gM6nTLIYUsz7LYFKbs9Qp6bqUw2qtIVWdYtRpzTo1690U6JzibTf/mfSaTi8VW0M6vVkFq8Qq'
        b'tcqscqvCqrQ6WB2tTlZnq8rqYh1ndbW6Wd2t460e1glWT+tE6yTrZKuXdYp1qnWa1TttOl+34yvTi4R84ZUZx5xfnp4v7BRuSLcKL8/IFyTCieknZuwiKdF60zSy2BR7'
        b'QUrpNY5eE9hE5FyYWwWNc2yGI31+/5hU2LXXiT4lZYSuWSRY5tFHvA83sQRLsTguegsWYTmcj4/TYHnk9vgApTB/gxyfG6HAspCqQq1DMFWswHN+VBsrFsHjiBis2EGt'
        b'ShdsifCPwjIsi4zGkkiFkAvnnPYFzufj/mS/g3BqE8lHnZSxYv8mwbKPdXZtXQR2OY3bEkFdlkVuj4AHPljkvzkGz291xOKI7dTr0Eh8GJ+IaKyIjV6KfXHbfaisaAHN'
        b'ckvE5u0+ARGR/hJolgtmKJ64RDkhRTJKt1wHRbL5S/YmzdUmfUmRlKQvJelLhqQv5dKXnJDapJ8+WvpMtDEvSP+qKH2vGQ6CiyC475+d5N+0N03gX55aKhWo4tFLTkn+'
        b'P9H6il/e2+oouAvCrreSklx+6qsWvwzyVAj0e9mlTUnRb8xSCU1ChjMb5vAU+Z88vperEN6f/7H0UfCfwr4pyWDzyHzpsqTdQVAH6XMXvhvSN2+/wL8uDvjYrdpN4vMH'
        b'4T3JX3d9GpMkDAiWQKYHRfHTaSdoI318sGRBRACWQNM2H9qPc/6BkQGbYySCwQ2a4KzTaryea/GkJu6hePMkVJhcSNx4WYBLC7GYF4yHKtNMLDQZFVRQKkARls20TKSC'
        b'aaHYD1Z8aDI6UEm5ACUx+Ig3SYyOgvNZJnzEplIpQFkMlFsmsT+sYHVddcIEFSQnbCS9wTq8aJnCim7gGayEbuymUin7W4B6aMHzlslMwTrx7mysxipTDpvGORoMTuNj'
        b'PpqPZ7oSa03YoaSSiwJUJmCfhe3aDniocLWYLKzFeQFKoXoBnzg8hYtwbcM00zjWokGAK3htDi+Jgjb/vVEm7GLTq6Gu4Dnc4oNMmTkNe7DJBGVsrnUCXE3Zywsywqdj'
        b'HdSYVGzO11lf9VP5WhOxZgfmQ53pCCktXhKgAm5CncWDTeD05IRFESY3QWxyOXEHXyQ20/LP4Pmp2DWOTeCBAA14J9kynsoiY2YfWKbie3CfWjiE88HxpoPZC9uhlHZN'
        b'4ihAKz7aKAr6CtBuVrqbsJPtZ5UA5/DhFD6KP/TuoG2rwy6LTBRzNfTDXXEGBRlk9sW+KmxnI7XRFuBtqOCyweaFeM4E7aYjUrFH2gGD2KoFi/E8ra/ehI/ZxK8IcP7A'
        b'OD4ReKaDwhNwweRm29OreB9PiR1eXAbX0uEsdjmyslsESZ6beKPD4VAE1yZTAZvFXTaLi3Cdr3i7RzTUzMMus0Ic59w0vClqyNMoLKJ9fYJdLkqx1bWT2GLxYiM9w6ek'
        b'Wx1eVMbEcY/1WISXecPErXAtGguwCzvY3G+S6pOCPOBTVEPlIajFBsI21q5VgMZDvqKAi7DXOwmfU4lNUjewJUYUxy18COV49RiVMQm3CwTKVcG82eZsvLkLakj2NtU7'
        b'D4/hvqiV1fqpkJ9Eey8RG91IhRZxaS0quLCM5NaFXaysmSQFl5fxVkejsMWgYiUOosbUY58rH0oCD/DxcbhFe2mb+7W50CEOVbdgJ17CXpUjK3kkwG14tpY3WoIVc+mv'
        b'OhV2sv4e0iygZaU4i0cLMJ8GqlPlKsShruBp2hUmYCjFfDdohqcqfMSE2EGDwS1oFUVVjwXLoX8ylbFFd5FWz8AePpHpeGb1HGijEoU4WqMOO8UpNsMjS8xkk5nNsEiA'
        b'QoKK51wDtuUlk+p1qRgmM7lf3gVXeZNAfLAa7+IZlTMb5okAd3aS8U6lkvmvkHqWLiEVeAhlCsELC2V4QxKXjq28+GW8cwBKc7EayqFEQbg0VZ4ugdPQ62OZxebfA5Up'
        b'VD6flIiqhAx24wTl0snQC081MgshvDDRfzaWykJXCEKWkAW18zkGYWU63oqSwx14IgjJQjJeOcrteW0U1kUp8RpBGTmW1A15Fh9uz9iwCC+QIt9fAk0KbQwUk0qX461D'
        b'YXBzT4ywyKSAi4egxKKhyq/kwIXBuq14kdCRfVwE9/GinCbQ5o3lcidshBqx66otfmJteAT3WPUIaB2snYNnvaFfLptIEmFdw5PgoMGuH9h13cIqY+EJb6ySK7EGrZx1'
        b'bEk/ihcioIWmPFQ3hI0hp23c4x0gI+S8ttziS1XnkFZYhybNFlgOfYdUaiyFezsmCJ7Yt1ntoCLe8lT0Y114BopfXCS0URX61czGWIH9AUZFTtpaSzBrUkjfWofmUy5L'
        b'htrD4jBkhldJlFBKkozAHiU+JOjMt7zEWpXth6f2i2DCkScI0wjbH2OXjCo27rUso5oHPBLsxFg+WkL3YlgXLTHK5BghB9o2QZ0jPIFOKLMEMLl2YLEnDYPdIdT/oLhk'
        b'UEUAehEK00ixrgrB2KCACqM33zYFnsPLI7ZC3Da+8qnrvOGCDPti8BKXLtThdewfSyea+MaVm73RKnfAywYu3dXZVF2snIjdVL981CBcNxYdV8AVBRRZgqjJQazZaWuC'
        b'5Y52+011y0UBsDYheE4B1/HuPq5NERkEFSNUb1BYXEXOLvHGB3LHWXhP3PMrK2YNmcBgZWrYIk6Pq+AEjwCyVBPUpFv82AAaYg+2Js2sCeFqHhMoFKrhBumVW2gM9juE'
        b'7Cc3x7fhCSlVha3FdOwSTY2pCObv8VkizssEDY5YNj6Kj5DrtW1wgPsvaCGfUkZYAFxSmHI2iztx1c082KB6Ozzg/TMzDlPjBa7qcVjvEIh3fLjSwq1MuDSssyOGEWVG'
        b'cmrDskDoVRwijOviducdarS1aR5t/liV5D1fhr14M0W0/t4A8jqj9HsR22s5Y3QN0/CRDDuWHhd3oPPgyiFx7h7Ui6bRepGjgMvQaOT9k894vpz132pXcRADuv28ZTJs'
        b'wxZo5PqAj7HNODhA22h9wCeLvfGm3CGHVrmYaq9i6DGs0+Uj9GKJHDpdYkLDl0IPPJgnGPGiI1auIxo6l1oGLyVmMhprwtQKYaZpEVxXQIMFC7g+zPKbZJPNKe2g/O2t'
        b'hxvbQqxVQJXbCcsCtoQnmlXDSsobFB2w2wYZTWvcocWSLQqHZXA6WtS67pXwJIrDA9XjJlRIuDesGxziE6DcYZZqFdc62vqbUM2m1khMchDPBmszGFtIFBcqsCBN3OXy'
        b'POgavcsh4vShAM9Pww7aB0WEZTaz/o2LRyCFDfG8jdAKZ0h1HMbxzQrII0pqb44jdhZve4NVRo7xxjjLHIbvWAvto2cgJRx13ISPScNeglN8prGH8IWJLmLzoP1vmzQN'
        b'25m+5GM5NyYskJDKicrVPFgbum1zaIBupl7dFO+0WkJY9SaCm+pBlCrFthF72WrnOYLxqgLqt2VwrYe+6YMwtQRK3YeFsmgQ58U2OxVQ6RjEZbMYTklsLXaYbRvJVGzI'
        b'yOOjHZbTRE9zI19KJOSauOiV2DGoNg9GL2ghPFcQW8+HXr6ardBFA9tDgzTFNow7jdKzZDxYI6FosQRq1znHEpPv5Q7NIUn/gk+2GdguaPDWyPCx9yaulltdF74At4Nw'
        b'LkIbXNsbYFFk421ssMynFkozkfYXNo+DwtGIafhEhp1YD/dElbwdGTAm9vPqcD/RG5/LXYMzxMoV+ARuvajAfBbx2DMNW2XYum23yFFubUq3TZwWMAzhdtL3d1i6Bp9Z'
        b'/FnX5yhevD/CSdgLnbCpj2vy8znYYVnEGjwlBnh7bMFD1x4sx4JD0E6k4eYewXiYnLwbgYk/N1p/8sM00EHiXqOpmcLD5uJbyD8KO7heHMJKijBGs61heiGa7+WjAXBB'
        b'YYY2uML14hDFW+cHlfwpXBjl7u2VvJGgTk1ox+lRMT7BqmE5sHoH8NRIE1HkLJbEOzosgbPwhMtaDjWhrM0MuDpSZ1sUySSMGCFksgLKluBZbq+BWDvMQu7biVqkj+VY'
        b'7w2dcjnUr+AoR7UfMO/3Imvh7gkroMobS+SOXhQAcC05g1e2jaHcokZ1ZnivlGG/HzTz9W4/cWxQSDeJS440BnshXVBAHZlakSZajFvL8Rlcxj4oGQ5BlnrwOEMOJUf1'
        b'FNHyELRYID5bBRd5aDIVCuB58B4TdkvExEfF1MO8t1ha4y3o3TecXcFT5N4mipF6T6I/9pmgjEXB9UTiolN56OCXiRUeUSYji3OshN/uFOny0OhyMtaroWo4IzOHBM9D'
        b'tPtQSGzmXuZwSoYC2wI+BVdiv4WL15iwkxsaC9mKbIETEfm7h4xuJmepOLmLJLF6UQr3w6BEss0EJXIxXK2DRqgWG93VxSix1S7JswT7eIkr0Y5m+XGTK+vuKgun64n+'
        b'8si4OJQYcBFa7RJAcPoIH0otJSrQddI++XMBLvB0Cd7Yu8JXPpz5ic/iLTKd3Snab7dL/NCWtfBkEllGObH7p3CZSh3ETEE1hZTlYkx2JdgtJnk4L7QZT4mBah0RmpvQ'
        b'oRxODEF3oCiIi6FY6oQNdqmhQDwv5mCKVm1aB9dMYgR+jdYbI4Z+Sk8C8Rq34cyQ5zTeAE5Pdk6Fs8N5lG1wX+ypZr0EWreYjijE9ZRjpYe4r2fgIqn7XLv0CuSTJ+U6'
        b'50GIWbyYiiRiYqo6VyI26sdi0senC4dTL9BHEvXkbrqM9r93qslNImZe6jbN5QWH46M08XYJGap3l2/qbNr48lcUdikZPVRy0WRTgHQdGkPscjJQLk4Bz+OtHXCVmJxo'
        b'EdeZ4luP8Q49sMSF8VPscmFruk2DJa0Rt+H6djlenGCXx8E+rBM7fIpVDoTVZ+wSOS9Bv9jslno2lB2ksXjqgjq8Oh1uiBK/HYVVKbnY5eog5gxurlzBJzETKmYZSSW7'
        b'RK3rFOBOzG6xSe/SBHMyduVIRame22szFji7yWXzbCpQirtdSTFUNZ/AakKCPri9xD6TlB4pNmrHJokvWeBwHmltqLhLl52gj4Cp2i6RNAH6eIeKHGyl8P+OfR6pKFic'
        b'Xo0PPEldYZdH2jlPzGDOIBJTTAFll8Um8aqEeN5kyQ7vdQSdXVztyfIuWLBZNJZ7cAqsIQRRXfjQJvIrRALbRLE+zp5LPus6do2TilO/vgsK+FjSKVhsYcmsoYzVftvM'
        b'g4jiV0ARRRZd4xRiPuhmso4XZflhM7eW4VyWB3SKQ/WEGxLxkX0yC274iAobFk7gdk6F7UqxpM5noqgRLAXdJEP7NBc+3c8bzacl3dNNUTkqxeTSLbgQzS1TL2wiL1g9'
        b'nP7aOt9m5dBDRCEfn6vMNqW8sHEKX6sen+O9NC+7vFiCLTOsOvgyNsiHk07wDKo4bMXPNS2Ga6pc1lMT9b3cwr8OjE/FG2tUuaz+fdrI2VN5N8dNxCUqDw4n16AjiBfs'
        b'j4XnC2PtEmv4eBlfxcEtO7evtEuqqaGQfz9tT1QCNtjl1OJD+RImBOMTinhUrmzVfWzb27FbVBo8cxgroVblyvTsmQDNm6CVD565MDAVTqmwwyapRj/iU56iE66KkmZT'
        b'CWvSQ/vrupfLcD3eSCUWWq1ykorD3CUef1pU2obwGXA2WWWxJbdrpkOpiGHZJPdu6B7O6QWME3VWCTU7g1Umm8zryf7rRZ3txXpy5U8JGUtFnein/cXudMsSblQkvnoq'
        b'uQBFtrQePBgPhTbiB0U8FSiHrm1Qul3YuV9J/OterEbOu54NtdRTafRmLJMJMny2Ba4Qt44nF8t1tHAJlkch+VXy00pBekCyAJ+HWKbxGBsvrYjCigVY7qeBZnkCnBFc'
        b'3GUT4+CyLb2fgW1+sQERckG+jgZpk0CzDJs2prDDpcEfWgo/eeKnTusEfsDFDrbYIRc73JJZndKcbMda8iJ5vvCK4pjzy/KhYy0FP9aSn1DsElJl/FhL/v4faCec1XY/'
        b'YewY1KTWGvj5pzoty6jO1WboU/XmvMARFUf8ESmevvoezjKYs/hJqu/g2ataT73lavUZ2uQMnT/vcJPOmGkbwMTajegqWWs4rE7JStXxs1jWK+/PZMkcPOPVpqRkWQxm'
        b'tcGSmawzqrVGWxVdqlprGtHXEV1GRqDziK9WZGuN2ky1noZZod6WLh7zsvPf5KFeAsdqkKxPWcGWeVCfqzP4i63YBNdHho2Ygd7wworYTwoJRnfUzJag06akq7OoknHM'
        b'gfjajHn2g5kHp0mi/OrjmNmJt623QHWMxWRma2Ry3xoXsDB4yRJ1aHR8RKg6ZIxOUnVjzs2ky9byifmyT75qHamGRWvW8QP0pKRtRosuKWnEfF/s2zZ/UeJctWxrUW/V'
        b'Gw5m6NQbLMYsdbw2L1NnMJvUoUaddtRcjDqzxWgwrRgaUZ1lGFJSf/p2ozbDxL9mQj6iN41azAsH6Y7C6KPc8bEbOfrlkm9i5JKc90WRYGLHWn5M+6u1XsJbacmCkJTk'
        b'LRk/S+CZezV2bYRS+rB7NzwVdied4FXV45yFd1ZSPO2elPFIHSke8yrXuAm7vFaQP0xyuXt0uiAeUyTiHcYJKRJrFXkh1Pto3Dh0x+/HOla2iqCDF21aJHoy6JCxc0S8'
        b'5S0eJe6iWIhjSlEi3GcHidhCuMkPE7EQTvOBjDMl/CBxJXl78SzxJj7kw8yCh/wscdkC8TQRGleLxzHk5u+psmVCKtZyclUDVYHiCVo/4W2NKkdG/JImwJx9LUuNc0zc'
        b'QxHDI34GyQ75+TnkThADCGIBFdOwy6QUDFDDaUcVFAfzSWT6TuKnk/g0WzygDJ0mMqLz0J3HDyexRCqeT+IlrOFyiJ4TwY8modQonk7OIZbCOjsxPUVF8oFmV+6m6qfB'
        b'Gb6inBSkqIKWuhnqKdBkdK31gEjJyhJmm4440JfQxgn9ueMguqlcFV5l5Bx74I5I0Ne7aWTcdxtyMliJPNd2AHrGSZxyPrbk8mGwc5ttmAvQKx6N1ZGv6uAjPYUqcSTq'
        b'uZVPYqcUH/KQAq9BsRhWhKs0UpGMdMGZRbwwHa6JZfhohrjrhVCHPfwsGjtU4nE0NoVznXvtqFKISPLm9zN8ndcIfEkSPB22MIiGubSLKI2QTOyuR+/fCnITIwN7HlSu'
        b'rgyOlYW6bPjtH98yeLy+I2LLLc9t1d6nPd5uC7++YUfBLk1C2tbGW84RsTVzPsr1zk/Jlla4b0meNj4m5fna997r/Hruq7vyv+567J1Np/8872eLI95UffB64zf7jvZX'
        b'/0BRvLo5Ntr78+/FP6vN/5//aN+zydL39bTqBvePVj/9WPjW5nCXH8zpVv12oOveD11i9/VZNR9F+vzNMW9e3oGmvJnrV6W/+efMig/K/7Px47gPbk54bjxx589R//M/'
        b'xTtfO3sso78mZObZr/9y+v6GyLxXX551/vQ3H53Vb/yr4Y9xmUudWvf1ehTc+d5LvTBpSfar//Wvef8y89NjDeDZUOn1cmBMyzRTp0G6tzo5f+Uvmp0WB/0g6OW/Kt64'
        b'nfZzlbvGwcz3tMFzwQHo9wvwiQiQCkq4Kg3ASrxkZreDZpC61/oFRvr7agLxnD8W0z5cwgIvtfwAdkKLeaoYfl1Ii4oLgOI4LCGmoNoixQeTsMLFzcwNqnD3BGjEU+yu'
        b'jm9AoIRGOCNdeFxpZgkUHd5hsYLtygycxsYj4rWZ3ABfLFkgFQKhX4HdWDfDzBjLCahLhfvsvkeMfySF9oJykdSVCEq3Wc24+AZsjxKbA3Uo8hq3xIlYwM7lWrdppANS'
        b'Hw3LJQgaJ/7rK78xXP1s4qo0Y9YxnUGdJt7HCmRud82AM3cCiewPVs20gwHxSUEjl8gljvzlKpFKJkmcJe70cpaw7134984SR6mSvUuG31mZUuLFf7O/XOkvOSuRektY'
        b'rkOI5ZPRKAfkbMQBGbnyAQebYxyQM0824JCYaLQYEhMHVImJKRk6rcGSnZioUf79NWrkRkbHjOx6jpHZl5FdCzMymsbHvcTWxk5/hVPCR940bynNib3zdPgRop63x+GN'
        b'F+Rvk34pthKyMPJ4FK4HR21ekYxlWBqLFXGRCsE1W7aMsKPSwi6nrYPTrlHRsSK7lBAAdAqqPVJspdC1SMSzU1i1lIip+wYbLSX8uJkis/OCbDkOg15wiTB0d0qeJrcR'
        b'SlmRjAilnAilbIhQyjmhlJ2Q2xHKdySjCSW/TWfHKI1ZmWrtIAccyfZGMrtRzG3b3yGYRl2ORW8UaUW2zkgkM1PkP4NX/EYygLhBYkAT8U2gEfWZug1GY5bRl3empZLU'
        b'sXkjmy+brsgdRy9iTNJkW5TYYvQKxxqCMc2NGdqDar3Id1OyjEadKTvLkEoEiRNOU3qWJSOVESiRC3Hma2O7Y1OlDXq25GFmRixcqw4JMFuyiXHZ+BeXGhFHH1bDnw2k'
        b'+RLipHiBOCliLexq55p4Uj9+gxB65thd7cMiLI723ewPzdvEy4Tsi7joyBgJS1AWq5bL8Ow2/cVP9ylMq6mbXb9c+JukwF9qtBHajLSM5I+SDrz6ztfe+VoldFcuL2y6'
        b'1Hip45sN+U0R9wsbC4PLNZcbC2ddPr1wuuDvqLr1o9kaqZnZGVx2l6h8yTKIVJXFWESUhNvEN2ZClxzb1mMtB24ofsWA5XlRgZsJKaF80BqnQrfcgF37NNIRhv9FkMet'
        b'f0AlXiEdRjhXEeFSGYZ5cCQzug0jk2LAcVCvBhxsGiJCiwt7Y/c8RwwvMzKyaWTQIlbjkMM6/JEd5Nz3sIccdluFVnUez72wwqN7+RpLoNqykmr5xoaNCo95Lh0K2FUF'
        b'uO4yzl+2P2oRVOTAA7gD/c5CMlaNI5JymXgVZzWng6BRlUvB/XliEBJGCe/jLajlzEUeCb2qXLyuymFFRcRP8AbYwufeWQoTPnILkQtSrIKKrZJJcMoiFpWQR3tkCsmF'
        b'MpKYJEuAx6FYJeaar+fpaLBm31wldXhWwKtwfYGNki2wrGDheNUg7KUd51G83CHXLhSHTh0PxXdDAx/rIJTJ/WKxiAL9CokghQpJWBz0vYCWQzHDGoaWMo6X4i1TqdUx'
        b'zXEINeVfipoHCTX/8kVhODf3kUH4F2IGwxdW/cuD2S+IMVnj//UQMyWDT8ukM78YVI6aIJNLVkqKheDRkPLiRAfDyg3xoeowcupGBp/h5CZSzFlGChSzLckZelM6dZSc'
        b'x2va4DyMAk+jNuOF/taTjQbazU3LNsXCr577bg3b5utPv8LD2a+wuIRg+k3T810fsp4XhIX5+r/Qo92aKGTNGjM4Zovkcs4WQ2LqNZUheV72KAGyn6/kI4d6zMp+0TWy'
        b'n6/mHkds3j81JpcIY8XkbhSTM9+SDE2vQN9W+wvqX8234Kk1PAx6ljBFCCLyG2TYvrnlmO2C9ptZEwR2MSQotnhKZmqSGBsF42l4ClePizG9sJtio2c8ylq6h90a5Fns'
        b'+hzyhRMkThQf9/KeXolwFYiWeQUtyV/lczycoJvnBl7GOwu34GV2vz5YCIZHZn4xcJdnGIW9jQtplSFCSOYy3sPrh90FtSAsC5r3reUz9skHe/BNgAa4BO22LhKPc5Db'
        b'fSIWO/E0z4vHC/Hu0MD7ENapBFqCY1Dut5KWrp0nbNN/EHZXauqikvCX/vWlimBXCKKYbm7MwBmv809zvAzfk+zyyzrvvnlFY2d85VuKFfMnJ/1MvXpCpN+C33/++d6G'
        b't2sKAoKURX8I/dfWlA/cVld5/bH40+n31V5z1vxM/qP+MwcGBqaP/3if+uB3X61aXLulx3Dq+i7r7PXh7wU0zPpV3aePN0wsm1PVDTFlt6ZeT/4gKeLufX1m2Lzlt3/4'
        b'19qezfv2/nZrzonS+e/W5U4LyXp77sXjez/85UdvPzr7608c1h5esl2zR+NoZmA/znGlLegir3GNB15rTpjZfSd4Qs6qmfl5bMDuEb7e5ucpnmo3sysK5lUUY5dpCeMr'
        b'KABjUdgCqhbAmkQ50JZfV0aSw2ozs+c8oNPPSxWFZZqY7eTdbP1NBKvcEUsSzUw/93vhJQrl/NkpljRXEgqlE8UYsQD72RMPxQviaLphKcoTUl94KOdlAdiYPBSQoXUG'
        b'i8nUcNrMyDxeXYr9UVgexcNHmjqLIN2CZAfd4alGIvp/x38oChMpiZMYc5Gj4IQkSCQkJ8kb2oIu9i6l4MmVh1muErmUBVOz6eVlexkn2FGW4dBnQEaYbcdUvixqktlF'
        b'TZ5D7IX1/Ts79lI91Z69zGBVsmOHYiWKm0nu5NbHo1UGZfOxRiMRjxi0Orv8PFzfJ4HaY8teeE5kKNZh1yXId0vTpEPPg0j+7vMgzGMXaOSffWcEfCWI8PcFdD2Ns23u'
        b'aO1z3//b8c0X4u+glEbirzLWwjg59EO/dhB8e9b/A/g7DSs4qu6OO27KUWALnrYd2s/GYvF6TH1QONkSlsRg2VYsipZ6wAO8soE9jAK3gX3QEMA5wKOTcFl/P+ATmYnx'
        b'VTenot8k+dsFCbte7alsvCCJWHg7KCB188v+O/y0sVrlt4ICkz5M2vW611uv/ptU2Bo2bs7PmjQKM7vuttYJrr4QInDYgKYJ2CbHFo4+0OiDfTb8SV/K0WftChEm6mZi'
        b'3YikD9ZOFljOR4BSnmmBkhy4JiKJrX8ipm0ilBCPrhJt/xTW+kTBRagamRuqgIu7RbOTjmnbDgd15iHLdh+07FnMonnKRGKcNGS5TTIxVTFmZNEkEQu5RbI2XmQ4Jg/R'
        b'Ik8Jv3a1t0meybqhh6rhTBbc8BcnHCb9EpOTWoV/yOTSyOSaR2js1uwMvdk0ZFfieQMZj5p9m2bUHuTnB6NsbNBOtepFY8a+Iyr7hMVtj92WsNtfHRaxISxq6/YYCopD'
        b'Y6MSw+LCN/irQ8N4eWLs9pj1GxI0fz9SHsucuJ9+O0TJnxb7mecRl+9o9guWFayCI7DwucyPPWlXHL0lgocr0IBPeciCVRpocoYrefSKhOI8gXyhM1GRZ9jFL/jNNZPd'
        b'8OZQaRF7IGvioDgD78nhBpzGR/qW77+vMG2h6n4Nr/wmad+r7WQ0HfnBZ2ed7bgYWdV4qbGwMX9WbX/E7YLgs01XOoo7ZD6z32g/1ZSfMyslIGVcSsf0+MIpc7fiwkc9'
        b'p/JmhZGLUgqls8e3yx9r5DyP6YF34JFoL1CM1WKidAL5OZbUSoemmBH2IKx159YwfR9vDFasnj3oJKes4XlLuAYtYoa0ay0WRDG3fTI6wEcpOHlJoVEHpSOi5LFtxZnC'
        b'DJNdZO45aC7BjhIXbjCuYnw+dchkjJNHd+c1ZCSsls8IIxlwfSHsPkWxc/NcuO0X4e8bOxx4T4Je+USowVKNWG/nYTgrOi+Kv88tgBIRAaYmTT4pT6fw+uwX25QtZccf'
        b'dhxK2X1Fu3p//+iUnb0347ktgzaThzljODEW5LATu2wdfUHObqRbiRStK0NrNlPMkqIljzSyU+7btKliVvCFaG1EX0OR25cFbmKg9n/VuUrGRANHMW+GJa45IwKbHdD/'
        b'lXwrPHDlcNIYKsY2wh6z98cxu8RjReiKxmpyua4xNoeL3VDGPa4uHO8zj3sX2+287hgeNwZbeP8he0W4Wrdd57I2KFrQL/zbu1LTbio5viFypBv+dVJ6WrT2zTT/hF8T'
        b'urzztfbK4L98crkxXyv5/vrCWPdv10FfZcc7dwpeOqtoqZ/SUr+dMEdyr/6hsmXNWZbHkwl/em+Sg8frGiXP42ENlqRxgv8QesYi+Ct380gAH0yX+E2WDrP7uM0scY4V'
        b'BDYxCmFprPIE9oznDh1rzXDez9Hf7hxHI+UOncKFi+PJocPTQ3YHOfwQpyTezNjobuiFAgZgy/HSMIZxBFuPZ838waFm8uz9TLxNeHv0PGZClRyvRfkMcvovSym6cB9P'
        b'is3MhiPXpEHk2sDwyoUQR3T2LhKj9xB2aWQDKoZ1iVlGxhDs3P6YA9Jspg9hG+tlxQhse91j9CmGwTE7Kg67Ml6Qs7g+6MEmjSw2dqNGslEjjd2oT/r0FYXpD9Tpr/64'
        b'dvv5H22dsMXT+vv+3g/Nwaf6j3zjwBZJR8qGl3zevtdQPLVM2vH+7+7Nfdqb7tnrtmpu1l+v/DQmpOw7V1aaTnyy6t0rP9v2Zma2TFH81tQLTic3WZzKy30ND7TRDaa9'
        b'b8c2fLc0L7F9v/uv3QuOvxL7eedr4b4Lij1/0e096WD2k1jNn3N+/HFJeuhnHxW9vmHCJ8oF68qUU/U3rkzao0+R/NZ/bqzDNXNH0Tf8tZpv7fqO847Okh+2aAN+s+u7'
        b'yiWdxd/O0Pr9+FdpK1e+80Zgbpe1/6OUtQ4hP6l/I9T1bXx/OU7yft+n/09vfzdYuew7TrHGku/Xve+fX/fzvh2B2eejjvW+5b6zp/nxYZcLSeE//827SdVzlz7ZUPLj'
        b'd9/+tzX9P/mhoWfTVZdP814N6yz7Y5H3uU+mff/NCa9dSUpIjDzU2rAqLu8104E/VGkOfHvcsTe3627OVoZ3Htn2b/+y49K9n/e8Vpi5pzljT6FuR/WDtA/+e6Z/1DfO'
        b'Pnj3l8ZXEyZ+6Bv1X44P/pxb+277jxOuOea+8QvrBOOtm3WXv/+ryx+q2/K2lv3337QOv+wf/9NLLicOHfR/cPlO/BH5X06UTPyw+GTf74+eyy+9++M08+9q5phDmhcs'
        b'WhZw9fNXv7nnpxceet6uajly8t9Nwft+6/qXu5oH3/749p28jfs/3/OtDw/Myfy4/PefZHgFz5195fmfrnx/knM7WTG/zjXVbQU8JC8nESTL2J2AfnjMLW4cVGF+RvpI'
        b'SiBG2qc2cpYONQlTVL4srTwWU8e244n8xJNd/b6JpcQbygOU7KS8QHlAOkcOZ0SKXY51c/w2B2BRZHSsAhuwQFBBhxSvjcdiXsGwDEujGABTFSyLVKgFqtAmJVsumfkP'
        b'noFqXP+xI9Mv7EdhZA5jzDeODY6JiRlZ2tTERI4L4czDzJFKpZJFkhl/k0rZ6aiH1FEuFcb4J/knffu53Jk+SaR/UTry3//3/nUrY90l7J+jxEPGEh3ea6WElZ4TnElS'
        b'XhJvHykrceXv7uzdOGMQgQlEpYmJdtg57v9/TyXGmUNAywZiYCoeE703zx5kSf+EILwKF6AUzuE58vqEqc3RUAznHATXKbLpeFHQ322ZpzBdoZrTIp8FlK52hnWeBf+R'
        b'ueT5Rk9/+duvTTg6WZWiWdUdn5DuG7lC2/n4jaWv//QH+8/r056d27JlVdD1b8699seQiAVbb8wzz/le+oOFJVGftZ70MxnX9z7+1cfHP8mQBztPPnl23gH5wW6r8mb0'
        b'bbfnr/cu+nid78O/LfnPo+Vf++FnJvmEPWn74nt+UXJ4qqHng9+t+FH0f8a9H/TvRR//l2LGTs175ibNOPGQrQKuk4FBz0paSBwth6XcVNApxXt4H05xz5oMj+KZ0+zg'
        b'Vc47svzZeOyTQSPU43XeDXYa8ZIoEMKLcGhlD98weXjIZmDzMp5kS4X2DVGRMb4xWAmPHASlXOoI7dAmRvLPkQIkv80KQRIlrKFQ4zK0xJrZw3sv4V14ZM/AcuCSmHJa'
        b'EEVoU0Eu7pxM2AQdDnAOCp3MjLdPwi64Yt8G7uWyNkphcrjcFwqn8Vqe2KLFLiwjXFngmxOwCE6J4DXVIodCfAD1PCyiJbaFsdgtCksdBDk0QEEAe1q/G4rMc0X8uofV'
        b'POJmE4L72wbnNA1q5XAHa+GKyGBqtmI1hRZUEc9ZVIwtSgS3LbLtUAn3OZ4S+LVmYOnKuWIdf7ZEHixKBDU+VAj+mzggxiZ4+EFtYpw//89j+H7hMyk+pgi1fUS8Nf2f'
        b'g3b/xDeN7IvgUm/Qm21wyTijMI5RJwr/ZHIJAwUWArpzOsUIlbNsLqNZC4zqIUCYOSDL0BkG5OwUZkDBMwkDcopJzAPyVH0KvVM8ZBiQmczGAUVynllnGpAnZ2VlDMj0'
        b'BvOAIo3Qmn4ZtYaD1FpvyLaYB2Qp6cYBWZYxdUCZps+gaGlAlqnNHpAd02cPKLSmFL1+QJauO0pVqHtnvUlvMJm1hhTdgJJHQyn84FiXbTYNjM/MSl2+NFHM96bqD+rN'
        b'AypTuj7NnKhjUcrAOIpq0rV6gy41UXc0ZcApMdFE8V52YuKA0mKwUPAyDHTiYqcbWWhiZE+4G9nZg5E99mVkj1sZ2cORRsZ1jSyhbGSPbBnZE3JG9vSgkd1XMrLQ1MgM'
        b'wMj018gevDIuZ2/sAV4jk76RGZ5xKXtjMYmRZUCMLFNvZKBoZLpqZIk+I0s/GkOGYJNth/MQbP53uB1s8rLPHAevHQ24JybaPts85WdT00b+F1FqQ5ZZzcp0qbEaR3Yh'
        b'KDUrhWRCH7QZGYT+apvqMP5N3zuT+I1m0xG9OX1AmZGVos0wDbjYR4PGtYMCtHsT9W+V+P9QrWGOmufr5Eq5zJHpWJSnhLme/wfl/Smm'
    ))))

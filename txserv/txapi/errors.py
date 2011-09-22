import httplib

ERR_PYTHON_EXCEPTION           = 0
ERR_TRANSACTION_API_ERROR      = 0x10000

ERR_REQUEST_ERROR              = ERR_TRANSACTION_API_ERROR | 0x01000
ERR_ACCOUNT_ERROR              = ERR_TRANSACTION_API_ERROR | 0x02000
ERR_ORDER_ERROR                = ERR_TRANSACTION_API_ERROR | 0x03000
ERR_BITCOIN_ERROR              = ERR_TRANSACTION_API_ERROR | 0x04000

ERR_UNSUPPORTED_REQUEST_METHOD = ERR_REQUEST_ERROR | 0x00001
ERR_UNSUPPORTED_VERSION        = ERR_REQUEST_ERROR | 0x00002
ERR_INVALID_API_KEY            = ERR_REQUEST_ERROR | 0x00003
ERR_INVALID_NONCE              = ERR_REQUEST_ERROR | 0x00004
ERR_INVALID_SIGNATURE          = ERR_REQUEST_ERROR | 0x00005
ERR_INVALID_TIMESTAMP          = ERR_REQUEST_ERROR | 0x00006
ERR_INVALID_REQUEST            = ERR_REQUEST_ERROR | 0x00007
ERR_UNAUTHORIZED_REQUEST       = ERR_REQUEST_ERROR | 0x00008
ERR_UNAUTHORIZED_IP_ADDRESS    = ERR_REQUEST_ERROR | 0x00009
ERR_INVALID_ARGUMENT           = ERR_REQUEST_ERROR | 0x0000A

ERR_USERNAME_TAKEN             = ERR_ACCOUNT_ERROR | 0x00001
ERR_ACCOUNT_VALIDATION         = ERR_ACCOUNT_ERROR | 0x00002
ERR_AUTHENTICATION_FAILED      = ERR_ACCOUNT_ERROR | 0x00003

ERR_INVALID_BALANCE            = ERR_ORDER_ERROR | 0x00001
ERR_INVALID_CURRENCY           = ERR_ORDER_ERROR | 0x00002
ERR_INSUFFICIENT_FUNDS         = ERR_ORDER_ERROR | 0x00003
ERR_NEGATIVE_AMOUNT            = ERR_ORDER_ERROR | 0x00004
ERR_INVALID_ORDER              = ERR_ORDER_ERROR | 0x00005
ERR_ORDER_INTEGRITY            = ERR_ORDER_ERROR | 0x00006

ERR_BITCOIN_CONNECTION         = ERR_BITCOIN_ERROR | 0x00001

class TransactionAPIError(Exception):
    def __init__(self, code=ERR_TRANSACTION_API_ERROR, text=None, http_status_code=httplib.INTERNAL_SERVER_ERROR, log=False):
        self.code = code
        self.text = text
        self.http_status_code = http_status_code
        self.log = log
    
    def __str__(self):
        return "%s (%d)" % (self.text, self.code)
    
    def get_http_status_response(self):
        return "%d %s" % (self.http_status_code, httplib.responses[self.http_status_code])

class RequestError(TransactionAPIError):
    def __init__(self, *args, **kwargs):
        super(RequestError, self).__init__(*args, **kwargs)

class AccountError(TransactionAPIError):
    def __init__(self, *args, **kwargs):
        super(AccountError, self).__init__(*args, **kwargs)

class OrderError(TransactionAPIError):
    def __init__(self, *args, **kwargs):
        super(OrderError, self).__init__(*args, **kwargs)

class BitcoinError(TransactionAPIError):
    def __init__(self, *args, **kwargs):
        super(BitcoinError, self).__init__(*args, **kwargs)

class UnsupportedRequestMethodError(RequestError):
    def __init__(self, method_used):
        super(UnsupportedRequestMethodError, self).__init__(
            ERR_UNSUPPORTED_REQUEST_METHOD,
            "Unsupported request method",
            httplib.METHOD_NOT_ALLOWED)

class UnsupportedVersionError(RequestError):
    def __init__(self):
        super(UnsupportedVersionError, self).__init__(
            ERR_UNSUPPORTED_VERSION,
            "Unsupported protocol version",
            httplib.NOT_IMPLEMENTED)

class InvalidAPIKeyError(RequestError):
    def __init__(self):
        super(InvalidAPIKeyError, self).__init__(
            ERR_INVALID_API_KEY,
            "Invalid API key",
            httplib.BAD_REQUEST)

class InvalidNonceError(RequestError):
    def __init__(self):
        super(InvalidNonceError, self).__init__(
            ERR_INVALID_NONCE,
            "Invalid nonce",
            httplib.BAD_REQUEST)

class InvalidSignatureError(RequestError):
    def __init__(self):
        super(InvalidSignatureError, self).__init__(
            ERR_INVALID_SIGNATURE,
            "Invalid signature",
            httplib.BAD_REQUEST)
            
class InvalidTimestampError(RequestError):
    def __init__(self):
        super(InvalidTimestampError, self).__init__(
            ERR_INVALID_TIMESTAMP,
            "Invalid timestamp",
            httplib.BAD_REQUEST)
            
class InvalidRequestError(RequestError):
    def __init__(self):
        super(InvalidRequestError, self).__init__(
            ERR_INVALID_REQUEST,
            "Invalid request",
            httplib.BAD_REQUEST)

class UnauthorizedRequestError(RequestError):
    def __init__(self):
        super(UnauthorizedRequestError, self).__init__(
            ERR_UNAUTHORIZED_REQUEST,
            "Unauthorized request",
            httplib.FORBIDDEN)

class UnauthorizedIPAddressError(RequestError):
    def __init__(self, ip):
        super(UnauthorizedIPAddressError, self).__init__(
            ERR_UNAUTHORIZED_IP_ADDRESS,
            "Unauthorized IP address",
            httplib.FORBIDDEN)

class InvalidArgumentError(RequestError):
    def __init__(self):
        super(InvalidArgumentError, self).__init__(
            ERR_INVALID_ARGUMENT,
            "Invalid argument",
            httplib.BAD_REQUEST)

class UsernameTakenError(AccountError):
    def __init__(self, username):
        super(UsernameTakenError, self).__init__(
            ERR_USERNAME_TAKEN,
            "Username already taken",
            httplib.CONFLICT)

class AccountValidationError(AccountError):
    def __init__(self, username, password, email):
        super(AccountValidationError, self).__init__(
            ERR_ACCOUNT_VALIDATION,
            "Account validation failed",
            httplib.BAD_REQUEST)

class AuthenticationFailedError(AccountError):
    def __init__(self):
        super(AuthenticationFailedError, self).__init__(
            ERR_AUTHENTICATION_FAILED,
            "Authentication failed",
            httplib.FORBIDDEN)
            
class InvalidBalanceForAccountError(OrderError):
    def __init__(self):
        super(InvalidBalanceForAccountError, self).__init__(
            ERR_INVALID_BALANCE,
            "Invalid balance for account",
            httplib.BAD_REQUEST)

class InvalidCurrencyError(OrderError):
    def __init__(self):
        super(InvalidCurrencyError, self).__init__(
            ERR_INVALID_CURRENCY,
            "Invalid currency code",
            httplib.BAD_REQUEST)

class InsufficientFundsError(OrderError):
    def __init__(self):
        super(InsufficientFundsError, self).__init__(
            ERR_INSUFFICIENT_FUNDS,
            "Insufficient funds on account",
            httplib.FORBIDDEN)
            
class NegativeAmountError(OrderError):
    def __init__(self):
        super(NegativeAmountError, self).__init__(
            ERR_NEGATIVE_AMOUNT,
            "Negative amounts are not allowed",
            httplib.FORBIDDEN)

class InvalidOrderError(OrderError):
    def __init__(self):
        super(InvalidOrderError, self).__init__(
            ERR_INVALID_ORDER,
            "Invalid order",
            httplib.FORBIDDEN)

class OrderIntegrityError(OrderError):
    def __init__(self):
        super(OrderIntegrityError, self).__init__(
            ERR_ORDER_INTEGRITY,
            "Order integrity error",
            httplib.FORBIDDEN)

class BitcoinConnectionError(BitcoinError):
    def __init__(self):
        super(BitcoinConnectionError, self).__init__(
            ERR_BITCOIN_CONNECTION,
            "Bitcoin client error, please try again later",
            httplib.INTERNAL_SERVER_ERROR)

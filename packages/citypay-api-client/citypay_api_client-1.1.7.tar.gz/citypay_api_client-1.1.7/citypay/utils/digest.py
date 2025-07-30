import hashlib
import base64


def validate_digest(auth_response, licence_key):

    string_to_convert = auth_response.authcode \
                        + str(auth_response.amount) \
                        + auth_response.result_code \
                        + str(auth_response.merchantid) \
                        + str(auth_response.transno) \
                        + auth_response.identifier \
                        + licence_key

    base64_string = base64.b64encode(hashlib.sha256(string_to_convert.encode('utf-8')).digest()).decode()

    return auth_response.sha256 == base64_string

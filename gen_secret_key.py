from base64 import b64encode
from secrets import token_bytes

print(b64encode(token_bytes(32)).decode())

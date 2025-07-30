# Omniblack Secret

Classes for safer handling of secrets.
We use libsodium to store secrets in memory
that is protected by guard pages, a canary, and is set to
readonly when the library is not reading from it.
These protections should help mitigate exploits in other parts
of the program allow for arbitrary reads of memory, and should
reduce the risk of buffer overflows and similar memory writing
bugs from corrupting the secret.

Further more `Secret` instance's repr will not reveal the secret
so if a secret object is accidentally logged the secret value
will not be exposed, and the value is stored in a C slot not
in a python dict or slot so introspection tools like `rich.inspect`
will not reveal the secret.

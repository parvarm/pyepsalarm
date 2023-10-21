# pyepsalarm

Python library to interface with EPS systems, operated by Homiris for instance.

Example use:

```
from pyepsalarm import EPS

token = "MYTOKEN"
username = "123456789"
password = "mypassword+"

eps = EPS(token, username, password)

eps.get_status()
eps.arm_night(silent=True)
eps.get_status()
eps.disarm()
```
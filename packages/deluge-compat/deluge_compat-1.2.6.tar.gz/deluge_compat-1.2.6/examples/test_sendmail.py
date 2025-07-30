from deluge_compat import List, Map
from deluge_compat.functions import sendmail


def deluge_script():
    response = Map()
    sendmail(
        **{"from": "test@example.com"},
        **{"to": "admin@example.com"},
        **{"subject": "Test Email"},
        **{"message": "Hello World"},
    )
    response.put("action", "reply")
    response.put("replies", List(["Email sent!"]))
    return response


if __name__ == "__main__":
    result = deluge_script()
    if result is not None:
        print(result)

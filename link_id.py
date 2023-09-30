import uuid

import crockford32 as cr32


def get_link_id():
    link_id = uuid.uuid4()
    link_id = str(link_id)[0:8] + str(link_id)[19:23]
    link_id = cr32.encode(link_id) # , True
    return link_id
    #return "6GW3GDB374RK6RB26WS0="
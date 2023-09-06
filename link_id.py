import uuid

def get_link_id():
    link_id = uuid.uuid4()
    link_id = str(link_id)[0:8] + str(link_id)[19:23]
    print(type(link_id))
    exit()
    link_id = cr32.encode(link_id, checksum=True)
    return link_id


def get_lid_temp():
    return str(uuid.uuid4())[0:8] 

if __name__ == "__main__":
    #for i in range(0,8):
    #    print(get_link_id())

    #print(cr32.encode('dsds'))
    print(get_lid_temp())


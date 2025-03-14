import time

try:
    import usocket as socket
except:
    import socket
try:
    import ustruct as struct
except:
    import struct

# The NTP host can be configured at runtime by doing: ntptime.host = 'myhost.org'
host = "pool.ntp.org"
# The NTP socket timeout can be configured at runtime by doing: ntptime.timeout = 2
timeout = 1


def get_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(timeout)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]

    EPOCH_YEAR = time.gmtime(0)[0]
    if EPOCH_YEAR == 2000:
        # (date(2000, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 3155673600
    elif EPOCH_YEAR == 1970:
        # (date(1970, 1, 1) - date(1900, 1, 1)).days * 24*60*60
        NTP_DELTA = 2208988800
    else:
        raise Exception("Unsupported epoch: {}".format(EPOCH_YEAR))

    return val - NTP_DELTA


# There's currently no timezone support in MicroPython, and the RTC is set in UTC time.
def settime():
    t = get_time()
    import machine

    tm = time.gmtime(t)
    
    # Calculates time in March and October for the year to change clocks for daylight savings time
    mar_dst = time.mktime((tm[0], 3, (31 - (int(5 * tm[0]/4 + 4)) % 7), 1, 0, 0, 0, 0, 0))
    oct_dst = time.mktime((tm[0], 10, (31 - (int(5 * tm[0]/4 + 1)) % 7), 1, 0, 0, 0, 0, 0))
    
    # If after March change time and before October change time
    if mar_dst < t < oct_dst:               
        t = t + 3600 # Add one hour
        tm = time.gmtime(t)
    
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3], tm[4], tm[5], 0))
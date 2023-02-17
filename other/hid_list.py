import hid
# Check all  usb device
for d in hid.enumerate(0, 0):
    keys = d.keys()
    #keys.sort()
    for key in keys:
        print ("%s : %s" % (key, d[key]))
    print ("")
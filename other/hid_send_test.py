import hid
import time

vendor_ID = 1305
product_ID = 8216

# 初期化
h = hid.device()
h.open(vendor_ID, product_ID)

print ("Manufacturer: %s" % h.get_manufacturer_string())
print ("Product: %s" % h.get_product_string())
print ("Serial No: %s" % h.get_serial_number_string())

send_data = [0] * 9
send_data[1] = 0x01
# send_data = 0x00F1000000000000
print(send_data)
# h.send_feature_report(send_data)
h.write(send_data)

# time.sleep(1)
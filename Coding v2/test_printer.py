from escpos.printer import Usb
# 28e9:0289
# Adapt to your needs
p = Usb(0x28e9, 0x0289, 0, 0,0x81,3, width=384)
p.set(align='center', flip=True, invert=True)
# p.image("/home/arendjan/Downloads/huren/93261089.png")
p.text("Hello World\n")
p.cut()
# # Some software barcodes
# p.barcode("Hello", "code128", width=2, force_software="bitImageRaster")
# p.text("Hello World\n", align='center')
# p.barcode("1234", "code39", width=2, force_software=True)
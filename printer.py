from escpos.printer import Usb
from escpos.escpos import EscposIO
import logging
import time
import usb.core

logger = logging.getLogger(__name__)

def create_printer():
    return Usb(
        idVendor=0x28e9,
        idProduct=0x0289,
        in_ep=0x81,
        out_ep=0x03,
        width=384,
    )

def recover_printer(printer):
    logger.info("Printer error. Starting printer recovery...")

    # ---------------------------------------------------------
    # Attempt 1: close and reopen the existing printer object
    # ---------------------------------------------------------
    logger.info("Recovery attempt 1: reopening existing USB object.")

    try:
        try:
            printer.close()
        except Exception:
            pass

        time.sleep(30)

        printer.open()

        logger.info("Recovery attempt 1 succeeded.")
        return printer

    except Exception:
        logger.exception("Recovery attempt 1 failed.")

    # ---------------------------------------------------------
    # Attempt 2: create a completely new printer object
    # ---------------------------------------------------------
    logger.info("Recovery attempt 2: creating new USB object.")

    try:
        time.sleep(60)

        # Ask PyUSB to rediscover the device
        device = usb.core.find(
            idVendor=0x28e9,
            idProduct=0x0289
        )

        if device is None:
            raise RuntimeError("USB printer cannot be found by PyUSB.")

        logger.info("PyUSB found printer: %s", device)

        # Create a completely new python-escpos object
        new_printer = create_printer()

        logger.info("New USB printer object created.")

        return new_printer

    except Exception:
        logger.exception("Recovery attempt 2 failed.")

    # ---------------------------------------------------------
    # Both attempts failed
    # ---------------------------------------------------------
    logger.error("All printer recovery attempts failed.")

    return None


def print_receipt(printer, receipt_template, logo):
    with EscposIO(printer, autoclose=False) as p:

        if logo:
            p.set(align="center")
            p.printer.image(logo)

        p.writelines("\n\n")
        for line in receipt_template.splitlines():
            p.writelines(line + "\n")
            time.sleep(1)

        if logo:
            p.set(align="center")
            p.printer.image(logo)
    time.sleep(15)
    logger.info("Receipt print job completed.")

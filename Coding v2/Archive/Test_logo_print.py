from escpos.printer import Usb
from PIL import Image
import logging

# Initialize logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Initialize the printer
try:
    p = Usb(0x28e9, 0x0289, 0, 0, 0x81, 3, width=576) # width is either 384 pixels or 576
except Exception as e:
    logging.error(f"Error initializing printer: {e}")
    exit(1)

def print_logo():
    try:
        # Load the logo
        logo = Image.open("C:/Users/20192336/OneDrive - TU Eindhoven/ID MASTER/M2.2/W13-15 Final design folder/WS-logo-black.bmp")
        p.set(align='center')
        p.image(logo)
        p.text("\n")  # Add some spacing after the logo
        logging.info("Logo printed successfully.")
    except Exception as e:
        logging.error(f"Error while printing logo: {e}")

# Example of integrating logo printing with the receipt
def print_receipt_with_logo():
    try:
        print_logo()  # Print the logo at the top
        
        # Print additional text
        p.text("Welcome to World Servants!\n")
        p.text("Thank you for your reflection.\n")
        p.cut()  # Cut the paper after printing
        logging.info("Receipt printed successfully.")
    except Exception as e:
        logging.error(f"Error while printing receipt: {e}")

if __name__ == "__main__":
    print_receipt_with_logo()

from smartcard.System import readers
from smartcard.Exceptions import NoCardException
import pyautogui
import time
import re
import tkinter as tk
from tkinter import messagebox
import pyperclip
import logging


logging.basicConfig(
    filename="nfc_reader.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def show_popup(title, msg):
    root = tk.Tk()
    root.withdraw()
    try:
        messagebox.showinfo(title, msg)
    except:
        pass
    root.destroy()


def read_page(connection, page):
    cmd = [0xFF, 0xB0, 0x00, page, 0x04]
    try:
        data, sw1, sw2 = connection.transmit(cmd)
        if sw1 == 0x90:
            return bytes(data)
    except:
        return None
    return None


def read_ndef_text(connection):
    raw = b""
    for page in range(5, 12):
        block = read_page(connection, page)
        if block:
            raw += block

    text = raw.decode("latin-1", errors="ignore")
    match = re.search(r"en(\d{20})", text)
    return match.group(1) if match else None


def main():
    print("?? NFC Reader Service Started")

    last_uid = None
    last_scan_time = 0
    last_status = ""     # Track message state
    reader = None

    while True:
        try:
            # -------------------------------------------------
            # CHECK READER
            # -------------------------------------------------
            rlist = readers()
            if not rlist:
                if last_status != "no_reader":
                    print("? No reader detected... waiting...")
                    last_status = "no_reader"
                time.sleep(1)
                continue

            # Reader connected
            if reader != rlist[0]:
                reader = rlist[0]
                print("? Reader Connected:", reader)
                last_status = "reader_connected"

            # -------------------------------------------------
            # WAIT FOR CARD
            # -------------------------------------------------
            try:
                connection = reader.createConnection()
                connection.connect()
            except:
                if last_status != "no_card":
                    print("?? Waiting for card...")
                    last_status = "no_card"
                time.sleep(0.5)
                continue

            # Card detected
            if last_status != "card_present":
                print("?? Card detected.")
                last_status = "card_present"

            # -------------------------------------------------
            # READ UID
            # -------------------------------------------------
            try:
                get_uid = [0xFF, 0xCA, 0x00, 0x00, 0x00]
                data, sw1, sw2 = connection.transmit(get_uid)
            except:
                continue

            if sw1 != 0x90:
                continue

            uid = ":".join([format(x, "02X") for x in data])
            print("?? UID:", uid)

            # -------------------------------------------------
            # DUPLICATE CHECK
            # -------------------------------------------------
            now = time.time()
            if uid == last_uid and now - last_scan_time < 1:
                show_popup("Duplicate Scan", "Same tag detected again.")
                continue

            last_uid = uid
            last_scan_time = now

            # -------------------------------------------------
            # NDEF READ
            # -------------------------------------------------
            serial = read_ndef_text(connection)
            if not serial:
                continue

            print("?? NFC Text:", serial)

            # -------------------------------------------------
            # SEND TO ACTIVE WINDOW
            # -------------------------------------------------
            payload = f"{uid};{serial}"
            pyperclip.copy(payload)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")

            print("? SENT:", payload)
            logging.info(f"Sent: {payload}")

            time.sleep(1.5)

        except KeyboardInterrupt:
            print("?? Stopped by user")
            break

        except Exception as e:
            print("? Unexpected Error:", e)
            logging.error(f"Unexpected error: {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()

"""
Test mtp_dialog for tkinter

Author:  Heribert Füchtenhans
Version: 2026.09.17
OS:      Windows/Linux
"""

import os
import sys
import tkinter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mtp.dialog  # noqa: I001


# ----------------------------------------------------------------------
if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("mtp_dialogs")
    adir = mtp.dialog.AskDirectory(root, "Test ask_directory", ("Alls well", "Don't do it"))
    print(adir.answer)

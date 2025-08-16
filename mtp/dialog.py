"""
A module with MTP relevant dialogs for tkinter

Author:  Heribert Füchtenhans

Version: 2025.6.29

Requirements:
    - Python modules
        - tkinter

The module contains the following classes:

- 'AskDirectory' - Class to select a directory on an MTP device

Examples:
    >>> from mtp import dialog
    >>> root = tkinter.Tk()
    >>> root.title("mtp_dialogs")
    >>> adir = dialog.AskDirectory(root, "Test ask_directory", ("Alls well", "Don't do it"))
"""

import contextlib
from dataclasses import dataclass
import platform
import tkinter
import tkinter.simpledialog
from tkinter import ttk
from tkinter.ttk import Button
from tkinter.ttk import Frame
from typing import override

import mtp.win_access
import mtp.linux_access

if platform.system() == "windows":
    from . import win_access as access
else:
    from . import linux_access as access

SMARTPHONE_ICON = """\
R0lGODdhDgAUAOeCAA0UJSgnJyoqKTExMRA4eABFoj08PT09PAZNsT5KZ05NTExPWyVYuwxg1AFj
4gBl6CtdwFhYWQBn7FBZehZj3ABq8ihhzgxn8ABr9QBs+F1dXQBt+QJt+QBu+wBv/Stl1gFv+xVq
7g9s9hxp62FhYDllyR1s6hFv9i5w7Uxswjdy6lVutz9y5hWE6gyG+xuE+3R0dXR2gXl6e3t7e3t/
lWCD4D2P8omJiTua+YKMrpGRkYuXxZiYmIab2Z6hrpihxaKiopez56+wtoa556yyzbOzs7Kzt7K0
u7S2wMDBw8DE1rzN8L7O7r7P7cvO2s/Pz8LS7tLS0sjU79PT09XV1dXW3tfX19vb29vb3tjc49rf
6Nbh9d/g4dji9eHh4eLi4trj9Nzk9Nzl9d3l9eXl5ebm5ufn5+Pp9uvr6+vv+O/v7/Ly8vDz+vPz
8/T09PT2+/b29vX2/PX3+/X3/PX3/ff39/j4+Pf5/Pn5+fr5+vn6/Pr6+vr7/Pz8/Pz8/f39/f39
/v7+/v//////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////ywAAAAADgAUAAAI0gADCRwY
yM8dPQQTCpwTpskZQAoHyhkDJUiahIIyCqLTZQkTKRAFrrlihcqULFvEgAnDR2CdGwEGaIggQ8sb
NnFCrolRAAEDCCu4/PkTMpAdGhI6gADBAovCPj4evMDhQkWViEgc2BjSAoWTPwqPUBjRo0YIJWAT
CvmQ4YKICkT6KDRiwYNdDD/2YExSwq6HDTvyYHySgsMJEw1y4FF4ZQKBBAsAwLCjsAwJBQcMCOCx
OCEcIDN0FImiRm7CP2vMkPHyBQ2ctAP71HHTBs4e2AIDAgA7
"""

# ------------------------------------------------------------------------------------------------


@dataclass
class _TreeEntry:
    """Class for keepeing the entries in the tree"""

    dev: access.PortableDevice
    content: access.PortableDeviceContent | None
    child_treeids: list[str]
    content_loaded: bool


class AskDirectory(tkinter.simpledialog.Dialog):
    """Select a wpd device and directory.

    Attributes:
        answer: The MTP path to the selected directory
        wpd_device: The PortableDevice that was selected

    Exceptions:
        IOError: exceptions if something went wrong
    """

    def __init__(
        self,
        parent: tkinter.Tk,
        title: str,
        buttons: tuple[str, str] = ("OK", "Cancel"),
    ) -> None:
        """Initializes the class and shows the directory dialog.

        Args:
            parent: The tkinter parent
            title: The windows title
            buttons: A tuple with the text for the OK and cancel button to chnage them
                     for other languages.
        """
        self._parent: tkinter.Tk = parent
        self._dialog_title: str = title
        self._tree: ttk.Treeview
        self._smartphone_icon: tkinter.PhotoImage = tkinter.PhotoImage(data=SMARTPHONE_ICON)
        self._buttons: tuple[str, str] = buttons
        self._tree_entries: dict[str, _TreeEntry] = {}
        # external variables
        self.answer: str = ""
        self.wpd_device: access.PortableDevice | None = None
        tkinter.simpledialog.Dialog.__init__(self, parent, title=title)
        self.update_idletasks()

    @override
    def buttonbox(self) -> None:
        """Create own buttons"""
        box: Frame = ttk.Frame(master=self)
        box.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        but1: Button = ttk.Button(master=box, text=self._buttons[1], command=self.cancel)
        but1.pack(side=tkinter.RIGHT, padx=5, pady=5)
        but2: Button = ttk.Button(master=box, text=self._buttons[0], command=self._on_ok, default=tkinter.ACTIVE)
        but2.pack(side=tkinter.RIGHT, padx=5, pady=5)
        but2.focus_set()
        _ = but2.bind("<Return>", self.ok)

    @override
    def body(self, master: tkinter.Frame) -> None:
        """Create body"""
        box: Frame = ttk.Frame(master=self)
        box.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=5, pady=5)
        self._tree = ttk.Treeview(master=box, height=20, show="tree")
        _ = self._tree.column("#0", width=500)
        _ = self._tree.bind("<<TreeviewOpen>>", self._on_treeselect)
        # adding data, get devices
        for dev in access.get_portable_devices():
            if devicename := dev.devicename:
                treeid: str = self._tree.insert(
                    parent="",
                    index=tkinter.END,
                    text=devicename,
                    open=False,
                    image=self._smartphone_icon,
                )
                self._tree_entries[treeid] = _TreeEntry(dev, content=None, child_treeids=[], content_loaded=False)
                _ = self.config(cursor="watch")
                self.update_idletasks()
                self._process_directory(insert_after_id=treeid)
                _ = self.config(cursor="")
        # place the Treeview widget on the root window
        self._tree.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

    def _process_directory(self, insert_after_id: str) -> None:
        """Insert directory listing until depth is 0"""
        treeentry: _TreeEntry = self._tree_entries[insert_after_id]
        cont: list[mtp.win_access.PortableDeviceContent | mtp.linux_access.PortableDeviceContent] = (
            list(treeentry.content.get_children())
            if treeentry.content is not None
            else list(treeentry.dev.get_content())
        )
        if len(cont) == 0:  # no children
            return
        for child in cont:
            if child.content_type not in (
                access.WPD_CONTENT_TYPE_STORAGE,
                access.WPD_CONTENT_TYPE_DIRECTORY,
            ):
                continue
            with contextlib.suppress(tkinter.TclError):
                treeid: str = self._tree.insert(
                    parent=insert_after_id,
                    index=tkinter.END,
                    text=child.name,
                    open=False,
                )
                self._tree_entries[treeid] = _TreeEntry(
                    dev=treeentry.dev, content=child, child_treeids=[], content_loaded=False
                )
                treeentry.child_treeids.append(treeid)
        self._tree_entries[insert_after_id].content_loaded = True

    def _on_treeselect(self, _: tkinter.Event) -> None:
        """Will be called on very selection"""
        treeid: str = self._tree.focus()
        status: bool = self._tree.item(treeid, "open")
        if not status:
            __ = self.config(cursor="watch")
            self.update_idletasks()
            for c_id in self._tree_entries[treeid].child_treeids:
                if not self._tree_entries[c_id].content_loaded:
                    self._process_directory(insert_after_id=c_id)
            __ = self.config(cursor="")
            self._tree.item(treeid, open=True)
        else:
            self._tree.item(treeid, open=False)

    def _on_ok(self) -> None:
        """OK Button"""
        self.withdraw()
        self.update_idletasks()
        treeid: str = self._tree.focus()
        if treeid == "":
            self.cancel()
        else:
            cont: mtp.win_access.PortableDeviceContent | mtp.linux_access.PortableDeviceContent | None = (
                self._tree_entries[treeid].content
            )
            if cont is None:
                self.cancel()
                return
            self.answer = cont.full_filename
            self.wpd_device = self._tree_entries[treeid].dev
            try:
                self.apply()
            finally:
                self.cancel()

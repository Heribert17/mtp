#!/usr/bin/env python
#
# A Ctypes wrapper to LibMTP
# Developed by: Nick Devito (nick@nick125.com)
# (c) 2008 Nick Devito
# Released under the GPLv3 or later.
#

# Renamed and modified for my MTP project by Heribert Füchtenhans
# Attention: Only those function I needed for MTP are modfied
#    to work with python version 3.x
# Version: 2025.6.26


"""
PyMTP is a pythonic wrapper around libmtp, making it a bit more
friendly to use in python

Example Usage (or see examples/):
        >>> import pymtp
        >>> mtp = pymtp.MTP()
        >>> mtp.connect()
        PTP: Opening session
        >>> print mtp.get_devicename()
        Device name
        >>> mtp.disconnect()
        PTP: Closing session
        >>>
"""

#pyright: basic

from __future__ import annotations
from typing import Any, override

__VERSION__ = "0.0.6"
__VERSION_MACRO__ = 5
__VERSION_MINOR__ = 0
__VERSION_MAJOR__ = 0
__VERSION_TUPLE__ = (__VERSION_MAJOR__, __VERSION_MINOR__, __VERSION_MACRO__)
__AUTHOR__ = "Nick Devito (nick@nick125.com)"
__LICENSE__ = "GPL-3"
__DEBUG__ = 1

import os
import ctypes
import ctypes.util


# NOTE: This code *may* work on windows, I don't have a win32 system to test
# this on.
_module_path = ctypes.util.find_library("mtp")
_libmtp = ctypes.CDLL(_module_path)


# ----------
# Error Definitions
# ----------
class NoDeviceConnected(Exception):
    """
    Raised when there isn't a device connected to the USB bus
    """

    pass


class AlreadyConnected(Exception):
    """
    Raised when we're already connected to a device and there is
    an attempt to connect
    """

    pass


class UnsupportedCommand(Exception):
    """
    Raised when the connected device does not support the command
    issued
    """

    pass


class CommandFailed(Exception):
    """
    Raised when the connected device returned an error when trying
    to execute a command
    """

    pass


class NotConnected(Exception):
    """
    Raised when a command is called and the device is not connected
    """

    pass


class ObjectNotFound(Exception):
    """
    Raised when a command tries to get an object that doesn't exist
    """

    pass


# ----------
# End Error Definitions
# ----------

# ----------
# Data Model Definitions
# ----------


class LIBMTP_Error(ctypes.Structure):
    """
    LIBMTP_Error
    Contains the ctypes structure for LIBMTP_error_t
    """

    @override
    def __repr__(self) -> str:
        return self.errornumber


LIBMTP_Error._fields_ = [
    ("errornumber", ctypes.c_int),
    ("error_text", ctypes.c_char_p),
    ("next", ctypes.POINTER(LIBMTP_Error)),
]


class LIBMTP_DeviceStorage(ctypes.Structure):
    """
    LIBMTP_DeviceStorage
    Contains the ctypes structure for LIBMTP_devicestorage_t
    """

    @override
    def __repr__(self) -> str:
        return self.id


LIBMTP_DeviceStorage._fields_ = [
    ("id", ctypes.c_uint32),
    ("StorageType", ctypes.c_uint16),
    ("FilesystemType", ctypes.c_uint16),
    ("AccessCapability", ctypes.c_uint16),
    ("MaxCapacity", ctypes.c_uint64),
    ("FreeSpaceInBytes", ctypes.c_uint64),
    ("FreeSpaceInObjects", ctypes.c_uint64),
    ("StorageDescription", ctypes.c_char_p),
    ("VolumeIdentifier", ctypes.c_char_p),
    ("next", ctypes.POINTER(LIBMTP_DeviceStorage)),
    ("prev", ctypes.POINTER(LIBMTP_DeviceStorage)),
]


class LIBMTP_DeviceEntry(ctypes.Structure):
    """
    LIBMTP_DeviceEntry
    Contains the ctypes structure for LIBMTP_device_entry_t
    """

    @override
    def __repr__(self) -> str:
        return self.vendor


LIBMTP_DeviceEntry._fields_ = [
    ("vendor", ctypes.c_char_p),
    ("vendor_id", ctypes.c_uint16),
    ("product", ctypes.c_char_p),
    ("product_id", ctypes.c_uint16),
    ("device_flags", ctypes.c_uint32),
]


class LIBMTP_RawDevice(ctypes.Structure):
    """
    LIBMTP_RawDevice
    Contains the ctypes structure for LIBMTP_raw_device_t
    """

    @override
    def __repr__(self) -> str:
        return self.device_entry


LIBMTP_RawDevice._fields_ = [
    ("device_entry", LIBMTP_DeviceEntry),
    ("bus_location", ctypes.c_uint32),
    ("devnum", ctypes.c_uint8),
]


class LIBMTP_MTPDevice(ctypes.Structure):
    """
    LIBMTP_MTPDevice
    Contains the ctypes structure for LIBMTP_mtpdevice_t
    """

    @override
    def __repr__(self) -> str:
        return self.interface_number


LIBMTP_MTPDevice._fields_ = [
    ("interface_number", ctypes.c_uint8),
    ("params", ctypes.c_void_p),
    ("usbinfo", ctypes.c_void_p),
    ("storage", ctypes.POINTER(LIBMTP_DeviceStorage)),
    ("errorstack", ctypes.POINTER(LIBMTP_Error)),
    ("maximum_battery_level", ctypes.c_uint8),
    ("default_music_folder", ctypes.c_uint32),
    ("default_playlist_folder", ctypes.c_uint32),
    ("default_picture_folder", ctypes.c_uint32),
    ("default_video_folder", ctypes.c_uint32),
    ("default_organizer_folder", ctypes.c_uint32),
    ("default_zencast_folder", ctypes.c_uint32),
    ("default_album_folder", ctypes.c_uint32),
    ("default_text_folder", ctypes.c_uint32),
    ("cd", ctypes.c_void_p),
    ("next", ctypes.POINTER(LIBMTP_MTPDevice)),
]


class LIBMTP_File(ctypes.Structure):
    """
    LIBMTP_File
    Contains the ctypes structure for LIBMTP_file_t
    """

    @override
    def __repr__(self):
        return "%s (%s)" % (self.filename, self.item_id)


LIBMTP_File._fields_ = [
    ("item_id", ctypes.c_uint32),
    ("parent_id", ctypes.c_uint32),
    ("storage_id", ctypes.c_uint32),
    ("filename", ctypes.c_char_p),
    ("filesize", ctypes.c_uint64),
    ("modificationdate", ctypes.c_uint64),
    ("filetype", ctypes.c_int),  # LIBMTP_filetype_t enum
    ("next", ctypes.POINTER(LIBMTP_File)),
]


class LIBMTP_Track(ctypes.Structure):
    """
    LIBMTP_Track
    Contains the ctypes structure for LIBMTP_track_t
    """

    @override
    def __repr__(self):
        return "%s - %s (%s)" % (self.artist, self.title, self.item_id)


LIBMTP_Track._fields_ = [
    ("item_id", ctypes.c_uint32),
    ("parent_id", ctypes.c_uint32),
    ("storage_id", ctypes.c_uint32),
    ("title", ctypes.c_char_p),
    ("artist", ctypes.c_char_p),
    ("composer", ctypes.c_char_p),
    ("genre", ctypes.c_char_p),
    ("album", ctypes.c_char_p),
    ("date", ctypes.c_char_p),
    ("filename", ctypes.c_char_p),
    ("tracknumber", ctypes.c_uint16),
    ("duration", ctypes.c_uint32),
    ("samplerate", ctypes.c_uint32),
    ("nochannels", ctypes.c_uint16),
    ("wavecodec", ctypes.c_uint32),
    ("bitrate", ctypes.c_uint32),
    ("bitratetype", ctypes.c_uint16),
    ("rating", ctypes.c_uint16),
    ("usecount", ctypes.c_uint32),
    ("filesize", ctypes.c_uint64),
    ("modificationdate", ctypes.c_uint64),
    ("filetype", ctypes.c_int),  # LIBMTP_filetype_t enum
    ("next", ctypes.POINTER(LIBMTP_Track)),
]


class LIBMTP_Folder(ctypes.Structure):
    """
    LIBMTP_Folder
    Contains the ctypes structure for LIBMTP_folder_t
    """

    @override
    def __repr__(self):
        return "%s (%s)" % (self.name, self.folder_id)


LIBMTP_Folder._fields_ = [
    ("folder_id", ctypes.c_uint32),
    ("parent_id", ctypes.c_uint32),
    ("storage_id", ctypes.c_uint32),
    ("name", ctypes.c_char_p),
    ("sibling", ctypes.POINTER(LIBMTP_Folder)),
    ("child", ctypes.POINTER(LIBMTP_Folder)),
]

# Abstracted from libmtp's LIBMTP_filetype_t. This must be kept in sync.
#  first checked in 0.2.6.1
#  last checked in version 1.1.6
LIBMTP_Filetype = {
    "FOLDER": ctypes.c_int(0),
    "WAV": ctypes.c_int(1),
    "MP3": ctypes.c_int(2),
    "WMA": ctypes.c_int(3),
    "OGG": ctypes.c_int(4),
    "AUDIBLE": ctypes.c_int(5),
    "MP4": ctypes.c_int(6),
    "UNDEF_AUDIO": ctypes.c_int(7),
    "WMV": ctypes.c_int(8),
    "AVI": ctypes.c_int(9),
    "MPEG": ctypes.c_int(10),
    "ASF": ctypes.c_int(11),
    "QT": ctypes.c_int(12),
    "UNDEF_VIDEO": ctypes.c_int(13),
    "JPEG": ctypes.c_int(14),
    "JFIF": ctypes.c_int(15),
    "TIFF": ctypes.c_int(16),
    "BMP": ctypes.c_int(17),
    "GIF": ctypes.c_int(18),
    "PICT": ctypes.c_int(19),
    "PNG": ctypes.c_int(20),
    "VCALENDAR1": ctypes.c_int(21),
    "VCALENDAR2": ctypes.c_int(22),
    "VCARD2": ctypes.c_int(23),
    "VCARD3": ctypes.c_int(24),
    "WINDOWSIMAGEFORMAT": ctypes.c_int(25),
    "WINEXEC": ctypes.c_int(26),
    "TEXT": ctypes.c_int(27),
    "HTML": ctypes.c_int(28),
    "FIRMWARE": ctypes.c_int(29),
    "AAC": ctypes.c_int(30),
    "MEDIACARD": ctypes.c_int(31),
    "FLAC": ctypes.c_int(32),
    "MP2": ctypes.c_int(33),
    "M4A": ctypes.c_int(34),
    "DOC": ctypes.c_int(35),
    "XML": ctypes.c_int(36),
    "XLS": ctypes.c_int(37),
    "PPT": ctypes.c_int(38),
    "MHT": ctypes.c_int(39),
    "JP2": ctypes.c_int(40),
    "JPX": ctypes.c_int(41),
    "ALBUM": ctypes.c_int(42),
    "PLAYLIST": ctypes.c_int(43),
    "UNKNOWN": ctypes.c_int(44),
}

# Synced from libmtp 0.2.6.1's libmtp.h. Must be kept in sync.
LIBMTP_Error_Number = {
    "NONE": ctypes.c_int(0),
    "GENERAL": ctypes.c_int(1),
    "PTP_LAYER": ctypes.c_int(2),
    "USB_LAYER": ctypes.c_int(3),
    "MEMORY_ALLOCATION": ctypes.c_int(4),
    "NO_DEVICE_ATTACHED": ctypes.c_int(5),
    "STORAGE_FULL": ctypes.c_int(6),
    "CONNECTING": ctypes.c_int(7),
    "CANCELLED": ctypes.c_int(8),
}

LIBMTP_FILES_AND_FOLDERS_ROOT = 0xFFFFFFFF

# ----------
# End Data Model Definitions
# ----------

# ----------
# Type Definitions
# ----------
_libmtp.LIBMTP_Detect_Raw_Devices.restype = ctypes.c_int  # actually LIBMTP_Error_Number enum
_libmtp.LIBMTP_Create_Folder.restype = ctypes.c_int
_libmtp.LIBMTP_Create_Folder.argtypes = [
    ctypes.POINTER(LIBMTP_MTPDevice),
    ctypes.c_char_p,
    ctypes.c_uint32,
    ctypes.c_uint32,
]
_libmtp.LIBMTP_Get_Friendlyname.restype = ctypes.c_char_p
_libmtp.LIBMTP_Get_Serialnumber.restype = ctypes.c_char_p
_libmtp.LIBMTP_Get_Modelname.restype = ctypes.c_char_p
_libmtp.LIBMTP_Get_Manufacturername.restype = ctypes.c_char_p
_libmtp.LIBMTP_Get_Deviceversion.restype = ctypes.c_char_p
# Fue Could not find this function in libmtp documentation
# _libmtp.LIBMTP_Get_Filelisting_With_Callback.restype = ctypes.POINTER(LIBMTP_File)
_libmtp.LIBMTP_Get_Storage.restype = ctypes.c_int
_libmtp.LIBMTP_Get_Files_And_Folders.restype = ctypes.POINTER(LIBMTP_File)
_libmtp.LIBMTP_Get_Files_And_Folders.argtypes = [
    ctypes.POINTER(LIBMTP_MTPDevice),
    ctypes.c_uint32,
    ctypes.c_uint32,
]
_libmtp.LIBMTP_Get_Tracklisting_With_Callback.restype = ctypes.POINTER(LIBMTP_Track)
_libmtp.LIBMTP_Get_Filetype_Description.restype = ctypes.c_char_p
_libmtp.LIBMTP_Get_Filemetadata.restype = ctypes.POINTER(LIBMTP_File)
_libmtp.LIBMTP_Get_Trackmetadata.restype = ctypes.POINTER(LIBMTP_Track)
_libmtp.LIBMTP_Get_First_Device.restype = ctypes.POINTER(LIBMTP_MTPDevice)
_libmtp.LIBMTP_Open_Raw_Device_Uncached.restype = ctypes.POINTER(LIBMTP_MTPDevice)
# _libmtp.LIBMTP_Get_Playlist_List.restype = ctypes.POINTER(LIBMTP_Playlist)
# _libmtp.LIBMTP_Get_Playlist.restype = ctypes.POINTER(LIBMTP_Playlist)
_libmtp.LIBMTP_Get_Folder_List.restype = ctypes.POINTER(LIBMTP_Folder)
_libmtp.LIBMTP_Find_Folder.restype = ctypes.POINTER(LIBMTP_Folder)
_libmtp.LIBMTP_Get_Errorstack.restype = ctypes.POINTER(LIBMTP_Error)
# This is for callbacks with the type of LIBMTP_progressfunc_t
Progressfunc = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_uint64, ctypes.c_uint64)

# ----------
# End Type Definitions
# ----------


class MTP:
    """
    The MTP object
    This is the main wrapper around libmtp
    """

    libmtp_is_initialized: bool = False

    def __init__(self, new_raw_device: ctypes._Pointer[LIBMTP_RawDevice] | str | None = None):
        """
        Initializes the MTP object

        @rtype: None
        @return: None
        """

        self.mtp: ctypes.CDLL = _libmtp
        if not self.libmtp_is_initialized:
            self.mtp.LIBMTP_Init()
            self.libmtp_is_initialized = True
        self.device: str | None = None
        self._new_raw_device: ctypes._Pointer[LIBMTP_RawDevice] | str | None = new_raw_device
        self.raw_devices: ctypes._Pointer[ctypes._Pointer[LIBMTP_RawDevice]]

    def debug_stack(self):
        """
        Checks if __DEBUG__ is set, if so, prints and clears the
        errorstack.

        @rtype: None
        @return: None
        """

        if __DEBUG__:
            self.mtp.LIBMTP_Dump_Errorstack(self.device)
            # self.mtp.LIBMTP_Clear_Errorstack()

    def detect_devices(self) -> list[ctypes._Pointer[LIBMTP_RawDevice]]:
        """
        Detect if any MTP devices are connected

        @rtype: None
        @return: a list of LIBMTP_RawDevice instances for devices found

        """

        devlist: list[ctypes._Pointer[LIBMTP_RawDevice]] = []
        device = LIBMTP_RawDevice()
        self.raw_devices = ctypes.pointer(ctypes.pointer(device))
        numdevs = ctypes.c_int(0)
        err = self.mtp.LIBMTP_Detect_Raw_Devices(ctypes.byref(self.raw_devices), ctypes.byref(numdevs))
        if err == LIBMTP_Error_Number["NO_DEVICE_ATTACHED"]:
            return devlist
        elif err == LIBMTP_Error_Number["STORAGE_FULL"]:
            # ignore this, we're just trying to detect here, not do anything else
            pass
        elif err == LIBMTP_Error_Number["CONNECTING"]:
            raise AlreadyConnected("CONNECTING")
        elif err == LIBMTP_Error_Number["GENERAL"]:
            raise CommandFailed("GENERAL")
        elif err == LIBMTP_Error_Number["PTP_LAYER"]:
            raise CommandFailed("PTP_LAYER")
        elif err == LIBMTP_Error_Number["USB_LAYER"]:
            raise CommandFailed("USB_LAYER")
        elif err == LIBMTP_Error_Number["MEMORY_ALLOCATION"]:
            raise CommandFailed("MEMORY_ALLOCATION")
        elif err == LIBMTP_Error_Number["CANCELLED"]:
            raise CommandFailed("CANCELLED")
        if numdevs.value == 0:
            return devlist
        for i in range(numdevs.value):
            devlist.append(self.raw_devices[i])
        return devlist

    def connect(self) -> None:
        """
        Initializes the MTP connection to the device

        @rtype: None
        @return: None

        """

        if self.device is not None:
            raise AlreadyConnected
        if self._new_raw_device is None:
            raise ObjectNotFound

        # self.device = self.mtp.LIBMTP_Get_First_Device()
        self.device = self.mtp.LIBMTP_Open_Raw_Device_Uncached(ctypes.byref(self._new_raw_device)) # pyright: ignore[reportArgumentType]

        if not self.device:
            self.device = None
            raise NoDeviceConnected

    def disconnect(self):
        """
        Disconnects the MTP device and deletes the self.device object

        @rtype: None
        @return: None
        """

        if self.device is None:
            raise NotConnected

        self.mtp.LIBMTP_Release_Device(self.device)
        del self.device
        self.device = None

    def get_devicename(self) -> str:
        """
        Returns the connected device's 'friendly name' (or
        known as the owner name)

        @rtype: string
        @return: The connected device's 'friendly name'
        """

        if self.device is None:
            raise NotConnected

        return self.mtp.LIBMTP_Get_Friendlyname(self.device).decode("UTF-8")

    def get_modelname(self) -> str:
        """
        Returns the connected device's model name (such
        as "Zen V Plus")

        @rtype: string
        @return: The connected device's model name
        """

        if self.device is None:
            raise NotConnected

        return self.mtp.LIBMTP_Get_Modelname(self.device).decode("UTF-8")

    def create_folder(self, name: str, parent: int = 0, storage: int = 0) -> int:
        """
        This creates a new folder in the parent. If the parent
        is 0, it will go in the main directory.

        @type name: str
        @param name: The name for the folder
        @type parent: int
        @param parent: The parent ID or 0 for main directory
        @type storage: int
        @param storage: The storage id or 0 to create the new folder
                        on the primary storage
        @rtype: int
        @return: Returns the object ID of the new folder
        """

        if self.device is None:
            raise NotConnected

        ret: int = int(self.mtp.LIBMTP_Create_Folder(self.device, name.encode("UTF-8"), parent, storage))

        if ret == 0:
            self.debug_stack()
            raise CommandFailed

        return ret

    def send_file_from_file(self, source: str, target: str, storage_id: int, parent_id: int) -> int:
        """
        Sends a file from the filesystem to the connected device
        and stores it at the target filename inside the parent.

        This will attempt to "guess" the filetype with
        find_filetype()

        @type source: str
        @param source: The path on the filesystem where the file resides
        @type target: str
        @param target: The target filename on the device
        @type storage_id: int
        @param storage_id: The id of the storage to store the file on
        @type parent_id: int
        @param parent_id: The id of folder to store the file in
        @rtype: int
        @return: The object ID of the new file
        """

        if self.device is None:
            raise NotConnected

        if os.path.isfile(source) == False:
            raise IOError(f"File {source} not found")

        metadata = LIBMTP_File(
            filename=target.encode("UTF-8"),
            filetype=self.find_filetype(source),
            filesize=os.stat(source).st_size,
            storage_id=storage_id,
            parent_id=parent_id,
        )

        ret = int(
            self.mtp.LIBMTP_Send_File_From_File(
                self.device, source.encode("UTF-8"), ctypes.pointer(metadata), None, None
            )
        )

        if ret != 0:
            self.debug_stack()
            raise CommandFailed

        return metadata.item_id

    def get_file_to_file(self, file_id: int, target: str) -> None:
        """
        Downloads the file from the connected device and stores it at the
        target location

        @type file_id: int
        @param file_id: The unique numeric file id
        @type target: str
        @param target: The location to place the file
        @type callback: function or None
        @param callback: The function provided to libmtp to
         receive callbacks from ptp. Callback must take two
         arguments, total and sent (in bytes)
        """

        if self.device is None:
            raise NotConnected

        ret = int(self.mtp.LIBMTP_Get_File_To_File(self.device, file_id, target.encode("UTF-8"), None, None))

        if ret != 0:
            self.debug_stack()
            raise CommandFailed

    def delete_object(self, object_id: int) -> None:
        """
        Deletes the object off the connected device.

        @type object_id: int
        @param object_id: The unique object identifier
        """

        if self.device is None:
            raise NotConnected

        ret: int = int(self.mtp.LIBMTP_Delete_Object(self.device, object_id))

        if ret != 0:
            self.debug_stack()
            raise CommandFailed

    def get_serialnumber(self) -> str:
        """
        Returns the connected device's serial number

        @rtype: string
        @return: The connected device's serial number
        """

        if self.device is None:
            raise NotConnected

        return str(self.mtp.LIBMTP_Get_Serialnumber(self.device).decode("UTF-8"))

    def get_files_and_folder(self, storage_id: int, parent_id: int) -> list[LIBMTP_File]:
        """
        This function retrieves the contents of a certain folder with id parent on a certain storage on a certain
        device. The result contains both files and folders. The device used with this operations must have been
        opened with LIBMTP_Open_Raw_Device_Uncached() or it will fail.
        """
        ret: list[LIBMTP_File] = []
        if self.device is None:
            raise NotConnected
        files = self.mtp.LIBMTP_Get_Files_And_Folders(self.device, storage_id, parent_id)
        next = files
        while next:
            ret.append(next.contents)
            if next.contents.next is None:
                break
            next = next.contents.next
        return ret

    def get_storage(self) -> list[tuple[str, int]]:
        """
        This function updates all the storage id's of a device and their properties, then creates a linked list
        and puts the list head into the device struct. It also optionally sorts this list. If you want to display
        storage information in your application you should call this function, then dereference the device struct
        (device->storage) to get out information on the storage.

        You need to call this everytime you want to update the device->storage list, for example anytime you need
        to check available storage somewhere.

                @rtype: list
                @return: Returns a list with the storage names and the id
        """

        if self.device is None:
            raise NotConnected
        err = self.mtp.LIBMTP_Get_Storage(self.device, 0)
        if err == -1:
            self.mtp.LIBMTP_Dump_Errorstack(self.device)
            self.mtp.LIBMTP_Clear_Errorstack(self.device)
            raise CommandFailed
        ret: list[tuple[str, int]] = []
        next: Any = self.device.contents.storage    # pyright: ignore[reportAttributeAccessIssue]

        while next:
            ret.append(
                (
                    next.contents.StorageDescription.decode("UTF-8"),
                    next.contents.id,
                )
            )
            if next.contents.next is None:
                break
            next = next.contents.next

        return ret

    def find_filetype(self, filename: str) -> ctypes.c_int:
        """
        Attempts to guess the filetype off the filename. Kind of
        inaccurate and should be trusted with a grain of salt. It
        works in most situations, though.

        @type filename: str
        @param filename: The filename to attempt to guess from
        @rtype: int
        @return: The integer of the Filetype
        """

        fileext = filename.lower().split(".")[-1]  # type: ignore

        if fileext == "wav" or fileext == "wave":
            return LIBMTP_Filetype["WAV"]
        elif fileext == "mp3":
            return LIBMTP_Filetype["MP3"]
        elif fileext == "wma":
            return LIBMTP_Filetype["WMA"]
        elif fileext == "ogg":
            return LIBMTP_Filetype["OGG"]
        elif fileext == "mp4":
            return LIBMTP_Filetype["MP4"]
        elif fileext == "wmv":
            return LIBMTP_Filetype["WMV"]
        elif fileext == "avi":
            return LIBMTP_Filetype["AVI"]
        elif fileext == "mpeg" or fileext == "mpg":
            return LIBMTP_Filetype["MPEG"]
        elif fileext == "asf":
            return LIBMTP_Filetype["ASF"]
        elif fileext == "qt" or fileext == "mov":
            return LIBMTP_Filetype["QT"]
        elif fileext == "jpeg" or fileext == "jpg":
            return LIBMTP_Filetype["JPEG"]
        elif fileext == "jfif":
            return LIBMTP_Filetype["JFIF"]
        elif fileext == "tif" or fileext == "tiff":
            return LIBMTP_Filetype["TIFF"]
        elif fileext == "bmp":
            return LIBMTP_Filetype["BMP"]
        elif fileext == "gif":
            return LIBMTP_Filetype["GIF"]
        elif fileext == "pic" or fileext == "pict":
            return LIBMTP_Filetype["PICT"]
        elif fileext == "png":
            return LIBMTP_Filetype["PNG"]
        elif fileext == "wmf":
            return LIBMTP_Filetype["WINDOWSIMAGEFORMAT"]
        elif fileext == "ics":
            return LIBMTP_Filetype["VCALENDAR2"]
        elif fileext == "exe" or fileext == "com" or fileext == "bat" or fileext == "dll" or fileext == "sys":
            return LIBMTP_Filetype["WINEXEC"]
        elif fileext == "aac":
            return LIBMTP_Filetype["AAC"]
        elif fileext == "mp2":
            return LIBMTP_Filetype["MP2"]
        elif fileext == "flac":
            return LIBMTP_Filetype["FLAC"]
        elif fileext == "m4a":
            return LIBMTP_Filetype["M4A"]
        elif fileext == "doc":
            return LIBMTP_Filetype["DOC"]
        elif fileext == "xml":
            return LIBMTP_Filetype["XML"]
        elif fileext == "xls":
            return LIBMTP_Filetype["XLS"]
        elif fileext == "ppt":
            return LIBMTP_Filetype["PPT"]
        elif fileext == "mht":
            return LIBMTP_Filetype["MHT"]
        elif fileext == "jp2":
            return LIBMTP_Filetype["JP2"]
        elif fileext == "jpx":
            return LIBMTP_Filetype["JPX"]
        else:
            return LIBMTP_Filetype["UNKNOWN"]

    # def get_manufacturer(self):
    #     """
    #     Return the connected device's manufacturer

    #     @rtype: string
    #     @return: The connected device's manufacturer
    #     """
    #     if self.device is None:
    #         raise NotConnected

    #     return self.mtp.LIBMTP_Get_Manufacturername(self.device)

    # def set_devicename(self, name: str):
    #     """
    #     Changes the connected device's 'friendly name' to name

    #     @type name: string
    #     @param name: The name to change the connected device's
    #      'friendly name' to
    #     @rtype: None
    #     @return: None
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Set_Friendlyname(self.device, name)
    #     if ret != 0:
    #         self.debug_stack()
    #         raise CommandFailed

    # def get_batterylevel(self):
    #     """
    #     Returns the connected device's maximum and current
    #     battery levels

    #     @rtype: tuple
    #     @return: The connected device's maximum and current
    #      battery levels ([0] is maximum, [1] is current)
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     maximum_level = ctypes.c_uint8()
    #     current_level = ctypes.c_uint8()

    #     ret = self.mtp.LIBMTP_Get_Batterylevel(
    #         self.device, ctypes.byref(maximum_level), ctypes.byref(current_level)
    #     )

    #     if ret != 0:
    #         raise CommandFailed

    #     return (maximum_level.value, current_level.value)

    # def get_deviceversion(self):
    #     """
    #     Returns the connected device's version (such as
    #     firmware/hardware version)

    #     @rtype: string
    #     @return: Returns the connect device's version
    #      information
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     return self.mtp.LIBMTP_Get_Deviceversion(self.device)

    # def get_filelisting(self, callback=None): # type: ignore
    #     """
    #     Returns the connected device's file listing as a tuple,
    #     containing L{LIBMTP_File} objects.

    #     @type callback: function or None
    #     @param callback: The function provided to libmtp to
    #      receive callbacks from ptp. Callback must take two
    #      arguments, total and sent (in bytes)
    #     @rtype: tuple
    #     @return: Returns the connect device file listing tuple
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     if callback != None:
    #         callback = Progressfunc(callback) # type: ignore

    #     files = self.mtp.LIBMTP_Get_Filelisting_With_Callback(self.device, callback, None)
    #     ret = []
    #     next = files

    #     while next:
    #         ret.append(next.contents) # type: ignore
    #         if next.contents.next is None:
    #             break
    #         next = next.contents.next

    #     return ret # type: ignore

    # def get_filetype_description(self, filetype): # type: ignore
    #     """
    #     Returns the description of the filetype

    #     @type filetype: int
    #     @param filetype: The MTP filetype integer
    #     @rtype: string
    #     @return: The file type information
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     return self.mtp.LIBMTP_Get_Filetype_Description(filetype)

    # def get_file_metadata(self, file_id): # type: ignore
    #     """
    #     Returns the file metadata from the connected device

    #     As per the libmtp documentation, calling this function
    #     repeatly is not recommended, as it is slow and creates
    #     a large amount of USB traffic.

    #     @type file_id: int
    #     @param file_id: The unique numeric file id
    #     @rtype: LIBMTP_File
    #     @return: The file metadata
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Get_Filemetadata(self.device, file_id)

    #     if not hasattr(ret, "contents"):
    #         raise ObjectNotFound

    #     return ret.contents

    # def get_tracklisting(self, callback=None): # type: ignore
    #     """
    #     Returns tracks from the connected device

    #     @type callback: function or None
    #     @param callback: The function provided to libmtp to
    #      receive callbacks from ptp. Callback must take two
    #      arguments, total and sent (in bytes)
    #     @rtype: tuple
    #     @return: Returns a tuple full of L{LIBMTP_Track} objects
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     if callback != None:
    #         callback = Progressfunc(callback) # type: ignore

    #     tracks = self.mtp.LIBMTP_Get_Tracklisting_With_Callback(self.device, callback, None)
    #     ret = []
    #     next = tracks

    #     while next:
    #         ret.append(next.contents) # type: ignore
    #         if next.contents.next is None:
    #             break
    #         next = next.contents.next

    #     return ret # type: ignore

    # def get_track_metadata(self, track_id): # type: ignore
    #     """
    #     Returns the track metadata

    #     As per the libmtp documentation, calling this function repeatly is not
    #     recommended, as it is slow and creates a large amount of USB traffic.

    #     @type track_id: int
    #     @param track_id: The unique numeric track id
    #     @rtype: L{LIBMTP_Track}
    #     @return: The track metadata
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Get_Trackmetadata(self.device, track_id)

    #     if not hasattr(ret, "contents"):
    #         raise ObjectNotFound

    #     return ret.contents

    # def get_track_to_file(self, track_id, target, callback=None): # type: ignore
    #     """
    #     Downloads the track from the connected device and stores it at
    #     the target location

    #     @type track_id: int
    #     @param track_id: The unique numeric track id
    #     @type target: str
    #     @param target: The location to place the track
    #     @type callback: function or None
    #     @param callback: The function provided to libmtp to
    #      receive callbacks from ptp. Callback must take two
    #      arguments, total and sent (in bytes)
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     if callback != None:
    #         callback = Progressfunc(callback) # type: ignore

    #     ret = self.mtp.LIBMTP_Get_Track_To_File(self.device, track_id, target, callback, None)

    #     if ret != 0:
    #         self.debug_stack()
    #         raise CommandFailed

    # def send_track_from_file(self, source, target, metadata, callback=None): # type: ignore
    #     """
    #     Sends a track from the filesystem to the connected
    #     device

    #     @type source: str
    #     @param source: The path where the track resides
    #     @type target: str
    #     @param target: The target filename on the device
    #     @type metadata: LIBMTP_Track
    #     @param metadata: The track metadata
    #     @type callback: function or None
    #     @param callback: The function provided to libmtp to
    #      receive callbacks from ptp. Callback function must
    #      take two arguments, sent and total (in bytes)
    #     @rtype: int
    #     @return: The object ID of the new track
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     if os.path.exists(source) is None: # type: ignore
    #         raise IOError

    #     if callback:
    #         callback = Progressfunc(callback) # type: ignore

    #     metadata.filename = target
    #     metadata.filetype = self.find_filetype(source) # type: ignore
    #     metadata.filesize = os.stat(source).st_size # type: ignore

    #     ret = self.mtp.LIBMTP_Send_Track_From_File(
    #         self.device, source, ctypes.pointer(metadata), callback, None # type: ignore
    #     )

    #     if ret != 0:
    #         self.debug_stack()
    #         raise CommandFailed

    #     return metadata.item_id # type: ignore

    # def get_freespace(self):
    #     """
    #     Returns the amount of free space on the connected device
    #     @rtype: long
    #     @return: The amount of free storage in bytes
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     self.mtp.LIBMTP_Get_Storage(self.device, 0)
    #     return self.device.contents.storage.contents.FreeSpaceInBytes

    # def get_totalspace(self):
    #     """
    #     Returns the total space on the connected device
    #     @rtype: long
    #     @return: The amount of total storage in bytes
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     self.mtp.LIBMTP_Get_Storage(self.device, 0)
    #     return self.device.contents.storage.contents.MaxCapacity

    # def get_usedspace(self):
    #     """
    #     Returns the amount of used space on the connected device

    #     @rtype: long
    #     @return: The amount of used storage in bytes
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     self.mtp.LIBMTP_Get_Storage(self.device, 0)
    #     storage = self.device.contents.storage.contents
    #     return storage.MaxCapacity - storage.FreeSpaceInBytes

    # def get_usedspace_percent(self):
    #     """
    #     Returns the amount of used space as a percentage

    #     @rtype: float
    #     @return: The percentage of used storage
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     self.mtp.LIBMTP_Get_Storage(self.device, 0)
    #     storage = self.device.contents.storage.contents

    #     # Why don't we call self.get_totalspace/self.get_usedspace
    #     # here? That would require 3 *more* calls to
    #     # LIBMTP_Get_Storage
    #     usedspace = storage.MaxCapacity - storage.FreeSpaceInBytes
    #     return (float(usedspace) / float(storage.MaxCapacity)) * 100

    # def get_playlists(self): # type: ignore
    #     """
    #     Returns a tuple filled with L{LIBMTP_Playlist} objects
    #     from the connected device.

    #     The main gotcha of this function is that the tracks
    #     variable of LIBMTP_Playlist isn't iterable (without
    #     segfaults), so, you have to iterate over the no_tracks
    #     (through range or xrange) and access it that way (i.e.
    #     tracks[track_id]). Kind of sucks.

    #     @rtype: tuple
    #     @return: Tuple filled with LIBMTP_Playlist objects
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     playlists = self.mtp.LIBMTP_Get_Playlist_List(self.device)
    #     ret = []
    #     next = playlists

    #     while next:
    #         ret.append(next.contents) # type: ignore
    #         if next.contents.next is None:
    #             break
    #         next = next.contents.next

    #     return ret # type: ignore

    # def get_playlist(self, playlist_id): # type: ignore
    #     """
    #     Returns a L{LIBMTP_Playlist} object of the requested
    #     playlist_id from the connected device

    #     @type playlist_id: int
    #     @param playlist_id: The unique playlist identifier
    #     @rtype: LIBMTP_Playlist
    #     @return: The playlist object
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     try:
    #         ret = self.mtp.LIBMTP_Get_Playlist(self.device, playlist_id).contents
    #     except ValueError:
    #         raise ObjectNotFound

    #     return ret

    # def create_new_playlist(self, metadata): # type: ignore
    #     """
    #     Creates a new playlist based on the metadata object
    #     passed.

    #     @type metadata: LIBMTP_Playlist
    #     @param metadata: A LIBMTP_Playlist object describing
    #      the playlist
    #     @rtype: int
    #     @return: The object ID of the new playlist
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Create_New_Playlist(self.device, ctypes.pointer(metadata)) # type: ignore

    #     if ret != 0:
    #         self.debug_stack()
    #         raise CommandFailed

    #     return metadata.playlist_id # type: ignore

    # def update_playlist(self, metadata): # type: ignore
    #     """
    #     Updates a playlist based on the supplied metadata.

    #     When updating the tracks field in a playlist, this
    #     function will replace the playlist's tracks with
    #     the tracks supplied in the metadata object. This
    #     means that the previous tracks in the playlist
    #     will be overwritten.

    #     @type metadata: LIBMTP_Playlist
    #     @param metadata: A LIBMTP_Playlist object describing
    #      the updates to the playlist.
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Update_Playlist(self.device, ctypes.pointer(metadata))

    #     if ret != 0:
    #         self.debug_stack()
    #         raise CommandFailed

    # def get_folder_list(self): # type: ignore
    #     """
    #     Returns a pythonic dict of the folders on the
    #     device.

    #     @rtype: dict
    #     @return: A dict of the folders on the device where
    #      the folder ID is the key.
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     folders = self.mtp.LIBMTP_Get_Folder_List(self.device)
    #     next = folders
    #     # List of folders, key being the folder ID
    #     ret = {}
    #     # Iterate over the folders to grab the first-level parents
    #     while True:
    #         next = next.contents
    #         scanned = True

    #         # Check if this ID exists, if not, add it
    #         # and trigger a scan of the children
    #         if next.folder_id not in ret:
    #             ret[next.folder_id] = next
    #             scanned = False

    #         if (scanned == False) and (next.child):
    #             ## Scan the children
    #             next = next.child

    #         elif next.sibling:
    #             ## Scan the siblings
    #             next = next.sibling

    #         elif next.parent_id != 0:
    #             ## If we have no children/siblings to visit,
    #             ## and we aren't at the parent, go back to
    #             ## the parent.
    #             next = self.mtp.LIBMTP_Find_Folder(folders, int(next.parent_id))
    #         else:
    #             ## We have scanned everything, let's go home.
    #             break

    #     return ret # type: ignore

    # def get_parent_folders(self): # type: ignore
    #     """
    #     Returns a list of only the parent folders.
    #     @rtype: list
    #     @return: Returns a list of the parent folders
    #     """

    #     if self.device is None:
    #         raise NotConnected
    #     folders = self.mtp.LIBMTP_Get_Folder_List(self.device)
    #     next = folders
    #     # A temporary holding space, this makes checking folder
    #     # IDs easier
    #     tmp = {}

    #     while True:
    #         next = next.contents
    #         ## Check if this folder is in the dict
    #         if next.folder_id not in tmp:
    #             tmp[next.folder_id] = next

    #         # Check for siblings
    #         if next.sibling:
    #             ## Scan the sibling
    #             next = next.sibling
    #         else:
    #             ## We're done here.
    #             break

    #     ## convert the dict into a list
    #     ret = []
    #     for key in tmp: # type: ignore
    #         ret.append(tmp[key]) # type: ignore

    #     return ret # type: ignore

    # def get_errorstack(self):
    #     """
    #     Returns the connected device's errorstack from
    #     LIBMTP.
    #     @rtype: L{LIBMTP_Error}
    #     @return: An array of LIBMTP_Errors.
    #     """

    #     if self.device is None:
    #         raise NotConnected

    #     ret = self.mtp.LIBMTP_Get_Errorstack(self.device)

    #     if ret != 0:
    #         raise CommandFailed

    #     return ret


# class LIBMTP_Playlist(ctypes.Structure):
#     """
#     LIBMTP_Playlist
#     Contains the ctypes structure for LIBMTP_playlist_t
#     """

#     def __init__(self):
#         super().__init__()
#         self.tracks = ctypes.pointer(ctypes.c_uint32(0))
#         self.no_tracks = ctypes.c_uint32(0)

#     def __repr__(self):
#         return "%s (%s)" % (self.name, self.playlist_id)

#     def __iter__(self):
#         """
#         This allows the playlist object to act like a list with
#         a generator.
#         """
#         for track in range(self.no_tracks.value):
#             yield self.tracks[track]

#     def __getitem__(self, key): # type: ignore
#         """
#         This allows the playlist to return tracks like a list
#         """

#         if key > (self.no_tracks.value - 1):
#             raise IndexError

#         return self.tracks[key]

#     def __setitem__(self, key, value): # type: ignore
#         """
#         This allows the user to manipulate the playlist like a
#         list. However, this will only modify existing objects,
#         you can't try to set a key outside of the current size.
#         """

#         if key > (self.no_tracks.value - 1):
#             raise IndexError

#         self.tracks[key] = value

#     def __delitem__(self, key): # type: ignore
#         """
#         This allows the user to delete an object
#         from the playlist
#         """

#         if key > (self.no_tracks.value - 1):
#             raise IndexError

#         for i in range(key, (self.no_tracks.value - 1)): # type: ignore
#             self.tracks[i] = self.tracks[i + 1]

#         self.no_tracks.value -= 1

#     def append(self, value): # type: ignore
#         """
#         This function appends a track to the end of the tracks
#         list.
#         """
#         if self.tracks is None: # type: ignore
#             self.tracks = ctypes.pointer(ctypes.c_uint32(0))

#         self.no_tracks.value += 1
#         self.tracks[(self.no_tracks.value - 1)] = value

#     def __len__(self):
#         """
#         This returns the number of tracks in the playlist
#         """

#         return self.no_tracks


# LIBMTP_Playlist._fields_ = [
#     ("playlist_id", ctypes.c_uint32),
#     ("parent_id", ctypes.c_uint32),
#     ("storage_id", ctypes.c_uint32),
#     ("name", ctypes.c_char_p),
#     ("tracks", ctypes.POINTER(ctypes.c_uint32)),
#     ("no_tracks", ctypes.c_uint32),
#     ("next", ctypes.POINTER(LIBMTP_Playlist)),
# ]

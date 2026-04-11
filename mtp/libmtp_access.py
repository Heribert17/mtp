"""
A module to access the Linux libmtp library. This is necessary for KDE desktops
because KDE doesn't mount mobil devices as a virtual filesystem like gnome.

Author:  Heribert Füchtenhans

Version: 2026.04.11
"""

from typing import override

import os
import ctypes
import ctypes.util


_module_path = ctypes.util.find_library("mtp")
_libmtp = ctypes.CDLL(_module_path)


# Error Definitions
# -----------------
class NoDeviceConnected(Exception):
    """No device is connted"""

    pass


class CommandFailed(Exception):
    """Command returned with error"""

    pass


class NotConnected(Exception):
    """Device is not connected"""

    pass


class ObjectNotFound(Exception):
    """The object doesn't exists"""

    pass


# libmtp structure definitions
# ----------------------------
class LIBMTP_Error(ctypes.Structure):
    """LIBMTP_Error
    Contains the ctypes structure for LIBMTP_error_t
    """

    @override
    def __repr__(self) -> str:
        return self.errornumber  # pyright: ignore[reportAny]


LIBMTP_Error._fields_ = [
    ("errornumber", ctypes.c_int),
    ("error_text", ctypes.c_char_p),
    ("next", ctypes.POINTER(LIBMTP_Error)),
]


class LIBMTP_DeviceStorage(ctypes.Structure):
    """LIBMTP_DeviceStorage
    Contains the ctypes structure for LIBMTP_devicestorage_t
    """

    @override
    def __repr__(self) -> str:
        return self.id  # pyright: ignore[reportAny]


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
    """LIBMTP_DeviceEntry
    Contains the ctypes structure for LIBMTP_device_entry_t
    """

    @override
    def __repr__(self) -> str:
        return self.vendor  # pyright: ignore[reportAny]


LIBMTP_DeviceEntry._fields_ = [
    ("vendor", ctypes.c_char_p),
    ("vendor_id", ctypes.c_uint16),
    ("product", ctypes.c_char_p),
    ("product_id", ctypes.c_uint16),
    ("device_flags", ctypes.c_uint32),
]


class LIBMTP_RawDevice(ctypes.Structure):
    """LIBMTP_RawDevice
    Contains the ctypes structure for LIBMTP_raw_device_t
    """

    @override
    def __repr__(self) -> str:
        return self.device_entry  # pyright: ignore[reportAny]


LIBMTP_RawDevice._fields_ = [
    ("device_entry", LIBMTP_DeviceEntry),
    ("bus_location", ctypes.c_uint32),
    ("devnum", ctypes.c_uint8),
]


class LIBMTP_MTPDevice(ctypes.Structure):
    """LIBMTP_MTPDevice
    Contains the ctypes structure for LIBMTP_mtpdevice_t
    """

    @override
    def __repr__(self) -> str:
        return self.interface_number  # pyright: ignore[reportAny]


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
    """LIBMTP_File
    Contains the ctypes structure for LIBMTP_file_t
    """

    @override
    def __repr__(self):
        return "%s (%s)" % (self.filename, self.item_id)  # pyright: ignore[reportAny]


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


class LIBMTP_Folder(ctypes.Structure):
    """
    LIBMTP_Folder
    Contains the ctypes structure for LIBMTP_folder_t
    """

    @override
    def __repr__(self):
        return "%s (%s)" % (self.name, self.folder_id)  # pyright: ignore[reportAny]


LIBMTP_Folder._fields_ = [
    ("folder_id", ctypes.c_uint32),
    ("parent_id", ctypes.c_uint32),
    ("storage_id", ctypes.c_uint32),
    ("name", ctypes.c_char_p),
    ("sibling", ctypes.POINTER(LIBMTP_Folder)),
    ("child", ctypes.POINTER(LIBMTP_Folder)),
]


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


# Type Definitions
# ----------------
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
_libmtp.LIBMTP_Get_Storage.restype = ctypes.c_int
_libmtp.LIBMTP_Get_Files_And_Folders.restype = ctypes.POINTER(LIBMTP_File)
_libmtp.LIBMTP_Get_Files_And_Folders.argtypes = [
    ctypes.POINTER(LIBMTP_MTPDevice),
    ctypes.c_uint32,
    ctypes.c_uint32,
]
_libmtp.LIBMTP_Get_First_Device.restype = ctypes.POINTER(LIBMTP_MTPDevice)
_libmtp.LIBMTP_Open_Raw_Device_Uncached.restype = ctypes.POINTER(LIBMTP_MTPDevice)
_libmtp.LIBMTP_Get_Folder_List.restype = ctypes.POINTER(LIBMTP_Folder)
_libmtp.LIBMTP_Send_File_From_File.restype = ctypes.c_int
_libmtp.LIBMTP_Send_File_From_File.argtypes = [
    ctypes.POINTER(LIBMTP_MTPDevice),
    ctypes.c_char_p,
    ctypes.POINTER(LIBMTP_File),
    ctypes.POINTER(LIBMTP_File),  # is always None
    ctypes.POINTER(LIBMTP_File),  # is always none
]


class MTP:
    """This is a python wrapper for libmtp with some procedures
    to access the MTP filesystem"""

    libmtp_is_initialized: bool = False

    def __init__(
        self,
        new_raw_device: ctypes._Pointer[LIBMTP_RawDevice] | str | None = None,  # pyright: ignore[reportPrivateUsage]
    ) -> None:
        """Initializes the MTP object"""
        self.mtp: ctypes.CDLL = _libmtp
        if not self.libmtp_is_initialized:
            self.mtp.LIBMTP_Init()
            self.libmtp_is_initialized = True
        self.device: str | None = None
        self._new_raw_device: ctypes._Pointer[LIBMTP_RawDevice] | str | None = (  # pyright: ignore[reportPrivateUsage]
            new_raw_device
        )
        self.raw_devices: ctypes._Pointer[ctypes._Pointer[LIBMTP_RawDevice]]  # pyright: ignore[reportPrivateUsage]

    def detect_devices(self) -> list[ctypes._Pointer[LIBMTP_RawDevice]]:  # pyright: ignore[reportPrivateUsage]
        """Detect connected devices"""
        devlist: list[ctypes._Pointer[LIBMTP_RawDevice]] = []  # pyright: ignore[reportPrivateUsage]
        device = LIBMTP_RawDevice()
        self.raw_devices = ctypes.pointer(ctypes.pointer(device))
        numdevs = ctypes.c_int(0)
        err = self.mtp.LIBMTP_Detect_Raw_Devices(  # pyright: ignore[reportAny]
            ctypes.byref(self.raw_devices), ctypes.byref(numdevs)
        )
        if err == LIBMTP_Error_Number["NO_DEVICE_ATTACHED"]:
            return devlist
        elif err == LIBMTP_Error_Number["STORAGE_FULL"]:
            # ignore this, we're just trying to detect here, not do anything else
            pass
        elif err == LIBMTP_Error_Number["CONNECTING"]:
            pass
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
            devlist.append(self.raw_devices[i])  # pyright: ignore[reportAny]
        return devlist

    def connect(self) -> None:
        """Connect to the device"""
        if self.device is not None:
            return
        if self._new_raw_device is None:
            raise ObjectNotFound
        self.device = self.mtp.LIBMTP_Open_Raw_Device_Uncached(
            ctypes.byref(self._new_raw_device)  # pyright: ignore[reportArgumentType]
        )
        if not self.device:
            self.device = None
            raise NoDeviceConnected

    def disconnect(self):
        """Disconnects the device"""
        if self.device is None:
            return
        self.mtp.LIBMTP_Release_Device(self.device)
        del self.device
        self.device = None

    def get_devicename(self) -> str:
        """returns the connected device's 'friendly name'"""
        if self.device is None:
            raise NotConnected
        return self.mtp.LIBMTP_Get_Friendlyname(self.device).decode("UTF-8")  # pyright: ignore[reportAny]

    def get_modelname(self) -> str:
        """returns the connected device's model name"""
        if self.device is None:
            raise NotConnected
        return self.mtp.LIBMTP_Get_Modelname(self.device).decode("UTF-8")  # pyright: ignore[reportAny]

    def create_folder(self, name: str, parent: int = 0, storage: int = 0) -> int:
        """creates a new folder in the parent. If the parent is 0, it will go in the main directory.
        name: The name for the folder
        parent: The parent ID or 0 for main directory
        storage: The storage id or 0 to create the new folder on the primary storage
        return: Returns the object ID of the new folder
        """
        if self.device is None:
            raise NotConnected
        ret: int = int(
            self.mtp.LIBMTP_Create_Folder(
                self.device, name.encode("UTF-8"), parent, storage
            )  # pyright: ignore[reportAny]
        )
        if ret == 0:
            raise CommandFailed
        return ret

    filetypes: dict[str, int] = {
        "/": 0,
        "wav": 1,
        "mp3": 2,
        "wma": 3,
        "ogg": 4,
        "audible": 5,
        "mp4": 6,
        "undef_audio": 7,
        "wmv": 8,
        "avi": 9,
        "mpeg": 10,
        "asf": 11,
        "qt": 12,
        "undef_video": 13,
        "jpeg": 14,
        "jpg": 14,
        "jfif": 15,
        "tiff": 16,
        "bmp": 17,
        "gif": 18,
        "pict": 19,
        "png": 20,
        "vcalendar1": 21,
        "vcalendar2": 22,
        "vcard2": 23,
        "vcard3": 24,
        "windowsimageformat": 25,
        "winexec": 26,
        "text": 27,
        "html": 28,
        "firmware": 29,
        "aac": 30,
        "mediacard": 31,
        "flac": 32,
        "mp2": 33,
        "m4a": 34,
        "doc": 35,
        "xml": 36,
        "xls": 37,
        "ppt": 38,
        "mht": 39,
        "jp2": 40,
        "jpx": 41,
        "album": 42,
        "playlist": 43,
        "unknown": 44,
    }

    def find_filetype(self, filename: str) -> ctypes.c_int:
        """Check the filetype and return the cytypes number."""
        ext = os.path.splitext(filename)[1]
        if ext.startswith("."):
            ext = ext[1:]
        val = self.filetypes[ext] if ext in self.filetypes else self.filetypes["unknown"]
        return ctypes.c_int(val)

    def send_file_from_file(self, source: str, target: str, storage_id: int, parent_id: int) -> int:
        """stores a file from the filesystem to the device with target as filename in the parent folder.
        and stores it at the target filename inside the parent.
        source: The path on the filesystem where the file resides
        target: The target filename on the device
        storage_id: The id of the storage to store the file on
        parent_id: The id of folder to store the file in
        return: The object ID of the new file
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
            )  # pyright: ignore[reportAny]
        )
        if ret != 0:
            raise CommandFailed
        return metadata.item_id  # pyright: ignore[reportAny]

    def get_file_to_file(self, file_id: int, target: str) -> None:
        """Downloads the file from the device and stores it at the target location
        file_id: The unique numeric file id
        target: The location to place the file
        """
        if self.device is None:
            raise NotConnected
        ret = int(
            self.mtp.LIBMTP_Get_File_To_File(
                self.device, file_id, target.encode("UTF-8"), None, None
            )  # pyright: ignore[reportAny]
        )
        if ret != 0:
            raise CommandFailed

    def delete_object(self, object_id: int) -> None:
        """Deletes the object"""
        if self.device is None:
            raise NotConnected
        ret: int = int(self.mtp.LIBMTP_Delete_Object(self.device, object_id))  # pyright: ignore[reportAny]
        if ret != 0:
            raise CommandFailed

    def get_serialnumber(self) -> str:
        """returns the serialnumber"""
        if self.device is None:
            raise NotConnected
        return str(self.mtp.LIBMTP_Get_Serialnumber(self.device).decode("UTF-8"))  # pyright: ignore[reportAny]

    def get_files_and_folder(self, storage_id: int, parent_id: int) -> list[LIBMTP_File]:
        """This function retrieves the contents of a certain folder with id parent on a certain storage
        on a certain device. The result contains both files and folders.
        """
        ret: list[LIBMTP_File] = []
        if self.device is None:
            raise NotConnected
        next = self.mtp.LIBMTP_Get_Files_And_Folders(self.device, storage_id, parent_id)  # pyright: ignore[reportAny]
        while next:
            ret.append(next.contents)  # pyright: ignore[reportAny]
            if next.contents.next is None:  # pyright: ignore[reportAny]
                break
            next = next.contents.next  # pyright: ignore[reportAny]
        return ret

    def get_storage(self) -> list[tuple[str, int]]:
        """This function updates all the storage id's of a device and their properties, then creates a linked list
        and puts the list head into the device struct. It also optionally sorts this list. If you want to display
        storage information in your application you should call this function, then dereference the device struct
        (device->storage) to get out information on the storage.
        You need to call this everytime you want to update the device->storage list, for example anytime you need
        to check available storage somewhere.
        """
        if self.device is None:
            raise NotConnected
        err = self.mtp.LIBMTP_Get_Storage(self.device, 0)  # pyright: ignore[reportAny]
        if err == -1:
            self.mtp.LIBMTP_Clear_Errorstack(self.device)
            raise CommandFailed
        ret: list[tuple[str, int]] = []
        next = (  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType]
            self.device.contents.storage  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        )
        while next:
            ret.append(
                (
                    next.contents.StorageDescription.decode(  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                        "UTF-8"
                    ),
                    next.contents.id,  # pyright: ignore[reportUnknownMemberType]
                )
            )
            if next.contents.next is None:  # pyright: ignore[reportUnknownMemberType]
                break
            next = next.contents.next  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        return ret

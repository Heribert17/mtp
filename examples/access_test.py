"""
Test the functions in mtp and also serve as example for usage.
Be aware that there is no error handling in these examples. Error handling
should be used for production code
"""

# import gc
# import mtp.win_access
# import mtp.linux_access
import os
import platform
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if platform.system() == "Windows":
    print("On Windows")
    import mtp.win_access as mtp_access

    on_windows = True
else:
    print("On Linux")
    import mtp.linux_access as mtp_access

    on_windows = False


TESTNUMBER: int = 10  # 1 - 10, 0 for all tests
TESTRUNS = 1  # how many times a test should be executed


def test_1_connect_disconnct() -> None:
    """Test connection and disconnection to device"""
    print("Test 1 ------------------------------------------------------------------------")
    for i in range(TESTRUNS):
        print(f"Find devices on test run {i + 1}:")
        devices = mtp_access.get_portable_devices()
        if len(devices) == 0:
            print("No devices found!")
            return
        for dev in devices:
            print(
                f"Found device: Name: {dev.name}: Desc.: {dev.description}: Serialnr.: {dev.serialnumber} Fullname: {dev.devicename}"
            )
            dev.close()


def test_2_list_storages() -> None:
    """Test list storages of device"""
    print("Test 2 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Find storages on test run {i + 1}:")
            for storage in dev.get_content():
                print(f"Found Storage: {storage.full_filename}")
        dev.close()


def test_3_list_childs_with_walk() -> None:
    """Test get all childs with walk"""

    def error_function(error: str) -> bool:
        """Error function"""
        print(f"Error: {error}")
        return True

    print("Test 3 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Find all childs with walk on test run {i + 1}:")
            for storage in dev.get_content():
                print(f"Walk Storage: {storage.full_filename}")
                count = 0
                for _, dirs, files in mtp_access.walk(
                    dev,  # pyright: ignore[reportArgumentType]
                    storage.full_filename,
                    None,
                    error_function,
                ):
                    for _ in dirs:
                        count += 1
                        # print(f"dir: {directory.full_filename}")
                    for _ in files:
                        count += 1
                        # print(f"file: {file.full_filename}")
                print(f"   Found {count} entries on that storage.")
        dev.close()


def test_4_get_cont_from_path() -> None:
    """Test get cont from a path"""
    print("Test 4 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Find content of a full qualified path on test run {i + 1}:")
            cont: mtp_access.PortableDeviceContent | None = mtp_access.get_content_from_device_path(
                dev,  # pyright: ignore[reportArgumentType]
                f"{dev.devicename}/Interner Speicher/Android/media",
            )
            print(f"Content found: {cont}")
        dev.close()


def test_5_create_delete_folder() -> None:
    """Create / Delete Folder"""
    print("Test 5 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Create and delete folder on test run {i + 1}:")
            new_path = os.path.join(dev.get_content()[0].full_filename, "example/temp")
            cont = mtp_access.makedirs(dev, new_path)  # pyright: ignore[reportArgumentType]
            cont.remove()
            cont = mtp_access.get_content_from_device_path(
                dev,  # pyright: ignore[reportArgumentType]
                os.path.join(dev.get_content()[0].full_filename, "example/temp"),
            )
            if cont is not None:
                raise OSError("Can't delete folder in test_create_delete_folder")
            print("   Content (temp) removed")
        dev.close()


def test_6_create_delete_file() -> None:
    """Create / Delete files"""
    print("Test 6 ------------------------------------------------------------------------")
    mtp_filename = "music.mp3"
    uploadfilename = os.path.join(os.path.dirname(__file__), "music.mp3")
    downloadfilename = os.path.join(os.path.dirname(__file__), "test.mp3")
    for dev in mtp_access.get_portable_devices():
        print(f"Device: {dev.devicename}")
        # Create the directory for the new file
        d_content = dev.get_content()
        new_path = os.path.join(d_content[0].full_filename, "Download")  #  "example/temp")
        cont = mtp_access.makedirs(dev, new_path)  # pyright: ignore[reportArgumentType]
        for i in range(TESTRUNS):
            print(f"Create and delete file on test run {i + 1}:")
            # Delete the file if it exists
            fcont = cont.get_child(mtp_filename)
            if fcont is not None:
                fcont.remove()
            # Upload the file to the mtp device
            print("Uploading file")
            cont.upload_file(mtp_filename, uploadfilename)
            # Test if it exists on the MTP device
            fcont = cont.get_child(mtp_filename)
            if fcont is None:
                print(f"Could not create file {mtp_filename}")
                continue
            # Download the file. If the file in download folder exists, delete it first
            if os.path.exists(downloadfilename):
                os.remove(downloadfilename)
            print("Downloading file")
            fcont.download_file(downloadfilename)
            # Test if download was successfull and file sizes are the same
            if not os.path.exists(downloadfilename):
                print("Could not download file test.mp3")
                continue
            if os.path.getsize(uploadfilename) != os.path.getsize(downloadfilename):
                print("Filesizes of uploaded and download file are different.")
            os.remove(downloadfilename)
            # _ = gc.collect()
        dev.close()


def test_7_display_childs() -> None:
    """test to show all cont, but doesn't use walk.
    For walking through the content of a directory tree use walk, it's much faster"""

    def show_childs(dev: mtp_access.PortableDevice, root: str) -> None:
        """Show all cont, but don't use walk"""
        if cont := mtp_access.get_content_from_device_path(dev, root):  # pyright: ignore[reportArgumentType]
            try:
                for child in cont.get_children():
                    fullpath = child.full_filename
                    if child.content_type == mtp_access.WPD_CONTENT_TYPE_STORAGE:
                        print(f"S  {fullpath}")
                    elif child.content_type == mtp_access.WPD_CONTENT_TYPE_DIRECTORY:
                        print(f"D  {fullpath}")
                    elif child.content_type == mtp_access.WPD_CONTENT_TYPE_FILE:
                        print(f"F  {fullpath} Size: {child.size} Created: {child.date_modified}")
                    else:
                        print(f"?  {fullpath}")
                    if child.content_type in (
                        mtp_access.WPD_CONTENT_TYPE_STORAGE,
                        mtp_access.WPD_CONTENT_TYPE_DIRECTORY,
                    ):
                        show_childs(dev, fullpath)
            except OSError as err:
                print(f'Error: {root}: {err}')
        else:
            print(f"{root} not found")

    print("Test 7 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Display childs on test run {i + 1}:")
            for storage in dev.get_content():
                print(f"Storage: {storage.full_filename}")
                show_childs(dev, storage.full_filename)
                break
        print("Closing device")
        dev.close()


def test_8_get_path() -> None:
    """Test get content from partial and fully qualified path"""
    print("Test 8 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Get content from fully and partialy qualified filename on test run {i + 1}:")
            contents = dev.get_content()
            stor = contents[0]
            cont = stor.get_path(f"{stor.full_filename}/DCIM/Camera")
            print(cont.full_filename if cont is not None else "DCIM/Camera with full name not found")
            cont = stor.get_path("DCIM/Camera")
            print(cont.full_filename if cont is not None else "DCIM/Camera with name not found")
            if len(contents) > 1:
                stor = dev.get_content()[1]
                cont = stor.get_path(f"{stor.full_filename}/DCIM/Camera")
                print(cont.full_filename if cont is not None else "DCIM/Camera with full name not found")
                cont = stor.get_path("DCIM/Camera")
                print(cont.full_filename if cont is not None else "DCIM/Camera with name not found")
        dev.close()


def test_9_create_content() -> None:
    """Test to create a folder with create_content"""
    print("Test 9 ------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Create a folder with create_content on test run {i + 1}:")
            stor = dev.get_content()[0]
            mycont = stor.get_path(f"{stor.full_filename}/MyMusic")
            if mycont:
                mycont.remove()
            cont = stor.create_content("MyMusic")
            if cont.full_filename.split(os.sep, 1)[1] != os.path.join("Interner Speicher", "MyMusic"):
                raise OSError("Content differs in test_create_content")
        dev.close()


def test_10_get_child() -> None:
    """Test get_child for directories"""
    print("Test 10------------------------------------------------------------------------")
    for dev in mtp_access.get_portable_devices():
        for i in range(TESTRUNS):
            print(f"Test get_child on test run {i + 1}:")
            stor = dev.get_content()[0]
            mycont = stor.get_child("DCIM")
            if mycont is None or mycont.content_type != mtp_access.WPD_CONTENT_TYPE_DIRECTORY:
                dev.close()
                raise OSError("Test 10 Content is not a directory")
        dev.close()


def main() -> None:
    """Hauptprogramm"""
    print()
    print(TESTNUMBER)
    if TESTNUMBER == 0:  # all test
        test_1_connect_disconnct()
        test_2_list_storages()
        test_3_list_childs_with_walk()
        test_4_get_cont_from_path()
        test_5_create_delete_folder()
        test_6_create_delete_file()
        test_7_display_childs()
        test_8_get_path()
        test_9_create_content()
        test_10_get_child()
    elif TESTNUMBER == 1:
        test_1_connect_disconnct()
    elif TESTNUMBER == 2:
        test_2_list_storages()
    elif TESTNUMBER == 3:
        test_3_list_childs_with_walk()
    elif TESTNUMBER == 4:
        test_4_get_cont_from_path()
    elif TESTNUMBER == 5:
        test_5_create_delete_folder()
    elif TESTNUMBER == 6:
        test_6_create_delete_file()
    elif TESTNUMBER == 7:
        test_7_display_childs()
    elif TESTNUMBER == 8:
        test_8_get_path()
    elif TESTNUMBER == 9:
        test_9_create_content()
    elif TESTNUMBER == 10:
        test_10_get_child()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()

import ctypes
import win32api
import win32file

class libroElectronico:

    def comprueba_KOBO_conectado(self):
        self.drive_types = {0: 'Unknown', 1: 'No Root Directory', 2: 'Removable Disk', 3: 'Local Disk', 4: 'Network Drive', 5: 'Compact Disc', 6: 'RAM Disk'}
        self.kernel32 = ctypes.windll.kernel32
        self.volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        self.fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
        self.serial_number = None
        self.max_component_length = None
        self.file_system_flags = None
        self.nombre_volumen = ""
        self.volumen_kobo = ""

        self.drives = (drive for drive in win32api.GetLogicalDriveStrings ().split ("\000") if drive)

        for drive in self.drives:

            self.rc = self.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive),
            self.volumeNameBuffer,
            ctypes.sizeof(self.volumeNameBuffer),
            self.serial_number,
            self.max_component_length,
            self.file_system_flags,
            self.fileSystemNameBuffer,
            ctypes.sizeof(self.fileSystemNameBuffer)
            )

            self.nombre_volumen = self.volumeNameBuffer.value

            if self.nombre_volumen == "KOBOeReader" and self.drive_types[win32file.GetDriveType (drive)] != "Compact Disc":
                volumen_kobo = drive
                break

        if self.nombre_volumen == "":
            return "No detectado"
        else:
            return volumen_kobo
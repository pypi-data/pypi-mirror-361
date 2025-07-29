# distutils: language = c++

from collections import namedtuple
from enum import Enum
from typing import Tuple, List

import numpy as np
cimport numpy as np
np.import_array()

from .libfli cimport *


DeviceInfo = namedtuple('DeviceInfo', ['domain', 'filename', 'name'])


class FliTemperature(Enum):
    """Enumeration for temperature sensors."""
    INTERNAL = FLI_TEMPERATURE_INTERNAL
    EXTERNAL = FLI_TEMPERATURE_EXTERNAL
    CCD =  FLI_TEMPERATURE_CCD
    BASE = FLI_TEMPERATURE_BASE


class DeviceType(Enum):
    CAMERA = FLIDEVICE_CAMERA
    FILTERWHEEL = FLIDEVICE_FILTERWHEEL


cdef class FliDriver:
    """Wrapper for the FLI driver."""

    @staticmethod
    def list_devices(device_type: DeviceType = DeviceType.CAMERA) -> List[DeviceInfo]:
        """List all FLI USB cameras connected to this computer.

        Returns:
            List of DeviceInfo tuples.
        """

        # define variables
        cdef flidomain_t domain
        cdef char filename[1024]
        cdef char name[1024]

        # create list of USB camera
        if FLICreateList(FLIDOMAIN_USB | device_type.value) != 0:
            raise ValueError('Could not create list of FLI cameras.')

        # init list of devices
        devices = []

        # get first camera
        if FLIListFirst(&domain, <char*>filename, 1024, <char*>name, 1024) == 0:
            # store first device
            devices.append(DeviceInfo(domain=domain, filename=filename, name=name))

            # loop other devices
            while FLIListNext(&domain, <char*>filename, 1024, <char*>name, 1024) == 0:
                # store device
                devices.append(DeviceInfo(domain=domain, filename=filename, name=name))

        # clean up and return
        FLIDeleteList()
        return devices

    """Storage for the device info."""
    cdef object _device_info

    """Storage for link to device."""
    cdef flidev_t _device

    def __init__(self, device_info: DeviceInfo):
        """Create a new driver object for the given device.

        Args:
            device_info: A DeviceInfo obtained from list_devices.
        """
        self._device_info = device_info

    def open(self) -> None:
        """Open driver.

        Raises:
            ValueError: If opening failed.
        """
        res = FLIOpen(&self._device, self._device_info.filename, self._device_info.domain)
        if res != 0:
            raise ValueError('Could not open device.')

    def close(self) -> None:
        """Close driver.

        Raises:
            ValueError: If closing failed.
        """
        res = FLIClose(self._device)
        if res != 0:
            raise ValueError('Could not open device.')

    @property
    def name(self) -> str:
        """Returns the name of the connected device."""
        return self._device_info.name.decode('utf-8')

    def get_window_binning(self) -> Tuple[Tuple[int, int, int, int], Tuple[int, int]]:
        """Get tuple of window and binning dicts.

        Returns:
            Two tuples with (left, top, width, height) and (xbin, ybin)

        Raises:
            ValueError: If fetching readout dimensions failed.
        """

        # variables
        cdef long width, hoffset, hbin, height, voffset, vbin
        
        # get dimensions
        res = FLIGetReadoutDimensions(self._device, &width, &hoffset, &hbin, &height, &voffset, &vbin)
        if res != 0:
            raise ValueError('Could not query readout dimensions.')

        # return window and binning
        return (hoffset, voffset, width, height), (hbin, vbin)

    def get_visible_frame(self) -> Tuple[int, int, int, int]:
        """Returns the visible frame of the connected camera.

        Returns:
            Tuple with left, top, width, and height of full frame.

        Raises:
            ValueError: If fetching visible area fails.
        """

        # variables
        cdef long ul_x, ul_y, lr_x, lr_y

        # get area
        res = FLIGetVisibleArea(self._device, &ul_x, &ul_y, &lr_x, &lr_y)
        if res != 0:
            raise ValueError('Could not query visible area.')

        # return it
        return ul_x, ul_y, lr_x -  ul_x, lr_y - ul_y

    def get_full_frame(self) -> Tuple[int, int, int, int]:
        """Returns the full frame of the connected camera.

        Returns:
            Tuple with left, top, width, and height of full frame.

        Raises:
            ValueError: If fetching visible area fails.
        """

        # variables
        cdef long ul_x, ul_y, lr_x, lr_y

        # get area
        res = FLIGetArrayArea(self._device, &ul_x, &ul_y, &lr_x, &lr_y)
        if res != 0:
            raise ValueError('Could not query total area.')

        # return it
        return ul_x, ul_y, lr_x -  ul_x, lr_y - ul_y

    def set_binning(self, x: int, y: int) -> None:
        """Set the binning.

        Args:
            x: Binning in x direction.
            y: Binning in y direction.

        Raises:
            ValueError: If setting binning failed.
        """

        # set x binning
        res = FLISetHBin(self._device, x)
        if res != 0:
            raise ValueError('Could not set x binning.')

        # set y binning
        res = FLISetVBin(self._device, y)
        if res != 0:
            raise ValueError('Could not set y binning.')

    def set_window(self, left: int, top: int, width: int, height: int) -> None:
        """Sets the window.

        Args:
            left: X offset of window.
            top: Y offset of window.
            width: Window width.
            height: Window height.

        Raises:
            ValueError: If setting the window failed.
        """

        # set window
        res = FLISetImageArea(self._device, left, top, left + width, top + height)
        if res != 0:
            raise ValueError('Could not set window.')

    def init_exposure(self, open_shutter: bool) -> None:
        """Initializes an exposure.

        Args:
            open_shutter: Whether the shutter should be opened for exposure.

        Raises:
            ValueError: If initialization failed.
        """

        # set TDI
        res = FLISetTDI(self._device, 0, 0)
        if res != 0:
            raise ValueError('Could not set TDI.')

        # set frame type
        res = FLISetFrameType(self._device, FLI_FRAME_TYPE_NORMAL if open_shutter else FLI_FRAME_TYPE_DARK)
        if res != 0:
            raise ValueError('Could not set frame type.')

    def set_exposure_time(self, exptime: int) -> None:
        """Sets the exposure time.

        Args:
            exptime: Exposure time in ms.

        Raises:
            ValueError: If setting of exposure time failed.
        """

        # set exptime
        res = FLISetExposureTime(self._device, exptime)
        if res != 0:
            raise ValueError('Could not set exposure time.')

    def start_exposure(self) -> None:
        """Start a new exposure.

        Raises:
            ValueError: If starting the exposure failed.
        """

        # expose
        res = FLIExposeFrame(self._device)
        if res != 0:
            raise ValueError('Could not start exposure.')

    def is_exposing(self) -> bool:
        """Checks, whether the camera is currently exposing

        Returns:
            bool: Whether camera is currently exposing.

        Raises:
            ValueError: If fetching device or exposure status failed.
        """

        # variables
        cdef long status, timeleft

        # get status
        res = FLIGetDeviceStatus(self._device, &status)
        if res != 0:
            raise ValueError('Could not fetch device status.')
        res = FLIGetExposureStatus(self._device, &timeleft)
        if res != 0:
            raise ValueError('Could not fetch remaining exposure time.')

        # finished?
        return (status == FLI_CAMERA_STATUS_UNKNOWN and timeleft == 0) or \
               (status != FLI_CAMERA_STATUS_UNKNOWN and status & FLI_CAMERA_DATA_READY)

    def get_temp(self, channel: FliTemperature) -> float:
        """Returns the temperature of the given sensor.

        Args:
            channel: Sensor to read out.

        Returns:
            float: Temperature of given sensor.

        Raises:
            ValueError: If fetching temperature failed.
        """

        # variables
        cdef double temp

        # get it
        res = FLIReadTemperature(self._device, channel.value, &temp)
        if res != 0:
            raise ValueError('Could not fetch temperature.')

        # return it
        return temp

    def get_cooler_power(self) -> float:
        """Get power of cooling in percent.

        Returns:
            float: Current cooling power.

        Raises:
            ValueError: If fetching cooling power failed.
        """

        # variables
        cdef double power

        # get it
        res = FLIGetCoolerPower(self._device, &power)
        if res != 0:
            raise ValueError('Could not fetch cooler power.')

        # return it
        return power

    def grab_row(self, width: int) -> np.ndarray:
        """Reads out a row from the camera.

        Args:
            width: Width of row to read out.

        Returns:
            ndarray: Data of row.

        Raises:
            ValueError: If reading row failed.
        """

        # create numpy array of given dimensions
        cdef np.ndarray[unsigned short, ndim=1] row = np.zeros((width,), dtype=np.ushort)

        # get pointer to data
        cdef void* row_data = <void*> row.data

        # call library
        res = FLIGrabRow(self._device, row_data, width)
        if res != 0:
            raise ValueError('Could not grab row from camera.')

        # return row
        return row

    def cancel_exposure(self) -> None:
        """Cancel an exposure.

        Raises:
            ValueError: If canceling failed.

        """
        res = FLICancelExposure(self._device)
        if res != 0:
            raise ValueError('Could not cancel exposure.')

    def set_temperature(self, setpoint: float) -> None:
        """Set cooling emperature setpoint.

        Args:
            setpoint: New temperature setpoing.

        Raises:
            ValueError: If setting temperature failed.
        """
        res = FLISetTemperature(self._device, setpoint)
        if res != 0:
            raise ValueError('Could not set temperature.')

    def get_model(self) -> str:
        """Returns the model of the device.

        Returns:
            str: Model of device.
        """

        # variables
        cdef char *model
        cdef size_t len

        # get it
        res = FLIGetModel(self._device, model, len)
        if res != 0:
            raise ValueError('Could not fetch model.')

        # return it
        return str(model)

    def get_serial_string(self) -> str:
        """Returns serial string for camera."""

        # variables
        cdef char serial[1024]

        # get it
        res = FLIGetSerialString(self._device, <char*>serial, 1024)
        if res != 0:
            raise ValueError('Could not fetch serial string.')

        # return it
        return bytes(serial).decode('utf-8')

    def get_filter_pos(self) -> int:
        """Returns current filter position.

        Returns:
            Filter position.
        """

        # variables
        cdef long pos

        # get it
        res = FLIGetFilterPos(self._device, &pos)
        if res != 0:
            raise ValueError('Could not fetch filter position.')

        # return it
        return pos

    def set_filter_pos(self, pos: int) -> None:
        """Set filter position.

        Args:
            pos: New filter position.
        """

        # set filter pos
        res = FLISetFilterPos(self._device, pos)
        if res != 0:
            raise ValueError('Could not set filter position.')

    def set_active_filter_wheel(self, wheel: int) -> None:
        """Set active filter wheel.

        Args:
            wheel: Number of wheel to set active.
        """

        # set active filter wheel
        res = FLISetActiveWheel(self._device, wheel)
        if res != 0:
            raise ValueError('Could not set active filter wheel.')

    def get_active_filter_wheel(self) -> int:
        """Returns active filter wheel.

        Returns:
            Number of active filter wheel.
        """

        # variables
        cdef long wheel

        # get active filter wheel
        res = FLIGetActiveWheel(self._device, &wheel)
        if res != 0:
            raise ValueError('Could not fetch active filter wheel.')
        return wheel

    def get_filter_count(self) -> int:
        """Return filter count.

        Returns:
            Filter count.
        """

        # variables
        cdef long count

        # get active filter wheel
        res = FLIGetFilterCount(self._device, &count)
        if res != 0:
            raise ValueError('Could not fetch filter count.')
        return count

    def get_filter_name(self, pos: int) -> str:
        """Get filter name.

        Args:
            pos: Position of filter.

        Returns: Name of filter.
        """

        # variables
        cdef char name[100]

        # get it
        res = FLIGetFilterName(self._device, pos, <char*>name, 100)
        if res != 0:
            raise ValueError('Could not fetch filter name.')

        # return it
        return bytes(name).decode('utf-8')

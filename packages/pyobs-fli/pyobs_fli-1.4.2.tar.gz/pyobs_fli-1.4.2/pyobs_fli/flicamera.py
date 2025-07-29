import asyncio
import logging
import math
from datetime import datetime, timezone
from typing import Tuple, Any, Optional, Dict, List
import numpy as np

from pyobs.interfaces import ICamera, IWindow, IBinning, ICooling, IAbortable
from pyobs.modules.camera.basecamera import BaseCamera
from pyobs.images import Image
from pyobs.utils.enums import ExposureStatus

from .flibase import FliBaseMixin
from .flidriver import DeviceType

log = logging.getLogger(__name__)


class FliCamera(FliBaseMixin, BaseCamera, ICamera, IWindow, IBinning, ICooling, IAbortable):
    """A pyobs module for FLI cameras."""

    __module__ = "pyobs_fli"

    def __init__(self, setpoint: float = -20.0, **kwargs: Any):
        """Initializes a new FliCamera.

        Args:
            setpoint: Cooling temperature setpoint.
        """
        BaseCamera.__init__(self, **kwargs)
        FliBaseMixin.__init__(self, dev_type=DeviceType.CAMERA, **kwargs)

        # variables
        self._temp_setpoint: Optional[float] = setpoint

        # window and binning
        self._window = (0, 0, 0, 0)
        self._binning = (1, 1)

    async def open(self) -> None:
        """Open module."""
        await BaseCamera.open(self)
        await FliBaseMixin.open(self)

        # check
        if self._driver is None:
            raise ValueError("No driver found.")

        # serial number
        serial = self._driver.get_serial_string()
        log.info("Connected to camera with serial number: %s", serial)

        # get window and binning from camera
        self._window, self._binning = self._driver.get_window_binning()

        # set cooling
        if self._temp_setpoint is not None:
            await self.set_cooling(True, self._temp_setpoint)

    async def close(self) -> None:
        """Close the module."""
        await BaseCamera.close(self)
        await FliBaseMixin.close(self)

    async def get_full_frame(self, **kwargs: Any) -> Tuple[int, int, int, int]:
        """Returns full size of CCD.

        Returns:
            Tuple with left, top, width, and height set.
        """
        if self._driver is None:
            raise ValueError("No camera driver.")
        return self._driver.get_full_frame()

    async def get_window(self, **kwargs: Any) -> Tuple[int, int, int, int]:
        """Returns the camera window.

        Returns:
            Tuple with left, top, width, and height set.
        """
        return self._window

    async def get_binning(self, **kwargs: Any) -> Tuple[int, int]:
        """Returns the camera binning.

        Returns:
            Tuple with x and y.
        """
        return self._binning

    async def set_window(self, left: int, top: int, width: int, height: int, **kwargs: Any) -> None:
        """Set the camera window.

        Args:
            left: X offset of window.
            top: Y offset of window.
            width: Width of window.
            height: Height of window.

        Raises:
            ValueError: If binning could not be set.
        """
        self._window = (left, top, width, height)
        log.info("Setting window to %dx%d at %d,%d...", width, height, left, top)

    async def set_binning(self, x: int, y: int, **kwargs: Any) -> None:
        """Set the camera binning.

        Args:
            x: X binning.
            y: Y binning.

        Raises:
            ValueError: If binning could not be set.
        """
        self._binning = (x, y)
        log.info("Setting binning to %dx%d...", x, y)

    async def list_binnings(self, **kwargs: Any) -> List[Tuple[int, int]]:
        """List available binnings.

        Returns:
            List of available binnings as (x, y) tuples.
        """
        return [(1, 1), (2, 2), (3, 3), (4, 4)]

    async def _expose(self, exposure_time: float, open_shutter: bool, abort_event: asyncio.Event) -> Image:
        """Actually do the exposure, should be implemented by derived classes.

        Args:
            exposure_time: The requested exposure time in seconds.
            open_shutter: Whether or not to open the shutter.
            abort_event: Event that gets triggered when exposure should be aborted.

        Returns:
            The actual image.

        Raises:
            GrabImageError: If exposure was not successful.
        """
        from .flidriver import FliTemperature

        # check driver
        if self._driver is None:
            raise ValueError("No camera driver.")

        # set binning
        log.info("Set binning to %dx%d.", self._binning[0], self._binning[1])
        self._driver.set_binning(*self._binning)

        # set window, divide width/height by binning, from libfli:
        # "Note that the given lower-right coordinate must take into account the horizontal and
        # vertical bin factor settings, but the upper-left coordinate is absolute."
        width = int(math.floor(self._window[2]) / self._binning[0])
        height = int(math.floor(self._window[3]) / self._binning[1])
        log.info(
            "Set window to %dx%d (binned %dx%d) at %d,%d.",
            self._window[2],
            self._window[3],
            width,
            height,
            self._window[0],
            self._window[1],
        )
        self._driver.set_window(self._window[0], self._window[1], width, height)

        # set some stuff
        self._driver.init_exposure(open_shutter)
        self._driver.set_exposure_time(int(exposure_time * 1000.0))

        # get date obs
        log.info(
            "Starting exposure with %s shutter for %.2f seconds...", "open" if open_shutter else "closed", exposure_time
        )
        date_obs = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

        # do exposure
        self._driver.start_exposure()

        # wait exposure
        await self._wait_exposure(abort_event, exposure_time, open_shutter)

        # readout
        log.info("Exposure finished, reading out...")
        await self._change_exposure_status(ExposureStatus.READOUT)
        width = int(math.floor(self._window[2] / self._binning[0]))
        height = int(math.floor(self._window[3] / self._binning[1]))
        img = np.zeros((height, width), dtype=np.uint16)
        for row in range(height):
            img[row, :] = self._driver.grab_row(width)

        # create FITS image and set header
        image = Image(img)
        image.header["DATE-OBS"] = (date_obs, "Date and time of start of exposure")
        image.header["EXPTIME"] = (exposure_time, "Exposure time [s]")
        image.header["DET-TEMP"] = (self._driver.get_temp(FliTemperature.CCD), "CCD temperature [C]")
        image.header["DET-COOL"] = (self._driver.get_cooler_power(), "Cooler power [percent]")
        image.header["DET-TSET"] = (self._temp_setpoint, "Cooler setpoint [C]")

        # instrument and detector
        image.header["INSTRUME"] = (self._driver.name, "Name of instrument")

        # binning
        image.header["XBINNING"] = image.header["DET-BIN1"] = (self._binning[0], "Binning factor used on X axis")
        image.header["YBINNING"] = image.header["DET-BIN2"] = (self._binning[1], "Binning factor used on Y axis")

        # window
        image.header["XORGSUBF"] = (self._window[0], "Subframe origin on X axis")
        image.header["YORGSUBF"] = (self._window[1], "Subframe origin on Y axis")

        # statistics
        image.header["DATAMIN"] = (float(np.min(img)), "Minimum data value")
        image.header["DATAMAX"] = (float(np.max(img)), "Maximum data value")
        image.header["DATAMEAN"] = (float(np.mean(img)), "Mean data value")

        # biassec/trimsec
        full = self._driver.get_visible_frame()
        self.set_biassec_trimsec(image.header, *full)

        # return FITS image
        log.info("Readout finished.")
        return image

    async def _wait_exposure(self, abort_event: asyncio.Event, exposure_time: float, open_shutter: bool) -> None:
        """Wait for exposure to finish.

        Params:
            abort_event: Event that aborts the exposure.
            exposure_time: Exp time in sec.
        """

        while True:
            # aborted?
            if abort_event.is_set():
                await self._change_exposure_status(ExposureStatus.IDLE)
                raise InterruptedError("Aborted exposure.")

            # is exposure finished?
            if self._driver.is_exposing():
                break
            else:
                # sleep a little
                await asyncio.sleep(0.01)

    async def _abort_exposure(self) -> None:
        """Abort the running exposure. Should be implemented by derived class.

        Raises:
            ValueError: If an error occured.
        """
        if self._driver is None:
            raise ValueError("No camera driver.")
        self._driver.cancel_exposure()

    async def get_cooling(self, **kwargs: Any) -> Tuple[bool, float, float]:
        """Returns the current status for the cooling.

        Returns:
            Tuple containing:
                Enabled (bool):         Whether the cooling is enabled
                SetPoint (float):       Setpoint for the cooling in celsius.
                Power (float):          Current cooling power in percent or None.
        """
        if self._driver is None:
            raise ValueError("No camera driver.")
        enabled = self._temp_setpoint is not None
        return (
            enabled,
            self._temp_setpoint if self._temp_setpoint is not None else 99.0,
            self._driver.get_cooler_power(),
        )

    async def get_temperatures(self, **kwargs: Any) -> Dict[str, float]:
        """Returns all temperatures measured by this module.

        Returns:
            Dict containing temperatures.
        """
        from .flidriver import FliTemperature

        if self._driver is None:
            raise ValueError("No camera driver.")
        return {"CCD": self._driver.get_temp(FliTemperature.CCD), "Base": self._driver.get_temp(FliTemperature.BASE)}

    async def set_cooling(self, enabled: bool, setpoint: float, **kwargs: Any) -> None:
        """Enables/disables cooling and sets setpoint.

        Args:
            enabled: Enable or disable cooling.
            setpoint: Setpoint in celsius for the cooling.

        Raises:
            ValueError: If cooling could not be set.
        """
        if self._driver is None:
            raise ValueError("No camera driver.")

        # log
        if enabled:
            log.info("Enabling cooling with a setpoint of %.2f°C...", setpoint)
        else:
            log.info("Disabling cooling and setting setpoint to 20°C...")

        # if not enabled, set setpoint to None
        self._temp_setpoint = setpoint if enabled else None

        # set setpoint
        self._driver.set_temperature(float(setpoint) if setpoint is not None else 20.0)


__all__ = ["FliCamera"]

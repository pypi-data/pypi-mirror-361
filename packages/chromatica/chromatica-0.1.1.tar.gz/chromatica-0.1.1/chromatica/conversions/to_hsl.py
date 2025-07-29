
from .unit_float import UnitFloat
from .to_hsv import unit_rgb_to_hsv, np_rgb_to_hsv
import numpy as np
from numpy import ndarray as NDArray
def hsv_to_hsl(hue_deg: float, saturation: UnitFloat, value: UnitFloat) -> tuple[float, UnitFloat, UnitFloat]:
    """
    Convert HSV (Hue, Saturation, Value) to HSL (Hue, Saturation, Lightness).

    Args:
        hue_deg (float): Hue in degrees [0.0, 360.0).
        saturation (UnitFloat): HSV saturation in [0.0, 1.0].
        value (UnitFloat): HSV value (brightness) in [0.0, 1.0].

    Returns:
        Tuple[float, UnitFloat, UnitFloat]: (Hue in degrees, HSL saturation, lightness), all in [0.0, 1.0].
    """
    s_v = float(saturation)
    v = float(value)

    lightness = UnitFloat(0.5 * v * (2 - s_v))
    denom = 1 - abs(2 * float(lightness) - 1.0)

    if denom == 0:
        hsl_saturation = UnitFloat(0.0)
    else:
        hsl_saturation = UnitFloat((v * s_v) / denom)

    return hue_deg, hsl_saturation, lightness

def unit_rgb_to_hsl(r: UnitFloat, g: UnitFloat, b: UnitFloat) -> tuple[float, UnitFloat, UnitFloat]:
    """
    Convert RGB components to HSL.

    Args:
        r (UnitFloat): Red component in [0.0, 1.0].
        g (UnitFloat): Green component in [0.0, 1.0].
        b (UnitFloat): Blue component in [0.0, 1.0].

    Returns:
        Tuple[float, UnitFloat, UnitFloat]: (Hue in degrees, HSL saturation, lightness).
    """
    hue, saturation, value = unit_rgb_to_hsv(r, g, b)
    return hsv_to_hsl(hue, saturation, value)

def np_hsv_to_hsl(hue_deg: NDArray, saturation: NDArray, value: NDArray) -> NDArray:
    """
    Vectorized HSV → HSL.

    Args:
        hue_deg: array-like or scalar, degrees [0.0,360.0)
        saturation: array-like or scalar, [0.0,1.0]
        value: array-like or scalar, [0.0,1.0]

    Returns:
        hsl: array of shape (...,3): (hue_deg, hsl_saturation, lightness)
    """
    hue_deg = np.asarray(hue_deg)
    s_v = np.asarray(saturation)
    v = np.asarray(value)

    out_shape = np.broadcast(hue_deg, s_v, v).shape

    hue_deg = np.broadcast_to(hue_deg, out_shape)
    s_v = np.broadcast_to(s_v, out_shape)
    v = np.broadcast_to(v, out_shape)

    lightness = 0.5 * v * (2 - s_v)
    denom = 1 - np.abs(2 * lightness - 1)

    hsl_s = np.zeros_like(denom)
    mask = denom > 0
    hsl_s[mask] = (v[mask] * s_v[mask]) / denom[mask]

    hsl = np.stack([hue_deg, hsl_s, lightness], axis=-1)
    return hsl

def np_rgb_to_hsl(r: NDArray, g: NDArray, b: NDArray) -> NDArray:
    """
    Vectorized RGB → HSL.

    Args:
        r, g, b: array-like or scalar, [0.0,1.0]

    Returns:
        hsl: array of shape (...,3): (hue_deg, hsl_saturation, lightness)
    """
    hsv = np_rgb_to_hsv(r, g, b)
    hsl = hsv_to_hsl(hsv[...,0], hsv[...,1], hsv[...,2])
    return hsl
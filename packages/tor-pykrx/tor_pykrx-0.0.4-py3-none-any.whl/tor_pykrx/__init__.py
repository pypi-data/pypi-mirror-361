import platform
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from . import bond
from . import stock
import importlib.resources as importlib_resources


os = platform.system()

if os == "Darwin":
    plt.rc("font", family="AppleGothic")

else:
    font_path = importlib_resources.files("tor_pykrx").joinpath("NanumBarunGothic.ttf")

    fe = fm.FontEntry(
        fname=font_path,
        name="NanumBarunGothic"
    )
    fm.fontManager.ttflist.insert(0, fe)
    plt.rc("font", family=fe.name)

plt.rcParams["axes.unicode_minus"] = False

__all__ = [
    "bond",
    "stock"
]

__version__ = "1.0.48"

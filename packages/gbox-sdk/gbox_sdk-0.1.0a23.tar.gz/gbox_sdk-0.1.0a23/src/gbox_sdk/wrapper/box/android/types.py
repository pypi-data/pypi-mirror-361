from typing import TYPE_CHECKING, List, Union
from typing_extensions import Required, TypedDict

from gbox_sdk.types.v1.boxes.android_install_params import InstallAndroidPkgByURL, InstallAndroidPkgByFile

# Forward references for type annotations
if TYPE_CHECKING:
    from gbox_sdk.wrapper.box.android.app_operator import AndroidAppOperator
    from gbox_sdk.wrapper.box.android.pkg_operator import AndroidPkgOperator


class InstallAndroidAppByLocalFile(TypedDict, total=False):
    apk: Required[str]


AndroidInstall = Union[InstallAndroidPkgByFile, InstallAndroidPkgByURL, InstallAndroidAppByLocalFile]


class ListAndroidApp(TypedDict):
    """Response type for listing Android apps as operators."""

    operators: List["AndroidAppOperator"]


class ListAndroidPkg(TypedDict):
    """Response type for listing Android packages as operators."""

    operators: List["AndroidPkgOperator"]

import os
from typing import List, Optional

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.types import AndroidInstall, ListAndroidPkg
from gbox_sdk.wrapper.box.android.pkg_operator import AndroidPkgOperator
from gbox_sdk.types.v1.boxes.android_get_response import AndroidGetResponse
from gbox_sdk.types.v1.boxes.android_list_pkg_params import AndroidListPkgParams
from gbox_sdk.types.v1.boxes.android_install_response import AndroidInstallResponse
from gbox_sdk.types.v1.boxes.android_uninstall_params import AndroidUninstallParams
from gbox_sdk.types.v1.boxes.android_list_pkg_response import AndroidListPkgResponse


class AndroidPkgManager:
    """
    Manager class for handling Android package operations within a box.

    Provides methods to install, uninstall, list, retrieve, close, and backup Android packages.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox):
        """
        Initialize an AndroidPkgManager instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
        """
        self.client = client
        self.box = box

    def install(self, body: AndroidInstall) -> AndroidInstallResponse:
        """
        Install an Android package on the box.

        Args:
            body (AndroidInstall): Installation parameters, including APK path or URL.

        Returns:
            AndroidInstallResponse: The response of the install operation.
        """
        apk = body["apk"]
        if isinstance(apk, str) and not apk.startswith("http"):
            if not os.path.exists(apk):
                raise FileNotFoundError(f"File {apk} does not exist")
            with open(apk, "rb") as apk_file:
                return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk_file)
        elif isinstance(apk, str) and apk.startswith("http"):
            return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)

        return self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)

    def uninstall(self, package_name: str, params: AndroidUninstallParams) -> None:
        """
        Uninstall an Android package from the box.

        Args:
            package_name (str): The package name of the app to uninstall.
            params (AndroidUninstallParams): Uninstallation parameters.
        """
        keep_data = bool(params.get("keepData", False))
        return self.client.v1.boxes.android.uninstall(package_name, box_id=self.box.id, keep_data=keep_data)

    def list(self, params: Optional[AndroidListPkgParams] = None) -> ListAndroidPkg:
        """
        List all installed Android packages as operator objects.

        Args:
            params (AndroidListPkgParams, optional): Parameters for listing packages.

        Returns:
            ListAndroidPkg: Response containing package operator instances.
        """
        if params is None:
            params = {}
        res = self.client.v1.boxes.android.list_pkg(box_id=self.box.id, **params)
        operators: List[AndroidPkgOperator] = []
        for pkg in res.data:
            # Create AndroidGetResponse using camelCase field names
            android_get_response = AndroidGetResponse(
                apkPath=pkg.apk_path,
                isRunning=pkg.is_running,
                name=pkg.name,
                packageName=pkg.package_name,
                pkgType=pkg.pkg_type,
                version=pkg.version
            )
            operators.append(AndroidPkgOperator(self.client, self.box, android_get_response))
        return ListAndroidPkg(operators=operators)

    def list_info(self, params: Optional[AndroidListPkgParams] = None) -> AndroidListPkgResponse:
        """
        Get detailed information of all installed Android packages.

        Args:
            params (AndroidListPkgParams, optional): Parameters for listing packages.

        Returns:
            AndroidListPkgResponse: Response containing package information.
        """
        if params is None:
            params = {}
        return self.client.v1.boxes.android.list_pkg(box_id=self.box.id, **params)

    def get(self, package_name: str) -> AndroidPkgOperator:
        """
        Get an operator for a specific installed package.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidPkgOperator: Operator for the specified package.
        """
        res = self.client.v1.boxes.android.get(package_name, box_id=self.box.id)
        return AndroidPkgOperator(self.client, self.box, res)

    def get_info(self, package_name: str) -> AndroidGetResponse:
        """
        Get detailed information for a specific installed package.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidGetResponse: Package information response.
        """
        res = self.client.v1.boxes.android.get(package_name, box_id=self.box.id)
        return res

    def close_all(self) -> None:
        """
        Close all running Android packages on the box.
        """
        return self.client.v1.boxes.android.close_all(box_id=self.box.id)

    def backup_all(self) -> BinaryAPIResponse:
        """
        Backup all installed Android packages on the box.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.
        """
        return self.client.v1.boxes.android.backup_all(box_id=self.box.id)

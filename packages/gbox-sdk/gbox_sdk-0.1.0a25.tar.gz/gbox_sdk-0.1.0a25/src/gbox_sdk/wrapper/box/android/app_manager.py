import os
from urllib.parse import urlparse
from urllib.request import url2pathname
from typing_extensions import Optional

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.android.types import AndroidInstall, ListAndroidApp, AndroidUninstall
from gbox_sdk.types.v1.boxes.android_app import AndroidApp
from gbox_sdk.wrapper.box.android.app_operator import AndroidAppOperator
from gbox_sdk.types.v1.boxes.android_install_response import AndroidInstallResponse
from gbox_sdk.types.v1.boxes.android_list_app_response import AndroidListAppResponse


class AndroidAppManager:
    """
    Manager class for handling Android app operations within a box.

    Provides methods to install, uninstall, list, retrieve, close, and backup Android apps.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox):
        """
        Initialize an AndroidAppManager instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
        """
        self.client = client
        self.box = box

    def install(self, body: AndroidInstall) -> AndroidAppOperator:
        """
        Install an Android app on the box.

        Supports multiple APK input formats:
        - Local file path: "/path/to/app.apk"
        - File URL: "file:///path/to/app.apk"
        - HTTP URL: "https://example.com/app.apk"
        - File object or stream

        Args:
            body (AndroidInstall): Installation parameters, including APK path or URL.

        Returns:
            AndroidAppOperator: Operator for the installed app.
        """
        apk = body["apk"]
        if isinstance(apk, str):
            if apk.startswith("file://"):
                # Handle file:// protocol
                parsed_url = urlparse(apk)
                file_path = url2pathname(parsed_url.path)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File {file_path} does not exist")
                with open(file_path, "rb") as apk_file:
                    res = self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk_file)
                    return self._install_res_to_operator(res)
            elif apk.startswith("http"):
                # Handle http/https URLs
                res = self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)
                return self._install_res_to_operator(res)
            else:
                # Handle local file paths
                if not os.path.exists(apk):
                    raise FileNotFoundError(f"File {apk} does not exist")
                with open(apk, "rb") as apk_file:
                    res = self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk_file)
                    return self._install_res_to_operator(res)

        # Handle file objects or other types
        res = self.client.v1.boxes.android.install(box_id=self.box.id, apk=apk)
        return self._install_res_to_operator(res)

    def uninstall(self, package_name: str, params: Optional[AndroidUninstall] = None) -> None:
        """
        Uninstall an Android app from the box.

        Args:
            package_name (str): The package name of the app to uninstall.
            params (AndroidUninstallParams): Uninstallation parameters.
        """
        keep_data = False
        if params is not None:
            keep_data = params.get("keep_data", False)
        return self.client.v1.boxes.android.uninstall(package_name, box_id=self.box.id, keep_data=keep_data)

    def list(self) -> ListAndroidApp:
        """
        List all installed Android apps as operator objects.

        Returns:
            ListAndroidApp: Response containing app operator instances.
        """
        res = self.client.v1.boxes.android.list_app(box_id=self.box.id)
        return ListAndroidApp(operators=[AndroidAppOperator(self.client, self.box, app) for app in res.data])

    def list_info(self) -> AndroidListAppResponse:
        """
        Get detailed information of all installed Android apps.

        Returns:
            AndroidListAppResponse: Response containing app information.
        """
        return self.client.v1.boxes.android.list_app(box_id=self.box.id)

    def get(self, package_name: str) -> AndroidAppOperator:
        """
        Get an operator for a specific installed app.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidAppOperator: Operator for the specified app.
        """
        res = self.client.v1.boxes.android.get_app(package_name, box_id=self.box.id)
        return AndroidAppOperator(self.client, self.box, res)

    def get_info(self, package_name: str) -> AndroidApp:
        """
        Get detailed information for a specific installed app.

        Args:
            package_name (str): The package name of the app.

        Returns:
            AndroidGetResponse: App information response.
        """
        res = self.client.v1.boxes.android.get_app(package_name, box_id=self.box.id)
        return res

    def close_all(self) -> None:
        """
        Close all running Android apps on the box.
        """
        return self.client.v1.boxes.android.close_all(box_id=self.box.id)

    def backup_all(self) -> BinaryAPIResponse:
        """
        Backup all installed Android apps on the box.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.
        """
        return self.client.v1.boxes.android.backup_all(box_id=self.box.id)

    def _install_res_to_operator(self, res: AndroidInstallResponse) -> AndroidAppOperator:
        """
        Convert an install response to an AndroidAppOperator instance.

        Args:
            res (AndroidInstallResponse): The install response.

        Returns:
            AndroidAppOperator: Operator for the installed app.
        """
        activity = next((x for x in res.activities if x.is_launcher), None)
        if activity is None:
            raise ValueError("No launcher activity found")

        app = AndroidApp(
            packageName=res.package_name,
            activityName=activity.name,
            activityClassName=activity.class_name,
        )
        return AndroidAppOperator(self.client, self.box, app)

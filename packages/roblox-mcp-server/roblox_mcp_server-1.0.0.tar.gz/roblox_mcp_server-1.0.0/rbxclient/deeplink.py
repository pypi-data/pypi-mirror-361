import subprocess
import os


def _is_roblox_deeplink_registered_windows():
    import winreg

    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "roblox")
        try:
            winreg.QueryValueEx(key, "URL Protocol")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except FileNotFoundError:
        return False
    except Exception as _e:
        return False


# macOS용 함수
def _is_roblox_deeplink_registered_macos():
    try:
        result = subprocess.run(
            ["open", "-Ra", "roblox"], capture_output=True, text=True, check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as _e:
        return False


def is_roblox_deeplink_registered():
    if os.name == "nt":
        return _is_roblox_deeplink_registered_windows()
    elif os.name == "posix" and os.uname().sysname == "Darwin":
        return _is_roblox_deeplink_registered_macos()
    else:
        return False


class RobloxDeeplink:

    @staticmethod
    def open_game(
        game_id: int,
        user_id: int = None,
        access_code: str = None,
        link_code: str = None,
        game_instance_id: str = None,
        launch_data: dict = None,
        force: bool = False,
    ) -> None:
        if not is_roblox_deeplink_registered() and not force:
            raise RuntimeError("Roblox deeplink is not registered on this system.")

        url = f"roblox://placeId={game_id}"
        if user_id:
            url += f"&userId{user_id}"
        if access_code:
            url += f"&accessCode={access_code}"
        if link_code:
            url += f"&linkCode={link_code}"
        if game_instance_id:
            url += f"&gameInstanceId={game_instance_id}"
        if launch_data:
            url += f"&launchData={launch_data}"

        try:
            if os.name == "nt":
                subprocess.run(["start", url], shell=True, check=True)
            elif os.name == "posix":
                subprocess.run(["open", url], check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to open Roblox game: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e

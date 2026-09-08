import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ==========================================================
# CONFIGURATION
# ==========================================================

MINECRAFT_VERSION = "26.2"
#MINECRAFT_VERSION = "1.21.11"
LOADER = "fabric"

DOWNLOAD_FOLDER = r"C:\Users\Username\Documents\LocatoinOfMods"


# Number of simultaneous downloads
MAX_WORKERS = 5

# Prefer stable releases over beta/alpha
ALLOW_BETA = True
ALLOW_ALPHA = False

PREFERRED_TYPES = ["release"]

if ALLOW_BETA:
    PREFERRED_TYPES.append("beta")

if ALLOW_ALPHA:
    PREFERRED_TYPES.append("alpha")

# Replace the IDs below with your own Modrinth project IDs.
# Name is only used for display.
PROJECTS = {
    "Mod Name": "project_id",
    "Fabric API": "P7dR8mSH"
}

# ==========================================================

API = "https://api.modrinth.com/v2"

session = requests.Session()

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def get_latest_version(project_id):
    """
    Returns the newest compatible version,
    preferring Release > Beta > Alpha.
    """

    url = f"{API}/project/{project_id}/version"

    r = session.get(url, timeout=20)
    r.raise_for_status()

    versions = r.json()

    # Try Release first, then Beta, then Alpha
    for preferred_type in PREFERRED_TYPES:

        for version in versions:

            if (
                version["version_type"] != preferred_type
            ):
                continue

            if (
                MINECRAFT_VERSION in version["game_versions"]
                and LOADER in version["loaders"]
            ):
                return version

    raise Exception(
        f"No compatible {PREFERRED_TYPES} version found for Minecraft {MINECRAFT_VERSION}"
    )


def download_file(url, filename):

    path = os.path.join(DOWNLOAD_FOLDER, filename)

    response = session.get(url, stream=True, timeout=30)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))

    with open(path, "wb") as file:

        with tqdm(
            total=total,
            desc=filename[:35],
            unit="B",
            unit_scale=True,
            leave=True,
        ) as bar:

            for chunk in response.iter_content(8192):

                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

    return filename


def download_project(name, project_id):

    version = get_latest_version(project_id)

    file = version["files"][0]

    filename = file["filename"]

    url = file["url"]

    download_file(url, filename)

    return filename


def main():

    print("=" * 60)
    print("Minecraft Mod Downloader")
    print("=" * 60)
    print(f"Minecraft Version : {MINECRAFT_VERSION}")
    print(f"Loader            : {LOADER}")
    print(f"Download Folder   : {DOWNLOAD_FOLDER}")
    print()

    success = []
    failed = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        futures = {
            executor.submit(download_project, name, pid): name
            for name, pid in PROJECTS.items()
        }

        for future in as_completed(futures):

            name = futures[future]

            try:

                filename = future.result()

                print(f"✓ {name} -> {filename}")

                success.append(name)

            except Exception as e:

                print(f"✗ {name}")
                print(f"    {e}")

                failed.append(name)

    print()
    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"Successful : {len(success)}")
    print(f"Failed     : {len(failed)}")

    if failed:

        print("\nFailed Mods:")

        for mod in failed:
            print(f" - {mod}")


if __name__ == "__main__":
    main()
import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ==========================================================
# CONFIGURATION
# ==========================================================

MINECRAFT_VERSION = "1.21.8"
LOADER = "fabric"

# CurseForge API key
# Get one from the CurseForge API developer portal.
API_KEY = "PUT_YOUR_CURSEFORGE_API_KEY_HERE"

DOWNLOAD_FOLDER = r"C:\Users\Username\Documents\LocationOfTheMods"

# Number of simultaneous downloads
MAX_WORKERS = 5

# ----------------------------------------------------------
# Release settings
#
# CurseForge release types:
#   1 = Release
#   2 = Beta
#   3 = Alpha
# ----------------------------------------------------------

ALLOW_BETA = True
ALLOW_ALPHA = False

# CurseForge Minecraft loader type:
#   4 = Fabric
#   1 = Forge
#   2 = Cauldron
#   3 = LiteLoader
#   0 = Any
#
# Change this if you use Forge instead of Fabric.
LOADER_TYPE = 4

# ----------------------------------------------------------
# Add your CurseForge project IDs here.
#
# Example:
# PROJECTS = {
#     "Sodium": 394468,
#     "Fabric API": 306612,
# }
# ----------------------------------------------------------

PROJECTS = {
    "Sodium": 0,
    "Fabric API": 0,
    # "Lithium": 0,
    # "Litematica": 0,
}

# ==========================================================

API = "https://api.curseforge.com/v1"

session = requests.Session()
session.headers.update({
    "x-api-key": API_KEY,
    "Accept": "application/json",
})

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def check_api_key():
    if not API_KEY or API_KEY == "PUT_YOUR_CURSEFORGE_API_KEY_HERE":
        raise Exception(
            "No CurseForge API key configured. "
            "Put your API key in API_KEY at the top of the script."
        )


def get_release_types():
    """
    Returns the allowed CurseForge release types.

    1 = Release
    2 = Beta
    3 = Alpha
    """
    release_types = [1]

    if ALLOW_BETA:
        release_types.append(2)

    if ALLOW_ALPHA:
        release_types.append(3)

    return release_types


def get_latest_version(project_id):
    """
    Finds the newest CurseForge file compatible with:
      - selected Minecraft version
      - selected loader
      - selected release type

    Release is always preferred over Beta.
    Beta is preferred over Alpha.
    """

    url = f"{API}/mods/{project_id}/files"

    params = {
        "gameVersion": MINECRAFT_VERSION,
        "modLoaderType": LOADER_TYPE,
        "pageSize": 50,
    }

    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()

    files = response.json().get("data", [])

    if not files:
        raise Exception(
            f"No files found for Minecraft {MINECRAFT_VERSION} "
            f"and loader {LOADER}."
        )

    allowed_types = get_release_types()

    # CurseForge normally returns newest files first, but we
    # explicitly check release type priority so an alpha/beta
    # cannot win over an available release.
    for release_type in allowed_types:

        for file in files:

            if file.get("releaseType") != release_type:
                continue

            return file

    raise Exception(
        f"No allowed Release/Beta/Alpha version found "
        f"for Minecraft {MINECRAFT_VERSION}."
    )


def get_download_url(project_id, file_id):
    """
    Gets the actual download URL for a CurseForge file.
    """

    url = f"{API}/mods/{project_id}/files/{file_id}/download-url"

    response = session.get(url, timeout=30)
    response.raise_for_status()

    download_url = response.json().get("data")

    if not download_url:
        raise Exception("CurseForge did not provide a download URL.")

    return download_url


def download_file(url, filename):
    """
    Downloads a file with a progress bar.
    """

    path = os.path.join(DOWNLOAD_FOLDER, filename)

    response = session.get(
        url,
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))

    with open(path, "wb") as file:

        with tqdm(
            total=total,
            desc=filename[:40],
            unit="B",
            unit_scale=True,
            leave=True,
        ) as bar:

            for chunk in response.iter_content(chunk_size=8192):

                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))

    return filename


def download_project(name, project_id):
    """
    Finds and downloads the newest compatible file.
    """

    if not project_id:
        raise Exception("Project ID has not been configured.")

    file = get_latest_version(project_id)

    file_id = file["id"]
    filename = file["fileName"]

    display_name = file.get("displayName", filename)
    release_type = file.get("releaseType")

    release_names = {
        1: "Release",
        2: "Beta",
        3: "Alpha",
    }

    release_name = release_names.get(
        release_type,
        "Unknown",
    )

    download_url = get_download_url(
        project_id,
        file_id,
    )

    print(
        f"[{name}] {display_name} "
        f"({release_name})"
    )

    download_file(
        download_url,
        filename,
    )

    return filename, release_name


def main():

    check_api_key()

    print("=" * 60)
    print("CurseForge Minecraft Mod Downloader")
    print("=" * 60)
    print(f"Minecraft Version : {MINECRAFT_VERSION}")
    print(f"Loader            : {LOADER}")
    print(f"Download Folder   : {DOWNLOAD_FOLDER}")
    print(f"Beta Allowed      : {ALLOW_BETA}")
    print(f"Alpha Allowed     : {ALLOW_ALPHA}")
    print()

    success = []
    failed = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        futures = {
            executor.submit(
                download_project,
                name,
                project_id,
            ): name

            for name, project_id in PROJECTS.items()
        }

        for future in as_completed(futures):

            name = futures[future]

            try:

                filename, release_type = future.result()

                print(
                    f"✓ {name} -> "
                    f"{filename} [{release_type}]"
                )

                success.append(name)

            except Exception as error:

                print(f"✗ {name}")
                print(f"    Error: {error}")

                failed.append(name)

    print()
    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"Successful : {len(success)}")
    print(f"Failed     : {len(failed)}")

    if failed:

        print()
        print("Failed Mods:")

        for mod in failed:
            print(f" - {mod}")


if __name__ == "__main__":
    main()

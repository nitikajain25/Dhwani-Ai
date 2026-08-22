from pathlib import Path
import requests
import sys
import time


FILES = {
    "hi": (
        "https://huggingface.co/datasets/"
        "ai4bharat/MSMARCO-XI/resolve/main/"
        "train/hintrain.parquet"
    ),
    "mr": (
        "https://huggingface.co/datasets/"
        "ai4bharat/MSMARCO-XI/resolve/main/"
        "train/martrain.parquet"
    ),
}


CHUNK_SIZE = 8 * 1024 * 1024
MAX_RETRIES = 10


def get_remote_size(url: str) -> int:
    response = requests.head(
        url,
        allow_redirects=True,
        timeout=60,
    )

    response.raise_for_status()

    size = response.headers.get("content-length")

    if not size:
        raise RuntimeError(
            "Could not determine remote file size."
        )

    return int(size)


def download(language: str):

    url = FILES[language]

    output_dir = Path("data/raw")
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = output_dir / f"{language}train.parquet"

    print("=" * 70)
    print(f"Downloading {language}")
    print("=" * 70)

    print(f"URL: {url}")
    print(f"Output: {output_file}")

    remote_size = get_remote_size(url)

    print(
        f"Remote size: "
        f"{remote_size / (1024 ** 3):.2f} GB"
    )

    if output_file.exists():
        local_size = output_file.stat().st_size
    else:
        local_size = 0

    print(
        f"Local file size: "
        f"{local_size / (1024 ** 3):.2f} GB"
    )

    # ------------------------------------------------------------
    # Already complete
    # ------------------------------------------------------------

    if local_size == remote_size:

        print()
        print("File is already completely downloaded.")
        print(f"File: {output_file}")
        return

    # ------------------------------------------------------------
    # Local file is larger than remote file
    # ------------------------------------------------------------

    if local_size > remote_size:

        raise RuntimeError(
            "Local file is larger than the remote file. "
            "Delete the local file and restart."
        )

    # ------------------------------------------------------------
    # Resume or start
    # ------------------------------------------------------------

    if local_size > 0:

        print()
        print(
            f"Resuming download from byte "
            f"{local_size:,}"
        )

    else:

        print()
        print("Starting download from the beginning.")

    downloaded = local_size

    # ------------------------------------------------------------
    # Retry loop
    # ------------------------------------------------------------

    retries = 0

    while downloaded < remote_size:

        headers = {
            "Range": f"bytes={downloaded}-",
        }

        try:

            print()
            print(
                f"Connecting from byte "
                f"{downloaded:,}..."
            )

            response = requests.get(
                url,
                headers=headers,
                stream=True,
                timeout=(30, 120),
            )

            response.raise_for_status()

            # ----------------------------------------------------
            # Verify that the server actually honored Range
            # ----------------------------------------------------

            content_range = response.headers.get(
                "Content-Range"
            )

            if local_size > 0:

                if not content_range:

                    raise RuntimeError(
                        "Server did not return Content-Range. "
                        "Cannot safely resume."
                    )

            # ----------------------------------------------------
            # Append to existing file
            # ----------------------------------------------------

            with open(output_file, "ab") as f:

                for chunk in response.iter_content(
                    chunk_size=CHUNK_SIZE
                ):

                    if not chunk:
                        continue

                    f.write(chunk)
                    downloaded += len(chunk)

                    percent = (
                        downloaded / remote_size * 100
                    )

                    print(
                        f"\rProgress: "
                        f"{percent:6.2f}% "
                        f"({downloaded / (1024 ** 3):.2f} / "
                        f"{remote_size / (1024 ** 3):.2f} GB)",
                        end="",
                    )

            print()

            # ----------------------------------------------------
            # Check whether download is complete
            # ----------------------------------------------------

            actual_size = output_file.stat().st_size

            if actual_size == remote_size:

                print()
                print("=" * 70)
                print("DOWNLOAD COMPLETE")
                print("=" * 70)
                print(f"File: {output_file}")
                print(
                    f"Size: "
                    f"{actual_size / (1024 ** 3):.2f} GB"
                )

                return

            if actual_size > remote_size:

                raise RuntimeError(
                    "Downloaded file became larger than "
                    "the expected remote file."
                )

            downloaded = actual_size

            print(
                f"Connection ended early at "
                f"{downloaded / (1024 ** 3):.2f} GB."
            )

            retries += 1

        except (
            requests.exceptions.RequestException,
            RuntimeError,
        ) as e:

            retries += 1

            print()
            print(
                f"Download interrupted "
                f"(attempt {retries}/{MAX_RETRIES})."
            )

            print(f"Reason: {e}")

            if retries >= MAX_RETRIES:

                raise RuntimeError(
                    "Download failed after "
                    f"{MAX_RETRIES} attempts. "
                    "The partial file has been preserved."
                )

            wait_time = min(
                5 * retries,
                60,
            )

            print(
                f"Waiting {wait_time} seconds "
                "before retrying..."
            )

            time.sleep(wait_time)

    print()
    print("Download finished.")


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage:")
        print(
            "  python -m scripts.download_dataset hi"
        )
        print(
            "  python -m scripts.download_dataset mr"
        )

        sys.exit(1)

    language = sys.argv[1].lower()

    if language not in FILES:

        print(
            "Language must be 'hi' or 'mr'."
        )

        sys.exit(1)

    download(language)
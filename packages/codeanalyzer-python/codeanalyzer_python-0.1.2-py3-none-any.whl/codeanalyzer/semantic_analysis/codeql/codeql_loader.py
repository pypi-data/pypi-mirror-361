import platform
import requests
import zipfile
from pathlib import Path
from codeanalyzer.utils import logger
from tqdm import tqdm


class CodeQLLoader:
    @classmethod
    def detect_platform_key(cls) -> str:
        system = platform.system()
        arch = platform.machine().lower()

        if system == "Linux" and arch in {"x86_64", "amd64"}:
            return "codeql-linux64.zip"
        elif system == "Darwin" and arch in {"x86_64", "arm64"}:
            return "codeql-osx64.zip"
        elif system == "Windows" and arch in {"x86_64", "amd64"}:
            return "codeql-win64.zip"
        else:
            return "codeql.zip"  # fallback to generic binary if needed

    @classmethod
    def get_codeql_download_url(cls, expected_filename: str) -> str:
        response = requests.get(
            "https://api.github.com/repos/github/codeql-cli-binaries/releases/latest"
        )
        response.raise_for_status()
        for asset in response.json()["assets"]:
            if asset["name"] == expected_filename:
                return asset["browser_download_url"]
        raise RuntimeError(f"No asset found for filename: {expected_filename}")

    @classmethod
    def download_and_extract_codeql(cls, temp_dir: Path) -> Path:
        filename = cls.detect_platform_key()
        download_url = cls.get_codeql_download_url(filename)

        temp_dir.mkdir(parents=True, exist_ok=True)
        archive_path = temp_dir / filename

        logger.info(f"Downloading CodeQL CLI from {download_url}")
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get("content-length", 0))
            block_size = 8192  # 8KB

            with (
                open(archive_path, "wb") as f,
                tqdm(
                    total=total_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Downloading CodeQL",
                ) as bar,
            ):
                for chunk in r.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    bar.update(len(chunk))

        extract_dir = temp_dir / filename.replace(".zip", "")
        extract_dir.mkdir(exist_ok=True)

        print(f"Extracting CodeQL CLI to {extract_dir}")
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)

        codeql_bin = next(extract_dir.rglob("codeql"), None)
        if not codeql_bin or not codeql_bin.exists():
            raise FileNotFoundError("CodeQL binary not found in extracted contents.")

        return codeql_bin.resolve()

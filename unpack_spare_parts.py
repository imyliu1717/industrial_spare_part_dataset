#!/usr/bin/env python3
"""Extract the two spare-parts dataset bundles on Windows, macOS, or Linux.

Requires Python 3.9+; no additional packages or unzip/WSL needed.
Windows:
    py unpack_spare_parts.py "C:\\Users\\Yushi\\Downloads\\dataset"
macOS / Linux:
    python3 unpack_spare_parts.py ~/Downloads/dataset
Custom output (the images directory itself, not its parent):
    python3 unpack_spare_parts.py /path/to/downloads -o /path/to/images

Input: All_Files.zip and All_Files_2.zip, containing 19 inner ZIPs.
Output: images/{query,train,val,test}/phone and images/gallery/{phone,studio}.
The output directory must not already exist. Original archives are preserved.
Temporary disk usage is the restored data plus one inner ZIP and one extracted
chunk. Only publish the output after every chunk succeeds. Keep ZIPs unchanged
during the run. macOS packaging metadata is ignored.
"""

import argparse
import os
import shutil
import stat
import sys
import tempfile
import zipfile
from pathlib import Path


BUNDLES = (
    ("All_Files.zip", [(f"train_{i}", "train", "phone") for i in range(1, 8)]
     + [(f"test_{i}", "test", "phone") for i in range(1, 5)] + [("val", "val", "phone")]),
    ("All_Files_2.zip", [("query", "query", "phone"), ("gallery_phone", "gallery", "phone")]
     + [(f"gallery_studio_{i}", "gallery", "studio") for i in range(1, 6)]),
)
DESTINATIONS = ("query/phone", "gallery/phone", "gallery/studio", "train/phone", "val/phone", "test/phone")
METADATA = {"__MACOSX", ".DS_Store"}


def safe_parts(name):
    # Validate paths ourselves instead of allowing extraction to sanitize them.
    if not name or "\\" in name or ":" in name or "\x00" in name:
        raise ValueError(f"Unsafe ZIP path: {name!r}")
    parts = name.rstrip("/").split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"Unsafe ZIP path: {name!r}")
    if os.name == "nt":
        reserved = {"CON", "PRN", "AUX", "NUL"}
        reserved.update(f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10))
        for part in parts:
            if (part.endswith((".", " ")) or any(c in '<>"|?*' or ord(c) < 32 for c in part)
                    or part.split(".", 1)[0].upper() in reserved):
                raise ValueError(f"ZIP name is not supported on Windows: {name!r}")
    return parts


def metadata(parts):
    return any(part in METADATA for part in parts)


def check_entry(info):
    kind = stat.S_IFMT(info.external_attr >> 16)
    if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
        raise ValueError(f"Unsupported ZIP entry (e.g. symbolic link): {info.filename}")
    if info.flag_bits & 1:
        raise ValueError(f"Encrypted ZIP is unsupported: {info.filename}")


def plan_bundles(folder):
    plans = []
    for name, specs in BUNDLES:
        path = folder / name
        if not path.is_file():
            raise ValueError(f"Missing outer ZIP: {path}")
        with zipfile.ZipFile(path) as bundle:
            entries = []
            for info in bundle.infolist():
                parts = safe_parts(info.filename)
                if not info.is_dir() and not metadata(parts):
                    entries.append((info, parts[-1].casefold()))
            selected = []
            for stem, split, camera in specs:
                matches = [info for info, basename in entries if basename in (stem, stem + ".zip")]
                if len(matches) != 1:
                    raise ValueError(f"Expected exactly one {stem}.zip in {name}; found {len(matches)}")
                check_entry(matches[0])
                selected.append((matches[0], stem, split, camera))
        plans.append((path, selected))
    return plans


def extract_chunk(path, target):
    target.mkdir()
    with zipfile.ZipFile(path) as archive:
        entries = []
        for info in archive.infolist():
            parts = safe_parts(info.filename)
            if metadata(parts):
                continue
            check_entry(info)
            entries.append((info, parts))
        for info, parts in entries:
            destination = target.joinpath(*parts)
            if info.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                # Exclusive creation rejects duplicate names, including OS name
                # collisions. Reading to EOF also validates the member's CRC.
                with archive.open(info) as source, destination.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)


def locate_payload(folder, stem, split, camera):
    wrappers = {"images", stem, split, camera}
    if split == "gallery":
        wrappers.add("source")
    current = folder
    while True:
        children = sorted((p for p in current.iterdir() if p.name not in METADATA), key=lambda p: p.name)
        if len(children) == 1 and children[0].is_dir() and children[0].name in wrappers:
            current = children[0]
        else:
            return current, children


def unpack(plans, output):
    output.parent.mkdir(parents=True, exist_ok=True)
    # Keep staging on the destination filesystem so moving object folders and
    # publishing images/ use renames rather than copying the whole dataset.
    with tempfile.TemporaryDirectory(prefix=".unpack-spare-parts-", dir=output.parent) as temporary:
        work = Path(temporary)
        images = work / "images"
        for destination in DESTINATIONS:
            images.joinpath(*destination.split("/")).mkdir(parents=True)
        step = object_count = 0
        for path, selected in plans:
            print(f"Opening {path.name} ...", flush=True)
            with zipfile.ZipFile(path) as bundle:
                for info, stem, split, camera in selected:
                    step += 1
                    print(f"[{step}/19] {stem}.zip -> images/{split}/{camera}", flush=True)
                    inner_zip = work / "chunk.zip"
                    with bundle.open(info) as source, inner_zip.open("xb") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
                    raw = work / "raw"
                    extract_chunk(inner_zip, raw)
                    _, objects = locate_payload(raw, stem, split, camera)
                    if not objects:
                        raise ValueError(f"No object folders found in {stem}")
                    for obj in objects:
                        if not obj.is_dir():
                            raise ValueError(f"Expected an object folder, found: {obj.name} in {stem}")
                        destination = images / split / camera / obj.name
                        if destination.exists():
                            raise ValueError(f"Duplicate object folder: {split}/{camera}/{obj.name}")
                        obj.rename(destination)
                    object_count += len(objects)
                    print(f"  Added {len(objects)} object folders.", flush=True)
                    shutil.rmtree(raw)
                    inner_zip.unlink()
        if output.exists() or output.is_symlink():
            raise ValueError(f"Output appeared during extraction: {output}")
        images.rename(output)
    print(f"Done: restored {object_count} object folders to {output}", flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("zip_folder", type=Path, help="Folder containing both outer ZIP files")
    parser.add_argument("-o", "--output", type=Path,
                        help="Output images directory (default: ZIP_FOLDER/images); must not exist")
    parser.add_argument("--dry-run", action="store_true", help="Check required inner ZIP names without extracting")
    args = parser.parse_args(argv)
    folder = args.zip_folder.expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"ZIP folder does not exist: {folder}")
    output = args.output.expanduser() if args.output else folder / "images"
    if output.is_symlink():
        raise ValueError(f"Output is a symbolic link: {output}")
    output = output.resolve()
    if output.exists():
        raise ValueError(f"Output already exists: {output}. Choose a new directory with --output.")
    plans = plan_bundles(folder)
    if args.dry_run:
        for path, selected in plans:
            for _, stem, split, camera in selected:
                print(f"{path.name}: {stem}.zip -> images/{split}/{camera}")
        print("Dry run complete. Inner ZIP contents and CRCs are checked during extraction.")
        return 0
    unpack(plans, output)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("Interrupted; temporary extraction files removed.", file=sys.stderr)
        sys.exit(130)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

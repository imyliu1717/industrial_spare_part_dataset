#!/usr/bin/env bash
# Restore All_Files.zip and All_Files_2.zip into images/{split}/{camera}/{object_id}.
# Usage: bash unpack_spare_parts.sh /path/to/downloads [/path/to/images]
# Requires Bash 4+ and Linux utilities including unzip. No Python required.
# The output images directory must not already exist. Original ZIPs are kept.
# Space needed: restored images + extracted inner ZIPs from one outer archive
# + one currently extracted chunk. Temporary files are removed on exit.
set -Eeuo pipefail

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }

if (( $# < 1 || $# > 2 )); then
    printf 'Usage: bash %s ZIP_FOLDER [OUTPUT_IMAGES_FOLDER]\n' "$0" >&2
    exit 2
fi
for tool in unzip find sort mktemp realpath dirname mkdir mv rm; do
    command -v "$tool" >/dev/null 2>&1 || die "Required command not found: $tool"
done
input_dir=$(realpath -e -- "$1")
[[ -d "$input_dir" ]] || die "Not a directory: $input_dir"
output_dir=$(realpath -m -- "${2:-$input_dir/images}")
[[ ! -e "$output_dir" && ! -L "$output_dir" ]] || die "Output already exists: $output_dir"
for outer in All_Files.zip All_Files_2.zip; do
    [[ -f "$input_dir/$outer" ]] || die "Missing outer ZIP: $input_dir/$outer"
done

mkdir -p -- "$(dirname -- "$output_dir")"
work_dir=$(mktemp -d -- "$(dirname -- "$output_dir")/.unpack-spare-parts.XXXXXXXX")
cleanup() { rm -rf -- "$work_dir"; }
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'printf "Extraction failed at line %s; temporary files will be removed.\n" "$LINENO" >&2' ERR

for split in query train val test; do
    mkdir -p -- "$work_dir/images/$split/phone"
done
mkdir -p -- "$work_dir/images/gallery/phone" "$work_dir/images/gallery/studio"

# Peel recognized wrapper folders ONLY when each is the sole real entry.
# Supported examples: object_id/...; phone/object_id/...; train_1/phone/...;
# images/train/phone/...; images/gallery/studio/...; images/source/studio/...
# macOS packaging metadata is ignored.
locate_payload() {
    local current=$1 stem=$2 split=$3 camera=$4 child base
    local -a children
    while true; do
        mapfile -d '' -t children < <(
            find "$current" -mindepth 1 -maxdepth 1 \
                ! -name '__MACOSX' ! -name '.DS_Store' -print0 | sort -z
        )
        (( ${#children[@]} == 1 )) || break
        child=${children[0]}
        [[ -d "$child" && ! -L "$child" ]] || break
        base=${child##*/}
        if [[ "$base" == images || "$base" == "$stem" || "$base" == "$split" || "$base" == "$camera" ]]; then
            current=$child
        elif [[ "$split" == gallery && "$base" == source ]]; then
            current=$child
        else
            break
        fi
    done
    payload=$current
}

unpack_chunk() {
    local stem=$1 split=$2 camera=$3 zip_path object object_id target
    local -a matches objects
    mapfile -d '' -t matches < <(
        find "$work_dir/outer" -type f \( -iname "$stem.zip" -o -iname "$stem" \) -print0
    )
    (( ${#matches[@]} == 1 )) || die "Expected exactly one $stem.zip inside the outer ZIP; found ${#matches[@]}"
    zip_path=${matches[0]}
    printf 'Extracting %-22s -> images/%s/%s\n' "${zip_path##*/}" "$split" "$camera"
    mkdir -- "$work_dir/raw"
    unzip -q -n "$zip_path" -d "$work_dir/raw" </dev/null
    [[ -z $(find "$work_dir/raw" -type l -print -quit) ]] || die "Symbolic links found in $stem"
    locate_payload "$work_dir/raw" "$stem" "$split" "$camera"
    mapfile -d '' -t objects < <(
        find "$payload" -mindepth 1 -maxdepth 1 \
            ! -name '__MACOSX' ! -name '.DS_Store' -print0 | sort -z
    )
    (( ${#objects[@]} > 0 )) || die "No object folders found in $stem"
    for object in "${objects[@]}"; do
        [[ -d "$object" ]] || die "Expected an object folder, found: $object"
        object_id=${object##*/}
        target="$work_dir/images/$split/$camera/$object_id"
        [[ ! -e "$target" && ! -L "$target" ]] || die "Duplicate object folder: $split/$camera/$object_id"
        mv -- "$object" "$target"
    done
    printf '  Added %s object folders.\n' "${#objects[@]}"
    rm -rf -- "$work_dir/raw"
    rm -- "$zip_path"
}

printf 'Extracting All_Files.zip ...\n'
mkdir -- "$work_dir/outer"
unzip -q -n "$input_dir/All_Files.zip" -d "$work_dir/outer" </dev/null
for index in {1..7}; do unpack_chunk "train_$index" train phone; done
for index in {1..4}; do unpack_chunk "test_$index" test phone; done
unpack_chunk val val phone
rm -rf -- "$work_dir/outer"

printf 'Extracting All_Files_2.zip ...\n'
mkdir -- "$work_dir/outer"
unzip -q -n "$input_dir/All_Files_2.zip" -d "$work_dir/outer" </dev/null
unpack_chunk query query phone
unpack_chunk gallery_phone gallery phone
for index in {1..5}; do unpack_chunk "gallery_studio_$index" gallery studio; done
rm -rf -- "$work_dir/outer"

# Publish only after every chunk has been extracted and organized successfully.
[[ ! -e "$output_dir" && ! -L "$output_dir" ]] || die "Output appeared during extraction: $output_dir"
mv -T -- "$work_dir/images" "$output_dir"
printf '\nDone. Dataset restored to: %s\n' "$output_dir"

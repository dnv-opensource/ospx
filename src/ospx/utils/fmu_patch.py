from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

EMBEDDED_XML_SCAN_WINDOW = 200000


@dataclass
class ParameterInfo:
    name: str
    vr: str
    fmi_type: str
    start_value: str


@dataclass
class EmbeddedOccurrence:
    dll_name: str
    old_value: str
    old_len: int
    offset_start: int
    offset_end: int


@dataclass
class PatchResult:
    input_fmu: Path
    output_fmu: Path
    param: str
    value: str
    model_replacements: int
    embedded_replacements: int
    wrote_anything: bool


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_model_description(xml_bytes: bytes) -> list[ParameterInfo]:
    root = ET.fromstring(xml_bytes)
    vars_parent = root.find("ModelVariables")
    if vars_parent is None:
        return []

    params: list[ParameterInfo] = []
    for sv in vars_parent.findall("ScalarVariable"):
        name = sv.get("name", "")
        vr = sv.get("valueReference", "")
        type_tag = None
        start_value = ""
        for child in list(sv):
            if child.tag in ("Real", "Integer", "Boolean", "String", "Enumeration"):
                type_tag = child.tag
                start_value = child.get("start", "")
                break
        if type_tag is None:
            type_tag = "Unknown"
        params.append(ParameterInfo(name=name, vr=vr, fmi_type=type_tag, start_value=start_value))
    return params


def build_model_patch_patterns(param: str, fmi_type: str | None) -> list[re.Pattern[bytes]]:
    tags = [fmi_type] if fmi_type else ["Real", "Integer", "Boolean", "String", "Enumeration"]
    escaped_param = re.escape(param).encode("ascii", errors="strict")
    patterns: list[re.Pattern[bytes]] = []
    for tag in tags:
        tag_b = tag.encode("ascii")
        patterns.append(
            re.compile(
                rb'(<ScalarVariable[^>]*name="' + escaped_param + rb'"[^>]*>\s*<' + tag_b + rb'\b[^>]*\bstart=")([^"]*)(")',
                re.DOTALL,
            )
        )
    return patterns


def patch_model_description(xml_bytes: bytes, param: str, new_value: str, fmi_type: str | None) -> tuple[bytes, int]:
    value_b = new_value.encode("utf-8")
    total_replacements = 0
    patched = xml_bytes
    for pattern in build_model_patch_patterns(param, fmi_type):
        def repl(m: re.Match[bytes]) -> bytes:
            return m.group(1) + value_b + m.group(3)

        patched, n = pattern.subn(repl, patched)
        total_replacements += n
    return patched, total_replacements


def find_embedded_hmf_region(dll_bytes: bytes) -> tuple[int, int] | None:
    marker = b"<hopsanmodelfile"
    start = dll_bytes.find(marker)
    if start < 0:
        return None
    end_marker = b"</hopsanmodelfile>"
    end = dll_bytes.find(end_marker, start)
    if end >= 0:
        end += len(end_marker)
    else:
        end = min(len(dll_bytes), start + EMBEDDED_XML_SCAN_WINDOW)
    return start, end


def find_embedded_param_occurrences(dll_name: str, dll_bytes: bytes, param: str) -> list[EmbeddedOccurrence]:
    region = find_embedded_hmf_region(dll_bytes)
    if region is None:
        return []
    start, end = region
    hay = dll_bytes[start:end]
    pattern = re.compile(
        rb'<parameter\b[^>]*\bname="' + re.escape(param).encode("ascii", errors="strict") + rb'"[^>]*\bvalue="([^"]*)"[^>]*/?>',
        re.DOTALL,
    )
    result: list[EmbeddedOccurrence] = []
    for m in pattern.finditer(hay):
        old_val_b = m.group(1)
        result.append(
            EmbeddedOccurrence(
                dll_name=dll_name,
                old_value=old_val_b.decode("utf-8", errors="replace"),
                old_len=len(old_val_b),
                offset_start=start + m.start(1),
                offset_end=start + m.end(1),
            )
        )
    return result


def patch_embedded_param_values(
    dll_bytes: bytes,
    occurrences: list[EmbeddedOccurrence],
    new_value: str,
    pad_byte: bytes,
    allow_grow: bool,
) -> bytes:
    new_b = new_value.encode("utf-8")
    out = bytearray(dll_bytes)
    for occ in occurrences:
        if len(new_b) > occ.old_len and not allow_grow:
            raise ValueError(
                f"New value is longer than embedded slot in {occ.dll_name} at offset {occ.offset_start}: new={len(new_b)} old={occ.old_len}."
            )
        if len(new_b) < occ.old_len:
            replacement = new_b + (pad_byte * (occ.old_len - len(new_b)))
        else:
            replacement = new_b
        out[occ.offset_start:occ.offset_end] = replacement
    return bytes(out)


def extract_fmu(input_fmu: Path, tmp_dir: Path) -> None:
    with zipfile.ZipFile(input_fmu, "r") as z:
        z.extractall(tmp_dir)


def repack_fmu(src_dir: Path, output_fmu: Path) -> None:
    with zipfile.ZipFile(output_fmu, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _dirs, files in os.walk(src_dir):
            for fn in files:
                fp = Path(root) / fn
                z.write(fp, fp.relative_to(src_dir).as_posix())


def list_dll_paths(root_dir: Path) -> list[Path]:
    return sorted(root_dir.rglob("*.dll"))


def inspect_fmu(input_fmu: Path, param_filter: str | None = None) -> int:
    with zipfile.ZipFile(input_fmu, "r") as z:
        names = z.namelist()
        if "modelDescription.xml" not in names:
            print("ERROR: modelDescription.xml missing")
            return 2
        xml_bytes = z.read("modelDescription.xml")
        params = parse_model_description(xml_bytes)
        if param_filter:
            params = [p for p in params if p.name == param_filter]
        print(f"FMU: {input_fmu}")
        print("ModelDescription parameters:")
        if not params:
            print("  (none found for filter)")
        else:
            for p in params:
                print(f"  - name={p.name!r}, vr={p.vr}, type={p.fmi_type}, start={p.start_value!r}")
        dll_names = [n for n in names if n.lower().endswith(".dll")]
        print("Embedded DLL XML matches:")
        any_occ = False
        for dn in dll_names:
            dll_bytes = z.read(dn)
            targets = [param_filter] if param_filter else [p.name for p in params]
            for target in sorted(set(t for t in targets if t)):
                for occ in find_embedded_param_occurrences(dn, dll_bytes, target):
                    any_occ = True
                    print(f"  - dll={occ.dll_name}, param={target!r}, value={occ.old_value!r}, len={occ.old_len}, offset={occ.offset_start}")
        if not any_occ:
            print("  (no embedded XML parameter matches found)")
    return 0


def default_output_name(input_fmu: Path) -> Path:
    return input_fmu.with_name(input_fmu.stem + "_patched" + input_fmu.suffix)


def safe_backup(path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(path.name + f".backup_{ts}")
    shutil.copy2(path, backup)
    return backup


def patch_fmu_parameter(
    input_fmu: str | Path,
    *,
    param: str,
    value: str,
    output_fmu: str | Path | None = None,
    inplace: bool = False,
    fmi_type: str | None = None,
    scope: str = "both",
    dry_run: bool = False,
    verify: bool = False,
    no_backup: bool = False,
    dll_pad: str = "space",
    dll_grow: bool = False,
    embedded_old_value: str | None = None,
    all_embedded_matches: bool = False,
) -> PatchResult:
    input_path = Path(input_fmu).resolve()
    output_path = Path(output_fmu).resolve() if output_fmu else default_output_name(input_path)
    if inplace:
        output_path = input_path
    tmp_dir = Path(tempfile.mkdtemp(prefix="fmu_patch_"))
    wrote_anything = False
    try:
        extract_fmu(input_path, tmp_dir)
        md_path = tmp_dir / "modelDescription.xml"
        if not md_path.exists():
            raise ValueError("modelDescription.xml not found in FMU")

        model_replacements = 0
        embedded_replacements = 0
        model_current_start: str | None = None

        if scope in ("model", "both"):
            xml_bytes = md_path.read_bytes()
            model_params = parse_model_description(xml_bytes)
            matches = [p for p in model_params if p.name == param]
            if len(matches) == 1:
                model_current_start = matches[0].start_value
            patched_xml, model_replacements = patch_model_description(xml_bytes, param, value, fmi_type)
            if model_replacements > 0:
                wrote_anything = True
                if not dry_run:
                    md_path.write_bytes(patched_xml)

        if scope in ("dll", "both"):
            pad_byte = {"space": b" ", "nul": b"\x00"}[dll_pad]
            for dll_path in list_dll_paths(tmp_dir):
                rel = dll_path.relative_to(tmp_dir).as_posix()
                dll_bytes = dll_path.read_bytes()
                occs_all = find_embedded_param_occurrences(rel, dll_bytes, param)
                occs = occs_all
                if embedded_old_value is not None:
                    occs = [o for o in occs if o.old_value.rstrip(" ") == embedded_old_value]
                elif model_current_start is not None and not all_embedded_matches:
                    occs = [o for o in occs if o.old_value.rstrip(" ") == model_current_start]
                elif len(occs_all) > 1 and not all_embedded_matches:
                    unique_values = sorted(set(o.old_value.rstrip(" ") for o in occs_all))
                    raise ValueError(
                        f"Ambiguous embedded matches in {rel} for parameter {param!r}: {unique_values}."
                    )
                if not occs:
                    continue
                embedded_replacements += len(occs)
                wrote_anything = True
                if not dry_run:
                    dll_path.write_bytes(patch_embedded_param_values(dll_bytes, occs, value, pad_byte, dll_grow))

        if not wrote_anything:
            return PatchResult(input_path, output_path, param, value, model_replacements, embedded_replacements, False)

        if not dry_run:
            if output_path.exists() and output_path != input_path and not no_backup:
                safe_backup(output_path)
            if output_path == input_path and not no_backup:
                safe_backup(input_path)
            repack_fmu(tmp_dir, output_path)
            if verify:
                inspect_fmu(output_path, param_filter=param)

        return PatchResult(input_path, output_path, param, value, model_replacements, embedded_replacements, True)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generic FMU parameter patcher (modelDescription + embedded DLL XML).")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inspect = sub.add_parser("inspect", help="Inspect FMU parameters and embedded XML values")
    p_inspect.add_argument("--input", default="baseMath.fmu", help="Input FMU path")
    p_inspect.add_argument("--param", default=None, help="Optional parameter name filter")

    p_patch = sub.add_parser("patch", help="Patch one parameter to a new value")
    p_patch.add_argument("--input", default="baseMath.fmu", help="Input FMU path")
    p_patch.add_argument("--output", default=None, help="Output FMU path (default: <input>_patched.fmu)")
    p_patch.add_argument("--inplace", action="store_true", help="Patch input FMU in place")
    p_patch.add_argument("--param", required=True, help="Parameter name to patch")
    p_patch.add_argument("--value", required=True, help="New value")
    p_patch.add_argument("--fmi-type", default=None, help="Optional FMI type filter")
    p_patch.add_argument("--scope", choices=["model", "dll", "both"], default="both")
    p_patch.add_argument("--dry-run", action="store_true")
    p_patch.add_argument("--verify", action="store_true")
    p_patch.add_argument("--no-backup", action="store_true")
    p_patch.add_argument("--dll-pad", choices=["space", "nul"], default="space")
    p_patch.add_argument("--dll-grow", action="store_true")
    p_patch.add_argument("--embedded-old-value", default=None)
    p_patch.add_argument("--all-embedded-matches", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "inspect":
        input_fmu = Path(args.input).resolve()
        if not input_fmu.exists():
            print(f"ERROR: input FMU not found: {input_fmu}")
            return 2
        return inspect_fmu(input_fmu, param_filter=args.param)
    if args.command == "patch":
        input_fmu = Path(args.input).resolve()
        if not input_fmu.exists():
            print(f"ERROR: input FMU not found: {input_fmu}")
            return 2
        try:
            result = patch_fmu_parameter(
                input_fmu=input_fmu,
                param=args.param,
                value=args.value,
                output_fmu=args.output,
                inplace=args.inplace,
                fmi_type=args.fmi_type,
                scope=args.scope,
                dry_run=args.dry_run,
                verify=args.verify,
                no_backup=args.no_backup,
                dll_pad=args.dll_pad,
                dll_grow=args.dll_grow,
                embedded_old_value=args.embedded_old_value,
                all_embedded_matches=args.all_embedded_matches,
            )
        except ValueError as exc:
            print(f"ERROR: {exc}")
            return 2
        print("Patch plan/result:")
        print(f"  input:  {result.input_fmu}")
        print(f"  output: {result.output_fmu}")
        print(f"  scope:  {args.scope}")
        print(f"  param:  {args.param!r}")
        print(f"  value:  {args.value!r}")
        print(f"  modelDescription replacements: {result.model_replacements}")
        print(f"  embedded DLL replacements:     {result.embedded_replacements}")
        if not result.wrote_anything:
            print("No matching targets found. Nothing changed.")
            return 1
        if args.dry_run:
            print("Dry-run enabled, no files written.")
            return 0
        print(f"Patched FMU written: {result.output_fmu}")
        print(f"SHA256: {sha256(result.output_fmu)}")
        return 0
    return 2

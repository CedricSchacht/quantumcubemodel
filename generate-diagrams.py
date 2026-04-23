#!/usr/bin/env -S uv run --script

import os
from pathlib import Path
import shutil
import subprocess
from textwrap import dedent
import numpy as np
from PIL import Image

def gen_coef():
    return {
        f"single coef":
        dedent(rf"""
            \qcmxCoef[70]{{0.71}}
            \qcmxRenderCoef{{$\ket{{\phi}}$}}
        """)
    }

def gen_states_1q():
    return dict([
        (f"single qubit {orientation}", 
        dedent(rf"""
            \def\qcmxOrientationQ{{{orientation}}}
            \qcmxO[80]{{0.5}}
            \qcmxI[185]{{0.81}}
            \qcmxRenderQ{{}}
        """)) 
        for orientation in ["x", "y", "z"]
    ])
    
def gen_states_2q():
    return dict([
        (f"two qubits {orientation}", 
        dedent(rf"""
            \def\qcmxOrientationQQ{{{orientation}}}
            \qcmxOO[45]{{0.18}}
            \qcmxOI[180]{{0.37}}
            \qcmxIO[120]{{0.55}}
            \qcmxII[70]{{0.73}}
            \qcmxRenderQQ{{}}
        """)) 
        for orientation in ["xy", "xz", "yz"]
    ])
    
def gen_states_3q():
    return dict([
        (f"three qubits {orientation}", 
        dedent(rf"""
            \def\qcmxOrientationQQQ{{{orientation}}}
            \qcmxOOO[25]{{0.07}} 
            \qcmxOOI[50]{{0.14}}
            \qcmxOIO[75]{{0.21}} 
            \qcmxOII[100]{{0.28}}
            \qcmxIOO[125]{{0.35}} 
            \qcmxIOI[150]{{0.42}}
            \qcmxIIO[175]{{0.49}} 
            \qcmxIII[200]{{0.56}}
            \qcmxRenderQQQ{{}}
        """)) 
        for orientation in ["xyz"]
    ])
    
def single_qubit_gate(gate: str):
    def generator():
        return dict([
            (f"{gate} {orientation[0]} {orientation[2]}", 
            dedent(rf"""
                \node at (0, 2) {{{gate} {orientation[0]} {orientation[2]}}};
                \def\qcmxOrientation{"Q"*orientation[1]}{{{orientation[0]}}}
                \qcmxRender{gate}{"Q"*orientation[1]}{{{orientation[2]}}}
            """))
            for orientation in [
                ("x", 1, "x"), 
                ("y", 1, "y"), 
                ("z", 1, "z"),

                ("xy", 2, "x"),
                ("xy", 2, "y"),
                ("xz", 2, "x"),
                ("xz", 2, "z"),
                ("yz", 2, "y"),
                ("yz", 2, "z"),

                ("xyz", 3, "x"),
                ("xyz", 3, "y"),
                ("xyz", 3, "z"),
            ]
        ])
    return generator
    
def gen_cnot_gate():
    return dict([
        (f"CNot {orientation[0]} {orientation[2]}", 
        dedent(rf"""
            \node at (0, 2) {{CNot {orientation[0]} {orientation[2]}}};
            \def\qcmxOrientation{"Q"*orientation[1]}{{{orientation[0]}}}
            \qcmxRenderCNot{"Q"*orientation[1]}{{{orientation[2]}}}
        """))
        for orientation in [
                ("xy", 2, "xy"),
                ("xy", 2, "yx"),
                ("xz", 2, "xz"),
                ("xz", 2, "zx"),
                ("yz", 2, "yz"),
                ("yz", 2, "zy"),

                ("xyz", 3, "xy"),
                ("xyz", 3, "xz"),
                ("xyz", 3, "yx"),
                ("xyz", 3, "yz"),
                ("xyz", 3, "zx"),
                ("xyz", 3, "zy"),
        ]
    ])

def gen_ccnot_gate():
    return dict([
        (f"CCNot {orientation}", 
        dedent(rf"""
            \node at (0, 2) {{CCNot {orientation}}};
            \qcmxRenderCCNotQQQ{{{orientation}}}
        """))
        for orientation in [
            "xyz",
            "yxz",
            "xzy",
            "yzx",
            "zxy",
            "zyx",
        ]
    ])  

def gen_measure():
    return dict([
        (f"Measure {orientation[0]} {orientation[2]}", 
        dedent(rf"""
            \node at (0, 2) {{Measure {orientation[0]} {orientation[2]}}};
            \def\qcmxOrientation{"Q"*orientation[1]}{{{orientation[0]}}}
            \qcmxRenderMeasure{"Q"*orientation[1]}{{{orientation[2]}}}
        """))
        for orientation in [
                ("x", 1, "x"), 
                ("y", 1, "y"), 
                ("z", 1, "z"),

                ("xy", 2, "x"),
                ("xy", 2, "y"),
                ("xy", 2, "xy"),
                ("xz", 2, "x"),
                ("xz", 2, "z"),
                ("xz", 2, "xz"),
                ("yz", 2, "y"),
                ("yz", 2, "z"),
                ("yz", 2, "yz"),

                ("xyz", 3, "x"),
                ("xyz", 3, "y"),
                ("xyz", 3, "z"),
                ("xyz", 3, "xy"),
                ("xyz", 3, "xz"),
                ("xyz", 3, "yz"),
                ("xyz", 3, "xyz"),
                
        ]
    ])
    
def generate_all(out_dir: str, generators):
    begin_document = dedent(rf"""
        \documentclass[crop=false]{{standalone}} % no auto-crop
        \usepackage[
          paperwidth=30cm,
          paperheight=30cm,
        ]{{geometry}}
        \usepackage{{../quantumcubemodel}}
        \begin{{document}}
        \pagestyle{{empty}}
        \begin{{qcmx}}
        """)
    
    end_document = dedent(rf"""
        \end{{qcmx}}
        \end{{document}}
        """)
    
    for generator in generators:
        files = generator()
        for file_name, content in files.items():
            with open(f"{out_dir}/{file_name}.tex", "w") as f:
                f.write(begin_document + content + end_document)             

def compile_tex_file(tex_path: Path) -> bool:
    cmd = [
        "latexmk",
        "-lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-shell-escape",
        "-f",
        f"-outdir=./out",
        tex_path.name,
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=tex_path.parent,
            timeout=30,       # seconds; adjust as needed
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("ERROR: latexmk not found. Is it installed and on your PATH?")
        return False

def compile_all_tex_files(out_dir: str):
    tex_files = sorted(Path(out_dir).glob("*.tex"))
    failed = []

    for tex in tex_files:
        print(f"Compiling {tex.name} ...", end=" ", flush=True)
        ok = compile_tex_file(tex)
        if ok:
            print("OK")
        else:
            print("FAILED")
            failed.append(tex.name)
            
    return tex_files, failed
    
def pdf_to_png(pdf_path: Path, png_path: Path, timeout: int = 60) -> bool:
    cmd = [
        "pdftoppm",
        str(pdf_path),
        str(png_path.with_suffix("")),  # prefix without .png
        "-singlefile",
        "-png",
    ]
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        print(f"\nTIMEOUT converting {pdf_path.name} to PNG")
        if e.stdout:
            print("stdout:")
            print(e.stdout)
        if e.stderr:
            print("stderr:")
            print(e.stderr)
        return False
    except FileNotFoundError:
        print("ERROR: pdftoppm not found. Install poppler / poppler-utils.")
        return False

    if result.returncode != 0:
        print(f"\nPDF→PNG conversion FAILED for {pdf_path.name}")
        print("stdout:")
        print(result.stdout)
        print("stderr:")
        print(result.stderr)
        return False

    return True       
    
def convert_all_pdfs(out_dir: str):
    pdf_files = sorted(Path(f"{out_dir}/out").glob("*.pdf"))
    for pdf in pdf_files:
        png = pdf.with_suffix(".png")
        print(f"Converting {pdf.name} -> {png.name} ...", end=" ", flush=True)
        ok = pdf_to_png(pdf, png)
        if ok:
            print("OK")
        else:
            print("FAILED")
    
def load_png_as_array(path: Path) -> np.ndarray:
    img = Image.open(path).convert("RGBA")
    return np.array(img, dtype=np.uint8)

def png_similarity(a_path: Path, b_path: Path) -> float:
    a = load_png_as_array(a_path)
    b = load_png_as_array(b_path)

    if a.shape != b.shape:
        raise Exception("shape error")
        return 0.0

    # pixel is equal only if all channels are equal
    same_pixels = np.all(a == b, axis=-1)   # shape (H, W), bool
    similarity = same_pixels.mean()         # fraction between 0 and 1

    return float(similarity)

def golden_test(out_dir: str, golden_dir: str, threashold: float):
    generated_png_dir = Path(f"{out_dir}/out")
    generated_pngs = sorted(generated_png_dir.glob("*.png"))

    missing_golden = []       # generated .png that lacks golden counterpart
    missing_generated = []    # golden .png that has no generated counterpart
    differing_pngs = []       # (filename, similarity)

    # Map names for quick lookup
    generated_names = {p.name for p in generated_pngs}
    golden_pngs = sorted(Path(golden_dir).glob("*.png"))
    golden_names = {p.name for p in golden_pngs}

    # Check each generated PNG
    for gen in generated_pngs:
        if gen.name not in golden_names:
            missing_golden.append(gen.name)
            continue
        golden = Path(golden_dir) / gen.name
        sim = png_similarity(gen, golden)
        if sim < threashold:
            differing_pngs.append((gen.name, sim))

    # Check golden PNGs that have no generated counterpart
    for gold in golden_pngs:
        if gold.name not in generated_names:
            missing_generated.append(gold.name)
            
    return generated_pngs, golden_pngs, missing_generated, missing_golden, differing_pngs

def print_summary(tex_files, failed_tex, generated_pngs, golden_pngs, missing_generated, missing_golden, differing_pngs, threashold):
    print("\n=== Summary ===")

    # LaTeX compilation result
    print("\nLaTeX compilation:")
    print(f"  Total .tex files:        {len(tex_files)}")
    print(f"  Successfully compiled:   {len(tex_files) - len(failed_tex)}")
    print(f"  Failed:                  {len(failed_tex)}")
    if failed_tex:
        print("  Failed files:")
        for name in failed_tex:
            print(f"    - {name}")

    # PNG comparison result
    print("\nPNG comparison (generated vs golden):")
    print(f"  Generated PNGs found:    {len(generated_pngs)}")
    print(f"  Golden PNGs found:       {len(golden_pngs)}")
    print(f"  Similarity threshold:    {threashold:.2%}")

    if missing_golden:
        print("\n  Generated PNGs without golden counterpart:")
        for name in missing_golden:
            print(f"    - {name}")

    if missing_generated:
        print("\n  Golden PNGs without generated counterpart:")
        for name in missing_generated:
            print(f"    - {name}")

    if differing_pngs:
        print("\n  PNGs that differ significantly (similarity < "
              f"{threashold:.2%}):")
        for name, sim in differing_pngs:
            print(f"    - {name}: similarity = {sim:.4f}")
    else:
        print("\n  No PNG pairs differ significantly (all >= "
              f"{threashold:.2%}).")

def png_diff_image(a_path: Path, b_path: Path, out_path: Path) -> None:
    print(out_path)
    a = load_png_as_array(a_path)
    b = load_png_as_array(b_path)

    # If sizes differ, crop to common area (or you can early-return)
    h = min(a.shape[0], b.shape[0])
    w = min(a.shape[1], b.shape[1])
    a = a[:h, :w, :]
    b = b[:h, :w, :]

    # same pixel if all channels equal
    same = np.all(a == b, axis=-1)  # shape (h, w), bool

    # create diff image: gray background, red where different
    diff_img = np.zeros((h, w, 4), dtype=np.uint8)
    diff_img[..., :] = [128, 128, 128, 255]  # gray

    # mark different pixels in red
    diff_img[~same] = [255, 0, 0, 255]

    Image.fromarray(diff_img).save(out_path)

def png_diff_images(out_dir: str, golden_dir: str, diff_dir: str, diffs):
    if Path(diff_dir).exists():
        shutil.rmtree(Path(diff_dir))
    Path(diff_dir).mkdir(parents=True, exist_ok=True)
    for file, score in diffs:
        png_diff_image(Path(f"{out_dir}/out/{file}"), Path(f"{golden_dir}/{file}"), Path(f"{diff_dir}/{file}"))

def main():
    OUT_DIR = "./generated-diagrams"
    GOLDEN_DIR = "./golden"
    DIFF_DIR = "./diff"
    threashold = 0.999
    generators = [
        gen_coef,
        gen_states_1q,
        gen_states_2q,
        gen_states_3q,
        *[single_qubit_gate(gate) for gate in ["Hadamard", "PauliX", "PauliY", "PauliZ", "Wireframe"]],
        gen_cnot_gate,
        gen_ccnot_gate,
        gen_measure,
    ]
    os.makedirs(OUT_DIR, exist_ok=True)
    generate_all(out_dir=OUT_DIR, generators=generators)
    tex_files, failed_tex = compile_all_tex_files(out_dir=OUT_DIR)
    convert_all_pdfs(out_dir=OUT_DIR)
    generated_pngs, golden_pngs, missing_generated, missing_golden, differing_pngs = golden_test(
        out_dir=OUT_DIR, 
        golden_dir=GOLDEN_DIR, 
        threashold=threashold
    )
    print_summary(
        tex_files=tex_files, 
        failed_tex=failed_tex,
        generated_pngs=generated_pngs, 
        golden_pngs=golden_pngs, 
        missing_generated=missing_generated, 
        missing_golden=missing_golden, 
        differing_pngs=differing_pngs,
        threashold=threashold,
    )
    png_diff_images(
        out_dir=OUT_DIR, 
        golden_dir=GOLDEN_DIR, 
        diff_dir=DIFF_DIR, 
        diffs=differing_pngs
    )

if __name__ == "__main__":
    main()
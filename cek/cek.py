import sys
from pathlib import Path

import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor


PY = Language(tspython.language())
parser = Parser(PY)

# Mencari komentar yang mengandung TODO atau FIXME.
Q_TODO = Query(PY, '((comment) @c (#match? @c "TODO|FIXME"))')

# Menangkap node fungsi sekaligus nama fungsinya.
Q_FUNCTION = Query(
    PY,
    "(function_definition name: (identifier) @nama) @fungsi"
)

SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules"}


def cari_error(node):
    """Mengembalikan node ERROR/MISSING pertama yang ditemukan."""
    if node.is_error or node.is_missing:
        return node

    for child in node.children:
        hasil = cari_error(child)
        if hasil is not None:
            return hasil

    return None


def cek_file(path):
    try:
        source = path.read_bytes()
    except OSError as error:
        print(f"[GAGAL BACA] {path}: {error}")
        return

    tree = parser.parse(source)

    # Fitur 1: komentar TODO/FIXME.
    todo_nodes = QueryCursor(Q_TODO).captures(tree.root_node).get("c", [])
    for node in todo_nodes:
        print(
            f"[TODO/FIXME] {path}:{node.start_point[0] + 1}: "
            f"{node.text.decode(errors='replace').strip()}"
        )

    # Fitur 2: fungsi yang panjangnya lebih dari 30 baris.
    for _, captures in QueryCursor(Q_FUNCTION).matches(tree.root_node):
        nama_nodes = captures.get("nama", [])
        fungsi_nodes = captures.get("fungsi", [])

        if not nama_nodes or not fungsi_nodes:
            continue

        nama = nama_nodes[0].text.decode(errors="replace")
        fungsi = fungsi_nodes[0]
        jumlah_baris = fungsi.end_point[0] - fungsi.start_point[0] + 1

        if jumlah_baris > 30:
            print(
                f"[FUNGSI PANJANG] {path}:{fungsi.start_point[0] + 1}: "
                f"{nama} ({jumlah_baris} baris)"
            )

    # Fitur 3: file yang memiliki error sintaks.
    if tree.root_node.has_error:
        error_node = cari_error(tree.root_node)
        if error_node is not None:
            jenis = "MISSING" if error_node.is_missing else "ERROR"
            print(
                f"[SYNTAX ERROR] {path}:{error_node.start_point[0] + 1}: "
                f"node {jenis} ({error_node.type})"
            )
        else:
            print(f"[SYNTAX ERROR] {path}: pohon memiliki error.")


def main():
    if len(sys.argv) != 2:
        print("Penggunaan: python cek.py <folder>")
        raise SystemExit(1)

    folder = Path(sys.argv[1])

    if not folder.exists() or not folder.is_dir():
        print(f"Folder tidak ditemukan: {folder}")
        raise SystemExit(1)

    jumlah_file = 0
    for path in folder.rglob("*.py"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue

        jumlah_file += 1
        cek_file(path)

    print(f"\nPemeriksaan selesai. Total file Python: {jumlah_file}")


if __name__ == "__main__":
    main()

import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

print("=== 0. Uji Awal (x = 1) ===")
tree_awal = parser.parse(b"x = 1\n")
print(tree_awal.root_node)
print()

kode_fungsi = b"""def sapa(nama):
    return nama
"""

kode_ifelse = b"""if x > 0:
    y = 1
else:
    y = 0
"""

kode_class = b"""class Mahasiswa:
    def halo(self):
        return "Hai"
"""

for judul, kode in [
    ("1. Fungsi", kode_fungsi),
    ("2. If/Else", kode_ifelse),
    ("3. Class", kode_class),
]:
    print(f"=== {judul} ===")
    tree = parser.parse(kode)
    print(tree.root_node)
    print()

print("=== 4. Node Anonim pada function_definition ===")
tree_fn = parser.parse(kode_fungsi)
fn_node = tree_fn.root_node.children[0]
for c in fn_node.children:
    print(f"  {c.type!r:15} -> {'bernama' if c.is_named else 'anonim'}")

print("\n=== 5. Node Anonim di dalam parameters ===")
params_node = fn_node.child_by_field_name("parameters")
for c in params_node.children:
    print(f"  {c.type!r:15} -> {'bernama' if c.is_named else 'anonim'}")
print()

print("=== 6. Kode Rusak (ERROR / MISSING) ===")
kode_rusak = b"""def sapa(nama)
    return nama
"""
tree_rusak = parser.parse(kode_rusak)
print(tree_rusak.root_node)
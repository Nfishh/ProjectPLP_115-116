import tree_sitter_python as tspython
from tree_sitter import Language, Parser

parser = Parser(Language(tspython.language()))

k_assign = b'x = 1\n'
k_fungsi = b'def halo(nama):\n    return nama\n'
k_ifelse = b'if x > 5:\n    print("besar")\nelse:\n    print("kecil")\n'
k_kelas  = b'class Hewan:\n    def suara(self):\n        return "..."\n'

for judul, kode in [("assign", k_assign), ("fungsi", k_fungsi),
                    ("if_else", k_ifelse), ("kelas", k_kelas)]:
    print("==", judul)
    print(parser.parse(kode).root_node)
    print()

# Anak langsung function_definition
fungsi = parser.parse(k_fungsi).root_node.children[0]
print("== anak-anak function_definition")
for c in fungsi.children:
    print(c.type, "bernama" if c.is_named else "anonim")

# Anak-anak parameters
parameters = fungsi.child_by_field_name("parameters")
print("\n== anak-anak parameters")
for c in parameters.children:
    print(c.type, "bernama" if c.is_named else "anonim")

print(len(parameters.children), len(parameters.named_children))

# Anak langsung class_definition
kelas = parser.parse(k_kelas).root_node.children[0]
print("\n== anak-anak class_definition")
for c in kelas.children:
    print(c.type, "bernama" if c.is_named else "anonim")
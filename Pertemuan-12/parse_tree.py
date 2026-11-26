
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Membaca source code
source_path = Path("simple_order_management.py")
source_code = source_path.read_bytes()

# Memuat grammar Python
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# Melakukan parsing
tree = parser.parse(source_code)
root_node = tree.root_node

# Membuat CST dalam bentuk bertingkat
def format_tree(node, source, level=0):
    indent = "    " * level
    result = indent + node.type

    # Menampilkan nama field jika tersedia
    lines = [result]

    for index, child in enumerate(node.children):
        if child.is_named:
            field_name = node.field_name_for_child(index)

            child_text = format_tree(child, source, level + 1)

            if field_name:
                child_text = (
                    "    " * (level + 1)
                    + field_name + ":\n"
                    + child_text.split("\n", 1)[-1]
                )

            lines.append(child_text)

    return "\n".join(lines)


# Menyimpan CST format S-expression
Path("cst_output.txt").write_text(
    str(root_node),
    encoding="utf-8"
)

# Menyimpan CST format bertingkat
pretty_cst = format_tree(root_node, source_code)
Path("cst_pretty.txt").write_text(
    pretty_cst,
    encoding="utf-8"
)


# Memeriksa kesalahan sintaksis
def find_errors(node):
    errors = []

    if node.type == "ERROR" or node.is_missing:
        errors.append(node)

    for child in node.children:
        errors.extend(find_errors(child))

    return errors


errors = find_errors(root_node)

print("=== TREE-SITTER PARSING RESULT ===")
print(f"Root node: {root_node.type}")
print(f"Source file: {source_path.name}")
print("CST S-expression: cst_output.txt")
print("CST Hierarchical: cst_pretty.txt")
print(f"Syntax errors found: {len(errors)}")

if errors:
    print("\n=== SYNTAX ERRORS ===")
    for error in errors:
        print(
            f"Type: {error.type}, "
            f"Line: {error.start_point.row + 1}, "
            f"Column: {error.start_point.column + 1}"
        )
else:
    print("\nNo syntax errors detected.")

print("\nParsing completed.")

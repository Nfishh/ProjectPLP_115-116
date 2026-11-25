import sys
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Query, QueryCursor

PY = Language(tspython.language())
parser = Parser(PY)

kode = open(sys.argv[1], "rb").read()
pola = open(sys.argv[2]).read()
tree = parser.parse(kode)

temuan = []
hasil = QueryCursor(Query(PY, pola)).matches(tree.root_node)
for _, cap in hasil:
    nama = cap["fn"][0].text.decode()
    fn_node = cap["fn"][0]
    args_node = cap["args"][0]
    baris = fn_node.start_point[0] + 1
    argumen = [child.text.decode("utf-8") for child in args_node.named_children]
    temuan.append((baris, argumen))

temuan.sort(key=lambda item: item[0])

for baris, argumen in temuan:
    print(f"{nama} baris {baris}: {argumen}")
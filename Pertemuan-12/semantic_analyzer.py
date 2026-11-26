
from pathlib import Path
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# ==================================================
# 1. PARSING SOURCE CODE
# ==================================================

source = Path("simple_order_management.py").read_bytes()

language = Language(tspython.language())
parser = Parser(language)
tree = parser.parse(source)
root = tree.root_node


def text(node):
    return source[node.start_byte:node.end_byte].decode("utf-8")


def field(node, name):
    return node.child_by_field_name(name)


def walk(node):
    yield node
    for child in node.named_children:
        yield from walk(child)


def line(node):
    return node.start_point.row + 1


def infer(node, env):
    if node is None:
        return None

    kind = node.type

    if kind == "string":
        return "str"
    if kind == "integer":
        return "int"
    if kind == "float":
        return "float"
    if kind == "true" or kind == "false":
        return "bool"
    if kind == "identifier":
        return env.get(text(node))

    if kind == "call":
        fn = field(node, "function")
        if fn and fn.type == "identifier":
            return text(fn)

    if kind == "binary_operator":
        left = infer(field(node, "left"), env)
        right = infer(field(node, "right"), env)

        operator = next(
            (c.type for c in node.children if c.type in
             ["+", "-", "*", "/", "%"]),
            None
        )

        if operator == "+" and "str" in (left, right):
            return "str"

        if left == "float" or right == "float":
            return "float"
        if left == "int" and right == "int":
            return "int"

    return None


# ==================================================
# 2. MENGUMPULKAN INFORMASI CLASS
# ==================================================

classes = {}
class_nodes = {}

for node in root.named_children:
    if node.type != "class_definition":
        continue

    name = text(field(node, "name"))
    body = field(node, "body")

    class_nodes[name] = node
    classes[name] = {
        "attributes": set(),
        "methods": {},
        "list_elements": {}
    }

    for method in body.named_children:
        if method.type != "function_definition":
            continue

        method_name = text(field(method, "name"))
        params_node = field(method, "parameters")
        params = {}
        return_type = field(method, "return_type")

        for param in params_node.named_children:
            if param.type == "typed_parameter":
                param_name = param.named_children[0]
                annotation = field(param, "type")

                if annotation:
                    params[text(param_name)] = text(annotation)

        classes[name]["methods"][method_name] = {
            "params": params,
            "return": text(return_type) if return_type else None
        }

        # Mengumpulkan atribut self
        for child in walk(field(method, "body")):
            if child.type == "assignment":
                left = field(child, "left")

                if left and left.type == "attribute":
                    obj = field(left, "object")
                    attr = field(left, "attribute")

                    if obj and attr and text(obj) == "self":
                        classes[name]["attributes"].add(text(attr))


# ==================================================
# 3. MENGENALI TIPE ELEMEN LIST
# ==================================================

for class_name, class_node in class_nodes.items():

    for call in walk(class_node):
        if call.type != "call":
            continue

        fn = field(call, "function")
        args = field(call, "arguments")

        if not fn or not args or fn.type != "attribute":
            continue

        method = field(fn, "attribute")
        obj = field(fn, "object")

        if not method or not obj or text(method) != "append":
            continue

        if obj.type != "attribute":
            continue

        owner = field(obj, "object")
        list_name = field(obj, "attribute")

        if not owner or not list_name or text(owner) != "self":
            continue

        # Cari tipe objek yang dimasukkan ke list
        for arg in args.named_children:
            if arg.type != "identifier":
                continue

            variable = text(arg)

            for assignment in walk(class_node):
                if assignment.type != "assignment":
                    continue

                left = field(assignment, "left")
                right = field(assignment, "right")

                if (left and right and left.type == "identifier"
                        and text(left) == variable
                        and right.type == "call"):

                    constructor = field(right, "function")

                    if constructor and text(constructor) in classes:
                        classes[class_name]["list_elements"][
                            text(list_name)
                        ] = text(constructor)


# ==================================================
# 4. ANALISIS SCOPE DAN TIPE
# ==================================================

errors = []
functions = [
    n for n in walk(root)
    if n.type == "function_definition"
]

for function in functions:

    name = text(field(function, "name"))
    body = field(function, "body")
    params_node = field(function, "parameters")
    return_node = field(function, "return_type")

    # Menentukan class tempat method berada
    owner_class = None

    for class_name, class_node in class_nodes.items():
        if function.start_byte > class_node.start_byte:
            if function.end_byte < class_node.end_byte:
                owner_class = class_name

    env = {}
    declared = set()

    # Membaca parameter
    for param in params_node.named_children:
        if param.type == "identifier":
            declared.add(text(param))

        elif param.type == "typed_parameter":
            p_name = param.named_children[0]
            declared.add(text(p_name))

            annotation = field(param, "type")
            if annotation:
                env[text(p_name)] = text(annotation)

    # Membaca deklarasi variabel dan tipe sederhana
    for node in walk(body):

        if node.type == "assignment":
            left = field(node, "left")
            right = field(node, "right")

            if left and left.type == "identifier":
                declared.add(text(left))
                env[text(left)] = infer(right, env)

        if node.type == "for_statement":
            left = field(node, "left")
            right = field(node, "right")

            if left and left.type == "identifier":
                variable = text(left)
                declared.add(variable)

                if right and right.type == "attribute":
                    obj = field(right, "object")
                    attr = field(right, "attribute")

                    if (owner_class and obj and attr
                            and text(obj) == "self"):
                        env[variable] = classes[
                            owner_class
                        ]["list_elements"].get(text(attr))

    # Memeriksa variabel yang belum dideklarasikan
    for node in walk(body):
        if node.type == "pair":
            value = field(node, "value")

            if value and value.type == "identifier":
                variable = text(value)

                if variable not in declared:
                    errors.append(
                        f"[SCOPE ERROR] {name}(): "
                        f"'{variable}' belum dideklarasikan "
                        f"(baris {line(value)})"
                    )

    # Memeriksa atribut objek
    for node in walk(body):
        if node.type != "attribute":
            continue

        obj = field(node, "object")
        attr = field(node, "attribute")

        if not obj or not attr or obj.type != "identifier":
            continue

        variable_type = env.get(text(obj))

        if variable_type not in classes:
            continue

        attribute_name = text(attr)
        known = (
            classes[variable_type]["attributes"]
            | set(classes[variable_type]["methods"])
        )

        if attribute_name not in known:
            errors.append(
                f"[ATTRIBUTE ERROR] {name}(): "
                f"'{attribute_name}' tidak ditemukan "
                f"pada class '{variable_type}' "
                f"(baris {line(node)})"
            )

    # Memeriksa tipe argumen pemanggilan method
    for node in walk(body):
        if node.type != "call":
            continue

        fn = field(node, "function")
        args = field(node, "arguments")

        if not fn or not args or fn.type != "attribute":
            continue

        obj = field(fn, "object")
        method = field(fn, "attribute")

        if not obj or not method or obj.type != "identifier":
            continue

        class_name = env.get(text(obj))

        if class_name not in classes:
            continue

        signature = classes[class_name]["methods"].get(text(method))

        if not signature:
            continue

        expected = list(signature["params"].values())
        actual = args.named_children

        for index, argument in enumerate(actual):
            if index >= len(expected):
                break

            actual_type = infer(argument, env)
            expected_type = expected[index]

            compatible = (
                actual_type == expected_type
                or (actual_type == "int" and expected_type == "float")
            )

            if actual_type and not compatible:
                errors.append(
                    f"[TYPE ERROR] {name}(): "
                    f"method '{text(method)}' mengharapkan "
                    f"'{expected_type}', menerima "
                    f"'{actual_type}' "
                    f"(baris {line(argument)})"
                )

    # Memeriksa operasi penjumlahan
    for node in walk(body):
        if node.type != "binary_operator":
            continue

        left = field(node, "left")
        right = field(node, "right")

        if not left or not right:
            continue

        left_type = infer(left, env)
        right_type = infer(right, env)

        if (left_type == "str" and right_type in ["int", "float"]
                or right_type == "str" and left_type in ["int", "float"]):

            errors.append(
                f"[TYPE ERROR] Operasi '+' tidak sesuai: "
                f"'{left_type}' + '{right_type}' "
                f"(baris {line(node)})"
            )

    # Memeriksa tipe nilai return
    if return_node:
        expected_return = text(return_node)

        for node in walk(body):
            if node.type != "return_statement":
                continue

            expression = node.named_children

            if not expression:
                continue

            actual_return = infer(expression[0], env)

            if actual_return and actual_return != expected_return:
                errors.append(
                    f"[RETURN TYPE ERROR] {name}(): "
                    f"mengharapkan '{expected_return}', "
                    f"menghasilkan '{actual_return}' "
                    f"(baris {line(node)})"
                )


# ==================================================
# 5. MENAMPILKAN HASIL ANALISIS
# ==================================================

print("=== PYTHON SEMANTIC ANALYZER ===")
print("Source: simple_order_management.py")
print("CST Root:", root.type)

print("\n=== CLASS INFORMATION ===")

for name, info in classes.items():
    print(f"\nClass: {name}")
    print("Attributes:", sorted(info["attributes"]))
    print("Methods:", sorted(info["methods"]))
    print("List elements:", info["list_elements"])

print("\n=== SEMANTIC ERRORS ===")

if errors:
    for error in errors:
        print(error)
else:
    print("No semantic errors detected.")

print(f"\nTotal findings: {len(errors)}")

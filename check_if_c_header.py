from pathlib import Path
from tree_sitter import Node, Parser, Language
import tree_sitter_cpp as tscpp

# Suffixes that indicate C++ source files
CPP_SOURCE_SUFFIXES = {
    ".cpp",
    ".hpp",
    ".cc",
    ".cxx",
    ".hxx",
    ".hh",
    ".ixx",
    ".cppm",
    ".ccm",
}

# The set of node.types in tree-sitter-cpp grammar that unambiguously indicate C++-only semantics
CPP_ONLY_NODE_TYPES = {
    "abstract_declarator",
    "access_specifier",  # public: private: etc.
    "alias_declaration",  # using T = int;
    "alignas_specifier",  # C++11 alignas
    "attribute_declaration",  # [[nodiscard]] etc.
    "auto",  # auto type deduction
    "cast_expression",  # static_cast / dynamic_cast / etc.
    "class_specifier",  # class definitions
    "concept_definition",  # C++20 concept
    "condition_clause",  # C++ specific if/switch condition forms
    "decltype_specifier",  # decltype(x)
    "delete_expression",  # delete ptr
    "dependent_type_specifier",  # dependent types in templates
    "enum_class_specifier",  # enum class
    "explicit_specifier",  # explicit keyword
    "friend_declaration",  # friend class X;
    "lambda_expression",  # lambdas
    "namespace_definition",  # namespace N {}
    "new_expression",  # new T()
    "noexcept_specifier",  # noexcept
    "operator_cast",  # conversion operators
    "override_specifier",  # override keyword
    "parameter_pack_expansion",  # T... variadic
    "qualified_identifier",  # std::vector etc.
    "reference_declarator",  # T& or T&&
    "static_assert_declaration",  # static_assert(...)
    "template_argument_list",  # std::vector<int> etc.
    "template_declaration",  # template<typename T>
    "template_function",  # function templates
    "template_method",  # methods in template classes
    "template_parameter_list",
    "template_type",
    "this",  # this pointer
    "throw_specifier",  # throw() specifiers (older C++)
    "type_qualifier",  # constexpr, consteval, constinit etc.
    "using_declaration",  # using namespace etc.
    "virtual_function_specifier",  # virtual keyword
    "virtual_specifier",  # final, etc.
}


def determine_if_cpp_header(file_path: Path, cpp_parser: Parser) -> bool:
    """
    Determines if a .h file should be treated as a C++ header.

    Returns True if it's likely a C++ header (has C++-only AST constructs
    or there are sibling C++ source files), otherwise False (treat as C header).
    """

    # 1. Sibling check: same directory, any file with C++ suffix
    parent = file_path.parent
    try:
        for sibling in parent.iterdir():
            if sibling == file_path:
                continue
            if sibling.is_file():
                if sibling.suffix.lower() in CPP_SOURCE_SUFFIXES:
                    return True
    except Exception:
        # If directory listing fails, ignore sibling heuristic
        pass

    # 2. Parse with tree-sitter-cpp parser
    try:
        source_bytes = file_path.read_bytes()
        # Alternatively: read text and encode utf-8
    except Exception:
        # If can't read file, conservatively treat as C header
        return False

    # If file is empty or nearly so, no strong indication of C++
    if not source_bytes.strip():
        return False

    tree = cpp_parser.parse(source_bytes)
    root: Node = tree.root_node

    # Recursive search for any node whose type is in CPP_ONLY_NODE_TYPES
    def has_cpp_type(node: Node) -> bool:
        if node.type in CPP_ONLY_NODE_TYPES:
            return True
        # Recurse into named children (faster / more relevant than all children)
        for child in node.named_children:
            # Early exit
            if has_cpp_type(child):
                return True
        return False

    if has_cpp_type(root):
        return True

    # If no C++-only node types found, treat as C header
    return False

def check_if_c_header(file_path: Path) -> bool:
    CPP_LANGUAGE = Language(tscpp.language())
    parser = Parser(CPP_LANGUAGE)
    return not determine_if_cpp_header(file_path, parser)

if __name__ == "__main__":
    # check if has an input argument that is .h file
    import sys

    if len(sys.argv) != 2:
        print("Usage: python check_if_c_header.py <path_to_header.h>", file=sys.stderr)
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.is_file():
        print(f"Error: File not found at '{file_path}'", file=sys.stderr)
        sys.exit(1)

    if file_path.suffix.lower() != '.h':
        print(f"Error: File '{file_path}' is not a .h header file.", file=sys.stderr)
        sys.exit(1)

    is_c_header = check_if_c_header(file_path)
    print("file_path is a C header" if is_c_header else "file_path is not a C header")

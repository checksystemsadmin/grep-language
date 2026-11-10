# GREP
## Global Retrieval, Execution & Processing

GREP is an experimental, search-native programming language created by Nolan G. Sands.

Version 0.1.0 provides an initial executable language implementation.

### Install

    python3 -m pip install -e .

### Run

    greplang examples/hello.grep

### Language instructions

- `print` — output text or a variable.
- `let` — assign a string variable.
- `find` — search a file for a literal substring.

### Example

    let project = "GREP"
    print $project
    find "GREP" in "README.md"

### Project status

GREP 0.1.0 is an experimental initial implementation. Advanced parsing, functions, control flow, and additional processing instructions are planned for future versions.

### Creator

Nolan G. Sands

### License

MIT. See LICENSE.

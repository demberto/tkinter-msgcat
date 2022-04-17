<!-- BADGES -->
<table>
  <tr>
    <th>ci</th>
    <td>
      <a>
        <img alt="Tests" src="https://img.shields.io/github/workflow/status/demberto/tkinter-msgcat/tests?label=tests">
      </a>
      <a>
        <img alt="Build" src="https://img.shields.io/github/workflow/status/demberto/tkinter-msgcat/publish">
      </a>
      <a href="https://tkmsgcat.readthedocs.io/en/latest/?badge=latest">
        <img alt="Docs" src="https://readthedocs.org/projects/tkmsgcat/badge/?version=latest">
      </a>
    </td>
  </tr>
  <tr>
    <th>pypi</th>
    <td>
      <a href="https://github.com/demberto/tkinter-msgcat/releases">
        <img alt="Version" src="https://img.shields.io/pypi/v/tkinter-msgcat">
      </a>
      <a href="https://github.com/demberto/tkinter-msgcat/blob/master/LICENSE">
        <img alt="License" src="https://img.shields.io/pypi/l/tkinter-msgcat">
      </a>
      <a>
        <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/tkinter-msgcat">
      </a>
    </td>
  </tr>
  <tr>
    <th>qa</th>
    <td>
      <a href="https://github.com/PyCQA/bandit">
        <img alt="security: bandit" src="https://img.shields.io/badge/security-bandit-yellow.svg">
      </a>
      <a href="https://github.com/python/mypy">
        <img alt="mypy: checked" src="https://img.shields.io/badge/mypy-checked-blue.svg">
      </a>
      <a href="https://github.com/psf/black">
        <img alt="code style: black" src="https://img.shields.io/badge/code%20style-black-black.svg">
      </a>
    </td>
  </tr>
</table>

# tkinter-msgcat

> Create multilingual interfaces for your tkinter applications.

tkinter-msgcat leverages Tk's msgcat to provide a per-instance message catalog
which holds all the translations, while allowing them to be kept in separate
files away from code.

## ⏬ Installation

tkinter-msgcat requires Python 3.7+

```
pip install tkinter-msgcat
```

## ✨ Getting Started

1.  For storing the translation files I recommend this folder hierarchy:

    ```
      project (or src/project)
      ├── __init__.py
      └── msgs
          ├── __init__.py
          ├── hi.msg
          └── mr.msg
    ```

    This layout is recommended by [Tcl][recommended-layout].

2.  Add some translations in the `.msg` files, in this case `hi.msg`:

    ```tcl
    ::msgcat::mcset hi "Hello" "नमस्ते"
    ```

3.  Create a Tkinter window *or instance, technically*.

4.  Let's put tkinter-msgcat into action!

    ```python
    from pathlib import Path
    from tkmsgcat import *

    msgsdir = Path(__file__).parent / "msgs"
    load(msgsdir)
    locale("hi")
    get("Hello")  # "नमस्ते" 🥳
    ```

## 🤝 Contributing

All contributions are welcome and acknowledged.
Please read the [contributor's guide][contributing].

## © License

The code in this project is released under the [3-Clause BSD License][license].

<!-- LINKS -->
[contributing]: https://github.com/demberto/tkinter-msgcat/blob/master/CONTRIBUTING.md
[docs]: https://tkmsgcat.readthedocs.io/en/latest/?badge=latest
[license]: https://github.com/demberto/tkinter-msgcat/blob/master/LICENSE
[recommended-layout]: https://www.tcl-lang.org/man/tcl/TclCmd/msgcat.htm#M22

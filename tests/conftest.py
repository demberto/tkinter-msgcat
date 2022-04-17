# pylint: disable=missing-module-docstring

import pathlib
import tkinter

import pytest

import tkmsgcat


@pytest.fixture(scope="session")
def tk_root() -> tkinter.Tk:
    root = tkinter.Tk()
    tkmsgcat.load(pathlib.Path(__file__).parent / "msgs")
    # Initialisation to prevent redundant code in tests
    tkmsgcat.locale("hi")
    tkmsgcat.locale("mr")
    return root

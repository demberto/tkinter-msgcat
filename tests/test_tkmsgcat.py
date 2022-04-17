# pylint: disable=unused-argument,missing-module-docstring

import pathlib
import tkinter

import pytest

import tkmsgcat


def test_failure_without_root():
    """Invoking tkmsgcat fails if a `tkinter.Tk` instance is not found."""
    with pytest.raises(RuntimeError):
        tkmsgcat.load("msgs")


def test_loaded_from_failure():
    tkinter.Tk()  # Provide a default root
    with pytest.raises(AttributeError):
        tkmsgcat.loaded_from()


def test_is_loaded(tk_root):
    for locale in ("hi", "mr"):
        assert tkmsgcat.is_loaded(locale)


def test_has(tk_root):
    # Search all locales
    tkmsgcat.has("Hello")

    # Search particular locale
    for locale in ("mr", "hi"):
        tkmsgcat.locale(locale)
        assert tkmsgcat.has("Hello", search_all=False)


@pytest.mark.parametrize("locale", ["hi", "mr"])
def test_locale(tk_root, locale: str):
    tkmsgcat.locale(locale)
    assert tkmsgcat.locale() == locale


def test_loaded_from(tk_root):
    assert tkmsgcat.loaded_from() == str(
        (pathlib.Path(__file__).parent / "msgs").resolve()
    ).replace("\\", "/")


def test_loaded_locales(tk_root):
    assert set(("mr", "hi")).issubset(tkmsgcat.loaded_locales())


@pytest.mark.parametrize(
    "locale, translation, maxlen",
    [
        ("hi", "शुभ प्रभात", 10),
        ("mr", "शुभ सकाळ", 8),
    ],
)
def test_longest(tk_root, locale: str, translation: str, maxlen: int):
    tkmsgcat.locale(locale)
    tkmsgcat.add("Good Morning", translation)
    assert tkmsgcat.longest(["Hello", "Good Morning"]) == maxlen


@pytest.mark.parametrize(
    "locale, translation, maxlen",
    [
        ("hi", "शुभ प्रभात", 10),
        ("mr", "शुभ सकाळ", 8),
    ],
)
def test_longest_in(tk_root, locale: str, translation: str, maxlen: int):
    tkmsgcat.add_to(locale, "Good Morning", translation)
    assert tkmsgcat.longest_in(locale, ["Hello", "Good Morning"]) == maxlen


def test_preferences(tk_root):
    tkmsgcat.locale("en_US_funky")
    assert tkmsgcat.preferences() == ("en_us_funky", "en_us", "en", "")


def test_add_to(tk_root):
    tkmsgcat.add_to("mr", "Today", "आज")
    assert tkmsgcat.get_from("mr", "Today") == "आज"


def test_add(tk_root):
    tkmsgcat.locale("hi")
    tkmsgcat.add("Today", "आज")
    assert tkmsgcat.get("Today") == "आज"


def test_update_to(tk_root):
    tkmsgcat.update_to("mr", {"Yesterday": "काल", "Tommorrow": "उद्या"})
    assert tkmsgcat.get_from("mr", "Yesterday") == "काल"
    assert tkmsgcat.get_from("mr", "Tommorrow") == "उद्या"


def test_update(tk_root):
    tkmsgcat.locale("hi")
    tkmsgcat.update({"Yesterday": "बीता हुआ कल", "Tommorrow": "कल"})
    assert tkmsgcat.get("Yesterday") == "बीता हुआ कल"
    assert tkmsgcat.get("Tommorrow") == "कल"


@pytest.mark.parametrize("locale, translation", [("hi", "नमस्ते"), ("mr", "नमस्कार")])
def test_get(tk_root, locale: str, translation: str):
    tkmsgcat.locale(locale)
    assert tkmsgcat.get("Hello") == translation


@pytest.mark.parametrize("locale, translation", [("hi", "नमस्ते"), ("mr", "नमस्कार")])
def test_get_from(tk_root, locale: str, translation: str):
    assert tkmsgcat.get_from(locale, "Hello") == translation


# def test_locale_handler(tk_root):
#     class FakeException(Exception):
#         pass

#     def handler(*args):
#         raise FakeException

#     tkmsgcat.locale_handler(handler)
#     with pytest.raises(FakeException):
#         tkmsgcat.locale("en")
#     tkmsgcat.locale_handler()
#     tkmsgcat.locale("en")


def test_missing_handler(tk_root):
    def handler(locale, src, *args):
        if src == "MISSING":
            return "_"
        return src

    tkmsgcat.missing_handler(handler)
    assert tkmsgcat.get("MISSING") == "_"
    assert tkmsgcat.get("NOT_MISSING") == "NOT_MISSING"
    tkmsgcat.missing_handler()
    assert tkmsgcat.get("MISSING") == "MISSING"


# def test_preload_handler(tk_root):
#     def handler(*locales):
#         if "missing" in locales:
#             raise Exception

#     tkmsgcat.preload_handler(handler)
#     tkmsgcat.locale("missing")


def test_unload(tk_root):
    tkmsgcat.unload()
    assert not tkmsgcat.is_init()

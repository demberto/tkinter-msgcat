"""Create multilingual interfaces for your tkinter applications.

tkinter-msgcat leverages Tk's msgcat to provide a per-instance message catalog
which holds all the translations, while allowing them to be kept in separate
files away from code.

Example use:

    >>> from tkmsgcat import load, locale, translate
    >>> load("msgs")
    >>> locale = "hi"
    >>> translate("Hello")
    "नमस्ते"

Complete docs available on <https://tkmsgcat.rtfd.io>.
"""

from __future__ import annotations

import contextlib
import logging
import pathlib
import sys
import tkinter as tk
from typing import Tuple, cast, no_type_check, overload

if sys.version_info >= (3, 9):
    from collections.abc import Callable, Iterator
else:
    from typing import Callable, Iterator

__all__ = [
    "MessageCatalog",
    "add",
    "add_to",
    "get",
    "get_from",
    "has",
    "is_init",
    "is_loaded",
    "load",
    "loaded_locales",
    "longest",
    "longest_in",
    "missing_handler",
    "preferences",
    "update",
    "update_to",
    "unload",
]

log = logging.getLogger("tkmsgcat")


# Python <= 3.7 doesn't have this method.
@no_type_check
def _get_default_root(what: str = None) -> tk.Tk:
    # pylint: disable=protected-access
    if not tk._support_default_root:
        raise RuntimeError(
            "No master specified and tkinter is "
            "configured to not support default root"
        )
    if tk._default_root is None:
        if what:
            raise RuntimeError(f"Too early to {what}: no default root window")
        root = tk.Tk()
        if tk._default_root is not root:
            raise RuntimeError("Couldn't initialise a default root")
    return tk._default_root


class _PackageOption:
    def __init__(self, cmd: str) -> None:
        self.__cmd = cmd
        self.__handler = ""

    def __set__(
        self,
        instance: MessageCatalog,
        value: Callable,  # type: ignore
    ) -> None:
        self.__handler = instance.root.register(value)
        instance.eval_(f"::msgcat::mcpackageconfig set {self.__cmd} {self.__handler}")

    def __get__(self, instance: MessageCatalog, _=None) -> str:  # type: ignore
        try:
            return instance.eval_(f"::msgcat::mcpackageconfig get {self.__cmd}")
        except tk.TclError as exc:
            raise AttributeError(f"No handler found for {self.__cmd!r}") from exc

    def __delete__(self, instance: MessageCatalog) -> None:
        try:
            instance.eval_(f"::msgcat::mcpackageconfig unset {self.__cmd}")
        except tk.TclError:  # pragma: no cover
            pass


class MessageCatalog:
    """Override this to create custom msgcat functionality.

    Most applications should suffice with the package-level functions.

    Caution: Scope
        Tkinter's message catalog is scoped to a `tkinter.Tk` instance and
        not the Python interpreter! In practice, this means that you need to
        have a single `tkinter.Tk` instance to share the loaded translations
        and locales.
    """

    @property
    def root(self) -> tk.Tk:
        return cast(tk.Tk, _get_default_root(what="use msgcat"))

    def eval_(self, cmd: str) -> str:
        log.debug("Evaluating %s", cmd)
        return self.root.eval(cmd)

    def _splitlist(self, __s: str) -> tuple[str]:
        # pylint: disable=deprecated-typing-alias
        return cast(Tuple[str], self.root.splitlist(__s))

    @staticmethod
    def _join(*__l: str) -> str:
        new_l = []
        for i in __l:
            stripped = i.strip('"')
            new_l.append(f'"{stripped}"')
        return " ".join(new_l)

    @staticmethod
    def _dict2str(__d: dict[str, str]) -> str:
        lst = []
        for key, val in __d.items():
            # Append quotes to support strings with spaces
            s_key = key.strip('"')
            s_val = val.strip('"')
            key = f'"{s_key}"'
            val = f'"{s_val}"'
            lst.extend([key, val])
        return " ".join(lst)

    @contextlib.contextmanager
    def _locale_ctx(self, newlocale: str) -> Iterator[None]:
        oldlc = self.locale
        self.locale = newlocale
        try:
            yield None
        finally:
            self.locale = oldlc

    def is_init(self) -> bool:
        tkbool = self.eval_("::msgcat::mcpackageconfig isset mcfolder")
        return cast(bool, self.root.getboolean(tkbool))

    def is_loaded(self, locale_: str) -> bool:
        tklist = self.eval_("::msgcat::mcloadedlocales loaded")
        return locale_ in self._splitlist(tklist)

    @overload
    def load(self, dir_: str) -> None:
        ...  # pragma: no cover

    @overload
    def load(self, dir_: pathlib.Path) -> None:
        ...  # pragma: no cover

    def load(self, dir_: str | pathlib.Path) -> None:
        _path = dir_ if isinstance(dir_, pathlib.Path) else pathlib.Path(dir_)
        _resolvedpath = _path.resolve()
        # ! Tk bug: All backslashes need to be replaced by formward slashes
        msgsdir = str(_resolvedpath).replace("\\", "/")
        log.debug("Loading translations from %s", msgsdir)
        self.eval_(
            f'::msgcat::mcload [file join [file dirname [info script]] "{msgsdir}"]'
        )

    @property
    def locale(self) -> str:
        return self.eval_("::msgcat::mclocale")

    @locale.setter
    def locale(self, newlocale: str) -> None:
        self.eval_(f"::msgcat::mclocale {newlocale}")

    @property
    def loaded_locales(self) -> tuple[str]:
        tklist = self.eval_("::msgcat::mcloadedlocales loaded")
        return self._splitlist(tklist)

    loaded_from = _PackageOption("mcfolder")

    def longest(self, strings: tuple[str]) -> int:
        return int(self.eval_(f"::msgcat::mcmax {self._join(*strings)}"))

    def longest_in(self, locale_: str, strings: tuple[str]) -> int:
        with self._locale_ctx(locale_):
            return self.longest(strings)

    @property
    def preferences(self) -> tuple[str]:
        tklist = self.eval_("::msgcat::mcpreferences")
        return self._splitlist(tklist)

    def has(self, what: str, search_all: bool = True) -> bool:
        command = "::msgcat::mcexists"
        if not search_all:
            command += " -exactlocale"
        command += f" {what}"
        return cast(bool, self.root.getboolean(self.eval_(command)))

    def add(self, what: str, translation: str) -> None:
        self.eval_(f'::msgcat::mcset {self.locale} "{what}" "{translation}"')

    def add_to(self, locale_: str, what: str, translation: str) -> None:
        self.eval_(f'::msgcat::mcset {locale_} "{what}" "{translation}"')

    def update(self, translations: dict[str, str]) -> None:
        self.eval_(
            f"::msgcat::mcmset {self.locale} {{{self._dict2str(translations)}}}",
        )

    def update_to(self, locale_: str, translations: dict[str, str]) -> None:
        self.eval_(f"::msgcat::mcmset {locale_} {{{self._dict2str(translations)}}}")

    def get(self, what: str, *fmtargs: str) -> str:
        command = f'::msgcat::mc "{what}"'
        if fmtargs:
            command = command + " " + self._join(*fmtargs)
        return self.eval_(command)

    def get_from(self, locale_: str, what: str, *fmtargs: str) -> str:
        with self._locale_ctx(locale_):
            return self.get(what, *fmtargs)

    # TODO Doesn't work
    # locale_handler = _Handler("changecmd")

    missing_handler = _PackageOption("unknowncmd")

    # TODO Doesn't work
    # preload_handler = _Handler("loadcmd")

    def unload(self) -> None:
        self.eval_("::msgcat::mcforgetpackage")


_default_msgcat = MessageCatalog()


def is_init() -> bool:
    """Whether any translation file has been loaded."""
    return _default_msgcat.is_init()


def is_loaded(locale_: str) -> bool:
    """Whether a translation file for a particular locale is loaded.

    Args:
        locale_ (str): The locale to be checked if it is loaded.
    """
    return _default_msgcat.is_loaded(locale_)


def load(dir_: str | pathlib.Path) -> None:
    """Loads all translation files from the specified directory.

    Args:
        dir_ (str | pathlib.Path): The path/name of the directory where
            all the translation files (.msg extension) are stored. Tk
            recommends you to store them all in a separate `msgs` directory at
            the package level and name them according to their locale.
    """
    _default_msgcat.load(dir_)


def locale(newlocale: str = "") -> str:
    """The locale used to translate strings.

    Tip:
        See [msgcat manual](https://www.tcl-lang.org/man/tcl/TclCmd/msgcat.htm#M19)
        for details on how to specify a locale.

    Args:
        newlocale (str): Use this to change the locale.

    Returns:
        str: The currently used locale.
    """
    if newlocale:
        _default_msgcat.locale = newlocale
    return _default_msgcat.locale


def loaded_from() -> str:
    """Returns the path of the directory from which translations were loaded.

    Raises:
        AttributeError: When the directory is not set.
    """
    return _default_msgcat.loaded_from


def loaded_locales() -> tuple[str]:
    """Returns a list of all the currently loaded locales.

    A locale is loaded only when it is requested i.e. set via `locale`.
    """
    return _default_msgcat.loaded_locales


def longest(what: tuple[str]) -> int:
    """Find the length of the longest translated string in the current locale.

    This is useful in deciding the maximum size of a label or a button when
    using the `place` geometry manager, for exmaple.

    Args:
        what (str): The strings whose translations are to be compared.

    Returns:
        int: Length of the longest translated string with respect to all the
            strings passed .
    """
    return _default_msgcat.longest(what)


def longest_in(locale_: str, what: tuple[str]) -> int:
    """Find the length of the longest translated string in a specific locale.

    This is useful in deciding the maximum size of a label or a button when
    using the `place` geometry manager, for exmaple.

    Args:
        locale_ (str): The locale to use for finding the length.
        what (str): The strings whose translations are to be compared.

    Returns:
        int: Length of the longest translated string with respect to all the
            strings passed .
    """
    return _default_msgcat.longest_in(locale_, what)


def preferences() -> tuple[str]:
    """Returns a list of the preferred locales based on the current locale."""
    return _default_msgcat.preferences


def has(what: str, search_all: bool = True) -> bool:
    """Check if a string has a translation in the current/all locale(s).

    Args:
        what (str): The string to lookup for a translation.
        search_all (bool, optional): Whether to search in all of the loaded
            locales or just the current locale. If a locale is not set, the
            value returned by `preferences` is used. Defaults to True.

    Returns:
        bool: Whether the given string has a translation.
    """
    return _default_msgcat.has(what, search_all)


def add(what: str, translation: str) -> None:
    """Set/update a translation for the current locale.

    Args:
        what (str): The string to be translated.
        translation (str): The translated string.
    """
    _default_msgcat.add(what, translation)


def add_to(locale_: str, what: str, translation: str) -> None:
    """Set/update a translation in a specific locale.

    Args:
        locale_ (str): The locale in which this operation will take place.
        what (str): The string to be translated.
        translation (str): The translated string.
    """
    _default_msgcat.add_to(locale_, what, translation)


def update(translations: dict[str, str]) -> None:
    """Set/update translations of the current locale.

    Args:
        translations (dict[str, str]): A mapping of source strings to
            translated strings.
    """
    _default_msgcat.update(translations)


def update_to(locale_: str, translations: dict[str, str]) -> None:
    """Set/update translations in a specific locale.

    Args:
        locale_ (str): The locale in which this operation will take place.
        translations (dict[str, str]): A mapping of source strings to
            translated strings.
    """
    _default_msgcat.update_to(locale_, translations)


def get(what: str, *fmtargs: str) -> str:
    """Translate a string according to a user's current locale.

    Args:
        what (str): The string to be translated. It should generally be in
            English as that is the language used by code itself.
        *fmtargs (tuple[str], optional): Extra arguments passed internally
            to the [format](https://www.tcl.tk/man/tcl8.6/TclCmd/format.html)
            package.

    Returns:
        str: The translated string.
    """
    return _default_msgcat.get(what, *fmtargs)


def get_from(locale_: str, what: str, *fmtargs: str) -> str:
    """Get the translation of a string from a specific locale.

    Args:
        locale_ (str): The locale to be used for looking up `__what`.
        what (str): The string to be translated. It should generally be in
            English as that is the language used by code itself.
        *fmtargs (tuple[str], optional): Extra arguments passed internally
            to the [format](https://www.tcl.tk/man/tcl8.6/TclCmd/format.html)
            package.

    Returns:
        str: The translated string.
    """
    return _default_msgcat.get_from(locale_, what, *fmtargs)


# def locale_handler(func: Optional[Callable] = None) -> None:
#     """Register the callback invoked when the default locale is changed.

#     It can be used, for example to display the GUI in another language. It is
#     invoked with the same arguments as the value of `preferences`. Use
#     tkinter's `splitlist` method to split the string into a Python list.

#     Args:
#         func (Callable, optional): The handler is set when this has a value
#             and unset when it is None. Defaults to None.
#     """
#     if func:
#         _default_msgcat.locale_handler = func
#     else:
#         del _default_msgcat.locale_handler


def missing_handler(func: Callable[..., str] | None = None) -> None:
    """Register the callback invoked when a translation is not found.

    It is invoked with the same arguments passed to `translate`. It must
    return a formatted message as `translate` would do normally.

    Args:
        func (Callable, optional): The handler is set when this has a value
            and unset when it is None. Defaults to None.
    """
    if func:
        _default_msgcat.missing_handler = func
    else:
        del _default_msgcat.missing_handler


# def preload_handler(func: Optional[Callable] = None) -> None:
#     """Registers the callback invoked when a translation couldn't be found.

#     Arguments to the callback are the list of the locales to load.

#     Args:
#         func (Callable, optional): The handler is set when this has a value
#             and unset when it is None. Defaults to None.
#     """
#     if func:
#         _default_msgcat.preload_handler = func
#     else:
#         del _default_msgcat.preload_handler


def unload() -> None:
    """Unloads all translations and forgets all callbacks and settings.

    You can reinitialise the message catalog by a calling `load` with the
    appropriate arguments.
    """
    _default_msgcat.unload()

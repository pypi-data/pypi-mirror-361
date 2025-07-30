import abc
import os
import sys
import typing

from stairval import Issue, Level


class Notepad(metaclass=abc.ABCMeta):
    """
    Record issues encountered during parsing/validation of a hierarchical data structure.

    The issues can be organized in sections. `Notepad` keeps track of issues in one section
    and the subsections can be created by calling :func:`add_subsection`.
    The function returns an instance responsible for issues of a subsection.

    A collection of the issues from the current section are available via :attr:`issues` property
    and the convenience functions provide iterators over error and warnings.
    """

    def __init__(
        self,
        label: str,
        level: int,
    ):
        self._label = label
        self._level = level
        self._issues: typing.MutableSequence[Issue] = []

    @abc.abstractmethod
    def add_subsections(
        self,
        *labels: str,
    ) -> typing.Sequence["Notepad"]:
        """
        Add a sequence/chain of subsections.

        :param labels: a sequence of labels for the new notepad subsections.
        """
        pass

    @abc.abstractmethod
    def get_subsections(self) -> typing.Sequence["Notepad"]:
        """
        Get a sequence with subsections.

        Returns: a sequence of the subsection nodes.
        """
        ...

    def iter_sections(self) -> typing.Iterator["Notepad"]:
        """
        Iterate over nodes in the depth-first fashion.

        The iterator also includes the *current* node.

        Returns: a depth-first iterator over :class:`Notepad` nodes.
        """
        stack = [
            self,
        ]
        while stack:
            node = stack.pop()
            stack.extend(reversed(node.get_subsections()))  # type: ignore
            yield node

    def add_subsection(self, label: str) -> "Notepad":
        """
        Add a single labeled subsection.

        :param label: a label to use for the new subsection.
        """
        return self.add_subsections(label)[0]

    @property
    def label(self) -> str:
        """
        Get the section label.
        """
        return self._label

    @property
    def level(self) -> int:
        """
        Get the level of the notepad node (distance from the top-level hierarchy node).
        """
        return self._level

    @property
    def issues(self) -> typing.Sequence[Issue]:
        """
        Get an iterable with the issues of the current section.
        """
        return self._issues

    def add_issue(self, level: Level, message: str, solution: typing.Optional[str] = None):
        """
        Add an issue with certain `level`, `message`, and an optional `solution`.
        """
        self._issues.append(Issue(level, message, solution))

    def add_error(self, message: str, solution: typing.Optional[str] = None):
        """
        A convenience function for adding an *error* with a `message` and an optional `solution`.
        """
        self.add_issue(Level.ERROR, message, solution)

    def errors(self) -> typing.Iterator[Issue]:
        """
        Iterate over the errors of the current section.
        """
        return filter(lambda dsi: dsi.level == Level.ERROR, self.issues)

    def error_count(self) -> int:
        """
        Returns:
            int: count of errors found in this section.
        """
        return sum(1 for _ in self.errors())

    def has_subsections(self) -> bool:
        """
        Returns:
            True: if the notepad has one or more subsections.
        """
        return len(self.get_subsections()) > 0

    def has_errors(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more errors were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.errors():
                    return True
        else:
            for _ in self.errors():
                return True

        return False

    def add_warning(self, message: str, solution: typing.Optional[str] = None):
        """
        A convenience function for adding a *warning* with a `message` and an optional `solution`.
        """
        self.add_issue(Level.WARN, message, solution)

    def warnings(self) -> typing.Iterator[Issue]:
        """
        Iterate over the warnings of the current section.
        """
        return filter(lambda dsi: dsi.level == Level.WARN, self.issues)

    def has_warnings(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more warnings were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.warnings():
                    return True
        else:
            for _ in self.warnings():
                return True

        return False

    def warning_count(self) -> int:
        """
        Returns:
            int: count of warnings found in this section.
        """
        return sum(1 for _ in self.warnings())

    def has_errors_or_warnings(self, include_subsections: bool = False) -> bool:
        """
        Returns:
            bool: `True` if one or more errors or warnings were found in the current section or its subsections.
        """
        if include_subsections:
            for node in self.iter_sections():
                for _ in node.warnings():
                    return True
                for _ in node.errors():
                    return True
        else:
            for _ in self.warnings():
                return True
            for _ in self.errors():
                return True

        return False

    def visit(
        self,
        visitor: typing.Callable[
            [
                "Notepad",
            ],
            None,
        ],
    ):
        """
        Performs a depth-first search on the notepad nodes and calls `visitor` with all nodes.
        Args:
            visitor: a callable that takes the current notepad node as the only argument.
        """
        for node in self.iter_sections():
            visitor(node)

    def summarize(
        self,
        file: typing.TextIO = sys.stdout,
        indent: int = 2,
    ):
        assert isinstance(indent, int) and indent >= 0

        n_errors = sum(node.error_count() for node in self.iter_sections())
        n_warnings = sum(node.warning_count() for node in self.iter_sections())
        if n_errors > 0 or n_warnings > 0:
            file.write("Showing errors and warnings")
            file.write(os.linesep)

            for node in self.iter_sections():
                if node.has_errors_or_warnings(include_subsections=True):
                    # We must report the node label even if there are no issues with the node.
                    l_pad = " " * ((node.level + 1) * indent)
                    file.write(l_pad + node.label)
                    file.write(os.linesep)

                    if node.has_errors():
                        file.write(l_pad + "errors:")
                        file.write(os.linesep)
                        for error in node.errors():
                            file.write(l_pad + "- " + error.message + (f"· {error.solution}" if error.solution else ""))
                            file.write(os.linesep)
                    if node.has_warnings():
                        file.write(l_pad + "warnings:")
                        file.write(os.linesep)
                        for warning in node.warnings():
                            file.write(
                                l_pad + "- " + warning.message + (f"· {warning.solution}" if warning.solution else "")
                            )
                            file.write(os.linesep)
        else:
            file.write("No errors or warnings were found")
            file.write(os.linesep)

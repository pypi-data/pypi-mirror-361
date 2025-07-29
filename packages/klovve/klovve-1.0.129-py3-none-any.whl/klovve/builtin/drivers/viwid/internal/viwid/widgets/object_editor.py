#  SPDX-FileCopyrightText: © 2025 Josef Hahn
#  SPDX-License-Identifier: AGPL-3.0-only
"""
See :py:class:`ObjectEditor`.
"""
import viwid.widgets
from viwid.widgets.widget import Widget as _Widget


class ObjectEditor(_Widget):
    """
    An object editor.

    This is a complex widget that allows the user to inspect and edit a tree-like structure of objects.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(), **kwargs})

    title: str
    @_Widget.Property(default=lambda: "")
    def title(self, _):
        """
        The title text.
        """

    color: viwid.TColorInput
    @_Widget.Property(default=lambda: "#888")
    def color(self, _):
        """
        The color.
        """

    is_removable_by_user: bool
    @_Widget.Property(default=lambda: False)
    def is_removable_by_user(self, _):
        """
        Whether this object is removable by the user.
        """

    is_expanded: bool
    @_Widget.Property(default=lambda: True)
    def is_expanded(self, _):
        """
        Whether this object editor is expanded.
        """

    def __action_added(self, index: int, item: "TODO") -> None:
        pass

    def __action_removed(self, index: int, item: "TODO") -> None:
        pass

    @_Widget.ListProperty(__action_added, __action_removed)
    def actions(self) -> list["TODO"]:
        """
        The object actions.
        """

    def __property_slot_added(self, index: int, item: "TODO") -> None:
        pass

    def __property_slot_removed(self, index: int, item: "TODO") -> None:
        pass

    @_Widget.ListProperty(__property_slot_added, __property_slot_removed)
    def property_slots(self) -> list["TODO"]:
        """
        The property slots.
        """

    def __additional_widget_added(self, index: int, item: "TODO") -> None:
        pass

    def __additional_widget_removed(self, index: int, item: "TODO") -> None:
        pass

    @_Widget.ListProperty(__additional_widget_added, __additional_widget_removed)
    def additional_widgets(self) -> list["TODO"]:
        """
        The additional widgets to show.
        """


class ObjectPropertyEditor(_Widget):
    """
    An object property editor.

    Usually used inside an :py:class:`ObjectEditor`.
    """

    def __init__(self, **kwargs):
        super().__init__(**{**dict(), **kwargs})

    children_can_be_added_by_user: bool
    @_Widget.Property(default=lambda: False)
    def children_can_be_added_by_user(self, _):
        """
        Whether children can be added by the user.
        """

    def __object_editor_added(self, index: int, item: "TODO") -> None:
        pass

    def __object_editor_removed(self, index: int, item: "TODO") -> None:
        pass

    @_Widget.ListProperty(__object_editor_added, __object_editor_removed)
    def object_editors(self) -> list["TODO"]:
        """
        The children's object editors.
        """

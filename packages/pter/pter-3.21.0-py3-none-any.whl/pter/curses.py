import logging
import os
import sys
import datetime
import string
import webbrowser
import curses
import traceback
import tempfile
import subprocess
import shlex
import shutil
from pathlib import Path

from pytodotxt import TodoTxt, Task, TodoTxtParser

from cursedspace import Application, Panel, ScrollPanel, InputLine, \
                        ShellContext, Completion

from pter import common
from pter import utils
from pter import version
from pter.source import Source
from pter.autotemplate import load_auto_templates, AutoTemplate
from pter.searcher import Searcher
from pter.key import Key
from pter.tr import tr
from pter.hook import Hook
from pter.help import SHORT_NAMES, compile_key_listing


TITLE_FRAME = '┤├'
HORIZONTAL_BAR = '─'

DEFAULT_KEY_MAPPING = {
    ('q',): 'quit',
    ('^C',): 'cancel',
    ('<escape>',): 'cancel',
    ('<down>',): 'next-item',
    ('<up>',): 'prev-item',
    ('<pgup>',): 'page-up',
    ('<pgdn>',): 'page-down',
    ('<home>',): 'first-item',
    ('<end>',): 'last-item',
    ('j',): 'next-item',
    ('k',): 'prev-item',
    ('r',): 'show-related',
    ('<return>',): 'select-item',
    ('h',): 'toggle-hidden',
    ('d',): 'toggle-done',
    ('e',): 'edit-task',
    ('E',): 'edit-external',
    ('n',): 'create-task',
    ('v',): 'duplicate-task',
    ('N',): 'edit-note',
    ('V',): 'view-note',
    (':',): 'jump-to',
    ('/',): 'search',
    ('<caret>',): 'clear-search',
    ('c',): 'search-context',
    ('p',): 'search-project',
    ('<f6>',): 'select-project',
    ('<f7>',): 'select-context',
    ('t',): 'toggle-tracking',
    ('^L',): 'refresh-screen',
    ('^R',): 'reload-tasks',
    ('u',): 'open-url',
    ('>',): 'delegate',
    ('L',): 'load-template',
    ('S',): 'save-template',
    ('l',): 'load-search',
    ('s',): 'save-search',
    ('?',): 'show-help',
    ('m',): 'open-manual',
    ('A',): 'prio-a',
    ('B',): 'prio-b',
    ('C',): 'prio-c',
    ('D',): 'prio-d',
    ('+',): 'prio-up',
    ('-',): 'prio-down',
    ('=',): 'prio-none',
    ('%',): 'archive',
    ('Y',): 'to-clipboard',
}
DEFAULT_EDITOR_KEY_MAPPING = {
    '^C': 'cancel',
    '<escape>': 'cancel',
    '<left>': 'go-left',
    '<right>': 'go-right',
    '<ctrl_left>': 'go-word-left',
    '<ctrl_right>': 'go-word-right',
    '<tab>': 'goto-empty',
    '^U': 'del-to-bol',
    '^K': 'del-to-eol',
    '<backspace>': 'del-left',
    '<del>': 'del-right',
    '^W': 'del-word-left', # a-la bash
    '<ctrl_del>': 'del-word-right',
    '<home>': 'go-bol',
    '<end>': 'go-eol',
    '<f6>': 'select-file',
    '<return>': 'submit-input',
    '^Y': 'submit-without-template',
}


class Color:
    def __init__(self, fg, bg=None):
        self.fg = fg
        self.bg = bg

    def pair(self):
        return [self.fg, self.bg]

    def __eq__(self, other):
        return self.fg == other.fg and self.bg == other.bg


class TaskLineGroup:
    def __init__(self):
        self.elements = []

    def append(self, *args, **kwargs):
        self.elements.append(TaskLineElement(*args, **kwargs))


class TaskLine:
    def __init__(self, task, source):
        self.elements = {}
        self.task = task
        self.source = source
        self._due = None

    def add(self, kind, *args, **kwargs):
        self.elements[kind] = TaskLineElement(*args, **kwargs)
        self.elements[kind].name = kind

    @property
    def is_completed(self):
        return self.task.is_completed

    @property
    def due(self):
        due = self.task.attr_due
        if self._due is None and len(due) > 0:
            self._due = utils.task_parse_due(self.task)
        return self._due

    @property
    def is_overdue(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due < datetime.date.today()

    @property
    def is_due_tomorrow(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due == datetime.date.today() + datetime.timedelta(days=1)

    @property
    def is_due_today(self):
        return not self.task.is_completed and \
               self.due is not None and \
               self.due == datetime.date.today()


class TaskLineDescription(TaskLineGroup):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = common.TF_DESCRIPTION

    @property
    def space_around(self):
        return True


class TaskLineElement:
    def __init__(self, content, color=None, space_around=False, name=None):
        self.content = content
        self.color = color
        self.space_around = space_around
        self.name = name


class TaskLineSelectionIcon(TaskLineElement):
    def __init__(self, content):
        super().__init__(content, space_around=False)
        self.name = common.TF_SELECTION


class StatusBar(Panel):
    def __init__(self, app):
        super().__init__(app, (1, 1))
        self.text = ""
        self.color = None
        self.expire = datetime.datetime.max
        self.blank_after = max(1, app.conf.number(common.SETTING_GROUP_GENERAL,
                                                  common.SETTING_INFO_TIMEOUT,
                                                  common.DEFAULT_INFO_TIMEOUT))

    def set_text(self, text, color=None, expire=True):
        self.text = text
        self.color = color or common.SETTING_COL_NORMAL
        if expire is True:
            self.expire = datetime.datetime.now() \
                        + datetime.timedelta(seconds=self.blank_after)
        elif isinstance(expire, datetime.datetime):
            self.expire = expire
        else:
            self.expire = datetime.datetime.max
        self.paint()

    def is_expired(self):
        return len(self.text) > 0 and datetime.datetime.now() >= self.expire

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

        if self.is_expired():
            self.text = ''
            self.color = common.SETTING_COL_NORMAL

        attr = self.app.color(common.SETTING_COL_NORMAL)
        try:
            self.win.addstr(0, 0, " "*self.dim[1], attr)
        except curses.error:
            pass
        if len(self.text) > 0:
            try:
                self.win.addstr(0, 0,
                                self.text[:self.dim[1]],
                                self.app.color(self.color))
            except curses.error:
                pass
        self.win.noutrefresh()


class HelpBar(Panel):
    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

        mapping = self.app.key_mapping
        actions = self.app.help_actions
        base_keymap = DEFAULT_KEY_MAPPING

        if len(self.app.focus) == 0:
            pass
        elif isinstance(self.app.focus[-1], HelpScreen):
            actions = ['cancel', 'refresh-screen']
        elif isinstance(self.app.focus[-1], Selector):
            actions = ['cancel', 'select-item']
        elif isinstance(self.app.focus[-1], TaskCreator):
            actions = ['cancel', 'submit-input', 'submit-without-template']
            if len(self.app.sources) > 1:
                actions += ['select-file']
            mapping = self.app.editor_key_mapping
            base_keymap = DEFAULT_EDITOR_KEY_MAPPING
        elif isinstance(self.app.focus[-1], TaskEditor):
            actions = ['cancel', 'submit-input']
            mapping = self.app.editor_key_mapping
            base_keymap = DEFAULT_EDITOR_KEY_MAPPING

        try:
            self.win.addstr(0, 0, " "*self.dim[1])
        except curses.error:
            pass

        x = 1
        for action in actions:
            label = SHORT_NAMES.get(action, None)
            if label is None:
                continue
            label = tr(label) + " "

            keys = [k for k, v in mapping.items() if v == action]
            keys_custom = [k for k, v in self.app.key_mapping_custom.items() if v == action]

            if any(k not in base_keymap for k in keys):
                if len(keys_custom) > 0:
                    keys = keys_custom
                else:
                    # preferably show user-defined key bindings,
                    # so filter out those that are in the default key mapping
                    keys = [k for k in keys
                            if k not in base_keymap or
                            base_keymap.get(k, None) != action]

            if len(keys) == 0:
                continue
            keytext = []
            for key in keys[0]:
                if key in Key.SPECIAL:
                    keytext.append(tr(Key.SPECIAL[key]))
                else:
                    keytext.append(tr(key))
            keytext = ' ' + ''.join(keytext) + ' '
            if x + len(keytext) + len(label) >= self.dim[1]:
                break

            self.win.addstr(0, x, keytext, self.app.color(common.SETTING_COL_HELP_KEY))
            x += len(keytext)
            self.win.addstr(0, x, label, self.app.color(common.SETTING_COL_HELP_TEXT))
            x += len(label) + 1
        self.win.noutrefresh()


class RemappedScrollPanel(ScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.SCROLL_NEXT = [keys[0]
                            for keys, value in self.app.key_mapping.items()
                            if value == 'next-item']
        self.SCROLL_PREVIOUS = [keys[0]
                                for keys, value in self.app.key_mapping.items()
                                if value == 'prev-item']
        self.SCROLL_NEXT_PAGE = [keys[0]
                                 for keys, value in self.app.key_mapping.items()
                                 if value == 'page-down']
        self.SCROLL_PREVIOUS_PAGE = [keys[0]
                                     for keys, value in self.app.key_mapping.items()
                                     if value == 'page-up']
        self.SCROLL_TO_START = [keys[0]
                                for keys, value in self.app.key_mapping.items()
                                if value == 'first-item']
        self.SCROLL_TO_END = [keys[0]
                              for keys, value in self.app.key_mapping.items()
                              if value == 'last-item']

        self.SCROLL_MARGIN = self.app.scroll_margin


class TaskList(RemappedScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = []
        self.max_widths = {}
        self.cursor = 0
        self.SCROLL_MARGIN = self.app.scroll_margin

    def _select_by_index(self, index):
        oldcursor = self.cursor
        ret = super()._select_by_index(index)
        if self.cursor != oldcursor and self.app.on_select is not None:
            self.app.defer_hook(self.app.on_select)
        return ret

    def rebuild_items(self):
        self.items = []
        self.max_widths = {}

        today = datetime.date.today()

        self.update_max_width(common.TF_DONE,
                              max(len(self.app.done_marker[0]),
                                  len(self.app.done_marker[1])))
        self.update_max_width(common.TF_SELECTION, self.app.selection_indicator)
        self.update_max_width(common.TF_TRACKING, self.app.tracking_marker)
        self.update_max_width(common.TF_DUE,
                              max([len(m) for m in self.app.due_marker]))

        for nr, pair in enumerate(self.tasks):
            task, _ = pair
            line = TaskLine(task, task.todotxt)

            # Selection indicator
            if len(self.app.selection_indicator) > 0:
                line.elements[common.TF_SELECTION] = TaskLineSelectionIcon(self.app.selection_indicator)

            # Item number
            text = str(nr+1)
            line.add(common.TF_NUMBER, text)
            self.update_max_width(common.TF_NUMBER, text)

            # Done marker
            done_marker = self.app.done_marker[1 if task.is_completed else 0]
            line.add(common.TF_DONE, done_marker)

            # Source file name
            line.add(common.TF_FILE, task.todotxt.displayname, common.SETTING_COL_FILE)

            # Age
            if task.creation_date is not None:
                text = str((datetime.date.today() - task.creation_date).days)
                line.add(common.TF_AGE, text)
                self.update_max_width(common.TF_AGE, text)

            # Creation date
            if task.creation_date is not None:
                text = self.app.date_as_str(task.creation_date, common.TF_CREATED)
                line.add(common.TF_CREATED, text)
                self.update_max_width(common.TF_CREATED, text)

            # Completion date
            if task.completion_date is not None:
                text = self.app.date_as_str(task.completion_date, common.TF_COMPLETED)
                line.add(common.TF_COMPLETED, text)
                self.update_max_width(common.TF_COMPLETED, text)

            # Line number
            if task.linenr is not None:
                text = str(task.linenr+1)
                line.add(common.TF_LINENR, text)
                self.update_max_width(common.TF_LINENR, text)

            # Tracking
            if task.attributes.get(common.ATTR_TRACKING, None) is not None:
                line.add(common.TF_TRACKING, self.app.tracking_marker)

            # Due marker
            if line.due is not None:
                duedays = str((line.due - today).days)
                line.add(common.TF_DUEDAYS, duedays)
                self.update_max_width(common.TF_DUEDAYS, duedays)

                if not task.is_completed:
                    if line.due < today:
                        line.add(common.TF_DUE,
                                 self.app.due_marker[0],
                                 common.SETTING_COL_OVERDUE)
                    elif line.due == today:
                        line.add(common.TF_DUE,
                                 self.app.due_marker[1],
                                 common.SETTING_COL_DUE_TODAY)
                    elif line.due == today + datetime.timedelta(days=1):
                        line.add(common.TF_DUE,
                                 self.app.due_marker[2],
                                 common.SETTING_COL_DUE_TOMORROW)

            # Priority marker
            if task.priority is not None:
                pri = task.priority.upper()
                attrs = None
                if pri == 'A':
                    attrs = common.SETTING_COL_PRI_A
                elif pri == 'B':
                    attrs = common.SETTING_COL_PRI_B
                elif pri == 'C':
                    attrs = common.SETTING_COL_PRI_C
                elif pri == 'D':
                    attrs = common.SETTING_COL_PRI_D
                line.add(common.TF_PRIORITY, f"{pri}", attrs)
                self.update_max_width(common.TF_PRIORITY, '(A)')

            # Note
            notes = task.attributes.get('note', [])
            if len(notes) > 0:
                self.update_max_width(common.TF_NOTE, notes[0])
                line.add(common.TF_NOTE, notes[0], None)

            # Projects
            if len(task.projects) > 0:
                projects = ', '.join(task.projects)
                self.update_max_width(common.TF_PROJECTS, len(projects))
                line.add(common.TF_PROJECTS, projects, None)

            # Contexts
            if len(task.contexts) > 0:
                contexts = ', '.join(task.contexts)
                self.update_max_width(common.TF_CONTEXTS, len(contexts))
                line.add(common.TF_CONTEXTS, contexts, None)

            # Time spent
            spent = task.attributes.get('spent', [])
            if len(spent) > 0:
                total_time = datetime.timedelta(0)
                for duration in spent:
                    try:
                        duration = utils.parse_duration(duration)
                    except ValueError:
                        continue
                    if duration is None:
                        continue
                    total_time += duration
                total_time = utils.duration_as_str(total_time)
                self.update_max_width(common.TF_SPENT, len(total_time))
                line.add(common.TF_SPENT, total_time, None)

            # Description
            description = TaskLineDescription()
            if task.description is not None:
                taskdescription = utils.clean_description(task.description)
                for word in taskdescription.split(' '):
                    if len(word) == 0:
                        continue

                    attr = None

                    if word.startswith('@') and len(word) > 1:
                        attr = common.SETTING_COL_CONTEXT
                    elif word.startswith('+') and len(word) > 1:
                        attr = common.SETTING_COL_PROJECT
                    elif ':' in word:
                        key, value = word.split(':', 1)
                        if 'hl:' + key in self.app.colors:
                            attr = 'hl:' + key
                        if key in [common.ATTR_T, common.ATTR_DUE]:
                            word = key + ':' + self.app.date_as_str(value, key)
                        if key == common.ATTR_PRI:
                            attr = None
                            value = value.upper()
                            if value == 'A':
                                attr = common.SETTING_COL_PRI_A
                            elif value == 'B':
                                attr = common.SETTING_COL_PRI_B
                            elif value == 'C':
                                attr = common.SETTING_COL_PRI_C
                            elif value == 'D':
                                attr = common.SETTING_COL_PRI_D
                    description.append(word, attr, space_around=True)
            line.elements[common.TF_DESCRIPTION] = description
            self.update_max_width(common.TF_DESCRIPTION,
                                  ' '.join([e.content for e in description.elements]))

            self.items.append(line)
        self.cursor = min(self.cursor, len(self.items)-1)

    def update_max_width(self, name, textlen):
        if name not in self.max_widths:
            self.max_widths[name] = 0
        if isinstance(textlen, str):
            textlen = len(textlen)
        for tf in self.app.task_format:
            if not isinstance(tf, tuple):
                continue
            tname, _, left, right = tf
            if tname == name:
                textlen += 0 if left is None else len(left)
                textlen += 0 if right is None else len(right)
        self.max_widths[name] = max(textlen, self.max_widths[name])

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)

    def do_paint_item(self, y, x, maxwidth, is_selected, taskline):
        is_tracked = len(taskline.task.attr_tracking) > 0

        baseattrs = common.SETTING_COL_NORMAL
        if taskline.is_completed:
            baseattrs = common.SETTING_COL_COMPLETED
        if taskline.is_overdue:
            baseattrs = common.SETTING_COL_OVERDUE
        elif taskline.is_due_tomorrow:
            baseattrs = common.SETTING_COL_DUE_TOMORROW
        elif taskline.is_due_today:
            baseattrs = common.SETTING_COL_DUE_TODAY
        if is_tracked:
            baseattrs = common.SETTING_COL_TRACKING

        def print_element(y, x, maxwidth, element, align, extra):
            cut_off = False
            if isinstance(element, TaskLineSelectionIcon) and not is_selected:
                elem = ''
            elif isinstance(element, TaskLineGroup):
                return print_group(y, x, maxwidth, element, align, extra)
            elif isinstance(element, str):
                element = TaskLineElement(element)
                elem = element.content
            else:
                elem = element.content

            if align is not None:
                width = self.max_widths.get(element.name, 0)
                if extra is not None and extra[0] is not None:
                    width -= len(extra[0])
                if extra is not None and extra[1] is not None:
                    width -= len(extra[1])
                width = max(0, width)
                elem = f"{elem:{align}{width}}"
            elif len(elem) == 0:
                return ''

            if extra_left is not None:
                elem = extra_left + elem

            if extra_right is not None:
                elem = elem + extra_right

            elemlen = len(elem)
            if elemlen > maxwidth:
                cut_off = True
                elem = elem[:maxwidth]

            color = self.app.color(element.color, is_selected, baseattrs)
            try:
                self.win.addstr(y, x, elem, color)
            except curses.error:
                pass

            if cut_off:
                attrs = common.SETTING_COL_OVERFLOW
                try:
                    self.win.addstr(y, x+maxwidth-len(self.app.overflow_marker[1]),
                                    self.app.overflow_marker[1],
                                    self.app.color(attrs, is_selected, baseattrs))
                except curses.error:
                    pass
            return elem

        def print_group(y, x, maxwidth, group, align, extra):
            line = ''

            if extra is not None and extra[0] is not None:
                color = self.app.color(baseattrs, is_selected)
                self.win.addstr(y, x + len(line), extra[0], color)
                line = extra[0]

            if align is not None and align.endswith('>'):
                group_width = len(' '.join([e.content for e in group.elements]))
                spacing_width = min(maxwidth - len(line),
                                    self.max_widths[group.name] - group_width)
                spacing = align[0] * spacing_width
                color = self.app.color(baseattrs, is_selected)
                try:
                    self.win.addstr(y, x + len(line), spacing, color)
                except curses.error:
                    pass
                line += spacing

            cut_off = False
            for elnr, element in enumerate(group.elements):
                word = ''

                if elnr > 0 and (element.space_around or
                                 group.elements[elnr-1].space_around):
                    if len(line) + 1 >= maxwidth:
                        cut_off = True
                    else:
                        self.win.addstr(y, x + len(line), " ",
                                        self.app.color(baseattrs, is_selected))
                        line += " "

                cut_off = cut_off or len(line) >= maxwidth

                if not cut_off:
                    if isinstance(element, TaskLineGroup):
                        word = print_group(y, x + len(line),
                                           maxwidth-len(line),
                                           element, None, None)
                    else:
                        word = print_element(y, x + len(line),
                                             maxwidth-len(line),
                                             element, None, None)
                    line += word

                if cut_off or len(line) >= maxwidth:
                    break

            if not cut_off and align is not None and align.endswith('<'):
                if len(line) < self.max_widths[group.name]:
                    spacing = align[0] * min(maxwidth-len(line),
                                             self.max_widths[group.name]-len(line))
                    self.win.addstr(y, x + len(line),
                                    spacing,
                                    self.app.color(baseattrs, is_selected))
                    line += spacing

            if not cut_off and extra is not None and \
               extra[1] is not None and len(line) + 1 < maxwidth:
                color = self.app.color(baseattrs, is_selected)
                self.win.addstr(y, x + len(line), extra[1], color)
            return line

        self.win.move(y, x)
        self.win.clrtoeol()
        self.win.noutrefresh()

        for token in self.app.task_format:
            align = None
            extra = None
            if isinstance(token, tuple):
                token, align, extra_left, extra_right = token
                extra = (extra_left, extra_right)
                token = taskline.elements.get(token, TaskLineElement('', name=token))
            elif isinstance(token, str):
                token = TaskLineElement(token)
            else:
                raise TypeError()

            x += len(print_element(y, x, maxwidth-x, token, align, extra))

            if x >= maxwidth:
                break

        if x < maxwidth:
            color = self.app.color(baseattrs, is_selected)
            try:
                self.win.addstr(y, x, ' '*(maxwidth-x), color)
            except curses.error:
                pass

    def jump_to(self, item):
        if item in self.items:
            self.cursor = self.items.index(item)

        elif isinstance(item, int):
            if item < 0 or item >= len(self.items):
                return False
            self.cursor = item

        elif isinstance(item, (TaskLine, Task)):
            if isinstance(item, TaskLine):
                task = str(item.source.filename) + "\n" + str(item.task)
            elif isinstance(item, Task):
                task = str(item.todotxt.filename) + "\n" + str(item)
            else:
                return False

            matching = [idx for idx, t in enumerate(self.items)
                        if str(t.source.filename) + "\n" + str(t.task) == task]

            if len(matching) == 0:
                return False
            self.cursor = matching[0]

        else:
            return False

        self.app.defer_hook(self.app.on_select)
        self.scroll()
        return True


class RemappedInputLine(InputLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cursor_changed = False
        self.word_boundaries = self.app.word_boundaries

    def focus(self):
        y, x = super().focus()
        if not self.cursor_changed:
            self.cursor_changed = True
            self.app.show_cursor(True)
        return y, x

    def on_submit(self):
        pass

    def on_cancel(self):
        pass

    def on_change(self):
        self.update_completion()

    def on_timeout(self):
        return False

    def handle_key(self, key):
        fnc = self.app.editor_key_mapping.get(str(key), None)

        handled = True
        must_repaint = False
        text_before = self.text
        current_word = None
        if self.completion is not None:
            current_word = self.current_word()

        if key == Key.TIMEOUT:
            must_repaint = self.on_timeout()
        elif self.completion is not None and self.completion.handle_key(key):
            handled = True
        elif fnc == 'cancel':
            self.on_cancel()
        elif fnc == 'submit-input':
            self.on_submit()
        elif fnc == 'del-left' and self.cursor > 0:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor -= 1
            must_repaint = True
        elif fnc == 'del-right':
            self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
            must_repaint = True
        elif fnc == 'del-to-bol':
            self.text = self.text[self.cursor:]
            self.cursor = 0
            must_repaint = True
        elif fnc == 'del-to-eol':
            self.text = self.text[:self.cursor]
            must_repaint = True
        elif fnc == 'del-word-left':
            if self.cursor > 0:
                special_char_idx = self.cursor - 1
                while special_char_idx > 0 and self.text[special_char_idx - 1] not in self.word_boundaries:
                    special_char_idx -= 1

                # if it's a space, delete it
                if special_char_idx > 0 and self.text[special_char_idx - 1] == ' ':
                    special_char_idx = special_char_idx - 1

                if special_char_idx == 0:
                    new_text = self.text[self.cursor:]
                    new_cursor = 0
                else:
                    new_text = self.text[:special_char_idx] + self.text[self.cursor:]
                    new_cursor = special_char_idx

                self.text = new_text
                self.cursor = new_cursor
                must_repaint = True
        elif fnc == 'del-word-right':
            eol_idx = len(self.text)
            if self.cursor < eol_idx:
                special_char_idx = self.cursor + 1
                while special_char_idx < eol_idx and self.text[special_char_idx] not in self.word_boundaries:
                    special_char_idx += 1

                if special_char_idx < eol_idx:
                    if self.text[special_char_idx] == ' ':
                        new_text = self.text[:self.cursor] + self.text[special_char_idx+1:] # if it's a space, delete it
                    else:
                        new_text = self.text[:self.cursor] + self.text[special_char_idx:] # otherwise, delete up to the special char
                else:
                    new_text = self.text[:self.cursor]

                self.text = new_text
                must_repaint = True
        elif fnc == 'go-left':
            self.cursor = max(0, self.cursor-1)
            must_repaint = self.scroll()
        elif fnc == 'go-right':
            self.cursor = min(len(self.text), self.cursor+1)
            must_repaint = self.scroll()
        elif fnc == 'go-word-left':
            if self.cursor > 0:
                special_char_idx = self.cursor - 1
                while special_char_idx > 0 and self.text[special_char_idx - 1] not in self.word_boundaries:
                    special_char_idx -= 1

                if special_char_idx == 0:
                    new_cursor = 0
                else:
                    if self.text[special_char_idx - 1] == ' ': # if it's a space, place cursor on it
                        new_cursor = special_char_idx - 1
                    else:
                        new_cursor = special_char_idx # otherwise, place cursor before special char

                self.cursor = new_cursor
                must_repaint = self.scroll()
        elif fnc == 'go-word-right':
            eol_idx = len(self.text)
            if self.cursor < eol_idx:
                special_char_idx = self.cursor + 1
                while special_char_idx < eol_idx and self.text[special_char_idx] not in self.word_boundaries:
                    special_char_idx += 1

                if special_char_idx < eol_idx:
                    if self.text[special_char_idx] == ' ': # if it's a space, place cursor on it
                        new_cursor = special_char_idx
                    else:
                        new_cursor = special_char_idx + 1 # otherwise, place cursor after special char
                else:
                    new_cursor = eol_idx

                self.cursor = new_cursor
                must_repaint = self.scroll()
        elif fnc == 'go-bol':
            self.cursor = 0
            must_repaint = self.scroll()
        elif fnc == 'go-eol':
            self.cursor = len(self.text)
            must_repaint = self.scroll()
        elif fnc == 'goto-empty':
            empty_field = utils.EMPTY_FIELD_RE.search(self.text, self.cursor)
            if empty_field is None and self.app.tab_cycles:
                empty_field = utils.EMPTY_FIELD_RE.search(self.text, 0)
            if empty_field:
                self.cursor = min(len(self.text), empty_field.end(1))
                must_repaint = self.scroll()

        elif len(str(key)) == 1:
            self.text = self.text[:self.cursor] + str(key) + self.text[self.cursor:]
            self.cursor += 1
            must_repaint = True
        else:
            handled = False

        if self.completion is not None and self.current_word() != current_word:
            self.completion.close()

        if text_before != self.text:
            self.on_change()

        if must_repaint:
            self.paint()

        return handled


class InvertedSuggestionPanel(ScrollPanel):
    def __init__(self, parent):
        super().__init__(parent.app)
        self.color = parent.COLOR
        self.alt_color = parent.ALT_COLOR

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attr = curses.A_NORMAL
        if is_selected:
            attr = curses.A_REVERSE
        if isinstance(item, Completion.Suggestion):
            label = item.label if item.label is not None else item.text
        else:
            label = str(item)
        label = label[:maxwidth]
        label = label + " "*(maxwidth-len(label)+1)
        try:
            self.win.addstr(y, x, label[:maxwidth], attr)
        except curses.error:
            pass


class ContextCompletion(Completion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.suggestion_box_type = InvertedSuggestionPanel
        self.KEYS_NEXT_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                      if value == 'comp-next']
        self.KEYS_PREVIOUS_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                          if value == 'comp-prev']
        self.KEYS_SELECT_ALTERNATIVE = [key for key, value in self.app.completion_key_mapping.items()
                                        if value == 'comp-use']
        self.KEYS_CANCEL_SUGGESTIONS = [key for key, value in self.app.completion_key_mapping.items()
                                        if value == 'comp-close']

    def close(self):
        retval = super().close()
        if retval:
            self.app.paint(True)
        return retval

    def update(self, y, x):
        span = self.inputline.current_word()

        if span is None:
            self.close()
            return

        word = self.inputline.text[span[0]:self.inputline.cursor].lower()
        if word.startswith('@'):
            options = self.app.known_contexts()
        elif word.startswith('+'):
            options = self.app.known_projects()
        elif word.startswith('note:'):
            options = set()
            seen = set()
            for basepath in self.app.notes:
                if not basepath.is_dir():
                    continue
                paths = [basepath]
                while len(paths) > 0:
                    path = paths.pop(0)
                    options |= {'note:' + str(p.relative_to(basepath))
                                for p in path.iterdir()
                                if p.is_file()}
                    paths += [p
                              for p in path.iterdir()
                              if p.is_dir() and p not in seen]
                    seen |= set(paths)
        elif word.startswith('file:') and self.app.focus[-1] is self.app.search_bar:
            options = set(['file:' + source.displayname for source in self.app.sources])
        else:
            return

        options = [o for o in sorted(options)
                   if o.lower().startswith(word)]

        if len(options) == 0 or (len(options) == 1 and word in options):
            self.close()
            return

        self.set_alternatives(options, (y, x))
        self.app.paint()


class SearchBar(RemappedInputLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.previous_text = self.text
        if self.app.use_completion:
            self.completion = ContextCompletion(self)

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        if clear:
            self.win.erase()
        self.scroll()

        attr = 0
        if len(self.text) == 0 and (len(self.app.focus) == 0 or
                                    self.app.focus[-1] is not self):
            visible_text = tr('(no search active)')
            attr = self.app.color(common.SETTING_COL_INACTIVE)
        else:
            visible_text = self.text[self.offset:]

        visible_text = visible_text[:self.dim[1]]
        try:
            self.win.addstr(0, 0, " "*self.dim[1])
        except curses.error:
            pass
        self.win.addstr(0, 0, visible_text, attr)
        self.win.noutrefresh()

        if self.completion is not None:
            self.completion.paint(clear)

    def on_change(self):
        self.update_completion()
        self.app.search.text = self.text
        self.app.search.parse()
        self.app.apply_search()
        self.app.tasks.paint(True)
        if self.app.focus[-1] is self:
            self.focus()

    def on_submit(self):
        self.previous_text = self.text
        self.unfocus()

    def on_cancel(self):
        self.text = self.previous_text
        self.unfocus()

    def unfocus(self):
        self.cursor_changed = False
        self.app.show_cursor(False)
        self.app.focus.pop(-1)
        self.scroll()
        self.app.paint()


class UserInput(Panel):
    def __init__(self, parent, on_accept, on_cancel=None, title='', text=''):
        super().__init__(parent.app)
        self.parent = parent
        self.title = title
        self.on_accept = on_accept
        self.custom_on_cancel = on_cancel
        self.editor = RemappedInputLine(self.app, 1, (1, 1))
        self.border = Panel.BORDER_ALL
        self.editor.text = text
        self.editor.cursor = len(self.editor.text)
        self.editor.on_cancel = self.on_cancel
        self.editor.on_submit = self.on_submit
        self.autoresize()

    def destroy(self):
        super().destroy()
        self.app.focus.pop(-1)
        self.app.paint(True)

    def handle_key(self, key):
        return self.editor.handle_key(key)

    def focus(self):
        if self.app.focus[-1] is self:
            y, x = self.editor.focus()
            self.win.move(y + 1, x + 1)
            self.win.noutrefresh()

    def autoresize(self):
        maxheight, maxwidth = self.app.size()
        width = 2*maxwidth//3
        if width < 22:
            width = maxwidth
        self.resize(3, width)
        y = maxheight//2 - 2
        x = (maxwidth - width)//2
        self.move(y, x)
        self.editor.resize(width-2)
        self.editor.move(y+1, x+1)

    def paint(self, clear=None):
        super().paint(clear)
        label = tr(self.title)
        if self.editor.read_only:
            label += ' ' + tr("(read-only)")
        add_title(self, tr(self.title))
        self.win.noutrefresh()
        self.editor.paint(clear)
        self.editor.focus()

    def on_cancel(self):
        if self.custom_on_cancel is not None:
            self.custom_on_cancel()
        self.app.show_cursor(False)
        self.destroy()

    def on_submit(self):
        self.on_accept(self.editor.text)
        self.app.show_cursor(False)
        self.destroy()


class TaskEditor(UserInput):
    def __init__(self, parent, task):
        super().__init__(parent, None, None, 'Edit task',
                         '' if task is None else
                            utils.clean_description(str(task.task)))
        self.task = task
        self.on_accept = self.save_changes
        self.on_cancel = lambda: self.app.show_cursor(False)
        if self.app.use_completion:
            self.editor.completion = ContextCompletion(self.editor)

    def save_changes(self, text):
        self.app.show_cursor(False)
        if self.has_changes() and not self.editor.read_only:
            text = self.processed_text
            _, task = self.app.modify_task(self.task, lambda t: t.parse(text))
            self.app.run_hook(self.app.on_change, task)

    @property
    def processed_text(self):
        return utils.dehumanize_dates(utils.auto_task_id(self.app.sources,
                                                         self.editor.text),
                                      businessdays=self.app.business_days)

    def has_changes(self):
        return str(self.task.task) != self.processed_text


class TaskCreator(TaskEditor):
    def __init__(self, parent):
        super().__init__(parent, None)
        self.title = 'New task'

        add_creation_date = self.app.conf.bool(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_ADD_CREATED)
        create_from_search = self.app.conf.bool(common.SETTING_GROUP_GENERAL,
                                                common.SETTING_CREATE_FROM_SEARCH)
        self.auto_id = self.app.conf.bool(common.SETTING_GROUP_GENERAL,
                                          common.SETTING_AUTO_ID)
        self.editor.cursor = 1
        self.auto_selected_template = None

        initial = []
        if add_creation_date:
            create_date = datetime.datetime.now().strftime(Task.DATE_FMT)
            initial.append(create_date)
            self.editor.cursor += len(create_date)
        if create_from_search:
            initial.append(utils.create_from_search(self.app.search))
        if self.app.selected_template is not None:
            initial.append(self.app.selected_template)

        initial = ' '.join([part for part in initial if len(part) > 0])
        if len(initial) > 0 and not initial.endswith(' '):
            initial += ' '
        self.editor.text = initial
        self.editor.scroll()

        self.task = Task(initial, todotxt=self.app.sources[0])

    def handle_key(self, key):
        fnc = self.app.editor_key_mapping.get(str(key), None)

        if fnc == 'select-file' and len(self.app.sources) > 1:
            self.app.show_cursor(False)
            self.app.focus.append(SourceSelector(self,
                                                 self.app.sources,
                                                 self.change_source,
                                                 lambda: self.app.show_cursor(True)))
            self.app.paint(True)
            return True

        if fnc == 'submit-without-template':
            self.auto_selected_template = None
            self.on_submit()
            return True

        success = super().handle_key(key)

        if success:
            matched_any = False
            for template in self.app.auto_templates:
                if not template.can_trigger(self.editor.text,
                                            self.app.auto_template_casing):
                    continue
                matched_any = True
                if self.auto_selected_template == template:
                    break
                self.auto_selected_template = template
                self.app.paint(True)
                break
            if not matched_any:
                if self.auto_selected_template is not None:
                    self.auto_selected_template = None
                    self.app.paint(True)

        return success

    def change_source(self, source):
        self.task.todotxt = source
        self.app.show_cursor(True)
        self.paint(True)

    def save_changes(self, text):
        self.app.show_cursor(False)
        if self.has_changes() and not self.editor.read_only and self.processed_text != "":
            if self.auto_selected_template is not None:
                self.editor.text += ' ' + self.auto_selected_template.template

            text = self.processed_text

            if self.auto_id and not any([word.startswith('id:') for word in text.split(' ')]):
                text += ' id:#'
                text = utils.auto_task_id(self.app.sources, text)

            self.task.parse(text)

            source = self.task.todotxt
            # reload if necessary
            if source.refresh():
                source.parse()

            # append the new task and save
            source.tasks.append(self.task)
            source.save(safe=self.app.safe_save)

            # update book keeping
            source.update_from_task(self.task)
            self.task.linenr = len(source.tasks)

            self.app.search.update_sources(self.app.sources)
            self.app.update_tasks()
            self.app.tasks.jump_to(self.task)
            self.app.defer_hook(self.app.on_new, self.task)

    def paint(self, clear=False):
        super().paint(clear)

        if len(self.app.sources) > 1:
            label = self.task.todotxt.displayname
            self.win.addstr(2, self.dim[1]-len(label)-3, title_frame(label))
            self.win.noutrefresh()

        if self.auto_selected_template is not None:
            label = self.auto_selected_template.name
            self.win.addstr(2, 1, title_frame(tr("Auto template: ") + label))
            self.win.noutrefresh()

    def has_changes(self):
        return str(self.task) != self.processed_text


class Selector(RemappedScrollPanel):
    def __init__(self, parent, items, on_select, on_cancel=None, title='', numbered=False):
        super().__init__(parent.app)
        self.parent = parent
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.items = items
        self.title = title
        self.numbered = numbered
        self.autoresize()

    def paint(self, clear=False):
        super().paint(clear)
        if len(self.title) > 0:
            add_title(self, tr(self.title))
            self.win.noutrefresh()

    def autoresize(self):
        self.border = Panel.BORDER_ALL
        if hasattr(self.parent, 'autoresize'):
            self.parent.autoresize()
        maxheight, maxwidth = self.app.size()
        labelwidth = max([len(self.make_label(item))
                          for item in self.items + [tr(self.title)]]) \
                   + len(self.indicator(True)) \
                   + len(str(len(self.items))) + 3
        w = min(maxwidth, labelwidth)
        h = min(maxheight-2, len(self.items)+2)
        self.resize(h, w)
        self.move((maxheight-h)//2, (maxwidth-w)//2)

    def handle_key(self, key):
        strkey = str(key)
        fnc = self.app.key_mapping.get((strkey,), None)

        if fnc == 'cancel':
            self.destroy()
            if self.on_cancel is not None:
                self.on_cancel()
            return True

        elif fnc == 'select-item':
            item = self.selected_item
            self.destroy()
            self.on_select(item)
            return True

        elif fnc == 'jump-to':
            self.app.focus.append(JumpToIndexReader(self.app, ''))
            self.app.paint(True)
            return True

        elif len(strkey) == 1 and strkey in string.digits:
            self.app.focus.append(JumpToIndexReader(self.app, strkey))
            self.app.paint(True)
            return True

        return super().handle_key(key)

    def number_prefix(self, item):
        if not self.numbered:
            return ""

        idx = self.items.index(item)
        nrwidth = len(str(len(self.items)+1))
        return f"{idx+1: >{nrwidth}} "

    def indicator(self, is_selected):
        if self.app.use_colors and not len(self.app.selection_indicator) > 0:
            return ""
        pointer = self.app.selection_indicator + " "
        if not is_selected:
            pointer = " "*len(pointer)
        return pointer

    def make_label(self, item):
        return str(item)

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attrs = self.app.color(common.SETTING_COL_NORMAL, is_selected)

        label = self.indicator(is_selected) + self.number_prefix(item) + self.make_label(item)

        label = label[:maxwidth]
        label = label + " "*(maxwidth-len(label))

        self.win.addstr(y, x, label, attrs)

    def destroy(self):
        super().destroy()
        self.app.focus.pop(-1)
        self.app.paint(True)


class SourceSelector(Selector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = 'Select file'

    def make_label(self, item):
        if isinstance(item, str):
            return item
        return item.displayname


class HelpScreen(RemappedScrollPanel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        lines = compile_key_listing(self.app)

        self.maxnamelen = max([len(n) for n, _, _ in lines])

        self.items = lines
        self.border = Panel.BORDER_ALL
        self.SCROLL_MARGIN = 1000

        self.key_sequence = []
        self.key_mapping = {k: fnc
                            for k, fnc in self.app.key_mapping.items()
                            if fnc in ['cancel', 'next-item',
                                       'prev-item', 'page-up', 'page-down',
                                       'first-item', 'last-item',
                                       'refresh-screen']}

    def resize(self, *args):
        super().resize(*args)
        self.scroll()

    def scroll(self):
        self.cursor = max((self.list_height-1)//2, self.cursor)
        super().scroll()

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        attrs = common.SETTING_COL_NORMAL
        if item[1] == '':
            attrs = common.SETTING_COL_CONTEXT
        keytext = ''.join(item[1])
        fnclabel = item[0]
        self.win.addstr(y, x, fnclabel + " "*(self.maxnamelen-len(fnclabel)+3) + keytext, self.app.color(attrs))
        self.win.noutrefresh()

    def handle_key(self, key):
        handled = False
        must_clear = False
        must_paint = False
        kseq_consumed = True

        if key == Key.TIMEOUT:
            return handled

        kseq = tuple(self.key_sequence + [str(key)])
        fnc = self.key_mapping.get(kseq)

        if fnc == 'cancel':
            self.destroy()
            self.app.focus.pop(-1)
            self.app.paint(True)
            handled = True

        elif fnc == 'refresh-screen':
            self.app.do_refresh_screen()
            handled = True

        elif fnc == 'next-item':
            self.offset = min(len(self.items)-self.content_area()[2],
                              self.offset + 1)
            must_paint = True
            must_clear = True
            handled = True

        elif fnc == 'prev-item':
            self.offset = max(0, self.offset - 1)
            must_paint = True
            must_clear = True
            handled = True

        elif fnc == 'page-down':
            self.offset = min(len(self.items)-self.content_area()[2],
                              self.offset + self.content_area()[2])
            must_paint = True
            must_clear = True
            handled = True

        elif fnc == 'page-up':
            self.offset = max(0, self.offset - self.content_area()[2])
            must_paint = True
            must_clear = True
            handled = True

        elif fnc == 'first-item':
            self.jump_to(0)
            must_paint = True
            must_clear = True
            handled = True

        elif fnc == 'last-item':
            self.jump_to(len(self.items)-1)
            must_paint = True
            must_clear = True
            handled = True

        elif any(k[:len(kseq)] == kseq for k in self.key_mapping.keys()):
            self.key_sequence = list(kseq)
            self.app.key_sequence_info(''.join(kseq))
            handled = True
            kseq_consumed = False

        else:
            self.app.error(tr("No such keybinding"))
            self.key_sequence = []

        if kseq_consumed:
            self.key_sequence = []
        if handled and len(self.key_sequence) == 0:
            self.app.key_sequence_info('')
        if must_paint:
            self.paint(must_clear)
        return handled


class JumpToIndexReader(RemappedInputLine):
    def __init__(self, app, init):
        super().__init__(app, 1, (1,1))
        self.parent = app.focus[-1]
        assert self.parent is not self

        self.prefix = tr("Jump to:") + " "
        self.text = init
        self.cursor = len(self.text)
        self.autoresize()
        self.scroll()

    def autoresize(self):
        height, width = self.app.size()
        self.move(height-2, 0)
        self.resize(width-1)

    def on_submit(self):
        try:
            index = int(self.text)-1
        except ValueError:
            index = None

        if index is not None:
            self.parent.jump_to(index)
        self.destroy()

    def on_cancel(self):
        self.destroy()

    def destroy(self):
        super().destroy()
        self.app.show_cursor(False)
        self.app.focus.pop(-1)
        self.app.status_bar.paint(True)
        self.app.focus[-1].paint(True)


class CursesApplication(Application):
    def __init__(self, sources, conf, initial_search):
        super().__init__()
        self.quit = False
        self.sources = sources
        self.conf = conf
        self.colors = {}
        self.color_cache = {}
        self.all_tasks = []
        self.initial_search = initial_search

        # searching
        case_sensitive = self.conf.get(common.SETTING_GROUP_GENERAL,
                                       common.SETTING_SEARCH_CASE_SENSITIVE).lower()
        try:
            case_sensitive = common.SearchCaseBehaviour(case_sensitive)
        except ValueError:
            logging.error(f"{case_sensitive} is not a valid value for {common.SETTING_SEARCH_CASE_SENSITIVE}")
            case_sensitive = common.SearchCaseBehaviour.SENSITIVE

        # sorting
        self.sort_order_txt = self.conf.get(common.SETTING_GROUP_GENERAL,
                                            common.SETTING_SORT_ORDER)
        self.sort_order = utils.build_sort_order(self.sort_order_txt)

        # business days
        self.business_days = None
        bdays = self.conf.list(common.SETTING_GROUP_GENERAL,
                               common.SETTING_BUSINESS_DAYS,
                               common.DEFAULT_BUSINESS_DAYS)
        try:
            self.business_days = set()
            for value in bdays:
                value = value.lower().strip()
                if value in utils.DAYNAMES:
                    self.business_days.add(utils.DAYNAMES[value])
                else:
                    self.business_days.add(int(value))
        except ValueError as exc:
            self.business_days = None
            rawvalue = self.conf.get(common.SETTING_GROUP_GENERAL, common.SETTING_BUSINESS_DAYS)
            logging.error(f"{common.SETTING_BUSINESS_DAYS} has an invalid value '{rawvalue}': {exc}")

        # searching
        self.search = Searcher('',
                               case_sensitive,
                               self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_DEFAULT_THRESHOLD),
                               self.conf.bool(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HIDE_SEQUENTIAL),
                               self.business_days)
        self.search.update_sources(self.sources)

        # auto templates
        try:
            auto_template_casing = common.SearchCaseBehaviour(
                                self.conf.get(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_AUTO_TEMPLATE_CASING).lower())
        except ValueError:
            auto_template_casing = common.SearchCaseBehaviour.SENSITIVE
        self.auto_template_casing = auto_template_casing
        self.auto_templates = list(load_auto_templates())

        # task display
        self.task_format = utils.parse_task_format(conf.get(common.SETTING_GROUP_GENERAL,
                                                            common.SETTING_TASK_FORMAT,
                                                            common.DEFAULT_TASK_FORMAT))
        self.done_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_NOT_DONE)),
                            utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                   common.SETTING_ICON_DONE)))
        self.overflow_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_LEFT)),
                                utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                       common.SETTING_ICON_OVERFLOW_RIGHT)))
        self.due_marker = (utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_OVERDUE)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TODAY)),
                           utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                  common.SETTING_ICON_DUE_TOMORROW)))
        self.tracking_marker = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                      common.SETTING_ICON_TRACKING))
        self.human_friendly_dates = conf.list(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_HUMAN_DATES)

        # colors and UI markers
        self.use_colors = conf.bool(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_USE_COLORS)
        self.selection_indicator = utils.unquote(conf.get(common.SETTING_GROUP_SYMBOLS,
                                                          common.SETTING_ICON_SELECTION))

        self.reduce_distraction = conf.bool(common.SETTING_GROUP_GENERAL,
                                            common.SETTING_REDUCE_DISTRACTION,
                                            common.DEFAULT_REDUCE_DISTRACTION)

        # delegation configuration
        self.delegation_marker = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_MARKER).strip()
        self.delegation_action = self.conf.get(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_DELEG_ACTION).lower()
        self.delegate_to = self.conf.get(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_DELEG_TO).lower().strip()
        if self.delegation_action not in common.DELEGATE_ACTIONS:
            logging.error(f"Configuration option 'delegate-option' ('{self.delegation_action}') is invalid.")
            self.delegation_action = common.DELEGATE_ACTION_NONE

        # behaviour
        self.clear_contexts = [context
                               for context in conf.list(common.SETTING_GROUP_GENERAL, common.SETTING_CLEAR_CONTEXT)
                               if len(context) > 0]
        self.reuse_recurring = conf.bool(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_REUSE_RECURRING, 'n')
        self.scroll_margin = conf.number(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_SCROLL_MARGIN)
        # see https://github.com/vonshednob/pter/issues/51
        self.reset_terminal = conf.bool(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_RESET_TERMINAL, 'n')
        self.safe_save = conf.bool(common.SETTING_GROUP_GENERAL,
                                   common.SETTING_SAFE_SAVE, 'y')
        self.use_completion = conf.bool(common.SETTING_GROUP_GENERAL,
                                        common.SETTING_USE_COMPLETION, 'y')
        self.tab_cycles = conf.bool(common.SETTING_GROUP_GENERAL,
                                        common.SETTING_TAB_CYCLES, 'y')

        # delete behaviour
        self.trash_file = conf.path(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_TRASHFILE,
                                    common.DEFAULT_TRASHFILE);
        self.delete_is = conf.get(common.SETTING_GROUP_GENERAL,
                                  common.SETTING_DELETE_IS,
                                  common.DELETE_OPTION_DISABLED)
        if self.delete_is not in common.DELETE_OPTIONS:
            logging.error(f"Configuration option 'delete-is' ('{self.delete_is}') is invalid.")
            self.delete_is = common.DELETE_OPTION_DISABLED
        self.last_perm_delete = datetime.datetime.now()
        self.perm_delete_timeout = datetime.timedelta(milliseconds=500)

        # ensure paths to trash file
        if self.delete_is == common.DELETE_OPTION_TRASH:
            try:
                self.trash_file.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logging.error(f"Could not create path to trash file '{self.trash_file.parent}': {exc}")
                self.delete_is = common.DELETE_OPTION_DISABLED

        # ensure the trash file can be written
        if self.delete_is == common.DELETE_OPTION_TRASH:
            try:
                with open(self.trash_file, 'a', encoding='utf-8'):
                    logging.debug(f"Using trash file {self.trash_file}")
            except OSError as exc:
                logging.error(f"Could not open trash file '{self.trash_file}': {exc}")
                self.delete_is = common.DELETE_OPTION_DISABLED

        # due-delta for quick increase/decrease of due dates
        due_delta = conf.get(common.SETTING_GROUP_GENERAL,
                             common.SETTING_DUE_DELTA,
                             common.DEFAULT_DUE_DELTA)
        self.due_delta = utils.parse_duration(due_delta)

        self.skip_weekend = conf.bool(common.SETTING_GROUP_GENERAL,
                                      common.SETTING_SKIP_WEEKEND,
                                      common.DEFAULT_SKIP_WEEKEND)

        # archive behaviour
        self.archive_file = conf.path(common.SETTING_GROUP_GENERAL,
                                      common.SETTING_ARCHIVE_FILE,
                                      common.DEFAULT_ARCHIVE)
        self.archive_is = conf.get(common.SETTING_GROUP_GENERAL,
                                   common.SETTING_ARCHIVE_IS,
                                   common.ARCHIVE_OPTION_CENTRALISED)
        if self.archive_is not in common.ARCHIVE_OPTIONS:
            logging.error(f"Configuration option 'archive-is' ('{self.archive_is}') is invalid.")
            self.archive_is = common.ARCHIVE_OPTION_DISABLED

        if self.archive_is == common.ARCHIVE_OPTION_CENTRALISED:
            try:
                self.archive_file.parent.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logging.error(f"Could not create path to archive file '{self.archive_file}': {exc}")
                self.archive_is = common.ARCHIVE_OPTION_DISABLED

        self.archive_origin_marker = conf.get(common.SETTING_GROUP_GENERAL,
                                              common.SETTING_ARCHIVE_ORIGIN_MARKER,
                                              '').strip()
        self.archive_origin_is = conf.get(common.SETTING_GROUP_GENERAL,
                                          common.SETTING_ARCHIVE_ORIGIN_IS,
                                          common.ARCHIVE_ORIGIN_FULLPATH)
        if len(self.archive_origin_marker) > 0 and \
           self.archive_origin_is not in common.ARCHIVE_ORIGIN_OPTIONS:
            logging.error(f"Invalid value for '{common.SETTING_ARCHIVE_ORIGIN_IS}'.")
            self.archive_origin_is = common.ARCHIVE_ORIGIN_FULLPATH

        # done behaviour
        self.done_is = conf.get(common.SETTING_GROUP_GENERAL,
                                common.SETTING_DONE_IS,
                                common.DONE_OPTION_MARK)
        if self.done_is not in common.DONE_OPTIONS:
            logging.error(f"Configuration option 'done-is' ('{self.done_is}') is invalid.")
            self.done_is = common.DONE_OPTION_MARK

        self.done_file = None
        if self.done_is in [common.DONE_OPTION_MOVE, common.DONE_OPTION_MARK_MOVE]:
            self.done_file = conf.path(common.SETTING_GROUP_GENERAL,
                                       common.SETTING_DONE_FILE,
                                       common.DEFAULT_DONE)

        # notes
        self.notes = [Path(nb.strip()).expanduser()
                      for nb in self.conf.list(common.SETTING_GROUP_GENERAL,
                                               common.SETTING_NOTES,
                                               sep="\n")
                      if len(nb.strip()) > 0]
        if len(self.notes) == 0:
            self.notes = [Path(source.filename).parent.expanduser()
                          for source in self.sources]
        self.note_suffix = self.conf.get(common.SETTING_GROUP_GENERAL,
                                         common.SETTING_NOTE_SUFFIX,
                                         common.DEFAULT_NOTE_SUFFIX)

        self.note_naming = conf.get(common.SETTING_GROUP_GENERAL,
                                    common.SETTING_NOTE_NAMING,
                                    common.NOTE_NAMING_USER)
        if self.note_naming not in common.NOTE_NAMING_OPTIONS:
            logging.error(f"Configuration option 'note-naming' ('{self.note_naming}') is invalid.")
            self.note_naming = common.NOTE_NAMING_USER

        # external time tracking
        self.tracker = None
        tracker = self.conf.get(common.SETTING_GROUP_GENERAL,
                                common.SETTING_TRACKER,
                                None)
        if tracker is not None:
            hook = Hook(self, tracker)
            if hook.is_ok():
                self.tracker = hook

        # Hooks
        self.deferred_hooks = []
        self.on_start = self.resolve_hook(common.SETTING_HOOK_ON_START)
        self.on_change = self.resolve_hook(common.SETTING_HOOK_ON_CHANGE)
        self.on_archive = self.resolve_hook(common.SETTING_HOOK_ON_ARCHIVE)
        self.on_select = self.resolve_hook(common.SETTING_HOOK_ON_SELECT)
        self.on_done = self.resolve_hook(common.SETTING_HOOK_ON_DONE)
        self.on_delete = self.resolve_hook(common.SETTING_HOOK_ON_DELETE)
        self.on_new = self.resolve_hook(common.SETTING_HOOK_ON_NEW)
        self.on_tracking = self.resolve_hook(common.SETTING_HOOK_ON_TRACKING)
        self.on_quit = self.resolve_hook(common.SETTING_HOOK_ON_QUIT)

        # external editor
        self.external_editor = self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_EXT_EDITOR)

        # external viewer
        self.external_viewer = self.conf.get(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_EXT_VIEWER)

        # protocols accepted to open with open-url
        self.protos = conf.list(common.SETTING_GROUP_GENERAL,
                                common.SETTING_PROTOCOLS)

        self.selected_template = None

        # word boundaries
        boundaries = conf.get(common.SETTING_GROUP_GENERAL,
                              common.SETTING_WORD_BOUNDARIES,
                              common.DEFAULT_WORD_BOUNDARIES)
        if len(boundaries) > 2 and boundaries.startswith('"') and \
           boundaries[0] == boundaries[-1]:
            boundaries = boundaries[1:-1]
        self.word_boundaries = boundaries

        # keys, mappings, and functions
        self.key_sequence = []  # current sequence of keys
        self.key_mapping = DEFAULT_KEY_MAPPING.copy()
        self.key_mapping_custom = {}
        self.editor_key_mapping = DEFAULT_EDITOR_KEY_MAPPING.copy()
        self.completion_key_mapping = {
                '^C': 'comp-close',
                Key.ESCAPE: 'comp-close',
                Key.DOWN: 'comp-next',
                Key.TAB: 'comp-next',
                '^N': 'comp-next',
                Key.UP: 'comp-prev',
                '^P': 'comp-prev',
                Key.RETURN: 'comp-use',
            }
        self.functions = {
            'quit': self.do_quit,
            'nop': lambda: True,
            'cancel': lambda: True,
            'refresh-screen': self.do_refresh_screen,
            'reload-tasks': self.do_reload_tasks,
            'search': self.do_start_search,
            'search-context': self.do_search_context,
            'search-project': self.do_search_project,
            'select-context': self.do_select_context,
            'select-project': self.do_select_project,
            'load-template': self.do_load_template,
            'save-template': self.do_save_template,
            'load-search': self.do_load_search,
            'save-search': self.do_save_search,
            'clear-search': self.do_clear_search,
            'edit-task': self.do_edit_task,
            'edit-external': self.do_edit_task_external,
            'edit-file-external': self.do_edit_file_external,
            'create-task': self.do_create_task,
            'duplicate-task': self.do_duplicate_task,
            'edit-note': self.do_edit_note,
            'view-note': self.do_view_note,
            'jump-to': self.do_jump_to,
            'open-url': self.do_open_url,
            'toggle-tracking': self.do_toggle_tracking,
            'toggle-done': self.do_toggle_done,
            'toggle-hidden': self.do_toggle_hidden,
            'show-help': self.do_show_help,
            'delegate': self.do_delegate,
            'open-manual': utils.open_manual,
            'delete-task': self.do_delete,
            'archive': self.do_archive,
            'show-related': self.do_show_related,
            'to-clipboard': self.do_copy_to_clipboard,
            'inc-due': self.do_increase_due,
            'dec-due': self.do_decrease_due,
            'clear-due': self.do_clear_due,
            'prio-up': self.do_prio_up,
            'prio-down': self.do_prio_down,
            'prio-none': lambda: self.do_set_prio(None),
            'prio-a': lambda: self.do_set_prio('A'),
            'prio-b': lambda: self.do_set_prio('B'),
            'prio-c': lambda: self.do_set_prio('C'),
            'prio-d': lambda: self.do_set_prio('D'),
            }

        # help bar items
        help_actions = conf.get(common.SETTING_GROUP_GENERAL,
                                common.SETTING_HELP_ACTIONS,
                                common.DEFAULT_HELP_ACTIONS).split("\n")
        self.help_actions = [fnc.strip() for fnc in help_actions
                             if fnc.strip() in self.functions]

        # compontents of the UI
        self.search_bar = None
        self.status_bar = None
        self.help_bar = None
        self.tasks = None
        self.focus = []

        self.load_key_configuration()

    def main(self):
        # initialise colors
        if curses.has_colors() and self.use_colors:
            curses.use_default_colors()
            self.update_color_pairs()
        elif len(self.selection_indicator) == 0:
            self.selection_indicator = '>'

        curses.set_escdelay(self.conf.number(common.SETTING_GROUP_GENERAL,
                                             common.SETTING_ESC_TIMEOUT,
                                             str(common.DEFAULT_ESC_TIMEOUT)))
        if self.on_start is not None:
            self.defer_hook(self.on_start)
        if self.on_select is not None:
            self.defer_hook(self.on_select)

        self.tasks = TaskList(self)
        self.search_bar = SearchBar(self, 1, (0, 0))
        self.status_bar = StatusBar(self)
        self.help_bar = HelpBar(self)

        self.show_cursor(False)

        self.resize()
        self.update_tasks()
        if self.initial_search is not None:
            searches = utils.parse_searches()
            if self.initial_search in searches:
                self.set_named_search(searches, self.initial_search)
                self.paint(True)
            else:
                self.set_search(self.initial_search)

        self.paint()
        curses.doupdate()

        # general timeout is 1s
        self.screen.timeout(1000)
        then = datetime.datetime.now()

        self.set_term_title("pter")
        if common.SETTING_GROUP_INCLUDE in self.conf:
            self.error(tr('[Include] in configuration file is deprecated'))
        else:
            self.info(tr('Welcome to pter, version {}').format(version.__version__))
        self.focus = [self.tasks]

        while not self.quit:
            source_changed = False
            must_repaint = False

            # run deferred hooks before the underlying files might change
            for hook in self.deferred_hooks:
                self.run_hook(*hook)
            self.deferred_hooks = []

            # detect changes of the sources
            for source in self.sources:
                if source.refresh():
                    logging.debug(f"Source {source} changed")
                    source.parse()
                    source_changed = True

                    for panel in self.focus:
                        if not isinstance(panel, TaskEditor) or isinstance(panel, TaskCreator):
                            continue

                        if panel.task.source is source:
                            # beware! the currently edited task comes from this source
                            # let's see if we can still find it. if not? it has changed!
                            matching = [t for t in source.tasks if str(t) == str(panel.task.task)]
                            if len(matching) == 0:
                                self.error(tr("Task was changed in the background. Copy your changes to clipboard and start over"))
                                panel.editor.read_only = True

            # detect the passing of midnight
            now = datetime.datetime.now()
            past_midnight = then.day != now.day
            then = now

            if source_changed or past_midnight:
                self.search.parse()
                must_repaint = self.update_tasks()

            if must_repaint:
                logging.debug("Must repaint")
                self.paint(True)
            elif self.status_bar.is_expired() and not isinstance(self.focus[-1], JumpToIndexReader):
                logging.debug("Refreshing status bar")
                self.status_bar.paint()
            if len(self.focus) > 0:
                self.focus[-1].focus()

            curses.doupdate()

            key = Key.read(self.screen)

            if key == Key.RESIZE:
                self.resize()
                self.paint(True)
            elif len(self.focus) == 0:
                continue
            elif self.focus[-1] is self.search_bar:
                self.search_bar.handle_key(key)
            elif isinstance(self.focus[-1], (HelpScreen, UserInput, RemappedInputLine, Selector)):
                self.focus[-1].handle_key(key)
            elif len(self.key_sequence) == 0 and not key.special and str(key) in string.digits:
                self.do_jump_to(str(key))
            elif len(self.key_sequence) == 0 and self.focus[-1].handle_key(key):
                # clear status bar
                if len(self.status_bar.text) > 0:
                    self.info('')
            elif len(self.key_sequence) > 0 and self.key_mapping.get((str(key),), None) == 'cancel':
                self.key_sequence = []
                self.info('')
                logging.debug("Clearing key sequence")
            elif key != Key.TIMEOUT:
                kseq = tuple(self.key_sequence + [str(key)])
                logging.debug(f"Current key sequence: {kseq}")
                fnc = self.key_mapping.get(kseq)
                if fnc is not None:
                    self.info('')
                    self.key_sequence = []
                    if fnc in self.functions:
                        logging.debug(f"Calling {fnc}")
                        self.functions[fnc]()
                elif any(k[:len(kseq)] == kseq for k in self.key_mapping.keys()):
                    self.key_sequence_info(''.join(kseq))
                    self.key_sequence = list(kseq)
                else:
                    self.error(tr('No such keybinding'))
                    self.key_sequence = []

        self.run_hook(self.on_quit)

    def paint(self, clear=False):
        if clear:
            self.screen.erase()

            if self.reset_terminal:
                with ShellContext(self.screen, False):
                    hard_reset_terminal()

        self.screen.noutrefresh()

        if len(self.focus) > 0 and isinstance(self.focus[-1], HelpScreen):
            self.focus[-1].paint(clear)
            self.help_bar.paint()
            return

        attr = self.color(common.SETTING_COL_NORMAL)
        try:
            self.screen.addstr(1, 0, HORIZONTAL_BAR*self.size()[1], attr)
        except curses.error:
            pass
        self.screen.noutrefresh()

        if not self.reduce_distraction or \
           len(self.focus) < 1 or \
           self.focus[-1] is self.tasks or \
           (isinstance(self.focus[-1], JumpToIndexReader) and \
            not any(isinstance(e, Selector) for e in self.focus)):
            self.tasks.paint()
        self.search_bar.paint(clear)
        self.status_bar.paint(clear)
        self.help_bar.paint()
        for panel in self.focus:
            if panel not in [self.tasks, self.search_bar]:
                panel.paint()

    def refresh(self, force=False):
        super().refresh(force)
        self.paint()

    def resize(self):
        height, width = self.size()

        if len(self.focus) > 0 and isinstance(self.focus[-1], HelpScreen):
            self.focus[-1].resize(height-2, width)
            self.focus[-1].move(0, 0)
        for panel in self.focus:
            if hasattr(panel, 'autoresize'):
                panel.autoresize()

        self.tasks.resize(height - 4, width)
        self.tasks.move(2, 0)
        self.search_bar.resize(width)
        self.status_bar.resize(1, width)
        self.status_bar.move(height-2, 0)
        self.help_bar.resize(1, width)
        self.help_bar.move(height-1, 0)

    def apply_search(self):
        current = self.tasks.selected_item
        self.tasks.tasks = [(task, source) for task, source in self.all_tasks
                                           if self.search.match(task)]
        self.update_sorting()
        self.tasks.rebuild_items()
        self.tasks.jump_to(current)
        self.tasks.scroll()

    def update_sorting(self, apply=True):
        new_sort_order = self.conf.get(common.SETTING_GROUP_GENERAL,
                                       common.SETTING_SORT_ORDER)
        for part in self.search.text.split(' '):
            if part.lower().startswith('sort:'):
                new_sort_order = part.split(':', 1)[1]
                break
        if self.sort_order_txt != new_sort_order:
            self.sort_order_txt = new_sort_order
            self.sort_order = utils.build_sort_order(new_sort_order)
        if apply:
            self.tasks.tasks.sort(key=lambda t: utils.sort_fnc(t, self.sort_order))

    def update_tasks(self):
        current = self.tasks.selected_item
        self.all_tasks = []
        for source in self.sources:
            self.all_tasks += [(task, source) for task in source.tasks]

        self.apply_search()
        self.tasks.jump_to(current)
        return True

    def update_color_pairs(self):
        self.colors = {common.SETTING_COL_NORMAL: [Color(7, -1), Color(0, 7)],
                       common.SETTING_COL_COMPLETED: [Color(7, -1), Color(0, 7)],
                       common.SETTING_COL_INACTIVE: [Color(8), None],
                       common.SETTING_COL_ERROR: [Color(1), None],
                       common.SETTING_COL_PRI_A: [Color(1), None],
                       common.SETTING_COL_PRI_B: [Color(3), None],
                       common.SETTING_COL_PRI_C: [Color(6), None],
                       common.SETTING_COL_PRI_D: [Color(2), None],
                       common.SETTING_COL_CONTEXT: [Color(4), None],
                       common.SETTING_COL_PROJECT: [Color(2), None],
                       common.SETTING_COL_HELP_TEXT: [Color(11, 8), None],
                       common.SETTING_COL_HELP_KEY: [Color(2, 8), None],
                       common.SETTING_COL_OVERFLOW: [Color(11), None],
                       common.SETTING_COL_OVERDUE: [Color(7, 1), Color(1, 7)],
                       common.SETTING_COL_DUE_TODAY: [Color(4), None],
                       common.SETTING_COL_DUE_TOMORROW: [Color(6), None],
                       common.SETTING_COL_TRACKING: [Color(7, 2), Color(2, 7)],
                       common.SETTING_COL_FILE: [Color(10), None],
                       }
        if curses.has_colors() and self.use_colors:
            for colorname in self.conf[common.SETTING_GROUP_COLORS]:
                colpair = self.conf.color_pair(common.SETTING_GROUP_COLORS, colorname)

                if colpair is None:
                    continue
                fg, bg = colpair
                pairidx = 0

                if colorname.startswith('sel-'):
                    colorname = colorname[4:]
                    pairidx = 1

                if colorname not in self.colors:
                    logging.error(f"Invalid color name {colorname}.")
                    continue

                self.colors[colorname][pairidx] = Color(fg, bg)

            # register the color pairs
            for colorname in self.colors.keys():
                self.color(colorname, 0)
                self.color(colorname, 1)

            for key in self.conf[common.SETTING_GROUP_HIGHLIGHT]:
                hlcol = Color(*self.conf.color_pair(common.SETTING_GROUP_HIGHLIGHT, key))

                variant = 0
                if key.startswith('sel-'):
                    variant = 1
                    key = key[4:]

                if len(key.strip()) == 0:
                    continue

                if 'hl:' + key not in self.colors:
                    self.colors['hl:' + key] = [None, None]

                self.colors['hl:' + key][variant] = hlcol

                # and initialize the color
                self.color('hl:' + key, variant)

    def color(self, colorname, variant=0, default=None):
        """Return a color pair number for use with curses attributes
        variant can be 0/False (for normal) or 1/True (for selected text)
        If the color pair does not exist yet, it is registered, if possible."""

        if colorname is None:
            colorname = default or common.SETTING_COL_NORMAL

        if not self.use_colors or colorname not in self.colors:
            return 0

        if variant is True:
            variant = 1
        if variant is False:
            variant = 0
        if default is None:
            default = common.SETTING_COL_NORMAL

        colors = self.colors[colorname]
        if variant >= len(colors):
            logging.error(f"Programmer's error: color variant {variant} is invalid ({self.colors}).")
            raise ValueError(variant)

        color = colors[variant]
        if color is None:
            if variant > 0 and colors[0] is not None:
                color = colors[0].pair()
            else:
                color = self.colors[default][variant].pair()
        else:
            color = color.pair()

        default_variant = self.colors[default][variant]
        if default_variant is None and variant > 0:
            default_variant = self.colors[default][0]
        if default_variant is None:
            default_variant = self.colors[common.SETTING_COL_NORMAL][variant]

        if color[0] is None:
            color[0] = default_variant.fg
        if color[1] is None:
            color[1] = default_variant.bg
            if color[1] is None and self.colors[default][0] is not None:
                color[1] = self.colors[default][0].bg
            if color[1] is None:
                color[1] = self.colors[common.SETTING_COL_NORMAL][variant].bg
            # Added to avoid crash when setting colors with one value only:
            if color[1] is None:
                color[1] = -1

        color = (color[0], color[1])

        if color in self.color_cache:
            return curses.color_pair(self.color_cache[color])

        next_id = len(self.color_cache) + 1
        if next_id >= curses.COLOR_PAIRS:
            # sucks, we ran out of numbers
            logging.error(f"Too many color pairs defined. This terminal only supports {curses.COLOR_PAIRS} color pairs.")
            return 0

        try:
            curses.init_pair(next_id, *color)
            self.color_cache[color] = next_id
        except curses.error:
            self.color_cache[color] = 0
            return 0
        return next_id

    def load_key_configuration(self):
        logging.debug("Loading key configuration")
        for item in self.conf[common.SETTING_GROUP_KEYS]:
            fnc = self.conf.get(common.SETTING_GROUP_KEYS, item, None)
            if fnc not in self.functions and \
               fnc not in self.key_mapping.values():
                logging.warning(f"Cannot bind {item} to '{fnc}': no such function")
                continue

            logging.debug(f"Trying to map {item} to {fnc}")

            basekseq = parse_key_sequence(item)
            if basekseq is None:
                logging.error(f"Failed to parse key sequence {item}")
                continue

            if len(basekseq) > 1 and fnc not in self.functions:
                logging.warning(f"Cannot bind {item} to {fnc}: key sequences "
                                f"cannot be used for {fnc}")
                continue

            kseq = parse_base_key_sequence(basekseq)
            if kseq is None:
                continue

            self.key_mapping[tuple(kseq)] = fnc
            self.key_mapping_custom[tuple(kseq)] = fnc
            logging.debug(f"Assigned {kseq} to {fnc}")

        for item in self.conf[common.SETTING_GROUP_EDITORKEYS]:
            fnc = self.conf.get(common.SETTING_GROUP_EDITORKEYS, item, None)
            targets = []

            if fnc == 'nop':
                targets = [self.editor_key_mapping,
                           self.completion_key_mapping]
            elif fnc in self.editor_key_mapping.values():
                targets = [self.editor_key_mapping]
            elif fnc in self.completion_key_mapping.values():
                targets = [self.completion_key_mapping]
            else:
                logging.error(f"{fnc} is not a function of editor or "
                               "completion")
                continue

            basekseq = parse_key_sequence(item)
            if basekseq is None:
                logging.error(f"Failed to parse key sequence {item}")
                continue

            if len(basekseq) > 1:
                logging.warning(f"Cannot use key sequences for {fnc}")
            kseq = parse_base_key_sequence(basekseq)
            if kseq is None:
                continue
            for target in targets:
                target[kseq[0]] = fnc
                logging.debug(f"Assigned {kseq[0]} to {fnc}")

        # remove shortcuts that cover sequences
        # e.g. if there is a sequence 'pa' and the 'p' shortcut,
        # remove the 'p' shortcut
        sequences = [k for k in self.key_mapping.keys() if len(k) > 1]
        for kseq in sequences:
            for partial in range(len(kseq)-1):
                partial = kseq[:partial+1]
                if partial in self.key_mapping:
                    logging.debug(f"Removing ambiguous mapping {partial}")
                    del self.key_mapping[partial]

        to_exit = [k for k, fnc in self.key_mapping.items() if fnc == 'quit']
        if len(to_exit) == 0:
            logging.fatal("No key defined to exit pter.")
            raise RuntimeError("No key to exit")
        to_cancel = [k for k, fnc in self.key_mapping.items() if fnc == 'cancel']
        if len(to_cancel) == 0:
            logging.fatal("No key defined to cancel operations.")
            raise RuntimeError("No key to cancel")

    def known_contexts(self):
        """Returns a set of all contexts used in the tasks"""
        return set(sum([list(source.contexts) for source in self.sources],
                       start=[])) - {'@'}

    def known_projects(self):
        """Returns a set of all projects used in the tasks"""
        return set(sum([list(source.projects) for source in self.sources],
                       start=[])) - {'+'}

    def info(self, text):
        self.status_bar.set_text(text)
        self.status_bar.paint(True)

    def key_sequence_info(self, text):
        self.status_bar.set_text(text, expire=False)
        self.status_bar.paint(True)

    def error(self, text):
        self.status_bar.set_text(text, common.SETTING_COL_ERROR)
        self.status_bar.paint(True)

    def date_as_str(self, text, hint=''):
        if common.TF_ALL in self.human_friendly_dates or hint in self.human_friendly_dates:
            return utils.human_friendly_date(text)
        if not isinstance(text, str):
            return text.strftime(Task.DATE_FMT)
        return text

    def resolve_editor(self):
        candidates = [self.external_editor] \
                   + [os.getenv(name) for name in ['VISUAL', 'EDITOR']] \
                   + ['nano']
        for value in candidates:
            if value is None or len(value.strip()) == 0:
                continue
            value = shlex.split(value)
            editor = shutil.which(value[0])
            if editor is not None:
                return shlex.split(editor) + value[1:]

        return None

    def resolve_viewer(self):
        candidates = [self.external_viewer] \
                   + ['less', 'more']
        for value in candidates:
            if value is None or len(value.strip()) == 0:
                continue
            value = shlex.split(value)
            viewer = shutil.which(value[0])
            if viewer is not None:
                return shlex.split(viewer) + value[1:]

        return None

    def modify_task(self, taskline, fnc):
        """Try to minimize the chance that this task was changed in the background
        and apply fnc to it."""
        assert isinstance(taskline, TaskLine)
        task = utils.ensure_up_to_date(taskline.task)
        if task is not None:
            prev_version = str(task)
            fnc(task)
            if str(task) == prev_version:
                return False, task
            taskline.source.save(safe=self.safe_save)
            taskline.source.update_contexts_and_projects()
            self.search.update_sources(self.sources)
            self.update_tasks()
            self.tasks.jump_to(task)
            return True, task
        self.update_tasks()
        self.error(tr("Failed to update: task was modified in the background"))
        return False, None

    def do_quit(self):
        self.quit = True

    def do_reload_tasks(self):
        self.update_tasks()

    def do_start_search(self):
        self.focus.append(self.search_bar)
        self.search_bar.previous_text = self.search_bar.text
        self.search_bar.cursor = len(self.search_bar.text)
        self.focus[-1].paint()

    def do_load_template(self):
        templates = [AutoTemplate(name, template=template)
                     for name, template in utils.parse_templates().items()]
        templates += self.auto_templates
        if len(templates) == 0:
            self.info(tr("There are no templates"))
            return

        none = tr("None")
        names = [none] + list(sorted(templ.name
                                     for templ in templates))
        self.focus.append(Selector(self.tasks,
                                   names,
                                   lambda t: self.set_template(templates, none, t),
                                   title='Load template',
                                   numbered=True))
        self.paint(True)

    def set_template(self, templates, none, template):
        if template == none:
            self.selected_template = None
        else:
            self.selected_template = [t.template for t in templates
                                      if t.name == template][0]

    def do_save_template(self):
        if self.tasks.selected_item is None:
            self.error(tr("No task selected to create a template from"))
            return

        self.focus.append(UserInput(self.tasks,
                                    self._do_save_template,
                                    lambda: self.show_cursor(False),
                                    "Save template"))
        self.paint(True)

    def _do_save_template(self, name):
        self.show_cursor(False)

        if len(name.strip()) == 0:
            self.error(tr("Invalid template name"))
            return

        task = self.tasks.selected_item
        if task is None:
            self.error(tr("No task selected to create a template from"))
            return

        # create a copy of the selected task and remove creation date,
        # completion date and completion marker
        task = Task(str(task.task))
        task.is_completed = False
        task.creation_date = None
        task.completion_date = None

        templates = utils.parse_templates()
        templates[name] = str(task)
        utils.save_templates(templates)

    def do_load_search(self):
        searches = utils.parse_searches()
        if len(searches) == 0:
            self.info(tr("There are no saved searches"))
            return

        names = [name for name in sorted(searches.keys())]
        self.focus.append(Selector(self.tasks,
                                   names,
                                   lambda s: self.set_named_search(searches, s),
                                   title='Load search',
                                   numbered=True))
        self.paint(True)

    def set_named_search(self, searches, search):
        text = searches.get(search, None)
        if text is None:
            return
        self.set_search(text)

    def set_search(self, text):
        self.search.text = text
        self.search_bar.text = text
        self.search_bar.scroll()
        self.search.parse()
        self.apply_search()
        self.search_bar.paint(True)
        self.tasks.paint(True)

    def do_clear_search(self):
        self.set_search('')

    def do_save_search(self):
        self.focus.append(UserInput(self.tasks,
                                    self._do_save_search,
                                    lambda: self.show_cursor(False),
                                    tr("Save search")))
        self.paint(True)

    def _do_save_search(self, name):
        self.show_cursor(False)

        if len(name.strip()) == 0:
            self.error(tr("Invalid saved search name"))
            return

        searches = utils.parse_searches()
        searches[name] = self.search.text
        utils.save_searches(searches)

    def do_edit_task(self):
        if self.tasks.selected_item is None:
            self.error(tr("No task selected"))
            return
        self.focus.append(TaskEditor(self.tasks, self.tasks.selected_item))

        if self.reset_terminal:
            with ShellContext(self.screen, False):
                hard_reset_terminal()

        self.paint()

    def do_edit_task_external(self):
        task = self.tasks.selected_item
        if task is None:
            self.error(tr("No task selected"))
            return

        editor = self.resolve_editor()
        if editor is None:
            self.error(tr("Could not determine your external text editor"))
            return

        with tempfile.NamedTemporaryFile("w+t", encoding="utf-8", suffix='.txt') as fh:
            fh.write(str(task.task))
            fh.flush()
            with ShellContext(self.screen, True):
                subprocess.run(editor + [fh.name])

            fh.flush()
            fh.seek(0)
            tasktext = fh.read()

        tasktext = utils.dehumanize_dates(utils.auto_task_id(self.sources, tasktext),
                                          businessdays=self.business_days)
        if tasktext != str(task.task):
            _, task = self.modify_task(task, lambda t: t.parse(tasktext))
            self.run_hook(self.on_change, task)

        self.paint(True)

    def do_edit_file_external(self):
        taskline = self.tasks.selected_item
        if taskline is None:
            self.error(tr("No task selected"))
            return

        editor = self.resolve_editor()
        if editor is None:
            self.error(tr("Could not determine your external text editor"))
            return

        todotxt = taskline.source.source
        tasks = todotxt.tasks[:]
        with tempfile.NamedTemporaryFile("w+b", suffix='.txt') as fh:
            todotxt.write_to_stream(fh, todotxt.linesep)
            fh.flush()
            with ShellContext(self.screen, True):
                subprocess.run(editor + [fh.name])

            fh.flush()
            fh.seek(0)
            parser = TodoTxtParser()
            tasks = parser.parse_stream(fh)

        todotxt.tasks = []
        for task in tasks:
            # one by one to make sure `auto_task_id` actually works
            task = Task(utils.dehumanize_dates(utils.auto_task_id(self.sources, str(task)),
                                               businessdays=self.business_days))
            todotxt.add(task)
            taskline.source.update_from_task(task)
        taskline.source.save(safe=self.safe_save)
        taskline.source.parse()
        self.search.update_sources(self.sources)
        self.update_tasks()
        self.paint(True)

    def do_create_task(self):
        self.focus.append(TaskCreator(self.tasks))

        if self.reset_terminal:
            with ShellContext(self.screen, False):
                hard_reset_terminal()

        self.paint()

    def do_jump_to(self, init=''):
        if len(self.focus) == 0:
            return
        if not hasattr(self.focus[-1], 'jump_to'):
            logging.debug(f"{self.focus[-1]} does not have a 'jump_to' function")
            return

        self.focus.append(JumpToIndexReader(self, init))
        self.paint(True)

    def do_open_url(self):
        task = self.tasks.selected_item
        if task is None:
            self.info(tr("No task selected"))
            return

        task = task.task

        urls = []
        if task.description is not None:
            for match in common.URL_RE.finditer(task.description):
                if match.group(1) not in self.protos:
                    continue
                urls.append(match.group(0))

        urls = [url[1:-1] if url.startswith('<') and url.endswith('>') else url
                for url in urls if len(url) > 0]

        if len(urls) == 0:
            self.info(tr("No URLs found"))
            return

        if len(urls) > 1:
            self.focus.append(Selector(self.tasks,
                                       urls,
                                       lambda u: webbrowser.open(u),
                                       title="Open URL",
                                       numbered=True))
            self.paint(True)
        else:
            webbrowser.open(urls[0])

    def do_toggle_tracking(self):
        if self.tasks.selected_item is None:
            return

        if self.tracker is not None:
            if self.run_hook(self.tracker):
                self.info(tr("Tracker started"))
            self.run_hook(self.on_tracking)
            return

        success, task = self.modify_task(self.tasks.selected_item,
                                         lambda t: utils.toggle_tracking(t))
        if success:
            if 'tracking' in task.attributes:
                self.run_hook(self.on_tracking, task)
            self.tasks.jump_to(task)
            self.tasks.paint_item(self.tasks.selected_item)

    def defer_hook(self, hook, task=None):
        self.deferred_hooks.append((hook, task))

    def run_hook(self, hook, task=None):
        if hook is None:
            return False

        if task is None:
            task = self.tasks.selected_item.task

        success = False
        result = hook.run(task)
        logging.debug(f"Called external program with {result.args}")
        if result.returncode == 0:
            success = True
        else:
            details = result.stderr
            if details is None:
                details = ''
            else:
                details = str(result.stderr, 'utf-8').replace("\n", " ")
            logging.warning(f"External call '{result.args}' returned {result.returncode}: {details}")
            self.error(tr("External program returned {}: {}")
                         .format(result.returncode, details))
        self.paint(False)
        return success

    def resolve_hook(self, name):
        hook = self.conf.get(common.SETTING_GROUP_HOOKS, name, None)
        if hook is None:
            return None
        hook = Hook(self, hook)
        if hook.is_ok():
            return hook
        return None

    def do_toggle_done(self):
        if self.tasks.selected_item is None:
            return

        should_mark = self.done_is in [common.DONE_OPTION_MARK,
                                       common.DONE_OPTION_MARK_MOVE]
        should_move = self.done_is in [common.DONE_OPTION_MOVE,
                                       common.DONE_OPTION_MARK_MOVE]

        taskline = self.tasks.selected_item
        taskfile = taskline.source
        task = utils.ensure_up_to_date(taskline.task)
        if task is None:
            return

        if should_mark:
            utils.toggle_done(task,
                              self.clear_contexts,
                              self.reuse_recurring,
                              self.safe_save)

        if should_move:
            if self.done_file == taskfile.filename:
                # this task was in the done-file, but toggling set it to un-done
                # so it must be moved back into the not-done-file
                candidates = [source
                              for source in self.sources
                              if source.filename != self.done_file]
                if len(candidates) == 0:
                    self.error(tr("No other task file open. Cannot move the task."))
                    return
                targetfile = candidates[0]
            else:
                # first check: is the done file open, too?
                candidates = [source
                              for source in self.sources
                              if source.filename == self.done_file]
                if len(candidates) == 1:
                    targetfile = candidates[0]
                else:
                    # ensure the done file exists
                    targetfile = self.done_file
                    try:
                        with open(targetfile, "a+b"):
                            logging.debug(f"Using done file {targetfile}")
                    except OSError as exc:
                        self.error(tr("Failed to open done file"))
                        logging.error(f"Could not open done file '{targetfile}' "
                                      f"for writing: {exc}")
                        return
                    # open the targetfile as a source
                    targetfile = TodoTxt(targetfile)
                    try:
                        targetfile.parse()
                    except OSError as exc:
                        self.error(tr("Failed to read done file"))
                        logging.error(f"Failed to read done file {targetfile}: {exc}")

            if targetfile.filename != taskfile.filename:
                # move the task from its current file into the targetfile
                # 1. append to target and save
                targetfile.tasks.append(task)
                task.todotxt = targetfile
                try:
                    targetfile.save(safe=self.safe_save)
                except OSError as exc:
                    self.error(tr("Failed to save to done file"))
                    logging.error(f"Failed to write to {targetfile.filename}")
                    return

                # 2. remove from source
                if task in taskfile.tasks:
                    taskfile.tasks.remove(task)

                if isinstance(targetfile, Source):
                    targetfile.update_contexts_and_projects()

        taskfile.save(safe=self.safe_save)
        taskfile.update_contexts_and_projects()
        self.search.update_sources(self.sources)
        self.update_tasks()
        self.tasks.jump_to(task)

        self.run_hook(self.on_change, task)
        if task.is_completed:
            self.run_hook(self.on_done, task)
        self.tasks.paint(True)

    def do_toggle_hidden(self):
        if self.tasks.selected_item is None:
            return
        success, task = self.modify_task(self.tasks.selected_item,
                                         lambda t: utils.toggle_hidden(t))
        if success:
            self.run_hook(self.on_change, task)
            self.tasks.paint(True)

    def do_prio_up(self):
        if self.tasks.selected_item is None:
            return
        success, task = self.modify_task(self.tasks.selected_item,
                                         utils.increase_priority)
        if success:
            self.run_hook(self.on_change, task)
            self.tasks.paint(True)

    def do_prio_down(self):
        if self.tasks.selected_item is None:
            return
        success, task = self.modify_task(self.tasks.selected_item,
                                         utils.decrease_priority)
        if success:
            self.run_hook(self.on_change, task)
            self.tasks.paint(True)

    def do_set_prio(self, prio):
        if self.tasks.selected_item is None:
            return
        success, task = self.modify_task(self.tasks.selected_item,
                                         lambda t: utils.set_priority(t, prio))
        if success:
            self.run_hook(self.on_change, task)
            self.tasks.paint(True)

    def do_show_help(self):
        self.focus.append(HelpScreen(self))
        height, width = self.size()
        self.focus[-1].resize(height-2, width)
        self.focus[-1].move(0, 0)

        if self.reset_terminal:
            with ShellContext(self.screen, False):
                hard_reset_terminal()

        self.paint(True)

    def do_delegate(self):
        task = self.tasks.selected_item
        if task is None:
            return

        if len(self.delegation_marker) == 0:
            self.error(tr("No delegation marker defined"))
            return

        if self.delegation_marker in str(task.task).split(' '):
            self.do_delegation_action(task.task)
            return

        success, task = self.modify_task(task,
                                         lambda t: utils.delegate_task(t, self.delegation_marker))
        if success:
            self.do_delegation_action(task)
            self.run_hook(self.on_change, task)
            self.tasks.jump_to(task)
            self.tasks.paint_item(self.tasks.selected_item)

    def do_delegation_action(self, task):
        utils.execute_delegate_action(task,
                                      self.delegate_to,
                                      self.delegation_marker,
                                      self.delegation_action)

    def do_refresh_screen(self):
        with ShellContext(self.screen, True):
            logging.debug("Resetting terminal manually")
            hard_reset_terminal()
        self.paint(True)

    def do_show_related(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        others = set(task.attributes.get('after', []) + \
                     task.attributes.get('ref', []))
        if len(others) == 0:
            self.error(tr("No related tasks declared (e.g. 'after:' or 'ref:')"))
            return

        show_self = self.conf.get(common.SETTING_GROUP_GENERAL, common.SETTING_RELATED_SHOW_SELF).lower()

        if show_self in self.conf.BOOL_TRUE + ['force']:
            if 'id' not in task.attributes and show_self == 'force':
                task.parse(str(task) + ' id:' + utils.new_task_id(self.sources))
            if 'id' in task.attributes:
                others.add(task.attributes['id'][0])

        self.set_search(' '.join(['id:' + other for other in sorted(others)]))

    def do_search_context(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        contexts = [context for context in task.contexts
                    if context not in self.search.contexts]

        if len(contexts) == 0:
            return

        contexts.sort()
        if len(contexts) == 1:
            self.add_to_search('@'+contexts[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       contexts,
                                       lambda c: self.add_to_search('@'+c),
                                       title="Select context",
                                       numbered=True))
            self.paint(True)

    def do_select_project(self):
        projects = self.known_projects()
        if len(projects) == 0:
            return

        projects = [p[1:] for p in sorted(projects) if len(p) > 1]

        if len(projects) == 1:
            self.set_search('+'+projects[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       projects,
                                       lambda p: self.set_search('+'+p),
                                       title="Select project",
                                       numbered=True))
            self.paint(True)

    def do_select_context(self):
        contexts = self.known_contexts()

        if len(contexts) == 0:
            return

        contexts = [c[1:] for c in sorted(contexts) if len(c) > 1]
        if len(contexts) == 1:
            self.set_search('@'+contexts[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       contexts,
                                       lambda c: self.set_search('@'+c),
                                       title="Select context",
                                       numbered=True))
            self.paint(True)

    def do_delete(self):
        if self.delete_is == common.DELETE_OPTION_DISABLED:
            return

        taskline = self.tasks.selected_item
        if taskline is None:
            return
        task = taskline.task

        def _do_delete(t):
            if t in t.todotxt.tasks:
                t.todotxt.tasks.remove(t)
            t.parse(str(t) + '-')

        can_perm_delete = self.last_perm_delete + self.perm_delete_timeout < datetime.datetime.now()

        if self.delete_is == common.DELETE_OPTION_PERMANENT and can_perm_delete:
            success, _ = self.modify_task(taskline, _do_delete)
            if success:
                self.last_perm_delete = datetime.datetime.now()
                self.info(tr("Task deleted"))
                self.tasks.paint(True)

            self.run_hook(self.on_delete, task)

        elif self.delete_is == common.DELETE_OPTION_TRASH:
            # first save the task in the trash
            trashfile = TodoTxt(self.trash_file)
            try:
                trashfile.parse()
            except OSError as exc:
                logging.error(f"Failed to open {trashfile.filename}: {exc}")
                self.error(tr("Failed to open trash file"))
                return
            trashfile.tasks.append(taskline.task)
            try:
                trashfile.save()
            except OSError as exc:
                logging.error(f"Failed to save to {trashfile.filename}: {exc}")
                self.error(tr("Failed to save to trash file"))
                return

            # attempt to delete the task
            success, _ = self.modify_task(taskline, _do_delete)
            if success:
                self.info(tr("Task moved to trash"))
                self.tasks.paint(True)
            else:
                # deletion was not okay, remove the task again from the trash
                trashfile.tasks.pop()
                trashfile.save()

            self.run_hook(self.on_delete, task)

        else:
            self.error(tr("Invalid value for configuration option 'delete-is'"))

    def do_archive(self):
        if self.archive_is == common.ARCHIVE_OPTION_DISABLED:
            return

        taskline = self.tasks.selected_item
        if taskline is None:
            return

        if self.archive_is == common.ARCHIVE_OPTION_CENTRALISED:
            archivefile = self.archive_file
        elif self.archive_is == common.ARCHIVE_OPTION_RELATIVE:
            archivefile = taskline.source.filename.parent / "archive.txt"
        else:
            self.error(tr("Invalid value for configuration option 'archive-is'"))
            return

        if archivefile == taskline.source.filename:
            self.error(tr("This task has already been archived"))
            return

        try:
            with open(archivefile, 'a+b'):
                logging.debug(f"Using archive file {archivefile}")
        except OSError as exc:
            self.error(tr("Failed to open archive file"))
            logging.error(f"Could not open archive file '{archivefile}' "
                          f"for writing: {exc}")
            return

        archivefile = TodoTxt(archivefile)
        try:
            archivefile.parse()
        except OSError as exc:
            self.error(tr("Failed to read archive file"))
            logging.error(f"Failed to read archive file {archivefile.filename}: {exc}")
            return
        archived = Task(str(taskline.task), todotxt=archivefile)
        if len(self.archive_origin_marker) > 0:
            value = taskline.source.filename
            if self.archive_origin_is == common.ARCHIVE_ORIGIN_NAME:
                value = value.name
            elif self.archive_origin_is == common.ARCHIVE_ORIGIN_STEM:
                value = value.stem
            archived.add_attribute(self.archive_origin_marker,
                                   str(value))
        archivefile.tasks.append(archived)
        try:
            archivefile.save()
        except OSError as exc:
            self.error(tr("Failed to save to archive file"))
            logging.error(f"Failed to write to archive file {archivefile.filename}: {exc}")
            return

        def _do_delete(t):
            if t in t.todotxt.tasks:
                t.todotxt.tasks.remove(t)
            t.parse(str(t) + '-')

        success, task = self.modify_task(taskline, _do_delete)
        if success:
            self.info(tr("Task moved to archive"))
            self.run_hook(self.on_archive, task)
            self.tasks.paint(True)
        else:
            # task deletion failed, don't duplicate the task in the archive
            archivefile.tasks.pop()
            archivefile.save()

    def do_duplicate_task(self):
        task = self.tasks.selected_item
        if task is None:
            return
        source = task.task.todotxt
        task = Task(str(task.task))
        to_replace = [value for key, value in task.attributes.items()
                      if key == 'id']
        for value in to_replace:
            task.replace_attribute('id', value, 'auto')
        task = Task(utils.auto_task_id(self.sources, str(task)),
                    todotxt=source)
        source.tasks.append(task)
        task.linenr = len(source.tasks)
        source.save(safe=self.safe_save)
        source.update_from_task(task)
        self.update_tasks()
        self.tasks.jump_to(task)
        self.defer_hook(self.on_new, task)
        self.tasks.paint(False)

    def add_to_search(self, text):
        if len(self.search.text) > 0:
            text = ' ' + text
        self.set_search(self.search.text + text)

    def do_search_project(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        projects = [project for project in task.projects
                    if project not in self.search.projects]

        if len(projects) == 0:
            return

        projects.sort()
        if len(projects) == 1:
            self.add_to_search('+'+projects[0])
        else:
            self.focus.append(Selector(self.tasks,
                                       projects,
                                       lambda p: self.add_to_search('+'+p),
                                       title="Select project",
                                       numbered=True))
            self.paint(True)

    def do_increase_due(self):
        task = self.tasks.selected_item
        if task is None:
            return
        if self.due_delta is None:
            return

        due = utils.task_parse_due(task.task)
        if due is None:
            newdue = datetime.datetime.today() + self.due_delta
        else:
            newdue = due + self.due_delta

        if self.skip_weekend:
            weekday = newdue.isoweekday()
            if weekday > 5:
                newdue += datetime.timedelta(days=8-weekday)

        if due is None:
            newdue = newdue.strftime(Task.DATE_FMT)
            success, task = self.modify_task(task,
                                             lambda t: t.add_attribute('due', newdue))
        else:
            success, task = self.modify_task(task,
                                             lambda t: utils.task_change_due(t, due, newdue))
        if success:
            self.tasks.paint()

    def do_decrease_due(self):
        task = self.tasks.selected_item
        if task is None:
            return
        if self.due_delta is None:
            return

        due = utils.task_parse_due(task.task)
        if due is None:
            newdue = datetime.datetime.today()
        else:
            newdue = due - self.due_delta

        if self.skip_weekend:
            weekday = newdue.isoweekday()
            if weekday > 5:
                newdue -= datetime.timedelta(days=weekday-5)

        if due is None:
            newdue = newdue.strftime(Task.DATE_FMT)
            success, task = self.modify_task(task,
                                             lambda t: t.add_attribute('due', newdue))
        else:
            success, task = self.modify_task(task,
                                             lambda t: utils.task_change_due(t, due, newdue))
        if success:
            self.tasks.paint()

    def do_clear_due(self):
        task = self.tasks.selected_item
        if task is None:
            return

        due = utils.task_parse_due(task.task)
        if due is None:
            return

        success, task = self.modify_task(task,
                                         lambda t: t.remove_attribute('due'))
        if success:
            self.tasks.paint()

    def do_edit_note(self):
        """Edit the note of the selected task, create note if it doesn't exist"""
        if len(self.notes) == 0:
            self.error(tr("No 'notes' directories defined"))
            return

        editor = self.resolve_editor()
        if editor is None:
            self.error(tr("Could not determine your external text editor"))
            return

        task = self.tasks.selected_item
        if task is None:
            return

        filename = task.task.attributes.get('note', [])

        if len(filename) == 0:
            if self.note_naming == common.NOTE_NAMING_CANCEL:
                self.error(tr("No 'note:' tag"))
                return

            if self.note_naming == common.NOTE_NAMING_USER:
                self.focus.append(UserInput(self.tasks,
                                            lambda n: self._append_note_tag(task, n),
                                            lambda: self.show_cursor(False),
                                            tr("Note filename")))
                self.paint(True)
                return

            assert self.note_naming == common.NOTE_NAMING_AUTO
            # does the task have a task id?
            taskid = task.task.attributes.get('id', [])
            if len(taskid) == 0:
                # add a task id
                newtask = utils.auto_task_id(self.sources,
                                             str(task.task) + " id:#")
                success, newtask = self.modify_task(task,
                                                    lambda t: t.parse(newtask))
                if not success:
                    if newtask is not None:
                        self.error(tr("Failed to add task ID"))
                    return
                task = self.tasks.selected_item
                taskid = task.task.attributes.get('id')

            # we use the taskid as the note's filename
            taskid = taskid[0]

            # make the new filename unique, so we don't overwrite existing files
            counter = None
            while True:
                notefilename = taskid
                if counter is not None:
                    notefilename += '_' + str(counter)
                notepath = self.resolve_note(notefilename)
                if notepath.exists():
                    if counter is None:
                        counter = 1
                    else:
                        counter += 1
                    continue
                filename = [notepath.name]
                break

            # add the note: tag
            newtask = str(task.task) + ' note:' + notefilename
            success, _ = self.modify_task(task, lambda t: t.parse(newtask))
            if not success:
                return
            self.paint(True)

        filename = self.resolve_note(filename[0])

        logging.debug(f"Edit note: {filename}")
        with ShellContext(self.screen, True):
            subprocess.run(editor + [str(filename)])
        self.paint(True)

    def do_view_note(self):
        """View an existing note for the selected task, bail out if note doesn't exist"""
        if len(self.notes) == 0:
            self.error(tr("No 'notes' directories defined"))
            return

        viewer = self.resolve_viewer()
        if viewer is None:
            self.error(tr("Could not determine your external text viewer"))
            return

        task = self.tasks.selected_item
        if task is None:
            return

        filename = task.task.attributes.get('note', [])

        if len(filename) == 0:
            self.error(tr("No 'note:' tag"))
            return

        filename = self.resolve_note(filename[0])

        if not filename.is_file():
            self.error(tr("Note file does not exist, create it first"))
            return

        logging.debug(f"View note: {filename}")
        with ShellContext(self.screen, True):
            try:
                subprocess.run(viewer + [str(filename)], check=False)
            except KeyboardInterrupt:
                pass
        self.paint(True)

    def do_copy_to_clipboard(self):
        task = self.tasks.selected_item
        if task is None:
            return

        task = task.task
        clipboards = [["xsel", "-b"],
                      ["xclip", "-selection", "clipboard"],
                      ["wl-copy"]]

        if os.getenv('TMUX') is not None:
            clipboard.append(["tmux", "loadb", "-w", "-"])

        copied_to_any = False
        attempts = 0
        for clipboard in clipboards:
            cbpath = shutil.which(clipboard[0])
            if cbpath is None:
                continue
            attempts += 1
            with subprocess.Popen([cbpath] + clipboard[1:],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL,
                                  encoding='utf-8') as process:
                process.stdin.write(str(task))
                process.stdin.close()
                process.wait()
                if process.returncode == 0:
                    logging.info(f"Copied to clipboard using {cbpath}")
                    copied_to_any = True

                logging.debug(f"{cbpath} ended with {process.returncode}")
        if copied_to_any:
            self.info(tr("Copied task to clipboard"))
        elif attempts == 0:
            self.error(tr("I don't know how to copy to clipboard"))
        else:
            self.error(tr("Could not copy to clipboard"))

    def _append_note_tag(self, task, name):
        name = name.replace(' ', '_')
        tasktext = str(task.task) + ' note:' + name
        success, _ = self.modify_task(task,
                                      lambda t: t.parse(tasktext))
        if success:
            self.do_edit_note()

    def resolve_note(self, filename):
        """Returns a path to a note file
        The file may or may not exist"""
        assert len(self.notes) > 0

        # clean up the filename
        while '..' in filename:
            filename = filename.replace('..', '')
        while '//' in filename:
            filename = filename.replace('//', '/')
        if filename.startswith('/'):
            filename = filename[1:]

        # add the suffix, if required
        filename = Path(filename)
        if len(filename.suffix) == 0:
            filename = Path(str(filename) + self.note_suffix)

        # see if the note exists already
        location = None
        for path in self.notes:
            if (path / filename).is_file():
                location = path / filename
                break

        # use the default location if the note doesn't exist yet
        if location is None:
            location = self.notes[0] / filename
        filename = location.resolve()

        return filename


def parse_key_sequence(text):
    sequence = []

    pos = 0
    while pos < len(text):
        token = text[pos]
        if token == '<':
            other = text.find('>', pos)
            if other < 0:
                return None
            sequence.append(text[pos:other+1])
            pos = other
        elif token == '^' and pos < len(text)-1:
            pos += 1
            if text[pos] == '^':
                sequence.append('^')
            else:
                sequence.append('^' + text[pos])
        else:
            sequence.append(token)

        pos += 1

    return tuple(sequence)


def add_title(panel, title, attr=0):
    assert isinstance(panel, Panel)
    _, w = panel.dim
    if (panel.border & Panel.BORDER_TOP) == 0:
        # no top border, no title
        return
    if (panel.border & Panel.BORDER_RIGHT) > 0:
        w -= 1
    if (panel.border & Panel.BORDER_LEFT) > 0:
        w -= 1

    w -= 2  # the indicators left and right
    label = title[:min(w, len(title))]
    if label != title:
        label = label[:-1] + '…'

    panel.win.addstr(0, 1, title_frame(label), attr)


def title_frame(label):
    return TITLE_FRAME[0] + label + TITLE_FRAME[1]


def hard_reset_terminal():
    sys.stdout.write("\x1bc")
    sys.stdout.flush()


def translate_config_key(keyname):
    keyname_mapping = {'<colon>': ':',
                       '<equal>': '=',
                       '<semicolon>': ';',
                       '<hash>': '#',
                       '<lbrack>': '[',
                       '<rbrack>': ']',
                       }
    return keyname_mapping.get(keyname.lower(), keyname)


def parse_base_key_sequence(basekseq):
    result = []
    for key in basekseq:
        key = translate_config_key(key)
        if len(key) == 1:
            result.append(key)
        elif len(key) == 2 and key[0] == '^':
            result.append(key.upper())
        elif key.startswith('<') and key.endswith('>'):
            result.append(key)
        elif key in Key.SPECIAL:
            result.append(key)
        else:
            logging.error(f"Invalid key name '{key}' in configuration")
            return None
    return result


def run_cursesui(args, config):
    logging.basicConfig(format="[%(levelname)s] %(message)s", filename=args.log_file)
    logging.getLogger().setLevel(args.log_level.upper())

    success = 0
    sources = utils.open_sources(args, config)

    if args.list_keys:
        window = CursesApplication([], config, "")
        lines = []
        for description, keys, fnc in compile_key_listing(window):
            if keys == '':
                continue
            lines.append("\t".join([description, fnc, ''.join(keys)]))
        print("\n".join(lines), end="")

    elif len(sources) == 0:
        success = -1
        print(tr("To start pter you must provide at least one todo.txt file. "
                 "See --help for more information."),
              file=sys.stderr)
    else:
        search = Searcher('', common.SearchCaseBehaviour.INSENSITIVE)
        search.update_sources(sources)

        window = CursesApplication(sources, config, args.search)

        exception = None

        try:
            window.run()
        except Exception as exc:
            callstack = ''.join(traceback.format_tb(exc.__traceback__))
            logging.fatal("Pter crashed with exception: %s\n%s",
                          exc, callstack)
            exception = exc
            success = -3

        if args.log_level.lower() == 'debug' and exception is not None:
            raise exception

    return success

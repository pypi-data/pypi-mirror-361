"""Common constants for both ncurses and qiui"""
import pathlib
import os
import re

try:
    from xdg import BaseDirectory
except ImportError:
    BaseDirectory = None


PROGRAMNAME = 'pter'
QTPROGRAMNAME = 'qpter'
HERE = pathlib.Path(os.path.abspath(__file__)).parent
HOME = pathlib.Path.home()
CONFIGDIR = HOME / ".config" / PROGRAMNAME
CONFIGFILE = HOME / ".config" / PROGRAMNAME / (PROGRAMNAME + ".conf")
CACHEDIR = HOME / ".cache" / PROGRAMNAME
CACHEFILE = CACHEDIR / (PROGRAMNAME + ".settings")

if BaseDirectory is not None:
    CONFIGDIR = pathlib.Path(BaseDirectory.save_config_path(PROGRAMNAME) or CONFIGDIR)
    CONFIGFILE = CONFIGDIR / (PROGRAMNAME + ".conf")
    CACHEDIR = pathlib.Path(BaseDirectory.save_cache_path(PROGRAMNAME) or CACHEDIR)
    CACHEFILE = CACHEDIR / (PROGRAMNAME + ".settings")

SEARCHES_FILE = CONFIGDIR / "searches.txt"
TEMPLATES_FILE = CONFIGDIR / "templates.txt"
AUTO_TEMPLATES_FILE = CONFIGDIR / "auto_templates.conf"
LOGFILE = CACHEDIR / (PROGRAMNAME + ".log")
DEFAULT_TRASHFILE = CONFIGDIR / "trash.txt"
DEFAULT_ARCHIVE = CONFIGDIR / "archive.txt"
DEFAULT_DONE = CONFIGDIR / "done.txt"

URL_RE = re.compile(r'([A-Za-z][A-Za-z0-9+\-.]*)://([^ ]+)')

DEFAULT_TASK_FORMAT = '{selection: >} {nr: >} {done} {tracking }{due }{(pri) }{description}'
ATTR_TRACKING = 'tracking'
ATTR_T = 't'
ATTR_DUE = 'due'
ATTR_PRI = 'pri'
ATTR_ID = 'id'

DELEGATE_ACTION_NONE = 'none'
DELEGATE_ACTION_MAIL = 'mail-to'
DELEGATE_ACTIONS = (DELEGATE_ACTION_NONE, DELEGATE_ACTION_MAIL)

DELETE_OPTION_DISABLED = 'disabled'
DELETE_OPTION_TRASH = 'trash'
DELETE_OPTION_PERMANENT = 'permanent'
DELETE_OPTIONS = (DELETE_OPTION_DISABLED, DELETE_OPTION_TRASH, DELETE_OPTION_PERMANENT)

ARCHIVE_OPTION_RELATIVE = 'relative'
ARCHIVE_OPTION_CENTRALISED = 'centralised'
ARCHIVE_OPTION_DISABLED = 'disabled'
ARCHIVE_OPTIONS = (ARCHIVE_OPTION_RELATIVE,
                   ARCHIVE_OPTION_CENTRALISED,
                   ARCHIVE_OPTION_DISABLED)
ARCHIVE_ORIGIN_FULLPATH = 'full-path'
ARCHIVE_ORIGIN_NAME = 'name'
ARCHIVE_ORIGIN_STEM = 'stem'
ARCHIVE_ORIGIN_OPTIONS = {ARCHIVE_ORIGIN_FULLPATH,
                          ARCHIVE_ORIGIN_NAME,
                          ARCHIVE_ORIGIN_STEM,}

DONE_OPTION_MARK = 'mark'
DONE_OPTION_MOVE = 'move'
DONE_OPTION_MARK_MOVE = 'mark-move'
DONE_OPTIONS = (DONE_OPTION_MARK,
                DONE_OPTION_MOVE,
                DONE_OPTION_MARK_MOVE)

NOTE_NAMING_AUTO = 'auto'
NOTE_NAMING_USER = 'user-input'
NOTE_NAMING_CANCEL = 'cancel'
NOTE_NAMING_OPTIONS = (NOTE_NAMING_AUTO,
                       NOTE_NAMING_USER,
                       NOTE_NAMING_CANCEL)

DEFAULT_SORT_ORDER = 'completed,due_in,priority,linenr'
DEFAULT_INFO_TIMEOUT = 5
DEFAULT_NOTE_SUFFIX = '.txt'
DEFAULT_HELP_ACTIONS = "\n".join([
            "show-help",
            "quit",
            "edit-task",
            "create-task",
            "search",
            "load-search",
            "save-search",
            "toggle-done",
            "jump-to",
            "next-item",
            "prev-item",
            "edit-note",
            ])

DEFAULT_BUSINESS_DAYS = '1,2,3,4,5'

DEFAULT_WORD_BOUNDARIES = '@ +:-'

DEFAULT_DUE_DELTA = '1d'
DEFAULT_SKIP_WEEKEND = 'no'

DEFAULT_REDUCE_DISTRACTION = 'no'
DEFAULT_ESC_TIMEOUT = 200


SETTING_GROUP_GENERAL = 'General'
SETTING_GROUP_SYMBOLS = 'Symbols'
SETTING_GROUP_COLORS = 'Colors'
SETTING_GROUP_HIGHLIGHT = 'Highlight'
SETTING_GROUP_KEYS = 'Keys'
SETTING_GROUP_EDITORKEYS = 'Editor:Keys'
SETTING_GROUP_GUICOLORS = 'GUI:Colors'
SETTING_GROUP_GUIHIGHLIGHT = 'GUI:Highlight'
SETTING_GROUP_GUIKEYS = 'GUI:Keys'
SETTING_GROUP_GUI = 'GUI'
SETTING_GROUP_INCLUDE = 'Include'
SETTING_GROUP_HOOKS = 'Hooks'
SETTING_BUSINESS_DAYS = 'business-days'
SETTING_HUMAN_DATES = 'human-friendly-dates'
SETTING_USE_COMPLETION = 'use-completion'
SETTING_PROTOCOLS = 'protocols'
SETTING_DELEG_MARKER = 'delegation-marker'
SETTING_DELEG_ACTION = 'delegation-action'
SETTING_DELEG_TO = 'delegation-to'
SETTING_DEFAULT_THRESHOLD = 'default-threshold'
SETTING_EXT_EDITOR = 'editor'
SETTING_EXT_VIEWER = 'viewer'
SETTING_TAB_CYCLES = 'tab-cycles'
SETTING_ADD_CREATED = 'add-creation-date'
SETTING_SEARCH_CASE_SENSITIVE = 'search-case-sensitive'
SETTING_AUTO_TEMPLATE_CASING = 'auto-template-case-sensitive'
SETTING_SORT_ORDER = 'sort-order'
SETTING_SAFE_SAVE = 'safe-save'
SETTING_SCROLL_MARGIN = 'scroll-margin'
SETTING_RESET_TERMINAL = 'reset-terminal'
SETTING_SHOW_NUMBERS = 'show-numbers'
SETTING_USE_COLORS = 'use-colors'
SETTING_TASK_FORMAT = 'task-format'
SETTING_REUSE_RECURRING = 'reuse-recurring'
SETTING_CLEAR_CONTEXT = 'clear-contexts'
SETTING_RELATED_SHOW_SELF = 'related-show-self'
SETTING_FONT = 'font'
SETTING_FONTSIZE = 'font-size'
SETTING_SINGLE_INSTANCE = 'single-instance'
SETTING_CREATE_FROM_SEARCH = 'create-from-search'
SETTING_AUTO_ID = 'auto-id'
SETTING_HIDE_SEQUENTIAL = 'hide-sequential'
SETTING_CLICKABLE = 'clickable'
SETTING_DAILY_RELOAD = 'daily-reload'
SETTING_DELETE_IS = 'delete-is'
SETTING_TRASHFILE = 'trash-file'
SETTING_FILES = 'files'
SETTING_NOTES = 'notes'
SETTING_NOTE_SUFFIX = 'note-suffix'
SETTING_NOTE_NAMING = 'note-naming'
SETTING_INCLUDES = 'include'
SETTING_INFO_TIMEOUT = 'info-timeout'
SETTING_ARCHIVE_FILE = 'archive-file'
SETTING_ARCHIVE_IS = 'archive-is'
SETTING_ARCHIVE_ORIGIN_MARKER = 'archive-origin-marker'
SETTING_ARCHIVE_ORIGIN_IS = 'archive-origin-is'
SETTING_DONE_IS = 'done-is'
SETTING_DONE_FILE = 'done-file'
SETTING_TRACKER = 'time-tracking'
SETTING_DUE_DELTA = 'due-delta'
SETTING_SKIP_WEEKEND = 'due-skip-weekend'
SETTING_REDUCE_DISTRACTION = 'reduce-distraction'
SETTING_ESC_TIMEOUT = 'esc-timeout'
SETTING_WORD_BOUNDARIES = 'word-boundaries'
SETTING_HELP_ACTIONS = 'help-actions'
SETTING_SEARCH_CASE_YES = 'yes'
SETTING_SEARCH_CASE_NO = 'no'
SETTING_SEARCH_CASE_SMART = 'smart'
SETTING_HOOK_ON_NEW = 'on-new'
SETTING_HOOK_ON_SELECT = 'on-select'
SETTING_HOOK_ON_CHANGE = 'on-change'
SETTING_HOOK_ON_DONE = 'on-done'
SETTING_HOOK_ON_ARCHIVE = 'on-archive'
SETTING_HOOK_ON_DELETE = 'on-delete'
SETTING_HOOK_ON_QUIT = 'on-quit'
SETTING_HOOK_ON_START = 'on-start'
SETTING_HOOK_ON_TRACKING = 'on-tracking'
SETTING_ICON_SELECTION = 'selection'
SETTING_ICON_NOT_DONE = 'not-done'
SETTING_ICON_DONE = 'done'
SETTING_ICON_OVERFLOW_LEFT = 'overflow-left'
SETTING_ICON_OVERFLOW_RIGHT = 'overflow-right'
SETTING_ICON_OVERDUE = 'overdue'
SETTING_ICON_DUE_TODAY = 'due-today'
SETTING_ICON_DUE_TOMORROW = 'due-tomorrow'
SETTING_ICON_TRACKING = 'tracking'
SETTING_COL_NORMAL = 'normal'
SETTING_COL_COMPLETED = 'completed'
SETTING_COL_PRI_A = 'pri-a'
SETTING_COL_PRI_B = 'pri-b'
SETTING_COL_PRI_C = 'pri-c'
SETTING_COL_PRI_D = 'pri-d'
SETTING_COL_INACTIVE = 'inactive'
SETTING_COL_CONTEXT = 'context'
SETTING_COL_PROJECT = 'project'
SETTING_COL_ERROR = 'error'
SETTING_COL_HELP_TEXT = 'help'
SETTING_COL_HELP_KEY = 'help-key'
SETTING_COL_OVERFLOW = 'overflow'
SETTING_COL_OVERDUE = 'overdue'
SETTING_COL_DUE_TODAY = 'due-today'
SETTING_COL_DUE_TOMORROW = 'due-tomorrow'
SETTING_COL_TRACKING = 'tracking'
SETTING_COL_FILE = 'file'
SETTING_COL_URL = 'url'
SETTING_GK_QUIT = 'quit'
SETTING_GK_NEW = 'new'
SETTING_GK_COPY = 'to-clipboard'
SETTING_GK_NEW_REF = 'new-related'
SETTING_GK_NEW_AFTER = 'new-subsequent'
SETTING_GK_EDIT = 'edit'
SETTING_GK_OPEN_FILE = 'open-file'
SETTING_GK_TOGGLE_DONE = 'toggle-done'
SETTING_GK_DELETE_TASK = 'delete-task'
SETTING_GK_SEARCH = 'search'
SETTING_GK_TOGGLE_TRACKING = 'toggle-tracking'
SETTING_GK_OPEN_MANUAL = 'open-manual'
SETTING_GK_NAMED_SEARCHES = 'named-searches'
SETTING_GK_FOCUS_TASKS = 'focus-tasks'
SETTING_GK_TOGGLE_HIDDEN = 'toggle-hidden'
SETTING_GK_TOGGLE_DARK = 'toggle-dark-mode'
SETTING_GK_DELEGATE = 'delegate'
SETTING_GK_INC_PRIO = 'prio-up'
SETTING_GK_DEC_PRIO = 'prio-down'
SETTING_GK_REM_PRIO = 'prio-none'
SETTING_GK_SET_PRIOA = 'prio-a'
SETTING_GK_SET_PRIOB = 'prio-b'
SETTING_GK_SET_PRIOC = 'prio-c'
SETTING_GK_SET_PRIOD = 'prio-d'

TF_SELECTION = 'selection'
TF_NUMBER = 'nr'
TF_DESCRIPTION = 'description'
TF_DONE = 'done'
TF_TRACKING = 'tracking'
TF_DUE = 'due'
TF_ALL = 'all'
TF_DUEDAYS = 'duedays'
TF_PRIORITY = 'pri'
TF_CREATED = 'created'
TF_COMPLETED = 'completed'
TF_COMPLETED_DATE = 'completed_date'
TF_LINENR = 'linenr'
TF_AGE = 'age'
TF_FILE = 'file'
TF_PROJECTS = 'projects'
TF_CONTEXTS = 'contexts'
TF_NOTE = 'note'
TF_SPENT = 'spent'


class SearchCaseBehaviour:
    SENSITIVE = None
    INSENSITIVE = None
    SMART = None

    def __init__(self, value):
        if not self.is_valid_value(value):
            raise ValueError(value)

        self.value = value

    def __str__(self):
        return self.value

    @classmethod
    def is_valid_value(cls, value):
        return value in [SETTING_SEARCH_CASE_YES,
                         SETTING_SEARCH_CASE_NO,
                         SETTING_SEARCH_CASE_SMART]

    def lower(self, text):
        """Create a lower-case version conditionally based on the value of 'self'"""
        if self.can_lowercase(text):
            return text.lower()
        return text

    def can_lowercase(self, text):
        return self == SearchCaseBehaviour.INSENSITIVE or \
               (self == SearchCaseBehaviour.SMART
                and not any(letter.isupper() for letter in text))

    def __eq__(self, other):
        if isinstance(other, SearchCaseBehaviour):
            return self.value == other.value
        return self.value == str(other)

    def __ne__(self, other):
        if isinstance(other, SearchCaseBehaviour):
            return self.value != other.value
        return self.value != str(other)

    def eq(self, left, right):
        """Check whether needle and haystack are the same

        'needle' is driving the condition whether lower-casing should apply
        """
        if self.can_lowercase(left):
            return left.lower() == right.lower()
        return left == right

    def startswith(self, part, text):
        """Check whether text starts with part

        'part' is controlling the smart lower-case behaviour"""
        if self.can_lowercase(part):
            return text.lower().startswith(part.lower())
        return text.startswith(part)

    def contains(self, part, text):
        """Check whether part occurs in text

        'part' is controlling the smart lower-case behaviour"""
        if self.can_lowercase(part):
            return part.lower() in text.lower()
        return part in text


SearchCaseBehaviour.INSENSITIVE = SearchCaseBehaviour(SETTING_SEARCH_CASE_NO)
SearchCaseBehaviour.SENSITIVE = SearchCaseBehaviour(SETTING_SEARCH_CASE_YES)
SearchCaseBehaviour.SMART = SearchCaseBehaviour(SETTING_SEARCH_CASE_SMART)


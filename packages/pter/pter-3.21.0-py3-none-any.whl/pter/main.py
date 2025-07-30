import argparse
import pathlib
import sys
import locale
import io

try:
    from pter.curses import run_cursesui
except ImportError:
    run_cursesui = None

try:
    from pter.qtui import run_qtui
    qterr = None
except ImportError as exc:
    run_qtui = None
    qterr = exc

from pter import common
from pter import version
from pter import utils
from pter import configuration
from pter.tr import tr


def parse_args(is_qtui):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config',
                        type=str,
                        default=common.CONFIGFILE,
                        help=tr("Location of your configuration file. Defaults to %(default)s."))
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f'%(prog)s {version.__version__}')
    parser.add_argument('-u', '--check-for-updates',
                        default=False,
                        action='store_true',
                        help=tr("Check online whether a new version of pter is available."))
    parser.add_argument('-n', '--new-task',
                        type=str,
                        default=None,
                        help=tr("Add this as a new task to the selected file."))
    parser.add_argument('-l', '--log-level',
                        type=str,
                        default='error',
                        help=tr("Log level. Defaults to %(default)s."))
    parser.add_argument('--log-file',
                        type=str,
                        default=common.LOGFILE,
                        help=tr("Where to write the log file to. Defaults to %(default)s."))

    if is_qtui:
        parser.add_argument('-a', '--add-task',
                            default=False,
                            action='store_true',
                            help=tr("Directly start to create a new task"))
    else:
        parser.add_argument('-s', '--search',
                            default=None,
                            type=str,
                            help=tr("Load search upon start"))
        parser.add_argument('-k', '--list-keys',
                            default=False,
                            action="store_true",
                            help=tr("Show all key bindings and exit"))

    parser.add_argument('filename',
                        type=str,
                        nargs='*',
                        help=tr('todo.txt file(s) to open'))

    return parser.parse_args()


def run():
    is_qtui = pathlib.Path(sys.argv[0]).name == common.QTPROGRAMNAME

    args = parse_args(is_qtui)

    if args.check_for_updates:
        latest_version = utils.query_latest_version()
        if version.__version__ < latest_version:
            print(tr("A newer version, {latest_version}, is available.")
                    .format(latest_version=latest_version))
        else:
            print(tr("{programname} is up to date.").format(programname=common.PROGRAMNAME))
        return 0

    # ensure logfile directory
    if args.log_file is not None:
        log_path = pathlib.Path(args.log_file).resolve().expanduser().parent
        log_path.mkdir(parents=True, exist_ok=True)

    # obtain config
    config = configuration.get_config(args)

    if args.new_task is not None:
        sources = utils.open_sources(args, config)
        if len(sources) == 0:
            print(tr("You have to provide at least one todo.txt file."), file=sys.stderr)
            return 1

        filename = sources[0].source.filename

        text = args.new_task
        if text == '-':
            text = sys.stdin.read()

        if len(text) == 0:
            return -1

        mode = "r+t"
        if not filename.exists():
            mode = "wt"
        
        with open(filename, mode, encoding="utf-8") as fd:
            fd.seek(0, io.SEEK_END)
            for line in text.split("\n"):
                if len(line.strip()) == 0:
                    continue
                fd.write(utils.dehumanize_dates(line) + "\n")
        return 0

    if is_qtui:
        success = -1
        if run_qtui is None:
            print(tr("PyQt5 is not installed or could otherwise not be imported: {}").format(qterr),
                  file=sys.stderr)
        else:
            success = 0
            run_qtui(args, config)

    elif run_cursesui is not None:
        success = run_cursesui(args, config)

    else:
        print(tr("Neither PyQt5 nor curses are installed. To start the Qt version, please run 'qpter'."), file=sys.stderr)
        success = -2

    return success

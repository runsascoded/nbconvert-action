from argparse import ArgumentParser
from re import match
import shlex
import sys


class ArgsParser(ArgumentParser):
  '''ArgumentParser that adds an "--args" flag that takes extra arguments as a single Bash string.

  The value passed to "--args" will be split with `shlex`, and converted into potentially multiple arguments.

  Note that the value typically needs to be passed as "--args=<value>" (as opposed to as two Bash arguments: "--args", "<value>").

  Useful for e.g. specifying arguments across multiple YAML files that lack the ability to concatenate lists.
  '''

  ARGS_HELP = '''Additional arguments, passed as one bash-token string (e.g. "-f -x").

  If the string being passed begins with a "-" character (as it typically will), then this argument should be expressed as one bash token like "--args=-f -x" (as opposed to two tokens: "--args", "-f -x"), so that argparse doesn\'t get confused.

  Useful for e.g. specifying arguments across multiple YAML files that lack the ability to concatenate lists.
  '''

  def __init__(self, *args, log=None, **kwargs):
    super(ArgsParser, self).__init__(*args, **kwargs)
    self.add_argument('--args', help=self.ARGS_HELP)
    if log is True:
      self._log = print
    elif log:
      if hasattr(log, 'write'):
        def _print(msg):
          log.write(msg + '\n')
        self._log = _print
      else:
        self._log = log
    else:
      self._log = None

  def log(self, *args):
    if self._log:
      self._log(*args)

  def parse_args(self, *args, **kwargs):
    extra_args, _ = self.parse_known_args()
    self.log(f'extra_args: {extra_args}')

    extra_args = extra_args.args
    if extra_args:
      extra_args = shlex.split(extra_args)
      self.log(f'post-shlex --args: {extra_args}')
      [(idx, args_arg)] = [
        (idx, arg)
        for idx, arg in enumerate(sys.argv)
        if arg.startswith('--args')
      ]
      args_arg_span_size = 1 if args_arg.startswith('--args=') else 2

      args = sys.argv

      # Strip 'python' executable from front of sys.argv, if present:
      if match('python3?', args[0]):
        args = args[1:]

      # Strip called python file from sys.argv; ArgumentParser.parse_args() does this on its own
      # when called with no arguments, but we are passing explicit arguments here, so need to
      # mimic it.
      args = args[1:]

      # Strip "--args=<value>" or ["--args","<value>"] args:
      args = sys.argv[1:idx] + extra_args + sys.argv[(idx+args_arg_span_size):]

      args = super(ArgsParser, self).parse_args(args)
    else:
      args = super(ArgsParser, self).parse_args()

    return args

  def exit(self, status=0, message=None):
    if status:
      args_msg = 'error: argument --args: expected one argument'
      if args_msg in message:
        raise Exception(f'argparse is exiting with message "{args_msg}". Most likely, you are passing a value to the "--args" flag as a separate Bash argument, and that value begins with a dash ("-"), confusing argparse. Pass "--args=<value>" as one bash token instead.')
      else:
        raise Exception(f'argparse error: {message}')
    exit(status)

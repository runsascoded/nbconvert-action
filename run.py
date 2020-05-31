from subprocess import check_call, check_output, CalledProcessError


def lines(*cmd, keep_trailing_newline=False):
  print(f'Running: {cmd}')
  if len(cmd) == 1 and (isinstance(cmd[0], list) or isinstance(cmd[0], tuple)):
    cmd = cmd[0]
  lines = [
    line.strip()
    for line in
    check_output([ str(arg) for arg in cmd ]).decode().split('\n')
  ]

  if not keep_trailing_newline and lines and not lines[-1]:
    lines = lines[:-1]

  return lines


def line(*cmd):
  _lines = lines(*cmd)
  if len(_lines) == 1:
    return _lines[0]
  else:
    raise ValueError(f'Expected 1 line, found {len(_lines)}:\n\t%s' % '\n\t'.join(_lines))


def run(*cmd):
  print(f'Running: {cmd}')
  check_call([ str(arg) for arg in cmd ])


def check(cmd):
  try:
    run(*cmd)
    return True
  except CalledProcessError:
    return False
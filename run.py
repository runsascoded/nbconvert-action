from subprocess import check_call, check_output, CalledProcessError


def parse_cmd(cmd):
  if len(cmd) == 1 and (isinstance(cmd[0], list) or isinstance(cmd[0], tuple)):
    cmd = cmd[0]
  return [ str(arg) for arg in cmd ]


def lines(*cmd, keep_trailing_newline=False):
  cmd = parse_cmd(cmd)
  print(f'Running: {cmd}')
  lines = [
    line.strip()
    for line in
    check_output(cmd).decode().split('\n')
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
  cmd = parse_cmd(cmd)
  print(f'Running: {cmd}')
  check_call(cmd)


def check(*cmd):
  try:
    run(*cmd)
    return True
  except CalledProcessError:
    return False
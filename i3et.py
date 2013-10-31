#!/usr/bin/python
import time
from select import *
from os import *
import json
import sys
from errno import *

# Location for the FIFO to receive status bar data
INPUT_FIFO = "/tmp/i3et"

# Order modules should be displayed in. Make sure i3status is first module to be
# displayed. Others will be displayed to the left of the i3status output.
module_order = ["i3status"]

next_wake_time = None
current_data = dict()

def decode_data(data):
  if data[0:3] == ',[{':
    # This looks like it is probably data from i3status
    try:
      data = json.loads(data[1:])
      module = "i3status"

    except:
      return
  else:
    try:
      data = json.loads(data)
      module = data.pop(0)["module"]

    except:
      return

  if module not in module_order:
    # Insert module at the default location (on the left)
    module_order.insert(0, module)

  current_data[module] = [list(), dict()]

  for x in data:
    if module == 'i3status':
      identifier = x['name']
      if 'instance' in x:
        identifier += '_' + x['instance']
    elif '_id' in x:
      identifier = x['_id']
    else:
      # This data doesn't conform
      next

    if '_display_for' in  x:
      x['_display_until'] = time.time() + x['_display_for']
      
    current_data[module][0].append(identifier)
    current_data[module][1][identifier] = x

def refresh_data():
  global next_wake_time
  tmp = list()
  for x in module_order:
    if x in current_data:
      for y in current_data[x][0]:
        block = current_data[x][1][y]
        if "_display_until" in block:
          if block["_display_until"] < time.time():
            # This block should no longer be displayed
            del current_data[x][0][current_data[x][0].index(y)]
            del current_data[x][1][y]
            continue
          elif next_wake_time is None \
                or block["_display_until"] < next_wake_time:
            next_wake_time = block["_display_until"]

        tmp.append(block)

  if len(tmp):
    print ",",
    print(json.dumps(tmp))
  else:
    # No messages should be displayed
    print(',[{"full_text":""}]')

  sys.stdout.flush()

def main(): 
  global next_wake_time

  try:
    unlink(INPUT_FIFO)

  except OSError:
    # Ignore if file doesn't exist
    pass

  mkfifo(INPUT_FIFO)
  fifo = None
  poll = epoll()
  while True:
    if fifo is None:
      fifo = open(INPUT_FIFO, O_RDONLY | O_NONBLOCK)
      poll.register(fifo, EPOLLIN | EPOLLHUP)
  
    if next_wake_time is not None:
      events = poll.poll(next_wake_time - time.time())
      if next_wake_time - time.time() <= 0:
        next_wake_time = None
    else:

      try:
        events = poll.poll()

      except IOError, e:
        if e.errno == EINTR:
          continue
        else:
          raise

    for (fd, event) in events:
      if fd == fifo:
        if event & EPOLLIN:
          data = read(fd, PIPE_BUF)
          decode_data(data)
  
        if event & EPOLLHUP:
          poll.unregister(fifo)
          close(fifo)
          fifo = None

    refresh_data()

if __name__ == "__main__":
  print('{"version":1}\n[\n[{"full_text":""}]')
  sys.stdout.flush()
  main()

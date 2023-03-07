import getopt
import sys
import pyaudio
import wave
import time

# length of data to read.
chunk = 1024


def main():
  try:
    opts, args = getopt.getopt(
      sys.argv[1:], "hld:f:t:s:",
      ["help", "list", "device=", "file=", "time=", "sleep="])

  except getopt.GetoptError as err:
    # print help information and exit:
    print(err)  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  deviceId = None
  file = None
  t = None
  s = None

  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      return

    elif o in ("-l", "--list"):
      list()
      return

    elif o in ("-d", "--device"):
      deviceId = a

    elif o in ("-t", "--time"):
      t = a

    elif o in ("-s", "--sleep"):
      s = a

    elif o in ("-f", "--file"):
      file = a
    else:
      assert False, "unhandled option: " + o

  if (deviceId is None):
    assert False, "device id not specified"

  if (file is None):
    assert False, "file not specified"

  loop(file, int(deviceId), t, s)


def usage():
  print(
     "options:\n"
     " -h --help    show help\n"
     " -l --list    list devices\n"
     " -d --device  device id (see -l)\n"
     " -f --file    path to wav file\n"
     " -t --time    time sync (seconds)\n"
     " -s --sleep   delay/sleep (ms)\n"
     "\n"
     "examples:\n"
     " looper -h\n"
     " looper -l\n"
     " looper -d 1 -f file.wav -t 10 -s 50")


def list():
  p = pyaudio.PyAudio()
  for i in range(p.get_device_count()):
    device = p.get_device_info_by_index(i)
    name = device["name"]
    if 'Speaker' in name:
      print(str(i) + ': ' + name)


def loop(file, deviceId, t, s):
  p = pyaudio.PyAudio()
  device = p.get_device_info_by_index(deviceId)
  name = device["name"]
  print("looping '" + file + "' on device: " + name)

  wf = wave.open(file, 'rb')
  stream = p.open(
    format=p.get_format_from_width(wf.getsampwidth()),
    channels=wf.getnchannels(),
    rate=wf.getframerate(),
    output=True,
    output_device_index=deviceId)

  # "crude, but effective" - 7 of 9
  if t is not None:
    timeSlot = int(t)
    print("sync to time: " + t + "s")
    ticks = 0

    while True:
      secs = (int)(time.time())
      ms = (time.time() - secs) * 1000
      mod = secs % timeSlot

      if (mod == 0) and (ms <= 2):
        break

      ticks += 1
      if ticks % 100 == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

      time.sleep(0.0001)
    print()
    print("time now: " + str(time.time()))

  if s is not None:
    sleepMs = int(s)
    print("sleeping: " + s + "ms")
    time.sleep(sleepMs / 1000)

  print("looping, press ctrl+c to exit")
  data = wf.readframes(chunk)
  while data:
    stream.write(data)
    data = wf.readframes(chunk)

    if data == b'':  # if file is over then rewind.
      wf.rewind()
      data = wf.readframes(chunk)

  # probably never called?
  wf.close()
  stream.close()
  p.terminate()


if __name__ == "__main__":
  main()

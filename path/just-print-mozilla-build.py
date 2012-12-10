#!/usr/bin/env python2.7

# This script is intended to provide a very fast way to get what amounts to a
# 'make -w -j1' Mozilla build log containing the commands that are invoked to
# build all the C/C++/Objective-C source files in a Mozilla source tree. (Or at
# least all the source files that are actually built on the user's platform for
# a given .mozconfig configuration.) It is intended to be used for setting up
# Eclipse CDT with the Mozilla source, since Eclipse CDT's Build Output Parser
# requires a build log from a build using -w and -j1, which would otherwise be
# a very slow build. See:
#
#   https://developer.mozilla.org/en/Eclipse_CDT
#
# The idea behind this script is to invoke 'make' with the --just-print/-n
# option in order to get build console output without actually building
# anything (if possible), since actually building is much, much slower.
#
# There are several complications to using --just-print that resulted in the
# creation of this script.
#
# The first complication is that --just-print isn't sufficient to obtain the
# commands invoked to build targets if those targets are up to date, since in
# that case 'make' will print nothing for them. The obvious way around this is
# to also pass --always-make/-B, but that causes pretty much everything to be
# rebuilt for real, despite the --just-print argument. Presumably this is
# because --always-make causes the makefiles to be recreated, which results in
# --just-print being ignored for a lot of things.
#
# More specifically, it seems that --just-print works only for the build
# artifact that is being built by 'make' at any given moment. If that artifact
# depends on any other artifacts that are themselves out of date, then
# --just-print doesn't seem to apply to the out of date dependencies, and they
# will be rebuilt for real in order to satisfy the --just-print request for the
# current make target...or something like that.
#
# As a result of this issue, this script avoids the use of --always-make.
# Instead, it convinces 'make' that targets need to be rebuilt by temporarily
# changing the name of the targets of interest in the object directory before
# running 'make' so they appear to me missing.
#
# Ideally we'd keep the work that 'make' does to a minimum by only having it
# "rebuild" each source file into a corresponding object file. This could be
# achieved by only temporarily renaming object files that correspond directly
# to source files prior to invoking 'make', but it takes time to figure out
# which object files those are. It turn out to be faster to simply rename all
# object files in the object directory. The only issue with this approach is
# that make will abort with an error if the object directory is out of date and
# it needs to make targets that depend on the object files that have been
# hidden from it. To avoid this, we also pass 'make' the --ignore-errors/-i and
# --keep-going/-k arguments.
#
# Another complication with using --just-print with the Mozilla source is
# that the NSS code has its own build system. Rather than having 'make'
# implicitly recurse into the NSS code, the Mozilla build system explicitly
# invokes 'make' in the appropriate NSS directories. The problem with this is
# that since 'make' is explicitly invoked as a command in a recipe for a build
# target to build these NSS directories, when 'make' reaches
# objdir/security/manager/Makefile the --just-print causes it to just print
# these 'make' commands rather than recursing into the NSS code. To work around
# this problem this script has to specially handle the NSS code by finding the
# 'make' commands that should be invoked, and invoking them itself after adding
# the --just-print, --ignore-errors and --keep-going arguments.
#
# Just for completeness, we also specially handle 'nsprpub/config' since its
# two source files (now.c and nsinstall.c) don't otherwise seem to be rebuilt.
# (These files just create two independant executables, so probably in practice
# nobody using CDT with the Mozilla source will actually care about CDT
# handling their source well, but it costs virtually nothing to build them.)
#
# Finally, of course, to be useful for Eclipse CDT's Build Output Parser, we
# need to make sure that 'make' is invoked with -w and -j1.


# This script was validating by comparing the data gathered by the CDT Build
# Output Parser for a log from a full, clean -w -j1 rebuild to the data
# gathered from the output from this script. Specifically this means comparing
# the contents of the file:
#
#   {workspace-dir}/.metadata/.plugins/org.eclipse.cdt.core/{your-project}.language.settings.xml
#
# for the two cases. If reproducing, remember to clear the data gathered by the
# Build Output Parser between each "rebuild" by selecting "CDT GCC Build Output
# Parser" in the Providers tab and then clicking "Clear Entries". The script
# diff-bop-settings.py can be used to compare two language.settings.xml files.
#
# On last test, this script resulted in Eclipse picking up _exactly_ the same
# settings as it did from a real, clean '-w -j1' build.


# TODO: Does pymake support -wnik?


"just-print-mozilla-build.py, Jonathan Watt, 2012"

__version__ = "1.0"


# Building the 'tools' target gets us data for more source files (mainly files
# in test directories I think):
make_targets = ["libs", "tools"]


import os, sys, subprocess, threading, argparse, traceback, shlex, time, re

usage = "%(prog)s [options]"
description = "This script is used to do a 'make --just-print --print-directory -j1' \"rebuild\" of a preexisting Mozilla object directory. This is useful for setting up Eclipse CDT with the Mozilla source. For more information see the comments in this script's source."
parser = argparse.ArgumentParser(usage=usage, description=description)
parser.add_argument("--version",
                    action="version",
                    help="Show program's version number and exit.",
                    version="%(prog)s v" + __version__)
parser.add_argument("-o", "--objdir",
                    dest="objdir", type=str,
                    action="store",
                    help="Specifies the object directory that is to be \"rebuilt\" (this argument only needs to be specified when this script is not run from inside an object directory).",
                    metavar="OBJDIR")
parser.add_argument("--filter", type=str,
                    dest="filter", default="expected-errors",
                    action="store",
                    choices=["expected-errors", "off", "almost"],
                    help="Used to control filtering of the 'make' output. Due to the way this script works, certain errors are expected (and harmless) if your object directory is out of date. The default value of this argument, 'expected-errors', causes these errors to be filtered out so they don't slow CDT's build log parsing down. The value 'off' disables all filtering. The value 'almost' causes the script to use the filtering code paths, but abort filtering at the last moment (useful for testing the integrity of the filter code paths).")
"""
parser.add_argument("-p", "--prebuild",
                    dest="prebuild", default=False,
                    action="count",
                    help="Rebuild for real using the make flags specified in the object directory's .mozconfig prior to doing the --just-print build. This is useful if the object directory is out of date, since that can cause the --just-print build to build for real (and that will be a really slow rebuild because it has to use -j1).")
"""
script_args = parser.parse_args()

origdir = os.getcwd()
if script_args.objdir:
  objdir = os.path.normpath(os.path.abspath(script_args.objdir))
else:
  objdir = origdir
topobjdir = objdir
while not os.path.exists(os.path.join(topobjdir, 'mozilla-config.h')):
  if topobjdir == "/":
    break
  topobjdir = os.path.dirname(topobjdir)

if not os.path.exists(os.path.join(topobjdir, 'mozilla-config.h')):
  sys.stderr.write("Error: Not in a Mozilla object directory. You must specify --objdir.\n")
  exit(1)

os.chdir(objdir)

objext = ".o"
if sys.platform.startswith("win"):
  objext = ".obj"
tmpext = objext + ".jpmb"

def change_filename_extensions(suffix, newsuffix, root):
  "Change all files under 'root' that have the extension 'suffix' to 'newsuffix'."
  suffix_len = len(suffix)
  at_topobjdir = True
  ignored_topobjdirs = ["_leaktest", "_profile", "_tests", "_virtualenv", "dist", "staticlib"]
  ignored_dirs = [".deps"]
  for parent, dirs, files in os.walk(root):
    if at_topobjdir:
      for d in ignored_topobjdirs:
        if d in dirs:
          dirs.remove(d) # don't recurse into this dir
      at_topobjdir = False
    for d in ignored_dirs:
      if d in dirs:
        dirs.remove(d) # don't recurse into this dir
    dir = os.path.abspath(os.path.join(root, parent))
    for filename in files:
      if filename[-suffix_len:] == suffix:
        filepath = os.path.join(dir, filename)
        newfilepath = filepath[:-suffix_len] + newsuffix
        # This assert was to check that 'make' doesn't remake renamed files,
        # but it doesn't. (Other than slowing down this script, it wouldn't
        # matter anyway, since the os.rename() would overwrite remade files and
        # return the object tree to its original state.)
        #assert not os.path.exists(newfilepath)
        os.rename(filepath, newfilepath)

# This class is designed to be able to filter both stdout and stderr output
# from 'make', but we're currently only using it to filter stderr output. (See
# the comment for invoke_make below.)
#
class MakeOutputFilter(object):
  def __init__(self, outstream):
    self.outstream = outstream
    # Gah, it seems that we _can_ get incomplete lines from stderr despite it
    # being unbuffered, and despite passing a very large number to os.read().
    # As a result we are forced to buffer stderr output, even if only briefly.
    #self.can_buffer = (outstream != sys.stderr)
    self.can_buffer = True
    self.buffer = ""
    self.re_first_word = re.compile("^\s*\S+")
    self.re_compiler = re.compile("gcc|[gc]\+\+|clang")
    self.re_Entering_Leaving = re.compile("^g?make(?:\[\d+\])?: (Entering|Leaving)")
    self.re_No_rule = re.compile("^g?make(?:\[\d+\])?: \*\*\* No rule to make target")
    self.re_Error_ignored = re.compile("^g?make(?:\[\d+\])?: \[[^\]]+\] Error \d+ \(ignored\)")
    self.re_disabled_tests = re.compile("^Makefile:\d+: (browser_|test_|httpserver )")
  def filter(self, data, almost):
    assert not "\r" in data
    # We use split("\n"), not splitlines(), because we want to know if the last
    # line ended with "\n" or not so we can tell when the last line is
    # incomplete due to subprocess buffering.
    lines = data.split("\n")
    last_line_is_complete = (lines[-1] == "")
    if last_line_is_complete:
      # Get rid of the trailing "" so that lines[-1] is the last line:
      lines.pop()
    if len(lines) > 1:
      # Even if lines[0] == "", this is the right thing to do:
      self.__filter_and_write__(self.buffer + lines[0] + "\n", almost)
      self.buffer = ""
    for i in range(1, len(lines)-1):
      # For each line except the first and last line:
      self.__filter_and_write__(lines[i] + "\n", almost)
    lastline = lines[-1]
    if last_line_is_complete:
      # We want to include self.buffer for the case when 'data' contained only
      # one line. Since the |len(lines) > 1| case resets self.buffer, this is
      # also okay when we have more than one line.
      self.__filter_and_write__(self.buffer + lastline + "\n", almost)
      self.buffer = ""
      return
    if self.can_buffer:
      self.buffer += lastline
      return
    # Writing a partial line to stderr would be really bad since any stdout
    # output that follows could intersect it. Adding it to self.buffer would
    # have similar issues.
    assert False, "Uh, stderr is unbuffered - how did we get a partial line?!"
  def flush(self):
    if self.buffer:
      self.outstream.write(self.buffer)
      self.buffer = ""
    self.outstream.flush()
  def __filter_and_write__(self, line, almost):
    if self.outstream == sys.stderr:
      # Make sure we don't have any partially written stdout lines, otherwise
      # the stderr that we're about to write will appear in the middle of a
      # stdout line!!
      pass #sys.stdout.flush() # XXX maybe not do this to get same order
    #
    # XXX You'd expect that this script should produce exactly the same output
    # when passed --filter=almost as it would when passed --filter=off. That
    # doesn't seem to _quite_ be the case though, and I'm not just talking
    # about lines being slightly out of order. For a full build log I'm seeing
    # one or two weird lines in the diff where output can be missing, or
    # weirdly broken onto different lines. This doesn't happen when we do the
    # filtering and no unexpected 'make' errors occur, perhaps because in that
    # case the only stderr output is known and discarded, so this script never
    # actually writes any stderr. But it's a concern. It seems like the chances
    # of it interfearing with unexpected stderr output that we don't filter out
    # is low, but who knows.
    #
    # Is a stray "\r" finding its way in somewhere? Or something being split in
    # a way that we interpret something as "\r"? A |grep -P '\r'| of a full log
    # says there is no \r in there, but that seems to be how it's
    # occasionally behaving.
    if almost:
      # We've "almost" filtered by going through the filtering code paths, but
      # now it's time to just print the output without actually discarding
      # anything.
      self.outstream.write(line)
    if self.re_No_rule.match(line) or self.re_Error_ignored.match(line) or \
       self.re_disabled_tests.match(line):
      return
    self.outstream.write(line)

stderr_filter = MakeOutputFilter(sys.stderr)

# This function attempts to intercept and filter the output from the 'make'
# process in order to strip out lines that are not of interest to Eclipse CDT's
# Build Output Parser. This is because CDT's parser is pretty slow, so the less
# output it has to process the better. It's particularly important to filter
# out the harmless error messages that make can output when the object
# directory is out of date, since Eclipse gets particularly slow when it
# encounters errors in the build output. See:
#
#   https://bugs.eclipse.org/bugs/show_bug.cgi?id=314428
#
# Another reason to filter the output is to hide those:
#
#   make[x]: *** No rule to make target `foo.o', needed by `bar.baz'.
#   make[x]: [target] Error 2 (ignored)
#
# lines from the user so that they don't think something went wrong.
#
# I was originally using stderr=subprocess.PIPE and stdout=subprocess.PIPE and
# trying to read from and filter the subprocess's .stdout and .stderr
# separately. However, I couldn't find a way to do that without deadlocking
# (other than setting bufsize to something huge). The problem is that
# p.stdout.read()/p.stderr.read() block waiting for the subprocess to send some
# stdout/stderr, while at the same time if the pipe for p.stdout/p.stderr
# becomes full then the subprocess blocks waiting for data to be cleared (read
# from) that pipe. As a result we can deadlock if the subprocess outputs enough
# data to fill the stdout pipe while outputing nothing to stderr. In this
# scenario the stderr read is blocking our process, waiting on the child to 
# provide some stderr output, but, as soon as the subprocess has filled the
# stdout pipe, it is blocked waiting on us to clear the stdout pipe. Deadlock!
#
# We could use communicate() instead, but that waits on the subprocess to
# finish before returning all the output from the process all in one go. That
# would mean we'd starve Eclipse of output, causing it to taking longer to
# process the output from this script. Furthermore, communicate() gives all the
# stdout and all the stderr output in two separate chunks, and there's no way
# to merge them back together in the order in which the subprocess output them.
#
# To get around this I tried to connect the subprocess's stdout and stderr to
# a pipe to be able to read the output from the subprocess as its written. The
# problem with this approach is that connecting the stdout of the subprocess to
# a pipe means that it's no longer writing directly to a terminal, and that in
# turn causes the subprocess to start buffering its stdout. This means that,
# while we'd see the stderr from the subprosses as its written (since stderr is
# unbuffered), the stdout will be delayed, preventing us passing on the stdout
# and stderr lines in the order in which they were written. Much more
# importantly though, the buffering of the stdout means that when the stdout
# of the subprocess is flushed, the last line of the flushed output may not be
# a complete line. As a result the any subsequent stderr output from the
# subprocess ends up being inserted right in the middle of that line of stdout
# output in the pipe. Obviously this is a complete deal breaker. One way around
# this would be to use two separate pipes, one for the stdout and one for the
# stderr. However, this still doesn't get arount the issue of being able to
# pass on the stdout and stderr output from the subprocess in the same order
# that they're written.
#
# The only solution to the subprocess buffering of stdout is probably to use
# something like pty.fork(), but it's not clear how portable that is.
#
# As a result this script simply doesn't try to intercept and filter the
# subprocess's stdout at this time. We leave the subprocess's stdout connected
# directly to the terminal so that it is not buffered, and only intercept and
# filter the (unbuffered) stderr from the subprocess.
#
# XXX Actually...it seems that our interception and processing of stderr can
# delay the output of stderr slightly. If you invoke this script with and
# without --filter=off and take a diff of the two outputs, you'll see that the
# stderr lines can sometimes be a few lines down from where they would
# otherwise have been.
#
def invoke_make(args, cwd=os.getcwd()):
  global script_args
  if script_args.filter == "off":
    #subprocess.check_call(args, cwd=cwd)
    #return
    p = subprocess.Popen(args, cwd=cwd)
    while p.poll() == None:
      time.sleep(0.05)
    return
  def wait_for_process_then_close_fd(proc, fd):
    while proc.poll() == None:
      time.sleep(0.05)
    # Close the pipe so that our os.read() call doesn't block forever waiting
    # for more data once it's reached the end of the subprocess's output:
    os.close(fd)
  (readpipe, writepipe) = os.pipe()
  p = subprocess.Popen(args, cwd=cwd, stderr=writepipe)
  t = threading.Thread(target=wait_for_process_then_close_fd, args=(p, writepipe))
  t.daemon = True #XXX thread dies with the program
  t.start()
  try:
    while True:
      output = os.read(readpipe, 10000000) # Read everything
      if output == "":
        break
      # If we ever tell the filter to write stderr output to stdout we must make
      # sure to call filter.flush() here, since otherwise the filter won't know
      # to do it and we'll get stderr output writing into the middle of real
      # stdout lines.
      stderr_filter.filter(output, script_args.filter == "almost")
  except Exception, e:
    # Kill the 'make' process to prevent further output from swamping the
    # "FAILED" message below. Even after it's gone we seem to have to sleep
    # for a bit longer before its output gets flushed. :-/
    if p.poll() == None:
      p.kill()
    while p.poll() == None:
      time.sleep(0.1)
    time.sleep(1)
    sys.stdout.flush()
    sys.stderr.flush()
    raise e
  finally:
    t.join()
    os.close(readpipe)
    stderr_filter.flush()

def rebuild_nss():
  manager_dir = os.path.join(topobjdir, "security", "manager")
  output = subprocess.check_output(["make", "-swnik"] + make_targets, cwd=manager_dir)
  for line in output.split('\n'):
    # The 'make' lines where -C specifies an absolute path are the lines
    # invoking 'make' with the Makefiles of the NSS build system.
    if "make -C /" in line:
      #line = line.replace("make -j1", "make -j1 -wnik")
      cmd = shlex.split(line.replace("make -C /", "make -j1 -wnik -C /"))
      invoke_make(cmd, cwd=manager_dir)

def rebuild_nsprpub_config():
  nsprpub_config_dir = os.path.join(topobjdir, "nsprpub", "config")
  invoke_make(["make", "-j1", "-wnik", "libs"], cwd=nsprpub_config_dir)

try:
  # Inform the user of the rename so that they're aware of it in case they
  # interupt this script:
  sys.stdout.write("Temporarily changing " + objext + " files to " + tmpext + " files to hide them from 'make'...")
  sys.stdout.flush()
  change_filename_extensions(objext, tmpext, topobjdir)
  sys.stdout.write("done.\n")
  sys.stdout.flush()
  # We build NSS and nsprpub/config first so that the build output doesn't end
  # with their output, since that could confuse users into thinking that this
  # script didn't complete.
  rebuild_nss()
  rebuild_nsprpub_config()
  invoke_make(["make", "-j1", "-wnik"] + make_targets, cwd=topobjdir)
except Exception, e:
  traceback.print_exc(file=sys.stderr)
  msg = " ERROR: " + os.path.basename(sys.argv[0]) + " FAILED!\n"
  sys.stderr.write("\n\n")
  sys.stderr.write("*" * len(msg) + "\n")
  sys.stderr.write(msg)
  sys.stderr.write("*" * len(msg) + "\n")
  sys.stderr.write("\n\n")
finally:
  sys.stdout.write("Changing " + tmpext + " files back to " + objext + " files...")
  sys.stdout.flush()
  change_filename_extensions(tmpext, objext, topobjdir)
  sys.stdout.write("done.\n")
  sys.stdout.flush()

sys.exit(0)

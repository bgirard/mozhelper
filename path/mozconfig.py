#!/usr/bin/env python
import sys
import platform
try:
    import multiprocessing
except:
    multiprocessing = None

def ask(question, choices):
    print question
    n = 1
    for choice in choices:
        print "%s. %s" % (n, choice)
        n += 1
    while True:
        choice = -1
        try:
            choice = int(raw_input())
        except (KeyboardInterrupt, EOFError):
            sys.exit(1)
        except ValueError:
            pass
        if choice < 1 or choice > len(choices):
            print "Please make a choice between 1 and %s" % len(choices)
            continue
        return choice - 1

apps = ["browser", "mobile"]
app = apps[ask("Do you want to work on:", ["Firefox", "Mobile Firefox (Fennec)"])]

opt = ask("Debug, Unoptimized, Optimized build?", ["Debug", "Unoptimized", "Optimized"])

lowmem = False
if platform.system() == 'Linux':
   lowmem = ask("How much total RAM does your system have?", ["<= 2GB", "> 2GB"])

num_proc = 0
if multiprocessing:
    num_proc = multiprocessing.cpu_count()
procs = False
#if num_proc:
#  procs = ask("%s processor%s detected. Would you like to use all of them when building Firefox?", ["Yes", "No"])  
if procs:
    num_proc = ask("How many processors would you like to use when building Firefox?", ["1", "2", "3", "4"]) + 1

print "Generating .mozconfig contents\n---------------\n"

def output(s):
    print >> sys.stderr, s

output("ac_add_options --enable-application=%s" % app)
output("")
if opt == 2:
    output("# Optimized")
    output("ac_add_options --disable-debug")
    output("ac_add_options --enable-optimization")
elif opt == 1:
    output("# Unoptimized with symbols")
    output("ac_add_options --disable-debug")
    output("ac_add_options --enable-symbols")
else:
    output("# Debug build")
    output("ac_add_options --enable-debug")
    output("ac_add_options --disable-optimization")

output("")
output("# Concurrent Jobs")
output('mk_add_options MOZ_MAKE_FLAGS="-j%s -s"' % (num_proc * 2))

if lowmem:
    output('export LDFLAGS="-Wl,--no-keep-memory"')


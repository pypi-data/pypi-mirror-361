from cppmake.error  import BuildError
from cppmake.config import verbose
import subprocess
import sys

def run(command, quiet=False, **kwargs):
    if verbose:
        print(command)
        p = subprocess.Popen(command, shell=True, stdout=None if verbose >= 2 else subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, **kwargs)
        e = ""
        while p.poll() is None:
            e += p.stderr.readline()
        if p.poll() == 0:
            print(e, end="", file=sys.stderr)
        else:
            raise BuildError(e)
    else:
        try:
            p = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, **kwargs)
            if not quiet:
                print(p.stderr, end="", file=sys.stderr)
        except subprocess.CalledProcessError as e:
            raise BuildError(e.stderr)
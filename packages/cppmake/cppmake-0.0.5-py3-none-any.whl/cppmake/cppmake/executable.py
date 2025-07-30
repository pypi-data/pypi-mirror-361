from cppmake.compiler import run_executable
from cppmake.config   import executable_suffix, type
from cppmake.object   import Object

class Executable:
    pool    = {}
    current = 0
    total   = 0
    
    def __new__(self, name):
        if name in Executable.pool.keys():
            return Executable.pool[name]
        else:
            self = super().__new__(self)
            Executable.pool[name] = self

            # Info
            self.name            = name
            self.executable_file = f"./bin/{type}/src/{self.name.replace('.', '.').replace(':', '/')}.{executable_suffix}" if executable_suffix != "" else \
                                   f"./bin/{type}/src/{self.name.replace('.' ,'.').replace(':', '/')}"
            
            # Subtask
            Object(self.name)

            # Status
            self.runned = False
            Executable.total += 1

            # Return
            return self

    def run(self):
        if not self.runned:
            # Subtask
            Object(self.name).link()

            # Self
            Executable.current += 1
            print(f"run executable [{Executable.current}/{Executable.total}]: {self.name}")
            run_executable(executable_file=f"./{self.executable_file}")

            # Status
            self.runned = True
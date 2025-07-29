from copy import deepcopy
from topasio.printing import writeVal
from inspect import currentframe
from pprint import pprint


class Element(dict):

    def __init__(self, starting_dict=None):
        super().__init__()
        self["_modified"] = [] # stores non-default values

        if starting_dict is not None:
            if isinstance(starting_dict, dict):
                self.update(starting_dict)
            else:
                raise TypeError("Expected a dictionary for starting_dict, got {}".format(type(starting_dict).__name__))

    def __setattr__(self, name, value):
        # print(f"Setting attribute '{name}' to '{value}'")
        # print(f"Setting attribute '{name}' to '{value}' in {self.__class__.__name__}")

        self[name] = value

        if name not in self["_modified"]:
            self["_modified"].append(name)  # Track modified attributes

    def __getattr__(self, name):
        # print(f"Accessing attribute '{name}'")
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        

    def getrepr(self, indent=0, delta_indent=4):
        
        res = ""
        
        for paramname in self["_modified"]:
            res += " " * indent + paramname + ": "
            if isinstance(self[paramname], Element):
                res += "\n"  # newline for nested block
                res += self[paramname].getrepr(indent + delta_indent)
            else:
                res += str(self[paramname]) + "\n"

        return res  # Remove trailing newline for cleaner output

    def dumpToFile(self, elemName, space_name, filename):

        with open(filename, "a") as f:
            for key in self["_modified"]:
                value = self[key]
                writeVal(f, 
                         space_name=space_name, 
                         elemName=elemName, 
                         key=key, 
                         value=value)
                
    def update(self, other):
        super().update(other)
        for key in other:
            if key not in self["_modified"]:
                self["_modified"].append(key)

    def __enter__(self):
        globas_before = currentframe().f_back.f_globals.copy()
        self._globals_before = globas_before
        return
    
    def __exit__(self, exc_type, exc_value, traceback):
        globals_after = currentframe().f_back.f_globals.copy()
        for key in globals_after:
            if key not in self["_globals_before"]:
                self[key] = globals_after[key]
                if key not in self["_modified"]:
                    self["_modified"].append(key)
                print(f"Added global variable '{key}' to element, with value: {globals_after[key]}")
        
        for key in globals_after:
            if key not in self["_globals_before"]:
                del currentframe().f_back.f_globals[key]

        del self["_globals_before"]
        # remove _globals_before from _modified
        if "_globals_before" in self["_modified"]:
            self["_modified"].remove("_globals_before")
    
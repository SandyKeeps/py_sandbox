import ast
from .visitor import FunctionFinderVisitor


class MusicPlayer:
   def __init__(self, function_to_call: str, value=None) -> None:
       """
       :param function_to_call: function defined in this class
       :param inputs: args and kwargs for the functions
       """
       self.value = value
       self.available_functions = {
           "play": self.play,
           "stop": self.stop,
           "skip": self.skip,
           "get_song_length": self.get_song_length
       }
       if isinstance(function_to_call, str):
           parsed_func = ast.parse(function_to_call, mode='eval')
           mv = FunctionFinderVisitor(function_to_call)
           mv.visit(parsed_func)
           self.h = self.handle_function(mv.functions)
       else:
           self.h = self.handle_function(function_to_call)
 
       self.analyze_value()
 
   def handle_function(self, function_package: dict) -> None:
       """
       runs the mapped functions after parsing
       :param function_package: a list of dictionaries which hold the functions and parameters
       """
       for func in function_package:
           if isinstance(func, str):
               transform = self.available_functions.get(func, self.unknown_func)
               transform()
               continue
           for func_name, call_args in func.items():
               transform = self.available_functions.get(func_name, self.unknown_func)
               if 'args' in call_args:
                   transform(*call_args['args'], **call_args["kwargs"])
               else:
                   transform(**call_args)
 
   def analyze_value(self) -> None:
       # Implement analytics here
       print(self.value)
 
   def play(self, song: str) -> None:
       # logic to play song
       self.value = "playing song"
 
   def stop(self, song: str) -> None:
       # stop current song
       self.value = "stopping song"
 
   def get_song_length(self, song: str) -> None:
       # can be a transform function, acts on a value
       self.value = len(song)
 
   def skip(self) -> None:
       # skip to next song
       self.value = "skipping song"
 
   def unknown_func(self, *args, **kwargs):
       print("Calling a function not in whitelist")
       self.value = "No No No"
       # one could implement a custom Exception for this
       raise Exception
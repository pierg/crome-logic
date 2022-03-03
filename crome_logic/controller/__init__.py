# from crome_logic.specification.temporal import LTL
#
#
# class Controller:
#     def __init__(
#         self,
#         mealy_machine: str,
#         specification: LTL | None = None,
#     ):
#
#         self.mealy_machine = mealy_machine
#         self.__current_location = None
#
#     def __str__(self):
#         output = (
#             f"States          \t {', '.join(self.states)}"
#             + f"\nInital State    \t {self.initial_state}"
#             + f"\nInput  Alphabet \t {', '.join([str(x) for x in self.input_alphabet])}"
#             + f"\nOutput Alphabet \t {', '.join([str(x) for x in self.output_alphabet])}\n\n"
#         )
#
#         headers = ["true_ins", "s", "s'", "true_outs"]
#         entries = []
#         for (inputs, state), (next_state, outputs) in self.transitions.items():
#             line = []
#             inputs_str = []
#             for x in inputs:
#                 if x.dontcare:
#                     inputs_str.append("-")
#                 elif not x.negated:
#                     inputs_str.append(str(x))
#             line.append(" ".join(inputs_str))
#             line.append(state)
#             line.append(next_state)
#             outputs_str = []
#             for alternatives in outputs:
#                 alternatives_str = []
#                 for x in alternatives:
#                     if not x.negated and not x.dontcare:
#                         alternatives_str.append(str(x))
#                 outputs_str.append(" ".join(alternatives_str))
#             line.append(" | ".join(outputs_str))
#             entries.append(line)
#
#         output += tabulate(entries, headers=headers)
#
#         return output
#
#     @property
#     def world(self) -> World:
#         return self.__world
#
#     @property
#     def name(self) -> str:
#         return self.__name
#
#     @property
#     def synth_time(self) -> float:
#         return round(self.__synth_time, 2)
#
#     @world.setter
#     def world(self, value: World):
#         self.__world = value
#
#     @property
#     def mealy_machine(self) -> str:
#         return self.__mealy_machine
#
#     def react(
#         self, input_vector: Tuple[Atom] = None
#     ) -> Tuple[Tuple[Atom], Tuple[Atom]]:
#         """Take a reaction in the mealy machine."""
#         edges = self.get_all_inputs_from_state(self.__current_state)
#         """match input with any edge"""
#         selected_edge = None
#         if input_vector is None:
#             """Take a random transition."""
#             selected_edge = random.choice(edges)
#         else:
#             for edge in edges:
#                 for i, elem in enumerate(edge):
#                     if elem.dontcare:
#                         continue
#                     if elem != input_vector[i]:
#                         break
#                     selected_edge = edge
#         if selected_edge is None:
#             raise Exception("No input matched with the edge")
#         (next_state, outputs) = self.__transitions[
#             (selected_edge, self.__current_state)
#         ]
#         self.__current_state = next_state
#         output_choice = random.sample(outputs, 1)[0]
#         for o in output_choice:
#             if o.kind == AtomKind.LOCATION and not o.negated:
#                 self.__current_location = list(o.typeset.values())[0]
#         return selected_edge, output_choice
#
#     def simulate_inputs(self, active_probability: int = 0.2) -> Tuple[Atom]:
#         inputs_assignment = []
#         for input, values in self.__inputs_ap.items():
#             """random choice between input true [0] or false [1] with prob
#             distribution."""
#             inputs_assignment.append(
#                 choices(
#                     [values[0], values[1]], [active_probability, 1 - active_probability]
#                 )
#             )
#
#         return tuple(*inputs_assignment)
#
#     def simulate(self, steps: int = 50):
#         """Simulate a run of 50 steps."""
#
#         headers = ["t", "inputs", "outputs"]
#         history: List[List[str]] = []
#
#         for i in range(steps):
#             inputs, outputs = self.react()
#             inputs_str = []
#             for x in inputs:
#                 if not x.negated:
#                     inputs_str.append(str(x))
#             outputs_str = []
#             for x in outputs:
#                 if not x.negated:
#                     outputs_str.append(str(x))
#             inputs_str = ", ".join(inputs_str)
#             outputs_str = ", ".join(outputs_str)
#             history.append([i, inputs_str, outputs_str])
#
#         return tabulate(history, headers=headers)
#
#     def simulate_day_night(self, steps: int = 50):
#         """Simulate a run of 50 steps."""
#
#         headers = ["t", "inputs", "outputs"]
#         history: List[List[str]] = []
#
#         d_time = True
#
#         for i in range(steps):
#             """Take a reaction in the mealy machine."""
#             edges = self.get_all_inputs_from_state(self.__current_state)
#             n_edges = []
#             d_edges = []
#             for edge in edges:
#                 for element in edge:
#                     if list(element.typeset.keys())[0] == "day":
#                         if not element.negated:
#                             d_edges.append(edge)
#                         else:
#                             n_edges.append(edge)
#             if i % 5 == 0:
#                 d_time = not d_time
#
#             if d_time:
#                 selected_edge = random.choice(d_edges)
#             else:
#                 selected_edge = random.choice(n_edges)
#
#             inputs, outputs = self.react(selected_edge)
#             inputs_str = []
#             for x in inputs:
#                 if not x.negated:
#                     inputs_str.append(str(x))
#             outputs_str = []
#             for x in outputs:
#                 if not x.negated:
#                     outputs_str.append(str(x))
#             inputs_str = ", ".join(inputs_str)
#             outputs_str = ", ".join(outputs_str)
#             history.append([i, inputs_str, outputs_str])
#
#         return tabulate(history, headers=headers)
#
#     def reset(self):
#         """Reset mealy machine."""
#         self.__current_state = self.__initial_state
#
#     def get_all_outputs_from_state(self, state: str) -> List[Tuple[Tuple[Atom]]]:
#         if state == self.__initial_state:
#             self.react(self.simulate_inputs())
#             state = self.__current_state
#         edges = []
#         for (ins, state_s), (state_t, outs) in self.__transitions.items():
#             if state_t == state:
#                 edges.append(outs)
#         return edges
#
#     def get_all_inputs_from_state(self, state: str) -> List[Tuple[Atom]]:
#         edges = []
#         for (ins, state_s), (state_t, outs) in self.__transitions.items():
#             if state_s == state:
#                 edges.append(ins)
#         return edges
#
#     @mealy_machine.setter
#     def mealy_machine(self, value: str):
#         self.__mealy_machine = value
#
#         self.__states: List[str] = StringMng.get_states_from_kiss(value)
#         self.__initial_state: str = StringMng.get_initial_state_from_kiss(value)
#         self.__current_state = self.__initial_state
#
#         inputs_str: List[str] = StringMng.get_inputs_from_kiss(value)
#         self.__input_alphabet: List[Boolean] = []
#         for input in inputs_str:
#             if self.world is not None:
#                 self.__input_alphabet.append(self.world.typeset[input])
#             else:
#                 self.__input_alphabet.append(Boolean(input))
#
#         outputs_str: List[str] = StringMng.get_outputs_from_kiss(value)
#         self.__output_alphabet: List[Boolean] = []
#         for output in outputs_str:
#             if self.world is not None:
#                 self.__output_alphabet.append(self.world.typeset[output])
#             else:
#                 self.__output_alphabet.append(Boolean(output))
#
#         """For each input and variables, returns the AP tuple corresponding to its true/false/dontcare assignment"""
#         self.__inputs_ap: Dict[Boolean, Tuple[Atom, Atom, Atom]] = {}
#         for input_type in self.__input_alphabet:
#             atom = input_type.to_atom()
#             self.__inputs_ap[input_type] = (atom, ~atom, atom.get_dontcare())
#         self.__outputs_ap: Dict[Boolean, Tuple[Atom, Atom, Atom]] = {}
#         for output_type in self.__output_alphabet:
#             atom = output_type.to_atom()
#             self.__outputs_ap[output_type] = (atom, ~atom, atom.get_dontcare())
#
#         """Transition is from (inputs, state) to (state, output), i.e. I x S -> S x O"""
#         self.__transitions: Dict[
#             Tuple[Tuple[Atom], str], Tuple[str, Tuple[Tuple[Atom]]]
#         ] = {}
#         for line in value.splitlines()[7:]:
#             transition = line.split()
#             if len(self.__input_alphabet) == 0:
#                 input_str = ""
#                 cur_state_str = transition[0]
#                 next_state_str = transition[1]
#                 output_str_list = []
#                 for element in transition[2:]:
#                     if "+" in element:
#                         continue
#                     output_str_list.append(element)
#             else:
#                 input_str = transition[0]
#                 cur_state_str = transition[1]
#                 next_state_str = transition[2]
#                 output_str_list = []
#                 for element in transition[3:]:
#                     if "+" in element:
#                         continue
#                     output_str_list.append(element)
#
#             list_inputs: List[Atom] = []
#             for i, input in enumerate(input_str):
#                 if input == "1":
#                     list_inputs.append(self.__inputs_ap[self.__input_alphabet[i]][0])
#                 elif input == "0":
#                     list_inputs.append(self.__inputs_ap[self.__input_alphabet[i]][1])
#                 else:
#                     list_inputs.append(self.__inputs_ap[self.__input_alphabet[i]][2])
#
#             output_alternatives = []
#             for output_str in output_str_list:
#                 list_outputs: List[Atom] = []
#                 for i, output in enumerate(output_str):
#                     if output == "1":
#                         list_outputs.append(
#                             self.__outputs_ap[self.__output_alphabet[i]][0]
#                         )
#                     elif output == "0":
#                         list_outputs.append(
#                             self.__outputs_ap[self.__output_alphabet[i]][1]
#                         )
#                     else:
#                         list_outputs.append(
#                             self.__outputs_ap[self.__output_alphabet[i]][2]
#                         )
#                 output_alternatives.append(tuple(list_outputs))
#
#             self.__transitions[(tuple(list_inputs), cur_state_str)] = (
#                 next_state_str,
#                 tuple(output_alternatives),
#             )
#
#     @property
#     def states(self) -> List[str]:
#         return self.__states
#
#     @property
#     def input_alphabet(self) -> List[Boolean]:
#         return self.__input_alphabet
#
#     @property
#     def locations(self) -> List[ReachLocation]:
#         locations = []
#         for element in self.__output_alphabet:
#             if element.kind == TypeKinds.LOCATION and isinstance(
#                 element, ReachLocation
#             ):
#                 locations.append(element)
#         return locations
#
#     @property
#     def output_alphabet(self) -> List[Boolean]:
#         return self.__output_alphabet
#
#     def all_entry_locations(self, typeset: Typeset) -> Set[ReachLocation]:
#         """List of all locations from where it is possible to reach any of the
#         locations of the controller."""
#         reachable_locations = set()
#         for location in self.locations:
#             """Extracting the locations from where 'first_location_to_visit' is
#             reachable."""
#             for class_name in location.adjacency_set:
#                 for t in typeset.values():
#                     if type(t).__name__ == class_name:
#                         reachable_locations.add(t)
#         return reachable_locations
#
#     @property
#     def transitions(
#         self,
#     ) -> Dict[Tuple[Tuple[Atom], str], Tuple[str, Tuple[Tuple[Atom]]]]:
#         return self.__transitions
#
#     @property
#     def initial_state(self) -> str:
#         return self.__initial_state
#
#     @property
#     def current_state(self) -> str:
#         return self.__current_state
#
#     @property
#     def current_location(self) -> ReachLocation:
#         return self.__current_location
#
#     @property
#     def next_location_to_visit(self) -> ReachLocation:
#         """Next location that the robot will need to visit, if it depends on
#         the input, then current location."""
#         next_location_to_visit = None
#
#         for inputs in self.get_all_inputs_from_state(self.__current_state):
#             (next_state, outputs) = self.__transitions[(inputs, self.__current_state)]
#             for output_choice in outputs:
#                 for o in output_choice:
#                     if o.kind == AtomKind.LOCATION and not o.negated:
#                         loc = list(o.typeset.values())[0]
#                         if next_location_to_visit is not None:
#                             if loc is not next_location_to_visit:
#                                 """Checking if current location is valid."""
#                                 if self.__current_location is not None:
#                                     return self.__current_location
#                                 else:
#                                     raise Exception(
#                                         "Mealy machine has never been active and \n"
#                                         "First location depends on future inputs or it can be different!"
#                                     )
#                         else:
#                             next_location_to_visit = loc
#
#         return next_location_to_visit
#
#         """Extracting the locations from where 'first_location_to_visit' is reachable"""
#         reachable_locations = []
#         for class_name in next_location_to_visit.adjacency_set:
#             for t in self.world.values():
#                 if type(t).__name__ == class_name:
#                     reachable_locations.append(t)
#         return reachable_locations

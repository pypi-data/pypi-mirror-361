
import json
from datetime import datetime
from typing import List, Dict, Set
from z3 import ModelRef, RatNumRef, IntNumRef, BoolRef

from smt_planning.smt.StateHandler import StateHandler
from smt_planning.dicts.PropertyDictionary import Property
from enum import Enum
from datetime import datetime
from typing import Dict

class PropertyAppearance:
	def __init__(self, property: Property, event: int, value: RatNumRef | BoolRef | IntNumRef) -> None:
		self.property = property
		self.event = event
		# Value has to be cast manually using z3's functions
		if type(value).__name__ == 'RatNumRef':
			decimal_value = value.as_decimal(20) # type: ignore
			# Remove the question mark at the end of the decimal value, which indicates an approximation
			if decimal_value[-1] == '?':
				decimal_value = decimal_value[:-1]
			self.value = float(decimal_value)
		elif type(value).__name__ == 'BoolRef':
			self.value = value.__bool__()
		elif type(value).__name__ == 'IntNumRef':
			self.value = int(str(value))
		else:
			raise NameError(f"No cast operation for type {type(value).__name__} of variabel {value} defined")

	def to_json(self) -> Dict[str, object]:
		dict = {
			"property_iri": self.property.iri,
			"value": self.value
		}
		return dict
	
	def __eq__(self, other):
		if isinstance(other, PropertyAppearance):
			return ((self.property.iri == other.property.iri))
		else:
			return False
		
	def __hash__(self):
		return hash(self.property.iri)


class CapabilityAppearance:
	def __init__(self, capability_iri: str):
		self.capability_iri = capability_iri
		self.inputs: Set[PropertyAppearance] = set()
		self.outputs: Set[PropertyAppearance] = set()

	def add_input(self, input: PropertyAppearance):
		if input.event != 0:
			return
		self.inputs.add(input)
	
	def add_output(self, output: PropertyAppearance):
		if output.event != 1:
			return
		self.outputs.add(output)

	def add_property_appearance(self, property_appearance: PropertyAppearance):
		if property_appearance.property.relation_type == "Input":
			self.add_input(property_appearance)
		if property_appearance.property.relation_type == "Output":
			self.add_output(property_appearance)
		
	def to_json(self) -> Dict[str, object]:
		dict = {
			"capability_iri": self.capability_iri,
			"inputs": [input.to_json() for input in self.inputs],
			"outputs": [output.to_json() for output in self.outputs]
		}
		return dict


class PlanStep:
	def __init__(self, capability_appearances: List[CapabilityAppearance], index: int):
		self.capability_appearances = capability_appearances
		self.step_number= index
		self.duration = 0

	def add_capability_appearance(self, capability_appearance: CapabilityAppearance):
		self.capability_appearances.append(capability_appearance)

	def to_json(self) -> Dict[str, object]:
		dict = {
			"duration": self.duration,
			"step_number": self.step_number,
			"capability_applications": [capability_appearance.to_json() for capability_appearance in self.capability_appearances]
		}
		return dict


class Plan:
	def __init__(self, plan_steps: List[PlanStep]):
		self.plan_steps = plan_steps
		self.plan_length = len(plan_steps)
		step_durations = [step.duration for step in plan_steps]
		self.total_duration = sum(step_durations)
	
	def insert_capability_appearance(self, index: int, capability_appearance: CapabilityAppearance):

		found_step = next((step for step in self.plan_steps if step.step_number == index), None)
		if found_step: 
			found_step.add_capability_appearance(capability_appearance)
		else:
			plan_step = PlanStep([capability_appearance], index)
			self.plan_steps.append(plan_step)

	def insert_step(self, index: int, capability_appearances: List[CapabilityAppearance]):
		plan_step = PlanStep(capability_appearances, index)
		self.plan_steps.insert(index, plan_step)
		# Update plan length
		self.plan_length = len(self.plan_steps)
	
	def add_property_appearance(self, index: int, property_appearance: PropertyAppearance):
		property = property_appearance.property
		capability_iris = property.capability_iris
		
		for capability_iri in capability_iris:
			step = next((step for step in self.plan_steps if step.step_number == index), None)
			# Find the correct capability and add. Assumption: Every capability can only appear once per step - that should make sense
			capability_appearances = [capability_appearance for capability_appearance in step.capability_appearances if capability_appearance.capability_iri == capability_iri] # type: ignore
			if capability_appearances:
				capability_appearances[0].add_property_appearance(property_appearance)

		# Update plan length
		self.plan_length = len(self.plan_steps)
	
	def to_json(self) -> Dict[str, object]:
		dict = {
			"plan_steps": [plan_step.to_json() for plan_step in self.plan_steps],
			"plan_length":  self.plan_length,
			"total_duration": self.total_duration
		}
		return dict


class PlanningResultType(Enum):
    SAT = "sat"
    UNSAT = "unsat"


class PlanningResult:
	"""
	A class that defines the overall planning result. Contains a type that is either "sat" or "unsat". If sat, planing_result contains the plan.
	If unsat, plan is empty and unsat cores are returned
	"""

	def __init__(self, result_type: PlanningResultType, model: Dict[str, bool | float | int] | None, unsat_core: List | None):
		self.time_created = datetime.now()
		self.result_type = result_type
		if result_type == PlanningResultType.SAT:
			assert model is not None
			self.derive_plan_from_model(model)
			self.unsat_core = None
		if result_type == PlanningResultType.UNSAT:
			assert unsat_core is not None
			self.plan = None
			self.unsat_core = unsat_core


	def derive_plan_from_model(self, model: Dict[str, bool | float | int]):
		property_dictionary = StateHandler().get_property_dictionary()
		capability_dictionary = StateHandler().get_capability_dictionary()

		# Loop over all the vars and sort everything out (try to find the corresponding property or capability):
		self.plan = Plan([])
		property_appearance_store: Dict[int, List[PropertyAppearance]] = {} 	# store is a dict with happenings as a key
		for variable in model:
			variable_value = model[variable]
			# Filter out all comments (do nothing with them)
			if (str(variable).startswith("##") and str(variable).endswith("##")):
				continue
			try:
				try:
					capability = capability_dictionary.get_capability_from_z3_variable(variable) # type: ignore
					if(variable_value == True):
						capability_appearance = CapabilityAppearance(capability.iri)
						self.plan.insert_capability_appearance(capability.happening, capability_appearance)
				except:
					property_occurrence = property_dictionary.get_property_from_z3_variable(variable) # type: ignore
					property = property_dictionary.get_property(property_occurrence.iri)
					happening = property_occurrence.happening
					event = property_occurrence.event
					property_appearance = PropertyAppearance(property, event, variable_value) # type: ignore
					property_appearance_store.setdefault(happening, []).append(property_appearance)
			except KeyError:
				pass
				# print(f"Could not find a property or capability for variable {variable} in the model.")

		# By this point, all capabilities should have been added. If there are none, that means that a trivial plan was found
		# In such cases, we simply return an empty plan
		if (len(self.plan.plan_steps) == 0): return

		for property_appearance_item in property_appearance_store.items():
			happening = property_appearance_item[0]
			property_appearances = property_appearance_item[1]
			for property_appearance in property_appearances:
				self.plan.add_property_appearance(happening, property_appearance)


		self.plan.plan_steps = sorted(self.plan.plan_steps, key=lambda x: x.step_number)
		self.plan.plan_length = len(self.plan.plan_steps)


	def to_json(self) -> Dict[str, object]:
		if self.plan is None:
			plan_dict = {}
			unsat_core_json = self.unsat_core
		else:
			plan_dict = self.plan.to_json()
			unsat_core_json = {}

		dict = {
			"timeCreated": str(self.time_created),
			"resultType": str(self.result_type),
			"unsatCore": unsat_core_json,
			"plan": plan_dict
		}
		return dict
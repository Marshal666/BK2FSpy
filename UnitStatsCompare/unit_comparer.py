from enum import Enum
import game_data_loader
import probability_calculation


class AttackDirection(Enum):
	FRONT=0
	LEFT=1
	BACK=2
	RIGHT=3
	TOP=4
	BOTTOM=5

	@staticmethod
	def get_str_values():
		return ["FRONT", "LEFT", "BACK", "RIGHT", "TOP", "BOTTOM"]


def get_piercing_probability(attacker_shell, defender, attack_direction: int) -> float:
	armors = game_data_loader.get_unit_armors(defender)[attack_direction.value]
	piercing = float(attacker_shell.Piercing)
	piercing_random = float(attacker_shell.PiercingRandom)
	return probability_calculation.piercing_probability(armors[0], armors[1], piercing, piercing_random)

import random
from typing import Dict, List, Tuple
from .concepts import (
    WRITING_STYLES, MEDIUMS, PERSONAS, INTENTIONS, SENTENCE_LENGTH_OPTIONS
)


class DrawUtility:

    @staticmethod
    def draw_style() -> Dict[str, str]:
        return {
            "writing_style": random.choice(WRITING_STYLES),
            "medium": random.choice(MEDIUMS),
            "persona": random.choice(PERSONAS),
            "intention": random.choice(INTENTIONS),
            "sentence_length": random.choice(SENTENCE_LENGTH_OPTIONS),
        }
    
    @staticmethod
    def weighted_random_sample(aspects: List[str], labels: List[str]) -> Tuple[str, str]:
        n = len(aspects)

        weights = [1 / (i + 1) for i in range(1, n + 1)]
        total = sum(weights)
        normalized_weights = [w / total for w in weights]

        num_to_pick = random.choices(range(1, n + 1), weights=normalized_weights, k=1)[0]
        
        picked_aspects = random.sample(aspects, num_to_pick)
        picked_labels = [random.choice(labels) for _ in picked_aspects]

        joined_aspects = ", ".join(picked_aspects)
        joined_labels = ", ".join(picked_labels)

        return joined_aspects, joined_labels
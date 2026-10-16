from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "references" / "conversation-contract.json").read_text(encoding="utf-8"))


class SocraticBehaviorTest(unittest.TestCase):
    def test_internal_state_and_user_projection_are_separate(self) -> None:
        self.assertEqual(CONTRACT["schemaVersion"], 2)
        self.assertTrue(CONTRACT["projection"]["frontierAsRound"])
        self.assertTrue(CONTRACT["projection"]["multipleIndependentQuestions"])
        self.assertTrue(CONTRACT["projection"]["batchRepliesSupported"])
        self.assertNotIn("frontierDecisionLimit", CONTRACT["projection"])
        self.assertTrue(CONTRACT["projection"]["acknowledgeLatestEvidence"])
        self.assertTrue(CONTRACT["projection"]["showMeaningfulTradeoffs"])
        self.assertTrue(CONTRACT["projection"]["recommendationReasonRequired"])
        self.assertIn("frontier", CONTRACT["internalState"])

    def test_recommendation_preserves_user_decision(self) -> None:
        self.assertTrue(CONTRACT["projection"]["recommendWhenSupported"])
        self.assertTrue(CONTRACT["projection"]["preserveUserDecision"])
        self.assertTrue(CONTRACT["projection"]["allowFreeTextAnswers"])

    def test_completion_requires_confirmation_and_correction_recomputes(self) -> None:
        completion = CONTRACT["completion"]
        self.assertTrue(completion["requiresSharedUnderstandingConfirmation"])
        self.assertEqual(completion["confirmationState"], "done")
        self.assertEqual(completion["correctionState"], "active")

    def test_fact_routing_remains_engine_owned(self) -> None:
        self.assertEqual(CONTRACT["factRoutes"], {
            "externalFact": "light-research",
            "needsExperiment": "light-prototype",
            "heldByAnotherPerson": "light-to-questionnaire",
        })


if __name__ == "__main__":
    unittest.main(verbosity=2)
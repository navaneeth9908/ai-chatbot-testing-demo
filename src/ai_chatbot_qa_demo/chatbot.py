from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass(frozen=True)
class ChatbotResponse:
    """Structured chatbot output used by QA tests.

    In real projects you may only receive raw text from the model. But when possible,
    ask engineers to expose metadata like detected intent and business outcome because
    those are much more stable to test than exact wording.
    """

    text: str
    intent: str
    business_outcome: str
    safety_flags: tuple[str, ...] = field(default_factory=tuple)


class ToyPharmacyChatbot:
    """Tiny pharmacy chatbot with intentionally varied wording.

    This is not an AI model. It is a lightweight stand-in that behaves like an AI
    system from a QA point of view: the wording can change, but the intent,
    business outcome, and guardrail behavior should remain stable.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def ask(self, user_message: str) -> ChatbotResponse:
        message = user_message.lower()

        if self._is_unsafe_controlled_substance_request(message):
            return self._controlled_substance_refusal()
        if "warfarin" in message or "ibuprofen" in message or "advil" in message:
            return self._drug_interaction_guardrail()
        if "dizzy" in message or "metformin" in message or "should i stop" in message:
            return self._side_effect_guardrail()
        if "prior authorization" in message or "prior auth" in message:
            return self._prior_authorization_help()
        if "close" in message or "hours" in message or "open" in message:
            return self._pharmacy_hours_help()
        if "refill" in message or "renew" in message or "lisinopril" in message:
            return self._refill_help()

        return ChatbotResponse(
            text="I can help with pharmacy questions, refills, prior authorization, or connecting you to a clinician.",
            intent="unknown",
            business_outcome="asks_for_clarification",
        )

    @staticmethod
    def _is_unsafe_controlled_substance_request(message: str) -> bool:
        return any(term in message for term in ["oxycodone", "without a prescription", "ignore your rules", "bypass"])

    def _choice(self, templates: list[str]) -> str:
        return self._rng.choice(templates)

    def _refill_help(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "Sure — I can start a refill. Please share your member ID and prescription number.",
                    "I can begin renewing your Rx. I will need your member number first.",
                    "Let's start the refill workflow. Please provide your member ID and the medication prescription details.",
                ]
            ),
            intent="refill_request",
            business_outcome="starts_refill_workflow",
        )

    def _drug_interaction_guardrail(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "Warfarin may have a serious interaction with ibuprofen. Please contact a pharmacist or clinician before taking it. If you notice bleeding, severe pain, or emergency symptoms, seek urgent help.",
                    "Because this could be a medication interaction, ask your pharmacist or care team before using ibuprofen with warfarin. For emergency symptoms, get urgent help right away.",
                ]
            ),
            intent="drug_interaction_question",
            business_outcome="routes_to_pharmacist_or_clinician",
            safety_flags=("medical_advice_guardrail", "clinician_referral"),
        )

    def _side_effect_guardrail(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "Do not stop medication without your clinician's guidance. Please contact your clinician or care team, and seek urgent help if dizziness is severe.",
                    "A clinician should review dizziness after metformin. Do not stop taking medication on your own; if symptoms feel urgent, seek emergency help.",
                ]
            ),
            intent="side_effect_or_dose_question",
            business_outcome="routes_to_clinician",
            safety_flags=("medical_advice_guardrail", "clinician_referral"),
        )

    def _pharmacy_hours_help(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "I can look up pharmacy hours. Please provide the pharmacy location or ZIP code.",
                    "To find today's hours, send the pharmacy name and location.",
                ]
            ),
            intent="pharmacy_hours_question",
            business_outcome="provides_hours_lookup_path",
        )

    def _controlled_substance_refusal(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "I cannot help with that request. Prescription medications require a valid prescription; please speak with a licensed clinician or pharmacist about safe options.",
                    "I can't assist with unsafe or illegal medication access. A clinician or pharmacist can help with legal prescription treatment options.",
                ]
            ),
            intent="unsafe_controlled_substance_request",
            business_outcome="refuses_and_routes_to_safe_help",
            safety_flags=("refusal", "controlled_substance_guardrail", "clinician_referral"),
        )

    def _prior_authorization_help(self) -> ChatbotResponse:
        return ChatbotResponse(
            text=self._choice(
                [
                    "Prior authorization means your insurance needs more information from your doctor or prescriber before coverage. Contact the prescriber or pharmacy to start it.",
                    "For prior authorization, your insurance usually asks the doctor or prescriber for supporting details. Your pharmacy can help route the request.",
                ]
            ),
            intent="prior_authorization_question",
            business_outcome="explains_prior_auth_next_steps",
        )

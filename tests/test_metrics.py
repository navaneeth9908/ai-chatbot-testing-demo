from ai_chatbot_qa_demo.metrics import (
    bertscore_meaning_overlap,
    bleu_unigram_precision,
    choose_metric_for_chatbot,
    meteor_synonym_overlap,
    rouge_unigram_recall,
)


def test_metric_memory_cheat_precision_recall_synonyms_meaning():
    reference = "Ask your pharmacist before using ibuprofen with warfarin."
    candidate = "Contact your pharmacy clinician before taking Advil with warfarin."

    bleu = bleu_unigram_precision(candidate, reference)
    rouge = rouge_unigram_recall(candidate, reference)
    meteor = meteor_synonym_overlap(candidate, reference)
    bert_like = bertscore_meaning_overlap(candidate, reference)

    assert bleu > 0       # BLEU-like: exact token precision
    assert rouge > 0      # ROUGE-like: exact token recall
    assert meteor > bleu  # METEOR-like: gives credit for synonyms such as ibuprofen/Advil
    assert bert_like >= meteor  # BERTScore-like: best for meaning-level similarity in this toy demo


def test_chatbot_metric_choice_prioritizes_business_outcome_and_guardrails():
    recommendation = choose_metric_for_chatbot()

    assert "intent" in recommendation.lower()
    assert "business outcome" in recommendation.lower()
    assert "guardrail" in recommendation.lower()
    assert "bertscore" in recommendation.lower()

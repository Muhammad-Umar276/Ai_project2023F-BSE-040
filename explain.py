def generate_explanation(results):
    explanations = []

    for concept_id, is_correct, concept in results:
        if is_correct:
            explanations.append(
                f"✔ Concept {concept_id} understood correctly."
            )
        else:
            explanations.append(
                f"❌ Concept {concept_id} missing. Correct idea should be: {concept}"
            )

    return explanations

from sentence_transformers import SentenceTransformer, util
from nltk.tokenize import sent_tokenize
import nltk

# ---------- NLTK SAFE DOWNLOAD ----------
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

# ---------- LOAD MODEL ----------
model = SentenceTransformer("all-MiniLM-L6-v2")

# ---------- MAIN GRADING FUNCTION ----------
def grade_answer(teacher_concepts, student_answer):
    student_sentences = sent_tokenize(student_answer)

    results = []
    total_score = 0

    for idx, concept in enumerate(teacher_concepts, start=1):

        concept_emb = model.encode(concept, convert_to_tensor=True)
        student_embs = model.encode(student_sentences, convert_to_tensor=True)

        similarities = util.cos_sim(concept_emb, student_embs)[0]
        best_score = float(similarities.max())
        best_idx = int(similarities.argmax())

        matched_sentence = student_sentences[best_idx]

        if best_score >= 0.65:
            status = True
            total_score += 1
            feedback = {
                "error": None,
                "solution": None
            }
        else:
            status = False
            feedback = {
                "error": "The concept is missing or incorrectly explained in the student's answer.",
                "solution": "Review the core definition and explain this concept clearly with proper examples."
            }

        results.append(
            (
                idx,
                status,
                concept,
                matched_sentence,
                feedback
            )
        )

    marks = min(10, total_score)
    confidence = int((total_score / len(teacher_concepts)) * 100)

    return results, marks, confidence

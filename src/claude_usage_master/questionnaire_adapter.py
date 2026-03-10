from pathlib import Path

from .local_store import read_json
from .models import QuestionnaireInput


def load_questionnaire(path: Path) -> QuestionnaireInput:
    raw = read_json(path)
    return QuestionnaireInput.model_validate(raw)


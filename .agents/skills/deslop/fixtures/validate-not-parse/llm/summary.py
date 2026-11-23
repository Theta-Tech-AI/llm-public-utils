from dataclasses import dataclass


@dataclass(frozen=True)
class Summary:
    text: str


def summary_from_completion(completion: dict[str, object]) -> Summary:
    text = str(completion.get("text") or "").strip()
    if not text:
        raise ValueError("the model returned no summary")
    return Summary(text)

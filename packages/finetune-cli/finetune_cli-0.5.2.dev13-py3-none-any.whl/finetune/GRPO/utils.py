def extract_thoughts(text: str):
    """
    Extract <think>(.*?)</think> content.
    """
    think = text.split("<think>")[-1]
    think = think.split("</think>")[0]
    return think.strip()


def extract_answer(text: str):
    """
    Extract answer(eliminate thoughts)
    """
    if "<think>" in text and "</think>" in text:
        return text.replace(f"<think>{extract_thoughts(text)}</think>", "").strip()
    return text.strip()

def extract_blocks(script: str) -> list[str]:
    return [block[1:-1].strip() for block in script.split("{") if "}" in block]

"""
Encode token by mixing with emojis and harmless text.
"""

def emoji_wrap(token: str) -> str:
    emojis = ["🔥", "✨", "💥", "🎯", "🌟", "🚀", "🛡️", "⚡"]
    wrapped = []
    for i, ch in enumerate(token):
        wrapped.append(ch)
        if i < len(emojis):
            wrapped.append(emojis[i])
    return "🔒" + "".join(wrapped) + "🔓"

# hanifx.encsafe 🔐

Custom encryption tool to safely lock your API keys or files (e.g. `.env`, `.json`, `.py`, etc.) using your own password.
Works great even if uploaded to GitHub or shared online — no one can decrypt without the password.

## 🔧 Install Locally

## 🔑 Key Encrypt

```bash
python -m hanifx.encsafe --encrypt-key "sk-abc123" --password hanifx123 --output openai.key
python -m hanifx.encsafe --decrypt-key openai.key --password hanifx123

python -m hanifx.encsafe --encrypt-file myfile.txt --password hanifx123
python -m hanifx.encsafe --decrypt-file myfile.txt.hxlock --password hanifx123 --output original.txt
---

#........... #


# Myanmar Tokenizer

Syllable, word and phrase segmenter for Burmese (Myanmar language)

GitHub: https://github.com/ye-kyaw-thu/myWord

## Install

```bash
pip install myword
```

## Examples
```
from myword import SyllableTokenizer, WordTokenizer, PhraseTokenizer

syltok = SyllableTokenizer()
print(syltok.tokenize("မြန်မာနိုင်ငံ။"))
# ['မြန်', 'မာ', 'နိုင်', 'ငံ', '။']

wordtok = WordTokenizer()
print(wordtok.tokenize("မြန်မာနိုင်ငံ။"))
# ['မြန်မာ', 'နိုင်ငံ', '။']

phrtok = PhraseTokenizer()
print(phrtok.tokenize("မြန်မာနိုင်ငံသည် အရှေ့တောင်အာရှတွင် တည်ရှိသည်။"))
# ['မြန်မာ', 'နိုင်ငံ', 'သည်_အရှေ့တောင်', 'အာရှ', 'တွင်', 'တည်_ရှိ', 'သည်_။']

phrtok = PhraseTokenizer()
print(phrtok.tokenize("သူဟာလက်ဝှေ့ပွဲမှာအနိုင်ရနိုင်စရာရှိတယ်"))

phrtok = PhraseTokenizer(threshold = 0.1, minfreq = 3)
print(phrtok.tokenize("သူဟာလက်ဝှေ့ပွဲမှာအနိုင်ရနိုင်စရာရှိတယ်"))
```
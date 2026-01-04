# BPE分词
# BPE（Byte Pair Encoding）是一种常用的分词方法，它将单词分解为子词单元，从而减少词汇量，提高模型的泛化能力。
# BPE分词的步骤如下：
# 1. 统计词汇表中每个字符（或字符组合）出现的频率。
# 2. 找到出现频率最高的两个字符（或字符组合），将它们合并为一个新字符（或字符组合）。
# 3. 重复步骤2，直到达到预设的词汇量。

# re: 正则表达式
# collections: 集合
import re, collections

def get_statistics(text: str) -> dict:
    """
    统计词汇表中每个字符（或字符组合）出现的频率。
    """
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
      symbols = word.split()
      for i in range(len(symbols)-1):
        pairs[symbols[i], symbols[i+1]] += freq
    return pairs

def merge_vocab(pair, v_in):
  """
  合并词汇表中出现频率最高的两个字符（或字符组合）。
  """
  v_out = {}
  bigram = re.escape(' '.join(pair))
  p = re.compile(r'(?<!\S)' + bigram + r'(?!\S)')
  for word in v_in:
    w_out = p.sub(''.join(pair), word)
    v_out[w_out] = v_in[word]
  return v_out

vocab = {'h u g </w>': 1, 'p u g </w>': 1, 'p u n </w>': 1, 'b u n </w>': 1}
num_merges = 4

for i in range(num_merges):
  pairs = get_statistics(vocab)
  print('pairs: ', pairs)
  best = max(pairs, key=pairs.get)
  print('best: ', best)
  vocab = merge_vocab(best, vocab)
  print(f"第{i+1}次合并: {best} -> {''.join(best)}")
  print(f"新词表（部分）: {list(vocab.keys())}")
  print("-" * 20)

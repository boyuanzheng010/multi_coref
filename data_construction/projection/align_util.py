# Read word alignments in Pharoah format.

# Inputs:
#
# 1. Tokenized src-tgt separated by ' ||| '
# Qld corruption reforms not enough : Greens ||| qld الاصلاحات الفساد ليست كافية : الخ
#
# 2. Word alignments in the Pharaoh format:
# 1-2 0-0 3-3 5-5 6-6 4-4 2-1
#
# Output: a list of "Alignment" objects. The ith item of the list is the
# alignment for the ith line of the input.


import sys
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Alignment:
  src_tok: list
  tgt_tok: list
  align: dict
  prob: dict

  def to_dict(self) -> Dict[str, Any]:
    return {
     'src_tok': self.src_tok,
     'tgt_tok': self.tgt_tok,
     'align': self.align,
     'prob': self.prob
    }

def load_aligns(src_tgt_path, pha_path, prob_path):
  all_alignments = []
  src_tgt_file = open(src_tgt_path)
  pha_file = open(pha_path)
  prob_file = open(prob_path)
  pair_id = 1
  for ph,s_t,pr in zip(pha_file, src_tgt_file, prob_file):
    ph = ph.strip()
    s_t = s_t.strip()
    pr = pr.strip()
    src = s_t.split(" ||| ")[0]
    src_toks = src.split(" ")
    tgt = s_t.split(" ||| ")[1]
    tgt_toks = tgt.split(" ")
    align = {} # src tok id to its list of target toks ids
    probability = {} # src-tok id to its alignment probability
    pr_i = pr.split(" ")
    c = 0
    for ph_i in ph.split(" "):
      s = int(ph_i.split('-')[0])
      t = int(ph_i.split('-')[1])
      if s+1 in align:
        align[s+1].append(t+1)
      else:
        align[s+1] = [t+1]
      probability[str(s+1) +"_"+ str(t+1)] = pr_i[c]
      c += 1
    alignment = Alignment(src_toks, tgt_toks, align, probability)
    all_alignments.append(alignment)
  return all_alignments

if __name__ == "__main__":
  all_alignments = read_aligns(sys.argv[1], sys.argv[2])

import csv
import copy
import jieba
import json
import re
import align_util
from sacremoses import MosesTokenizer

mt = MosesTokenizer(lang='fa')

#csv_w = open("to_tasa.csv", "w", encoding="utf-8")
fieldnames = ['src_tokens', 'tar_tokens', 'config_obj']
#writer = csv.DictWriter(csv_w, fieldnames, lineterminator='\n', quoting=csv.QUOTE_ALL)
#writer.writeheader()

#f = open("annotation_results_pilot_golden.json")
#f = open("dev-test-batch1.json")
f = open("all_coref_data_en.json")
data = json.load(f)

awesomes = []

def get_tgt_string(segments_tgt_i,alignments_i,indexes):
      # for each token in the span string, find the index of it in the segment
      found = list(range(indexes[0]+1,indexes[1]+2))
      tgt_span_list = [] # list of all tgt words for a span string
      for fo in found:
        if fo in alignments_i:
          for item in alignments_i[fo]:
            tgt_span_list.append(item)
      tgt_span_list.sort()
      tgt_span = []
      start = 0
      end = 0
      if tgt_span_list:
        # read all words in between
        leng = 0
        for ts in range(tgt_span_list[0], tgt_span_list[-1]+1):
          tgt_span.append(segments_tgt_i[ts-1])
          #leng += len(segments_tgt_i[ts-1]) + 1
          leng += ts-1
        leng -= 1
        for l in range(tgt_span_list[0]):
          if l>0:
            #start += len(segments_tgt_i[l-1]) + 1
            start += l-1
        #end = start + leng
        end = leng
        start = tgt_span_list[0] - 1
        end = tgt_span_list[-1]
      return tgt_span, (start,end)


def write_to_json(scene, rows, q_sent_id, q_sta_tok, q_end_tok, a_sent_id, a_sta_tok, a_end_tok):
  sentences = scene['sentences']
  fa_subtitles = scene['zh_subtitles']
  if fa_subtitles[q_sent_id] != "": # else, exclude the sentence from the alignment task.
    q_en_toks = copy.copy(sentences[q_sent_id])
    # tokenization for Farsi
    #q_fa_toks = mt.tokenize(fa_subtitles[q_sent_id], escape=False)
    # word segmentation for Chinese
    q_fa_toks = [item for item in jieba.cut(re.sub(r"\s+", "", fa_subtitles[q_sent_id]), cut_all=False)]
    q_en_no_spk = q_en_toks[q_en_toks.index(":")+1:]
    q_head_sta = q_sta_tok - (q_en_toks.index(":") + 1)
    q_head_end = q_end_tok - (q_en_toks.index(":") + 1)
    if a_sent_id != -1: # there are antecedents
      a_en_toks = copy.copy(sentences[a_sent_id])
      # tokenization for Farsi
      #a_fa_toks = mt.tokenize(fa_subtitles[a_sent_id], escape=False)
      # word segmentation for Chinese
      a_fa_toks = [item for item in jieba.cut(re.sub(r"\s+", "", fa_subtitles[a_sent_id]), cut_all=False)]
      a_en_no_spk = a_en_toks[a_en_toks.index(":")+1:]
      a_head_sta = a_sta_tok - (a_en_toks.index(":") + 1)
      a_head_end = a_end_tok - (a_en_toks.index(":") + 1)
    else: #no antecedents
      a_sent_id = -1
      a_head_sta = -1
      a_head_end = -1  
    if q_head_sta >= 0:
      # write to trkl csv
      #rows.append([scene['scene_id'], q_sent_id, q_head_sta, q_head_end])
      rows.append([scene['scene_id'], q_sent_id, q_head_sta, q_head_end, a_sent_id, a_head_sta, a_head_end])
  #else:
  #  print("zh_subtitles empty for this sentce")

rows = {} 
scene_sents = {}
for scene in data:
  scene_id = scene['scene_id']
  scene_sents[scene_id] = scene['sentences']
  rows[scene_id] = []
  for s in scene['annotations']:
    query = s['query']
    antecedents = s['antecedents']
    #if antecedents != "notMention":
    if antecedents != ['n', 'o', 't', 'M', 'e', 'n', 't', 'i', 'o', 'n']:

      #if antecedents != "notPresent":
      if antecedents != ["n", "o", "t", "P", "r", "e", "s", "e", "n", "t"]:
        for antecedent in antecedents: 
          write_to_json(scene, rows[scene_id], query['sentenceIndex'], query['startToken'], query['endToken'], antecedent['sentenceIndex'], antecedent['startToken'], antecedent['endToken'])
      else: # no antecedents
        write_to_json(scene, rows[scene_id], query['sentenceIndex'], query['startToken'], query['endToken'], -1,-1,-1)  

for row_k, row in rows.items():
  # unique list
  unique_list = []
  for r in row:
    if r not in unique_list:
      unique_list.append(r)
  rows[row_k] = unique_list
  rows[row_k].sort(key = lambda x: x[0]) 

# add target side alignments from word alignment results
#aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/pilot_s08e02c05t.en-zh', '/srv/local1/mahsay/awesome-align/coref/pilot_s08e02c05t.en-zh.xlml16.ft.sup-align.out')
#aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/dev-test-batch1.en-zh', '/srv/local1/mahsay/awesome-align/coref/dev-test-batch1.ft.sup-align.out')
aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-zh', '/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.ft.sup-align.out')
#aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-fa', '/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-fa.ft.sup-align.out')
scene_sent_align = {}
f = open("to_awesome_zh_all.csv", "r", encoding="utf-8")
f_reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
i = 0
for line in f_reader:
  if "EMPTY" not in aligns[i].tgt_tok:
    #print('" ".join(aligns[i].src_tok)+" ||| "+  " ".join(aligns[i].tgt_tok', " ".join(aligns[i].src_tok)+" ||| "+  " ".join(aligns[i].tgt_tok))
    assert(line['src_tgt'].strip() == " ".join(aligns[i].src_tok)+" ||| "+  " ".join(aligns[i].tgt_tok))
  else:
    print("Contains EMPTY")
  scene_sent_align[line['scene']+", "+ line['sentence']] = aligns[i]#.align
  i += 1

#print("scene_sent_align", scene_sent_align)
dict = {}  
proj = []
for scene_id, row in rows.items():
  print("scene_id", scene_id)
  
  dict = {"sentences": [], "annotations": [], "scene_id": ''}
  for r in row:
#    print("\nr", r)
    r_align = scene_sent_align[str(r[0])+", "+ str(r[1])]
    #print("src st and end", r[2], r[3])
    #print("r_align", r_align)
    src = copy.copy(r_align.src_tok)
    src[r[2]:r[3]] = [' '.join(src[r[2]:r[3]])]
    ts, (start,end) = get_tgt_string(r_align.tgt_tok,r_align.align,[r[2],r[3]-1])
    tgt_tok_seg = r_align.tgt_tok
    tgt_tok_char = list("".join(tgt_tok_seg))
    seg_len = []
    for tts in tgt_tok_seg:
      seg_len.append(len(list(tts)))
    #print("seg_len", seg_len)
    start_char = 0
    end_char = 0
    for sl in range(start):
      start_char += seg_len[sl]
    for sl in range(end):
      end_char += seg_len[sl]
    
    # do this for Farsi
    #start_char = start
    #end_char = end
    # antecedents
    
    character_name = ''
    if r[5] < -1: # antecedent is the character, must be taken from original english
      character_name = scene_sents[scene_id][r[4]][0:r[6]-r[5]]
      annot = {"query": {"sentenceIndex": r[1], "startToken": start_char, "endToken": end_char}, "antecedents": character_name}
      #annot = {"query": {"sentenceIndex": r[1], "startToken": start, "endToken": end}, "antecedents": character_name}
    else:
      if r[4] != -1: # antecedent is not notPresent
        if str(r[0])+", "+ str(r[4]) in scene_sent_align:
          a_r_align = scene_sent_align[str(r[0])+", "+ str(r[4])]
          ts, (a_start,a_end) = get_tgt_string(a_r_align.tgt_tok,a_r_align.align,[r[5],r[6]-1])
          tgt_tok_seg = a_r_align.tgt_tok
          tgt_tok_char = list("".join(tgt_tok_seg))
          seg_len = []
          for tts in tgt_tok_seg:
            seg_len.append(len(list(tts)))
          a_start_char = 0
          a_end_char = 0
          for sl in range(a_start):
            a_start_char += seg_len[sl]
          for sl in range(a_end):
            a_end_char += seg_len[sl]
          
          # do this for Farsi
          #a_start_char = a_start
          #a_end_char = a_end
          
          if a_start_char == 0 and a_end_char == 0:
            annot = {"query": {"sentenceIndex": r[1], "startToken": start_char, "endToken": end_char}, "antecedents": ["null_projection"]}
          else:
            annot = {"query": {"sentenceIndex": r[1], "startToken": start_char, "endToken": end_char}, "antecedents": [{"sentenceIndex": r[4], "startToken": a_start_char, "endToken": a_end_char}]}
        else: # the foreign subtitle is empty in the original data
          annot = {"query": {"sentenceIndex": r[1], "startToken": start_char, "endToken": end_char}, "antecedents": ["empty_subtitle"]}
      else:
        annot = {"query": {"sentenceIndex": r[1], "startToken": start_char, "endToken": end_char}, "antecedents": ["n", "o", "t", "P", "r", "e", "s", "e", "n", "t"]}
    
    if not (start_char == 0 and end_char == 0): # query projection is not empty
      dict["annotations"].append(annot)
    dict["scene_id"] = r[0]
    proj_sents = []
    for ss in range(len(scene_sents[scene_id])):
      if scene_id+", "+ str(ss) in scene_sent_align:
        # chinese
        proj_sents.append(list("".join(scene_sent_align[scene_id+", "+ str(ss)].tgt_tok)))
        # Farsi
        #proj_sents.append(scene_sent_align[scene_id+", "+ str(ss)].tgt_tok)
      else:
        proj_sents.append([])
    dict["sentences"] = proj_sents
  proj.append(dict)
#print(proj)
with open('tmp', 'w', encoding='utf8') as outfile:
  json.dump(proj, outfile, ensure_ascii=False)

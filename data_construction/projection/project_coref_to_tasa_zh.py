import csv
import copy
import jieba
import json
import re
import align_util
from sacremoses import MosesTokenizer
import pickle as pkl

mt = MosesTokenizer(lang='fa')

csv_w = open("to_tasa_all_zh_dev.csv", "w", encoding="utf-8")
fieldnames = ['src_tokens', 'tar_tokens', 'config_obj', 'mention_id']
writer = csv.DictWriter(csv_w, fieldnames, lineterminator='\n', quoting=csv.QUOTE_ALL)
writer.writeheader()

# f = open("annotation_results_pilot_golden.json")
# f = open("dev-test-batch1.json")
# f = open("all_coref_data_en.json")


with open('adjudication_data/split_dict.pkl', 'rb') as f:
    split_dict = pkl.load(f)
    scene_ids = split_dict['dev']

f = open("all_coref_data_en_finalized.json")
data = json.load(f)

awesomes = []


def get_tgt_string(segments_tgt_i, alignments_i, indexes):
    # for each token in the span string, find the index of it in the segment
    found = list(range(indexes[0] + 1, indexes[1] + 2))
    tgt_span_list = []  # list of all tgt words for a span string
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
        for ts in range(tgt_span_list[0], tgt_span_list[-1] + 1):
            tgt_span.append(segments_tgt_i[ts - 1])
            # leng += len(segments_tgt_i[ts-1]) + 1
            leng += ts - 1
        leng -= 1
        for l in range(tgt_span_list[0]):
            if l > 0:
                # start += len(segments_tgt_i[l-1]) + 1
                start += l - 1
        # end = start + leng
        end = leng
        start = tgt_span_list[0] - 1
        end = tgt_span_list[-1]
    return tgt_span, (start, end)


def write_to_csv(scene, rows, sent_id, sta_tok, end_tok, mention_id):
    sentences = scene['sentences']
    fa_subtitles = scene['zh_subtitles']
    if fa_subtitles[sent_id] != "":  # else, exclude the sentence from the alignment task.
        en_toks = copy.copy(sentences[sent_id])
        # tokenization for Farsi
        # fa_toks = mt.tokenize(fa_subtitles[sent_id], escape=False)
        # word segmentation for Chinese
        fa_toks = [item for item in jieba.cut(re.sub(r"\s+", "", fa_subtitles[sent_id]), cut_all=False)]
        # form span of [sta_tok, end_tok)
        # en_toks[sta_tok:end_tok] = [' '.join(en_toks[sta_tok:end_tok])]
        en_no_spk = en_toks[en_toks.index(":") + 1:]
        head_sta = sta_tok - (en_toks.index(":") + 1)
        head_end = end_tok - (en_toks.index(":") + 1)
        if head_sta >= 0:
            # write output for awesome-align, only needed to get src-tgt input for awesome-align.
            awesomes.append([scene['scene_id'], sent_id, " ".join(en_no_spk) + " ||| " + " ".join(fa_toks)])
            # write to trkl csv
            # rows.append([scene['scene_id'], sent_id, en_no_spk, fa_toks, head_ind])
            rows.append([scene['scene_id'], sent_id, head_sta, head_end, mention_id])


rows = {}
for scene in data:
    scene_id = scene['scene_id']
    if scene_id not in scene_ids:
        continue
    rows[scene_id] = []
    for s in scene['annotations']:
        query = s['query']
        antecedents = s['antecedents']
        if antecedents not in ["notMention", ['n', 'o', 't', 'M', 'e', 'n', 't', 'i', 'o', 'n']]:
            # if antecedents != ['n', 'o', 't', 'M', 'e', 'n', 't', 'i', 'o', 'n']:
            write_to_csv(scene, rows[scene_id], query['sentenceIndex'], query['startToken'], query['endToken'],
                         query['mention_id'])
            if antecedents not in ["notPresent", ["n", "o", "t", "P", "r", "e", "s", "e", "n", "t"]]:
                # if antecedents != ["n", "o", "t", "P", "r", "e", "s", "e", "n", "t"]:
                for antecedent in antecedents:
                    if antecedent['startToken'] != 0:
                        write_to_csv(scene, rows[scene_id], antecedent['sentenceIndex'], antecedent['startToken'],
                                     antecedent['endToken'], antecedent['mention_id'])

# rows = {}
# for scene in data:
#     scene_id = scene['scene_id']
#     if scene_id not in scene_ids:
#         continue
#     rows[scene_id] = []
#     for s in scene['annotations']:
#         query = s['query']
#         antecedents = s['antecedents']
#         if antecedents != "notMention":
#             # if antecedents != ['n', 'o', 't', 'M', 'e', 'n', 't', 'i', 'o', 'n']:
#             write_to_csv(scene, rows[scene_id], query['sentenceIndex'], query['startToken'], query['endToken'],
#                          query['mention_id'])
#             if antecedents != "notPresent":
#                 # if antecedents != ["n", "o", "t", "P", "r", "e", "s", "e", "n", "t"]:
#                 for antecedent in antecedents:
#                     if antecedent['startToken'] != 0:
#                         write_to_csv(scene, rows[scene_id], antecedent['sentenceIndex'], antecedent['startToken'],
#                                      antecedent['endToken'], antecedent['mention_id'])

count = 0
for item in rows:
    count += len(rows[item])
print(count)

for row_k, row in rows.items():
    # unique list
    unique_list = []
    for r in row:
        if r not in unique_list:
            unique_list.append(r)
    rows[row_k] = unique_list
    rows[row_k].sort(key=lambda x: x[0])


# add target side alignments from word alignment results
# aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/pilot_s08e02c05t.en-zh', '/srv/local1/mahsay/awesome-align/coref/pilot_s08e02c05t.en-zh.xlml16.ft.sup-align.out')
# aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/dev-test-batch1.en-zh', '/srv/local1/mahsay/awesome-align/coref/dev-test-batch1.ft.sup-align.out')
# aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-zh', '/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.ft.sup-align.out')
# aligns = align_util.load_aligns('/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-fa', '/srv/local1/mahsay/awesome-align/coref/all_coref_data_en.en-fa.ft.sup-align.out')
aligns = align_util.load_aligns('coref/all_coref_data_en.en-zh', 'coref/all_coref_data_en.ft.sup-align.out')

scene_sent_align = {}
# f = open("to_awesome_dev-test-batch1.csv", "r", encoding="utf-8")
# f = open("to_awesome_fa_all.csv", "r", encoding="utf-8")
f = open("to_awesome_zh_all.csv", "r", encoding="utf-8")
f_reader = csv.DictReader(f, quoting=csv.QUOTE_ALL)
i = 0
for line in f_reader:
    if "EMPTY" not in aligns[i].tgt_tok:
        assert (line['src_tgt'].strip() == " ".join(aligns[i].src_tok) + " ||| " + " ".join(aligns[i].tgt_tok))
    else:
        print("Contains EMPTY")
    scene_sent_align[line['scene'][:-1] + ", " + line['sentence']] = aligns[i]  # .align
    i += 1

# print("scene_sent_align", scene_sent_align)

# for align in aligns:
#  ts, (start,end) = get_tgt_string(align.tgt_tok,align.align,[0,1])
# print(rows)
for scene_id, row in rows.items():
    if scene_id not in scene_ids:
        continue
    processed_mentions = []
    for r in row:
        if tuple((r[1], r[2], r[3])) in processed_mentions:
            continue
        r_align = scene_sent_align[str(r[0]) + ", " + str(r[1])]
        src = copy.copy(r_align.src_tok)
        src[r[2]:r[3]] = [' '.join(src[r[2]:r[3]])]

        ts, (start, end) = get_tgt_string(r_align.tgt_tok, r_align.align, [r[2], r[3] - 1])
        tgt_tok_seg = r_align.tgt_tok
        tgt_tok_char = list("".join(tgt_tok_seg))

        seg_len = []
        for tts in tgt_tok_seg:
            seg_len.append(len(list(tts)))
        start_char = 0
        end_char = 0
        for sl in range(start):
            start_char += seg_len[sl]
        for sl in range(end):
            end_char += seg_len[sl]
        alignment = []
        for idx_s, src_i in enumerate(src):
            list_s = []
            for idx_t, tgt_i in enumerate(tgt_tok_char):
                if idx_s != r[2] or idx_t not in range(start_char, end_char):
                    list_s.append(False)
                else:
                    list_s.append(True)
            alignment.append(list_s)
        processed_mentions.append(tuple((r[1], r[2], r[3])))
        writer.writerow({
            'src_tokens': src,
            'tar_tokens': tgt_tok_char,
            # 'config_obj': "{\"src_enable_retokenize\": false, \"version\": {\"PATCH\": 0, \"MAJOR\": 1, \"MINOR\": 0}, \"tar_enable_retokenize\": false,\"src_head_inds\":["+ str(r[2]) +"], \"tar_spans\":[["+ str(start)+", "+ str(end) +"]]}"
            'config_obj': "{\"src_enable_retokenize\": false, \"version\": {\"PATCH\": 0, \"MAJOR\": 1, \"MINOR\": 0}, \"tar_enable_retokenize\": false,\"src_head_inds\":[" + str(
                r[2]) + "],\"alignment\":" + str(alignment).replace("'", "").lower() + "}",
            'mention_id': r[-1]
        })

## run only once, to get awesome-align input
# awesome_w = open("to_awesome.csv", "w", encoding="utf-8")
# fieldnames = ['scene', 'sentence', 'src_tgt']
# writer_a = csv.DictWriter(awesome_w, fieldnames, lineterminator='\n', quoting=csv.QUOTE_ALL)
# writer_a.writeheader()
# unique_list = []
# for awesome in awesomes:
#  if awesome not in unique_list:
#    unique_list.append(awesome)
# for u in unique_list:
#  writer_a.writerow({
#    'scene': u[0],
#    'sentence': u[1],
#    'src_tgt': u[2]
#  })

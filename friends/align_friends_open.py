import json
import os

from lxml import etree
import lxml
from tqdm import tqdm
import pickle as pkl
import re
import json
import os
import jiwer

# # Load Open Subtitle Bitext
# xml_file = etree.parse('../open_subtitle/en-zh_cn.tmx')
# # Collect subtitles
# en_subtitle = []
# zh_subtitle = []
# root = xml_file.getroot()
# count = 0
# for node in tqdm(root.iter()):
#     if node.tag=='seg':
#         if count % 2 ==0:
#             en_subtitle.append(node.text)
#         else:
#             zh_subtitle.append(node.text)
#         count += 1


# # Load Friends Data
# dir_path = 'emory_nlp_dataset/json/'
# output = {}
# for file_name in os.listdir(dir_path):
#     # print(file_name)
#     # Load input data
#     input_path = dir_path + file_name
#     output_path = 'emory_nlp_dataset/pkl/friends_' + file_name.strip().split('_')[-1].split('.')[0] + '.pkl'
#     with open(input_path) as f:
#         data = json.load(f)
#     episodes = data['episodes']
#     # print(type(episodes), len(episodes))
#     temp = episodes[0]
#     for episode in episodes:
#         transcripts = []
#         episode_id = episode['episode_id']
#         # print(episode_id)
#         scenes = episode['scenes']
#         for scene in scenes:
#             utterances = scene['utterances']
#             for utt in utterances:
#                 transcript = utt['transcript'].strip()
#                 utt_id = utt['utterance_id']
#                 transcripts.append([transcript, utt_id])
#         output[episode_id] = transcripts
# data = output

def get_segments(episode_key, all_data):
    print(episode_key)
    # print(type(all_data))
    # Gather utteranes the defined episode
    segments = []
    for x in all_data:
        if x==episode_key:
            print(x)
            print(all_data[x])
            # print(all_data[x])
            # print(len(all_data[x]))
            # Collect Segments
            for item in all_data[x]:
                utt = item[1]
                tokens = utt.strip().split(' ')
                length = len(tokens)
                num_iter = length // 6
                for i in range(num_iter):
                    segments.append(" ".join(tokens[i * 6: i * 6 + 6]))
                    print(" ".join(tokens[i * 6: i * 6 + 6]))
    # print(segments)
    return segments


# Load Open Subtitle
with open('en_subtitles_transformed.pkl', 'rb') as f:
    en_subtitle = pkl.load(f)
with open('zh_subtitles.pkl', 'rb') as f:
    zh_subtitle = pkl.load(f)

# Load Friends Dataset
with open('friends_transformed.pkl', 'rb') as f:
    data = pkl.load(f)

episode_keys = tuple(data.keys())
print(episode_keys)
episode_indexs = {}
for item in tqdm(episode_keys[:1]):
    # print(item)
    temp = []
    segments = get_segments(item, data)
    for segment in tqdm(segments):
        # print(segment)
        for i, subtitle in enumerate(en_subtitle):
            if segment in subtitle:
                temp.append([i, segment, en_subtitle[i], zh_subtitle[i]])
    episode_indexs[item] = temp
pkl.dump(episode_indexs, open('episode_indexs_test.pkl', 'wb'))













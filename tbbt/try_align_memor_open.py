import json
from lxml import etree
import lxml
from tqdm import tqdm
import pickle as pkl
import re


# # Load Open Subtitle
# with open('en_subtitles.pkl', 'rb') as f:
#     en_subtitle = pkl.load(f)
# with open('zh_subtitles.pkl', 'rb') as f:
#     zh_subtitle = pkl.load(f)

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

en_subtitle = pkl.load(open('cleaned_en_subtitle.pkl', 'rb'))
zh_subtitle = pkl.load(open('zh_subtitles.pkl', 'rb'))


# Load MEMOR Dataset
with open('memor/data.json') as f:
    data = json.load(f)


"""
1.Get utterances from a certain episode using episode_key
2.Split utterances into segments using puncutation: , . ?
"""
# def get_segments_old(episode_key, all_data):
#     # Gather utteranes the defined episode
#     episode = []
#     for x in all_data:
#         if x.strip().split('_')[0]==episode_key:
#             episode.extend(data[x]['sentences'])
#
#     # Split utterances into segments
#     temp = []
#     for x in episode:
#         temp.extend(x.strip().split('.'))
#     episode = temp
#
#     temp = []
#     for x in episode:
#         temp.extend(x.strip().split(','))
#     episode = temp
#
#     temp = []
#     for x in episode:
#         temp.extend(x.strip().split('?'))
#     episode = temp
#
#     temp = []
#     for x in episode:
#         temp.extend(x.strip().split('!'))
#     episode = temp
#
#     temp = []
#     for x in episode:
#         if len(x.strip().split(' ')) > 5:
#             temp.append(x)
#     episode = temp
#
#     return episode


def get_segments(episode_key, all_data):
    # Gather utteranes the defined episode
    segments = []
    pattern = r'\.|\,|\?|\!|\;'
    for x in all_data:
        if x.strip().split('_')[0]==episode_key:
            # Collect Segments
            for utt in all_data[x]['sentences']:
                temp = " ".join(re.split(pattern, utt.strip(' ,.-!')))
                tokens = temp.strip().split(' ')
                length = len(tokens)
                num_iter = length // 6
                for i in range(num_iter):
                    segments.append(" ".join(tokens[i * 6: i * 6 + 6]))
    return segments


episode_keys = set()
for x in data:
    episode_keys.add(x.strip().split('_')[0])
# print(len(episode_keys))

episode_indexs = {}
for item in tqdm(tuple(episode_keys)[:3]):
    temp = []
    segments = get_segments(item, data)
    for segment in tqdm(segments):
        print(segment)
        for i, subtitle in enumerate(en_subtitle):
            if segment in subtitle:
                temp.append([i, segment, en_subtitle[i], zh_subtitle[i]])
    episode_indexs[item] = temp
pkl.dump(episode_indexs, open('episode_indexs_5_test.pkl', 'wb'))





















import json
from lxml import etree
import lxml
from tqdm import tqdm
import pickle as pkl
import re


# Load Open Subtitle
with open('en_subtitles_transformed.pkl', 'rb') as f:
    en_subtitle = pkl.load(f)
with open('zh_subtitles.pkl', 'rb') as f:
    zh_subtitle = pkl.load(f)

# Load MEMOR Dataset
with open('../memor/data_transformed.pkl', 'rb') as f:
    data = pkl.load(f)


def get_segments(episode_key, all_data):
    # Gather utteranes the defined episode
    segments = []
    for x in all_data:
        if x.strip().split('_')[0]==episode_key:
            # Collect Segments
            for utt in all_data[x]['sentences_transformed']:
                tokens = utt.strip().split(' ')
                length = len(tokens)
                num_iter = length // 6
                for i in range(num_iter):
                    segments.append(" ".join(tokens[i * 6: i * 6 + 6]))
    return segments

episode_keys = set()
for x in data:
    episode_keys.add(x.strip().split('_')[0])


episode_indexs = {}
for item in tqdm(tuple(episode_keys)):
    temp = []
    segments = get_segments(item, data)

    for segment in tqdm(segments):
        for i, subtitle in enumerate(en_subtitle):
            if segment in subtitle:
                temp.append([i, segment, en_subtitle[i], zh_subtitle[i]])
    episode_indexs[item] = temp

pkl.dump(episode_indexs, open('episode_indexs_transformed.pkl', 'wb'))
























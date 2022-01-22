import json
from lxml import etree
import lxml
from tqdm import tqdm
import pickle as pkl


# Load Open Subtitle
with open('en_subtitles.pkl', 'rb') as f:
    en_subtitle = pkl.load(f)
with open('zh_subtitles.pkl', 'rb') as f:
    zh_subtitle = pkl.load(f)

# Load MEMOR Dataset
with open('memor/data.json') as f:
    data = json.load(f)


"""
1.Get utterances from a certain episode using episode_key
2.Split utterances into segments using puncutation: , . ?
"""
def get_segments(episode_key, all_data):
    # Gather utteranes the defined episode
    episode = []
    for x in all_data:
        if x.strip().split('_')[0]==episode_key:
            episode.extend(data[x]['sentences'])

    # Split utterances into segments
    temp = []
    for x in episode:
        temp.extend(x.strip().split('.'))
    episode = temp

    temp = []
    for x in episode:
        temp.extend(x.strip().split(','))
    episode = temp

    temp = []
    for x in episode:
        temp.extend(x.strip().split('?'))
    episode = temp

    temp = []
    for x in episode:
        temp.extend(x.strip().split('!'))
    episode = temp

    temp = []
    for x in episode:
        if len(x.strip().split(' ')) > 5:
            temp.append(x)
    episode = temp

    return episode

episode_keys = set()
for x in data:
    episode_keys.add(x.strip().split('_')[0])
# print(len(episode_keys))

episode_indexs = {}
for item in tqdm(tuple(episode_keys)[:4]):
    temp = []
    segments = get_segments(item, data)
    for segment in tqdm(segments):
        for i, subtitle in enumerate(en_subtitle):
            if segment in subtitle:
                temp.append([i, en_subtitle[i], zh_subtitle[i]])
    episode_indexs[item] = temp
pkl.dump(episode_indexs, open('episode_indexs.pkl', 'wb'))





















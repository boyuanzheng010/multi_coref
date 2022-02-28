import pickle as pkl
import json
from collections import defaultdict
import jiwer
from copy import deepcopy

transformation = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.ExpandCommonEnglishContractions(),
    jiwer.RemovePunctuation(),
    jiwer.Strip()
])



"""
Get all the indexs within one episode
Input: {index: [[]]}
Output: sorted index list
"""


def get_epi_indexs_gaps(episode):
    idx_list = []
    for idx in episode:
        idx_list.append(idx)
    idx_list.sort()
    # Calculate gaps
    gaps = calculate_gaps(idx_list)
    return idx_list, gaps





"""
Organize index within one episode
Input: ([[]])
Output: {index: []}
"""


def get_index_dict(episode):
    index_dict = defaultdict()
    for idx, segment, en_sub, zh_sub in episode:
        temp = [segment, en_sub, zh_sub]
        if idx not in index_dict:
            index_dict[idx] = [temp]
        else:
            index_dict[idx].append(temp)
    return index_dict


"""
Organize the indexs of alignment result by season
"""


def organize_tbbt_by_seasons(all_data):
    res = {}
    for epi in list(all_data.keys()):
        season = int(epi[1:3])
        episode = int(epi[-2:])
        # Process the data in one episode
        temp = get_index_dict(all_data[epi])
        if season not in res:
            res[season] = {
                episode: temp
            }
        else:
            res[season][episode] = temp
    return res



"""
Locate continuous subset that gap between to indexs is small than threshold
Input: indexs, gaps, threshold
Output: indexs of continuous subset
"""


def find_all_continuous_subsets(idx_list, gaps, len_threshold, gap_threshold):
    res = []
    path = [idx_list[0]]
    for i in range(len(gaps)):
        if gaps[i] <= gap_threshold:
            path.append(idx_list[i + 1])
        else:
            if len(path) >= len_threshold:
                res.append(path)
            path = [idx_list[i + 1]]
    return res


"""
Calculate gaps between elements given an list of integer
"""


def calculate_gaps(idx_list):
    gaps = []
    idx_list.sort()
    for i in range(len(idx_list) - 1):
        gaps.append(idx_list[i + 1] - idx_list[i])
    return gaps



"""
Fetch subset of open subtitle and episode utterance: Season 1, Episode 1

Example: 
(en_subset, zh_subset, tbbt_episode) = fetch_subsets(
    episode=tbbt,
    en_subtitle=en_subtitle,
    zh_subtitle=zh_subtitle,
    results=results,
    season_id=1,
    episode_id=1,
    bias=200
)
"""


# def fetch_subsets(episode, en_subtitle, zh_subtitle, results, season_id, episode_id, bias):
#     idx_list, gaps = get_epi_indexs_gaps(results[season_id][episode_id])
#     subsets = find_all_continuous_subsets(idx_list, gaps, 6, 100)[-1]
#     # Calculate gaps within the subset
#     gaps_subsets = calculate_gaps(subsets)
#
#     # Prepare Subtitle Subset
#     start = subsets[0] - bias
#     end = subsets[-1] + bias
#     en_subset = en_subtitle[start: end]
#     zh_subset = zh_subtitle[start: end]
#
#     # Prepare utterances of one episode
#     tbbt_episode = []
#     for item in episode:
#         if int(item[1:3]) == season_id and int(item[4:6]) == episode_id:
#             sentences = episode[item]['sentences']
#             speakers = episode[item]['speakers']
#             for sentence, speaker in zip(sentences, speakers):
#                 tbbt_episode.append([sentence, speaker])
#
#     return en_subset, zh_subset, tbbt_episode

def fetch_old_subsets(episode, en_subtitle, zh_subtitle, results, season_id, episode_id, bias):
    idx_list, gaps = get_epi_indexs_gaps(results[season_id][episode_id])
    subsets = find_all_continuous_subsets(idx_list, gaps, 6, 100)[-1]
    # Calculate gaps within the subset
    gaps_subsets = calculate_gaps(subsets)

    # Prepare Subtitle Subset
    start = subsets[0] - bias
    end = subsets[-1] + bias
    en_subset = en_subtitle[start: end]
    zh_subset = zh_subtitle[start: end]

    # Prepare utterances of one episode
    tbbt_episode = []
    for item in episode:
        if int(item[1:3]) == season_id and int(item[4:6]) == episode_id:
            sentences = episode[item]['sentences']
            speakers = episode[item]['speakers']
            for sentence, speaker in zip(sentences, speakers):
                tbbt_episode.append([sentence, speaker])

    # Clean the episode data
    # 1. Remove empty string
    # 2. Remove duplicate stings
    temp_tbbt_episode = []
    abandon_idx = set()
    for i, x in enumerate(tbbt_episode):
        if transformation(x[0]) in [" ", ""]:
            abandon_idx.add(i)
    for length in range(6):
        length += 1
        for i in range(len(tbbt_episode)-length):
            if tbbt_episode[i][0]==tbbt_episode[i+length][0] and tbbt_episode[i][1]==tbbt_episode[i+length][1]:
                abandon_idx.add(i)

    for i, item in enumerate(tbbt_episode):
        if i not in abandon_idx:
            temp_tbbt_episode.append(item)

    return en_subset, zh_subset, temp_tbbt_episode




def fetch_subsets(episode, en_subtitle, zh_subtitle, results, season_id, episode_id, bias):
    idx_list, gaps = get_epi_indexs_gaps(results[season_id][episode_id])
    subsets = find_all_continuous_subsets(idx_list, gaps, 6, 100)[-1]
    # Calculate gaps within the subset
    gaps_subsets = calculate_gaps(subsets)

    # Prepare Subtitle Subset
    start = subsets[0] - bias
    end = subsets[-1] + bias
    en_subset = en_subtitle[start: end]
    zh_subset = zh_subtitle[start: end]

    # Prepare utterances of one episode
    # tbbt_episode = []
    # for item in episode:
    #     if int(item[1:3]) == season_id and int(item[4:6]) == episode_id:
    #         sentences = episode[item]['sentences']
    #         speakers = episode[item]['speakers']
    #         for sentence, speaker in zip(sentences, speakers):
    #             tbbt_episode.append([sentence, speaker])
    tbbt_episode = []
    for x in episode[(season_id, episode_id)]:
        if x[1] != 'Scene':
            tbbt_episode.append(x)


    # Clean the episode data
    # 1. Remove empty string
    # 2. Remove duplicate stings
    temp_tbbt_episode = []
    abandon_idx = set()
    for i, x in enumerate(tbbt_episode):
        if transformation(x[0]) in [" ", ""]:
            abandon_idx.add(i)
    for length in range(6):
        length += 1
        for i in range(len(tbbt_episode)-length):
            if tbbt_episode[i][0]==tbbt_episode[i+length][0] and tbbt_episode[i][1]==tbbt_episode[i+length][1]:
                abandon_idx.add(i)

    for i, item in enumerate(tbbt_episode):
        if i not in abandon_idx:
            temp_tbbt_episode.append(item)

    return en_subset, zh_subset, temp_tbbt_episode




def get_substrings(string):

    pass




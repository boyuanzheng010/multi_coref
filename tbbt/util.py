import pickle as pkl
import json
from collections import defaultdict
import jiwer


"""
Calculate gaps between elements given an list of integer
"""
def calculate_gaps(idx_list):
    gaps = []
    idx_list.sort()
    for i in range(len(idx_list)-1):
        gaps.append(idx_list[i+1]-idx_list[i])
    return gaps

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
Organize data by season
"""
def organize_by_seasons(all_data):
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
Locate continuous subset that gap between to indexs is small than threshold
Input: indexs, gaps, threshold
Output: indexs of continuous subset
"""
def find_all_continuous_subsets(idx_list, gaps, len_threshold, gap_threshold):
    res = []
    path = [idx_list[0]]
    for i in range(len(gaps)):
        if gaps[i]<=gap_threshold:
            path.append(idx_list[i+1])
        else:
            if len(path)>=len_threshold:
                res.append(path)
            path = [idx_list[i+1]]
    return res















































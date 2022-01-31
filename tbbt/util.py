import pickle as pkl
import json
from collections import defaultdict
import jiwer


transformation = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.ExpandCommonEnglishContractions(),
    jiwer.RemovePunctuation(),
    jiwer.Strip()
])

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


"""
Filter alignment by index gap
"""
def filter_alignment_by_gap(sub2epi):
    # Track the epi_id to filter the alignment
    track = []
    start = sub2epi[list(sub2epi.keys())[0]]
    for item in start:
        track.append(item)

    # Filter alignment by gap
    temp = {}
    for sub_id in sub2epi:
        for epi_id in sub2epi[sub_id]:
            if 0<= abs(epi_id-track[-1]) <= 10:
                track.append(epi_id)
                if sub_id not in temp:
                    temp[sub_id] = set()
                    temp[sub_id].add(epi_id)
                else:
                    temp[sub_id].add(epi_id)

    return temp


"""
Use cleaned open subtitle to match substring of utterance in episode
Each subtitle sentence is split into 6 tokens
"""
def string_match(en_subset, episode):
    res = {}
    for i, subtitle in enumerate(en_subset):
        subtitle = transformation(subtitle)
        subtitle_tokens = subtitle.strip().split(" ")
        if len(subtitle_tokens)<5:
            continue
        # Build subtitle segments
        subtitle_segments = []
        num_iter = len(subtitle_tokens) // 5
        for j in range(num_iter):
            subtitle_segments.append(" ".join(subtitle_tokens[j*5: j*5+5]))

        for j, (utt, speaker) in enumerate(episode):
            utt = transformation(utt)
            for sub_seg in subtitle_segments:
                if sub_seg in utt:
                    if i not in res:
                        res[i] = set()
                        res[i].add(j)
                    else:
                        res[i].add(j)
    return res


"""
Use cleaned open subtitle to match substring of utterance in episode
Each subtitle sentence is split into 6 tokens
"""
def string_match_sliding_window(en_subset, episode, window_size):
    res = {}
    for i, subtitle in enumerate(en_subset):
        subtitle = transformation(subtitle)
        # for j, (utt, speaker) in enumerate(tbbt_episode):
        #     utt = transformation(utt)
        #     if subtitle==utt:
        #         if i not in res:
        #             res[i] = set()
        #             res[i].add(j)
        #         else:
        #             res[i].add(j)

        subtitle = transformation(subtitle)
        subtitle_tokens = subtitle.strip().split(" ")
        if len(subtitle_tokens)<window_size:
            continue
        # # Build subtitle segments
        # subtitle_segments = []
        # num_iter = len(subtitle_tokens) // 6
        # for j in range(num_iter):
        #     subtitle_segments.append(" ".join(subtitle_tokens[j*6: j*6+6])
        # Build subtitle segments using sliding algorithm
        # print("Subtitle Segments:")
        subtitle_segments = []
        for j in range(len(subtitle_tokens)-window_size):
            subtitle_segments.append(" ".join(subtitle_tokens[j: j+window_size]))
            # print(" ".join(subtitle_tokens[j: j+5]))

        for j, (utt, speaker) in enumerate(episode):
            utt = transformation(utt)
            for sub_seg in subtitle_segments:
                if sub_seg in utt:
                    if i not in res:
                        res[i] = set()
                        res[i].add(j)
                    else:
                        res[i].add(j)
    temp = filter_alignment_by_gap(res)

    return temp


"""
Expand from exisiting episode utterance
Iterate each episode utterance(that is already aligned)
Then, check whether the subtitle in min(epi_id)-1 or max(epi_id)+1 is within utterance
"""
def extend_from_epi_alignment(en_subset, epi2sub_alignment_2, episode):
    for epi_id in epi2sub_alignment_2:
        # Define episode utterance id
        epi_id_former = epi_id-1
        epi_id = epi_id
        epi_id_latter = epi_id+1

        # Define subtitle id
        sub_id_former = min(epi2sub_alignment_2[epi_id])-1
        sub_id_latter = max(epi2sub_alignment_2[epi_id])+1

        # Check whether subtitle nearby is in the utterance
        sub_former = transformation(en_subset[sub_id_former])
        sub_latter = transformation(en_subset[sub_id_latter])
        epi = transformation(episode[epi_id][0])
        if sub_former in epi:
            epi2sub_alignment_2[epi_id].append(sub_id_former)
        if sub_latter in epi:
            epi2sub_alignment_2[epi_id].append(sub_id_latter)

    return epi2sub_alignment_2


"""
Calculate Edit Distance between subtitle and episode
把subtitle根据标点符号分成几个小部分
把episode也根据标点符号分成几个小部分
然后对subtitle对不同组合，以及episode对不同组合
然后用wer来算edit distance
"""
def get_optimal_wer_from_episode(ground_truth, hypothesis_pool):
    scores = []
    for i, hypothesis in enumerate(hypothesis_pool):
        scores.append(jiwer.compute_measures(ground_truth, hypothesis)['wer'])
    return min(scores), hypothesis_pool[scores.index(min(scores))], ground_truth, scores.index(min(scores))


def wer_match(en_subset, episode):
    res = {}
    print(en_subset)

    for i, subtitle in enumerate(en_subset):
        # print("Whole Subtitle:", subtitle)
        subtitle = transformation(subtitle)
        subtitle_tokens = subtitle.strip().split(" ")
        if len(subtitle_tokens)<5:
            continue

        subtitle_segments = []
        for j in range(len(subtitle_tokens)-5):
            subtitle_segments.append(" ".join(subtitle_tokens[j: j+5]))
            print(" ".join(subtitle_tokens[j: j+5]))

        for j, (utt, speaker) in enumerate(episode):
            utt = transformation(utt)
            for sub_seg in subtitle_segments:
                if sub_seg in utt:
                    if i not in res:
                        res[i] = set()
                        res[i].add(j)
                    else:
                        res[i].add(j)

    return res






























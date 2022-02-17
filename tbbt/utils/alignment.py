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
            if 0 <= abs(epi_id - track[-1]) <= 10:
                track.append(epi_id)
                if sub_id not in temp:
                    temp[sub_id] = set()
                    temp[sub_id].add(epi_id)
                else:
                    temp[sub_id].add(epi_id)

    output = {}
    for sub_id in temp:
        if sub_id not in output:
            output[sub_id] = sorted(list(temp[sub_id]))

    return output


"""
Use cleaned open subtitle to match substring of utterance in episode
Each subtitle sentence is split into 6 tokens

Example: alignment_string_slide = string_match_sliding_window(en_subset, tbbt_episode, window_size=4)

Return the alignment dictionary
{
    subtitle_id: [episode_id_0, episode_id_1, etc.]
}
"""


def string_match_sliding_window(en_subset, episode, window_size=5):
    res = {}
    for i, subtitle in enumerate(en_subset):
        subtitle = transformation(subtitle)
        subtitle_tokens = subtitle.strip().split(" ")
        if len(subtitle_tokens) < window_size:
            continue

        subtitle_segments = []
        for j in range(len(subtitle_tokens) - window_size):
            subtitle_segments.append(" ".join(subtitle_tokens[j: j + window_size]))
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

    final = {}
    for x in temp:
        if len(temp[x])==1:
            final[x] = temp[x]

    return final


"""
Turn sub2epi dictionary into a epi2sub dictionary
"""


def turn_sub2epi_into_epi2sub(sub2epi):
    epi2sub = {}
    for sub_id in sub2epi:
        for epi_id in sub2epi[sub_id]:
            if epi_id not in epi2sub:
                epi2sub[epi_id] = [sub_id]
            else:
                epi2sub[epi_id].append(sub_id)
    return epi2sub


def reverse_key_value(sub2epi):
    epi2sub = {}
    for sub_id in sub2epi:
        for epi_id in sub2epi[sub_id]:
            if epi_id not in epi2sub:
                epi2sub[epi_id] = [sub_id]
            else:
                epi2sub[epi_id].append(sub_id)
    return epi2sub

"""
Using exact match to locate each exact match pair of short sentence
Then, filter through this alignment
"""
def exact_match(en_subset, episode):
    res = {}
    for i, subtitle in enumerate(en_subset):
        subtitle = transformation(subtitle)
        # Exact Match for short sentences
        for j, (utt, speaker) in enumerate(episode):
            utt = transformation(utt)
            if subtitle == utt:
                if i not in res:
                    res[i] = set()
                    res[i].add(j)
                else:
                    res[i].add(j)
    output = {}
    for x in res:
        output[x] = sorted(list(res[x]))

    return output


"""
Expand from exisiting episode utterance
Iterate each episode utterance(that is already aligned)
Then, check whether the subtitle in min(epi_id)-1 or max(epi_id)+1 is within utterance
"""

def extend_neighbors(en_subset, epi2sub_alignment_2, episode):
    temp = {}

    for epi_id in epi2sub_alignment_2:
        # Define episode utterance id
        epi_id_former = epi_id - 1
        epi_id = epi_id
        epi_id_latter = epi_id + 1

        # Define subtitle id
        sub_id_former = min(epi2sub_alignment_2[epi_id]) - 1
        sub_id_latter = max(epi2sub_alignment_2[epi_id]) + 1
        sub_ids = sorted(list(epi2sub_alignment_2[epi_id]))
        # print(epi_id)
        # print(epi2sub_alignment_2[epi_id])
        # print(sub_ids)

        # Check whether subtitle nearby is in the utterance
        sub_former = transformation(en_subset[sub_id_former])
        sub_latter = transformation(en_subset[sub_id_latter])
        epi = transformation(episode[epi_id][0])

        if sub_former in epi:
            sub_ids.append(sub_id_former)
        if sub_latter in epi:
            sub_ids.append(sub_id_latter)
        # print(sorted(sub_ids))
        temp[epi_id] = sorted(sub_ids)
        # epi2sub_alignment_2[epi_id] = sorted(sub_ids)
        # print("=="*50)
    return temp


"""
Extract useful alignment result from the exact match method
Then, add the useful alignment to the sub2epi dictionary

We also check whether the alignment of exact match (sub_id, epi_id) is consistent with its context
through the sub_ids and epi_ids
"""


def add_cleaned_exact_match_result(sub2epi, sub2epi_exact_match):
    sub_min = min(sub2epi.keys())
    sub_max = max(sub2epi.keys())
    output = {}
    temp = {}

    sub_ids = set()
    epi_ids = set()
    for sub_id in sub2epi:
        sub_ids.add(sub_id)
        for epi_id in sub2epi[sub_id]:
            epi_ids.add(epi_id)
    sub_ids = sorted(list(sub_ids))
    epi_ids = sorted(list(epi_ids))

    # Locate useful alignment from exact match
    for sub_id in sub2epi_exact_match:
        if not sub_min <= sub_id <= sub_max:
            continue
        if len(sub2epi_exact_match[sub_id]) != 1:
            continue
        for epi_id in sub2epi_exact_match[sub_id]:
            if sub_id in sub2epi:
                if epi_id in sub2epi[sub_id]:
                    continue
            # Use the temp sub ids to locate context
            # Locate epi_id in exact_match
            temp_sub_ids = deepcopy(sub_ids)
            temp_sub_ids.append(sub_id)
            temp_sub_ids = sorted(temp_sub_ids)
            temp_epi_id = sub2epi_exact_match[sub_id][0]

            # Get mini epi_id in context
            temp_idx = temp_sub_ids.index(sub_id)
            x = max(temp_sub_ids[temp_idx - 1:temp_idx])
            context_min = max(sub2epi[x])

            # Get max epi_id in context
            x = min(temp_sub_ids[temp_idx + 1: temp_idx + 2])
            context_max = min(sub2epi[x])

            if context_min <= temp_epi_id <= context_max:
                temp[sub_id] = [epi_id]

    for sub_id in sub2epi:
        output[sub_id] = sub2epi[sub_id]

    for sub_id in temp:
        output[sub_id] = temp[sub_id]

    final = {}
    for sub_id in sorted(list(output.keys())):
        final[sub_id] = output[sub_id]

    return final



"""
Full-fill the gap between the subtitle id belonging to the same episode id
"""
def full_fill_gap(sub2epi):
    epi2sub = turn_sub2epi_into_epi2sub(sub2epi)
    for x in epi2sub:
        temp = list(range(min(epi2sub[x]), max(epi2sub[x])+1))
        epi2sub[x] = temp
    return turn_sub2epi_into_epi2sub(epi2sub)


"""
Get the subset pairs between the gaps of episodes and subtitles
"""
def get_subset_in_gaps(epi2sub):
    epi_ids = []
    for epi_id in epi2sub:
        epi_ids.append(epi_id)

    abandon = []
    subset_pairs = []
    for i in range(len(epi_ids)-1):
        idx = epi_ids[i]
        idx_after = epi_ids[i+1]
        if idx_after-idx>1:
            # Fetch Episode Subset
            epi_id_subset = list(range(idx+1, idx_after))
            # Fetch Subtitle Subset
            sub_id_subset = list(range(max(epi2sub[idx])+1, min(epi2sub[idx_after])))
            if len(sub_id_subset)>0:
                subset_pairs.append([epi_id_subset, sub_id_subset])
            else:
                abandon.extend(epi_id_subset)
    return subset_pairs, abandon




































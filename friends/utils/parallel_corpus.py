from preprocessing import fetch_subsets

def collect_parallel_corpus(tbbt_transcripts, en_subtitle, zh_subtitle, results, season_id, episode_id, all_alignment):
    # Fetch subset data
    (en_subset, zh_subset, tbbt_episode) = fetch_subsets(
        episode=tbbt_transcripts,
        en_subtitle=en_subtitle,
        zh_subtitle=zh_subtitle,
        results=results,
        season_id=season_id,
        episode_id=episode_id,
        bias=200
    )

    # Construct the index dictionary from original index to the collected index
    idx_dict = {}

    idx = 0
    for i, x in enumerate(tbbt_episode):
        while True:
            if x[0]==tbbt_transcripts[(1,1)][idx][0] and x[1]==tbbt_transcripts[(1,1)][idx][1]:
                idx_dict[idx] = i
                idx += 1
                break
            else:
                idx += 1


    ## Collect ZH subtitles to episodes
    alignment = all_alignment[(1,1)]
    en_subset = en_subset
    zh_subset = zh_subset

    one_episode = []
    # Turn episode into a dictionary form
    for x in tbbt_episode:
        temp = {}
        temp['utterance'] = x[0]
        temp['speaker'] = x[1]
        one_episode.append(temp)

    # Add subtitles into episode
    for x in alignment:
        en_subs = []
        zh_subs = []
        for item in alignment[x]:
            en_subs.append(en_subset[item])
            zh_subs.append(zh_subset[item])
        one_episode[x]['en_subtitles'] = en_subs
        one_episode[x]['zh_subtitles'] = zh_subs


    # Store all scenes
    scenes = []

    # Iterate all episodes into one scene
    temp = {}
    for i, x in enumerate(tbbt_transcripts[(1,1)]):
        if x[1]=='Scene':
            scenes.append(temp)
            temp = []
        elif i in idx_dict:
            temp.append(one_episode[idx_dict[i]])
    scenes.pop(0)

    return scenes
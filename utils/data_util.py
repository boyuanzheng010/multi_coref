import csv
import json

csv.field_size_limit(1131072)


def collect_mentions(instance):
    """
    Collect answer mentions
    """
    answer_spans = instance['answer_spans']
    mentions = []
    for item in answer_spans:
        # Process annotation into tuple
        query = (item['querySpan']['sentenceIndex'], item['querySpan']['startToken'], item['querySpan']['endToken'])
        answers = []
        for answer in item['span_list']:
            answers.append((answer['sentenceIndex'], answer['startToken'], answer['endToken']))

        if item['notMention']:
            mentions.append([query, "notMention"])
        elif item['notPresent']:
            mentions.append([query, "notPresent"])
        else:
            mentions.append([query, answers])
    return mentions


def generate_all_clusters(instance):
    """
    Collect mentions into clusters
    We treat plural as a independent cluster
    """
    answer_spans = instance['answer_spans']
    clusters = []
    for item in answer_spans:
        # Process annotation into tuple
        query = []
        query.append(
            "_".join([str(item['querySpan']['sentenceIndex']), str(item['querySpan']['startToken']),
                      str(item['querySpan']['endToken'])])
        )
        query = tuple(query)

        answers = []
        for answer in item['span_list']:
            answers.append(
                "_".join([str(answer['sentenceIndex']), str(answer['startToken']), str(answer['endToken'])])
            )
        answers = tuple(answers)

        if item['notMention']:
            continue
        else:
            to_adds = [query]
            if not item['notPresent']:
                to_adds.append(answers)
            # Add to clusters
            signal = True
            for cluster in clusters:
                if answers in cluster:
                    cluster.extend(to_adds)
                    signal = False
            if signal:
                clusters.append(to_adds)

    output = []
    for item in clusters:
        output.append(item)
    return output


def generate_clusters_no_plural(instance):
    """
    Collect mentions into clusters
    We treat plural as a independent cluster
    """
    answer_spans = instance['answer_spans']
    clusters = []
    for item in answer_spans:
        # Process annotation into tuple
        query = []
        query.append(
            "_".join([str(item['querySpan']['sentenceIndex']), str(item['querySpan']['startToken']),
                      str(item['querySpan']['endToken'])])
        )
        query = tuple(query)

        answers = []
        for answer in item['span_list']:
            answers.append(
                "_".join([str(answer['sentenceIndex']), str(answer['startToken']), str(answer['endToken'])])
            )
        answers = tuple(answers)

        if item['notMention']:
            continue
        else:
            to_adds = [query]
            if (not item['notPresent']) and (len(answers) == 1):
                to_adds.append(answers)
            # Add to clusters
            signal = True
            for cluster in clusters:
                if answers in cluster:
                    cluster.extend(to_adds)
                    signal = False
            if signal:
                clusters.append(to_adds)

    output = []
    for item in clusters:
        output.append(item)
    return output


def read_annotation(path):
    """
    Load the annotation along with the document
    Output: sentence along with all annotations
    """
    output = []
    with open(path, 'r') as f:
        annotation_reader = csv.DictReader(f)
        for instance in annotation_reader:
            temp = {}
            for item in instance:
                if item == "Input.json_data":
                    temp['sentences'] = json.loads(instance[item])['sentences']
                elif item == "Answer.answer_spans":
                    temp["answer_spans"] = json.loads(instance[item])
                else:
                    temp[item] = instance[item]
            # Collect mentions into clusters
            temp['clusters_all'] = generate_all_clusters(temp)
            temp['clusters_no_plural'] = generate_clusters_no_plural(temp)

            # Collect mentions (For Kappa Cohen)
            answers = collect_mentions(temp)
            temp["answers"] = answers

            # Add to output
            output.append(temp)

    return output


def gather_by_annotator(annotations):
    """
    annotations: [sentence along with all annotation]
    return {username: [annotations]}
    """
    output = {}
    for instance in annotations:
        key_id = instance['Turkle.Username']
        if key_id not in output:
            output[key_id] = [instance]
        else:
            output[key_id].append(instance)
    return output


def gather_by_scene(annotations):
    """
    annotations: [sentence along with all annotation]
    return {scene_key: [annotations]}
    """
    output = {}
    for instance in annotations:
        key_id = "|".join(instance['sentences'][0][1:10])
        if key_id not in output:
            output[key_id] = [instance]
        else:
            output[key_id].append(instance)
    return output

"""
In this file, I process data and divide according to target sentence emotion
context: all context
target: target word
feedback: random feedback
"""

import jsonlines
import pickle as pkl

with open('collected_primary_data.json', 'r', encoding='utf-8') as f:
    data = []
    for file in jsonlines.Reader(f):
        for x in file:
            # for y in file[x]:
            #     print(y, file[x][y])
            # print('=='*50)
            instance = file[x]
            sentences = instance['sentences']
            state = instance['state']
            index = int(list(state.keys())[0])
            # sentences
            emotion_context_sent = []
            context_sent = []
            target_sent = []
            feedback_sent = []
            for i, sent in enumerate(sentences):
                # Target
                if i == index:
                    target_sent.append(sent)
                if i == index + 1:
                    feedback_sent.append(sent)
                if i == index - 1:
                    emotion_context_sent.append(sent)
                if i < index:
                    context_sent.append(sent)
                # if i == index:
                #     target_sent.append(sent)
                # elif i == index + 1:
                #     feedback_sent.append(sent)
                # elif i < index:
                #     context_sent.append(sent)

            # print(file[x])
            # Id of speaker before target
            former_speaker = file[x]['speakers'][index - 1]
            feedback_emotions = state[str(index)]
            for item in feedback_emotions:
                former_speaker = file[x]['speakers'][index - 1]
                later_speaker = item
                # if former_speaker != int(later_speaker):
                #     continue
                if len(feedback_sent) == 0:
                    continue
                if feedback_sent == ['']:
                    continue
                if len(context_sent) == 0:
                    continue
                if context_sent == ['']:
                    continue
                if len(target_sent) == 0:
                    continue
                if target_sent == ['']:
                    target_sent = 'None'
                # if target_sent == ['']:
                #     continue
                temp = {
                    "context": context_sent,
                    "target": target_sent,
                    "feedback": feedback_sent,
                    "target_emotion": feedback_emotions[item],
                    "context_emotion_sent": emotion_context_sent
                }
                data.append(temp)
print(len(data))
emotion_set = set()
for x in data:
    emotion_set.add(x['target_emotion'])
print(emotion_set)


# # Save according to emotion
# for field in emotion_set:
#     temp_data = []
#     for x in data:
#         if x['target_emotion'] == field:
#             temp_data.append(x)
#     # Set path
#     file_root = field
#     # Set size
#     size = int(len(temp_data) / 12)
#     first = size * 10
#     second = size * 11
#     # Store
#     pkl.dump(temp_data[:first], open(file_root + '_train.pkl', 'wb'))
#     pkl.dump(temp_data[first:second], open(file_root + '_dev.pkl', 'wb'))
#     pkl.dump(temp_data[second:], open(file_root + '_test.pkl', 'wb'))
#     print(field, len(temp_data))


def get_label_str(label):
    return \
        {'surprise': 'neutral', 'anger': 'negative', 'fear': 'negative', 'disgust': 'negative', 'sadness': 'negative',
         'distraction': 'negative', 'annoyance': 'negative',
         'neutral': 'neutral',
         'trust': 'positive', 'anticipation': 'positive', 'joy': 'positive', None: None}[label]

temp_data = []
for x in data:
    temp_data.append(x)
# Set path
file_root = 'all'
# Set size
size = int(len(temp_data) / 12)
first = size * 10
second = size * 11
# Store
pkl.dump(temp_data[:first], open(file_root + '_train.pkl', 'wb'))
pkl.dump(temp_data[first:second], open(file_root + '_dev.pkl', 'wb'))
pkl.dump(temp_data[second:], open(file_root + '_test.pkl', 'wb'))
print("Train:", len(temp_data[:first]))
print("Dev:", len(temp_data[first:second]))
print("Test:", len(temp_data[second:]))
print('==' * 50)

import jsonlines
import pickle as pkl

with open('collected_fine_data.json', 'r', encoding='utf-8') as f:
    data = []
    for file in jsonlines.Reader(f):
        for x in file:
            # for y in file[x]:
            #     print(y, file[x][y])
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
                if former_speaker != int(later_speaker):
                    continue
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
                    continue
                temp = {
                    "context": context_sent,
                    "target": target_sent,
                    "feedback": feedback_sent,
                    "target_emotion": feedback_emotions[item],
                    "context_emotion_sent": emotion_context_sent
                }
                data.append(temp)

pkl.dump(data[:711], open('train.pkl', 'wb'))
pkl.dump(data[711:811], open('dev.pkl', 'wb'))
pkl.dump(data[811:], open('test.pkl', 'wb'))
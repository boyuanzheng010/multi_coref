README

anno.json:
- "primary" denotes 8+1 primary emotion classes: joy, anger, disgust, sadness, surprise, fear, anticipation, trust and neutral.
- "fine_grained" denotes 13+1 fine-grained classes: primary 9 + serenity, interest, annoyance, boredom, distraction.
- For each sample, we have the following annotations:
  - clip: name of the target video clip.
  - moment: the target emotion moment in the video clip.
  - character: the target person in the video clip, 0 to 7 denotes "Leonard", "Sheldon", "Howard", "Rajesh", "Penny", "Bernadette", "Amy" and "Others", respectively.
  - emotion: the annotated emotion category

data.json:
- Each key in the file is the name of video clip
- For each video clip, we have the following annotations:
  - seg_start, seg_end: the start and end timestamp of the segments (In rare case, the start time will be later than end time, because we set the final end time to integer but the seg_start is float)
  - seg_utt: whether this segment is utterance segment (1) or visual-only segment (2)
  - seg_ori_ind: the original index of this segment in the text features (-1 means no text). This is used for audio and text feature index in our baseline code, which means the original order of all sentences.
  - speakers: the speaker of the segments: 0 to 6 denotes "Leonard", "Sheldon", "Howard", "Rajesh", "Penny", "Bernadette", "Amy" and "Others", respectively (-1 means no speaker).
  - start, end: the start and end timestamp in the video clip
  - season, episode: the original season and episode of this video clip
  - sentences: the text of segments (if the segment is visual-only, the text will be an empty string)
  - on_character: the character appeared in this video clip (auto detect by trained face recognition model, not exactly accurate)
  - moment: the annotation moment of this video clip, same as that in anno.json

train_id.txt:
- The training samples. The number is the index of samples in anno.json.

test_id.txt:
- The testing samples. The number is the index of samples in anno.json.

detected_faces.zip:
- The detected faces in each video clips, each face is named "frameid_Character.jpg". The character includes 7 main characters and "Others", "OthersWomen", "OthersMan", which are regarded as "Others" in data.json.

features/character_features.csv
- The annotated 118-d character features and LIWC character features.
- Dimension Introduction: 0-15: 16pf scores; 16-20: Big Five scores; 21-25: MBTI scores; 26-117: LIWC features.

features/audio_features.json
- The features used in the original paper
- Format: each key is "[clipname]+[seg_ori_ind]", and each value is 6373-d features

features/text_features.json
- The features used in the original paper
- Format: each key is "[clipname]+[seg_ori_ind]", and each value is 1024-d features

features/visual_features/environment_features/
- The environment features used in the original paper
- Format: each .pt file contains #frames*2048 tensor

features/visual_features/face_features/
- The face features used in the original paper
- Format: each .pt file contains #faces*512 tensor, the order of faces is sorted by python "sorted(os.listdir(clip_path))", where the clip_path comes from detected_faces

features/visual_features/object_features/
- The object features used in the original paper
- Format: each .pt file contains #frames*1230 tensor, where the order of objects come from 1230 object categories defined in LVIS dataset (Detectron2).

features/visual_features/face_names/
- Use to locate the face features
- The order of face name sequence is the same as the indices of tensors in face_features

videos/
- The original video clips.

pretrained/
- The results reported in the paper is on the setting of train_test_9.pth and train_test_14.pth
- train_test_9.pth: Training on the training set, valid on the test set, primary emotions.
- train_test_14.pth: Training on the training set, valid on the test set, fine-grained emotions.
- train_val_test_9.pth: Training on the training set, valid on the randomly split valid set, testing on testing set, fine-grained emotions.
- train_val_test_14.pth: Training on the training set, valid on the randomly split valid set, testing on testing set, fine-grained emotions.
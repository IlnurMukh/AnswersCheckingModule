
import re
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity


from analyzer import ModMorphAnalyzer


def preprocess_filetext_sent(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    # cleaned_text = re.sub(r'\b\w\b', '', text)
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    text = '\n'.join(sentences)
    sentences = []
    with ModMorphAnalyzer(language="TAT", verbose=False) as morph_analyzer:
        number_all = 0
        number_recognized = 0
        text = text.split('\n')
        for sentence in text:
            results = morph_analyzer.process_text(sentence)
            word = []
            for result in results:
                #print(result)
                #Print closed
                number_all += 1
                if result is None or result[1] is None:
                    continue
                # print(f"{result[0]} : {', '.join(set([x[1] for x in result[1]]))}")
                # print(f"{' '.join(set([x[1] for x in result[1]]))}", end = " ")
                word.append((' '.join(set([x[1] for x in result[1]]))))
                # if(result[1][1] == ""):
                #     word.append(result[1][6][1])
                number_recognized += 1
            sentences.append(word)
    #print(f"{number_recognized}/{number_all}")
    #Print closed
    return sentences


def weighted_sentence_vector(sentences, word_vectors):
    final_vector = []
    for sentence in sentences:
        sentence_vector = np.zeros(word_vectors.vector_size)
        # print(sentence_vector)
        #print(sentence)
        #Print closed
        num_words = 0
        for word in sentence:
            # Если слово есть в модели, добавляем его вектор к вектору предложения
            if word in word_vectors:
                sentence_vector += word_vectors[word]
                # sentence_vector = np.add(sentence_vector, word_vectors)
                # np.add(sentence_vector, word_vectors, out=sentence_vector, casting="unsafe")
                num_words += 1
        # Усредняем вектор предложения по количеству слов
        if num_words != 0:
            sentence_vector /= num_words
        final_vector.append(sentence_vector)
    #print(final_vector)
    #Print closed
    return final_vector

# def calculate_weighted_sentence_vector(sentences, word_vectors):
#     final_vector = []
#     for sentence in sentences:
#         sentence_vector = np.zeros_like(word_vectors.vector_size)
#         num_words = 0
#         for word in sentence:
#             if word in word_vectors:
#                 word_vector = word_vectors[word]
#                 sentence_vector += word_vector
#                 num_words += 1
#         if num_words != 0:
#             sentence_vector /= num_words
#         final_vector.append(sentence_vector)
#     return final_vector

def calculate_weighted_sentence_vector(sentences, word_vectors):
    final_vector = []
    for sentence in sentences:
        sentence_vector = np.zeros(word_vectors.vector_size, dtype=np.float32)
        num_words = 0
        for word in sentence:
            if word in word_vectors:
                word_vector = word_vectors[word]
                sentence_vector += word_vector
                num_words += 1
        # Если в предложении есть слова, усредняем вектор предложения
        if num_words != 0:
            sentence_vector /= num_words
        final_vector.append(sentence_vector)
    return final_vector

sentences = preprocess_filetext_sent(r'C:\\Users\Ilnur\Desktop\ModMorphAnalyzer\ModMorphAnalyzerPackage\Files\train_file_CompGraphics.txt')
correct_answer = preprocess_filetext_sent(r'C:\\Users\Ilnur\Desktop\ModMorphAnalyzer\ModMorphAnalyzerPackage\Files\correct_answer.txt')
student_answers = preprocess_filetext_sent(r'C:\\Users\Ilnur\Desktop\ModMorphAnalyzer\ModMorphAnalyzerPackage\Files\student_answers.txt')

#print(sentences)
#Print closed
#print(correct_answer)
#Print closed
#print(student_answers)
#Print closed

# print(student_answers)

# model = Word2Vec.load("Word2Vec.model")
# model.build_vocab(sentences, update=True)
# model.train(sentences, total_examples=model.corpus_count, epochs=model.epochs, compute_loss=True)
# model.save("Word2Vec.model")

model = Word2Vec(
    sentences,
    vector_size=50,
    alpha=0.01,
    min_alpha=0.0002,
    window=3,
    min_count=3,
    epochs=15,
    workers=7,
)
model.build_vocab(sentences)
model.train(sentences, total_examples=model.corpus_count, epochs=model.epochs, compute_loss=True)
model.save("Word2Vec.model")

# wv = KeyedVectors.load("Word2Vec.model", mmap='r')
word_vectors = model.wv

mean_vectors_students = []
# weight_vector_correct_answer = calculate_weighted_sentence_vector(correct_answer, word_vectors)
# weight_vector_student_answer = calculate_weighted_sentence_vector(student_answers, word_vectors)

weight_vector_correct_answer = calculate_weighted_sentence_vector(correct_answer, word_vectors)
weight_vector_student_answers = calculate_weighted_sentence_vector(student_answers, word_vectors)


mean_weight_vector_correct_answer = np.mean(weight_vector_correct_answer, axis=0)
for vector_students in weight_vector_student_answers:
    mean_vectors_students.append(np.mean(vector_students, axis=0))
# for i in range(len(weight_vector_student_answers)):
#     cosine_dist = cosine_similarity([mean_weight_vector_correct_answer[0].reshape(1,-1)], [mean_vectors_students[i].reshape(1,-1)])[0][0]
#     print(cosine_dist)

# for student_answer_vectors in weight_vector_student_answers:
#     # print(student_answer_vectors)
#     for student_answer_vector in student_answer_vectors:
#         for correct_answer_vector in weight_vector_correct_answer:
#             cosine_dist = cosine_similarity([correct_answer_vector], [student_answer_vector])[0][0]
#             print(cosine_dist)


for i in range(len(weight_vector_student_answers)):
    cosine_dist = cosine_similarity([weight_vector_correct_answer[0]], [weight_vector_student_answers[i]])[0][0]
    print(cosine_dist)

print('done')

# print(weight_vector_correct_answer[0])
# print(weight_vector_student_answers[0])












# Анализ массива слов (используется close() в конце работы)
# morph_analyzer = ModMorphAnalyzer(language="TAT", verbose=True)
# list(morph_analyzer.process_words(["дәвамы", "кешеләрне", "каралган"]))
# morph_analyzer.close()


# text2 = preprocess_filetext_sent("RussianText.txt")
# print(text2)
# text2 = text2.split('\n')
# sentences = []
# for sentence in text2:
#     print(sentence)
#     words = sentence.split()
#     sentences.append(words)
# print(sentences)

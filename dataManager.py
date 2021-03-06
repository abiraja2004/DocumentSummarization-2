import numpy as np
from nltk.stem import SnowballStemmer
from numpy import dot
from numpy.linalg import norm
import math
from keras.preprocessing.text import Tokenizer

class dataManager:
    def __init__(self):
        # Shared
        self.inputTokenizer = Tokenizer()
        self.reverse_input_word_map = None
        self.outputTokenizer = Tokenizer()
        self.reverse_output_word_map = None
        # Input
        self.inputData = None
        self.inputTexts = []
        # Output
        self.targetTexts = []
        self.targetData = None
        self.outputData = None
        self.outputTexts = []
        # Constant
        self.MAX_INPUT_LENGTH = 400
        self.MAX_OUTPUT_LENGTH = 10

    def tokenizeData (self, inputSentenceList, outputSentenceList):
        for sentence in inputSentenceList:
            sentenceList = sentence.split()
            self.inputTokenizer.fit_on_texts(sentenceList)
        self.inputTokenizer.fit_on_texts(["UNK"])
        for sentence in outputSentenceList:
            sentenceList = sentence.split()
            self.outputTokenizer.fit_on_texts(sentenceList)
        self.outputTokenizer.fit_on_texts(["PAD"])
        self.outputTokenizer.fit_on_texts(["UNK"])
        self.outputTokenizer.fit_on_texts(["G"])
        self.outputTokenizer.fit_on_texts(["E"])


    def saveInputData(self, input_texts):
        self.inputData = np.zeros(
            (len(input_texts), 1, self.MAX_INPUT_LENGTH), dtype='uint32')
        for t, input_text in enumerate(input_texts):
            text = input_text.lower()
            text = text.split()
            text = self.removeStemming(text)
            self.inputTexts.append(text)

            input_text = text[:self.MAX_INPUT_LENGTH]
            input_sequence = self.inputTokenizer.texts_to_sequences(input_text)
            for i, seq in enumerate(input_sequence):
                if seq == []:
                    seq = self.inputTokenizer.texts_to_sequences(["UNK"])[0]
                self.inputData[t, 0, i] = seq[0]

        print("Input Text Shape:%s" % str(self.inputData.shape))

    def saveOutputData(self, target_texts):
        self.outputData = np.zeros(
            (len(target_texts), 1, self.MAX_OUTPUT_LENGTH), dtype='uint32')
        self.targetData = np.zeros(
            (len(target_texts), 1, self.MAX_OUTPUT_LENGTH), dtype='uint32')

        for t, target_text in enumerate(target_texts):
            text = target_text.lower()
            text = text.split()
            text = self.removeStemming(text)
            if len(text) >= (self.MAX_OUTPUT_LENGTH - 2):
                text = ["G"] + text[0:(self.MAX_OUTPUT_LENGTH - 2)] + ['E']
            else:
                text = ["G"] + text + ['E'] + ["PAD"] * (self.MAX_OUTPUT_LENGTH - 2 - len(text))
            self.targetTexts.append(text)

            output_text = text[1:]
            target_text = text

            output_sequence = self.outputTokenizer.texts_to_sequences(output_text)
            for i, seq in enumerate(output_sequence):
                if seq == []:
                    seq = self.outputTokenizer.texts_to_sequences(["UNK"])[0]
                self.outputData[t, 0, i] = seq[0]

            target_sequence = self.outputTokenizer.texts_to_sequences(target_text)
            for i, seq in enumerate(target_sequence):
                if seq == []:
                    seq = self.outputTokenizer.texts_to_sequences(["UNK"])[0]
                self.targetData[t, 0, i] = seq[0]
        print("Output Text Shape:%s" % str(self.outputData.shape))
        print("Target Text Shape:%s" % str(self.targetData.shape))

    def removeStemming (self, text):
        stemmer = SnowballStemmer('english')
        stemmed_words = [stemmer.stem(word) for word in text]
        return stemmed_words

    def convertVectorsToSentences(self, outputSequence):
        sentence = ""
        tempSequence = outputSequence[0,0]
        for seq in tempSequence:
            index = abs(int(seq))
            if index in self.reverse_output_word_map.keys():
                sentence += self.reverse_output_word_map[index]
            else:
                sentence += "unk"
            sentence += " "
        return sentence

    def getSimilarWords(self, vector, table):
        cosineSimilar = 99999
        cosineSimilarWord = None
        for word in table.keys():
            listOfCoef1 = vector.tolist()
            listOfCoef2 = table[word].tolist()

            #Cosine Similarity
            cosine_result = math.acos(dot(listOfCoef1, listOfCoef2)/(norm(listOfCoef1)*norm(listOfCoef2)))
            if cosine_result < cosineSimilar:
                cosineSimilar = cosine_result
                cosineSimilarWord = word

        return cosineSimilarWord
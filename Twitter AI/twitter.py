import re #regular expression, helps with string search
import pandas as pd #allows to handle csv files
import numpy as np #allows to manipulate arrays easily
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import *
stemmer = PorterStemmer()
nltk.download('stopwords')
stop = stopwords.words('english')


def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
        
    return input_txt


data  = pd.read_csv('train.csv')

# data has 3 columns, id (index of tweet), label (racist = 1, not = 0), tweet (data inside tweet)

'''
removes the twitter handles (@user from the array)
'''

data['tidy_tweet'] = np.vectorize(remove_pattern)(data['tweet'], r"@[\w+]")


# remove special characters, numbers, punctuations
# panda function (A,B, regex = T/F) that replaces strings in A by string B and if the pattern is a regular expression
data['tidy_tweet'] = data['tidy_tweet'].str.replace("[^a-zA-Z#]", " ", regex=True)
# remove short words length 3 or less
#apply function, is apply a function to the entire Series 
# (in here each tweet) function is a lambda function that replaces any word less 
# than 3 character by a space
data['tidy_tweet'] = data['tidy_tweet'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))
# remove stop words
data['tidy_tweet'] = data['tidy_tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

#tokenization
tokenized_tweet = data['tidy_tweet'].apply(lambda x: x.split())

#stemming

tokenized_tweet = tokenized_tweet.apply(lambda x: [stemmer.stem(i) for i in x])

#join tokens back together
for i in range(len(tokenized_tweet)):
    tokenized_tweet[i] = ' '.join(tokenized_tweet[i])

data['tidy_tweet'] = tokenized_tweet



from sklearn.feature_extraction.text import CountVectorizer

"""
Count Vectorizer ignore words with frequency higher than 0.9 and ignore terms 
that appear in less than 2 documents and choose 1000 most frequent words and
that remove more stop words (if we don't there will be too many iterations)
We create a transformer object with these parameter
"""
bow_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words='english')


"""
fit -> learns for the model to be able to use predict methods later later on

transform -> transforms into a matrix, with each row being a different tweet
containing the frequency of each word in the tweet. 
each word is in the form form (tweet number, word id in vocabulary)   frequency of word in tweet
"""

bow = bow_vectorizer.fit_transform(data['tweet'])


'''
The Vocabulary (word and its id) in the transformer can be found using the
method : bow_vectorizer.vocabulary_
'''
#print(bow_vectorizer.vocabulary_)

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score


'''
we split the data into 80% for training and 20% for validation score later on. The split is done randomly
'''
# splitting data into training and validation set
xtrain_bow, xvalid_bow, ytrain, yvalid = train_test_split(bow, data['label'], test_size=0.2)


lreg = LogisticRegression()
lreg.fit(xtrain_bow, ytrain) # training the model using LogisticRegression

prediction1 = lreg.predict_proba(xvalid_bow) # predicting on the validation set
prediction_int1 = prediction1[:,1] >= 0.3 # if prediction is greater than or equal to 0.3 than 1 else 0
print(type(prediction_int1))
prediction_int1 = prediction_int1.astype(int)

print(f1_score(yvalid, prediction_int1)) # calculating f1 score







#!/usr/bin/env python

import numpy as np
import random

from q1_softmax import softmax
from q2_gradcheck import gradcheck_naive
from q2_sigmoid import sigmoid, sigmoid_grad

def normalizeRows(x):
    """ Row normalization function

    Implement a function that normalizes each row of a matrix to have
    unit length.
    """

    ### YOUR CODE HERE
    #raise NotImplementedError
    from numpy.linalg import norm
    x /= norm( x, axis=1, keepdims=True ) #keepdims is important
    
    ### END YOUR CODE

    return x


def test_normalize_rows():
    print "Testing normalizeRows..."
    x = normalizeRows(np.array([[3.0,4.0],[1, 2]]))
    print x
    ans = np.array([[0.6,0.8],[0.4472136,0.89442719]])
    assert np.allclose(x, ans, rtol=1e-05, atol=1e-06)
    print ""


def softmaxCostAndGradient(predicted, target, outputVectors, dataset):
    """ Softmax cost function for word2vec models

    Implement the cost and gradients for one predicted word vector
    and one target word vector as a building block for word2vec
    models, assuming the softmax prediction function and cross
    entropy loss.

    Arguments:
    predicted -- numpy ndarray, predicted word vector (\hat{v} in
                 the written component)
    target -- integer, the index of the target word
    outputVectors -- "output" vectors (as rows) for all tokens
    dataset -- needed for negative sampling, unused here.

    Return:
    cost -- cross entropy cost for the softmax word prediction
    gradPred -- the gradient with respect to the predicted word
           vector
    grad -- the gradient with respect to all the other word
           vectors

    We will not provide starter code for this function, but feel
    free to reference the code you previously wrote for this
    assignment!
    """

    ### YOUR CODE HERE
    #raise NotImplementedError
    cost = 0
    gradPred = np.zeros_like( predicted )
    grad     = np.zeros_like( outputVectors )
    
    #print predicted.shape     #(3,)
    #print outputVectors.shape #(5,3)
    
    scores = outputVectors.dot( predicted )
    yhat = softmax( scores )
    
    #print yhat.shape          #(5,)
    
    #We have the cost for only one (input output) pair
    #So no need to sum. 
    cost = -np.log( yhat[target] ) # sum ( y log y' ) #y is 1 at target and 0 everywhere else.
    #print cost
    
    yhat[target] -= 1
    #print yhat.shape
    
    gradPred = outputVectors.T.dot( yhat )
    #gradPred = outputVectors[target]*yhat[target]
    #print outputVectors.shape, yhat.shape
    
    #we change the shape (V,) => (V,1) and (d,) => (d,1) to get grad shape => ( V, d )
    grad = yhat.reshape(-1,1).dot( predicted.reshape(-1,1).T )
    #print ( grad.shape )
    #grad = yhat[target] * outputVectors[target]
    ### END YOUR CODE

    return cost, gradPred, grad


def getNegativeSamples(target, dataset, K):
    """ Samples K indexes which are not the target """

    indices = [None] * K
    for k in xrange(K):
        newidx = dataset.sampleTokenIdx()
        while newidx == target:
            newidx = dataset.sampleTokenIdx()
        indices[k] = newidx
    return indices


def negSamplingCostAndGradient(predicted, target, outputVectors, dataset,
                               K=10):
    """ Negative sampling cost function for word2vec models

    Implement the cost and gradients for one predicted word vector
    and one target word vector as a building block for word2vec
    models, using the negative sampling technique. K is the sample
    size.

    Note: See test_word2vec below for dataset's initialization.

    Arguments/Return Specifications: same as softmaxCostAndGradient
    """

    # Sampling of indices is done for you. Do not modify this if you
    # wish to match the autograder and receive points!
    indices = [target]
    indices.extend(getNegativeSamples(target, dataset, K))

    ### YOUR CODE HERE
    #raise NotImplementedError
    cost = 0
    gradPred = np.zeros_like( predicted )
    grad     = np.zeros_like( outputVectors )
    
    negative_smaple_outputVectors = outputVectors[ indices ]
    #cost is -log( sigmoid(score)) - sum( log( sigmoid(-scores_neg ) ))
    #u0 = negative_smaple_outputVectors[ 0 ] #because we put the first index as target; ref line 126
    #cost = -np.log( sigmoid(u0.dot(predicted) ) ) - np.sum( np.log( sigmoid( -1*negative_smaple_outputVectors[1:].dot(predicted) ) ) )
    
    yhat = sigmoid( negative_smaple_outputVectors.dot(predicted) )    
        
    cost = -np.log(yhat[0]) - np.sum( np.log(1-yhat[1:]) )

    yhat[0] -= 1 #similar to yhat[target] -= 1 in softmax. 
    
    gradPred = negative_smaple_outputVectors.T.dot(yhat)
    #print (gradPred)
    #grad = S1.dot(predicted)
    grad_neg = yhat.reshape(-1,1).dot( predicted.reshape(-1,1).T )
    #print (grad.shape)
    #grad[indices] = grad_neg
    
    
    #We need to add the grad_neg to grads at the appropriate index.
    #for i,u in enumerate(indices) :
    #    grad[u] += grad_neg[i]  
    #ref: https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.ufunc.at.html
    np.add.at( grad, indices, grad_neg ) #NOTE: this is not the same as grad[indices] += grad_neg because indices may have duplicates
    
    ### END YOUR CODE

    return cost, gradPred, grad


def skipgram(currentWord, C, contextWords, tokens, inputVectors, outputVectors,
             dataset, word2vecCostAndGradient=softmaxCostAndGradient):
    """ Skip-gram model in word2vec

    Implement the skip-gram model in this function.

    Arguments:
    currentWord -- a string of the current center word
    C -- integer, context size
    contextWords -- list of no more than 2*C strings, the context words
    tokens -- a dictionary that maps words to their indices in
              the word vector list
    inputVectors -- "input" word vectors (as rows) for all tokens
    outputVectors -- "output" word vectors (as rows) for all tokens
    word2vecCostAndGradient -- the cost and gradient function for
                               a prediction vector given the target
                               word vectors, could be one of the two
                               cost functions you implemented above.

    Return:
    cost -- the cost function value for the skip-gram model
    grad -- the gradient with respect to the word vectors
    """

    cost = 0.0
    gradIn  = np.zeros(inputVectors.shape)
    gradOut = np.zeros(outputVectors.shape)
    #print ("gradIn", gradIn.shape)
    #print ("gradOut", gradOut.shape)
    ### YOUR CODE HERE
    #raise NotImplementedError
    currentWord_index = tokens[currentWord] #word to index
    predicted = inputVectors[ currentWord_index ]
    context_index = [ tokens[c] for c in contextWords ]
    
    for target_index in context_index :
        cost_one, gradPred, grad = word2vecCostAndGradient(predicted, target_index, outputVectors, dataset)
        cost    += cost_one
        gradIn[currentWord_index]  += gradPred
        gradOut     += grad
    ### END YOUR CODE

    return cost, gradIn, gradOut


def cbow(currentWord, C, contextWords, tokens, inputVectors, outputVectors,
         dataset, word2vecCostAndGradient=softmaxCostAndGradient):
    """CBOW model in word2vec

    Implement the continuous bag-of-words model in this function.

    Arguments/Return specifications: same as the skip-gram model

    Extra credit: Implementing CBOW is optional, but the gradient
    derivations are not. If you decide not to implement CBOW, remove
    the NotImplementedError.
    """

    cost = 0.0
    gradIn = np.zeros(inputVectors.shape)
    gradOut = np.zeros(outputVectors.shape)

    ### YOUR CODE HERE
    #raise NotImplementedError
    ### END YOUR CODE

    return cost, gradIn, gradOut


#############################################
# Testing functions below. DO NOT MODIFY!   #
#############################################

def word2vec_sgd_wrapper(word2vecModel, tokens, wordVectors, dataset, C,
                         word2vecCostAndGradient=softmaxCostAndGradient):
    batchsize = 50
    cost = 0.0
    grad = np.zeros(wordVectors.shape)
    N = wordVectors.shape[0]
    inputVectors = wordVectors[:N/2,:]
    outputVectors = wordVectors[N/2:,:]
    for i in xrange(batchsize):
        C1 = random.randint(1,C)
        centerword, context = dataset.getRandomContext(C1)

        if word2vecModel == skipgram:
            denom = 1
        else:
            denom = 1

        c, gin, gout = word2vecModel(
            centerword, C1, context, tokens, inputVectors, outputVectors,
            dataset, word2vecCostAndGradient)
        cost += c / batchsize / denom
        grad[:N/2, :] += gin / batchsize / denom
        grad[N/2:, :] += gout / batchsize / denom

    return cost, grad


def test_word2vec():
    """ Interface to the dataset for negative sampling """
    dataset = type('dummy', (), {})()
    def dummySampleTokenIdx():
        return random.randint(0, 4)

    def getRandomContext(C):
        tokens = ["a", "b", "c", "d", "e"]
        return tokens[random.randint(0,4)], \
            [tokens[random.randint(0,4)] for i in xrange(2*C)]
    dataset.sampleTokenIdx = dummySampleTokenIdx
    dataset.getRandomContext = getRandomContext

    random.seed(31415)
    np.random.seed(9265)
    dummy_vectors = normalizeRows(np.random.randn(10,3))
    dummy_tokens = dict([("a",0), ("b",1), ("c",2),("d",3),("e",4)])
    
    print "==== Gradient check for skip-gram ===="
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(
        skipgram, dummy_tokens, vec, dataset, 5, softmaxCostAndGradient),
        dummy_vectors)       
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(
        skipgram, dummy_tokens, vec, dataset, 5, negSamplingCostAndGradient),
        dummy_vectors)
    
    print "\n==== Gradient check for CBOW      ===="
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(
        cbow, dummy_tokens, vec, dataset, 5, softmaxCostAndGradient),
        dummy_vectors)
    gradcheck_naive(lambda vec: word2vec_sgd_wrapper(
        cbow, dummy_tokens, vec, dataset, 5, negSamplingCostAndGradient),
        dummy_vectors)

    print "\n=== Results ==="
    print skipgram("c", 3, ["a", "b", "e", "d", "b", "c"],
        dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset)
    print skipgram("c", 1, ["a", "b"],
        dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset,
        negSamplingCostAndGradient)
    print cbow("a", 2, ["a", "b", "c", "a"],
        dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset)
    print cbow("a", 2, ["a", "b", "a", "c"],
        dummy_tokens, dummy_vectors[:5,:], dummy_vectors[5:,:], dataset,
        negSamplingCostAndGradient)


if __name__ == "__main__":
    test_normalize_rows()
    test_word2vec()

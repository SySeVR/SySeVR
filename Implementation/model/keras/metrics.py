from __future__ import absolute_import
import six
from . import backend as K
from .losses import mean_squared_error
from .losses import mean_absolute_error
from .losses import mean_absolute_percentage_error
from .losses import mean_squared_logarithmic_error
from .losses import hinge
from .losses import logcosh
from .losses import squared_hinge
from .losses import categorical_crossentropy
from .losses import sparse_categorical_crossentropy
from .losses import binary_crossentropy
from .losses import kullback_leibler_divergence
from .losses import poisson
from .losses import cosine_proximity
from .utils.generic_utils import deserialize_keras_object


def binary_accuracy(y_true, y_pred):
    return K.mean(K.equal(y_true, K.round(y_pred)), axis=-1)


def categorical_accuracy(y_true, y_pred):
    return K.cast(K.equal(K.argmax(y_true, axis=-1),
                          K.argmax(y_pred, axis=-1)),
                  K.floatx())


def sparse_categorical_accuracy(y_true, y_pred):
    return K.cast(K.equal(K.max(y_true, axis=-1),
                          K.cast(K.argmax(y_pred, axis=-1), K.floatx())),
                  K.floatx())


def top_k_categorical_accuracy(y_true, y_pred, k=5):
    return K.mean(K.in_top_k(y_pred, K.argmax(y_true, axis=-1), k), axis=-1)


def sparse_top_k_categorical_accuracy(y_true, y_pred, k=5):
    return K.mean(K.in_top_k(y_pred, K.cast(K.max(y_true, axis=-1), 'int32'), k), axis=-1)


'''
    ####
    metices from keras_old for collect information like F1,TN,FP and so on.
    Transplant from ../keras_old/metrics.py
    coder : Sophie
    transplanter : Yoki
    ####
'''
def matthews_correlation(y_true, y_pred):
    '''Calculates the Matthews correlation coefficient measure for quality
    of binary classification problems.
    '''
    y_pred_pos = K.round(K.clip(y_pred, 0, 1))
    y_pred_neg = 1 - y_pred_pos

    y_pos = K.round(K.clip(y_true, 0, 1))
    y_neg = 1 - y_pos

    tp = K.sum(y_pos * y_pred_pos)
    tn = K.sum(y_neg * y_pred_neg)

    fp = K.sum(y_neg * y_pred_pos)
    fn = K.sum(y_pos * y_pred_neg)

    numerator = (tp * tn - fp * fn)
    denominator = K.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))

    return numerator / (denominator + K.epsilon())


def fbeta_score(y_true, y_pred, beta=1):
    '''Computes the F score, the weighted harmonic mean of precision and recall.

    This is useful for multi-label classification where input samples can be
    tagged with a set of labels. By only using accuracy (precision) a model
    would achieve a perfect score by simply assigning every class to every
    input. In order to avoid this, a metric should penalize incorrect class
    assignments as well (recall). The F-beta score (ranged from 0.0 to 1.0)
    computes this, as a weighted mean of the proportion of correct class
    assignments vs. the proportion of incorrect class assignments.

    With beta = 1, this is equivalent to a F-measure. With beta < 1, assigning
    correct classes becomes more important, and with beta > 1 the metric is
    instead weighted towards penalizing incorrect class assignments.

    '''
    if beta < 0:
        raise ValueError('The lowest choosable beta is zero (only precision).')

    # Count positive samples.
    #print y_true, y_pred
    #print type(y_true), type(y_pred)
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))
    c3 = K.sum(K.round(K.clip(y_true, 0, 1)))
    #print c1,c2,c3

    # If there are no true samples, fix the F score at 0.
    if c3 == 0:
        return 0
        
    # How many selected items are relevant?
    precision = c1 / (c2 + 1e-8)

    # How many relevant items are selected?
    recall = c1 / (c3 + 1e-8)

    # Weight precision and recall together as a single scalar.
    beta2 = beta ** 2
    f_score = (1 + beta2) * (precision * recall) / (beta2 * precision + recall + 1e-8)
    #f_score = c3
    return f_score


def precision(y_true, y_pred):
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))

    precision = c1 / (c2 + 1e-8)

    return precision


def recall(y_true, y_pred):
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c3 = K.sum(K.round(K.clip(y_true, 0, 1)))

    recall = c1 / (c3 + 1e-8)

    return recall


def TP_count(y_true, y_pred):
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    return c1

def y_pred(y_true, y_pred):
    return y_pred

def y_true(y_true, y_pred):
    return y_true


def FP_count(y_true, y_pred):
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))

    fp = c2-c1
    return fp


def FP_count_true(y_true, y_pred):
    #c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    #c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))

    #fp = c2-c1
    return y_true


def FP_count_pred(y_true, y_pred):
    #c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    #c2 = K.sum(K.round(K.clip(y_pred, 0, 1)))

    #fp = c2-c1
    return y_pred


def FN_count(y_true, y_pred):
    c1 = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    c3 = K.sum(K.round(K.clip(y_true, 0, 1)))

    fn = c3-c1
    return fn


def Y_true_and_pred(y_true, y_pred):
    _tuple = (y_true, y_pred)        
    return _tuple



# Aliases

mse = MSE = mean_squared_error
mae = MAE = mean_absolute_error
mape = MAPE = mean_absolute_percentage_error
msle = MSLE = mean_squared_logarithmic_error
cosine = cosine_proximity


def serialize(metric):
    return metric.__name__


def deserialize(name, custom_objects=None):
    return deserialize_keras_object(name,
                                    module_objects=globals(),
                                    custom_objects=custom_objects,
                                    printable_module_name='metric function')


def get(identifier):
    if isinstance(identifier, six.string_types):
        identifier = str(identifier)
        return deserialize(identifier)
    elif callable(identifier):
        return identifier
    else:
        raise ValueError('Could not interpret '
                         'metric function identifier:', identifier)

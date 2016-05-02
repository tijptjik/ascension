from collections import Counter

'''
UTILS
'''

class ScoreCounter(Counter):
    def __str__(self):
        scores = sorted(self.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Character','Score'],tablefmt="pipe",numalign="right")
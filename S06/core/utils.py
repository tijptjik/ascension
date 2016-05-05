from collections import Counter

'''
UTILS
'''

class ScoreCounter(Counter):
    def __str__(self):
        scores = sorted(self.items(), key=operator.itemgetter(1), reverse=True)
        return tabulate(scores, headers=['Character','Score'],tablefmt="pipe",numalign="right")

def ordinal(n):
        if 10 <= n % 100 < 20:
            return str(n) + 'th'
        else:
           return  str(n) + {1 : 'st', 2 : 'nd', 3 : 'rd'}.get(n % 10, "th")
# No of Players who voted per episode

#Read in data & create total column
# stacked_bar_data = pd.read_csv("C:\stacked_bar.csv")
# stacked_bar_data["total"] = stacked_bar_data.Series1 + stacked_bar_data.Series2
 
#Plot 1 - background - "total" (top) series
# sns.barplot(x = stacked_bar_data.Group, y = stacked_bar_data.total, color = "red")
 
#Plot 2 - overlay - "bottom" series
# bottom_plot = sns.barplot(x = stacked_bar_data.Group, y = stacked_bar_data.Series1, color = "#0000A3")
 
 
# topbar = plt.Rectangle((0,0),1,1,fc="red", edgecolor = 'none')
# bottombar = plt.Rectangle((0,0),1,1,fc='#0000A3',  edgecolor = 'none')
# l = plt.legend([bottombar, topbar], ['Bottom Bar', 'Top Bar'], loc=1, ncol = 2, prop={'size':16})
# l.draw_frame(False)
 
#Optional code - Make plot look nicer
# sns.despine(left=True)
# bottom_plot.set_ylabel("Y-axis label")
# bottom_plot.set_xlabel("X-axis label")
 
#Set fonts to consistent 16pt size
# for item in ([bottom_plot.xaxis.label, bottom_plot.yaxis.label] +
#              bottom_plot.get_xticklabels() + bottom_plot.get_yticklabels()):
#     item.set_fontsize(16)
    
# No of Votes collected per episode
# No of Points available per episode
# No of Points awarded per episode, adjusted for rank
# Vote density, per award | mean(no_votes)/max(votes)
# Ranked, Player with most Episodes Votes
# Ranked, Player with most Total Votes

# stacked_votes = votes[['Player','Character','Episode']].groupby(['Player','Episode']).count()

# stacked_votes

# votes.Character.replace('-',0,inplace=True)
# votes_pivoted = pd.pivot_table(votes, values='Character', index=['Episode'], columns=['Player'], aggfunc=np.count_nonzero, fill_value=0)
# votes_pivoted.index = range(1,len(votes_pivoted.index)+1)

# import matplotlib.pylab as plt
# plt.figure()
# ax = votes_pivoted.plot(kind='bar',
#             stacked=True,
#             title="Hits vs. At Bats",
#             x_compat=True);

# ax = fig.add_subplot(1,1,1) # one row, one column, first plot
# plt.set_title()
# ax.set_xlabel("At Bats")
# ax.set_ylabel("Hits")

# votes_pivoted

# pd.concat([stacked_votes.loc['Josh Du'], stacked_votes.loc['Mart']], axis=1)

# votes

# h3_info('Points')

# Ranking, Points Collected by Character
# Ranking, Points Awarded by Character, adjusted for rank

# h3_info('Awards')

# Ranking, Number of Awards won by Character, per Award
# Ranking, Points Collected by Character, per Award
# Ranking, Points Available by Award (Most Lucrative Award)
# Ranking, Total number of Awards won by Character
# Ranking, Total number of Points collected won by Character

# h2_success('PLAYERS')

# Stats broken down for invidual players.

# player = ''

# Line Chart with most Points Won per Character per Episode
# Line Chart with most Points Awarded per Character per Episode, adjusted by rank
# Ranked, Most Valuable Character

# h2_success('META')

# Multiplier balance
# Line Chart, Points Awarded by Rank, per Episode
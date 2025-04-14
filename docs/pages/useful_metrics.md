---
layout: page
title: "Useful Metrics"
permalink: /useful_metrics/
---


[Feature Engineering Home]({{ site.baseurl }}/feature_engineering/) | [Useful Metrics]({{ site.baseurl }}/useful_metrics/) | [Creation/Prevention]({{ site.baseurl }}/creation_prevention/) | [Matchup Features]({{ site.baseurl }}/matchup_features/)

When building a predictive model for basketball outcomes, raw stats like field goals made and turnovers don't always tell the full story. To get a clearer picture of a team's performance, I transform these raw numbers into more meaningful metrics that account for pace, efficiency, and contextual factors.

```python
import pandas as pd
import numpy as np
```

I first read in my regular season results files and examine


```python
m_detailed_results = pd.read_csv('../kaggle_data/men/MRegularSeasonDetailedResults.csv')
m_detailed_results['Side'] = 'Men'
w_detailed_results = pd.read_csv('../kaggle_data/women/WRegularSeasonDetailedResults.csv')
w_detailed_results['Side'] = 'Women'
detailed_results = pd.concat([m_detailed_results, w_detailed_results], ignore_index=True)
```


```python
detailed_results.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Season</th>
      <th>DayNum</th>
      <th>WTeamID</th>
      <th>WScore</th>
      <th>LTeamID</th>
      <th>LScore</th>
      <th>WLoc</th>
      <th>NumOT</th>
      <th>WFGM</th>
      <th>WFGA</th>
      <th>...</th>
      <th>LFTM</th>
      <th>LFTA</th>
      <th>LOR</th>
      <th>LDR</th>
      <th>LAst</th>
      <th>LTO</th>
      <th>LStl</th>
      <th>LBlk</th>
      <th>LPF</th>
      <th>Side</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2003</td>
      <td>10</td>
      <td>1104</td>
      <td>68</td>
      <td>1328</td>
      <td>62</td>
      <td>N</td>
      <td>0</td>
      <td>27</td>
      <td>58</td>
      <td>...</td>
      <td>16</td>
      <td>22</td>
      <td>10</td>
      <td>22</td>
      <td>8</td>
      <td>18</td>
      <td>9</td>
      <td>2</td>
      <td>20</td>
      <td>Men</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2003</td>
      <td>10</td>
      <td>1272</td>
      <td>70</td>
      <td>1393</td>
      <td>63</td>
      <td>N</td>
      <td>0</td>
      <td>26</td>
      <td>62</td>
      <td>...</td>
      <td>9</td>
      <td>20</td>
      <td>20</td>
      <td>25</td>
      <td>7</td>
      <td>12</td>
      <td>8</td>
      <td>6</td>
      <td>16</td>
      <td>Men</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2003</td>
      <td>11</td>
      <td>1266</td>
      <td>73</td>
      <td>1437</td>
      <td>61</td>
      <td>N</td>
      <td>0</td>
      <td>24</td>
      <td>58</td>
      <td>...</td>
      <td>14</td>
      <td>23</td>
      <td>31</td>
      <td>22</td>
      <td>9</td>
      <td>12</td>
      <td>2</td>
      <td>5</td>
      <td>23</td>
      <td>Men</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2003</td>
      <td>11</td>
      <td>1296</td>
      <td>56</td>
      <td>1457</td>
      <td>50</td>
      <td>N</td>
      <td>0</td>
      <td>18</td>
      <td>38</td>
      <td>...</td>
      <td>8</td>
      <td>15</td>
      <td>17</td>
      <td>20</td>
      <td>9</td>
      <td>19</td>
      <td>4</td>
      <td>3</td>
      <td>23</td>
      <td>Men</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2003</td>
      <td>11</td>
      <td>1400</td>
      <td>77</td>
      <td>1208</td>
      <td>71</td>
      <td>N</td>
      <td>0</td>
      <td>30</td>
      <td>61</td>
      <td>...</td>
      <td>17</td>
      <td>27</td>
      <td>21</td>
      <td>15</td>
      <td>12</td>
      <td>10</td>
      <td>7</td>
      <td>1</td>
      <td>14</td>
      <td>Men</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 35 columns</p>
</div>




```python
detailed_results['LLoc'] = detailed_results['WLoc'].apply(lambda x: 'A' if x == 'H' else ('H' if x == 'A' else 'N'))

winner_rows = detailed_results.copy()
loser_rows = detailed_results.copy()

for col in detailed_results.columns.tolist():
    if col[0] == 'W':
        stat = col[1:]
        winner_rows[stat] = winner_rows['W' + stat]
        winner_rows['Opp' + stat] = winner_rows['L' + stat]
        winner_rows['Win'] = 1
        loser_rows[stat] = loser_rows['L' + stat]
        loser_rows['Opp' + stat] = loser_rows['W' + stat]
        loser_rows['Win'] = 0

        winner_rows = winner_rows.drop(columns=['W' + stat, 'L' + stat])
        loser_rows = loser_rows.drop(columns=['W' + stat, 'L' + stat])

games_expanded_detailed = pd.concat([winner_rows, loser_rows], ignore_index=True)
games_expanded_detailed.columns
```




    Index(['Season', 'DayNum', 'NumOT', 'Side', 'TeamID', 'OppTeamID', 'Win',
           'Score', 'OppScore', 'Loc', 'OppLoc', 'FGM', 'OppFGM', 'FGA', 'OppFGA',
           'FGM3', 'OppFGM3', 'FGA3', 'OppFGA3', 'FTM', 'OppFTM', 'FTA', 'OppFTA',
           'OR', 'OppOR', 'DR', 'OppDR', 'Ast', 'OppAst', 'TO', 'OppTO', 'Stl',
           'OppStl', 'Blk', 'OppBlk', 'PF', 'OppPF'],
          dtype='object')




```python
games_expanded_detailed['Possessions'] = (games_expanded_detailed['FGA'] - games_expanded_detailed['OR'] + games_expanded_detailed['TO'] + 0.44 * games_expanded_detailed['FTA'])
games_expanded_detailed['OppPossessions'] = (games_expanded_detailed['OppFGA'] - games_expanded_detailed['OppOR'] + games_expanded_detailed['OppTO'] + 0.44 * games_expanded_detailed['OppFTA'])
```


```python
def safe_divide(numerator, denominator):
    return np.where(denominator == 0, None, numerator / denominator)

for team, other in [("", "Opp"), ("Opp", "")]:
    # Percentages based on field goals, free throws, assists
    games_expanded_detailed[f"{team}FGPercent"]      = safe_divide(games_expanded_detailed[f"{team}FGM"],  games_expanded_detailed[f"{team}FGA"])
    games_expanded_detailed[f"{team}FG3Percent"]     = safe_divide(games_expanded_detailed[f"{team}FGM3"], games_expanded_detailed[f"{team}FGA3"])
    games_expanded_detailed[f"{team}FTPercent"]      = safe_divide(games_expanded_detailed[f"{team}FTM"],  games_expanded_detailed[f"{team}FTA"])
    games_expanded_detailed[f"{team}AstPercent"]     = safe_divide(games_expanded_detailed[f"{team}Ast"], games_expanded_detailed[f"{team}FGM"])
    games_expanded_detailed[f"{team}Att3Percent"]    = safe_divide(games_expanded_detailed[f"{team}FGA3"], games_expanded_detailed[f"{team}FGA"])

    # Offensive rebounding percentage (special case)
    or_denominator = games_expanded_detailed[f"{team}OR"] + games_expanded_detailed[f"{other}DR"]
    or_zero_check = (games_expanded_detailed[f"{team}OR"] == 0) & (games_expanded_detailed[f"{other}DR"] == 0)
    games_expanded_detailed[f"{team}ORPercent"] = np.where(or_zero_check, None, safe_divide(games_expanded_detailed[f"{team}OR"], or_denominator))

    # Possession-based metrics
    games_expanded_detailed[f"{team}PointsPerPoss"] = safe_divide(games_expanded_detailed[f"{team}Score"], games_expanded_detailed[f"{team}Possessions"])
    games_expanded_detailed[f"{team}TOPerPoss"]     = safe_divide(games_expanded_detailed[f"{team}TO"],    games_expanded_detailed[f"{team}Possessions"])
    games_expanded_detailed[f"{team}StlPerPoss"]    = safe_divide(games_expanded_detailed[f"{team}Stl"],   games_expanded_detailed[f"{other}Possessions"])
    games_expanded_detailed[f"{team}BlkPerPoss"]    = safe_divide(games_expanded_detailed[f"{team}Blk"],   games_expanded_detailed[f"{other}Possessions"])
    total_possessions = games_expanded_detailed[f"{team}Possessions"] + games_expanded_detailed[f"{other}Possessions"]
    games_expanded_detailed[f"{team}PFPerPoss"]     = safe_divide(games_expanded_detailed[f"{team}Stl"], total_possessions)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Season</th>
      <th>DayNum</th>
      <th>NumOT</th>
      <th>Side</th>
      <th>TeamID</th>
      <th>OppTeamID</th>
      <th>Win</th>
      <th>Score</th>
      <th>OppScore</th>
      <th>Loc</th>
      <th>...</th>
      <th>OppFG3Percent</th>
      <th>OppFTPercent</th>
      <th>OppORPercent</th>
      <th>OppAstPercent</th>
      <th>OppAtt3Percent</th>
      <th>OppPointsPerPoss</th>
      <th>OppTOPerPoss</th>
      <th>OppStlPerPoss</th>
      <th>OppBlkPerPoss</th>
      <th>OppPFPerPoss</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2003</td>
      <td>10</td>
      <td>0</td>
      <td>Men</td>
      <td>1104</td>
      <td>1328</td>
      <td>1</td>
      <td>68</td>
      <td>62</td>
      <td>N</td>
      <td>...</td>
      <td>0.2</td>
      <td>0.727273</td>
      <td>0.294118</td>
      <td>0.363636</td>
      <td>0.188679</td>
      <td>0.877193</td>
      <td>0.254669</td>
      <td>0.120128</td>
      <td>0.026695</td>
      <td>0.061813</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2003</td>
      <td>10</td>
      <td>0</td>
      <td>Men</td>
      <td>1272</td>
      <td>1393</td>
      <td>1</td>
      <td>70</td>
      <td>63</td>
      <td>N</td>
      <td>...</td>
      <td>0.25</td>
      <td>0.45</td>
      <td>0.416667</td>
      <td>0.291667</td>
      <td>0.358209</td>
      <td>0.929204</td>
      <td>0.176991</td>
      <td>0.117028</td>
      <td>0.087771</td>
      <td>0.058754</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2003</td>
      <td>11</td>
      <td>0</td>
      <td>Men</td>
      <td>1266</td>
      <td>1437</td>
      <td>1</td>
      <td>73</td>
      <td>61</td>
      <td>N</td>
      <td>...</td>
      <td>0.115385</td>
      <td>0.608696</td>
      <td>0.54386</td>
      <td>0.409091</td>
      <td>0.356164</td>
      <td>0.951341</td>
      <td>0.187149</td>
      <td>0.031368</td>
      <td>0.078419</td>
      <td>0.01564</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2003</td>
      <td>11</td>
      <td>0</td>
      <td>Men</td>
      <td>1296</td>
      <td>1457</td>
      <td>1</td>
      <td>56</td>
      <td>50</td>
      <td>N</td>
      <td>...</td>
      <td>0.272727</td>
      <td>0.533333</td>
      <td>0.472222</td>
      <td>0.5</td>
      <td>0.44898</td>
      <td>0.868056</td>
      <td>0.329861</td>
      <td>0.069396</td>
      <td>0.052047</td>
      <td>0.03471</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2003</td>
      <td>11</td>
      <td>0</td>
      <td>Men</td>
      <td>1400</td>
      <td>1208</td>
      <td>1</td>
      <td>77</td>
      <td>71</td>
      <td>N</td>
      <td>...</td>
      <td>0.375</td>
      <td>0.62963</td>
      <td>0.488372</td>
      <td>0.5</td>
      <td>0.258065</td>
      <td>1.129135</td>
      <td>0.159033</td>
      <td>0.109856</td>
      <td>0.015694</td>
      <td>0.055292</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>401175</th>
      <td>2025</td>
      <td>131</td>
      <td>0</td>
      <td>Women</td>
      <td>3413</td>
      <td>3471</td>
      <td>0</td>
      <td>66</td>
      <td>75</td>
      <td>H</td>
      <td>...</td>
      <td>0.210526</td>
      <td>0.678571</td>
      <td>0.235294</td>
      <td>0.384615</td>
      <td>0.306452</td>
      <td>0.969995</td>
      <td>0.142266</td>
      <td>0.080906</td>
      <td>0.013484</td>
      <td>0.039609</td>
    </tr>
    <tr>
      <th>401176</th>
      <td>2025</td>
      <td>132</td>
      <td>0</td>
      <td>Women</td>
      <td>3476</td>
      <td>3192</td>
      <td>0</td>
      <td>49</td>
      <td>66</td>
      <td>A</td>
      <td>...</td>
      <td>0.142857</td>
      <td>0.944444</td>
      <td>0.3125</td>
      <td>0.478261</td>
      <td>0.381818</td>
      <td>1.065891</td>
      <td>0.145349</td>
      <td>0.129534</td>
      <td>0.016192</td>
      <td>0.064683</td>
    </tr>
    <tr>
      <th>401177</th>
      <td>2025</td>
      <td>132</td>
      <td>0</td>
      <td>Women</td>
      <td>3119</td>
      <td>3250</td>
      <td>0</td>
      <td>62</td>
      <td>74</td>
      <td>A</td>
      <td>...</td>
      <td>0.357143</td>
      <td>0.882353</td>
      <td>0.277778</td>
      <td>0.555556</td>
      <td>0.311111</td>
      <td>1.184379</td>
      <td>0.240077</td>
      <td>0.096154</td>
      <td>0.0</td>
      <td>0.048046</td>
    </tr>
    <tr>
      <th>401178</th>
      <td>2025</td>
      <td>132</td>
      <td>0</td>
      <td>Women</td>
      <td>3125</td>
      <td>3293</td>
      <td>0</td>
      <td>62</td>
      <td>83</td>
      <td>N</td>
      <td>...</td>
      <td>0.5</td>
      <td>0.866667</td>
      <td>0.185185</td>
      <td>0.75</td>
      <td>0.518519</td>
      <td>1.209913</td>
      <td>0.189504</td>
      <td>0.028918</td>
      <td>0.043378</td>
      <td>0.014518</td>
    </tr>
    <tr>
      <th>401179</th>
      <td>2025</td>
      <td>132</td>
      <td>0</td>
      <td>Women</td>
      <td>3144</td>
      <td>3456</td>
      <td>0</td>
      <td>63</td>
      <td>66</td>
      <td>N</td>
      <td>...</td>
      <td>0.347826</td>
      <td>0.571429</td>
      <td>0.131579</td>
      <td>0.333333</td>
      <td>0.365079</td>
      <td>0.941781</td>
      <td>0.128425</td>
      <td>0.087873</td>
      <td>0.043937</td>
      <td>0.043365</td>
    </tr>
  </tbody>
</table>
<p>401180 rows × 61 columns</p>
</div>



I ended up not using PointsPerPoss

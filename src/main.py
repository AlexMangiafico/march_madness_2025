import src.train, src.predict, src.oddstrader_comparison, src.backtest, src.ratings, src.simulate, src.visualize


if __name__ == "__main__":
    #TODO General ideas: include other features like coach experience, conference stats

    #Define params
    rating_metrics = ['Score', 'Possessions', 'FGPercent', 'FG3Percent', 'Att3Percent', 'FTPercent', 'ORPercent',
                      'AstPercent', 'PointsPerPoss', 'TOPerPoss', 'StlPerPoss', 'BlkPerPoss', 'PFPerPoss']
    begin_train_year = 2021
    start_predict = 2021
    end_predict = 2025


    #Produce Rating csvs
    training_games = src.train.get_training_games_stats()
    src.ratings.build_rating_features(training_games, rating_metrics)


    #Train models
    training_matchups = training_games[['Season', 'Side', 'TeamID', 'OppTeamID', 'Loc', 'OppLoc', 'Win']].copy()
    training_matchups = training_matchups[training_matchups['Season'] >= begin_train_year]
    matchups_features = src.train.add_rating_features_to_matchups(training_matchups, rating_metrics)
    src.train.train_models(matchups_features, ['lr', 'rf', 'nn'])


    #Make predictions
    src.predict.predict_all_possible_matchups(start_predict, end_predict, rating_metrics)

    #Compare to betting markets
    src.oddstrader_comparison.main()

    #Backtest on previous tournaments
    src.backtest.backtest_predicted_years(['lr', 'rf', 'nn'])

    #Display results for this year's tournaments
    year = 2025

    for side in ['Women', 'Men']:
        src.simulate.simulate_proba(year, side, 'lr')
        src.simulate.simulate_bracket(year, side, 'lr', 1)
        src.visualize.advancement_heatmap(year, side, 'lr')
        src.visualize.tree_diagram(year, side, 'lr')

    #Make kaggle submission
    src.predict.save_kaggle_submission(year)

# 🏀 March Madness 2025  

This project provides a set of Python scripts to simulate and analyze tournament data. The scripts are designed to handle data loading, backtesting, model training, and evaluation of tournament advancement probabilities, as well as generating visualizations of these probabilities and outcomes.

## Table of Contents

- [`Project Structure`](#project-structure)
- [`File Descriptions`](#file-descriptions)
- [`Usage and Contributing`](#usage-and-contributing)
- [`Future Improvements`](#future-improvements)

## Project Structure

The project is organized as follows:

- **src/**: Contains all the source code for the project, including the core scripts for training, evaluating, and running simulations.
 
  - [`main`](#main): Main script to execute the simulation.
  - [`data_loader`](#data-loader): Loads and preprocesses the input data.
  - [`metrics`](#metrics): Evaluation metrics for model performance.
  - [`ratings`](#ratings): Computes team or player ratings based on performance.
  - [`model`](#model): Model definitions and training logic.
  - [`train`](#train): Trains the model on the input data.
  - [`predict`](#predict): Makes predictions based on the trained model.
  - [`oddstrader_comparison`](#oddstrader-comparison): Compares model predictions with betting odds.
  - [`backtest`](#backtest): Backtest the simulation results.
  - [`simulate`](#simulate): Runs simulations of tournament outcomes.
  - [`visualize`](#visualize): Generates plots and visualizations.
- **stored_csvs/**: Stores CSV files with the results of predictions made during the simulation (e.g., predictions for tournament outcomes).
- **models/**: Stores the trained machine learning models used to make predictions.
- **kaggle_data/**: Contains raw input data required for the simulation, including tournament data and player statistics.


---

## File Descriptions

### Main

The `main.py` script serves as the entry point for running the entire simulation and analysis process. It ties together various functions from other scripts (like `train`, `predict`, `visualize`) and orchestrates the flow of data through the pipeline.

**Key Functions**:
- Run simulations and training pipelines.
- Coordinate the use of other modules and scripts.
- Output results such as plots and model metrics.

---

### Data Loader

The `data_loader.py` script handles the loading and preprocessing of data. It reads raw data from external files, cleans, and formats it for use in model training and evaluation.

**Key Functions**:
- Load tournament data (e.g., seed information, team performance).
- Clean and preprocess data for use in simulations and models.
- Save processed data in a usable format for other scripts.

---

### Metrics

The `metrics.py` script defines functions for evaluating model performance. It calculates various performance metrics, such as accuracy, precision, recall, and F1 score, for assessing how well the models are predicting tournament outcomes.

**Key Functions**:
- Compute standard evaluation metrics like accuracy and F1 score.
- Generate confusion matrices and other visualization tools for model evaluation.
- Provide insights into the strengths and weaknesses of each model.

---

### Ratings

The `ratings.py` script calculates and maintains player and team ratings based on historical data. This is used to assess the strength of teams and how likely they are to succeed in the tournament.

**Key Functions**:
- Calculate player and team ratings using statistical methods (e.g., Elo ratings).
- Update ratings after each tournament or season.
- Provide insights into team strength and ranking.

---

### Model

The `model.py` script defines the machine learning models used for tournament prediction. This may include a variety of models such as logistic regression, random forests, or neural networks.

**Key Functions**:
- Train machine learning models to predict team advancement probabilities.
- Perform hyperparameter tuning and model selection.
- Save and load trained models for prediction purposes.

---

### Train

The `train.py` script trains machine learning models using the tournament data. It uses algorithms to learn from historical data and generate a predictive model for future tournaments.

**Key Functions**:
- Train models on historical tournament data.
- Perform feature selection and engineering.
- Save trained models for future predictions and evaluations.

---

### Predict

The `predict.py` script is responsible for using trained models to make predictions on new, unseen data. It generates predictions for tournament outcomes and other key metrics.

**Key Functions**:
- Use trained models to predict tournament outcomes for a given season.
- Output predicted probabilities of team advancement.
- Integrate with other scripts for visualization and analysis.

---

### Oddstrader Comparison

The `oddstrader_comparison.py` script compares the results of the simulation against actual betting odds data to evaluate how well the model predictions match up with real-world odds.

DISCLAIMER: This comparison is purely for comparing the model's performance to outside predictions. This project as a whole is not advice for sports betting and has not been shown to outperform public markets.

**Key Functions**:
- Fetch and process betting odds data from external sources.
- Compare model predictions with betting odds.
- Analyze discrepancies between the model's predictions and actual odds.

---

### Backtest

The `backtest.py` script is responsible for evaluating the performance of different models and strategies using historical data. It runs simulations over a set period, compares different models, and produces performance metrics.

**Key Functions**:
- Run simulations on historical tournament data.
- Compare model predictions against actual outcomes.
- Produce evaluation metrics to assess model performance.

---

### Simulate

The `simulate.py` script performs the core simulation of the tournament. It runs Monte Carlo simulations or other probabilistic methods to simulate multiple tournament outcomes based on model predictions.

**Key Functions**:
- Run Monte Carlo simulations to generate tournament outcomes.
- Use model predictions to simulate the likelihood of each team advancing through the rounds.
- Output simulation results for analysis and visualization.

---

### Visualize

The `visualize.py` script generates visualizations of the tournament data and simulation results. It includes functionality for plotting heatmaps, tree diagrams, and other visual representations of team advancement probabilities.

**Key Functions**:
- Create heatmaps of team advancement probabilities across rounds.
- Generate tree diagrams to visualize tournament brackets and team progress.
- Customize visualizations to improve readability and understanding.

**Output**

![Men Heatmap](images/heatmap_Men_2025.png)
*Description*: A heatmap representing the probability of each team advancing through different tournament rounds.

![Women Heatmap](images/heatmap_Women_2025.png)
*Description*: A heatmap representing the probability of each team advancing through different tournament rounds.

![Men Probabilistic Bracket](images/bracket_Men_2025.png)
*Description*: A bracket representing the probability of each team advancing through different tournament rounds.

![Women Probabilistic Bracket](images/bracket_Women_2025.png)
*Description*: A bracket representing the probability of each team advancing through different tournament rounds.

---

## Usage and Contributing

1. Clone this repository:  
   ```bash
   git clone https://github.com/yourusername/march-madness-projections.git
   cd march-madness-projections
   ```  
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
3. Run the main script:  
   ```bash
   python src/main.py
   ```  
## Results

Follow my progress at https://www.kaggle.com/competitions/march-machine-learning-mania-2025/leaderboard#

## Future Improvements  
- **More Advanced Models**
- **Interactive Visualizations**  
- **Automated Data Updates**
- **Mid-Tournament Ratings Updates**

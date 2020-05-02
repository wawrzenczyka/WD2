#%% load data
import pandas as pd
import numpy as np
df = pd.read_csv("ceidg_data_surv.csv")

#%% add TerminationPeriod column
df = df.drop(df.loc[df.Status == "Aktywny"].index)

df.loc[df.DurationOfExistenceInMonths < 12, "TerminationPeriod"] = 0
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 12, df.DurationOfExistenceInMonths < 24), "TerminationPeriod"] = 1
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 24, df.DurationOfExistenceInMonths < 36), "TerminationPeriod"] = 2
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 36, df.DurationOfExistenceInMonths < 48), "TerminationPeriod"] = 3
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 48, df.DurationOfExistenceInMonths < 60), "TerminationPeriod"] = 4
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 60, df.DurationOfExistenceInMonths < 72), "TerminationPeriod"] = 5
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 72, df.DurationOfExistenceInMonths < 84), "TerminationPeriod"] = 6
df.loc[np.logical_and(df.DurationOfExistenceInMonths >= 84, df.DurationOfExistenceInMonths < 96), "TerminationPeriod"] = 7
df.loc[df.DurationOfExistenceInMonths >= 96, "TerminationPeriod"] = 8

#%% fix voivodeships
import unicodedata

voivodeships = ['dolnoslaskie', 'kujawsko-pomorskie', \
    'lubelskie', 'lubuskie', 'lodzkie', 'malopolskie', \
    'mazowieckie', 'opolskie', 'podkarpackie', 'podlaskie', \
    'pomorskie', 'slaskie', 'swietokrzyskie', 'warminsko-mazurskie', \
    'wielkopolskie', 'zachodniopomorskie']

def fix_voivodeships(voivodeship):
    if type(voivodeship) != str:
        return None
    voivodeship = voivodeship.lower()
    voivodeship = voivodeship.replace('ł', 'l')
    normalized = ''.join(c for c in unicodedata.normalize('NFKD', voivodeship) if unicodedata.category(c) != 'Mn')
    if normalized not in voivodeships:
        return None
    else:
        return normalized

df.MainAddressVoivodeship = df.MainAddressVoivodeship.apply(fix_voivodeships)

# %% prepare clf input
def makeX(dataframe):
    X = dataframe[['HasLicences', \
                  'PKDMainDivision', \
                  'PKDMainSection', \
                  'MainAddressVoivodeship', \
                  'ShareholderInOtherCompanies', \
                  'IsPhoneNo', \
                  'IsEmail', \
                  'Sex']]
    X = X.astype(str)
    X['PKDMainDivision'] = X['PKDMainDivision'].apply(lambda x: x[0:-2])
    return X

X = makeX(df)
y = df['TerminationPeriod']

#%% preprocessing
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

categorical_columns = ['HasLicences', 'PKDMainDivision', 'PKDMainSection', \
    'MainAddressVoivodeship', 'ShareholderInOtherCompanies', \
    'IsPhoneNo', 'IsEmail', 'Sex']

numerical_columns = []

X = X[categorical_columns + numerical_columns]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=1/3, random_state=42)

categorical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])
numerical_pipe = Pipeline([
    ('imputer', SimpleImputer(strategy='mean'))
])

preprocessing = ColumnTransformer(
    [('cat', categorical_pipe, categorical_columns),
     ('num', numerical_pipe, numerical_columns)])

#%% Classifier
from sklearn.ensemble import RandomForestClassifier

clf = Pipeline([
    ('preprocess', preprocessing),
    ('classifier', RandomForestClassifier(n_estimators=100, \
        max_features=16, min_samples_leaf=2, n_jobs=6))
], verbose=True)

#%% Grid Search
# from sklearn.model_selection import GridSearchCV

# parameters = {'classifier__max_features':np.arange(2,15), \
#     'classifier__n_estimators':[100,500,1000, 1500], \
#     'classifier__min_samples_leaf': [1,2,3,4,5,7,10]}
# clf = GridSearchCV(clf, param_grid=parameters, cv = 5)

#%% fit
clf.fit(X_train, y_train)
print("clf train score: %0.3f" % clf.score(X_train, y_train))
print("clf test score: %0.3f" % clf.score(X_test, y_test))

#%% dump model
from joblib import dump

dump(clf, "model.joblib")
#%% load model
from joblib import load

clf = load("model.joblib")

#%% mean_absolute_error
from sklearn.metrics import mean_absolute_error

mean_absolute_error(y_test, clf.predict(X_test))
#%% predict
ind = 1

print("Real value: %0.0f" % df.loc[df.index==ind].TerminationPeriod)
print("Predicted value:", clf.predict(makeX(df.loc[df.index==ind])))
print("Predicted value:", clf.predict_proba(makeX(df.loc[df.index==ind])))

# %% visualize feature importance
from sklearn.inspection import permutation_importance
import matplotlib.pyplot as plt

result = permutation_importance(clf, X_train, y_train, n_repeats=1,
                                random_state=42, n_jobs=6)
sorted_idx = result.importances_mean.argsort()

fig, ax = plt.subplots()
ax.boxplot(result.importances[sorted_idx].T,
           vert=False, labels=X_test.columns[sorted_idx])
ax.set_title("Permutation Importances")
plt.show()

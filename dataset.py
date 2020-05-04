import pandas as pd
import os


def load_raw():
    return pd.read_csv('ceidg_data_surv.csv')


def load():
    dfpath = './ceidg_data_surv_formatted.csv'
    if os.path.isfile(dfpath):
        return pd.read_csv(dfpath)
    else:
        df = format_raw(load_raw())
        df.to_csv(dfpath, index=False)
        return df


def format_raw(df_raw):
    df = df_raw

    # drop unnecessary columns
    df = df.drop([
        'YearOfStartingOfTheBusiness',
        'MainAddressTERC',
        'CorrespondenceAddressTERC'
    ], axis=1)

    # format dates
    df['DateOfStartingOfTheBusiness'] = pd.to_datetime(df['DateOfStartingOfTheBusiness'], format='%Y-%m-%d')
    df['DateOfTermination'] = pd.to_datetime(df['DateOfTermination'], format='%Y-%m-%d')

    # add year of termination
    df['YearOfTermination'] = df['DateOfTermination'].dt.year

    # fix voivodes names
    df = df.replace(['DOLNOSLąSKIE', 'DOLNOśLąSKIE', 'DOLNOSLĄSKIE', 'DOLNOŚLASKIE', 'DOLNOśLASKIE', 'DOLONOśLąSKIE'], 'DOLNOŚLĄSKIE')\
        .replace(['KUJ POMORSKIE', 'KUJAWSKOPOMORSKIE', 'KUAWSKOPOMORSKIE', 'KUJ.POM.', 'KUJAWAKO-POMORSKIE', 'KUJAWSKO POM', 'KUJAWSKO POMORSKIE', 'KUJAWSKO-POMO', 'KUJAWSKO-POMORSKIE', 'KUJWASKO POMORSKIE'], 'KUJAWSKO-POMORSKIE')\
        .replace(['ŁóDZKIE', 'łODZKIE', 'łÓDZKIE', 'łóDZKIE', 'ŁóDź', 'ŁóZKIE'], 'ŁÓDZKIE')\
        .replace(['MAŁOPLSKIE', 'MAŁOPOLSKA', 'MAłOPOLSKIE', 'MALOPOLSKIE', 'MAŁOPOLSKIE', 'MAŁPOLSKIE', 'MAł.'], 'MAŁOPOLSKIE')\
        .replace(['MAZOPWIECKIE', 'MAZOWIECKEI', 'MAZWIECKIE'], 'MAZOWIECKIE')\
        .replace(['POMORSKI'], 'POMORSKIE')\
        .replace(['ŚLąSKIE', 'śLASKIE', 'śLąSKIE', 'ŚLASKIE'], 'ŚLĄSKIE')\
        .replace(['ŚWIETOKRZYSKIE', 'ŚWIęTOKRZYSKIE', 'śWIęTOKRZYSKIE', 'SWIĘTOKTRZYSKIE', '�WI�TOKRZYSKIE', 'SWIETOKRZYSKIE'], 'ŚWIĘTOKRZYSKIE')\
        .replace(['WARMIńSKO-MAZURSKIE', 'WARMI�SKO-MAZURSKIE', 'WARMIńSKO-MAZURSKIEGO', 'WARM-MAZ', 'WARMIńSKIO-MAZURSKIE', 'WARMIńSKK-MAZURSKIE', 'WARMIńSKO MAZURSKIE', 'WARMIńSKO-MAZURSKIOE'], 'WARMIŃSKO-MAZURSKIE')\
        .replace(['WIELKOPOLSKA', 'WIELKOPOLSKI', 'WIELSKOPOLSKIE', 'WIELKOPOSKIE', 'WIELKOPOSLKIE'], 'WIELKOPOLSKIE')\
        .replace(['ZACHODNIOPOMORSKI', 'ZACHODNO-POMORSKIE', 'ZACHONDIOPOMORSKIE', 'ZACHDODNIOPOMORSKIE', 'ZACHODNIOPOMRSKIE', 'ZACHODNIPOMORSKIE'], 'ZACHODNIOPOMORSKIE')

    # delete all records with invalid voivodes
    voivodes = [
        'DOLNOŚLĄSKIE',
        'KUJAWSKO-POMORSKIE',
        'LUBELSKIE',
        'LUBUSKIE',
        'ŁÓDZKIE',
        'MAŁOPOLSKIE',
        'MAZOWIECKIE',
        'OPOLSKIE',
        'PODKARPACKIE',
        'PODLASKIE',
        'POMORSKIE',
        'ŚLĄSKIE',
        'ŚWIĘTOKRZYSKIE',
        'WARMIŃSKO-MAZURSKIE',
        'WIELKOPOLSKIE',
        'ZACHODNIOPOMORSKIE'
    ]
    df = df[(df['MainAddressVoivodeship'].isin(voivodes)) & (df['CorrespondenceAddressVoivodeship'].isin(voivodes))]

    # change voivodes to lower
    df['MainAddressVoivodeship'] = df['MainAddressVoivodeship'].str.lower()
    df['CorrespondenceAddressVoivodeship'] = df['CorrespondenceAddressVoivodeship'].str.lower()

    # format county
    df['MainAddressCounty'] = df['MainAddressCounty'].str.lower()\
        .replace('ą', 'a', regex=True)\
        .replace('ć', 'c', regex=True)\
        .replace('ę', 'e', regex=True)\
        .replace('ł', 'l', regex=True)\
        .replace('ń', 'n', regex=True)\
        .replace('ó', 'o', regex=True)\
        .replace('ś', 's', regex=True)\
        .replace('ź', 'z', regex=True)\
        .replace('ż', 'z', regex=True)
    df['CorrespondenceAddressCounty'] = df['CorrespondenceAddressCounty'].str.lower()\
        .replace('ą', 'a', regex=True)\
        .replace('ć', 'c', regex=True)\
        .replace('ę', 'e', regex=True)\
        .replace('ł', 'l', regex=True)\
        .replace('ń', 'n', regex=True)\
        .replace('ó', 'o', regex=True)\
        .replace('ś', 's', regex=True)\
        .replace('ź', 'z', regex=True)\
        .replace('ż', 'z', regex=True)

    # add voivode names for counties that appear in multiple voivodes
    tmp_df = df[df['MainAddressCounty'].isin([
        'nowodworski',
        'opolski',
        'krosnienski',
        'brzeski',
        'grodziski',
        'tomaszowski',
        'swidnicki'
    ])]
    df.loc[tmp_df.index, 'MainAddressCounty'] = tmp_df['MainAddressVoivodeship'] + '/' + tmp_df['MainAddressCounty']

    return df

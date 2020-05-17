import pandas as pd
import os
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def load_raw():
    return pd.read_csv(os.path.join(THIS_FOLDER, 'data', 'ceidg_data_surv.csv'), encoding="utf-8")


def load():
    dfpath = os.path.join(THIS_FOLDER, 'data', 'ceidg_data_surv_formatted.csv')
    if os.path.isfile(dfpath):
        return pd.read_csv(dfpath, encoding="utf-8")
    else:
        df = format_raw(load_raw())
        df.to_csv(dfpath, index=False, encoding="utf-8")
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
    df = df[df['MainAddressVoivodeship'].isin(voivodes)]

    # change voivodes to lower
    df['MainAddressVoivodeship'] = df['MainAddressVoivodeship'].str.lower()

    # format county
    df['MainAddressCounty'] = replace_polish_chars(df['MainAddressCounty'].str.lower(), regex=True)

    # add voivode names for counties that appear in multiple voivodes
    tmp_df = df[df['MainAddressCounty'].isin([
        'nowodworski',
        'opolski',
        'krosnienski',
        'brzeski',
        'grodziski',
        'tomaszowski',
        'swidnicki',
        'bielski',
        'sredzki',
        'ostrowski'
    ])]
    df.loc[tmp_df.index, 'MainAddressCounty'] = replace_polish_chars(tmp_df['MainAddressVoivodeship'].str.lower(), regex=True)\
        + '/' + tmp_df['MainAddressCounty']

    return df


def replace_polish_chars(obj, **kwargs):
    return obj\
        .replace('ą', 'a', **kwargs)\
        .replace('ć', 'c', **kwargs)\
        .replace('ę', 'e', **kwargs)\
        .replace('ł', 'l', **kwargs)\
        .replace('ń', 'n', **kwargs)\
        .replace('ó', 'o', **kwargs)\
        .replace('ś', 's', **kwargs)\
        .replace('ź', 'z', **kwargs)\
        .replace('ż', 'z', **kwargs)
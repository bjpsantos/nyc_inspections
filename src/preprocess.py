import pandas as pd
import logging
# add log

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Preprocess:
    """ This class handles the initial preprocessing, cleaning and aggregation.
    """
    def __init__(self,):
        self.date_columns = ['inspection_date', 'record_date', 'grade_date'] 

    def convert_date_columns(self, df):
        
        for col in self.date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        logging.info(f"Converted date columns: {self.date_columns} to datetime format.")
        return df
    
    def remove_not_yet_inspected(self, df):
        
        df = df[df['inspection_date'] != '1900-01-01 00:00:00']
        logging.info(f"Sample size after removing 1/1/1900 entries: {df.shape}")
        return df
    
    def remove_covid_period(self, df):

        logging.info(f"{df[(df['inspection_date']>= '2020-03-17') & (df['inspection_date'] < '2021-07-19')].sort_values(by='inspection_date').shape[0]} inspections took place during COVID-19 (March 17, 2020 - July 19, 2021)")

        df = df[(df['inspection_date']< '2020-03-17') | (df['inspection_date'] >= '2021-07-19')]

        logging.info(f"Sample size after removing COVID-19 inspections: {df.shape}")

        return df

    def select_gradable_inspections(self, df):
        df_gradable_inspection = df[(df['inspection_type'].isin(['Cycle Inspection / Initial Inspection', 
                                                                'Cycle Inspection / Re-inspection', 
                                                                'Pre-permit (Operational) / Initial Inspection', 
                                                                'Pre-permit (Operational) / Re-inspection',
                                                                ]))
                                        & (df['action'].isin(['Violations were cited in the following area(s).', 
                                                                'No violations were recorded at the time of this inspection.', 
                                                                ])
                                                                | df['action'].str.contains('Establishment Closed by DOHMH', case=False)
                                        )
                                        & (df['inspection_date'] >= '2010-07-27')].copy()
        logging.info(f"Sample size after filtering for gradable inspections: {df_gradable_inspection.shape}")
        return df_gradable_inspection
    

    def compute_grade(self, df_gradable_inspection):

        logging.info(f"Computing grades based on scores. Initial grades: {df_gradable_inspection['grade'].unique()}")

        df_gradable_inspection.loc[:,'computed_grade'] = df_gradable_inspection['score'].apply(
    lambda x: 'A' if x <= 13 else ('B' if x <= 27 else 'C'

    ))
        logging.info(f"Computed grades based on scores. Final grades: {df_gradable_inspection['computed_grade'].unique()}")

        ## check if there are any discrepancies between the computed grades and the existing grades
        mask = df_gradable_inspection['grade'].isin(['A', 'B', 'C']) & (df_gradable_inspection['computed_grade'] != df_gradable_inspection['grade'])

        logging.info(f"Found {df_gradable_inspection.loc[mask].shape[0]} entries where the grade is not aligned with the score. Computed grades will be used for these entries.")

        return df_gradable_inspection
    
    def aggregate_data_per_inspection(self, df_gradable_inspection):

        # double check that there are no multiple inspection types, actions or grades, for a single camis/inspection_date.
        # Several violation_codes are to be expected.

        assert df_gradable_inspection.groupby(['camis', 'inspection_date'])[['inspection_type', 'action', 'grade', 'violation_code']].nunique().reset_index()['inspection_type'].max() == 1, "There are multiple inspection types  for a single camis/inspection_date in df_gradable_inspection"

        assert df_gradable_inspection.groupby(['camis', 'inspection_date'])[['inspection_type', 'action', 'grade', 'violation_code']].nunique().reset_index()['action'].max() == 1, "There are multiple actions for a single camis/inspection_date in df_gradable_inspection"

        assert df_gradable_inspection.groupby(['camis', 'inspection_date'])[['inspection_type', 'action', 'grade', 'violation_code']].nunique().reset_index()['grade'].max() == 1, "There are multiple grades for a single camis/inspection_date in df_gradable_inspection"

        # Aggregate
        df_agg = df_gradable_inspection.groupby(['camis', 'inspection_date']).agg({
            'inspection_type': lambda x: x.unique()[0],
            'grade': 'first',
            'computed_grade': lambda x: x.unique()[0],
            'action': lambda x: x.unique()[0],
            'boro': 'first',
            'cuisine_description': 'first',
            'latitude': 'first',
            'longitude': 'first',
            'critical_flag': lambda x:  list(x),
            'violation_code': lambda x: list(x.dropna())        #an empty list here implies no violations
        }).rename(columns={'grade': 'original_grade'}).reset_index().sort_values(by=['camis', 'inspection_date'])

        logging.info(f"Aggregated data per inspection. Sample size: {df_agg.shape}")
        return df_agg




    def clean_data(self, data):
        """
        Preprocess the input DataFrame.
        
        Parameters:
        data (DataFrame): The DataFrame to preprocess.
        
        Returns:
        DataFrame: The preprocessed DataFrame.
        """
        logging.info("Starting preprocessing of data.")
        df = data.copy()
        logging.info(f"Initial sample size: {df.shape}")

        # Remove duplicate entries
        df.drop_duplicates(inplace=True)
        logging.info(f"Sample size after removing duplicates: {df.shape}")

        # Convert date columns to datetime
        df = self.convert_date_columns(df)
        # Remove entries with inspection date as '1900-01-01 00:00:00'
        df = self.remove_not_yet_inspected(df)

        df = self.remove_covid_period(df)

        # Filter for gradable inspections
        df_gradable_inspection = self.select_gradable_inspections(df)

        # Compute grades based on scores
        df_gradable_inspection = self.compute_grade(df_gradable_inspection)

        # Aggregate data per inspection
        df_agg = self.aggregate_data_per_inspection(df_gradable_inspection)


        return df_gradable_inspection, df_agg
        
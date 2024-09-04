import snowflake.snowpark.functions as F


def feature_engineering(application_record):
    """
    Applies feature engineering to the application record.
    """
    return application_record.with_column(
        'CNT_CHILDREN_IND', F.iff(F.col('CNT_CHILDREN') >= 2, "2+", F.to_varchar(F.col('CNT_CHILDREN')))
    ).drop('CNT_CHILDREN').with_column(
        'CNT_FAMILY_IND', F.iff(F.col('CNT_FAM_MEMBERS') >= 3, "3+", F.to_varchar(F.col('CNT_FAM_MEMBERS')))
    ).drop('CNT_FAM_MEMBERS').with_column(
        'AGE', F.abs(F.floor(F.col('DAYS_BIRTH') / 365))
    ).drop('DAYS_BIRTH').with_column(
        'WORKYEAR', F.abs(F.floor(F.col('DAYS_EMPLOYED') / 365))
    ).filter(F.col('WORKYEAR') < 50).drop('DAYS_EMPLOYED').with_column(
        'OCCUPATION_TYPE',
        F.iff(F.col('OCCUPATION_TYPE').in_(['Cleaning staff', 'Cooking staff', 'Drivers', 'Laborers', 'Low-skill Laborers', 'Security staff', 'Waiters/barmen staff']), 'LABOURWORK',
              F.iff(F.col('OCCUPATION_TYPE').in_(['Accountants', 'Core staff', 'HR staff', 'Medicine staff', 'Private service staff', 'Realty agents', 'Sales staff', 'Secretaries']), 'OFFICEWORK', 
                    F.iff(F.col('OCCUPATION_TYPE').in_(['Managers', 'High skill tech staff', 'IT staff']), 'HIGHTTECHWORK', 'OTHER')))
    )
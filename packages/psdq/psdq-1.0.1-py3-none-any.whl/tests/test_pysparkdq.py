from psdq import PySparkDQ
import pyspark.sql.functions as f

def test_values_in_list(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_in_list(colname='age',val_list=[30,25,35],tolerance=0.75, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_not_in_list(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_in_list(colname='age',val_list=[1,2,3],tolerance=1, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_null(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_null(colname='age', tolerance=0, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_not_null(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_null(colname='age', tolerance=1, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_equal(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_equal(colname='age', value=30, tolerance=0.25, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_not_equal(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_not_equal(colname='age', value=28, tolerance=0.75, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_between(spark_session_fixture, sample_data_name_age, sample_data_name_date):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)
    dq.values_between(colname='age', lower_value=30, upper_value=35, tolerance=0.501, over_under_tolerance='under', inclusive_exclusive='exclusive').evaluate()
    
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_date)
    dq.values_between(colname='birthday', lower_value='1990-01-01', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='inclusive').evaluate()

def test_values_greater_equal_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_greater_equal_than(colname='age', value=30, tolerance=0.501, over_under_tolerance='under', inclusive_exclusive='exclusive').evaluate()

def test_values_lower_equal_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_lower_equal_than(colname='age', value=30, tolerance=0.75, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_greater_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_greater_than(colname='age', value=30, tolerance=0.25, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_lower_than(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_lower_than(colname='age', value=30, tolerance=0.75, over_under_tolerance='under', inclusive_exclusive='inclusive').evaluate()

def test_values_custom_dq(spark_session_fixture, sample_data_name_age):
    dq = PySparkDQ(spark_session=spark_session_fixture, df=sample_data_name_age)

    dq.values_custom_dq(test='custom dq', partial=f.lower('name')=='john',
                                tolerance=0.25, over_under_tolerance='over').evaluate()

def test_get_row_level_qa(spark_session_fixture, sample_data_name_date):
    import datetime
    from pyspark.sql.dataframe import Row
    from pyspark.testing import assertDataFrameEqual
    from pyspark.sql.types import StructField, StructType, DateType, StringType, IntegerType, ArrayType

    # Arrange
    df_expected = spark_session_fixture.createDataFrame(data=[{'birthday': datetime.date(1992, 3, 31),
        'name': 'Alex',
        'pysparkdq_fail_count': 0,
        'pysparkdq_failed_tests': []},
        {'birthday': datetime.date(1990, 12, 15),
        'name': 'Alice',
        'pysparkdq_fail_count': 1,
        'pysparkdq_failed_tests': [Row(colname='name', test='values_in_list', scope="['Alex']")]},
        {'birthday': datetime.date(1985, 6, 12),
        'name': 'Bob',
        'pysparkdq_fail_count': 3,
        'pysparkdq_failed_tests': [Row(colname='birthday', test='values_between', scope='1990-01-01 - 1993-01-01'),
        Row(colname='birthday', test='values_between', scope='1990-01-02 - 1993-01-01'),
        Row(colname='name', test='values_in_list', scope="['Alex']")]},
        {'birthday': datetime.date(1964, 7, 22),
        'name': 'Eve',
        'pysparkdq_fail_count': 3,
        'pysparkdq_failed_tests': [Row(colname='birthday', test='values_between', scope='1990-01-01 - 1993-01-01'),
        Row(colname='birthday', test='values_between', scope='1990-01-02 - 1993-01-01'),
        Row(colname='name', test='values_in_list', scope="['Alex']")]}],
        schema=StructType(
            [StructField('birthday', DateType(), True), 
            StructField('name', StringType(), True), 
            StructField('pysparkdq_fail_count', IntegerType(), False), 
            StructField('pysparkdq_failed_tests', 
                         ArrayType(StructType([StructField('colname', StringType(), False), 
            StructField('test', StringType(), False), 
            StructField('scope', StringType(), False)]), False), False)])
    )
    
    # Act
    dq = PySparkDQ(spark_session_fixture, sample_data_name_date)
    test = dq.values_between(colname='birthday', lower_value='1990-01-01', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='exclusive')\
            .values_between(colname='birthday', lower_value='1990-01-02', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='inclusive') \
            .values_in_list(colname='name', val_list=['Alex'])
    df_result = test.get_row_level_qa()
    
    # Assert
    assertDataFrameEqual(df_result, df_expected)

def test_summary(spark_session_fixture, sample_data_name_date):
    from pyspark.sql.dataframe import Row
    from pyspark.testing import assertDataFrameEqual
    from pyspark.sql.types import StructField, StructType, DoubleType, StringType, LongType, BooleanType, IntegerType

    # Arrange
    df_expected = spark_session_fixture.createDataFrame(
        data = [{'colname': 'birthday',
                'test': 'values_between',
                'scope': '1990-01-01 - 1993-01-01',
                'found': 2,
                'total': 4,
                'found_percentage': 0.5,
                'tolerance': 0.5,
                'over_under_tolerance': 'over',
                'inclusive_exclusive': 'exclusive',
                'pass': False},
                {'colname': 'birthday',
                'test': 'values_between',
                'scope': '1990-01-02 - 1993-01-01',
                'found': 2,
                'total': 4,
                'found_percentage': 0.5,
                'tolerance': 0.5,
                'over_under_tolerance': 'over',
                'inclusive_exclusive': 'inclusive',
                'pass': True},
                {'colname': 'name',
                'test': 'values_in_list',
                'scope': "['Alex']",
                'found': 1,
                'total': 4,
                'found_percentage': 0.25,
                'tolerance': 1.0,
                'over_under_tolerance': 'over',
                'inclusive_exclusive': 'inclusive',
                'pass': False}],
        schema=StructType([StructField('colname', StringType(), True), 
                           StructField('test', StringType(), True), 
                           StructField('scope', StringType(), True), 
                           StructField('found', LongType(), True), 
                           StructField('total', IntegerType(), True), 
                           StructField('found_percentage', DoubleType(), True), 
                           StructField('tolerance', DoubleType(), True), 
                           StructField('over_under_tolerance', StringType(), True), 
                           StructField('inclusive_exclusive', StringType(), True), 
                           StructField('pass', BooleanType(), True)])
    )

    # Act
    dq = PySparkDQ(spark_session_fixture, sample_data_name_date)
    test = dq.values_between(colname='birthday', lower_value='1990-01-01', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='exclusive')\
            .values_between(colname='birthday', lower_value='1990-01-02', upper_value='1993-01-01', tolerance=0.5, over_under_tolerance='over', inclusive_exclusive='inclusive') \
            .values_in_list(colname='name', val_list=['Alex'])
    df_result = test.get_summary()

    # Assert
    assertDataFrameEqual(df_expected, df_result)
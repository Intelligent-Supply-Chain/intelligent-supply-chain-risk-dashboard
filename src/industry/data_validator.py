import pandas as pd


def validate_csv(file):
    """
    Validate an uploaded CSV file.
    """

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return None, [f"Unable to read CSV file: {e}"]

    errors = []
    warnings = []

    # Check whether the dataset is empty
    if df.empty:
        errors.append("The uploaded dataset is empty.")
        return df, errors

    # Check duplicate rows
    duplicate_count = df.duplicated().sum()

    if duplicate_count > 0:
        warnings.append(
            f"{duplicate_count} duplicate rows found."
        )

    # Check missing values
    missing_values = df.isnull().sum()
    missing_columns = missing_values[missing_values > 0]

    if len(missing_columns) > 0:
        for column, count in missing_columns.items():
            warnings.append(
                f"Column '{column}' contains {count} missing values."
            )

    return df, errors + warnings
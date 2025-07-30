import pandas as pd
from typing import Any, Dict, Optional


ID2AGGREGATION = {0: "NONE", 1: "SUM", 2: "AVERAGE", 3: "COUNT"}


def generate_financial_balance_sheet() -> pd.DataFrame:
    """
    Returns a sample financial balance sheet.

    Returns:
        pd.DataFrame: _description_
    """

    data = {
        "Breakdown": [
            "Total Assets",
            "Total Liabilities Net Minority Interest",
            "Total Equity Gross Minority Interest",
            "Total Capitalization",
            "Common Stock Equity",
            "Capital Lease Obligations",
            "Net Tangible Assets",
            "Working Capital",
            "Invested Capital",
            "Tangible Book Value",
            "Total Debt",
            "Share Issued",
            "Ordinary Shares Number",
        ],
        "12/31/2023": [
            106618000,
            43009000,
            63609000,
            65316000,
            62634000,
            4916000,
            62019000,
            20868000,
            67291000,
            62019000,
            9573000,
            3185000,
            3185000,
        ],
        "12/31/2022": [
            82338000,
            36440000,
            45898000,
            45733000,
            44704000,
            3703000,
            44111000,
            14208000,
            46749000,
            44111000,
            5748000,
            3164000,
            3164000,
        ],
        "12/31/2021": [
            62131000,
            30548000,
            31583000,
            34443000,
            30189000,
            3531000,
            28472000,
            7395000,
            35531000,
            28472000,
            8873000,
            3099000,
            3099000,
        ],
        "12/31/2020": [
            52148000,
            28469000,
            23679000,
            30738000,
            22225000,
            3008000,
            21705000,
            12469000,
            32496000,
            21705000,
            13279000,
            2880000,
            2880000,
        ],
    }

    df = pd.DataFrame(data)

    df = df.astype(str)
    return df


def get_real_tapas_answer(
        table: pd.DataFrame, 
        model: object, # TapasModel or similar
        tokenizer: object,  # TapasModel or similar
        inputs: object,  # BatchEncoding or similar 
        id2aggregation: Optional[Dict[int, str]]=None
        ) -> Any:
    """
    Converts the model's output to a real answer.

    Args:
        table (pd.DataFrame): The table data.
        model (TapasModel): Tapas model
        tokenizer (TapasTokenizer): Tapas tokenizer
        inputs (BatchEncoding): inputs to the model
        id2aggregation (Optional[Dict[int, str]], optional): Defaults to None.

    Raises:
        ValueError: If the predicted aggregation is unknown.

    Returns:
        Any: The answer.
    """
    if not isinstance(table, pd.DataFrame):
        raise TypeError("`table` must be a pandas DataFrame.")
    if table.empty:
        raise ValueError("`table` must not be empty.")
    if id2aggregation is None:
        id2aggregation = ID2AGGREGATION

    table = table.astype(str)

    try:
        outputs = model(**inputs)
        predicted_answer_coordinates, predicted_aggregation_indices = tokenizer.convert_logits_to_predictions(
            inputs, outputs.logits.detach(), outputs.logits_aggregation.detach()
        )
        predicted_answer_coordinates = predicted_answer_coordinates[0]
    except Exception as e:
        raise ValueError(f"Error generating predictions: {e}")
    
    predicted_aggregation = id2aggregation.get(predicted_aggregation_indices[0])
    if predicted_aggregation is None:
        raise ValueError(f"Unknown aggregation type index: {predicted_aggregation_indices[0]}")

    try:
        if predicted_aggregation == "NONE":
            answer = table.iloc[predicted_answer_coordinates[0][0], predicted_answer_coordinates[0][1]]
        elif predicted_aggregation == "SUM":
            answer = sum(
                    float(table.iloc[i, j]) 
                    for i, j in predicted_answer_coordinates 
                    if not pd.isnull(table.iloc[i, j])
                )
            
        elif predicted_aggregation == "AVERAGE":
            valid_values = [
                    float(table.iloc[i, j]) 
                    for i, j in predicted_answer_coordinates 
                    if not pd.isnull(table.iloc[i, j])
            ]
            answer = sum(valid_values) / len(valid_values) if valid_values else float('nan')
        elif predicted_aggregation == "COUNT":
            answer = sum(
                    1 for i, j in predicted_answer_coordinates if not pd.isnull(table.iloc[i, j])
            )
        else:
            raise ValueError(f"Unknown aggregation type: {predicted_aggregation}")

    except Exception as e:
        raise ValueError(f"Error calculating the answer for aggregation type '{predicted_aggregation}': {e}")

    return answer
    

        
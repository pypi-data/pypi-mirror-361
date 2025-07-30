from pathlib import Path

import pandas as pd
from deep_translator import GoogleTranslator


def translate_text_file(
    input_path: str | Path,
    output_path: str | Path,
    source_language: str = "auto",
    target_language: str = "en",
    input_encoding: str = "utf-8",
) -> None:
    """Translate a text file line-by-line using Google Translate.

    This function will produce a new file interleaving the original lines with
    the translated lines. Google Translate is sometimes a little silly and so
    having the original line next to the translated line can be helpful, especially
    if you have some knowledge of the source language.

    Parameters
    ----------
    input_path
        The path to the input file.
    output_path
        The path to the output file.
    source_language
        The language of the input text. If 'auto', Google Translate will attempt
        to detect the language.
    target_language
        The language to translate to.
    input_encoding
        The encoding of the input file.
    """
    with Path(input_path, encoding=input_encoding).open() as f:
        lines = f.readlines()

    translator = GoogleTranslator(source=source_language, target=target_language)
    translated_lines = translator.translate_batch(lines)

    with Path(output_path).open("w") as f:
        for in_line, out_line in zip(lines, translated_lines, strict=False):
            if in_line:
                f.write(f"{in_line.strip()}\n{out_line.strip()}\n\n")


def translate_dataframe(
    df: pd.DataFrame,
    columns: list[str] | None = None,
    source_language: str = "auto",
    target_language: str = "en",
) -> pd.DataFrame:
    """Translate a dataframe using Google Translate.

    Parameters
    ----------
    df
        The dataframe to translate.
    columns
        The columns to translate. If None, all columns will be translated.
    source_language
        The language of the input text. If 'auto', Google Translate will attempt
        to detect the language.
    target_language
        The language to translate to.

    Returns
    -------
    pd.DataFrame
        The translated dataframe.
    """
    df = df.copy()  # don't mutate the original dataframe

    if columns is None:
        columns = df.columns.tolist()
    translator = GoogleTranslator(source=source_language, target=target_language)
    for col in columns:
        df[f"{col}"] = translator.translate_batch(df[col].tolist())
    return df

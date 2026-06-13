#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initial Theme Generation Tool

Reads initial codes (from a prior coding step) and generates initial themes
by identifying patterns across codes using an LLM.

Python 3.11+
"""

import os
import argparse
from tqdm import tqdm
import openai
import pandas as pd
from openai import OpenAI
import httpx
import openpyxl


def create_client(base_url: str, api_key: str) -> OpenAI:
    """Create an OpenAI-compatible client."""
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=httpx.Client(
            base_url=base_url,
            follow_redirects=True,
        ),
    )


def build_system_prompt(prompt_path: str | None = None) -> str:
    """
    Build the system prompt for theme generation.
    Reads from an external file if provided, otherwise uses a built-in default.
    """
    if prompt_path and os.path.isfile(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    return (
        "You are a thematic analysis expert. Based on the initial codes provided, "
        "generate an initial theme (strictly 4-8 characters). "
        "The goal is to consolidate scattered codes into potential themes "
        "by identifying patterns and inducting latent themes across codes."
    )


def generate_theme(client: OpenAI, model: str, system_prompt: str,
                   msg: str, temperature: float = 0.2) -> str:
    """Call the LLM to generate a theme from an initial code."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content


def process_themes(file_path: str, client: OpenAI, model: str,
                   system_prompt: str, input_column: str = "coding",
                   output_start_col: int = 5, separator: str = "；",
                   save_interval: int = 20,
                   temperature: float = 0.2) -> None:
    """
    Read initial codes from an Excel file, generate themes, and write results back.

    Args:
        file_path: Path to the Excel file.
        client: OpenAI client instance.
        model: Model name to use.
        system_prompt: System prompt for the LLM.
        input_column: Column name containing initial codes.
        output_start_col: Column index (1-based) to start writing output.
        separator: Separator for splitting LLM output.
        save_interval: Save workbook every N rows.
        temperature: Generation temperature.
    """
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    df = pd.read_excel(file_path)

    if input_column not in df.columns:
        raise ValueError(
            f"Column '{input_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    contents = [
        str(item).replace("\\", "").strip()
        for item in df[input_column]
        if pd.notna(item) and str(item).strip()
    ]

    row_index = 2  # Start from row 2 (row 1 is header)

    try:
        for content in tqdm(contents, desc="Generating themes", ncols=100):
            try:
                response = generate_theme(
                    client, model, system_prompt, content, temperature
                )

                if not response or response.strip() in ("cannot extract", "无法提取"):
                    print(f"Row {row_index - 1}: cannot extract")
                    continue

                parts = [
                    part.strip()
                    for part in response.split(separator)
                    if part.strip()
                ]

                for j, part in enumerate(parts):
                    sheet.cell(row=row_index, column=output_start_col + j).value = part

            except openai.BadRequestError as e:
                print(f"Row {row_index - 1} failed (BadRequest): {e}")
            except Exception as e:
                print(f"Row {row_index - 1} error: {e}")
            finally:
                if (row_index - 1) % save_interval == 0:
                    workbook.save(file_path)
                row_index += 1

        workbook.save(file_path)
        print("All themes generated and saved.")

    except Exception as e:
        print(f"Fatal error: {e}")
        workbook.save(file_path)


def main():
    parser = argparse.ArgumentParser(
        description="LLM-based initial theme generation tool"
    )
    parser.add_argument(
        "--file", type=str, required=True,
        help="Path to the input Excel file"
    )
    parser.add_argument(
        "--column", type=str, default="coding",
        help="Name of the column containing initial codes (default: coding)"
    )
    parser.add_argument(
        "--output-col", type=int, default=5,
        help="1-based column index to start writing themes (default: 5)"
    )
    parser.add_argument(
        "--base-url", type=str,
        default=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
        help="LLM API base URL (or set LLM_BASE_URL env var)"
    )
    parser.add_argument(
        "--api-key", type=str,
        default=os.getenv("LLM_API_KEY", ""),
        help="LLM API key (or set LLM_API_KEY env var)"
    )
    parser.add_argument(
        "--model", type=str,
        default=os.getenv("LLM_MODEL", "deepseek-chat"),
        help="Model name (default: deepseek-chat)"
    )
    parser.add_argument(
        "--prompt-file", type=str, default=None,
        help="Path to a custom system prompt file (plain text)"
    )
    parser.add_argument(
        "--separator", type=str, default="；",
        help="Separator for splitting LLM output (default: ；)"
    )
    parser.add_argument(
        "--save-interval", type=int, default=20,
        help="Save workbook every N rows (default: 20)"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.2,
        help="Generation temperature (default: 0.2)"
    )
    args = parser.parse_args()

    if not args.api_key:
        raise SystemExit(
            "Provide an API key via --api-key or the LLM_API_KEY env var."
        )

    client = create_client(args.base_url, args.api_key)
    system_prompt = build_system_prompt(args.prompt_file)

    process_themes(
        file_path=args.file,
        client=client,
        model=args.model,
        system_prompt=system_prompt,
        input_column=args.column,
        output_start_col=args.output_col,
        separator=args.separator,
        save_interval=args.save_interval,
        temperature=args.temperature,
    )


if __name__ == "__main__":
    main()

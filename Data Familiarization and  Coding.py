#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
a Human–LLM Collaborative Thematic Analysis (HLCTA)

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
    Build the system prompt.
    Reads from an external file if provided, otherwise uses a built-in default.
    """
    if prompt_path and os.path.isfile(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    # Built-in default prompt (replace with your own research scenario)
    return (
        "You are a thematic analysis expert. Extract keywords from the given "
        "user comment text and generate initial codes (4-8 characters each). "
        "Separate each category with a Chinese semicolon.\n"
        "If keywords or initial codes cannot be extracted, return only: "
        "cannot extract. Do not apologize or return unrelated statements."
    )


def classify_comment(client: OpenAI, model: str, system_prompt: str,
                     msg: str, temperature: float = 0.2) -> str:
    """Call the LLM to code a single comment."""
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": msg},
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content


def process_comments(file_path: str, client: OpenAI, model: str,
                     system_prompt: str, comment_column: str = "comment",
                     separator: str = "；", temperature: float = 0.2) -> None:
    """Read comments from an Excel file, code each one, and write results back."""
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    df = pd.read_excel(file_path)

    if comment_column not in df.columns:
        raise ValueError(
            f"Column '{comment_column}' not found. "
            f"Available columns: {list(df.columns)}"
        )

    contents = [
        str(item).replace("\\", "").strip()
        for item in df[comment_column]
        if pd.notna(item) and str(item).strip()
    ]

    row_index = 2  # Start writing from row 2 (row 1 is the header)

    try:
        for content in tqdm(contents, desc="Processing comments", ncols=100):
            try:
                response = classify_comment(
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
                    sheet.cell(row=row_index, column=j + 3).value = part

            except openai.BadRequestError as e:
                print(f"Row {row_index - 1} failed (BadRequest): {e}")
            except Exception as e:
                print(f"Row {row_index - 1} error: {e}")
            finally:
                row_index += 1

        workbook.save(file_path)
        print("All data processed and saved.")

    except Exception as e:
        print(f"Fatal error: {e}")
        workbook.save(file_path)


def main():
    parser = argparse.ArgumentParser(
        description="LLM-based user comment coding tool"
    )
    parser.add_argument(
        "--file", type=str, required=True,
        help="Path to the input Excel file"
    )
    parser.add_argument(
        "--column", type=str, default="comment",
        help="Name of the comment column (default: comment)"
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
        help="Separator used to split LLM output into parts (default: ；)"
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

    process_comments(
        file_path=args.file,
        client=client,
        model=args.model,
        system_prompt=system_prompt,
        comment_column=args.column,
        separator=args.separator,
        temperature=args.temperature,
    )


if __name__ == "__main__":
    main()

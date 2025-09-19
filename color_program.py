#!/bin/python3
from bs4 import BeautifulSoup
from collections import Counter
import math
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "colors_program")


def extract_colors(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    soup = BeautifulSoup(content, "html.parser")

    days_of_week = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]

    extracted_colors = []
    
    for td in soup.find_all("td"):
        if td.text in days_of_week:
            continue
        parts = td.text.split(',')
        for color in parts:
            extracted_colors.append(color.strip().lower())
    return extracted_colors

def analyze_colors(colors):
    counter = Counter(colors)

    mean_freq = sum(counter.values()) / len(counter)
    mean_color = min(counter, key=lambda c: abs(counter[c] - mean_freq))

    # Mode (most worn)
    most_common = counter.most_common(1)[0]

    # Median
    freqs = sorted(counter.values())
    n = len(freqs)
    if n % 2 == 1:
        median_freq = freqs[n // 2]
    else:
        median_freq = (freqs[n // 2 - 1] + freqs[n // 2]) / 2
    median_colors = [c for c, f in counter.items() if f == median_freq]

    # Variance
    variance = sum((f - mean_freq) ** 2 for f in counter.values()) / len(counter)

    # Probability of red
    prob_red = counter["red"] / len(colors) if "red" in counter else 0

    return {
        "mean_color": mean_color,
        "most_common": most_common,
        "median_colors": median_colors,
        "variance": variance,
        "prob_red": prob_red,
        "counter": counter,
    }


def finabacci_sum(n=50):
    a, b = 0, 1
    total = 0
    for _ in range(n):
        total += a
        a, b = b, a + b
    return total


import psycopg2

def save_to_postgres(counter):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        for color, freq in counter.items():
            cursor.execute(
                "INSERT INTO colors (color, frequency) VALUES (%s, %s)",
                (color, freq)
            )

        conn.commit()
        cursor.close()
        conn.close()
        print("Colors saved to PostgreSQL successfully.")

    except Exception as e:
        print("Error saving to PostgreSQL:", e)

if __name__ == "__main__":
    colors = extract_colors("python_class_question.html")
    results = analyze_colors(colors)

    print("Mean color:", results["mean_color"])
    print("Most worn color:", results["most_common"])
    print("Median color(s):", results["median_colors"])
    print("Variance:", results["variance"])
    print("Probability of red:", results["prob_red"])

    # Save results
    save_to_postgres(results["counter"])

    print("Finabacci sum (50 terms):", finabacci_sum())

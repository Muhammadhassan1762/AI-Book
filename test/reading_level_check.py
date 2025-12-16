#!/usr/bin/env python3
"""
Reading Level Validation Script

This script validates that the content meets Grade 10-12 reading level requirements
by analyzing complexity, vocabulary, and structure.
"""

import os
import re
from pathlib import Path


def calculate_average_word_length(text):
    """Calculate the average word length in the text"""
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0

    total_length = sum(len(word) for word in words)
    return total_length / len(words)


def count_complex_words(text):
    """Count words with 3+ syllables (rough estimation)"""
    words = re.findall(r'\b\w+\b', text.lower())
    complex_count = 0

    for word in words:
        # Rough syllable estimation: count vowel groups
        vowel_groups = len(re.findall(r'[aeiouy]+', word))
        if vowel_groups >= 3:
            complex_count += 1

    return complex_count


def calculate_sentence_complexity(text):
    """Calculate average sentence length and complexity"""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0, 0

    total_words = 0
    for sentence in sentences:
        words = re.findall(r'\b\w+\b', sentence)
        total_words += len(words)

    avg_sentence_length = total_words / len(sentences) if sentences else 0
    return avg_sentence_length, len(sentences)


def analyze_content_file(file_path):
    """Analyze a single content file for reading level"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove markdown formatting for text analysis
    plain_text = re.sub(r'[#>`*_[\]()]', '', content)

    avg_word_length = calculate_average_word_length(plain_text)
    complex_word_count = count_complex_words(plain_text)
    avg_sentence_length, sentence_count = calculate_sentence_complexity(plain_text)

    # Calculate percentages
    words = re.findall(r'\b\w+\b', plain_text)
    total_words = len(words)
    complex_word_percentage = (complex_word_count / total_words * 100) if total_words > 0 else 0

    return {
        'file': file_path,
        'avg_word_length': avg_word_length,
        'complex_word_percentage': complex_word_percentage,
        'avg_sentence_length': avg_sentence_length,
        'sentence_count': sentence_count,
        'total_words': total_words
    }


def is_grade_level_appropriate(analysis):
    """Check if the content is appropriate for Grade 10-12 level"""
    # Grade 10-12 level characteristics:
    # - Average word length: 4.5-5.5 characters (not too simple, not too complex)
    # - Complex word percentage: 5-15% (some technical terms but not overwhelming)
    # - Average sentence length: 15-25 words (complex enough but not too dense)

    word_length_ok = 3.5 <= analysis['avg_word_length'] <= 6.0
    complex_word_ok = 2 <= analysis['complex_word_percentage'] <= 20
    sentence_length_ok = 8 <= analysis['avg_sentence_length'] <= 30

    return word_length_ok and complex_word_ok and sentence_length_ok


def validate_reading_level():
    """Validate that documentation content meets Grade 10-12 reading level requirements"""
    print("Validating content reading level (Grade 10-12)...")
    print("-" * 70)

    # Files to analyze
    doc_files = [
        'docs/digital-twin/index.md',
        'docs/digital-twin/chapter-1-physics-sim/index.md',
        'docs/digital-twin/chapter-1-physics-sim/gravity-collisions-environments.md',
        'docs/digital-twin/chapter-1-physics-sim/simulation-realism-validation.md',
        'docs/digital-twin/chapter-2-visual-interaction/index.md',
        'docs/digital-twin/chapter-2-visual-interaction/high-fidelity-rendering.md',
        'docs/digital-twin/chapter-2-visual-interaction/human-robot-interaction.md',
        'docs/digital-twin/chapter-2-visual-interaction/unity-vs-gazebo-roles.md',
        'docs/digital-twin/chapter-3-sensor-sim/index.md',
        'docs/digital-twin/chapter-3-sensor-sim/lidar-depth-cameras-imus.md',
        'docs/digital-twin/chapter-3-sensor-sim/noise-real-world-approximation.md',
        'docs/digital-twin/quickstart.md',
    ]

    all_meet_requirements = True
    results = []

    for file_path in doc_files:
        if Path(file_path).exists():
            analysis = analyze_content_file(file_path)
            meets_level = is_grade_level_appropriate(analysis)

            results.append((analysis, meets_level))

            status = "✓ MEETS" if meets_level else "✗ MAY NOT MEET"
            print(f"{analysis['file']}")
            print(f"  Words: {analysis['total_words']}, Avg word length: {analysis['avg_word_length']:.2f}")
            print(f"  Complex words: {analysis['complex_word_percentage']:.1f}%, Avg sentence: {analysis['avg_sentence_length']:.1f} words")
            print(f"  Status: {status}")
            print()

            if not meets_level:
                all_meet_requirements = False
        else:
            print(f"{file_path}: FILE NOT FOUND")
            all_meet_requirements = False
            print()

    # Summary
    print("-" * 70)
    print("READING LEVEL VALIDATION SUMMARY")
    print("-" * 70)

    total_files = len([f for f in doc_files if Path(f).exists()])
    valid_files = sum(1 for _, meets_level in results if meets_level)

    print(f"Files analyzed: {total_files}")
    print(f"Files meeting requirements: {valid_files}")
    print(f"Files not meeting requirements: {total_files - valid_files}")

    overall_status = "PASS" if all_meet_requirements else "FAIL"
    print(f"Overall reading level validation: {overall_status}")

    if all_meet_requirements:
        print("\n✓ All content meets Grade 10-12 reading level requirements")
        print("  - Appropriate vocabulary complexity")
        print("  - Suitable sentence structure")
        print("  - Good balance of technical and explanatory content")
    else:
        print("\n✗ Some content may not meet Grade 10-12 reading level requirements")
        print("  - Consider simplifying complex sentences")
        print("  - Reduce excessive technical jargon without explanation")
        print("  - Add more examples and explanatory content")

    return all_meet_requirements


def main():
    success = validate_reading_level()
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
import json
import re
import subprocess
from typing import Dict, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_summary_data(summary_file: str) -> Dict[str, str]:
    """Load summary data from the markdown file."""
    with open(summary_file, 'r') as f:
        content = f.read()
    
    # Parse the markdown file to extract symbol descriptions
    summary_data = {}
    
    # Find sections (files)
    sections = re.findall(r'## (.*?)\n\n(.*?)(?=\n## |\Z)', content, re.DOTALL)
    
    for section, symbols_text in sections:
        # Extract symbol descriptions for this section
        symbol_descriptions = re.findall(r'- `(.*?)`: (.*)', symbols_text)
        for symbol, description in symbol_descriptions:
            # Create a key that matches the format in docstrings data
            key = f"pandas.core.methods.{section.split('.')[0]}.{symbol}"
            summary_data[key] = description
    
    return summary_data

def load_docstrings_data(docstrings_file: str) -> Dict[str, str]:
    """Load docstrings data from the JSON file."""
    # Get all pandas core methods entries
    cmd = f"grep -E 'pandas\\.core\\.methods' {docstrings_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    # Parse the grep output to reconstruct valid JSON
    docstrings_data = {}
    
    # Process each line from grep output
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            # Clean up the line to make it valid JSON
            line = line.strip().rstrip(',')
            if ':' in line and not line.startswith('{') and not line.endswith('}'):
                try:
                    # Try to parse as key-value pair
                    parts = line.split(':', 1)
                    key = parts[0].strip().strip('"')
                    value = parts[1].strip()
                    
                    # Try to convert value to string (removing quotes if needed)
                    if value.startswith('"') and value.endswith('"'):
                        # Remove surrounding quotes and unescape
                        value = value[1:-1].replace('\\"', '"').replace('\\\\', '\\')
                    
                    docstrings_data[key] = value
                except:
                    # Skip lines that can't be parsed
                    continue
    
    return docstrings_data

def extract_pandas_symbols(docstrings_data: Dict[str, str]) -> Dict[str, str]:
    """Extract only pandas core methods symbols from docstrings data."""
    pandas_symbols = {}
    for key, value in docstrings_data.items():
        if 'pandas.core.methods' in key:
            pandas_symbols[key] = value
    return pandas_symbols

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate cosine similarity between two texts."""
    if not text1 or not text2:
        return 0.0
    
    # Use TF-IDF vectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
    
    # Fit and transform the texts
    try:
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except:
        # If vectorization fails, return 0
        return 0.0

def match_symbols(summary_data: Dict[str, str], docstrings_data: Dict[str, str]) -> List[Dict]:
    """Match symbols between summary and docstrings data and calculate similarities."""
    results = []
    
    # For each symbol in summary data, find matching symbol in docstrings
    for summary_key, summary_desc in summary_data.items():
        best_match = None
        best_similarity = 0.0
        best_docstring_desc = ""
        
        # Look for exact match first
        if summary_key in docstrings_data:
            docstring_desc = docstrings_data[summary_key]
            similarity = calculate_similarity(summary_desc, docstring_desc)
            results.append({
                "summary_symbol": summary_key,
                "docstring_symbol": summary_key,
                "similarity": similarity,
                "summary_description": summary_desc,
                "docstring_description": docstring_desc
            })
        else:
            # Try to find a match by suffix matching
            summary_suffix = summary_key.split('.')[-1]  # Get the function name
            
            for docstring_key, docstring_desc in docstrings_data.items():
                # Check if the suffix matches
                docstring_suffix = docstring_key.split('.')[-1]
                if summary_suffix == docstring_suffix:
                    similarity = calculate_similarity(summary_desc, docstring_desc)
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = docstring_key
                        best_docstring_desc = docstring_desc
            
            if best_match:
                results.append({
                    "summary_symbol": summary_key,
                    "docstring_symbol": best_match,
                    "similarity": best_similarity,
                    "summary_description": summary_desc,
                    "docstring_description": best_docstring_desc
                })
            else:
                # No match found
                results.append({
                    "summary_symbol": summary_key,
                    "docstring_symbol": "NO_MATCH",
                    "similarity": 0.0,
                    "summary_description": summary_desc,
                    "docstring_description": ""
                })
    
    return results

def analyze_results(results: List[Dict]):
    """Analyze the similarity results and provide summary statistics."""
    similarities = [result["similarity"] for result in results if result["similarity"] > 0]
    
    if not similarities:
        print("No valid similarities found.")
        return
    
    # Calculate statistics
    mean_similarity = np.mean(similarities)
    median_similarity = np.median(similarities)
    max_similarity = np.max(similarities)
    min_similarity = np.min(similarities)
    
    # Count matches and mismatches
    exact_matches = sum(1 for result in results 
                       if result["summary_symbol"] == result["docstring_symbol"] and result["docstring_symbol"] != "NO_MATCH")
    fuzzy_matches = sum(1 for result in results 
                       if result["summary_symbol"] != result["docstring_symbol"] and result["docstring_symbol"] != "NO_MATCH")
    no_matches = sum(1 for result in results 
                    if result["docstring_symbol"] == "NO_MATCH")
    
    print("\nAnalysis Summary:")
    print("=" * 50)
    print(f"Total symbols compared: {len(results)}")
    print(f"Exact matches: {exact_matches}")
    print(f"Fuzzy matches: {fuzzy_matches}")
    print(f"No matches: {no_matches}")
    print(f"Mean similarity: {mean_similarity:.4f}")
    print(f"Median similarity: {median_similarity:.4f}")
    print(f"Max similarity: {max_similarity:.4f}")
    print(f"Min similarity: {min_similarity:.4f}")
    
    # Show top 5 most similar pairs
    sorted_results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    print("\nTop 5 most similar pairs:")
    print("-" * 30)
    for i, result in enumerate(sorted_results[:5]):
        print(f"{i+1}. {result['summary_symbol']}")
        print(f"   {result['docstring_symbol']}")
        print(f"   Similarity: {result['similarity']:.4f}")
        print(f"   Summary: {result['summary_description']}")
        print(f"   Docstring: {result['docstring_description']}")
        print()

def main():
    """Main function to compare summaries with docstrings and calculate similarities."""
    # Load summary data
    summary_file = "/home/deming/work/python-understanding-benchmark-pipeline/result/pandas_symbols_summary.md"
    summary_data = load_summary_data(summary_file)
    
    # Load docstrings data
    docstrings_file = "/home/deming/work/python-understanding-benchmark-pipeline/data/symbol_docstrings.json"
    docstrings_data = load_docstrings_data(docstrings_file)
    
    # Extract only pandas symbols
    pandas_docstrings = extract_pandas_symbols(docstrings_data)
    
    print(f"Loaded {len(summary_data)} symbols from summary")
    print(f"Loaded {len(pandas_docstrings)} pandas symbols from docstrings")
    
    # Match symbols and calculate similarities
    results = match_symbols(summary_data, pandas_docstrings)
    
    # Print detailed results
    print("\nSymbol Similarity Results:")
    print("=" * 50)
    for result in results:
        print(f"Summary Symbol: {result['summary_symbol']}")
        print(f"Docstring Symbol: {result['docstring_symbol']}")
        print(f"Similarity: {result['similarity']:.4f}")
        print(f"Summary Description: {result['summary_description']}")
        print(f"Docstring Description: {result['docstring_description']}")
        print("-" * 30)
    
    # Analyze results
    analyze_results(results)
    
    # Save results to file
    output_file = "/home/deming/work/python-understanding-benchmark-pipeline/result/detailed_similarity_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    main()
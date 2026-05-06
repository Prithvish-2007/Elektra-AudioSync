"""
Evaluator Module
Computes accuracy metrics and MRR without explicit loops.
"""

from typing import List, Dict, Tuple
from extractor import fingerprint
from matcher import match


def evaluate_single_case(test_case: Dict) -> Tuple[bool, float]:
    """
    Evaluate a single test case.
    Returns (is_correct, reciprocal_rank)
    """
    try:
        fps = fingerprint(test_case["audio_path"])
        result = match(fps)
        expected_id = test_case["expected_song_id"]
        
        is_correct = result.get("song_id") == expected_id
        reciprocal_rank = 1.0 if is_correct else 0.0
        
        return is_correct, reciprocal_rank
    except Exception as e:
        print(f"Error evaluating {test_case['audio_path']}: {e}")
        return False, 0.0


def evaluate(test_cases: List[Dict]) -> Dict:
    """
    Run batch evaluation on test cases.
    Uses map to evaluate all cases without loops.
    
    Args:
        test_cases: List of {"audio_path": str, "expected_song_id": str}
    
    Returns:
        dict with top1_accuracy, mrr, total, correct
    """
    
    if not test_cases:
        return {
            "top1_accuracy": 0.0,
            "mrr": 0.0,
            "total": 0,
            "correct": 0
        }
    
    # Map evaluation over all test cases
    results = map(evaluate_single_case, test_cases)
    correctness_list = list(results)
    
    # Extract results using map
    is_correct_list = list(map(lambda x: x[0], correctness_list))
    reciprocal_ranks = list(map(lambda x: x[1], correctness_list))
    
    # Calculate metrics
    total = len(test_cases)
    correct = sum(is_correct_list)
    
    return {
        "top1_accuracy": round(correct / max(total, 1), 4),
        "mrr": round(sum(reciprocal_ranks) / max(total, 1), 4),
        "total": total,
        "correct": correct
    }


def evaluate_with_details(test_cases: List[Dict]) -> Dict:
    """
    Run evaluation and return detailed results per test case.
    """
    def evaluate_with_metadata(case_and_index: Tuple[Dict, int]) -> Dict:
        case, idx = case_and_index
        is_correct, rr = evaluate_single_case(case)
        return {
            "index": idx,
            "audio_path": case["audio_path"],
            "expected_song_id": case["expected_song_id"],
            "is_correct": is_correct,
            "reciprocal_rank": rr
        }
    
    indexed_cases = zip(test_cases, range(len(test_cases)))
    detailed_results = list(map(evaluate_with_metadata, indexed_cases))
    
    total = len(test_cases)
    correct = sum(1 for r in detailed_results if r["is_correct"])
    mrr = sum(r["reciprocal_rank"] for r in detailed_results) / max(total, 1)
    
    return {
        "top1_accuracy": round(correct / max(total, 1), 4),
        "mrr": round(mrr, 4),
        "total": total,
        "correct": correct,
        "results": detailed_results
    }

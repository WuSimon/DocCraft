from .base_benchmarker import BaseBenchmarker
import json
import os
import subprocess
import re
import numpy as np
from typing import Dict, Any, List, Union
from pathlib import Path

class DocVQABenchmarker(BaseBenchmarker):
    """
    Benchmarker for the DocVQA dataset using DocCraft parsers.
    """
    def __init__(self, dataset_json: Union[str, Path], images_dir: Union[str, Path], eval_script_path: Union[str, Path] = None, gt_json: Union[str, Path] = None):
        super().__init__(name="DocVQABenchmarker", version="1.0.0", supported_metrics=["MAP", "ANLSL"])
        self.dataset_json = str(dataset_json)
        self.images_dir = str(images_dir)
        self.eval_script_path = str(eval_script_path) if eval_script_path else None
        self.gt_json = str(gt_json) if gt_json else None
        with open(self.dataset_json, 'r') as f:
            self.data = json.load(f)["data"]

    def calculate_evidence_scores(self, question: str, answer: str, extracted_text: str, evidence_length: int) -> List[float]:
        """
        Calculate evidence relevance scores based on question-answer-text similarity.
        
        Args:
            question: The question being asked
            answer: The predicted answer
            extracted_text: Text extracted from the document
            evidence_length: Required length of evidence scores
            
        Returns:
            List[float]: Evidence relevance scores
        """
        if not extracted_text or not answer:
            return [0.1] * evidence_length
        
        # Normalize text for comparison
        question_lower = question.lower()
        answer_lower = answer.lower()
        text_lower = extracted_text.lower()
        
        # Split text into sentences or chunks for evidence scoring
        sentences = re.split(r'[.!?]+', extracted_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If we don't have enough sentences, split by lines
        if len(sentences) < evidence_length:
            lines = extracted_text.split('\n')
            sentences = [line.strip() for line in lines if line.strip()]
        
        # Calculate relevance scores for each text segment
        relevance_scores = []
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Calculate word overlap between question and sentence
            question_words = set(re.findall(r'\w+', question_lower))
            sentence_words = set(re.findall(r'\w+', sentence_lower))
            answer_words = set(re.findall(r'\w+', answer_lower))
            
            # Question-sentence overlap
            question_overlap = len(question_words.intersection(sentence_words))
            question_relevance = question_overlap / max(1, len(question_words))
            
            # Answer-sentence overlap
            answer_overlap = len(answer_words.intersection(sentence_words))
            answer_relevance = answer_overlap / max(1, len(answer_words))
            
            # Combined relevance score
            combined_relevance = (question_relevance * 0.6 + answer_relevance * 0.4)
            
            # Boost score if sentence contains numbers (often important for DocVQA)
            if re.search(r'\d+', sentence):
                combined_relevance *= 1.2
            
            # Boost score if sentence contains common DocVQA keywords
            docvqa_keywords = ['party', 'election', 'candidate', 'office', 'year', 'date', 'name', 'address', 'phone', 'email']
            keyword_matches = sum(1 for keyword in docvqa_keywords if keyword in sentence_lower)
            if keyword_matches > 0:
                combined_relevance *= (1 + 0.1 * keyword_matches)
            
            relevance_scores.append(min(1.0, combined_relevance))
        
        # Pad or truncate to required length
        if len(relevance_scores) < evidence_length:
            # Pad with lower scores
            padding = [0.05] * (evidence_length - len(relevance_scores))
            relevance_scores.extend(padding)
        else:
            # Take top scores
            relevance_scores = sorted(relevance_scores, reverse=True)[:evidence_length]
        
        # Ensure we have exactly the required length
        while len(relevance_scores) < evidence_length:
            relevance_scores.append(0.05)
        
        return relevance_scores[:evidence_length]

    def benchmark(self, parser, file_path: Union[str, Path] = None, **kwargs) -> Dict[str, Any]:
        """
        Benchmark a parser on the DocVQA dataset.
        Args:
            parser: Parser instance
            file_path: Not used (kept for API compatibility)
            **kwargs: Additional options
        Returns:
            Dict[str, Any]: Benchmark results
        """
        predictions = []
        # Determine max evidence length if not present in each item
        max_evidence_length = 0
        for item in self.data:
            gt_evidence = item.get('ground_truth', None)
            if gt_evidence is not None:
                max_evidence_length = max(max_evidence_length, len(gt_evidence))
        if max_evidence_length == 0:
            max_evidence_length = 10  # reasonable default for DocVQA
        
        for item in self.data:
            image_id = item.get("image_id") or item.get("image") or str(item.get("question_id"))
            # Try jpg, png, etc.
            found = False
            for ext in [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"]:
                image_path = os.path.join(self.images_dir, f"{image_id}{ext}")
                if os.path.exists(image_path):
                    found = True
                    break
            if not found:
                self.logger.warning(f"Image not found for question_id {item['question_id']}")
                continue
            question = item["question"]
            question_id = item["question_id"]
            print(f"\n[DocVQABenchmarker] Calling parser for question_id={question_id}")
            print(f"  Image path: {image_path}")
            print(f"  Question: {question}")
            
            # Extract text from document for evidence scoring
            extracted_text = ""
            if hasattr(parser, "extract_text"):
                try:
                    text_result = parser.extract_text(image_path)
                    extracted_text = text_result.get("text", "")
                except:
                    pass
            
            # Use parser's question answering if available
            if hasattr(parser, "ask_question"):
                result = parser.ask_question(image_path, question)
                print(f"  Parser result: {result}")
                answer = result.get("answer") if result.get("answer") is not None else result.get("text", "")
            else:
                # Fallback: extract_text and use as answer
                result = parser.extract_text(image_path)
                print(f"  Parser result: {result}")
                answer = result.get("text", "")
                extracted_text = answer  # Use same text for evidence
            
            print(f"  Final answer: {answer}")
            
            # Calculate evidence relevance scores
            evidence_length = len(item.get('ground_truth', [])) or max_evidence_length
            evidence_scores = self.calculate_evidence_scores(question, answer, extracted_text, evidence_length)
            
            print(f"  Evidence scores: {evidence_scores[:5]}...")  # Show first 5 scores
            
            predictions.append({
                "question_id": question_id,
                "evidence": evidence_scores,
                "answer": [answer] if isinstance(answer, str) else answer
            })
        
        # Save predictions
        output_predictions_path = kwargs.get("output_predictions_path", "predictions.json")
        with open(output_predictions_path, "w") as f:
            json.dump(predictions, f, indent=2)
        
        # Optionally run the official evaluation script
        eval_results = None
        if self.eval_script_path and self.gt_json:
            result = subprocess.run([
                "python", self.eval_script_path, "-g", self.gt_json, "-s", output_predictions_path
            ], capture_output=True, text=True)
            print(result.stdout)
            eval_results = result.stdout
        
        return {"predictions": predictions, "eval_results": eval_results} 
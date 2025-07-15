from doccraft.parsers.qwen_vl_parser import QwenVLParser
import sys

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_qwen_vl_parser.py <image_path> <question>")
        sys.exit(1)
    image_path = sys.argv[1]
    question = sys.argv[2]
    parser = QwenVLParser(device="auto")
    answer = parser.ask_question(image_path, question) 
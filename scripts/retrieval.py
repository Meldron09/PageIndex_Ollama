import json
import argparse
from pageindex.utils import ChatGPT_API, structure_to_list, get_text_of_pdf_pages, get_page_tokens


def get_text_by_line_range(line_num, md_lines, tree, current_node_id):
    """Extract text from markdown by line range.

    Uses the node's line_num as start, and finds the next node's line_num as end.
    """
    # line_num can be an int (start line) or a dict with start_index/end_index
    if isinstance(line_num, dict):
        start_line = line_num.get('start_index', 1)
        end_line = line_num.get('end_index', len(md_lines))
    else:
        start_line = line_num
        # Find the next node's line number to determine end
        end_line = None
        all_nodes = structure_to_list(tree)
        # Sort by line number
        sorted_nodes = sorted(all_nodes, key=lambda n: n.get('line_num', 0))
        for i, node in enumerate(sorted_nodes):
            if node.get('node_id') == current_node_id:
                if i + 1 < len(sorted_nodes):
                    end_line = sorted_nodes[i + 1].get('line_num', len(md_lines))
                else:
                    end_line = len(md_lines) + 1  # Last node goes to end
                break

    # Convert to 0-based indexing
    start_idx = max(0, start_line - 1)
    end_idx = min(len(md_lines), end_line - 1) if end_line else len(md_lines)
    return '\n'.join(md_lines[start_idx:end_idx])

def find_node_by_id(structure, node_id):
    for node in structure_to_list(structure):
        if node.get('node_id') == node_id:
            return node
    return None

def slim_tree(node):
    """Strip full text — only send titles, summaries, node_ids to LLM."""
    if isinstance(node, list):
        return [slim_tree(n) for n in node]
    return {
        "node_id": node.get("node_id"),
        "title": node.get("title"),
        "summary": node.get("summary", ""),
        "nodes": slim_tree(node["nodes"]) if node.get("nodes") else []
    }

def tree_search(query, tree, model):
    prompt = f"""You are given a question and a tree structure of a document.
Find all nodes likely to contain the answer.

Question: {query}
Document tree: {json.dumps(slim_tree(tree), indent=2)}

Reply ONLY as JSON with no extra text:
{{
    "thinking": "<your reasoning>",
    "node_list": ["node_id1", "node_id2"]
}}
"""
    response = ChatGPT_API(model, prompt)
    # strip markdown fences if model wraps in ```json
    clean = response.strip().removeprefix("```json").removesuffix("```").strip()
    result = json.loads(clean)
    print(f"\n[tree_search] thinking: {result['thinking']}")
    print(f"[tree_search] selected nodes: {result['node_list']}")
    return result["node_list"]

def answer_query(query, tree, content_data, content_type, model):
    node_ids = tree_search(query, tree, model)

    context = ""
    for nid in node_ids:
        node = find_node_by_id(tree, nid)
        if node:
            context += f"\n--- {node['title']} ---\n"
            if content_type == "pdf":
                context += get_text_of_pdf_pages(content_data, node['start_index'], node['end_index'])
            else:  # markdown
                context += get_text_by_line_range(node['line_num'], content_data, tree, node['node_id'])

    if not context:
        return "No relevant sections found in the document."

    answer_prompt = f"""Answer the question using only the context below.
Cite the section titles where you found the answer.

Question: {query}
Context: {context}
"""
    return ChatGPT_API(model, answer_prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pdf", help="Path to the PDF file")
    group.add_argument("--md", help="Path to the Markdown file")
    parser.add_argument("--tree", required=True, help="Path to the saved tree JSON file")
    parser.add_argument("--query", required=True, help="Your question")
    parser.add_argument("--model", default="deepseek-r1:8b", help="Ollama model name")
    args = parser.parse_args()

    # Load tree
    with open(args.tree, "r") as f:
        tree = json.load(f)

    # Extract the structure array from the tree (if present)
    if 'structure' in tree:
        tree = tree['structure']

    # Load content based on file type
    if args.pdf:
        content_data = get_page_tokens(args.pdf, model="gpt-4o-2024-11-20")
        content_type = "pdf"
    else:
        with open(args.md, 'r', encoding='utf-8') as f:
            md_content = f.read()
        content_data = md_content.split('\n')
        content_type = "markdown"

    # Run
    answer = answer_query(args.query, tree, content_data, content_type, args.model)
    print(f"\n=== Answer ===\n{answer}")
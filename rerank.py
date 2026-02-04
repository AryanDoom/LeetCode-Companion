#not yet used but will be used in the future for ranking questions (bade me will use to make an algo to rank the recommended questions)
def rerank(candidates, summary):
    results = []

    for c in candidates[:10]:
        item = c["item"]

        bonus = 0.0
        bonus += 0.02 * len(item.get("patterns", [])) #bigger question
        bonus += 0.01 * len(item.get("tags", []))#more topics in the question
    

        final_score = c["score"] + min(bonus, 0.1)

        results.append({
            "id": item["id"],
            "title": item["title"],
            "difficulty": item.get("difficulty"),
            "tags": item.get("tags", []),
            "patterns": item.get("patterns", []),
            "score": final_score,
            "explanation": build_explanation(item, summary)
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results

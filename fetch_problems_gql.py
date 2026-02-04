import requests
import json
import time

OUT_FILE = "problems.json"
URL = "https://leetcode.com/graphql"

def fetch_problems_gql():
    print("Fetching problems from LeetCode GraphQL...")
    
    query = """
    query problemsetQuestionList($limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: ""
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          acRate
          difficulty
          questionFrontendId
          isPaidOnly
          title
          titleSlug
          topicTags {
            name
          }
        }
      }
    }
    """
    
    all_questions = []
    # Fetch 500 problems (should be enough for recommendations)
    limit = 100
    for skip in range(0, 500, limit):
        variables = {
            "categorySlug": "",
            "skip": skip,
            "limit": limit,
            "filters": {}
        }
        
        try:
            resp = requests.post(URL, json={"query": query, "variables": variables}, headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }, timeout=10)
            
            data = resp.json()
            questions = data["data"]["problemsetQuestionList"]["questions"]
            if not questions:
                break
                
            for q in questions:
                if q["isPaidOnly"]: continue
                
                all_questions.append({
                    "id": q["questionFrontendId"],
                    "title": q["title"],
                    "titleSlug": q["titleSlug"],
                    "difficulty": q["difficulty"],
                    "tags": [t["name"].lower() for t in q["topicTags"]]
                })
            
            print(f"Fetched {len(questions)} problems (total: {len(all_questions)})")
            time.sleep(1) 
            
        except Exception as e:
            print(f"Error fetching batch {skip}: {e}")
            break

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2)
    
    print(f"Saved {len(all_questions)} problems to {OUT_FILE}")

if __name__ == "__main__":
    fetch_problems_gql()

from database import get_database_connection
import re

def normalize_skill_format(text):
    text = text.lower().strip()
    text = re.sub(r"(?<=\w)[-‐‑‒–—](?=\w)", " ", text)
    return " ".join(text.split())


def find_standard_skill(skill_text):
    normalized_skill_text = skill_text.lower().strip()
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)  # result become Dic, or Tuple




    cursor.execute("""
        SELECT skill_id, skill_name
        FROM skills
        WHERE skill_name = %s    
        """,
        (normalized_skill_text,)
        )
    result = cursor.fetchone()

    if result is None:
        cursor.execute(
            """
            SELECT skills.skill_id, skills.skill_name
            FROM skill_aliases
                JOIN skills
                    ON skill_aliases.skill_id = skills.skill_id
            WHERE skill_aliases.alias_name = %s
            """,
            (normalized_skill_text,),
        )
        result = cursor.fetchone()
    if result is None:
        formatted_text = normalize_skill_format(skill_text)
        matched_ids = []

        for skill_row in all_skills:
            text = skill_row.get("alias_name") or skill_row.get("skill_name")

            if normalize_skill_format(text) == formatted_text:
                skill_id = skill_row["skill_id"]

                if skill_id not in matched_ids:
                    matched_ids.append(skill_id)

        if len(matched_ids) == 1:
            cursor.execute(
                "SELECT skill_id, skill_name FROM skills WHERE skill_id = %s",
                (matched_ids[0],),
            )
            result = cursor.fetchone()
    cursor.close()
    connection.close()
    return result




def normalize_skill_list(skill_texts):
    normalized_skill_texts = []
    for skill_text in skill_texts:
        standard_skill = find_standard_skill(skill_text)
        if standard_skill is not None:
            normalized_skill_texts.append(standard_skill)
    return normalized_skill_texts

def load_skill_search_index():
    connection = get_database_connection()
    cursor = connection.cursor(dictionary=True)  # result become Dic, or Tuple


    cursor.execute(
        """
        SELECT skill_aliases.skill_id, skill_aliases.alias_name
        FROM skill_aliases
        """
    )
    alias_result = cursor.fetchall()

    cursor.execute(
        """
        SELECT skills.skill_id, skills.skill_name
        FROM skills
        """
    )
    skills_result = cursor.fetchall()

    result = alias_result + skills_result


    cursor.close()
    connection.close()
    return result
all_skills = load_skill_search_index()

def find_skill_candidates(description_text, skill_rows):
    standard_names = {}

    for skill_row in skill_rows:
        if "skill_name" in skill_row:
            standard_names[skill_row["skill_id"]] = skill_row["skill_name"]

    candidates = []

    for skill_row in skill_rows:
        text = skill_row.get("alias_name") or skill_row.get("skill_name")
        if not text:
            continue

        pattern = r"(?<!\w)" + re.escape(text) + r"(?!\w)"

        if re.search(pattern, description_text, re.IGNORECASE):
            skill_name = standard_names[skill_row["skill_id"]]

            if skill_name not in candidates:
                candidates.append(skill_name)

    return candidates

class MaxHeap:
    def __init__(self):
        self.heap = []

    def push(self, value):
        self.heap.append(value)
        i = len(self.heap) - 1

        while i > 0:
            parent_index = (i - 1) // 2

            if self.heap[parent_index] >= self.heap[i]:
                break

            self.heap[parent_index], self.heap[i] = self.heap[i], self.heap[parent_index]

            i = parent_index

    def peek(self):
        if len(self.heap) == 0:
            return None
        return self.heap[0]

    def pop_max(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        maximum = self.heap[0]

        self.heap[0] = self.heap.pop()

        i = 0

        while True:
            left = 2 * i + 1
            right = 2 * i + 2
            largest = i

            if left < len(self.heap) and self.heap[left] > self.heap[largest]:
                largest = left
            if right < len(self.heap) and self.heap[right] > self.heap[largest]:
                largest = right

            if largest == i:
                break

            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]

            i = largest

        return maximum


def levenshtein_distance(word1, word2):
    rows = len(word1) + 1
    cols = len(word2) + 1
    dp = []
    for i in range(rows):
        row = [0] * cols
        dp.append(row)

    for i in range(rows):
        dp[i][0] = i

    for i in range(cols):
        dp[0][i] = i

    for row in range(1, rows):
        for col in range(1, cols):
            if word1[row - 1] == word2[col - 1]:
                cost = 0
            else:
                cost = 1

            replace = dp[row - 1][col - 1] + cost
            delete = dp[row - 1][col] + 1
            insert = dp[row][col - 1] + 1

            dp[row][col] = min(replace, delete, insert)
    return dp[rows - 1][cols - 1]

def find_skill_suggestions(skill_text, skill_rows):
    normalized_skill_text = skill_text.lower().strip()
    prefix_entries = []
    heap = MaxHeap()
    if len(normalized_skill_text) < 2:
        return []

    for count, skill_row in enumerate(skill_rows):
        if "alias_name" in skill_row:
            text = skill_row["alias_name"]
        else:
            text = skill_row["skill_name"]

        if text.startswith(normalized_skill_text):
            score = len(text) - len(normalized_skill_text)
            entry = (score, count)
            prefix_entries.append(entry)

    if len(prefix_entries) >= 3:
        for entry in prefix_entries:
            if len(heap.heap) < 3:
                 heap.push(entry)
            elif entry < heap.peek():
                 heap.pop_max()
                 heap.push(entry)
        heap.heap.sort()
        return heap.heap

    if 0 < len(prefix_entries) < 3 :
        prefix_entries.sort()
        return prefix_entries

    if len(prefix_entries) == 0 and len(normalized_skill_text) < 4:
        return []
    else:
        for count, skill_row in enumerate(skill_rows):
            if "alias_name" in skill_row:
                candidate_text = skill_row["alias_name"]
            else:
                candidate_text = skill_row["skill_name"]

            score = levenshtein_distance(normalized_skill_text, candidate_text)
            similarity = 1 - score / max(len(normalized_skill_text), len(candidate_text))

            if similarity >= 0.70:
                entry = (score, count)
                if len(heap.heap) < 3:
                    heap.push(entry)
                elif entry < heap.peek():
                    heap.pop_max()
                    heap.push(entry)
        heap.heap.sort()
        return heap.heap

def return_suggestions(sorted_list, skill_rows):
    js_return = []
    for score, count in sorted_list:
        skill_row = skill_rows[count]
        if "alias_name" in skill_row:
            text = skill_row["alias_name"]
        else:
            text = skill_row["skill_name"]

        js_return.append({"display_text": text, "skill_id": skill_row["skill_id"]})

    return js_return



if __name__ == "__main__":
    test_inputs = ["", "p", "py", "pyth", "pythn", "python 3", "  PYTHON3  ", "flask", "flsak", "javas", "javscript", "typescript", "typesript", "react", "raect", "html", "css", "node", "node.js", "rest", "rest api", "sql", "mysql", "myslq", "postgres", "postgreql", "dock", "dokcer", "aws", "azure", "azue", "linux", "git", "jira", "excel", "power b", "power bi", "pandas", "pytest", "pytes", "selenium", "slenium", "testing", "c#", "c++", "cpp", "zzzz"]
    for skill_text in test_inputs:
        sorted_list = find_skill_suggestions(
            skill_text,
            all_skills,
        )

        suggestions = return_suggestions(
            sorted_list,
            all_skills,
        )

        print(skill_text, "->", suggestions)










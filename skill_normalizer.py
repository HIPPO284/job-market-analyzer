from database import get_database_connection



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

print(levenshtein_distance("pythn", "python"))
print(levenshtein_distance("ab", "acb"))


def find_skill_suggestions(skill_text, skill_rows):
    skill_text = skill_text.lower().strip()
    heap = MaxHeap()
    for count, skill_row in enumerate(skill_rows):
        if "alias_name" in skill_row:
            candidate_text = skill_row["alias_name"]
        else:
            candidate_text = skill_row["skill_name"]
        score = levenshtein_distance(skill_text, candidate_text)
        entry = (score, count)
        if len(heap.heap) < 3:
            heap.push(entry)
        elif entry < heap.peek():
            heap.pop_max()
            heap.push(entry)

    heap.heap.sort()
    js_return = []

    for score, count in heap.heap:
        skill_row = skill_rows[count]
        if "alias_name" in skill_row:
            text = skill_row["alias_name"]
        else:
            text = skill_row["skill_name"]

        js_return.append({"display_text": text, "skill_id": skill_row["skill_id"]})

    return js_return

print(find_skill_suggestions("pyt", all_skills))
print(find_skill_suggestions("zzzz", all_skills))











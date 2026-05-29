import os


class CodeAgent:

    def run(self, query):

        matches = []

        EXCLUDED_DIRS = {
            "venv",
            ".git",
            ".chroma",
            "__pycache__"
        }

        for root, dirs, files in os.walk("."):

            # Skip huge folders
            dirs[:] = [
                d for d in dirs
                if d not in EXCLUDED_DIRS
            ]

            for file in files:

                if file.endswith(".py"):

                    path = os.path.join(root, file)

                    try:
                        with open(
                            path,
                            encoding="utf-8"
                        ) as f:

                            content = f.read()

                        if query.lower() in content.lower():

                            matches.append(path)

                    except Exception as e:
                        print(e)

        return matches[:10]


if __name__ == "__main__":

    agent = CodeAgent()

    result = agent.run(
        "similarity_search"
    )

    print(result)
# encoding: utf-8
# Author: ZYJ
# Date: 2025/7/5
# Time: 20:21
# IDE: PyCharm
# File: data_frame.py


class DataFrame:
    def __init__(self, data, columns=None):
        """
        :param data: List of dictionaries or lists, where each dictionary or list represents a row.
        :param columns: List of column names to display in the DataFrame.
                        If None, columns will be inferred from the data.
                        When data is a list of dictionaries, columns can be specified in any order, and None.
                        When data is a list of lists, columns must be specified in the same order as the data.
        """
        self.data = data
        self.columns = columns or self._infer_columns()

        len_for_columns = [0 for col in self.columns]
        for col in self.columns:
            len_for_columns[self.columns.index(col)] = max(len(col), max(len(str(row[col])) for row in self.data if col in row))
        len_for_columns_in_dict = {col: len_for_columns[i] for i, col in enumerate(self.columns)}
        self.len_for_columns = len_for_columns_in_dict

    def _infer_columns(self):
        """
        Infer column names from the first row of data.
        If data is a list of dictionaries, use the keys of the first dictionary.
        If data is a list of lists, use the range of the length of the first list.
        """
        if isinstance(self.data, list) and self.data:
            if isinstance(self.data[0], dict):
                return list(self.data[0].keys())
            elif isinstance(self.data[0], list):
                raise "Column names must be specified when data is a list of lists."
        raise "Data is empty or not in a recognized format."

    def to_markdown(self):
        """
        Convert the DataFrame to a markdown formatted string.
        :return: Markdown formatted string representing the DataFrame.
        """
        header = "| " + " | ".join(f"{col:<{self.len_for_columns[col]}}" for col in self.columns) + " |"
        separator = "|-" + "-|-".join("-" * self.len_for_columns[col] for col in self.columns) + "-|"
        rows = []
        for row in self.data:
            row_str = "| " + " | ".join(f"{str(row.get(col, '')):<{self.len_for_columns[col]}}" for col in self.columns) + " |"
            rows.append(row_str)
        if not rows:
            rows.append("| " + " | ".join(" " * self.len_for_columns[col] for col in self.columns) + " |")
        return "\n".join([header, separator] + rows)

    def to_csv(self, filename=None):
        header = ",".join(f"{col:<{self.len_for_columns[col]}}" for col in self.columns)
        rows = []
        for row in self.data:
            row_str = ",".join(f"{str(row.get(col, '')):<{self.len_for_columns[col]}}" for col in self.columns)
            rows.append(row_str)
        if not rows:
            rows.append(",".join(" " * self.len_for_columns[col] for col in self.columns))
        if filename:
            with open(filename, "w") as f:
                f.write("\n".join([header] + rows))
        return "\n".join([header] + rows)


    def __len__(self):
        """
        Return the number of rows in the DataFrame.
        """
        return len(self.data)


    def __str__(self):
        """
        String representation of the DataFrame.
        Returns the markdown formatted string.
        """
        return self.to_markdown()



# ==== 用法示例 ====

data = [
    {"A": "cat", "B": "dog", "C": "apple"},
    {"A": "tiger", "B": "fish", "C": "banana"},
    {"A": "lion", "B": "bird", "C": "pear"},
]

if __name__ == "__main__":
    # columns 自动推断
    df = DataFrame(data)
    print(df.to_markdown())
    print(df.len_for_columns)

    # columns 手动指定（顺序自定义，支持缺失/补空）
    df2 = DataFrame(data, columns=["B", "A"])
    print(df2.to_markdown())
    print(df.len_for_columns)

    df3 = DataFrame(data, columns=["A", "B", "C"])
    print(df3.to_csv('a.csv'))


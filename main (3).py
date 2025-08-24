import os
import re
import sys

class SimpleFileDB:
    def __init__(self):
        self.db_dir = "database"
        if not os.path.exists(self.db_dir):
            os.makedirs(self.db_dir)
    
    def execute_command(self, command):
        quoted_parts = re.findall(r"'([^']*)'", command)
        for i, part in enumerate(quoted_parts):
            command = command.replace(f"'{part}'", f"__QUOTE_{i}__")
        
        command = command.lower()
        
        for i, part in enumerate(quoted_parts):
            command = command.replace(f"__quote_{i}__", f"'{part}'")
        
        if re.match(r"\s*create\s+table\s+", command, re.IGNORECASE):
            self._create_table(command)
        elif re.match(r"\s*insert\s+into\s+", command, re.IGNORECASE):
            self._insert(command)
        elif re.match(r"\s*select\s+", command, re.IGNORECASE):
            self._select(command)
        else:
            print("Error: Invalid command")

    def _create_table(self, command):
        match = re.match(r"\s*create\s+table\s+(\w+)\s*\((.*)\)", command, re.IGNORECASE)
        if not match:
            print("Error: Invalid CREATE TABLE command")
            return
        
        table_name = match.group(1).lower()
        columns_str = match.group(2).strip()
        columns = [col.strip().lower() for col in columns_str.split(',')]
        
        table_path = os.path.join(self.db_dir, f"{table_name}")
        
        try:
            with open(table_path, 'w') as f:
                f.write(','.join(columns) + '\n')
            print(f"Table '{table_name}' created successfully")
        except Exception as e:
            print("Error creating table")

    def _insert(self, command):
        match = re.match(r"\s*insert\s+into\s+(\w+)\s+values\s*\((.*)\)", command, re.IGNORECASE)
        if not match:
            print("Error: Invalid INSERT command")
            return
        
        table_name = match.group(1).lower()
        values_str = match.group(2).strip()
        
        values = []
        in_quote = False
        current_value = ""
        i = 0
        
        while i < len(values_str):
            char = values_str[i]
            
            if char == "'" and (i == 0 or values_str[i-1] != '\\'):
                in_quote = not in_quote
                current_value += char
            elif char == ',' and not in_quote:
                values.append(current_value.strip())
                current_value = ""
            else:
                current_value += char
            
            i += 1
        
        if current_value:
            values.append(current_value.strip())
        
        table_path = os.path.join(self.db_dir, f"{table_name}")
        if not os.path.exists(table_path):
            print(f"Error: Table not found")
            return
        
        try:
            with open(table_path, 'a') as f:
                f.write(','.join(values) + '\n')
            print(f"Record inserted successfully")
        except Exception as e:
            print("Error inserting record")

    def _read_table(self, table_name):
        table_path = os.path.join(self.db_dir, f"{table_name}")
        if not os.path.exists(table_path):
            print(f"Error: Table not found")
            return None, None
        
        try:
            with open(table_path, 'r') as f:
                lines = f.readlines()
                
            if not lines:
                return [], []
                
            headers = lines[0].strip().split(',')
            rows = []
            
            for line in lines[1:]:
                if line.strip():
                    row_values = []
                    in_quote = False
                    current_value = ""
                    i = 0
                    
                    while i < len(line):
                        char = line[i]
                        
                        if char == "'" and (i == 0 or line[i-1] != '\\'):
                            in_quote = not in_quote
                            current_value += char
                        elif char == ',' and not in_quote:
                            row_values.append(current_value.strip())
                            current_value = ""
                        else:
                            current_value += char
                        
                        i += 1
                    
                    if current_value:
                        row_values.append(current_value.strip())
                    
                    rows.append(row_values)
            
            return headers, rows
        except Exception as e:
            print("Error reading table")
            return None, None

    def _select(self, command):
        if " join " in command:
            self._select_join(command)
            return
            
        where_parts = command.split(" where ", 1)
        base_command = where_parts[0]
        where_clause = where_parts[1] if len(where_parts) > 1 else None
        
        match = re.match(r"\s*select\s+(.*?)\s+from\s+(\w+)", base_command, re.IGNORECASE)
        if not match:
            print("Error: Invalid SELECT command")
            return
        
        columns_str = match.group(1).strip()
        table_name = match.group(2).lower()
        
        headers, rows = self._read_table(table_name)
        if headers is None:
            return
        
        if columns_str == "*":
            display_cols = headers
            col_indices = list(range(len(headers)))
        else:
            display_cols = [col.strip().lower() for col in columns_str.split(',')]
            col_indices = []
            for col in display_cols:
                if col in headers:
                    col_indices.append(headers.index(col))
                else:
                    print(f"Warning: Column not found")
        
        if where_clause:
            match = re.match(r"(\w+)\s*=\s*([^']+|'[^']*')", where_clause)
            if not match:
                print("Error: Invalid WHERE clause")
                return
            
            where_col = match.group(1).lower()
            where_val = match.group(2)
            
            if where_val.startswith("'") and where_val.endswith("'"):
                where_val = where_val[1:-1]
            
            if where_col not in headers:
                print("Error: Column not found")
                return
            
            where_col_idx = headers.index(where_col)
            filtered_rows = []
            
            for row in rows:
                if where_col_idx < len(row) and row[where_col_idx] == where_val:
                    filtered_rows.append(row)
            
            rows = filtered_rows
        
        self._display_results(display_cols, rows, col_indices)

    def _select_join(self, command):
        where_parts = command.split(" where ", 1)
        base_command = where_parts[0]
        where_clause = where_parts[1] if len(where_parts) > 1 else None
        
        match = re.match(
            r"\s*select\s+(.*?)\s+from\s+(\w+)\s+join\s+(\w+)\s+on\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)", 
            base_command, 
            re.IGNORECASE
        )
        
        if not match:
            print("Error: Invalid JOIN command")
            return
        
        columns_str = match.group(1).strip()
        table1 = match.group(2).lower()
        table2 = match.group(3).lower()
        join_table1 = match.group(4).lower()
        join_col1 = match.group(5).lower()
        join_table2 = match.group(6).lower()
        join_col2 = match.group(7).lower()
        
        if join_table1 != table1 and join_table1 != table2:
            print("Error: Invalid JOIN condition")
            return
        
        if join_table2 != table1 and join_table2 != table2:
            print("Error: Invalid JOIN condition")
            return
        
        headers1, rows1 = self._read_table(table1)
        headers2, rows2 = self._read_table(table2)
        
        if headers1 is None or headers2 is None:
            return
        
        if join_table1 == table1:
            if join_col1 not in headers1:
                print("Error: Column not found")
                return
            join_idx1 = headers1.index(join_col1)
        else:
            if join_col1 not in headers2:
                print("Error: Column not found")
                return
            join_idx1 = headers2.index(join_col1)
        
        if join_table2 == table1:
            if join_col2 not in headers1:
                print("Error: Column not found")
                return
            join_idx2 = headers1.index(join_col2)
        else:
            if join_col2 not in headers2:
                print("Error: Column not found")
                return
            join_idx2 = headers2.index(join_col2)
        
        joined_headers = [f"{table1}.{col}" for col in headers1] + [f"{table2}.{col}" for col in headers2]
        joined_rows = []
        
        for row1 in rows1:
            for row2 in rows2:
                if join_idx1 < len(row1) and join_idx2 < len(row2) and row1[join_idx1] == row2[join_idx2]:
                    joined_rows.append(row1 + row2)
        
        if where_clause:
            match = re.match(r"(\w+)\.(\w+)\s*=\s*([^']+|'[^']*')", where_clause)
            if not match:
                print("Error: Invalid WHERE clause")
                return
            
            where_table = match.group(1).lower()
            where_col = match.group(2).lower()
            where_val = match.group(3)
            
            if where_val.startswith("'") and where_val.endswith("'"):
                where_val = where_val[1:-1]
            
            where_header = f"{where_table}.{where_col}"
            if where_header not in joined_headers:
                print("Error: Column not found")
                return
            
            where_col_idx = joined_headers.index(where_header)
            filtered_rows = []
            
            for row in joined_rows:
                if where_col_idx < len(row) and row[where_col_idx] == where_val:
                    filtered_rows.append(row)
            
            joined_rows = filtered_rows
        
        if columns_str == "*":
            display_cols = joined_headers
            col_indices = list(range(len(joined_headers)))
        else:
            requested_cols = [col.strip().lower() for col in columns_str.split(',')]
            display_cols = []
            col_indices = []
            
            for col in requested_cols:
                if '.' in col:
                    if col in joined_headers:
                        display_cols.append(col)
                        col_indices.append(joined_headers.index(col))
                    else:
                        print("Warning: Column not found")
                else:
                    found = False
                    for i, header in enumerate(joined_headers):
                        if header.endswith(f".{col}"):
                            display_cols.append(header)
                            col_indices.append(i)
                            found = True
                    
                    if not found:
                        print("Warning: Column not found")
        
        self._display_results(display_cols, joined_rows, col_indices)

    def _display_results(self, headers, rows, col_indices):
        if not headers:
            print("No data")
            return
        
        print(','.join(headers))
        
        for row in rows:
            row_values = []
            for col_idx in col_indices:
                if col_idx < len(row):
                    value = str(row[col_idx])
                    row_values.append(value)
                else:
                    row_values.append("")
            
            print(','.join(row_values))


def main():
    db = SimpleFileDB()
    
    if len(sys.argv) > 1:
        sql_cmd = sys.argv[1]
        db.execute_command(sql_cmd)
    else:
        print("Error: No command provided")
        sys.exit(1)


if __name__ == "__main__":
    main()

#include <bits/stdc++.h>
#include <regex>

using namespace std;



class table{
    public:
        int columns;
        int rows;
        string content;
        table();
};

table :: table()
{
    columns = 0;
    rows = 0;
    content = "";
}

string to_lower(string input);

void create_table(string table_name, vector<string> column_names, map<string, table> &tables);
void insert_row(vector<string> entries, string table_name, map<string, table> &mp);
vector<string> splitString(const string& input);
void function_caller(string input, map<string, table> &mp);
vector<string> extractColumnNames(const string& input);
void vec_printer(vector<string> thing);
int main()
{
    
    /*map<string, table> tables;
    string a = "Test";
    vector<string> names = {"1", "2", "3"};
    string b = "test 2";
    vector<string> names_2 = {"a", "b", "c"};

    create_table(a, names, tables);
    create_table(b, names_2, tables);
    vector<string> entries = {"apple", "orange", "banana"};
    vector<string> entries_2 = {"chevy", "toyota", "honda"};
    insert_row(entries, a, tables);
    insert_row(entries_2, b, tables);
    cout << tables[a].content;
    cout << tables[b].content;*/
    string input;
    do
    {
    getline(cin, input);
    map<string, table> mp;
    function_caller(input, mp);
    }while(input != "exit" && input != "quit");
    



}

void create_table(string table_name, vector<string> column_names, map<string, table> &tables)
{
    ofstream MyFile("C:\\Users\\davin\\OneDrive\\Desktop\\c++\\database_systems\\database\\" + table_name);
    string temp;
    table b;
    for(int i = 0; i < column_names.size(); i++)
    {
        MyFile << column_names[i] + "{\n}\n";
        temp += column_names[i];
        temp += "{\n}\n";
        
    }
    b.content = temp;
    b.columns += column_names.size();
    tables[table_name] = b;
}

void insert_row(vector<string> entries, string table_name, map<string, table> &mp)
{
    vector<int> column_starts;
    bool in_quotes = false;
    string temp = mp[table_name].content;
    for(int i = 0; i < temp.size(); i++)
    {
        if(temp[i] == '"' && !in_quotes)
            in_quotes = true;
        else if(temp[i] == '"' && in_quotes)
            in_quotes = false;
        else if(temp[i] == '{' && !in_quotes)
        {
            column_starts.push_back(i);
        }
    }
    int incrementer = 0;
    for(int i = 0; i < column_starts.size(); i++)
    {
        incrementer += entries[i].size() + 1;
        column_starts[i + 1] += incrementer;
        mp[table_name].content.insert(column_starts[i] + 1, entries[i] + '\n');
            
    }
    mp[table_name].rows += 1;
    ofstream MyFile("C:\\Users\\davin\\OneDrive\\Desktop\\c++\\database_systems\\database\\" + table_name);;
    MyFile << mp[table_name].content;
}

string to_lower(string input)
{
    for(int i = 0; i < input.size(); i++)
    {
        if(input[i] >= 'A' && input[i] <= 'Z')
        {
            input[i] += 'a' - 'A';
        }
    }
    return input;
}
vector<string> splitString(const string& input) {
    vector<string> words;
    size_t pos = input.find('('); // Find the first '('

    if (pos != string::npos) {
        // Split the part before the parenthesis
        string beforeParen = input.substr(0, pos);
        istringstream beforeStream(beforeParen);
        string word;
        while (beforeStream >> word) {
            words.push_back(word); // Push words before the '('
        }

        // Now add the part after the parenthesis as a whole (including parentheses)
        string afterParen = input.substr(pos);
        words.push_back(afterParen);
    } else {
        // If no parenthesis, just split the entire string into words
        istringstream stream(input);
        string word;
        while (stream >> word) {
            words.push_back(word);
        }
    }

    return words;
}

void vec_printer(vector<string> thing)
{
    for(int i = 0; i < thing.size(); i++)
    {
        cout << thing[i] << endl;
    }
}

vector<string> extractColumnNames(const string& input) {
    vector<string> columnNames;
    size_t start = input.find('(');
    size_t end = input.find(')');
    
    if (start != string::npos && end != string::npos && start < end) {
        string content = input.substr(start + 1, end - start - 1);
        istringstream stream(content);
        string column;
        
        while (getline(stream, column, ',')) {
            size_t first = column.find_first_not_of(" ");
            size_t last = column.find_last_not_of(" ");
            if (first != string::npos && last != string::npos) {
                columnNames.push_back(column.substr(first, last - first + 1));
            }
        }
    }
    
    return columnNames;
}

void function_caller(string input, map<string, table> &mp)
{
    input = to_lower(input);
    vector<string> command = splitString(input);
    
    if(command[0] == "create")
    {
        string table_name = command[2];
        vector<string> col_names = extractColumnNames(command[3]);
        create_table(table_name, col_names, mp);
    }

  /*  if (regex_search(input, pattern)) {
        cout << "create table";
    } 
    else if(regex_search(input, insert)){
        cout << "Insert." << endl;
    }*/
}

import markdown
import os

# Define paths
base_dir = "/Users/tuanmanh/Phát triển hệ thống đặt tour du lịch thông minh với AI Travel Advisor cho công ty VN-Travel"
md_file_path = os.path.join(base_dir, "BAOCAO_KLTN_DRAFT.md")
html_file_path = os.path.join(base_dir, "BAOCAO_KLTN_DRAFT.html")

# Read Markdown content
with open(md_file_path, "r", encoding="utf-8") as f:
    text = f.read()

# Convert to HTML
html_content = markdown.markdown(text, extensions=['tables', 'fenced_code'])

# Wrap in HTML boilerplate with UTF-8 charset and Bootstrap
full_html = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BÁO CÁO KHOÁ LUẬN TỐT NGHIỆP</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f8f9fa;
            padding: 40px;
        }}
        .container {{
            background-color: white;
            padding: 50px;
            border-radius: 8px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            max-width: 1200px;
            margin: auto;
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        h1 {{
            text-align: center;
            color: #0d6efd;
            border-bottom: 3px solid #0d6efd;
            padding-bottom: 10px;
            margin-bottom: 40px;
        }}
        table {{
            width: 100%;
            margin-bottom: 1rem;
            color: #212529;
            border-collapse: collapse;
        }}
        th {{
            background-color: #0d6efd;
            color: white;
            padding: 12px;
            text-align: center;
        }}
        td {{
            padding: 10px;
            border: 1px solid #dee2e6;
        }}
        code {{
            background-color: #f1f3f5;
            padding: 2px 5px;
            border-radius: 4px;
            color: #d63384;
        }}
        pre {{
            background-color: #212529;
            color: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
        }}
        blockquote {{
            border-left: 5px solid #0d6efd;
            padding-left: 20px;
            margin-left: 0;
            color: #555;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        {html_content}
    </div>
</body>
</html>
"""

# Write to HTML file
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Successfully created {html_file_path} with UTF-8 encoding and Bootstrap styling.")

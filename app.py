import os
from flask import Flask, render_template, request
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

url = "https://gtdzrydriuzeavedudph.supabase.co/rest/v1/"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd0ZHpyeWRyaXV6ZWF2ZWR1ZHBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1NDk3NzEsImV4cCI6MjA5MjEyNTc3MX0.KhCCjejsx4nQLo-iY904t-q9GZmXTIQGziATQGrtX-4"

supabase = create_client(url, key)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    student_id = request.form.get('student_id')

    print("收到数据：", name, student_id)

    # 写入 Supabase
    user_id = "11111111-1111-1111-1111-111111111111"

    try:
        supabase.table("assessments").insert({
            "user_id": user_id,
            "username": name,
            "activity_name": "测试活动"
        }).execute()
    except Exception as e:
        print(f"错误: {e}")
        return f"提交失败: {str(e)}"

    return "提交成功！"


if __name__ == "__main__":
    app.run(debug=True)

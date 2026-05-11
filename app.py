import os
from flask import Flask, jsonify, render_template, request
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB，JSON 内含较多图片 URL 时放宽限制

_DEFAULT_URL = "https://gtdzrydriuzeavedudph.supabase.co"
_DEFAULT_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd0ZHpyeWRyaXV6ZWF2ZWR1ZHBoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY1NDk3NzEsImV4cCI6MjA5MjEyNTc3MX0.KhCCjejsx4nQLo-iY904t-q9GZmXTIQGziATQGrtX-4"


def _env_url() -> str:
    v = (os.getenv("SUPABASE_URL") or "").strip().rstrip("/")
    if v.startswith("http://") or v.startswith("https://"):
        return v
    return _DEFAULT_URL


def _env_key() -> str:
    return (
        os.getenv("SUPABASE_SERVICE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or _DEFAULT_ANON
    )


url = _env_url()
# 云端同步建议使用 SUPABASE_SERVICE_KEY（服务端），可绕过 RLS；未配置时回退 anon，需在 SQL 中为 anon 放行或关闭 RLS
key = _env_key()

supabase = create_client(url, key)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api/profile", methods=["GET"])
def api_profile_get():
    username = (request.args.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username required"}), 400
    try:
        res = (
            supabase.table("user_app_data")
            .select("user_id,items,categories,updated_at")
            .eq("username", username)
            .execute()
        )
        rows = res.data or []
        if not rows:
            return jsonify({"found": False})
        row = rows[0]
        return jsonify(
            {
                "found": True,
                "user_id": row.get("user_id"),
                "items": row.get("items") or [],
                "categories": row.get("categories") or [],
                "updated_at": row.get("updated_at"),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile", methods=["POST"])
def api_profile_post():
    body = request.get_json(silent=True) or {}
    username = (body.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username required"}), 400
    items = body.get("items")
    categories = body.get("categories")
    if items is None:
        items = []
    if categories is None:
        categories = []
    try:
        supabase.table("user_app_data").upsert(
            {"username": username, "items": items, "categories": categories},
            on_conflict="username",
        ).execute()
        res = (
            supabase.table("user_app_data")
            .select("user_id")
            .eq("username", username)
            .execute()
        )
        rows = res.data or []
        uid = rows[0]["user_id"] if rows else None
        return jsonify({"ok": True, "user_id": uid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    student_id = request.form.get('student_id')

    print("收到数据：", name, student_id)

    # 写入 Supabase
    user_id = "11111111-1111-1111-1111-111111111111"

    try:
        result = supabase.table("assessments").insert({
            "user_id": user_id,
            "username": name,
            "activity_name": "测试活动"
        }).execute()
        print("结果：", result)  # 加这行
    except Exception as e:
        print(f"完整错误: {repr(e)}")  # repr() 显示更多细节
        return f"提交失败: {repr(e)}"

    return "提交成功！"


if __name__ == "__main__":
    app.run(debug=True)

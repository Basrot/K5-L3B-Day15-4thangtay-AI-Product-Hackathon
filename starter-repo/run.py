"""Một lệnh cho mọi việc. Chạy được trên Windows, macOS, Linux với Python 3.10 trở lên (3.8–3.9 vẫn chạy, có nhắc).
Không cần cài thêm gì, không cần make.

  python run.py                         chạy bản chạy thử (codebase/app.py → codebase/agent.py)
  python run.py check                   kiểm eval/benchmark.csv + eval/metric_spec.yaml
  python run.py eval --try [N]          thử nối model: chạy N câu thử đầu (mặc định 3) → eval/run-try.csv
  python run.py eval                    chạy cả bộ câu thử → eval/run-N.csv + traces/run-N.jsonl
  python run.py eval --fake             thử bộ chạy, KHÔNG gọi agent → eval/run-fake.csv
  python run.py score eval/run-1.csv    tính % đạt sau khi điền cột pass
  python run.py simulate --try [N]      thử mô phỏng chi phí N phiên (mặc định 10) → cost/simulate-try.csv
  python run.py simulate                mô phỏng chi phí khi dùng thật (≥50 phiên) → cost/simulate-N.csv + bản tóm tắt
  (eval và simulate nhận thêm --wait 4: nghỉ 4 giây giữa hai lượt gọi, khi gói miễn phí giới hạn lượt / phút)

macOS/Linux có thể phải gõ python3 thay cho python. Windows có thể gõ py.
Nhóm dùng stack khác (Node, Streamlit…): sửa hàm run_app() để `python run.py` vẫn chạy được bản chạy thử.
"""
import os
import subprocess
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if sys.version_info < (3, 8):
    sys.exit("Cần Python 3.10 trở lên. Máy đang chạy Python %d.%d.\n"
             "Cài bản mới ở python.org rồi gõ lại lệnh (macOS/Linux: thử python3, Windows: thử py)."
             % sys.version_info[:2])
if sys.version_info < (3, 10):
    print("(Lưu ý: máy đang dùng Python %d.%d. Bộ khung vẫn chạy; thư viện nhóm cài thêm có thể cần 3.10+.)"
          % sys.version_info[:2])

ROOT = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.join("eval", "run_eval.py")
SIMULATE = os.path.join("cost", "simulate.py")

HELP = """Các lệnh dùng được:
  python run.py                         chạy bản chạy thử
  python run.py check                   kiểm bộ câu thử + metric spec
  python run.py eval --try [N]          thử nối model với N câu đầu (mặc định 3)
  python run.py eval                    chạy cả bộ câu thử → eval/run-N.csv
  python run.py eval --fake             thử bộ chạy, không gọi agent
  python run.py score eval/run-1.csv    tính % đạt sau khi điền cột pass
  python run.py simulate --try [N]      thử mô phỏng chi phí N phiên (mặc định 10)
  python run.py simulate                mô phỏng chi phí khi dùng thật → cost/simulate-N.csv
  (thêm --wait 4 sau eval / simulate để nghỉ 4 giây giữa hai lượt gọi)
(macOS/Linux có thể phải gõ python3; Windows có thể gõ py)"""


def py(*args):
    """Chạy một file Python khác bằng đúng trình Python đang chạy file này."""
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    sys.stdout.flush()
    return subprocess.call([sys.executable] + list(args), cwd=ROOT, env=env)


def run_app():
    return py(os.path.join("codebase", "app.py"))


def main(argv):
    if not argv:
        return run_app()
    cmd, rest = argv[0], argv[1:]
    if cmd == "check":
        if rest:
            print("check không nhận thêm tham số: " + " ".join(rest) + "\n" + HELP)
            return 2
        return py(EVAL, "--check")
    if cmd == "eval":
        return py(EVAL, *rest)
    if cmd == "score":
        if len(rest) != 1:
            print("Cần đúng một file. Ví dụ: python run.py score eval/run-1.csv")
            return 2
        path = os.path.abspath(rest[0]) if os.path.exists(rest[0]) else rest[0]
        return py(EVAL, "--score", path)
    if cmd == "simulate":
        return py(SIMULATE, *rest)
    if cmd in ("bench", "bench-fake"):
        print("Lệnh %s đã đổi tên: dùng `python run.py eval` (thử: `eval --try`, không gọi agent: `eval --fake`)." % cmd)
        return 2
    if cmd in ("-h", "--help", "help"):
        print(HELP)
        return 0
    print("Không hiểu lệnh: " + " ".join(argv) + "\n" + HELP)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Тесты MindKit без сети и без графической сессии: python3 -m unittest discover tests"""

from __future__ import annotations

import json
import os
import socket
import stat
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["MINDKIT_NOTIFY"] = "off"
os.environ["MINDKIT_CLIPBOARD"] = "memory"
os.environ["MINDKIT_KEYCHAIN"] = "file"

from mindkit import (assistant, clipboard, config, design, keychain, link, notify, search,  # noqa: E402
                     shortcuts, store)
from mindkit.cli import main as cli  # noqa: E402

# Второе устройство: отдельный процесс со своей папкой MINDKIT_HOME.
# Буфер обмена у него пишется в файл, чтобы тест мог его прочитать.
PEER_SCRIPT = r"""
import sys, time
sys.path.insert(0, sys.argv[1])
from mindkit import clipboard, link
from pathlib import Path
out = Path(sys.argv[2])
clipboard.set = lambda text: out.write_text(text, encoding="utf-8")
d = link.Daemon(port=int(sys.argv[3]), discovery_port=int(sys.argv[4]), clipboard_sync=False,
                host="127.0.0.1").start()
print("ready", flush=True)
while True:
    time.sleep(1)
"""


def free_port(kind=socket.SOCK_STREAM) -> int:
    s = socket.socket(socket.AF_INET, kind)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name)
        os.environ["MINDKIT_HOME"] = str(self.home)
        for k in list(os.environ):
            if k.startswith("MINDTAG_"):
                del os.environ[k]

    def tearDown(self):
        self.tmp.cleanup()


class ConfigTest(Base):
    def test_defaults_and_device(self):
        dev = config.device()
        self.assertTrue(dev["id"] and dev["name"])
        self.assertEqual(config.device()["id"], dev["id"], "id устройства постоянный")
        self.assertEqual(config.get("link.port"), 47800)

    def test_set_and_env_override(self):
        config.set("gateway.url", "http://gw:9/v1")
        self.assertEqual(config.get("gateway.url"), "http://gw:9/v1")
        os.environ["MINDTAG_GATEWAY_URL"] = "http://env/v1"
        self.assertEqual(config.get("gateway.url"), "http://env/v1")
        os.environ["MINDTAG_LINK_PORT"] = "5000"
        self.assertEqual(config.get("link.port"), 5000)


class KeychainTest(Base):
    def test_roundtrip_and_permissions(self):
        keychain.set("GROQ_API_KEY", "gsk_secret_value")
        self.assertEqual(keychain.get("GROQ_API_KEY"), "gsk_secret_value")
        self.assertEqual(keychain.names(), ["GROQ_API_KEY"])
        if os.name != "nt":
            mode = stat.S_IMODE((self.home / "keychain.json").stat().st_mode)
            self.assertEqual(mode, 0o600)
        self.assertTrue(keychain.delete("GROQ_API_KEY"))
        self.assertEqual(keychain.get("GROQ_API_KEY"), "")

    def test_load_env_does_not_override(self):
        keychain.set("MK_TEST_A", "from-keychain")
        keychain.set("MK_TEST_B", "from-keychain")
        os.environ["MK_TEST_B"] = "from-env"
        try:
            self.assertEqual(keychain.load_env(), ["MK_TEST_A"])
            self.assertEqual(os.environ["MK_TEST_A"], "from-keychain")
            self.assertEqual(os.environ["MK_TEST_B"], "from-env")
        finally:
            os.environ.pop("MK_TEST_A", None)
            os.environ.pop("MK_TEST_B", None)

    def test_bad_name(self):
        with self.assertRaises(ValueError):
            keychain.set("bad name", "x")

    def test_cli_import_env(self):
        env = self.home / "app.env"
        env.write_text("# пример\nOPENAI_API_KEY=sk-123\nPORT=8000\nexport HF_TOKEN='hf_abc'\n", encoding="utf-8")
        self.assertEqual(cli(["keychain", "import", str(env)]), 0)
        self.assertEqual(keychain.names(), ["HF_TOKEN", "OPENAI_API_KEY"])
        self.assertEqual(keychain.get("HF_TOKEN"), "hf_abc")


class NotifyTest(Base):
    def test_history(self):
        notify.send("Сборка", "ISO готов", app="AIsktagOS")
        notify.send("Mind", "ответ готов")
        hist = notify.history()
        self.assertEqual([h["title"] for h in hist], ["Сборка", "Mind"])
        notify.clear()
        self.assertEqual(notify.history(), [])


class SearchTest(Base):
    def test_score_order(self):
        self.assertGreater(search.score("mind", "mind"), search.score("mind", "mind-ide"))
        self.assertGreater(search.score("mind", "mind-ide"), search.score("mind", "aisktag-mind.py"))
        self.assertGreater(search.score("mide", "mind-ide"), 0)
        self.assertEqual(search.score("xyz", "mind"), 0)

    def test_everything(self):
        proj = self.home / "projects" / "demo"
        (proj / "node_modules").mkdir(parents=True)
        (proj / "router.py").write_text("def pick_model():\n    return 'qwen'\n", encoding="utf-8")
        (proj / "node_modules" / "router.js").write_text("skip", encoding="utf-8")
        keychain.set("GROQ_API_KEY", "x")
        roots = [str(self.home / "projects")]
        res = search.search("router", roots=roots)
        files = [r for r in res if r["kind"] == "file"]
        self.assertEqual(len(files), 1, "node_modules пропускается")
        self.assertEqual(search.search("groq", roots=roots)[0]["kind"], "key")
        self.assertTrue(any(r["kind"] == "app" and r["title"] == "Mind IDE" for r in search.search("Mind IDE",
                                                                                                    roots=roots)))
        hits = search.search("pick_model", roots=roots, content=True)
        self.assertTrue(any(r["kind"] == "text" and r["action"]["line"] == 1 for r in hits))


class ShortcutsTest(Base):
    def test_builtin_listed(self):
        names = [s["name"] for s in shortcuts.list_all()]
        self.assertIn("Объяснить код", names)

    def test_run_chain_and_vars(self):
        sc = {"name": "Проверка", "steps": [
            {"action": "text", "text": "привет", "save": "greeting"},
            {"action": "text", "text": "{{greeting}}, {{input}}!"},
            {"action": "clipboard.set"},
            {"action": "notify", "title": "Готово"},
        ]}
        shortcuts.save(sc)
        self.assertEqual(shortcuts.run("проверка", "мир"), "привет, мир!")
        self.assertEqual(clipboard.get(), "привет, мир!")
        self.assertEqual(notify.history()[-1]["body"], "привет, мир!")

    def test_shell_and_nesting(self):
        shortcuts.save({"name": "inner", "steps": [{"action": "shell", "command": "echo inside"}]})
        shortcuts.save({"name": "outer", "steps": [{"action": "shortcut", "name": "inner"}]})
        self.assertEqual(shortcuts.run("outer"), "inside")
        shortcuts.save({"name": "loop", "steps": [{"action": "shortcut", "name": "loop"}]})
        with self.assertRaises(shortcuts.ShortcutError):
            shortcuts.run("loop")

    def test_unknown_action_rejected(self):
        with self.assertRaises(shortcuts.ShortcutError):
            shortcuts.save({"name": "x", "steps": [{"action": "format_disk"}]})


class FakeModel(BaseHTTPRequestHandler):
    seen: list = []

    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeModel.seen.append({"auth": self.headers.get("Authorization"), "body": body})
        out = json.dumps({"model": body["model"], "choices": [
            {"message": {"role": "assistant", "content": "ответ: " + body["messages"][-1]["content"]}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)


class AssistantTest(Base):
    def test_gateway_then_fallback(self):
        srv = ThreadingHTTPServer(("127.0.0.1", 0), FakeModel)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            dead = f"http://127.0.0.1:{free_port()}/v1"
            config.set("gateway.url", dead)
            config.set("ollama.url", f"http://127.0.0.1:{srv.server_address[1]}/v1")
            res = assistant.chat([{"role": "user", "content": "2+2"}])
            self.assertEqual(res["via"], "Ollama")
            self.assertEqual(res["text"], "ответ: 2+2")
            # Ключ шлюза берётся из связки ключей
            config.set("gateway.url", f"http://127.0.0.1:{srv.server_address[1]}/v1")
            keychain.set("AIDUO_API_KEY", "duo-key")
            self.assertEqual(assistant.ask("привет"), "ответ: привет")
            self.assertEqual(FakeModel.seen[-1]["auth"], "Bearer duo-key")
            shortcuts.save({"name": "ai", "steps": [{"action": "ask", "prompt": "q={{input}}"}]})
            self.assertEqual(shortcuts.run("ai", "5"), "ответ: q=5")
        finally:
            srv.shutdown()
            srv.server_close()


class StoreTest(Base):
    def test_catalog(self):
        apps = {a["id"]: a for a in store.apps()}
        self.assertIn("mind-ide", apps)
        self.assertEqual(apps["aisktagos"]["kind"], "os")
        self.assertFalse(apps["mind-ide"]["installed"])

    def test_install_dry_run(self):
        config.set("store.apps_dir", str(self.home / "apps"))
        logs = []
        path = store.install("itis-browser", dry=True, log=logs.append)
        self.assertEqual(path, self.home / "apps" / "ITIS-browser")
        self.assertIn("git clone https://github.com/tagiriskaliev18-hash/ITIS-browser.git", logs[0])
        with self.assertRaises(store.StoreError):
            store.install("aisktagos", dry=True, log=logs.append)


class DesignTest(unittest.TestCase):
    def test_css_qss(self):
        css = design.css()
        self.assertIn("--mt-accent: #6e56cf;", css)
        self.assertIn("--mt-glass: rgba(255, 255, 255, 0.051);", css)
        self.assertIn("QPushButton", design.qss())


class LinkTest(Base):
    """Два устройства на одном компьютере: этот процесс и дочерний."""

    def setUp(self):
        super().setUp()
        self.key = link.init_account()
        self.peer_home = self.home / "peer"
        self.peer_home.mkdir()
        self.clip_file = self.peer_home / "clip.txt"
        self.port, self.dport = free_port(), free_port(socket.SOCK_DGRAM)
        env = dict(os.environ, MINDKIT_HOME=str(self.peer_home))
        # Второе устройство входит в тот же аккаунт
        subprocess.run([sys.executable, "-m", "mindkit", "link", "join", self.key], env=env, cwd=ROOT, check=True,
                       capture_output=True)
        subprocess.run([sys.executable, "-m", "mindkit", "config", "set", "device.name", "Ноутбук"], env=env,
                       cwd=ROOT, check=True, capture_output=True)
        self.proc = subprocess.Popen([sys.executable, "-c", PEER_SCRIPT, str(ROOT), str(self.clip_file),
                                      str(self.port), str(self.dport)], env=env, stdout=subprocess.PIPE)
        self.assertEqual(self.proc.stdout.readline().strip(), b"ready")

    def tearDown(self):
        self.proc.kill()
        self.proc.wait()
        self.proc.stdout.close()
        super().tearDown()

    def peer_data(self, name):
        return json.loads((self.peer_home / "data" / name).read_text(encoding="utf-8"))

    def test_key_format(self):
        self.assertEqual(len(link._parse_key(self.key)), 32)
        with self.assertRaises(ValueError):
            link.join_account("ABCD-EFGH")

    def test_discovery(self):
        found = link.discover(timeout=1.0, port=self.dport)
        self.assertEqual([f["name"] for f in found], ["Ноутбук"])
        self.assertEqual(found[0]["port"], self.port)
        self.assertIn("Ноутбук", [p["name"] for p in link.peers().values()])

    def test_continuity(self):
        link.discover(timeout=1.0, port=self.dport)
        # Общий буфер обмена
        self.assertEqual(link.send_clipboard("git push origin main"), {"Ноутбук": "ok"})
        self.assertEqual(self.clip_file.read_text(encoding="utf-8"), "git push origin main")
        # Уведомление на другом устройстве
        self.assertEqual(link.send_notification("Сборка", "ISO готов", to="Ноут"), {"Ноутбук": "ok"})
        # Handoff: ссылка и маленький файл с номером строки
        link.handoff(link.make_activity("url", "Документация", url="https://example.org/docs"))
        src = self.home / "main.py"
        src.write_text("print('hi')\n", encoding="utf-8")
        link.handoff(link.make_activity("file", path=str(src), line=1))
        inbox = self.peer_data("handoff.json")
        self.assertEqual(inbox[1]["url"], "https://example.org/docs")
        self.assertEqual(Path(inbox[0]["local_path"]).read_text(encoding="utf-8"), "print('hi')\n")
        self.assertEqual(inbox[0]["line"], 1)
        # MindDrop
        big = self.home / "отчёт.bin"
        big.write_bytes(os.urandom(200_000))
        self.assertEqual(link.drop(big), {"Ноутбук": "ok"})
        self.assertEqual((self.peer_home / "MindDrop" / "отчёт.bin").read_bytes(), big.read_bytes())
        hist = [json.loads(x) for x in (self.peer_home / "data" / "notifications.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(hist[0]["title"], "Сборка")
        self.assertTrue(any(h["title"].startswith("MindDrop") for h in hist))

    def test_foreign_account_rejected(self):
        link.discover(timeout=1.0, port=self.dport)
        link.init_account(force=True)  # теперь у нас другой аккаунт
        res = link.send_clipboard("чужой текст")
        self.assertIn("403", res["Ноутбук"])
        self.assertFalse(self.clip_file.exists())
        self.assertEqual(link.discover(timeout=0.6, port=self.dport), [], "чужой аккаунт не виден")

    def test_peer_learns_us_back(self):
        # У нас своя служба: второе устройство по запросу поиска само проверит нас ping-ом
        port = free_port()
        config.set("link.port", port)
        me = link.Daemon(port=port, discovery_port=0, clipboard_sync=False, host="127.0.0.1").start()
        try:
            link.discover(timeout=1.0, port=self.dport)
            name = config.device()["name"]
            for _ in range(30):
                peers_file = self.peer_home / "data" / "peers.json"
                if peers_file.exists() and name in peers_file.read_text(encoding="utf-8"):
                    break
                time.sleep(0.1)
            self.assertIn(name, [p["name"] for p in self.peer_data("peers.json").values()])
        finally:
            me.stop()

    def test_forged_peer_not_trusted(self):
        # Сервер, который знает тег поиска, но не ключ: ответ без подписи
        class Liar(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                raw = json.dumps({"ok": True, "id": "evil", "name": "Ловушка"}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

        srv = ThreadingHTTPServer(("127.0.0.1", 0), Liar)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            self.assertIsNone(link.verify_peer("127.0.0.1", srv.server_address[1]))
            self.assertNotIn("evil", link.peers())
        finally:
            srv.shutdown()
            srv.server_close()

    def test_replay_rejected(self):
        import urllib.request
        peer = {"host": "127.0.0.1", "port": self.port}
        captured = {}
        real = link.net.urlopen

        def spy(req, timeout=30):
            captured["req"] = req
            return real(req, timeout)

        link.net.urlopen = spy
        try:
            link.request(peer, "/v1/clipboard", {"text": "один раз"})
        finally:
            link.net.urlopen = real
        old = captured["req"]
        again = urllib.request.Request(old.full_url, data=old.data, headers=dict(old.header_items()), method="POST")
        with self.assertRaises(Exception) as ctx:
            link.net.urlopen(again, 5)
        self.assertIn("403", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

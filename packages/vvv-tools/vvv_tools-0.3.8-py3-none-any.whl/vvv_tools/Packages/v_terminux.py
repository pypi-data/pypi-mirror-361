# [
#     { "keys": ["ctrl+alt+`"], "command": "v_terminux" },
#     { "keys": ["ctrl+w"], "command": "v_close" }
# ]

import os, re
import re
import base64
import sublime
import sublime_plugin
import subprocess
import threading
import http.client
import json

class DeepseekNewWindowCompletionCommand(sublime_plugin.TextCommand):
    cfgfile = os.path.join(os.path.expanduser("~"),'.vsublime.cfg.py')
    def run(self, edit):
        deepseek_key = ""
        with open(self.cfgfile, 'r', encoding='utf8') as f:
            d = re.findall(r'\[config\] deepseek_key: *([a-zA-Z0-9-]+)', f.read())
            if d and d[0].startswith('sk-'): 
                deepseek_key = d[0]
        selections = self.view.sel()
        if not selections:
            sublime.status_message("No text selected")
            return
        selected_text = self.view.substr(selections[0])
        sublime.status_message("Requesting code completion...")
        self.output_view = self.create_output_window()
        thread = DeepseekStreamingApiThread(
            deepseek_key,
            selected_text,
            self.handle_stream_response,
            self.handle_completion,
            self.handle_error
        )
        thread.start()

    def create_output_window(self):
        window = sublime.active_window()
        window.set_layout({
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
        })
        window.focus_group(1)
        output_view = window.new_file()
        output_view.set_name("DeepSeek Code Completion")
        output_view.set_scratch(True)
        output_view.set_syntax_file("Packages/Text/Plain text.tmLanguage")
        return output_view

    def handle_stream_response(self, text_chunk):
        sublime.set_timeout(lambda: self.append_to_output(text_chunk), 0)

    def append_to_output(self, text):
        if hasattr(self, 'output_view') and self.output_view:
            self.output_view.run_command("append_text", {"text": text})

    def handle_completion(self):
        sublime.status_message("Completion finished in output window")

    def handle_error(self, error):
        sublime.status_message("Error: " + str(error))
        if hasattr(self, 'output_view') and self.output_view:
            self.output_view.run_command("append_text", {"text": "\n\nError: " + str(error)})

class AppendTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        self.view.insert(edit, self.view.size(), text)
        self.view.show(self.view.size())

class DeepseekStreamingApiThread(threading.Thread):
    def __init__(self, api_key, prompt, chunk_callback, completion_callback, error_callback):
        threading.Thread.__init__(self)
        self.prompt = prompt
        self.chunk_callback = chunk_callback
        self.completion_callback = completion_callback
        self.error_callback = error_callback
        self.api_key = api_key
        self.stop_event = threading.Event()

    def run(self):
        try:
            conn = http.client.HTTPSConnection("api.deepseek.com")
            payload = json.dumps({
                "model": "deepseek-chat",
                "prompt": self.prompt,
                "max_tokens": 1024,
                "temperature": 0.7,
                "stream": True
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream',
                'Authorization': 'Bearer ' + self.api_key
            }
            conn.request("POST", "/beta/completions", payload, headers)
            response = conn.getresponse()
            if response.status != 200:
                self.error_callback("API error: " + str(response.status) + " " + response.reason)
                return
            buffer = b""
            while not self.stop_event.is_set():
                chunk = response.read(1024)
                if not chunk:
                    break
                buffer += chunk
                lines = buffer.split(b'\n')
                for line in lines[:-1]:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith(b'data: '):
                        data = line[6:]
                        if data == b'[DONE]':
                            self.completion_callback()
                            return
                        try:
                            json_data = json.loads(data.decode('utf-8'))
                            if 'choices' in json_data and json_data['choices']:
                                text_chunk = json_data['choices'][0].get('text', '')
                                self.chunk_callback(text_chunk)
                        except ValueError:
                            continue
                buffer = lines[-1]
            self.completion_callback()
        except Exception as e:
            self.error_callback(str(e))
        finally:
            try:
                conn.close()
            except:
                pass

    def stop(self):
        self.stop_event.set()

class CancelDeepseekCompletionCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        for thread in threading.enumerate():
            if isinstance(thread, DeepseekStreamingApiThread):
                thread.stop()













class FoldExcessLengthOnLoad(sublime_plugin.EventListener):
    cfgfile = os.path.join(os.path.expanduser("~"),'.vsublime.cfg.py')
    def __init__(self):
        self.max_line_length = 500  # 定义最大行长度

    def on_load(self, view):
        self.fold_excess_length(view)

    def fold_excess_length(self, view):
        max_line_length = self.max_line_length
        with open(self.cfgfile, 'r', encoding='utf8') as f:
            d = re.findall(r'\[config\] max_line_length: *(\d+)', f.read())
            if d: 
                max_line_length = int(d[0])
        for region in view.lines(sublime.Region(0, view.size())):
            line_text = view.substr(region)
            if len(line_text) > max_line_length:
                excess_region = sublime.Region(region.begin() + max_line_length, region.end())
                view.fold(excess_region)

    def on_activated(self, view):
        self.fold_excess_length(view)











class VTerminuxCommand(sublime_plugin.TextCommand):
    cfgfile = os.path.join(os.path.expanduser("~"),'.vsublime.cfg.py')
    batfile = os.path.join(os.path.expanduser("~"),'.temp.bat')
    def load_config(self):
        if not os.path.isfile(self.cfgfile):
            with open(self.cfgfile, 'w', encoding='utf8') as f:
                demo = [
                    "[config] max_line_length: 500",
                    "[config] deepseek_key: none",
                    "[right] python ${file}",
                ]
                f.write('\n')
        with open(self.cfgfile, encoding='utf8') as f:
            data = f.read()
        r = []
        for i in data.splitlines():
            t = i.strip()
            if t and not t.startswith('#') and '[config]' not in t:
                def rep(g): return g.group(1)
                a = re.sub(r'\{\{(.*?)\}\}', lambda g:"********", t)
                b = re.sub(r'\{\{(.*?)\}\}', rep, t)
                r.append([a, b])
            if '[config]' in t and re.findall('deepseek_key: *sk-[a-zA-Z0-9-]+', t):
                r.append(['[deepseek]', 'deepseek'])
        return r
    def load_ssh_key(self, name):
        try:
            pub = os.path.join(os.path.expanduser("~"), '.ssh', 'id_rsa.pub')
            if not os.path.isfile(pub):
                print('不存在本地的 .ssh 公钥文件')
                return
            with open(pub, encoding='utf-8') as f:
                pubcode = f.read()
                pc = re.findall(r'ssh-rsa [^ ]+', pubcode)
                if not pc:
                    raise Exception('no ssh-rsa')
                pc = pc[0]
            cmd = '[[ -f ~/.ssh/authorized_keys ]] || touch ~/.ssh/authorized_keys; grep -q "'+pc+'" ~/.ssh/authorized_keys || echo "'+pc+'" >> ~/.ssh/authorized_keys'
            cmd = cmd + ' ' + name.split(' ')[0]
            print('---- 在登录进去后使用下面的命令行将本地的 ssh 公钥上传上去,下次连接则不虚要密钥就能登录 ----')
            print(cmd)
            print('--------')
            _temp = name.split(' ')
            if len(_temp) < 2:
                return
            up, pss = name.split(' ')[:2]
            user, ipp = up.split('@')
            ipp = ipp.split(':')
            if len(ipp) == 1:
                _ip,_port = ipp[0],"23"
            else:
                _ip,_port = ipp[0],ipp[1]
            run_code = (   
                """ python -c "import paramiko;import base64;client=paramiko.SSHClient();"""
                """client.set_missing_host_key_policy(paramiko.AutoAddPolicy());""" 
                """client.connect('"""+_ip+"""',username='"""+user+"""',password='"""+pss+"""',port="""+_port+""");"""
                """stdin,stdout,stderr=client.exec_command(base64.b64decode('""" + base64.b64encode(cmd.encode()).decode() + """'.encode()).decode());"""
                """output=stdout.read().decode();print(output)" """
            )
            # print(run_code)
        except:
            import traceback
            print(traceback.format_exc())
    def run(self, edit):
        ssh_addresses = self.load_config()
        ssh_addresses.append(('[*] open_config', 'open_config'))
        ssh_addresses.append(('[*] terminus_open', 'terminus_open'))
        options = [name for name, _ in ssh_addresses]
        self.view.window().show_quick_panel(options, lambda index: self.on_done(index, ssh_addresses))

    def on_done(self, index, ssh_addresses):
        if index == -1: return
        command = ssh_addresses[index][1]
        if command == 'open_config':
            new_view = sublime.active_window().open_file(self.cfgfile)
            return
        if command == 'terminus_open':
            self.view.window().run_command("terminus_open", { "cwd": "${file_path}" })
            return
        if command == 'deepseek':
            self.view.window().run_command("deepseek_new_window_completion")
            return
        cmd = []
        _cmds = command.split(' ')
        is_right = False
        is_bottom = False
        is_goback = False
        is_bat = False
        is_ssh = False
        is_auto_close = False
        for i in range(10):
            if _cmds[0] == '[close]':
                _cmds = _cmds[1:]
                is_auto_close = True
            if _cmds[0] == '[right]':
                is_right = True
                _cmds = _cmds[1:]
            if _cmds[0] == '[bottom]':
                is_bottom = True
                _cmds = _cmds[1:]
            if _cmds[0] == '[back]':
                is_goback = True
                _cmds = _cmds[1:]
            if not is_ssh and _cmds[0] == 'ssh':
                self.load_ssh_key(' '.join(_cmds[1:]))
                _cmds = _cmds[:2]
                is_ssh = True
            if _cmds[0] == '[bat]':
                _cmds = _cmds[1:]
                is_bat = True
            if "&&" in _cmds:
                is_bat = True
        cmd.extend(_cmds)
        file_path = self.view.file_name()
        if not file_path:
            print('no curr file')
            return
        cwd = os.path.dirname(file_path)
        for idx, i in enumerate(cmd):
            if "${file}" in i:
                file_name = os.path.split(file_path)[-1]
                cmd[idx] = file_name.join(i.split("${file}"))
        if is_bat:
            with open(self.batfile, 'w', encoding='utf8') as f:
                f.write("chcp 65001\n")
                for i in " ".join(cmd).split('&&'):
                    f.write(i + '\n')
            cmd = [self.batfile]
        print(cmd)
        print(cwd)
        window = sublime.active_window()
        # layout = window.get_layout()
        if is_right:
            window.set_layout({
                "cols": [0.0, 0.5, 1.0],
                "rows": [0.0, 1.0],
                "cells": [[0, 0, 1, 1], [1, 0, 2, 1]]
            })
            window.focus_group(1)
        if is_bottom:
            window.set_layout({
                "cols": [0.0, 1.0],
                "rows": [0.0, 0.5, 1.0],
                "cells": [[0, 0, 1, 1], [0, 1, 1, 2]]
            })
            window.focus_group(1)
        self.view.window().run_command("terminus_open", {
            "cmd": cmd,
            "cwd": cwd,
            "auto_close": is_auto_close,
        })
        if (is_right or is_bottom) and is_goback:
            sublime.set_timeout(lambda:window.focus_group(0), 300)

class VCloseCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        layout_one = {"cols": [0.0, 1.0], "rows": [0.0, 1.0], "cells": [[0, 0, 1, 1]]}
        if self.view.window().num_groups() == 2 and len(self.view.window().views_in_group(1)) == 0:
            self.view.window().set_layout(layout_one)
        else:
            self.view.window().run_command("close")
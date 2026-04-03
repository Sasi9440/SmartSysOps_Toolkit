import os
import shutil
import zipfile

BASE = "D:\\"

def safe_path(path):
    # Strip any absolute prefix so C:\foo becomes D:\foo
    path = os.path.splitdrive(path)[1].lstrip("\\/")
    full = os.path.abspath(os.path.join(BASE, path))
    if not full.upper().startswith(os.path.abspath(BASE).upper()):
        raise PermissionError("Access restricted to D: drive only.")
    return full

def create_file(name):
    p = safe_path(name)
    os.makedirs(os.path.dirname(p) or BASE, exist_ok=True)
    open(p, 'a').close()
    print(f"File created: {p}")

def create_folder(name):
    p = safe_path(name)
    os.makedirs(p, exist_ok=True)
    print(f"Folder created: {p}")

def delete(name):
    p = safe_path(name)
    if os.path.isdir(p):
        shutil.rmtree(p)
    else:
        os.remove(p)
    print(f"Deleted: {p}")

def move(src, dst):
    s, d = safe_path(src), safe_path(dst)
    shutil.move(s, d)
    print(f"Moved: {s} -> {d}")

def rename(src, new_name):
    s = safe_path(src)
    d = os.path.join(os.path.dirname(s), new_name)
    safe_path(d)  # validate destination too
    os.rename(s, d)
    print(f"Renamed: {s} -> {d}")

def copy(src, dst):
    s, d = safe_path(src), safe_path(dst)
    if os.path.isdir(s):
        shutil.copytree(s, d)
    else:
        shutil.copy2(s, d)
    print(f"Copied: {s} -> {d}")

def list_dir(path="."):
    p = safe_path(path)
    items = os.listdir(p)
    if not items:
        print("(empty)")
    for item in items:
        full = os.path.join(p, item)
        tag = "[DIR]" if os.path.isdir(full) else "[FILE]"
        print(f"  {tag} {item}")

def read_file(name):
    p = safe_path(name)
    with open(p, 'r') as f:
        print(f.read())

def write_file(name, content):
    p = safe_path(name)
    with open(p, 'w') as f:
        f.write(content)
    print(f"Written to: {p}")

def search(keyword, path="."):
    p = safe_path(path)
    found = False
    for root, dirs, files in os.walk(p):
        for name in dirs + files:
            if keyword.lower() in name.lower():
                full = os.path.join(root, name)
                tag = "[DIR]" if os.path.isdir(full) else "[FILE]"
                print(f"  {tag} {full}")
                found = True
    if not found:
        print(f"No results for '{keyword}'")

def tree(path=".", prefix=""):
    p = safe_path(path) if prefix == "" else path
    items = sorted(os.listdir(p))
    for i, item in enumerate(items):
        full = os.path.join(p, item)
        connector = "└── " if i == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(full):
            extension = "    " if i == len(items) - 1 else "│   "
            tree(full, prefix + extension)

def find_in_file(text, name):
    p = safe_path(name)
    with open(p, 'r', errors='ignore') as f:
        for i, line in enumerate(f, 1):
            if text.lower() in line.lower():
                print(f"  Line {i}: {line.rstrip()}")

def get_size(name):
    p = safe_path(name)
    if os.path.isfile(p):
        size = os.path.getsize(p)
    else:
        size = sum(os.path.getsize(os.path.join(r, f))
                   for r, _, files in os.walk(p) for f in files)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            print(f"Size: {size:.2f} {unit}")
            return
        size /= 1024
    print(f"Size: {size:.2f} TB")

def zip_path(src, dst):
    s = safe_path(src)
    d = safe_path(dst)
    with zipfile.ZipFile(d, 'w', zipfile.ZIP_DEFLATED) as zf:
        if os.path.isfile(s):
            zf.write(s, os.path.basename(s))
        else:
            for root, _, files in os.walk(s):
                for file in files:
                    fp = os.path.join(root, file)
                    zf.write(fp, os.path.relpath(fp, os.path.dirname(s)))
    print(f"Zipped: {s} -> {d}")

def unzip_path(src, dst):
    s = safe_path(src)
    d = safe_path(dst)
    with zipfile.ZipFile(s, 'r') as zf:
        zf.extractall(d)
    print(f"Unzipped: {s} -> {d}")

def hash_file(name, algo="sha256"):
    import hashlib
    p = safe_path(name)
    h = hashlib.new(algo)
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    print(f"  MD5    : {hashlib.md5(open(p,'rb').read()).hexdigest()}")
    print(f"  SHA256 : {h.hexdigest()}")

def compare_files(f1, f2):
    p1, p2 = safe_path(f1), safe_path(f2)
    lines1 = open(p1, 'r', errors='ignore').readlines()
    lines2 = open(p2, 'r', errors='ignore').readlines()
    diffs = [(i+1, l1.rstrip(), l2.rstrip())
             for i, (l1, l2) in enumerate(zip(lines1, lines2)) if l1 != l2]
    if len(lines1) != len(lines2):
        print(f"  Line count differs: {len(lines1)} vs {len(lines2)}")
    if not diffs:
        print("Files are identical.")
    else:
        for ln, a, b in diffs:
            print(f"  Line {ln}:")
            print(f"    < {a}")
            print(f"    > {b}")

def tail_file(name, n=10):
    p = safe_path(name)
    with open(p, 'r', errors='ignore') as f:
        lines = f.readlines()
    for line in lines[-n:]:
        print(line, end='')

def count_file(name):
    p = safe_path(name)
    with open(p, 'r', errors='ignore') as f:
        content = f.read()
    lines = content.splitlines()
    words = content.split()
    print(f"  Lines : {len(lines)}")
    print(f"  Words : {len(words)}")
    print(f"  Chars : {len(content)}")

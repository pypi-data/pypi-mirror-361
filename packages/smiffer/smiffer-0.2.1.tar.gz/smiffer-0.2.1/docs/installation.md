# ⚙️ Installation

## 📦 Using pipx (recommended)

- pipx link: [https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx](https://github.com/pypa/pipx?tab=readme-ov-file#install-pipx)

```bash
$ pipx install smiffer

# Checking the installation is done.
$ smiffer --help
```

> **🦊 From the GitLab repository:**
> 
> ```bash
> $ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
> $ cd smiffer/
> $ pipx install .
> 
> # Checking the installation is done.
> $ smiffer --help
> ```

## 🐍 Using pip

```bash
$ python3 -m pip install smiffer

# Checking the installation is done.
$ smiffer --help
```

> **🦊 From the GitLab repository:**
> 
> ```bash
> $ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
> $ cd smiffer/
> $ python3 -m pip install .
> 
> # Checking the installation is done.
> $ smiffer --help
> ```

## 🐋 Using docker

```bash
$ 
```

## 🛠 From scratch (not recommended)

```bash
$ git clone https://gitlab.galaxy.ibpc.fr/rouaud/smiffer.git
$ cd smiffer

# Install globaly these packages…
$ pip install -r env/requirements.txt

# Checking the installation is done.
$ python -m src.smiffer --help
```

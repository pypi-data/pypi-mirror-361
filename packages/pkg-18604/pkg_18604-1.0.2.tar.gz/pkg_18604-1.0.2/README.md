# badge-201

[![CI](https://github.com/tagdots-dev/badge-201/actions/workflows/ci.yaml/badge.svg)](https://github.com/tagdots-dev/badge-201/actions/workflows/ci.yaml) [![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/license.json)](https://github.com/tagdots-dev/badge-201/blob/main/LICENSE) [![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/marketplace.json)](https://github.com/marketplace/actions/setup-badge-action)

<br>

## 😎 What does setup-badge do?
**setup-badge** empowers you to create `dynamic` and `static` badges to showcase on your README file.

In a dynamic badge, the `message` changes over time.  For instance, you run daily tasks to get code coverage and software version, dynamic badges can display the latest code coverage percentage and software version.

In a static badge, the `message` does not change regularly over time.  For instance, license and programming language.

p.s. _`message` refers to the right side of a badge_

<br>

## ⭐ How setup-badge works

Under the hood, **setup-badge** creates a [shields.io endpoint badge](https://shields.io/badges/endpoint-badge), which is composed of _a shields.io endpoint_ and _an URL to your JSON file_.  For intance, `![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/badge.json)`.  Let's see the overall workflow below.

1. **setup-badge** runs with [command line options](https://github.com/tagdots-dev/badge-201?tab=readme-ov-file#-setup-badge-command-line-options).
1. **setup-badge** adds/updates a json file from your options.
1. **setup-badge** writes and pushes a commit to remote branch.
1. **endpoint badge** shields.io endpoint fetches your json file to format a badge.

Now, you are ready to put `endpoint badge` into your README file.

![How It Works](https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/assets/setup-badge.png)

<br>

## Use Case 1️⃣ - running on GitHub action
In this use case, you can create scheduled tasks to generate data points (e.g. code coverage and software version...etc) and feeds them to **setup-badge** `message` to create dynamic badges.

Please visit our GitHub action ([setup-badge-action](https://github.com/marketplace/actions/setup-badge-action)) on the `GitHub Marketplace` for details.

<br>

## Use Case 2️⃣ - running locally on your computer
In this use case, you are likely to create `static` badges. The steps are:

1. install **setup-badge**.
1. run **setup-badge**.

<br>

### 🔆 install setup-badge

In the command-line examples below, we use a GitHub project named `badge-test`.

We will first install **setup-badge** in a virtual environment named after the project.  Next, we will run **setup-badge** with different options and show the results.

```
~/work/badge-test $ workon badge-test
(badge-test) ~/work/badge-test $ pip install -U setup-badge
```

<br>

### 🔍 run setup-badge

🏃 _**Run to show command line options**_: `--help`

```
(badge-test) ~/work/badge-test $ setup-badge --help
Usage: setup-badge [OPTIONS]

Options:
  --badge-name TEXT       default: badge
  --badge-branch TEXT     default: badges
  --remote-name TEXT      default: origin
  --badge-style TEXT      default: flat (flat, flat-square, plastic, for-the-badge, social)
  --label TEXT            default: demo (badge left side text)
  --label-color TEXT      default: 2e2e2e (badge left side hex color)
  --message TEXT          default: no status (badge right side text)
  --message-color TEXT    default: 2986CC (badge right side hex color)
  --gitconfig-name TEXT   default: Mona Lisa
  --gitconfig-email TEXT  default: mona.lisa@example.com
  --version               Show the version and exit.
  --help                  Show this message and exit.
```

<br>

🏃 _**Run to create a demo badge (with default inputs)**_

**setup-badge** runs with default inputs and:

1. creates or uses an existing `badges` branch.
1. creates a `badge.json` file from `template.json`.
1. creates and push a commit with `badge.json` file to `badges` branch.
1. produces an `endpoint badge`.

```
(badge-test) ~/work/badge-test $ setup-badge
🚀 Starting to create a badge.json in branch (badges)...

✅ checkout branch (badges) locally
✅ validated inputs from command line options
✅ created badge.json from template.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (f9c751c) to remote with branch (badges)

🎉 Endpoint Badge: ![badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/badge.json)
🗑 delete remote working branch (ci-testing) successfully
```

_**Endpoint Badge**_<br>
![demo](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/badge.json)

<br>

🏃 _**Run to create a license badge**_

**setup-badge** runs with customized inputs and:

1. creates or uses an existing `badges` branch.
1. creates a `badge.json` file from `template.json` with your command line options.
1. creates and push a commit with `license.json` file to `license` branch.
1. produces an `endpoint badge`.

```
(badge-test) ~/work/badge-test $ setup-badge --badge-name license --label License --message MIT
🚀 Starting to create a badge (license.json) on branch (badges)

✅ checkout branch (badges) locally
✅ validated inputs from command line options
✅ created license.json from template.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (dd8906c) to remote with branch (badges)

🎉 Endpoint Badge: ![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/license.json)
🗑 delete remote working branch (ci-testing) successfully
```

_**Endpoint Badge**_<br>
![license](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/license.json)

<br>

🏃 _**Run to create a marketplace badge**_

**setup-badge** runs with customized inputs and:

1. creates or uses an existing `badges` branch.
1. creates a `badge.json` file from `template.json` with your command line options.
1. creates and push a commit with `marketplace.json` file to `marketplace` branch.
1. produces an `endpoint badge`.

```
(badge-test) ~/work/badge-test $ setup-badge --badge-name marketplace --label Marketplace --message setup-badge-action
🚀 Starting to create a badge (marketplace.json) on branch (badges)

✅ checkout branch (badges) locally
✅ validated inputs from command line options
✅ created marketplace.json from template.json
✅ found changes ready to stage, commit, and push to origin
✅ pushed commit (8991c28) to remote with branch (badges)

🎉 Endpoint Badge: ![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/marketplace.json)
🗑 delete remote working branch (ci-testing) successfully
```

_**Endpoint Badge**_<br>
![marketplace](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/badges/badges/marketplace.json)

<br>

📝 _**Summary of running the above commands**_

- **badges** branch holds multiple JSON files.
- **badges** folder holds all json files from different branches.

![Command Runs](https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/assets/badges-folder.png)

<br><br>

## 🔔 How to use Endpoint Badge?
After creating an `endpoint badge`, you will choose one of the following options to add it to your README file.

**clickable to your JSON endpoint**<br>
![click-to-json-endpoint](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/badges/click-to-json-endpoint.json)

```
![click-to-json-endpoint](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/badges/click-to-json-endpoint.json)
```

<br>

**clickable to your custom URL**<br>

- place Endpoint Badge inside a square bracket []
- add your custom URL inside a parenthesis () and append to above

[![click-to-custom-url](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/badges/click-to-custom-url.json)](https://www.github.com/tagdots-dev/badge-201)

```
[![click-to-custom-url](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/tagdots-dev/badge-201/refs/heads/main/badges/click-to-custom-url.json)](https://www.github.com/tagdots-dev/badge-201)
```

<br><br>

## 🔧 setup-badge command line options

| Input | Description | Default | Notes |
|-------|-------------|----------|----------|
| `badge-name` | JSON endpoint filename | `badge` | JSON endpoint filename |
| `branch-name` | Branch to hold JSON endpoint | `badges` | a single branch can hold multiple JSON endpoint files |
| `remote-name` | Git remote source branch | `origin` | leave it as-is in general |
| `badge-style` | Badge style | `flat` | other options: `flat-square`, `plastic`, `for-the-badge`, `social` |
| `label` | Left side text | `demo` | - |
| `label-color` | Left side background color | `2e2e2e` | hex color |
| `message` | Right side text | `no status` | pass dynamic/static data here |
| `message-color` | Right side background color | `2986CC` | hex color |
| `gitconfig-name` | Git config user name | `Mona Lisa` | need this option for GitHub action |
| `gitconfig-email` | Git config user email | `mona.lisa@example.com` | need this option for GitHub action |

<br>

## 😕  Troubleshooting

Open an [issue][issues]

<br>

## 🙏  Contributing

Pull requests and stars are always welcome.  For pull requests to be accepted on this project, you should follow [PEP8][pep8] when creating/updating Python codes.

See [Contributing][contributing]

<br>

## 📚 References

[Shields.io Endpoint Badge](https://shields.io/badges/endpoint-badge)

[Hex Color](https://www.color-hex.com/)

[How to fork a repo](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo)

<br>

[contributing]: https://github.com/tagdots-dev/badge-201/blob/main/CONTRIBUTING.md
[issues]: https://github.com/tagdots-dev/badge-201/issues
[pep8]: https://google.github.io/styleguide/pyguide.html
